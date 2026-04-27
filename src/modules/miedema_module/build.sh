#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_DIR="$SCRIPT_DIR"
BUILD_DIR="$SCRIPT_DIR/build"
LIB_DIR="$SCRIPT_DIR/lib"

mkdir -p "$BUILD_DIR"
mkdir -p "$LIB_DIR"

CACHE_FILE="$BUILD_DIR/CMakeCache.txt"
if [[ -f "$CACHE_FILE" ]]; then
    cached_source=$(grep "^CMAKE_HOME_DIRECTORY:" "$CACHE_FILE" | cut -d= -f2)
    if [[ "$cached_source" != "$MODULE_DIR" ]]; then
        echo "Stale CMake cache detected, cleaning build directory..."
        rm -rf "$BUILD_DIR"/*
    fi
fi

cd "$BUILD_DIR"

cmake "$MODULE_DIR"
make

echo "Build complete. Library located at: $LIB_DIR"
