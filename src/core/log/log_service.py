from collections import deque

from PySide6.QtCore import QObject, Signal

import logging

from .log import getLogLevelMap

_MAX_LOG_BUFFER_SIZE = 1000


class LogService(QObject):
    log_level_changed = Signal()

    def __init__(self, app):
        super().__init__(app)
        self._log_buffer: deque[str] = deque(maxlen=_MAX_LOG_BUFFER_SIZE)

    def getLogger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)

    def setupLogging(self, level=logging.DEBUG) -> None:
        logging.basicConfig(
            level=level,
            format="[%(levelname)s](%(name)s)|%(asctime)s|%(message)s",
        )
        root = logging.getLogger()
        root.handlers.clear()
        handler = _BufferingLogHandler(self._log_buffer, level)
        handler.setFormatter(
            logging.Formatter("[%(levelname)s](%(name)s)|%(asctime)s|%(message)s")
        )
        root.addHandler(handler)
        root.setLevel(level)

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

    def getBufferedLogs(self) -> list[str]:
        return list(self._log_buffer)


class _BufferingLogHandler(logging.Handler):
    def __init__(self, buffer: deque[str], level: int):
        super().__init__()
        self._buffer = buffer
        self.setLevel(level)

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self._buffer.append(msg)
        except Exception:
            pass
