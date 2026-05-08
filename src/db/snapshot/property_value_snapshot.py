from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class PropertyValueSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    system_id: int
    property_id: int
    value: float
    method_id: int | None = None
    group_id: int | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertyValueSnapshot":
        system_id, property_id, value = cls._getRequired(
            row, "system_id", "property_id", "value"
        )
        instance = cls(
            system_id=system_id,
            property_id=property_id,
            method_id=row.get("method_id"),
            value=value,
            group_id=row.get("group_id"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "system_id": self.system_id,
            "property_id": self.property_id,
            "method_id": self.method_id,
            "value": self.value,
            "group_id": self.group_id,
        }


__all__ = ["PropertyValueSnapshot"]
