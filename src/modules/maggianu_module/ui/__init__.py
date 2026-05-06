from .widget import MaggianuWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Maggianu wizard dialog."""
    if method_name == "calculateScatter":
        return MaggianuWizardDialog(module_service, user_db_service, method_type="scatter")
    elif method_name == "calculateContour":
        return MaggianuWizardDialog(module_service, user_db_service, method_type="contour")
    else:
        return None


__all__ = [
    "MaggianuWizardDialog",
    "createWizard",
]
