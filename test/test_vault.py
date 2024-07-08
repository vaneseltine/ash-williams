from pathlib import Path

import pytest

from ash.ash import Paper


class TestVaultDOIs:
    KNOWN = {
        "Weeden_2023_Crisis.pdf": {
            "10.1162/99608f92.151c41e3",
            "10.1038/s41467-023-41111-1",
            "10.1146/annurev-soc-060116-053450",
            "10.1007/s12108-006-1006-8",
            "10.1146/annurev-soc-090221-035954",
            "10.1177/0038038519853146",
            "10.1016/j.socscimed.2016.08.004",
            "10.7298/PKWJ-GM89",
        },
        "42-1-orig_article_Cagney.pdf": {
            "10.1016/S0140-6736(14)60921-1",
            "10.1016/S0140-6736(14)62216-9",
            "10.1016/S0140-6736(15)00342-6",
            "10.1016/S0140-6736(16)00041-6",
            "10.1016/S2213-2600(14)70125-0",
            "10.1016/S2213-2600(14)70141-9.113",
            "10.1016/S2213-2600(15)00005-3",
            "10.1016/S2213-2600(15)00007-7",
            "10.1038/478026a",
            "10.1087/20110208",
            "10.3109/08039488.2012.761401",
        },
        "pdf_without_suffix": {
            "10.21105/joss.03440",
        },
    }

    @pytest.mark.parametrize("filename, dois", KNOWN.items())
    def test_vault(self, vault, filename, dois):
        paper = Paper.from_path(vault[filename])
        assert set(paper.dois) == set(dois)

    @pytest.mark.xfail(reason="Need to check for line breaks")
    def test_line_break_shortens_doi_in_pdf(self, vault):
        """
        We get 10.3390/v130 instead
        """
        paper = Paper.from_path(vault["10.3389.fcvm.2021.745758.pdf"])
        assert "10.3390/v13040700" in paper.dois

    @pytest.mark.xfail(reason="Line breaks again")
    def test_line_break_obscures_doi_in_pdf(self, vault):
        """
        This one isn't detected at all
        """
        paper = Paper.from_path(vault["42-1-orig_article_Cagney.pdf"])
        assert "10.1016/S0140-6736(14)61033-3" in paper.dois


class TestMinimal:
    @pytest.mark.parametrize(
        "filename",
        [
            "basic_doi_colon.docx",
            "basic_doi_colon.latex",
            "basic_doi_colon.pdf",
            "basic_doi_colon.rtf",
            "basic_doi_colon.tex",
            "basic_doi_colon.txt",
            "basic_doi_url.docx",
            "basic_doi_url.pdf",
            "basic_doi_url.rtf",
            "basic_doi_url.txt",
        ],
    )
    def test_minimal_documents(self, vault, filename):
        try:
            paper = Paper.from_path(vault[filename])
        except NotImplementedError:
            pytest.xfail("Not implemented")
        assert set(paper.dois) == {"10.21105/joss.03440"}

    def test_minimal_documents_no_suffix(self, vault):
        paper = Paper.from_path(vault["pdf_without_suffix"])
        assert set(paper.dois) == {"10.21105/joss.03440"}
