# Deliberation Transcript: OBJ-031

---

## Round 1 — spec_author

# Specification: OBJ-031 — Gentle Float Camera Path Preset

## Summary

OBJ-031 defines the `gentle_float` camera path preset — a very slow, subtle multi-axis drift that produces an almost subliminal sense of life in otherwise static scenes. It is the universal ambient preset, compatible with most scene geometries, and designed for moments where camera motion should be felt rather than noticed. The preset implements the `CameraPathPreset` interface from OBJ-006 using incommensurate sinusoidal oscillations across X, Y, and Z axes to create organic, non-repeating drift within a single scene duration.

## Interface Contract

### Exported Preset

```typescript
// src/camera/presets/gentle_float.ts

import { CameraPathPreset } from '../types';

/**
 * The gentle_float camera path preset.
 * 
 * Produces very slow, subtle movement across all three axes using
 * incommensurate sinusoidal oscillations. The motion is designed to
 * feel organic and non-repeating within typical scene durations (5–30s).
 * 
 * At speed=1.0, the camera drifts within a small spatial envelope:
 *   X: ±0.3 world units
 *   Y: ±0.2 world units
 *   Z: ±0.4 world units (centered on start position)
 * 
 * lookAt target drifts with dampened, phase-offset oscillations to
 * create subtle gaze wander rather than a fixed stare point.
 * 
 * FOV is static at 50°.
 */
export const gentleFloat: CameraPathPreset;
```

### Motion Model

The motion model uses **three independent sinusoidal oscillations per output channel** (position X/Y/Z, lookAt X/Y/Z), each with carefully chosen frequencies and phases. The key mathematical properties:

#### Position Oscillation

```
position.x(t) = startX + amplitudeX * speed * sin(2π * freqX * t + phaseX)
position.y(t) = startY + amplitudeY * speed * sin(2π * freqY * t + phaseY)
position.z(t) = startZ + amplitudeZ * speed * sin(2π * freqZ * t + phaseZ)
```

Where:
- `t` is normalized time `[0, 1]`
- `speed` is from `ResolvedCameraParams.speed` (amplitude multiplier per OBJ-006 D3)
- Easing is **not applied to the primary oscillation** (see Design Decision D2)

#### Default Parameters

| Parameter | X-axis | Y-axis | Z-axis |
|-----------|--------|--------|--------|
| Amplitude (world units) | 0.3 | 0.2 | 0.4 |
| Frequency (cycles per normalized t) | 0.7 | 1.1 | 0.5 |
| Phase offset (radians) | 0 | π/3 | 2π/5 |

#### LookAt Oscillation

The lookAt target also drifts, but with **smaller amplitudes and different frequencies** to create subtle gaze wander:

| Parameter | X-axis | Y-axis | Z-axis |
|-----------|--------|--------|--------|
| Amplitude (world units) | 0.15 | 0.1 | 0.2 |
| Frequency (cycles per normalized t) | 0.9 | 0.6 | 0.4 |
| Phase offset (radians) | π/4 | π/6 | π/2 |

The lookAt amplitudes are **not scaled by `speed`**. Rationale: at low speed values, the camera barely moves — if lookAt also stopped drifting, the preset would collapse to `static`. Keeping lookAt drift independent preserves a subtle sense of life even at `speed: 0.3`.

#### Start/End State Continuity

Because sinusoidal functions do not generally return to their starting value at t=1, the evaluate function must apply a **fade envelope** that forces the motion to begin and end at rest:

```
envelope(t) = sin(π * t)
```

This produces zero displacement at t=0 and t=1, with full amplitude at t=0.5. The effective position becomes:

```
position.x(t) = startX + amplitudeX * speed * sin(2π * freqX * t + phaseX) * envelope(t)
```

This ensures:
- `evaluate(0)` exactly equals `defaultStartState`
- `evaluate(1)` exactly equals `defaultEndState` (which equals `defaultStartState` since the camera returns to its origin)
- No discontinuity at scene boundaries when transitioning

#### Default Camera Position

```
startPosition = [0, 0, 5]
startLookAt   = [0, 0, 0]
fov           = 50  (static, no animation)
```

These match the Three.js camera defaults from Seed Section 8.1–8.2. The gentle_float is geometry-agnostic — geometries place planes relative to the camera's start position, so the default `[0, 0, 5]` works universally.

### Preset Definition (Static Fields)

```typescript
{
  name: 'gentle_float',
  
  description: 'Very slow, subtle drift in all three axes. Almost subliminal. ' +
    'Creates a sense of life without drawing attention to camera movement. ' +
    'Good for ambient scenes, close-ups, and any geometry where stillness ' +
    'would feel lifeless.',
  
  // evaluate: <implementation per motion model above>
  
  defaultStartState: {
    position: [0, 0, 5],
    lookAt: [0, 0, 0],
    fov: 50,
  },
  
  defaultEndState: {
    position: [0, 0, 5],   // Returns to start (envelope forces convergence)
    lookAt: [0, 0, 0],     // Returns to start
    fov: 50,
  },
  
  defaultEasing: 'linear',  // See D2: easing is not meaningful for this preset
  
  compatibleGeometries: [
    'stage',
    'tunnel',
    'canyon',
    'flyover',
    'diorama',
    'portal',
    'panorama',
    'close_up',
  ],
  
  oversizeRequirements: {
    maxDisplacementX: 0.3,   // amplitude_X at speed=1.0
    maxDisplacementY: 0.2,   // amplitude_Y at speed=1.0
    maxDisplacementZ: 0.4,   // amplitude_Z at speed=1.0
    fovRange: [50, 50],      // No FOV animation
    recommendedOversizeFactor: 1.05,  // See D4
  },
  
  tags: ['ambient', 'subtle', 'float', 'drift', 'gentle', 'universal'],
}
```

## Design Decisions

### D1: Incommensurate Sinusoidal Frequencies

**Decision:** Use sinusoidal oscillations with frequencies that are not integer multiples of each other (0.7, 1.1, 0.5 for position; 0.9, 0.6, 0.4 for lookAt).

**Rationale:** If frequencies were commensurate (e.g., 1.0, 2.0, 3.0), the motion would produce a recognizable repeating pattern — the camera would trace the same path predictably. Incommensurate frequencies create quasi-periodic motion that never exactly repeats within a scene duration, producing a more organic, "breathing" quality. This is a standard technique in procedural animation (used in ocean wave simulation, foliage sway, etc.).

**Trade-off:** Incommensurate frequencies mean the camera does not naturally return to its start position at t=1. This is solved by the `sin(π * t)` fade envelope (see D3).

**Alternative considered:** Perlin/simplex noise for position. Rejected because: (a) noise requires either a library dependency or a non-trivial implementation, (b) noise output is harder to bound precisely for oversizing requirements, and (c) sinusoids are deterministic by construction (C-05) without needing to manage seeds.

### D2: Easing Override Has Minimal Effect

**Decision:** The `defaultEasing` is `linear`, and easing overrides from `CameraParams.easing` are accepted but applied only to the **envelope**, not to the sinusoidal oscillations themselves.

**Rationale:** The gentle_float motion model is fundamentally oscillatory, not interpolatory. Easing functions are designed for start-to-end interpolation — they map `[0,1] → [0,1]` monotonically. Applying easing to the sinusoidal phase would distort the oscillation frequencies in non-physical ways (bunching waves together at one end). Instead, easing is applied to the fade envelope:

```
envelope(t) = sin(π * easing(t))
```

This means:
- `linear` easing → symmetric fade in/out (default, most natural)
- `ease_in` → slow start, the drift takes longer to reach full amplitude
- `ease_out` → quick start, the drift reaches full amplitude early and fades slowly
- `ease_in_out` → similar to linear for this application but slightly more weighted toward the center

