from dataclasses import dataclass, field
from datetime import datetime
from .snapshot_base import SnapshotBase


@dataclass(frozen=True)
class SettingsSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    section: str
    key: str
    value: str

    @classmethod
    def fromRow(cls, row) -> "SettingsSnapshot":
        instance = cls(section=row["section"], key=row["key"], value=row["value"])
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "section": self.section,
            "key": self.key,
            "value": self.value,
        }


@dataclass(frozen=True)
class SymbolSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    symbol: str
    name: str | None = None
    category: str | None = None

    @classmethod
    def fromRow(cls, row) -> "SymbolSnapshot":
        instance = cls(
            symbol=row["symbol"],
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


@dataclass(frozen=True)
class UnitSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    symbol: str

    @classmethod
    def fromRow(cls, row) -> "UnitSnapshot":
        instance = cls(
            symbol=row["symbol"],
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "symbol": self.symbol,
        }


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
        instance = cls(
            symbol_id=row["symbol_id"],
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


@dataclass(frozen=True)
class SystemSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    label: str
    n_component: int | None = None

    @classmethod
    def fromRow(cls, row) -> "SystemSnapshot":
        instance = cls(
            label=row["label"],
            n_component=row.get("n_component"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "label": self.label,
            "n_component": self.n_component,
        }


@dataclass(frozen=True)
class SystemCompositionSnapshot(SnapshotBase):
    system_id: int
    element_id: int
    fraction: float

    @classmethod
    def fromRow(cls, row) -> "SystemCompositionSnapshot":
        instance = cls(
            system_id=row["system_id"],
            element_id=row["element_id"],
            fraction=row["fraction"],
        )
        return instance

    def toRecord(self) -> dict:
        return {
            "system_id": self.system_id,
            "element_id": self.element_id,
            "fraction": self.fraction,
        }


@dataclass(frozen=True)
class PropertySnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    symbol_id: int
    unit_id: int
    category: str | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertySnapshot":
        instance = cls(
            name=row["name"],
            symbol_id=row["symbol_id"],
            unit_id=row["unit_id"],
            category=row.get("category"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "name": self.name,
            "symbol_id": self.symbol_id,
            "unit_id": self.unit_id,
            "category": self.category,
        }


@dataclass(frozen=True)
class MethodSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    type: str | None = None
    detail: str | None = None

    @classmethod
    def fromRow(cls, row) -> "MethodSnapshot":
        instance = cls(
            name=row["name"],
            type=row.get("type"),
            detail=row.get("detail"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {"name": self.name, "type": self.type, "detail": self.detail}


@dataclass(frozen=True)
class ConditionSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    unit_id: int
    symbol_id: int | None = None

    @classmethod
    def fromRow(cls, row) -> "ConditionSnapshot":
        instance = cls(
            name=row["name"],
            symbol_id=row.get("symbol_id"),
            unit_id=row["unit_id"],
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "name": self.name,
            "symbol_id": self.symbol_id,
            "unit_id": self.unit_id,
        }


@dataclass(frozen=True)
class PropertyValueSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    system_id: int
    property_id: int
    value: float
    method_id: int | None = None
    group_id: int | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertyValueSnapshot":
        instance = cls(
            system_id=row["system_id"],
            property_id=row["property_id"],
            method_id=row.get("method_id"),
            value=row["value"],
            group_id=row.get("group_id"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "system_id": self.system_id,
            "property_id": self.property_id,
            "method_id": self.method_id,
            "value": self.value,
            "group_id": self.group_id,
        }


@dataclass(frozen=True)
class PropertyValueConditionSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    property_value_id: int
    symbol_id: int
    unit_id: int
    value: float
    name: str | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertyValueConditionSnapshot":
        instance = cls(
            property_value_id=row["property_value_id"],
            symbol_id=row["symbol_id"],
            unit_id=row["unit_id"],
            value=row["value"],
            name=row.get("name"),
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "property_value_id": self.property_value_id,
            "symbol_id": self.symbol_id,
            "unit_id": self.unit_id,
            "value": self.value,
            "name": self.name,
        }


@dataclass(frozen=True)
class MetaSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    value_id: int
    created_at: datetime | None = None
    created_by: str | None = None
    source_file: str | None = None
    source_type: str = "imported"

    @classmethod
    def fromRow(cls, row) -> "MetaSnapshot":
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            from datetime import datetime

            created_at = datetime.fromisoformat(created_at)

        instance = cls(
            value_id=row["value_id"],
            created_at=created_at,
            created_by=row.get("created_by"),
            source_file=row.get("source_file"),
            source_type=row.get("source_type") or "imported",
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "value_id": self.value_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "source_file": self.source_file,
            "source_type": self.source_type,
        }


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
            from datetime import datetime

            created_at = datetime.fromisoformat(created_at)

        instance = cls(
            run_id=row["run_id"],
            module_id=row["module_id"],
            method_name=row["method_name"],
            value=row["value"],
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


@dataclass(frozen=True)
class PropertyTagSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    property_id: int
    tag: str
    created_at: datetime | None = None

    @classmethod
    def fromRow(cls, row) -> "PropertyTagSnapshot":
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            from datetime import datetime

            created_at = datetime.fromisoformat(created_at)

        instance = cls(
            property_id=row["property_id"],
            tag=row["tag"],
            created_at=created_at,
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "property_id": self.property_id,
            "tag": self.tag,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass(frozen=True)
class DataGroupSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    priority: int = 0
    created_at: datetime | None = None

    @classmethod
    def fromRow(cls, row) -> "DataGroupSnapshot":
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            from datetime import datetime

            created_at = datetime.fromisoformat(created_at)

        instance = cls(
            name=row["name"],
            priority=row.get("priority") or 0,
            created_at=created_at,
        )
        object.__setattr__(instance, "id", row.get("id"))
        return instance

    def toRecord(self) -> dict:
        return {
            "name": self.name,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
