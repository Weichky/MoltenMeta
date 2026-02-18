from PySide6.QtCore import QObject

from db.core import SettingsRepository

from core.log import LogService

class CoreDbService(QObject):
    def __init__(self, app, log_service: LogService = None):
        super().__init__(app)