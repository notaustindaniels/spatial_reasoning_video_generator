# Specification: OBJ-004 — Manifest Schema Core

## Summary

OBJ-004 defines the Zod validation schema and loader for the depthkit manifest — the declarative JSON document that describes an entire video. This is the authoring contract between LLM manifest authors and the rendering engine. The schema enforces structural correctness (types, ranges, required fields) via Zod parsing and semantic correctness (geometry existence, camera compatibility, plane-slot matching) via a registry-backed validation pass. It satisfies C-04 (resolution/fps support) and C-10 (validate before rendering, fail fast with actionable errors).

## Interface Contract

### Module: `src/manifest/schema.ts`

Exports Zod schemas, inferred TypeScript types, and the registry interfaces that downstream geometry/camera objectives use to register their definitions.

```typescript
// === Registry Interfaces ===

/**
 * Describes a single plane slot within a scene geometry.
 * Populated by OBJ-005 (geometry base) and OBJ-018-025 (individual geometries).
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
 * for manifest validation (compatible geometries, FOV support).
 */
export interface CameraRegistration {
  name: string;
  compatibleGeometries: string[];  // Informational only — NOT used for validation (see D-03)
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

// === Validation Types ===

/**
 * A single validation error with an actionable message.
 */
export interface ManifestError {
  path: string;        // Dot-notation path (e.g., "scenes[0].planes.floor.src")
  code: string;        // Machine-readable error code (see Error Codes table)
  message: string;     // Human-readable, actionable description
  severity: "error" | "warning";
}

/**
 * The result of manifest validation. Discriminated union:
 * success=true means `manifest` is populated (may still carry warnings);
 * success=false means `errors` is populated.
 */
export type ManifestResult =
  | { success: true; manifest: Manifest; warnings: ManifestError[] }
  | { success: false; errors: ManifestError[] };

// === Zod Schemas ===

/** Audio configuration */
export const AudioSchema: z.ZodType;
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
  duration: z.number().positive().optional(),        // Seconds. When present, enables AUDIO_DURATION_MISMATCH check.
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
Note: C-04 requires support for 1920x1080, 1080x1920, 24fps, 30fps — but the schema does NOT restrict to only those values. It accepts any positive integer dimensions and any integer fps in [1, 120]. The constraint is that those four combinations *must work*; others may also work.

**TransitionSchema** (`.strict()`):
```typescript
{
  type: z.enum(["cut", "crossfade", "dip_to_black"]),
  duration: z.number().nonnegative().default(0),   // seconds
}
```
Refinement via `.superRefine()`: if `type` is `"crossfade"` or `"dip_to_black"`, `duration` must be > 0. If `type` is `"cut"`, any `duration` value is accepted but ignored by the engine (defaults to 0).

**Transition semantics** (for downstream OBJ-015 scene sequencer):
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
  src: z.string().min(1),                           // Path/URL to image file
  opacity: z.number().min(0).max(1).default(1.0),   // Static initial opacity
  position_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [x, y, z] — AP-08 escape hatch
  rotation_override: z.tuple([z.number(), z.number(), z.number()]).optional(),  // [rx, ry, rz] — AP-08 escape hatch
  scale: z.number().positive().default(1.0),         // Uniform scale multiplier
}
```
The `position_override` and `rotation_override` fields exist per AP-08 (do not hard-code the depth model). They are optional escape hatches — never the primary authoring method (AP-03).

**SceneSchema** (`.strict()`):
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

**ManifestSchema** (`.passthrough()` at top level):
```typescript
{
  version: z.literal("3.0"),
  composition: CompositionSchema,
  scenes: z.array(SceneSchema).min(1),               // At least one scene
  metadata: z.record(z.string(), z.unknown()).optional(),
    // Arbitrary key-value metadata for pipeline integration (e.g., job ID, topic, style).
    // Ignored by the rendering engine. Passed through for downstream consumers.
}
```

### Module: `src/manifest/loader.ts`

