from .widget import HillertToopWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Hillert-Toop wizard dialog."""
    if method_name == "calculateScatter":
        return HillertToopWizardDialog(module_service, user_db_service, method_type="scatter")
    elif method_name == "calculateContour":
        return HillertToopWizardDialog(module_service, user_db_service, method_type="contour")
    else:
        return None


__all__ = [
    "HillertToopWizardDialog",
    "createWizard",
]
