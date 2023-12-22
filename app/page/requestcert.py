from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer


class RequestCertificatePage(QWizardPage):
    def __init__(self, mypkcs, myacme, parent=None):
        super().__init__(parent)
        self.acme = myacme
        self.pkcs = mypkcs

    def initializePage(self):
        QTimer.singleShot(500, self.natimer)

    def natimer(self):
        self.setTitle("Request Certificate")
        layout = QVBoxLayout(self)
        label = QLabel("Certificate Requests")
        layout.addWidget(label)
        selectedYubiKeySlot, _, _ = self.wizard().property("selectedYubiKey")
        jwttoken = self.wizard().property("jwt_token")()
        hwattest = self.pkcs.attest.decode()
        print("JWT", jwttoken)
        print("Attest", hwattest)
        for keynum in [1, 2, 3, 4]:
            # newacme = ACME("https://acme.proeftuin.uzi-online.rdobeheer.nl/")
            newacme = self.acme
            newacme.order()
            newacme.getchallenge()
            newacme.send_request(hwattest, jwttoken)
            newacme.wait()
            csr = self.pkcs.getcsr(selectedYubiKeySlot, keynum)
            cert = newacme.final(csr)
            self.pkcs.savecert(selectedYubiKeySlot, keynum, cert)
        self.wizard().next()  # Programmatically trigger the Next button