```typescript
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
 * plane keys match geometry slots, required slots present, scene timing consistency,
 * transition adjacency, FOV support.
 * Returns an array of ManifestErrors (empty = valid).
 */
export function validateManifestSemantics(
  manifest: Manifest,
  registry: ManifestRegistry,
): ManifestError[];

/**
 * Full validation pipeline: parse + semantic validation.
 * This is the primary entry point for consumers.
 * If structural validation fails, semantic validation is skipped.
 */
export function loadManifest(
  raw: unknown,
  registry: ManifestRegistry,
): ManifestResult;

/**
 * Convenience: load from a file path. Reads JSON, then calls loadManifest().
 * Returns FILE_NOT_FOUND or INVALID_JSON errors for file-level failures.
 */
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
| `CROSSFADE_NO_ADJACENT` | error | `transition_in: crossfade` on the first scene (no preceding scene) or `transition_out: crossfade` on the last scene (no following scene) |
| `SCENE_GAP` | warning | Two consecutive scenes (by `start_time` order) have a time gap between them |
| `SCENE_ORDER_MISMATCH` | warning | Scenes in the array are not ordered by ascending `start_time` |
| `AUDIO_DURATION_MISMATCH` | warning | `audio.duration` is present and differs from `computeTotalDuration()` |
| `FOV_WITHOUT_SUPPORT` | warning | `camera_params.fov_start` or `fov_end` is set but the camera's `supportsFovAnimation` is false |
| `INVALID_JSON` | error | File exists but is not valid JSON (for `loadManifestFromFile`) |
| `FILE_NOT_FOUND` | error | File path does not exist (for `loadManifestFromFile`) |

### Scope Boundary: File Existence

File existence validation for `src` paths (images, audio) is NOT part of manifest validation. The orchestrator (OBJ-035) resolves and validates file paths at render time. The manifest schema validates only that `src` is a non-empty string.

## Design Decisions

### D-01: Two-Phase Validation (Structural + Semantic)

**Choice:** Validation is split: Zod structural parsing (Phase 1) and registry-backed semantic validation (Phase 2).

**Rationale:** Zod validates types, shapes, and value ranges statically. Geometry names, camera names, compatibility, and plane-slot matching depend on runtime registrations from OBJ-005, OBJ-006, OBJ-018-025, and OBJ-026-034. Separating phases means OBJ-004 defines the registry *interface* without depending on specific registrations.

**Alternative rejected:** A single Zod `.refine()` hardcoding known geometry names — creates circular dependency and requires modifying `schema.ts` for every new geometry.

### D-02: Registry Pattern for Extensibility

**Choice:** A `ManifestRegistry` with `registerGeometry()` and `registerCamera()`. The loader accepts a registry as a parameter.

**Rationale:** Decouples schema from implementations. If the registry is empty when `loadManifest()` is called, every scene produces `UNKNOWN_GEOMETRY`/`UNKNOWN_CAMERA` errors. Error messages should suggest: "Did you forget to register geometries? Ensure geometry modules are imported before validation."

### D-03: Geometry's `compatibleCameras` Is Authoritative for Validation

**Choice:** The `INCOMPATIBLE_CAMERA` check uses the geometry's `compatibleCameras` list as the single source of truth. If `scene.camera` is not in `registry.geometries.get(scene.geometry).compatibleCameras`, it is incompatible.

The camera's `compatibleGeometries` field is informational metadata for SKILL.md authoring guidance and documentation only. The semantic validator does NOT cross-check it.

**Rationale:** The seed Section 8.6 defines `compatible_cameras` on the geometry as the primary contract. Using a single authoritative direction eliminates ambiguity when the two lists disagree.

### D-04: `start_time` Is Explicit, Not Computed

**Choice:** Each scene has an explicit `start_time` field (seconds), not auto-computed from prior durations.

**Rationale:** Seed Section 4.6 example shows `start_time` on each scene. Explicit start times support overlapping transitions (scene 1 ends at 8.5s, scene 2 starts at 8.0s — 0.5s overlap).

### D-05: `version` as Literal `"3.0"`

**Choice:** `z.literal("3.0")`.

**Rationale:** Seed Section 4.6 shows `"version": "3.0"`. String literal enables future version dispatch.

### D-06: Easing Names Match Seed Vocabulary

**Choice:** Enum uses exact seed Section 2 names: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`.

**Rationale:** AP-06 compliance (do not invent new terminology).

### D-07: Audio Duration Mismatch Is a Warning, Not a Hard Error

**Choice:** When `audio.duration` is present on the manifest and the total scene duration (computed via `computeTotalDuration()`) differs, emit `AUDIO_DURATION_MISMATCH` as a warning. `loadManifest()` still returns `success: true`.

**Rationale:** Seed Section 8.7: "if both audio and explicit durations: explicit durations are used, but the engine warns." The `duration` field on `AudioSchema` is optional — if the manifest generator doesn't provide it, the check is skipped entirely. Audio file reading/probing is a render-time concern (OBJ-035), not a validation concern.

