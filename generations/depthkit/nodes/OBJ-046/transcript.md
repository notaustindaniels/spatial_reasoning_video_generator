# Deliberation Transcript: OBJ-046

---

## Round 1 — spec_author

I'll start by examining the existing codebase to understand what's already implemented for the dependencies.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the existing codebase to understand what's already implemented.
[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "depthkit/package.json"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-046/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/src/**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/package.json",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-046",
     3→  "description": "CLI interface -- Commander-based CLI with render, validate, and preview commands. Argument parsing for manifest path, output path, resolution overrides, fps overrides, verbose/debug mode. Output options (progress reporting, timing stats). Entry point at src/cli.ts.",
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
  "pattern": "**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-035/output.md",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md
Now let me check the other node specs that are relevant — specifically any nodes that the CLI would need to understand for the registry setup pattern, and the downstream consumers.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-*/output.md",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-001/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/n... [truncated]
Let me read the key outputs I need — OBJ-004 (manifest schema), OBJ-016 (manifest loader), OBJ-005 (geometry registry), OBJ-006 (camera registry), and OBJ-049 (which is a downstream peer and depends on OBJ-012). Also OBJ-038 since it's about CLI error formatting and is verified.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "limit": 100
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-016 — Manifest Loader and Validator
     2→
     3→## Summary
     4→
     5→OBJ-016 implements the manifest loading and validation pipeline defined by OBJ-004's interface contracts. It specifies how raw JSON is parsed through the two-phase validation pipeline (structural Zod parsing → semantic registry validation), how Zod errors are mapped to actionable `ManifestError` objects, how all errors are collected at once (not one-at-a-time), how file I/O works for `loadManifestFromFile()`, and how the fail-fast contract (C-10) is enforced: invalid manifests never produce partial output. This is the concrete behavioral specification for `src/manifest/loader.ts`.
     6→
     7→## Interface Contract
     8→
     9→All public exports match OBJ-004's interface contract exactly. OBJ-016 introduces one additional error code (`FILE_READ_ERROR`) for file I/O failures not covered by OBJ-004's table.
    10→
    11→### Module: `src/manifest/loader.ts`
    12→
    13→#### I... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "limit": 80
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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "limit": 80
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-038 — Audio Sync and Scene Timing
     2→
     3→## Summary
     4→
     5→OBJ-038 implements the scene timing resolution module (`src/engine/scene-timing.ts`) — the bridge between the declarative manifest timing and concrete, frame-level rendering instructions. It takes a validated Manifest (from OBJ-016), optional audio metadata (from OBJ-014's `probeMedia()`), and a timing configuration, then resolves scene durations and start times according to one of three timing modes defined in seed Section 8.7: **explicit** (manifest values as-is), **audio-proportional** (scale durations to fit audio length), or **audio-cue** (manifest `start_time` values treated as narration cue timestamps). It computes exact frame ranges per scene including transition overlaps, creates a `FrameClock` (OBJ-009) for the resolved composition, and provides a per-frame lookup function that returns which scene(s) are active with their normalized time and opacity. This module satisfies C-... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "offset": 100,
  "limit": 80
}
[Tool Result]    100→/** Camera parameters (per-scene overrides) */
   101→export const CameraParamsSchema: z.ZodType;
   102→export type CameraParams = z.infer<typeof CameraParamsSchema>;
   103→
   104→/** Plane reference (image source + optional overrides) */
   105→export const PlaneRefSchema: z.ZodType;
   106→export type PlaneRef = z.infer<typeof PlaneRefSchema>;
   107→
   108→/** A single scene */
   109→export const SceneSchema: z.ZodType;
   110→export type Scene = z.infer<typeof SceneSchema>;
   111→
   112→/** Top-level manifest */
   113→export const ManifestSchema: z.ZodType;
   114→export type Manifest = z.infer<typeof ManifestSchema>;
   115→```
   116→
   117→#### Zod Schema Shapes
   118→
   119→**AudioSchema:**
   120→```typescript
   121→{
   122→  src: z.string().min(1),                           // Path to audio file
   123→  volume: z.number().min(0).max(2).default(1.0),    // 0 = mute, 1 = normal, 2 = max boost
   124→  duration: z.number().positive().optional(),        // Se... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": 80,
  "limit": 80
}
[Tool Result]     80→   * less spatial ground.
    81→   *
    82→   * Must be > 0. Default: 1.0.
    83→   */
    84→  speed?: number;
    85→
    86→  /**
    87→   * Easing override for the primary motion.
    88→   * Replaces the preset's default easing.
    89→   */
    90→  easing?: EasingName;
    91→
    92→  /**
    93→   * Additive offset to the camera's position, in world units.
    94→   * Applied OUTSIDE evaluate() by the scene renderer — presets
    95→   * never see this value. The renderer adds offset to the position
    96→   * returned by evaluate() before setting the Three.js camera.
    97→   *
    98→   * lookAt is NOT shifted. This means offset creates a slight
    99→   * viewing angle change — the camera is displaced but still
   100→   * looks at the scene's focal point. This is intentional for
   101→   * framing adjustments (e.g., shift camera right to reframe
   102→   * the subject).
   103→   *
   104→   * Edge-reveal implication: offset displaces the frustum.
   105→  ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-049 — Software Rendering Configuration
     2→
     3→## Summary
     4→
     5→OBJ-049 delivers the `rendering-config` module (`src/engine/rendering-config.ts`) — a utility that resolves the correct *supplementary* Chromium launch arguments for software or hardware-accelerated WebGL rendering, probes the active WebGL backend after launch, and validates that the backend meets depthkit's minimum requirements. This module enforces C-11 (engine must render correctly with software WebGL / SwiftShader, without GPU passthrough) while providing an opt-in path to GPU acceleration when available. It does not own the Puppeteer lifecycle — it produces configuration that `PuppeteerBridge` (OBJ-009) consumes via its existing `gpu` and `extraArgs` config, and provides post-launch validation that `FrameCapture` (OBJ-012) and the orchestrator (OBJ-035) use to confirm rendering correctness.
     6→
     7→## Interface Contract
     8→
     9→### Module: `src/engine/rendering... [truncated]
Let me now check the OBJ-005 geometry registry pattern and OBJ-006 camera registry to understand how registries are populated:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": 80,
  "limit": 120
}
[Tool Result]     80→
    81→  /**
    82→   * Whether this plane's material should be created with
    83→   * transparent: true and expect an alpha channel in its texture.
    84→   * When true, the renderer uses alpha blending.
    85→   * When false, the texture is treated as fully opaque.
    86→   *
    87→   * Defaults to false. Typically true for subject and near_fg slots.
    88→   */
    89→  transparent?: boolean;
    90→
    91→  /**
    92→   * Whether this plane should be excluded from fog calculations.
    93→   * When true, the plane uses meshBasicMaterial regardless of scene fog,
    94→   * ensuring it renders at full brightness/opacity regardless of distance.
    95→   *
    96→   * Defaults to false. Typically true only for sky/backdrop planes
    97→   * that should remain vivid at extreme distances.
    98→   */
    99→  fogImmune?: boolean;
   100→}
   101→
   102→/**
   103→ * A complete scene geometry definition — the 3D spatial structure
   104→ * of a scene type. Each geom... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": 160,
  "limit": 120
}
[Tool Result]    160→  maxDisplacementX: number;
   161→
   162→  /**
   163→   * Maximum camera displacement along the Y axis (world units).
   164→   * Must be >= 0.
   165→   */
   166→  maxDisplacementY: number;
   167→
   168→  /**
   169→   * Maximum camera displacement along the Z axis (world units).
   170→   * Must be >= 0. Consumed by OBJ-040 to compute worst-case
   171→   * visible area at each plane's depth.
   172→   */
   173→  maxDisplacementZ: number;
   174→
   175→  /**
   176→   * The FOV range across the path's duration: [min, max] in degrees.
   177→   * Both values must be in (0, 180). min <= max.
   178→   * For paths with no FOV animation, min === max.
   179→   */
   180→  fovRange: readonly [number, number];
   181→
   182→  /**
   183→   * Recommended uniform oversize factor for "simple" plane sizing.
   184→   * A single scalar >= 1.0 that is sufficient to prevent edge reveals
   185→   * for ALL planes in all compatible geometries, assuming planes are
   186→   * sized ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": 195,
  "limit": 80
}
[Tool Result]    195→ *
   196→ * Used by:
   197→ * - Manifest validation (OBJ-017) to check geometry name existence
   198→ *   and validate plane slot keys.
   199→ * - Scene sequencer (OBJ-036) to look up geometry for a scene.
   200→ * - Page-side renderer (OBJ-039) to instantiate meshes from slots.
   201→ * - Spatial compatibility validator (OBJ-041) to cross-reference
   202→ *   geometry + camera compatibility.
   203→ */
   204→export type GeometryRegistry = Record<string, SceneGeometry>;
   205→```
   206→
   207→### Registry Access Functions
   208→
   209→```typescript
   210→// src/scenes/geometries/registry.ts
   211→
   212→import type { SceneGeometry, GeometryRegistry } from './types';
   213→
   214→/**
   215→ * Returns the complete registry of all registered scene geometries.
   216→ *
   217→ * On first call, the registry is locked — no further registrations
   218→ * are accepted (see D10). Returns a deeply frozen GeometryRegistry.
   219→ * Subsequent calls return the same fro... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": 280,
  "limit": 80
}
[Tool Result]    280→   * Tags for categorizing and searching presets in SKILL.md
   281→   * and for LLM-assisted preset selection. Lowercase.
   282→   * Examples: ['push', 'forward', 'dramatic'], ['ambient', 'subtle', 'float'].
   283→   */
   284→  tags: readonly string[];
   285→}
   286→```
   287→
   288→### Registry
   289→
   290→```typescript
   291→// src/camera/registry.ts
   292→
   293→import { CameraPathPreset } from './types';
   294→
   295→/**
   296→ * Type-safe registry of all camera path presets.
   297→ * Downstream objectives (OBJ-026 through OBJ-034) register their
   298→ * presets here. The registry is frozen at build time — no runtime mutation.
   299→ *
   300→ * Keys are preset names (lowercase snake_case). Values are CameraPathPreset objects.
   301→ */
   302→export type CameraPathRegistry = Readonly<Record<string, CameraPathPreset>>;
   303→
   304→/**
   305→ * Retrieves a camera path preset by name.
   306→ * @param registry - The camera path registry to search.
   ... [truncated]
Now let me check what OBJ-049 mentions about the rendering-config since the CLI will need to know about GpuMode:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "offset": 170,
  "limit": 50
}
[Tool Result]    170→}
   171→```
   172→
   173→**PlaneRefSchema** (`.strict()`):
   174→```typescript
   175→{
   176→  src: z.string().min(1),                           // Path/URL to image file
   177→  opacity: z.number().min(0).max(1).default(1.0),   // Static initial opacity
   178→  position_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [x, y, z] — AP-08 escape hatch
   179→  rotation_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [rx, ry, rz] — AP-08 escape hatch
   180→  scale: z.number().positive().default(1.0),         // Uniform scale multiplier
   181→}
   182→```
   183→The `position_override` and `rotation_override` fields exist per AP-08 (do not hard-code the depth model). They are optional escape hatches — never the primary authoring method (AP-03).
   184→
   185→**SceneSchema** (`.strict()`):
   186→```typescript
   187→{
   188→  id: z.string().min(1).regex(/^[a-zA-Z0-9_]+$/),  // Alphanumeric + underscore only
   189→  duration... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "limit": 60
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
Now I have enough context. Let me also quickly check what OBJ-015 (scene sequencer) looks like since OBJ-038 references it, and check how the orchestrator spec references registries being populated:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/output.md",
  "limit": 40
}
[Tool Result]      1→# Specification: OBJ-015 — Texture Loader and Format Handling
     2→
     3→## Summary
     4→
     5→OBJ-015 defines the browser-side texture loading module and its associated Node-side types. It provides: (1) a `THREE.TextureLoader`-based async texture loading API exposed on `window.depthkit`, with textures stored in a keyed map for retrieval by downstream geometry materialization; (2) alpha channel detection that samples loaded image pixel data to distinguish images with genuine transparency from those without; (3) texture metadata reporting (dimensions, aspect ratio, `hasAlpha`) back to the Node.js orchestrator; (4) a Node-side warning utility that flags non-transparent images assigned to slots that expect alpha (per OBJ-005's `PlaneSlot.transparent` field); and (5) texture lifecycle management (load, retrieve, unload, dispose). This directly satisfies C-09 (image format tolerance) and partially addresses OQ-02 (images without alpha — detect and warn, don't fix).
     6→
  ... [truncated]
Good. Now I have a comprehensive understanding of the architecture. Let me propose the spec.

---

# Specification Proposal: OBJ-046 — CLI Interface

## Summary

OBJ-046 delivers the Commander-based CLI for depthkit (`src/cli.ts`) — the primary human-facing entry point for rendering, validating, and previewing manifests. It exposes three commands (`render`, `validate`, `preview`), handles argument parsing for manifest paths, output paths, resolution/fps overrides, GPU mode, encoding presets, verbose/debug output, and provides structured progress reporting and timing statistics during renders. It composes the Orchestrator (OBJ-035), manifest loader (OBJ-016), geometry registry (OBJ-005), and camera registry (OBJ-006) into a user-friendly terminal experience. The `package.json` `bin` field points to this module.

## Interface Contract

### Module: `src/cli.ts`

This is the executable entry point. It is not designed for programmatic import — it runs `program.parse(process.argv)` at module scope. The CLI's behavior is defined entirely through its command-line interface.

### Shared Global Options

These options are available on every command:

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--verbose` | `-v` | boolean | `false` | Enable verbose output (timing stats, per-scene details, renderer info). |
| `--debug` | | boolean | `false` | Enable debug output (forwards headless Chromium console logs to stderr, enables `OrchestratorConfig.debug`). Implies `--verbose`. |
| `--color` | | boolean | auto-detected | Force color output. Default: auto-detect via `process.stdout.isTTY`. `--no-color` disables. |

### Command: `depthkit render <manifest>`

Renders a manifest to an MP4 file.

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:**

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output` | `-o` | string | `"./output.mp4"` | Output MP4 file path. |
| `--width` | `-w` | number | _(from manifest)_ | Override `composition.width`. |
| `--height` | `-h` | number | _(from manifest)_ | Override `composition.height`. |
| `--fps` | | number | _(from manifest)_ | Override `composition.fps`. |
| `--assets-dir` | `-a` | string | _(manifest's parent directory)_ | Base directory for resolving relative image paths. |
| `--gpu` | | string | `"software"` | GPU mode: `"software"`, `"hardware"`, or `"auto"`. Maps to `OrchestratorConfig.gpu` (boolean) — see D4. |
| `--preset` | | string | `"medium"` | H.264 encoding preset. One of: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`. Maps to `OrchestratorConfig.encodingPreset`. |
| `--crf` | | number | `23` | Constant Rate Factor (0–51). Maps to `OrchestratorConfig.crf`. |
| `--ffmpeg-path` | | string | _(auto-resolved)_ | Path to FFmpeg binary. Maps to `OrchestratorConfig.ffmpegPath`. |
| `--chromium-path` | | string | _(bundled)_ | Path to Chromium executable. Maps to `OrchestratorConfig.chromiumPath`. |

**Behavior:**
1. Parse and validate CLI arguments (see D2 for override application).
2. Populate registries (see D3).
3. Load manifest file via `loadManifestFromFile()` (OBJ-016).
4. Apply resolution/fps overrides to the loaded manifest (see D2).
5. Construct `OrchestratorConfig` and create `Orchestrator`.
6. Provide an `onProgress` callback that renders a progress bar to stderr (see D5).
7. Call `orchestrator.render()`.
8. On success: print summary to stdout, exit code 0.
9. On failure: print formatted error to stderr, exit code 1.

**Stdout output on success (non-verbose):**
```
✓ Rendered 1800 frames in 8m 32s → ./output.mp4
  Duration: 60.00s | Resolution: 1920×1080 | FPS: 30
  Avg frame: 284ms | File size: 12.4 MB
```

**Stdout output on success (verbose):**
```
✓ Rendered 1800 frames in 8m 32s → ./output.mp4
  Duration: 60.00s | Resolution: 1920×1080 | FPS: 30
  Avg frame: 284ms | File size: 12.4 MB
  Scenes: 5 | Geometry types: stage, tunnel, diorama
  Capture strategy: viewport-png | Encoding preset: medium | CRF: 23
  WebGL: SwiftShader (software) | WebGL 2.0
  Audio: muxed (narration.mp3)
  Warnings: 0
```

### Command: `depthkit validate <manifest>`

Validates a manifest without rendering. Fast — no browser or FFmpeg launched.

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:** None beyond global options.

**Behavior:**
1. Populate registries (see D3).
2. Load and validate manifest via `loadManifestFromFile()` (OBJ-016).
3. On valid (with or without warnings): print summary to stdout, exit code 0.
4. On invalid: print formatted errors to stderr, exit code 1.

**Stdout on valid:**
```
✓ Manifest valid: 5 scenes, 60.00s total duration
  Geometries: stage (2), tunnel (2), diorama (1)
  Cameras: slow_push_forward (3), tunnel_push_forward (2)
```

If warnings exist:
```
✓ Manifest valid with 2 warning(s): 5 scenes, 60.00s total duration
  ⚠ scenes: Scene array order differs from start_time order (SCENE_ORDER_MISMATCH)
  ⚠ scenes[2].planes.subject: Per-plane opacity is not supported in V1 (UNSUPPORTED_FEATURE)
  Geometries: stage (2), tunnel (2), diorama (1)
  Cameras: slow_push_forward (3), tunnel_push_forward (2)
```

**Stderr on invalid:**
```
✗ Manifest validation failed (3 error(s)):
  ✗ scenes[0].geometry: Unknown geometry "tunl". Available: stage, tunnel, canyon, flyover, diorama, portal, panorama, close_up (UNKNOWN_GEOMETRY)
  ✗ scenes[1].planes: Missing required slot "floor" for geometry "stage" (MISSING_REQUIRED_SLOT)
  ✗ scenes[2].camera: Unknown camera "push_fast". Available: static, slow_push_forward, ... (UNKNOWN_CAMERA)
```

### Command: `depthkit preview <manifest>`

Serves the Three.js scene on a local HTTP server for real-time preview in a browser. The human operator can preview camera motions interactively before committing to a full render. (Addresses OQ-05 from the seed.)

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:**

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--port` | `-p` | number | `3000` | HTTP server port. |
| `--open` | | boolean | `false` | Automatically open the preview URL in the default browser. |

**Behavior:**
1. Validate the manifest (same as `validate` command).
2. If valid: start an HTTP server that serves the Three.js page with the manifest's scene data, using real-time `requestAnimationFrame` playback.
3. Print the URL to stdout.
4. Keep the process running until the user presses Ctrl+C (SIGINT).

**Stdout:**
```
✓ Preview server running at http://localhost:3000
  Press Ctrl+C to stop.
```

**Scope note:** The preview command's HTTP server and page serving logic is deliberately under-specified in this objective. OBJ-046 defines the CLI command signature, argument parsing, manifest validation gate, and lifecycle (start, print URL, wait for SIGINT, cleanup). The actual preview server implementation (serving the Three.js page, real-time playback mode, scene switching) is deferred to a future objective. OBJ-046's implementation should expose a clear extension point (see D7) so the preview server can be plugged in later. If the preview server module is not yet available, the command prints an informational message and exits with code 0:

```
ℹ Preview server not yet implemented. Use 'depthkit render' for full rendering.
```

### Module: `src/cli.ts` — Programmatic Exports

While `src/cli.ts` is primarily an executable, it exports one function for testing and downstream integration (OBJ-077):

```typescript
/**
 * Creates and configures the Commander program instance.
 * Exported for testing — allows invoking CLI commands programmatically
 * without spawning a child process.
 *
 * @returns Configured Commander.Command instance with all commands registered.
 */
