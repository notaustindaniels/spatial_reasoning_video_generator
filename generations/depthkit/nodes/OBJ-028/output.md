# Specification: OBJ-028 — Lateral Track Camera Path Presets

## Summary

OBJ-028 defines two camera path presets — `lateral_track_left` and `lateral_track_right` — that translate the camera along the X-axis to produce cinematic tracking shots. The camera slides horizontally while looking slightly ahead of its travel direction, creating the classic dolly-track effect where foreground planes move faster than background planes due to perspective projection. These presets conform to the `CameraPathPreset` contract from OBJ-006 and require significant X-axis plane oversizing to prevent edge reveals.

## Interface Contract

### Preset Definitions

```typescript
// src/camera/presets/lateral_track.ts

import { CameraPathPreset } from '../types';

/**
 * Camera translates along the NEGATIVE X-axis (right to left in screen space).
 * The camera starts at a positive X offset and ends at a negative X offset,
 * producing apparent scene motion from left to right.
 *
 * lookAt is static, offset slightly toward the travel direction by
 * lookAtLeadX, creating subtle anticipatory framing rather than a
 * flat perpendicular view.
 *
 * Y and Z positions are constant. FOV is constant at 50 degrees.
 */
export const lateralTrackLeft: CameraPathPreset;

/**
 * Mirror of lateral_track_left. Camera translates along the POSITIVE X-axis
 * (left to right in screen space). The camera starts at a negative X offset
 * and ends at a positive X offset.
 *
 * lookAt leads toward positive X.
 */
export const lateralTrackRight: CameraPathPreset;
```

### Spatial Parameters

The following constants define the presets' spatial envelope at `speed = 1.0`:

| Parameter | `lateral_track_left` | `lateral_track_right` | Rationale |
|---|---|---|---|
| `startPosition` | `[3, 0, 5]` | `[-3, 0, 5]` | Camera starts 3 units offset from center along X |
| `endPosition` | `[-3, 0, 5]` | `[3, 0, 5]` | Total X displacement: 6 world units |
| `lookAtLeadX` | `1` | `1` | Lead offset toward travel direction. Subtle anticipatory framing. |
| `lookAtTarget` | `[-lookAtLeadX, 0, -10]` = `[-1, 0, -10]` | `[lookAtLeadX, 0, -10]` = `[1, 0, -10]` | Static target; camera slides past a fixed focal point |
| `cameraZ` | `5` | `5` | Default camera distance from origin (seed Section 8.1) |
| `lookAtZ` | `-10` | `-10` | Points camera into the scene at natural depth |
| `fov` | `50` | `50` | Constant, no FOV animation |
| `defaultEasing` | `ease_in_out` | `ease_in_out` | Smooth acceleration/deceleration feels like a physical dolly |

**Why 6 units total X displacement?** At FOV 50 degrees and camera Z=5, a plane at Z=-15 (20 units from camera) has visible width approximately `2 * 20 * tan(25 degrees) * (16/9)` which is approximately 33.1 units for 16:9. A 6-unit camera slide is ~18% of the visible width at that depth — enough to produce clear parallax separation between depth layers without being so large that oversizing becomes impractical. For closer planes (Z=-5, 10 units from camera), visible width is approximately 16.6 units and the 6-unit slide is ~36% — a strong tracking effect.

**Why static lookAt?** A static lookAt target means the camera's viewing direction rotates subtly as it translates — the camera is always pointed at the same scene point rather than maintaining a fixed heading. This produces a more natural tracking feel: the "subject" stays roughly centered while the background slides behind it, similar to how a dolly shot works on a film set where the camera operator keeps the subject framed. The `lookAtLeadX` offset (1 unit toward travel direction) prevents the subject from drifting to the leading edge of frame at the start of the shot.

**Why Z=5 for camera, Z=-10 for lookAt?** Z=5 is the default camera distance from origin (seed Section 8.1). The lookAt Z of -10 points the camera into the scene at a natural depth — deep enough to keep distant planes well-framed but not so deep that near planes fall outside the frustum. This is consistent with other presets (OBJ-027 uses similar depths).