### D-08: PlaneRef Includes `opacity` and `scale`

**Choice:** Static `opacity` (default 1.0) and `scale` (default 1.0) on `PlaneRefSchema`.

**Rationale:** Enables simple use cases (semi-transparent fog overlay) without schema migration. Per-frame animation is a separate concern for a later objective. Static values cost nothing in schema complexity.

### D-09: Scene ID Uniqueness Enforced

**Choice:** Duplicate `id` values produce `DUPLICATE_SCENE_ID` error.

**Rationale:** Scene IDs are referenced by the scene sequencer and potentially by transitions. Duplicate IDs would create ambiguity.

### D-10: Transition Validation Rules

**Choice:** `crossfade` requires an adjacent scene to blend with. `dip_to_black` and `cut` work on any scene.

Specifically:
- First scene's `transition_in`: `crossfade` produces `CROSSFADE_NO_ADJACENT` error. `dip_to_black` and `cut` are allowed.
- Last scene's `transition_out`: `crossfade` produces `CROSSFADE_NO_ADJACENT` error. `dip_to_black` and `cut` are allowed.
- For `type: "cut"`, any provided `duration` is accepted and ignored (defaults to 0). No superRefine rejection.
- For `type: "crossfade"` or `"dip_to_black"`, `duration` must be > 0 (enforced via superRefine).

### D-11: `start_time` Is Authoritative; Array Order Disagreement Is a Warning

**Choice:** `start_time` is the authoritative timestamp for scene ordering. The engine sorts scenes by `start_time` internally. If the array order disagrees with `start_time` order, emit `SCENE_ORDER_MISMATCH` warning. This is not an error — the manifest is valid.

### D-12: Integer FPS with Practical Bounds

**Choice:** `fps: z.number().int().min(1).max(120)`.

**Rationale:** The seed only mentions integer fps (24, 30). Integer fps simplifies frame-clock math (OBJ-010). The 1-120 range excludes impractical values while allowing common rates (24, 25, 30, 48, 60). Fractional fps (23.976 NTSC) is out of scope for V1.

### D-13: `planes` as Open Record with Semantic Slot Validation

**Choice:** `planes` is `z.record(z.string(), PlaneRefSchema)`. Keys validated against geometry slots in semantic pass.

**Rationale:** Each geometry defines different slot names. An open record + semantic validation is the only approach supporting extensible geometries without circular dependencies.

### D-14: Strict Sub-Schemas, Passthrough Top-Level

**Choice:** `.strict()` on `SceneSchema`, `CompositionSchema`, `TransitionSchema`, `CameraParamsSchema`, and `PlaneRefSchema`. `.passthrough()` on top-level `ManifestSchema`.

**Rationale:** Strict sub-schemas catch LLM author typos (e.g., `durration`, `opactiy`). Passthrough at top level allows forward-compatible metadata and top-level fields.

### D-15: Total Video Duration Computation

**Choice:** Total video duration = `max across all scenes of (start_time + duration)`. Exported as `computeTotalDuration()`.

**Rationale:** Accounts for overlapping and non-sequential scenes. Simple, unambiguous formula.

## Acceptance Criteria

