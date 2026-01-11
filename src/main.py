import sys
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from core.log import getLogger, setupLogging, setLogLevel

from core.config import getConfigs

from i18n import getI18nService, createI18nService

import logging

translator = None

def main():

    app = QApplication(sys.argv)

    init(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


def init(app):
    setupLogging(logging.DEBUG)
    logger = getLogger("main")

    logger.info("Starting application")

    config = getConfigs()

    setLogLevel(config["logging"]["level"])

    logger.info("Logging level: " + config["logging"]["level"]) 

    i18n_service = createI18nService(app)

    i18n_service.setLanguage(config["locale"]["language"])

if __name__ == "__main__":
    main()