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
| `viewport-png` | Yes | No | CDP screenshot (base64 PNG) | Production (default) |
| `canvas-png` | No | Yes (OBJ-010 default) | `canvas.toDataURL()` (base64 PNG) | Canvas-only testing |

**Rationale:**
- `viewport-png` is always correct and captures everything visible in the viewport, including HUD layers (OBJ-043). It does not require `preserveDrawingBuffer` because CDP captures from the compositor surface, not the canvas buffer.
- `canvas-png` captures only the WebGL canvas. Useful for testing and for verifying that HUD layers are correctly excluded from canvas-level capture. Requires `preserveDrawingBuffer: true` on the WebGLRenderer — OBJ-010 D3 sets this as the default.

**canvas-rgba (readPixels) deferred:** A raw RGBA strategy via `gl.readPixels()` was considered for V1 to eliminate PNG encode/decode overhead. Deferred per AP-05 (prioritize correctness over performance):
- For 1920x1080, the base64 transfer of raw RGBA via `page.evaluate()` is ~11MB per frame — potentially negating the throughput benefit.
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

**Decision:** The `canvasSelector` config defaults to `'#depthkit-canvas'`, matching OBJ-010's page shell `<canvas id="depthkit-canvas">` (OBJ-010 `index.html`). Configurable for edge cases (e.g., testing with a different page structure).

**Cross-objective contract:** OBJ-010 defines the canvas element with `id='depthkit-canvas'`. OBJ-012's default `canvasSelector` depends on this. If OBJ-010 changes the ID, OBJ-012's default must be updated.

### D8: Buffer Validation

**Decision:** After each capture, FrameCapture validates the result buffer:
- Checks that the buffer starts with the PNG magic bytes (`\x89PNG\r\n\x1a\n`) and has length > 8.

If validation fails, throws `FrameCaptureError` with code `INVALID_BUFFER`.

**Rationale:** Catches silent capture failures (e.g., CDP returns empty data, `toDataURL()` returns an empty/corrupt string due to context loss) before the corrupt data reaches FFmpeg, where it would cause a cryptic encoding error.

### D9: Scope Relationship with OBJ-009

