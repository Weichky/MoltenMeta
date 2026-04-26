from core.log import LogService
from i18n import I18nService
from gui.appearance.theme import ThemeService
from domain.settings import Settings
from application.service.core_db_service import CoreDbService
from application.service.user_db_service import UserDbService
from application.service.module_service import ModuleService
from application.service.unified_data_query_service import UnifiedDataQueryService


class AppContext:
    def __init__(
        self,
        log: LogService,
        settings: Settings | None,
        i18n: I18nService,
        theme: ThemeService,
        core_db: CoreDbService | None = None,
        user_db: UserDbService | None = None,
        modules: ModuleService | None = None,
        unified_data: UnifiedDataQueryService | None = None,
    ):
        self.log = log
        self._settings = settings
        self.i18n = i18n
        self.theme = theme
        self.core_db = core_db
        self.user_db = user_db
        self.modules = modules
        self.unified_data = unified_data

    @property
    def settings(self) -> Settings | None:
        if self.core_db is not None:
            return self.core_db.settings
        return self._settings

    @settings.setter
    def settings(self, value: Settings | None) -> None:
        self._settings = value
