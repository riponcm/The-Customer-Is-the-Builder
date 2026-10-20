<div align="center">
  <img src="static/logo-square.png" alt="Proofly Logo" width="128" height="128">

# Proofly

### Private AI Writing, Proofreading & Grammar Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Chrome](https://img.shields.io/badge/Chrome-141+-4285F4?logo=googlechrome&logoColor=white)](https://www.google.com/chrome/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

**Your privacy-first writing assistant powered by Chrome on-device AI**

<a href="https://www.youtube.com/watch?v=XU2wM87VukY" target="_blank"><img src="static/youtube-promo.png" alt="Watch Proofly Promo Video on YouTube" width="640"></a>

[Features](#features) •
[Why Proofly](#why-proofly) •
[Installation](#installation) •
[Contributing](#development) •
[Privacy](#privacy--security)

</div>

---

## What is Proofly?

Proofly is a free, open-source Chrome extension that brings professional-grade writing assistance directly to your browser—**without compromising your privacy**. Unlike cloud-based alternatives like Grammarly, LanguageTool, or QuillBot, Proofly uses Chrome's Built-in AI APIs to proofread your writing entirely on-device. Your keystrokes never leave your machine.

### The Problems We Solve

Traditional writing assistants require sending your text to remote servers:

- ❌ Your private data travels across the internet
- ❌ Your writing is stored on company servers
- ❌ Requires constant internet connectivity
- ❌ Subject to data breaches and privacy violations
- ❌ Injects excessive UI to the sites you visit
- ❌ Expensive subscription fees

### Our Solution

Proofly runs 100% locally on your device:

- ✅ **Zero data transmission** - Everything stays on your machine
- ✅ **Complete privacy** - No servers, no logs, no tracking
- ✅ **Works offline** - No internet required after model download
- ✅ **Free forever** - Open source, no subscriptions
- ✅ **Lightweight** - Minimal script injection, zero dependencies
- ✅ **User friendly** - Introduces fresh, non-invasive UX patterns
- ✅ **Customizable** - Complete control on how you'd like to get assistance

---

## Features

### Privacy-First Architecture

- **On-Device Processing**: All AI proofreading happens locally using Chrome's Built-in AI models
- **Zero Server Communication**: Your text never leaves your browser
- **No Telemetry**: We don't collect any usage data or analytics
- **Open Source**: Complete transparency - audit the code yourself

### Intelligent Writing Assistance

- **Multilingual**: Supports all languages that the built-in Gemini Nano model provides
- **Spelling Corrections**: Catch typos and misspellings instantly
- **Grammar Fixes**: Subject-verb agreement, tense consistency, and more
- **Punctuation**: Proper comma usage, missing periods, quotation marks
- **Capitalization**: Sentence starts, proper nouns, title case
- **Preposition Usage**: Correct preposition selection
- **Missing Words**: Detect incomplete sentences

### User-Friendly Interface

- **Visual Highlights**: Color-coded underlines for different issue types
- **Inline Corrections**: Click any highlight to see suggestions
- **Keyboard Shortcuts**: Quick access with customizable hotkeys (Cmd/Ctrl+Shift+P)
- **Auto-Correct Mode**: Real-time checking as you type
- **Manual Mode**: Check on-demand whenever you want
- **Selection Correction**: Proofread your own highlighted text on-demand
- **Issues Sidebar**: View issues, navigate through them and apply suggested corrections in a dedicated panel
- **Undo/Redo Support**: Full history management for corrections

### Performance & Compatibility

- **Lightweight**: Minimal footprint (<5KB initial injection)
- **Fast**: Instant suggestions powered by local on-device AI
- **Shadow DOM Isolation**: No interference with host pages
- **Works Everywhere**: Input fields, textareas, contenteditable elements
- **Web Standards Compliant**: Ignores auto-correction on fields based on their semantics

### Customization

- **Configurable Correction Types**: Enable/disable specific issue types
- **Custom Colors**: Personalize highlight colors for each issue type
- **Underline Styles**: Choose solid, wavy, or dotted underlines
- **Keyboard Shortcuts**: Customize your workflow with auto-fix or manual-fix options
- **Autofix on Double-Click**: Quick correction with double-click

---

## Why Proofly?

| Feature                | Proofly           | Grammarly        | LanguageTool     | QuillBot         |
| ---------------------- | ----------------- | ---------------- | ---------------- | ---------------- |
| **Privacy**            | ✅ On-device only | ❌ Cloud-based   | ❌ Cloud-based   | ❌ Cloud-based   |
| **Works Offline**      | ✅ Yes            | ❌ No            | ❌ No            | ❌ No            |
| **Cost**               | ✅ Free forever   | 💰 $12-30/mo     | 💰 $5-20/mo      | 💰 $8-20/mo      |
| **Open Source**        | ✅ Yes            | ❌ No            | ⚠️ Partial       | ❌ No            |
| **No Data Collection** | ✅ Zero tracking  | ❌ Collects data | ❌ Collects data | ❌ Collects data |
| **Lightweight**        | ✅ <5KB initial   | ❌ Heavy scripts | ❌ Heavy scripts | ❌ Heavy scripts |
| **Browser Support**    | Chrome 141+       | All browsers     | All browsers     | All browsers     |

### Key Advantages

1. **Privacy You Can Verify**: Open-source code means no hidden data collection
2. **No Subscription Treadmill**: Free forever, no artificial limitations
3. **True Offline Mode**: Works on airplanes, remote locations, anywhere
4. **Lightning Fast**: No network latency, instant corrections
5. **Resource Efficient**: Minimal CPU and memory usage
6. **Non-Invasive**: Minimal native code is injected to the sites only when needed
7. **No Account Required**: No sign-up, no email, no personal info
8. **Future-Proof**: Uses Chrome's standard Built-in AI API and modern web tech

---

## Technolog