<!-- Generated from docs/RELEASES-README.md in Lumae's source repository and mirrored here
     by scripts/publish-docs.sh on every release. Edit it there; changes made here are
     overwritten by the next release. -->

<p align="center">
  <a href="https://lumae.app"><img src="https://raw.githubusercontent.com/matlegault/lumae-releases/main/docs/images/lumae-icon.png" width="128" height="128" alt="Lumae app icon"></a>
</p>

<h1 align="center">Lumae</h1>

<p align="center">
  <strong>A free Mac screen recorder and screenshot tool for polished software demos,<br>
  with an MCP server built in so AI agents can record, edit and export them too.</strong>
</p>

<p align="center">
  <a href="https://github.com/matlegault/lumae-releases/releases/latest"><img src="https://img.shields.io/github/v/release/matlegault/lumae-releases?label=release&color=7cc243" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/macOS-26%2B-111111?logo=apple&logoColor=white" alt="macOS 26 or later">
  <img src="https://img.shields.io/badge/Apple%20silicon%20%2B%20Intel-universal-111111" alt="Universal: Apple silicon and Intel">
  <img src="https://img.shields.io/badge/price-free-7cc243" alt="Free">
  <a href="https://github.com/matlegault/lumae-releases/blob/main/docs/MCP.md"><img src="https://img.shields.io/badge/MCP-server-5a67d8" alt="MCP server"></a>
  <a href="https://github.com/matlegault/homebrew-lumae"><img src="https://img.shields.io/badge/brew-matlegault%2Flumae%2Flumae-fbb040?logo=homebrew&logoColor=white" alt="Homebrew cask"></a>
</p>

<p align="center">
  <a href="https://github.com/matlegault/lumae-releases/releases/latest"><b>Download for macOS</b></a> ·
  <a href="https://lumae.app">Website</a> ·
  <a href="https://github.com/matlegault/lumae-releases/blob/main/docs/MCP.md">MCP guide</a> ·
  <a href="https://github.com/matlegault/lumae-releases/releases">Changelog</a> ·
  <a href="https://lumae.app/feedback">Feedback</a>
</p>

<p align="center">
  <a href="https://github.com/matlegault/lumae-releases/releases/latest"><img src="https://raw.githubusercontent.com/matlegault/lumae-releases/main/docs/images/lumae-mac-screen-recorder-editor.jpg" alt="Lumae's editor on a Mac: a screen recording of a deploy console framed on a painted background, with automatic zooms, narration and captions on the timeline below"></a>
</p>

---

**Lumae** turns a raw screen recording into a product demo that looks edited by hand. Record a
display, a window or an area of your Mac; Lumae zooms in where you clicked, redraws the cursor so
it glides, frames the video on a background, and transcribes your voice into captions. Add your
camera, a voiceover, music and title cards on one timeline, then export MP4, MOV, ProRes or GIF.
Screenshots get the same treatment: capture, annotate, frame, copy.

It is native (SwiftUI, AppKit, ScreenCaptureKit, AVFoundation), everything runs on your Mac,
and it is free: no account, no watermark, no export limits.

And because Lumae is also a [Model Context Protocol](https://modelcontextprotocol.io) server,
**Claude Code, Claude Desktop, Codex, Cursor or any MCP client can film a demo, cut it, zoom it,
caption it and export it for you**, working live in the same editor you use.

## Contents

- [Install](#install)
- [Features](#features)
- [Let an AI agent record and edit your demos (MCP)](#let-an-ai-agent-record-and-edit-your-demos-mcp)
- [Privacy](#privacy)
- [Keyboard shortcuts](#keyboard-shortcuts)
- [FAQ](#faq)
- [Feedback and support](#feedback-and-support)

## Install

**Disk image.** Download `Lumae-<version>.dmg` from the
[latest release](https://github.com/matlegault/lumae-releases/releases/latest), open it and drag
Lumae into Applications. Every build is signed with a Developer ID and notarized by Apple.

**Homebrew.**

```bash
brew install --cask matlegault/lumae/lumae
```

**Requirements.** macOS 26.0 or later, on Apple silicon or Intel (Lumae is a universal app).

On first launch Lumae asks once for the Screen Recording permission. The microphone and camera are
asked for only when you first record with them.

**Updates** arrive inside the app through [Sparkle](https://sparkle-project.org): Lumae checks once a
day, downloads a small signed delta, and installs when you say so. **Lumae › Check for Updates…**
checks right away. Homebrew leaves an installed copy alone, so the app stays the one updater.

## Features

### Screen recording

- **Record a display, a window or an area** with Lumae's own selector: drag an area, press Space to
  pick a window, or take the whole display. Start from the menu bar, the library or a global
  shortcut in any app.
- **System audio and the microphone** are one toggle each, and you choose the microphone.
- **Film your camera at the same time.** It lands on a lane of its own as a bubble: circle,
  squircle, square or widescreen, any corner, with a ring, a shadow and mirroring. A floating
  preview shows you on screen while you record, and fades when the pointer comes near it so you
  can see what you are clicking.
- **Keep the recording controls out of the shot.** Drag the recording pill anywhere; the next
  recording opens it in the same spot.
- **Retake one clip** without touching the rest of the project, or record a new clip onto the end.

### Automatic zoom, smooth cursor, motion blur

- **Automatic zoom** reads the clicks in your recording and zooms in on them. Clicks close together
  become one move, leading in before the first and holding after the last. Every zoom stays
  editable: move it, resize it, change its scale, or add your own.
- **Zooms can follow the cursor**, panning to keep the pointer in view, or be aimed by hand on a
  focus map of the frame. Set the scale new zooms start at, how long they ease and the shape of
  the ease (Gentle, Standard or Snappy) once for the whole video.
- **A cursor worth watching.** Lumae hides the real pointer and redraws it from macOS's own vector
  artwork: a smoothed path, sharp at any zoom, w