# Deliberation Transcript: OBJ-003

---

## Round 1 — spec_author

# Specification: Coordinate System and Spatial Math Reference (OBJ-003)

## Summary

OBJ-003 codifies the spatial foundation for all depthkit geometry and camera work: the Three.js right-handed coordinate conventions, the relationship between camera FOV / distance and visible area, plane sizing math, and utility functions for computing spatial relationships. This module is a pure-math reference library with zero rendering dependencies — it exports constants, types, and deterministic computation functions that every downstream geometry definition (OBJ-005), camera path preset (OBJ-006), easing/interpolation module (OBJ-007), scene sequencer (OBJ-010), and edge-reveal validator (OBJ-040) will import.

## Interface Contract

### Constants

```typescript
// src/spatial/constants.ts

/** Three.js right-handed coordinate system conventions */
export const AXIS = {
  /** Positive X = right, negative X = left */
  RIGHT: [1, 0, 0] as const,
  LEFT: [-1, 0, 0] as const,
  /** Positive Y = up, negative Y = down */
  UP: [0, 1, 0] as const,
  DOWN: [0, -1, 0] as const,
  /** Positive Z = toward viewer, negative Z = into scene */
  TOWARD_VIEWER: [0, 0, 1] as const,
  INTO_SCENE: [0, 0, -1] as const,
} as const;

/** Default camera configuration (seed Section 8.2) */
export const DEFAULT_CAMERA = {
  fov: 50,           // vertical FOV in degrees
  near: 0.1,         // near clipping plane in world units
  far: 100,          // far clipping plane in world units
  position: [0, 0, 5] as Vec3,  // default camera position
  lookAt: [0, 0, 0] as Vec3,    // default lookAt target
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

/** 
 * Input for plane sizing calculations.
 * Either provide explicit size or let the system compute
 * a size that fills the frustum at the plane's distance.
 */
export interface PlaneSizingInput {
  /** Distance from camera to plane along the view axis (positive number) */
  distanceFromCamera: number;
  /** Camera vertical FOV in degrees */
  fov: number;
  /** Composition aspect ratio (width / height) */
  aspectRatio: number;
  /** 
   * Multiplier to oversize the plane beyond the visible area.
   * 1.0 = exact fit, 1.2 = 20% larger than visible area.
   * Must be >= 1.0.
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

/** 
 * Describes the camera's projection parameters at a moment in time.
 * Used by edge-reveal validation and geometry sizing.
 */
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
 *   visibleHeight = 2 × distance × tan(fov / 2)
 *   visibleWidth  = visibleHeight × aspectRatio
 * 
 * @param distance - Distance from camera along the view axis. Must be > 0.
 * @param fov - Vertical field of view in degrees. Must be in (0, 180).
 * @param aspectRatio - Width / height ratio. Must be > 0.
 * @returns FrustumRect with visible dimensions in world units.
 * @throws RangeError if any parameter is out of valid range.
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
 * Computes the unsigned distance from a camera position to a plane position
 * along the camera's view axis (the axis from camera position toward lookAt).
 * 
 * For the common case where the camera looks down -Z and the plane is at
 * some negative Z, this is simply: cameraPosition.z - planePosition.z
 * 
 * For arbitrary camera orientations, this projects the camera-to-plane vector
 * onto the camera's forward direction vector.
 * 
 * @param cameraPosition - Camera position in world space.
 * @param cameraLookAt - Camera lookAt target in world space.
 * @param planePosition - Plane center position in world space.
 * @returns Positive distance along the view axis. Returns 0 if the plane
 *          is at or behind the camera (caller should treat as an error condition).
 */
export function computeViewAxisDistance(
  cameraPosition: Vec3,
  cameraLookAt: Vec3,
  planePosition: Vec3
): number;

/**
 * Given a texture's native pixel dimensions, computes the aspect-correct
 * plane size that fits within a bounding box while preserving the image's
 * aspect ratio.
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

/**
 * Converts degrees to radians.
 */
export function degToRad(degrees: number): number;

/**
 * Converts radians to degrees.
 */
export function radToDeg(radians: number): number;

/**
 * Computes the Euclidean distance between two points in 3D space.
 */
export function distance3D(a: Vec3, b: Vec3): number;

/**
 * Normalizes a Vec3 to unit length. Returns [0,0,0] for zero-length input.
 */
export function normalize(v: Vec3): Vec3;

/**
 * Computes the dot product of two Vec3s.
 */
export function dot(a: Vec3, b: Vec3): number;

/**
 * Subtracts vector b from vector a: a - b.
 */
export function subtract(a: Vec3, b: Vec3): Vec3;

/**
 * Scales a Vec3 by a scalar.
 */
export function scale(v: Vec3, s: number): Vec3;

/**
 * Adds two Vec3s.
 */
export function add(a: Vec3, b: Vec3): Vec3;
```

### Module Exports

```typescript
// src/spatial/index.ts
// Barrel export — the single import point for all downstream consumers

export * from './types';
export * from './constants';
export * from './math';
```

## Design Decisions

### D1: Pure math module with no Three.js dependency

This module runs in Node.js (orchestrator side) and could also be bundled for the browser page side. It must NOT import `three` or any rendering library. The types use plain tuples (`[number, number, number]`) rather than `THREE.Vector3` to maintain this boundary. Downstream consumers (geometries, camera presets) will convert to Three.js types at the boundary.

**Rationale:** The spatial math is used in validation (manifest validation runs in Node.js before Puppeteer launches), in geometry definitions (which are authored in Node.js and serialized to the page), and potentially in the page itself. A dependency on Three.js would couple validation to the renderer, violating separation of concerns. It also keeps the module trivially unit-testable.

### D2: Distance is always positive and measured along the view axis

The `computeViewAxisDistance` function returns the projected distance along the camera's forward direction, not the raw Euclidean distance. This matters because `computeFrustumRect` uses the perpendicular distance from the camera to compute the visible rectangle (this is how a perspective projection actually works).

For the common case where the camera looks down -Z: `distance = camera.z - plane.z`. For arbitrary orientations, we project onto the forward vector.

**Rationale:** Euclidean distance would give incorrect frustum calculations for planes that are offset laterally — a plane 10 units to the right at the same Z-depth as the camera has zero view-axis distance, not 10 units.

### D3: Oversize factor as explicit parameter, not implicit convention

Every call to `computePlaneSize` requires the caller to state the oversize factor (defaulting to 1.0). Scene geometries will define their own oversize factors per-slot based on the expected camera motion range. This makes edge-reveal prevention explicit and auditable.

**Rationale:** The seed (Section 8.3) states "Planes should be sized larger than the visible area to prevent edge reveal during camera motion. The oversizing factor depends on how much the camera moves." Making this a parameter rather than a hidden constant ensures each geometry/camera combination can tune its own margin. The edge-reveal validator (OBJ-040) can verify that the chosen oversize factors are sufficient for the camera's motion range.

### D4: Vec3 as readonly tuple, not class

Using `readonly [number, number, number]` rather than a class or mutable array. This keeps the types simple, serializable (critical for Puppeteer message passing), and compatible with Three.js's `Vector3.fromArray()` / `Vector3.toArray()` at the boundary.

**Rationale:** Three.js's `Vector3` is mutable and carries methods — it's a rendering-side object. Our spatial math types need to cross the Node.js ↔ browser boundary via JSON serialization. Tuples serialize naturally; class instances do not.

### D5: Degrees for FOV, radians for rotation

FOV is always specified in degrees (matching Three.js's `PerspectiveCamera` constructor and the seed's convention). Plane rotations are always in radians (matching Three.js's `Euler` convention and the seed's notation `[-Math.PI/2, 0, 0]`). Conversion utilities (`degToRad`, `radToDeg`) are provided.

**Rationale:** Following Three.js conventions minimizes conversion bugs at the rendering boundary.

### D6: No dependency on composition resolution for spatial math

The spatial math operates in world units, not pixels. The only place pixel dimensions matter is computing the aspect ratio (`width / height`), which is passed as a plain number. This keeps the spatial module resolution-agnostic.

**Rationale:** Seed C-04 requires supporting multiple resolutions. The spatial math should be invariant to resolution — only the aspect ratio affects perspective projection geometry.

## Acceptance Criteria

- [ ] **AC-01:** `computeFrustumRect(30, 50, 16/9)` returns `visibleHeight ≈ 27.98` and `visibleWidth ≈ 49.74` (matching seed Section 8.3 example, tolerance ±0.1).
- [ ] **AC-02:** `computeFrustumRect` throws `RangeError` for `distance <= 0`, `fov <= 0`, `fov >= 180`, and `aspectRatio <= 0`.
- [ ] **AC-03:** `computePlaneSize` with `oversizeFactor: 1.2` returns dimensions exactly 1.2× the frustum's visible dimensions.
- [ ] **AC-04:** `computePlaneSize` throws `RangeError` for `oversizeFactor < 1.0`.
- [ ] **AC-05:** `computeViewAxisDistance` for camera at `[0, 0, 5]` looking at `[0, 0, 0]` and plane at `[0, 0, -25]` returns `30` (matching the seed Section 8.3 example: "a backdrop at z=-25 with camera at z=5").
- [ ] **AC-06:** `computeViewAxisDistance` returns `0` (not a negative number) when the plane is at or behind the camera position along the view axis.
- [ ] **AC-07:** `computeAspectCorrectSize` for a 1920×1080 texture with maxWidth=50, maxHeight=30 returns a size that preserves the 16:9 ratio and fits within the 50×30 bounding box.
- [ ] **AC-08:** `PLANE_ROTATIONS.FLOOR` equals `[-Math.PI / 2, 0, 0]` exactly.
- [ ] **AC-09:** All exported constants are `readonly` / `as const` — mutation attempts cause TypeScript compilation errors.
- [ ] **AC-10:** The module has zero runtime dependencies beyond standard JavaScript `Math`.
- [ ] **AC-11:** All exports are accessible via `import { ... } from './spatial'` (barrel export).
- [ ] **AC-12:** `computeViewAxisDistance` correctly handles non-axis-aligned cameras — e.g., camera at `[0, 5, 0]` looking at `[0, 0, -10]` with a plane at `[0, 0, -10]` returns the projected distance along the forward vector, not the Euclidean distance.

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
- **`computeViewAxisDistance` with plane behind camera:** Returns `0`. The caller (geometry or edge-reveal validator) is responsible for treating distance `0` as an error or warning — a plane behind the camera is invisible and indicates a manifest authoring error.
- **`computeViewAxisDistance` with camera and lookAt at same position:** The forward vector is undefined. Return `0` and document this as an invalid camera state. Manifest validation (OBJ-010) should reject this before it reaches spatial math.
- **`computeFrustumRect` with very small FOV (e.g., 1°):** Mathematically valid but produces very large distances for tiny visible areas. No special handling — the math is correct. Geometry validators may impose their own FOV range limits.
- **`computeFrustumRect` with FOV approaching 180°:** `tan(89.9°)` is a very large number, producing enormous visible areas. Mathematically correct. The FOV should be constrained by camera presets, not by this module.
- **`computeAspectCorrectSize` with extreme aspect ratios:** A 1×10000 texture with a 10×10 bounding box will produce a very thin plane. Mathematically correct. Geometries may want to warn or reject such inputs.
- **`normalize` with zero-length vector:** Returns `[0, 0, 0]` rather than `NaN`/`Infinity`. Documented.
- **NaN / Infinity inputs:** Functions do NOT explicitly guard against `NaN`/`Infinity` in every parameter (that would be excessive). They rely on TypeScript's type system and upstream validation. If `NaN` propagates, it produces `NaN` output — standard IEEE 754 behavior. Upstream manifest validation (OBJ-010) is the correct place to catch non-finite numbers.

