# vivo WATCH GT 2 原创表盘（BlueOS / 快应用 .ux）

三个原创表盘，全部按 GT2 参数：方形屏 432×514、`designWidth` 432、
`deviceTypeList: ["watch-square"]`、`minPlatformVersion` 1070、debug 包。

| 表盘 | 包名 / id | 设计 |
|---|---|---|
| 简约指针 `faces/analog/` | `com.cewnhai.wf.analog` / 900000001 | 黑盘白刻度（12/3/6/9 数字+60 分钟刻度），时/分/秒针为旋转 div，顶部日期+星期，底部步数+电量；AOD 只留时分针+数字时间 |
| 大数字 `faces/digital/` | `com.cewnhai.wf.digital` / 900000002 | 中央巨大 HH:MM（右上角小秒），下方日期+星期，步数/心率/电量一行，步数目标 10000 的环形进度；AOD 只留时间 |
| 照片数字 `faces/photo/` | `com.cewnhai.wf.photo` / 900000003 | 全屏黄昏山景照片底图（`bg.png`，AI 生成、可替换），白色大数字时间带阴影，底部日期+步数+电量小胶囊；AOD 纯黑底+时间 |

每个表盘都是完整 BlueOS 工程：`package.json` + `src/manifest.json` +
`src/app.ux` + `src/watchface/index.ux` + `src/assets/images/preview.png`
（432×514 预览图，也是 manifest 的 icon）。analog 另有表盘底图
`src/watchface/assets/images/dial.png`，photo 另有
`src/watchface/assets/images/bg.png`。

图片说明：GitHub 的文件推送接口只接受 UTF-8 文本，png 二进制进不了仓库，
所以图片以 base64 文本（`*.b64`）形式入库；构建前先跑
`bash tools/decode_assets.sh` 还原成 png（本地已有 png 时跳过），
还原后删掉 .b64，不让它打进 .rpk。
改完图片后用 `bash tools/encode_assets.sh` 重新生成 .b64。

## 本地构建

前置：按 `tools/TOOLCHAIN.md` 从 BlueOS Studio
macOS dmg 掏出工具链（`jax` CLI，debug 包用内置签名、无需证书）。

```bash
bash tools/decode_assets.sh   # 先还原图片（仓库里图片是 .b64 文本）
bash tools/build.sh          # 批量构建三个表盘
JAX=/path/to/jax bash tools/build.sh   # 自定义 jax 位置
```

构建脚本对每个表盘：先抽 `<script>` 段做 `node --check` 预检（写成
`.mjs`，因为源码含 import/export），再跑 `$JAX build`；日志含
`[ERROR]` 即判失败（jax 报错也会照常出包）；最后列出 `dist` 下的 `.rpk`。

## CI（GitHub Actions）

`.github/workflows/build.yml`（须在 GitHub 网页上手动新建，API 写 workflow
会 403）：ubuntu runner 上复现本地步骤——下载 BlueOS Studio dmg → 7z 抽取
`blueos-pack` 全量依赖 → 按 dmg 内版本号补 Linux 原生包 → 还原图片 →
`bash tools/build.sh` → 上传 `faces/*/dist/**/*.rpk` 为 Artifacts。
push 到 main 或手动触发都跑。

## 安装到手表

把 `.rpk` 用第三方 App（用户自备，可直接给手表装表盘）经蓝牙传到
GT2 安装。debug 包用内置签名，无需自备证书。

## 写法来源

- manifest 结构、事件订阅（`usual.event.TIME_TICK / DATE_CHANGED /
  TIME_FORMAT / SCREEN_AOD / SCREEN_ON / SCREEN_OFF / BATTERY_CHANGED`）、
  秒级对齐定时器、指针 `rotate()` 字符串、AOD 按 `screenStatus`
  切换、电量 `battery.getStatusSync()`、24 小时制读取
  （`storage.getSync({key: 'settings.TIME_FORMAT'})`）：照搬已拆包的
  vivo 官方表盘「日晷」（从 .rpk 解出源码对照）。
- 工程最小结构与 `jax build` 用法：社区已验证的 Linux 打包方案
  （见 `tools/TOOLCHAIN.md`）。
- 字体（`vivo-Regular` / `vivoSansSC600` / `Fliptime-Linear-C-regular`）
  沿用已拆包表盘的做法（手表系统字体）。
- 预览图用 `tools/draw_previews.py`（PIL）画；photo 的 `bg.png` 由
  图片生成工具生成后裁成 432×514。

## 已知风险（编之前先看）

1. **`import health from '@service.health'` 未在已拆包表盘里出现过**——
   三个已拆包表盘都不读步数/心率，只用到 `system.event/screen/storage`
   （+日晷的 `system.battery`）。`service.health` 只是 manifest 的
   features 声明。按「feature 名 = 模块路径」的惯例（`system.battery` ↔
   `@system.battery`，参考 App 里 `blueos.health.healthManager` ↔
   `@blueos.health.healthManager`）推断应为 `@service.health`；官方文档
   另写 `@blueos.health.health`（getStepCount/getHeartRate）。若构建报
   找不到模块，改 import 为 `@blueos.health.health` 并在 features 里加
   `blueos.health.health`。健康接口全部包在 try/catch + promise catch
   里，取不到只显示 `--`，不会崩。
2. **digital 的 `<progress type="arc">`**：progress 是官方组件，arc
   类型与 `stroke-width / color / layer-color` 属性按快应用文档写法；
   若 BlueOS 手表端不支持，改走 canvas 画环或去掉。
3. **指针 `transform-origin`**：日晷编译产物证明工具链会输出
   `transformOrigin`，源码写 `transform-origin: 180px 180px;`；
   若手表上指针转心不对，先检查这一项。
4. **manifest `icon` / `previewImage` 的 `/assets/images/...` 路径**：
   照抄日晷（文件放在 `src/watchface/assets/images/`）；若打包后预览图
   找不到，把 `preview.png` 也放到包根目录再试。
5. **AOD 秒针**：AOD 下秒级定时器已停，秒针静止；AOD 界面已去掉秒针。
6. **`hpw: 0 / powerLevel: "1" / aodHz: 1`** 照抄日晷，未逐项验证含义。
