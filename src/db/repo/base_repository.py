from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Any, Protocol
from pathlib import Path

from core.platform import getRuntimePath
from core.log import getLogService
from ..abstraction import DatabaseConnection, DatabaseConfig, DatabaseType
from ..adapters.sqlite import SQLiteConnection
from ..adapters.postgresql import PostgreSQLConnection


class EntityProtocol(Protocol):
    id: Optional[int]

    @classmethod
    def fromRow(cls, row) -> "EntityProtocol": ...

    def toRecord(self) -> dict: ...


T = TypeVar("T", bound=EntityProtocol)


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


class BaseRepository(ABC, Generic[T]):
    def __init__(self):
        self._db_manager = DatabaseManager()
        self._logger = getLogService().getLogger(self.__class__.__name__)

    @property
    def connection(self) -> DatabaseConnection:
        return self._db_manager.getConnection()

    @property
    def dialect(self):
        """Get database dialect for SQL generation"""
        return self._db_manager.getDialect()

    @abstractmethod
    def getTableName(self) -> str:
        ...

    @abstractmethod
    def getEntityClass(self) -> type[T]:
        ...

    def createTable(self) -> None:
        create_sql = self._getCreateTableSql()
        self.connection.execute(create_sql)
        self.connection.commit()
        self._logger.info(f"Created table {self.getTableName()}")

    @abstractmethod
    def _getCreateTableSql(self) -> str:
        ...

    def insert(self, entity: T) -> int:
        table = self.getTableName()
        record = entity.toRecord()
        columns = list(record.keys())
        dialect = self.dialect

        placeholders = ", ".join([dialect.getPlaceholder() for _ in columns])
        values = list(record.values())

        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

        cursor = self.connection.execute(sql, values)
        self.connection.commit()

        # Handle last ID differently for different databases
        if hasattr(entity, "id"):
            if cursor.lastRowId:
                entity.id = cursor.lastRowId
            elif dialect.getLastIdSyntax():
                # For databases that don't have lastrowid (like PostgreSQL)
                last_id_cursor = self.connection.execute(dialect.getLastIdSyntax())
                last_id_row = last_id_cursor.fetchone()
                if last_id_row:
                    entity.id = last_id_row.get("id") or last_id_row.get("lastval")

        self._logger.debug(f"Inserted record into {table} with id {entity.id}")
        return entity.id or 0

    def findById(self, id: int) -> Optional[T]:
        table = self.getTableName()
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM {table} WHERE id = {placeholder}"
        cursor = self.connection.execute(sql, [id])
        row = cursor.fetchone()

        if row:
            entity_class = self.getEntityClass()
            return entity_class.fromRow(row)  # type: ignore
        return None

    def findAll(self) -> List[T]:
        table = self.getTableName()
        sql = f"SELECT * FROM {table}"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()

        entity_class = self.getEntityClass()
        return [entity_class.fromRow(row) for row in rows]  # type: ignore

    def update(self, entity: T) -> bool:
        if not hasattr(entity, "id") or entity.id is None:
            raise ValueError("Entity must have an ID to update")

        table = self.getTableName()
        record = entity.toRecord()
        columns = list(record.keys())
        placeholder = self.dialect.getPlaceholder()
        set_clause = ", ".join([f"{col} = {placeholder}" for col in columns])
        values = list(record.values())
        values.append(entity.id)

        sql = f"UPDATE {table} SET {set_clause} WHERE id = {placeholder}"
        cursor = self.connection.execute(sql, values)
        self.connection.commit()

        updated = cursor.rowCount > 0
        if updated:
            self._logger.debug(f"Updated record in {table} with id {entity.id}")
        return updated

    def delete(self, id: int) -> bool:
        table = self.getTableName()
        placeholder = self.dialect.getPlaceholder()
        sql = f"DELETE FROM {table} WHERE id = {placeholder}"
        cursor = self.connection.execute(sql, [id])
        self.connection.commit()

        deleted = cursor.rowCount > 0
        if deleted:
            self._logger.debug(f"Deleted record from {table} with id {id}")
        return deleted

    def count(self) -> int:
        table = self.getTableName()
        sql = f"SELECT COUNT(*) FROM {table}"
        cursor = self.connection.execute(sql)
        result = cursor.fetchone()
        return result.get("count") or result.get("COUNT(*)") or 0
