#!/usr/bin/env bash
# 批量构建 faces/ 下的三个表盘（analog / digital / photo）
# 前置：按 tools/TOOLCHAIN.md 从 BlueOS Studio (macOS dmg) 掏出工具链
#   JAX 环境变量指向 blueos-pack CLI（默认 /root/blueos/bin/jax）
set -u
JAX="${JAX:-/root/blueos/bin/jax}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FACES="analog digital photo"
FAIL=0

for face in $FACES; do
  PROJ="$ROOT/faces/$face"
  echo "== [$face] 语法预检（<script> 段） =="
  if ! (cd "$PROJ" && python3 - <<'PY'
import os, re, subprocess, sys, tempfile
ux = open("src/watchface/index.ux", encoding="utf-8").read()
m = re.search(r"<script>(.*)</script>", ux, re.S)
if not m:
    print("no <script> found")
    sys.exit(1)
# 写成 .mjs 再 --check：源码含 import/export，.js 会按 CommonJS 判错
with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
    f.write(m.group(1))
    tmp = f.name
r = subprocess.run(["node", "--check", tmp])
os.unlink(tmp)
sys.exit(r.returncode)
PY
); then
    echo "!! [$face] 脚本预检失败"
    FAIL=1
    continue
  fi

  echo "== [$face] 打包 =="
  LOG="$(mktemp)"
  if ! (cd "$PROJ" && rm -rf dist && "$JAX" build 2>&1 | tee "$LOG"); then
    echo "!! [$face] jax build 退出码非 0"
    FAIL=1
    continue
  fi
  # 关键：jax 编译报错也会照常产出 rpk，必须显式检查日志
  if grep -qE "\[ERROR\]" "$LOG"; then
    echo "!! [$face] 编译日志含 [ERROR]，产物不可信"
    FAIL=1
    continue
  fi
  echo "-- [$face] 产物："
  find "$PROJ/dist" -name "*.rpk" 2>/dev/null
done

echo "== 全部产物 =="
find "$ROOT/faces" -path "*/dist/*" -name "*.rpk" 2>/dev/null
if [ "$FAIL" -ne 0 ]; then
  echo "!! 批量构建有失败项"
  exit 1
fi
echo "批量构建全部成功"
