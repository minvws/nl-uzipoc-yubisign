from typing import Any, Optional
from PyQt6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
)

from .yubikeyitem import YubiKeyItemWidget


class SelectYubiKeyPage(QWizardPage):
    selectedYubiKey: Optional[Any]
    yubikeyListWidget: QListWidget

    def _get_yubikeys(self):
        keys = []
        for slot in self.pkcs.pkcs11.getSlotList():
            try:
                info = self.pkcs.pkcs11.getTokenInfo(slot)
                keys += [(info.model, info.serialNumber, info.label, slot)]
            except Exception:
                pass

        return keys

    def _build_yubikey_list_widget(self, yubikeys: list[Any]) -> QListWidget:
        widget = QListWidget()
        # widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        for name, serial, available, slot in yubikeys:
            itemWidget = YubiKeyItemWidget(name, serial, available, slot)
            item = QListWidgetItem()
            item.setSizeHint(itemWidget.sizeHint())

            widget.addItem(item)
            widget.setItemWidget(item, itemWidget)

        return widget

    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)
        self.setTitle("Selecteer de te gebruiken yubikey")

        layout = QVBoxLayout(self)

        self.selectedYubiKey = None
        self.pkcs = mypkcs

        yubikeys = self._get_yubikeys()

        yubikey_list_widget = self._build_yubikey_list_widget(yubikeys)
        layout.addWidget(yubikey_list_widget)

        # Save it for later reference (can this be done better?)
        self.yubikeyListWidget = yubikey_list_widget

        # yubikey_list_widget.currentItemChanged.connect(self.on_yubikey_row_change)

        # # yubikey_list_widget.currentRowChanged.connect(self.yubiKeySelected)
        # yubikey_list_widget.itemClicked.connect(self.on_yubikey_row_click)

    def on_yubikey_row_click(self, item: QListWidgetItem):
        # TODO check here for current selection??? otherwise do nothing
        # TODO de-select the yubikey on page exit
        if item is not None:
            # Assuming the YubiKeyItemWidget has a method or property to get the YubiKey details
            self.selectedYubiKey = self.yubikeyListWidget.itemWidget(item).getYubiKeyDetails()

            # The next button does not have to be enabled manually, just trigger the completion signal.
            # This will re-check the isCompleted function
            # https://doc.qt.io/qt-6/qwizardpage.html#completeChanged
            self.completeChanged.emit()

    def on_yubikey_row_change(self, current: QListWidgetItem, previous: Optional[QListWidgetItem]):
        # TODO check here for current selection??? otherwise select other one
        item_in_list = self.yubikeyListWidget.itemWidget(current)

        print(1)

    def isComplete(self) -> bool:
        return self.selectedYubiKey is not None

    def nextId(self):
        # Store the selected YubiKey information in the wizard
        self.wizard().setProperty("selectedYubiKey", self.selectedYubiKey)
        return super().nextId()

    def initializePage(self) -> None:
        super().initializePage()

        self.yubikeyListWidget.clearSelection()

        self.yubikeyListWidget.currentItemChanged.connect(self.on_yubikey_row_change)

        # yubikey_list_widget.currentRowChanged.connect(self.yubiKeySelected)
        self.yubikeyListWidget.itemClicked.connect(self.on_yubikey_row_click)
