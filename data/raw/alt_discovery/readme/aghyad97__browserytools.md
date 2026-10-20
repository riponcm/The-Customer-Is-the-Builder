<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://browserytools.com/icon-dark.svg">
    <img src="https://browserytools.com/icon.svg" alt="" height="30">
  </picture>&nbsp;BrowseryTools
</h1>

<p align="center">
  <a href="https://browserytools.com"><img src="https://img.shields.io/website?url=https%3A%2F%2Fbrowserytools.com&label=browserytools.com&style=flat-square" alt="Live site" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/aghyad97/browserytools?style=flat-square&color=blue" alt="License" /></a>
  <a href="https://github.com/aghyad97/browserytools/stargazers"><img src="https://img.shields.io/github/stars/aghyad97/browserytools?style=flat-square" alt="Stars" /></a>
  <a href="https://github.com/aghyad97/browserytools/network/members"><img src="https://img.shields.io/github/forks/aghyad97/browserytools?style=flat-square" alt="Forks" /></a>
  <a href="https://github.com/aghyad97/browserytools/issues"><img src="https://img.shields.io/github/issues/aghyad97/browserytools?style=flat-square" alt="Open issues" /></a>
  <a href="#-contributing"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs welcome" /></a>
  <img src="https://img.shields.io/github/last-commit/aghyad97/browserytools?style=flat-square" alt="Last commit" />
  <img src="https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js" alt="Built with Next.js 15" />
</p>

![BrowseryTools](https://github.com/aghyad97/browserytools/blob/main/public/og-image.png?raw=true)

A comprehensive collection of **152 browser-based tools** built with Next.js, TypeScript, and Tailwind CSS. Your files and text are processed in your browser — no uploads, no accounts required. Includes on-device AI tools (transcription, translation, summarization, image upscaling, and more) powered by Transformers.js.

**Free, no accounts, no ads, no tracking.** If it saves you time, [star the repo](https://github.com/aghyad97/browserytools/stargazers). That is the fastest way to help other people find it.

Two caveats worth stating plainly, since "everything is local" is the headline claim:

- Tools that run an AI model download the model weights from a third-party CDN the first time you use them. Your content still stays on your device; the model files come over the network.
- Two tools genuinely need the network. **Live Dictation** uses the browser's Web Speech API, which in Chrome and Edge sends your audio to the browser vendor for recognition — don't use it for anything confidential. **Currency Converter** fetches exchange rates from an external API.

## 📚 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Supported Languages](#-supported-languages)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Running Tests](#-running-tests)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [Contributors](#-contributors)
- [Activity](#-activity)
- [Reporting Issues](#-reporting-issues)
- [Supporting the Project](#-supporting-the-project)
- [Star History](#-star-history)
- [License](#-license)
- [Contact](#-contact)

## 🚀 Features

### 🖼️ Image Tools

- **Background Removal**: Remove background from your images instantly using AI.
- **Phone Mockups**: Place screenshots into iPhone/Android device frames.
- **Image Compression**: Compress images to reduce file size while maintaining quality.
- **Format Converter**: Convert images between different formats like JPG, PNG, WebP, GIF, BMP, TIFF, and SVG.
- **Color Correction**: Adjust colors, brightness, contrast, saturation, and hue in images.
- **SVG Tools**: Edit and manipulate SVG vector graphics.
- **SVG to PNG**: Convert SVG vector files to PNG images.
- **Photo Censor**: Redact sensitive parts of an image with blur, pixelate, or black-box censoring.
- **Screenshot Beautifier**: Turn plain screenshots into beautiful images.
- **Meme Generator**: Make a meme online for free.
- **Photo Collage**: Combine multiple photos into a collage with grid, strip, and mosaic layouts.
- **EXIF Remover**: Strip EXIF metadata - GPS location, camera model, timestamps - from photos before sharing.
- **ASCII Art Generator**: Convert any image into ASCII art in your browser.
- **Image Upscaler**: Upscale and enhance images 2x with an on-device AI super-resolution model.
- **Image Captioner**: Generate a descriptive caption and ready-to-use alt text for any image with an on-device AI model.
- **Depth Map Generator**: Generate a depth map from any image with an on-device AI model.
- **Object Cutout**: Cut out any object from an image with one click using the Segment Anything (SAM) AI model in your browser.
- **Image Resizer**: Resize images to exact dimensions or by percentage.
- **EXIF Viewer**: View EXIF metadata from photos: camera model, lens, aperture, shutter speed, ISO, GPS coordinates, and more.
- **Favicon Generator**: Create a complete favicon set from an image or a letter/emoji.
- **Crop Image**: Crop images online with aspect-ratio presets and precise drag handles.
- **Watermark Image**: Add text or logo watermarks to photos — position, opacity, rotation, and tiling.

### 🤖 AI Tools

- **Token Counter**: Count tokens for any text across popular AI models: GPT-4o, Claude, Llama 3, and more.
- **Context Window Calculator**: Calculate how much of a model's context window your text uses.
- **AI Cost Calculator**: Estimate your AI API costs by entering token counts and selecting a model.
- **Model Comparison**: Compare AI language models side by side: context window size, pricing, capabilities, speed, and provider.
- **System Prompt Builder**: Build structured system prompts for AI models using a guided form.
- **Prompt Library**: Save, organize, and search your AI prompts locally in the browser.
- **CLAUDE.md Generator**: Generate CLAUDE.md files for your projects using a structured form.
- **AI Rules Generator**: Generate 