## Test Strategy

### Unit Tests (pure math, no rendering needed)

**Frustum computation tests:**
1. Verify the seed's worked example: FOV=50°, distance=30, aspect=16/9 → height≈27.98, width≈49.74.
2. Test with FOV=90° (tan(45°)=1, so visibleHeight = 2×distance).
3. Test with aspect ratio 1.0 (square) → width equals height.
4. Test portrait aspect ratio (9/16) → width < height.
5. Test all error conditions produce RangeError with descriptive messages.

**Plane sizing tests:**
1. `oversizeFactor: 1.0` → size matches frustum exactly.
2. `oversizeFactor: 1.5` → size is 1.5× frustum.
3. Error on `oversizeFactor: 0.5`.

**View axis distance tests:**
1. Standard case: camera at `[0,0,5]`, lookAt `[0,0,0]`, plane at `[0,0,-25]` → 30.
2. Plane at same Z as camera → distance is 0.
3. Plane behind camera → returns 0.
4. Non-axis-aligned: camera at `[0,5,0]`, lookAt `[0,0,-10]` — verify against manual projection calculation.
5. Laterally offset plane: camera at `[0,0,5]`, lookAt `[0,0,0]`, plane at `[10,0,-25]` → distance should still be 30 (only the Z-axis component matters when looking down -Z).

**Aspect-correct sizing tests:**
1. 1920×1080 image, 50×30 box → 50×28.125 (width-limited).
2. 1080×1920 image, 50×30 box → 16.875×30 (height-limited).
3. Square image, square box → exact fit.
4. Error on zero dimensions.

**Vector utility tests:**
1. `normalize([3,4,0])` → `[0.6, 0.8, 0]`.
2. `normalize([0,0,0])` → `[0,0,0]`.
3. `distance3D([0,0,0], [3,4,0])` → 5.
4. Dot product, add, subtract, scale — standard vector math verification.

**Constants tests:**
1. Verify `PLANE_ROTATIONS` values match seed Section 8.4 exactly.
2. Verify `DEFAULT_CAMERA` values match seed Section 8.2.
3. Verify `COMPOSITION_PRESETS` aspect ratios are internally consistent (width/height = aspectRatio).

### Relevant Testable Claims
- **TC-03** (partial): This module provides the math that proves perspective projection is correct — the frustum formulas, the distance calculations. The visual verification of TC-03 happens later, but mathematical correctness is verified here.
- **TC-04** (partial): By providing `computePlaneSize` with oversize factors, this module enables geometries to auto-size planes, contributing to the "no manual coordinates" goal.

## Integration Points

### Depends on
Nothing. This is a Tier 0 foundational module with zero dependencies.

### Consumed by
| Downstream | How it uses OBJ-003 |
|---|---|
| **OBJ-005** (Scene geometry slot definitions) | Imports `PlaneTransform`, `PLANE_ROTATIONS`, `computePlaneSize`, `computeFrustumRect` to define and validate slot positions/sizes for each geometry. |
| **OBJ-006** (Camera path preset definitions) | Imports `CameraState`, `DEFAULT_CAMERA`, `Vec3`, `computeViewAxisDistance` to define path keyframes and validate that camera stays within safe bounds. |
| **OBJ-007** (Easing and interpolation utilities) | Imports `Vec3` type for interpolation function signatures. |
| **OBJ-010** (Scene sequencer / manifest-to-frame mapping) | Imports `FRAME_RATES`, `COMPOSITION_PRESETS`, `CameraState` for timing and camera state computation per frame. |
| **OBJ-040** (Edge-reveal validation) | Imports `computeFrustumRect`, `computeViewAxisDistance`, `CameraState`, `PlaneTransform` to verify that no camera path reveals plane edges. |

### File Placement

```
depthkit/
  src/
    spatial/
      index.ts        # Barrel export
      types.ts         # Vec3, EulerRotation, Size2D, FrustumRect, PlaneTransform, PlaneSizingInput, PlaneSizingResult, CameraState
      constants.ts     # AXIS, DEFAULT_CAMERA, COMPOSITION_PRESETS, FRAME_RATES, PLANE_ROTATIONS
      math.ts          # computeFrustumRect, computePlaneSize, computeViewAxisDistance, computeAspectCorrectSize, degToRad, radToDeg, distance3D, normalize, dot, subtract, scale, add
```

## Open Questions

1. **Should this module include a `computeFrustumCorners` function?** OBJ-040 (edge-reveal validation) will need to know the exact frustum boundaries at each frame. A function returning the four corners of the visible rectangle at a given distance would be useful. However, this may be premature — OBJ-040 can define its own higher-level geometry using the primitives here. **Recommendation:** Defer to OBJ-040's spec. If needed, it can be added to this module in a follow-up.

2. **Should `CameraState` include `up` vector?** Three.js cameras have a configurable up vector (default `[0,1,0]`). For depthkit's use cases (no camera roll), the default up vector is always assumed. If camera roll is ever needed, `CameraState` would need an `up` field. **Recommendation:** Omit for now; add if OBJ-006 (camera paths) identifies a need for roll.

3. **Should there be a `FOV_RANGE` constant?** The seed suggests FOV values between 35°-75° for various effects. A min/max constant would help validation, but the spatial math module should not constrain creative choices — that's the camera preset's job. **Recommendation:** Do not include a range constant here. Camera presets (OBJ-006) will define their own valid FOV ranges.

---

