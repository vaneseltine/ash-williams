import csv
import logging
import mimetypes
import re
import zipfile
from abc import abstractmethod
from collections import Counter, defaultdict
from collections.abc import Callable
from itertools import chain
from pathlib import Path
from typing import Any, Protocol
from xml.etree.ElementTree import XML

import filetype  # type: ignore
import urllib3
from pypdf import PdfReader
from striprtf.striprtf import rtf_to_text

from .config import log_this

http = urllib3.PoolManager()


logger = logging.getLogger(__name__)


class InvalidDOIError(ValueError):
    pass


class DOI:
    """
    See https://www.crossref.org/blog/dois-and-matching-regular-expressions/

    https://www.doi.org/the-identifier/resources/factsheets/doi-resolution-documentation

    Response Codes

      1 : Success. (HTTP 200 OK)
      2 : Error. Something unexpected went wrong during handle resolution. (HTTP 500
          Internal Server Error)
    100 : Handle Not Found. (HTTP 404 Not Found)
    200 : Values Not Found. The handle exists but has no values (or no values according
          to the types and indices specified). (HTTP 200 OK)
    """

    CROSSREF_PATTERNS = [
        r"10.\d{4,9}/[-._;()/:A-Z0-9]+",
        r"10.1002/[^\s]+",
        r"10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\dP",
        r"10.1021/\w\w\d+",
        r"10.1207/[\w\d]+\&\d+_\d+",
    ]

    REGEXES = [re.compile(s, flags=re.IGNORECASE) for s in CROSSREF_PATTERNS]
    DOI_FIXES = {
        "10.1177/ 0020720920940575": "10.1177/0020720920940575",
    }

    API_URL = "https://doi.org/api/handles/{doi}"
    API_RESPONSE_MAP: dict[int, bool] = {
        200: True,
        404: False,
    }
    _cached_api_results: dict[str, bool] = {}

    def __init__(self, raw: str) -> None:
        self.raw = raw
        self.cleaned = self.clean(self.raw)
        self._validate_via_regex(self.cleaned)
        self._does_exist: bool | None = self._cached_api_results.get(self.cleaned)

    @classmethod
    def _validate_via_regex(cls, doi: str) -> None:
        # Fail fast on a range of things that are obviously not dois
        if not "/" in doi:
            cls._report_bad_doi(doi)
        # Slightly more slowly identify by regex
        if not any(pattern.match(doi) for pattern in cls.REGEXES):
            cls._report_bad_doi(doi)

    @staticmethod
    def _report_bad_doi(doi: Any) -> None:
        if not doi:
            raise InvalidDOIError("No DOI!")
        raise InvalidDOIError(f'Bad DOI: "{doi}"')

    def exists(self) -> bool | None:
        self._does_exist = self._cached_api_results.get(self.cleaned)
        if self._does_exist is None:
            self._does_exist = self._exists_at_api(self.cleaned)
        # But only bother to cache if there's a real answer
        if self._does_exist is not None:
            self._cached_api_results[self.cleaned] = self._does_exist
        return self._does_exist

    @classmethod
    def _exists_at_api(cls, doi: str) -> bool | None:
        url = cls.API_URL.format(doi=doi)
        resp = http.request("HEAD", url)
        existence = cls.API_RESPONSE_MAP.get(resp.status)
        logger.info(f"{doi} | {url} | {resp.status} = {existence}")
        return existence

    @classmethod
    def clean(cls, s: str) -> str:
        s = str(s)
        s = cls.DOI_FIXES.get(s, s)
        return s.strip(". /")

    def __str__(self) -> str:
        return self.cleaned

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}("{self.cleaned}")"""


class RetractionDatabase:
    """
    Lazily load and cache the DB.
    """

    _path_cache: dict[Path, defaultdict[str, list[dict[str, str]]]] = {}

    @log_this
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._data: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
        self._invalid_dois: list[str] = []

    @property
    def data(self) -> defaultdict[str, list[dict[str, str]]]:
        cached_data = self._path_cache.get(self.path)
        if cached_data is not None:
            logger.info(f"Using cached data from {self.path}")
            self._data = cached_data
        if len(self._data) == 0:
            self._build_data()
            self._path_cache[self.path] = self._data
        return self._data

    @property
    def dois(self) -> set[str]:
        return set(self.data.keys())

    def _build_data(self) -> None:
        """
        Build dict of doi -> database columns.

        Consider caching long term, e.g., outfile.write_text(json.dumps(self._data))
        """

        logger.info(f"Loading retraction database from {self.path.absolute()}...")
        with self.path.open(encoding="utf8", errors="backslashreplace") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                raw_doi = row.get("OriginalPaperDOI", "")
                try:
                    doi = DOI(raw_doi)
                except InvalidDOIError:
                    self._invalid_dois.append(raw_doi)
                    continue
                row_dict = {str(k): str(v) for k, v in row.items()}
                self._data[str(doi)].append(row_dict)
        self._log_data_details()

    def _log_data_details(self) -> None:
        n_valid_entries = sum(len(subdict) for subdict in self._data.values())
        logger.info(
            f"... Loaded {len(self._data):,} valid DOIs"
            + f" with {n_valid_entries:,} total records."
        )
        counted_errors = Counter(self._invalid_dois)
        logger.info(f"... Ignored {len(self._invalid_dois):,} invalid DOIs.")
        common = ", ".join(f"{s!r} ({i:,})" for s, i in counted_errors.most_common())
        logger.info(f"... Most common invalid DOIs: {common}")

    def __str__(self) -> str:
        return str(self.path.name)

    def __repr__(self):
        try:
            return f"{self.__class__.__name__}('{self.path}')"
        except AttributeError:
            return f"{self.__class__.__name__}(...)"


class MIMEHandler(Protocol):

    @abstractmethod
    def extract_dois(self, data: Any) -> list[str]: ...


class Paper:

    _MIME_handlers: dict[str, type[MIMEHandler]] = {}

    def __init__(self, data: Any, mime_type: str) -> None:
        self.mime_type = mime_type
        handler = self._get_handler(self.mime_type)
        self.dois = handler.extract_dois(data)

    @classmethod
    def from_path(cls, path: Path | str, mime_type: str | None = None) -> "Paper":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        mime_type = mime_type or path_to_mime_type(path)
        with path.open("rb") as stream:
            return cls(stream, mime_type)

    def report(
        self,
        db: RetractionDatabase | Path | str,
        validate_dois: bool = True,
    ) -> dict[str, Any]:
        if isinstance(db, (Path, str)):
            db = RetractionDatabase(db)
        dois_report = self._generate_dois_report(db, validate=validate_dois)
        zombie_report = self._generate_zombie_report(db)
        return {"dois": dois_report, "zombies": zombie_report}

    def _generate_dois_report(
        self, db: RetractionDatabase, validate: bool
    ) -> dict[str, Any]:
        if not validate:
            return {doi: {"Retracted": (doi in db.dois)} for doi in self.dois}

        return {
            doi: {
                "DOI is valid": DOI(doi).exists(),
                "Retracted": (doi in db.dois),
            }
            for doi in self.dois
        }

    def _generate_zombie_report(self, db: RetractionDatabase) -> list[dict[str, Any]]:
        zombies = sorted([doi for doi in self.dois if doi in db.dois])
        zombie_report = [
            {
                "Zombie": doi,
                "Item": record["RetractionNature"],
                "Date": record["RetractionDate"],
                "Notice DOI": f"https://doi.org/{record.get('RetractionDOI')}",
            }
            for doi in zombies
            for record in db.data[doi]
        ]
        return zombie_report

    @classmethod
    def register_handler(
        cls, mime_type: str
    ) -> Callable[[type[MIMEHandler]], type[MIMEHandler]]:

        def registrar_decorator(delegate: type[MIMEHandler]) -> type[MIMEHandler]:
            cls._MIME_handlers[mime_type] = delegate
            return delegate

        return registrar_decorator

    @classmethod
    def _get_handler(cls, mime_type: str) -> MIMEHandler:
        handler = cls._MIME_handlers.get(mime_type)
        if handler is None:
            implemented = ", ".join(cls._MIME_handlers.keys())
            msg = f"No handler for {mime_type!r}. Available: {implemented}."
            raise NotImplementedError(msg)

        return handler()


@Paper.register_handler("application/pdf")
@Paper.register_handler("application/acrobat")
class PDFHandler(MIMEHandler):

    def extract_dois(self, data: Any) -> list[str]:
        reader = PdfReader(stream=data)  # type: ignore -- it takes FileStorage fine
        complete_text = "\n".join(page.extract_text() for page in reader.pages)
        return text_to_dois(complete_text)


@Paper.register_handler(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
class DOCXHandler(MIMEHandler):
    """
    Adapted from https://etienned.github.io/posts/extract-text-from-word-docx-simply/
    Heavier solution if this fails: https://github.com/python-openxml/python-docx
    """

    WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    PARA = WORD_NAMESPACE + "p"
    TEXT = WORD_NAMESPACE + "t"

    def extract_dois(self, data: Any) -> list[str]:

        with zipfile.ZipFile(data) as document:
            xml_content = document.read("word/document.xml")
        tree = XML(xml_content)

        paragraphs: list[str] = []
        for paragraph in tree.iter(self.PARA):
            texts = [node.text for node in paragraph.iter(self.TEXT) if node.text]
            if texts:
                paragraphs.append("".join(texts))
        result = "\n\n".join(paragraphs)
        return text_to_dois(result)


@Paper.register_handler("application/rtf")  # .rtf on Linux
@Paper.register_handler("application/msword")  # .rtf on Windows
class RTFHandler(MIMEHandler):

    def extract_dois(self, data: Any) -> list[str]:
        ingested_rtf = data.read().decode()
        text: str = rtf_to_text(ingested_rtf)  # type: ignore
        return text_to_dois(text)  # type: ignore


@Paper.register_handler("text/plain")
@Paper.register_handler("text/x-tex")  # .tex on Linux
@Paper.register_handler("application/x-tex")  # .tex on Windows
@Paper.register_handler("text/x-latex")
@Paper.register_handler("application/x-latex")
class PlainTextHandler(MIMEHandler):

    def extract_dois(self, data: Any) -> list[str]:
        if isinstance(data, str):
            return text_to_dois(data)
        first_read = data.read()
        if isinstance(first_read, str):
            return text_to_dois(first_read)
        return text_to_dois(first_read.decode("utf-8"))


@log_this
def path_to_mime_type(path: str | Path) -> str:
    """
    We will usually expect to have the path available, and so we can use the builtin
    mimetypes to crosswalk the suffix to the MIME. However, if there is no suffix,
    we should be able to infer it using the magic numbers instead.
    """
    guessed_mime, _ = mimetypes.guess_type(path)
    if not guessed_mime:
        return binary_mime_check(path)
    return guessed_mime


def binary_mime_check(obj: Any) -> str:
    """
    Use filetype.guess, but it doesn't recognize .txt, .tex, or .latex.

    Note that the filetype package lacks correct typing.
    """
    kind = filetype.guess(obj)  # type: ignore
    if kind is None:
        raise TypeError(f"Could not determine MIME type of {obj}")
    return kind.mime


def text_to_dois(text: str) -> list[str]:
    matches = [pattern.findall(text) for pattern in DOI.REGEXES]
    dois = list(chain.from_iterable(matches))
    return [str(DOI(d)) for d in dois]
