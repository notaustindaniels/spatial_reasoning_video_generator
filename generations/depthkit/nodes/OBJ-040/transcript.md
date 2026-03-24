# Deliberation Transcript: OBJ-040

---

## Round 1 — spec_author

I'll start by reading the current state of OBJ-040's files and the key dependency outputs to understand what exists.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-040/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json

[Tool: Read]
  Input: {
  "file_path": "/home/user/nodes/OBJ-040/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

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
Good. Now I have all the context I need. Let me propose the full specification for OBJ-040.

---

# Proposed Specification: Plane Sizing and Edge-Reveal Prevention System (OBJ-040)

## Summary

OBJ-040 defines the plane sizing mathematics for depthkit: (1) **texture-to-plane auto-sizing** — how a plane's world-unit dimensions are computed from the loaded texture's aspect ratio and the slot's size bounds, using one of three modes (contain, cover, stretch); (2) **camera-motion-dependent oversizing** — computing the minimum plane size needed to prevent edge reveals given a camera path's displacement envelope; (3) **edge-reveal validation** — a sampling-based check that verifies no plane edge becomes visible at any point during a camera path's traversal. This is a pure spatial math module with zero rendering dependencies, extending OBJ-003's spatial library and consuming geometry definitions (OBJ-005), camera path metadata (OBJ-006), and texture metadata (OBJ-015).

## Interface Contract

### Texture-to-Plane Sizing

```typescript
// src/spatial/plane-sizing.ts

import type { Vec3, Size2D } from './types';

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
 *   If textureAR > slotAR: width exceeds slot → [slotHeight * textureAR, slotHeight]
 *   If textureAR < slotAR: height exceeds slot → [slotWidth, slotWidth / textureAR]
 *   If equal: exact fit → [slotWidth, slotHeight]
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
 * - Slots with transparent: true → 'contain' (preserve subject outline)
 * - Slots with fogImmune: true → 'cover' (sky/backdrop should fill)
 * - Slots whose rotation matches FLOOR, CEILING, LEFT_WALL, or RIGHT_WALL
 *   → 'cover' (structural planes need full coverage)
 * - All other facing-camera slots → 'cover' (backgrounds should fill)
 *
 * This is advisory — the manifest or downstream consumer can override.
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
import type { SceneGeometry } from '../scenes/geometries/types';

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
  /** Normalized time t ∈ [0, 1] at which this check was performed. */
  t: number;
  /** Camera position at this time. For diagnostics. */
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
  /** Whether ALL validated planes are safe. */
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
 * Computes where the camera's view center falls at a given Z depth,
 * for a facing-camera plane (perpendicular to the view axis).
 *
 * For a camera at position C looking at L:
 * - forward = normalize(L - C)
 * - t_intersect = (planeZ - C.z) / forward.z
 * - center = [C.x + t_intersect * forward.x, C.y + t_intersect * forward.y]
 *
 * For the common axis-aligned case (looking down -Z), this simplifies to
 * approximately [C.x, C.y] (the camera's XY position projected onto the
 * plane's Z depth). The small-angle deviation from non-axis-aligned lookAt
 * is accounted for by the full formula.
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
 * A facing-camera plane is one with rotation ≈ [0, 0, 0] — its normal
 * is approximately along the +Z axis. This function assumes the plane
 * is perpendicular to the camera's view direction and uses the
 * standard frustum rect formula for visible area computation.
 *
 * Margins are computed as:
 *   left_margin   = (planeCenter.x - planeWidth/2) - (frustumCenter.x - visibleWidth/2)
 *                 = how far the plane's left edge extends past the visible left edge
 *   right_margin  = (planeCenter.x + planeWidth/2) - (frustumCenter.x + visibleWidth/2)
 *                 = how far the plane's right edge extends past the visible right edge
 *   (similarly for top/bottom on the Y axis)
 *
 * Positive margin = the plane extends beyond the visible area on that side (safe).
 * Negative margin = the visible area extends beyond the plane on that side (edge reveal).
 *
 * @param planePosition - Plane center position [x, y, z].
 * @param planeSize - Plane dimensions [width, height] in world units.
 * @param cameraPosition - Camera position [x, y, z].
 * @param cameraLookAt - Camera lookAt target [x, y, z].
 * @param fov - Vertical FOV in degrees. Must be in (0, 180).
 * @param aspectRatio - Viewport width / height. Must be > 0.
 * @returns PlaneMargins with per-side margin values.
 * @throws RangeError if distance from camera to plane along view axis is <= 0
 *         (plane is at or behind the camera).
 * @throws RangeError if fov or aspectRatio is out of range.
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
 * @param slotName - Name of the slot (for the result report).
 * @param planePosition - Plane center position [x, y, z].
 * @param planeSize - Plane dimensions [width, height] in world units.
 * @param cameraPath - The camera path preset to evaluate.
 * @param params - Optional camera params (speed, easing, offset).
 * @param aspectRatio - Viewport width / height.
 * @param sampleCount - Number of evenly-spaced samples in [0, 1].
 *                      Default: 100. Includes t=0 and t=1.
 * @returns PlaneEdgeRevealResult with safe status and worst check.
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
 * Each plane's size is the slot's defined size (from the geometry
 * definition). If texture-adjusted sizes are needed, the caller
 * should construct a modified PlaneTransform with the adjusted size
 * and use validateFacingPlaneEdgeReveal directly.
 *
 * @param geometry - The scene geometry definition.
 * @param cameraPath - The camera path preset.
 * @param params - Optional camera params.
 * @param aspectRatio - Viewport width / height.
 * @param sampleCount - Samples per plane. Default: 100.
 * @returns GeometryEdgeRevealReport with per-plane results.
 */
export function validateGeometryEdgeReveal(
  geometry: SceneGeometry,
  cameraPath: CameraPathPreset,
  params: CameraParams | undefined,
  aspectRatio: number,
  sampleCount?: number
): GeometryEdgeRevealReport;

/**
 * Computes the minimum plane size for a facing-camera plane at a
 * given position that prevents edge reveals across an entire camera
 * path.
 *
 * Samples the camera path and computes the visible rect at the
 * plane's depth for each sample. Returns the size that encloses
 * ALL visible rects across all samples, accounting for the
 * frustum center shifting due to camera movement.
 *
 * The returned size is the tight minimum — for production use,
 * multiply by a safety margin (e.g., 1.05) to account for
 * floating-point imprecision and frame-rate-dependent interpolation.
 *
 * @param planePosition - Plane center position [x, y, z].
 *        The position determines the distance to the camera and
 *        the frustum center offset at each sample point.
 * @param cameraPath - The camera path preset.
 * @param params - Optional camera params (speed, easing, offset).
 * @param aspectRatio - Viewport width / height.
 * @param sampleCount - Samples. Default: 100.
 * @returns Size2D — the minimum [width, height] in world units.
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
 * required oversize. It computes the worst-case visible area by
 * considering:
 * - The maximum FOV in the path's fovRange
 * - The closest distance to the plane (accounting for Z displacement)
 * - The maximum lateral/vertical displacement of the frustum center
 *
 * The result is a scalar >= 1.0 that, when applied to the frustum-fit
 * plane size, ensures no edge reveals.
 *
 * This is less precise than computeMinimumFacingPlaneSize (which
 * samples the actual path) but much faster, suitable for geometry
 * definition and initial sizing.
 *
 * @param planePosition - Plane center position [x, y, z].
 * @param cameraStartPosition - Camera position at t=0.
 * @param oversizeReqs - The camera path's OversizeRequirements.
 * @param speed - The speed parameter (scales displacements). Default: 1.0.
 * @param offset - The offset parameter [x, y, z]. Default: [0, 0, 0].
 * @param fov - FOV to use for base frustum calc. If the path has FOV
 *              animation, use oversizeReqs.fovRange[1] (max). Default: 50.
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
 * tolerance of 0.01 radians (~0.57 degrees). Returns true if all
 * three rotation components are within tolerance of zero.
 *
 * Planes with rotations matching FLOOR, CEILING, LEFT_WALL, or
 * RIGHT_WALL from OBJ-003 constants return false.
 *
 * @param rotation - Euler rotation [rx, ry, rz] in radians.
 * @param tolerance - Max deviation per component. Default: 0.01.
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

**Decision:** The edge-reveal validation functions provide full margin computation and sampling-based validation for facing-camera planes (rotation ≈ [0, 0, 0]). Rotated planes (floor, ceiling, walls) are skipped with `skipped: true` and a `skipReason` string in the result.

**Rationale:** Edge-reveal math for facing-camera planes is straightforward: the frustum rect at the plane's depth vs. the plane's bounds. For rotated planes, the visible area on the plane surface is a trapezoid (perspective projection of the frustum onto an angled surface), and computing whether the trapezoid exceeds the plane's bounds requires ray-plane intersection and 2D polygon containment tests — significantly more complex. The facing-camera case covers the most critical planes in every geometry (sky, backdrop, end_wall, subject, near_fg). Rotated planes (floor, ceiling, walls) are validated through the Director Agent visual tuning workflow (OBJ-059 through OBJ-066), where edge reveals are caught visually. A future extension can add rotated plane validation using viewport-corner ray casting.

**Trade-off:** Geometry authors cannot get automated edge-reveal validation for rotated planes in V1. The `skipReason` field makes this gap explicit rather than silently ignoring it.

### D2: Three Texture Sizing Modes — Contain, Cover, Stretch

**Decision:** `TextureSizeMode` has exactly three values. `contain` fits the texture AR inside the slot bounds (OBJ-003's `computeAspectCorrectSize` logic). `cover` ensures the texture AR covers the slot bounds completely (the inverse). `stretch` keeps the slot size unchanged.

**Alternatives considered:**
- **`crop` mode (adjust UV mapping):** This is a rendering concern — changing texture repeat/offset — not a plane sizing concern. It belongs to OBJ-039 (page-side renderer), not OBJ-040. Excluded.
- **Per-axis scaling modes:** Overly complex for the use cases. The three modes cover all practical needs.

**Rationale:** The seed (Section 8.9) says "each geometry component loads its textures, reads texture dimensions, and adjusts plane sizes accordingly." The three modes provide clean, predictable sizing for the three common scenarios: preserve content (contain), ensure coverage (cover), or accept distortion (stretch).

### D3: `suggestTextureSizeMode` Uses Slot Metadata, Not Slot Name Pattern Matching

**Decision:** The mode suggestion heuristic inspects `PlaneSlot.transparent` and `PlaneSlot.fogImmune` flags and the slot's rotation, rather than matching against slot name patterns (e.g., "if name contains 'bg', use cover").

**Rationale:** Slot names are geometry-specific and may not follow predictable patterns (e.g., `end_wall` vs `backdrop` vs `sky`). The `transparent` and `fogImmune` flags are semantic indicators that reliably correlate with sizing intent: transparent planes (subjects, foreground) need contain mode to preserve their silhouette; opaque structural planes need cover mode to fill the space. This approach is robust to new geometry-specific slot names.

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

**Decision:** `PlaneMargins` values are positive when the plane extends beyond the visible area (safe) and negative when the visible area extends beyond the plane (edge reveal). The `left` margin specifically measures how far the plane's left edge extends beyond the visible area's left edge.

**Margin formulas:**
```
left   = frustumLeft - planeLeft
       = (frustumCenterX - visibleWidth/2) - (planeX - planeWidth/2)
       → positive when plane extends further left than frustum
       Wait, let me reconsider...
```

Actually, let me be very precise:
```
planeLeft     = planeX - planeWidth / 2
planeRight    = planeX + planeWidth / 2
frustumLeft   = frustumCenterX - visibleWidth / 2
frustumRight  = frustumCenterX + visibleWidth / 2

left_margin   = planeLeft - frustumLeft     (negative when plane doesn't reach)
              → but we want positive = safe

Hmm, "safe" on the left means the plane's left edge is further left than the frustum's left edge:
  planeLeft <= frustumLeft → safe
  planeLeft > frustumLeft → edge reveal on the left

left_margin = frustumLeft - planeLeft
  positive when planeLeft < frustumLeft (plane extends past) → safe
  negative when planeLeft > frustumLeft (frustum extends past) → edge reveal
```

OK let me clarify the formula in the spec:

```
left_margin   = frustumLeft - planeLeft
              = (frustumCenterX - visibleWidth/2) - (planeX - planeWidth/2)
right_margin  = planeRight - frustumRight  
              = (planeX + planeWidth/2) - (frustumCenterX + visibleWidth/2)
top_margin    = planeTop - frustumTop
              = (planeY + planeHeight/2) - (frustumCenterY + visibleHeight/2)
bottom_margin = frustumBottom - planeBottom
              = (frustumCenterY - visibleHeight/2) - (planeY - planeHeight/2)
```

Wait, this is getting confusing with the sign conventions. Let me think about it more carefully.

The plane occupies:
- X range: `[planeX - w/2, planeX + w/2]`
- Y range: `[planeY - h/2, planeY + h/2]`

The visible area occupies:
- X range: `[fcX - vw/2, fcX + vw/2]` where fc = frustum center, vw = visible width
- Y range: `[fcY - vh/2, fcY + vh/2]`

For the plane to cover the visible area, we need:
- `planeX - w/2 <= fcX - vw/2` → left side covered → margin = `(fcX - vw/2) - (planeX - w/2)` but this is negative when covered...

Let me just define margin as "how much extra plane extends beyond the frustum on each side":
```
left_margin   = (fcX - vw/2) - (planeX - w/2)
              = fcX - vw/2 - planeX + w/2
              positive means plane extends further left → safe
```

Hmm, let me verify: if planeX = 0, w = 50, fcX = 0, vw = 40:
- `left_margin = 0 - 20 - 0 + 25 = 5` → positive, 5 units of margin → correct, safe.

If planeX = 0, w = 30, fcX = 0, vw = 40:
- `left_margin = 0 - 20 - 0 + 15 = -5` → negative, 5 units of edge reveal → correct.

If camera shifts right (fcX = 3):
- `left_margin = 3 - 20 - 0 + 25 = 8` → more margin on left (camera moved away from left edge)
- `right_margin = (planeX + w/2) - (fcX + vw/2) = 0 + 25 - 3 - 20 = 2` → less margin on right

Good, that makes sense. Let me define all four:
```
left   = (fcX - vw/2) - (planeX - w/2) → inverted, this is wrong
```

Wait, I had it right. Let me re-derive from scratch.

"Left margin" = how much the plane extends beyond the frustum on the LEFT side.

The frustum's left boundary is at `fcX - vw/2`.
The plane's left boundary is at `planeX - w/2`.

The plane needs to reach at least as far left as the frustum. The margin is the distance the plane extends past the frustum's edge:

```
left_margin = (fcX - vw/2) - (planeX - w/2)
```

When planeX - w/2 < fcX - vw/2 (plane reaches further left), this is positive → safe.
When planeX - w/2 > fcX - vw/2 (frustum reaches further left), this is negative → edge reveal.

Wait no! If the plane's left edge is at x = -25 and the frustum's left edge is at x = -20, the plane reaches further left. The difference is: (-20) - (-25) = 5. That's positive. But the formula gives: `(fcX - vw/2) - (planeX - w/2) = -20 - (-25) = 5`. Yes, positive = safe. ✓

```
right_margin = (planeX + w/2) - (fcX + vw/2)
```
Plane right edge at x = 25, frustum right edge at x = 20: `25 - 20 = 5`. Positive = safe. ✓

```
top_margin = (planeY + h/2) - (fcY + vh/2)
bottom_margin = (fcY - vh/2) - (planeY - h/2)
```

OK great. Let me formalize these in the spec. I'll include them in the `computeFacingPlaneMargins` documentation.

### D8: Module Is Pure Math — Isomorphic, No Three.js, No Rendering Dependencies

**Decision:** Both `plane-sizing.ts` and `edge-reveal.ts` are pure TypeScript modules with no dependencies beyond OBJ-003 (spatial types/math), OBJ-005 (geometry types), and OBJ-006 (camera types). No Three.js, no Puppeteer, no Node.js-specific APIs.

**Rationale:** These functions run in Node.js (manifest validation, geometry definition) and could be bundled for the browser page (runtime sizing). Keeping them renderer-agnostic ensures isomorphism. Consistent with OBJ-003 D1 and OBJ-006 D12.

### D9: Default TextureSizeMode Is 'contain' — Safety Over Coverage

**Decision:** When `mode` is not specified, `computeTexturePlaneSize` defaults to `'contain'`.

**Rationale:** `contain` never produces a plane larger than the slot's defined bounds, which means it never introduces edge-reveal risk beyond what the geometry author designed for. `cover` could produce a larger plane (safe for coverage but potentially extending into adjacent geometry space). `stretch` distorts. The safest default is `contain`. The `suggestTextureSizeMode` function provides smarter per-slot recommendations.

### D10: computeOversizeFactor Formula

**Decision:** The analytical oversize factor accounts for three effects:

1. **Closest approach:** The camera's Z displacement reduces the distance to the plane, increasing the visible area. Worst-case distance = `baseDistance - maxDisplacementZ * speed`.
2. **Frustum center shift:** The camera's X/Y displacement shifts where the frustum falls on the plane. The plane must extend further to cover the shifted frustum.
3. **FOV variation:** If the path animates FOV, the widest FOV produces the largest visible area.

The formula:
```
baseDistance = abs(cameraStartZ - planeZ)
worstDistance = max(0.1, baseDistance - maxDisplacementZ * speed)
worstFov = fovRange[1]  // max FOV
frustumAtWorst = computeFrustumRect(worstDistance, worstFov, aspectRatio)
frustumAtBase = computeFrustumRect(baseDistance, baseFov, aspectRatio)

// Extra width/height needed for lateral shift
extraWidth = 2 * (maxDisplacementX * speed + abs(offset[0]))
extraHeight = 2 * (maxDisplacementY * speed + abs(offset[1]))

requiredWidth = frustumAtWorst.visibleWidth + extraWidth
requiredHeight = frustumAtWorst.visibleHeight + extraHeight

oversizeX = requiredWidth / frustumAtBase.visibleWidth
oversizeY = requiredHeight / frustumAtBase.visibleHeight
oversizeFactor = max(1.0, oversizeX, oversizeY)
```

This intentionally over-estimates (the worst distance, worst FOV, and worst lateral shift may not coincide). The result is a conservative upper bound, which is exactly what geometry authors need for safe defaults.

## Acceptance Criteria

### Texture Sizing ACs

- [ ] **AC-01:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'contain')` returns `size: [50, 28.125]` — same result as OBJ-003's `computeAspectCorrectSize(1920, 1080, 50, 30)`. The width matches the slot (width-limited), the height is proportionally smaller.
- [ ] **AC-02:** `computeTexturePlaneSize(1080, 1920, 50, 30, 'contain')` returns `size: [16.875, 30]` — height-limited.
- [ ] **AC-03:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'cover')` returns `size: [53.333..., 30]` (tolerance ±0.01). The height matches the slot; the width exceeds it to preserve the 16:9 texture aspect ratio covering the full slot.
- [ ] **AC-04:** `computeTexturePlaneSize(1080, 1920, 50, 30, 'cover')` returns `size: [50, 88.888...]` (tolerance ±0.01). The width matches the slot; the height exceeds it.
- [ ] **AC-05:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'stretch')` returns `size: [50, 30]` — slot size unchanged regardless of texture aspect ratio.
- [ ] **AC-06:** `computeTexturePlaneSize` with any dimension <= 0 throws `RangeError`.
- [ ] **AC-07:** `computeTexturePlaneSize` defaults to `'contain'` when mode is omitted.
- [ ] **AC-08:** `areaCoverageRatio` for 'contain' is <= 1.0, for 'cover' is >= 1.0, and for 'stretch' is exactly 1.0.
- [ ] **AC-09:** For a texture whose aspect ratio exactly matches the slot's aspect ratio, all three modes return the same size (the slot's exact size).

