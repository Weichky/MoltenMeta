from .toop_module import ToopCalc
from .data_source_discovery import ToopDataSourceDiscovery

__all__ = ["ToopCalc", "ToopDataSourceDiscovery", "registerDataSources"]


def registerDataSources() -> None:
    """Register data sources provided by this module."""
    pass


registerDataSources()
