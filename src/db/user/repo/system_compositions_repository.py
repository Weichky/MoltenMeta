from db.base_repository import BaseRepository
from db.snapshot import SystemCompositionSnapshot

from typing import List


class SystemCompositionsRepository(BaseRepository[SystemCompositionSnapshot]):
    def getTableName(self) -> str:
        return "system_compositions"

    def getEntityClass(self) -> type[SystemCompositionSnapshot]:
        return SystemCompositionSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS system_compositions (
            system_id {dialect.getIntegerType()} NOT NULL,
            element_id {dialect.getIntegerType()} NOT NULL,
            fraction {dialect.getRealType()} NOT NULL,
            PRIMARY KEY (system_id, element_id),
            FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE,
            FOREIGN KEY (element_id) REFERENCES elements(id) ON DELETE RESTRICT
        )
        """

    def findBySystemId(self, system_id: int) -> List[SystemCompositionSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM system_compositions WHERE system_id = {placeholder}"
        cursor = self.connection.execute(sql, [system_id])
        rows = cursor.fetchall()
        return [SystemCompositionSnapshot.fromRow(row) for row in rows]

    def insertBatch(self, items: List[SystemCompositionSnapshot]) -> int:
        if not items:
            return 0

        table = self.getTableName()
        dialect = self.dialect
        record_keys = list(items[0].toRecord().keys())
        placeholders = ", ".join([dialect.getPlaceholder() for _ in record_keys])

        if dialect.supportsInsertOrReplace():
            sql = f"INSERT OR IGNORE INTO {table} ({', '.join(record_keys)}) VALUES ({placeholders})"
        else:
            columns = ", ".join(record_keys)
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

        try:
            params = [tuple(item.toRecord().values()) for item in items]
            self.connection.executemany(sql, params)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return len(items)


__all__ = ["SystemCompositionsRepository"]
