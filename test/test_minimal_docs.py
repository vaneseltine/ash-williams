from pathlib import Path

import pytest

from ash.ash import Paper

VAULT = Path(__file__).parent / "vault"


@pytest.mark.parametrize("path", VAULT.glob("basic*"))
def test_minimal_documents(path):
    try:
        paper = Paper.from_path(path)
    except NotImplementedError:
        pytest.xfail("Not implemented")
    assert set(paper.dois) == {"10.21105/joss.03440"}


@pytest.mark.parametrize("path", VAULT.glob("*_without_suffix"))
@pytest.mark.xfail(reason="Haven't implemented attempts without MIME")
def test_minimal_documents_no_suffix(path):
    paper = Paper.from_path(path)
    assert set(paper.dois) == {"10.21105/joss.03440"}
