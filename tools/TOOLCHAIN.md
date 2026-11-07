# Linux 上构建蓝河手表表盘（工具链获取与复现步骤）
#
# BlueOS Studio 官方只有 macOS / Windows 版，但它内部是纯 Node 工具链，
# `blueos-pack` 里自带 Linux x86-64 原生二进制（vivo 自己的 CI 也是 Linux）。
# 把 macOS 版 dmg 掏出来，就能在 Linux 上完整出包。本文件记录实测可用的方法
# （2026-11-08 在 Ubuntu 容器 + GitHub Actions ubuntu-latest 上验证通过）。

## 1. 下载安装包

Windows 版（`.zip`/自解压壳）掏不出内层，用 macOS 版 dmg：

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
curl -L -A "$UA" -e "https://studio.blueos.com.cn/install" \
  -o blueos-m1.dmg \
  "https://ide-extensionstatic.vivo.com.cn/ide-extension/blue-os-studio-m1-2.2.1.dmg"
# 直链有防盗链，必须带 Referer + UA；约 876MB
```

## 2. 用 7z 精准抽取（dmg 对 7z 可直接读）

注意：通配符 `*/app/...` 在 7z 里跨不过 `/`，必须写完整路径前缀。

```bash
# 蓝河专用打包器 blueos-pack（v1.0.12-beta.13）+ 它的全部依赖：
# 只抽 blueos-pack 一个目录是不够的，它的 dist 运行时还要 require
# vite / lodash / css / parse5 等包，都在同级 node_modules 里。
7z x blueos-m1.dmg \
  "BlueOS Studio Installer/BlueOS Studio.app/Contents/Resources/app/extensions/blueos-debugger/node_modules/*" \
  -obpfull -y
```

## 3. 补 Linux 原生包（dmg 里只有 macOS 版）

dmg 自带的 `@rollup` / `@esbuild` 只有 `darwin-arm64` 变体，Linux 上构建会报
`Cannot find module @rollup/rollup-linux-x64-gnu`，随后 esbuild 服务起不来。
必须按 dmg 里 `esbuild` / `rollup` 自身的版本号装对应的 Linux 包
（版本必须精确一致，否则 esbuild 会拒绝启动）：

```bash
BP="bpfull/BlueOS Studio Installer/BlueOS Studio.app/Contents/Resources/app/extensions/blueos-debugger/node_modules"
ESBUILD_VER=$(BP="$BP" node -p "require(process.env.BP + '/esbuild/package.json').version")
ROLLUP_VER=$(BP="$BP" node -p "require(process.env.BP + '/rollup/package.json').version")
mkdir -p /tmp/native-pkgs && cd /tmp/native-pkgs && npm init -y >/dev/null 2>&1
npm i --ignore-scripts --no-audit --no-fund \
  "@esbuild/linux-x64@$ESBUILD_VER" "@rollup/rollup-linux-x64-gnu@$ROLLUP_VER"
cp -r node_modules/@esbuild/linux-x64 "$BP/@esbuild/"
cp -r node_modules/@rollup/rollup-linux-x64-gnu "$BP/@rollup/"
```

注：不要直接对 blueos-pack 跑 `npm i commander chalk` 之类——它会顺带装
整个依赖树，`@prisma/engines` 的 postinstall 要从外网下载二进制，常因
ECONNRESET 失败。blueos-pack 自身只缺上面两个 Linux 原生包。

## 4. 封装成 jax 命令

```bash
mkdir -p ~/blueos-toolchain/bin
cat > ~/blueos-toolchain/bin/jax <<'EOF'
#!/usr/bin/env bash
exec node "$HOME/blueos-toolchain/bpfull/BlueOS Studio Installer/BlueOS Studio.app/Contents/Resources/app/extensions/blueos-debugger/node_modules/blueos-pack/bin/index.js" "$@"
EOF
chmod +x ~/blueos-toolchain/bin/jax
jax --help   # 应列出 build / release / watch
```

## 5. 出包

```bash
bash tools/decode_assets.sh   # 还原图片（仓库里图片是 .b64 文本）
JAX=~/blueos-toolchain/bin/jax bash tools/build.sh
# → faces/*/dist/watch-square/debug/*.rpk（debug 包，内置签名，可直接侧载）
```

注意：`jax build` 编译报错也会照常产出 rpk，`tools/build.sh` 已内置
`[ERROR]` 日志检查，勿绕过。

## 6. 工程最小结构（表盘）

```
faces/<name>/
  package.json
  src/
    manifest.json        package / name / icon / versionCode / deviceTypeList /
                         config.designWidth / features / permissions / router.watchfaces
    app.ux               应用级入口（空实现）
    watchface/
      index.ux           表盘界面 <template> + <style> + <script>
      assets/images/     表盘内图片（dial.png / bg.png，构建时转 .vug）
    assets/images/
      preview.png        表盘图标/预览图（manifest icon 与 params.previewImage 都指它，
                         必须放 src/assets/images/，放 watchface/ 下构建会报 icon 找不到）
```
