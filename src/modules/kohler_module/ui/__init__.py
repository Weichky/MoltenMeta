from .widget_scatter import KohlerScatterWizardDialog
from .widget_contour import KohlerContourWizardDialog


def createKohlerWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Kohler wizard dialog."""
    if method_name == "calculateScatter":
        return KohlerScatterWizardDialog(module_service, user_db_service)
    elif method_name == "calculateContour":
        return KohlerContourWizardDialog(module_service, user_db_service)
    else:
        return None


__all__ = [
    "KohlerScatterWizardDialog",
    "KohlerContourWizardDialog",
    "createKohlerWizard",
]