- [ ] **AC-01:** `ManifestSchema` parses a valid manifest matching seed Section 4.6's example and returns the typed `Manifest` object.
- [ ] **AC-02:** `ManifestSchema` rejects a manifest missing `version`, `composition`, or `scenes` with Zod errors naming the missing field.
- [ ] **AC-03:** `ManifestSchema` rejects `version: "2.0"` and `version: "4.0"` — only `"3.0"` accepted.
- [ ] **AC-04:** `CompositionSchema` accepts `{width: 1920, height: 1080, fps: 30}` and `{width: 1080, height: 1920, fps: 24}` (C-04 baseline). Also accepts other valid combinations.
- [ ] **AC-05:** `CompositionSchema` rejects `width: 0`, `height: -1`, `fps: 0`, `fps: 121`, `fps: 23.976` (non-integer), `width: 1920.5` (non-integer).
- [ ] **AC-06:** `SceneSchema` rejects `duration: 0` and `duration: -5`.
- [ ] **AC-07:** `SceneSchema` rejects `start_time: -1`. Accepts `start_time: 0`.
- [ ] **AC-08:** `TransitionSchema` rejects `type: "wipe"`. Accepts `"cut"`, `"crossfade"`, `"dip_to_black"`.
- [ ] **AC-09:** `TransitionSchema` with `type: "crossfade"` rejects `duration: 0` and `duration: -1`. Accepts `duration: 0.5`. Same rules for `type: "dip_to_black"`.
- [ ] **AC-10:** `TransitionSchema` with `type: "cut"` accepts `duration: 1.0` without error (value is ignored).
- [ ] **AC-11:** `CameraParamsSchema` rejects `fov_start: 5` (below 10) and `fov_start: 130` (above 120).
- [ ] **AC-12:** `PlaneRefSchema` defaults `opacity` to 1.0 and `scale` to 1.0 when not provided.
- [ ] **AC-13:** Scene `id` rejects `"scene 001"` (spaces) and `""` (empty). Accepts `"scene_001"` and `"s1"`.
- [ ] **AC-14:** `ManifestSchema` rejects `scenes: []` (at least one scene required).
- [ ] **AC-15:** `PlaneRefSchema` rejects unknown keys (e.g., `{src: "x.png", opactiy: 0.5}` produces Zod error on `opactiy`).
- [ ] **AC-16:** `SceneSchema` rejects unknown keys (e.g., `{id: "s1", ..., durration: 5}` produces Zod error on `durration`).
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
- [ ] **AC-29:** `loadManifest()` runs both phases, returns single `ManifestResult`. Structural failure returns Zod errors mapped to `ManifestError` format; semantic validation is skipped.
- [ ] **AC-30:** `loadManifestFromFile()` returns `FILE_NOT_FOUND` for a nonexistent path and `INVALID_JSON` for invalid JSON content.
- [ ] **AC-31:** `createRegistry()` returns a fresh registry with empty maps.
- [ ] **AC-32:** `computeTotalDuration()` returns `max(start_time + duration)` across all scenes.
- [ ] **AC-33:** All exported types (`Manifest`, `Scene`, `Composition`, `Audio`, `Transition`, `CameraParams`, `PlaneRef`, `ManifestError`, `ManifestResult`, `ManifestRegistry`, `GeometryRegistration`, `CameraRegistration`, `PlaneSlotDef`) are importable by downstream objectives.
- [ ] **AC-34:** Every `ManifestError` has non-empty `path`, `code`, `message`, and `severity`. No generic messages — all are actionable (they name the specific field/value that caused the failure).

## Edge Cases and Error Handling

### E-01: Empty `planes` Object
`planes: {}` passes Zod structural validation. Semantic validation produces `MISSING_REQUIRED_SLOT` for each required slot in the geometry.

### E-02: Extra Fields on Strict Sub-Schemas
`.strict()` on `SceneSchema`, `CompositionSchema`, `TransitionSchema`, `CameraParamsSchema`, and `PlaneRefSchema` causes Zod to reject unrecognized keys with an error naming the key. `.passthrough()` on top-level `ManifestSchema` allows forward-compatible top-level fields.

### E-03: Overlapping Scenes — Precise Rules

Scenes are sorted by `start_time` for overlap analysis. For each consecutive pair (A, B) in sorted order:

1. **Compute overlap:** `overlap = max(0, (A.start_time + A.duration) - B.start_time)`
2. **If overlap == 0:** No overlap. Check for gap (E-04).
3. **If overlap > 0:** The overlap is valid if and only if ALL of:
   - `A.transition_out` exists and its `type` is not `"cut"`
   - `B.transition_in` exists and its `type` is not `"cut"`
   - `overlap <= min(A.transition_out.duration, B.transition_in.duration)`
4. If condition 3 is not fully met, emit `SCENE_OVERLAP` error naming scenes A and B, the overlap duration, and what's missing (e.g., "Scene 'scene_001' and 'scene_002' overlap by 0.5s but scene_001 has no transition_out").

### E-04: Scenes With Gaps
For consecutive scenes (sorted by `start_time`) where `B.start_time > A.start_time + A.duration`, emit `SCENE_GAP` warning. Gap = `B.start_time - (A.start_time + A.duration)`. The engine renders black frames during gaps.

### E-05: `audio.volume` Out of Range
Zod enforces `0 <= volume <= 2`. The range allows boost (>1) via FFmpeg audio filters.

### E-06: `fov_start` Without `fov_end` (or Vice Versa)
Not a semantic error. The engine interprets a missing value as "use the camera's default FOV" for that end. Allows setting just `fov_end` to animate from default to a target.

