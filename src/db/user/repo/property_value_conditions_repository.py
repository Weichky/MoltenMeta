from db.base_repository import BaseRepository
from db.snapshot import PropertyValueConditionSnapshot


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


__all__ = ["PropertyValueConditionsRepository"]
