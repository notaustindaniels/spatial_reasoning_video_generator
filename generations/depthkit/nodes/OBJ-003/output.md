# Specification: Coordinate System and Spatial Math Reference (OBJ-003)

## Summary

OBJ-003 codifies the spatial foundation for all depthkit geometry and camera work: the Three.js right-handed coordinate conventions, the relationship between camera FOV / distance and visible area, plane sizing math, and utility functions for computing spatial relationships. This module is a pure-math reference library with zero rendering dependencies — it exports constants, types, and deterministic computation functions that every downstream geometry definition (OBJ-005), camera path preset (OBJ-006), easing/interpolation module (OBJ-007), scene sequencer (OBJ-010), and edge-reveal validator (OBJ-040) will import.

## Interface Contract

### Constants

```typescript
// src/spatial/constants.ts

/** Three.js right-handed coordinate system conventions */
export const AXIS = {
  RIGHT: [1, 0, 0] as const,
  LEFT: [-1, 0, 0] as const,
  UP: [0, 1, 0] as const,
  DOWN: [0, -1, 0] as const,
  TOWARD_VIEWER: [0, 0, 1] as const,
  INTO_SCENE: [0, 0, -1] as const,
} as const;

/** Default camera configuration (seed Section 8.2) */
export const DEFAULT_CAMERA = {
  fov: 50,
  near: 0.1,
  far: 100,
  position: [0, 0, 5] as Vec3,
  lookAt: [0, 0, 0] as Vec3,
} as const;

/** Supported composition presets (seed C-04) */
export const COMPOSITION_PRESETS = {
  LANDSCAPE_1080P: { width: 1920, height: 1080, aspectRatio: 16 / 9 },
  PORTRAIT_1080P:  { width: 1080, height: 1920, aspectRatio: 9 / 16 },
} as const;

/** Standard frame rates (seed C-04) */
export const FRAME_RATES = [24, 30] as const;

/**
 * Standard plane rotations for common orientations (seed Section 8.4).
 * All values in radians.
 */
export const PLANE_ROTATIONS = {
  /** Faces camera (normal along +Z). Default orientation. */
  FACING_CAMERA: [0, 0, 0] as Vec3,
  /** Lies flat, faces up. For floor planes. */
  FLOOR: [-Math.PI / 2, 0, 0] as Vec3,
  /** Lies flat, faces down. For ceiling planes. */
  CEILING: [Math.PI / 2, 0, 0] as Vec3,
  /** Faces right. For left-side wall planes. */
  LEFT_WALL: [0, Math.PI / 2, 0] as Vec3,
  /** Faces left. For right-side wall planes. */
  RIGHT_WALL: [0, -Math.PI / 2, 0] as Vec3,
} as const;
```

### Types

```typescript
// src/spatial/types.ts

/** 3-component vector: [x, y, z] */
export type Vec3 = readonly [number, number, number];

/** Euler rotation in radians: [rx, ry, rz] */
export type EulerRotation = readonly [number, number, number];

/** 2-component size: [width, height] in world units */
export type Size2D = readonly [number, number];

/** Camera frustum dimensions at a given distance */
export interface FrustumRect {
  /** Visible height in world units */
  visibleHeight: number;
  /** Visible width in world units */
  visibleWidth: number;
  /** Distance from camera used for this calculation */
  distance: number;
  /** FOV used for this calculation (degrees) */
  fov: number;
  /** Aspect ratio used for this calculation */
  aspectRatio: number;
}

/** Describes a plane's complete spatial state */
export interface PlaneTransform {
  position: Vec3;
  rotation: EulerRotation;
  size: Size2D;
}

/** Input for plane sizing calculations. */
export interface PlaneSizingInput {
  /** Distance from camera to plane along the view axis (positive number) */
  distanceFromCamera: number;
  /** Camera vertical FOV in degrees */
  fov: number;
  /** Composition aspect ratio (width / height) */
  aspectRatio: number;
  /**
   * Scalar multiplier to oversize the plane beyond the visible area.
   * 1.0 = exact fit, 1.2 = 20% larger in both dimensions.
   * Must be >= 1.0. Defaults to 1.0.
   *
   * NOTE: This is uniform in both axes. For camera paths with purely
   * directional motion (e.g., lateral-only), this overallocates in the
   * non-moving axis. Per-axis oversize factors could be added if OBJ-040
   * (edge-reveal validation) identifies this as a significant waste issue,
   * but scalar is sufficient for V1 correctness.
   */
  oversizeFactor?: number;
}

/** Result of computing required plane dimensions */
export interface PlaneSizingResult {
  /** Recommended plane size in world units [width, height] */
  size: Size2D;
  /** The visible area at this distance (before oversizing) */
  frustum: FrustumRect;
  /** The oversize factor applied */
  oversizeFactor: number;
}

/** Describes the camera's projection parameters at a moment in time. */
export interface CameraState {
  position: Vec3;
  lookAt: Vec3;
  fov: number;
  aspectRatio: number;
  near: number;
  far: number;
}
```

