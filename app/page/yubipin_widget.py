from typing import Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QWidget, QPushButton

from app.yubikey_details import YubikeyDetails

from PyKCS11 import PyKCS11Lib, PyKCS11Error


class YubiPinWidget(QWidget):
    _pin_label = QLabel
    _input: QLineEdit
    _authenticate_button: QPushButton
    _notification_text: QLabel

    # What if we have a signal that can send a change with a yubikey or nothing. Then we don't need a booleand
    # We can't enforce this into a Optional[YubikeyDetails], so we have to do it like this
    _selectedYubiKeySignal = pyqtSignal(object)

    # This will get updated based on the incoming event
    _selected_yubikey: Optional[YubikeyDetails]

    # The lib used for authenticating
    _pykcs_lib: PyKCS11Lib

    # This is being passed in by a parent
    _pin_authenticated_signal: pyqtSignal

    def _build_label(self):
        label = QLabel("PIN")
        label.setEnabled(False)

        return label

    def _build_input(self):
        # TODO do we want to fill in the default value?
        i = QLineEdit()

        # By default, the button is enabled, but should be enabled when a YubiKey is selected
        i.setEnabled(False)
        i.setEchoMode(QLineEdit.EchoMode.Password)

        i.textChanged.connect(self._on_pin_edit)

        return i

    def _build_auth_button(self):
        button = QPushButton("Authenticate")
        button.setEnabled(False)
        button.clicked.connect(self._authenticate)

        return button

    def _setup_ui(self):
        layout = QHBoxLayout()

        label = self._build_label()
        layout.addWidget(label)
        self._pin_label = label

        pin_input = self._build_input()
        layout.addWidget(pin_input)

        button = self._build_auth_button()
        layout.addWidget(button)

        notification_text = QLabel()
        notification_text.hide()
        layout.addWidget(notification_text)
        self._notification_text = notification_text

        # Set this layout as the layout of the widget
        self.setLayout(layout)

        self._selectedYubiKeySignal.connect(self._internal_select_yubikey)
        self._input = pin_input
        self._authenticate_button = button

    def __init__(self, pykcs11lib: PyKCS11Lib, pin_authenticated_signal: pyqtSignal) -> None:
        super().__init__(None)
        self._setup_ui()
        self._pykcs_lib = pykcs11lib
        self._selected_yubikey = None
        self._pin_authenticated_signal = pin_authenticated_signal

    def get_value(self) -> str:
        return self._input.text()

    def _selected_yubikey_slot_available(self) -> bool:
        return self._selected_yubikey.slot in self._pykcs_lib.getSlotList()

    def _yubikey_available(self) -> bool:
        if not self._selected_yubikey:
            return False

        if not self._selected_yubikey_slot_available():
            return False

        return True

    def _is_pin_valid_to_yubikey(self) -> bool:
        try:
            pin = self.get_value()
            session = self._pykcs_lib.openSession(self._selected_yubikey.slot)

            # This will throw an exception if the pin is incorrect
            session.login(pin)
        except PyKCS11Error:
            return False

        return True

    def _notify_pin_ok(self):
        self._notification_text.setText("OK")
        self._notification_text.show()

    def _notify_pin_incorrect(self):
        self._notification_text.setText("PIN incorrect")
        self._notification_text.show()

    def _authenticate(self):
        # TODO shouldn't this an event configured by the upper class?
        if not self._yubikey_available():
            return

        authenticated: bool = self._is_pin_valid_to_yubikey()

        if not authenticated:
            self._notify_pin_incorrect()
            return

        self._notify_pin_ok()
        self._pin_authenticated_signal.emit()

        # TODO should we disable the auth button again?
        # TODO should we add a loading state?

    def _on_pin_edit(self, value: str):
        empty_text: bool = bool(not value.strip())
        disable_auth_button: bool = empty_text and self._authenticate_button.isEnabled()

        self._authenticate_button.setEnabled(not disable_auth_button)

    def toggle_input_field_ability(self, details: Optional[YubikeyDetails]):
        self._selectedYubiKeySignal.emit(details)

    def _internal_select_yubikey(self, details: Optional[YubikeyDetails]):
        on = details is not None

        # Update the selected yubikey
        self._selected_yubikey = details

        self._pin_label.setEnabled(on)
        self._input.setEnabled(on)

        # We don't want to always enable the auth button. Text has to be in there too.
        if not on:
            self._authenticate_button.setEnabled(False)
