"""
Butler Module Test - Al-Mg System
Temperature: 1773K
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve


R = 8.314462618
N_A = 6.02214076e23
S_CONSTANT = 1.091
T = 1773
BETA = 0.75

M_Al = 0.0269815
M_Mg = 0.02430
rho_Al_300 = 2702.0
rho_Mg_300 = 1738.0

alpha_Al = 2.5e-5
alpha_Mg = 2.7e-5

rho_Al = rho_Al_300 / (1 + alpha_Al * (T - 300))
rho_Mg = rho_Mg_300 / (1 + alpha_Mg * (T - 300))

sigma_Al = 0.74
sigma_Mg = 0.356

S_Al_val = S_CONSTANT * (N_A ** (1 / 3)) * ((M_Al / rho_Al) ** (2 / 3))
S_Mg_val = S_CONSTANT * (N_A ** (1 / 3)) * ((M_Mg / rho_Mg) ** (2 / 3))

print(f"T = {T}K")
print(f"rho_Al = {rho_Al:.2f} kg/m3")
print(f"rho_Mg = {rho_Mg:.2f} kg/m3")
print(f"S_Al = {S_Al_val:.2f} m2/mol")
print(f"S_Mg = {S_Mg_val:.2f} m2/mol")
print()

# Al-Mg RK 参数（文献值，正确）
# L0 = -12000 + 8.566 * T
# L1 = 1894 - 3 * T  (注意：没有除以1000)
# L2 = 2000
L0 = -12000 + 8.566 * T
L1 = 1894 - 3 * T
L2 = 2000

print(f"L0 = {L0:.2f}")
print(f"L1 = {L1:.2f}")
print(f"L2 = {L2:.2f}")
print()


def GE(x_Al, T):
    """Al-Mg G^E = x1*x2 * [L0 + L1*(2x-1) + L2*(2x-1)^2]"""
    x_Mg = 1 - x_Al
    delta = 2 * x_Al - 1
    return x_Al * x_Mg * (L0 + L1 * delta + L2 * delta**2)


def dGE_dx(x_Al, T):
    x_Mg = 1 - x_Al
    delta = 2 * x_Al - 1
    ddelta_dx = 2
    term_poly = L0 + L1 * delta + L2 * delta**2
    dpoly = L1 * ddelta_dx + L2 * 2 * delta * ddelta_dx
    return (x_Mg - x_Al) * term_poly + x_Al * x_Mg * dpoly


def G_E_partial_Al(x_Al, T):
    return GE(x_Al, T) + (1 - x_Al) * dGE_dx(x_Al, T)


def G_E_partial_Mg(x_Al, T):
    return GE(x_Al, T) - x_Al * dGE_dx(x_Al, T)


def solve_butler(x_bulk_Al):
    G_E_Al_bulk = G_E_partial_Al(x_bulk_Al, T)
    G_E_Mg_bulk = G_E_partial_Mg(x_bulk_Al, T)

    def butler_eqs(vars):
        sigma, x_Al_s, x_Mg_s = vars
        x_Al_s = np.clip(x_Al_s, 1e-10, 1 - 1e-10)
        x_Mg_s = np.clip(x_Mg_s, 1e-10, 1 - 1e-10)

        G_E_Al_surf = BETA * G_E_Al_bulk
        G_E_Mg_surf = BETA * G_E_Mg_bulk

        ln_term_Al = (R * T / S_Al_val) * np.log(x_Al_s / x_bulk_Al)
        ln_term_Mg = (R * T / S_Mg_val) * np.log(x_Mg_s / (1 - x_bulk_Al))

        GE_term_Al = (G_E_Al_surf - G_E_Al_bulk) / S_Al_val
        GE_term_Mg = (G_E_Mg_surf - G_E_Mg_bulk) / S_Mg_val

        eq1 = sigma - sigma_Al - ln_term_Al - GE_term_Al
        eq2 = sigma - sigma_Mg - ln_term_Mg - GE_term_Mg
        eq3 = x_Al_s + x_Mg_s - 1

        return [eq1, eq2, eq3]

    init_guesses = [
        [0.5, x_bulk_Al, 1 - x_bulk_Al],
        [0.3, 0.1, 0.9],
        [0.7, 0.9, 0.1],
        [0.99, 0.99, 0.01],
        [0.01, 0.01, 0.99],
        [0.5, 0.5, 0.5],
    ]

    for x0 in init_guesses:
        sol = fsolve(butler_eqs, x0, full_output=True)
        if sol[2] == 1:
            if 0 < sol[0][1] < 1 and 0 < sol[0][2] < 1:
                return sol[0][0], sol[0][1], sol[0][2]
    return None, None, None


if __name__ == "__main__":
    print("=== G^E at key compositions ===")
    for x in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        print(f"x(Al)={x:.1f}: G^E = {GE(x, T) / 1000:.4f} kJ/mol")

    x_pred = np.linspace(0.01, 0.99, 100)
    sigma_values = []
    xAl_s_values = []

    for x_Al in x_pred:
        sigma, x_Al_s, _ = solve_butler(x_Al)
        sigma_values.append(sigma if sigma is not None else np.nan)
        xAl_s_values.append(x_Al_s if x_Al_s is not None else np.nan)

    sigma_values = np.array(sigma_values)
    xAl_s_values = np.array(xAl_s_values)

    min_idx = np.nanargmin(sigma_values)
    max_idx = np.nanargmax(sigma_values)
    print()
    print(
        f"Sigma 最小值: {sigma_values[min_idx]:.4f} N/m at x(Al)={x_pred[min_idx]:.3f}"
    )
    print(
        f"Sigma 最大值: {sigma_values[max_idx]:.4f} N/m at x(Al)={x_pred[max_idx]:.3f}"
    )

    print("\n=== Plotting ===")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.plot(x_pred, sigma_values, "b-", linewidth=2)
    ax1.axhline(
        y=sigma_Al,
        color="gray",
        linestyle="--",
        alpha=0.5,
        label=f"sigma_Al={sigma_Al}",
    )
    ax1.axhline(
        y=sigma_Mg, color="gray", linestyle=":", alpha=0.5, label=f"sigma_Mg={sigma_Mg}"
    )
    ax1.set_xlabel("x^B (Al)", fontsize=12)
    ax1.set_ylabel("sigma (N/m)", fontsize=12)
    ax1.set_title(f"Al-Mg Surface Tension (T={T}K)", fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_aspect("equal", adjustable="box")

    ax2.plot(x_pred, xAl_s_values, "b-", linewidth=2, label="x^S")
    ax2.plot([0, 1], [0, 1], "k--", linewidth=1, label="x^S = x^B")
    ax2.set_xlabel("x^B (Al)", fontsize=12)
    ax2.set_ylabel("x^S (Al)", fontsize=12)
    ax2.set_title(f"Al-Mg Surface Composition (T={T}K)", fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_aspect("equal", adjustable="box")

    plt.tight_layout()
    plt.savefig("almg_butler_1773.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: alm g_butler_1773.png")
