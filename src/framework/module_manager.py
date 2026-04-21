import importlib
import sys
import tomllib
from pathlib import Path

from core.log import LogService


class ModuleManager:
    def __init__(self, runtime_path: Path, log_service: LogService):
        self._logger = log_service.getLogger(__name__)
        self._modules: dict[str, object] = {}
        self._module_infos: dict[str, dict] = {}
        self._runtime_path = runtime_path
        self._ensureRuntimeInPath()
        self._discover(runtime_path / "modules")

    def _ensureRuntimeInPath(self) -> None:
        runtime_parent = str(self._runtime_path.parent)
        if runtime_parent not in sys.path:
            sys.path.insert(0, runtime_parent)

    def _discover(self, modules_dir: Path) -> None:
        """Scan modules directory, load config.toml and instantiate module entry classes."""
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
                mod = importlib.import_module(f"runtime.modules.{package_name}")
                cls = getattr(mod, entry_class)
                instance = cls()

                self._modules[package_name] = instance
                self._module_infos[package_name] = config

                self._logger.info(f"Loaded module: {package_name} ({entry_class})")
            except Exception as e:
                self._logger.error(f"Failed to load module {package_name}: {e}")

    def get(self, package_name: str) -> object:
        if package_name not in self._modules:
            raise KeyError(f"Module not found: {package_name}")
        return self._modules[package_name]

    def list(self) -> list[dict]:
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
        if package_name not in self._module_infos:
            raise KeyError(f"Module not found: {package_name}")
        return self._module_infos[package_name]["module"].get("all_methods", [])

    def getModuleConfig(self, package_name: str) -> dict | None:
        return self._module_infos.get(package_name)
