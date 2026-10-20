# TextWarden: Private Grammar Checker for macOS

[![CI](https://github.com/PhilipSchmid/textwarden/actions/workflows/ci.yml/badge.svg)](https://github.com/PhilipSchmid/textwarden/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/PhilipSchmid/textwarden)](https://github.com/PhilipSchmid/textwarden/releases/latest)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-14%2B-brightgreen.svg)](https://github.com/PhilipSchmid/textwarden/releases/latest)

TextWarden is a free, open-source grammar checker and writing assistant for macOS. It checks English spelling, grammar, punctuation, and style while you type.

**Nothing you type is sent anywhere.** Your writing never leaves your Mac: not for grammar checking, not for AI features, and not for analytics. There is no account to create and no subscription.

<p align="center">
  <img src="Assets/textwarden_logo.svg" alt="TextWarden macOS grammar checker logo" width="320" height="320">
</p>

<p align="center">
  <a href="https://github.com/PhilipSchmid/textwarden/releases/latest">
    <img src="Assets/download-macos-button.png" alt="Download TextWarden for macOS" width="180">
  </a>
</p>

> [!NOTE]
> TextWarden is under active development. Apps do not all share text with macOS in the same way, so underlines and corrections may work differently from one app to another. If something breaks, please [open a bug report](https://github.com/PhilipSchmid/textwarden/issues/new/choose).

## Why TextWarden?

- **Your writing stays on your Mac:** Grammar checks run locally with [Harper](https://github.com/Automattic/harper), and optional AI features use Apple Intelligence on your Mac. TextWarden never uploads your text or prompts.
- **Works in many Mac apps:** Check writing in Apple apps, browsers, chat apps, web-based editors, and Microsoft Office.
- **Fast feedback:** TextWarden underlines errors when an app provides the location of each word. Otherwise, a small floating indicator shows the suggestions.
- **A rewrite without leaving your app:** Improve selected text using your preferred writing style, then review the changes before applying them.
- **No account or subscription:** Download the app and grant Accessibility permission. Your usage statistics and custom dictionary stay on your Mac.

## Features

- Real-time English grammar, spelling, punctuation, capitalization, and word-choice suggestions
- One-click corrections and a Fix All command for clear-cut errors
- American, British, Canadian, Australian, and Indian English dialects
- Custom vocabulary, the macOS learned-word dictionary, and optional word lists for technical terms, names, brands, abbreviations, and slang
- Optional detection of 69 selectable non-English languages to avoid false positives in multilingual documents
- Readability scores and sentence-complexity underlines for text with at least 30 words
- [Browser extension preview](#browser-extension-preview) with precise underlines and native writing tools
- Per-app pause controls, per-app underline controls, and website exclusions
- A built-in Sketch Pad for focused drafting and revision
- Optional automatic updates, with a separate channel for experimental releases

### Apple Intelligence writing tools

On macOS 26 or later, a compatible Mac with an Apple M-series chip can use Apple's built-in, on-device AI for:

- Style suggestions for clear, concise, formal, casual, or business writing
- Quick Rewrite, which proposes improvements to selected text using your configured writing style
- AI Compose, which drafts from your instructions or rewrites selected text with a specific instruction
- Sentence simplification and readability tips
- Quick actions in Sketch Pad for professional, friendly, concise, or refined rewrites

These features are off by default. Grammar checking, spell checking, custom dictionaries, language detection, and readability scoring do not require Apple Intelligence.

### Quick Rewrite

Quick Rewrite uses Apple Intelligence to suggest changes to selected text in supported apps, following your writing style from **Preferences → Style**. Compare the original and rewritten text before applying; nothing changes without your approval. AI can change meaning, so review the result carefully.

See [Quick Rewrite configuration](CONFIGURATION.md#quick-rewrite) for setup, shortcuts, and limits.

## Requirements

- macOS 14 Sonoma or later
- An Intel or Apple Silicon Mac
- Accessibility permission, so TextWarden can read and update text in other apps

Apple Intelligence features additionally require macOS 26, a supported Mac with an Apple M-series chip, and Apple Intelligence enabled in System Settings.

## Install TextWarden

1. Download the latest TextWarden installer (`.dmg`) from [GitHub Releases](https://github.com/PhilipSchmid/textwarden/releases/latest).
2. Drag TextWarden into the Applications folder and open it.
3. Grant Accessibility permission when macOS asks.
4. Start typing in a supported app.

The download works on both Intel and Apple Silicon Macs. To avoid overlapping suggestions, turn off the other app's built-in spelling and grammar checker when you use TextWarden there.

See the [Configuration Guide](CONFIGURATION.md) for every setting and the [Troubleshooting Guide](TROUBLESHOOTING.md) if the app, indicator, or underlines do not behave as expected.

## Browser Extension (Preview)

The extension adds precise underlines and TextWarden’s writing tools to Chrome, Brave, Firefox, Zen, and Safari. Your writing stays on your Mac. Google Docs and complex web editors are not supported yet.

Use a preview-enabled TextWarden build and open Preferences → Browser → Install Extension:

- Chrome / Brave: Enable Developer mode and Load unpacked from the revealed folder.
- Firefox / Zen: Load Temporary Add-on in `about:debugging` and select `manifest.json`. Repeat after each browser restart.
- Safari: Enable the bundled exte