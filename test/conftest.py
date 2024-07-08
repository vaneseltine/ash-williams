import pytest

try:
    from __vault__ import VAULT_DIR

    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


@pytest.fixture(scope="session")
def vault():
    print(VAULT_DIR)
    vault_files = list(VAULT_DIR.glob("*"))
    print(vault_files)
    if not VAULT_AVAILABLE:
        pytest.xfail(reason="Vault unavailable for testing.")
        return
    return {path.name: path for path in vault_files}
