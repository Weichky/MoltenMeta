from pathlib import Path
import uuid

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
        module = self.getModule(package_name)
        method = getattr(module, method_name, None)
        if method is None:
            raise AttributeError(
                f"Module {package_name} does not have method {method_name}"
            )
        self._logger.debug(f"Calling {package_name}.{method_name} with kwargs={kwargs}")
        result = method(**kwargs)

        if self._computation_cache_repo:
            run_id = self._cacheResult(package_name, method_name, result, kwargs)
            result["_run_id"] = run_id

        return result

    def _cacheResult(
        self, module_id: str, method_name: str, result: dict, kwargs: dict
    ) -> str:
        run_id = str(uuid.uuid4())
        parent_run_id = kwargs.get("_parent_run_id")

        for value_record in result.get("values", []):
            # FIXME: This assumes the last key is the output variable name.
            # Better approach: read output symbol from module config explicitly.
            # See issue: #weakness-value-extraction
            numeric_key = list(value_record.keys())[-1]
            entry = ComputationCacheSnapshot(
                run_id=run_id,
                module_id=module_id,
                method_name=method_name,
                value=value_record[numeric_key],
                unit=result.get("unit", {}).get("value", ""),
                params_json=None,
                parent_run_id=parent_run_id,
            )
            self._computation_cache_repo.insert(entry)

        self._logger.debug(
            f"Cached {len(result.get('values', []))} results with run_id={run_id}"
        )
        return run_id

    def registerModuleTags(self, package_name: str):
        """Register tags from module config."""
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
