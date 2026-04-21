from pathlib import Path
import uuid
import json

from core.log import LogService
from framework.module_manager import ModuleManager
from domain import ComputationCacheSnapshot


class ModuleService:
    def __init__(self, runtime_path: Path, log_service: LogService):
        self._logger = log_service.getLogger(__name__)
        self._manager = ModuleManager(runtime_path, log_service)
        self._computation_cache_repo = None
        self._property_tags_repo = None

    def setRepositories(self, computation_cache_repo, property_tags_repo):
        """Allow repositories to be injected after construction."""
        self._computation_cache_repo = computation_cache_repo
        self._property_tags_repo = property_tags_repo

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

        for value_record in result.get("values", []):
            if dims:
                for dim in dims:
                    if dim in value_record:
                        entry = ComputationCacheSnapshot(
                            run_id=run_id,
                            module_id=module_id,
                            method_name=method_name,
                            value=value_record[dim],
                            unit=units.get(dim, ""),
                            params_json=json.dumps(value_record),
                            parent_run_id=parent_run_id,
                        )
                        self._computation_cache_repo.insert(entry)
            else:
                for key, val in value_record.items():
                    entry = ComputationCacheSnapshot(
                        run_id=run_id,
                        module_id=module_id,
                        method_name=method_name,
                        value=val,
                        unit=units.get(key, ""),
                        params_json=json.dumps(value_record),
                        parent_run_id=parent_run_id,
                    )
                    self._computation_cache_repo.insert(entry)

        # self._logger.debug(
        #     f"Cached {len(result.get('values', []))} results with run_id={run_id}"
        # )
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
