# Specification: OBJ-017 — Geometry-Specific Structural Manifest Validation

## Summary

OBJ-017 defines a composable validation module that enforces geometry-specific structural correctness in depthkit manifests. It validates that: (1) each scene's `geometry` field references a registered geometry, (2) each scene's `planes` keys exactly match the geometry's declared slot names (no unknown keys, no missing required slots), and (3) error messages are actionable — naming the offending scene, the geometry, the missing/unknown slot, and listing valid alternatives. This module is consumed by `validateManifestSemantics()` (OBJ-004) as the geometry-specific validation pass. Camera-geometry compatibility validation is explicitly out of scope (OBJ-041). OBJ-017 is the authoritative source for the `UNKNOWN_GEOMETRY`, `MISSING_REQUIRED_SLOT`, and `UNKNOWN_SLOT` error codes defined by OBJ-004. No other validation module should emit these codes.

## Interface Contract

### Module: `src/manifest/validate-geometry.ts`

```typescript
import type { Manifest, Scene, ManifestError } from './schema';

/**
 * Minimal slot information needed for structural validation.
 * Both OBJ-004's PlaneSlotDef and OBJ-005's PlaneSlot structurally
 * satisfy this interface (PlaneSlot is a superset), so the bridge
 * code in loader.ts can use either registry without conversion.
 */
export interface GeometrySlotInfo {
  required: boolean;
  description: string;
}

/**
 * Minimal geometry information needed for structural slot validation.
 * Both OBJ-004's GeometryRegistration and OBJ-005's SceneGeometry
 * structurally satisfy this interface, enabling the bridge code in
 * loader.ts to pass either registry's entries without conversion.
 *
 * This interface intentionally excludes compatible_cameras,
 * default_camera, fog, and spatial data (positions, rotations) —
 * none of which are needed for structural slot validation.
 */
export interface ValidatableGeometry {
  name: string;
  slots: Record<string, GeometrySlotInfo>;
}

/**
 * Geometry resolution function type.
 * Abstracts the geometry lookup so this module doesn't directly
 * import any global registry — enabling isolated unit testing
 * with mock geometries.
 *
 * @param name - The geometry name from the scene's `geometry` field.
 * @returns The geometry definition, or undefined if not registered.
 */
export type GeometryResolver = (name: string) => ValidatableGeometry | undefined;

/**
 * Function type that returns all known geometry names.
 * Used for error messages ("expected one of: stage, tunnel, ...").
 */
export type GeometryNameLister = () => readonly string[];

/**
 * Validates geometry-specific structural correctness for all scenes
 * in a manifest. Checks geometry existence and plane-slot matching.
 *
 * Does NOT validate:
 * - Camera existence or camera-geometry compatibility (OBJ-041)
 * - Scene timing, transitions, audio (other semantic validators)
 * - Zod structural shape (already passed in Phase 1)
 *
 * This is the authoritative source for UNKNOWN_GEOMETRY,
 * MISSING_REQUIRED_SLOT, and UNKNOWN_SLOT error codes.
 * No other validation module should emit these codes.
 *
 * @param manifest - A structurally valid Manifest (passed Phase 1 Zod parsing).
 * @param resolveGeometry - Lookup function for geometry definitions.
 * @param listGeometryNames - Function returning all registered geometry names.
 * @returns Array of ManifestErrors. Empty array = all scenes pass geometry validation.
 */
export function validateGeometrySlots(
  manifest: Manifest,
  resolveGeometry: GeometryResolver,
  listGeometryNames: GeometryNameLister,
): ManifestError[];

/**
 * Validates geometry-specific structural correctness for a single scene.
 * Extracted for reuse and testability.
 *
 * @param scene - A single scene from the manifest.
 * @param sceneIndex - The scene's index in the manifest's scenes array (for error paths).
 * @param resolveGeometry - Lookup function for geometry definitions.
 * @param listGeometryNames - Function returning all registered geometry names.
 * @returns Array of ManifestErrors for this scene.
 */
export function validateSceneGeometrySlots(
  scene: Scene,
  sceneIndex: number,
  resolveGeometry: GeometryResolver,
  listGeometryNames: GeometryNameLister,
): ManifestError[];
```

