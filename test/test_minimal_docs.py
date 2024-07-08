from pathlib import Path

import pytest

from ash.ash import Paper

VAULT = Path(__file__).parent / "vault"


@pytest.mark.parametrize("path", VAULT.glob("basic*"))
def test_minimal_documents(path):
    paper = Paper(path)
    assert set(paper.dois) == {"10.21105/joss.03440"}
