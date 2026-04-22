from pathlib import Path

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QPalette, QColor, QStyleHints, QIcon
from PySide6.QtWidgets import QPushButton

from core.log import LogService
from .ads_theme import getAdsStylesheet
from .swiss_style import SwissStyle


def _convertDensityToScale(density: int) -> float:
    mapping = {-4: 0.5, -3: 0.75, -2: 1.0, -1: 1.25, 0: 1.5}
    return mapping.get(density, 1.0)


def _getDensityScaleOption(density: int) -> str:
    mapping = {
        -4: "50%",
        -3: "75%",
        -2: "100%",
        -1: "125%",
        0: "150%",
    }
    return mapping.get(density, "100%")


class InvertedIcon:
    """Marker class for icons that should be inverted in dark mode."""

    def __init__(self, icon_path: str):
        self.icon_path = icon_path

    def apply_to_button(self, button: QPushButton, is_dark_mode: bool) -> None:
        """Apply icon with appropriate CSS filter based on color scheme."""
        button.setProperty("icon_path", self.icon_path)
        button.setIcon(QIcon(self.icon_path))

        if is_dark_mode:
            current_style = button.styleSheet()
            if "filter:" in current_style:
                lines = [
                    line.strip()
                    for line in current_style.split("\n")
                    if not line.strip().startswith("filter:")
                ]
                current_style = "\n".join(lines)

            button.setStyleSheet(
                f"""
                {current_style}
                QPushButton {{
                    filter: invert(100%);
                }}
            """
            )
        else:
            current_style = button.styleSheet()
            if "filter:" in current_style:
                lines = [
                    line.strip()
                    for line in current_style.split("\n")
                    if not line.strip().startswith("filter:")
                ]
                if lines:
                    button.setStyleSheet("\n".join(lines))
                else:
                    button.setStyleSheet("")


class ThemeService(QObject):
    theme_changed = Signal()

    def __init__(self, app, log_service: LogService):
        super().__init__(app)
        self._app = app
        self._logger = log_service.getLogger(__name__)
        self._theme = "blue"
        self._scheme = "light"
        self._theme_mode = "system"
        self._density_scale = -3
        self._style_hints: QStyleHints | None = None
        self._inverted_icons: dict[str, InvertedIcon] = {}
        self._primary_color = "#C62828"
        self._secondary_color = "#1A1A1A"

    def _createLightPalette(self) -> QPalette:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(26, 26, 26))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(250, 250, 250))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(26, 26, 26))
        palette.setColor(QPalette.Text, QColor(26, 26, 26))
        palette.setColor(QPalette.Button, QColor(245, 245, 245))
        palette.setColor(QPalette.ButtonText, QColor(26, 26, 26))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(198, 40, 40))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.PlaceholderText, QColor(158, 158, 158))
        return palette

    def _createDarkPalette(self) -> QPalette:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
        palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(55, 55, 55))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(198, 40, 40))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(100, 180, 255))
        palette.setColor(QPalette.PlaceholderText, QColor(160, 160, 160))
        return palette

    def _createPalette(self, scheme: str) -> QPalette:
        if scheme == "dark":
            return self._createDarkPalette()
        return self._createLightPalette()

    def _applyNativePalette(self, scheme: str) -> None:
        palette = self._createPalette(scheme)
        self._app.setPalette(palette)

    def updateThemeColors(self, primary: str, secondary: str) -> None:
        self._primary_color = primary
        self._secondary_color = secondary
        self._applyTheme()

    def initialize(
        self, theme: str, scheme: str, theme_mode: str, density_scale: int = -3
    ) -> None:
        self._theme = theme
        self._scheme = scheme
        self._theme_mode = theme_mode
        self._density_scale = density_scale
        self._density_scale_option = _getDensityScaleOption(density_scale)

        if theme_mode == "system":
            self._startSystemThemeWatcher()
        else:
            self._applyTheme()

    def _startSystemThemeWatcher(self) -> None:
        self._style_hints = self._app.styleHints()
        self._style_hints.colorSchemeChanged.connect(self._onSystemColorSchemeChanged)
        self._applyTheme()

    def _onSystemColorSchemeChanged(self) -> None:
        if self._theme_mode == "system":
            self._applyTheme()

    def _isSystemDark(self) -> bool:
        if self._style_hints is None:
            return False
        return self._style_hints.colorScheme() == Qt.ColorScheme.Dark

    def _applyTheme(self) -> None:
        if self._theme_mode == "system":
            scheme = "dark" if self._isSystemDark() else "light"
        else:
            scheme = self._scheme

        self._applyNativePalette(scheme)
        self._updateInvertedIcons(scheme == "dark")

        ads_style = getAdsStylesheet(self._primary_color, self._secondary_color)
        swiss_style = SwissStyle.getStylesheet(
            self._density_scale_option,
            self._primary_color,
            self._secondary_color,
        )
        self._app.setStyleSheet(ads_style + "\n" + swiss_style)

        self.theme_changed.emit()

    def setThemeMode(self, mode: str) -> None:
        old_mode = self._theme_mode
        self._theme_mode = mode

        if mode == "system":
            if self._style_hints is None:
                self._startSystemThemeWatcher()
            else:
                self._applyTheme()
        else:
            self._scheme = mode
            if old_mode == "system" and self._style_hints:
                self._style_hints.colorSchemeChanged.disconnect(
                    self._onSystemColorSchemeChanged
                )
                self._style_hints = None
            self._applyTheme()

        self.theme_changed.emit()

    def setScheme(self, scheme: str) -> None:
        self._scheme = scheme
        if self._theme_mode != "system":
            self._applyTheme()
            self.theme_changed.emit()

    def setTheme(self, theme: str) -> None:
        self._theme = theme
        self._applyTheme()
        self.theme_changed.emit()

    def updateDensityScale(self, scale: int) -> None:
        self._density_scale = scale
        self._density_scale_option = _getDensityScaleOption(scale)
        self._applyTheme()

    @property
    def density_scale(self) -> int:
        return self._density_scale

    @property
    def density_scale_option(self) -> str:
        return self._density_scale_option

    @property
    def theme_mode(self) -> str:
        return self._theme_mode

    @property
    def scheme(self) -> str:
        if self._theme_mode == "system":
            return "dark" if self._isSystemDark() else "light"
        return self._scheme

    @property
    def theme(self) -> str:
        return self._theme

    def addStyleSheet(self, css: Path) -> None:
        self._logger.debug("Adding stylesheet: %s", css)

        stylesheet = self._app.styleSheet()
        with open(css, "r", encoding="utf-8") as f:
            self._app.setStyleSheet(stylesheet + f.read())

    def getThemeList(self) -> list[str]:
        return ["blue"]

    def registerInvertedIcon(self, button, icon_path: str) -> InvertedIcon:
        """Register an icon that should be inverted in dark mode."""
        if icon_path not in self._inverted_icons:
            self._inverted_icons[icon_path] = InvertedIcon(icon_path)

        inverted_icon = self._inverted_icons[icon_path]
        is_dark = self._scheme == "dark" or (
            self._theme_mode == "system" and self._isSystemDark()
        )
        inverted_icon.apply_to_button(button, is_dark)

        return inverted_icon

    def _updateInvertedIcons(self, is_dark_mode: bool) -> None:
        """Update all registered inverted icons based on color scheme."""
        for icon_obj in self._inverted_icons.values():
            for widget in self._app.topLevelWidgets():
                for button in widget.findChildren(QPushButton):
                    if button.property("icon_path") == icon_obj.icon_path:
                        icon_obj.apply_to_button(button, is_dark_mode)
