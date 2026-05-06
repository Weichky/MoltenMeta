from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class UnitSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    symbol: str

    @classmethod
    def fromRow(cls, row) -> "UnitSnapshot":
        (symbol,) = cls._getRequired(row, "symbol")
        instance = cls(symbol=symbol)
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "symbol": self.symbol,
        }


__all__ = ["UnitSnapshot"]
