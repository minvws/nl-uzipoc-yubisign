import os
from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QCheckBox, QLabel, QWizard
from PyQt6.QtCore import QTimer
import PyKCS11
from .worker import Worker


class CreateRSAKeysPage(QWizardPage):
    currentStep = 0
    totalSteps = 0
    alreadycalled = None

    emptyWarningCheckbox: QCheckBox
    yubiKeyInfoLabel: QLabel
    progressLabel: QLabel

    def _build_checkbox(self) -> QCheckBox:
        checkbox = QCheckBox("I understand that the YubiKey will be emptied")
        checkbox.setStyleSheet("color: red")
        checkbox.toggled.connect(self.updateNextButtonStatus)

        return checkbox

    def _setup_ui(self):
        self.setTitle("Create RSA Keys")

        layout = QVBoxLayout(self)

        self.emptyWarningCheckbox = self._build_checkbox()
        layout.addWidget(self.emptyWarningCheckbox)

        self.progressLabel = QLabel("Key creation progress will be displayed here.")
        layout.addWidget(self.progressLabel)

        self.yubiKeyInfoLabel = QLabel("YubiKey information will be displayed here.")
        layout.addWidget(self.yubiKeyInfoLabel)

    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)
        self._setup_ui()

        self.stepsCompleted = False
        self.pkcs = mypkcs
        self.threads = []

    def _reset_yubikey_configuration(self):
        os.system("ykman piv reset --force")

    def nextId(self):
        print("**   nextID called", self.stepsCompleted, self.alreadycalled)
        if self.alreadycalled and not self.stepsCompleted:
            return self.wizard().currentId()

        if self.stepsCompleted:
            print("Completed")
            return super().nextId()
        if self.is_selected_yubikey_filled() and not self.emptyWarningCheckbox.isChecked():
            # If the YubiKey is filled and the checkbox is not checked, do not proceed
            print("Not Completed 0")
            return self.wizard().currentId()

        if self.is_selected_yubikey_filled():
            # Decide whether we want this, because if this resets the PIN?
            # This also fails on my machine: ykman: command not found.
            self._reset_yubikey_configuration()

        # Start the key creation process
        QTimer.singleShot(1000, self.startKeyCreationProcess)

        self.alreadycalled = True
        print("Completed -1")

        current_page_id = self.wizard().currentId()
        return current_page_id

    def isComplete(self):
        if self.alreadycalled and not self.stepsCompleted:
            return False
        return True

    def startKeyCreationProcess(self):
        self.currentStep = 1
        self.totalSteps = 4
        self.stepsCompleted = False
        self.updateProgress()

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
        selectedYubiKeySlot, _, _ = self.wizard().property("selectedYubiKey")
        worker = Worker(self.pkcs, self.currentStep, selectedYubiKeySlot)
        worker.finished.connect(self.finishCurrentStep)
        worker.run()
        print("Worker", self.currentStep)
        # self.finishCurrentStep()

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
            self.wizard().next()  # Programmatically trigger the Next button

    def initializePage(self):
        self.alreadycalled = False
        selectedYubiKey = self.wizard().property("selectedYubiKey")
        self.yubiKeyInfoLabel.setText(f"YubiKey Selected: {selectedYubiKey}")
        self.pkcs.listattest(selectedYubiKey[0])

        yubiKeyFilled = self.is_selected_yubikey_filled()

        if yubiKeyFilled:
            self.emptyWarningCheckbox.show()
        else:
            self.emptyWarningCheckbox.hide()

        self.updateNextButtonStatus()

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

        selectedYubiKeySlot, _, _ = self.wizard().property("selectedYubiKey")
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

    def updateNextButtonStatus(self):
        yubiKeyFilled = self.is_selected_yubikey_filled()
        checkboxChecked = self.emptyWarningCheckbox.isChecked()
        self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(not yubiKeyFilled or checkboxChecked)
