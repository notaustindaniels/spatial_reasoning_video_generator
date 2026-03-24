# Deliberation Transcript: OBJ-016

---

## Round 1 — spec_author

Looking at OBJ-016's description and its dependency on OBJ-004, I need to understand the boundary. OBJ-004 defined the Zod schemas, registry interfaces, and function signatures. OBJ-016 specifies the **implementation behavior** of the loader: how Zod errors map to `ManifestError`, how errors are collected all-at-once, how actionable messages are formatted, how file I/O works, and how the fail-fast contract (C-10) is enforced.

Let me first check the current state of the codebase to understand what already exists.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]

[Tool: Glob]
  Input: {
  "pattern": "src/manifest/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-016/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-004/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/transcript.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-016",
     3→  "description": "Manifest loader and validator -- JSON parsing, Zod schema validation execution, error collection with actionable messages (file paths, field names, expected vs actual values), fail-fast behavior per C-10 (invalid manifests never produce partial output). Reports all validation errors at once rather than one-at-a-time.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-004"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Applies the schema from OBJ-004 to actual manifest files. Covers TC-07 (validation catches errors)."
    12→}
    13→
Good. Now I have full context. Let me propose the specification for OBJ-016.

---

# Specification Proposal: OBJ-016 — Manifest Loader and Validator

## Summary

OBJ-016 implements the manifest loading and validation pipeline defined by OBJ-004's interface contracts. It specifies how raw JSON is parsed through the two-phase validation pipeline (structural Zod parsing → semantic registry validation), how Zod errors are mapped to actionable `ManifestError` objects, how all errors are collected at once (not one-at-a-time), how file I/O works for `loadManifestFromFile()`, and how the fail-fast contract (C-10) is enforced: invalid manifests never produce partial output. This is the concrete behavioral specification that a code agent needs to implement `src/manifest/loader.ts`.

## Interface Contract

OBJ-004 already defined the function signatures. OBJ-016 specifies the **behavioral contracts** of those functions and introduces one internal helper type not exposed publicly.

### Module: `src/manifest/loader.ts`

All public exports match OBJ-004's interface contract exactly. No new public types are introduced.

#### Internal Helper (not exported)

```typescript
/**
 * Maps a single ZodIssue to a ManifestError.
 * Internal to the loader — not exported.
 */
function mapZodIssue(issue: z.ZodIssue): ManifestError;
```

### Behavioral Contracts

#### `parseManifest(raw: unknown): ManifestResult`

**Input:** Any JavaScript value (typically the result of `JSON.parse()`).

**Behavior:**
1. Calls `ManifestSchema.safeParse(raw)`.
2. If Zod parsing succeeds: returns `{ success: true, manifest: parsed, warnings: [] }`. No warnings are possible in Phase 1 — all structural issues are errors.
3. If Zod parsing fails: maps every `ZodIssue` in the `ZodError.issues` array to a `ManifestError` via `mapZodIssue()`. Returns `{ success: false, errors: mappedErrors }`.

**Key invariant:** All Zod issues are collected and returned. Zod's `.safeParse()` naturally collects all errors (it does not short-circuit on first failure for independent fields). This satisfies the "reports all validation errors at once" requirement.

**Key invariant:** This function never throws. All failures are returned as `ManifestResult` with `success: false`.

#### `validateManifestSemantics(manifest: Manifest, registry: ManifestRegistry): ManifestError[]`

**Input:** A structurally valid `Manifest` (has already passed Phase 1) and a populated `ManifestRegistry`.

**Behavior:** Executes all semantic checks in a defined order, collecting every error/warning into a single array. Returns the complete array (empty = valid). Never throws.

**Check execution order** (within each scene, checks run in this order; all scenes are checked):

1. **Geometry existence** — `UNKNOWN_GEOMETRY` if `scene.geometry` not in `registry.geometries`.
2. **Camera existence** — `UNKNOWN_CAMERA` if `scene.camera` not in `registry.cameras`.
3. **Camera-geometry compatibility** — `INCOMPATIBLE_CAMERA` if camera name not in geometry's `compatibleCameras`. Skipped if geometry was unknown (step 1 failed).
4. **Required slot presence** — `MISSING_REQUIRED_SLOT` for each required slot in geometry's `slots` that is absent from `scene.planes`. Skipped if geometry was unknown.
5. **Unknown slot detection** — `UNKNOWN_SLOT` for each key in `scene.planes` that is not in geometry's `slots`. Skipped if geometry was unknown.
6. **FOV support check** — `FOV_WITHOUT_SUPPORT` (warning) if `camera_params.fov_start` or `fov_end` is set but camera's `supportsFovAnimation` is false. Skipped if camera was unknown.

**Cross-scene checks** (run after all per-scene checks):

7. **Duplicate scene IDs** — `DUPLICATE_SCENE_ID` for every scene whose `id` appears more than once. Error is reported on the second (and subsequent) occurrence(s), with `path` pointing to the duplicate scene.
8. **Scene ordering** — Sort scenes by `start_time` (stable sort, preserving array order for equal `start_time` values). If sorted order differs from array order, emit `SCENE_ORDER_MISMATCH` warning once (not per-scene).
9. **Scene overlap analysis** — For each consecutive pair (A, B) in sorted order, compute `overlap = max(0, (A.start_time + A.duration) - B.start_time)`. Apply E-03 rules from OBJ-004. Emit `SCENE_OVERLAP` error if overlap is invalid.
10. **Scene gap analysis** — For each consecutive pair (A, B) in sorted order, if `B.start_time > A.start_time + A.duration`, emit `SCENE_GAP` warning.
11. **Crossfade adjacency** — `CROSSFADE_NO_ADJACENT` if first scene (by sorted order) has `transition_in.type === "crossfade"`, or last scene has `transition_out.type === "crossfade"`.
12. **Audio duration mismatch** — `AUDIO_DURATION_MISMATCH` (warning) if `manifest.composition.audio?.duration` is defined and differs from `computeTotalDuration(manifest)`. Comparison uses a tolerance of ±0.01 seconds to avoid floating-point false positives.

**Key invariant:** When a per-scene check is skipped due to an upstream failure (e.g., unknown geometry makes slot checks meaningless), the skip is silent — no placeholder error is emitted. The upstream error is sufficient.

**Key invariant:** All checks run to completion. A failure in check 1 does not prevent check 7-12 from running. Per-scene skips are scoped to that scene only.

#### `loadManifest(raw: unknown, registry: ManifestRegistry): ManifestResult`

**Behavior:**
1. Call `parseManifest(raw)`.
2. If Phase 1 fails (`success: false`): return immediately with the structural errors. Do not run semantic validation. (Semantic validation requires a typed `Manifest` — running it on invalid data is meaningless.)
3. If Phase 1 succeeds: call `validateManifestSemantics(result.manifest, registry)`.
4. Partition the semantic results into errors (`severity: "error"`) and warnings (`severity: "warning"`).
5. If any semantic errors exist: return `{ success: false, errors: semanticErrors }`. Warnings from semantic validation are included in the errors array (they are informational alongside the blocking errors).
6. If no semantic errors: return `{ success: true, manifest: result.manifest, warnings: semanticWarnings }`.

**Key invariant:** `success: true` is returned only when zero errors exist across both phases. Warnings do not block success.

#### `loadManifestFromFile(filePath: string, registry: ManifestRegistry): Promise<ManifestResult>`

**Behavior:**
1. Check if `filePath` exists using `fs.access()` (or equivalent). If not, return `{ success: false, errors: [{ path: "", code: "FILE_NOT_FOUND", message: "Manifest file not found: {filePath}", severity: "error" }] }`.
2. Read the file contents as UTF-8 string using `fs.readFile()`.
3. Attempt `JSON.parse()`. If it throws a `SyntaxError`, return `{ success: false, errors: [{ path: "", code: "INVALID_JSON", message: "Manifest file contains invalid JSON: {syntaxError.message}", severity: "error" }] }`.
4. Call `loadManifest(parsed, registry)` and return its result.

**Key invariant:** File-level errors (FILE_NOT_FOUND, INVALID_JSON) are terminal — no further validation runs. These are returned as `ManifestResult` with `success: false`, consistent with the return type.

**Key invariant:** This is the only async function in the loader. All other functions are synchronous.

#### `computeTotalDuration(manifest: Manifest): number`

**Behavior:** Returns `Math.max(...manifest.scenes.map(s => s.start_time + s.duration))`.

**Edge case:** Single scene — returns `scene.start_time + scene.duration`.

**Key invariant:** This function assumes a structurally valid `Manifest` (at least one scene, positive durations, non-negative start times). It does not re-validate.

## Design Decisions

### D-01: Zod Error Mapping Strategy

**Choice:** Each `ZodIssue` maps to one `ManifestError`. The mapping extracts:
- `path`: Join `issue.path` elements with dots, using `[N]` notation for array indices. E.g., `["scenes", 0, "planes", "floor", "src"]` → `"scenes[0].planes.floor.src"`.
- `code`: Map from Zod's issue code to a generic `"SCHEMA_VALIDATION"` code. (OBJ-004's error codes are for semantic errors; Zod structural errors use a single code since Zod's own `code` field + the message provide sufficient specificity.)
- `message`: Use Zod's `issue.message` directly, which already names the field and the violation. Zod's messages are actionable by default (e.g., "Expected string, received number"). For `.strict()` unknown key rejections, Zod produces "Unrecognized key(s) in object: 'durration'" — this is already actionable.
- `severity`: Always `"error"` for structural failures.

**Rationale:** Zod's built-in error messages are already actionable and field-specific. Wrapping them with additional formatting adds complexity without value. The `path` field provides the machine-readable location; the `message` provides the human-readable explanation.

**Alternative rejected:** Custom error messages per Zod issue type — this would be a large surface area to maintain and Zod's defaults are already good.

