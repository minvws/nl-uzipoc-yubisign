from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from app import appacme
from app.yubikey_details import YubikeyDetails


class RequestCertificatePage(QWizardPage):
    acme: appacme.ACME

    def __init__(self, mypkcs, myacme, parent=None):
        super().__init__(parent)
        self.acme = myacme
        self.pkcs = mypkcs

    def initializePage(self):
        QTimer.singleShot(500, self.natimer)

    def _get_selected_yubikey(self) -> YubikeyDetails:
        return self.wizard().property("selected_yubikey")

    def natimer(self):
        self.setTitle("Request Certificate")
        layout = QVBoxLayout(self)
        label = QLabel("Certificate Requests")
        layout.addWidget(label)

        selected_yubikey = self._get_selected_yubikey()
        slot = selected_yubikey.slot

        jwttoken = self.wizard().property("jwt_token")()
        f9crt = self.pkcs.getf9(slot)

        for keynum in [4, 3, 2, 1]:
            hwattest = self.pkcs.getattest(slot, keynum)
            self.acme.send_request(hwattest, jwttoken, keynum - 1, f9crt)
            self.acme.wait(keynum - 1)
            csr = self.pkcs.getcsr(slot, keynum)
            cert = self.acme.final(keynum, csr, jwttoken)
            self.pkcs.savecert(slot, keynum, cert)
        self.wizard().next()  # Programmatically trigger the Next button
