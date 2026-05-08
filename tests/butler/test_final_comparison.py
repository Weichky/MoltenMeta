"""
Final comparison: dRK, dGPRK, rGPRK with optimal GP settings (Fixed Matern ls=1)
Noise: ±10%

Usage: uv run python tests/butler/test_final_comparison.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import importlib.util
import warnings

warnings.filterwarnings("ignore")

from modules.rk_module import RKCalc, DataPoint
from modules.butler_module import ButlerCalc, ButlerConfig, ButlerGEFunctions
from modules.miedema_module import MiedemaCalc


def load_config(config_path, name):
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


CONFIG_DIR = Path(__file__).parent.parent / "config"


def create_butler_config(config, elem_A, elem_B):
    return ButlerConfig(
        sigma_i_func=config.sigma_i,
        density_func=config.density,
        element_props_get_M=lambda e: config.MOLAR_MASS[e],
        elem_A=elem_A,
        elem_B=elem_B,
    )


def generate_samples(lit_func, T, n_samples=20, seed=None):
    if seed is not None:
        np.random.seed(seed)

    n_left = int(n_samples * 0.55)
    n_center = int(n_samples * 0.30)
    n_right = n_samples - n_left - n_center

    left_x = sorted(np.random.uniform(0.01, 0.34, size=n_left))
    center_x = sorted(np.random.uniform(0.30, 0.70, size=n_center))
    right_x = sorted(np.random.uniform(0.66, 0.99, size=n_right))
    all_x = left_x + center_x + right_x

    G_values = [lit_func(x, T) for x in all_x]
    noise_factor = 1 + np.random.uniform(-0.10, 0.10, size=len(G_values))
    noisy_G = [g * nf for g, nf in zip(G_values, noise_factor)]
    points = [
        DataPoint(features=(float(x), float(T)), target=g)
        for x, g in zip(all_x, noisy_G)
    ]

    return points, all_x, G_values, noisy_G


class FixedMaternGP:
    def __init__(self, length_scale=1.0, nu=1.5):
        self._length_scale = length_scale
        self._nu = nu
        self._X_train = []
        self._y_train = []
        self._model = None
        self._is_trained = False

    def train(self, data_points):
        self._X_train = [dp.features for dp in data_points]
        self._y_train = [dp.target for dp in data_points]
        self._trainGP()
        self._is_trained = True

    def _trainGP(self):
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import Matern

        kernel = Matern(
            length_scale=self._length_scale, nu=self._nu, length_scale_bounds="fixed"
        )
        X = np.array(self._X_train)
        y = np.array(self._y_train)
        self._model = GaussianProcessRegressor(
            kernel=kernel, alpha=0.01, n_restarts_optimizer=0
        )
        self._model.fit(X, y)

    def predict(self, features_array):
        if not self._is_trained:
            raise RuntimeError("Must train first")
        X = np.array(features_array)
        y_pred, var_pred = self._model.predict(X, return_std=True)
        return {"target_array": y_pred.tolist(), "var_array": (var_pred**2).tolist()}


def run_comparison(config_path, name, elem_A, elem_B, n_trials=20):
    config = load_config(config_path, name)
    T = config.T
    L_coeffs = [coef for key in ["L0", "L1", "L2"] for coef in config.L_COEFFS[key]]

    lit_func, lit_dfunc = RKCalc.from_L(L_coeffs)
    butler_config = create_butler_config(config, elem_A, elem_B)

    x_range = np.linspace(0.01, 0.99, 100)
    x_dense = np.linspace(0.05, 0.95, 50)
    features_dense = [(float(x), float(T)) for x in x_dense]

    np.random.seed(42)
    seeds = [np.random.randint(0, 100000) for _ in range(n_trials)]

    results = {m: [] for m in ["dRK", "dGPRK", "rGPRK"]}

    miedema = MiedemaCalc()

    for seed in seeds:
        np.random.seed(seed)
        n_samples = np.random.randint(15, 26)
        points, all_x, G_values, noisy_G = generate_samples(
            lit_func, T, n_samples, seed=None
        )

        lit_butler = ButlerCalc(
            ButlerGEFunctions(GE_func=lit_func, dGE_dx_func=lit_dfunc)
        )
        lit_butler.fit(butler_config)
        lit_sigma = np.array([lit_butler.solve(T, x)["sigma"] for x in x_range])

        dRK = RKCalc()
        dRK.fit(points, order=2)
        dRK_func, dRK_dfunc = dRK.get_GE_functions()
        dRK_butler = ButlerCalc(
            ButlerGEFunctions(GE_func=dRK_func, dGE_dx_func=dRK_dfunc)
        )
        dRK_butler.fit(butler_config)
        dRK_sigma = np.array([dRK_butler.solve(T, x)["sigma"] for x in x_range])
        results["dRK"].append(np.sqrt(np.mean((dRK_sigma - lit_sigma) ** 2)))

        mie_at_x = [
            miedema.calculateSingleBatch(elem_A, elem_B, [x])["values"][0] * 1000
            for x in all_x
        ]
        residual_targets = [noisy - mie for noisy, mie in zip(noisy_G, mie_at_x)]
        residual_points = [
            DataPoint(features=(float(x), float(T)), target=r)
            for x, r in zip(all_x, residual_targets)
        ]

        gp_r = FixedMaternGP(length_scale=1.0, nu=1.5)
        gp_r.train(residual_points)
        pred_r = gp_r.predict(features_dense)

        def rGP_func(x, T):
            mie = miedema.calculateSingleBatch(elem_A, elem_B, [x])["values"][0] * 1000
            idx = np.argmin(np.abs(x_dense - x))
            return mie + pred_r["target_array"][idx]

        rGP_dense = [rGP_func(x, T) for x in x_dense]
        rGP_dense_points = [
            DataPoint(features=(float(x), float(T)), target=y)
            for x, y in zip(x_dense, rGP_dense)
        ]
        rGPRK = RKCalc()
        rGPRK.fit(rGP_dense_points, order=2)
        rGPRK_func, rGPRK_dfunc = rGPRK.get_GE_functions()
        rGPRK_butler = ButlerCalc(
            ButlerGEFunctions(GE_func=rGPRK_func, dGE_dx_func=rGPRK_dfunc)
        )
        rGPRK_butler.fit(butler_config)
        rGPRK_sigma = np.array([rGPRK_butler.solve(T, x)["sigma"] for x in x_range])
        results["rGPRK"].append(np.sqrt(np.mean((rGPRK_sigma - lit_sigma) ** 2)))

        gp_d = FixedMaternGP(length_scale=1.0, nu=1.5)
        gp_d.train(points)
        pred_d = gp_d.predict(features_dense)
        dense_points_d = [
            DataPoint(features=(x, T), target=y)
            for x, y in zip(x_dense, pred_d["target_array"])
        ]
        dGPRK = RKCalc()
        dGPRK.fit(dense_points_d, order=2)
        dGPRK_func, dGPRK_dfunc = dGPRK.get_GE_functions()
        dGPRK_butler = ButlerCalc(
            ButlerGEFunctions(GE_func=dGPRK_func, dGE_dx_func=dGPRK_dfunc)
        )
        dGPRK_butler.fit(butler_config)
        dGPRK_sigma = np.array([dGPRK_butler.solve(T, x)["sigma"] for x in x_range])
        results["dGPRK"].append(np.sqrt(np.mean((dGPRK_sigma - lit_sigma) ** 2)))

    return (
        results,
        x_range,
        x_dense,
        lit_func,
        lit_dfunc,
        T,
        butler_config,
        points,
        all_x,
        noisy_G,
    )


def plot_comparison(
    name,
    results,
    x_range,
    x_dense,
    lit_func,
    lit_dfunc,
    T,
    butler_config,
    points,
    all_x,
    noisy_G,
):
    config = load_config(
        str(CONFIG_DIR / f"{'AlMg' if 'Mg' in name else 'AlEr'}.py"), name
    )
    elem_A, elem_B = 13, 12 if name == "Al-Mg" else 39
    features_dense = [(float(x), float(T)) for x in x_dense]

    miedema = MiedemaCalc()

    lit_butler = ButlerCalc(ButlerGEFunctions(GE_func=lit_func, dGE_dx_func=lit_dfunc))
    lit_butler.fit(butler_config)
    lit_sigma = np.array([lit_butler.solve(T, x)["sigma"] for x in x_range])

    dRK = RKCalc()
    dRK.fit(points, order=2)
    dRK_func, dRK_dfunc = dRK.get_GE_functions()
    dRK_butler = ButlerCalc(ButlerGEFunctions(GE_func=dRK_func, dGE_dx_func=dRK_dfunc))
    dRK_butler.fit(butler_config)
    dRK_sigma = np.array([dRK_butler.solve(T, x)["sigma"] for x in x_range])

    mie_at_x = [
        miedema.calculateSingleBatch(elem_A, elem_B, [x])["values"][0] * 1000
        for x in all_x
    ]
    residual_targets = [noisy - mie for noisy, mie in zip(noisy_G, mie_at_x)]
    residual_points = [
        DataPoint(features=(float(x), float(T)), target=r)
        for x, r in zip(all_x, residual_targets)
    ]

    gp_r = FixedMaternGP(length_scale=1.0, nu=1.5)
    gp_r.train(residual_points)
    pred_r = gp_r.predict(features_dense)

    def rGP_func(x, T):
        mie = miedema.calculateSingleBatch(elem_A, elem_B, [x])["values"][0] * 1000
        idx = np.argmin(np.abs(x_dense - x))
        return mie + pred_r["target_array"][idx]

    rGP_dense = [rGP_func(x, T) for x in x_dense]
    rGP_dense_points = [
        DataPoint(features=(float(x), float(T)), target=y)
        for x, y in zip(x_dense, rGP_dense)
    ]
    rGPRK = RKCalc()
    rGPRK.fit(rGP_dense_points, order=2)
    rGPRK_func, rGPRK_dfunc = rGPRK.get_GE_functions()
    rGPRK_butler = ButlerCalc(
        ButlerGEFunctions(GE_func=rGPRK_func, dGE_dx_func=rGPRK_dfunc)
    )
    rGPRK_butler.fit(butler_config)
    rGPRK_sigma = np.array([rGPRK_butler.solve(T, x)["sigma"] for x in x_range])

    gp_d = FixedMaternGP(length_scale=1.0, nu=1.5)
    gp_d.train(points)
    pred_d = gp_d.predict(features_dense)
    dense_points_d = [
        DataPoint(features=(x, T), target=y)
        for x, y in zip(x_dense, pred_d["target_array"])
    ]
    dGPRK = RKCalc()
    dGPRK.fit(dense_points_d, order=2)
    dGPRK_func, dGPRK_dfunc = dGPRK.get_GE_functions()
    dGPRK_butler = ButlerCalc(
        ButlerGEFunctions(GE_func=dGPRK_func, dGE_dx_func=dGPRK_dfunc)
    )
    dGPRK_butler.fit(butler_config)
    dGPRK_sigma = np.array([dGPRK_butler.solve(T, x)["sigma"] for x in x_range])

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0, 0]
    ax.plot(x_range, lit_sigma, "k-", linewidth=2, label="RK (truth)")
    ax.plot(
        x_range,
        dRK_sigma,
        "c--",
        linewidth=1.5,
        alpha=0.8,
        label=f"dRK (RMSE={np.mean(results['dRK']):.4f})",
    )
    ax.scatter(
        all_x,
        noisy_G,
        c="green",
        s=40,
        marker="o",
        label="Data (10% noise)",
        zorder=5,
        alpha=0.6,
    )
    y_min = min(lit_sigma.min(), dRK_sigma.min()) * 0.95
    y_max = max(lit_sigma.max(), dRK_sigma.max()) * 1.05
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("x")
    ax.set_ylabel("σ (N/m)")
    ax.set_title(f"{name}: dRK vs Ground Truth")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    ax.plot(x_range, lit_sigma, "k-", linewidth=2, label="RK (truth)")
    ax.plot(
        x_range,
        dGPRK_sigma,
        "g:",
        linewidth=1.5,
        alpha=0.8,
        label=f"dGPRK (RMSE={np.mean(results['dGPRK']):.4f})",
    )
    ax.plot(
        x_range,
        rGPRK_sigma,
        "r-.",
        linewidth=1.5,
        alpha=0.8,
        label=f"rGPRK (RMSE={np.mean(results['rGPRK']):.4f})",
    )
    ax.scatter(
        all_x,
        noisy_G,
        c="green",
        s=40,
        marker="o",
        label="Data (10% noise)",
        zorder=5,
        alpha=0.6,
    )
    y_min = min(lit_sigma.min(), dGPRK_sigma.min(), rGPRK_sigma.min()) * 0.95
    y_max = max(lit_sigma.max(), dGPRK_sigma.max(), rGPRK_sigma.max()) * 1.05
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("x")
    ax.set_ylabel("σ (N/m)")
    ax.set_title(f"{name}: GP+RK Methods vs Ground Truth")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    methods = ["dRK", "dGPRK", "rGPRK"]
    colors = ["cyan", "green", "red"]
    x_pos = np.arange(len(methods))
    for i, (m, c) in enumerate(zip(methods, colors)):
        rmse = np.mean(results[m])
        std = np.std(results[m])
        ax.bar(m, rmse, yerr=std, color=c, alpha=0.6, capsize=5)
    ax.set_ylabel("RMSE (N/m)")
    ax.set_title(f"{name}: Method Comparison (20 trials)")
    ax.grid(True, alpha=0.3, axis="y")

    ax = axes[1, 1]
    ax.axis("off")
    summary = f"""
    Optimal GP Configuration:
    - Kernel: Matern (nu=1.5)
    - Length scale: fixed at 1.0 (not optimized)
    - Alpha: 0.01

    Key Finding:
    Fixing length_scale prevents GP from overfitting
    on limited data (15-25 points with 10% noise).

    Results (RMSE ± std):
    ----------------------
    Al-Mg:
      dRK:   {np.mean(results["dRK"]):.6f} ± {np.std(results["dRK"]):.6f}
      dGPRK: {np.mean(results["dGPRK"]):.6f} ± {np.std(results["dGPRK"]):.6f}
      rGPRK: {np.mean(results["rGPRK"]):.6f} ± {np.std(results["rGPRK"]):.6f}

    Al-Er:
      (See console output)
    """
    ax.text(
        0.1, 0.5, summary, fontsize=10, family="monospace", verticalalignment="center"
    )

    plt.tight_layout()
    plt.savefig(f"temp/{name}_final_comparison.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Final Comparison: dRK, dGPRK, rGPRK (Noise: ±10%)")
    print("=" * 70)

    print("\n--- Al-Mg ---")
    (
        results_mg,
        x_range,
        x_dense,
        lit_func,
        lit_dfunc,
        T,
        butler_config,
        points_mg,
        all_x_mg,
        noisy_G_mg,
    ) = run_comparison(str(CONFIG_DIR / "AlMg.py"), "Al-Mg", 13, 12, n_trials=20)
    print(f"{'Method':<10} {'RMSE':<15} {'Std':<10}")
    print("-" * 35)
    for m in ["dRK", "dGPRK", "rGPRK"]:
        print(f"{m:<10} {np.mean(results_mg[m]):.6f}     {np.std(results_mg[m]):.6f}")

    print("\n--- Al-Er ---")
    (
        results_er,
        x_range,
        x_dense,
        lit_func,
        lit_dfunc,
        T,
        butler_config_er,
        points_er,
        all_x_er,
        noisy_G_er,
    ) = run_comparison(str(CONFIG_DIR / "AlEr.py"), "Al-Er", 13, 39, n_trials=20)
    print(f"{'Method':<10} {'RMSE':<15} {'Std':<10}")
    print("-" * 35)
    for m in ["dRK", "dGPRK", "rGPRK"]:
        print(f"{m:<10} {np.mean(results_er[m]):.6f}     {np.std(results_er[m]):.6f}")

    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Method':<10} {'Al-Mg RMSE':<20} {'Al-Er RMSE':<20}")
    print("-" * 50)
    for m in ["dRK", "dGPRK", "rGPRK"]:
        mg = np.mean(results_mg[m])
        er = np.mean(results_er[m])
        mg_std = np.std(results_mg[m])
        er_std = np.std(results_er[m])
        print(f"{m:<10} {mg:.6f} ± {mg_std:.6f}     {er:.6f} ± {er_std:.6f}")

    print("\n--- Generating plots ---")
    plot_comparison(
        "Al-Mg",
        results_mg,
        x_range,
        x_dense,
        lit_func,
        lit_dfunc,
        T,
        butler_config,
        points_mg,
        all_x_mg,
        noisy_G_mg,
    )
    plot_comparison(
        "Al-Er",
        results_er,
        x_range,
        x_dense,
        lit_func,
        lit_dfunc,
        T,
        butler_config_er,
        points_er,
        all_x_er,
        noisy_G_er,
    )
