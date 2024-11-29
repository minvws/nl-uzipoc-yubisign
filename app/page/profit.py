from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QLabel


class ProfitPage(QWizardPage):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setTitle("Profit???!!")
		layout = QVBoxLayout(self)
		label = QLabel("Congratulations! Process Completed.")
		layout.addWidget(label)
