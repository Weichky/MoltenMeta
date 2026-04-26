/**
 * Hillert-Toop module for calculating thermodynamic properties.
 *
 * Input:
 *  - x_A: mole fraction of element A [0, 1]
 *  - x_B: mole fraction of element B [0, 1]
 *  - x_C: mole fraction of element C [0, 1]
 *  - Z_AB: Any thermodynamic property at composition of x_A A and x_B B
 *  - Z_AC: Any thermodynamic property at composition of x_A A and x_C C
 *  - Z_BC: Any thermodynamic property at composition of x_B B and x_C C
 *
 * Output: Z_ABC
 *
 * Formula in LaTeX:
 * $$
 * Z_{ABC} = \frac{x_B}{x_B+x_C} \cdot Z_{AB}(x_A, 1-x_A) + \frac{x_C}{x_B+x_C} \cdot Z_{AC}(x_A, 1-x_A) + \frac{x_B x_C}{V_{BC} V_{CB}} Z_{BC}(V_{BC})
 * $$
 *
 * Where:
 *   V_{BC} = (1 + x_B - x_C) / 2
 *   V_{CB} = (1 + x_C - x_B) / 2
 *
 * The third term uses normalized composition V instead of simple fraction.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

namespace py = pybind11;

double calculateSingleProperty(double x_A, double x_B, double x_C, double Z_AB, double Z_AC, double Z_BC) {
    double sum_BC = x_B + x_C;
    double frac_B = (sum_BC > 0) ? x_B / sum_BC : 0.0;
    double frac_C = (sum_BC > 0) ? x_C / sum_BC : 0.0;

    double V_BC = (1.0 + x_B - x_C) / 2.0;
    double V_CB = (1.0 + x_C - x_B) / 2.0;

    double term_AB = frac_B * Z_AB;
    double term_AC = frac_C * Z_AC;
    double term_BC = (x_B * x_C) / (V_BC * V_CB) * Z_BC;

    return term_AB + term_AC + term_BC;
}

py::array_t<double> calculatePropertyList(
    py::array_t<double> x_A_list,
    py::array_t<double> x_B_list,
    py::array_t<double> x_C_list,
    py::array_t<double> Z_AB_list,
    py::array_t<double> Z_AC_list,
    py::array_t<double> Z_BC_list) {

    size_t n = x_A_list.size();

    double* ptr_xA = static_cast<double*>(x_A_list.request().ptr);
    double* ptr_xB = static_cast<double*>(x_B_list.request().ptr);
    double* ptr_xC = static_cast<double*>(x_C_list.request().ptr);
    double* ptr_AB = static_cast<double*>(Z_AB_list.request().ptr);
    double* ptr_AC = static_cast<double*>(Z_AC_list.request().ptr);
    double* ptr_BC = static_cast<double*>(Z_BC_list.request().ptr);

    py::array_t<double> result(n);
    double* ptr_res = static_cast<double*>(result.request().ptr);

    for (Py_ssize_t i = 0; i < n; ++i) {
        double x_A = ptr_xA[i];
        double x_B = ptr_xB[i];
        double x_C = ptr_xC[i];

        double sum_BC = x_B + x_C;
        double frac_B = (sum_BC > 0) ? x_B / sum_BC : 0.0;
        double frac_C = (sum_BC > 0) ? x_C / sum_BC : 0.0;

        double V_BC = (1.0 + x_B - x_C) / 2.0;
        double V_CB = (1.0 + x_C - x_B) / 2.0;

        double term_AB = frac_B * ptr_AB[i];
        double term_AC = frac_C * ptr_AC[i];
        double term_BC = (x_B * x_C) / (V_BC * V_CB) * ptr_BC[i];

        ptr_res[i] = term_AB + term_AC + term_BC;
    }

    return result;
}

PYBIND11_MODULE(hillert_toop_algorithm, m) {
    m.def("calculateSingleProperty", &calculateSingleProperty, "Calculate Z_ABC for a single composition point");
    m.def("calculatePropertyList", &calculatePropertyList, "Calculate Z_ABC for an array of composition points");
}