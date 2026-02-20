from PySide6.QtCore import QObject

from db.core import SettingsRepository
from .db_service import DatabaseService

from domain.settings import Settings

from core.log import LogService

class CoreDbService(QObject):
    def __init__(self, app, log_service: LogService, database_service: DatabaseService, settings: Settings):
        super().__init__(app)
        self._settings_repo = SettingsRepository()
        self._logger = log_service.getLogger(__name__)
        self._db_service = database_service
        self._settings = settings
        self._loadSettings()

    def _loadSettings(self) -> None:
        self._settings = self._settings_repo.findAll()