#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="$SCRIPT_DIR"

echo "========================================"
echo "Building all modules..."
echo "========================================"

for module_dir in "$MODULES_DIR"/*/; do
    module_name=$(basename "$module_dir")
    build_script="$module_dir/build.sh"

    if [[ -f "$build_script" ]]; then
        echo ""
        echo ">>> Building $module_name..."
        bash "$build_script"
        echo ">>> $module_name build complete."
    fi
done

echo ""
echo "========================================"
echo "All modules built successfully."
echo "========================================"
