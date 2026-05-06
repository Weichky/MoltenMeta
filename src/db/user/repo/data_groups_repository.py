from db.base_repository import BaseRepository
from db.snapshot import DataGroupSnapshot

from typing import List


class DataGroupsRepository(BaseRepository[DataGroupSnapshot]):
    def getTableName(self) -> str:
        return "data_groups"

    def getEntityClass(self) -> type[DataGroupSnapshot]:
        return DataGroupSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS data_groups (
            id {dialect.getAutoincrementType()},
            name {dialect.getTextType()} NOT NULL UNIQUE,
            priority {dialect.getIntegerType()} NOT NULL DEFAULT 0,
            created_at {dialect.getDatetimeType()} DEFAULT CURRENT_TIMESTAMP
        )
        """

    def findByName(self, name: str) -> DataGroupSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM data_groups WHERE name = {placeholder}"
        cursor = self.connection.execute(sql, [name])
        row = cursor.fetchone()

        if row:
            return DataGroupSnapshot.fromRow(row)
        return None

    def findAll(self) -> List[DataGroupSnapshot]:
        sql = "SELECT * FROM data_groups ORDER BY priority DESC, created_at DESC"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()
        return [DataGroupSnapshot.fromRow(row) for row in rows]


__all__ = ["DataGroupsRepository"]
