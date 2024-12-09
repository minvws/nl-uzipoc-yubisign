from typing import Any, Optional
from PyQt6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import pyqtSignal

from app.page.yubipin_widget import YubiPinWidget
from app.yubikey_details import YubikeyDetails

from .yubikeyitem import YubiKeyItemWidget
from app.pkcs import pkcs as InternalPKCSWrapper


class SelectYubiKeyPage(QWizardPage):
    _TITLE = "Selectie en authenticatie Yubikey"
    _SUBTITLE = """
    Selecteer de desbetreffende Yubikey en vul vervolgens hiervan de PIN-code in. De standaard PIN-code is alvast ingevuld.
    """

    pkcs: InternalPKCSWrapper
    key_list_widget: QListWidget
    _pin_input_widget: YubiPinWidget

    # This will be called when the user has succesfully authenticated
    _pin_authenticated_signal = pyqtSignal(bool)
    _pin_authenticated: bool

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

    def _setup_ui(self, pkcslib: InternalPKCSWrapper):
        self.setTitle(self._TITLE)
        self.setSubTitle(self._SUBTITLE.strip())

        self._prevent_backbutton_clicks()

        yubikeys = self._get_yubikeys()
        yubikey_list_widget = self._build_yubikey_list_widget(yubikeys)

        layout = QVBoxLayout(self)
        layout.addWidget(yubikey_list_widget)

        yubipin_widget = YubiPinWidget(pkcslib.pkcs11, self._pin_authenticated_signal)
        layout.addWidget(yubipin_widget)

        self.key_list_widget = yubikey_list_widget
        self._pin_input_widget = yubipin_widget

    def __init__(self, mypkcs: InternalPKCSWrapper, parent=None):
        super().__init__(parent)
        self.pkcs = mypkcs
        self._pin_authenticated = False

        self._setup_ui(mypkcs)

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

    def _find_selected_yubikey_details_from_widget(self):
        selected_yubikey_widget_item: Optional[YubiKeyItemWidget] = self._find_selected_widget_item()

        if selected_yubikey_widget_item is None:
            return None

        slot, name, serial = selected_yubikey_widget_item.getYubiKeyDetails()
        return YubikeyDetails(
            slot,
            name,
            serial,
        )

    def on_yubikey_item_change(self):
        selected_yubikey: Optional[YubikeyDetails] = self._find_selected_yubikey_details_from_widget()

        if not selected_yubikey:
            self._pin_authenticated = False

        # Pass none if nothing is selected
        self._pin_input_widget.toggle_input_field_ability(details=selected_yubikey)

        # The next button does not have to be enabled manually, just trigger the completion signal.
        # This will re-check the isCompleted function
        # https://doc.qt.io/qt-6/qwizardpage.html#completeChanged
        self.completeChanged.emit()

    def has_selection(self) -> bool:
        return self._find_selected_widget_item() is not None

    def isComplete(self) -> bool:
        return self.has_selection() and self._pin_authenticated

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
        # Should we set the PIN here?
        return super().nextId()

    def _on_yubikey_authentication(self, authenticated: bool):
        self._pin_authenticated = authenticated
        self.completeChanged.emit()

    def initializePage(self) -> None:
        super().initializePage()

        self.key_list_widget.itemSelectionChanged.connect(self.on_yubikey_item_change)
        self._pin_authenticated_signal.connect(self._on_yubikey_authentication)

    def cleanupPage(self) -> None:
        self._pin_authenticated = False
        self._pin_input_widget.cleanup()
        self.key_list_widget.clearSelection()
