from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from application.service.module_service import ModuleService


class KohlerDataSourceDiscovery:
    def __init__(
        self,
        module_service: "ModuleService",
        user_db_service: Any,
    ):
        self._ms = module_service
        self._user_db = user_db_service
        self._unified_query = None

    def _getUnifiedQuery(self):
        if self._unified_query is None:
            return None
        return self._unified_query

    def findSources(self, tag: str, elem_1: int, elem_2: int) -> list:
        """
        Discover all available data sources for the given tag and element pair.

        Args:
            tag: Data source tag (e.g., "thermodynamic", "binary_data")
            elem_1: Atomic number of first element
            elem_2: Atomic number of second element

        Returns:
            List of DataSource objects
        """
        from framework.data_source_registry import DataSourceRegistry

        sources = []

        module_sources = DataSourceRegistry.findByTag(tag, self._ms)
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
