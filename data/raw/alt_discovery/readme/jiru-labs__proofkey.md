# ProofKey

[![Chrome Web Store](https://img.shields.io/badge/Chrome%20Web%20Store-Install-4285F4?logo=googlechrome&logoColor=white)](https://chromewebstore.google.com/detail/loibjoemoahkajjnfioajcibcamhdafc)
[![Version](https://img.shields.io/chrome-web-store/v/loibjoemoahkajjnfioajcibcamhdafc?label=version&color=4285F4)](https://chromewebstore.google.com/detail/loibjoemoahkajjnfioajcibcamhdafc)
[![License](https://img.shields.io/github/license/jiru-labs/proofkey)](LICENSE)

A Grammarly-style writing assistant for Chrome that talks to **your** LLM, using **your** API key — or, in Google Chrome, to the model Chrome already keeps on your computer, with no key at all.

No backend, no account, no telemetry. Your text goes from your browser straight to the provider you picked, and nowhere else.

![Typing a draft, the underlines appearing, one fix applied from the card, then the shortcut fixing the rest](docs/demo.gif)

*Recorded against the shipped content script with canned corrections, so no key was involved. On a real site the suggestions come from the model you configured.*

> **[Install from the Chrome Web Store](https://chromewebstore.google.com/detail/loibjoemoahkajjnfioajcibcamhdafc)** — or [build it from source](#install-from-source) if you would rather read the code first.
>
> **New here?** In Google Chrome it works as installed: [Chrome's built-in model](#no-api-key-at-all-chromes-built-in-model) checks your writing on your own computer — free, no account, one download. For every action rather than two, [start with Gemini](#no-api-key-yet-start-with-gemini): about two minutes to a key, and ordinary use usually costs nothing.
>
> **What is actually known to work is a much shorter list than what is built.** The table below is the whole of it — [reports](CONTRIBUTING.md) are the fastest way to grow it.

---

## Where it works today

Everything here was run by hand, in a real browser, against a real key. Everything
else is either covered by automated tests or by nothing at all, and
[COMPATIBILITY.md](COMPATIBILITY.md) marks every row with the evidence behind it.

**Sites**

| Site | Status |
|---|---|
| Gmail · Telegram Web · Outlook / Hotmail · Tuta · X / Twitter · Reddit | **Verified** — 2026-08-02 to 2026-09-02 |
| Infomaniak Mail · iCloud Mail | **Verified** — 2026-09-14, published build; the editor sits inside a cross-origin frame, so ProofKey offers that one extra origin when the cursor lands there: Allow in its toast, then the browser's own prompt |
| WhatsApp Web | **Verified** — 2026-09-10, published build, live checking and quick actions; the 2026-09-04 "Broken" reading was taken with the site switched off |
| Slack · Notion · Discord · LinkedIn · GitHub | *Untested* — same code path as a verified one, but nobody has run it |
| Google Docs | **Not supported** — text is painted to a canvas, so there is nothing to underline |

**Providers**

| Provider | Status |
|---|---|
| Google Gemini · xAI (Grok) · OpenRouter · llama.cpp (self-hosted) | **Verified** against real keys |
| OpenCode Go | **Verified since 0.1.15**, with `gpt-6-luna` through the extension against Go's own endpoint — since about 2026-09-17 Go refuses requests without a session header and its `gpt-*` models answer only the Responses API, so **0.1.14 and earlier cannot reach it**; see [MODELS.md](MODELS.md#if-you-are-on-opencode) |
| Chrome's built-in model (Gemini Nano, no key) | **Verified** — 2026-09-13, Chrome 153 on one laptop, through the real service worker. Live checking and Fix grammar only; [why](#no-api-key-at-all-chromes-built-in-model) |
| The other 31 presets | *Prefilled, not confirmed* — the base URL is filled in for you, that is all it means |

Untested does not mean broken: most of these share a code path with something
verified. It means nobody has checked, and this project would rather say so.

## Why

Grammarly and LanguageTool are excellent, and both route your writing through their servers. ProofKey keeps the interaction model — inline underlines, a suggestion card, quick rewrite actions — and swaps the engine for an endpoint you control. Point it at a model running on your own machine and nothing leaves it at all.

## Features

- **Quick actions** on any selected text, from the right-click menu or `Ctrl+Shift+K`: fix grammar, improve writing, make professional, make friendly, simplify, summarize, expand, convert to bullet points, and translate. Translate uses the first language your profile names — its own field, then the one you asked for explanations in, then your first language — so it usually works without being configured, and says which setting is missing rather than guessing when none of them is set.
- **Editable prompts.** Every built-in action is a prompt you can rewrite, and you can add your own.
- **A key per action.** Any action, including one you wrote, can be given its own shortcut in the options page — press the combination, and it is recorded. These are handled inside the page rather than by Chrome's shortcut system, which is limited to four keys fixed at build time and can only be changed from `chrome://extensions/shortcuts`. The trade is that ProofKey has to be loaded in a page to see a keypress there, so these keys run on the sites you list and nowhere else. The right-click menu works everywhere with no site permission, and `Ctrl+Shift+K` does too — [when Chrome actually assigned it](#ctrlshiftk-does-nothing).
- **Live checking is quieter than the quick actions, on purpose.** It fires on a pause you did not ask for, so it treats messaging conventions as valid: no full stop added to a line that lacks one, no capitalising a lowercase sentence start, no expanding slang. `Ctrl+Shift+K` you pressed deliberately, so it completes the correction, capitals included.
- **Chrome's built-in model, with nothing to set up.** In Google Chrome the first connection is Chrome's own on-device model: no key, no account, and ProofKey sends your text nowhere — Chrome runs the check on the com