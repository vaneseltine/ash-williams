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
    """
    The last-sorted should be, if file naming is consistent, the most recent.
    But don't use this fixture if it's critical that you use the most recent dataset.
    """
    latest_csv = sorted(DATA_DIR.glob("*.csv"))[-1]
    print(f"Passing full_db as {latest_csv}")
    return latest_csv


@pytest.fixture(scope="session")
def mock_db():
    return RetractionDatabase(MOCK_DIR / "rw_database.csv")