### Error Codes Produced

This module produces exactly three of the error codes defined by OBJ-004:

| Code | Severity | Condition | Error Path Pattern |
|------|----------|-----------|-------------------|
| `UNKNOWN_GEOMETRY` | `"error"` | `scene.geometry` is not found by `resolveGeometry` | `scenes[{i}].geometry` |
| `MISSING_REQUIRED_SLOT` | `"error"` | A required slot (per geometry definition) has no key in `scene.planes` | `scenes[{i}].planes` |
| `UNKNOWN_SLOT` | `"error"` | A key in `scene.planes` is not a defined slot for the geometry | `scenes[{i}].planes.{key}` |

### Error Message Formats

Each error message must be actionable per OBJ-004 AC-34. The exact message templates:

**`UNKNOWN_GEOMETRY`:**
```
Scene '{scene.id}' references unknown geometry '{scene.geometry}'. Registered geometries: {comma-separated list from listGeometryNames()}.
```
When no geometries are registered:
```
Scene '{scene.id}' references unknown geometry '{scene.geometry}'. No geometries are registered. Did you forget to import geometry modules before validation?
```

**`MISSING_REQUIRED_SLOT`:**
```
Scene '{scene.id}' (geometry '{scene.geometry}') is missing required plane slot '{slotName}' ({slot.description}).
```
One error per missing required slot. If a scene is missing 3 required slots, 3 separate `ManifestError` objects are returned.

**`UNKNOWN_SLOT`:**
```
Scene '{scene.id}' (geometry '{scene.geometry}') has unknown plane slot '{key}'. Valid slots for '{scene.geometry}': {comma-separated list of all slot names}.
```
One error per unknown slot key.

### Integration with `validateManifestSemantics()`

OBJ-004 defined `validateManifestSemantics()` as the entry point for all semantic validation. OBJ-017's `validateGeometrySlots()` is composed into that function. The integration pattern:

```typescript
// Inside src/manifest/loader.ts (OBJ-004's validateManifestSemantics)
// This shows how OBJ-017 plugs in — NOT implementation code for OBJ-017.

export function validateManifestSemantics(
  manifest: Manifest,
  registry: ManifestRegistry,
): ManifestError[] {
  const errors: ManifestError[] = [];

  // OBJ-017: Geometry-specific slot validation
  // Bridge: ManifestRegistry.geometries stores GeometryRegistration,
  // which structurally satisfies ValidatableGeometry.
  errors.push(...validateGeometrySlots(
    manifest,
    (name) => registry.geometries.get(name),  // GeometryRegistration satisfies ValidatableGeometry
    () => [...registry.geometries.keys()],
  ));

  // OBJ-041 (future): Camera-geometry compatibility
  // errors.push(...validateCameraCompatibility(manifest, registry));

  // Other semantic checks (scene timing, transitions, audio, etc.)
  // ...

  return errors;
}
```

The `ValidatableGeometry` interface is satisfied by both `GeometryRegistration` (from OBJ-004's `ManifestRegistry`) and `SceneGeometry` (from OBJ-005's `GeometryRegistry`). The bridge code in `loader.ts` can pass entries from either registry without conversion.

## Design Decisions

### D-01: Separate Module, Not Inline in `loader.ts`

**Choice:** Geometry-slot validation lives in its own module (`validate-geometry.ts`) rather than being inlined in `validateManifestSemantics()`.

**Rationale:** (a) OBJ-004 spec defines `validateManifestSemantics()` as the composition point for multiple validation concerns. Keeping geometry validation in its own module allows OBJ-041 to add camera compatibility checks in a separate module with the same pattern. (b) Testability — the module can be unit-tested with mock geometries without instantiating a full `ManifestRegistry`. (c) Follows OBJ-017's metadata: "structural validation only — spatial compatibility rules come from OBJ-041 and are additive."

