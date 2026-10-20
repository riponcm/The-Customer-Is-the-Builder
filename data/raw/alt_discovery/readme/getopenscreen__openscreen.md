<p align="center">
  <img src="public/openscreen.png" alt="OpenScreen Logo" width="64" />
</p>

# <p align="center">OpenScreen</p>

<p align="center"><strong>A free, open-source desktop app for recording your screen and turning the result into polished product demos and walkthroughs.</strong></p>

<p align="center">
  <img src="docs/assets/demo.gif" alt="Editing a recording in OpenScreen: one click restyles the whole video, deleting a sentence in the transcript cuts it from the video, and the editor's agent adds a zoom on every click" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/getopenscreen/openscreen/blob/main/LICENSE"><img src="https://img.shields.io/github/license/getopenscreen/openscreen?style=for-the-badge&label=License" alt="License" /></a>
  <a href="https://github.com/getopenscreen/openscreen/releases/latest"><img src="https://img.shields.io/github/v/release/getopenscreen/openscreen?style=for-the-badge&label=Release" alt="Latest Release" /></a>
  <a href="https://github.com/getopenscreen/openscreen/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/getopenscreen/openscreen/ci.yml?style=for-the-badge&label=CI" alt="CI Status" /></a>
  <a href="https://getopenscreen.com/discord"><img src="https://img.shields.io/badge/Discord-Join%20us-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" /></a>
  <a href="https://github.com/sponsors/EtienneLescot"><img src="https://img.shields.io/badge/Sponsor-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Sponsor" /></a>
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Platform" />
</p>

<p align="center">
  <a href="https://trendshift.io/repositories/57147?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-57147" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/57147" alt="getopenscreen/openscreen | Trendshift" width="250" height="55" /></a>
  <a href="https://www.producthunt.com/posts/openscreen-2-3?embed=true&amp;utm_source=badge-featured&amp;utm_medium=badge&amp;utm_campaign=badge-openscreen-2-3" target="_blank" rel="noopener noreferrer"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1263181&amp;theme=light" alt="OpenScreen 2 on Product Hunt" width="250" height="54" /></a>
</p>

> [!NOTE]
> **This is OpenScreen, continued.** [Siddharth Vaddem](https://github.com/siddharthvaddem) created the project and [archived the original repository](https://github.com/siddharthvaddem/openscreen) after v1.5.0. Development moved here with his approval, under the same name and the same MIT license.

A raw capture goes in and comes out ready to post — on X, Reddit, YouTube, a docs page, or a landing page. That is the category Screen Studio defined; OpenScreen is the open-source entry in it, and not a clone.

**100% free** for personal and commercial use, with nothing held behind a paywall.

**Project status.** OpenScreen is under active development — expect rough edges and occasional breaking changes, including to the `.openscreen` project format and the CLI. Bug reports are welcome: [open an issue](https://github.com/getopenscreen/openscreen/issues).

## Core Features
- Record a specific window, or your whole screen.
- Record microphone and system audio.
- Webcam overlay with picture-in-picture, eight snap positions, adjustable roundness, mirroring, and shape options.
- Auto or manual zooms with adjustable depth, duration, easing, and pixel-precise position; auto-zoom follows your cursor as you work.
- Custom cursor size, smoothing, and click effects, with post-recording path smoothing.
- Automatic captions for voiceovers, transcribed on-device with no upload (works offline), with an editable transcript you can cut from and optional subtitle translation.
- AI editing assistant: describe the edit you want in chat and it applies to the timeline — cuts, zooms, speed ramps, annotations, camera framing. Bring your own key (Claude, OpenAI, Gemini, Mistral, OpenRouter, MiniMax, or any OpenAI-compatible endpoint); nothing is enabled by default.
- Wallpapers, solid colors, gradients, or your own background image.
- Motion blur.
- Crop, trim, and per-segment speed control on the timeline.
- Text, arrow, and image annotations, with text animation presets.
- Timeline snapping guides and an audio waveform to make trimming easier.
- Customizable keyboard shortcuts.
- Export to MP4 or GIF in multiple aspect ratios and resolutions, rendered and encoded on the GPU (Metal on macOS, D3D11 on Windows, Vulkan on Linux) with an automatic CPU fallback.
- Languages supported: Arabic, Czech, English, Spanish, French, German, Italian, Japanese, Korean, Portuguese (Brazil), Russian, Turkish, Vietnamese, Simplified Chinese, and Traditional Chinese.

## Command-line interface (headless)

OpenScreen ships a CLI for scripts, CI, and AI coding agents: record the screen
headlessly, edit the `.openscreen` project JSON programmatically (zooms,
annotations, trims), and render MP4/GIF with the full export pipeline — no
visible windows, NDJSON output with `--json`.

```bash
openscreen record --duration 20 --project demo.openscreen --json
openscreen export demo.openscreen -o demo.mp4 --json
```

See the [CLI reference](https://getopenscreen.com/docs/cli/).

### Let your coding agent ship the feature with its video

Give Claude Code, Codex or Cursor OpenScreen's MCP tools, and the skill that
teaches the whole job:

```bash
claude mcp add openscreen -- "/Applications/Openscreen.app/Contents/MacOS/Openscreen" mcp
npx skills add getopenscreen/openscreen --skill openscreen-demo
```

Then ask: *"Add a video of this change to the PR."* The agent plans the
storyboard, records the app, edits the take with OpenScreen's own editing tools,
exports the MP4, checks it frame by frame, and attaches it to the pull request,
wh