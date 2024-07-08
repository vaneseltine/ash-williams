import csv
import random
import re
import zipfile
from abc import abstractmethod
from collections import defaultdict
from collections.abc import Callable, Collection
from io import BufferedReader
from itertools import chain
from mimetypes import guess_type
from pathlib import Path
from pprint import pprint
from typing import Any, Protocol
from xml.etree.ElementTree import XML

from pypdf import PdfReader
from werkzeug.datastructures import FileStorage

from .config import log_this

# https://www.crossref.org/blog/dois-and-matching-regular-expressions/
CROSSREF_PATTERNS = [
    r"10.\d{4,9}/[-._;()/:A-Z0-9]+",
    r"10.1002/[^\s]+",
    r"10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\dP",
    r"10.1021/\w\w\d++",
    r"10.1207/[\w\d]+\&\d+_\d+",
]
MY_DUMB_PATTERNS = []

DOI_PATTERNS = [
    re.compile(s, flags=re.IGNORECASE) for s in CROSSREF_PATTERNS + MY_DUMB_PATTERNS
]
BAD_DOIS = ["", "unavailable", "Unavailable"]
DOI_FIXES = {
    "10.1177/ 0020720920940575": "10.1177/0020720920940575",
}


def clean_doi(s: str) -> str:
    s = DOI_FIXES.get(s, s)
    return s.strip(". /")


def path_to_mime_type(path: str | Path) -> str:
    guessed_mime, _ = guess_type(path)
    if not guessed_mime:
        raise TypeError(f"Could not determine MIME type of {path}")
    return guessed_mime


def text_to_dois(text: str) -> list[str]:
    matches = [pattern.findall(text) for pattern in DOI_PATTERNS]
    dois = list(chain.from_iterable(matches))
    clean_dois = [clean_doi(doi) for doi in dois]
    return clean_dois


