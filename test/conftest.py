import pytest

try:
    from __vault__ import VAULT_DIR

    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


@pytest.fixture(scope="session")
def vault():
    return {path.name: path for path in VAULT_DIR.glob("*.*")}