### D-02: Function Injection Over Direct Registry Import

**Choice:** `validateGeometrySlots` accepts `GeometryResolver` and `GeometryNameLister` function parameters rather than importing `getGeometry`/`getGeometryNames` directly from OBJ-005's registry.

**Rationale:** (a) Testability — unit tests inject mock resolvers returning test geometries without triggering the global registry's lock-on-first-read behavior (OBJ-005 D10). No need for `_resetRegistry()` hacks. (b) Decoupling — the module depends only on types from OBJ-004 and its own minimal interfaces. (c) OBJ-004's `ManifestRegistry` and OBJ-005's `GeometryRegistry` are separate registries; the bridge logic belongs in the caller, not in this module.

### D-03: Early Exit on `UNKNOWN_GEOMETRY`

**Choice:** When a scene's geometry is not found, emit `UNKNOWN_GEOMETRY` and skip slot validation for that scene. Do NOT also emit `MISSING_REQUIRED_SLOT` or `UNKNOWN_SLOT` errors for that scene.

**Rationale:** If the geometry is unknown, the engine has no slot definitions to validate against. Emitting "missing required slot" errors would be misleading — the actual problem is the geometry name, not the slots. This follows the principle of reporting the root cause, not derived symptoms. Mirrors OBJ-004's Phase 1/Phase 2 split where structural failure skips semantic validation.

### D-04: One Error Per Violation, Not Aggregated

**Choice:** Each missing required slot and each unknown slot produces its own `ManifestError` with its own `path`, `code`, and `message`. If a scene has 3 missing required slots and 2 unknown slots, 5 errors are returned.

**Rationale:** OBJ-004 AC-34 requires actionable messages naming the specific field/value. Individual errors allow error-reporting UIs (CLI, n8n response) to display them as a list, and enable LLM authors to fix each issue independently.

### D-05: Slot Description Included in `MISSING_REQUIRED_SLOT` Messages

**Choice:** The error message for `MISSING_REQUIRED_SLOT` includes the slot's `description` field from the geometry definition (e.g., "Ground surface").

**Rationale:** The LLM author may not know what a slot name like `end_wall` means in context. Including the description ("Distant end of tunnel") makes the error self-correcting — the author can immediately understand what image to assign without looking up the geometry documentation. Supports C-06 (blind-authorable).

### D-06: Valid Slot Names Listed in `UNKNOWN_SLOT` Messages

**Choice:** `UNKNOWN_SLOT` error messages list all valid slot names for the geometry.

**Rationale:** Follows OBJ-004 AC-21: "Error message names the unknown key and lists valid slots." Enables the LLM author to correct the typo or wrong key immediately.

### D-07: `INCOMPATIBLE_CAMERA` Is NOT Produced by This Module

**Choice:** Camera-geometry compatibility validation is explicitly excluded from OBJ-017, per the metadata boundary: "spatial compatibility rules (camera+geometry compatibility) come from OBJ-041."

**Rationale:** OBJ-041 depends on both OBJ-005 (geometries) and OBJ-006 (camera paths). OBJ-017 depends only on OBJ-004 and OBJ-005. Keeping camera validation in OBJ-041 maintains clean dependency boundaries. OBJ-004's `validateManifestSemantics()` composes both.

### D-08: Per-Scene Validation Function Exposed

**Choice:** Both `validateGeometrySlots` (all scenes) and `validateSceneGeometrySlots` (single scene) are exported.

**Rationale:** The per-scene function enables focused unit testing of individual validation scenarios without constructing full manifests.

### D-09: Minimal `ValidatableGeometry` Interface Over Direct OBJ-005 Import

