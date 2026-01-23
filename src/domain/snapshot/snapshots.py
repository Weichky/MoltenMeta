from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .snapshot_base import SnapshotBase


@dataclass
class ElementSnapshot(SnapshotBase):
    symbol: str = ""
    atomic_mass: Optional[float] = None
    atomic_radius: Optional[float] = None
    melting_point: Optional[float] = None
    melt_density: Optional[float] = None
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "ElementSnapshot":
        instance = cls(
            symbol=row.get("symbol", ""),
            atomic_mass=row.get("atomic_mass"),
            atomic_radius=row.get("atomic_radius"),
            melting_point=row.get("melting_point"),
            melt_density=row.get("melt_density"),
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "symbol": self.symbol,
            "atomic_mass": self.atomic_mass,
            "atomic_radius": self.atomic_radius,
            "melting_point": self.melting_point,
            "melt_density": self.melt_density,
        }


@dataclass
class SystemSnapshot(SnapshotBase):
    component: str = ""
    n_component: int = 0
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "SystemSnapshot":
        instance = cls(
            component=row.get("component", ""),
            n_component=row.get("n_component", 0),
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {"component": self.component, "n_component": self.n_component}


@dataclass
class SystemCompositionSnapshot(SnapshotBase):
    system_id: int = 0
    element_id: int = 0
    fraction: float = 0.0

    @classmethod
    def fromRow(cls, row) -> "SystemCompositionSnapshot":
        instance = cls(
            system_id=row.get("system_id", 0),
            element_id=row.get("element_id", 0),
            fraction=row.get("fraction", 0.0),
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
    name: str = ""
    symbol: str = ""
    unit: str = ""
    category: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "PropertySnapshot":
        instance = cls(
            name=row.get("name", ""),
            symbol=row.get("symbol", ""),
            unit=row.get("unit", ""),
            category=row.get("category"),
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "unit": self.unit,
            "category": self.category,
        }


@dataclass
class MethodSnapshot(SnapshotBase):
    name: str = ""
    type: Optional[str] = None
    detail: Optional[str] = None
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "MethodSnapshot":
        instance = cls(
            name=row.get("name", ""),
            type=row.get("type"),
            detail=row.get("detail"),
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {"name": self.name, "type": self.type, "detail": self.detail}


@dataclass
class PropertyValueSnapshot(SnapshotBase):
    system_id: int = 0
    property_id: int = 0
    method_id: Optional[int] = None
    value: float = 0.0
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    id: Optional[int] = field(default=None, init=False)

    @classmethod
    def fromRow(cls, row) -> "PropertyValueSnapshot":
        instance = cls(
            system_id=row.get("system_id", 0),
            property_id=row.get("property_id", 0),
            method_id=row.get("method_id"),
            value=row.get("value", 0.0),
            temperature=row.get("temperature"),
            pressure=row.get("pressure"),
        )
        instance.id = row.get("id")
        return instance

    def toRecord(self) -> dict:
        return {
            "system_id": self.system_id,
            "property_id": self.property_id,
            "method_id": self.method_id,
            "value": self.value,
            "temperature": self.temperature,
            "pressure": self.pressure,
        }


@dataclass
class MetaSnapshot(SnapshotBase):
    value_id: int = 0
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
            value_id=row.get("value_id", 0),
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