This preserves the OBJ-006 contract (easing overrides are respected) while maintaining physically plausible motion. The SKILL.md should note that easing has subtle effect on this preset.

### D3: Fade Envelope for Start/End Continuity

**Decision:** Apply `sin(π * t)` envelope to all oscillations so the camera starts and ends at rest.

**Rationale:** OBJ-006 requires `evaluate(0) === defaultStartState` and `evaluate(1) === defaultEndState`. Without an envelope, the sinusoidal values at t=0 would depend on phase offsets — phases would need to be chosen so that `sin(phase) = 0` for all axes, which constrains the creative space. The multiplicative envelope is cleaner: it zeros out displacement at boundaries regardless of phase, while preserving the organic feel in the middle of the scene.

**Consequence:** `defaultEndState === defaultStartState`. The camera returns to its origin. This is ideal for scene transitions — the camera is at a known, predictable position at scene boundaries.

### D4: Recommended Oversize Factor of 1.05

**Decision:** `recommendedOversizeFactor: 1.05` (5% oversize).

**Rationale:** The maximum displacement at speed=1.0 is 0.4 world units (Z-axis). At the default camera position of z=5, the nearest plane in most geometries is the `subject` at approximately z=-5 (distance=10 units). The visible height at distance 10 with FOV=50° is `2 * 10 * tan(25°) ≈ 9.33` units. A 0.4-unit camera displacement at this distance shifts the visible area by roughly 0.4 units, requiring planes to be `(9.33 + 0.8) / 9.33 ≈ 1.086` oversized in the worst axis. For farther planes, the displacement is even less significant proportionally.

The 1.05 factor is conservative for the average case. OBJ-040 will compute precise per-plane factors using the per-axis displacements, so the scalar is a guideline, not a critical boundary. Rounding down to 1.05 from 1.086 is acceptable because: (a) most planes are farther than the nearest subject, reducing the proportional impact, and (b) geometries already include some built-in margin in their plane sizing.

**Speed interaction:** At `speed: 2.0`, effective displacements double. OBJ-040 must compute `displacement * speed` and re-derive the oversize factor. The `recommendedOversizeFactor` is for speed=1.0 only.

### D5: LookAt Drift Independent of Speed

**Decision:** The lookAt target oscillates independently of the `speed` parameter.

**Rationale:** Speed controls spatial amplitude (OBJ-006 D3). At speed=0, position displacement is zero — the camera is static. If lookAt also zeroed out, the preset would be indistinguishable from `static` (OBJ-026). Keeping lookAt drift preserves a minimal sense of camera life (subtle gaze wander) even at very low speeds. This matches the preset's purpose: it's the "breathing" camera, and breathing should never fully stop unless the author chooses `static` instead.

**Edge case:** At very high speed values (e.g., 3.0+), position displacement grows to ±0.9/±0.6/±1.2 units, but lookAt drift stays at ±0.15/±0.1/±0.2. This creates a growing disparity between camera movement and gaze target, which produces a more noticeable parallax shift. This is acceptable — if the author cranks speed that high, they want more visible motion.

### D6: Universal Geometry Compatibility

**Decision:** Compatible with all 8 proposed geometries.

**Rationale:** The gentle_float's motion envelope is small enough (±0.4 units maximum) that it cannot cause edge reveals or spatial violations in any standard geometry. Tunnels, canyons, and other enclosed geometries have walls at ±4 units from center (per Seed Section 8.6); a ±0.3 X drift cannot approach them. The preset is explicitly described in the seed as "compatible with most geometries" and its purpose is to be the universal ambient fallback.

**Caveat:** If a future geometry has extremely tight spatial bounds (< 1 unit clearance), compatibility should be re-evaluated. But no such geometry exists in the current proposal.

### D7: No Duration Dependency

**Decision:** The oscillation frequencies are defined per normalized time `t ∈ [0,1]`, not per real seconds. The preset does NOT accept or use scene duration.

**Rationale:** OBJ-006 Open Question #2 raised whether gentle_float should vary frequency based on duration. The concern: a 5-second scene would have the same oscillation count as a 30-second scene, making the motion appear 6x faster in wall-clock time.

However, the chosen frequencies (0.5–1.1 cycles per normalized t) map to:
- 5-second scene: 0.1–0.22 Hz (one cycle every 4.5–10 seconds). Slow and subtle.
- 15-second scene: 0.033–0.073 Hz (one cycle every 14–30 seconds). Very slow, subliminal.
- 30-second scene: 0.017–0.037 Hz (one cycle every 27–60 seconds). Glacial.

For short scenes (5s), the motion is still within the "subtle" range. For long scenes (30s+), the motion becomes extremely slow — but the envelope `sin(π * t)` ensures the full amplitude is still reached at the midpoint. The visual effect remains appropriate across the 5–30 second range without duration tuning.

If future testing reveals that 30+ second scenes feel too static, a `duration`-aware variant can be added as a separate preset (e.g., `gentle_float_extended`) without modifying this one. This avoids complicating the OBJ-006 `CameraParams` interface for a speculative need.

## Acceptance Criteria

### Contract Conformance (from OBJ-006)

- [ ] **AC-01:** `gentleFloat` satisfies the `CameraPathPreset` interface from OBJ-006.
- [ ] **AC-02:** `gentleFloat.name` equals `'gentle_float'`.
- [ ] **AC-03:** `evaluate(0)` returns `{ position: [0, 0, 5], lookAt: [0, 0, 0], fov: 50 }` (exact match).
- [ ] **AC-04:** `evaluate(1)` returns `{ position: [0, 0, 5], lookAt: [0, 0, 0], fov: 50 }` (exact match).
- [ ] **AC-05:** `evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-06:** `evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-07:** `validateCameraPathPreset(gentleFloat)` returns an empty array (passes all validation).
- [ ] **AC-08:** FOV is exactly 50 at all points in `[0, 1]` (no FOV animation).

### Motion Character

- [ ] **AC-09:** At `t=0.5` with default params, `evaluate(0.5).position` differs from `defaultStartState.position` in all three components (all axes are active).
- [ ] **AC-10:** The maximum Euclidean distance from the start position across 1000 evenly-spaced samples is ≤ `sqrt(0.3² + 0.2² + 0.4² )` ≈ 0.539 world units (at speed=1.0).
- [ ] **AC-11:** No two of the 1000 evenly-spaced samples produce identical position values (non-degenerate motion).
- [ ] **AC-12:** The position trajectory is symmetric about `t=0.5` in amplitude (due to the `sin(π*t)` envelope): the maximum displacement magnitude in `[0, 0.25]` is less than the maximum in `[0.25, 0.5]`.

### Speed Scaling

- [ ] **AC-13:** At `speed=0.5`, the maximum displacement from start position across 100 samples is strictly less than at `speed=1.0`.
- [ ] **AC-14:** At `speed=2.0`, the maximum displacement from start position is strictly greater than at `speed=1.0`.
- [ ] **AC-15:** At `speed=0.5`, the lookAt drift range is identical to `speed=1.0` (lookAt is speed-independent).
- [ ] **AC-16:** At `speed=0.0001` (near-zero), position is nearly static but lookAt still drifts measurably from `[0,0,0]` at `t=0.5`.

### Easing

- [ ] **AC-17:** `evaluate(0.25, { easing: 'ease_in' })` produces different position values than `evaluate(0.25, { easing: 'linear' })`.
- [ ] **AC-18:** `evaluate(0.5, { easing: 'ease_in' })` and `evaluate(0.5, { easing: 'linear' })` produce similar but not necessarily identical position values (easing affects envelope, not oscillation frequency).

### Determinism

