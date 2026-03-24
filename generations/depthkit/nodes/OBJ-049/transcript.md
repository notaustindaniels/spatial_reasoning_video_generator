# Deliberation Transcript: OBJ-049

---

## Round 1 — spec_author

Looking at the objective metadata, seed constraints (especially C-11), and the OBJ-012 dependency spec, let me draft the specification for OBJ-049.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me examine the existing codebase to understand OBJ-009's PuppeteerBridge interface and any existing GPU/rendering configuration.
[Tool: Glob]
  Input: {
  "pattern": "**/puppeteer-bridge*"
}

[Tool: Glob]
  Input: {
  "pattern": "**/frame-capture*"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-009/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-049/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/meta.json"
}
[Tool Error] File content (10461 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.
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
  "limit": 150
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
  "offset": 270,
  "limit": 150
}
[Tool Result]    270→
   271→**Decision:** `FrameClock` is constructed with `fps` and `totalFrames`, then never changes. It has no internal cursor or mutable state. The `frames()` generator is a fresh iterator each time, producing frame ticks without side effects.
   272→
   273→**Rationale:** The clock is a **coordinate system**, not a ticker. It maps between frame numbers and timestamps. Statefulness (tracking "current frame") belongs to the orchestrator (OBJ-035), which may need to render frames out of order for parallelization (seed C-08 mentions splitting frame ranges). A stateless clock supports any iteration pattern.
   274→
   275→**Alternative considered:** A stateful clock with `advance()` / `currentFrame` API. Rejected because it couples the clock to sequential iteration, making parallelized rendering harder.
   276→
   277→### D3: Frame Numbers are Zero-Indexed
   278→
   279→**Decision:** Frame 0 is the first frame. Frame `totalFrames - 1` is the last frame. `frameToTimestamp(0) = 0.0`.... [truncated]
Now I have a thorough understanding of OBJ-009's PuppeteerBridge. It already has `gpu?: boolean` config and `--disable-gpu` flag handling. Let me also check OBJ-035 (orchestrator) and OBJ-050/OBJ-074 to understand downstream consumers.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-050/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-074/output.md"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-035/output.md"
}
[Tool Result] No files found
OBJ-035, OBJ-050, and OBJ-074 don't have output.md yet (OBJ-035 is in_progress, OBJ-050 and OBJ-074 are open). Let me check the existing source to understand what's already been implemented.
[Tool: Glob]
  Input: {
  "pattern": "src/engine/**/*.ts"
}

[Tool: Glob]
  Input: {
  "pattern": "src/**/*.ts"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*"
}
[Tool Result] No files found
No source code yet — this is a spec-only phase. Good. Now I have everything I need. Let me draft the specification.

---

Here is my proposed specification for OBJ-049:

---

# Specification: OBJ-049 — Software Rendering Configuration

## Summary

OBJ-049 delivers the `RenderingConfig` module (`src/engine/rendering-config.ts`) — a utility that resolves the correct Chromium launch arguments for software or hardware-accelerated WebGL rendering, detects GPU availability at runtime, and validates post-launch that the WebGL context is functional. This module enforces C-11 (engine must render correctly with software WebGL / SwiftShader, without GPU passthrough) while providing an opt-in path to GPU acceleration when available. It does not own the Puppeteer lifecycle — it produces configuration that `PuppeteerBridge` (OBJ-009) consumes, and provides post-launch validation that `FrameCapture` (OBJ-012) and the orchestrator (OBJ-035) use to confirm rendering correctness.

## Interface Contract

### Module: `src/engine/rendering-config.ts`

```typescript
import type { PuppeteerBridge } from './puppeteer-bridge.js';

/**
 * GPU rendering mode for the engine.
 *
 * - 'software': Force software rendering via SwiftShader/ANGLE.
 *   Adds --disable-gpu and related flags. Guaranteed to work in
 *   Docker containers and CI/CD without GPU passthrough. This is
 *   the C-11 baseline. Always correct, potentially slower.
 *
 * - 'hardware': Request hardware GPU acceleration. Omits
 *   --disable-gpu. Requires GPU drivers and (in Docker) GPU
 *   passthrough. Faster when available, but may fail in
 *   environments without GPU access — the caller is responsible
 *   for knowing their environment.
 *
 * - 'auto': Attempt hardware GPU, fall back to software if
 *   unavailable. Launches Puppeteer twice in the worst case
 *   (first attempt with GPU flags, probe WebGL, if probe fails
 *   re-launch with software flags). Useful for environments
 *   where GPU availability is unknown (e.g., heterogeneous
 *   deployment targets).
 */
export type GpuMode = 'software' | 'hardware' | 'auto';

/**
 * Information about the active WebGL rendering backend,
 * obtained by probing the launched browser's WebGL context.
 */
export interface WebGLRendererInfo {
  /** The WebGL renderer string from WEBGL_debug_renderer_info.
   *  e.g., "Google SwiftShader", "ANGLE (NVIDIA GeForce RTX 3080 ...)"
   *  null if the extension is unavailable. */
  renderer: string | null;

  /** The WebGL vendor string from WEBGL_debug_renderer_info.
   *  e.g., "Google Inc. (Google)", "Google Inc. (NVIDIA)"
   *  null if the extension is unavailable. */
  vendor: string | null;

  /** WebGL version string from gl.getParameter(gl.VERSION).
   *  e.g., "WebGL 2.0 (OpenGL ES 3.0 SwiftShader 5.0.0)" */
  version: string;

  /** Whether the renderer appears to be software-based.
   *  Detected by checking if the renderer string contains
   *  "SwiftShader", "llvmpipe", "Mesa", or "Software". */
  isSoftwareRenderer: boolean;

  /** Maximum texture size supported (gl.MAX_TEXTURE_SIZE).
   *  Typically 4096-16384 for hardware, 8192 for SwiftShader. */
  maxTextureSize: number;

  /** Maximum viewport dimensions (gl.MAX_VIEWPORT_DIMS).
   *  Array of [maxWidth, maxHeight]. */
  maxViewportDims: [number, number];
}

/**
 * Result of resolving the GPU mode, including the Chromium
 * launch arguments to use.
 */
export interface ResolvedRenderingConfig {
  /** The resolved GPU mode. For 'auto', this reflects the
   *  mode that was actually selected (either 'hardware' or
   *  'software') after probing. */
  resolvedMode: 'software' | 'hardware';

  /** The requested GPU mode (what the caller asked for). */
  requestedMode: GpuMode;

  /** The complete set of Chromium launch arguments for rendering.
   *  Includes all baseline args plus mode-specific GPU flags. */
  chromiumArgs: string[];

  /** Whether GPU was detected as available (only meaningful
   *  when requestedMode was 'auto'). null if detection was
   *  not performed (i.e., mode was explicitly 'software'
   *  or 'hardware'). */
  gpuDetected: boolean | null;
}

/**
 * Error thrown when WebGL validation fails after launch.
 */
export class WebGLValidationError extends Error {
  /** The specific validation failure. */
  readonly code: WebGLValidationErrorCode;
  /** The WebGLRendererInfo that was probed (if available). */
  readonly rendererInfo?: WebGLRendererInfo;

  constructor(
    code: WebGLValidationErrorCode,
    message: string,
    rendererInfo?: WebGLRendererInfo
  );
}

export type WebGLValidationErrorCode =
  | 'NO_WEBGL'            // WebGL context could not be created
  | 'CONTEXT_LOST'        // WebGL context was created but is lost
  | 'VIEWPORT_TOO_SMALL'  // maxViewportDims < requested composition size
  | 'TEXTURE_TOO_SMALL'   // maxTextureSize < largest texture dimension
  ;

/**
 * Resolve the Chromium launch arguments for a given GPU mode.
 *
 * This is a pure function — it does not launch Puppeteer or
 * perform any I/O. It produces the argument list that should
 * be passed to PuppeteerBridge via the `extraArgs` config
 * (or used to determine the `gpu` config flag).
 *
 * For 'auto' mode: returns the hardware-attempt args first.
 * The caller (orchestrator) must probe WebGL after launch and
 * call resolveGpuMode() again with 'software' if the probe fails.
 * See the orchestrator integration pattern below.
 *
 * @param mode - The requested GPU mode.
 * @returns ResolvedRenderingConfig with the args and resolved mode.
 */
export function resolveRenderingConfig(mode: GpuMode): ResolvedRenderingConfig;

/**
 * Probe the WebGL rendering backend of a launched PuppeteerBridge.
 *
 * Executes JavaScript in the browser page context to:
 * 1. Create a temporary <canvas> element.
 * 2. Obtain a WebGL context (tries WebGL2 first, falls back to WebGL1).
 * 3. Query WEBGL_debug_renderer_info for renderer/vendor strings.
 * 4. Query gl.getParameter() for version, max texture size, max viewport.
 * 5. Clean up the temporary canvas.
 *
 * The probe uses a temporary canvas — it does NOT interfere with
 * the depthkit #depthkit-canvas or the Three.js renderer.
 *
 * @param bridge - A launched PuppeteerBridge instance.
 * @returns WebGLRendererInfo with the backend details.
 * @throws Error if bridge is not launched.
 * @throws WebGLValidationError with code 'NO_WEBGL' if no WebGL
 *         context can be created (extremely unlikely in Chromium).
 */
export function probeWebGLRenderer(
  bridge: PuppeteerBridge
): Promise<WebGLRendererInfo>;

/**
 * Validate that the WebGL backend meets depthkit's minimum
 * requirements for a given composition size.
 *
 * Checks:
 * 1. WebGL context exists (probeWebGLRenderer succeeded).
 * 2. maxTextureSize >= max(width, height) of any texture
 *    the composition will use. Since texture dimensions are
 *    not known at config time, validates against the
 *    composition's viewport dimensions as a proxy (textures
 *    larger than the viewport are unusual).
 * 3. maxViewportDims >= [compositionWidth, compositionHeight].
 *
 * @param info - WebGLRendererInfo from probeWebGLRenderer().
 * @param compositionWidth - Viewport width in pixels.
 * @param compositionHeight - Viewport height in pixels.
 * @throws WebGLValidationError if any check fails.
 */
export function validateWebGLCapabilities(
  info: WebGLRendererInfo,
  compositionWidth: number,
  compositionHeight: number
): void;

/**
 * Baseline Chromium arguments shared between software and
 * hardware rendering modes. Exported for testing and for
 * PuppeteerBridge consumers that want to inspect the defaults.
 */
export const BASELINE_CHROMIUM_ARGS: readonly string[];

/**
 * Additional Chromium arguments applied in software rendering mode.
 * Exported for testing.
 */
export const SOFTWARE_RENDERING_ARGS: readonly string[];

/**
 * Additional Chromium arguments applied in hardware rendering mode.
 * Exported for testing.
 */
export const HARDWARE_RENDERING_ARGS: readonly string[];
```

## Design Decisions

### D1: Separate Module from PuppeteerBridge

**Decision:** OBJ-049 is a standalone utility module (`rendering-config.ts`), not a modification to OBJ-009's `PuppeteerBridge`. It produces configuration that the bridge consumes.

**Rationale:** OBJ-009 is verified. Modifying it would require re-verification. OBJ-009 already exposes `gpu: boolean` and `extraArgs: string[]` — OBJ-049's `resolveRenderingConfig()` produces values that map to these config options. The bridge remains a transport layer; OBJ-049 provides the domain knowledge about *which* flags to use and *why*.

