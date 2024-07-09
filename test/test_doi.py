import pytest

from ash.ash import DOI, BadDOIError
import ash.ash
from ash.ash import http


class TestInstantiation:

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            None,
            "unavailable",
            "Unavailable",
            "12356.23",
        ],
    )
    def test_dois_obviously_bad(self, raw):
        with pytest.raises(BadDOIError):
            _ = DOI(raw)

    @pytest.mark.parametrize(
        "raw",
        [
            "10.1234/retracted12345",
            "10.1126/science.aax5705",
        ],
    )
    def test_dois_regex_acceptable(self, raw):
        _ = DOI(raw)


class TestAPI:

    def test_existence(self, mocker):
        # Mock the 'request' method on the already instantiated 'http' instance in 'ash.ash'
        mock_http_request = mocker.patch("ash.ash.http.request")

        # Configure the mock to return a mock response object when called
        mock_response = mocker.MagicMock()
        mock_response.status = 200  # Presume a status code of 200 for the example
        mock_http_request.return_value = mock_response

        # Call the method that you expect to make the HTTP request
        good_doi = "10.1126/science.aax5705"
        doi = DOI(good_doi)
        exists_result = doi.exists()

        # Check if the endpoint meets your expectation
        expected_url = "https://doi.org/api/handles/" + good_doi
        mock_http_request.assert_called_once_with("HEAD", expected_url)

        # Any other assertions regarding the return value of doi.exists() can follow...
        assert exists_result  # Replace with the actual expected result
