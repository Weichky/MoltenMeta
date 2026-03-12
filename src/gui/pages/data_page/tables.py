from domain.snapshot import (
    SymbolSnapshot,
    UnitSnapshot,
    ElementSnapshot,
    SystemSnapshot,
    SystemCompositionSnapshot,
    PropertySnapshot,
    MethodSnapshot,
    PropertyValueSnapshot,
    PropertyValueConditionSnapshot,
    MetaSnapshot,
)

# Mapping from table names to repository property names in UserDbService
TABLE_TO_REPO_PROPERTY: dict[str, str] = {
    "symbols": "_symbol_repo",
    "units": "_unit_repo",
    "elements": "_element_repo",
    "systems": "_system_repo",
    "system_compositions": "_system_composition_repo",
    "properties": "_property_repo",
    "methods": "_method_repo",
    "property_values": "_property_value_repo",
    "property_value_conditions": "_property_value_condition_repo",
    "meta": "_meta_repo",
}

# Mapping from table names to Snapshot classes
TABLE_TO_SNAPSHOT_CLASS: dict[str, type] = {
    "symbols": SymbolSnapshot,
    "units": UnitSnapshot,
    "elements": ElementSnapshot,
    "systems": SystemSnapshot,
    "system_compositions": SystemCompositionSnapshot,
    "properties": PropertySnapshot,
    "methods": MethodSnapshot,
    "property_values": PropertyValueSnapshot,
    "property_value_conditions": PropertyValueConditionSnapshot,
    "meta": MetaSnapshot,
}
