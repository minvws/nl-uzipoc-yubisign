from typing import Any
import requests

from app.acme_directory_configuration import ACMEDirectoryConfiguration
from urllib.parse import urljoin, urlparse, ParseResult as URLParseResult


class ACMEDirectoryConfigurationParser:
    def _build_conf_from_json(self, json: dict[str, Any]) -> ACMEDirectoryConfiguration:
        new_nonce_url = str(
            json["newNonce"],
        )
        new_account_url = str(
            json["newAccount"],
        )
        new_order_url = str(
            json["newOrder"],
        )
        revoke_cert_url = str(
            json["revokeCert"],
        )
        conf = ACMEDirectoryConfiguration(
            new_nonce_url=new_nonce_url,
            new_order_url=new_order_url,
            new_account_url=new_account_url,
            revoke_cert_url=revoke_cert_url,
        )
        return conf

    def parse(self, acme_base_url: URLParseResult) -> ACMEDirectoryConfiguration:
        response = requests.get(
            acme_base_url.geturl(),
        )
        json = response.json()

        return self._build_conf_from_json(json)