### Computation Functions

```typescript
// src/spatial/math.ts

/**
 * Computes the visible rectangle of the camera frustum at a given distance.
 *
 * Formula (seed Section 8.3):
 *   visibleHeight = 2 * distance * tan(fov / 2)
 *   visibleWidth  = visibleHeight * aspectRatio
 *
 * @param distance - Distance from camera along the view axis. Must be > 0.
 * @param fov - Vertical field of view in degrees. Must be in (0, 180).
 * @param aspectRatio - Width / height ratio. Must be > 0.
 * @returns FrustumRect with visible dimensions in world units.
 * @throws RangeError if distance <= 0, fov not in (0, 180), or aspectRatio <= 0.
 */
export function computeFrustumRect(
  distance: number,
  fov: number,
  aspectRatio: number
): FrustumRect;

/**
 * Computes the recommended plane size to fill (or overfill) the camera's
 * visible area at a given distance.
 *
 * @param input - PlaneSizingInput with distance, FOV, aspect ratio, and optional oversize factor.
 * @returns PlaneSizingResult with the recommended [width, height] and frustum data.
 * @throws RangeError if oversizeFactor < 1.0 or other params out of range.
 */
export function computePlaneSize(input: PlaneSizingInput): PlaneSizingResult;

/**
 * Computes the signed distance from a camera position to a plane position
 * projected along the camera's forward direction (from camera toward lookAt).
 *
 * Returns positive values when the plane is in front of the camera,
 * negative values when behind, and 0 when coplanar with the camera
 * (perpendicular to the forward vector).
 *
 * If cameraPosition equals cameraLookAt (forward vector undefined),
 * returns 0.
 *
 * For the common case where the camera looks down -Z:
 *   result = cameraPosition.z - planePosition.z
 *
 * For arbitrary orientations, this projects the camera-to-plane vector
 * onto the normalized forward direction vector.
 *
 * Callers should treat values <= 0 as error conditions -- a plane at or
 * behind the camera is invisible and indicates a manifest authoring error.
 *
 * @param cameraPosition - Camera position in world space.
 * @param cameraLookAt - Camera lookAt target in world space.
 * @param planePosition - Plane center position in world space.
 * @returns Signed distance along the view axis.
 */
export function computeViewAxisDistance(
  cameraPosition: Vec3,
  cameraLookAt: Vec3,
  planePosition: Vec3
): number;

/**
 * Given a texture's native pixel dimensions, computes the aspect-correct
 * plane size that fits within a bounding box while preserving the image's
 * aspect ratio. Uses "fit inside" (contain) logic -- the larger dimension
 * is scaled to fill its bound, the other is proportionally reduced.
 *
 * Use case (seed Section 8.9): geometry components load textures and auto-size
 * planes to avoid image distortion.
 *
 * @param textureWidth - Texture width in pixels.
 * @param textureHeight - Texture height in pixels.
 * @param maxWidth - Maximum allowed plane width in world units.
 * @param maxHeight - Maximum allowed plane height in world units.
 * @returns Size2D [width, height] in world units, aspect-correct, fitting within bounds.
 * @throws RangeError if any dimension is <= 0.
 */
export function computeAspectCorrectSize(
  textureWidth: number,
  textureHeight: number,
  maxWidth: number,
  maxHeight: number
): Size2D;

/** Converts degrees to radians. */
export function degToRad(degrees: number): number;

/** Converts radians to degrees. */
export function radToDeg(radians: number): number;

/** Computes the Euclidean distance between two points in 3D space. */
export function distance3D(a: Vec3, b: Vec3): number;

/** Normalizes a Vec3 to unit length. Returns [0,0,0] for zero-length input. */
export function normalize(v: Vec3): Vec3;

/** Computes the dot product of two Vec3s. */
export function dot(a: Vec3, b: Vec3): number;

/** Subtracts vector b from vector a: a - b. */
export function subtract(a: Vec3, b: Vec3): Vec3;

/** Scales a Vec3 by a scalar. */
export function scale(v: Vec3, s: number): Vec3;

/** Adds two Vec3s. */
export function add(a: Vec3, b: Vec3): Vec3;
```

