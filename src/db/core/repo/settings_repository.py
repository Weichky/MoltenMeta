from db.base_repository import BaseRepository
from domain.snapshot import SettingsSnapshot
from db.db_manager import DatabaseManager
from core.log import LogService

from typing import List


class SettingsRepository(BaseRepository[SettingsSnapshot]):
    def __init__(
        self, log_service: LogService, db_manager: DatabaseManager | None = None
    ):
        super().__init__(log_service, db_manager)

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
            record = snap.toRecord()
            self.connection.execute(sql, list(record.values()))

        self.connection.commit()

    def findBySectionAndKey(self, section: str, key: str) -> SettingsSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM settings WHERE section = {placeholder} AND key = {placeholder}"
        cursor = self.connection.execute(sql, [section, key])
        row = cursor.fetchone()

        if row:
            return SettingsSnapshot.fromRow(row)
        return None
