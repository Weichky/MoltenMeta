"""
Abstract base class for geometric model calculators.

Provides common infrastructure for all geometric models (Kohler, Toop, Maggianu, Hillert-Toop).
"""

from abc import ABC, abstractmethod
from typing import TypedDict

from ..element_map.element_map import elemIdToSymbol
from ..grid_module.grid import generateTriangularGrid


class EmptyResultDict(TypedDict):
    conditions: dict
    values: list
    units: dict
    latex: dict
    dims: list[str]
    main_dim: str
    method: str


class GeometricModelCalculator(ABC):
    """Base class for ternary geometric model calculators.

    Subclasses must implement:
    - calculatePropertyList() - the actual calculation algorithm
    - _getMethodName() - return the method name string (e.g. "Kohler")
    """

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

    def _emptyResult(
        self,
        elem_A: int,
        elem_B: int,
        elem_C: int,
        cfg: dict,
        extra_conditions: dict | None = None,
    ) -> EmptyResultDict:
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
            "method": self._getMethodName(),
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
        """Calculate ternary property from binary values.

        Parameter Order Convention: AB -> AC -> BC (alphabetical)
            - x_A_list, x_B_list, x_C_list: mole fractions (same length)
            - Z_AB_list: binary property at AB composition
            - Z_AC_list: binary property at AC composition
            - Z_BC_list: binary property at BC composition
        """
        if len(Z_AB_list) != len(x_A_list):
            raise ValueError(
                f"Z_AB_list length {len(Z_AB_list)} must match x_A_list length {len(x_A_list)}"
            )
        if len(Z_AC_list) != len(x_A_list):
            raise ValueError(
                f"Z_AC_list length {len(Z_AC_list)} must match x_A_list length {len(x_A_list)}"
            )
        if len(Z_BC_list) != len(x_A_list):
            raise ValueError(
                f"Z_BC_list length {len(Z_BC_list)} must match x_A_list length {len(x_A_list)}"
            )
        return self._calculatePropertyListImpl(
            x_A_list, x_B_list, x_C_list, Z_AB_list, Z_AC_list, Z_BC_list
        )

    @abstractmethod
    def _calculatePropertyListImpl(
        self,
        x_A_list: list[float],
        x_B_list: list[float],
        x_C_list: list[float],
        Z_AB_list: list[float],
        Z_AC_list: list[float],
        Z_BC_list: list[float],
    ) -> list[float]:
        """Internal implementation of ternary property calculation. Must be implemented by subclass."""
        ...

    @abstractmethod
    def _getMethodName(self) -> str:
        """Return the method name (e.g. 'Kohler', 'Toop', 'Maggianu')."""
        ...
