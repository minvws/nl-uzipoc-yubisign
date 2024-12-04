from unittest.mock import MagicMock, patch
from app.acme_directory_configuration import ACMEDirectoryConfiguration
from app.acme_directory_configuration_parser import ACMEDirectoryConfigurationParser

from urllib.parse import urljoin, urlparse


@patch(
    "app.acme_directory_configuration_parser.requests.get",
    return_value=MagicMock(
        status_code=200,
        json=MagicMock(
            return_value={
                "meta": {"website": "http://localhost:9090"},
                "newNonce": "123",
                "newAccount": "123",
                "newOrder": "123",
                "revokeCert": "123",
            },
        ),
    ),
)
def test_url_parse(request_get_mock: MagicMock):
    base_url = urlparse("http://localhost:9090/")
    expected_request_url = urljoin(base_url.geturl(), "/directory")

    result: ACMEDirectoryConfiguration = ACMEDirectoryConfigurationParser().parse(
        base_url
    )

    assert result.new_nonce_url == "123"
    request_get_mock.assert_called_with(expected_request_url)
