# Specification: OBJ-027 — Push/Pull Camera Path Presets

## Summary

OBJ-027 defines two camera path presets — `slow_push_forward` and `slow_pull_back` — the defining camera motions for 2.5D projection. `slow_push_forward` moves the camera from z=5 toward z=-3, creating the "moving into the scene" effect where WebGL's perspective projection naturally produces foreshortening, vanishing points, and depth separation. `slow_pull_back` is the mathematical mirror: same trajectory reversed, creating a "revealing the scene" effect as the camera retreats. Both implement the `CameraPathPreset` interface from OBJ-006 and share a common internal path function, differing only in the mapping of `t=0`/`t=1` to start/end positions. One specification covers both because they are structurally identical save for direction.

## Interface Contract

### Exported Presets

```typescript
// src/camera/presets/push_pull.ts

import { CameraPathPreset } from '../types';

/**
 * slow_push_forward — Camera moves from z=5 toward z=-3 along
 * the Z axis (default speed=1.0, 8 world units of displacement).
 * lookAt is fixed at [0, 0, -30], deep in the scene.
 * FOV is static at 50°.
 *
 * This is the defining 2.5D motion. As the camera pushes forward,
 * planes at different Z-depths undergo differential perspective
 * shift — near planes grow faster, far planes grow slower —
 * producing the parallax depth illusion natively via WebGL's
 * perspective projection matrix.
 *
 * The default easing is ease_in_out, producing a cinematic feel
 * where the camera gently accelerates, sustains, and gently
 * decelerates. Linear easing feels robotic; ease_in_out feels
 * like a dolly on a track.
 */
export const slowPushForward: CameraPathPreset;

/**
 * slow_pull_back — Mathematical mirror of slow_push_forward.
 * Camera starts at z=-3 and retreats to z=5.
 * lookAt remains fixed at [0, 0, -30].
 * FOV is static at 50°.
 *
 * Creates a "scene reveal" — the viewer begins close to the
 * subject/environment and gradually pulls back to reveal the
 * full spatial arrangement. Effective for opening shots and
 * establishing context after a close-up.
 */
export const slowPullBack: CameraPathPreset;
```

### Preset Values — `slow_push_forward`

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'slow_push_forward'` | Seed Section 4.3 naming |
| `description` | `'Camera pushes forward along the Z axis into the scene. The defining 2.5D motion — produces natural parallax through perspective projection.'` | |
| `defaultEasing` | `'ease_in_out'` | Cinematic dolly feel. TC-09 asserts eased > linear. ease_in_out is the standard dolly feel. |
| `defaultStartState.position` | `[0, 0, 5]` | Three.js default camera position per seed Section 8.1. |
| `defaultStartState.lookAt` | `[0, 0, -30]` | Fixed deep target. See D1. |
| `defaultStartState.fov` | `50` | Seed Section 8.2 default. |
| `defaultEndState.position` | `[0, 0, -3]` | 8 units of Z displacement at speed=1.0. See D2. |
| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target. |
| `defaultEndState.fov` | `50` | No FOV animation. |
| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | All geometries where forward Z motion is meaningful. Excludes `panorama` (rotation-based). See D4. |
| `tags` | `['push', 'forward', 'z_axis', 'depth', 'cinematic', 'defining_motion']` | |

### Preset Values — `slow_pull_back`

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'slow_pull_back'` | Seed Section 4.3 naming |
| `description` | `'Camera pulls back along the Z axis away from the scene. Reveals the full spatial arrangement. The reverse of slow_push_forward.'` | |
| `defaultEasing` | `'ease_in_out'` | Same dolly feel, reversed direction. |
| `defaultStartState.position` | `[0, 0, -3]` | Begins where push_forward ends. |
| `defaultStartState.lookAt` | `[0, 0, -30]` | Same fixed target. |
| `defaultStartState.fov` | `50` | |
| `defaultEndState.position` | `[0, 0, 5]` | Ends where push_forward begins. |
| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target. |
| `defaultEndState.fov` | `50` | |
| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | Same as push_forward. |
| `tags` | `['pull', 'back', 'z_axis', 'reveal', 'cinematic']` | |