### suggestTextureSizeMode ACs

- [ ] **AC-10:** A slot with `transparent: true` returns `'contain'`.
- [ ] **AC-11:** A slot with rotation matching `PLANE_ROTATIONS.FLOOR` returns `'cover'`.
- [ ] **AC-12:** A slot with `fogImmune: true` and `transparent: false` returns `'cover'`.
- [ ] **AC-13:** A facing-camera slot with `transparent: false` and `fogImmune: false` returns `'cover'`.

### Edge-Reveal Margin ACs

- [ ] **AC-14:** `computeFacingPlaneMargins` for a plane centered at [0, 0, -25] with size [50, 28], camera at [0, 0, 5] looking at [0, 0, 0], FOV 50, aspect 16/9: all four margins are positive (plane size 50×28 exceeds visible area ~49.74×27.98 at distance 30).
- [ ] **AC-15:** Same as AC-14 but with plane size [40, 28]: `left` and `right` margins are negative (width 40 < visible width ~49.74), `top` and `bottom` margins are positive.
- [ ] **AC-16:** Camera shifted right by 3 units (position [3, 0, 5]): `right_margin` decreases by 3 units compared to centered camera, `left_margin` increases by 3 units.
- [ ] **AC-17:** `computeFacingPlaneMargins` throws `RangeError` when the plane is behind the camera (view-axis distance <= 0).

