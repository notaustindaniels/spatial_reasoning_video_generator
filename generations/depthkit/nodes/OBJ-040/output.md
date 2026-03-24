# Specification: Plane Sizing and Edge-Reveal Prevention System (OBJ-040)

## Summary

OBJ-040 defines the plane sizing mathematics for depthkit: (1) **texture-to-plane auto-sizing** — how a plane's world-unit dimensions are computed from the loaded texture's aspect ratio and the slot's size bounds, using one of three modes (contain, cover, stretch); (2) **camera-motion-dependent oversizing** — computing the minimum plane size needed to prevent edge reveals given a camera path's displacement envelope; (3) **edge-reveal validation** — a sampling-based check that verifies no plane edge becomes visible at any point during a camera path's traversal. This is a pure spatial math module with zero rendering dependencies, extending OBJ-003's spatial library and consuming geometry definitions (OBJ-005), camera path metadata (OBJ-006), and texture metadata (OBJ-015).

## Interface Contract

### Texture-to-Plane Sizing

```typescript
// src/spatial/plane-sizing.ts

import type { Vec3, Size2D, EulerRotation } from './types';
import type { PlaneSlot } from '../scenes/geometries/types';

/**
 * Determines how a texture's aspect ratio is reconciled with a
 * slot's defined size bounding box.
 *
 * - 'contain': Plane shrinks to fit the texture's aspect ratio
 *   WITHIN the slot's size bounds. The texture is fully visible
 *   with no distortion. The plane may be smaller than the slot
 *   in one dimension ("letterboxed" or "pillarboxed").
 *   Use: subject, near_fg — preserving image content matters
 *   more than filling the spatial allocation.
 *
 * - 'cover': Plane grows so the texture's aspect ratio COVERS
 *   the slot's size bounds in both dimensions. The plane is >=
 *   the slot size in both dimensions; one dimension matches the
 *   slot, the other exceeds it. No distortion, but the plane
 *   extends beyond the slot's intended spatial area. The extra
 *   area is naturally clipped by the frustum or occluded by
 *   other planes.
 *   Use: sky, backdrop, floor, walls — full spatial coverage
 *   matters more than precise spatial allocation.
 *
 * - 'stretch': Plane stays at the slot's exact defined size.
 *   The texture is stretched/squished to fill via default UV
 *   mapping. May distort if aspect ratios differ.
 *   Use: abstract/procedural textures, gradients, or when the
 *   image was generated at the exact target aspect ratio.
 */
export type TextureSizeMode = 'contain' | 'cover' | 'stretch';

/**
 * Result of computing a texture-adjusted plane size.
 */
export interface TexturePlaneSizeResult {
  /** Final plane dimensions in world units [width, height]. */
  size: Size2D;
  /** The mode that was applied. */
  mode: TextureSizeMode;
  /**
   * Ratio of the slot's area that the final plane covers.
   * - contain: <= 1.0 (plane fits inside slot bounds)
   * - cover: >= 1.0 (plane covers all of slot bounds)
   * - stretch: exactly 1.0 (plane matches slot exactly)
   *
   * Computed as (size[0] * size[1]) / (slotWidth * slotHeight).
   */
  areaCoverageRatio: number;
}

/**
 * Computes the plane dimensions after adjusting for a texture's
 * aspect ratio, given the slot's size bounds and a sizing mode.
 *
 * - 'contain': Uses the same logic as OBJ-003's computeAspectCorrectSize.
 *   The texture aspect ratio fits within [slotWidth, slotHeight].
 *   Result: one dimension matches the slot bound, the other is smaller.
 *
 * - 'cover': The inverse of contain. The texture aspect ratio covers
 *   [slotWidth, slotHeight] completely.
 *   Let textureAR = textureWidth / textureHeight.
 *   Let slotAR = slotWidth / slotHeight.
 *   If textureAR > slotAR: height matches slot -> [slotHeight * textureAR, slotHeight]
 *   If textureAR < slotAR: width matches slot -> [slotWidth, slotWidth / textureAR]
 *   If equal: exact fit -> [slotWidth, slotHeight]
 *
 * - 'stretch': Returns [slotWidth, slotHeight] unchanged.
 *
 * @param textureWidth - Texture width in pixels. Must be > 0.
 * @param textureHeight - Texture height in pixels. Must be > 0.
 * @param slotWidth - Slot's defined width in world units. Must be > 0.
 * @param slotHeight - Slot's defined height in world units. Must be > 0.
 * @param mode - Sizing mode. Defaults to 'contain'.
 * @returns TexturePlaneSizeResult with final size and metadata.
 * @throws RangeError if any dimension is <= 0.
 */
export function computeTexturePlaneSize(
  textureWidth: number,
  textureHeight: number,
  slotWidth: number,
  slotHeight: number,
  mode?: TextureSizeMode
): TexturePlaneSizeResult;

/**
 * Suggests the appropriate TextureSizeMode for a given slot based on
 * its role in the geometry.
 *
 * Heuristic:
 * - Slots with transparent: true -> 'contain' (preserve subject outline)
 * - Slots with fogImmune: true -> 'cover' (sky/backdrop should fill)
 * - Slots whose rotation matches FLOOR, CEILING, LEFT_WALL, or RIGHT_WALL
 *   -> 'cover' (structural planes need full coverage)
 * - All other facing-camera slots -> 'cover' (backgrounds should fill)
 *
 * This is advisory — the manifest or downstream consumer can override.
 *
 * NOTE: This heuristic depends on the geometry author correctly setting
 * `transparent: true` on subject/foreground slots (per OBJ-005 slot
 * conventions). If a subject slot lacks `transparent: true`, this
 * function returns 'cover', which may produce a plane larger than the
 * slot's intended spatial allocation. See OBJ-005 slot naming conventions
 * for guidance on when to set `transparent: true`.
 *
 * @param slot - The PlaneSlot to analyze.
 * @returns The suggested TextureSizeMode.
 */
export function suggestTextureSizeMode(
  slot: PlaneSlot
): TextureSizeMode;
```

### Edge-Reveal Computation

