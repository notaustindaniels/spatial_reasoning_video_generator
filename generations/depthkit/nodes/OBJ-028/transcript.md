# Deliberation Transcript: OBJ-028

---

## Round 1 — spec_author

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
 * lookAt tracks slightly ahead of the camera's travel direction —
 * the lookAt X is offset toward the destination (more negative) by a
 * fixed lead amount, creating a subtle anticipatory framing rather
 * than a flat perpendicular view.
 *
 * Y and Z positions are constant. FOV is constant at 50°.
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
| `startLookAt` | `[-1, 0, -10]` | `[1, 0, -10]` | Leads 1 unit ahead of center toward travel direction |
| `endLookAt` | `[-1, 0, -10]` | `[1, 0, -10]` | lookAt target is STATIC — camera slides past a fixed focal point |
| `fov` | `50` | `50` | Constant, no FOV animation |
| `defaultEasing` | `ease_in_out` | `ease_in_out` | Smooth acceleration/deceleration feels like a physical dolly |

**Why 6 units total X displacement?** At FOV 50° and camera Z=5, a plane at Z=-15 (20 units from camera) has visible width ≈ `2 × 20 × tan(25°) × (16/9)` ≈ 33.1 units for 16:9. A 6-unit camera slide is ~18% of the visible width at that depth — enough to produce clear parallax separation between depth layers without being so large that oversizing becomes impractical. For closer planes (Z=-5, 10 units from camera), visible width ≈ 16.6 units and the 6-unit slide is ~36% — a strong tracking effect.

**Why static lookAt?** A static lookAt target means the camera's viewing direction rotates subtly as it translates — the camera is always pointed at the same scene point rather than maintaining a fixed heading. This produces a more natural tracking feel: the "subject" stays roughly centered while the background slides behind it, similar to how a dolly shot works on a film set where the camera operator keeps the subject framed. The 1-unit X lead on the lookAt (toward travel direction) prevents the subject from drifting to the leading edge of frame at the start of the shot.

**Why Z=5 for camera, Z=-10 for lookAt?** Z=5 is the default camera distance from origin (seed Section 8.1). The lookAt Z of -10 points the camera into the scene at a natural depth — deep enough to keep distant planes well-framed but not so deep that near planes fall outside the frustum. This is consistent with other presets (OBJ-027 uses similar depths).

### Speed Scaling

When `speed ≠ 1.0`, the X displacement scales linearly:

- `effectiveStartX = startX * speed` (positive for left, negative for right)
- `effectiveEndX = endX * speed`
- Y, Z positions unchanged
- lookAt unchanged (focal point stays fixed regardless of travel amplitude)
- FOV unchanged

Example: `speed = 0.5` on `lateral_track_left` → camera moves from `[1.5, 0, 5]` to `[-1.5, 0, 5]` (3 units total instead of 6).

### Oversize Requirements

```typescript
// For lateral_track_left (identical for lateral_track_right)
const oversizeRequirements: OversizeRequirements = {
  maxDisplacementX: 6,    // Full X travel range at speed=1.0
  maxDisplacementY: 0,    // No Y motion
  maxDisplacementZ: 0,    // No Z motion
  fovRange: [50, 50],     // Constant FOV
  recommendedOversizeFactor: 1.5,
};
```

**Why `recommendedOversizeFactor = 1.5`?** The camera displaces 6 units along X. At FOV 50° and camera Z=5, the visible half-width at the farthest compatible plane (~Z=-30, distance=35) is `35 × tan(25°) × (16/9)` ≈ 29 units. A 6-unit displacement is ~20% of that. An oversize factor of 1.5 (50% wider than the static frustum) provides ample margin, even with some `speed > 1.0` or `offset` values. For closer planes, the displacement is a larger fraction of visible width, but closer planes are physically smaller in a scene geometry, so the 1.5x factor still covers them. This is a conservative safe upper bound; OBJ-040 will compute per-plane factors using the axis displacements.

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
- **`flyover`** — Flyover positions the camera above the ground plane looking down. Lateral tracking at elevated Y with a downward-looking angle is a different motion profile (more of a "pan across terrain" than a "tracking shot"). Could be added in a future revision if there's demand.
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
4. Return `{ position: [x, 0, 5], lookAt: [-1, 0, -10], fov: 50 }`.

