# Temporarily copied from user_manager.py
# TODO: Implement a proper database manager(inculding proper path)

from catalog import DatabaseType, DatabaseConnInfo

from db.adapters.sqlite import SQLiteConnection
from db.adapters.postgresql import PostgreSQLConnection

class DatabaseManager:
    _active_conn: DatabaseConnInfo | None = None
    _conn_info: DatabaseConnInfo | None = None

    def applyConnection(self, config: DatabaseConnInfo) -> None:
        self._conn_info = config
        if self._active_conn:
            self._active_conn.close()

        # Create connection based on database type
        if self._conn_info.db_type == DatabaseType.SQLITE:
            self._active_conn = SQLiteConnection(self._conn_info)
        elif self._conn_info.db_type == DatabaseType.POSTGRESQL:
            self._active_conn = PostgreSQLConnection(self._conn_info)
        else:
            raise ValueError(f"Unsupported database type: {self._conn_info.db_type}")

        self._active_conn.connect()    

    @property
    def connection(self) -> DatabaseConnInfo:
        return self._active_conn

    @property 
    def dialect(self) -> DatabaseDialect:
        return self.connection().getDialect()

    def closeConnection(self) -> None:
        if self._active_conn:
            self._active_conn.close()
            self._active_conn = None