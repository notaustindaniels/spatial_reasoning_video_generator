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

7. **Duplicate scene IDs** — `DUPLICATE_SCENE_ID` for every scene whose `id` appears more than once. Error is reported on the second (and subsequent) occurrence(s), with `path` pointing to the duplicate scene's original array index.
8. **Scene ordering** — Sort scenes by `start_time` using a stable sort (preserving array order for equal `start_time` values; Node.js 12+ guarantees stable `Array.prototype.sort()`). If sorted order differs from array order, emit `SCENE_ORDER_MISMATCH` warning once (not per-scene), with `path` set to `"scenes"`.
9. **Scene overlap analysis** — For each consecutive pair (A, B) in sorted order, compute `overlap = max(0, (A.start_time + A.duration) - B.start_time)`. Apply E-03 rules from OBJ-004. Emit `SCENE_OVERLAP` error if overlap is invalid.
10. **Scene gap analysis** — For each consecutive pair (A, B) in sorted order, if `B.start_time > A.start_time + A.duration`, emit `SCENE_GAP` warning.
11. **Crossfade adjacency** — `CROSSFADE_NO_ADJACENT` if first scene (by sorted order) has `transition_in.type === "crossfade"`, or last scene has `transition_out.type === "crossfade"`.
12. **Audio duration mismatch** — `AUDIO_DURATION_MISMATCH` (warning) if `manifest.composition.audio?.duration` is defined and differs from `computeTotalDuration(manifest)`. Comparison uses a tolerance of ±0.01 seconds to avoid floating-point false positives.

**Key invariant:** When a per-scene check is skipped due to an upstream failure (e.g., unknown geometry makes slot checks meaningless), the skip is silent — no placeholder error is emitted. The upstream error is sufficient.

**Key invariant:** All checks run to completion. A failure in check 1 does not prevent check 7-12 from running. Per-scene skips are scoped to that scene only.

**Path index rule:** All `path` values referencing a scene use the scene's **original array index** from the manifest (not its position after sorting by `start_time`). This ensures consumers can locate the scene in the source JSON.

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

**Choice:** When `scene.geometry` is unknown, skip slot checks (MISSING_REQUIRED_SLOT, UNKNOWN_SLOT) and camera compatibility check (INCOMPATIBLE_CAMERA) for that scene. When `scene.camera` is unknown, skip FOV support check.

**Rationale:** Checking slots against an unknown geometry produces misleading errors. The upstream error is sufficient and actionable.

### D-05: Floating-Point Tolerance for Audio Duration Comparison

**Choice:** `AUDIO_DURATION_MISMATCH` uses ±0.01 second tolerance. `|audio.duration - computeTotalDuration()| > 0.01` triggers the warning.

**Rationale:** Scene durations from different sources and floating-point arithmetic in duration summing can produce tiny discrepancies. A 10ms tolerance avoids false positives.

### D-06: Scene Overlap — Tolerance for Floating-Point

**Choice:** Overlap computation: `overlap = Math.max(0, (A.start_time + A.duration) - B.start_time)`. For the validity check in E-03 rule 3, the comparison uses `overlap <= min(A.transition_out.duration, B.transition_in.duration) + 0.001` (1ms tolerance).

**Rationale:** Avoids rejecting overlaps that are equal within floating-point precision.

### D-07: `path` Format — Standard JSON-Path-Like for All Errors

**Choice:** The `path` field always uses standard dot-notation with `[N]` array indices. For per-scene errors: `"scenes[0].geometry"`, `"scenes[2].planes.floor"`. For cross-scene errors (SCENE_OVERLAP, SCENE_GAP): `path` references the first scene only (e.g., `"scenes[1]"`), using the scene's **original array index**; the second scene is identified by `id` in the `message` text. For manifest-level warnings (SCENE_ORDER_MISMATCH): `path` is `"scenes"`. For composition-level warnings (AUDIO_DURATION_MISMATCH): `path` is `"composition.audio.duration"`. For file-level errors: `path` is `""`.

**Rationale:** Keeps `path` as a single, ASCII, machine-parseable JSON-path-like reference. Cross-scene context is conveyed in the human-readable `message`, which already names both scenes by `id`.

### D-08: Duplicate Scene ID — Report on Second Occurrence

