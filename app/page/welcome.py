from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QTextBrowser


class WelcomePage(QWizardPage):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setTitle("Welcome")

		layout = QVBoxLayout(self)

		htmlContent = """
        <html>
                <body style='background: transparent;'>
                 <img src="images/ro-logo.svg" alt="Logo Rijksoverheid">Rijksoverheid
                <h1>Welkom bij de demo digitaal ondertekenen</h1>
                <p>Met deze applicatie is een YubiKey te vullen met een demo-uzi-certifcaat</p>
            </body>
        </html>
        """

		htmlView = QTextBrowser()
		htmlView.setHtml(htmlContent)
		htmlView.setStyleSheet("background: transparent")
		layout.addWidget(htmlView)
