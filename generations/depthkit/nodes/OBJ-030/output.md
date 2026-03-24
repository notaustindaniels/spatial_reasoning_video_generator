# Specification: OBJ-030 — Flyover Glide Camera Path Preset

## Summary

OBJ-030 defines the `flyover_glide` camera path preset — a bird's-eye aerial movement where the camera is positioned at elevated Y, moves forward along the Z-axis, and looks slightly downward throughout. This preset conforms to the `CameraPathPreset` contract from OBJ-006 and is designed primarily for the `flyover` scene geometry. It produces the feel of gliding over a landscape, looking ahead and down at the terrain below.

## Interface Contract

### Preset Export

```typescript
// src/camera/presets/flyover-glide.ts

import { CameraPathPreset } from '../types';

/**
 * The flyover_glide camera path preset.
 * Conforms to CameraPathPreset (OBJ-006).
 */
export const flyoverGlide: CameraPathPreset;
```

### Spatial Parameters (Constants)

These are the defining spatial values for the preset at `speed = 1.0`. They are **module-private named constants** (not exported). They are tested indirectly via `defaultStartState`, `defaultEndState`, and the spatial behavior acceptance criteria. OBJ-062 modifies them in-source during visual tuning rounds.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `Y_CAMERA` | `8` | Elevated above ground plane. Flyover geometry places ground at approximately Y=-2; this gives ~10 units of clearance — high enough for aerial feel without losing ground detail. |
| `Z_START` | `5` | Camera starts slightly in front of origin, consistent with Three.js default camera convention. |
| `Z_END` | `-25` | 30 world-units of forward travel. Provides substantial forward motion for scenes up to ~15s without feeling rushed. |
| `Y_LOOK` | `-2` | lookAt Y target — at ground plane level. Creates the downward gaze angle. |
| `LOOK_AHEAD` | `15` | How far ahead of the camera (on Z) the lookAt target sits. lookAt Z tracks the camera's Z minus this offset, keeping the camera looking forward-and-down rather than straight down. |
| `FOV` | `50` | Static FOV. No FOV animation — the aerial feel comes from elevation and forward motion, not lens distortion. |

### Derived Motion

The evaluate function computes position and lookAt using inline linear interpolation (`a + (b - a) * u`) — no external `lerp` import is needed since this is a single arithmetic expression.

```
eased_t    = easingFn(t)    // resolved via resolveCameraParams()

position(t) = [0, Y_CAMERA, Z_START + (Z_END - Z_START) * eased_t]
lookAt(t)   = [0, Y_LOOK,   (Z_START - LOOK_AHEAD) + (Z_END - Z_START) * eased_t]
fov(t)      = FOV  (constant)
```

The lookAt target moves in lockstep with the camera on Z (same interpolation, same easing), offset by `LOOK_AHEAD` units ahead. This maintains a constant downward viewing angle throughout the flight — approximately `atan2(Y_CAMERA - Y_LOOK, LOOK_AHEAD) = atan2(10, 15) ~ 33.7 degrees` below horizontal.

**LOOK_AHEAD invariant under speed:** The invariant `lookAt[2] === position[2] - LOOK_AHEAD` holds for all `speed` values because both position Z and lookAt Z use the same base displacement `(Z_END - Z_START) * speed` with the same easing. The `LOOK_AHEAD` constant is subtracted from the lookAt's base point, not from the displacement term, so speed scaling cancels out in the difference.

### Speed Scaling

Per OBJ-006 D3, `speed` scales spatial amplitude, not temporal rate:

```
effective_z_displacement = (Z_END - Z_START) * speed = -30 * speed

position(t) = [0, Y_CAMERA, Z_START + (Z_END - Z_START) * speed * eased_t]
lookAt(t)   = [0, Y_LOOK,   (Z_START - LOOK_AHEAD) + (Z_END - Z_START) * speed * eased_t]
```