### OversizeRequirements — `slow_push_forward`

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
| `maxDisplacementY` | `0` | No vertical displacement. |
| `maxDisplacementZ` | `8` | Total Z travel: z=5 to z=-3 = 8 world units at speed=1.0. |
| `fovRange` | `[50, 50]` | FOV is constant. |
| `recommendedOversizeFactor` | `1.0` | See D3. Camera approaches all planes — no edge-reveal risk. |

### OversizeRequirements — `slow_pull_back`

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
| `maxDisplacementY` | `0` | No vertical displacement. |
| `maxDisplacementZ` | `8` | Total Z travel: z=-3 to z=5 = 8 world units at speed=1.0. |
| `fovRange` | `[50, 50]` | FOV is constant. |
| `recommendedOversizeFactor` | `1.7` | See D3. Camera retreats from all planes — planes must be oversized to fill the widening frustum. |

### evaluate() Behavior

```typescript
evaluate(t: number, params?: CameraParams): CameraFrameState
```

Both presets call `resolveCameraParams(params, 'ease_in_out')` at the top of `evaluate()` to validate and resolve params. Invalid params (speed <= 0, invalid easing name) cause an immediate throw, consistent with all presets per OBJ-006 D11.

#### Core motion model

Both presets use a single-axis linear interpolation on Z, modulated by the resolved easing function:

```
For slow_push_forward:
  startZ = 5
  endZ   = 5 - (8 * speed)
  easedT = easing(t)
  camZ   = startZ + (endZ - startZ) * easedT
         = 5 - (8 * speed * easedT)

  position(t) = [0, 0, camZ]
  lookAt(t)   = [0, 0, -30]     // constant
  fov(t)      = 50               // constant

For slow_pull_back:
  startZ = 5 - (8 * speed)
  endZ   = 5
  easedT = easing(t)
  camZ   = startZ + (endZ - startZ) * easedT
         = (5 - 8*speed) + (8 * speed * easedT)

  position(t) = [0, 0, camZ]
  lookAt(t)   = [0, 0, -30]     // constant
  fov(t)      = 50               // constant
```

**Note on `defaultStartState`/`defaultEndState` vs speed:** The static metadata corresponds to `evaluate(0)` and `evaluate(1)` with default params (speed=1.0) only. The `evaluate()` function computes actual positions using the resolved speed parameter, which may produce different boundary positions when speed != 1.0. OBJ-006's `validateCameraPathPreset` only checks evaluate(0) and evaluate(1) against static metadata with default params.

#### CameraParams handling

- **`speed`**: Scales total Z displacement. `speed=0.5` -> 4 units of travel. `speed=2.0` -> 16 units. Resolved via `resolveCameraParams()`. Must be > 0.
- **`easing`**: Replaces the default `ease_in_out` for the Z interpolation. Resolved via `resolveCameraParams()`.
- **`offset`**: Not handled inside `evaluate()`. Applied by the renderer post-evaluate, per OBJ-006 D2.

#### `defaultStartState` / `defaultEndState` consistency

Since all valid easing functions satisfy `easing(0) = 0` and `easing(1) = 1`, boundary values are easing-independent at default speed:

- push_forward: `evaluate(0, defaults)` -> `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }` = `defaultStartState`
- push_forward: `evaluate(1, defaults)` -> `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }` = `defaultEndState`
- pull_back: `evaluate(0, defaults)` -> `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }` = `defaultStartState`
- pull_back: `evaluate(1, defaults)` -> `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }` = `defaultEndState`

### Module Exports

```typescript
// src/camera/presets/push_pull.ts
export { slowPushForward, slowPullBack };
```

