# include <pybind11/pybind11.h>

int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(example_add, m) {
    m.doc() = "pybind11 example plugin";

    m.def("add",
        &add,
        "A function which adds two numbers",
        py::arg("i") = 1,
        py::arg("j") = 2);
}