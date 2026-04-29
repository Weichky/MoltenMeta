"""
Data source discovery for geometric model modules.

Provides a generic discovery mechanism that can be used by all geometric models
(Toop, Kohler, etc.) without requiring module-specific implementations.

Architecture Note:
    This is a shared, non-registered module. Other modules import from it:
    - toop_module.data_source_discovery: imports BinaryDataSourceDiscovery as ToopDataSourceDiscovery
    - kohler_module.data_source_discovery: imports BinaryDataSourceDiscovery as KohlerDataSourceDiscovery

Usage:
    from ..geometric_model_core.data_source_discovery import BinaryDataSourceDiscovery
    ToopDataSourceDiscovery = BinaryDataSourceDiscovery
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from application.service.module_service import ModuleService


class BinaryDataSourceDiscovery:
    def __init__(
        self,
        module_service: "ModuleService",
        user_db_service: Any,
        registry: Any,
    ):
        self._ms = module_service
        self._user_db = user_db_service
        self._registry = registry

    def findSources(self, tag: str, elem_1: int, elem_2: int) -> list:
        sources = []

        module_sources = self._registry.findByTag(tag, self._ms)
        sources.extend(module_sources)

        db_sources = self._findDbSources(tag, elem_1, elem_2)
        sources.extend(db_sources)

        return sources

    def _findDbSources(self, tag: str, elem_1: int, elem_2: int) -> list:
        """
        Find database records matching the tag and element pair.

        Args:
            tag: Data source tag
            elem_1: Atomic number of first element
            elem_2: Atomic number of second element

        Returns:
            List of DatabaseDataSource objects
        """
        return []


__all__ = ["BinaryDataSourceDiscovery"]