At `speed = 0.5`: camera travels 15 units forward instead of 30. Same easing curve, same duration, less ground covered.

At `speed = 1.5`: camera travels 45 units forward. Greater risk of edge reveals — OBJ-040 must account for this.

**Y_CAMERA and Y_LOOK are NOT scaled by speed.** The elevation is a fixed property of the flyover vantage point. Speed controls how far the camera flies, not how high it flies.

**LOOK_AHEAD is NOT scaled by speed.** The viewing angle remains consistent regardless of flight distance.

### Preset Definition

```typescript
export const flyoverGlide: CameraPathPreset = {
  name: 'flyover_glide',

  description: 'Bird\'s-eye aerial glide. Camera moves forward at elevated Y, looking down at the ground plane. Smooth, expansive feel suited to landscapes, cityscapes, and environmental establishing shots.',

  evaluate: /* implements the motion equations above using resolveCameraParams() and inline arithmetic */,

  defaultStartState: {
    position: [0, 8, 5],
    lookAt: [0, -2, -10],   // Z_START - LOOK_AHEAD = 5 - 15 = -10
    fov: 50,
  },

  defaultEndState: {
    position: [0, 8, -25],
    lookAt: [0, -2, -40],   // Z_END - LOOK_AHEAD = -25 - 15 = -40
    fov: 50,
  },

  defaultEasing: 'ease_in_out',

  compatibleGeometries: ['flyover'],

  oversizeRequirements: {
    maxDisplacementX: 0,
    maxDisplacementY: 0,
    maxDisplacementZ: 30,
    fovRange: [50, 50],
    recommendedOversizeFactor: 1.4,
  },

  tags: ['aerial', 'flyover', 'forward', 'birds_eye', 'glide', 'landscape'],
};
```

### Oversize Factor: Initial Estimate with Validation Gate

The `recommendedOversizeFactor` of **1.4** is an initial estimate, not a derivation from first principles. The rationale for this starting value:

- The camera views the ground plane at an oblique angle (~33.7 degrees below horizontal). The visible footprint on a horizontal plane is stretched along the depth direction relative to a perpendicular view.
- The camera travels 30 units on Z at speed=1.0, changing which portion of the ground plane is visible.
- A 40% margin over base frustum size is intended to cover both the oblique angle stretch and the travel range.

**However,** the precise required oversize depends on the flyover geometry's plane layout (defined by OBJ-021), which this preset should not hardcode knowledge of. The 1.4 value is subject to validation:

- **OBJ-040** (edge-reveal validation) will compute precise per-plane oversize factors using the displacement values (`maxDisplacementX/Y/Z`) and the geometry's plane positions. If OBJ-040 computes a required factor > 1.4 for any plane in the `flyover` geometry at speed=1.0, this value **MUST** be updated to match or exceed that computed maximum.
- **OBJ-062** (visual tuning) may further adjust this value based on observed edge reveals in test renders.

This is captured in AC-29 below.

## Design Decisions

### D1: Constant viewing angle via co-moving lookAt

**Decision:** The lookAt target moves forward on Z in lockstep with the camera position, maintaining a fixed LOOK_AHEAD offset.

**Rationale:** A fixed lookAt point (e.g., always looking at `[0, -2, -15]`) would cause the viewing angle to change dramatically as the camera moves — starting by looking slightly ahead/down, then looking nearly straight down as the camera passes over the target, then looking backward. This is disorienting and not the "glide" feel described in the seed. Co-moving lookAt produces a steady, consistent aerial vantage throughout the flight.

**Alternative considered:** lookAt that sweeps from ahead to below (fixed target). Rejected — too dramatic for a preset named "glide." A separate `flyover_sweep` preset could implement that variation if needed.

### D2: Fixed elevation (Y not scaled by speed)

**Decision:** Camera Y position is constant at `Y_CAMERA = 8` regardless of speed parameter.

