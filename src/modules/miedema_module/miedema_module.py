import csv
import tomllib
import importlib.util
from pathlib import Path

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
        if not 0 <= x_A <= 1:
            raise ValueError(f"x_A must be in [0, 1], got {x_A}")

        elem_props_A = self._getElementProperties(elem_A)
        elem_props_B = self._getElementProperties(elem_B)
        miedema_const = self._getMiedemaConst(elem_A, elem_B)

        core = _miedema_core.MiedemaCore(elem_props_A, elem_props_B, miedema_const)
        value = core.calculateSingle(x_A)

        return {
            "elem_A": elem_A,
            "elem_B": elem_B,
            "x_A": x_A,
            "value": value,
            "unit": "kJ/mol",
            "method": "Miedema",
        }

    def calculateRange(
        self, elem_A: int, elem_B: int, x_A_start: float, x_A_end: float, n_points: int
    ) -> list[dict]:
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

        return [
            {
                "elem_A": elem_A,
                "elem_B": elem_B,
                "x_A": x_A,
                "value": value,
                "unit": "kJ/mol",
                "method": "Miedema",
            }
            for x_A, value in zip(
                self._generateXPoints(x_A_start, x_A_end, n_points),
                raw_results,
            )
        ]

    def _generateXPoints(
        self, x_A_start: float, x_A_end: float, n_points: int
    ) -> list[float]:
        if n_points == 1:
            return [x_A_start]
        step = (x_A_end - x_A_start) / (n_points - 1)
        return [x_A_start + i * step for i in range(n_points)]
