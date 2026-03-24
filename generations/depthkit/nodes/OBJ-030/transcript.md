# Deliberation Transcript: OBJ-030

---

## Round 1 — spec_author

# Proposed Specification: OBJ-030 — Flyover Glide Camera Path Preset

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

These are the defining spatial values for the preset at `speed = 1.0`. They are not configurable via the manifest — they are baked into the preset and tuned during development (OBJ-062).

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `Y_CAMERA` | `8` | Elevated above ground plane. Flyover geometry places ground at approximately Y=-2; this gives ~10 units of clearance — high enough for aerial feel without losing ground detail. |
| `Z_START` | `5` | Camera starts slightly in front of origin, consistent with Three.js default camera convention. |
| `Z_END` | `-25` | 30 world-units of forward travel. Provides substantial forward motion for scenes up to ~15s without feeling rushed. |
| `Y_LOOK` | `-2` | lookAt Y target — at ground plane level. Creates the downward gaze angle. |
| `LOOK_AHEAD` | `15` | How far ahead of the camera (on Z) the lookAt target sits. lookAt Z tracks the camera's Z minus this offset, keeping the camera looking forward-and-down rather than straight down. |
| `FOV` | `50` | Static FOV. No FOV animation — the aerial feel comes from elevation and forward motion, not lens distortion. |

### Derived Motion

```
position(t) = [0, Y_CAMERA, lerp(Z_START, Z_END, eased(t))]
lookAt(t)   = [0, Y_LOOK,   lerp(Z_START - LOOK_AHEAD, Z_END - LOOK_AHEAD, eased(t))]
fov(t)      = FOV  (constant)
```

Where `eased(t)` applies the resolved easing function (default or overridden) to normalized time `t`, and `lerp(a, b, u) = a + (b - a) * u`.

The lookAt target moves in lockstep with the camera on Z (same interpolation, same easing), offset by `LOOK_AHEAD` units ahead. This maintains a constant downward viewing angle throughout the flight — approximately `atan2(Y_CAMERA - Y_LOOK, LOOK_AHEAD) ≈ atan2(10, 15) ≈ 33.7°` below horizontal.

### Speed Scaling

Per OBJ-006 D3, `speed` scales spatial amplitude, not temporal rate:

```
effective_z_displacement = (Z_END - Z_START) * speed = -30 * speed
position(t) = [0, Y_CAMERA, lerp(Z_START, Z_START + (Z_END - Z_START) * speed, eased(t))]
lookAt(t)   = [0, Y_LOOK,   lerp(Z_START - LOOK_AHEAD, Z_START - LOOK_AHEAD + (Z_END - Z_START) * speed, eased(t))]
```

At `speed = 0.5`: camera travels 15 units forward instead of 30. Same easing curve, same duration, less ground covered.

At `speed = 1.5`: camera travels 45 units forward. Greater risk of edge reveals — OBJ-040 must account for this.

**Y_CAMERA and Y_LOOK are NOT scaled by speed.** The elevation is a fixed property of the flyover vantage point. Speed controls how far the camera flies, not how high it flies.

**LOOK_AHEAD is NOT scaled by speed.** The viewing angle should remain consistent regardless of flight distance.

### Preset Definition

```typescript
export const flyoverGlide: CameraPathPreset = {
  name: 'flyover_glide',
  
  description: 'Bird\'s-eye aerial glide. Camera moves forward at elevated Y, looking down at the ground plane. Smooth, expansive feel suited to landscapes, cityscapes, and environmental establishing shots.',
  
  evaluate: /* implements the motion equations above using resolveCameraParams() */,
  
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
    maxDisplacementX: 0,      // No lateral motion
    maxDisplacementY: 0,      // Fixed elevation
    maxDisplacementZ: 30,     // |Z_END - Z_START| = 30
    fovRange: [50, 50],       // Static FOV
    recommendedOversizeFactor: 1.4,
  },
  
  tags: ['aerial', 'flyover', 'forward', 'birds_eye', 'glide', 'landscape'],
};
```

### Oversize Factor Derivation

The `recommendedOversizeFactor` of 1.4 is derived as follows:

The ground plane in a flyover geometry lies below the camera. As the camera moves forward, the visible area of the ground plane changes. The worst-case visible area occurs at the camera position closest to the ground plane's extent — typically the start position (z=5) looking ahead to z=-10.

For the ground plane (horizontal, at Y=-2), the camera views it at an oblique angle from Y=8. The visible footprint on the ground is larger than a perpendicular view would suggest due to the angle. The 1.4 factor provides a 40% margin over the base frustum size to account for:
1. The oblique viewing angle expanding the ground plane footprint
2. The full 30-unit Z travel at speed=1.0
3. Minor additional margin for safety

This is a conservative estimate. OBJ-040 will compute precise per-plane requirements using the displacement values. The scalar is a safe fallback.

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

**Decision:** FOV is constant at 50° throughout the path.

