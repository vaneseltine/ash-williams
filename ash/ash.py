import csv
import mimetypes
import zipfile
from abc import abstractmethod
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol
from xml.etree.ElementTree import XML

import filetype  # type: ignore
from pypdf import PdfReader
from striprtf.striprtf import rtf_to_text

from . import doi
from .config import log_this


class RetractionDatabase:
    """
    Lazily load the DB.

    TODO: Cache path -> data so people don't have to use this object directly.
    """

    @log_this
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._data: defaultdict[str, list[dict[str, str]]] = defaultdict(list)

    @property
    def data(self) -> defaultdict[str, list[dict[str, str]]]:
        if len(self._data) == 0:
            self._build_data()
            doi.validate_collection(self.dois)
        return self._data

    @property
    def dois(self) -> set[str]:
        return set(self.data.keys())

    def _build_data(self) -> None:
        """
        Consider caching this, e.g., outfile.write_text(json.dumps(self._data))
        """
        print(f"Loading retraction database from {self.path.absolute()}...")
        with self.path.open(encoding="utf8", errors="backslashreplace") as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader.fieldnames)
            for row in reader:
                raw_doi = row.get("OriginalPaperDOI", "")
                clean_doi = doi.clean(raw_doi)
                if clean_doi in doi.BAD_DOIS:
                    continue
                row_dict = {str(k): str(v) for k, v in row.items()}
                self._data[clean_doi].append(row_dict)


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
    def from_path(cls, path: Path, mime_type: str | None = None) -> "Paper":
        if not path.exists():
            raise FileNotFoundError(path)
        mime_type = mime_type or path_to_mime_type(path)
        with path.open("rb") as stream:
            return cls(stream, mime_type)

    def report(self, db: RetractionDatabase | Path | str) -> dict[str, Any]:
        if isinstance(db, (Path, str)):
            db = RetractionDatabase(db)
        all_dois = {doi: (doi in db.dois) for doi in self.dois}
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
        return {"dois": all_dois, "zombies": zombie_report}

    @classmethod
    @log_this
    def register_handler(
        cls, mime_type: str
    ) -> Callable[[type[MIMEHandler]], type[MIMEHandler]]:

        def registrar_decorator(delegate: type[MIMEHandler]) -> type[MIMEHandler]:
            cls._MIME_handlers[mime_type] = delegate
            return delegate

        return registrar_decorator

    @classmethod
    def _get_handler(cls, mime_type: str) -> MIMEHandler:
        return cls._MIME_handlers[mime_type]()


@Paper.register_handler("application/pdf")
class PDFHandler(MIMEHandler):

    def extract_dois(self, data: Any) -> list[str]:
        reader = PdfReader(stream=data)  # type: ignore -- it takes FileStorage fine
        complete_text = "\n".join(page.extract_text() for page in reader.pages)
        return doi.text_to_dois(complete_text)


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
        print("docx", result)
        return doi.text_to_dois(result)


@Paper.register_handler("application/rtf")  # .rtf on Linux
@Paper.register_handler("application/msword")  # .rtf on Windows
class RTFHandler(MIMEHandler):

    def extract_dois(self, data: Any) -> list[str]:
        ingested_rtf = data.read().decode()
        text: str = rtf_to_text(ingested_rtf)  # type: ignore
        return doi.text_to_dois(text)  # type: ignore


@Paper.register_handler("text/plain")
@Paper.register_handler("application/x-latex")
@Paper.register_handler("text/x-tex")  # .tex on Linux
@Paper.register_handler("application/x-tex")  # .tex on Windows
class PlainTextHandler(MIMEHandler):

    def extract_dois(self, data: Any) -> list[str]:
        if isinstance(data, str):
            return doi.text_to_dois(data)
        first_read = data.read()
        if isinstance(first_read, str):
            return doi.text_to_dois(first_read)
        return doi.text_to_dois(first_read.decode("utf-8"))


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
