![ltapiserv-rs](doc/logo.webp)

This provides a **lightweight alternative backend implementation** of the LanguageTool API for **offline grammar and spell checking**, based on:

- [nlprule](https://github.com/bminixhofer/nlprule) for grammar and style checking, using the [LanguageTool rules](https://github.com/languagetool-org/languagetool).
- [symspell](https://github.com/reneklacan/symspell) for spell-checking.

A simple command-line client, `ltapi-client`, is also provided, displaying results graphically with [miette](https://docs.rs/miette/latest/miette/).

## Quick start

1. [Install the server](#installation), which is a single binary with no dependencies, which can be run as a systemd service. Debian/Ubuntu and Arch packages are provided. Alternatively, a Docker image is available.
2. [Configure your client](#usage-clients) (browser, editor, `ltapi-client`, ...) to use the local server.

## Screenshots

![Illustration](doc/illustration.png) \
_Using the `ltapiserv-rs` server with the official LanguageTool browser extension._

![Command line interface](doc/client.png)
_Output from the client CLI_

## Background

## LanguageTool

[LanguageTool](https://languagetool.org/) is an open-source alternative to [Grammarly](https://www.grammarly.com/) for natural language linting (spelling, grammar, style), with a [large set of rules](https://community.languagetool.org/). Multiple clients exist for its API, bringing functionalities to [Firefox](https://addons.mozilla.org/firefox/addon/languagetool/), [Chrome](https://chrome.google.com/webstore/detail/grammar-and-spell-checker/oldceeleldhonbafppcapldpdifcinji?utm_source=lt-homepage&utm_medium=referral), [LibreOffice](https://languagetool.org/libre-office), [Thunderbird](https://languagetool.org/thunderbird), [emacs](https://github.com/emacs-languagetool/flycheck-languagetool), and many more.

### Self-hosting LanguageTool

While most users access LanguageTool through the official hosted server (with a free or paid plan), the Java API server can be [hosted locally](https://dev.languagetool.org/http-server), which can be particularly desirable for privacy reasons (e.g. when editing confidential documents).

Even though the browser extensions are unfortunately [closed-source](https://forum.languagetool.org/t/license-and-source-code-for-firefox-add-on/3851), they still allow custom servers to be specified.

### Lightweight LanguageTool API server

[Benjamin Minixhofer](https://bmin.ai/) wrote a Rust crate, [`nlprule`](https://github.com/bminixhofer/nlprule), that is able to parse and then apply LanguageTool rules noticeably faster than the original Java implementation (see [this benchmark](https://github.com/bminixhofer/nlprule)). More complex rules written in Java are not supported and spellchecking is not implemented, but nevertheless roughly 85% of the LanguageTool grammar rules (as of 2021) are available.

Using `nlprule` and [`symspell`](https://crates.io/crates/symspell) (for spell-checking), we can implement a simple LanguageTool API server in Rust that can then be called from a variety of contexts using LanguageTool clients.

The code and binaries can be found on <i class="bi bi-github"></i> <https://github.com/cpg314/ltapiserv-rs>.  
See the `README` there for the configuration as a `systemd` service as well as the setup of the clients.

### Comparison with the Java server

Running [H.G. Wells' War of the Worlds](https://en.wikipedia.org/wiki/The_War_of_the_Worlds) (~6k lines and 62k words) through the two servers, using [hyperfine](https://github.com/sharkdp/hyperfine) and [httpie](https://httpie.io/docs/cli), we get:

```console
$ docker pull erikvl87/languagetool
$ docker run --rm -p 8010:8010 erikvl87/languagetool
  http://localhost:{port}/v2/check language=en-us text=@wells.txt'
$ for port in 8875 8010; do http --form  POST http://localhost:$port/v2/check \
                            language=en-us text=@wells.txt | jq ".matches|length"; done
1490
1045
$ hyperfine -L port 8875,8010 --runs 10 'http --ignore-stdin --meta --form  POST \
                   http://localhost:{port}/v2/check language=en-us text=@wells.txt'
```

The additional false positives in `ltapiserv-rs` seem to come mostly from the spell-checking.

| Command        |       Mean [s] | Min [s] | Max [s] |    Relative |
| :------------- | -------------: | ------: | ------: | ----------: |
| `ltapiserv-rs` | 16.002 ± 0.629 |  15.566 |  17.745 |        1.00 |
| `java`         | 30.594 ± 2.372 |  29.569 |  37.296 | 1.91 ± 0.17 |

With only a paragraph (to simulate something close to the normal use of LanguageTool, say in emails):

| Command        |   Mean [ms] | Min [ms] | Max [ms] | Relative |
| :------------- | ----------: | -------: | -------: | -------: |
| `ltapiserv-rs` | 379.7 ± 9.3 |    362.6 |    393.4 |     1.00 |

## Installation

Any of the following methods will make a server available at http://localhost:8875

By default, the custom dictionary is located in `~/.local/share/ltapiserv-rs/dictionary.txt`. A different path can be passed via the `--dictionary` option. The contents are automatically reloaded on file change.

### Docker

```console
$ docker run -d --name ltapiserv-rs -p 8875:8875 -v ~/.local/share/ltapiserv-rs:/data ghcr.io/cpg314/ltapiserv-rs:0.2.2
$ docker logs -f ltapiserv-rs
```

### Debian/Ubuntu and Arch packages

Packages are available from the [releases page](https://github.com/cpg314/ltapiserv-rs/releases), containing the server and `ltapi-client`. They will install a `systemd` service definition in `/usr/lib/systemd/user/ltapiserv-rs.service`, which can be enabled with:

```console
$ systemctl --user enable --now ltapiserv-rs
$ # Check status
$ systemctl --user status ltapiserv-rs
$ # Check logs
$ journalctl --user -u ltapiserv-rs -f
$ # After updating:
$ systemctl --user restart ltapiserv-rs
```

### tar.gz archive

For other distributions, standalone binaries are also available from the [releases page](https://github.com/cpg314/ltapise