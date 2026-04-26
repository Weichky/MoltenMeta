/**
 * Maggianu module for calculating thermodynamic properties.
 *
 * Input:
 *  - x_A: mole fraction of element A [0, 1]
 *  - x_B: mole fraction of element B [0, 1]
 *  - x_C: mole fraction of element C [0, 1]
 *  - Z_AB: Binary property at normalized composition V_AB
 *  - Z_BC: Binary property at normalized composition V_BC
 *  - Z_AC: Binary property at normalized composition V_AC
 *
 * Output: Z_ABC
 *
 * Formula in LaTeX:
 * $$
 * Z_{ABC} = \sum_{i<j} \frac{x_i x_j}{V_{ij} V_{ji}} Z_{ij}\left(V_{ij}, V_{ji}\right)
 * $$
 *
 * Where (normalized):
 *   V_{AB} = (1 + x_A - x_B) / 2
 *   V_{BA} = (1 + x_B - x_A) / 2
 *   V_{AC} = (1 + x_A - x_C) / 2
 *   V_{CA} = (1 + x_C - x_A) / 2
 *   V_{BC} = (1 + x_B - x_C) / 2
 *   V_{CB} = (1 + x_C - x_B) / 2
 *
 * Expanded form (3 terms, cyclic symmetric):
 * $$
 * Z_{ABC} = \frac{x_A x_B}{V_{AB} V_{BA}} Z_{AB}(V_{AB})
 *         + \frac{x_A x_C}{V_{AC} V_{CA}} Z_{AC}(V_{AC})
 *         + \frac{x_B x_C}{V_{BC} V_{CB}} Z_{BC}(V_{BC})
 * $$
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

namespace py = pybind11;

double calculateSingleProperty(double x_A, double x_B, double x_C, double Z_AB, double Z_BC, double Z_AC) {
    double V_AB = (1.0 + x_A - x_B) / 2.0;
    double V_BA = (1.0 + x_B - x_A) / 2.0;
    double V_AC = (1.0 + x_A - x_C) / 2.0;
    double V_CA = (1.0 + x_C - x_A) / 2.0;
    double V_BC = (1.0 + x_B - x_C) / 2.0;
    double V_CB = (1.0 + x_C - x_B) / 2.0;

    double term_AB = (x_A * x_B) / (V_AB * V_BA) * Z_AB;
    double term_AC = (x_A * x_C) / (V_AC * V_CA) * Z_AC;
    double term_BC = (x_B * x_C) / (V_BC * V_CB) * Z_BC;

    return term_AB + term_AC + term_BC;
}

py::array_t<double> calculatePropertyList(
    py::array_t<double> x_A_list,
    py::array_t<double> x_B_list,
    py::array_t<double> x_C_list,
    py::array_t<double> Z_AB_list,
    py::array_t<double> Z_BC_list,
    py::array_t<double> Z_AC_list) {

    size_t n = x_A_list.size();

    double* ptr_xA = static_cast<double*>(x_A_list.request().ptr);
    double* ptr_xB = static_cast<double*>(x_B_list.request().ptr);
    double* ptr_xC = static_cast<double*>(x_C_list.request().ptr);
    double* ptr_AB = static_cast<double*>(Z_AB_list.request().ptr);
    double* ptr_BC = static_cast<double*>(Z_BC_list.request().ptr);
    double* ptr_AC = static_cast<double*>(Z_AC_list.request().ptr);

    py::array_t<double> result(n);
    double* ptr_res = static_cast<double*>(result.request().ptr);

    for (Py_ssize_t i = 0; i < n; ++i) {
        double x_A = ptr_xA[i];
        double x_B = ptr_xB[i];
        double x_C = ptr_xC[i];

        double V_AB = (1.0 + x_A - x_B) / 2.0;
        double V_BA = (1.0 + x_B - x_A) / 2.0;
        double V_AC = (1.0 + x_A - x_C) / 2.0;
        double V_CA = (1.0 + x_C - x_A) / 2.0;
        double V_BC = (1.0 + x_B - x_C) / 2.0;
        double V_CB = (1.0 + x_C - x_B) / 2.0;

        double term_AB = (x_A * x_B) / (V_AB * V_BA) * ptr_AB[i];
        double term_AC = (x_A * x_C) / (V_AC * V_CA) * ptr_AC[i];
        double term_BC = (x_B * x_C) / (V_BC * V_CB) * ptr_BC[i];

        ptr_res[i] = term_AB + term_AC + term_BC;
    }

    return result;
}

PYBIND11_MODULE(maggianu_algorithm, m) {
    m.def("calculateSingleProperty", &calculateSingleProperty, "Calculate Z_ABC for a single composition point");
    m.def("calculatePropertyList", &calculatePropertyList, "Calculate Z_ABC for an array of composition points");
}