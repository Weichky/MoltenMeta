from .widget_scatter import ToopScatterWizardDialog
from .widget_contour import ToopContourWizardDialog


def createToopWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Toop wizard dialog."""
    if method_name == "calculateScatter":
        return ToopScatterWizardDialog(module_service, user_db_service)
    elif method_name == "calculateContour":
        return ToopContourWizardDialog(module_service, user_db_service)
    else:
        return None


__all__ = ["ToopScatterWizardDialog", "ToopContourWizardDialog", "createToopWizard"]
