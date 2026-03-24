# Specification: OBJ-006 — Camera Path Type Contract

## Summary

OBJ-006 defines the TypeScript type system for camera path presets in depthkit. A camera path preset is a named, self-contained unit that maps normalized time `t ∈ [0, 1]` to a complete camera state (`position`, `lookAt`, `fov`) and carries metadata for validation, edge-reveal prevention, and blind authoring. This is the Tier 1 contract that all downstream camera path preset implementations (OBJ-026 through OBJ-034) conform to, and that the scene sequencer (OBJ-010), edge-reveal validator (OBJ-040), and geometry-camera compatibility validator (OBJ-041) consume.

## Interface Contract

### Core Types

```typescript
// src/camera/types.ts

import { Vec3, CameraState } from '../spatial/types';
import { EasingName, EasingFn } from '../interpolation/easings';

/**
 * The path-controlled subset of camera state at a single moment in time.
 * Returned by a camera path's evaluate() function.
 *
 * Relationship to CameraState (OBJ-003): CameraFrameState contains only
 * the properties that a camera PATH controls — position, lookAt, fov.
 * The complete CameraState also includes aspectRatio, near, and far,
 * which are composition-level constants (set from the manifest's
 * composition.width/height and the geometry's near/far recommendations).
 * The scene renderer constructs a full CameraState by combining
 * CameraFrameState from the path with composition-level values.
 * Use toCameraState() to perform this merge.
 */
export interface CameraFrameState {
  /** Camera position in world space [x, y, z] */
  position: Vec3;
  /** Camera lookAt target in world space [x, y, z] */
  lookAt: Vec3;
  /** Vertical field of view in degrees. Must be in (0, 180). */
  fov: number;
}

/**
 * Combines path-controlled camera state with composition-level constants
 * to produce a complete CameraState (as defined by OBJ-003).
 *
 * @param frame - Path output from evaluate().
 * @param aspectRatio - Composition width / height (e.g., 16/9).
 * @param near - Near clipping plane distance. Default: 0.1 (from DEFAULT_CAMERA).
 * @param far - Far clipping plane distance. Default: 100 (from DEFAULT_CAMERA).
 * @returns Complete CameraState suitable for Three.js camera configuration.
 */
export function toCameraState(
  frame: CameraFrameState,
  aspectRatio: number,
  near?: number,
  far?: number
): CameraState;

/**
 * Parameters the manifest author can pass to customize a camera path
 * at the scene level. These override the preset's defaults.
 *
 * Presets receive RESOLVED params (via resolveCameraParams), never raw
 * CameraParams. See ResolvedCameraParams.
 *
 * Unrecognized fields are ignored (not rejected) — this allows presets
 * to evolve without breaking existing manifests.
 */
export interface CameraParams {
  /**
   * Amplitude/displacement multiplier. Scales the spatial intensity
   * of the path's motion, NOT its temporal rate.
   *
   * For linear paths (push/pull/track): scales total displacement.
   *   speed=0.5 on a 25-unit Z push -> 12.5-unit push.
   * For oscillating paths (gentle_float): scales amplitude.
   *   speed=0.5 -> half the drift range in each axis.
   * For FOV-animating paths (dolly_zoom): scales FOV delta.
   *   speed=0.5 -> half the FOV change.
   *
   * The temporal easing curve is unaffected. A speed=0.5 path still
   * starts and ends at the same normalized times — it just covers
   * less spatial ground.
   *
   * Must be > 0. Default: 1.0.
   */
  speed?: number;

  /**
   * Easing override for the primary motion.
   * Replaces the preset's default easing.
   */
  easing?: EasingName;

  /**
   * Additive offset to the camera's position, in world units.
   * Applied OUTSIDE evaluate() by the scene renderer — presets
   * never see this value. The renderer adds offset to the position
   * returned by evaluate() before setting the Three.js camera.
   *
   * lookAt is NOT shifted. This means offset creates a slight
   * viewing angle change — the camera is displaced but still
   * looks at the scene's focal point. This is intentional for
   * framing adjustments (e.g., shift camera right to reframe
   * the subject).
   *
   * Edge-reveal implication: offset displaces the frustum.
   * OBJ-040 must add abs(offset[i]) to the path's displacement
   * in each axis when computing required plane sizes.
   *
   * Default: [0, 0, 0].
   */
  offset?: Vec3;
}

/**
 * Resolved and validated CameraParams, ready for preset consumption.
 * Produced by resolveCameraParams(). Presets receive this, not raw CameraParams.
 *
 * Note: offset is NOT included here because it is applied outside
 * evaluate() by the renderer. Presets only need speed and easing.
 */
export interface ResolvedCameraParams {
  /** Guaranteed > 0. */
  speed: number;
  /** Resolved easing function. */
  easing: EasingFn;
}

/**
 * Resolves raw CameraParams into validated, defaulted values.
 * Presets call this at the top of their evaluate() to get clean inputs.
 *
 * @param params - Raw params from manifest (may be undefined).
 * @param defaultEasing - The preset's own default easing name.
 * @returns Resolved params with defaults applied.
 * @throws {Error} if speed <= 0 or easing is not a valid EasingName.
 */
export function resolveCameraParams(
  params: CameraParams | undefined,
  defaultEasing: EasingName
): ResolvedCameraParams;

/**
 * Oversizing metadata that a camera path preset provides so that
 * OBJ-040 (edge-reveal validation) and geometry definitions can
 * compute the minimum plane sizes needed to prevent edge reveals.
 *
 * All displacement values describe the MAXIMUM extent of camera motion
 * in each axis, in world units, at the preset's default speed (speed=1.0).
 *
 * For speed != 1.0, effective displacements scale linearly:
 *   effectiveDisplacement = maxDisplacement * speed
 *
 * These values do NOT account for CameraParams.offset. OBJ-040 must
 * add abs(offset[i]) to each axis displacement when validating.
 */
export interface OversizeRequirements {
  /**
   * Maximum camera displacement along the X axis (world units).
   * Must be >= 0.
   */
  maxDisplacementX: number;

  /**
   * Maximum camera displacement along the Y axis (world units).
   * Must be >= 0.
   */
  maxDisplacementY: number;

  /**
   * Maximum camera displacement along the Z axis (world units).
   * Must be >= 0. Consumed by OBJ-040 to compute worst-case
   * visible area at each plane's depth.
   */
  maxDisplacementZ: number;

  /**
   * The FOV range across the path's duration: [min, max] in degrees.
   * Both values must be in (0, 180). min <= max.
   * For paths with no FOV animation, min === max.
   */
  fovRange: readonly [number, number];

  /**
   * Recommended uniform oversize factor for "simple" plane sizing.
   * A single scalar >= 1.0 that is sufficient to prevent edge reveals
   * for ALL planes in all compatible geometries, assuming planes are
   * sized to the frustum at their distance from the camera's start
   * position and speed=1.0.
   *
   * OBJ-040 may compute more precise per-plane factors using the
   * displacement values above. This scalar is a safe upper bound.
   */
  recommendedOversizeFactor: number;
}

/**
 * A camera path evaluation function.
 * Given normalized time t in [0, 1], returns the path-controlled camera state.
 *
 * Contract:
 * - t = 0 returns the camera's start state.
 * - t = 1 returns the camera's end state.
 * - Values are continuous between 0 and 1 (no discontinuities).
 * - Behavior for t outside [0, 1] is undefined. Callers must clamp.
 * - CameraParams.offset is NOT handled here — it is applied by the
 *   scene renderer after evaluate() returns.
 *
 * Implementations should call resolveCameraParams() at the top of
 * their function body to get validated speed and easing values.
 */
export type CameraPathEvaluator = (
  t: number,
  params?: CameraParams
) => CameraFrameState;

/**
 * The complete definition of a camera path preset.
 * This is the type that all OBJ-026 through OBJ-034 implementations export.
 */
export interface CameraPathPreset {
  /** Unique preset name. Must match the key in the registry. Lowercase snake_case. */
  name: string;

  /**
   * Human-readable description for SKILL.md and error messages.
   * Should describe the visual effect in 1-2 sentences.
   */
  description: string;

  /**
   * The evaluation function. Given t in [0, 1] and optional params,
   * returns the path-controlled camera state.
   */
  evaluate: CameraPathEvaluator;

  /**
   * The camera state at t=0 with default params (speed=1, default easing, no offset).
   * Redundant with evaluate(0), but provided as static data for
   * fast access during validation without calling evaluate().
   */
  defaultStartState: CameraFrameState;

  /**
   * The camera state at t=1 with default params.
   * Redundant with evaluate(1), but provided as static data.
   */
  defaultEndState: CameraFrameState;

  /**
   * Default easing applied to the primary motion.
   * Can be overridden by CameraParams.easing in the manifest.
   */
  defaultEasing: EasingName;

  /**
   * Names of scene geometries this path is designed to work with.
   * The geometry-camera compatibility validator (OBJ-041) uses this
   * to reject invalid combinations in the manifest.
   *
   * Must be non-empty. List geometry names explicitly — no wildcards.
   * Until OBJ-005 finalizes geometry names, use provisional names
   * from seed Section 4.2: 'stage', 'tunnel', 'canyon', 'flyover',
   * 'diorama', 'portal', 'panorama', 'close_up'.
   *
   * When a new geometry is added, each preset must explicitly declare
   * compatibility with it (or not). This keeps compatibility auditable.
   *
   * NOTE: validateCameraPathPreset checks only for non-emptiness.
   * Geometry name existence validation belongs to OBJ-041, which
   * cross-references against the geometry registry.
   */
  compatibleGeometries: readonly string[];

  /**
   * Oversizing metadata for edge-reveal prevention.
   * Describes the spatial envelope of the camera's motion.
   */
  oversizeRequirements: OversizeRequirements;

  /**
   * Tags for categorizing and searching presets in SKILL.md
   * and for LLM-assisted preset selection. Lowercase.
   * Examples: ['push', 'forward', 'dramatic'], ['ambient', 'subtle', 'float'].
   */
  tags: readonly string[];
}
```

