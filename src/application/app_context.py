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
        i18n: I18nService,
        theme: ThemeService,
        core_db: CoreDbService | None = None,
    ):
        self.log = log
        self.settings = settings
        self.i18n = i18n
        self.theme = theme
        self.core_db = core_db
