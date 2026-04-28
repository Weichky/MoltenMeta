import sys
import tomllib
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from framework.binary_provider import BinaryDataProvider

from .element_map import elemIdToSymbol
from modules.geometric_model_core import GeometricModelCalculator

_MODULE_DIR = Path(__file__).parent

if sys.platform == "win32":
    _ALG_EXT = "hillert_toop_algorithm.pyd"
else:
    _ALG_EXT = "hillert_toop_algorithm.so"

_spec_alg = importlib.util.spec_from_file_location(
    "hillert_toop_algorithm", _MODULE_DIR / "lib" / _ALG_EXT
)
assert _spec_alg is not None and _spec_alg.loader is not None
_hillert_toop_algorithm = importlib.util.module_from_spec(_spec_alg)
_spec_alg.loader.exec_module(_hillert_toop_algorithm)

with open(_MODULE_DIR / "config.toml", "rb") as _f:
    MODULE_INFO = tomllib.load(_f)


class HillertToopCalc(GeometricModelCalculator):
    def __init__(self, binary_provider: "BinaryDataProvider | None" = None):
        super().__init__()
        self._provider = binary_provider

    def setProvider(self, provider: "BinaryDataProvider") -> None:
        self._provider = provider

    def _getMethodName(self) -> str:
        return "HillertToop"

    def calculateSingleProperty(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        x_A: float,
        x_B: float,
        x_C: float,
        Z_AB: float,
        Z_AC: float,
        Z_BC: float,
    ) -> dict:
        value = _hillert_toop_algorithm.calculateSingleProperty(
            x_A, x_B, x_C, Z_AB, Z_AC, Z_BC
        )

        cfg = MODULE_INFO["calculateSingleProperty"]
        output_symbol = cfg["outputs"]["symbol"][0]
        inputs_latex = cfg["inputs"]["latex"]

        return {
            "conditions": {
                "elem_A": elemIdToSymbol(elem_A),
                "elem_B": elemIdToSymbol(elem_B),
                "elem_C": elemIdToSymbol(elem_C),
            },
            "values": [{"x_A": x_A, "x_B": x_B, "x_C": x_C, output_symbol: value}],
            "units": {
                "x_A": "",
                "x_B": "",
                "x_C": "",
                output_symbol: cfg["outputs"]["unit"][output_symbol],
            },
            "latex": {
                "elem_A": inputs_latex["elem_A"],
                "elem_B": inputs_latex["elem_B"],
                "elem_C": inputs_latex["elem_C"],
                "x_A": inputs_latex["x_A"],
                "x_B": inputs_latex["x_B"],
                "x_C": inputs_latex["x_C"],
                output_symbol: cfg["outputs"]["latex"][output_symbol],
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "main_dim": output_symbol,
            "method": "HillertToop",
        }

    def calculatePropertyList(
        self,
        x_A_list: list[float],
        x_B_list: list[float],
        x_C_list: list[float],
        Z_AB_list: list[float],
        Z_AC_list: list[float],
        Z_BC_list: list[float],
    ) -> list[float]:
        """Call C++ batch calculation."""
        import numpy as np

        x_A_arr = np.array(x_A_list, dtype=np.float64)
        x_B_arr = np.array(x_B_list, dtype=np.float64)
        x_C_arr = np.array(x_C_list, dtype=np.float64)
        Z_AB_arr = np.array(Z_AB_list, dtype=np.float64)
        Z_AC_arr = np.array(Z_AC_list, dtype=np.float64)
        Z_BC_arr = np.array(Z_BC_list, dtype=np.float64)

        result = _hillert_toop_algorithm.calculatePropertyList(
            x_A_arr, x_B_arr, x_C_arr, Z_AB_arr, Z_AC_arr, Z_BC_arr
        )
        return result.tolist()

    def calculateScatter(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        n_points: int = 50,
        z_symbol: str | None = None,
    ) -> dict:
        """Calculate Hillert-Toop model for a triangular grid."""
        if n_points < 0:
            raise ValueError(f"n_points must be non-negative, got {n_points}")

        cfg = MODULE_INFO["calculateScatter"]
        output_symbol = z_symbol or cfg["outputs"]["symbol"][0]

        if n_points == 0:
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateScatter"],
                extra_conditions={"output_symbol": output_symbol},
            )

        x_A_list, x_B_list, x_C_list = self._generateGrid(n_points)

        if not x_A_list or len(x_A_list) < 3:
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateScatter"],
                extra_conditions={"output_symbol": output_symbol},
            )

        Z_AB_list = self._provider.get_values(elem_A, elem_B, x_A_list)
        Z_AC_list = self._provider.get_values(elem_A, elem_C, x_A_list)

        V_BC_list = [(1.0 + x_B - x_C) / 2.0 for x_B, x_C in zip(x_B_list, x_C_list)]
        Z_BC_list = self._provider.get_values(elem_B, elem_C, V_BC_list)

        Z_ABC_list = self.calculatePropertyList(
            x_A_list, x_B_list, x_C_list, Z_AB_list, Z_AC_list, Z_BC_list
        )

        if not Z_ABC_list or len(Z_ABC_list) != len(x_A_list):
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateScatter"],
                extra_conditions={"output_symbol": output_symbol},
            )

        values = []
        for a, b, c, z in zip(x_A_list, x_B_list, x_C_list, Z_ABC_list):
            if z is not None and z == z:
                values.append({output_symbol: z, "x_A": a, "x_B": b, "x_C": c})

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
                output_symbol: cfg["outputs"]["unit"][output_symbol],
            },
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: cfg["outputs"]["latex"][output_symbol],
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "main_dim": output_symbol,
            "method": "HillertToop",
        }

    def calculateContourWithData(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        plane: str,
        n_points: int,
        Z_AB_list: list[float],
        Z_BC_list: list[float],
        Z_AC_list: list[float],
        z_latex: str,
        z_unit: str,
        z_symbol: str | None = None,
    ) -> dict:
        """Calculate contour data for x_i-x_j plane with direct data input."""
        if plane not in ("x_A-x_B", "x_A-x_C", "x_B-x_C"):
            raise ValueError(f"plane must be x_A-x_B, x_A-x_C, or x_B-x_C, got {plane}")

        cfg = MODULE_INFO["calculateContour"]
        output_symbol = z_symbol or cfg["outputs"]["symbol"][0]

        if n_points <= 0:
            return {
                "conditions": {
                    "elem_A": elemIdToSymbol(elem_A),
                    "elem_B": elemIdToSymbol(elem_B),
                    "elem_C": elemIdToSymbol(elem_C),
                    "plane": plane,
                },
                "dims": ["x_A", "x_B", "x_C", output_symbol],
                "main_dim": output_symbol,
                "values": [],
                "latex": {
                    "x_A": "x_A",
                    "x_B": "x_B",
                    "x_C": "x_C",
                    output_symbol: z_latex,
                },
                "units": {"x_A": "", "x_B": "", "x_C": "", output_symbol: z_unit},
                "plane": plane,
            }

        x_A_list, x_B_list, x_C_list = self._generateGrid(n_points)

        if not x_A_list or len(x_A_list) < 3:
            return {
                "conditions": {
                    "elem_A": elemIdToSymbol(elem_A),
                    "elem_B": elemIdToSymbol(elem_B),
                    "elem_C": elemIdToSymbol(elem_C),
                    "plane": plane,
                },
                "dims": ["x_A", "x_B", "x_C", output_symbol],
                "main_dim": output_symbol,
                "values": [],
                "latex": {
                    "x_A": "x_A",
                    "x_B": "x_B",
                    "x_C": "x_C",
                    output_symbol: z_latex,
                },
                "units": {"x_A": "", "x_B": "", "x_C": "", output_symbol: z_unit},
                "plane": plane,
            }

        V_BC_list = [(1.0 + x_B - x_C) / 2.0 for x_B, x_C in zip(x_B_list, x_C_list)]
        if len(Z_BC_list) != len(V_BC_list):
            raise ValueError(
                f"Z_BC_list has {len(Z_BC_list)} values, expected {len(V_BC_list)}"
            )

        Z_ABC_list = self.calculatePropertyList(
            x_A_list, x_B_list, x_C_list, Z_AB_list, Z_AC_list, Z_BC_list
        )

        if not Z_ABC_list or len(Z_ABC_list) != len(x_A_list):
            return {
                "conditions": {
                    "elem_A": elemIdToSymbol(elem_A),
                    "elem_B": elemIdToSymbol(elem_B),
                    "elem_C": elemIdToSymbol(elem_C),
                    "plane": plane,
                },
                "dims": ["x_A", "x_B", "x_C", output_symbol],
                "main_dim": output_symbol,
                "values": [],
                "latex": {
                    "x_A": "x_A",
                    "x_B": "x_B",
                    "x_C": "x_C",
                    output_symbol: z_latex,
                },
                "units": {"x_A": "", "x_B": "", "x_C": "", output_symbol: z_unit},
                "plane": plane,
            }

        values = []
        for a, b, c, z in zip(x_A_list, x_B_list, x_C_list, Z_ABC_list):
            if z is not None and z == z:
                values.append({output_symbol: z, "x_A": a, "x_B": b, "x_C": c})

        return {
            "conditions": {
                "elem_A": elemIdToSymbol(elem_A),
                "elem_B": elemIdToSymbol(elem_B),
                "elem_C": elemIdToSymbol(elem_C),
                "plane": plane,
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "main_dim": output_symbol,
            "values": values,
            "latex": {"x_A": "x_A", "x_B": "x_B", "x_C": "x_C", output_symbol: z_latex},
            "units": {"x_A": "", "x_B": "", "x_C": "", output_symbol: z_unit},
            "x_i": x_A_list,
            "x_j": x_B_list,
            output_symbol: Z_ABC_list,
            "plane": plane,
        }

    def calculateScatterWithData(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        n_points: int,
        Z_AB_list: list[float],
        Z_AC_list: list[float],
        Z_BC_list: list[float],
        z_latex: str,
        z_unit: str,
        z_symbol: str | None = None,
    ) -> dict:
        if n_points < 0:
            raise ValueError(f"n_points must be non-negative, got {n_points}")

        cfg = MODULE_INFO["calculateScatter"]
        output_symbol = z_symbol or cfg["outputs"]["symbol"][0]
        final_latex = z_latex
        final_unit = z_unit

        if n_points == 0:
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateScatter"],
                extra_conditions={"output_symbol": output_symbol},
            )

        x_A_list, x_B_list, x_C_list = self._generateGrid(n_points)

        if not x_A_list or len(x_A_list) < 3:
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateScatter"],
                extra_conditions={"output_symbol": output_symbol},
            )

        Z_ABC_list = self.calculatePropertyList(
            x_A_list, x_B_list, x_C_list, Z_AB_list, Z_AC_list, Z_BC_list
        )

        if not Z_ABC_list or len(Z_ABC_list) != len(x_A_list):
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateScatter"],
                extra_conditions={"output_symbol": output_symbol},
            )

        # Filter out NaN values that arise at triangle vertices and edges.
        # The Hillert-Toop formula divides by V_BC*V_CB which becomes zero
        # at pure component corners (x_B=0, x_C=0) or midpoints (x_B=x_C=0.5)
        # on an edge. SQLite NOT NULL constraint disallows nan as a valid value.
        values = [
            {output_symbol: z, "x_A": a, "x_B": b, "x_C": c}
            for a, b, c, z in zip(x_A_list, x_B_list, x_C_list, Z_ABC_list)
            if z is not None and z == z
        ]

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
                output_symbol: final_unit,
            },
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: final_latex,
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "main_dim": output_symbol,
            "method": "HillertToop",
        }


def _linspace(start: float, end: float, num: int) -> list[float]:
    """Generate evenly spaced points."""
    if num <= 0:
        return []
    if num <= 1:
        return [start]
    step = (end - start) / (num - 1)
    return [start + i * step for i in range(num)]
