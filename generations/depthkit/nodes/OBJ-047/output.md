# Specification: OBJ-047 — Library API

## Summary

OBJ-047 delivers the importable programmatic interface for depthkit (`src/index.ts`) — the public entry point for Node.js consumers such as the n8n HTTP endpoint (OBJ-055) and any other programmatic caller. It wraps the Orchestrator (OBJ-035) with a higher-level API that handles registry initialization internally, supports resolution/fps overrides, and provides rich event hooks (`onFrameRendered`, `onSceneStart`, `onSceneEnd`, `onComplete`, `onError`) beyond the Orchestrator's single `onProgress` callback. It also relocates `initRegistries()` and `RegistryBundle` from `src/cli/registry-init.ts` (OBJ-046) to a shared `src/registry.ts` module so both the CLI and Library API consume the same registry initialization without cross-layer imports.

## Interface Contract

### Module: `src/index.ts`

The package's main entry point. All public types and functions are re-exported from here. The `package.json` `"main"` (or `"exports"`) field points to the compiled output of this module.

```typescript
// -- Re-exports (public surface) --------------------------------

// From OBJ-035 -- callers who need low-level access
export { Orchestrator, OrchestratorError } from './engine/orchestrator.js';
export type {
  OrchestratorConfig,
  OrchestratorResult,
  OrchestratorErrorCode,
  RenderProgress,
} from './engine/orchestrator.js';

// From OBJ-013 -- encoding types used in RenderOptions
export type { H264Preset } from './engine/ffmpeg-encoder.js';

// From OBJ-012 -- capture types used in RenderOptions
export type { CaptureStrategy } from './engine/frame-capture.js';

// From this module -- the high-level API
export { render, renderFile };
export type {
  RenderOptions,
  RenderHooks,
  RenderOverrides,
  SceneEvent,
  FrameEvent,
  RenderResult,
};

// From shared registry
export { initRegistries } from './registry.js';
export type { RegistryBundle } from './registry.js';

// From manifest schema -- needed by callers constructing manifests
// or inspecting validation errors
export type { Manifest, ManifestError } from './manifest/schema.js';

// Note: Types from OBJ-035's result sub-components (CaptureStats,
// FFmpegEncoderResult, AudioMuxerResult, RendererInfo) are accessible
// via RenderResult.raw but are not re-exported in V1. Consumers
// needing these types can import them directly from their source
// modules (e.g., './engine/frame-capture.js').
```

### Module: `src/registry.ts` — Shared Registry Initialization

Relocated from OBJ-046's `src/cli/registry-init.ts`. Both the CLI and Library API import from here. OBJ-046's `src/cli/registry-init.ts` becomes a one-line re-export: `export { initRegistries, type RegistryBundle } from '../registry.js';`

```typescript
import type { ManifestRegistry } from './manifest/schema.js';
import type { GeometryRegistry } from './scenes/geometries/types.js';
import type { CameraPathRegistry } from './camera/types.js';

/**
 * Registry bundle containing all three registries needed by the
 * orchestrator. Identical to the type defined in OBJ-046's D3.
 */
export interface RegistryBundle {
  manifestRegistry: ManifestRegistry;
  geometryRegistry: GeometryRegistry;
  cameraRegistry: CameraPathRegistry;
}

/**
 * Populates and returns all three registries.
 *
 * Synchronous. All geometry and camera modules are statically imported
 * at the top of this module -- their registerGeometry() side effects
 * execute at module load time. This function:
 *
 * 1. Calls getGeometryRegistry() to retrieve the frozen geometry registry.
 * 2. Constructs CameraPathRegistry from camera preset barrel imports.
 * 3. Creates ManifestRegistry via createRegistry() and populates it
 *    by converting each SceneGeometry -> GeometryRegistration and
 *    CameraPathPreset -> CameraRegistration.
 * 4. Returns the RegistryBundle.
 *
 * Idempotent -- subsequent calls return equivalent registries.
 */
export function initRegistries(): RegistryBundle;
```

### Module: `src/api.ts` — Library API Implementation

The core Library API logic. Separated from `src/index.ts` to keep the entry point clean (re-exports only).

```typescript
import type { OrchestratorResult, RenderProgress } from './engine/orchestrator.js';
import type { H264Preset } from './engine/ffmpeg-encoder.js';
import type { CaptureStrategy } from './engine/frame-capture.js';

// ────────────────────────────────────────────
// Configuration Types
// ────────────────────────────────────────────

/**
 * Resolution and timing overrides applied to the manifest
 * before rendering begins. These override the manifest's
 * composition fields without modifying the source manifest object.
 */
export interface RenderOverrides {
  /** Override composition.width. Must be a positive even integer. */
  width?: number;
  /** Override composition.height. Must be a positive even integer. */
  height?: number;
  /** Override composition.fps. Must be 1-120. */
  fps?: number;
}

/**
 * Event data emitted when a scene starts or ends rendering.
 */
export interface SceneEvent {
  /** The scene's `id` from the manifest. */
  sceneId: string;
  /** Zero-based index of this scene in the sorted scene array. */
  sceneIndex: number;
  /** Total number of scenes in the manifest. */
  totalScenes: number;
  /** The scene's geometry name. */
  geometry: string;
  /** The scene's camera preset name. */
  camera: string;
  /** The scene's start time in seconds. */
  startTime: number;
  /** The scene's duration in seconds. */
  duration: number;
}

/**
 * Event data emitted after each frame is rendered.
 * Superset of OrchestratorResult's RenderProgress with additional
 * convenience fields.
 */
export interface FrameEvent {
  /** Current frame number (zero-indexed). */
  frame: number;
  /** Total number of frames. */
  totalFrames: number;
  /** Progress as a percentage [0, 100]. Computed as ratio * 100. */
  percent: number;
  /** Progress ratio [0, 1]. */
  ratio: number;
  /** Elapsed wall-clock time in milliseconds. */
  elapsedMs: number;
  /** Estimated remaining time in milliseconds. */
  estimatedRemainingMs: number;
  /** Rendered frames per second throughput. */
  throughputFps: number;
  /** Scene IDs active for this frame. */
  activeSceneIds: string[];
}

/**
 * Event hooks for observing the render lifecycle.
 *
 * All hooks are optional. All hooks are invoked synchronously
 * within the render loop -- long-running hooks slow rendering.
 * Hooks must not throw -- if they do, the render is cancelled
 * (same behavior as OrchestratorConfig.onProgress throwing).
 *
 * Hooks are NOT called on validation failure -- only once
 * rendering begins.
 */
export interface RenderHooks {
  /**
   * Called after each frame is rendered, captured, and written to FFmpeg.
   *
   * Return `false` to cancel the render. Returning anything else
   * (including undefined/void) continues rendering.
   *
   * This replaces OrchestratorConfig.onProgress for Library API callers.
   */
  onFrameRendered?: (event: FrameEvent) => boolean | void;

  /**
   * Called when a scene begins rendering for the first time.
   * Specifically: called on the first frame where this scene's ID
   * appears in activeSceneIds and was not in the previous frame's
   * activeSceneIds.
   *
   * For the first scene, this fires on frame 0.
   * During crossfade transitions, the incoming scene's onSceneStart
   * fires on the first overlap frame.
   */
  onSceneStart?: (event: SceneEvent) => void;

  /**
   * Called when a scene finishes rendering its last frame.
   * Specifically: called on the first frame where this scene's ID
   * no longer appears in activeSceneIds but was in the previous frame's.
   *
   * For the last scene, this fires after the final frame (during
   * result assembly, not mid-loop).
   */
  onSceneEnd?: (event: SceneEvent) => void;

  /**
   * Called after render completes successfully, just before the
   * promise resolves. Receives the full result.
   *
   * This is a convenience for fire-and-forget patterns. The same
   * result is available from the resolved promise.
   */
  onComplete?: (result: RenderResult) => void;

  /**
   * Called when the render fails, just before the promise rejects.
   * Receives the OrchestratorError.
   *
   * This is a convenience for fire-and-forget patterns. The same
   * error is available from the rejected promise.
   */
  onError?: (error: Error) => void;
}

/**
 * Full result returned by render() and renderFile().
 * Wraps OrchestratorResult with additional convenience fields.
 */
export interface RenderResult {
  /** Absolute path to the output MP4 file. */
  outputPath: string;
  /** Total frames rendered. */
  totalFrames: number;
  /**
   * Video content duration in seconds (totalFrames / fps).
   * This is the playback length of the output video,
   * NOT the wall-clock time the render took.
   */
  durationSeconds: number;
  /** Total wall-clock time for the entire operation (ms). */
  totalDurationMs: number;
  /** Wall-clock time for the frame render loop only (ms). */
  renderDurationMs: number;
  /** Average milliseconds per frame. */
  averageFrameMs: number;
  /**
   * Validation warnings (non-blocking). Each string is the
   * message field from a ManifestError with severity "warning".
   */
  warnings: string[];
  /** Whether audio was muxed into the output. */
  hasAudio: boolean;
  /** The underlying OrchestratorResult for callers needing full detail. */
  raw: OrchestratorResult;
}

/**
 * Options for the render() function.
 */
export interface RenderOptions {
  /**
   * The manifest to render. Accepts:
   * - A manifest object (validated before rendering).
   * - A JSON string (parsed via JSON.parse(), then validated).
   *
   * For file paths, use renderFile() instead.
   */
  manifest: unknown;

  /**
   * Output file path for the final MP4.
   * Parent directory must exist. File is overwritten if it exists.
   */
  outputPath: string;

  /**
   * Base directory for resolving relative image paths.
   * Default: process.cwd()
   */
  assetsDir?: string;

  /**
   * Resolution and timing overrides. Applied to the manifest's
   * composition before rendering, without modifying the input object.
   */
  overrides?: RenderOverrides;

  /**
   * Event hooks for observing the render lifecycle.
   */
  hooks?: RenderHooks;

  /**
   * Enable GPU-accelerated WebGL. Default: false (software/SwiftShader).
   */
  gpu?: boolean;

  /**
   * H.264 encoding preset. Default: 'medium'.
   */
  encodingPreset?: H264Preset;

  /**
   * Constant Rate Factor (0-51). Default: 23.
   */
  crf?: number;

  /**
   * Capture strategy for pixel extraction from headless Chromium.
   * Default: 'viewport-png'.
   */
  captureStrategy?: CaptureStrategy;

  /**
   * Path to FFmpeg binary. Default: auto-resolved.
   */
  ffmpegPath?: string;

  /**
   * Path to Chromium executable. Default: Puppeteer's bundled Chromium.
   */
  chromiumPath?: string;

  /**
   * Forward headless browser console to Node stdout. Default: false.
   */
  debug?: boolean;

  /**
   * Skip manifest validation. Default: false.
   * WARNING: Only for testing/debugging.
   */
  skipValidation?: boolean;
}

// ────────────────────────────────────────────
// Primary Functions
// ────────────────────────────────────────────

/**
 * Render a depthkit manifest to an MP4 video file.
 *
 * This is the primary programmatic entry point. It handles:
 * 1. Registry initialization (geometry, camera, manifest registries).
 * 2. Manifest parsing (JSON strings are parsed automatically).
 * 3. Manifest validation (C-10).
 * 4. Resolution/fps override application.
 * 5. Orchestrator construction and execution.
 * 6. Event hook dispatch (onFrameRendered, onSceneStart, onSceneEnd,
 *    onComplete, onError).
 *
 * Registries are initialized once on first call and cached for
 * subsequent calls within the same process.
 *
 * @param options - Render configuration.
 * @returns RenderResult on success.
 * @throws OrchestratorError on any failure (after calling onError hook).
 */
export async function render(options: RenderOptions): Promise<RenderResult>;

/**
 * Render a manifest from a JSON file path.
 *
 * Convenience wrapper: reads and parses the file, then delegates to
 * render().
 *
 * If `options.assetsDir` is not provided, it defaults to
 * `path.dirname(manifestPath)` (the manifest file's parent directory),
 * overriding the `process.cwd()` default used by `render()`.
 *
 * @param manifestPath - Path to the manifest JSON file.
 * @param options - Render configuration (manifest field is not present;
 *                  the file contents are used instead).
 * @returns RenderResult on success.
 * @throws OrchestratorError on file read failure or any render failure.
 */
export async function renderFile(
  manifestPath: string,
  options: Omit<RenderOptions, 'manifest'>,
): Promise<RenderResult>;
```

## Design Decisions

### D1: Library API Wraps Orchestrator, Does Not Extend It

**Decision:** `render()` and `renderFile()` are standalone async functions that internally construct an `Orchestrator`, call `render()`, and map the result. They do not subclass or modify `Orchestrator`.

**Rationale:** The Orchestrator (OBJ-035) is a well-defined, single-responsibility class: one instance per render, no reuse. The Library API adds ergonomics (registry auto-init, event hooks, overrides, simplified types) without changing the rendering pipeline. Wrapping keeps concerns separated: OBJ-035 owns the rendering invariants (C-02, C-03, C-05), OBJ-047 owns the public DX surface.

### D2: Registry Auto-Initialization with Module-Level Cache

**Decision:** `render()` calls `initRegistries()` internally. The result is cached at module scope in `src/api.ts` (a `let registryBundle: RegistryBundle | null = null` variable, populated on first call). Subsequent calls reuse the cached bundle.

**Why not require callers to pass registries?** The n8n endpoint (OBJ-055) and other consumers should not need to understand the registry system. The whole point of OBJ-047 is to hide internal wiring. Callers who need custom registries (e.g., with additional geometries) can use the `Orchestrator` directly -- it is re-exported.

**Why cache?** `initRegistries()` is idempotent (OBJ-046 D3), but it performs static imports and registry iteration. Caching avoids redundant work in long-running server processes (OBJ-055) that render multiple videos.

**Thread safety:** Node.js is single-threaded. No mutex needed. Two concurrent `render()` calls will both check the cache, at most one will initialize -- the second will find the result already populated. The underlying `getGeometryRegistry()` from OBJ-005 locks on first read, so double-init is safe.

### D3: Event Hooks Derived from onProgress State Tracking

**Decision:** The Library API implements `onSceneStart` and `onSceneEnd` by tracking `activeSceneIds` across frames.

**Internal `onProgress` wiring rule:** An internal `onProgress` callback is wired to the Orchestrator whenever at least one of `onFrameRendered`, `onSceneStart`, or `onSceneEnd` is provided. If only `onComplete` and/or `onError` are provided (no frame-level hooks), `onProgress` is left `undefined` on the `OrchestratorConfig` -- these hooks are invoked from the promise resolution/rejection path, not the frame loop.

**Pre-computation step:** Before the render loop, `render()` constructs a `Map<string, SceneEvent>` keyed by scene ID from the validated manifest's `scenes` array (sorted by `start_time`). Each `SceneEvent` is pre-computed: `sceneIndex` is the position in the sorted array, `totalScenes` is the array length, and `geometry`/`camera`/`startTime`/`duration` are read from the scene definition. When `onSceneStart` or `onSceneEnd` fires, the pre-computed `SceneEvent` for that scene ID is passed to the hook.

**State tracking algorithm:**

