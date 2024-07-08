import pytest

try:
    from __vault__ import VAULT_DIR

    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


@pytest.fixture(scope="session")
def vault():
    if not VAULT_AVAILABLE:
        pytest.xfail(reason="Vault unavailable for testing.")
        return
    return {path.name: path for path in VAULT_DIR.glob("*.*")}
