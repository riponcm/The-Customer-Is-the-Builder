# GhostEdit

**Free, open-source offline grammar checker for macOS. Fix grammar, spelling, and punctuation in any app with a single hotkey - powered by local Hugging Face models (T5, Gemma, Llama), Claude, OpenAI Codex, or Gemini. On-device AI grammar correction with streaming preview, live feedback, writing coach, and no subscriptions. The best free Grammarly alternative for Mac.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS%2013%2B-black.svg)](https://github.com/nareshnavinash/GhostEdit/releases)
[![Latest Release](https://img.shields.io/github/v/release/nareshnavinash/GhostEdit)](https://github.com/nareshnavinash/GhostEdit/releases/latest)

> GhostEdit is a lightweight macOS menu bar app that corrects grammar, spelling, and punctuation in any text field system-wide. Press a hotkey and your text is fixed instantly - using local Hugging Face models on-device or your choice of Claude, Codex, or Gemini. Streaming preview shows corrections in real time. No accounts, no subscriptions, no data leaves your Mac.

![GhostEdit launch preview](remotion/out/TwitterBanner.png)

## Installation

### Homebrew (Recommended)

```bash
brew tap nareshnavinash/ghostedit
brew install --cask ghostedit
```

This installs GhostEdit to `/Applications`, clears the quarantine flag automatically, and supports `brew upgrade --cask ghostedit` for future updates.

### Manual Download

Download the latest `.dmg` from the [Releases page](https://github.com/nareshnavinash/GhostEdit/releases/latest), drag GhostEdit to Applications, and grant Accessibility permission.

### macOS Installation & Troubleshooting

Because GhostEdit is not currently signed with an Apple Developer certificate, macOS Gatekeeper may flag it and show an error saying: **"Apple could not verify 'GhostEdit' is free of malware"** or **"'GhostEdit' is damaged and can't be opened."**

If you encounter this error and only see a "Move to Bin" option, you can easily bypass it using one of the following methods:

#### Method 1: Using Terminal (Recommended)
This removes the macOS "quarantine" flag from the downloaded app, allowing it to run normally.

1. Unzip the downloaded release and move `GhostEdit.app` to your **Applications** folder.
2. Open the **Terminal** app.
3. Paste the following command and press Enter:
   xattr -cr /Applications/GhostEdit.app

You can now double-click the app to open it normally! (You only need to do this once).

#### Method 2: System Settings
1. Attempt to open the app normally by double-clicking it (this triggers the error). Click Done.
2. Open your Mac's System Settings and go to Privacy & Security.
3. Scroll down to the Security section.
4. You will see a message saying that "GhostEdit" was blocked. Click the Open Anyway button next to it.
5. Enter your Mac password or use Touch ID, and click Open on the final prompt.

## Trailer

![GhostEdit launch trailer](remotion/out/LaunchTrailerInstant.gif)

## Why GhostEdit?

- **No account required** - uses AI CLIs you already have installed (Claude, Codex, Gemini). No sign-ups, no subscriptions.
- **Privacy-first** - text never leaves your machine through a third-party service. Corrections run through your own local LLM. No telemetry, no data collection.
- **Free and open source** - no premium tiers, no word limits, no feature gates. Full grammar correction, streaming preview, writing coaching, and history - all included.
- **Works everywhere** - correct text in any macOS app: Slack, Notion, VS Code, Mail, Pages, or any text field. One hotkey, any app.
- **Bring your own AI** - switch between Claude, OpenAI Codex, and Gemini from Settings. Pick the model that works best for you.
- **On-device grammar** - local Hugging Face models (T5, Gemma, Llama) and Harper provide fully offline corrections with no API calls needed.
- **Streaming preview** - watch corrections appear in real time with character-level diff highlighting, then accept, regenerate, or cancel.

## How It Works

1. **Press cmd+E** for a local fix - a two-pass pipeline runs Harper grammar rules first, then your local Hugging Face model corrects spelling and grammar entirely offline
2. **Press cmd+shift+E** for a deep LLM fix - Claude, Codex, or Gemini rewrites and polishes your text with full contextual understanding, shown live via streaming preview
3. **No selection? No problem** - if no text is selected, GhostEdit automatically extracts the line at your cursor and corrects it
4. **See what changed** - an integrated diff overlay highlights every correction in the HUD before it's applied, and you can undo any fix instantly

No setup needed for local fixes. For LLM fixes, install any supported AI CLI and GhostEdit auto-detects it.

## Features

### v7.5 Highlights

- **Streaming preview with live diff**: Watch AI corrections stream in character by character with real-time diff highlighting - accept (Tab), regenerate (R), or cancel (Esc) from the preview window with change navigation
- **Per-model custom prompt templates**: Each local Hugging Face model can have its own task prompt - customize via Settings > Local Models or `localModelPromptTemplates` in config
- **Two-pass local correction pipeline**: cmd+E runs Harper grammar rules first, then applies your local Hugging Face model for deeper corrections - catching more issues than either engine alone
- **Line-at-cursor extraction**: No need to select text first - GhostEdit automatically detects and corrects the entire line at your cursor position in any app
- **Independent cloud hotkey**: Configure the cloud LLM hotkey (cmd+shift+E) separately from the local fix hotkey - both are fully customizable in Settings > Hotkey
- **Integrated diff in HUD overlay**: The diff preview is merged directly into the ghost HUD - see corrections at a glance without a separate window
- **Token preservation everywhere**: Mentions, URLs, emojis, and code blocks are now protected across all cor