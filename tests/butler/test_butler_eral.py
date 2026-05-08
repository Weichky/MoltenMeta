"""
Butler Module Test - Er-Al System with Corrected RK Parameters
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
M_Er = 0.08890585
rho_Al_300 = 2702.0
rho_Er_300 = 4140.0

alpha_Al = 2.5e-5
alpha_Er = 3.5e-5

rho_Al = rho_Al_300 / (1 + alpha_Al * (T - 300))
rho_Er = rho_Er_300 / (1 + alpha_Er * (T - 300))

sigma_Al = 0.74
sigma_Er = 0.50

S_Al_val = S_CONSTANT * (N_A ** (1 / 3)) * ((M_Al / rho_Al) ** (2 / 3))
S_Er_val = S_CONSTANT * (N_A ** (1 / 3)) * ((M_Er / rho_Er) ** (2 / 3))

print(f"T = {T}K")
print(f"rho_Al = {rho_Al:.2f} kg/m3")
print(f"rho_Er = {rho_Er:.2f} kg/m3")
print(f"S_Al = {S_Al_val:.2f} m2/mol")
print(f"S_Er = {S_Er_val:.2f} m2/mol")
print()

C1 = -176486 + 55.6852 * T
C2 = -36685.5 + 23.4492 * T
C3 = 34349.1 - 8.23519 * T

print(f"C1 = {C1:.2f}")
print(f"C2 = {C2:.2f}")
print(f"C3 = {C3:.2f}")
print()


def GE(x_Er, T):
    x_Al = 1 - x_Er
    delta = x_Er - x_Al
    return x_Er * x_Al * C1 - C2 * delta + C3 * delta**2


def dGE_dx(x_Er, T):
    x_Al = 1 - x_Er
    delta = x_Er - x_Al
    ddelta_dx = 2
    term1 = (x_Al + x_Er * (-1)) * C1
    term2 = -C2 * ddelta_dx
    term3 = C3 * 2 * delta * ddelta_dx
    return term1 + term2 + term3


def G_E_partial_Er(x_Er, T):
    return GE(x_Er, T) + (1 - x_Er) * dGE_dx(x_Er, T)


def G_E_partial_Al(x_Er, T):
    return GE(x_Er, T) - x_Er * dGE_dx(x_Er, T)


def solve_butler(x_bulk):
    G_E_Er_bulk = G_E_partial_Er(x_bulk, T)
    G_E_Al_bulk = G_E_partial_Al(x_bulk, T)

    def butler_eqs(vars):
        sigma, x_Er_s, x_Al_s = vars
        x_Er_s = np.clip(x_Er_s, 1e-10, 1 - 1e-10)
        x_Al_s = np.clip(x_Al_s, 1e-10, 1 - 1e-10)

        G_E_Er_surf = BETA * G_E_Er_bulk
        G_E_Al_surf = BETA * G_E_Al_bulk

        ln_term_Er = (R * T / S_Er_val) * np.log(x_Er_s / x_bulk)
        ln_term_Al = (R * T / S_Al_val) * np.log(x_Al_s / (1 - x_bulk))

        GE_term_Er = (G_E_Er_surf - G_E_Er_bulk) / S_Er_val
        GE_term_Al = (G_E_Al_surf - G_E_Al_bulk) / S_Al_val

        eq1 = sigma - sigma_Er - ln_term_Er - GE_term_Er
        eq2 = sigma - sigma_Al - ln_term_Al - GE_term_Al
        eq3 = x_Er_s + x_Al_s - 1

        return [eq1, eq2, eq3]

    init_guesses = [
        [0.5, x_bulk, 1 - x_bulk],
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
    x_pred = np.linspace(0.01, 0.99, 100)
    sigma_values = []
    xEr_s_values = []
    xAl_bulk_values = []

    for x_Er in x_pred:
        sigma, xEr_s, _ = solve_butler(x_Er)
        sigma_values.append(sigma if sigma is not None else np.nan)
        xEr_s_values.append(xEr_s if xEr_s is not None else np.nan)
        xAl_bulk_values.append(1 - x_Er)

    sigma_values = np.array(sigma_values)
    xEr_s_values = np.array(xEr_s_values)
    xAl_bulk_values = np.array(xAl_bulk_values)

    xAl_s_values = 1 - xEr_s_values

    min_idx = np.nanargmin(sigma_values)
    max_idx = np.nanargmax(sigma_values)
    print(
        f"Sigma 最小值: {sigma_values[min_idx]:.4f} N/m at x(Al)={xAl_bulk_values[min_idx]:.3f}"
    )
    print(
        f"Sigma 最大值: {sigma_values[max_idx]:.4f} N/m at x(Al)={xAl_bulk_values[max_idx]:.3f}"
    )

    print("\n=== Plotting ===")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.plot(xAl_bulk_values, sigma_values, "b-", linewidth=2)
    ax1.axhline(
        y=sigma_Al,
        color="gray",
        linestyle="--",
        alpha=0.5,
        label=f"sigma_Al={sigma_Al}",
    )
    ax1.axhline(
        y=sigma_Er, color="gray", linestyle=":", alpha=0.5, label=f"sigma_Er={sigma_Er}"
    )
    ax1.set_xlabel("x^B (Al)", fontsize=12)
    ax1.set_ylabel("sigma (N/m)", fontsize=12)
    ax1.set_title(f"Er-Al Surface Tension (T={T}K)", fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_aspect("equal", adjustable="box")

    ax2.plot(xAl_bulk_values, xAl_s_values, "b-", linewidth=2, label="x^S")
    ax2.plot([0, 1], [0, 1], "k--", linewidth=1, label="x^S = x^B")
    ax2.set_xlabel("x^B (Al)", fontsize=12)
    ax2.set_ylabel("x^S (Al)", fontsize=12)
    ax2.set_title(f"Er-Al Surface Composition (T={T}K)", fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_aspect("equal", adjustable="box")

    plt.tight_layout()
    plt.savefig("eral_butler_1773.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: eral_butler_1773.png")
