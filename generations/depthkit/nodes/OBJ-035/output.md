# Specification: OBJ-035 — Orchestrator: Main Render Loop

## Summary

OBJ-035 delivers the `Orchestrator` class (`src/engine/orchestrator.ts`) — the top-level integration point that coordinates the entire depthkit rendering pipeline from manifest to MP4. It composes FrameClock and PuppeteerBridge (OBJ-009), FrameCapture (OBJ-012), FFmpegEncoder (OBJ-013), AudioMuxer (OBJ-014), PageProtocol (OBJ-011), and the manifest loader (OBJ-016) into a deterministic frame-by-frame render loop implementing seed Section 4.4 steps 1–5. It enforces C-02 (Puppeteer + Three.js + FFmpeg pipeline), C-03 (deterministic virtualized timing), C-05 (deterministic output), and C-10 (manifest validation before rendering). This is the single entry point for both the CLI (OBJ-046) and the programmatic library API.

## Interface Contract

### Module: `src/engine/orchestrator.ts`

```typescript
import type { Manifest, ManifestRegistry, ManifestError } from '../manifest/schema.js';
import type { FFmpegEncoderResult } from './ffmpeg-encoder.js';
import type { AudioMuxerResult } from './audio-muxer.js';
import type { CaptureStats, CaptureStrategy } from './frame-capture.js';
import type { RendererInfo } from './protocol-types.js';
import type { H264Preset } from './ffmpeg-encoder.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

// ────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────

/**
 * Configuration for the Orchestrator.
 */
export interface OrchestratorConfig {
  /**
   * The manifest to render. Always validated via loadManifest()
   * (Phase 1 structural + Phase 2 semantic) before rendering begins.
   * Zod parsing is synchronous and cheap — re-validating a pre-parsed
   * Manifest object adds negligible overhead.
   *
   * To skip validation entirely (testing/debugging only), set
   * skipValidation: true. In that case, `manifest` must be a
   * structurally valid Manifest object — undefined behavior otherwise.
   */
  manifest: unknown;

  /**
   * The manifest registry containing registered geometries and cameras
   * for semantic validation (OBJ-016 Phase 2). Provides validation
   * metadata: slot names, compatible cameras, required/optional flags.
   */
  registry: ManifestRegistry;

  /**
   * The geometry registry containing full SceneGeometry definitions.
   * Used to resolve slot positions, rotations, and sizes for scene setup.
   * Obtain via getGeometryRegistry() from OBJ-005's registry module.
   *
   * Distinct from ManifestRegistry's GeometryRegistration, which
   * contains only validation metadata (slot names, compatible cameras).
   * This registry contains the spatial data (PlaneSlot positions,
   * rotations, sizes) needed to construct SlotSetup objects.
   */
  geometryRegistry: GeometryRegistry;

  /**
   * The camera path registry containing full CameraPathPreset objects.
   * Used to call evaluate(t, params) per frame for camera positioning.
   * Obtain via the camera registry from OBJ-006.
   *
   * Distinct from ManifestRegistry's CameraRegistration, which
   * contains only validation metadata (compatible geometries,
   * supportsFovAnimation flag).
   */
  cameraRegistry: CameraPathRegistry;

  /**
   * Output file path for the final MP4.
   * Parent directory must exist. File is overwritten if it exists.
   */
  outputPath: string;

  /**
   * Base directory for resolving relative image paths in the manifest.
   * If a plane's `src` is a relative path, it is resolved via
   * path.resolve(assetsDir, src).
   *
   * Default: process.cwd()
   */
  assetsDir?: string;

  /**
   * Capture strategy for pixel extraction from headless Chromium.
   * Default: 'viewport-png'.
   */
  captureStrategy?: CaptureStrategy;

  /**
   * H.264 encoding preset. Default: 'medium'.
   */
  encodingPreset?: H264Preset;

  /**
   * Constant Rate Factor for encoding quality (0-51). Default: 23.
   */
  crf?: number;

  /**
   * Enable GPU-accelerated WebGL rendering. Default: false.
   * When false: software rendering via SwiftShader (C-11 compliance).
   */
  gpu?: boolean;

  /**
   * Path to FFmpeg binary. Default: resolved via resolveFFmpegPath().
   */
  ffmpegPath?: string;

  /**
   * Path to Chromium executable. Default: Puppeteer's bundled Chromium.
   */
  chromiumPath?: string;

  /**
   * Skip manifest validation entirely. Default: false.
   * WARNING: Only for testing/debugging. When true, `manifest` must
   * be a structurally valid Manifest object — undefined behavior
   * otherwise. No validation errors are returned.
   */
  skipValidation?: boolean;

  /**
   * Forward headless browser console messages to Node stdout.
   * Default: false.
   */
  debug?: boolean;

  /**
   * Progress callback invoked after each frame is captured and
   * written to FFmpeg.
   *
   * Return `false` to request cancellation. The orchestrator aborts
   * after the current frame completes and throws OrchestratorError
   * with code 'CANCELLED'.
   *
   * If the callback throws, the error is caught and treated as a
   * cancellation request (same behavior as returning false).
   */
  onProgress?: (progress: RenderProgress) => boolean | void;
}

/**
 * Progress data passed to the onProgress callback.
 */
export interface RenderProgress {
  /** Current frame number (zero-indexed). */
  frame: number;
  /** Total number of frames in the composition. */
  totalFrames: number;
  /**
   * Progress ratio [0, 1]. Computed as (frame + 1) / totalFrames.
   * Reaches 1.0 after the last frame is processed.
   */
  ratio: number;
  /** Elapsed wall-clock time in milliseconds since render loop start. */
  elapsedMs: number;
  /**
   * Estimated remaining time in milliseconds.
   * Computed as: (totalFrames - frame - 1) * (elapsedMs / (frame + 1)).
   * 0 on the last frame.
   */
  estimatedRemainingMs: number;
  /** Throughput: (frame + 1) / (elapsedMs / 1000). Rendered fps. */
  throughputFps: number;
  /**
   * Scene ID(s) being rendered for this frame.
   * - Normal frame: ['scene_001'] (single active scene)
   * - Crossfade transition: ['scene_001', 'scene_002'] (outgoing first)
   * - Gap (no active scene): [] (empty array)
   */
  activeSceneIds: string[];
}

// ────────────────────────────────────────────
// Result
// ────────────────────────────────────────────

/**
 * Result returned on successful render completion.
 */
export interface OrchestratorResult {
  /** Absolute path to the final output MP4 file. */
  outputPath: string;

  /** Total number of frames rendered. */
  totalFrames: number;

  /** Wall-clock time for the frame render loop in milliseconds
   *  (from first frame to FFmpeg finalize, excluding validation,
   *  browser launch, and audio mux). */
  renderDurationMs: number;

  /** Total wall-clock time including validation, setup, render,
   *  and audio mux. */
  totalDurationMs: number;

  /** Average milliseconds per frame (renderDurationMs / totalFrames). */
  averageFrameMs: number;

  /** Video duration in seconds (totalFrames / fps). */
  videoDurationSeconds: number;

  /** Capture statistics from FrameCapture (OBJ-012). */
  captureStats: CaptureStats;

  /** FFmpeg encoding result from FFmpegEncoder (OBJ-013). */
  encoderResult: FFmpegEncoderResult;

  /** Audio muxing result from AudioMuxer (OBJ-014). null if no audio. */
  audioResult: AudioMuxerResult | null;

  /** WebGL renderer info from the headless browser. */
  rendererInfo: RendererInfo;

  /** Validation warnings (non-blocking) from manifest validation. */
  warnings: ManifestError[];
}

// ────────────────────────────────────────────
// Errors
// ────────────────────────────────────────────

export type OrchestratorErrorCode =
  | 'MANIFEST_INVALID'      // Manifest validation failed (C-10)
  | 'BROWSER_LAUNCH_FAILED' // Puppeteer/Chromium failed to start
  | 'PAGE_INIT_FAILED'      // Three.js page initialization failed
  | 'SCENE_SETUP_FAILED'    // Scene setup (texture loading or missing images)
  | 'RENDER_FAILED'         // Frame rendering failed on the page
  | 'CAPTURE_FAILED'        // Frame capture failed (FrameCapture error)
  | 'ENCODE_FAILED'         // FFmpeg encoding failed
  | 'AUDIO_MUX_FAILED'      // Audio muxing failed (OBJ-014)
  | 'CANCELLED'             // Cancelled via onProgress callback
  | 'GEOMETRY_NOT_FOUND'    // Geometry missing from geometryRegistry at render time
  | 'CAMERA_NOT_FOUND'      // Camera preset missing from cameraRegistry at render time
  ;

/**
 * Structured error from the orchestrator.
 */
export class OrchestratorError extends Error {
  readonly code: OrchestratorErrorCode;
  /** Frame number where the error occurred. -1 if not frame-related. */
  readonly frame: number;
  /** The original error that caused this failure. */
  readonly cause?: Error;
  /** Validation errors when code is MANIFEST_INVALID. */
  readonly validationErrors?: ManifestError[];

  constructor(
    code: OrchestratorErrorCode,
    message: string,
    options?: { frame?: number; cause?: Error; validationErrors?: ManifestError[] }
  );
}

// ────────────────────────────────────────────
// Main Class
// ────────────────────────────────────────────

/**
 * The main rendering orchestrator for depthkit.
 *
 * Composes the full pipeline per seed Section 4.4:
 *
 *   Phase A — Validation & Pre-Flight:
 *   1. Validate manifest against registry (OBJ-016). Fail-fast on error (C-10).
 *   2. Resolve geometry definitions and camera presets for all scenes.
 *   3. Compute total duration and frame count via FrameClock (OBJ-009).
 *   4. Resolve and verify all image paths exist on disk (pre-flight).
 *
 *   Phase B — Infrastructure Launch:
 *   5. Launch headless Chromium via PuppeteerBridge (OBJ-009).
 *   6. Initialize Three.js renderer via PageProtocol (OBJ-011).
 *   7. Spawn FFmpeg encoder (OBJ-013). Create FrameCapture (OBJ-012).
 *
 *   Phase C — Frame Render Loop (C-02, C-03):
 *   8. Sort scenes by start_time.
 *   9. For each frame from FrameClock.frames():
 *      a. Determine active scene(s) for this timestamp.
 *      b. Lazy-setup scenes needed but not yet on the page.
 *      c. Compute camera state via CameraPathPreset.evaluate().
 *      d. Construct RenderFrameCommand (single/multi-pass, or
 *         clear-only for gap frames).
 *      e. protocol.renderFrame(command) — or explicit canvas clear
 *         for gap frames.
 *      f. capture.capture()
 *      g. encoder.writeFrame(result.data)
 *      h. Eager-teardown scenes no longer needed.
 *      i. Invoke onProgress callback; abort if returns false or throws.
 *
 *   Phase D — Finalization:
 *   10. encoder.finalize() — produces video-only MP4.
 *   11. Close browser via bridge.close().
 *   12. If audio: mux via AudioMuxer (OBJ-014); delete temp video file.
 *   13. Return OrchestratorResult.
 *
 * The orchestrator owns the lifecycle of ALL sub-components.
 * Callers interact only with render().
 *
 * NOT reusable — one instance per render. Not thread-safe.
 *
 * Scene transition rendering (crossfade, dip_to_black) is handled
 * inline in V1. OBJ-036 (scene sequencer) will later extract this
 * logic; the orchestrator's private methods are structured to be
 * replaceable by OBJ-036 without changing the public API.
 */
export class Orchestrator {
  constructor(config: OrchestratorConfig);

  /**
   * Execute the full rendering pipeline.
   *
   * Lifecycle guarantees:
   * - All sub-resources (browser, FFmpeg process) are cleaned up
   *   on both success and failure via try/finally.
   * - On failure: partial output files are deleted. The outputPath
   *   contains a valid file only on success.
   * - The OrchestratorError always wraps the original error as `cause`.
   *
   * @returns OrchestratorResult on success.
   * @throws OrchestratorError on any failure.
   */
  render(): Promise<OrchestratorResult>;
}

// ────────────────────────────────────────────
// Convenience Function
// ────────────────────────────────────────────

/**
 * Convenience: loads manifest from a JSON file, creates an
 * Orchestrator, and calls render().
 *
 * Uses loadManifestFromFile() (OBJ-016) for file loading + Phase 1
 * validation. Phase 2 runs inside the Orchestrator.
 *
 * @param manifestPath - Path to the manifest JSON file.
 * @param registry - Populated ManifestRegistry.
 * @param geometryRegistry - Populated GeometryRegistry (from OBJ-005).
 * @param cameraRegistry - Populated CameraPathRegistry (from OBJ-006).
 * @param options - Remaining config options (outputPath required).
 * @returns OrchestratorResult.
 * @throws OrchestratorError on any failure.
 */
export async function renderFromFile(
  manifestPath: string,
  registry: ManifestRegistry,
  geometryRegistry: GeometryRegistry,
  cameraRegistry: CameraPathRegistry,
  options: Omit<OrchestratorConfig, 'manifest' | 'registry' | 'geometryRegistry' | 'cameraRegistry'>,
): Promise<OrchestratorResult>;
```

