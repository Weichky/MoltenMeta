from abc import ABC, abstractmethod

class SnapshotBase(ABC):
    id: int | None

    @classmethod
    @abstractmethod
    def fromRow(cls, row) -> 'SnapshotBase':
        ...
    
    @abstractmethod
    def toRecord(self) -> dict:
        ...