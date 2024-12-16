from os import getenv
from pathlib import Path


from PyQt6.QtWidgets import (
    QApplication,
    QSizePolicy,
    QWizard,
)
from PyQt6.QtCore import Qt


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


class MainWindow(QWizard):
    def __init__(self, mypkcs, myacme, oidc_provider_base_url: urllib.parse.ParseResult):
        self.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowTitle("YubiKey Wizard")
        self.resize(1024, 768)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.addPage(WelcomePage())
        self.addPage(SelectYubiKeyPage(mypkcs))
        self.addPage(CreateRSAKeysPage(mypkcs))
        self.addPage(LoginWithDigiDPage(myacme, oidc_provider_base_url))
        self.addPage(RequestCertificatePage(mypkcs, myacme))
        self.addPage(SaveToYubiKeyPage(mypkcs))

        # When the wizard has finished, close the application
        self.finished.connect(QApplication.instance().quit)


if __name__ == "__main__":
    load_dotenv()

    app = QApplication([])

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
