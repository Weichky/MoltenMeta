import logging

from catalog import LogLevel

def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def setupLogging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(levelname)s](%(name)s)|%(asctime)s|%(message)s",
    )

def setLogLevel(level: str) -> None:
    level_map = getLogLevelMap()
    key = level.lower()

    if key not in level_map:
        raise ValueError(f"Invalid log level: {level}")

    lvl = level_map[key]

    root = logging.getLogger()
    root.setLevel(lvl)

    for handler in root.handlers:
        handler.setLevel(lvl)

def getLogLevelMap() -> dict[str, int]:
    return {
        lvl.value: getattr(logging, lvl.name)
        for lvl in LogLevel
    }