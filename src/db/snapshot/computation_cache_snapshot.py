from dataclasses import dataclass, field
from datetime import datetime

from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class ComputationCacheSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    run_id: str
    module_id: str
    method_name: str
    value: float
    system_id: int | None = None
    property_id: int | None = None
    unit: str | None = None
    params_json: str | None = None
    parent_run_id: str | None = None
    is_deleted: int = 0
    group_id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def fromRow(cls, row) -> "ComputationCacheSnapshot":
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        run_id, module_id, method_name, value = cls._getRequired(
            row, "run_id", "module_id", "method_name", "value"
        )
        instance = cls(
            run_id=run_id,
            module_id=module_id,
            method_name=method_name,
            value=value,
            system_id=row.get("system_id"),
            property_id=row.get("property_id"),
            unit=row.get("unit"),
            params_json=row.get("params_json"),
            parent_run_id=row.get("parent_run_id"),
            is_deleted=row.get("is_deleted") or 0,
            group_id=row.get("group_id"),
            created_at=created_at,
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "run_id": self.run_id,
            "module_id": self.module_id,
            "method_name": self.method_name,
            "value": self.value,
            "system_id": self.system_id,
            "property_id": self.property_id,
            "unit": self.unit,
            "params_json": self.params_json,
            "parent_run_id": self.parent_run_id,
            "is_deleted": self.is_deleted,
            "group_id": self.group_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


__all__ = ["ComputationCacheSnapshot"]