1. Before the render loop, initialize `previousActiveSceneIds: string[] = []`.
2. Wire an internal `onProgress` callback to the Orchestrator (if needed per the wiring rule above).
3. On each `onProgress` invocation:
   a. Compute newly active scene IDs: `current.activeSceneIds.filter(id => !previousActiveSceneIds.includes(id))`.
   b. Compute newly inactive scene IDs: `previousActiveSceneIds.filter(id => !current.activeSceneIds.includes(id))`.
   c. For each newly active ID: invoke `hooks.onSceneStart` (if provided) with the pre-computed `SceneEvent` for that scene ID.
   d. For each newly inactive ID: invoke `hooks.onSceneEnd` (if provided) with the pre-computed `SceneEvent` for that scene ID.
   e. Invoke `hooks.onFrameRendered` (if provided) with the `FrameEvent`.
   f. Update `previousActiveSceneIds = [...current.activeSceneIds]`.
   g. Return the value from `hooks.onFrameRendered` (for cancellation). If `onFrameRendered` is not provided, return `undefined` (continue rendering).
4. After the render loop completes: fire `onSceneEnd` for any scenes still in `previousActiveSceneIds` (handles the last scene, which ends when the loop finishes rather than when a subsequent frame removes it).

### D4: Resolution Overrides Applied via Deep Copy

**Decision:** When `overrides` is provided, `render()` creates a deep copy of the manifest object (after validation) and mutates the copy's `composition.width`, `composition.height`, and/or `composition.fps`. The original input object is never mutated.

**Override validation:**
- `width` and `height` must be positive even integers (H.264 requires even dimensions). If odd, negative, or zero, the Library API throws `OrchestratorError` with code `MANIFEST_INVALID` and a descriptive message (e.g., "Override width must be a positive even integer, got 1281").
- `fps` must be between 1 and 120 inclusive. If out of range, throws `OrchestratorError` with code `MANIFEST_INVALID`.
- Overrides are applied after Zod validation but before Orchestrator construction. The Orchestrator receives the already-overridden manifest.

**Rationale:** OBJ-046 applies overrides by mutating the manifest object directly (OBJ-046 D2). This is acceptable for a CLI (the object is created from file and discarded). The Library API must not mutate input -- callers may reuse the manifest object across multiple renders with different overrides.

### D5: RenderResult Simplifies OrchestratorResult

**Decision:** `RenderResult` is a flattened, consumer-friendly subset of `OrchestratorResult`. It includes the most commonly needed fields at the top level and preserves the full `OrchestratorResult` in `raw` for callers who need capture stats, encoder details, or renderer info.

The `warnings` field maps `OrchestratorResult.warnings` (array of `ManifestError`) to `string[]` by extracting each error's `message` field. This avoids requiring Library API consumers to import `ManifestError` for simple warning display.

**Rationale:** n8n workflows and HTTP endpoint consumers need output path, duration, and timing -- not capture strategy stats. The `raw` escape hatch preserves full detail without polluting the primary interface.

### D6: Manifest Input — String Parsing Strategy

**Decision:** `RenderOptions.manifest` accepts `unknown`. If it is a `string`, it is unconditionally passed through `JSON.parse()`:
- If parsing succeeds, the parsed result is used as the manifest object.
- If parsing fails, `render()` throws `OrchestratorError` with code `MANIFEST_INVALID`, with the `SyntaxError` as `cause`. If the original string does not start with `{` or `[` (after trimming), the error message appends: `"Did you mean to use renderFile()?"`.

If `manifest` is not a string, it is passed directly to `loadManifest()` (OBJ-016) for Zod validation.

**Why not accept file paths in `manifest`?** Separating file-based rendering into `renderFile()` eliminates ambiguity. The hint text guides callers who accidentally pass a file path.

**Rationale:** HTTP endpoints receive JSON request bodies as strings or parsed objects depending on middleware configuration. Accepting both covers common integration patterns without requiring the caller to pre-parse.

### D7: onComplete and onError Are Supplementary to the Promise

**Decision:** `render()` always returns a promise. `onComplete` is called just before the promise resolves; `onError` is called just before the promise rejects. These hooks do NOT replace the promise -- the promise is the primary result mechanism.

If `onComplete` or `onError` throws, the thrown error is logged to `console.error` and swallowed -- it does not alter the render result or the rejection.

**Rationale:** Fire-and-forget patterns in n8n workflows benefit from callbacks. Promise-based callers use `await`. Both work. Hook errors must not corrupt the render result.

### D8: Shared Registry Module Location (Cross-Objective Modification)

**Decision:** `initRegistries()` and `RegistryBundle` are defined in `src/registry.ts`. OBJ-046's `src/cli/registry-init.ts` is updated to re-export from `src/registry.ts` to maintain backward compatibility.

**Cross-objective impact:** This relocation modifies OBJ-046's file structure. OBJ-046 is `status: "verified"`. OBJ-046's `src/cli/registry-init.ts` becomes a re-export shim:
```typescript
export { initRegistries, type RegistryBundle } from '../registry.js';
```
OBJ-046's public interface and behavior are unchanged -- only the file that holds the source implementation moves. The CLI's `render` and `validate` commands continue to import from `src/cli/registry-init.ts` and function identically.

