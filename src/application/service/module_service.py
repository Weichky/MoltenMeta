from pathlib import Path
import uuid
import json

from core.log import LogService
from framework.module_manager import ModuleManager
from domain import ComputationCacheSnapshot, SymbolSnapshot


class ModuleService:
    def __init__(self, runtime_path: Path, log_service: LogService):
        self._logger = log_service.getLogger(__name__)
        self._manager = ModuleManager(runtime_path, log_service)
        self._computation_cache_repo = None
        self._property_tags_repo = None
        self._symbols_repo = None
        self._units_repo = None
        self._properties_repo = None
        self._symbol_to_property_id: dict[str, int] = {}

    def setRepositories(
        self,
        computation_cache_repo,
        property_tags_repo,
        symbols_repo=None,
        units_repo=None,
        properties_repo=None,
    ):
        """Allow repositories to be injected after construction."""
        self._computation_cache_repo = computation_cache_repo
        self._property_tags_repo = property_tags_repo
        self._symbols_repo = symbols_repo
        self._units_repo = units_repo
        self._properties_repo = properties_repo

    def getModule(self, package_name: str) -> object:
        try:
            return self._manager.get(package_name)
        except KeyError:
            self._logger.error(f"Module not found: {package_name}")
            raise

    def listModules(self) -> list[dict]:
        return self._manager.list()

    def getMethods(self, package_name: str) -> list[str]:
        try:
            return self._manager.getMethods(package_name)
        except KeyError:
            self._logger.error(f"Module not found: {package_name}")
            raise

    def callMethod(self, package_name: str, method_name: str, **kwargs) -> dict:
        """Invoke a method on a module with caching support."""
        module = self.getModule(package_name)
        method = getattr(module, method_name, None)
        if method is None:
            raise AttributeError(
                f"Module {package_name} does not have method {method_name}"
            )

        skip_cache = kwargs.pop("_skip_cache", False)

        result = method(**kwargs)

        if skip_cache:
            return result

        if self._computation_cache_repo:
            run_id = self._cacheResult(package_name, method_name, result, kwargs)
            result["_run_id"] = run_id

        return result

    def cacheResult(
        self, module_id: str, method_name: str, result: dict, **kwargs
    ) -> str:
        """Cache a pre-computed result. Useful for module methods called outside callMethod."""
        if not self._computation_cache_repo:
            return ""
        run_id = self._cacheResult(module_id, method_name, result, kwargs)
        result["_run_id"] = run_id
        return run_id

    def getModuleConfig(self, package_name: str) -> dict | None:
        return self._manager.getModuleConfig(package_name)

    def _cacheResult(
        self, module_id: str, method_name: str, result: dict, kwargs: dict
    ) -> str:
        """Persist computation result to cache with dimension-aware snapshot creation."""
        run_id = str(uuid.uuid4())
        parent_run_id = kwargs.get("_parent_run_id")

        dims = result.get("dims", [])
        units = result.get("units", {})
        main_dim = result.get("main_dim")
        values = result.get("values", [])
        entries: list[ComputationCacheSnapshot] = []

        if main_dim and dims:
            condition_dims = [d for d in dims if d != main_dim]
            property_id = self.getPropertyIdBySymbol(main_dim)
            for value_record in values:
                if not isinstance(value_record, dict) or main_dim not in value_record:
                    continue
                val = value_record[main_dim]
                if val is None:
                    continue
                params = {
                    c: value_record[c] for c in condition_dims if c in value_record
                }
                entry = ComputationCacheSnapshot(
                    run_id=run_id,
                    module_id=module_id,
                    method_name=method_name,
                    value=float(val),
                    unit=units.get(main_dim, ""),
                    params_json=json.dumps(params) if params else None,
                    parent_run_id=parent_run_id,
                    property_id=property_id,
                )
                entries.append(entry)
        elif dims:
            for value_record in values:
                if not isinstance(value_record, dict):
                    continue
                for dim in dims:
                    if dim in value_record:
                        val = value_record[dim]
                        if val is None:
                            continue
                        entry = ComputationCacheSnapshot(
                            run_id=run_id,
                            module_id=module_id,
                            method_name=method_name,
                            value=float(val),
                            unit=units.get(dim, ""),
                            params_json=json.dumps(value_record),
                            parent_run_id=parent_run_id,
                        )
                        entries.append(entry)
        else:
            if values and isinstance(values[0], (int, float)):
                entry = ComputationCacheSnapshot(
                    run_id=run_id,
                    module_id=module_id,
                    method_name=method_name,
                    value=float("nan"),
                    unit=units.get(list(units.keys())[0], "") if units else "",
                    params_json=json.dumps({"raw_values": values}),
                    parent_run_id=parent_run_id,
                )
                entries.append(entry)

        if entries:
            self._computation_cache_repo.insertBatch(entries)

        return run_id

    def registerModuleTags(self, package_name: str):
        """Extract tags from module config outputs and register them for symbol-based lookup."""
        if not self._property_tags_repo:
            return

        config = self._manager.getModuleConfig(package_name)
        if not config:
            return

        for method_name in config.get("all_methods", []):
            method_config = config.get(method_name, {})
            outputs = method_config.get("outputs", {})
            tags = outputs.get("tags", [])
            for symbol in outputs.get("symbol", []):
                if tags:
                    self._property_tags_repo.addTags(symbol, tags)

    def findMethodsByTag(self, tag: str) -> list[tuple[str, str]]:
        """
        Find all module methods that have the specified tag in their outputs.

        Args:
            tag: The tag to search for

        Returns:
            List of (package_name, method_name) tuples
        """
        results = []
        for module_info in self._manager.list():
            package_name = module_info.get("package_name")
            if not package_name:
                continue

            config = self._manager.getModuleConfig(package_name)
            if not config:
                continue

            module_cfg = config.get("module", {})
            for method_name in module_cfg.get("all_methods", []):
                method_config = config.get(method_name, {})
                outputs = method_config.get("outputs", {})
                tags = outputs.get("tags", [])
                if tag in tags:
                    results.append((package_name, method_name))

        return results

    def registerModuleProperties(self, package_name: str) -> None:
        """Register module output properties in the database, creating symbols and units as needed."""
        if not all([self._symbols_repo, self._units_repo, self._properties_repo]):
            self._logger.debug(
                "Property registration skipped: repos not fully initialized"
            )
            return

        config = self._manager.getModuleConfig(package_name)
        if not config:
            return

        module_cfg = config.get("module", {})
        for method_name in module_cfg.get("all_methods", []):
            method_config = config.get(method_name, {})
            outputs = method_config.get("outputs", {})

            if outputs.get("is_virtual"):
                continue

            output_symbols = outputs.get("symbol", [])
            output_units = outputs.get("unit", {})
            for symbol in output_symbols:
                prop = self._properties_repo.findByName(symbol)
                if prop is not None:
                    self._symbol_to_property_id[symbol] = prop.id
                    continue

                prop_symbol = self._symbols_repo.findBySymbol(symbol)
                if prop_symbol is None:
                    prop_symbol = SymbolSnapshot(
                        symbol=symbol, name=symbol, category="property"
                    )
                    self._symbols_repo.upsert([prop_symbol])
                    prop_symbol = self._symbols_repo.findBySymbol(symbol)

                unit_str = output_units.get(symbol, "")
                unit_symbol = None
                unit_id = None
                if unit_str:
                    unit_symbol = self._symbols_repo.findBySymbol(unit_str)
                    if unit_symbol is None:
                        unit_symbol = SymbolSnapshot(symbol=unit_str, category="unit")
                        self._symbols_repo.upsert([unit_symbol])
                        unit_symbol = self._symbols_repo.findBySymbol(unit_str)
                    if unit_symbol:
                        unit_id = self._units_repo.upsertBySymbolId(unit_symbol.id)

                from domain import PropertySnapshot

                new_prop = PropertySnapshot(
                    name=symbol,
                    symbol_id=prop_symbol.id,
                    unit_id=unit_id or 0,
                    category=module_cfg.get("category"),
                )
                new_id = self._properties_repo.upsert(new_prop)
                self._symbol_to_property_id[symbol] = new_id
                self._logger.debug(f"Registered property: {symbol} (id={new_id})")

    def registerAllModulesProperties(self) -> None:
        """Register properties for all discovered modules."""
        for module_info in self._manager.list():
            package_name = module_info.get("package_name")
            if package_name:
                self.registerModuleProperties(package_name)

    def getPropertyIdBySymbol(self, symbol: str) -> int | None:
        """Look up a property_id by its symbol name."""
        return self._symbol_to_property_id.get(symbol)
