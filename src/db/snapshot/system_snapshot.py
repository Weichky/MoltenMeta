from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class SystemSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    label: str
    n_component: int | None = None

    @classmethod
    def fromRow(cls, row) -> "SystemSnapshot":
        (label,) = cls._getRequired(row, "label")
        instance = cls(
            label=label,
            n_component=row.get("n_component"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "label": self.label,
            "n_component": self.n_component,
        }


__all__ = ["SystemSnapshot"]