For `lateral_track_right`, the X values are mirrored: `x = lerp(-3 * speed, 3 * speed, te)`.

Where `lerp(a, b, t) = a + (b - a) * t` (standard linear interpolation from OBJ-002).

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

**Decision:** The lookAt point is static at `[-1, 0, -10]` (left) / `[1, 0, -10]` (right) throughout the motion. It does not track with the camera's X position.

**Rationale:** Three alternatives were considered:

1. **lookAt tracks with camera (fixed heading):** Camera maintains perpendicular view. Looks robotic — like a security camera on a rail. No natural framing behavior.
2. **lookAt at center `[0, 0, -10]` (no lead):** Camera always points at scene center. At `t=0`, camera at `[3, 0, 5]` looking at `[0, 0, -10]` means the view is angled inward. At `t=1`, `[-3, 0, 5]` looking at `[0, 0, -10]` means the view is angled the other way. The center of the frame sweeps across the scene — a reasonable option.
3. **lookAt with lead offset (chosen):** A 1-unit lead toward the travel direction creates subtle anticipatory framing at the start and a slight "settling past" feel at the end. The lead is small enough (1 unit vs. 6 units of travel) that the viewing angle change is subtle, not dramatic.

Option 3 was chosen because it best emulates how a camera operator frames a tracking shot: the camera leads slightly into the direction of travel. The 1-unit lead amount is modest and should work across all compatible geometries without causing edge issues.

**Trade-off:** The static lookAt means the camera's heading rotates by approximately `atan2(6, 15)` ≈ 21.8° across the full track — noticeable but not extreme. This rotation is what creates the natural "panning past" feel rather than a flat slide.

### D3: Easing default is ease_in_out

**Decision:** Default easing is `ease_in_out`, matching TC-09's claim that eased paths feel more natural than linear.

**Rationale:** A physical dolly on a track accelerates from rest and decelerates to rest. `ease_in_out` matches this physics. Linear motion would feel robotic. The author can override via `camera_params.easing`.

### D4: Speed scales X displacement only, not lookAt

**Decision:** `speed` scales the camera's start/end X positions but does NOT move the lookAt target.

**Rationale:** The lookAt target represents "where the scene's subject is." Scaling displacement changes how far the camera travels, but the subject hasn't moved. If lookAt scaled with speed, the lead offset would grow proportionally, causing an increasingly oblique viewing angle at higher speeds — visually jarring and not what "more intensity" means to an LLM author.

### D5: Symmetric spatial envelope for both presets

**Decision:** Both presets have identical `OversizeRequirements` (same displacement magnitudes), differing only in direction.

**Rationale:** Edge-reveal prevention depends on the magnitude of displacement, not its sign. A 6-unit slide left requires the same plane oversizing as a 6-unit slide right. OBJ-040 uses absolute displacement values.

### D6: No Y-axis micro-drift

**Decision:** Y position is constant at 0. No subtle vertical float is added.

