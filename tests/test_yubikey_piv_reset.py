from unittest.mock import MagicMock, patch
import pytest
from app.yubikey_details import YubikeyDetails
from app.yubikey_piv_resetter import YubiKeyPIVResetter


@patch("app.yubikey_piv_resetter.subprocess.run")
def test_yubikey_reset_not_found(run_mock: MagicMock):
    run_mock.return_value.stdout.decode.return_value = "ERROR: Failed connecting to a YubiKey with serial: 1"

    details = YubikeyDetails("1", "1", "123")

    r = YubiKeyPIVResetter()

    with pytest.raises(Exception) as exc:
        r.reset(details)

    assert str(exc.value) == "Selected Yubikey could not be found."
