from db.base_repository import BaseRepository
from db.snapshot import PropertySnapshot

from typing import List


class PropertiesRepository(BaseRepository[PropertySnapshot]):
    def getTableName(self) -> str:
        return "properties"

    def getEntityClass(self) -> type[PropertySnapshot]:
        return PropertySnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS properties (
            id {dialect.getAutoincrementType()},
            name {dialect.getTextType()} NOT NULL UNIQUE,
            symbol_id {dialect.getIntegerType()} NOT NULL,
            unit_id {dialect.getIntegerType()} NOT NULL,
            category {dialect.getTextType()},
            FOREIGN KEY (symbol_id) REFERENCES symbols(id) ON DELETE RESTRICT,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE RESTRICT
        )
        """

    def findByName(self, name: str) -> PropertySnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM properties WHERE name = {placeholder}"
        cursor = self.connection.execute(sql, [name])
        row = cursor.fetchone()

        if row:
            return PropertySnapshot.fromRow(row)
        return None

    def findByCategory(self, category: str) -> List[PropertySnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM properties WHERE category = {placeholder}"
        cursor = self.connection.execute(sql, [category])
        rows = cursor.fetchall()
        return [PropertySnapshot.fromRow(row) for row in rows]

    def upsert(self, snapshot: PropertySnapshot) -> int:
        existing = self.findByName(snapshot.name)
        if existing is not None:
            record = snapshot.toRecord()
            record["id"] = existing.id
            dialect = self.dialect
            set_clause = ", ".join(
                [f"{col} = {dialect.getPlaceholder()}" for col in record.keys()]
            )
            values = list(record.values())
            sql = f"UPDATE {self.getTableName()} SET {set_clause} WHERE id = {dialect.getPlaceholder()}"
            values.append(existing.id)
            self.connection.execute(sql, values)
            self.connection.commit()
            return existing.id
        else:
            return self.insert(snapshot)


__all__ = ["PropertiesRepository"]
