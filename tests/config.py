"""
Shared Test Configuration for Algorithm Chain Tests
Alters configuration for GP, RK, and Butler modules
"""

ELEM_A = 13
ELEM_B = 12
ELEM_NAMES = {12: "Mg", 13: "Al", 14: "Si"}

X_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
T_VALUES = [800, 900, 1000]

NOISE_STD = 0.1
KERNEL_TYPE = "rbf"
RK_ORDER = 2

T_PLOT = 850

OUTPUT_PREFIX = "gp"