### Registry Integration

The assembly module imports both presets and registers them under keys `'slow_push_forward'` and `'slow_pull_back'`. Registry assembly is not this objective's responsibility. Keys must match each preset's `name` field.

## Design Decisions

### D1: Fixed lookAt at [0, 0, -30] — not tracking with camera

**Decision:** The lookAt target is a constant `[0, 0, -30]` for all values of `t`, regardless of camera position.

**Alternatives considered:**
- **Tracking lookAt** (e.g., `lookAt.z = camZ - 35`): Camera always points exactly down -Z. Viewing direction is perfectly constant at `(0, 0, -1)`.
- **Fixed lookAt at origin** `[0, 0, 0]`: Viewing angle changes significantly as camera moves past origin.

**Rationale:** For pure Z-axis motion where both camera and lookAt are on the Z axis, the viewing direction is always `(0, 0, -1)` regardless of lookAt distance — so a fixed lookAt and a tracking lookAt produce identical results. The choice of z=-30 matters only when `CameraParams.offset` displaces the camera off-axis (e.g., `offset: [2, 0, 0]`), in which case the lookAt anchors the viewing direction toward the scene's depth center (the `back_wall` region per seed Section 4.1). A very deep lookAt (z=-100) would minimize the viewing angle shift from offset; z=-30 provides a natural focal anchor within the scene's spatial range.

### D2: 8 world units of Z displacement at speed=1.0

**Decision:** Default displacement is 8 units (z=5 to z=-3).

**Rationale:** Balances three concerns:
1. **Perceptible depth effect** — Too little displacement (e.g., 2 units) and the parallax effect is barely noticeable.
2. **Safety with typical geometries** — The subject slot at z=-5 (seed Section 4.1) remains 2 units ahead of the end position at z=-3. The near_fg slot at z=-1 ends up 2 units behind the camera — this is expected behavior for foreground framing elements (particles, foliage) that slide out of view.
3. **Controllable via speed** — At speed=0.5 (4 units), the push is very conservative. At speed=1.5 (12 units), the camera passes the subject slot. OBJ-040 validates per-geometry safety.

**Visible area change at key planes (push_forward, speed=1.0, FOV=50 degrees):**

| Plane (Z) | Distance at start (cam z=5) | Distance at end (cam z=-3) | Apparent size ratio (end/start) |
|-----------|---------------------------|--------------------------|-------------------------------|
| sky (z=-50) | 55 | 47 | 1.17x |
| back_wall (z=-30) | 35 | 27 | 1.30x |
| midground (z=-15) | 20 | 12 | 1.67x |
| subject (z=-5) | 10 | 2 | 5.00x |
| near_fg (z=-1) | 6 | behind camera | N/A |

### D3: OversizeRequirements — direction-dependent factors

**Decision:** Push and pull presets have different `recommendedOversizeFactor` values because the direction of motion determines edge-reveal risk.

**Oversize factor formula:** For a plane at distance `d_start` from the camera's start position and `d_end` from the camera's end position, the plane must be sized to fill the larger of the two frustums. If the plane is sized to fill the frustum at `d_start`, the oversize factor needed is `d_end / d_start` when `d_end > d_start`, or `1.0` when `d_end <= d_start`.

**Push forward (camera approaches all planes):** As the camera moves from z=5 to z=-3, every plane in front of the camera (z < 5) gets closer. The frustum at each plane's location *narrows* as the camera approaches, so a plane sized for the start (farther) distance already overfills the end (closer) frustum. **No oversizing needed.** `recommendedOversizeFactor = 1.0`.

**Pull back (camera retreats from all planes):** As the camera moves from z=-3 to z=5, every plane gets farther away. The frustum at each plane's location *widens*, so the plane must be larger than needed at the start distance. Per-plane factors at default speed:

| Plane (Z) | d_start (cam z=-3) | d_end (cam z=5) | Factor (d_end / d_start) |
|-----------|-------------------|-----------------|--------------------------|
| sky (z=-50) | 47 | 55 | 1.17 |
| back_wall (z=-30) | 27 | 35 | 1.30 |
| midground (z=-15) | 12 | 20 | 1.67 |
| subject (z=-5) | 2 | 10 | 5.00 |

`recommendedOversizeFactor = 1.7` covers midground-distance planes (factor 1.67) and everything farther. Subject and near_fg planes at closer distances require per-plane factors computed by OBJ-040 — the single-scalar model cannot practically cover them (a factor of 5.0 would make distant planes wastefully oversized).

### D4: Panorama excluded from compatible geometries

**Decision:** Both presets exclude `panorama` from `compatibleGeometries`.

**Rationale:** Panorama geometry (seed Section 4.2) uses a wide backdrop with camera rotation (panning), not translation. A forward Z push on a panorama creates an inappropriate approach toward the cylindrical backdrop rather than the intended panning motion. Including panorama would produce a technically renderable but visually wrong result — violating C-06 (blind-authorable correctness).

### D5: Both presets in a single file — shared internal helper

**Decision:** Both presets live in `src/camera/presets/push_pull.ts` and share a common internal interpolation function. The only difference is which end of the trajectory maps to `t=0` vs `t=1`.

**Rationale:** The seed metadata states "These are mathematical mirrors with swapped start/end positions; one spec covers both." Sharing an internal helper prevents drift between the two presets and makes the mirror relationship explicit. The internal helper is not exported.

### D6: No Y-axis drift — pure Z-axis motion

**Decision:** Position interpolates only on Z. X and Y remain at 0 throughout.

**Rationale:** Seed Section 8.5 shows a slight Y drift alongside Z push as an illustrative example, not a definition of `slow_push_forward`. Multi-axis motion belongs to presets like `gentle_float` (OBJ-031) or `crane_up` (OBJ-033). Pure Z-axis makes these presets composable: `CameraParams.offset` provides static displacement, and future camera composition (OQ-06) could chain push + rise. Single-axis motion is unambiguous for blind authoring (C-06).

### D7: ease_in_out as default easing (not linear)

**Decision:** Default easing is `ease_in_out`.

**Rationale:** TC-09 asserts that eased camera paths feel more natural than linear. A physical camera dolly accelerates from rest, sustains, and decelerates to rest. `ease_in_out` maps this directly. Linear motion feels robotic. The author can override via `CameraParams.easing` if desired.

### D8: Return a new object per evaluate() call

**Decision:** Each call to `evaluate()` returns a freshly constructed `CameraFrameState` object with new `Vec3` arrays for position and lookAt.

**Rationale:** Unlike the static preset where a cached object could suffice, push/pull presets return different positions for different `t` values. Fresh objects eliminate mutation hazards (e.g., the renderer adding offset to position) with zero meaningful performance cost.

## Acceptance Criteria

### Contract Conformance (OBJ-006 test pattern)

- [ ] **AC-01:** `slowPushForward.evaluate(0)` returns `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-02:** `slowPushForward.evaluate(1)` returns `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-03:** `slowPushForward.evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-04:** `slowPushForward.evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-05:** `slowPullBack.evaluate(0)` returns `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-06:** `slowPullBack.evaluate(1)` returns `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-07:** `slowPullBack.evaluate(0)` matches its `defaultStartState` within 1e-6.
- [ ] **AC-08:** `slowPullBack.evaluate(1)` matches its `defaultEndState` within 1e-6.
- [ ] **AC-09:** For both presets, `evaluate(t)` at 100 evenly-spaced `t` in [0,1] returns no NaN, no Infinity, and FOV in (0, 180).
- [ ] **AC-10:** 1000 calls to `evaluate(0.5)` with the same params produce identical results (determinism, C-05).

### Mirror Relationship

