# <img src="ui/pixmaps/com.github.xournalpp.xournalpp.svg" align="left" width="100" height="100">  <br> Xournal++


[![Build Status](https://dev.azure.com/xournalpp/xournalpp/_apis/build/status/CI?branchName=master)](https://dev.azure.com/xournalpp/xournalpp/_build/latest?definitionId=1&branchName=master)

<img src="readme/main.png" width=550px% title="Xournal++ on GNU/Linux"/>

## Translations

Would you like to see Xournal++ in your own language? Translators are welcome to contribute to Xournal++.

You can contribute translations on [Crowdin](https://crowdin.com/project/xournalpp/).

Interested in translating a new language? Discuss on [Matrix](https://matrix.to/#/#xournalpp_xournalpp:gitter.im) or create a [new issue](https://github.com/xournalpp/xournalpp/issues) to unlock the language on Crowdin.

**Thanks in advance!**

## Features

Xournal++ (/ˌzɚnl̟ˌplʌsˈplʌs/) is a hand note-taking software written in C++ with the target of flexibility, functionality and speed.
Stroke recognizer and other parts are based on Xournal Code, which you can find at [SourceForge](http://sourceforge.net/projects/xournal/).

Xournal++ features:

- Supports pressure-sensitive styluses and digital pen tables (e.g. Wacom, Huion, XP Pen, etc. tablets)
- Paper backgrounds for note-taking, scratch paper, or whiteboarding
- Annotate on top of PDFs
- Select text from the background PDF, copy, highlight or underline it or strike it through
- Follow links from the background PDF
- Export to a variety of formats including SVG, PNG and PDF, both from the GUI and command line
- Different drawing tools (e.g. pen, highlighter) and stroke styles (e.g. solid, dotted)
- Shape drawing (line, arrow, circle, rectangle, spline)
- Use the set-square and compass tools for measurements or as a guide for drawing straight lines, circular arcs and radii
- Fill shape functionality
- Shape resizing and rotation
- Rotation and grid snapping for precise alignment of objects
- Input stabilization for smoother writing/drawing
- Text tool for adding text in different fonts, colors, and sizes
- Enhanced support for image insertion
- Eraser with multiple configurations
- LaTeX support (requires a working LaTeX installation) with customizable template and a resizable editor with syntax highlighting
- Sidebar containing page previews with advanced page sorting, PDF bookmarks and layers (can be individually hidden/edited)
- Allows mapping different tools/colors etc. to stylus/mouse buttons
- Customizable toolbar with multiple configurations, e.g. to optimize toolbar for portrait/landscape
- Custom color palette support using the .gpl format
- Page template definitions
- Bug reporting, auto-save, and auto backup tools
- Audio recording and playback alongside with handwritten notes
- Multi language support (over 20 languages supported)
- Plugins using Lua scripting


<table>
<tr>
<td>

## GNU/Linux

<img src="readme/main.png" width=100% title="Xournal++ on GNU/Linux"/>

</td><td>

## Windows 10

<img src="readme/main-win.png" width=100% title="Xournal++ on Windows 10"/>

</td></tr><tr><td>

## macOS Catalina

<img src="readme/main-mac.png" width=100% title="Xournal++ on macOS Catalina"/>

</td><td>

## Xournal++ Mobile on Chromium OS

<img src="https://gitlab.com/TheOneWithTheBraid/xournalpp_mobile/-/raw/master/fastlane/metadata/android/en_US/images/tenInchScreenshots/03.png" width=100% title="Xournal++ Mobile on Chromium OS"/>

</td></tr><tr><td>

## Toolbar / Page Background / Layer

Multiple page background, easy selectable on the toolbar
<img src="readme/background.png" width=100% title="Changing the page background in Xournal++"/>

</td><td>

## Layer sidebar and advanced layer selection

<img src="readme/layer.png" width=100% title="Layers in Xournal++"/>

</td></tr><tr><td>

## Multiple predefined and fully customizable toolbars

<img src="readme/toolbar.png" width=100% title="Custom toolbars in Xournal++"/>

</td></tr></table>

## User Guide

Check out the [website](https://xournalpp.github.io/guide/overview/) for a detailed user guide.

## Installing

The official releases of Xournal++ can be found on the
[Releases](https://github.com/xournalpp/xournalpp/releases) page. We provide
binaries for Debian, Ubuntu, macOS and Windows.
For other GNU/Linux distributions (or older/newer ones), we also provide an
AppImage that is binary compatible with any distribution released around or
after Ubuntu 22.04. For installing Xournal++ Mobile on handheld devices, please check out the [Mobile & web app section](#mobile--web-app)

**A note for Ubuntu/Debian users**: The official binaries that we provide are
only compatible with the _specific version of Debian or Ubuntu_ indicated by the
file name. For example, if you are on Ubuntu 20.04, the binary whose name
contains `Ubuntu-bionic` is _only_ compatible with Ubuntu 18.04. If your system
is not one of the specific Debian or Ubuntu versions that are supported by the
official binaries, we recommend you use either the PPA (Ubuntu only), the Flatpak, or the
AppImage.

There is also an _unstable_, [automated nightly
release](https://github.com/xournalpp/xournalpp/releases/tag/nightly) that
includes the very latest features and bug fixes.

With the help of the community, Xournal++ is also available on official repositories
of some popular GNU/Linux distros and platforms.

[![Packaging status](https://repology.org/badge/vertical-allrepos/xournalpp.svg?columns=5)](https://repology.org/project/xournalpp/versions)


### Debian

On Debian bookworm and Debian sid the `xournalpp` package (stable version) is contained in the official repositories. Simply install via

```sh
sudo apt install xournalpp
```

There are also the official [Stable releases](https://github.com/xournalpp/xournalpp/releases) and
_unstable_ [automated nightly releases](https://github.com/xournalpp/xournalpp/releases/tag/nightly).

### Ubuntu and derivatives

On distros based on Ubuntu 22.04 Jammy Jellyfish (and later) the `xournalpp` package (st