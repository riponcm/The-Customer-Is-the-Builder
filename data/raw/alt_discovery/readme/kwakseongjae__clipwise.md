[English](./README.md) | [한국어](./README.ko.md)

# Clipwise

Scriptable cinematic screen recorder for product demos — YAML in, polished MP4 out. Powered by Playwright CDP.

<p align="center">
  <video src="https://github.com/user-attachments/assets/800d956f-ecf3-40c4-8750-c93b34285f11" autoplay loop muted playsinline width="100%"></video>
</p>

> *Generated with `npx clipwise demo` — 1 YAML file, 248 lines, one command.*

## Quick Start

```bash
# No install needed — run straight from npx (your package.json stays untouched)
npx clipwise@latest demo                       # Try the built-in demo instantly

# Or create your own scenario
npx clipwise@latest init                       # Scaffolds .clipwise/ (single footprint dir)
# Edit .clipwise/scenarios/demo.yaml — change the URL to your site
npx clipwise@latest record .clipwise/scenarios/demo.yaml
```

**Zero footprint**: everything Clipwise touches lives in one `.clipwise/` directory —
scenarios, fixtures, auth state, output. Remove every trace with `rm -rf .clipwise`.

### Your first 5 minutes

1. `npx clipwise@latest init` — scaffolds `.clipwise/` with two ready scenarios
2. `npx clipwise@latest record .clipwise/scenarios/keynote.yaml` — renders a full
   keynote-style launch video **with zero edits** (it records the hosted demo dashboard)
3. Open `.clipwise/output/keynote.mp4` — this is the quality bar you get out of the box
4. Edit `keynote.yaml`: swap the `url:` and selectors for **your** app, tweak the captions
5. Edit `brand.yaml`: your accent color, font preset, catchphrases — the whole video follows

Prefer natural language? `npx clipwise install-skill`, then ask `/clipwise` in
Claude Code — it writes these YAMLs for you (the skill ships with the full
keynote recipe). For a plain screen recording instead of a launch video, start
from `scenarios/demo.yaml` and the [YAML Scenario Format](#yaml-scenario-format) below.

## Requirements

- **Node.js** >= 18
- **ffmpeg** (for MP4 output)
- **Chromium** (auto-installed on first run via Playwright)

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

## Usage

### CLI Commands

```bash
# Instant demo — records the built-in dashboard showcase
npx clipwise demo                          # Browser frame, MP4
npx clipwise demo --device iphone          # iPhone mockup
npx clipwise demo --device android         # Android mockup
npx clipwise demo --device ipad            # iPad mockup
npx clipwise demo --url https://my-app.com # Your deployed site

# Record from YAML scenario (output defaults to .clipwise/output)
npx clipwise record <scenario.yaml> -f mp4
npx clipwise record <scenario.yaml> -f gif -o ./custom-dir

# Scaffold .clipwise/ (scenarios, fixtures, prepare assets, auth — one dir, zero footprint)
npx clipwise init

# Validate without recording
npx clipwise validate <scenario.yaml>
```

### Programmatic API

```typescript
import { ClipwiseRecorder, CanvasRenderer, encodeMp4, loadScenario } from "clipwise";

const scenario = await loadScenario("my-scenario.yaml");
const recorder = new ClipwiseRecorder();
const session = await recorder.record(scenario);

const renderer = new CanvasRenderer(scenario.effects, scenario.output, scenario.steps);
const frames = await renderer.composeAll(session.frames);

const mp4 = await encodeMp4(frames, scenario.output);
```

## Claude Code Skill

Clipwise ships a built-in [Claude Code](https://claude.com/claude-code) skill. Once installed, type `/clipwise` in Claude Code to generate YAML scenarios, validate, and record — all through natural language.

### Install the skill

```bash
npx clipwise install-skill
```

This copies the skill file to `.claude/skills/clipwise.md` (project-level if `.claude/` exists, otherwise `~/.claude/skills/`).

### Usage

In any Claude Code session:

```
/clipwise
> Record a demo of my dashboard at http://localhost:3000
  — click the login button, type credentials, navigate to analytics
```

Claude will:
1. Generate a complete `clipwise.yaml` scenario
2. Run `npx clipwise validate` to check for errors
3. Run `npx clipwise record` to produce the MP4

### Update / Remove

Re-run `npx clipwise install-skill` after upgrading clipwise to get the latest skill.
Remove it anytime with `npx clipwise install-skill --remove` — the skill file is the
only thing Clipwise leaves outside `.clipwise/`.

## YAML Scenario Format

A scenario has 4 sections: metadata, effects, output, and steps.

```yaml
name: "My Demo"
description: "Optional description"

viewport:
  width: 1280    # Browser width (default: 1280)
  height: 800    # Browser height (default: 800)

effects:
  # See "Effects" section below

output:
  format: mp4              # gif | mp4 | png-sequence
  width: 1280
  height: 800
  fps: 30                  # 1-60
  preset: social           # social | balanced | archive

steps:
  - name: "Step name"
    actions:
      - action: navigate
        url: "https://example.com"
    captureDelay: 200       # ms to wait after actions
    holdDuration: 800       # ms to hold on result
    transition: none        # none | fade | slide-left | slide-up | blur
    effects:                # Per-step effects override (optional)
      zoom:
        enabled: false      # Disable zoom for this step only
```

### Actions

#### Basic Actions

| Action | Parameters | Default | Description |
|--------|-----------|---------|-------------|
| `navigate` | `url`, `waitUntil?` | `waitUntil: "networkidle"` | Navigate to URL |
| `click` | `selector`, `delay?`, `timeout?` | | Click an element |
| `type` | `selector`, `text`, `delay?`, `timeout?` | `delay: 50` | Type text (char-by-char, React/Vue compatible) |
| `hover` | `selector`, `timeout?` | | Hover over element |
| `scroll` | `y?`, `x?`, `selector?`, `smooth?`, `timeout?` | `y: 0`, `x: 0`, `smooth: true` | Scroll by offset |
| `wait` | `duration` | | Wait (ms) |
| `screenshot` | `name?`, `fullPage?` | `fullPage: false` | Capture marker |

#### Async Wait Action