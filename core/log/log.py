import logging

def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def setupLogging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(levelname)s](%(name)s)|%(asctime)s|%(message)s",
    )

def setLogLevel(level: str):
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    logging.getLogger().setLevel(level_map[level])

def getLogLevelMap() -> dict:
    return {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }