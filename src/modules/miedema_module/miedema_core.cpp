/**
 * Miedema module for calculating enthalpy of mixing.
 * 
 * Input:
 *   - x_A: mole fraction of element A [0, 1]
 *   - elemA/elemB: ElementProperties {V_23, phi, n_WS_13, mu}
 *   - miedemaConst: {a, p, q, r_over_p}
 * 
 * Output: ΔH_AB in kJ/mol (per mole of alloy)
 * 
 * Ref: Miedema et al., Philips Tech. Rev. (1973)


 * Original formula in LaTeX: 
 * $$
 * \Delta H_{AB}=f_{AB}\frac{x_Ax_B\left[1+\mu_Ax_B\left(\phi_A-\phi_B\right)\right]\left[1+\mu_Bx_A\left(\phi_B-\phi_A\right)\right]}{x_AV_{A}^{2/3}\left[1+\mu_Ax_B\left(\phi_A-\phi_B\right)\right]+x_BV_{B}^{2/3}\left[1+\mu_Bx_A\left(\phi_B-\phi_A\right)\right]}
 * $$
 * where:
 * $$
 * f_{AB}=2pV_A^{2/3}V_B^{2/3}\frac{\frac{q}{p}\left(\Delta n^{1/3}_{WS}\right)^2-\left(\Delta\phi\right)^2-a\frac{r}{p}}{\left(n^{1/3}_{WS}\right)^{-1}_A+\left(n^{1/3}_{WS}\right)^{-1}_B}
 * $$
**/

// This module is also an official example of how to create a module for MoltenMeta.
// For more information, please refer to our official documentation.

# include <pybind11/pybind11.h>
# include <pybind11/numpy.h>
# include <cmath>

struct ElementProperties
{
    double V_23;
    double phi;
    double n_WS_13;
    double mu;
};

struct MiedemaConst
{
    double a;
    double p;
    double q;
    double r_over_p;
};

namespace py = pybind11;
class MiedemaCore {
    public:
        MiedemaCore(ElementProperties elemA, ElementProperties elemB, MiedemaConst miedemaConst)
            : elemA(elemA), elemB(elemB), miedemaConst(miedemaConst) {
            precompute();
        }

        double calculateSingle(double x_A) const{
            const double x_B = 1 - x_A;
            double numerator = x_A * x_B * (1 + elemA.mu * x_B * delta_phi) * (1 - elemB.mu * x_A * delta_phi);
            double denominator = x_A * elemA.V_23 * (1 + elemA.mu * x_B * delta_phi)
                + x_B * elemB.V_23 * (1 - elemB.mu * x_A * delta_phi);

            return f_AB * numerator / denominator;
        }

// Note: This is an optimized version of the loop.
// For clarity, use calculateSingle() in single-value scenarios.
        py::array_t<double> calculateRange(double x_A_start, double x_A_end, int num) const {
            py::array_t<double> result(num);
            double *ptr = static_cast<double*>(result.request().ptr);

            double step = (num > 1) ? (x_A_end - x_A_start) / (num - 1) : 0;

            // Precompute repeated values to avoid per-iteration overhead
            const double muA_delta = elemA.mu * delta_phi;
            const double muB_delta = elemB.mu * delta_phi;
            const double VA = elemA.V_23;
            const double VB = elemB.V_23;

            for (int i = 0; i < num; ++i) {
                double x_A = (i == num - 1) ? x_A_end : x_A_start + i * step;
                double x_B = 1 - x_A;

                // Expanded from calculateSingle() to avoid function call overhead
                const double term1 = 1 + muA_delta * x_B;
                const double term2 = 1 - muB_delta * x_A;

                const double numerator = x_A * x_B * term1 * term2;
                const double denominator = x_A * VA * term1 + x_B * VB * term2;

                ptr[i] = f_AB * numerator / denominator;
            }

            return result;
        }

        py::array_t<double> calculateSingleBatch(py::array_t<double> x_array) const {
            const Py_ssize_t num = x_array.size();
            py::array_t<double> result(num);
            double *ptr_res = static_cast<double*>(result.request().ptr);
            const double *ptr_x = static_cast<double*>(x_array.request().ptr);

            // Precompute repeated values
            const double muA_delta = elemA.mu * delta_phi;
            const double muB_delta = elemB.mu * delta_phi;
            const double VA = elemA.V_23;
            const double VB = elemB.V_23;

            for (Py_ssize_t i = 0; i < num; ++i) {
                const double x_A = ptr_x[i];
                const double x_B = 1 - x_A;

                const double term1 = 1 + muA_delta * x_B;
                const double term2 = 1 - muB_delta * x_A;

                const double numerator = x_A * x_B * term1 * term2;
                const double denominator = x_A * VA * term1 + x_B * VB * term2;

                ptr_res[i] = f_AB * numerator / denominator;
            }

            return result;
        }

    private:
        ElementProperties elemA, elemB;
        MiedemaConst miedemaConst;

        double f_AB;
        double delta_phi;

        void precompute() {
            // Calculate f_AB based on the provided properties and constants

            // Define delta_phi as the difference in electronegativity between A and B
            // Thus, phi_B - phi_A = - delta_phi
            delta_phi = elemA.phi - elemB.phi;

            double delta_n_WS_13 = elemA.n_WS_13 - elemB.n_WS_13;

            double pre_factor = 2 * miedemaConst.p * elemA.V_23 * elemB.V_23;
            double numerator = miedemaConst.q / miedemaConst.p 
                * delta_n_WS_13 * delta_n_WS_13 - delta_phi * delta_phi - miedemaConst.a * miedemaConst.r_over_p;

            double denominator =1 / elemA.n_WS_13 + 1 / elemB.n_WS_13;
            // Calculate f_AB
            f_AB = pre_factor * numerator / denominator;
        }

};

// To know how to use pybind11, please refer to pybind11's official documentation.
// We don't provide instructions here.
PYBIND11_MODULE(miedema_core, m) {
    py::class_<ElementProperties>(m, "ElementProperties")
        .def(py::init<double, double, double, double>())
        .def_readwrite("V_23", &ElementProperties::V_23)
        .def_readwrite("phi", &ElementProperties::phi)
        .def_readwrite("n_WS_13", &ElementProperties::n_WS_13)
        .def_readwrite("mu", &ElementProperties::mu);
    py::class_<MiedemaConst>(m, "MiedemaConst")
        .def(py::init<double, double, double, double>())
        .def_readwrite("a", &MiedemaConst::a)
        .def_readwrite("p", &MiedemaConst::p)
        .def_readwrite("q", &MiedemaConst::q)
        .def_readwrite("r_over_p", &MiedemaConst::r_over_p);
    py::class_<MiedemaCore>(m, "MiedemaCore")
        .def(py::init<ElementProperties, ElementProperties, MiedemaConst>())
        .def("calculateSingle", &MiedemaCore::calculateSingle)
        .def("calculateRange", &MiedemaCore::calculateRange)
        .def("calculateSingleBatch", &MiedemaCore::calculateSingleBatch);
}