## Design Decisions

### D1: Single `render()` Method, No Exposed Sub-Components

**Decision:** The `Orchestrator` exposes only `render()`. PuppeteerBridge, PageProtocol, FrameCapture, and FFmpegEncoder are internal and inaccessible to callers.

**Rationale:** The orchestrator owns all sub-component lifecycles. Exposing internals would allow callers to interfere with the deterministic render loop (violating C-03) or leak resources. The CLI and n8n endpoint only need `render()`. If fine-grained control is needed later, it can be added as a separate `PipelineBuilder` class.

### D2: Resource Cleanup via try/finally

**Decision:** `render()` uses a try/finally pattern guaranteeing cleanup of all resources on both success and failure.

**Cleanup order on failure:**
1. `encoder.abort()` — kills FFmpeg process (idempotent per OBJ-013).
2. `protocol.dispose()` — tears down all page scenes (idempotent per OBJ-011).
3. `bridge.close()` — kills Chromium (idempotent per OBJ-009).
4. Delete partial output files (temp video MP4 and/or final output MP4).
5. Throw OrchestratorError.

**Rationale:** C-10 requires no partial output from invalid manifests. The same principle extends to runtime failures — a failed render must not leave zombie processes, open pipes, or corrupted files.

### D3: Scene Iteration With Inline Transition Handling

