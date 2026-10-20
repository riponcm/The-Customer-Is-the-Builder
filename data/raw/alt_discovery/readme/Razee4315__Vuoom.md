<div align="center">

<img src=".github/assets/logo.png" alt="Vuoom logo" width="110" />

# Vuoom

**Screen recordings that zoom where it matters.**

A **free, open-source screen recorder for Windows** with cinematic **auto-zoom**.
Record your screen, the camera glides into the action, and you export a small,
crisp **demo GIF or MP4** ready for your GitHub README, changelog, Slack, or
product post. No account, no watermark, no subscription.

**[Website](https://razee4315.github.io/Vuoom/)** · **[Download](https://razee4315.github.io/Vuoom/download/)** · **[Guide](https://razee4315.github.io/Vuoom/guide/)**

[![Latest release](https://img.shields.io/github/v/release/Razee4315/Vuoom?label=download&color=e5484d)](https://github.com/Razee4315/Vuoom/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Razee4315/Vuoom/total?color=2ea44f)](https://github.com/Razee4315/Vuoom/releases)
[![CI](https://img.shields.io/badge/CI-Windows%20checks-0078d4)](https://github.com/Razee4315/Vuoom/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](./LICENSE)
![Platform: Windows 10/11](https://img.shields.io/badge/platform-Windows%2010%2F11-0078d4)

<img src=".github/assets/screenshot-editor.png" alt="The Vuoom editor: zoom blocks, annotation lanes, speed regions and cuts on one timeline" width="820" />

</div>

---

## Why Vuoom?

A flat recording of your whole screen makes UI text tiny and the "wow" moment
invisible. The tools that fix this, the ones that smoothly zoom into each click
like a little camera operator (Screen Studio and friends), are **Mac-only, paid,
or both**. Vuoom is that experience as a free Screen Studio alternative for
Windows, in a small native app:

**Record, zoom happens where you point, cut the dead air, export a GIF or MP4
you can paste anywhere.**

## A studio, not a toolbar

The interface is a quiet workspace built from floating panels you control:

- **Every panel is yours to arrange.** Show or hide the tool rail, inspector and
  timeline (`Ctrl+1/2/3`), drag the inspector and timeline to any size, collapse
  the timeline to its transport bar, slim the tool rail to icons. Double click a
  divider to reset it, `Ctrl+0` resets everything. Layout is remembered.
- **An inspector that follows you.** Select something and its every property is
  there in collapsible sections; select nothing and the **Clip** tab holds the
  whole-recording settings: frame and backdrop, crop, auto zooms, pacing, click
  ripples and keystrokes.
- **Search every action** with `Ctrl+K`, right-click anything for its menu, and
  hover any control to see its shortcut.
- **Home that starts the right take**: Region, Full screen or Window, with frame
  rate, zoom strength, audio and countdown set right there.

| | |
|---|---|
| <img src=".github/assets/screenshot-home.png" alt="Vuoom home with recovery and recents" /> | <img src=".github/assets/screenshot-record.png" alt="Picking a region to record" /> |
| **Home that starts the right take.** Region, full screen or window, with frame rate, zoom and countdown on the page; recovery and recents below. | **Framing first.** One glass HUD over the frozen desktop: aspect presets, zoom, fps and countdown next to a single Record button. |
| <img src=".github/assets/screenshot-export.png" alt="The export card with GIF and MP4 presets" /> | <img src=".github/assets/screenshot-editor-light.png" alt="The editor in the light theme" /> |
| **Export without a wizard.** Format cards, presets, sliders, an honest size estimate and a fit-under-N-MB helper, then copy or reveal. | **Five themes, re-tuned.** Black and white first, plus Graphite, Paper and Midnight. No purple anywhere. |

## Features

- 🎥 **Native capture**: Windows Graphics Capture at full resolution: a region
  (free or 16:9 / 9:16 / 1:1 / 4:5), a whole display, or a single app window,
  on any monitor, with pause/resume. Capture is paced at the compositor to the
  frame rate you pick (24 / 30 / 60 fps), so a 144 Hz screen doesn't burn CPU on
  frames nobody needs.
- 🖱️ **A smooth pointer**: record without the real cursor and Vuoom draws a
  clean one from your movements, gliding (jitter smoothed out with no lag),
  pressing on every click, sized so it stays legible in a small GIF,
  scaling with the zoom like the real thing, and (if you like) fading away
  while it rests, back just before it moves.
- 🎙️ **Narration and system sound**: record your microphone, everything the
  computer plays, or both, each as its own track with a live level meter while
  you frame the shot. Audio is timed by the same clock as the frames, so it
  stays in sync through every cut and speed-up; sped-up stretches play silent.
  Waveforms sit on the timeline, with volume and mute per track, and MP4
  exports carry an AAC soundtrack.
- 🎥 **You, in the corner**: record your webcam alongside the screen and it
  appears as a bubble you can move to any corner, resize, reshape (circle,
  rounded square, 16:9) and mirror after the fact. The record HUD previews it
  live, right where it will sit.
- 🧹 **Studio-clean narration**: one switch removes fan noise, hum and hiss
  (RNNoise), another evens out a voice that drifts toward and away from the
  mic, with peaks held safely under clipping. Both work on a copy, so the
  original recording is always one click away.
- 💬 **Captions, made offline**: one click turns your narration into captions,
  on your own computer (whisper.cpp; the speech model downloads once, nothing is
  uploaded). They show in the preview and in every GIF and MP4, bottom or top, at
  the size you pick; fix any word in the inspector, drag a caption's bar to
  retime it, and save an `.srt` file timed to your export for YouTube and other
  players.
- 🗜️ **Recordings that stay small**: frames are stored losslessly as LZ4
  compressed XOR deltas with periodic keyframes, typically 20x+ smaller than raw
  pixels, streamed to disk as you record so length is bounded by yo