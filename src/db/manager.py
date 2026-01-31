from typing import Optional
from .abstraction import DatabaseConnection

from catalog import DatabaseType, DatabaseConfig

from core.platform import getRuntimePath

from .adapters.sqlite import SQLiteConnection
from .adapters.postgresql import PostgreSQLConnection

class DatabaseManager:
    """Manages database connections and provides unified interface"""

    _instance = None
    _connection: Optional[DatabaseConnection] = None
    _config: Optional[DatabaseConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def configure(self, config: DatabaseConfig) -> None:
        """Configure database connection"""
        self._config = config
        if self._connection:
            self._connection.close()
        self._connection = None

    def getConnection(self) -> DatabaseConnection:
        """Get database connection, establishing it if needed"""
        if self._connection is None:
            if self._config is None:
                # Default to SQLite in runtime directory
                runtime_path = getRuntimePath()
                if not runtime_path:
                    raise RuntimeError("No runtime path available for database")

                self._config = DatabaseConfig(
                    db_type=DatabaseType.SQLITE,
                    file_path=str(runtime_path / "moltenmeta.mmdb"),
                )

            # Create connection based on database type
            if self._config.db_type == DatabaseType.SQLITE:
                self._connection = SQLiteConnection(self._config)
            elif self._config.db_type == DatabaseType.POSTGRESQL:
                self._connection = PostgreSQLConnection(self._config)
            else:
                raise ValueError(f"Unsupported database type: {self._config.db_type}")

            self._connection.connect()

        return self._connection

    def close(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def getDialect(self):
        """Get database dialect"""
        return self.getConnection().getDialect()