### Module Exports

```typescript
// src/spatial/index.ts
// Barrel export -- the single import point for all downstream consumers

export * from './types';
export * from './constants';
export * from './math';
```

## Design Decisions

### D1: Pure math module with no Three.js dependency

This module runs in Node.js (orchestrator side) and could also be bundled for the browser page side. It must NOT import `three` or any rendering library. The types use plain tuples (`[number, number, number]`) rather than `THREE.Vector3`. Downstream consumers convert to Three.js types at the boundary.

**Rationale:** Spatial math is used in validation (Node.js, before Puppeteer launches), in geometry definitions, and potentially in the browser page. A Three.js dependency would couple validation to the renderer. Plain tuples are trivially unit-testable and JSON-serializable.

### D2: Distance is signed and measured along the view axis

`computeViewAxisDistance` returns the **signed** projected distance along the camera's forward direction -- positive when the plane is in front of the camera, negative when behind, zero when coplanar or when the forward vector is undefined. This is the perpendicular distance from the camera's near plane, not the Euclidean distance to the plane center.

**Rationale:** (a) Frustum computations require perpendicular distance, not Euclidean. A plane 10 units to the right at the same Z has zero view-axis distance, not 10 units -- returning 10 would produce incorrect frustum calculations. (b) Returning the signed value preserves information. Clamping to 0 would make "behind the camera" indistinguishable from "coplanar with the camera." Callers (OBJ-040 edge-reveal validation, geometry validators) should treat `<= 0` as an error condition, but the distinction between negative (behind) and zero (coplanar) may be useful for diagnostic messages.

### D3: Oversize factor is scalar (uniform), documented as deliberate V1 simplification

Every call to `computePlaneSize` requires the caller to state the oversize factor (defaulting to 1.0). The factor is applied uniformly to both width and height. For camera paths with purely directional motion (e.g., lateral-only tracking), this overallocates texture area in the non-moving axis. Per-axis oversize factors (`[horizontalFactor, verticalFactor]`) could be added if OBJ-040 identifies this as a significant issue, but scalar is sufficient for V1 correctness -- it always provides *at least* enough margin, just sometimes more than strictly needed.

**Rationale:** The seed (Section 8.3) says oversizing depends on camera motion range. Making it explicit and per-call ensures each geometry/camera combination can tune its own margin. Starting scalar keeps the API simple.

### D4: Vec3 as readonly tuple, not class

Using `readonly [number, number, number]` rather than a class or mutable array. Serializes naturally via JSON for Puppeteer message passing. Compatible with Three.js's `Vector3.fromArray()` / `Vector3.toArray()` at the boundary.

### D5: Degrees for FOV, radians for rotation

FOV is always in degrees (matching Three.js `PerspectiveCamera`). Rotations are always in radians (matching Three.js `Euler`). Conversion utilities provided.

### D6: No dependency on composition resolution for spatial math

All spatial math operates in world units. Pixel dimensions only matter for computing the aspect ratio (`width / height`), passed as a plain number. Resolution-agnostic per seed C-04.

## Acceptance Criteria

