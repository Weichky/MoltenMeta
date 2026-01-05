import logging

def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def setupLogging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(levelname)s](%(name)s)|%(asctime)s|%(message)s",
    )