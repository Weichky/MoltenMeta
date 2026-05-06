from .widget import ToopWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    """Factory function to create the appropriate Toop wizard dialog."""
    if method_name == "calculateScatter":
        return ToopWizardDialog(module_service, user_db_service, method_type="scatter")
    elif method_name == "calculateContour":
        return ToopWizardDialog(module_service, user_db_service, method_type="contour")
    else:
        return None


__all__ = ["ToopWizardDialog", "createWizard"]
