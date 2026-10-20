<div align="center">

English | [Español](README.es.md)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/media/klipe-logo-dark.svg">
  <img src="docs/media/klipe-logo-light.svg" width="260" alt="Klipe Studio">
</picture>

<br/><br/>

[![Windows 10 | 11](https://img.shields.io/badge/Windows%2010%20%7C%2011-7C62FF?style=for-the-badge&logo=windows&logoColor=white)](#installation)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-7C62FF?style=for-the-badge)](LICENSE)

### Record. Zoom. Polish. Ship — fully open source, 100% local.

A Windows **screen recorder and cinematic editor** with automatic zoom-on-click,
smooth cursor, beautiful backgrounds, a webcam bubble and Android phone mirroring —
in the spirit of Screen Studio, but for Windows.

[![Download for Windows](https://img.shields.io/badge/⬇%20%20Download%20for%20Windows-7C62FF?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/jcurotto-c/Klipe-Studio/releases/latest/download/Klipe-Studio-Setup.exe)

<video src="https://github.com/user-attachments/assets/aac24b6c-8c93-4e42-8f38-680ed02964e0" width="820" controls></video>

</div>

---

## What is Klipe Studio?

Klipe Studio records your screen (or an Android phone) and turns raw captures into
polished, motion-driven product videos — automatic zoom on clicks, a buttery-smooth
rendered cursor, cinematic camera moves, styled backgrounds, a webcam bubble, title
cards and on-device captions. Think **Screen Studio**, but for Windows and fully
open source.

Everything runs **locally**: no backend, no telemetry, no uploads. Export uses your
GPU's hardware encoder via WebCodecs — not FFmpeg.wasm.

> **Platform:** Windows 10 (build 19041+) or Windows 11, x64. Screen capture uses
> native **Windows.Graphics.Capture**; system audio uses **WASAPI** loopback.

> **Stack:** Electron · React · Vite · TypeScript · PixiJS · WebCodecs + [mediabunny](https://www.npmjs.com/package/mediabunny) · scrcpy (phone capture) · transformers.js (on-device Whisper)

---

## Core features

### 🎯 Automatic zoom & cinematic camera-follow
Klipe watches your clicks, typing bursts and cursor-type changes and **zooms in
automatically** at the right moments — no manual keyframing. Add or tweak **manual
zoom segments** with per-segment scale, easing and focus point, then let the
**camera follow** the cursor with `static`, `follow` (safe-zone) or `cinematic`
(floaty springs + look-ahead) behaviour.

<!-- Add demo: docs/media/feature-zoom.gif — auto-zoom + camera follow -->

### 🖱️ Cursor polish
The recorded cursor is **re-rendered**, not captured — so it can be smoothed, resized
and restyled after the fact: multiple cursor styles, motion blur, click bounce and
velocity-based sway. The live preview cursor sits on a **content-protected overlay**,
so the real OS cursor never bleeds into the capture.

<!-- Add demo: docs/media/feature-cursor.gif — cursor polish -->

### 🎨 Beautiful backgrounds, framing & webcam bubble
Drop your recording onto **wallpapers, gradients, solid colors, custom images or a
looping video background**, with adjustable blur, corner radius, padding and frame
shadow. Add a **webcam bubble** anywhere on a 9-position grid (circle, card or pill),
mirrored and resizable, that can even shrink while zoomed.

<!-- Add demo: docs/media/feature-background.gif — backgrounds / framing / webcam -->

### 📱 Android phone mirroring
Record an Android device — over USB — straight into Klipe via bundled **scrcpy + adb**
(downloaded and integrity-checked automatically), composited inside an on-screen
**phone frame** (iPhone, Dynamic Island or Galaxy).

<!-- Add demo: docs/media/feature-phone.gif — phone mirroring -->

---

## All features

### Recording
- Record an entire display or a single window (Electron `desktopCapturer` / `getDisplayMedia`).
- Microphone **and** system/desktop audio (WASAPI loopback) as independent tracks.
- **Global input tracking** — mouse moves, clicks and keystrokes captured at the OS
  level by a Win32-backed PowerShell helper (`GetCursorPos` / `GetAsyncKeyState` /
  `GetCursorInfo`). No native modules to compile.
- Webcam capture as a separate track.
- Android phone mirroring via bundled scrcpy + adb.
- Every recording **auto-saves** to your library ("My videos" gallery).

### Editing & timeline
- Multi-fragment timeline: trim, cut/split, reorder, click markers, scrubbable playhead.
- Real-time PixiJS + WebCodecs preview.
- Reopen any past project from the library; undo/redo.

### Zoom & camera
- Automatic zoom from clicks, typing bursts and UI-focus cursor types.
- Manual zoom segments — center point, scale, duration, ease-in/ease-out, zoom blur.
- Camera-follow modes: `static`, `follow` (safe-zone), `cinematic`.

### Cursor
- Show/hide, loop, size (0.5×–5×), multiple styles.
- Smoothing, motion blur, click bounce and sway, plus one-click movement presets.

### Backgrounds & framing
- Wallpaper presets + custom uploads, gradients, solid colors, **video backgrounds**.
- Background blur, frame shadow, corner radius, padding.
- Source crop with optional aspect lock; `fit` vs `fill` modes.

### Webcam bubble
- 9-position grid · circle / card / pill shapes · size, roundness, mirror.
- Optional different size while zoomed.

### Overlays, title cards & captions
- Text & image **overlays** with PixiJS animations (fade, rise, zoom, blur, typewriter)
  and per-overlay keyframes.
- **Intro / outro / mid-roll title cards**, including a parametric **Reveal** template
  (cascading images + title + callout labels), with fade transitions.
- **Captions** generated **on-device** by Whisper (transformers.js, runs in a Web
  Worker — no API key, no cloud), auto-detect or pick a language, fully styleable.

### Audio
- Independent mic + system-audio volumes.
- Generated **click / keystroke sound effects** (auto / on / off).
- Looping **background music** with fade-in / fade-out.

### Blur / redaction
- Rectangle or ellipse regions, gaussian blur or pixelate, with 