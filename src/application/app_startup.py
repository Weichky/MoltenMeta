from core.log import LogService
from core.platform import getArgs, getRuntimePath

from db.core import DatabaseManager
from catalog import DatabaseType, DatabaseConnInfo, UI_THEME_PRIMARY_DEFAULT, UI_THEME_SECONDARY_DEFAULT

from .app_context import AppContext

from application.settings import Settings

from application.service.core_db_service import CoreDbService
from application.service.user_db_service import UserDbService
from application.service.module_service import ModuleService
from application.service.unified_data_query_service import UnifiedDataQueryService
from i18n import I18nService

from gui.appearance.theme import ThemeService


def _createCoreDbManager() -> DatabaseManager:
    db_manager = DatabaseManager()
    runtime_path = getRuntimePath()
    db_path = runtime_path / "data" / "core" / "core.mmdb"

    conn_info = DatabaseConnInfo(db_type=DatabaseType.SQLITE, file_path=db_path)
    db_manager.applyConnection(conn_info)
    return db_manager


def _createUserDbManager(settings: Settings) -> DatabaseManager:
    db_manager = DatabaseManager()
    runtime_path = getRuntimePath()
    db_path = runtime_path / settings.sqlite_db_path

    db_type = DatabaseType(settings.database_type)
    conn_info = DatabaseConnInfo(db_type=db_type, file_path=db_path)
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
        log=log_service, i18n=i18n_service, theme=theme_service, settings=None
    )


def initApp(app) -> AppContext:
    context = bootstrap(app)
    db_manager = _createCoreDbManager()
    core_db_service = CoreDbService(app, context.log, db_manager)
    context.core_db = core_db_service
    context.settings = core_db_service.settings

    user_db_manager = _createUserDbManager(context.settings)
    user_db_service = UserDbService(
        app,
        context.log,
        user_db_manager,
    )
    context.user_db = user_db_service

    context.log.setLogLevel(core_db_service.settings.log_level)
    context.i18n.setLanguage(core_db_service.settings.language)
    context.theme.initialize(
        core_db_service.settings.scheme,
        core_db_service.settings.theme_mode,
        core_db_service.settings.density_scale,
    )
    primary = core_db_service.settings.primary_color or UI_THEME_PRIMARY_DEFAULT
    secondary = core_db_service.settings.secondary_color or UI_THEME_SECONDARY_DEFAULT
    context.theme.updateThemeColors(primary, secondary)

    context.modules = ModuleService(getRuntimePath(), context.log)
    context.modules.setRepositories(
        user_db_service.computation_cache_repo,
        user_db_service.property_tags_repo,
        user_db_service.symbol_repo,
        user_db_service.unit_repo,
        user_db_service.property_repo,
    )
    context.modules.registerAllModulesProperties()

    context.unified_data = UnifiedDataQueryService(context.log, user_db_service)

    return context
