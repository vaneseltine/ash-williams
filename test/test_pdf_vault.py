from pathlib import Path

import pytest

from ash.ash import Paper

VAULT = Path(__file__).parent / "vault"


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
        "10.7298/PKWJ-GM89",
    }
}

# pdf_doi_pairs = [(fn, doi) for fn, dois in PDF_DOIS.items() for doi in dois]


@pytest.mark.parametrize("filename, dois", PDF_DOIS.items())
def test_vault(filename, dois):
    paper = Paper(path_from_vault(filename))
    assert set(paper.dois) == set(dois)


@pytest.mark.xfail(reason="Need to check for line breaks")
def test_line_break_mid_doi_in_pdf():
    """
    We get 10.3390/v130 instead
    """
    paper = Paper(path_from_vault("10.3389.fcvm.2021.745758.pdf"))
    assert "10.3390/v13040700" in paper.dois
