from .widget import KohlerWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Kohler wizard dialog."""
    if method_name == "calculateScatter":
        return KohlerWizardDialog(module_service, user_db_service, method_type="scatter")
    elif method_name == "calculateContour":
        return KohlerWizardDialog(module_service, user_db_service, method_type="contour")
    else:
        return None


__all__ = [
    "KohlerWizardDialog",
    "createWizard",
]
