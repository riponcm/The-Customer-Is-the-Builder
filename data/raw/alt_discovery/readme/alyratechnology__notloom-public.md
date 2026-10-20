<p align="center">
  <img src="native/notloom-art.png" alt="Not Loom, by Alyra Technology" width="300">
</p>

A tiny, free, local screen recorder for product demos, walkthroughs, and call recordings. Records your full screen with your webcam in a circle overlay and saves the video straight to your computer.

**No cloud. No account. No subscription. Nothing ever leaves your machine.**

Built by [Alyra Technology](https://alyratechnology.com) because we wanted the core of Loom or Cap without the SaaS around it.

## What's in this repo

| Version | Runs on | Best for |
|---|---|---|
| **Native app** (`native/Not Loom.app`) | macOS 13+ | The full experience: menu-bar app, true WYSIWYG camera circle, call recording with system audio, echo cancellation |
| **Browser version** (`index.html`) | macOS and Windows, in Chrome or Edge | Zero-install recording on any machine |

## Features

- **Camera circle overlay**: your webcam in a draggable, resizable circle. In the native app, what you see on screen is exactly what lands in the video.
- **Invisible controls**: the record bar, timer, and menu-bar icon never appear in the recording. The native app filters its own windows out of the capture at the OS level (the same approach Loom and Cap use).
- **Call recording** (native app): records system audio (your teammates' voices) and your mic mixed into one track, with FaceTime-style echo cancellation and automatic mic ducking while others talk.
- **Pause and resume**: paused time is cut from the file seamlessly, as if it never happened.
- **Local output**: full-resolution 30 fps H.264 `.mp4`, saved to your Desktop (demos) or Movies folder (calls).
- **Optional shared-folder handoff** (native app): point it at any synced folder (Google Drive for desktop, Dropbox, OneDrive) and finished call recordings are moved there, monitored until the sync completes, then evicted from local disk to free space.

## Quick start on macOS

1. Download the repo: `git clone https://github.com/alyratechnology/notloom-public.git`, or click the green **Code** button then **Download ZIP** and unzip it.
2. Open the `native` folder and double-click **Not Loom.app**.
3. If macOS warns that the app is from an unidentified developer (it will, if you downloaded the ZIP): right-click the app, choose **Open**, then click **Open**. One time only. If macOS says the app is damaged, run:
   ```
   xattr -dr com.apple.quarantine "Not Loom.app"
   ```
4. Grant the one-time permissions:
   - **Camera and Microphone**: macOS asks on first launch. Allow both.
   - **Screen Recording**: on your first Record click, macOS sends you to System Settings, Privacy & Security, Screen Recording. Enable Not Loom, then relaunch the app (macOS requires the relaunch).

You're set. The app lives in the menu bar (circle icon, no dock icon) and puts two things on screen:

- **Camera circle** (bottom-right by default). Drag it anywhere. Always on top. This is exactly what gets recorded.
- **Control bar** (left side by default). Record / Pause / Stop, a timer, and a circle-size slider. It never appears in recordings.

Recordings save automatically as `CircleRecorder-<date>.mp4` and Finder reveals the file when you stop.

### Recording a call (Zoom, Meet, Teams)

Choose the call-recording mode from the menu-bar icon. The app captures the screen, system audio, and your mic together. Tips:

- Use the built-in speakers or AirPods. Echo cancellation can't initialize on some monitor or dock audio outputs; the app falls back to mic ducking and tells you when that happens.
- Recordings land in your Movies folder unless you configure a shared folder (below).

### Optional: auto-move recordings to a synced folder

If you use Google Drive for desktop, Dropbox, or OneDrive, you can have finished call recordings moved into a synced folder automatically. Set it once in Terminal:

```
defaults write com.alyra.notloom SharedDriveFolder "/path/to/your/synced/folder"
```

The app moves the file there, waits for the sync client to finish uploading, then frees the local disk space and notifies you. To turn it off:

```
defaults delete com.alyra.notloom SharedDriveFolder
```

### Building from source

The whole app is one Swift file, `native/main.swift`. With Xcode command line tools installed:

```
cd native && ./build.sh
```

The build is ad-hoc signed by default. If you rebuild often, set `CODESIGN_IDENTITY` to an Apple Development certificate so the macOS permission grants survive rebuilds:

```
CODESIGN_IDENTITY="Apple Development: you@example.com (TEAMID)" ./build.sh
```

## Quick start on Windows

The browser version covers Windows. It records your screen, camera circle, and mic (no system audio).

1. Download the repo (same as above).
2. Open the `windows` folder and double-click **`Start Circle Recorder.bat`**. It starts a tiny local server (built into Windows, nothing to install) and opens the recorder in your default browser.
3. Use **Chrome or Edge**. If your default browser is something else, open one of those at `http://localhost:4831/index.html`.
4. Keep the command window open while you record.

If SmartScreen warns about the .bat file, click **More info**, then **Run anyway**.

## Using the browser version (macOS or Windows)

macOS users can launch it by double-clicking `Start Circle Recorder.command` in the repo root.

1. Allow camera and microphone access when the browser asks.
2. Pick your camera and mic, position and size the circle, then click **Start recording** and share **Entire Screen** in the browser's picker.
3. Click **Float camera bubble**: a small always-on-top window with your camera, a timer, and Pause/Stop buttons. Drag it anywhere; the circle in the video follows it. Nothing in the bubble appears in the final video.
4. Switch to any app; recording keeps going. Pause and resume freely.
5. Click **Stop**, review, then **Save video**. Output is `.mp4` when the browser supports it, otherwise `.webm`.

## How it works

**Native app** (`native/main.swift`