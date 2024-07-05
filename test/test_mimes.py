import pytest
from xdg import Mime


@pytest.mark.parametrize(
    "path, mime",
    [
        ("pyproject.toml", "toml"),
        ("test/vault/Weeden_2023_Crisis.pdf", "pdf"),
        ("test/vault/10.3389.fcvm.2021.745758.pdf", "pdf"),
    ],
)
def test_whether_mimes_work(path, mime):
    assert Mime.get_type2(path).subtype == mime