I believe this specification is complete and precise enough for an implementer to build from. I'd like the Challenger to review and verify — particularly:
- Whether the function signatures cover all downstream needs (OBJ-005, 006, 007, 010, 040)
- Whether the edge case handling is sufficient
- Whether the Vec3-as-tuple design decision is sound given the serialization requirement

---

## Round 2 — spec_challenger

I've read the spec carefully. It's well-structured and covers most of what a foundational spatial math module needs. Here's my assessment:

## What's Sound

- **D1 (pure math, no Three.js):** Correct. Keeps validation decoupled from rendering. The tuple-based Vec3 serializes cleanly across the Puppeteer boundary.
- **D2 (view-axis distance, not Euclidean):** Mathematically necessary. Frustum width at a given depth is defined by perpendicular distance from camera, not Euclidean distance to the plane center.
- **D4 (readonly tuples):** Right choice given JSON serialization to the browser page.
- **D5 (degrees for FOV, radians for rotation):** Matches Three.js conventions. Reduces conversion bugs.
- **D6 (world units, not pixels):** Correct for resolution-agnostic spatial math.
- **Edge case table and error messages:** Specific enough to implement against.
- **Integration points table:** Correctly maps downstream consumers to what they import.

## Issues

### 1. AC-12 test case is degenerate — doesn't verify what it claims (Major)

AC-12 says: *"camera at `[0, 5, 0]` looking at `[0, 0, -10]` with a plane at `[0, 0, -10]`"*

The forward vector here is `normalize([0, -5, -10])`. The camera-to-plane vector is `[0, -5, -10]`. The plane lies **exactly along the forward ray**, so the projected distance equals the Euclidean distance (`√125 ≈ 11.18`). This test case does **not** distinguish view-axis projection from Euclidean distance — an implementation that naively returns Euclidean distance would also pass.

**Fix:** Replace with a test case where the plane is offset laterally from the camera's forward ray. For example:

> AC-12: `computeViewAxisDistance` correctly handles non-axis-aligned cameras. Camera at `[0, 5, 0]`, lookAt `[0, 0, -10]`, plane at `[5, 0, -10]`. The forward vector is `normalize([0, -5, -10])`. The camera-to-plane vector is `[5, -5, -10]`. The projected distance is `dot([5,-5,-10], normalize([0,-5,-10]))` = `(25 + 100) / √125` = `√125 ≈ 11.18`. Note: this happens to equal the on-axis case here.

Hmm, that's still numerically identical. Let me construct a genuinely distinguishing case:

Camera at `[0, 0, 0]`, lookAt `[0, 0, -1]` (looking down -Z), plane at `[10, 0, -5]`. Euclidean distance = `√(100 + 25) ≈ 11.18`. View-axis projected distance = `5` (only the Z component, since forward is `[0, 0, -1]`). 

**Proposed AC-12 replacement:**
> `computeViewAxisDistance` for camera at `[0, 0, 0]`, lookAt `[0, 0, -1]`, plane at `[10, 0, -5]` returns `5` (the projected distance along the forward vector), NOT `√125 ≈ 11.18` (the Euclidean distance).

This clearly distinguishes the two implementations. Add a second non-trivial case:
> For camera at `[0, 5, 0]`, lookAt `[0, 0, -10]`, plane at `[3, 2, -7]`, the result matches the manual dot-product projection: `dot(planePos - camPos, normalize(lookAt - camPos))`. Provide the expected numeric value (tolerance ±0.01).

Let me compute: forward = normalize([0,-5,-10]) = [0, -0.4472, -0.8944]. Cam-to-plane = [3, -3, -7]. Dot = 0 + 1.3416 + 6.2610 = 7.60 (approx). Euclidean = √(9+9+49) = √67 ≈ 8.19. These differ, so this test works.

### 2. Missing acceptance criterion for zero-length forward vector (Major)

The edge case section says: *"camera and lookAt at same position: forward vector undefined, return 0."* But there's no acceptance criterion testing this. An implementer might miss this guard.

**Fix:** Add:
> AC-13: `computeViewAxisDistance` returns `0` when `cameraPosition` equals `cameraLookAt` (e.g., both `[0, 0, 5]`), since the forward vector is undefined.

### 3. Oversize factor is scalar-only — should this be documented as deliberate? (Minor)

A camera that only tracks laterally needs horizontal oversize but not vertical. A camera that only cranes up needs vertical oversize but not horizontal. A scalar `oversizeFactor` wastes texture area for directional motion.

I'm not asking for per-axis oversize in V1 — that's an optimization. But the spec should **acknowledge** this as a known limitation so OBJ-040 (edge-reveal validation) doesn't discover it later and wonder if it's a bug.

**Fix:** Add to Design Decisions or Open Questions: *"The oversize factor is scalar (uniform in both dimensions). For camera paths with purely directional motion (e.g., lateral-only), this overallocates in the non-moving axis. Per-axis oversize factors could be added if OBJ-040 identifies this as a significant issue, but scalar is sufficient for V1."*

### 4. `computeViewAxisDistance` return type ambiguity for "behind camera" (Minor)

The spec says "Returns 0 if the plane is at or behind the camera." But a plane at distance 0 (coplanar with the camera) and a plane behind the camera are semantically different conditions. Returning 0 for both makes them indistinguishable to the caller.

**Fix:** Either:
- (a) Return the signed projected distance (negative = behind), document that callers should treat `<= 0` as invalid. This gives more information. OR  
- (b) Keep returning 0, but add a note in the JSDoc: *"Callers cannot distinguish 'behind camera' from 'at camera plane' — both return 0. For depthkit's use cases, both conditions indicate a manifest error and should be treated identically."*

I'd prefer (a) — the function is called `computeViewAxisDistance` and documents "unsigned distance," but if the math naturally produces a signed value, clamping to 0 destroys information. However, I won't block on this if you choose (b) with the clarifying note.