- [ ] **AC-11:** `slowPushForward.defaultStartState` deep-equals `slowPullBack.defaultEndState`.
- [ ] **AC-12:** `slowPushForward.defaultEndState` deep-equals `slowPullBack.defaultStartState`.
- [ ] **AC-13:** For every `t` in {0, 0.25, 0.5, 0.75, 1.0}: `slowPushForward.evaluate(t).position` deep-equals `slowPullBack.evaluate(1 - t).position` (within 1e-6), when both use default params (speed=1.0, easing=ease_in_out). **Note:** This mirror relationship holds because `ease_in_out` is symmetric (`e(t) + e(1-t) = 1`). Asymmetric easings (`ease_in`, `ease_out`, `ease_out_cubic`) do NOT satisfy this property, so the mirror relationship breaks when asymmetric easings are applied via `CameraParams.easing`. This AC tests only the default symmetric easing.

### Z-Axis Interpolation

- [ ] **AC-14:** `slowPushForward.evaluate(0.5)` with default params returns a Z position between 5 and -3 (exclusive). For symmetric `ease_in_out`, Z should be approximately 1.0 (the spatial midpoint).
- [ ] **AC-15:** Z position is monotonically non-increasing across `t` in [0,1] for `slow_push_forward` with any monotonic easing (camera always moves forward, never reverses).
- [ ] **AC-16:** Z position is monotonically non-decreasing across `t` in [0,1] for `slow_pull_back` with any monotonic easing.
- [ ] **AC-17:** X and Y components of position are exactly 0 for all `t` values (pure Z-axis motion).

### lookAt and FOV Invariance

- [ ] **AC-18:** lookAt is `[0, 0, -30]` for all `t` in [0,1] for both presets.
- [ ] **AC-19:** FOV is exactly 50 for all `t` in [0,1] for both presets.

### Speed Scaling

- [ ] **AC-20:** `slowPushForward.evaluate(1, { speed: 0.5 })` returns Z position of `5 - (8 * 0.5) = 1.0`.
- [ ] **AC-21:** `slowPushForward.evaluate(1, { speed: 2.0 })` returns Z position of `5 - (8 * 2.0) = -11.0`.
- [ ] **AC-22:** The maximum Euclidean distance from start across 100 samples with `speed: 0.5` is strictly less than with `speed: 1.0` (OBJ-006 conformance pattern).

### Easing Override

- [ ] **AC-23:** `slowPushForward.evaluate(0.5, { easing: 'linear' })` returns Z = `5 - (8 * 0.5) = 1.0` (linear midpoint).
- [ ] **AC-24:** `slowPushForward.evaluate(0.5, { easing: 'ease_in' })` returns a Z value > 1.0 (ease_in is slow at start, so at t=0.5 eased time < 0.5, less displacement).
- [ ] **AC-25:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in the Z position component (OBJ-006 conformance pattern).

### Invalid Params Rejection

- [ ] **AC-26:** `evaluate(0.5, { speed: -1 })` throws an Error (via `resolveCameraParams`).
- [ ] **AC-27:** `evaluate(0.5, { speed: 0 })` throws an Error.
- [ ] **AC-28:** `evaluate(0.5, { easing: 'invalid_name' as any })` throws an Error whose message includes `'invalid_name'`.

### Preset Metadata

- [ ] **AC-29:** `slowPushForward.name` is `'slow_push_forward'` and matches `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`.
- [ ] **AC-30:** `slowPullBack.name` is `'slow_pull_back'` and matches the same regex.
- [ ] **AC-31:** Both presets have `defaultEasing` of `'ease_in_out'`.
- [ ] **AC-32:** Both presets have `compatibleGeometries` containing exactly `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` — 7 entries, excluding `panorama`.
- [ ] **AC-33:** `slowPushForward.tags` includes `'push'` and `'forward'`.
- [ ] **AC-34:** `slowPullBack.tags` includes `'pull'` and `'back'`.

