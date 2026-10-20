<div align="center">

# ClearPDF

### Open-source PDF and document tools for Android.

Read and annotate PDFs, sign forms, work with Office documents, edit spreadsheets and images, and create PDFs on your phone. Built with Kotlin and Jetpack Compose.

<p>
  <a href="https://github.com/Chethan616/ClearPDF/releases/latest"><strong>Download the latest ClearPDF</strong></a>
  · <a href="https://github.com/Chethan616/ClearPDF/releases">All releases</a>
  · <a href="https://github.com/Chethan616/ClearPDF/issues/new/choose">Report a problem or request a feature</a>
  · <a href="CONTRIBUTING.md">Contribute</a>
</p>

<p>
  <a href="https://github.com/Chethan616/ClearPDF/stargazers"><img src="https://img.shields.io/github/stars/Chethan616/ClearPDF?style=flat-square&color=FF9F0A" alt="GitHub stars"></a>
  <a href="https://github.com/Chethan616/ClearPDF/releases/latest"><img src="https://img.shields.io/github/v/release/Chethan616/ClearPDF?style=flat-square&color=0A84FF&label=latest%20release" alt="Latest release"></a>
  <a href="https://github.com/Chethan616/ClearPDF/releases"><img src="https://img.shields.io/github/downloads/Chethan616/ClearPDF/total?style=flat-square&color=BF5AF2&label=downloads" alt="Total GitHub downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/Chethan616/ClearPDF?style=flat-square&color=30D158" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/Android-6.0%2B-3DDC84?style=flat-square&logo=android&logoColor=white" alt="Android 6.0 or newer">
  <a href="https://github.com/Chethan616/ClearPDF/actions/workflows/android.yml"><img src="https://img.shields.io/github/actions/workflow/status/Chethan616/ClearPDF/android.yml?branch=main&style=flat-square&label=Android%20build" alt="Android build status"></a>
</p>

</div>

ClearPDF is an Android document toolkit for reading and annotating PDFs, managing PDF pages, scanning paper documents, and opening common Office and image files. The source is licensed under MIT. Most file operations run on-device. The FOSS build uses network for its optional Office engine and URL-to-PDF features; Google Play services may provide scanner and background-removal components. See the [privacy notes](PRIVACY.md).

## Featured by HowToMen

ClearPDF was featured by HowToMen. [Watch the video from 9:08](https://www.youtube.com/watch?v=TYNzg59ke30&t=548s).

## Screenshots

<p align="center">
  <img src="screenshots/light%20home%20screen.jpg" width="24%" alt="ClearPDF home screen in light mode">
  <img src="screenshots/light%20pdf%20tools.jpg" width="24%" alt="ClearPDF PDF tools in light mode">
  <img src="screenshots/light%20settings%20screen.jpg" width="24%" alt="ClearPDF settings in light mode">
  <img src="demo/3.jpg" width="24%" alt="ClearPDF PDF editing tools">
</p>
<p align="center">
  <img src="screenshots/dark%20home%20screen.jpg" width="24%" alt="ClearPDF home screen in dark mode">
  <img src="screenshots/dark%20pdf%20tools.jpg" width="24%" alt="ClearPDF PDF tools in dark mode">
  <img src="screenshots/dark%20settings%20screen.jpg" width="24%" alt="ClearPDF settings in dark mode">
  <img src="demo/4.jpg" width="24%" alt="ClearPDF annotation tools">
</p>

Short walkthroughs: [onboarding](demo/1.mp4) · [PDF viewer](demo/2.mp4).

## What you can do

### Read and work with PDFs

- Read with continuous scrolling, pinch-to-zoom, page navigation, and in-document search.
- Select and copy text; run on-device OCR for image-only pages.
- Add highlights, underlines, strikethroughs, ink, shapes, arrows, text notes, and signatures.
- Fill PDF forms, flatten form fields, and export an annotated copy.
- Organize, rotate, delete, or extract pages; merge and split files.
- Compress, encrypt, or decrypt PDFs; add page numbers or watermarks; export pages as images; extract text; create PDFs from text or images.

### Open Office and text documents

Open PDF, DOC/DOCX, XLS/XLSX, PPT/PPTX, ODT/ODS/ODP, RTF, CSV, and TXT files. Rendering depends on the format and renderer. The optional LibreOffice-based engine can improve rendering for supported Office formats.

The spreadsheet editor can edit and save XLSX workbooks. Word and PowerPoint files are opened for viewing; ClearPDF does not rewrite their original text layout. You can annotate the rendered document and export it as a PDF.

### Edit images and scan paper

- Crop, rotate, straighten, and perspective-correct images.
- Adjust colour and tone, apply filters, draw, add text or watermarks, and resize.
- Remove image backgrounds on supported devices; Google Play services may provide the segmentation model.
- Scan multi-page documents, adjust the results, and save them as PDF. Scanning is provided by Google Play services and depends on its availability on the device.

### Create PDFs from local content or a web address

Create a PDF from images, text, or local HTML. The FOSS build can also convert a web address; this requests that site and its page resources. Local HTML conversion works without loading a website.

## Supported Android versions and formats

- **Android:** API 23 (Android 6.0) or newer.
- **Document formats:** PDF; DOC/DOCX; XLS/XLSX; PPT/PPTX; ODT/ODS/ODP; RTF; CSV; TXT.
- **Images:** PNG, JPEG, WebP, BMP, and HEIC are supported by the image/document flows. Feature availability can vary by device and Android version.

Only XLSX files have spreadsheet cell editing and save support. Other Office formats are viewed through the built-in or optional Office renderer; visual fidelity varies by document and renderer.

ClearPDF annotates PDFs and edits form fields, signatures, and pages, but it does not rewrite arbitrary text already printed into a PDF page. Likewise, Word and PowerPoint files are viewed and exported as PDF rather than edited in their original formats.

## Download

The current stable release is **V4 (app version 2.0.0)**. Open the [V4 release page](https://github.com/Chethan616/ClearPDF/releases/tag/v4) and choose the APK that matches your device:

| APK 