**Rationale:** Registry initialization is consumed by both the CLI (OBJ-046) and the Library API (OBJ-047). Placing it in `src/cli/` creates a layering violation where the library API imports from the CLI layer. `src/registry.ts` is the natural shared location. The re-export shim ensures zero behavioral change for OBJ-046.

### D9: No Engine/Builder Pattern in V1

**Decision:** The Library API is two stateless async functions (`render()`, `renderFile()`). There is no `createEngine()` or `DepthkitEngine` class.

**Rationale:** A reusable engine class would pre-initialize registries and hold configuration defaults. This is marginally useful but adds lifecycle semantics (disposal? browser pooling?) that don't exist yet. The module-level registry cache (D2) achieves the main benefit. An engine class can be added later without breaking the function-based API.

### D10: FrameEvent.percent as Convenience

**Decision:** `FrameEvent` includes both `ratio` (0-1, matching `RenderProgress.ratio`) and `percent` (0-100, computed as `ratio * 100`). Percent is a convenience for progress reporting in HTTP responses and logs.

## Acceptance Criteria

### Core Rendering

- [ ] **AC-01:** `render()` with a valid manifest object and `outputPath` produces a valid MP4 file. The returned `RenderResult.outputPath` points to the file. `ffprobe` confirms H.264 encoding.
- [ ] **AC-02:** `renderFile()` with a valid manifest JSON file path produces the same result as reading the file, parsing it, and calling `render()`.
- [ ] **AC-03:** `render()` with a JSON string as `manifest` parses it and renders successfully.
- [ ] **AC-04:** The manifest input object is not mutated, even when `overrides` are provided.

### Registry Auto-Initialization

- [ ] **AC-05:** `render()` works without the caller constructing or passing any registries. All built-in geometries and camera presets are available.
- [ ] **AC-06:** Calling `render()` twice in the same process does not re-initialize registries. The second call reuses the cached `RegistryBundle`.
- [ ] **AC-07:** `initRegistries()` is exported from `src/index.ts` for callers who need direct registry access.

### Overrides

- [ ] **AC-08:** `render()` with `overrides: { width: 1280, height: 720 }` produces a 1280x720 MP4 regardless of the manifest's `composition.width` and `composition.height`.
- [ ] **AC-09:** `render()` with `overrides: { fps: 24 }` produces a 24fps MP4 regardless of the manifest's `composition.fps`.
- [ ] **AC-10:** `render()` with `overrides: { width: 1281 }` (odd number) throws `OrchestratorError` with code `MANIFEST_INVALID` and a message mentioning even dimensions.
- [ ] **AC-11:** `render()` with `overrides: { fps: 0 }` or `overrides: { fps: 200 }` throws `OrchestratorError` with code `MANIFEST_INVALID`.

### Event Hooks

- [ ] **AC-12:** `hooks.onFrameRendered` is called once per frame. The `frame` field increments from 0 to `totalFrames - 1`. `percent` reaches 100 on the last frame.
- [ ] **AC-13:** `hooks.onFrameRendered` returning `false` cancels the render. `render()` rejects with `OrchestratorError` code `CANCELLED`.
- [ ] **AC-14:** `hooks.onSceneStart` fires on the first frame where a scene becomes active. For a 2-scene manifest with a cut transition, `onSceneStart` fires twice: once for scene 1 on frame 0, once for scene 2 on the first frame of scene 2.
- [ ] **AC-15:** `hooks.onSceneEnd` fires on the first frame after a scene is no longer active. For a 2-scene manifest with a cut transition, `onSceneEnd` fires for scene 1 on the first frame of scene 2.
- [ ] **AC-16:** `hooks.onSceneEnd` fires for the last scene after the render loop completes (not during the loop), since no subsequent frame removes it from `activeSceneIds`.
- [ ] **AC-17:** `hooks.onSceneStart` fires correctly during crossfade transitions: the incoming scene's event fires on the first overlap frame.
- [ ] **AC-18:** `hooks.onComplete` is called with the `RenderResult` just before the promise resolves.
- [ ] **AC-19:** `hooks.onError` is called with the `OrchestratorError` just before the promise rejects.
- [ ] **AC-20:** If `hooks.onComplete` throws, the exception is logged to `console.error` and swallowed -- the promise still resolves with the result.
- [ ] **AC-21:** If `hooks.onError` throws, the exception is logged to `console.error` and swallowed -- the promise still rejects with the original error.
- [ ] **AC-22:** If no hooks are provided, `render()` works identically (hooks are optional).

### RenderResult

- [ ] **AC-23:** `RenderResult.durationSeconds` equals `totalFrames / fps` (video content duration, not wall-clock time).
- [ ] **AC-24:** `RenderResult.warnings` is a `string[]` containing the messages from `OrchestratorResult.warnings`.
- [ ] **AC-25:** `RenderResult.hasAudio` is `true` when the manifest has `composition.audio`, `false` otherwise.
- [ ] **AC-26:** `RenderResult.raw` is the full `OrchestratorResult` from the Orchestrator.

### Error Handling

