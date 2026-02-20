from core.log import LogService
from core.platform import getArgs

from core.config import (
    loadConfig,
    getLanguage,
    getLogLevel,
    getThemeXML,
    getScheme,
)

from db.core import DatabaseManager

from .app_context import AppContext

from i18n import I18nService

from gui.appearance.theme import ThemeService

from resources.qt_material import default_extra
def bootstrap(app) -> AppContext:

    log_service = LogService(app)

    # loadConfig()
    core_db_manager = DatabaseManager()
    user_db_manager = DatabaseManager()

    if getArgs().log_level:
        log_service.setLogLevel(getArgs().log_level)
    else:    
        log_service.setLogLevel(getLogLevel())

    # logger = log_service.getLogger("main")

    i18n_service = I18nService(app)

    i18n_service.setLanguage(getLanguage())

    # Necessary evil
    # Inject the log service
    theme_service = ThemeService(app, log_service)

    theme_service.applyTheme(getThemeXML(), getScheme(), default_extra)

    return AppContext(
        log=log_service,
        core_db_manager=core_db_manager,
        user_db_manager=user_db_manager,
        i18n=i18n_service,
        theme=theme_service,
    )