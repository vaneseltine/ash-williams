import csv
import re
from collections import defaultdict
from collections.abc import Collection
from enum import Enum, auto
from itertools import chain
from pathlib import Path

from pypdf import PdfReader

from .config import DATA_DIR


class FileType(Enum):
    DOC = auto()
    DOCX = auto()
    TEXT = auto()
    PDF = auto()
    RDF = auto()


ARCHIVE_JSON = DATA_DIR / "current_retraction_watch.json"

LOCAL_DATA_DIR = Path(__file__).parent.parent / "data"
try:
    RETRACTION_WATCH_CSV = list(LOCAL_DATA_DIR.glob("*.csv"))[-1]
except (FileNotFoundError, IndexError) as err:
    raise FileNotFoundError(f"Could not find a CSV in {LOCAL_DATA_DIR}") from err

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

    TODO - we are clobbering multiple records of retraction/concern

    This should probably actually have
        doi: [{rw_entry}, {rw_entry}]
    defaultdict instead?
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
        import json

        _ = ARCHIVE_JSON.write_text(json.dumps(self._data))

        import random

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

    def __init__(self, path: Path, filetype: FileType | None = None) -> None:
        if not path.exists():
            raise FileNotFoundError(path)
        self.path = path
        self.filetype = filetype or self.suffix_to_filetype[path.suffix.lower()]
        self.dois = self.extract_dois(self.path)

    def extract_dois(self, path: Path) -> list[str]:
        text = self.pdf_to_text(path)
        dois = self.text_to_dois(text)
        return dois

    @staticmethod
    def pdf_to_text(path: Path) -> str:
        reader = PdfReader(path)
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
                        "  ❌",
                        "-",
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


def run_cli() -> None:
    retraction_db = RetractionDatabase(RETRACTION_WATCH_CSV)
    print(len(retraction_db.dois))
    # https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2021.745758/full?s=09

    for filename in [
        "10.3389.fcvm.2021.745758.pdf",
        "42-1-orig_article_Cagney.pdf",
    ]:
        sample = Paper(Path(__file__).parent.parent / "test" / "vault" / filename)
        # print(sample.dois)
        print(filename)
        sample.report(retraction_db)

    # print("10.1016/S0140-6736(20)32656-8" in retraction_db.dois)


if __name__ == "__main__":
    run_cli()
