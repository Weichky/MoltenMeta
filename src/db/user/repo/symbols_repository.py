from db.base_repository import BaseRepository
from db.snapshot import SymbolSnapshot


class SymbolsRepository(BaseRepository[SymbolSnapshot]):
    def getTableName(self) -> str:
        return "symbols"

    def getEntityClass(self) -> type[SymbolSnapshot]:
        return SymbolSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS symbols (
            id {dialect.getAutoincrementType()},
            symbol {dialect.getTextType()} NOT NULL,
            name {dialect.getTextType()},
            category {dialect.getTextType()}
        )
        """

    def findBySymbol(self, symbol: str) -> SymbolSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM symbols WHERE symbol = {placeholder}"
        cursor = self.connection.execute(sql, [symbol])
        row = cursor.fetchone()

        if row:
            return SymbolSnapshot.fromRow(row)
        return None

    def upsert(self, snapshots: list[SymbolSnapshot]) -> None:
        sql = self.dialect.getUpsertSyntax(
            table="symbols",
            columns=["symbol", "name", "category"],
        )

        try:
            for snap in snapshots:
                record = snap.toRecord()
                self.connection.execute(sql, list(record.values()))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise


__all__ = ["SymbolsRepository"]
