# Deliberation Transcript: OBJ-035

---

## Round 1 — spec_author

Let me start by understanding the current state of the codebase and the dependency specs I don't have in the prompt (particularly OBJ-011, which is clearly needed by the orchestrator).
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the codebase to understand the current state and find OBJ-011's spec.
[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-011/output.md"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-011/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Glob]
  Input: {
  "pattern": "src/engine/*.ts",
  "path": "/home/user/depthkit"
}
[Tool Error] <tool_use_error>Directory does not exist: /home/user/depthkit. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.</tool_use_error>

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-011/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "src/engine/*.ts"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "src/**/*.ts"
}
[Tool Result] No files found
[Tool Error] File content (15329 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "limit": 200
}
[Tool Result]      1→# Specification: OBJ-011 — Puppeteer-to-Page Message Protocol
     2→
     3→## Summary
     4→
     5→OBJ-011 defines the complete cross-boundary message protocol between the Node.js orchestrator and the headless Chromium page. It delivers: (1) a `PageProtocol` class on the Node side that wraps `PuppeteerBridge.evaluate()` with typed, high-level commands — initialization, scene setup/teardown, frame rendering (with multi-pass support for transitions), and disposal; (2) page-side extensions to `window.depthkit` that implement the protocol handlers — scene management (creating/removing THREE.Group instances with textured meshes), texture loading via THREE.TextureLoader, and multi-pass compositing for transitions; and (3) shared protocol types (`src/engine/protocol-types.ts`) that define every data structure crossing the boundary. This is the single source of truth for the Node.js/browser contract, building on OBJ-009's `evaluate()` primitive, OBJ-010's renderer skeleton, and OBJ-... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": 200,
  "limit": 250
}
[Tool Result]    200→ *   covers A. At p=0.5: ~50/50 blend. At p=1.0: fully B.
   201→ *   This is an approximation of true alpha compositing but produces
   202→ *   visually acceptable results for opaque scenes.
   203→ *
   204→ * For dip_to_black transitions:
   205→ *   Fade out: passes = [{ sceneId: A, opacity: 1-p, camera: ... }]
   206→ *   Fade in:  passes = [{ sceneId: B, opacity: p,   camera: ... }]
   207→ *   The clear color (black) shows through where opacity < 1.
   208→ *
   209→ * For cut transitions:
   210→ *   passes = [{ sceneId: B, opacity: 1.0, camera: ... }]
   211→ *   Scene just changes between frames.
   212→ *
   213→ * The orchestrator (OBJ-036) is responsible for computing the
   214→ * correct opacity values for each pass given the transition type
   215→ * and progress. The protocol transmits them as-is.
   216→ */
   217→export interface RenderFrameCommand {
   218→  /**
   219→   * Ordered list of render passes. Rendered in order;
   220→   * later passes paint over... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": 450,
  "limit": 200
}
[Tool Result]    450→   *
   451→   * @param command - The render passes for this frame.
   452→   * @throws PageProtocolError with code 'NOT_INITIALIZED' if init not called.
   453→   * @throws PageProtocolError with code 'SCENE_NOT_FOUND' if a pass references
   454→   *         a sceneId that has not been set up or has been torn down.
   455→   * @throws PageProtocolError with code 'INVALID_COMMAND' if passes is empty.
   456→   */
   457→  renderFrame(command: RenderFrameCommand): Promise<void>;
   458→
   459→  /**
   460→   * Tear down a scene: remove all meshes from the Three.js scene,
   461→   * dispose all textures and materials, and delete the scene group.
   462→   *
   463→   * After teardown, the sceneId is no longer valid for renderFrame
   464→   * or teardownScene. setupScene can be called again with the same
   465→   * sceneId (fresh setup).
   466→   *
   467→   * @param sceneId - The scene to tear down.
   468→   * @returns Disposal statistics.
   469→   * @throws PageProtocolEr... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": 650,
  "limit": 200
}
[Tool Result]    650→  fog: FogConfig | null;
   651→}
   652→
   653→// Internal registry: Map<string, PageSceneEntry>
   654→// Insertion-ordered (JavaScript Map guarantees insertion order).
   655→// Managed by setupScene() and teardownScene().
   656→```
   657→
   658→## Design Decisions
   659→
   660→### D1: PageProtocol Wraps Bridge, Does Not Own It
   661→
   662→**Decision:** `PageProtocol` accepts a `PuppeteerBridge` in its constructor but does not call `bridge.launch()` or `bridge.close()`. The orchestrator (OBJ-035) owns the bridge lifecycle.
   663→
   664→**Rationale:** Separation of concerns. The bridge is a transport layer; the protocol is a domain layer. The orchestrator needs direct bridge access for `captureFrame()` (which is not a protocol concern — it's a pixel extraction concern for FFmpeg piping). Ownership nesting: orchestrator -> bridge + protocol -> page.
   665→
   666→### D2: Multi-Pass Compositing via Sequential Over-Paint
   667→
   668→**Decision:** Transitions are ex... [truncated]
Now let me check OBJ-014 (audio muxing) and OBJ-010 (page-types) since the orchestrator likely needs to invoke audio muxing and understand page initialization:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: OBJ-014 — FFmpeg Audio Muxing
     2→
     3→## Summary
     4→
     5→OBJ-014 implements the audio muxing module (`src/engine/audio-muxer.ts`) — the post-encoding stage that combines OBJ-013's video-only MP4 with an audio file (WAV or MP3) to produce the final deliverable MP4 with synchronized audio. This module covers constraint C-07 (audio synchronization) at the encoding level, making the single-pass vs. two-pass decision, handling format differences between WAV and MP3 inputs, and managing duration mismatches between video and audio streams.
     6→
     7→This module is deliberately separate from OBJ-013's `FFmpegEncoder` — it operates on completed files, not on streaming frame data. It accepts file paths, not buffers.
     8→
     9→## Interface Contract
    10→
    11→```typescript
    12→// src/engine/audio-muxer.ts
    13→
    14→/**
    15→ * Strategy for handling duration mismatches between video and audio.
    16→ *
    17→ * - 'match_shortest': Out... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "limit": 100
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
Now let me check OBJ-005 (scene geometry types) and OBJ-015 (texture loading) briefly:
[Tool: Grep]
  Input: {
  "pattern": "export interface SceneGeometry|export interface PlaneSlot|export interface CameraPathPreset",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes",
  "output_mode": "content",
  "-A": 5
}
[Tool Result] nodes/OBJ-015/transcript.md:135:   115→export interface SceneGeometry {
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/transcript.md-136-   116→  /**
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/transcript.md-137-   117→   * Unique identifier for this geometry. Must match the key used
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/transcript.md-138-   118→   * in the geometry registry. Lowercase, underscore-separated.
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/transcript.md-139-   119→   * Must match /^[a-z][a-z0-9_]*$/.
nodes/OBJ-015/transcript.md-140-   120→   * Examples: 'stage', 'tunnel', 'canyon', 'flyover'
--
nodes/OBJ-015/transcript.md:837:    51→export interface PlaneSlot extends PlaneTransform {
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/transcript.md-838-    52→  /**
/Users/austin/spatial_... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "limit": 120
}
[Tool Result]      1→# Specification: Scene Geometry Type Contract (OBJ-005)
     2→
     3→## Summary
     4→
     5→OBJ-005 defines the TypeScript type system for all scene geometries in depthkit: the `PlaneSlot` interface describing a single named position in a 3D scene, the `SceneGeometry` interface describing a complete spatial arrangement of planes, the `FogConfig` interface for depth-based atmospheric fading, a geometry registry with explicit registration and deep-freeze semantics, and the slot naming conventions that all 8 geometry implementations (OBJ-018 through OBJ-025) must follow. This is a pure type/contract module — it defines the shape of geometry data, not any specific geometry's values. It imports spatial primitives from OBJ-003 and is consumed by every downstream objective that creates, validates, instantiates, or queries scene geometries.
     6→
     7→## Interface Contract
     8→
     9→### Core Types
    10→
    11→```typescript
    12→// src/scenes/geometries/types.ts
    13... [truncated]
Let me also check OBJ-006 (camera path presets) and the OBJ-004 manifest types:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-006 — Camera Path Type Contract
     2→
     3→## Summary
     4→
     5→OBJ-006 defines the TypeScript type system for camera path presets in depthkit. A camera path preset is a named, self-contained unit that maps normalized time `t ∈ [0, 1]` to a complete camera state (`position`, `lookAt`, `fov`) and carries metadata for validation, edge-reveal prevention, and blind authoring. This is the Tier 1 contract that all downstream camera path preset implementations (OBJ-026 through OBJ-034) conform to, and that the scene sequencer (OBJ-010), edge-reveal validator (OBJ-040), and geometry-camera compatibility validator (OBJ-041) consume.
     6→
     7→## Interface Contract
     8→
     9→### Core Types
    10→
    11→```typescript
    12→// src/camera/types.ts
    13→
    14→import { Vec3, CameraState } from '../spatial/types';
    15→import { EasingName, EasingFn } from '../interpolation/easings';
    16→
    17→/**
    18→ * The path-controlled subset of camer... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: OBJ-004 — Manifest Schema Core
     2→
     3→## Summary
     4→
     5→OBJ-004 defines the Zod validation schema and loader for the depthkit manifest — the declarative JSON document that describes an entire video. This is the authoring contract between LLM manifest authors and the rendering engine. The schema enforces structural correctness (types, ranges, required fields) via Zod parsing and semantic correctness (geometry existence, camera compatibility, plane-slot matching) via a registry-backed validation pass. It satisfies C-04 (resolution/fps support) and C-10 (validate before rendering, fail fast with actionable errors).
     6→
     7→## Interface Contract
     8→
     9→### Module: `src/manifest/schema.ts`
    10→
    11→Exports Zod schemas, inferred TypeScript types, and the registry interfaces that downstream geometry/camera objectives use to register their definitions.
    12→
    13→```typescript
    14→// === Registry Interfaces ===
    15→
    16→... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": 100,
  "limit": 150
}
[Tool Result]    100→   * looks at the scene's focal point. This is intentional for
   101→   * framing adjustments (e.g., shift camera right to reframe
   102→   * the subject).
   103→   *
   104→   * Edge-reveal implication: offset displaces the frustum.
   105→   * OBJ-040 must add abs(offset[i]) to the path's displacement
   106→   * in each axis when computing required plane sizes.
   107→   *
   108→   * Default: [0, 0, 0].
   109→   */
   110→  offset?: Vec3;
   111→}
   112→
   113→/**
   114→ * Resolved and validated CameraParams, ready for preset consumption.
   115→ * Produced by resolveCameraParams(). Presets receive this, not raw CameraParams.
   116→ *
   117→ * Note: offset is NOT included here because it is applied outside
   118→ * evaluate() by the renderer. Presets only need speed and easing.
   119→ */
   120→export interface ResolvedCameraParams {
   121→  /** Guaranteed > 0. */
   122→  speed: number;
   123→  /** Resolved easing function. */
   124→  easing: EasingFn;
   125→... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "offset": 150,
  "limit": 100
}
[Tool Result]    150→- `transition_out: crossfade` — scene blends out into the following scene over `duration` seconds. Requires a following scene.
   151→- `transition_in: dip_to_black` — scene fades in from black over `duration` seconds. No preceding scene required.
   152→- `transition_out: dip_to_black` — scene fades out to black over `duration` seconds. No following scene required.
   153→- The seed's description "fade out then fade in" describes the combined effect of scene A's `transition_out: dip_to_black` + scene B's `transition_in: dip_to_black`.
   154→- `cut` — instant transition. No blending.
   155→
   156→**CameraParamsSchema** (`.strict()`):
   157→```typescript
   158→{
   159→  speed: z.number().positive().default(1.0),
   160→  easing: z.enum([
   161→    "linear",
   162→    "ease_in",
   163→    "ease_out",
   164→    "ease_in_out",
   165→    "ease_out_cubic",
   166→    "ease_in_out_cubic",
   167→  ]).default("ease_in_out"),
   168→  fov_start: z.number().min(10).max(120).opt... [truncated]
Now I have a comprehensive understanding of all the dependency interfaces. Let me compose the specification for OBJ-035.

---

# Specification: OBJ-035 — Orchestrator: Main Render Loop

## Summary

OBJ-035 delivers the `Orchestrator` class (`src/engine/orchestrator.ts`) — the top-level integration point that coordinates the entire depthkit rendering pipeline from manifest to MP4. It composes the four dependency modules (FrameClock from OBJ-009, PuppeteerBridge from OBJ-009, FrameCapture from OBJ-012, FFmpegEncoder from OBJ-013) plus the PageProtocol (OBJ-011) and manifest loader (OBJ-016) into a deterministic frame-by-frame render loop that implements seed Section 4.4 steps 1–5 at the integration level. It enforces C-02 (Puppeteer + Three.js + FFmpeg pipeline), C-03 (deterministic virtualized timing), C-05 (deterministic output), and C-10 (manifest validation before rendering). Audio muxing via OBJ-014 is integrated as an optional post-encoding step. This is the single entry point for both the CLI (OBJ-048) and the programmatic library API.

## Interface Contract

### Module: `src/engine/orchestrator.ts`

```typescript
import type { Manifest, ManifestRegistry, ManifestResult } from '../manifest/schema.js';
import type { FFmpegEncoderResult } from './ffmpeg-encoder.js';
import type { AudioMuxerResult } from './audio-muxer.js';
import type { CaptureStats } from './frame-capture.js';
import type { RendererInfo } from './protocol-types.js';

// ────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────

/**
 * Configuration for the Orchestrator.
 * Provides the manifest (or raw JSON to validate), registry,
 * and optional tuning knobs for the rendering pipeline.
 */
