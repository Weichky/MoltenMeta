from .kohler_module import KohlerCalc

__all__ = ["KohlerCalc", "registerDataSources"]


def registerDataSources() -> None:
    """Register data sources provided by this module."""
    pass


registerDataSources()