- [ ] **AC-01:** `computeFrustumRect(30, 50, 16/9)` returns `visibleHeight ~= 27.98` and `visibleWidth ~= 49.74` (tolerance +/-0.1), matching seed Section 8.3.
- [ ] **AC-02:** `computeFrustumRect` throws `RangeError` for `distance <= 0`, `fov <= 0`, `fov >= 180`, and `aspectRatio <= 0`.
- [ ] **AC-03:** `computePlaneSize` with `oversizeFactor: 1.2` returns dimensions exactly 1.2x the frustum's visible dimensions.
- [ ] **AC-04:** `computePlaneSize` throws `RangeError` for `oversizeFactor < 1.0`.
- [ ] **AC-05:** `computeViewAxisDistance` for camera at `[0, 0, 5]` looking at `[0, 0, 0]` and plane at `[0, 0, -25]` returns `30`.
- [ ] **AC-06:** `computeViewAxisDistance` returns a negative value when the plane is behind the camera (e.g., camera at `[0, 0, 5]` looking at `[0, 0, 0]`, plane at `[0, 0, 10]` returns `-5`). Callers treat `<= 0` as invalid.
- [ ] **AC-07:** `computeAspectCorrectSize(1920, 1080, 50, 30)` returns `[50, 28.125]`. `computeAspectCorrectSize(1080, 1920, 50, 30)` returns `[16.875, 30]`.
- [ ] **AC-08:** `PLANE_ROTATIONS.FLOOR` equals `[-Math.PI / 2, 0, 0]` exactly.
- [ ] **AC-09:** All exported constants are `readonly` / `as const` -- mutation attempts cause TypeScript compilation errors.
- [ ] **AC-10:** The module has zero runtime dependencies beyond standard JavaScript `Math`.
- [ ] **AC-11:** All exports are accessible via `import { ... } from './spatial'` (barrel export).
- [ ] **AC-12:** `computeViewAxisDistance` for camera at `[0, 0, 0]`, lookAt `[0, 0, -1]`, plane at `[10, 0, -5]` returns `5` (the projected distance along forward), NOT `sqrt(125) ~= 11.18` (the Euclidean distance).
- [ ] **AC-13:** `computeViewAxisDistance` for camera at `[0, 5, 0]`, lookAt `[0, 0, -10]`, plane at `[3, 2, -7]` returns `~= 7.60` (tolerance +/-0.01), matching manual dot-product projection: `dot([3, -3, -7], normalize([0, -5, -10]))`.
- [ ] **AC-14:** `computeViewAxisDistance` returns `0` when `cameraPosition` equals `cameraLookAt` (e.g., both `[0, 0, 5]`), since the forward vector is undefined.

## Edge Cases and Error Handling

### Invalid Parameters (throw RangeError)

| Function | Condition | Error Message Pattern |
|---|---|---|
| `computeFrustumRect` | `distance <= 0` | `"distance must be positive, got {value}"` |
| `computeFrustumRect` | `fov <= 0 \|\| fov >= 180` | `"fov must be in (0, 180) degrees, got {value}"` |
| `computeFrustumRect` | `aspectRatio <= 0` | `"aspectRatio must be positive, got {value}"` |
| `computePlaneSize` | `oversizeFactor < 1.0` | `"oversizeFactor must be >= 1.0, got {value}"` |
| `computeAspectCorrectSize` | any dimension `<= 0` | `"dimensions must be positive"` |

### Boundary Behaviors

- **`computeViewAxisDistance` with plane behind camera:** Returns a negative number. The magnitude indicates how far behind. Callers should treat `<= 0` as an error condition -- a plane at or behind the camera is invisible and indicates a manifest authoring error.
- **`computeViewAxisDistance` with camera and lookAt at same position:** Forward vector is undefined. Returns `0`. Manifest validation (OBJ-010) should reject this camera state before it reaches spatial math.
- **`computeFrustumRect` with very small FOV (e.g., 1 degree):** Mathematically valid. No special handling. Camera presets may impose their own FOV ranges.
- **`computeFrustumRect` with FOV approaching 180 degrees:** `tan(89.9 degrees)` produces enormous visible areas. Mathematically correct. FOV should be constrained by camera presets, not by this module.
- **`computeAspectCorrectSize` with extreme aspect ratios:** A 1x10000 texture in a 10x10 box produces a very thin plane. Mathematically correct. Geometries may warn or reject such inputs.
- **`normalize` with zero-length vector:** Returns `[0, 0, 0]` rather than `NaN`/`Infinity`.
- **NaN / Infinity inputs:** Functions do NOT guard against `NaN`/`Infinity`. They rely on TypeScript's type system and upstream validation. `NaN` propagates per IEEE 754. Manifest validation (OBJ-010) catches non-finite numbers.

## Test Strategy

### Unit Tests (pure math, no rendering needed)

**Frustum computation tests:**
1. Seed worked example: FOV=50 degrees, distance=30, aspect=16/9 -> height ~= 27.98, width ~= 49.74.
2. FOV=90 degrees (tan(45 degrees)=1) -> visibleHeight = 2 * distance.
3. Aspect ratio 1.0 -> width equals height.
4. Portrait aspect (9/16) -> width < height.
5. All error conditions produce RangeError with descriptive messages.

**Plane sizing tests:**
1. `oversizeFactor: 1.0` -> size matches frustum exactly.
2. `oversizeFactor: 1.5` -> size is 1.5x frustum.
3. `oversizeFactor` defaults to 1.0 when omitted.
4. Error on `oversizeFactor: 0.5`.

