# Specification: OBJ-029 — Tunnel Push Forward Camera Path Preset

## Summary

OBJ-029 defines the `tunnel_push_forward` camera path preset — a deep Z-axis push specifically tuned for the tunnel geometry (OBJ-019). Unlike `slow_push_forward` (OBJ-027), which covers 8 world units of generic Z-axis motion, `tunnel_push_forward` covers **25 world units** (z=5 to z=-20), pushing the camera deep into the tunnel corridor where walls, floor, and ceiling undergo dramatic perspective distortion — converging toward the end wall at z=-45. This preset includes a subtle Y-axis rise (from y=-0.3 to y=0) to simulate a slightly grounded starting perspective that levels out, and uses `ease_in_out_cubic` as its default easing for a heavier, more cinematic feel appropriate for the dramatic spatial motion. It implements the `CameraPathPreset` interface from OBJ-006 and is the default camera for the tunnel geometry.

## Interface Contract

### Exported Preset

```typescript
// src/camera/presets/tunnel_push.ts

import { CameraPathPreset } from '../types';

/**
 * tunnel_push_forward — Camera pushes deep into Z-space along
 * the tunnel corridor, from z=5 to z=-20 (25 world units at speed=1.0).
 * lookAt is fixed at [0, 0, -45], anchored to the end wall.
 * FOV is static at 50°.
 *
 * Includes a subtle Y-axis rise from y=-0.3 to y=0, simulating a
 * camera that starts with a slightly low, grounded perspective and
 * levels out as it moves through the tunnel. This prevents the
 * motion from feeling perfectly robotic while remaining subtle
 * enough to not draw attention away from the forward push.
 *
 * Default easing is ease_in_out_cubic, producing a heavier
 * cinematic feel — the camera accelerates smoothly, sustains
 * through the middle of the tunnel, and decelerates to a halt
 * before the end wall. The cubic curve has a longer sustained
 * middle section than ease_in_out, which suits longer spatial
 * traversals.
 *
 * This is the tunnel geometry's default camera and the preset
 * that produces the defining "traveling through a space" effect
 * described in seed Section 4.2 and tested by TC-05.
 */
export const tunnelPushForward: CameraPathPreset;
```

### Preset Values

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'tunnel_push_forward'` | Seed Section 4.3 naming. Matches `tunnelGeometry.default_camera`. |
| `description` | `'Deep Z-axis push through a tunnel corridor. Walls, floor, and ceiling converge to a vanishing point as the camera travels forward. The defining motion for enclosed-space scenes.'` | |
| `defaultEasing` | `'ease_in_out_cubic'` | Heavier feel than `ease_in_out`. See D2. |
| `defaultStartState.position` | `[0, -0.3, 5]` | Camera starts at default Z with slight downward offset. See D3. |
| `defaultStartState.lookAt` | `[0, 0, -45]` | Anchored to end wall position. See D1. |
| `defaultStartState.fov` | `50` | Seed Section 8.2 default. |
| `defaultEndState.position` | `[0, 0, -20]` | 25 units of Z displacement, Y rises to center. See D4. |
| `defaultEndState.lookAt` | `[0, 0, -45]` | Same fixed target throughout. |
| `defaultEndState.fov` | `50` | No FOV animation. |
| `compatibleGeometries` | `['tunnel']` | Tunnel-specific preset. See D5. |
| `tags` | `['push', 'forward', 'tunnel', 'z_axis', 'deep', 'corridor', 'vanishing_point', 'dramatic']` | |

### OversizeRequirements

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | No lateral displacement. |
| `maxDisplacementY` | `0.3` | Subtle Y rise from -0.3 to 0. |
| `maxDisplacementZ` | `25` | Total Z travel: z=5 to z=-20. |
| `fovRange` | `[50, 50]` | FOV is constant. |
| `recommendedOversizeFactor` | `1.0` | Camera approaches all planes (push direction). See D6. |

### evaluate() Behavior

```typescript
evaluate(t: number, params?: CameraParams): CameraFrameState
```

Calls `resolveCameraParams(params, 'ease_in_out_cubic')` at the top to validate and resolve params.

#### Core motion model

```
Given resolved speed and easing:

  easedT = easing(t)

  Z interpolation:
    startZ = 5
    endZ   = 5 - (25 * speed)
    camZ   = startZ + (endZ - startZ) * easedT
           = 5 - (25 * speed * easedT)

  Y interpolation (same easing):
    startY = -0.3 * speed    // Y offset scales with speed
    endY   = 0
    camY   = startY + (endY - startY) * easedT
           = (-0.3 * speed) + (0.3 * speed * easedT)
           = -0.3 * speed * (1 - easedT)

  position(t) = [0, camY, camZ]
  lookAt(t)   = [0, 0, -45]      // constant
  fov(t)      = 50                // constant
