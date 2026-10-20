<div align="center">

<img src="assets/logo.svg" alt="GemType" width="420" />

**A free, open-source Grammarly alternative for your browser, Microsoft Word, and the whole desktop — powered by your own Gemini API key.**

[![Chrome Web Store](https://img.shields.io/chrome-web-store/v/linnnamnhkciekgpnegkcajcafmjlhgh?label=Chrome%20Web%20Store&logo=googlechrome&logoColor=white&color=4285F4)](https://chromewebstore.google.com/detail/linnnamnhkciekgpnegkcajcafmjlhgh)
[![Users](https://img.shields.io/chrome-web-store/users/linnnamnhkciekgpnegkcajcafmjlhgh?color=10a37f)](https://chromewebstore.google.com/detail/linnnamnhkciekgpnegkcajcafmjlhgh)
[![Rating](https://img.shields.io/chrome-web-store/rating/linnnamnhkciekgpnegkcajcafmjlhgh?color=f59e0b)](https://chromewebstore.google.com/detail/linnnamnhkciekgpnegkcajcafmjlhgh)
[![Edge Add-ons](https://img.shields.io/badge/Edge%20Add--ons-Live-0C88DA?logo=microsoftedge&logoColor=white)](https://microsoftedge.microsoft.com/addons/detail/edbehlnmfcjhlbdlnmklicdoaopobbel)
[![Firefox Add-ons](https://img.shields.io/amo/v/gemtype-ai-writing-assistant?label=Firefox%20Add-ons&logo=firefoxbrowser&logoColor=white&color=FF7139)](https://addons.mozilla.org/firefox/addon/gemtype-ai-writing-assistant/)
[![Manifest V3](https://img.shields.io/badge/manifest-v3-6366f1)](extension/manifest.json)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-D22128.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../pulls)

### [➜ Install free: Chrome](https://chromewebstore.google.com/detail/linnnamnhkciekgpnegkcajcafmjlhgh) · [Edge](https://microsoftedge.microsoft.com/addons/detail/edbehlnmfcjhlbdlnmklicdoaopobbel) · [Firefox](https://addons.mozilla.org/firefox/addon/gemtype-ai-writing-assistant/)

**[gemtype.matily.org](https://gemtype.matily.org)** — the official site, with a live demo and everything in one place.

<img src="assets/hero.svg" alt="GemType demo: typing with mistakes, wavy underlines appear, one click fixes them" width="820" />

</div>

---

## Watch the tutorial

[**▶ 2-minute tutorial on YouTube**](https://www.youtube.com/watch?v=j7Su-4hvigU) — install GemType, add your free Gemini key, and see grammar checking + rewrites in action.

## Now available

GemType runs everywhere you write — all surfaces share the same private,
bring-your-own-key core (your text goes straight to Google's Gemini API, never
through a server of ours):

| Platform | Status |
|---|---|
| **Chrome** | [Live on the Chrome Web Store](https://chromewebstore.google.com/detail/linnnamnhkciekgpnegkcajcafmjlhgh) |
| **Edge** | [Live on Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/edbehlnmfcjhlbdlnmklicdoaopobbel) |
| **Firefox** | [Live on Firefox Add-ons](https://addons.mozilla.org/firefox/addon/gemtype-ai-writing-assistant/) |
| **Microsoft Word** | Office task-pane add-in — see [`msword/`](msword/) |
| **Desktop (macOS · Windows · Linux)** | Menu-bar/tray app — works in **any** application via a global hotkey. [Download the latest release](../../releases/latest) · see [`desktop/`](desktop/) |
| **Safari** | Build ready (needs the Apple Developer fee — [sponsor](#sponsor-this-project)) |
| **iOS / Android keyboards** | Planned |

Works in **any language** (auto-detected), on any website, inside Word, and now anywhere on your desktop.

## Features

- **Live grammar and spelling checking** — underlines appear in any text field about a second after you stop typing: Gmail, LinkedIn, X, Reddit, GitHub, anywhere
- **One-click fixes** — click an underline and accept the correction; `Ctrl/Cmd+Z` always undoes
- **Sentence verification** — after every accepted fix, the surrounding sentence is automatically re-checked, so word-level fixes never leave broken sentences behind
- **Rewrite on demand** — select text for a floating toolbar with *Improve, Fix, Shorten, Formal,* and *Casual* actions, also available from the right-click menu
- **Context-aware suggestions** — an LLM judges whole sentences in any language, not just pattern rules
- **Bring your own key** — uses your free [Google AI Studio](https://aistudio.google.com/apikey) key; no account, no subscription, no middleman server
- **Private by design** — text goes only to Google's Gemini API; no tracking, no analytics, nothing else phones home
- **Full control** — per-site disable, global toggle, model picker, language setting; sites can exclude a field with `data-gemtype="false"`

## Comparison with Grammarly

| | GemType | Grammarly |
|---|---|---|
| Price | Free — bring your own Gemini key ([free tier](https://aistudio.google.com/apikey), no card required) | Free plan is limited; Premium $12–30 per month |
| Grammar and spelling fixes | Unlimited | Full corrections require Premium |
| Sentence re-check after each accepted fix | Automatic | Not available |
| AI rewrites (Improve, Shorten) | Included | Premium |
| Preset styles (Formal, Casual) | Included | Premium |
| Languages | Any language Gemini understands, auto-detected | English and a small set of variants |
| Trackers and analytics | None | Product analytics and telemetry |
| Account required | No | Yes |
| Where your text is processed | Google's Gemini API only, with your key — no middleman server | Grammarly's servers |
| Open source | Yes (Apache 2.0) | No |
| Google Docs | Not supported (Google whitelists specific vendors) | Supported |

**What does "bring your own key" really cost?** For a single person typing,
the free Gemini tier is more than enough — GemType checks only after you
pause, skips unchanged text, and caches results, so even a heavy writing day
stays comfortably inside the free quota. On the paid tier, a typical check
costs around $0.0003 — roughly one dollar per month for very heavy daily
use, compared with $144–360 per year for Premium.

## Screenshots

| | |
|---|---|
| ![Live checking with underlines and the issue-count badge](assets/screenshots/underlines.png) | ![Suggestion card 