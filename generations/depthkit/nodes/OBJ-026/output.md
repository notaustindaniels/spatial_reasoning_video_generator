# Specification: OBJ-026 — Static Camera Path Preset

## Summary

OBJ-026 defines the `static` camera path preset — the simplest possible camera path where the camera remains at a fixed position and orientation for the entire scene duration. It implements the `CameraPathPreset` interface from OBJ-006, returns identical `CameraFrameState` for all values of `t` in `[0, 1]`, declares compatibility with all eight scene geometries, and requires zero plane oversizing since no camera motion means no edge-reveal risk. This preset serves as the baseline for all geometries and the reference implementation for the OBJ-006 contract.

## Interface Contract

### Preset Definition

```typescript
// src/camera/presets/static.ts

import { CameraPathPreset } from '../types';

/**
 * The static camera path preset.
 * Camera remains at a fixed position looking at a fixed target.
 * FOV does not animate. All oversizing requirements are zero.
 *
 * This is the canonical reference implementation of CameraPathPreset.
 * Every geometry is compatible because a static camera cannot
 * cause edge reveals, depth mismatches, or spatial conflicts.
 */
export const staticPreset: CameraPathPreset;
```

### Preset Values

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'static'` | Matches seed Section 4.3 naming |
| `description` | `'Camera at fixed position and orientation. No movement.'` | Seed Section 4.3 description verbatim |
| `defaultEasing` | `'linear'` | Easing is irrelevant (no interpolation occurs), but `linear` is the simplest valid value |
| `defaultStartState.position` | `[0, 0, 5]` | Three.js default camera position per seed Section 8.1 |
| `defaultStartState.lookAt` | `[0, 0, 0]` | Three.js default lookAt target per seed Section 8.1 |
| `defaultStartState.fov` | `50` | Seed Section 8.2 default FOV |
| `defaultEndState` | Identical to `defaultStartState` | No motion — start and end are the same |
| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']` | All eight geometries from seed Section 4.2. A static camera is universally safe. |
| `tags` | `['static', 'fixed', 'no_motion', 'baseline']` | Discoverability for LLM preset selection |

### OversizeRequirements

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | No camera motion in any axis |
| `maxDisplacementY` | `0` | |
| `maxDisplacementZ` | `0` | |
| `fovRange` | `[50, 50]` | FOV is constant at 50 degrees |
| `recommendedOversizeFactor` | `1.0` | No motion means no edge reveal risk; planes sized exactly to frustum are sufficient |

### evaluate() Behavior

```typescript
evaluate(t: number, params?: CameraParams): CameraFrameState
```

**Behavior:** Returns the same `CameraFrameState` for every value of `t`, regardless of `params`.

**`speed` handling:** `resolveCameraParams()` is called (to validate params and throw on invalid inputs), but the resolved `speed` value is ignored. Speed scales spatial displacement; zero displacement scaled by any factor is still zero.

**`easing` handling:** `resolveCameraParams()` is called, but the resolved easing function is never applied. There is no interpolation to ease — all values are constant.

**`offset` handling:** Not applicable inside `evaluate()`. Per OBJ-006 D2, offset is applied by the scene renderer post-evaluate.

**Return value for all `t` and all valid `params`:**
```typescript
{
  position: [0, 0, 5],
  lookAt: [0, 0, 0],
  fov: 50
}
```

### Module Exports

```typescript
// src/camera/presets/static.ts
export { staticPreset };
```

### Registry Integration

The assembly module imports `staticPreset` and includes it in the `CameraPathRegistry` object under key `'static'`. The registry assembly is NOT this objective's responsibility — OBJ-026 only exports the preset. However, the key must match `staticPreset.name` (`'static'`).

## Design Decisions

### D1: Constant return value — no internal interpolation

**Decision:** `evaluate()` returns a hardcoded constant state. It does not call `interpolate()` from OBJ-002.

**Rationale:** There is nothing to interpolate. Start and end states are identical. Calling `interpolate(t, [0, totalFrames], [5, 5], easing)` would return `5` for all `t` — correct but pointless. The constant return is clearer, faster, and serves as documentation that this preset has zero motion. This also means the preset has no dependency on OBJ-002's interpolation utilities at runtime, though it still depends on OBJ-006's `resolveCameraParams()` which imports OBJ-002 types.

### D2: resolveCameraParams() still called despite ignoring results

**Decision:** `evaluate()` calls `resolveCameraParams(params, 'linear')` even though speed and easing are unused.

