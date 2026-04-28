/**
 * Kohler module for calculating thermodynamic properties.
 *
 * Parameter Order Convention: AB -> AC -> BC (alphabetical)
 *   - x_A, x_B, x_C: mole fractions
 *   - Z_AB, Z_AC, Z_BC: binary properties at corresponding compositions
 *
 * Output: Z_ABC
 *
 * Original formula in LaTeX:
 * $$
 * Z_{ABC} = (x_A+x_B)^2 \cdot Z_{AB}\left(\frac{x_A}{x_A+x_B}, \frac{x_B}{x_A+x_B}\right)
 *         + (x_B+x_C)^2 \cdot Z_{BC}\left(\frac{x_B}{x_B+x_C}, \frac{x_C}{x_B+x_C}\right)
 *         + (x_A+x_C)^2 \cdot Z_{AC}\left(\frac{x_A}{x_A+x_C}, \frac{x_C}{x_A+x_C}\right)
 * $$
 *
 * This is the cyclic symmetric form of the Toop model, where each term follows
 * the same pattern as the Toop's third term.
 **/

// This module is also an official example of how to create a module for MoltenMeta.
// For more information, please refer to our official documentation.

# include <pybind11/pybind11.h>
# include <pybind11/numpy.h>
# include <cmath>

namespace py = pybind11;

double calculateSingleProperty(double x_A, double x_B, double x_C, double Z_AB, double Z_AC, double Z_BC) {
    double term_AB = (x_A + x_B) * (x_A + x_B) * Z_AB;
    double term_AC = (x_A + x_C) * (x_A + x_C) * Z_AC;
    double term_BC = (x_B + x_C) * (x_B + x_C) * Z_BC;
    return term_AB + term_AC + term_BC;
}

// Note: This is an optimized version of the loop.
// For clarity, use calculateSingleProperty() in single-value scenarios.
py::array_t<double> calculatePropertyList(
    py::array_t<double> x_A_list,
    py::array_t<double> x_B_list,
    py::array_t<double> x_C_list,
    py::array_t<double> Z_AB_list,
    py::array_t<double> Z_AC_list,
    py::array_t<double> Z_BC_list) {

    size_t n = x_A_list.size();

    // request() ensures the array is contiguous C-order and returns buffer info
    // We access ptr directly to avoid Python/C API overhead on each element access
    double* ptr_xA = static_cast<double*>(x_A_list.request().ptr);
    double* ptr_xB = static_cast<double*>(x_B_list.request().ptr);
    double* ptr_xC = static_cast<double*>(x_C_list.request().ptr);
    double* ptr_AB = static_cast<double*>(Z_AB_list.request().ptr);
    double* ptr_AC = static_cast<double*>(Z_AC_list.request().ptr);
    double* ptr_BC = static_cast<double*>(Z_BC_list.request().ptr);

    // Create result array and get its buffer pointer for writing
    py::array_t<double> result(n);
    double* ptr_res = static_cast<double*>(result.request().ptr);

    // Expanded from calculateSingleProperty() to avoid function call overhead
    for (Py_ssize_t i = 0; i < n; ++i) {
        double x_A = ptr_xA[i];
        double x_B = ptr_xB[i];
        double x_C = ptr_xC[i];

        double term_AB = (x_A + x_B) * (x_A + x_B) * ptr_AB[i];
        double term_BC = (x_B + x_C) * (x_B + x_C) * ptr_BC[i];
        double term_AC = (x_A + x_C) * (x_A + x_C) * ptr_AC[i];

        ptr_res[i] = term_AB + term_BC + term_AC;
    }

    return result;
}

PYBIND11_MODULE(kohler_algorithm, m) {
    m.def("calculateSingleProperty", &calculateSingleProperty, "Calculate Z_ABC for a single composition point");
    m.def("calculatePropertyList", &calculatePropertyList, "Calculate Z_ABC for an array of composition points");
}