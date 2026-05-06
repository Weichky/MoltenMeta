from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class ElementSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    symbol_id: int
    atomic_mass: float | None = None
    melting_point: float | None = None
    boiling_point: float | None = None
    liquid_range: float | None = None

    @classmethod
    def fromRow(cls, row) -> "ElementSnapshot":
        (symbol_id,) = cls._getRequired(row, "symbol_id")
        instance = cls(
            symbol_id=symbol_id,
            atomic_mass=row.get("atomic_mass"),
            melting_point=row.get("melting_point"),
            boiling_point=row.get("boiling_point"),
            liquid_range=row.get("liquid_range"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "symbol_id": self.symbol_id,
            "atomic_mass": self.atomic_mass,
            "melting_point": self.melting_point,
            "boiling_point": self.boiling_point,
            "liquid_range": self.liquid_range,
        }


__all__ = ["ElementSnapshot"]
