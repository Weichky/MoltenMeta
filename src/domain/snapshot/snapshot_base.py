from abc import ABC, abstractmethod

class SnapshotBase(ABC):
    id: int | None

    @classmethod
    @abstractmethod
    def from_row(cls, row) -> 'SnapshotBase':
        ...
    
    @abstractmethod
    def to_record(self) -> dict:
        ...