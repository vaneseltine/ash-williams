"""
See https://www.crossref.org/blog/dois-and-matching-regular-expressions/
"""

import re
from collections.abc import Collection
from itertools import chain

CROSSREF_PATTERNS = [
    r"10.\d{4,9}/[-._;()/:A-Z0-9]+",
    r"10.1002/[^\s]+",
    r"10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\dP",
    r"10.1021/\w\w\d++",
    r"10.1207/[\w\d]+\&\d+_\d+",
]
ADDITIONAL_PATTERNS = []

DOI_PATTERNS = [
    re.compile(s, flags=re.IGNORECASE) for s in CROSSREF_PATTERNS + ADDITIONAL_PATTERNS
]
BAD_DOIS = ["", "unavailable", "Unavailable"]
DOI_FIXES = {
    "10.1177/ 0020720920940575": "10.1177/0020720920940575",
}


def text_to_dois(text: str) -> list[str]:
    matches = [pattern.findall(text) for pattern in DOI_PATTERNS]
    dois = list(chain.from_iterable(matches))
    clean_dois = [clean(doi) for doi in dois]
    return clean_dois


def clean(s: str) -> str:
    s = DOI_FIXES.get(s, s)
    return s.strip(". /")


def validate_collection(dois: Collection[str]) -> None:
    for d in dois:
        if any(text_to_dois(d)):
            continue
        print(f"Warning, DOI does not match regex patterns: {d}")
