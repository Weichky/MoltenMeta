import sys
from PySide6.QtWidgets import QApplication

from core.log import getLogger, setLogLevel

from core.platform import getArgs

from core.config import getConfigs

from i18n import createI18nService

from gui.main_window import MainWindow

def main():

    app = QApplication(sys.argv)

    init(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
def init(app):
    config = getConfigs()

    # Commands have higher priority
    if getArgs().log_level:
        setLogLevel(getArgs().log_level)
    else:    
        setLogLevel(config["logging"]["level"])

    logger = getLogger("main")

    logger.info("Starting application")

    i18n_service = createI18nService(app)

    i18n_service.setLanguage(config["locale"]["language"])

if __name__ == "__main__":
    main()