**Choice:** OBJ-017 defines its own `ValidatableGeometry` and `GeometrySlotInfo` interfaces containing only the fields needed for structural validation (`name`, `slots` with `required` and `description`). It does NOT import `SceneGeometry` from OBJ-005 or any runtime functions.

**Rationale:** OBJ-004's `ManifestRegistry` stores `GeometryRegistration` objects (with `PlaneSlotDef` slots), while OBJ-005's `GeometryRegistry` stores `SceneGeometry` objects (with `PlaneSlot` slots). These are different types — `PlaneSlotDef` lacks the spatial fields (`position`, `rotation`, `size`) that `PlaneSlot` has. The minimal `ValidatableGeometry` interface is structurally satisfied by both `GeometryRegistration` and `SceneGeometry`, allowing the bridge code in `loader.ts` to pass entries from either registry without conversion or type assertions. This also means OBJ-017 has zero runtime imports from OBJ-005 — it depends only on OBJ-004 types and its own interfaces.

### D-10: `MISSING_REQUIRED_SLOT` Path Points to Parent `planes` Object

**Choice:** The error path for `MISSING_REQUIRED_SLOT` is `scenes[{i}].planes` (the parent object), not `scenes[{i}].planes.{slotName}` (the absent key).

**Rationale:** The error describes the *absence* of a key. Pointing to a non-existent path would be misleading. The missing slot name is communicated in the `message` text. The `path` points to the object that the author needs to modify (add the missing key to `planes`).

### D-11: Deterministic Error Ordering

**Choice:** Within a single scene's validation results, errors are ordered as follows: (1) `UNKNOWN_GEOMETRY` (if applicable — and if emitted, no other errors for that scene per D-03), (2) `MISSING_REQUIRED_SLOT` errors sorted alphabetically by slot name, (3) `UNKNOWN_SLOT` errors sorted alphabetically by key name. Across scenes, errors are ordered by scene index.

**Rationale:** Deterministic ordering ensures reproducible test assertions and consistent error output across runs. Alphabetical ordering within each category is simple and predictable.

## Acceptance Criteria

- [ ] **AC-01:** `validateGeometrySlots()` returns an empty array for a manifest where every scene's geometry is registered and all required slots are provided with no unknown slots.
- [ ] **AC-02:** `validateGeometrySlots()` returns `UNKNOWN_GEOMETRY` error for a scene referencing an unregistered geometry. The error `path` is `scenes[{i}].geometry`. The error `message` includes the geometry name and lists all registered geometries.
- [ ] **AC-03:** When no geometries are registered (empty registry), `UNKNOWN_GEOMETRY` message includes "No geometries are registered. Did you forget to import geometry modules before validation?"
- [ ] **AC-04:** `validateGeometrySlots()` returns `MISSING_REQUIRED_SLOT` error for each required slot missing from `scene.planes`. The error `path` is `scenes[{i}].planes`. The error `message` includes the scene ID, geometry name, slot name, and slot description.
- [ ] **AC-05:** `validateGeometrySlots()` returns `UNKNOWN_SLOT` error for each key in `scene.planes` that is not a defined slot in the geometry. The error `path` is `scenes[{i}].planes.{key}`. The error `message` includes the scene ID, geometry name, unknown key, and lists all valid slot names.
- [ ] **AC-06:** When a scene's geometry is unknown (`UNKNOWN_GEOMETRY`), no `MISSING_REQUIRED_SLOT` or `UNKNOWN_SLOT` errors are emitted for that scene (D-03 early exit).
- [ ] **AC-07:** Optional slots that are omitted from `scene.planes` do NOT produce errors.
- [ ] **AC-08:** Optional slots that ARE provided in `scene.planes` do NOT produce `UNKNOWN_SLOT` errors.
- [ ] **AC-09:** A scene with `planes: {}` (empty) produces one `MISSING_REQUIRED_SLOT` error per required slot in the geometry (OBJ-004 E-01).
- [ ] **AC-10:** A manifest with multiple scenes validates each scene independently — errors from scene 0 do not affect validation of scene 1.
- [ ] **AC-11:** Every returned `ManifestError` has non-empty `path`, `code`, `message`, and valid `severity` (`"error"` for all three codes produced by this module).
- [ ] **AC-12:** Error paths use zero-indexed array notation: `scenes[0]`, `scenes[1]`, etc.
- [ ] **AC-13:** The module imports only types from OBJ-004 (`Manifest`, `Scene`, `ManifestError`). It defines its own `ValidatableGeometry` and `GeometrySlotInfo` interfaces. No direct imports from OBJ-005, the geometry registry, or Three.js. Zero runtime dependencies beyond standard JavaScript.
- [ ] **AC-14:** The module is testable with mock geometry definitions passed via `GeometryResolver` — no global state dependency.
- [ ] **AC-15:** A scene providing all required slots plus some optional slots and no unknown slots produces zero errors.
- [ ] **AC-16:** Covers TC-07 scenarios for geometry-slot validation: unknown geometry, missing required slots, unknown slots, geometry name existence.
- [ ] **AC-17:** Within a single scene's errors, `MISSING_REQUIRED_SLOT` errors are sorted alphabetically by slot name, and `UNKNOWN_SLOT` errors are sorted alphabetically by key name. Across scenes, errors are ordered by scene index.
- [ ] **AC-18:** `ValidatableGeometry` is structurally compatible with both OBJ-004's `GeometryRegistration` and OBJ-005's `SceneGeometry` — both satisfy the interface without conversion.

