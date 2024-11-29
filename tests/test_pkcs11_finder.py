from unittest.mock import MagicMock, patch

import pytest
from app.pkcs_lib_finder import PKCS11LibFinder, PyKCS11


@patch(
    "app.pkcs_lib_finder.PyKCS11.PyKCS11Lib.load",
    side_effect=PyKCS11.PyKCS11Error("No library found"),
)
def test_lib_not_found(load_mock: MagicMock):
    finder = PKCS11LibFinder()
    result = finder.find()

    assert load_mock.call_count == 8
    assert result is None


@patch(
    "app.pkcs_lib_finder.PyKCS11.PyKCS11Lib.load",
    side_effect=None,
)
def test_success(load_mock: MagicMock):
    finder = PKCS11LibFinder()
    finder.find()

    assert load_mock.call_count == 1
