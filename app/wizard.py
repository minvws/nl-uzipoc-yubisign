from os import getenv
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSizePolicy,
    QWizard,
)

from app.acme_directory_configuration_parser import ACMEDirectoryConfigurationParser
from app.pkcs_lib_finder import PKCS11LibFinder

from .pkcs import pkcs
from .appacme import ACME
from .page.welcome import WelcomePage
from .page.selectkey import SelectYubiKeyPage
from .page.logindigid import LoginWithDigiDPage
from .page.creatersakey import CreateRSAKeysPage
from .page.requestcert import RequestCertificatePage
from .page.savetoyubi import SaveToYubiKeyPage
from .page.profit import ProfitPage

import urllib.parse
from dotenv import load_dotenv

DEFAULT_ACME_CA_SERVER_URL = (
    "https://acme.proeftuin.uzi-online.irealisatie.nl/directory"
)
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

    yubikey_pin = getenv(
        "YUBIKEY_PIN",
    )
    # This will search default locations and fall back to the PYKCS11LIB environment variable
    pkcslib = PKCS11LibFinder().find()
    pkcscls = pkcs(pykcs11lib=pkcslib, yubikey_pin=yubikey_pin)

    oidc_provider_url = urllib.parse.urlparse(
        getenv("OIDC_PROVIDER_BASE_URL", DEFAULT_PROEFTUIN_OIDC_LOGIN_URL)
    )
    acme_ca_server_url = urllib.parse.urlparse(
        getenv("ACME_SERVER_DIRECTORY_URL", DEFAULT_ACME_CA_SERVER_URL)
    )
    directory_config = ACMEDirectoryConfigurationParser().parse(acme_ca_server_url)
    acme = ACME(directory_config)

    mainWindow = MainWindow(pkcscls, acme, oidc_provider_url)
    mainWindow.show()
    app.exec()
