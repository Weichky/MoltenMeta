from core.log import getLogService

from catalog import DatabaseType, DatabaseConfig

from core.config import getDatabaseType, getDatabaseFilePath

from db import getDatabaseManager, DatabaseManager

class DatabaseConfigManager:

    _database_service: DatabaseService | None = None

    @classmethod
    def generateConfig(cls) -> DatabaseConfig:
        db_type = getDatabaseType()

        # postgresql is not our goal for now
        if db_type == DatabaseType.POSTGRESQL:
            return DatabaseConfig(
                db_type=db_type,
                    # host=os.getenv("MOLTENMETA_DB_HOST", "localhost"),
                    # port=int(os.getenv("MOLTENMETA_DB_PORT", "5432")),
                    # database=os.getenv("MOLTENMETA_DB_NAME", "moltenmeta"),
                    # username=os.getenv("MOLTENMETA_DB_USER", "moltenmeta"),
                    # password=os.getenv("MOLTENMETA_DB_PASSWORD"),
            )
        elif db_type == DatabaseType.SQLITE:
            return DatabaseConfig(
                db_type=db_type,
                file_path=getDatabaseFilePath(),
            )        
def getDatabaseService() -> DatabaseService:
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service

def configureDatabase(config: DatabaseConfig | None = None) -> None:
    global _database_service
    if _database_service is None:
        raise RuntimeError("Database service not created")

    _database_service.configureDatabase(config)

    if not _database_service.testConnection():
        raise RuntimeError("Failed to connect to database")
    
def closeDatabase() -> None:
    global _database_service
    if _database_service:
        _database_service.close()
        _database_service = None

class DatabaseService:
    def __init__(self):
        self._logger = getLogService().getLogger(__name__)
        self._manager = getDatabaseManager()

    def configureDatabase(self, config: DatabaseConfig | None = None) -> None:
        if config is None:
            config = DatabaseConfigManager.generateConfig()

        self._manager.configure(config)
        # 注意此处写法问题
        # 类DatabaseService、类DatabaseManager和类DatabaseConfigManager写法耦合

    def getManager(self) -> DatabaseManager:
        return self._manager
    
    def testConnection(self) -> bool:
        try:
            connection = self._manager.getConnection()
            cursor = connection.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            self._logger.error(f"Database connection test failed: {e}")
            return False

    def close(self) -> None:
        self._manager.close()