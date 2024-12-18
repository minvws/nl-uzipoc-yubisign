from unittest.mock import MagicMock

from app.yubikey_content_checker import YubikeyContentChecker
from app.yubikey_details import YubikeyDetails

_SAMPLE_YUBIKEY = YubikeyDetails("1", "1", "test")


def test_yubikey_content_finder_empty():
    pkcs_wrapper = MagicMock()
    checker = YubikeyContentChecker(pkcs_wrapper)
    result = checker.check(_SAMPLE_YUBIKEY)

    assert result is False