export interface OrchestratorConfig {
  /**
   * The manifest to render. Accepts either:
   * - A pre-validated `Manifest` object (skips Phase 1+2 validation).
   * - A raw `unknown` value (runs full validation via loadManifest()).
   *
   * When a pre-validated Manifest is provided, the orchestrator still
   * runs semantic validation against the registry (Phase 2 only) to
   * catch registry mismatches. To skip ALL validation, use the
   * `skipValidation` flag (testing/debugging only).
   */
  manifest: Manifest | unknown;

  /**
   * The manifest registry containing registered geometries and cameras.
   * Required for semantic validation and for resolving geometry slot
   * positions and camera path evaluators at render time.
   */
  registry: ManifestRegistry;

  /**
   * Directory containing image assets referenced by the manifest's
   * plane `src` paths. If manifest paths are absolute, this is ignored.
   * If manifest paths are relative, they are resolved against this
   * directory using path.resolve(assetsDir, src).
   *
   * Default: process.cwd()
   */
  assetsDir?: string;

  /**
   * Output file path for the final MP4 (with audio if applicable).
   * Parent directory must exist.
   */
  outputPath: string;

  /**
   * Capture strategy for pixel extraction from the headless browser.
   * Default: 'viewport-png'.
   */
  captureStrategy?: 'viewport-png' | 'canvas-png';

  /**
   * H.264 encoding preset. Default: 'medium'.
   */
  encodingPreset?: 'ultrafast' | 'superfast' | 'veryfast' | 'faster'
    | 'fast' | 'medium' | 'slow' | 'slower' | 'veryslow';

  /**
   * Constant Rate Factor for encoding quality. Default: 23.
   */
  crf?: number;

  /**
   * Enable GPU-accelerated rendering. Default: false.
   * When false: software WebGL via SwiftShader (C-11).
   */
  gpu?: boolean;

  /**
   * Path to FFmpeg binary. If not provided, uses resolveFFmpegPath().
   */
  ffmpegPath?: string;

  /**
   * Path to Chromium executable. If not provided, uses Puppeteer's
   * bundled Chromium.
   */
  chromiumPath?: string;

  /**
   * Skip manifest validation entirely. Default: false.
   * WARNING: Only for testing/debugging. Rendering an invalid
   * manifest with skipValidation=true produces undefined behavior.
   */
  skipValidation?: boolean;

  /**
   * Forward headless browser console messages to Node's stdout.
   * Default: false.
   */
  debug?: boolean;

  /**
   * Progress callback invoked after each frame is captured and
   * written to FFmpeg. Allows the caller to display progress bars,
   * log throughput, or implement cancellation.
   *
   * Return `false` from the callback to request cancellation.
   * The orchestrator will abort the render after the current frame
   * completes and throw an OrchestratorError with code 'CANCELLED'.
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
  /** Progress as a ratio [0, 1]. frame / totalFrames. */
  ratio: number;
  /** Elapsed wall-clock time in milliseconds since render start. */
  elapsedMs: number;
  /** Estimated time remaining in milliseconds (based on average frame time). */
  estimatedRemainingMs: number;
  /** Frames per second throughput (rendered frames / elapsed seconds). */
  fps: number;
  /** The active scene ID being rendered. */
  activeSceneId: string;
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

  /** Total wall-clock rendering time in milliseconds. */
  totalDurationMs: number;

  /** Average milliseconds per frame (totalDurationMs / totalFrames). */
  averageFrameMs: number;

  /** Video duration in seconds (totalFrames / fps). */
  videoDurationSeconds: number;

  /** Capture statistics from OBJ-012's FrameCapture. */
  captureStats: CaptureStats;

  /** FFmpeg encoding result from OBJ-013. */
  encoderResult: FFmpegEncoderResult;

  /** Audio muxing result from OBJ-014. null if no audio. */
  audioResult: AudioMuxerResult | null;

  /** WebGL renderer info from the headless browser. */
  rendererInfo: RendererInfo;

  /** Validation warnings (non-blocking) from manifest validation. */
  warnings: string[];
}

// ────────────────────────────────────────────
// Errors
// ────────────────────────────────────────────

export type OrchestratorErrorCode =
  | 'MANIFEST_INVALID'      // Manifest validation failed
  | 'BROWSER_LAUNCH_FAILED' // Puppeteer/Chromium failed to start
  | 'PAGE_INIT_FAILED'      // Three.js page initialization failed
  | 'SCENE_SETUP_FAILED'    // Scene setup (texture loading) failed
  | 'RENDER_FAILED'         // Frame rendering failed
  | 'CAPTURE_FAILED'        // Frame capture failed
  | 'ENCODE_FAILED'         // FFmpeg encoding failed
  | 'AUDIO_MUX_FAILED'      // Audio muxing failed
  | 'CANCELLED'             // Cancelled via onProgress callback
  ;

/**
 * Structured error from the orchestrator.
 */
export class OrchestratorError extends Error {
  readonly code: OrchestratorErrorCode;
  /** Frame number where the error occurred (if applicable). */
  readonly frame?: number;
  /** The original error that caused this failure. */
  readonly cause?: Error;

  constructor(
    code: OrchestratorErrorCode,
    message: string,
    options?: { frame?: number; cause?: Error }
  );
}

// ────────────────────────────────────────────
// Main Class
// ────────────────────────────────────────────

/**
 * The main rendering orchestrator for depthkit.
 *
 * Composes the full pipeline:
 *   1. Validate manifest (OBJ-016)
 *   2. Compute total duration and frame count (OBJ-009 FrameClock)
 *   3. Launch headless Chromium (OBJ-009 PuppeteerBridge)
 *   4. Initialize Three.js renderer (OBJ-011 PageProtocol)
 *   5. Spawn FFmpeg encoder (OBJ-013)
 *   6. For each scene, in start_time order:
 *      a. Setup scene on the page (load textures, create meshes)
 *      b. For each frame in the scene's time range:
 *         i.   Compute camera state from camera path preset
 *         ii.  Send RenderFrameCommand to page via PageProtocol
 *         iii. Capture frame via FrameCapture (OBJ-012)
 *         iv.  Pipe frame buffer to FFmpeg via writeFrame()
 *      c. Teardown scene (release textures/meshes)
 *   7. Finalize FFmpeg encoding
 *   8. Mux audio (OBJ-014) if manifest specifies an audio track
 *   9. Close browser, return result
 *
 * The orchestrator owns the lifecycle of all sub-components.
 * It creates, starts, and closes them. Callers do not interact
 * with PuppeteerBridge, PageProtocol, FrameCapture, or
 * FFmpegEncoder directly.
 *
 * NOT reusable — one orchestrator instance per render.
 * Thread-safety: NOT safe for concurrent use. One render at a time.
 *
 * Scene transition rendering (crossfade, dip_to_black) is handled
 * in V1 with a simplified model: for frames within a transition
 * window, the orchestrator sets up both the outgoing and incoming
 * scenes simultaneously and sends multi-pass RenderFrameCommands
 * with computed opacity values. OBJ-036 (scene sequencer) will
 * later extract this logic into a dedicated module; the
 * orchestrator's internal scene iteration is designed to be
 * replaceable by OBJ-036's sequencer without changing the public API.
 *
 * Usage:
 *   const orchestrator = new Orchestrator(config);
 *   const result = await orchestrator.render();
 */
export class Orchestrator {
  constructor(config: OrchestratorConfig);

  /**
   * Execute the full rendering pipeline.
   *
   * This is the sole public method. It runs the complete pipeline
   * from validation through final MP4 output.
   *
   * Lifecycle guarantees:
   * - All sub-resources (browser, FFmpeg process) are cleaned up
   *   on both success and failure. If render() throws, the browser
   *   is closed and the FFmpeg process is aborted.
   * - Partial output files (incomplete MP4) are deleted on failure.
   *   The outputPath is only populated with a valid file on success.
   *
   * @returns OrchestratorResult on success.
   * @throws OrchestratorError on any failure, with appropriate code.
   */
  render(): Promise<OrchestratorResult>;
}

// ────────────────────────────────────────────
// Convenience Function
// ────────────────────────────────────────────

/**
 * Convenience wrapper: validates manifest from file, creates an
 * Orchestrator, and calls render().
 *
 * This is the simplest programmatic entry point.
 *
 * @param manifestPath - Path to the manifest JSON file.
 * @param registry - Populated ManifestRegistry.
 * @param options - Additional OrchestratorConfig options (outputPath required).
 * @returns OrchestratorResult on success.
 * @throws OrchestratorError on any failure.
 */
export async function renderFromFile(
  manifestPath: string,
  registry: ManifestRegistry,
  options: Omit<OrchestratorConfig, 'manifest' | 'registry'>,
): Promise<OrchestratorResult>;
```

## Design Decisions

### D1: Single `render()` Method, No Exposed Sub-Components

**Decision:** The `Orchestrator` class exposes only `render()`. Callers cannot access the PuppeteerBridge, PageProtocol, FrameCapture, or FFmpegEncoder directly.

**Rationale:** The orchestrator is the integration point — it owns the lifecycle of all sub-components. Exposing internal components would allow callers to interfere with the deterministic render loop (violating C-03) or to leak resources (e.g., not closing the browser). The CLI (OBJ-048) and n8n endpoint (OBJ-057) only need `render()`.

**Alternative considered:** A multi-step API (`orchestrator.validate()`, `orchestrator.setup()`, `orchestrator.renderFrames()`, `orchestrator.finalize()`). Rejected because it shifts lifecycle management to the caller, creating more failure modes. If fine-grained control is needed later, it can be added as protected methods or a separate `PipelineBuilder` without changing the public API.

### D2: Orchestrator Owns All Resource Cleanup

**Decision:** `render()` uses a try/finally pattern to guarantee that all sub-resources (PuppeteerBridge, FFmpeg process, temporary files) are cleaned up on both success and failure. On failure, partial output files are deleted.

**Rationale:** C-10 requires "fail fast, fail clearly." A failed render must not leave zombie Chromium processes, open FFmpeg pipes, or corrupted partial MP4 files. The orchestrator is the only component that knows about all resources, so it must own cleanup.

**Cleanup order on failure:**
1. Abort FFmpeg encoder (kills process, does not delete partial file).
2. Close PuppeteerBridge (kills Chromium).
3. Delete partial output file(s) at outputPath.
4. Throw OrchestratorError.

### D3: Scene Iteration With Inline Transition Handling

**Decision:** In V1, the orchestrator iterates through frames linearly (via FrameClock.frames()), determining for each frame which scene(s) are active and constructing the appropriate `RenderFrameCommand` (single-pass for normal frames, multi-pass for transition frames). This logic lives inside the orchestrator as private methods.

**Rationale:** OBJ-036 (scene sequencer) will later extract the per-scene routing and transition logic into a dedicated module. But OBJ-035 must be functional without OBJ-036 — it is OBJ-036's dependency, not the other way around. The orchestrator's internal scene iteration methods are structured to be replaceable: OBJ-036 can provide a `SceneSequencer` that the orchestrator delegates to, without changing the orchestrator's public API.

**Internal scene iteration algorithm:**

1. Sort scenes by `start_time` (stable sort, preserving array order for equal start times).
2. For each frame tick from FrameClock:
   a. Compute absolute timestamp: `tick.timestamp`.
   b. Find the "active scene" — the scene whose time range `[start_time, start_time + duration)` contains the timestamp.
   c. Check for transition windows:
      - If the timestamp is in the **transition_out** window of the active scene AND the **transition_in** window of the next scene, compute transition progress and generate a multi-pass command.
      - Otherwise, generate a single-pass command.
   d. For scenes that need to be set up but aren't yet on the page, call `protocol.setupScene()`.
   e. For scenes that are past their time range and no longer needed for transitions, call `protocol.teardownScene()` to free GPU memory.

**Scene setup strategy (lazy, one-ahead):**
- A scene is set up on the page when it is first needed: either when its time range starts, or when a preceding scene's transition_out begins (which may require the next scene to be visible for crossfade).
- A scene is torn down after its time range ends AND it is no longer needed by any transition window.
- This keeps at most 2 scenes active on the page simultaneously (the minimum for transitions).

### D4: Camera State Computation Per Frame

**Decision:** For each frame, the orchestrator:
1. Looks up the active scene's geometry definition from the registry.
2. Looks up the active scene's camera path preset from the registry.
3. Computes per-scene normalized time `t`: `(tick.timestamp - scene.start_time) / scene.duration`, clamped to [0, 1].
4. Calls the camera path's `evaluate(t, scene.camera_params)` to get `CameraFrameState`.
5. Applies `camera_params.offset` (if any) to the position.
6. Converts `CameraFrameState` to `RequiredCameraState` for the protocol.

**Rationale:** Camera state is computed fresh per frame from the path evaluator. No caching, no state carried between frames. This aligns with C-03 (deterministic) and with OBJ-006's stateless `CameraPathEvaluator` contract.

### D5: Geometry-to-SlotSetup Mapping

**Decision:** When setting up a scene on the page, the orchestrator maps manifest plane references to `SlotSetup` objects by:
1. Looking up the scene's geometry in the registry to get `SceneGeometry.slots`.
2. For each plane key in the manifest's `scene.planes`:
   a. Get the geometry's `PlaneSlot` for that key (position, rotation, size, transparent, fogImmune, renderOrder).
   b. Apply any `position_override` or `rotation_override` from the manifest's `PlaneRef`.
   c. Apply `scale` from `PlaneRef` by multiplying geometry slot `size` by `scale`.
   d. Resolve the image `src` path (relative to `assetsDir` if not absolute).
   e. Construct the `SlotSetup` object.
3. Pass the assembled `SceneSetupConfig` to `protocol.setupScene()`.

**Rationale:** The orchestrator is the translation layer between the declarative manifest and the imperative page protocol. The manifest says "geometry: tunnel, planes: { floor: { src: './images/floor.png' } }"; the orchestrator looks up the tunnel geometry's floor slot, resolves the image path, and sends the complete `SlotSetup` with position/rotation/size to the page.

### D6: Audio Muxing as Post-Encoding Step

**Decision:** If the manifest specifies `composition.audio`, the orchestrator:
1. First renders the video-only MP4 to a temporary path (e.g., `{outputPath}.video.mp4`).
2. Then calls the AudioMuxer (OBJ-014) to combine video + audio into the final `outputPath`.
3. Deletes the temporary video-only MP4.

If no audio is specified, the video-only MP4 is written directly to `outputPath`.

**Rationale:** OBJ-013's FFmpegEncoder produces video-only output (by design — D-04 in OBJ-013). Audio muxing is a separate FFmpeg pass via OBJ-014. This keeps encoding simple and allows the audio to be processed independently.

### D7: Manifest Validation Gate

**Decision:** Before any rendering begins, the orchestrator validates the manifest. If validation fails, `render()` throws `OrchestratorError` with code `MANIFEST_INVALID`. The error message includes all validation errors formatted as a multi-line string.

**Rationale:** C-10: "Invalid manifests must never produce partial output — fail fast, fail clearly." The orchestrator is the enforcement point. No Puppeteer launch, no FFmpeg spawn, no resource allocation until the manifest is confirmed valid.

### D8: Image Path Resolution

**Decision:** Manifest `PlaneRef.src` paths are resolved as follows:
1. If the path is absolute (starts with `/`): used as-is.
2. If the path is relative: resolved via `path.resolve(config.assetsDir ?? process.cwd(), src)`.
3. If the path starts with `http://`, `https://`, or `data:`: passed through as-is (the page handler supports these formats per OBJ-011).

