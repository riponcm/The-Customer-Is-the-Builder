<p align="center">
  <a href="https://getartcraft.com/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="docs/brand/artcraft-logo-white.svg">
      <img alt="ArtCraft" src="docs/brand/artcraft-logo.svg" width="200">
    </picture>
  </a>
</p>


<h1 align="center">PdfCraft</h1>

<p align="center">
  <b>The PDF workbench; an open-source, clean-room reimplementation of Adobe Acrobat, rebuilt in pure Rust.</b><br>
  Read, organize, combine, split and secure PDFs in a fast, native app, written in Rust from the ground up.<br>
  macOS · Windows · Linux · FreeBSD · the web
</p>

<p align="center">
  <img alt="License: MIT OR Apache-2.0" src="https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-12a58a">
  <img alt="Written in Rust" src="https://img.shields.io/badge/written%20in-Rust-0a7563">
  <img alt="Platforms: macOS, Windows, Linux, FreeBSD, web" src="https://img.shields.io/badge/runs%20on-macOS%20%C2%B7%20Windows%20%C2%B7%20Linux%20%C2%B7%20FreeBSD%20%C2%B7%20web-12a58a">
  <img alt="No account, no telemetry" src="https://img.shields.io/badge/no%20account-no%20telemetry-0a7563">
</p>

<p align="center">
  <a href="https://discord.gg/artcraft"><img alt="Join the ArtCraft community on Discord" src="https://img.shields.io/badge/Join%20us%20on%20Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" height="40"></a>
</p>

<p align="center">
  <a href="https://getartcraft.com/apps/pdfcraft"><b>PdfCraft on getartcraft.com</b></a> ·
  <a href="https://getartcraft.com/">ArtCraft</a> ·
  <a href="https://getartcraft.com/apps">All Crafting Apps</a>
</p>

<br>

<p align="center">
  <img src="docs/images/pdfcraft-viewer.png" alt="PdfCraft with the PdfCraft Showcase cover page open, the All tools panel on the left and 20 threaded comments on the right" width="100%">
  <br>
  <sub>The PdfCraft Showcase, a 13-page specimen PDF, open with the All tools panel and threaded comments.</sub>
</p>

> [!NOTE]
> **ArtCraft is a community of artists from all walks of life.** Digital, generative, music,
> games &mdash; if you make things, you're one of us. **[Come say hi on Discord](https://discord.gg/artcraft).**

<p align="center">
  <a href="#highlights">Highlights</a> ·
  <a href="#read-anything-beautifully">Read</a> ·
  <a href="#find-it-select-it-copy-it">Find</a> ·
  <a href="#organize-pages-like-cards-on-a-table">Organize</a> ·
  <a href="#combine-and-split-without-losing-a-thing">Combine &amp; split</a> ·
  <a href="#open-protected-documents-and-respect-their-rules">Protect</a> ·
  <a href="#comments-forms-layers-and-attachments">Forms &amp; layers</a> ·
  <a href="#runs-everywhere-stays-yours">Everywhere</a> ·
  <a href="#built-for-agents-too">Agents</a> ·
  <a href="#how-its-built">How it's built</a> ·
  <a href="#get-started">Get started</a> ·
  <a href="#whats-next">What's next</a> ·
  <a href="#downloads">Downloads</a> ·
  <a href="#the-crafting-apps">Crafting Apps</a>
</p>

---

## Community

PdfCraft is part of [ArtCraft](https://getartcraft.com). Come say hello, get help and follow development:

- **Discord: [discord.gg/artcraft](https://discord.gg/artcraft)**. This is the fastest way to get help and share feedback. The app has a Discord button in its title bar.
- **Web page:** [getartcraft.com/apps/pdfcraft](https://getartcraft.com/apps/pdfcraft)
- **Source:** [github.com/storytold/pdfcraft](https://github.com/storytold/pdfcraft)

The ArtCraft name and logos in `docs/brand/` are trademarks of the ArtCraft Team and are not open source. They may be used only unmodified, and only as part of PdfCraft (see `docs/brand/LICENSE-brand.txt`). Forks and modified versions must remove them.

## Highlights

<table>
<tr>
<td width="33%" valign="top">

### Faithful
Real-world typography: world scripts, vertical Japanese, colour emoji, gradients, soft masks and transparency. All of it renders the way the author intended.

</td>
<td width="33%" valign="top">

### Fearless
Every save appends your changes and leaves the original bytes untouched. Writes are atomic, undo runs deep, and nothing is lost if you close by mistake.

</td>
<td width="33%" valign="top">

### Yours
No account, no telemetry, no cloud. It works offline and opens instantly. The engine, CLI and app are all open source.

</td>
</tr>
</table>

---

## Read anything, beautifully

PdfCraft renders PDFs with care for the details that make a page feel right: kerning and ligatures, right-to-left and complex scripts, vertical CJK, colour emoji, shadings, blend modes, soft masks and optional content.

<p align="center">
  <img src="docs/images/pdfcraft-scripts.png" alt="The Scripts of the World page: Arabic, Hebrew, Devanagari, Thai, Greek, Cyrillic, Chinese, Korean, IPA, Armenian, Georgian and Tamil samples, with vertical Japanese in the right margin" width="100%">
  <br>
  <sub>Twelve writing systems on one page, plus vertical Japanese, at 125%.</sub>
</p>

- **Deep zoom stays sharp.** Large pages render in tiles, so text stays crisp at any magnification.
- **Built to survive bad files.** Every page renders in isolation and damaged documents are repaired. Across the 983-file pdf.js test corpus the result is 0 crashes.
- **Layouts for every task:** continuous, single page, two-up, view rotation, full screen and a distraction-free Read mode.
- **Light and dark themes**, both designed to be easy on the eyes for long sessions.

<table>
<tr>
<td width="50%"><img src="docs/images/pdfcraft-twoup.png" alt="Two facing pages in Read mode with the dark theme: the Foreword and the Setting Text chapter with its drop cap and pull quote"></td>
<td width="50%"><img src="docs/images/pdfcraft-dark.png" alt="The dark theme showing the Code and Images chapter, a syntax-coloured listing and a fractal image, with the comments panel open"></td>
</tr>
<tr>
<td align="center"><sub>Two-up Read mode, ready for long reading</sub></td>
<td align="center"><sub>The dark theme, with the comments panel open</sub></td>
</tr>
</table>

## Find it, s