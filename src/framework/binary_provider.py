from abc import ABC, abstractmethod


class BinaryDataProvider(ABC):
    """
    Interface for providing binary property data.

    Used by modules like Toop that need to query binary data (e.g., Z_AB, Z_AC, Z_BC)
    from other modules like Miedema.

    Usage:
        class MiedemaProvider(BinaryDataProvider):
            def get_values(self, elem_1, elem_2, x_array):
                result = self._module_service.callMethod(
                    "miedema_module", "calculateSingleBatch",
                    elem_A=elem_1, elem_B=elem_2, x_array=x_array
                )
                return result["values"]

        toop = ToopCalc(MiedemaProvider(module_service))
    """

    @abstractmethod
    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        """
        Get binary property values for an array of compositions.

        Args:
            elem_1: Atomic number of first element
            elem_2: Atomic number of second element
            x_array: Array of mole fractions of elem_1

        Returns:
            Array of property values corresponding to x_array
        """
        raise NotImplementedError