### OversizeRequirements — push_forward

- [ ] **AC-35:** `slowPushForward.oversizeRequirements.maxDisplacementX === 0`.
- [ ] **AC-36:** `slowPushForward.oversizeRequirements.maxDisplacementY === 0`.
- [ ] **AC-37:** `slowPushForward.oversizeRequirements.maxDisplacementZ === 8`.
- [ ] **AC-38:** `slowPushForward.oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-39:** `slowPushForward.oversizeRequirements.recommendedOversizeFactor === 1.0`.

### OversizeRequirements — pull_back

- [ ] **AC-40:** `slowPullBack.oversizeRequirements.maxDisplacementX === 0`.
- [ ] **AC-41:** `slowPullBack.oversizeRequirements.maxDisplacementY === 0`.
- [ ] **AC-42:** `slowPullBack.oversizeRequirements.maxDisplacementZ === 8`.
- [ ] **AC-43:** `slowPullBack.oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-44:** `slowPullBack.oversizeRequirements.recommendedOversizeFactor === 1.7`.

### FOV Range Conformance

- [ ] **AC-45:** All sampled FOV values (100 points) for both presets fall within their declared `fovRange` (tolerance 1e-6).

### Full Validation

- [ ] **AC-46:** `validateCameraPathPreset(slowPushForward)` returns an empty array.
- [ ] **AC-47:** `validateCameraPathPreset(slowPullBack)` returns an empty array.

## Edge Cases and Error Handling

### evaluate() — Push Forward

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState`: position `[0, 0, 5]` |
| `t = 1` | Returns `defaultEndState`: position `[0, 0, -3]` |
| `t = 0.5` (default params) | Z near midpoint of eased curve. For symmetric `ease_in_out`, approximately z=1 |
| `t < 0` (e.g., -0.1) | Undefined behavior per OBJ-006. Callers must clamp. |
| `t > 1` (e.g., 1.5) | Undefined behavior. Preset may extrapolate beyond end position. |
| `params = undefined` | Uses defaults: speed=1.0, ease_in_out easing. |
| `params = {}` | Same as undefined — all defaults. |
| `params = { speed: 0.001 }` | Valid. Camera moves 0.008 units — nearly imperceptible. |
| `params = { speed: 0.5 }` | Camera moves 4 units (z=5 to z=1). Conservative, safe with all typical geometries. |
| `params = { speed: 2.0 }` | Camera moves 16 units (z=5 to z=-11). Passes through subject (z=-5) and midground (z=-15). OBJ-040 must flag edge reveals per geometry. |
| `params = { speed: 5.0 }` | Camera moves 40 units (z=5 to z=-35). Passes through most scene planes. Valid per CameraParams contract but will fail OBJ-040 validation for most geometries. |
| `params = { speed: -1 }` | Throws Error via `resolveCameraParams`. |
| `params = { speed: 0 }` | Throws Error via `resolveCameraParams`. |
| `params = { easing: 'linear' }` | Valid. Uniform velocity. |
| `params = { easing: 'ease_out_cubic' }` | Valid. Fast start, slow end. |
| `params = { easing: 'nonexistent' }` | Throws Error via `resolveCameraParams`, listing valid names. |
| `params = { offset: [2, 0, 0] }` | Not processed inside evaluate(). Renderer applies post-evaluate. |

### evaluate() — Pull Back

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState`: position `[0, 0, -3]` |
| `t = 1` | Returns `defaultEndState`: position `[0, 0, 5]` |
| `params = { speed: 0.5 }` | Camera starts at z=1, retreats to z=5. 4 units of travel. |
| `params = { speed: 2.0 }` | Camera starts at z=-11 (behind midground z=-15 and subject z=-5). Multiple planes begin behind the camera and gradually enter view as it retreats. |
| `params = { speed: 5.0 }` | Camera starts at z=-35 (near back_wall z=-30). Most scene planes are initially behind the camera. They come into view progressively as the camera retreats. |