### Speed Scaling

When `speed != 1.0`, the X displacement scales linearly:

- `effectiveStartX = startX * speed` (positive for left, negative for right)
- `effectiveEndX = endX * speed`
- Y, Z positions unchanged
- lookAt unchanged (focal point stays fixed regardless of travel amplitude)
- FOV unchanged

Example: `speed = 0.5` on `lateral_track_left` results in camera moving from `[1.5, 0, 5]` to `[-1.5, 0, 5]` (3 units total instead of 6).

**Caution at high speed values:** At `speed > ~2.0`, the fixed lookAt creates increasingly oblique viewing angles. At `speed=3.0`, the camera at t=0 is at `[9, 0, 5]` looking at `[-1, 0, -10]`, giving a viewing angle of `atan2(10, 15)` which is approximately 33.7 degrees off the Z-axis. This produces noticeable perspective distortion on all planes. OBJ-040 should flag such combinations as high-risk for edge reveals.

### Oversize Requirements

```typescript
// For lateral_track_left (identical for lateral_track_right)
const oversizeRequirements: OversizeRequirements = {
  maxDisplacementX: 6,    // Full X travel range at speed=1.0 (positional only)
  maxDisplacementY: 0,    // No Y motion
  maxDisplacementZ: 0,    // No Z motion
  fovRange: [50, 50],     // Constant FOV
  recommendedOversizeFactor: 2.5,
};
```

**Why `recommendedOversizeFactor = 2.5`?**

The factor must be a safe upper bound for ALL planes in ALL compatible geometries, at BOTH 16:9 and 9:16 aspect ratios (per C-04).

Worst case: a subject plane at Z=-5 (distance 10 from camera at Z=5) in 9:16 portrait mode. Visible width = `2 * 10 * tan(25 degrees) * (9/16)` which is approximately 5.24 units. Camera displaces 6 units positionally, plus the lookAt rotation sweeps the frustum further. Required factor from position alone: `(5.24 + 6) / 5.24` which is approximately 2.14. Adding margin for lookAt rotation (~22 degrees sweep creating additional frustum coverage at plane depth) brings the safe upper bound to ~2.5.

For 16:9 at distant planes, 2.5 is conservative — but `recommendedOversizeFactor` is explicitly a safe upper bound, not an optimal value. OBJ-040 computes precise per-plane factors using the axis displacements and `evaluate()` sampling.

**Important:** `maxDisplacementX = 6` describes camera *positional* displacement only. It does NOT account for the additional frustum sweep caused by the lookAt rotation (~22 degrees across the full track). OBJ-040 MUST sample `evaluate()` at multiple `t` values to compute actual frustum coverage at each plane's depth, rather than relying solely on `maxDisplacementX` for per-plane calculations.

### Compatible Geometries

```typescript
compatibleGeometries: ['stage', 'canyon', 'diorama', 'portal', 'panorama']
```

**Rationale for each:**
- **`stage`** — Classic tracking shot past a subject against a backdrop. The primary use case.
- **`canyon`** — Tracking between tall walls. X displacement slides past the walls, revealing depth.
- **`diorama`** — Lateral motion across layered planes produces strong parallax separation — the defining visual of a diorama.
- **`portal`** — Lateral track across concentric frames creates interesting asymmetric reveal.
- **`panorama`** — Lateral translation across a wide backdrop is natural for panoramic environments.

**Excluded geometries and rationale:**
- **`tunnel`** — A tunnel is designed for forward motion (Z-axis push). Lateral tracking inside a tunnel would slide the camera toward a wall, breaking the spatial illusion. The tunnel's walls are sized for forward motion, not lateral.
- **`flyover`** — Flyover positions the camera above the ground plane looking down. Lateral tracking at elevated Y with a downward-looking angle is a different motion profile (more of a "pan across terrain" than a "tracking shot"). Could be added as a dedicated `flyover_lateral` variant in a future objective.
- **`close_up`** — Close-up geometry has minimal background and the subject fills the frame. A 6-unit lateral track would move the subject out of frame entirely. Not compatible.

