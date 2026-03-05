from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor, QStyleHints, QIcon
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

from core.log import LogService
from qt_material import QtStyleTools, apply_stylesheet, list_themes
from resources.qt_material import default_extra
from .ads_theme import getAdsStylesheet


from pathlib import Path
import os


class InvertedIcon:
    """Marker class for icons that should be inverted in dark mode.
    
    This class manages icons that need color inversion when dark theme is active.
    It applies CSS filter to achieve the inversion effect dynamically.
    """
    def __init__(self, icon_path: str):
        self.icon_path = icon_path
    
    def apply_to_button(self, button: QPushButton, is_dark_mode: bool) -> None:
        """Apply icon with appropriate CSS filter based on color scheme.
        
        Args:
            button: The QPushButton widget to apply the icon to
            is_dark_mode: True if dark theme is active, False otherwise
        """
                
        # Store icon path for future updates
        button.setProperty("icon_path", self.icon_path)
        
        # Set the icon
        button.setIcon(QIcon(self.icon_path))
        
        # Apply CSS filter for dark mode inversion
        # Using filter property to invert icon colors
        if is_dark_mode:
            current_style = button.styleSheet()
            # Remove any existing icon-filter style first
            if "filter:" in current_style:
                lines = [line.strip() for line in current_style.split('\n') 
                        if not line.strip().startswith('filter:')]
                current_style = '\n'.join(lines)
            
            # Add invert filter for dark mode
            button.setStyleSheet(f"""
                {current_style}
                QPushButton {{
                    filter: invert(100%);
                }}
            """)
        else:
            # Remove filter for light mode
            current_style = button.styleSheet()
            if "filter:" in current_style:
                lines = [line.strip() for line in current_style.split('\n') 
                        if not line.strip().startswith('filter:')]
                if lines:
                    button.setStyleSheet('\n'.join(lines))
                else:
                    button.setStyleSheet("")


class ThemeService(QObject, QtStyleTools):
    theme_changed = Signal()

    def __init__(self, app, log_service: LogService):
        super().__init__(app)
        self._app = app
        self._logger = log_service.getLogger(__name__)
        self._theme = "blue"
        self._scheme = "light"
        self._theme_mode = "system"
        self._style_hints: QStyleHints | None = None
        self._inverted_icons: dict[str, InvertedIcon] = {}

    def _createPalette(self, scheme: str) -> QPalette:
        if scheme == "dark":
            return self._createDarkPalette()
        return self._createLightPalette()

    def _createLightPalette(self) -> QPalette:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        palette.setColor(QPalette.Base, QColor(250, 250, 250))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(50, 50, 50))
        palette.setColor(QPalette.Text, QColor(50, 50, 50))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        # palette.setColor(QPalette.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.PlaceholderText, QColor(150, 150, 150))
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
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(100, 180, 255))
        palette.setColor(QPalette.PlaceholderText, QColor(160, 160, 160))
        return palette

    def _applyNativePalette(self, scheme: str) -> None:
        palette = self._createPalette(scheme)
        self._app.setPalette(palette)

    def initialize(self, theme: str, scheme: str, theme_mode: str) -> None:
        self._theme = theme
        self._scheme = scheme
        self._theme_mode = theme_mode

        if theme_mode == "system":
            self._startSystemThemeWatcher()
        else:
            self._applyTheme()

    def _startSystemThemeWatcher(self) -> None:
        self._style_hints = self._app.styleHints()
        self._style_hints.colorSchemeChanged.connect(
            self._onSystemColorSchemeChanged
        )
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

        theme_xml = f"{scheme}_{self._theme}.xml"
        self.applyTheme(theme_xml, scheme)

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

    @property
    def theme_mode(self) -> str:
        return self._theme_mode

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def theme(self) -> str:
        return self._theme

    def applyTheme(
        self, theme_xml: str, scheme: str, extra: list | None = None
    ) -> None:
        self._logger.debug("Applying theme: %s", theme_xml)

        self._app.setStyleSheet(getAdsStylesheet())

        apply_stylesheet(
            self._app,
            theme=theme_xml,
            invert_secondary=(scheme == "light"),
            extra=extra if extra is not None else default_extra,
        )

        self.theme_changed.emit()

    def addStyleSheet(self, css: Path) -> None:
        self._logger.debug("Adding stylesheet: %s", css)

        stylesheet = self._app.styleSheet()
        with open(css, "r", encoding="utf-8") as f:
            self._app.setStyleSheet(stylesheet + f.read().format(**os.environ))

    def getThemeList(self) -> list[str]:
        return list_themes()

    def registerInvertedIcon(self, button, icon_path: str) -> InvertedIcon:
        """
        Register an icon that should be inverted in dark mode.
        
        This method registers a button's icon for automatic color inversion
        when dark theme is active. The inversion is achieved using CSS filters.
        
        Args:
            button: The QPushButton widget to apply the icon to
            icon_path: Path to the SVG icon file
            
        Returns:
            InvertedIcon instance for managing the icon
        """
        if icon_path not in self._inverted_icons:
            self._inverted_icons[icon_path] = InvertedIcon(icon_path)
        
        inverted_icon = self._inverted_icons[icon_path]
        is_dark = self._scheme == "dark" or (
            self._theme_mode == "system" and self._isSystemDark()
        )
        inverted_icon.apply_to_button(button, is_dark)
        
        return inverted_icon

    def _updateInvertedIcons(self, is_dark_mode: bool) -> None:
        """Update all registered inverted icons based on color scheme.
        
        Args:
            is_dark_mode: True if dark theme should be applied, False otherwise
        """
        for icon_obj in self._inverted_icons.values():
            # Find all buttons using this icon and update them
            for widget in self._app.topLevelWidgets():
                for button in widget.findChildren(QPushButton):
                    if button.property("icon_path") == icon_obj.icon_path:
                        icon_obj.apply_to_button(button, is_dark_mode)
