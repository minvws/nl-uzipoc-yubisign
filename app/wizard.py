from os import getenv
import sys

from PyQt6.QtWidgets import (
	QApplication,
	QMainWindow,
	QSizePolicy,
	QWizard,
)

from .pkcs import pkcs
from .appacme import ACME
from .page.welcome import WelcomePage
from .page.selectkey import SelectYubiKeyPage
from .page.logindigid import LoginWithDigiDPage
from .page.creatersakey import CreateRSAKeysPage
from .page.requestcert import RequestCertificatePage
from .page.savetoyubi import SaveToYubiKeyPage
from .page.profit import ProfitPage

from dotenv import load_dotenv

import urllib.parse

DEFAULT_ACME_CA_SERVER_URL = "https://acme.proeftuin.uzi-online.irealisatie.nl"
DEFAULT_YUBIKEY_PIN = "123456"
DEFAULT_PROEFTUIN_OIDC_LOGIN_URL = "https://proeftuin.uzi-online.irealisatie.nl"


class MainWindow(QMainWindow):
	def __init__(
		self, mypkcs, myacme, oidc_provider_base_url: urllib.parse.ParseResult
	):
		super().__init__()
		self.setWindowTitle("YubiKey Wizard")
		self.resize(1024, 768)

		# Create the wizard
		self.wizard = QWizard()
		self.wizard.setSizePolicy(
			QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
		)
		self.wizard.addPage(WelcomePage())
		self.wizard.addPage(SelectYubiKeyPage(mypkcs))
		self.wizard.addPage(CreateRSAKeysPage(mypkcs))
		self.wizard.addPage(LoginWithDigiDPage(myacme, oidc_provider_base_url))
		self.wizard.addPage(RequestCertificatePage(mypkcs, myacme))
		self.wizard.addPage(SaveToYubiKeyPage(mypkcs))
		self.wizard.addPage(ProfitPage())
		self.wizard.setWindowTitle("YubiKey Wizard")

		# Set the wizard as the central widget of the main window
		self.setCentralWidget(self.wizard)


if __name__ == "__main__":
	load_dotenv()
	app = QApplication(sys.argv)

	oidc_provider_url = urllib.parse.urlparse(
		getenv("OIDC_PROVIDER_BASE_URL", DEFAULT_PROEFTUIN_OIDC_LOGIN_URL)
	)
	acme_ca_server_url = urllib.parse.urlparse(
		getenv("ACME_CA_SERVER", DEFAULT_ACME_CA_SERVER_URL)
	)
	yubikey_pin = getenv(
		"YUBIKEY_PIN",
	)
	pkcsobj = pkcs(yubikey_pin)
	acme = ACME(acme_ca_server_url)

	mainWindow = MainWindow(pkcsobj, acme, oidc_provider_url)
	mainWindow.show()
	app.exec()
