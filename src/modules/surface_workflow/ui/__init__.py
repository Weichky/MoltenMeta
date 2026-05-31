from .widget import SurfaceWorkflowWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    if method_name == "fit":
        return SurfaceWorkflowWizardDialog(
            module_service, user_db_service, method_type="fit"
        )
    elif method_name == "predict":
        return SurfaceWorkflowWizardDialog(
            module_service, user_db_service, method_type="predict"
        )
    elif method_name == "predictCurve":
        return SurfaceWorkflowWizardDialog(
            module_service, user_db_service, method_type="predictCurve"
        )
    else:
        return None


__all__ = ["SurfaceWorkflowWizardDialog", "createWizard"]
