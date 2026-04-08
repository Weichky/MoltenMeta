import logging

from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QTextCursor

from application import AppContext

from .ui import UiSettingsPage

from domain.snapshot import SettingsSnapshot

from gui.appearance.theme import ThemeService


class QtLogHandler(logging.Handler):
    class SignalEmitter(QObject):
        log_message = Signal(str, int)

        def __init__(self):
            super().__init__()
            self.log_message.connect(self._appendLog)

        def _appendLog(self, message: str, level: int):
            self._text_edit.append(message)
            self._text_edit.moveCursor(QTextCursor.MoveOperation.End)

        def setTextEdit(self, text_edit: QtWidgets.QTextEdit):
            self._text_edit = text_edit

    def __init__(self):
        super().__init__()
        self._emitter = self.SignalEmitter()
        self.setFormatter(
            logging.Formatter("[%(levelname)s](%(name)s)|%(asctime)s|%(message)s")
        )

    def setTextEdit(self, text_edit: QtWidgets.QTextEdit):
        self._emitter.setTextEdit(text_edit)

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self._emitter.log_message.emit(msg, record.levelno)
        except Exception:
            self.handleError(record)


class SettingsController(QObject):
    plot_settings_changed = Signal()

    def __init__(
        self, ui: UiSettingsPage, context: AppContext, theme_service: ThemeService
    ):
        super().__init__()
        self.i18n_service = context.i18n
        self.ui = ui
        self._log_service = context.log
        self._settings_repo = context.core_db.settings_repo
        self._theme_service = theme_service
        self._setupNavigation()
        self._setupLogHandler()

    def _setupLogHandler(self):
        self._log_handler = QtLogHandler()
        self._log_handler.setTextEdit(self.ui.log_display)
        logging.getLogger().addHandler(self._log_handler)

    def _setupNavigation(self):
        # Use exclusive button group to ensure only one button is checked
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.ui.general_button)
        self.button_group.addButton(self.ui.log_button)
        self.button_group.addButton(self.ui.plot_button)
        self.button_group.setExclusive(True)

        # Connect button clicks to page switching
        self.ui.general_button.clicked.connect(
            lambda: self.ui.content_area.setCurrentIndex(0)
        )
        self.ui.log_button.clicked.connect(
            lambda: self.ui.content_area.setCurrentIndex(1)
        )
        self.ui.plot_button.clicked.connect(
            lambda: self.ui.content_area.setCurrentIndex(2)
        )

    def connectSignals(self):
        self.ui.lang_combo.currentIndexChanged.connect(self._onLanguageChanged)
        self.ui.log_level_combo.currentIndexChanged.connect(self._onLogLevelChanged)
        self.ui.theme_mode_combo.currentIndexChanged.connect(self._onThemeModeChanged)
        self.ui.theme_color_combo.currentIndexChanged.connect(self._onThemeColorChanged)
        self.ui.density_scale_spin.valueChanged.connect(self._onDensityScaleChanged)

        self.ui.palette_combo.currentIndexChanged.connect(self._onColorschemeChanged)
        self.ui.color_scheme_combo.currentIndexChanged.connect(
            self._onColorSchemeChanged
        )
        self.ui.line_style_combo.currentIndexChanged.connect(self._onLineStyleChanged)
        self.ui.marker_combo.currentIndexChanged.connect(self._onMarkerChanged)
        self.ui.line_width_spin.valueChanged.connect(self._onLineWidthChanged)
        self.ui.marker_size_spin.valueChanged.connect(self._onMarkerSizeChanged)
        self.ui.grid_check.toggled.connect(self._onGridChanged)
        self.ui.font_size_spin.valueChanged.connect(self._onFontSizeChanged)

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

    def _onThemeModeChanged(self, index: int):
        mode = self.ui.theme_mode_combo.itemData(index)
        self._theme_service.setThemeMode(mode)
        snapshots = [SettingsSnapshot("appearance", "theme_mode", mode)]
        if mode != "system":
            snapshots.append(SettingsSnapshot("appearance", "scheme", mode))
        self._settings_repo.upsert(snapshots)

    def _onThemeColorChanged(self, index: int):
        color = self.ui.theme_color_combo.itemData(index)
        self._theme_service.setTheme(color)
        self._settings_repo.upsert([SettingsSnapshot("appearance", "theme", color)])

    def _onDensityScaleChanged(self, value: int):
        self._theme_service.updateDensityScale(value)
        self._settings_repo.upsert(
            [SettingsSnapshot("appearance", "density_scale", str(value))]
        )

    def _onColorschemeChanged(self, index: int):
        scheme = self.ui.palette_combo.itemData(index)
        self._settings_repo.upsert([SettingsSnapshot("plot", "colorscheme", scheme)])
        self.plot_settings_changed.emit()

    def _onColorSchemeChanged(self, index: int):
        scheme = self.ui.color_scheme_combo.itemData(index)
        self._settings_repo.upsert([SettingsSnapshot("plot", "colorScheme", scheme)])
        self.plot_settings_changed.emit()

    def _onLineStyleChanged(self, index: int):
        style = self.ui.line_style_combo.itemData(index)
        self._settings_repo.upsert([SettingsSnapshot("plot", "lineStyle", style)])
        self.plot_settings_changed.emit()

    def _onMarkerChanged(self, index: int):
        marker = self.ui.marker_combo.itemData(index)
        self._settings_repo.upsert([SettingsSnapshot("plot", "marker", marker)])
        self.plot_settings_changed.emit()

    def _onLineWidthChanged(self, value: float):
        self._settings_repo.upsert([SettingsSnapshot("plot", "lineWidth", str(value))])
        self.plot_settings_changed.emit()

    def _onMarkerSizeChanged(self, value: float):
        self._settings_repo.upsert([SettingsSnapshot("plot", "markerSize", str(value))])
        self.plot_settings_changed.emit()

    def _onGridChanged(self, checked: bool):
        self._settings_repo.upsert(
            [SettingsSnapshot("plot", "grid", "true" if checked else "false")]
        )
        self.plot_settings_changed.emit()

    def _onFontSizeChanged(self, value: int):
        self._settings_repo.upsert([SettingsSnapshot("plot", "fontSize", str(value))])
        self.plot_settings_changed.emit()

    def _onFontSizeChanged(self, value: int):
        self._settings_repo.upsert([SettingsSnapshot("plot", "fontSize", str(value))])