### Tags

```typescript
tags: ['lateral', 'track', 'horizontal', 'dolly', 'cinematic']
```

### Description Strings

- `lateral_track_left`: `"Camera tracks left along the X-axis, sliding past the scene like a dolly shot. Background planes move right, foreground planes move right faster. Smooth ease-in-out by default."`
- `lateral_track_right`: `"Camera tracks right along the X-axis, mirror of lateral_track_left. Background planes move left, foreground planes move left faster. Smooth ease-in-out by default."`

### evaluate() Behavior

The `evaluate()` function for `lateral_track_left`:

1. Call `resolveCameraParams(params, 'ease_in_out')` to get `{ speed, easing }`.
2. Compute eased time: `te = easing(t)`.
3. Compute X position: `x = lerp(3 * speed, -3 * speed, te)` — interpolate from start X to end X.
4. Return `{ position: [x, 0, 5], lookAt: [-lookAtLeadX, 0, -10], fov: 50 }`.

For `lateral_track_right`: `x = lerp(-3 * speed, 3 * speed, te)`, lookAt is `[lookAtLeadX, 0, -10]`.

Where `lerp(a, b, t) = a + (b - a) * t` (standard linear interpolation from OBJ-002) and `lookAtLeadX = 1`.

### Module Exports

```typescript
// src/camera/presets/lateral_track.ts
export { lateralTrackLeft, lateralTrackRight };

// These are registered in the camera path registry (src/camera/presets/index.ts)
// under the keys 'lateral_track_left' and 'lateral_track_right'.
```

## Design Decisions

### D1: Two separate preset objects, not a parameterized factory

**Decision:** Export `lateralTrackLeft` and `lateralTrackRight` as two distinct `CameraPathPreset` objects rather than a `createLateralTrack(direction)` factory.

**Rationale:** OBJ-006 D3 and the registry contract expect concrete `CameraPathPreset` instances keyed by name. The manifest schema uses string names (`"camera": "lateral_track_left"`). Two presets with fixed names are simpler, more discoverable in SKILL.md, and require no factory machinery. Internally, the implementation may share a helper function, but the exported surface is two named presets.

### D2: Static lookAt target with subtle lead offset

**Decision:** The lookAt point is static at `[-lookAtLeadX, 0, -10]` (left) / `[lookAtLeadX, 0, -10]` (right) throughout the motion, where `lookAtLeadX = 1`. It does not track with the camera's X position.

**Rationale:** Three alternatives were considered:

1. **lookAt tracks with camera (fixed heading):** Camera maintains perpendicular view. Looks robotic — like a security camera on a rail. No natural framing behavior.
2. **lookAt at center `[0, 0, -10]` (no lead):** Camera always points at scene center. At `t=0`, camera at `[3, 0, 5]` looking at `[0, 0, -10]` means the view is angled inward. At `t=1`, `[-3, 0, 5]` looking at `[0, 0, -10]` means the view is angled the other way. The center of the frame sweeps across the scene — a reasonable option.
3. **lookAt with lead offset (chosen):** A 1-unit lead toward the travel direction creates subtle anticipatory framing at the start and a slight "settling past" feel at the end. The lead is small enough (1 unit vs. 6 units of travel) that the viewing angle change is subtle, not dramatic.

Option 3 was chosen because it best emulates how a camera operator frames a tracking shot: the camera leads slightly into the direction of travel. The `lookAtLeadX` of 1 unit is modest and should work across all compatible geometries without causing edge issues.

**Trade-off:** The static lookAt means the camera's heading rotates by approximately `atan2(6, 15)` which is approximately 21.8 degrees across the full track — noticeable but not extreme. This rotation is what creates the natural "panning past" feel rather than a flat slide. However, it also means `maxDisplacementX` understates the true frustum sweep. See Oversize Requirements for how this is addressed.

### D3: Easing default is ease_in_out