- [ ] **AC-19:** Calling `evaluate(t)` with the same `t` and same `params` 1000 times produces bit-identical results (C-05).

### Metadata

- [ ] **AC-20:** `compatibleGeometries` includes all 8 geometry names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.
- [ ] **AC-21:** `oversizeRequirements.maxDisplacementX` equals 0.3.
- [ ] **AC-22:** `oversizeRequirements.maxDisplacementY` equals 0.2.
- [ ] **AC-23:** `oversizeRequirements.maxDisplacementZ` equals 0.4.
- [ ] **AC-24:** `oversizeRequirements.fovRange` equals `[50, 50]`.
- [ ] **AC-25:** `oversizeRequirements.recommendedOversizeFactor` equals 1.05.
- [ ] **AC-26:** `defaultEasing` equals `'linear'`.
- [ ] **AC-27:** `tags` includes at least `'ambient'`, `'subtle'`, `'float'`.

### OBJ-006 Conformance Suite

- [ ] **AC-28:** Passes all 8 checks of the OBJ-006 contract conformance test pattern (boundary start, boundary end, continuity, FOV range, determinism, full validation, speed scaling, easing override).

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Exact match with `defaultStartState`. Envelope = `sin(0) = 0`, so all displacement terms vanish. |
| `t = 1` | Exact match with `defaultEndState`. Envelope = `sin(π) = 0`, so all displacement terms vanish. |
| `t = 0.5` | Maximum envelope amplitude. All three position axes show non-zero displacement. |
| `t < 0` or `t > 1` | Undefined per OBJ-006 contract. The implementation may clamp as a safety measure but is not required to. |
| `params = undefined` | Uses defaults: `speed=1.0`, `easing=linear`. |
| `params = {}` | Same as undefined. |
| `params.speed = 0` | `resolveCameraParams` throws (speed must be > 0). `evaluate` is never called. |
| `params.speed = 0.0001` | Valid. Position displacement is near-zero but non-zero. LookAt still drifts normally. |
| `params.speed = 5.0` | Valid. Position amplitudes scale to ±1.5/±1.0/±2.0 units. May cause edge reveals — OBJ-040 should flag this with a warning, not a hard error. |
| `params.easing = 'ease_in_out_cubic'` | Applied to the envelope. Motion ramps in/out more aggressively. |
| `params.offset = [2, 0, 0]` | Applied by renderer post-evaluate. Shifts entire drift envelope 2 units right. OBJ-040 must account for this. |
| Very short scene (1 second) | Frequencies map to ~0.5–1.1 Hz. Motion is subtle but visible. Envelope ramps up and down quickly — peak displacement is brief. Acceptable. |
| Very long scene (60 seconds) | Frequencies map to ~0.008–0.018 Hz. Motion is extremely slow / glacial. Envelope ensures peak is reached at t=0.5. The visual effect is subliminal, which matches the preset's purpose. |

### Numerical Precision

The `sin(π * 1.0)` computation in JavaScript produces approximately `1.2246e-16`, not exactly `0`. This means `evaluate(1)` will not return *exactly* `[0, 0, 5]` but rather `[0 ± ~1e-16, 0 ± ~1e-16, 5 ± ~1e-16]`. This is within the OBJ-006 validation tolerance of `1e-6` and is acceptable. No special handling is needed.

## Test Strategy

### Unit Tests

**1. Contract conformance (reuse OBJ-006 pattern):**
Run the 8-check conformance suite defined in OBJ-006's test strategy. This covers boundary values, continuity, FOV range, determinism, speed scaling, and easing override.

**2. Motion character tests:**
- Sample 1000 points in `[0, 1]`. Verify all three position components differ from start at `t=0.5`.
- Verify the maximum Euclidean displacement is within the expected bound (~0.539 at speed=1.0).
- Verify no two samples produce identical positions (non-degenerate).
- Verify envelope symmetry: max displacement in `[0, 0.25]` < max in `[0.25, 0.5]`.

**3. Speed scaling tests:**
- Compare max displacement at speed=0.5 vs 1.0 vs 2.0. Verify monotonic increase.
- Verify lookAt drift at speed=0.5 equals lookAt drift at speed=1.0 (within tolerance).
- Verify near-zero speed (0.0001) produces near-zero position displacement but non-zero lookAt displacement.

**4. Easing tests:**
- Compare `evaluate(0.25, {easing: 'ease_in'})` vs `evaluate(0.25, {easing: 'linear'})`. Verify they differ.
- Verify both still satisfy boundary conditions (t=0 and t=1 match start/end states).

**5. Determinism:**
- Call `evaluate(0.3)` 1000 times. All results must be bit-identical.

**6. Metadata validation:**
- Verify all static fields (name, tags, compatibleGeometries, oversizeRequirements) match specified values.
- `validateCameraPathPreset(gentleFloat)` returns empty array.

### Relevant Testable Claims

- **TC-04:** The preset is selectable by name without XYZ coordinate authoring.
- **TC-06:** Deterministic output verified by repeated evaluation.
- **TC-08:** Universal compatibility supports coverage analysis.
- **TC-09:** Easing override enables comparison with linear baseline.

## Integration Points

### Depends On

| Dependency | What is imported |
|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `ResolvedCameraParams`, `OversizeRequirements`, `resolveCameraParams` |
| **OBJ-002** (`src/interpolation/`) | `getEasing()` used indirectly via `resolveCameraParams`. Easing functions used for envelope modulation. |
| **OBJ-003** (`src/spatial/types.ts`) | `Vec3` type for position and lookAt values. |

### Consumed By

| Downstream | How it uses gentle_float |
|---|---|
| **Camera Path Registry** | Registered as `'gentle_float'` in the `CameraPathRegistry`. |
| **OBJ-059** (Stage tuning) | Stage + gentle_float is a primary combination for ambient content. |
| **OBJ-060** (Tunnel tuning) | Tunnel + gentle_float for atmospheric tunnel scenes. |
| **OBJ-061** (Canyon tuning) | Canyon + gentle_float for ambient canyon scenes. |
| **OBJ-062** (Flyover tuning) | Flyover + gentle_float for contemplative aerial scenes. |
| **OBJ-063** (Diorama tuning) | Diorama + gentle_float for paper-theater ambiance. |
| **OBJ-065** (Panorama tuning) | Panorama + gentle_float for slow environmental scenes. |
| **OBJ-066** (Close-up tuning) | Close-up + gentle_float is a natural pairing. |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "gentle_float"` from manifest. |
| **Edge-reveal validator** (OBJ-040) | Uses `oversizeRequirements` to compute plane sizing. |
| **Geometry-camera compatibility** (OBJ-041) | Cross-references `compatibleGeometries`. |
| **SKILL.md** (OBJ-070, OBJ-071) | Documented as the ambient/default camera for most geometries. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        gentle_float.ts    # CameraPathPreset definition + evaluate function
```

The preset is imported by the registry assembly module (which collects all presets from `src/camera/presets/` and builds the `CameraPathRegistry`).

## Open Questions

1. **Should lookAt amplitudes also be affected by speed at a reduced rate (e.g., 0.3× speed)?** Current spec says lookAt is fully speed-independent. An alternative: `lookAtAmplitude * (0.7 + 0.3 * speed)` so it scales partially. This would prevent the growing disparity at high speeds. **Recommendation:** Start with full independence as specified. Revisit during visual tuning (OBJ-059 through OBJ-066) if the Director Agent flags gaze behavior at high speed values.

2. **Should the frequencies be configurable via CameraParams extension?** E.g., `{ oscillationScale?: number }` to globally scale all frequencies. **Recommendation:** Defer. The preset is designed to "just work" without tuning. If frequency control is needed, it belongs in a separate `configurable_float` preset, not in gentle_float's params.

