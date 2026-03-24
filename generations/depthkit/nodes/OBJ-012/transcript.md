# Deliberation Transcript: OBJ-012

---

## Round 1 — spec_author

Let me start by understanding the current state of the codebase — what OBJ-009 already provides for the Puppeteer bridge, and what the page shell looks like.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the existing codebase to understand what OBJ-009 already provides and what the current state looks like.
[Tool: Glob]
  Input: {
  "pattern": "**/puppeteer-bridge*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/ffmpeg*"
}

[Tool: Glob]
  Input: {
  "pattern": "**/page-types*"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/frame-capture*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-009/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-012/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-012",
     3→  "description": "Puppeteer bridge and frame capture -- Puppeteer launch configuration (headless mode, viewport size, WebGL flags), page loading strategy, frame capture via CDP Page.captureScreenshot vs canvas.toDataURL vs canvas.toBlob, pixel buffer extraction and format (PNG vs raw RGBA). Implements the browser-side capture half of C-02 (Puppeteer + Three.js + FFmpeg pipeline).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-011"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Depends on message protocol (OBJ-011) for communication with the page."
    12→}
    13→
[Tool Error] File content (10461 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "limit": 120
}
[Tool Result]      1→# Specification: OBJ-009 — Virtualized Clock and Puppeteer Bridge
     2→
     3→## Summary
     4→
     5→OBJ-009 delivers two modules that together implement the virtualized clock mechanism defined in C-03. First, `FrameClock` (`src/engine/frame-clock.ts`) — a pure, stateless utility that maps frame numbers to timestamps and provides an iterator for deterministic frame stepping. It has no scene awareness; per-scene normalized time is OBJ-036's responsibility. Second, `PuppeteerBridge` (`src/engine/puppeteer-bridge.ts`) — the Puppeteer lifecycle manager that launches headless Chromium, loads the OBJ-010 page shell, exposes an `evaluate()` primitive for downstream message protocols (OBJ-011), and captures rendered frames as PNG pixel buffers via Puppeteer's screenshot API. Together, these two modules provide the building blocks that OBJ-035 (orchestrator) composes into the deterministic render loop from seed Section 4.4.
     6→
     7→## Interface Contract
     8→
     9→### Mo... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": 120,
  "limit": 200
}
[Tool Result]    120→  pagePath?: string;
   121→  /**
   122→   * Headless mode. Default: true.
   123→   * Set to false for debugging (opens visible browser window).
   124→   */
   125→  headless?: boolean;
   126→  /**
   127→   * Path to a custom Chromium/Chrome executable.
   128→   * If not provided, uses Puppeteer's bundled Chromium.
   129→   */
   130→  executablePath?: string;
   131→  /**
   132→   * Enable GPU-accelerated rendering. Default: false.
   133→   *
   134→   * When false (default): adds --disable-gpu and related flags
   135→   * for software rendering via SwiftShader (C-11 compliance).
   136→   *
   137→   * When true: omits GPU-disabling flags, allowing hardware
   138→   * acceleration when available. Faster but requires GPU passthrough
   139→   * in Docker/CI environments.
   140→   */
   141→  gpu?: boolean;
   142→  /**
   143→   * Additional Chromium launch arguments.
   144→   * Appended after the bridge's default arguments.
   145→   */
   146→  extraArgs?: string... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": 319,
  "limit": 200
}
[Tool Result]    319→
   320→**Rationale:** C-11 mandates software rendering correctness. The engine must run in Docker without GPU passthrough. SwiftShader (Chromium's software WebGL) is available by default in Puppeteer's bundled Chromium. GPU acceleration is opt-in for environments where it's available.
   321→
   322→**Default Chromium args:**
   323→```
   324→--disable-gpu                    // Software WebGL (SwiftShader) — omitted when gpu=true
   325→--disable-dev-shm-usage          // Docker: use /tmp instead of /dev/shm
   326→--no-sandbox                     // Docker: required when running as root
   327→--disable-setuid-sandbox         // Docker: companion to --no-sandbox
   328→--hide-scrollbars                // Prevent scrollbar interference
   329→--mute-audio                     // No audio output from browser
   330→--allow-file-access-from-files   // Enable file:// CORS for texture loading
   331→```
   332→
   333→When `gpu: true`, `--disable-gpu` is omitted; all other args rem... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": 518
}
[Tool Result]    518→|---|---|
   519→| **OBJ-001** (Project scaffolding) | `puppeteer` in dependencies. `src/engine/puppeteer-bridge.ts` and `src/engine/frame-clock.ts` stub files. `dist/page/` build output path. |
   520→
   521→**Build-time dependency on OBJ-010:** The bridge does not import OBJ-010 code. It loads OBJ-010's built page (`dist/page/index.html`) as a file via Puppeteer. The bridge's `launch()` validation (checking for `window.depthkit`) assumes OBJ-010's page shell has been built. This is a build-time dependency, not a code-import dependency. The bridge works with whatever page is at `pagePath` and verifies the expected global exists.
   522→
   523→### Consumed by
   524→
   525→| Downstream | How it uses OBJ-009 |
   526→|---|---|
   527→| **OBJ-011** (Message protocol) | Imports `PuppeteerBridge`. Builds the full message protocol on top of `bridge.evaluate()`. Defines frame step commands, scene setup/teardown, texture loading — all implemented as `evaluate()` calls with structure... [truncated]
