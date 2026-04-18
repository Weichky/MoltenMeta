from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class DataSource(ABC):
    @property
    @abstractmethod
    def source_type(self) -> str:
        """返回 'module' 或 'database'"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """返回 'Miedema' 或 'Fe-Cu-001' 等"""

    @property
    @abstractmethod
    def unit(self) -> str:
        """返回单位，如 'kJ/mol'"""

    @abstractmethod
    def get_value(self, elem_1: int, elem_2: int, x: float) -> float:
        """单点查询"""

    @abstractmethod
    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        """批量查询"""


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
    def unit(self) -> str:
        return ""

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
    def __init__(self, db_record: dict, unit: str):
        self._record = db_record
        self._unit = unit

    @property
    def source_type(self) -> str:
        return "database"

    @property
    def source_name(self) -> str:
        return self._record.get("name", "Unknown")

    @property
    def unit(self) -> str:
        return self._unit

    def get_value(self, elem_1: int, elem_2: int, x: float) -> float:
        return self._record.get("value", 0.0)

    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        value = self._record.get("value", 0.0)
        return [value] * len(x_array)
