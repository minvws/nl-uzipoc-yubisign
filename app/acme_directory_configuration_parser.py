from typing import Any
import requests

from app.acme_directory_configuration import ACMEDirectoryConfiguration
from urllib.parse import urljoin, urlparse, ParseResult as URLParseResult


class ACMEDirectoryConfigurationParser:
    def _build_conf_from_json(self, json: dict[str, Any]) -> ACMEDirectoryConfiguration:
        base = urlparse(
            json["meta"]["website"],
        )
        new_nonce_url = urlparse(
            json["newNonce"],
        )
        new_account_url = urlparse(
            json["newAccount"],
        )
        new_order_url = urlparse(
            json["newOrder"],
        )
        revoke_cert_url = urlparse(
            json["revokeCert"],
        )
        conf = ACMEDirectoryConfiguration(
            base_url=base,
            new_nonce_url=new_nonce_url,
            new_order_url=new_order_url,
            new_account_url=new_account_url,
            revoke_cert_url=revoke_cert_url,
        )
        return conf

    def parse(self, acme_base_url: URLParseResult) -> ACMEDirectoryConfiguration:
        directory_url = urljoin(
            acme_base_url.geturl(),
            "/acme/directory",
        )
        response = requests.get(directory_url)
        json = response.json()

        return self._build_conf_from_json(json)
