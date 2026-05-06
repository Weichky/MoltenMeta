from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class SymbolSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    symbol: str
    name: str | None = None
    category: str | None = None

    @classmethod
    def fromRow(cls, row) -> "SymbolSnapshot":
        (symbol,) = cls._getRequired(row, "symbol")
        instance = cls(
            symbol=symbol,
            name=row.get("name"),
            category=row.get("category"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "category": self.category,
        }


__all__ = ["SymbolSnapshot"]
