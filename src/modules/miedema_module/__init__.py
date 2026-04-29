from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from .miedema_module import MiedemaCalc

__all__ = ["MiedemaCalc", "registerDataSources"]


def _createMiedemaSource(module_service):
    from framework.data_source import ModuleDataSource

    config_path = Path(__file__).parent / "config.toml"
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    batch_config = config.get("calculateSingleBatch", {})
    outputs = batch_config.get("outputs", {})
    output_symbol = outputs.get("symbol", ["Delta_H_mix"])[0]

    return ModuleDataSource(
        module_service,
        module_name="miedema_module",
        method_name="calculateSingleBatch",
        output_symbol=output_symbol,
    )


def registerDataSources() -> None:
    """Register data sources provided by this module."""
    from framework.data_source_registry import DataSourceRegistry

    DataSourceRegistry.register("binary_data", _createMiedemaSource)
    DataSourceRegistry.register("thermodynamic", _createMiedemaSource)


registerDataSources()