### Edge-Reveal Validation ACs

- [ ] **AC-18:** `validateFacingPlaneEdgeReveal` for a plane that is sufficiently oversized for a static camera path returns `safe: true` and all margins positive in `worstCheck`.
- [ ] **AC-19:** `validateFacingPlaneEdgeReveal` for a plane that is too small for a push-forward path returns `safe: false` and identifies the frame (t value) where the worst edge reveal occurs (the closest approach, where the frustum is largest).
- [ ] **AC-20:** `validateFacingPlaneEdgeReveal` correctly accounts for `params.offset` — a plane that is safe without offset becomes unsafe when a large offset is applied.
- [ ] **AC-21:** `validateFacingPlaneEdgeReveal` correctly accounts for `params.speed` — at `speed: 0.5` the camera covers half the displacement, so a plane that fails at `speed: 1.0` may pass at `speed: 0.5`.
- [ ] **AC-22:** `validateGeometryEdgeReveal` marks rotated planes (floor, ceiling, walls) as `skipped: true` with a non-empty `skipReason`.
- [ ] **AC-23:** `validateGeometryEdgeReveal` only evaluates planes that have `isFacingCameraRotation(slot.rotation) === true`.
- [ ] **AC-24:** `validateGeometryEdgeReveal` populates `geometryName`, `cameraPathName`, `speed`, `offset`, `aspectRatio`, and `sampleCount` in the report.

### Minimum Size and Oversize ACs