**Rationale:** Speed semantically means "how far the camera flies" in the context of a flyover. Changing elevation would alter the fundamental character of the shot (high vs. low flyover), which is a different creative choice than "more/less motion." If elevation variants are needed, they should be separate presets or a future `elevation` parameter in CameraParams (backward-compatible extension per OBJ-006 — unrecognized fields are ignored).

### D3: No lateral (X-axis) motion

**Decision:** Camera stays at X=0 throughout.

**Rationale:** The flyover_glide is a straight-ahead aerial pass. Lateral drift would make it a different shot type (aerial tracking shot). An LLM author who wants lateral reframing can use `CameraParams.offset` to shift the camera laterally — the post-evaluate offset mechanism from OBJ-006 handles this cleanly without complicating the preset's internal math.

### D4: Default easing `ease_in_out`

**Decision:** The default easing is `ease_in_out`.

**Rationale:** Aerial shots benefit from gentle acceleration and deceleration. A linear flyover feels mechanical. `ease_in_out` produces a natural "takeoff cruise landing" rhythm. This aligns with TC-09 (eased paths preferred over linear). The easing is overridable via `CameraParams.easing`.

### D5: Static FOV (no animation)

**Decision:** FOV is constant at 50 degrees throughout the path.

**Rationale:** The aerial feel comes from elevation and forward motion, not from lens distortion. FOV animation on a flyover would compete with the spatial motion for the viewer's attention. Static FOV keeps the shot clean. If a dolly-zoom-over-landscape effect is wanted, the `dolly_zoom` preset (OBJ-034) is the appropriate tool.

### D6: Compatible only with `flyover` geometry

**Decision:** `compatibleGeometries` is `['flyover']` only.

**Rationale:** The elevated Y position of 8 and downward lookAt are specifically designed for the flyover geometry's ground-plane-below layout. Using this preset with a `tunnel` (walls at Y=+/-2) or `stage` (backdrop at Z=-30, subject at Z=-5) would produce nonsensical framing — the camera would be above the tunnel or looking down past the stage subject. Per OBJ-006 D6, compatibility is explicit and conservative. If future geometries are compatible (e.g., a `terrain` geometry), they must be explicitly added.

### D7: Viewing angle ~33.7 degrees below horizontal

**Decision:** The combination of `Y_CAMERA=8`, `Y_LOOK=-2`, `LOOK_AHEAD=15` produces a downward angle of approximately 33.7 degrees.

**Rationale:** This angle is shallow enough to see the horizon/distant elements (not a top-down surveillance view) but steep enough to clearly show the ground terrain (not a level flyby). It approximates a typical aerial establishing shot in documentary cinematography. The exact angle is subject to visual tuning in OBJ-062; these initial values are mathematically grounded starting points.

### D8: Inline arithmetic, no `lerp` import

**Decision:** The evaluate function uses inline `a + (b - a) * u` arithmetic rather than importing a `lerp` utility from OBJ-002.

**Rationale:** Linear interpolation is a single arithmetic expression. Importing a utility for it adds a dependency with no benefit. OBJ-002's interpolation utilities (`interpolate()`, easing functions) are consumed indirectly via `resolveCameraParams()` for easing resolution. The direct spatial interpolation is trivial and self-contained.

## Acceptance Criteria

### Contract Conformance (from OBJ-006)

- [ ] **AC-01:** `flyoverGlide` satisfies the `CameraPathPreset` interface from OBJ-006.
- [ ] **AC-02:** `flyoverGlide.name` is `'flyover_glide'` (lowercase snake_case).
- [ ] **AC-03:** `flyoverGlide.evaluate(0)` matches `flyoverGlide.defaultStartState` within 1e-6 per component.
- [ ] **AC-04:** `flyoverGlide.evaluate(1)` matches `flyoverGlide.defaultEndState` within 1e-6 per component.
- [ ] **AC-05:** `flyoverGlide.evaluate(t)` returns finite values (no NaN, no Infinity) for position, lookAt, and fov at 100 evenly-spaced sample points in [0, 1].
- [ ] **AC-06:** `flyoverGlide.evaluate(t).fov` equals 50 for all `t` in [0, 1] (static FOV).
- [ ] **AC-07:** `validateCameraPathPreset(flyoverGlide)` returns an empty array.
- [ ] **AC-08:** Calling `evaluate(t)` with the same `t` and same `params` 1000 times produces identical `CameraFrameState` each time (determinism, C-05).