export function createProgram(): Command;
```

### Module: `src/cli/format.ts` — Output Formatting

Handles all terminal output formatting. Separated from `src/cli.ts` for testability.

```typescript
/**
 * Formats an OrchestratorResult into a human-readable summary string.
 *
 * @param result - The orchestrator result.
 * @param verbose - Whether to include extended details.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string (no trailing newline).
 */
export function formatRenderResult(
  result: OrchestratorResult,
  verbose: boolean,
  color: boolean,
): string;

/**
 * Formats a successful validation result into a human-readable summary.
 *
 * @param manifest - The validated manifest.
 * @param warnings - Any validation warnings.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatValidationSuccess(
  manifest: Manifest,
  warnings: ManifestError[],
  color: boolean,
): string;

/**
 * Formats validation errors into a human-readable error report.
 *
 * @param errors - All ManifestError objects from validation.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatValidationErrors(
  errors: ManifestError[],
  color: boolean,
): string;

/**
 * Formats an OrchestratorError into a human-readable error message.
 * Includes the error code, message, and context (frame number, validation errors).
 *
 * @param error - The orchestrator error.
 * @param verbose - Whether to include stack trace and cause chain.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatOrchestratorError(
  error: OrchestratorError,
  verbose: boolean,
  color: boolean,
): string;

/**
 * Formats a render progress update for terminal display.
 * Returns a single-line string suitable for overwriting the current line
 * via \r (carriage return).
 *
 * Example: "⠸ Rendering [████████░░░░░░░░] 48% | Frame 864/1800 | 3m 12s remaining"
 *
 * @param progress - The RenderProgress data from the orchestrator callback.
 * @param color - Whether to include ANSI color codes.
 * @returns Single-line string (no newline).
 */
export function formatProgress(
  progress: RenderProgress,
  color: boolean,
): string;

/**
 * Formats a file size in bytes into a human-readable string.
 * e.g., 1024 → "1.0 KB", 13042688 → "12.4 MB"
 */
export function formatFileSize(bytes: number): string;

/**
 * Formats a duration in milliseconds into a human-readable string.
 * e.g., 512000 → "8m 32s", 1500 → "1.5s", 45 → "45ms"
 */
export function formatDuration(ms: number): string;
```

### Module: `src/cli/registry-init.ts` — Registry Population

Centralizes registry population so both `render` and `validate` commands use the same registries.

```typescript
import type { ManifestRegistry } from '../manifest/schema.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

/**
 * Registry bundle returned by initRegistries().
 */
export interface RegistryBundle {
  manifestRegistry: ManifestRegistry;
  geometryRegistry: GeometryRegistry;
  cameraRegistry: CameraPathRegistry;
}

/**
 * Populates and returns all three registries needed by the orchestrator.
 *
 * This function:
 * 1. Imports all geometry modules (OBJ-018 through OBJ-025), triggering
 *    their registerGeometry() side effects.
 * 2. Calls getGeometryRegistry() to freeze and retrieve the geometry registry.
 * 3. Imports the camera registry module and retrieves the camera path registry.
 * 4. Creates a ManifestRegistry via createRegistry() and populates it
 *    by iterating the geometry and camera registries, converting each
 *    SceneGeometry → GeometryRegistration and CameraPathPreset → CameraRegistration.
 * 5. Returns the RegistryBundle.
 *
 * Must be called once at startup. Subsequent calls return the same registries
 * (because OBJ-005's registry locks on first read).
 *
 * @returns RegistryBundle with all registries populated.
 */
