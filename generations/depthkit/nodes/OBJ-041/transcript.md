# Deliberation Transcript: OBJ-041

---

## Round 1 — spec_author

Looking at OBJ-041's metadata and its dependencies, let me read the current state of any existing files for this objective.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-041/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-040/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-069/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-069/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-040",
     3→  "description": "Plane sizing and oversizing system -- visible area calculation per Section 8.3 (visible_height = 2 * d * tan(FOV/2)), camera-motion-dependent oversizing factors to prevent edge reveals during camera movement, edge-reveal prevention math, AND texture-to-plane auto-sizing algorithm per Section 8.9 (how planes adapt dimensions from loaded texture aspect ratios while maintaining geometry spatial structure -- letterbox vs crop vs scale decisions).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-006", "OBJ-003", "OBJ-015"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 spatial feature. Expanded to include texture auto-sizing per Round 2 Issue 6. OBJ-015 dep added for texture aspect ratio data."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-069/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-069",
     3→  "description": "Edge reveal systematic validation -- test all geometry+camera combinations for edge reveals with the oversizing system applied. Verify that no camera path reveals the edge of any plane during its full motion range. Requires concrete geometry (OBJ-018) and camera (OBJ-027) implementations plus the oversizing system (OBJ-040) and compatibility rules (OBJ-041). Addresses TC-03 (perspective projection convincing).",
     4→  "category": "tuning",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-018", "OBJ-027", "OBJ-040", "OBJ-041", "OBJ-035"],
     9→  "visual_status": "needs_tuning",
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 tuning. High priority. Fixed deps per Round 2 Issue 3 to include concrete implementations."
    12→}
    13→
Let me also check the OBJ-017 metadata to understand the boundary between structural and spatial validation:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-017/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-017",
     3→  "description": "Geometry-specific structural manifest validation -- per-geometry Zod refinements ensuring plane keys in the manifest match the geometry's expected slot requirements (e.g., tunnel requires floor, left_wall, right_wall, end_wall). Enforces required vs optional slots, validates geometry name existence. Structural validation only -- spatial compatibility rules (camera+geometry compatibility) come from OBJ-041 and are additive. Covers TC-07.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-004", "OBJ-005"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Boundary clarification: OBJ-017 = structural correctness, OBJ-041 = spatial correctness."
    12→}
    13→
Now I have a clear picture. Let me propose the specification.

---

# Specification Proposal: OBJ-041 — Geometry-Camera Spatial Compatibility Validation

## Summary

OBJ-041 defines the spatial compatibility validation layer for depthkit manifests. It cross-references the geometry registry (OBJ-005) and camera path registry (OBJ-006) to enforce three categories of spatial correctness: (1) **compatibility validation** — a manifest's chosen camera path must be in the geometry's `compatible_cameras` list and vice versa, (2) **registry consistency validation** — all geometry-referenced camera names must exist in the camera registry and all camera-referenced geometry names must exist in the geometry registry, and (3) **oversizing sufficiency checks** — given a camera path's `OversizeRequirements` and a geometry's `PlaneSlot` sizes, planes must be large enough to prevent edge reveals. It also provides a **coverage analysis utility** for TC-08 (do 8 geometries cover the design space). This module sits between the type contracts (OBJ-005, OBJ-006) and manifest validation (OBJ-017), producing spatial validation rules that OBJ-017 can invoke additively on top of structural validation.

## Interface Contract

### Core Validation Types

```typescript
// src/validation/spatial-compatibility.ts

import type { SceneGeometry, GeometryRegistry } from '../scenes/geometries';
import type { CameraPathPreset, CameraPathRegistry, OversizeRequirements, CameraParams } from '../camera';
import type { Vec3 } from '../spatial/types';

/**
 * A single spatial validation error. More structured than a plain string
 * to enable programmatic error handling and actionable LLM feedback.
 */
export interface SpatialValidationError {
  /** Error category for filtering/grouping */
  category: 'compatibility' | 'registry_consistency' | 'oversizing';

  /** Identifier of the scene in the manifest (e.g., 'scene_001'), or null for registry-level errors */
  sceneId: string | null;

  /** Human-readable error message, actionable for an LLM author */
  message: string;

  /**
   * Suggested fix, phrased as an instruction the LLM can act on.
   * E.g., "Use one of: static, slow_push_forward, gentle_float"
   */
  suggestion: string;
}
```

### Scene-Level Compatibility Validation

```typescript
/**
 * Validates that a single manifest scene's camera path is spatially
 * compatible with its chosen geometry. This is the per-scene check
 * that OBJ-017 invokes for each scene in the manifest.
 *
 * Checks performed:
 * 1. The camera path name exists in the camera registry.
 * 2. The camera path name is in the geometry's compatible_cameras list.
 * 3. The geometry name is in the camera preset's compatibleGeometries list.
 * 4. If camera_params.offset is provided, the offset does not push
 *    oversizing requirements beyond plane capacity (delegates to
 *    oversizing check).
 *
 * This function does NOT validate geometry name existence or plane slot
 * keys — those are OBJ-017's structural validation responsibility.
 *
 * @param sceneId - The manifest scene's id (for error reporting).
 * @param geometryName - The geometry name from the manifest scene.
 * @param cameraName - The camera path name from the manifest scene.
 * @param cameraParams - Optional camera params from the manifest scene.
 * @param geometryRegistry - The geometry registry.
 * @param cameraRegistry - The camera path registry.
 * @returns Array of SpatialValidationError. Empty = valid.
 */
export function validateSceneSpatialCompatibility(
  sceneId: string,
  geometryName: string,
  cameraName: string,
  cameraParams: CameraParams | undefined,
  geometryRegistry: Readonly<GeometryRegistry>,
  cameraRegistry: Readonly<CameraPathRegistry>
): SpatialValidationError[];
```

### Registry-Level Consistency Validation

```typescript
/**
 * Validates bidirectional consistency between the geometry and camera
 * registries. This is a boot-time / development-time check, not a
 * per-manifest check. It ensures that the preset libraries are
 * internally consistent.
 *
 * Checks performed:
 * 1. For every geometry, every entry in compatible_cameras exists
 *    as a key in the camera registry.
 * 2. For every camera preset, every entry in compatibleGeometries
 *    exists as a key in the geometry registry.
 * 3. Bidirectional agreement: if geometry G lists camera C in
 *    compatible_cameras, then camera C must list geometry G in
 *    compatibleGeometries (and vice versa). Mismatches are errors.
 * 4. Every geometry has at least one compatible camera that exists
 *    in the camera registry (non-empty intersection).
 *
 * @param geometryRegistry - The full geometry registry.
 * @param cameraRegistry - The full camera path registry.
 * @returns Array of SpatialValidationError with sceneId = null.
 *   Empty = fully consistent.
 */
export function validateRegistryConsistency(
  geometryRegistry: Readonly<GeometryRegistry>,
  cameraRegistry: Readonly<CameraPathRegistry>
): SpatialValidationError[];
```

### Oversizing Sufficiency Validation

```typescript
/**
 * Result of an oversizing check for a single plane slot.
 */
export interface OversizingCheckResult {
  /** Slot name (e.g., 'floor', 'left_wall') */
  slotName: string;

  /** Whether the plane is large enough to prevent edge reveals */
  sufficient: boolean;

  /**
   * Required plane size [width, height] in world units to prevent
   * edge reveals, given the camera path's motion envelope.
   * Computed from visible area at the plane's depth + camera displacement.
   */
  requiredSize: readonly [number, number];

  /** Actual plane size from the geometry definition */
  actualSize: readonly [number, number];

  /**
   * The computed oversize factor needed. Values > actualSize/requiredSize
   * indicate the plane is too small. A factor of 1.0 means exact fit
   * (no margin). The recommendedOversizeFactor from the camera preset
   * is the minimum safe value.
   */
  effectiveOversizeFactor: number;
}

/**
 * Checks whether all planes in a geometry are large enough to prevent
 * edge reveals for a given camera path preset at a given speed.
 *
 * The algorithm:
 * 1. For each plane slot in the geometry:
 *    a. Compute the plane's distance from the camera's closest approach
 *       (using the camera's Z displacement and the plane's Z position).
 *    b. Compute the visible area at that distance using the camera's
 *       maximum FOV: visible_h = 2 * d * tan(maxFov/2),
 *       visible_w = visible_h * aspectRatio.
 *    c. Add the camera's displacement in X and Y axes (scaled by speed)
 *       plus any offset to the required visible area.
 *    d. For rotated planes (floor, ceiling, walls), project the
 *       visible area requirement onto the plane's surface using
 *       the plane's rotation. A floor plane (rotated -π/2 on X)
 *       needs depth coverage in its local Y that maps to the camera's
 *       Z displacement in world space.
 *    e. Compare the required size against the slot's defined size.
 *       If required > actual in either dimension, the plane is
 *       undersized.
 *
 * This is a conservative check — it uses worst-case camera position
 * (closest approach + maximum FOV) for each plane. The actual
 * visible area at most frames will be smaller.
 *
 * @param geometry - The scene geometry definition.
 * @param cameraPreset - The camera path preset.
 * @param speed - The camera_params.speed value (default 1.0).
 * @param offset - The camera_params.offset value (default [0,0,0]).
 * @param aspectRatio - Composition aspect ratio (width/height).
 * @returns Array of OversizingCheckResult, one per slot.
 */
export function checkOversizingSufficiency(
  geometry: SceneGeometry,
  cameraPreset: CameraPathPreset,
  speed: number,
  offset: Vec3,
  aspectRatio: number
): OversizingCheckResult[];

/**
 * Convenience wrapper that returns only SpatialValidationErrors for
 * planes that fail the oversizing check. Used by
 * validateSceneSpatialCompatibility when camera_params are provided.
 *
 * @param sceneId - For error reporting.
 * @param geometry - The scene geometry.
 * @param cameraPreset - The camera path preset.
 * @param speed - Camera params speed (default 1.0).
 * @param offset - Camera params offset (default [0,0,0]).
 * @param aspectRatio - Composition aspect ratio.
 * @returns Array of SpatialValidationError for undersized planes.
 */
export function validateOversizing(
  sceneId: string,
  geometry: SceneGeometry,
  cameraPreset: CameraPathPreset,
  speed: number,
  offset: Vec3,
  aspectRatio: number
): SpatialValidationError[];
```

### Coverage Analysis Utility

```typescript
// src/validation/coverage-analysis.ts

import type { GeometryRegistry } from '../scenes/geometries';
import type { CameraPathRegistry } from '../camera';

/**
 * A compatibility matrix entry showing which cameras work with
 * which geometries, for documentation and TC-08 analysis.
 */
export interface CompatibilityMatrixEntry {
  geometryName: string;
  cameraName: string;
  /** true if both sides declare compatibility */
  bidirectionallyCompatible: boolean;
  /** true if only the geometry lists the camera */
  geometryOnly: boolean;
  /** true if only the camera lists the geometry */
  cameraOnly: boolean;
}

/**
 * Coverage analysis summary for TC-08.
 */
export interface CoverageAnalysis {
  /** Total number of registered geometries */
  totalGeometries: number;

  /** Total number of registered camera presets */
  totalCameraPresets: number;

  /** Number of valid (bidirectionally compatible) geometry-camera pairs */
  totalCompatiblePairs: number;

  /** Geometries with no compatible cameras (registry errors) */
  orphanedGeometries: string[];

  /** Camera presets with no compatible geometries (registry errors) */
  orphanedCameras: string[];

  /**
   * The full compatibility matrix.
   * Only includes entries where at least one side declares compatibility.
   */
  matrix: CompatibilityMatrixEntry[];

  /**
   * Per-geometry summary: how many cameras are compatible.
   */
  geometryCoverage: Record<string, {
    compatibleCameraCount: number;
    compatibleCameras: string[];
  }>;

  /**
   * Per-camera summary: how many geometries are compatible.
   */
  cameraCoverage: Record<string, {
    compatibleGeometryCount: number;
    compatibleGeometries: string[];
  }>;
}

/**
 * Produces a coverage analysis report from the two registries.
 * Used for TC-08 evaluation, SKILL.md generation, and
 * development-time auditing.
 *
 * @param geometryRegistry - The full geometry registry.
 * @param cameraRegistry - The full camera path registry.
 * @returns CoverageAnalysis summary.
 */
export function analyzeCoverage(
  geometryRegistry: Readonly<GeometryRegistry>,
  cameraRegistry: Readonly<CameraPathRegistry>
): CoverageAnalysis;

/**
 * Formats the coverage analysis as a human-readable Markdown table.
 * Rows = geometries, columns = cameras. Cells show ✓ for
 * bidirectional compatibility, G→ for geometry-only, →C for
 * camera-only, and blank for no compatibility.
 *
 * @param analysis - The coverage analysis to format.
 * @returns Markdown string.
 */
export function formatCoverageMatrix(analysis: CoverageAnalysis): string;
```

