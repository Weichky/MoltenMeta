import sys
import tomllib
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from framework.binary_provider import BinaryDataProvider

from .element_map import elemIdToSymbol
from ..grid_module.grid import generateTriangularGrid

_MODULE_DIR = Path(__file__).parent

if sys.platform == "win32":
    _ALG_EXT = "maggianu_algorithm.pyd"
else:
    _ALG_EXT = "maggianu_algorithm.so"

_spec_alg = importlib.util.spec_from_file_location(
    "maggianu_algorithm", _MODULE_DIR / "lib" / _ALG_EXT
)
assert _spec_alg is not None and _spec_alg.loader is not None
_maggianu_algorithm = importlib.util.module_from_spec(_spec_alg)
_spec_alg.loader.exec_module(_maggianu_algorithm)

with open(_MODULE_DIR / "config.toml", "rb") as _f:
    MODULE_INFO = tomllib.load(_f)


class MaggianuCalc:
    def __init__(self, binary_provider: "BinaryDataProvider | None" = None):
        self._provider = binary_provider

    def setProvider(self, provider: "BinaryDataProvider") -> None:
        self._provider = provider

    def calculateSingleProperty(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        x_A: float,
        x_B: float,
        x_C: float,
        Z_AB: float,
        Z_BC: float,
        Z_AC: float,
    ) -> dict:
        value = _maggianu_algorithm.calculateSingleProperty(
            x_A, x_B, x_C, Z_AB, Z_BC, Z_AC
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
            "method": "Maggianu",
        }

    def calculatePropertyList(
        self,
        x_A_list: list[float],
        x_B_list: list[float],
        x_C_list: list[float],
        Z_AB_list: list[float],
        Z_BC_list: list[float],
        Z_AC_list: list[float],
    ) -> list[float]:
        """Call C++ batch calculation."""
        import numpy as np

        x_A_arr = np.array(x_A_list, dtype=np.float64)
        x_B_arr = np.array(x_B_list, dtype=np.float64)
        x_C_arr = np.array(x_C_list, dtype=np.float64)
        Z_AB_arr = np.array(Z_AB_list, dtype=np.float64)
        Z_BC_arr = np.array(Z_BC_list, dtype=np.float64)
        Z_AC_arr = np.array(Z_AC_list, dtype=np.float64)

        result = _maggianu_algorithm.calculatePropertyList(
            x_A_arr, x_B_arr, x_C_arr, Z_AB_arr, Z_BC_arr, Z_AC_arr
        )
        return result.tolist()

    def _generateGrid(
        self, n_points: int
    ) -> tuple[list[float], list[float], list[float]]:
        """Generate triangular grid points on x_A + x_B + x_C = 1 via C++."""
        if n_points <= 0:
            return [], [], []
        if n_points == 1:
            return [0.0], [0.0], [1.0]
        x_A_arr, x_B_arr, x_C_arr = generateTriangularGrid(n_points)
        return list(x_A_arr), list(x_B_arr), list(x_C_arr)

    def calculateScatter(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        n_points: int = 50,
        z_symbol: str | None = None,
    ) -> dict:
        """
        Calculate Kohler model for a triangular grid.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            elem_C: Atomic number of element C
            n_points: Number of points per edge (total ~ n_points^2/2)
            z_symbol: Output symbol name (e.g. "Delta_H_mix"). If None, uses config default.

        Returns:
            Dictionary containing calculation results
        """
        if n_points < 0:
            raise ValueError(f"n_points must be non-negative, got {n_points}")

        if self._provider is None:
            raise RuntimeError("No BinaryDataProvider configured for KohlerCalc")

        x_A_list, x_B_list, x_C_list = self._generateGrid(n_points)

        if not x_A_list:
            return self._emptyResult(
                elem_A,
                elem_B,
                elem_C,
                MODULE_INFO["calculateScatter"],
                extra_conditions={"output_symbol": z_symbol} if z_symbol else None,
            )

        V_AB_list = [(1.0 + x_A - x_B) / 2.0 for x_A, x_B in zip(x_A_list, x_B_list)]
        Z_AB_list = self._provider.get_values(elem_A, elem_B, V_AB_list)
        if len(Z_AB_list) != len(V_AB_list):
            raise ValueError(
                f"Provider Z_AB returned {len(Z_AB_list)} values, expected {len(V_AB_list)}"
            )

        V_BC_list = [(1.0 + x_B - x_C) / 2.0 for x_B, x_C in zip(x_B_list, x_C_list)]
        Z_BC_list = self._provider.get_values(elem_B, elem_C, V_BC_list)
        if len(Z_BC_list) != len(V_BC_list):
            raise ValueError(
                f"Provider Z_BC returned {len(Z_BC_list)} values, expected {len(V_BC_list)}"
            )

        V_AC_list = [(1.0 + x_A - x_C) / 2.0 for x_A, x_C in zip(x_A_list, x_C_list)]
        Z_AC_list = self._provider.get_values(elem_A, elem_C, V_AC_list)
        if len(Z_AC_list) != len(V_AC_list):
            raise ValueError(
                f"Provider Z_AC returned {len(Z_AC_list)} values, expected {len(V_AC_list)}"
            )

        Z_ABC_list = self.calculatePropertyList(
            x_A_list, x_B_list, x_C_list, Z_AB_list, Z_BC_list, Z_AC_list
        )

        cfg = MODULE_INFO["calculateScatter"]
        output_symbol = z_symbol or cfg["outputs"]["symbol"][0]

        values = [
            {output_symbol: z, "x_A": a, "x_B": b, "x_C": c}
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
                output_symbol: cfg["outputs"]["unit"].get(
                    output_symbol,
                    cfg["outputs"]["unit"].get(cfg["outputs"]["symbol"][0], ""),
                ),
            },
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: cfg["outputs"]["latex"].get(
                    output_symbol,
                    cfg["outputs"]["latex"].get(cfg["outputs"]["symbol"][0], ""),
                ),
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "main_dim": output_symbol,
            "method": "Maggianu",
        }

    def calculateContour(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        plane: str,
        n_points: int = 50,
    ) -> dict:
        """
        Calculate contour data for x_i-x_j plane.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            elem_C: Atomic number of element C
            plane: Projection plane - "x_A-x_B", "x_A-x_C", or "x_B-x_C"
            n_points: Number of points per axis (grid will be n_points x n_points)

        Returns:
            Dictionary containing meshgrid data for contour plotting:
            - x_i, x_j: 2D arrays forming the meshgrid
            - Z_ABC: 2D array of calculated values
            - plane: The projection plane used

        Note: Returns meshgrid format (not point-wise) because contourf requires
              structured grid data. This is a special case for visualization.
        """
        if n_points < 0:
            raise ValueError(f"n_points must be non-negative, got {n_points}")

        if plane not in ("x_A-x_B", "x_A-x_C", "x_B-x_C"):
            raise ValueError(f"plane must be x_A-x_B, x_A-x_C, or x_B-x_C, got {plane}")

        if self._provider is None:
            raise RuntimeError("No BinaryDataProvider configured for KohlerCalc")

        if n_points == 0:
            return {
                "conditions": {
                    "elem_A": elemIdToSymbol(elem_A),
                    "elem_B": elemIdToSymbol(elem_B),
                    "elem_C": elemIdToSymbol(elem_C),
                    "plane": plane,
                },
                "x_i": [],
                "x_j": [],
                "Z_ABC": [],
                "plane": plane,
            }

        import numpy as np

        if plane == "x_A-x_B":
            x_i_arr = np.linspace(0, 1, n_points)
            x_j_arr = np.linspace(0, 1, n_points)
            x_i_mesh, x_j_mesh = np.meshgrid(x_i_arr, x_j_arr)

            x_A_flat = x_i_mesh.flatten()
            x_B_flat = x_j_mesh.flatten()
            x_C_flat = 1 - x_A_flat - x_B_flat

            valid_mask = x_C_flat >= 0
            x_A_flat = x_A_flat[valid_mask]
            x_B_flat = x_B_flat[valid_mask]
            x_C_flat = x_C_flat[valid_mask]

        elif plane == "x_A-x_C":
            x_i_arr = np.linspace(0, 1, n_points)
            x_j_arr = np.linspace(0, 1, n_points)
            x_i_mesh, x_j_mesh = np.meshgrid(x_i_arr, x_j_arr)

            x_A_flat = x_i_mesh.flatten()
            x_C_flat = x_j_mesh.flatten()
            x_B_flat = 1 - x_A_flat - x_C_flat

            valid_mask = x_B_flat >= 0
            x_A_flat = x_A_flat[valid_mask]
            x_B_flat = x_B_flat[valid_mask]
            x_C_flat = x_C_flat[valid_mask]

        else:
            x_i_arr = np.linspace(0, 1, n_points)
            x_j_arr = np.linspace(0, 1, n_points)
            x_i_mesh, x_j_mesh = np.meshgrid(x_i_arr, x_j_arr)

            x_B_flat = x_i_mesh.flatten()
            x_C_flat = x_j_mesh.flatten()
            x_A_flat = 1 - x_B_flat - x_C_flat

            valid_mask = x_A_flat >= 0
            x_A_flat = x_A_flat[valid_mask]
            x_B_flat = x_B_flat[valid_mask]
            x_C_flat = x_C_flat[valid_mask]

        if len(x_A_flat) == 0:
            return {
                "conditions": {
                    "elem_A": elemIdToSymbol(elem_A),
                    "elem_B": elemIdToSymbol(elem_B),
                    "elem_C": elemIdToSymbol(elem_C),
                    "plane": plane,
                },
                "x_i": [],
                "x_j": [],
                "Z_ABC": [],
                "plane": plane,
            }

        with np.errstate(invalid="ignore"):
            V_AB_flat = np.where(
                (x_A_flat + x_B_flat) > 0,
                (1.0 + x_A_flat - x_B_flat) / 2.0,
                0.0,
            )
        Z_AB_list = self._provider.get_values(elem_A, elem_B, V_AB_flat.tolist())
        if len(Z_AB_list) != len(V_AB_flat):
            raise ValueError(
                f"Provider Z_AB returned {len(Z_AB_list)} values, expected {len(V_AB_flat)}"
            )

        with np.errstate(invalid="ignore"):
            V_BC_flat = np.where(
                (x_B_flat + x_C_flat) > 0,
                (1.0 + x_B_flat - x_C_flat) / 2.0,
                0.0,
            )
        Z_BC_list = self._provider.get_values(elem_B, elem_C, V_BC_flat.tolist())
        if len(Z_BC_list) != len(V_BC_flat):
            raise ValueError(
                f"Provider Z_BC returned {len(Z_BC_list)} values, expected {len(V_BC_flat)}"
            )

        with np.errstate(invalid="ignore"):
            V_AC_flat = np.where(
                (x_A_flat + x_C_flat) > 0,
                (1.0 + x_A_flat - x_C_flat) / 2.0,
                0.0,
            )
        Z_AC_list = self._provider.get_values(elem_A, elem_C, V_AC_flat.tolist())
        if len(Z_AC_list) != len(V_AC_flat):
            raise ValueError(
                f"Provider Z_AC returned {len(Z_AC_list)} values, expected {len(V_AC_flat)}"
            )

        Z_ABC_flat = self.calculatePropertyList(
            x_A_flat.tolist(),
            x_B_flat.tolist(),
            x_C_flat.tolist(),
            Z_AB_list,
            Z_BC_list,
            Z_AC_list,
        )

        Z_ABC_mesh = np.full_like(x_i_mesh, np.nan, dtype=float)
        Z_ABC_mesh.flat[valid_mask] = Z_ABC_flat

        return {
            "conditions": {
                "elem_A": elemIdToSymbol(elem_A),
                "elem_B": elemIdToSymbol(elem_B),
                "elem_C": elemIdToSymbol(elem_C),
                "plane": plane,
            },
            "x_i": x_i_mesh.tolist(),
            "x_j": x_j_mesh.tolist(),
            "Z_ABC": Z_ABC_mesh.tolist(),
            "plane": plane,
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
        fallback_symbol = cfg["outputs"]["symbol"][0]
        output_symbol = (
            extra_conditions.get("output_symbol", fallback_symbol)
            if extra_conditions
            else fallback_symbol
        )
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
                output_symbol: cfg["outputs"]["unit"].get(
                    output_symbol, cfg["outputs"]["unit"].get(fallback_symbol, "")
                ),
            },
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: cfg["outputs"]["latex"].get(
                    output_symbol, cfg["outputs"]["latex"].get(fallback_symbol, "")
                ),
            },
            "dims": ["x_A", "x_B", "x_C", output_symbol],
            "main_dim": output_symbol,
            "method": "Maggianu",
        }

    def calculateScatterWithData(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        n_points: int,
        Z_AB_list: list[float],
        Z_BC_list: list[float],
        Z_AC_list: list[float],
        z_latex: str,
        z_unit: str,
        z_symbol: str | None = None,
    ) -> dict:
        """
        Calculate Kohler model for a triangular grid with direct data input.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            elem_C: Atomic number of element C
            n_points: Number of points per edge
            Z_AB_list: Pre-computed binary AB values at w_AB points
            Z_BC_list: Pre-computed binary BC values at w_BC points
            Z_AC_list: Pre-computed binary AC values at w_AC points
            z_latex: LaTeX symbol for z-axis property
            z_unit: Unit for z-axis property
            z_symbol: Output symbol name (e.g. "Delta_H_mix"). If None, uses config default.

        Returns:
            Dictionary containing calculation results
        """
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

        V_AB_list = [(1.0 + x_A - x_B) / 2.0 for x_A, x_B in zip(x_A_list, x_B_list)]
        if len(Z_AB_list) != len(V_AB_list):
            raise ValueError(
                f"Z_AB_list has {len(Z_AB_list)} values, expected {len(V_AB_list)}"
            )

        V_BC_list = [(1.0 + x_B - x_C) / 2.0 for x_B, x_C in zip(x_B_list, x_C_list)]
        if len(Z_BC_list) != len(V_BC_list):
            raise ValueError(
                f"Z_BC_list has {len(Z_BC_list)} values, expected {len(V_BC_list)}"
            )

        V_AC_list = [(1.0 + x_A - x_C) / 2.0 for x_A, x_C in zip(x_A_list, x_C_list)]
        if len(Z_AC_list) != len(V_AC_list):
            raise ValueError(
                f"Z_AC_list has {len(Z_AC_list)} values, expected {len(V_AC_list)}"
            )

        Z_ABC_list = self.calculatePropertyList(
            x_A_list, x_B_list, x_C_list, Z_AB_list, Z_BC_list, Z_AC_list
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
            "method": "Maggianu",
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
        """
        Calculate contour data for x_i-x_j plane with direct data input.

        Args:
            elem_A: Atomic number of element A
            elem_B: Atomic number of element B
            elem_C: Atomic number of element C
            plane: Projection plane - "x_A-x_B", "x_A-x_C", or "x_B-x_C"
            n_points: Number of points per axis
            Z_AB_list: Pre-computed binary AB values at w_AB points
            Z_BC_list: Pre-computed binary BC values at w_BC points
            Z_AC_list: Pre-computed binary AC values at w_AC points
            z_latex: LaTeX symbol for z-axis property
            z_unit: Unit for z-axis property
            z_symbol: Output symbol name (e.g. "Delta_H_mix"). If None, uses config default.

        Returns:
            Dictionary containing meshgrid data for contour plotting
        """
        if n_points < 0:
            raise ValueError(f"n_points must be non-negative, got {n_points}")

        if plane not in ("x_A-x_B", "x_A-x_C", "x_B-x_C"):
            raise ValueError(f"plane must be x_A-x_B, x_A-x_C, or x_B-x_C, got {plane}")

        cfg = MODULE_INFO["calculateContour"]
        output_symbol = z_symbol or cfg["outputs"]["symbol"][0]
        final_latex = z_latex
        final_unit = z_unit

        if n_points == 0:
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
                    output_symbol: final_latex,
                },
                "units": {"x_A": "", "x_B": "", "x_C": "", output_symbol: final_unit},
                "x_i": [],
                "x_j": [],
                output_symbol: [],
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
                    output_symbol: final_latex,
                },
                "units": {"x_A": "", "x_B": "", "x_C": "", output_symbol: final_unit},
                "plane": plane,
            }

        V_AB_list = [(1.0 + x_A - x_B) / 2.0 for x_A, x_B in zip(x_A_list, x_B_list)]
        if len(Z_AB_list) != len(V_AB_list):
            raise ValueError(
                f"Z_AB_list has {len(Z_AB_list)} values, expected {len(V_AB_list)}"
            )

        V_BC_list = [(1.0 + x_B - x_C) / 2.0 for x_B, x_C in zip(x_B_list, x_C_list)]
        if len(Z_BC_list) != len(V_BC_list):
            raise ValueError(
                f"Z_BC_list has {len(Z_BC_list)} values, expected {len(V_BC_list)}"
            )

        V_AC_list = [(1.0 + x_A - x_C) / 2.0 for x_A, x_C in zip(x_A_list, x_C_list)]
        if len(Z_AC_list) != len(V_AC_list):
            raise ValueError(
                f"Z_AC_list has {len(Z_AC_list)} values, expected {len(V_AC_list)}"
            )

        Z_ABC_list = self.calculatePropertyList(
            x_A_list, x_B_list, x_C_list, Z_AB_list, Z_BC_list, Z_AC_list
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
                    output_symbol: final_latex,
                },
                "units": {"x_A": "", "x_B": "", "x_C": "", output_symbol: final_unit},
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
            "latex": {
                "x_A": "x_A",
                "x_B": "x_B",
                "x_C": "x_C",
                output_symbol: final_latex,
            },
            "units": {
                "x_A": "",
                "x_B": "",
                "x_C": "",
                output_symbol: final_unit,
            },
            "x_i": x_A_list,
            "x_j": x_B_list,
            output_symbol: Z_ABC_list,
            "plane": plane,
        }


def _linspace(start: float, end: float, num: int) -> list[float]:
    """Generate evenly spaced points."""
    if num <= 0:
        return []
    if num <= 1:
        return [start]
    step = (end - start) / (num - 1)
    return [start + i * step for i in range(num)]
