import sqlite3
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..abstraction import (
    DatabaseDialect,
    DatabaseConnection,
    DatabaseCursor,
)

from catalog import DatabaseConfig

from core.log import getLogService


class SQLiteDialect(DatabaseDialect):
    """SQLite-specific SQL dialect"""

    def getPlaceholder(self) -> str:
        return "?"

    def getAutoincrementType(self) -> str:
        return "INTEGER PRIMARY KEY AUTOINCREMENT"

    def getPrimaryKeyType(self) -> str:
        return "INTEGER PRIMARY KEY"

    def getTextType(self) -> str:
        return "TEXT"

    def getRealType(self) -> str:
        return "REAL"

    def getIntegerType(self) -> str:
        return "INTEGER"

    def getDatetimeType(self) -> str:
        return "DATETIME"

    def supportsInsertOrReplace(self) -> bool:
        return True

    def getUpsertSyntax(self, table: str, columns: List[str]) -> str:
        placeholders = ", ".join([self.getPlaceholder() for _ in columns])
        return f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    def getLastIdSyntax(self) -> str:
        return "SELECT last_insert_rowid()"


class SQLiteCursor(DatabaseCursor):
    """SQLite cursor wrapper"""

    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def fetchone(self) -> Optional[Dict[str, Any]]:
        row = self._cursor.fetchone()
        if row:
            return dict(row)
        return None

    def fetchall(self) -> List[Dict[str, Any]]:
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]

    @property
    def rowCount(self) -> int:
        return self._cursor.rowcount

    @property
    def lastRowId(self) -> Optional[int]:
        return self._cursor.lastrowid


class SQLiteConnection(DatabaseConnection):
    """SQLite connection implementation"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection: Optional[sqlite3.Connection] = None
        self._dialect = SQLiteDialect()
        self._logger = getLogService().getLogger(__name__)

    def connect(self) -> None:
        if self.config.file_path is None:
            raise ValueError("SQLite requires file_path in config")

        db_path = Path(self.config.file_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(db_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")

        self._logger.info(f"Connected to SQLite database at {db_path}")

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            self._logger.info("Closed SQLite connection")

    def execute(self, sql: str, params: Optional[List[Any]] = None) -> DatabaseCursor:
        if not self._connection:
            raise RuntimeError("Database connection not established")

        cursor = self._connection.execute(sql, params or [])
        return SQLiteCursor(cursor)

    def commit(self) -> None:
        if self._connection:
            self._connection.commit()

    def rollback(self) -> None:
        if self._connection:
            self._connection.rollback()

    def getDialect(self) -> DatabaseDialect:
        return self._dialect
