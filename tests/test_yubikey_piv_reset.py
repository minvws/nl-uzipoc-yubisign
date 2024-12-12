import pytest
from app.yubikey_details import YubikeyDetails
from app.yubikey_piv_resetter import YubiKeyPIVResetter


def test_yubikey_reset_not_found():
    details = YubikeyDetails("1", "1", "123")

    r = YubiKeyPIVResetter()

    with pytest.raises(Exception) as exc:
        r.reset(details)

    assert str(exc.value) == "Selected Yubikey could not be found."