### Module Exports

```typescript
// src/validation/index.ts (spatial compatibility exports)
// May be part of a broader validation barrel; placement TBD.

export type {
  SpatialValidationError,
  OversizingCheckResult,
  CompatibilityMatrixEntry,
  CoverageAnalysis,
} from './spatial-compatibility';

export {
  validateSceneSpatialCompatibility,
  validateRegistryConsistency,
  checkOversizingSufficiency,
  validateOversizing,
} from './spatial-compatibility';

export {
  analyzeCoverage,
  formatCoverageMatrix,
} from './coverage-analysis';
```

## Design Decisions

### D1: Three-tier validation — scene-level, registry-level, oversizing

**Decision:** Spatial compatibility is split into three distinct validation tiers:
1. **Scene-level compatibility** (`validateSceneSpatialCompatibility`) — invoked per-scene during manifest validation, checks that the specific geometry+camera combination in a manifest scene is valid.
2. **Registry-level consistency** (`validateRegistryConsistency`) — invoked once at boot/build time, checks that the geometry and camera registries are mutually consistent.
3. **Oversizing sufficiency** (`checkOversizingSufficiency`) — invoked per-scene when camera params (especially speed and offset) are provided, checks that planes are large enough.

**Rationale:** These have different invocation timing and different consumers. Scene-level is called by OBJ-017 during manifest validation. Registry-level is a development-time integrity check (run in CI/tests, not per-render). Oversizing is the most computationally intensive and depends on runtime parameters (speed, offset, aspect ratio). Separating them lets consumers invoke only what they need.

### D2: Bidirectional compatibility enforcement

**Decision:** If geometry G lists camera C in `compatible_cameras`, then camera C MUST list geometry G in `compatibleGeometries`, and vice versa. Mismatches are errors reported by `validateRegistryConsistency`.

**Rationale:** OBJ-005's `compatible_cameras` and OBJ-006's `compatibleGeometries` are redundant by design (D7 in OBJ-005 explains why: avoiding circular dependencies between OBJ-005 and OBJ-006). Since they're maintained separately, they can drift. Bidirectional enforcement catches drift. The alternative — treating one side as authoritative — would make the other side's list misleading.

**Consequence:** When a new geometry is added (e.g., OBJ-022 `portal`), both the geometry's `compatible_cameras` and each compatible camera's `compatibleGeometries` must be updated simultaneously. `validateRegistryConsistency` catches omissions.

### D3: Scene-level validation assumes geometry exists

**Decision:** `validateSceneSpatialCompatibility` does NOT validate geometry name existence. It assumes the geometry has already been resolved by OBJ-017's structural validation. If the geometry name doesn't exist in the registry, the function skips compatibility checks and returns no errors (the structural validator already caught this).

**Rationale:** The boundary between OBJ-017 and OBJ-041 is: OBJ-017 validates structure (geometry exists, plane keys match slots), OBJ-041 validates spatial compatibility (camera works with geometry, planes are large enough). Duplicating the geometry-existence check would blur this boundary. The function still validates camera name existence because that's a spatial concern — the camera registry is OBJ-041's domain.

### D4: Oversizing uses conservative worst-case computation

**Decision:** The oversizing check computes required plane sizes using the camera's worst-case parameters: closest approach distance (minimum camera-to-plane distance across the path) and maximum FOV. This is deliberately conservative — most frames will have smaller visible areas.

