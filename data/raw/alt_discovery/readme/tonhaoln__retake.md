# Retake: a free alternative to Screen Studio

[![tests](https://github.com/tonhaoln/retake/actions/workflows/test.yml/badge.svg)](https://github.com/tonhaoln/retake/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Claude wrote most of the code. The design decisions, the rejections and the
taste are mine — that was the experiment.

A free, two-part replacement for Screen Studio:

1. **Recorder** (`retake`) — a tiny native macOS tool that records your screen
   *without* the cursor, logs every cursor movement and click, and can record your
   webcam + microphone at the same time. Everything lands in one `.take` folder.
2. **Editor** (`retake-editor.html`) — one HTML file that runs in Chrome. Nothing to
   install, no server, no account, works offline. Drop the `.take` folder in, press
   **Auto** and it builds zoom-ins from your clicks, redraws a buttery-smooth cursor,
   adds the gradient framing / rounded corners / shadow, overlays your webcam bubble,
   and exports a polished MP4. It is one readable file, so you can check for yourself
   that nothing leaves your machine.

The editor also accepts **any plain video** (QuickTime recordings, OBS captures…) —
without auto-zoom or the redrawn cursor, which need the recorder's data.

The recorder is macOS only. The editor is a plain HTML file, so it runs anywhere a
browser does.

---

## Install

    curl -fsSL https://raw.githubusercontent.com/tonhaoln/retake/main/install.sh | sh

That downloads the latest release, puts `retake` in `/usr/local/bin` and the
editor in `~/Applications/Retake`, and stops. [Read the script first](install.sh)
— it is short and there is no checksum step, so read it rather than trusting it.

The binary is not notarised by Apple. Two consequences worth knowing: a
tarball downloaded in a **browser** gets quarantined by macOS — the `curl`
line above does not — and macOS re-asks for permissions after each update.

### Updating

Run the install command again — it downloads the latest release and replaces
both files. Retake never checks for updates itself (no network code is the
point), so updating is always your move. macOS will re-ask for permissions
after an update; that's the signature changing, not a fault.

### Permissions (first run)

The first time you record, macOS will ask (or silently block) until
you grant your terminal app (Terminal / iTerm / Warp) these, under
**System Settings → Privacy & Security**:

- **Screen Recording** — required, for the capture itself
- **Accessibility** — recommended, for clicks (that's what powers auto-zoom) and the ⌃⎋ stop hotkey
- **Camera / Microphone** — only if you use `--webcam` / `--mic`

After granting Screen Recording you must quit and reopen the terminal app once.

What Accessibility actually grants, said plainly: while a recording runs, macOS
hands Retake every click and keypress on the machine, not only the app you are
recording. Retake keeps click positions and the *times* of keypresses. It never
keeps which key, unless you pass `--keys`. Details in [Privacy](#privacy).

The agent path's programs live under `agent/` (see "Let an agent make the
demo" below). One of them is a small driver that *posts* mouse and key events
so an agent can drive a demo with the real pointer. Posting needs Accessibility
for the app hosting the agent, and it is a separate program from the recorder
on purpose: the recorder only watches, and that stays true.

### Or build it yourself (about 2 minutes)

You need Apple's command line tools (free). If you don't have them:

    xcode-select --install

Then build the recorder:

    cd Recorder
    swift build -c release
    sudo mkdir -p /usr/local/bin
    sudo cp .build/release/retake /usr/local/bin/

## Recording

    retake                    # main display + system audio
    retake --webcam           # + webcam bubble + mic
    retake --mic              # + mic voiceover, no webcam
    retake --window safari    # record one window (see --list for names)
    retake --area 100,80,1280,720   # record a region — x, y, width, height from the top-left
    retake --display 1        # record your second display
    retake --list             # show displays and windows
    retake --keys             # ALSO record which keys you press (see below)
    retake --no-system-audio  # skip app/system sound
    retake --no-notify        # skip the "Saved" notification
    retake --fps 30           # lighter files
    retake --out ~/Movies     # save somewhere other than ~/Desktop/Retake
    retake --json             # for scripts and agents: JSON events on stdout (see below)

With `--webcam` or `--mic`, Retake switches the camera on first and waits for
you to press **Enter**. A camera takes about a second to wake up, and this way
that second happens before the recording rather than inside it — so your take
starts when you do. (Scripts aren't prompted.) Plain `retake` starts straight away.

Stop with **Ctrl+C** in the terminal — or **⌃⎋ (Control+Escape)** from any app.
You get a folder like `~/Desktop/Retake/2026-07-29 14.03.12.take` containing
the raw video (with system audio), cursor data, and webcam/mic track.

One thing about `--window`: don't move the window mid-recording — the cursor
is logged against where the window started.

If something goes wrong mid-recording — you close the terminal, the machine
gives up, you force-quit — the take survives. Closing the terminal stops it
cleanly; a hard crash costs you the last few seconds, not the whole session.

Privacy note: by default the recorder logs *when* keys are pressed but never
*which* keys. Full detail in [Privacy](#privacy) below.

**Driving it from a script.** `retake record --json` (or `retake --json`) keeps
stdout for machines: one line `{"event":"recording","take":"…","width":…,"height":…,"fps":…}`
when capture starts and one `{"event":"saved","take":"…","droppedFrames":0}` when it
stops (or `{"event":"error",…}` and a non-zero exit if the reco