```typescript
// src/spatial/edge-reveal.ts

import type { Vec3, Size2D, FrustumRect } from './types';
import type { CameraFrameState, CameraPathPreset, CameraParams, OversizeRequirements } from '../camera/types';
import type { PlaneTransform } from './types';
import type { SceneGeometry, PlaneSlot } from '../scenes/geometries/types';
import { computeFrustumRect, computeViewAxisDistance, add } from './math';

/**
 * Margin on each side of a facing-camera plane.
 * Positive values indicate safe coverage beyond the visible area.
 * Negative values indicate the visible area extends past the plane edge
 * (edge reveal).
 *
 * All values in world units.
 */
export interface PlaneMargins {
  /** Margin on the left side (positive = safe). */
  left: number;
  /** Margin on the right side (positive = safe). */
  right: number;
  /** Margin on the top side (positive = safe). */
  top: number;
  /** Margin on the bottom side (positive = safe). */
  bottom: number;
}

/**
 * Result of checking edge reveal for a single plane at a single
 * moment in time.
 */
export interface EdgeRevealCheck {
  /** Whether the plane fully covers the visible area at this moment. */
  safe: boolean;
  /** Per-side margins. All positive = safe. Any negative = edge reveal. */
  margins: PlaneMargins;
  /** Minimum margin across all four sides. Negative = edge reveal. */
  worstMargin: number;
  /** Normalized time t in [0, 1] at which this check was performed. */
  t: number;
  /** Camera position at this time (after offset). For diagnostics. */
  cameraPosition: Vec3;
  /** FOV at this time (degrees). For diagnostics. */
  fov: number;
  /** View-axis distance from camera to plane at this time. */
  distanceToPlane: number;
}

/**
 * Result of validating edge reveal for a single plane across
 * an entire camera path.
 */
export interface PlaneEdgeRevealResult {
  /** Slot name or identifier for this plane. */
  slotName: string;
  /** Whether the plane is safe at ALL sampled points. */
  safe: boolean;
  /**
   * The check with the smallest worstMargin across all samples.
   * If safe is false, this identifies the worst moment.
   * Null only if the plane was skipped (not facing-camera).
   */
  worstCheck: EdgeRevealCheck | null;
  /**
   * Whether this plane was skipped because it is not a
   * facing-camera plane. When true, safe is set to true
   * (no assertion made), and worstCheck is null.
   */
  skipped: boolean;
  /**
   * If skipped, the reason (e.g., "rotated plane: floor orientation").
   * Null if not skipped.
   */
  skipReason: string | null;
}

/**
 * Result of validating edge reveal for an entire geometry
 * against a camera path.
 */
export interface GeometryEdgeRevealReport {
  /** Whether ALL validated (non-skipped) planes are safe. */
  safe: boolean;
  /** Geometry name. */
  geometryName: string;
  /** Camera path preset name. */
  cameraPathName: string;
  /** Speed parameter used. */
  speed: number;
  /** Offset parameter used. */
  offset: Vec3;
  /** Aspect ratio used. */
  aspectRatio: number;
  /** Per-plane results, keyed by slot name. */
  planes: PlaneEdgeRevealResult[];
  /** Number of sample points used. */
  sampleCount: number;
}

/**
 * Computes where the camera's view center falls on a facing-camera
 * plane at a given Z depth.
 *
 * For a camera at position C looking at L:
 * - forward = normalize(L - C)
 * - t_intersect = (planeZ - C.z) / forward.z
 * - center = [C.x + t_intersect * forward.x, C.y + t_intersect * forward.y]
 *
 * For the common axis-aligned case (looking down -Z), this simplifies to
 * approximately [C.x, C.y].
 *
 * Returns a 2-component [x, y] tuple representing the point on the
 * plane where the view center falls, not a Vec3. The Z coordinate
 * is the input `planeZ`.
 *
 * @param cameraPosition - Camera position in world space.
 * @param cameraLookAt - Camera lookAt target in world space.
 * @param planeZ - The Z coordinate of the facing-camera plane.
 * @returns [x, y] — the point on the plane where the view center falls.
 *          Returns [cameraPosition[0], cameraPosition[1]] if the forward
 *          vector's Z component is zero (camera parallel to the plane).
 */
export function computeFrustumCenterAtDepth(
  cameraPosition: Vec3,
  cameraLookAt: Vec3,
  planeZ: number
): readonly [number, number];

/**
 * Computes the per-side margins for a facing-camera plane at a
 * single camera state.
 *
 * A facing-camera plane is one with rotation approximately [0, 0, 0] — its normal
 * is approximately along the +Z axis. This function assumes the plane
 * is perpendicular to the camera's view direction and uses the
 * standard frustum rect formula for visible area computation.
 *
 * Internally calls `computeFrustumCenterAtDepth` to determine where
 * the view center falls on the plane, and `computeViewAxisDistance`
 * (from OBJ-003) to determine the perpendicular distance from the
 * camera to the plane for frustum rect computation. Both are consistent
 * because the function's prerequisite is that the plane faces the
 * camera (perpendicular to the view axis).
 *
 * Margin formulas (positive = safe, negative = edge reveal):
 *
 *   Let fc = computeFrustumCenterAtDepth(cameraPosition, cameraLookAt, planePosition[2])
 *   Let vw, vh = visibleWidth, visibleHeight from computeFrustumRect
 *   Let px, py = planePosition[0], planePosition[1]
 *   Let pw, ph = planeSize[0], planeSize[1]
 *
 *   left   = (fc[0] - vw/2) - (px - pw/2)
 *          -> positive when plane's left edge extends past frustum's left edge
 *   right  = (px + pw/2) - (fc[0] + vw/2)
 *          -> positive when plane's right edge extends past frustum's right edge
 *   top    = (py + ph/2) - (fc[1] + vh/2)
 *          -> positive when plane's top edge extends past frustum's top edge
 *   bottom = (fc[1] - vh/2) - (py - ph/2)
 *          -> positive when plane's bottom edge extends past frustum's bottom edge
 *
 * Verification: Plane at x=0, w=50, frustum center fcX=0, vw=40:
 *   left = (0 - 20) - (0 - 25) = 5   (positive = safe, 5 units margin)
 *   right = (0 + 25) - (0 + 20) = 5   (positive = safe, 5 units margin)
 *
 * @param planePosition - Plane center position [x, y, z].
 * @param planeSize - Plane dimensions [width, height] in world units.
 * @param cameraPosition - Camera position [x, y, z].
 * @param cameraLookAt - Camera lookAt target [x, y, z].
 * @param fov - Vertical FOV in degrees. Must be in (0, 180).
 * @param aspectRatio - Viewport width / height. Must be > 0.
 * @returns PlaneMargins with per-side margin values.
 * @throws RangeError if distance from camera to plane along view axis is <= 0
 *         (plane is at or behind the camera):
 *         "plane is at or behind camera (view-axis distance: {value})"
 * @throws RangeError if fov or aspectRatio is out of range (propagated
 *         from computeFrustumRect).
 */
export function computeFacingPlaneMargins(
  planePosition: Vec3,
  planeSize: Size2D,
  cameraPosition: Vec3,
  cameraLookAt: Vec3,
  fov: number,
  aspectRatio: number
): PlaneMargins;

/**
 * Validates whether a facing-camera plane is free of edge reveals
 * across an entire camera path, by sampling the path at evenly-spaced
 * time points and computing margins at each.
 *
 * The camera state at each sample is computed as:
 *   state = cameraPath.evaluate(t, params)
 *   effectivePosition = add(state.position, offset)
 * where offset is resolved from params.offset ?? [0, 0, 0].
 *
 * Sample distribution: for N samples, the time values are
 * t_i = i / (N - 1) for i = 0..N-1. This includes both t=0 and t=1.
 * For the special case N=1, only t=0 is sampled.
 *
 * If the view-axis distance from the effective camera position to the
 * plane is <= 0 at any sample point (the plane is at or behind the
 * camera), that sample produces an `EdgeRevealCheck` with `safe: false`,
 * `worstMargin: -Infinity`, `distanceToPlane` set to the actual
 * (non-positive) value, and margins of
 * `{ left: -Infinity, right: -Infinity, top: -Infinity, bottom: -Infinity }`.
 * The function does not throw for this condition — it catches the
 * `RangeError` from `computeFacingPlaneMargins` (or preemptively checks
 * distance) and reports it as a maximally-failed check in the result.
 * This ensures that camera paths passing through or behind planes produce
 * diagnostic results rather than crashing validation.
 *
 * @param slotName - Name of the slot (for the result report).
 * @param planePosition - Plane center position [x, y, z].
 * @param planeSize - Plane dimensions [width, height] in world units.
 * @param cameraPath - The camera path preset to evaluate.
 * @param params - Optional camera params (speed, easing, offset).
 * @param aspectRatio - Viewport width / height.
 * @param sampleCount - Number of evenly-spaced samples in [0, 1].
 *                      Default: 100. Includes t=0 and t=1.
 *                      Must be >= 1.
 * @returns PlaneEdgeRevealResult with safe status and worst check.
 * @throws RangeError if sampleCount < 1.
 */
export function validateFacingPlaneEdgeReveal(
  slotName: string,
  planePosition: Vec3,
  planeSize: Size2D,
  cameraPath: CameraPathPreset,
  params: CameraParams | undefined,
  aspectRatio: number,
  sampleCount?: number
): PlaneEdgeRevealResult;

/**
 * Validates all facing-camera planes in a geometry against a camera
 * path. Rotated planes (floor, ceiling, walls) are skipped with a
 * documented reason in the result.
 *
 * By default, each plane's size is the slot's defined size from the
 * geometry definition. When `textureSizeOverrides` is provided, the
 * override size is used instead for any slot name present in the map.
 * This allows callers to validate against actual rendered sizes (e.g.,
 * after texture-to-plane auto-sizing in 'contain' mode, which may
 * produce a plane smaller than the slot definition).
 *
 * **Important:** Slot definition sizes represent the geometry author's
 * intended spatial allocation. Texture-adjusted sizes (especially in
 * 'contain' mode) may be smaller. If you validate only against slot
 * sizes, a plane that passes here may still reveal edges at render
 * time when the texture produces a smaller plane. Pass texture size
 * overrides when available.
 *
 * @param geometry - The scene geometry definition.
 * @param cameraPath - The camera path preset.
 * @param params - Optional camera params.
 * @param aspectRatio - Viewport width / height.
 * @param sampleCount - Samples per plane. Default: 100.
 * @param textureSizeOverrides - Optional map from slot name to actual
 *        rendered plane size [width, height] in world units. When a
 *        slot name appears in this map, its override size is used
 *        instead of the slot's defined size. Slot names NOT in the
 *        map use the geometry's slot definition size.
 * @returns GeometryEdgeRevealReport with per-plane results.
 */
export function validateGeometryEdgeReveal(
  geometry: SceneGeometry,
  cameraPath: CameraPathPreset,
  params: CameraParams | undefined,
  aspectRatio: number,
  sampleCount?: number,
  textureSizeOverrides?: Record<string, Size2D>
): GeometryEdgeRevealReport;

/**
 * Computes the minimum plane size for a facing-camera plane at a
 * given position that prevents edge reveals across an entire camera
 * path.
 *
 * Samples the camera path and computes the visible rect at the
 * plane's depth for each sample, accounting for the frustum center
 * shifting due to camera movement. Returns the size that encloses
 * ALL visible rects across all samples.
 *
 * Samples where the view-axis distance is <= 0 (camera behind the
 * plane) are skipped — they indicate a fundamentally incompatible
 * geometry+camera pairing, which should be caught by
 * validateFacingPlaneEdgeReveal. If ALL samples have distance <= 0,
 * throws RangeError: "camera is behind the plane at all sample points".
 *
 * The returned size is the tight minimum — for production use,
 * multiply by a safety margin (e.g., 1.05) to account for
 * floating-point imprecision and frame-rate-dependent interpolation.
 *
 * @param planePosition - Plane center position [x, y, z].
 * @param cameraPath - The camera path preset.
 * @param params - Optional camera params (speed, easing, offset).
 * @param aspectRatio - Viewport width / height.
 * @param sampleCount - Samples. Default: 100.
 * @returns Size2D — the minimum [width, height] in world units.
 * @throws RangeError if camera is behind the plane at all sample points.
 */
export function computeMinimumFacingPlaneSize(
  planePosition: Vec3,
  cameraPath: CameraPathPreset,
  params: CameraParams | undefined,
  aspectRatio: number,
  sampleCount?: number
): Size2D;

/**
 * Computes a per-plane oversize factor for a facing-camera plane,
 * given the camera path's OversizeRequirements.
 *
 * This is a fast analytical computation (no path sampling) that uses
 * the camera path's declared displacement envelope to estimate the
 * required oversize. See D10 for the full formula.
 *
 * The result is a conservative upper bound: it assumes worst-case
 * distance, worst-case FOV, and worst-case lateral shift all coincide,
 * which may not happen in practice. This makes it safe for geometry
 * definition (slot sizes that pass this check will also pass
 * sampling-based validation). See AC-32.
 *
 * If the returned factor exceeds a practical threshold (e.g., > 10.0),
 * this indicates the plane is too close to the camera's path for
 * effective edge-reveal prevention. The geometry author should increase
 * the plane's Z-distance from the camera's closest approach, or exclude
 * this camera path from the geometry's `compatible_cameras`.
 *
 * @param planePosition - Plane center position [x, y, z].
 * @param cameraStartPosition - Camera position at t=0.
 * @param oversizeReqs - The camera path's OversizeRequirements.
 * @param speed - The speed parameter (scales displacements). Default: 1.0.
 * @param offset - The offset parameter [x, y, z]. Default: [0, 0, 0].
 * @param fov - Base FOV used for initial plane sizing (the FOV at which
 *              the plane would be sized to exactly fit the frustum before
 *              oversizing). Default: 50. See D10 for how this interacts
 *              with the path's fovRange.
 * @param aspectRatio - Viewport width / height. Default: 16/9.
 * @returns A scalar >= 1.0. Multiply the frustum-fit plane size by this
 *          factor to prevent edge reveals.
 */
export function computeOversizeFactor(
  planePosition: Vec3,
  cameraStartPosition: Vec3,
  oversizeReqs: OversizeRequirements,
  speed?: number,
  offset?: Vec3,
  fov?: number,
  aspectRatio?: number
): number;

/**
 * Determines whether a plane's rotation represents a facing-camera
 * orientation (normal approximately along +Z).
 *
 * Compares each component of the rotation against zero with a
 * tolerance. Returns true if all three rotation components are
 * within tolerance of zero.
 *
 * Planes with rotations matching FLOOR, CEILING, LEFT_WALL, or
 * RIGHT_WALL from OBJ-003 constants return false.
 *
 * @param rotation - Euler rotation [rx, ry, rz] in radians.
 * @param tolerance - Max deviation per component in radians.
 *                    Default: 0.01 (~0.57 degrees).
 * @returns true if the plane faces the camera.
 */
export function isFacingCameraRotation(
  rotation: readonly [number, number, number],
  tolerance?: number
): boolean;
```

