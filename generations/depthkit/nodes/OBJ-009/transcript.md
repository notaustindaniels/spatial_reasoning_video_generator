# Deliberation Transcript: OBJ-009

---

## Round 1 — spec_author

Looking at OBJ-009's metadata and the file assignments from OBJ-001, I need to reconcile an apparent tension: the metadata description says "Virtualized clock — pure utility," but OBJ-001 assigns `puppeteer-bridge.ts`, `page/index.html`, and `page/message-handler.js` to OBJ-009. Let me read the existing codebase to understand what's already in place.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-009/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-010/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/engine/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/page/**/*"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md"
}
[Tool Result]      1→# Specification: OBJ-010 — Three.js Page Shell, Build/Bundle Architecture, and Scene Renderer Skeleton
     2→
     3→## Summary
     4→
     5→OBJ-010 establishes the browser-side rendering foundation and the authoritative Node.js/browser code-split architecture for depthkit. It delivers: (1) the final HTML page shell with a properly sized WebGL canvas, (2) the Three.js `Scene` / `PerspectiveCamera` / `WebGLRenderer` initialization skeleton that all downstream rendering depends on, (3) the architectural decision that the browser page is a **data-driven renderer** — a "dumb page" that receives computed scene state from the Node.js orchestrator and executes Three.js calls accordingly, and (4) a minimal `renderFrame()` primitive that downstream objectives build upon. This objective also defines Node-side TypeScript types for data crossing the Node/browser boundary (excluding geometry serialization, which is deferred to OBJ-011).
     6→
     7→## Interface Contract
     8→
     9→... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-009",
     3→  "description": "Virtualized clock -- global frame-to-timestamp mapping (t = frame / fps), frame counter mechanics, deterministic frame stepping guarantee per C-03. Pure utility with no scene awareness. The clock provides the global frame number and timestamp; per-scene normalized time computation is handled by the scene sequencer (OBJ-036). Ensures zero dropped frames regardless of scene complexity or hardware speed.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Narrowed to pure global clock -- per-scene time normalization moved to OBJ-036."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-011/meta.json"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-035/meta.json"
}
[Tool Result] No files found
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-038/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-011",
     3→  "description": "Full Puppeteer-to-page message protocol -- defines every message type crossing the Node.js/browser boundary. Includes: frame step commands (frame number, fps, totalFrames), scene setup/teardown commands (geometry instantiation, texture URLs, slot assignments), texture loading completion signals, transition signals (prepare next scene, start overlap rendering), and error reporting from page back to orchestrator. Single source of truth for the cross-boundary contract.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-010", "OBJ-005"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Expanded scope per Round 2 Issue 7 to cover full protocol, not just frame stepping. Depends on OBJ-005 for geometry slot structures in sce... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-035",
     3→  "description": "Orchestrator -- the main render loop coordinating Puppeteer, FFmpeg, and the virtualized clock per Section 4.4 steps 1-5. Spawns Puppeteer and FFmpeg child process, iterates through frames, sends frame commands to the page, waits for render completion, captures pixels, pipes to FFmpeg, closes stdin when done. Implements C-02 (Puppeteer+Three.js+FFmpeg pipeline) and C-03 (deterministic virtualized timing) at the integration level.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-012", "OBJ-013", "OBJ-016"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration. The central coordination point -- most Tier 4+ objectives depend on this."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-038",
     3→  "description": "Audio sync and scene timing -- duration distribution algorithm per Section 8.7: audio-driven (T = audio_duration, scenes share proportionally), explicit (T = sum of scene durations + transition overlaps), or combined (explicit durations with audio mismatch warning). Timestamp-based scene boundary alignment to narration cues. Covers C-07 (audio synchronization) and TC-13 (audio duration drives total video length).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-014", "OBJ-016"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration."
    12→}
    13→
Now I have full context. Let me understand the picture:

- **OBJ-010** (verified) created the Three.js page shell (`window.depthkit` API, `scene-renderer.js`, `page-types.ts`). It explicitly says OBJ-009 is the "Puppeteer bridge."
- **OBJ-009** metadata says "Virtualized clock — frame-to-timestamp mapping, frame counter mechanics."
- **OBJ-001** assigns `puppeteer-bridge.ts` to OBJ-009 and `frame-clock.ts` to OBJ-010 (but OBJ-010 was re-scoped to the page shell, so `frame-clock.ts` needs a home).
- **OBJ-011** (depends on OBJ-009) builds the full message protocol ON TOP of the bridge.
- **OBJ-035** (depends on OBJ-009) is the orchestrator that uses the bridge and clock.

OBJ-009 delivers two modules: the **FrameClock** (pure utility) and the **PuppeteerBridge** (enforcement mechanism for the virtualized clock). Let me propose the spec.

---

# Specification Proposal: OBJ-009 — Virtualized Clock and Puppeteer Bridge

## Summary

OBJ-009 delivers two modules that together implement the virtualized clock mechanism defined in C-03. First, `FrameClock` (`src/engine/frame-clock.ts`) — a pure, stateless utility that maps frame numbers to timestamps and provides an iterator for deterministic frame stepping. It has no scene awareness; per-scene normalized time is OBJ-036's responsibility. Second, `PuppeteerBridge` (`src/engine/puppeteer-bridge.ts`) — the Puppeteer lifecycle manager that launches headless Chromium, loads the OBJ-010 page shell, exposes an `evaluate()` primitive for downstream message protocols (OBJ-011), and captures rendered frames as pixel buffers via CDP. Together, these two modules provide the building blocks that OBJ-035 (orchestrator) composes into the deterministic render loop from seed Section 4.4.

## Interface Contract

### Module: `src/engine/frame-clock.ts`

```typescript
/**
 * Configuration for creating a FrameClock.
 */
export interface FrameClockConfig {
  /** Frames per second. Must be a positive finite number. */
  fps: number;
  /** Total number of frames in the composition. Must be a positive integer. */
  totalFrames: number;
}

/**
 * Information about a single frame tick.
 * Yielded by FrameClock.frames() iterator.
 */
export interface FrameTick {
  /** Zero-indexed frame number: 0 to totalFrames - 1 */
  frame: number;
  /** Absolute timestamp in seconds: frame / fps */
  timestamp: number;
  /** Whether this is the first frame (frame === 0) */
  isFirst: boolean;
  /** Whether this is the last frame (frame === totalFrames - 1) */
  isLast: boolean;
}

/**
 * Pure, immutable utility for deterministic frame-to-timestamp mapping.
 * No I/O, no scene awareness, no side effects.
 *
 * The clock defines the global temporal coordinate system for a composition.
 * It does NOT compute per-scene normalized time — that is OBJ-036's
 * responsibility using the clock's frame/timestamp outputs as inputs.
 */
export class FrameClock {
  /** Frames per second. */
  readonly fps: number;
  /** Total number of frames in the composition. */
  readonly totalFrames: number;
  /** Total duration in seconds: totalFrames / fps */
  readonly duration: number;
  /** Duration of a single frame in seconds: 1 / fps */
  readonly frameDuration: number;

  constructor(config: FrameClockConfig);

  /**
   * Convert a frame number to an absolute timestamp in seconds.
   * @param frame — Zero-indexed frame number.
   * @returns timestamp in seconds (frame / fps).
   * @throws RangeError if frame < 0 or frame >= totalFrames or not an integer.
   */
  frameToTimestamp(frame: number): number;

  /**
   * Convert an absolute timestamp (seconds) to the nearest frame number.
   * Uses Math.round(), then clamps to [0, totalFrames - 1].
   * @param timestamp — Time in seconds.
   * @returns frame number (integer, clamped).
   * @throws RangeError if timestamp is negative.
   */
  timestampToFrame(timestamp: number): number;

  /**
   * Generator that yields FrameTick objects for every frame from 0
   * to totalFrames - 1, in order. This is the canonical iteration
   * primitive for the render loop.
   *
   * Usage:
   *   for (const tick of clock.frames()) {
   *     // render tick.frame at tick.timestamp
   *   }
   */
  frames(): Generator<FrameTick, void, undefined>;

  /**
   * Static factory: create a FrameClock from a duration in seconds.
   * totalFrames = Math.ceil(durationSeconds * fps).
   *
   * @param fps — Frames per second.
   * @param durationSeconds — Desired duration in seconds. Must be positive.
   * @returns FrameClock instance.
   */
  static fromDuration(fps: number, durationSeconds: number): FrameClock;
}
```

### Module: `src/engine/puppeteer-bridge.ts`

```typescript
import type { Page, Browser } from 'puppeteer';
import type { PageInitConfig, RendererInfo } from './page-types.js';

/**
 * Configuration for launching the PuppeteerBridge.
 */
export interface PuppeteerBridgeConfig {
  /** Viewport width in pixels. Must match composition width. */
  width: number;
  /** Viewport height in pixels. Must match composition height. */
  height: number;
  /**
   * Absolute path to the built page directory containing index.html
   * and scene-renderer.js. Defaults to dist/page/ relative to the
   * package root, resolved at runtime.
   */
  pagePath?: string;
  /**
   * Headless mode. Default: true.
   * Set to false for debugging (opens visible browser window).
   */
  headless?: boolean;
  /**
   * Path to a custom Chromium/Chrome executable.
   * If not provided, uses Puppeteer's bundled Chromium.
   */
  executablePath?: string;
  /**
   * Enable GPU-accelerated rendering. Default: false.
   *
   * When false (default): adds --disable-gpu and related flags
   * for software rendering via SwiftShader (C-11 compliance).
   *
   * When true: omits GPU-disabling flags, allowing hardware
   * acceleration when available. Faster but requires GPU passthrough
   * in Docker/CI environments.
   */
  gpu?: boolean;
  /**
   * Additional Chromium launch arguments.
   * Appended after the bridge's default arguments.
   */
  extraArgs?: string[];
}

/**
 * Supported formats for frame capture.
 * 'png' — Lossless, larger buffers, guaranteed determinism (C-05).
 * 'raw' — Raw RGBA pixel data, fastest for FFmpeg piping.
 *         Returned as a Buffer of width * height * 4 bytes.
 */
export type CaptureFormat = 'png' | 'raw';

/**
 * Manages the Puppeteer lifecycle for depthkit's rendering pipeline.
 *
 * Responsibilities:
 * - Launch headless Chromium with correct flags for WebGL rendering.
 * - Load the depthkit page shell (OBJ-010's index.html + scene-renderer.js).
 * - Set viewport to match composition dimensions exactly.
 * - Provide evaluate() for downstream message protocols (OBJ-011).
 * - Capture rendered frames as pixel buffers via CDP.
 * - Clean up browser resources on close.
 *
 * The bridge is the enforcement mechanism for the virtualized clock (C-03):
 * it never uses requestAnimationFrame or wall-clock timing. The caller
 * (orchestrator, OBJ-035) controls when each frame is rendered by calling
 * evaluate() to send frame commands, then captureFrame() to extract pixels.
 */
export class PuppeteerBridge {
  constructor(config: PuppeteerBridgeConfig);

  /**
   * Launch headless Chromium, create a page, set viewport, and load
   * the depthkit page shell (index.html).
   *
   * Postconditions:
   * - Browser is running.
   * - Page is loaded and scene-renderer.js has executed.
   * - Viewport is set to config.width x config.height with deviceScaleFactor=1.
   * - window.depthkit is available on the page.
   *
   * @throws Error if browser fails to launch.
   * @throws Error if page fails to load or scene-renderer.js errors.
   * @throws Error if already launched (call close() first).
   */
  launch(): Promise<void>;

  /**
   * Execute a function in the browser page context.
   * Thin wrapper around Puppeteer's page.evaluate().
   *
   * This is the primitive that OBJ-011 builds its message protocol on.
   * The orchestrator (OBJ-035) uses it via OBJ-011's higher-level API.
   *
   * @param pageFunction — Function or string to evaluate in the page.
   * @param args — Serializable arguments passed to the function.
   * @returns The serializable return value from the page function.
   * @throws Error if not launched.
   * @throws Error if the page function throws (error is propagated).
   */
  evaluate<T>(
    pageFunction: string | ((...args: any[]) => T),
    ...args: any[]
  ): Promise<T>;

  /**
   * Capture the current state of the page viewport as a pixel buffer.
   *
   * Uses CDP Page.captureScreenshot for 'png' format.
   * Uses CDP + canvas pixel extraction for 'raw' format.
   *
   * The caller is responsible for ensuring the frame has been rendered
   * (via evaluate() + renderFrame()) before calling captureFrame().
   * This method captures whatever is currently on the canvas.
   *
   * @param format — Capture format. Default: 'png'.
   * @returns Buffer containing the frame data.
   * @throws Error if not launched.
   */
  captureFrame(format?: CaptureFormat): Promise<Buffer>;

  /**
   * Close the browser and release all resources.
   * Idempotent — safe to call multiple times.
   *
   * After close(), launch() can be called again.
   */
  close(): Promise<void>;

  /**
   * Whether the bridge has been launched and is ready.
   */
  readonly isLaunched: boolean;

  /**
   * The underlying Puppeteer Page instance.
   * Exposed for advanced use by OBJ-011 (e.g., page.on('console')).
   * null before launch() or after close().
   */
  readonly page: Page | null;
}
```

