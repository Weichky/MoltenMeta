from abc import ABC, abstractmethod


class DataSource(ABC):
    @property
    @abstractmethod
    def source_type(self) -> str:
        """Returns 'module' or 'database'"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Returns 'Miedema' or 'Fe-Cu-001' etc"""

    @abstractmethod
    def get_value(self, elem_1: int, elem_2: int, x: float) -> float:
        """Single point query"""

    @abstractmethod
    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        """Batch query"""


class ModuleDataSource(DataSource):
    def __init__(
        self,
        module_service,
        module_name: str,
        method_name: str,
        output_symbol: str,
    ):
        self._ms = module_service
        self._module = module_name
        self._method = method_name
        self._output_symbol = output_symbol

    @property
    def source_type(self) -> str:
        return "module"

    @property
    def source_name(self) -> str:
        return self._module

    @property
    def output_symbol(self) -> str:
        return self._output_symbol

    def get_value(self, elem_1: int, elem_2: int, x: float) -> float:
        result = self._ms.callMethod(
            self._module,
            self._method,
            elem_A=elem_1,
            elem_B=elem_2,
            x_A=x,
            _skip_cache=True,
        )
        return result["values"][0][self._output_symbol]

    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        result = self._ms.callMethod(
            self._module,
            self._method,
            elem_A=elem_1,
            elem_B=elem_2,
            x_array=x_array,
            _skip_cache=True,
        )
        return result["values"]


class DatabaseDataSource(DataSource):
    def __init__(self, db_record: dict):
        self._record = db_record

    @property
    def source_type(self) -> str:
        return "database"

    @property
    def source_name(self) -> str:
        return self._record.get("name", "Unknown")

    def get_value(self, elem_1: int, elem_2: int, x: float) -> float:
        return self._record.get("value", 0.0)

    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        value = self._record.get("value", 0.0)
        return [{"value": value} for _ in x_array]