### Module Exports

```typescript
// src/spatial/plane-sizing.ts exports
export type { TextureSizeMode, TexturePlaneSizeResult };
export { computeTexturePlaneSize, suggestTextureSizeMode };

// src/spatial/edge-reveal.ts exports
export type {
  PlaneMargins,
  EdgeRevealCheck,
  PlaneEdgeRevealResult,
  GeometryEdgeRevealReport,
};
export {
  computeFrustumCenterAtDepth,
  computeFacingPlaneMargins,
  validateFacingPlaneEdgeReveal,
  validateGeometryEdgeReveal,
  computeMinimumFacingPlaneSize,
  computeOversizeFactor,
  isFacingCameraRotation,
};

// All re-exported from src/spatial/index.ts barrel
```

## Design Decisions

### D1: Facing-Camera Planes Get Full Analytical Validation; Rotated Planes Are Skipped With Documented Reason

**Decision:** The edge-reveal validation functions provide full margin computation and sampling-based validation for facing-camera planes (rotation approximately [0, 0, 0]). Rotated planes (floor, ceiling, walls) are skipped with `skipped: true` and a `skipReason` string in the result.

**Rationale:** Edge-reveal math for facing-camera planes is straightforward: the frustum rect at the plane's depth vs. the plane's bounds. For rotated planes, the visible area on the plane surface is a trapezoid (perspective projection of the frustum onto an angled surface), and computing whether the trapezoid exceeds the plane's bounds requires ray-plane intersection and 2D polygon containment tests — significantly more complex. The facing-camera case covers the most critical planes in every geometry (sky, backdrop, end_wall, subject, near_fg). Rotated planes (floor, ceiling, walls) are validated through the Director Agent visual tuning workflow (OBJ-059 through OBJ-066), where edge reveals are caught visually. A future extension can add rotated plane validation using viewport-corner ray casting.