export function initRegistries(): RegistryBundle;
```

## Design Decisions

### D1: Commander as CLI Framework

**Decision:** Use `commander` (npm) for argument parsing and command routing.

**Rationale:** Commander is MIT-licensed, the most widely adopted Node.js CLI framework, and is already permitted by C-01 ("Standard npm utilities... are allowed"). It provides subcommand support, automatic `--help` generation, option type coercion, and default values — all of which reduce implementation effort without adding licensing risk.

### D2: Resolution/FPS Overrides Are Applied Post-Validation

**Decision:** CLI `--width`, `--height`, and `--fps` overrides are applied to the manifest object **after** Phase 1 (structural) and Phase 2 (semantic) validation, but **before** constructing the Orchestrator. The overrides mutate the `Manifest.composition` fields directly.

**Rationale:** The manifest on disk is the source of truth. Overrides are a convenience for testing different resolutions without editing the file. Applying overrides after validation ensures the base manifest is valid. The overridden values do not need re-validation because:
- Width/height: any positive integer is valid per OBJ-004's `CompositionSchema`.
- FPS: any integer in [1, 120] is valid per OBJ-004's `CompositionSchema`.

**Guard:** The CLI validates override values before applying: width and height must be positive integers; fps must be an integer in [1, 120]. Invalid CLI overrides produce an error message and exit code 1 before any manifest loading.

### D3: Registry Population is Centralized

**Decision:** A single `initRegistries()` function in `src/cli/registry-init.ts` imports all geometry and camera modules, triggering their registration side effects, and returns a `RegistryBundle` containing all three registries.

**Rationale:** Both `render` and `validate` commands need the same registries. Centralizing avoids duplication and ensures consistency. The function also bridges between OBJ-005/OBJ-006's spatial registries (which use `Record<string, T>` and `registerGeometry()` side effects) and OBJ-004's `ManifestRegistry` (which uses `Map<string, T>` and `registerGeometry()`/`registerCamera()`).

**Key detail:** The `ManifestRegistry` (OBJ-004) stores validation-only metadata (`GeometryRegistration`, `CameraRegistration`), while the spatial registries (`GeometryRegistry`, `CameraPathRegistry`) store full 3D data. `initRegistries()` must convert between them:
- `SceneGeometry` → `GeometryRegistration`: extract `name`, `slots` (convert `PlaneSlot` → `PlaneSlotDef` by keeping only `required` and `description`), `compatibleCameras` (from `compatible_cameras`), `defaultCamera` (from `default_camera`).
- `CameraPathPreset` → `CameraRegistration`: extract `name`, `compatibleGeometries`, `supportsFovAnimation` (derived from `oversizeRequirements.fovRange[0] !== oversizeRequirements.fovRange[1]`).

### D4: GPU Mode Mapping

**Decision:** The CLI `--gpu` flag accepts `"software"`, `"hardware"`, or `"auto"` (string). This maps to `OrchestratorConfig.gpu` (boolean) as follows:
- `"software"` → `gpu: false`
- `"hardware"` → `gpu: true`
- `"auto"` → `gpu: false` (V1 simplification)

**Rationale:** OBJ-035's `OrchestratorConfig.gpu` is a simple boolean (true = use GPU, false = software). OBJ-049 defines a richer `GpuMode` type (`'software' | 'hardware' | 'auto'`) but that integration is between OBJ-049 and OBJ-035. For V1, the CLI maps to the boolean. When OBJ-049 is integrated into the orchestrator (OBJ-050), the CLI can be updated to pass the string directly. The `--gpu` flag is a string (not boolean) to preserve forward compatibility — no breaking change needed later.

### D5: Progress Reporting via stderr

**Decision:** The `onProgress` callback writes progress updates to stderr using carriage return (`\r`) line overwriting. When stderr is not a TTY (piped to a file or another process), progress is suppressed entirely.

**Rationale:**
- **stderr, not stdout:** Stdout is reserved for the final result summary. This allows `depthkit render manifest.json > result.txt` to capture only the summary, while progress appears in the terminal.
- **Carriage return overwriting:** Standard CLI progress bar pattern. Single-line updates that overwrite each other. After completion, a final newline is written so the success message appears on a fresh line.
- **TTY detection:** Piped stderr should not contain ANSI escape codes or carriage-return progress spam.

### D6: Exit Codes

**Decision:**
| Exit Code | Meaning |
|---|---|
| `0` | Success (render complete, manifest valid, preview started). |
| `1` | Failure (validation error, render error, invalid arguments). |
| `2` | Usage error (unknown command, missing required argument). Commander handles this by default. |

**Rationale:** Standard Unix convention. Only three codes are needed — the error message itself provides specificity.

### D7: Preview Command Stub with Extension Point

**Decision:** The `preview` command validates the manifest and then attempts to dynamically import a preview server module (`../preview/server.js`). If the import fails (module doesn't exist yet), it prints an informational message and exits with code 0.

**Rationale:** The preview server is outside OBJ-046's scope but the CLI command should be registered now so the `--help` output is complete. Dynamic import keeps the dependency optional — no build errors if the preview module doesn't exist.

### D8: Assets Dir Default

**Decision:** If `--assets-dir` is not provided, the default is the **parent directory of the manifest file**, not `process.cwd()`. This matches the common pattern where images sit alongside or relative to the manifest.

**Rationale:** OBJ-035's default `assetsDir` is `process.cwd()`, which is appropriate for the programmatic API. For CLI usage, the manifest's directory is more intuitive — a user running `depthkit render ./projects/video1/manifest.json` expects image paths in the manifest to resolve relative to `./projects/video1/`, not the current directory.

### D9: SIGINT Handling

**Decision:** During rendering, SIGINT (Ctrl+C) is caught and converted to a cancellation request. The `onProgress` callback checks a flag and returns `false` to trigger the orchestrator's graceful shutdown. A second SIGINT force-kills the process.

**Rationale:** Graceful shutdown ensures FFmpeg is properly terminated and partial files are cleaned up, per OBJ-035's cleanup guarantees. The second-SIGINT escape hatch prevents the process from becoming unkillable if cleanup hangs.

### D10: No Color Dependency

**Decision:** ANSI color codes are generated using inline escape sequences, not a color library (chalk, kleur, etc.). A minimal color utility (6-8 functions: `red`, `green`, `yellow`, `cyan`, `bold`, `dim`, `reset`) is implemented in `src/cli/colors.ts`.

**Rationale:** Minimizes dependencies. The CLI needs only basic colors (red for errors, green for success, yellow for warnings, cyan for info, dim for secondary text). A full color library is overkill. The `--color` / `--no-color` flag and TTY detection control whether escape codes are emitted.

### D11: File Size in Summary

**Decision:** The render summary includes the output file size. This requires a `fs.stat()` call on the output MP4 after `render()` completes.

**Rationale:** File size is the most commonly wanted piece of information after a render — it tells the user whether the output is reasonable and whether the CRF/preset settings need adjustment.

## Acceptance Criteria

### Argument Parsing

- [ ] **AC-01:** `depthkit render manifest.json` renders the manifest to `./output.mp4` (default output path).
- [ ] **AC-02:** `depthkit render manifest.json -o video.mp4` renders to the specified output path.
- [ ] **AC-03:** `depthkit render manifest.json --width 1080 --height 1920 --fps 24` overrides the manifest's composition settings. The output video is 1080×1920 at 24fps.
- [ ] **AC-04:** `depthkit render` with no manifest argument prints a usage error and exits with code 2.
- [ ] **AC-05:** `depthkit render manifest.json --gpu hardware --preset slow --crf 18` passes the correct values to the orchestrator.
- [ ] **AC-06:** `depthkit --help` prints help with all three commands listed. `depthkit render --help` prints render-specific options.
- [ ] **AC-07:** `depthkit --version` prints the version from `package.json`.

### Validate Command

- [ ] **AC-08:** `depthkit validate manifest.json` with a valid manifest prints a success summary and exits with code 0. No browser or FFmpeg process is launched.
- [ ] **AC-09:** `depthkit validate manifest.json` with an invalid manifest prints all errors to stderr and exits with code 1.
- [ ] **AC-10:** `depthkit validate manifest.json` with a valid manifest that has warnings prints both the success summary and the warnings, and exits with code 0.

### Render Command — Success Path

- [ ] **AC-11:** A successful render prints a summary to stdout including frame count, duration, resolution, fps, average frame time, and file size.
- [ ] **AC-12:** With `--verbose`, the summary additionally includes scene count, geometry types used, capture strategy, encoding preset, CRF, WebGL renderer info, audio status, and warning count.
- [ ] **AC-13:** During rendering, a progress bar updates on stderr showing percentage, current/total frames, and estimated remaining time. The progress bar is suppressed when stderr is not a TTY.

### Render Command — Error Path

- [ ] **AC-14:** A `MANIFEST_INVALID` orchestrator error prints all validation errors to stderr in the same format as the `validate` command, and exits with code 1.
- [ ] **AC-15:** A non-validation orchestrator error (e.g., `ENCODE_FAILED`) prints the error code, message, and (if `--verbose`) the cause chain to stderr, and exits with code 1.
- [ ] **AC-16:** Invalid CLI argument values (e.g., `--fps -5`, `--crf 60`, `--gpu banana`) print a descriptive error and exit with code 1, before any manifest loading.
- [ ] **AC-17:** A non-existent manifest file path prints `"Manifest file not found: <path>"` and exits with code 1.

### Preview Command

- [ ] **AC-18:** `depthkit preview manifest.json` validates the manifest. If valid, attempts to start the preview server. If the preview server module is not available, prints an informational message and exits with code 0.
- [ ] **AC-19:** `depthkit preview invalid-manifest.json` prints validation errors and exits with code 1 (same as `validate`).

### SIGINT Handling

- [ ] **AC-20:** Pressing Ctrl+C during a render triggers graceful cancellation. The orchestrator's `CANCELLED` error is caught, partial files are cleaned up (per OBJ-035), and the process exits with code 1 and message `"Render cancelled."`.
- [ ] **AC-21:** Pressing Ctrl+C twice force-kills the process immediately.

### Output Formatting

- [ ] **AC-22:** All stderr error output uses red coloring (when color is enabled). Success uses green. Warnings use yellow.
- [ ] **AC-23:** `--no-color` suppresses all ANSI escape codes in both stdout and stderr output.
- [ ] **AC-24:** Progress bar format includes a spinner, visual bar, percentage, frame counter, and ETA.

### Assets Dir

- [ ] **AC-25:** When `--assets-dir` is not specified, relative image paths in the manifest are resolved against the manifest file's parent directory.
- [ ] **AC-26:** When `--assets-dir /custom/path` is specified, relative image paths resolve against `/custom/path`.

### Registry Initialization

- [ ] **AC-27:** Both `render` and `validate` commands use the same registry population logic. A geometry or camera available to `validate` is also available to `render`.
- [ ] **AC-28:** If no geometries are registered (empty registry), `validate` reports `UNKNOWN_GEOMETRY` for every scene — it does not crash.

## Edge Cases and Error Handling

### CLI Argument Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `--width 0` or `--width -1` | Error: "Width must be a positive integer." Exit code 1. |
| `--fps 0` or `--fps 200` | Error: "FPS must be an integer between 1 and 120." Exit code 1. |
| `--crf -1` or `--crf 52` | Error: "CRF must be between 0 and 51." Exit code 1. |
| `--gpu invalid` | Error: "GPU mode must be one of: software, hardware, auto." Exit code 1. |
| `--preset invalid` | Error: "Encoding preset must be one of: ultrafast, superfast, ..." Exit code 1. |
| `--output` pointing to a read-only directory | FFmpeg fails → `ENCODE_FAILED`. Orchestrator error formatted and printed. Exit code 1. |
| Manifest path is a directory, not a file | `loadManifestFromFile()` returns `FILE_READ_ERROR`. Formatted and printed. Exit code 1. |
| Manifest file is valid JSON but not a valid manifest | Validation errors listed. Exit code 1. |
| Manifest file is not valid JSON | `INVALID_JSON` error. Exit code 1. |
| `--width` without `--height` (or vice versa) | Allowed. Only the specified dimension is overridden; the other comes from the manifest. |

### Runtime Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Render succeeds but output file is 0 bytes | Summary prints "0 B" for file size. No special handling — the file was created by FFmpeg. |
| Very long render (>1 hour) | Duration formats as "1h 12m 45s". Progress bar ETA formats similarly. |
| Very short render (<1 second) | Duration formats as "0.8s" or "845ms". |
| SIGINT during validation (before render starts) | Process exits immediately (validation is synchronous and fast). |
| SIGINT during audio mux phase | Orchestrator handles cleanup per OBJ-035. CLI catches the `CANCELLED` error. |
| Orchestrator throws an unexpected non-OrchestratorError | Caught by a top-level handler. Prints "Unexpected error: <message>". If `--verbose`, includes stack trace. Exit code 1. |
| Multiple `--width` flags (e.g., `--width 1080 --width 720`) | Commander takes the last value. Standard behavior. |

### Output Formatting Edge Cases

| Scenario | Expected Behavior |
|---|---|
| No audio in manifest | Summary omits the "Audio: ..." line (non-verbose) or shows "Audio: none" (verbose). |
| 0 warnings | Verbose summary shows "Warnings: 0". Non-verbose omits. |
| 50+ validation errors | All errors are printed. No truncation. |
| Very long file paths in error messages | Not truncated. Terminal wrapping handles it. |
| Unicode in manifest file paths | Handled natively by Node.js fs module. No special treatment. |

## Test Strategy

### Unit Tests: `test/unit/cli/format.test.ts`

These test the formatting module in isolation.

1. **formatRenderResult — non-verbose:** Given an `OrchestratorResult` with known values, verify the output matches the expected format with frame count, duration, resolution, fps, avg frame time, and file size.

2. **formatRenderResult — verbose:** Same result, verify extended output includes scene count, geometry types, WebGL info, audio status, warnings.

3. **formatRenderResult — no audio:** Verify the "Audio" line is omitted (non-verbose) or shows "none" (verbose) when `audioResult` is null.

4. **formatValidationSuccess — no warnings:** Verify output includes scene count, total duration, geometry summary, camera summary.

5. **formatValidationSuccess — with warnings:** Verify warnings are listed with `⚠` prefix and error codes.

6. **formatValidationErrors:** Given 3 `ManifestError` objects, verify each is formatted with `✗`, path, message, and code.

7. **formatOrchestratorError — MANIFEST_INVALID:** Verify validation errors are listed.

8. **formatOrchestratorError — ENCODE_FAILED, verbose:** Verify cause chain is included.

9. **formatProgress:** Given progress at 48%, verify the single-line output contains a bar, percentage, frame counter, and ETA.

10. **formatProgress — 0%:** First frame. ETA shows "calculating...".

11. **formatProgress — 100%:** Last frame. ETA shows "0s".

12. **formatFileSize:** Test bytes, KB, MB, GB boundaries.

13. **formatDuration:** Test ms, seconds, minutes, hours boundaries.

14. **Color disabled:** All format functions with `color: false` produce strings with no ANSI escape sequences.

### Unit Tests: `test/unit/cli/registry-init.test.ts`

15. **initRegistries returns populated bundle:** Verify `manifestRegistry.geometries.size > 0`, `manifestRegistry.cameras.size > 0`, and both spatial registries are non-empty.

16. **Geometry conversion:** Verify a `SceneGeometry` is correctly converted to `GeometryRegistration` — `required` and `description` are preserved, spatial data is not present.

17. **Camera conversion:** Verify a `CameraPathPreset` is correctly converted to `CameraRegistration` — `supportsFovAnimation` is true when `fovRange[0] !== fovRange[1]`.

18. **Idempotent:** Calling `initRegistries()` twice returns equivalent registries (same keys, same values).

### Integration Tests: `test/integration/cli.test.ts`

These spawn the CLI as a child process (or use `createProgram().parseAsync()`) with real or minimal test manifests.

19. **render — success:** Create a minimal valid manifest with a test geometry and a solid-color test image. Run `depthkit render manifest.json -o output.mp4`. Verify exit code 0, stdout contains "Rendered", output file exists.

20. **render — invalid manifest:** Run `depthkit render broken.json`. Verify exit code 1, stderr contains error code.

21. **render — missing file:** Run `depthkit render nonexistent.json`. Verify exit code 1, stderr contains "not found".

22. **validate — valid:** Run `depthkit validate manifest.json`. Verify exit code 0, stdout contains "valid".

23. **validate — invalid:** Run `depthkit validate broken.json`. Verify exit code 1, stderr contains errors.

24. **validate — warnings:** Run `depthkit validate manifest-with-warnings.json`. Verify exit code 0, stdout contains both success and warning messages.

25. **render — resolution override:** Run with `--width 320 --height 240 --fps 10`. Verify output MP4 is 320×240 via ffprobe.

26. **render — assets-dir:** Create a manifest with `./images/bg.png`, images in a separate directory. Run with `--assets-dir <dir>`. Verify render succeeds.

27. **render — default assets-dir:** Run without `--assets-dir`. Verify images are resolved relative to the manifest's parent directory.

28. **help output:** Run `depthkit --help`. Verify output lists `render`, `validate`, `preview` commands.

29. **version output:** Run `depthkit --version`. Verify it prints a semver string.

30. **invalid arguments:** Run `depthkit render manifest.json --fps -5`. Verify exit code 1, stderr contains "FPS must be".

31. **no-color:** Run `depthkit render manifest.json --no-color`. Verify stdout/stderr contain no ANSI escape codes.

32. **preview — stub:** Run `depthkit preview manifest.json`. If preview module is absent, verify exit code 0 and informational message.

### Relevant Testable Claims

- **TC-04:** Tests 19, 22 verify that the CLI (using geometry names and slot keys) produces correct output.
- **TC-07:** Tests 20, 23 verify manifest validation catches errors via the CLI path.
- **TC-11:** All integration tests can run with default `--gpu software` (software WebGL).

## Integration Points

### Depends on

| Dependency | What OBJ-046 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`, `OrchestratorErrorCode`, `RenderProgress`, `renderFromFile()`. |
| **OBJ-004** (Manifest Schema) | `Manifest`, `ManifestError`, `ManifestRegistry`, `createRegistry()`, `GeometryRegistration`, `CameraRegistration`, `PlaneSlotDef`. |
| **OBJ-016** (Manifest Loader) | `loadManifestFromFile()`, `loadManifest()`, `computeTotalDuration()`. |
| **OBJ-005** (Geometry Registry) | `GeometryRegistry`, `SceneGeometry`, `getGeometryRegistry()`, `registerGeometry()`. Imported transitively by `registry-init.ts`. |
| **OBJ-006** (Camera Registry) | `CameraPathRegistry`, `CameraPathPreset`. The camera registry module. |
| **OBJ-018–025** (Individual Geometries) | Imported for their `registerGeometry()` side effects by `registry-init.ts`. |
| **OBJ-026–034** (Individual Camera Presets) | Imported for their registration side effects by `registry-init.ts`. |

