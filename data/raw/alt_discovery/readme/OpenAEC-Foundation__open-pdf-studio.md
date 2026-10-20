<p align="center">
  <img src="open-pdf-studio/src-tauri/icons/icon.png" alt="Open PDF Studio" width="128" height="128">
</p>

<h1 align="center">Open PDF Studio</h1>

<p align="center">
  <strong>A free, open-source PDF editor and annotator for Windows, macOS, Linux, and Android.</strong>
</p>

<p align="center">
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/releases/latest"><img src="https://img.shields.io/github/v/release/OpenAEC-Foundation/open-pdf-studio?style=flat-square" alt="Latest Release"></a>
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/license-LGPL--3.0-blue?style=flat-square" alt="License"></a>
  <a href="https://snapcraft.io/open-pdf-studio"><img src="https://img.shields.io/badge/snap-open--pdf--studio-green?style=flat-square&logo=snapcraft" alt="Snap Store"></a>
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/releases"><img src="https://img.shields.io/github/downloads/OpenAEC-Foundation/open-pdf-studio/total?style=flat-square" alt="Total downloads"></a>
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/commits"><img src="https://img.shields.io/github/commit-activity/m/OpenAEC-Foundation/open-pdf-studio?style=flat-square" alt="Commit activity"></a>
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/commits"><img src="https://img.shields.io/github/last-commit/OpenAEC-Foundation/open-pdf-studio?style=flat-square" alt="Last commit"></a>
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/stargazers"><img src="https://img.shields.io/github/stars/OpenAEC-Foundation/open-pdf-studio?style=flat-square" alt="Stars"></a>
</p>

---

Open PDF Studio is a lightweight, native desktop application that provides professional-grade PDF annotation, markup, and editing tools without subscriptions, telemetry, or bloatware. Built with [Tauri 2](https://tauri.app/) and web technologies, it delivers a fast, modern experience with a Microsoft Office-style ribbon interface.

It is built for people who work with drawings: import DWG and DXF as a vector PDF with layers and a measuring scale, measure and take off quantities, export a page back to CAD, verify digital signatures, make scans searchable with OCR, and let an AI assistant operate the app through a local connection.

<p align="center">
  <img src="docs/screenshots/pdf-compare.jpg" alt="Open PDF Studio – side-by-side PDF compare with change list" width="100%">
</p>

<p align="center">
  <img src="docs/screenshots/drawing-tools.jpg" alt="CAD-style drawing, measurement, and markup tools on an architectural elevation" width="100%">
</p>

<p align="center">
  <img src="docs/screenshots/plattegrond-demo.gif" alt="Drawing a floor plan with parametric walls: corners trim themselves, doors, windows and rooms snap into place" width="640">
  <br><sub>Parametric walls with self-trimming corners, doors, windows and rooms — drawn to scale on a blank sheet.</sub>
</p>

## Repository activity

Downloads, commit activity, and star growth for this active open-source project.

<p align="center">
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/releases"><img src="https://img.shields.io/github/downloads/OpenAEC-Foundation/open-pdf-studio/total?style=for-the-badge&label=Total%20downloads&color=2563eb" alt="Total downloads"></a>
  &nbsp;
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/releases/latest"><img src="https://img.shields.io/github/downloads/OpenAEC-Foundation/open-pdf-studio/latest/total?style=for-the-badge&label=Latest%20release&color=059669" alt="Latest release downloads"></a>
  &nbsp;
  <a href="https://github.com/OpenAEC-Foundation/open-pdf-studio/commits"><img src="https://img.shields.io/github/commit-activity/m/OpenAEC-Foundation/open-pdf-studio?style=for-the-badge&label=Commits%2Fmonth&color=7c3aed" alt="Commits per month"></a>
</p>

**Star history**

<p align="center">
  <a href="https://www.star-history.com/?repos=openaec-foundation%2Fopen-pdf-studio&type=date&legend=top-left">
    <img src="https://api.star-history.com/svg?repos=openaec-foundation%2Fopen-pdf-studio&type=date&legend=top-left" alt="Star History Chart" width="100%">
  </a>
</p>

<!-- Commit & contributor activity chart: register this repo once at
     https://repobeats.axiom.co, then paste the generated embed here for a
     live commit-history graph:
     ![Activity](https://repobeats.axiom.co/api/embed/<hash>.svg) -->

## Why Open PDF Studio?

Professional annotation, markup, measurement, redaction and page management — the tools that typical commercial PDF editors lock behind a subscription or a paid tier — are all included, free and fully open source. No subscriptions, no telemetry, no watermarks.

| | Open PDF Studio | Typical commercial PDF editors |
|---|:---:|:---:|
| **Price** | Free & open source (LGPL-3.0) | Subscription or paid license |
| **Annotations & markup** | All included | Often a paid tier |
| **Measurement tools** | Included | Usually paid |
| **DWG/DXF import & export** | Included | Rare, or a separate product |
| **OCR** | Included | Often a paid tier |
| **AI connection (MCP)** | Included, local and optional | Cloud service, if any |
| **Stamps, watermarks & redaction** | Included | Usually paid |
| **Page management** | Included | Usually paid |
| **Multi-tab editing** | Included | Varies |
| **Telemetry** | None | Common |
| **Platforms** | Windows, macOS, Linux, Android | Varies (often fewer) |

## Features

### Annotations & Markup (20+ Tools)
- **Text markup:** Highlight, underline, strikethrough
- **Shapes:** Rectangle, ellipse, polygon, cloud, cloud polyline, line, arrow, polyline
- **Hatch fill patterns:** Cross-hatch, diagonal, dots, and more for shape fills
- **Freehand drawing:** Pen tool with configurable color, width, and opacity
- **Text annotations:** Text box, callout with leader line, sticky notes with popup editing
- **Stamps:** 10 built-in stamps (Approved, Rejected, Draft, Confidential, Final, etc.)
- **Images: