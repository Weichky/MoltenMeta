from db.base_repository import BaseRepository
from db.snapshot import ElementSnapshot


class ElementsRepository(BaseRepository[ElementSnapshot]):
    def getTableName(self) -> str:
        return "elements"

    def getEntityClass(self) -> type[ElementSnapshot]:
        return ElementSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS elements (
            id {dialect.getIntegerType()} PRIMARY KEY,
            symbol_id {dialect.getIntegerType()} NOT NULL,
            atomic_mass {dialect.getRealType()},
            melting_point {dialect.getRealType()},
            boiling_point {dialect.getRealType()},
            liquid_range {dialect.getRealType()},
            FOREIGN KEY (symbol_id) REFERENCES symbols(id) ON DELETE RESTRICT
        )
        """

    def findBySymbolId(self, symbol_id: int) -> ElementSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM elements WHERE symbol_id = {placeholder}"
        cursor = self.connection.execute(sql, [symbol_id])
        row = cursor.fetchone()

        if row:
            return ElementSnapshot.fromRow(row)
        return None


__all__ = ["ElementsRepository"]