### 5. AC-07 is under-specified (Minor)

> `computeAspectCorrectSize` for a 1920×1080 texture with maxWidth=50, maxHeight=30 returns a size that preserves the 16:9 ratio and fits within the 50×30 bounding box.

This doesn't state the **expected values**. The test strategy section does (`50×28.125`), but the acceptance criterion itself is vague — an implementer reading only the AC table couldn't write a pass/fail assertion.

**Fix:** Make it concrete:
> AC-07: `computeAspectCorrectSize(1920, 1080, 50, 30)` returns `[50, 28.125]`. `computeAspectCorrectSize(1080, 1920, 50, 30)` returns `[16.875, 30]`.

---

## Summary

- **2 major issues** (AC-12 degenerate test case; missing AC for zero-length forward vector)  
- **3 minor issues** (scalar oversize documentation; signed vs unsigned distance clarity; AC-07 specificity)
- **0 critical issues**

The overall design is solid. Fix the two major issues and I'll be ready to converge (with minors documented as refinements or open questions if you prefer not to fully address them).

---

## Round 3 — spec_author

# Revised Specification: Coordinate System and Spatial Math Reference (OBJ-003)

All five issues from the challenger are valid. Here's the revised spec with each addressed.

---

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
  visibleHeight: number;
  visibleWidth: number;
  distance: number;
  fov: number;
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
  distanceFromCamera: number;
  fov: number;
  aspectRatio: number;
  /** 
   * Scalar multiplier to oversize the plane beyond the visible area.
   * 1.0 = exact fit, 1.2 = 20% larger in both dimensions.
   * Must be >= 1.0.
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
  size: Size2D;
  frustum: FrustumRect;
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
 *   visibleHeight = 2 × distance × tan(fov / 2)
 *   visibleWidth  = visibleHeight × aspectRatio
 * 
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
 * Callers should treat values <= 0 as error conditions — a plane at or
 * behind the camera is invisible and indicates a manifest authoring error.
 */
export function computeViewAxisDistance(
  cameraPosition: Vec3,
  cameraLookAt: Vec3,
  planePosition: Vec3
): number;

/**
 * Given a texture's native pixel dimensions, computes the aspect-correct
 * plane size that fits within a bounding box while preserving the image's
 * aspect ratio. Uses "fit inside" (contain) logic — the larger dimension
 * is scaled to fill its bound, the other is proportionally reduced.
 * 
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

/** Euclidean distance between two points in 3D space. */
export function distance3D(a: Vec3, b: Vec3): number;

/** Normalizes a Vec3 to unit length. Returns [0,0,0] for zero-length input. */
export function normalize(v: Vec3): Vec3;

