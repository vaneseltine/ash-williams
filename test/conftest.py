from pathlib import Path

import pytest

from ash.main import DOI, RetractionDatabase

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
    Generally mock_db is the one to use.
    """
    latest_csv = sorted(DATA_DIR.glob("*.csv"))[-1]
    print(f"Passing full_db as {latest_csv}")
    return latest_csv


@pytest.fixture(scope="session")
def fake_db():
    """
    Four rows of badly faked data from the Crossref distribution of the Retraction Watch
    database. Includes the following retracted DOIs:

        - 10.1234/retracted12345
        - 10.1234/retracted12346
        - 10.1234/retracted12349
        - 10.1234/retracted12345
    """
    return RetractionDatabase(MOCK_DIR / "rw_database.csv")


@pytest.fixture(scope="function")
def mock_http(mocker, request):
    code = request.param

    http_request = mocker.patch("ash.main.http.request")

    mock_response = mocker.Mock()
    mock_response.status = code
    http_request.return_value = mock_response
    return http_request


@pytest.fixture(scope="function", autouse=True)
def delete_api_cache():
    DOI._cached_api_results = {}  # pylint: disable=protected-access
