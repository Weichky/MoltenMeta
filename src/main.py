import sys
from PySide6.QtWidgets import QApplication

from core.log import getLogger, setLogLevel, setupLogging

from core.platform import getArgs

from core.config import (
    loadConfig,
    getLanguage,
    getLogLevel,
    getThemeXML,
    getScheme,
)

from i18n import createI18nService

from gui.appearance.theme import applyStyleSheet

from gui.main_window import MainWindow

def main():

    app = QApplication(sys.argv)

    init(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
def init(app):
    # Can set log level here
    # Accept logging level such as logging.DEBUG, logging.INFO, etc.
    setupLogging()

    loadConfig()  

    if getArgs().log_level:
        setLogLevel(getArgs().log_level)
    else:    
        setLogLevel(getLogLevel())

    logger = getLogger("main")

    logger.info("Starting application")

    i18n_service = createI18nService(app)

    i18n_service.setLanguage(getLanguage())

    applyStyleSheet(app, getThemeXML(), getScheme())

if __name__ == "__main__":
    main()