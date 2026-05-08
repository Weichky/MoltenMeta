from dataclasses import dataclass, field
from datetime import datetime

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class MetaSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    value_id: int
    created_at: datetime | None = None
    created_by: str | None = None
    source_file: str | None = None
    source_type: str = "imported"

    @classmethod
    def fromRow(cls, row) -> "MetaSnapshot":
        (value_id,) = cls._getRequired(row, "value_id")
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        instance = cls(
            value_id=value_id,
            created_at=created_at,
            created_by=row.get("created_by"),
            source_file=row.get("source_file"),
            source_type=row.get("source_type") or "imported",
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "value_id": self.value_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "source_file": self.source_file,
            "source_type": self.source_type,
        }


__all__ = ["MetaSnapshot"]
