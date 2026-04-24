# =============================================================================
# CMakeLists.txt - Build Configuration for Pybind11 Modules
# =============================================================================
# This file tells CMake how to compile your C++ code into a Python module.
# CMake is a build system that generates platform-specific build files
# (Makefiles on Linux/macOS, Visual Studio projects on Windows).
#
# BASIC CONCEPTS:
# - project(): Define the project name and languages used
# - find_package(): Locate and load external dependencies (e.g., Python, pybind11)
# - add_executable/add_library(): Tell CMake what to build
# - target_*_properties: Configure how to build the target
#
# HOW TO USE:
#   1. Create a 'build' directory inside this module folder
#   2. Run: cmake ..   (from inside the build directory)
#   3. Run: make       (to compile)
#
#   Or simply use the provided build.sh script: ./build.sh
# =============================================================================

# -----------------------------------------------------------------------------
# 1. PROJECT SETUP
# -----------------------------------------------------------------------------
# Minimum CMake version required. 3.18 is needed for modern pybind11 features.
cmake_minimum_required(VERSION 3.18)

# Define the project name and the programming language(s) used.
# LANGUAGES CXX means we're using C++.
# The project name "KohlerCore" is arbitrary - it doesn't affect the module name.
project(KohlerCore LANGUAGES CXX)

# -----------------------------------------------------------------------------
# 2. C++ STANDARD SETTINGS
# -----------------------------------------------------------------------------
# Set the C++ standard to version 17 (modern C++ with many useful features).
set(CMAKE_CXX_STANDARD 17)

# Require that the C++ standard is strictly followed.
# If the compiler doesn't support C++17, CMake will abort.
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -----------------------------------------------------------------------------
# 3. FIND PYTHON
# -----------------------------------------------------------------------------
# Tell CMake to search for Python in virtual environments first.
# This ensures we use the Python interpreter from the project's venv,
# not the system Python (which might have different packages).
set(Python3_FIND_VIRTUALENV FIRST)

# Find Python interpreter and development headers.
# We need:
#   - Interpreter: To run Python scripts (e.g., for pybind11 detection)
#   - Development: Contains Python.h header files needed to compile C++ extensions
# COMPONENTS lists the specific parts we need.
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Print which Python executable was found (helpful for debugging).
message(STATUS "Using Python: ${Python3_EXECUTABLE}")

# -----------------------------------------------------------------------------
# 4. FIND PYBIND11
# -----------------------------------------------------------------------------
# pybind11 is a library that makes it easy to create Python bindings for C++ code.
# We need to find where pybind11 is installed so CMake can use its build rules.
#
# execute_process(): Runs a shell command and captures its output.
# Here we ask Python where pybind11's CMake files are located.
# The output is stored in the PYBIND11_CMAKE_DIR variable.
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE  # Remove trailing newline from output
)

# Tell CMake to search for pybind11 in the directory we just found.
set(pybind11_DIR "${PYBIND11_CMAKE_DIR}")
find_package(pybind11 CONFIG REQUIRED)

# -----------------------------------------------------------------------------
# 5. CONFIGURE OUTPUT DIRECTORY
# -----------------------------------------------------------------------------
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_CURRENT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_CURRENT_SOURCE_DIR}/lib)

# -----------------------------------------------------------------------------
# 6. BUILD MODULES
# -----------------------------------------------------------------------------
pybind11_add_module(kohler_algorithm kohler_algorithm.cpp)
pybind11_add_module(kohler_grid kohler_grid.cpp)

# -----------------------------------------------------------------------------
# 7. CONFIGURE LIBRARY PROPERTIES
# -----------------------------------------------------------------------------
if(WIN32)
    set(PLATFORM_SUFFIX ".pyd")
else()
    set(PLATFORM_SUFFIX ".so")
endif()

foreach(_MODULE kohler_algorithm kohler_grid)
    set_target_properties(${_MODULE} PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib
        PREFIX ""
        SUFFIX "${PLATFORM_SUFFIX}"
    )
endforeach()

# =============================================================================
# RESULT
# =============================================================================
# After running cmake .. && make, you should find:
#   lib/kohler_algorithm.so
#   lib/kohler_grid.so
# =============================================================================