- [ ] **AC-27:** `render()` with an invalid manifest throws `OrchestratorError` with code `MANIFEST_INVALID`, just as the Orchestrator does. No browser is launched.
- [ ] **AC-28:** `renderFile()` with a non-existent file path throws `OrchestratorError` with code `MANIFEST_INVALID`.
- [ ] **AC-29:** All `OrchestratorError` codes from OBJ-035 are preserved -- the Library API does not wrap or alter error codes.

### Package Exports

- [ ] **AC-30:** `import { render, renderFile, Orchestrator, OrchestratorError, initRegistries } from 'depthkit'` works. All five are accessible.
- [ ] **AC-31:** `import type { RenderOptions, RenderResult, RenderHooks, FrameEvent, SceneEvent, Manifest, RegistryBundle, ManifestError, H264Preset, CaptureStrategy } from 'depthkit'` works. All types are accessible.

### Shared Registry

- [ ] **AC-32:** `src/registry.ts` exports `initRegistries` and `RegistryBundle`. `src/cli/registry-init.ts` re-exports from `src/registry.ts`.
- [ ] **AC-33:** The CLI (`depthkit render` and `depthkit validate` commands) continues to work after the registry relocation. Both commands still import from `src/cli/registry-init.ts` and behave identically.

### renderFile Specifics

- [ ] **AC-34:** `renderFile()` without `assetsDir` in options defaults to `path.dirname(manifestPath)` as the base directory for resolving relative image paths. A manifest at `/tmp/project/manifest.json` referencing `./images/bg.png` resolves to `/tmp/project/images/bg.png`.

## Edge Cases and Error Handling

### Manifest Input

| Scenario | Expected Behavior |
|---|---|
| `manifest` is a valid object | Passed to `loadManifest()`. Rendered. |
| `manifest` is a valid JSON string | Parsed with `JSON.parse()`. Passed to `loadManifest()`. Rendered. |
| `manifest` is an invalid JSON string (e.g., `"not json {"`) | `JSON.parse()` throws `SyntaxError`. Rethrown as `OrchestratorError` code `MANIFEST_INVALID` with the `SyntaxError` as `cause`. |
| `manifest` is a string that looks like a file path (e.g., `"./manifest.json"`) | `JSON.parse()` fails. `OrchestratorError` code `MANIFEST_INVALID`. Error message appends: "Did you mean to use renderFile()?" (because the string does not start with `{` or `[` after trimming). |
| `manifest` is null/undefined/number | Passed to `loadManifest()` which rejects it. `MANIFEST_INVALID`. |

### Overrides

| Scenario | Expected Behavior |
|---|---|
| `overrides: {}` (empty) | No overrides applied. Manifest values used as-is. |
| `overrides: { width: 1920 }` with manifest width already 1920 | No-op. No error. |
| `overrides: { width: 1280 }` only (no height) | Only width overridden. Height from manifest. Aspect ratio changes. |
| `overrides: { width: -100 }` | `MANIFEST_INVALID`: "Override width must be a positive even integer." |
| `overrides: { fps: 1 }` | Valid (minimum). Renders at 1fps. |
| `overrides: { fps: 120 }` | Valid (maximum). Renders at 120fps. |

### Hook Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `onFrameRendered` throws on frame 5 | Orchestrator's internal `onProgress` treats thrown exceptions as cancellation. `render()` rejects with `CANCELLED`, cause is the thrown error. `onError` is called before rejection. |
| Single-scene manifest | `onSceneStart` fires once (frame 0). `onSceneEnd` fires once (after render loop). |
| Gap frames between scenes | During gap frames, `activeSceneIds` is empty. If the previous frame had a scene, `onSceneEnd` fires for it. When the next scene starts, `onSceneStart` fires. |
| Two `onSceneStart` in quick succession (crossfade) | Both fire: outgoing scene's `onSceneStart` already fired previously; incoming scene's `onSceneStart` fires on first overlap frame. No `onSceneEnd` for outgoing until overlap ends. |
| `hooks` is undefined | All hooks skipped. Internal `onProgress` is not wired. |
| `hooks` with only `onComplete` (no frame-level hooks) | Internal `onProgress` is not wired. `onComplete` fires after render. |
| `hooks` with only `onSceneStart` (needs frame tracking but no onFrameRendered) | Internal `onProgress` IS wired (to track `activeSceneIds` changes). `onFrameRendered` is not called since it's not provided. |

### Concurrent Renders

| Scenario | Expected Behavior |
|---|---|
| Two `render()` calls in parallel | Each creates its own Orchestrator. Both share the cached registry bundle. Both run independently. Both complete or fail independently. |
| `render()` called while a previous render is still running | Works. Each Orchestrator is independent (OBJ-035 D10). |

### renderFile Specifics

| Scenario | Expected Behavior |
|---|---|
| File exists, valid JSON, valid manifest | Renders successfully. |
| File exists, invalid JSON | `MANIFEST_INVALID` with JSON parse error. |
| File exists, valid JSON, invalid manifest | `MANIFEST_INVALID` with validation errors. |
| File doesn't exist | `MANIFEST_INVALID` with `FILE_NOT_FOUND`. |
| `assetsDir` not provided | Defaults to `path.dirname(manifestPath)`, not `process.cwd()`. |

