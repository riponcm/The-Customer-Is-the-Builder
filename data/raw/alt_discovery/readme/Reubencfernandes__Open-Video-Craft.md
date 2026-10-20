<div align="center">

<img src="src/renderer/assets/app.png" alt="Open Video Craft" width="96" />

# Open Video Craft

**Record your screen, camera, and audio — then cut, mix, subtitle, and export locally. No required account or upload.**

[**Download Open Video Craft for macOS or Windows →**](https://github.com/Reubencfernandes/Open-Video-Craft/releases/latest)

[![Latest release](https://img.shields.io/github/v/release/Reubencfernandes/Open-Video-Craft?label=download&color=34d399)](https://github.com/Reubencfernandes/Open-Video-Craft/releases/latest)
[![Community](https://img.shields.io/badge/community-questions%20%26%20feedback-f472b6)](https://github.com/Reubencfernandes/Open-Video-Craft/discussions/7)
[![Source platforms](https://img.shields.io/badge/source-macOS%20%7C%20Windows-6366f1)](#development)
[![Built with Electron](https://img.shields.io/badge/Electron%2043-React%20%2B%20TypeScript-38bdf8)](#development)

</div>

![The editor with the timeline, subtitle lanes, and camera composition](build/app-store/screenshots/01-editor.png)

## What it does

Open Video Craft is a desktop screen studio in two parts:

1. **A floating recorder** captures your selected display with optional camera,
   microphone, and **system audio** tracks — each saved as its own file inside a
   plain project folder you can open, move, or back up like any other folder.
2. **A timeline editor** opens the recording (or any imported media) for
   editing: cut, move, trim, copy/paste, zoom-in effects, speed ramps,
   AI-generated subtitles, camera layouts, backgrounds, and dB-based audio
   mixing. FFmpeg exports MP4, WebM, or MOV, and subtitles can be written as a
   synchronized `.srt` sidecar.

Recording, editing, Whisper transcription, and export run locally. Optional
Gemini, Cohere, and Claude Code connections are used only when you explicitly
invoke their AI features.

## Screenshots — v1.0.3

| Launcher | Floating recorder |
| :---: | :---: |
| ![Launcher with recent projects](docs/screenshots/launcher.png) | ![Floating recorder controller](docs/screenshots/recorder.png) |

| Editor workspace | Timeline & subtitles |
| :---: | :---: |
| ![Editor with backgrounds, preview, and multi-lane timeline](build/app-store/screenshots/01-editor.png) | ![Timeline and multilingual subtitle inspector](build/app-store/screenshots/02-timeline-subtitles.png) |

### Latest improvements

- The projects dashboard now gives recent projects more room, waits for real
  thumbnails instead of flashing placeholder artwork, and keeps the latest
  recordings one click away.
- The floating recorder has a camera-first preview, an opaque recording timer,
  clearer controls, and a compact mode that stays out of the captured content.
- Timeline clips have a stronger selected state, Space consistently controls
  playback across editor panels, and drag-selection no longer outlines the
  whole timeline.
- Whisper, Gemini, and Cohere subtitle generation now expose consistent
  timeline processing states. On-device Whisper auto-detects the spoken
  language, while readable errors and retry guidance replace raw provider
  payloads.
- Subtitle cues stay sorted by their timeline position, send a fast red laser
  beam between cues, highlight the active cue in red, and keep start/end
  timestamps read-only because timing is adjusted by dragging or trimming the
  timeline clip.
- AI prompts can be copied, concurrent requests are guarded cleanly, and Gemini
  errors are presented as concise messages instead of IPC implementation text.
- Text overlays can be added directly to the viewport and styled with consistent
  font, weight, color, opacity, position, size, and animation controls. Their
  readable layer index follows viewport and timeline selection in red.
- Unsupported legacy project entries can be removed safely from Recents without
  deleting an unknown or incompatible folder from disk.
- The export dialog is wider and more compact, video corners now offer clear
  Flat, Slight, and Rounded choices, and selected clips remain
  visible over bright filmstrip frames.

## Features

### Recording

- Floating always-on-top recorder with pause/resume, countdown, and a compact pill mode.
- Screen, camera, microphone, and **system/desktop audio** as separate tracks.
- The selected display is identified inside the recorder without placing a
  display-sized overlay over macOS or Windows.
- Media is written to disk in chunks while you record, limiting data loss after
  an interrupted recorder session.
- Recorder-renderer crashes and failed device acquisition are handled without
  wedging the active app session.

### Editing

- Multi-lane timeline: video, audio lanes, zoom, speed, and subtitle tracks.
- Export-correct crossfade, fade-through-black, slide-left, and wipe-left clip transitions.
- Move, trim, split, delete, and **copy/paste clips** — with undo/redo.
- Horizontal timeline zoom and a resizable timeline panel.
- Zoom-in effects with an adjustable focal point; speed sections up to 5×.
- Camera layouts (bubble, side-by-side, presenter…), draggable/resizable
  screen and camera, backgrounds and corner styling.
- **Multilingual on-device Whisper subtitles** with automatic language
  detection and word-level karaoke highlighting, plus draggable and trimmable
  subtitle clips with millisecond-accurate read-only timestamps in the cue list.
- Per-lane mute and volume controls with the same mix used for preview,
  transcription, and export; background music drops straight onto the timeline.
- Debounced autosave, dirty-state close protection, and safe recovery from an
  invalid or unsupported `editor.json`.
- Export to MP4 / WebM / MOV at source, 720p, 1080p, or 1440p, with microphone,
  system audio, background audio, per-track levels, and optional `.srt` subtitles.
- Connect Claude Code through the built-in local MCP server or Gemini with an
  API key so an AI agent can inspect and edit the complete project surface.

> **Current project-timeline export