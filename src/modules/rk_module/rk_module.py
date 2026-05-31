from dataclasses import dataclass
from typing import TypedDict, Callable
import numpy as np
import logging


RK_CENTER = 0.5
WEIGHT_EPSILON = 1e-10
_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataPoint:
    features: tuple[float, ...]
    target: float
    variance: float | None = None


class LCoeffsDict(TypedDict):
    coeffs: list[float]
    order: int


class SigmaLDict(TypedDict):
    Sigma_L: list[list[float]]
    n_params: int


class RKCalc:
    def __init__(self):
        self._is_fitted = False
        self._order = 2
        self._L_coeffs: list[float] | None = None
        self._Sigma_L: list[list[float]] | None = None
        self._X_design: np.ndarray | None = None
        self._effective_order: int = 2
        self._warning_reason: str | None = None

    def fit(
        self,
        points: list[DataPoint],
        order: int = 2,
        use_variance_weighting: bool = True,
    ) -> dict:
        if not points:
            raise ValueError("points cannot be empty")

        self._order = order
        effective_order, warning_reason = self._detectCollinearity(points, order)
        self._effective_order = effective_order
        self._warning_reason = warning_reason

        if warning_reason:
            _logger.warning(f"RK auto-adjust: {warning_reason}")

        self._fitWLS(points, use_variance_weighting)
        self._is_fitted = True
        return {
            "status": "fitted",
            "n_points": len(points),
            "order": order,
            "effective_order": self._effective_order,
            "n_params": (self._effective_order + 1) * 2,
            "warning": warning_reason,
        }

    def _detectCollinearity(
        self, points: list[DataPoint], requested_order: int
    ) -> tuple[int, str | None]:
        x_vals = set(p.features[0] for p in points)
        T_vals = set(p.features[1] for p in points)

        x_unique = len(x_vals)
        T_unique = len(T_vals)

        if x_unique == 1 and T_unique == 1:
            raise ValueError(
                "Need both x and T variation - only one unique point provided"
            )

        if x_unique == 1:
            return (
                0,
                f"x is fixed (single value), using order=0 (temperature term only)",
            )

        if T_unique == 1:
            max_order = min(requested_order, 1)
            if requested_order > 1:
                return (
                    max_order,
                    f"T is fixed, capping order from {requested_order} to {max_order}",
                )
            return max_order, None

        return requested_order, None

    def _fitWLS(self, points: list[DataPoint], use_variance_weighting: bool) -> None:
        n_points = len(points)
        n_params = (self._effective_order + 1) * 2

        X_design = self._buildDesignMatrix(points)
        y = np.array([p.target for p in points])

        if use_variance_weighting:
            variances = np.array(
                [p.variance if p.variance is not None else 1.0 for p in points]
            )
            weights = 1.0 / (variances + WEIGHT_EPSILON)
        else:
            weights = np.ones(n_points)

        W = np.diag(weights)
        self._X_design = X_design

        XtWX = X_design.T @ W @ X_design
        XtWy = X_design.T @ W @ y

        lambda_reg = 1e-3
        XtWX_reg = XtWX + lambda_reg * np.eye(n_params)
        coeffs = np.linalg.solve(XtWX_reg, XtWy)
        self._L_coeffs = coeffs.tolist()

        if use_variance_weighting:
            y_pred = X_design @ coeffs
            residuals_vec = y - y_pred
            weighted_residuals = np.sqrt(weights) * residuals_vec
            RSS = np.sum(weighted_residuals**2)
            dof = n_points - n_params
            if dof > 0:
                noise_variance = RSS / dof
            else:
                noise_variance = 1.0
        else:
            y_pred = X_design @ coeffs
            residuals_vec = y - y_pred
            RSS = np.sum(residuals_vec**2)
            dof = n_points - n_params
            noise_variance = RSS / dof if dof > 0 else 1.0

        XtWX_inv = np.linalg.inv(XtWX_reg)
        self._Sigma_L = noise_variance * XtWX_inv

    def _buildDesignMatrix(self, points: list[DataPoint]) -> np.ndarray:
        n_points = len(points)
        n_params = (self._effective_order + 1) * 2
        X = np.zeros((n_points, n_params))

        for i, dp in enumerate(points):
            f0 = dp.features[0]
            f1 = dp.features[1]
            delta = 2 * (f0 - RK_CENTER)
            factor = f0 * (1 - f0)
            for k in range(self._effective_order + 1):
                X[i, 2 * k] = delta**k * factor
                X[i, 2 * k + 1] = delta**k * f1 * factor

        return X

    def evaluate(
        self, features: tuple[float, ...], L_coeffs: list[float] | None = None
    ) -> float:
        if L_coeffs is None:
            if not self._is_fitted:
                raise RuntimeError("RK model must be fitted before evaluation")
            L_coeffs = self._L_coeffs

        f0 = features[0]
        f1 = features[1]
        delta = 2 * (f0 - RK_CENTER)

        polynomial = 0.0
        for k in range(self._effective_order + 1):
            a_k = L_coeffs[2 * k]
            b_k = L_coeffs[2 * k + 1]
            L_k = a_k + b_k * f1
            polynomial += L_k * delta**k

        return f0 * (1 - f0) * polynomial

    def dG_E_df0(
        self, features: tuple[float, ...], L_coeffs: list[float] | None = None
    ) -> float:
        if L_coeffs is None:
            if not self._is_fitted:
                raise RuntimeError("RK model must be fitted before evaluation")
            L_coeffs = self._L_coeffs

        f0 = features[0]
        f1 = features[1]
        delta = 2 * (f0 - RK_CENTER)

        L_vals = [
            L_coeffs[2 * k] + L_coeffs[2 * k + 1] * f1
            for k in range(self._effective_order + 1)
        ]
        poly = sum(L_vals[k] * (delta**k) for k in range(self._effective_order + 1))

        term1 = (1 - 2 * f0) * poly

        term2 = 0.0
        for k in range(1, self._effective_order + 1):
            term2 += L_vals[k] * k * (delta ** (k - 1))
        term2 *= f0 * (1 - f0) * 2

        return term1 + term2

    def dG_E_df1(
        self, features: tuple[float, ...], L_coeffs: list[float] | None = None
    ) -> float:
        if L_coeffs is None:
            if not self._is_fitted:
                raise RuntimeError("RK model must be fitted before evaluation")
            L_coeffs = self._L_coeffs

        f0 = features[0]
        delta = 2 * (f0 - RK_CENTER)

        result = 0.0
        for k in range(1, self._effective_order + 1):
            b_k = L_coeffs[2 * k + 1]
            result += k * (delta ** (k - 1)) * 2 * b_k

        result *= f0 * (1 - f0)

        return result

    def getLCoefficients(self) -> LCoeffsDict | None:
        if not self._is_fitted:
            return None
        return {
            "coeffs": self._L_coeffs,
            "order": self._effective_order,
        }

    def getSigmaL(self) -> SigmaLDict | None:
        if not self._is_fitted:
            return None
        return {
            "Sigma_L": self._Sigma_L,
            "n_params": (self._effective_order + 1) * 2,
        }

    def sampleL(self, n_samples: int = 1000) -> dict:
        if not self._is_fitted:
            raise RuntimeError("RK model must be fitted before sampling")

        L_coeffs_mean = np.array(self._L_coeffs)
        Sigma_L = np.array(self._Sigma_L)

        L_samples = np.random.multivariate_normal(
            L_coeffs_mean, Sigma_L, size=n_samples
        )

        return {
            "L_samples": L_samples.tolist(),
            "L_mean": L_coeffs_mean.tolist(),
            "n_samples": n_samples,
        }

    @staticmethod
    def from_L(
        L_coeffs: list[float],
    ) -> tuple[Callable[[float, float], float], Callable[[float, float], float]]:
        order = (len(L_coeffs) // 2) - 1

        def GE_func(x: float, T: float) -> float:
            delta = 2 * (x - RK_CENTER)
            polynomial = 0.0
            for k in range(order + 1):
                a_k = L_coeffs[2 * k]
                b_k = L_coeffs[2 * k + 1]
                L_k = a_k + b_k * T
                polynomial += L_k * delta**k
            return x * (1 - x) * polynomial

        def dGE_dx_func(x: float, T: float) -> float:
            delta = 2 * (x - RK_CENTER)
            L_vals = [
                L_coeffs[2 * k] + L_coeffs[2 * k + 1] * T for k in range(order + 1)
            ]
            poly = sum(L_vals[k] * (delta**k) for k in range(order + 1))
            term1 = (1 - 2 * x) * poly
            term2 = 0.0
            for k in range(1, order + 1):
                term2 += L_vals[k] * k * (delta ** (k - 1))
            term2 *= x * (1 - x) * 2
            return term1 + term2

        return GE_func, dGE_dx_func

    def get_GE_functions(self):
        if not self._is_fitted:
            raise RuntimeError("RK model must be fitted before getting GE functions")

        def GE_func(x: float, T: float) -> float:
            delta = 2 * (x - RK_CENTER)
            polynomial = 0.0
            for k in range(self._effective_order + 1):
                a_k = self._L_coeffs[2 * k]
                b_k = self._L_coeffs[2 * k + 1]
                L_k = a_k + b_k * T
                polynomial += L_k * delta**k
            return x * (1 - x) * polynomial

        def dGE_dx_func(x: float, T: float) -> float:
            delta = 2 * (x - RK_CENTER)
            L_vals = [
                self._L_coeffs[2 * k] + self._L_coeffs[2 * k + 1] * T
                for k in range(self._effective_order + 1)
            ]
            poly = sum(L_vals[k] * (delta**k) for k in range(self._effective_order + 1))
            term1 = (1 - 2 * x) * poly
            term2 = 0.0
            for k in range(1, self._effective_order + 1):
                term2 += L_vals[k] * k * (delta ** (k - 1))
            term2 *= x * (1 - x) * 2
            return term1 + term2

        return GE_func, dGE_dx_func
