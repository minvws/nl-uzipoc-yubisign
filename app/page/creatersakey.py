import os
from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QCheckBox, QLabel, QWizard
from PyQt6.QtCore import QTimer
import PyKCS11
from .worker import Worker


class CreateRSAKeysPage(QWizardPage):
    currentStep = 0
    totalSteps = 0

    _key_creation_called: bool
    _accepted_risks: bool

    emptyWarningCheckbox: QCheckBox
    yubiKeyInfoLabel: QLabel
    progressLabel: QLabel

    _selected_yubikey: tuple[str, str, str]

    def _build_checkbox(self) -> QCheckBox:
        checkbox = QCheckBox("I understand that the YubiKey will be emptied")
        checkbox.setStyleSheet("color: red")
        checkbox.toggled.connect(self._on_checkbox_toggle)

        if self.is_selected_yubikey_filled():
            checkbox.show()
        else:
            checkbox.hide()

        return checkbox

    def _setup_ui(self):
        self.setTitle("Create RSA Keys")

        layout = QVBoxLayout(self)

        self.emptyWarningCheckbox = self._build_checkbox()
        layout.addWidget(self.emptyWarningCheckbox)

        self.progressLabel = QLabel("Key creation progress will be displayed here.")
        layout.addWidget(self.progressLabel)

        self.yubiKeyInfoLabel.setText(f"YubiKey Selected: {self._selected_yubikey}")
        layout.addWidget(self.yubiKeyInfoLabel)

    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)

        self._selected_yubikey = self.wizard().property("selectedYubiKey")
        self._setup_ui()

        self._key_creation_called = False
        self._accepted_risks = False

        self.stepsCompleted = False
        self.pkcs = mypkcs
        self.threads = []

    def _reset_yubikey_configuration(self):
        os.system("ykman piv reset --force")

    def nextId(self):
        if self._key_creation_called and not self.stepsCompleted:
            return self.wizard().currentId()

        # If the YubiKey is filled and the checkbox is not checked, do not proceed
        # This should not happen, since the button can't be clicked
        if self.is_selected_yubikey_filled() and not self.emptyWarningCheckbox.isChecked():
            return self.wizard().currentId()

        if self.stepsCompleted:
            return super().nextId()

        if self.is_selected_yubikey_filled():
            # Decide whether we want this, because if this resets the PIN?
            # This also fails on my machine: ykman: command not found.
            self._reset_yubikey_configuration()

        # Start the key creation process
        QTimer.singleShot(1000, self.startKeyCreationProcess)

        self._key_creation_called = True

        current_page_id = self.wizard().currentId()
        return current_page_id

    def isComplete(self):
        # This is the first step and the first time the user should click on continue
        if not self._accepted_risks:
            return False

        # When the keys are being created (TODO can this be only one condition?)
        if self._key_creation_called and not self.stepsCompleted:
            return False

        return True

    def startKeyCreationProcess(self):
        self._key_creation_called = True

        self.currentStep = 1
        self.totalSteps = 4
        self.stepsCompleted = False
        self.updateProgress()

        self.completeChanged.emit()

    def updateProgress(self):
        print(f"Creating key {self.currentStep} of {self.totalSteps}...")
        if self.currentStep > self.totalSteps:
            print("Alles gedaan")
            if not self.stepsCompleted:
                self.progressLabel.setText("All keys created.")
                self.stepsCompleted = True
                self.completeKeyCreationProcess()
            return

        self.progressLabel.setText(f"Creating key {self.currentStep} of {self.totalSteps}...")
        selectedYubiKeySlot, _, _ = self._selected_yubikey
        worker = Worker(self.pkcs, self.currentStep, selectedYubiKeySlot)
        worker.finished.connect(self.finishCurrentStep)
        worker.run()
        print("Worker", self.currentStep)

    def finishCurrentStep(self):
        print("Called, should be finished")
        self.currentStep += 1
        if self.currentStep <= self.totalSteps:
            prevstep = self.currentStep - 1
            self.progressLabel.setText(f"Key {prevstep} of {self.totalSteps}... Done")
            if self.currentStep <= self.totalSteps:
                QTimer.singleShot(500, self.updateProgress)
        else:
            QTimer.singleShot(500, self.updateProgress)

    def completeKeyCreationProcess(self):
        if self.stepsCompleted:
            self.wizard().next()

    def initializePage(self):
        self.pkcs.listattest(self._selected_yubikey[0])

    def is_selected_yubikey_filled(self) -> bool:
        finds = {x: {y: False for y in range(3)} for x in range(4)}

        HEADERS = [
            "X.509 Certificate",
            "Public key",
            "Private key",
            "PIV Attestation",
            "UZI Certificate",
        ]

        LABEL_MAPPING = {
            "PIV Authentication": " 9a",
            "Digital Signature": " 9c",
            "Key Management": "9d",
            "Card Authentication": " 9e",
        }

        selectedYubiKeySlot, _, _ = self._selected_yubikey
        session = self.pkcs.getsession(selectedYubiKeySlot)
        for col, cko_type in enumerate(
            [
                PyKCS11.CKO_CERTIFICATE,
                PyKCS11.CKO_PUBLIC_KEY,
                PyKCS11.CKO_PRIVATE_KEY,
                PyKCS11.CKO_CERTIFICATE,
            ]
        ):
            all_objects = session.findObjects([(PyKCS11.CKA_CLASS, cko_type)])
            for row, (x, y) in enumerate(LABEL_MAPPING.items()):
                for obj in all_objects:
                    label = session.getAttributeValue(obj, [PyKCS11.CKA_LABEL])[0]
                    if label == HEADERS[col] + " for " + x and col < 3:
                        finds[col][row] = True
                        break
                    if label == "X.509 Certificate for PIV Attestation" + y and col == 3:
                        finds[col][row] = True
                        break
        self.pkcs.delsession(selectedYubiKeySlot)
        print(finds)
        return any(value for inner_dict in finds.values() for value in inner_dict.values())

    def _on_checkbox_toggle(self):
        self._accepted_risks = self.emptyWarningCheckbox.isChecked()
        self.completeChanged.emit()
