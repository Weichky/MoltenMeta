import logging

def setLoggingLevel(level: str):
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    logging.getLogger().setLevel(level_map[level])