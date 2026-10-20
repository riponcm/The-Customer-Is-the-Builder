# PDFLokal

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ojanlubis/pdflokal)](https://github.com/ojanlubis/pdflokal/stargazers)
[![Client-Side Only](https://img.shields.io/badge/Privacy-100%25%20Client--Side-brightgreen.svg)](https://www.pdflokal.id/privasi.html)
[![Security Headers](https://img.shields.io/badge/Security-Headers%20Enabled-green.svg)](https://www.pdflokal.id/.well-known/security.txt)
[![AI Contributions Welcome](https://img.shields.io/badge/AI-Contributions%20Welcome-blueviolet.svg)](CONTRIBUTING.md)

> **Urus dokumen langsung di browser.** Cepat, gratis, file tidak pernah diupload.

PDFLokal adalah tool PDF gratis untuk pengguna Indonesia. Semua proses berjalan di browser - file tidak pernah meninggalkan perangkatmu.

**[Buka PDFLokal](https://www.pdflokal.id/)**

## Fitur

### PDF Tools
- **Editor PDF** — Unified editor with whiteout, text (9 fonts, bold/italic, color), signatures (upload with background removal, draw, place → Konfirmasi to lock, double-click to unlock), paraf/initials, watermark, page numbers, password protection
- **Edit teks asli** (beta) — edit the text already printed in the PDF, in place, in the document's own font
- **Kelola Halaman** — reorder, rotate, delete, and split pages
- **Tema gelap / terang** — Theme toggle stored per-device
- **Gabung PDF** — Merge multiple PDFs and images with drag-drop reordering
- **Split PDF** — Extract selected pages as a separate PDF
- **Kompres PDF** — Reduce file size by compressing embedded images
- **PDF ke Gambar** — Export pages as PNG/JPG with batch download
- **Proteksi PDF** — Add password protection

### Image Tools
- **Kompres Gambar** — Reduce file size with quality control
- **Ubah Ukuran** — Resize with locked aspect ratio
- **Convert Format** — JPG, PNG, WebP
- **Gambar ke PDF** — Combine images into a single PDF
- **Hapus Background** — Remove white backgrounds for transparent PNG

## Privasi

- **100% Client-side** — All file processing happens in the browser
- **No uploads** — The PDFs and images you work on are never uploaded
- **Open source** — Code can be inspected by anyone
- **Security headers** — CSP, X-Frame-Options, and more ([details](docs/security.md))

What does leave the browser, stated plainly:

- Anonymous, typed usage events (which tool, how long an export took, device class) to PDFLokal's
  own endpoint, with a random per-browser visitor id. The schema has no field that could carry file
  contents.
- Page views and the same kind of tool events to Vercel Web Analytics, Google Analytics, Google Ads
  and Mixpanel. Google Analytics and Google Ads set cookies.
- Session replay: Sentry (1 in 10 sessions, plus any session with an error) and Mixpanel (every
  session, ongoing). Text is masked and document pages are blocked from the recording.
- Sentry error reports, whose messages can quote a single character of text you typed.
- Only what you choose to send as feedback: a typed note, a pasted screenshot, or, after a 👎 in the
  Edit beta, a crop of one edited line that you see before tapping Kirim.

Full detail in [privasi.html](privasi.html).

## Cara Pakai

1. Buka [pdflokal.id](https://www.pdflokal.id/)
2. Pilih tool yang dibutuhkan atau drag & drop file PDF
3. Proses dan download hasilnya

Tidak perlu install, tidak perlu daftar, tidak perlu bayar.

## Development

### Run Locally
```bash
git clone https://github.com/ojanlubis/pdflokal
cd pdflokal
npx serve .
# Open http://localhost:3000
# Always hard refresh (Ctrl+Shift+R) after changes — npx serve caches aggressively
```

### Tech Stack
- **Vanilla JS** — Native ES modules, no build step, no framework
- **Zero CDN** — every library below is self-hosted; the app runs fully offline
- **[pdf-lib](https://pdf-lib.js.org/)** — PDF manipulation (self-hosted)
- **[PDF.js](https://mozilla.github.io/pdf.js/)** — PDF rendering with Web Worker (self-hosted)
- **[Signature Pad](https://github.com/szimek/signature_pad)** — Digital signatures (self-hosted)
- **[fontkit](https://github.com/foliojs/fontkit)** — Reads a PDF's own embedded font program (glyph coverage, weight, PANOSE) and embeds fonts into exports (self-hosted)
- **[pdf-encrypt-lite](https://github.com/nicholasohjj/pdf-encrypt-lite)** — PDF password encryption (self-hosted)
- **Canvas API** — Image processing
- **Self-hosted fonts** — UI font Plus Jakarta Sans + annotation fonts Montserrat, Carlito, and the metric-compatible Croscore set (Arimo/Tinos/Cousine/Caladea — stand-ins for Arial/Times/Courier/Cambria when a document's own font can't be reused)

## Kontribusi

Contributions are welcome from humans and AI assistants! See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

Quick summary:
1. **Report bugs** — use the [bug report template](https://github.com/ojanlubis/pdflokal/issues/new?template=bug_report.yml)
2. **Request features** — use the [feature request template](https://github.com/ojanlubis/pdflokal/issues/new?template=feature_request.yml)
3. **Submit PRs** — fork, branch, follow [CONTRIBUTING.md](CONTRIBUTING.md), submit

### For AI Contributors

Point your AI assistant to `CLAUDE.md` — it contains everything needed to understand the codebase: architecture, patterns, helpers, gotchas, and conventions. The issue templates are structured (YAML forms) for easy parsing.

## Field Notes

Some of the real bugs in this repo's history are written up as field notes: the commit, the investigation, and the lesson behind it. If you want the story behind a fix, not just the diff:

- [When AI-Built Software Breaks](https://mesindev.com/notes) — field notes on cleaning up AI-generated code, drawn from this repo's git history
- [The tool that passed every test and was quietly broken](https://mesindev.com/notes/ai-code-passed-every-test) — the Ganti File blank-render bug: the guess ([bb7470e](https://github.com/ojanlubis/pdflokal/commit/bb7470e)) logged, then confirmed weeks later ([