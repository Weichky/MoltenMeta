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
# The project name "MiedemaCore" is arbitrary - it doesn't affect the module name.
project(MiedemaCore LANGUAGES CXX)

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
# 5. AUTO-DETECT C++ SOURCE FILE
# -----------------------------------------------------------------------------
# This block automatically finds the .cpp file in this directory.
# The module name will be derived from the source file name.
# For example: miedema_core.cpp -> module name "miedema_core"
#
# file(GLOB ...): Searches for files matching a pattern.
# "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp" means "all .cpp files in this directory".
file(GLOB CPP_FILES "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

# list(LENGTH ...): Gets the number of items in a list.
list(LENGTH CPP_FILES _CPP_COUNT)

# Check that exactly one .cpp file was found.
# If zero or more than one .cpp file exists, abort with an error message.
# This prevents accidental build failures from having multiple source files.
if(NOT _CPP_COUNT EQUAL 1)
    message(FATAL_ERROR "Expected exactly one .cpp file in ${CMAKE_CURRENT_SOURCE_DIR}, found ${_CPP_COUNT}")
endif()

# list(GET ... 0 ...): Gets the first item (index 0) from the list.
list(GET CPP_FILES 0 _CPP_SOURCE)

# Extract the module name from the source file path:
#   1. Remove the ".cpp" extension
#   2. Remove directory path, keeping only the filename
# Example: "/path/to/miedema_core.cpp" -> "miedema_core"
string(REGEX REPLACE "\\.cpp$" "" _MODULE_NAME "${_CPP_SOURCE}")
string(REGEX REPLACE ".*/" "" _MODULE_NAME "${_MODULE_NAME}")

# Print the detected module name (shows up during cmake ..)
message(STATUS "Detected module: ${_MODULE_NAME}")

# -----------------------------------------------------------------------------
# 6. CONFIGURE OUTPUT DIRECTORY
# -----------------------------------------------------------------------------
# Tell CMake where to put the compiled library file (.so on Linux/macOS, .pyd on Windows).
# CMAKE_LIBRARY_OUTPUT_DIRECTORY is the default location.
# We also set the DEBUG and RELEASE variants to the same location.
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_CURRENT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_CURRENT_SOURCE_DIR}/lib)

# -----------------------------------------------------------------------------
# 7. BUILD THE PYTHON MODULE
# -----------------------------------------------------------------------------
# pybind11_add_module(): The pybind11 command to create a Python extension module.
# It takes two arguments:
#   1. Module name (how you'll import it in Python: import <name>)
#   2. Source file(s) to compile
# The module will be linked with Python and pybind11 automatically.
pybind11_add_module(${_MODULE_NAME} ${_CPP_SOURCE})

# -----------------------------------------------------------------------------
# 8. CONFIGURE LIBRARY PROPERTIES
# -----------------------------------------------------------------------------
# Fine-tune how the compiled library file is named and located.
set_target_properties(${_MODULE_NAME} PROPERTIES
    # Output directory (where to put the .so/.pyd file)
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib

    # Remove any prefix that might be added (e.g., "lib" on Linux).
    # On Linux, CMake would normally produce "libmiedema_core.so",
    # but we want just "miedema_core.so".
    PREFIX ""

    # Force the file extension to be ".so" on all platforms.
    # On macOS, CMake would normally produce ".dylib", but Python expects ".so".
    # On Windows, Python expects ".pyd", but we'll leave that for future handling.
    SUFFIX ".so"
)

# =============================================================================
# RESULT
# =============================================================================
# After running cmake .. && make, you should find:
#   lib/miedema_core.so   (Linux/macOS)
#   lib/miedema_core.pyd  (Windows)
#
# You can then import it in Python:
#   import miedema_core
#   core = miedema_core.MiedemaCore(...)
# =============================================================================
