from PySide6.QtCore import QObject

from db.core import SettingsRepository
from .db_service import DatabaseService

from core.log import LogService

class CoreDbService(QObject):
    def __init__(self, app, log_service: LogService, database_service: DatabaseService):
        super().__init__(app)
        self._settings_repo = SettingsRepository()
        self._logger = log_service.getLogger(__name__)
        self._db_service = database_service