## Edge Cases and Error Handling

### E-01: Scene With `planes: {}` (Empty Object)
Produces one `MISSING_REQUIRED_SLOT` per required slot, sorted alphabetically by slot name. Does not produce `UNKNOWN_SLOT` (there are no keys to be unknown). Consistent with OBJ-004 E-01.

### E-02: Scene With Only Unknown Slots
A scene providing only unrecognized slot keys (e.g., `planes: { "foo": {...}, "bar": {...} }`) produces both `UNKNOWN_SLOT` errors for each unknown key AND `MISSING_REQUIRED_SLOT` errors for each missing required slot. These are independent checks — unknown keys don't satisfy required slots, and missing slots aren't caused by unknown keys.

### E-03: Scene With Some Required, Some Unknown, Some Optional
Each plane key is evaluated independently:
- Keys matching required slots: satisfy the requirement, no error.
- Keys matching optional slots: accepted, no error.
- Keys not matching any slot: `UNKNOWN_SLOT` error.
- Required slots with no matching key: `MISSING_REQUIRED_SLOT` error.

### E-04: Geometry With All Optional Slots
Cannot happen — OBJ-005's `validateGeometryDefinition` (AC-06, rule 4) requires at least one required slot. The guard is upstream in OBJ-005, not here.

### E-05: Geometry With No Optional Slots
All slots are required. Every slot must be present in `scene.planes`. Any extra key is `UNKNOWN_SLOT`.

### E-06: Multiple Scenes With Same Geometry
Each scene is validated independently against the same geometry definition. Errors reference the specific scene index and ID.

### E-07: Multiple Scenes With Different Geometries
Each scene resolves its own geometry. Scene 0 might use "tunnel" and scene 1 might use "stage" — each validated against its own slot contract.

### E-08: Case-Sensitive Slot Key Matching
Slot key matching is exact string comparison, case-sensitive. `"Floor"` does not match `"floor"`. The `UNKNOWN_SLOT` error will list valid keys (all lowercase per OBJ-005 naming convention), making the fix obvious.

### E-09: Manifest With 0 Scenes
Cannot happen — `ManifestSchema` requires `scenes: z.array(SceneSchema).min(1)` (OBJ-004). The module receives a structurally valid manifest.

### E-10: Geometry Resolver Returns Undefined After First Call Returns Defined
Not possible in normal operation (registry is frozen after first read). The module is stateless per-call — each `resolveGeometry(name)` call is independent.

