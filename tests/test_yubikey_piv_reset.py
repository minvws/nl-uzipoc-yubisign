from unittest.mock import MagicMock, patch
import pytest
from app.yubikey_details import YubikeyDetails
from app.yubikey_piv_resetter import YubiKeyPIVResetter


@patch("app.yubikey_piv_resetter.subprocess.run")
def test_yubikey_reset_not_found(run_mock: MagicMock):
    run_mock.return_value.stdout.decode.return_value = "ERROR: Failed connecting to a YubiKey with serial: 1"

    details = YubikeyDetails("1", "1", "123")
    with pytest.raises(Exception) as exc:
        YubiKeyPIVResetter().reset(details)

    assert str(exc.value) == "Selected Yubikey could not be found."


@patch("app.yubikey_piv_resetter.subprocess.run")
def test_ykman_empty_result(run_mock: MagicMock):
    run_mock.return_value.stdout.decode.return_value = ""

    details = YubikeyDetails("1", "1", "123")

    with pytest.raises(Exception) as exc:
        YubiKeyPIVResetter().reset(details)

    assert str(exc.value) == "The command returned an empty string"


@patch("app.yubikey_piv_resetter.subprocess.run")
def test_ykman_runs_ok(run_mock: MagicMock):
    run_mock.return_value.stdout.decode.return_value = (
        "Resetting PIV data...\nReset complete. All PIV data has been cleared from the YubiKey."
    )

    details = YubikeyDetails("1", "30631123", "123")
    result = YubiKeyPIVResetter().reset(details)

    assert result is True