**Integration pattern for OBJ-035 (orchestrator):**
```typescript
// Resolve rendering configuration
const renderConfig = resolveRenderingConfig(userRequestedMode);

// Create bridge with resolved config
const bridge = new PuppeteerBridge({
  width: 1920,
  height: 1080,
  gpu: renderConfig.resolvedMode === 'hardware',
  extraArgs: renderConfig.chromiumArgs,
});

await bridge.launch();

// Probe and validate WebGL after launch
const webglInfo = await probeWebGLRenderer(bridge);
validateWebGLCapabilities(webglInfo, 1920, 1080);
```

### D2: Three GPU Modes — software, hardware, auto

**Decision:** Three explicit modes rather than a simple boolean.

**Rationale:**
- `software` is the C-11 baseline. It must always work. Docker, CI/CD, VPS without GPU — this is the default.
- `hardware` is for environments where the operator knows a GPU is available (e.g., local development with a GPU, a GPU-provisioned cloud instance).
- `auto` is for heterogeneous environments (e.g., an n8n pipeline that may run on different machines). It requires a probe-and-fallback pattern.

OBJ-009's `gpu: boolean` maps directly: `software` → `gpu: false`, `hardware` → `gpu: true`. The `auto` mode is handled at the orchestrator level by first trying `hardware`, probing, and falling back to `software` if the probe detects a software renderer when hardware was expected. The fallback requires closing and re-launching the bridge.

### D3: `resolveRenderingConfig()` is Pure

**Decision:** The config resolver is a pure function — no I/O, no probing, no system calls. It takes a mode and returns the args.

**Rationale:** GPU detection requires a running browser (to probe WebGL capabilities) or unreliable system-level checks (parsing `lspci` or `nvidia-smi`, which are platform-specific and may not reflect what Chromium can actually use). The reliable detection path is: launch Chromium → probe WebGL → inspect renderer string. This two-phase approach (resolve args → launch → probe) is cleaner than a single function that does everything.

### D4: Baseline Chromium Arguments

**Decision:** Baseline args shared by all modes:

```
--disable-dev-shm-usage         # Docker: /tmp instead of /dev/shm (prevents OOM)
--no-sandbox                    # Docker: required when running as root
--disable-setuid-sandbox        # Docker: companion to --no-sandbox
--hide-scrollbars               # Prevent scrollbar artifacts in viewport capture
--mute-audio                    # No browser audio output
--allow-file-access-from-files  # Enable file:// texture loading (OBJ-009 D10)
--disable-background-timer-throttling  # Prevent background tab throttling
--disable-renderer-backgrounding       # Prevent renderer deprioritization
--disable-backgrounding-occluded-windows
```

These are carried over from OBJ-009's D8 with the addition of three throttling-prevention flags. The throttling flags are important because Puppeteer may consider the page a "background" context in headless mode, which could throttle JavaScript execution and introduce non-deterministic timing — violating C-03 (virtualized clock determinism).

**Software-specific args:**
```
--disable-gpu                   # Force software WebGL via SwiftShader
--disable-gpu-compositing       # Disable GPU-based compositing
--use-gl=swiftshader            # Explicitly select SwiftShader GL backend
```

**Hardware-specific args:**
```
--enable-gpu-rasterization      # Use GPU for rasterization
--enable-zero-copy              # Zero-copy GPU memory for textures
--ignore-gpu-blocklist          # Allow GPUs that Chromium has blocklisted
```

### D5: Probe via Temporary Canvas

**Decision:** `probeWebGLRenderer()` creates a temporary `<canvas>` in the page, obtains a WebGL context, reads the debug info, then removes the canvas. It does NOT use the `#depthkit-canvas` or the Three.js renderer.

**Rationale:** The probe may run before OBJ-011's `init()` creates the Three.js renderer. Using a temporary canvas avoids coupling to the renderer lifecycle and prevents any interference with the depthkit rendering context (e.g., context limits — some platforms allow only a small number of simultaneous WebGL contexts).

### D6: Software Renderer Detection Heuristic

**Decision:** `isSoftwareRenderer` is determined by checking if the `WEBGL_debug_renderer_info` renderer string contains any of: `"SwiftShader"`, `"llvmpipe"`, `"Mesa"` (without "NVIDIA"/"AMD"/"Intel" qualifier suggesting hardware Mesa), or `"Software"`. The check is case-insensitive.

**Rationale:** SwiftShader is Chromium's built-in software renderer and is the most common case. `llvmpipe` is Mesa's software rasterizer (encountered on some Linux systems). The heuristic is intentionally conservative — if the renderer string is unrecognized, `isSoftwareRenderer` defaults to `false`. False negatives (hardware misidentified as unknown) are harmless; false positives (software misidentified as hardware) would be problematic for the `auto` mode's fallback logic but are unlikely given the known software renderer strings.

**The `WEBGL_debug_renderer_info` extension** is universally available in Chromium. If unavailable (e.g., privacy-restricted browser profile), `renderer` and `vendor` are `null`, and `isSoftwareRenderer` defaults to `false` (unknown, treated as hardware).

### D7: Validation Against Composition Dimensions

**Decision:** `validateWebGLCapabilities()` checks that `maxViewportDims` and `maxTextureSize` accommodate the composition's viewport dimensions. It does NOT check individual texture files' dimensions (those are unknown at config time).

**Rationale:** SwiftShader's `MAX_TEXTURE_SIZE` is typically 8192, which accommodates all standard video resolutions (1920×1080, 3840×2160). The viewport check catches pathological cases early (e.g., attempting 8K rendering on a backend that maxes out at 4096). Individual texture oversizing is handled at texture load time by OBJ-015.

### D8: `auto` Mode — Orchestrator-Level Fallback

