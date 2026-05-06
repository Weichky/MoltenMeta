from .element_properties_module import ElementPropertiesCalc, ElementProperties

__all__ = ["ElementPropertiesCalc", "ElementProperties", "registerDataSources"]


def registerDataSources(registry) -> None:
    from framework.data_module_registry import DataModuleRegistry

    DataModuleRegistry.register(ElementProperties, "element_properties")