**Decision:** Default easing is `ease_in_out`, matching TC-09's claim that eased paths feel more natural than linear.

**Rationale:** A physical dolly on a track accelerates from rest and decelerates to rest. `ease_in_out` matches this physics. Linear motion would feel robotic. The author can override via `camera_params.easing`.

### D4: Speed scales X displacement only, not lookAt

**Decision:** `speed` scales the camera's start/end X positions but does NOT move the lookAt target.

**Rationale:** The lookAt target represents "where the scene's subject is." Scaling displacement changes how far the camera travels, but the subject hasn't moved. If lookAt scaled with speed, the lead offset would grow proportionally, causing an increasingly oblique viewing angle at higher speeds — visually jarring and not what "more intensity" means to an LLM author.

**Consequence:** At high speed values (> ~2.0), the fixed lookAt creates increasingly oblique viewing angles because the camera's positional range grows while the lookAt remains fixed. This is documented as a known limitation. See Edge Cases.

### D5: Symmetric spatial envelope for both presets

**Decision:** Both presets have identical `OversizeRequirements` (same displacement magnitudes), differing only in direction.

**Rationale:** Edge-reveal prevention depends on the magnitude of displacement, not its sign. A 6-unit slide left requires the same plane oversizing as a 6-unit slide right. OBJ-040 uses absolute displacement values.

### D6: No Y-axis micro-drift

**Decision:** Y position is constant at 0. No subtle vertical float is added.

**Rationale:** A real dolly on rails has essentially zero vertical movement — the track constrains it. Adding Y-axis drift would make this a blend of tracking and floating, which is the domain of `gentle_float` (OBJ-031). Keeping the lateral track pure makes it predictable for blind authoring. If an LLM wants combined lateral + vertical, it can use `offset` to shift the camera vertically.

### D7: recommendedOversizeFactor accounts for portrait mode and lookAt rotation

**Decision:** `recommendedOversizeFactor` is set to `2.5`, which covers the worst-case combination of 9:16 portrait aspect ratio at close plane distances plus the additional frustum sweep from the ~22 degree lookAt rotation.

**Rationale:** OBJ-006 defines this factor as "sufficient to prevent edge reveals for ALL planes in all compatible geometries." C-04 requires support for both 16:9 and 9:16. The worst case is a subject plane at Z=-5 in 9:16 portrait: visible width ~5.24 units, positional displacement 6 units, plus lookAt rotation sweep. Factor 2.5 covers this with margin. While conservative for 16:9 far planes, OBJ-040 computes precise per-plane factors using axis displacements and `evaluate()` sampling — the scalar is a safe fallback.

## Acceptance Criteria

### Preset Registration
- [ ] **AC-01:** `lateral_track_left` is registered in the camera path registry under the key `'lateral_track_left'`.
- [ ] **AC-02:** `lateral_track_right` is registered in the camera path registry under the key `'lateral_track_right'`.

### Type Conformance
- [ ] **AC-03:** Both presets satisfy the `CameraPathPreset` interface from OBJ-006.
- [ ] **AC-04:** `validateCameraPathPreset(lateralTrackLeft)` returns an empty array.
- [ ] **AC-05:** `validateCameraPathPreset(lateralTrackRight)` returns an empty array.

### Boundary Values
- [ ] **AC-06:** `lateralTrackLeft.evaluate(0)` returns `{ position: [3, 0, 5], lookAt: [-1, 0, -10], fov: 50 }` and matches `defaultStartState` within 1e-6.
- [ ] **AC-07:** `lateralTrackLeft.evaluate(1)` returns `{ position: [-3, 0, 5], lookAt: [-1, 0, -10], fov: 50 }` and matches `defaultEndState` within 1e-6.
- [ ] **AC-08:** `lateralTrackRight.evaluate(0)` returns `{ position: [-3, 0, 5], lookAt: [1, 0, -10], fov: 50 }` and matches `defaultStartState` within 1e-6.
- [ ] **AC-09:** `lateralTrackRight.evaluate(1)` returns `{ position: [3, 0, 5], lookAt: [1, 0, -10], fov: 50 }` and matches `defaultEndState` within 1e-6.

