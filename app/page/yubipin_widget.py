from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont


class YubiPinWidget(QWidget):
    _input: QLineEdit
    _authenticate_button: QPushButton

    # The bool is an indicator for the on/off toggle
    _yubiKeySelectedSignal = pyqtSignal(bool)

    def _build_label(self):
        label = QLabel("YubiKey PIN")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        return label

    def _build_input(self):
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

    def __init__(self) -> None:
        super().__init__(None)
        layout = QHBoxLayout()

        label = self._build_label()
        layout.addWidget(label)

        pin_input = self._build_input()
        layout.addWidget(pin_input)

        button = self._build_auth_button()
        layout.addWidget(button)

        # Make this work with de-selecting as well
        self._yubiKeySelectedSignal.connect(self._internal_toggle_input)

        # Set this layout as the layout of the widget
        self.setLayout(layout)

        self._input = pin_input
        self._authenticate_button = button

    def get_value(self) -> str:
        return self._input.text()

    def _authenticate(self):
        pin = self.get_value()
        # TODO shouldn't this an event configured by the upper class?
        # TODO do we want to have an override by our environment variable?
        # TODO do we want to fill in the default value?
        # TODO select the correct yubikey here
        print("trying to authenticate")

    def _on_pin_edit(self, value: str):
        # We ceck if the value is not an empty string
        if not value.strip() and self._authenticate_button.isEnabled():
            self._authenticate_button.setEnabled(False)
        else:
            self._authenticate_button.setEnabled(True)

    def toggle_input_field_ability(self, on: bool):
        """on means that the input is useable"""
        # Why use signals?
        # TODO on disable, also set the authenticate button to off
        self._yubiKeySelectedSignal.emit(on)

    def _internal_toggle_input(self, on: bool):
        self._input.setEnabled(on)

        if not on:
            self._authenticate_button.setEnabled(False)
