/**
 * Triangular Grid Generator - Generate triangular grid points for ternary systems.
 *
 * Generates points on the triangular plane x_A + x_B + x_C = 1 with x_A, x_B, x_C >= 0.
 * This is shared by all geometric models (Kohler, Toop, Maggianu, Hillert-Toop).
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

py::array_t<double> generateTriangularGrid(int n_points) {
    std::vector<double> x_A, x_B, x_C;

    if (n_points <= 0) {
        return py::array_t<double>(0);
    }

    double step = 1.0 / (n_points - 1);

    for (int i = 0; i < n_points; ++i) {
        double x_A_val = i * step;
        int n_B = n_points - i;
        double step_B = (1.0 - x_A_val) / (n_B > 1 ? n_B - 1 : 1);

        for (int j = 0; j < n_B; ++j) {
            double x_B_val = j * step_B;
            double x_C_val = 1.0 - x_A_val - x_B_val;
            x_A.push_back(x_A_val);
            x_B.push_back(x_B_val);
            x_C.push_back(x_C_val);
        }
    }

    py::array_t<double> result_A(x_A.size());
    py::array_t<double> result_B(x_B.size());
    py::array_t<double> result_C(x_C.size());

    auto* ptr_A = static_cast<double*>(result_A.request().ptr);
    auto* ptr_B = static_cast<double*>(result_B.request().ptr);
    auto* ptr_C = static_cast<double*>(result_C.request().ptr);

    for (size_t i = 0; i < x_A.size(); ++i) {
        ptr_A[i] = x_A[i];
        ptr_B[i] = x_B[i];
        ptr_C[i] = x_C[i];
    }

    return py::make_tuple(result_A, result_B, result_C);
}

PYBIND11_MODULE(triangular_grid, m) {
    m.def("generateTriangularGrid", &generateTriangularGrid,
          "Generate triangular grid points for ternary system. "
          "Returns tuple of (x_A, x_B, x_C) arrays where x_A + x_B + x_C = 1");
}