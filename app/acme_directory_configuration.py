from dataclasses import dataclass


@dataclass
class ACMEDirectoryConfiguration:
    """
    This data is generated from the directory endpoint. These endpoints can be different per server.
    """

    new_order_url: str
    new_account_url: str
    new_nonce_url: str
    revoke_cert_url: str