- [ ] **AC-25:** `computeMinimumFacingPlaneSize` for a static camera path (zero displacement) returns a size matching the frustum rect at the plane's depth (within tolerance ±0.01).
- [ ] **AC-26:** `computeMinimumFacingPlaneSize` for a push-forward path returns a size larger than the frustum at the initial distance, because the camera gets closer to the plane (larger frustum at the plane's depth).
- [ ] **AC-27:** `computeOversizeFactor` returns exactly 1.0 for a camera path with zero displacement, zero FOV animation, and zero offset.
- [ ] **AC-28:** `computeOversizeFactor` returns > 1.0 for a camera path with non-zero Z displacement (camera approaches the plane, enlarging the frustum).
- [ ] **AC-29:** `computeOversizeFactor` is always >= 1.0.

### Classification ACs

- [ ] **AC-30:** `isFacingCameraRotation([0, 0, 0])` returns `true`.
- [ ] **AC-31:** `isFacingCameraRotation([-Math.PI/2, 0, 0])` (FLOOR) returns `false`.
- [ ] **AC-32:** `isFacingCameraRotation([0, Math.PI/2, 0])` (LEFT_WALL) returns `false`.
- [ ] **AC-33:** `isFacingCameraRotation([0.005, -0.003, 0.001])` (small perturbation within default 0.01 tolerance) returns `true`.

### Isomorphism ACs

- [ ] **AC-34:** Both modules have zero runtime imports outside `src/spatial/`, `src/scenes/geometries/` (types only), and `src/camera/` (types only).
- [ ] **AC-35:** Neither module uses Node.js-specific APIs or browser-specific APIs.

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
| Plane exactly matches frustum size | All margins = 0 (within float tolerance). |
| Plane centered, uniformly oversized 20% | All margins equal and positive. |
| Camera offset [5, 0, 0] from plane center | Left margin increases, right margin decreases (by 5 each). |
| Plane behind camera (distance <= 0) | Throws RangeError: `"plane is at or behind camera (view-axis distance: {value})"` |
| FOV = 0 or FOV >= 180 | Throws RangeError (propagated from computeFrustumRect). |
| Camera at same position as lookAt | `computeFrustumCenterAtDepth` returns camera's XY (forward undefined). Distance = 0 → RangeError. |

### validateFacingPlaneEdgeReveal

| Scenario | Expected Behavior |
|---|---|
| sampleCount = 1 | Only checks t=0. Potentially misses edge reveals at other times. Valid but inadvisable. |
| sampleCount = 0 | Throws RangeError: `"sampleCount must be >= 1"` |
| Plane becomes behind camera during path | The check at that sample throws internally; the result for that sample reports `safe: false` with `distanceToPlane <= 0`. The overall result is `safe: false`. |
| Camera path with FOV animation | Margins change due to varying visible area. The worst check reflects the widest FOV moment at the closest approach. |

### validateGeometryEdgeReveal

| Scenario | Expected Behavior |
|---|---|
| Geometry with all rotated planes (e.g., theoretical all-floor geometry) | All planes skipped. `safe: true` (no assertion failures, no validated planes). |
| Geometry with mix of facing and rotated | Only facing planes validated. Rotated planes appear in results as `skipped: true`. |
| Camera path not in geometry's `compatible_cameras` | Not checked here — that's OBJ-041's responsibility. This function validates spatial coverage, not compatibility metadata. |
| Optional slot not populated in manifest | Not relevant — this function validates the geometry's slot DEFINITIONS, not manifest assignments. |

### computeOversizeFactor

| Scenario | Expected Behavior |
|---|---|
| `worstDistance` would be <= 0 (camera passes through the plane) | Clamped to 0.1 (the near plane default). Results in a very large oversize factor, which correctly signals that the plane cannot prevent edge reveals at this distance. |
| All displacements = 0, no FOV animation | Returns 1.0 exactly. |
| `speed = 0.5` | Effective displacements are halved → smaller oversize factor. |
| Large offset `[10, 0, 0]` | Adds 20 to required width (2 * abs(10)). Large oversize factor. |

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
8. Test each heuristic branch: transparent slot → contain, floor rotation → cover, fogImmune → cover, default facing-camera → cover.

**Margin computation tests:**
9. Seed worked example: FOV=50, distance=30, aspect=16/9, plane size [50, 28] → compute expected margins and verify.
10. Camera offset shifts margins: offset [3, 0, 0] increases left margin by 3, decreases right by 3.
11. Closer plane = larger frustum = smaller margins.
12. Wider FOV = larger frustum = smaller margins.
13. Zero margins when plane exactly matches frustum size.
14. RangeError when plane is behind camera.

**Frustum center tests:**
15. Axis-aligned camera (looking down -Z): frustum center at planeZ equals camera XY position.
16. Camera at [0, 0, 5] looking at [0, 0, 0], planeZ = -25: center at [0, 0] (camera is on-axis).
17. Camera at [3, 2, 5] looking at [0, 0, 0], planeZ = -25: center shifts according to the view direction's intersection with z = -25.

**Edge-reveal validation tests:**
18. Static camera + oversized plane → safe: true.
19. Static camera + undersized plane → safe: false, worstCheck at t=0.
20. Push-forward camera + plane sized for start distance → safe: false (plane too small at closest approach), worstCheck near t=1.
21. Push-forward camera + plane oversized for closest approach → safe: true.
22. Lateral track + narrow plane → safe: false, worstCheck at maximum lateral displacement.
23. Offset applied → plane that was safe becomes unsafe.
24. Speed=0.5 → smaller displacement → plane that was unsafe at speed=1.0 becomes safe.

**Geometry-level validation tests:**
25. Validate the seed's tunnel geometry (Section 8.6) against a mock static camera path. Facing-camera planes (end_wall) are validated; rotated planes (floor, ceiling, walls) are skipped.
26. Report includes all slot names, correct geometry/camera names, and correct sample count.

**Minimum size tests:**
27. Static camera → minimum size equals frustum rect at plane depth.
28. Push-forward → minimum size larger than initial frustum (camera gets closer).
29. Lateral track → minimum size wider than frustum (needs horizontal coverage for shifted frustum center).

**Oversize factor tests:**
30. Zero-displacement path → factor = 1.0.
31. Z-displacement only → factor > 1.0 (closer approach = larger frustum).
32. X-displacement only → factor > 1.0 (lateral coverage needed).
33. Speed=0.5 → smaller factor than speed=1.0.
34. Offset adds to effective displacement.
35. Factor is always >= 1.0.

**Classification tests:**
36. All PLANE_ROTATIONS constants: FACING_CAMERA → true, all others → false.
37. Small perturbations within tolerance → true.
38. Small perturbations outside tolerance → false.
39. Custom tolerance parameter works.

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
| **OBJ-006** (`src/camera/`) | `CameraPathPreset`, `CameraParams`, `CameraFrameState`, `OversizeRequirements` types. Used by validation functions to evaluate camera paths and read displacement metadata. `resolveCameraParams` called internally to resolve speed/easing. |
| **OBJ-015** (`src/engine/`) | `TextureMetadata` type. Not directly imported — OBJ-040 accepts `textureWidth`/`textureHeight` as numbers, making it independent of OBJ-015's specific type. OBJ-015 is listed as a dependency because OBJ-040's texture sizing features were designed to consume OBJ-015's metadata. |

### Consumed by

| Downstream | How it uses OBJ-040 |
|---|---|
| **OBJ-018–025** (Geometry implementations) | Use `computeOversizeFactor` and `computeMinimumFacingPlaneSize` when defining slot sizes to ensure they are large enough for all compatible camera paths. Use `suggestTextureSizeMode` to document recommended sizing per slot. |
| **OBJ-039** (Page-side geometry instantiation) | Calls `computeTexturePlaneSize` with loaded texture metadata and slot size to compute final plane dimensions at render time. Uses `suggestTextureSizeMode` if no explicit mode is specified. |
| **OBJ-059–066** (Geometry visual tuning) | Run `validateGeometryEdgeReveal` during tuning to verify that geometry + camera combinations have no edge reveals on facing-camera planes. |
| **OBJ-069** (Edge-reveal tuning) | Primary consumer — uses the full validation suite to systematically verify and tune all geometry + camera combinations. |
| **OBJ-017** (Manifest validation, optional) | Could call `validateGeometryEdgeReveal` during manifest validation to warn about edge-reveal risks. This is optional — manifest validation may choose to rely on geometry definitions being pre-validated. |

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

Both are viable. At render time (OBJ-039 in the browser), texture metadata is available from OBJ-015. At validation time (Node side), texture metadata would need to be communicated back from the page. The current spec makes the function isomorphic so it can run in either context. **Recommendation:** OBJ-039 calls it at render time using `getTextureMetadata()` from OBJ-015. Node-side validation can call it if texture dimensions are known (e.g., from a pre-scan step).

### OQ-B: Should the manifest support per-scene `size_mode` overrides?

The manifest could allow `"planes": { "backdrop": { "src": "...", "size_mode": "contain" } }`. This would let the LLM author control sizing per plane. **Recommendation:** Defer to OBJ-004 (manifest schema) or a follow-up. OBJ-040 defines the computation; how the mode is specified in the manifest is a schema concern. `suggestTextureSizeMode` provides a reasonable default when no override is given.

### OQ-C: Should rotated plane edge-reveal validation be added in a follow-up objective?

V1 skips rotated planes. A follow-up could add viewport-corner ray casting to validate floor/ceiling/wall planes analytically. **Recommendation:** Track as a potential future objective. The Director Agent visual tuning workflow covers rotated planes adequately for V1. If a pattern of rotated-plane edge reveals emerges during tuning, escalate to a new objective.

### OQ-D: Should `computeMinimumFacingPlaneSize` account for the plane's XY position?

Currently it does — the plane position determines the frustum center offset at each sample. But if the plane is not centered at [0, 0, z], the frustum may fall more to one side, requiring asymmetric sizing. The current function returns a symmetric size centered at the plane position. If the plane is significantly off-center from the camera's average lookAt, the minimum size may be larger than necessary in one direction. **Recommendation:** The current symmetric approach is correct — it computes the bounding box of all frustum projections centered on the plane. No change needed.

---

I believe this covers all four parts of OBJ-040's description: visible area calculation, camera-motion-dependent oversizing, edge-reveal prevention math, and texture-to-plane auto-sizing. I've kept the scope pragmatic (facing-camera planes for V1, documented skip for rotated planes) while providing both fast analytical estimates (`computeOversizeFactor`) and precise sampling-based validation (`validateFacingPlaneEdgeReveal`).

I'd like the Challenger to review this proposal and identify any gaps, ambiguities, or issues.

---

## Round 2 — spec_challenger

I've read the proposal carefully. It's a solid foundation — the two-tier approach (analytical `computeOversizeFactor` for geometry definition time, sampling-based `validateFacingPlaneEdgeReveal` for validation time) is well-reasoned, and the texture sizing modes are practical. But I have several issues that need addressing before this is implementable.

---

## Issues

### Issue 1: `computeFacingPlaneMargins` margin formulas are documented incorrectly in D7 (Major)

D7 walks through the margin derivation but the final formulas have a sign error in the left margin. You write:

```
left_margin = (fcX - vw/2) - (planeX - w/2)
```

Let's verify: plane at x=0, w=50, frustum center fcX=0, vw=40.
- `planeLeft = 0 - 25 = -25`
- `frustumLeft = 0 - 20 = -20`
- The plane's left edge (-25) extends 5 units past the frustum's left edge (-20). That's safe. margin should be +5.
- Formula: `(0 - 20) - (0 - 25) = -20 + 25 = 5` ✓

OK that actually works. But the *prose* in the function's JSDoc says:

> `left_margin = frustumLeft - planeLeft` → "positive when plane extends further left than frustum"

That's `(-20) - (-25) = 5`. Same result. But in the JSDoc for `computeFacingPlaneMargins`, you wrote a *different* description:

> ```
> left_margin   = (planeCenter.x - planeWidth/2) - (frustumCenter.x - visibleWidth/2)
>               = how far the plane's left edge extends past the visible left edge
> ```

That gives `(0 - 25) - (0 - 20) = -25 + 20 = -5`. **This is the negation of the intended value.** The JSDoc formula contradicts the D7 formula.

**Proposed fix:** Remove the inline formula from `computeFacingPlaneMargins`'s JSDoc (it's the wrong one). Instead, reference D7 for the canonical formulas, or replace the JSDoc with the correct formulas from D7. The canonical formulas should be:

```
left   = (frustumCenterX - visibleWidth/2) - (planeX - planeWidth/2)
right  = (planeX + planeWidth/2) - (frustumCenterX + visibleWidth/2)
top    = (planeY + planeHeight/2) - (frustumCenterY + visibleHeight/2)
bottom = (frustumCenterY - visibleHeight/2) - (planeY - planeHeight/2)
```

All positive = safe. Verify with a test case in AC-14.

---

### Issue 2: `computeFrustumCenterAtDepth` uses `planeZ` as a raw Z coordinate, but facing-camera planes aren't always at fixed Z (Major)

The function signature is:
```typescript
computeFrustumCenterAtDepth(cameraPosition: Vec3, cameraLookAt: Vec3, planeZ: number): [number, number]
```

This takes a scalar `planeZ` and computes the ray-plane intersection at z = planeZ. But `computeFacingPlaneMargins` takes a full `planePosition: Vec3`. Inside, it would need to call `computeFrustumCenterAtDepth` with `planePosition[2]` as the planeZ.

The problem: for a non-axis-aligned camera (camera at [0, 5, 5] looking at [0, 0, -10]), the "plane at z = -25" assumption means you're intersecting the view ray with the plane z = -25. But the visible area calculation (`computeFrustumRect`) needs the *distance along the view axis*, not the Z coordinate. These are different for non-axis-aligned cameras.

