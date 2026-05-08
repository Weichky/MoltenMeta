"""
Butler Module - Surface tension calculation via Butler equation
Decoupled from specific thermodynamic models (RK, Miedema, etc.)
"""

from dataclasses import dataclass
from typing import TypedDict, Callable
import numpy as np


R = 8.314462618
N_A = 6.02214076e23
S_CONSTANT = 1.091
BETA = 0.75


@dataclass(frozen=True)
class ButlerGEFunctions:
    GE_func: Callable[[float, float], float]
    dGE_dx_func: Callable[[float, float], float]


@dataclass(frozen=True)
class ButlerConfig:
    sigma_i_func: Callable[[int, float], float]
    density_func: Callable[[int, float], float]
    element_props_get_M: Callable[[int], float]
    elem_A: int
    elem_B: int


class ButlerSolutionDict(TypedDict):
    sigma: float
    x_A_surface: float
    x_B_surface: float
    success: bool


class ButlerSampleDict(TypedDict):
    sigma_samples: list[float]
    x_A_samples: list[float]
    x_B_samples: list[float]
    sigma_percentiles: dict


class ButlerCalc:
    def __init__(self, GE_functions: ButlerGEFunctions):
        if GE_functions is None:
            raise ValueError("GE_functions must be provided")
        self._GE_functions = GE_functions
        self._is_fitted = False
        self._config: ButlerConfig | None = None

    def fit(self, config: ButlerConfig) -> dict:
        self._config = config
        self._is_fitted = True
        return {
            "status": "fitted",
            "elem_A": config.elem_A,
            "elem_B": config.elem_B,
        }

    def _compute_S_i(self, elem: int, T: float) -> float:
        if self._config is None:
            raise RuntimeError("Butler not fitted")

        rho = self._config.density_func(elem, T)
        M = self._config.element_props_get_M(elem)

        V_m = M / rho
        return S_CONSTANT * (N_A ** (1 / 3)) * (V_m ** (2 / 3))

    def _compute_GE_i(self, x: float, T: float) -> tuple[float, float]:
        GE = self._GE_functions.GE_func(x, T)
        dGE_dx = self._GE_functions.dGE_dx_func(x, T)
        G_E_A = GE + (1 - x) * dGE_dx
        G_E_B = GE - x * dGE_dx
        return G_E_A, G_E_B

    def _butler_equations(
        self, vars: list[float], T: float, x_bulk_A: float
    ) -> list[float]:
        if self._config is None:
            raise RuntimeError("Butler not fitted")

        sigma, x_A_s, x_B_s = vars

        x_A_s_safe = np.clip(x_A_s, 1e-10, 1 - 1e-10)
        x_B_s_safe = np.clip(x_B_s, 1e-10, 1 - 1e-10)

        sigma_A = self._config.sigma_i_func(self._config.elem_A, T)
        sigma_B = self._config.sigma_i_func(self._config.elem_B, T)

        S_A = self._compute_S_i(self._config.elem_A, T)
        S_B = self._compute_S_i(self._config.elem_B, T)

        G_E_A_bulk, G_E_B_bulk = self._compute_GE_i(x_bulk_A, T)
        G_E_A_surf_est = BETA * G_E_A_bulk
        G_E_B_surf_est = BETA * G_E_B_bulk

        eq1 = (
            sigma
            - sigma_A
            - (R * T / S_A) * np.log(x_A_s_safe / x_bulk_A)
            - (G_E_A_surf_est - G_E_A_bulk) / S_A
        )
        eq2 = (
            sigma
            - sigma_B
            - (R * T / S_B) * np.log(x_B_s_safe / (1 - x_bulk_A))
            - (G_E_B_surf_est - G_E_B_bulk) / S_B
        )
        eq3 = x_A_s_safe + x_B_s_safe - 1.0

        return [eq1, eq2, eq3]

    def _solve_butler(self, T: float, x_bulk_A: float) -> ButlerSolutionDict:
        from scipy.optimize import fsolve

        sigma_A = self._config.sigma_i_func(self._config.elem_A, T)
        sigma_B = self._config.sigma_i_func(self._config.elem_B, T)

        if x_bulk_A >= 0.9999:
            return {
                "sigma": float(sigma_A),
                "x_A_surface": 1.0,
                "x_B_surface": 0.0,
                "success": True,
            }

        if x_bulk_A <= 0.0001:
            return {
                "sigma": float(sigma_B),
                "x_A_surface": 0.0,
                "x_B_surface": 1.0,
                "success": True,
            }

        x_A_s_init = max(0.01, min(0.99, x_bulk_A))
        x_B_s_init = 1 - x_A_s_init
        sigma_init = (sigma_A + sigma_B) / 2

        initial_guess = [sigma_init, x_A_s_init, x_B_s_init]

        result = fsolve(
            lambda v: self._butler_equations(v, T, x_bulk_A),
            initial_guess,
            full_output=True,
        )

        solution = result[0]
        info = result[1]

        success = info == 1 if isinstance(info, (int, np.integer)) else True

        if not success:
            return {
                "sigma": float(sigma_init),
                "x_A_surface": float(x_A_s_init),
                "x_B_surface": float(x_B_s_init),
                "success": False,
            }

        return {
            "sigma": float(solution[0]),
            "x_A_surface": float(np.clip(solution[1], 0, 1)),
            "x_B_surface": float(np.clip(solution[2], 0, 1)),
            "success": True,
        }

    def solve(self, T: float, x_bulk_A: float) -> ButlerSolutionDict:
        if not self._is_fitted:
            raise RuntimeError("Butler model must be fitted before solving")

        return self._solve_butler(T, x_bulk_A)

    def sample(
        self,
        T: float,
        x_bulk_A: float,
        n_samples: int,
        Sigma_L: list[list[float]],
        L_coeffs: list[float],
    ) -> ButlerSampleDict:
        if not self._is_fitted:
            raise RuntimeError("Butler model must be fitted before sampling")

        L_mean = np.array(L_coeffs)
        Sigma_L = np.array(Sigma_L)

        L_samples = np.random.multivariate_normal(L_mean, Sigma_L, size=n_samples)

        sigma_samples = []
        x_A_samples = []
        x_B_samples = []

        for i in range(n_samples):
            L_sample = L_samples[i].tolist()

            def GE_wrapper(x, T, L=L_sample):
                return self._evaluate_GE_with_L(x, T, L)

            def dGE_wrapper(x, T, L=L_sample):
                return self._evaluate_dGE_dx_with_L(x, T, L)

            saved_GE_func = self._GE_functions.GE_func
            saved_dGE_func = self._GE_functions.dGE_dx_func
            self._GE_functions = ButlerGEFunctions(
                GE_func=GE_wrapper, dGE_dx_func=dGE_wrapper
            )

            result = self._solve_butler(T, x_bulk_A)
            if result["success"]:
                sigma_samples.append(result["sigma"])
                x_A_samples.append(result["x_A_surface"])
                x_B_samples.append(result["x_B_surface"])

            self._GE_functions = ButlerGEFunctions(
                GE_func=saved_GE_func, dGE_dx_func=saved_dGE_func
            )

        sigma_array = np.array(sigma_samples)

        return {
            "sigma_samples": sigma_samples,
            "x_A_samples": x_A_samples,
            "x_B_samples": x_B_samples,
            "sigma_percentiles": {
                "p5": float(np.percentile(sigma_array, 5)),
                "p50": float(np.percentile(sigma_array, 50)),
                "p95": float(np.percentile(sigma_array, 95)),
                "mean": float(np.mean(sigma_array)),
                "std": float(np.std(sigma_array)),
            },
        }

    def _evaluate_GE_with_L(self, x: float, T: float, L_coeffs: list[float]) -> float:
        order = (len(L_coeffs) // 2) - 1
        delta = 2 * (x - 0.5)
        polynomial = 0.0
        for k in range(order + 1):
            a_k = L_coeffs[2 * k]
            b_k = L_coeffs[2 * k + 1]
            L_k = a_k + b_k * T
            polynomial += L_k * delta**k
        return x * (1 - x) * polynomial

    def _evaluate_dGE_dx_with_L(
        self, x: float, T: float, L_coeffs: list[float]
    ) -> float:
        order = (len(L_coeffs) // 2) - 1
        delta = 2 * (x - 0.5)
        result = 0.0
        for k in range(1, order + 1):
            a_k = L_coeffs[2 * k]
            b_k = L_coeffs[2 * k + 1]
            L_k = a_k + b_k * T
            result += L_k * k * (delta ** (k - 1)) * 2
        result *= x * (1 - x)
        L_0 = L_coeffs[0] + L_coeffs[1] * T
        result += (1 - 2 * x) * L_0
        return result
