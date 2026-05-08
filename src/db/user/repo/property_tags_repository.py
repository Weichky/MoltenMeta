from db.base_repository import BaseRepository
from db.snapshot import PropertyTagSnapshot

from typing import List


class PropertyTagsRepository(BaseRepository[PropertyTagSnapshot]):
    def getTableName(self) -> str:
        return "property_tags"

    def getEntityClass(self) -> type[PropertyTagSnapshot]:
        return PropertyTagSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS property_tags (
            id {dialect.getAutoincrementType()},
            property_id {dialect.getIntegerType()} NOT NULL,
            tag {dialect.getTextType()} NOT NULL,
            created_at {dialect.getDatetimeType()} DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
            UNIQUE(property_id, tag)
        )
        """

    def _getCreateIndexSql(self) -> List[str]:
        return [
            "CREATE INDEX IF NOT EXISTS idx_tags_property ON property_tags(property_id)",
            "CREATE INDEX IF NOT EXISTS idx_tags_tag ON property_tags(tag)",
        ]

    def createTable(self) -> None:
        super().createTable()
        for index_sql in self._getCreateIndexSql():
            self.connection.execute(index_sql)
        self.connection.commit()

    def findByPropertyId(self, property_id: int) -> List[PropertyTagSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_tags WHERE property_id = {placeholder}"
        cursor = self.connection.execute(sql, [property_id])
        rows = cursor.fetchall()
        return [PropertyTagSnapshot.fromRow(row) for row in rows]

    def findByTag(self, tag: str) -> List[PropertyTagSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_tags WHERE tag = {placeholder}"
        cursor = self.connection.execute(sql, [tag])
        rows = cursor.fetchall()
        return [PropertyTagSnapshot.fromRow(row) for row in rows]

    def addTag(self, property_id: int, tag: str) -> int:
        placeholder = self.dialect.getPlaceholder()
        dialect = self.dialect

        if dialect.supportsInsertOrReplace():
            sql = f"INSERT OR IGNORE INTO property_tags (property_id, tag) VALUES ({placeholder}, {placeholder})"
        else:
            sql = f"INSERT INTO property_tags (property_id, tag) VALUES ({placeholder}, {placeholder}) ON CONFLICT DO NOTHING"

        cursor = self.connection.execute(sql, [property_id, tag])
        self.connection.commit()
        self._logger.debug(f"Added tag '{tag}' to property_id {property_id}")
        return cursor.rowCount

    def addTags(self, property_id: int, tags: List[str]) -> int:
        if not tags:
            return 0

        dialect = self.dialect
        placeholder = dialect.getPlaceholder()

        if dialect.supportsInsertOrReplace():
            sql = f"INSERT OR IGNORE INTO property_tags (property_id, tag) VALUES ({placeholder}, {placeholder})"
        else:
            sql = f"INSERT INTO property_tags (property_id, tag) VALUES ({placeholder}, {placeholder}) ON CONFLICT DO NOTHING"

        try:
            params = [[property_id, tag] for tag in tags]
            self.connection.executemany(sql, params)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

        return len(tags)

    def removeTag(self, property_id: int, tag: str) -> bool:
        placeholder = self.dialect.getPlaceholder()
        sql = f"DELETE FROM property_tags WHERE property_id = {placeholder} AND tag = {placeholder}"
        cursor = self.connection.execute(sql, [property_id, tag])
        self.connection.commit()
        return cursor.rowCount > 0

    def getPropertyIdsByTag(self, tag: str) -> List[int]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT property_id FROM property_tags WHERE tag = {placeholder}"
        cursor = self.connection.execute(sql, [tag])
        rows = cursor.fetchall()
        return [row["property_id"] for row in rows]


__all__ = ["PropertyTagsRepository"]
