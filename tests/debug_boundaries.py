"""
Debug script for Al-Mg Butler boundary conditions at T=973K
"""

import sys

sys.path.insert(0, "/Users/weichky/Repositories/MoltenMeta/src")

import numpy as np
from scipy.optimize import fsolve
from config.AlMg import sigma_i, density, MOLAR_MASS

T = 973
R = 8.314462618
N_A = 6.02214076e23
S_CONSTANT = 1.091
BETA = 0.75

print("=" * 70)
print(f"Debug: Al-Mg Butler at T={T}K")
print("=" * 70)

# Physical constants
M_Al = MOLAR_MASS[13]
M_Mg = MOLAR_MASS[12]
rho_Al = density(13, T)
rho_Mg = density(12, T)
S_Al = S_CONSTANT * (N_A ** (1 / 3)) * ((M_Al / rho_Al) ** (2 / 3))
S_Mg = S_CONSTANT * (N_A ** (1 / 3)) * ((M_Mg / rho_Mg) ** (2 / 3))
sigma_Al = sigma_i(13, T)
sigma_Mg = sigma_i(12, T)

print(f"\nPhysical parameters at T={T}K:")
print(f"  M_Al = {M_Al:.6f} kg/mol")
print(f"  M_Mg = {M_Mg:.6f} kg/mol")
print(f"  rho_Al = {rho_Al:.2f} kg/m3")
print(f"  rho_Mg = {rho_Mg:.2f} kg/m3")
print(f"  S_Al = {S_Al:.2f} m2/mol")
print(f"  S_Mg = {S_Mg:.2f} m2/mol")
print(f"  sigma_Al (pure) = {sigma_Al:.4f} N/m")
print(f"  sigma_Mg (pure) = {sigma_Mg:.4f} N/m")

# L coefficients
L0 = -12000 + 8.566 * T
L1 = 1894 - 3 * T
L2 = 2000.0

print(f"\nL coefficients at T={T}K:")
print(f"  L0 = {L0:.2f}")
print(f"  L1 = {L1:.2f}")
print(f"  L2 = {L2:.2f}")


def GE(x_Al, T):
    """GE = x_Al * x_Mg * [L0 + L1*(2x-1) + L2*(2x-1)^2]"""
    x_Mg = 1 - x_Al
    delta = 2 * x_Al - 1
    return x_Al * x_Mg * (L0 + L1 * delta + L2 * delta**2)


def dGE_dx(x_Al, T):
    """dGE/dx for the Redlich-Kister polynomial"""
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


print(f"\nGE at key compositions:")
for x in [0.0, 0.01, 0.5, 0.99, 1.0]:
    print(f"  x_Al={x:.2f}: GE = {GE(x, T):.4f} J/mol")


def solve_butler(x_bulk_Al, verbose=False):
    """Solve Butler equation for given bulk composition"""

    G_E_Al_bulk = G_E_partial_Al(x_bulk_Al, T)
    G_E_Mg_bulk = G_E_partial_Mg(x_bulk_Al, T)

    if verbose:
        print(f"    G_E_Al_bulk = {G_E_Al_bulk:.4f}")
        print(f"    G_E_Mg_bulk = {G_E_Mg_bulk:.4f}")

    # At x=1, force surface to be pure Al
    if x_bulk_Al > 0.9999:
        # At pure Al, surface must be pure Al, sigma = sigma_Al
        return sigma_Al, 1.0, 0.0

    # At x=0, force surface to be pure Mg
    if x_bulk_Al < 0.0001:
        # At pure Mg, surface must be pure Mg, sigma = sigma_Mg
        return sigma_Mg, 0.0, 1.0

    def equations(vars):
        sigma, x_Al_s, x_Mg_s = vars
        x_Al_s = np.clip(x_Al_s, 1e-15, 1 - 1e-15)
        x_Mg_s = np.clip(x_Mg_s, 1e-15, 1 - 1e-15)

        # Surface excess GE (using bulk GE with BETA factor)
        G_E_Al_surf = BETA * G_E_Al_bulk
        G_E_Mg_surf = BETA * G_E_Mg_bulk

        # Log terms
        if x_bulk_Al > 1e-10:
            ln_Al = (R * T / S_Al) * np.log(x_Al_s / x_bulk_Al)
        else:
            ln_Al = 0

        if (1 - x_bulk_Al) > 1e-10:
            ln_Mg = (R * T / S_Mg) * np.log(x_Mg_s / (1 - x_bulk_Al))
        else:
            ln_Mg = 0

        # GE terms
        GE_term_Al = (G_E_Al_surf - G_E_Al_bulk) / S_Al
        GE_term_Mg = (G_E_Mg_surf - G_E_Mg_bulk) / S_Mg

        # Butler equations
        eq1 = sigma - sigma_Al - ln_Al - GE_term_Al
        eq2 = sigma - sigma_Mg - ln_Mg - GE_term_Mg
        eq3 = x_Al_s + x_Mg_s - 1

        return [eq1, eq2, eq3]

    # Try multiple initial guesses
    init_guesses = [
        [sigma_Al, 0.5, 0.5],
        [sigma_Mg, 0.5, 0.5],
        [(sigma_Al + sigma_Mg) / 2, 0.5, 0.5],
        [0.7, 0.9, 0.1],
        [0.7, 0.1, 0.9],
        [0.5, 0.01, 0.99],
        [0.5, 0.99, 0.01],
        [0.8, 0.5, 0.5],
    ]

    for x0 in init_guesses:
        sol, info, ier, msg = fsolve(equations, x0, full_output=True)
        if ier == 1 and 0 < sol[1] < 1 and 0 < sol[2] < 1:
            return sol[0], sol[1], sol[2]

    return None, None, None


print(f"\n" + "=" * 70)
print("Boundary and test composition results:")
print("=" * 70)

test_points = [
    (0.0, "pure Mg"),
    (0.001, "near pure Mg"),
    (0.01, "1% Al"),
    (0.1, "10% Al"),
    (0.5, "50% Al"),
    (0.9, "90% Al"),
    (0.99, "99% Al"),
    (0.999, "near pure Al"),
    (1.0, "pure Al"),
]

for x_bulk, label in test_points:
    sigma, x_s_Al, x_s_Mg = solve_butler(x_bulk)
    if sigma is not None:
        print(
            f"x_bulk_Al={x_bulk:.3f} ({label:12s}): sigma={sigma:.4f} N/m, x_s_Al={x_s_Al:.4f}"
        )
    else:
        print(f"x_bulk_Al={x_bulk:.3f} ({label:12s}): FAILED")

print(f"\n" + "=" * 70)
print("Experimental comparison:")
print("=" * 70)

x_exp = [0.990017, 0.962830, 0.938312, 0.902031]
exp_sigma = [0.865, 0.862, 0.857, 0.846]

for x, exp in zip(x_exp, exp_sigma):
    sigma, x_s_Al, x_s_Mg = solve_butler(x)
    if sigma is not None:
        diff_pct = 100 * (sigma - exp) / exp
        print(f"x={x:.6f}: calc={sigma:.4f}, exp={exp:.4f}, diff={diff_pct:.2f}%")
    else:
        print(f"x={x:.6f}: FAILED")

print(f"\n" + "=" * 70)
print("Analysis:")
print("=" * 70)
print(f"At x=0 (pure Mg), sigma should approach sigma_Mg = {sigma_Mg:.4f} N/m")
print(f"At x=1 (pure Al), sigma should approach sigma_Al = {sigma_Al:.4f} N/m")