### D-02: Structural Error Code — Single `SCHEMA_VALIDATION` vs. Granular Codes

**Choice:** All Zod structural errors use code `"SCHEMA_VALIDATION"`. Semantic errors use the specific codes from OBJ-004's error code table (`UNKNOWN_GEOMETRY`, `MISSING_REQUIRED_SLOT`, etc.).

**Rationale:** Zod issues are diverse (wrong type, missing field, invalid enum, regex mismatch, refinement failure, unrecognized key). Creating a depthkit error code for each Zod issue type would duplicate Zod's own type system. The `message` field carries the specificity. Semantic errors, by contrast, are domain-specific and benefit from machine-readable codes that consuming tools (CLI, n8n) can programmatically act on.

### D-03: Error Collection — All At Once

**Choice:** Both phases collect all errors before returning. Phase 1 uses Zod's `safeParse()` which naturally collects all issues. Phase 2 iterates all scenes and all cross-scene checks, appending to a single array.

**Rationale:** OBJ-016's description explicitly requires "Reports all validation errors at once rather than one-at-a-time." This is critical for LLM manifest authors who may make multiple errors — fixing one error only to discover another on the next run is a poor experience.

**Constraint:** Phase 2 is skipped entirely when Phase 1 fails. This is unavoidable — semantic checks require typed data. This means an author with both structural and semantic errors will see structural errors first, then semantic errors on the next run. This is acceptable because structural errors (wrong types, missing fields) must be fixed before semantic questions (does this geometry exist?) are even meaningful.

### D-04: Fail-Fast Contract (C-10)

**Choice:** "Fail fast" means: validation runs completely and reports all errors, but the `ManifestResult` with `success: false` prevents any downstream rendering. The rendering orchestrator (OBJ-035) calls `loadManifest()` and must check `success` before proceeding. Invalid manifests never reach the rendering pipeline.

**Rationale:** C-10 says "Invalid manifests must never produce partial output — fail fast, fail clearly." "Fail fast" doesn't mean stop at the first error — it means stop before rendering starts. "Fail clearly" means actionable error messages. Collecting all errors is not in tension with fail-fast; it's in tension with fail-at-first-error, which the objective description explicitly rejects.

### D-05: Skip-on-Unknown-Geometry Pattern

**Choice:** When `scene.geometry` is unknown, skip slot checks (MISSING_REQUIRED_SLOT, UNKNOWN_SLOT) and camera compatibility check for that scene. When `scene.camera` is unknown, skip FOV support check for that scene.

