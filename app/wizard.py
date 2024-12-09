from os import getenv
from pathlib import Path
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

import urllib.parse
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent

DEFAULT_ACME_CA_SERVER_URL = "https://acme.proeftuin.uzi-online.rdobeheer.nl/directory"
DEFAULT_YUBIKEY_PIN = "123456"
DEFAULT_PROEFTUIN_OIDC_LOGIN_URL = "https://proeftuin.uzi-online.irealisatie.nl"


class MainWindow(QMainWindow):
    def __init__(self, mypkcs, myacme, oidc_provider_base_url: urllib.parse.ParseResult):
        super().__init__()

        self.setWindowTitle("YubiKey Wizard")
        self.resize(1024, 768)

        # Create the wizard
        self.wizard = QWizard()
        self.wizard.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.wizard.addPage(WelcomePage())
        self.wizard.addPage(SelectYubiKeyPage(mypkcs))
        self.wizard.addPage(CreateRSAKeysPage(mypkcs))
        self.wizard.addPage(LoginWithDigiDPage(myacme, oidc_provider_base_url))
        self.wizard.addPage(RequestCertificatePage(mypkcs, myacme))
        self.wizard.addPage(SaveToYubiKeyPage(mypkcs))
        self.wizard.setWindowTitle("YubiKey Wizard")

        # When the wizard has finished, close the application
        self.wizard.finished.connect(QApplication.instance().quit)

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

    oidc_provider_url = urllib.parse.urlparse(getenv("OIDC_PROVIDER_BASE_URL", DEFAULT_PROEFTUIN_OIDC_LOGIN_URL))
    print(
        f'Using OIDC base URL "{oidc_provider_url.geturl()}"',
    )

    acme_ca_server_url = urllib.parse.urlparse(getenv("ACME_SERVER_DIRECTORY_URL", DEFAULT_ACME_CA_SERVER_URL))
    print(
        f'Using ACME server directory URL "{acme_ca_server_url.geturl()}"',
    )

    directory_config = ACMEDirectoryConfigurationParser().parse(acme_ca_server_url)
    acme = ACME(directory_config)

    mainWindow = MainWindow(pkcscls, acme, oidc_provider_url)
    mainWindow.show()
    app.exec()
