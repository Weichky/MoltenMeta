# =============================================================================
# CMakeLists.txt - Build Configuration for Pybind11 Modules
# =============================================================================
cmake_minimum_required(VERSION 3.18)
project(HillertToopCore LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(Python3_FIND_VIRTUALENV FIRST)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
message(STATUS "Using Python: ${Python3_EXECUTABLE}")
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
set(pybind11_DIR "${PYBIND11_CMAKE_DIR}")
find_package(pybind11 CONFIG REQUIRED)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_CURRENT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_CURRENT_SOURCE_DIR}/lib)
pybind11_add_module(hillert_toop_algorithm hillert_toop_algorithm.cpp)
pybind11_add_module(hillert_toop_grid hillert_toop_grid.cpp)
if(WIN32)
    set(PLATFORM_SUFFIX ".pyd")
else()
    set(PLATFORM_SUFFIX ".so")
endif()
foreach(_MODULE hillert_toop_algorithm hillert_toop_grid)
    set_target_properties(${_MODULE} PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib
        PREFIX ""
        SUFFIX "${PLATFORM_SUFFIX}"
    )
endforeach()