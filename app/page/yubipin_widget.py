from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont


class YubiPinWidget(QWidget):
    _input: QLineEdit
    _authenticate_button: QPushButton

    def __init__(self) -> None:
        super().__init__(None)
        layout = QHBoxLayout()

        label = QLabel("YubiKey PIN")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)

        pin_input = QLineEdit()

        # By default, the button is enabled, but should be enabled when a YubiKey is selected
        pin_input.setEnabled(False)
        pin_input.setEchoMode(QLineEdit.EchoMode.Password)

        pin_input.textChanged.connect(self._on_pin_edit)

        layout.addWidget(pin_input)

        button = QPushButton("Authenticate")
        button.setEnabled(False)
        button.clicked.connect(self._authenticate)

        layout.addWidget(button)

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