3. **Are the specific frequency values (0.7, 1.1, 0.5, etc.) optimal?** These are informed estimates chosen for incommensurability and pleasant visual rhythm. They should be verified during the visual tuning phase (OBJ-059+). The implementation should define them as named constants at the top of the file so they can be adjusted easily during tuning without restructuring code.

---

I believe this spec is complete and ready for review. I'd like the Challenger to verify that:
1. The motion model is sufficiently specified for implementation
2. The envelope approach for boundary continuity is sound
3. The speed/easing interaction is correctly handled per OBJ-006's contract
4. The acceptance criteria are testable and complete

---

## Round 2 — spec_challenger

I've carefully reviewed the OBJ-031 spec against the seed, OBJ-006, and my implementability checklist. Here's my assessment:

## What's Sound

- **Motion model choice** (incommensurate sinusoids) is well-justified and deterministic by construction (C-05). Good decision over Perlin noise.
- **Speed scaling position but not lookAt** (D5) is a smart design choice with clear rationale.
- **No duration dependency** (D7) — the frequency-to-wall-clock analysis is convincing for the 5–30s range.
- **Universal geometry compatibility** (D6) — the math checks out; ±0.4 units is negligible against ±4-unit tunnel walls.
- **OBJ-006 contract conformance** is thoroughly addressed. The OversizeRequirements, tags, and registry integration are all well-specified.

## Challenges

### Issue 1: LookAt envelope omission — CRITICAL

The spec states a `sin(π * t)` fade envelope for position, but **never explicitly states that the same envelope (or any envelope) applies to lookAt oscillations**. The formula section only shows:

```
position.x(t) = startX + amplitudeX * speed * sin(2π * freqX * t + phaseX) * envelope(t)
```

No equivalent formula for lookAt. Without an envelope on lookAt, at `t=0`:

```
lookAt.x(0) = 0 + 0.15 * sin(0 + π/4) = 0.15 * 0.707 ≈ 0.106
lookAt.y(0) = 0 + 0.1 * sin(0 + π/6) = 0.1 * 0.5 = 0.05
lookAt.z(0) = 0 + 0.2 * sin(0 + π/2) = 0.2 * 1.0 = 0.2
```

This violates **AC-03** (`evaluate(0)` returns `lookAt: [0, 0, 0]`) and **AC-04**. The implementer must guess whether lookAt uses the envelope.

**Proposed fix:** Add an explicit lookAt formula section parallel to the position formula:

```
lookAt.x(t) = startLookAtX + lookAtAmplitudeX * sin(2π * lookAtFreqX * t + lookAtPhaseX) * envelope(t)
lookAt.y(t) = startLookAtY + lookAtAmplitudeY * sin(2π * lookAtFreqY * t + lookAtPhaseY) * envelope(t)
lookAt.z(t) = startLookAtZ + lookAtAmplitudeZ * sin(2π * lookAtFreqZ * t + lookAtPhaseZ) * envelope(t)
```

### Issue 2: Easing application to lookAt envelope — MAJOR

D2 specifies: `envelope(t) = sin(π * easing(t))` and says easing applies to the envelope for position. Does easing also apply to the lookAt envelope? Since D5 says lookAt is speed-independent, should it also be easing-independent? An implementer would have to guess.

**Proposed fix:** Add an explicit statement: either (a) lookAt uses `sin(π * t)` always (raw `t`, easing-independent — consistent with lookAt being author-parameter-independent), or (b) lookAt shares the eased envelope. I recommend option (a) for consistency with D5's "lookAt is independent of author overrides" principle.

### Issue 3: AC-04 claims "exact match" at t=1 — MINOR

AC-04 says `evaluate(1)` returns the expected values with "(exact match)". But the Numerical Precision section correctly notes `sin(π * 1.0) ≈ 1.2e-16 ≠ 0`. So AC-04's "exact match" is literally false. AC-06 (within 1e-6) covers it properly.

**Proposed fix:** Change AC-04 to say "(within floating-point tolerance)" or remove the "(exact match)" annotation and let AC-06 be the authoritative boundary check.

### Issue 4: AC-12 misleading symmetry claim — MINOR

AC-12 says: "The position trajectory is symmetric about t=0.5 in amplitude (due to the sin(π*t) envelope)."

The envelope is symmetric. The trajectory is NOT symmetric — at time `t` and time `1-t`, the envelope values are equal (`sin(π*t) = sin(π*(1-t))`), but the oscillatory terms produce different values. The testable assertion (max displacement in [0, 0.25] < max in [0.25, 0.5]) is correct because the envelope peaks in [0.25, 0.5], but calling this "symmetric" is wrong.

**Proposed fix:** Rewrite AC-12 to: "The envelope ensures displacement grows toward the midpoint: the maximum displacement magnitude across samples in [0, 0.25] is strictly less than the maximum in [0.25, 0.5]." Drop the "symmetric" claim.

### Issue 5: LookAt drift not accounted for in OversizeRequirements — MINOR

OversizeRequirements captures position displacement only. LookAt drift shifts the frustum direction, which shifts what's visible. For this preset, lookAt amplitude is ≤0.2 units. At ~10 unit distance to a plane, that's ~1.1° angular shift — negligible for oversizing. But the spec should acknowledge this explicitly so OBJ-040 implementers don't wonder whether they missed something.

**Proposed fix:** Add a note under the OversizeRequirements section or in D4: "LookAt drift at the specified amplitudes (≤0.2 units) produces angular frustum shifts of ≤~1.1° at typical plane distances, which is negligible for edge-reveal computation and is not included in displacement values. OBJ-040 may ignore lookAt drift for this preset."

---

These are my five issues. Issue 1 is critical (blocks correct implementation). Issue 2 is major (forces an implementer to guess about easing/lookAt interaction). Issues 3–5 are minor polish. Please address #1 and #2 in your revision; I'll verify them before converging.

---

## Round 3 — spec_author

Thank you for the thorough review. All five issues are valid. Here's my revised spec with each addressed:

---

# Specification: OBJ-031 — Gentle Float Camera Path Preset

## Summary

OBJ-031 defines the `gentle_float` camera path preset — a very slow, subtle multi-axis drift that produces an almost subliminal sense of life in otherwise static scenes. It is the universal ambient preset, compatible with most scene geometries, and designed for moments where camera motion should be felt rather than noticed. The preset implements the `CameraPathPreset` interface from OBJ-006 using incommensurate sinusoidal oscillations across X, Y, and Z axes to create organic, non-repeating drift within a single scene duration.

## Interface Contract

### Exported Preset

```typescript
// src/camera/presets/gentle_float.ts

import { CameraPathPreset } from '../types';

/**
 * The gentle_float camera path preset.
 * 
 * Produces very slow, subtle movement across all three axes using
 * incommensurate sinusoidal oscillations. The motion is designed to
 * feel organic and non-repeating within typical scene durations (5–30s).
 * 
 * At speed=1.0, the camera drifts within a small spatial envelope:
 *   X: ±0.3 world units
 *   Y: ±0.2 world units
 *   Z: ±0.4 world units (centered on start position)
 * 
 * lookAt target drifts with dampened, phase-offset oscillations to
 * create subtle gaze wander rather than a fixed stare point.
 * lookAt drift is independent of both speed and easing parameters.
 * 
 * FOV is static at 50°.
 */
export const gentleFloat: CameraPathPreset;
```

### Motion Model

The motion model uses **three independent sinusoidal oscillations per output channel** (position X/Y/Z, lookAt X/Y/Z), each with carefully chosen frequencies and phases. A multiplicative fade envelope ensures the camera starts and ends at rest.

#### Fade Envelope