**Rationale:** Validation. If a manifest author passes `{ speed: -1 }` or `{ easing: 'nonsense' }`, the preset must throw — not silently accept invalid params. Calling `resolveCameraParams()` guarantees consistent validation across all presets. The cost is one function call per `evaluate()` invocation; the benefit is uniform error behavior. An implementer SHOULD cache or short-circuit if params is undefined (the common case), but this is an optimization detail, not a contract requirement.

### D3: Default position [0, 0, 5] and lookAt [0, 0, 0]

**Decision:** Use Three.js's conventional default camera position.

**Rationale:** Seed Section 8.1 states "The camera defaults to position `[0, 0, 5]` looking toward `[0, 0, 0]`." This default positions the camera in front of the scene origin, looking into negative Z. Every geometry defines its planes relative to the origin in negative Z space, so this default produces a valid view for all geometries. Per OBJ-006 D2, the manifest author can use `CameraParams.offset` to shift the camera if the geometry's default framing needs adjustment — offset is applied by the renderer post-evaluate.

### D4: FOV = 50 degrees (constant)

**Decision:** Static preset uses the seed's default FOV of 50 degrees, with no animation.

**Rationale:** Seed Section 8.2 specifies 50 degrees as the default. Geometry definitions size their planes relative to this FOV. A static camera with the default FOV is the most conservative, universally compatible choice. If an author wants a different FOV, they can use a different preset (e.g., `dolly_zoom` from OBJ-034) or a future `fovOverride` param (see OBJ-006 Open Question 1).

### D5: Compatible with all eight geometries

**Decision:** `compatibleGeometries` lists all eight geometries from seed Section 4.2.

**Rationale:** A static camera produces zero displacement in all axes. It cannot cause edge reveals, cannot move outside a geometry's spatial envelope, and cannot conflict with any spatial arrangement. There is no geometry for which a static camera is invalid. Listing all eight explicitly (rather than using a wildcard, which OBJ-006 D6 prohibits) means each new geometry added in the future must be explicitly added to this list — maintaining the auditability contract.

### D6: Speed has no observable effect

**Decision:** `speed` is validated but has no effect on output.

**Rationale:** Per OBJ-006 D3, speed scales spatial amplitude/displacement. `0 * speed = 0` for any speed value. This is mathematically correct and requires no special-casing. The manifest author CAN pass `speed: 2.0` to a static preset — it will be accepted (validated as > 0) and produce the same output as `speed: 1.0`. This is not a bug; it is the correct behavior of an amplitude multiplier on zero amplitude. The SKILL.md should note that speed has no effect on the static preset.

### D7: Easing has no observable effect

**Decision:** Easing is validated but has no effect on output.

**Rationale:** Same logic as D6. Easing remaps `t` to `t'`, but when the output is constant for all `t`, any remapping produces the same result. Valid easing names are accepted; invalid names cause a throw via `resolveCameraParams()`.

## Acceptance Criteria

### Contract Conformance (from OBJ-006 test pattern)

- [ ] **AC-01:** `evaluate(0)` returns `{ position: [0, 0, 5], lookAt: [0, 0, 0], fov: 50 }`.
- [ ] **AC-02:** `evaluate(1)` returns `{ position: [0, 0, 5], lookAt: [0, 0, 0], fov: 50 }`.
- [ ] **AC-03:** `evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-04:** `evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-05:** `defaultStartState` and `defaultEndState` are identical (deep equality).
- [ ] **AC-06:** `evaluate(t)` for 100 evenly-spaced `t` values in `[0, 1]` returns the same `CameraFrameState` for every `t` — no NaN, no Infinity, FOV in (0, 180).
- [ ] **AC-07:** 1000 calls to `evaluate(0.5)` with the same params produce identical results (determinism, C-05).

### Preset Metadata

- [ ] **AC-08:** `name` is `'static'`.
- [ ] **AC-09:** `name` matches the regex `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/` (lowercase snake_case).
- [ ] **AC-10:** `defaultEasing` is `'linear'` (a valid `EasingName`).
- [ ] **AC-11:** `compatibleGeometries` contains exactly: `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']`.
- [ ] **AC-12:** `compatibleGeometries` is non-empty.
- [ ] **AC-13:** `tags` includes `'static'`.

### OversizeRequirements

- [ ] **AC-14:** `maxDisplacementX === 0`, `maxDisplacementY === 0`, `maxDisplacementZ === 0`.
- [ ] **AC-15:** `fovRange` is `[50, 50]`.
- [ ] **AC-16:** `recommendedOversizeFactor === 1.0`.
- [ ] **AC-17:** All sampled FOV values (100 points) fall within `fovRange` (tolerance 1e-6).

### CameraParams Handling

