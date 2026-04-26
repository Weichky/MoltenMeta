import sys
import importlib.util
from pathlib import Path

_MODULE_DIR = Path(__file__).parent

if sys.platform == "win32":
    _GRID_EXT = "triangular_grid.pyd"
else:
    _GRID_EXT = "triangular_grid.so"

_spec_grid = importlib.util.spec_from_file_location(
    "triangular_grid", _MODULE_DIR / "lib" / _GRID_EXT
)
assert _spec_grid is not None and _spec_grid.loader is not None
_triangular_grid = importlib.util.module_from_spec(_spec_grid)
_spec_grid.loader.exec_module(_triangular_grid)


def generateTriangularGrid(
    n_points: int,
) -> tuple[list[float], list[float], list[float]]:
    """Generate triangular grid points on x_A + x_B + x_C = 1.

    Args:
        n_points: Number of points per edge of the triangle

    Returns:
        tuple of (x_A_list, x_B_list, x_C_list) where each is a list of floats
    """
    if n_points <= 0:
        return [], [], []
    if n_points == 1:
        return [0.0], [0.0], [1.0]
    x_A_arr, x_B_arr, x_C_arr = _triangular_grid.generateTriangularGrid(n_points)
    return list(x_A_arr), list(x_B_arr), list(x_C_arr)


__all__ = ["generateTriangularGrid"]
