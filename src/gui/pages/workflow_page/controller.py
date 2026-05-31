from core.platform import getRuntimePath


class WorkflowController:
    def __init__(self, context):
        self._logger = context.log.getLogger(__name__)
        self._module_service = context.modules
        self._context = context

    def getWorkflows(self) -> list[dict]:
        modules = self._module_service.listModules()
        return [
            m
            for m in modules
            if m.get("type") == "workflow" and m.get("category") == "workflow"
        ]

    def getMethods(self, package_name: str) -> list[str]:
        return self._module_service.getMethods(package_name)

    def getModuleConfig(self, package_name: str) -> dict | None:
        return self._module_service.getModuleConfig(package_name)

    def getWorkflowModule(self, package_name: str):
        return self._module_service.getModule(package_name)

    def hasModuleWidget(self, package_name: str) -> bool:
        ui_dir = getRuntimePath() / "modules" / package_name / "ui"
        self._logger.debug(f"Checking widget for {package_name}: ui_dir={ui_dir}")
        if not ui_dir.exists():
            self._logger.debug(f"UI dir does not exist: {ui_dir}")
            return False
        ui_init = ui_dir / "__init__.py"
        if not ui_init.exists():
            self._logger.debug(f"UI __init__ does not exist: {ui_init}")
            return False
        import sys
        from importlib import import_module

        runtime_path = str(getRuntimePath())
        if runtime_path not in sys.path:
            sys.path.insert(0, runtime_path)
        try:
            ui_module = import_module(f"modules.{package_name}.ui")
            result = hasattr(ui_module, "createWizard")
            self._logger.debug(f"createWizard exists: {result}")
            return result
        except Exception as e:
            self._logger.error(f"hasModuleWidget failed: {e}")
            return False

    def getModuleWidget(self, package_name: str, method_name: str = ""):
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
            return widget
        except Exception as e:
            self._logger.error(
                f"Failed to load widget for {package_name}.{method_name}: {e}"
            )
            return None

    def callWorkflow(self, package_name: str, method_name: str, **kwargs) -> dict:
        self._logger.info(f"Calling {package_name}.{method_name}")
        self._logger.debug(f"Arguments: {kwargs}")
        try:
            result = self._module_service.callMethod(
                package_name, method_name, **kwargs
            )
            self._logger.info("Workflow execution successful")
            return result
        except Exception as e:
            self._logger.error(f"Workflow failed: {e}")
            raise