```

**Note on Y-axis scaling with speed:** The Y offset scales with `speed` to maintain proportional motion. At `speed=0.5`, the Y rise is from -0.15 to 0 (half as noticeable). At `speed=2.0`, the Y rise is from -0.6 to 0 (more pronounced). This keeps the Y drift perceptually proportional to the forward push magnitude, preventing situations where a short push has a disproportionately large vertical drift.

**Note on divergence from OBJ-027 pattern:** Unlike OBJ-027's `slow_push_forward`, where the start position `[0, 0, 5]` is invariant with speed and only the end position changes, this preset's Y start position varies with speed because the Y drift is anchored at the end (Y=0) rather than the start. This ensures the camera always levels out to center regardless of speed. Consequently, `evaluate(0, { speed: 0.5 })` returns `[0, -0.15, 5]` (not `[0, -0.3, 5]`). The `defaultStartState` corresponds only to default params (speed=1.0).

**Note on viewing direction tilt:** Because the camera starts at Y=-0.3 while lookAt is at Y=0 (Z=-45), the viewing direction at t=0 has a ~0.34° upward tilt (`atan(0.3 / 50)`) that corrects to perfectly level by t=1. This tilt is imperceptible but contributes to the organic "leveling out" feel. Unlike OBJ-027's pure Z-axis motion (constant `[0, 0, -1]` direction), this preset's viewing angle is not perfectly constant.

#### CameraParams handling

- **`speed`**: Scales total Z displacement AND Y offset amplitude. `speed=0.5` → 12.5 units of Z travel, 0.15 units of Y travel. `speed=2.0` → 50 units of Z travel, 0.6 units of Y travel. Must be > 0.
- **`easing`**: Replaces the default `ease_in_out_cubic` for both Z and Y interpolation (same easing function applied to both axes).
- **`offset`**: Not handled inside `evaluate()`. Applied by the renderer post-evaluate, per OBJ-006 D2.

#### defaultStartState / defaultEndState consistency

Since all valid easing functions satisfy `easing(0) = 0` and `easing(1) = 1`, boundary values are easing-independent at default speed:

- `evaluate(0, defaults)` → `{ position: [0, -0.3, 5], lookAt: [0, 0, -45], fov: 50 }` = `defaultStartState` ✓
- `evaluate(1, defaults)` → `{ position: [0, 0, -20], lookAt: [0, 0, -45], fov: 50 }` = `defaultEndState` ✓

### Module Exports

```typescript
// src/camera/presets/tunnel_push.ts
export { tunnelPushForward };
```

### Registry Integration

The assembly module imports the preset and registers it under key `'tunnel_push_forward'`. Registry assembly is not this objective's responsibility. The key must match `tunnelPushForward.name`.

## Design Decisions

### D1: Fixed lookAt at [0, 0, -45] — anchored to end wall

**Decision:** The lookAt target is a constant `[0, 0, -45]`, coinciding with the tunnel geometry's end wall position (OBJ-019).

**Rationale:** The end wall at z=-45 is the vanishing point of the tunnel. Anchoring lookAt to it means the camera always stares down the corridor toward the terminus. As the camera pushes forward, the viewing angle remains essentially unchanged (both camera and lookAt are on the Z-axis, differing only by the subtle Y offset which produces a ~0.34° tilt at t=0 that corrects to zero by t=1).

**Why not [0, 0, -30] like OBJ-027?** The `slow_push_forward` preset uses lookAt `[0, 0, -30]`, which was chosen as a generic "deep in the scene" anchor. The tunnel's end wall is at z=-45, much deeper. Using z=-30 would still produce a `-Z` viewing direction (because camera is always at Z > -30), but anchoring to the actual end wall makes the geometric relationship explicit and ensures that when `CameraParams.offset` displaces the camera laterally, the viewing direction converges toward the tunnel's actual vanishing point.

### D2: ease_in_out_cubic as default easing (not ease_in_out)

**Decision:** Default easing is `ease_in_out_cubic`, a heavier cubic curve.

**Rationale:** The tunnel push covers 25 world units — over 3× the displacement of `slow_push_forward` (8 units). The longer traversal benefits from a more gradual acceleration/deceleration profile. `ease_in_out` (quadratic) transitions relatively quickly through the acceleration phase; `ease_in_out_cubic` has a longer sustained middle velocity, which creates a sense of coasting through the tunnel's center section. This gives the viewer more time to appreciate the perspective convergence of the walls at full speed before the camera begins decelerating.

The author can override to any easing via `CameraParams.easing` if a different feel is desired (e.g., `ease_out` for a burst-then-settle motion).

**Dependency:** `ease_in_out_cubic` must be a valid `EasingName` from OBJ-002. The seed's vocabulary (Section 2, "Easing") explicitly lists it.

### D3: Subtle Y-axis rise from -0.3 to 0

**Decision:** The camera starts 0.3 units below the tunnel's vertical center (y=-0.3) and rises to the center (y=0) during the push.

**Rationale:** A perfectly centered, single-axis Z push feels robotic. The subtle Y drift adds organic quality — as if the camera is mounted on a physical dolly that rises slightly as it accelerates. The 0.3-unit offset is small relative to the tunnel's 6-unit height (5% of the cross-section, per OBJ-019's floor at Y=-3 and ceiling at Y=3), keeping it subliminal. The starting low position slightly emphasizes the floor perspective (the viewer sees slightly more floor, slightly less ceiling), which grounds the scene and enhances the spatial feel.

**Why not add X-axis drift?** Lateral drift in a narrow tunnel (8 units wide, per OBJ-019's walls at X=±4) risks asymmetric wall visibility. At x=0.3, one wall is 3.7 units away and the other 4.3 units — a noticeable asymmetry. Keeping X=0 maintains the tunnel's symmetry. X-axis displacement is available via `CameraParams.offset` if the author wants it.

**Why scale Y with speed?** At `speed=2.0`, the Z displacement doubles to 50 units. If Y remained at a fixed 0.3 offset, the rise would be barely perceptible relative to the massive forward movement. Scaling Y proportionally keeps the vertical drift's visual contribution consistent across speed values.

**Divergence from OBJ-027:** In OBJ-027, the start position is invariant with speed — only the end position changes. Here, the Y start position varies with speed because the drift is anchored at the end (Y=0), not the start. This ensures the camera always finishes at center regardless of speed. See the evaluate() behavior notes for details.

### D4: 25 units of Z displacement — calibrated to tunnel depth

**Decision:** The camera travels from z=5 to z=-20 at speed=1.0 (25 world units).

**Rationale and safety analysis:**

The tunnel geometry (OBJ-019) has:
- Corridor planes (floor, ceiling, walls) centered at z=-20 with 50-unit depth, spanning approximately z=+5 to z=-45
- End wall at z=-45
- Camera default start at z=5

At the end position z=-20:
- **Distance to end wall:** 25 units. Comfortable margin.
- **Visible cross-section at end wall** (distance=25, FOV=50°, 16:9): Height ≈ 2×25×tan(25°) ≈ 23.3 units. Width ≈ 41.5 units. The end wall is 8×6 — it fills only a fraction of the view, surrounded by the converging corridor planes. This is the intended vanishing-point effect.
- **Corridor rear edges:** At z=+5, now 25 units behind the camera. Well outside the rear frustum.
- **Wall proximity at end:** The camera is centered (x=0, y=0), walls are at x=±4, floor at y=-3, ceiling at y=+3. No risk of clipping through surfaces.

**Speed safety bounds:**

| Speed | End Z | Distance to End Wall | Risk |
|-------|-------|---------------------|------|
| 0.5 | -7.5 | 37.5 | Safe — conservative push |
| 1.0 | -20 | 25 | Safe — intended default |
| 1.5 | -32.5 | 12.5 | Cautious — end wall visible area approaches tunnel cross-section |
| 1.8 | -40 | 5 | **Risky** — camera very close to end wall |
| 2.0 | -45 | 0 | **Unsafe** — camera reaches end wall |
| >2.0 | <-45 | negative | **Broken** — camera passes through end wall |

OBJ-040 (edge-reveal validation) is responsible for flagging unsafe speed values per geometry. This preset does not clamp speed — it provides displacement metadata for OBJ-040 to compute safety.

**Recommended safe speed range for tunnel:** `0.1 ≤ speed ≤ 1.6`. At speed=1.6, end Z = 5 - 40 = -35, with 10 units of clearance to the end wall. This recommendation should be documented in SKILL.md (OBJ-071) but is NOT enforced by the preset or `resolveCameraParams()` — enforcement belongs to OBJ-040.

### D5: Compatible only with 'tunnel' geometry

**Decision:** `compatibleGeometries` contains only `['tunnel']`.

**Rationale:** This preset is specifically tuned for the tunnel geometry's spatial structure (OBJ-019):
- The 25-unit displacement is calibrated to the tunnel's 50-unit corridor depth.
- The lookAt at z=-45 targets the tunnel's end wall.
- The Y-axis starting offset of -0.3 assumes the tunnel's ±3 unit vertical range.
- The `recommendedOversizeFactor` of 1.0 assumes corridor planes that extend behind the camera start position.

Using this preset with a `stage` geometry would push the camera 25 units forward through a scene designed for 8 units of Z travel — flying past the subject, through the backdrop, and beyond. Using it with `flyover` would push horizontally through a scene designed for vertical movement. Every aspect of this preset's calibration is tunnel-specific.

If a future geometry has similar corridor structure (e.g., a `canyon` geometry), it could be added to `compatibleGeometries` after OBJ-041 validates the combination.

### D6: recommendedOversizeFactor of 1.0 — camera approaches all planes

**Decision:** `recommendedOversizeFactor` is 1.0.

**Rationale:** Following OBJ-027's D3 logic — when the camera pushes forward (approaches scene planes), the frustum at each plane's location narrows as the camera gets closer. Planes sized to fill the frustum at the camera's start distance (farthest) automatically overfill the frustum when the camera is closer. No oversizing beyond the start-distance frustum is needed.

The tunnel geometry's corridor planes are already designed (OBJ-019) to extend from z=+5 to z=-45, encompassing the camera's full range of motion. The end wall is sized to match the tunnel cross-section. Edge-reveal prevention for the tunnel depends on the planes' longitudinal extent (their 50-unit depth) rather than a width/height oversize factor.

### D7: New object per evaluate() call

**Decision:** Each call to `evaluate()` returns a freshly constructed `CameraFrameState` with new `Vec3` arrays.

**Rationale:** Position varies with both `t` and `speed`, so caching is impractical. Fresh objects prevent mutation hazards (e.g., renderer adding offset to position). Consistent with OBJ-027's D8.

### D8: Single file for a single preset

**Decision:** `tunnel_push_forward` lives in its own file `src/camera/presets/tunnel_push.ts`, not combined with other presets.

**Rationale:** Unlike OBJ-027 which pairs `slow_push_forward` and `slow_pull_back` as mathematical mirrors sharing an internal helper, `tunnel_push_forward` has no natural counterpart. A `tunnel_pull_back` preset is conceivable but would have fundamentally different spatial concerns (retreating from inside a tunnel, revealing the corridor opening behind) and would need independent tuning. If it's added later, it can share the file or get its own.

## Acceptance Criteria

### Contract Conformance (OBJ-006 test pattern)

- [ ] **AC-01:** `tunnelPushForward.evaluate(0)` returns `{ position: [0, -0.3, 5], lookAt: [0, 0, -45], fov: 50 }`.
- [ ] **AC-02:** `tunnelPushForward.evaluate(1)` returns `{ position: [0, 0, -20], lookAt: [0, 0, -45], fov: 50 }`.
- [ ] **AC-03:** `tunnelPushForward.evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-04:** `tunnelPushForward.evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-05:** For 100 evenly-spaced `t` in [0,1], `evaluate(t)` returns no NaN, no Infinity, and FOV in (0, 180).
- [ ] **AC-06:** 1000 calls to `evaluate(0.5)` with the same params produce identical results (determinism, C-05).

### Z-Axis Interpolation

- [ ] **AC-07:** Z position is monotonically non-increasing across 100 evenly-spaced `t` in [0,1] with default params (camera always moves forward, never reverses).
- [ ] **AC-08:** `evaluate(0.5, { easing: 'linear' })` returns Z = `5 - (25 * 0.5) = -7.5` (exact linear midpoint).
- [ ] **AC-09:** X component of position is exactly 0 for all `t` values (no lateral motion).

### Y-Axis Interpolation

- [ ] **AC-10:** Y position at t=0 with default params is exactly -0.3.
- [ ] **AC-11:** Y position at t=1 with default params is exactly 0.
- [ ] **AC-12:** Y position is monotonically non-decreasing across 100 evenly-spaced `t` in [0,1] with default params (camera always rises, never dips).
- [ ] **AC-13:** At `speed=0.5`, Y position at t=0 is -0.15 (Y offset scales with speed).
- [ ] **AC-14:** At `speed=2.0`, Y position at t=0 is -0.6 (Y offset scales with speed).

### lookAt and FOV Invariance

- [ ] **AC-15:** lookAt is `[0, 0, -45]` for all `t` in [0,1].
- [ ] **AC-16:** FOV is exactly 50 for all `t` in [0,1].

### Speed Scaling

- [ ] **AC-17:** `evaluate(1, { speed: 0.5 })` returns position Z of `5 - (25 * 0.5) = -7.5`.
- [ ] **AC-18:** `evaluate(1, { speed: 2.0 })` returns position Z of `5 - (25 * 2.0) = -45`.
- [ ] **AC-19:** The maximum Euclidean distance from `defaultStartState.position` across 100 samples with `speed: 0.5` is strictly less than with `speed: 1.0` (OBJ-006 conformance pattern).

### Easing Override

- [ ] **AC-20:** `evaluate(0.5, { easing: 'linear' })` returns Z = -7.5 and Y = -0.15 (linear midpoints).
- [ ] **AC-21:** `evaluate(0.5, { easing: 'ease_in' })` returns a Z value > -7.5 (ease_in is slow at start, so at t=0.5 eased time < 0.5, less displacement).
- [ ] **AC-22:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in position components (OBJ-006 conformance pattern).

### Invalid Params Rejection

- [ ] **AC-23:** `evaluate(0.5, { speed: -1 })` throws an Error (via `resolveCameraParams`).
- [ ] **AC-24:** `evaluate(0.5, { speed: 0 })` throws an Error.
- [ ] **AC-25:** `evaluate(0.5, { easing: 'invalid_name' as any })` throws an Error whose message includes `'invalid_name'`.

### Preset Metadata

- [ ] **AC-26:** `tunnelPushForward.name` is `'tunnel_push_forward'` and matches `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`.
- [ ] **AC-27:** `tunnelPushForward.defaultEasing` is `'ease_in_out_cubic'`.
- [ ] **AC-28:** `tunnelPushForward.compatibleGeometries` deep-equals `['tunnel']`.
- [ ] **AC-29:** `tunnelPushForward.tags` includes `'push'`, `'forward'`, and `'tunnel'`.
- [ ] **AC-30:** `tunnelPushForward.description` is non-empty and mentions tunnel/corridor and vanishing point.

### OversizeRequirements

- [ ] **AC-31:** `oversizeRequirements.maxDisplacementX === 0`.
- [ ] **AC-32:** `oversizeRequirements.maxDisplacementY === 0.3`.
- [ ] **AC-33:** `oversizeRequirements.maxDisplacementZ === 25`.
- [ ] **AC-34:** `oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-35:** `oversizeRequirements.recommendedOversizeFactor === 1.0`.

