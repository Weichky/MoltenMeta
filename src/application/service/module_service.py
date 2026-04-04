from pathlib import Path

from core.log import LogService
from framework.module_manager import ModuleManager


class ModuleService:
    def __init__(self, runtime_path: Path, log_service: LogService):
        self._logger = log_service.getLogger(__name__)
        self._manager = ModuleManager(runtime_path, log_service)

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
        return method(**kwargs)
