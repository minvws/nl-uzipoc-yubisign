from typing import Any, Optional
from PyQt6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
)

from .yubikeyitem import YubiKeyItemWidget


class SelectYubiKeyPage(QWizardPage):
    selected_key: Optional[Any]
    key_list_widget: QListWidget

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

        self.selected_key = None
        self.pkcs = mypkcs
        yubikeys = self._get_yubikeys()
        yubikey_list_widget = self._build_yubikey_list_widget(yubikeys)

        layout = QVBoxLayout(self)
        layout.addWidget(yubikey_list_widget)

        # Save it for later reference (can this be done better?)
        self.key_list_widget = yubikey_list_widget

    def _find_selected_widget_item(self) -> Optional[YubiKeyItemWidget]:
        selected_indexes = self.key_list_widget.selectedIndexes()

        if selected_indexes == []:
            return None

        # Only one should be selected
        first_row = selected_indexes[0].row()
        selected_item = self.key_list_widget.item(first_row)

        # Get the widget associated to the selected item
        widget = self.key_list_widget.itemWidget(selected_item)

        return widget

    def on_yubikey_item_change(self):
        selection = self._find_selected_widget_item()

        if not selection:
            return

        # Update the details
        self.selected_key = selection.getYubiKeyDetails()

        # The next button does not have to be enabled manually, just trigger the completion signal.
        # This will re-check the isCompleted function
        # https://doc.qt.io/qt-6/qwizardpage.html#completeChanged
        self.completeChanged.emit()

    def isComplete(self) -> bool:
        return self.selected_key is not None

    def nextId(self):
        # Store the selected YubiKey information in the wizard
        self.wizard().setProperty("selectedYubiKey", self.selected_key)
        return super().nextId()

    def initializePage(self) -> None:
        super().initializePage()

        self.key_list_widget.itemSelectionChanged.connect(self.on_yubikey_item_change)
