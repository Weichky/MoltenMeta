"""
Al-Er System Configuration for Butler Tests
T = 1773K
"""

ELEM_A = 13
ELEM_B = 39
T = 1773

SIGMA_I = {
    ELEM_A: 0.74,
    ELEM_B: 0.640,
}


def sigma_i(elem: int, T: float) -> float:
    return SIGMA_I.get(elem, 0.0)


MOLAR_MASS = {
    ELEM_A: 0.0269815,
    ELEM_B: 0.16726,
}

RHO_300 = {
    ELEM_A: 2702.0,
    ELEM_B: 9050.0,
}

THERMAL_EXPANSION = {
    ELEM_A: 2.5e-5,
    ELEM_B: 3.5e-5,
}


def density(elem: int, T: float) -> float:
    alpha = THERMAL_EXPANSION[elem]
    return RHO_300[elem] / (1 + alpha * (T - 300))


L_COEFFS = {
    "L0": [-176486, 55.6852],
    "L1": [36685.5, -23.4492],
    "L2": [34349.1, -8.23519],
}
