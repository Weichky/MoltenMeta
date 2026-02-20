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
        instance.id = row.get("id")
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
        instance.id = row.get("id")
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
        instance.id = row.get("id")
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
    atomic_radius: float | None = None
    melting_point: float | None = None
    melt_density: float | None = None

    @classmethod
    def fromRow(cls, row) -> "ElementSnapshot":
        instance = cls(
            symbol_id=row["symbol_id"],
            atomic_mass=row.get("atomic_mass"),
            atomic_radius=row.get("atomic_radius"),
            melting_point=row.get("melting_point"),
            melt_density=row.get("melt_density"),
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "symbol_id": self.symbol_id,
            "atomic_mass": self.atomic_mass,
            "atomic_radius": self.atomic_radius,
            "melting_point": self.melting_point,
            "melt_density": self.melt_density,
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
        instance.id = row.get("id")
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
        instance.id = row.get("id")
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
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {"name": self.name, "type": self.type, "detail": self.detail}


@dataclass(frozen=True)
class ConditionSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    name: str
    symbol_id: int | None = None
    unit_id: int

    @classmethod
    def fromRow(cls, row) -> "ConditionSnapshot":
        instance = cls(
            name=row["name"],
            symbol_id=row.get("symbol_id"),
            unit_id=row["unit_id"],
        )
        instance.id = row.get("id")
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
    method_id: int | None = None
    value: float

    @classmethod
    def fromRow(cls, row) -> "PropertyValueSnapshot":
        instance = cls(
            system_id=row["system_id"],
            property_id=row["property_id"],
            method_id=row.get("method_id"),
            value=row["value"],
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "system_id": self.system_id,
            "property_id": self.property_id,
            "method_id": self.method_id,
            "value": self.value,
        }


@dataclass(frozen=True)
class PropertyValueConditionSnapshot(SnapshotBase):
    value_id: int
    condition_id: int
    value: float

    @classmethod
    def fromRow(cls, row) -> "PropertyValueConditionSnapshot":
        instance = cls(
            value_id=row["value_id"],
            condition_id=row["condition_id"],
            value=row["value"],
        )
        return instance

    def toRecord(self) -> dict:
        return {
            "value_id": self.value_id,
            "condition_id": self.condition_id,
            "value": self.value,
        }


@dataclass(frozen=True)
class MetaSnapshot(SnapshotBase):
    id: int | None = field(default=None, init=False)
    value_id: int
    created_at: datetime | None = None
    created_by: str | None = None
    source_file: str | None = None

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
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "value_id": self.value_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "source_file": self.source_file,
        }