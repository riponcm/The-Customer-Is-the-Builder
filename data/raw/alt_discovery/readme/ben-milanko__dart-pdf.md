![dart-pdf, an open-source Flutter PDF editor and pure-Dart renderer](doc/banner.png)

# dart-pdf: Flutter PDF editor and renderer

[![CI](https://github.com/ben-milanko/dart-pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/ben-milanko/dart-pdf/actions/workflows/ci.yml)
[![dart_pdf_editor on pub.dev](https://img.shields.io/pub/v/dart_pdf_editor.svg)](https://pub.dev/packages/dart_pdf_editor)
[![codecov](https://codecov.io/gh/ben-milanko/dart-pdf/branch/main/graph/badge.svg)](https://codecov.io/gh/ben-milanko/dart-pdf)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> [!TIP]
> **Want the app, not the SDK?** [**DartPDF**](https://dart-pdf.com) is the
> official PDF editor built on this library. Edit, annotate, sign, and fill
> PDFs entirely on your device, with no account and no uploads. Get it at
> [dart-pdf.com](https://dart-pdf.com) or
> [open it in your browser](https://app.dart-pdf.com).
>
> Need to complete a form? [Fill and sign a PDF with DartPDF](doc/guides/fill-and-sign-pdf.md)
> explains existing fields, flat forms, drawn signatures, and saving a checked copy.

[![DartPDF, the official PDF editor app, built on this SDK. Get the app at dart-pdf.com](doc/app-banner.svg)](https://dart-pdf.com)

An open-source Flutter PDF editor, viewer, and renderer written entirely in
Dart. No PDFium, no platform channels.

The goal is a PSPDFKit-class SDK built natively for Flutter: a fast
viewer, a full annotation suite with appearance-stream generation,
AcroForm filling, page manipulation, and editing that preserves digital
signatures.

Feature parity is only the foundation. The [UX vision](doc/ux-vision.md)
defines the product north star, the journeys that matter, how their quality is
measured, and the definition of done for user-facing work.

> Status: the roadmap below is complete. COS parsing with xref recovery,
> signature-preserving incremental updates with encrypt-on-write, a
> content-stream interpreter with TrueType/CFF/Type3 font rendering,
> mesh shadings, ICC color, pure-Dart CCITT/JBIG2/JPEG 2000 decoders, a
> zoomable Flutter viewer with text selection and search, inferred text
> reflow, annotation authoring and flattening, AcroForm filling, page
> manipulation, digital signatures with trust-store chain validation,
> content editing, and the full editing UI: tools, panels, forms,
> touch/stylus input, theming, and a sync surface for collaborative
> annotation stores.

![The example app: PdfEditorView showing the feature showcase document](doc/dart_pdf_editor_example.jpg)

Live demo: <https://dart-pdf-demo.web.app> (the example app built for
the web; it opens onto a six-page feature showcase, and the open button
loads your own PDF).

Developer overview: [Flutter PDF editor](https://dart-pdf.com/flutter-pdf-editor)

Step-by-step integration: [How to add PDF editing to a Flutter app](https://dart-pdf.com/guides/add-pdf-editing-to-flutter)
with installation, architecture, supported editing features, and benchmarks.

Visual render results, browsable directly in GitHub: the checked-in
[PDF.js corpus comparison gallery](test_corpora/pdfjs/_renders/README.md)
shows PDF.js baselines, Dart renders, and diffs side by side, and the
[Ghent Output Suite render gallery](test_corpora/ghent/_baselines/README.md)
shows every print-conformance page we rasterize (our own renders, which
are the baselines - so no diff column).

## Merge PDFs

```dart
import 'package:pdf_document/pdf_document.dart';

final mergedBytes = PdfMerger.merge([firstPdfBytes, secondPdfBytes]);
```

The bytes-only API runs on desktop, mobile, and web. It preserves the first
PDF's encryption and viewing settings, imports form fields and bookmarks, and
remaps named links. See [merge options and collision rules](packages/pdf_document/README.md#merge-pdfs).

In DartPDF, choose **Insert document…** from the app menu to insert a PDF after
the current page. Dropping PDFs on the thumbnail strip inserts at the marked
position; dropping on the document offers **Insert pages** to append them.
Each inserted file is one undo step and uses the existing save/recovery session.

## Reduce file size

In DartPDF, choose **Reduce file size…** from the app menu. Start with
**Lossless**, or choose **Screen**, **eBook**, or **Print** to trade image
resolution for a smaller file. Advanced settings control individual passes,
target DPI, and JPEG quality. Review the before/after sizes and category
breakdown, then **Save copy** using the platform's save/download/share flow.

The library exposes the same optimiser through `PdfCompressor.optimize` and
`PdfEditor.compress`. See [compression options and supported content](packages/pdf_document/README.md#reduce-file-size).

## Performance

**The default viewer has not reached PDFium interaction parity yet.** The most
recent real-document checkpoint (2 October 2026, commit `fadf7760`) used five
interleaved DartPDF/PDFium runs in Chrome 154 on an M1 Pro, a 1400×1000
viewport, and the default JS/CanvasKit web build. The input was a locally
supplied 62-page, 24.1 MB illustrated PDF; the journey opened it, jumped to
pages 3 and 47, zoomed to 1.72×, and drove matched wheel gestures. Lower
ratios are better.

| user-visible metric | DartPDF p50 / p95 | PDFium p50 / p95 | ratio p50 / p95 |
|---|---:|---:|---:|
| open to stable visual | 711 / 757 ms | 1264 / 1411 ms | **0.56× / 0.54×** |
| page first visual change | 24 / 31 ms | 19 / 22 ms | 1.26× / 1.39× |
| page stable visual | 271 / 357 ms | 118 / 121 ms | **2.30× / 2.95×** |
| zoom stable visual | 44 / 47 ms | 19 / 25 ms | **2.32× / 1.92×** |
| wheel journey | 413 / 919 ms | 972 / 1022 ms | 0.42× / 0.90× |
| wheel rAF interval p95 | 83 ms | 17 ms | **4.96×** |
| peak browser RSS p50 | 2167 MiB | 1887 MiB | 1.15× |

The wheel journey completes sooner, but its worse rAF tail means it is not yet
as smooth; total duration alone would be a misleading win. Headless Chrome 154
appears to pace frames at 60 Hz on this