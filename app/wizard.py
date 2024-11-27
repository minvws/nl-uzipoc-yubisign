import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSizePolicy,
    QWizard,
)

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


class MainWindow(QMainWindow, pkcs):
    def __init__(self, mypkcs, myacme):
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
        self.wizard.addPage(LoginWithDigiDPage(myacme))
        self.wizard.addPage(RequestCertificatePage(mypkcs, myacme))
        self.wizard.addPage(SaveToYubiKeyPage(mypkcs))
        self.wizard.addPage(ProfitPage())
        self.wizard.setWindowTitle("YubiKey Wizard")

        # Set the wizard as the central widget of the main window
        self.setCentralWidget(self.wizard)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # This will search default locations and fall back to the PYKCS11LIB environment variable
    pkcslib = PKCS11LibFinder().find()

    pkcs = pkcs(pkcslib)

    # This expects the new ACME server to run on this port. Later on, make this configurable
    acme = ACME("http://localhost:8080/")

    mainWindow = MainWindow(pkcs, acme)
    mainWindow.show()
    app.exec()