**Trade-off:** Geometry authors cannot get automated edge-reveal validation for rotated planes in V1. The `skipReason` field makes this gap explicit rather than silently ignoring it.

### D2: Three Texture Sizing Modes — Contain, Cover, Stretch

**Decision:** `TextureSizeMode` has exactly three values. `contain` fits the texture AR inside the slot bounds (OBJ-003's `computeAspectCorrectSize` logic). `cover` ensures the texture AR covers the slot bounds completely (the inverse). `stretch` keeps the slot size unchanged.

**Alternatives considered:**
- **`crop` mode (adjust UV mapping):** This is a rendering concern — changing texture repeat/offset — not a plane sizing concern. It belongs to OBJ-039 (page-side renderer), not OBJ-040. Excluded.
- **Per-axis scaling modes:** Overly complex for the use cases. The three modes cover all practical needs.

**Rationale:** The seed (Section 8.9) says "each geometry component loads its textures, reads texture dimensions, and adjusts plane sizes accordingly." The three modes provide clean, predictable sizing for the three common scenarios: preserve content (contain), ensure coverage (cover), or accept distortion (stretch).

### D3: `suggestTextureSizeMode` Uses Slot Metadata, Not Slot Name Pattern Matching

**Decision:** The mode suggestion heuristic inspects `PlaneSlot.transparent` and `PlaneSlot.fogImmune` flags and the slot's rotation, rather than matching against slot name patterns.

**Rationale:** Slot names are geometry-specific and may not follow predictable patterns. The `transparent` and `fogImmune` flags are semantic indicators that reliably correlate with sizing intent. This approach is robust to new geometry-specific slot names.

### D4: Sampling-Based Validation Rather Than Analytical Worst-Case

**Decision:** `validateFacingPlaneEdgeReveal` samples the camera path at N evenly-spaced time points (default 100) and computes margins at each. It does NOT attempt to analytically find the worst-case moment.

**Rationale:** Camera paths can have arbitrary complexity (sinusoidal drift in `gentle_float`, coordinated position + FOV animation in `dolly_zoom`). Finding the analytical worst case requires solving for the maximum of a potentially complex function. Sampling at 100 points is fast (100 frustum calculations take microseconds), reliable, and correct for all path types. The default of 100 samples provides sub-1% temporal resolution, which is more than sufficient — a 10-second scene at 30fps has 300 frames, so 100 samples is one check per ~3 frames.

**Trade-off:** Could miss a brief spike between sample points. Mitigated by the `computeOversizeFactor` analytical function (which uses displacement envelopes and is intentionally conservative) and by the recommended 1.05 safety margin on `computeMinimumFacingPlaneSize`.

### D5: `computeOversizeFactor` Provides Fast Analytical Estimate From OversizeRequirements

**Decision:** A separate function uses the camera path's declared `OversizeRequirements` metadata (from OBJ-006) to compute an oversize factor analytically, without sampling the path.

**Rationale:** Geometry authors (OBJ-018 through OBJ-025) define slot sizes at definition time, before any specific camera path is selected. They need a way to size planes that works for ALL compatible camera paths. `computeOversizeFactor` takes a camera path's displacement envelope and computes the worst-case oversize needed. This is faster than `computeMinimumFacingPlaneSize` and suitable for baking into geometry definitions. The sampling-based validation is used at manifest validation time for precise per-scene checking.

### D6: Offset Is Added to Camera Position Before Margin Computation

**Decision:** When validating edge reveal, the camera position at each sample is `add(evaluate(t, params).position, resolvedOffset)`. The offset is resolved from `params.offset ?? [0, 0, 0]`.

**Rationale:** Per OBJ-006 D2, offset is applied outside `evaluate()` by the renderer. OBJ-040 must replicate this behavior to accurately model the camera's effective position. The offset shifts the frustum laterally/vertically, which directly affects edge-reveal margins.

### D7: Margin Convention — Positive Is Safe, Negative Is Edge Reveal

**Decision:** `PlaneMargins` values are positive when the plane extends beyond the visible area (safe) and negative when the visible area extends beyond the plane (edge reveal).

**Canonical margin formulas:**

Let:
- `fc = computeFrustumCenterAtDepth(cameraPosition, cameraLookAt, planePosition[2])` — the [x, y] point on the plane where the view center falls
- `vw, vh = computeFrustumRect(viewAxisDistance, fov, aspectRatio)` — visible width and height at the plane's depth
- `px, py = planePosition[0], planePosition[1]` — plane center
- `pw, ph = planeSize[0], planeSize[1]` — plane dimensions

```
left   = (fc[0] - vw/2) - (px - pw/2)
right  = (px + pw/2) - (fc[0] + vw/2)
top    = (py + ph/2) - (fc[1] + vh/2)
bottom = (fc[1] - vh/2) - (py - ph/2)
```

**Verification:** Plane at x=0, w=50, frustum center fcX=0, vw=40:
- `left = (0 - 20) - (0 - 25) = -20 + 25 = 5` — positive = safe (plane extends 5 units past frustum on left)
- `right = (0 + 25) - (0 + 20) = 25 - 20 = 5` — positive = safe

Camera shifted right by 3 (fcX=3):
- `left = (3 - 20) - (0 - 25) = -17 + 25 = 8` — more margin on left
- `right = (0 + 25) - (3 + 20) = 25 - 23 = 2` — less margin on right

### D8: Module Is Pure Math — Isomorphic, No Three.js, No Rendering Dependencies

**Decision:** Both `plane-sizing.ts` and `edge-reveal.ts` are pure TypeScript modules with no dependencies beyond OBJ-003 (spatial types/math), OBJ-005 (geometry types), and OBJ-006 (camera types). No Three.js, no Puppeteer, no Node.js-specific APIs.

**Rationale:** These functions run in Node.js (manifest validation, geometry definition) and could be bundled for the browser page (runtime sizing). Consistent with OBJ-003 D1 and OBJ-006 D12.

### D9: Default TextureSizeMode Is 'contain' — Safety Over Coverage

**Decision:** When `mode` is not specified, `computeTexturePlaneSize` defaults to `'contain'`.

**Rationale:** `contain` never produces a plane larger than the slot's defined bounds, which means it never introduces edge-reveal risk beyond what the geometry author designed for. `cover` could produce a larger plane. `stretch` distorts. The safest default is `contain`. The `suggestTextureSizeMode` function provides smarter per-slot recommendations.

### D10: computeOversizeFactor Formula

**Decision:** The analytical oversize factor accounts for three effects:

1. **Closest approach:** The camera's Z displacement reduces the distance to the plane, increasing the visible area. Worst-case distance = `baseDistance - maxDisplacementZ * speed`.
2. **Frustum center shift:** The camera's X/Y displacement shifts where the frustum falls on the plane. The plane must extend further to cover the shifted frustum.
3. **FOV variation:** If the path animates FOV, the widest FOV produces the largest visible area.

The formula:
```
baseDistance = abs(cameraStartZ - planeZ)
worstDistance = max(0.1, baseDistance - maxDisplacementZ * speed)
worstFov = oversizeReqs.fovRange[1]   // max FOV across the path
baseFov = fov parameter (default: 50 degrees) // the FOV used for initial plane sizing

frustumAtWorst = computeFrustumRect(worstDistance, worstFov, aspectRatio)
frustumAtBase = computeFrustumRect(baseDistance, baseFov, aspectRatio)

// Extra width/height needed for lateral shift of frustum center
extraWidth = 2 * (maxDisplacementX * speed + abs(offset[0]))
extraHeight = 2 * (maxDisplacementY * speed + abs(offset[1]))

requiredWidth = frustumAtWorst.visibleWidth + extraWidth
requiredHeight = frustumAtWorst.visibleHeight + extraHeight

oversizeX = requiredWidth / frustumAtBase.visibleWidth
oversizeY = requiredHeight / frustumAtBase.visibleHeight
oversizeFactor = max(1.0, oversizeX, oversizeY)
```

**`baseFov`** is the `fov` parameter to the function (default: 50 degrees). It represents the FOV at which the plane was initially sized to fit the frustum, before oversizing. The oversize factor is relative to a plane sized for `baseFov` at `baseDistance`. When the camera path animates FOV to a wider value (`worstFov > baseFov`), the oversize factor increases to compensate.

This intentionally over-estimates (the worst distance, worst FOV, and worst lateral shift may not coincide). The result is a conservative upper bound, which is exactly what geometry authors need for safe defaults.

## Acceptance Criteria

### Texture Sizing ACs

- [ ] **AC-01:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'contain')` returns `size: [50, 28.125]` — same result as OBJ-003's `computeAspectCorrectSize(1920, 1080, 50, 30)`.
- [ ] **AC-02:** `computeTexturePlaneSize(1080, 1920, 50, 30, 'contain')` returns `size: [16.875, 30]`.
- [ ] **AC-03:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'cover')` returns `size: [53.333..., 30]` (tolerance +/-0.01). Height matches slot; width exceeds to preserve 16:9 AR covering the full slot.
- [ ] **AC-04:** `computeTexturePlaneSize(1080, 1920, 50, 30, 'cover')` returns `size: [50, 88.888...]` (tolerance +/-0.01). Width matches slot; height exceeds.
- [ ] **AC-05:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'stretch')` returns `size: [50, 30]`.
- [ ] **AC-06:** `computeTexturePlaneSize` with any dimension <= 0 throws `RangeError`.
- [ ] **AC-07:** `computeTexturePlaneSize` defaults to `'contain'` when mode is omitted.
- [ ] **AC-08:** `areaCoverageRatio` for 'contain' is <= 1.0, for 'cover' is >= 1.0, and for 'stretch' is exactly 1.0.
- [ ] **AC-09:** For a texture whose aspect ratio exactly matches the slot's aspect ratio, all three modes return the same size (the slot's exact size).

### suggestTextureSizeMode ACs

- [ ] **AC-10:** A slot with `transparent: true` returns `'contain'`.
- [ ] **AC-11:** A slot with rotation matching `PLANE_ROTATIONS.FLOOR` returns `'cover'`.
- [ ] **AC-12:** A slot with `fogImmune: true` and `transparent: false` returns `'cover'`.
- [ ] **AC-13:** A facing-camera slot with `transparent: false` (or undefined) and `fogImmune: false` (or undefined) returns `'cover'`.

### Edge-Reveal Margin ACs

- [ ] **AC-14:** `computeFacingPlaneMargins` for a plane centered at [0, 0, -25] with size [50, 28], camera at [0, 0, 5] looking at [0, 0, 0], FOV 50, aspect 16/9: all four margins are positive (plane size 50x28 exceeds visible area ~49.74x27.98 at distance 30).
- [ ] **AC-15:** Same as AC-14 but with plane size [40, 28]: `left` and `right` margins are negative (width 40 < visible width ~49.74), `top` and `bottom` margins are positive.
- [ ] **AC-16:** Camera shifted right by 3 units (position [3, 0, 5]): `right` margin decreases by 3 units compared to centered camera, `left` margin increases by 3 units.
- [ ] **AC-17:** `computeFacingPlaneMargins` throws `RangeError` when the plane is behind the camera (view-axis distance <= 0).

### Edge-Reveal Validation ACs

- [ ] **AC-18:** `validateFacingPlaneEdgeReveal` for a plane that is sufficiently oversized for a static camera path returns `safe: true` and all margins positive in `worstCheck`.
- [ ] **AC-19:** `validateFacingPlaneEdgeReveal` for a plane that is too small for a push-forward path returns `safe: false` and identifies the frame (t value) where the worst edge reveal occurs (the closest approach, where the frustum is largest).
- [ ] **AC-20:** `validateFacingPlaneEdgeReveal` correctly accounts for `params.offset` — a plane that is safe without offset becomes unsafe when a large offset is applied.
- [ ] **AC-21:** `validateFacingPlaneEdgeReveal` correctly accounts for `params.speed` — at `speed: 0.5` the camera covers half the displacement, so a plane that fails at `speed: 1.0` may pass at `speed: 0.5`.
- [ ] **AC-22:** `validateGeometryEdgeReveal` marks rotated planes (floor, ceiling, walls) as `skipped: true` with a non-empty `skipReason`.
- [ ] **AC-23:** `validateGeometryEdgeReveal` only evaluates planes that have `isFacingCameraRotation(slot.rotation) === true`.
- [ ] **AC-24:** `validateGeometryEdgeReveal` populates `geometryName`, `cameraPathName`, `speed`, `offset`, `aspectRatio`, and `sampleCount` in the report.
- [ ] **AC-25:** `validateGeometryEdgeReveal` with `textureSizeOverrides` for a facing-camera slot uses the override size instead of the slot's defined size. A slot that is safe at its defined size [50, 30] but receives a smaller override [16.875, 30] (from 'contain' mode with a tall texture) correctly reports `safe: false` if the override size is too narrow.
- [ ] **AC-26:** `validateGeometryEdgeReveal` without `textureSizeOverrides` uses the geometry's slot definition sizes for all planes.

### Minimum Size and Oversize ACs

- [ ] **AC-27:** `computeMinimumFacingPlaneSize` for a static camera path (zero displacement) returns a size matching the frustum rect at the plane's depth (within tolerance +/-0.01).
- [ ] **AC-28:** `computeMinimumFacingPlaneSize` for a push-forward path returns a size larger than the frustum at the initial distance.
- [ ] **AC-29:** `computeOversizeFactor` returns exactly 1.0 for a camera path with zero displacement, zero FOV animation, and zero offset.
- [ ] **AC-30:** `computeOversizeFactor` returns > 1.0 for a camera path with non-zero Z displacement.
- [ ] **AC-31:** `computeOversizeFactor` is always >= 1.0.
- [ ] **AC-32:** (**Analytical-vs-sampling invariant**) For a push-forward camera path with non-zero Z displacement, the plane size computed as `computePlaneSize({ distanceFromCamera, fov, aspectRatio, oversizeFactor: computeOversizeFactor(...) })` is >= the size returned by `computeMinimumFacingPlaneSize(...)` in both width and height (within tolerance +/-0.1 world units). This validates that the analytical estimate is a safe upper bound of the sampling-based minimum.

### Classification ACs

- [ ] **AC-33:** `isFacingCameraRotation([0, 0, 0])` returns `true`.
- [ ] **AC-34:** `isFacingCameraRotation([-Math.PI/2, 0, 0])` (FLOOR) returns `false`.
- [ ] **AC-35:** `isFacingCameraRotation([0, Math.PI/2, 0])` (LEFT_WALL) returns `false`.
- [ ] **AC-36:** `isFacingCameraRotation([0.005, -0.003, 0.001])` (within default 0.01 tolerance) returns `true`.

### Isomorphism ACs

- [ ] **AC-37:** Both modules have zero runtime imports outside `src/spatial/`, `src/scenes/geometries/` (types only), and `src/camera/` (types only).
- [ ] **AC-38:** Neither module uses Node.js-specific APIs or browser-specific APIs.

### Behind-Camera Handling AC

- [ ] **AC-39:** `validateFacingPlaneEdgeReveal` for a camera path where the camera passes behind the plane at some sample point does NOT throw. The result is `safe: false`, and the `worstCheck` has `worstMargin === -Infinity` and `distanceToPlane <= 0`.

## Edge Cases and Error Handling

### computeTexturePlaneSize

| Scenario | Expected Behavior |
|---|---|
| Texture AR exactly matches slot AR | All three modes return slot size. `areaCoverageRatio` = 1.0. |
| Texture is 1x1 (square), slot is 50x30 | contain: [30, 30]. cover: [50, 50]. stretch: [50, 30]. |
| Very wide texture (10000x1), slot 50x30 | contain: [50, 0.005]. cover: [300000, 30]. Both mathematically valid but impractical. No clamping — upstream validation should catch extreme aspect ratios. |
| textureWidth <= 0 | Throws RangeError: `"textureWidth must be > 0, got {value}"` |
| slotWidth <= 0 | Throws RangeError: `"slotWidth must be > 0, got {value}"` |
| All dimensions equal (e.g., 100, 100, 10, 10) | All modes: [10, 10]. areaCoverageRatio = 1.0. |

### computeFacingPlaneMargins

| Scenario | Expected Behavior |
|---|---|
| Plane exactly matches frustum size | All margins approximately 0 (within float tolerance). |
| Plane centered, uniformly oversized 20% | All margins equal and positive. |
| Camera offset [5, 0, 0] from plane center | Left margin increases, right margin decreases (by 5 each). |
| Plane behind camera (distance <= 0) | Throws RangeError: `"plane is at or behind camera (view-axis distance: {value})"` |
| FOV = 0 or FOV >= 180 | Throws RangeError (propagated from computeFrustumRect). |
| Camera at same position as lookAt | `computeFrustumCenterAtDepth` returns camera's XY. `computeViewAxisDistance` returns 0 -> RangeError. |

### validateFacingPlaneEdgeReveal

| Scenario | Expected Behavior |
|---|---|
| sampleCount = 1 | Only checks t=0. Valid but inadvisable. |
| sampleCount = 0 | Throws RangeError: `"sampleCount must be >= 1"` |
| Plane becomes behind camera during path | The check at that sample has `safe: false`, `worstMargin: -Infinity`, `distanceToPlane <= 0`, and all margins `-Infinity`. The function does NOT throw. |
| Camera path with FOV animation | Margins change due to varying visible area. The worst check reflects the widest FOV moment at the closest approach. |

### validateGeometryEdgeReveal

| Scenario | Expected Behavior |
|---|---|
| Geometry with all rotated planes | All planes skipped. `safe: true` (no validated planes failed). |
| Geometry with mix of facing and rotated | Only facing planes validated. Rotated planes appear as `skipped: true`. |
| Camera path not in geometry's `compatible_cameras` | Not checked here — that's OBJ-041's responsibility. |
| `textureSizeOverrides` with a slot name not in the geometry | Override is ignored (no matching slot to apply it to). |
| `textureSizeOverrides` with a rotated plane's slot name | Override is stored but the plane is still skipped (rotation check takes priority). |

### computeMinimumFacingPlaneSize

| Scenario | Expected Behavior |
|---|---|
| Static camera (zero displacement) | Returns frustum rect size at the plane's depth. |
| Camera passes behind plane at some samples | Those samples are skipped. Size is computed from valid samples only. |
| Camera behind plane at ALL samples | Throws RangeError: `"camera is behind the plane at all sample points"` |

### computeOversizeFactor

| Scenario | Expected Behavior |
|---|---|
| `worstDistance` would be <= 0 (camera passes through the plane) | Clamped to 0.1 (near plane default). Results in very large oversize factor — signals incompatible geometry + camera combination. |
| All displacements = 0, no FOV animation | Returns 1.0 exactly. |
| `speed = 0.5` | Effective displacements halved -> smaller oversize factor. |
| Large offset `[10, 0, 0]` | Adds 20 to required width (2 * abs(10)). Large oversize factor. |
| Returned factor > 10.0 | Mathematically valid but signals impractical geometry + camera pairing. Documented in JSDoc. |

### isFacingCameraRotation

| Scenario | Expected Behavior |
|---|---|
| Exactly [0, 0, 0] | true |
| [0.009, 0, 0] (within default 0.01 tolerance) | true |
| [0.011, 0, 0] (outside tolerance) | false |
| [-Math.PI/2, 0, 0] (FLOOR) | false |
| [0, -Math.PI/2, 0] (RIGHT_WALL) | false |
| [Math.PI, 0, 0] (facing away from camera) | false |
| Custom tolerance 0.1 with rotation [0.05, 0, 0] | true |

## Test Strategy

### Unit Tests

**Texture sizing tests:**
1. Verify contain mode matches OBJ-003's `computeAspectCorrectSize` for several aspect ratio combinations (16:9 in landscape slot, 9:16 in landscape slot, square in rectangle, etc.).
2. Verify cover mode produces the inverse of contain — one dimension matches slot, the other exceeds it.
3. Verify stretch always returns slot size unchanged.
4. Verify `areaCoverageRatio` invariants: <= 1.0 for contain, >= 1.0 for cover, == 1.0 for stretch.
5. Verify equal aspect ratios produce identical results across all modes.
6. Verify all RangeError conditions.
7. Verify default mode is 'contain'.

**suggestTextureSizeMode tests:**
8. Test each heuristic branch: transparent slot -> contain, floor rotation -> cover, fogImmune -> cover, default facing-camera -> cover.
9. Verify a subject slot without `transparent: true` returns 'cover' (documents the known limitation per D3 note).

**Margin computation tests:**
10. Seed worked example: FOV=50, distance=30, aspect=16/9, plane at [0, 0, -25], camera at [0, 0, 5], plane size [50, 28] -> compute expected margins and verify all positive.
11. Camera offset [3, 0, 0] shifts margins: left increases by 3, right decreases by 3.
12. Closer plane = larger frustum = smaller margins.
13. Wider FOV = larger frustum = smaller margins.
14. Zero margins when plane exactly matches frustum size.
15. RangeError when plane is behind camera.
16. Verify `computeFrustumCenterAtDepth` for axis-aligned camera returns camera XY.
17. Verify `computeFrustumCenterAtDepth` for non-axis-aligned camera returns correct ray-plane intersection point.

**Edge-reveal validation tests:**
18. Static camera + oversized plane -> safe: true.
19. Static camera + undersized plane -> safe: false, worstCheck at t=0.
20. Push-forward camera + plane sized for start distance -> safe: false, worstCheck near t=1.
21. Push-forward camera + plane oversized for closest approach -> safe: true.
22. Lateral track + narrow plane -> safe: false, worstCheck at maximum lateral displacement.
23. Offset applied -> plane that was safe becomes unsafe.
24. Speed=0.5 -> smaller displacement -> plane that was unsafe at speed=1.0 becomes safe.
25. Camera passes behind plane at some samples -> safe: false, worstMargin: -Infinity, no throw.

**Geometry-level validation tests:**
26. Validate the seed's tunnel geometry (Section 8.6) against a mock static camera path. Facing-camera planes (end_wall) are validated; rotated planes (floor, ceiling, walls) are skipped.
27. Report includes all slot names, correct geometry/camera names, and correct sample count.
28. With `textureSizeOverrides`: a facing-camera slot that is safe at defined size becomes unsafe at a smaller override size.
29. Without `textureSizeOverrides`: uses geometry's slot definition sizes.

**Minimum size tests:**
30. Static camera -> minimum size equals frustum rect at plane depth.
31. Push-forward -> minimum size larger than initial frustum.
32. Lateral track -> minimum size wider than frustum.
33. Camera behind plane at all samples -> throws RangeError.

**Oversize factor tests:**
34. Zero-displacement path -> factor = 1.0.
35. Z-displacement only -> factor > 1.0.
36. X-displacement only -> factor > 1.0.
37. Speed=0.5 -> smaller factor than speed=1.0.
38. Offset adds to effective displacement.
39. Factor is always >= 1.0.

**Analytical-vs-sampling cross-validation test:**
40. For a push-forward path, verify that `computePlaneSize` with `computeOversizeFactor`'s result produces a plane >= `computeMinimumFacingPlaneSize`'s result in both dimensions.

**Classification tests:**
41. All PLANE_ROTATIONS constants: FACING_CAMERA -> true, all others -> false.
42. Small perturbations within tolerance -> true.
43. Small perturbations outside tolerance -> false.
44. Custom tolerance parameter works.

### Relevant Testable Claims

- **TC-04** (partial): `computeTexturePlaneSize` and `suggestTextureSizeMode` automate plane sizing from texture metadata, contributing to "no manual coordinates."
- **TC-05** (partial): Edge-reveal validation can verify that tunnel geometry planes are large enough for tunnel_push_forward.
- **TC-07** (partial): `validateGeometryEdgeReveal` feeds into manifest validation's ability to warn about edge-reveal risks.

### Contract Conformance Test Pattern

For each geometry (OBJ-018 through OBJ-025), once implemented:
1. For each compatible camera path, run `validateGeometryEdgeReveal` with default params at both 16:9 and 9:16 aspect ratios.
2. All facing-camera planes must return `safe: true`.
3. Document any planes that required size adjustments.

## Integration Points

### Depends on

| Dependency | What OBJ-040 imports |
|---|---|
| **OBJ-003** (`src/spatial/`) | `Vec3`, `Size2D`, `FrustumRect`, `PlaneTransform`, `EulerRotation` types. `computeFrustumRect`, `computeViewAxisDistance`, `computeAspectCorrectSize`, `add`, `normalize`, `subtract`, `dot`, `PLANE_ROTATIONS` constants. Core spatial math for frustum calculations. |
| **OBJ-005** (`src/scenes/geometries/`) | `PlaneSlot`, `SceneGeometry` types. Used by `validateGeometryEdgeReveal` to iterate over a geometry's slots, and by `suggestTextureSizeMode` to inspect slot metadata (`transparent`, `fogImmune`, `rotation`). Types only — no registry access needed. |
| **OBJ-006** (`src/camera/`) | `CameraPathPreset`, `CameraParams`, `CameraFrameState`, `OversizeRequirements` types. Used by validation functions to evaluate camera paths and read displacement metadata. |
| **OBJ-015** (`src/engine/`) | `TextureMetadata` type. Not directly imported — OBJ-040 accepts `textureWidth`/`textureHeight` as numbers, making it independent of OBJ-015's specific type. OBJ-015 is listed as a dependency because OBJ-040's texture sizing features were designed to consume OBJ-015's metadata. |

### Consumed by

| Downstream | How it uses OBJ-040 |
|---|---|
| **OBJ-018-025** (Geometry implementations) | Use `computeOversizeFactor` and `computeMinimumFacingPlaneSize` when defining slot sizes. Use `suggestTextureSizeMode` to document recommended sizing per slot. |
| **OBJ-039** (Page-side geometry instantiation) | Calls `computeTexturePlaneSize` with loaded texture metadata and slot size to compute final plane dimensions at render time. Uses `suggestTextureSizeMode` if no explicit mode is specified. |
| **OBJ-059-066** (Geometry visual tuning) | Run `validateGeometryEdgeReveal` during tuning to verify geometry + camera combinations. |
| **OBJ-069** (Edge-reveal tuning) | Primary consumer — uses the full validation suite. |
| **OBJ-017** (Manifest validation, optional) | Could call `validateGeometryEdgeReveal` with `textureSizeOverrides` during manifest validation. |

### File Placement

```
depthkit/
  src/
    spatial/
      index.ts             # MODIFY — add re-exports for new modules
      plane-sizing.ts      # NEW — TextureSizeMode, computeTexturePlaneSize,
                           #        suggestTextureSizeMode
      edge-reveal.ts       # NEW — PlaneMargins, EdgeRevealCheck,
                           #        PlaneEdgeRevealResult, GeometryEdgeRevealReport,
                           #        computeFrustumCenterAtDepth,
                           #        computeFacingPlaneMargins,
                           #        validateFacingPlaneEdgeReveal,
                           #        validateGeometryEdgeReveal,
                           #        computeMinimumFacingPlaneSize,
                           #        computeOversizeFactor,
                           #        isFacingCameraRotation
