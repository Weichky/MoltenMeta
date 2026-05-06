from db.base_repository import BaseRepository
from db.snapshot import UnitSnapshot


class UnitsRepository(BaseRepository[UnitSnapshot]):
    def getTableName(self) -> str:
        return "units"

    def getEntityClass(self) -> type[UnitSnapshot]:
        return UnitSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS units (
            id {dialect.getAutoincrementType()},
            symbol_id {dialect.getIntegerType()} NOT NULL,
            FOREIGN KEY (symbol_id) REFERENCES symbols(id) ON DELETE RESTRICT
        )
        """

    def findBySymbol(self, symbol: str) -> UnitSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"""
            SELECT u.*, s.symbol
            FROM units u
            LEFT JOIN symbols s ON u.symbol_id = s.id
            WHERE s.symbol = {placeholder}
        """
        cursor = self.connection.execute(sql, [symbol])
        row = cursor.fetchone()

        if row:
            return UnitSnapshot.fromRow(row)
        return None

    def upsertBySymbolId(self, symbol_id: int) -> int:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT id FROM {self.getTableName()} WHERE symbol_id = {placeholder}"
        cursor = self.connection.execute(sql, [symbol_id])
        row = cursor.fetchone()
        if row:
            return row["id"]
        sql = f"INSERT INTO {self.getTableName()} (symbol_id) VALUES ({placeholder})"
        cursor = self.connection.execute(sql, [symbol_id])
        self.connection.commit()
        return cursor.lastRowId


__all__ = ["UnitsRepository"]
