import sys
import tomllib
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from framework.binary_provider import BinaryDataProvider

from .element_map import elemIdToSymbol

_MODULE_DIR = Path(__file__).parent

if sys.platform == "win32":
    _ALG_EXT = "toop_algorithm.pyd"
    _GRID_EXT = "toop_grid.pyd"
else:
    _ALG_EXT = "toop_algorithm.so"
    _GRID_EXT = "toop_grid.so"

_spec_alg = importlib.util.spec_from_file_location(
    "toop_algorithm", _MODULE_DIR / "lib" / _ALG_EXT
)
assert _spec_alg is not None and _spec_alg.loader is not None
_toop_algorithm = importlib.util.module_from_spec(_spec_alg)
_spec_alg.loader.exec_module(_toop_algorithm)

_spec_grid = importlib.util.spec_from_file_location(
    "toop_grid", _MODULE_DIR / "lib" / _GRID_EXT
)
assert _spec_grid is not None and _spec_grid.loader is not None
_toop_grid = importlib.util.module_from_spec(_spec_grid)
_spec_grid.loader.exec_module(_toop_grid)

with open(_MODULE_DIR / "config.toml", "rb") as _f:
    MODULE_INFO = tomllib.load(_f)


class ToopCalc:
    def __init__(self, binary_provider: "BinaryDataProvider | None" = None):
        self._provider = binary_provider

    def setProvider(self, provider: "BinaryDataProvider") -> None:
        self._provider = provider

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
        value = _toop_algorithm.calculateSingleProperty(x_B, x_C, Z_AB, Z_AC, Z_BC)

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
                output_symbol: cfg["outputs"]["unit"][0],
            },
            "latex": {
                "elem_A": inputs_latex[0],
                "elem_B": inputs_latex[1],
                "elem_C": inputs_latex[2],
                "x_A": inputs_latex[3],
                "x_B": inputs_latex[4],
                "x_C": inputs_latex[5],
                output_symbol: cfg["outputs"]["latex"][0],
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "method": "Toop",
        }

    def calculatePropertyList(
        self,
        x_B_list: list[float],
        x_C_list: list[float],
        Z_AB_list: list[float],
        Z_AC_list: list[float],
        Z_BC_list: list[float],
    ) -> list[float]:
        """Call C++ batch calculation."""
        import numpy as np

        x_B_arr = np.array(x_B_list, dtype=np.float64)
        x_C_arr = np.array(x_C_list, dtype=np.float64)
        Z_AB_arr = np.array(Z_AB_list, dtype=np.float64)
        Z_AC_arr = np.array(Z_AC_list, dtype=np.float64)
        Z_BC_arr = np.array(Z_BC_list, dtype=np.float64)

        result = _toop_algorithm.calculatePropertyList(
            x_B_arr, x_C_arr, Z_AB_arr, Z_AC_arr, Z_BC_arr
        )
        return result

    def _generateGrid(
        self, n_points: int
    ) -> tuple[list[float], list[float], list[float]]:
        """Generate triangular grid points on x_A + x_B + x_C = 1 via C++."""
        if n_points <= 0:
            return [], [], []
        if n_points == 1:
            return [0.0], [0.0], [1.0]
        x_A_arr, x_B_arr, x_C_arr = _toop_grid.generateTriangularGrid(n_points)
        return list(x_A_arr), list(x_B_arr), list(x_C_arr)

    def calculateRange(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        n_points: int = 50,
    ) -> dict:
        """
        Calculate Toop model for a triangular grid.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            elem_C: Atomic number of element C
            n_points: Number of points per edge (total ~ n_points^2/2)

        Returns:
            Dictionary containing calculation results
        """
        if n_points < 0:
            raise ValueError(f"n_points must be non-negative, got {n_points}")

        if self._provider is None:
            raise RuntimeError("No BinaryDataProvider configured for ToopCalc")

        x_A_list, x_B_list, x_C_list = self._generateGrid(n_points)

        if not x_A_list:
            return self._emptyResult(
                elem_A, elem_B, elem_C, MODULE_INFO["calculateRange"]
            )

        Z_AB_list = self._provider.get_values(elem_A, elem_B, x_A_list)
        if len(Z_AB_list) != len(x_A_list):
            raise ValueError(
                f"Provider Z_AB returned {len(Z_AB_list)} values, expected {len(x_A_list)}"
            )

        Z_AC_list = self._provider.get_values(elem_A, elem_C, x_A_list)
        if len(Z_AC_list) != len(x_A_list):
            raise ValueError(
                f"Provider Z_AC returned {len(Z_AC_list)} values, expected {len(x_A_list)}"
            )

        w_B_list = [
            x_B / (x_B + x_C) if (x_B + x_C) > 0 else 0
            for x_B, x_C in zip(x_B_list, x_C_list)
        ]
        Z_BC_list = self._provider.get_values(elem_B, elem_C, w_B_list)
        if len(Z_BC_list) != len(w_B_list):
            raise ValueError(
                f"Provider Z_BC returned {len(Z_BC_list)} values, expected {len(w_B_list)}"
            )

        Z_ABC_list = self.calculatePropertyList(
            x_B_list, x_C_list, Z_AB_list, Z_AC_list, Z_BC_list
        )

        cfg = MODULE_INFO["calculateRange"]
        output_symbol = cfg["outputs"]["symbol"][0]

        values = [
            {"x_A": a, "x_B": b, "x_C": c, output_symbol: z}
            for a, b, c, z in zip(x_A_list, x_B_list, x_C_list, Z_ABC_list)
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
                output_symbol: cfg["outputs"]["unit"][0],
            },
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: cfg["outputs"]["latex"][0],
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "method": "Toop",
        }

    def calculateCrossSection(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        fixed_component: str,
        fixed_value: float,
        n_points: int = 50,
    ) -> dict:
        """
        Calculate cross section of the Toop model.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            elem_C: Atomic number of element C
            fixed_component: Which component is fixed ("x_A", "x_B", or "x_C")
            fixed_value: Value of the fixed component
            n_points: Number of points

        Returns:
            Dictionary containing cross section results
        """
        if n_points < 0:
            raise ValueError(f"n_points must be non-negative, got {n_points}")

        if not 0 <= fixed_value <= 1:
            raise ValueError(f"fixed_value must be in [0, 1], got {fixed_value}")

        if fixed_component not in ("x_A", "x_B", "x_C"):
            raise ValueError(
                f"fixed_component must be x_A, x_B, or x_C, got {fixed_component}"
            )

        max_other = 1 - fixed_value
        if max_other < 0:
            raise ValueError(
                f"fixed_value {fixed_value} leaves no room for other components (must be <= 1)"
            )

        if self._provider is None:
            raise RuntimeError("No BinaryDataProvider configured for ToopCalc")

        x_A_list, x_B_list, x_C_list = [], [], []

        if fixed_component == "x_A":
            x_A_fixed = fixed_value
            for x_B in _linspace(0, max_other, n_points):
                x_C = 1 - x_A_fixed - x_B
                x_A_list.append(x_A_fixed)
                x_B_list.append(x_B)
                x_C_list.append(x_C)
        elif fixed_component == "x_B":
            x_B_fixed = fixed_value
            for x_A in _linspace(0, max_other, n_points):
                x_C = 1 - x_A - x_B_fixed
                x_A_list.append(x_A)
                x_B_list.append(x_B_fixed)
                x_C_list.append(x_C)
        elif fixed_component == "x_C":
            x_C_fixed = fixed_value
            for x_A in _linspace(0, max_other, n_points):
                x_B = 1 - x_A - x_C_fixed
                x_A_list.append(x_A)
                x_B_list.append(x_B)
                x_C_list.append(x_C_fixed)

        if not x_A_list:
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateCrossSection"],
                {
                    "fixed_component": fixed_component,
                    "fixed_value": fixed_value,
                },
            )

        Z_AB_list = self._provider.get_values(elem_A, elem_B, x_A_list)
        if len(Z_AB_list) != len(x_A_list):
            raise ValueError(
                f"Provider Z_AB returned {len(Z_AB_list)} values, expected {len(x_A_list)}"
            )

        Z_AC_list = self._provider.get_values(elem_A, elem_C, x_A_list)
        if len(Z_AC_list) != len(x_A_list):
            raise ValueError(
                f"Provider Z_AC returned {len(Z_AC_list)} values, expected {len(x_A_list)}"
            )

        w_B_list = [
            x_B / (x_B + x_C) if (x_B + x_C) > 0 else 0
            for x_B, x_C in zip(x_B_list, x_C_list)
        ]
        Z_BC_list = self._provider.get_values(elem_B, elem_C, w_B_list)
        if len(Z_BC_list) != len(w_B_list):
            raise ValueError(
                f"Provider Z_BC returned {len(Z_BC_list)} values, expected {len(w_B_list)}"
            )

        Z_ABC_list = self.calculatePropertyList(
            x_B_list, x_C_list, Z_AB_list, Z_AC_list, Z_BC_list
        )

        cfg = MODULE_INFO["calculateCrossSection"]
        output_symbol = cfg["outputs"]["symbol"][0]

        values = [
            {"x_A": a, "x_B": b, "x_C": c, output_symbol: z}
            for a, b, c, z in zip(x_A_list, x_B_list, x_C_list, Z_ABC_list)
        ]

        return {
            "conditions": {
                "elem_A": elemIdToSymbol(elem_A),
                "elem_B": elemIdToSymbol(elem_B),
                "elem_C": elemIdToSymbol(elem_C),
                "fixed_component": fixed_component,
                "fixed_value": fixed_value,
            },
            "values": values,
            "units": {
                "x_A": "",
                "x_B": "",
                "x_C": "",
                output_symbol: cfg["outputs"]["unit"][0],
            },
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: cfg["outputs"]["latex"][0],
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "method": "Toop",
        }

    def _emptyResult(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        cfg: dict,
        extra_conditions: dict | None = None,
    ) -> dict:
        """Return an empty result structure for edge cases."""
        output_symbol = cfg["outputs"]["symbol"][0]
        conditions = {
            "elem_A": elemIdToSymbol(elem_A),
            "elem_B": elemIdToSymbol(elem_B),
            "elem_C": elemIdToSymbol(elem_C),
        }
        if extra_conditions:
            conditions.update(extra_conditions)

        return {
            "conditions": conditions,
            "values": [],
            "units": {
                "x_A": "",
                "x_B": "",
                "x_C": "",
                output_symbol: cfg["outputs"]["unit"][0],
            },
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: cfg["outputs"]["latex"][0],
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "method": "Toop",
        }


def _linspace(start: float, end: float, num: int) -> list[float]:
    """Generate evenly spaced points."""
    if num <= 0:
        return []
    if num <= 1:
        return [start]
    step = (end - start) / (num - 1)
    return [start + i * step for i in range(num)]
