from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Protocol

from core.log import LogService
from .abstraction import DatabaseConnection
from .db_manager import DatabaseManager


class EntityProtocol(Protocol):
    id: int | None

    @classmethod
    def fromRow(cls, row) -> "EntityProtocol": ...

    def toRecord(self) -> dict: ...


T = TypeVar("T", bound=EntityProtocol)


class BaseRepository(ABC, Generic[T]):
    def __init__(self, log_service: LogService, db_manager: DatabaseManager):
        self._db_manager = db_manager
        self._logger = log_service.getLogger(self.__class__.__name__)

    @property
    def connection(self) -> DatabaseConnection:
        conn = self._db_manager.connection
        if conn is None:
            raise RuntimeError(
                f"Database connection not established for {self.__class__.__name__}. "
                "Ensure applyConnection() was called on the DatabaseManager."
            )
        return conn

    @property
    def dialect(self):
        return self._db_manager.dialect

    @abstractmethod
    def getTableName(self) -> str: ...

    @abstractmethod
    def getEntityClass(self) -> type[T]: ...

    def createTable(self) -> None:
        create_sql = self._getCreateTableSql()
        self.connection.execute(create_sql)
        self.connection.commit()
        self._logger.info(f"Created table {self.getTableName()}")

    @abstractmethod
    def _getCreateTableSql(self) -> str: ...

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
            if cursor.lastRowId is not None:
                object.__setattr__(entity, "id", cursor.lastRowId)
            elif dialect.getLastIdSyntax():
                # For databases that don't have lastrowid (like PostgreSQL)
                last_id_cursor = self.connection.execute(dialect.getLastIdSyntax())
                last_id_row = last_id_cursor.fetchone()
                if last_id_row:
                    object.__setattr__(
                        entity,
                        "id",
                        last_id_row.get("id") or last_id_row.get("lastval"),
                    )

        self._logger.debug(f"Inserted record into {table} with id {entity.id}")
        return entity.id or 0

    def findById(self, id: int) -> T | None:
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

    def save(self, entity: T) -> T:
        if hasattr(entity, "id") and entity.id is not None:
            self.update(entity)
            return entity
        else:
            self.insert(entity)
            return entity

    def update(self, entity: T) -> bool:
        if not hasattr(entity, "id") or entity.id is None:
            raise ValueError("Entity must have an ID to update")

        table = self.getTableName()
        record = entity.toRecord()
        columns = list(record.keys())
        placeholder = self.dialect.getPlaceholder()
        # NOTE: column names come from entity.toRecord().keys() which is internal app data,
        # not user input. For this offline desktop app with local SQLite only, SQL injection
        # is not a risk.
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
