from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QCheckBox, QLabel, QWizard
from PyQt6.QtCore import QTimer

from app.yubikey_content_checker import YubikeyContentChecker
from app.yubikey_details import YubikeyDetails
from app.yubikey_piv_resetter import YubiKeyPIVResetter
from .worker import Worker


class CreateRSAKeysPage(QWizardPage):
    currentStep = 0
    totalSteps = 0
    alreadycalled = None

    _selected_yubikey: YubikeyDetails

    def _set_yelected_yubikey(self):
        slot, name, serial = self.wizard().property("selectedYubiKey")
        self._selected_yubikey = YubikeyDetails(slot=slot, name=name, serial=serial.strip())

    def _build_checkbox(self):
        checkbox = QCheckBox("I understand that the YubiKey will be emptied")
        checkbox.hide()
        checkbox.setStyleSheet("color: red")
        checkbox.toggled.connect(self.updateNextButtonStatus)

        return checkbox

    def _setup_ui(self):
        self.setTitle("Create RSA Keys")

        layout = QVBoxLayout(self)

        checkbox = self._build_checkbox()
        layout.addWidget(checkbox)
        self.emptyWarningCheckbox = checkbox

        self.progressLabel = QLabel("Key creation progress will be displayed here.")
        layout.addWidget(self.progressLabel)

        self.yubiKeyInfoLabel = QLabel("YubiKey information will be displayed here.")
        layout.addWidget(self.yubiKeyInfoLabel)

    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)
        self._setup_ui()

        self.stepsCompleted = False
        self.pkcs = mypkcs
        self.threads = []  # Keep track of threads

    def nextId(self):
        if self.alreadycalled and not self.stepsCompleted:
            return self.wizard().currentId()

        if self.stepsCompleted:
            return super().nextId()

        # This should not happen since the isComplete didn't become true yets
        if self._yubikey_filled() and not self.emptyWarningCheckbox.isChecked():
            return self.wizard().currentId()

        # When the initial process starts, reset the key
        if self._yubikey_filled():
            YubiKeyPIVResetter().reset(self._selected_yubikey)

        QTimer.singleShot(1000, self.startKeyCreationProcess)
        self.alreadycalled = True

        return self.wizard().currentId()

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
            self.wizard().next()

    def initializePage(self):
        self._set_yelected_yubikey()

        self.alreadycalled = False
        self.yubiKeyInfoLabel.setText(f"YubiKey Selected: {self._selected_yubikey.serial}")
        self.pkcs.listattest(self._selected_yubikey.slot)

        self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(False)

        # The checkbox is hidden by default
        if self._yubikey_filled():
            self.emptyWarningCheckbox.show()

        self.updateNextButtonStatus()

    def _yubikey_filled(self):
        return YubikeyContentChecker(self.pkcs).check(self._selected_yubikey)

    def updateNextButtonStatus(self):
        yubiKeyFilled = self._yubikey_filled()
        checkboxChecked = self.emptyWarningCheckbox.isChecked()
        self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(not yubiKeyFilled or checkboxChecked)