### Registry

```typescript
// src/camera/registry.ts

import { CameraPathPreset } from './types';

/**
 * Type-safe registry of all camera path presets.
 * Downstream objectives (OBJ-026 through OBJ-034) register their
 * presets here. The registry is frozen at build time — no runtime mutation.
 *
 * Keys are preset names (lowercase snake_case). Values are CameraPathPreset objects.
 */
export type CameraPathRegistry = Readonly<Record<string, CameraPathPreset>>;

/**
 * Retrieves a camera path preset by name.
 * @param registry - The camera path registry to search.
 * @param name - The preset name.
 * @returns The CameraPathPreset.
 * @throws {Error} if name is not found. Error message includes the
 *   invalid name and lists all available preset names.
 */
export function getCameraPath(
  registry: CameraPathRegistry,
  name: string
): CameraPathPreset;

/**
 * Type guard: checks if a name exists in the given registry.
 */
export function isCameraPathName(
  registry: CameraPathRegistry,
  name: string
): boolean;

/**
 * Returns all preset names in the registry, sorted alphabetically.
 */
export function listCameraPathNames(
  registry: CameraPathRegistry
): readonly string[];

/**
 * Returns all presets compatible with a given geometry name.
 * @param registry - The camera path registry.
 * @param geometryName - The geometry to filter by.
 * @returns Array of compatible CameraPathPreset objects. Empty if none match.
 */
export function getCameraPathsForGeometry(
  registry: CameraPathRegistry,
  geometryName: string
): readonly CameraPathPreset[];
```

