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
import tomllib
import importlib.util
from pathlib import Path

from .element_map import elemIdToSymbol

_MODULE_DIR = Path(__file__).parent

_LIB_PATH = _MODULE_DIR / "lib" / "miedema_core.so"
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

    _OUTPUT_SYMBOL = "Delta_H_mix"
    _OUTPUT_LATEX = MODULE_INFO["calculateSingle"]["outputs"]["latex"][0]
    _OUTPUT_UNIT = MODULE_INFO["calculateSingle"]["outputs"]["unit"][0]
    _INPUT_LATEX = {
        "elem_A": MODULE_INFO["calculateSingle"]["inputs"]["latex"][0],
        "elem_B": MODULE_INFO["calculateSingle"]["inputs"]["latex"][1],
        "x_A": MODULE_INFO["calculateSingle"]["inputs"]["latex"][2],
    }

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

    def _elemIdToSymbol(self, elem_id: int) -> str:
        """
        Convert atomic number to element symbol.

        Args:
            elem_id: Atomic number (1-118)

        Returns:
            Element symbol string (e.g., "Al", "Si")
        """
        return elemIdToSymbol(elem_id)

    def _buildOutput(self, elem_A: int, elem_B: int, values: list[dict]) -> dict:
        """
        Build standardized output dictionary with complete information.

        The output structure is designed to be self-describing for the
        plotting and display subsystems:
        - conditions: Fixed parameters that define the calculation series
        - values: Array of data points
        - unit: Units for each variable
        - latex: LaTeX labels for display
        - method: Source of the calculation

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            values: List of {x_A, Delta_H_mix} dictionaries

        Returns:
            Standardized result dictionary
        """
        return {
            "conditions": {
                "elem_A": self._elemIdToSymbol(elem_A),
                "elem_B": self._elemIdToSymbol(elem_B),
            },
            "values": values,
            "unit": {
                "x_A": "",
                self._OUTPUT_SYMBOL: self._OUTPUT_UNIT,
            },
            "latex": {
                "elem_A": self._INPUT_LATEX["elem_A"],
                "elem_B": self._INPUT_LATEX["elem_B"],
                "x_A": self._INPUT_LATEX["x_A"],
                self._OUTPUT_SYMBOL: self._OUTPUT_LATEX,
            },
            "method": "Miedema",
        }

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

        return self._buildOutput(
            elem_A, elem_B, [{"x_A": x_A, self._OUTPUT_SYMBOL: value}]
        )

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

        values = [
            {"x_A": x_A, self._OUTPUT_SYMBOL: value}
            for x_A, value in zip(
                self._generateXPoints(x_A_start, x_A_end, n_points),
                raw_results,
            )
        ]

        return self._buildOutput(elem_A, elem_B, values)

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
