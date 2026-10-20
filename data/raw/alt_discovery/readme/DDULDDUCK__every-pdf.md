> [!WARNING]
> ### ⚠️ Important Notice for macOS Users Regarding Updates ⚠️
>
> To enhance the security of Every-PDF, we have updated our official code signature. As a result, **the auto-updater will fail for all previous versions.**
>
> **You must manually download and install v2.0.2 or later versions to receive this update.**
>
> We apologize for this one-time inconvenience. All future updates will be delivered automatically as expected.
>
> **[➡️ Download the Latest Version Here](https://github.com/DDULDDUCK/every-pdf/releases/latest)**
---


# Every PDF
<p align="center">
  <!-- 프로젝트 로고를 여기에 추가할 수 있습니다. -->
  <img src="resources/logo.png" alt="Every PDF Logo" width="150">
  <br>
  <strong>A powerful and intuitive all-in-one desktop PDF editing tool.</strong>
</p>

<p align="center">
  <!-- 소셜 및 커뮤니티 배지 -->
  <a href="https://github.com/DDULDDUCK/every-pdf/stargazers"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/DDULDDUCK/every-pdf?style=for-the-badge&logo=github&color=gold"></a>
  <a href="https://github.com/DDULDDUCK/every-pdf/network/members"><img alt="GitHub Forks" src="https://img.shields.io/github/forks/DDULDDUCK/every-pdf?style=for-the-badge&logo=github&color=blueviolet"></a>
  <a href="https://github.com/DDULDDUCK/every-pdf/graphs/contributors"><img alt="All Contributors" src="https://img.shields.io/github/all-contributors/DDULDDUCK/every-pdf?style=for-the-badge&color=orange"></a>
  <br>
  <!-- 상태 및 릴리즈 배지 -->
  <a href="https://github.com/DDULDDUCK/every-pdf/releases"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/DDULDDUCK/every-pdf?style=for-the-badge&color=brightgreen"></a>
  <a href="https://github.com/DDULDDUCK/every-pdf/releases"><img alt="GitHub Downloads" src="https://img.shields.io/github/downloads/DDULDDUCK/every-pdf/total?style=for-the-badge&logo=github&color=success"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/DDULDDUCK/every-pdf?style=for-the-badge&color=informational"></a>
  <br>
  <!-- 개발 활동 배지 -->
  <a href="https://github.com/DDULDDUCK/every-pdf/actions/workflows/release.yml"><img alt="Build Status" src="https://img.shields.io/github/actions/workflow/status/DDULDDUCK/every-pdf/release.yml?branch=main&style=for-the-badge&logo=githubactions"></a>
  <a href="https://github.com/DDULDDUCK/every-pdf/issues"><img alt="GitHub Issues" src="https://img.shields.io/github/issues/DDULDDUCK/every-pdf?style=for-the-badge&logo=github&color=red"></a>
  <a href="https://github.com/DDULDDUCK/every-pdf/pulls"><img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/DDULDDUCK/every-pdf?style=for-the-badge&logo=github&color=yellow"></a>
</p>

<p align="center">
  <a href="./README.md"><img alt="Language-English" src="https://img.shields.io/badge/Language-English-blue?style=for-the-badge"></a>
  <a href="./README.ko.md"><img alt="Language-Korean" src="https://img.shields.io/badge/언어-한국어-blue?style=for-the-badge"></a>
</p>

---

## ✨ Key Features

Every PDF is a powerful desktop application packed with all the features you need, from everyday document tasks to professional-level editing.

*   **✍️ PDF Editor (New!)**: Add text, signatures, images, and checkboxes to complete your documents.
*   **🔄 Convert PDF**: Converting PDFs to different formats and converting different formats to PDFs .
*   **📄 Split Pages**: Easily split large PDF files by a specific page range or individual page numbers.
*   **➕ Merge Files**: Effortlessly combine multiple PDF documents into a single file with a simple drag-and-drop.
*   **💧 Watermark**: Protect your documents by adding custom text or image watermarks.
*   **🔄 Manage Pages**: Rotate or reorder pages to take full control of your document's flow.
*   **🔐 Encrypt/Decrypt**: Secure your PDF documents by adding or removing password protection.
---

## 📥 Download

Get the latest version of Every PDF for your operating system.

| Operating System | File Format | Download Link |
| :---: | :---: | :---: |
| 💻 **Windows** | `.exe` | <a href="https://github.com/DDULDDUCK/every-pdf/releases/latest"><img src="https://img.shields.io/badge/Latest_Release-Download-brightgreen?style=flat-square" /></a> |
| 🍏 **macOS** | `.dmg` | <a href="https://github.com/DDULDDUCK/every-pdf/releases/latest"><img src="https://img.shields.io/badge/Latest_Release-Download-brightgreen?style=flat-square" /></a> |
<!--| 🐧 **Linux** | `.AppImage` | <a href="https://github.com/DDULDDUCK/every-pdf/releases/latest"><img src="https://img.shields.io/badge/Latest_Release-Download-brightgreen?style=flat-square" /></a> |-->

---

## 📺 Demos in Action

<details open>
<summary><strong>New Editing Features Demo (v2.0.0)</strong></summary>

![Edit Demo](https://github.com/user-attachments/assets/e3ec427a-5a43-4d23-840b-9fbc73e1a8cb)
</details>

<details open>
<summary><strong>Split Feature Demo</strong></summary>

![Split Demo](https://github.com/user-attachments/assets/bcf83b87-b04a-436b-9e7f-f585f4c78faa)
</details>

---

## 👨‍💻 For Developers

Interested in contributing? Follow this guide to set up the project locally.

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://www.python.org/) (v3.10 or higher)
- [Git](https://git-scm.com/)

### Installation & Run

```bash
# 1. Clone the project
git clone https://github.com/DDULDDUCK/every-pdf.git
cd every-pdf

# 2. Install Node.js dependencies
npm install

# 3. Set up the Python backend environment (automatic)
# This script creates a virtual environment and installs dependencies.
npm run setup-backend

# 4. Run in development mode (starts both frontend and backend)
npm run dev
```

### Project Structure
```
every-pdf/
├── app/          # Final Electron app resources (built by Nextron)
├── backend/      # Python backend source and virtual environment (venv)
├── main/         # Electron main process source (TypeScript)
├── public/       # Static assets (images, etc.)
├── renderer/     # Next.js frontend sour