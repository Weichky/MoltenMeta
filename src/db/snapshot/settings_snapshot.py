from dataclasses import dataclass, field

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class SettingsSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    section: str
    key: str
    value: str

    @classmethod
    def fromRow(cls, row) -> "SettingsSnapshot":
        section, key, value = cls._getRequired(row, "section", "key", "value")
        instance = cls(section=section, key=key, value=value)
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "section": self.section,
            "key": self.key,
            "value": self.value,
        }


__all__ = ["SettingsSnapshot"]