### Validation Utility

```typescript
// src/camera/validate.ts

import { CameraPathPreset, CameraParams } from './types';

/**
 * Validates that a CameraPathPreset satisfies its own internal contract.
 * Used during development/testing — NOT runtime manifest validation.
 *
 * Checks:
 * 1. evaluate(0) matches defaultStartState (within tolerance 1e-6 per component).
 * 2. evaluate(1) matches defaultEndState (within tolerance 1e-6 per component).
 * 3. FOV is within (0, 180) at 100 evenly-spaced sample points in [0, 1].
 * 4. evaluate() returns finite values (no NaN/Infinity) for position, lookAt,
 *    and fov at 100 sample points.
 * 5. oversizeRequirements.recommendedOversizeFactor >= 1.0.
 * 6. oversizeRequirements.fovRange[0] <= fovRange[1], both in (0, 180).
 * 7. oversizeRequirements displacement values are >= 0.
 * 8. name is non-empty, lowercase snake_case (regex: /^[a-z][a-z0-9]*(_[a-z0-9]+)*$/).
 * 9. compatibleGeometries is non-empty.
 *    NOTE: does NOT validate that geometry names are real — that's OBJ-041.
 * 10. defaultEasing is a valid EasingName.
 * 11. All sampled FOV values fall within oversizeRequirements.fovRange (tolerance 1e-6).
 *
 * @param preset - The preset to validate.
 * @returns Array of validation error strings. Empty array = valid.
 */
export function validateCameraPathPreset(
  preset: CameraPathPreset
): readonly string[];

/**
 * Validates CameraParams from a manifest scene.
 * Checks:
 * 1. speed > 0 (if provided).
 * 2. easing is a valid EasingName (if provided).
 * 3. offset contains finite values (if provided).
 *
 * @param params - The params to validate. undefined treated as all-defaults (valid).
 * @returns Array of validation error strings. Empty array = valid.
 */
export function validateCameraParams(
  params: CameraParams | undefined
): readonly string[];
```

### Module Exports

```typescript
// src/camera/index.ts

export type {
  CameraFrameState,
  CameraParams,
  ResolvedCameraParams,
  OversizeRequirements,
  CameraPathEvaluator,
  CameraPathPreset,
} from './types';

export {
  toCameraState,
  resolveCameraParams,
} from './types';

export type { CameraPathRegistry } from './registry';

export {
  getCameraPath,
  isCameraPathName,
  listCameraPathNames,
  getCameraPathsForGeometry,
} from './registry';

export {
  validateCameraPathPreset,
  validateCameraParams,
} from './validate';
```

## Design Decisions

### D1: Evaluation function over keyframe data

**Decision:** Camera path presets define an `evaluate(t, params) => CameraFrameState` function rather than exposing raw keyframe data that the caller interpolates.