## Design Decisions

### D1: Two Modules, Clean Separation

**Decision:** OBJ-009 delivers two separate modules: `FrameClock` (pure math) and `PuppeteerBridge` (I/O + browser lifecycle). They do not import each other.

**Rationale:** The frame clock is consumed by OBJ-035 (orchestrator) and OBJ-038 (audio sync) for timestamp computation. The Puppeteer bridge is consumed by OBJ-035 and OBJ-011. Keeping them separate honors the "pure utility with no scene awareness" description for the clock, while cleanly isolating all Puppeteer I/O concerns. OBJ-035 composes them: it creates a `FrameClock`, iterates its `frames()`, and for each tick calls `bridge.evaluate()` + `bridge.captureFrame()`.

### D2: FrameClock is Immutable and Stateless

**Decision:** `FrameClock` is constructed with `fps` and `totalFrames`, then never changes. It has no internal cursor or mutable state. The `frames()` generator is a fresh iterator each time, producing frame ticks without side effects.

**Rationale:** The clock is a **coordinate system**, not a ticker. It maps between frame numbers and timestamps. Statefulness (tracking "current frame") belongs to the orchestrator (OBJ-035), which may need to render frames out of order for parallelization (seed C-08 mentions splitting frame ranges). A stateless clock supports any iteration pattern.

**Alternative considered:** A stateful clock with `advance()` / `currentFrame` API. Rejected because it couples the clock to sequential iteration, making parallelized rendering harder.

### D3: Frame Numbers are Zero-Indexed

**Decision:** Frame 0 is the first frame. Frame `totalFrames - 1` is the last frame. `frameToTimestamp(0) = 0.0`. `frameToTimestamp(totalFrames - 1) = (totalFrames - 1) / fps`.

**Rationale:** Zero-indexing is conventional for frame ranges in video pipelines and aligns with FFmpeg's frame numbering. The last frame's timestamp is `(totalFrames - 1) / fps`, NOT `totalFrames / fps` (which would be one frame past the end).

### D4: `timestampToFrame()` Uses `Math.round()` with Clamping

**Decision:** `timestampToFrame()` converts seconds to a frame via `Math.round(timestamp * fps)`, then clamps to `[0, totalFrames - 1]`.

**Rationale:** `Math.round()` produces the frame whose timestamp is nearest to the input. Clamping prevents out-of-range indices. This is used by OBJ-038 (audio sync) to convert narration cue timestamps to frame boundaries.

### D5: `fromDuration()` Uses `Math.ceil()`

**Decision:** `FrameClock.fromDuration(fps, durationSeconds)` computes `totalFrames = Math.ceil(durationSeconds * fps)`.

**Rationale:** `Math.ceil()` ensures the video duration is at least as long as the requested duration. A 10-second video at 30fps = 300 frames, covering `[0, 9.967s]`. With `Math.ceil()`, 10.01 seconds → 301 frames, ensuring the last moment is captured. `Math.floor()` would truncate, potentially cutting off the end of audio (violating C-07). `Math.round()` could go either way, making behavior unpredictable at boundaries.

### D6: PuppeteerBridge Provides Raw Primitives, Not Domain Logic

**Decision:** The bridge exposes `evaluate()` and `captureFrame()` — raw primitives. It does NOT expose `renderFrame()`, `initScene()`, or any depthkit-specific operations. Those are defined by OBJ-011 (message protocol) using `evaluate()` as the transport.

**Rationale:** OBJ-011 owns the full cross-boundary message contract. If the bridge pre-defined `renderFrame()`, it would duplicate OBJ-011's responsibility and couple the bridge to the page API. The bridge is a transport layer; OBJ-011 defines the protocol; OBJ-035 orchestrates.

**Exception:** `launch()` loads the page and verifies `window.depthkit` exists — this minimal check ensures the page shell (OBJ-010) loaded correctly, without coupling to its internal API.

### D7: CDP `Page.captureScreenshot` for PNG Capture

**Decision:** PNG capture uses CDP's `Page.captureScreenshot` method (via Puppeteer's `page.screenshot()`), which captures the full viewport.

