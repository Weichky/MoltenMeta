from .butler_module import (
    ButlerCalc,
    ButlerConfig,
    ButlerGEFunctions,
    ButlerSolutionDict,
    ButlerSampleDict,
    R,
    N_A,
    S_CONSTANT,
    BETA,
)

__all__ = [
    "ButlerCalc",
    "ButlerConfig",
    "ButlerGEFunctions",
    "ButlerSolutionDict",
    "ButlerSampleDict",
    "R",
    "N_A",
    "S_CONSTANT",
    "BETA",
    "registerDataSources",
    "ButlerDataSource",
]


class ButlerDataSource:
    def __init__(
        self, module_service, module_name: str, method_name: str, output_symbol: str
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
        return f"{self._module}"

    @property
    def output_symbol(self) -> str:
        return self._output_symbol

    @property
    def tags(self) -> list[str]:
        return ["sigma", "Butler", "Any"]

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


def _createButlerSource(module_service):
    return ButlerDataSource(module_service, "butler_module", "solve", "sigma")


def registerDataSources(registry) -> None:
    registry.register("sigma", _createButlerSource)
    registry.register("Butler", _createButlerSource)
