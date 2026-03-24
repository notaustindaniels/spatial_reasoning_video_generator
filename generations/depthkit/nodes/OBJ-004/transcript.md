# Deliberation Transcript: OBJ-004

---

## Round 1 — spec_author

I'll review the seed document, dependency specs, and constraints to craft the OBJ-004 specification. Let me first check any existing files in the project.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]


Let me check the existing project structure and any relevant files.
[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/manifest/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-004/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-001/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-001/output.md

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/manifest/**"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/manifest/**"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-004",
     3→  "description": "Manifest schema core -- Zod schema for the top-level manifest structure: composition settings (width, height, fps, audio), scenes array (id, duration, start_time, geometry, camera, camera_params, transition_in, transition_out, planes), and global metadata per Section 4.6. Covers C-04 (resolution/fps support for 1920x1080, 1080x1920, 24fps, 30fps) and C-10 (validation before rendering). Defines the contract between LLM manifest authors and the rendering engine.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. The most critical contract -- defines the authoring interface."
    12→}
    13→
Now I have sufficient context. Let me propose the complete specification for OBJ-004.

---

# Proposed Specification: OBJ-004 — Manifest Schema Core

## Summary

OBJ-004 defines the Zod validation schema and loader for the depthkit manifest — the declarative JSON document that describes an entire video. This is the authoring contract between LLM manifest authors and the rendering engine. The schema enforces structural correctness (types, ranges, required fields) via Zod parsing and semantic correctness (geometry existence, camera compatibility, plane-slot matching) via a registry-backed validation pass. It satisfies C-04 (resolution/fps support) and C-10 (validate before rendering, fail fast with actionable errors).

## Interface Contract

### Module: `src/manifest/schema.ts`

This module exports the Zod schemas and their inferred TypeScript types. It also exports the geometry and camera registry interfaces, so that downstream objectives (OBJ-005, OBJ-006, OBJ-018–025, OBJ-026–034) can register their definitions without modifying this module.

```typescript
// === Registry Interfaces ===

/**
 * Describes a single plane slot within a scene geometry.
 * Populated by OBJ-005 (geometry base) and OBJ-018–025 (individual geometries).
 */
export interface PlaneSlotDef {
  required: boolean;
  description: string;
}

/**
 * A registered scene geometry definition. Contains enough metadata
 * for manifest validation (slot names, compatible cameras).
 * Does NOT contain 3D spatial data (positions, rotations) — that
 * lives in OBJ-005's geometry implementations.
 */
export interface GeometryRegistration {
  name: string;
  slots: Record<string, PlaneSlotDef>;
  compatibleCameras: string[];
  defaultCamera: string;
}

/**
 * A registered camera path definition. Contains enough metadata
 * for manifest validation (compatible geometries).
 */
export interface CameraRegistration {
  name: string;
  compatibleGeometries: string[];  // Empty array = compatible with all
  supportsFovAnimation: boolean;
}

/**
 * The mutable registry that geometry and camera objectives populate.
 * The manifest loader queries this during semantic validation.
 */
export interface ManifestRegistry {
  geometries: Map<string, GeometryRegistration>;
  cameras: Map<string, CameraRegistration>;

  registerGeometry(def: GeometryRegistration): void;
  registerCamera(def: CameraRegistration): void;
}

/**
 * Factory function — creates a fresh, empty registry.
 */
export function createRegistry(): ManifestRegistry;

// === Zod Schemas ===

// All Zod schemas below are exported as named constants.
// Their inferred types are exported as type aliases.

/** Audio configuration */
export const AudioSchema: z.ZodType;  // see shape below
export type Audio = z.infer<typeof AudioSchema>;

/** Composition (global video settings) */
export const CompositionSchema: z.ZodType;
export type Composition = z.infer<typeof CompositionSchema>;

/** Transition preset */
export const TransitionSchema: z.ZodType;
export type Transition = z.infer<typeof TransitionSchema>;

/** Camera parameters (per-scene overrides) */
export const CameraParamsSchema: z.ZodType;
export type CameraParams = z.infer<typeof CameraParamsSchema>;

/** Plane reference (image source + optional overrides) */
export const PlaneRefSchema: z.ZodType;
export type PlaneRef = z.infer<typeof PlaneRefSchema>;

/** A single scene */
export const SceneSchema: z.ZodType;
export type Scene = z.infer<typeof SceneSchema>;

/** Top-level manifest */
export const ManifestSchema: z.ZodType;
export type Manifest = z.infer<typeof ManifestSchema>;
```

#### Zod Schema Shapes

**AudioSchema:**
```typescript
{
  src: z.string().min(1),                           // Path to audio file
  volume: z.number().min(0).max(2).default(1.0),    // 0 = mute, 1 = normal, 2 = max boost
}
```

**CompositionSchema:**
```typescript
{
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  fps: z.number().positive(),
  audio: AudioSchema.optional(),
}
```
Note: C-04 requires support for 1920×1080, 1080×1920, 24fps, 30fps — but the schema does NOT restrict to only those values. It accepts any positive integer dimensions and any positive fps. The constraint is that those four combinations *must work*; others may also work. This avoids artificially limiting the engine.

**TransitionSchema:**
```typescript
{
  type: z.enum(["cut", "crossfade", "dip_to_black"]),
  duration: z.number().nonnegative(),   // seconds; 0 is valid for "cut"
}
```
Refinement: if `type === "cut"`, `duration` must be 0 (or is ignored). If `type !== "cut"`, `duration` must be > 0. Enforced via `.superRefine()`.

**CameraParamsSchema:**
```typescript
{
  speed: z.number().positive().default(1.0),
  easing: z.enum([
    "linear",
    "ease_in",
    "ease_out",
    "ease_in_out",
    "ease_out_cubic",
    "ease_in_out_cubic",
  ]).default("ease_in_out"),
  fov_start: z.number().min(10).max(120).optional(),
  fov_end: z.number().min(10).max(120).optional(),
}
```

**PlaneRefSchema:**
```typescript
{
  src: z.string().min(1),                           // Path/URL to image file
  opacity: z.number().min(0).max(1).default(1.0),   // OQ-01: per-plane opacity
  position_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [x, y, z] — AP-08 escape hatch
  rotation_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [rx, ry, rz] — AP-08 escape hatch
  scale: z.number().positive().default(1.0),         // Uniform scale multiplier
}
```
The `position_override` and `rotation_override` fields exist per AP-08 (do not hard-code the depth model). They are optional escape hatches — never the primary authoring method (AP-03).

**SceneSchema:**
```typescript
{
  id: z.string().min(1).regex(/^[a-zA-Z0-9_]+$/),  // Alphanumeric + underscore only
  duration: z.number().positive(),                   // Seconds, must be > 0
  start_time: z.number().nonnegative(),              // Seconds, >= 0
  geometry: z.string().min(1),                       // Validated against registry in semantic pass
  camera: z.string().min(1),                         // Validated against registry in semantic pass
  camera_params: CameraParamsSchema.optional(),
  transition_in: TransitionSchema.optional(),
  transition_out: TransitionSchema.optional(),
  planes: z.record(z.string(), PlaneRefSchema),      // Keys validated against geometry slots in semantic pass
}
```

**ManifestSchema:**
```typescript
{
  version: z.literal("3.0"),
  composition: CompositionSchema,
  scenes: z.array(SceneSchema).min(1),               // At least one scene
  metadata: z.record(z.string(), z.unknown()).optional(),  // Arbitrary key-value metadata, ignored by engine
}
```

### Module: `src/manifest/loader.ts`

This module exports the manifest loading and validation pipeline.

```typescript
/**
 * A single validation error with an actionable message.
 */
export interface ManifestError {
  path: string;        // Dot-notation path to the offending field (e.g., "scenes[0].planes.floor.src")
  code: string;        // Machine-readable error code (e.g., "UNKNOWN_GEOMETRY", "MISSING_REQUIRED_SLOT")
  message: string;     // Human-readable, actionable description
}

/**
 * The result of manifest validation. Discriminated union:
 * success=true means `manifest` is populated; success=false means `errors` is populated.
 */
export type ManifestResult =
  | { success: true; manifest: Manifest }
  | { success: false; errors: ManifestError[] };

/**
 * Phase 1: Structural validation via Zod.
 * Parses raw JSON/object against ManifestSchema.
 * Returns Zod-level errors mapped to ManifestError format.
 */
export function parseManifest(raw: unknown): ManifestResult;

/**
 * Phase 2: Semantic validation against a registry.
 * Assumes structural validation has already passed (input is a typed Manifest).
 * Checks: geometry existence, camera existence, camera-geometry compatibility,
 * plane keys match geometry slots, required slots are present, scene timing consistency.
 * Returns an array of ManifestErrors (empty = valid).
 */
export function validateManifestSemantics(
  manifest: Manifest,
  registry: ManifestRegistry,
): ManifestError[];

/**
 * Full validation pipeline: parse + semantic validation.
 * This is the primary entry point for consumers.
 */
export function loadManifest(
  raw: unknown,
  registry: ManifestRegistry,
): ManifestResult;

/**
 * Convenience: load from a file path. Reads JSON, then calls loadManifest().
 * Rejects with a ManifestError if the file doesn't exist or isn't valid JSON.
 */
export function loadManifestFromFile(
  filePath: string,
  registry: ManifestRegistry,
): Promise<ManifestResult>;
```

### Error Codes

The semantic validation pass must use these machine-readable error codes:

| Code | Condition |
|------|-----------|
| `UNKNOWN_GEOMETRY` | `scene.geometry` is not registered in the registry |
| `UNKNOWN_CAMERA` | `scene.camera` is not registered in the registry |
| `INCOMPATIBLE_CAMERA` | `scene.camera` is not in the geometry's `compatibleCameras` list |
| `MISSING_REQUIRED_SLOT` | A required plane slot for the geometry is not present in `scene.planes` |
| `UNKNOWN_SLOT` | A key in `scene.planes` is not a defined slot for the geometry |
| `DUPLICATE_SCENE_ID` | Two or more scenes share the same `id` |
| `SCENE_OVERLAP` | Two scenes' time ranges overlap (computed from `start_time` and `duration`) without a transition to justify it |
| `AUDIO_DURATION_MISMATCH` | Audio is provided and explicit scene durations sum to a different total (warning, not error — see design decision D-07) |
| `FOV_WITHOUT_SUPPORT` | `camera_params.fov_start` or `fov_end` is set but the camera preset does not support FOV animation |
| `INVALID_JSON` | File exists but is not valid JSON (for `loadManifestFromFile`) |
| `FILE_NOT_FOUND` | File path does not exist (for `loadManifestFromFile`) |

## Design Decisions

### D-01: Two-Phase Validation (Structural + Semantic)

**Choice:** Validation is split into two phases: Zod structural parsing (Phase 1) and registry-backed semantic validation (Phase 2).

**Rationale:** The Zod schema validates types, shapes, and value ranges — things that are statically knowable from the schema alone. But geometry names, camera names, camera-geometry compatibility, and plane-slot matching all depend on what geometries and cameras have been registered. Those registrations come from OBJ-005, OBJ-006, OBJ-018–025, and OBJ-026–034 — all of which are downstream of or parallel to OBJ-004. Separating the phases means OBJ-004 defines the registry *interface* but does not depend on any specific registrations existing.

**Alternative rejected:** A single Zod `.refine()` that hardcodes known geometry names. This would create a circular dependency (schema depends on geometry definitions) and require modifying `schema.ts` every time a new geometry is added.

### D-02: Registry Pattern for Extensibility

**Choice:** A `ManifestRegistry` with `registerGeometry()` and `registerCamera()` methods. Geometries and cameras register themselves at module load time. The loader accepts a registry as a parameter.

**Rationale:** Decouples the schema from specific geometry/camera implementations. OBJ-005 registers its base geometries; OBJ-018 registers the `stage` geometry's slots and compatible cameras; OBJ-026 registers the `slow_push_forward` camera's compatible geometries. The schema never changes.

**Implication:** `loadManifest()` requires a populated registry. The CLI (OBJ-013) and orchestrator (OBJ-035) are responsible for importing geometry/camera modules to populate the registry before calling `loadManifest()`. If the registry is empty, all geometry/camera references will fail semantic validation — this is correct behavior, not a bug.

### D-03: Manifest `planes` as `Record<string, PlaneRef>` (Not a Typed Per-Geometry Object)

**Choice:** `planes` is a `z.record(z.string(), PlaneRefSchema)` — an open-keyed map. The keys are validated against the geometry's slot definitions in the semantic pass, not in the Zod schema itself.

**Rationale:** Each geometry defines different slot names (`tunnel` has `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`; `stage` has `backdrop`, `floor`, `subject`). A Zod discriminated union keyed on `geometry` would require the schema to know all geometries at definition time — violating D-01. The open record + semantic validation approach is the only one that supports extensibility.

**Trade-off:** Zod parse alone cannot catch missing/extra plane keys. The semantic pass is required for complete validation. `loadManifest()` (which runs both phases) is the correct entry point for full validation.

### D-04: `start_time` Is Explicit, Not Computed

**Choice:** Each scene has an explicit `start_time` field (in seconds) rather than being auto-computed from the sum of prior scene durations.

**Rationale:** The seed example (Section 4.6) shows `start_time` on each scene. Explicit start times support overlapping transitions (scene 1 ends at 8.5s, scene 2 starts at 8.0s — a 0.5s overlap). Auto-computation would require a sequential model that doesn't naturally express overlaps.

**Implication:** The semantic validator checks for invalid overlaps (two scenes that overlap in time without a transition to justify the overlap). A valid overlap occurs when scene A's `transition_out` overlaps scene B's `transition_in`. The overlap window must not exceed the shorter of the two transition durations.

### D-05: `version` as Literal `"3.0"`

**Choice:** `z.literal("3.0")` — not a semver pattern, not a number.

**Rationale:** Seed Section 4.6 shows `"version": "3.0"`. A literal ensures forward compatibility: when v4.0 schemas exist, the loader can dispatch on version. Keeping it as a string (not number) avoids floating-point ambiguity.

### D-06: Easing Names Match Seed Vocabulary

**Choice:** The `easing` enum uses exact seed Section 2 names: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`.

**Rationale:** AP-06 (do not invent new terminology). These names are the binding vocabulary.

### D-07: Audio Duration Mismatch Is a Warning, Not a Hard Error

**Choice:** When audio is provided and explicit scene durations sum to a different total than the audio duration, the semantic validator emits a warning-level `ManifestError` with code `AUDIO_DURATION_MISMATCH`, but `loadManifest()` still returns `success: true`.

**Rationale:** Seed Section 8.7 says "if both audio and explicit durations: explicit durations are used, but the engine warns if T ≠ audio_duration." The manifest is valid; the engine should proceed but log the mismatch.

**Implementation detail:** `ManifestError` gains a `severity` field:

```typescript
export interface ManifestError {
  path: string;
  code: string;
  message: string;
  severity: "error" | "warning";
}
```

`ManifestResult` when `success: true` may still carry warnings:
```typescript
export type ManifestResult =
  | { success: true; manifest: Manifest; warnings: ManifestError[] }
  | { success: false; errors: ManifestError[] };
```

### D-08: PlaneRef Includes `opacity` and `scale`

**Choice:** Include `opacity` (default 1.0) and `scale` (default 1.0) on `PlaneRefSchema`.

**Rationale:** OQ-01 asks whether planes should support per-frame opacity animation. OBJ-004 does NOT define animation — it defines the *initial* opacity and scale as static values. Per-frame animation is a separate concern for a later objective. But including static opacity/scale in the manifest schema costs nothing and enables simple use cases (e.g., a semi-transparent fog overlay) without a future schema migration.

### D-09: Scene ID Uniqueness Enforced

**Choice:** Scene `id` values must be unique within a manifest. Validated in the semantic pass.

**Rationale:** Scene IDs are referenced by the scene sequencer and potentially by transitions. Duplicate IDs would create ambiguity.

### D-10: Transition Validation Rules

**Choice:** `transition_in` on scene 0 (the first scene) is allowed but only `cut` and `dip_to_black` types are valid (crossfade requires a preceding scene). Similarly, `transition_out` on the last scene is allowed for `cut` and `dip_to_black`. A `crossfade` on the first scene's `transition_in` or last scene's `transition_out` is a semantic error because there is no adjacent scene to blend with.

**Rationale:** Crossfade requires rendering two scenes simultaneously (seed Section 8.8). Without an adjacent scene, crossfade is undefined.

## Acceptance Criteria

- [ ] **AC-01:** `ManifestSchema` parses a valid manifest matching seed Section 4.6's example (with all required fields) and returns the typed `Manifest` object.
- [ ] **AC-02:** `ManifestSchema` rejects a manifest missing `version`, `composition`, or `scenes` with Zod errors that name the missing field.
- [ ] **AC-03:** `ManifestSchema` rejects `version: "2.0"` or `version: "4.0"` — only `"3.0"` is accepted.
- [ ] **AC-04:** `CompositionSchema` accepts `width: 1920, height: 1080, fps: 30` and `width: 1080, height: 1920, fps: 24` (C-04 baseline). Also accepts arbitrary positive integer dimensions and positive fps values.
- [ ] **AC-05:** `CompositionSchema` rejects `width: 0`, `height: -1`, `fps: 0`, `width: 1920.5` (non-integer dimensions).
- [ ] **AC-06:** `SceneSchema` rejects a scene with `duration: 0` or `duration: -5` (must be positive).
- [ ] **AC-07:** `SceneSchema` rejects a scene with `start_time: -1` (must be non-negative). Accepts `start_time: 0`.
- [ ] **AC-08:** `TransitionSchema` rejects `type: "wipe"` (not in the enum). Accepts `"cut"`, `"crossfade"`, `"dip_to_black"`.
- [ ] **AC-09:** `TransitionSchema` with `type: "crossfade"` rejects `duration: 0` and `duration: -1`. Accepts `duration: 0.5`.
- [ ] **AC-10:** `CameraParamsSchema` rejects `fov_start: 5` (below 10) and `fov_start: 130` (above 120).
- [ ] **AC-11:** `PlaneRefSchema` defaults `opacity` to 1.0 and `scale` to 1.0 when not provided.
- [ ] **AC-12:** Scene `id` field rejects `"scene 001"` (spaces) and `""` (empty). Accepts `"scene_001"` and `"s1"`.
- [ ] **AC-13:** `ManifestSchema` rejects `scenes: []` (at least one scene required).
- [ ] **AC-14:** `validateManifestSemantics()` returns `UNKNOWN_GEOMETRY` error when a scene references a geometry not in the registry. Error message includes the unknown geometry name.
- [ ] **AC-15:** `validateManifestSemantics()` returns `UNKNOWN_CAMERA` error when a scene references a camera not in the registry. Error message includes the unknown camera name.
- [ ] **AC-16:** `validateManifestSemantics()` returns `INCOMPATIBLE_CAMERA` error when a scene's camera is not in the geometry's `compatibleCameras` list. Error message names both the camera and geometry.
- [ ] **AC-17:** `validateManifestSemantics()` returns `MISSING_REQUIRED_SLOT` error when a geometry has a required slot not present in `scene.planes`. Error message names the missing slot.
- [ ] **AC-18:** `validateManifestSemantics()` returns `UNKNOWN_SLOT` error when `scene.planes` contains a key not defined by the geometry. Error message names the unknown key and lists valid slot names.
- [ ] **AC-19:** `validateManifestSemantics()` returns `DUPLICATE_SCENE_ID` error when two scenes share the same `id`.
- [ ] **AC-20:** `loadManifest()` runs both phases and returns a single `ManifestResult`. When structural validation fails, it returns all Zod errors mapped to `ManifestError` format — semantic validation is skipped.
- [ ] **AC-21:** `loadManifestFromFile()` returns `FILE_NOT_FOUND` error for a nonexistent path and `INVALID_JSON` error for a file containing `{not valid json}`.
- [ ] **AC-22:** `ManifestResult` on success includes a `warnings` array. `AUDIO_DURATION_MISMATCH` appears as a warning (not error) when audio is present and scene durations don't match.
- [ ] **AC-23:** `createRegistry()` returns a fresh registry with empty geometry and camera maps.
- [ ] **AC-24:** All exported types (`Manifest`, `Scene`, `Composition`, `Audio`, `Transition`, `CameraParams`, `PlaneRef`) are importable by downstream objectives.
- [ ] **AC-25:** Every `ManifestError` has a non-empty `path`, `code`, `message`, and `severity` field. No error has a generic message like "validation failed" — all messages are actionable (they name the specific field/value that caused the failure).

## Edge Cases and Error Handling

### E-01: Empty `planes` Object
A scene with `planes: {}` is structurally valid (Zod passes). Semantic validation checks whether the geometry has any required slots — if so, `MISSING_REQUIRED_SLOT` errors are produced for each one.

### E-02: Extra Fields in JSON
Zod's default behavior strips unknown keys. The schema should use `.passthrough()` on the top-level `ManifestSchema` and on `metadata` (which is explicitly a `z.record`), but `.strict()` on `SceneSchema`, `CompositionSchema`, `TransitionSchema`, and `CameraParamsSchema` to catch typos (e.g., `durration` instead of `duration`). Design choice: strict sub-schemas catch author typos; passthrough at the top level allows forward-compatible metadata.

### E-03: Overlapping Scenes Without Transitions
If scene A runs from t=0 to t=10 and scene B runs from t=9 to t=19 (a 1-second overlap), but neither has a `transition_out`/`transition_in` to justify the overlap, emit `SCENE_OVERLAP` error. Valid overlaps: the overlap duration must be ≤ the shorter of scene A's `transition_out.duration` and scene B's `transition_in.duration`.

### E-04: Scenes With Gaps
If scene A runs from t=0 to t=5 and scene B starts at t=7, there is a 2-second gap. This is a warning (`SCENE_GAP`), not an error — the engine renders black frames during gaps, which may be intentional (e.g., between a dip_to_black out and a dip_to_black in).

### E-05: `audio.volume` Out of Range
Zod enforces `0 ≤ volume ≤ 2`. Values outside that range are rejected at parse time. The range 0–2 allows for boost (values >1) which FFmpeg can apply via audio filters.

### E-06: `camera_params.fov_start` Without `fov_end` (or Vice Versa)
If only one of `fov_start` or `fov_end` is provided, the semantic validator does NOT error. The engine interprets a missing value as "use the camera's default FOV" for that end. This allows setting just `fov_end` to animate from default to a specific value.

### E-07: Registry With No Registrations
If `loadManifest()` is called with an empty registry, every scene will produce `UNKNOWN_GEOMETRY` and `UNKNOWN_CAMERA` errors. This is correct — the caller is responsible for populating the registry. The error messages should suggest "Did you forget to register geometries? Ensure geometry modules are imported before validation."

### E-08: Very Large Scene Counts
No hardcoded limit on scene count. A manifest with 500 scenes is valid if each scene is individually valid. Performance implications are the orchestrator's concern, not the schema's.

### E-09: `position_override` and `rotation_override` Values
These accept any finite number triples. No range restriction is applied at the schema level — the values are in world units/radians and depend on the geometry. A `position_override` of `[0, 0, -9999]` is syntactically valid even if it places the plane outside the camera frustum. The engine may log a warning at render time, but the schema does not reject it (AP-08: overrides must be possible).

### E-10: Manifest With Only Audio, No Explicit Scene Durations
The schema requires `duration > 0` on every scene, so a scene cannot have `duration: null` or `duration: 0`. If the caller wants audio-driven timing (seed Section 8.7: "scenes share duration proportionally"), this is handled by the manifest *generator* (which computes durations from audio length before producing the manifest), not by the schema. The schema always requires explicit positive durations.

### E-11: `start_time` Does Not Match Sum of Prior Durations
This is allowed. `start_time` is the authoritative timestamp for when a scene begins. The engine uses `start_time`, not accumulated durations. Semantic validation only checks for unintended overlaps and gaps (E-03, E-04).

## Test Strategy

### Unit Tests (`test/unit/manifest/`)

**Structural validation tests (`schema.test.ts`):**
1. Parse the seed Section 4.6 example manifest — must succeed.
2. Parse manifests with each optional field omitted — must succeed with defaults applied.
3. Parse manifests with each required field removed — must fail naming the field.
4. Parse manifests with wrong types (e.g., `duration: "eight"`) — must fail.
5. Parse manifests with boundary values: `duration: 0.001` (passes), `duration: 0` (fails), `fps: 0.5` (passes), `width: 1` (passes).
6. Verify `.strict()` rejects unknown keys on scene/composition objects.
7. Verify `TransitionSchema` superRefine rejects `crossfade` with `duration: 0`.
8. Verify `CameraParamsSchema` rejects FOV values outside 10–120.
9. Verify default values: `opacity` defaults to 1.0, `scale` to 1.0, `volume` to 1.0, `easing` to `"ease_in_out"`, `speed` to 1.0.

**Semantic validation tests (`loader.test.ts`):**
1. Register a mock `tunnel` geometry and `tunnel_push_forward` camera. Validate a manifest with matching planes — must succeed.
2. Validate a manifest referencing unregistered geometry — must return `UNKNOWN_GEOMETRY`.
3. Validate a manifest with missing required slot — must return `MISSING_REQUIRED_SLOT` with slot name.
4. Validate a manifest with extra unknown slot — must return `UNKNOWN_SLOT` with valid slot names listed.
5. Validate a manifest with incompatible camera — must return `INCOMPATIBLE_CAMERA`.
6. Validate a manifest with duplicate scene IDs — must return `DUPLICATE_SCENE_ID`.
7. Validate overlapping scenes without transitions — must return `SCENE_OVERLAP`.
8. Validate overlapping scenes WITH matching transitions — must succeed.
9. Validate with audio and mismatched durations — must succeed with `AUDIO_DURATION_MISMATCH` warning.
10. Validate with empty registry — all scenes produce `UNKNOWN_GEOMETRY` with a helpful suggestion message.

**Registry tests (`registry.test.ts`):**
1. `createRegistry()` returns a registry with empty maps.
2. `registerGeometry()` adds a geometry retrievable by name.
3. `registerCamera()` adds a camera retrievable by name.
4. Registering a geometry with a duplicate name overwrites the previous registration (no error — allows hot-reloading during development).

**File loading tests (`loader-file.test.ts`):**
1. Load from a valid JSON fixture file — must succeed.
2. Load from a nonexistent path — must return `FILE_NOT_FOUND` error.
3. Load from a file with invalid JSON — must return `INVALID_JSON` error.

**Relevant testable claims:** TC-04 (scene geometries eliminate manual 3D positioning — verified indirectly: the schema accepts geometry names + plane slot keys without coordinates), TC-07 (manifest validation catches common authoring errors — directly tested by the 20+ error scenarios above).

### Integration Test Sketch
A test in `test/integration/` that loads a complete manifest JSON file from `test/fixtures/`, registers mock geometries and cameras, validates the manifest, and asserts success. This is the "round-trip" test that validates the full `loadManifestFromFile()` pipeline. The fixture file should match the seed Section 4.6 example.

## Integration Points

### Depends on
- **OBJ-001** (Project Scaffolding): Provides `src/manifest/schema.ts` and `src/manifest/loader.ts` stubs, `zod` in dependencies, TypeScript build configuration, vitest test runner. OBJ-004 implements these two stubs.

### Consumed by
- **OBJ-005** (Scene Geometry Base): Imports `GeometryRegistration`, `PlaneSlotDef`, `ManifestRegistry` from `schema.ts` to register geometry definitions.
- **OBJ-006** (Camera Path Presets): Imports `CameraRegistration`, `ManifestRegistry` from `schema.ts` to register camera definitions.
- **OBJ-010** (Frame Clock): Imports `Manifest`, `Scene` types for timing calculations.
- **OBJ-013** (CLI): Imports `loadManifestFromFile()` and `createRegistry()` to validate manifests from the command line.
- **OBJ-016** (Audio Muxing): Imports `Audio` type and `Manifest` for audio configuration.
- **OBJ-017** (Texture Loading): Imports `PlaneRef` type for image source resolution.
- **OBJ-035** (Orchestrator): Imports `loadManifest()` as the entry point before rendering.
- **OBJ-044, OBJ-045** (Position/rotation overrides): Import `PlaneRef` type which already includes `position_override` and `rotation_override`.
- **OBJ-056** (SKILL.md): Documents the manifest schema as the authoring interface.
- **OBJ-070** (SKILL.md integration): References manifest schema for LLM authoring guidance.

### File Placement
- `src/manifest/schema.ts` — Zod schemas, TypeScript types, registry interfaces, `createRegistry()`.
- `src/manifest/loader.ts` — `parseManifest()`, `validateManifestSemantics()`, `loadManifest()`, `loadManifestFromFile()`.
- `test/unit/manifest/schema.test.ts` — Structural validation tests.
- `test/unit/manifest/loader.test.ts` — Semantic validation and file loading tests.
- `test/unit/manifest/registry.test.ts` — Registry tests.
- `test/fixtures/valid-manifest.json` — A complete valid manifest matching seed Section 4.6.

## Open Questions

### OQ-A: Should `planes` Allow Non-Geometry Slots for HUD Layers?
The seed defines HUD layers (Section 2) as 2D overlays not affected by perspective. Should the manifest schema support HUD layers within a scene's `planes` record (with a special prefix like `hud_title`), or should HUD layers be a separate top-level field on the scene? **Recommendation:** Defer to a later objective. HUD layers are mentioned in OQ-03 as potentially out of scope for V1. The current schema does not include them. If added later, a `hud_layers` field on `SceneSchema` would be cleaner than overloading `planes`.

### OQ-B: Should the Schema Support Scene Weights for Audio-Proportional Duration?
Seed Section 8.7 mentions "scenes share duration proportionally (or equally if no weights are provided)" when audio drives timing. The current schema requires explicit `duration` on every scene (E-10). Should an optional `weight` field be added to `SceneSchema` for proportional distribution? **Recommendation:** Defer. The manifest *generator* (the LLM authoring pipeline) computes durations from audio length before emitting the manifest. The schema always receives resolved durations.

### OQ-C: Scene Ordering — Array Index vs. `start_time`?
The manifest uses both array order and `start_time`. If array order and `start_time` values disagree (e.g., scene at index 0 has `start_time: 10` and scene at index 1 has `start_time: 0`), which takes precedence? **Recommendation:** `start_time` is authoritative. The semantic validator should emit a warning (`SCENE_ORDER_MISMATCH`) if scenes are not in `start_time` order, but this is not an error. The engine sorts scenes by `start_time` internally.

---

I believe this specification is complete and precise. I'd like the Challenger to verify:

1. The two-phase validation approach (structural Zod + semantic registry) is sound and doesn't create gaps.
2. The registry interface is sufficient for OBJ-005 and OBJ-006 to register their definitions without schema changes.
3. The error codes and messages satisfy C-10's "actionable messages" requirement.
4. The edge cases around scene timing (overlaps, gaps, audio mismatch) are handled correctly per the seed.
5. The `PlaneRefSchema` fields (`opacity`, `scale`, `position_override`, `rotation_override`) are appropriate at this level vs. deferring to later objectives.

Please review and challenge.

---

## Round 2 — spec_challenger

I've read the proposed spec carefully. Let me start with what's sound, then systematically challenge the gaps.

## Points of Agreement

These aspects are well-designed and I approve them:

1. **Two-phase validation (structural Zod + semantic registry)** — Clean separation, avoids circular dependencies. Sound.
2. **Registry pattern** — Correctly decouples schema from geometry/camera implementations. The `ManifestRegistry` interface is minimal and sufficient.
3. **`planes` as `Record<string, PlaneRef>`** — Only viable approach given extensible geometries. Correct.
4. **`version: z.literal("3.0")`** — Matches seed Section 4.6 exactly.
5. **Easing names** — Match seed Section 2 vocabulary. AP-06 compliant.
6. **D-04 (explicit `start_time`)** — Correctly supports overlapping transitions per the seed example.
7. **File placement** — Aligns with OBJ-001 stubs.
8. **Most acceptance criteria** — AC-01 through AC-13 are specific and testable.

---

## Challenges

### CRITICAL-1: `severity` field exists in D-07 but not in the canonical `ManifestError` interface

The `ManifestError` interface at the top of the loader contract has three fields: `path`, `code`, `message`. Then D-07 casually adds `severity: "error" | "warning"` and AC-25 requires it. An implementer reading top-to-bottom would define the interface without `severity`, then hit D-07 and have to retrofit it.

**Fix:** The canonical `ManifestError` interface definition must include `severity` from the start:

```typescript
export interface ManifestError {
  path: string;
  code: string;
  message: string;
  severity: "error" | "warning";
}
```

### CRITICAL-2: `SCENE_GAP` warning code used in E-04 but missing from the error codes table

E-04 introduces `SCENE_GAP` as a warning but it's not in the error codes table. An implementer following the table as their checklist would never implement it.

**Fix:** Add to the error codes table:

| `SCENE_GAP` | Two adjacent scenes (by `start_time` order) have a time gap between them (warning, not error) |

### CRITICAL-3: Camera-geometry compatibility check direction is ambiguous

`GeometryRegistration` has `compatibleCameras: string[]`. `CameraRegistration` has `compatibleGeometries: string[]`. The `INCOMPATIBLE_CAMERA` check — which list is authoritative? What if the geometry says camera X is compatible but camera X says it's NOT compatible with that geometry? Must both agree? Either one?

The seed Section 8.6 defines `compatible_cameras` on the geometry. Section 4.3 defines `compatible_geometries` on the camera. Both exist, but the validation rule needs a single source of truth.

**Fix:** Define explicitly: The `INCOMPATIBLE_CAMERA` check uses the geometry's `compatibleCameras` list as the authoritative source. If `scene.camera` is not in `registry.geometries.get(scene.geometry).compatibleCameras`, it's incompatible. The camera's `compatibleGeometries` is informational metadata for SKILL.md authoring guidance — the semantic validator does NOT cross-check it. Add this as a design decision.

### CRITICAL-4: `AUDIO_DURATION_MISMATCH` requires audio file reading — where does the duration come from?

The semantic validator checks whether scene durations match audio duration. But `AudioSchema` only has `src` (a file path) and `volume`. To know the audio's duration, the validator would need to read the audio file and call FFprobe or similar — which is a render-time concern, not a validation concern.

The spec never addresses how the audio duration is obtained for this check.

**Fix:** Three options (pick one):
- **(a)** Add an optional `duration` field to `AudioSchema`: `duration: z.number().positive().optional()`. The manifest generator fills this in. The semantic validator only checks mismatch when `audio.duration` is present. This is the cleanest.
- **(b)** Remove `AUDIO_DURATION_MISMATCH` from manifest validation entirely — make it a render-time warning in the orchestrator (OBJ-035).
- **(c)** Add an optional `audioDuration` parameter to `validateManifestSemantics()`.

I recommend **(a)** — it's self-contained and the manifest generator (the LLM pipeline) already knows the audio duration.

### MAJOR-1: `SCENE_OVERLAP` validation logic is imprecise

The spec says "the overlap window must not exceed the shorter of the two transition durations" but doesn't define the overlap calculation precisely. Given:
- Scene A: `start_time=0, duration=8.5, transition_out={type:"crossfade", duration:1.0}`
- Scene B: `start_time=8.0, duration=10.0, transition_in={type:"crossfade", duration:1.0}`

What's the overlap? Is it `max(0, (A.start_time + A.duration) - B.start_time)` = `max(0, 8.5 - 8.0)` = 0.5? And the rule is `overlap ≤ min(A.transition_out.duration, B.transition_in.duration)`?

What if scene A has `transition_out` but scene B has NO `transition_in`? Is a 0.5s overlap valid?

What if both scenes have `cut` transitions (duration 0) but overlap by 0.5s?

**Fix:** Define precisely:
1. Overlap between consecutive scenes (sorted by `start_time`) = `max(0, (A.start_time + A.duration) - B.start_time)`.
2. Overlap is valid if AND only if: both `A.transition_out` and `B.transition_in` exist, neither is `type: "cut"`, and `overlap ≤ min(A.transition_out.duration, B.transition_in.duration)`.
3. Any overlap that doesn't satisfy condition 2 produces `SCENE_OVERLAP` error.

### MAJOR-2: `TransitionSchema` superRefine for `cut` is ambiguous: "must be 0 (or is ignored)"

"If `type === 'cut'`, `duration` must be 0 (or is ignored)." Which is it? Reject `{type: "cut", duration: 1.0}`, or accept it and discard the duration? These are different behaviors for an LLM author.

**Fix:** Pick one. I recommend: for `type: "cut"`, `duration` defaults to 0 and any provided value is accepted but ignored by the engine. This is more forgiving for LLM authors (consistent with AP-03's "make correct authoring easy" spirit). Remove the superRefine for `cut` — only enforce `duration > 0` for non-`cut` types.

### MAJOR-3: `fps` allows impractical values

`fps: z.number().positive()` accepts `fps: 0.001` (one frame per 1000 seconds) or `fps: 240` (expensive renders). The seed specifies integer fps values (24, 30). Should fractional fps (23.976 for NTSC) be supported? If yes, fine — but there should be practical bounds.

**Fix:** Add `.min(1).max(120)` to the fps constraint. If fractional fps is intended, keep it as `z.number()`. If only integer fps is intended (the seed only mentions 24 and 30), use `z.number().int()`. Document the decision. I'd recommend `z.number().int().min(1).max(120)` for V1 — the seed never discusses fractional fps and it simplifies frame-clock math.

### MAJOR-4: `dip_to_black` semantics as `transition_in` vs `transition_out` are undefined

D-10 says `dip_to_black` is allowed on the first scene's `transition_in` and last scene's `transition_out`. But the seed defines `dip_to_black` as "fade out then fade in." When used as `transition_in` alone, does it mean "fade in from black"? When used as `transition_out` alone, "fade out to black"?

The implementer of the scene sequencer (OBJ-015) needs to know what these mean. Since OBJ-004 defines the contract, it should specify the semantics.

**Fix:** Add a note to `TransitionSchema` or a design decision:
- `transition_in: dip_to_black` = scene fades in from black over `duration` seconds.
- `transition_out: dip_to_black` = scene fades out to black over `duration` seconds.
- The seed's "fade out then fade in" describes the combined effect of scene A's `transition_out: dip_to_black` + scene B's `transition_in: dip_to_black`.

### MAJOR-5: Total video duration computation is never defined

E-04, `AUDIO_DURATION_MISMATCH`, and the orchestrator all need to know the total video duration. Is it `max(scene.start_time + scene.duration)` across all scenes? Or `sum(scene.duration)`? These differ when scenes overlap.

**Fix:** Define: Total video duration = `max across all scenes of (start_time + duration)`. Add this as a note or a utility function export from the loader.

### MAJOR-6: `PlaneRefSchema` uses `.strict()` or not?

E-02 says `SceneSchema`, `CompositionSchema`, `TransitionSchema`, and `CameraParamsSchema` use `.strict()`. But `PlaneRefSchema` is not mentioned. If it's not strict, a typo like `opactiy: 0.5` would be silently stripped, and the LLM author would get full opacity with no error.

**Fix:** Add `PlaneRefSchema` to the `.strict()` list in E-02.

### MINOR-1: `metadata` field purpose is undocumented

`metadata: z.record(z.string(), z.unknown()).optional()` — what is this for? The seed doesn't mention manifest-level metadata. A one-line description would prevent confusion.

**Fix:** Add a comment: "Arbitrary key-value metadata for pipeline integration (e.g., job ID, topic, style). Ignored by the rendering engine. Passed through for downstream consumers."

### MINOR-2: `SCENE_ORDER_MISMATCH` in OQ-C should be a decision, not an open question

OQ-C presents a clear recommendation ("start_time is authoritative, warn if array order disagrees") but frames it as an open question. If the spec author is confident, promote it to a design decision. If genuinely unresolved, keep it as OQ but add the warning code to the error codes table as provisional.

**Fix:** Promote to design decision D-11. Add `SCENE_ORDER_MISMATCH` to the error codes table as a warning.

### MINOR-3: `CameraRegistration.supportsFovAnimation` is never used in validation

The interface defines `supportsFovAnimation: boolean` and error code `FOV_WITHOUT_SUPPORT` exists, but the validation logic description doesn't explain when this check fires.

**Fix:** Add to the semantic validation description: "If `camera_params.fov_start` or `camera_params.fov_end` is set, and the camera's `supportsFovAnimation` is false, emit `FOV_WITHOUT_SUPPORT`."

### MINOR-4: File existence validation for `src` paths is implicitly out of scope but never stated

The spec validates structure and semantics but never checks whether `planes.*.src` or `audio.src` files actually exist. This is probably correct (render-time concern), but the boundary should be explicit.

**Fix:** Add a note: "File existence validation for `src` paths (images, audio) is NOT part of manifest validation. The orchestrator (OBJ-035) resolves and validates file paths at render time."

---

## Summary

- **4 critical issues** (severity field placement, missing error code, compatibility direction, audio duration source)
- **6 major issues** (overlap logic, cut/duration ambiguity, fps bounds, dip_to_black semantics, total duration computation, PlaneRef strictness)
- **4 minor issues** (metadata docs, order mismatch promotion, FOV check logic, file existence scope)

Please address all critical and major issues in your revision. I'll verify the fixes structurally before converging.

---

## Round 3 — spec_author

Thank you for the thorough review. All 14 issues are valid. Here's the revised specification with every point addressed.

---

# Revised Specification: OBJ-004 — Manifest Schema Core

## Summary

OBJ-004 defines the Zod validation schema and loader for the depthkit manifest — the declarative JSON document that describes an entire video. This is the authoring contract between LLM manifest authors and the rendering engine. The schema enforces structural correctness (types, ranges, required fields) via Zod parsing and semantic correctness (geometry existence, camera compatibility, plane-slot matching) via a registry-backed validation pass. It satisfies C-04 (resolution/fps support) and C-10 (validate before rendering, fail fast with actionable errors).

## Interface Contract

### Module: `src/manifest/schema.ts`

Exports Zod schemas, inferred TypeScript types, and the registry interfaces that downstream geometry/camera objectives use to register their definitions.

```typescript
// === Registry Interfaces ===

export interface PlaneSlotDef {
  required: boolean;
  description: string;
}

export interface GeometryRegistration {
  name: string;
  slots: Record<string, PlaneSlotDef>;
  compatibleCameras: string[];
  defaultCamera: string;
}

export interface CameraRegistration {
  name: string;
  compatibleGeometries: string[];  // Informational only — NOT used for validation (see D-03)
  supportsFovAnimation: boolean;
}

export interface ManifestRegistry {
  geometries: Map<string, GeometryRegistration>;
  cameras: Map<string, CameraRegistration>;
  registerGeometry(def: GeometryRegistration): void;
  registerCamera(def: CameraRegistration): void;
}

export function createRegistry(): ManifestRegistry;

// === Validation Types ===

export interface ManifestError {
  path: string;        // Dot-notation path (e.g., "scenes[0].planes.floor.src")
  code: string;        // Machine-readable error code (see Error Codes table)
  message: string;     // Human-readable, actionable description
  severity: "error" | "warning";
}

export type ManifestResult =
  | { success: true; manifest: Manifest; warnings: ManifestError[] }
  | { success: false; errors: ManifestError[] };

// === Zod Schemas (shapes below) ===

export const AudioSchema: z.ZodType;
export type Audio = z.infer<typeof AudioSchema>;

export const CompositionSchema: z.ZodType;
export type Composition = z.infer<typeof CompositionSchema>;

export const TransitionSchema: z.ZodType;
export type Transition = z.infer<typeof TransitionSchema>;

export const CameraParamsSchema: z.ZodType;
export type CameraParams = z.infer<typeof CameraParamsSchema>;

export const PlaneRefSchema: z.ZodType;
export type PlaneRef = z.infer<typeof PlaneRefSchema>;

export const SceneSchema: z.ZodType;
export type Scene = z.infer<typeof SceneSchema>;

export const ManifestSchema: z.ZodType;
export type Manifest = z.infer<typeof ManifestSchema>;
```

#### Zod Schema Shapes

**AudioSchema:**
```typescript
{
  src: z.string().min(1),
  volume: z.number().min(0).max(2).default(1.0),
  duration: z.number().positive().optional(),  // Seconds. When present, enables AUDIO_DURATION_MISMATCH check.
}
```

**CompositionSchema** (`.strict()`):
```typescript
{
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  fps: z.number().int().min(1).max(120),
  audio: AudioSchema.optional(),
}
```

**TransitionSchema** (`.strict()`):
```typescript
{
  type: z.enum(["cut", "crossfade", "dip_to_black"]),
  duration: z.number().nonnegative().default(0),
}
```
Refinement via `.superRefine()`: if `type` is `"crossfade"` or `"dip_to_black"`, `duration` must be > 0. If `type` is `"cut"`, any `duration` value is accepted but ignored by the engine (defaults to 0).

Transition semantics (for downstream OBJ-015 scene sequencer):
- `transition_in: crossfade` — scene blends in from the preceding scene over `duration` seconds. Requires a preceding scene.
- `transition_out: crossfade` — scene blends out into the following scene over `duration` seconds. Requires a following scene.
- `transition_in: dip_to_black` — scene fades in from black over `duration` seconds. No preceding scene required.
- `transition_out: dip_to_black` — scene fades out to black over `duration` seconds. No following scene required.
- The seed's description "fade out then fade in" describes the combined effect of scene A's `transition_out: dip_to_black` + scene B's `transition_in: dip_to_black`.
- `cut` — instant transition. No blending.

**CameraParamsSchema** (`.strict()`):
```typescript
{
  speed: z.number().positive().default(1.0),
  easing: z.enum([
    "linear",
    "ease_in",
    "ease_out",
    "ease_in_out",
    "ease_out_cubic",
    "ease_in_out_cubic",
  ]).default("ease_in_out"),
  fov_start: z.number().min(10).max(120).optional(),
  fov_end: z.number().min(10).max(120).optional(),
}
```

**PlaneRefSchema** (`.strict()`):
```typescript
{
  src: z.string().min(1),
  opacity: z.number().min(0).max(1).default(1.0),
  position_override: z.tuple([z.number(), z.number(), z.number()]).optional(),
  rotation_override: z.tuple([z.number(), z.number(), z.number()]).optional(),
  scale: z.number().positive().default(1.0),
}
```

**SceneSchema** (`.strict()`):
```typescript
{
  id: z.string().min(1).regex(/^[a-zA-Z0-9_]+$/),
  duration: z.number().positive(),
  start_time: z.number().nonnegative(),
  geometry: z.string().min(1),
  camera: z.string().min(1),
  camera_params: CameraParamsSchema.optional(),
  transition_in: TransitionSchema.optional(),
  transition_out: TransitionSchema.optional(),
  planes: z.record(z.string(), PlaneRefSchema),
}
```

**ManifestSchema** (`.passthrough()` at top level):
```typescript
{
  version: z.literal("3.0"),
  composition: CompositionSchema,
  scenes: z.array(SceneSchema).min(1),
  metadata: z.record(z.string(), z.unknown()).optional(),
    // Arbitrary key-value metadata for pipeline integration (e.g., job ID, topic, style).
    // Ignored by the rendering engine. Passed through for downstream consumers.
}
```

### Module: `src/manifest/loader.ts`

```typescript
export function parseManifest(raw: unknown): ManifestResult;

export function validateManifestSemantics(
  manifest: Manifest,
  registry: ManifestRegistry,
): ManifestError[];

export function loadManifest(
  raw: unknown,
  registry: ManifestRegistry,
): ManifestResult;

export function loadManifestFromFile(
  filePath: string,
  registry: ManifestRegistry,
): Promise<ManifestResult>;

/**
 * Computes total video duration from a validated manifest.
 * Total = max across all scenes of (start_time + duration).
 */
export function computeTotalDuration(manifest: Manifest): number;
```

### Error Codes

| Code | Severity | Condition |
|------|----------|-----------|
| `UNKNOWN_GEOMETRY` | error | `scene.geometry` is not registered in the registry |
| `UNKNOWN_CAMERA` | error | `scene.camera` is not registered in the registry |
| `INCOMPATIBLE_CAMERA` | error | `scene.camera` is not in the geometry's `compatibleCameras` list |
| `MISSING_REQUIRED_SLOT` | error | A required plane slot for the geometry is not present in `scene.planes` |
| `UNKNOWN_SLOT` | error | A key in `scene.planes` is not a defined slot for the geometry |
| `DUPLICATE_SCENE_ID` | error | Two or more scenes share the same `id` |
| `SCENE_OVERLAP` | error | Two scenes overlap in time without valid transitions justifying the overlap (see E-03) |
| `SCENE_GAP` | warning | Two consecutive scenes (by `start_time` order) have a time gap between them |
| `SCENE_ORDER_MISMATCH` | warning | Scenes in the array are not ordered by ascending `start_time` |
| `AUDIO_DURATION_MISMATCH` | warning | `audio.duration` is present and differs from `computeTotalDuration()` |
| `FOV_WITHOUT_SUPPORT` | warning | `camera_params.fov_start` or `fov_end` is set but the camera's `supportsFovAnimation` is false |
| `CROSSFADE_NO_ADJACENT` | error | `transition_in: crossfade` on the first scene (no preceding scene) or `transition_out: crossfade` on the last scene (no following scene) |
| `INVALID_JSON` | error | File exists but is not valid JSON (for `loadManifestFromFile`) |
| `FILE_NOT_FOUND` | error | File path does not exist (for `loadManifestFromFile`) |

### Scope Boundary: File Existence

File existence validation for `src` paths (images, audio) is NOT part of manifest validation. The orchestrator (OBJ-035) resolves and validates file paths at render time. The manifest schema validates only that `src` is a non-empty string.

## Design Decisions

### D-01: Two-Phase Validation (Structural + Semantic)

**Choice:** Validation is split: Zod structural parsing (Phase 1) and registry-backed semantic validation (Phase 2).

**Rationale:** Zod validates types, shapes, and value ranges statically. Geometry names, camera names, compatibility, and plane-slot matching depend on runtime registrations from OBJ-005, OBJ-006, OBJ-018–025, and OBJ-026–034. Separating phases means OBJ-004 defines the registry *interface* without depending on specific registrations.

**Alternative rejected:** A single Zod `.refine()` hardcoding known geometry names — creates circular dependency and requires modifying `schema.ts` for every new geometry.

### D-02: Registry Pattern for Extensibility

**Choice:** A `ManifestRegistry` with `registerGeometry()` and `registerCamera()`. The loader accepts a registry as a parameter.

**Rationale:** Decouples schema from implementations. If the registry is empty when `loadManifest()` is called, every scene produces `UNKNOWN_GEOMETRY`/`UNKNOWN_CAMERA` errors. Error messages should suggest: "Did you forget to register geometries? Ensure geometry modules are imported before validation."

### D-03: Geometry's `compatibleCameras` Is Authoritative for Validation

**Choice:** The `INCOMPATIBLE_CAMERA` check uses the geometry's `compatibleCameras` list as the single source of truth. If `scene.camera` is not in `registry.geometries.get(scene.geometry).compatibleCameras`, it is incompatible.

The camera's `compatibleGeometries` field is informational metadata for SKILL.md authoring guidance and documentation only. The semantic validator does NOT cross-check it.

**Rationale:** The seed Section 8.6 defines `compatible_cameras` on the geometry as the primary contract. The camera's `compatibleGeometries` in Section 4.3 is descriptive. Using a single authoritative direction eliminates ambiguity when the two lists disagree.

### D-04: `start_time` Is Explicit, Not Computed

**Choice:** Each scene has an explicit `start_time` field (seconds), not auto-computed from prior durations.

**Rationale:** Seed Section 4.6 example shows `start_time` on each scene. Explicit start times support overlapping transitions (scene 1 ends at 8.5s, scene 2 starts at 8.0s — 0.5s overlap).

### D-05: `version` as Literal `"3.0"`

**Choice:** `z.literal("3.0")`.

**Rationale:** Seed Section 4.6 shows `"version": "3.0"`. String literal enables future version dispatch.

### D-06: Easing Names Match Seed Vocabulary

**Choice:** Enum uses exact seed Section 2 names: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`.

**Rationale:** AP-06 compliance.

### D-07: Audio Duration Mismatch Is a Warning, Not a Hard Error

**Choice:** When `audio.duration` is present on the manifest and the total scene duration (computed via `computeTotalDuration()`) differs, emit `AUDIO_DURATION_MISMATCH` as a warning. `loadManifest()` still returns `success: true`.

**Rationale:** Seed Section 8.7: "if both audio and explicit durations: explicit durations are used, but the engine warns." The `duration` field on `AudioSchema` is optional — if the manifest generator doesn't provide it, the check is skipped entirely. Audio file reading/probing is a render-time concern (OBJ-035), not a validation concern.

### D-08: PlaneRef Includes `opacity` and `scale`

**Choice:** Static `opacity` (default 1.0) and `scale` (default 1.0) on `PlaneRefSchema`.

**Rationale:** Enables simple use cases (semi-transparent fog overlay) without schema migration. Per-frame animation is a separate concern for a later objective.

### D-09: Scene ID Uniqueness Enforced

**Choice:** Duplicate `id` values produce `DUPLICATE_SCENE_ID` error.

### D-10: Transition Validation Rules

**Choice:** `crossfade` requires an adjacent scene to blend with. `dip_to_black` and `cut` work on any scene.

Specifically:
- First scene's `transition_in`: `crossfade` → `CROSSFADE_NO_ADJACENT` error. `dip_to_black` and `cut` → allowed.
- Last scene's `transition_out`: `crossfade` → `CROSSFADE_NO_ADJACENT` error. `dip_to_black` and `cut` → allowed.
- For `type: "cut"`, any provided `duration` is accepted and ignored (defaults to 0). No superRefine rejection.
- For `type: "crossfade"` or `"dip_to_black"`, `duration` must be > 0 (enforced via superRefine).

### D-11: `start_time` Is Authoritative; Array Order Disagreement Is a Warning

**Choice:** `start_time` is the authoritative timestamp for scene ordering. The engine sorts scenes by `start_time` internally. If the array order disagrees with `start_time` order, emit `SCENE_ORDER_MISMATCH` warning. This is not an error — the manifest is valid.

### D-12: Integer FPS with Practical Bounds

**Choice:** `fps: z.number().int().min(1).max(120)`.

**Rationale:** The seed only mentions integer fps (24, 30). Integer fps simplifies frame-clock math (OBJ-010). The 1–120 range excludes impractical values while allowing common rates (24, 25, 30, 48, 60). Fractional fps (23.976 NTSC) is out of scope for V1. If needed later, the constraint can be relaxed.

### D-13: `planes` as Open Record with Semantic Slot Validation

**Choice:** `planes` is `z.record(z.string(), PlaneRefSchema)`. Keys validated against geometry slots in semantic pass.

**Rationale:** Each geometry defines different slot names. An open record + semantic validation is the only approach supporting extensible geometries.

### D-14: Strict Sub-Schemas, Passthrough Top-Level

**Choice:** `.strict()` on `SceneSchema`, `CompositionSchema`, `TransitionSchema`, `CameraParamsSchema`, and `PlaneRefSchema`. `.passthrough()` on top-level `ManifestSchema`.

**Rationale:** Strict sub-schemas catch LLM author typos (e.g., `durration`). Passthrough at top level allows forward-compatible metadata. `PlaneRefSchema` is strict to catch typos like `opactiy`.

### D-15: Total Video Duration Computation

**Choice:** Total video duration = `max across all scenes of (start_time + duration)`. Exported as `computeTotalDuration()`.

**Rationale:** This accounts for overlapping and non-sequential scenes. Simple, unambiguous.

## Acceptance Criteria

- [ ] **AC-01:** `ManifestSchema` parses a valid manifest matching seed Section 4.6's example and returns the typed `Manifest` object.
- [ ] **AC-02:** `ManifestSchema` rejects a manifest missing `version`, `composition`, or `scenes` with Zod errors naming the missing field.
- [ ] **AC-03:** `ManifestSchema` rejects `version: "2.0"` and `version: "4.0"` — only `"3.0"` accepted.
- [ ] **AC-04:** `CompositionSchema` accepts `{width: 1920, height: 1080, fps: 30}` and `{width: 1080, height: 1920, fps: 24}` (C-04 baseline). Also accepts other valid combinations.
- [ ] **AC-05:** `CompositionSchema` rejects `width: 0`, `height: -1`, `fps: 0`, `fps: 121`, `fps: 23.976` (non-integer), `width: 1920.5` (non-integer).
- [ ] **AC-06:** `SceneSchema` rejects `duration: 0` and `duration: -5`.
- [ ] **AC-07:** `SceneSchema` rejects `start_time: -1`. Accepts `start_time: 0`.
- [ ] **AC-08:** `TransitionSchema` rejects `type: "wipe"`. Accepts `"cut"`, `"crossfade"`, `"dip_to_black"`.
- [ ] **AC-09:** `TransitionSchema` with `type: "crossfade"` rejects `duration: 0` and `duration: -1`. Accepts `duration: 0.5`.
- [ ] **AC-10:** `TransitionSchema` with `type: "cut"` accepts `duration: 1.0` without error (value is ignored).
- [ ] **AC-11:** `CameraParamsSchema` rejects `fov_start: 5` (below 10) and `fov_start: 130` (above 120).
- [ ] **AC-12:** `PlaneRefSchema` defaults `opacity` to 1.0 and `scale` to 1.0 when not provided.
- [ ] **AC-13:** Scene `id` rejects `"scene 001"` (spaces) and `""` (empty). Accepts `"scene_001"` and `"s1"`.
- [ ] **AC-14:** `ManifestSchema` rejects `scenes: []` (at least one scene required).
- [ ] **AC-15:** `PlaneRefSchema` rejects unknown keys (e.g., `{src: "x.png", opactiy: 0.5}` → Zod error on `opactiy`).
- [ ] **AC-16:** `SceneSchema` rejects unknown keys (e.g., `{id: "s1", ..., durration: 5}` → Zod error on `durration`).
- [ ] **AC-17:** `validateManifestSemantics()` returns `UNKNOWN_GEOMETRY` when a scene references an unregistered geometry. Error message includes the geometry name.
- [ ] **AC-18:** `validateManifestSemantics()` returns `UNKNOWN_CAMERA` when a scene references an unregistered camera. Error message includes the camera name.
- [ ] **AC-19:** `validateManifestSemantics()` returns `INCOMPATIBLE_CAMERA` when a scene's camera is not in the geometry's `compatibleCameras` list. Error message names both camera and geometry.
- [ ] **AC-20:** `validateManifestSemantics()` returns `MISSING_REQUIRED_SLOT` when a required slot is missing from `scene.planes`. Error message names the missing slot.
- [ ] **AC-21:** `validateManifestSemantics()` returns `UNKNOWN_SLOT` when `scene.planes` has a key not in the geometry's slot definitions. Error message names the unknown key and lists valid slots.
- [ ] **AC-22:** `validateManifestSemantics()` returns `DUPLICATE_SCENE_ID` when two scenes share the same `id`.
- [ ] **AC-23:** `validateManifestSemantics()` returns `SCENE_OVERLAP` error for overlapping scenes without valid transitions (per E-03 rules).
- [ ] **AC-24:** `validateManifestSemantics()` returns `SCENE_GAP` warning for time gaps between consecutive scenes.
- [ ] **AC-25:** `validateManifestSemantics()` returns `SCENE_ORDER_MISMATCH` warning when array order disagrees with `start_time` order.
- [ ] **AC-26:** `validateManifestSemantics()` returns `AUDIO_DURATION_MISMATCH` warning when `audio.duration` is present and differs from `computeTotalDuration()`. `loadManifest()` still returns `success: true`.
- [ ] **AC-27:** `validateManifestSemantics()` returns `CROSSFADE_NO_ADJACENT` error for `crossfade` as `transition_in` on the first scene or `transition_out` on the last scene.
- [ ] **AC-28:** `validateManifestSemantics()` returns `FOV_WITHOUT_SUPPORT` warning when `camera_params.fov_start` or `fov_end` is set but the camera's `supportsFovAnimation` is false.
- [ ] **AC-29:** `loadManifest()` runs both phases, returns single `ManifestResult`. Structural failure → returns Zod errors, skips semantic validation.
- [ ] **AC-30:** `loadManifestFromFile()` returns `FILE_NOT_FOUND` for a nonexistent path and `INVALID_JSON` for invalid JSON.
- [ ] **AC-31:** `createRegistry()` returns a fresh registry with empty maps.
- [ ] **AC-32:** `computeTotalDuration()` returns `max(start_time + duration)` across all scenes.
- [ ] **AC-33:** All exported types are importable by downstream objectives.
- [ ] **AC-34:** Every `ManifestError` has non-empty `path`, `code`, `message`, and `severity`. No generic messages — all are actionable.

## Edge Cases and Error Handling

### E-01: Empty `planes` Object
`planes: {}` passes Zod. Semantic validation produces `MISSING_REQUIRED_SLOT` for each required slot in the geometry.

### E-02: Extra Fields on Strict Sub-Schemas
`.strict()` on `SceneSchema`, `CompositionSchema`, `TransitionSchema`, `CameraParamsSchema`, and `PlaneRefSchema` causes Zod to reject unrecognized keys with an error naming the key. `.passthrough()` on top-level `ManifestSchema` allows forward-compatible top-level fields.

### E-03: Overlapping Scenes — Precise Rules

Scenes are sorted by `start_time` for overlap analysis. For each consecutive pair (A, B) in sorted order:

1. **Compute overlap:** `overlap = max(0, (A.start_time + A.duration) - B.start_time)`
2. **If overlap == 0:** No overlap. Check for gap (E-04).
3. **If overlap > 0:** The overlap is valid if and only if ALL of:
   - `A.transition_out` exists and its `type` is not `"cut"`
   - `B.transition_in` exists and its `type` is not `"cut"`
   - `overlap ≤ min(A.transition_out.duration, B.transition_in.duration)`
4. If condition 3 is not fully met, emit `SCENE_OVERLAP` error naming scenes A and B, the overlap duration, and what's missing (e.g., "Scene 'scene_001' and 'scene_002' overlap by 0.5s but scene_001 has no transition_out").

### E-04: Scenes With Gaps
For consecutive scenes (sorted by `start_time`) where `B.start_time > A.start_time + A.duration`, emit `SCENE_GAP` warning. Gap = `B.start_time - (A.start_time + A.duration)`. The engine renders black frames during gaps.

### E-05: `audio.volume` Out of Range
Zod enforces `0 ≤ volume ≤ 2`. The range allows boost (>1) via FFmpeg audio filters.

### E-06: `fov_start` Without `fov_end` (or Vice Versa)
Not a semantic error. The engine interprets a missing value as "use the camera's default FOV" for that end. Allows setting just `fov_end` to animate from default to a target.

### E-07: Registry With No Registrations
All scenes produce `UNKNOWN_GEOMETRY` and `UNKNOWN_CAMERA`. Error messages include: "Did you forget to register geometries? Ensure geometry modules are imported before validation."

### E-08: Very Large Scene Counts
No hardcoded limit. A 500-scene manifest is valid if individually valid.

### E-09: `position_override` and `rotation_override` Values
Accept any finite number triples. No range restriction — values are in world units/radians and depend on geometry context. Out-of-frustum placements are the engine's concern at render time.

### E-10: Audio-Driven Timing
The schema requires `duration > 0` on every scene. Audio-proportional timing is computed by the manifest *generator* before emitting the manifest. The schema always receives resolved durations.

### E-11: `start_time` Disagrees With Array Order
Warning `SCENE_ORDER_MISMATCH`, not an error. Engine sorts by `start_time` internally (D-11).

### E-12: Single-Scene Manifests
A manifest with one scene is valid. No transition adjacency issues (crossfade checks don't apply to middle-position transitions since there's only first=last). The scene's `transition_in` and `transition_out` follow D-10 rules for both first and last scene.

## Test Strategy

### Unit Tests (`test/unit/manifest/`)

**`schema.test.ts` — Structural validation:**
1. Parse seed Section 4.6 example manifest — succeeds.
2. Parse with each optional field omitted — succeeds with defaults.
3. Parse with each required field removed — fails naming the field.
4. Parse with wrong types (`duration: "eight"`) — fails.
5. Boundary values: `duration: 0.001` (passes), `duration: 0` (fails), `fps: 1` (passes), `fps: 121` (fails), `fps: 23.976` (fails).
6. `.strict()` rejects unknown keys on SceneSchema, CompositionSchema, PlaneRefSchema.
7. `TransitionSchema` superRefine: `crossfade` with `duration: 0` fails; `cut` with `duration: 1.0` passes.
8. FOV bounds: 9 (fails), 10 (passes), 120 (passes), 121 (fails).
9. Default values: opacity→1.0, scale→1.0, volume→1.0, easing→"ease_in_out", speed→1.0.
10. `dip_to_black` with `duration: 0` fails (requires >0).

**`loader.test.ts` — Semantic validation:**
1. Register mock `tunnel` geometry + `tunnel_push_forward` camera. Validate matching manifest → succeeds.
2. Unregistered geometry → `UNKNOWN_GEOMETRY`.
3. Missing required slot → `MISSING_REQUIRED_SLOT` naming the slot.
4. Extra unknown slot → `UNKNOWN_SLOT` listing valid slot names.
5. Incompatible camera (not in geometry's `compatibleCameras`) → `INCOMPATIBLE_CAMERA`.
6. Duplicate scene IDs → `DUPLICATE_SCENE_ID`.
7. Overlapping scenes without transitions → `SCENE_OVERLAP`.
8. Overlapping scenes WITH valid transitions (overlap ≤ min durations) → succeeds.
9. Overlapping scenes where overlap > transition duration → `SCENE_OVERLAP`.
10. Audio with `duration` that mismatches scene total → warning `AUDIO_DURATION_MISMATCH`, still `success: true`.
11. Audio without `duration` field + mismatched scenes → no warning (check skipped).
12. Empty registry → `UNKNOWN_GEOMETRY` with helpful suggestion message.
13. Scene gap → `SCENE_GAP` warning.
14. Array order disagrees with `start_time` → `SCENE_ORDER_MISMATCH` warning.
15. `crossfade` as `transition_in` on first scene → `CROSSFADE_NO_ADJACENT`.
16. `crossfade` as `transition_out` on last scene → `CROSSFADE_NO_ADJACENT`.
17. `dip_to_black` as `transition_in` on first scene → allowed.
18. `fov_start` set but camera's `supportsFovAnimation` is false → `FOV_WITHOUT_SUPPORT` warning.
19. `computeTotalDuration()` with overlapping scenes returns correct max.

**`registry.test.ts`:**
1. `createRegistry()` returns empty maps.
2. `registerGeometry()` adds retrievable geometry.
3. `registerCamera()` adds retrievable camera.
4. Re-registering with same name overwrites (no error).

**`loader-file.test.ts`:**
1. Valid JSON fixture → succeeds.
2. Nonexistent path → `FILE_NOT_FOUND`.
3. Invalid JSON content → `INVALID_JSON`.

**Relevant testable claims:** TC-04 (verified indirectly — schema accepts geometry names + slot keys without coordinates), TC-07 (directly — 20+ error scenarios above).

### Integration Test
`test/integration/manifest-roundtrip.test.ts`: Load complete manifest JSON from `test/fixtures/valid-manifest.json`, register mock geometries/cameras, validate via `loadManifestFromFile()`, assert success. Fixture matches seed Section 4.6 example.

## Integration Points

### Depends on
- **OBJ-001** (Project Scaffolding): Provides `src/manifest/schema.ts` and `src/manifest/loader.ts` stubs, `zod` in dependencies, TypeScript build config, vitest runner.

### Consumed by
- **OBJ-005** (Scene Geometry Base): Imports `GeometryRegistration`, `PlaneSlotDef`, `ManifestRegistry` to register geometries.
- **OBJ-006** (Camera Path Presets): Imports `CameraRegistration`, `ManifestRegistry` to register cameras.
- **OBJ-010** (Frame Clock): Imports `Manifest`, `Scene`, `computeTotalDuration()` for timing.
- **OBJ-013** (CLI): Imports `loadManifestFromFile()`, `createRegistry()`.
- **OBJ-016** (Audio Muxing): Imports `Audio`, `Manifest` types.
- **OBJ-017** (Texture Loading): Imports `PlaneRef` type.
- **OBJ-035** (Orchestrator): Imports `loadManifest()` as pre-render entry point.
- **OBJ-044, OBJ-045** (Position/rotation overrides): Import `PlaneRef` with `position_override`/`rotation_override`.
- **OBJ-056, OBJ-070** (SKILL.md): Document manifest schema as authoring interface.

### File Placement
- `src/manifest/schema.ts` — Zod schemas, types, registry interfaces, `createRegistry()`.
- `src/manifest/loader.ts` — `parseManifest()`, `validateManifestSemantics()`, `loadManifest()`, `loadManifestFromFile()`, `computeTotalDuration()`.
- `test/unit/manifest/schema.test.ts`
- `test/unit/manifest/loader.test.ts`
- `test/unit/manifest/registry.test.ts`
- `test/unit/manifest/loader-file.test.ts`
- `test/fixtures/valid-manifest.json`

## Open Questions

### OQ-A: Should the Manifest Support HUD Layers?
Deferred to a later objective. If added, a `hud_layers` field on `SceneSchema` is cleaner than overloading `planes`.

### OQ-B: Should the Schema Support Scene Weights for Audio-Proportional Duration?
Deferred. The manifest generator computes durations from audio length before emitting the manifest.

---

I believe this revision addresses all 14 issues raised:

- **CRITICAL-1:** `severity` in canonical `ManifestError` interface from the start ✓
- **CRITICAL-2:** `SCENE_GAP` in error codes table ✓
- **CRITICAL-3:** D-03 explicitly defines geometry's `compatibleCameras` as authoritative ✓
- **CRITICAL-4:** Optional `duration` on `AudioSchema`, check skipped when absent ✓
- **MAJOR-1:** E-03 defines precise overlap calculation with all conditions ✓
- **MAJOR-2:** D-10: `cut` accepts any duration, ignored; superRefine only for non-cut types ✓
- **MAJOR-3:** D-12: `z.number().int().min(1).max(120)` ✓
- **MAJOR-4:** Transition semantics block defines dip_to_black for in/out ✓
- **MAJOR-5:** D-15 + `computeTotalDuration()` export ✓
- **MAJOR-6:** PlaneRefSchema added to `.strict()` list in D-14/E-02 ✓
- **MINOR-1:** Metadata comment in ManifestSchema shape ✓
- **MINOR-2:** Promoted to D-11 + `SCENE_ORDER_MISMATCH` in error codes ✓
- **MINOR-3:** FOV check logic described, AC-28 added ✓
- **MINOR-4:** Scope boundary section explicitly states file existence is out of scope ✓

Challenger, please verify and approve if satisfied.

---

## Round 4 — spec_challenger

I'll verify each fix systematically against the revised spec.

**CRITICAL-1 (severity field):** ✓ Verified — `ManifestError` interface now has `severity: "error" | "warning"` in the canonical definition. `ManifestResult` success case includes `warnings: ManifestError[]`.

**CRITICAL-2 (SCENE_GAP):** ✓ Verified — present in error codes table with severity `warning`.

**CRITICAL-3 (compatibility direction):** ✓ Verified — D-03 explicitly states geometry's `compatibleCameras` is authoritative. Camera's `compatibleGeometries` is "informational only — NOT used for validation."

**CRITICAL-4 (audio duration source):** ✓ Verified — `AudioSchema` has `duration: z.number().positive().optional()`. D-07 says check skipped when absent. AC-26 tests the warning case.

**MAJOR-1 (overlap logic):** ✓ Verified — E-03 has precise 4-step rules with all conditions enumerated. The conjunction requirement (all three sub-conditions) is explicit.

**MAJOR-2 (cut/duration):** ✓ Verified — D-10 says `cut` accepts any duration, ignored. SuperRefine only for `crossfade` and `dip_to_black`. AC-10 tests `cut` with `duration: 1.0` passes.

**MAJOR-3 (fps bounds):** ✓ Verified — D-12 specifies `z.number().int().min(1).max(120)`. AC-05 tests `fps: 121` and `fps: 23.976` rejection.

**MAJOR-4 (dip_to_black semantics):** ✓ Verified — Transition semantics block explicitly defines each combination.

**MAJOR-5 (total duration):** ✓ Verified — D-15 defines formula. `computeTotalDuration()` exported from loader. AC-32 tests it.

**MAJOR-6 (PlaneRef strictness):** ✓ Verified — D-14 lists `PlaneRefSchema` in the `.strict()` set. AC-15 tests it.

**MINOR-1 (metadata docs):** ✓ Verified — comment in ManifestSchema shape.

**MINOR-2 (order mismatch promotion):** ✓ Verified — D-11 as design decision. `SCENE_ORDER_MISMATCH` in error codes table. AC-25 tests it.

**MINOR-3 (FOV check logic):** ✓ Verified — AC-28 tests it. Error codes table has `FOV_WITHOUT_SUPPORT`.

**MINOR-4 (file existence scope):** ✓ Verified — "Scope Boundary: File Existence" section is explicit.

All 14 original issues are structurally resolved. Now let me check for new issues introduced by the revisions.

---

**One new issue found:**

**MINOR-5: `SCENE_ORDER_MISMATCH` detection is underspecified for equal `start_time` values**

If two scenes have the same `start_time`, should the validator emit `SCENE_ORDER_MISMATCH` if they're in one array order vs another? The overlap check (E-03) would fire for these since `overlap = max(0, A.duration)` which is positive. So the overlap check handles the semantic problem. But the order check is ambiguous — with equal `start_time`, any array order is "consistent."

This is genuinely minor — the overlap check catches the real problem. No fix needed; just noting it for completeness.

**One clarification worth noting but not blocking:**

The `SCENE_OVERLAP` error in E-03 step 4 says to name "what's missing" in the message. This is good guidance for implementers but doesn't need further spec precision — the AC already requires actionable messages (AC-34).

---

The spec is thorough, precise, and implementable. Every interface is typed. Every error code has a trigger condition and severity. The acceptance criteria are specific and testable. The scope stays within OBJ-004's boundaries. The vocabulary matches the seed. The registry pattern cleanly supports downstream extensibility.

Let me write the conclusion.

CONCLUSION:

The specification for OBJ-004 is approved. All 14 issues from Round 2 (4 critical, 6 major, 4 minor) have been verified as structurally resolved in the revision. The two-phase validation approach (Zod structural + registry-backed semantic) is sound and extensible. The registry interface cleanly supports downstream geometry/camera registration. Error codes are exhaustive with severity levels. Edge cases around scene timing, transitions, and audio are precisely defined.

Let me write the final spec to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me read the existing meta.json before updating it.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-004",
     3→  "description": "Manifest schema core -- Zod schema for the top-level manifest structure: composition settings (width, height, fps, audio), scenes array (id, duration, start_time, geometry, camera, camera_params, transition_in, transition_out, planes), and global metadata per Section 4.6. Covers C-04 (resolution/fps support for 1920x1080, 1080x1920, 24fps, 30fps) and C-10 (validation before rendering). Defines the contract between LLM manifest authors and the rendering engine.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. The most critical contract -- defines the authoring interface."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "content": "# Specification: OBJ-004 \u2014 Manifest Schema Core\n\n## Summary\n\nOBJ-004 defines the Zod validation schema and loader for the depthkit manifest \u2014 the declarative JSON document that describes an entire video. This is the authoring contract between LLM manifest authors and the rendering engine. The schema enforces structural correctness (types, ranges, required fields) via Zod parsing and semantic correctness (geometry existence, camera compatibility, plane-slot matching) via a registry-backed validation pass. It satisfies C-04 (resolution/fps support) and C-10 (validate before rendering, fail fast with actionable errors).\n\n## Interface Contract\n\n### Module: `src/manifest/schema.ts`\n\nExports Zod schemas, inferred TypeScript types, and the registry interfaces that downstream geometry/camera objectives use to register their definitions.\n\n```typescript\n// === Registry Interfaces ===\n\n/**\n * Describes a single plane slot within a scene geometry.\n * Populated by OBJ-005 (geometry base) and OBJ-018-025 (individual geometries).\n */\nexport interface PlaneSlotDef {\n  required: boolean;\n  description: string;\n}\n\n/**\n * A registered scene geometry definition. Contains enough metadata\n * for manifest validation (slot names, compatible cameras).\n * Does NOT contain 3D spatial data (positions, rotations) \u2014 that\n * lives in OBJ-005's geometry implementations.\n */\nexport interface GeometryRegistration {\n  name: string;\n  slots: Record<string, PlaneSlotDef>;\n  compatibleCameras: string[];\n  defaultCamera: string;\n}\n\n/**\n * A registered camera path definition. Contains enough metadata\n * for manifest validation (compatible geometries, FOV support).\n */\nexport interface CameraRegistration {\n  name: string;\n  compatibleGeometries: string[];  // Informational only \u2014 NOT used for validation (see D-03)\n  su
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/meta.json",
  "content": "{\n  \"id\": \"OBJ-004\",\n  \"description\": \"Manifest schema core -- Zod schema for the top-level manifest structure: composition settings (width, height, fps, audio), scenes array (id, duration, start_time, geometry, camera, camera_params, transition_in, transition_out, planes), and global metadata per Section 4.6. Covers C-04 (resolution/fps support for 1920x1080, 1080x1920, 24fps, 30fps) and C-10 (validation before rendering). Defines the contract between LLM manifest authors and the rendering engine.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T01:30:00Z\",\n  \"depends_on\": [\"OBJ-001\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 1 contract. The most critical contract -- defines the authoring interface. Spec approved after 4-round deliberation. Two-phase validation (Zod structural + registry-backed semantic). 14 error codes with severity levels. 34 acceptance criteria.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/meta.json has been updated successfully.
Now let me commit these files.
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
[Tool Result] 90a2c38 spec(OBJ-002): interpolation, easing, and spring utilities
28fe944 spec(OBJ-001): Project scaffolding and build system specification
fb3e4b3 spec(OBJ-003): Coordinate system and spatial math reference
76f7b6b Initialize DAG decomposition: 83 objectives across 7 dependency tiers
f5f8c11 Initial project setup
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-004/meta.json
	modified:   nodes/OBJ-007/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/transcript.md
	nodes/OBJ-002/transcript.md
	nodes/OBJ-003/transcript.md
	nodes/OBJ-004/output.md
	nodes/OBJ-007/output.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-004/output.md nodes/OBJ-004/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-004): Manifest schema core \u2014 Zod validation and registry contract\n\nDefine the two-phase validation pipeline (Zod structural + registry-backed\nsemantic) for depthkit manifests. Covers composition settings, scenes array,\nplane references, transitions, camera params, and 14 error codes with\nseverity levels. Satisfies C-04 (resolution/fps) and C-10 (fail-fast\nvalidation). 34 acceptance criteria across structural and semantic checks.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-004 spec files"
}
[Tool Result] [master dc13dd4] spec(OBJ-004): Manifest schema core — Zod validation and registry contract
 2 files changed, 552 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-004/output.md
The specification for OBJ-004 has been written to disk and committed. 

**Deliberation summary:** The spec went through 4 rounds. Round 1 produced a strong initial proposal. Round 2 identified 14 issues (4 critical, 6 major, 4 minor). Round 3 addressed all 14. Round 4 verified each fix structurally and found no remaining blockers.

**Key design decisions in the final spec:**
- Two-phase validation: Zod structural parsing + registry-backed semantic checks
- Registry pattern decouples schema from geometry/camera implementations
- Geometry's `compatibleCameras` is the single authoritative source for compatibility checks
- Optional `audio.duration` field enables mismatch warnings without file I/O
- Integer fps with [1, 120] bounds
- `.strict()` on all sub-schemas (including `PlaneRefSchema`) to catch LLM author typos
- 14 error codes with explicit severity (`error` vs `warning`)
- `computeTotalDuration()` exported as `max(start_time + duration)` across all scenes
- Precise overlap validation rules with all edge cases enumerated
