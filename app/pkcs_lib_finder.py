import logging
import pathlib
from typing import Optional
import PyKCS11

logger = logging.getLogger(__name__)


class PKCS11LibFinder:
    _MAC_SILLICON_HOMEBREW_LOCATION = pathlib.Path(
        "/opt/homebrew/lib/libykcs11.dylib",
    )
    _MAC_NON_SILLICON_DEFAULT_LOCATION = pathlib.Path("/usr/local/lib/libykcs11.dylib")

    _LINUX_X86_DEFAULT_PATH = pathlib.Path("/usr/lib/libykcs11.so")
    _LINUX_X64_DEFAULT_PATH = pathlib.Path("/usr/lib64/libykcs11.so")

    _WINDOWS_DEFAULT_LOCATION = pathlib.Path(
        "C:\\Program Files\\Yubico\\YubiKey PIV Tool\\ykcs11.dll"
    )
    _WINDOWS_DEFAULT_SYSTEM32_PATH = pathlib.Path("C:\\Windows\\System32\\ykcs11.dll")
    _WINDOWS_DEFAULT_SYSWOW64_PATH = pathlib.Path("C:\\Windows\\SysWOW64\\ykcs11.dll")

    def _load_lib_from_env(self) -> None:
        try:
            # This is being handled internally in the library pointing to the PYKCS11LIB variable
            lib = PyKCS11.PyKCS11Lib()
            lib.load()
        except Exception:
            return None

        return lib

    def _try_default_location(self, libpath: pathlib.Path):
        lib = PyKCS11.PyKCS11Lib()
        lib.load(str(libpath))

        return lib

    def _try_load_from_paths(
        self, paths: list[pathlib.Path]
    ) -> Optional[PyKCS11.PyKCS11Lib]:
        for path in paths:
            try:
                logger.info(f"Trying to parse libykcs11 library from {path}...")

                # This will throw an exception if the library was not found
                lib = self._try_default_location(path)
                return lib
            except PyKCS11.PyKCS11Error:
                logger.info(f"Failed to load library at {path}...")

                # If this raises an exception, try the next
                continue

        return None

    def _try_load_from_default_paths(self):
        defaults = [
            self._WINDOWS_DEFAULT_LOCATION,
            self._WINDOWS_DEFAULT_SYSTEM32_PATH,
            self._WINDOWS_DEFAULT_SYSWOW64_PATH,
            self._MAC_SILLICON_HOMEBREW_LOCATION,
            self._MAC_NON_SILLICON_DEFAULT_LOCATION,
            self._LINUX_X64_DEFAULT_PATH,
            self._LINUX_X86_DEFAULT_PATH,
        ]
        return self._try_load_from_paths(defaults)

    def find(self) -> PyKCS11.PyKCS11Lib:
        # If no defaults are found, return to PYKCS11LIB environment variable
        lib = self._load_lib_from_env() or self._try_load_from_default_paths()

        return lib