### Consumed by

| Downstream | How it uses OBJ-046 |
|---|---|
| **OBJ-050** (Preview Server Integration) | The preview command stub will be connected to the actual preview server when OBJ-050 is implemented. |
| **OBJ-070** (SKILL.md) | Documents CLI usage, command syntax, and examples for LLM authors and human operators. |
| **OBJ-075** (n8n HTTP Interface) | May invoke the CLI as a subprocess, or may use the programmatic API directly (via `Orchestrator`). The CLI provides a tested, validated entry path. |
| **OBJ-077** (End-to-End Integration) | Uses the CLI or `createProgram()` to run full pipeline tests. |

### File Placement

```
depthkit/
  src/
    cli.ts                      # NEW — Main CLI entry point, Commander setup, command handlers
    cli/
      format.ts                 # NEW — Output formatting (render result, validation, progress, errors)
      colors.ts                 # NEW — Minimal ANSI color utilities
      registry-init.ts          # NEW — Registry population bridge
  test/
    unit/
      cli/
        format.test.ts          # NEW — Format function unit tests
        registry-init.test.ts   # NEW — Registry initialization unit tests
    integration/
      cli.test.ts               # NEW — CLI integration tests (child process or programmatic)
```

The `package.json` `bin` field should include:
```json
{
  "bin": {
    "depthkit": "./dist/cli.js"
  }
}
```

(Assuming TypeScript compiles to `dist/`. Exact path depends on `tsconfig.json` `outDir`.)

## Open Questions

### OQ-A: Should the CLI support `--quiet` mode?

A `--quiet` flag that suppresses all output except errors (no progress bar, no success summary) could be useful for scripted pipelines. Currently not specified — can be added as a minor enhancement.

### OQ-B: Should `validate` check image file existence?

Currently `validate` runs OBJ-016's two-phase validation (structural + semantic), which does not check whether image files exist on disk. Adding a `--check-assets` flag to `validate` that runs OBJ-035's pre-flight image check (without launching the browser) would catch missing files earlier. This would require extracting the image path resolution logic from the orchestrator into a shared utility.

### OQ-C: Should the render command support `--dry-run`?

A `--dry-run` flag that validates the manifest and computes the frame count / estimated duration without actually rendering could be useful for pipeline planning. This is strictly a superset of `validate` with additional computation.

### OQ-D: Should progress be emitted as JSON for machine consumption?

A `--json` flag that emits progress as newline-delimited JSON objects (one per frame or per-second) would be useful for n8n or other automation tools. Currently deferred — the n8n integration (OBJ-075) may use the programmatic API instead.

### OQ-E: Should the CLI read environment variables for defaults?

E.g., `DEPTHKIT_FFMPEG_PATH`, `DEPTHKIT_GPU_MODE`, `DEPTHKIT_ASSETS_DIR`. Commander supports `.env()` on options. Low priority but trivial to add.

---

I believe this spec is comprehensive. I'd like the Challenger to verify:
1. The registry population bridge (`registry-init.ts`) correctly bridges between OBJ-005/006's spatial registries and OBJ-004's `ManifestRegistry`.
2. The GPU mode mapping (D4) is a reasonable V1 simplification.
3. The assets-dir default (D8) is the right choice vs. `process.cwd()`.
4. The preview command stub approach (D7) is appropriate for scope.
5. The format module is sufficiently specified without being over-prescriptive.

---

## Round 2 — spec_challenger

