from dataclasses import dataclass, field
from datetime import datetime

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class DataGroupSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    priority: int = 0
    created_at: datetime | None = None

    @classmethod
    def fromRow(cls, row) -> "DataGroupSnapshot":
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        (name,) = cls._getRequired(row, "name")
        instance = cls(
            name=name,
            priority=row.get("priority") or 0,
            created_at=created_at,
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "name": self.name,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


__all__ = ["DataGroupSnapshot"]