### FOV Range Conformance

- [ ] **AC-36:** All sampled FOV values (100 points) fall within declared `fovRange` (tolerance 1e-6).

### Full Validation

- [ ] **AC-37:** `validateCameraPathPreset(tunnelPushForward)` returns an empty array.

### Tunnel Geometry Compatibility

- [ ] **AC-38:** The camera's start Z position (5) does not exceed `DEFAULT_CAMERA.position[2]` (5), satisfying OBJ-019's D8 constraint that tunnel-compatible cameras must not position the camera at Z > 5.
- [ ] **AC-39:** At default speed=1.0, the camera's end Z position (-20) maintains at least 25 units of clearance from the tunnel's end wall (z=-45).
- [ ] **AC-40:** At speed=1.0, the camera remains within the tunnel cross-section at all times: X=0 is within [-4, 4] (wall bounds), Y ranges from -0.3 to 0 which is within [-3, 3] (floor/ceiling bounds).

## Edge Cases and Error Handling

### evaluate()

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState`: position `[0, -0.3, 5]` |
| `t = 1` | Returns `defaultEndState`: position `[0, 0, -20]` |
| `t = 0.5` (default params) | Z near eased midpoint. For `ease_in_out_cubic`, Z is approximately -7.5 (cubic ease's midpoint is close to linear midpoint). Y is approximately -0.15. |
| `t < 0` (e.g., -0.1) | Undefined behavior per OBJ-006. Callers must clamp. |
| `t > 1` (e.g., 1.5) | Undefined behavior. Preset may extrapolate beyond end position. |
| `params = undefined` | Uses defaults: speed=1.0, ease_in_out_cubic easing. |
| `params = {}` | Same as undefined — all defaults. |
| `params = { speed: 0.5 }` | Camera moves 12.5 units Z (z=5 to z=-7.5). Y rises from -0.15 to 0. Conservative, safe push. |
| `params = { speed: 1.0 }` | Default: 25 units Z (z=5 to z=-20). Safe. |
| `params = { speed: 1.5 }` | Camera moves 37.5 units Z (z=5 to z=-32.5). 12.5 units from end wall. Cautious — OBJ-040 should validate. |
| `params = { speed: 2.0 }` | Camera reaches z=-45 — coincides with end wall. **Unsafe.** OBJ-040 must flag. |
| `params = { speed: 3.0 }` | Camera at z=-70 — past end wall and corridor planes. **Broken.** OBJ-040 must reject. |
| `params = { speed: 0.001 }` | Valid. Camera moves 0.025 units. Nearly imperceptible. |
| `params = { speed: -1 }` | Throws Error via `resolveCameraParams`. |
| `params = { speed: 0 }` | Throws Error via `resolveCameraParams`. |
| `params = { easing: 'linear' }` | Valid. Uniform velocity. No acceleration/deceleration. |
| `params = { easing: 'ease_out' }` | Valid. Fast start, slow end — "launch into the tunnel" feel. |
| `params = { easing: 'nonexistent' }` | Throws Error via `resolveCameraParams`, listing valid names. |
| `params = { offset: [1, 0, 0] }` | Not processed inside evaluate(). Renderer applies post-evaluate. Shifts camera laterally in the tunnel — one wall closer, one wall farther. OBJ-040 must verify the offset doesn't move the camera outside the tunnel cross-section. |

### Near-Plane Collision Awareness

| Scenario | Behavior |
|----------|----------|
| Camera at z=-20, end wall at z=-45 | 25 units of clearance. End wall visible as a small rectangle at the vanishing point, heavily fogged. |
| High speed (1.8): camera at z=-40, end wall at z=-45 | 5 units of clearance. End wall fills a large portion of the viewport. May look flat if fog is insufficient. |
| Speed 2.0: camera at z=-45 | Camera is at the end wall plane. The plane may clip or render as a full-screen fill. OBJ-040 should prevent this. |
| Speed >2.0: camera past z=-45 | Camera is behind the end wall. The end wall renders from behind (back face of meshBasicMaterial, double-sided by default). Corridor planes' far edges (at z=-45) are now behind the camera. Visual artifacts guaranteed. |

### Offset Interactions

| Scenario | Behavior |
|----------|----------|
| `offset = [0, 0, 0]` | No change. |
| `offset = [2, 0, 0]` | Camera shifts right. Left wall at x=-4 is now 6 units away, right wall at x=4 is 2 units away. Asymmetric but valid if walls are wide enough. lookAt remains at [0,0,-45] so viewing direction angles slightly left. |
| `offset = [4, 0, 0]` | Camera at right wall position. **Risky** — wall may clip or not be visible. OBJ-040 should flag. |
| `offset = [0, 2.5, 0]` | Camera near ceiling (y=0+2.5=2.5, ceiling at y=3). 0.5 units clearance. lookAt at [0,0,-45] angles the view slightly downward. |

## Test Strategy

### Unit Tests

**1. Boundary values:** Verify `evaluate(0)` and `evaluate(1)` match `defaultStartState` and `defaultEndState` exactly (1e-6 tolerance per component).

**2. Monotonic Z:** Sample 100 points. Verify each successive Z value ≤ previous (non-increasing) with default params.

**3. Monotonic Y:** Sample 100 points. Verify each successive Y value ≥ previous (non-decreasing) with default params.

**4. X invariance:** For 100 sample points, verify position[0] === 0.

**5. lookAt/FOV invariance:** For 100 sample points, verify lookAt is `[0, 0, -45]` and fov is exactly 50.

**6. Speed scaling — Z:** Verify `evaluate(1, { speed: 0.5 }).position[2]` is -7.5. Verify `evaluate(1, { speed: 2.0 }).position[2]` is -45.

**7. Speed scaling — Y:** Verify `evaluate(0, { speed: 0.5 }).position[1]` is -0.15. Verify `evaluate(0, { speed: 2.0 }).position[1]` is -0.6.

**8. Speed scaling — max distance:** Verify maximum Euclidean distance from start at speed=0.5 < distance at speed=1.0.

**9. Easing override:** Verify `evaluate(0.5, { easing: 'linear' })` gives Z=-7.5, Y=-0.15. Verify different easing produces different position at t=0.5.

**10. Invalid params:** Verify throws for speed ≤ 0 and invalid easing names.

**11. Determinism:** 1000 calls to `evaluate(0.5)` produce identical results.

**12. Full preset validation:** `validateCameraPathPreset(tunnelPushForward)` returns empty array.

**13. Tunnel geometry constraint:** Camera start Z (5) ≤ DEFAULT_CAMERA.position[2] (5). Camera end Z at default speed (-20) is well above end wall Z (-45).

**14. OBJ-006 conformance suite:** Run the reusable conformance test pattern from OBJ-006's test strategy against `tunnelPushForward`.

### Relevant Testable Claims

- **TC-05:** "The tunnel geometry with a forward camera push produces a convincing 'traveling through a space' effect where walls visibly recede to a vanishing point." This preset is the primary test vehicle.
- **TC-04** (partial): An LLM specifies `"camera": "tunnel_push_forward"` — no XYZ coordinates needed.
- **TC-09** (partial): The `ease_in_out_cubic` default can be A/B tested against `linear` to validate TC-09's claim.

## Integration Points

### Depends on

| Upstream | What OBJ-029 imports |
|----------|---------------------|
| **OBJ-006** (Camera path type contract) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `ResolvedCameraParams`, `OversizeRequirements` types. `resolveCameraParams()` function for param resolution. `CameraPathEvaluator` type for the evaluate signature. |
| **OBJ-002** (`src/interpolation/`) | `EasingName` type (used by `resolveCameraParams`). Easing functions are accessed indirectly via `resolveCameraParams()`, not imported directly. `ease_in_out_cubic` must be a valid `EasingName`. |
| **OBJ-003** (`src/spatial/`) | `Vec3` type for position/lookAt tuples. `DEFAULT_CAMERA` constant for reference (camera start Z = 5). |
| **OBJ-019** (Tunnel geometry — value dependency) | No code imports. All concrete spatial values in this spec are calibrated to OBJ-019's frozen geometry definition: end wall at Z=-45 (lookAt target), cross-section 8 wide × 6 tall with walls at X=±4 and floor/ceiling at Y=∓3 (lateral/vertical safety bounds), corridor planes centered at Z=-20 with 50-unit depth spanning Z=+5 to Z=-45 (displacement range and safety analysis). If OBJ-019's values change, this preset's calibration must be revisited. |

### Consumed by

| Downstream | How it uses OBJ-029 |
|------------|---------------------|
| **OBJ-060** (Tunnel visual tuning) | The Director Agent reviews test renders using this preset with the tunnel geometry. May recommend adjustments to displacement, Y offset, easing, or speed bounds. |
| **OBJ-019** (Tunnel geometry) | Lists `'tunnel_push_forward'` in `compatible_cameras` and `default_camera`. OBJ-019 is already verified — the name was a forward reference that this preset fulfills. |
| **OBJ-040** (Edge-reveal validation) | Reads `oversizeRequirements` to compute whether tunnel geometry planes are large enough. Uses `evaluate()` to sample the trajectory for per-frame frustum analysis. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatibleGeometries: ['tunnel']` against the geometry registry. |
| **OBJ-071** (SKILL.md) | Documents this preset as the default/recommended camera for tunnel scenes, with speed guidance (recommended 0.5–1.5). |
| **Camera registry assembly** | Imports `tunnelPushForward` and registers under key `'tunnel_push_forward'`. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t, params)`, applies offset, calls `toCameraState()`, sets Three.js camera. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        tunnel_push.ts    # tunnelPushForward preset definition
```

