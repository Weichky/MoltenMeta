from PySide6.QtCore import QObject

from db.core import SettingsRepository, DatabaseManager
from .db_service import DatabaseService

from domain.settings import Settings

from core.log import LogService

from db.seeds.settings_seed import loadDefaultSettings


class CoreDbService(QObject):
    def __init__(
        self,
        app,
        log_service: LogService,
        db_manager: DatabaseManager | None = None,
    ):
        super().__init__(app)
        self._db_service = DatabaseService(log_service, db_manager)
        self._settings_repo = SettingsRepository(
            log_service=log_service, db_manager=self._db_service.getManager()
        )
        self._logger = log_service.getLogger(__name__)
        self._settings = Settings()
        self._initSettings()

    @property
    def settings_repo(self) -> SettingsRepository:
        return self._settings_repo

    def _initSettings(self) -> None:
        self._settings_repo.createTable()
        if self._settings_repo.count() == 0:
            defaults = loadDefaultSettings()
            self._settings_repo.upsert(defaults)
        self._settings = Settings(records=self._settings_repo.findAll())

    @property
    def settings(self) -> Settings:
        return self._settings
