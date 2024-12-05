from typing import Any, Optional
from PyQt6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QLabel,
    QHBoxLayout,
)
from PyQt6.QtGui import QFont

from app.page.yubipin_widget import YubiPinWidget

from .yubikeyitem import YubiKeyItemWidget


class SelectYubiKeyPage(QWizardPage):
    key_list_widget: QListWidget
    _pin_input_widget: QLineEdit

    def _prevent_backbutton_clicks(self):
        self.setCommitPage(True)

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

    def _build_yubipin_widget(self) -> QVBoxLayout:
        layout = QHBoxLayout()

        label = QLabel("YubiKey PIN")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)

        pin_input = QLineEdit()
        pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(pin_input)

        return layout

    def __init__(self, mypkcs, parent=None):
        super().__init__(parent)
        self.setTitle("Selecteer de te gebruiken yubikey")
        self._prevent_backbutton_clicks()

        self.pkcs = mypkcs
        yubikeys = self._get_yubikeys()
        yubikey_list_widget = self._build_yubikey_list_widget(yubikeys)

        layout = QVBoxLayout(self)
        layout.addWidget(yubikey_list_widget)

        # TODO add PIN-code input (password)
        # Add use default button?
        yubipin_widget = YubiPinWidget()
        layout.addWidget(yubipin_widget)

        # yubipin_widget.
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
        # The next button does not have to be enabled manually, just trigger the completion signal.
        # This will re-check the isCompleted function
        # https://doc.qt.io/qt-6/qwizardpage.html#completeChanged
        self.completeChanged.emit()

    def isComplete(self) -> bool:
        # TODO this should also include if the PIN has been filled in and succesful
        return self._find_selected_widget_item() is not None

    def nextId(self):
        widget = self._find_selected_widget_item()

        # This should and can not happen, since we're disabling the button
        if not widget:
            return super().nextId()

        # Store the selected YubiKey information in the wizard
        self.wizard().setProperty(
            "selectedYubiKey",
            widget.getYubiKeyDetails(),
        )
        return super().nextId()

    def initializePage(self) -> None:
        super().initializePage()

        self.key_list_widget.itemSelectionChanged.connect(self.on_yubikey_item_change)

    def cleanupPage(self) -> None:
        self.key_list_widget.clearSelection()