Your `computeFrustumCenterAtDepth` computes the ray intersection correctly for an arbitrary camera direction, which is good. But then `computeFacingPlaneMargins` needs to use `computeViewAxisDistance` (from OBJ-003) to get the correct distance for the frustum rect calculation, and `computeFrustumCenterAtDepth` for the center point. These are consistent only if the facing-camera plane is actually perpendicular to the camera's forward direction — which is the `isFacingCameraRotation` assumption.

This is subtly correct but the spec doesn't explicitly state the assumption chain. An implementer might compute the frustum center and the frustum rect using different distance measures and get wrong results.

**Proposed fix:** Add to `computeFacingPlaneMargins`'s description: "Internally, uses `computeViewAxisDistance` from OBJ-003 to determine the perpendicular distance from the camera to the plane for frustum rect calculation, and `computeFrustumCenterAtDepth` to determine where the view center falls on the plane. Both are consistent because the function's prerequisite is that the plane faces the camera (perpendicular to the view axis)."

---

### Issue 3: `suggestTextureSizeMode` returns 'cover' for ALL non-transparent facing-camera slots — including `subject` when transparent is unset (Minor)

The heuristic as written:
1. `transparent: true` → 'contain'
2. `fogImmune: true` → 'cover'
3. rotation matches floor/ceiling/wall → 'cover'
4. **All other facing-camera slots → 'cover'**

A `subject` slot that doesn't have `transparent: true` explicitly set (maybe a geometry author forgot) would get 'cover', which means the subject plane could extend beyond its intended spatial allocation. The seed says subjects "almost always need transparency" (Section 4.7), but the slot definition might not always have `transparent: true`.

However, the function is documented as advisory, and the heuristic's logic is internally consistent with its documented rules. The real fix is for geometry authors to mark `transparent: true` on subject slots, which OBJ-005's conventions already encourage.

**Proposed fix:** Minor — add a note in the function's JSDoc: "This heuristic depends on the geometry author correctly setting `transparent: true` on subject/foreground slots. If a subject slot lacks `transparent: true`, this function returns 'cover', which may not be the intended behavior. See OBJ-005 slot naming conventions."

---

### Issue 4: No acceptance criterion verifies `computeOversizeFactor`'s formula against `computeMinimumFacingPlaneSize` (Major)

You have two methods for computing oversizing: the fast analytical `computeOversizeFactor` and the precise sampling-based `computeMinimumFacingPlaneSize`. The spec says `computeOversizeFactor` is a "conservative upper bound." But there's no AC that verifies this invariant — that for any given configuration, `computeOversizeFactor` produces a factor that, when applied to the base frustum-fit size, yields a plane at least as large as `computeMinimumFacingPlaneSize` returns.

If this invariant is violated, geometry authors who rely on `computeOversizeFactor` to size their slots would have edge reveals that only show up during sampling validation.

**Proposed fix:** Add an acceptance criterion:

> **AC-36:** For a push-forward camera path (non-zero Z displacement), the plane size computed as `computePlaneSize({ distanceFromCamera, fov, aspectRatio, oversizeFactor: computeOversizeFactor(...) })` is >= the size returned by `computeMinimumFacingPlaneSize(...)` in both width and height (within tolerance ±0.01). This validates that the analytical estimate is a safe upper bound of the sampling-based minimum.

---

### Issue 5: `computeOversizeFactor` formula in D10 uses `baseFov` but doesn't define it (Minor)

The formula references `baseFov` in `frustumAtBase = computeFrustumRect(baseDistance, baseFov, aspectRatio)` but the function signature uses `fov` as the parameter. And the formula says to use `fovRange[1]` for `worstFov`, but what FOV is used for the "base" frustum? Is it `fov` (the parameter, default 50), or `fovRange[0]`, or the camera path's start FOV?

**Proposed fix:** Clarify in D10: "baseFov = the `fov` parameter (default: 50°). This represents the FOV used for initial plane sizing (before oversizing). The oversize factor is relative to a plane sized for this FOV at the base distance."

---

### Issue 6: `computeFrustumCenterAtDepth` return type is `readonly [number, number]` but other spatial types use `Vec3` (Minor)

It returns a 2D point `[x, y]` since Z is the input. This is fine semantically but introduces a new tuple type that doesn't exist in OBJ-003's type vocabulary. Downstream consumers need to reconstruct a Vec3 by combining this with planeZ.

**Proposed fix:** This is acceptable as-is — a 2D coordinate on a plane surface is genuinely a different type than a 3D position. But add a brief note: "Returns a 2-component [x, y] tuple representing the point on the plane, not a Vec3. The Z coordinate is the input `planeZ`."

---

### Issue 7: `validateGeometryEdgeReveal` doesn't account for texture-adjusted sizes (Major)

The function description says: "Each plane's size is the slot's defined size (from the geometry definition). If texture-adjusted sizes are needed, the caller should construct a modified PlaneTransform with the adjusted size and use `validateFacingPlaneEdgeReveal` directly."

This means the geometry-level validation function always uses the *slot definition size*, not the *actual rendered size* (which could be smaller in 'contain' mode). A slot sized at [50, 30] that gets a tall texture in 'contain' mode might render as [16.875, 30] — much narrower, potentially revealing edges.

The spec acknowledges this by telling callers to use the per-plane function directly, but `validateGeometryEdgeReveal` is the primary function downstream consumers (OBJ-059-066, OBJ-069) will call. If it gives false "safe" results because it uses slot sizes instead of rendered sizes, it's misleading.

**Proposed fix:** Either:
(a) Add an optional parameter `textureSizeOverrides?: Record<string, Size2D>` to `validateGeometryEdgeReveal` that replaces slot sizes with actual rendered sizes when provided. OR
(b) Add a prominent warning in the function doc AND add an acceptance criterion that documents this limitation explicitly, so downstream consumers know they must use per-plane validation for texture-adjusted sizing.

I lean toward (a) — it's a small addition that makes the primary API correct by default when texture metadata is available.

---

### Issue 8: Missing import in `suggestTextureSizeMode` signature — needs `PlaneSlot` type (Minor)

The function signature references `PlaneSlot` but the import block at the top of `plane-sizing.ts` only shows:
```typescript
import type { Vec3, Size2D } from './types';
```

It would also need `import type { PlaneSlot } from '../scenes/geometries/types'`.

**Proposed fix:** Add the import to the file's documented imports, or note that `plane-sizing.ts` imports from both `./types` (OBJ-003) and `../scenes/geometries/types` (OBJ-005).

---

### Issue 9: `computeFacingPlaneMargins` should use `computeFrustumCenterAtDepth` internally, but this isn't stated (Minor)

The spec defines both functions but doesn't explicitly state that `computeFacingPlaneMargins` calls `computeFrustumCenterAtDepth` internally. An implementer might compute the frustum center differently and get subtly wrong results for non-axis-aligned cameras.

**Proposed fix:** Add to `computeFacingPlaneMargins` JSDoc: "Internally calls `computeFrustumCenterAtDepth` to determine the frustum center on the plane, and `computeViewAxisDistance` (from OBJ-003) to determine the distance for frustum rect computation."

---

### Issue 10: The spec doesn't address what happens when `computeOversizeFactor` returns a very large value (e.g., >10) (Minor)

If the camera passes very close to a plane (e.g., near-plane distance approaches 0.1), the oversize factor could be enormous (e.g., 50x). This is mathematically correct but practically useless — it means the geometry + camera combination is fundamentally incompatible (you can't size a texture plane large enough to cover the view at near-zero distance).

**Proposed fix:** Add to the function's JSDoc: "If the returned factor exceeds a practical threshold (e.g., > 10.0), this indicates the plane is too close to the camera's path for effective edge-reveal prevention. The geometry author should increase the plane's Z-distance from the camera's closest approach, or exclude this camera path from the geometry's `compatible_cameras`." Not a code change — just documentation for geometry authors.

---

## What's Sound

- The two-tier approach (fast analytical + precise sampling) is architecturally clean.
- The `TextureSizeMode` trio (contain/cover/stretch) is pragmatic and covers real needs.
- Skipping rotated planes with explicit `skipped: true` + `skipReason` is honest about the V1 limitation.
- The `PlaneMargins` / `EdgeRevealCheck` / `PlaneEdgeRevealResult` / `GeometryEdgeRevealReport` hierarchy provides good diagnostic detail for tuning sessions.
- `isFacingCameraRotation` with a tolerance parameter is sensible.
- File placement in `src/spatial/` is correct — this is pure math, not rendering.
- The dependency analysis is thorough and accurate.
- The test strategy is comprehensive and the ACs are mostly testable.

---

## Summary of Required Changes

| # | Severity | Summary |
|---|---|---|
| 1 | Major | Fix contradictory margin formula in `computeFacingPlaneMargins` JSDoc |
| 2 | Major | Document the consistency assumption between `computeFrustumCenterAtDepth` and `computeViewAxisDistance` |
| 4 | Major | Add AC verifying analytical oversize factor is >= sampling-based minimum |
| 7 | Major | Add `textureSizeOverrides` param to `validateGeometryEdgeReveal` or explicitly document/AC the limitation |
| 3 | Minor | Note `suggestTextureSizeMode` dependency on geometry author setting `transparent` correctly |
| 5 | Minor | Define `baseFov` in D10 formula |
| 6 | Minor | Clarify `computeFrustumCenterAtDepth` return type note |
| 8 | Minor | Add missing `PlaneSlot` import |
| 9 | Minor | State `computeFacingPlaneMargins` internal delegation |
| 10 | Minor | Document behavior when oversize factor is impractically large |

Please address the 4 major issues and as many minors as practical, then present the revised spec.

---

## Round 3 — spec_author

All ten issues are valid. Here's the revised specification addressing every one.

---

# Revised Specification: Plane Sizing and Edge-Reveal Prevention System (OBJ-040)

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
 *   If textureAR > slotAR: height matches slot → [slotHeight * textureAR, slotHeight]
 *   If textureAR < slotAR: width matches slot → [slotWidth, slotWidth / textureAR]
 *   If equal: exact fit → [slotWidth, slotHeight]
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
 * - Slots with transparent: true → 'contain' (preserve subject outline)
 * - Slots with fogImmune: true → 'cover' (sky/backdrop should fill)
 * - Slots whose rotation matches FLOOR, CEILING, LEFT_WALL, or RIGHT_WALL
 *   → 'cover' (structural planes need full coverage)
 * - All other facing-camera slots → 'cover' (backgrounds should fill)
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
  /** Normalized time t ∈ [0, 1] at which this check was performed. */
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
 * A facing-camera plane is one with rotation ≈ [0, 0, 0] — its normal
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
 *   Let fc = frustumCenter from computeFrustumCenterAtDepth
 *   Let vw, vh = visibleWidth, visibleHeight from computeFrustumRect
 *   Let px, py = planePosition[0], planePosition[1]
 *   Let pw, ph = planeSize[0], planeSize[1]
 *
 *   left   = (fc[0] - vw/2) - (px - pw/2)
 *          → positive when plane's left edge extends past frustum's left edge
 *   right  = (px + pw/2) - (fc[0] + vw/2)
 *          → positive when plane's right edge extends past frustum's right edge
 *   top    = (py + ph/2) - (fc[1] + vh/2)
 *          → positive when plane's top edge extends past frustum's top edge
 *   bottom = (fc[1] - vh/2) - (py - ph/2)
 *          → positive when plane's bottom edge extends past frustum's bottom edge
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
 * sampling-based validation). See AC-36.
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

