from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class MethodSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    type: str | None = None
    detail: str | None = None

    @classmethod
    def fromRow(cls, row) -> "MethodSnapshot":
        (name,) = cls._getRequired(row, "name")
        instance = cls(
            name=name,
            type=row.get("type"),
            detail=row.get("detail"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {"name": self.name, "type": self.type, "detail": self.detail}


__all__ = ["MethodSnapshot"]
