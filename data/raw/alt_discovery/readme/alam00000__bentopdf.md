<p align="center"><img src="public/images/favicon-no-bg.svg" width="80"></p>
<h1 align="center">BentoPDF</h1>
<p align="center"><sub>Supported by</sub></p>
<p align="center">
  <a href="https://vercel.com/open-source-program">
    <img alt="Vercel OSS Program" src="https://vercel.com/oss/program-badge-2026.svg" height="30" />
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://www.digitalocean.com/?refcode=d93c189ef6d0&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge">
    <img src="https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%203.svg" alt="DigitalOcean Referral Badge" height="44">
  </a>
</p>

**BentoPDF** is a powerful, privacy-first, client-side PDF toolkit that is self-hostable and allows you to manipulate, edit, merge, and process PDF files directly in your browser. No server-side processing is required, ensuring your files remain secure and private.

[![Docker Downloads](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Falam00000%2Fbentopdf%2Fbadges%2Fdocker-downloads.json&cacheSeconds=3600)](https://github.com/alam00000/bentopdf/pkgs/container/bentopdf-simple) [![Ko-fi](https://img.shields.io/badge/Buy%20me%20a%20Coffee-yellow?logo=kofi&style=flat-square)](https://ko-fi.com/alio01) ![GitHub Stars](https://img.shields.io/github/stars/alam00000/bentopdf?style=social)
[![Sponsor me on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ff69b4)](https://github.com/sponsors/alam00000)

![BentoPDF Tools](public/images/bentopdf-tools.png)

---

## Table of Contents

- [Join Us on Discord](#-join-us-on-discord)
- [Documentation](#-documentation)
- [Licensing](#-licensing)
- [Stargazers over time](#-stargazers-over-time)
- [Thank You to Our Sponsors](#-thank-you-to-our-sponsors)
- [Why BentoPDF?](#-why-bentopdf)
- [Features / Tools Supported](#️-features--tools-supported)
  - [Organize & Manage PDFs](#organize--manage-pdfs)
  - [Edit & Modify PDFs](#edit--modify-pdfs)
  - [Convert to PDF](#convert-to-pdf)
  - [Convert from PDF](#convert-from-pdf)
  - [Secure & Optimize PDFs](#secure--optimize-pdfs)
- [Other Products](#-other-products)
- [Translations](#-translations)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#-quick-start)
  - [Static Hosting](#static-hosting-using-netlify-vercel-and-github-pages)
  - [Self-Hosting Locally](#-self-hosting-locally)
  - [Docker Compose / Podman Compose](#-run-with-docker-compose--podman-compose-recommended)
  - [Podman Quadlet](#-podman-quadlet-systemd-integration)
  - [Self-Hosted Build (Simple Mode)](#-self-hosted-build-simple-mode)
  - [Commercial Build](#-commercial-build)
  - [Custom Branding](#-custom-branding)
  - [Disabling Specific Tools](#-disabling-specific-tools)
  - [Disabling the GitHub Star Counter](#-disabling-the-github-star-counter)
  - [WASM Configuration](#wasm-configuration)
  - [Air-Gapped / Offline Deployment](#air-gapped--offline-deployment)
  - [Security Features](#-security-features)
  - [Digital Signature CORS Proxy](#digital-signature-cors-proxy-required)
  - [Version Management](#-version-management)
  - [Development Setup](#-development-setup)
- [Tech Stack & Background](#️-tech-stack--background)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [Special Thanks](#special-thanks)

---

## 📢 Join Us on Discord

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-7289da?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/Bgq3Ay3f2w)

Have questions, feature requests, or want to chat with the community? Join our Discord server!

---

## 📚 Documentation

[![Documentation](https://img.shields.io/badge/Docs-VitePress-646cff?style=for-the-badge&logo=vite&logoColor=white)](https://bentopdf.com/docs/)

Visit our [Documentation](https://bentopdf.com/docs/) for:

- **Getting Started** guide
- **Tools Reference** (50+ tools)
- **Self-Hosting** guides (Docker, Vercel, Netlify, Cloudflare, AWS, Hostinger, Nginx, Apache)
- **Contributing** guide
- **Commercial License** details

---

## 📜 Licensing

BentoPDF is **dual-licensed** to fit your needs:

| License        | Best For                                     | Price              |
| -------------- | -------------------------------------------- | ------------------ |
| **AGPL-3.0**   | Open-source projects with public source code | **Free**           |
| **Commercial** | Proprietary / closed-source applications     | **$79** (lifetime) |

<p align="center">
  <a href="https://buy.polar.sh/polar_cl_ThDfffbl733x7oAodcIryCzhlO57ZtcWPq6HJ1qMChd">
    <img src="https://img.shields.io/badge/🚀_Get_Commercial_License-$79_Lifetime-6366f1?style=for-the-badge&labelColor=1f2937" alt="Get Commercial License">
  </a>
</p>

> **One-time purchase** · **Unlimited devices & users** · **Lifetime updates** · **No AGPL obligations**

📖 For more details, see our [Licensing Page](https://bentopdf.com/licensing.html)

### AGPL Components (Pre-configured via CDN)

BentoPDF does **not** bundle AGPL-licensed processing libraries in its source code, but **pre-configures CDN URLs** so all features work out of the box with zero setup:

| Component              | License  | Features Enabled                                                                                    |
| ---------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| **PyMuPDF**            | AGPL-3.0 | PDF to Text/Markdown/SVG/DOCX, Extract Images/Tables, EPUB/MOBI/XPS conversion, Compression, Deskew |
| **Ghostscript**        | AGPL-3.0 | PDF/A Conversion, Font to Outline                                                                   |
| **CoherentPDF (CPDF)** | AGPL-3.0 | Merge, Split by Bookmarks, Table of Contents, PDF to/from JSON, Attachments                         |

> [!TIP]
> **Zero-config by default.** WASM modules are loaded at runtime from jsDelivr CDN. No manual configuration is needed. For custom