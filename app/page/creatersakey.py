from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QCheckBox, QLabel
from PyQt6.QtCore import QTimer

from app.yubikey_content_checker import YubikeyContentChecker
from app.yubikey_details import YubikeyDetails
from app.yubikey_piv_resetter import YubiKeyPIVResetter
from .worker import Worker


class CreateRSAKeysPage(QWizardPage):
    currentStep = 0
    totalSteps = 0

    _key_creation_started: bool
    _keys_created: bool

    _selected_yubikey: YubikeyDetails

    def _set_yelected_yubikey(self):
        key: YubikeyDetails = self.wizard().property("selected_yubikey")
        self._selected_yubikey = key

    def _build_checkbox(self):
        checkbox = QCheckBox("I understand that the YubiKey will be emptied")
        checkbox.hide()
        checkbox.setStyleSheet("color: red")

        # We simply rerun the isComplete function, since that checks on the isChecked
        checkbox.toggled.connect(lambda: self.completeChanged.emit())

        return checkbox

    def _setup_ui(self):
        self.setTitle("Create RSA Keys")

        layout = QVBoxLayout(self)

        checkbox = self._build_checkbox()
        layout.addWidget(checkbox)
        self._warning_checkbox = checkbox

        self.progressLabel = QLabel("Key creation progress will be displayed here.")
        layout.addWidget(self.progressLabel)

        self.yubiKeyInfoLabel = QLabel("YubiKey information will be displayed here.")
        layout.addWidget(self.yubiKeyInfoLabel)

    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)
        self._setup_ui()

        self._key_creation_started = False
        self._keys_created = False
        self.pkcs = mypkcs
        self.threads = []

    def nextId(self):
        # This should not happen since the isComplete didn't become true yets
        if self._yubikey_filled() and not self._accepted_risks():
            return self.wizard().currentId()

        if self._key_creation_started and not self._keys_created:
            return self.wizard().currentId()

        if self._keys_created:
            return super().nextId()

        # When the initial process starts, reset the key
        if self._yubikey_filled():
            YubiKeyPIVResetter().reset(self._selected_yubikey)

        self.start_key_creation()

        return self.wizard().currentId()

    def _accepted_risks(self) -> bool:
        return self._warning_checkbox.isChecked()

    def isComplete(self):
        if not self._accepted_risks():
            return False

        if self._key_creation_started and not self._keys_created:
            return False

        return True

    def start_key_creation(self):
        self._key_creation_started = True

        # Emit the signal so the button will get disabled
        self.completeChanged.emit()

        self.currentStep = 1
        self.totalSteps = 4
        self.updateProgress()

    def updateProgress(self):
        print(f"Creating key {self.currentStep} of {self.totalSteps}...")
        if self.currentStep > self.totalSteps:
            print("Alles gedaan")
            if not self._keys_created:
                self.progressLabel.setText("All keys created.")
                self._keys_created = True
                self.completeKeyCreationProcess()
            return
        self.progressLabel.setText(f"Creating key {self.currentStep} of {self.totalSteps}...")

        worker = Worker(self.pkcs, self.currentStep, self._selected_yubikey.slot)
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
        if self._keys_created:
            self.wizard().next()

    def initializePage(self):
        self._set_yelected_yubikey()

        self.yubiKeyInfoLabel.setText(f"YubiKey Selected: {self._selected_yubikey.serial}")
        self.pkcs.listattest(self._selected_yubikey.slot)

        # The checkbox is hidden by default
        if self._yubikey_filled():
            self._warning_checkbox.show()

    def _yubikey_filled(self):
        return YubikeyContentChecker(self.pkcs).check(self._selected_yubikey)
