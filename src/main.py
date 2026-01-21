import sys
from PySide6.QtWidgets import QApplication

from core.log import (
    createLogService,
)

from core.platform import getArgs

from core.config import (
    loadConfig,
    getLanguage,
    getLogLevel,
    getThemeXML,
    getScheme,
)

from i18n import createI18nService

from gui.appearance.theme import createThemeService

from gui.main_window import MainWindow

from resources.qt_material import default_extra

def main():

    app = QApplication(sys.argv)

    init(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
def init(app):

    log_service = createLogService(app)

    loadConfig()  

    if getArgs().log_level:
        log_service.setLogLevel(getArgs().log_level)
    else:    
        log_service.setLogLevel(getLogLevel())

    logger = log_service.getLogger("main")

    i18n_service = createI18nService(app)

    i18n_service.setLanguage(getLanguage())

    theme_service = createThemeService(app)

    theme_service.applyTheme(getThemeXML(), getScheme(), default_extra)
    
if __name__ == "__main__":
    main()