/** Dot product of two Vec3s. */
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
export * from './types';
export * from './constants';
export * from './math';
```

## Design Decisions

### D1: Pure math module with no Three.js dependency

This module runs in Node.js (orchestrator side) and could also be bundled for the browser page side. It must NOT import `three` or any rendering library. The types use plain tuples (`[number, number, number]`) rather than `THREE.Vector3`. Downstream consumers convert to Three.js types at the boundary.

**Rationale:** Spatial math is used in validation (Node.js, before Puppeteer launches), in geometry definitions, and potentially in the browser page. A Three.js dependency would couple validation to the renderer. Plain tuples are trivially unit-testable and JSON-serializable.

### D2: Distance is signed and measured along the view axis

`computeViewAxisDistance` returns the **signed** projected distance along the camera's forward direction — positive when the plane is in front of the camera, negative when behind, zero when coplanar or when the forward vector is undefined. This is the perpendicular distance from the camera's near plane, not the Euclidean distance to the plane center.

**Rationale:** (a) Frustum computations require perpendicular distance, not Euclidean. A plane 10 units to the right at the same Z has zero view-axis distance, not 10 units — and returning 10 would produce incorrect frustum calculations. (b) Returning the signed value preserves information. Clamping to 0 would make "behind the camera" indistinguishable from "coplanar with the camera." Callers (OBJ-040 edge-reveal validation, geometry validators) should treat `<= 0` as an error condition, but the distinction between negative (behind) and zero (coplanar) may be useful for diagnostic messages.

### D3: Oversize factor is scalar (uniform), documented as deliberate V1 simplification

Every call to `computePlaneSize` requires the caller to state the oversize factor (defaulting to 1.0). The factor is applied uniformly to both width and height. For camera paths with purely directional motion (e.g., lateral-only tracking), this overallocates texture area in the non-moving axis. Per-axis oversize factors (`[horizontalFactor, verticalFactor]`) could be added if OBJ-040 identifies this as a significant issue, but scalar is sufficient for V1 correctness — it always provides *at least* enough margin, just sometimes more than strictly needed.

**Rationale:** The seed (Section 8.3) says oversizing depends on camera motion range. Making it explicit and per-call ensures each geometry/camera combination can tune its own margin. Starting scalar keeps the API simple.

### D4: Vec3 as readonly tuple, not class

Using `readonly [number, number, number]` rather than a class or mutable array. Serializes naturally via JSON for Puppeteer message passing. Compatible with Three.js's `Vector3.fromArray()` / `Vector3.toArray()` at the boundary.

### D5: Degrees for FOV, radians for rotation

FOV is always in degrees (matching Three.js `PerspectiveCamera`). Rotations are always in radians (matching Three.js `Euler`). Conversion utilities provided.

### D6: No dependency on composition resolution for spatial math

All spatial math operates in world units. Pixel dimensions only matter for computing the aspect ratio (`width / height`), passed as a plain number. Resolution-agnostic per seed C-04.

## Acceptance Criteria

- [ ] **AC-01:** `computeFrustumRect(30, 50, 16/9)` returns `visibleHeight ≈ 27.98` and `visibleWidth ≈ 49.74` (tolerance ±0.1), matching seed Section 8.3.
- [ ] **AC-02:** `computeFrustumRect` throws `RangeError` for `distance <= 0`, `fov <= 0`, `fov >= 180`, and `aspectRatio <= 0`.
- [ ] **AC-03:** `computePlaneSize` with `oversizeFactor: 1.2` returns dimensions exactly 1.2× the frustum's visible dimensions.
- [ ] **AC-04:** `computePlaneSize` throws `RangeError` for `oversizeFactor < 1.0`.
- [ ] **AC-05:** `computeViewAxisDistance` for camera at `[0, 0, 5]` looking at `[0, 0, 0]` and plane at `[0, 0, -25]` returns `30`.
- [ ] **AC-06:** `computeViewAxisDistance` returns a negative value when the plane is behind the camera (e.g., camera at `[0, 0, 5]` looking at `[0, 0, 0]`, plane at `[0, 0, 10]` returns `-5`). Callers treat `<= 0` as invalid.
- [ ] **AC-07:** `computeAspectCorrectSize(1920, 1080, 50, 30)` returns `[50, 28.125]`. `computeAspectCorrectSize(1080, 1920, 50, 30)` returns `[16.875, 30]`.
- [ ] **AC-08:** `PLANE_ROTATIONS.FLOOR` equals `[-Math.PI / 2, 0, 0]` exactly.
- [ ] **AC-09:** All exported constants are `readonly` / `as const` — mutation attempts cause TypeScript compilation errors.
- [ ] **AC-10:** The module has zero runtime dependencies beyond standard JavaScript `Math`.
- [ ] **AC-11:** All exports are accessible via `import { ... } from './spatial'` (barrel export).
- [ ] **AC-12:** `computeViewAxisDistance` for camera at `[0, 0, 0]`, lookAt `[0, 0, -1]`, plane at `[10, 0, -5]` returns `5` (the projected distance along forward), NOT `√125 ≈ 11.18` (the Euclidean distance).
- [ ] **AC-13:** `computeViewAxisDistance` for camera at `[0, 5, 0]`, lookAt `[0, 0, -10]`, plane at `[3, 2, -7]` returns `≈ 7.60` (tolerance ±0.01), matching manual dot-product projection: `dot([3, -3, -7], normalize([0, -5, -10]))`.
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
- **`computeViewAxisDistance` with plane behind camera:** Returns a negative number. The magnitude indicates how far behind. Callers should treat `<= 0` as an error condition — a plane at or behind the camera is invisible and indicates a manifest authoring error.
- **`computeViewAxisDistance` with camera and lookAt at same position:** Forward vector is undefined. Returns `0`. Manifest validation (OBJ-010) should reject this camera state before it reaches spatial math.
- **`computeFrustumRect` with very small FOV (e.g., 1°):** Mathematically valid. No special handling. Camera presets may impose their own FOV ranges.
- **`computeFrustumRect` with FOV approaching 180°:** `tan(89.9°)` produces enormous visible areas. Mathematically correct. FOV should be constrained by camera presets, not by this module.
- **`computeAspectCorrectSize` with extreme aspect ratios:** A 1×10000 texture in a 10×10 box produces a very thin plane. Mathematically correct. Geometries may warn or reject such inputs.
- **`normalize` with zero-length vector:** Returns `[0, 0, 0]` rather than `NaN`/`Infinity`.
- **NaN / Infinity inputs:** Functions do NOT guard against `NaN`/`Infinity`. They rely on TypeScript's type system and upstream validation. `NaN` propagates per IEEE 754. Manifest validation (OBJ-010) catches non-finite numbers.

## Test Strategy

### Unit Tests (pure math, no rendering needed)

**Frustum computation tests:**
1. Seed worked example: FOV=50°, distance=30, aspect=16/9 → height≈27.98, width≈49.74.
2. FOV=90° (tan(45°)=1) → visibleHeight = 2×distance.
3. Aspect ratio 1.0 → width equals height.
4. Portrait aspect (9/16) → width < height.
5. All error conditions produce RangeError with descriptive messages.

**Plane sizing tests:**
1. `oversizeFactor: 1.0` → size matches frustum exactly.
2. `oversizeFactor: 1.5` → size is 1.5× frustum.
3. `oversizeFactor` defaults to 1.0 when omitted.
4. Error on `oversizeFactor: 0.5`.

**View axis distance tests:**
1. Standard case: camera `[0,0,5]`, lookAt `[0,0,0]`, plane `[0,0,-25]` → 30.
2. Plane at same Z as camera → 0.
3. Plane behind camera → negative value (e.g., camera `[0,0,5]`, lookAt `[0,0,0]`, plane `[0,0,10]` → -5).
4. Laterally offset plane, axis-aligned camera: camera `[0,0,0]`, lookAt `[0,0,-1]`, plane `[10,0,-5]` → 5 (not √125).
5. Non-axis-aligned camera: camera `[0,5,0]`, lookAt `[0,0,-10]`, plane `[3,2,-7]` → ≈7.60.
6. Camera equals lookAt → 0.

**Aspect-correct sizing tests:**
1. 1920×1080, box 50×30 → `[50, 28.125]` (width-limited).
2. 1080×1920, box 50×30 → `[16.875, 30]` (height-limited).
3. Square image, square box → exact fit.
4. Error on zero dimensions.

**Vector utility tests:**
1. `normalize([3,4,0])` → `[0.6, 0.8, 0]`.
2. `normalize([0,0,0])` → `[0,0,0]`.
3. `distance3D([0,0,0], [3,4,0])` → 5.
4. Standard vector math verification for dot, add, subtract, scale.

**Constants tests:**
1. `PLANE_ROTATIONS` values match seed Section 8.4 exactly.
2. `DEFAULT_CAMERA` values match seed Section 8.2.
3. `COMPOSITION_PRESETS` aspect ratios are internally consistent.

### Relevant Testable Claims
- **TC-03** (partial): This module provides the math that proves perspective projection is correct.
- **TC-04** (partial): `computePlaneSize` with oversize factors enables geometries to auto-size planes.

## Integration Points

### Depends on
Nothing. Tier 0 foundational module.

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
      types.ts         # Vec3, EulerRotation, Size2D, FrustumRect, PlaneTransform, PlaneSizingInput, PlaneSizingResult, CameraState
      constants.ts     # AXIS, DEFAULT_CAMERA, COMPOSITION_PRESETS, FRAME_RATES, PLANE_ROTATIONS
      math.ts          # computeFrustumRect, computePlaneSize, computeViewAxisDistance, computeAspectCorrectSize, degToRad, radToDeg, distance3D, normalize, dot, subtract, scale, add
```

