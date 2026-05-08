"""
Al-Mg System Configuration for Butler Tests
T = 1773K
"""

ELEM_A = 13
ELEM_B = 12
T = 1773

MOLAR_MASS = {
    ELEM_A: 0.026982,
    ELEM_B: 0.024305,
}

RHO_300 = {
    ELEM_A: 2702.0,
    ELEM_B: 1738.0,
}

THERMAL_EXPANSION = {
    ELEM_A: 2.5e-5,
    ELEM_B: 2.7e-5,
}


def density(elem: int, T: float) -> float:
    alpha = THERMAL_EXPANSION[elem]
    return RHO_300[elem] / (1 + alpha * (T - 300))


def sigma_i(elem: int, T: float) -> float:
    if elem == 13:
        return (871.0 - 0.155 * (T - 933)) / 1000.0
    elif elem == 12:
        return (577.0 - 0.26 * (T - 923)) / 1000.0
    raise ValueError(f"Unknown element: {elem}")


L_COEFFS = {
    "L0": [-12000, 8.566],
    "L1": [1894, -3],
    "L2": [2000.0, 0.0],
}