**Rationale:** Downstream presets vary dramatically in complexity. `static` (OBJ-026) returns the same state for all `t`. `slow_push_forward` (OBJ-027) is linear Z interpolation. `gentle_float` (OBJ-031) involves multi-axis sinusoidal drift. `dolly_zoom` (OBJ-034) requires coordinated position + FOV animation. A keyframe-based interface would either be too simple for complex presets or too complex for simple ones. The evaluation function lets each preset own its interpolation logic (using OBJ-002 utilities internally) while presenting a uniform interface.

**Trade-off:** Callers cannot introspect the trajectory without sampling. Mitigated by `defaultStartState`, `defaultEndState`, and `oversizeRequirements` as static metadata.

### D2: CameraParams split — speed and easing inside evaluate(), offset outside

**Decision:** `CameraParams` has three fields: `speed`, `easing`, and `offset`. Speed and easing are handled inside `evaluate()` (via `resolveCameraParams()`). Offset is applied by the scene renderer *after* `evaluate()` returns — presets never see it.

**Rationale for the split:**
- **Speed** must be inside `evaluate()` because it changes how the preset computes positions (scaling displacement/amplitude). Only the preset knows its internal motion structure.
- **Easing** must be inside `evaluate()` because it changes the temporal mapping from `t` to eased time. Only the preset knows where to apply it.
- **Offset** is a uniform post-transform — add `[ox, oy, oz]` to position. This is identical for every preset. Putting it inside `evaluate()` would force every preset to implement the same addition, creating boilerplate. Putting it outside means one line in the renderer: `position = add(evaluate(t, params).position, resolvedOffset)`.

**Consequence:** `ResolvedCameraParams` contains only `speed` and `easing` (not offset). The renderer resolves offset separately from `CameraParams.offset ?? [0, 0, 0]` and applies it post-evaluate. Offset validation is handled by `validateCameraParams()` (pre-flight manifest validation), not by `resolveCameraParams()`. OBJ-040 must account for offset when computing edge-reveal margins (add `abs(offset[i])` to each axis displacement).

### D3: Speed scales spatial amplitude, not temporal rate

**Decision:** `speed` is a displacement/amplitude multiplier. `speed: 0.5` means the camera covers half the spatial distance/range. The temporal easing curve is unaffected — the path still starts at t=0 and ends at t=1 with the same easing shape.

**Rationale:** For linear paths (push/pull/track), both interpretations (half displacement vs. time remapping) produce similar results. But for oscillating paths (`gentle_float`), they diverge dramatically:
- Half amplitude: same number of oscillations, smaller range. The path feels "calmer."
- Half speed (time remap): reaches only the midpoint of the oscillation pattern. The path feels "cut short."

Amplitude scaling is more intuitive for LLM authors: "make it more/less intense" maps naturally to speed. Time remapping is harder to reason about. The seed's manifest example shows `"speed": 1.0` as an intensity control, not a playback rate.

**Per-preset application:** Each preset applies speed to its own motion structure:
- Linear Z push: `totalDisplacement * speed`
- Sinusoidal drift: `amplitude * speed` per axis
- Dolly zoom: `zDisplacement * speed` for position, `fovDelta * speed` for FOV

### D4: OversizeRequirements as structured metadata, not a single scalar

**Decision:** Presets expose per-axis displacement maximums and FOV range, plus a convenience `recommendedOversizeFactor` scalar.

**Rationale:** OBJ-040 needs per-axis displacements to compute precise per-plane oversize factors. A lateral track only needs horizontal oversizing, not vertical. The `recommendedOversizeFactor` convenience scalar serves simpler consumers that want a safe margin without the full OBJ-040 algorithm. It must be a safe upper bound for the worst-case plane in any compatible geometry at speed=1.0.

**Interaction with CameraParams:** Effective displacements are `maxDisplacement * speed`. Offset adds `abs(offset[i])` per axis. OBJ-040 must account for both.

### D5: Static defaultStartState and defaultEndState alongside evaluate()

**Decision:** Presets provide pre-computed start and end states as static data, redundant with `evaluate(0)` and `evaluate(1)`.

**Rationale:** Validation (OBJ-041) needs quick compatibility checks. Having start/end states as static data means validators don't need to reason about evaluate()'s side effects. Also serves as self-documentation. `validateCameraPathPreset` checks consistency between the static data and `evaluate()`.

### D6: compatibleGeometries as explicit string enumeration

**Decision:** `compatibleGeometries` is `readonly string[]` with explicit geometry name enumeration. No wildcards. Must be non-empty.

**Rationale:** Explicit enumeration keeps compatibility auditable. When a new geometry is added, each preset must explicitly declare compatibility. Implicit universal compatibility via `['*']` risks silent false-positive compatibility with untested geometries.

