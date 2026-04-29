"""
==================== Algorithm ====================

Step 1: Select Miedema constants (p, q, r/p) based on whether each
        element is a transition metal (TM).

Step 2: Calculate the interaction parameter f_AB:
        f_AB = 2 * p * V_A^(2/3) * V_B^(2/3)
               * [ (q/p) * (Δn_WS^1/3)² - (Δφ)² - a * (r/p) ]
               / [ (n_WS^1/3)_A^(-1) + (n_WS^1/3)_B^(-1) ]

        where Δn_WS^1/3 = (n_WS^1/3)_A - (n_WS^1/3)_B
              Δφ = φ_A - φ_B

Step 3: Calculate ΔH_AB at composition x_A:
        numerator   = x_A * x_B * (1 + μ_A * x_B * Δφ) * (1 - μ_B * x_A * Δφ)
        denominator = x_A * V_A^(2/3) * (1 + μ_A * x_B * Δφ)
                   + x_B * V_B^(2/3) * (1 - μ_B * x_A * Δφ)

        ΔH_AB = f_AB * numerator / denominator

Step 4: Return the result in structured format with element symbols
        and LaTeX labels for display.
"""

import csv
import sys
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
import importlib.util
from pathlib import Path

from .element_map import elemIdToSymbol

_MODULE_DIR = Path(__file__).parent

if sys.platform == "win32":
    _LIB_NAME = "miedema_core.pyd"
else:
    _LIB_NAME = "miedema_core.so"
_LIB_PATH = _MODULE_DIR / "lib" / _LIB_NAME
_spec = importlib.util.spec_from_file_location("miedema_core", _LIB_PATH)
assert _spec is not None and _spec.loader is not None
_miedema_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_miedema_core)

with open(_MODULE_DIR / "config.toml", "rb") as _f:
    MODULE_INFO = tomllib.load(_f)


