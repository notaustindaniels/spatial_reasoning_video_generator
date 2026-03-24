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

**Rationale:** `Math.ceil()` ensures the video duration is at least as long as the requested duration. A 10-second video at 30fps = 300 frames, covering `[0, 9.967s]`. With `Math.ceil()`, 10.01 seconds -> 301 frames, ensuring the last moment is captured. `Math.floor()` would truncate, potentially cutting off the end of audio (violating C-07). `Math.round()` could go either way, making behavior unpredictable at boundaries.

### D6: PuppeteerBridge Provides Raw Primitives, Not Domain Logic

**Decision:** The bridge exposes `evaluate()` and `captureFrame()` — raw primitives. It does NOT expose `renderFrame()`, `initScene()`, or any depthkit-specific operations. Those are defined by OBJ-011 (message protocol) using `evaluate()` as the transport. The bridge does NOT call `window.depthkit.init()` — initialization of the Three.js renderer is the responsibility of OBJ-011 or OBJ-035 via `evaluate()`.

**Rationale:** OBJ-011 owns the full cross-boundary message contract. If the bridge pre-defined `renderFrame()`, it would duplicate OBJ-011's responsibility and couple the bridge to the page API. The bridge is a transport layer; OBJ-011 defines the protocol; OBJ-035 orchestrates.

**Exception:** `launch()` loads the page and verifies `window.depthkit` is defined — this minimal check ensures the page shell (OBJ-010) loaded correctly, without coupling to its internal API.

### D7: PNG-Only Capture via `page.screenshot()`

**Decision:** `captureFrame()` returns PNG data exclusively, using Puppeteer's `page.screenshot({ type: 'png', encoding: 'binary' })`. There is no raw RGBA capture format.

**Rationale:** `page.screenshot()` captures the **full composited viewport** — both the WebGL canvas and any HTML elements positioned above it. This is the correct behavior for future HUD layers (seed vocabulary), where titles/captions rendered as HTML/CSS must appear in the captured frame.

Raw RGBA extraction was considered and deferred:
- Extracting raw pixels from a WebGL canvas via `gl.readPixels()` requires transferring `width * height * 4` bytes through Puppeteer's serialization layer (JSON-encoded base64), which is slow for 1920x1080 frames (~8MB per frame).
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

**Rationale:** Combined with OBJ-010's `renderer.setPixelRatio(1)`, this ensures 1:1 pixel mapping. A 1920x1080 viewport produces a 1920x1080 screenshot. HiDPI scaling would silently double the resolution, breaking FFmpeg encoding and violating C-05 (deterministic output).

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
| `width` or `height` <= 0 | Constructor throws `RangeError`: `"width and height must be positive integers"`. |
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
| Very large viewport (e.g., 7680x4320) | Allowed — Puppeteer and Chromium handle it. May be slow or OOM on constrained machines. Not validated by the bridge. |
| `extraArgs` override a default arg | Allowed. Last occurrence of a Chromium flag wins. Documented as "use at your own risk." |
| Default `pagePath` and `dist/page/` doesn't exist | `launch()` throws the "page not found" error. The error message includes the resolved path so the user knows what's missing. |

## Test Strategy

### FrameClock — Unit Tests (`test/unit/frame-clock.test.ts`)

Pure synchronous tests, no I/O dependencies.

1. **Construction:** Valid configs create instances with correct readonly properties (`fps`, `totalFrames`, `duration`, `frameDuration`).
2. **`frameToTimestamp()`:** Test frame 0 -> 0.0; last frame -> `(totalFrames-1)/fps`; intermediate frames at 24fps and 30fps.
3. **`timestampToFrame()`:** Test round-trip: `timestampToFrame(frameToTimestamp(N)) === N` for all frames in a small clock. Test clamping: timestamp beyond duration -> last frame.
4. **`frames()` iterator:** Verify length equals `totalFrames`. Verify first tick's `isFirst`, last tick's `isLast`. Verify every tick's `timestamp === frame / fps`. Verify calling `frames()` twice yields independent generators.
5. **`fromDuration()` factory:** Test exact durations (e.g., 10.0s at 30fps -> 300 frames). Test fractional durations (10.01s at 30fps -> 301 frames). Test very short durations (0.001s -> 1 frame).
6. **Boundary: single-frame clock:** `totalFrames = 1` — `frames()` yields one tick with `isFirst: true, isLast: true`.
7. **Error cases:** All RangeError conditions from edge cases table — 9 distinct cases (fps: 0, negative, NaN, Infinity; totalFrames: 0, negative, non-integer, NaN, Infinity).
8. **Determinism (TC-06):** Same config always produces same results — trivially true for pure math but worth asserting as a property test.

### PuppeteerBridge — Integration Tests (`test/integration/puppeteer-bridge.test.ts`)

These tests launch real headless Chromium. They are slower (~2-5s per test) and should be tagged/separated from unit tests.

9. **Launch and verify:** `launch()` succeeds, `isLaunched === true`, `page` is non-null. `evaluate(() => typeof window.depthkit)` returns `'object'`.
10. **Viewport dimensions:** After launch, verify viewport matches config via `page.viewport()`.
11. **PNG capture:** Init depthkit on page, render a frame (add a colored mesh via evaluate), capture as PNG. Verify Buffer starts with PNG magic bytes. Verify image is not all-black (proves rendering + capture works).
12. **Close and re-launch:** `close()`, verify `isLaunched === false`, `launch()` again, verify it works.
13. **Double launch error:** `launch()` twice without close -> error.
14. **Operations before launch:** `evaluate()` and `captureFrame()` before launch -> errors.
15. **Missing page path:** Launch with nonexistent path -> descriptive error.
16. **Page error propagation (synchronous):** `evaluate(() => { throw new Error('test') })` -> rejected promise with 'test' in message.
17. **Page error propagation (uncaught/async):** Trigger an uncaught page error via evaluate, wait briefly, verify next `evaluate()` rejects with the stored error.
18. **GPU flag:** Launch with `gpu: false`, verify Chromium args include `--disable-gpu` (inspectable via `browser.process().spawnargs` or similar).
19. **`--allow-file-access-from-files` flag:** Verify it's always in the launch args regardless of `gpu` setting.
20. **Small viewport:** Launch with 100x100 viewport. Capture PNG. Verify buffer starts with PNG magic bytes.
21. **Non-integer dimensions:** `new PuppeteerBridge({ width: 1920.5, height: 1080 })` -> `RangeError`.
22. **Default pagePath resolution:** Launch with no `pagePath` specified, verify page loads from `dist/page/` relative to the bridge module.

**Performance baseline (TC-02):** Test 11 provides a data point on single-frame launch+init+render+capture time. Log it but don't assert a threshold — that's OBJ-035/TC-02's concern.

**Relevant testable claims:**
- **TC-02** (render performance): Bridge launch + capture latency is the per-frame baseline.
- **TC-06** (deterministic output): Verify two captures of the same scene produce identical PNG buffers.
- **TC-11** (Docker/software WebGL): Tests run with `gpu: false` (SwiftShader) by default.

### Test Infrastructure Notes

- Integration tests require Puppeteer + Chromium installed. CI must not skip these.
- Tests should use small viewports (e.g., 320x240) to minimize memory and time, except where resolution matters.
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
