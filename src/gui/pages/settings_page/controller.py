import logging

from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QTextCursor

from application import AppContext

from .ui import UiSettingsPage

from domain.snapshot import SettingsSnapshot
from domain.settings import Settings

from core.plot.config import PlotStyleService
from core.plot.color import ColorPalette
from catalog import ColorAlgorithm

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
        self._context = context
        self._log_service = context.log
        self._settings_repo = context.core_db.settings_repo
        self._theme_service = theme_service
        self._plot_style_service = PlotStyleService()
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
            lambda: (self.ui.content_area.setCurrentIndex(2), self._updatePlotPreview())
        )

    def connectSignals(self):
        self.ui.lang_combo.currentIndexChanged.connect(self._onLanguageChanged)
        self.ui.log_level_combo.currentIndexChanged.connect(self._onLogLevelChanged)
        self.ui.theme_mode_combo.currentIndexChanged.connect(self._onThemeModeChanged)
        self.ui.theme_color_combo.currentIndexChanged.connect(self._onThemeColorChanged)
        self.ui.density_scale_spin.valueChanged.connect(self._onDensityScaleChanged)

        self.ui.palette_combo.currentIndexChanged.connect(self._onColorschemeChanged)
        self.ui.algorithm_combo.currentIndexChanged.connect(
            self._onColorAlgorithmChanged
        )
        self.ui.color_scheme_combo.currentIndexChanged.connect(
            self._onColorSchemeChanged
        )
        self.ui.line_style_combo.currentIndexChanged.connect(self._onLineStyleChanged)
        self.ui.marker_combo.currentIndexChanged.connect(self._onMarkerChanged)
        self.ui.line_width_spin.valueChanged.connect(self._onLineWidthChanged)
        self.ui.marker_size_spin.valueChanged.connect(self._onMarkerSizeChanged)
        self.ui.grid_check.toggled.connect(self._onGridChanged)
        self.ui.grid_mode_combo.currentIndexChanged.connect(self._onGridModeChanged)
        self.ui.grid_density_spin.valueChanged.connect(self._onGridDensityChanged)
        self.ui.grid_label_density_spin.valueChanged.connect(
            self._onGridLabelDensityChanged
        )
        self.ui.title_font_size_spin.valueChanged.connect(self._onTitleFontSizeChanged)
        self.ui.label_font_size_spin.valueChanged.connect(self._onLabelFontSizeChanged)
        self.ui.tick_font_size_spin.valueChanged.connect(self._onTickFontSizeChanged)
        self.ui.legend_font_size_spin.valueChanged.connect(
            self._onLegendFontSizeChanged
        )

        # i18n
        # Connect to self.ui instead of self.
        self.i18n_service.language_changed.connect(self.ui.retranslateUi)

    def _saveAndReload(self, snapshots: list[SettingsSnapshot]) -> None:
        self._settings_repo.upsert(snapshots)
        self._context.core_db.reloadSettings()

    def _onLanguageChanged(self, index: int):
        language = self.ui.lang_combo.itemData(index)
        self.i18n_service.setLanguage(language)
        self._saveAndReload([SettingsSnapshot("locale", "language", language)])

    def _onLogLevelChanged(self, index: int):
        level = self.ui.log_level_combo.itemData(index)
        self._log_service.setLogLevel(level)
        self._saveAndReload([SettingsSnapshot("log", "level", level)])
        self._log_service.getLogger(__name__).debug(f"Log level changed to {level}")

    def _onThemeModeChanged(self, index: int):
        mode = self.ui.theme_mode_combo.itemData(index)
        self._theme_service.setThemeMode(mode)
        snapshots = [SettingsSnapshot("appearance", "theme_mode", mode)]
        if mode != "system":
            snapshots.append(SettingsSnapshot("appearance", "scheme", mode))
        self._saveAndReload(snapshots)

    def _onThemeColorChanged(self, index: int):
        color = self.ui.theme_color_combo.itemData(index)
        self._theme_service.setTheme(color)
        self._saveAndReload([SettingsSnapshot("appearance", "theme", color)])

    def _onDensityScaleChanged(self, value: int):
        self._theme_service.updateDensityScale(value)
        self._saveAndReload(
            [SettingsSnapshot("appearance", "density_scale", str(value))]
        )

    def _updatePlotPreview(self) -> None:
        settings = Settings(records=self._settings_repo.findAll())
        colorscheme = self.ui.palette_combo.currentData()
        algorithm = self.ui.algorithm_combo.currentData()
        line_style = self.ui.line_style_combo.currentData()
        marker = self.ui.marker_combo.currentData()
        line_width = self.ui.line_width_spin.value()
        grid = self.ui.grid_check.isChecked()
        grid_mode = self.ui.grid_mode_combo.currentData()
        grid_density = self.ui.grid_density_spin.value()
        grid_label_density = self.ui.grid_label_density_spin.value()
        title_font_size = self.ui.title_font_size_spin.value()
        label_font_size = self.ui.label_font_size_spin.value()
        tick_font_size = self.ui.tick_font_size_spin.value()
        legend_font_size = self.ui.legend_font_size_spin.value()

        if colorscheme == "custom":
            primary = settings.get("plot", "custom_primary") or "#1f77b4"
            secondary = settings.get("plot", "custom_secondary") or "#ff7f0e"
            from core.plot.color import ThemeColors

            theme = ThemeColors(primary=primary, secondary=secondary)
        else:
            theme = ColorPalette.getThemeColors(colorscheme)

        algo = ColorAlgorithm(algorithm) if algorithm else ColorAlgorithm.LINEAR
        from core.plot.color import ColorGenerator

        gen = ColorGenerator(theme, algo)
        colors = gen.getColorN(5)

        self.ui.updatePreview(
            colors,
            line_style,
            marker,
            line_width,
            grid,
            grid_mode,
            grid_density,
            grid_label_density,
            title_font_size,
            label_font_size,
            tick_font_size,
            legend_font_size,
        )

    def _onColorschemeChanged(self, index: int):
        scheme = self.ui.palette_combo.itemData(index)
        self._saveAndReload([SettingsSnapshot("plot", "colorscheme", scheme)])
        if scheme == "custom":
            self._showCustomColorDialog()
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _showCustomColorDialog(self) -> None:
        current_primary = self._settings_repo.findBySectionAndKey(
            "plot", "custom_primary"
        )
        current_secondary = self._settings_repo.findBySectionAndKey(
            "plot", "custom_secondary"
        )

        current_text = ""
        if current_primary:
            current_text = current_primary.value
        if current_secondary:
            current_text += ", " + current_secondary.value

        dialog = QtWidgets.QInputDialog(self.ui.plot_page)
        dialog.setWindowTitle(self.tr("Custom Colors"))
        dialog.setLabelText(
            self.tr("Enter primary and secondary colors (e.g., #3f50b5, #f44336)")
        )
        if current_text:
            dialog.setTextValue(current_text)

        if dialog.exec():
            text = dialog.textValue()
            if text:
                colors = self._parseColors(text)
                if colors:
                    self._saveCustomColors(colors)
                    self._updatePlotPreview()

    def _parseColors(self, text: str) -> list[str]:
        import re

        color_pattern = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
        colors = []
        for part in text.replace(",", " ").split():
            part = part.strip()
            if color_pattern.match(part):
                if len(part) == 4:
                    part = f"#{part[1]}{part[1]}{part[2]}{part[2]}{part[3]}{part[3]}"
                colors.append(part.upper())
        return colors[:2]

    def _saveCustomColors(self, colors: list[str]) -> None:
        snapshots = []
        snapshots.append(SettingsSnapshot("plot", "custom_primary", colors[0]))
        if len(colors) > 1:
            snapshots.append(SettingsSnapshot("plot", "custom_secondary", colors[1]))
        self._saveAndReload(snapshots)

    def _onColorAlgorithmChanged(self, index: int):
        algorithm = self.ui.algorithm_combo.itemData(index)
        self._saveAndReload([SettingsSnapshot("plot", "color_algorithm", algorithm)])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onColorSchemeChanged(self, index: int):
        scheme = self.ui.color_scheme_combo.itemData(index)
        self._saveAndReload([SettingsSnapshot("plot", "colorScheme", scheme)])
        self.plot_settings_changed.emit()

    def _onLineStyleChanged(self, index: int):
        style = self.ui.line_style_combo.itemData(index)
        self._saveAndReload([SettingsSnapshot("plot", "lineStyle", style)])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onMarkerChanged(self, index: int):
        marker = self.ui.marker_combo.itemData(index)
        self._saveAndReload([SettingsSnapshot("plot", "marker", marker)])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onLineWidthChanged(self, value: float):
        self._saveAndReload([SettingsSnapshot("plot", "lineWidth", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onMarkerSizeChanged(self, value: float):
        self._saveAndReload([SettingsSnapshot("plot", "markerSize", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onGridChanged(self, checked: bool):
        self._saveAndReload(
            [SettingsSnapshot("plot", "grid", "true" if checked else "false")]
        )
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onGridModeChanged(self, index: int):
        mode = self.ui.grid_mode_combo.itemData(index)
        self._saveAndReload([SettingsSnapshot("plot", "gridMode", mode)])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onGridDensityChanged(self, value: float):
        self._saveAndReload([SettingsSnapshot("plot", "gridDensity", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onGridLabelDensityChanged(self, value: float):
        self._saveAndReload([SettingsSnapshot("plot", "gridLabelDensity", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onTitleFontSizeChanged(self, value: int):
        self._saveAndReload([SettingsSnapshot("plot", "titleFontSize", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onLabelFontSizeChanged(self, value: int):
        self._saveAndReload([SettingsSnapshot("plot", "labelFontSize", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onTickFontSizeChanged(self, value: int):
        self._saveAndReload([SettingsSnapshot("plot", "tickFontSize", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()

    def _onLegendFontSizeChanged(self, value: int):
        self._saveAndReload([SettingsSnapshot("plot", "legendFontSize", str(value))])
        self._updatePlotPreview()
        self.plot_settings_changed.emit()
