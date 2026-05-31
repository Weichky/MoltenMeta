from dataclasses import dataclass
import logging


_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SurfaceWorkflowParams:
    order: int = 2
    L_coeffs: list[float] | None = None
    Sigma_L: list[list[float]] | None = None


@dataclass
class SurfaceWorkflowResult:
    status: str
    elem_A: int
    elem_B: int
    L_coeffs: list[float]
    Sigma_L: list[list[float]] | None = None


class SurfaceWorkflowCalc:
    def __init__(self, module_service=None, log_service=None):
        self._logger = log_service or logging.getLogger(__name__)
        self._module_service = module_service
        self._butler_calc = None
        self._is_fitted = False
        self._params: SurfaceWorkflowParams = SurfaceWorkflowParams()
        self._elem_A = 0
        self._elem_B = 0

    def setModuleService(self, module_service) -> None:
        self._module_service = module_service

    def fit(
        self,
        elem_A: int,
        elem_B: int,
        L_coeffs: list[float],
        order: int = 2,
    ) -> dict:
        self._elem_A = elem_A
        self._elem_B = elem_B
        self._params = SurfaceWorkflowParams(order=order, L_coeffs=L_coeffs)

        from modules.rk_module import RKCalc

        GE_func, dGE_dx_func = RKCalc.from_L(L_coeffs)

        from modules.butler_module import ButlerCalc, ButlerConfig, ButlerGEFunctions

        def sigma_i_func(elem, T):
            return 1.0

        def density_func(elem, T):
            return 2500.0

        def element_props_get_M(elem):
            return 0.027

        config = ButlerConfig(
            sigma_i_func=sigma_i_func,
            density_func=density_func,
            element_props_get_M=element_props_get_M,
            elem_A=elem_A,
            elem_B=elem_B,
        )

        self._butler_calc = ButlerCalc(
            GE_functions=ButlerGEFunctions(
                GE_func=GE_func,
                dGE_dx_func=dGE_dx_func,
            )
        )
        self._butler_calc.fit(config)

        self._is_fitted = True
        self._logger.info(
            "SurfaceWorkflow fitted: elem_A=%d, elem_B=%d, L_coeffs_len=%d",
            elem_A,
            elem_B,
            len(L_coeffs),
        )

        return {
            "status": "fitted",
            "elem_A": elem_A,
            "elem_B": elem_B,
            "L_coeffs": L_coeffs,
        }

    def predict(self, T: float, x_bulk_A: float) -> dict:
        if not self._is_fitted or self._butler_calc is None:
            raise RuntimeError("SurfaceWorkflow must be fitted before prediction")

        result = self._butler_calc.solve(T, x_bulk_A)

        return {
            "sigma": result["sigma"],
            "x_A_surface": result["x_A_surface"],
            "x_B_surface": result["x_B_surface"],
            "success": result["success"],
            "T": T,
            "x_bulk_A": x_bulk_A,
        }

    def predictCurve(self, T: float, n_points: int = 21) -> dict:
        if not self._is_fitted or self._butler_calc is None:
            raise RuntimeError("SurfaceWorkflow must be fitted before prediction")

        x_bulk_A = []
        sigma = []
        x_A_surface = []
        x_B_surface = []

        for i in range(n_points):
            x = float(i) / float(n_points - 1)
            result = self._butler_calc.solve(T, x)
            x_bulk_A.append(x)
            sigma.append(result["sigma"])
            x_A_surface.append(result["x_A_surface"])
            x_B_surface.append(result["x_B_surface"])

        self._logger.info(
            "SurfaceWorkflow predictCurve: T=%.1f, n_points=%d, sigma_range=[%.4f, %.4f]",
            T,
            n_points,
            min(sigma),
            max(sigma),
        )

        return {
            "T": T,
            "x_bulk_A": x_bulk_A,
            "sigma": sigma,
            "x_A_surface": x_A_surface,
            "x_B_surface": x_B_surface,
        }

    def setLCoeffs(self, L_coeffs: list[float]) -> None:
        self._params.L_coeffs = L_coeffs

    def setSigmaL(self, Sigma_L: list[list[float]]) -> None:
        self._params.Sigma_L = Sigma_L

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted
