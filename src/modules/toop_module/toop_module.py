import sys
import tomllib
import importlib.util
from pathlib import Path

from .element_map import elemIdToSymbol

_MODULE_DIR = Path(__file__).parent

if sys.platform == "win32":
    _LIB_NAME = "toop_algorithm.pyd"
else:
    _LIB_NAME = "toop_algorithm.so"
_LIB_PATH = _MODULE_DIR / "lib" / _LIB_NAME
_spec = importlib.util.spec_from_file_location("toop_algorithm", _LIB_PATH)
assert _spec is not None and _spec.loader is not None
_toop_algorithm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_toop_algorithm)

with open(_MODULE_DIR / "config.toml", "rb") as _f:
    MODULE_INFO = tomllib.load(_f)


class ToopCalc:
    _OUTPUT_SYMBOL = "follow Z_BC"
    _OUTPUT_LATEX = MODULE_INFO["calculateSingleProperty"]["outputs"]["latex"][0]

    def _buildOutput(
        self, elem_A: int, elem_B: int, elem_C: int, values: list[dict]
    ) -> dict:
        return {
            "conditions": {
                "elem_A": elemIdToSymbol(elem_A),
                "elem_B": elemIdToSymbol(elem_B),
                "elem_C": elemIdToSymbol(elem_C),
            },
            "values": values,
            "units": {
                "x_A": "",
                "x_B": "",
                "x_C": "",
            },
        }

    def calculateSingleProperty(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        x_B: float,
        x_C: float,
        Z_AB: float,
        Z_AC: float,
        Z_BC: float,
    ) -> dict:
        x_A = 1 - x_B - x_C
