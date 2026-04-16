from db.base_repository import BaseRepository
from domain import (
    SymbolSnapshot,
    UnitSnapshot,
    ElementSnapshot,
    SystemSnapshot,
    SystemCompositionSnapshot,
    PropertySnapshot,
    MethodSnapshot,
    PropertyValueSnapshot,
    PropertyValueConditionSnapshot,
    MetaSnapshot,
    ComputationCacheSnapshot,
    PropertyTagSnapshot,
    DataGroupSnapshot,
)
from typing import List


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
        placeholders = ", ".join(
            [dialect.getPlaceholder() for _ in items[0].toRecord().keys()]
        )
        sql = f"INSERT OR IGNORE INTO {table} ({', '.join(items[0].toRecord().keys())}) VALUES ({placeholders})"

        for item in items:
            record = item.toRecord()
            self.connection.execute(sql, list(record.values()))

        self.connection.commit()
        return len(items)


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


class PropertyValuesRepository(BaseRepository[PropertyValueSnapshot]):
    def getTableName(self) -> str:
        return "property_values"

    def getEntityClass(self) -> type[PropertyValueSnapshot]:
        return PropertyValueSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS property_values (
            id {dialect.getAutoincrementType()},
            system_id {dialect.getIntegerType()} NOT NULL,
            property_id {dialect.getIntegerType()} NOT NULL,
            method_id {dialect.getIntegerType()},
            value {dialect.getRealType()} NOT NULL,
            group_id {dialect.getIntegerType()},
            FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE,
            FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE RESTRICT,
            FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE SET NULL,
            FOREIGN KEY (group_id) REFERENCES data_groups(id) ON DELETE SET NULL
        )
        """

    def findBySystemId(self, system_id: int) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE system_id = {placeholder}"
        cursor = self.connection.execute(sql, [system_id])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def findByPropertyId(self, property_id: int) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE property_id = {placeholder}"
        cursor = self.connection.execute(sql, [property_id])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def findByGroupId(self, group_id: int) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE group_id = {placeholder}"
        cursor = self.connection.execute(sql, [group_id])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def findByGroupIdPaginated(
        self, group_id: int, limit: int, offset: int
    ) -> List[PropertyValueSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_values WHERE group_id = {placeholder} ORDER BY id LIMIT {placeholder} OFFSET {placeholder}"
        cursor = self.connection.execute(sql, [group_id, limit, offset])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def countByGroupId(self, group_id: int) -> int:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT COUNT(*) as cnt FROM property_values WHERE group_id = {placeholder}"
        cursor = self.connection.execute(sql, [group_id])
        row = cursor.fetchone()
        return row["cnt"] if row else 0

    def findUngroupedPaginated(
        self, limit: int, offset: int
    ) -> List[PropertyValueSnapshot]:
        sql = f"SELECT * FROM property_values WHERE group_id IS NULL ORDER BY id LIMIT {self.dialect.getPlaceholder()} OFFSET {self.dialect.getPlaceholder()}"
        cursor = self.connection.execute(sql, [limit, offset])
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]

    def countUngrouped(self) -> int:
        sql = "SELECT COUNT(*) as cnt FROM property_values WHERE group_id IS NULL"
        cursor = self.connection.execute(sql)
        row = cursor.fetchone()
        return row["cnt"] if row else 0

    def updateGroupIdBatch(self, data_ids: list[int], new_group_id: int | None) -> int:
        if not data_ids:
            return 0
        placeholders = ", ".join([self.dialect.getPlaceholder() for _ in data_ids])
        if new_group_id is None:
            sql = f"UPDATE property_values SET group_id = NULL WHERE id IN ({placeholders})"
        else:
            sql = f"UPDATE property_values SET group_id = {self.dialect.getPlaceholder()} WHERE id IN ({placeholders})"
            data_ids = [new_group_id] + data_ids
        cursor = self.connection.execute(sql, data_ids)
        self.connection.commit()
        return cursor.rowCount

    def findAll(self) -> List[PropertyValueSnapshot]:
        sql = "SELECT * FROM property_values"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()
        return [PropertyValueSnapshot.fromRow(row) for row in rows]


class MetaRepository(BaseRepository[MetaSnapshot]):
    def getTableName(self) -> str:
        return "meta"

    def getEntityClass(self) -> type[MetaSnapshot]:
        return MetaSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS meta (
            value_id {dialect.getIntegerType()} PRIMARY KEY,
            created_at {dialect.getDatetimeType()} DEFAULT CURRENT_TIMESTAMP,
            created_by {dialect.getTextType()},
            source_file {dialect.getTextType()},
            source_type {dialect.getTextType()} DEFAULT 'imported',
            FOREIGN KEY (value_id) REFERENCES property_values(id) ON DELETE CASCADE
        )
        """

    def findByValueId(self, value_id: int) -> List[MetaSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM meta WHERE value_id = {placeholder}"
        cursor = self.connection.execute(sql, [value_id])
        rows = cursor.fetchall()
        return [MetaSnapshot.fromRow(row) for row in rows]

    def insert(self, entity: MetaSnapshot) -> int:
        table = self.getTableName()
        record = entity.toRecord()
        columns = list(record.keys())
        values = list(record.values())

        dialect = self.dialect

        if dialect.supportsInsertOrReplace():
            placeholders = ", ".join([dialect.getPlaceholder() for _ in columns])
            sql = f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            self.connection.execute(sql, values)
        else:
            sql = dialect.getUpsertSyntax(table, columns)
            self.connection.execute(sql, values)

        self.connection.commit()

        # For MetaRepository, value_id is the primary key
        self._logger.debug(
            f"Inserted/Updated record in {table} with value_id {entity.value_id}"
        )
        return entity.value_id


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

        for snap in snapshots:
            record = snap.toRecord()
            self.connection.execute(sql, list(record.values()))

        self.connection.commit()


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


class PropertyValueConditionsRepository(BaseRepository[PropertyValueConditionSnapshot]):
    def getTableName(self) -> str:
        return "property_value_conditions"

    def getEntityClass(self) -> type[PropertyValueConditionSnapshot]:
        return PropertyValueConditionSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS property_value_conditions (
            id {dialect.getAutoincrementType()},
            property_value_id {dialect.getIntegerType()} NOT NULL,
            symbol_id {dialect.getIntegerType()} NOT NULL,
            unit_id {dialect.getIntegerType()} NOT NULL,
            value {dialect.getRealType()} NOT NULL,
            name {dialect.getTextType()},
            FOREIGN KEY (property_value_id) REFERENCES property_values(id) ON DELETE CASCADE,
            FOREIGN KEY (symbol_id) REFERENCES symbols(id) ON DELETE RESTRICT,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE RESTRICT
        )
        """


class ComputationCacheRepository(BaseRepository[ComputationCacheSnapshot]):
    def getTableName(self) -> str:
        return "computation_cache"

    def getEntityClass(self) -> type[ComputationCacheSnapshot]:
        return ComputationCacheSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS computation_cache (
            id {dialect.getAutoincrementType()},
            run_id {dialect.getTextType()} NOT NULL,
            module_id {dialect.getTextType()} NOT NULL,
            method_name {dialect.getTextType()} NOT NULL,
            system_id {dialect.getIntegerType()},
            property_id {dialect.getIntegerType()},
            value {dialect.getRealType()} NOT NULL,
            unit {dialect.getTextType()},
            params_json {dialect.getTextType()},
            parent_run_id {dialect.getTextType()},
            is_deleted {dialect.getIntegerType()} DEFAULT 0,
            group_id {dialect.getIntegerType()},
            created_at {dialect.getDatetimeType()} DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (system_id) REFERENCES systems(id),
            FOREIGN KEY (property_id) REFERENCES properties(id),
            FOREIGN KEY (group_id) REFERENCES data_groups(id) ON DELETE SET NULL
        )
        """

    def _getCreateIndexSql(self) -> List[str]:
        return [
            "CREATE INDEX IF NOT EXISTS idx_cache_run_id ON computation_cache(run_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_module ON computation_cache(module_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_parent ON computation_cache(parent_run_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_property ON computation_cache(property_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_system ON computation_cache(system_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_group ON computation_cache(group_id)",
        ]

    def createTable(self) -> None:
        super().createTable()
        for index_sql in self._getCreateIndexSql():
            self.connection.execute(index_sql)
        self.connection.commit()

    def findByRunId(self, run_id: str) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE run_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [run_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByModuleId(self, module_id: str) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE module_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [module_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByParentRunId(self, parent_run_id: str) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE parent_run_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [parent_run_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByPropertyId(self, property_id: int) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE property_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [property_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findByGroupId(self, group_id: int) -> List[ComputationCacheSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM computation_cache WHERE group_id = {placeholder} AND is_deleted = 0"
        cursor = self.connection.execute(sql, [group_id])
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def findAll(self) -> List[ComputationCacheSnapshot]:
        sql = "SELECT * FROM computation_cache WHERE is_deleted = 0"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()
        return [ComputationCacheSnapshot.fromRow(row) for row in rows]

    def softDeleteByRunId(self, run_id: str) -> int:
        placeholder = self.dialect.getPlaceholder()
        sql = (
            f"UPDATE computation_cache SET is_deleted = 1 WHERE run_id = {placeholder}"
        )
        cursor = self.connection.execute(sql, [run_id])
        self.connection.commit()
        return cursor.rowCount

    def countActive(self) -> int:
        sql = "SELECT COUNT(*) FROM computation_cache WHERE is_deleted = 0"
        cursor = self.connection.execute(sql)
        result = cursor.fetchone()
        return result.get("count") or result.get("COUNT(*)") or 0


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
        total = 0
        for tag in tags:
            total += self.addTag(property_id, tag)
        return total

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


class DataGroupsRepository(BaseRepository[DataGroupSnapshot]):
    def getTableName(self) -> str:
        return "data_groups"

    def getEntityClass(self) -> type[DataGroupSnapshot]:
        return DataGroupSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS data_groups (
            id {dialect.getAutoincrementType()},
            name {dialect.getTextType()} NOT NULL UNIQUE,
            priority {dialect.getIntegerType()} NOT NULL DEFAULT 0,
            created_at {dialect.getDatetimeType()} DEFAULT CURRENT_TIMESTAMP
        )
        """

    def findByName(self, name: str) -> DataGroupSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM data_groups WHERE name = {placeholder}"
        cursor = self.connection.execute(sql, [name])
        row = cursor.fetchone()

        if row:
            return DataGroupSnapshot.fromRow(row)
        return None

    def findAll(self) -> List[DataGroupSnapshot]:
        sql = "SELECT * FROM data_groups ORDER BY priority DESC, created_at DESC"
        cursor = self.connection.execute(sql)
        rows = cursor.fetchall()
        return [DataGroupSnapshot.fromRow(row) for row in rows]
