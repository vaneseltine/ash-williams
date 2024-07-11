from io import StringIO

import pytest

from ash.ash import DOI, InvalidDOIError, Paper, path_to_mime_type

UNRETRACTED_TEXT = "A DOI here 10.21105/joss.03440 and that's all for now."
UNRETRACTED_DOI = "10.21105/joss.03440"
MOCKED_RETRACTION = "This is retracted 10.1234/retracted12349 in mock db."
MOCKED_RETRACTION_DOI = "10.1234/retracted12349"


class TestEndtoEnd:
    """
    Maybe one day I'll sort out a doctest but there's a lot of mocking currently...
    """

    @pytest.mark.parametrize("mock_http", [200], indirect=True)
    def test_readme_style_invocation_works(self, fake_db, mock_http, tmpdir):
        path = tmpdir / "text.txt"
        path.write_text(MOCKED_RETRACTION, encoding="utf-8")
        paper = Paper.from_path(path)
        assert len(paper.report(fake_db)) > 0


class TestPaperCreation:

    def test_not_imp_error_for_bad_mimes(self):
        with pytest.raises(NotImplementedError):
            _ = Paper("asdf", mime_type="ba/nanas")


class TestPaperDOIExtraction:

    def test_create_via_string_with_mime(self):
        paper = Paper(UNRETRACTED_TEXT, mime_type="text/plain")
        assert set(paper.dois) == {UNRETRACTED_DOI}

    def test_create_via_stringio_with_mime(self):
        stringio = StringIO(UNRETRACTED_TEXT)
        paper = Paper(stringio, mime_type="text/plain")
        assert set(paper.dois) == {UNRETRACTED_DOI}

    def test_create_via_pdf_without_suffix(self, vault):
        paper = Paper.from_path(vault["pdf_without_suffix"])
        assert set(paper.dois) == {"10.21105/joss.03440"}

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
        paper = Paper.from_path(vault[filename])
        assert set(paper.dois) == {"10.21105/joss.03440"}

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
    def test_pdf_vault_dois(self, vault, filename, dois):
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


class TestPaperReports:

    @pytest.mark.parametrize("mock_http", [200], indirect=True)
    def test_single_unret(self, fake_db, mock_http):  # pylint: disable=unused-argument
        paper = Paper(UNRETRACTED_TEXT, mime_type="text/plain")
        report = paper.report(fake_db)
        assert report["dois"][UNRETRACTED_DOI] == {
            "DOI is valid": True,
            "Retracted": False,
        }

    @pytest.mark.parametrize("mock_http", [404], indirect=True)
    def test_report_structure_retracted(
        self, fake_db, mock_http
    ):  # pylint: disable=unused-argument
        paper = Paper(MOCKED_RETRACTION, mime_type="text/plain")
        report = paper.report(fake_db)
        assert report["dois"][MOCKED_RETRACTION_DOI] == {
            "DOI is valid": False,
            "Retracted": True,
        }

    @pytest.mark.parametrize("mock_http", [418], indirect=True)
    def test_unclear_response_from_server(self, fake_db, mock_http, tmpdir):

        path = tmpdir / "text.txt"
        path.write_text(MOCKED_RETRACTION, encoding="utf-8")
        paper = Paper.from_path(path)
        report = paper.report(fake_db)
        assert report["dois"][MOCKED_RETRACTION_DOI] == {
            "DOI is valid": None,
            "Retracted": True,
        }

    def test_no_socket_hits_with_no_validation(self, fake_db):
        text = """
        You can find this in the sporting goods department. That's right, this sweet
        baby was made in Grand Rapids, Michigan. Retails for about
        doi:10.10995/walnutstock. That's right. "Short Smart: Shop S-Mart!"
        """
        paper = Paper(text, mime_type="text/plain")
        print(paper.report(fake_db, validate_dois=False))


class TestMIMEBehavior:
    @pytest.mark.parametrize(
        "filename, acceptable_mimes",
        [
            (
                "basic_doi_colon.pdf",
                ("application/pdf"),
            ),
            (
                "pdf_without_suffix",
                ("application/pdf"),
            ),
            (
                "basic_doi_colon.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            (
                "basic_doi_colon.rtf",
                ("application/rtf", "application/msword"),
            ),
            (
                "basic_doi_colon.txt",
                ("text/plain"),
            ),
            (
                "basic_doi_colon.latex",
                ("application/x-latex"),
            ),
            (
                "basic_doi_colon.tex",
                ("text/x-tex", "application/x-tex"),
            ),
        ],
    )
    def test_mimes_detected_from_vault(self, vault, filename, acceptable_mimes):
        path = vault[filename]
        guessed_mime = path_to_mime_type(path)
        assert guessed_mime in acceptable_mimes


class TestDOI:

    @pytest.mark.parametrize("raw", ["", None, "unavailable", "Unavailable", "1235.23"])
    def test_dois_obviously_bad(self, raw):
        with pytest.raises(InvalidDOIError):
            _ = DOI(raw)

    @pytest.mark.parametrize(
        "raw", ["10.1234/retracted12345", "10.1126/science.aax5705"]
    )
    def test_dois_regex_acceptable(self, raw):
        _ = DOI(raw)


class TestAPICallsForDOI:

    @pytest.mark.parametrize("mock_http", [200], indirect=True)
    def test_existence(self, mock_http):

        good_doi = "10.1126/science.aax5705"
        doi = DOI(good_doi)
        exists_result = doi.exists()

        expected_url = "https://doi.org/api/handles/" + good_doi
        mock_http.assert_called_once_with("HEAD", expected_url)

        assert exists_result