**Rationale:** The aerial feel comes from elevation and forward motion, not from lens distortion. FOV animation on a flyover would compete with the spatial motion for the viewer's attention. Static FOV keeps the shot clean. If a dolly-zoom-over-landscape effect is wanted, the `dolly_zoom` preset (OBJ-034) is the appropriate tool.

### D6: Compatible only with `flyover` geometry

**Decision:** `compatibleGeometries` is `['flyover']` only.

**Rationale:** The elevated Y position of 8 and downward lookAt are specifically designed for the flyover geometry's ground-plane-below layout. Using this preset with a `tunnel` (walls at Y=±2) or `stage` (backdrop at Z=-30, subject at Z=-5) would produce nonsensical framing — the camera would be above the tunnel or looking down past the stage subject. Per OBJ-006 D6, compatibility is explicit and conservative. If future geometries are compatible (e.g., a `terrain` geometry), they must be explicitly added.

### D7: Viewing angle ~33.7° below horizontal

**Decision:** The combination of `Y_CAMERA=8`, `Y_LOOK=-2`, `LOOK_AHEAD=15` produces a downward angle of approximately 33.7°.

**Rationale:** This angle is shallow enough to see the horizon/distant elements (not a top-down surveillance view) but steep enough to clearly show the ground terrain (not a level flyby). It approximates a typical aerial establishing shot in documentary cinematography. The exact angle is subject to visual tuning in OBJ-062; these initial values are mathematically grounded starting points.

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
- [ ] **AC-15:** For all `t`, `evaluate(t).lookAt[2]` equals `evaluate(t).position[2] - 15` — lookAt Z tracks camera Z with constant 15-unit ahead offset.

### Speed Scaling

- [ ] **AC-16:** `evaluate(1, { speed: 0.5 }).position` is `[0, 8, -10]` — half Z displacement (5 + (-30 * 0.5) = -10).
- [ ] **AC-17:** `evaluate(1, { speed: 0.5 }).lookAt` is `[0, -2, -25]` — lookAt Z also half-scaled (-10 - 15 = -25).
- [ ] **AC-18:** `evaluate(t, { speed: 0.5 }).position[1]` equals 8 for all `t` — Y unaffected by speed.
- [ ] **AC-19:** `evaluate(t, { speed: 2.0 }).position[2]` interpolates from 5 to -55 (5 + (-30 * 2.0) = -55).

### Easing Override

- [ ] **AC-20:** `evaluate(0.5, { easing: 'linear' }).position[2]` equals `-10` (midpoint of 5 to -25 with linear easing).
- [ ] **AC-21:** `evaluate(0.5).position[2]` is NOT `-10` (default `ease_in_out` produces a different midpoint than linear).

### Metadata

