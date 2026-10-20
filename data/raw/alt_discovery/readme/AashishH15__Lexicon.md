<p align="center">
  <img src="media/lexicon-logo-windows.png" alt="Lexicon logo" width="150" />
</p>

<h1 align="center">Lexicon</h1>

<p align="center">
  <strong>A local-first writing assistant for clearer drafts.</strong><br />
  Proofread, rewrite, format, and export your work while keeping your words on your machine.
</p>

<p align="center">
  <a href="https://lexicon-writer.pages.dev/">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://github.com/AashishH15/Lexicon/releases/latest">Download release</a>
  &nbsp;&middot;&nbsp;
  <a href="https://discord.gg/nDCedWH3SV">Report an issue</a>
  &nbsp;&middot;&nbsp;
  <a href="https://discord.gg/nDCedWH3SV">Discord</a>
</p>

<p align="center">
  <a href="https://github.com/AashishH15/Lexicon/releases/latest"><img src="https://img.shields.io/github/v/release/AashishH15/Lexicon?display_name=tag" alt="Latest release" /></a>
  <a href="https://github.com/AashishH15/Lexicon/releases"><img src="https://img.shields.io/github/downloads/AashishH15/Lexicon/total" alt="Total Downloads" /></a>
  <a href="https://github.com/AashishH15/Lexicon/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License" /></a>
  <a href="#download"><img src="https://img.shields.io/badge/supported%20OS-Windows%20%7C%20macOS%20%7C%20Linux-4c8bf5" alt="Supported OS: Windows, macOS, and Linux" /></a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=LGL-8wP_CAY" target="_blank">
    <img src="media/Lexicon.gif" alt="Lexicon editor tour" />
  </a>
  <br />
  <sub>🍿 <em>Click the GIF above or <a href="https://www.youtube.com/watch?v=LGL-8wP_CAY">watch the full project launch video on YouTube</a> (with audio)</em></sub>
</p>

Lexicon is a distraction-free rich-text editor with inline proofreading,
local AI writing tools, and a review panel for suggestions. It is designed to
feel calm, private, and useful without requiring an account or a cloud writing
service.

## Download

Download the installer for your device from the
[latest GitHub release](https://github.com/AashishH15/Lexicon/releases/latest).

### Windows

- **x64** - most modern Intel and AMD PCs
- **ARM64** - Windows ARM devices
- **x86** - older 32-bit Windows systems

The Windows installer bundles the app backend and its runtime. You do not need
Python, Node.js, or Java to use the installed application.

Windows builds are not yet Authenticode code-signed. That can trigger
**SmartScreen** and occasional **antivirus false positives** (Windows Defender,
AVG, and similar). Lexicon is open source and MIT-licensed; only download
installers from this repository’s
[Releases](https://github.com/AashishH15/Lexicon/releases) page.

**SmartScreen (“Windows protected your PC”):**

1. Click **More info**
2. Click **Run anyway**

**Antivirus quarantine / “malicious code” warnings:** these are usually
reputation heuristics on new or unsigned indie installers, not a confirmed
infection. If Defender or another AV blocks the file, restore/allow it from
quarantine after you have confirmed the download came from the GitHub Releases
URL above. If you are unsure, compare the release asset name and checksums on
the release page before allowing.

### macOS

- **Apple Silicon / arm64** - M-series Macs
- **Intel / x64** - Intel Macs

The macOS build is currently pre-release (**unsigned**). Gatekeeper may block
launch or prevent the background engine from spawning because the app is not
notarized by Apple. That is an unsigned-developer warning, not a claim that the
build contains malware. Only download builds from this repository’s releases
page.

If Gatekeeper blocks Lexicon:

- **GUI:** Control-click (right-click) `Lexicon.app` → **Open** → **Open**
- **System Settings:** **Privacy & Security** → **Open Anyway**
  ([Apple’s guide](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac))
- **Terminal:** `xattr -cr /Applications/Lexicon.app` to clear the download
  quarantine flag


### Linux

- **DEB (`.deb`)** - Debian, Ubuntu, Linux Mint, Pop!_OS, etc.

## First launch

1. Open Lexicon and choose whether to download a local AI model.
2. Choose **Light** for the smaller, faster model (about 0.8 GB), or
   **Standard** for the larger model (about 1.4 GB).
3. Wait for the download progress to finish. The model is stored in your local
   app data and does not need to be downloaded again after a restart.
4. The first AI action may briefly warm up the local model. Proofread uses the
   separate LanguageTool engine and does not require the AI model.

The editor and proofreading tools work without downloading an AI model. The AI
tools can also use an existing local Ollama server when one is available.

## Updates

Lexicon checks for new releases when it starts and provides **Check for
updates** in Settings. Updates install over the app while keeping downloaded
models and other app data in the user profile, so models do not need to be
downloaded again after an update.

## What Lexicon includes

### Writing workspace

- Rich-text editing with headings, lists, tasks, links, images, code blocks,
  tables, blockquotes, alignment, highlights, and typography rules
- Inline and block LaTeX math with a live preview editor
- Slash commands with keyboard navigation
- Resizable side panels, Focus Mode, drag handles, and local auto-save
- Language, font size, line spacing, and keyboard shortcut settings
- Personal dictionary for words that should not be flagged

### Proofreading and review

- Local LanguageTool proofreading with inline grammar and spelling squiggles
- Clickable suggestion cards that stay synchronized with the editor
- Apply, dismiss, accept all, and dismiss all actions
- Dismissed suggestions remain dismissed across re-checks
- Tone detection and a clarity/readability score

### Local AI tools

With a downloaded bundled model, Lexicon provides:

- Rewrite and Concise
- Friendly, Professional, Academic, Formal, Casual, Playful, Empathetic,
  Persuas