## Test Strategy

### Unit Tests: `test/unit/api.test.ts`

Tests the Library API logic with a mocked Orchestrator. Mock `initRegistries()` to return a stub bundle. Mock the `Orchestrator` class to return predetermined results.

1. **Basic render:** Mock orchestrator to succeed. Verify `RenderResult` fields map correctly from `OrchestratorResult`.

2. **JSON string manifest:** Pass a JSON string. Verify it's parsed and passed to the Orchestrator as an object.

3. **Invalid JSON string:** Pass `"not json {"`. Verify `MANIFEST_INVALID` with `SyntaxError` in `cause`.

4. **Non-JSON string (file path hint):** Pass `"./manifest.json"`. Verify `MANIFEST_INVALID` message includes "Did you mean to use renderFile()?"

5. **JSON string starting with `[`:** Pass `"[1,2,3]"`. Verify `JSON.parse` succeeds but Zod rejects the array. `MANIFEST_INVALID` without the file path hint (since the string started with `[`).

6. **Overrides applied:** Pass `overrides: { width: 1280, height: 720, fps: 24 }`. Verify the manifest passed to the Orchestrator has these values. Verify original input object unchanged.

7. **Odd width rejected:** `overrides: { width: 1281 }`. Verify `MANIFEST_INVALID`.

8. **FPS out of range:** `overrides: { fps: 0 }`. Verify `MANIFEST_INVALID`. Also test `fps: 121`.

9. **Registry caching:** Call `render()` twice (mocked). Verify `initRegistries()` is called once.

10. **onFrameRendered wiring:** Verify the mock Orchestrator receives an `onProgress` callback. Simulate 3 progress calls. Verify `onFrameRendered` called 3 times with correct `FrameEvent` (including `percent`).

11. **onFrameRendered cancellation:** Mock `onFrameRendered` to return `false`. Verify the value is propagated through the internal `onProgress` return.

12. **onSceneStart detection:** Simulate progress calls with changing `activeSceneIds`: `['s1'] -> ['s1'] -> ['s1','s2'] -> ['s2']`. Verify `onSceneStart` called twice: once for `s1` (frame 0), once for `s2` (frame 2).

13. **onSceneEnd detection:** Same sequence as above. Verify `onSceneEnd` called for `s1` on frame 3 (when `s1` leaves `activeSceneIds`).

14. **Last scene onSceneEnd:** Simulate 3 frames all with `['s1']`. After render completes, verify `onSceneEnd` called for `s1`.

15. **Gap frame transitions:** `['s1'] -> [] -> ['s2']`. Verify `onSceneEnd` for `s1` on frame 1, `onSceneStart` for `s2` on frame 2.

16. **onComplete called:** Mock successful render. Verify `onComplete` called with `RenderResult`.

17. **onError called:** Mock failed render. Verify `onError` called with the error.

18. **onComplete throws swallowed:** Mock `onComplete` to throw. Verify `render()` still resolves. Verify `console.error` called.

19. **onError throws swallowed:** Mock `onError` to throw. Verify `render()` still rejects with original error. Verify `console.error` called.

20. **No hooks:** No `hooks` in options. Verify Orchestrator `onProgress` is `undefined`.

21. **Only onSceneStart hook:** Verify internal `onProgress` is wired (to track scenes), but `onFrameRendered` is not called.

22. **Only onComplete hook:** Verify internal `onProgress` is NOT wired.

23. **RenderResult.warnings mapping:** `OrchestratorResult.warnings` with two `ManifestError` objects. Verify `RenderResult.warnings` is `['msg1', 'msg2']`.

24. **RenderResult.hasAudio:** Verify true when `audioResult` is non-null, false when null.

25. **SceneEvent pre-computation:** Verify that `SceneEvent` objects contain correct `sceneIndex`, `totalScenes`, `geometry`, `camera`, `startTime`, `duration` from the manifest.

### Integration Tests: `test/integration/api.test.ts`

Real rendering with small viewports. Short manifests (320x240, 0.5s at 10fps).

26. **End-to-end render():** Create a test manifest object with one scene. Call `render()`. Verify MP4 exists and plays.

27. **End-to-end renderFile():** Write manifest to temp file. Call `renderFile()`. Verify MP4 exists.

28. **renderFile default assetsDir:** Manifest in `/tmp/test/manifest.json` with images relative to `/tmp/test/images/`. Verify images resolve correctly without passing `assetsDir`.

29. **Override resolution:** Render with `overrides: { width: 160, height: 120 }`. Verify `ffprobe` reports 160x120.

30. **Hook invocation order:** Render a 2-scene manifest. Collect all hook calls in order. Verify: `onSceneStart(s1)` -> N x `onFrameRendered` -> `onSceneStart(s2)` -> ... -> `onSceneEnd(s1)` -> ... -> `onSceneEnd(s2)` -> `onComplete`.

31. **Cancellation via hook:** `onFrameRendered` returns `false` after 3 frames. Verify `render()` rejects with `CANCELLED`. Verify `onError` is called.