**Decision:** The `auto` mode does NOT internally launch two browsers. Instead, `resolveRenderingConfig('auto')` returns hardware-attempt args (with `resolvedMode: 'hardware'`). After launch, the orchestrator probes WebGL. If `webglInfo.isSoftwareRenderer === true` and the orchestrator expected hardware (because it's in `auto` mode), the orchestrator closes the bridge, calls `resolveRenderingConfig('software')`, and re-launches. This keeps the launch/close lifecycle firmly in OBJ-035's control.

**Rationale:** OBJ-049 is a configuration utility, not a lifecycle manager. Having it spawn and close browsers would violate the separation of concerns established by OBJ-009 and OBJ-035. The orchestrator owns the bridge lifecycle; OBJ-049 provides the decision logic.

**Auto-mode orchestrator pattern (for OBJ-035):**
```
1. resolveRenderingConfig('auto') → hardware args
2. Launch bridge with hardware args
3. probeWebGLRenderer(bridge) → info
4. If info.isSoftwareRenderer is true:
   a. Log: "GPU not available, falling back to software rendering"
   b. bridge.close()
   c. resolveRenderingConfig('software') → software args
   d. Re-launch bridge with software args
   e. probeWebGLRenderer(bridge) → re-validate
5. validateWebGLCapabilities(info, width, height)
6. Log resolved mode and renderer info
7. Proceed with rendering
```

### D9: Relationship to OBJ-009's `gpu` Flag

**Decision:** OBJ-049 does NOT replace OBJ-009's `gpu: boolean` config. Instead, it complements it. The orchestrator (OBJ-035) uses OBJ-049 to *decide* the gpu value and *augment* the args:

| OBJ-049 resolvedMode | OBJ-009 `gpu` | OBJ-009 `extraArgs` |
|---|---|---|
| `'software'` | `false` | `SOFTWARE_RENDERING_ARGS` (minus `--disable-gpu` which OBJ-009 already adds when `gpu: false`) |
| `'hardware'` | `true` | `HARDWARE_RENDERING_ARGS` |

**De-duplication concern:** OBJ-009 adds `--disable-gpu` when `gpu: false`. OBJ-049's `SOFTWARE_RENDERING_ARGS` includes `--disable-gpu-compositing` and `--use-gl=swiftshader` but NOT `--disable-gpu` (to avoid duplication). The `chromiumArgs` returned by `resolveRenderingConfig()` includes ALL args (baseline + mode-specific), and the orchestrator can either:
- Pass the full `chromiumArgs` via `extraArgs` and set `gpu: true` (to prevent OBJ-009 from adding its own `--disable-gpu`), OR
- Use `gpu: false/true` as the primary switch and pass only the *additional* mode-specific args via `extraArgs`.

The spec recommends the second approach: use OBJ-009's `gpu` flag for the primary `--disable-gpu` control, and pass the remaining mode-specific args via `extraArgs`. The `chromiumArgs` export is still useful for inspection and testing.

## Acceptance Criteria

### Configuration Resolution

- [ ] **AC-01:** `resolveRenderingConfig('software')` returns `resolvedMode: 'software'`, `requestedMode: 'software'`, `gpuDetected: null`, and `chromiumArgs` containing `'--disable-gpu'`, `'--disable-gpu-compositing'`, `'--use-gl=swiftshader'`, `'--no-sandbox'`, `'--disable-dev-shm-usage'`.
- [ ] **AC-02:** `resolveRenderingConfig('hardware')` returns `resolvedMode: 'hardware'`, `requestedMode: 'hardware'`, `gpuDetected: null`, and `chromiumArgs` containing `'--ignore-gpu-blocklist'` and NOT containing `'--disable-gpu'`.
- [ ] **AC-03:** `resolveRenderingConfig('auto')` returns `resolvedMode: 'hardware'` (initial attempt), `requestedMode: 'auto'`, and `chromiumArgs` identical to the `'hardware'` resolution.
- [ ] **AC-04:** `BASELINE_CHROMIUM_ARGS` is a frozen readonly array. `SOFTWARE_RENDERING_ARGS` and `HARDWARE_RENDERING_ARGS` are frozen readonly arrays.
- [ ] **AC-05:** `resolveRenderingConfig()` is a pure function — calling it twice with the same argument returns deeply equal results.

### WebGL Probing

- [ ] **AC-06:** After launching a PuppeteerBridge with `gpu: false`, `probeWebGLRenderer(bridge)` returns a `WebGLRendererInfo` with `isSoftwareRenderer: true`, `renderer` containing `"SwiftShader"`, `version` containing `"WebGL"`, `maxTextureSize` >= 4096, and `maxViewportDims` each >= 1920.
- [ ] **AC-07:** `probeWebGLRenderer()` when bridge is not launched throws `Error` (not `WebGLValidationError`) with a message containing "not launched".
- [ ] **AC-08:** `probeWebGLRenderer()` does not interfere with the `#depthkit-canvas`. After probing, the Three.js renderer (if initialized via OBJ-011) still functions correctly. Verifiable by: launch bridge → probe → init page (OBJ-011) → render a frame → capture — the capture succeeds.
- [ ] **AC-09:** `WebGLRendererInfo.renderer` and `vendor` are populated strings (not null) when running in Chromium (which universally supports `WEBGL_debug_renderer_info`).

### WebGL Validation

- [ ] **AC-10:** `validateWebGLCapabilities(info, 1920, 1080)` does not throw when `maxViewportDims >= [1920, 1080]` and `maxTextureSize >= 1920`.
- [ ] **AC-11:** `validateWebGLCapabilities(info, 32000, 32000)` throws `WebGLValidationError` with code `'VIEWPORT_TOO_SMALL'` (because no WebGL backend supports 32000×32000 viewports).
- [ ] **AC-12:** `WebGLValidationError` instances have `code`, `message`, and optional `rendererInfo`. `error instanceof WebGLValidationError` is `true`. `error instanceof Error` is `true`.

### Software Rendering Correctness (C-11)

- [ ] **AC-13:** A PuppeteerBridge launched with software rendering config (`resolveRenderingConfig('software')`) can: initialize the Three.js page (OBJ-011), render a scene with a colored mesh, and produce a non-black frame capture (OBJ-012). This is the end-to-end C-11 validation.
- [ ] **AC-14:** The frame captured under software rendering is visually identical (same PNG bytes or pixel-level equivalent) to a frame captured under hardware rendering for the same scene. This validates C-05 (deterministic output) across rendering backends. Note: minor per-pixel differences due to floating point may exist — the test should allow a tolerance of ±1 per color channel per pixel across up to 0.1% of pixels.
- [ ] **AC-15:** `probeWebGLRenderer()` after software rendering launch returns `isSoftwareRenderer: true`.

### Error Handling

- [ ] **AC-16:** `WebGLValidationError` with each code (`NO_WEBGL`, `CONTEXT_LOST`, `VIEWPORT_TOO_SMALL`, `TEXTURE_TOO_SMALL`) can be constructed and has the correct `code` property.
- [ ] **AC-17:** If `probeWebGLRenderer()` fails to create a WebGL context (simulated by navigating the page to `about:blank` before probing), it throws `WebGLValidationError` with code `'NO_WEBGL'`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `resolveRenderingConfig()` called with invalid mode | TypeScript compile error (union type). No runtime check needed — the type system enforces valid modes. |
| `probeWebGLRenderer()` on a page with no WebGL support | Throws `WebGLValidationError` with code `'NO_WEBGL'`. Extremely unlikely in Chromium (SwiftShader always provides WebGL). |
| `probeWebGLRenderer()` when `WEBGL_debug_renderer_info` is unavailable | Returns `renderer: null`, `vendor: null`, `isSoftwareRenderer: false` (unknown defaults to not-software). `version` and capability values are still populated from standard WebGL API. |
| `validateWebGLCapabilities()` with viewport larger than `maxViewportDims` | Throws `WebGLValidationError` with code `'VIEWPORT_TOO_SMALL'`, message includes requested vs. available dimensions. |
| `validateWebGLCapabilities()` with texture larger than `maxTextureSize` | Throws `WebGLValidationError` with code `'TEXTURE_TOO_SMALL'`, message includes requested vs. available size. |
| Hardware mode in Docker without GPU passthrough | Browser launches (Chromium falls back to SwiftShader internally). `probeWebGLRenderer()` returns `isSoftwareRenderer: true`. The orchestrator (if using `auto` mode) detects this and re-launches with software args. If using `hardware` mode explicitly, rendering still works (SwiftShader fallback) but without the GPU-specific optimization flags. |
| `auto` mode on a machine with a GPU | First launch with hardware args succeeds. `probeWebGLRenderer()` returns `isSoftwareRenderer: false`. No fallback needed. Rendering proceeds with GPU acceleration. |
| `auto` mode on a machine without a GPU | First launch with hardware args — Chromium falls back to SwiftShader. `probeWebGLRenderer()` returns `isSoftwareRenderer: true`. Orchestrator closes bridge, re-launches with software args. Second probe confirms software renderer. |
| Multiple calls to `probeWebGLRenderer()` on same bridge | Safe. Each call creates and destroys a temporary canvas. No state accumulation. |
| `probeWebGLRenderer()` after WebGL context loss on the depthkit canvas | The probe uses its own temporary canvas. Context loss on `#depthkit-canvas` does not affect the probe's ability to create a new context (context loss is per-context, not per-page, unless system-wide GPU reset occurs). |
| SwiftShader `maxTextureSize` vs. composition dimensions | SwiftShader's typical `MAX_TEXTURE_SIZE` is 8192 and `MAX_VIEWPORT_DIMS` is [8192, 8192]. This accommodates 4K (3840×2160) but not 8K. The validation function catches this. |

## Test Strategy

### Unit Tests: `test/unit/rendering-config.test.ts`

1. **`resolveRenderingConfig('software')`:** Returns correct `resolvedMode`, `requestedMode`, `gpuDetected`, and `chromiumArgs` containing software-specific flags.
2. **`resolveRenderingConfig('hardware')`:** Returns correct fields, `chromiumArgs` containing hardware-specific flags, no `--disable-gpu`.
3. **`resolveRenderingConfig('auto')`:** Returns `resolvedMode: 'hardware'`, `requestedMode: 'auto'`, `chromiumArgs` matching hardware config.
4. **`BASELINE_CHROMIUM_ARGS` contents:** Contains all expected baseline flags (`--no-sandbox`, `--disable-dev-shm-usage`, etc.).
5. **Software/hardware arg exclusivity:** `SOFTWARE_RENDERING_ARGS` does not contain any hardware-only flags. `HARDWARE_RENDERING_ARGS` does not contain `--disable-gpu`.
6. **`resolveRenderingConfig` purity:** Two calls with same arg return deeply equal results.
7. **`WebGLValidationError` construction:** All error codes construct correctly, `instanceof` checks pass.
8. **`validateWebGLCapabilities` pass case:** Mock `WebGLRendererInfo` with `maxTextureSize: 8192`, `maxViewportDims: [8192, 8192]`. Validate against 1920×1080 — no throw.
9. **`validateWebGLCapabilities` viewport fail:** Mock info with `maxViewportDims: [1024, 1024]`. Validate against 1920×1080 — throws `VIEWPORT_TOO_SMALL`.
10. **`validateWebGLCapabilities` texture fail:** Mock info with `maxTextureSize: 1024`. Validate against 1920×1080 — throws `TEXTURE_TOO_SMALL`.
11. **`isSoftwareRenderer` detection:** Mock renderer strings: `"Google SwiftShader"` → true, `"ANGLE (NVIDIA GeForce RTX 3080)"` → false, `"Mesa/X.org llvmpipe"` → true, `null` → false, `""` → false.

### Integration Tests: `test/integration/rendering-config.test.ts`

These tests launch real headless Chromium. Use small viewports (320×240) for speed.

12. **Software rendering probe:** Launch bridge with `gpu: false`, probe → `isSoftwareRenderer: true`, `renderer` contains "SwiftShader".
13. **Software rendering captures correctly:** Launch with software config, init page (OBJ-011), render colored mesh, capture (OBJ-012) → non-black PNG. (C-11 end-to-end validation.)
14. **Probe does not interfere with rendering:** Launch → probe → init → render → capture succeeds.
15. **Probe on unlaunched bridge:** Throws Error with "not launched".
16. **Validation passes for standard viewport:** Probe real SwiftShader → validate against 1920×1080 → no throw.
17. **Validation fails for excessive viewport:** Probe real SwiftShader → validate against 32000×32000 → throws `VIEWPORT_TOO_SMALL`.
18. **Multiple probes are safe:** Probe 3 times sequentially on same bridge → all return consistent results.

### Performance Baseline

19. **Probe latency:** Time 10 sequential `probeWebGLRenderer()` calls. Log average. Expected: <100ms per probe. This is a one-time cost per render job, not per-frame.

### Docker/CI Validation (TC-11)

20. **Software rendering in Docker:** Run integration test 13 inside a Docker container with no GPU passthrough. The test must pass, confirming C-11 compliance.

### Relevant Testable Claims

- **TC-02** (render performance): Software vs. hardware rendering performance comparison is observable via OBJ-012's `CaptureStats` and OBJ-035's render timing. OBJ-049's probe reports which backend is active.
- **TC-06** (deterministic output): AC-14 validates cross-backend frame consistency.
- **TC-11** (Docker/software WebGL): Tests 12, 13, and 20 directly validate this claim.

## Integration Points

### Depends on

| Dependency | What OBJ-049 uses |
|---|---|
| **OBJ-012** (FrameCapture) | Used in integration tests to verify that frame capture produces correct output under software rendering. The `FrameCapture.capture()` method is the validation mechanism for C-11 — if capture produces a non-black, valid PNG under software WebGL, the rendering config is correct. |
| **OBJ-009** (PuppeteerBridge) — transitive via OBJ-012 | `probeWebGLRenderer()` accepts a `PuppeteerBridge` and calls `bridge.evaluate()` to run WebGL probing JavaScript in the page context. Uses `bridge.isLaunched` for pre-condition checks. `resolveRenderingConfig()` produces values that map to OBJ-009's `gpu` and `extraArgs` config options. |

### Consumed by

| Downstream | How it uses OBJ-049 |
|---|---|
| **OBJ-035** (Orchestrator) | Calls `resolveRenderingConfig()` to determine GPU mode and Chromium args. Passes result to PuppeteerBridge constructor. After launch, calls `probeWebGLRenderer()` and `validateWebGLCapabilities()`. Implements the `auto`-mode fallback pattern. Logs `WebGLRendererInfo` for debugging. |
| **OBJ-050** (Docker containerization) | Depends on OBJ-049's software rendering configuration being correct and validated. The Docker image uses `resolveRenderingConfig('software')` as the default. OBJ-050's acceptance tests exercise the full software rendering pipeline inside Docker. |
| **OBJ-074** (Performance benchmarking) | Uses `probeWebGLRenderer()` to report which rendering backend is active during benchmarks. Compares software vs. hardware rendering performance. |

### File Placement

```
depthkit/
  src/
    engine/
      rendering-config.ts       # NEW — resolveRenderingConfig(), probeWebGLRenderer(),
                                 #       validateWebGLCapabilities(), GpuMode,
                                 #       WebGLRendererInfo, ResolvedRenderingConfig,
                                 #       WebGLValidationError, arg constants
  test/
    unit/
      rendering-config.test.ts   # NEW — unit tests (pure function tests, no browser)
    integration/
      rendering-config.test.ts   # NEW — integration tests with Puppeteer
```

## Open Questions

### OQ-A: Should `probeWebGLRenderer()` also check WebGL extension availability?

Some Three.js features (e.g., anisotropic filtering, float textures) require specific WebGL extensions. SwiftShader supports most standard extensions but may lack some. Should the probe return a list of available extensions, and should the validator check for depthkit-required extensions? For V1, Three.js's `meshBasicMaterial` (used per seed Section 8.4) does not require any non-standard extensions, so this is likely unnecessary. Defer until a scene geometry requires an advanced material.

### OQ-B: Should the module export a convenience function that combines resolve + launch + probe + validate?

A `launchWithRendering(mode, bridgeConfig)` function that wraps the full pattern (resolve → create bridge → launch → probe → validate → optionally re-launch for auto mode) would simplify OBJ-035's implementation. However, it would own bridge lifecycle, violating the separation established in D1 and D3. Defer to OBJ-035's spec — if the orchestrator pattern becomes unwieldy, this can be reconsidered.

### OQ-C: Cross-backend determinism tolerance in AC-14

AC-14 allows ±1 per channel per pixel for up to 0.1% of pixels between software and hardware renders. This tolerance is a hunch — SwiftShader and hardware GPUs may produce larger differences for complex shading. For `meshBasicMaterial` (unlit, texture-only), differences should be minimal. If the tolerance is too tight, document the actual divergence and adjust. If cross-backend determinism is not achievable, restrict C-05 (deterministic output) to "same backend" rather than "any backend."

---

I believe this spec is complete and precise. It covers the three functions (resolve, probe, validate), the type contracts, the relationship to OBJ-009's existing `gpu` flag, the `auto`-mode orchestrator pattern, error handling, and test strategy. I'd like the challenger to verify and provide feedback.

---

## Round 2 — spec_challenger

I've read the proposed spec carefully. Let me examine the OBJ-009 spec more closely to verify the integration claims.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


Let me read the OBJ-009 spec more carefully to check the arg overlap issue.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": 130,
  "limit": 140
}
[Tool Result]    130→  executablePath?: string;
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
   146→  extraArgs?: string[];
   147→  /**
   148→   * Forward page console.log messages to Node's stdout.
   149→   * Default: false. When true, all page console output (log, warn,
   150→   * error, info) is forwarded to Node's console prefixed with
   151→   * '[depthkit:page]'. When false, only page crashes (uncaught
   152→   * exceptions) are surfaced — see pag... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": 300,
  "limit": 150
}
[Tool Result]    300→
   301→**Exception:** `launch()` loads the page and verifies `window.depthkit` is defined — this minimal check ensures the page shell (OBJ-010) loaded correctly, without coupling to its internal API.
   302→
   303→### D7: PNG-Only Capture via `page.screenshot()`
   304→
   305→**Decision:** `captureFrame()` returns PNG data exclusively, using Puppeteer's `page.screenshot({ type: 'png', encoding: 'binary' })`. There is no raw RGBA capture format.
   306→
   307→**Rationale:** `page.screenshot()` captures the **full composited viewport** — both the WebGL canvas and any HTML elements positioned above it. This is the correct behavior for future HUD layers (seed vocabulary), where titles/captions rendered as HTML/CSS must appear in the captured frame.
   308→
   309→Raw RGBA extraction was considered and deferred:
   310→- Extracting raw pixels from a WebGL canvas via `gl.readPixels()` requires transferring `width * height * 4` bytes through Puppeteer's serialization layer (JSON-en... [truncated]
Now I have the full picture of OBJ-009. Let me check the key details about its default args:

**OBJ-009 D8** defines these default args:
- `--disable-gpu` (only when `gpu: false`, the default)
- `--disable-dev-shm-usage`
- `--no-sandbox`
- `--disable-setuid-sandbox`
- `--hide-scrollbars`
- `--mute-audio`
- `--allow-file-access-from-files`

And OBJ-009 does NOT include: `--disable-background-timer-throttling`, `--disable-renderer-backgrounding`, `--disable-backgrounding-occluded-windows`, `--use-gl=swiftshader`, `--disable-gpu-compositing`, or any hardware-specific flags.

Now I have enough context to give a thorough review. Here are my findings:

---

## Challenge — Round 2

### Points of Agreement

The overall architecture is sound: a pure config resolver + post-launch probe + validator, without modifying the verified OBJ-009 module. The three-mode `GpuMode` enum, the `WebGLRendererInfo` type, and the validation function are well-designed abstractions. The separation from PuppeteerBridge lifecycle is correct.

### Issues

---

#### Issue 1 (Critical): AC-01 contradicts D9 — `--disable-gpu` in `chromiumArgs`

**AC-01** states: `chromiumArgs` containing `'--disable-gpu'`, `'--disable-gpu-compositing'`, `'--use-gl=swiftshader'`, `'--no-sandbox'`, `'--disable-dev-shm-usage'`.

**D9** states: `SOFTWARE_RENDERING_ARGS` does NOT include `--disable-gpu` (to avoid duplication with OBJ-009).

These directly contradict each other. If `SOFTWARE_RENDERING_ARGS` omits `--disable-gpu`, and `BASELINE_CHROMIUM_ARGS` must also omit it (since baseline is shared by both software and hardware modes), then `chromiumArgs` from `resolveRenderingConfig('software')` cannot contain `--disable-gpu`. But AC-01 says it does.

**Proposed fix:** Decide once whether `chromiumArgs` is the **complete** arg list (including `--disable-gpu`) or only the **supplementary** args (to be combined with OBJ-009's own defaults). Then make AC-01, D4, and D9 all consistent with that decision. I recommend `chromiumArgs` be the complete list (all args the orchestrator needs), and document that the orchestrator should NOT use OBJ-009's `gpu` flag at all — instead passing the complete `chromiumArgs` via `extraArgs` with `gpu: true` (to suppress OBJ-009's own `--disable-gpu` logic). This eliminates the de-duplication dance entirely.

---

#### Issue 2 (Critical): Arg duplication / overlap with OBJ-009's default args

OBJ-009 D8 already adds these args on every launch: `--disable-dev-shm-usage`, `--no-sandbox`, `--disable-setuid-sandbox`, `--hide-scrollbars`, `--mute-audio`, `--allow-file-access-from-files`. These are added by OBJ-009 internally, not via `extraArgs`.

OBJ-049's `BASELINE_CHROMIUM_ARGS` includes all of these PLUS three throttling-prevention flags. If the orchestrator passes OBJ-049's `chromiumArgs` via `extraArgs`, the common flags appear twice — once from OBJ-009's internals and once from `extraArgs`.

**Is arg duplication harmful?** Chromium generally tolerates duplicate args, but it's sloppy and confusing for debugging. More importantly, the spec doesn't document this overlap at all — an implementer would notice the duplication and wonder if it's a bug.

**Proposed fix:** Redefine what OBJ-049 returns:

- `BASELINE_CHROMIUM_ARGS` should contain ONLY the args that OBJ-009 does NOT already add: `--disable-background-timer-throttling`, `--disable-renderer-backgrounding`, `--disable-backgrounding-occluded-windows`. These are the OBJ-049 additions.
- `SOFTWARE_RENDERING_ARGS`: `--disable-gpu`, `--disable-gpu-compositing`, `--use-gl=swiftshader`.
- `HARDWARE_RENDERING_ARGS`: `--enable-gpu-rasterization`, `--enable-zero-copy`, `--ignore-gpu-blocklist`.
- `chromiumArgs` = `BASELINE_CHROMIUM_ARGS` + mode-specific args.

The orchestrator passes `chromiumArgs` via `extraArgs` (which OBJ-009 appends after its own defaults). For the `gpu` flag: set `gpu: true` always (to prevent OBJ-009 from adding its own `--disable-gpu`), and let OBJ-049's `SOFTWARE_RENDERING_ARGS` add `--disable-gpu` when needed.

Alternatively, rename `chromiumArgs` to `extraChromiumArgs` to make it crystal clear these supplement OBJ-009's defaults, not replace them.

---

#### Issue 3 (Major): `auto` mode re-launch is unjustified overhead

D8 describes the auto-mode fallback: launch with hardware args → probe → if SwiftShader detected → close → re-launch with software args.

But here's the thing: when Chromium can't access a GPU, it **already** falls back to SwiftShader internally. The browser is already rendering with SwiftShader. Re-launching with `--disable-gpu` and `--use-gl=swiftshader` just restarts the browser to use... the same SwiftShader backend it was already using. The only practical difference is a few optimization flags (`--disable-gpu-compositing`).

The spec doesn't justify **why** the re-launch is necessary. Is there a measurable difference in SwiftShader performance or correctness when `--use-gl=swiftshader` is explicit vs. when Chromium falls back to it implicitly? If not, the re-launch is pure waste (adds 2-5 seconds of browser startup latency).

**Proposed fix:** One of:
1. **Justify the re-launch:** Document specifically what `--use-gl=swiftshader` and `--disable-gpu-compositing` do that Chromium's implicit fallback doesn't. If there's a correctness or performance reason, state it.
2. **Simplify auto mode:** If the implicit fallback is equivalent, change auto-mode to: launch with hardware args → probe → log the result → continue. No re-launch. The orchestrator just records which backend it got.
3. **Make re-launch optional:** Add a `fallbackRelaunch?: boolean` to the config. Default `false` (just log). Set `true` if the operator wants the explicit software flags for reproducibility.

---

#### Issue 4 (Major): AC-14 cross-backend determinism is untestable in most environments

AC-14: "The frame captured under software rendering is visually identical... to a frame captured under hardware rendering for the same scene."

This requires both a GPU and SwiftShader to be available in the test environment. CI/CD pipelines (GitHub Actions, Docker) typically have no GPU. Developer machines have GPUs but may not have the same GPU. The test is environment-dependent and non-reproducible.

Furthermore, cross-backend determinism is a C-05 aspiration, not a C-11 requirement. C-11 says "render correctly using software WebGL." It says nothing about matching hardware output.

**Proposed fix:** Demote AC-14 from an acceptance criterion to an open question (OQ-C already covers this). Replace it with a simpler criterion: "A frame rendered under software rendering matches a second render of the same frame under software rendering (same-backend determinism)." This is testable everywhere and directly validates C-05 + C-11.

---

#### Issue 5 (Minor): `isSoftwareRenderer` detection heuristic for Mesa is too broad

D6 says check for `"Mesa"` (without "NVIDIA"/"AMD"/"Intel" qualifier). But Mesa is also the userspace driver stack for hardware-accelerated rendering on Linux (Mesa with Radeon, Mesa with Intel iris, etc.). The renderer string for hardware Mesa often looks like: `"Mesa Intel(R) UHD Graphics 630"` or `"AMD RADV NAVI10 (ACO)"`. Checking for `"Mesa"` alone would incorrectly flag these as software renderers.

**Proposed fix:** Change the Mesa detection to check for `"llvmpipe"` or `"softpipe"` specifically (Mesa's actual software rasterizers), NOT the generic `"Mesa"` string. The current spec already lists `"llvmpipe"` — just remove `"Mesa"` from the heuristic.

---

#### Issue 6 (Minor): `TEXTURE_TOO_SMALL` validation is misleading

`validateWebGLCapabilities()` checks `maxTextureSize >= max(compositionWidth, compositionHeight)`. But textures can be arbitrarily sized — a 4096×4096 texture is common for sky backgrounds even on a 1920×1080 viewport. The validation passes for the viewport but the actual texture load fails later.

The spec acknowledges this in D7 ("texture dimensions are unknown at config time") but still includes `TEXTURE_TOO_SMALL` as an error code, creating the impression that texture sizing is validated.

**Proposed fix:** Either:
1. Remove `TEXTURE_TOO_SMALL` from the error codes and only validate viewport dimensions, OR
2. Keep the error code but rename the function parameter to make it clear: `validateWebGLCapabilities(info, viewportWidth, viewportHeight)` and document in the JSDoc that this does NOT validate individual texture sizes — those are validated at texture load time by OBJ-015.

I'd go with option 2 since the current function signature already uses "compositionWidth/Height" — just make the doc comment explicit that texture validation is out of scope.

---

#### Issue 7 (Minor): No mention of `--headless=new` vs `--headless`

Puppeteer's newer versions use `--headless=new` (Chrome's new headless mode) by default, which has different WebGL behavior than the old `--headless` mode. The spec doesn't mention which headless mode is expected or how it affects software rendering.

**Proposed fix:** Add a note in D4 (or as an OQ) about headless mode selection. OBJ-009 already has a `headless?: boolean` config — OBJ-049 should note that the rendering config args are tested with Puppeteer's default headless mode and that `headless: 'shell'` (old mode) may have different SwiftShader behavior.

---

#### Issue 8 (Minor): Missing acceptance criterion for the throttling-prevention flags

D4 adds three throttling-prevention flags (`--disable-background-timer-throttling`, `--disable-renderer-backgrounding`, `--disable-backgrounding-occluded-windows`) but no AC validates that they are present in the args. These are arguably the most important contribution of OBJ-049 beyond what OBJ-009 already does — they directly affect C-03 (deterministic timing).

**Proposed fix:** Add an AC that validates these three flags appear in both software and hardware `chromiumArgs`.

---

### Summary

| # | Severity | Issue |
|---|---|---|
| 1 | Critical | AC-01 contradicts D9 on `--disable-gpu` in `chromiumArgs` |
| 2 | Critical | Arg overlap/duplication with OBJ-009's internal defaults is unspecified |
| 3 | Major | Auto-mode re-launch is unjustified — Chromium already falls back to SwiftShader |
| 4 | Major | AC-14 cross-backend determinism is untestable in most CI environments |
| 5 | Minor | Mesa detection heuristic is too broad — will false-positive on hardware Mesa |
| 6 | Minor | `TEXTURE_TOO_SMALL` validation gives false sense of security |
| 7 | Minor | No headless mode consideration |
| 8 | Minor | No AC for throttling-prevention flags |

Please address the two critical and two major issues. I'm happy to converge once those are resolved with the minor issues either fixed or documented as OQs.

---

## Round 3 — spec_author

Excellent critique. All eight issues are valid. Here's my revised specification addressing each:

---

# Specification: OBJ-049 — Software Rendering Configuration

## Summary

OBJ-049 delivers the `rendering-config` module (`src/engine/rendering-config.ts`) — a utility that resolves the correct *supplementary* Chromium launch arguments for software or hardware-accelerated WebGL rendering, probes the active WebGL backend after launch, and validates that the backend meets depthkit's minimum requirements. This module enforces C-11 (engine must render correctly with software WebGL / SwiftShader, without GPU passthrough) while providing an opt-in path to GPU acceleration when available. It does not own the Puppeteer lifecycle — it produces configuration that `PuppeteerBridge` (OBJ-009) consumes via its existing `gpu` and `extraArgs` config, and provides post-launch validation that `FrameCapture` (OBJ-012) and the orchestrator (OBJ-035) use to confirm rendering correctness.

## Interface Contract

### Module: `src/engine/rendering-config.ts`

```typescript
import type { PuppeteerBridge } from './puppeteer-bridge.js';

/**
 * GPU rendering mode for the engine.
 *
 * - 'software': Force software rendering via SwiftShader/ANGLE.
 *   OBJ-009's gpu:false handles --disable-gpu. OBJ-049 adds
 *   supplementary flags (--use-gl=swiftshader, --disable-gpu-compositing).
 *   Guaranteed to work in Docker/CI without GPU passthrough.
 *   This is the C-11 baseline.
 *
 * - 'hardware': Request hardware GPU acceleration. OBJ-009's
 *   gpu:true omits --disable-gpu. OBJ-049 adds optimization
 *   flags (--enable-gpu-rasterization, etc.). Requires GPU
 *   drivers and (in Docker) GPU passthrough.
 *
 * - 'auto': Launch with hardware flags, probe WebGL. If the
 *   probe detects a software renderer, log the result and
 *   continue — Chromium's implicit SwiftShader fallback is
 *   functionally equivalent. No re-launch. The orchestrator
 *   records which backend it got for logging/diagnostics.
 */