### Motion Profile
- [ ] **AC-10:** At `t=0.5` with default params, `lateralTrackLeft.evaluate(0.5).position[0]` is approximately `0` (camera at center of travel; for `ease_in_out`, the midpoint maps to 0.5, so `lerp(3, -3, 0.5) = 0`).
- [ ] **AC-11:** For `lateralTrackLeft`, `position[1]` (Y) is exactly `0` for all `t` in `[0, 1]`.
- [ ] **AC-12:** For `lateralTrackLeft`, `position[2]` (Z) is exactly `5` for all `t` in `[0, 1]`.
- [ ] **AC-13:** For `lateralTrackLeft`, `fov` is exactly `50` for all `t` in `[0, 1]`.
- [ ] **AC-14:** For `lateralTrackLeft`, `lookAt` is exactly `[-1, 0, -10]` for all `t` in `[0, 1]`.

### Mirroring
- [ ] **AC-15:** For any `t` and identical `params`, `lateralTrackLeft.evaluate(t, params).position[0]` equals `-lateralTrackRight.evaluate(t, params).position[0]` (X positions are mirrored).
- [ ] **AC-16:** `lateralTrackLeft.evaluate(t).lookAt[0]` equals `-lateralTrackRight.evaluate(t).lookAt[0]` for all `t`.

### Speed Scaling
- [ ] **AC-17:** `lateralTrackLeft.evaluate(0, { speed: 0.5 }).position[0]` equals `1.5` (half of 3).
- [ ] **AC-18:** `lateralTrackLeft.evaluate(1, { speed: 0.5 }).position[0]` equals `-1.5`.
- [ ] **AC-19:** `lateralTrackLeft.evaluate(0, { speed: 2.0 }).position[0]` equals `6` (double of 3).
- [ ] **AC-20:** Speed scaling does not affect Y, Z, lookAt, or fov.

### Easing Override
- [ ] **AC-21:** `lateralTrackLeft.evaluate(0.25, { easing: 'linear' }).position[0]` equals `lerp(3, -3, 0.25) = 1.5`.
- [ ] **AC-22:** `lateralTrackLeft.evaluate(0.25)` with default `ease_in_out` easing produces a different X value than with `linear` easing at `t=0.25`.

### Metadata
- [ ] **AC-23:** `lateralTrackLeft.defaultEasing` equals `'ease_in_out'`.
- [ ] **AC-24:** `lateralTrackRight.defaultEasing` equals `'ease_in_out'`.
- [ ] **AC-25:** Both presets' `compatibleGeometries` include `'stage'`, `'canyon'`, `'diorama'`, `'portal'`, `'panorama'`.
- [ ] **AC-26:** Neither preset's `compatibleGeometries` includes `'tunnel'`, `'flyover'`, or `'close_up'`.
- [ ] **AC-27:** `lateralTrackLeft.oversizeRequirements.maxDisplacementX` equals `6`.
- [ ] **AC-28:** `lateralTrackLeft.oversizeRequirements.maxDisplacementY` equals `0`.
- [ ] **AC-29:** `lateralTrackLeft.oversizeRequirements.maxDisplacementZ` equals `0`.
- [ ] **AC-30:** `lateralTrackLeft.oversizeRequirements.fovRange` equals `[50, 50]`.
- [ ] **AC-31:** `lateralTrackLeft.oversizeRequirements.recommendedOversizeFactor` equals `2.5`.
- [ ] **AC-32:** Both presets have `tags` containing at least `'lateral'`, `'track'`, and `'horizontal'`.

### Determinism
- [ ] **AC-33:** Calling `lateralTrackLeft.evaluate(t, params)` 1000 times with the same `t` and `params` produces identical `CameraFrameState` values every time (C-05).

### Continuity
- [ ] **AC-34:** Sampling both presets at 100 evenly-spaced points in `[0, 1]` produces no NaN, no Infinity, and FOV always equals 50.