- [ ] **AC-18:** `evaluate(0.5, undefined)` returns the same state as `evaluate(0.5)`.
- [ ] **AC-19:** `evaluate(0.5, { speed: 2.0 })` returns the same state as `evaluate(0.5)` (speed has no effect on zero displacement).
- [ ] **AC-20:** `evaluate(0.5, { easing: 'ease_in_out' })` returns the same state as `evaluate(0.5)` (easing has no effect on constant output).
- [ ] **AC-21:** `evaluate(0.5, { speed: -1 })` throws an Error (via `resolveCameraParams`).
- [ ] **AC-22:** `evaluate(0.5, { speed: 0 })` throws an Error (via `resolveCameraParams`).
- [ ] **AC-23:** `evaluate(0.5, { easing: 'invalid_name' as any })` throws an Error whose message includes `'invalid_name'`.

### Validation

- [ ] **AC-24:** `validateCameraPathPreset(staticPreset)` returns an empty array (no errors).

### OBJ-006 Conformance Test Pattern (all must pass)

- [ ] **AC-25:** Boundary start check passes.
- [ ] **AC-26:** Boundary end check passes.
- [ ] **AC-27:** Continuity check (100 points, no NaN/Infinity) passes.
- [ ] **AC-28:** FOV range check passes.
- [ ] **AC-29:** Determinism check (100 calls, same t, same output) passes.
- [ ] **AC-30:** Full `validateCameraPathPreset` passes.
- [ ] **AC-31:** Speed scaling check: max Euclidean distance between `evaluate(t, { speed: 0.5 }).position` and `defaultStartState.position` over 100 samples equals 0 (both maximums are zero — the exception case in OBJ-006's conformance pattern).
- [ ] **AC-32:** Easing override check: `evaluate(0.5, { easing: 'linear' })` equals `evaluate(0.5, { easing: 'ease_in' })` (the exception case for static presets in OBJ-006's conformance pattern).

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `{ position: [0,0,5], lookAt: [0,0,0], fov: 50 }` |
| `t = 1` | Same as above |
| `t = 0.5` | Same as above |
| `t = 0.001` | Same as above |
| `t = 0.999` | Same as above |
| `t < 0` (e.g., `-0.1`) | Undefined behavior per OBJ-006. Preset MAY return the constant state (since there's no interpolation to go wrong), but callers must clamp. |
| `t > 1` (e.g., `1.5`) | Same as above — undefined behavior. |
| `params = undefined` | Returns constant state. No error. |
| `params = {}` | Returns constant state. No error. |
| `params = { speed: 0.5 }` | Returns constant state. Speed validated (> 0) but has no effect. |
| `params = { speed: 100 }` | Returns constant state. Validated, no effect. |
| `params = { speed: -1 }` | Throws Error: speed must be > 0. |
| `params = { speed: 0 }` | Throws Error: speed must be > 0. |
| `params = { easing: 'ease_out_cubic' }` | Returns constant state. Validated, no effect. |
| `params = { easing: 'nonexistent' }` | Throws Error, lists valid easing names. |
| `params = { offset: [1, 0, 0] }` | Returns constant state unchanged. Offset is applied by the renderer post-evaluate, not inside evaluate(). |
| `params = { speed: 2.0, easing: 'ease_in', offset: [0, 1, 0] }` | Returns constant state. All params validated; speed and easing have no effect; offset not applied here. |

## Test Strategy

### Unit Tests for `staticPreset`

1. **Constant output verification:** Call `evaluate()` at `t = 0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0`. Assert all return values are deep-equal to `{ position: [0,0,5], lookAt: [0,0,0], fov: 50 }`.

2. **Start/end state consistency:** Assert `evaluate(0)` deep-equals `defaultStartState`. Assert `evaluate(1)` deep-equals `defaultEndState`. Assert `defaultStartState` deep-equals `defaultEndState`.

3. **Determinism:** Call `evaluate(0.5)` 100 times, assert all results are identical (reference equality of numeric values).

4. **Speed invariance:** Call `evaluate(0.5, { speed: 0.5 })` and `evaluate(0.5, { speed: 2.0 })`. Assert both equal `evaluate(0.5)`.

5. **Easing invariance:** Call `evaluate(0.5, { easing: 'linear' })` and `evaluate(0.5, { easing: 'ease_in_out_cubic' })`. Assert both equal `evaluate(0.5)`.

6. **Invalid params rejection:** Assert `evaluate(0.5, { speed: -1 })` throws. Assert `evaluate(0.5, { speed: 0 })` throws. Assert `evaluate(0.5, { easing: 'bogus' as any })` throws.

7. **Metadata validation:** Assert `name === 'static'`. Assert `defaultEasing === 'linear'`. Assert `compatibleGeometries` has length 8 and includes all geometry names. Assert `tags` includes `'static'`.

8. **OversizeRequirements validation:** Assert all displacements are 0. Assert `fovRange` is `[50, 50]`. Assert `recommendedOversizeFactor` is 1.0.

9. **Full contract conformance:** Run OBJ-006's reusable conformance test suite against `staticPreset`. This covers boundary checks, continuity, FOV range, determinism, and `validateCameraPathPreset`.

### Relevant Testable Claims

- **TC-04:** The static preset is selectable by name without XYZ coordinates.
- **TC-06:** Static preset contributes to deterministic output (constant values, no randomness).
- **TC-08:** Static preset's universal compatibility enables coverage of all geometry types.
- **TC-09:** Static preset is the control case for easing comparison (easing has no visible effect on a static camera, confirming that easing only affects motion paths).

## Integration Points

### Depends On

| Dependency | What is imported | How it's used |
|---|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `resolveCameraParams` | `staticPreset` conforms to `CameraPathPreset`. `evaluate()` calls `resolveCameraParams()` for param validation. |
| **OBJ-006** (`src/camera/validate.ts`) | `validateCameraPathPreset` | Used in tests to verify the preset passes full validation. |
| **OBJ-002** (`src/interpolation/`) | `EasingName` (transitively via OBJ-006) | `defaultEasing: 'linear'` uses the `EasingName` type. No direct import of interpolation functions needed — `resolveCameraParams` handles easing resolution internally. |
| **OBJ-003** (`src/spatial/`) | `Vec3` (transitively via OBJ-006) | Position and lookAt values are `Vec3` tuples. |

### Consumed By

| Downstream | How it uses OBJ-026 |
|---|---|
| **Registry assembly** | Imports `staticPreset` and registers under key `'static'`. |
| **OBJ-059 through OBJ-066** (Visual tuning objectives) | `static` is listed in their dependencies as a compatible camera path for their respective geometries. Every geometry's tuning cycle should include at least one test render with the static preset as a baseline. |
| **OBJ-040** (Edge-reveal validation) | Uses `oversizeRequirements` (all zeros) — static preset trivially passes edge-reveal validation for any geometry. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatibleGeometries` — `static` is compatible with all geometries. |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "static"` from manifest, calls `evaluate(t)` per frame. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t)`, applies offset (if any), calls `toCameraState()`. |
| **SKILL.md** (OBJ-070/071) | Documents the static preset as the simplest camera option — recommended when the visual focus should be entirely on the scene content, not camera motion. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        static.ts       # staticPreset definition and export
        index.ts         # Re-exports all presets; assembles registry
```

The `presets/` subdirectory keeps individual preset implementations separate from the type contract (`src/camera/types.ts`) and registry infrastructure (`src/camera/registry.ts`). Each preset (OBJ-026 through OBJ-034) gets its own file in `presets/`. The `presets/index.ts` barrel re-exports all presets and may also assemble the canonical `CameraPathRegistry` object.

## Open Questions

1. **Should the static preset's default position be geometry-aware?** Currently the default is `[0, 0, 5]` (Three.js convention). Some geometries may have their content centered at different positions — e.g., a tunnel geometry's spatial midpoint might be at `[0, 0, -15]`, not `[0, 0, 0]`. With the static preset at `[0, 0, 5]`, the camera would see the tunnel from outside. **Resolution approach:** The geometry definitions (OBJ-005) are responsible for placing their planes relative to the camera's expected position. The seed's tunnel geometry example (Section 8.6) places planes at negative Z, which is visible from the default `[0, 0, 5]` camera position. If a geometry needs the camera elsewhere, the manifest author uses `CameraParams.offset` or selects a geometry-specific preset (e.g., `tunnel_push_forward`). The static preset's universal default of `[0, 0, 5]` is intentionally simple. **No action needed for OBJ-026.**

2. **Should the `description` field include usage guidance for the SKILL.md?** E.g., "Use when scene content should be the sole focus; no camera movement to distract." **Recommendation:** Keep `description` factual and terse. The SKILL.md (OBJ-070/071) can elaborate with usage guidance. The `tags` field provides machine-readable categorization for LLM preset selection.

3. **Return object mutability.** Since `evaluate()` always returns the same values, an implementer may be tempted to return a shared singleton object. If a consumer (e.g., the renderer applying offset) mutates the returned object (e.g., `state.position[0] += offset[0]`), this would corrupt subsequent calls. This is an OBJ-006-level contract concern (whether `evaluate()` must return fresh objects), not specific to OBJ-026, but the static preset is uniquely vulnerable to this optimization pitfall. **Recommendation for implementer:** Either return a new object each call, or return a deeply frozen object. This should be addressed at the OBJ-006 contract level if it becomes a pattern across presets.