**Decision:** OBJ-012 does NOT modify OBJ-009's `PuppeteerBridge` class. It accesses the bridge's `page` property (public per OBJ-009's interface: `readonly page: Page | null`) to obtain CDP sessions and execute canvas-level captures. It accesses `bridge.isLaunched` for state checks and `bridge.evaluate()` for the canvas-png strategy.

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
| Very large viewport (e.g., 3840x2160) | Works but slow. No artificial limit — the caller (OBJ-035) controls viewport dimensions. |
| Very small viewport (e.g., 1x1) | Works. |
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

These tests launch real headless Chromium. Use small viewports (e.g., 320x240) and simple test scenes for speed.

**Setup per test:** Create a PuppeteerBridge, launch it, create a PageProtocol, initialize the page, set up a scene with a colored mesh, render a frame.

7. **viewport-png basic capture:** Render a red mesh, capture, verify PNG magic bytes, verify result is not all-black.
8. **viewport-png determinism (TC-06):** Capture the same rendered frame twice, verify identical buffers.
9. **viewport-png includes HUD:** Add a visible `<div>` over the canvas via evaluate, capture, verify the overlay is in the captured PNG (check pixel color at the overlay position by decoding the PNG with a lightweight decoder or comparing against a capture without the overlay).
10. **canvas-png basic capture:** Render a scene, capture with canvas-png, verify PNG magic bytes.
11. **canvas-png excludes HUD:** Add a visible `<div>` over the canvas, capture with canvas-png, verify the overlay is NOT in the captured PNG.
12. **Error: bridge not launched:** Create FrameCapture with an unlaunched bridge, call capture(), verify FrameCaptureError with BRIDGE_NOT_LAUNCHED.
13. **Error: canvas not found:** Use a non-matching canvasSelector with canvas-png, verify FrameCaptureError with CANVAS_NOT_FOUND.
14. **Statistics tracking:** Capture 5 frames, verify getStats() returns captureCount: 5, totalCaptureMs > 0, averageCaptureMs approximately equal to totalCaptureMs / 5.
15. **Statistics reset:** Capture, resetStats(), capture, verify captureCount: 1.
16. **CDPSession reuse:** Capture multiple frames, verify no performance degradation from session creation (timing should be consistent after the first capture).
17. **Bridge re-launch recovery:** Launch bridge, create FrameCapture, capture works. Close bridge, re-launch bridge, capture works again with fresh CDPSession.
18. **Format compatibility with OBJ-013:** Capture a frame with viewport-png, pipe the buffer to FFmpegEncoder with `frameFormat: 'png'`, verify FFmpeg produces a valid MP4.

### Performance Baseline (TC-02)

19. **Per-frame capture latency:** Render and capture 30 frames at 320x240 with each strategy. Log average capture time per strategy. This provides a baseline for OBJ-035 to compare against the 500ms/frame budget (TC-02). Do NOT assert a threshold — just log.
20. **1080p capture latency:** Render and capture 10 frames at 1920x1080 with viewport-png. Log average capture time. This is the production-relevant data point.

### Relevant Testable Claims

- **TC-02** (render performance): Tests 19-20 measure capture overhead as a component of total render time.
- **TC-06** (deterministic output): Test 8 verifies capture determinism.
- **TC-11** (Docker/software WebGL): All integration tests run with `gpu: false` (SwiftShader) by default, validating software rendering capture correctness.

## Integration Points

### Depends on

| Dependency | What OBJ-012 uses |
|---|---|
| **OBJ-009** (PuppeteerBridge) | `PuppeteerBridge` instance — accesses `bridge.page` (public: `readonly page: Page \| null`) for CDPSession creation (viewport-png) and `bridge.evaluate()` for canvas-level capture (canvas-png). Accesses `bridge.isLaunched` for state checks. Uses bridge's configured `width` and `height` for CaptureResult metadata. Does NOT use `bridge.captureFrame()` — OBJ-012 supersedes it for production capture. |
| **OBJ-011** (PageProtocol) | Indirect dependency — OBJ-011 must have rendered a frame (via `protocol.renderFrame()`) before `capture.capture()` is called. OBJ-012 does not import or call OBJ-011 directly; the orchestrator (OBJ-035) sequences the calls. |
| **OBJ-010** (Page shell) | The canvas element ID `#depthkit-canvas` (OBJ-010 `index.html`) is the default `canvasSelector`. If OBJ-010 changes this ID, OBJ-012's default must be updated. The `canvas-png` strategy requires `preserveDrawingBuffer: true` on the WebGLRenderer — OBJ-010 D3 sets this as the default. If the orchestrator sets `preserveDrawingBuffer: false` in `PageInitConfig`, the `canvas-png` strategy will silently produce blank frames. The `viewport-png` strategy is unaffected by `preserveDrawingBuffer`. |

### Consumed by

| Downstream | How it uses OBJ-012 |
|---|---|
| **OBJ-035** (Orchestrator) | The primary consumer. Creates a `FrameCapture` instance alongside `PageProtocol` and `FFmpegEncoder`. In the render loop: `protocol.renderFrame()` -> `capture.capture()` -> `encoder.writeFrame(result.data)`. Selects strategy based on whether the composition uses HUD layers. Logs `capture.getStats()` after the render loop. |
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

A `canvas-rgba` strategy using `gl.readPixels()` would eliminate PNG encode/decode overhead, potentially improving throughput for canvas-only scenes. For 1920x1080, the raw buffer is ~8MB but the base64 transfer via `page.evaluate()` would be ~11MB per frame. At 1,800 frames, that's ~20GB of string data through V8's JSON serializer — potentially negating the throughput benefit.

Deferred per AP-05 (prioritize correctness over render speed). If TC-02 benchmarking reveals capture as the bottleneck, revisit with:
- CDP `IO.read` streaming API to transfer the buffer without base64 overhead
- `renderer.getContext()` (Three.js API) for WebGL context access (works for both WebGL1 and WebGL2)
- `gl.readPixels(0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, pixels)` followed by a vertical row flip (readPixels returns bottom-to-top; FFmpeg rawvideo expects top-to-bottom)

The `FrameCapture` interface (`CaptureStrategy` union, `CaptureResult.format`) can accommodate a `'canvas-rgba'` strategy without breaking changes.

### OQ-B: Should FrameCapture support JPEG format for preview mode?

A `viewport-jpeg` strategy with configurable quality (e.g., 80%) would produce smaller buffers and faster captures for preview/debugging workflows (seed OQ-05). Deferred — the current two strategies cover production needs. JPEG can be added later without interface changes.

### OQ-C: Should capture() accept per-call options overriding the constructor config?

E.g., `capture({ strategy: 'canvas-png' })` to switch strategies mid-render. Currently the strategy is fixed at construction time. If OBJ-035 needs to switch strategies (e.g., viewport-png for HUD frames, canvas-png for non-HUD frames), it would create two FrameCapture instances. Per-call override is simpler but adds complexity to the interface. Deferred until OBJ-035's spec reveals the need.

### OQ-D: CDPSession lifecycle — should FrameCapture dispose its session?

Currently the CDPSession is created lazily and not explicitly disposed. Puppeteer CDPSessions are cleaned up when the page is closed. If FrameCapture should have an explicit `dispose()` method for clean shutdown, that can be added. For V1, implicit cleanup via page closure is sufficient.
