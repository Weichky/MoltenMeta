from PySide6.QtCore import QObject, Signal

import logging

from .log import getLogLevelMap
_log_service: _LogService | None = None

class _LogService(QObject):
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

# Also see function getI18nService() in i18n_service.py
def getLogService() -> _LogService:
    global _log_service
    if _log_service:
        return _log_service
    
    raise RuntimeError("log service not created")

# You cannot create service twice
def createLogService(app) -> _LogService:
    global _log_service
    if _log_service:
        raise RuntimeError("Log service already created")
    
    _log_service = _LogService(app)

    getLogService().setupLogging()

    getLogService().getLogger("log service").debug("Log service created")
    return _log_service