Let me also check OBJ-013 and other related objectives to understand the full engine architecture, particularly which objective covers FFmpeg encoding.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-013/**"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-049/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/transcript.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-043/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-043/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-013 — FFmpeg Encoder
     2→
     3→## Summary
     4→
     5→OBJ-013 implements the FFmpeg encoding module (`src/engine/ffmpeg-encoder.ts`) — the final stage of the rendering pipeline that receives raw pixel buffers via its API, pipes them to an FFmpeg child process over stdin, and produces an H.264-encoded MP4 file. This module is deliberately independent of Puppeteer: it accepts `Buffer` data from any source, making it testable in isolation and reusable if the frame-capture mechanism changes. It implements the encoding half of constraint C-02 and supports the determinism guarantee of C-05.
     6→
     7→Audio muxing is **out of scope** — that is OBJ-014's responsibility. This module produces a video-only MP4.
     8→
     9→## Interface Contract
    10→
    11→```typescript
    12→// src/engine/ffmpeg-encoder.ts
    13→
    14→/**
    15→ * Supported input pixel formats for frame data piped to FFmpeg.
    16→ * - 'png': Each frame is a complete PNG-encod... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-049",
     3→  "description": "Software rendering configuration -- SwiftShader/ANGLE flags for headless Chromium, --disable-gpu and related Puppeteer launch args for software WebGL, GPU detection and optional GPU acceleration flags when available. Ensures correctness with software rendering per C-11 (engine must render correctly without GPU passthrough).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-012"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 interface. Covers C-11."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-043/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-043",
     3→  "description": "HUD layer system -- 2D overlay rendered on top of the 3D scene for titles, captions, subtitles, and UI elements. Implemented as HTML/CSS elements positioned absolutely over the Three.js canvas in headless Chromium, not affected by perspective projection. Viewport-pinned positioning. Per AP-07 (never put text in parallax planes) and OQ-03 (subtitle/caption overlay scope for V1).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-010", "OBJ-012"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 spatial feature. Medium priority. Addresses OQ-03."
    12→}
    13→
Let me check the existing implementation to understand what's already been built.
[Tool: Glob]
  Input: {
  "pattern": "**/src/engine/**"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/page/**"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**"
}

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/**/*.ts"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "offset": 80,
  "limit": 200
}
[Tool Result]     80→
    81→  /**
    82→   * Optional path to FFmpeg binary. If not provided, resolves via resolveFFmpegPath().
    83→   */
    84→  ffmpegPath?: string;
    85→}
    86→
    87→/**
    88→ * Result returned when encoding completes successfully.
    89→ */
    90→export interface FFmpegEncoderResult {
    91→  /** Absolute path to the output MP4 file. */
    92→  outputPath: string;
    93→
    94→  /** Total number of frames written. */
    95→  frameCount: number;
    96→
    97→  /** Total encoding duration in milliseconds (wall-clock time from start() to finalize()). */
    98→  durationMs: number;
    99→
   100→  /** FFmpeg's stderr output (contains encoding stats, warnings). Capped at last 1MB. */
   101→  ffmpegLog: string;
   102→}
   103→
   104→/**
   105→ * Custom error class for FFmpeg encoding failures.
   106→ * Contains the FFmpeg stderr log for diagnosis.
   107→ */
   108→export class FFmpegEncoderError extends Error {
   109→  constructor(
   110→    message: st... [truncated]
Now I have a complete picture of the architecture. Let me also check the OBJ-011 implementation (page-protocol) and the page shell (OBJ-010) for completeness.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-010/**"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-011/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/transcript.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/transcript.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "limit": 60
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
Now I have the complete picture. Let me summarize what I've found:

- **OBJ-009** (verified): `FrameClock` + `PuppeteerBridge` with `launch()`, `evaluate()`, `captureFrame()` (PNG via `page.screenshot()`), `close()`
- **OBJ-010** (verified): Three.js page shell — `window.depthkit` with `init()`, `renderFrame()`, `dispose()`
- **OBJ-011** (verified): Message protocol — `PageProtocol` with `setupScene()`, `renderFrame()`, `teardownScene()`, multi-pass compositing
- **OBJ-013** (verified): FFmpeg encoder — `FFmpegEncoder` with `start()`, `writeFrame(Buffer)`, `finalize()`, accepts PNG or raw RGBA
- **OBJ-043** (open, depends on OBJ-012): HUD layer system — HTML/CSS overlays captured in frames
- **OBJ-049** (open, depends on OBJ-012): Software rendering configuration — SwiftShader correctness

OBJ-012 sits between the rendered page and the FFmpeg encoder. OBJ-009 has a basic `captureFrame()` via `page.screenshot()`, but OBJ-012's role is the **production-quality frame capture pipeline** — evaluating capture methods, providing CDP-level optimization, supporting format selection aligned with OBJ-013's input, and establishing the capture contract that downstream objectives depend on.

---

Here is my proposed specification:

---

# Specification: OBJ-012 — Frame Capture Pipeline

## Summary

OBJ-012 delivers the `FrameCapture` class (`src/engine/frame-capture.ts`) — the configurable frame extraction service that sits between OBJ-011's rendered page state and OBJ-013's FFmpeg encoder input. It uses the Chrome DevTools Protocol (CDP) directly for optimized viewport screenshot capture, bypassing Puppeteer's `page.screenshot()` wrapper to reduce per-frame overhead. It also provides a canvas-only capture path via WebGL `readPixels()` for raw RGBA extraction when HUD layers are not present. The module tracks capture timing statistics for performance monitoring and establishes the capture format contract that OBJ-035 (orchestrator) uses to bridge rendering and encoding. This implements the "capture" step in seed Section 4.4 step 3f and completes the browser-side capture half of C-02.

## Interface Contract

### Module: `src/engine/frame-capture.ts`

```typescript
import type { PuppeteerBridge } from './puppeteer-bridge.js';

/**
 * Capture strategy determines both the capture mechanism and the
 * output buffer format. Each strategy has distinct capabilities
 * and performance characteristics.
 *
 * - 'viewport-png': CDP Page.captureScreenshot with optimizeForSpeed.
 *   Captures the full composited viewport — the WebGL canvas plus
 *   any HTML/CSS elements layered on top (HUD layers per OBJ-043).
 *   Output is a PNG-encoded Buffer. This is the production default.
 *
 * - 'canvas-png': Extracts the canvas content via page.evaluate()
 *   calling canvas.toDataURL('image/png'). Captures only the WebGL
 *   canvas — HTML overlays are NOT included. Output is a PNG-encoded
 *   Buffer (base64-decoded from toDataURL result). Useful for
 *   canvas-only capture when HUD layers are absent.
 *
 * - 'canvas-rgba': Extracts raw pixel data via page.evaluate()
 *   calling gl.readPixels() on the WebGL context. Captures only the
 *   WebGL canvas — HTML overlays are NOT included. Output is a raw
 *   RGBA Buffer (width * height * 4 bytes), vertically flipped to
 *   top-to-bottom row order (readPixels returns bottom-to-top).
 *   Pairs with OBJ-013's frameFormat: 'rgba' for zero-decode piping
 *   to FFmpeg. Highest throughput for canvas-only scenes but largest
 *   per-frame buffer size.
 */
export type CaptureStrategy = 'viewport-png' | 'canvas-png' | 'canvas-rgba';

/**
 * Configuration for the FrameCapture service.
 */
export interface FrameCaptureConfig {
  /**
   * Capture strategy. Default: 'viewport-png'.
   * See CaptureStrategy documentation for trade-offs.
   */
  strategy?: CaptureStrategy;

  /**
   * The CSS selector of the canvas element on the page.
   * Required for 'canvas-png' and 'canvas-rgba' strategies.
   * Ignored for 'viewport-png' (captures full viewport).
   * Default: '#depthkit-canvas' (matches OBJ-010's page shell).
   */
  canvasSelector?: string;
}

/**
 * Result of a single frame capture.
 */
export interface CaptureResult {
  /** The captured pixel data. Format depends on strategy. */
  data: Buffer;

  /**
   * The format of the data buffer.
   * - 'png': Buffer contains a complete PNG image.
   * - 'rgba': Buffer contains raw RGBA pixels,
   *   width * height * 4 bytes, top-to-bottom row order.
   */
  format: 'png' | 'rgba';

  /** Frame width in pixels. */
  width: number;

  /** Frame height in pixels. */
  height: number;

  /** Time taken for this capture in milliseconds. */
  captureMs: number;
}

/**
 * Aggregate capture statistics for performance monitoring.
 */
export interface CaptureStats {
  /** Total number of frames captured. */
  captureCount: number;

  /** Total capture time across all frames in milliseconds. */
  totalCaptureMs: number;

  /** Average capture time per frame in milliseconds. 0 if no captures. */
  averageCaptureMs: number;

  /** Minimum capture time across all frames. Infinity if no captures. */
  minCaptureMs: number;

  /** Maximum capture time across all frames. 0 if no captures. */
  maxCaptureMs: number;

  /** The configured strategy. */
  strategy: CaptureStrategy;
}

/**
 * Error class for frame capture failures.
 */
export class FrameCaptureError extends Error {
  /** Error category for programmatic handling. */
  readonly code: FrameCaptureErrorCode;
  readonly details?: Record<string, unknown>;

  constructor(code: FrameCaptureErrorCode, message: string, details?: Record<string, unknown>);
}

export type FrameCaptureErrorCode =
  | 'BRIDGE_NOT_LAUNCHED'     // PuppeteerBridge is not launched
  | 'CANVAS_NOT_FOUND'        // Canvas element not found (canvas strategies)
  | 'WEBGL_CONTEXT_LOST'      // WebGL context is lost
  | 'CAPTURE_FAILED'          // CDP or canvas capture failed
  | 'INVALID_BUFFER'          // Captured buffer is empty or corrupt
  ;

/**
 * Configurable frame capture service for the depthkit rendering pipeline.
 *
 * Sits between OBJ-011's renderFrame() (which renders a frame to the page)
 * and OBJ-013's writeFrame() (which pipes the buffer to FFmpeg). The
 * orchestrator (OBJ-035) calls capture() after each renderFrame() to
 * extract the rendered pixels.
 *
 * The FrameCapture does NOT own the PuppeteerBridge lifecycle. The caller
 * (OBJ-035 orchestrator) creates the bridge, launches it, then creates
 * FrameCapture with the bridge reference.
 *
 * Usage:
 *   const bridge = new PuppeteerBridge({ width: 1920, height: 1080 });
 *   await bridge.launch();
 *   const capture = new FrameCapture(bridge);
 *   // ... render frames via PageProtocol ...
 *   const result = await capture.capture();
 *   await encoder.writeFrame(result.data);
 *   // ... after all frames ...
 *   console.log(capture.getStats());
 */
export class FrameCapture {
  constructor(bridge: PuppeteerBridge, config?: FrameCaptureConfig);

  /**
   * Capture the current state of the page as a pixel buffer.
   *
   * The caller must ensure a frame has been rendered (via
   * PageProtocol.renderFrame()) before calling capture().
   * This method captures whatever is currently displayed.
   *
   * For 'viewport-png':
   *   Uses CDP Page.captureScreenshot with:
   *   - format: 'png'
   *   - optimizeForSpeed: true
   *   - fromSurface: true
   *   Decodes the base64 response to a Buffer.
   *
   * For 'canvas-png':
   *   Uses bridge.evaluate() to call canvas.toDataURL('image/png')
   *   on the canvas element identified by canvasSelector.
   *   Strips the data URI prefix and decodes base64 to a Buffer.
   *
   * For 'canvas-rgba':
   *   Uses bridge.evaluate() to call gl.readPixels() on the
   *   WebGL context, base64-encodes the Uint8Array on the page,
   *   transfers the string, and decodes to a Buffer on the Node side.
   *   The buffer is vertically flipped from bottom-to-top (WebGL native)
   *   to top-to-bottom (image convention) before returning.
   *
   * @returns CaptureResult with the pixel buffer and metadata.
   * @throws FrameCaptureError with appropriate code on failure.
   */
  capture(): Promise<CaptureResult>;

  /**
   * Returns aggregate capture statistics.
   * Statistics accumulate over the lifetime of this FrameCapture instance.
   */
  getStats(): CaptureStats;

  /**
   * Resets capture statistics to zero.
   */
  resetStats(): void;

  /**
   * The resolved configuration (with defaults applied).
   */
  readonly strategy: CaptureStrategy;

  /**
   * Width and height from the PuppeteerBridge config.
   * Used for buffer size validation (canvas-rgba) and
   * CaptureResult metadata.
   */
  readonly width: number;
  readonly height: number;
}
```

## Design Decisions

### D1: CDP Direct Capture over page.screenshot()

**Decision:** The `viewport-png` strategy uses CDP `Page.captureScreenshot` directly via the Puppeteer CDPSession, bypassing `page.screenshot()`.

**Rationale:** Puppeteer's `page.screenshot()` is a convenience wrapper that adds overhead unnecessary for depthkit's use case:
- Handles scrolling into view (depthkit's viewport is exactly the output size — no scrolling)
- Handles CSS animations and network idle (depthkit's virtualized clock means the page is always in a settled state after `renderFrame()`)
- Handles clip regions (depthkit captures the full viewport)

By using CDP directly, we eliminate this overhead and gain access to the `optimizeForSpeed` parameter (available in Chrome 91+), which skips post-processing on the captured bitmap. For a 1,800-frame render, even a 10ms-per-frame saving yields 18 seconds total.

The CDP call:
```
CDPSession.send('Page.captureScreenshot', {
  format: 'png',
  optimizeForSpeed: true,
  fromSurface: true
})
```

Returns `{ data: string }` where `data` is base64-encoded PNG. Decoded via `Buffer.from(data, 'base64')`.

**Alternative considered:** Keep using `bridge.captureFrame()` (OBJ-009). Rejected because OBJ-009's `page.screenshot()` approach is correct but not optimized for high-throughput frame capture. OBJ-009 remains a valid fallback if CDP access is unavailable.

### D2: Three Strategies with Clear Trade-offs

**Decision:** Three capture strategies, each with distinct capabilities:

| Strategy | Captures HUD | Format | Transfer Size (1080p) | Encode/Decode | Best For |
|---|---|---|---|---|---|
| `viewport-png` | ✅ Yes | PNG | ~200KB-1MB | PNG decode in FFmpeg | Production (default) |
| `canvas-png` | ❌ No | PNG | ~200KB-1MB | PNG decode in FFmpeg | Canvas-only scenes |
| `canvas-rgba` | ❌ No | RGBA | ~11MB (base64) | None (rawvideo) | Maximum throughput |

**Rationale:** Different downstream consumers need different capabilities:
- OBJ-043 (HUD layers) requires viewport-level capture that includes HTML overlays → `viewport-png`
- OBJ-049 (software rendering) needs to validate WebGL output directly → any strategy works
- Performance-critical renders without HUD layers may prefer `canvas-rgba` to eliminate PNG encode/decode overhead

The orchestrator (OBJ-035) selects the strategy based on whether the composition uses HUD layers and performance requirements. The default (`viewport-png`) is always correct; the alternatives are optimizations.

### D3: Vertical Flip for readPixels RGBA

**Decision:** The `canvas-rgba` strategy flips the buffer from bottom-to-top (WebGL's `readPixels()` native order) to top-to-bottom (standard image row order) before returning.

**Rationale:** FFmpeg's `rawvideo` demuxer expects top-to-bottom row order. Flipping on the Node side (after base64 decode) is straightforward and ensures the CaptureResult buffer is always in standard image orientation regardless of strategy. The flip is a simple row-swap loop: O(width × height × 4) with no allocations beyond the output buffer.

**Alternative considered:** Pass `-vf vflip` to FFmpeg (OBJ-013). Rejected because it pushes a capture-layer concern into the encoding layer, violating separation of concerns. The encoder should receive correctly-oriented frames.

### D4: FrameCapture Does Not Own the Bridge

**Decision:** `FrameCapture` accepts a `PuppeteerBridge` reference in its constructor but does not call `bridge.launch()` or `bridge.close()`. The orchestrator (OBJ-035) owns the bridge lifecycle.

**Rationale:** Same rationale as OBJ-011 D1. The bridge is shared between PageProtocol (rendering) and FrameCapture (pixel extraction). The orchestrator composes them.

### D5: CDP Session Acquisition

**Decision:** FrameCapture obtains the CDP session via `bridge.page.createCDPSession()` (for the `viewport-png` strategy). The session is created lazily on the first `capture()` call and reused for subsequent captures. The session is NOT disposed by FrameCapture — it's valid for the lifetime of the page.

**Rationale:** Creating a CDPSession per capture would add overhead. A single session is sufficient for the viewport screenshot command. If the page is closed (bridge.close()), the session becomes invalid, but FrameCapture checks `bridge.isLaunched` before each capture.

**Alternative considered:** Use `bridge.page.target().createCDPSession()`. Both approaches work; `bridge.page.createCDPSession()` is the documented Puppeteer API.

### D6: Statistics for Performance Monitoring

**Decision:** FrameCapture tracks per-frame capture timing and provides aggregate statistics via `getStats()`. Statistics include count, total/average/min/max capture times, and the configured strategy.

**Rationale:** TC-02 (render performance) requires measuring the per-frame capture overhead. OBJ-035 can log capture stats after the render loop to identify bottlenecks. No external dependency needed — just `performance.now()` or `Date.now()` timing around each capture.

### D7: Error Classification via FrameCaptureErrorCode

**Decision:** Capture failures are wrapped in `FrameCaptureError` with structured error codes. The error codes distinguish between bridge state issues (not launched), page state issues (canvas not found, WebGL context lost), and capture mechanism failures.

**Rationale:** The orchestrator (OBJ-035) needs to distinguish between recoverable errors (retry the frame) and fatal errors (abort the render). A context-lost error is fatal; a transient CDP failure might be retryable.

### D8: canvasSelector Defaults to OBJ-010's Canvas ID

**Decision:** The `canvasSelector` config defaults to `'#depthkit-canvas'`, matching OBJ-010's page shell `<canvas id="depthkit-canvas">`.

**Rationale:** Tight coupling to OBJ-010's known DOM structure. If OBJ-010's canvas ID changes, this default must be updated. Configurable for edge cases (e.g., testing with a different page structure).

### D9: Base64 Transfer for canvas-rgba

**Decision:** The `canvas-rgba` strategy transfers raw pixel data from the page to Node.js by base64-encoding the `Uint8Array` inside the page's `evaluate()` call, returning the base64 string, and decoding it on the Node side via `Buffer.from(base64String, 'base64')`.

**Rationale:** Puppeteer's `page.evaluate()` serializes return values via JSON. Raw `Uint8Array` data would be serialized as a JSON array of numbers (`[255, 128, 0, ...]`), which is extremely inefficient for 8MB of pixel data (the JSON encoding would be ~25MB+ due to number formatting). Base64 encoding produces ~11MB of text — still large but 2-3x smaller than JSON array encoding and much faster to parse.

For 1920×1080 RGBA:
- Raw buffer: 8,294,400 bytes
- Base64 string: ~11,059,200 characters
- JSON number array: ~25,000,000+ characters

The base64 encode/decode adds ~10-20ms per frame on a 4-core VPS. This is acceptable but not free — it's why `canvas-rgba` is an opt-in alternative rather than the default.

**Alternative considered:** Use CDP `Runtime.evaluate` with `returnByValue: false` and `IO.read` to stream the buffer. This avoids base64 overhead but requires complex CDP stream management. Deferred to a future optimization pass.

### D10: Buffer Validation

**Decision:** After each capture, FrameCapture validates the result buffer:
- For PNG: Checks that the buffer starts with the PNG magic bytes (`\x89PNG\r\n\x1a\n`) and has length > 8.
- For RGBA: Checks that the buffer length equals `width * height * 4` exactly.

If validation fails, throws `FrameCaptureError` with code `INVALID_BUFFER`.

**Rationale:** Catches silent capture failures (e.g., CDP returns empty data, readPixels returns a zero-length buffer due to context loss) before the corrupt data reaches FFmpeg, where it would cause a cryptic encoding error.

### D11: Scope Relationship with OBJ-009

**Decision:** OBJ-012 does NOT modify OBJ-009's `PuppeteerBridge` class. It accesses the bridge's `page` property (already public per OBJ-009's interface) to obtain CDP sessions and execute canvas-level captures. OBJ-009's `captureFrame()` method remains available but is not used by OBJ-012 or OBJ-035 in the production render loop.

**Rationale:** OBJ-009 is verified. Modifying it would require re-verification. OBJ-012 provides a higher-level, optimized capture service that supersedes `bridge.captureFrame()` for production use. The bridge's `captureFrame()` remains a valid quick-and-dirty capture for debugging and testing.

## Acceptance Criteria

### Construction and Configuration

- [ ] **AC-01:** `FrameCapture` is importable from `src/engine/frame-capture.ts`. `new FrameCapture(bridge)` creates an instance with strategy `'viewport-png'` and canvasSelector `'#depthkit-canvas'`.
- [ ] **AC-02:** `new FrameCapture(bridge, { strategy: 'canvas-rgba' })` creates an instance with `strategy === 'canvas-rgba'`.
- [ ] **AC-03:** `capture.width` and `capture.height` match the bridge's configured viewport dimensions.

### viewport-png Capture

- [ ] **AC-04:** After rendering a scene with a colored mesh via PageProtocol, `capture.capture()` returns a `CaptureResult` with `format: 'png'`, `data` starting with PNG magic bytes (`\x89PNG\r\n\x1a\n`), and `width`/`height` matching the viewport.
- [ ] **AC-05:** The captured PNG is NOT all-black (proves the rendered scene was captured, not just the clear color with nothing rendered).
- [ ] **AC-06:** Two consecutive captures of the same rendered frame produce identical `data` buffers (determinism, C-05).
- [ ] **AC-07:** The capture includes HTML elements overlaid on the canvas (proving viewport-level capture). Verifiable by adding a visible `<div>` with a solid background color over the canvas, capturing, and confirming the captured PNG contains the overlay color at the expected position.

### canvas-png Capture

- [ ] **AC-08:** With strategy `'canvas-png'`, `capture()` returns a `CaptureResult` with `format: 'png'`, valid PNG data.
- [ ] **AC-09:** With strategy `'canvas-png'`, HTML elements overlaid on the canvas are NOT captured (canvas-only). Verifiable by the same overlay test as AC-07 — the overlay color should NOT appear in the capture.

### canvas-rgba Capture

- [ ] **AC-10:** With strategy `'canvas-rgba'`, `capture()` returns a `CaptureResult` with `format: 'rgba'` and `data.length === width * height * 4`.
- [ ] **AC-11:** The returned RGBA buffer is in top-to-bottom row order (not WebGL's native bottom-to-top). Verifiable by rendering a scene with a known color at the top of the viewport and checking that the first row of the buffer contains that color.
- [ ] **AC-12:** The RGBA buffer, when piped to FFmpeg with `-f rawvideo -pix_fmt rgba -s {w}x{h}`, produces a visually correct image (no vertical flip, no color channel swap).

### Error Handling

- [ ] **AC-13:** `capture()` when `bridge.isLaunched === false` throws `FrameCaptureError` with code `'BRIDGE_NOT_LAUNCHED'`.
- [ ] **AC-14:** `capture()` with strategy `'canvas-png'` or `'canvas-rgba'` when the canvas element matching `canvasSelector` does not exist throws `FrameCaptureError` with code `'CANVAS_NOT_FOUND'`.
- [ ] **AC-15:** `FrameCaptureError` instances have `code`, `message`, and optional `details` properties. `error instanceof FrameCaptureError` is `true`. `error instanceof Error` is `true`.

### Statistics

- [ ] **AC-16:** After 0 captures, `getStats()` returns `captureCount: 0`, `averageCaptureMs: 0`, `minCaptureMs: Infinity`, `maxCaptureMs: 0`.
- [ ] **AC-17:** After N captures, `getStats()` returns `captureCount: N`, `totalCaptureMs` > 0, `averageCaptureMs` approximately equal to `totalCaptureMs / N`.
- [ ] **AC-18:** `resetStats()` resets all statistics to their initial values. Subsequent `getStats()` returns zeroed stats.
- [ ] **AC-19:** Each `CaptureResult.captureMs` is > 0 (non-zero timing).

### Buffer Validation

- [ ] **AC-20:** If CDP returns an empty screenshot (simulated by intercepting the CDP response), `capture()` throws `FrameCaptureError` with code `'INVALID_BUFFER'`.
- [ ] **AC-21:** For `canvas-rgba`, if the returned buffer length does not equal `width * height * 4` (e.g., WebGL context was lost mid-capture), throws `FrameCaptureError` with code `'INVALID_BUFFER'`.

### Format Alignment with OBJ-013

- [ ] **AC-22:** The `data` buffer from `viewport-png` is directly consumable by `FFmpegEncoder.writeFrame()` when the encoder is configured with `frameFormat: 'png'`.
- [ ] **AC-23:** The `data` buffer from `canvas-rgba` is directly consumable by `FFmpegEncoder.writeFrame()` when the encoder is configured with `frameFormat: 'rgba'`.

## Edge Cases and Error Handling

### Capture

| Scenario | Expected Behavior |
|---|---|
| `capture()` before bridge is launched | `FrameCaptureError` with code `BRIDGE_NOT_LAUNCHED`. |
| `capture()` after bridge is closed | `FrameCaptureError` with code `BRIDGE_NOT_LAUNCHED` (bridge.isLaunched is false after close). |
| Canvas element not found (canvas strategies) | `FrameCaptureError` with code `CANVAS_NOT_FOUND`, message includes the selector. |
| WebGL context lost before capture | `FrameCaptureError` with code `WEBGL_CONTEXT_LOST`. Detected by checking `gl.isContextLost()` inside the evaluate call (canvas strategies) or by an empty/corrupt CDP response (viewport strategy). |
| CDP session disconnected (e.g., page navigated away) | CDP call rejects. Caught and wrapped as `FrameCaptureError` with code `CAPTURE_FAILED`, original error in `details`. |
| Very large viewport (e.g., 3840×2160) | Works but slow. For canvas-rgba, the base64 transfer is ~33MB. No artificial limit — the caller (OBJ-035) controls viewport dimensions. |
| Very small viewport (e.g., 1×1) | Works. Canvas-rgba produces a 4-byte buffer. |
| Page has no WebGL canvas (e.g., init not called) | viewport-png captures the blank page. canvas-png/canvas-rgba throw `CANVAS_NOT_FOUND` or `WEBGL_CONTEXT_LOST` depending on whether the canvas element exists but has no WebGL context. |
| Multiple FrameCapture instances on the same bridge | Allowed. Each creates its own CDPSession. No interference. Statistics are per-instance. |
| capture() called concurrently (parallel calls) | Not safe. CDP screenshot and evaluate are serialized by Puppeteer/CDP anyway, but concurrent calls may interleave statistics tracking. The orchestrator's deterministic frame loop (C-03) guarantees sequential calls. |

### CDPSession Management

| Scenario | Expected Behavior |
|---|---|
| First capture() call | CDPSession created lazily. Subsequent captures reuse it. |
| Bridge closed and re-launched | FrameCapture detects stale session (bridge.isLaunched toggled). Creates a new CDPSession on the next capture(). The old session is implicitly invalidated by browser closure. |
| CDPSession creation fails | Wrapped as `FrameCaptureError` with code `CAPTURE_FAILED`. |

### Buffer Validation

| Scenario | Expected Behavior |
|---|---|
| PNG buffer < 8 bytes | `FrameCaptureError` with code `INVALID_BUFFER`, message: "Captured PNG buffer too small ({length} bytes)". |
| PNG buffer doesn't start with magic bytes | `FrameCaptureError` with code `INVALID_BUFFER`, message: "Captured buffer is not valid PNG data". |
| RGBA buffer length ≠ width × height × 4 | `FrameCaptureError` with code `INVALID_BUFFER`, message: "RGBA buffer size mismatch: expected {expected}, got {actual}". |
| RGBA buffer is all zeros (blank frame) | NOT an error. Blank frames are valid (e.g., opacity=0 render pass). The validator checks size, not content. |

## Test Strategy

### Unit Tests: `test/unit/frame-capture.test.ts`

1. **Construction defaults:** `new FrameCapture(bridge)` produces `strategy === 'viewport-png'`, `canvasSelector === '#depthkit-canvas'`, width/height from bridge config.
2. **Construction with config:** Custom strategy and canvasSelector are stored correctly.
3. **FrameCaptureError:** Construct with code/message/details, verify `instanceof Error`, verify properties.
4. **Stats initial state:** `getStats()` before any captures returns zeroed stats.
5. **Stats reset:** `resetStats()` returns stats to initial state.
6. **PNG magic byte validation:** Test the internal validation logic with valid PNG buffers, truncated buffers, and non-PNG data.
7. **RGBA size validation:** Test with correct-size buffers and mismatched-size buffers.
8. **RGBA vertical flip logic:** Test the flip function with a small known buffer (e.g., 2×2 RGBA) and verify row order is reversed.

### Integration Tests: `test/integration/frame-capture.test.ts`

These tests launch real headless Chromium. Use small viewports (e.g., 320×240) and simple test scenes for speed.

**Setup per test:** Create a PuppeteerBridge, launch it, create a PageProtocol, initialize the page, set up a scene with a colored mesh, render a frame.

9. **viewport-png basic capture:** Render a red mesh, capture, verify PNG magic bytes, verify result is not all-black.
10. **viewport-png determinism (TC-06):** Capture the same rendered frame twice, verify identical buffers.
11. **viewport-png includes HUD:** Add a visible `<div>` over the canvas via evaluate, capture, verify the overlay is in the captured PNG (check pixel color at the overlay position by decoding the PNG with a lightweight decoder or comparing against a capture without the overlay).
12. **canvas-png basic capture:** Render a scene, capture with canvas-png, verify PNG magic bytes.
13. **canvas-png excludes HUD:** Add a visible `<div>` over the canvas, capture with canvas-png, verify the overlay is NOT in the captured PNG.
14. **canvas-rgba basic capture:** Render a scene, capture with canvas-rgba, verify buffer length === width × height × 4.
15. **canvas-rgba vertical flip:** Render a scene with a known color at the top, verify first row of RGBA buffer contains that color (not the bottom color).
16. **canvas-rgba format compatibility:** Capture a frame, pipe the buffer to FFmpeg with `frameFormat: 'rgba'`, verify FFmpeg produces a valid MP4 (not corrupt, not flipped).
17. **Error: bridge not launched:** Create FrameCapture with an unlaunched bridge, call capture(), verify FrameCaptureError with BRIDGE_NOT_LAUNCHED.
18. **Error: canvas not found:** Use a non-matching canvasSelector with canvas-png, verify FrameCaptureError with CANVAS_NOT_FOUND.
19. **Statistics tracking:** Capture 5 frames, verify getStats() returns captureCount: 5, totalCaptureMs > 0, averageCaptureMs ≈ totalCaptureMs / 5.
20. **Statistics reset:** Capture, resetStats(), capture, verify captureCount: 1.
21. **CDPSession reuse:** Capture multiple frames, verify no performance degradation from session creation (timing should be consistent after the first capture).
22. **Bridge re-launch recovery:** Launch bridge, create FrameCapture, capture works. Close bridge, re-launch bridge, capture works again with fresh CDPSession.

### Performance Baseline (TC-02)

23. **Per-frame capture latency:** Render and capture 30 frames at 320×240 with each strategy. Log average capture time per strategy. This provides a baseline for OBJ-035 to compare against the 500ms/frame budget (TC-02). Do NOT assert a threshold — just log.
24. **1080p capture latency:** Render and capture 10 frames at 1920×1080 with viewport-png. Log average capture time. This is the production-relevant data point.

### Relevant Testable Claims

- **TC-02** (render performance): Tests 23-24 measure capture overhead as a component of total render time.
- **TC-06** (deterministic output): Test 10 verifies capture determinism.
- **TC-11** (Docker/software WebGL): All integration tests run with `gpu: false` (SwiftShader) by default, validating software rendering capture correctness.

## Integration Points

### Depends on

| Dependency | What OBJ-012 uses |
|---|---|
| **OBJ-009** (PuppeteerBridge) | `PuppeteerBridge` instance — accesses `bridge.page` for CDPSession creation and `bridge.evaluate()` for canvas-level capture. Accesses `bridge.isLaunched` for state checks. Uses bridge's configured `width` and `height` for buffer size validation. Does NOT use `bridge.captureFrame()` — OBJ-012 supersedes it for production capture. |
| **OBJ-011** (PageProtocol) | Indirect dependency — OBJ-011 must have rendered a frame (via `protocol.renderFrame()`) before `capture.capture()` is called. OBJ-012 does not import or call OBJ-011 directly; the orchestrator (OBJ-035) sequences the calls. The dependency exists because OBJ-012 requires the page's `window.depthkit` infrastructure to be initialized and scenes to be rendered before capture makes sense. |
| **OBJ-010** (Page shell) | The canvas element ID (`#depthkit-canvas`) defined by OBJ-010 is the default `canvasSelector`. The page's WebGL context (created by `window.depthkit.init()`) is accessed by canvas capture strategies. |

### Consumed by

| Downstream | How it uses OBJ-012 |
|---|---|
| **OBJ-035** (Orchestrator) | The primary consumer. Creates a `FrameCapture` instance alongside `PageProtocol` and `FFmpegEncoder`. In the render loop: `protocol.renderFrame()` → `capture.capture()` → `encoder.writeFrame(result.data)`. Selects strategy based on whether the composition uses HUD layers. Logs `capture.getStats()` after the render loop. |
| **OBJ-043** (HUD layer system) | Requires `viewport-png` strategy to capture HTML/CSS overlay elements. OBJ-043 validates that its overlays appear in captured frames. |
| **OBJ-049** (Software rendering config) | Validates that frame capture produces correct output with software WebGL (SwiftShader). Uses any capture strategy — the concern is software rendering correctness, not capture method. |

### File Placement

```
depthkit/
  src/
    engine/
      frame-capture.ts        # NEW — FrameCapture class, CaptureStrategy,
                               #       FrameCaptureConfig, CaptureResult,
                               #       CaptureStats, FrameCaptureError
  test/
    unit/
      frame-capture.test.ts   # NEW — unit tests
    integration/
      frame-capture.test.ts   # NEW — integration tests with Puppeteer
```

## Open Questions

### OQ-A: Is the base64 transfer overhead for canvas-rgba acceptable?

For 1920×1080 RGBA, the base64 string is ~11MB transferred through Puppeteer's evaluate() serialization. Benchmarking (test 23-24) will reveal whether this overhead negates the benefit of avoiding PNG encode/decode. If the overhead is too high, the `canvas-rgba` strategy may need to use CDP's `IO.read` streaming API or be marked as unsuitable for 1080p production use.

### OQ-B: Should FrameCapture support JPEG format for preview mode?

A `viewport-jpeg` strategy with configurable quality (e.g., 80%) would produce smaller buffers and faster captures for preview/debugging workflows (seed OQ-05). Deferred — the current three strategies cover production needs. JPEG can be added later without interface changes.

### OQ-C: Should capture() accept per-call options overriding the constructor config?

E.g., `capture({ strategy: 'canvas-png' })` to switch strategies mid-render. Currently the strategy is fixed at construction time. If OBJ-035 needs to switch strategies (e.g., viewport-png for HUD frames, canvas-rgba for non-HUD frames), it would create two FrameCapture instances. Per-call override is simpler but adds complexity to the interface. Deferred until OBJ-035's spec reveals the need.

### OQ-D: CDPSession lifecycle — should FrameCapture dispose its session?

Currently the spec says the CDPSession is created lazily and not explicitly disposed. Puppeteer CDPSessions are cleaned up when the page is closed. If FrameCapture should have an explicit `dispose()` method for clean shutdown, that can be added. For V1, implicit cleanup via page closure is sufficient.

---

I believe this spec provides a clear, implementable contract for OBJ-012 that:

1. **Fills the architectural gap** between OBJ-011's render commands and OBJ-013's encoder — the "capture" step in the render pipeline
2. **Adds real value** over OBJ-009's basic `captureFrame()` via CDP optimization, multiple capture strategies, format selection, and statistics
3. **Serves all three downstream consumers** — OBJ-035 (orchestrator), OBJ-043 (HUD layers need viewport capture), OBJ-049 (software rendering validation)
4. **Acknowledges the scope overlap** with OBJ-009 via D11, without requiring OBJ-009 modification

I'd like the Challenger to review this proposal, particularly:
- Whether the three-strategy approach is the right abstraction level (or if V1 should only implement `viewport-png`)
- Whether the CDPSession management is specified precisely enough
- Whether the base64 transfer approach for `canvas-rgba` is the right call vs. deferring raw capture entirely

---

## Round 2 — spec_challenger


[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": "60",
  "limit": "260"
}
[Tool Result]     60→   * @returns timestamp in seconds (frame / fps).
    61→   * @throws RangeError if frame < 0 or frame >= totalFrames or not an integer.
    62→   */
    63→  frameToTimestamp(frame: number): number;
    64→
    65→  /**
    66→   * Convert an absolute timestamp (seconds) to the nearest frame number.
    67→   * Uses Math.round(), then clamps to [0, totalFrames - 1].
    68→   * @param timestamp — Time in seconds.
    69→   * @returns frame number (integer, clamped).
    70→   * @throws RangeError if timestamp is negative.
    71→   */
    72→  timestampToFrame(timestamp: number): number;
    73→
    74→  /**
    75→   * Generator that yields FrameTick objects for every frame from 0
    76→   * to totalFrames - 1, in order. This is the canonical iteration
    77→   * primitive for the render loop.
    78→   *
    79→   * Usage:
    80→   *   for (const tick of clock.frames()) {
    81→   *     // render tick.frame at tick.timestamp
    82→   *   }
    83→   */
    84→  frames():... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "offset": "10",
  "limit": "70"
}
[Tool Result]     10→
    11→```typescript
    12→// src/engine/ffmpeg-encoder.ts
    13→
    14→/**
    15→ * Supported input pixel formats for frame data piped to FFmpeg.
    16→ * - 'png': Each frame is a complete PNG-encoded buffer. FFmpeg uses `image2pipe` demuxer.
    17→ * - 'rgba': Each frame is raw RGBA pixel data (width * height * 4 bytes). FFmpeg uses `rawvideo` input.
    18→ */
    19→export type FrameFormat = 'png' | 'rgba';
    20→
    21→/**
    22→ * H.264 encoding preset. Controls the speed/quality/filesize tradeoff.
    23→ * Maps directly to FFmpeg's `-preset` flag.
    24→ */
    25→export type H264Preset =
    26→  | 'ultrafast' | 'superfast' | 'veryfast' | 'faster'
    27→  | 'fast' | 'medium' | 'slow' | 'slower' | 'veryslow';
    28→
    29→/**
    30→ * Configuration for the FFmpeg encoder.
    31→ */
    32→export interface FFmpegEncoderConfig {
    33→  /** Output file path for the MP4. Must be writable. Parent directory must exist. */
    34→  outputPath: string;
    35→
... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": "340",
  "limit": "180"
}
[Tool Result]    340→
   341→**Rationale:** Combined with OBJ-010's `renderer.setPixelRatio(1)`, this ensures 1:1 pixel mapping. A 1920x1080 viewport produces a 1920x1080 screenshot. HiDPI scaling would silently double the resolution, breaking FFmpeg encoding and violating C-05 (deterministic output).
   342→
   343→### D10: Page Loading via `file://` Protocol
   344→
   345→**Decision:** The bridge loads `index.html` via `file://` protocol using `page.goto('file://...')`.
   346→
   347→**Rationale:** The built page is self-contained — `index.html` loads `scene-renderer.js` (esbuild bundle with Three.js inlined). No network requests needed for page load. `file://` avoids the complexity of spinning up a local HTTP server.
   348→
   349→**Texture loading constraint:** The `--allow-file-access-from-files` Chromium flag (D8) enables Three.js `TextureLoader` to load images from the filesystem via `file://` URLs. This means OBJ-015 (texture loading) can pass absolute `file://` paths to `TextureLoader` v... [truncated]
I've read the full OBJ-009 spec, OBJ-013 interface, OBJ-011 spec, and OBJ-012 meta.json. Let me now give a thorough review.

---

## What's Sound

Before the critique, I want to explicitly approve the strong parts:

1. **Architectural placement is correct.** The spec correctly identifies the gap between OBJ-011's `renderFrame()` and OBJ-013's `writeFrame()`. The "capture" step needed a home and this is it.
2. **D4 (no bridge ownership)** is consistent with OBJ-011 D1 and the orchestrator-owns-everything pattern.
3. **D10 (buffer validation)** is a smart defensive measure — catching corrupt data before it reaches FFmpeg is the right place.
4. **D11 (doesn't modify OBJ-009)** is the correct scope discipline. OBJ-009 is verified.
5. **Statistics tracking (D6)** is well-motivated by TC-02 and the acceptance criteria for it are specific.
6. **Error classification** is clean and matches the pattern established by OBJ-011's `PageProtocolError`.

---

## Challenges

### 1. CRITICAL: `preserveDrawingBuffer` requirement for canvas strategies is undocumented

For `canvas.toDataURL()` and `gl.readPixels()` to return valid data after `renderer.render()`, Three.js's `WebGLRenderer` must be created with `{ preserveDrawingBuffer: true }`. Without this, the drawing buffer is cleared after compositing, and both canvas strategies silently return blank (transparent/black) frames.

The `viewport-png` strategy via CDP `Page.captureScreenshot` is unaffected — CDP captures from the compositor, not the canvas buffer. But `canvas-png` and `canvas-rgba` will **silently fail** without this flag.

This is a cross-objective dependency on OBJ-010 that must be explicitly documented.

**Proposed fix:** Add to the Integration Points / Depends On table:

> **OBJ-010 (Page shell):** ... Additionally, the `canvas-png` and `canvas-rgba` strategies require that OBJ-010's `WebGLRenderer` is created with `preserveDrawingBuffer: true`. Without this Three.js option, `canvas.toDataURL()` and `gl.readPixels()` return blank data after `renderer.render()`. The `viewport-png` strategy is unaffected (CDP captures from the compositor). If OBJ-010 does not set this flag, the implementer must add it — document this as a precondition in the `canvas-png` and `canvas-rgba` strategy descriptions.

Also add an edge case row:

| WebGLRenderer created without `preserveDrawingBuffer: true` | `canvas-png` and `canvas-rgba` return blank (all-black or all-transparent) frames. `viewport-png` is unaffected. The implementation should detect this (check if all returned bytes are zero after a known non-blank render) and throw `FrameCaptureError` with code `CAPTURE_FAILED` and a message mentioning `preserveDrawingBuffer`. |

### 2. MAJOR: CDPSession staleness detection mechanism is unspecified

D5 says the session is "created lazily and reused." The edge case table says "Bridge closed and re-launched: FrameCapture detects stale session." But **how**?

After `bridge.close()`, the CDPSession is implicitly invalidated. If the orchestrator calls `bridge.close()` then `bridge.launch()` (re-entrant lifecycle per OBJ-009 AC-22), the cached CDPSession is dead. The next `capture()` call using the stale session will throw a Puppeteer error.

The spec says "Creates a new CDPSession on the next capture()" but doesn't specify the detection logic.

**Proposed fix:** Specify the mechanism explicitly in D5:

> The FrameCapture tracks the `bridge.page` reference that was used to create the CDPSession. On each `capture()` call, if `bridge.page !== this._sessionPage` (i.e., the page object has changed due to a bridge close/re-launch cycle), the cached CDPSession is discarded and a new one is created from the current `bridge.page`. This comparison works because `bridge.close()` sets `bridge.page = null` and `bridge.launch()` creates a new `Page` instance.

### 3. MAJOR: WebGL context acquisition for `canvas-rgba` readPixels is unspecified

The spec says `canvas-rgba` "calls gl.readPixels() on the WebGL context" but doesn't specify:

- How to obtain the WebGL context on the page side (Three.js may use WebGL1 or WebGL2; `canvas.getContext('webgl')` would return `null` if Three.js obtained a WebGL2 context)
- The exact `readPixels()` call parameters (x, y, width, height, format, type, buffer)
- Whether to use `renderer.getContext()` (Three.js API) or query the canvas directly

An implementer would have to guess.

**Proposed fix:** Add to D9 or create a new design decision specifying the page-side readPixels implementation:

```javascript
// Inside page.evaluate():
const gl = window.depthkit.renderer.getContext();
const width = gl.drawingBufferWidth;
const height = gl.drawingBufferHeight;
const pixels = new Uint8Array(width * height * 4);
gl.readPixels(0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
// base64 encode pixels and return
```

Note that `renderer.getContext()` is the Three.js-native way to get the underlying WebGL context, regardless of whether it's WebGL1 or WebGL2.

### 4. MAJOR: `canvas-rgba` at 1080p transfers ~11MB base64 per frame — AP-05 conflict

The spec acknowledges this in OQ-A but still specifies it as a fully specified V1 strategy. For a 1,800-frame render, that's ~20GB of string data serialized through V8's JSON layer. This is a premature optimization (AP-05 says "first version should prioritize correctness and authorability over render speed").

The `viewport-png` strategy is always correct and sufficient. `canvas-png` offers marginal benefit (no HUD capture — useful for testing). `canvas-rgba` exists only for throughput, which AP-05 says to defer.

**Proposed fix:** Either:
- **(A)** Demote `canvas-rgba` to an Open Question / future optimization, removing it from the type union and all acceptance criteria. Specify only `viewport-png` (production default) and `canvas-png` (testing/canvas-only). Add OQ: "canvas-rgba via readPixels + base64 transfer was considered for V1 but deferred per AP-05. Benchmark viewport-png first; if capture is the bottleneck, revisit with CDP IO.read streaming or SharedArrayBuffer transfer."
- **(B)** Keep it but mark it explicitly as "experimental" in the strategy docs and add a warning in the implementation that base64 transfer of ~11MB per frame may degrade performance at 1080p.

I prefer **(A)**. Two strategies is simpler, and the FFmpeg encoder already accepts PNG natively.

### 5. MINOR: `fromSurface` CDP parameter is deprecated

The spec's D1 says the CDP call includes `fromSurface: true`. This parameter was deprecated (it's now always true by default in Chrome 92+). Including it won't break anything, but it's cargo-cult.

**Proposed fix:** Remove `fromSurface: true` from the CDP call specification. Note: "The `fromSurface` parameter was deprecated in Chrome 92 (always true by default) and is omitted."

### 6. MINOR: Timing function not specified

D6 says "just `performance.now()` or `Date.now()` timing." These have different precision (sub-ms vs 1ms). For consistent stats, pick one.

**Proposed fix:** Specify `performance.now()` (available in Node.js) for capture timing. Sub-millisecond precision is valuable for distinguishing capture overhead from render overhead in OBJ-035's performance logs.

### 7. MINOR: `#depthkit-canvas` selector coupling not verified

D8 says the default canvasSelector is `'#depthkit-canvas'` and claims this matches OBJ-010's page shell. This is a cross-objective coupling that needs to be stated as a hard contract.

**Proposed fix:** In the integration points table for OBJ-010, explicitly state: "OBJ-010 defines the canvas element with `id='depthkit-canvas'`. OBJ-012's default `canvasSelector` depends on this. If OBJ-010 changes the ID, OBJ-012's default must be updated." Also: is this actually what OBJ-010 uses? The spec should reference the specific OBJ-010 decision/AC that establishes this ID.

### 8. MINOR: No mention of `preserveDrawingBuffer` impact on `viewport-png` performance

With `preserveDrawingBuffer: true` (needed for canvas strategies per issue #1), there's a small performance cost to ALL rendering — Three.js has to preserve the buffer after each render. If only `viewport-png` is used (no canvas strategies), `preserveDrawingBuffer: false` would be faster. The spec should note this trade-off so OBJ-035 can make an informed choice.

**Proposed fix:** Add a note to D2's trade-off table: "Note: `canvas-png` and `canvas-rgba` require `preserveDrawingBuffer: true` on the WebGLRenderer (OBJ-010), which has a small performance cost applied to all rendering. `viewport-png` does not require this flag. If only `viewport-png` is used, the renderer can be initialized with `preserveDrawingBuffer: false` for slightly better performance."

---

## Summary

| # | Severity | Issue | Status |
|---|---|---|---|
| 1 | Critical | `preserveDrawingBuffer` requirement for canvas strategies | Needs fix |
| 2 | Major | CDPSession staleness detection mechanism | Needs fix |
| 3 | Major | WebGL context acquisition for readPixels | Needs fix |
| 4 | Major | `canvas-rgba` is premature optimization (AP-05) | Needs fix |
| 5 | Minor | `fromSurface` CDP parameter deprecated | Needs fix |
| 6 | Minor | Timing function unspecified | Needs fix |
| 7 | Minor | Canvas ID cross-objective coupling | Needs fix |
| 8 | Minor | preserveDrawingBuffer performance note | Needs fix |

Please address the critical and major issues (#1-4). The minor issues (#5-8) can be addressed or documented as known coupling points.

---

## Round 3 — spec_author

Let me check what OBJ-010 specifies for the canvas element ID before revising.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "offset": "60",
  "limit": "150"
}
[Tool Result]     60→  getRendererInfo(): RendererInfo;
    61→
    62→  /**
    63→   * Renders the current scene with the current camera to the canvas.
    64→   * This is the primitive render call. OBJ-011's message protocol will
    65→   * call this after setting camera state per frame.
    66→   *
    67→   * If cameraState is provided, updates the camera before rendering.
    68→   * Fields are applied in this exact order:
    69→   *   1. position — camera.position.set(x, y, z)
    70→   *   2. lookAt — camera.lookAt(x, y, z)  (must follow position, since
    71→   *      lookAt computes rotation from the camera's current position)
    72→   *   3. fov — camera.fov = value; camera.updateProjectionMatrix()
    73→   *
    74→   * Only provided fields are updated; omitted fields leave the camera unchanged.
    75→   * After applying any updates, calls renderer.render(scene, camera).
    76→   *
    77→   * @param cameraState - Optional partial camera state to apply before rendering.
    78→   ... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "depthkit-canvas|canvas.*id",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md"
}
[Tool Result] Found 1 file
nodes/OBJ-010/output.md

[Tool: Grep]
  Input: {
  "pattern": "canvas|getElementById|querySelector",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md"
}
[Tool Result] Found 1 file
nodes/OBJ-010/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "offset": "200",
  "limit": "200"
}
[Tool Result]    200→After OBJ-010, this file contains a **stub**. OBJ-011 defines the full message handling protocol.
   201→
   202→```javascript
   203→// src/page/message-handler.js
   204→// Stub: Message protocol between Puppeteer orchestrator and browser page.
   205→//
   206→// OBJ-011 defines every message type crossing the Node.js/browser boundary:
   207→// frame step commands, scene setup/teardown, texture loading signals, etc.
   208→//
   209→// Messages arrive via page.evaluate() calls from the Node.js orchestrator.
   210→// The handler calls into window.depthkit methods (init, renderFrame, dispose).
   211→//
   212→// TODO: OBJ-011 — Full message protocol
   213→export {};
   214→```
   215→
   216→### Module: `src/page/index.html`
   217→
   218→The final HTML shell (evolving the OBJ-001 stub):
   219→
   220→```html
   221→<!DOCTYPE html>
   222→<html lang="en">
   223→<head>
   224→  <meta charset="UTF-8">
   225→  <meta name="viewport" content="width=device-width, initial-scal... [truncated]
Good — I've confirmed the key facts:

1. **OBJ-010 uses `#depthkit-canvas`** (line 232, 236)
2. **OBJ-010 already has `preserveDrawingBuffer: true` as the default** (D3, AC-08, and `PageInitConfig` line 152-156)
3. **OBJ-010's renderer is created with `preserveDrawingBuffer: true`** and explicitly supports `canvas.toDataURL()` capture

Now let me prepare the revised specification addressing all 8 challenger issues.

---

Here is the revised specification for OBJ-012, addressing every issue raised:

---

# Specification: OBJ-012 — Frame Capture Pipeline

## Summary

OBJ-012 delivers the `FrameCapture` class (`src/engine/frame-capture.ts`) — the configurable frame extraction service that sits between OBJ-011's rendered page state and OBJ-013's FFmpeg encoder input. It provides two capture strategies: `viewport-png` (CDP `Page.captureScreenshot` for full viewport capture including HUD overlays) and `canvas-png` (canvas-level `toDataURL()` for WebGL-only capture). The module tracks capture timing statistics for performance monitoring and establishes the capture format contract that OBJ-035 (orchestrator) uses to bridge rendering and encoding. This implements the "capture" step in seed Section 4.4 step 3f and completes the browser-side capture half of C-02.

## Interface Contract

### Module: `src/engine/frame-capture.ts`

```typescript
import type { PuppeteerBridge } from './puppeteer-bridge.js';

/**
 * Capture strategy determines both the capture mechanism and the
 * output buffer format.
 *
 * - 'viewport-png': CDP Page.captureScreenshot with optimizeForSpeed.
 *   Captures the full composited viewport — the WebGL canvas plus
 *   any HTML/CSS elements layered on top (HUD layers per OBJ-043).
 *   Output is a PNG-encoded Buffer. This is the production default.
 *   Does NOT require preserveDrawingBuffer on the WebGLRenderer.
 *
 * - 'canvas-png': Extracts the canvas content via page.evaluate()
 *   calling canvas.toDataURL('image/png'). Captures only the WebGL
 *   canvas — HTML overlays are NOT included. Output is a PNG-encoded
 *   Buffer (base64-decoded from toDataURL result). Useful for
 *   canvas-only capture when HUD layers are absent and for testing.
 *   REQUIRES preserveDrawingBuffer: true on the WebGLRenderer
 *   (OBJ-010 D3 — this is OBJ-010's default).
 */
export type CaptureStrategy = 'viewport-png' | 'canvas-png';

/**
 * Configuration for the FrameCapture service.
 */
export interface FrameCaptureConfig {
  /**
   * Capture strategy. Default: 'viewport-png'.
   * See CaptureStrategy documentation for trade-offs.
   */
  strategy?: CaptureStrategy;

  /**
   * The CSS selector of the canvas element on the page.
   * Required for 'canvas-png' strategy.
   * Ignored for 'viewport-png' (captures full viewport).
   * Default: '#depthkit-canvas' (matches OBJ-010's page shell
   * — see OBJ-010 index.html: <canvas id="depthkit-canvas">).
   */
  canvasSelector?: string;
}

/**
 * Result of a single frame capture.
 */
export interface CaptureResult {
  /** The captured pixel data as a PNG-encoded Buffer. */
  data: Buffer;

  /**
   * The format of the data buffer. Always 'png' in V1.
   * Present for forward compatibility if raw formats are
   * added in the future.
   */
  format: 'png';

  /** Frame width in pixels. */
  width: number;

  /** Frame height in pixels. */
  height: number;

  /** Time taken for this capture in milliseconds (via performance.now()). */
  captureMs: number;
}

/**
 * Aggregate capture statistics for performance monitoring.
 */
export interface CaptureStats {
  /** Total number of frames captured. */
  captureCount: number;

  /** Total capture time across all frames in milliseconds. */
  totalCaptureMs: number;

  /** Average capture time per frame in milliseconds. 0 if no captures. */
  averageCaptureMs: number;

  /** Minimum capture time across all frames. Infinity if no captures. */
  minCaptureMs: number;

  /** Maximum capture time across all frames. 0 if no captures. */
  maxCaptureMs: number;

  /** The configured strategy. */
  strategy: CaptureStrategy;
}

/**
 * Error class for frame capture failures.
 */
export class FrameCaptureError extends Error {
  /** Error category for programmatic handling. */
  readonly code: FrameCaptureErrorCode;
  readonly details?: Record<string, unknown>;

  constructor(code: FrameCaptureErrorCode, message: string, details?: Record<string, unknown>);
}

export type FrameCaptureErrorCode =
  | 'BRIDGE_NOT_LAUNCHED'     // PuppeteerBridge is not launched
  | 'CANVAS_NOT_FOUND'        // Canvas element not found (canvas-png strategy)
  | 'WEBGL_CONTEXT_LOST'      // WebGL context is lost
  | 'CAPTURE_FAILED'          // CDP or canvas capture failed
  | 'INVALID_BUFFER'          // Captured buffer is empty or corrupt
  ;

/**
 * Configurable frame capture service for the depthkit rendering pipeline.
 *
 * Sits between OBJ-011's renderFrame() (which renders a frame to the page)
 * and OBJ-013's writeFrame() (which pipes the buffer to FFmpeg). The
 * orchestrator (OBJ-035) calls capture() after each renderFrame() to
 * extract the rendered pixels.
 *
 * The FrameCapture does NOT own the PuppeteerBridge lifecycle. The caller
 * (OBJ-035 orchestrator) creates the bridge, launches it, then creates
 * FrameCapture with the bridge reference.
 *
 * Usage:
 *   const bridge = new PuppeteerBridge({ width: 1920, height: 1080 });
 *   await bridge.launch();
 *   const capture = new FrameCapture(bridge);
 *   // ... render frames via PageProtocol ...
 *   const result = await capture.capture();
 *   await encoder.writeFrame(result.data);
 *   // ... after all frames ...
 *   console.log(capture.getStats());
 */
export class FrameCapture {
  constructor(bridge: PuppeteerBridge, config?: FrameCaptureConfig);

  /**
   * Capture the current state of the page as a PNG pixel buffer.
   *
   * The caller must ensure a frame has been rendered (via
   * PageProtocol.renderFrame()) before calling capture().
   * This method captures whatever is currently displayed.
   *
   * For 'viewport-png':
   *   Uses CDP Page.captureScreenshot with:
   *   - format: 'png'
   *   - optimizeForSpeed: true
   *   Decodes the base64 response to a Buffer.
   *
   * For 'canvas-png':
   *   Uses bridge.evaluate() to call canvas.toDataURL('image/png')
   *   on the canvas element identified by canvasSelector.
   *   Strips the 'data:image/png;base64,' prefix and decodes to Buffer.
   *   REQUIRES preserveDrawingBuffer: true on the WebGLRenderer.
   *
   * @returns CaptureResult with the PNG pixel buffer and metadata.
   * @throws FrameCaptureError with appropriate code on failure.
   */
  capture(): Promise<CaptureResult>;

  /**
   * Returns aggregate capture statistics.
   * Statistics accumulate over the lifetime of this FrameCapture instance.
   */
  getStats(): CaptureStats;

  /**
   * Resets capture statistics to zero.
   */
  resetStats(): void;

  /**
   * The resolved configuration (with defaults applied).
   */
  readonly strategy: CaptureStrategy;

  /**
   * Width and height from the PuppeteerBridge config.
   * Used for CaptureResult metadata.
   */
  readonly width: number;
  readonly height: number;
}
```

## Design Decisions

### D1: CDP Direct Capture over page.screenshot()

**Decision:** The `viewport-png` strategy uses CDP `Page.captureScreenshot` directly via the Puppeteer CDPSession, bypassing `page.screenshot()`.

**Rationale:** Puppeteer's `page.screenshot()` is a convenience wrapper that adds overhead unnecessary for depthkit's use case:
- Handles scrolling into view (depthkit's viewport is exactly the output size — no scrolling)
- Handles CSS animations and network idle (depthkit's virtualized clock means the page is always in a settled state after `renderFrame()`)
- Handles clip regions (depthkit captures the full viewport)

By using CDP directly, we eliminate this overhead and gain access to the `optimizeForSpeed` parameter (available in Chrome 91+), which skips post-processing on the captured bitmap. For a 1,800-frame render, even a 10ms-per-frame saving yields 18 seconds total.

The CDP call:
```
CDPSession.send('Page.captureScreenshot', {
  format: 'png',
  optimizeForSpeed: true
})
```

Returns `{ data: string }` where `data` is base64-encoded PNG. Decoded via `Buffer.from(data, 'base64')`.

Note: The `fromSurface` parameter was deprecated in Chrome 92 (always true by default) and is omitted.

**Alternative considered:** Keep using `bridge.captureFrame()` (OBJ-009). Rejected because OBJ-009's `page.screenshot()` approach is correct but not optimized for high-throughput frame capture. OBJ-009 remains a valid fallback if CDP access is unavailable.

### D2: Two Strategies — viewport-png (Default) and canvas-png

**Decision:** Two capture strategies, each with distinct capabilities:

| Strategy | Captures HUD | Needs preserveDrawingBuffer | Transfer Mechanism | Best For |
|---|---|---|---|---|
| `viewport-png` | ✅ Yes | ❌ No | CDP screenshot (base64 PNG) | Production (default) |
| `canvas-png` | ❌ No | ✅ Yes (OBJ-010 default) | `canvas.toDataURL()` (base64 PNG) | Canvas-only testing |

**Rationale:**
- `viewport-png` is always correct and captures everything visible in the viewport, including HUD layers (OBJ-043). It does not require `preserveDrawingBuffer` because CDP captures from the compositor surface, not the canvas buffer.
- `canvas-png` captures only the WebGL canvas. Useful for testing and for verifying that HUD layers are correctly excluded from canvas-level capture. Requires `preserveDrawingBuffer: true` on the WebGLRenderer — OBJ-010 D3 sets this as the default.

**canvas-rgba (readPixels) deferred:** A raw RGBA strategy via `gl.readPixels()` was considered for V1 to eliminate PNG encode/decode overhead. Deferred per AP-05 (prioritize correctness over performance):
- For 1920×1080, the base64 transfer of raw RGBA via `page.evaluate()` is ~11MB per frame — potentially negating the throughput benefit.
- Both production strategies output PNG, which aligns with OBJ-013's `frameFormat: 'png'`.
- If capture is identified as the performance bottleneck (via TC-02 benchmarking), a `canvas-rgba` strategy using CDP `IO.read` streaming can be added without changing the `FrameCapture` interface.

**preserveDrawingBuffer performance note:** When `preserveDrawingBuffer: true` is set on the WebGLRenderer (OBJ-010's default), there is a small performance cost to all rendering — Three.js preserves the buffer after each render call. If only `viewport-png` is used and no downstream code needs `toDataURL()`, the orchestrator could set `preserveDrawingBuffer: false` in `PageInitConfig` for slightly faster rendering. However, OBJ-010's default of `true` is the safe choice and the performance difference is negligible for V1.

### D3: FrameCapture Does Not Own the Bridge

**Decision:** `FrameCapture` accepts a `PuppeteerBridge` reference in its constructor but does not call `bridge.launch()` or `bridge.close()`. The orchestrator (OBJ-035) owns the bridge lifecycle.

**Rationale:** Same rationale as OBJ-011 D1. The bridge is shared between PageProtocol (rendering) and FrameCapture (pixel extraction). The orchestrator composes them.

### D4: CDPSession Lifecycle — Lazy Creation with Staleness Detection

**Decision:** For the `viewport-png` strategy, FrameCapture obtains the CDP session via `bridge.page.createCDPSession()`. The session is created lazily on the first `capture()` call and reused for subsequent captures.

**Staleness detection:** FrameCapture tracks the `Page` instance (`bridge.page` reference) that was used to create the current CDPSession. On each `capture()` call:
1. Check `bridge.isLaunched === true`. If false, throw `FrameCaptureError` with code `BRIDGE_NOT_LAUNCHED`.
2. Compare `bridge.page` to the stored page reference. If they differ (the bridge was closed and re-launched, which creates a new `Page` instance), discard the cached CDPSession and create a new one from `bridge.page`.
3. Use the (valid) CDPSession for the CDP call.

This works because:
- `bridge.close()` destroys the browser and page. After re-`launch()`, `bridge.page` is a new `Page` instance — referential inequality detects the change.
- The old CDPSession is implicitly invalidated when the browser closes. No explicit disposal needed.

**The CDPSession is NOT explicitly disposed by FrameCapture.** It is valid for the lifetime of the page and is implicitly cleaned up when the page/browser is closed. For V1, implicit cleanup via page closure is sufficient.

### D5: Statistics via performance.now()

**Decision:** FrameCapture tracks per-frame capture timing using `performance.now()` (available in Node.js via `perf_hooks` or globally in Node 16+) and provides aggregate statistics via `getStats()`. Statistics include count, total/average/min/max capture times, and the configured strategy.

**Rationale:** TC-02 (render performance) requires measuring the per-frame capture overhead. `performance.now()` provides sub-millisecond precision, which is valuable for distinguishing capture overhead from render overhead in OBJ-035's performance logs. `Date.now()` provides only millisecond precision, which would be insufficient for captures that complete in <1ms.

### D6: Error Classification via FrameCaptureErrorCode

**Decision:** Capture failures are wrapped in `FrameCaptureError` with structured error codes. The error codes distinguish between bridge state issues (not launched), page state issues (canvas not found, WebGL context lost), and capture mechanism failures.

**Rationale:** The orchestrator (OBJ-035) needs to distinguish between recoverable errors (retry the frame) and fatal errors (abort the render). A context-lost error is fatal; a transient CDP failure might be retryable.

### D7: canvasSelector Defaults to OBJ-010's Canvas ID

**Decision:** The `canvasSelector` config defaults to `'#depthkit-canvas'`, matching OBJ-010's page shell `<canvas id="depthkit-canvas">` (OBJ-010 `index.html`, line 236 of the OBJ-010 spec). Configurable for edge cases (e.g., testing with a different page structure).

**Cross-objective contract:** OBJ-010 defines the canvas element with `id='depthkit-canvas'`. OBJ-012's default `canvasSelector` depends on this. If OBJ-010 changes the ID, OBJ-012's default must be updated.

### D8: Buffer Validation

**Decision:** After each capture, FrameCapture validates the result buffer:
- Checks that the buffer starts with the PNG magic bytes (`\x89PNG\r\n\x1a\n`) and has length > 8.

If validation fails, throws `FrameCaptureError` with code `INVALID_BUFFER`.

**Rationale:** Catches silent capture failures (e.g., CDP returns empty data, `toDataURL()` returns an empty/corrupt string due to context loss) before the corrupt data reaches FFmpeg, where it would cause a cryptic encoding error.

### D9: Scope Relationship with OBJ-009

**Decision:** OBJ-012 does NOT modify OBJ-009's `PuppeteerBridge` class. It accesses the bridge's `page` property (already public per OBJ-009's interface) to obtain CDP sessions and execute canvas-level captures. It accesses `bridge.isLaunched` for state checks and `bridge.evaluate()` for the canvas-png strategy.

OBJ-009's `captureFrame()` method remains available but is not used by OBJ-012 or OBJ-035 in the production render loop. `captureFrame()` is a convenience method for debugging and testing.

**Rationale:** OBJ-009 is verified. Modifying it would require re-verification. OBJ-012 provides a higher-level, optimized capture service that supersedes `bridge.captureFrame()` for production use.

## Acceptance Criteria

### Construction and Configuration

- [ ] **AC-01:** `FrameCapture` is importable from `src/engine/frame-capture.ts`. `new FrameCapture(bridge)` creates an instance with strategy `'viewport-png'` and canvasSelector `'#depthkit-canvas'`.
- [ ] **AC-02:** `new FrameCapture(bridge, { strategy: 'canvas-png' })` creates an instance with `strategy === 'canvas-png'`.
- [ ] **AC-03:** `capture.width` and `capture.height` match the bridge's configured viewport dimensions.

### viewport-png Capture

- [ ] **AC-04:** After rendering a scene with a colored mesh via PageProtocol, `capture.capture()` returns a `CaptureResult` with `format: 'png'`, `data` starting with PNG magic bytes (`\x89PNG\r\n\x1a\n`), and `width`/`height` matching the viewport.
- [ ] **AC-05:** The captured PNG is NOT all-black (proves the rendered scene was captured, not just the clear color with nothing rendered).
- [ ] **AC-06:** Two consecutive captures of the same rendered frame produce identical `data` buffers (determinism, C-05).
- [ ] **AC-07:** The capture includes HTML elements overlaid on the canvas (proving viewport-level capture). Verifiable by adding a visible `<div>` with a solid background color over the canvas via `bridge.evaluate()`, capturing, and confirming the captured PNG contains the overlay color at the expected position.

### canvas-png Capture

- [ ] **AC-08:** With strategy `'canvas-png'`, `capture()` returns a `CaptureResult` with `format: 'png'`, valid PNG data.
- [ ] **AC-09:** With strategy `'canvas-png'`, HTML elements overlaid on the canvas are NOT captured (canvas-only). Verifiable by the same overlay test as AC-07 — the overlay color should NOT appear in the capture.
- [ ] **AC-10:** With strategy `'canvas-png'`, if the WebGLRenderer was created without `preserveDrawingBuffer: true`, the captured PNG is all-black (demonstrating the dependency). Note: this tests a misconfiguration scenario — OBJ-010's default is `preserveDrawingBuffer: true`, so this would only occur if the default is overridden.

### Error Handling

- [ ] **AC-11:** `capture()` when `bridge.isLaunched === false` throws `FrameCaptureError` with code `'BRIDGE_NOT_LAUNCHED'`.
- [ ] **AC-12:** `capture()` with strategy `'canvas-png'` when the canvas element matching `canvasSelector` does not exist throws `FrameCaptureError` with code `'CANVAS_NOT_FOUND'`.
- [ ] **AC-13:** `FrameCaptureError` instances have `code`, `message`, and optional `details` properties. `error instanceof FrameCaptureError` is `true`. `error instanceof Error` is `true`.

### Statistics

- [ ] **AC-14:** After 0 captures, `getStats()` returns `captureCount: 0`, `averageCaptureMs: 0`, `minCaptureMs: Infinity`, `maxCaptureMs: 0`.
- [ ] **AC-15:** After N captures, `getStats()` returns `captureCount: N`, `totalCaptureMs` > 0, `averageCaptureMs` approximately equal to `totalCaptureMs / N`.
- [ ] **AC-16:** `resetStats()` resets all statistics to their initial values. Subsequent `getStats()` returns zeroed stats.
- [ ] **AC-17:** Each `CaptureResult.captureMs` is > 0 (non-zero timing).

### Buffer Validation

- [ ] **AC-18:** If CDP returns an empty screenshot (simulated by intercepting the CDP response or by other means), `capture()` throws `FrameCaptureError` with code `'INVALID_BUFFER'`.
- [ ] **AC-19:** If `canvas.toDataURL()` returns a blank result (e.g., due to missing `preserveDrawingBuffer` or context loss), and the resulting buffer fails PNG magic byte validation, `capture()` throws `FrameCaptureError` with code `'INVALID_BUFFER'`.

### Format Alignment with OBJ-013

- [ ] **AC-20:** The `data` buffer from both strategies is directly consumable by `FFmpegEncoder.writeFrame()` when the encoder is configured with `frameFormat: 'png'`.

### CDPSession Management

- [ ] **AC-21:** After bridge close and re-launch, FrameCapture detects the stale CDPSession (via page reference comparison) and creates a new one. Capture succeeds after re-launch.

## Edge Cases and Error Handling

### Capture

| Scenario | Expected Behavior |
|---|---|
| `capture()` before bridge is launched | `FrameCaptureError` with code `BRIDGE_NOT_LAUNCHED`. |
| `capture()` after bridge is closed | `FrameCaptureError` with code `BRIDGE_NOT_LAUNCHED` (bridge.isLaunched is false after close). |
| Canvas element not found (canvas-png) | `FrameCaptureError` with code `CANVAS_NOT_FOUND`, message includes the selector. |
| WebGL context lost before capture | For canvas-png: detected by checking `gl.isContextLost()` inside the evaluate call. Throws `FrameCaptureError` with code `WEBGL_CONTEXT_LOST`. For viewport-png: CDP may return an empty or corrupt response; caught by buffer validation as `INVALID_BUFFER`. |
| CDP session disconnected (e.g., page navigated away) | CDP call rejects. Caught and wrapped as `FrameCaptureError` with code `CAPTURE_FAILED`, original error in `details`. |
| Very large viewport (e.g., 3840×2160) | Works but slow. No artificial limit — the caller (OBJ-035) controls viewport dimensions. |
| Very small viewport (e.g., 1×1) | Works. |
| Page has no WebGL canvas (e.g., init not called) | viewport-png captures the blank page (valid PNG of black). canvas-png throws `CANVAS_NOT_FOUND` if the canvas element doesn't exist, or returns a black/blank PNG if it exists but has no rendered content. |
| Multiple FrameCapture instances on the same bridge | Allowed. Each creates its own CDPSession (for viewport-png). No interference. Statistics are per-instance. |
| capture() called concurrently (parallel calls) | Not safe. CDP screenshot and evaluate are serialized by Puppeteer/CDP anyway, but concurrent calls may interleave statistics tracking. The orchestrator's deterministic frame loop (C-03) guarantees sequential calls. Not a design concern. |
| `preserveDrawingBuffer: false` with canvas-png strategy | `canvas.toDataURL()` returns blank (all-black or all-transparent) data. Buffer validation passes (it's a valid PNG), but the image content is empty. This is a misconfiguration — OBJ-010's default is `preserveDrawingBuffer: true`. The strategy documentation notes this dependency. The orchestrator should verify `preserveDrawingBuffer` is set when using canvas-png, or simply use viewport-png (which is unaffected). |

### CDPSession Management

| Scenario | Expected Behavior |
|---|---|
| First capture() call (viewport-png) | CDPSession created lazily from `bridge.page`. Stored alongside the page reference. Subsequent captures reuse it. |
| Bridge closed and re-launched | `bridge.page` is a new `Page` instance. FrameCapture detects `bridge.page !== storedPageRef`, discards cached CDPSession, creates a new one from current `bridge.page`. |
| CDPSession creation fails | Wrapped as `FrameCaptureError` with code `CAPTURE_FAILED`. |
| canvas-png strategy (no CDPSession needed) | No CDPSession created. Uses `bridge.evaluate()` directly. Staleness detection is N/A — `bridge.evaluate()` uses the current page. |

### Buffer Validation

| Scenario | Expected Behavior |
|---|---|
| PNG buffer < 8 bytes | `FrameCaptureError` with code `INVALID_BUFFER`, message: "Captured PNG buffer too small ({length} bytes)". |
| PNG buffer doesn't start with magic bytes | `FrameCaptureError` with code `INVALID_BUFFER`, message: "Captured buffer is not valid PNG data". |
| Blank but valid PNG (all-black frame) | NOT an error. Blank frames are valid (e.g., opacity=0 render pass). The validator checks PNG structure, not content. |

## Test Strategy

### Unit Tests: `test/unit/frame-capture.test.ts`

1. **Construction defaults:** `new FrameCapture(bridge)` produces `strategy === 'viewport-png'`, `canvasSelector === '#depthkit-canvas'`, width/height from bridge config.
2. **Construction with config:** Custom strategy and canvasSelector are stored correctly.
3. **FrameCaptureError:** Construct with code/message/details, verify `instanceof Error`, verify properties.
4. **Stats initial state:** `getStats()` before any captures returns zeroed stats with `minCaptureMs: Infinity`, `maxCaptureMs: 0`.
5. **Stats reset:** `resetStats()` returns stats to initial state.
6. **PNG magic byte validation:** Test the internal validation logic with valid PNG buffers, truncated buffers, and non-PNG data.

### Integration Tests: `test/integration/frame-capture.test.ts`

These tests launch real headless Chromium. Use small viewports (e.g., 320×240) and simple test scenes for speed.

**Setup per test:** Create a PuppeteerBridge, launch it, create a PageProtocol, initialize the page, set up a scene with a colored mesh, render a frame.

7. **viewport-png basic capture:** Render a red mesh, capture, verify PNG magic bytes, verify result is not all-black.
8. **viewport-png determinism (TC-06):** Capture the same rendered frame twice, verify identical buffers.
9. **viewport-png includes HUD:** Add a visible `<div>` over the canvas via evaluate, capture, verify the overlay is in the captured PNG (check pixel color at the overlay position by decoding the PNG with a lightweight decoder or comparing against a capture without the overlay).
10. **canvas-png basic capture:** Render a scene, capture with canvas-png, verify PNG magic bytes.
11. **canvas-png excludes HUD:** Add a visible `<div>` over the canvas, capture with canvas-png, verify the overlay is NOT in the captured PNG.
12. **Error: bridge not launched:** Create FrameCapture with an unlaunched bridge, call capture(), verify FrameCaptureError with BRIDGE_NOT_LAUNCHED.
13. **Error: canvas not found:** Use a non-matching canvasSelector with canvas-png, verify FrameCaptureError with CANVAS_NOT_FOUND.
14. **Statistics tracking:** Capture 5 frames, verify getStats() returns captureCount: 5, totalCaptureMs > 0, averageCaptureMs ≈ totalCaptureMs / 5.
15. **Statistics reset:** Capture, resetStats(), capture, verify captureCount: 1.
16. **CDPSession reuse:** Capture multiple frames, verify no performance degradation from session creation (timing should be consistent after the first capture).
17. **Bridge re-launch recovery:** Launch bridge, create FrameCapture, capture works. Close bridge, re-launch bridge, capture works again with fresh CDPSession.
18. **Format compatibility with OBJ-013:** Capture a frame with viewport-png, pipe the buffer to FFmpegEncoder with `frameFormat: 'png'`, verify FFmpeg produces a valid MP4.

### Performance Baseline (TC-02)

19. **Per-frame capture latency:** Render and capture 30 frames at 320×240 with each strategy. Log average capture time per strategy. This provides a baseline for OBJ-035 to compare against the 500ms/frame budget (TC-02). Do NOT assert a threshold — just log.
20. **1080p capture latency:** Render and capture 10 frames at 1920×1080 with viewport-png. Log average capture time. This is the production-relevant data point.

### Relevant Testable Claims

- **TC-02** (render performance): Tests 19-20 measure capture overhead as a component of total render time.
- **TC-06** (deterministic output): Test 8 verifies capture determinism.
- **TC-11** (Docker/software WebGL): All integration tests run with `gpu: false` (SwiftShader) by default, validating software rendering capture correctness.

## Integration Points

### Depends on

| Dependency | What OBJ-012 uses |
|---|---|
| **OBJ-009** (PuppeteerBridge) | `PuppeteerBridge` instance — accesses `bridge.page` for CDPSession creation (viewport-png) and `bridge.evaluate()` for canvas-level capture (canvas-png). Accesses `bridge.isLaunched` for state checks. Uses bridge's configured `width` and `height` for CaptureResult metadata. Does NOT use `bridge.captureFrame()` — OBJ-012 supersedes it for production capture. |
| **OBJ-011** (PageProtocol) | Indirect dependency — OBJ-011 must have rendered a frame (via `protocol.renderFrame()`) before `capture.capture()` is called. OBJ-012 does not import or call OBJ-011 directly; the orchestrator (OBJ-035) sequences the calls. |
| **OBJ-010** (Page shell) | The canvas element ID `#depthkit-canvas` (OBJ-010 `index.html`) is the default `canvasSelector`. If OBJ-010 changes this ID, OBJ-012's default must be updated. The `canvas-png` strategy requires `preserveDrawingBuffer: true` on the WebGLRenderer — OBJ-010 D3 sets this as the default. If the orchestrator sets `preserveDrawingBuffer: false` in `PageInitConfig`, the `canvas-png` strategy will silently produce blank frames. The `viewport-png` strategy is unaffected by `preserveDrawingBuffer`. |

### Consumed by

| Downstream | How it uses OBJ-012 |
|---|---|
| **OBJ-035** (Orchestrator) | The primary consumer. Creates a `FrameCapture` instance alongside `PageProtocol` and `FFmpegEncoder`. In the render loop: `protocol.renderFrame()` → `capture.capture()` → `encoder.writeFrame(result.data)`. Selects strategy based on whether the composition uses HUD layers. Logs `capture.getStats()` after the render loop. |
| **OBJ-043** (HUD layer system) | Requires `viewport-png` strategy to capture HTML/CSS overlay elements. OBJ-043 validates that its overlays appear in captured frames. |
| **OBJ-049** (Software rendering config) | Validates that frame capture produces correct output with software WebGL (SwiftShader). Uses either capture strategy — the concern is software rendering correctness, not capture method. |

### File Placement

```
depthkit/
  src/
    engine/
      frame-capture.ts        # NEW — FrameCapture class, CaptureStrategy,
                               #       FrameCaptureConfig, CaptureResult,
                               #       CaptureStats, FrameCaptureError
  test/
    unit/
      frame-capture.test.ts   # NEW — unit tests
    integration/
      frame-capture.test.ts   # NEW — integration tests with Puppeteer
```

## Open Questions

### OQ-A: Is a raw RGBA capture strategy needed for V1?

A `canvas-rgba` strategy using `gl.readPixels()` would eliminate PNG encode/decode overhead, potentially improving throughput for canvas-only scenes. For 1920×1080, the raw buffer is ~8MB but the base64 transfer via `page.evaluate()` would be ~11MB per frame. At 1,800 frames, that's ~20GB of string data through V8's JSON serializer — potentially negating the throughput benefit.

Deferred per AP-05 (prioritize correctness over render speed). If TC-02 benchmarking reveals capture as the bottleneck, revisit with:
- CDP `IO.read` streaming API to transfer the buffer without base64 overhead
- `renderer.getContext()` (Three.js API) for WebGL context access (works for both WebGL1 and WebGL2)
- `gl.readPixels(0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, pixels)` followed by a vertical row flip (readPixels returns bottom-to-top; FFmpeg rawvideo expects top-to-bottom)

The `FrameCapture` interface (`CaptureStrategy` union, `CaptureResult.format`) can accommodate a `'canvas-rgba'` strategy without breaking changes.

### OQ-B: Should FrameCapture support JPEG format for preview mode?

A `viewport-jpeg` strategy with configurable quality (e.g., 80%) would produce smaller buffers and faster captures for preview/debugging workflows (seed OQ-05). Deferred — the current two strategies cover production needs. JPEG can be added later without interface changes.

### OQ-C: Should capture() accept per-call options overriding the constructor config?

E.g., `capture({ strategy: 'canvas-png' })` to switch strategies mid-render. Currently the strategy is fixed at construction time. If OBJ-035 needs to switch strategies (e.g., viewport-png for HUD frames, canvas-png for non-HUD frames), it would create two FrameCapture instances. Per-call override is simpler but adds complexity to the interface. Deferred until OBJ-035's spec reveals the need.

---

## Summary of Changes from Round 1

| # | Issue | Resolution |
|---|---|---|
| 1 (Critical) | `preserveDrawingBuffer` requirement | Documented explicitly: OBJ-010 D3 already defaults to `true`. Cross-objective dependency noted in Integration Points. canvas-png strategy docs note the requirement. Added AC-10 testing the misconfiguration case. Added edge case row for `preserveDrawingBuffer: false`. |
| 2 (Major) | CDPSession staleness detection | D4 now specifies the exact mechanism: track the `Page` reference from which the CDPSession was created; on each `capture()`, compare `bridge.page` to the stored reference; if different, discard and recreate. |
| 3 (Major) | WebGL context acquisition for readPixels | Entire `canvas-rgba` strategy deferred to OQ-A. The OQ documents the implementation details (`renderer.getContext()`, readPixels params, vertical flip) for future reference. |
| 4 (Major) | `canvas-rgba` is premature optimization | Demoted to OQ-A per AP-05. V1 ships two PNG strategies only. |
| 5 (Minor) | `fromSurface` deprecated | Removed from CDP call. Note added to D1. |
| 6 (Minor) | Timing function unspecified | D5 specifies `performance.now()` with rationale for sub-ms precision. |
| 7 (Minor) | Canvas ID coupling | D7 now explicitly references OBJ-010's `index.html` line. Integration Points table documents the cross-objective contract and update obligation. |
| 8 (Minor) | preserveDrawingBuffer performance note | Added to D2's trade-off discussion. Notes that viewport-png doesn't need it, and the orchestrator could disable it when using viewport-png exclusively. |

I believe all 8 issues have been fully addressed. Challenger, please verify and approve if satisfied.

---

## Round 4 — spec_challenger


[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": "85",
  "limit": "120"
}
[Tool Result]     85→
    86→  /**
    87→   * Static factory: create a FrameClock from a duration in seconds.
    88→   * totalFrames = Math.ceil(durationSeconds * fps).
    89→   *
    90→   * @param fps — Frames per second.
    91→   * @param durationSeconds — Desired duration in seconds. Must be positive.
    92→   * @returns FrameClock instance.
    93→   */
    94→  static fromDuration(fps: number, durationSeconds: number): FrameClock;
    95→}
    96→```
    97→
    98→### Module: `src/engine/puppeteer-bridge.ts`
    99→
   100→```typescript
   101→import type { Page, Browser } from 'puppeteer';
   102→
   103→/**
   104→ * Configuration for launching the PuppeteerBridge.
   105→ */
   106→export interface PuppeteerBridgeConfig {
   107→  /** Viewport width in pixels. Must be a positive integer. */
   108→  width: number;
   109→  /** Viewport height in pixels. Must be a positive integer. */
   110→  height: number;
   111→  /**
   112→   * Absolute path to the built page directory containing... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": "200",
  "limit": "120"
}
[Tool Result]    200→  launch(): Promise<void>;
   201→
   202→  /**
   203→   * Execute a function in the browser page context.
   204→   * Thin wrapper around Puppeteer's page.evaluate().
   205→   *
   206→   * This is the primitive that OBJ-011 builds its message protocol on.
   207→   * The orchestrator (OBJ-035) uses it via OBJ-011's higher-level API.
   208→   *
   209→   * @param pageFunction — Function or string to evaluate in the page.
   210→   * @param args — Serializable arguments passed to the function.
   211→   * @returns The serializable return value from the page function.
   212→   * @throws Error if not launched.
   213→   * @throws Error if a prior uncaught page error was detected (pageerror).
   214→   * @throws Error if the page function throws (error is propagated).
   215→   */
   216→  evaluate<T>(
   217→    pageFunction: string | ((...args: any[]) => T),
   218→    ...args: any[]
   219→  ): Promise<T>;
   220→
   221→  /**
   222→   * Capture the current state of the pag... [truncated]
Good — I've confirmed **`bridge.page` is public** (line 253-257 of OBJ-009): `readonly page: Page | null`. It's explicitly documented as "Exposed for advanced use by OBJ-011."

Now let me verify the full revised spec systematically.

---

## Verification of Round 2 Fixes

| # | Issue | Status | Verification |
|---|---|---|---|
| 1 | `preserveDrawingBuffer` | ✅ **Fixed** | CaptureStrategy docs note it. D2 trade-off table. Integration Points OBJ-010 row. AC-10. Edge case table row. |
| 2 | CDPSession staleness | ✅ **Fixed** | D4 specifies page-reference comparison mechanism. AC-21 tests it. Edge case table covers it. |
| 3 | WebGL readPixels unspecified | ✅ **Fixed** | Removed by deferring canvas-rgba. OQ-A preserves technical details. |
| 4 | canvas-rgba premature optimization | ✅ **Fixed** | Demoted to OQ-A. V1 is two PNG strategies only. |
| 5 | `fromSurface` deprecated | ✅ **Fixed** | Removed from D1 CDP call. |
| 6 | Timing function | ✅ **Fixed** | D5 specifies `performance.now()`. |
| 7 | Canvas ID coupling | ✅ **Fixed** | D7 explicit reference. Integration Points documents contract. |
| 8 | preserveDrawingBuffer perf note | ✅ **Fixed** | D2 documents the trade-off. |

All 8 issues are structurally resolved. Let me now scan for any new issues introduced by the revision...

**New scan results:** I find no new critical or major issues. The spec is clean, focused, and implementable. A few observations:

1. The `format: 'png'` literal type on `CaptureResult` is forward-compatible — widening to `'png' | 'rgba'` later is a non-breaking change.
2. AC-10 testing `preserveDrawingBuffer: false` misconfiguration is a nice defensive test — it documents expected behavior for an edge case that a developer might hit during debugging.
3. The CDPSession staleness mechanism (D4) is well-specified — the page reference comparison is the cleanest detection approach.
4. The edge case table is thorough and covers the scenarios I'd worry about.

I'm satisfied. All critical and major objections have been properly addressed. The spec is implementable by a competent developer using only this document plus the seed and dependency specs.

CONCLUSION:

The OBJ-012 specification defines the `FrameCapture` class — a configurable frame extraction service sitting between OBJ-011's rendered page state and OBJ-013's FFmpeg encoder input. It provides two V1 capture strategies: `viewport-png` (CDP `Page.captureScreenshot` for full viewport including HUD overlays) and `canvas-png` (`canvas.toDataURL()` for WebGL-only capture). Key design decisions: CDP direct capture bypassing `page.screenshot()` for throughput; lazy CDPSession creation with page-reference staleness detection; `performance.now()` timing for sub-ms capture statistics; PNG buffer validation via magic bytes; and deferral of raw RGBA capture per AP-05. The spec correctly documents the `preserveDrawingBuffer` cross-dependency with OBJ-010, scope relationship with OBJ-009, and format alignment with OBJ-013.

Let me write the final spec and update meta.json.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/output.md",
  "content": "# Specification: OBJ-012 \u2014 Frame Capture Pipeline\n\n## Summary\n\nOBJ-012 delivers the `FrameCapture` class (`src/engine/frame-capture.ts`) \u2014 the configurable frame extraction service that sits between OBJ-011's rendered page state and OBJ-013's FFmpeg encoder input. It provides two capture strategies: `viewport-png` (CDP `Page.captureScreenshot` for full viewport capture including HUD overlays) and `canvas-png` (canvas-level `toDataURL()` for WebGL-only capture). The module tracks capture timing statistics for performance monitoring and establishes the capture format contract that OBJ-035 (orchestrator) uses to bridge rendering and encoding. This implements the \"capture\" step in seed Section 4.4 step 3f and completes the browser-side capture half of C-02.\n\n## Interface Contract\n\n### Module: `src/engine/frame-capture.ts`\n\n```typescript\nimport type { PuppeteerBridge } from './puppeteer-bridge.js';\n\n/**\n * Capture strategy determines both the capture mechanism and the\n * output buffer format.\n *\n * - 'viewport-png': CDP Page.captureScreenshot with optimizeForSpeed.\n *   Captures the full composited viewport \u2014 the WebGL canvas plus\n *   any HTML/CSS elements layered on top (HUD layers per OBJ-043).\n *   Output is a PNG-encoded Buffer. This is the production default.\n *   Does NOT require preserveDrawingBuffer on the WebGLRenderer.\n *\n * - 'canvas-png': Extracts the canvas content via page.evaluate()\n *   calling canvas.toDataURL('image/png'). Captures only the WebGL\n *   canvas \u2014 HTML overlays are NOT included. Output is a PNG-encoded\n *   Buffer (base64-decoded from toDataURL result). Useful for\n *   canvas-only capture when HUD layers are absent and for testing.\n *   REQUIRES preserveDrawingBuffer: true on the WebGLRenderer\n *   (OBJ-010 D3 \u2014 this is OBJ-010's default).\n */\nexport type Ca
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/output.md
Now update meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-012",
     3→  "description": "Puppeteer bridge and frame capture -- Puppeteer launch configuration (headless mode, viewport size, WebGL flags), page loading strategy, frame capture via CDP Page.captureScreenshot vs canvas.toDataURL vs canvas.toBlob, pixel buffer extraction and format (PNG vs raw RGBA). Implements the browser-side capture half of C-02 (Puppeteer + Three.js + FFmpeg pipeline).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-011"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Depends on message protocol (OBJ-011) for communication with the page."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/meta.json",
  "content": "{\n  \"id\": \"OBJ-012\",\n  \"description\": \"Frame capture pipeline -- FrameCapture class providing CDP Page.captureScreenshot (viewport-png) and canvas.toDataURL (canvas-png) strategies for extracting rendered frames as PNG buffers. Sits between OBJ-011 renderFrame and OBJ-013 FFmpeg encoder. Includes CDPSession management, PNG buffer validation, and capture statistics. Implements the browser-side capture half of C-02.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"spec-deliberation\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-011\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 engine core. Delivers FrameCapture class (src/engine/frame-capture.ts). Two strategies: viewport-png (production default, captures HUD layers via CDP) and canvas-png (canvas-only, requires preserveDrawingBuffer). canvas-rgba deferred to OQ-A per AP-05. Depends on OBJ-009 bridge.page for CDPSession, OBJ-010 canvas ID (#depthkit-canvas) and preserveDrawingBuffer default, OBJ-011 for frame rendering sequencing.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/meta.json has been updated successfully.
Now commit to git:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Check git status for OBJ-012 files"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "View recent commit messages"
}
[Tool Result] 6dbb8fc spec(OBJ-021): flyover scene geometry specification
fd55d28 spec(OBJ-020): canyon scene geometry specification
4fb72b7 spec(OBJ-014): FFmpeg audio muxing specification
85a7d42 spec(OBJ-019): tunnel scene geometry specification
9ea9d41 spec(OBJ-011): Puppeteer-to-page message protocol
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-012/meta.json

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
	nodes/OBJ-008/transcript.md
	nodes/OBJ-009/transcript.md
	nodes/OBJ-010/transcript.md
	nodes/OBJ-011/transcript.md
	nodes/OBJ-012/output.md
	nodes/OBJ-013/transcript.md
	nodes/OBJ-014/transcript.md
	nodes/OBJ-015/transcript.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-019/transcript.md
	nodes/OBJ-020/transcript.md
	nodes/OBJ-021/transcript.md
	nodes/OBJ-026/transcript.md
	nodes/OBJ-... [truncated]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-012/output.md nodes/OBJ-012/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-012): frame capture pipeline specification\n\nDefines FrameCapture class (src/engine/frame-capture.ts) with two\ncapture strategies: viewport-png (CDP Page.captureScreenshot for\nproduction, captures HUD layers) and canvas-png (canvas.toDataURL\nfor canvas-only testing). Includes CDPSession lazy creation with\nstaleness detection, PNG buffer validation via magic bytes, and\nperformance.now() capture statistics. Raw RGBA capture deferred\nper AP-05. Depends on OBJ-009 bridge.page, OBJ-010 canvas ID and\npreserveDrawingBuffer, OBJ-011 for render sequencing.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-012 spec files"
}
[Tool Result] [master a17e226] spec(OBJ-012): frame capture pipeline specification
 2 files changed, 481 insertions(+), 4 deletions(-)
 create mode 100644 nodes/OBJ-012/output.md