**Rationale:** A real dolly on rails has essentially zero vertical movement — the track constrains it. Adding Y-axis drift would make this a blend of tracking and floating, which is the domain of `gentle_float` (OBJ-031). Keeping the lateral track pure makes it predictable for blind authoring. If an LLM wants combined lateral + vertical, it can use `offset` to shift the camera vertically.

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
- [ ] **AC-10:** At `t=0.5` with default params, `lateralTrackLeft.evaluate(0.5).position[0]` is approximately `0` (camera at center of travel, within tolerance of easing curve — for `ease_in_out`, the midpoint maps to 0.5, so `lerp(3, -3, 0.5) = 0`).
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
- [ ] **AC-31:** `lateralTrackLeft.oversizeRequirements.recommendedOversizeFactor` equals `1.5`.
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
| `params.speed = 5.0` | Valid. Camera moves 30 units total. Likely causes edge reveals — OBJ-040 will flag this based on `maxDisplacementX * speed`. |
| `params.easing = 'linear'` | Overrides ease_in_out. Camera moves at constant velocity. |
| `params.offset = [0, 2, 0]` | Applied by renderer post-evaluate. Camera floats 2 units above the track. Not handled by evaluate(). OBJ-040 accounts for offset in edge-reveal checks. |
| Very short scene duration (e.g., 0.5s at 30fps = 15 frames) | Works correctly — t still maps [0, 1]. Motion may feel abrupt at short durations. This is an authoring concern, not an engine concern. |
| Very long scene duration (e.g., 60s) | Works correctly. Motion may feel very slow. Author can increase speed. |

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
- With `ease_in_out` at `t=0.25`: X ≠ 1.5 (easing curve bends the interpolation).

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
| **OBJ-040** (Edge-reveal validation) | Reads `oversizeRequirements.maxDisplacementX = 6` to compute required X-axis plane sizing. |
| **OBJ-041** (Geometry-camera compatibility) | Reads `compatibleGeometries` to validate manifest combinations. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t, params)`, applies offset, sets Three.js camera. |
| **SKILL.md** (OBJ-071) | `description` and `tags` used for LLM authoring documentation. |
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

1. **Should the lookAt lead amount (1 unit) be affected by speed?** Currently it is not — the lead is a fixed framing aesthetic, not a motion parameter. If speed=3.0, the camera travels 18 units but the lead is still 1 unit, which becomes proportionally less noticeable. This seems fine — the lead is about subtle framing, not about matching travel distance. But worth noting for the tuning phase.

2. **Should `flyover` be added to compatible geometries?** A lateral track at elevated Y across a ground plane is a valid cinematic motion (aerial tracking shot). However, the current preset fixes Y=0, which is incorrect for flyover's elevated camera. A dedicated `flyover_lateral` variant might be more appropriate. Deferring to a future objective.

3. **Is 6 units of total X displacement optimal?** This was derived from visible-width analysis at typical plane depths. The Director Agent tuning workflow (if a tuning OBJ is created for lateral tracks) would validate whether 6 units produces a visually compelling tracking effect or needs adjustment. The `speed` parameter allows per-scene scaling in the meantime.

---

I believe this spec is complete and precise enough for implementation. I'd like the Challenger to verify the spatial parameters, the compatible geometry choices, the lookAt behavior, and the oversize requirements in particular. Please review and let me know if any aspect needs tightening.

---

## Round 2 — spec_challenger

## Challenger Review — Round 2

I've reviewed the spec carefully against the seed, OBJ-006 contract, and implementability standards. The spec is well-structured, clearly written, and mostly precise. Let me call out what's sound before getting to the issues.

### What's Sound

- **Type conformance with OBJ-006** — The spec correctly conforms to `CameraPathPreset`, uses `resolveCameraParams`, returns `CameraFrameState`, and provides all required metadata fields. ✓
- **Mirroring symmetry** — The two presets are clean mirrors. The math checks out: left goes `[3→-3]`, right goes `[-3→3]`, lookAt X signs are mirrored. AC-15/16 capture this correctly. ✓
- **Speed scaling semantics** — Scaling the X endpoints symmetrically around origin preserves balanced framing at all speed values. This is the right call for a lateral track. ✓
- **Static lookAt with lead** — D2 is well-reasoned. The lead-toward-travel-direction creates natural dolly-shot framing. The rationale for choosing option 3 over the other two alternatives is clear. ✓
- **Easing default** — `ease_in_out` for physical dolly feel is correct and well-justified. ✓
- **Compatible geometry exclusions** — Tunnel, flyover, and close_up exclusions are well-reasoned. ✓
- **Acceptance criteria** — Thorough and precise. AC-06 through AC-09 nail the boundary values. AC-15/16 verify mirroring. AC-17-20 verify speed scaling. AC-21/22 verify easing override. AC-34/35 cover continuity and OBJ-006 conformance. ✓

### Issues

---

**Issue 1: `recommendedOversizeFactor` of 1.5 is not a safe upper bound (Major)**

OBJ-006 defines `recommendedOversizeFactor` as: *"A single scalar >= 1.0 that is sufficient to prevent edge reveals for ALL planes in all compatible geometries."*

The spec's value of 1.5 fails this requirement in two ways:

**(a) Portrait mode (C-04 requires 9:16 support).** At FOV 50° with a subject plane at Z=-5 (distance 10 from camera at Z=5), the visible width in 9:16 portrait is `2 × 10 × tan(25°) × (9/16)` ≈ 5.24 units. The camera displaces 6 units. Required factor: `(5.24 + 6) / 5.24` ≈ **2.14**. Far above 1.5.

**(b) lookAt rotation amplifies effective frustum sweep.** Because the lookAt is static at `[-1, 0, -10]`, the camera's viewing direction rotates ~22° across the full track. At a plane 35 units from camera, this rotation sweeps an additional `35 × sin(22°)` ≈ 13 units of scene area beyond the 6 units of positional displacement. Even in 16:9, this pushes the factor above 1.5 for near planes.

**Proposed fix:** Either:
1. Increase the factor to a genuinely conservative value (e.g., **2.5**) that covers both 16:9 and 9:16 for all compatible geometry plane distances, OR
2. Set it to ~1.7 for the common 16:9 case and add an explicit note that this factor assumes 16:9 landscape, and that portrait mode requires higher factors computed by OBJ-040 using per-axis displacements.

I'd recommend option 1 since OBJ-006 says "sufficient for ALL planes in all compatible geometries" without aspect-ratio scoping. A value of **2.5** covers portrait at d=10 (factor ~2.14) with margin, and while wasteful for 16:9 far planes, it serves its stated purpose as a safe upper bound. OBJ-040 computes precise per-plane values anyway.

Additionally, the spec should note that `maxDisplacementX: 6` describes camera *position* displacement only and does NOT account for the additional frustum sweep caused by lookAt rotation. OBJ-040 should sample `evaluate()` at multiple `t` values to compute actual frustum coverage rather than relying solely on `maxDisplacementX`.

---

**Issue 2: Extreme viewing angles at high speed values need documentation (Minor)**

At `speed=3.0`, the camera moves from `[9, 0, 5]` to `[-9, 0, 5]` while lookAt remains at `[-1, 0, -10]`. At t=0, the direction vector is `[-10, 0, -15]`, giving a viewing angle of `atan2(10, 15)` ≈ 33.7° — nearly looking sideways into the scene rather than forward. This would produce extremely distorted perspective on all planes.

**Proposed fix:** Add a note in the Edge Cases table for `speed = 5.0` (or the existing entry) and in Open Questions: *"At speed > ~2.0, the fixed lookAt creates increasingly oblique viewing angles that may produce unnatural perspective distortion. If this becomes a problem during tuning, consider either clamping effective speed or scaling the lookAt X lead proportionally with speed."*

This isn't something the spec needs to solve now — just document it so an implementer or tuner knows it's a known limitation.

---

**Issue 3: Missing "lead amount" as a named constant in the Spatial Parameters section (Minor)**

The 1-unit lookAt lead toward the travel direction is a meaningful design parameter, but it's buried inside the lookAt coordinate values (`[-1, 0, -10]`). If a tuning round wants to adjust the lead, there's no named concept to reference.

**Proposed fix:** Add a row to the Spatial Parameters table:

| Parameter | Value | Rationale |
|---|---|---|
| `lookAtLeadX` | `1` | Lead offset toward travel direction. Subtle anticipatory framing. |

And in the evaluate() pseudocode, make it explicit: `lookAt: [-lookAtLeadX, 0, -10]` for left, `[lookAtLeadX, 0, -10]` for right. This doesn't change behavior — just makes the constant visible.

---

That's it. One major issue (oversize factor), two minor issues (extreme speed documentation, named lead constant). The spec is otherwise solid and ready to converge after these fixes.

---

## Round 3 — spec_author

# Revised Specification: OBJ-028 — Lateral Track Camera Path Presets

All three issues from the Challenger are valid. Here are the revisions:

**Issue 1 (Major — oversize factor):** Accepted. Increased `recommendedOversizeFactor` to `2.5`. Added explicit documentation that `maxDisplacementX` reflects positional displacement only and does not account for frustum sweep from lookAt rotation. Added a note directing OBJ-040 to sample `evaluate()` rather than relying solely on axis displacements.

**Issue 2 (Minor — extreme speed angles):** Accepted. Added documentation in the Edge Cases table and a new note in Open Questions about oblique viewing angles at high speed values.

**Issue 3 (Minor — named lead constant):** Accepted. Added `lookAtLeadX` as a named parameter in the Spatial Parameters table and made it explicit in the evaluate() pseudocode.

---

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
 * Y and Z positions are constant. FOV is constant at 50°.
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
| `cameraZ` | `5` | `5` | Default camera distance from origin (seed §8.1) |
| `lookAtZ` | `-10` | `-10` | Points camera into the scene at natural depth |
| `fov` | `50` | `50` | Constant, no FOV animation |
| `defaultEasing` | `ease_in_out` | `ease_in_out` | Smooth acceleration/deceleration feels like a physical dolly |

**Why 6 units total X displacement?** At FOV 50° and camera Z=5, a plane at Z=-15 (20 units from camera) has visible width ≈ `2 × 20 × tan(25°) × (16/9)` ≈ 33.1 units for 16:9. A 6-unit camera slide is ~18% of the visible width at that depth — enough to produce clear parallax separation between depth layers without being so large that oversizing becomes impractical. For closer planes (Z=-5, 10 units from camera), visible width ≈ 16.6 units and the 6-unit slide is ~36% — a strong tracking effect.

**Why static lookAt?** A static lookAt target means the camera's viewing direction rotates subtly as it translates — the camera is always pointed at the same scene point rather than maintaining a fixed heading. This produces a more natural tracking feel: the "subject" stays roughly centered while the background slides behind it, similar to how a dolly shot works on a film set where the camera operator keeps the subject framed. The `lookAtLeadX` offset (1 unit toward travel direction) prevents the subject from drifting to the leading edge of frame at the start of the shot.

**Why Z=5 for camera, Z=-10 for lookAt?** Z=5 is the default camera distance from origin (seed Section 8.1). The lookAt Z of -10 points the camera into the scene at a natural depth — deep enough to keep distant planes well-framed but not so deep that near planes fall outside the frustum. This is consistent with other presets (OBJ-027 uses similar depths).

### Speed Scaling

When `speed ≠ 1.0`, the X displacement scales linearly:

- `effectiveStartX = startX * speed` (positive for left, negative for right)
- `effectiveEndX = endX * speed`
- Y, Z positions unchanged
- lookAt unchanged (focal point stays fixed regardless of travel amplitude)
- FOV unchanged

Example: `speed = 0.5` on `lateral_track_left` → camera moves from `[1.5, 0, 5]` to `[-1.5, 0, 5]` (3 units total instead of 6).

**Caution at high speed values:** At `speed > ~2.0`, the fixed lookAt creates increasingly oblique viewing angles. At `speed=3.0`, the camera at t=0 is at `[9, 0, 5]` looking at `[-1, 0, -10]`, giving a viewing angle of `atan2(10, 15)` ≈ 33.7° off the Z-axis. This produces noticeable perspective distortion on all planes. OBJ-040 should flag such combinations as high-risk for edge reveals.

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

Worst case: a subject plane at Z=-5 (distance 10 from camera at Z=5) in 9:16 portrait mode. Visible width = `2 × 10 × tan(25°) × (9/16)` ≈ 5.24 units. Camera displaces 6 units positionally, plus the lookAt rotation sweeps the frustum further. Required factor from position alone: `(5.24 + 6) / 5.24` ≈ 2.14. Adding margin for lookAt rotation (~22° sweep creating additional frustum coverage at plane depth) brings the safe upper bound to ~2.5.

For 16:9 at distant planes, 2.5 is conservative — but `recommendedOversizeFactor` is explicitly a safe upper bound, not an optimal value. OBJ-040 computes precise per-plane factors using the axis displacements and `evaluate()` sampling.

**Important:** `maxDisplacementX = 6` describes camera *positional* displacement only. It does NOT account for the additional frustum sweep caused by the lookAt rotation (~22° across the full track). OBJ-040 MUST sample `evaluate()` at multiple `t` values to compute actual frustum coverage at each plane's depth, rather than relying solely on `maxDisplacementX` for per-plane calculations.

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

**Trade-off:** The static lookAt means the camera's heading rotates by approximately `atan2(6, 15)` ≈ 21.8° across the full track — noticeable but not extreme. This rotation is what creates the natural "panning past" feel rather than a flat slide. However, it also means `maxDisplacementX` understates the true frustum sweep. See Oversize Requirements for how this is addressed.

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

**Decision:** `recommendedOversizeFactor` is set to `2.5`, which covers the worst-case combination of 9:16 portrait aspect ratio at close plane distances plus the additional frustum sweep from the ~22° lookAt rotation.

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
| `params.speed = 2.0` | Valid. Camera moves 12 units total. Viewing angle at extremes: `atan2(7, 15)` ≈ 25°. Noticeable perspective distortion but still functional. OBJ-040 flags edge-reveal risk using `maxDisplacementX * speed = 12`. |
| `params.speed = 5.0` | Valid but produces extreme oblique viewing: camera at `[15, 0, 5]` looking at `[-1, 0, -10]`, angle ≈ `atan2(16, 15)` ≈ 46.8°. Nearly sideways. OBJ-040 will likely flag edge reveals. Authoring guidance in SKILL.md should recommend `speed ≤ 2.0` for lateral tracks. |
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
- With `ease_in_out` at `t=0.25`: X ≠ 1.5 (easing curve bends the interpolation).

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
| **SKILL.md** (OBJ-071) | `description` and `tags` used for LLM authoring documentation. Should include guidance that `speed ≤ 2.0` is recommended for lateral tracks. |
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

4. **Should speed be clamped or warned above ~2.0?** At `speed > 2.0`, the fixed lookAt creates oblique viewing angles (>25°) that produce noticeable perspective distortion. Options: (a) clamp speed in `evaluate()`, (b) emit a validation warning in OBJ-040, (c) document in SKILL.md only. Recommend (b) + (c): OBJ-040 flags edge-reveal risk, SKILL.md recommends `speed ≤ 2.0`. No hard clamp — the author may intentionally want oblique framing.

---

I believe this revision addresses all three of the Challenger's issues:
- **Issue 1:** `recommendedOversizeFactor` increased to `2.5` with full portrait-mode and lookAt-rotation justification. Added explicit note about `maxDisplacementX` being positional-only and OBJ-040 needing to sample `evaluate()`.
- **Issue 2:** Edge Cases table updated for `speed=2.0` and `speed=5.0` with viewing angle calculations. New Open Question #4 documents the high-speed limitation.
- **Issue 3:** `lookAtLeadX` added as a named constant in Spatial Parameters and made explicit in the evaluate() pseudocode.

Challenger, please verify these changes and approve if satisfied.

---

## Round 4 — spec_challenger

## Challenger Verification — Round 4

I've verified all three fixes against the revised spec:

**Issue 1 (oversize factor):** ✓ Confirmed. `recommendedOversizeFactor` changed from 1.5 to 2.5. The justification now includes the portrait-mode worst case (factor ~2.14 at Z=-5 in 9:16) plus lookAt rotation margin. The note about `maxDisplacementX` being positional-only is present in both the Oversize Requirements section and the OBJ-040 row in Integration Points.

**Issue 2 (extreme speed):** ✓ Confirmed. Edge Cases table now has entries for `speed=2.0` (angle ~25°, "noticeable but functional") and `speed=5.0` (angle ~46.8°, "nearly sideways"). Open Question #4 documents the limitation and recommends OBJ-040 warning + SKILL.md guidance without a hard clamp.

**Issue 3 (named lead constant):** ✓ Confirmed. `lookAtLeadX` appears in the Spatial Parameters table with its own row, and the evaluate() pseudocode uses `[-lookAtLeadX, 0, -10]` / `[lookAtLeadX, 0, -10]` explicitly.

No new issues introduced by the revisions. The spec is complete, precise, and implementable.

CONCLUSION:

The spec defines `lateral_track_left` and `lateral_track_right` camera path presets conforming to OBJ-006's `CameraPathPreset` contract. Key parameters: 6-unit X displacement at speed=1.0, static lookAt with 1-unit lead (`lookAtLeadX`), FOV fixed at 50°, `ease_in_out` default easing. Compatible with stage, canyon, diorama, portal, and panorama geometries. `recommendedOversizeFactor = 2.5` covers portrait mode and lookAt rotation sweep. 35 acceptance criteria cover boundary values, mirroring, speed scaling, easing override, metadata, determinism, continuity, and OBJ-006 conformance. Four open questions document deferred decisions (lead scaling with speed, flyover compatibility, optimal displacement, speed clamping).
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me check the current state of the node directory and meta.json before writing files.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-028",
     3→  "description": "Lateral track camera path presets -- lateral_track_left (camera translates along negative X-axis, looking slightly ahead) and lateral_track_right (mirror). Cinematic tracking shots. Defines position(t), lookAt(t), easing defaults, compatible geometries, and oversizing requirements (significant X-axis oversizing needed).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Currently a leaf node -- no tuning objective directly references lateral tracks."
    12→}
    13→

[Tool: Bash]
  Input: {
  "command": "ls /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/",
  "description": "List OBJ-028 node directory"
}
[Tool Result] meta.json
Good. Now let me write the output.md and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "content": "# Specification: OBJ-028 \u2014 Lateral Track Camera Path Presets\n\n## Summary\n\nOBJ-028 defines two camera path presets \u2014 `lateral_track_left` and `lateral_track_right` \u2014 that translate the camera along the X-axis to produce cinematic tracking shots. The camera slides horizontally while looking slightly ahead of its travel direction, creating the classic dolly-track effect where foreground planes move faster than background planes due to perspective projection. These presets conform to the `CameraPathPreset` contract from OBJ-006 and require significant X-axis plane oversizing to prevent edge reveals.\n\n## Interface Contract\n\n### Preset Definitions\n\n```typescript\n// src/camera/presets/lateral_track.ts\n\nimport { CameraPathPreset } from '../types';\n\n/**\n * Camera translates along the NEGATIVE X-axis (right to left in screen space).\n * The camera starts at a positive X offset and ends at a negative X offset,\n * producing apparent scene motion from left to right.\n *\n * lookAt is static, offset slightly toward the travel direction by\n * lookAtLeadX, creating subtle anticipatory framing rather than a\n * flat perpendicular view.\n *\n * Y and Z positions are constant. FOV is constant at 50 degrees.\n */\nexport const lateralTrackLeft: CameraPathPreset;\n\n/**\n * Mirror of lateral_track_left. Camera translates along the POSITIVE X-axis\n * (left to right in screen space). The camera starts at a negative X offset\n * and ends at a positive X offset.\n *\n * lookAt leads toward positive X.\n */\nexport const lateralTrackRight: CameraPathPreset;\n```\n\n### Spatial Parameters\n\nThe following constants define the presets' spatial envelope at `speed = 1.0`:\n\n| Parameter | `lateral_track_left` | `lateral_track_right` | Rationale |\n|---|---|---|---|\n| `startPosition` | `[3, 0, 5]` | `[-3, 0, 5]` | Camera starts 3 units o
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/meta.json",
  "content": "{\n  \"id\": \"OBJ-028\",\n  \"description\": \"Lateral track camera path presets -- lateral_track_left (camera translates along negative X-axis, looking slightly ahead) and lateral_track_right (mirror). Cinematic tracking shots. Defines position(t), lookAt(t), easing defaults, compatible geometries, and oversizing requirements (significant X-axis oversizing needed).\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:00:00Z\",\n  \"depends_on\": [\"OBJ-006\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 camera path. Currently a leaf node -- no tuning objective directly references lateral tracks. Spec complete: two presets (lateral_track_left, lateral_track_right), 6-unit X displacement, static lookAt with 1-unit lead, FOV 50, ease_in_out default, recommendedOversizeFactor 2.5 (covers 9:16 portrait + lookAt rotation sweep). Compatible with stage, canyon, diorama, portal, panorama.\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/meta.json has been updated successfully.