### E-11: Plane Slot Key Is Empty String
The key `""` would survive Zod structural parsing (`z.record(z.string(), PlaneRefSchema)`). In geometry validation, it would not match any slot (OBJ-005 slot names must match `/^[a-z][a-z0-9_]*$/`), so it would produce `UNKNOWN_SLOT`.

## Test Strategy

### Unit Tests: `test/unit/manifest/validate-geometry.test.ts`

All tests use mock `GeometryResolver` and `GeometryNameLister` functions — no global registry.

**Define mock geometries for testing (as `ValidatableGeometry`):**
- `mockTunnel`: 4 required slots (`floor`, `left_wall`, `right_wall`, `end_wall`), 1 optional (`ceiling`). Mirrors seed Section 8.6.
- `mockStage`: 2 required slots (`backdrop`, `subject`), 1 optional (`floor`).
- `mockCloseUp`: 1 required slot (`subject`), no optional slots.

**Test cases for `validateSceneGeometrySlots`:**

1. **Valid scene — all required slots provided:** tunnel with `floor`, `left_wall`, `right_wall`, `end_wall` → empty array.
2. **Valid scene — all required + optional:** tunnel with all 5 slots → empty array.
3. **Valid scene — required + some optional:** tunnel with 4 required + `ceiling` → empty array.
4. **Unknown geometry:** scene with `geometry: "nonexistent"`, 2 registered geometries → one `UNKNOWN_GEOMETRY` error, message lists both registered names.
5. **Unknown geometry, empty registry:** scene with `geometry: "tunnel"`, no registered geometries → `UNKNOWN_GEOMETRY` with "No geometries are registered" message.
6. **Unknown geometry skips slot checks:** scene with unknown geometry and `planes: {}` → only `UNKNOWN_GEOMETRY`, no `MISSING_REQUIRED_SLOT`.
7. **Missing one required slot:** tunnel scene omitting `floor` → one `MISSING_REQUIRED_SLOT` error for `floor`, message includes description "Ground surface".
8. **Missing all required slots:** tunnel scene with `planes: {}` → 4 `MISSING_REQUIRED_SLOT` errors (one per required slot), sorted alphabetically: `end_wall`, `floor`, `left_wall`, `right_wall`.
9. **Missing multiple required slots:** tunnel scene with only `floor` → 3 `MISSING_REQUIRED_SLOT` errors for the other 3, sorted alphabetically.
10. **One unknown slot:** tunnel scene with required slots + `"bogus"` key → one `UNKNOWN_SLOT` error, message lists all 5 valid slots.
11. **Multiple unknown slots:** scene with `"foo"` and `"bar"` → 2 `UNKNOWN_SLOT` errors, sorted alphabetically: `bar`, `foo`.
12. **Mixed: missing required + unknown slots:** tunnel with `floor` + `"foo"` → `MISSING_REQUIRED_SLOT` for 3 missing (alphabetical) then `UNKNOWN_SLOT` for `"foo"`.
13. **Optional slot omitted:** tunnel without `ceiling` but all required present → empty array.
14. **Case sensitivity:** tunnel scene with `"Floor"` instead of `"floor"` → `UNKNOWN_SLOT` for `"Floor"` + `MISSING_REQUIRED_SLOT` for `"floor"`.
15. **Empty string key:** scene with `"": { src: "x.png" }` → `UNKNOWN_SLOT`.
16. **Geometry with single required slot (close_up):** scene with `subject` → empty. Scene without `subject` → `MISSING_REQUIRED_SLOT`.

**Test cases for `validateGeometrySlots` (multi-scene):**