The barrel export `src/camera/presets/index.ts` (or wherever presets are aggregated) must re-export from `./tunnel_push`.

## Open Questions

### OQ-A: Should the Y-axis drift be configurable via CameraParams?

The current design hard-codes the Y drift ratio (0.3 units per unit of speed) into the preset. An alternative would be to accept a `yDrift?: number` in `CameraParams`. However, `CameraParams` is intentionally minimal (speed, easing, offset) per OBJ-006 D2 — adding preset-specific fields muddies the universal contract. The author can use `offset: [0, -0.3, 0]` to start low and the renderer's static offset won't animate, but that's a different effect (constant displacement vs. animated rise).

**Recommendation:** Keep Y drift as a preset-internal behavior. If tuning (OBJ-060) reveals that the 0.3 value is wrong, revise the preset. If per-scene Y drift control becomes a requirement, consider extending `CameraParams` in a backward-compatible way (unrecognized fields are ignored per OBJ-006).

### OQ-B: Should a `tunnel_pull_back` preset be defined alongside this?

A reverse tunnel push (retreating out of the tunnel) is a natural complement. However, it has different spatial concerns (revealing the tunnel mouth behind the camera, oversizing the opening, potentially needing to see "outside" the tunnel) and would have a non-trivial `recommendedOversizeFactor` (camera retreating from planes requires oversizing, unlike the push direction). It should be a separate objective if needed, not bundled here.

### OQ-C: Should the preset enforce a max safe speed?

The analysis shows speed > ~1.8 puts the camera dangerously close to the end wall. The current design relies on OBJ-040 to validate speed per geometry. An alternative is for the preset to clamp speed internally. However, this would violate OBJ-006's contract where `speed` is a pure amplitude multiplier and presets apply it uniformly. Clamping would make the preset's behavior non-linear with respect to the author's intent. **Recommendation:** Keep validation in OBJ-040, document safe range in SKILL.md.