Both position and lookAt oscillations are modulated by a fade envelope that forces zero displacement at `t=0` and `t=1`:

**Position envelope** (easing-responsive):
```
positionEnvelope(t) = sin(π * easing(t))
```
Where `easing` is the resolved easing function from `ResolvedCameraParams` (default: `linear`, i.e., identity).

**LookAt envelope** (easing-independent):
```
lookAtEnvelope(t) = sin(π * t)
```
The lookAt envelope always uses raw `t`, never the eased value. This is consistent with Design Decision D5: lookAt drift is independent of all author-controlled parameters (`speed` and `easing`).

#### Position Oscillation

```
position.x(t) = startX + amplitudeX * speed * sin(2π * freqX * t + phaseX) * positionEnvelope(t)
position.y(t) = startY + amplitudeY * speed * sin(2π * freqY * t + phaseY) * positionEnvelope(t)
position.z(t) = startZ + amplitudeZ * speed * sin(2π * freqZ * t + phaseZ) * positionEnvelope(t)
```

Where:
- `t` is normalized time `[0, 1]`
- `speed` is from `ResolvedCameraParams.speed` (amplitude multiplier per OBJ-006 D3)
- `positionEnvelope(t) = sin(π * easing(t))`

**Default Position Parameters:**

| Parameter | X-axis | Y-axis | Z-axis |
|-----------|--------|--------|--------|
| Amplitude (world units) | 0.3 | 0.2 | 0.4 |
| Frequency (cycles per normalized t) | 0.7 | 1.1 | 0.5 |
| Phase offset (radians) | 0 | π/3 | 2π/5 |

#### LookAt Oscillation

```
lookAt.x(t) = startLookAtX + lookAtAmplitudeX * sin(2π * lookAtFreqX * t + lookAtPhaseX) * lookAtEnvelope(t)
lookAt.y(t) = startLookAtY + lookAtAmplitudeY * sin(2π * lookAtFreqY * t + lookAtPhaseY) * lookAtEnvelope(t)
lookAt.z(t) = startLookAtZ + lookAtAmplitudeZ * sin(2π * lookAtFreqZ * t + lookAtPhaseZ) * lookAtEnvelope(t)
```

Where `lookAtEnvelope(t) = sin(π * t)` (always raw `t`, never eased).

The lookAt amplitudes are **not scaled by `speed`** and the lookAt envelope is **not affected by `easing`**. Rationale: lookAt drift is fully independent of author-controlled parameters, preserving a minimal sense of camera life even at extreme speed/easing values (see D5).

**Default LookAt Parameters:**

| Parameter | X-axis | Y-axis | Z-axis |
|-----------|--------|--------|--------|
| Amplitude (world units) | 0.15 | 0.1 | 0.2 |
| Frequency (cycles per normalized t) | 0.9 | 0.6 | 0.4 |
| Phase offset (radians) | π/4 | π/6 | π/2 |

#### Default Camera Position

```
startPosition = [0, 0, 5]
startLookAt   = [0, 0, 0]
fov           = 50  (static, no animation)
```

These match the Three.js camera defaults from Seed Section 8.1–8.2. The gentle_float is geometry-agnostic — geometries place planes relative to the camera's start position, so the default `[0, 0, 5]` works universally.

### Preset Definition (Static Fields)

```typescript
{
  name: 'gentle_float',
  
  description: 'Very slow, subtle drift in all three axes. Almost subliminal. ' +
    'Creates a sense of life without drawing attention to camera movement. ' +
    'Good for ambient scenes, close-ups, and any geometry where stillness ' +
    'would feel lifeless.',
  
  // evaluate: <implementation per motion model above>
  
  defaultStartState: {
    position: [0, 0, 5],
    lookAt: [0, 0, 0],
    fov: 50,
  },
  
  defaultEndState: {
    position: [0, 0, 5],   // Returns to start (envelope forces convergence)
    lookAt: [0, 0, 0],     // Returns to start (envelope forces convergence)
    fov: 50,
  },
  
  defaultEasing: 'linear',  // See D2: easing affects position envelope only
  
  compatibleGeometries: [
    'stage',
    'tunnel',
    'canyon',
    'flyover',
    'diorama',
    'portal',
    'panorama',
    'close_up',
  ],
  
  oversizeRequirements: {
    maxDisplacementX: 0.3,   // amplitude_X at speed=1.0
    maxDisplacementY: 0.2,   // amplitude_Y at speed=1.0
    maxDisplacementZ: 0.4,   // amplitude_Z at speed=1.0
    fovRange: [50, 50],      // No FOV animation
    recommendedOversizeFactor: 1.05,  // See D4
  },
  
  tags: ['ambient', 'subtle', 'float', 'drift', 'gentle', 'universal'],
}
```

## Design Decisions

### D1: Incommensurate Sinusoidal Frequencies

**Decision:** Use sinusoidal oscillations with frequencies that are not integer multiples of each other (0.7, 1.1, 0.5 for position; 0.9, 0.6, 0.4 for lookAt).

**Rationale:** If frequencies were commensurate (e.g., 1.0, 2.0, 3.0), the motion would produce a recognizable repeating pattern. Incommensurate frequencies create quasi-periodic motion that never exactly repeats within a scene duration, producing a more organic, "breathing" quality. This is a standard technique in procedural animation (ocean waves, foliage sway).

**Trade-off:** Incommensurate frequencies mean the camera does not naturally return to its start position at t=1. This is solved by the fade envelope (see D3).

**Alternative considered:** Perlin/simplex noise for position. Rejected because: (a) noise requires either a library dependency or a non-trivial implementation, (b) noise output is harder to bound precisely for oversizing requirements, and (c) sinusoids are deterministic by construction (C-05) without needing to manage seeds.

### D2: Easing Affects Position Envelope Only, Not LookAt

**Decision:** The `defaultEasing` is `linear`. Easing overrides from `CameraParams.easing` are applied **only to the position envelope**, not to the sinusoidal oscillations themselves and not to the lookAt envelope.

Position envelope: `sin(π * easing(t))`
LookAt envelope: `sin(π * t)` (always raw `t`)

**Rationale:** The gentle_float motion model is fundamentally oscillatory, not interpolatory. Easing functions are designed for start-to-end interpolation — they map `[0,1] → [0,1]` monotonically. Applying easing to the sinusoidal phase would distort oscillation frequencies in non-physical ways. Applying it to the envelope modulates how quickly the motion ramps in/out, which is intuitive:

- `linear` easing → symmetric fade in/out (default, most natural)
- `ease_in` → slow start, the drift takes longer to reach full amplitude
- `ease_out` → quick start, the drift reaches full amplitude early and fades slowly
- `ease_in_out` → similar to linear for this application but slightly more weighted toward the center

LookAt is excluded from easing for the same reason it's excluded from speed (D5): lookAt drift is independent of all author-controlled parameters. This makes lookAt the "always-on heartbeat" of the preset — the one thing that never changes regardless of parameter overrides.

The SKILL.md should note that easing has subtle effect on this preset.

### D3: Fade Envelope for Start/End Continuity

**Decision:** Apply multiplicative fade envelopes to both position and lookAt oscillations so the camera starts and ends at rest.

**Rationale:** OBJ-006 requires `evaluate(0) === defaultStartState` and `evaluate(1) === defaultEndState`. Without an envelope, the sinusoidal values at t=0 would depend on phase offsets — phases would need to be chosen so that `sin(phase) = 0` for all axes, which constrains the creative space. The multiplicative envelope zeros out displacement at boundaries regardless of phase, while preserving the organic feel in the middle of the scene.

**Consequence:** `defaultEndState === defaultStartState`. The camera returns to its origin. This is ideal for scene transitions — the camera is at a known, predictable position at scene boundaries.