17. **Multi-scene, all valid:** 2 scenes (tunnel + stage), all slots correct → empty array.
18. **Multi-scene, one invalid:** scene 0 valid, scene 1 missing slot → errors only for scene 1, path starts with `scenes[1]`.
19. **Multi-scene, both invalid:** both scenes have errors → errors for both, correct indices.
20. **Multi-scene, different geometries:** scene 0 uses tunnel, scene 1 uses stage — slot validation uses correct geometry for each.
21. **Scene with unknown geometry + scene with missing slot:** both errors returned, independent.

**Error format tests:**

22. **Error path format:** `UNKNOWN_GEOMETRY` path is `scenes[0].geometry`, `MISSING_REQUIRED_SLOT` path is `scenes[0].planes`, `UNKNOWN_SLOT` path is `scenes[0].planes.foo`.
23. **Error severity:** All three error codes return `severity: "error"`.
24. **Error code values:** Exactly `"UNKNOWN_GEOMETRY"`, `"MISSING_REQUIRED_SLOT"`, `"UNKNOWN_SLOT"`.
25. **Non-empty fields:** Every returned error has non-empty `path`, `code`, `message`.
26. **Scene ID in messages:** All error messages include the scene's `id` field value.

### Integration Test: `test/integration/manifest/geometry-validation.test.ts`

1. Register real geometry definitions (from OBJ-018+) via `registerGeometry()`. Construct a `GeometryResolver` bridging to the geometry registry. Validate a manifest with correct slot assignments → passes.
2. Same setup, validate a manifest with intentionally wrong slot keys → correct errors.
3. Call `loadManifest()` (OBJ-004 full pipeline) with geometry errors → geometry errors appear in the result's error array alongside any other semantic errors.

### Relevant Testable Claims

- **TC-07:** This module directly covers "planes that don't match the geometry's slot contract" and "geometry names that don't exist." TC-07's remaining scenarios (camera incompatibility, negative durations, overlapping timecodes, resolution mismatches) are covered by OBJ-041 and other validators in `validateManifestSemantics`.

## Integration Points

### Depends on

| Dependency | What OBJ-017 Imports |
|---|---|
| **OBJ-004** (Manifest Schema Core) | `Manifest`, `Scene`, `ManifestError` **types only**. OBJ-017's output is composed into OBJ-004's `validateManifestSemantics()`. |
| **OBJ-005** (Scene Geometry Type Contract) | **No imports.** OBJ-017 defines its own `ValidatableGeometry` and `GeometrySlotInfo` interfaces, which are structurally compatible with OBJ-005's `SceneGeometry` and `PlaneSlot`. The structural compatibility is verified by AC-18. |

### Consumed by

| Downstream | How It Uses OBJ-017 |
|---|---|
| **OBJ-004's `validateManifestSemantics()`** | Calls `validateGeometrySlots()` as one of several composed validation passes. Bridges between `ManifestRegistry.geometries` (which stores `GeometryRegistration`) and OBJ-017's `GeometryResolver` (which accepts `ValidatableGeometry`). The bridge is zero-cost: `GeometryRegistration` structurally satisfies `ValidatableGeometry`. OBJ-017 is the authoritative and sole source of `UNKNOWN_GEOMETRY`, `MISSING_REQUIRED_SLOT`, and `UNKNOWN_SLOT` error codes. |
| **OBJ-035** (Orchestrator) | Indirectly — via `loadManifest()` which calls `validateManifestSemantics()` which calls `validateGeometrySlots()`. |
| **OBJ-013** (CLI) | Indirectly — via `loadManifestFromFile()`. |

### File Placement

```
depthkit/
  src/
    manifest/
      schema.ts               # OBJ-004 (exists)
      loader.ts               # OBJ-004 (exists) — calls validateGeometrySlots
      validate-geometry.ts    # OBJ-017 — this module
  test/
    unit/
      manifest/
        validate-geometry.test.ts   # Unit tests with mock geometries
    integration/
      manifest/
        geometry-validation.test.ts # Integration tests with real registrations
```

## Open Questions

None. All design questions raised during deliberation were resolved and promoted to design decisions (D-09 through D-11).