**Decision:** In V1, the orchestrator iterates frames linearly via `FrameClock.frames()`, determining for each frame which scene(s) are active and constructing the appropriate `RenderFrameCommand`. This logic lives as private methods on the Orchestrator class.

**Internal scene iteration algorithm:**

1. Sort scenes by `start_time` (stable sort, per OBJ-016 D-11).
2. Build a scene timeline: for each sorted scene, compute `endTime = start_time + duration`.
3. For each frame tick from FrameClock:
   a. `timestamp = tick.timestamp`
   b. Find the primary active scene: the scene whose `[start_time, start_time + duration)` contains `timestamp`. For the last scene, the interval is `[start_time, start_time + duration]` (inclusive end) to ensure the last frame is rendered.
   c. Check for transition windows (see D13).
   d. **If no scene's time range contains the timestamp (gap frame):** handle via D16 (explicit canvas clear, then capture). No `RenderFrameCommand` is sent.
   e. **If one scene is active (normal frame):** construct single-pass `RenderFrameCommand`.
   f. **If two scenes are active (transition overlap):** construct multi-pass `RenderFrameCommand` per D13.

**Rationale:** OBJ-036 (scene sequencer) depends on OBJ-035, so the orchestrator must be functional without it. Private methods are structured so OBJ-036 can later provide a `SceneSequencer` that replaces the scene iteration without changing the public API.

### D4: Camera State Computation Per Frame

**Decision:** For each frame, the orchestrator:
1. Computes per-scene normalized time: `t = clamp((tick.timestamp - scene.start_time) / scene.duration, 0, 1)`.
2. Reads `CameraParams` from the manifest scene's `camera_params` (with defaults applied by Zod: `speed: 1.0`, `easing: 'ease_in_out'`).
3. Calls `cameraPreset.evaluate(t, cameraParams)` to get `CameraFrameState`. The preset internally resolves easing names to functions via `resolveCameraParams()` — the orchestrator does not call `resolveCameraParams()` directly.
4. Applies `camera_params.offset` (if any) additively to the returned position: `position[i] += offset[i]`.
5. Constructs `RequiredCameraState` for the RenderPass: `{ position, lookAt, fov }`.

**Rationale:** Camera state is stateless per OBJ-006's `CameraPathEvaluator` contract. Fresh computation per frame with no carried state aligns with C-03 and C-05.

### D5: Geometry Slot to SlotSetup Mapping

