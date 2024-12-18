from os import getenv
import sys

from PyQt6.QtWidgets import (
    QApplication,
)

from app.acme_directory_configuration_parser import ACMEDirectoryConfigurationParser
from app.pkcs_lib_finder import PKCS11LibFinder

from .pkcs import pkcs
from .appacme import ACME

import urllib.parse


from .page.welcome import WelcomePage
from .page.selectkey import SelectYubiKeyPage
from .page.logindigid import LoginWithDigiDPage
from .page.creatersakey import CreateRSAKeysPage
from .page.requestcert import RequestCertificatePage
from .page.savetoyubi import SaveToYubiKeyPage


from PyQt6.QtWidgets import (
    QSizePolicy,
    QWizard,
)


class MainWindow(QWizard):
    def __init__(self, mypkcs, myacme, oidc_provider_base_url: urllib.parse.ParseResult):
        super().__init__()

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


class ApplicationBootstrapper:
    DEFAULT_ACME_CA_SERVER_URL = "https://acme.proeftuin.uzi-online.rdobeheer.nl/directory"
    DEFAULT_YUBIKEY_PIN = "123456"
    DEFAULT_PROEFTUIN_OIDC_LOGIN_URL = "https://proeftuin.uzi-online.irealisatie.nl"

    def _load_pkcs_wrapper(self) -> pkcs:
        yubikey_pin = getenv(
            "YUBIKEY_PIN",
        )

        # This will search default locations and fall back to the PYKCS11LIB environment variable
        pkcslib = PKCS11LibFinder().find()

        if not pkcslib:
            raise RuntimeError("The PKCS library was not found. Application can not start up.")

        pkcscls = pkcs(pykcs11lib=pkcslib, yubikey_pin=yubikey_pin)

        return pkcscls

    def start(self):
        app = QApplication(sys.argv)

        pkcscls: pkcs = self._load_pkcs_wrapper()

        oidc_provider_url = urllib.parse.urlparse(
            getenv("OIDC_PROVIDER_BASE_URL", self.DEFAULT_PROEFTUIN_OIDC_LOGIN_URL)
        )
        print(
            f'Using OIDC base URL "{oidc_provider_url.geturl()}"',
        )

        acme_ca_server_url = urllib.parse.urlparse(getenv("ACME_SERVER_DIRECTORY_URL", self.DEFAULT_ACME_CA_SERVER_URL))
        print(
            f'Using ACME server directory URL "{acme_ca_server_url.geturl()}"',
        )

        directory_config = ACMEDirectoryConfigurationParser().parse(acme_ca_server_url)
        acme = ACME(directory_config)

        mainWindow = MainWindow(pkcscls, acme, oidc_provider_url)
        mainWindow.show()
        app.exec()
