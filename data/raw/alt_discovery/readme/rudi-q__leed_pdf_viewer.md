<div align="center">
  <img src="static/logo.png" alt="LeedPDF Logo" width="160" height="160">
  
  # LeedPDF - Free PDF Annotation Tool
  
  **Add drawings and notes to any PDF.**
  
  *Works with mouse, touch, or stylus - completely free and private.*
</div>
<br>

<div align="center">

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-87A96B.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Commercial License](https://img.shields.io/badge/Commercial%20License-Available-87A96B.svg)](https://buy.polar.sh/polar_cl_tPmQ3d72uYwrYvzzIUM4R7cku7hg2kmEQqruI1its5c)
[![Free for Personal Use on Web](https://img.shields.io/badge/Free-Web%20App-87A96B.svg)](#web-app-agpl)
[![GitHub Stars](https://img.shields.io/github/stars/rudi-q/leed_pdf_viewer?color=87A96B&style=flat&logo=github)](https://github.com/rudi-q/leed_pdf_viewer/stargazers)
[![Downloads](https://img.shields.io/github/downloads/rudi-q/leed_pdf_viewer/total?label=Downloads&logo=github&color=87A96B)](https://github.com/rudi-q/leed_pdf_viewer/releases)
[![WCAG AAA Compliant](https://img.shields.io/badge/WCAG%20AAA-Compliant-87A96B?style=flat&logo=accessibilityalt&logoColor=white)](https://www.w3.org/WAI/WCAG2AAA-Conformance)

[![SvelteKit](https://img.shields.io/badge/SvelteKit-FF3E00?style=flat&logo=svelte&logoColor=white)](https://kit.svelte.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tauri](https://img.shields.io/badge/Tauri-24C8D8?style=flat&logo=tauri&logoColor=white)](https://tauri.app/)
[![PDF.js](https://img.shields.io/badge/PDF.js-000000?style=flat&logo=mozilla&logoColor=white)](https://mozilla.github.io/pdf.js/)
[![Brave Search API](https://img.shields.io/badge/Brave%20Search-FB542B?style=flat&logo=brave&logoColor=white)](https://api.search.brave.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![CodeRabbit](https://img.shields.io/badge/CodeRabbit-FF570A?style=flat&logo=coderabbit&logoColor=white)](https://coderabbit.ai/)
[![Appwrite](https://img.shields.io/badge/Appwrite-F02E65?style=flat&logo=appwrite&logoColor=white)](https://appwrite.io/)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)

</div>

**A modern, open-source PDF annotation tool that runs entirely in your browser**

Transform any PDF into an interactive canvas. Draw, annotate, and collaborate without uploading your documents to external servers.

<div align="center">
  <img src="static/screenshot.png" alt="LeedPDF in action - annotating a Y Combinator fundraising guide with highlights, comments, and drawings" width="800" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);">
</div>

[**Try it now →**](https://leed.my) | [**Report Issues**](https://github.com/rudi-q/leed_pdf_viewer/issues) | [**Contribute**](https://github.com/rudi-q/leed_pdf_viewer/blob/main/CONTRIBUTING.md)

## ✨ Features

### 🔍 **PDF Search & Discovery**
- **Web-wide PDF search** powered by Brave Search API
- **Direct PDF opening** from search results
- **Smart filtering** for PDF documents only
- **Pagination** through search results
- **Real-time search** with instant results
- **Setup guide**: See [docs/SEARCH_FEATURE.md](docs/SEARCH_FEATURE.md) for configuration

### 🎨 **Drawing & Annotation**
- **Freehand drawing** with customizable pencil and highlighter tools
- **Shape tools** including rectangles, circles, arrows, and stars
- **Text annotations** with inline editing
- **Sticky notes** for quick comments
- **Smart eraser** that removes intersecting elements

### 📱 **Universal Access**
- Works on **any device** - desktop, tablet, or phone
- **Touch-optimized** with Apple Pencil support
- **Mobile-friendly** interface that works seamlessly on smartphones and tablets
- **No installation required** - runs in your browser
- **Fast loading** with optimized caching

### ♿ **Accessibility First**
- **WCAG AAA compliant** - exceeds accessibility standards with 7.06:1 contrast ratios
- **Keyboard navigation** - full functionality without a mouse
- **Screen reader friendly** - semantic HTML and proper ARIA labels
- **High contrast mode** support for visually impaired users
- **Scalable interface** - works with browser zoom up to 200%
- **Color blind friendly** - doesn't rely solely on color for information
- **Focus indicators** - clear visual focus states for all interactive elements

### 🔒 **Privacy First**
- **100% client-side** - your PDFs never leave your device
- **No account required** - start annotating immediately
- **Local auto-save** - your work is preserved automatically

### ⚡ **Performance**
- **Instant loading** from URLs (including Dropbox links)
- **High-DPI rendering** for crisp display on all screens
- **Infinite canvas** - pan and zoom without limits
- **Full undo/redo** with keyboard shortcuts

## 🚀 Quick Start

### Option 1: Use Online
Visit [leed.my](https://leed.my) and start annotating immediately.

### Option 2: Load from URL
Share annotated PDFs by adding `/pdf/` to any URL:
```
https://leed.my/pdf/https://example.com/document.pdf
```

### Option 3: Run Locally
```bash
git clone https://github.com/rudi-q/leed_pdf_viewer.git
cd leed_pdf_viewer
pnpm install
pnpm build && pnpm preview

# Or just use the shorthand:
pnpm prev
```

Open `http://localhost:4173` in your browser.

## 🛠️ Tech Stack

- **Framework**: SvelteKit + TypeScript
- **PDF Rendering**: PDF.js
- **Drawing Engine**: HTML5 Canvas
- **Styling**: Tailwind CSS
- **Build**: Vite

## 📖 Usage

### Basic Controls
- **Upload**: Drag & drop a PDF or click the folder icon
- **Draw**: Select the pencil tool and start drawing
- **Navigate**: Use arrow keys or toolbar buttons
- **Zoom**: Ctrl + scroll wheel or toolbar bu