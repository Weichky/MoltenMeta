from db.base_repository import BaseRepository
from db.snapshot import PropertyValueSnapshot

from typing import List


class PropertyValuesRepository(BaseRepository[PropertyValueSnapshot]):
    def getTableName(self) -> str:
        return "property_values"

    def getEntityClass(self) -> type[PropertyValueSnapshot]:
        return PropertyValueSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS property_values (
            id {dialect.getAutoincrementType()},
            system_id {dialect.getIntegerType()} NOT NULL,
            property_id {dialect.getIntegerType()} NOT NULL,
            method_id {dialect.getIntegerType()},
            value {dialect.getRealType()} NOT NULL,
            group_id {dialect.getIntegerType()},
            FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE,
            FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE RESTRICT,
            FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE SET NULL,
            FOREIGN KEY (group_id) REFERENCES data_groups(id) ON DELETE SET NULL
        )
        """

    def findBySystemId(self, system_id: int) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE system_id = {placeholder}"
        cursor = self.connection.execute(sql, [system_id])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def findByPropertyId(self, property_id: int) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE property_id = {placeholder}"
        cursor = self.connection.execute(sql, [property_id])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def findByGroupId(self, group_id: int) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE group_id = {placeholder}"
        cursor = self.connection.execute(sql, [group_id])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def findByGroupIdPaginated(
        self, group_id: int, limit: int, offset: int
    ) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE group_id = {placeholder} ORDER BY id LIMIT {limit} OFFSET {offset}"
        cursor = self.connection.execute(sql, [group_id])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def countByGroupId(self, group_id: int) -> int:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT COUNT(*) as cnt FROM property_values WHERE group_id = {placeholder}"
        cursor = self.connection.execute(sql, [group_id])
        row = cursor.fetchone()
        return row["cnt"] if row else 0

    def findUngroupedPaginated(
        self, limit: int, offset: int
    ) -> List[PropertyValueSnapshot]:
        sql = f"SELECT * FROM property_values WHERE group_id IS NULL ORDER BY id LIMIT {limit} OFFSET {offset}"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def countUngrouped(self) -> int:
        sql = "SELECT COUNT(*) as cnt FROM property_values WHERE group_id IS NULL"
        cursor = self.connection.execute(sql)
        row = cursor.fetchone()
        return row["cnt"] if row else 0

    def updateGroupIdBatch(self, data_ids: list[int], new_group_id: int | None) -> int:
        if not data_ids:
            return 0
        placeholders = ", ".join([self.dialect.getPlaceholder() for _ in data_ids])
        if new_group_id is None:
            sql = f"UPDATE property_values SET group_id = NULL WHERE id IN ({placeholders})"
        else:
            sql = f"UPDATE property_values SET group_id = {self.dialect.getPlaceholder()} WHERE id IN ({placeholders})"
            data_ids = [new_group_id] + data_ids
        cursor = self.connection.execute(sql, data_ids)
        self.connection.commit()
        return cursor.rowCount

    def findAll(self) -> List[PropertyValueSnapshot]:
        sql = "SELECT * FROM property_values"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]


__all__ = ["PropertyValuesRepository"]