**Provisional names:** Until OBJ-005 finalizes, presets use seed Section 4.2 names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`. `validateCameraPathPreset` checks only for non-emptiness. Geometry name existence validation belongs to OBJ-041.

### D7: Registry takes registry as parameter, not a singleton

**Decision:** `getCameraPath(registry, name)` accepts the registry as an argument.

**Rationale:** Testability. Unit tests can pass mock registries. Avoids import-order issues. The canonical registry is assembled once by the module that imports all preset implementations and passed through the system.

### D8: Vec3 from OBJ-003, not Three.js types

**Decision:** All spatial types use `Vec3` from `src/spatial/types.ts`.

**Rationale:** JSON-serializable for Puppeteer message passing. Renderer-agnostic. Consistent with OBJ-003's D1 (pure math module, no Three.js dependency).

### D9: FOV always returned from evaluate()

**Decision:** `CameraFrameState` always includes `fov`, even for static-FOV paths.

**Rationale:** Eliminates conditionals in the renderer. For static-FOV paths, `evaluate()` returns the same value for all `t`. `OversizeRequirements.fovRange` with `min === max` signals no animation.

### D10: CameraFrameState is path-controlled subset of CameraState

**Decision:** `CameraFrameState` (position, lookAt, fov) is the path-controlled subset. `CameraState` from OBJ-003 adds aspectRatio, near, far (composition-level). `toCameraState()` merges them.

**Rationale:** Camera paths should not concern themselves with aspect ratio or clipping planes — these are determined by the manifest's composition settings and the geometry's spatial bounds. The clean separation avoids coupling paths to composition config. The explicit `toCameraState()` bridge function makes the merge point visible rather than leaving each consumer to figure it out.

### D11: resolveCameraParams() eliminates boilerplate across presets

**Decision:** A shared `resolveCameraParams(params, defaultEasing)` function resolves raw `CameraParams` into a `ResolvedCameraParams` with validated `speed: number` and `easing: EasingFn`.

**Rationale:** Without this, every preset must: check if params is undefined, default speed to 1.0, resolve easing name to function via `getEasing()`. This is boilerplate duplicated across 10+ presets. `resolveCameraParams` centralizes it. The `defaultEasing` parameter lets each preset supply its own default. Note: `resolveCameraParams` does NOT validate or handle `offset` — offset validation belongs to `validateCameraParams()`, and offset application belongs to the renderer.

### D12: Isomorphic module — no platform-specific APIs

**Decision:** All code in `src/camera/` must be pure JavaScript/TypeScript with no Node.js-specific APIs (`process`, `fs`, `Buffer`) and no browser-specific APIs (`window`, `document`, `requestAnimationFrame`).

**Rationale:** Like OBJ-002's interpolation module (D1), the camera module runs in both Node.js (validation, scene sequencing) and headless Chromium (frame rendering via evaluate()). The build system bundles this module into the page payload alongside `src/interpolation/`. Platform-specific code would break one context or the other.

## Acceptance Criteria

### Type Contract ACs

- [ ] **AC-01:** `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `ResolvedCameraParams`, `OversizeRequirements`, `CameraPathEvaluator` are all exported from `src/camera/index.ts`.
- [ ] **AC-02:** `CameraFrameState.position` and `CameraFrameState.lookAt` use the `Vec3` type from `src/spatial/types.ts`.
- [ ] **AC-03:** `CameraFrameState.fov` is `number` (degrees), not optional.
- [ ] **AC-04:** `CameraPathPreset.evaluate` accepts `(t: number, params?: CameraParams)` and returns `CameraFrameState`.
- [ ] **AC-05:** `CameraPathPreset.compatibleGeometries` is `readonly string[]`.
- [ ] **AC-06:** `CameraPathPreset.oversizeRequirements` includes `maxDisplacementX`, `maxDisplacementY`, `maxDisplacementZ`, `fovRange`, and `recommendedOversizeFactor`.
- [ ] **AC-07:** `CameraParams.speed`, `CameraParams.easing`, and `CameraParams.offset` are all optional.
- [ ] **AC-08:** `OversizeRequirements.fovRange` is `readonly [number, number]`.

### toCameraState ACs

- [ ] **AC-09:** `toCameraState({ position: [0,0,5], lookAt: [0,0,0], fov: 50 }, 16/9)` returns a `CameraState` with `position: [0,0,5]`, `lookAt: [0,0,0]`, `fov: 50`, `aspectRatio: 16/9`, `near: 0.1`, `far: 100`.
- [ ] **AC-10:** `toCameraState(frame, 16/9, 0.5, 200)` returns `near: 0.5` and `far: 200` (overriding defaults).

### resolveCameraParams ACs

