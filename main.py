import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale, QTranslator, QLibraryInfo

from gui.main_window import MainWindow
from core.fio import loadConfig
from core.log import getLogger, setupLogging
from core.configure import setLogLevel

import logging

def main():

    init()

    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


def init():
    setupLogging(logging.DEBUG)
    logger = getLogger("main")

    logger.info("Starting application")

    config = loadConfig()

    logger.info("Configuration ready")

    setLogLevel(config["logging"]["level"])

    logger.info("Logging level: " + config["logging"]["level"])
    
if __name__ == "__main__":
    main()