### Spatial Behavior

- [ ] **AC-09:** `evaluate(0).position` is `[0, 8, 5]` — camera starts elevated and forward.
- [ ] **AC-10:** `evaluate(1).position` is `[0, 8, -25]` — camera ends elevated, 30 units further into the scene.
- [ ] **AC-11:** `evaluate(t).position[1]` (Y) equals 8 for all `t` — constant elevation.
- [ ] **AC-12:** `evaluate(t).position[0]` (X) equals 0 for all `t` — no lateral motion.
- [ ] **AC-13:** `evaluate(t).lookAt[1]` (Y) equals -2 for all `t` — lookAt always at ground level.
- [ ] **AC-14:** `evaluate(t).lookAt[0]` (X) equals 0 for all `t` — no lateral lookAt drift.
- [ ] **AC-15:** For all `t`, `evaluate(t).lookAt[2]` equals `evaluate(t).position[2] - 15` — lookAt Z tracks camera Z with constant 15-unit ahead offset (LOOK_AHEAD invariant).

### Speed Scaling

- [ ] **AC-16:** `evaluate(1, { speed: 0.5 }).position` is `[0, 8, -10]` — half Z displacement (5 + (-30 * 0.5) = -10).
- [ ] **AC-17:** `evaluate(1, { speed: 0.5 }).lookAt` is `[0, -2, -25]` — lookAt Z also half-scaled (-10 - 15 = -25).
- [ ] **AC-18:** `evaluate(t, { speed: 0.5 }).position[1]` equals 8 for all `t` — Y unaffected by speed.
- [ ] **AC-19:** `evaluate(t, { speed: 2.0 }).position[2]` interpolates from 5 to -55 (5 + (-30 * 2.0) = -55).

### Easing Override

- [ ] **AC-20:** `evaluate(0.5, { easing: 'linear' }).position[2]` equals `-10` (midpoint of 5 to -25 with linear easing: `5 + (-30) * 0.5 = -10`).
- [ ] **AC-21:** `evaluate(0.25).position[2]` differs from `evaluate(0.25, { easing: 'linear' }).position[2]` — the default `ease_in_out` produces a different eased value than linear at t=0.25 (symmetric ease_in_out(0.5) = 0.5 so the midpoint is not a useful test, but at t=0.25 the curves diverge).

### Metadata

