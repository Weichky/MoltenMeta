from .widget_scatter import MaggianuScatterWizardDialog
from .widget_contour import MaggianuContourWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Maggianu wizard dialog."""
    if method_name == "calculateScatter":
        return MaggianuScatterWizardDialog(module_service, user_db_service)
    elif method_name == "calculateContour":
        return MaggianuContourWizardDialog(module_service, user_db_service)
    else:
        return None


__all__ = [
    "MaggianuScatterWizardDialog",
    "MaggianuContourWizardDialog",
    "createWizard",
]
