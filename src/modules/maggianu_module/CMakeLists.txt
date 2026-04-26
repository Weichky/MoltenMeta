# =============================================================================
# CMakeLists.txt - Build Configuration for Pybind11 Modules
# =============================================================================
# This file tells CMake how to compile your C++ code into a Python module.
# CMake is a build system that generates platform-specific build files
# (Makefiles on Linux/macOS, Visual Studio projects on Windows).
#
# BASIC CONCEPTS:
#   - project(): Define the project name and languages used
#   - find_package(): Locate and load external dependencies (e.g., Python, pybind11)
#   - add_executable/add_library(): Tell CMake what to build
#   - target_*_properties: Configure how to build the target
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
cmake_minimum_required(VERSION 3.18)

project(MaggianuCore LANGUAGES CXX)

# -----------------------------------------------------------------------------
# 2. C++ STANDARD SETTINGS
# -----------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -----------------------------------------------------------------------------
# 3. FIND PYTHON
# -----------------------------------------------------------------------------
set(Python3_FIND_VIRTUALENV FIRST)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

message(STATUS "Using Python: ${Python3_EXECUTABLE}")

# -----------------------------------------------------------------------------
# 4. FIND PYBIND11
# -----------------------------------------------------------------------------
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

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
pybind11_add_module(maggianu_algorithm maggianu_algorithm.cpp)

# -----------------------------------------------------------------------------
# 7. CONFIGURE LIBRARY PROPERTIES
# -----------------------------------------------------------------------------
if(WIN32)
    set(PLATFORM_SUFFIX ".pyd")
else()
    set(PLATFORM_SUFFIX ".so")
endif()

foreach(_MODULE maggianu_algorithm)
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
#   lib/maggianu_algorithm.so
# Note: triangular_grid is shared in grid_module/
# =============================================================================