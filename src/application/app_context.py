from core.log import LogService
from i18n import I18nService
from db.core import CoreDatabaseManager
from db.user import UserDatabaseManager
from gui.appearance.theme import ThemeService

class AppContext:
    def __init__(
            self,
            log: LogService,
            core_db_manager: CoreDatabaseManager,
            user_db_manager: UserDatabaseManager,
            i18n: I18nService,
            theme: ThemeService):
        self.log = log
        self.core_db_manager = core_db_manager
        self.user_db_manager = user_db_manager
        self.i18n = i18n
        self.theme = theme