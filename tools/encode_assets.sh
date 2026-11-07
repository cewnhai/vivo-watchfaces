#!/usr/bin/env bash
# 本地改完图片后，把 *.png 重新编码成 *.b64（仓库里只存 .b64，见 decode_assets.sh）。
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
find "$ROOT/faces" -name "*.png" -not -path "*/build/*" -not -path "*/dist/*" | while read -r png; do
  base64 -w0 "$png" > "$png.b64"
  echo "encoded: $png.b64"
done
