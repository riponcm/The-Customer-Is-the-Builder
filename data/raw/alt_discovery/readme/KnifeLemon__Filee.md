<p align="center">
  <a href="https://filee.sh"><img src="docs/media/banner-en.jpg" alt="Filee: Drag. Drop. Converted." width="100%"></a>
</p>

<p align="center">
  <b>A free, open-source file converter you use by dragging.</b><br>
  Hold a key (<kbd>Ctrl</kbd>, <kbd>Option</kbd> on macOS), drag files and drop them on a format in the donut that opens at your cursor.
</p>

<p align="center">
  <a href="https://filee.sh"><b>Website</b></a> ·
  <a href="https://github.com/KnifeLemon/Filee/releases/latest"><b>Download</b></a> ·
  <a href="#install">Install</a> ·
  <a href="#command-line">Command line</a> ·
  <a href="#documentation">Docs</a>
</p>

<p align="center">
  <a href="https://github.com/KnifeLemon/Filee/actions/workflows/ci.yml"><img src="https://github.com/KnifeLemon/Filee/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/KnifeLemon/Filee/releases/latest"><img src="https://img.shields.io/github/v/release/KnifeLemon/Filee?color=7F77DD&label=release" alt="Latest release"></a>
  <a href="https://github.com/KnifeLemon/Filee/releases"><img src="https://img.shields.io/github/downloads/KnifeLemon/Filee/total?color=1D9E75" alt="Downloads"></a>
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-3C3489" alt="Windows 10 | 11">
  <img src="https://img.shields.io/badge/macOS%20%7C%20Linux-preview-534AB7" alt="macOS | Linux preview">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-6A62C9" alt="MIT license"></a>
</p>

<p align="center"><b>English</b> · <a href="README.ko.md">한국어</a> · <a href="README.zh-CN.md">简体中文</a></p>

<table>
  <tr>
    <td width="33%" valign="top"><b>Right at your cursor</b><br>No app window to open. The formats appear where you already are, only the ones that make sense for the files you drag.</td>
    <td width="33%" valign="top"><b>180 formats, no other software</b><br>Images, PDF, Word, Excel, PowerPoint, HWP, e-books, archives, fonts and CAD work without Office, Hancom Office or LibreOffice.</td>
    <td width="33%" valign="top"><b>Stays on your computer</b><br>Nothing is uploaded. Filee works offline and saves the result next to the original.</td>
  </tr>
</table>

## See it in action

<p align="center">
  <a href="https://filee.sh"><img src="docs/media/demo-en.webp" alt="Dragging trip.jpg with Ctrl held: a donut of formats opens at the cursor, the file is dropped on PNG, a progress ring completes and trip.png appears" width="820"></a><br>
  <sub>Watch the 27-second video and try the interactive demo on <a href="https://filee.sh">filee.sh</a></sub>
</p>

## Install

Download from [Releases](https://github.com/KnifeLemon/Filee/releases/latest).

### Windows 10/11 (64-bit)

Run `Filee-<version>-win-Setup.exe`. It asks for administrator rights once and installs Filee for all users. Setup
also offers the File Explorer menu entry, starting at sign-in, the `filee` command and the optional engines
(video and audio with FFmpeg, about 100 MB; rare formats with LibreOffice, calibre, Ghostscript or Pandoc).

Without installing: unzip `Filee-<version>-win-Portable.zip` and run `Filee.exe`.

When a new release is out, Filee shows it in the menu and the tray. **Update** downloads the installer, checks its
SHA-256 against the release and installs it, keeping your settings and engines. The portable copy opens the release
page instead.

### macOS 14 or later (preview)

1. Download `Filee-<version>-osx-arm64.tar.gz` (Apple silicon) or `Filee-<version>-osx-x64.tar.gz` (Intel).
2. Open Terminal in the extracted folder and run `./install.sh`. It copies Filee.app to `~/Applications` and adds
   the `filee` command to `~/.local/bin`.
3. The build is not notarized yet, so macOS blocks the first start. Allow it in System Settings → Privacy & Security
   → **Open Anyway**.
4. Filee asks for Accessibility permission, which <kbd>Option</kbd>+drag needs. It starts working as soon as you
   switch Filee on.

"Convert with Filee" appears when you right-click files in Finder. FFmpeg and Ghostscript come from Homebrew
(`brew install ffmpeg ghostscript`); Filee finds them by itself.

### Linux x64 and ARM64 (preview)

1. Download `Filee-<version>-linux-x64.tar.gz` or `Filee-<version>-linux-arm64.tar.gz`.
2. Run `./install.sh` in the extracted folder. It installs for your user only (no root), adds Filee to the app menu
   and the `filee` command to `~/.local/bin`. Python 3 is required.

Drag gestures need an X11 session (on Ubuntu, "Ubuntu on Xorg" on the login screen). Wayland doesn't let apps watch
global input, so there Filee works through the drop zone and the right-click action in Nautilus, Nemo, Thunar or
Dolphin. Ubuntu 24.04 is the tested baseline; `INSTALL.txt` in the package lists the system libraries.

## Features

- **Donut toolbar at the cursor.** Hold a modifier (<kbd>Ctrl</kbd>, <kbd>Option</kbd> on macOS) and drag files.
  Modifiers, mouse button, drag distance, a hold gesture and a keyboard shortcut for the selected files are all
  configurable, and apps where gestures should never fire can be picked from the running apps.
- **One toolbar per file type.** Images, PDF, documents, spreadsheets, presentations, HWP, text, e-books, video,
  audio, vector graphics, archives, CAD, fonts and mixed selections. Arrange presets on a live donut by drag and drop,
  search the profiles and presets, add extensions as tags.
- **Presets.** Quality, size, DPI, metadata, PDF merge, split and page ranges, video quality and resolution, audio
  bitrate, channels and WAV format, archive level, output folder, file names, conflict handling and keeping the
  original file dates. TIFF presets can join every file into one multi-page TIFF.
- **Batch conversion.** One file or a hundred, in parallel; one failure never stops the rest. "One ZIP" packs any
  files into an archive, "Merge PDF" makes one PDF.
- **Multi-step routes.** Filee finds conversions that need several steps (HWP → HWPX → DOCX, EPUB → HWPX → PDF → PNG),
  each step with the engine th