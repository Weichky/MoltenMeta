import importlib
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from core.log import LogService


class ModuleManager:
    def __init__(self, runtime_path: Path, log_service: LogService, data_source_registry):
        """
        Initializes the Module Manager.
        :param runtime_path: Absolute path to the runtime directory.
        :param log_service: Service used to create the logger.
        :param data_source_registry: DataSourceRegistry instance for module data sources.
        """
        self._logger = log_service.getLogger(__name__)
        self._modules: dict[str, object] = {}
        self._module_infos: dict[str, dict] = {}
        self._runtime_path = runtime_path
        self._data_source_registry = data_source_registry

        self._ensureRuntimeInPath()
        self._discover(runtime_path / "modules")

    def _ensureRuntimeInPath(self) -> None:
        runtime_parent = str(self._runtime_path)
        if runtime_parent not in sys.path:
            sys.path.insert(0, runtime_parent)

    def _discover(self, modules_dir: Path) -> None:
        """
        Scans the modules directory, loads config.toml, and dynamically 
        instantiates module entry classes using physical file paths.
        """
        if not modules_dir.exists():
            self._logger.warning(f"Modules directory does not exist: {modules_dir}")
            return

        for subdir in modules_dir.iterdir():
            if not subdir.is_dir():
                continue

            config_path = subdir / "config.toml"
            if not config_path.exists():
                self._logger.debug(f"No config.toml found in {subdir}, skipping")
                continue

            try:
                with open(config_path, "rb") as f:
                    config = tomllib.load(f)
            except Exception as e:
                self._logger.error(f"Failed to load config.toml from {subdir}: {e}")
                continue

            package_name = config["module"]["package_name"]
            entry_class = config["module"]["entry_class"]

            try:
                mod = importlib.import_module(f"modules.{package_name}")

                # Instantiate the entry class
                cls = getattr(mod, entry_class)
                instance = cls()

                self._modules[package_name] = instance
                self._module_infos[package_name] = config

                self._logger.info(f"Loaded module: {package_name} ({entry_class})")

                register_func = getattr(mod, "registerDataSources", None)
                if register_func is not None:
                    register_func(self._data_source_registry)
            except Exception as e:
                self._logger.error(f"Failed to load module {package_name}: {e}")

    def get(self, package_name: str) -> object:
        """Returns the instantiated module object by its package name."""
        if package_name not in self._modules:
            raise KeyError(f"Module not found: {package_name}")
        return self._modules[package_name]

    def listModules(self) -> list[dict]:
        """Returns a list of all loaded modules with their metadata."""
        return [
            {
                "package_name": info["module"]["package_name"],
                "name": info["module"].get("name", info["module"]["package_name"]),
                "type": info["module"].get("type", ""),
                "category": info["module"].get("category", ""),
                "version": info["module"].get("version", ""),
                "description": info["module"].get("description", ""),
            }
            for info in self._module_infos.values()
        ]

    def getMethods(self, package_name: str) -> list[str]:
        """Returns the list of available methods for a specific module."""
        if package_name not in self._module_infos:
            raise KeyError(f"Module not found: {package_name}")
        return self._module_infos[package_name]["module"].get("all_methods", [])

    def getModuleConfig(self, package_name: str) -> dict | None:
        """Returns the full configuration dictionary for a module."""
        return self._module_infos.get(package_name)