export type GpuMode = 'software' | 'hardware' | 'auto';

/**
 * Information about the active WebGL rendering backend,
 * obtained by probing the launched browser's WebGL context.
 */
export interface WebGLRendererInfo {
  /** The WebGL renderer string from WEBGL_debug_renderer_info.
   *  e.g., "Google SwiftShader", "ANGLE (NVIDIA GeForce RTX 3080 ...)"
   *  null if the extension is unavailable. */
  renderer: string | null;

  /** The WebGL vendor string from WEBGL_debug_renderer_info.
   *  e.g., "Google Inc. (Google)", "Google Inc. (NVIDIA)"
   *  null if the extension is unavailable. */
  vendor: string | null;

  /** WebGL version string from gl.getParameter(gl.VERSION).
   *  e.g., "WebGL 2.0 (OpenGL ES 3.0 SwiftShader 5.0.0)" */
  version: string;

  /** Whether the renderer appears to be software-based.
   *  Detected by checking if the renderer string contains
   *  "SwiftShader", "llvmpipe", or "softpipe" (case-insensitive).
   *  Returns false if renderer is null or unrecognized. */
  isSoftwareRenderer: boolean;

  /** Maximum texture size supported (gl.MAX_TEXTURE_SIZE).
   *  Typically 4096-16384 for hardware, 8192 for SwiftShader. */
  maxTextureSize: number;

