from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QWidget,
)
from PyQt6.QtGui import QFont

from app.yubikey_details import YubikeyDetails


class YubiKeyItemWidget(QWidget):
    def __init__(self, name, serial, available, slot):
        super().__init__()

        layout = QVBoxLayout()

        nameLabel = QLabel(name)
        nameLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(nameLabel)

        serialLabel = QLabel(f"Serial: {serial}")
        layout.addWidget(serialLabel)

        availableLabel = QLabel(f"Available: {'yes' if available else 'no'}")
        layout.addWidget(availableLabel)

        self.setLayout(layout)
        self.slot = slot
        self.name = name
        self.serial = serial

    def getYubiKeyDetails(self):
        return self.slot, self.name, self.serial

    def get_details(self) -> YubikeyDetails:
        return YubikeyDetails(slot=self.slot, name=self.name, serial=self.serial.strip())
