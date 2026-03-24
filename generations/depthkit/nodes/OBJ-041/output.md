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
   * Invariant: effectiveOversizeFactor < 1.0 iff sufficient === false
   * (when skippedNonAxisAligned is false and cameraPassesThrough is false).
   */
  effectiveOversizeFactor: number;

  /**
   * If the camera's movement range includes the plane's perpendicular
   * coordinate (the camera would pass through or beyond the plane),
   * this is true. When true, sufficient is always false — this is a
   * spatial structure error, not just a sizing issue.
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
 * **FACING_CAMERA planes** (rotation approx [0,0,0]):
 *   The perpendicular axis is Z.
 *   - If minCamZ <= planeZ <= maxCamZ: camera passes through. cameraPassesThrough = true.
 *   - Otherwise: closestDistance = min(abs(planeZ - minCamZ), abs(planeZ - maxCamZ))
 *
 * **FLOOR/CEILING planes** (rotation approx [-pi/2,0,0] or [pi/2,0,0]):
 *   The perpendicular axis is Y.
 *   - If minCamY <= planeY <= maxCamY: camera passes through. cameraPassesThrough = true.
 *   - Otherwise: closestDistance = min(abs(planeY - minCamY), abs(planeY - maxCamY))
 *
 * **LEFT/RIGHT WALL planes** (rotation approx [0,+/-pi/2,0]):
 *   The perpendicular axis is X.
 *   - If minCamX <= planeX <= maxCamX: camera passes through. cameraPassesThrough = true.
 *   - Otherwise: closestDistance = min(abs(planeX - minCamX), abs(planeX - maxCamX))
 *
 * If closestDistance computes to 0 (camera envelope boundary touches plane),
 * use EPSILON = 0.001 world units as the minimum to avoid division by zero.
 *
 * ### Visible Area at Distance
 *
 *   maxFov = oversizeRequirements.fovRange[1]
 *   visibleHeight = 2 * closestDistance * tan(maxFov_radians / 2)
 *   visibleWidth = visibleHeight * aspectRatio
 *
 * ### Required Size Mapping (plane-local coordinates)
 *
 * The camera's world-space displacement range must be projected onto each
 * plane's local coordinate axes. For axis-aligned planes, this is a fixed
 * mapping between world axes and PlaneSlot.size[0] / size[1]:
 *
 * | Rotation              | size[0] covers (world)           | size[1] covers (world)           |
 * |-----------------------|----------------------------------|----------------------------------|
 * | FACING_CAMERA [0,0,0] | visibleWidth + camRangeX         | visibleHeight + camRangeY        |
 * | FLOOR [-pi/2,0,0]     | visibleWidth + camRangeX         | visibleHeight + camRangeZ        |
 * | CEILING [pi/2,0,0]    | visibleWidth + camRangeX         | visibleHeight + camRangeZ        |
 * | LEFT_WALL [0,pi/2,0]  | visibleHeight + camRangeZ        | visibleHeight + camRangeY        |
 * | RIGHT_WALL [0,-pi/2,0]| visibleHeight + camRangeZ        | visibleHeight + camRangeY        |
 *
 * Where:
 *   camRangeX = (maxDisplacementX * speed + abs(offset[0])) * 2
 *   camRangeY = (maxDisplacementY * speed + abs(offset[1])) * 2
 *   camRangeZ = (maxDisplacementZ * speed + abs(offset[2])) * 2
 *
 * For FACING_CAMERA planes, visibleWidth and visibleHeight are computed
 * at the closest approach distance along Z.
 *
 * For FLOOR/CEILING planes, visibleWidth and visibleHeight are computed
 * at the closest approach distance along Y (the perpendicular axis).
 * The floor extends in world X and Z, so size[0] maps to X coverage
 * and size[1] maps to Z coverage.
 *
 * For LEFT/RIGHT_WALL planes, visibleWidth and visibleHeight are computed
 * at the closest approach distance along X (the perpendicular axis).
 * The wall extends in world Z and Y, so size[0] maps to Z coverage
 * and size[1] maps to Y coverage.
 *
 * Note: For walls and floors, the "visibleWidth" from the frustum formula
 * is not directly used because the aspect ratio applies to the camera's
 * viewport, not to the plane's surface. Instead, both axes of the plane's
 * required coverage use visibleHeight (the FOV-derived extent) scaled by
 * the appropriate camera displacement. The aspect ratio is accounted for
 * by the fact that the frustum's horizontal extent at a given distance is
 * visibleHeight * aspectRatio, but for perpendicular planes, the relevant
 * extent is the angular coverage in the direction parallel to the plane's
 * surface, which depends on the viewing angle. The conservative approach
 * uses visibleHeight (the larger of the two FOV-derived extents when
 * aspectRatio < 1, or visibleWidth when aspectRatio > 1) for the plane
 * axis that aligns with the camera's wider field. Specifically:
 * - For the plane axis aligned with the camera's horizontal: use visibleWidth
 * - For the plane axis aligned with the camera's vertical: use visibleHeight
 *
 * The mapping table above reflects this: FACING_CAMERA size[0] uses
 * visibleWidth (horizontal), size[1] uses visibleHeight (vertical).
 * FLOOR size[0] uses visibleWidth (world X = camera horizontal),
 * size[1] uses visibleHeight (world Z, viewed from above at perpendicular
 * distance, the angular extent is the vertical FOV extent).
 * LEFT_WALL size[0] uses visibleHeight (world Z, looking sideways the
 * Z extent maps to vertical FOV), size[1] uses visibleHeight (world Y).
 *
 * **Non-axis-aligned rotations:** Planes whose rotation does not match
 * any of the five axis-aligned cases (within a tolerance of 0.01 radians
 * per component) are skipped. The result entry has
 * skippedNonAxisAligned = true and sufficient = true (benefit of the
 * doubt). A warning should be logged.
 *
 * **Rotation classification (0.01 radian tolerance per component):**
 *
 * | Rotation (within tolerance) | Classification  |
 * |-----------------------------|-----------------|
 * | [0, 0, 0]                   | FACING_CAMERA   |
 * | [-pi/2, 0, 0]               | FLOOR           |
 * | [pi/2, 0, 0]                | CEILING         |
 * | [0, pi/2, 0]                | LEFT_WALL       |
 * | [0, -pi/2, 0]               | RIGHT_WALL      |
 * | Anything else                | Non-axis-aligned -> skip |
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
 * "Plane '{slotName}' at {axis}={value} is within the camera's movement
 * range [{min}, {max}]. The camera would pass through this plane."
 * Suggestion: "Move the plane further from the camera path, or choose
 * a camera preset with less displacement."
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
 * Rows = geometries, columns = cameras. Cells show:
 * - checkmark for bidirectional compatibility
 * - G-> for geometry-only declaration
 * - ->C for camera-only declaration
 * - blank for no compatibility
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

**Decision:** The oversizing check recognizes five axis-aligned rotation cases (within 0.01 radian tolerance per component): `FACING_CAMERA`, `FLOOR`, `CEILING`, `LEFT_WALL`, `RIGHT_WALL`. For each, the mapping from world-space camera displacement to `PlaneSlot.size[0]` and `size[1]` is a fixed table. Planes with non-axis-aligned rotations are skipped with `skippedNonAxisAligned: true`.

**Rationale:** General rotation projection requires building a rotation matrix, projecting the frustum onto the rotated plane, and computing the bounding rectangle in plane-local coordinates. This is complex math for an edge case — the seed's 8 geometries use exclusively axis-aligned rotations. Non-axis-aligned planes (e.g., a tilted `midground` at 30 degrees) are rare and better served by OBJ-040's precise sampling. The fixed lookup table is trivial to implement and verify.

**Rotation classification (0.01 radian tolerance per component):**

| Rotation (within tolerance) | Classification |
|---|---|
| `[0, 0, 0]` | `FACING_CAMERA` |
| `[-pi/2, 0, 0]` | `FLOOR` |
| `[pi/2, 0, 0]` | `CEILING` |
| `[0, pi/2, 0]` | `LEFT_WALL` |
| `[0, -pi/2, 0]` | `RIGHT_WALL` |
| Anything else | Non-axis-aligned, skip |

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
- [ ] **AC-16:** For a forward-pushing camera and a floor plane (`rotation=[-pi/2,0,0]`), the `requiredSize[1]` (floor's local height, which maps to world Z) reflects the camera's Z displacement range, not the camera's Y displacement.
- [ ] **AC-17:** For a left wall plane (`rotation=[0,pi/2,0]`), `requiredSize[0]` (wall's local width, which maps to world Z) reflects the camera's Z displacement range, and `requiredSize[1]` reflects camera Y displacement.
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
- [ ] **AC-29:** `formatCoverageMatrix` produces valid Markdown with geometry rows, camera columns, and appropriate compatibility markers in cells.

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
| Closest distance exactly 0 (camera envelope boundary touches plane) | Use EPSILON = 0.001 world units as minimum distance to avoid division by zero. |
| FOV animation (fovRange[0] != fovRange[1]) | Uses `fovRange[1]` (maximum FOV) for worst-case visible area. |
| Very wide aspect ratio (32:9) | Width requirement much larger. Correctly scaled by `aspectRatio`. |
| Non-axis-aligned rotation (e.g., `[0.5, 0, 0]`) | `skippedNonAxisAligned: true`, `sufficient: true`. Warning logged. |
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
3. Mutual compatibility returns empty array.
4. Camera not in geometry's list returns error with suggestion listing compatible cameras.
5. Camera not in registry returns error listing available cameras.
6. Geometry not in registry returns empty array (skip).
7. Geometry lists camera, camera doesn't list geometry returns error identifying mismatch direction.

**Registry consistency tests:**
1. Fully consistent registries returns empty array.
2. Geometry lists non-existent camera returns error.
3. Camera lists non-existent geometry returns error.
4. Geometry->camera but not camera->geometry returns mismatch error with clear directional message.
5. Camera->geometry but not geometry->camera returns mismatch error.
6. Both registries empty returns empty array.
7. Multiple mismatches: all reported.

**Oversizing sufficiency tests:**

Build mock geometry and camera preset for each test:

1. **Static camera, exact-fit plane:** Zero displacement, constant FOV=50 degrees, facing-camera plane sized to exactly `2 * d * tan(25deg) * aspectRatio` wide and `2 * d * tan(25deg)` tall at distance `d`. Returns `sufficient: true`, `effectiveOversizeFactor` approximately 1.0.
2. **Static camera, undersized plane:** Same but plane 80% of required size. Returns `sufficient: false`, factor approximately 0.8.
3. **Forward push, facing-camera plane:** `maxDisplacementZ=10`, plane at Z=-30, camera start Z=5. Camera range Z: [-5, 15]. Closest approach: `abs(-30 - (-5))` = 25. Required size = visible area at 25 + camRangeX/Y. Verify against undersized plane returns `sufficient: false`.
4. **Forward push, floor plane:** `maxDisplacementZ=10`, floor at Y=-2, camera start at Y=0. Floor's `requiredSize[1]` must reflect `camRangeZ` (not camRangeY). Verify this mapping.
5. **Forward push, left wall:** `maxDisplacementZ=10`, wall at X=-4. Wall's `requiredSize[0]` reflects `camRangeZ`. Verify.
6. **Speed=2.0:** Doubles effective displacement, producing larger required sizes compared to speed=1.0.
7. **Offset [1,0,0]:** Adds to required width for facing-camera plane.
8. **Camera passes through facing-camera plane:** Camera start Z=5, `maxDisplacementZ=30`, plane at Z=-10. Camera range Z: [-25, 35]. Plane Z=-10 is within range. Returns `cameraPassesThrough: true`, `sufficient: false`.
9. **Camera passes through floor:** Camera start Y=2, `maxDisplacementY=5`, floor at Y=-2. Camera Y range [-3, 7]. Floor Y=-2 is within range. Returns `cameraPassesThrough: true`.
10. **FOV animation:** `fovRange=[40, 70]`. Check uses 70 degrees for visible area, producing larger required size than with constant 40 degrees.
11. **Non-axis-aligned rotation:** `rotation=[0.5, 0, 0]`. Returns `skippedNonAxisAligned: true`, `sufficient: true`.
12. **Near-axis-aligned rotation:** `rotation=[-1.5708, 0.005, 0]`. Classified as FLOOR, normal check runs.

**validateOversizing wrapper tests:**
1. Mock `checkOversizingSufficiency` results with 2 sufficient and 1 insufficient slot: returns 1 error.
2. All sufficient: returns empty array.
3. Camera-passes-through slot: error message mentions "passes through."

**Coverage analysis tests:**
1. Known registries: verify all counts, matrix entries, and coverage summaries.
2. Orphaned geometry: appears in `orphanedGeometries`.
3. One-directional compatibility: shown in matrix, NOT in `totalCompatiblePairs`.
4. `formatCoverageMatrix`: produces parseable Markdown with correct markers in correct cells.

### Relevant Testable Claims

- **TC-07** (partial): Spatial compatibility validation catches camera-geometry mismatches before rendering. OBJ-041 provides spatial rules; OBJ-017 integrates them.
- **TC-08** (direct): `analyzeCoverage` provides data to evaluate geometry coverage. Include a test exercising it with all 8 proposed geometries and all 11 proposed cameras once they're implemented.
- **TC-04** (partial): Spatial compatibility validation ensures valid combinations produce correct spatial relationships.

### Integration Tests (post-implementation of OBJ-018+ and OBJ-026+)

1. `validateRegistryConsistency` against real registries returns empty array.
2. `analyzeCoverage` confirms every geometry has at least 1 compatible camera.
3. `checkOversizingSufficiency` for every bidirectionally-compatible geometry+camera pair at speed=1.0, offset=[0,0,0], aspect=16/9: all slots sufficient.

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

### OQ-3: EPSILON constant value

The oversizing algorithm uses EPSILON = 0.001 world units as a minimum distance to avoid division by zero when the camera envelope boundary touches a plane. This value is specified inline in the algorithm description. If a different value proves more appropriate during implementation (e.g., matching OBJ-003's tolerance constants), it can be adjusted without affecting the contract.

### OQ-4: Visible area formula for non-perpendicular viewing of rotated planes

The current oversizing check assumes the camera views each plane approximately perpendicularly (e.g., looking straight down at a floor, looking straight at a wall). In practice, the camera typically looks forward along -Z, meaning it views floor/ceiling/wall planes at oblique angles. The oblique viewing angle increases the visible footprint on the plane surface compared to the perpendicular case. The conservative check partially accounts for this by adding the full camera displacement range, but for extreme oblique angles the visible footprint could exceed the conservative estimate. OBJ-040's trajectory sampling handles this precisely. If OBJ-041's conservative check proves insufficient for oblique-viewing scenarios, the formula can be enhanced with a viewing-angle correction factor without changing the interface.