Now let me update the index.json to reflect the status change:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/index.json",
  "offset": 108,
  "limit": 15
}
[Tool Result]    108→        "OBJ-029",
   109→        "OBJ-030",
   110→        "OBJ-031",
   111→        "OBJ-032",
   112→        "OBJ-033",
   113→        "OBJ-034",
   114→        "OBJ-040",
   115→        "OBJ-041",
   116→        "OBJ-045",
   117→        "OBJ-071",
   118→        "OBJ-079"
   119→      ],
   120→      "priority": "critical",
   121→      "review_status": "approved",
   122→      "visual_status": null,

[Tool: ToolSearch]
  Input: {
  "query": "select:Edit",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Edit'}]

[Tool: Edit]
  Input: {
  "replace_all": false,
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/index.json",
  "old_string": "    \"OBJ-028\": {\n      \"status\": \"in_progress\",\n      \"depends_on\": [\n        \"OBJ-006\"\n      ],\n      \"blocks\": [],\n      \"priority\": \"high\",\n      \"review_status\": null,\n      \"visual_status\": null,\n      \"category\": \"spatial\"\n    }",
  "new_string": "    \"OBJ-028\": {\n      \"status\": \"specified\",\n      \"depends_on\": [\n        \"OBJ-006\"\n      ],\n      \"blocks\": [],\n      \"priority\": \"high\",\n      \"review_status\": \"approved\",\n      \"visual_status\": null,\n      \"category\": \"spatial\"\n    }"
}
[Tool Error] <tool_use_error>File has been modified since read, either by the user or by a linter. Read it again before attempting to write it.</tool_use_error>

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/index.json",
  "offset": 155,
  "limit": 15
}
[Tool Result]    155→      ],
   156→      "priority": "high",
   157→      "review_status": "approved",
   158→      "visual_status": null,
   159→      "category": "spatial"
   160→    },
   161→    "OBJ-009": {
   162→      "status": "verified",
   163→      "depends_on": [
   164→        "OBJ-001"
   165→      ],
   166→      "blocks": [
   167→        "OBJ-011",
   168→        "OBJ-035",
   169→        "OBJ-038"

[Tool: Bash]
  Input: {
  "command": "grep -n \"OBJ-028\" /Users/austin/spatial_reasoning_video_generator/generations/depthkit/index.json",
  "description": "Find OBJ-028 in index.json"
}
[Tool Result] 107:        "OBJ-028",
451:    "OBJ-028": {

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/index.json",
  "offset": 451,
  "limit": 12
}
[Tool Result]    451→    "OBJ-028": {
   452→      "status": "in_progress",
   453→      "depends_on": [
   454→        "OBJ-006"
   455→      ],
   456→      "blocks": [],
   457→      "priority": "high",
   458→      "review_status": null,
   459→      "visual_status": null,
   460→      "category": "spatial"
   461→    },
   462→    "OBJ-029": {

[Tool: Edit]
  Input: {
  "replace_all": false,
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/index.json",
  "old_string": "    \"OBJ-028\": {\n      \"status\": \"in_progress\",\n      \"depends_on\": [\n        \"OBJ-006\"\n      ],\n      \"blocks\": [],\n      \"priority\": \"high\",\n      \"review_status\": null,\n      \"visual_status\": null,\n      \"category\": \"spatial\"\n    }",
  "new_string": "    \"OBJ-028\": {\n      \"status\": \"specified\",\n      \"depends_on\": [\n        \"OBJ-006\"\n      ],\n      \"blocks\": [],\n      \"priority\": \"high\",\n      \"review_status\": \"approved\",\n      \"visual_status\": null,\n      \"category\": \"spatial\"\n    }"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/index.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-028/output.md nodes/OBJ-028/meta.json index.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-028): lateral track camera path presets\n\nDefine lateral_track_left and lateral_track_right presets conforming to\nOBJ-006 CameraPathPreset contract. 6-unit X displacement, static lookAt\nwith 1-unit lead, FOV 50, ease_in_out default, recommendedOversizeFactor\n2.5 covering portrait mode and lookAt rotation sweep. Compatible with\nstage, canyon, diorama, portal, panorama geometries.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-028 spec files"
}
[Tool Result] [master 0d39d2e] spec(OBJ-028): lateral track camera path presets
 3 files changed, 1109 insertions(+), 216 deletions(-)
 create mode 100644 nodes/OBJ-028/output.md
OBJ-028 specification is committed. The spec defines two lateral track camera path presets with:

- **6-unit X displacement** at speed=1.0, mirrored between left/right
- **Static lookAt** with named `lookAtLeadX = 1` constant for anticipatory framing
- **`recommendedOversizeFactor = 2.5`** covering worst-case 9:16 portrait + lookAt rotation sweep
- **35 acceptance criteria** covering boundary values, mirroring, speed scaling, easing override, metadata, determinism, continuity, and OBJ-006 conformance
- **4 open questions** for future tuning/expansion
