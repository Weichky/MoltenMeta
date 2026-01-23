from .snapshot_base import SnapshotBase
from dataclasses import dataclass

@dataclass
class ElementSnapshot(SnapshotBase):
    symbol: str
    atomic_mass: float
    atomic_radius: float
    melting_point: float
    melt_density: float

@dataclass
class SystemSnapshot(SnapshotBase):
    component: str
    n_component: int

@dataclass
class SystemComponentSnapshot(SnapshotBase):
    system_id: int
    element_id: int
    fraction: float

@dataclass
class PropertySnapshot(SnapshotBase):
    name: str
    symbol: str
    unit: str
    category: str

@dataclass
class MethodSnapshot(SnapshotBase):
    name: str
    type: str
    detail: str

@dataclass
class PropertyValueSnapshot(SnapshotBase):
    property_id: int
    system_id: int
    property_id: int
    value: float
    temperature: float
    pressure: float

@dataclass
class MetaSnapshot(SnapshotBase):
    value_id: int
    created_at: 'datetime'
    created_by: str