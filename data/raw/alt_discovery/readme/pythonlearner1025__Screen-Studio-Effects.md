# screen-studio-effects

Open-source auto-zoom and physics-based frame settling algorithms for building Screen Studio-style animated screen recordings.

No UI, no video processing — just the core math. Bring your own renderer.

<video src="https://github.com/user-attachments/assets/729008f7-b79e-4ee2-bbe4-9c5cee0a3601" autoplay loop muted playsinline></video>

## What this does

Screen Studio's signature effect: the camera **smoothly zooms in** when you're clicking and typing, **follows your cursor** with spring physics, and **zooms out** during pauses. This repo contains the algorithms that make that work.

### The pipeline

```
Raw cursor events
  → Shake filter (remove jitter)
  → Densify (fill time gaps)
  → Spring simulation (smooth trajectory)
  → Auto-zoom detection (silence analysis)
  → Per-frame crop evaluation (spring-animated viewport)
```

### Key techniques

**Spring-mass-damper physics** — All animations use exact analytical solutions to the damped harmonic oscillator ODE (not Euler/RK4). This means:
- Stable at any frame rate
- Frame-rate-independent results
- Three regimes: underdamped (bouncy), critically damped (fast settle), overdamped (slow settle)

**Cursor smoothing** — Three spring profiles switch based on interaction context:
- `default` (tension=170, friction=20): natural follow
- `snappy` (tension=700, friction=30): tight response within 160ms of clicks
- `drag` (tension=136, friction=26): heavier feel during mouse drag

**Viewport panning** — The viewport locks on segment entry and only pans when the cursor exits a "safe zone" (inner 70%). Before panning:
1. **Lookahead jitter cancellation**: checks 1 second ahead — if the cursor returns to the safe zone, the pan is skipped
2. **Trajectory-averaged targeting**: the pan target is averaged over 0.5s of future cursor positions

**Zoom transitions** — Spring easing between zoom levels with different curves for zoom-in (slightly bouncy) vs zoom-out (softer, more damped).

## Install

```bash
npm install screen-studio-effects
```

## Usage

```ts
import {
  buildSmoothedCursor,
  detectSilenceZones,
  generateAutoZoomSegments,
  createZoomState,
  evaluateZoom,
  VP_PRESETS,
} from 'screen-studio-effects'

// 1. Smooth raw cursor events into a precomputed trajectory
const cursor = buildSmoothedCursor(rawCursorEvents, {
  windowX: 0,        // window origin in screen coords
  windowY: 0,
  captureWidth: 3840, // capture dimensions in pixels
  captureHeight: 2160,
})

// 2. Auto-detect where to zoom based on cursor activity
const silences = detectSilenceZones(rawCursorEvents)
const segments = generateAutoZoomSegments(silences, totalDurationSecs)

// Or define segments manually:
// const segments = [
//   { sourceStart: 2.0, sourceEnd: 5.0, amount: 2.0 },
//   { sourceStart: 7.0, sourceEnd: 9.0, amount: 1.5, manualCenter: [0.3, 0.4] },
// ]

// 3. Evaluate per frame — returns crop bounds in UV space [0,1]
const state = createZoomState()

for (const frame of frames) {
  const pos = cursor.interpolateAt(frame.time)
  const crop = evaluateZoom(
    segments,
    frame.time,
    pos,
    state,
    (t) => cursor.interpolateAt(t),  // lookahead for jitter cancellation
    VP_PRESETS.focused,               // or VP_PRESETS.smooth
  )

  // crop = { x, y, w, h } in normalized 0-1 space
  // Full frame: { x:0, y:0, w:1, h:1 }
  // 2x zoom centered: { x:0.25, y:0.25, w:0.5, h:0.5 }

  // Apply to your renderer:
  // const srcRect = {
  //   x: crop.x * sourceWidth,
  //   y: crop.y * sourceHeight,
  //   w: crop.w * sourceWidth,
  //   h: crop.h * sourceHeight,
  // }
}
```

## API

### Cursor smoothing

| Function | Description |
|---|---|
| `buildSmoothedCursor(events, transform)` | Build precomputed spring-smoothed cursor. Returns `SmoothedCursor` with `interpolateAt(t)` and `isClickingAt(t)`. |
| `screenToVideoUV(x, y, transform)` | Convert screen coordinates to video UV space. |

### Auto-zoom detection

| Function | Description |
|---|---|
| `detectSilenceZones(events, minSilenceSecs?)` | Find periods where cursor is stationary (< 2px displacement, >= 0.5s). |
| `generateAutoZoomSegments(silences, totalDuration, zoomAmount?)` | Convert silence gaps into zoom segments for active regions. |

### Zoom evaluation

| Function | Description |
|---|---|
| `evaluateZoom(segments, time, cursor?, state?, lookahead?, springConfig?)` | Per-frame crop bounds with spring-animated transitions. |
| `createZoomState()` | Create persistent state for `evaluateZoom`. |
| `VP_PRESETS` | Built-in spring configs: `focused` (snappy) and `smooth` (cinematic). |

### Spring physics

| Function | Description |
|---|---|
| `solveSpring1d(disp, vel, t, omega0, zeta)` | Exact 1D spring-mass-damper solution. Returns `[displacement, velocity]`. |
| `stepSpring2D(state, dtMs, config)` | Step a 2D spring simulation forward by dt milliseconds. |

## Spring tuning guide

The spring feel is controlled by three parameters:

| Parameter | Effect | Higher = |
|---|---|---|
| `tension` | Stiffness | Faster response, more overshoot |
| `mass` | Inertia | Slower, heavier, more overshoot |
| `friction` | Damping | Less oscillation, slower settling |

The **damping ratio** ζ = friction / (2 * √(tension * mass)) determines the character:
- ζ < 1: **Underdamped** — bouncy, oscillates around target
- ζ ≈ 1: **Critically damped** — fastest approach without oscillation
- ζ > 1: **Overdamped** — slow, no oscillation

Built-in presets:

```ts
// Viewport panning springs
VP_PRESETS.focused  = { tension: 300, mass: 6.75, friction: 120 }  // ζ ≈ 1.33
VP_PRESETS.smooth   = { tension: 240, mass: 3.375, friction: 80 }  // ζ ≈ 1.40

// Cursor smoothing springs
SPRING_DEFAULT = { tension: 170, mass: 1.0,  friction: 20 }  // ζ ≈ 0.77 (bouncy)
SPRING_SNAPPY  = { tension: 700, mass: 1.0,  friction: 30 }  // ζ ≈ 0.57 (very bouncy, fast)
SPRING_DRAG    = { tension: 136, mass: 1.2,  friction: 26 }  // ζ ≈ 1.02 (critically damped)
```

## Rust reference implementation

A standalone Rust 