- [ ] **AC-22:** `flyoverGlide.defaultEasing` is `'ease_in_out'`.
- [ ] **AC-23:** `flyoverGlide.compatibleGeometries` deep-equals `['flyover']`.
- [ ] **AC-24:** `flyoverGlide.oversizeRequirements.maxDisplacementX` is `0`.
- [ ] **AC-25:** `flyoverGlide.oversizeRequirements.maxDisplacementY` is `0`.
- [ ] **AC-26:** `flyoverGlide.oversizeRequirements.maxDisplacementZ` is `30`.
- [ ] **AC-27:** `flyoverGlide.oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-28:** `flyoverGlide.oversizeRequirements.recommendedOversizeFactor` is `1.4`.
- [ ] **AC-29:** `flyoverGlide.tags` includes at least `'aerial'`, `'flyover'`, `'forward'`, and `'glide'`.

### Registry Integration

- [ ] **AC-30:** After registration, `getCameraPath(registry, 'flyover_glide')` returns `flyoverGlide`.
- [ ] **AC-31:** After registration, `getCameraPathsForGeometry(registry, 'flyover')` includes `flyoverGlide`.
- [ ] **AC-32:** After registration, `getCameraPathsForGeometry(registry, 'tunnel')` does NOT include `flyoverGlide`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState` exactly (within 1e-6). |
| `t = 1` | Returns `defaultEndState` exactly (within 1e-6). |
| `t = 0.5` with default easing | Z position is NOT the arithmetic midpoint of 5 and -25 due to `ease_in_out` curve. |
| `t < 0` or `t > 1` | Undefined behavior per OBJ-006 contract. Callers must clamp. Implementer MAY clamp internally as safety measure. |
| `params = undefined` | Uses defaults: speed=1.0, easing=ease_in_out. Calls `resolveCameraParams(undefined, 'ease_in_out')`. |
| `params = {}` | Same as undefined — all defaults. |
| `speed = 0.5` | Z travel halved (15 units instead of 30). Y and lookAt angle unchanged. |
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
1. Boundary start/end: `evaluate(0)` and `evaluate(1)` match static states.
2. Continuity: 100 sample points, all finite.
3. FOV range: all samples equal 50.
4. Determinism: 100 repeated calls at same `t` produce identical output.
5. Full validation: `validateCameraPathPreset(flyoverGlide)` returns `[]`.
6. Speed scaling: max displacement at `speed=0.5` < max displacement at `speed=1.0`.
7. Easing override: `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in position Z.

**Flyover-specific tests:**
1. **Constant elevation:** Sample 100 points; all `position[1] === 8`.
2. **Constant lateral:** Sample 100 points; all `position[0] === 0`.
3. **Monotonic Z forward:** For linearly spaced t values with linear easing, `position[2]` is strictly decreasing (camera moves into scene).
4. **lookAt offset invariant:** For all sampled t, `lookAt[2] === position[2] - 15`.
5. **lookAt Y constant:** All `lookAt[1] === -2`.
6. **Speed scaling Z only:** Compare `speed=0.5` and `speed=1.0` at t=1: Y identical, X identical, Z halved displacement.
7. **Speed does not affect lookAt Y:** At `speed=2.0`, `lookAt[1]` is still -2 for all t.

### Relevant Testable Claims

- **TC-04:** Manifest authors select `"camera": "flyover_glide"` — no XYZ coordinates needed.
- **TC-08:** This preset contributes to covering the `flyover` geometry in the design space.
- **TC-09:** Default `ease_in_out` can be A/B tested against `linear` via easing override.

### Visual Tuning (OBJ-062)

The spatial constants (`Y_CAMERA`, `Z_START`, `Z_END`, `Y_LOOK`, `LOOK_AHEAD`) are initial values derived from geometric reasoning. OBJ-062 will use the Director Agent workflow (Seed Section 10) to visually validate and tune these values. The constants should be implemented as named module-level constants (not magic numbers) to facilitate easy adjustment during tuning rounds.

## Integration Points

### Depends on

| Dependency | What is imported |
|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `resolveCameraParams`, `OversizeRequirements` types and utilities. |
| **OBJ-002** (`src/interpolation/`) | `lerp` or equivalent interpolation utility used internally by `evaluate()`. Easing functions resolved via `resolveCameraParams()` which calls `getEasing()`. |
| **OBJ-003** (`src/spatial/types.ts`) | `Vec3` type for position and lookAt values. |

### Consumed by

| Downstream | How it uses OBJ-030 |
|---|---|
| **OBJ-062** (Visual tuning — flyover) | The preset to be visually tuned via Director Agent workflow. OBJ-062 depends on this preset existing and passing contract validation before tuning begins. |
| **Camera registry** | `flyoverGlide` is registered under key `'flyover_glide'`. |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "flyover_glide"` from manifest, calls `evaluate(t, params)`. |
| **OBJ-040** (Edge-reveal validation) | Reads `oversizeRequirements` to compute minimum plane sizes for `flyover` geometry when this path is active. |
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

The preset is registered into the camera path registry alongside other presets. The exact registry assembly mechanism is determined by whatever pattern OBJ-026/027 established (likely a `presets/index.ts` barrel that collects all presets into a single registry object).

## Open Questions

1. **Should `flyover_glide` also be compatible with `canyon` geometry?** A canyon has walls on both sides with a floor and open sky — an elevated flyover through a canyon could work cinematically. However, canyon walls at X=±4 and camera at Y=8 might look down over the walls rather than through the canyon. **Recommendation:** Defer. Start with `flyover` only. If OBJ-062 tuning reveals it works with `canyon`, add compatibility then.

2. **Should there be a slight Y descent during the flight?** A gentle Y decrease (e.g., from 8 to 6) would create a "descending approach" feel. This could be a separate preset (`flyover_descend`) or a parameter. **Recommendation:** Keep `flyover_glide` as constant-elevation for simplicity and predictability. A descending variant can be a separate preset if needed.

3. **Should LOOK_AHEAD scale with speed?** Currently it doesn't — at `speed=0.5` the camera covers less ground but still looks 15 units ahead. At `speed=2.0` it covers more ground but still looks only 15 ahead. This means the viewing angle is always ~33.7° regardless of speed, which is consistent but means at high speeds the camera "looks closer to its feet" relative to its travel distance. **Recommendation:** Keep LOOK_AHEAD constant. The viewing angle is a property of the camera's vantage, not its velocity. Consistent angle is easier for blind authoring.

---

I believe this spec is complete and precise enough for implementation. I'd like the Challenger to verify the spatial math, the oversize factor derivation, the speed scaling behavior, and the completeness of acceptance criteria.

---

## Round 2 — spec_challenger

I've read the proposed spec carefully. It's well-structured and covers the core behavior clearly. I have a handful of issues to raise, mostly major, one critical.

---

## Points of Agreement

These are sound and I won't revisit them:

1. **Co-moving lookAt (D1)** — correct design for a "glide" feel. The constant viewing angle is well-reasoned.
2. **Fixed elevation (D2)** — Y not scaling with speed is the right call.
3. **No lateral motion (D3)** — clean separation; offset handles reframing.
4. **Static FOV (D5)** — appropriate for this preset.
5. **Compatible only with `flyover` (D6)** — conservative and correct per OBJ-006 D6.
6. **AC-01 through AC-08 (contract conformance)** — directly map to OBJ-006's conformance test pattern. Good.
7. **AC-09 through AC-15 (spatial behavior)** — precise, testable, cover the core invariants.
8. **Speed scaling ACs (AC-16 through AC-19)** — correct math, clearly testable.
9. **Edge cases table** — thorough for the most part.