### D4: Recommended Oversize Factor of 1.05

**Decision:** `recommendedOversizeFactor: 1.05` (5% oversize).

**Rationale:** The maximum displacement at speed=1.0 is 0.4 world units (Z-axis). At the default camera position of z=5, the nearest plane in most geometries is the `subject` at approximately z=-5 (distance=10 units). The visible height at distance 10 with FOV=50° is `2 * 10 * tan(25°) ≈ 9.33` units. A 0.4-unit camera displacement at this distance shifts the visible area by roughly 0.4 units, requiring planes to be `(9.33 + 0.8) / 9.33 ≈ 1.086` oversized in the worst axis. For farther planes, the displacement is even less significant proportionally.

The 1.05 factor is conservative for the average case. OBJ-040 will compute precise per-plane factors using the per-axis displacements, so the scalar is a guideline, not a critical boundary. Rounding down to 1.05 from 1.086 is acceptable because: (a) most planes are farther than the nearest subject, reducing the proportional impact, and (b) geometries already include some built-in margin in their plane sizing.

**LookAt drift and oversizing:** LookAt drift at the specified amplitudes (≤0.2 units) produces angular frustum shifts of ≤~1.1° at typical plane distances (~10 units), which is negligible for edge-reveal computation. The displacement values in `oversizeRequirements` reflect position displacement only. OBJ-040 may safely ignore lookAt drift for this preset. If a future preset has large lookAt amplitudes, its spec should document whether lookAt drift contributes meaningfully to frustum shift and whether OBJ-040 should account for it.

**Speed interaction:** At `speed: 2.0`, effective position displacements double. OBJ-040 must compute `displacement * speed` and re-derive the oversize factor. The `recommendedOversizeFactor` is for speed=1.0 only. LookAt drift does not scale with speed, so no adjustment is needed for lookAt-related frustum shift at any speed.

### D5: LookAt Drift Independent of Speed and Easing

**Decision:** The lookAt target oscillates independently of both the `speed` and `easing` parameters.

**Rationale for speed independence:** Speed controls spatial amplitude (OBJ-006 D3). At speed≈0, position displacement is near-zero — the camera is nearly static. If lookAt also zeroed out, the preset would be indistinguishable from `static` (OBJ-026). Keeping lookAt drift preserves a minimal sense of camera life (subtle gaze wander) even at very low speeds.

**Rationale for easing independence:** Consistent with speed independence — lookAt is the "always-on" component that doesn't respond to author overrides. The lookAt envelope always uses raw `t`.

**Edge case — high speed:** At very high speed values (e.g., 3.0+), position displacement grows to ±0.9/±0.6/±1.2 units, but lookAt drift stays at ±0.15/±0.1/±0.2. This creates a growing disparity between camera movement and gaze target, which produces a more noticeable parallax shift. This is acceptable — if the author cranks speed that high, they want more visible motion.

### D6: Universal Geometry Compatibility

**Decision:** Compatible with all 8 proposed geometries.

**Rationale:** The gentle_float's motion envelope is small enough (±0.4 units maximum) that it cannot cause edge reveals or spatial violations in any standard geometry. Tunnels, canyons, and other enclosed geometries have walls at ±4 units from center (per Seed Section 8.6); a ±0.3 X drift cannot approach them.

**Caveat:** If a future geometry has extremely tight spatial bounds (< 1 unit clearance), compatibility should be re-evaluated. But no such geometry exists in the current proposal.

### D7: No Duration Dependency

**Decision:** The oscillation frequencies are defined per normalized time `t ∈ [0,1]`, not per real seconds. The preset does NOT accept or use scene duration.

**Rationale:** OBJ-006 Open Question #2 raised whether gentle_float should vary frequency based on duration. The chosen frequencies (0.5–1.1 cycles per normalized t) map to:
- 5-second scene: 0.1–0.22 Hz (one cycle every 4.5–10 seconds). Slow and subtle.
- 15-second scene: 0.033–0.073 Hz (one cycle every 14–30 seconds). Very slow, subliminal.
- 30-second scene: 0.017–0.037 Hz (one cycle every 27–60 seconds). Glacial.

For short scenes (5s), the motion is still within the "subtle" range. For long scenes (30s+), the motion becomes extremely slow — but the envelope ensures the full amplitude is still reached at the midpoint. The visual effect remains appropriate across the 5–30 second range without duration tuning.

If future testing reveals that 30+ second scenes feel too static, a duration-aware variant can be added as a separate preset (e.g., `gentle_float_extended`) without modifying this one.

## Acceptance Criteria

### Contract Conformance (from OBJ-006)

- [ ] **AC-01:** `gentleFloat` satisfies the `CameraPathPreset` interface from OBJ-006.
- [ ] **AC-02:** `gentleFloat.name` equals `'gentle_float'`.
- [ ] **AC-03:** `evaluate(0)` returns `{ position: [0, 0, 5], lookAt: [0, 0, 0], fov: 50 }` (within floating-point tolerance; see Numerical Precision).
- [ ] **AC-04:** `evaluate(1)` returns `{ position: [0, 0, 5], lookAt: [0, 0, 0], fov: 50 }` (within floating-point tolerance; see Numerical Precision).
- [ ] **AC-05:** `evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-06:** `evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-07:** `validateCameraPathPreset(gentleFloat)` returns an empty array (passes all validation).
- [ ] **AC-08:** FOV is exactly 50 at all points in `[0, 1]` (no FOV animation).

### Motion Character

- [ ] **AC-09:** At `t=0.5` with default params, `evaluate(0.5).position` differs from `defaultStartState.position` in all three components (all axes are active).
- [ ] **AC-10:** The maximum Euclidean distance from the start position across 1000 evenly-spaced samples is ≤ `sqrt(0.3² + 0.2² + 0.4²)` ≈ 0.539 world units (at speed=1.0).
- [ ] **AC-11:** No two of the 1000 evenly-spaced samples produce identical position values (non-degenerate motion).
- [ ] **AC-12:** The envelope ensures displacement grows toward the midpoint: the maximum displacement magnitude across samples in `[0, 0.25]` is strictly less than the maximum in `[0.25, 0.5]`.

### Speed Scaling

- [ ] **AC-13:** At `speed=0.5`, the maximum displacement from start position across 100 samples is strictly less than at `speed=1.0`.
- [ ] **AC-14:** At `speed=2.0`, the maximum displacement from start position is strictly greater than at `speed=1.0`.
- [ ] **AC-15:** At `speed=0.5`, the lookAt drift range is identical to `speed=1.0` (lookAt is speed-independent).
- [ ] **AC-16:** At `speed=0.0001` (near-zero), position is nearly static but lookAt still drifts measurably from `[0,0,0]` at `t=0.5`.

### Easing

- [ ] **AC-17:** `evaluate(0.25, { easing: 'ease_in' })` produces different position values than `evaluate(0.25, { easing: 'linear' })`.
- [ ] **AC-18:** `evaluate(0.25, { easing: 'ease_in' }).lookAt` equals `evaluate(0.25, { easing: 'linear' }).lookAt` (lookAt envelope is easing-independent).

### Determinism

- [ ] **AC-19:** Calling `evaluate(t)` with the same `t` and same `params` 1000 times produces bit-identical results (C-05).

### Metadata

- [ ] **AC-20:** `compatibleGeometries` includes all 8 geometry names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.
- [ ] **AC-21:** `oversizeRequirements.maxDisplacementX` equals 0.3.
- [ ] **AC-22:** `oversizeRequirements.maxDisplacementY` equals 0.2.
- [ ] **AC-23:** `oversizeRequirements.maxDisplacementZ` equals 0.4.
- [ ] **AC-24:** `oversizeRequirements.fovRange` equals `[50, 50]`.
- [ ] **AC-25:** `oversizeRequirements.recommendedOversizeFactor` equals 1.05.
- [ ] **AC-26:** `defaultEasing` equals `'linear'`.
- [ ] **AC-27:** `tags` includes at least `'ambient'`, `'subtle'`, `'float'`.

