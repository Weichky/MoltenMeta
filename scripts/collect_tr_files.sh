#!/usr/bin/env bash
set -e

# 1. 路径锚定
script_dir="$(cd "$(dirname "$0")" && pwd)"
project_root="$(dirname "$script_dir")"

# 2. 输出文件
out_file="$script_dir/translate_files.txt"
: > "$out_file"

# 3. 扫描
find "$project_root" \
  -path "$script_dir" -prune -o \
  -path "*/__pycache__" -prune -o \
  -type f -name "*.py" -print |
while read -r file; do
  if grep -q "self\.tr(" "$file"; then
    echo "$file" >> "$out_file"
  fi
done

echo "Found $(wc -l < "$out_file") translatable files."
echo "List saved to: $out_file"

