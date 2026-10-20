# write good [![Build Status](https://travis-ci.org/btford/write-good.svg?branch=master)](https://travis-ci.org/btford/write-good)

Naive linter for English prose for developers who can't write good and wanna learn to do other stuff good too.


## Use

```shell
npm install write-good
```

**Important:** Do not use this tool to be a jerk to other people about their writing.


## API

`writeGood` is a function that takes a string and returns an array of suggestions.

```javascript
var writeGood = require('write-good');

var suggestions = writeGood('So the cat was stolen.');

// suggestions:
//
// [{
//   reason: "omit 'So' from the beginning of sentences",
//   index: 0, offset: 2
// }, {
//   reason: "'was stolen' is passive voice",
//   index: 11, offset: 10
// }]
```

`writeGood` takes an optional second argument that allows you to disable certain checks.

You can disable checking for passive voice like this:

```javascript
var writeGood = require('write-good');

var suggestions = writeGood('So the cat was stolen', { passive: false });
// suggestions: []
```

You can use the second argument's `checks` property to pass in custom checks instead of `write-good`'s default linting configuration.
Like this, you can check non-English documents, for example with the linter extension for German, [schreib-gut](https://github.com/TimKam/schreib-gut):


```javascript
var schreibGut = require('schreib-gut');

writeGood('Aller Wahrscheinlichkeit nach können Entwickler nicht gut schreiben', { weasel-words: false, checks: schreibGut });

// suggestions
// [{index : 0, offset : 29, reason : '"Aller Wahrscheinlichkeit nach" is wordy or unneeded' }]
```

You can use the second argument's `whitelist` property to pass in a list of strings to whitelist from suggestions.
For example, normally `only` would be picked up as a bad word to use, but you might want to exempt `read-only` from that:

```javascript
var writeGood = require('write-good');

var suggestions = writeGood('Never write read-only sentences.');
// suggestions: [{ index: 17, offset: 4, reason: '"only" can weaken meaning' }]

var filtered = writeGood('Never write read-only sentences.', { whitelist: ['read-only'] });
// filtered: []

```

## CLI

You can use `write-good` as a command-line tool by installing it globally:

```shell
npm install -g write-good
```

If you have npm version 5.2.0 or later installed, you can use npx to run write-good without installing it:

```shell
npx write-good *.md
```

`write-good` takes a [glob](https://github.com/isaacs/node-glob) and prints suggestions to stdout:

```shell
$ write-good *.md

In README.md
=============
 = writeGood('So the cat was stolen.');
                         ^^^^^^^^^^
"was stolen" is passive voice on line 20 at column 40
-------------
//   suggestion: "'was stolen' is passive voice",
                   ^^^^^^^^^^
"was stolen" is passive voice on line 28 at column 19
```

You can run just specific checks like this:

```shell
write-good *.md --weasel --so
```

Or exclude checks like this:

```shell
write-good *.md --no-passive
```

Or include checks like this:

```shell
# E-Prime is disabled by default.
write-good *.md --yes-eprime
```

**Note:** The ``--yes`` prefix only works for *E-Prime*, because the other checks are included by default, anyway.

You can run just with text without supplying files:

```shell
write-good --text="It should have been defined there."
```

You can even supply multi-line text:

```shell
write-good --text="I can't see a problem there that's not been defined yet.
Should be defined again."
```

You can also pass other arguments:

```shell
write-good --text="It should have been defined there." --no-passive
```

You can even fetch output from a remote file:

```shell
write-good --text="$(curl https://raw.githubusercontent.com/btford/write-good/master/README.md)"
```

Use the ``--parse`` option to activate parse-happy output and a more conventional Unix exit code:

```shell
write-good *.md --parse
```

To specify a custom checks extension, for example [schreib-gut](https://github.com/TimKam/schreib-gut), run:

```shell
npm install -g schreib-gut
write-good *.md --checks=schreib-gut
```

To view all available options use the ``--help`` option:

```shell
write-good --help
```

## Checks

You can disable any combination of the following by providing a key with value `false` as the second argument to `writeGood`.

### `passive`
Checks for passive voice.

### `illusion`
Checks for lexical illusions – cases where a word is repeated.

### `so`
Checks for `so` at the beginning of the sentence.

### `thereIs`
Checks for `there is` or `there are` at the beginning of the sentence.

### `weasel`
Checks for "weasel words."

### `adverb`
Checks for adverbs that can weaken meaning: really, very, extremely, etc.

### `tooWordy`
Checks for wordy phrases and unnecessary words.

### `cliches`
Checks for common cliches.

### `eprime`
Checks for ["to-be"](https://en.wikipedia.org/wiki/E-Prime) verbs. _Disabled by default_

## Extensions
Users can create their own `write-good` language checks. As described above,
you can specify such extensions when running `write-good` on the command line
or calling it in your JavaScript code.

The following 3rd-party `write-good` extensions are available:

* [schreib-gut](https://github.com/timkam/schreib-gut): A basic extension for
  the German language

If you know of any `write-good` extensions that are not in this list, please open a pull request!

### Interface
An extension is a Node.js module that exposes an object containing a check
function (``fn``) and an ``explanation`` string for each new check:

```javascript
module.exports = {
  check1: {
    fn: function(text) {
      …
    },
    explanation: '…'
  },
  check2: {
    fn: function(text) {
      …
    },
    explanation: '…'
  }
}
```

Each check function takes a string input and determines a list of style
violation objects, each with an ``index`` and an ``offset``:

```javascript
/**
* @para