  /** Maximum viewport dimensions (gl.MAX_VIEWPORT_DIMS).
   *  Array of [maxWidth, maxHeight]. */
  maxViewportDims: [number, number];
}

/**
 * Result of resolving the GPU mode, including the supplementary
 * Chromium launch arguments that OBJ-009 does NOT already provide.
 */
export interface ResolvedRenderingConfig {
  /** The resolved GPU mode. For 'auto', this is 'hardware'
   *  (initial attempt — actual backend is determined post-launch
   *  via probeWebGLRenderer). */
  resolvedMode: 'software' | 'hardware';

  /** The requested GPU mode (what the caller asked for). */
  requestedMode: GpuMode;

  /** The value to pass to PuppeteerBridge's `gpu` config option.
   *  'software' → false, 'hardware'/'auto' → true. */
  bridgeGpu: boolean;

  /** Supplementary Chromium args to pass to PuppeteerBridge's
   *  `extraArgs` config. These ONLY contain args that OBJ-009
   *  does NOT already add. OBJ-009's internal defaults
   *  (--no-sandbox, --disable-dev-shm-usage, etc.) and
   *  gpu-flag logic (--disable-gpu when gpu:false) are NOT
   *  duplicated here.
   *
   *  For 'software': EXTRA_SOFTWARE_ARGS
   *    (--use-gl=swiftshader, --disable-gpu-compositing)
   *  For 'hardware'/'auto': EXTRA_HARDWARE_ARGS
   *    (--enable-gpu-rasterization, --enable-zero-copy,
   *     --ignore-gpu-blocklist)
   *  Both modes also include EXTRA_BASELINE_ARGS
   *    (throttling-prevention flags).
   */
  extraArgs: string[];

  /** Whether GPU was detected as available. null until
   *  probeWebGLRenderer() is called post-launch. This field
   *  is NOT populated by resolveRenderingConfig() — it is
   *  set by the orchestrator after probing. Present in the
   *  type for the orchestrator to populate and log. */
  gpuDetected: boolean | null;
}

/**
 * Error thrown when WebGL validation fails after launch.
 */
export class WebGLValidationError extends Error {
  readonly code: WebGLValidationErrorCode;
  readonly rendererInfo?: WebGLRendererInfo;

  constructor(
    code: WebGLValidationErrorCode,
    message: string,
    rendererInfo?: WebGLRendererInfo
  );
}

export type WebGLValidationErrorCode =
  | 'NO_WEBGL'            // WebGL context could not be created
  | 'CONTEXT_LOST'        // WebGL context was created but is lost
  | 'VIEWPORT_TOO_SMALL'  // maxViewportDims < requested viewport size
  ;

/**
 * Resolve the supplementary Chromium args and bridge config
 * for a given GPU mode. Pure function — no I/O.
 *
 * Returns the `bridgeGpu` flag and `extraArgs` to pass to
 * PuppeteerBridge's constructor. Does NOT duplicate args that
 * OBJ-009 already adds internally.
 */
export function resolveRenderingConfig(mode: GpuMode): ResolvedRenderingConfig;

/**
 * Probe the WebGL rendering backend of a launched PuppeteerBridge.
 *
 * Creates a temporary <canvas> in the page, obtains a WebGL context
 * (tries WebGL2 first, falls back to WebGL1), queries debug info,
 * then removes the canvas. Does NOT interfere with #depthkit-canvas
 * or the Three.js renderer.
 *
 * @param bridge - A launched PuppeteerBridge instance.
 * @throws Error if bridge is not launched.
 * @throws WebGLValidationError with code 'NO_WEBGL' if no WebGL
 *         context can be created.
 */
export function probeWebGLRenderer(
  bridge: PuppeteerBridge
): Promise<WebGLRendererInfo>;

/**
 * Validate that the WebGL backend meets depthkit's minimum
 * requirements for a given viewport size.
 *
 * Checks:
 * 1. maxViewportDims >= [viewportWidth, viewportHeight].
 *
 * This does NOT validate individual texture dimensions — those
 * are unknown at config time and are validated at texture load
 * time by OBJ-015. The viewportWidth/Height parameters refer
 * to the composition's output dimensions (e.g., 1920x1080),
 * not texture sizes.
 *
 * @throws WebGLValidationError with code 'VIEWPORT_TOO_SMALL'
 *         if maxViewportDims is insufficient.
 */
export function validateWebGLCapabilities(
  info: WebGLRendererInfo,
  viewportWidth: number,
  viewportHeight: number
): void;

/**
 * Supplementary baseline args that OBJ-009 does NOT add.
 * These prevent Chromium from throttling background pages,
 * which is critical for C-03 (deterministic virtualized timing).
 * Included in both software and hardware modes.
 */
export const EXTRA_BASELINE_ARGS: readonly string[];

/**
 * Supplementary software-rendering args that OBJ-009 does NOT add.
 * OBJ-009 already adds --disable-gpu when gpu:false.
 * These add explicit SwiftShader selection and compositing control.
 */
export const EXTRA_SOFTWARE_ARGS: readonly string[];

/**
 * Supplementary hardware-rendering args for GPU optimization.
 */
export const EXTRA_HARDWARE_ARGS: readonly string[];
```

## Design Decisions

### D1: Separate Module from PuppeteerBridge

**Decision:** OBJ-049 is a standalone utility module (`rendering-config.ts`), not a modification to OBJ-009's `PuppeteerBridge`.

**Rationale:** OBJ-009 is verified. Modifying it would require re-verification. OBJ-009 already exposes `gpu: boolean` and `extraArgs: string[]` — OBJ-049 produces values that map directly to these config options. The bridge remains a transport layer; OBJ-049 provides the domain knowledge about *which supplementary flags* to use and *why*.

### D2: Supplementary Args Only — No Duplication with OBJ-009

**Decision:** OBJ-049's exported arg constants (`EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, `EXTRA_HARDWARE_ARGS`) contain ONLY args that OBJ-009 does NOT already add internally. The `extraArgs` field in `ResolvedRenderingConfig` is passed directly to `PuppeteerBridge({ extraArgs })`.

**OBJ-009's internal args (NOT duplicated):**
- `--disable-dev-shm-usage`
- `--no-sandbox`
- `--disable-setuid-sandbox`
- `--hide-scrollbars`
- `--mute-audio`
- `--allow-file-access-from-files`
- `--disable-gpu` (added by OBJ-009 when `gpu: false`)

