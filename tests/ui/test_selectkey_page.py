from unittest.mock import MagicMock
from pytestqt.qtbot import QtBot

from app.page.selectkey import SelectYubiKeyPage

from PyQt6.QtWidgets import QWizardPage, QWizard

from PyKCS11 import CK_TOKEN_INFO

from app.page.yubikeyitem import YubiKeyItemWidget


def _create_sample_token_info() -> CK_TOKEN_INFO:
    info = CK_TOKEN_INFO()
    info.model = "key"
    info.serialNumber = "1234"
    info.label = "1234"

    return info


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
    mock_token_info = _create_sample_token_info()
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
    mock_token_info = _create_sample_token_info()

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


def test_deselect(qtbot: QtBot):
    mock_token_info = _create_sample_token_info()

    pkcs_wrapper = MagicMock()
    pkcs_wrapper.pkcs11.getSlotList.return_value = ["123"]
    pkcs_wrapper.pkcs11.getTokenInfo.return_value = mock_token_info

    page = SelectYubiKeyPage(pkcs_wrapper)
    qtbot.addWidget(page)

    first_item = page.key_list_widget.item(0)
    assert first_item is not None

    # First, select the item
    with qtbot.waitSignal(page.key_list_widget.itemSelectionChanged):
        page.key_list_widget.setCurrentRow(0)

    assert page._pin_input_widget._input.isEnabled()

    # Then de-select and assert
    with qtbot.waitSignal(page.key_list_widget.itemSelectionChanged):
        page.key_list_widget.clearSelection()

    assert page._pin_input_widget._input.isEnabled() is False


def test_cleanup(qtbot: QtBot):
    mock_token_info = _create_sample_token_info()

    pkcs_wrapper = MagicMock()
    pkcs_wrapper.pkcs11.getSlotList.return_value = ["123"]
    pkcs_wrapper.pkcs11.getTokenInfo.return_value = mock_token_info

    page = SelectYubiKeyPage(pkcs_wrapper)
    qtbot.addWidget(page)

    first_item = page.key_list_widget.item(0)
    assert first_item is not None

    # First, select the item
    with qtbot.waitSignal(page.key_list_widget.itemSelectionChanged):
        page.key_list_widget.setCurrentRow(0)

    page.cleanupPage()

    assert page._pin_authenticated is False
    assert page.key_list_widget.selectedIndexes() == []


def test_mock_next_page(qtbot: QtBot):
    mock_token_info = _create_sample_token_info()

    pkcs_wrapper = MagicMock()
    pkcs_wrapper.pkcs11.getSlotList.return_value = ["123"]
    pkcs_wrapper.pkcs11.getTokenInfo.return_value = mock_token_info

    page = SelectYubiKeyPage(pkcs_wrapper)

    wizard = QWizard()
    wizard.addPage(page)

    qtbot.addWidget(wizard)
    assert page.key_list_widget.item(0) is not None

    with qtbot.waitSignal(page.key_list_widget.itemSelectionChanged):
        page.key_list_widget.setCurrentRow(0)

    page._pin_authenticated = True
    page.nextId()

    pin = wizard.property("yubikey_pin")
    details = wizard.property("selectedYubiKey")

    assert pin == "123456"
    assert details