The resolved path is passed to `SlotSetup.textureSrc` which the page handler converts to a `file://` URL for Three.js TextureLoader (OBJ-011 D6).

**Rationale:** The manifest is authored relative to an assets directory (typical LLM workflow: generate images into `./assets/images/`, reference them as `./images/scene1_floor.png`). The orchestrator resolves paths once at setup time.

### D9: Progress Callback and Cancellation

**Decision:** The optional `onProgress` callback is invoked after each frame is written to FFmpeg (not after capture, and not after render — after the complete frame pipeline). If the callback returns `false`, the orchestrator aborts the render cleanly.

**Rationale:** Progress reporting is essential for the CLI (progress bar) and the n8n endpoint (status polling). Cancellation via the callback is the simplest mechanism — no separate `abort()` method needed.

### D10: One Orchestrator Instance Per Render

**Decision:** The `Orchestrator` is not reusable. After `render()` completes (or fails), the instance is spent. Creating a new `Orchestrator` for a new render is the intended pattern.

**Rationale:** Reusable orchestrators require complex state management (reset sub-components, re-validate). One-shot instances are simpler, match the CLI pattern (one render per invocation), and prevent stale state.

### D11: Temporary Video File Naming

**Decision:** When audio muxing is needed, the temporary video-only MP4 is written to `{outputPath}.tmp.video.mp4`. After successful mux, it is deleted. On failure, both the temporary file and any partial final output are deleted.

**Rationale:** Naming the temp file adjacent to the output (same directory, predictable name) avoids cross-filesystem issues and makes debugging easy — if cleanup fails, the temp file is identifiable.

### D12: Scene Sorted by start_time at Render Time

**Decision:** The orchestrator sorts scenes by `start_time` before rendering. This sorting uses the same stable sort as OBJ-016's validation. If scenes are not in start_time order in the manifest, the orchestrator silently sorts them (OBJ-016 already emits a warning for this).

**Rationale:** The render loop iterates frames linearly by timestamp. Scenes must be in temporal order for the "active scene" lookup to work correctly.

### D13: Transition Overlap Rendering

**Decision:** For crossfade transitions, the orchestrator computes:
- `overlap_start = scene_B.start_time` (when scene B begins)
- `overlap_end = scene_A.start_time + scene_A.duration` (when scene A ends)
- `overlap_duration = overlap_end - overlap_start`
- For a frame at timestamp `t` within the overlap window:
  - `progress = (t - overlap_start) / overlap_duration`
  - Passes: `[{ sceneId: A, opacity: 1.0, camera: A_cam }, { sceneId: B, opacity: progress, camera: B_cam }]`

For dip_to_black:
- Scene A fade-out: opacity = `1 - progress_A` where `progress_A = (t - fade_out_start) / transition_out.duration`
- Scene B fade-in: opacity = `progress_B` where `progress_B = (t - scene_B.start_time) / transition_in.duration`
- These may not overlap temporally — dip_to_black can have a gap of black frames between scenes.

For cut transitions: single-pass, opacity 1.0. Scene switches instantly at the boundary frame.

**Rationale:** This matches OBJ-011's multi-pass compositing model (D2 in OBJ-011). The crossfade algorithm — pass A at 1.0, pass B at progress — produces the correct `A * (1-p) + B * p` blend for opaque scenes.

### D14: Lazy Scene Setup, Eager Teardown

**Decision:** Scenes are set up on the page "just in time" — when a frame first needs them. Scenes are torn down "as soon as possible" — when the last frame that needs them has been rendered. The orchestrator tracks which scenes are currently active on the page.

**Implementation logic:**
- Before rendering frame N at timestamp T:
  1. Determine which scene IDs are needed for this frame (1 or 2 during transitions).
  2. For each needed scene not yet set up: call `protocol.setupScene()`.
  3. For each currently-active scene no longer needed: call `protocol.teardownScene()`.

**Rationale:** Minimizes GPU memory usage — at most 2 scenes with their textures are loaded simultaneously. Important for the 4GB RAM constraint in C-08. Eager teardown frees texture memory for subsequent scenes.

### D15: Geometry and Camera Preset Lookup

**Decision:** The orchestrator resolves geometry definitions and camera path presets from the registry at the start of rendering (after validation). It builds a lookup map: `scene.id -> { geometry: SceneGeometry, cameraPreset: CameraPathPreset }`. These are resolved once and reused for every frame.

**Rationale:** Looking up geometries and camera presets per-frame is wasteful. They don't change during rendering. Resolving upfront also catches any registry inconsistencies before the expensive render loop begins.

**Dependency note:** This requires the registry to contain not just the `GeometryRegistration`/`CameraRegistration` used for validation (OBJ-004), but also the full `SceneGeometry` (OBJ-005) and `CameraPathPreset` (OBJ-006) objects. The orchestrator imports both registry types. The `ManifestRegistry` maps names to validation metadata; a separate lookup (e.g., the OBJ-005 geometry registry and OBJ-006 camera registry) provides the full objects.

Actually, looking at OBJ-005's interface more carefully — OBJ-005 has its own geometry registry (`GeometryRegistry`), and OBJ-006 likely has a camera path registry. The orchestrator needs to accept these registries alongside the ManifestRegistry. Let me refine:

```typescript
// Additional imports for orchestrator config:
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

export interface OrchestratorConfig {
  // ... existing fields ...

  /**
   * The geometry registry containing full SceneGeometry definitions.
   * Used to resolve slot positions, rotations, and sizes for scene setup.
   * This is distinct from ManifestRegistry's GeometryRegistration, which
   * contains only validation metadata (slot names, compatible cameras).
   */
  geometryRegistry: GeometryRegistry;

  /**
   * The camera path registry containing full CameraPathPreset definitions.
   * Used to evaluate camera positions per frame.
   * This is distinct from ManifestRegistry's CameraRegistration, which
   * contains only validation metadata.
   */
  cameraRegistry: CameraPathRegistry;
}
```

Wait — let me check whether OBJ-005 and OBJ-006 define separate registries or if ManifestRegistry contains the full definitions.
[Tool: Grep]
  Input: {
  "pattern": "GeometryRegistry|registerGeometry|getGeometry",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "output_mode": "content",
  "-C": 3
}
[Tool Result] 201- * - Spatial compatibility validator (OBJ-041) to cross-reference
202- *   geometry + camera compatibility.
203- */
204:export type GeometryRegistry = Record<string, SceneGeometry>;
205-```
206-
207-### Registry Access Functions
--
209-```typescript
210-// src/scenes/geometries/registry.ts
211-
212:import type { SceneGeometry, GeometryRegistry } from './types';
213-
214-/**
215- * Returns the complete registry of all registered scene geometries.
216- *
217- * On first call, the registry is locked — no further registrations
218: * are accepted (see D10). Returns a deeply frozen GeometryRegistry.
219- * Subsequent calls return the same frozen object.
220- *
221- * Mutation attempts on the returned object or any nested object
222- * (geometry, slot, position tuple) throw TypeError at runtime.
223- *
224: * @returns A deeply frozen GeometryRegistry.
225- */
226:export function getGeometryRegistry(): Readonly<GeometryRegistry>;
227-
228-/**
229- * Retrieves a single geometry by name.
23... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "CameraPathRegistry|registerCamera|getCamera",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "output_mode": "content",
  "-C": 3
}
[Tool Result] 299- *
300- * Keys are preset names (lowercase snake_case). Values are CameraPathPreset objects.
301- */
302:export type CameraPathRegistry = Readonly<Record<string, CameraPathPreset>>;
303-
304-/**
305- * Retrieves a camera path preset by name.
--
309- * @throws {Error} if name is not found. Error message includes the
310- *   invalid name and lists all available preset names.
311- */
312:export function getCameraPath(
313:  registry: CameraPathRegistry,
314-  name: string
315-): CameraPathPreset;
316-
--
318- * Type guard: checks if a name exists in the given registry.
319- */
320-export function isCameraPathName(
321:  registry: CameraPathRegistry,
322-  name: string
323-): boolean;
324-
--
326- * Returns all preset names in the registry, sorted alphabetically.
327- */
328-export function listCameraPathNames(
329:  registry: CameraPathRegistry
330-): readonly string[];
331-
332-/**
--
335- * @param geometryName - The geometry to filter by.
336- * @returns Array of compatible CameraP... [truncated]
Now I have a complete picture. Let me propose the specification.

---

# Specification: OBJ-035 — Orchestrator: Main Render Loop

## Summary

OBJ-035 delivers the `Orchestrator` class (`src/engine/orchestrator.ts`) — the top-level integration point that coordinates the entire depthkit rendering pipeline from manifest to MP4. It composes FrameClock and PuppeteerBridge (OBJ-009), FrameCapture (OBJ-012), FFmpegEncoder (OBJ-013), AudioMuxer (OBJ-014), PageProtocol (OBJ-011), and the manifest loader (OBJ-016) into a deterministic frame-by-frame render loop implementing seed Section 4.4 steps 1–5. It enforces C-02 (Puppeteer + Three.js + FFmpeg pipeline), C-03 (deterministic virtualized timing), C-05 (deterministic output), and C-10 (manifest validation before rendering). This is the single entry point for both the CLI (OBJ-048) and the programmatic library API.

## Interface Contract

### Module: `src/engine/orchestrator.ts`

```typescript
import type { Manifest, ManifestRegistry, ManifestError } from '../manifest/schema.js';
import type { FFmpegEncoderResult } from './ffmpeg-encoder.js';
import type { AudioMuxerResult } from './audio-muxer.js';
import type { CaptureStats, CaptureStrategy } from './frame-capture.js';
import type { RendererInfo } from './protocol-types.js';
import type { H264Preset } from './ffmpeg-encoder.js';
import type { CameraPathRegistry } from '../camera/types.js';

// ────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────

/**
 * Configuration for the Orchestrator.
 */
export interface OrchestratorConfig {
  /**
   * The manifest to render. Accepts either:
   * - A pre-validated `Manifest` object (has already passed Phase 1
   *   Zod parsing). The orchestrator still runs Phase 2 semantic
   *   validation against the registry.
   * - A raw `unknown` value (runs full Phase 1 + Phase 2 validation
   *   via loadManifest()).
   *
   * The orchestrator distinguishes these by checking for a `version`
   * property with value "3.0" — if present and the value has the
   * Manifest shape, it is treated as pre-validated.
   *
   * To skip ALL validation (testing/debugging only), set
   * `skipValidation: true`.
   */
  manifest: Manifest | unknown;

  /**
   * The manifest registry containing registered geometries and cameras.
   * Required for semantic validation (OBJ-016 Phase 2).
   */
  registry: ManifestRegistry;

  /**
   * The camera path registry containing full CameraPathPreset objects.
   * Used to call evaluate(t, params) per frame for camera positioning.
   * Distinct from ManifestRegistry's CameraRegistration (validation-only).
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
   * WARNING: Only for testing/debugging. Rendering an invalid
   * manifest with skipValidation=true produces undefined behavior.
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
  /** Progress ratio [0, 1]. (frame + 1) / totalFrames. */
  ratio: number;
  /** Elapsed wall-clock time in milliseconds since render start. */
  elapsedMs: number;
  /**
   * Estimated remaining time in milliseconds.
   * Computed as: (totalFrames - frame - 1) * (elapsedMs / (frame + 1)).
   * 0 on the last frame.
   */
  estimatedRemainingMs: number;
  /** Throughput: (frame + 1) / (elapsedMs / 1000). Rendered fps. */
  throughputFps: number;
  /** The active scene ID being rendered for this frame. */
  activeSceneId: string;
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

  /** Total wall-clock rendering time in milliseconds
   *  (from start of frame loop to FFmpeg finalize, excluding audio mux). */
  renderDurationMs: number;

