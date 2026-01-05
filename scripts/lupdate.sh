#!/usr/bin/env bash
set -e

# =========================
# 1. 路径锚定
# =========================

script_dir="$(cd "$(dirname "$0")" && pwd)"
project_root="$(dirname "$script_dir")"

i18n_dir="$project_root/i18n"
ts_file="$i18n_dir/zh_CN.ts"

tmp_list="$script_dir/.lupdate_files.txt"

# =========================
# 2. 准备
# =========================

mkdir -p "$i18n_dir"
: > "$tmp_list"

# =========================
# 3. 扫描可翻译 Python 文件
# =========================

find "$project_root" \
  -path "$script_dir" -prune -o \
  -path "*/__pycache__" -prune -o \
  -type f -name "*.py" -print |
while read -r file; do
  if grep -q "self\.tr(" "$file"; then
    echo "$file" >> "$tmp_list"
  fi
done

count=$(wc -l < "$tmp_list")

if [ "$count" -eq 0 ]; then
  echo "No translatable Python files found."
  exit 0
fi

echo "Found $count translatable files."

# =========================
# 4. 调用 lupdate
# =========================

echo "Running lupdate..."

lupdate $(<"$tmp_list") -ts "$ts_file"

echo "Updated: $ts_file"

# =========================
# 5. 清理
# =========================

rm "$tmp_list"

