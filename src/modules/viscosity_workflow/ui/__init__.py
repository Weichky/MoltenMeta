from .widget import ViscosityWorkflowWizardDialog


def createWizard(method_name: str, module_service, user_db_service):
    if method_name == "fit":
        return ViscosityWorkflowWizardDialog(
            module_service, user_db_service, method_type="fit"
        )
    elif method_name == "predict":
        return ViscosityWorkflowWizardDialog(
            module_service, user_db_service, method_type="predict"
        )
    elif method_name == "predictBatch":
        return ViscosityWorkflowWizardDialog(
            module_service, user_db_service, method_type="predictBatch"
        )
    elif method_name == "predictOnGrid":
        return ViscosityWorkflowWizardDialog(
            module_service, user_db_service, method_type="predictOnGrid"
        )
    else:
        return None


__all__ = ["ViscosityWorkflowWizardDialog", "createWizard"]
