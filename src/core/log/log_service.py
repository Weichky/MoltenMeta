from PySide6.QtCore import QObject, Signal

import logging

from .log import getLogLevelMap

class LogService(QObject):
    log_level_changed = Signal()

    def __init__(self, app):
        super().__init__(app)

    def getLogger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)

    def setupLogging(self, level = logging.DEBUG) -> None:
        logging.basicConfig(
            level=level,
            format="[%(levelname)s](%(name)s)|%(asctime)s|%(message)s",
        )        

    def setLogLevel(self, level: str) -> None:
        level_map = getLogLevelMap()
        key = level.lower()

        if key not in level_map:
            raise ValueError(f"Invalid log level: {level}")

        lvl = level_map[key]

        root = logging.getLogger()
        root.setLevel(lvl)

        for handler in root.handlers:
            handler.setLevel(lvl)

        self.log_level_changed.emit()