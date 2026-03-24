# Deliberation Transcript: OBJ-047

---

## Round 1 — spec_author

Let me first look at the current codebase to understand what's already implemented.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]

[Tool: Glob]
  Input: {
  "pattern": "src/**/*.ts"
}

[Tool: Glob]
  Input: {
  "pattern": "src/index.ts"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-047/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Glob]
  Input: {
  "pattern": "**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-047/**/*",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-047/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-035/**/*",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/transcript.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-047/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-047",
     3→  "description": "Library API -- importable programmatic interface for depthkit. render(manifest) function signature, event hooks (onFrameRendered, onSceneStart, onComplete, onError), progress callbacks with frame count and percentage, and configuration options (output path, resolution overrides). Enables programmatic use from n8n HTTP endpoint and other Node.js consumers.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 interface."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-055/**/*",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-055/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-046/**/*",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/transcript.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-055/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-055",
     3→  "description": "n8n HTTP endpoint and job lifecycle -- Express/Fastify server wrapping the depthkit library API. POST endpoint accepts topic and duration, returns job ID. Poll endpoint returns job status (queued/rendering/complete/failed). Download endpoint returns MP4. Async job queue for managing concurrent render requests. Status management and cleanup. Per SC-05 (n8n integration works).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-047"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. Medium priority. Split from original OBJ-055 (Round 2 Issue 1). HTTP/job lifecycle only -- manifest generation is OBJ-056, asset orchestration is OBJ-057."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md"
}
[Tool Error] File content (11031 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-046 — CLI Interface
     2→
     3→## Summary
     4→
     5→OBJ-046 delivers the Commander-based CLI for depthkit (`src/cli.ts`) — the primary human-facing entry point for rendering, validating, and previewing manifests. It exposes three commands (`render`, `validate`, `preview`), handles argument parsing for manifest paths, output paths, resolution/fps overrides, GPU mode, encoding presets, verbose/debug output, and provides structured progress reporting and timing statistics during renders. It composes the Orchestrator (OBJ-035), manifest loader (OBJ-016), geometry registry (OBJ-005), and camera registry (OBJ-006) into a user-friendly terminal experience. The `package.json` `bin` field points to this module.
     6→
     7→## Interface Contract
     8→
     9→### Module: `src/cli.ts`
    10→
    11→This is the executable entry point. The source file begins with `#!/usr/bin/env node` (preserved by the TypeScript compiler or prepended by the build step). It... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "offset": 100,
  "limit": 80
}
[Tool Result]    100→Validates a manifest without rendering. Fast — no browser or FFmpeg launched.
   101→
   102→**Positional argument:**
   103→- `<manifest>` — Path to the manifest JSON file. Required.
   104→
   105→**Options:** None beyond global options.
   106→
   107→**Behavior:**
   108→1. Populate registries via `initRegistries()` (see D3).
   109→2. Load and validate manifest via `loadManifestFromFile()` (OBJ-016).
   110→3. On valid (with or without warnings): print summary to stdout, exit code 0.
   111→4. On invalid: print formatted errors to stderr, exit code 1.
   112→
   113→**Stdout on valid:**
   114→```
   115→✓ Manifest valid: 5 scenes, 60.00s total duration
   116→  Geometries: stage (2), tunnel (2), diorama (1)
   117→  Cameras: slow_push_forward (3), tunnel_push_forward (2)
   118→```
   119→
   120→If warnings exist:
   121→```
   122→✓ Manifest valid with 2 warning(s): 5 scenes, 60.00s total duration
   123→  ⚠ scenes: Scene array order differs from start_time order (SCENE_... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "initRegistries|registry",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "output_mode": "content",
  "-n": true
}
[Tool Result] 5:[Omitted long matching line]
70:2. Populate registries via `initRegistries()` (see D3).
108:1. Populate registries via `initRegistries()` (see D3).
260:### Module: `src/cli/registry-init.ts` — Registry Population
262:Centralizes registry population so both `render` and `validate` commands use the same registries.
270: * Registry bundle returned by initRegistries().
282: * imported statically at the top of registry-init.ts — their
287: *    the geometry registry.
297: * registries (because OBJ-005's registry locks on first read).
301:export function initRegistries(): RegistryBundle;
324:**Decision:** A single synchronous `initRegistries()` function in `src/cli/registry-init.ts` returns a `RegistryBundle` containing all three registries. All geometry and camera modules are **statically imported** at the top of `registry-init.ts` — their `registerGeometry()` side effects execute at module load time. The function body only calls `getGeometryRegistry()`, assembles the camera registry, ite... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "offset": 255,
  "limit": 60
}
[Tool Result]    255→ * e.g., 512000 → "8m 32s", 1500 → "1.5s", 45 → "45ms"
   256→ */
   257→export function formatDuration(ms: number): string;
   258→```
   259→
   260→### Module: `src/cli/registry-init.ts` — Registry Population
   261→
   262→Centralizes registry population so both `render` and `validate` commands use the same registries.
   263→
   264→```typescript
   265→import type { ManifestRegistry } from '../manifest/schema.js';
   266→import type { GeometryRegistry } from '../scenes/geometries/types.js';
   267→import type { CameraPathRegistry } from '../camera/types.js';
   268→
   269→/**
   270→ * Registry bundle returned by initRegistries().
   271→ */
   272→export interface RegistryBundle {
   273→  manifestRegistry: ManifestRegistry;
   274→  geometryRegistry: GeometryRegistry;
   275→  cameraRegistry: CameraPathRegistry;
   276→}
   277→
   278→/**
   279→ * Populates and returns all three registries needed by the orchestrator.
   280→ *
   281→ * This function is synchronous. A... [truncated]
Now I have a thorough understanding of the landscape. Let me propose the specification.

---

# Specification: OBJ-047 — Library API

## Summary

OBJ-047 delivers the importable programmatic interface for depthkit (`src/index.ts`) — the public entry point for Node.js consumers such as the n8n HTTP endpoint (OBJ-055) and any other programmatic caller. It wraps the Orchestrator (OBJ-035) with a higher-level API that handles registry initialization internally, supports resolution/fps overrides, and provides rich event hooks (`onFrameRendered`, `onSceneStart`, `onSceneEnd`, `onComplete`, `onError`) beyond the Orchestrator's single `onProgress` callback. It also relocates `initRegistries()` and `RegistryBundle` from `src/cli/registry-init.ts` (OBJ-046) to a shared `src/registry.ts` module so both the CLI and Library API consume the same registry initialization without cross-layer imports.

## Interface Contract

### Module: `src/index.ts`

The package's main entry point. All public types and functions are re-exported from here. The `package.json` `"main"` (or `"exports"`) field points to the compiled output of this module.

```typescript
// ── Re-exports (public surface) ──────────────────────────

// From OBJ-035 — callers who need low-level access
export { Orchestrator, OrchestratorError } from './engine/orchestrator.js';
export type {
  OrchestratorConfig,
  OrchestratorResult,
  OrchestratorErrorCode,
  RenderProgress,
} from './engine/orchestrator.js';

// From this module — the high-level API
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

// From manifest schema — needed by callers constructing manifests
export type { Manifest } from './manifest/schema.js';
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
 * at the top of this module — their registerGeometry() side effects
 * execute at module load time. This function:
 *
 * 1. Calls getGeometryRegistry() to retrieve the frozen geometry registry.
 * 2. Constructs CameraPathRegistry from camera preset barrel imports.
 * 3. Creates ManifestRegistry via createRegistry() and populates it
 *    by converting each SceneGeometry → GeometryRegistration and
 *    CameraPathPreset → CameraRegistration.
 * 4. Returns the RegistryBundle.
 *
 * Idempotent — subsequent calls return equivalent registries.
 */
export function initRegistries(): RegistryBundle;
```

### Module: `src/api.ts` — Library API Implementation

The core Library API logic. Separated from `src/index.ts` to keep the entry point clean (re-exports only).

```typescript
import type { OrchestratorResult, RenderProgress } from './engine/orchestrator.js';

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
  /** Override composition.fps. Must be 1–120. */
  fps?: number;
}