**OBJ-049's `EXTRA_BASELINE_ARGS` (new, added to both modes):**
```
--disable-background-timer-throttling
--disable-renderer-backgrounding
--disable-backgrounding-occluded-windows
```
These prevent Chromium from throttling the headless page's JavaScript execution, which would introduce non-deterministic timing — violating C-03.

**OBJ-049's `EXTRA_SOFTWARE_ARGS`:**
```
--use-gl=swiftshader            # Explicitly select SwiftShader GL backend
--disable-gpu-compositing       # Disable GPU-based compositing
```
Note: `--disable-gpu` is NOT here — OBJ-009 adds it when `gpu: false`.

**OBJ-049's `EXTRA_HARDWARE_ARGS`:**
```
--enable-gpu-rasterization      # Use GPU for rasterization
--enable-zero-copy              # Zero-copy GPU memory for textures
--ignore-gpu-blocklist          # Allow GPUs that Chromium has blocklisted
```

**Integration pattern for OBJ-035:**
```typescript
const config = resolveRenderingConfig('software');
const bridge = new PuppeteerBridge({
  width: 1920,
  height: 1080,
  gpu: config.bridgeGpu,        // false for software
  extraArgs: config.extraArgs,  // EXTRA_BASELINE_ARGS + EXTRA_SOFTWARE_ARGS
});
```

### D3: Three GPU Modes — software, hardware, auto

**Decision:** Three explicit modes rather than a simple boolean.

**Rationale:**
- `software` is the C-11 baseline. Always works. Docker, CI/CD, VPS without GPU. This is the default.
- `hardware` is for environments where the operator knows a GPU is available.
- `auto` attempts hardware, then probes to discover what it actually got. See D4.

**Mapping to OBJ-009's `gpu: boolean`:**
| GpuMode | `bridgeGpu` | OBJ-009 behavior |
|---|---|---|
| `'software'` | `false` | OBJ-009 adds `--disable-gpu` |
| `'hardware'` | `true` | OBJ-009 omits `--disable-gpu` |
| `'auto'` | `true` | OBJ-009 omits `--disable-gpu` (let Chromium try hardware, fall back internally) |

### D4: `auto` Mode — Probe and Log, No Re-Launch

**Decision:** In `auto` mode, the orchestrator launches with hardware flags, probes WebGL, and **logs the result without re-launching**. If Chromium fell back to SwiftShader internally, rendering proceeds on SwiftShader.

**Rationale:** When Chromium can't access a GPU, it automatically falls back to SwiftShader. The browser is already rendering with SwiftShader — re-launching with explicit `--disable-gpu` and `--use-gl=swiftshader` restarts the browser to arrive at the same backend. The supplementary software args (`--disable-gpu-compositing`, `--use-gl=swiftshader`) provide marginally cleaner initialization but do not change the rendering backend or correctness. The 2-5 second re-launch cost is not justified by this marginal benefit.

**Auto-mode orchestrator pattern (for OBJ-035):**
```
1. resolveRenderingConfig('auto') → { bridgeGpu: true, extraArgs: [...hardware + baseline] }
2. Launch bridge
3. probeWebGLRenderer(bridge) → info
4. If info.isSoftwareRenderer:
   Log: "GPU not available; rendering with SwiftShader (software)"
5. Else:
   Log: "GPU available; rendering with hardware acceleration ({info.renderer})"
6. validateWebGLCapabilities(info, width, height)
7. Proceed with rendering
```

No re-launch. No bridge lifecycle management in OBJ-049.

**When explicit software mode matters:** If the operator wants guaranteed reproducibility of the software rendering path (e.g., for CI/CD where deterministic args are desired regardless of host GPU), they should use `'software'` explicitly, not `'auto'`.

### D5: `resolveRenderingConfig()` is Pure

**Decision:** The config resolver is a pure function — no I/O, no probing, no system calls.

**Rationale:** Reliable GPU detection requires a running browser. System-level checks (`lspci`, `nvidia-smi`) are platform-specific and may not reflect what Chromium can actually use. The two-phase approach (resolve args → launch → probe) is cleaner.

### D6: Probe via Temporary Canvas

**Decision:** `probeWebGLRenderer()` creates a temporary `<canvas>` in the page, obtains a WebGL context, reads the debug info, then removes the canvas. It does NOT use `#depthkit-canvas` or the Three.js renderer.

**Rationale:** The probe may run before OBJ-011's `init()` creates the Three.js renderer. A temporary canvas avoids coupling to the renderer lifecycle and prevents interference (e.g., WebGL context limits).

### D7: Software Renderer Detection Heuristic

**Decision:** `isSoftwareRenderer` checks if the `WEBGL_debug_renderer_info` renderer string contains (case-insensitive) any of:
- `"SwiftShader"` — Chromium's built-in software renderer
- `"llvmpipe"` — Mesa's software rasterizer
- `"softpipe"` — Mesa's reference software rasterizer

Returns `false` if renderer is `null` or unrecognized.

**Rationale:** The generic `"Mesa"` string is NOT checked because Mesa is also the userspace driver stack for hardware-accelerated rendering on Linux (e.g., `"Mesa Intel(R) UHD Graphics 630"`, `"AMD RADV NAVI10"`). Checking for `"Mesa"` would false-positive on hardware Mesa. The specific software rasterizer names (`llvmpipe`, `softpipe`) are unambiguous.

**If `WEBGL_debug_renderer_info` is unavailable** (privacy-restricted profile): `renderer` and `vendor` are `null`, `isSoftwareRenderer` is `false` (unknown defaults to not-software). This is conservative — the worst case is that `auto` mode doesn't detect software rendering, which is harmless (rendering proceeds regardless).

### D8: Validation Scope — Viewport Only

**Decision:** `validateWebGLCapabilities()` checks only `maxViewportDims >= [viewportWidth, viewportHeight]`. It does NOT check `maxTextureSize` against texture dimensions (unknown at config time). The `TEXTURE_TOO_SMALL` error code is removed.

**Rationale:** Individual texture oversizing is handled at texture load time by OBJ-015. Validating `maxTextureSize` against the viewport dimensions would give a false sense of security — a 4096×4096 sky texture on a 1920×1080 viewport would pass the viewport check but fail the texture check. Better to not pretend we validate textures here and leave that to the appropriate module.

### D9: Headless Mode Compatibility

**Decision:** OBJ-049's args are tested with Puppeteer's default headless mode (which uses `--headless=new` in modern Puppeteer/Chrome). The spec does not prescribe a specific headless mode — OBJ-009 controls this via its `headless` config option.

**Rationale:** Chrome's new headless mode (`--headless=new`, default since Puppeteer v21 / Chrome 112) uses the same browser engine as headed mode, including full WebGL support. The old headless mode (`--headless=old` / `headless: 'shell'`) used a stripped-down rendering path with potentially different SwiftShader behavior. OBJ-009's `headless: true` maps to the new headless mode by default, which is the correct choice for depthkit. If an operator explicitly sets `headless: 'shell'` (old mode) via OBJ-009, OBJ-049's software rendering config is still expected to work — SwiftShader is available in both modes — but this combination is not a tested configuration. Documented as OQ-D.

## Acceptance Criteria

### Configuration Resolution

- [ ] **AC-01:** `resolveRenderingConfig('software')` returns `resolvedMode: 'software'`, `requestedMode: 'software'`, `bridgeGpu: false`, `gpuDetected: null`, and `extraArgs` containing `'--use-gl=swiftshader'`, `'--disable-gpu-compositing'`, `'--disable-background-timer-throttling'`, `'--disable-renderer-backgrounding'`, `'--disable-backgrounding-occluded-windows'`. `extraArgs` does NOT contain `'--disable-gpu'` (OBJ-009 handles that via `bridgeGpu: false`).
- [ ] **AC-02:** `resolveRenderingConfig('hardware')` returns `resolvedMode: 'hardware'`, `bridgeGpu: true`, and `extraArgs` containing `'--enable-gpu-rasterization'`, `'--ignore-gpu-blocklist'`, `'--disable-background-timer-throttling'`, `'--disable-renderer-backgrounding'`, `'--disable-backgrounding-occluded-windows'`. `extraArgs` does NOT contain `'--disable-gpu'`.
- [ ] **AC-03:** `resolveRenderingConfig('auto')` returns `resolvedMode: 'hardware'`, `requestedMode: 'auto'`, `bridgeGpu: true`, and `extraArgs` identical to the `'hardware'` resolution.
- [ ] **AC-04:** `EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, and `EXTRA_HARDWARE_ARGS` are frozen readonly arrays.
- [ ] **AC-05:** `resolveRenderingConfig()` is a pure function — calling it twice with the same argument returns deeply equal results.
- [ ] **AC-06:** The throttling-prevention flags (`--disable-background-timer-throttling`, `--disable-renderer-backgrounding`, `--disable-backgrounding-occluded-windows`) appear in `extraArgs` for ALL three modes (`software`, `hardware`, `auto`).

### WebGL Probing

- [ ] **AC-07:** After launching a PuppeteerBridge with `gpu: false`, `probeWebGLRenderer(bridge)` returns a `WebGLRendererInfo` with `isSoftwareRenderer: true`, `renderer` containing `"SwiftShader"`, `version` containing `"WebGL"`, `maxTextureSize >= 4096`, and `maxViewportDims` each `>= 1920`.
- [ ] **AC-08:** `probeWebGLRenderer()` when bridge is not launched throws `Error` (not `WebGLValidationError`) with a message containing "not launched".
- [ ] **AC-09:** `probeWebGLRenderer()` does not interfere with `#depthkit-canvas`. After probing, the Three.js renderer (if initialized via OBJ-011) still functions correctly. Verifiable by: launch bridge → probe → init page (OBJ-011) → render a frame → capture — capture succeeds.
- [ ] **AC-10:** `WebGLRendererInfo.renderer` and `vendor` are populated strings (not null) when running in standard headless Chromium.

### isSoftwareRenderer Detection

- [ ] **AC-11:** Renderer string `"Google SwiftShader"` → `isSoftwareRenderer: true`.
- [ ] **AC-12:** Renderer string `"ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 ...)"` → `isSoftwareRenderer: false`.
- [ ] **AC-13:** Renderer string containing `"llvmpipe"` → `isSoftwareRenderer: true`.
- [ ] **AC-14:** Renderer string `"Mesa Intel(R) UHD Graphics 630"` → `isSoftwareRenderer: false` (hardware Mesa).
- [ ] **AC-15:** Renderer string `null` → `isSoftwareRenderer: false`.

### WebGL Validation

- [ ] **AC-16:** `validateWebGLCapabilities(info, 1920, 1080)` does not throw when `maxViewportDims >= [1920, 1080]`.
- [ ] **AC-17:** `validateWebGLCapabilities(info, 32000, 32000)` throws `WebGLValidationError` with code `'VIEWPORT_TOO_SMALL'`.
- [ ] **AC-18:** `WebGLValidationError` instances have `code`, `message`, and optional `rendererInfo`. `error instanceof WebGLValidationError === true`. `error instanceof Error === true`.

### Software Rendering Correctness (C-11)

