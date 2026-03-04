from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor, QStyleHints
from PySide6.QtCore import Qt

from core.log import LogService
from qt_material import QtStyleTools, apply_stylesheet, list_themes
from resources.qt_material import default_extra

from pathlib import Path
import os


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

    def _create_palette(self, scheme: str) -> QPalette:
        if scheme == "dark":
            return self._create_dark_palette()
        return self._create_light_palette()

    def _create_light_palette(self) -> QPalette:
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
        palette.setColor(QPalette.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.PlaceholderText, QColor(150, 150, 150))
        return palette

    def _create_dark_palette(self) -> QPalette:
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

    def _apply_native_palette(self, scheme: str) -> None:
        palette = self._create_palette(scheme)
        self._app.setPalette(palette)

    def initialize(self, theme: str, scheme: str, theme_mode: str) -> None:
        self._theme = theme
        self._scheme = scheme
        self._theme_mode = theme_mode

        if theme_mode == "system":
            self._start_system_theme_watcher()
        else:
            self._apply_theme()
        
        # Apply ADS (Qt Advanced Docking System) custom stylesheet
        self._applyADSStylesheet(scheme)

    def _applyADSStylesheet(self, scheme: str) -> None:
        """
        Apply custom ADS stylesheet based on current theme scheme.
        
        This method applies a custom QSS stylesheet to the Qt Advanced Docking System
        components to ensure consistent styling with the application theme.
        
        Args:
            scheme: Color scheme ('light' or 'dark')
        """
        # Define ADS custom stylesheet
        # Uses palette colors for automatic theme adaptation
        ads_stylesheet = """
ads--CDockWidgetTab QLabel {
    color: palette(Text) !important;
}
ads--CDockWidgetTab[activeTab="true"] QLabel,
ads--CDockWidgetTab[focused="true"] QLabel {
    color: palette(HighlightedText) !important;
}
ads--CDockWidgetTab #dockWidgetTabLabel {
    color: palette(Text) !important;
}
ads--CDockWidgetTab[activeTab="true"] #dockWidgetTabLabel,
ads--CDockWidgetTab[focused="true"] #dockWidgetTabLabel {
    color: palette(HighlightedText) !important;
}
"""
        
        self.setADSStylesheet(ads_stylesheet)

    def _start_system_theme_watcher(self) -> None:
        self._style_hints = self._app.styleHints()
        self._style_hints.colorSchemeChanged.connect(
            self._on_system_color_scheme_changed
        )
        self._apply_theme()

    def _on_system_color_scheme_changed(self) -> None:
        if self._theme_mode == "system":
            self._apply_theme()

    def _is_system_dark(self) -> bool:
        if self._style_hints is None:
            return False
        return self._style_hints.colorScheme() == Qt.ColorScheme.Dark

    def _apply_theme(self) -> None:
        if self._theme_mode == "system":
            scheme = "dark" if self._is_system_dark() else "light"
        else:
            scheme = self._scheme

        self._apply_native_palette(scheme)

        theme_xml = f"{scheme}_{self._theme}.xml"
        self.applyTheme(theme_xml, scheme)

    def setThemeMode(self, mode: str) -> None:
        old_mode = self._theme_mode
        self._theme_mode = mode

        if mode == "system":
            if self._style_hints is None:
                self._start_system_theme_watcher()
            else:
                self._apply_theme()
        else:
            self._scheme = mode
            if old_mode == "system" and self._style_hints:
                self._style_hints.colorSchemeChanged.disconnect(
                    self._on_system_color_scheme_changed
                )
                self._style_hints = None
            self._apply_theme()

        self.theme_changed.emit()

    def setScheme(self, scheme: str) -> None:
        self._scheme = scheme
        if self._theme_mode != "system":
            self._apply_theme()
            self.theme_changed.emit()

    def setTheme(self, theme: str) -> None:
        self._theme = theme
        self._apply_theme()
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

    def setADSStylesheet(self, css: str) -> None:
        """
        Set custom stylesheet for Qt Advanced Docking System components.
        
        This method allows you to override or extend the default ADS styles.
        The stylesheet will be applied to the CDockManager and affects all
        dock widgets managed by it.
        
        Args:
            css: QSS stylesheet string for ADS components
        
        Example:
            >>> ads_css = '''
            ... ads--CDockWidgetTab QLabel {
            ...     color: palette(Text) !important;
            ... }
            ... '''
            >>> theme_service.setADSStylesheet(ads_css)
        """
        self._logger.debug("Setting ADS stylesheet")
        
        # Apply ADS stylesheet through the dock manager
        # This requires importing PySide6QtAds where this is called
        try:
            import PySide6QtAds as QtAds
            
            # Get current ADS stylesheet and append custom styles
            current_stylesheet = QtAds.CDockManager.stylesheet()
            new_stylesheet = current_stylesheet + "\n" + css if current_stylesheet else css
            
            QtAds.CDockManager.setStyleSheet(new_stylesheet)
            
            self._logger.debug("ADS stylesheet applied successfully")
        except ImportError:
            self._logger.warning("PySide6QtAds not available, skipping ADS stylesheet")
        except Exception as e:
            self._logger.error("Failed to apply ADS stylesheet: %s", e)

    def getThemeList(self) -> list[str]:
        return list_themes()
