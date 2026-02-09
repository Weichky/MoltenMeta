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

from resources.qt_material import default_extra
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
