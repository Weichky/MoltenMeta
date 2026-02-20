from core.log import LogService

from catalog import DatabaseType, DatabaseConnInfo

from db import DatabaseManager


class DatabaseService:
    def __init__(
        self, log_service: LogService, db_manager: DatabaseManager | None = None
    ):
        self._logger = log_service.getLogger(__name__)
        self._manager = db_manager if db_manager else DatabaseManager()

    def configureDatabase(self, conn_info: DatabaseConnInfo) -> None:
        self._manager.applyConnection(conn_info)

    def getManager(self) -> DatabaseManager:
        return self._manager

    def testConnection(self) -> bool:
        try:
            connection = self._manager.connection()
            cursor = connection.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            self._logger.error(f"Database connection test failed: {e}")
            return False

    def close(self) -> None:
        self._manager.closeConnection()
