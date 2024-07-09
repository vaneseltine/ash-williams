from io import StringIO

from ash import Paper

UNRETRACTED_TEXT = "A DOI here 10.21105/joss.03440 and that's all for now."
UNRETRACTED_DOI = "10.21105/joss.03440"
MOCKED_RETRACTION = "This is retracted 10.1234/retracted12349 in mock db."
MOCKED_RETRACTION_DOI = "10.1234/retracted12349"


class TestInputs:

    def test_string_with_mime(self):
        paper = Paper(UNRETRACTED_TEXT, mime_type="text/plain")
        assert set(paper.dois) == {UNRETRACTED_DOI}

    def test_stringio_with_mime(self):
        stringio = StringIO(UNRETRACTED_TEXT)
        paper = Paper(stringio, mime_type="text/plain")
        assert set(paper.dois) == {UNRETRACTED_DOI}


class TestReports:

    def test_report_structure_unretracted(self, mock_db):
        paper = Paper(UNRETRACTED_TEXT, mime_type="text/plain")
        report = paper.report(mock_db)
        assert report["dois"][UNRETRACTED_DOI] == {
            "DOI is valid:": True,
            "Retracted:": False,
        }

    def test_report_structure_retracted(self, mock_db):
        paper = Paper(MOCKED_RETRACTION, mime_type="text/plain")
        report = paper.report(mock_db)
        assert report["dois"][MOCKED_RETRACTION_DOI] == {
            "DOI is valid:": False,
            "Retracted:": True,
        }

    def test_single_unretracted_doi_captured(self, mock_db):
        paper = Paper(UNRETRACTED_TEXT, mime_type="text/plain")
        report = paper.report(mock_db)
        assert report["dois"][UNRETRACTED_DOI] == {
            "DOI is valid:": True,
            "Retracted:": False,
        }
