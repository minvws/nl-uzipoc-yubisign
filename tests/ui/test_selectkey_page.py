from unittest.mock import MagicMock
from pytestqt.qtbot import QtBot

from app.page.selectkey import SelectYubiKeyPage

from PyQt6.QtWidgets import QWizardPage

from PyKCS11 import CK_TOKEN_INFO

from app.page.yubikeyitem import YubiKeyItemWidget


def test_is_wizard_page(qtbot: QtBot):
    pkcs_wrapper = MagicMock()

    page = SelectYubiKeyPage(pkcs_wrapper)
    qtbot.addWidget(page)

    assert isinstance(page, QWizardPage)


def test_not_complete_yet(qtbot: QtBot):
    pkcs_wrapper = MagicMock()

    page = SelectYubiKeyPage(pkcs_wrapper)
    qtbot.addWidget(page)

    assert page._pin_authenticated is False
    assert page.isComplete() is False


def test_with_key_on_page(qtbot: QtBot):
    mock_token_info = CK_TOKEN_INFO()
    mock_token_info.model = "key"
    mock_token_info.serialNumber = "1234"
    mock_token_info.label = "1234"

    pkcs_wrapper = MagicMock()
    pkcs_wrapper.pkcs11.getSlotList.return_value = ["123"]
    pkcs_wrapper.pkcs11.getTokenInfo.return_value = mock_token_info

    page = SelectYubiKeyPage(pkcs_wrapper)
    qtbot.addWidget(page)

    first_item = page.key_list_widget.item(0)
    assert first_item is not None

    widget_item = page.key_list_widget.itemWidget(first_item)
    assert isinstance(widget_item, YubiKeyItemWidget)

    slot, name, serial = widget_item.getYubiKeyDetails()

    assert slot == "123"
    assert name == mock_token_info.model
    assert serial == mock_token_info.serialNumber

    assert page._pin_input_widget._input.isEnabled() is False


def test_select_key_on_page(qtbot: QtBot):
    mock_token_info = CK_TOKEN_INFO()
    mock_token_info.model = "key"
    mock_token_info.serialNumber = "1234"
    mock_token_info.label = "1234"

    pkcs_wrapper = MagicMock()
    pkcs_wrapper.pkcs11.getSlotList.return_value = ["123"]
    pkcs_wrapper.pkcs11.getTokenInfo.return_value = mock_token_info

    page = SelectYubiKeyPage(pkcs_wrapper)
    qtbot.addWidget(page)

    first_item = page.key_list_widget.item(0)
    assert first_item is not None

    with qtbot.waitSignal(page.key_list_widget.itemSelectionChanged):
        page.key_list_widget.setCurrentRow(0)

    assert page._pin_input_widget._input.isEnabled()