32. **Package exports:** `import { render, renderFile, Orchestrator, OrchestratorError, initRegistries } from '../src/index.js'` -- verify all are defined.

33. **Concurrent renders:** Initiate two `render()` calls concurrently with different manifests and output paths. Verify both complete successfully. Verify `initRegistries()` is called only once (via the cache).

34. **CLI backward compatibility:** After registry relocation, run `depthkit render` and `depthkit validate` via subprocess and verify exit codes and output match expected behavior.

### Relevant Testable Claims

- **TC-04:** Tests 26-27 verify that the Library API produces correct video from manifest + geometry/camera names alone.
- **TC-06:** Test 26 run twice verifies deterministic output through the Library API.
- **TC-07:** Tests verifying `MANIFEST_INVALID` for bad manifests confirm validation through the Library API layer.

## Integration Points

### Depends on

| Dependency | What OBJ-047 Uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`, `RenderProgress`. The Library API constructs an Orchestrator internally. |
| **OBJ-046** (CLI, for registry-init relocation) | OBJ-046's `src/cli/registry-init.ts` is the current location of `initRegistries()` and `RegistryBundle`. OBJ-047 relocates the implementation to `src/registry.ts` and updates OBJ-046's file to a re-export shim. |
| **OBJ-004** (Manifest Schema) | `Manifest`, `ManifestError` types. `createRegistry()`. |
| **OBJ-005** (Geometry Registry) | `GeometryRegistry`, `getGeometryRegistry()`. Consumed transitively via `initRegistries()`. |
| **OBJ-006** (Camera Registry) | `CameraPathRegistry`, `getCameraPath()`. Consumed transitively via `initRegistries()`. |
| **OBJ-013** (FFmpeg Encoder) | `H264Preset` type. Re-exported for consumer type safety. |
| **OBJ-012** (Frame Capture) | `CaptureStrategy` type. Re-exported for consumer type safety. |
| **OBJ-016** (Manifest Loader) | `loadManifest()`. Used by `render()` for manifest validation. |

### Consumed by

| Downstream | How It Uses OBJ-047 |
|---|---|
| **OBJ-055** (n8n HTTP endpoint) | Imports `render()` or `renderFile()` to execute video rendering from HTTP request handlers. Uses `hooks.onFrameRendered` for progress reporting via SSE or polling. Uses `RenderResult` to construct HTTP responses. |
| **OBJ-071** (SKILL.md) | Documents the Library API as the programmatic interface. |
| **OBJ-077** (End-to-end integration) | May use `render()` for integration tests. |
| **External consumers** | Any Node.js application that `import { render } from 'depthkit'`. |

### File Placement

```
depthkit/
  src/
    index.ts                   # NEW -- Package entry point with re-exports
    api.ts                     # NEW -- render(), renderFile(), types
    registry.ts                # NEW -- initRegistries(), RegistryBundle
                               #        (relocated from src/cli/registry-init.ts)
    cli/
      registry-init.ts         # MODIFIED -- re-exports from ../registry.ts
  test/
    unit/
      api.test.ts              # NEW -- Unit tests with mocked Orchestrator
    integration/
      api.test.ts              # NEW -- End-to-end integration tests
  package.json                 # MODIFIED -- "main"/"exports" points to
                               #             compiled src/index.ts
```

## Open Questions

### OQ-A: Should the Library API support streaming/chunked output?

For very long videos, the n8n endpoint might want to stream progress updates. The current hook-based design supports this (the endpoint can SSE-push `FrameEvent` data), but there's no built-in stream. A `renderToStream()` variant returning a `ReadableStream<FrameEvent>` with the MP4 path on close could be useful. Deferred -- hooks are sufficient for V1.

### OQ-B: Should there be a `validate()` function in the Library API?

The CLI has a `validate` command. Should the Library API export a `validate(manifest)` function that returns validation results without rendering? Currently, callers can use `loadManifest()` from OBJ-016 directly (which is not re-exported). Adding a `validate()` to the Library API surface would be trivial and useful for the n8n endpoint (validate manifest before queueing a render job). Low effort, but possibly scope creep for OBJ-047.

### OQ-C: Should SceneEvent include plane/slot information?

`SceneEvent` currently includes geometry and camera names. Should it also include the list of plane slot names being rendered? This could be useful for progress reporting ("Rendering scene 2: tunnel with 5 planes"). Low priority.

### OQ-D: Should render() accept a pre-initialized RegistryBundle?

For advanced callers who register custom geometries, a `registries?: RegistryBundle` option on `RenderOptions` would bypass auto-initialization. This maintains the simple API while enabling extensibility. Currently, advanced callers can use the `Orchestrator` directly. Could be added later without breaking changes.

### OQ-E: renderFile implementation — file reading vs loadManifestFromFile

`renderFile()` reads and parses the manifest JSON file, then delegates to `render()` with the parsed object. An alternative would be to call `loadManifestFromFile()` from OBJ-016 directly. The current design (read + delegate) keeps file I/O in `renderFile` and reuses `render()`'s full pipeline including JSON parsing and validation. Either approach produces identical results; the implementer should follow the function description (read file, parse, delegate to `render()`).
