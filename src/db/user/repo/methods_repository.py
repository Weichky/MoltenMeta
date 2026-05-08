from db.base_repository import BaseRepository
from db.snapshot import MethodSnapshot


class MethodsRepository(BaseRepository[MethodSnapshot]):
    def getTableName(self) -> str:
        return "methods"

    def getEntityClass(self) -> type[MethodSnapshot]:
        return MethodSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS methods (
            id {dialect.getAutoincrementType()},
            name {dialect.getTextType()} NOT NULL,
            type {dialect.getTextType()},
            detail {dialect.getTextType()}
        )
        """

    def findByName(self, name: str) -> MethodSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM methods WHERE name = {placeholder}"
        cursor = self.connection.execute(sql, [name])
        row = cursor.fetchone()

        if row:
            return MethodSnapshot.fromRow(row)
        return None


__all__ = ["MethodsRepository"]
