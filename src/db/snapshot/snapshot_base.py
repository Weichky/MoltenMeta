from abc import ABC, abstractmethod


class SnapshotBase(ABC):
    id: int | None

    @classmethod
    @abstractmethod
    def fromRow(cls, row) -> "SnapshotBase": ...

    @abstractmethod
    def toRecord(self) -> dict: ...

    @classmethod
    def _getRequired(cls, row: dict, *keys: str) -> tuple:
        missing = [k for k in keys if k not in row]
        if missing:
            raise ValueError(
                f"fromRow: missing required field(s) {missing} in row with keys {list(row.keys())}"
            )
        return tuple(row[k] for k in keys)