### OBJ-006 Conformance Suite
- [ ] **AC-35:** Both presets pass the full OBJ-006 contract conformance test pattern (boundary start, boundary end, continuity, FOV range, determinism, full validation, speed scaling, easing override).

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `t = 0` | Returns start position exactly matching `defaultStartState` |
| `t = 1` | Returns end position exactly matching `defaultEndState` |
| `t < 0` or `t > 1` | Undefined behavior per OBJ-006 contract. Callers must clamp. Implementer MAY clamp internally as a safety measure. |
| `params = undefined` | Uses defaults: `speed=1.0`, `easing=ease_in_out` |
| `params = {}` | Same as undefined — all defaults |
| `params.speed = 0` | `resolveCameraParams` throws (speed must be > 0) |
| `params.speed = 0.001` | Valid. Camera barely moves (0.006 units total). No edge reveals. |
| `params.speed = 2.0` | Valid. Camera moves 12 units total. Viewing angle at extremes: `atan2(7, 15)` is approximately 25 degrees. Noticeable perspective distortion but still functional. OBJ-040 flags edge-reveal risk using `maxDisplacementX * speed = 12`. |
| `params.speed = 5.0` | Valid but produces extreme oblique viewing: camera at `[15, 0, 5]` looking at `[-1, 0, -10]`, angle is approximately `atan2(16, 15)` which is approximately 46.8 degrees. Nearly sideways. OBJ-040 will likely flag edge reveals. Authoring guidance in SKILL.md should recommend `speed <= 2.0` for lateral tracks. |
| `params.easing = 'linear'` | Overrides ease_in_out. Camera moves at constant velocity. |
| `params.offset = [0, 2, 0]` | Applied by renderer post-evaluate. Camera floats 2 units above the track. Not handled by evaluate(). OBJ-040 accounts for offset in edge-reveal checks. |
| Very short scene duration (e.g., 0.5s at 30fps = 15 frames) | Works correctly — t still maps [0, 1]. Motion may feel abrupt at short durations. This is an authoring concern, not an engine concern. |
| Very long scene duration (e.g., 60s) | Works correctly. Motion may feel very slow. Author can increase speed. |
| 9:16 portrait aspect ratio | Works correctly. Visible width is narrower, so the same 6-unit displacement covers a larger proportion of frame. `recommendedOversizeFactor = 2.5` accounts for this. |

## Test Strategy

### Unit Tests

**1. Boundary conformance (per OBJ-006 conformance suite):**
- `evaluate(0)` matches `defaultStartState` within 1e-6 per component for both presets.
- `evaluate(1)` matches `defaultEndState` within 1e-6 per component for both presets.

**2. Motion axis isolation:**
- Sample 100 points: Y is always 0, Z is always 5, FOV is always 50 for both presets.
- Only X varies.

**3. Monotonicity of X under linear easing:**
- With `{ easing: 'linear' }`, `lateralTrackLeft`'s X should be strictly decreasing from t=0 to t=1.
- With `{ easing: 'linear' }`, `lateralTrackRight`'s X should be strictly increasing from t=0 to t=1.

**4. Mirror symmetry:**
- For 100 evenly-spaced `t` values, verify `left.evaluate(t).position[0] === -right.evaluate(t).position[0]`.
- Verify `left.evaluate(t).lookAt[0] === -right.evaluate(t).lookAt[0]`.

**5. Speed scaling:**
- `speed=0.5`: start X is halved, end X is halved, midpoint X proportional.
- `speed=2.0`: start X is doubled, end X is doubled.
- Speed does not affect Y, Z, lookAt, or fov.

**6. Easing override:**
- With `linear` easing at `t=0.25`: X = `lerp(3, -3, 0.25)` = 1.5 for left track.
- With `ease_in_out` at `t=0.25`: X != 1.5 (easing curve bends the interpolation).

**7. lookAt constancy:**
- For 100 samples, lookAt is identical for all t values (static target).