```

## Open Questions

### OQ-A: Should `computeTexturePlaneSize` be called at render time (browser) or validation time (Node)?

Both are viable. The current spec makes the function isomorphic so it can run in either context. **Recommendation:** OBJ-039 calls it at render time using `getTextureMetadata()` from OBJ-015. Node-side validation can call it if texture dimensions are known.

### OQ-B: Should the manifest support per-scene `size_mode` overrides?

The manifest could allow `"planes": { "backdrop": { "src": "...", "size_mode": "contain" } }`. **Recommendation:** Defer to OBJ-004 (manifest schema). OBJ-040 defines the computation; `suggestTextureSizeMode` provides a reasonable default.

### OQ-C: Should rotated plane edge-reveal validation be added in a follow-up objective?

V1 skips rotated planes. A follow-up could add viewport-corner ray casting. **Recommendation:** Track as a potential future objective. The Director Agent visual tuning workflow covers rotated planes adequately for V1.

### OQ-D: Sample distribution formula for edge cases

The sample distribution for all sampling functions is `t_i = i / (N - 1)` for `i = 0..N-1`, with the `N=1` case special-cased to `t=0`. For `N >= 2`, this includes both endpoints `t=0` and `t=1`. This is specified in the `validateFacingPlaneEdgeReveal` JSDoc. Implementers should use the same formula for `validateGeometryEdgeReveal` and `computeMinimumFacingPlaneSize`.
