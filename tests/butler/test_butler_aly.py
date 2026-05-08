"""
Butler Module Test - Al-Y System with Literature RK Parameters
Usage: uv run python tests/butler/test_butler_aly.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt

from modules.butler_module import ButlerCalc, ButlerConfig


class MockSurfaceTensionProvider:
    def __init__(self):
        self._sigma = {13: 0.74, 39: 0.50}

    def __call__(self, elem: int, T: float) -> float:
        return self._sigma[elem]


class MockDensityProvider:
    def __init__(self):
        self._rho = {13: 2702.0, 39: 4140.0}

    def __call__(self, elem: int, T: float) -> float:
        return self._rho[elem]


class MockElementPropertiesProvider:
    def __init__(self):
        self._M = {13: 0.0269815, 39: 0.08890585}

    def getAtomicWeight(self, elem: int) -> float:
        return self._M[elem]


def solve_butler_range(butler, T_fixed: float, x_range: np.ndarray) -> tuple:
    sigma_values = []
    x_A_surf_values = []
    for x in x_range:
        result = butler.solve(T_fixed, float(x))
        sigma_values.append(result["sigma"])
        x_A_surf_values.append(result["x_A_surface"])
    return np.array(sigma_values), np.array(x_A_surf_values)


if __name__ == "__main__":
    elem_A = 13
    elem_B = 39
    elem_name_a = "Al"
    elem_name_b = "Y"

    print(f"Butler Test: {elem_name_a}-{elem_name_b}\n")

    sigma_provider = MockSurfaceTensionProvider()
    density_provider = MockDensityProvider()
    elem_props_provider = MockElementPropertiesProvider()

    T_test = 900
    x_pred = np.linspace(0.01, 0.99, 50)

    print("=== Literature RK Parameters (Al-Y) ===")
    print("L0 = -36685.5 + 23.4492*T")
    print("L1 = 34349.1 - 8.23519*T")
    print(
        f"T = {T_test}K: L0 = {-36685.5 + 23.4492 * T_test:.2f} J/mol, L1 = {34349.1 - 8.23519 * T_test:.2f} J/mol"
    )
    print()

    L_literature = [-36685.5, 23.4492, 34349.1, -8.23519, 0.0, 0.0]
    Sigma_L_lit = np.eye(6) * 100.0

    config_lit = ButlerConfig(
        L_coeffs=L_literature,
        Sigma_L=Sigma_L_lit.tolist(),
        order=2,
        sigma_i_func=sigma_provider,
        density_func=density_provider,
        element_props_get_M=elem_props_provider.getAtomicWeight,
        elem_A=elem_A,
        elem_B=elem_B,
    )
    butler_lit = ButlerCalc()
    butler_lit.fit(config_lit)

    sigma_lit, xA_lit = solve_butler_range(butler_lit, T_test, x_pred)

    print(f"At x=0.3: σ={sigma_lit[14]:.4f}, X_A^S={xA_lit[14]:.4f}")
    print(f"At x=0.5: σ={sigma_lit[24]:.4f}, X_A^S={xA_lit[24]:.4f}")
    print()

    print("=== Generating Plots ===")
    fig1, ax1 = plt.subplots(figsize=(8, 8))
    ax1.plot(x_pred, sigma_lit, "b-", linewidth=2, label=f"σ (Al-Y, T={T_test}K)")
    ax1.axhline(
        y=0.74, color="gray", linestyle="--", alpha=0.5, label="σ_Al = 0.74 N/m"
    )
    ax1.axhline(y=0.50, color="gray", linestyle=":", alpha=0.5, label="σ_Y = 0.50 N/m")
    ax1.set_xlabel(f"x ({elem_name_a})", fontsize=12)
    ax1.set_ylabel("σ (N/m)", fontsize=12)
    ax1.set_title(
        f"Surface Tension: {elem_name_a}-{elem_name_b} at T={T_test}K", fontsize=14
    )
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    fig1.savefig("butler_sigma_aly.png", dpi=150, bbox_inches="tight")
    plt.close(fig1)
    print("Saved: butler_sigma_aly.png")

    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.plot(x_pred, xA_lit, "b-", linewidth=2, label=f"X_A^S (Al-Y, T={T_test}K)")
    ax2.plot(x_pred, x_pred, "k--", linewidth=1, label="X^B (no segregation)")
    ax2.set_xlabel(f"x ({elem_name_a})", fontsize=12)
    ax2.set_ylabel("X_A^S", fontsize=12)
    ax2.set_title(
        f"Surface Composition: {elem_name_a}-{elem_name_b} at T={T_test}K", fontsize=14
    )
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    fig2.savefig("butler_xs_aly.png", dpi=150, bbox_inches="tight")
    plt.close(fig2)
    print("Saved: butler_xs_aly.png")

    print("\nDone!")
