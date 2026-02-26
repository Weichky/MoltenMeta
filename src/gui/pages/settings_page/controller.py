from PySide6 import QtWidgets
from PySide6.QtCore import QObject

from application import AppContext

from .ui import UiSettingsPage

from domain.snapshot import SettingsSnapshot


class SettingsController(QObject):
    def __init__(self, ui: UiSettingsPage, context: AppContext):
        super().__init__()
        self.i18n_service = context.i18n
        self.ui = ui
        self._log_service = context.log
        self._settings_repo = context.core_db.settings_repo
        self._setupNavigation()

    def _setupNavigation(self):
        # Use exclusive button group to ensure only one button is checked
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.ui.general_button)
        self.button_group.addButton(self.ui.log_button)
        self.button_group.setExclusive(True)

        # Connect button clicks to page switching
        self.ui.general_button.clicked.connect(
            lambda: self.ui.content_area.setCurrentIndex(0)
        )
        self.ui.log_button.clicked.connect(
            lambda: self.ui.content_area.setCurrentIndex(1)
        )

    def connectSignals(self):
        self.ui.lang_combo.currentIndexChanged.connect(self._onLanguageChanged)
        self.ui.log_level_combo.currentIndexChanged.connect(self._onLogLevelChanged)

        # i18n
        # Connect to self.ui instead of self.
        self.i18n_service.language_changed.connect(self.ui.retranslateUi)

    def _onLanguageChanged(self, index: int):
        language = self.ui.lang_combo.itemData(index)
        self.i18n_service.setLanguage(language)
        self._settings_repo.upsert([SettingsSnapshot("locale", "language", language)])

    def _onLogLevelChanged(self, index: int):
        level = self.ui.log_level_combo.itemData(index)
        self._log_service.setLogLevel(level)
        self._settings_repo.upsert([SettingsSnapshot("log", "level", level)])
        self._log_service.getLogger(__name__).debug(f"Log level changed to {level}")
