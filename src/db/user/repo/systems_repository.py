from db.base_repository import BaseRepository
from db.snapshot import SystemSnapshot


class SystemsRepository(BaseRepository[SystemSnapshot]):
    def getTableName(self) -> str:
        return "systems"

    def getEntityClass(self) -> type[SystemSnapshot]:
        return SystemSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS systems (
            id {dialect.getAutoincrementType()},
            label {dialect.getTextType()} NOT NULL,
            n_component {dialect.getIntegerType()}
        )
        """

    def findByLabel(self, label: str) -> SystemSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM systems WHERE label = {placeholder}"
        cursor = self.connection.execute(sql, [label])
        row = cursor.fetchone()

        if row:
            return SystemSnapshot.fromRow(row)
        return None


__all__ = ["SystemsRepository"]
