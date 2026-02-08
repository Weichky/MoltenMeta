from pathlib import Path

from catalog import LogLevel
from core.log import getLogService

from db.repo import SettingsRepository

class SettingsQuery:
    def __init__(self, settings_repository: SettingsRepository):
        self._repo = settings_repository
        self._logger = getLogService().getLogger(__name__)
    
    def getLogLevel(self) -> LogLevel | None:
        snapshot = self._repo.findBySectionAndKey("log", "level")
        if snapshot and snapshot.value:
            return LogLevel(snapshot.value)
        return None
    
    def getLanguage(self) -> str | None:
        snapshot = self._repo.findBySectionAndKey("locale", "language")
        if snapshot and snapshot.value:
            return snapshot.value
        return None
    def getTheme(self) -> str | None:
        snapshot = self._repo.findBySectionAndKey("appearance", "theme")
        if snapshot and snapshot.value:
            return snapshot.value
        return None
    
    def isAutoDarkModeEnabled(self) -> bool | None:
        snapshot = self._repo.findBySectionAndKey("appearance", "enable_auto_dark_mode")
        if snapshot and snapshot.value:
            return snapshot.value == "true"
        return None
