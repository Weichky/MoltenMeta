from dataclasses import dataclass
import logging
import numpy as np


R_GAS = 8.314462618
T_FIXED = 2033


_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ViscosityWorkflowParams:
    alpha: float = 0.01
    kernel_type: str = "rbf"
    nu: float = 1.5
    model_name: str = "hillert_toop"


class ViscosityWorkflowCalc:
    def __init__(self, module_service=None, log_service=None):
        self._logger = log_service or logging.getLogger(__name__)
        self._module_service = module_service
        self._arrhenius_params: dict[str, tuple[float, float]] = {}
        self._eta_pure: dict[str, float] = {}
        self._params = ViscosityWorkflowParams()
        self._is_fitted = False
        self._md_data: dict | None = None
        self._md_data_cartesian: dict | None = None
        self._grid_cartesian: dict | None = None

    def setModuleService(self, module_service) -> None:
        self._module_service = module_service

    def setArrheniusParams(self, params: dict[str, tuple[float, float]]) -> None:
        self._arrhenius_params = params
        self._eta_pure = {
            e: p[0] * np.exp(p[1] * 1000 / (R_GAS * T_FIXED)) for e, p in params.items()
        }

    def fit(
        self,
        ternary_data: dict,
        arrhenius_params: dict[str, tuple[float, float]] | None = None,
        params: ViscosityWorkflowParams | None = None,
    ) -> dict:
        if params is not None:
            self._params = params
        if arrhenius_params is not None:
            self.setArrheniusParams(arrhenius_params)
        if not self._arrhenius_params:
            raise ValueError("Arrhenius params required")
        if "vi" not in ternary_data:
            raise ValueError("ternary_data must contain 'vi'")

        self._md_data = {
            "x_Ti": np.array(ternary_data["x_Ti"]),
            "x_Al": np.array(ternary_data["x_Al"]),
            "x_Ni": np.array(ternary_data["x_Ni"]),
            "vi": np.array(ternary_data["vi"]),
        }

        sqrt3_2 = np.sqrt(3) / 2
        x_cart_md = self._md_data["x_Al"] + 0.5 * self._md_data["x_Ni"]
        y_cart_md = sqrt3_2 * self._md_data["x_Ni"]
        self._md_data_cartesian = {
            "x": x_cart_md,
            "y": y_cart_md,
            "vi": self._md_data["vi"],
        }

        binary_systems = [
            ("Ti-Al", "Ti", "Al"),
            ("Ti-Ni", "Ti", "Ni"),
            ("Al-Ni", "Al", "Ni"),
        ]
        self._binary_funcs = {}
        binary_results = {}
        for name, elem1, elem2 in binary_systems:
            predict_fn, bin_result = self._fit_binary_from_ternary(
                ternary_data, elem1, elem2
            )
            self._binary_funcs[name] = predict_fn
            binary_results[name] = bin_result

        x_Ti_md = self._md_data["x_Ti"]
        x_Al_md = self._md_data["x_Al"]
        x_Ni_md = self._md_data["x_Ni"]
        vi_md = self._md_data["vi"]

        eta_mix_ter = (
            x_Ti_md * self._eta_pure["Ti"]
            + x_Al_md * self._eta_pure["Al"]
            + x_Ni_md * self._eta_pure["Ni"]
        )

        vi_model = self._compute_eta_E(x_Ti_md, x_Al_md, x_Ni_md)
        vi_binary = eta_mix_ter + vi_model
        residuals = vi_md - vi_binary

        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import Matern, RBF

        X_ter = np.column_stack([x_Ti_md, x_Al_md])
        y_ter = residuals.ravel()
        Xm = X_ter.mean(axis=0)
        Xs = X_ter.std(axis=0)
        ym = y_ter.mean()
        ys = y_ter.std()
        alpha_s = self._params.alpha / (ys**2)

        if self._params.kernel_type == "rbf":
            k_ter = RBF(length_scale=[1.0, 1.0], length_scale_bounds=(1e-2, 1e2))
        else:
            k_ter = Matern(
                length_scale=[1.0, 1.0],
                nu=self._params.nu,
                length_scale_bounds=(1e-2, 1e2),
            )

        gp_ter = GaussianProcessRegressor(
            kernel=k_ter, alpha=alpha_s, n_restarts_optimizer=5, random_state=42
        )
        gp_ter.fit((X_ter - Xm) / Xs, (y_ter - ym) / ys)

        self._gp_ternary = gp_ter
        self._gp_Xm = Xm
        self._gp_Xs = Xs
        self._gp_ym = ym
        self._gp_ys = ys
        self._eta_mix_md = eta_mix_ter
        self._vi_binary_md = vi_binary
        self._vi_model_md = vi_model

        rmse = float(np.sqrt(np.mean(residuals**2)))
        r2 = float(1 - np.sum(residuals**2) / np.sum((vi_md - vi_md.mean()) ** 2))

        self._is_fitted = True
        self._logger.info(
            f"ViscosityWorkflow fitted: model={self._params.model_name}, RMSE={rmse:.4f}, R2={r2:.4f}"
        )

        return {
            "status": "fitted",
            "params": {
                "alpha": self._params.alpha,
                "kernel_type": self._params.kernel_type,
                "nu": self._params.nu,
                "model_name": self._params.model_name,
            },
            "binary_results": binary_results,
            "md_data": self._md_data,
            "rmse": rmse,
            "r2": r2,
        }

    def _fit_binary_from_ternary(
        self,
        ternary_data: dict,
        elem1: str,
        elem2: str,
    ):
        key1 = f"x_{elem1}"
        key2 = f"x_{elem2}"

        x1_list, x2_list, vi_list = [], [], []
        for i in range(len(ternary_data[key1])):
            x1_val = ternary_data[key1][i]
            x2_val = ternary_data[key2][i]
            x_sum = x1_val + x2_val
            if x_sum > 1e-10:
                x1_list.append(x1_val / x_sum)
                x2_list.append(x2_val / x_sum)
                vi_list.append(ternary_data["vi"][i])

        if not x1_list:
            raise ValueError(f"No valid binary data for {elem1}-{elem2}")

        x_arr = np.array(x1_list)
        vi_exp = np.array(vi_list)
        eta_mix = x_arr * self._eta_pure[elem1] + (1 - x_arr) * self._eta_pure[elem2]
        eta_E = vi_exp - eta_mix

        from modules.rk_module import RKCalc, DataPoint as RKDataPoint

        points = [
            RKDataPoint(features=(x, T_FIXED), target=float(e))
            for x, e in zip(x_arr, eta_E)
        ]
        rk = RKCalc()
        rk.fit(points, order=2)
        GE_func, _ = rk.get_GE_functions()
        eta_RK = np.array([GE_func(x, T_FIXED) for x in x_arr])
        residuals = eta_E - eta_RK

        X = x_arr.reshape(-1, 1)
        y = residuals.ravel()
        X_mean, X_std = X.mean(axis=0), X.std(axis=0)
        y_mean, y_std = y.mean(), y.std()
        Xs = (X - X_mean) / X_std
        ys = (y - y_mean) / y_std
        alpha_s = self._params.alpha / (y_std**2)

        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, Matern

        if self._params.kernel_type == "rbf":
            k = RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e3))
        else:
            k = Matern(
                length_scale=1.0, nu=self._params.nu, length_scale_bounds=(1e-2, 1e3)
            )

        gp = GaussianProcessRegressor(
            kernel=k, alpha=alpha_s, n_restarts_optimizer=5, random_state=42
        )
        gp.fit(Xs, ys)

        def predict_eta_E(z):
            z = np.asarray(z, dtype=float).ravel()
            rk_vals = np.array([GE_func(float(zz), T_FIXED) for zz in z])
            xs = (z.reshape(-1, 1) - X_mean) / X_std
            gp_vals = gp.predict(xs, return_std=True)[0].ravel() * y_std + y_mean
            return rk_vals + gp_vals

        vi_pred_binary = predict_eta_E(x_arr)
        resid_binary = eta_E - vi_pred_binary
        rmse_binary = float(np.sqrt(np.mean(resid_binary**2)))
        r2_binary = float(
            1 - np.sum(resid_binary**2) / np.sum((eta_E - eta_E.mean()) ** 2)
        )

        return predict_eta_E, {"rmse": rmse_binary, "r2": r2_binary}

    def _model_kohler(self, x_Ti, x_Al, x_Ni):
        f_TiAl = self._binary_funcs["Ti-Al"]
        f_TiNi = self._binary_funcs["Ti-Ni"]
        f_AlNi = self._binary_funcs["Al-Ni"]

        s_AB = x_Ti + x_Al
        s_BC = x_Al + x_Ni
        s_AC = x_Ti + x_Ni
        w_AB = np.where(s_AB > 0, x_Ti / s_AB, 0.0)
        w_BC = np.where(s_BC > 0, x_Al / s_BC, 0.0)
        w_AC = np.where(s_AC > 0, x_Ti / s_AC, 0.0)
        return s_AB**2 * f_TiAl(w_AB) + s_AC**2 * f_TiNi(w_AC) + s_BC**2 * f_AlNi(w_BC)

    def _model_toop(self, x_Ti, x_Al, x_Ni):
        f_TiAl = self._binary_funcs["Ti-Al"]
        f_TiNi = self._binary_funcs["Ti-Ni"]
        f_AlNi = self._binary_funcs["Al-Ni"]

        s_BC = x_Ti + x_Ni
        w_BC = np.where(s_BC > 0, x_Ti / s_BC, 0.0)
        eta_AB = f_TiAl(1 - x_Al)
        eta_AC = f_AlNi(x_Al)
        eta_BC = f_TiNi(w_BC)
        return np.where(
            s_BC > 0,
            (x_Ti / s_BC) * eta_AB + (x_Ni / s_BC) * eta_AC + s_BC**2 * eta_BC,
            eta_AB,
        )

    def _model_maggianu(self, x_Ti, x_Al, x_Ni):
        f_TiAl = self._binary_funcs["Ti-Al"]
        f_TiNi = self._binary_funcs["Ti-Ni"]
        f_AlNi = self._binary_funcs["Al-Ni"]

        V_TiAl = (1.0 + x_Ti - x_Al) / 2.0
        V_AlTi = (1.0 + x_Al - x_Ti) / 2.0
        V_TiNi = (1.0 + x_Ti - x_Ni) / 2.0
        V_NiTi = (1.0 + x_Ni - x_Ti) / 2.0
        V_AlNi = (1.0 + x_Al - x_Ni) / 2.0
        V_NiAl = (1.0 + x_Ni - x_Al) / 2.0

        denom_TiAl = V_TiAl * V_AlTi
        denom_TiNi = V_TiNi * V_NiTi
        denom_AlNi = V_AlNi * V_NiAl

        term_TiAl = np.where(
            denom_TiAl > 1e-10,
            (x_Ti * x_Al) / denom_TiAl * f_TiAl(V_TiAl),
            0.0,
        )
        term_TiNi = np.where(
            denom_TiNi > 1e-10,
            (x_Ti * x_Ni) / denom_TiNi * f_TiNi(V_TiNi),
            0.0,
        )
        term_AlNi = np.where(
            denom_AlNi > 1e-10,
            (x_Al * x_Ni) / denom_AlNi * f_AlNi(V_AlNi),
            0.0,
        )
        return term_TiAl + term_TiNi + term_AlNi

    def _model_hillert_toop(self, x_Ti, x_Al, x_Ni):
        f_TiAl = self._binary_funcs["Ti-Al"]
        f_TiNi = self._binary_funcs["Ti-Ni"]
        f_AlNi = self._binary_funcs["Al-Ni"]

        s_BC = x_Ti + x_Ni
        V_TiNi = (1.0 + x_Ti - x_Ni) / 2.0
        V_NiTi = (1.0 + x_Ni - x_Ti) / 2.0

        eta_AB = f_TiAl(1 - x_Al)
        eta_AC = f_AlNi(x_Al)
        eta_BC = f_TiNi(V_TiNi)

        denom = V_TiNi * V_NiTi
        safe_denom = np.where(denom > 1e-10, denom, 1.0)
        term3 = (x_Ti * x_Ni) / safe_denom * eta_BC
        term3 = np.where(denom > 1e-10, term3, 0.0)

        return np.where(
            s_BC > 0,
            (x_Ti / s_BC) * eta_AB + (x_Ni / s_BC) * eta_AC + term3,
            eta_AB,
        )

    def _compute_eta_E(self, x_Ti, x_Al, x_Ni):
        x_Ti = np.asarray(x_Ti, dtype=float)
        x_Al = np.asarray(x_Al, dtype=float)
        x_Ni = np.asarray(x_Ni, dtype=float)

        if self._params.model_name == "kohler":
            return self._model_kohler(x_Ti, x_Al, x_Ni)
        elif self._params.model_name == "toop":
            return self._model_toop(x_Ti, x_Al, x_Ni)
        elif self._params.model_name == "maggianu":
            return self._model_maggianu(x_Ti, x_Al, x_Ni)
        elif self._params.model_name == "hillert_toop":
            return self._model_hillert_toop(x_Ti, x_Al, x_Ni)
        else:
            return self._model_hillert_toop(x_Ti, x_Al, x_Ni)

    def _predict_ternary_correction(self, x_Ti, x_Al):
        if self._gp_ternary is None:
            return np.zeros_like(x_Ti)
        X_q = np.column_stack([np.asarray(x_Ti).ravel(), np.asarray(x_Al).ravel()])
        X_qs = (X_q - self._gp_Xm) / self._gp_Xs
        return (
            self._gp_ternary.predict(X_qs, return_std=True)[0].ravel() * self._gp_ys
            + self._gp_ym
        )

    def predictOnGrid(self, n_points: int = 30, include_ternary_gp: bool = True):
        if not self._is_fitted:
            raise RuntimeError("Must fit before prediction")

        from modules.grid_module import generateTriangularGrid

        x_Ti_g, x_Al_g, x_Ni_g = generateTriangularGrid(n_points)
        x_Ti_g = np.array(x_Ti_g)
        x_Al_g = np.array(x_Al_g)
        x_Ni_g = np.array(x_Ni_g)

        sqrt3_2 = np.sqrt(3) / 2
        x_cart_g = x_Al_g + 0.5 * x_Ni_g
        y_cart_g = sqrt3_2 * x_Ni_g

        eta_mix_g = (
            x_Ti_g * self._eta_pure["Ti"]
            + x_Al_g * self._eta_pure["Al"]
            + x_Ni_g * self._eta_pure["Ni"]
        )

        vi_binary = eta_mix_g + self._compute_eta_E(x_Ti_g, x_Al_g, x_Ni_g)

        if include_ternary_gp and self._gp_ternary is not None:
            gp_correction = self._predict_ternary_correction(x_Ti_g, x_Al_g)
            vi_full = vi_binary + gp_correction
        else:
            gp_correction = np.zeros_like(vi_binary)
            vi_full = vi_binary

        x_cart_md = self._md_data["x_Al"] + 0.5 * self._md_data["x_Ni"]
        y_cart_md = sqrt3_2 * self._md_data["x_Ni"]

        from scipy.interpolate import griddata

        vi_md_grid = griddata(
            np.column_stack([x_cart_md, y_cart_md]),
            self._md_data["vi"],
            (x_cart_g, y_cart_g),
            method="linear",
        )
        nan_mask = np.isnan(vi_md_grid)
        if nan_mask.any():
            vi_md_grid[nan_mask] = griddata(
                np.column_stack([x_cart_md, y_cart_md]),
                self._md_data["vi"],
                (x_cart_g[nan_mask], y_cart_g[nan_mask]),
                method="nearest",
            )
        vi_md_grid = np.where(
            np.isnan(vi_md_grid), np.nanmean(self._md_data["vi"]), vi_md_grid
        )

        return {
            "vi_md_grid": vi_md_grid.tolist(),
            "vi_binary": vi_binary.tolist(),
            "vi_full": vi_full.tolist(),
            "gp_correction": gp_correction.tolist(),
            "x_cart_g": x_cart_g.tolist(),
            "y_cart_g": y_cart_g.tolist(),
            "x_cart_md": x_cart_md.tolist(),
            "y_cart_md": y_cart_md.tolist(),
            "n_points": n_points,
            "model_name": self._params.model_name,
            "include_ternary_gp": include_ternary_gp,
        }

    def getMDData(self) -> dict | None:
        if not self._md_data:
            return None
        return {
            "x_Ti": self._md_data["x_Ti"].copy(),
            "x_Al": self._md_data["x_Al"].copy(),
            "x_Ni": self._md_data["x_Ni"].copy(),
            "vi": self._md_data["vi"].copy(),
        }

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    @property
    def model_name(self) -> str:
        return self._params.model_name
