from db.base_repository import BaseRepository
from domain.snapshot import SettingsSnapshot

from typing import List

class SettingsRepository(BaseRepository[SettingsSnapshot]):
    def getTableName(self) -> str:
        return "settings"

    def getEntityClass(self) -> type[SettingsSnapshot]:
        return SettingsSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS settings (
            id {dialect.getAutoincrementType()},
            section {dialect.getTextType()} NOT NULL,
            key {dialect.getTextType()} NOT NULL,
            value {dialect.getTextType()} NOT NULL,
            UNIQUE(section, key)
        )
        """
    
    def upsert(self, snapshots: List[SettingsSnapshot]) -> None:
            sql = self.dialect.getUpsertSyntax(
                table="settings",
                columns=["section", "key", "value"],
            )

            for snap in snapshots:
                self.connection.execute(sql, snap.toRecord())

            self.connection.commit()

    def findBySectionAndKey(self, section: str, key: str) -> SettingsSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM settings WHERE section = {placeholder} AND key = {placeholder}"
        cursor = self.connection.execute(sql, [section, key])
        row = cursor.fetchone()

        if row:
            return SettingsSnapshot.fromRow(row)
        return None