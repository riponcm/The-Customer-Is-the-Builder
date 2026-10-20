# PDF.js [![CI](https://github.com/mozilla/pdf.js/actions/workflows/ci.yml/badge.svg?query=branch%3Amaster)](https://github.com/mozilla/pdf.js/actions/workflows/ci.yml?query=branch%3Amaster) [![codecov](https://codecov.io/gh/mozilla/pdf.js/branch/master/graph/badge.svg)](https://codecov.io/gh/mozilla/pdf.js) [![Reference images](https://img.shields.io/endpoint?url=https%3A%2F%2Fmozilla.github.io%2Fpdf.js.refs%2Fmakeref-badge.json)](https://github.com/mozilla/pdf.js.refs/commits/main)

[PDF.js](https://mozilla.github.io/pdf.js/) is a Portable Document Format (PDF) viewer that is built with HTML5.

PDF.js is community-driven and supported by Mozilla. Our goal is to
create a general-purpose, web standards-based platform for parsing and
rendering PDFs.

## Contributing

PDF.js is an open source project and always looking for more contributors. To
get involved, visit:

+ [Issue Reporting Guide](https://github.com/mozilla/pdf.js/blob/master/.github/CONTRIBUTING.md)
+ [Code Contribution Guide](https://github.com/mozilla/pdf.js/wiki/Contributing)
+ [Frequently Asked Questions](https://github.com/mozilla/pdf.js/wiki/Frequently-Asked-Questions)
+ [Good Beginner Bugs](https://github.com/mozilla/pdf.js/issues?q=is%3Aissue%20state%3Aopen%20label%3Agood-beginner-bug)
+ [Projects](https://github.com/mozilla/pdf.js/projects)

Feel free to stop by our [Matrix room](https://chat.mozilla.org/#/room/#pdfjs:mozilla.org) for questions or guidance.

## Getting Started

### Online demo

Please note that the "Modern browsers" version assumes native support for the
latest JavaScript features; please also see [this wiki page](https://github.com/mozilla/pdf.js/wiki/Frequently-Asked-Questions#faq-support).

+ Modern browsers: https://mozilla.github.io/pdf.js/web/viewer.html

+ Older browsers: https://mozilla.github.io/pdf.js/legacy/web/viewer.html

> [!NOTE]
> Open new files via the menu (the ">>" icon) or by dragging and dropping.

### Browser Extensions

#### Firefox

PDF.js is built into version 19+ of Firefox.

#### Chrome

+ The official extension for Chrome can be installed from the [Chrome Web Store](https://chrome.google.com/webstore/detail/pdf-viewer/oemmndcbldboiebfnladdacbdfmadadm).
*This extension is maintained by [@Rob--W](https://github.com/Rob--W).*
+ Build Your Own - Get the code as explained below and issue `npx gulp chromium`. Then open
Chrome, go to `Tools > Extension` and load the (unpackaged) extension from the
directory `build/chromium`.

### PDF debugger

Browse the internal structure of a PDF document with https://mozilla.github.io/pdf.js/internal-viewer/web/debugger.html

## Getting the Code

To get a local copy of the current code, clone it using git:

    $ git clone https://github.com/mozilla/pdf.js.git
    $ cd pdf.js

Next, install Node.js via the [official package](https://nodejs.org) or via
[nvm](https://github.com/creationix/nvm). If everything worked out, install
all dependencies for PDF.js:

    $ npm install

Finally, you need to start a local web server as some browsers do not allow opening
PDF files using a `file://` URL. Run:

    $ npx gulp server

and then you can open:

+ http://localhost:8888/web/viewer.html

Please keep in mind that this assumes the latest version of Mozilla Firefox; refer to [Building PDF.js](https://github.com/mozilla/pdf.js/blob/master/README.md#building-pdfjs) for non-development usage of the PDF.js library.

It is also possible to view all test PDF files on the right side by opening:

+ http://localhost:8888/test/pdfs/?frame

## Building PDF.js

In order to bundle all `src/` files into two production scripts and build the generic
viewer, run:

    $ npx gulp generic

If you need to support older browsers, run:

    $ npx gulp generic-legacy

This will generate `pdf.js` and `pdf.worker.js` in the `build/generic/build/` directory (respectively `build/generic-legacy/build/`).
Both scripts are needed but only `pdf.js` needs to be included since `pdf.worker.js` will
be loaded by `pdf.js`. The PDF.js files are large and should be minified for production.

## Code coverage

We track how much of the code is exercised by the test suite on
[Codecov](https://codecov.io/gh/mozilla/pdf.js) (see the badge at the top of this
file).

### How it is collected

When coverage is enabled, the build instruments the bundled code with
[`babel-plugin-istanbul`](https://github.com/istanbuljs/babel-plugin-istanbul),
which adds counters that record every line, branch and function that runs:

+ For browser-based tests (unit, integration and reference tests) the
  instrumented code runs in the browser, fills a global `window.__coverage__`
  object, and the test runner collects it from each browser session, merges the
  results, and writes the report.
+ For the Node-based unit tests (`unittestcli`) the raw data is written to
  `build/tmp/unittestcli-coverage.json` and turned into a report afterwards.

### Collecting coverage locally

Add the `--coverage` flag to any of the test tasks, for example:

    $ npx gulp unittest --coverage           # browser unit tests
    $ npx gulp unittestcli --coverage        # Node unit tests
    $ npx gulp integrationtest --coverage    # Puppeteer integration tests
    $ npx gulp botbrowsertest --coverage     # reference tests

The following options control the output:

| Option | Description | Default |
| --- | --- | --- |
| `--coverage` | Enable coverage collection. | off |
| `--coverage-output <dir>` | Directory where the report is written. | `build/coverage` |
| `--coverage-formats <list>` | Comma-separated list of formats: `info`, `html`, `json`, `text`, `cobertura`, `clover`. | `info` |
| `--coverage-per-test` | Also build a per-test index (see below). | off |

By default the report is written to `build/coverage` in the `info` format, i.e.
an [LCOV](https://github.com/linux-test-project/lcov) `lcov.info` file (the same
format that is uploaded to Codecov). Use `--coverage-formats html` to get a
browsable HTML report instead, or pass several fo