### OBJ-006 Conformance Suite

- [ ] **AC-28:** Passes all 8 checks of the OBJ-006 contract conformance test pattern (boundary start, boundary end, continuity, FOV range, determinism, full validation, speed scaling, easing override).

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Matches `defaultStartState` within 1e-6. Both envelopes = `sin(0) = 0`, all displacement terms vanish. |
| `t = 1` | Matches `defaultEndState` within 1e-6. Both envelopes = `sin(π) ≈ 1.2e-16 ≈ 0`, all displacement terms vanish. |
| `t = 0.5` | Maximum envelope amplitude. All three position axes and all three lookAt axes show non-zero displacement. |
| `t < 0` or `t > 1` | Undefined per OBJ-006 contract. The implementation may clamp as a safety measure but is not required to. |
| `params = undefined` | Uses defaults: `speed=1.0`, `easing=linear`. |
| `params = {}` | Same as undefined. |
| `params.speed = 0` | `resolveCameraParams` throws (speed must be > 0). `evaluate` is never called. |
| `params.speed = 0.0001` | Valid. Position displacement is near-zero but non-zero. LookAt still drifts normally (speed-independent). |
| `params.speed = 5.0` | Valid. Position amplitudes scale to ±1.5/±1.0/±2.0 units. May cause edge reveals — OBJ-040 should flag this. |
| `params.easing = 'ease_in'` | Applied to position envelope only: `sin(π * easeIn(t))`. LookAt uses `sin(π * t)` unchanged. |
| `params.easing = 'ease_in_out_cubic'` | Same pattern — position envelope uses eased `t`, lookAt uses raw `t`. |
| `params.offset = [2, 0, 0]` | Applied by renderer post-evaluate. Shifts entire drift envelope 2 units right. OBJ-040 must account for this. |
| Very short scene (1 second) | Frequencies map to ~0.5–1.1 Hz. Motion is subtle but visible. Envelope ramps up and down quickly — peak displacement is brief. Acceptable. |
| Very long scene (60 seconds) | Frequencies map to ~0.008–0.018 Hz. Motion is extremely slow/glacial. Envelope ensures peak is reached at t=0.5. The visual effect is subliminal, matching the preset's purpose. |

### Numerical Precision

The `sin(π * 1.0)` computation in JavaScript produces approximately `1.2246e-16`, not exactly `0`. This means `evaluate(1)` will not return *exactly* `[0, 0, 5]` but rather `[0 ± ~1e-16, 0 ± ~1e-16, 5 ± ~1e-16]`. This is within the OBJ-006 validation tolerance of `1e-6` and is acceptable. No special handling is needed.

## Test Strategy

### Unit Tests

**1. Contract conformance (reuse OBJ-006 pattern):**
Run the 8-check conformance suite defined in OBJ-006's test strategy. This covers boundary values, continuity, FOV range, determinism, speed scaling, and easing override.

**2. Motion character tests:**
- Sample 1000 points in `[0, 1]`. Verify all three position components differ from start at `t=0.5`.
- Verify the maximum Euclidean displacement is within the expected bound (~0.539 at speed=1.0).
- Verify no two samples produce identical positions (non-degenerate).
- Verify envelope growth: max displacement in `[0, 0.25]` < max in `[0.25, 0.5]`.

**3. Speed scaling tests:**
- Compare max displacement at speed=0.5 vs 1.0 vs 2.0. Verify monotonic increase.
- Verify lookAt drift at speed=0.5 equals lookAt drift at speed=1.0 (within tolerance).
- Verify near-zero speed (0.0001) produces near-zero position displacement but non-zero lookAt displacement.

**4. Easing tests:**
- Compare `evaluate(0.25, {easing: 'ease_in'})` vs `evaluate(0.25, {easing: 'linear'})`. Verify position differs.
- Compare lookAt at same two calls. Verify lookAt is identical (easing-independent).
- Verify both still satisfy boundary conditions (t=0 and t=1 match start/end states within 1e-6).

**5. Determinism:**
- Call `evaluate(0.3)` 1000 times. All results must be bit-identical.

**6. Metadata validation:**
- Verify all static fields (name, tags, compatibleGeometries, oversizeRequirements) match specified values.
- `validateCameraPathPreset(gentleFloat)` returns empty array.

### Relevant Testable Claims

- **TC-04:** The preset is selectable by name without XYZ coordinate authoring.
- **TC-06:** Deterministic output verified by repeated evaluation.
- **TC-08:** Universal compatibility supports coverage analysis.
- **TC-09:** Easing override enables comparison with linear baseline.

## Integration Points

### Depends On

| Dependency | What is imported |
|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `ResolvedCameraParams`, `OversizeRequirements`, `resolveCameraParams` |
| **OBJ-002** (`src/interpolation/`) | `getEasing()` used indirectly via `resolveCameraParams`. Easing functions used for position envelope modulation. |
| **OBJ-003** (`src/spatial/types.ts`) | `Vec3` type for position and lookAt values. |

### Consumed By

| Downstream | How it uses gentle_float |
|---|---|
| **Camera Path Registry** | Registered as `'gentle_float'` in the `CameraPathRegistry`. |
| **OBJ-059** (Stage tuning) | Stage + gentle_float for ambient content. |
| **OBJ-060** (Tunnel tuning) | Tunnel + gentle_float for atmospheric tunnel scenes. |
| **OBJ-061** (Canyon tuning) | Canyon + gentle_float for ambient canyon scenes. |
| **OBJ-062** (Flyover tuning) | Flyover + gentle_float for contemplative aerial scenes. |
| **OBJ-063** (Diorama tuning) | Diorama + gentle_float for paper-theater ambiance. |
| **OBJ-065** (Panorama tuning) | Panorama + gentle_float for slow environmental scenes. |
| **OBJ-066** (Close-up tuning) | Close-up + gentle_float is a natural pairing. |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "gentle_float"` from manifest. |
| **Edge-reveal validator** (OBJ-040) | Uses `oversizeRequirements` (position displacements only; lookAt drift negligible). |
| **Geometry-camera compatibility** (OBJ-041) | Cross-references `compatibleGeometries`. |
| **SKILL.md** (OBJ-070, OBJ-071) | Documented as the ambient/default camera for most geometries. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        gentle_float.ts    # CameraPathPreset definition + evaluate function
```

The preset is imported by the registry assembly module (which collects all presets from `src/camera/presets/` and builds the `CameraPathRegistry`).

## Open Questions

1. **Should lookAt amplitudes also be affected by speed at a reduced rate (e.g., 0.3× speed)?** Current spec says lookAt is fully speed-independent. An alternative: `lookAtAmplitude * (0.7 + 0.3 * speed)` so it scales partially. **Recommendation:** Start with full independence as specified. Revisit during visual tuning (OBJ-059 through OBJ-066) if the Director Agent flags gaze behavior at high speed values.

2. **Should the frequencies be configurable via CameraParams extension?** E.g., `{ oscillationScale?: number }` to globally scale all frequencies. **Recommendation:** Defer. The preset is designed to "just work" without tuning. If frequency control is needed, it belongs in a separate `configurable_float` preset, not in gentle_float's params.

3. **Are the specific frequency values (0.7, 1.1, 0.5, etc.) optimal?** These are informed estimates chosen for incommensurability and pleasant visual rhythm. They should be verified during the visual tuning phase (OBJ-059+). The implementation should define them as named constants at the top of the file so they can be adjusted easily during tuning without restructuring code.

