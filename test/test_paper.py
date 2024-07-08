from io import StringIO
from pathlib import Path

import pytest

from ash.ash import Paper


class TestPaperInputs:
    def test_stringio(self):
        stringio = StringIO("A DOI here 10.21105/joss.03440 and that's all for now.")
        paper = Paper(stringio, mime_type="text/plain")
        assert set(paper.dois) == {"10.21105/joss.03440"}
