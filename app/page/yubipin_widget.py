from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFont


class YubiPinWidget(QWidget):
    _input: QLineEdit

    def __init__(self, parent: QWidget | None, flags: Qt.WindowType) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()

        label = QLabel("YubiKey PIN")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)

        pin_input = QLineEdit()
        pin_input.setEchoMode(QLineEdit.EchoMode.Password)

        # TODO add authenticate button :D

        layout.addWidget(pin_input)

        button = QPushButton()
        button.setText("Authenticate")
        layout.addWidget(button)

        # Set this layout as the layout of the widget
        self.setLayout(layout)

        self._input = pin_input

    def has_value(self) -> bool:
        return self.get_value() is not None

    def get_value(self) -> str:
        return self._input.text()