class MiedemaCalc:
    _DEFAULT_A = 0.73
    _Q_OVER_P = 9.4
    _P_MAP: dict[int, float] = {2: 14.1, 1: 12.3, 0: 10.6}

    def __init__(self):
        self._element_data: dict[int, dict] = {}
        self._loadElementDataFromCSV()

    def _loadElementDataFromCSV(self) -> None:
        csv_path = _MODULE_DIR / MODULE_INFO["data"]["csv"]
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                elem_id = int(row["element_id"])
                self._element_data[elem_id] = {
                    "is_transition_metal": row["is_transition_metal"] == "1",
                    "n_ws_13": float(row["n_ws_13"]),
                    "phi": float(row["phi"]),
                    "v_23": float(row["v_23"]),
                    "mu": float(row["mu"]),
                    "r_over_p": float(row["r_over_p"]) if row["r_over_p"] else 0.0,
                }

    def _getElementProperties(self, elem_id: int):
        if elem_id not in self._element_data:
            raise ValueError(f"Element data not found for elem_id: {elem_id}")
        data = self._element_data[elem_id]
        return _miedema_core.ElementProperties(
            data["v_23"],
            data["phi"],
            data["n_ws_13"],
            data["mu"],
        )

    def _getMiedemaConst(self, elem_A: int, elem_B: int):
        """
        Select Miedema constants based on element pair types.

        The constants p, q, and r/p depend on whether each element
        is a transition metal:

        | t_count | p    | q = 9.4*p | r/p                    |
        |---------|------|-----------|-------------------------|
        | 0 (both non-TM) | 10.6 | 99.64   | 0                      |
        | 1 (one TM)     | 12.3 | 115.62  | r_over_p_A * r_over_p_B |
        | 2 (both TM)    | 14.1 | 132.54  | 0                      |

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B

        Returns:
            C++ MiedemaConst struct with a, p, q, r_over_p
        """
        is_TM_A = self._element_data[elem_A]["is_transition_metal"]
        is_TM_B = self._element_data[elem_B]["is_transition_metal"]
        t_count = int(is_TM_A) + int(is_TM_B)

        p = self._P_MAP[t_count]
        q = self._Q_OVER_P * p

        if t_count == 1:
            r_over_p = (
                self._element_data[elem_A]["r_over_p"]
                * self._element_data[elem_B]["r_over_p"]
            )
        else:
            r_over_p = 0.0

        return _miedema_core.MiedemaConst(
            self._DEFAULT_A,
            p,
            q,
            r_over_p,
        )

    def calculateSingle(self, elem_A: int, elem_B: int, x_A: float) -> dict:
        """
        Calculate enthalpy of mixing at a single composition.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            x_A: Mole fraction of element A (0 ≤ x_A ≤ 1)

        Returns:
            Dictionary containing:
            - conditions: Element symbols for A and B
            - values: Single data point with x_A and ΔH_mix
            - unit: Units for each variable
            - latex: LaTeX representations for display
            - method: "Miedema"

        Raises:
            ValueError: If x_A is outside [0, 1]
        """
        if not 0 <= x_A <= 1:
            raise ValueError(f"x_A must be in [0, 1], got {x_A}")

        elem_props_A = self._getElementProperties(elem_A)
        elem_props_B = self._getElementProperties(elem_B)
        miedema_const = self._getMiedemaConst(elem_A, elem_B)

        core = _miedema_core.MiedemaCore(elem_props_A, elem_props_B, miedema_const)
        value = core.calculateSingle(x_A)

        cfg = MODULE_INFO["calculateSingle"]
        output_symbol = cfg["outputs"]["symbol"][0]
        inputs_latex = cfg["inputs"]["latex"]
        return {
            "conditions": {
                "elem_A": elemIdToSymbol(elem_A),
                "elem_B": elemIdToSymbol(elem_B),
            },
            "values": [{"x_A": x_A, output_symbol: value}],
            "units": {
                "x_A": "",
                output_symbol: cfg["outputs"]["unit"][output_symbol],
            },
            "latex": {
                "elem_A": inputs_latex["elem_A"],
                "elem_B": inputs_latex["elem_B"],
                "x_A": inputs_latex["x_A"],
                output_symbol: cfg["outputs"]["latex"][output_symbol],
            },
            "dims": ["x_A", output_symbol],
            "main_dim": output_symbol,
            "method": "Miedema",
        }

    def calculateRange(
        self,
        elem_A: int,
        elem_B: int,
        x_A_start: float,
        x_A_end: float,
        n_points: int,
    ) -> dict:
        """
        Calculate enthalpy of mixing over a composition range.

        Generates a series of ΔH_mix values at evenly spaced compositions
        between x_A_start and x_A_end (inclusive).

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            x_A_start: Starting mole fraction of A (0 ≤ x_A_start ≤ 1)
            x_A_end: Ending mole fraction of A (0 ≤ x_A_end ≤ 1)
            n_points: Number of data points to generate (n_points ≥ 1)

        Returns:
            Dictionary containing:
            - conditions: Element symbols for A and B
            - values: Array of {x_A, ΔH_mix} data points
            - unit: Units for each variable
            - latex: LaTeX representations for display
            - method: "Miedema"

        Raises:
            ValueError: If any composition is outside [0, 1] or n_points < 1
        """
        if not 0 <= x_A_start <= 1:
            raise ValueError(f"x_A_start must be in [0, 1], got {x_A_start}")
        if not 0 <= x_A_end <= 1:
            raise ValueError(f"x_A_end must be in [0, 1], got {x_A_end}")
        if n_points < 1:
            raise ValueError(f"n_points must be >= 1, got {n_points}")

        elem_props_A = self._getElementProperties(elem_A)
        elem_props_B = self._getElementProperties(elem_B)
        miedema_const = self._getMiedemaConst(elem_A, elem_B)

        core = _miedema_core.MiedemaCore(elem_props_A, elem_props_B, miedema_const)
        raw_results = core.calculateRange(x_A_start, x_A_end, n_points)

        cfg = MODULE_INFO["calculateRange"]
        output_symbol = cfg["outputs"]["symbol"][0]
        inputs_latex = cfg["inputs"]["latex"]
        values = [
            {"x_A": x_A, output_symbol: value}
            for x_A, value in zip(
                self._generateXPoints(x_A_start, x_A_end, n_points),
                raw_results,
            )
        ]

        return {
            "conditions": {
                "elem_A": elemIdToSymbol(elem_A),
                "elem_B": elemIdToSymbol(elem_B),
            },
            "values": values,
            "units": {
                "x_A": "",
                output_symbol: cfg["outputs"]["unit"][output_symbol],
            },
            "latex": {
                "elem_A": inputs_latex["elem_A"],
                "elem_B": inputs_latex["elem_B"],
                "x_A": inputs_latex["x_A"],
                output_symbol: cfg["outputs"]["latex"][output_symbol],
            },
            "dims": ["x_A", output_symbol],
            "main_dim": output_symbol,
            "method": "Miedema",
        }

    def calculateSingleBatch(
        self, elem_A: int, elem_B: int, x_array: list[float]
    ) -> dict:
        """
        Calculate enthalpy of mixing for an array of compositions.

        This method is designed for batch processing, typically called
        by other modules (e.g., Toop) via the Provider pattern.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            x_array: Array of mole fractions of element A

        Returns:
            Dictionary containing:
            - values: Array of property values (list[float])
            - method: "Miedema"
        """
        elem_props_A = self._getElementProperties(elem_A)
        elem_props_B = self._getElementProperties(elem_B)
        miedema_const = self._getMiedemaConst(elem_A, elem_B)

        core = _miedema_core.MiedemaCore(elem_props_A, elem_props_B, miedema_const)

        raw_results = core.calculateSingleBatch(x_array)

        return {
            "values": raw_results,
            "method": "Miedema",
        }

    def _generateXPoints(
        self, x_A_start: float, x_A_end: float, n_points: int
    ) -> list[float]:
        """
        Generate evenly spaced composition points.

        Uses linear interpolation from x_A_start to x_A_end.
        The last point is always exactly x_A_end to ensure precision.

        Args:
            x_A_start: Starting composition
            x_A_end: Ending composition
            n_points: Number of points (n_points ≥ 1)

        Returns:
            List of n_points evenly spaced compositions
        """
        if n_points == 1:
            return [x_A_start]
        step = (x_A_end - x_A_start) / (n_points - 1)
        return [x_A_start + i * step for i in range(n_points)]


class MiedemaProvider:
    """
    BinaryDataProvider implementation using Miedema calculations.

    This provider is designed for use by modules like Toop that need
    binary property data (Z_AB, Z_AC, Z_BC) as input.
    """

    def __init__(self, module_service):
        self._module_service = module_service

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
        result = self._module_service.callMethod(
            "miedema_module",
            "calculateSingleBatch",
            elem_A=elem_1,
            elem_B=elem_2,
            x_array=x_array,
        )
        return result["values"]


def createMiedemaProvider(module_service) -> MiedemaProvider:
    """
    Factory function to create a MiedemaProvider.

    Usage:
        provider = createMiedemaProvider(module_service)
        toop = ToopCalc(provider)
    """
    return MiedemaProvider(module_service)
