from dataclasses import dataclass
from typing import TypedDict
import logging
import numpy as np


R_GAS = 8.314462618
_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ArrheniusParams:
    eta_0: float
    E_a: float


class ArrheniusResultDict(TypedDict):
    eta_0: float
    E_a: float
    residuals: list[float]
    n_points: int


class ArrheniusCalc:
    def __init__(self, log_service=None):
        self._logger = log_service or logging.getLogger(__name__)
        self._params: ArrheniusParams | None = None
        self._is_fitted = False

    def fit(
        self, eta_exp: list[tuple[float, float]], order: int = 1
    ) -> ArrheniusResultDict:
        if not eta_exp:
            raise ValueError("eta_exp cannot be empty")

        y_data = np.array([np.log(eta) for eta, T in eta_exp])
        x_data = np.array([1.0 / T for eta, T in eta_exp])

        coeffs = np.polyfit(x_data, y_data, order)

        E_a = -coeffs[0] * R_GAS
        ln_eta_0 = coeffs[1]
        eta_0 = np.exp(ln_eta_0)
        self._params = ArrheniusParams(eta_0=eta_0, E_a=E_a)
        self._is_fitted = True

        residuals = []
        for (eta, T), coef in zip(eta_exp, np.polyval(coeffs, x_data)):
            residuals.append(np.log(eta) - coef)

        self._logger.debug(
            "Fitted Arrhenius: eta_0=%.6e, E_a=%.1f J/mol, n_points=%d",
            eta_0,
            E_a,
            len(eta_exp),
        )
        return {
            "eta_0": eta_0,
            "E_a": E_a,
            "residuals": residuals,
            "n_points": len(eta_exp),
        }

    def predict(self, T: float) -> float:
        if not self._is_fitted:
            raise RuntimeError("Arrhenius model must be fitted before prediction")
        return self._params.eta_0 * np.exp(self._params.E_a / (R_GAS * T))

    def get_params(self) -> ArrheniusParams | None:
        return self._params

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted
