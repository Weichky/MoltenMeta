from core.log import LogService
from core.platform import getArgs

from db.core import DatabaseManager

from .app_context import AppContext

from domain.settings import Settings

from application.service.core_db_service import CoreDbService
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

    # logger = log_service.getLogger("main")

    i18n_service = I18nService(app)

    # Necessary evil
    # Inject the log service
    theme_service = ThemeService(app, log_service)

    return AppContext(
        log=log_service,
        core_db_manager=core_db_manager,
        user_db_manager=user_db_manager,
        i18n=i18n_service,
        theme=theme_service,
        settings=Settings
    )

def initApp(app) -> AppContext:
    context = bootstrap(app)
    core_db_service = CoreDbService(app, context.log, context.core_db_manager, context.settings)
    context.log.setLogLevel(core_db_service.settings.log_level)
    context.i18n.setLanguage(core_db_service.settings.language)
    context.theme.applyTheme(core_db_service.settings.theme_XML, core_db_service.settings.scheme, default_extra)