- [ ] **AC-11:** `resolveCameraParams(undefined, 'ease_in_out')` returns `{ speed: 1.0, easing: <ease_in_out function> }`.
- [ ] **AC-12:** `resolveCameraParams({ speed: 2.0, easing: 'linear' }, 'ease_in_out')` returns `{ speed: 2.0, easing: <linear function> }`.
- [ ] **AC-13:** `resolveCameraParams({ speed: -1 }, 'linear')` throws an `Error`.
- [ ] **AC-14:** `resolveCameraParams({ speed: 0 }, 'linear')` throws an `Error`.
- [ ] **AC-15:** `resolveCameraParams({ easing: 'invalid' }, 'linear')` throws an `Error` whose message includes `'invalid'` and lists valid easing names.

### Registry ACs

- [ ] **AC-16:** `getCameraPath(registry, 'nonexistent')` throws an `Error` whose message includes `'nonexistent'` and lists all available preset names.
- [ ] **AC-17:** `isCameraPathName(registry, name)` returns `true` for registered names, `false` for unregistered.
- [ ] **AC-18:** `listCameraPathNames(registry)` returns names in alphabetical order.
- [ ] **AC-19:** `getCameraPathsForGeometry(registry, 'tunnel')` returns only presets whose `compatibleGeometries` includes `'tunnel'`.
- [ ] **AC-20:** `getCameraPathsForGeometry(registry, 'nonexistent_geometry')` returns an empty array (no throw).

### Validation ACs

- [ ] **AC-21:** `validateCameraPathPreset` detects a preset where `evaluate(0).position` disagrees with `defaultStartState.position` by > 1e-6 in any component.
- [ ] **AC-22:** `validateCameraPathPreset` detects a preset where FOV at any of 100 evenly-spaced sample points is <= 0 or >= 180.
- [ ] **AC-23:** `validateCameraPathPreset` detects a preset where `evaluate()` returns NaN or Infinity for position, lookAt, or fov at any of 100 sample points.
- [ ] **AC-24:** `validateCameraPathPreset` detects `recommendedOversizeFactor < 1.0`.
- [ ] **AC-25:** `validateCameraPathPreset` detects an empty `compatibleGeometries` array.
- [ ] **AC-26:** `validateCameraPathPreset` detects a `name` that is empty or not lowercase snake_case (regex: `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`).
- [ ] **AC-27:** `validateCameraPathPreset` detects a `defaultEasing` that is not a valid `EasingName`.
- [ ] **AC-28:** `validateCameraPathPreset` returns an empty array for a well-formed preset.
- [ ] **AC-29:** `validateCameraPathPreset` detects negative displacement values in `oversizeRequirements`.
- [ ] **AC-30:** `validateCameraPathPreset` detects sampled FOV values outside the declared `oversizeRequirements.fovRange` (tolerance 1e-6).
- [ ] **AC-31:** `validateCameraParams` detects `speed <= 0`, invalid `easing` names, and non-finite `offset` values.
- [ ] **AC-32:** `validateCameraParams` returns an empty array for `{}` (all-defaults).
- [ ] **AC-33:** `validateCameraParams` returns an empty array for `undefined` input.

### Determinism ACs

- [ ] **AC-34:** For any valid `CameraPathPreset`, calling `evaluate(t)` with the same `t` and same `params` 1000 times produces identical `CameraFrameState` values every time (C-05).

### Isomorphism ACs

- [ ] **AC-35:** The module has zero runtime imports outside `src/camera/`, `src/spatial/`, and `src/interpolation/`.
- [ ] **AC-36:** The module uses no Node.js-specific APIs and no browser-specific APIs.

## Edge Cases and Error Handling