  /** Total wall-clock time including validation, setup, audio mux. */
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
  | 'SCENE_SETUP_FAILED'    // Scene setup (texture loading) failed critically
  | 'RENDER_FAILED'         // Frame rendering failed on the page
  | 'CAPTURE_FAILED'        // Frame capture failed (FrameCapture error)
  | 'ENCODE_FAILED'         // FFmpeg encoding failed
  | 'AUDIO_MUX_FAILED'      // Audio muxing failed (OBJ-014)
  | 'CANCELLED'             // Cancelled via onProgress callback
  | 'GEOMETRY_NOT_FOUND'    // Geometry definition missing from registry at render time
  | 'CAMERA_NOT_FOUND'      // Camera preset missing from cameraRegistry at render time
  ;

/**
 * Structured error from the orchestrator.
 */
export class OrchestratorError extends Error {
  readonly code: OrchestratorErrorCode;
  /** Frame number where the error occurred (if applicable). -1 if not frame-related. */
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
 *   Phase A — Validation & Setup:
 *   1. Validate manifest against registry (OBJ-016). Fail-fast on error (C-10).
 *   2. Resolve geometry definitions and camera presets for all scenes.
 *   3. Compute total duration and frame count via FrameClock (OBJ-009).
 *   4. Resolve all image paths.
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
 *      d. Construct RenderFrameCommand (single or multi-pass for transitions).
 *      e. protocol.renderFrame(command)
 *      f. capture.capture()
 *      g. encoder.writeFrame(result.data)
 *      h. Eager-teardown scenes no longer needed.
 *      i. Invoke onProgress callback; abort if it returns false.
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
 * logic into a dedicated module; the orchestrator's internal scene
 * iteration is designed as private methods replaceable by OBJ-036.
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
 * @param cameraRegistry - Populated CameraPathRegistry.
 * @param options - Remaining OrchestratorConfig options (outputPath required).
 * @returns OrchestratorResult.
 * @throws OrchestratorError on any failure (including file not found, invalid JSON).
 */
export async function renderFromFile(
  manifestPath: string,
  registry: ManifestRegistry,
  cameraRegistry: CameraPathRegistry,
  options: Omit<OrchestratorConfig, 'manifest' | 'registry' | 'cameraRegistry'>,
): Promise<OrchestratorResult>;
```

## Design Decisions

### D1: Single `render()` Method, No Exposed Sub-Components

**Decision:** The `Orchestrator` exposes only `render()`. PuppeteerBridge, PageProtocol, FrameCapture, and FFmpegEncoder are internal and inaccessible to callers.

**Rationale:** The orchestrator is the integration point — it owns the lifecycle of all sub-components. Exposing internals would allow callers to interfere with the deterministic render loop (violating C-03) or leak resources. The CLI and n8n endpoint only need `render()`. If fine-grained control is needed later, it can be added as a separate `PipelineBuilder` class.

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
   d. Construct `RenderFrameCommand` with appropriate passes.

**Rationale:** OBJ-036 (scene sequencer) depends on OBJ-035 — so the orchestrator must be functional without OBJ-036. The private methods are structured so OBJ-036 can later provide a `SceneSequencer` interface that the orchestrator delegates to.

### D4: Camera State Computation Per Frame

**Decision:** For each frame, the orchestrator:
1. Computes per-scene normalized time: `t = clamp((tick.timestamp - scene.start_time) / scene.duration, 0, 1)`.
2. Calls `cameraPreset.evaluate(t, scene.camera_params)` to get `CameraFrameState`.
3. Applies `camera_params.offset` (if any) additively to the returned position: `position[i] += offset[i]`.
4. Constructs `RequiredCameraState` for the RenderPass: `{ position, lookAt, fov }`.

**Rationale:** Camera state is stateless per OBJ-006's `CameraPathEvaluator` contract. Fresh computation per frame with no carried state aligns with C-03 and C-05.

### D5: Geometry Slot to SlotSetup Mapping

**Decision:** When setting up a scene, the orchestrator:
1. Looks up `SceneGeometry` by name from OBJ-005's `getGeometry()`.
2. For each plane key in the manifest scene's `planes` record:
   a. Gets the geometry's `PlaneSlot` for that key.
   b. Applies `position_override` from `PlaneRef` if present (replaces the slot's position entirely).
   c. Applies `rotation_override` from `PlaneRef` if present (replaces the slot's rotation entirely).
   d. Applies `scale` from `PlaneRef` by multiplying `slot.size[0] * scale` and `slot.size[1] * scale`.
   e. Resolves image `src` path (relative to `assetsDir` if not absolute).
   f. Constructs `SlotSetup`: `{ position, rotation, size, textureSrc, transparent: slot.transparent, renderOrder: slot.renderOrder, fogImmune: slot.fogImmune }`.
3. Constructs `SceneSetupConfig`: `{ sceneId: scene.id, slots, fog: geometry.fog }`.
4. Calls `protocol.setupScene(config)`.

**Rationale:** The orchestrator is the translation layer between the declarative manifest and the imperative page protocol. The manifest specifies slot names and image paths; the orchestrator resolves the spatial data from the geometry and constructs the full setup.

### D6: Audio Muxing as Post-Encoding Step

**Decision:** If `manifest.composition.audio` is defined:
1. Render video to a temporary path: `{outputPath}.tmp.video.mp4`.
2. Mux audio via OBJ-014's `AudioMuxer` with `durationStrategy: 'match_audio'`.
3. Delete the temporary video-only file on success.

If no audio, write video-only MP4 directly to `outputPath`.

**Rationale:** OBJ-013 produces video-only output by design. Audio muxing is a cheap separate FFmpeg pass (`-c:v copy`) that adds negligible time.

### D7: Manifest Validation Gate (C-10)

**Decision:** Before any resource allocation, the orchestrator validates the manifest. If validation fails, `render()` throws `OrchestratorError` with code `MANIFEST_INVALID`, containing all `ManifestError` objects in the `validationErrors` property.

No PuppeteerBridge launch, no FFmpeg spawn until validation passes.

**Rationale:** C-10: "Invalid manifests must never produce partial output — fail fast, fail clearly."

### D8: Image Path Resolution

**Decision:** Image `src` paths from the manifest are resolved:
1. Absolute path (starts with `/`): used as-is.
2. Protocol prefix (`http://`, `https://`, `data:`): passed through as-is.
3. Relative path: `path.resolve(config.assetsDir ?? process.cwd(), src)`.

Resolved paths are validated for existence (via `fs.access`) before scene setup. Missing files cause `OrchestratorError` with code `SCENE_SETUP_FAILED` — failing before the render loop starts rather than mid-render when a texture load fails on the page.

**Rationale:** Failing fast on missing images saves time. Discovering a missing image at frame 900 of 1800 wastes half the render. Pre-flight checks catch this before any rendering begins.

### D9: Progress Callback and Cancellation

**Decision:** `onProgress` is invoked after each frame is fully processed (rendered + captured + written to FFmpeg). If it returns `false`, the orchestrator:
1. Aborts the FFmpeg encoder.
2. Disposes page protocol and closes browser.
3. Deletes partial output.
4. Throws `OrchestratorError` with code `CANCELLED`.

**Rationale:** Post-write invocation ensures accurate throughput stats. Cancellation via return value is simpler than a separate abort signal.

### D10: One Instance Per Render

**Decision:** `Orchestrator` is not reusable. `render()` can be called once. A second call throws `OrchestratorError` with code `RENDER_FAILED` and message indicating the orchestrator has already been used.

**Rationale:** Reusable orchestrators require complex reset logic. One-shot instances are simpler and match the production pattern.

### D11: Temporary Video File Naming

**Decision:** When audio muxing is needed, the temp video file is `{outputPath}.tmp.video.mp4`. Deleted on success. Deleted on failure.

**Rationale:** Predictable naming in the same directory avoids cross-filesystem issues.

### D12: Geometry and Camera Preset Resolution at Render Start

**Decision:** After validation passes, the orchestrator resolves the full `SceneGeometry` and `CameraPathPreset` for every scene upfront, building a `Map<string, { geometry: SceneGeometry, cameraPreset: CameraPathPreset }>` keyed by scene ID. If any geometry or camera is not found in the spatial registries (despite passing manifest validation), throws `OrchestratorError` with `GEOMETRY_NOT_FOUND` or `CAMERA_NOT_FOUND`.

**Rationale:** Catches registry inconsistencies before the render loop. Looking up per-frame is wasteful.

### D13: Transition Rendering Algorithm

**Decision:** The orchestrator computes transition state per-frame:

**Crossfade** (scene A transition_out -> scene B transition_in):
- Overlap window: `[B.start_time, A.start_time + A.duration]`.
- Progress `p = (timestamp - B.start_time) / (A.start_time + A.duration - B.start_time)`, clamped to [0, 1].
- Passes: `[{ sceneId: A, opacity: 1.0, camera: A_state }, { sceneId: B, opacity: p, camera: B_state }]`.
- This matches OBJ-011 D2's compositing model: `B * p + A * (1-p)` for opaque scenes.

**Dip-to-black** (scene A transition_out):
- Fade-out window: `[A.start_time + A.duration - A.transition_out.duration, A.start_time + A.duration]`.
- Progress `p_out = (timestamp - fade_out_start) / transition_out.duration`, clamped to [0, 1].
- Pass: `[{ sceneId: A, opacity: 1 - p_out, camera: A_state }]`.
- The clear color (black) shows through.

**Dip-to-black** (scene B transition_in):
- Fade-in window: `[B.start_time, B.start_time + B.transition_in.duration]`.
- Progress `p_in = (timestamp - B.start_time) / transition_in.duration`, clamped to [0, 1].
- Pass: `[{ sceneId: B, opacity: p_in, camera: B_state }]`.

**Cut**: Single pass, opacity 1.0. Scene switches instantly at boundary frame.

**Easing on transitions:** Transition progress values are NOT eased in V1 — linear opacity ramps. If transition easing is needed, it can be added in OBJ-036.

### D14: Lazy Scene Setup, Eager Teardown

**Decision:**
- A scene is set up when first needed: at its `start_time`, or earlier if a preceding scene's crossfade transition requires the next scene to be present.
- A scene is torn down when the last frame that references it has been rendered.
- At most 2 scenes are active simultaneously (for transitions).

**Implementation:**
- Track `Set<string>` of scene IDs currently active on the page.
- Before each frame: compute needed scene IDs. Setup any not in the active set. After each frame: teardown any in the active set that are no longer needed.

**Rationale:** Minimizes GPU memory — critical for the 4GB RAM constraint in C-08. A 5-scene video never has more than 2 scenes' textures loaded at once.

### D15: Pre-Flight Image Existence Check

**Decision:** After manifest validation, before launching the browser, the orchestrator resolves all image paths across all scenes and checks each with `fs.access(path, fs.constants.R_OK)`. Missing or unreadable files cause immediate failure with `OrchestratorError` code `SCENE_SETUP_FAILED`, listing all missing files.

**Rationale:** This is an extension of C-10's "fail fast" principle. Texture load failures on the page (OBJ-011) produce magenta fallback meshes — usable for debugging but wrong for production. Pre-flight checks catch the common case (typo in path, missing asset generation step) before any expensive operations.

**Exception:** Paths with `http://`, `https://`, or `data:` protocol prefixes skip the filesystem check (they're loaded by the browser directly).

### D16: FrameClock Duration Source

**Decision:** Total composition duration is computed as `Math.max(...scenes.map(s => s.start_time + s.duration))` — the same formula as OBJ-016's `computeTotalDuration()`. The FrameClock is created via `FrameClock.fromDuration(manifest.composition.fps, totalDuration)`.

**Rationale:** Audio duration does NOT override scene durations in the render loop. If there's a mismatch, OBJ-016 emits an `AUDIO_DURATION_MISMATCH` warning, and OBJ-014's `durationStrategy: 'match_audio'` handles the alignment at the mux stage.

### D17: Aspect Ratio for Camera State

**Decision:** The orchestrator computes `aspectRatio = manifest.composition.width / manifest.composition.height` once and uses it for all `toCameraState()` calls (OBJ-006). This value is also passed to `PageProtocol.initialize()` as part of the `PageInitConfig`.

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
- [ ] **AC-15:** Pre-flight image check: if a manifest references a non-existent image file, `render()` throws `OrchestratorError` with code `SCENE_SETUP_FAILED` before launching the browser. The error message lists the missing file path.
- [ ] **AC-16:** During a 5-scene render, at most 2 scenes are active on the page simultaneously (verifiable by logging `protocol.getActiveSceneIds()` per frame in debug mode).

### Transitions

- [ ] **AC-17:** A 2-scene manifest with a `crossfade` transition of 1.0s between scenes renders the overlap frames as multi-pass commands. The captured frames during the transition are visually distinct from either scene alone.
- [ ] **AC-18:** A 2-scene manifest with a `cut` transition has no overlap — the scene switches at the boundary frame.
- [ ] **AC-19:** A 2-scene manifest with `dip_to_black` transitions produces frames that fade to the clear color (black) between scenes.

### Camera Paths

- [ ] **AC-20:** For a scene using the `slow_push_forward` camera preset, the captured frames show progressive forward movement (early frames show a wider view than later frames).
- [ ] **AC-21:** `camera_params.offset` shifts the camera position without affecting lookAt. A scene with `offset: [2, 0, 0]` renders with the camera shifted 2 units to the right compared to the same scene without offset.

### Error Handling and Cleanup

- [ ] **AC-22:** If FFmpeg crashes mid-encode, `render()` throws `OrchestratorError` with code `ENCODE_FAILED`. The browser is closed (no zombie Chromium process).
- [ ] **AC-23:** If a page error occurs during frame rendering, `render()` throws `OrchestratorError` with code `RENDER_FAILED`. FFmpeg is aborted. Browser is closed.
- [ ] **AC-24:** On any failure, partial output files are deleted. The `outputPath` does not contain a corrupted partial MP4.
- [ ] **AC-25:** `render()` called twice on the same instance throws `OrchestratorError` without launching any resources.

### Progress and Cancellation

- [ ] **AC-26:** `onProgress` is called once per frame. The `frame` field increments from 0 to totalFrames-1. `ratio` reaches 1.0 on the last frame.
- [ ] **AC-27:** If `onProgress` returns `false` at frame 10 of a 60-frame render, `render()` throws `OrchestratorError` with code `CANCELLED`. Fewer than 60 frames are written. All resources are cleaned up.

### Performance (C-08, TC-02)

- [ ] **AC-28:** A 60-second, 30fps, 5-plane-per-scene video at 1920x1080 renders in under 15 minutes on a 4-core VPS with 4GB+ RAM using software WebGL. (Performance test, not enforced in CI — logged as a benchmark.)

### Convenience Function

- [ ] **AC-29:** `renderFromFile()` with a valid manifest file path produces the same result as manually loading the file and creating an Orchestrator.
- [ ] **AC-30:** `renderFromFile()` with a non-existent file path throws `OrchestratorError` with code `MANIFEST_INVALID`, with `validationErrors` containing a `FILE_NOT_FOUND` error.

## Edge Cases and Error Handling

### Manifest and Validation

| Scenario | Expected Behavior |
|---|---|
| `manifest` is null/undefined/number | Full validation catches it. `OrchestratorError` code `MANIFEST_INVALID`. |
| Valid manifest but empty `cameraRegistry` | Passes manifest validation (ManifestRegistry may have camera registrations). Fails at D12 preset resolution with `CAMERA_NOT_FOUND`. |
| Manifest with 0-duration scene | Zod schema rejects (`duration` must be positive). `MANIFEST_INVALID`. |
| `skipValidation: true` with an invalid manifest | Undefined behavior (documented). May crash mid-render. |
| Manifest where scene geometries pass validation but `getGeometry()` returns undefined | `OrchestratorError` with code `GEOMETRY_NOT_FOUND`. Indicates registry inconsistency between ManifestRegistry and OBJ-005's geometry registry. |

### Image Resolution

| Scenario | Expected Behavior |
|---|---|
| Image path is absolute and exists | Used as-is. Pre-flight check passes. |
| Image path is relative, `assetsDir` not set | Resolved against `process.cwd()`. |
| Image path is relative and resolved path doesn't exist | `OrchestratorError` code `SCENE_SETUP_FAILED`, message includes resolved absolute path. |
| Multiple missing images across different scenes | All missing paths listed in the error message (not just the first). |
| Image path is `data:image/png;base64,...` | Skips filesystem check. Passed through to page. |
| Image path is `https://example.com/img.png` | Skips filesystem check. Passed through to page. Network failure would be caught by page texture loading as a degraded render (magenta fallback). |

### Scene Timing

| Scenario | Expected Behavior |
|---|---|
| Single scene, no transitions | Renders all frames with that scene. Single-pass commands. |
| Two scenes with no overlap and no gap | Scene A renders until its end, scene B starts on the next frame. Cut transition. |
| Two scenes with a gap (B.start_time > A.end_time) | Frames in the gap render nothing — the clear color (black) is captured. No scene is active. |
| Scenes not in start_time order in manifest | Sorted by start_time before rendering (OBJ-016 warned about this). |
| Scene with zero-length transition (cut with duration: 0) | Equivalent to an instant cut. Single pass, no overlap. |
| Crossfade where both scenes are the same geometry | Works correctly — two separate scene instances with potentially different images. |

### Transition Edge Cases

| Scenario | Expected Behavior |
|---|---|
| First scene has `transition_in: crossfade` | OBJ-016 validation catches this (`CROSSFADE_NO_ADJACENT`). If `skipValidation` is true, the first frame would attempt a multi-pass render with a non-existent preceding scene — caught by `SCENE_NOT_FOUND` from the page protocol. |
| Crossfade progress exactly 0.0 | Pass B opacity = 0.0. Only scene A visible. |
| Crossfade progress exactly 1.0 | Pass B opacity = 1.0. Scene B fully covers A. |
| Dip-to-black with no subsequent scene | Scene fades to black. Remaining frames (if any gap) are black. |

### Resource Failures

| Scenario | Expected Behavior |
|---|---|
| Puppeteer fails to launch (no Chromium) | `OrchestratorError` code `BROWSER_LAUNCH_FAILED`. No FFmpeg process spawned. |
| Page init fails (WebGL not available) | `OrchestratorError` code `PAGE_INIT_FAILED`. Browser is closed. |
| Texture load fails for one slot during setupScene | `protocol.setupScene()` returns `success: false`. Orchestrator throws `OrchestratorError` code `SCENE_SETUP_FAILED` listing the failed slots. Browser and FFmpeg are cleaned up. |
| FFmpeg exits mid-encode | Detected at next `writeFrame()` or `finalize()`. `OrchestratorError` code `ENCODE_FAILED` with FFmpeg stderr in `cause.ffmpegLog`. Browser closed. |
| Audio file missing or corrupt | `OrchestratorError` code `AUDIO_MUX_FAILED`. Temp video file deleted. |
| Output directory doesn't exist | FFmpeg fails to open output. `ENCODE_FAILED`. |
| `onProgress` throws | Treated as cancellation. Same cleanup as `CANCELLED`. |

### Concurrent and Lifecycle

| Scenario | Expected Behavior |
|---|---|
| `render()` called twice | Second call throws `OrchestratorError` with message "Orchestrator has already been used. Create a new instance." |
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

8. **Transition computation:** For a crossfade at progress 0.5, verify multi-pass command: A at opacity 1.0, B at opacity 0.5.

9. **Dip-to-black computation:** At progress 0.7 of a fade-out, verify single pass at opacity 0.3.

10. **Cut transition:** At the boundary frame, verify single pass with the new scene.

11. **Scene lifecycle tracking:** Simulate a 3-scene timeline with one crossfade. Verify setup/teardown calls: scene 1 setup before frame 0, scene 2 setup before the crossfade starts, scene 1 teardown after the crossfade ends.

12. **Double render:** Create orchestrator, mock render to succeed, call `render()` twice — second call throws.

13. **Progress callback values:** Verify `frame`, `totalFrames`, `ratio`, `elapsedMs`, `estimatedRemainingMs` are populated correctly.

14. **Cancellation:** Mock `onProgress` to return `false` at frame 5. Verify render throws `CANCELLED`, cleanup methods called.

### Integration Tests: `test/integration/orchestrator.test.ts`

These launch real Puppeteer + FFmpeg. Use small viewports (320x240) and short durations (0.5-1s at 10fps = 5-10 frames) for speed.

15. **Single-scene end-to-end:** Register a mock "test" geometry with one slot. Create a solid-color test image. Render a 0.5s manifest at 10fps (5 frames). Verify output MP4 exists, ffprobe reports 320x240, H.264, ~5 frames. Verify `encoderResult.frameCount === 5`.

16. **Multi-scene with cut:** Two scenes, each 0.5s. Render 10 frames total. Verify output is ~1.0s.

17. **Multi-scene with crossfade:** Two scenes with 0.2s crossfade overlap. Verify total frame count accounts for the overlap.

18. **Audio muxing:** Single scene with a short test WAV file. Verify final MP4 has both video and audio streams via ffprobe. Verify temp file is deleted.

19. **Missing image pre-flight:** Manifest references a non-existent image. Verify `SCENE_SETUP_FAILED` is thrown before any browser launch (verify by checking no Chromium process was started — or by confirming the error occurs in <100ms).

20. **Determinism (TC-06):** Render same manifest twice. Compare frame checksums of resulting MP4s. They should be identical (with `deterministic: true` on the encoder) or visually indistinguishable.

21. **Cleanup on failure:** Provide an invalid FFmpeg path. Render should fail with `ENCODE_FAILED`. Verify no browser process remains (check process list or verify bridge.isLaunched === false).

22. **Cancellation:** Render with `onProgress` returning false at frame 2. Verify partial output deleted. Verify result is `CANCELLED`.

23. **renderFromFile convenience:** Write a valid manifest JSON to a temp file. Call `renderFromFile()`. Verify success.

24. **renderFromFile with missing file:** Call with non-existent path. Verify `MANIFEST_INVALID` with `FILE_NOT_FOUND`.

### Performance Benchmark (TC-02, C-08)

25. **Benchmark:** Register the "stage" geometry (or a test geometry). Render a 60-second, 30fps, 5-slot manifest at 1920x1080 with software WebGL. Log total render time, average frame time, and capture stats. Assert render time < 15 minutes on qualifying hardware.

### Relevant Testable Claims

- **TC-02:** Tests 15, 25 measure per-frame rendering time.
- **TC-04:** Tests 15-17 verify that an orchestrator using only geometry names and slot keys (no manual coordinates) produces correct output.
- **TC-06:** Test 20 verifies deterministic output.
- **TC-07:** Tests 1-3 verify manifest validation catches errors before rendering.
- **TC-10:** Test 17 verifies crossfade transitions work.
- **TC-11:** All integration tests run with `gpu: false` (software WebGL).
- **TC-13:** Test 18 verifies audio duration drives video length (indirectly, via OBJ-014's match_audio strategy).

## Integration Points

### Depends on

| Dependency | What OBJ-035 uses |
|---|---|
| **OBJ-009** (FrameClock + PuppeteerBridge) | `FrameClock.fromDuration()` to create the clock from manifest fps and computed duration. `FrameClock.frames()` to drive the render loop. `PuppeteerBridge` constructor, `launch()`, `close()`, and `page` property. |
| **OBJ-011** (PageProtocol) | `PageProtocol` constructor, `initialize()`, `setupScene()`, `renderFrame()`, `teardownScene()`, `dispose()`, `getActiveSceneIds()`. Protocol types: `RequiredCameraState`, `SceneSetupConfig`, `SlotSetup`, `RenderFrameCommand`, `RenderPass`, `PageInitConfig`. |
| **OBJ-012** (FrameCapture) | `FrameCapture` constructor, `capture()`, `getStats()`. |
| **OBJ-013** (FFmpegEncoder) | `FFmpegEncoder` constructor, `start()`, `writeFrame()`, `finalize()`, `abort()`. `resolveFFmpegPath()`. |
| **OBJ-014** (AudioMuxer) | `muxAudio()` function (or `AudioMuxer` class) for post-encoding audio mux. `probeMedia()` for audio duration inspection. |
| **OBJ-016** (Manifest Loader) | `loadManifest()`, `loadManifestFromFile()`, `computeTotalDuration()`. |
| **OBJ-004** (Manifest Schema) | `ManifestRegistry`, `ManifestError`, `ManifestResult`, `Manifest`, `Scene`, `PlaneRef`, `Composition` types. `createRegistry()`. |
| **OBJ-005** (Geometry Types) | `getGeometry()` to resolve full `SceneGeometry` by name. `SceneGeometry`, `PlaneSlot` types. |
| **OBJ-006** (Camera Path Types) | `CameraPathRegistry`, `getCameraPath()`, `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `toCameraState()`. |
| **OBJ-007** (Interpolation/Easings) | Indirectly consumed via OBJ-006's camera presets. The orchestrator does not call easing functions directly. |

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

If `protocol.setupScene()` returns `success: false` for one slot (e.g., network timeout on an HTTP texture), should the orchestrator retry? Current decision: no — fail fast. Retries add complexity and the production path uses local file:// textures which don't fail transiently. Revisit if HTTP texture sources become common.

### OQ-B: Should the orchestrator support rendering a subset of frames?

A `frameRange?: { start: number; end: number }` config option would enable rendering specific segments for debugging or parallel rendering (OBJ-082). Currently deferred — OBJ-082 depends on OBJ-035 and may add this.

### OQ-C: Should the orchestrator validate audio file existence in pre-flight?

Currently, audio file issues surface at the muxing stage (OBJ-014). Pre-flight validation would catch missing audio files earlier. Low priority — audio is typically generated by the pipeline before the orchestrator runs.

### OQ-D: How should the orchestrator handle scenes with partial texture failures?

Current decision: treat any texture load failure (`SceneSetupResult.success === false`) as a fatal error. Alternative: render with magenta fallback meshes (which OBJ-011 creates for failed textures) and include a warning in the result. This would be useful for development but wrong for production. Could be gated behind a `tolerateTextureFailures?: boolean` config option. Deferred.

### OQ-E: Should OBJ-035 accept full GeometryRegistry or use getGeometry()?

The current design calls `getGeometry(name)` from OBJ-005's module-level registry. This introduces a coupling to OBJ-005's global registry singleton. An alternative is accepting a `GeometryRegistry` parameter (like `cameraRegistry`). The trade-off: OBJ-005 uses a register-then-lock singleton pattern, while OBJ-006 uses a passed-in record. For consistency, the orchestrator could accept both as parameters, but this means the caller must construct the geometry record. Current design: use OBJ-005's `getGeometry()` directly (it's the canonical access pattern established by OBJ-005's spec). Flag for challenger review.

---

I believe this specification is comprehensive. The key design thread is: the orchestrator owns the full lifecycle, validates before allocating resources, iterates frames deterministically, delegates rendering to the page protocol, and cleans up unconditionally. I'm particularly interested in the challenger's view on OQ-E (geometry registry access pattern) and whether the transition handling algorithm in D13 is precise enough for implementation.

Challenger, please review and let me know your assessment.

---

## Round 2 — spec_challenger

Let me verify some of the dependency interfaces referenced in this spec before providing my assessment.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/output.md",
  "offset": "0",
  "limit": "300"
}
[Tool Result]      0→# Specification: OBJ-014 — FFmpeg Audio Muxing
     1→
     2→## Summary
     3→
     4→OBJ-014 implements the audio muxing module (`src/engine/audio-muxer.ts`) — the post-encoding stage that combines OBJ-013's video-only MP4 with an audio file (WAV or MP3) to produce the final deliverable MP4 with synchronized audio. This module covers constraint C-07 (audio synchronization) at the encoding level, making the single-pass vs. two-pass decision, handling format differences between WAV and MP3 inputs, and managing duration mismatches between video and audio streams.
     5→
     6→This module is deliberately separate from OBJ-013's `FFmpegEncoder` — it operates on completed files, not on streaming frame data. It accepts file paths, not buffers.
     7→
     8→## Interface Contract
     9→
    10→```typescript
    11→// src/engine/audio-muxer.ts
    12→
    13→/**
    14→ * Strategy for handling duration mismatches between video and audio.
    15→ *
    16→ * - 'match_shortest': Out... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": "180",
  "limit": "120"
}
[Tool Result]    180→ * Supports multi-pass rendering for transitions: each pass
   181→ * renders one scene with its own camera state and opacity.
   182→ * The page composites all passes into a single frame using
   183→ * sequential rendering with autoClear=false.
   184→ *
   185→ * COMPOSITING MODEL (order-dependent over-paint):
   186→ *
   187→ * Passes are rendered sequentially. Each pass paints over whatever
   188→ * was rendered by previous passes. The visual result depends on
   189→ * both the opacity values AND the pass order.
   190→ *
   191→ * For normal (non-transition) frames:
   192→ *   passes = [{ sceneId: A, opacity: 1.0, camera: ... }]
   193→ *
   194→ * For crossfade transitions at progress p (0->1, where 0=fully A, 1=fully B):
   195→ *   passes = [
   196→ *     { sceneId: A, opacity: 1.0, camera: ... },  // outgoing scene, full opacity
   197→ *     { sceneId: B, opacity: p,   camera: ... },   // incoming scene, increasing opacity
   198→ *   ]
   199→ *   Visual result:... [truncated]
Good — OBJ-011 lines 194-198 actually show the **same** crossfade formula the spec proposes: `[A at 1.0, B at p]`. Let me also check the OBJ-011 setupScene interface and the OBJ-005 geometry access:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": "300",
  "limit": "200"
}
[Tool Result]    300→  /** Additional context (e.g., which sceneId, which slot). */
   301→  details?: Record<string, unknown>;
   302→}
   303→
   304→/**
   305→ * Error codes for page-side errors.
   306→ */
   307→export type PageErrorCode =
   308→  | 'NOT_INITIALIZED'        // init() not called
   309→  | 'ALREADY_INITIALIZED'    // init() called twice
   310→  | 'SCENE_EXISTS'           // setupScene with duplicate sceneId
   311→  | 'SCENE_NOT_FOUND'        // renderFrame/teardown with unknown sceneId
   312→  | 'TEXTURE_LOAD_FAILED'    // One or more textures failed to load
   313→  | 'WEBGL_ERROR'            // WebGL context error
   314→  | 'INVALID_COMMAND'        // Malformed command data
   315→  ;
   316→```
   317→
   318→### Node-Side Protocol Class: `src/engine/page-protocol.ts`
   319→
   320→```typescript
   321→// src/engine/page-protocol.ts
   322→
   323→import type { PuppeteerBridge } from './puppeteer-bridge.js';
   324→import type {
   325→  PageInitConfig,
   326→  Render... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": "120",
  "limit": "200"
}
[Tool Result]    120→   * Examples: 'stage', 'tunnel', 'canyon', 'flyover'
   121→   */
   122→  name: string;
   123→
   124→  /**
   125→   * The named plane slots that make up this geometry.
   126→   * Keys are slot names (lowercase, underscore-separated,
   127→   * matching /^[a-z][a-z0-9_]*$/).
   128→   * Values define the spatial placement of each slot.
   129→   *
   130→   * The manifest's planes object must use these exact keys.
   131→   * Manifest validation (OBJ-017) checks that all required slots
   132→   * have images and that no unrecognized slot keys are present.
   133→   */
   134→  slots: Record<string, PlaneSlot>;
   135→
   136→  /**
   137→   * Camera path preset names that are validated to work with this
   138→   * geometry — meaning they produce no edge reveals and create
   139→   * a visually coherent motion for this spatial arrangement.
   140→   *
   141→   * Manifest validation (OBJ-041) rejects camera paths not in this list.
   142→   * Must contain at least one en... [truncated]
Now let me check the SceneSetupConfig and SlotSetup types from OBJ-011:
[Tool: Grep]
  Input: {
  "pattern": "SceneSetupConfig|SlotSetup|RequiredCameraState|PageInitConfig",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "context"
}
[Tool Error] <tool_use_error>InputValidationError: [
  {
    "code": "invalid_value",
    "values": [
      "content",
      "files_with_matches",
      "count"
    ],
    "path": [
      "output_mode"
    ],
    "message": "Invalid option: expected one of \"content\"|\"files_with_matches\"|\"count\""
  }
]

This tool's schema was not sent to the API — it was not in the discovered-tool set derived from message history. Without the schema in your prompt, typed parameters (arrays, numbers, booleans) get emitte

[Tool: ToolSearch]
  Input: {
  "query": "select:Grep",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Grep'}]

[Tool: Grep]
  Input: {
  "pattern": "SceneSetupConfig|SlotSetup|RequiredCameraState|PageInitConfig",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "-C": 3,
  "head_limit": 80
}
[Tool Result] 13-```typescript
14-// src/engine/protocol-types.ts
15-
16:import type { PageInitConfig, RendererInfo } from './page-types.js';
17-import type { FogConfig } from '../scenes/geometries/types.js';
18-
19-// Re-export for protocol consumers
20:export type { PageInitConfig, RendererInfo, FogConfig };
21-
22-// ────────────────────────────────────────────
23-// Camera State
--
33- * which is used by OBJ-010's lower-level renderFrame() method.
34- * This type is used exclusively in the OBJ-011 render protocol.
35- */
36:export interface RequiredCameraState {
37-  /** Camera position in world units [x, y, z]. */
38-  position: [number, number, number];
39-  /** Camera lookAt target in world units [x, y, z]. */
--
54- * by sceneId. Multiple scenes can coexist on the page simultaneously
55- * (required for transition overlap rendering).
56- */
57:export interface SceneSetupConfig {
58-  /**
59-   * Unique identifier for this scene instance.
60-   * Must match the manifest's scene.id.
--
71-   *... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "export interface SlotSetup",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "-A": 30
}
[Tool Result] 90:export interface SlotSetup {
91-  /** Position in world units [x, y, z]. */
92-  position: [number, number, number];
93-  /** Euler rotation in radians [rx, ry, rz]. */
94-  rotation: [number, number, number];
95-  /** Plane geometry dimensions in world units [width, height]. */
96-  size: [number, number];
97-  /**
98-   * Texture source. One of:
99-   * - Absolute POSIX file path (starting with '/', converted to
100-   *   'file://' + path by the page handler)
101-   * - file:// URL
102-   * - data: URI (base64-encoded image)
103-   * - http:// or https:// URL (development/testing only)
104-   *
105-   * The page handler detects the format and handles accordingly.
106-   * Absolute POSIX file paths are the primary production path
107-   * per OBJ-009 D10.
108-   *
109-   * Production use should prefer absolute file paths or data URIs
110-   * for deterministic rendering (C-05). HTTP/HTTPS URLs are
111-   * supported for development/testing but introduce network
112-   * dependency... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "export interface SlotSetup",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "-A": 50
}
[Tool Result] 90:export interface SlotSetup {
91-  /** Position in world units [x, y, z]. */
92-  position: [number, number, number];
93-  /** Euler rotation in radians [rx, ry, rz]. */
94-  rotation: [number, number, number];
95-  /** Plane geometry dimensions in world units [width, height]. */
96-  size: [number, number];
97-  /**
98-   * Texture source. One of:
99-   * - Absolute POSIX file path (starting with '/', converted to
100-   *   'file://' + path by the page handler)
101-   * - file:// URL
102-   * - data: URI (base64-encoded image)
103-   * - http:// or https:// URL (development/testing only)
104-   *
105-   * The page handler detects the format and handles accordingly.
106-   * Absolute POSIX file paths are the primary production path
107-   * per OBJ-009 D10.
108-   *
109-   * Production use should prefer absolute file paths or data URIs
110-   * for deterministic rendering (C-05). HTTP/HTTPS URLs are
111-   * supported for development/testing but introduce network
112-   * dependency... [truncated]
Now let me check `SceneSetupResult` and `PageInitConfig`:
[Tool: Grep]
  Input: {
  "pattern": "export interface SceneSetupResult|export interface PageInitConfig",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "-A": 20
}
[Tool Result] 150:export interface SceneSetupResult {
151-  /** The scene ID that was set up. */
152-  sceneId: string;
153-  /** Per-slot loading results. Keys match the input slots. */
154-  slots: Record<string, SlotLoadResult>;
155-  /** True if ALL slots loaded successfully. */
156-  success: boolean;
157-}
158-
159-/**
160- * Result of loading a single slot's texture.
161- */
162-export interface SlotLoadResult {
163-  /** Whether the texture loaded successfully. */
164-  status: 'loaded' | 'error';
165-  /** Natural width of the loaded texture in pixels. Present when status='loaded'. */
166-  naturalWidth?: number;
167-  /** Natural height of the loaded texture in pixels. Present when status='loaded'. */
168-  naturalHeight?: number;
169-  /** Error message if status='error'. */
170-  error?: string;

[Tool: Grep]
  Input: {
  "pattern": "export interface PageInitConfig",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "output_mode": "content",
  "-A": 30
}
[Tool Result] 255:export interface PageInitConfig {
256-  width: number;
257-  height: number;
258-  clearColor?: string;
259-  clearAlpha?: number;
260-  fov?: number;
261-  near?: number;
262-  far?: number;
263-  cameraPosition?: Vec3;
264-  cameraLookAt?: Vec3;
265-  antialias?: boolean;
266-  preserveDrawingBuffer?: boolean;
267-}
268-
269-/**
270- * Diagnostic info returned by the page's getRendererInfo() function.
271- */
272-export interface RendererInfo {
273-  initialized: boolean;
274-  canvasSize: [number, number];
275-  webglVersion: string;
276-  vendor: string;
277-  gpuRenderer: string;
278-  maxTextureSize: number;
279-  antialias: boolean;
280-}
281-
282-/**
283- * Partial camera state for the page's renderFrame() function.
284- * Sent per-frame by the orchestrator (via OBJ-011 message protocol).
285- */
Now let me check how OBJ-006 exposes `evaluate()` and `CameraFrameState`:
[Tool: Grep]
  Input: {
  "pattern": "evaluate|CameraFrameState",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "output_mode": "content",
  "-C": 3,
  "head_limit": 60
}
[Tool Result] 16-
17-/**
18- * The path-controlled subset of camera state at a single moment in time.
19: * Returned by a camera path's evaluate() function.
20- *
21: * Relationship to CameraState (OBJ-003): CameraFrameState contains only
22- * the properties that a camera PATH controls — position, lookAt, fov.
23- * The complete CameraState also includes aspectRatio, near, and far,
24- * which are composition-level constants (set from the manifest's
25- * composition.width/height and the geometry's near/far recommendations).
26- * The scene renderer constructs a full CameraState by combining
27: * CameraFrameState from the path with composition-level values.
28- * Use toCameraState() to perform this merge.
29- */
30:export interface CameraFrameState {
31-  /** Camera position in world space [x, y, z] */
32-  position: Vec3;
33-  /** Camera lookAt target in world space [x, y, z] */
--
40- * Combines path-controlled camera state with composition-level constants
41- * to produce a complete CameraState... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "CameraPathEvaluator|interface CameraPathPreset",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "output_mode": "content",
  "-A": 25
}
[Tool Result] 210:export type CameraPathEvaluator = (
211-  t: number,
212-  params?: CameraParams
213-) => CameraFrameState;
214-
215-/**
216- * The complete definition of a camera path preset.
217- * This is the type that all OBJ-026 through OBJ-034 implementations export.
218- */
219:export interface CameraPathPreset {
220-  /** Unique preset name. Must match the key in the registry. Lowercase snake_case. */
221-  name: string;
222-
223-  /**
224-   * Human-readable description for SKILL.md and error messages.
225-   * Should describe the visual effect in 1-2 sentences.
226-   */
227-  description: string;
228-
229-  /**
230-   * The evaluation function. Given t in [0, 1] and optional params,
231-   * returns the path-controlled camera state.
232-   */
233:  evaluate: CameraPathEvaluator;
234-
235-  /**
236-   * The camera state at t=0 with default params (speed=1, default easing, no offset).
237-   * Redundant with evaluate(0), but provided as static data for
238-   * fast access during validati... [truncated]
Now I have a thorough understanding of all the dependency interfaces. Let me also check one more thing - how OBJ-004's manifest schema handles `PlaneRef`:
[Tool: Grep]
  Input: {
  "pattern": "PlaneRef|position_override|rotation_override|opacity",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "output_mode": "content",
  "-C": 2,
  "head_limit": 40
}
[Tool Result] 103-
104-/** Plane reference (image source + optional overrides) */
105:export const PlaneRefSchema: z.ZodType;
106:export type PlaneRef = z.infer<typeof PlaneRefSchema>;
107-
108-/** A single scene */
--
171-```
172-
173:**PlaneRefSchema** (`.strict()`):
174-```typescript
175-{
176-  src: z.string().min(1),                           // Path/URL to image file
177:  opacity: z.number().min(0).max(1).default(1.0),   // Static initial opacity
178:  position_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [x, y, z] — AP-08 escape hatch
179:  rotation_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [rx, ry, rz] — AP-08 escape hatch
180-  scale: z.number().positive().default(1.0),         // Uniform scale multiplier
181-}
182-```
183:The `position_override` and `rotation_override` fields exist per AP-08 (do not hard-code the depth model). They are optional escape hatches — never the primary authoring method (AP-03).
184-
185-**SceneSchema** (`.... [truncated]
Good. Now I have a complete picture. Let me deliver my review.

---

## Challenger Review — Round 2

I've done a thorough cross-reference against all dependency specs (OBJ-009, OBJ-011, OBJ-012, OBJ-013, OBJ-014, OBJ-016, OBJ-004, OBJ-005, OBJ-006). The spec is substantial and mostly well-structured. Here are my findings:

---

### Points of Agreement (Sound)

1. **Overall architecture** — the phased pipeline (validate → launch → render loop → finalize → mux) is correct and aligns with seed Section 4.4.
2. **Single `render()` method with owned lifecycle** (D1, D2) — clean, correct, prevents resource leaks.
3. **Pre-flight image check** (D15) — excellent extension of C-10's fail-fast principle.
4. **Lazy setup / eager teardown** (D14) — correctly limits GPU memory to 2 scenes max.
5. **Crossfade formula** — `[A at 1.0, B at p]` matches OBJ-011 lines 194-198 exactly. My initial concern was wrong — OBJ-011 was updated to use this model. ✓
6. **Dip-to-black handling** matches OBJ-011 lines 204-207. ✓
7. **Audio muxing as post-step** (D6) aligns with OBJ-014's `muxAudio()` function. ✓
8. **Camera state computation** (D4) correctly uses `CameraPathPreset.evaluate(t, params)` and applies offset externally per OBJ-006's contract. ✓

---

### Issue 1 — CRITICAL: Geometry registry access is unresolved

The config has `cameraRegistry: CameraPathRegistry` as an explicit parameter, but geometry access is left to OQ-E with "Flag for challenger review." This means the implementer must guess.

**The problem:** OBJ-005 uses a **global singleton** with register-then-lock semantics (`getGeometry(name)`). OBJ-006 uses a **passed-in record** (`CameraPathRegistry`). The spec uses both patterns simultaneously — `cameraRegistry` is a parameter, but geometry is accessed via OBJ-005's singleton. This asymmetry is confusing and creates a hidden coupling.

Worse, `renderFromFile()` doesn't include geometry access at all — if geometries come from the singleton, the convenience function works; if from a parameter, it's missing from the signature.

**Proposed fix:** Resolve OQ-E with a definitive decision. I recommend: **accept a `GeometryRegistry` parameter** (matching the camera pattern) for consistency and testability. The caller constructs it from `getGeometryRegistry()`. This makes the dependency explicit and allows tests to inject mock registries.

```typescript
export interface OrchestratorConfig {
  // ...existing...
  
  /**
   * The geometry registry containing full SceneGeometry definitions.
   * Used to resolve slot positions, rotations, and sizes for scene setup.
   * Obtain via getGeometryRegistry() from OBJ-005.
   */
  geometryRegistry: GeometryRegistry;
}
```

And update `renderFromFile()` to accept it:
```typescript
export async function renderFromFile(
  manifestPath: string,
  registry: ManifestRegistry,
  geometryRegistry: GeometryRegistry,
  cameraRegistry: CameraPathRegistry,
  options: Omit<OrchestratorConfig, 'manifest' | 'registry' | 'geometryRegistry' | 'cameraRegistry'>,
): Promise<OrchestratorResult>;
```

Remove OQ-E entirely — it's now a design decision, not an open question.

---

### Issue 2 — MAJOR: Manifest type discrimination is fragile

The spec says the orchestrator distinguishes pre-validated `Manifest` from raw `unknown` by "checking for a `version` property with value '3.0'." This is unreliable — `{ version: "3.0" }` would pass the check but crash during rendering.

**Proposed fix:** Always run full validation (Phase 1 + Phase 2) via `loadManifest()` regardless of input type. The cost is negligible (synchronous Zod parse). This eliminates the need for type discrimination entirely. The `manifest` field becomes simply `unknown`:

```typescript
/**
 * The manifest to render. Raw JSON value — always validated via
 * loadManifest() before rendering. Pre-parsed Manifest objects
 * are re-validated (Zod parse is cheap).
 * To skip validation for testing, use skipValidation: true.
 */
manifest: unknown;
```

If someone really wants to skip Phase 1 re-validation, `skipValidation: true` is the explicit opt-out.

---

### Issue 3 — MAJOR: `activeSceneId` in RenderProgress is undefined for gap frames and transition frames

During a **gap** between scenes (no scene active), what is `activeSceneId`? During a **crossfade** (two scenes active), which scene is reported?

**Proposed fix:** Change to:
```typescript
export interface RenderProgress {
  // ...existing...
  
  /**
   * Scene ID(s) being rendered for this frame.
   * - Single scene: ['scene_001']
   * - Crossfade transition: ['scene_001', 'scene_002'] (outgoing first)
   * - Gap (no active scene): [] — empty array
   */
  activeSceneIds: string[];
}
```

Update AC-26 to verify the array semantics.

---

### Issue 4 — MAJOR: Gap frame rendering algorithm is unspecified

D3's algorithm says "Find the primary active scene" but doesn't define what happens when **no scene** contains the current timestamp (a gap between scenes). The edge case table says "the clear color (black) is captured" but the algorithm doesn't describe how.

**Proposed fix:** Add explicit handling in D3's algorithm:
> If no scene's time range contains the timestamp:
> - Render an empty frame (no passes). The orchestrator sends a `RenderFrameCommand` with `passes: []`... 
> 
> Wait — OBJ-011 rejects empty passes (`INVALID_COMMAND` if passes is empty). 

So the orchestrator needs a different approach for gap frames. Options:
1. Skip the render step and capture the clear color directly (just call `captureFrame()` without `renderFrame()`).
2. Render a single pass with an invisible scene.

**Recommended fix:** For gap frames, the orchestrator skips `protocol.renderFrame()` and calls `capture.capture()` directly — the page shows whatever was last rendered (which, after the previous frame's render with proper scene group visibility management, should be just the clear color). Actually, OBJ-011's multi-pass compositing path starts with `renderer.clear()`, so the last frame's content persists on the canvas.

Better approach: The orchestrator calls `bridge.evaluate(() => { window.depthkit.renderer.clear(); })` to explicitly clear the canvas to the clear color, then captures. Document this explicitly in the spec.

Or simplest: **acknowledge that gaps are a degenerate case and require the orchestrator to explicitly clear the canvas before capture.** Add a private method `clearFrame()` that uses `bridge.evaluate()` to call `renderer.clear()`, and invoke it for gap frames.

---

### Issue 5 — MAJOR: `PlaneRef.opacity` is not carried through to SlotSetup

OBJ-004's `PlaneRef` has a static `opacity` field (default 1.0). OBJ-011's `SlotSetup` does NOT have an opacity field — opacity is only set per-frame via `RenderPass.opacity`. The spec's D5 (geometry-to-SlotSetup mapping) doesn't mention how `PlaneRef.opacity` is handled.

If a manifest author sets `opacity: 0.5` on a plane, what happens? The current spec silently ignores it.

**Proposed fix:** Document the handling explicitly. Options:
1. `PlaneRef.opacity` is stored by the orchestrator and multiplied into `RenderPass.opacity` during frame rendering. The spec should state this in D4 or a new D18.
2. `PlaneRef.opacity` is applied during scene setup by setting initial material opacity. But OBJ-011's `SlotSetup` has no opacity field, so this requires an OBJ-011 change (out of scope).

Recommend option 1: The orchestrator stores per-slot opacity from the manifest and factors it into the pass opacity. Document this:

> **D18: Per-Plane Static Opacity**
> `PlaneRef.opacity` (from OBJ-004) is a per-plane static opacity value. OBJ-011's `SlotSetup` has no opacity field — opacity is applied at render time via `RenderPass.opacity`. The orchestrator stores each plane's static opacity per scene and, when constructing `RenderPass`, sets:
> ```
> pass.opacity = transitionOpacity * min(scene_plane_opacities)
> ```
> Wait — `RenderPass.opacity` applies to ALL meshes in the scene group equally (OBJ-011 line 437: `material.opacity = originalOpacity * pass.opacity`). Per-plane opacity cannot be achieved through `RenderPass.opacity` alone.

Actually, looking at OBJ-011 line 437 more carefully: `material.opacity = originalOpacity * pass.opacity`. The `originalOpacity` is the material's initial opacity. If `PlaneRef.opacity` was set as the material's initial opacity during `setupScene()`, then `RenderPass.opacity` would correctly scale it.

But `SlotSetup` doesn't have an opacity field. This is a gap between OBJ-004 and OBJ-011.

**Revised fix:** Document this as a known limitation. `PlaneRef.opacity` in the manifest is not supported in V1 because `SlotSetup` does not carry per-slot opacity. Add an open question noting this gap. The field exists in the schema (OBJ-004) but has no rendering effect until OBJ-011's `SlotSetup` is extended with an `opacity` field. The orchestrator should log a warning if any `PlaneRef.opacity !== 1.0` is encountered.

---

### Issue 6 — MAJOR: Pre-flight check collects all missing files, but AC-15 says singular

D15 says: "listing all missing files." AC-15 says: "The error message lists the missing file path" (singular). These contradict.

**Proposed fix:** AC-15 should read:
> Pre-flight image check: if a manifest references non-existent image files, `render()` throws `OrchestratorError` with code `SCENE_SETUP_FAILED` before launching the browser. The error message lists **all** missing file paths.

---

### Issue 7 — MINOR: `RenderProgress.ratio` documentation inconsistency

The interface says `(frame + 1) / totalFrames` in the comment but the docstring earlier says "Progress as a ratio [0, 1]. frame / totalFrames." These are different formulas (the +1 version reaches 1.0 after the last frame; the other reaches `(N-1)/N`).

**Proposed fix:** Settle on `(frame + 1) / totalFrames`. Update the field comment to remove the `frame / totalFrames` text. The +1 version is correct — after rendering the last frame (frame = totalFrames-1), ratio should be 1.0.

---

### Issue 8 — MINOR: No acceptance criterion for `rendererInfo` population

`OrchestratorResult.rendererInfo` is declared but no AC tests that it's populated correctly.

**Proposed fix:** Add:
> **AC-31:** `OrchestratorResult.rendererInfo.initialized === true` and `rendererInfo.webglVersion` is a non-empty string.

---

### Issue 9 — MINOR: `onProgress` exception handling

D9 says "if onProgress returns false, abort." Edge case table says "onProgress throws → treated as cancellation." But the `onProgress` callback signature returns `boolean | void`. What if it throws? The edge case table handles this, but D9 doesn't mention it, and there's no AC for it.

**Proposed fix:** Add to D9: "If `onProgress` throws, the error is caught and treated as a cancellation request." Add an AC:
> **AC-32:** If `onProgress` throws an error, `render()` throws `OrchestratorError` with code `CANCELLED`. All resources are cleaned up.

---

### Issue 10 — MINOR: `SceneSetupResult.success === false` handling isn't fully specified

D5 calls `protocol.setupScene()` which returns `SceneSetupResult` with a `success` boolean. The spec says in the edge case table "Orchestrator throws `OrchestratorError` code `SCENE_SETUP_FAILED` listing the failed slots." But D5 doesn't mention checking `success` at all — it just constructs the config and calls `setupScene()`.

**Proposed fix:** Add to D5 after step 4:
> 5. Check `result.success`. If `false`, throw `OrchestratorError` with code `SCENE_SETUP_FAILED`, listing each slot with `status: 'error'` and its error message.

---

### Summary

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| 1 | Critical | Geometry registry access unresolved (OQ-E) | Needs fix |
| 2 | Major | Manifest type discrimination fragile | Needs fix |
| 3 | Major | `activeSceneId` undefined for gaps/transitions | Needs fix |
| 4 | Major | Gap frame rendering algorithm unspecified | Needs fix |
| 5 | Major | `PlaneRef.opacity` not carried through | Needs documentation |
| 6 | Major | AC-15 singular vs. D15 plural mismatch | Needs fix |
| 7 | Minor | `ratio` formula inconsistency | Needs fix |
| 8 | Minor | No AC for `rendererInfo` | Needs fix |
| 9 | Minor | `onProgress` throw behavior undocumented | Needs fix |
| 10 | Minor | `setupScene` success check missing from D5 | Needs fix |

Please address all critical and major issues. For minors, I'll accept reasonable fixes or explicit deferral to open questions.

---

## Round 3 — spec_author

All 10 issues are valid. I'll address every one. Here's the revised specification:

---

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
2. Resolves `CameraParams` from the manifest scene's `camera_params` (with defaults applied by Zod: `speed: 1.0`, `easing: 'ease_in_out'`).
3. Calls `cameraPreset.evaluate(t, resolvedParams)` to get `CameraFrameState`.
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

**Crossfade** (scene A `transition_out: crossfade` → scene B `transition_in: crossfade`):
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

**Implementation note:** The `window.depthkit.renderer` reference is available because OBJ-010's page shell exposes it on the `window.depthkit` namespace. The `clear()` method clears the canvas to the configured clear color (default: black, `#000000`).

### D17: FrameClock Duration Source

**Decision:** Total composition duration is computed as `Math.max(...scenes.map(s => s.start_time + s.duration))` — the same formula as OBJ-016's `computeTotalDuration()`. The FrameClock is created via `FrameClock.fromDuration(manifest.composition.fps, totalDuration)`.

**Rationale:** Audio duration does NOT override scene durations in the render loop. If there's a mismatch, OBJ-016 emits an `AUDIO_DURATION_MISMATCH` warning, and OBJ-014's duration strategy handles the alignment at the mux stage.

### D18: Per-Plane Static Opacity — V1 Limitation

**Decision:** OBJ-004's `PlaneRef.opacity` field (default 1.0) is **not supported in V1**. OBJ-011's `SlotSetup` does not carry a per-slot opacity field — opacity is applied only at the scene level via `RenderPass.opacity`, which affects all meshes in a scene group uniformly.

If any `PlaneRef` in the manifest has `opacity !== 1.0`, the orchestrator logs a warning to the console (when `debug: true`) and includes a `ManifestError` with severity `"warning"` and a descriptive message in `OrchestratorResult.warnings`. The opacity value is silently ignored — all planes render at full opacity within their scene.

**Rationale:** Supporting per-plane opacity requires extending OBJ-011's `SlotSetup` interface, which is outside OBJ-035's scope. The manifest schema (OBJ-004) defines the field for forward compatibility, but the rendering pipeline does not yet consume it. This is documented as an open question for future work.

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
| **OBJ-006** (Camera Path Types) | `CameraPathRegistry`, `getCameraPath()`, `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `ResolvedCameraParams`, `resolveCameraParams()`. |

### Consumed by

| Downstream | How it uses OBJ-035 |
|---|---|
| **OBJ-036** (Scene Sequencer) | Depends on OBJ-035. May refactor the orchestrator's internal scene iteration into a dedicated `SceneSequencer` class. OBJ-035's public API does not change. |
| **OBJ-046** (CLI render command) | Calls `renderFromFile()` or creates `Orchestrator` directly. Formats `OrchestratorResult` for terminal output. |
| **OBJ-048** (CLI error formatting) | Consumes `OrchestratorError.validationErrors` for human-readable error display. |
| **OBJ-058** (Test harness for tuning) | Creates `Orchestrator` programmatically to render test clips for Director Agent review. |
| **OBJ-073** (Docker integration) | Runs the orchestrator in a container environment with software WebGL. |
| **OBJ-074** (Performance benchmarking) | Benchmarks `Orchestrator.render()` for TC-02 compliance. |
| **OBJ-077** (End-to-end integration) | Full pipeline integration test: manifest → orchestrator → MP4. |
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

---

Challenger, I believe this revision addresses all 10 issues you raised:

1. **Geometry registry** — Resolved. Added `geometryRegistry: GeometryRegistry` as an explicit config parameter. Updated `renderFromFile()` signature. Removed from open questions, added as D12's lookup source.
2. **Manifest type discrimination** — Resolved. `manifest` is now `unknown`, always validated via `loadManifest()`. No type discrimination logic.
3. **activeSceneId → activeSceneIds** — Resolved. Changed to `activeSceneIds: string[]` with documentation for normal/transition/gap cases.
4. **Gap frame rendering** — Resolved. Added D16 with explicit canvas clear via `bridge.evaluate()`. Added AC-20 and test 11/25.
5. **PlaneRef.opacity** — Resolved. Added D18 documenting the V1 limitation. Added AC-34 for the warning behavior. Moved to OQ-E for future work.
6. **AC-15 singular/plural** — Resolved. AC-15 now says "all missing file paths."
7. **ratio formula** — Resolved. Settled on `(frame + 1) / totalFrames` consistently.
8. **rendererInfo AC** — Resolved. Added AC-33.
9. **onProgress throw** — Resolved. Added to D9 documentation and AC-29.
10. **setupScene success check** — Resolved. Added step 5 to D5.

Please verify and approve if satisfied.

---

## Round 4 — spec_challenger

Let me verify a few things in the revised spec before making my determination.
[Tool: Grep]
  Input: {
  "pattern": "window\\.depthkit\\.renderer|renderer.*clear|clear.*renderer",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "output_mode": "content",
  "-C": "3"
}
[Tool Result] 24-   * - Creates a WebGLRenderer bound to the #depthkit-canvas element.
25-   * - Calls renderer.setSize(width, height) to set canvas intrinsic dimensions.
26-   * - Calls renderer.setPixelRatio(1) to prevent HiDPI scaling.
27:   * - Calls renderer.setClearColor(clearColor, clearAlpha) for the background.
28-   *   scene.background is NOT set — the clear color serves as the background.
29-   * - Creates a PerspectiveCamera with the specified (or default) parameters.
30-   * - Creates an empty Scene.
--
529-
530-### OQ-B: Should the page support `renderer.autoClear` toggling?
531-
532:Transition rendering (OBJ-008) may need multi-pass rendering to the same canvas (render outgoing scene, then incoming scene without clearing). This requires `renderer.autoClear = false` for the second pass. OBJ-010 leaves `autoClear` at its Three.js default (`true`). Downstream objectives can toggle it via `window.depthkit.renderer.autoClear = false` from `page.evaluate()`. **No action needed in OBJ-010**... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "window\\.depthkit",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "output_mode": "content",
  "-C": "5",
  "head_limit": "60"
}
[Tool Result] 6-
7-## Interface Contract
8-
9-### Module: `src/page/scene-renderer.js`
10-
11:This is the esbuild entry point (per OBJ-001). It initializes Three.js, exposes a global `window.depthkit` namespace, and imports the other page modules. After OBJ-010, this file contains the renderer skeleton — downstream objectives populate scene management and message handling.
12-
13-```typescript
14:// Conceptual contract for window.depthkit (exposed as globals on the page).
15-// These are NOT TypeScript files — they are plain JS running in Chromium.
16-// Types here document the contract; implementation is JS.
17-
18-interface DepthkitPage {
19-  /**
--
205-//
206-/ OBJ-011 defines every message type crossing the Node.js/browser boundary:
207-// frame step commands, scene setup/teardown, texture loading signals, etc.
208-//
209-// Messages arrive via page.evaluate() calls from the Node.js orchestrator.
210:// The handler calls into window.depthkit methods (init, renderFrame, dispose).
211-//
212-/ TO... [truncated]
Good — OBJ-010 AC-02 confirms `window.depthkit` exposes `renderer` as a property. D16's `window.depthkit.renderer.clear()` approach is valid.

## Verification of Round 2 Fixes

| # | Issue | Fixed? | Verification |
|---|-------|--------|-------------|
| 1 | Geometry registry unresolved | ✅ | `geometryRegistry: GeometryRegistry` in config. `renderFromFile()` includes it. D12 uses `config.geometryRegistry[scene.geometry]`. |
| 2 | Manifest type discrimination fragile | ✅ | `manifest: unknown`. D7: "always validated via `loadManifest()`". No type discrimination. |
| 3 | `activeSceneId` undefined for gaps/transitions | ✅ | `activeSceneIds: string[]` with documented semantics for normal/transition/gap. |
| 4 | Gap frame rendering unspecified | ✅ | D16 added. `bridge.evaluate(() => { window.depthkit.renderer.clear(); })`. AC-20. Verified `renderer` is exposed per OBJ-010 AC-02. |
| 5 | `PlaneRef.opacity` not carried through | ✅ | D18 documents V1 limitation. AC-34 for warning. OQ-E for future. |
| 6 | AC-15 singular vs plural | ✅ | AC-15: "all missing file paths." |
| 7 | `ratio` formula inconsistency | ✅ | `(frame + 1) / totalFrames` consistently. |
| 8 | No AC for `rendererInfo` | ✅ | AC-33 added. |
| 9 | `onProgress` throw undocumented | ✅ | D9 documents. AC-29 tests. |
| 10 | `setupScene` success check missing | ✅ | D5 step 5 added. |

## New Issues Check

**One minor inconsistency found:** The integration points table lists `resolveCameraParams()` and `ResolvedCameraParams` from OBJ-006, but D4 passes raw `CameraParams` directly to `cameraPreset.evaluate(t, resolvedParams)` — and OBJ-006's `CameraPathEvaluator` takes `CameraParams` (raw), not `ResolvedCameraParams`. The preset resolves internally. The integration table over-specifies. This is cosmetic — an implementer reading D4 would get it right.

**Disposition:** Include as a minor note in the final spec by removing `ResolvedCameraParams` and `resolveCameraParams()` from the OBJ-006 integration row.

Everything else is sound. The spec is comprehensive, implementable, and correctly integrates with all dependencies.

CONCLUSION:

The specification for OBJ-035 — Orchestrator: Main Render Loop is agreed. It defines the top-level integration class that composes FrameClock, PuppeteerBridge (OBJ-009), PageProtocol (OBJ-011), FrameCapture (OBJ-012), FFmpegEncoder (OBJ-013), AudioMuxer (OBJ-014), and the manifest loader (OBJ-016) into a deterministic frame-by-frame render pipeline. Key design decisions include: single `render()` method with full lifecycle ownership (D1, D2), always-validate manifest via `loadManifest()` (D7), explicit geometry and camera registry parameters (D12), inline transition handling with multi-pass compositing (D13), lazy scene setup / eager teardown (D14), pre-flight image existence checks (D15), explicit canvas clear for gap frames (D16), and documented V1 limitation for per-plane opacity (D18). 34 acceptance criteria cover validation, pipeline integration, deterministic timing, audio mux, transitions, gap frames, error handling, progress/cancellation, and performance.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the final specification to disk, with the minor OBJ-006 integration table fix applied.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md",
  "content": "# Specification: OBJ-035 \u2014 Orchestrator: Main Render Loop\n\n## Summary\n\nOBJ-035 delivers the `Orchestrator` class (`src/engine/orchestrator.ts`) \u2014 the top-level integration point that coordinates the entire depthkit rendering pipeline from manifest to MP4. It composes FrameClock and PuppeteerBridge (OBJ-009), FrameCapture (OBJ-012), FFmpegEncoder (OBJ-013), AudioMuxer (OBJ-014), PageProtocol (OBJ-011), and the manifest loader (OBJ-016) into a deterministic frame-by-frame render loop implementing seed Section 4.4 steps 1\u20135. It enforces C-02 (Puppeteer + Three.js + FFmpeg pipeline), C-03 (deterministic virtualized timing), C-05 (deterministic output), and C-10 (manifest validation before rendering). This is the single entry point for both the CLI (OBJ-046) and the programmatic library API.\n\n## Interface Contract\n\n### Module: `src/engine/orchestrator.ts`\n\n```typescript\nimport type { Manifest, ManifestRegistry, ManifestError } from '../manifest/schema.js';\nimport type { FFmpegEncoderResult } from './ffmpeg-encoder.js';\nimport type { AudioMuxerResult } from './audio-muxer.js';\nimport type { CaptureStats, CaptureStrategy } from './frame-capture.js';\nimport type { RendererInfo } from './protocol-types.js';\nimport type { H264Preset } from './ffmpeg-encoder.js';\nimport type { GeometryRegistry } from '../scenes/geometries/types.js';\nimport type { CameraPathRegistry } from '../camera/types.js';\n\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n// Configuration\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md
Now update the meta.json:
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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/meta.json",
  "content": "{\n  \"id\": \"OBJ-035\",\n  \"description\": \"Orchestrator -- the main render loop coordinating Puppeteer, FFmpeg, and the virtualized clock per Section 4.4 steps 1-5. Spawns Puppeteer and FFmpeg child process, iterates through frames, sends frame commands to the page, waits for render completion, captures pixels, pipes to FFmpeg, closes stdin when done. Implements C-02 (Puppeteer+Three.js+FFmpeg pipeline) and C-03 (deterministic virtualized timing) at the integration level.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:15:00Z\",\n  \"depends_on\": [\"OBJ-009\", \"OBJ-012\", \"OBJ-013\", \"OBJ-016\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 3 engine integration. The central coordination point -- most Tier 4+ objectives depend on this. Spec completed via 4-round deliberation. Key decisions: single render() method with full lifecycle ownership, always-validate manifest, explicit geometry/camera registry parameters, inline transition handling (crossfade/dip_to_black/cut), lazy setup/eager teardown (max 2 scenes active), pre-flight image existence check, explicit canvas clear for gap frames, V1 limitation on per-plane opacity (PlaneRef.opacity ignored with warning).\",\n  \"review_status\": \"approved\",\n  \"spec_version\": \"1.0\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/meta.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-035/output.md nodes/OBJ-035/meta.json && git commit -m \"OBJ-035: Orchestrator spec - main render loop coordinating Puppeteer, FFmpeg, virtualized clock\n\nSpec completed via 4-round deliberation between spec_author and spec_challenger.\n\nKey design decisions:\n- Single render() method with full lifecycle ownership (D1, D2)\n- Always-validate manifest via loadManifest() - no fragile type discrimination (D7)\n- Explicit geometryRegistry and cameraRegistry parameters (D12)\n- Inline transition handling: crossfade, dip_to_black, cut (D13)\n- Lazy scene setup / eager teardown, max 2 scenes active (D14)\n- Pre-flight image existence check across all scenes (D15)\n- Explicit canvas clear for gap frames via window.depthkit.renderer (D16)\n- Per-plane opacity (PlaneRef.opacity) documented as V1 limitation (D18)\n\n34 acceptance criteria covering validation, pipeline integration,\ndeterministic timing, audio mux, transitions, gap frames, error\nhandling, progress/cancellation, and performance.\n\nDepends on: OBJ-009, OBJ-011, OBJ-012, OBJ-013, OBJ-014, OBJ-016\nConsumed by: OBJ-036, OBJ-046, OBJ-048, OBJ-058, OBJ-073, OBJ-074, OBJ-077, OBJ-082, OBJ-083\""
}
[Tool Result] [master f831439] OBJ-035: Orchestrator spec - main render loop coordinating Puppeteer, FFmpeg, virtualized clock
 2 files changed, 872 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-035/output.md
The specification for OBJ-035 has been written to disk and committed. 

**Summary of what was agreed:**

The Orchestrator is the top-level integration class with a single `render()` method that owns the complete pipeline lifecycle. It composes all lower-level modules (FrameClock, PuppeteerBridge, PageProtocol, FrameCapture, FFmpegEncoder, AudioMuxer) and the manifest loader into a deterministic frame-by-frame render loop. Key design choices resolved through deliberation:

1. **Manifest always re-validated** (no fragile type discrimination)
2. **Explicit geometry + camera registry parameters** (testable, no global singleton coupling)
3. **`activeSceneIds: string[]`** (handles normal, transition, and gap frames cleanly)
4. **Gap frames explicitly clear the canvas** via `window.depthkit.renderer.clear()` (verified against OBJ-010's exposed API)
5. **Per-plane opacity documented as V1 limitation** (cross-objective change needed for OBJ-011's SlotSetup)
6. **Pre-flight image checks collect all missing files** before any resource allocation
7. **onProgress callback exceptions treated as cancellation** with original error as cause