**Decision:** When setting up a scene, the orchestrator:
1. Looks up `SceneGeometry` by name from the `geometryRegistry` config parameter.
2. For each plane key in the manifest scene's `planes` record:
   a. Gets the geometry's `PlaneSlot` for that key.
   b. Applies `position_override` from `PlaneRef` if present (replaces the slot's position entirely).
   c. Applies `rotation_override` from `PlaneRef` if present (replaces the slot's rotation entirely).
   d. Applies `scale` from `PlaneRef` by multiplying `slot.size[0] * scale` and `slot.size[1] * scale`.
   e. Resolves image `src` path (per D8).
   f. Constructs `SlotSetup`: `{ position, rotation, size, textureSrc, transparent: slot.transparent, renderOrder: slot.renderOrder, fogImmune: slot.fogImmune }`.
3. Constructs `SceneSetupConfig`: `{ sceneId: scene.id, slots, fog: geometry.fog }`.
4. Calls `protocol.setupScene(config)`.
5. **Checks `SceneSetupResult.success`.** If `false`, throws `OrchestratorError` with code `SCENE_SETUP_FAILED`. The error message lists each slot with `status: 'error'` and its error message from `SlotLoadResult`.

**Rationale:** The orchestrator is the translation layer between the declarative manifest and the imperative page protocol. Setup failures are fatal — rendering with magenta fallback meshes is wrong for production.

### D6: Audio Muxing as Post-Encoding Step

**Decision:** If `manifest.composition.audio` is defined:
1. Render video to a temporary path: `{outputPath}.tmp.video.mp4`.
2. Mux audio via OBJ-014's `muxAudio()` function with the audio file path from the manifest.
3. Delete the temporary video-only file on success.

If no audio, write video-only MP4 directly to `outputPath`.

**Rationale:** OBJ-013 produces video-only output by design. Audio muxing is a cheap separate FFmpeg pass (`-c:v copy`) that adds negligible time.

### D7: Manifest Validation Gate (C-10)

**Decision:** Before any resource allocation, the orchestrator validates the manifest by calling `loadManifest(config.manifest, config.registry)`. If validation fails (`success: false`), `render()` throws `OrchestratorError` with code `MANIFEST_INVALID`, containing all `ManifestError` objects in the `validationErrors` property.

No PuppeteerBridge launch, no FFmpeg spawn, no image pre-flight checks until validation passes.

**The manifest is always validated.** Even if the caller passes a pre-parsed `Manifest` object, it is re-validated through `loadManifest()`. Zod's `safeParse()` is synchronous and fast — re-parsing a valid manifest is negligible overhead compared to the rendering pipeline. This eliminates the need for fragile type discrimination.

**Exception:** When `skipValidation: true`, the orchestrator casts `config.manifest` to `Manifest` without validation. The manifest is treated as valid. Undefined behavior if it isn't.

**Rationale:** C-10: "Invalid manifests must never produce partial output — fail fast, fail clearly."

### D8: Image Path Resolution

**Decision:** Image `src` paths from the manifest are resolved:
1. Protocol prefix (`http://`, `https://`, `data:`): passed through as-is. No filesystem check.
2. Absolute path (starts with `/`): used as-is. Filesystem-checked.
3. Relative path: `path.resolve(config.assetsDir ?? process.cwd(), src)`. Filesystem-checked.

Resolved paths are validated for existence (via `fs.access(path, fs.constants.R_OK)`) during pre-flight, before launching the browser. All missing files across all scenes are collected, and if any are missing, `render()` throws `OrchestratorError` with code `SCENE_SETUP_FAILED` listing **all** missing file paths. This fails before any resource allocation beyond manifest validation.

**Rationale:** Failing fast on missing images saves time. Discovering a missing image at frame 900 of 1800 wastes half the render. Pre-flight checks catch this before any rendering begins.

### D9: Progress Callback and Cancellation

**Decision:** `onProgress` is invoked after each frame is fully processed (rendered + captured + written to FFmpeg). If it returns `false`, the orchestrator:
1. Aborts the FFmpeg encoder.
2. Disposes page protocol and closes browser.
3. Deletes partial output.
4. Throws `OrchestratorError` with code `CANCELLED`.

**If `onProgress` throws an exception,** the error is caught and treated as a cancellation request — same cleanup and `CANCELLED` error as returning `false`. The original exception is available as the `cause` on the `OrchestratorError`.

**Rationale:** Post-write invocation ensures accurate throughput stats. Cancellation via return value is simpler than a separate abort signal. Treating thrown exceptions as cancellation prevents unhandled errors from leaking.

### D10: One Instance Per Render

**Decision:** `Orchestrator` is not reusable. `render()` can be called once. A second call throws `OrchestratorError` with code `RENDER_FAILED` and message: "Orchestrator has already been used. Create a new instance."

**Rationale:** Reusable orchestrators require complex reset logic. One-shot instances are simpler and match the production pattern.

### D11: Temporary Video File Naming

**Decision:** When audio muxing is needed, the temp video file is `{outputPath}.tmp.video.mp4`. Deleted on success. Deleted on failure.

**Rationale:** Predictable naming in the same directory avoids cross-filesystem issues.

### D12: Geometry and Camera Preset Resolution at Render Start

**Decision:** After validation passes, the orchestrator resolves the full `SceneGeometry` and `CameraPathPreset` for every scene upfront, building a `Map<string, { geometry: SceneGeometry, cameraPreset: CameraPathPreset }>` keyed by scene ID.

- Geometry: looked up from `config.geometryRegistry[scene.geometry]`.
- Camera: looked up via `getCameraPath(config.cameraRegistry, scene.camera)` (OBJ-006).

If any geometry or camera is not found in the spatial registries (despite passing manifest validation against `ManifestRegistry`), throws `OrchestratorError` with `GEOMETRY_NOT_FOUND` or `CAMERA_NOT_FOUND`. This catches inconsistencies between the validation registry and the spatial registries.

**Rationale:** Catches registry inconsistencies before the render loop. Looking up per-frame is wasteful. Upfront resolution also provides clear error messages naming the missing geometry/camera and the scene that requires it.

### D13: Transition Rendering Algorithm

**Decision:** The orchestrator computes transition state per-frame:

**Crossfade** (scene A `transition_out: crossfade` -> scene B `transition_in: crossfade`):
- Overlap window: `[B.start_time, A.start_time + A.duration]`.
- Progress `p = clamp((timestamp - B.start_time) / (A.start_time + A.duration - B.start_time), 0, 1)`.
- Passes: `[{ sceneId: A, opacity: 1.0, camera: A_state }, { sceneId: B, opacity: p, camera: B_state }]`.
- This matches OBJ-011 D2's compositing model: over-paint produces `A * (1-p) + B * p` for opaque scenes.

**Dip-to-black** (scene A `transition_out: dip_to_black`):
- Fade-out window: `[A.start_time + A.duration - A.transition_out.duration, A.start_time + A.duration]`.
- Progress `p_out = clamp((timestamp - fade_out_start) / transition_out.duration, 0, 1)`.
- Pass: `[{ sceneId: A, opacity: 1 - p_out, camera: A_state }]`.
- The clear color (black) shows through where opacity < 1.

**Dip-to-black** (scene B `transition_in: dip_to_black`):
- Fade-in window: `[B.start_time, B.start_time + B.transition_in.duration]`.
- Progress `p_in = clamp((timestamp - B.start_time) / transition_in.duration, 0, 1)`.
- Pass: `[{ sceneId: B, opacity: p_in, camera: B_state }]`.

**Cut**: Single pass, opacity 1.0. Scene switches instantly at the boundary frame.

**Easing on transitions:** Transition progress values are NOT eased in V1 — linear opacity ramps. Transition easing can be added in OBJ-036.

### D14: Lazy Scene Setup, Eager Teardown

**Decision:**
- A scene is set up when first needed: at its `start_time`, or earlier if a preceding scene's crossfade transition requires it.
- A scene is torn down when the last frame that references it has been rendered.
- At most 2 scenes are active simultaneously (for transitions).

**Implementation:**
- Track `Set<string>` of scene IDs currently active on the page.
- Before each frame: compute needed scene IDs. Setup any not in the active set. After each frame: teardown any in the active set that are no longer needed by any subsequent frame.

**Rationale:** Minimizes GPU memory — critical for the 4GB RAM constraint in C-08. A 5-scene video never has more than 2 scenes' textures loaded at once.

### D15: Pre-Flight Image Existence Check

**Decision:** After manifest validation, before launching the browser, the orchestrator resolves all image paths across all scenes and checks each with `fs.access(path, fs.constants.R_OK)`. **All** missing or unreadable files are collected into a single list, and if any are missing, `render()` throws `OrchestratorError` with code `SCENE_SETUP_FAILED`, listing every missing file path with its scene ID and slot name.

**Exception:** Paths with `http://`, `https://`, or `data:` protocol prefixes skip the filesystem check.

**Rationale:** Extension of C-10's fail-fast principle. Collecting all missing files (not just the first) allows the user to fix all issues in one pass.

### D16: Gap Frame Rendering

**Decision:** When no scene's time range contains the current timestamp (a time gap between scenes), the orchestrator:
1. Explicitly clears the canvas by calling `bridge.evaluate(() => { window.depthkit.renderer.clear(); })`.
2. Calls `capture.capture()` to capture the clear color (black by default).
3. Pipes the captured buffer to FFmpeg.

No `protocol.renderFrame()` is called for gap frames, because OBJ-011 rejects empty passes (`INVALID_COMMAND`).

**Rationale:** Gaps between scenes are valid per the manifest schema (OBJ-016 emits a `SCENE_GAP` warning but does not reject them). The clear color provides a clean black frame during gaps, which is the expected visual behavior for `dip_to_black` transitions and explicit timing gaps.

**Implementation note:** The `window.depthkit.renderer` reference is available because OBJ-010's page shell exposes it on the `window.depthkit` namespace (confirmed by OBJ-010 AC-02: `window.depthkit` exposes `renderer`, `scene`, and `camera` properties; and OBJ-010 OQ-B which explicitly states "the renderer property is exposed and mutable"). The `clear()` method clears the canvas to the configured clear color (default: black, `#000000`).

### D17: FrameClock Duration Source

**Decision:** Total composition duration is computed as `Math.max(...scenes.map(s => s.start_time + s.duration))` — the same formula as OBJ-016's `computeTotalDuration()`. The FrameClock is created via `FrameClock.fromDuration(manifest.composition.fps, totalDuration)`.

**Rationale:** Audio duration does NOT override scene durations in the render loop. If there's a mismatch, OBJ-016 emits an `AUDIO_DURATION_MISMATCH` warning, and OBJ-014's duration strategy handles the alignment at the mux stage.

### D18: Per-Plane Static Opacity — V1 Limitation

**Decision:** OBJ-004's `PlaneRef.opacity` field (default 1.0) is **not supported in V1**. OBJ-011's `SlotSetup` does not carry a per-slot opacity field — opacity is applied only at the scene level via `RenderPass.opacity`, which affects all meshes in a scene group uniformly.

If any `PlaneRef` in the manifest has `opacity !== 1.0`, the orchestrator logs a warning to the console (when `debug: true`) and includes a `ManifestError` with severity `"warning"` and a descriptive message in `OrchestratorResult.warnings`. The opacity value is silently ignored — all planes render at full opacity within their scene.

**Rationale:** Supporting per-plane opacity requires extending OBJ-011's `SlotSetup` interface, which is outside OBJ-035's scope. The manifest schema (OBJ-004) defines the field for forward compatibility, but the rendering pipeline does not yet consume it. This is documented as an open question for future work (OQ-E).

### D19: Aspect Ratio for PageInitConfig

**Decision:** The orchestrator computes `aspectRatio = manifest.composition.width / manifest.composition.height` and passes `width`, `height`, and `fov` (from the geometry's default FOV or the camera's FOV configuration) to `PageProtocol.initialize()` as part of `PageInitConfig`.

## Acceptance Criteria

### Validation (C-10)

- [ ] **AC-01:** `render()` with a manifest containing an unknown geometry name throws `OrchestratorError` with code `MANIFEST_INVALID`. No browser is launched.
- [ ] **AC-02:** `render()` with a manifest missing required plane slots throws `OrchestratorError` with code `MANIFEST_INVALID`. No FFmpeg process is spawned.
- [ ] **AC-03:** `OrchestratorError` for `MANIFEST_INVALID` includes all validation errors in `validationErrors`, not just the first.
- [ ] **AC-04:** A valid manifest with a `SCENE_ORDER_MISMATCH` warning renders successfully. The warning appears in `OrchestratorResult.warnings`.

### Pipeline Integration (C-02)

- [ ] **AC-05:** A single-scene manifest with one plane renders to a valid MP4 that `ffprobe` reports as H.264, with correct resolution, fps, and approximately correct duration.
- [ ] **AC-06:** A 3-scene manifest with different geometries renders to a valid MP4. Each scene's planes are visible in the corresponding time segment.
- [ ] **AC-07:** The output MP4 includes `movflags +faststart` (verifiable via `ffprobe`).

### Deterministic Timing (C-03, C-05)

- [ ] **AC-08:** For a manifest with 30fps and 2.0 seconds duration, exactly 60 frames are written to FFmpeg (`encoderResult.frameCount === 60`).
- [ ] **AC-09:** Rendering the same manifest + same images twice produces identical `totalFrames` and `videoDurationSeconds` in both results.
- [ ] **AC-10:** The orchestrator never calls `requestAnimationFrame` or uses wall-clock timing for frame advancement. Frame iteration is driven exclusively by `FrameClock.frames()`.

### Audio (C-07)

- [ ] **AC-11:** A manifest with `composition.audio.src` pointing to a valid MP3 file produces a final MP4 with both video and audio streams (verifiable via `ffprobe`).
- [ ] **AC-12:** A manifest without `composition.audio` produces a video-only MP4. `OrchestratorResult.audioResult` is `null`.
- [ ] **AC-13:** After successful audio muxing, the temporary video-only file (`{outputPath}.tmp.video.mp4`) does not exist on disk.

### Scene Setup and Teardown

- [ ] **AC-14:** Images with relative paths in the manifest are resolved against `assetsDir`. A manifest referencing `./images/bg.png` with `assetsDir: '/project/assets'` resolves to `/project/assets/images/bg.png`.
- [ ] **AC-15:** Pre-flight image check: if a manifest references non-existent image files, `render()` throws `OrchestratorError` with code `SCENE_SETUP_FAILED` before launching the browser. The error message lists **all** missing file paths.
- [ ] **AC-16:** During a 5-scene render, at most 2 scenes are active on the page simultaneously (verifiable by logging `protocol.getActiveSceneIds()` per frame in debug mode, or by inspecting setup/teardown calls in a mock).

### Transitions

- [ ] **AC-17:** A 2-scene manifest with a `crossfade` transition of 1.0s between scenes renders the overlap frames as multi-pass commands. The captured frames during the transition are visually distinct from either scene alone.
- [ ] **AC-18:** A 2-scene manifest with a `cut` transition has no overlap — the scene switches at the boundary frame.
- [ ] **AC-19:** A 2-scene manifest with `dip_to_black` transitions produces frames that fade to the clear color (black) between scenes.

### Gap Frames

- [ ] **AC-20:** A manifest with a time gap between two scenes renders black frames during the gap. The orchestrator explicitly clears the canvas for gap frames without calling `protocol.renderFrame()`.

### Camera Paths

- [ ] **AC-21:** For a scene using a forward-push camera preset, the captured frames show progressive forward movement (early frames show a wider view than later frames).
- [ ] **AC-22:** `camera_params.offset` shifts the camera position without affecting lookAt. A scene with `offset: [2, 0, 0]` renders with the camera shifted 2 units to the right compared to the same scene without offset.

### Error Handling and Cleanup

- [ ] **AC-23:** If FFmpeg crashes mid-encode, `render()` throws `OrchestratorError` with code `ENCODE_FAILED`. The browser is closed (no zombie Chromium process).
- [ ] **AC-24:** If a page error occurs during frame rendering, `render()` throws `OrchestratorError` with code `RENDER_FAILED`. FFmpeg is aborted. Browser is closed.
- [ ] **AC-25:** On any failure, partial output files are deleted. The `outputPath` does not contain a corrupted partial MP4.
- [ ] **AC-26:** `render()` called twice on the same instance throws `OrchestratorError` without launching any resources.

### Progress and Cancellation

- [ ] **AC-27:** `onProgress` is called once per frame. The `frame` field increments from 0 to totalFrames-1. `ratio` reaches 1.0 on the last callback invocation.
- [ ] **AC-28:** If `onProgress` returns `false` at frame 10 of a 60-frame render, `render()` throws `OrchestratorError` with code `CANCELLED`. Fewer than 60 frames are written. All resources are cleaned up.
- [ ] **AC-29:** If `onProgress` throws an error, `render()` throws `OrchestratorError` with code `CANCELLED`. The thrown error is available as `cause`. All resources are cleaned up.

### Performance (C-08, TC-02)

- [ ] **AC-30:** A 60-second, 30fps, 5-plane-per-scene video at 1920x1080 renders in under 15 minutes on a 4-core VPS with 4GB+ RAM using software WebGL. (Performance test — logged as a benchmark, not enforced in CI.)

### Convenience Function

- [ ] **AC-31:** `renderFromFile()` with a valid manifest file path produces the same result as manually loading the file and creating an Orchestrator.
- [ ] **AC-32:** `renderFromFile()` with a non-existent file path throws `OrchestratorError` with code `MANIFEST_INVALID`, with `validationErrors` containing a `FILE_NOT_FOUND` error.

### Renderer Info and Diagnostics

- [ ] **AC-33:** `OrchestratorResult.rendererInfo.initialized === true` and `rendererInfo.webglVersion` is a non-empty string.

### Per-Plane Opacity Warning (D18)

- [ ] **AC-34:** A manifest with a `PlaneRef` having `opacity: 0.5` renders successfully (the plane renders at full opacity). `OrchestratorResult.warnings` includes a warning about unsupported per-plane opacity.

## Edge Cases and Error Handling

### Manifest and Validation

| Scenario | Expected Behavior |
|---|---|
| `manifest` is null/undefined/number | Full validation catches it. `OrchestratorError` code `MANIFEST_INVALID`. |
| Valid manifest but `geometryRegistry` is empty | Passes manifest validation (ManifestRegistry may have registrations). Fails at D12 preset resolution with `GEOMETRY_NOT_FOUND`. |
| Valid manifest but `cameraRegistry` is empty | Passes manifest validation. Fails at D12 with `CAMERA_NOT_FOUND`. |
| Manifest with 0-duration scene | Zod schema rejects (`duration` must be positive). `MANIFEST_INVALID`. |
| `skipValidation: true` with an invalid manifest | Undefined behavior (documented). May crash mid-render. |
| Manifest with `PlaneRef.opacity !== 1.0` | Warning in result. Plane renders at full opacity. |

### Image Resolution

| Scenario | Expected Behavior |
|---|---|
| Image path is absolute and exists | Used as-is. Pre-flight check passes. |
| Image path is relative, `assetsDir` not set | Resolved against `process.cwd()`. |
| Image path is relative and resolved path doesn't exist | Collected. After checking all paths, `OrchestratorError` code `SCENE_SETUP_FAILED` with all missing paths listed. |
| Multiple missing images across different scenes | All missing paths listed in the error message. |
| Image path is `data:image/png;base64,...` | Skips filesystem check. Passed through to page. |
| Image path is `https://example.com/img.png` | Skips filesystem check. Passed through to page. Network failure caught by page texture loading; `setupScene()` returns `success: false`; orchestrator throws `SCENE_SETUP_FAILED`. |

### Scene Timing

| Scenario | Expected Behavior |
|---|---|
| Single scene, no transitions | Renders all frames with that scene. Single-pass commands. |
| Two scenes with no overlap and no gap | Scene A renders until its end, scene B starts on the next frame. Cut transition. |
| Two scenes with a gap (B.start_time > A.end_time) | Gap frames: canvas cleared to black, captured, piped to FFmpeg. Per D16. |
| Scenes not in start_time order in manifest | Sorted by start_time before rendering (OBJ-016 warned about this). |
| Scene with zero-length transition (cut with duration: 0) | Equivalent to an instant cut. Single pass, no overlap. |
| Crossfade where both scenes use the same geometry | Works correctly — two separate scene instances with potentially different images. |

### Transition Edge Cases

| Scenario | Expected Behavior |
|---|---|
| First scene has `transition_in: crossfade` | OBJ-016 validation catches this (`CROSSFADE_NO_ADJACENT`). If `skipValidation` is true: the first frame attempts multi-pass with non-existent preceding scene — PageProtocol throws `SCENE_NOT_FOUND`; orchestrator catches and throws `RENDER_FAILED`. |
| Crossfade progress exactly 0.0 | Pass B opacity = 0.0. Only scene A visible. |
| Crossfade progress exactly 1.0 | Pass B opacity = 1.0. Scene B fully covers A. |
| Dip-to-black with no subsequent scene | Scene fades to black. Remaining frames (if any gap) are black per D16. |

### Resource Failures

| Scenario | Expected Behavior |
|---|---|
| Puppeteer fails to launch (no Chromium) | `OrchestratorError` code `BROWSER_LAUNCH_FAILED`. No FFmpeg process spawned. |
| Page init fails (WebGL not available) | `OrchestratorError` code `PAGE_INIT_FAILED`. Browser is closed. |
| Texture load fails for one slot during setupScene | `protocol.setupScene()` returns `success: false`. Orchestrator throws `SCENE_SETUP_FAILED` listing the failed slots and their error messages. Browser and FFmpeg are cleaned up. |
| FFmpeg exits mid-encode | Detected at next `writeFrame()` or `finalize()`. `OrchestratorError` code `ENCODE_FAILED` with FFmpeg stderr in `cause`. Browser closed. |
| Audio file missing or corrupt | `OrchestratorError` code `AUDIO_MUX_FAILED`. Temp video file deleted. |
| Output directory doesn't exist | FFmpeg fails to open output. `ENCODE_FAILED`. |
| `onProgress` throws | Treated as cancellation. `CANCELLED` with original error as `cause`. Same cleanup. |

### Concurrent and Lifecycle

| Scenario | Expected Behavior |
|---|---|
| `render()` called twice | Second call throws `OrchestratorError` code `RENDER_FAILED` with message "Orchestrator has already been used. Create a new instance." No resources allocated. |
| Two Orchestrator instances running in parallel | Each is independent — separate browser, separate FFmpeg. Works if system resources permit. |

## Test Strategy

### Unit Tests: `test/unit/orchestrator.test.ts`

These test the orchestrator's logic without launching real sub-components. Sub-components are mocked.

1. **Validation gate:** Mock `loadManifest()` to return `{ success: false, errors: [...] }`. Verify `render()` throws `OrchestratorError` with `MANIFEST_INVALID` and correct `validationErrors`. Verify no bridge/encoder was created.

2. **Scene sorting:** Test that scenes are sorted by `start_time` regardless of manifest array order. Verify with a 3-scene manifest where scenes are [C, A, B] by start_time.

3. **FrameClock creation:** A manifest with fps=30 and total duration=10s creates a FrameClock with totalFrames=300.

4. **Camera state computation:** Mock a CameraPathPreset's `evaluate()`. For a frame at the midpoint of a scene, verify `evaluate` is called with `t=0.5`. Verify offset is applied to position.

5. **SlotSetup mapping:** Given a geometry with known slot positions and a manifest PlaneRef with scale=2.0, verify the resulting SlotSetup has doubled size.

6. **SlotSetup with overrides:** PlaneRef with `position_override: [1,2,3]` replaces geometry's default position.

7. **Image path resolution:** Test relative paths resolved against assetsDir. Test absolute paths passed through. Test protocol-prefixed paths passed through.

8. **Transition computation — crossfade:** For a crossfade at progress 0.5, verify multi-pass command: A at opacity 1.0, B at opacity 0.5.

9. **Transition computation — dip_to_black:** At progress 0.7 of a fade-out, verify single pass at opacity 0.3.

10. **Transition computation — cut:** At the boundary frame, verify single pass with the new scene.

11. **Gap frame detection:** Simulate a timeline with a gap. Verify the orchestrator identifies gap frames and does not generate a `RenderFrameCommand` for them.

12. **Scene lifecycle tracking:** Simulate a 3-scene timeline with one crossfade. Verify setup/teardown calls: scene 1 setup before frame 0, scene 2 setup before the crossfade starts, scene 1 teardown after the crossfade ends.

13. **Double render:** Create orchestrator, mock render to succeed, call `render()` twice — second call throws.

14. **Progress callback values:** Verify `frame`, `totalFrames`, `ratio`, `elapsedMs`, `estimatedRemainingMs`, `activeSceneIds` are populated correctly. Verify `activeSceneIds` is an array with correct entries for normal, transition, and gap frames.

15. **Cancellation:** Mock `onProgress` to return `false` at frame 5. Verify render throws `CANCELLED`, cleanup methods called.

16. **onProgress throws:** Mock `onProgress` to throw. Verify `CANCELLED` with original error as `cause`.

17. **Per-plane opacity warning:** Manifest with `PlaneRef.opacity: 0.5`. Verify warning in result.

18. **Pre-flight missing files:** Manifest with two missing image paths. Verify `SCENE_SETUP_FAILED` lists both paths. Verify no bridge/encoder was created.

19. **Geometry not found in geometryRegistry:** Registry mismatch. Verify `GEOMETRY_NOT_FOUND` thrown at D12.

20. **Camera not found in cameraRegistry:** Registry mismatch. Verify `CAMERA_NOT_FOUND` thrown at D12.

21. **SetupScene failure:** Mock `protocol.setupScene()` to return `{ success: false, slots: { floor: { status: 'error', error: 'timeout' } } }`. Verify `SCENE_SETUP_FAILED` with slot error details.

### Integration Tests: `test/integration/orchestrator.test.ts`

These launch real Puppeteer + FFmpeg. Use small viewports (320x240) and short durations (0.5-1s at 10fps = 5-10 frames) for speed.

22. **Single-scene end-to-end:** Register a mock "test" geometry with one slot. Create a solid-color test image. Render a 0.5s manifest at 10fps (5 frames). Verify output MP4 exists, ffprobe reports 320x240, H.264, ~5 frames. Verify `encoderResult.frameCount === 5`.

23. **Multi-scene with cut:** Two scenes, each 0.5s. Render 10 frames total. Verify output is ~1.0s.

24. **Multi-scene with crossfade:** Two scenes with 0.2s crossfade overlap. Verify total frame count accounts for the overlap.

25. **Gap frames:** Two scenes with a 0.3s gap. Verify frames in the gap are black (or at least that the output has the correct total frame count).

26. **Audio muxing:** Single scene with a short test WAV file. Verify final MP4 has both video and audio streams via ffprobe. Verify temp file is deleted.

27. **Missing image pre-flight:** Manifest references a non-existent image. Verify `SCENE_SETUP_FAILED` is thrown before any browser launch (verify by timing — should fail in <100ms — or by mocking bridge to detect it was never instantiated).

28. **Determinism (TC-06):** Render same manifest twice with `deterministic: true` on the encoder. Compare frame checksums of resulting MP4s.

29. **Cleanup on failure:** Provide an invalid FFmpeg path. Render should fail with `ENCODE_FAILED`. Verify no browser process remains.

30. **Cancellation:** Render with `onProgress` returning false at frame 2. Verify partial output deleted.

31. **renderFromFile convenience:** Write a valid manifest JSON to a temp file. Call `renderFromFile()`. Verify success.

32. **renderFromFile with missing file:** Call with non-existent path. Verify `MANIFEST_INVALID` with `FILE_NOT_FOUND`.

33. **Renderer info populated:** Verify `OrchestratorResult.rendererInfo.initialized === true` and `webglVersion` is non-empty.

### Performance Benchmark (TC-02, C-08)

34. **Benchmark:** Register a test geometry with 5 slots. Render a 60-second, 30fps manifest at 1920x1080 with software WebGL. Log total render time, average frame time, capture stats. Assert render time < 15 minutes on qualifying hardware.

### Relevant Testable Claims

- **TC-02:** Tests 22, 34 measure per-frame rendering time.
- **TC-04:** Tests 22-24 verify that an orchestrator using only geometry names and slot keys produces correct output.
- **TC-06:** Test 28 verifies deterministic output.
- **TC-07:** Tests 1-3 verify manifest validation catches errors before rendering.
- **TC-10:** Test 24 verifies crossfade transitions work.
- **TC-11:** All integration tests run with `gpu: false` (software WebGL).
- **TC-13:** Test 26 verifies audio synchronization.

## Integration Points

### Depends on

| Dependency | What OBJ-035 uses |
|---|---|
| **OBJ-009** (FrameClock + PuppeteerBridge) | `FrameClock.fromDuration()` to create the clock. `FrameClock.frames()` to drive the render loop. `PuppeteerBridge` constructor, `launch()`, `close()`, `page`, `evaluate()`, `isLaunched`. |
| **OBJ-011** (PageProtocol) | `PageProtocol` constructor, `initialize()`, `setupScene()`, `renderFrame()`, `teardownScene()`, `dispose()`. Protocol types: `RequiredCameraState`, `SceneSetupConfig`, `SlotSetup`, `RenderFrameCommand`, `RenderPass`, `PageInitConfig`, `SceneSetupResult`. |
| **OBJ-012** (FrameCapture) | `FrameCapture` constructor, `capture()`, `getStats()`. |
| **OBJ-013** (FFmpegEncoder) | `FFmpegEncoder` constructor, `start()`, `writeFrame()`, `finalize()`, `abort()`. `resolveFFmpegPath()`. |
| **OBJ-014** (AudioMuxer) | `muxAudio()` function for post-encoding audio mux. |
| **OBJ-016** (Manifest Loader) | `loadManifest()`, `loadManifestFromFile()`, `computeTotalDuration()`. |
| **OBJ-004** (Manifest Schema) | `ManifestRegistry`, `ManifestError`, `ManifestResult`, `Manifest`, `Scene`, `PlaneRef`, `Composition` types. `createRegistry()`. |
| **OBJ-005** (Geometry Types) | `GeometryRegistry`, `SceneGeometry`, `PlaneSlot` types. The orchestrator reads geometry data from the `geometryRegistry` config parameter. |
| **OBJ-006** (Camera Path Types) | `CameraPathRegistry`, `getCameraPath()`, `CameraPathPreset`, `CameraFrameState`, `CameraParams`. The orchestrator passes raw `CameraParams` to `preset.evaluate()` — the preset internally resolves easing names to functions. |

### Consumed by

| Downstream | How it uses OBJ-035 |
|---|---|
| **OBJ-036** (Scene Sequencer) | Depends on OBJ-035. May refactor the orchestrator's internal scene iteration into a dedicated `SceneSequencer` class. OBJ-035's public API does not change. |
| **OBJ-046** (CLI render command) | Calls `renderFromFile()` or creates `Orchestrator` directly. Formats `OrchestratorResult` for terminal output. |
| **OBJ-048** (CLI error formatting) | Consumes `OrchestratorError.validationErrors` for human-readable error display. |
| **OBJ-058** (Test harness for tuning) | Creates `Orchestrator` programmatically to render test clips for Director Agent review. |
| **OBJ-073** (Docker integration) | Runs the orchestrator in a container environment with software WebGL. |
| **OBJ-074** (Performance benchmarking) | Benchmarks `Orchestrator.render()` for TC-02 compliance. |
| **OBJ-077** (End-to-end integration) | Full pipeline integration test: manifest -> orchestrator -> MP4. |
| **OBJ-082** (Parallel rendering) | May extend the orchestrator to split frame ranges across multiple instances. |
| **OBJ-083** (Extended CLI) | Additional CLI features built on the orchestrator. |

### File Placement

```
depthkit/
  src/
    engine/
      orchestrator.ts          # NEW — Orchestrator class, OrchestratorConfig,
                               #       OrchestratorResult, OrchestratorError,
                               #       RenderProgress, renderFromFile()
  test/
    unit/
      orchestrator.test.ts     # NEW — unit tests with mocked dependencies
    integration/
      orchestrator.test.ts     # NEW — end-to-end integration tests
```

## Open Questions

### OQ-A: Should the orchestrator retry failed texture loads?

If `protocol.setupScene()` returns `success: false` for one slot (e.g., network timeout on an HTTP texture), should the orchestrator retry? Current decision: no — fail fast. Retries add complexity and the production path uses local `file://` textures which don't fail transiently. Revisit if HTTP texture sources become common.

### OQ-B: Should the orchestrator support rendering a subset of frames?

A `frameRange?: { start: number; end: number }` config option would enable rendering specific segments for debugging or parallel rendering (OBJ-082). Currently deferred — OBJ-082 depends on OBJ-035 and may add this.

### OQ-C: Should the orchestrator validate audio file existence in pre-flight?

Currently, audio file issues surface at the muxing stage (OBJ-014). Pre-flight validation would catch missing audio files earlier. Low priority — audio is typically generated by the pipeline before the orchestrator runs.

### OQ-D: How should the orchestrator handle scenes with partial texture failures?

Current decision: treat any texture load failure (`SceneSetupResult.success === false`) as a fatal error. Alternative: render with magenta fallback meshes (which OBJ-011 creates for failed textures) and include a warning. This would be useful for development but wrong for production. Could be gated behind a `tolerateTextureFailures?: boolean` config option. Deferred.

### OQ-E: Per-plane opacity support

`PlaneRef.opacity` exists in the manifest schema (OBJ-004) but `SlotSetup` (OBJ-011) has no per-slot opacity field. To support per-plane opacity, OBJ-011's `SlotSetup` would need an `opacity?: number` field, and the page handler would need to set `material.opacity` per mesh during scene setup. This is a cross-objective change. Deferred to a future objective that extends both OBJ-011 and OBJ-035 together.