**View axis distance tests:**
1. Standard case: camera `[0,0,5]`, lookAt `[0,0,0]`, plane `[0,0,-25]` -> 30.
2. Plane at same Z as camera -> 0.
3. Plane behind camera -> negative value (e.g., camera `[0,0,5]`, lookAt `[0,0,0]`, plane `[0,0,10]` -> -5).
4. Laterally offset plane, axis-aligned camera: camera `[0,0,0]`, lookAt `[0,0,-1]`, plane `[10,0,-5]` -> 5 (not sqrt(125)).
5. Non-axis-aligned camera: camera `[0,5,0]`, lookAt `[0,0,-10]`, plane `[3,2,-7]` -> ~= 7.60.
6. Camera equals lookAt -> 0.

**Aspect-correct sizing tests:**
1. 1920x1080, box 50x30 -> `[50, 28.125]` (width-limited).
2. 1080x1920, box 50x30 -> `[16.875, 30]` (height-limited).
3. Square image, square box -> exact fit.
4. Error on zero dimensions.

**Vector utility tests:**
1. `normalize([3,4,0])` -> `[0.6, 0.8, 0]`.
2. `normalize([0,0,0])` -> `[0,0,0]`.
3. `distance3D([0,0,0], [3,4,0])` -> 5.
4. Standard vector math verification for dot, add, subtract, scale.

**Constants tests:**
1. `PLANE_ROTATIONS` values match seed Section 8.4 exactly.
2. `DEFAULT_CAMERA` values match seed Section 8.2.
3. `COMPOSITION_PRESETS` aspect ratios are internally consistent (width/height = aspectRatio).

### Relevant Testable Claims
- **TC-03** (partial): This module provides the math that proves perspective projection is correct -- the frustum formulas, the distance calculations. The visual verification of TC-03 happens later, but mathematical correctness is verified here.
- **TC-04** (partial): `computePlaneSize` with oversize factors enables geometries to auto-size planes, contributing to the "no manual coordinates" goal.

## Integration Points

### Depends on
Nothing. Tier 0 foundational module with zero dependencies.

### Consumed by

| Downstream | How it uses OBJ-003 |
|---|---|
| **OBJ-005** (Scene geometry slot definitions) | Imports `PlaneTransform`, `PLANE_ROTATIONS`, `computePlaneSize`, `computeFrustumRect` to define and validate slot positions/sizes. |
| **OBJ-006** (Camera path preset definitions) | Imports `CameraState`, `DEFAULT_CAMERA`, `Vec3`, `computeViewAxisDistance` to define path keyframes and validate camera bounds. |
| **OBJ-007** (Easing and interpolation utilities) | Imports `Vec3` type for interpolation function signatures. |
| **OBJ-010** (Scene sequencer / manifest-to-frame mapping) | Imports `FRAME_RATES`, `COMPOSITION_PRESETS`, `CameraState` for timing and camera state computation. |
| **OBJ-040** (Edge-reveal validation) | Imports `computeFrustumRect`, `computeViewAxisDistance`, `CameraState`, `PlaneTransform` to verify no camera path reveals plane edges. |

### File Placement

```
depthkit/
  src/
    spatial/
      index.ts        # Barrel export
      types.ts         # Vec3, EulerRotation, Size2D, FrustumRect, PlaneTransform,
                       # PlaneSizingInput, PlaneSizingResult, CameraState
      constants.ts     # AXIS, DEFAULT_CAMERA, COMPOSITION_PRESETS, FRAME_RATES,
                       # PLANE_ROTATIONS
      math.ts          # computeFrustumRect, computePlaneSize, computeViewAxisDistance,
                       # computeAspectCorrectSize, degToRad, radToDeg, distance3D,
                       # normalize, dot, subtract, scale, add
```

## Open Questions

1. **Should this module include `computeFrustumCorners`?** OBJ-040 (edge-reveal validation) may need frustum boundary corners at each frame. A function returning the four corners of the visible rectangle at a given distance would be useful. **Recommendation:** Defer to OBJ-040's spec. If needed, it can be added to this module in a follow-up.

2. **Should `CameraState` include `up` vector?** Three.js cameras have a configurable up vector (default `[0,1,0]`). For depthkit's use cases (no camera roll), the default up vector is always assumed. **Recommendation:** Omit for now; add if OBJ-006 (camera paths) identifies a need for roll.

3. **Should there be a `FOV_RANGE` constant?** The seed suggests FOV values between 35-75 degrees for various effects. **Recommendation:** Do not include here. Camera presets (OBJ-006) define their own valid FOV ranges. This module should not constrain creative choices.
