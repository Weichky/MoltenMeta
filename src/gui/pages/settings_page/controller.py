from PySide6 import QtWidgets
from PySide6.QtCore import QObject

from .ui import UiSettingsPage

from i18n import getI18nService

class SettingsController(QObject):
    def __init__(self, ui: UiSettingsPage):
        super().__init__()
        self.ui = ui
        self._setupNavigation()

    def _setupNavigation(self):
        # Use exclusive button group to ensure only one button is checked
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.ui.general_button)
        self.button_group.addButton(self.ui.log_button)
        self.button_group.setExclusive(True)
        
        # Connect button clicks to page switching
        self.ui.general_button.clicked.connect(lambda: self.ui.content_area.setCurrentIndex(0))
        self.ui.log_button.clicked.connect(lambda: self.ui.content_area.setCurrentIndex(1))

    def connectSignals(self):
        self.ui.lang_combo.currentIndexChanged.connect(self._onLanguageChanged)

        # i18n
        # Connect to self.ui instead of self.
        getI18nService().languageChanged.connect(self.ui.retranslateUi)

    def _onLanguageChanged(self, index: int):
        language = self.ui.lang_combo.itemData(index)
        getI18nService().setLanguage(language)