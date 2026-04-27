#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="$SCRIPT_DIR"

echo "========================================"
echo "Building all modules in parallel..."
echo "========================================"

pids=()
names=()

for module_dir in "$MODULES_DIR"/*/; do
    module_name=$(basename "$module_dir")
    build_script="$module_dir/build.sh"

    if [[ -f "$build_script" ]]; then
        echo ">>> Building $module_name in background..."
        bash "$build_script" &
        pids+=($!)
        names+=("$module_name")
    fi
done

echo ""
echo ">>> Waiting for all builds to complete..."
echo ""

failed=0
for i in "${!pids[@]}"; do
    wait ${pids[$i]} || failed=1
    if [[ $failed -eq 1 ]]; then
        echo ">>> ${names[$i]} build FAILED"
    else
        echo ">>> ${names[$i]} build complete."
    fi
done

echo ""
echo "========================================"
if [[ $failed -eq 1 ]]; then
    echo "Some modules failed to build."
    exit 1
else
    echo "All modules built successfully."
fi
echo "========================================"
