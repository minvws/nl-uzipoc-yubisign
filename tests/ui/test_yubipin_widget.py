from unittest.mock import MagicMock
from pytestqt.qtbot import QtBot

from app.page.yubipin_widget import YubiPinWidget

from PyQt6.QtCore import pyqtSignal

from app.yubikey_details import YubikeyDetails


def _create_default_widget():
    pykcslib = MagicMock()
    pin_authentication_signal = pyqtSignal()

    widget = YubiPinWidget(
        pykcs11lib=pykcslib,
        pin_authenticated_signal=pin_authentication_signal,
    )
    return widget


def test_cant_authorize_yet(qtbot: QtBot):
    widget = _create_default_widget()

    qtbot.addWidget(widget)

    button = widget._authenticate_button
    passwordinput = widget._input
    notification_text = widget._notification_text

    assert not button.isEnabled()
    assert not passwordinput.isEnabled()
    assert notification_text.isHidden()


def test_with_selected_key_no_action(qtbot: QtBot):
    widget = _create_default_widget()
    qtbot.addWidget(widget)

    selected_key = YubikeyDetails(
        "testslot",
        "testkey",
        "123",
    )
    widget.toggle_input_field_ability(selected_key)

    button = widget._authenticate_button
    passwordinput = widget._input
    notification_text = widget._notification_text

    assert widget.get_value() == "123456"

    assert passwordinput.isEnabled()
    assert button.isEnabled()
    assert notification_text.isHidden()
