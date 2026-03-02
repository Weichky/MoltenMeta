from core.log import LogService
from i18n import I18nService
from db.core import DatabaseManager
from gui.appearance.theme import ThemeService
from domain.settings import Settings
from application.service.core_db_service import CoreDbService
from application.service.user_db_service import UserDbService


class AppContext:
    def __init__(
        self,
        log: LogService,
        settings: Settings | None,
        i18n: I18nService,
        theme: ThemeService,
        core_db: CoreDbService | None = None,
        user_db: UserDbService | None = None,
    ):
        self.log = log
        self.settings = settings
        self.i18n = i18n
        self.theme = theme
        self.core_db = core_db
        self.user_db = user_db
