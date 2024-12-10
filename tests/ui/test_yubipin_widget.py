from unittest import mock
from unittest.mock import MagicMock
from pytestqt.qtbot import QtBot

from app.page.yubipin_widget import YubiPinWidget

from app.yubikey_details import YubikeyDetails


def _create_default_widget():
    pykcslib = MagicMock()
    widget = YubiPinWidget(pykcs11lib=pykcslib)
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


def test_auth_key_not_available(qtbot: QtBot):
    widget = _create_default_widget()
    qtbot.addWidget(widget)

    on_pin_auth_mock = mock.Mock(wraps=lambda _: ...)

    selected_key = YubikeyDetails(
        "testslot",
        "testkey",
        "123",
    )
    widget.toggle_input_field_ability(selected_key)
    widget.pin_authenticated_signal.connect(on_pin_auth_mock)

    with qtbot.waitSignal(widget.pin_authenticated_signal, timeout=5000):
        widget._authenticate_button.click()

    assert widget._notification_text.text() == "PIN incorrect"
    on_pin_auth_mock.assert_called_once_with(False)


def test_auth_pin_ok(qtbot: QtBot):
    selected_key = YubikeyDetails(
        "testslot",
        "testkey",
        "123",
    )
    # TODO mock the pkcs library to fake a login session
    pykcslib = MagicMock()
    pykcslib.getSlotList.return_value = [selected_key.slot]
    pykcslib.openSession.return_value.login.return_value = True

    widget = YubiPinWidget(pykcs11lib=pykcslib)
    qtbot.addWidget(widget)

    on_pin_auth_mock = mock.Mock(wraps=lambda _: ...)

    widget.toggle_input_field_ability(selected_key)
    widget.pin_authenticated_signal.connect(on_pin_auth_mock)

    with qtbot.waitSignal(widget.pin_authenticated_signal, timeout=5000):
        widget._authenticate_button.click()

    assert widget._notification_text.text() == "OK"
    on_pin_auth_mock.assert_called_once_with(True)
