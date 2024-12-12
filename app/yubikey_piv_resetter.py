from subprocess import CompletedProcess
from app.yubikey_details import YubikeyDetails
import subprocess


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
            # We need the extra space for the command to work
            f"--device={yubikey_serial} ",
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

    def reset(self, yubikey: YubikeyDetails) -> bool:
        result: CompletedProcess = self._run_reset(yubikey.serial)

        # What's the return code? Can we work with that
        self._validate_cmd_result(result)

        ok = self._is_complete(result)

        return ok
