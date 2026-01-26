from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .snapshot_base import SnapshotBase


@dataclass
class SymbolSnapshot(SnapshotBase):
    symbol: str
    name: str
    category: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "SymbolSnapshot":
        instance = cls(
            symbol=row["symbol"],
            name=row["name"],
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


@dataclass
class UnitSnapshot(SnapshotBase):
    symbol: str
    id: Optional[int] = field(default=None, init=False)

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


@dataclass
class ElementSnapshot(SnapshotBase):
    symbol_id: int
    atomic_mass: float
    atomic_radius: float
    melting_point: float
    melt_density: float
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "ElementSnapshot":
        instance = cls(
            symbol_id=row["symbol_id"],
            atomic_mass=row["atomic_mass"],
            atomic_radius=row["atomic_radius"],
            melting_point=row["melting_point"],
            melt_density=row["melt_density"],
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


@dataclass
class SystemSnapshot(SnapshotBase):
    label: str
    n_component: int
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "SystemSnapshot":
        instance = cls(
            label=row["label"],
            n_component=row["n_component"],
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "label": self.label,
            "n_component": self.n_component,
        }


@dataclass
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


@dataclass
class PropertySnapshot(SnapshotBase):
    name: str
    symbol_id: int
    unit_id: int
    category: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

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


@dataclass
class MethodSnapshot(SnapshotBase):
    name: str
    type: Optional[str] = None
    detail: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

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


@dataclass
class ConditionSnapshot(SnapshotBase):
    name: str
    symbol_id: int
    unit_id: int
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "ConditionSnapshot":
        instance = cls(
            name=row["name"],
            symbol_id=row["symbol_id"],
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


@dataclass
class PropertyValueSnapshot(SnapshotBase):
    system_id: int
    property_id: int
    value: float
    method_id: Optional[int] = None
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "PropertyValueSnapshot":
        instance = cls(
            system_id=row["system_id"],
            property_id=row["property_id"],
            value=row["value"],
            method_id=row.get("method_id"),
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "system_id": self.system_id,
            "property_id": self.property_id,
            "value": self.value,
            "method_id": self.method_id,
        }


@dataclass
class PropertyValueConditionSnapshot(SnapshotBase):
    value_id: int
    condition_id: int
    condition_value: float

    @classmethod
    def fromRow(cls, row) -> "PropertyValueConditionSnapshot":
        instance = cls(
            value_id=row["value_id"],
            condition_id=row["condition_id"],
            condition_value=row["value"],
        )
        return instance

    def toRecord(self) -> dict:
        return {
            "value_id": self.value_id,
            "condition_id": self.condition_id,
            "value": self.condition_value,
        }


@dataclass
class MetaSnapshot(SnapshotBase):
    value_id: int
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    source_file: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

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


@dataclass
class SettingSnapshot(SnapshotBase):
    section: str
    key: str
    value: str
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "SettingSnapshot":
        instance = cls(
            section=row["section"],
            key=row["key"],
            value=row["value"],
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "section": self.section,
            "key": self.key,
            "value": self.value,
        }