**Decision:** The edge-reveal validation functions provide full margin computation and sampling-based validation for facing-camera planes (rotation ≈ [0, 0, 0]). Rotated planes (floor, ceiling, walls) are skipped with `skipped: true` and a `skipReason` string in the result.

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
- `left = (0 - 20) - (0 - 25) = -20 + 25 = 5` ✓ positive = safe (plane extends 5 units past frustum on left)
- `right = (0 + 25) - (0 + 20) = 25 - 20 = 5` ✓ positive = safe

Camera shifted right by 3 (fcX=3):
- `left = (3 - 20) - (0 - 25) = -17 + 25 = 8` ✓ more margin on left
- `right = (0 + 25) - (3 + 20) = 25 - 23 = 2` ✓ less margin on right

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
baseFov = fov parameter (default: 50°) // the FOV used for initial plane sizing

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

**`baseFov`** is the `fov` parameter to the function (default: 50°). It represents the FOV at which the plane was initially sized to fit the frustum, before oversizing. The oversize factor is relative to a plane sized for `baseFov` at `baseDistance`. When the camera path animates FOV to a wider value (`worstFov > baseFov`), the oversize factor increases to compensate.

This intentionally over-estimates (the worst distance, worst FOV, and worst lateral shift may not coincide). The result is a conservative upper bound, which is exactly what geometry authors need for safe defaults.

## Acceptance Criteria

### Texture Sizing ACs

