from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from .miedema_module import MiedemaCalc

__all__ = ["MiedemaCalc", "registerDataSources"]


class _ModuleDataSource:
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
    def display_name(self) -> str:
        return f"{self._module} ({self._output_symbol})"

    @property
    def output_symbol(self) -> str:
        return self._output_symbol

    def getValue(self, elem_1: int, elem_2: int, x: float) -> float:
        result = self._ms.callMethod(
            self._module,
            self._method,
            elem_A=elem_1,
            elem_B=elem_2,
            x_A=x,
            _skip_cache=True,
        )
        return result["values"][0][self._output_symbol]

    def getValues(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        result = self._ms.callMethod(
            self._module,
            self._method,
            elem_A=elem_1,
            elem_B=elem_2,
            x_array=x_array,
            _skip_cache=True,
        )
        return result["values"]


def _createMiedemaSource(module_service):
    config_path = Path(__file__).parent / "config.toml"
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    batch_config = config.get("calculateSingleBatch", {})
    outputs = batch_config.get("outputs", {})
    output_symbol = outputs.get("symbol", ["Delta_H_mix"])[0]

    return _ModuleDataSource(
        module_service,
        module_name="miedema_module",
        method_name="calculateSingleBatch",
        output_symbol=output_symbol,
    )


def registerDataSources(registry) -> None:
    """Register data sources provided by this module."""
    registry.register("binary_data", _createMiedemaSource)
    registry.register("thermodynamic", _createMiedemaSource)