- [ ] **AC-22:** `flyoverGlide.defaultEasing` is `'ease_in_out'`.
- [ ] **AC-23:** `flyoverGlide.compatibleGeometries` deep-equals `['flyover']`.
- [ ] **AC-24:** `flyoverGlide.oversizeRequirements.maxDisplacementX` is `0`.
- [ ] **AC-25:** `flyoverGlide.oversizeRequirements.maxDisplacementY` is `0`.
- [ ] **AC-26:** `flyoverGlide.oversizeRequirements.maxDisplacementZ` is `30`.
- [ ] **AC-27:** `flyoverGlide.oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-28:** `flyoverGlide.oversizeRequirements.recommendedOversizeFactor` is `>= 1.4` (initial value 1.4, subject to upward revision per AC-29).
- [ ] **AC-29:** `flyoverGlide.oversizeRequirements.recommendedOversizeFactor` is greater than or equal to the maximum per-plane oversize factor computed by OBJ-040 for all planes in the `flyover` geometry at speed=1.0. If OBJ-040 computes a required factor exceeding the current value, this preset's value MUST be updated.

### Registry Integration

- [ ] **AC-30:** After registration, `getCameraPath(registry, 'flyover_glide')` returns `flyoverGlide`.
- [ ] **AC-31:** After registration, `getCameraPathsForGeometry(registry, 'flyover')` includes `flyoverGlide`.
- [ ] **AC-32:** After registration, `getCameraPathsForGeometry(registry, 'tunnel')` does NOT include `flyoverGlide`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState` exactly (within 1e-6). |
| `t = 1` | Returns `defaultEndState` exactly (within 1e-6). |
| `t = 0.5` with default easing | Z position IS the arithmetic midpoint (-10) because symmetric `ease_in_out(0.5) = 0.5`. This is expected, not a bug. |
| `t = 0.25` with default easing | Z position differs from linear's value at t=0.25, because `ease_in_out(0.25) != 0.25`. |
| `t < 0` or `t > 1` | Undefined behavior per OBJ-006 contract. Callers must clamp. Implementer MAY clamp internally as safety measure. |
| `params = undefined` | Uses defaults: speed=1.0, easing=ease_in_out. Calls `resolveCameraParams(undefined, 'ease_in_out')`. |
| `params = {}` | Same as undefined — all defaults. |
| `speed = 0.5` | Z travel halved (15 units instead of 30). Y and lookAt angle unchanged. LOOK_AHEAD invariant preserved. |
| `speed = 2.0` | Z travel doubled (60 units). Camera reaches Z=-55. Ground plane and sky plane must be sized accordingly or OBJ-040 flags edge reveal risk. |
| `speed <= 0` | `resolveCameraParams` throws before evaluate logic runs. |
| `easing = 'linear'` | Overrides default ease_in_out. Camera moves at constant velocity. |
| `offset = [2, 0, 0]` | Applied by renderer post-evaluate. Camera shifts 2 units right. lookAt unchanged — creates slight rightward viewing angle. May reveal left edge of ground plane. |
| `offset = [0, -5, 0]` | Applied post-evaluate. Camera drops to effective Y=3. Still above ground (Y=-2) but much closer — dramatically changes the feel. This is valid but potentially surprising. |
| Very short scene (< 1s) | At 30fps, fewer than 30 frames. The eased motion may appear jumpy with few frames but remains mathematically correct. |
| Very long scene (> 30s) | The 30-unit Z travel spread over 30+ seconds produces very slow apparent motion. `speed > 1.0` can compensate. |

## Test Strategy

### Unit Tests

**Contract conformance suite** (reusable pattern from OBJ-006):
1. Boundary start/end: `evaluate(0)` and `evaluate(1)` match static states within 1e-6.
2. Continuity: 100 sample points, all finite.
3. FOV range: all samples equal 50.
4. Determinism: 100 repeated calls at same `t` produce identical output.
5. Full validation: `validateCameraPathPreset(flyoverGlide)` returns `[]`.
6. Speed scaling: max displacement at `speed=0.5` < max displacement at `speed=1.0`.
7. Easing override: `evaluate(0.25, { easing: 'linear' })` differs from `evaluate(0.25, { easing: 'ease_in' })` in position Z.

**Flyover-specific tests:**
1. **Constant elevation:** Sample 100 points; all `position[1] === 8`.
2. **Constant lateral:** Sample 100 points; all `position[0] === 0`.
3. **Monotonic Z forward:** For linearly spaced t values with linear easing, `position[2]` is strictly decreasing (camera moves into scene).
4. **LOOK_AHEAD invariant:** For all sampled t (and for `speed` values 0.5, 1.0, 2.0), `lookAt[2] === position[2] - 15`.
5. **lookAt Y constant:** All `lookAt[1] === -2`.
6. **Speed scaling Z only:** Compare `speed=0.5` and `speed=1.0` at t=1: Y identical, X identical, Z halved displacement.
7. **Speed does not affect lookAt Y:** At `speed=2.0`, `lookAt[1]` is still -2 for all t.

