import tomllib
from PySide6 import QtWidgets

from core.platform import getRuntimePath

from .input_dialog import InputDialog


class SimulationController:
    def __init__(self, context):
        self._logger = context.log.getLogger(__name__)
        self._module_service = context.modules
        self._context = context
        self._current_config: dict = {}

    def getCategories(self) -> list[str]:
        modules = self._module_service.listModules()
        categories = set()
        for m in modules:
            if m.get("type") == "simulation":
                categories.add(m.get("category", ""))
        return sorted(list(categories))

    def getModulesByCategory(self, category: str) -> list[dict]:
        modules = self._module_service.listModules()
        return [
            m
            for m in modules
            if m.get("type") == "simulation" and m.get("category") == category
        ]

    def getMethodsByModule(self, package_name: str) -> list[str]:
        return self._module_service.getMethods(package_name)

    def loadModuleConfig(self, package_name: str, method_name: str) -> dict | None:
        try:
            self._module_service.getModule(package_name)
            mod_dir = getRuntimePath() / "modules" / package_name
            config_path = mod_dir / "config.toml"
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            self._current_config = config
            return config.get(method_name, {})
        except Exception as e:
            self._logger.error(f"Failed to load config for {package_name}: {e}")
            return None

    def getCurrentConfig(self) -> dict:
        return self._current_config

    def showInputDialog(self, method_name: str, parent=None) -> tuple[bool, dict]:
        config = self._current_config.get(method_name, {})
        if not config:
            return False, {}

        inputs_config = config.get("inputs", {})
        dialog = InputDialog(inputs_config, self._context.user_db, parent)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            return True, dialog.getInputs()
        return False, {}

    def callCalculation(self, package_name: str, method_name: str, **kwargs) -> dict:
        self._logger.info(f"Calling {package_name}.{method_name}")
        self._logger.debug(f"Arguments: {kwargs}")
        try:
            result = self._module_service.callMethod(
                package_name, method_name, **kwargs
            )
            self._logger.info("Calculation successful")
            return result
        except Exception as e:
            self._logger.error(f"Calculation failed: {e}")
            raise

    def getModuleInfo(self, package_name: str) -> dict | None:
        modules = self._module_service.listModules()
        for m in modules:
            if m.get("package_name") == package_name:
                return m
        return None