---

## Changes from Round 1 (addressing Challenger's issues)

**Issue 1 (CRITICAL) — LookAt envelope omission:** Added explicit lookAt oscillation formulas with the `lookAtEnvelope(t) = sin(π * t)` envelope. Both position and lookAt formulas are now fully specified with their respective envelopes.

**Issue 2 (MAJOR) — Easing/lookAt interaction:** Clarified that the position envelope uses `sin(π * easing(t))` while the lookAt envelope uses `sin(π * t)` (raw `t`, easing-independent). Updated D2 to explicitly state both envelope formulas and the rationale. Added **AC-18** to test that lookAt is identical regardless of easing parameter.

**Issue 3 (MINOR) — AC-04 "exact match":** Changed AC-03 and AC-04 to say "(within floating-point tolerance; see Numerical Precision)" instead of "(exact match)".

**Issue 4 (MINOR) — AC-12 symmetry claim:** Reworded AC-12 to: "The envelope ensures displacement grows toward the midpoint: the maximum displacement magnitude across samples in [0, 0.25] is strictly less than the maximum in [0.25, 0.5]." Removed the incorrect "symmetric" claim.

**Issue 5 (MINOR) — LookAt in OversizeRequirements:** Added explicit note in D4: "LookAt drift at the specified amplitudes (≤0.2 units) produces angular frustum shifts of ≤~1.1° at typical plane distances (~10 units), which is negligible for edge-reveal computation." Also noted this in the Integration Points table for OBJ-040.

---

Challenger — I believe all five issues are resolved. Please verify and approve if satisfied.

---

## Round 4 — spec_challenger

I've verified all five fixes against the revised spec:

1. **Issue 1 (CRITICAL):** ✓ Explicit lookAt formulas with `lookAtEnvelope(t) = sin(π * t)` are present in the Motion Model section.
2. **Issue 2 (MAJOR):** ✓ D2 explicitly distinguishes `sin(π * easing(t))` for position vs `sin(π * t)` for lookAt. AC-18 now tests lookAt easing-independence.
3. **Issue 3 (MINOR):** ✓ AC-03/AC-04 say "(within floating-point tolerance)".
4. **Issue 4 (MINOR):** ✓ AC-12 reworded — no false symmetry claim.
5. **Issue 5 (MINOR):** ✓ D4 includes the angular shift analysis and guidance for OBJ-040.

No new issues introduced by the revisions. The spec is implementable without guessing.

CONCLUSION:

The specification for OBJ-031 (Gentle Float Camera Path Preset) defines a `gentle_float` camera path using incommensurate sinusoidal oscillations with fade envelopes for boundary continuity. Position drift is speed-scaled and easing-responsive; lookAt drift is independent of both. The preset is universally compatible with all 8 geometries due to its small motion envelope (±0.4 units max). All formulas, parameters, acceptance criteria, edge cases, and integration points are fully specified.

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me check the current state of the node directory first.
[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-031/meta.json"
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
  "command": "ls /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-031 node directory exists"
}
[Tool Result] meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-031",
     3→  "description": "Gentle float camera path preset -- very slow, subtle movement in all three axes. Almost subliminal. Good for ambient scenes. Defines position(t), lookAt(t) with small-amplitude multi-axis drift, easing defaults, compatible geometries (most geometries), and oversizing requirements (minimal due to small motion range).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Universal ambient preset -- compatible with most geometries."
    12→}
    13→
Good. Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md",
  "content": "# Specification: OBJ-031 \u2014 Gentle Float Camera Path Preset\n\n## Summary\n\nOBJ-031 defines the `gentle_float` camera path preset \u2014 a very slow, subtle multi-axis drift that produces an almost subliminal sense of life in otherwise static scenes. It is the universal ambient preset, compatible with most scene geometries, and designed for moments where camera motion should be felt rather than noticed. The preset implements the `CameraPathPreset` interface from OBJ-006 using incommensurate sinusoidal oscillations across X, Y, and Z axes to create organic, non-repeating drift within a single scene duration.\n\n## Interface Contract\n\n### Exported Preset\n\n```typescript\n// src/camera/presets/gentle_float.ts\n\nimport { CameraPathPreset } from '../types';\n\n/**\n * The gentle_float camera path preset.\n *\n * Produces very slow, subtle movement across all three axes using\n * incommensurate sinusoidal oscillations. The motion is designed to\n * feel organic and non-repeating within typical scene durations (5\u201330s).\n *\n * At speed=1.0, the camera drifts within a small spatial envelope:\n *   X: \u00b10.3 world units\n *   Y: \u00b10.2 world units\n *   Z: \u00b10.4 world units (centered on start position)\n *\n * lookAt target drifts with dampened, phase-offset oscillations to\n * create subtle gaze wander rather than a fixed stare point.\n * lookAt drift is independent of both speed and easing parameters.\n *\n * FOV is static at 50\u00b0.\n */\nexport const gentleFloat: CameraPathPreset;\n```\n\n### Motion Model\n\nThe motion model uses **three independent sinusoidal oscillations per output channel** (position X/Y/Z, lookAt X/Y/Z), each with carefully chosen frequencies and phases. A multiplicative fade envelope ensures the camera starts and ends at rest.\n\n#### Fade Envelope\n\nBoth position and lookAt oscillations are modula
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/meta.json",
  "content": "{\n  \"id\": \"OBJ-031\",\n  \"description\": \"Gentle float camera path preset -- very slow, subtle movement in all three axes. Almost subliminal. Good for ambient scenes. Defines position(t), lookAt(t) with small-amplitude multi-axis drift, easing defaults, compatible geometries (most geometries), and oversizing requirements (minimal due to small motion range).\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-006\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 camera path. Universal ambient preset -- compatible with most geometries. Spec complete: incommensurate sinusoidal oscillations with fade envelopes, speed scales position only, easing modulates position envelope only, lookAt drift independent of all author params.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/meta.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-031/output.md nodes/OBJ-031/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-031): gentle_float camera path preset specification\n\nDefines the gentle_float preset using incommensurate sinusoidal\noscillations with fade envelopes for boundary continuity. Key decisions:\n- Position drift scaled by speed, lookAt drift independent\n- Easing modulates position envelope only, lookAt uses raw t\n- Universal compatibility with all 8 geometries (small motion envelope)\n- recommendedOversizeFactor 1.05 at speed=1.0\n- 28 acceptance criteria covering contract conformance, motion character,\n  speed scaling, easing behavior, determinism, and metadata\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-031 spec files"
}
[Tool Result] [master 306fe35] spec(OBJ-031): gentle_float camera path preset specification
 2 files changed, 399 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-031/output.md
The specification for OBJ-031 has been written to disk and committed. 

**Summary of the agreed spec:**

- **Motion model:** Incommensurate sinusoidal oscillations (6 independent channels — 3 for position, 3 for lookAt) with carefully chosen non-repeating frequencies
- **Boundary continuity:** `sin(π * t)` fade envelope on both position and lookAt ensures `evaluate(0) == evaluate(1) == defaultStartState`
- **Speed:** Scales position amplitude only; lookAt drift is speed-independent (preserves "life" even at near-zero speed)
- **Easing:** Modulates position envelope via `sin(π * easing(t))`; lookAt envelope always uses raw `t` (easing-independent)
- **Compatibility:** All 8 geometries (motion envelope ±0.4 units max is negligible vs. geometry bounds)
- **Oversize:** 1.05 factor at speed=1.0; OBJ-040 computes precise per-plane factors using per-axis displacements
- **28 acceptance criteria** covering OBJ-006 conformance, motion character, speed/easing behavior, determinism, and metadata
