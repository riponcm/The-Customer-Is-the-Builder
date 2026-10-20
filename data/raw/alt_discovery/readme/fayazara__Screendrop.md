# Screendrop

A beautiful screenshot + screen recording + Loom alternative - all native, self hostable and free.

<p>
  <a href="https://github.com/fayazara/Screendrop/releases/latest/download/Screendrop.dmg">
    <img src="download-button.png" alt="Download the latest version of Screendrop" width="220">
  </a>
</p>

<img width="3494" height="2206" alt="Screendrop_2026-08-17-09-17-20-compressed-550B05" src="https://github.com/user-attachments/assets/e4c2ef6c-97af-4ad4-8885-442c7fbb07b7" />



<br />
<br />



> [!IMPORTANT]
> Screendrop is under active development. Expect rough edges and occasional breaking changes


<p>
  <a href="https://github.com/fayazara/Screendrop/releases/latest">Latest release</a>
  ·
  <a href="https://github.com/fayazara/Screendrop/releases">All releases</a>
</p>


## Features

- Capture a display, window, or selected area as a screenshot or recording.
- Configure global hotkeys, timers, file formats, save behavior, and complete after-capture workflows.
- Copy, compress, save, pin, preview, annotate, edit, upload, or delete directly from a customizable floating preview stack.
- Grab text off the screen with on-device OCR - no screenshot saved, just the text on your clipboard.
- Open images from Finder with Screendrop and edit imported copies without touching the originals.
- Annotate non-destructively with drawing tools, crop, smart redaction, backgrounds, wallpaper packs, perspective effects, progressive blur, borders, and watermarks.
- Record camera, microphone, and system audio as separately editable sources.
- Use a notch-native teleprompter that follows your narration with on-device speech recognition.
- Edit recordings with smooth zooms, reconstructed cursors and clicks, keystroke captions, camera layouts, clip cuts, speed changes, social aspect ratios, and reusable style presets.
- Transcribe narration on-device, burn in karaoke-style captions, or edit the video by cutting its transcript.
- Share through your own Cloudflare account with a video player, scrub previews, searchable transcripts, comments, and rich link previews.
- Automate screenshots and recordings with Apple Shortcuts, Siri, and App Intents.

## Install

### Download

1. Download the latest `Screendrop.dmg` using the button above or from the [releases page](https://github.com/fayazara/Screendrop/releases/latest).
2. Open the DMG and drag **Screendrop** into your Applications folder.
3. Launch Screendrop. It lives in the menu bar at the top-right of the screen.

The download button always points to the newest release.

**Requirements:** macOS 26.4 or newer.


### Homebrew

Install from the Homebrew tap:

```bash
brew install --cask fayazara/tap/screendrop
```

Update later with:

```bash
brew upgrade --cask screendrop
```

Screendrop can also update itself through Sparkle.

## Quick Start

Screendrop can be controlled from its menu bar item or with global hotkeys.

| Default shortcut | Action |
| --- | --- |
| `Option + 1` | Capture full screen |
| `Option + 2` | Capture a window |
| `Option + 3` | Capture an area |
| `Option + 4` | Open the screen-recording picker |
| `Option + 5` | Capture text (OCR) to the clipboard |

All five shortcuts are customizable under **Settings → Screenshots** and **Settings → Screen Recordings**. If a replacement shortcut cannot be registered, Settings explains the failure and keeps your previous working shortcut.

You can also:

- Run capture and recording actions from Apple Shortcuts, Siri, or Spotlight.
- Right-click one or more images in Finder and choose **Open With → Screendrop**.
- Browse screenshots and recordings together in the native Library, or reopen recent captures from the menu bar.

## Screenshots

### Capture

Capture an entire display, a window, or a freely selected area. Screenshots are taken at native display resolution and imported into the local Library before any optional automation runs.

Screenshot preferences include:

- A self-timer of 3, 5, or 10 seconds.
- Optional window shadows.
- Automatic trimming of the empty black menu-bar strip on notched Macs.
- PNG or JPEG export with configurable JPEG quality.
- A configurable export folder and a Save action that can bypass the save panel.
- A lower-resolution editor preview to reduce memory use while preserving full-resolution exports.
- An option to include Screendrop's own windows in screenshots and recordings; they are excluded by default.

### Capture Text

**Capture Text** (`Option + 5`, or the menu bar) drags out an area like a normal
area capture, recognizes the text inside it with on-device Vision OCR, and puts
that text on the clipboard. No image is saved, nothing is added to Library, and
no preview card appears - a brief toast confirms what was copied.

Recognized lines are returned in reading order, so multi-column screenshots
paste in the order you read them rather than the order Vision happened to find
them.

### After-Capture Automation

Choose exactly what happens after every screenshot:

- Show the preview overlay.
- Copy the image to the clipboard.
- Save it to the export folder.
- Upload it and copy the share link.
- Open the annotation editor.
- Pin it above other windows.

Recording automation has its own independent settings for previewing, copying, saving, uploading, and opening Studio. Automatic uploading requires Cloud setup; the action links directly to **Settings → Cloud** when configuration is missing.

### Floating Preview Stack

New captures appear as floating cards on the active display. From a card you can:

- Copy the capture or drag it into another app.
- Save it to disk.
- Create a smaller JPEG.
- Pin a screenshot as an always-on-top reference.
- Open Quick Look.
- Annotate a screenshot or edit a recording.
- Upload to your cloud and copy the link.
- Delete the file or dismiss only the preview.
- Copy recognized text from a screenshot using on-device OCR.

The overlay can appear on the left or right, close automatically after a chosen delay, and dismiss 