- [ ] **AC-19:** A PuppeteerBridge launched with software rendering config can: initialize the Three.js page (OBJ-011), render a scene with a colored mesh, and produce a non-black frame capture (OBJ-012). This is the end-to-end C-11 validation.
- [ ] **AC-20:** A frame rendered under software rendering, captured twice in sequence, produces identical PNG buffers (same-backend determinism, C-05 + C-11).
- [ ] **AC-21:** `probeWebGLRenderer()` after software rendering launch returns `isSoftwareRenderer: true`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `resolveRenderingConfig()` with invalid mode | TypeScript compile error (union type). No runtime check needed. |
| `probeWebGLRenderer()` on page with no WebGL support | Throws `WebGLValidationError` with code `'NO_WEBGL'`. Extremely unlikely in Chromium (SwiftShader always provides WebGL). |
| `probeWebGLRenderer()` when `WEBGL_debug_renderer_info` unavailable | Returns `renderer: null`, `vendor: null`, `isSoftwareRenderer: false`. `version` and capability values still populated from standard WebGL API. |
| `validateWebGLCapabilities()` with viewport > `maxViewportDims` | Throws `WebGLValidationError` with code `'VIEWPORT_TOO_SMALL'`, message includes requested vs. available dimensions. |
| Hardware mode in Docker without GPU passthrough | Browser launches, Chromium internally falls back to SwiftShader. `probeWebGLRenderer()` returns `isSoftwareRenderer: true`. Rendering works correctly — SwiftShader is a complete WebGL implementation. |
| `auto` mode on machine with GPU | Launch with hardware flags → probe → `isSoftwareRenderer: false` → log "hardware acceleration active" → proceed. |
| `auto` mode on machine without GPU | Launch with hardware flags → Chromium falls back to SwiftShader → probe → `isSoftwareRenderer: true` → log "software rendering active" → proceed (no re-launch). |
| Multiple `probeWebGLRenderer()` calls on same bridge | Safe. Each creates and destroys a temporary canvas. No state accumulation. |
| Probe after WebGL context loss on `#depthkit-canvas` | Probe uses its own temporary canvas. Context loss on depthkit canvas doesn't affect probe. |
| SwiftShader `maxViewportDims` vs. 4K composition | SwiftShader's typical `MAX_VIEWPORT_DIMS` is [8192, 8192], accommodating 4K (3840×2160). Validation catches attempts beyond this. |
| `extraArgs` passed to OBJ-009 with duplicate args | OBJ-049's `extraArgs` are designed to contain NO duplicates with OBJ-009's internal args. If a caller manually adds duplicates via their own `extraArgs`, Chromium tolerates them harmlessly. |

## Test Strategy

### Unit Tests: `test/unit/rendering-config.test.ts`

1. **`resolveRenderingConfig('software')`:** Returns correct `resolvedMode`, `bridgeGpu: false`, `extraArgs` containing `EXTRA_BASELINE_ARGS` + `EXTRA_SOFTWARE_ARGS` but NOT `--disable-gpu`.
2. **`resolveRenderingConfig('hardware')`:** Returns correct fields, `bridgeGpu: true`, `extraArgs` containing `EXTRA_BASELINE_ARGS` + `EXTRA_HARDWARE_ARGS`, no `--disable-gpu`.
3. **`resolveRenderingConfig('auto')`:** Returns `resolvedMode: 'hardware'`, `requestedMode: 'auto'`, `bridgeGpu: true`, `extraArgs` matching hardware config.
4. **Throttling flags in all modes:** All three modes include `--disable-background-timer-throttling`, `--disable-renderer-backgrounding`, `--disable-backgrounding-occluded-windows` in `extraArgs`.
5. **No OBJ-009 arg duplication:** None of `EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, `EXTRA_HARDWARE_ARGS` contain `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-setuid-sandbox`, `--hide-scrollbars`, `--mute-audio`, `--allow-file-access-from-files`, or `--disable-gpu`.
6. **Purity:** Two calls with same arg return deeply equal results.
7. **Arg arrays frozen:** `EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, `EXTRA_HARDWARE_ARGS` are frozen (Object.isFrozen).
8. **`WebGLValidationError` construction:** All error codes construct correctly, `instanceof` checks pass.
9. **`validateWebGLCapabilities` pass:** Mock info with `maxViewportDims: [8192, 8192]`, validate 1920×1080 — no throw.
10. **`validateWebGLCapabilities` viewport fail:** Mock info with `maxViewportDims: [1024, 1024]`, validate 1920×1080 — throws `VIEWPORT_TOO_SMALL`.
11. **`isSoftwareRenderer` detection cases:** `"Google SwiftShader"` → true, `"ANGLE (NVIDIA ...)"` → false, `"Mesa/X.org llvmpipe"` → true, `"softpipe"` → true, `"Mesa Intel(R) UHD Graphics 630"` → false, `null` → false, `""` → false.

### Integration Tests: `test/integration/rendering-config.test.ts`

Small viewports (320×240) for speed. All tests run with `gpu: false` (software rendering) by default.

12. **Software rendering probe:** Launch bridge with software config → probe → `isSoftwareRenderer: true`, renderer contains "SwiftShader".
13. **Software rendering end-to-end (C-11):** Launch with software config → init page (OBJ-011) → render colored mesh → capture (OBJ-012) → non-black PNG.
14. **Same-backend determinism (C-05):** Render same frame twice under software rendering → identical PNG buffers.
15. **Probe does not interfere:** Launch → probe → init → render → capture succeeds.
16. **Probe on unlaunched bridge:** Throws Error with "not launched".
17. **Viewport validation with real SwiftShader:** Probe real SwiftShader → validate 1920×1080 → no throw.
18. **Viewport validation failure:** Probe real SwiftShader → validate 32000×32000 → throws `VIEWPORT_TOO_SMALL`.
19. **Multiple probes safe:** Probe 3 times sequentially → all return consistent results.

### Performance Baseline

20. **Probe latency:** Time 10 sequential `probeWebGLRenderer()` calls, log average. Expected: <100ms per probe. One-time cost per render job.

### Docker/CI Validation (TC-11)

21. **Software rendering in Docker:** Run integration test 13 inside a Docker container with no GPU passthrough. Must pass, confirming C-11.

### Relevant Testable Claims

- **TC-02**: Software vs. hardware performance is observable via downstream modules' stats. OBJ-049's probe reports which backend is active.
- **TC-06**: Test 14 validates same-backend determinism.
- **TC-11**: Tests 12, 13, and 21 directly validate Docker/software WebGL.

## Integration Points

### Depends on

| Dependency | What OBJ-049 uses |
|---|---|
| **OBJ-012** (FrameCapture) | Used in integration tests to verify frame capture produces correct output under software rendering. `FrameCapture.capture()` is the validation mechanism for C-11. |
| **OBJ-009** (PuppeteerBridge) — transitive via OBJ-012 | `probeWebGLRenderer()` accepts a `PuppeteerBridge` and calls `bridge.evaluate()` for WebGL probing. Uses `bridge.isLaunched` for pre-condition checks. `resolveRenderingConfig()` produces `bridgeGpu` and `extraArgs` values that map to OBJ-009's `gpu` and `extraArgs` config. |

### Consumed by

| Downstream | How it uses OBJ-049 |
|---|---|
| **OBJ-035** (Orchestrator) | Calls `resolveRenderingConfig()` to determine bridge config. Passes `bridgeGpu` and `extraArgs` to PuppeteerBridge constructor. After launch, calls `probeWebGLRenderer()` and `validateWebGLCapabilities()`. Implements `auto`-mode probe-and-log pattern. Logs `WebGLRendererInfo` for diagnostics. |
| **OBJ-050** (Docker containerization) | Depends on OBJ-049's software rendering config being correct. Docker image uses `resolveRenderingConfig('software')` as default. OBJ-050's acceptance tests exercise the full software rendering pipeline inside Docker. |
| **OBJ-074** (Performance benchmarking) | Uses `probeWebGLRenderer()` to report active rendering backend during benchmarks. |

### File Placement

```
depthkit/
  src/
    engine/
      rendering-config.ts         # NEW — resolveRenderingConfig(), probeWebGLRenderer(),
                                   #       validateWebGLCapabilities(), GpuMode,
                                   #       WebGLRendererInfo, ResolvedRenderingConfig,
                                   #       WebGLValidationError, arg constants
  test/
    unit/
      rendering-config.test.ts     # NEW — unit tests (pure function tests, no browser)
    integration/
      rendering-config.test.ts     # NEW — integration tests with Puppeteer
```

## Open Questions

### OQ-A: Should `probeWebGLRenderer()` also check WebGL extension availability?

Some Three.js features require specific WebGL extensions. SwiftShader supports most standard extensions but may lack some. For V1, `meshBasicMaterial` doesn't require non-standard extensions. Defer until a scene geometry requires an advanced material.

### OQ-B: Should the module export a convenience function combining resolve + launch + probe + validate?

A `launchWithRendering(mode, bridgeConfig)` function would simplify OBJ-035 but would own bridge lifecycle, violating D1. Defer to OBJ-035's spec.

### OQ-C: Cross-backend determinism (software vs. hardware)

Software and hardware WebGL renderers may produce per-pixel differences due to floating-point implementation differences. For `meshBasicMaterial` (unlit, texture-only), differences should be minimal but non-zero. C-05 (deterministic output) should be scoped to "same rendering backend" rather than "any backend." Cross-backend visual equivalence is desirable but not guaranteed. If empirically tested and the divergence is measurable, document the tolerance.

### OQ-D: Old headless mode compatibility

Puppeteer's `headless: 'shell'` (old headless mode) uses a stripped-down rendering path. OBJ-049's software rendering config is expected to work in both modes, but only the new headless mode (`headless: true`, the default) is a tested configuration. If old headless mode produces different SwiftShader behavior, document the divergence.

---

I believe this revision addresses all eight issues raised:

1. **Critical (AC-01 vs D9):** Resolved. `extraArgs` is now explicitly supplementary — does NOT contain `--disable-gpu`. AC-01 matches D2. The `bridgeGpu` field controls OBJ-009's `--disable-gpu` behavior.
2. **Critical (arg duplication):** Resolved. D2 exhaustively lists which args OBJ-009 handles vs. which OBJ-049 adds. Unit test 5 explicitly validates no duplication.
3. **Major (auto re-launch):** Resolved. D4 eliminates re-launch. Auto mode probes and logs, no lifecycle management.
4. **Major (AC-14 cross-backend):** Resolved. Removed. Replaced with AC-20 (same-backend determinism). Cross-backend moved to OQ-C.
5. **Minor (Mesa detection):** Resolved. D7 checks only `"SwiftShader"`, `"llvmpipe"`, `"softpipe"` — NOT generic `"Mesa"`. AC-14 tests hardware Mesa → false.
6. **Minor (TEXTURE_TOO_SMALL):** Resolved. D8 removes it. Only `VIEWPORT_TOO_SMALL` remains. Function JSDoc explicitly states texture validation is out of scope.
7. **Minor (headless mode):** Resolved. D9 documents new headless as tested config. OQ-D covers old headless.
8. **Minor (throttling flags AC):** Resolved. AC-06 explicitly validates throttling flags appear in all modes. Unit test 4 covers this.

I ask the challenger to verify and approve.

---

## Round 4 — spec_challenger

