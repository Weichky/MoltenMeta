from db.base_repository import BaseRepository
from db.snapshot import MetaSnapshot

from typing import List


class MetaRepository(BaseRepository[MetaSnapshot]):
    def getTableName(self) -> str:
        return "meta"

    def getEntityClass(self) -> type[MetaSnapshot]:
        return MetaSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS meta (
            value_id {dialect.getIntegerType()} PRIMARY KEY,
            created_at {dialect.getDatetimeType()} DEFAULT CURRENT_TIMESTAMP,
            created_by {dialect.getTextType()},
            source_file {dialect.getTextType()},
            source_type {dialect.getTextType()} DEFAULT 'imported',
            FOREIGN KEY (value_id) REFERENCES property_values(id) ON DELETE CASCADE
        )
        """

    def findByValueId(self, value_id: int) -> List[MetaSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM meta WHERE value_id = {placeholder}"
        cursor = self.connection.execute(sql, [value_id])
        rows = cursor.fetchall()
        return [MetaSnapshot.fromRow(row) for row in rows]

    def insert(self, entity: MetaSnapshot) -> int:
        table = self.getTableName()
        record = entity.toRecord()
        columns = list(record.keys())
        values = list(record.values())

        dialect = self.dialect

        if dialect.supportsInsertOrReplace():
            placeholders = ", ".join([dialect.getPlaceholder() for _ in columns])
            sql = f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            self.connection.execute(sql, values)
        else:
            sql = dialect.getUpsertSyntax(table, columns)
            self.connection.execute(sql, values)

        self.connection.commit()

        self._logger.debug(
            f"Inserted/Updated record in {table} with value_id {entity.value_id}"
        )
        return entity.value_id


__all__ = ["MetaRepository"]
