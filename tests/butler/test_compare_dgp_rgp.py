"""
Compare GP alpha=0.01 + WLS vs alpha=0.1 (no WLS) for Al-Mg and Al-Er
Focus on dGPRK/rGPRK for sigma, and dGP/dGPRK/rGP/rGPRK for G^E
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
from modules.gp_module import GPCalc
from modules.butler_module import ButlerCalc, ButlerConfig, ButlerGEFunctions
from modules.miedema_module import MiedemaCalc


def load_config(config_path):
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
    noise_factor = 1 + np.random.uniform(-0.15, 0.15, size=len(G_values))
    noisy_G = [g * nf for g, nf in zip(G_values, noise_factor)]
    points = [
        DataPoint(features=(float(x), float(T)), target=g)
        for x, g in zip(all_x, noisy_G)
    ]

    return points, all_x, G_values, noisy_G


def run_single_trial(
    lit_func,
    lit_dfunc,
    butler_config,
    miedema,
    elem_A,
    elem_B,
    T,
    x_range,
    n_samples,
    seed,
    gp_alpha,
    use_wls,
):
    np.random.seed(seed)
    points, all_x, G_values, noisy_G = generate_samples(
        lit_func, T, n_samples, seed=None
    )

    x_dense = np.linspace(0.05, 0.95, 50)
    features_dense = [(float(x), float(T)) for x in x_dense]

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

    gp_r = GPCalc()
    gp_r.train(residual_points, target_mode="direct", kernel_type="rbf", alpha=gp_alpha)
    pred_r = gp_r.predict(features_dense)

    gp_d = GPCalc()
    gp_d.train(points, target_mode="direct", kernel_type="rbf", alpha=gp_alpha)
    pred_d = gp_d.predict(features_dense)

    def rGP_func(x, T):
        mie = miedema.calculateSingleBatch(elem_A, elem_B, [x])["values"][0] * 1000
        idx = np.argmin(np.abs(x_dense - x))
        return mie + pred_r["target_array"][idx]

    def dGP_func(x, T):
        idx = np.argmin(np.abs(x_dense - x))
        return pred_d["target_array"][idx]

    def rGP_dfunc(x, T):
        dx = 0.001
        return (rGP_func(x + dx, T) - rGP_func(x - dx, T)) / (2 * dx)

    def dGP_dfunc(x, T):
        dx = 0.001
        return (dGP_func(x + dx, T) - dGP_func(x - dx, T)) / (2 * dx)

    dGP_butler = ButlerCalc(ButlerGEFunctions(GE_func=dGP_func, dGE_dx_func=dGP_dfunc))
    dGP_butler.fit(butler_config)
    dGP_sigma = np.array([dGP_butler.solve(T, x)["sigma"] for x in x_range])

    rGP_butler = ButlerCalc(ButlerGEFunctions(GE_func=rGP_func, dGE_dx_func=rGP_dfunc))
    rGP_butler.fit(butler_config)
    rGP_sigma = np.array([rGP_butler.solve(T, x)["sigma"] for x in x_range])

    rGP_dense = [rGP_func(x, T) for x in x_dense]

    if use_wls:
        points_d = [
            DataPoint(features=(x, T), target=y, variance=v)
            for x, y, v in zip(x_dense, pred_d["target_array"], pred_d["var_array"])
        ]
        points_r = [
            DataPoint(features=(float(x), float(T)), target=y, variance=v)
            for x, y, v in zip(x_dense, rGP_dense, pred_r["var_array"])
        ]
    else:
        points_d = [
            DataPoint(features=(x, T), target=y)
            for x, y in zip(x_dense, pred_d["target_array"])
        ]
        points_r = [
            DataPoint(features=(float(x), float(T)), target=y)
            for x, y in zip(x_dense, rGP_dense)
        ]

    dGPRK = RKCalc()
    dGPRK.fit(points_d, order=2, use_variance_weighting=use_wls)
    dGPRK_func, dGPRK_dfunc = dGPRK.get_GE_functions()
    dGPRK_butler = ButlerCalc(
        ButlerGEFunctions(GE_func=dGPRK_func, dGE_dx_func=dGPRK_dfunc)
    )
    dGPRK_butler.fit(butler_config)
    dGPRK_sigma = np.array([dGPRK_butler.solve(T, x)["sigma"] for x in x_range])

    rGPRK = RKCalc()
    rGPRK.fit(points_r, order=2, use_variance_weighting=use_wls)
    rGPRK_func, rGPRK_dfunc = rGPRK.get_GE_functions()
    rGPRK_butler = ButlerCalc(
        ButlerGEFunctions(GE_func=rGPRK_func, dGE_dx_func=rGPRK_dfunc)
    )
    rGPRK_butler.fit(butler_config)
    rGPRK_sigma = np.array([rGPRK_butler.solve(T, x)["sigma"] for x in x_range])

    lit_Ge = np.array([lit_func(x, T) for x in x_range])
    dRK_Ge = np.array([dRK_func(x, T) for x in x_range])
    dGP_Ge = np.array([dGP_func(x, T) for x in x_range])
    rGP_Ge = np.array([rGP_func(x, T) for x in x_range])
    dGPRK_Ge = np.array([dGPRK_func(x, T) for x in x_range])
    rGPRK_Ge = np.array([rGPRK_func(x, T) for x in x_range])

    return {
        "lit_sigma": lit_sigma,
        "dRK_sigma": dRK_sigma,
        "dGP_sigma": dGP_sigma,
        "rGP_sigma": rGP_sigma,
        "dGPRK_sigma": dGPRK_sigma,
        "rGPRK_sigma": rGPRK_sigma,
        "lit_Ge": lit_Ge,
        "dRK_Ge": dRK_Ge,
        "dGP_Ge": dGP_Ge,
        "rGP_Ge": rGP_Ge,
        "dGPRK_Ge": dGPRK_Ge,
        "rGPRK_Ge": rGPRK_Ge,
        "all_x": all_x,
        "noisy_G": noisy_G,
    }


def run_system_comparison(config_path, name, elem_A, elem_B, n_trials=20):
    config = load_config(config_path)
    T = config.T
    L_coeffs = [coef for key in ["L0", "L1", "L2"] for coef in config.L_COEFFS[key]]

    lit_func, lit_dfunc = RKCalc.from_L(L_coeffs)
    butler_config = create_butler_config(config, elem_A, elem_B)

    miedema = MiedemaCalc()

    x_range = np.linspace(0.01, 0.99, 100)

    np.random.seed(42)
    seeds = [np.random.randint(0, 100000) for _ in range(n_trials)]

    methods = ["dRK", "dGP", "rGP", "dGPRK", "rGPRK"]

    all_results = {
        "alpha01_WLS": {m: [] for m in methods},
        "alpha01_noWLS": {m: [] for m in methods},
        "alpha1_noWLS": {m: [] for m in methods},
    }

    for seed in seeds:
        for config_name, alpha, use_wls in [
            ("alpha01_WLS", 0.01, True),
            ("alpha01_noWLS", 0.01, False),
            ("alpha1_noWLS", 0.1, False),
        ]:
            r = run_single_trial(
                lit_func,
                lit_dfunc,
                butler_config,
                miedema,
                elem_A,
                elem_B,
                T,
                x_range,
                n_samples=20,
                seed=seed,
                gp_alpha=alpha,
                use_wls=use_wls,
            )
            lit_sigma = r["lit_sigma"]
            lit_Ge = r["lit_Ge"]

            for m in methods:
                all_results[config_name][m].append(
                    np.sqrt(np.mean((r[f"{m}_sigma"] - lit_sigma) ** 2))
                )

    print(f"\n{'=' * 70}")
    print(f"{name}")
    print(f"{'=' * 70}")

    print(f"\n--- Sigma RMSE (N/m) ---")
    print(f"{'Config':<20} {'dRK':<12} {'dGPRK':<12} {'rGPRK':<12}")
    print(f"{'-' * 60}")
    for cfg in ["alpha01_WLS", "alpha01_noWLS", "alpha1_noWLS"]:
        dRK_m = np.mean(all_results[cfg]["dRK"])
        dGPRK_m = np.mean(all_results[cfg]["dGPRK"])
        rGPRK_m = np.mean(all_results[cfg]["rGPRK"])
        print(f"{cfg:<20} {dRK_m:.6f}    {dGPRK_m:.6f}    {rGPRK_m:.6f}")

    print(f"\n--- G^E RMSE (J/mol) ---")
    print(f"Note: G^E computed differently - showing for reference only")

    return all_results


def main():
    all_mg = run_system_comparison(
        str(CONFIG_DIR / "AlMg.py"), "Al-Mg", 13, 12, n_trials=20
    )
    all_er = run_system_comparison(
        str(CONFIG_DIR / "AlEr.py"), "Al-Er", 13, 39, n_trials=20
    )

    print(f"\n{'=' * 70}")
    print("SUMMARY - Sigma RMSE Comparison")
    print(f"{'=' * 70}")
    print(
        f"\n{'Config':<20} {'Al-Mg dGPRK':<15} {'Al-Mg rGPRK':<15} {'Al-Er dGPRK':<15} {'Al-Er rGPRK':<15}"
    )
    print(f"{'-' * 80}")
    for cfg in ["alpha01_WLS", "alpha01_noWLS", "alpha1_noWLS"]:
        mg_d = np.mean(all_mg[cfg]["dGPRK"])
        mg_r = np.mean(all_mg[cfg]["rGPRK"])
        er_d = np.mean(all_er[cfg]["dGPRK"])
        er_r = np.mean(all_er[cfg]["rGPRK"])
        print(
            f"{cfg:<20} {mg_d:.6f}         {mg_r:.6f}         {er_d:.6f}         {er_r:.6f}"
        )

    print(f"\n{'=' * 70}")
    print("Key Findings:")
    print(f"{'=' * 70}")
    print("1. alpha01 + WLS vs alpha01 no WLS:")
    for name, all_sys in [("Al-Mg", all_mg), ("Al-Er", all_er)]:
        dGPRK_imp = (
            (
                np.mean(all_sys["alpha01_noWLS"]["dGPRK"])
                - np.mean(all_sys["alpha01_WLS"]["dGPRK"])
            )
            / np.mean(all_sys["alpha01_noWLS"]["dGPRK"])
            * 100
        )
        rGPRK_imp = (
            (
                np.mean(all_sys["alpha01_noWLS"]["rGPRK"])
                - np.mean(all_sys["alpha01_WLS"]["rGPRK"])
            )
            / np.mean(all_sys["alpha01_noWLS"]["rGPRK"])
            * 100
        )
        print(
            f"  {name}: dGPRK {dGPRK_imp:.1f}% improvement, rGPRK {rGPRK_imp:.1f}% improvement"
        )

    print("\n2. alpha01 + WLS vs alpha1 no WLS:")
    for name, all_sys in [("Al-Mg", all_mg), ("Al-Er", all_er)]:
        dGPRK_imp = (
            (
                np.mean(all_sys["alpha1_noWLS"]["dGPRK"])
                - np.mean(all_sys["alpha01_WLS"]["dGPRK"])
            )
            / np.mean(all_sys["alpha1_noWLS"]["dGPRK"])
            * 100
        )
        rGPRK_imp = (
            (
                np.mean(all_sys["alpha1_noWLS"]["rGPRK"])
                - np.mean(all_sys["alpha01_WLS"]["rGPRK"])
            )
            / np.mean(all_sys["alpha1_noWLS"]["rGPRK"])
            * 100
        )
        print(
            f"  {name}: dGPRK {dGPRK_imp:.1f}% improvement, rGPRK {rGPRK_imp:.1f}% improvement"
        )


if __name__ == "__main__":
    main()
