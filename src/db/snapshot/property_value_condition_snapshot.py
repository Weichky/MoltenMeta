from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class PropertyValueConditionSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    property_value_id: int
    symbol_id: int
    unit_id: int
    value: float
    name: str | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertyValueConditionSnapshot":
        property_value_id, symbol_id, unit_id, value = cls._getRequired(
            row, "property_value_id", "symbol_id", "unit_id", "value"
        )
        instance = cls(
            property_value_id=property_value_id,
            symbol_id=symbol_id,
            unit_id=unit_id,
            value=value,
            name=row.get("name"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "property_value_id": self.property_value_id,
            "symbol_id": self.symbol_id,
            "unit_id": self.unit_id,
            "value": self.value,
            "name": self.name,
        }


__all__ = ["PropertyValueConditionSnapshot"]
