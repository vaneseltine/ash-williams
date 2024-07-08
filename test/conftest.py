from pathlib import Path

import pytest

from ash.ash import RetractionDatabase

MAIN_DIR = Path(__file__).parent.parent
DATA_DIR = MAIN_DIR / "data"

TEST_DIR = Path(__file__).parent
MOCK_DIR = TEST_DIR / "mock"

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
    vault_files = list(VAULT_DIR.glob("*"))
    return {path.name: path for path in vault_files}


@pytest.fixture(scope="session")
def full_db():
    return RetractionDatabase(DATA_DIR / "retraction-watch-2024-07-04.csv")


@pytest.fixture(scope="session")
def mock_db():
    return RetractionDatabase(MOCK_DIR / "rw_database.csv")
