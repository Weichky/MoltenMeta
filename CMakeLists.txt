cmake_minimum_required(VERSION 3.18)
project(MoltenMeta LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import pybind11, sys; sys.stdout.write(pybind11.get_cmake_dir())"
    RESULT_VARIABLE _pybind11_status
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
)

if(NOT _pybind11_status EQUAL 0)
    message(FATAL_ERROR "pybind11 not found. Please uv pip install pybind11")
endif()

set(pybind11_DIR "${PYBIND11_CMAKE_DIR}")
find_package(pybind11 CONFIG REQUIRED)

add_subdirectory(src)