from dataclasses import dataclass
from urllib.parse import ParseResult as URLParseResult


@dataclass
class ACMEDirectoryConfiguration:
    """
    This data is generated from the /acme/directory endpoint. These endpoints can be different per server
    """

    base_url: URLParseResult
    new_order_url: URLParseResult
    new_account_url: URLParseResult
    new_nonce_url: URLParseResult
    revoke_cert_url: URLParseResult
