from io import StringIO

from ash.ash import Paper


class TestPaperInputs:

    SIMPLE_STRING = "A DOI here 10.21105/joss.03440 and that's all for now."

    def test_string_with_mime(self):
        paper = Paper(self.SIMPLE_STRING, mime_type="text/plain")
        assert set(paper.dois) == {"10.21105/joss.03440"}

    def test_stringio_with_mime(self):
        stringio = StringIO(self.SIMPLE_STRING)
        paper = Paper(stringio, mime_type="text/plain")
        assert set(paper.dois) == {"10.21105/joss.03440"}
