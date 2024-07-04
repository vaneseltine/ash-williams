import pytest

PDF_DOIS = {
    "Weeden_2023_Crisis.pdf": {
        "https://doi.org/10.1162/99608f92.151c41e3",
        "https://doi.org/10.1038/s41467-023-41111-1",
        "https://doi.org/10.1146/annurev-soc-060116-053450",
        "https://doi.org/10.1007/s12108-006-1006-8",
        "https://doi.org/10.1146/annurev-soc-090221-035954",
        "https://doi.org/10.1177/0038038519853146",
        "https://doi.org/10.1016/j.socscimed.2016.08.004",
    }
}

pdf_doi_pairs = [(fn, doi) for fn, dois in PDF_DOIS.items() for doi in dois]


@pytest.mark.parametrize("filename, doi", pdf_doi_pairs)
def test_vault(filename, doi):
    assert filename == doi
