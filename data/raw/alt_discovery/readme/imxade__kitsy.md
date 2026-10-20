# Kitsy

Kitsy is a local-first toolbox for everyday file, media, document, recorder, and todo workflows. It runs as an offline-capable PWA, keeps file processing on the user's device, and uses a small backend session only for optional Google Drive authorization and upload proxying.

Optional Google Drive support lets users sync the todo list into their own hidden Drive app data and save processed outputs into their own Drive. The app still works local-only when Drive is disconnected, unconfigured, or unavailable.

Useful if you want an offline-friendly alternative to TinyWow, 123apps, Smallpdf, iLovePDF, and similar browser tool services.

> Please consider leaving a star.

---

## Architecture

### Component Overview

```mermaid
flowchart TD
    UI["UI Layer<br/>(React 19 + DaisyUI 5 + Tabler icons)"] --> Router["Routing Layer<br/>(TanStack Start / React Router)"]
    Router --> HomeRoute["/ Route"]
    Router --> ToolRoute["/tool/$id Route"]
    HomeRoute --> SearchRank["search.ts<br/>(intent-aware ranking)"]
    ToolRoute --> Registry["tool-registry.ts<br/>(63 registered tools)"]
    Registry --> Processors["Processor Functions"]
    Processors --> ImgProc["image-processor.ts<br/>(OffscreenCanvas + imagetracerjs + IMG.LY background removal)"]
    Processors --> PdfProc["pdf-processor.ts<br/>(pdf-lib + pdfjs-dist + qpdf-wasm + signing libs)"]
    Processors --> FileProc["file-processor.ts<br/>(fflate + papaparse)"]
    Processors --> FfmpegProc["ffmpeg-processor.ts<br/>(FFmpeg.wasm)"]
    Registry --> DocInline["Document Viewer<br/>(inline registry processor)"]
    DocInline --> docxPrev["docx-preview (DOCX)"]
    DocInline --> xlsxLib["exceljs + papaparse<br/>(XLSX/CSV HTML tables)"]
    DocInline --> nativeDocs["Native pass-through<br/>(PDF/TXT/JSON)"]
    UI --> CollageUI["CollagePanel.tsx<br/>(react-konva)"]
    UI --> RecorderUI["RecorderPanel.tsx<br/>(MediaRecorder + capture APIs + canvas composition)"]
    UI --> TodoUI["TodoListPanel.tsx<br/>(localStorage + Drive sync + JSON import/export)"]
    TodoUI --> TodoModel["todo-list.ts<br/>(schema normalization + merge/search/link parsing)"]
    UI --> ShellUI["AppShellProvider.tsx<br/>(offline status + Drive auth/sync + PWA-ready toast)"]
    UI --> Header["Header.tsx<br/>(search, cloud, GitHub, debug console, theme)"]
    ShellUI --> DriveAuth["google-drive.ts<br/>(Google Identity Services code popup)"]
    ShellUI --> ServerFns["server-functions.ts<br/>(OAuth exchange + Drive REST proxy)"]
    ShellUI --> SW["src/sw.ts<br/>(Serwist precache runtime)"]

    style ImgProc fill:#4ecdc4,color:#000
    style PdfProc fill:#ff6b6b,color:#000
    style FileProc fill:#ffe66d,color:#000
    style FfmpegProc fill:#9b5de5,color:#fff
    style DocInline fill:#f4a261,color:#000
```

### Routing

- `/` renders `src/routes/index.tsx`, reads the `q` search param, ranks all registry tools with `rankToolsByQuery()`, and otherwise groups tools by category.
- `/tool/$id` renders `src/routes/tool.$id.tsx`, looks up the ID with `getToolById()`, and passes the selected tool to `ToolPanel`.
- `src/routes/__root.tsx` owns the app shell, metadata, theme bootstrap, route preloading, and route-specific PWA manifest switching. `/tool/todo-list` uses `/manifest-todo.json`; all other routes use `/manifest.json`.
- There are no per-tool route files.

---

## Tool Model

All tools are objects in `src/lib/tool-registry.ts`. A tool definition contains:

- `id`, `name`, `description`, `category`, `icon`
- `acceptedExtensions` and optional `producedExtensions`
- `multiple`
- optional `requiresFiles`
- optional `uiMode`: `standard`, `auto-process`, `collage`, `recorder`, or `todo`
- `options`
- `process(files, options) => Promise<ProcessedFile[]>`

`ToolPanel` handles file selection, previews, options, processing, result cards, downloads, ZIP download-all, and Drive upload actions for standard tools. Custom UI modes render:

- `auto-process`: runs immediately after file selection; currently used by `document-viewer`.
- `collage`: renders `CollagePanel`.
- `recorder`: renders `RecorderPanel`.
- `todo`: renders `TodoListPanel`.

`batch()` in the registry sequentially applies single-file processors to multi-file tools. Tools like PDF merge and image-to-PDF handle all files as one batch.

`FileDropzone` accepts drag/drop and hidden file input selection. It builds the input `accept` string from `acceptedExtensions`, optional MIME types, and an extra `text/csv` hint for CSV selection on mobile browsers. `ToolCard` shows the first four accepted extensions visually, adds a `+N` badge for the rest, and includes an `sr-only` metadata block with the tool description and accepted extensions.

### Registered Tools

This list matches the current registry.

| Category | Tools |
| --- | --- |
| Image | `image-convert`, `image-resize`, `image-rotate`, `image-crop`, `image-upscale`, `image-collage`, `image-blur`, `image-pixelate`, `image-add-text`, `image-remove-bg` |
| PDF | `pdf-merge`, `pdf-split`, `pdf-delete-pages`, `pdf-reorder`, `pdf-header-footer`, `pdf-bates-numbering`, `pdf-add-blank-pages`, `pdf-remove-blank-pages`, `pdf-crop-pages`, `pdf-overlay-pages`, `pdf-resize-pages`, `pdf-n-up`, `pdf-page-dimensions`, `pdf-sign-visual`, `pdf-digital-sign`, `pdf-validate-signature`, `pdf-lock`, `pdf-unlock`, `pdf-images-to-pdf`, `pdf-to-images`, `pdf-compress`, `pdf-watermark`, `pdf-rotate`, `pdf-flatten`, `pdf-metadata`, `pdf-strip-metadata`, `pdf-remove-annotations` |
| Video | `video-convert`, `video-trim`, `video-extract-audio`, `video-merge`, `video-audio-merge`, `video-mute`, `video-speed`, `screen-recorder`, `camera-recorder`, `video-resize`, `video-crop`, `video-watermark`, `video-extract-frames` |
| Audio | `audio-convert`, `audio-trim`, `audio-merge`, `audio-recorder`, `audio-volume`, `audio-fade` |
| Document | `document-viewer` |
| File | `file-zip`, `file-unzip` |
| Data | `data-csv-to-json`, `data-json-to-csv`, `data-format-json`, `todo-list` |

Current count: 63 tools.

