from core.log import LogService
from core.platform import getArgs, getRuntimePath

from db.core import DatabaseManager
from catalog import DatabaseType, DatabaseConnInfo

from .app_context import AppContext

from domain.settings import Settings

from application.service.core_db_service import CoreDbService
from i18n import I18nService

from gui.appearance.theme import ThemeService

from resources.qt_material import default_extra


def _createCoreDbManager() -> DatabaseManager:
    db_manager = DatabaseManager()
    runtime_path = getRuntimePath()
    if runtime_path:
        db_path = runtime_path / "data" / "core" / "core.mmdb"

    conn_info = DatabaseConnInfo(db_type=DatabaseType.SQLITE, file_path=db_path)
    db_manager.applyConnection(conn_info)
    return db_manager


def bootstrap(app) -> AppContext:
    log_service = LogService(app)
    log_service.setupLogging()

    if getArgs().log_level:
        log_service.setLogLevel(getArgs().log_level)

    # logger = log_service.getLogger("main")

    i18n_service = I18nService(app)

    # Necessary evil
    # Inject the log service
    theme_service = ThemeService(app, log_service)

    return AppContext(
        log=log_service,
        i18n=i18n_service,
        theme=theme_service,
        settings=None
    )


def initApp(app) -> AppContext:
    context = bootstrap(app)
    db_manager = _createCoreDbManager()
    core_db_service = CoreDbService(
        app, 
        context.log, 
        db_manager
    )
    context.core_db = core_db_service
    context.settings = core_db_service.settings

    context.log.setLogLevel(core_db_service.settings.log_level)
    context.i18n.setLanguage(core_db_service.settings.language)
    context.theme.initialize(
        core_db_service.settings.theme,
        core_db_service.settings.scheme,
        core_db_service.settings.theme_mode,
    )

    return context
