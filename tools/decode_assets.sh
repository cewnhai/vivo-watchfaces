#!/usr/bin/env bash
# 把仓库里的 *.b64 图片资源还原成 *.png（CI 用；本地已有 png 时跳过）。
# 背景：GitHub 的文件推送接口只接受 UTF-8 文本，png 二进制放不进仓库，
# 所以图片以 base64 文本（*.b64）形式入库，构建前用本脚本还原。
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
find "$ROOT/faces" -name "*.b64" | while read -r b64; do
  png="${b64%.b64}"
  if [ -f "$png" ]; then
    echo "skip (exists): $png"
  else
    base64 -d "$b64" > "$png"
    echo "decoded: $png"
  fi
done