## Open Questions

1. **Should this module include `computeFrustumCorners`?** OBJ-040 may need frustum boundary corners. **Recommendation:** Defer; OBJ-040 can request it as a follow-up addition to this module if needed.

2. **Should `CameraState` include `up` vector?** For depthkit's use cases (no camera roll), the default `[0,1,0]` up is always assumed. **Recommendation:** Omit; add if OBJ-006 identifies a need for roll.

3. **Should there be a `FOV_RANGE` constant?** The seed suggests 35°-75°. **Recommendation:** Do not include here. Camera presets (OBJ-006) define their own valid FOV ranges.

---

## Changes from Round 1

Addressing the challenger's five issues:

1. **AC-12 degenerate test case (Major):** Replaced with camera at `[0,0,0]`, lookAt `[0,0,-1]`, plane at `[10,0,-5]` → returns `5`, not `√125`. This clearly distinguishes view-axis projection from Euclidean distance. Added **AC-13** with the non-axis-aligned case (camera `[0,5,0]`, lookAt `[0,0,-10]`, plane `[3,2,-7]` → ≈7.60) as a second discriminating test.

2. **Missing AC for zero-length forward vector (Major):** Added **AC-14**: `computeViewAxisDistance` returns `0` when `cameraPosition` equals `cameraLookAt`.

3. **Scalar oversize documentation (Minor):** Added explicit documentation in `PlaneSizingInput.oversizeFactor` JSDoc and in Design Decision D3, acknowledging the limitation and stating per-axis factors can be added if OBJ-040 identifies a need.

4. **Signed vs unsigned distance (Minor):** Changed `computeViewAxisDistance` to return **signed** distance. Positive = in front, negative = behind, 0 = coplanar or undefined forward vector. Updated AC-06 to test negative return for behind-camera planes. Updated edge case documentation. This preserves information for diagnostic purposes while keeping the caller contract clear: treat `<= 0` as invalid.

5. **AC-07 specificity (Minor):** Replaced vague description with concrete expected values: `computeAspectCorrectSize(1920, 1080, 50, 30)` → `[50, 28.125]` and `computeAspectCorrectSize(1080, 1920, 50, 30)` → `[16.875, 30]`.

---

I believe all five of the challenger's issues have been addressed. I'd like the challenger to verify the revisions and confirm whether this is ready to commit.

---

## Round 4 — spec_challenger

I've verified all five fixes against the revised spec:

1. **AC-12 (degenerate test):** ✅ New test case (camera `[0,0,0]`, lookAt `[0,0,-1]`, plane `[10,0,-5]` → 5, not √125) genuinely distinguishes projection from Euclidean. AC-13's non-axis-aligned case computes correctly: forward = `normalize([0,-5,-10])` = `[0, -0.4472, -0.8944]`, cam-to-plane = `[3,-3,-7]`, dot = `1.3416 + 6.2608 ≈ 7.60`. Confirmed.

2. **AC-14 (zero-length forward):** ✅ Present and testable.

3. **Scalar oversize docs:** ✅ In both `PlaneSizingInput` JSDoc and D3. Explicitly names OBJ-040 as the trigger for revisiting.

4. **Signed distance:** ✅ AC-06 now tests negative return (`-5`). Edge case docs updated. D2 rationale explains the information-preservation argument. `computeViewAxisDistance` JSDoc clearly states the sign convention.

5. **AC-07 specificity:** ✅ Concrete values: `[50, 28.125]` and `[16.875, 30]`.

No new issues introduced by the revisions. The spec is complete, precise, and implementable.

CONCLUSION:

The specification for OBJ-003 (Coordinate System and Spatial Math Reference) is approved. It defines a pure-math, zero-dependency spatial foundation module exporting constants (coordinate axes, default camera, composition presets, plane rotations), types (Vec3, CameraState, PlaneTransform, FrustumRect, etc.), and computation functions (frustum sizing, plane sizing with explicit oversize factors, signed view-axis distance projection, aspect-correct texture sizing, and vector utilities). Key design decisions: readonly tuples for serialization across the Puppeteer boundary, signed view-axis distance for diagnostic preservation, scalar oversize factor as a documented V1 simplification, degrees for FOV / radians for rotation matching Three.js conventions. 14 acceptance criteria with concrete numeric expected values. All five challenger issues resolved.

Let me write the files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me check the current state of the files I need to update.
[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-003/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "ls -la nodes/OBJ-003/ 2>/dev/null; pwd",
  "description": "Check OBJ-003 directory and current working directory"
}
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:16 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   701 Mar 22 19:16 meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-003",
     3→  "description": "Coordinate system and spatial math reference -- Three.js right-handed coordinate conventions per Section 8.1-8.3, visible area formulas (visible_height = 2 * d * tan(FOV/2)), plane sizing math, and the relationship between camera distance, FOV, and visible area. This is the spatial foundation all geometry and camera specs reference.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": [],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 0 foundation. No dependencies. Codifies spatial conventions for all geometry and camera work."
    12→}
    13→