**8. Determinism:**
- 1000 calls with same inputs produce identical outputs.

**9. Continuity / no discontinuities:**
- 100 samples produce finite, non-NaN values.
- Adjacent samples have X difference < expected maximum per-step delta (no jumps).

**10. Validation pass:**
- `validateCameraPathPreset` returns empty array for both presets.

**11. OBJ-006 reusable conformance suite:**
- Run the standard 8-check conformance pattern defined in OBJ-006's test strategy for both presets.

### Relevant Testable Claims

- **TC-04:** These presets allow LLM authors to specify lateral tracking by name without XYZ math.
- **TC-08:** Lateral tracks contribute to the geometry coverage claim — they serve stage, canyon, diorama, portal, and panorama geometries.
- **TC-09:** Default `ease_in_out` easing supports A/B comparison with `linear` for naturalness testing.

## Integration Points

### Depends On

| Dependency | What is imported | How it's used |
|---|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `OversizeRequirements`, `resolveCameraParams` | Preset conforms to `CameraPathPreset` interface. `evaluate()` calls `resolveCameraParams()` to resolve speed/easing. Returns `CameraFrameState`. |
| **OBJ-002** (`src/interpolation/`) | `interpolate` or `lerp` utility | Used internally by `evaluate()` to interpolate X position. Also `EasingName` type via OBJ-006. |

### Consumed By

| Consumer | How it uses these presets |
|---|---|
| **Camera path registry** (`src/camera/presets/index.ts`) | Both presets registered under `'lateral_track_left'` and `'lateral_track_right'`. |
| **OBJ-040** (Edge-reveal validation) | Reads `oversizeRequirements`. MUST sample `evaluate()` at multiple `t` values to compute actual frustum coverage rather than relying solely on `maxDisplacementX`, because the lookAt rotation creates additional frustum sweep beyond positional displacement. |
| **OBJ-041** (Geometry-camera compatibility) | Reads `compatibleGeometries` to validate manifest combinations. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t, params)`, applies offset, sets Three.js camera. |
| **SKILL.md** (OBJ-071) | `description` and `tags` used for LLM authoring documentation. Should include guidance that `speed <= 2.0` is recommended for lateral tracks. |
| **Tuning objectives** | Currently a leaf node (no tuning OBJ directly references lateral tracks per meta.json). Future tuning may be added. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        lateral_track.ts    # Exports lateralTrackLeft, lateralTrackRight
        index.ts            # Re-exports and registers in registry
```

## Open Questions

1. **Should the lookAt lead amount (`lookAtLeadX = 1`) be affected by speed?** Currently it is not — the lead is a fixed framing aesthetic, not a motion parameter. If speed=3.0, the camera travels 18 units but the lead is still 1 unit, which becomes proportionally less noticeable. This seems fine — the lead is about subtle framing, not about matching travel distance. But worth noting for the tuning phase.

2. **Should `flyover` be added to compatible geometries?** A lateral track at elevated Y across a ground plane is a valid cinematic motion (aerial tracking shot). However, the current preset fixes Y=0, which is incorrect for flyover's elevated camera. A dedicated `flyover_lateral` variant might be more appropriate. Deferring to a future objective.

3. **Is 6 units of total X displacement optimal?** This was derived from visible-width analysis at typical plane depths. The Director Agent tuning workflow (if a tuning OBJ is created for lateral tracks) would validate whether 6 units produces a visually compelling tracking effect or needs adjustment. The `speed` parameter allows per-scene scaling in the meantime.

4. **Should speed be clamped or warned above ~2.0?** At `speed > 2.0`, the fixed lookAt creates oblique viewing angles (>25 degrees) that produce noticeable perspective distortion. Options: (a) clamp speed in `evaluate()`, (b) emit a validation warning in OBJ-040, (c) document in SKILL.md only. Recommend (b) + (c): OBJ-040 flags edge-reveal risk, SKILL.md recommends `speed <= 2.0`. No hard clamp — the author may intentionally want oblique framing.
