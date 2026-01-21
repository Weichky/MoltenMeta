from PySide6.QtCore import QObject, Signal

from qt_material import (
    QtStyleTools,
    apply_stylesheet,
    list_themes
)

from importlib.resources import files
from pathlib import Path
import os

from core.log import getLogService

_theme_service: _ThemeService | None = None

class _ThemeService(QObject, QtStyleTools):
    theme_changed = Signal()

    def __init__(self, app: 'QApplication'):
        super().__init__(app)
        self._app = app
        self._logger = getLogService().getLogger("theme service")


    def applyTheme(
            self,
            theme_xml: str | None = None,
            scheme: str | None = None,
            extra: list | None = None
        ) -> None:
        self._logger.info(
            "Applying theme: %s", theme_xml
        )

        apply_stylesheet(
            self._app,
            theme = theme_xml,
            invert_secondary = (scheme == "light"),
            extra=extra
        )

        self.theme_changed.emit()

    def addStyleSheet(self, css: Path) -> None:
        self._logger.debug("Adding stylesheet: %s", css)

        stylesheet = self._app.styleSheet()
        with open(css, "r", encoding="utf-8") as f:
            self._app.setStyleSheet(
                stylesheet + f.read().format(**os.environ)
            )
    def getThemeList(self) -> list[str]:
        return list_themes()
def getThemeService() -> _ThemeService:
    if _theme_service:
        return _theme_service
    raise RuntimeError("Theme service not created")

def createThemeService(app: 'QApplication') -> _ThemeService:
    global _theme_service

    if _theme_service:
        raise RuntimeError("Theme service already created")

    _theme_service = _ThemeService(app)
    return _theme_service
