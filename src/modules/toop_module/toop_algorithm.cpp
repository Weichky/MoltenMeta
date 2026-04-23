/**
 * Toop module for calculating thermodynamic properties.
 * 
 * Input:
 *  - x_B: mole fraction of element B [0, 1]
 *  - x_C: mole fraction of element C [0, 1]
 *  - Z_AB: Any thermodynamic property at composition of x_B B and 1 - x_B - x_C A
 *  - Z_AC: Any thermodynamic property at composition of x_C C and 1 - x_B - x_C A
 *  - Z_BC: Any thermodynamic property at composition of x_B B and x_C C
 * 
 * Output: Z_ABC
 * 
 * Original formula in LaTeX:
 * $$
 * Z_{ABC} = \frac{x_B}{x_B+x_C} \cdot Z_{AB}(x_A, 1-x_A) + \frac{x_C}{x_B+x_C} \cdot Z_{AC}(x_A, 1-x_A) + (x_B+x_C)^2 \cdot Z_{BC}\left(\frac{x_B}{x_B+x_C}, \frac{x_C}{x_B+x_C}\right)
 * $$
 **/

// This module is also an official example of how to create a module for MoltenMeta.
// For more information, please refer to our official documentation.

# include <pybind11/pybind11.h>
# include <pybind11/numpy.h>
# include <cmath>

namespace py = pybind11;

double calculateSingleProperty(double x_B, double x_C, double Z_AB, double Z_AC, double Z_BC) {
    double frac_B = x_B / (x_B + x_C);
    double frac_C = x_C / (x_B + x_C);
    double frac_BC_squared = (x_B + x_C) * (x_B + x_C);
    return frac_B * Z_AB + frac_C * Z_AC + frac_BC_squared * Z_BC;
}

// Note: This is an optimized version of the loop.
// For clarity, use calculateSingleProperty() in single-value scenarios.
py::array_t<double> calculatePropertyList(
    py::array_t<double> x_B_list,
    py::array_t<double> x_C_list,
    py::array_t<double> Z_AB_list,
    py::array_t<double> Z_AC_list,
    py::array_t<double> Z_BC_list) {

    size_t n = x_B_list.size();

    // request() ensures the array is contiguous C-order and returns buffer info
    // We access ptr directly to avoid Python/C API overhead on each element access
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
        double x_B = ptr_xB[i];
        double x_C = ptr_xC[i];
        double sum = x_B + x_C;

        double frac_B = x_B / sum;
        double frac_C = x_C / sum;
        double frac_BC_squared = sum * sum;

        ptr_res[i] = frac_B * ptr_AB[i] + frac_C * ptr_AC[i] + frac_BC_squared * ptr_BC[i];
    }

    return result;
}

PYBIND11_MODULE(toop_algorithm, m) {
    m.def("calculateSingleProperty", &calculateSingleProperty, "Calculate Z_ABC for a single composition point");
    m.def("calculatePropertyList", &calculatePropertyList, "Calculate Z_ABC for an array of composition points");
}