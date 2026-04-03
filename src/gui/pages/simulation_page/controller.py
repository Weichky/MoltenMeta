import tomllib
from pathlib import Path
from PySide6 import QtWidgets

from .input_dialog import InputDialog


class SimulationController:
    def __init__(self, context):
        self._logger = context.log.getLogger(__name__)
        self._module_service = context.modules
        self._context = context
        self._current_config: dict = {}

    def get_categories(self) -> list[str]:
        modules = self._module_service.list_modules()
        categories = set()
        for m in modules:
            if m.get("type") == "simulation":
                categories.add(m.get("category", ""))
        return sorted(list(categories))

    def get_modules_by_category(self, category: str) -> list[dict]:
        modules = self._module_service.list_modules()
        return [
            m
            for m in modules
            if m.get("type") == "simulation" and m.get("category") == category
        ]

    def get_methods_by_module(self, package_name: str) -> list[str]:
        return self._module_service.get_methods(package_name)

    def load_module_config(self, package_name: str, method_name: str) -> dict | None:
        try:
            self._module_service.get_module(package_name)
            mod_dir = Path("runtime/modules") / package_name
            config_path = mod_dir / "config.toml"
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            self._current_config = config
            return config.get(method_name, {})
        except Exception as e:
            self._logger.error(f"Failed to load config for {package_name}: {e}")
            return None

    def get_current_config(self) -> dict:
        return self._current_config

    def show_input_dialog(self, method_name: str, parent=None) -> tuple[bool, dict]:
        config = self._current_config.get(method_name, {})
        if not config:
            return False, {}

        inputs_config = config.get("inputs", {})
        dialog = InputDialog(inputs_config, parent)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            return True, dialog.get_inputs()
        return False, {}

    def call_calculation(self, package_name: str, method_name: str, **kwargs) -> dict:
        self._logger.info(f"Calling {package_name}.{method_name}")
        self._logger.debug(f"Arguments: {kwargs}")
        try:
            result = self._module_service.call_method(
                package_name, method_name, **kwargs
            )
            self._logger.info("Calculation successful")
            return result
        except Exception as e:
            self._logger.error(f"Calculation failed: {e}")
            raise

    def get_module_info(self, package_name: str) -> dict | None:
        modules = self._module_service.list_modules()
        for m in modules:
            if m.get("package_name") == package_name:
                return m
        return None