Let me verify a few critical details in the dependency specs before I challenge.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "offset": "0",
  "limit": "100"
}
[Tool Result]      0→# Specification: OBJ-004 — Manifest Schema Core
     1→
     2→## Summary
     3→
     4→OBJ-004 defines the Zod validation schema and loader for the depthkit manifest — the declarative JSON document that describes an entire video. This is the authoring contract between LLM manifest authors and the rendering engine. The schema enforces structural correctness (types, ranges, required fields) via Zod parsing and semantic correctness (geometry existence, camera compatibility, plane-slot matching) via a registry-backed validation pass. It satisfies C-04 (resolution/fps support) and C-10 (validate before rendering, fail fast with actionable errors).
     5→
     6→## Interface Contract
     7→
     8→### Module: `src/manifest/schema.ts`
     9→
    10→Exports Zod schemas, inferred TypeScript types, and the registry interfaces that downstream geometry/camera objectives use to register their definitions.
    11→
    12→```typescript
    13→// === Registry Interfaces ===
    14→
    15→... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": "290",
  "limit": "80"
}
[Tool Result]    290→```typescript
   291→// src/camera/registry.ts
   292→
   293→import { CameraPathPreset } from './types';
   294→
   295→/**
   296→ * Type-safe registry of all camera path presets.
   297→ * Downstream objectives (OBJ-026 through OBJ-034) register their
   298→ * presets here. The registry is frozen at build time — no runtime mutation.
   299→ *
   300→ * Keys are preset names (lowercase snake_case). Values are CameraPathPreset objects.
   301→ */
   302→export type CameraPathRegistry = Readonly<Record<string, CameraPathPreset>>;
   303→
   304→/**
   305→ * Retrieves a camera path preset by name.
   306→ * @param registry - The camera path registry to search.
   307→ * @param name - The preset name.
   308→ * @returns The CameraPathPreset.
   309→ * @throws {Error} if name is not found. Error message includes the
   310→ *   invalid name and lists all available preset names.
   311→ */
   312→export function getCameraPath(
   313→  registry: CameraPathRegistry,
   314→  name: ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "offset": "117",
  "limit": "70"
}
[Tool Result]    117→#### Zod Schema Shapes
   118→
   119→**AudioSchema:**
   120→```typescript
   121→{
   122→  src: z.string().min(1),                           // Path to audio file
   123→  volume: z.number().min(0).max(2).default(1.0),    // 0 = mute, 1 = normal, 2 = max boost
   124→  duration: z.number().positive().optional(),        // Seconds. When present, enables AUDIO_DURATION_MISMATCH check.
   125→}
   126→```
   127→
   128→**CompositionSchema** (`.strict()`):
   129→```typescript
   130→{
   131→  width: z.number().int().positive(),
   132→  height: z.number().int().positive(),
   133→  fps: z.number().int().min(1).max(120),
   134→  audio: AudioSchema.optional(),
   135→}
   136→```
   137→Note: C-04 requires support for 1920x1080, 1080x1920, 24fps, 30fps — but the schema does NOT restrict to only those values. It accepts any positive integer dimensions and any integer fps in [1, 120]. The constraint is that those four combinations *must work*; others may also work.
   138→
   139... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": "200",
  "limit": "60"
}
[Tool Result]    200→ * - Page-side renderer (OBJ-039) to instantiate meshes from slots.
   201→ * - Spatial compatibility validator (OBJ-041) to cross-reference
   202→ *   geometry + camera compatibility.
   203→ */
   204→export type GeometryRegistry = Record<string, SceneGeometry>;
   205→```
   206→
   207→### Registry Access Functions
   208→
   209→```typescript
   210→// src/scenes/geometries/registry.ts
   211→
   212→import type { SceneGeometry, GeometryRegistry } from './types';
   213→
   214→/**
   215→ * Returns the complete registry of all registered scene geometries.
   216→ *
   217→ * On first call, the registry is locked — no further registrations
   218→ * are accepted (see D10). Returns a deeply frozen GeometryRegistry.
   219→ * Subsequent calls return the same frozen object.
   220→ *
   221→ * Mutation attempts on the returned object or any nested object
   222→ * (geometry, slot, position tuple) throw TypeError at runtime.
   223→ *
   224→ * @returns A deeply frozen Geometr... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "offset": "185",
  "limit": "40"
}
[Tool Result]    185→**SceneSchema** (`.strict()`):
   186→```typescript
   187→{
   188→  id: z.string().min(1).regex(/^[a-zA-Z0-9_]+$/),  // Alphanumeric + underscore only
   189→  duration: z.number().positive(),                   // Seconds, must be > 0
   190→  start_time: z.number().nonnegative(),              // Seconds, >= 0
   191→  geometry: z.string().min(1),                       // Validated against registry in semantic pass
   192→  camera: z.string().min(1),                         // Validated against registry in semantic pass
   193→  camera_params: CameraParamsSchema.optional(),
   194→  transition_in: TransitionSchema.optional(),
   195→  transition_out: TransitionSchema.optional(),
   196→  planes: z.record(z.string(), PlaneRefSchema),      // Keys validated against geometry slots in semantic pass
   197→}
   198→```
   199→
   200→**ManifestSchema** (`.passthrough()` at top level):
   201→```typescript
   202→{
   203→  version: z.literal("3.0"),
   204→  composition: Compositio... [truncated]
Good. Now I have the full picture. Let me also check one more thing about `CameraParams` in OBJ-004 vs OBJ-006:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": "60",
  "limit": "30"
}
[Tool Result]     60→ * Presets receive RESOLVED params (via resolveCameraParams), never raw
    61→ * CameraParams. See ResolvedCameraParams.
    62→ *
    63→ * Unrecognized fields are ignored (not rejected) — this allows presets
    64→ * to evolve without breaking existing manifests.
    65→ */
    66→export interface CameraParams {
    67→  /**
    68→   * Amplitude/displacement multiplier. Scales the spatial intensity
    69→   * of the path's motion, NOT its temporal rate.
    70→   *
    71→   * For linear paths (push/pull/track): scales total displacement.
    72→   *   speed=0.5 on a 25-unit Z push -> 12.5-unit push.
    73→   * For oscillating paths (gentle_float): scales amplitude.
    74→   *   speed=0.5 -> half the drift range in each axis.
    75→   * For FOV-animating paths (dolly_zoom): scales FOV delta.
    76→   *   speed=0.5 -> half the FOV change.
    77→   *
    78→   * The temporal easing curve is unaffected. A speed=0.5 path still
    79→   * starts and ends at the same norma... [truncated]
Now I have enough context. Let me write my challenge.

---

## Challenger Review — Round 1

Good first draft. The overall structure is sound and the scope is appropriate for a CLI interface objective. I'll go through my findings organized by severity.

### Points of Agreement (These Are Sound)

- **Three-command structure** (render, validate, preview) — correct decomposition.
- **D1: Commander** — right tool, MIT-licensed, seed-compliant.
- **D5: Progress on stderr** — correctly separates machine-consumable stdout from human-facing progress.
- **D6: Exit codes** — standard Unix convention, appropriate.
- **D8: Assets-dir default** — manifests directory is more intuitive for CLI use than `process.cwd()`. The divergence from OBJ-035's default is correctly documented and well-reasoned.
- **D9: SIGINT handling** — two-stage interrupt is standard and necessary.
- **D10: No color dependency** — inline ANSI is the right call for minimizing deps.
- **D11: File size in summary** — useful, trivially implemented.
- **Edge cases table** — thorough and well-organized.
- **Format module separation** — good for testability.

### Issue 1: `-h` Short Flag Conflicts with Commander's `--help` (Critical)

**What:** The options table maps `--height` to short flag `-h`. Commander reserves `-h` for its auto-generated `--help` flag. This will either cause a runtime error or silently shadow `--help`.

**Fix:** Remove the `-h` short flag for `--height`. Either leave height without a short flag, or use `-H` (uppercase). I'd recommend no short flag — height overrides are rare enough that they don't warrant one.

### Issue 2: `initRegistries()` Sync vs Async Ambiguity (Major)

**What:** The function signature shows `initRegistries(): RegistryBundle` (synchronous). But to import geometry modules (OBJ-018 through OBJ-025) and camera modules (OBJ-026 through OBJ-034), the implementation has two choices:
1. Static top-level imports — side effects run at module load time, function is sync.
2. Dynamic `import()` — must be async.

The spec doesn't state which approach is required. An implementer choosing dynamic imports would need to change the signature to `async`, which changes the calling code in both `render` and `validate` handlers.

**Fix:** Either (a) explicitly state that `initRegistries()` uses **static imports** at the top of `registry-init.ts` (making the function body purely synchronous — it just calls `getGeometryRegistry()`, iterates, and builds the bundle), or (b) make the signature `async function initRegistries(): Promise<RegistryBundle>`. Given that registry-init is loaded once at startup and all geometry/camera modules are known at build time, option (a) is simpler and correct.

### Issue 3: `createProgram()` Testability — Missing `exitOverride()` (Major)

**What:** The spec exports `createProgram()` for testing but doesn't specify whether Commander's `exitOverride()` is called. By default, Commander calls `process.exit()` on errors (missing arguments, unknown commands). This makes programmatic testing via `createProgram().parseAsync(['render'])` kill the test runner.

**Fix:** Add to the `createProgram()` doc: "The returned program has `exitOverride()` enabled. Instead of calling `process.exit()`, Commander throws a `CommanderError` with `exitCode` and `message`. The `src/cli.ts` entry point catches `CommanderError` and calls `process.exit(error.exitCode)`. This separation ensures `createProgram()` is safe for programmatic invocation in tests."

### Issue 4: `CameraParams.offset` Missing from OBJ-004 Schema (Major — Verification)

**What:** OBJ-035 D4 mentions applying `camera_params.offset` additively to position. The spec's render options don't expose this, which is fine — it's a manifest-level concern. But D3 references converting `CameraPathPreset → CameraRegistration` and mentions deriving `supportsFovAnimation` from `oversizeRequirements.fovRange`. I verified against OBJ-004 and OBJ-006 — the conversion logic is correct. `PlaneSlotDef` is confirmed in OBJ-004 (lines 19-22). The `GeometryRegistration` shape matches (lines 30-35).

However, OBJ-004's `CameraParamsSchema` does **not** include an `offset` field (it has `speed`, `easing`, `fov_start`, `fov_end`). Yet OBJ-006's `CameraParams` type includes `offset?: Vec3`. The orchestrator (OBJ-035 D4) says "Applies `camera_params.offset` (if any) additively." This is a discrepancy between the manifest schema (OBJ-004) and the camera type system (OBJ-006), but it's **not OBJ-046's problem to solve**. Noting this for awareness — the CLI correctly passes through whatever the manifest contains.

**No fix required for OBJ-046.** But flag it as an open question.

### Issue 5: Missing Shebang Specification (Minor)

**What:** The spec mentions `package.json`'s `bin` field pointing to `./dist/cli.js` but doesn't mention that the compiled output needs a `#!/usr/bin/env node` shebang line. Without it, `npx depthkit` or a global install won't work.

**Fix:** Add a note: "The compiled `dist/cli.js` must begin with `#!/usr/bin/env node`. This is typically configured via TypeScript's `tsconfig.json` or a build script that prepends the shebang. The entry point source file (`src/cli.ts`) should include a leading comment `#!/usr/bin/env node` that the compiler preserves or that the build step adds."

### Issue 6: `--version` Source Not Specified (Minor)

**What:** AC-07 says `depthkit --version` prints the version from `package.json`. But the spec doesn't specify how the version is obtained at runtime. Options: (a) `require('../package.json').version`, (b) read and parse package.json from disk, (c) inject at build time.

**Fix:** Add to the design decisions or interface contract: "Version is read from `package.json` using `import { readFileSync } from 'fs'` and `JSON.parse()` at module load time, resolving the package.json path relative to `__dirname`. Alternatively, use Commander's `.version()` method with the version string extracted from package.json."

### Issue 7: Progress Bar — Spinner State Source (Minor)

**What:** The `formatProgress()` function takes `RenderProgress` and returns a string that includes a spinner (`⠸`). But `RenderProgress` has no spinner-state field. The spinner must cycle through frames, implying state external to the function.

**Fix:** Either (a) derive spinner state from `progress.frame % SPINNER_CHARS.length` (documented in the function's description), or (b) add a `spinnerIndex: number` parameter. Option (a) is simpler and the spec should just state it: "Spinner character cycles based on `progress.frame % SPINNER_FRAMES.length` using Braille dot characters."

### Issue 8: `initRegistries()` Camera Registry Population Mechanism Unspecified (Major)

**What:** The spec describes how geometry modules use `registerGeometry()` side effects. But OBJ-006's `CameraPathRegistry` is `Readonly<Record<string, CameraPathPreset>>` — it's a plain frozen object, not a mutable registry with a `register()` function. How does `initRegistries()` obtain the camera registry? OBJ-006 doesn't define a `getCameraPathRegistry()` equivalent to OBJ-005's `getGeometryRegistry()`.

The spec says "Imports the camera registry module and retrieves the camera path registry" — but **which module** and **which function**? The implementer would have to guess.

**Fix:** Specify explicitly: "The camera registry is obtained by importing the camera registry module (`src/camera/registry.ts`). If OBJ-006 does not provide a global `getCameraPathRegistry()` function analogous to OBJ-005's `getGeometryRegistry()`, then `registry-init.ts` must construct the `CameraPathRegistry` by importing each camera preset module (OBJ-026 through OBJ-034) and assembling them into a `Record<string, CameraPathPreset>`. The exact import mechanism depends on the camera module implementations — `initRegistries()` should document which modules it imports." Also, if the camera registry API is uncertain, flag this as an open question rather than leaving it implicit.

### Issue 9: Missing AC for `--debug` Behavior (Minor)

**What:** D3 in the global options says `--debug` "implies `--verbose`" and forwards Chromium console logs. But no acceptance criterion tests that `--debug` actually enables verbose output or that browser console output appears on stderr.

**Fix:** Add: 
- **AC-29:** `depthkit render manifest.json --debug` produces verbose output (same as `--verbose`) plus headless browser console messages on stderr.

### Issue 10: `formatValidationSuccess` Needs `ManifestRegistry` to List Available Resources? (Minor)

**What:** The validation success output format shows "Geometries: stage (2), tunnel (2), diorama (1)" — this is derivable from iterating `manifest.scenes` and counting `.geometry` values. Fine. But the *invalid* validation output shows "Available: stage, tunnel, canyon, ..." — this requires knowing all registered geometry names. The `formatValidationErrors` function signature takes only `errors: ManifestError[]` and `color: boolean`. The available names must already be embedded in the error messages by OBJ-016.

Let me verify: OBJ-004's error codes table likely includes the available names in the `message` field. If so, this is fine — the CLI just prints the message. If not, `formatValidationErrors` would need the registry.

Given that OBJ-016 is responsible for producing actionable error messages (per C-10), and those messages should include available options, this is likely handled upstream. **No fix needed**, but worth noting the assumption: "Validation error messages from OBJ-016 include available options (geometry names, camera names) in their `message` field. The CLI does not need access to registries for error formatting."

---

### Summary of Required Fixes Before Convergence

| # | Severity | Issue | Status |
|---|---|---|---|
| 1 | **Critical** | `-h` conflicts with `--help` | Needs fix |
| 2 | **Major** | `initRegistries()` sync vs async | Needs explicit choice |
| 3 | **Major** | `createProgram()` missing `exitOverride()` | Needs fix |
| 8 | **Major** | Camera registry population mechanism unspecified | Needs fix |
| 5 | Minor | Missing shebang specification | Needs fix |
| 6 | Minor | `--version` source mechanism | Needs fix |
| 7 | Minor | Spinner state derivation | Needs fix |
| 9 | Minor | Missing AC for `--debug` | Needs fix |

Please revise the spec addressing at minimum issues 1, 2, 3, and 8 before I consider convergence.

---

## Round 3 — spec_author

Thank you for the thorough review. All issues are valid. Here's my revised spec addressing each one.

---

# Specification: OBJ-046 — CLI Interface

## Summary

OBJ-046 delivers the Commander-based CLI for depthkit (`src/cli.ts`) — the primary human-facing entry point for rendering, validating, and previewing manifests. It exposes three commands (`render`, `validate`, `preview`), handles argument parsing for manifest paths, output paths, resolution/fps overrides, GPU mode, encoding presets, verbose/debug output, and provides structured progress reporting and timing statistics during renders. It composes the Orchestrator (OBJ-035), manifest loader (OBJ-016), geometry registry (OBJ-005), and camera registry (OBJ-006) into a user-friendly terminal experience. The `package.json` `bin` field points to this module.

## Interface Contract

### Module: `src/cli.ts`

This is the executable entry point. The source file begins with `#!/usr/bin/env node` (preserved by the TypeScript compiler or prepended by the build step). It is not designed for programmatic import — it runs `program.parse(process.argv)` at module scope, wrapped in a top-level error handler.

**Entry point structure:**

```typescript
#!/usr/bin/env node

/**
 * Creates and configures the Commander program instance.
 * Exported for testing — allows invoking CLI commands programmatically
 * without spawning a child process.
 *
 * The returned program has exitOverride() enabled. Instead of calling
 * process.exit(), Commander throws a CommanderError with exitCode and
 * message. The src/cli.ts entry-point code catches CommanderError and
 * calls process.exit(error.exitCode). This separation ensures
 * createProgram() is safe for programmatic invocation in tests.
 *
 * @returns Configured Commander.Command instance with all commands registered.
 */
export function createProgram(): Command;
```

**Version source:** The program version is read from `package.json` at module load time. The implementation resolves the `package.json` path relative to `__dirname` (or `import.meta.url` for ESM), reads it with `readFileSync`, parses it, and extracts the `version` field. This value is passed to Commander's `.version()` method.

### Shared Global Options

These options are available on every command:

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--verbose` | `-v` | boolean | `false` | Enable verbose output (timing stats, per-scene details, renderer info). |
| `--debug` | | boolean | `false` | Enable debug output (forwards headless Chromium console logs to stderr, enables `OrchestratorConfig.debug`). Implies `--verbose`. |
| `--color` | | boolean | auto-detected | Force color output. Default: auto-detect via `process.stdout.isTTY`. `--no-color` disables. |

### Command: `depthkit render <manifest>`

Renders a manifest to an MP4 file.

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:**

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output` | `-o` | string | `"./output.mp4"` | Output MP4 file path. |
| `--width` | `-W` | number | _(from manifest)_ | Override `composition.width`. |
| `--height` | `-H` | number | _(from manifest)_ | Override `composition.height`. Note: uppercase `-H` to avoid conflict with Commander's reserved `-h` for `--help`. |
| `--fps` | | number | _(from manifest)_ | Override `composition.fps`. |
| `--assets-dir` | `-a` | string | _(manifest's parent directory)_ | Base directory for resolving relative image paths. |
| `--gpu` | | string | `"software"` | GPU mode: `"software"`, `"hardware"`, or `"auto"`. Maps to `OrchestratorConfig.gpu` (boolean) — see D4. |
| `--preset` | | string | `"medium"` | H.264 encoding preset. One of: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`. Maps to `OrchestratorConfig.encodingPreset`. |
| `--crf` | | number | `23` | Constant Rate Factor (0–51). Maps to `OrchestratorConfig.crf`. |
| `--ffmpeg-path` | | string | _(auto-resolved)_ | Path to FFmpeg binary. Maps to `OrchestratorConfig.ffmpegPath`. |
| `--chromium-path` | | string | _(bundled)_ | Path to Chromium executable. Maps to `OrchestratorConfig.chromiumPath`. |

**Behavior:**
1. Parse and validate CLI arguments (see D2 for override application).
2. Populate registries via `initRegistries()` (see D3).
3. Load manifest file via `loadManifestFromFile()` (OBJ-016).
4. Apply resolution/fps overrides to the loaded manifest (see D2).
5. Construct `OrchestratorConfig` and create `Orchestrator`.
6. Provide an `onProgress` callback that renders a progress bar to stderr (see D5).
7. Call `orchestrator.render()`.
8. On success: print summary to stdout, exit code 0.
9. On failure: print formatted error to stderr, exit code 1.

**Stdout output on success (non-verbose):**
```
✓ Rendered 1800 frames in 8m 32s → ./output.mp4
  Duration: 60.00s | Resolution: 1920×1080 | FPS: 30
  Avg frame: 284ms | File size: 12.4 MB
```

**Stdout output on success (verbose):**
```
✓ Rendered 1800 frames in 8m 32s → ./output.mp4
  Duration: 60.00s | Resolution: 1920×1080 | FPS: 30
  Avg frame: 284ms | File size: 12.4 MB
  Scenes: 5 | Geometry types: stage, tunnel, diorama
  Capture strategy: viewport-png | Encoding preset: medium | CRF: 23
  WebGL: SwiftShader (software) | WebGL 2.0
  Audio: muxed (narration.mp3)
  Warnings: 0
```

### Command: `depthkit validate <manifest>`

Validates a manifest without rendering. Fast — no browser or FFmpeg launched.

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:** None beyond global options.

**Behavior:**
1. Populate registries via `initRegistries()` (see D3).
2. Load and validate manifest via `loadManifestFromFile()` (OBJ-016).
3. On valid (with or without warnings): print summary to stdout, exit code 0.
4. On invalid: print formatted errors to stderr, exit code 1.

**Stdout on valid:**
```
✓ Manifest valid: 5 scenes, 60.00s total duration
  Geometries: stage (2), tunnel (2), diorama (1)
  Cameras: slow_push_forward (3), tunnel_push_forward (2)
```

If warnings exist:
```
✓ Manifest valid with 2 warning(s): 5 scenes, 60.00s total duration
  ⚠ scenes: Scene array order differs from start_time order (SCENE_ORDER_MISMATCH)
  ⚠ scenes[2].planes.subject: Per-plane opacity is not supported in V1 (UNSUPPORTED_FEATURE)
  Geometries: stage (2), tunnel (2), diorama (1)
  Cameras: slow_push_forward (3), tunnel_push_forward (2)
```

**Stderr on invalid:**
```
✗ Manifest validation failed (3 error(s)):
  ✗ scenes[0].geometry: Unknown geometry "tunl". Available: stage, tunnel, canyon, flyover, diorama, portal, panorama, close_up (UNKNOWN_GEOMETRY)
  ✗ scenes[1].planes: Missing required slot "floor" for geometry "stage" (MISSING_REQUIRED_SLOT)
  ✗ scenes[2].camera: Unknown camera "push_fast". Available: static, slow_push_forward, ... (UNKNOWN_CAMERA)
```

**Assumption:** Validation error messages from OBJ-016 include available options (geometry names, camera names) in their `message` field. The CLI does not need access to registries for error formatting.

### Command: `depthkit preview <manifest>`

Serves the Three.js scene on a local HTTP server for real-time preview in a browser. (Addresses OQ-05 from the seed.)

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:**

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--port` | `-p` | number | `3000` | HTTP server port. |
| `--open` | | boolean | `false` | Automatically open the preview URL in the default browser. |

**Behavior:**
1. Validate the manifest (same as `validate` command).
2. If valid: start an HTTP server that serves the Three.js page with the manifest's scene data, using real-time `requestAnimationFrame` playback.
3. Print the URL to stdout.
4. Keep the process running until the user presses Ctrl+C (SIGINT).

**Scope note:** The preview command's HTTP server and page serving logic is deliberately under-specified. OBJ-046 defines the CLI command signature, argument parsing, manifest validation gate, and lifecycle. The actual preview server implementation is deferred. OBJ-046's implementation uses a dynamic import extension point (see D7) so the preview server can be plugged in later. If the preview server module is not yet available, the command prints an informational message and exits with code 0:

```
ℹ Preview server not yet implemented. Use 'depthkit render' for full rendering.
```

### Module: `src/cli/format.ts` — Output Formatting

Handles all terminal output formatting. Separated from `src/cli.ts` for testability.

```typescript
/**
 * Formats an OrchestratorResult into a human-readable summary string.
 * File size is obtained by the caller via fs.stat() and passed in.
 *
 * @param result - The orchestrator result.
 * @param fileSizeBytes - Output file size in bytes.
 * @param verbose - Whether to include extended details.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string (no trailing newline).
 */
export function formatRenderResult(
  result: OrchestratorResult,
  fileSizeBytes: number,
  verbose: boolean,
  color: boolean,
): string;

/**
 * Formats a successful validation result into a human-readable summary.
 *
 * @param manifest - The validated manifest.
 * @param warnings - Any validation warnings.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatValidationSuccess(
  manifest: Manifest,
  warnings: ManifestError[],
  color: boolean,
): string;

/**
 * Formats validation errors into a human-readable error report.
 *
 * @param errors - All ManifestError objects from validation.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatValidationErrors(
  errors: ManifestError[],
  color: boolean,
): string;

/**
 * Formats an OrchestratorError into a human-readable error message.
 * Includes the error code, message, and context (frame number, validation errors).
 *
 * @param error - The orchestrator error.
 * @param verbose - Whether to include stack trace and cause chain.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatOrchestratorError(
  error: OrchestratorError,
  verbose: boolean,
  color: boolean,
): string;

/**
 * Formats a render progress update for terminal display.
 * Returns a single-line string suitable for overwriting the current line
 * via \r (carriage return).
 *
 * Spinner character cycles based on progress.frame % SPINNER_FRAMES.length
 * using Braille dot characters (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏).
 *
 * Example: "⠸ Rendering [████████░░░░░░░░] 48% | Frame 864/1800 | 3m 12s remaining"
 *
 * @param progress - The RenderProgress data from the orchestrator callback.
 * @param color - Whether to include ANSI color codes.
 * @returns Single-line string (no newline).
 */
export function formatProgress(
  progress: RenderProgress,
  color: boolean,
): string;

/**
 * Formats a file size in bytes into a human-readable string.
 * e.g., 1024 → "1.0 KB", 13042688 → "12.4 MB"
 */
export function formatFileSize(bytes: number): string;

/**
 * Formats a duration in milliseconds into a human-readable string.
 * e.g., 512000 → "8m 32s", 1500 → "1.5s", 45 → "45ms"
 */
export function formatDuration(ms: number): string;
```

### Module: `src/cli/registry-init.ts` — Registry Population

Centralizes registry population so both `render` and `validate` commands use the same registries.

```typescript
import type { ManifestRegistry } from '../manifest/schema.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

/**
 * Registry bundle returned by initRegistries().
 */
export interface RegistryBundle {
  manifestRegistry: ManifestRegistry;
  geometryRegistry: GeometryRegistry;
  cameraRegistry: CameraPathRegistry;
}

/**
 * Populates and returns all three registries needed by the orchestrator.
 *
 * This function is synchronous. All geometry and camera modules are
 * imported statically at the top of registry-init.ts — their
 * registerGeometry() side effects execute at module load time, before
 * this function is called. The function body simply:
 *
 * 1. Calls getGeometryRegistry() (OBJ-005) to retrieve and freeze
 *    the geometry registry.
 * 2. Constructs the CameraPathRegistry by importing the camera
 *    preset barrel module (see D8 for mechanism).
 * 3. Creates a ManifestRegistry via createRegistry() (OBJ-004) and
 *    populates it by iterating the geometry and camera registries,
 *    converting each SceneGeometry → GeometryRegistration and
 *    CameraPathPreset → CameraRegistration.
 * 4. Returns the RegistryBundle.
 *
 * Must be called once at startup. Subsequent calls return the same
 * registries (because OBJ-005's registry locks on first read).
 *
 * @returns RegistryBundle with all registries populated.
 */
export function initRegistries(): RegistryBundle;
```

## Design Decisions

### D1: Commander as CLI Framework

**Decision:** Use `commander` (npm) for argument parsing and command routing.

**Rationale:** Commander is MIT-licensed, the most widely adopted Node.js CLI framework, and is already permitted by C-01 ("Standard npm utilities... are allowed"). It provides subcommand support, automatic `--help` generation, option type coercion, and default values.

### D2: Resolution/FPS Overrides Are Applied Post-Validation

**Decision:** CLI `--width`, `--height`, and `--fps` overrides are applied to the manifest object **after** Phase 1 (structural) and Phase 2 (semantic) validation, but **before** constructing the Orchestrator. The overrides mutate the `Manifest.composition` fields directly.

**Rationale:** The manifest on disk is the source of truth. Overrides are a convenience for testing different resolutions without editing the file. Applying overrides after validation ensures the base manifest is valid. The overridden values do not need re-validation because:
- Width/height: any positive integer is valid per OBJ-004's `CompositionSchema`.
- FPS: any integer in [1, 120] is valid per OBJ-004's `CompositionSchema`.

**Guard:** The CLI validates override values before applying: width and height must be positive integers; fps must be an integer in [1, 120]. Invalid CLI overrides produce an error message and exit code 1 before any manifest loading.

### D3: Registry Population is Centralized and Synchronous

**Decision:** A single synchronous `initRegistries()` function in `src/cli/registry-init.ts` returns a `RegistryBundle` containing all three registries. All geometry and camera modules are **statically imported** at the top of `registry-init.ts` — their `registerGeometry()` side effects execute at module load time. The function body only calls `getGeometryRegistry()`, assembles the camera registry, iterates both to build the `ManifestRegistry`, and returns.

**Rationale:** Both `render` and `validate` commands need the same registries. All geometry and camera modules are known at build time — dynamic imports add async complexity for no benefit. Static imports ensure all side-effect registrations are complete before `initRegistries()` is called.

**Key detail:** The `ManifestRegistry` (OBJ-004) stores validation-only metadata, while the spatial registries store full 3D data. `initRegistries()` converts between them:
- `SceneGeometry` → `GeometryRegistration`: extract `name`, `slots` (convert `PlaneSlot` → `PlaneSlotDef` by keeping only `required` and `description`), `compatibleCameras` (from `compatible_cameras`), `defaultCamera` (from `default_camera`).
- `CameraPathPreset` → `CameraRegistration`: extract `name`, `compatibleGeometries`, `supportsFovAnimation` (derived from `oversizeRequirements.fovRange[0] !== oversizeRequirements.fovRange[1]`).

### D4: GPU Mode Mapping

**Decision:** The CLI `--gpu` flag accepts `"software"`, `"hardware"`, or `"auto"` (string). This maps to `OrchestratorConfig.gpu` (boolean):
- `"software"` → `gpu: false`
- `"hardware"` → `gpu: true`
- `"auto"` → `gpu: false` (V1 simplification)

**Rationale:** OBJ-035's `OrchestratorConfig.gpu` is a simple boolean. OBJ-049 defines a richer `GpuMode` type but that integration is between OBJ-049 and OBJ-035. For V1, the CLI maps to the boolean. The `--gpu` flag is a string (not boolean) to preserve forward compatibility.

### D5: Progress Reporting via stderr

**Decision:** The `onProgress` callback writes progress updates to stderr using carriage return (`\r`) line overwriting. When stderr is not a TTY (piped to a file or another process), progress is suppressed entirely.

**Rationale:**
- **stderr, not stdout:** Stdout is reserved for the final result summary. This allows `depthkit render manifest.json > result.txt` to capture only the summary.
- **Carriage return overwriting:** Standard CLI progress bar pattern. After completion, a final newline is written so the success message appears on a fresh line.
- **TTY detection:** Piped stderr should not contain ANSI escape codes or carriage-return progress spam.

### D6: Exit Codes

**Decision:**
| Exit Code | Meaning |
|---|---|
| `0` | Success (render complete, manifest valid, preview started). |
| `1` | Failure (validation error, render error, invalid arguments). |
| `2` | Usage error (unknown command, missing required argument). Commander handles this by default. |

### D7: Preview Command Stub with Dynamic Import Extension Point

**Decision:** The `preview` command validates the manifest and then attempts to dynamically import a preview server module (`../preview/server.js`). If the import fails (module doesn't exist yet), it prints an informational message and exits with code 0.

**Rationale:** The preview server is outside OBJ-046's scope but the CLI command should be registered now so the `--help` output is complete. Dynamic import keeps the dependency optional — no build errors if the preview module doesn't exist.

### D8: Camera Registry Population Mechanism

**Decision:** OBJ-006 defines `CameraPathRegistry` as `Readonly<Record<string, CameraPathPreset>>` but does not define a mutable registry with `register()` / `getCameraPathRegistry()` functions analogous to OBJ-005's pattern. The `registry-init.ts` module constructs the `CameraPathRegistry` by:

1. Statically importing a **barrel module** at `src/camera/presets/index.ts` that re-exports all camera preset objects from OBJ-026 through OBJ-034. Each preset module exports a `CameraPathPreset` object as its default or named export.
2. Assembling these into a `Record<string, CameraPathPreset>` keyed by `preset.name`.
3. Freezing the record to produce a `CameraPathRegistry`.

**If the barrel module pattern is not used by the camera preset implementations**, `registry-init.ts` instead imports each camera preset module individually (e.g., `import { staticPreset } from '../camera/presets/static.js'`) and assembles them manually.

**Rationale:** OBJ-006's registry type is a plain frozen Record, not a stateful registry. The assembly must happen somewhere — `registry-init.ts` is the natural place since it's already responsible for bridging between spatial registries and the `ManifestRegistry`. The exact import mechanism depends on how OBJ-026–034 export their presets, but the contract is: `registry-init.ts` must produce a `CameraPathRegistry` containing all registered camera presets.

### D9: Assets Dir Default

**Decision:** If `--assets-dir` is not provided, the default is the **parent directory of the manifest file**, not `process.cwd()`. This matches the common pattern where images sit alongside or relative to the manifest.

**Rationale:** OBJ-035's default `assetsDir` is `process.cwd()`, which is appropriate for the programmatic API. For CLI usage, the manifest's directory is more intuitive — a user running `depthkit render ./projects/video1/manifest.json` expects image paths in the manifest to resolve relative to `./projects/video1/`, not the current directory.

### D10: SIGINT Handling

**Decision:** During rendering, SIGINT (Ctrl+C) is caught and converted to a cancellation request. The `onProgress` callback checks a flag and returns `false` to trigger the orchestrator's graceful shutdown. A second SIGINT force-kills the process via `process.exit(1)`.

**Rationale:** Graceful shutdown ensures FFmpeg is properly terminated and partial files are cleaned up, per OBJ-035's cleanup guarantees. The second-SIGINT escape hatch prevents the process from becoming unkillable if cleanup hangs.

### D11: No Color Dependency

**Decision:** ANSI color codes are generated using inline escape sequences, not a color library. A minimal color utility (6-8 functions: `red`, `green`, `yellow`, `cyan`, `bold`, `dim`, `reset`) is implemented in `src/cli/colors.ts`.

**Rationale:** Minimizes dependencies. The CLI needs only basic colors. The `--color` / `--no-color` flag and TTY detection control whether escape codes are emitted.

### D12: File Size in Summary

**Decision:** The render summary includes the output file size. This requires a `fs.stat()` call on the output MP4 after `render()` completes. The file size is passed to `formatRenderResult()` as a separate parameter (not derived from `OrchestratorResult`).

### D13: Commander exitOverride for Testability

**Decision:** `createProgram()` calls Commander's `exitOverride()` on the returned program. Instead of calling `process.exit()`, Commander throws a `CommanderError` with `exitCode` and `message` properties. The `src/cli.ts` entry-point code (the non-exported part that calls `program.parse(process.argv)`) wraps the parse call in a try/catch that catches `CommanderError` and calls `process.exit(error.exitCode)`.

**Rationale:** Without `exitOverride()`, Commander calls `process.exit()` on missing arguments, unknown commands, and `--help`/`--version`. This kills the test runner when tests invoke `createProgram().parseAsync()`. With `exitOverride()`, tests can catch `CommanderError` and assert on its `exitCode` and `message`.

## Acceptance Criteria

### Argument Parsing

- [ ] **AC-01:** `depthkit render manifest.json` renders the manifest to `./output.mp4` (default output path).
- [ ] **AC-02:** `depthkit render manifest.json -o video.mp4` renders to the specified output path.
- [ ] **AC-03:** `depthkit render manifest.json -W 1080 -H 1920 --fps 24` overrides the manifest's composition settings. The output video is 1080×1920 at 24fps.
- [ ] **AC-04:** `depthkit render` with no manifest argument prints a usage error and exits with code 2.
- [ ] **AC-05:** `depthkit render manifest.json --gpu hardware --preset slow --crf 18` passes the correct values to the orchestrator.
- [ ] **AC-06:** `depthkit --help` prints help with all three commands listed. `depthkit render --help` prints render-specific options including `-W` and `-H`.
- [ ] **AC-07:** `depthkit --version` prints the version string read from `package.json`.

### Validate Command

- [ ] **AC-08:** `depthkit validate manifest.json` with a valid manifest prints a success summary and exits with code 0. No browser or FFmpeg process is launched.
- [ ] **AC-09:** `depthkit validate manifest.json` with an invalid manifest prints all errors to stderr and exits with code 1.
- [ ] **AC-10:** `depthkit validate manifest.json` with a valid manifest that has warnings prints both the success summary and the warnings, and exits with code 0.

### Render Command — Success Path

- [ ] **AC-11:** A successful render prints a summary to stdout including frame count, duration, resolution, fps, average frame time, and file size.
- [ ] **AC-12:** With `--verbose`, the summary additionally includes scene count, geometry types used, capture strategy, encoding preset, CRF, WebGL renderer info, audio status, and warning count.
- [ ] **AC-13:** During rendering, a progress bar updates on stderr showing spinner, percentage, current/total frames, and estimated remaining time. The progress bar is suppressed when stderr is not a TTY.

### Render Command — Error Path

- [ ] **AC-14:** A `MANIFEST_INVALID` orchestrator error prints all validation errors to stderr in the same format as the `validate` command, and exits with code 1.
- [ ] **AC-15:** A non-validation orchestrator error (e.g., `ENCODE_FAILED`) prints the error code, message, and (if `--verbose`) the cause chain to stderr, and exits with code 1.
- [ ] **AC-16:** Invalid CLI argument values (e.g., `--fps -5`, `--crf 60`, `--gpu banana`) print a descriptive error and exit with code 1, before any manifest loading.
- [ ] **AC-17:** A non-existent manifest file path prints `"Manifest file not found: <path>"` and exits with code 1.

### Preview Command

- [ ] **AC-18:** `depthkit preview manifest.json` validates the manifest. If valid, attempts to start the preview server. If the preview server module is not available, prints an informational message and exits with code 0.
- [ ] **AC-19:** `depthkit preview invalid-manifest.json` prints validation errors and exits with code 1 (same as `validate`).

### SIGINT Handling

- [ ] **AC-20:** Pressing Ctrl+C during a render triggers graceful cancellation. The orchestrator's `CANCELLED` error is caught, partial files are cleaned up (per OBJ-035), and the process exits with code 1 and message `"Render cancelled."`.
- [ ] **AC-21:** Pressing Ctrl+C twice force-kills the process immediately.

### Output Formatting

- [ ] **AC-22:** All stderr error output uses red coloring (when color is enabled). Success uses green. Warnings use yellow.
- [ ] **AC-23:** `--no-color` suppresses all ANSI escape codes in both stdout and stderr output.
- [ ] **AC-24:** Progress bar format includes a spinner (Braille dot characters cycling based on frame number), visual bar, percentage, frame counter, and ETA.

### Assets Dir

- [ ] **AC-25:** When `--assets-dir` is not specified, relative image paths in the manifest are resolved against the manifest file's parent directory.
- [ ] **AC-26:** When `--assets-dir /custom/path` is specified, relative image paths resolve against `/custom/path`.

### Registry Initialization

- [ ] **AC-27:** Both `render` and `validate` commands use the same registry population logic. A geometry or camera available to `validate` is also available to `render`.
- [ ] **AC-28:** If no geometries are registered (empty registry), `validate` reports `UNKNOWN_GEOMETRY` for every scene — it does not crash.

### Debug Mode

- [ ] **AC-29:** `depthkit render manifest.json --debug` produces verbose output (same as `--verbose`) plus headless browser console messages on stderr.

### Testability

- [ ] **AC-30:** `createProgram()` returns a Commander program with `exitOverride()` enabled. Programmatic invocation via `createProgram().parseAsync([...])` does not call `process.exit()` — it throws `CommanderError` instead.

## Edge Cases and Error Handling

### CLI Argument Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `--width 0` or `--width -1` | Error: "Width must be a positive integer." Exit code 1. |
| `--fps 0` or `--fps 200` | Error: "FPS must be an integer between 1 and 120." Exit code 1. |
| `--crf -1` or `--crf 52` | Error: "CRF must be between 0 and 51." Exit code 1. |
| `--gpu invalid` | Error: "GPU mode must be one of: software, hardware, auto." Exit code 1. |
| `--preset invalid` | Error: "Encoding preset must be one of: ultrafast, superfast, ..." Exit code 1. |
| `--output` pointing to a read-only directory | FFmpeg fails → `ENCODE_FAILED`. Orchestrator error formatted and printed. Exit code 1. |
| Manifest path is a directory, not a file | `loadManifestFromFile()` returns `FILE_READ_ERROR`. Formatted and printed. Exit code 1. |
| Manifest file is valid JSON but not a valid manifest | Validation errors listed. Exit code 1. |
| Manifest file is not valid JSON | `INVALID_JSON` error. Exit code 1. |
| `-W` without `-H` (or vice versa) | Allowed. Only the specified dimension is overridden; the other comes from the manifest. |
| `-h` flag | Commander treats this as `--help`, not `--height`. This is correct — `--height` uses `-H`. |

### Runtime Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Render succeeds but output file is 0 bytes | Summary prints "0 B" for file size. No special handling. |
| Very long render (>1 hour) | Duration formats as "1h 12m 45s". Progress bar ETA formats similarly. |
| Very short render (<1 second) | Duration formats as "0.8s" or "845ms". |
| SIGINT during validation (before render starts) | Process exits immediately (validation is synchronous and fast). |
| SIGINT during audio mux phase | Orchestrator handles cleanup per OBJ-035. CLI catches the `CANCELLED` error. |
| Orchestrator throws an unexpected non-OrchestratorError | Caught by a top-level handler. Prints "Unexpected error: <message>". If `--verbose`, includes stack trace. Exit code 1. |
| Multiple `-W` flags (e.g., `-W 1080 -W 720`) | Commander takes the last value. Standard behavior. |

### Output Formatting Edge Cases

| Scenario | Expected Behavior |
|---|---|
| No audio in manifest | Summary omits the "Audio: ..." line (non-verbose) or shows "Audio: none" (verbose). |
| 0 warnings | Verbose summary shows "Warnings: 0". Non-verbose omits. |
| 50+ validation errors | All errors are printed. No truncation. |
| Very long file paths in error messages | Not truncated. Terminal wrapping handles it. |
| Unicode in manifest file paths | Handled natively by Node.js fs module. No special treatment. |

## Test Strategy

### Unit Tests: `test/unit/cli/format.test.ts`

1. **formatRenderResult — non-verbose:** Given an `OrchestratorResult` with known values, verify the output matches the expected format with frame count, duration, resolution, fps, avg frame time, and file size.

2. **formatRenderResult — verbose:** Same result, verify extended output includes scene count, geometry types, WebGL info, audio status, warnings.

3. **formatRenderResult — no audio:** Verify the "Audio" line is omitted (non-verbose) or shows "none" (verbose) when `audioResult` is null.

4. **formatValidationSuccess — no warnings:** Verify output includes scene count, total duration, geometry summary, camera summary.

5. **formatValidationSuccess — with warnings:** Verify warnings are listed with `⚠` prefix and error codes.

6. **formatValidationErrors:** Given 3 `ManifestError` objects, verify each is formatted with `✗`, path, message, and code.

7. **formatOrchestratorError — MANIFEST_INVALID:** Verify validation errors are listed.

8. **formatOrchestratorError — ENCODE_FAILED, verbose:** Verify cause chain is included.

9. **formatProgress:** Given progress at 48%, verify the single-line output contains a spinner, bar, percentage, frame counter, and ETA.

10. **formatProgress — 0%:** First frame. ETA shows "calculating...".

11. **formatProgress — 100%:** Last frame. ETA shows "0s".

12. **formatFileSize:** Test bytes, KB, MB, GB boundaries.

13. **formatDuration:** Test ms, seconds, minutes, hours boundaries.

14. **Color disabled:** All format functions with `color: false` produce strings with no ANSI escape sequences.

### Unit Tests: `test/unit/cli/registry-init.test.ts`

15. **initRegistries returns populated bundle:** Verify `manifestRegistry.geometries.size > 0`, `manifestRegistry.cameras.size > 0`, and both spatial registries are non-empty.

16. **Geometry conversion:** Verify a `SceneGeometry` is correctly converted to `GeometryRegistration` — `required` and `description` are preserved, spatial data (position, rotation, size) is not present in the `GeometryRegistration`.

17. **Camera conversion:** Verify a `CameraPathPreset` is correctly converted to `CameraRegistration` — `supportsFovAnimation` is true when `fovRange[0] !== fovRange[1]`.

18. **Idempotent:** Calling `initRegistries()` twice returns equivalent registries (same keys, same values).

### Integration Tests: `test/integration/cli.test.ts`

These use `createProgram().parseAsync()` for speed, or spawn the CLI as a child process where needed.

19. **render — success:** Create a minimal valid manifest with a test geometry and a solid-color test image. Run `depthkit render manifest.json -o output.mp4`. Verify exit code 0, stdout contains "Rendered", output file exists.

20. **render — invalid manifest:** Run `depthkit render broken.json`. Verify exit code 1, stderr contains error code.

21. **render — missing file:** Run `depthkit render nonexistent.json`. Verify exit code 1, stderr contains "not found".

22. **validate — valid:** Run `depthkit validate manifest.json`. Verify exit code 0, stdout contains "valid".

23. **validate — invalid:** Run `depthkit validate broken.json`. Verify exit code 1, stderr contains errors.

24. **validate — warnings:** Run `depthkit validate manifest-with-warnings.json`. Verify exit code 0, stdout contains both success and warning messages.

25. **render — resolution override:** Run with `-W 320 -H 240 --fps 10`. Verify output MP4 is 320×240 via ffprobe.

26. **render — assets-dir:** Create a manifest with `./images/bg.png`, images in a separate directory. Run with `--assets-dir <dir>`. Verify render succeeds.

27. **render — default assets-dir:** Run without `--assets-dir`. Verify images are resolved relative to the manifest's parent directory.

28. **help output:** Run `depthkit --help`. Verify output lists `render`, `validate`, `preview` commands.

29. **version output:** Run `depthkit --version`. Verify it prints a semver string.

30. **invalid arguments:** Run `depthkit render manifest.json --fps -5`. Verify exit code 1, stderr contains "FPS must be".

31. **no-color:** Run `depthkit render manifest.json --no-color`. Verify stdout/stderr contain no ANSI escape codes (`\x1b[` not present).

32. **preview — stub:** Run `depthkit preview manifest.json`. If preview module is absent, verify exit code 0 and informational message.

33. **debug mode:** Run `depthkit render manifest.json --debug`. Verify verbose output is present (debug implies verbose).

34. **createProgram exitOverride:** Call `createProgram().parseAsync(['render'])` with no manifest. Verify `CommanderError` is thrown (not `process.exit()`), with `exitCode` of 2.

### Relevant Testable Claims

- **TC-04:** Tests 19, 22 verify that the CLI (using geometry names and slot keys) produces correct output.
- **TC-07:** Tests 20, 23 verify manifest validation catches errors via the CLI path.
- **TC-11:** All integration tests can run with default `--gpu software` (software WebGL).

## Integration Points

### Depends on

| Dependency | What OBJ-046 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`, `OrchestratorErrorCode`, `RenderProgress`, `renderFromFile()`. |
| **OBJ-004** (Manifest Schema) | `Manifest`, `ManifestError`, `ManifestRegistry`, `createRegistry()`, `GeometryRegistration`, `CameraRegistration`, `PlaneSlotDef`. |
| **OBJ-016** (Manifest Loader) | `loadManifestFromFile()`, `loadManifest()`, `computeTotalDuration()`. |
| **OBJ-005** (Geometry Registry) | `GeometryRegistry`, `SceneGeometry`, `getGeometryRegistry()`, `registerGeometry()`. Imported transitively by `registry-init.ts`. |
| **OBJ-006** (Camera Registry) | `CameraPathRegistry`, `CameraPathPreset`. The camera registry type and `getCameraPath()` function. |
| **OBJ-018–025** (Individual Geometries) | Imported statically by `registry-init.ts` for their `registerGeometry()` side effects. |
| **OBJ-026–034** (Individual Camera Presets) | Imported statically by `registry-init.ts` to assemble the `CameraPathRegistry`. |

### Consumed by

| Downstream | How it uses OBJ-046 |
|---|---|
| **OBJ-050** (Preview Server Integration) | The preview command stub will be connected to the actual preview server when OBJ-050 is implemented. |
| **OBJ-070** (SKILL.md) | Documents CLI usage, command syntax, and examples for LLM authors and human operators. |
| **OBJ-075** (n8n HTTP Interface) | May invoke the CLI as a subprocess, or may use the programmatic API directly (via `Orchestrator`). The CLI provides a tested, validated entry path. |
| **OBJ-077** (End-to-End Integration) | Uses the CLI or `createProgram()` to run full pipeline tests. |

### File Placement

```
depthkit/
  src/
    cli.ts                      # NEW — Main CLI entry point (#!/usr/bin/env node),
                                #       Commander setup, command handlers, createProgram()
    cli/
      format.ts                 # NEW — Output formatting (render result, validation,
                                #       progress, errors)
      colors.ts                 # NEW — Minimal ANSI color utilities (red, green, yellow,
                                #       cyan, bold, dim; gated by color flag)
      registry-init.ts          # NEW — Registry population bridge (static imports of
                                #       all geometry + camera modules, registry assembly)
  test/
    unit/
      cli/
        format.test.ts          # NEW — Format function unit tests
        registry-init.test.ts   # NEW — Registry initialization unit tests
    integration/
      cli.test.ts               # NEW — CLI integration tests
```

The `package.json` `bin` field:
```json
{
  "bin": {
    "depthkit": "./dist/cli.js"
  }
}
```

The compiled `dist/cli.js` must begin with `#!/usr/bin/env node`. This is typically ensured by including the shebang as the first line in `src/cli.ts` (TypeScript preserves leading comments when `removeComments` is false, or a build step prepends it).

## Open Questions

### OQ-A: Should the CLI support `--quiet` mode?

A `--quiet` flag that suppresses all output except errors could be useful for scripted pipelines. Not specified for V1.

### OQ-B: Should `validate` check image file existence?

Currently `validate` runs OBJ-016's two-phase validation, which does not check whether image files exist on disk. Adding a `--check-assets` flag would require extracting the image path resolution logic from the orchestrator into a shared utility.

### OQ-C: Should the render command support `--dry-run`?

A `--dry-run` that validates and computes frame count without rendering. Strictly a superset of `validate` with additional computation.

### OQ-D: Should progress be emitted as JSON for machine consumption?

A `--json` flag emitting newline-delimited JSON progress. Deferred — OBJ-075 may use the programmatic API.

### OQ-E: Should the CLI read environment variables for defaults?

E.g., `DEPTHKIT_FFMPEG_PATH`, `DEPTHKIT_GPU_MODE`. Commander supports `.env()` on options. Low priority.

### OQ-F: CameraParams.offset discrepancy between OBJ-004 and OBJ-006

OBJ-004's `CameraParamsSchema` does not include an `offset` field, while OBJ-006's `CameraParams` type does. This is a cross-objective discrepancy not caused by OBJ-046. The CLI passes through whatever the manifest contains — if `offset` is present in the JSON, Zod's behavior depends on whether `CameraParamsSchema` uses `.strict()` or `.passthrough()`. This should be resolved between OBJ-004 and OBJ-006 directly.

---

I believe all 8 issues from the challenger's review are now addressed:

1. **`-h` conflict** → Changed to `-H` for height and `-W` for width. Updated AC-03, AC-06, edge cases table, and test 25.
2. **`initRegistries()` sync/async** → Explicitly specified as synchronous with static imports (D3 rewritten).
3. **`createProgram()` exitOverride** → Added D13, updated `createProgram()` doc, added AC-30, added test 34.
4. **Camera registry population** → Added D8 with explicit barrel module assembly mechanism.
5. **Shebang** → Added to file placement section and interface contract preamble.
6. **Version source** → Added explicit mechanism in the interface contract section.
7. **Spinner state** → Updated `formatProgress` doc to specify Braille dots cycling via `frame % length`.
8. **Missing AC for `--debug`** → Added AC-29 and test 33.

I ask the Challenger to verify and approve.

---

## Round 4 — spec_challenger

I've verified all 8 issues from Round 2 against the revised spec:

| # | Issue | Verified Fix |
|---|---|---|
| 1 | `-h` conflicts with `--help` | ✓ Changed to `-H`/`-W`. Updated in options table, AC-03 (`-W 1080 -H 1920`), AC-06, edge cases table (`-h` → `--help` row added). |
| 2 | `initRegistries()` sync/async | ✓ D3 explicitly states "synchronous" with "statically imported at the top." Function signature remains `(): RegistryBundle`. |
| 3 | `createProgram()` exitOverride | ✓ D13 added. `createProgram()` JSDoc updated. AC-30 added. Test 34 added. |
| 4 | Camera registry population | ✓ D8 added with barrel module pattern and fallback to individual imports. |
| 5 | Shebang | ✓ Added to interface contract preamble and file placement section. |
| 6 | Version source | ✓ Explicit mechanism in interface contract: `readFileSync` + `JSON.parse` relative to `__dirname`. |
| 7 | Spinner state | ✓ `formatProgress` doc now specifies "Braille dot characters cycling based on `progress.frame % SPINNER_FRAMES.length`". |
| 8 | Missing AC for `--debug` | ✓ AC-29 added. Test 33 added. |

No new issues introduced by the revisions. The spec is implementable.

One minor note for meta.json: `depends_on` lists only `["OBJ-035"]` but `registry-init.ts` directly imports from OBJ-004, OBJ-005, OBJ-006, and OBJ-018–034. This is acceptable because OBJ-035 transitively depends on all of them, and the spec's Integration Points table correctly documents all direct imports. I'll preserve the existing `depends_on` since it was set by the initializer and reflects the DAG structure.

CONCLUSION:

The spec for OBJ-046 (CLI Interface) is complete and ready for implementation. It defines:

- **Three commands** (`render`, `validate`, `preview`) with Commander, MIT-licensed per C-01
- **Argument parsing** with `-W`/`-H` short flags (avoiding `-h` conflict), resolution/fps overrides applied post-validation
- **Registry population** via synchronous `initRegistries()` with static imports, bridging OBJ-005/OBJ-006 spatial registries to OBJ-004's ManifestRegistry
- **Progress reporting** on stderr with TTY detection, spinner via Braille dots cycling on frame number
- **Output formatting** in a separate testable module (`src/cli/format.ts`)
- **SIGINT handling** with two-stage interrupt (graceful then force-kill)
- **Testability** via `createProgram()` with Commander's `exitOverride()`
- **30 acceptance criteria** and **34 tests** covering argument parsing, validation, rendering, error paths, formatting, and edge cases
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "content": "# Specification: OBJ-046 \u2014 CLI Interface\n\n## Summary\n\nOBJ-046 delivers the Commander-based CLI for depthkit (`src/cli.ts`) \u2014 the primary human-facing entry point for rendering, validating, and previewing manifests. It exposes three commands (`render`, `validate`, `preview`), handles argument parsing for manifest paths, output paths, resolution/fps overrides, GPU mode, encoding presets, verbose/debug output, and provides structured progress reporting and timing statistics during renders. It composes the Orchestrator (OBJ-035), manifest loader (OBJ-016), geometry registry (OBJ-005), and camera registry (OBJ-006) into a user-friendly terminal experience. The `package.json` `bin` field points to this module.\n\n## Interface Contract\n\n### Module: `src/cli.ts`\n\nThis is the executable entry point. The source file begins with `#!/usr/bin/env node` (preserved by the TypeScript compiler or prepended by the build step). It is not designed for programmatic import \u2014 it runs `program.parse(process.argv)` at module scope, wrapped in a top-level error handler.\n\n**Entry point structure:**\n\n```typescript\n#!/usr/bin/env node\n\n/**\n * Creates and configures the Commander program instance.\n * Exported for testing \u2014 allows invoking CLI commands programmatically\n * without spawning a child process.\n *\n * The returned program has exitOverride() enabled. Instead of calling\n * process.exit(), Commander throws a CommanderError with exitCode and\n * message. The src/cli.ts entry-point code catches CommanderError and\n * calls process.exit(error.exitCode). This separation ensures\n * createProgram() is safe for programmatic invocation in tests.\n *\n * @returns Configured Commander.Command instance with all commands registered.\n */\nexport function createProgram(): Command;\n```\n\n**Version source:** The program version is read 
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md
Now update meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-046",
     3→  "description": "CLI interface -- Commander-based CLI with render, validate, and preview commands. Argument parsing for manifest path, output path, resolution overrides, fps overrides, verbose/debug mode. Output options (progress reporting, timing stats). Entry point at src/cli.ts.",
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/meta.json",
  "content": "{\n  \"id\": \"OBJ-046\",\n  \"description\": \"CLI interface -- Commander-based CLI with render, validate, and preview commands. Argument parsing for manifest path, output path, resolution overrides, fps overrides, verbose/debug mode. Output options (progress reporting, timing stats). Entry point at src/cli.ts.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"spec_deliberation\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:00:00Z\",\n  \"depends_on\": [\"OBJ-035\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 4 interface. Spec complete. Three commands: render, validate, preview (stub). Uses Commander with exitOverride for testability. Registry population centralized in src/cli/registry-init.ts (synchronous, static imports). Short flags: -W for width, -H for height (avoiding -h conflict with --help). Progress on stderr, results on stdout. SIGINT two-stage: graceful then force-kill.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/meta.json has been updated successfully.
Now commit:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-046/output.md nodes/OBJ-046/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-046): CLI interface specification \u2014 render, validate, preview commands\n\nDefines Commander-based CLI with three commands, argument parsing,\nprogress reporting, output formatting, and registry initialization.\nKey decisions: -W/-H short flags (avoiding -h/--help conflict),\nsynchronous registry population via static imports, exitOverride\nfor testability, two-stage SIGINT handling, progress on stderr.\n30 acceptance criteria, 34 tests specified.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-046 spec files"
}
[Tool Result] [master 37cb4b1] spec(OBJ-046): CLI interface specification — render, validate, preview commands
 2 files changed, 678 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-046/output.md
The specification for OBJ-046 has been written to `nodes/OBJ-046/output.md`, `meta.json` updated, and committed. The spec is complete and ready for implementation.
