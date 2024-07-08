from io import StringIO

from ash.ash import Paper

UNRETRACTED = "A DOI here 10.21105/joss.03440 and that's all for now."
MOCKED_RETRACTION = "This is retracted 10.1234/retracted12349 in mock db."


class TestInputs:

    def test_string_with_mime(self):
        paper = Paper(UNRETRACTED, mime_type="text/plain")
        assert set(paper.dois) == {"10.21105/joss.03440"}

    def test_stringio_with_mime(self):
        stringio = StringIO(UNRETRACTED)
        paper = Paper(stringio, mime_type="text/plain")
        assert set(paper.dois) == {"10.21105/joss.03440"}


class TestReports:

    def test_report_structure_unretracted(self, mock_db):
        paper = Paper(UNRETRACTED, mime_type="text/plain")
        report = paper.report(mock_db)
        assert ("10.21105/joss.03440", False) in report["dois"].items()

    def test_report_structure_retracted(self, mock_db):
        paper = Paper(MOCKED_RETRACTION, mime_type="text/plain")
        report = paper.report(mock_db)
        assert ("10.1234/retracted12349", True) in report["dois"].items()

    def test_single_unretracted_doi_captured(self, full_db):
        paper = Paper(UNRETRACTED, mime_type="text/plain")
        report = paper.report(full_db)
        assert ("10.21105/joss.03440", False) in report["dois"].items()
