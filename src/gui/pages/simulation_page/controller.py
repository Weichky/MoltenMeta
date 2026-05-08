try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from PySide6 import QtWidgets

from core.platform import getRuntimePath


class SimulationController:
    def __init__(self, context):
        self._logger = context.log.getLogger(__name__)
        self._module_service = context.modules
        self._context = context
        self._current_config: dict = {}
        self._module_widget_cache: dict = {}

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

    def hasModuleWidget(self, package_name: str) -> bool:
        ui_dir = getRuntimePath() / "modules" / package_name / "ui"
        if not ui_dir.exists():
            return False
        ui_init = ui_dir / "__init__.py"
        if not ui_init.exists():
            return False
        import sys
        from importlib import import_module

        runtime_path = str(getRuntimePath())
        if runtime_path not in sys.path:
            sys.path.insert(0, runtime_path)
        try:
            ui_module = import_module(f"modules.{package_name}.ui")
            return hasattr(ui_module, "createWizard")
        except Exception:
            return False

    def getModuleWidget(
        self, package_name: str, method_name: str = ""
    ) -> QtWidgets.QWidget | None:
        cache_key = f"{package_name}.{method_name}"
        if cache_key in self._module_widget_cache:
            return self._module_widget_cache[cache_key]

        try:
            import sys
            from importlib import import_module

            runtime_path = str(getRuntimePath())
            if runtime_path not in sys.path:
                sys.path.insert(0, runtime_path)

            ui_module_name = f"modules.{package_name}.ui"
            ui_module = import_module(ui_module_name)

            wizard_factory = getattr(ui_module, "createWizard", None)
            if wizard_factory is None:
                self._logger.error(f"No 'createWizard' found in {package_name}.ui")
                return None

            widget = wizard_factory(
                method_name, self._module_service, self._context.user_db
            )
            if widget is not None:
                self._module_widget_cache[cache_key] = widget
            return widget
        except Exception as e:
            self._logger.error(
                f"Failed to load widget for {package_name}.{method_name}: {e}"
            )
            return None
