# FlyingMouse Format / 飞鼠格式

> **0.7.10 Windows 公开版 / Windows release**：修复大 TXT 转 EPUB 资源暴涨、混合 PDF 漏页和结果保存问题，增加真实耗时与阶段进度。此次提供 Windows 10/11 x64 完整版；Microsoft Store 状态独立核对。见 [版本说明 / Release notes](docs/release-notes-0710.md)。

> A mouse-themed, offline Windows file converter. / 一款鼠鼠主题、可离线使用的 Windows 文件格式转换工具。

> **作者 Author：牢蜂（LaoFeng）**
>
> **⚠️ 非商用声明 Non-Commercial Notice：本软件仅供个人免费使用，禁止任何形式的商业售卖、转卖、套壳换皮重新发布（详见 [LICENSE](LICENSE)）。发现闲鱼/淘宝等渠道倒卖请告知作者，感谢！**

[![Release](https://img.shields.io/github/v/release/LaoFeng-mouse/flyingmouse-format?color=e95f6d)](https://github.com/LaoFeng-mouse/flyingmouse-format/releases/latest)
![CI](https://github.com/LaoFeng-mouse/flyingmouse-format/actions/workflows/ci.yml/badge.svg)
![Platform](https://img.shields.io/badge/0.7.10-Windows%2010%2F11%20x64-0078D6)
![License](https://img.shields.io/badge/License-Non--Commercial-e95f6d)

[下载 Windows 0.7.10 / Download](https://github.com/LaoFeng-mouse/flyingmouse-format/releases/download/v0.7.10/FlyingMouse-Format-Setup-0.7.10-x64.exe) · [版本详情 / Release](https://github.com/LaoFeng-mouse/flyingmouse-format/releases/tag/v0.7.10) · [问题反馈 / Issues](https://github.com/LaoFeng-mouse/flyingmouse-format/issues)

![FlyingMouse Format mouse UI](public/assets/screenshots/home.png)

## 中文

### 主要功能

- 鼠鼠原版界面：鼠鼠会跟随上传、识别、批量、OCR、转换成功或失败切换状态。
- 本地离线转换：Windows 完整版内置 FFmpeg、LibreOffice、Poppler、Tesseract 和 Pandoc。AV3A 和平台加密音频不在当前支持范围内。
- 支持图片、文本、Word/WPS、Excel/WPS、PPT/WPS、PDF、音频、视频和 ZIP。
- 音频转换：支持 MP3 / WAV / FLAC / M4A / AAC / OGG / OPUS / WMA 等普通格式互转；**不支持其他音乐平台的加密特殊格式**（如 NCM / KGG / mflac / kgma / kwm 等）。
- 视频编码选择：转视频时可选 H.264 / H.265 / AV1 编码（目标 mp4/mov/mkv 时显示）。
- 操作记忆：按“源文件格式”分别记住上次选择的目标格式；重新修改后，新选择会成为该源格式的默认值。
- 路径记忆：记住上次保存目录，下次保存时自动从该目录开始。
- 中文/English 界面：首次启动跟随系统语言，手动选择后会记住设置。
- 外观：可选择浅色、深色或跟随系统；切换系统外观时自动更新，选择会保存。
- Markdown → Word/PDF：保留标题、表格、嵌套列表、代码原文及可编辑 Word 公式；缺失图片或不支持的原始内容会提示。Win7 Legacy 未捆绑新版 Pandoc，因此不提供这两个目标。
- 批量转换：显示逐文件进度、结果和失败原因，并可单独保存或保存全部。
- 真实进度与耗时：显示本次已耗时；有实际总量时显示当前阶段比例，否则明确提示无法估算。完成或失败后冻结耗时，不把保存时间计入转换。
- 结果预览：转换完成后可在侧边抽屉预览图片、PDF、文本、音频和视频；窄窗口自动切换为底部面板。
- CLI 与 Agent 接入：命令行覆盖能力查询、目标查询、单个/批量转换、图片合并 PDF 和 PDF 合并；应用内可把配套 skill 一键接入现有 Codex、Claude 或通用 Agent 目录。
- 转换质量：HTML / Office 转 Markdown 保留标题、列表和代码块；CSV 支持 BOM、转义引号和字段内换行。
- PDF → Excel（智能表格提取）：支持电子文字坐标、扫描页 OCR、有框/无框表格、多表、跨页续接、合并单元格和低置信度批注。Raw 工作表仅保留原生非表格文字；扫描页无法恢复时明确失败。
- PDF → Word：Windows 10/11 优先使用版式引擎，检查文字覆盖后再接受结果；旋转文字和碎片正文可重建为可编辑段落，混合扫描页逐页处理。降级重建和 OCR 会显示说明；复杂多栏、图片定位和扫描标点不能保证与原 PDF 完全一致。
- PDF 拆分 / 加密 / 解密：PDF 可逐页拆分或每 N 页一组（打包 ZIP），也可用密码加密（AES-256）或解密（需原密码）。
- 电子书：txt/md/html → EPUB；EPUB → TXT/Markdown/HTML，以及有 LibreOffice 时转 PDF/DOCX。读取按章节目录排序，缺章、缺图、加密及不支持的 MOBI 压缩会明确失败；复杂 CSS 版式会简化。
- 文本转 EPUB 可选择源编码：UTF-8、GBK/GB18030、UTF-16LE/BE；自动模式支持 UTF-8 和带 BOM 的 UTF-16，不能严格解码时提示选择编码重试。
- 图片合并 PDF 支持调整顺序：多张图片转 PDF 前可在队列中上移/下移，PDF 页序跟随队列顺序。
- HEIC/HEIF 图片可转换为 JPG/PNG/WebP 等（内置 ffmpeg 解码）。
- ICO 图标可转换为 PNG/JPG 等，PNG/JPG 也可生成多尺寸 ICO 图标（实验性）。
- TGA 图片可转换为 PNG/JPG/WebP 等（内置 ffmpeg 解码，实验性）。
- 相机 RAW 原片（CR2/CR3/NEF/ARW/DNG 等）可转换为 JPG/PNG/WebP/TIFF 等（内置 dcraw 解码，Windows 版，实验性）。
- 资源保护：普通转换受引擎能力和机器内存约束；高级 PDF 结构识别限制为 500 页、单页 5000 万像素、每批最多 8 页且累计 1 亿像素（144 DPI）；整份超过单批预算时自动串行分批，仍保留总页数和全局输出预算，超限会明确提示。解码合法性与产物完整性校验保留。

> **合规声明 Compliance Notice：本软件仅支持普通音频格式转换（MP3 / WAV / FLAC / AAC / OGG 等），不支持任何音乐平台的加密特殊格式。请支持正版音乐，尊重创作者。音频文件版权归原作者/唱片公司所有，本工具与各音乐平台无任何关联。本软件仅供个人免费使用，禁止商业售卖/转卖/套壳换皮重新发布。**

### 快速开始

0.7.10 提供 Windows 10/11 x64 完整版，已在 Windows 11 完成原生成品转换、启动和交互验证。Lite、macOS 和 Windows 7 的 0.7.10 安装包此次未发布；商店状态见[分渠道记录](docs/REPAIR-0.7.10.md)。其他系统与硬件的验证边界见[版本说明](docs/release-notes-0710.md)。

1. 下载 v0.7.10 对应系统的安装包：本次仅提供 [Windows 10/11 x64 完整版（FlyingMouse-Format-Setup-0.7.10-x64.exe）](https://github.com/LaoFeng-mouse/flyingmouse-format/releases/download/v0.7.10/FlyingMouse-Format-Setup-0.7.10-x64.exe)。
2. 安装并启动 FlyingMouse Format。
3. 拖入文件，选择目标格式并开始转换。
4. 选择保存位置；软件会记住目标格式与保存目录。

安装包为 1,515,803,399 字节（约 1.41 GiB）；完整展开文件约 3.76 GiB，较本次 0.7.9 对照布局减少约 6.2%，仍包含完整离线引擎和识别模型。此口径不含运行缓存、临时产物或文件系统分配差异。高级 PDF 结构识别启动前要求至少 5 GiB 当前可用物理内存；普通文字提取及 TXT 转 EPUB 不受这个独立门槛影响。

从源码运行：

> 源码仓库不包含体积较大的 FFmpeg、LibreOffice、Poppler 和 Tesseract 资源；普通用户请直接下载 Release 安装包。开发者从源码运行完整转换功能前，需要自行准备 `bin/` 下的引擎资源。

```powershell
npm install
npm run desktop
```

命令行示例：

```powershell
node cli.js capabilities --json
node cli.js targets example.pdf --json
node cli.js convert input.docx --to pdf --output output.pdf --json
node cli.js convert a.png b.png --to webp --output-dir converted --json
node cli.js images-to-pdf 1.jpg 2.jpg --output album.pdf --json
node cli.js merge-pdfs a.pdf b.pdf --output merged.pdf --json
```

安装版也可直接调用应用入口：macOS 使用 `FlyingMouse Format.app/Contents/MacOS/FlyingMouse Format --cli ...`，Windows 使用 `FlyingMouse Format.exe --cli ...`。在软件顶部点击“接入 Agent”，会检索已存在的 `~/.codex/skills`、`~/.claude/skills`、`~/.agents/skills`（Windows 对应用户目录）并在确认后安装或更新 skill；不会自动创建未安装产品的目录。

运行测试与打包：

```powershell
npm test
npm run dist
```

### 版本与平台

| 0.7.10 渠道 | 本次状态 |
|---|---|
| Windows 10/11 x64 完整版 | GitHub 公开安装包，包含高级扫描表格引擎；实际设备验收为 Windows 11。 |
| Windows Lite、macOS | 本次未发布对应安装包。源码/CI 支持不等于成品已交付。 |
| Windows 7 | 本次未发布；仅保留源码构建目标 `FlyingMouse Format-Setup-0.7.10-win7-x64.exe`，不是可下载资产。 |
| Microsoft Store | 独立提交与认证渠道；本轮没有 0.7.10 商店发布凭证，现场状态见分渠道记录。 |

公开 Windows 安装包未签名，SmartScreen 可能提示。Windows 10、旧系统、其他显卡和商店签名版升级仍需对应环境验证，不能以本机通过保证所有电脑兼容。开发构建与 Legacy 依赖边界见[发布流程](docs/RELEASE.md)。

## English

### Highlights

- Original mouse UI with animated state changes for upload, detection, batch work, OCR, success, and errors.
- Fully local conversion with bundled FFmpeg, LibreOffice, Poppler, and Tesseract. AV3A and platform-encrypted audio are not supported inputs.
- Converts images, text, Word/WPS, Excel/WPS, PPT/WPS, PDF, audio, video, and ZIP files.
- Audio conversion between ordinary formats: MP3 / WAV / FLAC / M4A / AAC / OGG / OPUS / WMA. **Encrypted special formats from music platforms (NCM / KGG / mflac / kgma / kwm etc.) are NOT supported.**
- Video codec selection: H.264 / H.265 / AV1 for video conversion (shown when targeting