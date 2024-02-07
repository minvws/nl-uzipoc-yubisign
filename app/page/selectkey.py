from PyQt6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QListWidget,
    QWizard,
    QListWidgetItem,
)

from .yubikeyitem import YubiKeyItemWidget


class SelectYubiKeyPage(QWizardPage):
    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)
        self.setTitle("Selecteer de te gebruiken yubikey")

        layout = QVBoxLayout(self)

        self.yubikeyListWidget = QListWidget()

        self.selectedYubiKey = None
        self.yubikeyListWidget.currentItemChanged.connect(self.yubiKeySelected)
        self.pkcs = mypkcs

        # Sample YubiKeys
        yubikeys = []
        for slot in self.pkcs.pkcs11.getSlotList():
            try:
                info = self.pkcs.pkcs11.getTokenInfo(slot)
                yubikeys += [(info.model, info.serialNumber, info.label, slot)]
            except:
                pass

        for name, serial, available, slot in yubikeys:
            itemWidget = YubiKeyItemWidget(name, serial, available, slot)
            item = QListWidgetItem()
            self.yubikeyListWidget.addItem(item)
            self.yubikeyListWidget.setItemWidget(item, itemWidget)
            item.setSizeHint(itemWidget.sizeHint())

        layout.addWidget(self.yubikeyListWidget)

        self.yubikeyListWidget.currentItemChanged.connect(self.enableNextButton)

    def yubiKeySelected(self, current, _previous):
        if current is not None:
            # Assuming the YubiKeyItemWidget has a method or property to get the YubiKey details
            self.selectedYubiKey = self.yubikeyListWidget.itemWidget(
                current
            ).getYubiKeyDetails()
            self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(True)

    def nextId(self):
        # Store the selected YubiKey information in the wizard
        self.wizard().setProperty("selectedYubiKey", self.selectedYubiKey)
        return super().nextId()

    def initializePage(self):
        self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(False)

    def enableNextButton(self):
        self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(True)
