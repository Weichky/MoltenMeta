from .toop_module import ToopCalc
from .data_source_registry import DataSourceRegistry
from .data_source import ModuleDataSource
from .data_source_discovery import ToopDataSourceDiscovery

__all__ = ["ToopCalc", "ToopDataSourceDiscovery", "register_data_sources"]


def _create_miedema_source(module_service) -> ModuleDataSource:
    """Factory function for Miedema module data source."""
    return ModuleDataSource(
        module_service,
        module_name="miedema_module",
        method_name="calculateSingleBatch",
        output_symbol="Delta_H_mix",
    )


def register_data_sources() -> None:
    """Register all data sources provided by this module."""
    DataSourceRegistry.register("binary_data", _create_miedema_source)
    DataSourceRegistry.register("thermodynamic", _create_miedema_source)


register_data_sources()