The specification for OBJ-012 has been written to `nodes/OBJ-012/output.md`, `meta.json` updated, and committed as `a17e226`.

**Summary of the converged specification:**

The OBJ-012 Frame Capture Pipeline delivers a `FrameCapture` class with two V1 capture strategies:

1. **`viewport-png`** (production default) — Uses CDP `Page.captureScreenshot` with `optimizeForSpeed: true`, bypassing Puppeteer's `page.screenshot()` overhead. Captures the full composited viewport including HUD layers. Does not require `preserveDrawingBuffer`.

2. **`canvas-png`** — Uses `canvas.toDataURL('image/png')` via `bridge.evaluate()`. Captures only the WebGL canvas (no HUD overlays). Requires `preserveDrawingBuffer: true` (OBJ-010's default).

**Key design decisions resolved during deliberation:**
- **canvas-rgba deferred** (was a premature optimization per AP-05 — ~11MB base64 per frame at 1080p would negate throughput gains)
- **CDPSession staleness detection** via page reference comparison (tracks `bridge.page` instance, recreates session when it changes after bridge close/re-launch)
- **`preserveDrawingBuffer` cross-dependency** explicitly documented (OBJ-010 D3 already defaults to `true`; canvas-png requires it, viewport-png doesn't)
- **`performance.now()`** for sub-ms capture timing precision
- **PNG buffer validation** via magic bytes before data reaches FFmpeg
- **`fromSurface` CDP parameter** omitted (deprecated since Chrome 92)