---

## Issues

### Issue 1 (Major): `recommendedOversizeFactor` derivation is hand-wavy and possibly wrong

The spec says 1.4 and gives a qualitative rationale about "oblique viewing angle" and "40% margin." But the oversize factor should be derivable from the spatial parameters, and the derivation provided doesn't actually compute anything.

The camera is at Y=8 looking down at ~33.7°. It's viewing a *horizontal* ground plane, not a vertical plane. The standard frustum-size formula (`2 * d * tan(FOV/2)`) applies to planes perpendicular to the viewing direction. For an oblique ground plane, the visible footprint is stretched along the depth direction by `1/cos(angle)`. The visible footprint is substantially larger than a perpendicular view — and it changes as the camera moves 30 units forward.

The problem: an implementer reading "1.4" has no way to verify it's correct, and OBJ-040 (edge-reveal validation) will compute its own per-plane values from the displacement data anyway. So the scalar is supposed to be a *safe upper bound*, but there's no proof it actually is one.

**Proposed fix:** Either:
(a) Show the actual worst-case computation for the ground plane footprint and demonstrate 1.4 covers it, or
(b) State explicitly that the 1.4 value is an initial estimate subject to validation by OBJ-040 and refinement during OBJ-062 tuning — and add a note that if OBJ-040 computes a required factor > 1.4 for any plane in the `flyover` geometry, this value MUST be updated to match. Add an acceptance criterion: "AC-XX: `recommendedOversizeFactor` >= the maximum per-plane oversize factor computed by OBJ-040 for all planes in the `flyover` geometry at speed=1.0."

I prefer option (b) because the precise computation depends on the flyover geometry's plane layout (OBJ-021), which this spec shouldn't hardcode knowledge of.

### Issue 2 (Major): The spec doesn't specify what `lerp` is imported or how it's used

The "Derived Motion" section uses `lerp(a, b, u)` and defines it inline as `a + (b - a) * u`. But in the "Depends on" table, it says OBJ-002 provides `lerp or equivalent interpolation utility`. 

