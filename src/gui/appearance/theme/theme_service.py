from PySide6.QtCore import QObject, Signal

from core.log import LogService

from qt_material import (
    QtStyleTools,
    apply_stylesheet,
    list_themes
)

from importlib.resources import files
from pathlib import Path
import os

from core.log import LogService

class ThemeService(QObject, QtStyleTools):
    theme_changed = Signal()

    def __init__(self, app, log_service: LogService):
        super().__init__(app)
        self._app = app
        self._logger = log_service.getLogger(__name__)


    def applyTheme(
            self,
            theme_xml: str | None = None,
            scheme: str | None = None,
            extra: list | None = None
        ) -> None:
        self._logger.debug(
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
