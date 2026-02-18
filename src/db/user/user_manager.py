from db.abstraction import DatabaseConnection

from catalog import DatabaseType, DatabaseConnInfo

from core.platform import getRuntimePath

from db.adapters.sqlite import SQLiteConnection
from db.adapters.postgresql import PostgreSQLConnection
def getCoreDatabaseManager() -> UserDatabaseManager:
    database_manager = UserDatabaseManager()
    return database_manager

class UserDatabaseManager:
    _active_conn: DatabaseConnInfo | None = None
    _config: DatabaseConnInfo | None = None

    def applyConnection(self, config: DatabaseConnInfo) -> None:
        self._config = config
        if self._active_conn:
            self._active_conn.close()
        self._active_conn = None

    def getConnection(self) -> DatabaseConnInfo:
        if self._active_conn is None:
            if self._config is None:
                # Default to SQLite in runtime directory
                runtime_path = getRuntimePath()
                if not runtime_path:
                    raise RuntimeError("No runtime path available for database")

                self._config = DatabaseConnInfo(
                    db_type=DatabaseType.SQLITE,
                    file_path=str(runtime_path / "moltenmeta.mmdb"),
                )

            # Create connection based on database type
            if self._config.db_type == DatabaseType.SQLITE:
                self._active_conn = SQLiteConnection(self._config)
            elif self._config.db_type == DatabaseType.POSTGRESQL:
                self._active_conn = PostgreSQLConnection(self._config)
            else:
                raise ValueError(f"Unsupported database type: {self._config.db_type}")

            self._active_conn.connect()

        return self._active_conn

    def close(self) -> None:
        if self._active_conn:
            self._active_conn.close()
            self._active_conn = None

    def getDialect(self):
        return self.getConnection().getDialect()