### Near-Plane Collision Awareness

| Scenario | Behavior |
|----------|----------|
| Push: camera at z=-3, near_fg plane at z=-1 | near_fg is 2 units between camera and lookAt. Plane appears very large/close or partially clips through the near frustum (0.1 units). |
| Push: camera at z=-3, subject at z=-5 | Subject is 2 units ahead. At FOV=50 degrees, visible height at distance 2 is `2 * 2 * tan(25 degrees) ~ 1.86 units`. Subject plane must be at least this size to fill the view. |
| Camera passes through a plane (high speed) | WebGL renders the plane from behind (back face). `meshBasicMaterial` is double-sided by default — the plane appears mirror-flipped. This is a visual artifact — OBJ-040 should prevent this combination. |
| Pull back: camera starts behind planes (high speed) | Planes initially behind the camera are not visible. They enter view as the camera retreats past them. |

### Mirror Relationship Edge Cases

| Scenario | Behavior |
|----------|----------|
| Same speed, same symmetric easing (linear, ease_in_out, ease_in_out_cubic) | `pushForward.evaluate(t).position` equals `pullBack.evaluate(1-t).position` for all t. Symmetric easings satisfy `e(t) + e(1-t) = 1`. |
| Same speed, asymmetric easing (ease_in, ease_out, ease_out_cubic) | Mirror relationship does NOT hold. `e(t) + e(1-t) != 1` for asymmetric easings. Both presets still individually satisfy start/end boundary conditions. |
| Different speed values on push vs. pull | Mirror relationship breaks — different displacement ranges. |

## Test Strategy

### Unit Tests

**1. Boundary values:** For each preset, verify `evaluate(0)` and `evaluate(1)` match `defaultStartState` and `defaultEndState` exactly (1e-6 tolerance per component).

**2. Mirror symmetry (symmetric easing only):** For `t` in {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}, verify `pushForward.evaluate(t).position` equals `pullBack.evaluate(1-t).position` within 1e-6 (both with default params, which use symmetric `ease_in_out`). Additionally test with `{ easing: 'linear' }` (also symmetric). Verify the mirror does NOT hold with `{ easing: 'ease_in' }` — positions should differ.

**3. Monotonic Z:** Sample 100 points for push_forward with default easing. Verify each successive Z value is <= the previous (non-increasing). Same for pull_back (non-decreasing).

**4. X/Y invariance:** For 100 sample points, verify position[0] === 0 and position[1] === 0 for both presets.

**5. lookAt/FOV invariance:** For 100 sample points, verify lookAt is exactly [0, 0, -30] and fov is exactly 50.

**6. Speed scaling:** Verify `evaluate(1, { speed: 0.5 })` gives Z = 1.0 for push_forward. Verify `evaluate(1, { speed: 2.0 })` gives Z = -11.0. Verify max distance from start is less at speed=0.5 than at speed=1.0.

**7. Easing override:** Verify `evaluate(0.5, { easing: 'linear' })` gives Z = 1.0 (exact linear midpoint) for push_forward. Verify different easing produces different Z at t=0.5.

**8. Invalid params:** Verify throws for speed <= 0 and invalid easing names.

**9. Determinism:** 100 calls with same `t` and same params produce bit-identical results.

**10. OBJ-006 conformance suite:** Run the reusable conformance test pattern from `src/camera/` against both presets.

**11. OversizeRequirements differentiation:** Verify `slowPushForward.oversizeRequirements.recommendedOversizeFactor === 1.0` and `slowPullBack.oversizeRequirements.recommendedOversizeFactor === 1.7`. Verify all other oversize fields are identical between the two presets.

### Relevant Testable Claims

