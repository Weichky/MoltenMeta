from dataclasses import dataclass
from typing import TypedDict


ALPHA = 0.01
N_RESTARTS_OPTIMIZER = 5
LENGTH_SCALE_BOUNDS = (1e-2, 1e3)
LENGTH_SCALE_INIT = 1.0


@dataclass(frozen=True)
class DataPoint:
    features: tuple[float, ...]
    target: float


class GPResultDict(TypedDict):
    target_array: list[float]
    var_array: list[float]
    method: str


class GPCalc:
    def __init__(self, module_service=None):
        self._module_service = module_service
        self._is_trained = False
        self._kernel_type = "rbf"
        self._X_train: list[tuple[float, ...]] = []
        self._y_train: list[float] = []
        self._hyperparameters: dict = {}
        self._model = None

    def setModuleService(self, module_service) -> None:
        self._module_service = module_service

    def train(
        self,
        data_points: list[DataPoint],
        target_mode: str = "direct",
        prior: dict | None = None,
        kernel_type: str = "rbf",
        alpha: float = ALPHA,
    ) -> dict:
        if not data_points:
            raise ValueError("data_points cannot be empty")

        self._kernel_type = kernel_type.lower()
        self._X_train = [dp.features for dp in data_points]
        self._y_train = [dp.target for dp in data_points]
        self._alpha = alpha

        if target_mode == "residual" and prior is not None:
            self._y_train = self._computeResiduals(data_points, prior)

        self._trainGP()
        self._is_trained = True
        return {
            "status": "trained",
            "n_samples": len(data_points),
            "n_features": len(data_points[0].features),
            "kernel": self._kernel_type,
            "target_mode": target_mode,
        }

    def _computeResiduals(
        self, data_points: list[DataPoint], prior: dict
    ) -> list[float]:
        if self._module_service is None:
            raise RuntimeError("Module service required for residual mode")

        prior_outputs = self._callPrior(prior, data_points)

        residuals = []
        for dp, prior_value in zip(data_points, prior_outputs):
            residuals.append(dp.target - prior_value)

        return residuals

    def _callPrior(self, prior: dict, data_points: list[DataPoint]) -> list[float]:
        module_name = prior["module"]
        method_name = prior["method"]

        features_list = [dp.features for dp in data_points]

        result = self._module_service.callMethod(
            module_name,
            method_name,
            **prior.get("kwargs", {}),
            features_list=features_list,
        )

        return result["values"]

    def _trainGP(self) -> None:
        import numpy as np
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, Matern

        n_features = len(self._X_train[0])
        length_scale_init = [LENGTH_SCALE_INIT] * n_features
        length_scale_bounds = LENGTH_SCALE_BOUNDS

        if self._kernel_type == "rbf":
            kernel = RBF(
                length_scale=length_scale_init, length_scale_bounds=length_scale_bounds
            )
        elif self._kernel_type == "matern":
            kernel = Matern(
                length_scale=length_scale_init,
                nu=1.5,
                length_scale_bounds=length_scale_bounds,
            )
        else:
            kernel = RBF(
                length_scale=length_scale_init, length_scale_bounds=length_scale_bounds
            )

        X = np.array(self._X_train)
        y = np.array(self._y_train)

        self._model = GaussianProcessRegressor(
            kernel=kernel, alpha=self._alpha, n_restarts_optimizer=N_RESTARTS_OPTIMIZER
        )
        self._model.fit(X, y)

    def predict(self, features_array: list[tuple[float, ...]]) -> GPResultDict:
        if not self._is_trained:
            raise RuntimeError("GP model must be trained before prediction")

        import numpy as np

        X = np.array(features_array)
        y_pred, var_pred = self._model.predict(X, return_std=True)

        return {
            "target_array": y_pred.tolist(),
            "var_array": (var_pred**2).tolist(),
            "method": "GP",
        }

    def getTrainingData(self) -> tuple[list[tuple[float, ...]], list[float]]:
        if not self._is_trained:
            raise RuntimeError("GP model must be trained first")
        return self._X_train, self._y_train