### E-07: Registry With No Registrations
All scenes produce `UNKNOWN_GEOMETRY` and `UNKNOWN_CAMERA`. Error messages include: "Did you forget to register geometries? Ensure geometry modules are imported before validation."

### E-08: Very Large Scene Counts
No hardcoded limit on scene count. A 500-scene manifest is valid if individually valid. Performance is the orchestrator's concern.

### E-09: `position_override` and `rotation_override` Values
Accept any finite number triples. No range restriction — values are in world units/radians and depend on geometry context. Out-of-frustum placements are the engine's concern at render time.

### E-10: Audio-Driven Timing
The schema requires `duration > 0` on every scene. Audio-proportional timing is computed by the manifest *generator* before emitting the manifest. The schema always receives resolved durations.

### E-11: `start_time` Disagrees With Array Order
Warning `SCENE_ORDER_MISMATCH`, not an error. Engine sorts by `start_time` internally (D-11).

### E-12: Single-Scene Manifests
A manifest with one scene is valid. The scene is simultaneously the first and last scene. Its `transition_in` and `transition_out` follow D-10 rules for both first and last positions (crossfade is rejected on both sides via `CROSSFADE_NO_ADJACENT`; `dip_to_black` and `cut` are allowed).

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
9. Default values: opacity -> 1.0, scale -> 1.0, volume -> 1.0, easing -> "ease_in_out", speed -> 1.0.
10. `dip_to_black` with `duration: 0` fails (requires > 0).

**`loader.test.ts` — Semantic validation:**
1. Register mock `tunnel` geometry + `tunnel_push_forward` camera. Validate matching manifest — succeeds.
2. Unregistered geometry -> `UNKNOWN_GEOMETRY`.
3. Missing required slot -> `MISSING_REQUIRED_SLOT` naming the slot.
4. Extra unknown slot -> `UNKNOWN_SLOT` listing valid slot names.
5. Incompatible camera (not in geometry's `compatibleCameras`) -> `INCOMPATIBLE_CAMERA`.
6. Duplicate scene IDs -> `DUPLICATE_SCENE_ID`.
7. Overlapping scenes without transitions -> `SCENE_OVERLAP`.
8. Overlapping scenes WITH valid transitions (overlap <= min durations) -> succeeds.
9. Overlapping scenes where overlap > transition duration -> `SCENE_OVERLAP`.
10. Audio with `duration` that mismatches scene total -> warning `AUDIO_DURATION_MISMATCH`, still `success: true`.
11. Audio without `duration` field + mismatched scenes -> no warning (check skipped).
12. Empty registry -> `UNKNOWN_GEOMETRY` with helpful suggestion message.
13. Scene gap -> `SCENE_GAP` warning.
14. Array order disagrees with `start_time` -> `SCENE_ORDER_MISMATCH` warning.
15. `crossfade` as `transition_in` on first scene -> `CROSSFADE_NO_ADJACENT`.
16. `crossfade` as `transition_out` on last scene -> `CROSSFADE_NO_ADJACENT`.
17. `dip_to_black` as `transition_in` on first scene -> allowed.
18. `fov_start` set but camera's `supportsFovAnimation` is false -> `FOV_WITHOUT_SUPPORT` warning.
19. `computeTotalDuration()` with overlapping scenes returns correct max.

**`registry.test.ts`:**
1. `createRegistry()` returns empty maps.
2. `registerGeometry()` adds retrievable geometry.
3. `registerCamera()` adds retrievable camera.
4. Re-registering with same name overwrites (no error).

**`loader-file.test.ts`:**
1. Valid JSON fixture -> succeeds.
2. Nonexistent path -> `FILE_NOT_FOUND`.
3. Invalid JSON content -> `INVALID_JSON`.

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
- `test/unit/manifest/schema.test.ts` — Structural validation tests.
- `test/unit/manifest/loader.test.ts` — Semantic validation and `computeTotalDuration()` tests.
- `test/unit/manifest/registry.test.ts` — Registry tests.
- `test/unit/manifest/loader-file.test.ts` — File loading tests.
- `test/fixtures/valid-manifest.json` — A complete valid manifest matching seed Section 4.6.

## Open Questions

### OQ-A: Should the Manifest Support HUD Layers?
Deferred to a later objective. If added, a `hud_layers` field on `SceneSchema` would be cleaner than overloading `planes`.

### OQ-B: Should the Schema Support Scene Weights for Audio-Proportional Duration?
Deferred. The manifest generator computes durations from audio length before emitting the manifest. The schema always receives resolved durations.
