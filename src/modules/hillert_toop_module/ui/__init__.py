from .widget_scatter import HillertToopScatterWizardDialog
from .widget_contour import HillertToopContourWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Hillert-Toop wizard dialog."""
    if method_name == "calculateScatter":
        return HillertToopScatterWizardDialog(module_service, user_db_service)
    elif method_name == "calculateContour":
        return HillertToopContourWizardDialog(module_service, user_db_service)
    else:
        return None


__all__ = [
    "HillertToopScatterWizardDialog",
    "HillertToopContourWizardDialog",
    "createWizard",
]