**Rationale:** Checking slots against an unknown geometry would produce misleading errors ("slot 'floor' is unknown" when the real problem is the geometry doesn't exist). The upstream error is sufficient and actionable.

### D-06: Floating-Point Tolerance for Audio Duration Comparison

**Choice:** `AUDIO_DURATION_MISMATCH` uses ±0.01 second tolerance. `|audio.duration - computeTotalDuration()| > 0.01` triggers the warning.

**Rationale:** Scene durations and audio durations come from different sources (manifest author vs. audio probing) and floating-point arithmetic in duration summing can produce tiny discrepancies (e.g., 3 scenes of 8.333... seconds). A 10ms tolerance avoids false positives while still catching meaningful mismatches.

### D-07: Scene Overlap — Tolerance for Floating-Point

**Choice:** Overlap computation uses raw arithmetic: `overlap = (A.start_time + A.duration) - B.start_time`. A tiny negative overlap (due to floating point, e.g., -1e-15) is treated as 0. Use `Math.max(0, ...)` as specified.

For the validity check in E-03 rule 3, the comparison `overlap <= min(A.transition_out.duration, B.transition_in.duration)` also uses a tolerance: `overlap <= min(...) + 0.001` (1ms tolerance) to avoid rejecting overlaps that are equal within floating-point precision.

### D-08: `path` Format for Cross-Scene Errors

**Choice:** For per-scene errors, `path` uses the scene's array index: `"scenes[0].geometry"`, `"scenes[2].planes.floor"`. For cross-scene errors, `path` references both scenes: `"scenes[1]↔scenes[2]"` for overlap/gap errors. For manifest-level errors, `path` is the relevant top-level field: `"composition.audio.duration"` for audio mismatch, `""` for file-level errors.

**Rationale:** The `path` must be unambiguous and machine-parseable. Array-index notation is standard (matches Zod's output format). The `↔` separator for cross-scene errors is visually distinct and won't appear in field names.

### D-09: Duplicate Scene ID — Report on Second Occurrence

**Choice:** When duplicate IDs are found, the error is reported on every occurrence after the first, with `path` pointing to the duplicate scene's array index.

**Rationale:** The first occurrence is "correct" (or at least, established first). Reporting on subsequent occurrences tells the author which scenes to fix.

### D-10: Error Message Templates

**Choice:** Semantic error messages follow consistent templates that include the problematic value and context:

| Code | Message Template |
|------|-----------------|
| `UNKNOWN_GEOMETRY` | `Scene '{id}': geometry '{name}' is not registered. Available geometries: {list}. Did you forget to register geometries?` |
| `UNKNOWN_CAMERA` | `Scene '{id}': camera '{name}' is not registered. Available cameras: {list}.` |
| `INCOMPATIBLE_CAMERA` | `Scene '{id}': camera '{camera}' is not compatible with geometry '{geometry}'. Compatible cameras: {list}.` |
| `MISSING_REQUIRED_SLOT` | `Scene '{id}': geometry '{geometry}' requires plane slot '{slot}' but it is not provided.` |
| `UNKNOWN_SLOT` | `Scene '{id}': plane slot '{slot}' is not defined by geometry '{geometry}'. Valid slots: {list}.` |
| `DUPLICATE_SCENE_ID` | `Scene at index {index}: id '{id}' is already used by a previous scene.` |
| `SCENE_OVERLAP` | `Scenes '{idA}' and '{idB}' overlap by {overlap}s but {reason}.` |
| `SCENE_GAP` | `Gap of {gap}s between scenes '{idA}' and '{idB}' (from {endA}s to {startB}s). The engine will render black frames during the gap.` |
| `SCENE_ORDER_MISMATCH` | `Scenes are not ordered by start_time in the array. The engine will sort by start_time internally, but array order should match for clarity.` |
| `AUDIO_DURATION_MISMATCH` | `Audio duration ({audioDur}s) differs from total scene duration ({sceneDur}s). The engine will use scene durations as specified.` |
| `CROSSFADE_NO_ADJACENT` | `Scene '{id}': crossfade {direction} requires an adjacent scene to blend with, but this is the {position} scene.` |
| `FOV_WITHOUT_SUPPORT` | `Scene '{id}': fov_start/fov_end is set but camera '{camera}' does not support FOV animation. FOV values will be ignored.` |
| `FILE_NOT_FOUND` | `Manifest file not found: {filePath}` |
| `INVALID_JSON` | `Manifest file contains invalid JSON: {parseErrorMessage}` |

**Rationale:** Every message names the specific scene, field, and value that caused the error, plus the available alternatives where applicable. This satisfies "actionable messages (file paths, field names, expected vs actual values)" from the objective description.

### D-11: Empty Registry — Helpful Error Messages

**Choice:** When the registry has zero geometries registered, `UNKNOWN_GEOMETRY` errors include the suffix: `"Did you forget to register geometries? Ensure geometry modules are imported before validation."` (per OBJ-004 E-07). When the registry has geometries but the specific one is unknown, the message lists available geometries without the "did you forget" suffix.

**Rationale:** An empty registry is almost always a wiring bug, not an authoring error. The message should diagnose the likely root cause.

## Acceptance Criteria

### Structural Validation (Phase 1)

- [ ] **AC-01:** `parseManifest()` with a valid manifest matching seed Section 4.6 returns `{ success: true }` with the typed `Manifest` object and empty `warnings` array.
- [ ] **AC-02:** `parseManifest()` with `null`, `undefined`, `42`, `"string"`, and `[]` returns `{ success: false }` with at least one error.
- [ ] **AC-03:** `parseManifest()` never throws — all failures are returned as `ManifestResult`.
- [ ] **AC-04:** `parseManifest()` with a manifest missing `version`, `composition`, AND `scenes` returns errors for all three missing fields simultaneously (not just the first).
- [ ] **AC-05:** Every `ManifestError` from `parseManifest()` has `code: "SCHEMA_VALIDATION"`, a non-empty `path`, a non-empty `message`, and `severity: "error"`.
- [ ] **AC-06:** `parseManifest()` error `path` uses dot notation with `[N]` array indices. E.g., a type error on the first scene's duration produces path `"scenes[0].duration"` (or equivalent Zod path representation).

### Semantic Validation (Phase 2)

- [ ] **AC-07:** `validateManifestSemantics()` with a fully valid manifest and properly registered geometry+camera returns an empty array.
- [ ] **AC-08:** `validateManifestSemantics()` collects errors from ALL scenes, not just the first scene with an error.
- [ ] **AC-09:** When `scene.geometry` is unknown, `MISSING_REQUIRED_SLOT` and `UNKNOWN_SLOT` checks are skipped for that scene (no misleading downstream errors).
- [ ] **AC-10:** When `scene.camera` is unknown, `FOV_WITHOUT_SUPPORT` check is skipped for that scene.
- [ ] **AC-11:** `UNKNOWN_GEOMETRY` message includes the geometry name and lists available geometries from the registry.
- [ ] **AC-12:** `UNKNOWN_CAMERA` message includes the camera name and lists available cameras from the registry.
- [ ] **AC-13:** `INCOMPATIBLE_CAMERA` message names both the camera and geometry and lists compatible cameras.
- [ ] **AC-14:** `MISSING_REQUIRED_SLOT` message names the missing slot and the geometry.
- [ ] **AC-15:** `UNKNOWN_SLOT` message names the unknown slot and lists valid slots for the geometry.
- [ ] **AC-16:** `DUPLICATE_SCENE_ID` is reported on the second (and any subsequent) occurrence, not the first.
- [ ] **AC-17:** `SCENE_OVERLAP` error message describes the overlap duration and explains why it's invalid (e.g., "no transition_out on scene A", "overlap exceeds transition duration").
- [ ] **AC-18:** `SCENE_GAP` warning includes the gap duration and the time range.
- [ ] **AC-19:** `SCENE_ORDER_MISMATCH` is emitted at most once, not per-scene.
- [ ] **AC-20:** `AUDIO_DURATION_MISMATCH` is a warning (not error) — `loadManifest()` still returns `success: true` when this is the only issue.
- [ ] **AC-21:** Audio duration comparison uses ±0.01s tolerance — a 0.005s difference does NOT trigger the warning.
- [ ] **AC-22:** `CROSSFADE_NO_ADJACENT` on first scene's `transition_in` and last scene's `transition_out`.
- [ ] **AC-23:** `FOV_WITHOUT_SUPPORT` is a warning (not error).
- [ ] **AC-24:** When the registry is completely empty, `UNKNOWN_GEOMETRY` messages include the "Did you forget to register geometries?" hint.

### Combined Pipeline (`loadManifest`)

- [ ] **AC-25:** `loadManifest()` runs Phase 1 first. If Phase 1 fails, returns structural errors only — Phase 2 is not run.
- [ ] **AC-26:** `loadManifest()` returns `success: true` only when zero errors exist across both phases. Warnings alone do not block success.
- [ ] **AC-27:** When Phase 2 produces both errors and warnings, `success: false` is returned and both errors and warnings appear in the `errors` array.

### File Loading (`loadManifestFromFile`)

- [ ] **AC-28:** Nonexistent file path returns `{ success: false, errors: [{ code: "FILE_NOT_FOUND", ... }] }`.
- [ ] **AC-29:** File with invalid JSON returns `{ success: false, errors: [{ code: "INVALID_JSON", ... }] }` and the message includes the parse error details.
- [ ] **AC-30:** Valid JSON file is passed through `loadManifest()` and returns its result.
- [ ] **AC-31:** `loadManifestFromFile()` never throws — file I/O errors are caught and returned as `ManifestResult`.

### General

- [ ] **AC-32:** `computeTotalDuration()` returns `max(start_time + duration)` across all scenes. Verified with overlapping scenes, sequential scenes, and single-scene manifests.
- [ ] **AC-33:** All `ManifestError` objects have non-empty `path` (except file-level errors where `path` is `""`), non-empty `code`, non-empty `message`, and valid `severity`.
- [ ] **AC-34:** The loader module has no side effects on import. No global state. The registry is passed as a parameter, not stored globally.

## Edge Cases and Error Handling

### EC-01: Non-Object Input to `parseManifest`
`parseManifest(null)`, `parseManifest(42)`, `parseManifest("hello")` — Zod produces a type error. Mapped to `ManifestError` with `path: ""`, `code: "SCHEMA_VALIDATION"`, message describing expected object.

### EC-02: Valid JSON But Not an Object
`loadManifestFromFile` on a file containing `[1, 2, 3]` (valid JSON, but an array) — `JSON.parse` succeeds, then `parseManifest` receives an array, Zod rejects it.

### EC-03: Deeply Nested Zod Errors
A `PlaneRef` with `opacity: "high"` inside the third scene — Zod error path should resolve to `"scenes[2].planes.{slotName}.opacity"`.

### EC-04: Multiple Errors Per Scene
A scene with unknown geometry AND unknown camera AND duplicate ID — all three errors are reported for that scene.

### EC-05: Overlapping Scenes With Valid Transitions
Scene A: `start_time: 0, duration: 10, transition_out: { type: "crossfade", duration: 1.0 }`. Scene B: `start_time: 9.5, duration: 8, transition_in: { type: "crossfade", duration: 1.0 }`. Overlap = 0.5s. `0.5 <= min(1.0, 1.0)` → valid. No `SCENE_OVERLAP` error.

### EC-06: Overlapping Scenes Where Overlap Exceeds Transition Duration
Scene A: `start_time: 0, duration: 10, transition_out: { type: "crossfade", duration: 0.3 }`. Scene B: `start_time: 9.5, duration: 8, transition_in: { type: "crossfade", duration: 1.0 }`. Overlap = 0.5s. `0.5 > min(0.3, 1.0) = 0.3` → `SCENE_OVERLAP` error.

### EC-07: Scenes With Identical `start_time`
Two scenes with the same `start_time` — overlap equals the shorter scene's full duration. Unless both have transitions justifying it, this produces `SCENE_OVERLAP`.

### EC-08: Single Scene With Crossfade
One scene with `transition_in: { type: "crossfade", duration: 1.0 }` — it's simultaneously first and last, so `CROSSFADE_NO_ADJACENT` is emitted for `transition_in`. If it also has `transition_out: crossfade`, a second `CROSSFADE_NO_ADJACENT` error is emitted.

### EC-09: File Read Permission Error
If `fs.readFile` throws an error other than "file not found" (e.g., permission denied), return `{ success: false, errors: [{ path: "", code: "FILE_NOT_FOUND", message: "Cannot read manifest file: {error.message}", severity: "error" }] }`. Use the `FILE_NOT_FOUND` code since there's no separate code for permission errors — the message distinguishes the cause.

### EC-10: Very Large Manifest
No size limit enforced by the loader. A 10MB JSON file or 500 scenes is processed normally. If `JSON.parse` runs out of memory, the resulting error is caught and returned as `INVALID_JSON`.

### EC-11: Unicode and Special Characters in Scene IDs
Scene IDs are validated by `SceneSchema`'s regex (`/^[a-zA-Z0-9_]+$/`) in Phase 1. Unicode characters are rejected structurally before reaching the semantic validator.

### EC-12: `planes` With Zero Keys But Geometry Has No Required Slots
`planes: {}` with a geometry where all slots have `required: false` — no `MISSING_REQUIRED_SLOT` errors. Valid (though unusual).

## Test Strategy

### Unit Tests: `test/unit/manifest/loader.test.ts`

**Zod-to-ManifestError mapping tests:**
1. Single Zod error → single `ManifestError` with correct path, code, message, severity.
2. Multiple Zod errors → multiple `ManifestError`s, one per issue.
3. Nested path (e.g., `scenes[0].planes.floor.src`) is correctly formatted.
4. Root-level type error (non-object input) → path is `""`.
5. `.strict()` rejection of unknown key → message includes the key name.

**`parseManifest()` tests:**
6. Valid seed Section 4.6 manifest → success.
7. Multiple missing required fields → all reported simultaneously.
8. Non-object inputs (null, number, string, array) → error, no throw.
9. Type mismatches in nested fields → correct path in error.
10. Defaults are applied (opacity, scale, volume, easing, speed).

**`validateManifestSemantics()` tests:**
11. All semantic error codes tested individually (one test per code from OBJ-004's error table).
12. Skip-on-unknown: unknown geometry → no MISSING_REQUIRED_SLOT or UNKNOWN_SLOT for that scene.
13. Skip-on-unknown: unknown camera → no FOV_WITHOUT_SUPPORT for that scene.
14. Multi-scene error collection: 3 scenes each with a different error → all 3 errors returned.
15. Overlap valid: scenes overlap within transition durations → no error.
16. Overlap invalid: scenes overlap beyond transition durations → SCENE_OVERLAP error.
17. Overlap invalid: scenes overlap with no transitions → SCENE_OVERLAP error with appropriate reason text.
18. Gap: consecutive scenes with time gap → SCENE_GAP warning.
19. Duplicate ID: 3 scenes with same id → 2 errors (on 2nd and 3rd occurrence).
20. Audio duration mismatch within tolerance (±0.005s) → no warning.
21. Audio duration mismatch beyond tolerance → warning, success still true.
22. Empty registry → UNKNOWN_GEOMETRY with "did you forget" hint.
23. Registry with geometries but wrong name → UNKNOWN_GEOMETRY lists available names, no hint.
24. Single scene with crossfade on both sides → two CROSSFADE_NO_ADJACENT errors.
25. E-03 rules: overlap with `cut` transition type → SCENE_OVERLAP (cut doesn't justify overlap).

**`loadManifest()` pipeline tests:**
26. Phase 1 failure → returns structural errors, Phase 2 not run.
27. Phase 1 success + Phase 2 failure → returns semantic errors.
28. Phase 1 success + Phase 2 warnings only → success: true with warnings.
29. Phase 1 success + Phase 2 errors + warnings → success: false, both in errors array.

**`computeTotalDuration()` tests:**
30. Sequential scenes → sum check.
31. Overlapping scenes → max(start_time + duration).
32. Single scene → start_time + duration.
33. Non-sequential scenes (scene 2 starts before scene 1 in array but after in time) → correct max.

### Unit Tests: `test/unit/manifest/loader-file.test.ts`

34. Valid JSON fixture file → success.
35. Nonexistent path → FILE_NOT_FOUND, no throw.
36. File with `{invalid json}` → INVALID_JSON with parse error details.
37. File containing `null` → valid JSON, then parseManifest handles it.
38. Empty file → INVALID_JSON (empty string is not valid JSON).

### Integration Test: `test/integration/manifest-roundtrip.test.ts`

39. Load `test/fixtures/valid-manifest.json`, register mock geometries and cameras matching the fixture, call `loadManifestFromFile()`, assert `success: true`, verify parsed manifest matches expected typed structure.

### Relevant Testable Claims

- **TC-07:** Tests 11-25 directly verify that "manifest validation catches common authoring errors" — covering unknown geometries, incompatible cameras, missing slots, unknown slots, duplicate IDs, overlapping scenes, and more.

## Integration Points

### Depends On

- **OBJ-004 (Manifest Schema Core):** Imports `ManifestSchema`, `SceneSchema`, all type exports (`Manifest`, `Scene`, `ManifestError`, `ManifestResult`, `ManifestRegistry`, `GeometryRegistration`, `CameraRegistration`, `PlaneSlotDef`), and `createRegistry()`. OBJ-004 defines the schemas and types; OBJ-016 implements the validation pipeline that uses them.
- **OBJ-001 (Project Scaffolding):** `fs/promises` for file I/O, vitest for testing, TypeScript compilation.

### Consumed By

- **OBJ-013 (CLI):** Calls `loadManifestFromFile()` and `createRegistry()` as the first step of the `render` command. Formats `ManifestError[]` for terminal output.
- **OBJ-035 (Orchestrator):** Calls `loadManifest()` (or `loadManifestFromFile()`) as the pre-render validation gate. If `success: false`, aborts rendering and surfaces errors. This is the enforcement point for C-10.
- **OBJ-048 (CLI Error Formatting):** Consumes `ManifestError` objects and formats them for human-readable terminal output (colors, grouping, etc.).

### File Placement

- **Implementation:** `src/manifest/loader.ts` — all public functions and internal helpers.
- **Tests:**
  - `test/unit/manifest/loader.test.ts` — structural and semantic validation tests.
  - `test/unit/manifest/loader-file.test.ts` — file I/O tests.
  - `test/integration/manifest-roundtrip.test.ts` — end-to-end file loading.
- **Fixtures:** `test/fixtures/valid-manifest.json` — complete valid manifest per seed Section 4.6.
- **Additional fixtures:** `test/fixtures/invalid/` directory containing deliberately broken manifests for testing (e.g., `missing-fields.json`, `wrong-types.json`, `duplicate-ids.json`, `overlapping-scenes.json`, `invalid.json` containing malformed JSON).

## Open Questions

### OQ-A: Should `loadManifestFromFile` Accept YAML?
The seed specifies JSON manifests. YAML support would be trivial (parse with `js-yaml` then pass to `loadManifest`) but adds a dependency. Deferred — JSON only for V1.

### OQ-B: Should Error Messages Be Localizable?
Current design uses English-only message templates. Internationalization is out of scope for V1 but the template pattern (D-10) would support it if needed later.

### OQ-C: Should There Be a `formatErrors()` Utility?
OBJ-016 produces `ManifestError[]` objects. Formatting them for display (terminal colors, grouping by scene, severity icons) is a presentation concern. This spec defers formatting to OBJ-013 (CLI) and OBJ-048 (CLI error formatting). The loader returns structured data only.

---

I believe this spec fully covers the behavioral contracts, error mapping, collection strategy, and fail-fast semantics that OBJ-016 requires. I'd like the Challenger to verify:

1. The boundary between OBJ-004 (schema/types) and OBJ-016 (loader behavior) is clean — no overlap, no gaps.
2. The Zod error mapping strategy (single `SCHEMA_VALIDATION` code) is appropriate vs. granular codes.
3. The skip-on-unknown pattern and execution order are well-specified.
4. The overlap validation logic (E-03 tolerance, floating-point handling) is precise enough for implementation.
5. The test strategy covers TC-07 adequately.

---

## Round 2 — spec_challenger

I've reviewed the proposed spec for OBJ-016 thoroughly against the seed, OBJ-004's spec, and the objective description. This is a solid proposal — the core behavioral contracts, error collection strategy, and fail-fast semantics are well-reasoned. Let me itemize what's sound and what needs fixing.

## Points of Agreement (Explicitly Approved)

1. **Two-phase skip behavior (D-03, D-05):** Skipping Phase 2 when Phase 1 fails, and skipping downstream checks when upstream checks fail (unknown geometry → skip slot checks), is correct and well-specified.
2. **Error collection — all at once (D-03):** Uses Zod's natural `safeParse()` collection + iterative semantic check accumulation. Clean.
3. **Fail-fast interpretation (D-04):** "Fail fast" = validate completely, then block rendering — not "stop at first error." Correct reading of C-10 in context of the objective description's "all errors at once" mandate.
4. **Error message templates (D-10):** Actionable, include the offending value, list alternatives. Directly satisfies the objective's "file paths, field names, expected vs actual values" requirement.
5. **Audio duration tolerance (D-06):** ±0.01s is well-justified for floating-point accumulation.
6. **Behavioral contracts for all five public functions:** Precise, step-by-step, no ambiguity in the happy path.

## Issues

### Issue 1: EC-09 — Permission Error Mislabeled (Minor)

**Problem:** The spec says to reuse `FILE_NOT_FOUND` code for permission errors, with the message distinguishing the cause. But `FILE_NOT_FOUND` is semantically wrong — the file *was* found, it just can't be read. A CLI or n8n workflow checking `code === "FILE_NOT_FOUND"` might suggest the user check the path when the real problem is permissions.

**Proposed fix:** OBJ-004's error code table is fixed — adding a new code would be OBJ-004's territory. Instead, use a new code `FILE_READ_ERROR` for non-ENOENT file access errors, and document it as an OBJ-016-originated code that extends OBJ-004's table. Alternatively, just use `FILE_NOT_FOUND` for ENOENT specifically, and introduce a general `FILE_READ_ERROR` for other `fs` errors (EACCES, EISDIR, etc.). The error code table in OBJ-004 is descriptive, not exhaustive — OBJ-016 can legitimately introduce codes for error conditions that only arise in its implementation scope (file I/O).

### Issue 2: D-08 — Unicode `↔` in `path` Field (Major)

**Problem:** Using `↔` (U+2194) as a separator in the `path` field for cross-scene errors (`"scenes[1]↔scenes[2]"`) introduces a Unicode character into what is otherwise an ASCII, dot-notation, machine-parseable path format. Consumers doing regex or string parsing on `path` will not expect this. It's also invisible in some terminal fonts.

**Proposed fix:** For cross-scene errors (SCENE_OVERLAP, SCENE_GAP), set `path` to the first scene's path (e.g., `"scenes[1]"`) and include the second scene's reference in the `message`. This keeps `path` as a single, standard JSON-path-like reference. The message already names both scenes by `id`, which is more useful than array indices anyway.

### Issue 3: AC-27 — Warnings Mixed Into `errors` Array Needs Consumer Guidance (Minor)

**Problem:** When `loadManifest()` returns `success: false`, warnings from Phase 2 are placed in the `errors` array (since the failure variant of `ManifestResult` only has `errors`, not `warnings`). This is a consequence of OBJ-004's type design, but consumers need to know they should filter by `severity` to distinguish.

**Proposed fix:** Add a sentence to the `loadManifest()` behavioral contract: "Consumers should filter the `errors` array by `severity` to separate blocking errors from informational warnings." This is documentation, not a type change. Also add an acceptance criterion: "AC-XX: When `loadManifest()` returns `success: false` and Phase 2 produced warnings, those warnings appear in the `errors` array with `severity: 'warning'` and can be distinguished from errors by checking the `severity` field."

### Issue 4: Test Fixture Ownership (Minor)

**Problem:** Both OBJ-004 and OBJ-016 reference `test/fixtures/valid-manifest.json`. OBJ-004's file placement says it goes in that location. If OBJ-004 already created it (its status is "verified"), OBJ-016 should reference the existing fixture, not create it. If OBJ-004 didn't create it (only specified where it should go), OBJ-016 needs to create it. The spec should be explicit.

**Proposed fix:** Add to the file placement section: "`test/fixtures/valid-manifest.json` — created by OBJ-004 (reused, not recreated). OBJ-016 creates `test/fixtures/invalid/` directory with broken manifests for error testing."

### Issue 5: Overlap Tolerance Asymmetry (Minor)

**Problem:** D-07 applies a 1ms tolerance to the overlap validity check (`overlap <= min(...) + 0.001`) but applies no tolerance to the overlap *detection* (`Math.max(0, ...)`). This means an overlap of 0.0001 (clearly floating-point noise) would be detected as a real overlap, then validated against transition durations. It would pass the validity check (0.0001 <= any positive transition duration), so no error — but it's semantically noise. This is fine in practice but the asymmetry is a bit surprising. No fix needed, just noting it's coherent.

### Issue 6: `SCENE_ORDER_MISMATCH` — Missing Stable Sort Specification (Minor)

**Problem:** D-11 says the engine sorts by `start_time` internally. The semantic validator also sorts by `start_time` (behavioral contract step 8). The spec says "stable sort, preserving array order for equal `start_time` values." But JavaScript's `Array.prototype.sort` is only guaranteed stable in ES2019+. Node.js has had stable sort since V8 7.0+ (Node 12+), so this is fine for any modern Node, but the spec should state the minimum Node version assumption or note that the sort must be stable.

**Proposed fix:** Add a note: "Stable sort is required (preserving array order for equal `start_time` values). Node.js 12+ guarantees stable `Array.prototype.sort()`, which is within depthkit's supported runtime." Or just say: "Use a stable sort algorithm."

---

## Summary

- **0 critical issues**
- **1 major issue** (Issue 2: Unicode in path)
- **4 minor issues** (Issues 1, 3, 4, 6 — all easily fixable)
- **1 observation** (Issue 5 — no fix needed)

The spec is close to convergence. Please address Issue 2 (the `↔` path format) and the minor issues, and I'll verify in the next round.

---

## Round 3 — spec_author

Thank you for the thorough review. All issues are valid. Here's my revised spec with each addressed:

---

# Specification: OBJ-016 — Manifest Loader and Validator

## Summary

OBJ-016 implements the manifest loading and validation pipeline defined by OBJ-004's interface contracts. It specifies how raw JSON is parsed through the two-phase validation pipeline (structural Zod parsing → semantic registry validation), how Zod errors are mapped to actionable `ManifestError` objects, how all errors are collected at once (not one-at-a-time), how file I/O works for `loadManifestFromFile()`, and how the fail-fast contract (C-10) is enforced: invalid manifests never produce partial output. This is the concrete behavioral specification for `src/manifest/loader.ts`.

## Interface Contract

All public exports match OBJ-004's interface contract exactly. OBJ-016 introduces one additional error code (`FILE_READ_ERROR`) for file I/O failures not covered by OBJ-004's table.

### Module: `src/manifest/loader.ts`

#### Internal Helper (not exported)

```typescript
/**
 * Maps a single ZodIssue to a ManifestError.
 * Internal to the loader — not exported.
 */
function mapZodIssue(issue: z.ZodIssue): ManifestError;
```

### Behavioral Contracts

#### `parseManifest(raw: unknown): ManifestResult`

**Input:** Any JavaScript value (typically the result of `JSON.parse()`).

**Behavior:**
1. Calls `ManifestSchema.safeParse(raw)`.
2. If Zod parsing succeeds: returns `{ success: true, manifest: parsed, warnings: [] }`. No warnings are possible in Phase 1 — all structural issues are errors.
3. If Zod parsing fails: maps every `ZodIssue` in the `ZodError.issues` array to a `ManifestError` via `mapZodIssue()`. Returns `{ success: false, errors: mappedErrors }`.

**Key invariant:** All Zod issues are collected and returned. Zod's `.safeParse()` naturally collects all errors (it does not short-circuit on first failure for independent fields). This satisfies the "reports all validation errors at once" requirement.

**Key invariant:** This function never throws. All failures are returned as `ManifestResult` with `success: false`.

#### `validateManifestSemantics(manifest: Manifest, registry: ManifestRegistry): ManifestError[]`

**Input:** A structurally valid `Manifest` (has already passed Phase 1) and a populated `ManifestRegistry`.

**Behavior:** Executes all semantic checks in a defined order, collecting every error/warning into a single array. Returns the complete array (empty = valid). Never throws.

**Check execution order** (within each scene, checks run in this order; all scenes are checked):

1. **Geometry existence** — `UNKNOWN_GEOMETRY` if `scene.geometry` not in `registry.geometries`.
2. **Camera existence** — `UNKNOWN_CAMERA` if `scene.camera` not in `registry.cameras`.
3. **Camera-geometry compatibility** — `INCOMPATIBLE_CAMERA` if camera name not in geometry's `compatibleCameras`. Skipped if geometry was unknown (step 1 failed).
4. **Required slot presence** — `MISSING_REQUIRED_SLOT` for each required slot in geometry's `slots` that is absent from `scene.planes`. Skipped if geometry was unknown.
5. **Unknown slot detection** — `UNKNOWN_SLOT` for each key in `scene.planes` that is not in geometry's `slots`. Skipped if geometry was unknown.
6. **FOV support check** — `FOV_WITHOUT_SUPPORT` (warning) if `camera_params.fov_start` or `fov_end` is set but camera's `supportsFovAnimation` is false. Skipped if camera was unknown.

**Cross-scene checks** (run after all per-scene checks):

7. **Duplicate scene IDs** — `DUPLICATE_SCENE_ID` for every scene whose `id` appears more than once. Error is reported on the second (and subsequent) occurrence(s), with `path` pointing to the duplicate scene.
8. **Scene ordering** — Sort scenes by `start_time` using a stable sort (preserving array order for equal `start_time` values; Node.js 12+ guarantees stable `Array.prototype.sort()`). If sorted order differs from array order, emit `SCENE_ORDER_MISMATCH` warning once (not per-scene).
9. **Scene overlap analysis** — For each consecutive pair (A, B) in sorted order, compute `overlap = max(0, (A.start_time + A.duration) - B.start_time)`. Apply E-03 rules from OBJ-004. Emit `SCENE_OVERLAP` error if overlap is invalid.
10. **Scene gap analysis** — For each consecutive pair (A, B) in sorted order, if `B.start_time > A.start_time + A.duration`, emit `SCENE_GAP` warning.
11. **Crossfade adjacency** — `CROSSFADE_NO_ADJACENT` if first scene (by sorted order) has `transition_in.type === "crossfade"`, or last scene has `transition_out.type === "crossfade"`.
12. **Audio duration mismatch** — `AUDIO_DURATION_MISMATCH` (warning) if `manifest.composition.audio?.duration` is defined and differs from `computeTotalDuration(manifest)`. Comparison uses a tolerance of ±0.01 seconds to avoid floating-point false positives.

**Key invariant:** When a per-scene check is skipped due to an upstream failure (e.g., unknown geometry makes slot checks meaningless), the skip is silent — no placeholder error is emitted. The upstream error is sufficient.

**Key invariant:** All checks run to completion. A failure in check 1 does not prevent check 7-12 from running. Per-scene skips are scoped to that scene only.

#### `loadManifest(raw: unknown, registry: ManifestRegistry): ManifestResult`

**Behavior:**
1. Call `parseManifest(raw)`.
2. If Phase 1 fails (`success: false`): return immediately with the structural errors. Do not run semantic validation.
3. If Phase 1 succeeds: call `validateManifestSemantics(result.manifest, registry)`.
4. Partition the semantic results into errors (`severity: "error"`) and warnings (`severity: "warning"`).
5. If any semantic errors exist: return `{ success: false, errors: allSemanticResults }`. Both errors and warnings from semantic validation appear in the `errors` array. Consumers should filter by `severity` to separate blocking errors from informational warnings.
6. If no semantic errors: return `{ success: true, manifest: result.manifest, warnings: semanticWarnings }`.

**Key invariant:** `success: true` is returned only when zero errors exist across both phases. Warnings do not block success.

#### `loadManifestFromFile(filePath: string, registry: ManifestRegistry): Promise<ManifestResult>`

**Behavior:**
1. Attempt to read the file using `fs.readFile()` (UTF-8). If the call rejects:
   - If the error code is `ENOENT`: return `{ success: false, errors: [{ path: "", code: "FILE_NOT_FOUND", message: "Manifest file not found: {filePath}", severity: "error" }] }`.
   - For any other `fs` error (EACCES, EISDIR, etc.): return `{ success: false, errors: [{ path: "", code: "FILE_READ_ERROR", message: "Cannot read manifest file '{filePath}': {error.message}", severity: "error" }] }`.
2. Attempt `JSON.parse()`. If it throws a `SyntaxError`, return `{ success: false, errors: [{ path: "", code: "INVALID_JSON", message: "Manifest file contains invalid JSON: {syntaxError.message}", severity: "error" }] }`.
3. Call `loadManifest(parsed, registry)` and return its result.

**Key invariant:** File-level errors (FILE_NOT_FOUND, FILE_READ_ERROR, INVALID_JSON) are terminal — no further validation runs.

**Key invariant:** This is the only async function in the loader. All other functions are synchronous.

#### `computeTotalDuration(manifest: Manifest): number`

**Behavior:** Returns `Math.max(...manifest.scenes.map(s => s.start_time + s.duration))`.

**Edge case:** Single scene — returns `scene.start_time + scene.duration`.

**Key invariant:** This function assumes a structurally valid `Manifest` (at least one scene, positive durations, non-negative start times). It does not re-validate.

## Design Decisions

### D-01: Zod Error Mapping Strategy

**Choice:** Each `ZodIssue` maps to one `ManifestError`. The mapping extracts:
- `path`: Join `issue.path` elements with dots, using `[N]` notation for array indices. E.g., `["scenes", 0, "planes", "floor", "src"]` → `"scenes[0].planes.floor.src"`. Empty path array → `""`.
- `code`: `"SCHEMA_VALIDATION"` for all Zod structural errors.
- `message`: Use Zod's `issue.message` directly. Zod's messages are already actionable (e.g., "Expected string, received number", "Unrecognized key(s) in object: 'durration'").
- `severity`: Always `"error"`.

**Rationale:** Zod's built-in error messages are already actionable and field-specific. Creating granular depthkit codes for each Zod issue type would duplicate Zod's own type system. Semantic errors, by contrast, are domain-specific and benefit from machine-readable codes.

### D-02: Error Collection — All At Once

**Choice:** Both phases collect all errors before returning. Phase 1 uses Zod's `safeParse()` which naturally collects all issues. Phase 2 iterates all scenes and all cross-scene checks, appending to a single array.

**Rationale:** OBJ-016's description explicitly requires "Reports all validation errors at once rather than one-at-a-time."

**Constraint:** Phase 2 is skipped entirely when Phase 1 fails. This is unavoidable — semantic checks require typed data. An author with both structural and semantic errors sees structural errors first, then semantic errors on the next run. Acceptable because structural errors must be fixed before semantic questions are meaningful.

### D-03: Fail-Fast Contract (C-10)

**Choice:** "Fail fast" means: validation runs completely and reports all errors, but `ManifestResult` with `success: false` prevents any downstream rendering. The rendering orchestrator (OBJ-035) calls `loadManifest()` and must check `success` before proceeding.

**Rationale:** C-10: "Invalid manifests must never produce partial output — fail fast, fail clearly." "Fail fast" = stop before rendering starts. "Fail clearly" = actionable error messages. Collecting all errors satisfies the objective's "all errors at once" mandate.

### D-04: Skip-on-Unknown-Geometry Pattern

**Choice:** When `scene.geometry` is unknown, skip slot checks and camera compatibility for that scene. When `scene.camera` is unknown, skip FOV support check.

**Rationale:** Checking slots against an unknown geometry produces misleading errors. The upstream error is sufficient and actionable.

### D-05: Floating-Point Tolerance for Audio Duration Comparison

**Choice:** `AUDIO_DURATION_MISMATCH` uses ±0.01 second tolerance. `|audio.duration - computeTotalDuration()| > 0.01` triggers the warning.

**Rationale:** Scene durations from different sources (manifest author vs. audio probing) and floating-point arithmetic in duration summing can produce tiny discrepancies. A 10ms tolerance avoids false positives.

### D-06: Scene Overlap — Tolerance for Floating-Point

**Choice:** Overlap computation: `overlap = Math.max(0, (A.start_time + A.duration) - B.start_time)`. For the validity check in E-03 rule 3, the comparison uses `overlap <= min(A.transition_out.duration, B.transition_in.duration) + 0.001` (1ms tolerance).

**Rationale:** Avoids rejecting overlaps that are equal within floating-point precision.

### D-07: `path` Format — Standard JSON-Path-Like for All Errors

**Choice:** The `path` field always uses standard dot-notation with `[N]` array indices. For per-scene errors: `"scenes[0].geometry"`, `"scenes[2].planes.floor"`. For cross-scene errors (SCENE_OVERLAP, SCENE_GAP): `path` references the first scene only (e.g., `"scenes[1]"`); the second scene is identified by `id` in the `message` text. For manifest-level errors: `"composition.audio.duration"`. For file-level errors: `""`.

**Rationale:** Keeps `path` as a single, ASCII, machine-parseable JSON-path-like reference. Cross-scene context is conveyed in the human-readable `message`, which already names both scenes by `id`.

### D-08: Duplicate Scene ID — Report on Second Occurrence

**Choice:** When duplicate IDs are found, the error is reported on every occurrence after the first, with `path` pointing to the duplicate scene's array index.

**Rationale:** The first occurrence is established first. Reporting on subsequent occurrences tells the author which scenes to fix.

### D-09: Error Message Templates

**Choice:** Semantic error messages follow consistent templates:

| Code | Message Template |
|------|-----------------|
| `UNKNOWN_GEOMETRY` | `Scene '{id}': geometry '{name}' is not registered. Available geometries: {list}.` (If registry has zero geometries, append: `" Did you forget to register geometries? Ensure geometry modules are imported before validation."`) |
| `UNKNOWN_CAMERA` | `Scene '{id}': camera '{name}' is not registered. Available cameras: {list}.` |
| `INCOMPATIBLE_CAMERA` | `Scene '{id}': camera '{camera}' is not compatible with geometry '{geometry}'. Compatible cameras: {list}.` |
| `MISSING_REQUIRED_SLOT` | `Scene '{id}': geometry '{geometry}' requires plane slot '{slot}' but it is not provided.` |
| `UNKNOWN_SLOT` | `Scene '{id}': plane slot '{slot}' is not defined by geometry '{geometry}'. Valid slots: {list}.` |
| `DUPLICATE_SCENE_ID` | `Scene at index {index}: id '{id}' is already used by a previous scene.` |
| `SCENE_OVERLAP` | `Scenes '{idA}' and '{idB}' overlap by {overlap}s but {reason}.` |
| `SCENE_GAP` | `Gap of {gap}s between scenes '{idA}' and '{idB}' (from {endA}s to {startB}s). The engine will render black frames during the gap.` |
| `SCENE_ORDER_MISMATCH` | `Scenes are not ordered by start_time in the array. The engine will sort by start_time internally, but array order should match for clarity.` |
| `AUDIO_DURATION_MISMATCH` | `Audio duration ({audioDur}s) differs from total scene duration ({sceneDur}s). The engine will use scene durations as specified.` |
| `CROSSFADE_NO_ADJACENT` | `Scene '{id}': crossfade {direction} requires an adjacent scene to blend with, but this is the {position} scene.` |
| `FOV_WITHOUT_SUPPORT` | `Scene '{id}': fov_start/fov_end is set but camera '{camera}' does not support FOV animation. FOV values will be ignored.` |
| `FILE_NOT_FOUND` | `Manifest file not found: {filePath}` |
| `FILE_READ_ERROR` | `Cannot read manifest file '{filePath}': {error.message}` |
| `INVALID_JSON` | `Manifest file contains invalid JSON: {parseErrorMessage}` |

**Rationale:** Every message names the specific scene, field, and value that caused the error, plus available alternatives where applicable.

### D-10: `FILE_READ_ERROR` as OBJ-016-Originated Error Code

**Choice:** OBJ-016 introduces `FILE_READ_ERROR` for non-ENOENT file system errors (EACCES, EISDIR, etc.). This extends OBJ-004's error code table, which covers validation-level codes but not all file I/O failure modes.

**Rationale:** `FILE_NOT_FOUND` is semantically wrong for permission errors. A CLI checking `code === "FILE_NOT_FOUND"` would suggest fixing the path when the real problem is permissions. `FILE_READ_ERROR` is a distinct, actionable code.

### D-11: Stable Sort Requirement

**Choice:** Scene sorting by `start_time` must be stable (preserving array order for equal `start_time` values). Node.js 12+ guarantees stable `Array.prototype.sort()`, which is within depthkit's supported runtime (the project uses modern TypeScript features that already require Node 18+).

### D-12: Warnings in Failed Results

**Choice:** When `loadManifest()` returns `success: false`, warnings from Phase 2 appear in the `errors` array alongside blocking errors. Consumers filter by `severity` to distinguish them.

**Rationale:** OBJ-004's `ManifestResult` type has no `warnings` field on the failure variant. Discarding warnings would lose information. Including them with their `severity: "warning"` tag preserves all validation output.

## Acceptance Criteria

### Structural Validation (Phase 1)

- [ ] **AC-01:** `parseManifest()` with a valid manifest matching seed Section 4.6 returns `{ success: true }` with the typed `Manifest` object and empty `warnings` array.
- [ ] **AC-02:** `parseManifest()` with `null`, `undefined`, `42`, `"string"`, and `[]` returns `{ success: false }` with at least one error.
- [ ] **AC-03:** `parseManifest()` never throws — all failures are returned as `ManifestResult`.
- [ ] **AC-04:** `parseManifest()` with a manifest missing `version`, `composition`, AND `scenes` returns errors for all three missing fields simultaneously (not just the first).
- [ ] **AC-05:** Every `ManifestError` from `parseManifest()` has `code: "SCHEMA_VALIDATION"`, a non-empty `path` (or `""` for root-level errors), a non-empty `message`, and `severity: "error"`.
- [ ] **AC-06:** `parseManifest()` error `path` uses dot notation with `[N]` array indices. E.g., a type error on the first scene's duration produces a path containing `"scenes[0].duration"`.

### Semantic Validation (Phase 2)

- [ ] **AC-07:** `validateManifestSemantics()` with a fully valid manifest and properly registered geometry+camera returns an empty array.
- [ ] **AC-08:** `validateManifestSemantics()` collects errors from ALL scenes, not just the first scene with an error.
- [ ] **AC-09:** When `scene.geometry` is unknown, `MISSING_REQUIRED_SLOT`, `UNKNOWN_SLOT`, and `INCOMPATIBLE_CAMERA` checks are skipped for that scene.
- [ ] **AC-10:** When `scene.camera` is unknown, `FOV_WITHOUT_SUPPORT` check is skipped for that scene.
- [ ] **AC-11:** `UNKNOWN_GEOMETRY` message includes the geometry name and lists available geometries from the registry.
- [ ] **AC-12:** `UNKNOWN_CAMERA` message includes the camera name and lists available cameras from the registry.
- [ ] **AC-13:** `INCOMPATIBLE_CAMERA` message names both the camera and geometry and lists compatible cameras.
- [ ] **AC-14:** `MISSING_REQUIRED_SLOT` message names the missing slot and the geometry.
- [ ] **AC-15:** `UNKNOWN_SLOT` message names the unknown slot and lists valid slots for the geometry.
- [ ] **AC-16:** `DUPLICATE_SCENE_ID` is reported on the second (and any subsequent) occurrence, not the first.
- [ ] **AC-17:** `SCENE_OVERLAP` error message describes the overlap duration and explains why it's invalid.
- [ ] **AC-18:** `SCENE_GAP` warning includes the gap duration and the time range.
- [ ] **AC-19:** `SCENE_ORDER_MISMATCH` is emitted at most once, not per-scene.
- [ ] **AC-20:** `AUDIO_DURATION_MISMATCH` is a warning (not error) — `loadManifest()` still returns `success: true` when this is the only issue.
- [ ] **AC-21:** Audio duration comparison uses ±0.01s tolerance — a 0.005s difference does NOT trigger the warning.
- [ ] **AC-22:** `CROSSFADE_NO_ADJACENT` on first scene's `transition_in` and last scene's `transition_out`.
- [ ] **AC-23:** `FOV_WITHOUT_SUPPORT` is a warning (not error).
- [ ] **AC-24:** When the registry is completely empty, `UNKNOWN_GEOMETRY` messages include the "Did you forget to register geometries?" hint.

### Combined Pipeline (`loadManifest`)

- [ ] **AC-25:** `loadManifest()` runs Phase 1 first. If Phase 1 fails, returns structural errors only — Phase 2 is not run.
- [ ] **AC-26:** `loadManifest()` returns `success: true` only when zero errors exist across both phases. Warnings alone do not block success.
- [ ] **AC-27:** When Phase 2 produces both errors and warnings and `loadManifest()` returns `success: false`, both errors and warnings appear in the `errors` array. Warnings are distinguishable by `severity: "warning"`.

### File Loading (`loadManifestFromFile`)

- [ ] **AC-28:** Nonexistent file path returns `{ success: false, errors: [{ code: "FILE_NOT_FOUND", ... }] }`.
- [ ] **AC-29:** File with invalid JSON returns `{ success: false, errors: [{ code: "INVALID_JSON", ... }] }` and the message includes the parse error details.
- [ ] **AC-30:** Valid JSON file is passed through `loadManifest()` and returns its result.
- [ ] **AC-31:** `loadManifestFromFile()` never throws — file I/O errors are caught and returned as `ManifestResult`.
- [ ] **AC-32:** Permission-denied or other non-ENOENT file errors return `{ success: false, errors: [{ code: "FILE_READ_ERROR", ... }] }` with the OS error message included.

### General

- [ ] **AC-33:** `computeTotalDuration()` returns `max(start_time + duration)` across all scenes. Verified with overlapping scenes, sequential scenes, and single-scene manifests.
- [ ] **AC-34:** All `ManifestError` objects have non-empty `code`, non-empty `message`, and valid `severity`. `path` is non-empty for field-level errors and `""` for file-level errors.
- [ ] **AC-35:** The loader module has no side effects on import. No global state. The registry is passed as a parameter.

## Edge Cases and Error Handling

### EC-01: Non-Object Input to `parseManifest`
`parseManifest(null)`, `parseManifest(42)`, `parseManifest("hello")` — Zod produces a type error. Mapped to `ManifestError` with `path: ""`, `code: "SCHEMA_VALIDATION"`, message describing expected object.

### EC-02: Valid JSON But Not an Object
`loadManifestFromFile` on a file containing `[1, 2, 3]` — `JSON.parse` succeeds, then `parseManifest` receives an array, Zod rejects it.

### EC-03: Deeply Nested Zod Errors
A `PlaneRef` with `opacity: "high"` inside the third scene — Zod error path resolves to `"scenes[2].planes.{slotName}.opacity"`.

### EC-04: Multiple Errors Per Scene
A scene with unknown geometry AND unknown camera AND duplicate ID — all three errors are reported for that scene (unknown geometry and unknown camera are independent checks; duplicate ID is a cross-scene check).

### EC-05: Overlapping Scenes With Valid Transitions
Scene A: `start_time: 0, duration: 10, transition_out: { type: "crossfade", duration: 1.0 }`. Scene B: `start_time: 9.5, duration: 8, transition_in: { type: "crossfade", duration: 1.0 }`. Overlap = 0.5s. `0.5 <= min(1.0, 1.0) + 0.001` → valid. No `SCENE_OVERLAP` error.

### EC-06: Overlapping Scenes Where Overlap Exceeds Transition Duration
Scene A: `start_time: 0, duration: 10, transition_out: { type: "crossfade", duration: 0.3 }`. Scene B: `start_time: 9.5, duration: 8, transition_in: { type: "crossfade", duration: 1.0 }`. Overlap = 0.5s. `0.5 > min(0.3, 1.0) + 0.001 = 0.301` → `SCENE_OVERLAP` error.

### EC-07: Scenes With Identical `start_time`
Two scenes with the same `start_time` — overlap equals the shorter scene's full duration. Unless both have transitions justifying it, `SCENE_OVERLAP`.

### EC-08: Single Scene With Crossfade
One scene with `transition_in: { type: "crossfade", duration: 1.0 }` — it's simultaneously first and last, so `CROSSFADE_NO_ADJACENT` for `transition_in`. If it also has `transition_out: crossfade`, a second error.

### EC-09: File Read Permission Error
`fs.readFile` throws with code `EACCES` → return `FILE_READ_ERROR` with the OS error message. Distinct from `FILE_NOT_FOUND` (ENOENT only).

### EC-10: Very Large Manifest
No size limit enforced. 500 scenes processed normally. If `JSON.parse` runs out of memory, caught and returned as `INVALID_JSON`.

### EC-11: Unicode and Special Characters in Scene IDs
Rejected structurally by `SceneSchema`'s regex (`/^[a-zA-Z0-9_]+$/`) in Phase 1.

### EC-12: `planes` With Zero Keys But Geometry Has No Required Slots
`planes: {}` with a geometry where all slots have `required: false` — no errors. Valid.

### EC-13: Empty File
Empty string fails `JSON.parse` → `INVALID_JSON`.

### EC-14: Directory Path Instead of File
`fs.readFile` on a directory throws `EISDIR` → `FILE_READ_ERROR`.

## Test Strategy

### Unit Tests: `test/unit/manifest/loader.test.ts`

**Zod-to-ManifestError mapping tests:**
1. Single Zod error → single `ManifestError` with correct path, code, message, severity.
2. Multiple Zod errors → multiple `ManifestError`s, one per issue.
3. Nested path (e.g., `scenes[0].planes.floor.src`) is correctly formatted.
4. Root-level type error (non-object input) → path is `""`.
5. `.strict()` rejection of unknown key → message includes the key name.

**`parseManifest()` tests:**
6. Valid seed Section 4.6 manifest → success.
7. Multiple missing required fields → all reported simultaneously.
8. Non-object inputs (null, number, string, array) → error, no throw.
9. Type mismatches in nested fields → correct path in error.
10. Defaults applied (opacity, scale, volume, easing, speed).

**`validateManifestSemantics()` tests:**
11. All semantic error codes tested individually (one test per code from the error table).
12. Skip-on-unknown: unknown geometry → no MISSING_REQUIRED_SLOT, UNKNOWN_SLOT, or INCOMPATIBLE_CAMERA for that scene.
13. Skip-on-unknown: unknown camera → no FOV_WITHOUT_SUPPORT for that scene.
14. Multi-scene error collection: 3 scenes each with a different error → all 3 errors returned.
15. Overlap valid: scenes overlap within transition durations → no error.
16. Overlap invalid: scenes overlap beyond transition durations → SCENE_OVERLAP.
17. Overlap invalid: scenes overlap with no transitions → SCENE_OVERLAP with reason text.
18. Overlap invalid: scenes overlap with `cut` transitions → SCENE_OVERLAP (cut doesn't justify overlap).
19. Gap: consecutive scenes with time gap → SCENE_GAP warning.
20. Duplicate ID: 3 scenes with same id → 2 errors (on 2nd and 3rd occurrence).
21. Audio duration mismatch within tolerance (±0.005s) → no warning.
22. Audio duration mismatch beyond tolerance → warning, success still true.
23. Empty registry → UNKNOWN_GEOMETRY with "did you forget" hint.
24. Registry with geometries but wrong name → UNKNOWN_GEOMETRY lists available names, no hint.
25. Single scene with crossfade on both sides → two CROSSFADE_NO_ADJACENT errors.
26. Scene order mismatch → single SCENE_ORDER_MISMATCH warning.

**`loadManifest()` pipeline tests:**
27. Phase 1 failure → returns structural errors, Phase 2 not run.
28. Phase 1 success + Phase 2 failure → returns semantic errors.
29. Phase 1 success + Phase 2 warnings only → success: true with warnings.
30. Phase 1 success + Phase 2 errors + warnings → success: false, both in errors array, distinguishable by severity.

**`computeTotalDuration()` tests:**
31. Sequential scenes → correct sum.
32. Overlapping scenes → max(start_time + duration).
33. Single scene → start_time + duration.
34. Non-sequential array order → correct max regardless of array order.

### Unit Tests: `test/unit/manifest/loader-file.test.ts`

35. Valid JSON fixture file → success.
36. Nonexistent path → FILE_NOT_FOUND, no throw.
37. File with `{invalid json}` → INVALID_JSON with parse error details.
38. File containing `null` → valid JSON, then parseManifest handles it.
39. Empty file → INVALID_JSON.
40. Permission-denied path → FILE_READ_ERROR (requires test setup for EACCES, or mock `fs`).
41. Directory path → FILE_READ_ERROR.

### Integration Test: `test/integration/manifest-roundtrip.test.ts`

42. Load `test/fixtures/valid-manifest.json`, register mock geometries and cameras matching the fixture, call `loadManifestFromFile()`, assert `success: true`, verify parsed manifest matches expected typed structure.

### Relevant Testable Claims

- **TC-07:** Tests 11-26 directly verify "manifest validation catches common authoring errors."

## Integration Points

### Depends On

- **OBJ-004 (Manifest Schema Core):** Imports `ManifestSchema`, all Zod sub-schemas, all type exports (`Manifest`, `Scene`, `ManifestError`, `ManifestResult`, `ManifestRegistry`, `GeometryRegistration`, `CameraRegistration`, `PlaneSlotDef`), and `createRegistry()`. OBJ-004 defines the schemas and types; OBJ-016 implements the validation pipeline.
- **OBJ-001 (Project Scaffolding):** `fs/promises` for file I/O, vitest for testing, TypeScript compilation.

### Consumed By

- **OBJ-013 (CLI):** Calls `loadManifestFromFile()` and `createRegistry()` as the first step of the `render` command. Formats `ManifestError[]` for terminal output.
- **OBJ-035 (Orchestrator):** Calls `loadManifest()` (or `loadManifestFromFile()`) as the pre-render validation gate. If `success: false`, aborts rendering and surfaces errors. This is the enforcement point for C-10.
- **OBJ-048 (CLI Error Formatting):** Consumes `ManifestError` objects for human-readable terminal formatting.

### File Placement

- **Implementation:** `src/manifest/loader.ts`
- **Tests:**
  - `test/unit/manifest/loader.test.ts` — structural and semantic validation tests.
  - `test/unit/manifest/loader-file.test.ts` — file I/O tests.
  - `test/integration/manifest-roundtrip.test.ts` — end-to-end file loading.
- **Fixtures:** `test/fixtures/valid-manifest.json` — created by OBJ-004 (reused, not recreated by OBJ-016). OBJ-016 creates `test/fixtures/invalid/` directory with deliberately broken manifests: `missing-fields.json`, `wrong-types.json`, `duplicate-ids.json`, `overlapping-scenes.json`, `invalid.json` (malformed JSON text).

## Error Code Table (Complete)

Includes OBJ-004's codes plus OBJ-016's addition:

| Code | Severity | Origin | Condition |
|------|----------|--------|-----------|
| `SCHEMA_VALIDATION` | error | OBJ-016 | Any Zod structural validation failure |
| `UNKNOWN_GEOMETRY` | error | OBJ-004 | Scene geometry not registered |
| `UNKNOWN_CAMERA` | error | OBJ-004 | Scene camera not registered |
| `INCOMPATIBLE_CAMERA` | error | OBJ-004 | Camera not in geometry's compatibleCameras |
| `MISSING_REQUIRED_SLOT` | error | OBJ-004 | Required plane slot missing |
| `UNKNOWN_SLOT` | error | OBJ-004 | Plane key not in geometry's slots |
| `DUPLICATE_SCENE_ID` | error | OBJ-004 | Two+ scenes share same id |
| `SCENE_OVERLAP` | error | OBJ-004 | Invalid scene time overlap |
| `CROSSFADE_NO_ADJACENT` | error | OBJ-004 | Crossfade without adjacent scene |
| `SCENE_GAP` | warning | OBJ-004 | Time gap between consecutive scenes |
| `SCENE_ORDER_MISMATCH` | warning | OBJ-004 | Array order ≠ start_time order |
| `AUDIO_DURATION_MISMATCH` | warning | OBJ-004 | Audio vs scene duration differ |
| `FOV_WITHOUT_SUPPORT` | warning | OBJ-004 | FOV params on non-FOV camera |
| `FILE_NOT_FOUND` | error | OBJ-004 | ENOENT on file read |
| `FILE_READ_ERROR` | error | OBJ-016 | Non-ENOENT file read failure |
| `INVALID_JSON` | error | OBJ-004 | File contains unparseable JSON |

## Open Questions

### OQ-A: Should `loadManifestFromFile` Accept YAML?
Deferred — JSON only for V1. YAML would be trivial to add later.

### OQ-B: Should There Be a `formatErrors()` Utility?
Deferred to OBJ-048 (CLI error formatting). The loader returns structured data only.

---

I believe this revision addresses all raised issues:

1. **Issue 1 (Permission error):** Introduced `FILE_READ_ERROR` code, ENOENT-specific routing for `FILE_NOT_FOUND` (D-10, EC-09, AC-32).
2. **Issue 2 (Unicode `↔` in path):** Replaced with single-scene `path` reference; second scene identified by `id` in `message` (D-07).
3. **Issue 3 (Warnings in errors array):** Added consumer guidance in `loadManifest()` contract and AC-27 explicitly tests severity distinguishability (D-12).
4. **Issue 4 (Fixture ownership):** File placement section clarifies OBJ-004 owns the valid fixture; OBJ-016 creates the `invalid/` directory.
5. **Issue 5 (Overlap tolerance asymmetry):** Acknowledged as coherent, no change needed.
6. **Issue 6 (Stable sort):** Added D-11 noting Node.js 12+ guarantee and depthkit's modern runtime requirement.

Challenger, please verify these revisions and approve if satisfactory.

---

## Round 4 — spec_challenger

I've carefully verified each revision against my Round 2 objections. Let me confirm:

**Issue 1 (Permission error):** ✅ Verified. `FILE_READ_ERROR` introduced in D-10, ENOENT routing in `loadManifestFromFile` behavioral contract step 1, EC-09 updated, EC-14 added for directory paths, AC-32 added. All structurally present.

**Issue 2 (Unicode `↔`):** ✅ Verified. D-07 now specifies single-scene `path` with second scene in `message`. Consistent across SCENE_OVERLAP and SCENE_GAP.

**Issue 3 (Warnings in errors array):** ✅ Verified. D-12 added, `loadManifest` step 5 includes consumer guidance, AC-27 explicitly tests severity distinguishability.

**Issue 4 (Fixture ownership):** ✅ Verified. File placement section states "created by OBJ-004 (reused, not recreated by OBJ-016)."

**Issue 6 (Stable sort):** ✅ Verified. D-11 added with Node.js 12+ justification.

**New scan — two minor observations:**

1. **SCENE_ORDER_MISMATCH `path` value unspecified.** The warning is emitted once, not per-scene. What should `path` be? It's not file-level (`""`), not a specific field. I'd set it to `"scenes"` since the concern is about the array. Minor — can be noted in the spec as a clarification.

2. **Cross-scene error `path` — original vs sorted array index.** D-07 says `path` references the first scene (e.g., `"scenes[1]"`). After sorting by `start_time`, the "first scene in a pair" might be at a different array index than its original position. The path should use the **original array index** so consumers can locate the scene in the source JSON. This is the natural behavior (scenes carry their original indices from iteration), but worth a one-line clarification.

Neither is blocking. Both are easily folded into the final write.

CONCLUSION:

The spec is complete, implementable, and correctly scoped. I'll write it to disk now with the two minor clarifications folded in.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/output.md",
  "content": "# Specification: OBJ-016 \u2014 Manifest Loader and Validator\n\n## Summary\n\nOBJ-016 implements the manifest loading and validation pipeline defined by OBJ-004's interface contracts. It specifies how raw JSON is parsed through the two-phase validation pipeline (structural Zod parsing \u2192 semantic registry validation), how Zod errors are mapped to actionable `ManifestError` objects, how all errors are collected at once (not one-at-a-time), how file I/O works for `loadManifestFromFile()`, and how the fail-fast contract (C-10) is enforced: invalid manifests never produce partial output. This is the concrete behavioral specification for `src/manifest/loader.ts`.\n\n## Interface Contract\n\nAll public exports match OBJ-004's interface contract exactly. OBJ-016 introduces one additional error code (`FILE_READ_ERROR`) for file I/O failures not covered by OBJ-004's table.\n\n### Module: `src/manifest/loader.ts`\n\n#### Internal Helper (not exported)\n\n```typescript\n/**\n * Maps a single ZodIssue to a ManifestError.\n * Internal to the loader \u2014 not exported.\n */\nfunction mapZodIssue(issue: z.ZodIssue): ManifestError;\n```\n\n### Behavioral Contracts\n\n#### `parseManifest(raw: unknown): ManifestResult`\n\n**Input:** Any JavaScript value (typically the result of `JSON.parse()`).\n\n**Behavior:**\n1. Calls `ManifestSchema.safeParse(raw)`.\n2. If Zod parsing succeeds: returns `{ success: true, manifest: parsed, warnings: [] }`. No warnings are possible in Phase 1 \u2014 all structural issues are errors.\n3. If Zod parsing fails: maps every `ZodIssue` in the `ZodError.issues` array to a `ManifestError` via `mapZodIssue()`. Returns `{ success: false, errors: mappedErrors }`.\n\n**Key invariant:** All Zod issues are collected and returned. Zod's `.safeParse()` naturally collects all errors (it does not short-circuit on first failure for indep
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-016",
     3→  "description": "Manifest loader and validator -- JSON parsing, Zod schema validation execution, error collection with actionable messages (file paths, field names, expected vs actual values), fail-fast behavior per C-10 (invalid manifests never produce partial output). Reports all validation errors at once rather than one-at-a-time.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-004"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Applies the schema from OBJ-004 to actual manifest files. Covers TC-07 (validation catches errors)."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/meta.json",
  "content": "{\n  \"id\": \"OBJ-016\",\n  \"description\": \"Manifest loader and validator -- JSON parsing, Zod schema validation execution, error collection with actionable messages (file paths, field names, expected vs actual values), fail-fast behavior per C-10 (invalid manifests never produce partial output). Reports all validation errors at once rather than one-at-a-time.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-004\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 engine core. Applies the schema from OBJ-004 to actual manifest files. Covers TC-07 (validation catches errors). Spec complete: two-phase validation (structural Zod + semantic registry), all-at-once error collection, FILE_READ_ERROR code for non-ENOENT fs errors, skip-on-unknown pattern, floating-point tolerances for overlap/audio checks.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/meta.json has been updated successfully.
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
  "description": "Show working tree status"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commit messages"
}
[Tool Result] baa00bf spec(OBJ-013): FFmpeg encoder specification -- approved after 4-round deliberation
306fe35 spec(OBJ-031): gentle_float camera path preset specification
d3e98dd Specify OBJ-026: static camera path preset
065cb85 spec(OBJ-005): scene geometry type contract — PlaneSlot, SceneGeometry, registry
04524be spec(OBJ-006): camera path type contract — presets, registry, and validation
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-016/meta.json

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
	nodes/OBJ-010/transcript.md
	nodes/OBJ-013/transcript.md
	nodes/OBJ-016/output.md
	nodes/OBJ-026/transcript.md
	nodes/OBJ-031/transcript.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-016/output.md nodes/OBJ-016/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-016): manifest loader and validator behavioral specification\n\nDefines two-phase validation pipeline (structural Zod parsing + semantic\nregistry validation), all-at-once error collection, Zod-to-ManifestError\nmapping, skip-on-unknown pattern, floating-point tolerances for overlap\nand audio duration checks, and FILE_READ_ERROR code for non-ENOENT fs\nerrors. Covers TC-07 (validation catches common authoring errors).\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-016 spec files"
}
[Tool Result] [master e320132] spec(OBJ-016): manifest loader and validator behavioral specification
 2 files changed, 414 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-016/output.md
Spec committed. The OBJ-016 specification is finalized with:

- **Two-phase validation**: Structural (Zod `safeParse`) → Semantic (registry-backed checks), with Phase 2 skipped if Phase 1 fails
- **All-at-once error collection**: Both phases collect every error before returning, satisfying C-10's "fail clearly" mandate
- **Skip-on-unknown pattern**: Unknown geometry skips slot/compatibility checks; unknown camera skips FOV checks — no misleading downstream errors
- **`FILE_READ_ERROR`**: New OBJ-016-originated code distinguishing permission/EISDIR errors from ENOENT
- **Standard `path` format**: ASCII dot-notation with `[N]` indices throughout; cross-scene errors use first scene's original array index with second scene named in message
- **Floating-point tolerances**: ±0.01s for audio duration, +0.001s for overlap validity checks
- **36 acceptance criteria** covering structural validation, semantic validation, pipeline composition, file I/O, and general invariants
- **43 test cases** mapped to TC-07
