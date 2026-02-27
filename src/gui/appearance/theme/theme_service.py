from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QStyleHints
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

    def initialize(self, theme: str, scheme: str, theme_mode: str) -> None:
        self._theme = theme
        self._scheme = scheme
        self._theme_mode = theme_mode

        if theme_mode == "system":
            self._start_system_theme_watcher()
        else:
            self._apply_theme()

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

    def getThemeList(self) -> list[str]:
        return list_themes()