class RetractionDatabase:
    """
    Lazily load the DB.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        # self._data: dict[str, dict[str, str]] = {}
        self._data: defaultdict[str, list[dict[str, str]]] = defaultdict(list)

    @property
    def data(self) -> defaultdict[str, list[dict[str, str]]]:
        if len(self._data) == 0:
            self._build_data()
            self._validate_dois(self.dois)
        return self._data

    @property
    def dois(self) -> set[str]:
        return set(self.data.keys())

    def _build_data(self) -> None:
        print(f"Loading retraction database from {self.path.absolute()}...")
        with self.path.open(encoding="utf8", errors="backslashreplace") as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader.fieldnames)
            for row in reader:
                raw_doi = row.get("OriginalPaperDOI", "")
                doi = clean_doi(raw_doi)
                if doi in BAD_DOIS:
                    continue
                row_dict = {str(k): str(v) for k, v in row.items()}
                self._data[doi].append(row_dict)

        # _ = ARCHIVE_JSON.write_text(json.dumps(self._data))

        print(random.choice(list(self._data.values())))

    def _validate_dois(self, dois: Collection[str]) -> None:
        for doi in dois:
            if any(text_to_dois(doi)):
                continue
            print(f"Warning, DOI does not match regex patterns: {doi}")


class MIMEHandler(Protocol):

    @abstractmethod
    def extract_dois(self, data: BufferedReader | FileStorage) -> list[str]: ...


class Paper:

    _MIME_handlers: dict[str, type[MIMEHandler]] = {}

    def __init__(self, data: BufferedReader | FileStorage, mime_type: str) -> None:
        self.mime_type = mime_type
        handler = self.get_handler(self.mime_type)
        self.dois = handler.extract_dois(data)
        # self.dois = self._extract_dois(data)

    @classmethod
    def from_path(cls, path: Path, mime_type: str | None = None) -> "Paper":
        if not path.exists():
            raise FileNotFoundError(path)
        mime_type = mime_type or path_to_mime_type(path)
        with path.open("rb") as stream:
            return cls(stream, mime_type)

    def printout(self, db: RetractionDatabase) -> None:
        zombies: list[str] = []
        for doi in self.dois:
            zombie = doi in db.dois
            mark = " " if zombie else "✔️"
            print(f"{mark} {doi}")
            if not zombie:
                continue
            zombies.append(doi)
            for rw_record in db.data[doi]:
                comment = " ".join(
                    (
                        "  ❗",
                        rw_record["RetractionNature"],
                        "-",
                        rw_record["RetractionDate"],
                        "-",
                        "see https://doi.org/" + rw_record["RetractionDOI"],
                    )
                )
                print(comment)

        for doi in zombies:
            print(db.data[doi])

    def report(self, db: RetractionDatabase) -> dict[str, Any]:
        all_dois = {doi: (doi in db.dois) for doi in self.dois}
        zombies = sorted(
            [doi for doi in self.dois if doi in db.dois], key=lambda x: x[1]
        )
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
    def get_handler(cls, mime_type: str) -> MIMEHandler:
        return cls._MIME_handlers[mime_type]()


@Paper.register_handler("application/pdf")
class PDFHandler(MIMEHandler):

    def extract_dois(self, data: BufferedReader | FileStorage) -> list[str]:
        reader = PdfReader(stream=data)  # type: ignore -- it takes FileStorage fine
        complete_text = "\n".join(page.extract_text() for page in reader.pages)
        return text_to_dois(complete_text)


@Paper.register_handler("application/rtf")  # .rtf on Linux
@Paper.register_handler("application/msword")  # .rtf on Windows
class RTFHandler(MIMEHandler):

    def extract_dois(self, data: BufferedReader | FileStorage) -> list[str]:
        raise NotImplementedError("Have not implemented RTF")


@Paper.register_handler(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
class DOCXHandler(MIMEHandler):
    WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    PARA = WORD_NAMESPACE + "p"
    TEXT = WORD_NAMESPACE + "t"

    def extract_dois(self, data: BufferedReader | FileStorage) -> list[str]:

        document = zipfile.ZipFile(data)
        xml_content = document.read("word/document.xml")
        document.close()
        tree = XML(xml_content)

        paragraphs: list[str] = []
        for paragraph in tree.iter(self.PARA):
            texts = [node.text for node in paragraph.iter(self.TEXT) if node.text]
            if texts:
                paragraphs.append("".join(texts))
        result = "\n\n".join(paragraphs)
        print("docx", result)
        return text_to_dois(result)


@Paper.register_handler("text/plain")
@Paper.register_handler("application/x-latex")
@Paper.register_handler("text/x-tex")  # .tex on Linux
@Paper.register_handler("application/x-tex")  # .tex on Windows
class PlainTextHandler(MIMEHandler):

    def extract_dois(self, data: BufferedReader | FileStorage) -> list[str]:
        first_read = data.read()
        if isinstance(first_read, str):
            return text_to_dois(first_read)
        return text_to_dois(first_read.decode("utf-8"))


def run_cli() -> None:

    # ARCHIVE_JSON = DATA_DIR / "current_retraction_watch.json"

    # LOCAL_DATA_DIR = Path(__file__).parent.parent / "data"
    # try:
    #     RETRACTION_WATCH_CSV = list(LOCAL_DATA_DIR.glob("*.csv"))[-1]
    # except (FileNotFoundError, IndexError) as err:
    #     raise FileNotFoundError(f"Could not find a CSV in {LOCAL_DATA_DIR}") from err

    retraction_db = RetractionDatabase(Path("./data/retraction-watch-2024-07-04.csv"))
    print(len(retraction_db.dois))
    # https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2021.745758/full?s=09

    # for filename in [
    #     # "10.3389.fcvm.2021.745758.pdf",
    #     # "42-1-orig_article_Cagney.pdf",
    #     "basic_doi_url.pdf",
    #     "basic_doi_url.txt",
    # ]:
    #     path = Path(__file__).parent.parent / "test" / "vault" / filename
    #     sample = Paper.from_path(path)
    #     # print(sample.dois)
    #     print()
    #     print(filename)
    #     pprint(sample.report(retraction_db))

    # print("10.1016/S0140-6736(20)32656-8" in retraction_db.dois)

    from io import StringIO

    filelike = StringIO("soadifja 10.21105/joss.03440 soiadjf")
    print(Paper(filelike, "text/plain").dois)
    # print("10.21105/joss.03440", text_to_dois())


if __name__ == "__main__":
    run_cli()
