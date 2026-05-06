from dataclasses import dataclass, field
from datetime import datetime

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class PropertyTagSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    property_id: int
    tag: str
    created_at: datetime | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertyTagSnapshot":
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        property_id, tag = cls._getRequired(row, "property_id", "tag")
        instance = cls(
            property_id=property_id,
            tag=tag,
            created_at=created_at,
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "property_id": self.property_id,
            "tag": self.tag,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


__all__ = ["PropertyTagSnapshot"]
