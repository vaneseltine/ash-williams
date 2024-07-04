from pathlib import Path

import pytest

from ash.ash import pdf_to_dois

VAULT = Path(__file__).parent / "pdfs"


def path_from_vault(path) -> Path:
    return VAULT / path


PDF_DOIS = {
    "Weeden_2023_Crisis.pdf": {
        "10.1162/99608f92.151c41e3",
        "10.1038/s41467-023-41111-1",
        "10.1146/annurev-soc-060116-053450",
        "10.1007/s12108-006-1006-8",
        "10.1146/annurev-soc-090221-035954",
        "10.1177/0038038519853146",
        "10.1016/j.socscimed.2016.08.004",
    }
}

# pdf_doi_pairs = [(fn, doi) for fn, dois in PDF_DOIS.items() for doi in dois]


@pytest.mark.parametrize("filename, dois", PDF_DOIS.items())
def test_vault(filename, dois):
    assert set(pdf_to_dois(path_from_vault(filename))) == set(dois)
