#!/bin/bash

# 配置参数
A=' type="unfinished">'       # 要匹配的字符串A
B="<"       # A后面不能跟的字符串B
C=">"  # 替换为的字符串C
FILE="../i18n/zh_CN.ts"  # 操作的文件路径
BACKUP=true    # 是否备份原文件（true/false）
OUTPUT_NEW=false  # 是否输出到新文件（true时生成新文件，false时直接修改原文件）

# 检查文件是否存在
if [ ! -f "$FILE" ]; then
    echo "错误：文件 $FILE 不存在！"
    exit 1
fi

# 备份原文件（如果启用）
if [ "$BACKUP" = true ]; then
    cp "$FILE" "${FILE}.bak"
    echo "已备份原文件: ${FILE}.bak"
fi

# 替换逻辑（Perl正则兼容负向先行断言）
if [ "$OUTPUT_NEW" = true ]; then
    # 输出到新文件
    NEW_FILE="${FILE}.new"
    perl -pe "s/$A(?!$B)/$C/g" "$FILE" > "$NEW_FILE"
    echo "替换完成！结果已保存到: $NEW_FILE"
else
    # 直接修改原文件
    perl -pi -e "s/$A(?!$B)/$C/g" "$FILE"
    echo "替换完成！原文件已修改。"
fi

