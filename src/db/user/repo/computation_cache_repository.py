from db.base_repository import BaseRepository
from db.snapshot import ComputationCacheSnapshot

from typing import List


class ComputationCacheRepository(BaseRepository[ComputationCacheSnapshot]):
    def getTableName(self) -> str:
        return "computation_cache"

    def getEntityClass(self) -> type[ComputationCacheSnapshot]:
        return ComputationCacheSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS computation_cache (
            id {dialect.getAutoincrementType()},
            run_id {dialect.getTextType()} NOT NULL,
            module_id {dialect.getTextType()} NOT NULL,
            method_name {dialect.getTextType()} NOT NULL,
            system_id {dialect.getIntegerType()},
            property_id {dialect.getIntegerType()},
            value {dialect.getRealType()} NOT NULL,
            unit {dialect.getTextType()},
            params_json {dialect.getTextType()},
            parent_run_id {dialect.getTextType()},
            is_deleted {dialect.getIntegerType()} DEFAULT 0,
            group_id {dialect.getIntegerType()},
            created_at {dialect.getDatetimeType()} DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (system_id) REFERENCES systems(id),
            FOREIGN KEY (property_id) REFERENCES properties(id),
            FOREIGN KEY (group_id) REFERENCES data_groups(id) ON DELETE SET NULL
        )
        """

    def _getCreateIndexSql(self) -> List[str]:
        return [
            "CREATE INDEX IF NOT EXISTS idx_cache_run_id ON computation_cache(run_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_module ON computation_cache(module_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_parent ON computation_cache(parent_run_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_property ON computation_cache(property_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_system ON computation_cache(system_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_group ON computation_cache(group_id)",
        ]

    def createTable(self) -> None:
        super().createTable()
        for index_sql in self._getCreateIndexSql():
            self.connection.execute(index_sql)
        self.connection.commit()

    def findByRunId(self, run_id: str) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE run_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [run_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByModuleId(self, module_id: str) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE module_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [module_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByParentRunId(self, parent_run_id: str) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE parent_run_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [parent_run_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByPropertyId(self, property_id: int) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE property_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [property_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByGroupId(self, group_id: int) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE group_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [group_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findAll(self) -> List[ComputationCacheSnapshot]:
        sql = "SELECT * FROM computation_cache WHERE is_deleted = 0"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def softDeleteByRunId(self, run_id: str) -> int:
        placeholder = self.dialect.getPlaceholder()
        sql = (
            f"UPDATE computation_cache SET is_deleted = 1 WHERE run_id = {placeholder}"
        )
        cursor = self.connection.execute(sql, [run_id])
        self.connection.commit()
        return cursor.rowCount

    def insertBatch(self, entries: list["ComputationCacheSnapshot"]) -> int:
        if not entries:
            return 0
        table = self.getTableName()
        dialect = self.dialect
        record = entries[0].toRecord()
        columns = list(record.keys())
        placeholders = ", ".join([dialect.getPlaceholder() for _ in columns])
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        try:
            params = [tuple(entry.toRecord().values()) for entry in entries]
            self.connection.executemany(sql, params)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return len(entries)

    def countActive(self) -> int:
        sql = "SELECT COUNT(*) FROM computation_cache WHERE is_deleted = 0"
        cursor = self.connection.execute(sql)
        result = cursor.fetchone()
        return result.get("count") or result.get("COUNT(*)") or 0


__all__ = ["ComputationCacheRepository"]