**Choice:** When duplicate IDs are found, the error is reported on every occurrence after the first, with `path` pointing to the duplicate scene's original array index.

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
- [ ] **AC-09:** When `scene.geometry` is unknown, `MISSING_REQUIRED_SLOT`, `UNKNOWN_SLOT`, and `INCOMPATIBLE_CAMERA` checks are skipped for that scene (no misleading downstream errors).
- [ ] **AC-10:** When `scene.camera` is unknown, `FOV_WITHOUT_SUPPORT` check is skipped for that scene.
- [ ] **AC-11:** `UNKNOWN_GEOMETRY` message includes the geometry name and lists available geometries from the registry.
- [ ] **AC-12:** `UNKNOWN_CAMERA` message includes the camera name and lists available cameras from the registry.
- [ ] **AC-13:** `INCOMPATIBLE_CAMERA` message names both the camera and geometry and lists compatible cameras.
- [ ] **AC-14:** `MISSING_REQUIRED_SLOT` message names the missing slot and the geometry.
- [ ] **AC-15:** `UNKNOWN_SLOT` message names the unknown slot and lists valid slots for the geometry.
- [ ] **AC-16:** `DUPLICATE_SCENE_ID` is reported on the second (and any subsequent) occurrence, not the first.
- [ ] **AC-17:** `SCENE_OVERLAP` error message describes the overlap duration and explains why it's invalid.
- [ ] **AC-18:** `SCENE_GAP` warning includes the gap duration and the time range.
- [ ] **AC-19:** `SCENE_ORDER_MISMATCH` is emitted at most once, not per-scene, with `path` set to `"scenes"`.
- [ ] **AC-20:** `AUDIO_DURATION_MISMATCH` is a warning (not error) — `loadManifest()` still returns `success: true` when this is the only issue.
- [ ] **AC-21:** Audio duration comparison uses ±0.01s tolerance — a 0.005s difference does NOT trigger the warning.
- [ ] **AC-22:** `CROSSFADE_NO_ADJACENT` on first scene's `transition_in` and last scene's `transition_out`.
- [ ] **AC-23:** `FOV_WITHOUT_SUPPORT` is a warning (not error).
- [ ] **AC-24:** When the registry is completely empty, `UNKNOWN_GEOMETRY` messages include the "Did you forget to register geometries?" hint.
- [ ] **AC-25:** All `path` values referencing scenes use the scene's original array index, not the sorted position.

### Combined Pipeline (`loadManifest`)

- [ ] **AC-26:** `loadManifest()` runs Phase 1 first. If Phase 1 fails, returns structural errors only — Phase 2 is not run.
- [ ] **AC-27:** `loadManifest()` returns `success: true` only when zero errors exist across both phases. Warnings alone do not block success.
- [ ] **AC-28:** When Phase 2 produces both errors and warnings and `loadManifest()` returns `success: false`, both errors and warnings appear in the `errors` array. Warnings are distinguishable by `severity: "warning"`.

### File Loading (`loadManifestFromFile`)

- [ ] **AC-29:** Nonexistent file path returns `{ success: false, errors: [{ code: "FILE_NOT_FOUND", ... }] }`.
- [ ] **AC-30:** File with invalid JSON returns `{ success: false, errors: [{ code: "INVALID_JSON", ... }] }` and the message includes the parse error details.
- [ ] **AC-31:** Valid JSON file is passed through `loadManifest()` and returns its result.
- [ ] **AC-32:** `loadManifestFromFile()` never throws — file I/O errors are caught and returned as `ManifestResult`.
- [ ] **AC-33:** Permission-denied or other non-ENOENT file errors return `{ success: false, errors: [{ code: "FILE_READ_ERROR", ... }] }` with the OS error message included.

### General

- [ ] **AC-34:** `computeTotalDuration()` returns `max(start_time + duration)` across all scenes. Verified with overlapping scenes, sequential scenes, and single-scene manifests.
- [ ] **AC-35:** All `ManifestError` objects have non-empty `code`, non-empty `message`, and valid `severity`. `path` is non-empty for field-level errors and `""` for file-level errors.
- [ ] **AC-36:** The loader module has no side effects on import. No global state. The registry is passed as a parameter.

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
26. Scene order mismatch → single SCENE_ORDER_MISMATCH warning with path `"scenes"`.
27. Path values use original array indices after sorting.

**`loadManifest()` pipeline tests:**
28. Phase 1 failure → returns structural errors, Phase 2 not run.
29. Phase 1 success + Phase 2 failure → returns semantic errors.
30. Phase 1 success + Phase 2 warnings only → success: true with warnings.
31. Phase 1 success + Phase 2 errors + warnings → success: false, both in errors array, distinguishable by severity.

**`computeTotalDuration()` tests:**
32. Sequential scenes → correct sum.
33. Overlapping scenes → max(start_time + duration).
34. Single scene → start_time + duration.
35. Non-sequential array order → correct max regardless of array order.

### Unit Tests: `test/unit/manifest/loader-file.test.ts`

36. Valid JSON fixture file → success.
37. Nonexistent path → FILE_NOT_FOUND, no throw.
38. File with `{invalid json}` → INVALID_JSON with parse error details.
39. File containing `null` → valid JSON, then parseManifest handles it.
40. Empty file → INVALID_JSON.
41. Permission-denied path → FILE_READ_ERROR (requires test setup for EACCES, or mock `fs`).
42. Directory path → FILE_READ_ERROR.

### Integration Test: `test/integration/manifest-roundtrip.test.ts`

43. Load `test/fixtures/valid-manifest.json`, register mock geometries and cameras matching the fixture, call `loadManifestFromFile()`, assert `success: true`, verify parsed manifest matches expected typed structure.

### Relevant Testable Claims

- **TC-07:** Tests 11-27 directly verify "manifest validation catches common authoring errors."

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