Let me verify the revised spec against each of my Round 2 objections.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": "150",
  "limit": "120"
}
[Tool Result]    150→   * error, info) is forwarded to Node's console prefixed with
   151→   * '[depthkit:page]'. When false, only page crashes (uncaught
   152→   * exceptions) are surfaced — see pageerror handling.
   153→   */
   154→  debug?: boolean;
   155→}
   156→
   157→/**
   158→ * Manages the Puppeteer lifecycle for depthkit's rendering pipeline.
   159→ *
   160→ * Responsibilities:
   161→ * - Launch headless Chromium with correct flags for WebGL rendering.
   162→ * - Load the depthkit page shell (OBJ-010's index.html + scene-renderer.js).
   163→ * - Set viewport to match composition dimensions exactly.
   164→ * - Provide evaluate() for downstream message protocols (OBJ-011).
   165→ * - Capture rendered frames as PNG buffers via page.screenshot().
   166→ * - Detect and surface uncaught page errors (pageerror events).
   167→ * - Clean up browser resources on close.
   168→ *
   169→ * The bridge does NOT call window.depthkit.init(). Initialization of the
   170→ * Three.js render... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "offset": "350",
  "limit": "100"
}
[Tool Result]    350→
   351→**Binding constraint for OBJ-015:** Texture file paths passed to the page must be absolute filesystem paths convertible to `file://` URLs, OR data URIs / Blob URLs injected via `evaluate()`. Relative HTTP URLs will not resolve.
   352→
   353→### D11: Default `pagePath` Resolution via `import.meta.url`
   354→
   355→**Decision:** When `pagePath` is not provided, the bridge resolves it relative to its own file location using the ESM-compatible pattern:
   356→
   357→```typescript
   358→import { fileURLToPath } from 'node:url';
   359→import path from 'node:path';
   360→
   361→const __dirname = path.dirname(fileURLToPath(import.meta.url));
   362→const defaultPagePath = path.resolve(__dirname, '../page');
   363→```
   364→
   365→This resolves from `dist/engine/puppeteer-bridge.js` to `dist/page/`. Works for both local development (`npm run build` then run) and when depthkit is installed as a dependency (the `dist/` directory is part of the published package).
   366... [truncated]
Good — I've confirmed OBJ-009's internal args. Let me now verify the revised spec systematically against my 8 issues.

**Issue 1 (Critical) — AC-01 vs D9 contradiction:** ✅ Fixed. AC-01 now explicitly says `extraArgs` does NOT contain `--disable-gpu`. The new `bridgeGpu: false` field maps to OBJ-009's `gpu: false`, which adds `--disable-gpu` internally. Consistent throughout.

**Issue 2 (Critical) — Arg duplication:** ✅ Fixed. D2 exhaustively lists OBJ-009's internal args and states OBJ-049 doesn't duplicate them. The constants are renamed to `EXTRA_*`. Unit test 5 validates no duplication. The integration pattern using `bridgeGpu` + `extraArgs` is clean.

**Issue 3 (Major) — Auto re-launch:** ✅ Fixed. D4 eliminates re-launch entirely. Auto mode probes and logs. No lifecycle management.

**Issue 4 (Major) — AC-14 cross-backend:** ✅ Fixed. Old AC-14 removed. New AC-20 is same-backend determinism. Cross-backend moved to OQ-C.

**Issue 5 (Minor) — Mesa detection:** ✅ Fixed. D7 checks only `"SwiftShader"`, `"llvmpipe"`, `"softpipe"`. AC-14 (now renumbered) tests hardware Mesa → false.

**Issue 6 (Minor) — TEXTURE_TOO_SMALL:** ✅ Fixed. Removed from error codes. D8 explicitly scopes to viewport only. JSDoc says texture validation is OBJ-015's job.

**Issue 7 (Minor) — Headless mode:** ✅ Fixed. D9 documents this. OQ-D covers old headless mode.

**Issue 8 (Minor) — Throttling flags AC:** ✅ Fixed. AC-06 validates throttling flags in all modes.

Now let me check for any new issues introduced by the revision:

1. **`gpuDetected` field in `ResolvedRenderingConfig`** — The doc says "This field is NOT populated by resolveRenderingConfig() — it is set by the orchestrator after probing." This is odd — why include a field in a return type that the function never populates? It's always `null` from `resolveRenderingConfig()`. This adds noise to the interface.

   **Severity: Minor.** The field exists for the orchestrator's convenience (it can mutate the config object and log it). But it's a mutable field on what should be a pure function's return value. Not blocking — just slightly smelly.

2. **`auto` mode `resolvedMode` is `'hardware'`** — AC-03 says `resolvedMode: 'hardware'` for auto. But after probing, the actual backend might be software. The `resolvedMode` stays 'hardware' even when SwiftShader is active. This is technically accurate (the *resolved config* used hardware flags) but could confuse downstream consumers who check `resolvedMode` to understand what's running.

   **Severity: Minor.** The probe result (`WebGLRendererInfo.isSoftwareRenderer`) is the authoritative source. But the naming could mislead. The doc in the type comment covers this adequately.

3. **No AC for `probeWebGLRenderer` returning `maxTextureSize` and `maxViewportDims`** — AC-07 checks these values but only for software rendering. There's no explicit AC that the values are positive integers or that `maxViewportDims` is a 2-element tuple.

   **Severity: Negligible.** AC-07 implicitly checks this (">= 4096", ">= 1920").

These are all minor/negligible. The spec is solid. All critical and major issues are resolved. The interface is precise, the arg separation from OBJ-009 is clean, the auto-mode simplification is well-justified, and the acceptance criteria are testable.

CONCLUSION:

The specification for OBJ-049 (Software Rendering Configuration) is approved. All critical and major issues from Round 2 have been verified as resolved:

1. No arg duplication with OBJ-009 — `EXTRA_*` constants contain only supplementary args
2. `bridgeGpu` field cleanly maps to OBJ-009's `gpu` flag
3. Auto mode simplified to probe-and-log without re-launch
4. Cross-backend determinism moved to open question; AC-20 validates same-backend determinism
5. Software renderer detection uses specific names (SwiftShader, llvmpipe, softpipe) not generic Mesa
6. TEXTURE_TOO_SMALL removed; validation scoped to viewport only
7. Headless mode documented in D9 with OQ-D for old mode
8. Throttling flags validated by AC-06

Let me write the final spec to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/output.md",
  "content": "# Specification: OBJ-049 \u2014 Software Rendering Configuration\n\n## Summary\n\nOBJ-049 delivers the `rendering-config` module (`src/engine/rendering-config.ts`) \u2014 a utility that resolves the correct *supplementary* Chromium launch arguments for software or hardware-accelerated WebGL rendering, probes the active WebGL backend after launch, and validates that the backend meets depthkit's minimum requirements. This module enforces C-11 (engine must render correctly with software WebGL / SwiftShader, without GPU passthrough) while providing an opt-in path to GPU acceleration when available. It does not own the Puppeteer lifecycle \u2014 it produces configuration that `PuppeteerBridge` (OBJ-009) consumes via its existing `gpu` and `extraArgs` config, and provides post-launch validation that `FrameCapture` (OBJ-012) and the orchestrator (OBJ-035) use to confirm rendering correctness.\n\n## Interface Contract\n\n### Module: `src/engine/rendering-config.ts`\n\n```typescript\nimport type { PuppeteerBridge } from './puppeteer-bridge.js';\n\n/**\n * GPU rendering mode for the engine.\n *\n * - 'software': Force software rendering via SwiftShader/ANGLE.\n *   OBJ-009's gpu:false handles --disable-gpu. OBJ-049 adds\n *   supplementary flags (--use-gl=swiftshader, --disable-gpu-compositing).\n *   Guaranteed to work in Docker/CI without GPU passthrough.\n *   This is the C-11 baseline.\n *\n * - 'hardware': Request hardware GPU acceleration. OBJ-009's\n *   gpu:true omits --disable-gpu. OBJ-049 adds optimization\n *   flags (--enable-gpu-rasterization, etc.). Requires GPU\n *   drivers and (in Docker) GPU passthrough.\n *\n * - 'auto': Launch with hardware flags, probe WebGL. If the\n *   probe detects a software renderer, log the result and\n *   continue \u2014 Chromium's implicit SwiftShader fallback is\n *   functionally equivalent. No re-laun
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/output.md
Now update the meta.json:
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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/meta.json",
  "content": "{\n  \"id\": \"OBJ-049\",\n  \"description\": \"Software rendering configuration -- SwiftShader/ANGLE flags for headless Chromium, --disable-gpu and related Puppeteer launch args for software WebGL, GPU detection and optional GPU acceleration flags when available. Ensures correctness with software rendering per C-11 (engine must render correctly without GPU passthrough).\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:00:00Z\",\n  \"depends_on\": [\"OBJ-012\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 4 interface. Covers C-11. Spec delivers rendering-config.ts module with resolveRenderingConfig(), probeWebGLRenderer(), validateWebGLCapabilities(). Supplementary args only \u2014 no duplication with OBJ-009. Three GPU modes: software/hardware/auto. Auto mode probes and logs without re-launch.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/meta.json has been updated successfully.
Now commit:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Check git status for changed files"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "View recent commit messages for style"
}
[Tool Result] 55e99d9 spec(OBJ-030): flyover_glide camera path preset specification
a17e226 spec(OBJ-012): frame capture pipeline specification
6dbb8fc spec(OBJ-021): flyover scene geometry specification
fd55d28 spec(OBJ-020): canyon scene geometry specification
4fb72b7 spec(OBJ-014): FFmpeg audio muxing specification
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-049/meta.json

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
	nodes/OBJ-012/transcript.md
	nodes/OBJ-013/transcript.md
	nodes/OBJ-014/transcript.md
	nodes/OBJ-015/transcript.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-019/transcript.md
	nodes/OBJ-020/transcript.md
	nodes/OBJ-021/transcript.md
	nodes/OBJ-026/transcript.md
	nodes/... [truncated]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-049/output.md nodes/OBJ-049/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-049): software rendering configuration specification\n\nDefines rendering-config.ts module with three GPU modes (software/hardware/auto),\nWebGL backend probing via temporary canvas, and viewport capability validation.\nSupplementary args only \u2014 no duplication with OBJ-009's internal Chromium flags.\nAuto mode probes and logs without re-launch. Covers C-11 compliance.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-049 spec files"
}
[Tool Result] [master f54a115] spec(OBJ-049): software rendering configuration specification
 2 files changed, 483 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-049/output.md
Specification for OBJ-049 has been written and committed. 

**Deliberation summary:** The spec converged after 4 rounds. The Round 1 proposal was solid architecturally but had two critical issues (arg duplication contradiction between AC-01 and D9, unspecified overlap with OBJ-009's internal args), two major issues (unjustified auto-mode re-launch, untestable cross-backend determinism AC), and four minor issues (Mesa detection too broad, misleading TEXTURE_TOO_SMALL, missing headless mode consideration, missing throttling flag AC). All were resolved in Round 3 with:

- **`EXTRA_*` arg constants** that contain only supplementary flags OBJ-009 doesn't already add
- **`bridgeGpu` field** cleanly mapping to OBJ-009's `gpu: boolean` 
- **Auto mode simplified** to probe-and-log (no re-launch)
- **Same-backend determinism** replacing cross-backend (cross-backend moved to OQ-C)
- **Specific software renderer names** (SwiftShader, llvmpipe, softpipe) instead of generic Mesa
- **Viewport-only validation** with TEXTURE_TOO_SMALL removed
- **AC-06** explicitly validating throttling flags across all modes
