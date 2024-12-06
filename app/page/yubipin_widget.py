from typing import Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont

from app.yubikey_details import YubikeyDetails


class YubiPinWidget(QWidget):
    _input: QLineEdit
    _authenticate_button: QPushButton

    # What if we have a signal that can send a change with a yubikey or nothing. Then we don't need a booleand
    # We can't enforce this into a Optional[YubikeyDetails], so we have to do it like this
    _selectedYubiKeySignal = pyqtSignal(object)

    # This will get updated based on the incoming event
    _selected_yubikey: Optional[YubikeyDetails]

    def _build_label(self):
        label = QLabel("YubiKey PIN")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        return label

    def _build_input(self):
        # TODO do we want to fill in the default value?
        # TODO do we want to have an override by our environment variable?
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

        pin_input = self._build_input()
        layout.addWidget(pin_input)

        button = self._build_auth_button()
        layout.addWidget(button)

        # Set this layout as the layout of the widget
        self.setLayout(layout)

        self._selectedYubiKeySignal.connect(self._internal_select_yubikey)
        self._input = pin_input
        self._authenticate_button = button

    def __init__(self) -> None:
        super().__init__(None)
        self._setup_ui()
        self._selected_yubikey = None

    def get_value(self) -> str:
        return self._input.text()

    def _authenticate(self):
        if not self._selected_yubikey:
            return

        pin = self.get_value()

        # TODO shouldn't this an event configured by the upper class?

        print("trying to authenticate")

    def _on_pin_edit(self, value: str):
        # We ceck if the value is not an empty string
        if not value.strip() and self._authenticate_button.isEnabled():
            self._authenticate_button.setEnabled(False)
        else:
            self._authenticate_button.setEnabled(True)

    def toggle_input_field_ability(self, details: Optional[YubikeyDetails]):
        """on means that the input is useable"""
        self._selectedYubiKeySignal.emit(details)

    def _internal_select_yubikey(self, details: Optional[YubikeyDetails]):
        on = details is not None

        # Update the selected yubikey
        self._selected_yubikey = details

        self._input.setEnabled(on)

        # We don't want to always enable the auth button. Text has to be in there too.
        if not on:
            self._authenticate_button.setEnabled(False)