Good. Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "content": "# Specification: Coordinate System and Spatial Math Reference (OBJ-003)\n\n## Summary\n\nOBJ-003 codifies the spatial foundation for all depthkit geometry and camera work: the Three.js right-handed coordinate conventions, the relationship between camera FOV / distance and visible area, plane sizing math, and utility functions for computing spatial relationships. This module is a pure-math reference library with zero rendering dependencies \u2014 it exports constants, types, and deterministic computation functions that every downstream geometry definition (OBJ-005), camera path preset (OBJ-006), easing/interpolation module (OBJ-007), scene sequencer (OBJ-010), and edge-reveal validator (OBJ-040) will import.\n\n## Interface Contract\n\n### Constants\n\n```typescript\n// src/spatial/constants.ts\n\n/** Three.js right-handed coordinate system conventions */\nexport const AXIS = {\n  RIGHT: [1, 0, 0] as const,\n  LEFT: [-1, 0, 0] as const,\n  UP: [0, 1, 0] as const,\n  DOWN: [0, -1, 0] as const,\n  TOWARD_VIEWER: [0, 0, 1] as const,\n  INTO_SCENE: [0, 0, -1] as const,\n} as const;\n\n/** Default camera configuration (seed Section 8.2) */\nexport const DEFAULT_CAMERA = {\n  fov: 50,\n  near: 0.1,\n  far: 100,\n  position: [0, 0, 5] as Vec3,\n  lookAt: [0, 0, 0] as Vec3,\n} as const;\n\n/** Supported composition presets (seed C-04) */\nexport const COMPOSITION_PRESETS = {\n  LANDSCAPE_1080P: { width: 1920, height: 1080, aspectRatio: 16 / 9 },\n  PORTRAIT_1080P:  { width: 1080, height: 1920, aspectRatio: 9 / 16 },\n} as const;\n\n/** Standard frame rates (seed C-04) */\nexport const FRAME_RATES = [24, 30] as const;\n\n/**\n * Standard plane rotations for common orientations (seed Section 8.4).\n * All values in radians.\n */\nexport const PLANE_ROTATIONS = {\n  /** Faces camera (normal along +Z). Default orientation. */\n  FACING_CAMERA: [0, 0, 0] 
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/meta.json",
  "content": "{\n  \"id\": \"OBJ-003\",\n  \"description\": \"Coordinate system and spatial math reference -- Three.js right-handed coordinate conventions per Section 8.1-8.3, visible area formulas (visible_height = 2 * d * tan(FOV/2)), plane sizing math, and the relationship between camera distance, FOV, and visible area. This is the spatial foundation all geometry and camera specs reference.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-22T23:45:00Z\",\n  \"depends_on\": [],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 0 foundation. No dependencies. Codifies spatial conventions for all geometry and camera work. Spec completed via 4-round deliberation. Exports constants (AXIS, DEFAULT_CAMERA, COMPOSITION_PRESETS, FRAME_RATES, PLANE_ROTATIONS), types (Vec3, CameraState, PlaneTransform, FrustumRect, etc.), and pure-math functions (computeFrustumRect, computePlaneSize, computeViewAxisDistance, computeAspectCorrectSize, vector utilities). Zero runtime dependencies. Key decisions: signed view-axis distance, readonly tuples for serialization, scalar oversize factor, degrees for FOV / radians for rotation.\",\n  \"status\": \"specified\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/meta.json has been updated successfully.
Now let me commit these files:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-003/output.md nodes/OBJ-003/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-003): Coordinate system and spatial math reference\n\nPure-math foundation module defining Three.js coordinate conventions,\nfrustum visibility formulas, plane sizing math, and vector utilities.\nKey decisions: signed view-axis distance, readonly Vec3 tuples for\nPuppeteer serialization, scalar oversize factor, degrees/radians\nconvention matching Three.js. 14 acceptance criteria with concrete\nnumeric expected values. Zero runtime dependencies.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-003 spec and updated meta.json"
}
[Tool Result] [master fb3e4b3] spec(OBJ-003): Coordinate system and spatial math reference
 2 files changed, 419 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-003/output.md
The specification for OBJ-003 has been committed. 

**Summary of the agreed specification:**

OBJ-003 defines a pure-math, zero-dependency spatial foundation module (`src/spatial/`) with three files:

- **`types.ts`** — `Vec3`, `EulerRotation`, `Size2D`, `FrustumRect`, `PlaneTransform`, `PlaneSizingInput`, `PlaneSizingResult`, `CameraState` (all readonly tuples/interfaces for JSON serialization across the Puppeteer boundary)
- **`constants.ts`** — `AXIS`, `DEFAULT_CAMERA` (fov:50, near:0.1, far:100, position:[0,0,5]), `COMPOSITION_PRESETS` (1920×1080, 1080×1920), `FRAME_RATES` ([24,30]), `PLANE_ROTATIONS` (FLOOR, CEILING, LEFT_WALL, RIGHT_WALL, FACING_CAMERA)
- **`math.ts`** — `computeFrustumRect`, `computePlaneSize` (with explicit scalar oversize factor), `computeViewAxisDistance` (signed, projected along forward vector), `computeAspectCorrectSize`, plus vector utilities (`normalize`, `dot`, `subtract`, `scale`, `add`, `distance3D`, `degToRad`, `radToDeg`)

**Key design decisions resolved during deliberation:**
1. Signed view-axis distance (preserves behind-camera diagnostic info)
2. Scalar oversize factor with documented V1 limitation
3. Readonly tuples, not classes (serialization-first)
4. 14 concrete acceptance criteria with discriminating test cases (AC-12 distinguishes projection from Euclidean distance)