**Rationale:** Edge reveals are catastrophic visual failures. A single frame showing a plane edge breaks immersion. Conservative sizing means planes may be 10-20% larger than strictly necessary, but this costs nothing (textures are already loaded; slightly larger planes don't impact render performance). The alternative — sampling multiple points along the path — is more precise but risks missing edge cases between sample points.

### D5: Rotated plane projection in oversizing checks

**Decision:** For planes that are rotated (floors, ceilings, walls), the oversizing check projects the camera's displacement onto the plane's surface coordinate system. A floor plane (rotated -π/2 on X) needs coverage in its local Y dimension that corresponds to the camera's Z displacement in world space, not the camera's Y displacement.

**Rationale:** This is the non-obvious part of the oversizing algorithm. A camera pushing forward on Z doesn't increase the required width of a floor plane — it increases the required depth (the floor's local Y, which maps to world Z due to rotation). Without this projection, the check would either produce false positives (requiring enormous planes for axes that don't matter) or false negatives (missing the axis that actually causes edge reveals).

**Formula sketch (not implementation, but specifying the math the implementer must follow):**

For a plane with rotation `[rx, ry, rz]`:
- The plane's local axes in world space are determined by the rotation.
- Camera displacement `[dx, dy, dz]` in world space must be projected onto the plane's local U and V axes.
- Required size = visible area at closest distance + projected displacement

For the common cases:
- `FACING_CAMERA` (rotation [0,0,0]): local U = world X, local V = world Y. Camera X displacement → width, Camera Y displacement → height.
- `FLOOR` (rotation [-π/2,0,0]): local U = world X, local V = world Z. Camera X displacement → width, Camera Z displacement → height.
- `CEILING` (rotation [π/2,0,0]): same as floor.
- `LEFT_WALL` (rotation [0,π/2,0]): local U = world Z, local V = world Y. Camera Z displacement → width, Camera Y displacement → height.
- `RIGHT_WALL` (rotation [0,-π/2,0]): same as left wall.

### D6: Coverage analysis is a development tool, not a runtime gate

**Decision:** `analyzeCoverage` and `formatCoverageMatrix` are development/documentation utilities. They are NOT invoked during manifest validation or rendering. They produce reports for TC-08 evaluation and SKILL.md generation.

**Rationale:** TC-08 asks "do 8 geometries cover the design space?" This is a qualitative question answered during development by examining the compatibility matrix and manually checking topic coverage. The tooling produces the data; the human makes the judgment.

### D7: SpatialValidationError includes suggestion field

**Decision:** Every error includes a `suggestion` string with an actionable fix instruction.

**Rationale:** Seed constraint C-06 (blind-authorable) and C-10 (actionable error messages). The LLM author needs to know not just what's wrong but how to fix it. The suggestion should name valid alternatives: "Use one of: static, slow_push_forward, gentle_float" rather than just "incompatible camera."

### D8: Registries passed as parameters, not imported as singletons

**Decision:** All functions accept both registries as parameters.

**Rationale:** Consistent with OBJ-006's D7 (registry as parameter for testability). Unit tests can pass mock registries. Avoids import-order coupling.

### D9: Oversizing check operates on PlaneSlot sizes, not texture sizes

**Decision:** The oversizing check uses the geometry's `PlaneSlot.size` (world-unit dimensions from the geometry definition), not the actual loaded texture dimensions.

**Rationale:** OBJ-041 is a pre-render validation step. Textures haven't been loaded yet. The geometry's slot sizes are the contract — if the geometry defines a floor as `[8, 40]` world units, that's what the oversizing check validates against. OBJ-040 (plane sizing / auto-sizing from textures) handles the runtime reconciliation between texture aspect ratios and slot sizes. OBJ-041 validates that the geometry's defined sizes are sufficient for the camera's motion.

### D10: Speed > 1.0 may cause oversizing failures — warning, not blocking

**Decision:** When `speed > 1.0`, the oversizing check uses the effective displacement (`maxDisplacement * speed`). If this exceeds the plane sizes, the check reports errors. However, `validateSceneSpatialCompatibility` reports these as `'oversizing'` category errors, distinguishable from `'compatibility'` errors. The manifest validator (OBJ-017) can choose to treat oversizing errors as warnings rather than hard failures.

**Rationale:** Speed > 1.0 is a legitimate authoring choice that may work fine with specific geometry configurations even if the conservative check flags it. Hard-blocking would prevent experimentation. The separate category lets OBJ-017 apply different severity levels.

## Acceptance Criteria

### Compatibility Validation

- [ ] **AC-01:** `validateSceneSpatialCompatibility` returns an error when the camera name does not exist in the camera registry. Error message includes the invalid camera name and lists all available camera presets.
- [ ] **AC-02:** `validateSceneSpatialCompatibility` returns an error when the camera name is not in the geometry's `compatible_cameras` list. Error message names the geometry, the camera, and lists the geometry's compatible cameras.
- [ ] **AC-03:** `validateSceneSpatialCompatibility` returns an error when the geometry name is not in the camera preset's `compatibleGeometries` list. Error message names the camera, the geometry, and lists the camera's compatible geometries.
- [ ] **AC-04:** `validateSceneSpatialCompatibility` returns an empty array when geometry and camera are mutually compatible, the camera exists, and no oversizing issues are present.
- [ ] **AC-05:** `validateSceneSpatialCompatibility` returns no errors (skips all checks) when the geometry name does not exist in the geometry registry (structural validation is OBJ-017's responsibility).

### Registry Consistency

- [ ] **AC-06:** `validateRegistryConsistency` detects a geometry that lists a camera name not present in the camera registry. Error message includes the geometry name and the missing camera name.
- [ ] **AC-07:** `validateRegistryConsistency` detects a camera preset that lists a geometry name not present in the geometry registry. Error message includes the camera name and the missing geometry name.
- [ ] **AC-08:** `validateRegistryConsistency` detects a one-directional mismatch: geometry G lists camera C, but camera C does not list geometry G. Error message names both and identifies which side is missing the declaration.
- [ ] **AC-09:** `validateRegistryConsistency` detects the reverse mismatch: camera C lists geometry G, but geometry G does not list camera C.
- [ ] **AC-10:** `validateRegistryConsistency` returns an empty array when both registries are fully bidirectionally consistent.
- [ ] **AC-11:** All `SpatialValidationError` objects from `validateRegistryConsistency` have `sceneId: null`.

### Oversizing Sufficiency

- [ ] **AC-12:** `checkOversizingSufficiency` returns one `OversizingCheckResult` per slot in the geometry.
- [ ] **AC-13:** For a static camera (zero displacement, constant FOV) and a plane sized to exactly fill the visible area, `sufficient` is `true` and `effectiveOversizeFactor` is approximately 1.0.
- [ ] **AC-14:** For a forward-pushing camera (Z displacement > 0) and a backdrop plane (`rotation=[0,0,0]`) that is not oversized, `sufficient` is `false`.
- [ ] **AC-15:** For a forward-pushing camera and a floor plane (`rotation=[-π/2,0,0]`), the required height of the floor plane reflects the camera's Z displacement (world Z maps to the floor's local Y), not the camera's Y displacement.
- [ ] **AC-16:** `speed` scales effective displacement: `checkOversizingSufficiency` with `speed=2.0` requires larger planes than `speed=1.0` for non-static cameras.
- [ ] **AC-17:** `offset` increases required size: a non-zero offset in any axis increases the required plane dimensions in the corresponding projected axis.
- [ ] **AC-18:** `validateOversizing` returns `SpatialValidationError` entries only for slots where `sufficient === false`. The error message names the slot and states the required vs actual sizes.

### Coverage Analysis

- [ ] **AC-19:** `analyzeCoverage` returns correct `totalGeometries` and `totalCameraPresets` counts.
- [ ] **AC-20:** `analyzeCoverage` correctly identifies bidirectionally compatible pairs.
- [ ] **AC-21:** `analyzeCoverage` correctly identifies orphaned geometries (no compatible cameras in the registry) and orphaned cameras.
- [ ] **AC-22:** `formatCoverageMatrix` produces valid Markdown with geometry rows, camera columns, and ✓/blank cells.

### Error Quality

- [ ] **AC-23:** Every `SpatialValidationError` has a non-empty `suggestion` field containing actionable instructions.
- [ ] **AC-24:** Error messages use seed vocabulary (geometry, camera path, plane slot) consistently.

### Module Constraints

- [ ] **AC-25:** The module imports only from `src/scenes/geometries/` (OBJ-005), `src/camera/` (OBJ-006), and `src/spatial/` (OBJ-003). No Three.js, Puppeteer, or Node.js-specific APIs.
- [ ] **AC-26:** All functions are deterministic: same inputs produce same outputs.

## Edge Cases and Error Handling

### Compatibility Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Camera name is empty string | Error: camera not found in registry. Lists available cameras. |
| Geometry exists but has empty `compatible_cameras` | Cannot happen — `validateGeometryDefinition` (OBJ-005 AC-06) rejects this. If somehow encountered, any camera is incompatible. |
| Camera default_camera not compatible with its own geometry | Caught by OBJ-005 validation. If encountered here, reported as bidirectional mismatch. |
| Same camera listed twice in geometry's `compatible_cameras` | Not an error for OBJ-041. OBJ-005's geometry validation may or may not catch duplicates. OBJ-041 treats it as one entry. |
| Geometry name in manifest is valid but camera name is `undefined`/omitted | The manifest schema (OBJ-004) resolves this to the geometry's `default_camera` before OBJ-041 is invoked. OBJ-041 always receives a resolved camera name. |

### Registry Consistency Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty geometry registry, non-empty camera registry | Every camera's `compatibleGeometries` entries are flagged as non-existent. No orphaned geometries (none exist). |
| Both registries empty | Returns empty array (vacuously consistent). |
| Geometry lists camera "static"; camera "static" lists geometry — fully consistent | No errors for this pair. |
| Geometry "tunnel" lists camera "crane_up"; camera "crane_up" does NOT list "tunnel" | Error: "Camera 'crane_up' is listed as compatible by geometry 'tunnel', but 'crane_up' does not list 'tunnel' in its compatibleGeometries. Add 'tunnel' to crane_up's compatibleGeometries, or remove 'crane_up' from tunnel's compatible_cameras." |

### Oversizing Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `speed = 0` | Invalid — `resolveCameraParams` (OBJ-006) throws before OBJ-041 is called. If somehow received, treat as speed=1.0 (defensive). |
| `speed = 0.001` (very small) | Near-static camera. All planes should pass sufficiency. |
| `offset = [0, 0, 0]` | No additional displacement. Check uses only camera preset's displacements. |
| Plane at Z=0 (same as camera start) | Distance approaches 0 → visible area approaches infinity. This is a degenerate configuration. The check should report `sufficient: false` with a message indicating the plane is too close to the camera path. |
| Plane behind the camera (Z > camera Z) | Plane is not visible (behind the camera). Oversizing check should skip it or report `sufficient: true` (it can't have edge reveals if it's not rendered). |
| FOV animation (fovRange[0] ≠ fovRange[1]) | Uses `fovRange[1]` (maximum FOV) for worst-case visible area calculation. |
| `aspectRatio` is very wide (e.g., 32:9 ultrawide) | Width requirement is much larger. Check correctly uses aspect ratio in visible_w calculation. |
| Optional slot not provided in manifest | OBJ-041 still checks the slot's defined size for sufficiency. Whether the slot is actually used is a manifest concern (OBJ-017). The geometry's spatial structure should be valid regardless. |

### Coverage Analysis Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Geometry with many compatible cameras (>10) | All listed in `geometryCoverage`. No special handling. |
| Camera compatible with all geometries | Listed in all geometries' coverage. `compatibleGeometryCount` = total geometries. |
| One-directional compatibility (geometry lists camera but not vice versa) | Shown in matrix with `geometryOnly: true`. NOT counted in `totalCompatiblePairs`. |

## Test Strategy

### Unit Tests

**Compatibility validation tests:**
1. Build mock geometry registry with 2 geometries ("stage" with cameras ["static", "slow_push_forward"], "tunnel" with cameras ["tunnel_push_forward", "static"]).
2. Build mock camera registry with 3 presets ("static" with geometries ["stage", "tunnel"], "slow_push_forward" with geometries ["stage"], "tunnel_push_forward" with geometries ["tunnel"]).
3. `validateSceneSpatialCompatibility("s1", "stage", "static", ...)` → empty array.
4. `validateSceneSpatialCompatibility("s1", "stage", "tunnel_push_forward", ...)` → error (camera not in geometry's list). Suggestion lists compatible cameras.
5. `validateSceneSpatialCompatibility("s1", "stage", "nonexistent", ...)` → error (camera not in registry). Message lists available cameras.
6. `validateSceneSpatialCompatibility("s1", "nonexistent_geo", "static", ...)` → empty array (geometry doesn't exist; skip spatial checks).
7. Test with geometry listing camera but camera not listing geometry → error with message identifying the mismatch direction.

**Registry consistency tests:**
1. Fully consistent registries → empty array.
2. Geometry lists non-existent camera → error.
3. Camera lists non-existent geometry → error.
4. Geometry lists camera C, camera C doesn't list geometry → mismatch error with clear message.
5. Camera lists geometry G, geometry G doesn't list camera → mismatch error.
6. Both registries empty → empty array.
7. Multiple mismatches → all reported (not just the first).

**Oversizing sufficiency tests:**
1. Static camera (zero displacement), plane sized exactly to visible area → `sufficient: true`, factor ≈ 1.0.
2. Static camera, plane smaller than visible area → `sufficient: false`.
3. Forward push camera, facing-camera plane at Z=-30: required width increases by camera X displacement → verify formula.
4. Forward push camera, floor plane (rotated -π/2 on X): required height reflects Z displacement → verify projection.
5. Left wall (rotated π/2 on Y): required width reflects Z displacement, required height reflects Y displacement → verify.
6. Speed=2.0 doubles effective displacement → larger required sizes.
7. Offset [1, 0, 0] increases required width for facing-camera planes.
8. Plane at same Z as camera → degenerate, `sufficient: false`.
9. FOV range with max > min → uses max for calculation.

**Coverage analysis tests:**
1. 2 geometries, 3 cameras, known compatibility → verify all counts and matrix entries.
2. Orphaned geometry (no cameras list it) → appears in `orphanedGeometries`.
3. `formatCoverageMatrix` produces parseable Markdown with correct ✓ markers.

### Relevant Testable Claims

- **TC-07** (partial): Spatial compatibility validation catches camera-geometry mismatches before rendering. OBJ-041 provides the spatial rules; OBJ-017 integrates them into the manifest validation pipeline.
- **TC-08** (direct): `analyzeCoverage` provides the data to evaluate whether 8 geometries cover the design space. The implementer should include a test that exercises `analyzeCoverage` with all 8 proposed geometries and all 11 proposed cameras.
- **TC-04** (partial): Spatial compatibility validation ensures that valid camera-geometry combinations produce correct spatial relationships.

### Integration Tests

Once concrete geometries (OBJ-018+) and camera presets (OBJ-026+) are implemented:
1. Run `validateRegistryConsistency` against the real registries. Must return empty array.
2. Run `analyzeCoverage` and verify every geometry has ≥1 compatible camera.
3. Run `checkOversizingSufficiency` for every bidirectionally-compatible geometry+camera pair at speed=1.0, offset=[0,0,0], aspect=16/9. All slots must be sufficient.

## Integration Points

### Depends on

| Dependency | What OBJ-041 imports |
|---|---|
| **OBJ-005** (Scene Geometry Type Contract) | `SceneGeometry`, `PlaneSlot`, `GeometryRegistry` types. `isCameraCompatible()` for checking geometry's compatible_cameras list. |
| **OBJ-006** (Camera Path Type Contract) | `CameraPathPreset`, `CameraPathRegistry`, `OversizeRequirements`, `CameraParams` types. `isCameraPathName()`, `getCameraPath()`, `getCameraPathsForGeometry()` for registry lookups. |
| **OBJ-003** (Spatial Math) | `Vec3` type for offset parameters. Potentially frustum/visible-area math utilities if OBJ-003 provides them, otherwise computed inline. |

### Consumed by

| Downstream | How it uses OBJ-041 |
|---|---|
| **OBJ-017** (Manifest structural validation) | Calls `validateSceneSpatialCompatibility` for each scene in the manifest, additively on top of structural validation. |
| **OBJ-069** (Edge reveal systematic validation) | Uses `checkOversizingSufficiency` and `validateRegistryConsistency` as part of its comprehensive edge-reveal testing across all geometry+camera combinations. |
| **OBJ-071** (SKILL.md) | Uses `analyzeCoverage` / `formatCoverageMatrix` to generate the geometry-camera compatibility reference table in SKILL.md. |
| **Development/CI** | `validateRegistryConsistency` runs as a CI check to catch bidirectional mismatches when new geometries or cameras are added. |

### File Placement

```
depthkit/
  src/
    validation/
      spatial-compatibility.ts   # validateSceneSpatialCompatibility,
                                 # validateRegistryConsistency,
                                 # checkOversizingSufficiency,
                                 # validateOversizing,
                                 # SpatialValidationError,
                                 # OversizingCheckResult types
      coverage-analysis.ts       # analyzeCoverage, formatCoverageMatrix,
                                 # CompatibilityMatrixEntry, CoverageAnalysis types
      index.ts                   # Barrel export
```

Note: OBJ-017 may already have a `src/manifest/` validation directory. OBJ-041's spatial validation is placed under `src/validation/` rather than `src/manifest/` because: (a) registry consistency validation is not manifest-specific, (b) oversizing checks are consumed by OBJ-069 (tuning) outside the manifest validation context, and (c) it avoids coupling to OBJ-017's file structure. If an integrator prefers `src/manifest/spatial-validation.ts`, the contracts are unaffected.

## Open Questions

### OQ-1: Should oversizing check support sampling-based validation as an alternative to conservative bounds?

The conservative approach (worst-case camera position + max FOV) may be overly pessimistic for complex paths like `gentle_float` where the camera oscillates and the worst case in X and worst case in Z never occur simultaneously. A sampling-based approach (evaluate the path at N points, compute visible area at each, take the maximum per-plane) would be more precise but risks missing edge cases between samples.

**Recommendation:** Start with conservative bounds. Add sampling-based validation as an optional `mode` parameter in a future iteration if conservative checks produce too many false positives. The conservative check is simpler, faster, and has no false negatives.

### OQ-2: Should `validateSceneSpatialCompatibility` invoke oversizing checks by default?

Oversizing checks require `aspectRatio`, which is a composition-level parameter not available per-scene without passing it through. Should the function always run oversizing checks, or only when explicitly requested?

**Recommendation:** Always run when `cameraParams` are provided (since speed/offset affect oversizing). The caller (OBJ-017) has access to `composition.width/height` and passes `aspectRatio`. When `cameraParams` is undefined (all defaults), oversizing is checked with speed=1.0 and offset=[0,0,0] — these are the conditions under which the geometry's plane sizes should already be validated by the geometry author.

### OQ-3: Should the coverage analysis include a "topic coverage" scoring system for TC-08?

TC-08 asks whether 8 geometries cover the design space. The programmatic analysis shows compatibility counts, but the actual evaluation — "can these 8 geometries accommodate 20/25 random topics?" — is a qualitative human judgment. Should OBJ-041 provide any structure for this (e.g., a topic-to-geometry mapping template)?

**Recommendation:** No. OBJ-041 provides the quantitative tooling (compatibility matrix, coverage counts). The qualitative TC-08 evaluation is done by the human during the tuning phase. Adding topic-mapping templates would overcomplicate this module's scope.

---

I believe this spec covers the full scope of OBJ-041 as described in the metadata: compatibility validation, oversizing checks, registry consistency, and TC-08 coverage analysis. I'd like the Challenger to verify:

1. Whether the three-tier validation split is appropriate
2. Whether the oversizing algorithm specification (especially the rotated-plane projection in D5) is sufficiently precise for an implementer
3. Whether the boundary with OBJ-017 and OBJ-040 is clear
4. Whether the coverage analysis tooling is the right scope for TC-08

Please review and challenge.

---

## Round 2 — spec_challenger

I've read the proposal carefully. The three-tier structure (compatibility, registry consistency, oversizing) is well-reasoned, and the coverage analysis utility is appropriate scope for TC-08. The boundary with OBJ-017 (structural) vs OBJ-041 (spatial) is clearly articulated through D3 and the metadata boundary note. The bidirectional enforcement (D2) is a smart catch for the deliberate redundancy between OBJ-005's `compatible_cameras` and OBJ-006's `compatibleGeometries`.

Here are my challenges:

---

### Issue 1 (Critical): `validateSceneSpatialCompatibility` is missing `aspectRatio` parameter

The function signature:
```typescript
export function validateSceneSpatialCompatibility(
  sceneId: string,
  geometryName: string,
  cameraName: string,
  cameraParams: CameraParams | undefined,
  geometryRegistry: ...,
  cameraRegistry: ...
): SpatialValidationError[];
```

The spec says this function runs oversizing checks (checks #4 in the doc, and OQ-2's recommendation says "Always run when cameraParams are provided"). But `checkOversizingSufficiency` requires `aspectRatio`. The function signature has no `aspectRatio` parameter. OQ-2 identifies this gap but the recommendation doesn't fix it — it says "The caller passes aspectRatio" but the signature has nowhere to receive it.

**Fix:** Add `aspectRatio: number` as a required parameter to `validateSceneSpatialCompatibility`. Update AC-04 and AC-05 to include the parameter. Or, if you want to keep oversizing checks optional at this layer, add an options object: `options?: { aspectRatio?: number }` where oversizing checks are skipped when `aspectRatio` is not provided.

---

### Issue 2 (Major): Oversizing closest-approach algorithm is underspecified

D5 and `checkOversizingSufficiency` say to compute "the plane's distance from the camera's closest approach." But the algorithm to determine the camera's position range is not defined.

`OversizeRequirements` from OBJ-006 provides `maxDisplacementX/Y/Z` as unsigned magnitudes. These don't tell the implementer:
1. **Direction of displacement** — a forward push (z=5 → z=-20) has maxDisplacementZ=25, but the camera only moves in one direction. `gentle_float` might oscillate symmetrically.
2. **How to compute the camera's position envelope** — Is it `[startPos - displacement, startPos + displacement]` (symmetric)? Or `[startPos, startPos - displacement]` (one-directional)?

The preset provides `defaultStartState.position` and `defaultEndState.position`, which could be used. But the spec doesn't say to use these. And for oscillating paths, the extremes might not be at t=0 or t=1.

**Fix:** Specify the algorithm explicitly. I suggest:

> The camera's worst-case position envelope for oversizing purposes is computed as:
> - `minZ = defaultStartState.position[2] - maxDisplacementZ`
> - `maxZ = defaultStartState.position[2] + maxDisplacementZ`
> - (analogously for X and Y)
>
> For each plane, the closest approach distance is: `min(abs(planeZ - camZ))` for all `camZ` in `[minZ, maxZ]`. This is equivalent to:
> ```
> closestDistance = max(0, abs(planeZ - startZ) - maxDisplacementZ)
> ```
> When `closestDistance ≤ 0` (camera range overlaps the plane's Z), report the plane as degenerate (too close to camera path).

This is conservative (treats displacement as symmetric) which aligns with D4's stated intent. The implementer shouldn't have to figure this out.

---

### Issue 3 (Major): Overlapping oversizing math with OBJ-040

OBJ-040's metadata says: "camera-motion-dependent oversizing factors to prevent edge reveals during camera movement, edge-reveal prevention math." OBJ-041's `checkOversizingSufficiency` implements visible-area calculation and oversizing factor computation — the same domain.

D9 tries to distinguish them: "OBJ-041 validates geometry definition sizes; OBJ-040 handles runtime texture-to-plane reconciliation." But the underlying math (visible area from FOV + distance, projection onto rotated planes) is identical. Two independent implementations of the same math will either diverge (disagreeing on whether a plane is sufficient) or be duplicated code.

**Fix:** One of:

**(a)** State explicitly that OBJ-041 and OBJ-040 share a common visible-area utility that should be defined in OBJ-003 (or a shared math module), and add a design decision specifying this. Both objectives import the shared math.

**(b)** State explicitly that OBJ-041 implements a *simplified conservative* version of the oversizing check (using only `OversizeRequirements` metadata, not sampling `evaluate()`), while OBJ-040 implements the *precise* version (potentially sampling the actual trajectory). Document that OBJ-041's check is a necessary-but-not-sufficient gate — passing OBJ-041 means the geometry's authored sizes are plausible, but OBJ-040 provides the final runtime validation.

I recommend (b) because it maintains the DAG as-is (OBJ-041 doesn't depend on OBJ-040) and gives OBJ-041 a clearly scoped, simpler algorithm.

---

### Issue 4 (Major): Rotated-plane projection formula in D5 is incomplete

D5 says "For a plane with rotation [rx, ry, rz]: the plane's local axes in world space are determined by the rotation." Then it lists the common cases. But:

1. It only covers axis-aligned rotations. What about a plane with arbitrary rotation (e.g., a `midground` plane tilted at 30°)? The spec should either (a) state that only axis-aligned rotations are supported for oversizing checks, or (b) provide the general rotation matrix projection.

2. For the floor case (rotation [-π/2, 0, 0]): "Camera Z displacement → height" — but what "height" means here is ambiguous. The floor plane's `PlaneSlot.size` is `[width, height]` in local coordinates. When rotated to become a floor, the plane's local Y axis maps to world Z. So the required `size[1]` (local height) must accommodate the camera's Z displacement. This should be stated explicitly with reference to `PlaneSlot.size[0]` and `PlaneSlot.size[1]`.

**Fix:** For each common case, map explicitly to `size[0]` and `size[1]`:

| Rotation | `requiredSize[0]` needs to cover | `requiredSize[1]` needs to cover |
|---|---|---|
| FACING_CAMERA [0,0,0] | visibleWidth + camDisplacementX | visibleHeight + camDisplacementY |
| FLOOR [-π/2,0,0] | visibleWidth + camDisplacementX | visibleDepth + camDisplacementZ |
| LEFT_WALL [0,π/2,0] | visibleDepth + camDisplacementZ | visibleHeight + camDisplacementY |

And state: "Planes with non-axis-aligned rotations are not validated by the oversizing check. The implementer should log a warning and skip the check for such planes, or treat them as FACING_CAMERA."

---

### Issue 5 (Minor): `effectiveOversizeFactor` definition is confusing

The doc says: "Values > actualSize/requiredSize indicate the plane is too small." This is backwards. The factor should be `actualSize / requiredSize`. When this is < 1.0, the plane is too small. When ≥ 1.0, it's sufficient. The current description reads as if values *greater than* the ratio indicate undersizing.

**Fix:** Define explicitly:
> `effectiveOversizeFactor = min(actualSize[0] / requiredSize[0], actualSize[1] / requiredSize[1])`. Values < 1.0 indicate the plane is undersized. Values ≥ 1.0 indicate sufficiency.

And add an AC: "AC-XX: `effectiveOversizeFactor` < 1.0 if and only if `sufficient === false`."

---

### Issue 6 (Minor): No AC for the relationship between `checkOversizingSufficiency` and `validateOversizing`

`validateOversizing` is described as a "convenience wrapper" that converts `OversizingCheckResult` entries into `SpatialValidationError` entries. But there's no AC that verifies they agree — i.e., that `validateOversizing` returns errors for exactly the slots where `checkOversizingSufficiency` returns `sufficient: false`.

**Fix:** Add AC: "AC-XX: `validateOversizing` returns one `SpatialValidationError` per slot where `checkOversizingSufficiency` returned `sufficient: false`, and no errors for sufficient slots."

---

### Issue 7 (Minor): Edge case — camera at plane Z or beyond

The edge case table says: "Plane behind the camera (Z > camera Z) — Plane is not visible. Oversizing check should skip it or report sufficient: true."

But a camera pushing forward might start with a plane in front and end with the plane behind. The plane is visible for part of the path. The spec doesn't specify how to handle this partial-visibility case.

**Fix:** Add: "If the camera's position range includes the plane's Z coordinate (the camera passes through or past the plane), report `sufficient: false` with message: 'Plane {slotName} at Z={z} is within the camera's movement range [minZ, maxZ]. The camera would pass through this plane, causing visual artifacts.'"

This is actually a compatibility issue, not just an oversizing issue.

---

### Summary of challenges:

| # | Severity | Issue |
|---|---|---|
| 1 | **Critical** | Missing `aspectRatio` parameter on `validateSceneSpatialCompatibility` |
| 2 | **Major** | Closest-approach algorithm underspecified (direction/envelope) |
| 3 | **Major** | Overlapping oversizing math with OBJ-040 needs explicit boundary |
| 4 | **Major** | Rotated-plane projection formula incomplete (size[0]/size[1] mapping, non-axis-aligned) |
| 5 | Minor | `effectiveOversizeFactor` definition confusing/backwards |
| 6 | Minor | Missing AC linking `checkOversizingSufficiency` to `validateOversizing` |
| 7 | Minor | Partial-visibility edge case (camera passes through plane) unhandled |

I will not converge until Issues 1-4 are addressed in the revised spec. Please revise.

---

## Round 3 — spec_author

Thank you for the thorough review. All seven issues are valid. Here's my revised specification addressing each one.

---

# Specification: OBJ-041 — Geometry-Camera Spatial Compatibility Validation

## Summary

OBJ-041 defines the spatial compatibility validation layer for depthkit manifests. It cross-references the geometry registry (OBJ-005) and camera path registry (OBJ-006) to enforce three categories of spatial correctness: (1) **compatibility validation** — a manifest's chosen camera path must be mutually declared compatible with the geometry, (2) **registry consistency validation** — all cross-references between geometry and camera registries must resolve and agree bidirectionally, and (3) **oversizing sufficiency checks** — given a camera path's `OversizeRequirements` and a geometry's `PlaneSlot` sizes, planes must be large enough to prevent edge reveals. It also provides a **coverage analysis utility** for TC-08 (do 8 geometries cover the design space). This module sits between the type contracts (OBJ-005, OBJ-006) and manifest validation (OBJ-017), producing spatial validation rules that OBJ-017 invokes additively on top of structural validation.

## Interface Contract

### Core Validation Types

```typescript
// src/validation/spatial-compatibility.ts

import type { SceneGeometry, GeometryRegistry } from '../scenes/geometries';
import type { CameraPathPreset, CameraPathRegistry, OversizeRequirements, CameraParams } from '../camera';
import type { Vec3 } from '../spatial/types';

/**
 * A single spatial validation error. Structured for programmatic
 * error handling and actionable LLM feedback (seed C-06, C-10).
 */
export interface SpatialValidationError {
  /** Error category for filtering/grouping */
  category: 'compatibility' | 'registry_consistency' | 'oversizing';

  /** Identifier of the scene in the manifest (e.g., 'scene_001'), or null for registry-level errors */
  sceneId: string | null;

  /** Human-readable error message, actionable for an LLM author */
  message: string;

  /**
   * Suggested fix, phrased as an instruction the LLM can act on.
   * E.g., "Use one of: static, slow_push_forward, gentle_float"
   */
  suggestion: string;
}
```

### Scene-Level Compatibility Validation

```typescript
/**
 * Validates that a single manifest scene's camera path is spatially
 * compatible with its chosen geometry. This is the per-scene check
 * that OBJ-017 invokes for each scene in the manifest.
 *
 * Checks performed:
 * 1. The camera path name exists in the camera registry.
 * 2. The camera path name is in the geometry's compatible_cameras list.
 * 3. The geometry name is in the camera preset's compatibleGeometries list.
 * 4. Oversizing sufficiency: planes are large enough for the camera's
 *    motion envelope at the given speed, offset, and aspect ratio.
 *
 * This function does NOT validate geometry name existence or plane slot
 * keys — those are OBJ-017's structural validation responsibility.
 * If the geometry name is not found in the geometry registry, this
 * function returns an empty array (skip all spatial checks).
 *
 * @param sceneId - The manifest scene's id (for error reporting).
 * @param geometryName - The geometry name from the manifest scene.
 * @param cameraName - The camera path name from the manifest scene.
 * @param cameraParams - Optional camera params from the manifest scene.
 * @param aspectRatio - Composition aspect ratio (width / height, e.g., 16/9).
 * @param geometryRegistry - The geometry registry.
 * @param cameraRegistry - The camera path registry.
 * @returns Array of SpatialValidationError. Empty = valid.
 */
export function validateSceneSpatialCompatibility(
  sceneId: string,
  geometryName: string,
  cameraName: string,
  cameraParams: CameraParams | undefined,
  aspectRatio: number,
  geometryRegistry: Readonly<GeometryRegistry>,
  cameraRegistry: Readonly<CameraPathRegistry>
): SpatialValidationError[];
```

### Registry-Level Consistency Validation

```typescript
/**
 * Validates bidirectional consistency between the geometry and camera
 * registries. This is a boot-time / development-time / CI check, not a
 * per-manifest check. It ensures that the preset libraries are
 * internally consistent.
 *
 * Checks performed:
 * 1. For every geometry, every entry in compatible_cameras exists
 *    as a key in the camera registry.
 * 2. For every camera preset, every entry in compatibleGeometries
 *    exists as a key in the geometry registry.
 * 3. Bidirectional agreement: if geometry G lists camera C in
 *    compatible_cameras, then camera C must list geometry G in
 *    compatibleGeometries (and vice versa). Mismatches are errors.
 * 4. Every geometry has at least one compatible camera that exists
 *    in the camera registry (non-empty intersection).
 *
 * @param geometryRegistry - The full geometry registry.
 * @param cameraRegistry - The full camera path registry.
 * @returns Array of SpatialValidationError with sceneId = null.
 *   Empty = fully consistent.
 */
export function validateRegistryConsistency(
  geometryRegistry: Readonly<GeometryRegistry>,
  cameraRegistry: Readonly<CameraPathRegistry>
): SpatialValidationError[];
```

### Oversizing Sufficiency Validation

```typescript
/**
 * Result of an oversizing check for a single plane slot.
 */
export interface OversizingCheckResult {
  /** Slot name (e.g., 'floor', 'left_wall') */
  slotName: string;

  /** Whether the plane is large enough to prevent edge reveals */
  sufficient: boolean;

  /**
   * Required plane size [width, height] in the plane's local coordinate
   * system (matching PlaneSlot.size semantics) to prevent edge reveals,
   * given the camera path's motion envelope.
   *
   * For a FACING_CAMERA plane: [0] = world X coverage, [1] = world Y coverage.
   * For a FLOOR plane: [0] = world X coverage, [1] = world Z coverage.
   * For a LEFT/RIGHT_WALL: [0] = world Z coverage, [1] = world Y coverage.
   */
  requiredSize: readonly [number, number];

  /** Actual plane size from the geometry definition (PlaneSlot.size) */
  actualSize: readonly [number, number];

  /**
   * Effective oversize factor: min(actualSize[0]/requiredSize[0],
   * actualSize[1]/requiredSize[1]).
   *
   * Values >= 1.0 indicate the plane is sufficiently sized.
   * Values < 1.0 indicate the plane is undersized.
   * Invariant: effectiveOversizeFactor < 1.0 iff sufficient === false.
   */
  effectiveOversizeFactor: number;

  /**
   * If the camera's movement range includes the plane's Z coordinate
   * (the camera would pass through or beyond the plane), this is true.
   * When true, sufficient is always false — this is a spatial structure
   * error, not just a sizing issue.
   */
  cameraPassesThrough: boolean;

  /**
   * Set to true when the plane has a non-axis-aligned rotation that
   * the oversizing check cannot validate. The check skips projection
   * for such planes and reports them as unchecked rather than
   * sufficient or insufficient. sufficient is set to true (benefit
   * of the doubt) but this flag signals that manual review is needed.
   */
  skippedNonAxisAligned: boolean;
}

/**
 * Checks whether all planes in a geometry are large enough to prevent
 * edge reveals for a given camera path preset at a given speed and offset.
 *
 * This is a SIMPLIFIED CONSERVATIVE check using only the camera preset's
 * OversizeRequirements metadata (maxDisplacementX/Y/Z, fovRange). It does
 * NOT sample the camera's evaluate() function. OBJ-040 provides precise
 * per-frame edge-reveal validation using trajectory sampling. OBJ-041's
 * check is a necessary-but-not-sufficient gate: passing it means the
 * geometry's authored sizes are plausible for the camera's declared
 * motion envelope. Failing it means the combination is definitely broken.
 *
 * ### Camera Position Envelope Algorithm
 *
 * The camera's worst-case position envelope is computed symmetrically
 * from the start position and max displacements:
 *
 *   camStartPos = cameraPreset.defaultStartState.position
 *   minCamX = camStartPos[0] - (maxDisplacementX * speed) - abs(offset[0])
 *   maxCamX = camStartPos[0] + (maxDisplacementX * speed) + abs(offset[0])
 *   (analogously for Y and Z)
 *
 * This is conservative: it assumes displacement could go in either
 * direction from the start, even if the actual path is one-directional.
 * This is intentional per D4 — no false negatives.
 *
 * ### Per-Plane Distance Calculation
 *
 * For each plane slot, the closest approach distance (used for worst-case
 * visible area) depends on the plane's orientation:
 *
 * **FACING_CAMERA planes** (rotation ≈ [0,0,0]):
 *   closestDistance = max(EPSILON, abs(planeZ - closestCamZ))
 *   where closestCamZ = clamp(planeZ, minCamZ, maxCamZ) if camera
 *   range doesn't contain planeZ, or EPSILON if it does (degenerate).
 *
 *   Actually simplified: since we want the minimum distance from
 *   camera range to the plane:
 *   - If minCamZ <= planeZ <= maxCamZ: camera passes through → degenerate
 *   - Otherwise: closestDistance = min(abs(planeZ - minCamZ), abs(planeZ - maxCamZ))
 *
 * **FLOOR/CEILING planes** (rotation ≈ [-π/2,0,0] or [π/2,0,0]):
 *   The "distance" for visible area is the camera's perpendicular
 *   distance to the plane surface, which is along the Y axis:
 *   closestDistance = max(EPSILON, min over camera Y range of abs(planeY - camY))
 *   Camera-passes-through check: does the camera Y range contain planeY?
 *
 * **LEFT/RIGHT WALL planes** (rotation ≈ [0,±π/2,0]):
 *   Distance is along the X axis:
 *   closestDistance = max(EPSILON, min over camera X range of abs(planeX - camX))
 *   Camera-passes-through check: does the camera X range contain planeX?
 *
 * ### Visible Area at Distance
 *
 *   visibleHeight = 2 * closestDistance * tan(maxFov / 2)
 *   visibleWidth = visibleHeight * aspectRatio
 *
 * (maxFov = oversizeRequirements.fovRange[1])
 *
 * ### Required Size Mapping (plane-local coordinates)
 *
 * The camera's world-space displacement must be projected onto each
 * plane's local coordinate axes. For axis-aligned planes, this is
 * a fixed mapping between world axes and PlaneSlot.size[0]/size[1]:
 *
 * | Rotation              | size[0] covers (world) | size[1] covers (world) |
 * |-----------------------|------------------------|------------------------|
 * | FACING_CAMERA [0,0,0] | visibleWidth + camRangeX | visibleHeight + camRangeY |
 * | FLOOR [-π/2,0,0]      | visibleWidth + camRangeX | visibleDepth + camRangeZ |
 * | CEILING [π/2,0,0]     | visibleWidth + camRangeX | visibleDepth + camRangeZ |
 * | LEFT_WALL [0,π/2,0]   | visibleDepth + camRangeZ | visibleHeight + camRangeY |
 * | RIGHT_WALL [0,-π/2,0] | visibleDepth + camRangeZ | visibleHeight + camRangeY |
 *
 * Where:
 *   camRangeX = (maxDisplacementX * speed + abs(offset[0])) * 2
 *   camRangeY = (maxDisplacementY * speed + abs(offset[1])) * 2
 *   camRangeZ = (maxDisplacementZ * speed + abs(offset[2])) * 2
 *
 *   visibleWidth and visibleHeight are computed at the closest approach
 *   distance using the maximum FOV.
 *
 *   visibleDepth = visibleHeight (the perpendicular visible extent at
 *   the closest distance, before aspect ratio scaling — used for the
 *   axis that maps to the camera's depth direction for wall/floor planes).
 *
 * Wait — let me be more precise. For a FLOOR plane, the camera looks
 * down at it from above. The floor extends in world X and world Z.
 * The camera's frustum intersects the floor plane as a trapezoid.
 * At the closest approach (camera directly above at min distance),
 * the visible footprint on the floor is approximately:
 *   footprintX = visibleWidth (at that perpendicular distance)
 *   footprintZ = visibleHeight (at that perpendicular distance)
 *
 * But when the camera is NOT directly above — when it's offset in Z —
 * the visible footprint extends further in Z. The conservative bound
 * adds the camera's Z displacement range. So:
 *   requiredSize[0] = footprintX + camRangeX
 *   requiredSize[1] = footprintZ + camRangeZ
 *
 * For FACING_CAMERA planes, the visible area depends on distance in Z:
 *   requiredSize[0] = visibleWidth + camRangeX
 *   requiredSize[1] = visibleHeight + camRangeY
 *
 * For LEFT_WALL planes, the visible area depends on distance in X:
 *   requiredSize[0] = footprintZ_at_X_distance + camRangeZ
 *   requiredSize[1] = footprintY_at_X_distance + camRangeY
 *
 * **Non-axis-aligned rotations:** Planes whose rotation does not match
 * any of the five axis-aligned cases (within a tolerance of 0.01 radians)
 * are skipped. The result entry has skippedNonAxisAligned = true and
 * sufficient = true (benefit of the doubt). A console warning is logged.
 *
 * @param geometry - The scene geometry definition.
 * @param cameraPreset - The camera path preset.
 * @param speed - The camera_params.speed value (default 1.0).
 * @param offset - The camera_params.offset value (default [0,0,0]).
 * @param aspectRatio - Composition aspect ratio (width/height).
 * @returns Array of OversizingCheckResult, one per slot in the geometry.
 */
export function checkOversizingSufficiency(
  geometry: SceneGeometry,
  cameraPreset: CameraPathPreset,
  speed: number,
  offset: Vec3,
  aspectRatio: number
): OversizingCheckResult[];

/**
 * Convenience wrapper that converts OversizingCheckResult entries into
 * SpatialValidationError entries for slots that fail.
 *
 * Returns one SpatialValidationError per slot where sufficient === false,
 * and zero errors for sufficient slots.
 *
 * For cameraPassesThrough slots, the error message says:
 * "Plane '{slotName}' at Z={z} is within the camera's movement range
 * [{minZ}, {maxZ}]. The camera would pass through this plane."
 * Suggestion: "Move the plane further from the camera path, or choose
 * a camera preset with less Z displacement."
 *
 * For undersized slots, the error message states required vs actual sizes.
 * Suggestion: "Increase the plane size in the geometry definition, reduce
 * camera speed, or choose a less aggressive camera preset."
 *
 * @param sceneId - For error reporting.
 * @param geometry - The scene geometry.
 * @param cameraPreset - The camera path preset.
 * @param speed - Camera params speed (default 1.0).
 * @param offset - Camera params offset (default [0,0,0]).
 * @param aspectRatio - Composition aspect ratio.
 * @returns Array of SpatialValidationError for insufficient slots only.
 */
export function validateOversizing(
  sceneId: string,
  geometry: SceneGeometry,
  cameraPreset: CameraPathPreset,
  speed: number,
  offset: Vec3,
  aspectRatio: number
): SpatialValidationError[];
```

### Coverage Analysis Utility

```typescript
// src/validation/coverage-analysis.ts

import type { GeometryRegistry } from '../scenes/geometries';
import type { CameraPathRegistry } from '../camera';

/**
 * A compatibility matrix entry showing which cameras work with
 * which geometries, for documentation and TC-08 analysis.
 */
export interface CompatibilityMatrixEntry {
  geometryName: string;
  cameraName: string;
  /** true if both sides declare compatibility */
  bidirectionallyCompatible: boolean;
  /** true if only the geometry lists the camera (but not vice versa) */
  geometryOnly: boolean;
  /** true if only the camera lists the geometry (but not vice versa) */
  cameraOnly: boolean;
}

/**
 * Coverage analysis summary for TC-08.
 */
export interface CoverageAnalysis {
  /** Total number of registered geometries */
  totalGeometries: number;

  /** Total number of registered camera presets */
  totalCameraPresets: number;

  /** Number of valid (bidirectionally compatible) geometry-camera pairs */
  totalCompatiblePairs: number;

  /** Geometries with no bidirectionally compatible cameras */
  orphanedGeometries: string[];

  /** Camera presets with no bidirectionally compatible geometries */
  orphanedCameras: string[];

  /**
   * The full compatibility matrix.
   * Only includes entries where at least one side declares compatibility.
   */
  matrix: CompatibilityMatrixEntry[];

  /**
   * Per-geometry summary: how many cameras are bidirectionally compatible.
   */
  geometryCoverage: Record<string, {
    compatibleCameraCount: number;
    compatibleCameras: string[];
  }>;

  /**
   * Per-camera summary: how many geometries are bidirectionally compatible.
   */
  cameraCoverage: Record<string, {
    compatibleGeometryCount: number;
    compatibleGeometries: string[];
  }>;
}

/**
 * Produces a coverage analysis report from the two registries.
 * Used for TC-08 evaluation, SKILL.md generation, and
 * development-time auditing.
 *
 * @param geometryRegistry - The full geometry registry.
 * @param cameraRegistry - The full camera path registry.
 * @returns CoverageAnalysis summary.
 */
export function analyzeCoverage(
  geometryRegistry: Readonly<GeometryRegistry>,
  cameraRegistry: Readonly<CameraPathRegistry>
): CoverageAnalysis;

/**
 * Formats the coverage analysis as a human-readable Markdown table.
 * Rows = geometries, columns = cameras. Cells show ✓ for
 * bidirectional compatibility, G→ for geometry-only declaration,
 * →C for camera-only declaration, and blank for no compatibility.
 *
 * @param analysis - The coverage analysis to format.
 * @returns Markdown string.
 */
export function formatCoverageMatrix(analysis: CoverageAnalysis): string;
```

### Module Exports

```typescript
// src/validation/index.ts

export type {
  SpatialValidationError,
  OversizingCheckResult,
  CompatibilityMatrixEntry,
  CoverageAnalysis,
} from './spatial-compatibility';

export {
  validateSceneSpatialCompatibility,
  validateRegistryConsistency,
  checkOversizingSufficiency,
  validateOversizing,
} from './spatial-compatibility';

export {
  analyzeCoverage,
  formatCoverageMatrix,
} from './coverage-analysis';
```

## Design Decisions

### D1: Three-tier validation — scene-level, registry-level, oversizing

**Decision:** Spatial compatibility is split into three distinct validation tiers:
1. **Scene-level compatibility** (`validateSceneSpatialCompatibility`) — invoked per-scene during manifest validation, checks that the specific geometry+camera combination is valid and planes are large enough.
2. **Registry-level consistency** (`validateRegistryConsistency`) — invoked once at boot/build/CI time, checks bidirectional consistency between registries.
3. **Oversizing sufficiency** (`checkOversizingSufficiency`) — invoked per-scene, checks that planes are large enough for the camera's motion envelope.

**Rationale:** Different invocation timing and different consumers. Scene-level is called by OBJ-017 during manifest validation. Registry-level is a development/CI integrity check. Oversizing is the most computationally intensive and depends on runtime parameters (speed, offset, aspect ratio). Separating them lets consumers invoke only what they need.

### D2: Bidirectional compatibility enforcement

**Decision:** If geometry G lists camera C in `compatible_cameras`, then camera C MUST list geometry G in `compatibleGeometries`, and vice versa. Mismatches are errors.

**Rationale:** OBJ-005's `compatible_cameras` and OBJ-006's `compatibleGeometries` are deliberately redundant (OBJ-005 D7 explains why: avoiding circular dependencies). Since they're maintained separately, they can drift. Bidirectional enforcement catches drift. Treating one side as authoritative would make the other's list misleading.

**Consequence:** When a new geometry is added, both sides must be updated. `validateRegistryConsistency` catches omissions.

### D3: Scene-level validation assumes geometry exists

**Decision:** `validateSceneSpatialCompatibility` does NOT validate geometry name existence. If the geometry name is not found in the geometry registry, the function returns an empty array.

**Rationale:** The boundary between OBJ-017 and OBJ-041 is: OBJ-017 validates structure (geometry exists, plane keys match slots), OBJ-041 validates spatial compatibility (camera works with geometry, planes large enough). The camera name existence check IS in OBJ-041 because the camera registry is OBJ-041's domain.

### D4: Oversizing uses conservative worst-case computation with symmetric envelope

**Decision:** The oversizing check treats `maxDisplacementX/Y/Z` as symmetric ranges from the camera start position, even for one-directional paths. A `slow_push_forward` with `maxDisplacementZ=25` is treated as if the camera could be anywhere in `[startZ - 25, startZ + 25]`.

**Rationale:** Edge reveals are catastrophic visual failures. Conservative sizing means planes may be 10-20% larger than strictly necessary, but larger planes cost nothing. This approach uses only `OversizeRequirements` metadata (no `evaluate()` sampling), keeping the algorithm simple and fast. OBJ-040 provides the precise trajectory-sampling validation for cases where conservative bounds are too pessimistic.

### D5: Rotated-plane projection uses axis-aligned lookup, not general rotation matrices

**Decision:** The oversizing check recognizes five axis-aligned rotation cases (within 0.01 radian tolerance): `FACING_CAMERA`, `FLOOR`, `CEILING`, `LEFT_WALL`, `RIGHT_WALL`. For each, the mapping from world-space camera displacement to `PlaneSlot.size[0]` and `size[1]` is a fixed table. Planes with non-axis-aligned rotations are skipped with `skippedNonAxisAligned: true`.

**Rationale:** General rotation projection requires building a rotation matrix, projecting the frustum onto the rotated plane, and computing the bounding rectangle in plane-local coordinates. This is complex math for an edge case — the seed's 8 geometries use exclusively axis-aligned rotations. Non-axis-aligned planes (e.g., a tilted `midground` at 30°) are rare and better served by OBJ-040's precise sampling. The fixed lookup table is trivial to implement and verify.

**Rotation classification (0.01 radian tolerance):**

| Rotation (within tolerance) | Classification |
|---|---|
| `[0, 0, 0]` | `FACING_CAMERA` |
| `[-π/2, 0, 0]` | `FLOOR` |
| `[π/2, 0, 0]` | `CEILING` |
| `[0, π/2, 0]` | `LEFT_WALL` |
| `[0, -π/2, 0]` | `RIGHT_WALL` |
| Anything else | Non-axis-aligned → skip |

### D6: Coverage analysis is a development tool, not a runtime gate

**Decision:** `analyzeCoverage` and `formatCoverageMatrix` are development/documentation utilities. NOT invoked during manifest validation or rendering.

**Rationale:** TC-08 asks "do 8 geometries cover the design space?" — a qualitative question answered by examining the compatibility matrix and manually checking topic coverage. The tooling provides data; the human makes the judgment.

### D7: SpatialValidationError includes suggestion field

**Decision:** Every error includes a `suggestion` with an actionable fix instruction.

**Rationale:** Seed C-06 (blind-authorable) and C-10 (actionable error messages). The LLM needs to know how to fix errors, not just what's wrong.

### D8: Registries passed as parameters, not imported as singletons

**Decision:** All functions accept both registries as parameters.

**Rationale:** Consistent with OBJ-006 D7. Enables unit testing with mock registries. Avoids import-order coupling.

### D9: OBJ-041 provides simplified conservative oversizing; OBJ-040 provides precise validation

**Decision:** OBJ-041's `checkOversizingSufficiency` is a simplified conservative check using only `OversizeRequirements` metadata (displacement magnitudes, FOV range). It does NOT call the camera preset's `evaluate()` function or sample the actual trajectory. OBJ-040 provides the precise version using trajectory sampling and runtime texture dimensions.

**Rationale:** OBJ-041 and OBJ-040 both involve visible-area math, but they serve different purposes at different times:
- **OBJ-041** validates the geometry *definition* against the camera preset's *declared* motion envelope. It runs at manifest validation time (pre-render) and answers: "Are the geometry's authored plane sizes plausible for this camera?"
- **OBJ-040** validates *actual* plane sizes (after texture auto-sizing) against the *actual* camera trajectory (via `evaluate()` sampling). It runs at render setup time and answers: "Will this specific render produce edge reveals?"

OBJ-041's check is a necessary-but-not-sufficient gate. Passing it means the combination is plausible. Failing it means it's definitely broken. OBJ-040 provides the definitive answer.

**Shared math:** Both objectives need `visibleHeight = 2 * d * tan(fov/2)` and `visibleWidth = visibleHeight * aspectRatio`. This formula is trivial (one line) and does not warrant a shared utility module. Both may inline it. If a future integrator wants to extract it to `src/spatial/frustum.ts`, that's a backward-compatible refactor, not a design dependency.

### D10: Speed > 1.0 may cause oversizing failures — separate category, not blocking

**Decision:** When `speed > 1.0`, the oversizing check uses effective displacement (`maxDisplacement * speed`). Failures are reported as `'oversizing'` category errors. The manifest validator (OBJ-017) can choose to treat oversizing errors as warnings.

**Rationale:** Speed > 1.0 is a legitimate authoring choice. The conservative check may flag it even when it works fine in practice. The separate category lets OBJ-017 apply different severity.

### D11: Camera-passes-through detection

**Decision:** If the camera's position envelope (computed per D4) includes the plane's coordinate on the plane's perpendicular axis, the check reports `cameraPassesThrough: true` and `sufficient: false`.

**Rationale:** A camera passing through a plane causes catastrophic visual artifacts — the plane flips orientation and textures render inside-out. This is a structural error more serious than undersizing. The perpendicular axis depends on orientation: Z for facing-camera planes, Y for floor/ceiling, X for walls. This uses the same axis-aligned classification from D5.

## Acceptance Criteria

### Compatibility Validation

- [ ] **AC-01:** `validateSceneSpatialCompatibility` returns an error when the camera name does not exist in the camera registry. Error message includes the invalid camera name and lists all available camera presets. Error has category `'compatibility'`.
- [ ] **AC-02:** `validateSceneSpatialCompatibility` returns an error when the camera name is not in the geometry's `compatible_cameras` list. Error message names the geometry, the camera, and lists the geometry's compatible cameras. Suggestion names specific valid alternatives.
- [ ] **AC-03:** `validateSceneSpatialCompatibility` returns an error when the geometry name is not in the camera preset's `compatibleGeometries` list. Error message names the camera, the geometry, and lists the camera's compatible geometries.
- [ ] **AC-04:** `validateSceneSpatialCompatibility` returns an empty array when geometry and camera are mutually compatible, the camera exists, planes are sufficiently sized, and `aspectRatio` is valid.
- [ ] **AC-05:** `validateSceneSpatialCompatibility` returns an empty array (skips all checks) when the geometry name does not exist in the geometry registry.
- [ ] **AC-06:** `validateSceneSpatialCompatibility` runs oversizing checks using the provided `aspectRatio`, `cameraParams.speed` (default 1.0), and `cameraParams.offset` (default [0,0,0]).

### Registry Consistency

- [ ] **AC-07:** `validateRegistryConsistency` detects a geometry that lists a camera name not present in the camera registry. Error includes the geometry name and the missing camera name.
- [ ] **AC-08:** `validateRegistryConsistency` detects a camera preset that lists a geometry name not present in the geometry registry. Error includes the camera name and the missing geometry name.
- [ ] **AC-09:** `validateRegistryConsistency` detects a one-directional mismatch: geometry G lists camera C, but camera C does not list geometry G. Error names both and identifies which side is missing.
- [ ] **AC-10:** `validateRegistryConsistency` detects the reverse mismatch: camera C lists geometry G, but geometry G does not list camera C.
- [ ] **AC-11:** `validateRegistryConsistency` returns an empty array when both registries are fully bidirectionally consistent.
- [ ] **AC-12:** All `SpatialValidationError` objects from `validateRegistryConsistency` have `sceneId: null`.

### Oversizing Sufficiency

- [ ] **AC-13:** `checkOversizingSufficiency` returns one `OversizingCheckResult` per slot in the geometry.
- [ ] **AC-14:** For a static camera (zero displacement, constant FOV) and a plane sized to exactly fill the visible area at its distance, `sufficient` is `true` and `effectiveOversizeFactor` is approximately 1.0 (within floating-point tolerance).
- [ ] **AC-15:** For a forward-pushing camera (maxDisplacementZ > 0) and a backdrop plane (`rotation=[0,0,0]`) that is not oversized, `sufficient` is `false`.
- [ ] **AC-16:** For a forward-pushing camera and a floor plane (`rotation=[-π/2,0,0]`), the `requiredSize[1]` (floor's local height, which maps to world Z) reflects the camera's Z displacement range, not the camera's Y displacement.
- [ ] **AC-17:** For a left wall plane (`rotation=[0,π/2,0]`), `requiredSize[0]` (wall's local width, which maps to world Z) reflects the camera's Z displacement range, and `requiredSize[1]` reflects camera Y displacement.
- [ ] **AC-18:** `speed` scales effective displacement: `checkOversizingSufficiency` with `speed=2.0` requires larger planes than `speed=1.0` for non-static cameras.
- [ ] **AC-19:** `offset` increases required size: a non-zero offset in any axis increases the required plane dimensions in the corresponding projected axis.
- [ ] **AC-20:** `effectiveOversizeFactor` < 1.0 if and only if `sufficient === false` (when `skippedNonAxisAligned` is false and `cameraPassesThrough` is false).
- [ ] **AC-21:** When the camera's position envelope includes a facing-camera plane's Z coordinate, `cameraPassesThrough` is `true` and `sufficient` is `false`.
- [ ] **AC-22:** When the camera's position envelope includes a floor plane's Y coordinate, `cameraPassesThrough` is `true` and `sufficient` is `false`.
- [ ] **AC-23:** For a plane with non-axis-aligned rotation (e.g., `[0.5, 0.3, 0]`), `skippedNonAxisAligned` is `true` and `sufficient` is `true`.
- [ ] **AC-24:** `validateOversizing` returns one `SpatialValidationError` per slot where `checkOversizingSufficiency` returned `sufficient === false`, and no errors for sufficient slots.
- [ ] **AC-25:** `validateOversizing` error messages for `cameraPassesThrough` slots mention that the camera passes through the plane and suggest moving the plane or choosing a different camera preset.

### Coverage Analysis

- [ ] **AC-26:** `analyzeCoverage` returns correct `totalGeometries` and `totalCameraPresets` counts.
- [ ] **AC-27:** `analyzeCoverage` correctly identifies bidirectionally compatible pairs (both sides declare compatibility). `totalCompatiblePairs` counts only these.
- [ ] **AC-28:** `analyzeCoverage` correctly identifies orphaned geometries (no bidirectionally compatible cameras) and orphaned cameras.
- [ ] **AC-29:** `formatCoverageMatrix` produces valid Markdown with geometry rows, camera columns, and ✓/G→/→C/blank cells.

### Error Quality

- [ ] **AC-30:** Every `SpatialValidationError` has a non-empty `suggestion` field containing actionable instructions.
- [ ] **AC-31:** Error messages use seed vocabulary (geometry, camera path, plane slot) consistently.

### Module Constraints

- [ ] **AC-32:** The module imports only from `src/scenes/geometries/` (OBJ-005), `src/camera/` (OBJ-006), and `src/spatial/` (OBJ-003). No Three.js, Puppeteer, or Node.js-specific APIs.
- [ ] **AC-33:** All functions are deterministic: same inputs produce same outputs.

## Edge Cases and Error Handling

### Compatibility Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Camera name is empty string | Error: camera not found in registry. Lists available cameras. |
| Geometry exists but has empty `compatible_cameras` | Cannot happen — `validateGeometryDefinition` (OBJ-005 AC-06) rejects this. If encountered, any camera is incompatible. |
| Same camera listed twice in geometry's `compatible_cameras` | Not an error for OBJ-041. Treated as one entry. |
| Camera name omitted from manifest | Resolved to geometry's `default_camera` by OBJ-004/OBJ-017 before OBJ-041 is invoked. OBJ-041 always receives a resolved camera name. |

### Registry Consistency Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty geometry registry, non-empty camera registry | Every camera's `compatibleGeometries` entries flagged as non-existent. |
| Both registries empty | Returns empty array (vacuously consistent). |
| Geometry "tunnel" lists camera "crane_up"; camera "crane_up" does NOT list "tunnel" | Error: "Camera 'crane_up' is listed as compatible by geometry 'tunnel', but 'crane_up' does not list 'tunnel' in its compatibleGeometries." Suggestion: "Add 'tunnel' to crane_up's compatibleGeometries, or remove 'crane_up' from tunnel's compatible_cameras." |
| Multiple mismatches | All reported, not just the first. |

### Oversizing Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `speed = 0` | Invalid — `resolveCameraParams` (OBJ-006) throws before OBJ-041 is called. If received, treat as speed=1.0 defensively. |
| `speed = 0.001` (very small) | Near-static camera. All planes should pass. |
| `offset = [0, 0, 0]` | No additional displacement. |
| Camera range includes plane's perpendicular coordinate | `cameraPassesThrough: true`, `sufficient: false`. Error message: "Plane '{slotName}' at {axis}={value} is within the camera's movement range [{min}, {max}]. The camera would pass through this plane." |
| Plane behind camera (never visible) | If the plane's Z > maxCamZ for a facing-camera plane, the closest distance is `abs(planeZ - maxCamZ)`. The check still runs normally — the plane is behind the camera and visible area calculation works. This is not a special case. (A plane behind the camera is only invisible if it's behind the near plane AND the camera never turns to face it — but camera paths always face forward, so a plane at Z > camZ is behind the camera. However, during forward push the camera Z decreases, so a plane at Z=-5 and camera starting at Z=5 pushing to Z=-20 will have the camera pass Z=-5. This is caught by the passes-through check.) |
| FOV animation (fovRange[0] ≠ fovRange[1]) | Uses `fovRange[1]` (maximum FOV) for worst-case visible area. |
| Very wide aspect ratio (32:9) | Width requirement much larger. Correctly scaled by `aspectRatio`. |
| Non-axis-aligned rotation (e.g., `[0.5, 0, 0]`) | `skippedNonAxisAligned: true`, `sufficient: true`. Console warning logged. |
| Rotation close to axis-aligned but within tolerance (e.g., `[-1.5708, 0.005, 0]`) | Classified as FLOOR (within 0.01 radian tolerance). Normal check runs. |

### Coverage Analysis Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Geometry with many compatible cameras (>10) | All listed. No special handling. |
| Camera compatible with all geometries | Listed in all geometries' coverage. |
| One-directional compatibility | Shown in matrix with `geometryOnly: true` or `cameraOnly: true`. NOT counted in `totalCompatiblePairs`. |
| Both registries empty | All counts are 0. Matrix is empty. |

## Test Strategy

### Unit Tests

**Compatibility validation tests:**
1. Build mock geometry registry with 2 geometries ("stage" with `compatible_cameras: ["static", "slow_push_forward"]`, "tunnel" with `compatible_cameras: ["tunnel_push_forward", "static"]`).
2. Build mock camera registry with 3 presets ("static" with `compatibleGeometries: ["stage", "tunnel"]`, "slow_push_forward" with `compatibleGeometries: ["stage"]`, "tunnel_push_forward" with `compatibleGeometries: ["tunnel"]`).
3. Mutual compatibility → empty array.
4. Camera not in geometry's list → error with suggestion listing compatible cameras.
5. Camera not in registry → error listing available cameras.
6. Geometry not in registry → empty array (skip).
7. Geometry lists camera, camera doesn't list geometry → error identifying mismatch direction.

**Registry consistency tests:**
1. Fully consistent registries → empty array.
2. Geometry lists non-existent camera → error.
3. Camera lists non-existent geometry → error.
4. Geometry→camera but not camera→geometry → mismatch error with clear directional message.
5. Camera→geometry but not geometry→camera → mismatch error.
6. Both registries empty → empty array.
7. Multiple mismatches → all reported.

**Oversizing sufficiency tests:**

Build mock geometry and camera preset for each test:

1. **Static camera, exact-fit plane:** Zero displacement, constant FOV=50°, facing-camera plane sized to exactly `2 * d * tan(25°) * aspectRatio` wide and `2 * d * tan(25°)` tall at distance `d`. → `sufficient: true`, `effectiveOversizeFactor ≈ 1.0`.
2. **Static camera, undersized plane:** Same but plane 80% of required size. → `sufficient: false`, factor ≈ 0.8.
3. **Forward push, facing-camera plane:** `maxDisplacementZ=10`, plane at Z=-30, camera start Z=5. Camera range Z: [-5, 15]. Closest approach: `abs(-30 - (-5))` = 25. Required size = visible area at 25 + camRangeX/Y. Verify against undersized plane → `sufficient: false`.
4. **Forward push, floor plane:** `maxDisplacementZ=10`, floor at Y=-2, camera start at Y=0. Floor's `requiredSize[1]` must reflect `camRangeZ` (not camRangeY). Verify this mapping.
5. **Forward push, left wall:** `maxDisplacementZ=10`, wall at X=-4. Wall's `requiredSize[0]` reflects `camRangeZ`. Verify.
6. **Speed=2.0:** Doubles effective displacement → larger required sizes compared to speed=1.0.
7. **Offset [1,0,0]:** Adds to required width for facing-camera plane.
8. **Camera passes through:** Camera start Z=5, `maxDisplacementZ=30`, plane at Z=-10. Camera range Z: [-25, 35]. Plane Z=-10 is within range. → `cameraPassesThrough: true`, `sufficient: false`.
9. **Camera passes through floor:** Camera start Y=2, `maxDisplacementY=5`, floor at Y=-2. Camera Y range [-3, 7]. Floor Y=-2 is within range. → `cameraPassesThrough: true`.
10. **FOV animation:** `fovRange=[40, 70]`. Check uses 70° for visible area. → larger required size than with constant 40°.
11. **Non-axis-aligned rotation:** `rotation=[0.5, 0, 0]`. → `skippedNonAxisAligned: true`, `sufficient: true`.
12. **Near-axis-aligned rotation:** `rotation=[-1.5708, 0.005, 0]`. → classified as FLOOR, normal check runs.

**validateOversizing wrapper tests:**
1. Mock `checkOversizingSufficiency` results with 2 sufficient and 1 insufficient slot → returns 1 error.
2. All sufficient → empty array.
3. Camera-passes-through slot → error message mentions "passes through."

**Coverage analysis tests:**
1. Known registries → verify all counts, matrix entries, and coverage summaries.
2. Orphaned geometry → appears in `orphanedGeometries`.
3. One-directional compatibility → shown in matrix, NOT in `totalCompatiblePairs`.
4. `formatCoverageMatrix` → parseable Markdown with ✓ markers in correct cells.

### Relevant Testable Claims

- **TC-07** (partial): Spatial compatibility validation catches camera-geometry mismatches before rendering. OBJ-041 provides spatial rules; OBJ-017 integrates them.
- **TC-08** (direct): `analyzeCoverage` provides data to evaluate geometry coverage. Include a test exercising it with all 8 proposed geometries and all 11 proposed cameras once they're implemented.
- **TC-04** (partial): Spatial compatibility validation ensures valid combinations produce correct spatial relationships.

### Integration Tests (post-implementation of OBJ-018+ and OBJ-026+)

1. `validateRegistryConsistency` against real registries → empty array.
2. `analyzeCoverage` → every geometry has ≥1 compatible camera.
3. `checkOversizingSufficiency` for every bidirectionally-compatible geometry+camera pair at speed=1.0, offset=[0,0,0], aspect=16/9 → all slots sufficient.

## Integration Points

### Depends on

| Dependency | What OBJ-041 imports |
|---|---|
| **OBJ-005** (Scene Geometry Type Contract) | `SceneGeometry`, `PlaneSlot`, `GeometryRegistry` types. `isCameraCompatible()` for checking geometry's compatible_cameras list. |
| **OBJ-006** (Camera Path Type Contract) | `CameraPathPreset`, `CameraPathRegistry`, `OversizeRequirements`, `CameraParams` types. `isCameraPathName()`, `getCameraPath()` for registry lookups. |
| **OBJ-003** (Spatial Math) | `Vec3` type for offset parameters. |

### Consumed by

| Downstream | How it uses OBJ-041 |
|---|---|
| **OBJ-017** (Manifest structural validation) | Calls `validateSceneSpatialCompatibility` for each scene, passing `aspectRatio` from `composition.width/height`. Adds spatial errors to structural errors. May treat `'oversizing'` category as warnings. |
| **OBJ-069** (Edge reveal systematic validation) | Uses `checkOversizingSufficiency` and `validateRegistryConsistency` as part of comprehensive edge-reveal testing. |
| **OBJ-071** (SKILL.md) | Uses `analyzeCoverage`/`formatCoverageMatrix` to generate geometry-camera compatibility reference. |
| **Development/CI** | `validateRegistryConsistency` runs as CI check when geometries or cameras change. |

### File Placement

```
depthkit/
  src/
    validation/
      spatial-compatibility.ts   # validateSceneSpatialCompatibility,
                                 # validateRegistryConsistency,
                                 # checkOversizingSufficiency,
                                 # validateOversizing,
                                 # SpatialValidationError,
                                 # OversizingCheckResult types
      coverage-analysis.ts       # analyzeCoverage, formatCoverageMatrix,
                                 # CompatibilityMatrixEntry, CoverageAnalysis
      index.ts                   # Barrel export
```

Placed under `src/validation/` rather than `src/manifest/` because: (a) registry consistency validation is not manifest-specific, (b) oversizing checks are consumed by OBJ-069 outside manifest context, (c) avoids coupling to OBJ-017's file structure.

## Open Questions

### OQ-1: Should oversizing support sampling-based mode as future enhancement?

The conservative approach (symmetric envelope from `OversizeRequirements`) may be overly pessimistic for complex oscillating paths. A sampling mode using `evaluate()` at N points would be more precise.

**Recommendation:** Start with conservative bounds. This is explicitly OBJ-041's simplified gate; OBJ-040 provides the precise version. If the conservative check produces unacceptable false positives in practice, add a `mode: 'conservative' | 'sampled'` parameter in a future iteration.

### OQ-2: Should the coverage analysis include topic-mapping for TC-08?

TC-08 asks whether 8 geometries can accommodate 20/25 random topics. The programmatic analysis shows compatibility counts, but topic evaluation is qualitative.

**Recommendation:** No. OBJ-041 provides quantitative tooling. Qualitative TC-08 evaluation is done by the human during tuning. Adding topic templates would overcomplicate this module.

---

I believe this revision addresses all seven issues:

1. **Issue 1 (Critical):** Added `aspectRatio: number` parameter to `validateSceneSpatialCompatibility`. Updated AC-04, AC-06.
2. **Issue 2 (Major):** Added explicit "Camera Position Envelope Algorithm" section in `checkOversizingSufficiency` JSDoc, with symmetric computation from start position and displacement magnitudes.
3. **Issue 3 (Major):** Added D9 explicitly distinguishing OBJ-041 (simplified conservative using metadata only) from OBJ-040 (precise using trajectory sampling). Both may inline the trivial `2*d*tan(fov/2)` formula.
4. **Issue 4 (Major):** Added explicit `size[0]`/`size[1]` mapping table for all five axis-aligned rotations. Added non-axis-aligned handling: skip with `skippedNonAxisAligned: true`, `sufficient: true`. Added AC-16, AC-17, AC-23.
5. **Issue 5 (Minor):** Fixed `effectiveOversizeFactor` definition: `min(actual[0]/required[0], actual[1]/required[1])`, values < 1.0 = undersized. Added AC-20.
6. **Issue 6 (Minor):** Added AC-24 linking `validateOversizing` to `checkOversizingSufficiency` results.
7. **Issue 7 (Minor):** Added `cameraPassesThrough` field on `OversizingCheckResult`. Added D11. Added AC-21, AC-22, AC-25. Updated edge case table.

Challenger, please verify these changes address your concerns.

---

## Round 4 — spec_challenger

I've carefully verified each of my seven original issues against the revised spec. Let me report:

**Issue 1 (Critical): Missing `aspectRatio` parameter** — ✅ VERIFIED. `aspectRatio: number` is now in the `validateSceneSpatialCompatibility` signature. AC-04 and AC-06 reference it.

**Issue 2 (Major): Closest-approach algorithm underspecified** — ✅ VERIFIED. The "Camera Position Envelope Algorithm" section specifies symmetric computation explicitly. Per-plane distance calculations are spelled out per orientation.

**Issue 3 (Major): Overlapping math with OBJ-040** — ✅ VERIFIED. D9 cleanly distinguishes OBJ-041 (simplified conservative, metadata-only) from OBJ-040 (precise, trajectory-sampling).

**Issue 4 (Major): Rotated-plane projection incomplete** — ✅ VERIFIED. Explicit `size[0]`/`size[1]` mapping table for five axis-aligned cases. Non-axis-aligned: skip with `skippedNonAxisAligned: true`. AC-16, AC-17, AC-23 cover this.

**Issue 5 (Minor): `effectiveOversizeFactor`** — ✅ VERIFIED. Now `min(actual[0]/required[0], actual[1]/required[1])`, < 1.0 = undersized. AC-20 ties it to `sufficient`.

**Issue 6 (Minor): Missing AC linking functions** — ✅ VERIFIED. AC-24 added.

**Issue 7 (Minor): Camera passes through plane** — ✅ VERIFIED. `cameraPassesThrough` field, D11, AC-21/22/25.

I have two remaining minor observations that are not blocking:

1. **EPSILON undefined:** The algorithm references `EPSILON` (e.g., `max(EPSILON, ...)`) without specifying its value. This is trivially resolvable by the implementer but should be noted.

2. **Prose cleanup:** The `checkOversizingSufficiency` JSDoc contains a "Wait — let me be more precise" section that reads like working notes rather than specification. The final table and formulas are correct and unambiguous, so this is purely cosmetic.

Neither of these blocks implementation. I'll note them as open questions in the final spec.

All critical and major issues are resolved. The spec is implementable. I'm converging.

CONCLUSION:

The spec defines three tiers of spatial validation: (1) per-scene compatibility checking that camera-geometry pairs are mutually declared compatible, (2) registry-level bidirectional consistency enforcement, and (3) conservative oversizing sufficiency checks using camera `OversizeRequirements` metadata with explicit axis-aligned rotation projection. It also provides a coverage analysis utility for TC-08. The boundary with OBJ-017 (structural) and OBJ-040 (precise trajectory-sampling) is clearly drawn via D3 and D9.

Let me write the files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the final spec and update meta.json.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-041",
     3→  "description": "Geometry-camera spatial compatibility validation -- cross-reference validation ensuring camera paths are compatible with chosen geometries (a tunnel_push doesn't work on a stage geometry), oversizing sufficiency checks. Produces spatial validation rules that feed into the manifest validation pipeline (OBJ-017 handles structural validation; OBJ-041 handles spatial compatibility). TC-08 coverage analysis (do 8 geometries cover the design space).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 spatial feature. Boundary clarification: structural validation = OBJ-017, spatial compatibility = OBJ-041."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/output.md",
  "content": "# Specification: OBJ-041 \u2014 Geometry-Camera Spatial Compatibility Validation\n\n## Summary\n\nOBJ-041 defines the spatial compatibility validation layer for depthkit manifests. It cross-references the geometry registry (OBJ-005) and camera path registry (OBJ-006) to enforce three categories of spatial correctness: (1) **compatibility validation** \u2014 a manifest's chosen camera path must be mutually declared compatible with the geometry, (2) **registry consistency validation** \u2014 all cross-references between geometry and camera registries must resolve and agree bidirectionally, and (3) **oversizing sufficiency checks** \u2014 given a camera path's `OversizeRequirements` and a geometry's `PlaneSlot` sizes, planes must be large enough to prevent edge reveals. It also provides a **coverage analysis utility** for TC-08 (do 8 geometries cover the design space). This module sits between the type contracts (OBJ-005, OBJ-006) and manifest validation (OBJ-017), producing spatial validation rules that OBJ-017 invokes additively on top of structural validation.\n\n## Interface Contract\n\n### Core Validation Types\n\n```typescript\n// src/validation/spatial-compatibility.ts\n\nimport type { SceneGeometry, GeometryRegistry } from '../scenes/geometries';\nimport type { CameraPathPreset, CameraPathRegistry, OversizeRequirements, CameraParams } from '../camera';\nimport type { Vec3 } from '../spatial/types';\n\n/**\n * A single spatial validation error. Structured for programmatic\n * error handling and actionable LLM feedback (seed C-06, C-10).\n */\nexport interface SpatialValidationError {\n  /** Error category for filtering/grouping */\n  category: 'compatibility' | 'registry_consistency' | 'oversizing';\n\n  /** Identifier of the scene in the manifest (e.g., 'scene_001'), or null for registry-level errors */\n  sceneId: string | null;\n\n  /
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/meta.json",
  "content": "{\n  \"id\": \"OBJ-041\",\n  \"description\": \"Geometry-camera spatial compatibility validation -- cross-reference validation ensuring camera paths are compatible with chosen geometries (a tunnel_push doesn't work on a stage geometry), oversizing sufficiency checks. Produces spatial validation rules that feed into the manifest validation pipeline (OBJ-017 handles structural validation; OBJ-041 handles spatial compatibility). TC-08 coverage analysis (do 8 geometries cover the design space).\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-22T17:00:00Z\",\n  \"depends_on\": [\"OBJ-005\", \"OBJ-006\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 3 spatial feature. Boundary clarification: structural validation = OBJ-017, spatial compatibility = OBJ-041. Spec defines three-tier validation: scene-level compatibility, registry-level bidirectional consistency, and conservative oversizing sufficiency checks using OversizeRequirements metadata. Coverage analysis utility for TC-08. OBJ-040 provides precise trajectory-sampling validation; OBJ-041 provides simplified conservative gate.\",\n  \"status\": \"specced\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/meta.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-041/output.md nodes/OBJ-041/meta.json && git commit -m \"OBJ-041: Geometry-camera spatial compatibility validation spec\n\nThree-tier validation:\n1. Scene-level compatibility (camera-geometry mutual declaration check)\n2. Registry-level bidirectional consistency (CI/boot-time check)\n3. Conservative oversizing sufficiency (symmetric envelope from OversizeRequirements)\n\nCoverage analysis utility for TC-08.\n\nKey design decisions:\n- Bidirectional enforcement: geometry.compatible_cameras and camera.compatibleGeometries must agree\n- Conservative worst-case oversizing using metadata only (no evaluate() sampling)\n- Axis-aligned rotation lookup table for plane projection (5 cases + skip for non-axis-aligned)\n- Camera-passes-through detection for degenerate plane positions\n- Clear boundary: OBJ-041 = simplified conservative gate, OBJ-040 = precise trajectory sampling\n- Registries as parameters for testability\n\nDeliberation resolved 7 issues across 4 rounds:\n- Added aspectRatio parameter to validateSceneSpatialCompatibility\n- Specified camera position envelope algorithm (symmetric from start + displacement)\n- Distinguished OBJ-041 (metadata-only) from OBJ-040 (trajectory-sampling)\n- Explicit size[0]/size[1] mapping table for axis-aligned rotations\n- Fixed effectiveOversizeFactor definition\n- Added AC linking checkOversizingSufficiency to validateOversizing\n- Added cameraPassesThrough detection\"\n"
}
[Tool Result] [master bd72df5] OBJ-041: Geometry-camera spatial compatibility validation spec
 2 files changed, 772 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-041/output.md
The specification for OBJ-041 has been written and committed. The deliberation converged after verifying all 7 issues (1 critical, 3 major, 3 minor) were addressed in the revision:

1. **`aspectRatio` parameter** added to `validateSceneSpatialCompatibility`
2. **Camera position envelope algorithm** explicitly specified with symmetric computation
3. **OBJ-041 vs OBJ-040 boundary** cleanly separated (metadata-only conservative gate vs precise trajectory sampling)
4. **Rotated-plane projection** mapped explicitly to `size[0]`/`size[1]` for 5 axis-aligned cases, with skip for non-axis-aligned
5. **`effectiveOversizeFactor`** correctly defined as `min(actual/required)`, < 1.0 = undersized
6. **AC-24** links `validateOversizing` output to `checkOversizingSufficiency` results
7. **`cameraPassesThrough`** detection added for degenerate plane positions
