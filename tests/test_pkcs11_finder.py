from unittest.mock import MagicMock, patch
from app.pkcs_lib_finder import PKCS11LibFinder, PyKCS11


@patch("app.pkcs_lib_finder.PyKCS11.PyKCS11Lib.load")
def test_env_file(load_mock: MagicMock):
    def badload(filepath: str | None = None, **kwargs):
        # Only raise an error when we're searching for a file
        if filepath:
            raise PyKCS11.PyKCS11Error("not able to find lib")

    load_mock.side_effect = badload
    # TODO mock the file open to not being able to find the file. Fallback to the env variable
    finder = PKCS11LibFinder()
    finder.find()
