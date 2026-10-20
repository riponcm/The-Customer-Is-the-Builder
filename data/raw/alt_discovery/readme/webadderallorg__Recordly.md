Language: EN | [简中](README.zh-CN.md)

<p align="center">
  <img width="220" alt="Recordly Logo" src="https://github.com/user-attachments/assets/414b8838-6731-45d4-a815-6e3c0aa1fe52" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/macOS%20%7C%20Windows%20%7C%20Linux-111827?style=for-the-badge" alt="macOS Windows Linux" />
  <img src="https://img.shields.io/badge/open%20source-AGPL3.0-2563eb?style=for-the-badge" alt="AGPL 3.0 license" />
</p>

### Create polished demo videos in minutes
[Recordly](https://www.recordly.dev) is your **open-source screen recorder** and editor for **walkthroughs, demos, product videos**, and more. 
**Accepting PRs.**

<img width="1280" height="720" alt="MP4 to GIF export (4)" src="https://github.com/user-attachments/assets/e6d68606-5fc0-4f70-99cd-7521982dc13b" />


---
### Backed by the community
<a href="https://coderabbit.link/recordly"><img width="400" alt="CodeRabbit Typemark" src="https://github.com/user-attachments/assets/3926ecfd-8652-4f2d-8da8-ac7641017cf5" /></a>

---

## What is Recordly?

Recordly is a desktop app for recording and editing screen captures with motion-driven presentation tools built in. Instead of sending raw footage to a motion designer just to add zooms, cursor polish, or a styled background, Recordly handles that workflow in one place for free.

Recordly runs on:

- **macOS** 14.0+
- **Windows** 10 Build 19041+
- **Linux** on modern distros

Platform notes:

- **macOS** uses native ScreenCaptureKit-based capture helpers.
- **Windows** uses a native Windows Graphics Capture (WGC) helper on supported builds, with native WASAPI audio support.
- **Linux** records through Electron capture APIs. Cursor hiding is not supported on Linux today.

---

# Core Features

## Auto-zooms, cursor polish, and styled frames
Recordly can automatically emphasize activity with zoom suggestions, smooth cursor movement, add motion effects, and place the final composition inside a styled frame with wallpapers, colors, gradients, blur, padding, and shadows.

<p>
  <img src="./docs/media/feature1.gif" width="450" alt="Recordly cursor and zoom demo video">
</p>

## Dynamic webcam bubble overlays
Add webcam footage as an overlay bubble, position it with presets or custom coordinates, mirror it, control shadow and roundness, and optionally make it react to zoom so it stays visually balanced during motion.

<p>
  <img src="./docs/media/feature2.gif" width="450" alt="Recordly webcam overlay demo video">
</p>

## Timeline editing built for demos
Use drag-and-drop timeline tools for zooms, trims, speed regions, annotations, extra audio regions, and crop-aware edits. Save and reopen work as `.recordly` project files.

<p>
  <img width="450" alt="timeline editor" src="https://github.com/user-attachments/assets/3692bd8f-7b8d-4a93-b696-d17c828487ea" />
</p>

## Extensions & Marketplace

Recordly has a community-driven extension system. Anyone can build and publish extensions that add new capabilities to Recordly — cursor click sounds, device frames, browser mockups, wallpapers, render hooks, settings panels, and more.

Browse and install community extensions from the [Recordly Marketplace](https://marketplace.recordly.dev/extensions).

---

## All Features

### Recording

- Record an entire display or a single app window
- Jump directly from recording into the editor
- Capture microphone audio and system audio
- Use native capture backends where supported
- Resume editing from saved `.recordly` project files
- Open existing recordings or existing project files from the app

### Timeline and Editing

- Drag-and-drop timeline editing
- Trim unwanted sections
- Add manual zoom regions
- Use automatic zoom suggestions based on cursor activity
- Add speed-up and slow-down regions
- Add text, image, and figure annotations
- Add extra audio regions on the timeline
- Crop the recorded frame
- Save and reopen projects with editor state preserved

### Cursor Controls

- Show or hide the rendered cursor overlay
- Cursor size adjustment
- Cursor smoothing
- Cursor motion blur
- Cursor click bounce
- Cursor sway
- Cursor loop mode for cleaner looping exports
- macOS-style cursor assets for the rendered overlay

### Webcam Overlay

- Enable or disable webcam overlay footage
- Upload, replace, or remove webcam footage
- Mirror webcam footage
- Size control
- Preset positions and custom X/Y placement
- Margin control
- Roundness control
- Shadow control
- Optional zoom-reactive webcam scaling

### Frame Styling and Backgrounds

- Built-in wallpapers
- Runtime wallpaper discovery from the wallpapers directory
- Custom uploaded backgrounds
- Solid color backgrounds
- Gradient backgrounds
- Frame padding
- Rounded corners
- Background blur
- Drop shadows
- Aspect ratio presets for the final frame

### Export

- MP4 export
- GIF export
- Export quality selection
- GIF frame-rate selection
- GIF loop toggle
- GIF size presets
- Aspect ratio and output dimension controls
- Reveal exported files in the system file manager

### Workflow and Usability

- Customizable keyboard shortcuts
- In-app shortcut reference
- Feedback and issue links from the editor
- Project persistence for editor preferences
- Faster preview recovery after export
---

# Screenshots

<p align="center">
  <img src="https://i.postimg.cc/8CrQtGJf/Screenshot-2026-04-30-at-5-11-52-pm.png" width="700" alt="Recordly recording interface screenshot">
</p>

<p align="center">
  <img src="https://i.postimg.cc/pLSMfrTM/Screenshot-2026-04-30-at-5-11-45-pm.png" width="700" alt="Recordly editor screenshot">
</p>

<p align="center">
  <img src="https://i.postimg.cc/Zn9VY6bg/Screenshot-2026-03-18-at-6-32-59-pm.png" width="700" alt="Recordly timeline screenshot">
</p>

---

# Installation

## Download a build

Prebuilt releases are available at:

https://github.com/webadderallorg/Recordly/releases

---

## Arch Linux / Manjaro (yay)

Install from the AUR ([recordly-bin](https://aur.archlinux.org/packages/recordly-bin