/**
 * Event data emitted when a scene starts rendering.
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
  /** Progress as a percentage [0, 100]. */
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
 * within the render loop — long-running hooks slow rendering.
 * Hooks must not throw — if they do, the render is cancelled
 * (same behavior as OrchestratorConfig.onProgress throwing).
 *
 * Hooks are NOT called on validation failure — only once
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
  /** Video duration in seconds. */
  durationSeconds: number;
  /** Total wall-clock time for the entire operation (ms). */
  totalDurationMs: number;
  /** Wall-clock time for the frame render loop only (ms). */
  renderDurationMs: number;
  /** Average milliseconds per frame. */
  averageFrameMs: number;
  /** Validation warnings (non-blocking). */
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
   * - A JSON string (parsed then validated).
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
  encodingPreset?: string;

  /**
   * Constant Rate Factor (0–51). Default: 23.
   */
  crf?: number;

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
 * 2. Manifest validation (C-10).
 * 3. Resolution/fps override application.
 * 4. Orchestrator construction and execution.
 * 5. Event hook dispatch (onFrameRendered, onSceneStart, onSceneEnd,
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
 * render(). The file's parent directory is used as the default
 * assetsDir (unless overridden in options).
 *
 * @param manifestPath - Path to the manifest JSON file.
 * @param options - Render configuration (manifest field is ignored;
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

**Why not require callers to pass registries?** The n8n endpoint (OBJ-055) and other consumers should not need to understand the registry system. The whole point of OBJ-047 is to hide internal wiring. Callers who need custom registries (e.g., with additional geometries) can use the `Orchestrator` directly — it is re-exported.

**Why cache?** `initRegistries()` is idempotent (OBJ-046 D3), but it performs static imports and registry iteration. Caching avoids redundant work in long-running server processes (OBJ-055) that render multiple videos.

**Thread safety:** Node.js is single-threaded. No mutex needed. Two concurrent `render()` calls will both check the cache, at most one will initialize — the second will find the result already populated. The underlying `getGeometryRegistry()` from OBJ-005 locks on first read, so double-init is safe.

### D3: Event Hooks Derived from onProgress State Tracking

**Decision:** The Library API implements `onSceneStart` and `onSceneEnd` by tracking `activeSceneIds` across frames:

1. Before the render loop, initialize `previousActiveSceneIds: string[] = []`.
2. Wire an internal `onProgress` callback to the Orchestrator.
3. On each `onProgress` invocation:
   a. Compute newly active scene IDs: `current.activeSceneIds.filter(id => !previousActiveSceneIds.includes(id))`.
   b. Compute newly inactive scene IDs: `previousActiveSceneIds.filter(id => !current.activeSceneIds.includes(id))`.
   c. For each newly active ID: invoke `hooks.onSceneStart` with the corresponding `SceneEvent`.
   d. For each newly inactive ID: invoke `hooks.onSceneEnd` with the corresponding `SceneEvent`.
   e. Invoke `hooks.onFrameRendered` with the `FrameEvent`.
   f. Update `previousActiveSceneIds = [...current.activeSceneIds]`.
   g. Return the value from `hooks.onFrameRendered` (for cancellation).
4. After the render loop completes: fire `onSceneEnd` for any scenes still in `previousActiveSceneIds` (handles the last scene, which ends when the loop finishes rather than when a subsequent frame removes it).

**Rationale:** This derives scene lifecycle events purely from the Orchestrator's existing `RenderProgress.activeSceneIds` field, without modifying OBJ-035. The state tracking is trivial and adds negligible overhead.

### D4: Resolution Overrides Applied via Deep Copy

**Decision:** When `overrides` is provided, `render()` creates a deep copy of the manifest object (after validation) and mutates the copy's `composition.width`, `composition.height`, and/or `composition.fps`. The original input object is never mutated.

**Override validation:**
- `width` and `height` must be positive even integers (H.264 requires even dimensions). If odd, the Library API throws `OrchestratorError` with code `MANIFEST_INVALID` and a descriptive message.
- `fps` must be between 1 and 120 inclusive.
- Overrides are applied after Zod validation but before Orchestrator construction. The Orchestrator receives the already-overridden manifest.

**Rationale:** OBJ-046 applies overrides by mutating the manifest object directly (OBJ-046 D2). This is acceptable for a CLI (the object is created from file and discarded). The Library API must not mutate input — callers may reuse the manifest object across multiple renders with different overrides.

### D5: RenderResult Simplifies OrchestratorResult

**Decision:** `RenderResult` is a flattened, consumer-friendly subset of `OrchestratorResult`. It includes the most commonly needed fields at the top level and preserves the full `OrchestratorResult` in `raw` for callers who need capture stats, encoder details, or renderer info.

The `warnings` field maps `OrchestratorResult.warnings` (array of `ManifestError`) to `string[]` by extracting each error's `message` field. This avoids requiring Library API consumers to import `ManifestError`.

**Rationale:** n8n workflows and HTTP endpoint consumers need output path, duration, and timing — not capture strategy stats. The `raw` escape hatch preserves full detail without polluting the primary interface.

### D6: Manifest Input Accepts Object or JSON String

**Decision:** `RenderOptions.manifest` accepts `unknown`. If it's a string that starts with `{` (after trimming), it is parsed as JSON first. Otherwise, it is passed directly to `loadManifest()` (OBJ-016) for Zod validation.

**Why not accept file paths in `manifest`?** Ambiguity: `"./manifest.json"` is a valid JSON string (it's a string literal). Separating file-based rendering into `renderFile()` eliminates this ambiguity.

**Rationale:** HTTP endpoints receive JSON request bodies as strings or parsed objects depending on middleware configuration. Accepting both covers common integration patterns without requiring the caller to pre-parse.

### D7: onComplete and onError Are Supplementary to the Promise

**Decision:** `render()` always returns a promise. `onComplete` is called just before the promise resolves; `onError` is called just before the promise rejects. These hooks do NOT replace the promise — the promise is the primary result mechanism.

If `onComplete` or `onError` throws, the thrown error is logged to `console.error` and swallowed — it does not alter the render result or the rejection.

**Rationale:** Fire-and-forget patterns in n8n workflows benefit from callbacks. Promise-based callers use `await`. Both work. Hook errors must not corrupt the render result.

### D8: Shared Registry Module Location

**Decision:** `initRegistries()` and `RegistryBundle` are defined in `src/registry.ts`. OBJ-046's `src/cli/registry-init.ts` is updated to re-export from `src/registry.ts` to maintain backward compatibility.

**Rationale:** Registry initialization is consumed by both the CLI (OBJ-046) and the Library API (OBJ-047). Placing it in `src/cli/` creates a layering violation where the library API imports from the CLI layer. `src/registry.ts` is the natural shared location. This is a minor refactor to OBJ-046's file placement, not a change to its interface contract.

### D9: No Engine/Builder Pattern in V1

**Decision:** The Library API is two stateless async functions (`render()`, `renderFile()`). There is no `createEngine()` or `DepthkitEngine` class.

**Why not?** A reusable engine class would pre-initialize registries and hold configuration defaults, enabling `engine.render(manifest1)` then `engine.render(manifest2)` without re-passing options. This is marginally useful but adds a class with lifecycle semantics (disposal? browser pooling?) that don't exist yet. The module-level registry cache (D2) achieves the main benefit (avoid re-initialization). An engine class can be added later without breaking the function-based API.

### D10: FrameEvent.percent as Convenience

**Decision:** `FrameEvent` includes both `ratio` (0–1, matching `RenderProgress.ratio`) and `percent` (0–100, computed as `ratio * 100`). Percent is a convenience for progress reporting in HTTP responses and logs.

**Rationale:** Every consumer of progress data will compute `ratio * 100` for display. Including it avoids N duplicate computations across N consumers.

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

- [ ] **AC-08:** `render()` with `overrides: { width: 1280, height: 720 }` produces a 1280×720 MP4 regardless of the manifest's `composition.width` and `composition.height`.
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
- [ ] **AC-20:** If `hooks.onComplete` throws, the exception is logged to `console.error` and swallowed — the promise still resolves with the result.
- [ ] **AC-21:** If `hooks.onError` throws, the exception is logged to `console.error` and swallowed — the promise still rejects with the original error.
- [ ] **AC-22:** If no hooks are provided, `render()` works identically (hooks are optional).

### RenderResult

- [ ] **AC-23:** `RenderResult.durationSeconds` equals `totalFrames / fps`.
- [ ] **AC-24:** `RenderResult.warnings` is a `string[]` containing the messages from `OrchestratorResult.warnings`.
- [ ] **AC-25:** `RenderResult.hasAudio` is `true` when the manifest has `composition.audio`, `false` otherwise.
- [ ] **AC-26:** `RenderResult.raw` is the full `OrchestratorResult` from the Orchestrator.

### Error Handling

- [ ] **AC-27:** `render()` with an invalid manifest throws `OrchestratorError` with code `MANIFEST_INVALID`, just as the Orchestrator does. No browser is launched.
- [ ] **AC-28:** `renderFile()` with a non-existent file path throws `OrchestratorError` with code `MANIFEST_INVALID`.
- [ ] **AC-29:** All `OrchestratorError` codes from OBJ-035 are preserved — the Library API does not wrap or alter error codes.

### Package Exports

- [ ] **AC-30:** `import { render, renderFile, Orchestrator, OrchestratorError, initRegistries } from 'depthkit'` works. All five are accessible.
- [ ] **AC-31:** `import type { RenderOptions, RenderResult, RenderHooks, FrameEvent, SceneEvent, Manifest, RegistryBundle } from 'depthkit'` works. All types are accessible.

### Shared Registry

- [ ] **AC-32:** `src/registry.ts` exports `initRegistries` and `RegistryBundle`. `src/cli/registry-init.ts` re-exports from `src/registry.ts`.
- [ ] **AC-33:** The CLI (`depthkit render`) continues to work after the registry relocation.

## Edge Cases and Error Handling

### Manifest Input

| Scenario | Expected Behavior |
|---|---|
| `manifest` is a valid object | Passed to `loadManifest()`. Rendered. |
| `manifest` is a valid JSON string | Parsed with `JSON.parse()`. Passed to `loadManifest()`. Rendered. |
| `manifest` is an invalid JSON string | `JSON.parse()` throws. Caught and rethrown as `OrchestratorError` code `MANIFEST_INVALID` with the parse error as `cause`. |
| `manifest` is null/undefined/number | Passed to `loadManifest()` which rejects it. `MANIFEST_INVALID`. |
| `manifest` is a string not starting with `{` (e.g., a file path) | Passed to `loadManifest()` as-is (not parsed as JSON). Zod rejects it. `MANIFEST_INVALID`. The error message should hint: "Did you mean to use renderFile()?" |

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
| `hooks` is undefined | All hooks skipped. Internal `onProgress` is not wired (the Orchestrator's `onProgress` is left undefined). |
| `hooks` with only `onComplete` (no frame-level hooks) | Internal `onProgress` is still not wired (no frame tracking needed). `onComplete` fires after render. |
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
| `assetsDir` not provided | Defaults to the manifest file's parent directory (via `path.dirname(manifestPath)`), not `process.cwd()`. |

## Test Strategy

### Unit Tests: `test/unit/api.test.ts`

Tests the Library API logic with a mocked Orchestrator. Mock `initRegistries()` to return a stub bundle. Mock the `Orchestrator` class to return predetermined results.

1. **Basic render:** Mock orchestrator to succeed. Verify `RenderResult` fields map correctly from `OrchestratorResult`.

2. **JSON string manifest:** Pass a JSON string. Verify it's parsed and passed to the Orchestrator as an object.

3. **Invalid JSON string:** Pass `"not json {"`. Verify `MANIFEST_INVALID` with parse error in `cause`.

4. **Non-object string (file path hint):** Pass `"./manifest.json"`. Verify `MANIFEST_INVALID` message includes "Did you mean to use renderFile()?"

5. **Overrides applied:** Pass `overrides: { width: 1280, height: 720, fps: 24 }`. Verify the manifest passed to the Orchestrator has these values. Verify original input object unchanged.

6. **Odd width rejected:** `overrides: { width: 1281 }`. Verify `MANIFEST_INVALID`.

7. **FPS out of range:** `overrides: { fps: 0 }`. Verify `MANIFEST_INVALID`.

8. **Registry caching:** Call `render()` twice (mocked). Verify `initRegistries()` is called once.

9. **onFrameRendered wiring:** Verify the mock Orchestrator receives an `onProgress` callback. Simulate 3 progress calls. Verify `onFrameRendered` called 3 times with correct `FrameEvent` (including `percent`).

10. **onFrameRendered cancellation:** Mock `onFrameRendered` to return `false`. Verify the value is propagated through the internal `onProgress` return.

11. **onSceneStart detection:** Simulate progress calls with changing `activeSceneIds`: `['s1'] → ['s1'] → ['s1','s2'] → ['s2']`. Verify `onSceneStart` called twice: once for `s1` (frame 0), once for `s2` (frame 2).

12. **onSceneEnd detection:** Same sequence as above. Verify `onSceneEnd` called for `s1` on frame 3 (when `s1` leaves `activeSceneIds`).

13. **Last scene onSceneEnd:** Simulate 3 frames all with `['s1']`. After render completes, verify `onSceneEnd` called for `s1`.

14. **Gap frame transitions:** `['s1'] → [] → ['s2']`. Verify `onSceneEnd` for `s1` on frame 1, `onSceneStart` for `s2` on frame 2.

15. **onComplete called:** Mock successful render. Verify `onComplete` called with `RenderResult`.

16. **onError called:** Mock failed render. Verify `onError` called with the error.

17. **onComplete throws swallowed:** Mock `onComplete` to throw. Verify `render()` still resolves. Verify `console.error` called.

18. **onError throws swallowed:** Mock `onError` to throw. Verify `render()` still rejects with original error. Verify `console.error` called.

19. **No hooks:** No `hooks` in options. Verify Orchestrator `onProgress` is `undefined`.

20. **Only onSceneStart hook:** Verify internal `onProgress` is wired (to track scenes), but `onFrameRendered` is not called.

21. **RenderResult.warnings mapping:** `OrchestratorResult.warnings` with two `ManifestError` objects. Verify `RenderResult.warnings` is `['msg1', 'msg2']`.

22. **RenderResult.hasAudio:** Verify true when `audioResult` is non-null, false when null.

### Integration Tests: `test/integration/api.test.ts`

Real rendering with small viewports. Short manifests (320×240, 0.5s at 10fps).

23. **End-to-end render():** Create a test manifest object with one scene. Call `render()`. Verify MP4 exists and plays.

24. **End-to-end renderFile():** Write manifest to temp file. Call `renderFile()`. Verify MP4 exists.

25. **renderFile default assetsDir:** Manifest in `/tmp/test/manifest.json` with images relative to `/tmp/test/images/`. Verify images resolve correctly without passing `assetsDir`.

26. **Override resolution:** Render with `overrides: { width: 160, height: 120 }`. Verify `ffprobe` reports 160×120.

27. **Hook invocation order:** Render a 2-scene manifest. Collect all hook calls in order. Verify: `onSceneStart(s1)` → N × `onFrameRendered` → `onSceneStart(s2)` → ... → `onSceneEnd(s1)` → ... → `onSceneEnd(s2)` → `onComplete`.

28. **Cancellation via hook:** `onFrameRendered` returns `false` after 3 frames. Verify `render()` rejects with `CANCELLED`. Verify `onError` is called.

29. **Package exports:** `import { render, renderFile, Orchestrator, OrchestratorError, initRegistries } from '../src/index.js'` — verify all are defined.

### Relevant Testable Claims

- **TC-04:** Tests 23–24 verify that the Library API produces correct video from manifest + geometry/camera names alone.
- **TC-06:** Test 23 run twice verifies deterministic output through the Library API.
- **TC-07:** Tests verifying `MANIFEST_INVALID` for bad manifests confirm validation through the Library API layer.

## Integration Points

### Depends on

| Dependency | What OBJ-047 Uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`, `RenderProgress`. The Library API constructs an Orchestrator internally. |
| **OBJ-046** (CLI, for registry-init relocation) | OBJ-046's `src/cli/registry-init.ts` is the current location of `initRegistries()` and `RegistryBundle`. OBJ-047 relocates these to `src/registry.ts` and updates OBJ-046's file to re-export. |
| **OBJ-004** (Manifest Schema) | `Manifest`, `ManifestError` types. `createRegistry()`. |
| **OBJ-005** (Geometry Registry) | `GeometryRegistry`, `getGeometryRegistry()`. Consumed transitively via `initRegistries()`. |
| **OBJ-006** (Camera Registry) | `CameraPathRegistry`, `getCameraPath()`. Consumed transitively via `initRegistries()`. |
| **OBJ-016** (Manifest Loader) | `loadManifest()`, `loadManifestFromFile()`. Used by `render()` and `renderFile()` respectively. |

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
    index.ts                   # NEW — Package entry point with re-exports
    api.ts                     # NEW — render(), renderFile(), types
    registry.ts                # NEW — initRegistries(), RegistryBundle
                               #       (relocated from src/cli/registry-init.ts)
    cli/
      registry-init.ts         # MODIFIED — re-exports from ../registry.ts
  test/
    unit/
      api.test.ts              # NEW — Unit tests with mocked Orchestrator
    integration/
      api.test.ts              # NEW — End-to-end integration tests
  package.json                 # MODIFIED — "main"/"exports" points to
                               #            compiled src/index.ts
```

## Open Questions

### OQ-A: Should the Library API support streaming/chunked output?

For very long videos, the n8n endpoint might want to stream progress updates. The current hook-based design supports this (the endpoint can SSE-push `FrameEvent` data), but there's no built-in stream. A `renderToStream()` variant returning a `ReadableStream<FrameEvent>` with the MP4 path on close could be useful. Deferred — hooks are sufficient for V1.

### OQ-B: Should there be a `validate()` function in the Library API?

The CLI has a `validate` command. Should the Library API export a `validate(manifest)` function that returns validation results without rendering? Currently, callers can use `loadManifest()` from OBJ-016 directly (which is not re-exported). Adding a `validate()` to the Library API surface would be trivial and useful for the n8n endpoint (validate manifest before queueing a render job). Low effort, but possibly scope creep for OBJ-047.

### OQ-C: Should SceneEvent include plane/slot information?

`SceneEvent` currently includes geometry and camera names. Should it also include the list of plane slot names being rendered? This could be useful for progress reporting ("Rendering scene 2: tunnel with 5 planes"). Low priority.

### OQ-D: Should render() accept a pre-initialized RegistryBundle?

For advanced callers who register custom geometries, a `registries?: RegistryBundle` option on `RenderOptions` would bypass auto-initialization. This maintains the simple API while enabling extensibility. Currently, advanced callers can use the `Orchestrator` directly. Could be added later without breaking changes.

---

I believe this specification fully covers the OBJ-047 description: the `render(manifest)` function signature, event hooks (`onFrameRendered`, `onSceneStart`, `onSceneEnd`, `onComplete`, `onError`), progress callbacks with frame count and percentage (`FrameEvent.frame`, `FrameEvent.percent`), configuration options (output path, resolution overrides), and enablement of programmatic use from the n8n HTTP endpoint.

I'd like the challenger to review and verify this proposal. Key areas I'd especially appreciate scrutiny on:

1. **D3 (scene event derivation from activeSceneIds)** — is the state-tracking algorithm correct for all transition types?
2. **D8 (registry relocation)** — is modifying OBJ-046's file placement acceptable given it's already verified?
3. **The manifest string detection heuristic** (D6, checking for `{`) — is this robust enough?

---

## Round 2 — spec_challenger

I'll review the proposed OBJ-047 spec carefully against the seed, the OBJ-035 dependency, and the OBJ-046 downstream spec.

Let me first check some additional context.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Grep",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]
Let me check a few more details before delivering my review.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "offset": 300,
  "limit": 80
}
[Tool Result]    300→ */
   301→export function initRegistries(): RegistryBundle;
   302→```
   303→
   304→## Design Decisions
   305→
   306→### D1: Commander as CLI Framework
   307→
   308→**Decision:** Use `commander` (npm) for argument parsing and command routing.
   309→
   310→**Rationale:** Commander is MIT-licensed, the most widely adopted Node.js CLI framework, and is already permitted by C-01 ("Standard npm utilities... are allowed"). It provides subcommand support, automatic `--help` generation, option type coercion, and default values.
   311→
   312→### D2: Resolution/FPS Overrides Are Applied Post-Validation
   313→
   314→**Decision:** CLI `--width`, `--height`, and `--fps` overrides are applied to the manifest object **after** Phase 1 (structural) and Phase 2 (semantic) validation, but **before** constructing the Orchestrator. The overrides mutate the `Manifest.composition` fields directly.
   315→
   316→**Rationale:** The manifest on disk is the source of truth. Overrides are a c... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "encodingPreset|H264Preset",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md",
  "output_mode": "content"
}
[Tool Result] 17:import type { H264Preset } from './ffmpeg-encoder.js';
95:  encodingPreset?: H264Preset;

[Tool: Grep]
  Input: {
  "pattern": "H264Preset|type.*H264",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes",
  "output_mode": "content",
  "head_limit": 10
}
[Tool Result] nodes/OBJ-013/transcript.md:31:export type H264Preset =
nodes/OBJ-013/transcript.md:64:  preset?: H264Preset;
nodes/OBJ-013/transcript.md:505:export type H264Preset =
nodes/OBJ-013/transcript.md:531:  preset?: H264Preset;
nodes/OBJ-013/transcript.md:950:[Omitted long matching line]
nodes/OBJ-013/output.md:25:export type H264Preset =
nodes/OBJ-013/output.md:56:  preset?: H264Preset;
nodes/OBJ-012/transcript.md:927:    25→export type H264Preset =
nodes/OBJ-035/transcript.md:930:import type { H264Preset } from './ffmpeg-encoder.js';
nodes/OBJ-035/transcript.md:995:  encodingPreset?: H264Preset;

[Showing results with pagination = limit: 10, offset: 0]

[Tool: Grep]
  Input: {
  "pattern": "CaptureStrategy",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md",
  "output_mode": "content"
}
[Tool Result] 15:import type { CaptureStats, CaptureStrategy } from './frame-capture.js';
90:  captureStrategy?: CaptureStrategy;

[Tool: Grep]
  Input: {
  "pattern": "type H264Preset",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "output_mode": "content",
  "-A": 5
}
[Tool Result] 25:export type H264Preset =
26-  | 'ultrafast' | 'superfast' | 'veryfast' | 'faster'
27-  | 'fast' | 'medium' | 'slow' | 'slower' | 'veryslow';
28-
29-/**
30- * Configuration for the FFmpeg encoder.
Good, now I have enough context. Let me deliver my review.

---

## Challenger Review — OBJ-047 Library API

The proposal is well-structured overall. The wrapping pattern (D1), event derivation from `activeSceneIds` (D3), and the result simplification (D5) are all sound decisions. I'll explicitly approve what works, then enumerate my objections.

### Points of Agreement

- **D1 (wrap, don't extend)** — Clean separation. Correct pattern.
- **D3 (scene event derivation)** — The algorithm is correct for all transition types. The post-loop `onSceneEnd` for the last scene is a detail most specs miss. Good.
- **D5 (RenderResult simplifies OrchestratorResult)** — The `raw` escape hatch is the right tradeoff.
- **D7 (onComplete/onError supplementary to promise)** — Correct. Swallowing hook errors is the right call.
- **D9 (no engine/builder for V1)** — Agreed. YAGNI.
- **D10 (percent convenience)** — Fine.
- **Test strategy** — Thorough. The mock-based unit tests for hook derivation (tests 11-14) are exactly what's needed.

---

### Issue 1: `encodingPreset` typed as `string` instead of `H264Preset` (Major)

**Where:** `RenderOptions.encodingPreset`

**Problem:** OBJ-035's `OrchestratorConfig.encodingPreset` is typed as `H264Preset` (a union of 9 string literals from OBJ-013). The Library API declares it as `string`. This loses type safety — a caller could pass `"garbage"` and get a runtime error from FFmpeg instead of a compile-time error.

**Proposed fix:** Import and use `H264Preset` from OBJ-013 (via OBJ-035's re-export), or re-export it from `src/index.ts`. The type in `RenderOptions` should be:
```typescript
encodingPreset?: H264Preset;
```
And add `H264Preset` to the re-exports in `src/index.ts`.

---

### Issue 2: `renderFile` default `assetsDir` inconsistency (Major)

**Where:** `renderFile()` documentation vs. `render()` documentation vs. OBJ-046 behavior.

**Problem:** Three different defaults are stated:
- `RenderOptions.assetsDir` says "Default: `process.cwd()`"
- `renderFile()` edge case table says "Defaults to the manifest file's parent directory (via `path.dirname(manifestPath)`), not `process.cwd()`"
- OBJ-046 D9 says CLI defaults to the parent directory of the manifest file.

The `renderFile` behavior (parent of manifest file) is correct for file-based use. But the spec never explicitly documents this override in the `renderFile` function description beyond the edge case table. An implementer might read `Omit<RenderOptions, 'manifest'>` and assume `assetsDir` defaults to `process.cwd()` from the `RenderOptions` docs.

**Proposed fix:** In the `renderFile()` JSDoc, explicitly state: "If `options.assetsDir` is not provided, it defaults to `path.dirname(manifestPath)` (the manifest file's parent directory), overriding the `process.cwd()` default used by `render()`." Also add an acceptance criterion verifying this behavior (the current test 25 covers it, but there's no AC for it).

---

### Issue 3: JSON string detection heuristic is fragile (Major)

**Where:** D6 — "If it's a string that starts with `{` (after trimming)"

**Problem:** A valid JSON manifest is an object, so starting with `{` is correct. But what about:
1. A string starting with whitespace then `{` — the "(after trimming)" handles this but trimming isn't mentioned in the edge case table.
2. A JSON string that starts with `[` — this would be an invalid manifest, but the error message would be confusing (Zod would reject the string literal `"[...]"` instead of rejecting it as an invalid manifest structure).
3. A file path like `{project}/manifest.json` — extremely unlikely but technically matches.

The real concern: the heuristic isn't wrong, but it's described ambiguously. "Starts with `{`" is informal.

**Proposed fix:** Be precise in D6: "If `manifest` is a `string`, it is passed through `JSON.parse()`. If parsing succeeds, the parsed result is used. If parsing fails, `render()` throws `OrchestratorError` with code `MANIFEST_INVALID`, with the `SyntaxError` as `cause`. If the error message from `JSON.parse` suggests a non-JSON string was passed, append hint text: 'Did you mean to use renderFile()?'" This eliminates the `{`-prefix check entirely — just always try parsing strings as JSON. Simpler, more robust.

---

### Issue 4: Missing `captureStrategy` from `RenderOptions` (Minor)

**Where:** `RenderOptions` type definition.

**Problem:** `OrchestratorConfig` exposes `captureStrategy?: CaptureStrategy` (from OBJ-012). The Library API's `RenderOptions` omits it. This may be intentional (defaulting to `'viewport-png'`), but it's not documented as a deliberate omission.

**Proposed fix:** Either add `captureStrategy?: CaptureStrategy` to `RenderOptions` (and re-export `CaptureStrategy` from `src/index.ts`), or add a brief note in D1 or a new design decision explaining that `captureStrategy` is intentionally omitted from the Library API because it's an internal performance knob that consumers don't need.

---

### Issue 5: Registry relocation modifies a verified objective (Major)

**Where:** D8 — moving `initRegistries()` from `src/cli/registry-init.ts` to `src/registry.ts`.

**Problem:** OBJ-046 is `status: "verified"`. Its spec defines `initRegistries()` in `src/cli/registry-init.ts`. OBJ-047 proposes relocating this to `src/registry.ts` and updating OBJ-046's file to be a re-export. This is a modification to a verified objective's file placement.

Is this within OBJ-047's scope? The meta.json description says "importable programmatic interface" — it doesn't mention refactoring OBJ-046's internals. The refactor is sensible (fixing a layering violation), but it introduces risk: if the re-export breaks the CLI, that's a regression on a verified objective.

**Proposed fix:** Keep the refactoring but be more explicit about the backward-compatibility guarantee. Add:
1. An acceptance criterion: **AC-33** (currently "The CLI (`depthkit render`) continues to work after the registry relocation") is good — keep it.
2. A design decision noting that this is a deliberate cross-objective modification: "This relocation modifies OBJ-046's file structure. OBJ-046's `src/cli/registry-init.ts` becomes a re-export shim (`export { initRegistries, type RegistryBundle } from '../registry.js';`). OBJ-046's public interface and behavior are unchanged — only the file that holds the source implementation moves."
3. Note in the test strategy that integration test 33 (AC-33) must verify the CLI's `render` and `validate` commands still function after the move.

This is already *mostly* addressed; I just want the design decision to be more explicit about the cross-objective nature.

---

### Issue 6: `onSceneStart`/`onSceneEnd` hooks need `onProgress` even without `onFrameRendered` — incomplete spec for internal wiring (Minor)

**Where:** D3 algorithm, Hook Edge Cases table ("Only onSceneStart hook" row), Test 20.

**Problem:** The edge case table says "Internal `onProgress` IS wired (to track `activeSceneIds` changes). `onFrameRendered` is not called since it's not provided." This is correct behavior. But D3 doesn't explicitly state the condition for wiring `onProgress`. An implementer needs to know:

*Wire an internal `onProgress` to the Orchestrator if ANY of `onFrameRendered`, `onSceneStart`, or `onSceneEnd` are provided.*

The edge case table for "hooks is undefined" says `onProgress` is not wired, and "Only onComplete" says it's not wired. But the general rule isn't stated in D3.

**Proposed fix:** Add to D3: "The internal `onProgress` callback is wired to the Orchestrator whenever at least one of `onFrameRendered`, `onSceneStart`, or `onSceneEnd` is provided. If only `onComplete` and/or `onError` are provided (no frame-level hooks), `onProgress` is left `undefined` on the `OrchestratorConfig` — these hooks are invoked from the promise resolution/rejection path, not the frame loop."

---

### Issue 7: `SceneEvent` construction — where does the data come from? (Major)

**Where:** `SceneEvent` interface and D3.

**Problem:** `SceneEvent` includes `sceneIndex`, `totalScenes`, `geometry`, `camera`, `startTime`, `duration`. To construct this, the Library API needs access to the parsed manifest's scene array (sorted by `start_time`). But D3 only describes tracking `activeSceneIds` from `RenderProgress`. The Library API needs to build a `Map<string, SceneEvent>` from the manifest scenes at setup time — this isn't specified.

An implementer would figure this out, but "would figure it out" means "would guess," which violates the spec's purpose.

**Proposed fix:** Add to D3: "Before the render loop, `render()` constructs a `Map<string, SceneEvent>` keyed by scene ID from the validated manifest's `scenes` array (sorted by `start_time`). Each `SceneEvent` is pre-computed: `sceneIndex` is the position in the sorted array, `totalScenes` is the array length, and `geometry`/`camera`/`startTime`/`duration` are read from the scene definition. When `onSceneStart` or `onSceneEnd` fires, the pre-computed `SceneEvent` for that scene ID is passed to the hook."

---

### Issue 8: Missing re-exports for downstream consumers (Minor)

**Where:** `src/index.ts` re-exports.

**Problem:** The re-export list includes `Manifest` from `./manifest/schema.js` but not `ManifestError`, which is referenced by `OrchestratorResult.warnings` and `OrchestratorError.validationErrors`. A caller who catches `OrchestratorError` and wants to inspect `validationErrors` would need to import `ManifestError` — but it's not re-exported.

Similarly, `CaptureStats`, `FFmpegEncoderResult`, `AudioMuxerResult`, and `RendererInfo` are part of `OrchestratorResult` (accessible via `RenderResult.raw`) but not re-exported. A consumer accessing `raw` would need deep imports.

**Proposed fix:** Either:
(a) Add `ManifestError` to the re-exports (it's the most likely needed type), or
(b) Add a comment in the re-exports section: "Types from OBJ-035's result sub-components (CaptureStats, FFmpegEncoderResult, etc.) are not re-exported in V1. Consumers needing these types can import them directly from their source modules. ManifestError can be imported from './manifest/schema.js'."

I'd recommend (a) — re-export `ManifestError` at minimum.

---

### Issue 9: `RenderResult.durationSeconds` naming inconsistency (Minor)

**Where:** `RenderResult.durationSeconds` vs. `OrchestratorResult.videoDurationSeconds`.

**Problem:** The field is renamed from `videoDurationSeconds` to `durationSeconds`. AC-23 says `durationSeconds` equals `totalFrames / fps`. This is fine as a simplification, but the name `durationSeconds` is ambiguous — is it video duration or total operation duration? `totalDurationMs` is already present for operation duration, but the naming overlap could confuse consumers.

**Proposed fix:** Minor — either keep `durationSeconds` (it's clear enough in context) but add a JSDoc comment: `/** Video content duration in seconds (totalFrames / fps). Not wall-clock render time. */`, or rename to `videoDurationSeconds` to match OBJ-035. I'd lean toward keeping `durationSeconds` with the JSDoc.

---

### Issue 10: No acceptance criterion for concurrent renders (Minor)

**Where:** Edge Cases table mentions concurrent renders work, but no AC verifies it.

**Problem:** The edge case table says "Two `render()` calls in parallel: Each creates its own Orchestrator. Both share the cached registry bundle. Both run independently." But there's no test or AC for this. It's important for OBJ-055 (n8n endpoint), which may queue multiple renders.

**Proposed fix:** Add a test (not necessarily an AC, since it's more of an integration concern): "Test: Two `render()` calls initiated concurrently with different manifests both complete successfully. Registry is initialized only once."

---

### Summary of Objections by Severity

| # | Severity | Issue |
|---|---|---|
| 1 | Major | `encodingPreset` typed as `string` instead of `H264Preset` |
| 2 | Major | `renderFile` default `assetsDir` inconsistency |
| 3 | Major | JSON string detection heuristic — simplify to always `JSON.parse` |
| 5 | Major | Registry relocation needs explicit cross-objective documentation |
| 7 | Major | `SceneEvent` construction data source unspecified |
| 4 | Minor | `captureStrategy` omission undocumented |
| 6 | Minor | Internal `onProgress` wiring condition not stated in D3 |
| 8 | Minor | Missing `ManifestError` re-export |
| 9 | Minor | `durationSeconds` naming ambiguity |
| 10 | Minor | No test for concurrent renders |

No critical issues. The spec is close. Please address the 5 major issues; I'll accept reasonable resolutions for the minor ones.

---

## Round 3 — spec_author

Thank you for the thorough review. All 10 issues are valid. Here's how I'm addressing each:

---

## Issue Resolutions

### Issue 1 (Major): `encodingPreset` typed as `string` — **Accepted**
Changed to `H264Preset`. Added `H264Preset` and `CaptureStrategy` to re-exports.

### Issue 2 (Major): `renderFile` default `assetsDir` — **Accepted**
Added explicit JSDoc to `renderFile()` and a new AC-34 for this behavior.

### Issue 3 (Major): JSON string detection heuristic — **Accepted**
Eliminated the `{`-prefix check. D6 now says: if `manifest` is a string, always `JSON.parse()` it. If parse fails, throw `MANIFEST_INVALID` with the `SyntaxError` as `cause` and append hint text.

### Issue 4 (Minor): `captureStrategy` omission — **Accepted**
Added `captureStrategy` to `RenderOptions` and `CaptureStrategy` to re-exports.

### Issue 5 (Major): Registry relocation cross-objective documentation — **Accepted**
D8 now explicitly states the cross-objective nature and backward-compatibility guarantee. AC-33 expanded to verify both `render` and `validate` CLI commands.

### Issue 6 (Minor): Internal `onProgress` wiring condition — **Accepted**
Added explicit wiring rule to D3.

### Issue 7 (Major): `SceneEvent` construction data source — **Accepted**
Added pre-computation step to D3 describing the `Map<string, SceneEvent>` built from the manifest.

### Issue 8 (Minor): Missing `ManifestError` re-export — **Accepted**
Added `ManifestError` to re-exports. Added a comment noting that `raw` sub-component types are available via direct import.

### Issue 9 (Minor): `durationSeconds` naming — **Accepted**
Added JSDoc comment clarifying it's video content duration, not wall-clock time.

### Issue 10 (Minor): No concurrent render test — **Accepted**
Added integration test 30 for concurrent renders.

---

## Revised Specification: OBJ-047 — Library API

### Summary

OBJ-047 delivers the importable programmatic interface for depthkit (`src/index.ts`) — the public entry point for Node.js consumers such as the n8n HTTP endpoint (OBJ-055) and any other programmatic caller. It wraps the Orchestrator (OBJ-035) with a higher-level API that handles registry initialization internally, supports resolution/fps overrides, and provides rich event hooks (`onFrameRendered`, `onSceneStart`, `onSceneEnd`, `onComplete`, `onError`) beyond the Orchestrator's single `onProgress` callback. It also relocates `initRegistries()` and `RegistryBundle` from `src/cli/registry-init.ts` (OBJ-046) to a shared `src/registry.ts` module so both the CLI and Library API consume the same registry initialization without cross-layer imports.

### Interface Contract

#### Module: `src/index.ts`

The package's main entry point. All public types and functions are re-exported from here. The `package.json` `"main"` (or `"exports"`) field points to the compiled output of this module.

```typescript
// ── Re-exports (public surface) ──────────────────────────

// From OBJ-035 — callers who need low-level access
export { Orchestrator, OrchestratorError } from './engine/orchestrator.js';
export type {
  OrchestratorConfig,
  OrchestratorResult,
  OrchestratorErrorCode,
  RenderProgress,
} from './engine/orchestrator.js';

// From OBJ-013 — encoding types used in RenderOptions
export type { H264Preset } from './engine/ffmpeg-encoder.js';

// From OBJ-012 — capture types used in RenderOptions
export type { CaptureStrategy } from './engine/frame-capture.js';

// From this module — the high-level API
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

// From manifest schema — needed by callers constructing manifests
// or inspecting validation errors
export type { Manifest, ManifestError } from './manifest/schema.js';

// Note: Types from OBJ-035's result sub-components (CaptureStats,
// FFmpegEncoderResult, AudioMuxerResult, RendererInfo) are accessible
// via RenderResult.raw but are not re-exported in V1. Consumers
// needing these types can import them directly from their source
// modules (e.g., './engine/frame-capture.js').
```

#### Module: `src/registry.ts` — Shared Registry Initialization

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
 * at the top of this module — their registerGeometry() side effects
 * execute at module load time. This function:
 *
 * 1. Calls getGeometryRegistry() to retrieve the frozen geometry registry.
 * 2. Constructs CameraPathRegistry from camera preset barrel imports.
 * 3. Creates ManifestRegistry via createRegistry() and populates it
 *    by converting each SceneGeometry → GeometryRegistration and
 *    CameraPathPreset → CameraRegistration.
 * 4. Returns the RegistryBundle.
 *
 * Idempotent — subsequent calls return equivalent registries.
 */
export function initRegistries(): RegistryBundle;
```

#### Module: `src/api.ts` — Library API Implementation

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
  /** Override composition.fps. Must be 1–120. */
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
 * within the render loop — long-running hooks slow rendering.
 * Hooks must not throw — if they do, the render is cancelled
 * (same behavior as OrchestratorConfig.onProgress throwing).
 *
 * Hooks are NOT called on validation failure — only once
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
   * Constant Rate Factor (0–51). Default: 23.
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

### Design Decisions

#### D1: Library API Wraps Orchestrator, Does Not Extend It

**Decision:** `render()` and `renderFile()` are standalone async functions that internally construct an `Orchestrator`, call `render()`, and map the result. They do not subclass or modify `Orchestrator`.

**Rationale:** The Orchestrator (OBJ-035) is a well-defined, single-responsibility class: one instance per render, no reuse. The Library API adds ergonomics (registry auto-init, event hooks, overrides, simplified types) without changing the rendering pipeline. Wrapping keeps concerns separated: OBJ-035 owns the rendering invariants (C-02, C-03, C-05), OBJ-047 owns the public DX surface.

#### D2: Registry Auto-Initialization with Module-Level Cache

**Decision:** `render()` calls `initRegistries()` internally. The result is cached at module scope in `src/api.ts` (a `let registryBundle: RegistryBundle | null = null` variable, populated on first call). Subsequent calls reuse the cached bundle.

**Why not require callers to pass registries?** The n8n endpoint (OBJ-055) and other consumers should not need to understand the registry system. The whole point of OBJ-047 is to hide internal wiring. Callers who need custom registries (e.g., with additional geometries) can use the `Orchestrator` directly — it is re-exported.

**Why cache?** `initRegistries()` is idempotent (OBJ-046 D3), but it performs static imports and registry iteration. Caching avoids redundant work in long-running server processes (OBJ-055) that render multiple videos.

**Thread safety:** Node.js is single-threaded. No mutex needed. Two concurrent `render()` calls will both check the cache, at most one will initialize — the second will find the result already populated. The underlying `getGeometryRegistry()` from OBJ-005 locks on first read, so double-init is safe.

#### D3: Event Hooks Derived from onProgress State Tracking

**Decision:** The Library API implements `onSceneStart` and `onSceneEnd` by tracking `activeSceneIds` across frames.

**Internal `onProgress` wiring rule:** An internal `onProgress` callback is wired to the Orchestrator whenever at least one of `onFrameRendered`, `onSceneStart`, or `onSceneEnd` is provided. If only `onComplete` and/or `onError` are provided (no frame-level hooks), `onProgress` is left `undefined` on the `OrchestratorConfig` — these hooks are invoked from the promise resolution/rejection path, not the frame loop.

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

#### D4: Resolution Overrides Applied via Deep Copy

**Decision:** When `overrides` is provided, `render()` creates a deep copy of the manifest object (after validation) and mutates the copy's `composition.width`, `composition.height`, and/or `composition.fps`. The original input object is never mutated.

**Override validation:**
- `width` and `height` must be positive even integers (H.264 requires even dimensions). If odd, negative, or zero, the Library API throws `OrchestratorError` with code `MANIFEST_INVALID` and a descriptive message (e.g., "Override width must be a positive even integer, got 1281").
- `fps` must be between 1 and 120 inclusive. If out of range, throws `OrchestratorError` with code `MANIFEST_INVALID`.
- Overrides are applied after Zod validation but before Orchestrator construction. The Orchestrator receives the already-overridden manifest.

**Rationale:** OBJ-046 applies overrides by mutating the manifest object directly (OBJ-046 D2). This is acceptable for a CLI (the object is created from file and discarded). The Library API must not mutate input — callers may reuse the manifest object across multiple renders with different overrides.

#### D5: RenderResult Simplifies OrchestratorResult

**Decision:** `RenderResult` is a flattened, consumer-friendly subset of `OrchestratorResult`. It includes the most commonly needed fields at the top level and preserves the full `OrchestratorResult` in `raw` for callers who need capture stats, encoder details, or renderer info.

The `warnings` field maps `OrchestratorResult.warnings` (array of `ManifestError`) to `string[]` by extracting each error's `message` field. This avoids requiring Library API consumers to import `ManifestError` for simple warning display.

**Rationale:** n8n workflows and HTTP endpoint consumers need output path, duration, and timing — not capture strategy stats. The `raw` escape hatch preserves full detail without polluting the primary interface.

#### D6: Manifest Input — String Parsing Strategy

**Decision:** `RenderOptions.manifest` accepts `unknown`. If it is a `string`, it is unconditionally passed through `JSON.parse()`:
- If parsing succeeds, the parsed result is used as the manifest object.
- If parsing fails, `render()` throws `OrchestratorError` with code `MANIFEST_INVALID`, with the `SyntaxError` as `cause`. If the original string does not start with `{` or `[` (after trimming), the error message appends: `"Did you mean to use renderFile()?"`.

If `manifest` is not a string, it is passed directly to `loadManifest()` (OBJ-016) for Zod validation.

**Why not accept file paths in `manifest`?** Separating file-based rendering into `renderFile()` eliminates ambiguity. The hint text guides callers who accidentally pass a file path.

**Rationale:** HTTP endpoints receive JSON request bodies as strings or parsed objects depending on middleware configuration. Accepting both covers common integration patterns without requiring the caller to pre-parse.

#### D7: onComplete and onError Are Supplementary to the Promise

**Decision:** `render()` always returns a promise. `onComplete` is called just before the promise resolves; `onError` is called just before the promise rejects. These hooks do NOT replace the promise — the promise is the primary result mechanism.

If `onComplete` or `onError` throws, the thrown error is logged to `console.error` and swallowed — it does not alter the render result or the rejection.

**Rationale:** Fire-and-forget patterns in n8n workflows benefit from callbacks. Promise-based callers use `await`. Both work. Hook errors must not corrupt the render result.

#### D8: Shared Registry Module Location (Cross-Objective Modification)

**Decision:** `initRegistries()` and `RegistryBundle` are defined in `src/registry.ts`. OBJ-046's `src/cli/registry-init.ts` is updated to re-export from `src/registry.ts` to maintain backward compatibility.

**Cross-objective impact:** This relocation modifies OBJ-046's file structure. OBJ-046 is `status: "verified"`. OBJ-046's `src/cli/registry-init.ts` becomes a re-export shim:
```typescript
export { initRegistries, type RegistryBundle } from '../registry.js';
```
OBJ-046's public interface and behavior are unchanged — only the file that holds the source implementation moves. The CLI's `render` and `validate` commands continue to import from `src/cli/registry-init.ts` and function identically.

**Rationale:** Registry initialization is consumed by both the CLI (OBJ-046) and the Library API (OBJ-047). Placing it in `src/cli/` creates a layering violation where the library API imports from the CLI layer. `src/registry.ts` is the natural shared location. The re-export shim ensures zero behavioral change for OBJ-046.

#### D9: No Engine/Builder Pattern in V1

**Decision:** The Library API is two stateless async functions (`render()`, `renderFile()`). There is no `createEngine()` or `DepthkitEngine` class.

**Rationale:** A reusable engine class would pre-initialize registries and hold configuration defaults. This is marginally useful but adds lifecycle semantics (disposal? browser pooling?) that don't exist yet. The module-level registry cache (D2) achieves the main benefit. An engine class can be added later without breaking the function-based API.

#### D10: FrameEvent.percent as Convenience

**Decision:** `FrameEvent` includes both `ratio` (0–1, matching `RenderProgress.ratio`) and `percent` (0–100, computed as `ratio * 100`). Percent is a convenience for progress reporting in HTTP responses and logs.

### Acceptance Criteria

#### Core Rendering

- [ ] **AC-01:** `render()` with a valid manifest object and `outputPath` produces a valid MP4 file. The returned `RenderResult.outputPath` points to the file. `ffprobe` confirms H.264 encoding.
- [ ] **AC-02:** `renderFile()` with a valid manifest JSON file path produces the same result as reading the file, parsing it, and calling `render()`.
- [ ] **AC-03:** `render()` with a JSON string as `manifest` parses it and renders successfully.
- [ ] **AC-04:** The manifest input object is not mutated, even when `overrides` are provided.

#### Registry Auto-Initialization

- [ ] **AC-05:** `render()` works without the caller constructing or passing any registries. All built-in geometries and camera presets are available.
- [ ] **AC-06:** Calling `render()` twice in the same process does not re-initialize registries. The second call reuses the cached `RegistryBundle`.
- [ ] **AC-07:** `initRegistries()` is exported from `src/index.ts` for callers who need direct registry access.

#### Overrides

- [ ] **AC-08:** `render()` with `overrides: { width: 1280, height: 720 }` produces a 1280×720 MP4 regardless of the manifest's `composition.width` and `composition.height`.
- [ ] **AC-09:** `render()` with `overrides: { fps: 24 }` produces a 24fps MP4 regardless of the manifest's `composition.fps`.
- [ ] **AC-10:** `render()` with `overrides: { width: 1281 }` (odd number) throws `OrchestratorError` with code `MANIFEST_INVALID` and a message mentioning even dimensions.
- [ ] **AC-11:** `render()` with `overrides: { fps: 0 }` or `overrides: { fps: 200 }` throws `OrchestratorError` with code `MANIFEST_INVALID`.

#### Event Hooks

- [ ] **AC-12:** `hooks.onFrameRendered` is called once per frame. The `frame` field increments from 0 to `totalFrames - 1`. `percent` reaches 100 on the last frame.
- [ ] **AC-13:** `hooks.onFrameRendered` returning `false` cancels the render. `render()` rejects with `OrchestratorError` code `CANCELLED`.
- [ ] **AC-14:** `hooks.onSceneStart` fires on the first frame where a scene becomes active. For a 2-scene manifest with a cut transition, `onSceneStart` fires twice: once for scene 1 on frame 0, once for scene 2 on the first frame of scene 2.
- [ ] **AC-15:** `hooks.onSceneEnd` fires on the first frame after a scene is no longer active. For a 2-scene manifest with a cut transition, `onSceneEnd` fires for scene 1 on the first frame of scene 2.
- [ ] **AC-16:** `hooks.onSceneEnd` fires for the last scene after the render loop completes (not during the loop), since no subsequent frame removes it from `activeSceneIds`.
- [ ] **AC-17:** `hooks.onSceneStart` fires correctly during crossfade transitions: the incoming scene's event fires on the first overlap frame.
- [ ] **AC-18:** `hooks.onComplete` is called with the `RenderResult` just before the promise resolves.
- [ ] **AC-19:** `hooks.onError` is called with the `OrchestratorError` just before the promise rejects.
- [ ] **AC-20:** If `hooks.onComplete` throws, the exception is logged to `console.error` and swallowed — the promise still resolves with the result.
- [ ] **AC-21:** If `hooks.onError` throws, the exception is logged to `console.error` and swallowed — the promise still rejects with the original error.
- [ ] **AC-22:** If no hooks are provided, `render()` works identically (hooks are optional).

#### RenderResult

- [ ] **AC-23:** `RenderResult.durationSeconds` equals `totalFrames / fps` (video content duration, not wall-clock time).
- [ ] **AC-24:** `RenderResult.warnings` is a `string[]` containing the messages from `OrchestratorResult.warnings`.
- [ ] **AC-25:** `RenderResult.hasAudio` is `true` when the manifest has `composition.audio`, `false` otherwise.
- [ ] **AC-26:** `RenderResult.raw` is the full `OrchestratorResult` from the Orchestrator.

#### Error Handling

- [ ] **AC-27:** `render()` with an invalid manifest throws `OrchestratorError` with code `MANIFEST_INVALID`, just as the Orchestrator does. No browser is launched.
- [ ] **AC-28:** `renderFile()` with a non-existent file path throws `OrchestratorError` with code `MANIFEST_INVALID`.
- [ ] **AC-29:** All `OrchestratorError` codes from OBJ-035 are preserved — the Library API does not wrap or alter error codes.

#### Package Exports

- [ ] **AC-30:** `import { render, renderFile, Orchestrator, OrchestratorError, initRegistries } from 'depthkit'` works. All five are accessible.
- [ ] **AC-31:** `import type { RenderOptions, RenderResult, RenderHooks, FrameEvent, SceneEvent, Manifest, RegistryBundle, ManifestError, H264Preset, CaptureStrategy } from 'depthkit'` works. All types are accessible.

#### Shared Registry

- [ ] **AC-32:** `src/registry.ts` exports `initRegistries` and `RegistryBundle`. `src/cli/registry-init.ts` re-exports from `src/registry.ts`.
- [ ] **AC-33:** The CLI (`depthkit render` and `depthkit validate` commands) continues to work after the registry relocation. Both commands still import from `src/cli/registry-init.ts` and behave identically.

#### renderFile Specifics

- [ ] **AC-34:** `renderFile()` without `assetsDir` in options defaults to `path.dirname(manifestPath)` as the base directory for resolving relative image paths. A manifest at `/tmp/project/manifest.json` referencing `./images/bg.png` resolves to `/tmp/project/images/bg.png`.

### Edge Cases and Error Handling

#### Manifest Input

| Scenario | Expected Behavior |
|---|---|
| `manifest` is a valid object | Passed to `loadManifest()`. Rendered. |
| `manifest` is a valid JSON string | Parsed with `JSON.parse()`. Passed to `loadManifest()`. Rendered. |
| `manifest` is an invalid JSON string (e.g., `"not json {"`) | `JSON.parse()` throws `SyntaxError`. Rethrown as `OrchestratorError` code `MANIFEST_INVALID` with the `SyntaxError` as `cause`. |
| `manifest` is a string that looks like a file path (e.g., `"./manifest.json"`) | `JSON.parse()` fails. `OrchestratorError` code `MANIFEST_INVALID`. Error message appends: "Did you mean to use renderFile()?" (because the string does not start with `{` or `[` after trimming). |
| `manifest` is null/undefined/number | Passed to `loadManifest()` which rejects it. `MANIFEST_INVALID`. |

#### Overrides

| Scenario | Expected Behavior |
|---|---|
| `overrides: {}` (empty) | No overrides applied. Manifest values used as-is. |
| `overrides: { width: 1920 }` with manifest width already 1920 | No-op. No error. |
| `overrides: { width: 1280 }` only (no height) | Only width overridden. Height from manifest. Aspect ratio changes. |
| `overrides: { width: -100 }` | `MANIFEST_INVALID`: "Override width must be a positive even integer." |
| `overrides: { fps: 1 }` | Valid (minimum). Renders at 1fps. |
| `overrides: { fps: 120 }` | Valid (maximum). Renders at 120fps. |

#### Hook Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `onFrameRendered` throws on frame 5 | Orchestrator's internal `onProgress` treats thrown exceptions as cancellation. `render()` rejects with `CANCELLED`, cause is the thrown error. `onError` is called before rejection. |
| Single-scene manifest | `onSceneStart` fires once (frame 0). `onSceneEnd` fires once (after render loop). |
| Gap frames between scenes | During gap frames, `activeSceneIds` is empty. If the previous frame had a scene, `onSceneEnd` fires for it. When the next scene starts, `onSceneStart` fires. |
| Two `onSceneStart` in quick succession (crossfade) | Both fire: outgoing scene's `onSceneStart` already fired previously; incoming scene's `onSceneStart` fires on first overlap frame. No `onSceneEnd` for outgoing until overlap ends. |
| `hooks` is undefined | All hooks skipped. Internal `onProgress` is not wired. |
| `hooks` with only `onComplete` (no frame-level hooks) | Internal `onProgress` is not wired. `onComplete` fires after render. |
| `hooks` with only `onSceneStart` (needs frame tracking but no onFrameRendered) | Internal `onProgress` IS wired (to track `activeSceneIds` changes). `onFrameRendered` is not called since it's not provided. |

#### Concurrent Renders

| Scenario | Expected Behavior |
|---|---|
| Two `render()` calls in parallel | Each creates its own Orchestrator. Both share the cached registry bundle. Both run independently. Both complete or fail independently. |
| `render()` called while a previous render is still running | Works. Each Orchestrator is independent (OBJ-035 D10). |

#### renderFile Specifics

| Scenario | Expected Behavior |
|---|---|
| File exists, valid JSON, valid manifest | Renders successfully. |
| File exists, invalid JSON | `MANIFEST_INVALID` with JSON parse error. |
| File exists, valid JSON, invalid manifest | `MANIFEST_INVALID` with validation errors. |
| File doesn't exist | `MANIFEST_INVALID` with `FILE_NOT_FOUND`. |
| `assetsDir` not provided | Defaults to `path.dirname(manifestPath)`, not `process.cwd()`. |

### Test Strategy

#### Unit Tests: `test/unit/api.test.ts`

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

12. **onSceneStart detection:** Simulate progress calls with changing `activeSceneIds`: `['s1'] → ['s1'] → ['s1','s2'] → ['s2']`. Verify `onSceneStart` called twice: once for `s1` (frame 0), once for `s2` (frame 2).

13. **onSceneEnd detection:** Same sequence as above. Verify `onSceneEnd` called for `s1` on frame 3 (when `s1` leaves `activeSceneIds`).

14. **Last scene onSceneEnd:** Simulate 3 frames all with `['s1']`. After render completes, verify `onSceneEnd` called for `s1`.

15. **Gap frame transitions:** `['s1'] → [] → ['s2']`. Verify `onSceneEnd` for `s1` on frame 1, `onSceneStart` for `s2` on frame 2.

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

#### Integration Tests: `test/integration/api.test.ts`

Real rendering with small viewports. Short manifests (320×240, 0.5s at 10fps).

26. **End-to-end render():** Create a test manifest object with one scene. Call `render()`. Verify MP4 exists and plays.

27. **End-to-end renderFile():** Write manifest to temp file. Call `renderFile()`. Verify MP4 exists.

28. **renderFile default assetsDir:** Manifest in `/tmp/test/manifest.json` with images relative to `/tmp/test/images/`. Verify images resolve correctly without passing `assetsDir`.

29. **Override resolution:** Render with `overrides: { width: 160, height: 120 }`. Verify `ffprobe` reports 160×120.

30. **Hook invocation order:** Render a 2-scene manifest. Collect all hook calls in order. Verify: `onSceneStart(s1)` → N × `onFrameRendered` → `onSceneStart(s2)` → ... → `onSceneEnd(s1)` → ... → `onSceneEnd(s2)` → `onComplete`.

31. **Cancellation via hook:** `onFrameRendered` returns `false` after 3 frames. Verify `render()` rejects with `CANCELLED`. Verify `onError` is called.

32. **Package exports:** `import { render, renderFile, Orchestrator, OrchestratorError, initRegistries } from '../src/index.js'` — verify all are defined.

33. **Concurrent renders:** Initiate two `render()` calls concurrently with different manifests and output paths. Verify both complete successfully. Verify `initRegistries()` is called only once (via the cache).

34. **CLI backward compatibility:** After registry relocation, run `depthkit render` and `depthkit validate` via subprocess and verify exit codes and output match expected behavior.

#### Relevant Testable Claims

- **TC-04:** Tests 26–27 verify that the Library API produces correct video from manifest + geometry/camera names alone.
- **TC-06:** Test 26 run twice verifies deterministic output through the Library API.
- **TC-07:** Tests verifying `MANIFEST_INVALID` for bad manifests confirm validation through the Library API layer.

### Integration Points

#### Depends on

| Dependency | What OBJ-047 Uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`, `RenderProgress`. The Library API constructs an Orchestrator internally. |
| **OBJ-046** (CLI, for registry-init relocation) | OBJ-046's `src/cli/registry-init.ts` is the current location of `initRegistries()` and `RegistryBundle`. OBJ-047 relocates the implementation to `src/registry.ts` and updates OBJ-046's file to a re-export shim. |
| **OBJ-004** (Manifest Schema) | `Manifest`, `ManifestError` types. `createRegistry()`. |
| **OBJ-005** (Geometry Registry) | `GeometryRegistry`, `getGeometryRegistry()`. Consumed transitively via `initRegistries()`. |
| **OBJ-006** (Camera Registry) | `CameraPathRegistry`, `getCameraPath()`. Consumed transitively via `initRegistries()`. |
| **OBJ-013** (FFmpeg Encoder) | `H264Preset` type. Re-exported for consumer type safety. |
| **OBJ-012** (Frame Capture) | `CaptureStrategy` type. Re-exported for consumer type safety. |
| **OBJ-016** (Manifest Loader) | `loadManifest()`, `loadManifestFromFile()`. Used by `render()` and `renderFile()` respectively. |

#### Consumed by

| Downstream | How It Uses OBJ-047 |
|---|---|
| **OBJ-055** (n8n HTTP endpoint) | Imports `render()` or `renderFile()` to execute video rendering from HTTP request handlers. Uses `hooks.onFrameRendered` for progress reporting via SSE or polling. Uses `RenderResult` to construct HTTP responses. |
| **OBJ-071** (SKILL.md) | Documents the Library API as the programmatic interface. |
| **OBJ-077** (End-to-end integration) | May use `render()` for integration tests. |
| **External consumers** | Any Node.js application that `import { render } from 'depthkit'`. |

#### File Placement

```
depthkit/
  src/
    index.ts                   # NEW — Package entry point with re-exports
    api.ts                     # NEW — render(), renderFile(), types
    registry.ts                # NEW — initRegistries(), RegistryBundle
                               #       (relocated from src/cli/registry-init.ts)
    cli/
      registry-init.ts         # MODIFIED — re-exports from ../registry.ts
  test/
    unit/
      api.test.ts              # NEW — Unit tests with mocked Orchestrator
    integration/
      api.test.ts              # NEW — End-to-end integration tests
  package.json                 # MODIFIED — "main"/"exports" points to
                               #            compiled src/index.ts
```

### Open Questions

#### OQ-A: Should the Library API support streaming/chunked output?

For very long videos, the n8n endpoint might want to stream progress updates. The current hook-based design supports this (the endpoint can SSE-push `FrameEvent` data), but there's no built-in stream. A `renderToStream()` variant returning a `ReadableStream<FrameEvent>` with the MP4 path on close could be useful. Deferred — hooks are sufficient for V1.

#### OQ-B: Should there be a `validate()` function in the Library API?

The CLI has a `validate` command. Should the Library API export a `validate(manifest)` function that returns validation results without rendering? Currently, callers can use `loadManifest()` from OBJ-016 directly (which is not re-exported). Adding a `validate()` to the Library API surface would be trivial and useful for the n8n endpoint (validate manifest before queueing a render job). Low effort, but possibly scope creep for OBJ-047.

#### OQ-C: Should SceneEvent include plane/slot information?

`SceneEvent` currently includes geometry and camera names. Should it also include the list of plane slot names being rendered? This could be useful for progress reporting ("Rendering scene 2: tunnel with 5 planes"). Low priority.

#### OQ-D: Should render() accept a pre-initialized RegistryBundle?

For advanced callers who register custom geometries, a `registries?: RegistryBundle` option on `RenderOptions` would bypass auto-initialization. This maintains the simple API while enabling extensibility. Currently, advanced callers can use the `Orchestrator` directly. Could be added later without breaking changes.

---

I believe all 10 issues have been addressed. Challenger, please verify and approve.

---

## Round 4 — spec_challenger

Let me verify each fix against the revised spec.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Grep",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]
I'll now systematically verify each of my 10 original issues against the revised Round 3 spec.

**Issue 1 (Major): `encodingPreset` typed as `string`** — ✅ FIXED. The revised `RenderOptions.encodingPreset` is now `H264Preset`. `H264Preset` and `CaptureStrategy` are both in the re-exports block.

**Issue 2 (Major): `renderFile` default `assetsDir`** — ✅ FIXED. The `renderFile()` JSDoc now explicitly states the `path.dirname(manifestPath)` default. AC-34 verifies this behavior.

**Issue 3 (Major): JSON string detection heuristic** — ✅ FIXED. D6 now says strings are unconditionally passed through `JSON.parse()`. The hint text logic is clearly specified (appended when the string doesn't start with `{` or `[` after trimming).

**Issue 4 (Minor): `captureStrategy` omission** — ✅ FIXED. Added to `RenderOptions` with proper type.

**Issue 5 (Major): Registry relocation cross-objective docs** — ✅ FIXED. D8 now explicitly labels itself "Cross-Objective Modification," describes the re-export shim, and confirms OBJ-046's interface is unchanged. AC-33 expanded.

**Issue 6 (Minor): `onProgress` wiring condition** — ✅ FIXED. D3 now states the explicit wiring rule.

**Issue 7 (Major): `SceneEvent` construction data source** — ✅ FIXED. D3 now includes the pre-computation step describing the `Map<string, SceneEvent>`. Test 25 verifies it.

**Issue 8 (Minor): Missing `ManifestError` re-export** — ✅ FIXED. Added to re-exports with a comment about `raw` sub-component types.

**Issue 9 (Minor): `durationSeconds` naming** — ✅ FIXED. JSDoc added clarifying it's video content duration.

**Issue 10 (Minor): No concurrent render test** — ✅ FIXED. Integration test 33 added.

All 10 issues are structurally resolved in the revised spec. Now let me check for any new issues introduced by the revisions or anything I missed in Round 2.

**New check — test numbering:** Tests were renumbered (unit 1-25, integration 26-34). The numbering is consistent and sequential. Good.

**New check — AC-11 fps boundary:** AC-11 says `fps: 200` throws. D4 says fps must be 1–120. But test 8 says "Also test `fps: 121`." This is consistent — 200 and 121 are both > 120. Fine.

**New check — `renderFile` uses `loadManifestFromFile` or reads + `render()`?** The `renderFile` description says "reads and parses the file, then delegates to `render()`." But the Integration Points table says it uses `loadManifestFromFile()` from OBJ-016. These are subtly different approaches. Looking more carefully: `renderFile` reads the file, gets the JSON content, then calls `render({ manifest: parsedContent, ... })`. That means `render()` would `JSON.parse` it again if it's a string... wait, no — if `renderFile` reads and parses, it passes an object to `render()`, which passes it to `loadManifest()`. That works. But the dependency table says `loadManifestFromFile()` is used — this is a minor inconsistency. The implementation path is clear enough though: read file → parse → delegate to `render()`. The `loadManifestFromFile` mention in the deps table is slightly misleading but not blocking. I'll note it as a minor point.

**New check — D6 string detection vs `renderFile` interaction:** When `renderFile` reads a file and gets the content, does it pass the raw string or the parsed object to `render()`? The spec says "reads and parses the file, then delegates to render()." If it passes a parsed object, `render()` won't try `JSON.parse` on it (only strings get parsed). This is correct behavior. Fine.

**New check — `render()` ordering of operations:** D6 says JSON string parsing happens first, then it goes to `loadManifest()`. D4 says overrides are applied "after Zod validation but before Orchestrator construction." The full sequence should be: (1) parse string if needed, (2) validate via `loadManifest()`, (3) deep copy + apply overrides, (4) construct Orchestrator. But the Orchestrator also validates internally (OBJ-035 D7: "The manifest is always validated"). So the manifest gets validated twice — once by the Library API (to get the parsed Manifest), and once by the Orchestrator. This is consistent with OBJ-035's design (which says re-validation is negligible). But wait — the Library API applies overrides to the *validated* manifest, then passes the overridden manifest to the Orchestrator, which re-validates. This means the overridden values get validated by Zod too. Good — no gap here.

**One remaining concern — does the Library API need `loadManifest()` directly?** If `render()` passes the manifest to the Orchestrator and the Orchestrator validates it internally, the Library API doesn't need to call `loadManifest()` itself. But the Library API needs the parsed `Manifest` object to: (a) deep-copy and apply overrides, (b) build the `SceneEvent` map. So it does need to validate/parse first to get a typed `Manifest`. This is fine — double validation is explicitly acceptable per OBJ-035.

Actually, let me re-read: D4 says "overrides are applied after Zod validation but before Orchestrator construction." So the Library API calls `loadManifest()` to get the typed Manifest, applies overrides to a copy, then passes the overridden manifest to the Orchestrator. The Orchestrator re-validates. This works.

Everything checks out. The spec is complete, implementable, and addresses all raised issues.

CONCLUSION:

The specification for OBJ-047 (Library API) is approved. All 10 issues from Round 2 have been structurally verified as resolved in the Round 3 revision. The spec defines a clean programmatic wrapper around OBJ-035's Orchestrator with: (1) `render()` and `renderFile()` as the primary entry points, (2) automatic registry initialization with module-level caching, (3) rich event hooks derived from `activeSceneIds` state tracking, (4) resolution/fps overrides via deep copy, (5) a simplified `RenderResult` with `raw` escape hatch, and (6) a shared `src/registry.ts` module relocating `initRegistries()` from OBJ-046's CLI layer. One minor note for the Open Questions: the Integration Points table lists `loadManifestFromFile()` as a dependency, but the `renderFile()` description says it reads and parses the file then delegates to `render()` — the implementer should follow the function description (read + delegate), not the table entry.

Now I'll write the final spec to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-047/output.md",
  "content": "# Specification: OBJ-047 \u2014 Library API\n\n## Summary\n\nOBJ-047 delivers the importable programmatic interface for depthkit (`src/index.ts`) \u2014 the public entry point for Node.js consumers such as the n8n HTTP endpoint (OBJ-055) and any other programmatic caller. It wraps the Orchestrator (OBJ-035) with a higher-level API that handles registry initialization internally, supports resolution/fps overrides, and provides rich event hooks (`onFrameRendered`, `onSceneStart`, `onSceneEnd`, `onComplete`, `onError`) beyond the Orchestrator's single `onProgress` callback. It also relocates `initRegistries()` and `RegistryBundle` from `src/cli/registry-init.ts` (OBJ-046) to a shared `src/registry.ts` module so both the CLI and Library API consume the same registry initialization without cross-layer imports.\n\n## Interface Contract\n\n### Module: `src/index.ts`\n\nThe package's main entry point. All public types and functions are re-exported from here. The `package.json` `\"main\"` (or `\"exports\"`) field points to the compiled output of this module.\n\n```typescript\n// -- Re-exports (public surface) --------------------------------\n\n// From OBJ-035 -- callers who need low-level access\nexport { Orchestrator, OrchestratorError } from './engine/orchestrator.js';\nexport type {\n  OrchestratorConfig,\n  OrchestratorResult,\n  OrchestratorErrorCode,\n  RenderProgress,\n} from './engine/orchestrator.js';\n\n// From OBJ-013 -- encoding types used in RenderOptions\nexport type { H264Preset } from './engine/ffmpeg-encoder.js';\n\n// From OBJ-012 -- capture types used in RenderOptions\nexport type { CaptureStrategy } from './engine/frame-capture.js';\n\n// From this module -- the high-level API\nexport { render, renderFile };\nexport type {\n  RenderOptions,\n  RenderHooks,\n  RenderOverrides,\n  SceneEvent,\n  FrameEvent,\n  RenderResult,\n};\n\n
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-047/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-047/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-047",
     3→  "description": "Library API -- importable programmatic interface for depthkit. render(manifest) function signature, event hooks (onFrameRendered, onSceneStart, onComplete, onError), progress callbacks with frame count and percentage, and configuration options (output path, resolution overrides). Enables programmatic use from n8n HTTP endpoint and other Node.js consumers.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 interface."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-047/meta.json",
  "content": "{\n  \"id\": \"OBJ-047\",\n  \"description\": \"Library API -- importable programmatic interface for depthkit. render(manifest) function signature, event hooks (onFrameRendered, onSceneStart, onSceneEnd, onComplete, onError), progress callbacks with frame count and percentage, and configuration options (output path, resolution overrides). Enables programmatic use from n8n HTTP endpoint and other Node.js consumers.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:00:00Z\",\n  \"depends_on\": [\"OBJ-035\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"notes\": \"Tier 4 interface. Spec approved after 4-round deliberation. Wraps Orchestrator with ergonomic render()/renderFile() functions, event hooks derived from activeSceneIds tracking, resolution/fps overrides, module-level registry caching. Relocates initRegistries() from src/cli/registry-init.ts to shared src/registry.ts.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-047/meta.json has been updated successfully.
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
  "description": "Check git status for uncommitted changes"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "View recent commit messages for style"
}
[Tool Result] c16726a spec(OBJ-070): SKILL.md structure and core content
0d39d2e spec(OBJ-028): lateral track camera path presets
326107f spec(OBJ-017): geometry-specific structural manifest validation - minimal ValidatableGeometry interface, function injection, deterministic error ordering. Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
2e80bae spec(OBJ-036): scene sequencer — stateless planFrame model, boundary resolution, independent fades
2b71510 spec(OBJ-040): plane sizing and edge-reveal prevention system
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-047/meta.json

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
	nodes/OBJ-017/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-019/transcript.md
	nodes/OBJ-020/transcript.md
	nodes/OBJ-021/transcript.md
	nodes/... [truncated]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-047/output.md nodes/OBJ-047/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-047): Library API \u2014 importable programmatic interface for depthkit\n\nDefines render() and renderFile() as the public programmatic entry points,\nwrapping OBJ-035's Orchestrator with registry auto-init, resolution/fps\noverrides, and event hooks (onFrameRendered, onSceneStart, onSceneEnd,\nonComplete, onError). Relocates initRegistries() to shared src/registry.ts.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-047 spec files"
}
[Tool Result] [master 7788a22] spec(OBJ-047): Library API — importable programmatic interface for depthkit
 2 files changed, 756 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-047/output.md
The spec is committed. Here's a summary of the converged specification:

## OBJ-047 — Library API: Final Summary

**What it delivers:** The importable programmatic interface for depthkit via `src/index.ts`, `src/api.ts`, and `src/registry.ts`.

**Key interfaces:**
- **`render(options: RenderOptions)`** — Primary entry point accepting manifest objects or JSON strings, with automatic registry initialization, resolution/fps overrides via deep copy, and rich event hooks
- **`renderFile(manifestPath, options)`** — Convenience wrapper that reads a manifest file and defaults `assetsDir` to the file's parent directory
- **`RenderResult`** — Simplified result wrapper with `raw` escape hatch to full `OrchestratorResult`
- **`RenderHooks`** — `onFrameRendered`, `onSceneStart`, `onSceneEnd`, `onComplete`, `onError`

**Key design decisions (10 total):**
- D1: Wraps Orchestrator, doesn't extend it
- D2: Module-level registry cache (idempotent, no mutex needed)
- D3: Scene events derived from `activeSceneIds` state tracking with pre-computed `SceneEvent` map
- D4: Overrides via deep copy (never mutates input)
- D6: Strings always go through `JSON.parse()` (no prefix heuristic)
- D8: Cross-objective registry relocation with re-export shim for OBJ-046 backward compatibility

**34 acceptance criteria** covering core rendering, registry auto-init, overrides, event hooks, result mapping, error handling, package exports, shared registry, and `renderFile` specifics.

**Issues resolved during deliberation:** `H264Preset` typing, `renderFile` assetsDir default, JSON parsing strategy, `captureStrategy` exposure, cross-objective documentation, `onProgress` wiring rule, `SceneEvent` data source, `ManifestError` re-export, `durationSeconds` JSDoc, concurrent render testing.
