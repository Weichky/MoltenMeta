from dataclasses import dataclass, field
from typing import Literal


@dataclass
class FieldMeta:
    name: str
    label_key: str
    field_type: Literal["text", "number", "fk"] = "text"
    fk_target: str | None = None
    required: bool = False
    default_values: dict = field(default_factory=dict)


ENTITY_TYPES = [
    ("symbols", "Symbol"),
    ("units", "Unit"),
    ("elements", "Element"),
    ("systems", "System"),
    ("system_compositions", "System Composition"),
    ("properties", "Property"),
    ("methods", "Method"),
    ("property_values", "Property Value"),
    ("property_value_conditions", "Property Value Condition"),
    ("meta", "Meta"),
]

ENTITY_FIELDS: dict[str, list[FieldMeta]] = {
    "symbols": [
        FieldMeta("symbol", "Symbol:", "text", required=True),
        FieldMeta("name", "Name:", "text"),
        FieldMeta("category", "Category:", "text"),
    ],
    "units": [
        FieldMeta("symbol_id", "Symbol:", "fk", "symbols", required=True),
    ],
    "elements": [
        FieldMeta("symbol_id", "Symbol:", "fk", "symbols", required=True),
        FieldMeta("atomic_mass", "Atomic Mass:", "number"),
        FieldMeta("melting_point", "Melting Point:", "number"),
        FieldMeta("boiling_point", "Boiling Point:", "number"),
        FieldMeta("liquid_range", "Liquid Range:", "number"),
    ],
    "systems": [
        FieldMeta("label", "Label:", "text", required=True),
        FieldMeta("n_component", "N Component:", "number"),
    ],
    "system_compositions": [
        FieldMeta("system_id", "System:", "fk", "systems", required=True),
        FieldMeta("element_id", "Element:", "fk", "elements", required=True),
        FieldMeta("fraction", "Fraction:", "number", required=True),
    ],
    "properties": [
        FieldMeta("name", "Name:", "text", required=True),
        FieldMeta("symbol_id", "Symbol:", "fk", "symbols", required=True),
        FieldMeta("unit_id", "Unit:", "fk", "units", required=True),
        FieldMeta("category", "Category:", "text"),
    ],
    "methods": [
        FieldMeta("name", "Name:", "text", required=True),
        FieldMeta("type", "Type:", "text"),
        FieldMeta("detail", "Detail:", "text"),
    ],
    "property_values": [
        FieldMeta("system_id", "System:", "fk", "systems", required=True),
        FieldMeta("property_id", "Property:", "fk", "properties", required=True),
        FieldMeta("method_id", "Method:", "fk", "methods"),
        FieldMeta("value", "Value:", "number", required=True),
    ],
    "property_value_conditions": [
        FieldMeta(
            "property_value_id",
            "Property Value:",
            "fk",
            "property_values",
            required=True,
        ),
        FieldMeta("symbol_id", "Symbol:", "fk", "symbols", required=True),
        FieldMeta("unit_id", "Unit:", "fk", "units", required=True),
        FieldMeta("value", "Value:", "number", required=True),
        FieldMeta("name", "Name:", "text"),
    ],
    "meta": [
        FieldMeta(
            "value_id", "Property Value:", "fk", "property_values", required=True
        ),
        FieldMeta("created_by", "Created By:", "text"),
        FieldMeta("source_file", "Source File:", "text"),
    ],
}

FK_DISPLAY_COLUMNS: dict[str, str] = {
    "symbols": "symbol",
    "units": "symbol",
    "elements": "symbol",
    "properties": "name",
    "methods": "name",
    "systems": "label",
    "property_values": "id",
}


def getFkDisplayColumn(table: str) -> str:
    return FK_DISPLAY_COLUMNS.get(table, "name")