OBJ-006's spec says presets use `resolveCameraParams()` which gives them an easing function, and that presets use OBJ-002 utilities internally. But the spec doesn't confirm that OBJ-002 actually exports a `lerp` function by that name. If it exports `interpolate()` with a different signature (as shown in the seed's Section 8.5 — `interpolate(frame, inputRange, outputRange, easing)`), the implementer needs to know which function to use and how.

**Proposed fix:** Either:
(a) Specify that the implementation uses a simple `a + (b - a) * u` computation inline (it's one line, no import needed), making the OBJ-002 dependency for `lerp` unnecessary, or
(b) Pin the exact function name and signature from OBJ-002 that will be used.

Option (a) is cleaner — `lerp` is trivial and doesn't warrant a dependency.

### Issue 3 (Major): Speed scaling on lookAt Z is specified but not obviously correct in the equations

The "Speed Scaling" section shows:
```
lookAt(t) = [0, Y_LOOK, lerp(Z_START - LOOK_AHEAD, Z_START - LOOK_AHEAD + (Z_END - Z_START) * speed, eased(t))]
```

Let me verify AC-17: at `speed=0.5`, `t=1`, eased(1)=1:
- lookAt Z = `Z_START - LOOK_AHEAD + (Z_END - Z_START) * speed` = `5 - 15 + (-30) * 0.5` = `-10 - 15` = `-25` ✓

And the position Z at t=1, speed=0.5: `5 + (-30) * 0.5 = -10` ✓
So `lookAt[2] - position[2] = -25 - (-10) = -15` ✓ — the LOOK_AHEAD invariant holds.

Math checks out. But the equations in the "Speed Scaling" section are harder to read than they need to be. The implementer needs to see clearly that the LOOK_AHEAD invariant (`lookAt[2] = position[2] - LOOK_AHEAD`) holds for ALL speed values, not just speed=1.0.

**Proposed fix:** Add one sentence after the speed-scaling equations: "Note: the LOOK_AHEAD invariant (`lookAt[2] === position[2] - LOOK_AHEAD`) holds for all `speed` values because both position and lookAt Z use the same base displacement `(Z_END - Z_START) * speed` with the same easing." This makes the invariant obviously preserved rather than requiring the reader to verify algebraically.

### Issue 4 (Minor): AC-20 assumes specific easing behavior at t=0.5

AC-20 states: `evaluate(0.5, { easing: 'linear' }).position[2]` equals `-10`.

Let me verify: with linear easing, eased(0.5) = 0.5. `lerp(5, -25, 0.5) = 5 + (-30)(0.5) = -10` ✓

AC-21 states: `evaluate(0.5).position[2]` is NOT `-10`. This is correct for `ease_in_out` since eased(0.5) ≠ 0.5... wait. Actually, for symmetric ease-in-out functions, `eased(0.5)` is typically exactly `0.5`. The standard cubic ease-in-out `3t² - 2t³` at t=0.5 gives `3(0.25) - 2(0.125) = 0.75 - 0.25 = 0.5`. So AC-21 would *fail* — `ease_in_out(0.5) = 0.5` for all standard symmetric implementations, meaning the position at the midpoint IS `-10`.

**This is a critical issue.** AC-21 as stated is **wrong** and would cause a correct implementation to fail the acceptance test.

**Proposed fix:** Remove AC-21 entirely, or change it to test at a non-midpoint where ease_in_out diverges from linear, e.g.: "AC-21: `evaluate(0.25).position[2]` differs from `evaluate(0.25, { easing: 'linear' }).position[2]`." At t=0.25, linear gives eased=0.25, but ease_in_out gives a different value (for cubic: `3(0.0625) - 2(0.015625) = 0.1875 - 0.03125 = 0.15625 ≠ 0.25`).

### Issue 5 (Minor): No mention of module-level constant naming convention

D7 says the viewing angle values are "subject to visual tuning in OBJ-062" and the test strategy section says "constants should be implemented as named module-level constants." But the spec doesn't name them consistently with a convention. The "Spatial Parameters" table uses `Y_CAMERA`, `Z_START`, etc. — are these the actual exported constant names? Are they exported at all (for testing)? Or are they private implementation details?

**Proposed fix:** State explicitly: "The spatial constants (`Y_CAMERA`, `Z_START`, `Z_END`, `Y_LOOK`, `LOOK_AHEAD`, `FOV`) are module-private named constants (not exported). They are tested indirectly via `defaultStartState`, `defaultEndState`, and the spatial behavior acceptance criteria. OBJ-062 modifies them in-source during tuning."

### Issue 6 (Minor): Missing guidance on registry integration pattern

AC-30 says "After registration, `getCameraPath(registry, 'flyover_glide')` returns `flyoverGlide`." The file placement section says "The exact registry assembly mechanism is determined by whatever pattern OBJ-026/027 established." 

This is fine for now, but if OBJ-026/027 hasn't established that pattern yet (they're verified, so presumably they have), the implementer might not know whether to add to an existing barrel file, call a registration function, etc.

**Proposed fix:** Since OBJ-026 and OBJ-027 are both verified, add a note: "Follow the registration pattern established by OBJ-026/OBJ-027 (see their `output.md` for the concrete barrel export / registry assembly approach)."

---

## Summary of Required Changes

| # | Severity | Issue | Required Action |
|---|----------|-------|-----------------|
| 1 | Major | Oversize factor unverified | Add caveat that 1.4 is initial estimate, add AC requiring it >= OBJ-040's computed max |
| 2 | Major | `lerp` dependency unclear | Clarify: inline computation, no OBJ-002 dependency for lerp |
| 3 | Major | LOOK_AHEAD invariant under speed not stated explicitly | Add clarifying sentence |
| 4 | **Critical** | AC-21 is wrong — symmetric ease_in_out(0.5) = 0.5 | Fix test point to t=0.25 or remove |
| 5 | Minor | Constant export/visibility unspecified | State they're module-private |
| 6 | Minor | Registry pattern reference missing | Point to OBJ-026/027 output.md |

I need issues 1-4 addressed before I'll converge. Issues 5-6 can be addressed or documented as minor notes in the spec.

---

## Round 3 — spec_author

# Revised Specification: OBJ-030 — Flyover Glide Camera Path Preset

All six issues are addressed below. I'll call out each fix inline for easy verification.

---

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

These are the defining spatial values for the preset at `speed = 1.0`. They are **module-private named constants** (not exported). They are tested indirectly via `defaultStartState`, `defaultEndState`, and the spatial behavior acceptance criteria. OBJ-062 modifies them in-source during visual tuning rounds. **(Issue 5 fix)**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `Y_CAMERA` | `8` | Elevated above ground plane. Flyover geometry places ground at approximately Y=-2; this gives ~10 units of clearance — high enough for aerial feel without losing ground detail. |
| `Z_START` | `5` | Camera starts slightly in front of origin, consistent with Three.js default camera convention. |
| `Z_END` | `-25` | 30 world-units of forward travel. Provides substantial forward motion for scenes up to ~15s without feeling rushed. |
| `Y_LOOK` | `-2` | lookAt Y target — at ground plane level. Creates the downward gaze angle. |
| `LOOK_AHEAD` | `15` | How far ahead of the camera (on Z) the lookAt target sits. lookAt Z tracks the camera's Z minus this offset, keeping the camera looking forward-and-down rather than straight down. |
| `FOV` | `50` | Static FOV. No FOV animation — the aerial feel comes from elevation and forward motion, not lens distortion. |

### Derived Motion

The evaluate function computes position and lookAt using inline linear interpolation (`a + (b - a) * u`) — no external `lerp` import is needed since this is a single arithmetic expression. **(Issue 2 fix)**

```
eased_t    = easingFn(t)    // resolved via resolveCameraParams()

position(t) = [0, Y_CAMERA, Z_START + (Z_END - Z_START) * eased_t]
lookAt(t)   = [0, Y_LOOK,   (Z_START - LOOK_AHEAD) + (Z_END - Z_START) * eased_t]
fov(t)      = FOV  (constant)
```

The lookAt target moves in lockstep with the camera on Z (same interpolation, same easing), offset by `LOOK_AHEAD` units ahead. This maintains a constant downward viewing angle throughout the flight — approximately `atan2(Y_CAMERA - Y_LOOK, LOOK_AHEAD) ≈ atan2(10, 15) ≈ 33.7°` below horizontal.

**LOOK_AHEAD invariant under speed:** The invariant `lookAt[2] === position[2] - LOOK_AHEAD` holds for all `speed` values because both position Z and lookAt Z use the same base displacement `(Z_END - Z_START) * speed` with the same easing. The `LOOK_AHEAD` constant is subtracted from the lookAt's base point, not from the displacement term, so speed scaling cancels out in the difference. **(Issue 3 fix)**

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

### Oversize Factor: Initial Estimate with Validation Gate **(Issue 1 fix)**

The `recommendedOversizeFactor` of **1.4** is an initial estimate, not a derivation from first principles. The rationale for this starting value:

- The camera views the ground plane at an oblique angle (~33.7° below horizontal). The visible footprint on a horizontal plane is stretched along the depth direction relative to a perpendicular view.
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

**Decision:** FOV is constant at 50° throughout the path.

**Rationale:** The aerial feel comes from elevation and forward motion, not from lens distortion. FOV animation on a flyover would compete with the spatial motion for the viewer's attention. Static FOV keeps the shot clean. If a dolly-zoom-over-landscape effect is wanted, the `dolly_zoom` preset (OBJ-034) is the appropriate tool.

### D6: Compatible only with `flyover` geometry

**Decision:** `compatibleGeometries` is `['flyover']` only.

**Rationale:** The elevated Y position of 8 and downward lookAt are specifically designed for the flyover geometry's ground-plane-below layout. Using this preset with a `tunnel` (walls at Y=±2) or `stage` (backdrop at Z=-30, subject at Z=-5) would produce nonsensical framing — the camera would be above the tunnel or looking down past the stage subject. Per OBJ-006 D6, compatibility is explicit and conservative. If future geometries are compatible (e.g., a `terrain` geometry), they must be explicitly added.

### D7: Viewing angle ~33.7° below horizontal

**Decision:** The combination of `Y_CAMERA=8`, `Y_LOOK=-2`, `LOOK_AHEAD=15` produces a downward angle of approximately 33.7°.

**Rationale:** This angle is shallow enough to see the horizon/distant elements (not a top-down surveillance view) but steep enough to clearly show the ground terrain (not a level flyby). It approximates a typical aerial establishing shot in documentary cinematography. The exact angle is subject to visual tuning in OBJ-062; these initial values are mathematically grounded starting points.

### D8: Inline arithmetic, no `lerp` import **(Issue 2 fix)**

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

- [ ] **AC-16:** `evaluate(1, { speed: 0.5 }).position` is `[0, 8, -10]` — half Z displacement (5 + (-30 × 0.5) = -10).
- [ ] **AC-17:** `evaluate(1, { speed: 0.5 }).lookAt` is `[0, -2, -25]` — lookAt Z also half-scaled (-10 - 15 = -25).
- [ ] **AC-18:** `evaluate(t, { speed: 0.5 }).position[1]` equals 8 for all `t` — Y unaffected by speed.
- [ ] **AC-19:** `evaluate(t, { speed: 2.0 }).position[2]` interpolates from 5 to -55 (5 + (-30 × 2.0) = -55).

### Easing Override **(Issue 4 fix)**

- [ ] **AC-20:** `evaluate(0.5, { easing: 'linear' }).position[2]` equals `-10` (midpoint of 5 to -25 with linear easing: `5 + (-30) × 0.5 = -10`).
- [ ] **AC-21:** `evaluate(0.25).position[2]` differs from `evaluate(0.25, { easing: 'linear' }).position[2]` — the default `ease_in_out` produces a different eased value than linear at t=0.25 (symmetric ease_in_out(0.5) = 0.5 so the midpoint is not a useful test, but at t=0.25 the curves diverge).

### Metadata

- [ ] **AC-22:** `flyoverGlide.defaultEasing` is `'ease_in_out'`.
- [ ] **AC-23:** `flyoverGlide.compatibleGeometries` deep-equals `['flyover']`.
- [ ] **AC-24:** `flyoverGlide.oversizeRequirements.maxDisplacementX` is `0`.
- [ ] **AC-25:** `flyoverGlide.oversizeRequirements.maxDisplacementY` is `0`.
- [ ] **AC-26:** `flyoverGlide.oversizeRequirements.maxDisplacementZ` is `30`.
- [ ] **AC-27:** `flyoverGlide.oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-28:** `flyoverGlide.oversizeRequirements.recommendedOversizeFactor` is `>= 1.4` (initial value 1.4, subject to upward revision per AC-29).
- [ ] **AC-29:** `flyoverGlide.oversizeRequirements.recommendedOversizeFactor` is greater than or equal to the maximum per-plane oversize factor computed by OBJ-040 for all planes in the `flyover` geometry at speed=1.0. If OBJ-040 computes a required factor exceeding the current value, this preset's value MUST be updated. **(Issue 1 fix)**

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
| `t = 0.25` with default easing | Z position differs from linear's midpoint at t=0.25, because `ease_in_out(0.25) ≠ 0.25`. |
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
| **Camera registry** | `flyoverGlide` is registered under key `'flyover_glide'`. Follow the registration pattern established by OBJ-026/OBJ-027 (see their `output.md` for the concrete barrel export / registry assembly approach). **(Issue 6 fix)** |
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

1. **Should `flyover_glide` also be compatible with `canyon` geometry?** A canyon has walls on both sides with a floor and open sky — an elevated flyover through a canyon could work cinematically. However, canyon walls at X=±4 and camera at Y=8 might look down over the walls rather than through the canyon. **Recommendation:** Defer. Start with `flyover` only. If OBJ-062 tuning reveals it works with `canyon`, add compatibility then.

2. **Should there be a slight Y descent during the flight?** A gentle Y decrease (e.g., from 8 to 6) would create a "descending approach" feel. This could be a separate preset (`flyover_descend`) or a parameter. **Recommendation:** Keep `flyover_glide` as constant-elevation for simplicity and predictability. A descending variant can be a separate preset if needed.

3. **Should LOOK_AHEAD scale with speed?** Currently it doesn't — at `speed=0.5` the camera covers less ground but still looks 15 units ahead. At `speed=2.0` it covers more ground but still looks only 15 ahead. This means the viewing angle is always ~33.7° regardless of speed, which is consistent but means at high speeds the camera "looks closer to its feet" relative to its travel distance. **Recommendation:** Keep LOOK_AHEAD constant. The viewing angle is a property of the camera's vantage, not its velocity. Consistent angle is easier for blind authoring.

---

## Changes Summary

| Issue # | Severity | Fix Applied |
|---------|----------|-------------|
| 1 | Major | Oversize factor reframed as initial estimate; added AC-29 requiring it >= OBJ-040's computed max; added explicit caveat in new "Oversize Factor" section |
| 2 | Major | Changed to inline arithmetic; removed `lerp` as OBJ-002 dependency; added D8 design decision; updated "Depends on" table |
| 3 | Major | Added explicit paragraph in "Derived Motion" section proving LOOK_AHEAD invariant holds under speed scaling; updated LOOK_AHEAD-specific test to cover multiple speed values |
| 4 | **Critical** | AC-21 changed from t=0.5 to t=0.25; added note in edge cases that `ease_in_out(0.5) = 0.5` is expected behavior, not a bug |
| 5 | Minor | Added statement that constants are module-private, tested indirectly |
| 6 | Minor | Added explicit reference to OBJ-026/OBJ-027 registration pattern in "Consumed by" table |

---

I believe all six issues are fully addressed. Challenger, please verify and approve if satisfied.

---

## Round 4 — spec_challenger

I've carefully verified all six fixes against my original objections:

**Issue 1 (Major) — Oversize factor:** ✓ New "Oversize Factor: Initial Estimate with Validation Gate" section correctly frames 1.4 as an estimate. AC-28 changed to `>= 1.4`. AC-29 adds the OBJ-040 cross-validation gate. Structurally present and correct.

**Issue 2 (Major) — `lerp` dependency:** ✓ "Derived Motion" section states inline arithmetic. D8 added. "Depends on" table updated. No phantom dependency.

**Issue 3 (Major) — LOOK_AHEAD invariant:** ✓ Explicit paragraph in "Derived Motion" proves the invariant algebraically. Flyover-specific test #4 updated to cover speed values 0.5, 1.0, 2.0.

**Issue 4 (Critical) — AC-21 wrong:** ✓ Changed to t=0.25. Edge cases table notes `ease_in_out(0.5) = 0.5` is expected. Let me re-verify the math: cubic ease_in_out at t=0.25 gives `3(0.0625) - 2(0.015625) = 0.15625`, which ≠ 0.25 (linear). So position Z with ease_in_out at t=0.25 = `5 + (-30)(0.15625) = 0.3125`, while linear gives `5 + (-30)(0.25) = -2.5`. These differ. ✓ Correct.

**Issue 5 (Minor) — Constant visibility:** ✓ Explicit statement added.

**Issue 6 (Minor) — Registry pattern:** ✓ Reference to OBJ-026/OBJ-027 added.

No new issues introduced by the revisions. The spec is clean, precise, and implementable.

CONCLUSION:

The specification for OBJ-030 (Flyover Glide Camera Path Preset) is complete and approved. It defines the `flyover_glide` camera path preset — an elevated aerial glide with constant Y=8, forward Z motion from 5 to -25, co-moving lookAt maintaining a 15-unit ahead offset and ~33.7° downward angle. All spatial parameters, speed scaling behavior, easing defaults, oversize requirements, and compatibility metadata are precisely specified. The spec conforms to the OBJ-006 `CameraPathPreset` contract with 32 testable acceptance criteria.

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me first check the current state of the meta.json and find the project root.
[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-030/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-030",
     3→  "description": "Flyover glide camera path preset -- camera moves forward on Z while positioned above the ground plane (elevated Y), looking slightly downward. Bird's-eye aerial movement feel. Defines position(t), lookAt(t), easing defaults, compatible geometries (flyover), and oversizing requirements.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Geometry-specific preset for flyover."
    12→}
    13→
Good. Now let me write both files.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md",
  "content": "# Specification: OBJ-030 \u2014 Flyover Glide Camera Path Preset\n\n## Summary\n\nOBJ-030 defines the `flyover_glide` camera path preset \u2014 a bird's-eye aerial movement where the camera is positioned at elevated Y, moves forward along the Z-axis, and looks slightly downward throughout. This preset conforms to the `CameraPathPreset` contract from OBJ-006 and is designed primarily for the `flyover` scene geometry. It produces the feel of gliding over a landscape, looking ahead and down at the terrain below.\n\n## Interface Contract\n\n### Preset Export\n\n```typescript\n// src/camera/presets/flyover-glide.ts\n\nimport { CameraPathPreset } from '../types';\n\n/**\n * The flyover_glide camera path preset.\n * Conforms to CameraPathPreset (OBJ-006).\n */\nexport const flyoverGlide: CameraPathPreset;\n```\n\n### Spatial Parameters (Constants)\n\nThese are the defining spatial values for the preset at `speed = 1.0`. They are **module-private named constants** (not exported). They are tested indirectly via `defaultStartState`, `defaultEndState`, and the spatial behavior acceptance criteria. OBJ-062 modifies them in-source during visual tuning rounds.\n\n| Parameter | Value | Rationale |\n|-----------|-------|-----------|\n| `Y_CAMERA` | `8` | Elevated above ground plane. Flyover geometry places ground at approximately Y=-2; this gives ~10 units of clearance \u2014 high enough for aerial feel without losing ground detail. |\n| `Z_START` | `5` | Camera starts slightly in front of origin, consistent with Three.js default camera convention. |\n| `Z_END` | `-25` | 30 world-units of forward travel. Provides substantial forward motion for scenes up to ~15s without feeling rushed. |\n| `Y_LOOK` | `-2` | lookAt Y target \u2014 at ground plane level. Creates the downward gaze angle. |\n| `LOOK_AHEAD` | `15` | How far ahead of the camera (on Z) the lookAt 
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/meta.json",
  "content": "{\n  \"id\": \"OBJ-030\",\n  \"description\": \"Flyover glide camera path preset -- camera moves forward on Z while positioned above the ground plane (elevated Y), looking slightly downward. Bird's-eye aerial movement feel. Defines position(t), lookAt(t), easing defaults, compatible geometries (flyover), and oversizing requirements.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:00:00Z\",\n  \"depends_on\": [\"OBJ-006\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 camera path. Geometry-specific preset for flyover. Spec completed via 4-round deliberation.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/meta.json has been updated successfully.
Now let me commit:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-030/output.md nodes/OBJ-030/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-030): flyover_glide camera path preset specification\n\nDefines the flyover_glide preset \u2014 elevated Y camera gliding forward\non Z-axis with constant downward lookAt angle (~33.7\u00b0). Includes\nspatial parameters, speed scaling behavior, oversize requirements,\nand 32 acceptance criteria. Compatible with flyover geometry only.\n\nDeliberation resolved: oversize factor validation gate (AC-29),\ninline arithmetic over lerp import, LOOK_AHEAD invariant proof,\ncorrected easing test point from t=0.5 to t=0.25.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-030 spec files"
}
[Tool Result] [master 55e99d9] spec(OBJ-030): flyover_glide camera path preset specification
 2 files changed, 323 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-030/output.md
The specification for OBJ-030 has been written and committed. Here's a summary of what was agreed:

**OBJ-030 — Flyover Glide Camera Path Preset** defines `flyover_glide`, a bird's-eye aerial camera path that:

- Maintains constant elevation at Y=8, looking down at Y=-2 with a 15-unit look-ahead offset (~33.7° below horizontal)
- Moves forward on Z from 5 to -25 (30 world-units of travel at speed=1.0)
- Uses `ease_in_out` default easing for natural acceleration/deceleration
- Has static FOV at 50°, no lateral motion
- Is compatible only with the `flyover` geometry

**Key deliberation outcomes (4 rounds):**
1. Oversize factor (1.4) reframed as initial estimate with AC-29 validation gate against OBJ-040
2. Spatial interpolation uses inline arithmetic — no `lerp` dependency on OBJ-002
3. LOOK_AHEAD invariant (`lookAt[2] === position[2] - 15`) proven to hold under all speed values
4. AC-21 easing test corrected from t=0.5 to t=0.25 (symmetric ease_in_out(0.5)=0.5 makes midpoint useless for distinguishing easings)
