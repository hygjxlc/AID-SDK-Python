# -*- coding: utf-8 -*-
"""
把 --files a b c 形式的空格分隔参数合并为 --files a,b,c 供 Click 使用。
用法: python _merge_files_args.py -- [原始参数...]
输出: 处理后的参数字符串（单行）
"""
import sys

args = sys.argv[1:]
# 跳过开头的 -- 分隔符
if args and args[0] == '--':
    args = args[1:]

out = []
i = 0
while i < len(args):
    if args[i] == '--files':
        i += 1
        vals = []
        while i < len(args) and not args[i].startswith('--'):
            vals.append(args[i])
            i += 1
        out.extend(['--files', ','.join(vals)])
    else:
        out.append(args[i])
        i += 1

print(' '.join(out))
