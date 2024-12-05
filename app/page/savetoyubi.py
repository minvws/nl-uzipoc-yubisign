from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QLabel


class SaveToYubiKeyPage(QWizardPage):
    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)
        self.pkcs = mypkcs

    def initializePage(self):
        self.setTitle("Save to YubiKey")
        layout = QVBoxLayout(self)
        label = QLabel("Keys and certificates have been saved to the YubiKey. Process completed.")
        layout.addWidget(label)
