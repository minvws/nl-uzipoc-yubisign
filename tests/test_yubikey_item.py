from app.page.yubikeyitem import YubiKeyItemWidget
from pytestqt.qtbot import QtBot

from app.yubikey_details import YubikeyDetails


def test_widget_load(qtbot: QtBot):
    details = YubikeyDetails("slot1", "123", "myyubikey")

    widget = YubiKeyItemWidget(
        name=details.name,
        serial=details.serial,
        slot=details.slot,
        available=True,
    )
    qtbot.addWidget(widget)

    actual_details = widget.get_details()
    assert actual_details.name == details.name
    assert actual_details.slot == details.slot
    assert actual_details.serial == details.serial
