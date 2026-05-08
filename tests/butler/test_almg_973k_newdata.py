"""
Test Al-Mg at specific compositions with temperature 973K
New experimental data from literature
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

from importlib.util import spec_from_file_location, module_from_spec
from modules.rk_module import RKCalc, DataPoint
from modules.gp_module import GPCalc
from modules.butler_module import ButlerCalc, ButlerConfig, ButlerGEFunctions
from modules.miedema_module import MiedemaCalc


def load_config(config_path):
    spec = spec_from_file_location("config", config_path)
    config = module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


CONFIG_DIR = Path(__file__).parent.parent / "config"


def mass_to_atomic_fraction(mass_frac_Al, M_Al=0.0269815, M_Mg=0.02430):
    n_Al = mass_frac_Al / M_Al
    n_Mg = (1 - mass_frac_Al) / M_Mg
    return n_Al / (n_Al + n_Mg)


def test_almg_973k_newdata():
    config = load_config(str(CONFIG_DIR / "AlMg.py"))
    T = 973

    new_exp_x_mg = np.array([0.8, 3, 5, 8]) / 100
    new_exp_sigma = np.array([0.856, 0.822, 0.798, 0.781])

    print(f"\n{'=' * 70}")
    print(f"Al-Mg Surface Tension at T={T}K")
    print(f"New experimental data:")
    print(f"  x_Mg (atomic): {new_exp_x_mg}")
    print(f"  sigma: {new_exp_sigma}")
    print(f"{'=' * 70}")

    butler_config = ButlerConfig(
        sigma_i_func=config.sigma_i,
        density_func=config.density,
        element_props_get_M=lambda e: config.MOLAR_MASS[e],
        elem_A=13,
        elem_B=12,
    )

    L_coeffs_raw = [coef for key in ["L0", "L1", "L2"] for coef in config.L_COEFFS[key]]

    lit_func, lit_dfunc = RKCalc.from_L(L_coeffs_raw)
    lit_butler = ButlerCalc(ButlerGEFunctions(GE_func=lit_func, dGE_dx_func=lit_dfunc))
    lit_butler.fit(butler_config)

    x_train = np.array(
        [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95]
    )
    G_true_train = np.array([lit_func(x, T) for x in x_train])

    points = [
        DataPoint(features=(float(x), float(T)), target=float(g))
        for x, g in zip(x_train, G_true_train)
    ]

    dRK = RKCalc()
    dRK.fit(points, order=2)
    dRK_func, dRK_dfunc = dRK.get_GE_functions()
    dRK_butler = ButlerCalc(ButlerGEFunctions(GE_func=dRK_func, dGE_dx_func=dRK_dfunc))
    dRK_butler.fit(butler_config)

    x_dense = np.linspace(0.01, 0.99, 100)
    features_dense = [(float(x), float(T)) for x in x_dense]

    miedema = MiedemaCalc()
    mie_train = np.array(
        [miedema.calculateSingleBatch(13, 12, [x])["values"][0] * 1000 for x in x_train]
    )
    residual_targets = G_true_train - mie_train
    residual_points = [
        DataPoint(features=(float(x), float(T)), target=float(r))
        for x, r in zip(x_train, residual_targets)
    ]

    gp_d = GPCalc()
    gp_d.train(points, target_mode="direct", kernel_type="rbf", alpha=0.01)
    pred_d = gp_d.predict(features_dense)

    gp_r = GPCalc()
    gp_r.train(residual_points, target_mode="direct", kernel_type="rbf", alpha=0.01)
    pred_r = gp_r.predict(features_dense)

    def dGP_func(x, T):
        idx = np.argmin(np.abs(x_dense - x))
        return pred_d["target_array"][idx]

    def rGP_func(x, T):
        mie = miedema.calculateSingleBatch(13, 12, [x])["values"][0] * 1000
        idx = np.argmin(np.abs(x_dense - x))
        return mie + pred_r["target_array"][idx]

    dense_points_d = [
        DataPoint(features=(float(x), float(T)), target=float(y), variance=float(v))
        for x, y, v in zip(x_dense, pred_d["target_array"], pred_d["var_array"])
    ]
    dGPRK = RKCalc()
    dGPRK.fit(dense_points_d, order=2, use_variance_weighting=True)
    dGPRK_func, dGPRK_dfunc = dGPRK.get_GE_functions()
    dGPRK_butler = ButlerCalc(
        ButlerGEFunctions(GE_func=dGPRK_func, dGE_dx_func=dGPRK_dfunc)
    )
    dGPRK_butler.fit(butler_config)

    rGP_dense = [rGP_func(x, T) for x in x_dense]
    rGP_dense_points = [
        DataPoint(features=(float(x), float(T)), target=float(y), variance=float(v))
        for x, y, v in zip(x_dense, rGP_dense, pred_r["var_array"])
    ]
    rGPRK = RKCalc()
    rGPRK.fit(rGP_dense_points, order=2, use_variance_weighting=True)
    rGPRK_func, rGPRK_dfunc = rGPRK.get_GE_functions()
    rGPRK_butler = ButlerCalc(
        ButlerGEFunctions(GE_func=rGPRK_func, dGE_dx_func=rGPRK_dfunc)
    )
    rGPRK_butler.fit(butler_config)

    x_full = np.linspace(0.0, 1.0, 200)
    x_full_mg = 1 - x_full
    lit_sigma_full = np.array([lit_butler.solve(T, x)["sigma"] for x in x_full])
    dRK_sigma_full = np.array([dRK_butler.solve(T, x)["sigma"] for x in x_full])
    dGPRK_sigma_full = np.array([dGPRK_butler.solve(T, x)["sigma"] for x in x_full])
    rGPRK_sigma_full = np.array([rGPRK_butler.solve(T, x)["sigma"] for x in x_full])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.plot(x_full_mg, lit_sigma_full, "k-", linewidth=2, label="RK (true)")
    ax1.plot(x_full_mg, dRK_sigma_full, "c--", linewidth=1.5, alpha=0.8, label="dRK")
    ax1.plot(x_full_mg, dGPRK_sigma_full, "g:", linewidth=1.5, alpha=0.8, label="dGPRK")
    ax1.plot(
        x_full_mg, rGPRK_sigma_full, "r-.", linewidth=1.5, alpha=0.8, label="rGPRK"
    )

    for i, (xm, s) in enumerate(zip(new_exp_x_mg, new_exp_sigma)):
        ax1.scatter(xm, s, color="red", s=100, zorder=5)
        ax1.annotate(
            f"#{i + 1}(xMg={xm:.3f})",
            (xm, s),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )

    ax1.set_xlabel("$x_{Mg}$", fontsize=12)
    ax1.set_ylabel(r"$\sigma$ (N/m)", fontsize=12)
    ax1.set_title(f"Al-Mg Surface Tension at T={T}K", fontsize=14)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)

    lit_xs_full = np.array([lit_butler.solve(T, x)["x_A_surface"] for x in x_full])
    dRK_xs_full = np.array([dRK_butler.solve(T, x)["x_A_surface"] for x in x_full])
    dGPRK_xs_full = np.array([dGPRK_butler.solve(T, x)["x_A_surface"] for x in x_full])
    rGPRK_xs_full = np.array([rGPRK_butler.solve(T, x)["x_A_surface"] for x in x_full])

    lit_xs_mg = 1 - lit_xs_full
    dRK_xs_mg = 1 - dRK_xs_full
    dGPRK_xs_mg = 1 - dGPRK_xs_full
    rGPRK_xs_mg = 1 - rGPRK_xs_full

    ax2.plot(x_full_mg, lit_xs_mg, "k-", linewidth=2, label="RK (true)")
    ax2.plot(x_full_mg, dRK_xs_mg, "c--", linewidth=1.5, alpha=0.8, label="dRK")
    ax2.plot(x_full_mg, dGPRK_xs_mg, "g:", linewidth=1.5, alpha=0.8, label="dGPRK")
    ax2.plot(x_full_mg, rGPRK_xs_mg, "r-.", linewidth=1.5, alpha=0.8, label="rGPRK")
    ax2.plot([0, 1], [0, 1], "gray", linestyle=":", alpha=0.5, label="y=x")
    ax2.set_xlabel("$x_{Mg}^{B}$", fontsize=12)
    ax2.set_ylabel("$x_{Mg}^{S}$", fontsize=12)
    ax2.set_title(f"Al-Mg Surface Enrichment at T={T}K", fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig("temp/almg_973k_newdata.png", dpi=150)
    print(f"\nPlot saved to temp/almg_973k_newdata.png")

    print(f"\n{'=' * 70}")
    print("Results at new experimental compositions:")
    print(f"{'=' * 70}")
    print(
        f"{'Method':<15} {'x=0.0080':<12} {'x=0.0300':<12} {'x=0.0500':<12} {'x=0.0800':<12} {'RMSE':<10}"
    )
    print(f"{'-' * 70}")

    x_test = 1 - new_exp_x_mg

    for name, butler in [
        ("RK (true)", lit_butler),
        ("dRK", dRK_butler),
        ("dGPRK", dGPRK_butler),
        ("rGPRK", rGPRK_butler),
    ]:
        vals = [butler.solve(T, x)["sigma"] for x in x_test]
        rmse = np.sqrt(np.mean([(p - e) ** 2 for p, e in zip(vals, new_exp_sigma)]))
        print(
            f"{name:<15} {vals[0]:<12.4f} {vals[1]:<12.4f} {vals[2]:<12.4f} {vals[3]:<12.4f} {rmse:<10.4f}"
        )


if __name__ == "__main__":
    test_almg_973k_newdata()
