# Temporarily copied from user_manager.py
# TODO: Implement a proper database manager(inculding proper path)

from catalog import DatabaseType, DatabaseConnInfo

from db.adapters.sqlite import SQLiteConnection
from db.adapters.postgresql import PostgreSQLConnection
from db.abstraction import DatabaseDialect, DatabaseConnection

from core.log import LogService


class DatabaseManager:
    _active_conn: DatabaseConnection | None = None
    _conn_info: DatabaseConnInfo | None = None
    _log_service: LogService | None = None

    def applyConnection(
        self, config: DatabaseConnInfo, log_service: LogService | None = None
    ) -> None:
        self._conn_info = config
        self._log_service = log_service
        if self._active_conn:
            self._active_conn.close()

        # Create connection based on database type
        if self._conn_info.db_type == DatabaseType.SQLITE:
            self._active_conn = SQLiteConnection(
                self._conn_info, log_service or LogService(None)
            )
        elif self._conn_info.db_type == DatabaseType.POSTGRESQL:
            self._active_conn = PostgreSQLConnection(
                self._conn_info, log_service or LogService(None)
            )
        else:
            raise ValueError(f"Unsupported database type: {self._conn_info.db_type}")

        self._active_conn.connect()

    @property
    def connection(self) -> DatabaseConnection | None:
        return self._active_conn

    @property
    def dialect(self) -> DatabaseDialect:
        return self.connection.getDialect()

    def closeConnection(self) -> None:
        if self._active_conn:
            self._active_conn.close()
            self._active_conn = None