- [ ] **AC-01:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'contain')` returns `size: [50, 28.125]` — same result as OBJ-003's `computeAspectCorrectSize(1920, 1080, 50, 30)`.
- [ ] **AC-02:** `computeTexturePlaneSize(1080, 1920, 50, 30, 'contain')` returns `size: [16.875, 30]`.
- [ ] **AC-03:** `computeTexturePlaneSize(1920, 1080, 50, 30, 'cover')` returns `size: [53.333..., 30]` (tolerance ±0.01). Height matches slot; width exceeds to preserve 16:9 AR covering the full slot.
- [ ] **AC-04:** `computeTexturePlaneSize(1080, 1920, 50, 30, 'cover')` returns `size: [50, 88.888...]` (tolerance ±0.01). Width matches slot; height exceeds.
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

- [ ] **AC-14:** `computeFacingPlaneMargins` for a plane centered at [0, 0, -25] with size [50, 28], camera at [0, 0, 5] looking at [0, 0, 0], FOV 50, aspect 16/9: all four margins are positive (plane size 50×28 exceeds visible area ~49.74×27.98 at distance 30).
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

- [ ] **AC-27:** `computeMinimumFacingPlaneSize` for a static camera path (zero displacement) returns a size matching the frustum rect at the plane's depth (within tolerance ±0.01).
- [ ] **AC-28:** `computeMinimumFacingPlaneSize` for a push-forward path returns a size larger than the frustum at the initial distance.
- [ ] **AC-29:** `computeOversizeFactor` returns exactly 1.0 for a camera path with zero displacement, zero FOV animation, and zero offset.
- [ ] **AC-30:** `computeOversizeFactor` returns > 1.0 for a camera path with non-zero Z displacement.
- [ ] **AC-31:** `computeOversizeFactor` is always >= 1.0.
- [ ] **AC-32:** (**Analytical-vs-sampling invariant**) For a push-forward camera path with non-zero Z displacement, the plane size computed as `computePlaneSize({ distanceFromCamera, fov, aspectRatio, oversizeFactor: computeOversizeFactor(...) })` is >= the size returned by `computeMinimumFacingPlaneSize(...)` in both width and height (within tolerance ±0.1 world units). This validates that the analytical estimate is a safe upper bound of the sampling-based minimum.

### Classification ACs

- [ ] **AC-33:** `isFacingCameraRotation([0, 0, 0])` returns `true`.
- [ ] **AC-34:** `isFacingCameraRotation([-Math.PI/2, 0, 0])` (FLOOR) returns `false`.
- [ ] **AC-35:** `isFacingCameraRotation([0, Math.PI/2, 0])` (LEFT_WALL) returns `false`.
- [ ] **AC-36:** `isFacingCameraRotation([0.005, -0.003, 0.001])` (within default 0.01 tolerance) returns `true`.

### Isomorphism ACs

- [ ] **AC-37:** Both modules have zero runtime imports outside `src/spatial/`, `src/scenes/geometries/` (types only), and `src/camera/` (types only).
- [ ] **AC-38:** Neither module uses Node.js-specific APIs or browser-specific APIs.

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
| Plane exactly matches frustum size | All margins ≈ 0 (within float tolerance). |
| Plane centered, uniformly oversized 20% | All margins equal and positive. |
| Camera offset [5, 0, 0] from plane center | Left margin increases, right margin decreases (by 5 each). |
| Plane behind camera (distance <= 0) | Throws RangeError: `"plane is at or behind camera (view-axis distance: {value})"` |
| FOV = 0 or FOV >= 180 | Throws RangeError (propagated from computeFrustumRect). |
| Camera at same position as lookAt | `computeFrustumCenterAtDepth` returns camera's XY. `computeViewAxisDistance` returns 0 → RangeError. |

### validateFacingPlaneEdgeReveal

| Scenario | Expected Behavior |
|---|---|
| sampleCount = 1 | Only checks t=0. Valid but inadvisable. |
| sampleCount = 0 | Throws RangeError: `"sampleCount must be >= 1"` |
| Plane becomes behind camera during path | The check at that sample has `distanceToPlane <= 0`. The result reports `safe: false` with negative `worstMargin`. |
| Camera path with FOV animation | Margins change due to varying visible area. The worst check reflects the widest FOV moment at the closest approach. |

### validateGeometryEdgeReveal

| Scenario | Expected Behavior |
|---|---|
| Geometry with all rotated planes | All planes skipped. `safe: true` (no validated planes failed). |
| Geometry with mix of facing and rotated | Only facing planes validated. Rotated planes appear as `skipped: true`. |
| Camera path not in geometry's `compatible_cameras` | Not checked here — that's OBJ-041's responsibility. |
| `textureSizeOverrides` with a slot name not in the geometry | Override is ignored (no matching slot to apply it to). |
| `textureSizeOverrides` with a rotated plane's slot name | Override is stored but the plane is still skipped (rotation check takes priority). |

### computeOversizeFactor

| Scenario | Expected Behavior |
|---|---|
| `worstDistance` would be <= 0 (camera passes through the plane) | Clamped to 0.1 (near plane default). Results in very large oversize factor — signals incompatible geometry + camera combination. |
| All displacements = 0, no FOV animation | Returns 1.0 exactly. |
| `speed = 0.5` | Effective displacements halved → smaller oversize factor. |
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
8. Test each heuristic branch: transparent slot → contain, floor rotation → cover, fogImmune → cover, default facing-camera → cover.
9. Verify a subject slot without `transparent: true` returns 'cover' (documents the known limitation).

**Margin computation tests:**
10. Seed worked example: FOV=50, distance=30, aspect=16/9, plane at [0, 0, -25], camera at [0, 0, 5], plane size [50, 28] → compute expected margins and verify all positive.
11. Camera offset [3, 0, 0] shifts margins: left increases by 3, right decreases by 3.
12. Closer plane = larger frustum = smaller margins.
13. Wider FOV = larger frustum = smaller margins.
14. Zero margins when plane exactly matches frustum size.
15. RangeError when plane is behind camera.
16. Verify `computeFrustumCenterAtDepth` for axis-aligned camera returns camera XY.
17. Verify `computeFrustumCenterAtDepth` for non-axis-aligned camera returns correct ray-plane intersection point.

**Edge-reveal validation tests:**
18. Static camera + oversized plane → safe: true.
19. Static camera + undersized plane → safe: false, worstCheck at t=0.
20. Push-forward camera + plane sized for start distance → safe: false, worstCheck near t=1.
21. Push-forward camera + plane oversized for closest approach → safe: true.
22. Lateral track + narrow plane → safe: false, worstCheck at maximum lateral displacement.
23. Offset applied → plane that was safe becomes unsafe.
24. Speed=0.5 → smaller displacement → plane that was unsafe at speed=1.0 becomes safe.

**Geometry-level validation tests:**
25. Validate the seed's tunnel geometry (Section 8.6) against a mock static camera path. Facing-camera planes (end_wall) are validated; rotated planes (floor, ceiling, walls) are skipped.
26. Report includes all slot names, correct geometry/camera names, and correct sample count.
27. With `textureSizeOverrides`: a facing-camera slot that is safe at defined size becomes unsafe at a smaller override size.
28. Without `textureSizeOverrides`: uses geometry's slot definition sizes.

**Minimum size tests:**
29. Static camera → minimum size equals frustum rect at plane depth.
30. Push-forward → minimum size larger than initial frustum.
31. Lateral track → minimum size wider than frustum.

**Oversize factor tests:**
32. Zero-displacement path → factor = 1.0.
33. Z-displacement only → factor > 1.0.
34. X-displacement only → factor > 1.0.
35. Speed=0.5 → smaller factor than speed=1.0.
36. Offset adds to effective displacement.
37. Factor is always >= 1.0.

**Analytical-vs-sampling cross-validation test:**
38. For a push-forward path, verify that `computePlaneSize` with `computeOversizeFactor`'s result produces a plane >= `computeMinimumFacingPlaneSize`'s result in both dimensions.

**Classification tests:**
39. All PLANE_ROTATIONS constants: FACING_CAMERA → true, all others → false.
40. Small perturbations within tolerance → true.
41. Small perturbations outside tolerance → false.
42. Custom tolerance parameter works.

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
| **OBJ-018–025** (Geometry implementations) | Use `computeOversizeFactor` and `computeMinimumFacingPlaneSize` when defining slot sizes. Use `suggestTextureSizeMode` to document recommended sizing per slot. |
| **OBJ-039** (Page-side geometry instantiation) | Calls `computeTexturePlaneSize` with loaded texture metadata and slot size to compute final plane dimensions at render time. Uses `suggestTextureSizeMode` if no explicit mode is specified. |
| **OBJ-059–066** (Geometry visual tuning) | Run `validateGeometryEdgeReveal` during tuning to verify geometry + camera combinations. |
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

### OQ-D: Should `computeMinimumFacingPlaneSize` account for the plane's XY position?

It does — the plane position determines the frustum center offset at each sample. The current symmetric approach computes the bounding box of all frustum projections at the plane's depth, which is correct regardless of the plane's XY offset. No change needed.

---

## Changelog from Round 1

| Issue | Resolution |
|---|---|
| **#1 (Major):** Contradictory margin formula in JSDoc | Removed incorrect inline formulas from `computeFacingPlaneMargins` JSDoc. Replaced with the correct canonical formulas from D7, with full derivation and verification example. |
| **#2 (Major):** Undocumented consistency assumption | Added explicit statement to `computeFacingPlaneMargins` JSDoc: "Internally calls `computeFrustumCenterAtDepth` to determine the frustum center on the plane, and `computeViewAxisDistance` (from OBJ-003) to determine the distance for frustum rect computation. Both are consistent because the function's prerequisite is that the plane faces the camera (perpendicular to the view axis)." |
| **#4 (Major):** Missing AC for analytical-vs-sampling invariant | Added **AC-32**: verifies `computeOversizeFactor` produces a plane >= `computeMinimumFacingPlaneSize` in both dimensions. |
| **#7 (Major):** `validateGeometryEdgeReveal` doesn't account for texture-adjusted sizes | Added `textureSizeOverrides?: Record<string, Size2D>` parameter. Added **AC-25** and **AC-26** testing with and without overrides. Added prominent JSDoc warning about slot sizes vs rendered sizes. |
| **#3 (Minor):** suggestTextureSizeMode dependency on transparent | Added NOTE in JSDoc documenting the dependency. Added test case #9 for a subject slot without transparent. |
| **#5 (Minor):** `baseFov` undefined in D10 | Clarified in D10: "`baseFov` is the `fov` parameter to the function (default: 50°)." Also clarified in `computeOversizeFactor` JSDoc. |
| **#6 (Minor):** Return type note | Added to `computeFrustumCenterAtDepth` JSDoc: "Returns a 2-component [x, y] tuple representing the point on the plane, not a Vec3. The Z coordinate is the input `planeZ`." |
| **#8 (Minor):** Missing PlaneSlot import | Added `import type { PlaneSlot } from '../scenes/geometries/types'` to `plane-sizing.ts` imports. |
| **#9 (Minor):** Internal delegation not stated | Added to `computeFacingPlaneMargins` JSDoc: explicit statement that it calls `computeFrustumCenterAtDepth` and `computeViewAxisDistance` internally. |
| **#10 (Minor):** Large oversize factor behavior | Added to `computeOversizeFactor` JSDoc: guidance that factors > 10.0 indicate impractical pairings. |

---

I believe all 10 issues have been addressed. I'd like the Challenger to verify and approve.

---

## Round 4 — spec_challenger

I've verified all 10 issues from Round 2 against the revised spec. Every one is structurally addressed in the revision. Good work. I have one remaining issue that needs fixing before I can converge.

---

## Remaining Issue

### Issue 11: `validateFacingPlaneEdgeReveal` doesn't specify how it handles the RangeError from `computeFacingPlaneMargins` when a plane is behind/at the camera during the path (Major)

The edge case table says:

> | Plane becomes behind camera during path | The check at that sample has `distanceToPlane <= 0`. The result reports `safe: false` with negative `worstMargin`. |

But `computeFacingPlaneMargins` *throws* a `RangeError` when `view-axis distance <= 0`. So `validateFacingPlaneEdgeReveal` must catch that error (or preemptively check distance) to produce the documented behavior. The function contract doesn't mention this.

An implementer could reasonably:
- (a) Let the RangeError propagate — crashing validation for any camera path that passes through or behind a plane.
- (b) Catch the RangeError and produce a synthetic failed `EdgeRevealCheck`.
- (c) Check distance before calling `computeFacingPlaneMargins` and produce the failed check directly.

Options (b) and (c) match the edge case table; option (a) contradicts it. This is a real ambiguity that would force the implementer to guess.

**Proposed fix:** Add to `validateFacingPlaneEdgeReveal`'s JSDoc:

> If the view-axis distance from the camera to the plane is <= 0 at any sample point (the plane is at or behind the camera), that sample produces an `EdgeRevealCheck` with `safe: false`, `worstMargin: -Infinity`, `distanceToPlane` set to the actual (non-positive) distance, and margins of `{ left: -Infinity, right: -Infinity, top: -Infinity, bottom: -Infinity }`. The function does not throw for this condition — it is reported as a maximally-failed check in the result.

Also add an AC:

> **AC-XX:** `validateFacingPlaneEdgeReveal` for a camera path where the camera passes behind the plane at some sample point does NOT throw. The result is `safe: false`, and the `worstCheck` has `worstMargin === -Infinity` and `distanceToPlane <= 0`.

---

## Verification Summary

| Issue # | Status | Verification |
|---------|--------|--------------|
| 1 (Major) | ✅ Fixed | Correct formulas now in JSDoc with verification example |
| 2 (Major) | ✅ Fixed | Explicit internal delegation statement in JSDoc |
| 4 (Major) | ✅ Fixed | AC-32 added with appropriate invariant |
| 7 (Major) | ✅ Fixed | `textureSizeOverrides` param added with AC-25/AC-26 |
| 3 (Minor) | ✅ Fixed | NOTE added to `suggestTextureSizeMode` JSDoc |
| 5 (Minor) | ✅ Fixed | `baseFov` clarified in D10 and JSDoc |
| 6 (Minor) | ✅ Fixed | Return type note added |
| 8 (Minor) | ✅ Fixed | Import added |
| 9 (Minor) | ✅ Fixed | Internal delegation documented |
| 10 (Minor) | ✅ Fixed | Large factor guidance in JSDoc |
| **11 (Major)** | ❌ New | RangeError handling for behind-camera samples unspecified |

---

Once Issue 11 is addressed, I'm ready to converge. Everything else is solid.

---

## Round 5 — spec_author

Issue 11 is valid and straightforward. Here's the targeted fix:

---

## Changes for Issue 11

### 1. Add to `validateFacingPlaneEdgeReveal` JSDoc

After the existing description of how the camera state is computed at each sample, add:

> If the view-axis distance from the effective camera position to the plane is <= 0 at any sample point (the plane is at or behind the camera), that sample produces an `EdgeRevealCheck` with `safe: false`, `worstMargin: -Infinity`, `distanceToPlane` set to the actual (non-positive) value, and margins of `{ left: -Infinity, right: -Infinity, top: -Infinity, bottom: -Infinity }`. The function does not throw for this condition — it catches the `RangeError` from `computeFacingPlaneMargins` (or preemptively checks distance) and reports it as a maximally-failed check in the result. This ensures that camera paths passing through or behind planes produce diagnostic results rather than crashing validation.

### 2. Add to `validateFacingPlaneEdgeReveal` edge case table

| Scenario | Expected Behavior |
|---|---|
| Plane becomes behind camera during path | The check at that sample has `safe: false`, `worstMargin: -Infinity`, `distanceToPlane <= 0`, and all margins `-Infinity`. The function does NOT throw. |

(This replaces the existing row for this scenario.)

### 3. Add AC-39

> - [ ] **AC-39:** `validateFacingPlaneEdgeReveal` for a camera path where the camera passes behind the plane at some sample point does NOT throw. The result is `safe: false`, and the `worstCheck` has `worstMargin === -Infinity` and `distanceToPlane <= 0`.

### 4. Renumber existing isomorphism ACs

AC-37 and AC-38 (isomorphism) stay as-is. AC-39 is the new one, appended after AC-38.

---

That's the only change. The full revised spec is identical to the Round 3 version with these three additions (JSDoc clarification, edge case table update, AC-39). Everything else — the interface contracts, design decisions, all other ACs, test strategy, integration points — remains unchanged.

I'd like the Challenger to verify this addresses Issue 11 and approve the spec for convergence.

---

## Round 6 — spec_challenger

I've verified the Round 5 fix for Issue 11 against the full spec. The fix is structurally sound:

1. ✅ JSDoc addition specifies `-Infinity` margins, no throw, diagnostic result
2. ✅ Edge case table row replaced with correct behavior  
3. ✅ AC-39 is testable and unambiguous

**Final sweep — one minor clarification I want to note but will NOT block on:**

The sample distribution formula for `validateFacingPlaneEdgeReveal` and related functions is implied but never stated explicitly. The edge case table says `sampleCount=1` → checks only `t=0`, and the JSDoc says "Includes t=0 and t=1." The natural formula is `t_i = i / (sampleCount - 1)` for `i = 0..sampleCount-1`, with the `sampleCount=1` case special-cased to `t=0`. I'll include this as an open question in the final output rather than blocking convergence.

All 11 issues are resolved. The spec is implementable. Let me write it to disk.

CONCLUSION:

The specification defines two pure-math modules (`plane-sizing.ts` and `edge-reveal.ts`) in `src/spatial/` that handle: (1) texture-to-plane auto-sizing with three modes (contain/cover/stretch), (2) camera-motion-dependent oversizing via both fast analytical estimates and precise sampling-based validation, and (3) edge-reveal prevention for facing-camera planes with full diagnostic reporting. Rotated planes are explicitly skipped in V1 with documented reasons. The analytical `computeOversizeFactor` is guaranteed to be a conservative upper bound of the sampling-based `computeMinimumFacingPlaneSize` (AC-32). The `validateGeometryEdgeReveal` function accepts optional `textureSizeOverrides` to validate against actual rendered sizes rather than slot definitions. Behind-camera conditions during path sampling produce `-Infinity` margins rather than throwing (AC-39).
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Bash",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Now let me write the final spec and update meta.json:
[Tool: Bash]
  Input: {
  "command": "ls /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/",
  "description": "List OBJ-040 node directory"
}
[Tool Result] meta.json

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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/output.md",
  "content": "# Specification: Plane Sizing and Edge-Reveal Prevention System (OBJ-040)\n\n## Summary\n\nOBJ-040 defines the plane sizing mathematics for depthkit: (1) **texture-to-plane auto-sizing** \u2014 how a plane's world-unit dimensions are computed from the loaded texture's aspect ratio and the slot's size bounds, using one of three modes (contain, cover, stretch); (2) **camera-motion-dependent oversizing** \u2014 computing the minimum plane size needed to prevent edge reveals given a camera path's displacement envelope; (3) **edge-reveal validation** \u2014 a sampling-based check that verifies no plane edge becomes visible at any point during a camera path's traversal. This is a pure spatial math module with zero rendering dependencies, extending OBJ-003's spatial library and consuming geometry definitions (OBJ-005), camera path metadata (OBJ-006), and texture metadata (OBJ-015).\n\n## Interface Contract\n\n### Texture-to-Plane Sizing\n\n```typescript\n// src/spatial/plane-sizing.ts\n\nimport type { Vec3, Size2D, EulerRotation } from './types';\nimport type { PlaneSlot } from '../scenes/geometries/types';\n\n/**\n * Determines how a texture's aspect ratio is reconciled with a\n * slot's defined size bounding box.\n *\n * - 'contain': Plane shrinks to fit the texture's aspect ratio\n *   WITHIN the slot's size bounds. The texture is fully visible\n *   with no distortion. The plane may be smaller than the slot\n *   in one dimension (\"letterboxed\" or \"pillarboxed\").\n *   Use: subject, near_fg \u2014 preserving image content matters\n *   more than filling the spatial allocation.\n *\n * - 'cover': Plane grows so the texture's aspect ratio COVERS\n *   the slot's size bounds in both dimensions. The plane is >=\n *   the slot size in both dimensions; one dimension matches the\n *   slot, the other exceeds it. No distortion, but the plane\n *   
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json",
  "content": "{\n  \"id\": \"OBJ-040\",\n  \"description\": \"Plane sizing and oversizing system -- visible area calculation per Section 8.3 (visible_height = 2 * d * tan(FOV/2)), camera-motion-dependent oversizing factors to prevent edge reveals during camera movement, edge-reveal prevention math, AND texture-to-plane auto-sizing algorithm per Section 8.9 (how planes adapt dimensions from loaded texture aspect ratios while maintaining geometry spatial structure -- letterbox vs crop vs scale decisions).\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:15:00Z\",\n  \"depends_on\": [\"OBJ-005\", \"OBJ-006\", \"OBJ-003\", \"OBJ-015\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"notes\": \"Tier 3 spatial feature. Spec defines two pure-math modules: plane-sizing.ts (texture-to-plane auto-sizing with contain/cover/stretch modes) and edge-reveal.ts (sampling-based validation for facing-camera planes, analytical oversize factor from OversizeRequirements, margin computation). Rotated planes explicitly skipped in V1 with documented skipReason. 39 acceptance criteria. Deliberation resolved 11 issues across 6 rounds.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Check git status"
}
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-040/meta.json

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
	nodes/OBJ-008/transcript.md
	nodes/OBJ-009/transcript.md
	nodes/OBJ-010/transcript.md
	nodes/OBJ-011/transcript.md
	nodes/OBJ-012/transcript.md
	nodes/OBJ-013/transcript.md
	nodes/OBJ-014/transcript.md
	nodes/OBJ-015/transcript.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-019/transcript.md
	nodes/OBJ-020/transcript.md
	nodes/OBJ-021/transcript.md
	nodes/OBJ-026/transcript.md
	nodes/... [truncated]

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Check recent commits"
}
[Tool Result] 7bceeb2 spec(OBJ-058): Director Agent workflow specification — HITL tuning protocol, Visual Critique template, test render utility
bd72df5 OBJ-041: Geometry-camera spatial compatibility validation spec
37cb4b1 spec(OBJ-046): CLI interface specification — render, validate, preview commands
593383f spec(OBJ-038): audio sync and scene timing specification
f831439 OBJ-035: Orchestrator spec - main render loop coordinating Puppeteer, FFmpeg, virtualized clock

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-040/output.md nodes/OBJ-040/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-040): plane sizing and edge-reveal prevention system\n\nDefines two pure-math modules (plane-sizing.ts, edge-reveal.ts) in src/spatial/:\n- Texture-to-plane auto-sizing with contain/cover/stretch modes\n- Camera-motion-dependent oversizing via analytical estimates and sampling validation\n- Edge-reveal margin computation for facing-camera planes\n- Geometry-level validation with optional texture size overrides\n\nRotated planes explicitly skipped in V1 with documented skipReason.\n39 acceptance criteria. Deliberation resolved 11 issues across 6 rounds.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-040 spec files"
}
[Tool Result] [master 2b71510] spec(OBJ-040): plane sizing and edge-reveal prevention system
 2 files changed, 929 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-040/output.md
The specification for OBJ-040 has been written to `nodes/OBJ-040/output.md`, the metadata updated in `nodes/OBJ-040/meta.json`, and committed to git.

**Deliberation summary:**
- **6 rounds**, resolving **11 issues** (5 major, 6 minor)
- Key issues addressed: contradictory margin formulas, texture-size-override parameter for geometry validation, analytical-vs-sampling invariant AC, behind-camera error handling semantics, `baseFov` definition, and internal function delegation documentation
- **39 acceptance criteria** covering texture sizing, mode suggestion, margin computation, edge-reveal validation, minimum sizing, oversize factors, rotation classification, isomorphism, and behind-camera handling
