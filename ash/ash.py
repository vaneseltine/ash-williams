import csv
import json
import random
import re
from collections import defaultdict
from collections.abc import Collection
from enum import Enum, auto
from io import BufferedReader
from itertools import chain
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from werkzeug.datastructures import FileStorage

from .config import DATA_DIR


class FileType(Enum):
    DOC = auto()
    DOCX = auto()
    TEXT = auto()
    PDF = auto()
    RDF = auto()


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
            self.validate_dois(self.dois)
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

    def validate_dois(self, dois: Collection[str]) -> None:
        for doi in dois:
            if any(Paper.text_to_dois(doi)):
                continue
            print(f"Warning, DOI does not match regex patterns: {doi}")


class Paper:

    suffix_to_filetype = {
        ".doc": FileType.DOC,
        ".docx": FileType.DOCX,
        ".text": FileType.TEXT,
        ".pdf": FileType.PDF,
        ".rdf": FileType.RDF,
    }

    def __init__(
        self, data: BufferedReader | FileStorage, filetype: FileType | None = None
    ) -> None:
        self.filetype = filetype
        self.dois = self.extract_dois(data)

    @classmethod
    def from_path(cls, path: Path, filetype: FileType | None = None) -> "Paper":
        if not path.exists():
            raise FileNotFoundError(path)
        filetype = filetype or cls.suffix_to_filetype.get(path.suffix.lower())
        with path.open("rb") as stream:
            return cls(stream)

    def extract_dois(self, data: BufferedReader) -> list[str]:
        text = self.pdf_to_text(data)
        dois = self.text_to_dois(text)
        return dois

    @staticmethod
    def pdf_to_text(data: BufferedReader) -> str:
        reader = PdfReader(data)
        complete_text = "\n".join(page.extract_text() for page in reader.pages)
        return complete_text

    @staticmethod
    def text_to_dois(text: str) -> list[str]:
        matches = [pattern.findall(text) for pattern in DOI_PATTERNS]
        dois = list(chain.from_iterable(matches))
        clean_dois = [clean_doi(doi) for doi in dois]
        return clean_dois

    def report(self, db: RetractionDatabase) -> None:
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

    def json_report(self, db: RetractionDatabase) -> dict[str, Any]:
        return {doi: doi in db.dois for doi in self.dois}


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

    for filename in [
        "10.3389.fcvm.2021.745758.pdf",
        "42-1-orig_article_Cagney.pdf",
    ]:
        path = Path(__file__).parent.parent / "test" / "vault" / filename
        sample = Paper.from_path(path)
        # print(sample.dois)
        print(filename)
        sample.report(retraction_db)

    # print("10.1016/S0140-6736(20)32656-8" in retraction_db.dois)


if __name__ == "__main__":
    run_cli()
