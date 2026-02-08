from .base_repository import BaseRepository
from domain import (
    SettingsSnapshot,
    SymbolSnapshot,
    UnitSnapshot,
    ElementSnapshot,
    SystemSnapshot,
    SystemCompositionSnapshot,
    PropertySnapshot,
    MethodSnapshot,
    ConditionSnapshot,
    PropertyValueSnapshot,
    PropertyValueConditionSnapshot,
    MetaSnapshot,
)
from typing import List, Any
from importlib.resources import files
from pathlib import Path
import tomllib

DEFAULT_SETTINGS_PATH = files("resources.default") / "default_settings.toml"

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

    # TODO: function initialize move to abstract base class
    def initialize(self) -> None:
        with open(DEFAULT_SETTINGS_PATH, "rb") as f:
            config = tomllib.load(f)

        sql = self.dialect.getUpsertSyntax(
                table="settings",
                columns=["section", "key", "value"],
            )

        for section, kv_pairs in config.items():
            for key, value in kv_pairs.items():
                self.connection.execute(sql, [section, key, self._serialize_value(value)])
    
        self.connection.commit()
    def _serialize_value(self, val: Any) -> str:
        if isinstance(val, bool):
            return "true" if val else "false"
        return str(val)
    def findBySectionAndKey(self, section: str, key: str) -> SettingsSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM settings WHERE section = {placeholder} AND key = {placeholder}"
        cursor = self.connection.execute(sql, [section, key])
        row = cursor.fetchone()

        if row:
            return SettingsSnapshot.fromRow(row)
        return None


class ElementRepository(BaseRepository[ElementSnapshot]):
    def getTableName(self) -> str:
        return "elements"

    def getEntityClass(self) -> type[ElementSnapshot]:
        return ElementSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS elements (
            id {dialect.getIntegerType()},
            symbol_id {dialect.getIntegerType()} NOT NULL,
            atomic_mass {dialect.getRealType()},
            atomic_radius {dialect.getRealType()},
            melting_point {dialect.getRealType()},
            melt_density {dialect.getRealType()},
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


class SystemRepository(BaseRepository[SystemSnapshot]):
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


class SystemCompositionRepository(BaseRepository[SystemCompositionSnapshot]):
    def getTableName(self) -> str:
        return "system_composition"

    def getEntityClass(self) -> type[SystemCompositionSnapshot]:
        return SystemCompositionSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS system_composition (
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
        sql = f"SELECT * FROM system_composition WHERE system_id = {placeholder}"
        cursor = self.connection.execute(sql, [system_id])
        rows = cursor.fetchall()
        return [SystemCompositionSnapshot.fromRow(row) for row in rows]


class PropertyRepository(BaseRepository[PropertySnapshot]):
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


class MethodRepository(BaseRepository[MethodSnapshot]):
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


class PropertyValueRepository(BaseRepository[PropertyValueSnapshot]):
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
            FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE,
            FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE RESTRICT,
            FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE SET NULL
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
            # Use INSERT OR REPLACE for SQLite
            placeholders = ", ".join([dialect.getPlaceholder() for _ in columns])
            sql = f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            cursor = self.connection.execute(sql, values)
        else:
            # Use upsert syntax for PostgreSQL
            sql = dialect.getUpsertSyntax(table, columns)
            cursor = self.connection.execute(sql, values)

        self.connection.commit()

        # For MetaRepository, value_id is the primary key
        self._logger.debug(
            f"Inserted/Updated record in {table} with value_id {entity.value_id}"
        )
        return entity.value_id

class SymbolRepository(BaseRepository[SymbolSnapshot]):
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


class UnitRepository(BaseRepository[UnitSnapshot]):
    def getTableName(self) -> str:
        return "units"

    def getEntityClass(self) -> type[UnitSnapshot]:
        return UnitSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS units (
            id {dialect.getAutoincrementType()},
            symbol {dialect.getTextType()} NOT NULL
        )
        """

    def findBySymbol(self, symbol: str) -> UnitSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM units WHERE symbol = {placeholder}"
        cursor = self.connection.execute(sql, [symbol])
        row = cursor.fetchone()

        if row:
            return UnitSnapshot.fromRow(row)
        return None


class ConditionRepository(BaseRepository[ConditionSnapshot]):
    def getTableName(self) -> str:
        return "conditions"

    def getEntityClass(self) -> type[ConditionSnapshot]:
        return ConditionSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS conditions (
            id {dialect.getAutoincrementType()},
            name {dialect.getTextType()} NOT NULL UNIQUE,
            symbol_id {dialect.getIntegerType()},
            unit_id {dialect.getIntegerType()} NOT NULL,
            FOREIGN KEY (symbol_id) REFERENCES symbols(id) ON DELETE RESTRICT,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE RESTRICT
        )
        """

    def findByName(self, name: str) -> ConditionSnapshot | None:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM conditions WHERE name = {placeholder}"
        cursor = self.connection.execute(sql, [name])
        row = cursor.fetchone()

        if row:
            return ConditionSnapshot.fromRow(row)
        return None


class PropertyValueConditionRepository(BaseRepository[PropertyValueConditionSnapshot]):
    def getTableName(self) -> str:
        return "property_value_conditions"

    def getEntityClass(self) -> type[PropertyValueConditionSnapshot]:
        return PropertyValueConditionSnapshot

    def _getCreateTableSql(self) -> str:
        dialect = self.dialect
        return f"""
        CREATE TABLE IF NOT EXISTS property_value_conditions (
            value_id {dialect.getIntegerType()} NOT NULL,
            condition_id {dialect.getIntegerType()} NOT NULL,
            value {dialect.getRealType()} NOT NULL,
            PRIMARY KEY (value_id, condition_id),
            FOREIGN KEY (value_id) REFERENCES property_values(id) ON DELETE CASCADE,
            FOREIGN KEY (condition_id) REFERENCES conditions(id) ON DELETE RESTRICT
        )
        """

    def findByValueId(self, value_id: int) -> List[PropertyValueConditionSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_value_conditions WHERE value_id = {placeholder}"
        cursor = self.connection.execute(sql, [value_id])
        rows = cursor.fetchall()
        return [PropertyValueConditionSnapshot.fromRow(row) for row in rows]

    def findByConditionId(
        self, condition_id: int
    ) -> List[PropertyValueConditionSnapshot]:
        placeholder = self.dialect.getPlaceholder()
        sql = f"SELECT * FROM property_value_conditions WHERE condition_id = {placeholder}"
        cursor = self.connection.execute(sql, [condition_id])
        rows = cursor.fetchall()
        return [PropertyValueConditionSnapshot.fromRow(row) for row in rows]
