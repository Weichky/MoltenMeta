from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class PropertySnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    symbol_id: int
    unit_id: int
    category: str | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertySnapshot":
        name, symbol_id, unit_id = cls._getRequired(row, "name", "symbol_id", "unit_id")
        instance = cls(
            name=name,
            symbol_id=symbol_id,
            unit_id=unit_id,
            category=row.get("category"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "name": self.name,
            "symbol_id": self.symbol_id,
            "unit_id": self.unit_id,
            "category": self.category,
        }


__all__ = ["PropertySnapshot"]