### CameraPathEvaluator

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns values matching `defaultStartState` (within 1e-6 per component) |
| `t = 1` | Returns values matching `defaultEndState` (within 1e-6 per component) |
| `t = 0.5` | Returns a valid intermediate state (no NaN, no Infinity, FOV in (0,180)) |
| `t < 0` or `t > 1` | **Undefined behavior.** Callers must clamp before calling. Presets may clamp internally as a safety measure but are not required to. |
| `params` is `undefined` | Uses all defaults (speed=1.0, preset's default easing). Offset not applicable (applied externally). |
| `params.speed = 0` | Invalid. `resolveCameraParams` throws. |
| `params.speed = 0.5` | Camera's spatial amplitude/displacement is halved. Temporal easing unchanged. |
| `params.speed = 2.0` | Camera's spatial amplitude/displacement is doubled. **Warning:** may cause edge reveals. OBJ-040 must use `displacement * speed`. |
| `params.easing = 'ease_out_cubic'` | Overrides the preset's default easing for the primary interpolation. |

### Offset (applied by renderer, post-evaluate)

| Scenario | Expected Behavior |
|----------|-------------------|
| `offset = [0, 0, 0]` | No change to evaluate() output. |
| `offset = [1, 0, 0]` | Renderer adds [1,0,0] to position. lookAt unchanged -- slight viewing angle shift. |
| `offset = [NaN, 0, 0]` | Caught by `validateCameraParams`. Renderer should not receive invalid offset. |
| Large offset (e.g., [10, 0, 0]) | Valid but likely causes edge reveals. OBJ-040 accounts for this. |

### Registry

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty registry | `getCameraPath` throws. `listCameraPathNames` returns `[]`. `getCameraPathsForGeometry` returns `[]`. |
| Name collision | `Record<string, ...>` -- last assignment wins. Assembly module must ensure uniqueness. |

### OversizeRequirements

| Scenario | Expected Behavior |
|----------|-------------------|
| Static camera (no motion) | All displacements = `0`. `recommendedOversizeFactor` = `1.0`. `fovRange` = `[fov, fov]`. |
| FOV animation | `fovRange[0] < fovRange[1]`. Wider FOV moment determines larger visible area. |
| `recommendedOversizeFactor < 1.0` | Caught by `validateCameraPathPreset`. |
| Negative displacement | Caught by `validateCameraPathPreset`. Displacements are absolute magnitudes, always >= 0. |

### resolveCameraParams

| Scenario | Expected Behavior |
|----------|-------------------|
| `undefined` | Returns `{ speed: 1.0, easing: <defaultEasing function> }` |
| `{}` | Same as undefined -- all defaults. |
| `{ speed: -1 }` | Throws: "speed must be greater than 0, got -1" |
| `{ speed: 0 }` | Throws: "speed must be greater than 0, got 0" |
| `{ easing: 'invalid' }` | Throws: includes `'invalid'` and lists valid easing names |
| `{ speed: 1.5, easing: 'ease_out' }` | Returns `{ speed: 1.5, easing: <ease_out function> }` |

### toCameraState

| Scenario | Expected Behavior |
|----------|-------------------|
| All defaults | `near: 0.1`, `far: 100` (from OBJ-003 `DEFAULT_CAMERA`) |
| Custom near/far | Uses provided values |
| `aspectRatio <= 0` | Undefined behavior -- composition validation catches this upstream |

## Test Strategy

### Unit Tests

**Registry functions:**
- Build a mock registry with 3 presets (one compatible with `'tunnel'`, one with `'stage'`, one with both).
- `getCameraPath` returns correct preset by name.
- `getCameraPath` throws with informative message for unknown name.
- `isCameraPathName` true/false for known/unknown.
- `listCameraPathNames` returns sorted array.
- `getCameraPathsForGeometry('tunnel')` returns only tunnel-compatible presets.
- `getCameraPathsForGeometry('unknown')` returns empty array.
- Empty registry edge cases.

**resolveCameraParams:**
- `undefined` -> defaults.
- `{}` -> defaults.
- Valid speed + easing -> resolved correctly.
- Speed <= 0 -> throws.
- Invalid easing -> throws with valid names listed.
- Verify returned easing function is callable and matches expected behavior.

**toCameraState:**
- Default near/far applied.
- Custom near/far used.
- All CameraFrameState fields pass through unchanged.

**Validation (`validateCameraPathPreset`):**
- Create a valid mock preset (with evaluate function, matching start/end states, valid oversize requirements) -> returns empty array.
- Mutate one field at a time: bad name, empty compatibleGeometries, FOV out of range at sampled point, NaN in evaluate, start/end mismatch, oversize factor < 1.0, negative displacements, invalid easing, FOV outside declared fovRange -> each produces the expected error.

**Validation (`validateCameraParams`):**
- `undefined` -> valid.
- `{}` -> valid.
- Various invalid params -> correct errors.
- Valid params with all fields -> valid.
- Non-finite offset -> error.

### Contract Conformance Test Pattern

Each downstream preset (OBJ-026 through OBJ-034) should run a standard conformance suite. This pattern should be exported as a reusable test utility from `src/camera/`:

1. **Boundary start:** `evaluate(0)` matches `defaultStartState` within 1e-6 per component.
2. **Boundary end:** `evaluate(1)` matches `defaultEndState` within 1e-6 per component.
3. **Continuity:** Sample 100 points in [0, 1]; no NaN/Infinity in any field.
4. **FOV range:** All sampled FOV values fall within `oversizeRequirements.fovRange` (tolerance 1e-6).
5. **Determinism:** 100 calls with same `t` produce identical output.
6. **Full validation:** `validateCameraPathPreset(preset)` returns empty array.
7. **Speed scaling:** The maximum Euclidean distance between `evaluate(t, { speed: 0.5 }).position` and `defaultStartState.position` over 100 samples is strictly less than the maximum distance with default params. (Exception: static presets where both maximums are zero.)
8. **Easing override:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in at least one position component. (Exception: static presets.)

### Relevant Testable Claims

- **TC-04** (partial): The type contract ensures LLM authors select preset names, not XYZ coordinates.
- **TC-05** (prerequisite): Tunnel camera path (OBJ-029) will conform to this contract.
- **TC-08** (partial): `compatibleGeometries` metadata enables coverage analysis.
- **TC-09** (prerequisite): Easing override in `CameraParams` enables A/B comparison.

## Integration Points

### Depends on

| Dependency | What is imported |
|---|---|
| **OBJ-002** (`src/interpolation/`) | `EasingName`, `EasingFn` types for `CameraParams.easing`, `CameraPathPreset.defaultEasing`, `ResolvedCameraParams.easing`. `getEasing()` and `isEasingName()` used by `resolveCameraParams` and `validateCameraParams`. |
| **OBJ-003** (`src/spatial/`) | `Vec3` type for positions, lookAt, offset. `CameraState` type as the output of `toCameraState()`. `DEFAULT_CAMERA` constants for `toCameraState()` defaults (near=0.1, far=100). |

### Consumed by

| Downstream | How it uses OBJ-006 |
|---|---|
| **OBJ-026** (`static`) | Implements `CameraPathPreset`. Zero displacement. |
| **OBJ-027** (`slow_push_forward`, `slow_pull_back`) | Implements `CameraPathPreset`. Z-axis interpolation. |
| **OBJ-028** (`lateral_track_left`, `lateral_track_right`) | Implements `CameraPathPreset`. X-axis interpolation. |
| **OBJ-029** (`tunnel_push_forward`) | Implements `CameraPathPreset`. Tunnel-specific Z push. |
| **OBJ-030** (`flyover_glide`) | Implements `CameraPathPreset`. Elevated Y + forward Z. |
| **OBJ-031** (`gentle_float`) | Implements `CameraPathPreset`. Multi-axis sinusoidal. |
| **OBJ-032** (`dramatic_push`) | Implements `CameraPathPreset`. Aggressive ease-out Z push. |
| **OBJ-033** (`crane_up`) | Implements `CameraPathPreset`. Y-axis rise. |
| **OBJ-034** (`dolly_zoom`) | Implements `CameraPathPreset`. Z + FOV animation. |
| **OBJ-040** (Edge-reveal validation) | Reads `OversizeRequirements`, accounts for `speed` and `offset`. Uses `evaluate()` for trajectory sampling. |
| **OBJ-041** (Geometry-camera compatibility) | Reads `compatibleGeometries`. Cross-references against geometry registry. |
| **OBJ-045**, **OBJ-071**, **OBJ-079** | Use registry and types. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t, params)`, applies offset, calls `toCameraState()`, sets Three.js camera. |
| **Scene sequencer** (OBJ-010) | Resolves preset names from manifest, passes `CameraParams`. |

### File Placement

```
depthkit/
  src/
    camera/
      index.ts          # Barrel export
      types.ts          # CameraFrameState, CameraParams, ResolvedCameraParams,
                        # OversizeRequirements, CameraPathEvaluator, CameraPathPreset,
                        # toCameraState(), resolveCameraParams()
      registry.ts       # CameraPathRegistry type, getCameraPath, isCameraPathName,
                        # listCameraPathNames, getCameraPathsForGeometry
      validate.ts       # validateCameraPathPreset, validateCameraParams
