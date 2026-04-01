#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
LIB_DIR="$SCRIPT_DIR/lib"

mkdir -p "$BUILD_DIR"
mkdir -p "$LIB_DIR"

cd "$BUILD_DIR"

cmake ..
make

echo "Build complete. Library located at: $LIB_DIR"
