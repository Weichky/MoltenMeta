from dataclasses import dataclass

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class SystemCompositionSnapshot(SnapshotBase):
    system_id: int
    element_id: int
    fraction: float

    @classmethod
    def fromRow(cls, row) -> "SystemCompositionSnapshot":
        system_id, element_id, fraction = cls._getRequired(
            row, "system_id", "element_id", "fraction"
        )
        instance = cls(
            system_id=system_id,
            element_id=element_id,
            fraction=fraction,
        )
        return instance

    def toRecord(self) -> dict:
        return {
            "system_id": self.system_id,
            "element_id": self.element_id,
            "fraction": self.fraction,
        }


__all__ = ["SystemCompositionSnapshot"]
