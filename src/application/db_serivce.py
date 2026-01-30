from core.log import getLogService
from core.platform import getRuntimePath

from core.fio import config_io

class DatabaseCConfigManager:
    DEFAULT_CONFIG_FILE = "db_config.json"

class DatabaseService:
    def __init__(self):
        self._logger = getLogService().getLogger(__name__)