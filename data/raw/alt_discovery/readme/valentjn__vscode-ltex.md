<!--
   - Copyright (C) 2019-2021 Julian Valentin, LTeX Development Community
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/.
   -->

<!-- #if TARGET == 'vscode' -->
# LT<sub>E</sub>X Extension for VS Code: Grammar/Spell Checker Using LanguageTool with Support for L<sup>A</sup>T<sub>E</sub>X, Markdown, and Others
<!-- #elseif TARGET == 'coc.nvim' -->
<!-- # LT<sub>E</sub>X Extension for coc.nvim: Grammar/Spell Checker Using LanguageTool with Support for L<sup>A</sup>T<sub>E</sub>X, Markdown, and Others -->
<!-- #endif -->

[![latest release](https://badgen.net/badge/-/release/585858?label=)![version number](https://badgen.net/vs-marketplace/v/valentjn.vscode-ltex?label=)![release date](https://badgen.net/github/last-commit/valentjn/vscode-ltex/release?label=)][website]&nbsp;
[![installs](https://badgen.net/vs-marketplace/i/valentjn.vscode-ltex)][website]&nbsp;
[![rating](https://badgen.net/vs-marketplace/rating/valentjn.vscode-ltex)][marketplace]

[![vscode-ltex](https://badgen.net/github/license/valentjn/vscode-ltex?label=vscode-ltex)](https://github.com/valentjn/vscode-ltex)&nbsp;
[![CI status](https://github.com/valentjn/vscode-ltex/workflows/CI/badge.svg?branch=release)](https://github.com/valentjn/vscode-ltex/actions?query=workflow%3A%22CI%22+branch%3Arelease)&nbsp;
[![stars](https://badgen.net/github/stars/valentjn/vscode-ltex)](https://github.com/valentjn/vscode-ltex)&nbsp;
[![open issues](https://badgen.net/github/open-issues/valentjn/vscode-ltex?label=open/closed%20issues&color=blue)](https://github.com/valentjn/vscode-ltex/issues)&nbsp;[![closed issues](https://badgen.net/github/closed-issues/valentjn/vscode-ltex?label=)](https://github.com/valentjn/vscode-ltex/issues)\
[![ltex-ls](https://badgen.net/github/license/valentjn/ltex-ls?label=ltex-ls)](https://github.com/valentjn/ltex-ls)&nbsp;
[![CI status](https://github.com/valentjn/ltex-ls/workflows/CI/badge.svg?branch=release)](https://github.com/valentjn/ltex-ls/actions?query=workflow%3A%22CI%22+branch%3Arelease)&nbsp;
[![coverage](https://badgen.net/coveralls/c/github/valentjn/ltex-ls/release)](https://coveralls.io/github/valentjn/ltex-ls)&nbsp;
[![stars](https://badgen.net/github/stars/valentjn/ltex-ls)](https://github.com/valentjn/ltex-ls)&nbsp;
[![open issues](https://badgen.net/github/open-issues/valentjn/ltex-ls?label=open/closed%20issues&color=blue)](https://github.com/valentjn/ltex-ls/issues)&nbsp;[![closed issues](https://badgen.net/github/closed-issues/valentjn/ltex-ls?label=)](https://github.com/valentjn/ltex-ls/issues)

<!-- #if TARGET == 'vscode' -->
**LT<sub>E</sub>X** provides offline grammar checking of various markup languages in Visual Studio Code using [LanguageTool (LT)](https://languagetool.org/). LT<sub>E</sub>X currently supports BibT<sub>E</sub>X, ConT<sub>E</sub>Xt, L<sup>A</sup>T<sub>E</sub>X, Markdown, Org, reStructuredText, R Sweave, and XHTML documents. In addition, LT<sub>E</sub>X can check comments in many popular programming languages (optional, opt-in).
<!-- #elseif TARGET == 'coc.nvim' -->
<!-- **LT<sub>E</sub>X** provides offline grammar checking of various markup languages in Vim/Neovim using [LanguageTool (LT)](https://languagetool.org/) and [coc.nvim](https://github.com/neoclide/coc.nvim). LT<sub>E</sub>X currently supports BibT<sub>E</sub>X, ConT<sub>E</sub>Xt, L<sup>A</sup>T<sub>E</sub>X, Markdown, Org, reStructuredText, R Sweave, and XHTML documents. In addition, LT<sub>E</sub>X can check comments in many popular programming languages (optional, opt-in). -->
<!-- #endif -->

The difference to regular spell checkers is that LT<sub>E</sub>X not only detects spelling errors, but also many grammar and stylistic errors such as:

- `This is an mistake.`
- `The bananas is tasty.`
- `We look forward to welcome you.`
- `Are human beings any different than animals?`

A classic use case of LT<sub>E</sub>X is checking scientific L<sup>A</sup>T<sub>E</sub>X papers, but why not check your next blog post, book chapter, or long e-mail before you send it to someone else?

[Find more information and documentation about LT<sub>E</sub>X on the official website.][website]

LT<sub>E</sub>X is a successor (since it's a fork) of the abandoned [LanguageTool for Visual Studio Code extension](https://github.com/adamvoss/vscode-languagetool) by Adam Voss<sup>†</sup>.

## Features

![Grammar/Spell Checker for VS Code with LanguageTool and LaTeX Support](https://github.com/valentjn/vscode-ltex/raw/release/img/banner-ltex.png)

- **Supported markup languages:** BibT<sub>E</sub>X, ConT<sub>E</sub>Xt, L<sup>A</sup>T<sub>E</sub>X, Markdown, Org, reStructuredText, R Sweave, XHTML
- Comment checking in **many popular programming languages** (optional, opt-in)
- Comes with **everything included,** no need to install Java or LanguageTool
- **Offline checking:** Does not upload anything to the internet
- Supports **over 20 languages:** English, French, German, Dutch, Chinese, Russian, etc.
- **Issue highlighting** with hover description
- **Replacement suggestions** via quick fixes
- **User dictionaries**
- **Multilingual support** with babel commands or magic comments
- Possibility to use **external LanguageTool servers**
- **[Extensive documentation][website]**

## Requirements

<!-- #if TARGET == 'vscode' -->
- 64-bit Linux, Mac, or Windows operating system
- [VS Code 1.52.0 or newer](https://code.visualstudio.com/)
- Optional:
  - If you want to check documents written in a markup language that VS Code does not support out-of-the-box (e.g., L<sup>A</sup>T<sub>E</sub>X), install an extension that provides support for that language (e.g., [LaTeX Workshop Extension for VS Code](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)) in addition to this extension.
<!-- #elseif TARGET == 'coc.nvim' -->
<!-- - 64-bit Linux, Mac, or Windows op