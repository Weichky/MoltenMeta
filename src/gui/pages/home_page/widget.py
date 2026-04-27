from PySide6 import QtWidgets
from PySide6.QtCore import Signal

from i18n import I18nService
from gui.appearance.theme import ThemeService

from .ui import UiHomePage


class HomePage(QtWidgets.QWidget):
    projectButtonClicked = Signal()
    databaseButtonClicked = Signal()
    simulationButtonClicked = Signal()
    settingsButtonClicked = Signal()

    def __init__(self, i18n_service: I18nService, theme_service: ThemeService):
        super().__init__(parent=None)
        self.i18n_service = i18n_service
        self._theme_service = theme_service

        self.ui = UiHomePage()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        self._connect_signals()
        theme_service.theme_changed.connect(self._onThemeChanged)
        self._apply_theme_colors()
        self._apply_title_color()

    def _connect_signals(self):
        # Tile order: [Project, Data, Simulation, Settings] — must match ui.py layout.
        PROJECT_INDEX = 0
        DATABASE_INDEX = 1
        SIMULATION_INDEX = 2
        SETTINGS_INDEX = 3

        self.ui.tiles[PROJECT_INDEX].clicked.connect(self.projectButtonClicked.emit)
        self.ui.tiles[DATABASE_INDEX].clicked.connect(self.databaseButtonClicked.emit)
        self.ui.tiles[SIMULATION_INDEX].clicked.connect(
            self.simulationButtonClicked.emit
        )
        self.ui.tiles[SETTINGS_INDEX].clicked.connect(self.settingsButtonClicked.emit)

        self.i18n_service.language_changed.connect(self.retranslateUi)

    def _onThemeChanged(self):
        self._apply_theme_colors()
        self._apply_title_color()

    def _apply_theme_colors(self):
        primary = self._theme_service.primary_color
        self.ui.accent_line.setStyleSheet(f"background-color: {primary}; border: none;")

    def _apply_title_color(self):
        primary = self._theme_service.primary_color
        self.ui.setupTitleLabel(primary)

    def resizeEvent(self, event):
        # Reserved for responsive layout. Currently a no-op.
        super().resizeEvent(event)

    def retranslateUi(self):
        self.ui.retranslateUi()
