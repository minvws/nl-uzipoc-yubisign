import logging
from subprocess import CompletedProcess
from app.yubikey_details import YubikeyDetails
import subprocess

logger = logging.getLogger()


class YubiKeyPIVResetter:
    """IMPORTANT NOTE: Use this class carefully, this will reset the whole PIV module of the selected YubiKey"""

    def _is_complete(self, result: CompletedProcess) -> bool:
        if result.stdout is None:
            return False

        actual: str = result.stdout.decode()
        expected_in_stdout = "Resetting PIV data...\nReset complete. All PIV data has been cleared from the YubiKey."

        ok = expected_in_stdout in actual

        return ok

    def _run_reset(self, yubikey_serial: str) -> CompletedProcess:
        cmdargs = [
            "ykman",
            f"--device={yubikey_serial} ",  # We need the extra space for the command to work
            "piv",
            "reset",
            "--force",
        ]
        result = subprocess.run(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result

    def _validate_cmd_result(self, result: CompletedProcess):
        decoded = result.stdout.decode()

        if decoded == "":
            raise Exception("The command returned an empty string")

        if "ERROR: Failed connecting to a YubiKey with serial:" in decoded:
            raise Exception("Selected Yubikey could not be found.")

    def _log_result(self, resetted: bool):
        if resetted:
            logger.info("Yubikey successfully resetted")

    def reset(self, yubikey: YubikeyDetails) -> bool:
        logger.info(
            f"Resetting the PIV module for Yubikey with serial {yubikey.serial}...",
        )
        result: CompletedProcess = self._run_reset(yubikey.serial)
        self._validate_cmd_result(result)

        ok = self._is_complete(result)

        if not ok:
            logger.warning(
                "Yubikey was not reset.",
            )
        else:
            logger.info(
                f"Yubikey with serial {yubikey.serial} was successfully reset",
            )

        return ok
