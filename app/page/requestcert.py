from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from app import appacme


class RequestCertificatePage(QWizardPage):
    acme: appacme.ACME

    def __init__(self, mypkcs, myacme, parent=None):
        super().__init__(parent)
        self.acme = myacme
        self.pkcs = mypkcs

    def initializePage(self):
        QTimer.singleShot(500, self.natimer)

    def _get_yubikey_pin(self) -> str:
        return self.wizard().property("yubikey_pin")

    def natimer(self):
        self.setTitle("Request Certificate")
        layout = QVBoxLayout(self)
        label = QLabel("Certificate Requests")
        layout.addWidget(label)
        selectedYubiKeySlot, _, _ = self.wizard().property("selectedYubiKey")
        yubikey_pin = self._get_yubikey_pin()

        jwttoken = self.wizard().property("jwt_token")()
        f9crt = self.pkcs.getf9(selectedYubiKeySlot)
        for keynum in [4, 3, 2, 1]:
            hwattest = self.pkcs.getattest(selectedYubiKeySlot, keynum)
            self.acme.send_request(hwattest, jwttoken, keynum - 1, f9crt)
            self.acme.wait(keynum - 1)
            csr = self.pkcs.getcsr(selectedYubiKeySlot, keynum, yubikey_pin)
            cert = self.acme.final(keynum, csr, jwttoken)
            self.pkcs.savecert(selectedYubiKeySlot, keynum, cert)
        self.wizard().next()  # Programmatically trigger the Next button