```

**NOTE:** The seed's Section 4.5 places camera code under `src/scenes/cameras/`. This spec proposes `src/camera/` as a top-level module instead, because camera types are consumed by the scene sequencer, the manifest validator, the edge-reveal validator, and the page renderer — they are not scoped to `scenes/`. If OBJ-005 places scene geometry types at `src/geometry/`, the parallel structure is `src/camera/`. If the integrator prefers `src/scenes/cameras/`, the type contract is unaffected — only import paths change.

## Open Questions

1. **Should `CameraParams` support a `fovOverride` for static-FOV paths?** A manifest author might want `slow_push_forward` at 35 degrees instead of 50 degrees. Currently only FOV-animating presets control FOV. A simple `fovOverride?: number` in `CameraParams` would let any path use a custom static FOV. **Recommendation:** Defer to OBJ-027 implementation round. Backward-compatible addition.

2. **Should `evaluate()` receive scene duration for duration-dependent paths?** `gentle_float` (OBJ-031) might want to vary oscillation frequency based on scene length — a 5-second scene shouldn't have the same number of oscillations as a 30-second scene. **Recommendation:** Presets that need duration can accept it via `CameraParams` extension (e.g., `{ duration?: number }`). Since unrecognized params are ignored, this is backward-compatible. Defer to OBJ-031 implementation.

3. **Should there be a `CameraPathPresetFactory` for parameterized preset families?** E.g., `createPushPreset({ axis: 'z', distance: 25 })`. **Recommendation:** Defer. Preset implementations can use internal factories, but the external registry contains concrete `CameraPathPreset` instances. The type contract doesn't need to expose factories.
