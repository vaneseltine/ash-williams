import re
from pathlib import Path

from pypdf import PdfReader

# https://www.crossref.org/blog/dois-and-matching-regular-expressions/
CROSSREF_PATTERNS = [
    r"10.\d{4,9}/[-._;()/:A-Z0-9]+",
    r"10.1002/[^\s]+",
    r"10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d",
    r"10.1021/\w\w\d++",
    r"10.1207/[\w\d]+\&\d+_\d+",
]
MY_DUMB_PATTERNS = []

DOI_PATTERNS = [
    re.compile(s, flags=re.IGNORECASE) for s in CROSSREF_PATTERNS + MY_DUMB_PATTERNS
]


def run_cli() -> None:
    PDF_DIR = Path("C:/Users/vanes/Dropbox (University of Michigan)/zotero")

    reader = PdfReader(PDF_DIR / "Weeden_2023_Crisis.pdf")

    complete_text = "\n".join(
        page.extract_text() for i, page in enumerate(reader.pages)
    )
    # print(complete_text)
    for pattern in DOI_PATTERNS:
        print(pattern)
        matches = pattern.findall(complete_text)
        print(matches)


if __name__ == "__main__":
    run_cli()