**Rationale:** CDP screenshot is the most reliable capture method — it works regardless of `preserveDrawingBuffer`, captures the composited page (including future HUD layers), and returns a PNG Buffer directly. For `raw` format, the bridge uses `page.evaluate()` to extract RGBA pixels from the canvas via `getImageData()`, which requires `preserveDrawingBuffer: true` (set by OBJ-010's defaults).

### D8: Software Rendering by Default (C-11)

**Decision:** Default launch args include `--disable-gpu` for software rendering. A `gpu: true` config option omits this flag.

**Rationale:** C-11 mandates software rendering correctness. The engine must run in Docker without GPU passthrough. SwiftShader (Chromium's software WebGL) is available by default in Puppeteer's bundled Chromium. GPU acceleration is opt-in for environments where it's available.

**Default Chromium args:**
```
--disable-gpu              // Software WebGL (SwiftShader)
--disable-dev-shm-usage    // Docker: use /tmp instead of /dev/shm
--no-sandbox               // Docker: required when running as root
--disable-setuid-sandbox   // Docker: companion to --no-sandbox
--hide-scrollbars          // Prevent scrollbar interference
--mute-audio               // No audio output from browser
```

When `gpu: true`, `--disable-gpu` is omitted; all other args remain.

### D9: Viewport `deviceScaleFactor: 1`

**Decision:** The Puppeteer viewport is always set with `deviceScaleFactor: 1`.

**Rationale:** Combined with OBJ-010's `renderer.setPixelRatio(1)`, this ensures 1:1 pixel mapping. A 1920×1080 viewport produces a 1920×1080 screenshot. HiDPI scaling would silently double the resolution, breaking FFmpeg encoding and violating C-05 (deterministic output).

### D10: Page Loading via `file://` Protocol

**Decision:** The bridge loads `index.html` via `file://` protocol using `page.goto('file://...')`.

**Rationale:** The built page is self-contained — `index.html` loads `scene-renderer.js` (esbuild bundle with Three.js inlined). No network requests needed for page load. `file://` avoids the complexity of spinning up a local HTTP server.

**Known constraint:** Three.js `TextureLoader` uses `fetch()`, which may fail with `file://` due to CORS. This is OBJ-011/OBJ-015's concern — they will likely load textures by passing image data through `page.evaluate()` rather than via URL fetch. Documented here so downstream consumers are aware.

### D11: Bridge Validates Page Load

**Decision:** After `page.goto()`, the bridge verifies that `window.depthkit` is defined on the page. If not, `launch()` throws with a descriptive error.

**Rationale:** Catches build failures (missing bundle, esbuild errors) at bridge launch time rather than later when `evaluate()` calls fail with cryptic "depthkit is not defined" errors.

## Acceptance Criteria

- [ ] **AC-01:** `FrameClock` is importable from `src/engine/frame-clock.ts`. `new FrameClock({ fps: 30, totalFrames: 900 })` creates an instance with `fps === 30`, `totalFrames === 900`, `duration === 30.0`, `frameDuration` approximately `0.03333`.
- [ ] **AC-02:** `clock.frameToTimestamp(0) === 0.0`. `clock.frameToTimestamp(899)` approximately equals `29.9667` (899/30). `clock.frameToTimestamp(450)` equals `15.0`.
- [ ] **AC-03:** `clock.timestampToFrame(0) === 0`. `clock.timestampToFrame(15.0) === 450`. `clock.timestampToFrame(30.0)` clamps to `899` (not 900).
- [ ] **AC-04:** `clock.frameToTimestamp(-1)` throws `RangeError`. `clock.frameToTimestamp(900)` throws `RangeError` (for a 900-frame clock). `clock.frameToTimestamp(1.5)` throws `RangeError` (non-integer).
- [ ] **AC-05:** `clock.timestampToFrame(-0.1)` throws `RangeError`.
- [ ] **AC-06:** `FrameClock.fromDuration(30, 10.0)` creates a clock with `totalFrames === 300`. `FrameClock.fromDuration(30, 10.01)` creates a clock with `totalFrames === 301`.
- [ ] **AC-07:** `Array.from(clock.frames())` for a 3-frame clock produces `[{ frame: 0, timestamp: 0, isFirst: true, isLast: false }, { frame: 1, timestamp: 1/fps, isFirst: false, isLast: false }, { frame: 2, timestamp: 2/fps, isFirst: false, isLast: true }]`.
- [ ] **AC-08:** `new FrameClock({ fps: 0, totalFrames: 100 })` throws (fps must be positive). `new FrameClock({ fps: 30, totalFrames: 0 })` throws (totalFrames must be positive integer). `new FrameClock({ fps: -1, totalFrames: 100 })` throws. `new FrameClock({ fps: 30, totalFrames: 1.5 })` throws.
- [ ] **AC-09:** `PuppeteerBridge` is importable from `src/engine/puppeteer-bridge.ts`.
- [ ] **AC-10:** After `bridge.launch()`, `bridge.isLaunched === true` and `bridge.page` is a non-null Puppeteer `Page` instance.
- [ ] **AC-11:** After `bridge.launch()`, `bridge.evaluate(() => typeof window.depthkit)` resolves to `'object'`.
- [ ] **AC-12:** After launching and calling `window.depthkit.init()` via `evaluate()`, `bridge.captureFrame('png')` returns a `Buffer` whose first 8 bytes are the PNG magic number (`\x89PNG\r\n\x1a\n`).
- [ ] **AC-13:** After launching, `bridge.captureFrame('raw')` returns a `Buffer` of exactly `width * height * 4` bytes.
- [ ] **AC-14:** `bridge.close()` terminates the browser process. `bridge.isLaunched === false` and `bridge.page === null` after close.
- [ ] **AC-15:** `bridge.close()` is idempotent — calling it twice does not throw.
- [ ] **AC-16:** `bridge.evaluate()` before `launch()` throws with message containing "not launched".
- [ ] **AC-17:** `bridge.captureFrame()` before `launch()` throws with message containing "not launched".
- [ ] **AC-18:** `bridge.launch()` when already launched throws with message containing "already launched".
- [ ] **AC-19:** The Puppeteer viewport after launch has `width` and `height` matching the config, and `deviceScaleFactor === 1`.
- [ ] **AC-20:** When `gpu` is `false` (default), the Chromium launch args include `--disable-gpu`. When `gpu` is `true`, `--disable-gpu` is NOT in the args.
- [ ] **AC-21:** `bridge.launch()` with `pagePath` pointing to a directory without `index.html` throws with a descriptive error message.
- [ ] **AC-22:** After `bridge.close()`, `bridge.launch()` can be called again (re-entrant lifecycle).
- [ ] **AC-23:** `FrameClock.fromDuration(30, -1)` throws (negative duration). `FrameClock.fromDuration(0, 10)` throws (zero fps).
- [ ] **AC-24:** A page-side error thrown during `bridge.evaluate()` propagates as a rejected promise with the original error message.

## Edge Cases and Error Handling

### FrameClock

| Scenario | Expected Behavior |
|---|---|
| `fps` is 0, negative, `NaN`, or `Infinity` | Constructor throws `RangeError`: `"fps must be a positive finite number, got {value}"` |
| `totalFrames` is 0, negative, non-integer, `NaN`, or `Infinity` | Constructor throws `RangeError`: `"totalFrames must be a positive integer, got {value}"` |
| `frameToTimestamp()` with frame < 0 | Throws `RangeError`: `"frame must be in range [0, {totalFrames-1}], got {frame}"` |
| `frameToTimestamp()` with frame >= totalFrames | Throws `RangeError`: `"frame must be in range [0, {totalFrames-1}], got {frame}"` |
| `frameToTimestamp()` with non-integer frame | Throws `RangeError`: `"frame must be an integer, got {frame}"` |
| `timestampToFrame()` with negative timestamp | Throws `RangeError`: `"timestamp must be non-negative, got {timestamp}"` |
| `timestampToFrame()` with timestamp beyond duration | Clamps to `totalFrames - 1`. No error — this enables audio-aligned lookups where the timestamp may slightly exceed the video duration. |
| `fromDuration()` with non-positive duration | Throws `RangeError`: `"durationSeconds must be positive, got {value}"` |
| `fromDuration()` with very small duration (e.g., 0.001s at 30fps) | Produces `totalFrames = 1` via `Math.ceil()`. Valid. |
| `frames()` called multiple times | Returns a fresh generator each time. Generators are independent. |
| `totalFrames = 1` | Single-frame video. `frames()` yields one tick: `{ frame: 0, timestamp: 0, isFirst: true, isLast: true }`. |
| Floating-point precision: `frameToTimestamp(1)` at fps=30 | Returns `1 / 30` — standard JS floating-point. No special rounding. Precision is sufficient for video timing. |

### PuppeteerBridge

| Scenario | Expected Behavior |
|---|---|
| `launch()` when already launched | Throws `Error`: `"PuppeteerBridge: already launched. Call close() first."` |
| `evaluate()` before launch | Throws `Error`: `"PuppeteerBridge: not launched. Call launch() first."` |
| `captureFrame()` before launch | Throws `Error`: `"PuppeteerBridge: not launched. Call launch() first."` |
| `close()` when not launched | No-op. Idempotent. |
| `close()` after close | No-op. Idempotent. |
| `launch()` after `close()` | Succeeds — fresh browser instance. Re-entrant lifecycle. |
| `pagePath` doesn't exist or lacks `index.html` | `launch()` throws `Error`: `"PuppeteerBridge: page not found at {path}. Run 'npm run build' first."` Check is performed before `page.goto()`. |
| Page fails to load (JS error in bundle) | `launch()` throws `Error` with the page error message. Detected by listening for page errors and verifying `window.depthkit` exists. |
| `window.depthkit` not found after page load | `launch()` throws `Error`: `"PuppeteerBridge: window.depthkit not found. The page bundle may be corrupt."` |
| `evaluate()` with non-serializable args | Puppeteer throws — error propagates unmodified. |
| Page function throws during `evaluate()` | Error propagates as a rejected Promise with the original error message. |
| Chromium crashes during operation | `evaluate()` / `captureFrame()` throw Puppeteer's native crash error. Caller (OBJ-035) handles retry/abort. |
| `captureFrame('raw')` when canvas has `preserveDrawingBuffer: false` | Returns a zero-filled buffer (blank frame). This is a misconfig — OBJ-010 defaults to `preserveDrawingBuffer: true`. Bridge does not validate this. |
| Very large viewport (e.g., 7680×4320) | Allowed — Puppeteer and Chromium handle it. May be slow or OOM on constrained machines. Not validated by the bridge. |
| `width` or `height` ≤ 0 | Constructor throws `RangeError`: `"width and height must be positive integers"`. |
| Non-integer `width` or `height` | Rounded via `Math.round()`, matching OBJ-010's behavior. If result ≤ 0, throws. |
| `extraArgs` override a default arg | Allowed. Last occurrence of a Chromium flag wins. Documented as "use at your own risk." |

## Test Strategy

### FrameClock — Unit Tests (`test/unit/frame-clock.test.ts`)

Pure synchronous tests, no I/O dependencies.

1. **Construction:** Valid configs create instances with correct readonly properties (`fps`, `totalFrames`, `duration`, `frameDuration`).
2. **`frameToTimestamp()`:** Test frame 0 → 0.0; last frame → `(totalFrames-1)/fps`; intermediate frames at 24fps and 30fps.
3. **`timestampToFrame()`:** Test round-trip: `timestampToFrame(frameToTimestamp(N)) === N` for all frames in a small clock. Test clamping: timestamp beyond duration → last frame.
4. **`frames()` iterator:** Verify length equals `totalFrames`. Verify first tick's `isFirst`, last tick's `isLast`. Verify every tick's `timestamp === frame / fps`. Verify calling `frames()` twice yields independent generators.
5. **`fromDuration()` factory:** Test exact durations (e.g., 10.0s at 30fps → 300 frames). Test fractional durations (10.01s at 30fps → 301 frames). Test very short durations (0.001s → 1 frame).
6. **Boundary: single-frame clock:** `totalFrames = 1` — `frames()` yields one tick with `isFirst: true, isLast: true`.
7. **Error cases:** All RangeError conditions from edge cases table. 9 distinct cases.
8. **Determinism (TC-06):** Same config always produces same results — trivially true for pure math but worth asserting as a property test.

### PuppeteerBridge — Integration Tests (`test/integration/puppeteer-bridge.test.ts`)

These tests launch real headless Chromium. They are slower (~2-5s per test) and should be tagged/separated from unit tests.

9. **Launch and verify:** `launch()` succeeds, `isLaunched === true`, `page` is non-null. `evaluate(() => typeof window.depthkit)` returns `'object'`.
10. **Viewport dimensions:** After launch, verify viewport matches config via `page.viewport()`.
11. **PNG capture:** Init depthkit on page, render a frame (add a colored mesh via evaluate), capture as PNG. Verify Buffer starts with PNG magic bytes. Verify image is not all-black (proves rendering + capture works).
12. **Raw capture:** Same as above but with `'raw'` format. Verify buffer size is `width * height * 4`.
13. **Close and re-launch:** `close()`, verify `isLaunched === false`, `launch()` again, verify it works.
14. **Double launch error:** `launch()` twice without close → error.
15. **Operations before launch:** `evaluate()` and `captureFrame()` before launch → errors.
16. **Missing page path:** Launch with nonexistent path → descriptive error.
17. **Page error propagation:** `evaluate(() => { throw new Error('test') })` → rejected promise with 'test' in message.
18. **GPU flag:** Launch with `gpu: false`, verify Chromium args include `--disable-gpu` (inspectable via `browser.process().spawnargs` or similar).
19. **Small viewport:** Launch with 100×100 viewport. Capture PNG. Verify image dimensions match (can decode PNG header for width/height).

**Performance baseline (TC-02):** Test 11 provides a data point on single-frame launch+init+render+capture time. Log it but don't assert a threshold — that's OBJ-035/TC-02's concern.

**Relevant testable claims:**
- **TC-02** (render performance): Bridge launch + capture latency is the per-frame baseline.
- **TC-06** (deterministic output): Verify two captures of the same scene produce identical PNG buffers.
- **TC-11** (Docker/software WebGL): Tests run with `gpu: false` (SwiftShader) by default.

### Test Infrastructure Notes

- Integration tests require Puppeteer + Chromium installed. CI must not skip these.
- Tests should use small viewports (e.g., 320×240) to minimize memory and time, except where resolution matters.
- Each test should `close()` the bridge in an `afterEach` or `finally` block to prevent leaked Chromium processes.

## Integration Points

### Depends on

| Dependency | What OBJ-009 uses |
|---|---|
| **OBJ-001** (Project scaffolding) | `puppeteer` in dependencies. `src/engine/puppeteer-bridge.ts` and `src/engine/frame-clock.ts` stub files. `dist/page/` build output path. |

**Note:** OBJ-009 does NOT depend on OBJ-010 at the module level — `PuppeteerBridge` loads the page as a file, not as an import. However, the bridge's `launch()` validation (checking for `window.depthkit`) assumes OBJ-010's page shell has been built. This is a **build-time dependency**, not a code-import dependency. The bridge is designed so it works with whatever page is at `pagePath`, and simply verifies the expected global exists.

### Consumed by

| Downstream | How it uses OBJ-009 |
|---|---|
| **OBJ-011** (Message protocol) | Imports `PuppeteerBridge`. Builds the full message protocol on top of `bridge.evaluate()`. Defines frame step commands, scene setup/teardown, texture loading — all implemented as `evaluate()` calls with structured payloads. |
| **OBJ-035** (Orchestrator) | Imports both `FrameClock` and `PuppeteerBridge`. Creates a `FrameClock` from the manifest's fps/duration. Iterates `clock.frames()`. For each tick, uses OBJ-011's protocol (built on the bridge) to send frame commands and capture frames. Pipes captured buffers to FFmpeg (OBJ-012). |
| **OBJ-038** (Audio sync) | Imports `FrameClock`. Uses `timestampToFrame()` to convert narration cue timestamps to frame boundaries. Uses `fromDuration()` to create clocks from audio file duration. |

### File Placement

```
depthkit/
  src/
    engine/
      frame-clock.ts           # EVOLVE from OBJ-001 stub (originally assigned to OBJ-010)
      puppeteer-bridge.ts      # EVOLVE from OBJ-001 stub
  test/
    unit/
      frame-clock.test.ts      # NEW — unit tests for FrameClock
    integration/
      puppeteer-bridge.test.ts # NEW — integration tests for PuppeteerBridge
```

## Open Questions

### OQ-A: Should `captureFrame('raw')` extract via `getImageData` or CDP?

Two approaches for raw RGBA capture:
1. **`page.evaluate()` with `canvas.getContext('2d').getImageData()`** — requires creating a 2D context from the WebGL canvas, which may fail or be slow.
2. **CDP `Page.captureScreenshot` as PNG, then decode in Node** — extra decode step but more reliable.
3. **`canvas.toDataURL('image/png')` via evaluate, decode in Node** — similar overhead.

**Recommendation:** For V1, use approach 2 (CDP screenshot → decode in Node.js using a lightweight PNG decoder or pass PNG directly to FFmpeg, which can decode PNG input frames natively). The `raw` format is an optimization for FFmpeg; if FFmpeg accepts PNG input (it does, via `-f image2pipe -c:v png`), the `raw` format may be unnecessary for V1. The implementer should verify FFmpeg performance with PNG input before investing in raw pixel extraction. If `raw` proves unnecessary, defer it and support only `png`.

### OQ-B: Should the bridge expose `page.on('console')` forwarding?

Chromium `console.log` messages from the page (e.g., OBJ-010's dimension rounding warnings) are silently dropped unless the caller subscribes to `page.on('console')`. Should the bridge automatically forward page console messages to Node's `console`?

**Recommendation:** Yes, but gated by a `debug` config option. Page console output is valuable during development but noisy in production. Default `false`. When enabled, pipe `page.on('console', msg => console.log('[depthkit:page]', msg.text()))`.

### OQ-C: Default `pagePath` resolution strategy

The bridge needs to find `dist/page/index.html`. Options:
1. Resolve relative to `__dirname` (reliable for installed packages).
2. Resolve relative to `process.cwd()` (fragile).
3. Require explicit `pagePath` always (no default).

**Recommendation:** Option 1. The bridge resolves `pagePath` relative to its own file location: `path.resolve(__dirname, '../../dist/page')` (from `dist/engine/puppeteer-bridge.js` to `dist/page/`). This works both for local development and when depthkit is installed as a dependency. Allow override via config.

---

I believe this spec is complete and precise enough for an implementer to build from. I'd like the Challenger to review and verify, particularly:
1. The scope split between FrameClock and PuppeteerBridge.
2. Whether the `raw` capture format should be deferred per OQ-A.
3. Whether the bridge's relationship to OBJ-010 (build-time dependency, not code-import) is correctly characterized.

---

## Round 2 — spec_challenger

Let me start by reading the full OBJ-010 spec to understand the page-side contract that the bridge interacts with.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md"
}
[Tool Result]      1→# Specification: OBJ-010 — Three.js Page Shell, Build/Bundle Architecture, and Scene Renderer Skeleton
     2→
     3→## Summary
     4→
     5→OBJ-010 establishes the browser-side rendering foundation and the authoritative Node.js/browser code-split architecture for depthkit. It delivers: (1) the final HTML page shell with a properly sized WebGL canvas, (2) the Three.js `Scene` / `PerspectiveCamera` / `WebGLRenderer` initialization skeleton that all downstream rendering depends on, (3) the architectural decision that the browser page is a **data-driven renderer** — a "dumb page" that receives computed scene state from the Node.js orchestrator and executes Three.js calls accordingly, and (4) a minimal `renderFrame()` primitive that downstream objectives build upon. This objective also defines Node-side TypeScript types for data crossing the Node/browser boundary (excluding geometry serialization, which is deferred to OBJ-011).
     6→
     7→## Interface Contract
     8→
     9→... [truncated]
Now let me also check if there are any other relevant files:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-010",
     3→  "description": "Three.js page shell, build/bundle strategy, and scene renderer skeleton -- HTML shell (src/page/index.html), page-side module loading strategy (CDN vs bundled Three.js, ESM vs build step via esbuild/vite), mechanism for making TypeScript geometry definitions available to the browser page, Three.js Scene/PerspectiveCamera/WebGLRenderer initialization, and WebGL canvas setup. This is the authoritative decision point for the Node.js/browser code-split architecture.",
     4→  "category": "engine",
     5→  "created_by_session": "spec-deliberation",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-23T01:30:00Z",
     8→  "depends_on": ["OBJ-001", "OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "review_status": "approved",
    12→  "notes": "Spec approved after 4-round deliberation. Key decision: Dumb Page / Smart Orchestrator architecture (D1) -- browser page is a dat... [truncated]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-036/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-036/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-036/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-036",
     3→  "description": "Scene sequencer -- routes manifest scenes to geometries, computes per-scene normalized time from the global frame/timestamp (absorbs per-scene time normalization from the virtualized clock), manages scene lifecycle (setup, active rendering, teardown), handles transition timing windows and overlap scheduling. Uses the transition contract (OBJ-008) to compute when scenes overlap.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035", "OBJ-005", "OBJ-008"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration. Absorbs per-scene time normalization (moved from OBJ-009 per Round 2 Issue 8). Depends on OBJ-008 per Round 2 Issue 2."
    12→}
    13→
Good. Now I have the full picture. Let me do my review.

---

## Challenger Review — OBJ-009 Spec Proposal

I've read the proposal carefully against the seed, OBJ-001 spec, OBJ-010 spec, and the downstream consumer metadata. Here's my assessment.

### What's Sound

1. **Two-module split (FrameClock + PuppeteerBridge)** — Clean, well-motivated. The clock is pure math, the bridge is I/O. Good separation of concerns.

2. **FrameClock immutability (D2)** — Correct. Stateless coordinate system, not a ticker. Supports parallelization. Well-reasoned.

3. **Zero-indexing (D3)** — Conventional and correct.

4. **`fromDuration` with `Math.ceil` (D5)** — Good reasoning about not truncating audio.

5. **Bridge as raw primitive, not domain logic (D6)** — Correctly defers protocol to OBJ-011.

6. **Software rendering default (D8)** — C-11 compliant.

7. **Edge cases table for FrameClock** — Thorough, covers all constructible error states.

8. **Test strategy** — Good separation of unit (FrameClock) vs integration (PuppeteerBridge).

### Issues

---

**Issue 1: `PuppeteerBridge` imports `PageInitConfig` and `RendererInfo` but never uses them in its interface** — Severity: **Minor**

The import line says `import type { PageInitConfig, RendererInfo } from './page-types.js'` but neither type appears in any method signature. `launch()` doesn't take a `PageInitConfig`. The bridge doesn't call `init()` on the page — that's OBJ-011's job.

**Fix:** Remove the import from the interface contract. The bridge has no business knowing about page-types. If they're there for documentation purposes only, say so in a comment, but don't present them as part of the module's import surface.

---

**Issue 2: How does `captureFrame('raw')` actually work?** — Severity: **Major**

The spec says `'raw'` returns `width * height * 4` bytes of RGBA data, and D7 says it uses "CDP + canvas pixel extraction." But the mechanism is unspecified. The spec needs to say *how* raw pixels are extracted. There are several approaches:

- `page.evaluate()` calling `canvas.getContext('2d').getImageData()` — but you can't get a 2D context from a WebGL canvas
- `page.evaluate()` calling `renderer.getContext().readPixels()` — returns an ArrayBuffer, but transferring large buffers back through `page.evaluate()` serialization is slow (JSON serialization of megabytes of pixel data)
- CDP `Page.captureScreenshot` with `format: 'png'` then decode on Node — contradicts the point of `'raw'`

OQ-A acknowledges this uncertainty but the spec still includes `'raw'` as a supported format with a concrete AC (AC-13).

**Fix:** Either (a) specify the exact mechanism for raw capture so the implementer doesn't have to research this, or (b) defer `'raw'` format entirely and only support `'png'` for V1, as OQ-A recommends. Given AP-05 (no premature optimization), I recommend option (b). Remove `'raw'` from `CaptureFormat`, remove AC-13, and document the deferral. If `'raw'` is kept, you must specify: the bridge uses `page.evaluate()` to call `gl.readPixels()` on the WebGL context, encode the resulting `Uint8Array` as a base64 string for transfer back to Node, then decode to Buffer. Include the performance cost in the spec.

---

**Issue 3: Missing type import — `PageInitConfig` and `RendererInfo` in `PuppeteerBridgeConfig`** — Severity: **Minor (related to Issue 1)**

The bridge's interface imports these types but doesn't use them. Meanwhile, the bridge's `launch()` method validates `window.depthkit` exists (D11), but doesn't call `window.depthkit.init()`. Who calls `init()`? OBJ-011. This is fine architecturally, but the spec should explicitly state: "The bridge does NOT call `window.depthkit.init()`. Initialization of the Three.js renderer is the responsibility of the message protocol (OBJ-011) or the orchestrator (OBJ-035) via `evaluate()`."

**Fix:** Add a clear statement in the Design Decisions or Integration Points that the bridge's responsibility ends at page load + `window.depthkit` existence check. Init is downstream's job.

---

**Issue 4: AC-12 assumes `init()` has been called, but the bridge doesn't call it** — Severity: **Major**

AC-12 says: "After launching and calling `window.depthkit.init()` via `evaluate()`, `bridge.captureFrame('png')` returns a Buffer whose first 8 bytes are the PNG magic number."

This is actually a test of the bridge + OBJ-010 working together. But the spec doesn't define *how* the test calls init — it must use `bridge.evaluate(() => window.depthkit.init({ width: ..., height: ... }))`. The AC is fine as written — it describes the test setup — but it conflates bridge testing with OBJ-010's `init()`. This is acceptable for an integration test.

Actually, on re-reading, AC-12 is clear: "After launching **and calling** `window.depthkit.init()` via `evaluate()`" — it specifies the setup. This is fine. **Withdrawn.**

---

**Issue 5: `captureFrame()` for PNG — `page.screenshot()` vs CDP `Page.captureScreenshot`** — Severity: **Minor**

D7 says "Uses CDP `Page.captureScreenshot` for 'png' format" but the spec doesn't clarify whether this is `page.screenshot()` (Puppeteer's wrapper) or a direct CDP call. They produce different results:

- `page.screenshot({ type: 'png' })` captures the **full page viewport**, including HTML elements above/below the canvas (relevant for future HUD layers).
- Direct CDP `Page.captureScreenshot` is essentially the same but lower-level.

For V1 this doesn't matter (page has only the canvas), but for HUD layers (seed vocabulary), `page.screenshot()` is correct because it captures the composited page.

**Fix:** Specify that `captureFrame('png')` uses Puppeteer's `page.screenshot({ type: 'png', encoding: 'binary' })`. This captures the full viewport composited output, which future HUD layers will rely on. Make explicit that this captures HTML + canvas together, not just the WebGL canvas.

---

**Issue 6: Missing `FrameTick` field — `totalFrames`** — Severity: **Minor**

`FrameTick` includes `frame`, `timestamp`, `isFirst`, `isLast`. But downstream consumers (OBJ-035, OBJ-036) will need `totalFrames` and `fps` when computing per-scene normalized time. Currently they'd have to carry these separately from the clock.

**Proposed fix:** Add `fps` and `totalFrames` to `FrameTick`, OR accept that the orchestrator already has the `FrameClock` instance and can access `clock.fps` and `clock.totalFrames` alongside the tick. The latter is simpler and avoids redundant data in every tick. **No change needed** — the orchestrator creates the clock and iterates it, so it has both. **Withdrawn.**

---

**Issue 7: `file://` CORS for textures — mismatch with OBJ-010's contract** — Severity: **Major**

D10 says the bridge loads the page via `file://` protocol. The spec correctly notes that Three.js `TextureLoader` may fail with `file://` due to CORS. But it waves this away as "OBJ-011/OBJ-015's concern."

This is a structural problem. If the bridge loads via `file://`, and OBJ-011/OBJ-015 need to load textures via URL, they either need:
1. A way to tell the bridge to load via `http://` instead (spinning up a local server), or
2. A completely different texture loading strategy (injecting image data via `evaluate()`)

The bridge's page loading strategy constrains all downstream texture loading. This needs to either:
- **Document the constraint explicitly** as a known limitation that downstream must work around, with a recommended approach, OR
- **Provide an option** to serve the page via a local HTTP server instead of `file://`

Looking at OBJ-010's spec, it says textures are loaded by downstream objectives. OBJ-015 is the texture loader. The bridge's choice of `file://` vs `http://` is an architectural decision that affects OBJ-015's design space.

**Fix:** Add a `serveMode` config option: `'file'` (default, uses `file://`) or `'http'` (spins up a local HTTP server on an ephemeral port). OR: document that `file://` is the only mode, and texture loading MUST be done via data injection (`page.evaluate()` with base64 data or Blob URLs), not via HTTP fetch. The latter is the cleaner approach for a self-contained engine. State this as a binding constraint for OBJ-015.

Actually, re-reading the seed Section 4.4 more carefully: textures are "pre-loaded" before rendering starts. Puppeteer can use `page.evaluate()` to inject texture data. And Chromium can be launched with `--allow-file-access-from-files` to enable file:// CORS.

**Revised fix:** Add `--allow-file-access-from-files` to the default Chromium launch args. This allows `TextureLoader` to load images from the filesystem via `file://` URLs. Document this in D8's arg list. This is the simplest solution and doesn't require a local HTTP server.

---

**Issue 8: Default `pagePath` resolution (OQ-C) should not be an open question** — Severity: **Major**

OQ-C asks how to resolve the default `pagePath`. But this is a critical implementation decision — if the implementer guesses wrong, the bridge won't find its page. The spec must decide.

The recommendation in OQ-C (option 1: resolve relative to `__dirname`) is correct, but it should be a **Design Decision**, not an open question.

**Fix:** Promote OQ-C to a design decision. State: "Default `pagePath` is resolved relative to the bridge module's location: `path.resolve(import.meta.dirname, '../page')` (from `dist/engine/puppeteer-bridge.js` to `dist/page/`). Uses `import.meta.dirname` (Node 21.2+) or `path.dirname(fileURLToPath(import.meta.url))` for Node 18+ compatibility." Also add an AC verifying that the default pagePath resolution works.

Wait — Node 18 doesn't have `import.meta.dirname`. The spec needs to specify the ESM-compatible approach: `path.dirname(fileURLToPath(import.meta.url))`. OBJ-001 targets Node >=18.

**Fix:** Design decision must use `fileURLToPath(import.meta.url)` pattern for Node 18 compatibility.

---

**Issue 9: `PuppeteerBridgeConfig` — `width` and `height` non-integer handling** — Severity: **Minor**

The edge cases table says non-integer width/height are "Rounded via `Math.round()`, matching OBJ-010's behavior." But the bridge sets the Puppeteer viewport, not the canvas. Puppeteer's `page.setViewport()` may or may not accept non-integers — it depends on the implementation.

**Fix:** Validate `width` and `height` are positive integers in the constructor. Throw `RangeError` for non-integers. Don't silently round. The bridge sets pixel-exact viewport dimensions; rounding is OBJ-010's concern for canvas sizing. The caller (OBJ-035/orchestrator) should pass integer dimensions. This is simpler and clearer.

---

**Issue 10: Missing AC for page console forwarding (OQ-B)** — Severity: **Minor**

OQ-B recommends a `debug` config option for forwarding page console messages. But like OQ-C, this is important enough to be a design decision, not an open question. Page console errors (JS exceptions, Three.js warnings) being silently swallowed makes debugging impossible.

**Fix:** Promote to a design decision. Recommend: always forward `console.error` and `console.warn` from the page. Optional `debug` flag for forwarding `console.log`. Add a `PuppeteerBridgeConfig.debug?: boolean` field. Add an AC verifying that page-side errors are forwarded to Node's stderr.

Actually, this may be overreach — it's useful but not critical for the bridge's core functionality. **Revised: keep as open question** but at minimum specify that page crash errors (uncaught exceptions) must be detectable. The bridge should listen for `page.on('pageerror')` and either throw or store the error for the next `evaluate()` call. This IS critical — if the page throws during rendering, the bridge must surface it, not hang.

**Revised fix:** Add handling for `page.on('pageerror')`: the bridge stores the error and throws it on the next `evaluate()` or `captureFrame()` call. Add an AC: "If the page throws an uncaught exception, the next `evaluate()` or `captureFrame()` call rejects with that error." Keep console forwarding as an open question.

---

**Issue 11: Spec references `import type { Vec3 }` but doesn't define it** — Severity: **Negligible**

The bridge spec imports `PageInitConfig` and `RendererInfo` from `page-types.ts`, which in OBJ-010's spec imports `Vec3` from `../spatial/types.js` (OBJ-003). This is fine — it's OBJ-010's dependency, not OBJ-009's. But since Issue 1 says to remove the import entirely, this is moot.

---

### Summary of Required Changes

**Critical:** None.

**Major (3):**
1. **Issue 2:** Either fully specify `'raw'` capture mechanism or defer it. Recommend deferring.
2. **Issue 7:** Add `--allow-file-access-from-files` to default Chromium args, or specify an alternative texture loading constraint.
3. **Issue 8:** Promote pagePath resolution from OQ to Design Decision with ESM-compatible code.

**Minor (4):**
1. **Issue 1:** Remove unused type imports from PuppeteerBridge interface.
3. **Issue 3:** Explicitly state bridge doesn't call `init()`.
5. **Issue 5:** Specify `page.screenshot()` as the capture mechanism for PNG.
9. **Issue 9:** Validate width/height as positive integers, don't silently round.
10. **Issue 10 (revised):** Handle `page.on('pageerror')` — surface uncaught page errors.

Please revise the proposal addressing these. I'll verify the fixes structurally in the next round.

---

## Round 3 — spec_author

Thank you for the thorough review. All issues are valid. Here's the revised spec addressing each one:

---

# Specification: OBJ-009 — Virtualized Clock and Puppeteer Bridge

## Summary

OBJ-009 delivers two modules that together implement the virtualized clock mechanism defined in C-03. First, `FrameClock` (`src/engine/frame-clock.ts`) — a pure, stateless utility that maps frame numbers to timestamps and provides an iterator for deterministic frame stepping. It has no scene awareness; per-scene normalized time is OBJ-036's responsibility. Second, `PuppeteerBridge` (`src/engine/puppeteer-bridge.ts`) — the Puppeteer lifecycle manager that launches headless Chromium, loads the OBJ-010 page shell, exposes an `evaluate()` primitive for downstream message protocols (OBJ-011), and captures rendered frames as PNG pixel buffers via Puppeteer's screenshot API. Together, these two modules provide the building blocks that OBJ-035 (orchestrator) composes into the deterministic render loop from seed Section 4.4.

## Interface Contract

### Module: `src/engine/frame-clock.ts`

```typescript
/**
 * Configuration for creating a FrameClock.
 */
export interface FrameClockConfig {
  /** Frames per second. Must be a positive finite number. */
  fps: number;
  /** Total number of frames in the composition. Must be a positive integer. */
  totalFrames: number;
}

/**
 * Information about a single frame tick.
 * Yielded by FrameClock.frames() iterator.
 */
export interface FrameTick {
  /** Zero-indexed frame number: 0 to totalFrames - 1 */
  frame: number;
  /** Absolute timestamp in seconds: frame / fps */
  timestamp: number;
  /** Whether this is the first frame (frame === 0) */
  isFirst: boolean;
  /** Whether this is the last frame (frame === totalFrames - 1) */
  isLast: boolean;
}

/**
 * Pure, immutable utility for deterministic frame-to-timestamp mapping.
 * No I/O, no scene awareness, no side effects.
 *
 * The clock defines the global temporal coordinate system for a composition.
 * It does NOT compute per-scene normalized time — that is OBJ-036's
 * responsibility using the clock's frame/timestamp outputs as inputs.
 */
export class FrameClock {
  /** Frames per second. */
  readonly fps: number;
  /** Total number of frames in the composition. */
  readonly totalFrames: number;
  /** Total duration in seconds: totalFrames / fps */
  readonly duration: number;
  /** Duration of a single frame in seconds: 1 / fps */
  readonly frameDuration: number;

  constructor(config: FrameClockConfig);

  /**
   * Convert a frame number to an absolute timestamp in seconds.
   * @param frame — Zero-indexed frame number.
   * @returns timestamp in seconds (frame / fps).
   * @throws RangeError if frame < 0 or frame >= totalFrames or not an integer.
   */
  frameToTimestamp(frame: number): number;

  /**
   * Convert an absolute timestamp (seconds) to the nearest frame number.
   * Uses Math.round(), then clamps to [0, totalFrames - 1].
   * @param timestamp — Time in seconds.
   * @returns frame number (integer, clamped).
   * @throws RangeError if timestamp is negative.
   */
  timestampToFrame(timestamp: number): number;

  /**
   * Generator that yields FrameTick objects for every frame from 0
   * to totalFrames - 1, in order. This is the canonical iteration
   * primitive for the render loop.
   *
   * Usage:
   *   for (const tick of clock.frames()) {
   *     // render tick.frame at tick.timestamp
   *   }
   */
  frames(): Generator<FrameTick, void, undefined>;

  /**
   * Static factory: create a FrameClock from a duration in seconds.
   * totalFrames = Math.ceil(durationSeconds * fps).
   *
   * @param fps — Frames per second.
   * @param durationSeconds — Desired duration in seconds. Must be positive.
   * @returns FrameClock instance.
   */
  static fromDuration(fps: number, durationSeconds: number): FrameClock;
}
```

### Module: `src/engine/puppeteer-bridge.ts`

```typescript
import type { Page, Browser } from 'puppeteer';

/**
 * Configuration for launching the PuppeteerBridge.
 */
export interface PuppeteerBridgeConfig {
  /** Viewport width in pixels. Must be a positive integer. */
  width: number;
  /** Viewport height in pixels. Must be a positive integer. */
  height: number;
  /**
   * Absolute path to the built page directory containing index.html
   * and scene-renderer.js.
   *
   * Default: resolved relative to this module's location —
   * path.resolve(bridgeDir, '../page') where bridgeDir is derived from
   * import.meta.url via fileURLToPath. This resolves from
   * dist/engine/puppeteer-bridge.js to dist/page/.
   */
  pagePath?: string;
  /**
   * Headless mode. Default: true.
   * Set to false for debugging (opens visible browser window).
   */
  headless?: boolean;
  /**
   * Path to a custom Chromium/Chrome executable.
   * If not provided, uses Puppeteer's bundled Chromium.
   */
  executablePath?: string;
  /**
   * Enable GPU-accelerated rendering. Default: false.
   *
   * When false (default): adds --disable-gpu and related flags
   * for software rendering via SwiftShader (C-11 compliance).
   *
   * When true: omits GPU-disabling flags, allowing hardware
   * acceleration when available. Faster but requires GPU passthrough
   * in Docker/CI environments.
   */
  gpu?: boolean;
  /**
   * Additional Chromium launch arguments.
   * Appended after the bridge's default arguments.
   */
  extraArgs?: string[];
  /**
   * Forward page console.log messages to Node's stdout.
   * Default: false. When true, all page console output (log, warn,
   * error, info) is forwarded to Node's console prefixed with
   * '[depthkit:page]'. When false, only page crashes (uncaught
   * exceptions) are surfaced — see pageerror handling.
   */
  debug?: boolean;
}

/**
 * Manages the Puppeteer lifecycle for depthkit's rendering pipeline.
 *
 * Responsibilities:
 * - Launch headless Chromium with correct flags for WebGL rendering.
 * - Load the depthkit page shell (OBJ-010's index.html + scene-renderer.js).
 * - Set viewport to match composition dimensions exactly.
 * - Provide evaluate() for downstream message protocols (OBJ-011).
 * - Capture rendered frames as PNG buffers via page.screenshot().
 * - Detect and surface uncaught page errors (pageerror events).
 * - Clean up browser resources on close.
 *
 * The bridge does NOT call window.depthkit.init(). Initialization of the
 * Three.js renderer is the responsibility of the message protocol (OBJ-011)
 * or the orchestrator (OBJ-035) via evaluate(). The bridge's responsibility
 * ends at page load + window.depthkit existence check.
 *
 * The bridge is the enforcement mechanism for the virtualized clock (C-03):
 * it never uses requestAnimationFrame or wall-clock timing. The caller
 * (orchestrator, OBJ-035) controls when each frame is rendered by calling
 * evaluate() to send frame commands, then captureFrame() to extract pixels.
 */
export class PuppeteerBridge {
  constructor(config: PuppeteerBridgeConfig);

  /**
   * Launch headless Chromium, create a page, set viewport, and load
   * the depthkit page shell (index.html).
   *
   * Postconditions:
   * - Browser is running.
   * - Page is loaded and scene-renderer.js has executed.
   * - Viewport is set to config.width x config.height with deviceScaleFactor=1.
   * - window.depthkit is available on the page.
   * - page.on('pageerror') listener is registered.
   * - If debug=true, page.on('console') listener is registered.
   *
   * @throws Error if browser fails to launch.
   * @throws Error if page fails to load or scene-renderer.js errors.
   * @throws Error if already launched (call close() first).
   * @throws Error if pagePath does not exist or lacks index.html.
   * @throws Error if window.depthkit is not found after page load.
   */
  launch(): Promise<void>;

  /**
   * Execute a function in the browser page context.
   * Thin wrapper around Puppeteer's page.evaluate().
   *
   * This is the primitive that OBJ-011 builds its message protocol on.
   * The orchestrator (OBJ-035) uses it via OBJ-011's higher-level API.
   *
   * @param pageFunction — Function or string to evaluate in the page.
   * @param args — Serializable arguments passed to the function.
   * @returns The serializable return value from the page function.
   * @throws Error if not launched.
   * @throws Error if a prior uncaught page error was detected (pageerror).
   * @throws Error if the page function throws (error is propagated).
   */
  evaluate<T>(
    pageFunction: string | ((...args: any[]) => T),
    ...args: any[]
  ): Promise<T>;

  /**
   * Capture the current state of the page viewport as a PNG buffer.
   *
   * Uses Puppeteer's page.screenshot({ type: 'png', encoding: 'binary' }).
   * This captures the full composited viewport — both the WebGL canvas
   * and any HTML elements layered on top (future HUD layers). This is
   * intentional: HUD elements are part of the rendered frame.
   *
   * The caller is responsible for ensuring the frame has been rendered
   * (via evaluate() + renderFrame()) before calling captureFrame().
   * This method captures whatever is currently on the viewport.
   *
   * @returns Buffer containing PNG image data.
   * @throws Error if not launched.
   * @throws Error if a prior uncaught page error was detected (pageerror).
   */
  captureFrame(): Promise<Buffer>;

  /**
   * Close the browser and release all resources.
   * Idempotent — safe to call multiple times.
   *
   * After close(), launch() can be called again.
   */
  close(): Promise<void>;

  /**
   * Whether the bridge has been launched and is ready.
   */
  readonly isLaunched: boolean;

  /**
   * The underlying Puppeteer Page instance.
   * Exposed for advanced use by OBJ-011 (e.g., page.on('console')).
   * null before launch() or after close().
   */
  readonly page: Page | null;
}
```

## Design Decisions

### D1: Two Modules, Clean Separation

**Decision:** OBJ-009 delivers two separate modules: `FrameClock` (pure math) and `PuppeteerBridge` (I/O + browser lifecycle). They do not import each other.

**Rationale:** The frame clock is consumed by OBJ-035 (orchestrator) and OBJ-038 (audio sync) for timestamp computation. The Puppeteer bridge is consumed by OBJ-035 and OBJ-011. Keeping them separate honors the "pure utility with no scene awareness" description for the clock, while cleanly isolating all Puppeteer I/O concerns. OBJ-035 composes them: it creates a `FrameClock`, iterates its `frames()`, and for each tick calls `bridge.evaluate()` + `bridge.captureFrame()`.

### D2: FrameClock is Immutable and Stateless

**Decision:** `FrameClock` is constructed with `fps` and `totalFrames`, then never changes. It has no internal cursor or mutable state. The `frames()` generator is a fresh iterator each time, producing frame ticks without side effects.

**Rationale:** The clock is a **coordinate system**, not a ticker. It maps between frame numbers and timestamps. Statefulness (tracking "current frame") belongs to the orchestrator (OBJ-035), which may need to render frames out of order for parallelization (seed C-08 mentions splitting frame ranges). A stateless clock supports any iteration pattern.

**Alternative considered:** A stateful clock with `advance()` / `currentFrame` API. Rejected because it couples the clock to sequential iteration, making parallelized rendering harder.

### D3: Frame Numbers are Zero-Indexed

**Decision:** Frame 0 is the first frame. Frame `totalFrames - 1` is the last frame. `frameToTimestamp(0) = 0.0`. `frameToTimestamp(totalFrames - 1) = (totalFrames - 1) / fps`.

**Rationale:** Zero-indexing is conventional for frame ranges in video pipelines and aligns with FFmpeg's frame numbering. The last frame's timestamp is `(totalFrames - 1) / fps`, NOT `totalFrames / fps` (which would be one frame past the end).

### D4: `timestampToFrame()` Uses `Math.round()` with Clamping

**Decision:** `timestampToFrame()` converts seconds to a frame via `Math.round(timestamp * fps)`, then clamps to `[0, totalFrames - 1]`.

**Rationale:** `Math.round()` produces the frame whose timestamp is nearest to the input. Clamping prevents out-of-range indices. This is used by OBJ-038 (audio sync) to convert narration cue timestamps to frame boundaries.

### D5: `fromDuration()` Uses `Math.ceil()`

**Decision:** `FrameClock.fromDuration(fps, durationSeconds)` computes `totalFrames = Math.ceil(durationSeconds * fps)`.

**Rationale:** `Math.ceil()` ensures the video duration is at least as long as the requested duration. A 10-second video at 30fps = 300 frames, covering `[0, 9.967s]`. With `Math.ceil()`, 10.01 seconds → 301 frames, ensuring the last moment is captured. `Math.floor()` would truncate, potentially cutting off the end of audio (violating C-07). `Math.round()` could go either way, making behavior unpredictable at boundaries.

### D6: PuppeteerBridge Provides Raw Primitives, Not Domain Logic

**Decision:** The bridge exposes `evaluate()` and `captureFrame()` — raw primitives. It does NOT expose `renderFrame()`, `initScene()`, or any depthkit-specific operations. Those are defined by OBJ-011 (message protocol) using `evaluate()` as the transport. The bridge does NOT call `window.depthkit.init()` — initialization of the Three.js renderer is the responsibility of OBJ-011 or OBJ-035 via `evaluate()`.

**Rationale:** OBJ-011 owns the full cross-boundary message contract. If the bridge pre-defined `renderFrame()`, it would duplicate OBJ-011's responsibility and couple the bridge to the page API. The bridge is a transport layer; OBJ-011 defines the protocol; OBJ-035 orchestrates.

**Exception:** `launch()` loads the page and verifies `window.depthkit` is defined — this minimal check ensures the page shell (OBJ-010) loaded correctly, without coupling to its internal API.

### D7: PNG-Only Capture via `page.screenshot()`

**Decision:** `captureFrame()` returns PNG data exclusively, using Puppeteer's `page.screenshot({ type: 'png', encoding: 'binary' })`. There is no raw RGBA capture format.

**Rationale:** `page.screenshot()` captures the **full composited viewport** — both the WebGL canvas and any HTML elements positioned above it. This is the correct behavior for future HUD layers (seed vocabulary), where titles/captions rendered as HTML/CSS must appear in the captured frame.

Raw RGBA extraction was considered and deferred:
- Extracting raw pixels from a WebGL canvas via `gl.readPixels()` requires transferring `width * height * 4` bytes through Puppeteer's serialization layer (JSON-encoded base64), which is slow for 1920×1080 frames (~8MB per frame).
- FFmpeg accepts PNG input natively via `-f image2pipe -c:v png`, so PNG is a fully viable pipeline format.
- Per AP-05 (no premature optimization), raw capture is deferred until benchmarking proves PNG throughput is a bottleneck in the FFmpeg pipeline.

If raw capture is needed later, it would be added as a separate method or format option on the bridge, with the mechanism specified at that time.

### D8: Software Rendering by Default (C-11)

**Decision:** Default Chromium launch args include `--disable-gpu` for software rendering. A `gpu: true` config option omits this flag.

**Rationale:** C-11 mandates software rendering correctness. The engine must run in Docker without GPU passthrough. SwiftShader (Chromium's software WebGL) is available by default in Puppeteer's bundled Chromium. GPU acceleration is opt-in for environments where it's available.

**Default Chromium args:**
```
--disable-gpu                    // Software WebGL (SwiftShader) — omitted when gpu=true
--disable-dev-shm-usage          // Docker: use /tmp instead of /dev/shm
--no-sandbox                     // Docker: required when running as root
--disable-setuid-sandbox         // Docker: companion to --no-sandbox
--hide-scrollbars                // Prevent scrollbar interference
--mute-audio                     // No audio output from browser
--allow-file-access-from-files   // Enable file:// CORS for texture loading
```

When `gpu: true`, `--disable-gpu` is omitted; all other args remain.

**The `--allow-file-access-from-files` flag** enables Three.js `TextureLoader` to load image files via `file://` URLs from the filesystem. Without this flag, CORS restrictions would block file:// fetches, breaking texture loading. This flag is safe because the page runs in a controlled headless environment with no untrusted content. See D10 for the full file:// rationale.

### D9: Viewport `deviceScaleFactor: 1`

**Decision:** The Puppeteer viewport is always set with `deviceScaleFactor: 1`.

**Rationale:** Combined with OBJ-010's `renderer.setPixelRatio(1)`, this ensures 1:1 pixel mapping. A 1920×1080 viewport produces a 1920×1080 screenshot. HiDPI scaling would silently double the resolution, breaking FFmpeg encoding and violating C-05 (deterministic output).

### D10: Page Loading via `file://` Protocol

**Decision:** The bridge loads `index.html` via `file://` protocol using `page.goto('file://...')`.

**Rationale:** The built page is self-contained — `index.html` loads `scene-renderer.js` (esbuild bundle with Three.js inlined). No network requests needed for page load. `file://` avoids the complexity of spinning up a local HTTP server.

**Texture loading constraint:** The `--allow-file-access-from-files` Chromium flag (D8) enables Three.js `TextureLoader` to load images from the filesystem via `file://` URLs. This means OBJ-015 (texture loading) can pass absolute `file://` paths to `TextureLoader` via `evaluate()`, or inject image data as base64/Blob URLs. Both approaches work with `file://` page loading. The `--allow-file-access-from-files` flag makes this transparent.

**Binding constraint for OBJ-015:** Texture file paths passed to the page must be absolute filesystem paths convertible to `file://` URLs, OR data URIs / Blob URLs injected via `evaluate()`. Relative HTTP URLs will not resolve.

### D11: Default `pagePath` Resolution via `import.meta.url`

**Decision:** When `pagePath` is not provided, the bridge resolves it relative to its own file location using the ESM-compatible pattern:

```typescript
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaultPagePath = path.resolve(__dirname, '../page');
```

This resolves from `dist/engine/puppeteer-bridge.js` to `dist/page/`. Works for both local development (`npm run build` then run) and when depthkit is installed as a dependency (the `dist/` directory is part of the published package).

**Rationale:** `import.meta.dirname` requires Node 21.2+, but OBJ-001 targets Node >=18. The `fileURLToPath(import.meta.url)` pattern is the standard ESM approach for Node 18+. Resolving relative to the module's own location (not `process.cwd()`) ensures the bridge finds its page regardless of the caller's working directory.

### D12: Bridge Validates Page Load

**Decision:** After `page.goto()`, the bridge verifies that `window.depthkit` is defined on the page. If not, `launch()` throws with a descriptive error.

**Rationale:** Catches build failures (missing bundle, esbuild errors) at bridge launch time rather than later when `evaluate()` calls fail with cryptic "depthkit is not defined" errors.

### D13: Uncaught Page Errors Are Surfaced

**Decision:** The bridge registers a `page.on('pageerror')` listener during `launch()`. When an uncaught page error is detected, the bridge stores it. Subsequent calls to `evaluate()` or `captureFrame()` reject with that stored error immediately, without attempting the operation.

**Rationale:** If the page throws an uncaught exception (e.g., Three.js initialization fails, WebGL context lost, out-of-memory), the page is in an undefined state. Continuing to send frame commands would produce unpredictable results. The bridge surfaces the error to the caller (OBJ-035), which can then abort the render with a clear error message. This prevents silent corruption where the bridge hangs or returns blank frames after a page crash.

**Reset behavior:** Calling `close()` clears the stored error. A subsequent `launch()` starts fresh.

### D14: Width and Height Must Be Positive Integers

**Decision:** The `PuppeteerBridgeConfig` constructor validates that `width` and `height` are positive integers. Non-integers throw `RangeError`.

**Rationale:** The bridge sets pixel-exact viewport dimensions via `page.setViewport()`. Viewport dimensions are inherently integer pixels. Silent rounding would mask errors upstream (e.g., a miscalculated composition width of `1920.5`). OBJ-010 handles canvas sizing; the bridge handles viewport sizing. Both must be exact.

## Acceptance Criteria

### FrameClock

- [ ] **AC-01:** `FrameClock` is importable from `src/engine/frame-clock.ts`. `new FrameClock({ fps: 30, totalFrames: 900 })` creates an instance with `fps === 30`, `totalFrames === 900`, `duration === 30.0`, `frameDuration` approximately `0.03333`.
- [ ] **AC-02:** `clock.frameToTimestamp(0) === 0.0`. `clock.frameToTimestamp(899)` approximately equals `29.9667` (899/30). `clock.frameToTimestamp(450) === 15.0`.
- [ ] **AC-03:** `clock.timestampToFrame(0) === 0`. `clock.timestampToFrame(15.0) === 450`. `clock.timestampToFrame(30.0)` clamps to `899` (not 900).
- [ ] **AC-04:** `clock.frameToTimestamp(-1)` throws `RangeError`. `clock.frameToTimestamp(900)` throws `RangeError` (for a 900-frame clock). `clock.frameToTimestamp(1.5)` throws `RangeError` (non-integer).
- [ ] **AC-05:** `clock.timestampToFrame(-0.1)` throws `RangeError`.
- [ ] **AC-06:** `FrameClock.fromDuration(30, 10.0)` creates a clock with `totalFrames === 300`. `FrameClock.fromDuration(30, 10.01)` creates a clock with `totalFrames === 301`.
- [ ] **AC-07:** `Array.from(clock.frames())` for a 3-frame clock at 30fps produces `[{ frame: 0, timestamp: 0, isFirst: true, isLast: false }, { frame: 1, timestamp: 1/30, isFirst: false, isLast: false }, { frame: 2, timestamp: 2/30, isFirst: false, isLast: true }]`.
- [ ] **AC-08:** `new FrameClock({ fps: 0, totalFrames: 100 })` throws `RangeError`. `new FrameClock({ fps: 30, totalFrames: 0 })` throws `RangeError`. `new FrameClock({ fps: -1, totalFrames: 100 })` throws `RangeError`. `new FrameClock({ fps: 30, totalFrames: 1.5 })` throws `RangeError`.
- [ ] **AC-09:** `FrameClock.fromDuration(30, -1)` throws `RangeError`. `FrameClock.fromDuration(0, 10)` throws `RangeError`.

### PuppeteerBridge

- [ ] **AC-10:** `PuppeteerBridge` is importable from `src/engine/puppeteer-bridge.ts`.
- [ ] **AC-11:** After `bridge.launch()`, `bridge.isLaunched === true` and `bridge.page` is a non-null Puppeteer `Page` instance.
- [ ] **AC-12:** After `bridge.launch()`, `bridge.evaluate(() => typeof window.depthkit)` resolves to `'object'`.
- [ ] **AC-13:** After launching and calling `window.depthkit.init()` via `evaluate()`, `bridge.captureFrame()` returns a `Buffer` whose first 8 bytes are the PNG magic number (`\x89PNG\r\n\x1a\n`).
- [ ] **AC-14:** `bridge.close()` terminates the browser process. `bridge.isLaunched === false` and `bridge.page === null` after close.
- [ ] **AC-15:** `bridge.close()` is idempotent — calling it twice does not throw.
- [ ] **AC-16:** `bridge.evaluate()` before `launch()` throws with message containing "not launched".
- [ ] **AC-17:** `bridge.captureFrame()` before `launch()` throws with message containing "not launched".
- [ ] **AC-18:** `bridge.launch()` when already launched throws with message containing "already launched".
- [ ] **AC-19:** The Puppeteer viewport after launch has `width` and `height` matching the config, and `deviceScaleFactor === 1`.
- [ ] **AC-20:** When `gpu` is `false` (default), the Chromium launch args include `--disable-gpu`. When `gpu` is `true`, `--disable-gpu` is NOT in the args.
- [ ] **AC-21:** `bridge.launch()` with `pagePath` pointing to a directory without `index.html` throws with a descriptive error message.
- [ ] **AC-22:** After `bridge.close()`, `bridge.launch()` can be called again (re-entrant lifecycle).
- [ ] **AC-23:** A page-side error thrown during `bridge.evaluate()` propagates as a rejected promise with the original error message.
- [ ] **AC-24:** `new PuppeteerBridge({ width: 0, height: 1080 })` throws `RangeError`. `new PuppeteerBridge({ width: 1920.5, height: 1080 })` throws `RangeError`.
- [ ] **AC-25:** The Chromium launch args always include `--allow-file-access-from-files`.
- [ ] **AC-26:** When `pagePath` is not provided, `launch()` resolves the default path relative to the module's own location and loads the page successfully (assuming the project has been built).
- [ ] **AC-27:** If an uncaught page error occurs (e.g., via `bridge.evaluate(() => { setTimeout(() => { throw new Error('async boom') }, 0) })`), the next call to `evaluate()` or `captureFrame()` rejects with an error message containing the original page error text.

## Edge Cases and Error Handling

### FrameClock

| Scenario | Expected Behavior |
|---|---|
| `fps` is 0, negative, `NaN`, or `Infinity` | Constructor throws `RangeError`: `"fps must be a positive finite number, got {value}"` |
| `totalFrames` is 0, negative, non-integer, `NaN`, or `Infinity` | Constructor throws `RangeError`: `"totalFrames must be a positive integer, got {value}"` |
| `frameToTimestamp()` with frame < 0 | Throws `RangeError`: `"frame must be in range [0, {totalFrames-1}], got {frame}"` |
| `frameToTimestamp()` with frame >= totalFrames | Throws `RangeError`: `"frame must be in range [0, {totalFrames-1}], got {frame}"` |
| `frameToTimestamp()` with non-integer frame | Throws `RangeError`: `"frame must be an integer, got {frame}"` |
| `timestampToFrame()` with negative timestamp | Throws `RangeError`: `"timestamp must be non-negative, got {timestamp}"` |
| `timestampToFrame()` with timestamp beyond duration | Clamps to `totalFrames - 1`. No error — this enables audio-aligned lookups where the timestamp may slightly exceed the video duration. |
| `fromDuration()` with non-positive duration | Throws `RangeError`: `"durationSeconds must be positive, got {value}"` |
| `fromDuration()` with very small duration (e.g., 0.001s at 30fps) | Produces `totalFrames = 1` via `Math.ceil()`. Valid. |
| `frames()` called multiple times | Returns a fresh generator each time. Generators are independent. |
| `totalFrames = 1` | Single-frame video. `frames()` yields one tick: `{ frame: 0, timestamp: 0, isFirst: true, isLast: true }`. |
| Floating-point precision: `frameToTimestamp(1)` at fps=30 | Returns `1 / 30` — standard JS floating-point. No special rounding. Precision is sufficient for video timing. |

### PuppeteerBridge

| Scenario | Expected Behavior |
|---|---|
| `width` or `height` ≤ 0 | Constructor throws `RangeError`: `"width and height must be positive integers"`. |
| Non-integer `width` or `height` | Constructor throws `RangeError`: `"width and height must be positive integers, got width={w}, height={h}"`. |
| `launch()` when already launched | Throws `Error`: `"PuppeteerBridge: already launched. Call close() first."` |
| `evaluate()` before launch | Throws `Error`: `"PuppeteerBridge: not launched. Call launch() first."` |
| `captureFrame()` before launch | Throws `Error`: `"PuppeteerBridge: not launched. Call launch() first."` |
| `close()` when not launched | No-op. Idempotent. |
| `close()` after close | No-op. Idempotent. |
| `launch()` after `close()` | Succeeds — fresh browser instance. Re-entrant lifecycle. Stored page error is cleared. |
| `pagePath` doesn't exist or lacks `index.html` | `launch()` throws `Error`: `"PuppeteerBridge: page not found at {path}. Run 'npm run build' first."` Check is performed before `page.goto()`. |
| Page fails to load (JS error in bundle) | `launch()` throws `Error` with the page error message. Detected by listening for page errors and verifying `window.depthkit` exists. |
| `window.depthkit` not found after page load | `launch()` throws `Error`: `"PuppeteerBridge: window.depthkit not found. The page bundle may be corrupt."` |
| `evaluate()` with non-serializable args | Puppeteer throws — error propagates unmodified. |
| Page function throws during `evaluate()` | Error propagates as a rejected Promise with the original error message. |
| Uncaught page error (pageerror event) | Bridge stores the error. Next `evaluate()` or `captureFrame()` rejects immediately with `Error`: `"PuppeteerBridge: page crashed with uncaught error: {originalMessage}"`. |
| Chromium crashes during operation | `evaluate()` / `captureFrame()` throw Puppeteer's native crash error. Caller (OBJ-035) handles retry/abort. |
| Very large viewport (e.g., 7680×4320) | Allowed — Puppeteer and Chromium handle it. May be slow or OOM on constrained machines. Not validated by the bridge. |
| `extraArgs` override a default arg | Allowed. Last occurrence of a Chromium flag wins. Documented as "use at your own risk." |
| Default `pagePath` and `dist/page/` doesn't exist | `launch()` throws the "page not found" error. The error message includes the resolved path so the user knows what's missing. |

## Test Strategy

### FrameClock — Unit Tests (`test/unit/frame-clock.test.ts`)

Pure synchronous tests, no I/O dependencies.

1. **Construction:** Valid configs create instances with correct readonly properties (`fps`, `totalFrames`, `duration`, `frameDuration`).
2. **`frameToTimestamp()`:** Test frame 0 → 0.0; last frame → `(totalFrames-1)/fps`; intermediate frames at 24fps and 30fps.
3. **`timestampToFrame()`:** Test round-trip: `timestampToFrame(frameToTimestamp(N)) === N` for all frames in a small clock. Test clamping: timestamp beyond duration → last frame.
4. **`frames()` iterator:** Verify length equals `totalFrames`. Verify first tick's `isFirst`, last tick's `isLast`. Verify every tick's `timestamp === frame / fps`. Verify calling `frames()` twice yields independent generators.
5. **`fromDuration()` factory:** Test exact durations (e.g., 10.0s at 30fps → 300 frames). Test fractional durations (10.01s at 30fps → 301 frames). Test very short durations (0.001s → 1 frame).
6. **Boundary: single-frame clock:** `totalFrames = 1` — `frames()` yields one tick with `isFirst: true, isLast: true`.
7. **Error cases:** All RangeError conditions from edge cases table — 9 distinct cases (fps: 0, negative, NaN, Infinity; totalFrames: 0, negative, non-integer, NaN, Infinity).
8. **Determinism (TC-06):** Same config always produces same results — trivially true for pure math but worth asserting as a property test.

### PuppeteerBridge — Integration Tests (`test/integration/puppeteer-bridge.test.ts`)

These tests launch real headless Chromium. They are slower (~2-5s per test) and should be tagged/separated from unit tests.

9. **Launch and verify:** `launch()` succeeds, `isLaunched === true`, `page` is non-null. `evaluate(() => typeof window.depthkit)` returns `'object'`.
10. **Viewport dimensions:** After launch, verify viewport matches config via `page.viewport()`.
11. **PNG capture:** Init depthkit on page, render a frame (add a colored mesh via evaluate), capture as PNG. Verify Buffer starts with PNG magic bytes. Verify image is not all-black (proves rendering + capture works).
12. **Close and re-launch:** `close()`, verify `isLaunched === false`, `launch()` again, verify it works.
13. **Double launch error:** `launch()` twice without close → error.
14. **Operations before launch:** `evaluate()` and `captureFrame()` before launch → errors.
15. **Missing page path:** Launch with nonexistent path → descriptive error.
16. **Page error propagation (synchronous):** `evaluate(() => { throw new Error('test') })` → rejected promise with 'test' in message.
17. **Page error propagation (uncaught/async):** Trigger an uncaught page error via evaluate, wait briefly, verify next `evaluate()` rejects with the stored error.
18. **GPU flag:** Launch with `gpu: false`, verify Chromium args include `--disable-gpu` (inspectable via `browser.process().spawnargs` or similar).
19. **`--allow-file-access-from-files` flag:** Verify it's always in the launch args regardless of `gpu` setting.
20. **Small viewport:** Launch with 100×100 viewport. Capture PNG. Verify buffer starts with PNG magic bytes.
21. **Non-integer dimensions:** `new PuppeteerBridge({ width: 1920.5, height: 1080 })` → `RangeError`.
22. **Default pagePath resolution:** Launch with no `pagePath` specified, verify page loads from `dist/page/` relative to the bridge module.

**Performance baseline (TC-02):** Test 11 provides a data point on single-frame launch+init+render+capture time. Log it but don't assert a threshold — that's OBJ-035/TC-02's concern.

**Relevant testable claims:**
- **TC-02** (render performance): Bridge launch + capture latency is the per-frame baseline.
- **TC-06** (deterministic output): Verify two captures of the same scene produce identical PNG buffers.
- **TC-11** (Docker/software WebGL): Tests run with `gpu: false` (SwiftShader) by default.

### Test Infrastructure Notes

- Integration tests require Puppeteer + Chromium installed. CI must not skip these.
- Tests should use small viewports (e.g., 320×240) to minimize memory and time, except where resolution matters.
- Each test should `close()` the bridge in an `afterEach` or `finally` block to prevent leaked Chromium processes.

## Integration Points

### Depends on

| Dependency | What OBJ-009 uses |
|---|---|
| **OBJ-001** (Project scaffolding) | `puppeteer` in dependencies. `src/engine/puppeteer-bridge.ts` and `src/engine/frame-clock.ts` stub files. `dist/page/` build output path. |

**Build-time dependency on OBJ-010:** The bridge does not import OBJ-010 code. It loads OBJ-010's built page (`dist/page/index.html`) as a file via Puppeteer. The bridge's `launch()` validation (checking for `window.depthkit`) assumes OBJ-010's page shell has been built. This is a build-time dependency, not a code-import dependency. The bridge works with whatever page is at `pagePath` and verifies the expected global exists.

### Consumed by

| Downstream | How it uses OBJ-009 |
|---|---|
| **OBJ-011** (Message protocol) | Imports `PuppeteerBridge`. Builds the full message protocol on top of `bridge.evaluate()`. Defines frame step commands, scene setup/teardown, texture loading — all implemented as `evaluate()` calls with structured payloads. |
| **OBJ-035** (Orchestrator) | Imports both `FrameClock` and `PuppeteerBridge`. Creates a `FrameClock` from the manifest's fps/duration. Iterates `clock.frames()`. For each tick, uses OBJ-011's protocol (built on the bridge) to send frame commands and capture frames. Pipes captured buffers to FFmpeg (OBJ-012). |
| **OBJ-038** (Audio sync) | Imports `FrameClock`. Uses `timestampToFrame()` to convert narration cue timestamps to frame boundaries. Uses `fromDuration()` to create clocks from audio file duration. |

### File Placement

```
depthkit/
  src/
    engine/
      frame-clock.ts           # EVOLVE from OBJ-001 stub
      puppeteer-bridge.ts      # EVOLVE from OBJ-001 stub
  test/
    unit/
      frame-clock.test.ts      # NEW — unit tests for FrameClock
    integration/
      puppeteer-bridge.test.ts # NEW — integration tests for PuppeteerBridge
```

## Open Questions

### OQ-A: Should the bridge expose console forwarding beyond `debug` mode?

The `debug` config option controls whether `page.on('console')` messages are forwarded to Node's console. This is sufficient for development. A more structured approach (e.g., returning console messages as part of `evaluate()` results, or emitting events) could be useful for production logging, but adds complexity. Deferred until a downstream objective identifies a concrete need.

### OQ-B: Should raw pixel capture be added later?

If FFmpeg benchmarks show that PNG decode overhead in the pipeline is significant (unlikely — FFmpeg's PNG decoder is highly optimized), a `captureRaw()` method could be added. The implementation would use `page.evaluate()` to call `gl.readPixels()` on the WebGL context, base64-encode the result for transfer, and decode to Buffer on the Node side. This bypasses HTML compositing (no HUD layers), so it would only be appropriate for scenes without HUD elements. Deferred per AP-05.

---

I believe this revision addresses all 10 issues raised by the Challenger:

1. **Issue 1 (unused imports):** Removed `PageInitConfig` and `RendererInfo` imports entirely.
2. **Issue 2 (raw capture):** Deferred `'raw'` format. `captureFrame()` returns PNG only. Removed `CaptureFormat` type. Documented reasoning in D7.
3. **Issue 3 (init responsibility):** Explicitly stated in `PuppeteerBridge` class doc and D6 that the bridge does NOT call `init()`.
4. **Issue 5 (capture mechanism):** Specified `page.screenshot({ type: 'png', encoding: 'binary' })` in D7 and the `captureFrame()` JSDoc. Noted it captures the full composited viewport.
5. **Issue 7 (file:// CORS):** Added `--allow-file-access-from-files` to default args in D8. Added binding constraint for OBJ-015 in D10. Added AC-25.
6. **Issue 8 (pagePath resolution):** Promoted to D11 with ESM-compatible `fileURLToPath(import.meta.url)` pattern for Node 18+. Added AC-26.
7. **Issue 9 (integer validation):** Changed to strict positive integer validation in D14. Throws `RangeError` for non-integers. Added AC-24.
8. **Issue 10 (page errors):** Added D13 for `pageerror` handling. Bridge stores uncaught errors and surfaces them on next operation. Added AC-27. Added test case 17.

Challenger, please verify these revisions and confirm whether the spec is ready for commit.

---

## Round 4 — spec_challenger

## Challenger Review — Round 4 (Verification)

Let me systematically verify each of my Round 2 issues against the revised spec.

**Issue 1 (unused imports):** ✅ Fixed. The `import type { PageInitConfig, RendererInfo }` line is gone from the PuppeteerBridge interface.

**Issue 2 (raw capture):** ✅ Fixed. `CaptureFormat` type removed. `captureFrame()` returns PNG only. D7 documents the deferral with clear rationale. OQ-B documents the future path. AC-13 (old raw capture AC) is gone.

**Issue 3 (init responsibility):** ✅ Fixed. Class JSDoc explicitly states "The bridge does NOT call window.depthkit.init()." D6 repeats this.

**Issue 5 (capture mechanism):** ✅ Fixed. D7 specifies `page.screenshot({ type: 'png', encoding: 'binary' })`. JSDoc on `captureFrame()` explains it captures the full composited viewport including future HUD layers.

**Issue 7 (file:// CORS):** ✅ Fixed. `--allow-file-access-from-files` added to D8's default args. D10 documents the binding constraint for OBJ-015. AC-25 verifies the flag is present.

**Issue 8 (pagePath resolution):** ✅ Fixed. Promoted to D11 with the correct `fileURLToPath(import.meta.url)` pattern for Node 18+. AC-26 verifies default resolution works.

**Issue 9 (integer validation):** ✅ Fixed. D14 specifies strict positive integer validation. Constructor throws `RangeError` for non-integers. AC-24 tests this.

**Issue 10 (page errors):** ✅ Fixed. D13 specifies `page.on('pageerror')` handling. Stored error surfaces on next operation. AC-27 tests async page errors. Test case 17 added.

All major and minor issues are structurally addressed in the revised spec. Let me do one final scan for anything new or previously missed.

---

**New scan — minor items:**

1. **AC-27 test timing:** The AC says "e.g., via `bridge.evaluate(() => { setTimeout(() => { throw new Error('async boom') }, 0) })`" — the `setTimeout` trick is correct for triggering an uncaught error, but the test needs a brief `await` (e.g., `await new Promise(r => setTimeout(r, 50))`) between the triggering evaluate and the verifying evaluate, to allow the pageerror event to fire. The test strategy's case 17 says "wait briefly" which covers this. Acceptable.

2. **D13 reset behavior:** "Calling `close()` clears the stored error." This is stated in D13 and also in the edge cases table ("launch() after close() — Stored page error is cleared"). Consistent. ✅

3. **Spec mentions `NaN` and `Infinity` in FrameClock error cases table but AC-08 only tests 0, negative, and non-integer for totalFrames.** The edge cases table covers NaN/Infinity, but the ACs don't explicitly test them. This is minor — the edge cases table is normative and the test strategy item 7 says "All RangeError conditions from edge cases table — 9 distinct cases." An implementer following the test strategy would cover them. Acceptable.

4. **One vocabulary check:** The spec uses "frame clock" and "Puppeteer bridge" — neither is in the seed vocabulary Section 2, but both are module names from the seed's project structure (Section 4.5: `frame-clock.ts`, `puppeteer-bridge.ts`). These are implementation artifact names, not domain vocabulary. No violation.

The spec is clean. All issues resolved. No new critical or major issues.

CONCLUSION:

The spec for OBJ-009 is approved. It defines two cleanly separated modules — `FrameClock` (pure stateless frame-to-timestamp mapping) and `PuppeteerBridge` (Puppeteer lifecycle, page loading, evaluate primitive, PNG frame capture) — that together implement the virtualized clock mechanism per C-03. Key decisions: PNG-only capture via `page.screenshot()`, `file://` page loading with `--allow-file-access-from-files` for texture CORS, ESM-compatible default pagePath resolution, strict integer viewport validation, and uncaught page error surfacing via `pageerror` listener. Raw RGBA capture deferred per AP-05.

Let me write the final spec and update meta.json.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Now let me read the existing meta.json before updating it:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-009",
     3→  "description": "Virtualized clock -- global frame-to-timestamp mapping (t = frame / fps), frame counter mechanics, deterministic frame stepping guarantee per C-03. Pure utility with no scene awareness. The clock provides the global frame number and timestamp; per-scene normalized time computation is handled by the scene sequencer (OBJ-036). Ensures zero dropped frames regardless of scene complexity or hardware speed.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Narrowed to pure global clock -- per-scene time normalization moved to OBJ-036."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "content": "# Specification: OBJ-009 \u2014 Virtualized Clock and Puppeteer Bridge\n\n## Summary\n\nOBJ-009 delivers two modules that together implement the virtualized clock mechanism defined in C-03. First, `FrameClock` (`src/engine/frame-clock.ts`) \u2014 a pure, stateless utility that maps frame numbers to timestamps and provides an iterator for deterministic frame stepping. It has no scene awareness; per-scene normalized time is OBJ-036's responsibility. Second, `PuppeteerBridge` (`src/engine/puppeteer-bridge.ts`) \u2014 the Puppeteer lifecycle manager that launches headless Chromium, loads the OBJ-010 page shell, exposes an `evaluate()` primitive for downstream message protocols (OBJ-011), and captures rendered frames as PNG pixel buffers via Puppeteer's screenshot API. Together, these two modules provide the building blocks that OBJ-035 (orchestrator) composes into the deterministic render loop from seed Section 4.4.\n\n## Interface Contract\n\n### Module: `src/engine/frame-clock.ts`\n\n```typescript\n/**\n * Configuration for creating a FrameClock.\n */\nexport interface FrameClockConfig {\n  /** Frames per second. Must be a positive finite number. */\n  fps: number;\n  /** Total number of frames in the composition. Must be a positive integer. */\n  totalFrames: number;\n}\n\n/**\n * Information about a single frame tick.\n * Yielded by FrameClock.frames() iterator.\n */\nexport interface FrameTick {\n  /** Zero-indexed frame number: 0 to totalFrames - 1 */\n  frame: number;\n  /** Absolute timestamp in seconds: frame / fps */\n  timestamp: number;\n  /** Whether this is the first frame (frame === 0) */\n  isFirst: boolean;\n  /** Whether this is the last frame (frame === totalFrames - 1) */\n  isLast: boolean;\n}\n\n/**\n * Pure, immutable utility for deterministic frame-to-timestamp mapping.\n * No I/O, no scene awareness, no side effects.\n *
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json",
  "content": "{\n  \"id\": \"OBJ-009\",\n  \"description\": \"Virtualized clock -- global frame-to-timestamp mapping (t = frame / fps), frame counter mechanics, deterministic frame stepping guarantee per C-03. Pure utility with no scene awareness. The clock provides the global frame number and timestamp; per-scene normalized time computation is handled by the scene sequencer (OBJ-036). Also delivers the PuppeteerBridge -- Puppeteer lifecycle manager for launching headless Chromium, loading the page shell, providing evaluate() primitive for downstream protocols, and capturing rendered frames as PNG buffers.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"spec-deliberation\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-001\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"review_status\": \"approved\",\n  \"notes\": \"Spec approved after 4-round deliberation. Two modules: FrameClock (pure stateless frame-to-timestamp mapping) and PuppeteerBridge (Puppeteer lifecycle, page loading via file://, evaluate() primitive, PNG capture via page.screenshot()). Key decisions: PNG-only capture (raw deferred per AP-05), --allow-file-access-from-files for texture CORS, ESM-compatible pagePath resolution via fileURLToPath, strict integer viewport validation, uncaught page error surfacing via pageerror listener. Binding constraint for OBJ-015: texture paths must be absolute file:// URLs or data URIs.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json has been updated successfully.
Now let me commit:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Show working tree status"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commit messages"
}
[Tool Result] e320132 spec(OBJ-016): manifest loader and validator behavioral specification
baa00bf spec(OBJ-013): FFmpeg encoder specification -- approved after 4-round deliberation
306fe35 spec(OBJ-031): gentle_float camera path preset specification
d3e98dd Specify OBJ-026: static camera path preset
065cb85 spec(OBJ-005): scene geometry type contract — PlaneSlot, SceneGeometry, registry
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-009/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/transcript.md
	nodes/OBJ-002/transcript.md
	nodes/OBJ-003/transcript.md
	nodes/OBJ-004/transcript.md
	nodes/OBJ-005/transcript.md
	nodes/OBJ-006/transcript.md
	nodes/OBJ-007/transcript.md
	nodes/OBJ-009/output.md
	nodes/OBJ-010/transcript.md
	nodes/OBJ-013/transcript.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-026/transcript.md
	nodes/OBJ-031/transcript.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-009/output.md nodes/OBJ-009/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-009): virtualized clock and Puppeteer bridge specification\n\nTwo modules: FrameClock (pure stateless frame-to-timestamp mapping,\niterator for deterministic frame stepping) and PuppeteerBridge\n(Puppeteer lifecycle, file:// page loading, evaluate() primitive,\nPNG capture via page.screenshot()). Key decisions: PNG-only capture\n(raw deferred per AP-05), --allow-file-access-from-files for texture\nCORS, ESM-compatible pagePath resolution, strict integer viewport\nvalidation, uncaught page error surfacing via pageerror listener.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-009 spec files"
}
[Tool Result] [master 82035d9] spec(OBJ-009): virtualized clock and Puppeteer bridge specification
 2 files changed, 559 insertions(+), 4 deletions(-)
 create mode 100644 nodes/OBJ-009/output.md
Committed. The OBJ-009 specification is finalized and written to disk. 

**Summary of what was approved:**

- **FrameClock** (`src/engine/frame-clock.ts`) — Pure, immutable, stateless utility. Maps frame numbers ↔ timestamps via `frameToTimestamp()` / `timestampToFrame()`. Provides a `frames()` generator for the render loop. `fromDuration()` factory using `Math.ceil()`. 9 acceptance criteria covering happy paths, boundary conditions, and all error states.

- **PuppeteerBridge** (`src/engine/puppeteer-bridge.ts`) — Puppeteer lifecycle manager. Launches headless Chromium with software rendering by default (C-11), loads the page shell via `file://`, validates `window.depthkit` exists, exposes `evaluate()` as the raw primitive for OBJ-011's message protocol, captures frames as PNG via `page.screenshot()`. Surfaces uncaught page errors via `pageerror` listener. 18 acceptance criteria covering launch, capture, error propagation, lifecycle, and configuration validation.

- **14 design decisions** documented with rationale and alternatives considered.
- **Key binding constraints** established for downstream: OBJ-015 must use absolute `file://` paths or data URIs for textures; OBJ-011 builds protocol on `evaluate()`; OBJ-035 composes both modules.