- **TC-03:** These presets are the primary vehicle for verifying that perspective projection produces convincing 2.5D. Test renders with push_forward should show planes undergoing natural perspective shift.
- **TC-04:** An LLM selects `"camera": "slow_push_forward"` — no XYZ coordinates required.
- **TC-05:** Push_forward on a tunnel geometry is the core test for convincing depth. (OBJ-029 `tunnel_push_forward` is the specialized version; `slow_push_forward` is also tunnel-compatible.)
- **TC-09:** Comparing push_forward with `ease_in_out` vs `linear` easing validates that eased paths feel more natural.

## Integration Points

### Depends On

| Dependency | What is imported | How it's used |
|---|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `resolveCameraParams` | Both presets conform to `CameraPathPreset`. `evaluate()` calls `resolveCameraParams()` for param validation and easing resolution. |
| **OBJ-006** (`src/camera/validate.ts`) | `validateCameraPathPreset` | Used in tests to verify both presets pass full validation. |
| **OBJ-002** (`src/interpolation/`) | `EasingName`, `EasingFn` (transitively via OBJ-006) | `defaultEasing: 'ease_in_out'` uses `EasingName`. The resolved easing function is applied to `t` inside `evaluate()`. No direct import of `interpolate()` — the interpolation is a single lerp `start + (end - start) * easedT`. |
| **OBJ-003** (`src/spatial/`) | `Vec3` (transitively via OBJ-006) | Position and lookAt values are `Vec3` tuples. |

### Consumed By

| Downstream | How it uses OBJ-027 |
|---|---|
| **Registry assembly** | Imports `slowPushForward` and `slowPullBack`, registers under keys `'slow_push_forward'` and `'slow_pull_back'`. |
| **OBJ-059** (Stage geometry tuning) | `slow_push_forward` is the primary motion for stage geometry. |
| **OBJ-069** (Edge-reveal tuning) | Push/pull presets have the most significant Z displacement among common presets. Edge-reveal validation is critical. |
| **OBJ-070/071** (SKILL.md) | Documents both presets as the primary camera motions. |
| **OBJ-040** (Edge-reveal validation) | Uses `oversizeRequirements.maxDisplacementZ = 8` and the evaluate function for trajectory sampling. Must compute per-plane factors for close-approach planes since pull_back's `recommendedOversizeFactor` (1.7) does not cover them, and push_forward's (1.0) only applies because approach direction is safe. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatibleGeometries` — 7 of 8 geometries (all except panorama). |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "slow_push_forward"` or `"camera": "slow_pull_back"` from manifest, calls `evaluate(t)` per frame. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t)`, applies offset, calls `toCameraState()`, sets Three.js camera. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        push_pull.ts     # slowPushForward and slowPullBack definitions
        static.ts        # (OBJ-026)
        index.ts         # Re-exports all presets
```

Both presets reside in a single file because they share an internal helper and are logically a single unit (mirror pair). The filename `push_pull.ts` reflects this pairing.

## Open Questions

1. **Should pull_back use a different default easing than push_forward?** A pull_back with `ease_in_out` starts slow (at the close position) and ends slow (at the far position). An `ease_out_in` would start fast and end fast, with a slow middle — potentially more dramatic for a "reveal" shot. **Recommendation:** Keep `ease_in_out` for consistency. The author can override via `CameraParams.easing`.

2. **Near_fg plane behavior during push.** At speed=1.0, near_fg (z=-1) ends up behind the camera. Should the SKILL.md warn about this? **Recommendation:** This is OBJ-040's responsibility for validation; the SKILL.md (OBJ-070/071) should note that near_fg planes are transient framing elements that may exit the view during camera pushes.

3. **Should `recommendedOversizeFactor` for pull_back be increased to cover subject-distance planes?** At speed=1.0, subject (z=-5) at start distance 2, end distance 10, needs factor 5.0. The current 1.7 covers midground and farther. **Recommendation:** Keep 1.7; OBJ-040's per-plane computation is the real safety mechanism. A factor of 5.0 would make distant planes wastefully oversized.
