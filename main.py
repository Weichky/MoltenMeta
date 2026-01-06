import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator

from gui.main_window import MainWindow
from core.fio import getLanguagePackagePath
from core.log import getLogger, setupLogging, setLogLevel

from core.config import getConfigs
from i18n import language

import logging

translator = None

def main():

    app = QApplication(sys.argv)

    init()
    
    init_i18n(app)

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


def init():
    setupLogging(logging.DEBUG)
    logger = getLogger("main")

    logger.info("Starting application")

    config = getConfigs()

    setLogLevel(config["logging"]["level"])

    logger.info("Logging level: " + config["logging"]["level"]) 

def init_i18n(app):
    config = getConfigs()

    language = config["locale"]["language"]

    translator = QTranslator(app)

    translator.load(getLanguagePackagePath(language))

    app.installTranslator(translator)

if __name__ == "__main__":
    main()