from core.log import LogService
from i18n import I18nService
from db.core import DatabaseManager
from gui.appearance.theme import ThemeService
from domain.settings import Settings


class AppContext:
    def __init__(
        self,
        log: LogService,
        settings: Settings,
        core_db_manager: DatabaseManager,
        user_db_manager: DatabaseManager,
        i18n: I18nService,
        theme: ThemeService,
    ):
        self.log = log
        self.settings = settings
        self.core_db_manager = core_db_manager
        self.user_db_manager = user_db_manager
        self.i18n = i18n
        self.theme = theme
