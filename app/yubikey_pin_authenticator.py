from app.yubikey_details import YubikeyDetails

from PyKCS11 import PyKCS11Lib, PyKCS11Error


class YubikeyPINAuthenticator:
    _pykcs11lib: PyKCS11Lib

    def __init__(self, pykcs11lib: PyKCS11Lib):
        self._pykcs11lib = pykcs11lib

    def _selected_yubikey_slot_available(self, key: YubikeyDetails) -> bool:
        return key.slot in self._pykcs11lib.getSlotList()

    def _key_available(self, key: YubikeyDetails) -> bool:
        if not key:
            return False

        if not self._selected_yubikey_slot_available(key):
            return False

        return True

    def _is_pin_valid_to_yubikey(self, slot: str, pin: str) -> bool:
        try:
            session = self._pykcs11lib.openSession(slot)

            # This will throw an exception if the pin is incorrect
            session.login(pin)
        except PyKCS11Error as exc:
            session.closeSession()
            return False

        # Currently, since it's just validation, we log the user out
        session.logout()
        session.closeSession()

        return True

    def login(self, key: YubikeyDetails, pin: str) -> bool:
        if not self._key_available(key):
            return False

        return self._is_pin_valid_to_yubikey(key.slot, pin)
