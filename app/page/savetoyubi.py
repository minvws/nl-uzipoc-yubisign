from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QLabel


class SaveToYubiKeyPage(QWizardPage):
	def __init__(self, mypkcs, parent=None):
		super().__init__(parent)
		self.pkcs = mypkcs

	def initializePage(self):
		self.setTitle("Save to YubiKey")
		layout = QVBoxLayout(self)
		# Placeholder for YubiKey saving logic
		label = QLabel("Save Keys and Certificate to YubiKey (already done)")
		layout.addWidget(label)