### Relevant Testable Claims

- **TC-04:** Manifest authors select `"camera": "flyover_glide"` — no XYZ coordinates needed.
- **TC-08:** This preset contributes to covering the `flyover` geometry in the design space.
- **TC-09:** Default `ease_in_out` can be A/B tested against `linear` via easing override.

### Visual Tuning (OBJ-062)

The spatial constants (`Y_CAMERA`, `Z_START`, `Z_END`, `Y_LOOK`, `LOOK_AHEAD`) are initial values derived from geometric reasoning. OBJ-062 will use the Director Agent workflow (Seed Section 10) to visually validate and tune these values. The constants are module-private named constants (not magic numbers) to facilitate easy adjustment during tuning rounds.

## Integration Points

### Depends on

| Dependency | What is imported |
|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `resolveCameraParams`, `OversizeRequirements` types and utilities. |
| **OBJ-002** (`src/interpolation/`) | Easing functions resolved indirectly via `resolveCameraParams()` which calls `getEasing()`. No direct `lerp` import — spatial interpolation is inline arithmetic. |
| **OBJ-003** (`src/spatial/types.ts`) | `Vec3` type for position and lookAt values. |

### Consumed by

| Downstream | How it uses OBJ-030 |
|---|---|
| **OBJ-062** (Visual tuning — flyover) | The preset to be visually tuned via Director Agent workflow. OBJ-062 depends on this preset existing and passing contract validation before tuning begins. |
| **Camera registry** | `flyoverGlide` is registered under key `'flyover_glide'`. Follow the registration pattern established by OBJ-026/OBJ-027 (see their `output.md` for the concrete barrel export / registry assembly approach). |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "flyover_glide"` from manifest, calls `evaluate(t, params)`. |
| **OBJ-040** (Edge-reveal validation) | Reads `oversizeRequirements` to compute minimum plane sizes for `flyover` geometry when this path is active. Validates that `recommendedOversizeFactor` is sufficient (see AC-29). |
| **OBJ-041** (Geometry-camera compatibility) | Reads `compatibleGeometries` to validate manifest scenes pairing `flyover_glide` with compatible geometries only. |
| **SKILL.md** (OBJ-071) | Documents this preset's visual effect, when to use it, and compatible geometries. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        flyover-glide.ts    # flyoverGlide export
```

The preset is registered into the camera path registry alongside other presets, following the pattern established by OBJ-026/OBJ-027.

## Open Questions

1. **Should `flyover_glide` also be compatible with `canyon` geometry?** A canyon has walls on both sides with a floor and open sky — an elevated flyover through a canyon could work cinematically. However, canyon walls at X=+/-4 and camera at Y=8 might look down over the walls rather than through the canyon. **Recommendation:** Defer. Start with `flyover` only. If OBJ-062 tuning reveals it works with `canyon`, add compatibility then.

2. **Should there be a slight Y descent during the flight?** A gentle Y decrease (e.g., from 8 to 6) would create a "descending approach" feel. This could be a separate preset (`flyover_descend`) or a parameter. **Recommendation:** Keep `flyover_glide` as constant-elevation for simplicity and predictability. A descending variant can be a separate preset if needed.

3. **Should LOOK_AHEAD scale with speed?** Currently it doesn't — at `speed=0.5` the camera covers less ground but still looks 15 units ahead. At `speed=2.0` it covers more ground but still looks only 15 ahead. This means the viewing angle is always ~33.7 degrees regardless of speed, which is consistent but means at high speeds the camera "looks closer to its feet" relative to its travel distance. **Recommendation:** Keep LOOK_AHEAD constant. The viewing angle is a property of the camera's vantage, not its velocity. Consistent angle is easier for blind authoring.
