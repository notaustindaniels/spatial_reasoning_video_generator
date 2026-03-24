# Specification: OBJ-002 — Interpolation, Easing, and Spring Utilities

## Summary

OBJ-002 defines the math primitives that underpin all animation in depthkit: an `interpolate()` function for mapping frame numbers to output values, a `spring()` function for organic/physics-based motion, and six named easing functions. These utilities are isomorphic — they must run identically in both the Node.js orchestrator (scene sequencer transition timing) and the headless Chromium browser (Three.js camera interpolation). This is a Tier 0 foundation with no dependencies; every camera path preset, scene transition, and FOV animation consumes these primitives.

## Interface Contract

### Module: `src/interpolation/easings.ts`

```typescript
/**
 * An easing function maps normalized time t in [0,1] to eased time t' in [0,1].
 * Behavior outside [0,1] is undefined (see design notes).
 */
export type EasingFn = (t: number) => number;

/** Named easing registry key. These names appear in manifests. */
export type EasingName =
  | 'linear'
  | 'ease_in'
  | 'ease_out'
  | 'ease_in_out'
  | 'ease_out_cubic'
  | 'ease_in_out_cubic';

/**
 * Registry mapping easing names to functions.
 * Keyed by EasingName. Used for manifest-driven lookups.
 */
export const easings: Record<EasingName, EasingFn>;

/**
 * Retrieves an easing function by name.
 * @throws {Error} if name is not a valid EasingName. Error message must include
 *   the invalid name and the list of valid names.
 */
export function getEasing(name: string): EasingFn;

/**
 * Type guard: returns true if input is a valid EasingName.
 */
export function isEasingName(name: string): name is EasingName;
```

### Easing Function Definitions (mathematical contracts)

| Name | Formula | Notes |
|------|---------|-------|
| `linear` | `t' = t` | Identity |
| `ease_in` | `t' = t^2` | Quadratic ease-in |
| `ease_out` | `t' = 1 - (1-t)^2` | Quadratic ease-out |
| `ease_in_out` | `t < 0.5 ? 2t^2 : 1 - (-2t+2)^2/2` | Quadratic ease-in-out |
| `ease_out_cubic` | `t' = 1 - (1-t)^3` | Cubic ease-out |
| `ease_in_out_cubic` | `t < 0.5 ? 4t^3 : 1 - (-2t+2)^3/2` | Cubic ease-in-out |

**Invariants (all six):**
- `f(0) === 0` exactly (boundary special-case, not computed from formula)
- `f(1) === 1` exactly (boundary special-case, not computed from formula)
- Monotonically non-decreasing on `[0, 1]`

**Behavior outside `[0, 1]`:** Undefined. Easing functions are never called with values outside `[0, 1]` by `interpolate()` (see computation contract below). Direct callers who pass out-of-range values get formula results — no throw, no clamp, but no guarantees about monotonicity or range.

### Module: `src/interpolation/interpolate.ts`

```typescript
import { EasingFn, EasingName } from './easings';

export interface InterpolateOptions {
  /**
   * Easing function or name. Defaults to 'linear'.
   * Accepts either an EasingFn or an EasingName string.
   */
  easing?: EasingFn | EasingName;

  /**
   * Clamp behavior for input values outside inputRange.
   * 'clamp' (default): clamp t to [0, 1] before easing.
   * 'extend': allow linear extrapolation beyond outputRange (easing NOT applied outside [0,1]).
   */
  extrapolate?: 'clamp' | 'extend';
}

/**
 * Maps a value from an input range to an output range, applying an easing function.
 *
 * @param value - The current value (e.g., frame number). Must not be NaN.
 * @param inputRange - [start, end]. Both must be finite. start < end.
 * @param outputRange - [start, end]. Both must be finite. start may equal or exceed end.
 * @param options - Easing and extrapolation behavior.
 * @returns The interpolated output value.
 * @throws {Error} if value is NaN.
 * @throws {Error} if any element of inputRange or outputRange is NaN or +/-Infinity.
 * @throws {Error} if inputRange[0] >= inputRange[1].
 * @throws {Error} if inputRange or outputRange does not have exactly 2 elements.
 * @throws {Error} if easing is a string that is not a valid EasingName.
 */
export function interpolate(
  value: number,
  inputRange: [number, number],
  outputRange: [number, number],
  options?: InterpolateOptions
): number;
```

**Computation contract:**

1. **Validate inputs.** Throw on NaN `value`, non-finite range elements, or `inputRange[0] >= inputRange[1]`.
2. Compute raw `t = (value - inputRange[0]) / (inputRange[1] - inputRange[0])`.
3. **Branch on extrapolation mode:**
   - **`'clamp'` (default):** Clamp `t` to `[0, 1]`. Apply easing: `t' = easingFn(t)`. Map to output: `result = outputRange[0] + t' * (outputRange[1] - outputRange[0])`.
   - **`'extend'`:** If `t` is within `[0, 1]`, apply easing normally as above. If `t < 0` or `t > 1`, use **linear extrapolation** from the nearest boundary — easing is NOT applied outside `[0, 1]`:
     - If `t < 0`: `result = outputRange[0] + t * (outputRange[1] - outputRange[0])` (linear from the start)
     - If `t > 1`: `result = outputRange[1] + (t - 1) * (outputRange[1] - outputRange[0])` (linear from the eased endpoint)

**Rationale for linear extrapolation in extend mode:** Applying easing functions outside their defined domain `[0, 1]` produces mathematically surprising results (e.g., `ease_in(-0.5) = 0.25`, moving in the wrong direction). Linear extrapolation is the standard approach used by Remotion's `interpolate()` and React Native Reanimated. It guarantees continuous, predictable behavior at the boundaries.

### Module: `src/interpolation/spring.ts`

```typescript
export interface SpringConfig {
  /** Damping coefficient. Default: 200. Must be > 0. */
  damping: number;
  /** Mass. Default: 0.5. Must be > 0. */
  mass: number;
  /** Stiffness. Default: 10. Must be > 0. */
  stiffness: number;
}

export const DEFAULT_SPRING_CONFIG: Readonly<SpringConfig>;
// Value: { damping: 200, mass: 0.5, stiffness: 10 }

/**
 * Computes the response of a damped spring system at a given frame.
 * Returns a value representing progress from rest (0) to target (1).
 *
 * The spring always starts at 0 and settles toward 1.
 * For critically/over-damped springs (zeta >= 1), the response is monotonic.
 * For under-damped springs (zeta < 1), the response may overshoot 1 before settling.
 * Output is NOT clamped — callers are responsible for handling overshoot if needed.
 *
 * @param frame - Current frame number (0-based). Must be >= 0.
 * @param fps - Frames per second. Must be > 0.
 * @param config - Spring parameters. All values must be > 0. Merged with DEFAULT_SPRING_CONFIG.
 * @returns Spring response value (unclamped).
 * @throws {Error} if frame < 0, fps <= 0, or any config value <= 0.
 * @throws {Error} if intermediate physics computation produces NaN or +/-Infinity
 *   (degenerate config). Message describes which config values caused the issue.
 */
export function spring(
  frame: number,
  fps: number,
  config?: Partial<SpringConfig>
): number;
```

**Physics contract (from seed Section 8.5):**
```
t = frame / fps
omega = sqrt(stiffness / mass)
zeta = damping / (2 * sqrt(stiffness * mass))

If zeta >= 1 (critically/over-damped):
  response = 1 - e^(-omega*t) * (1 + omega*t)

If zeta < 1 (under-damped):
  omega_d = omega * sqrt(1 - zeta^2)
  response = 1 - e^(-zeta*omega*t) * cos(omega_d * t)
```

**Non-finite guard:** After computing the response, if the result is NaN or +/-Infinity, throw an `Error` describing the degenerate configuration. Do NOT clamp to an arbitrary range.

### Module: `src/interpolation/index.ts` (barrel export)

```typescript
export { interpolate, InterpolateOptions } from './interpolate';
export { spring, SpringConfig, DEFAULT_SPRING_CONFIG } from './spring';
export { easings, getEasing, isEasingName, EasingFn, EasingName } from './easings';
```

## Design Decisions

### D1: Isomorphic module shared via build-time bundling

**Decision:** The interpolation module lives once in `src/interpolation/`. It is consumed directly by Node.js code (scene sequencer, orchestrator) via normal TypeScript imports. For the browser context (`src/page/`), the build step bundles this module into the page's JavaScript payload. The module uses only pure math — no Node.js APIs, no DOM APIs, no `require`/`import` of anything outside itself.

**Rationale:** The seed (OBJ-002 metadata) explicitly asks us to specify the sharing mechanism. The three options were:
1. **Isomorphic module** (chosen) — single source of truth, no drift risk, works because these are pure functions with zero platform dependencies.
2. **Duplication** — copy-paste into `src/page/`. Rejected: violates DRY, creates drift risk across contexts.
3. **Build-time inclusion** — the module is authored once and the build system includes it in the page bundle. This is effectively the same as option 1.

Options 1 and 3 converge to the same thing. The module must be written as pure ES module code (no CommonJS-only patterns) so it can be bundled for the browser.

**Constraint alignment:** C-01 (zero-license) — pure math, no dependencies. C-05 (deterministic) — pure functions, no randomness, no state.

### D2: Two-element inputRange/outputRange (not multi-segment)

**Decision:** `interpolate()` accepts exactly two-element tuples for input and output ranges. Multi-segment interpolation (e.g., `[0, 50, 100] -> [0, 10, 0]`) is explicitly deferred.

**Rationale:** Seed Section 8.5 shows only two-point interpolation. OQ-06 asks whether camera paths should support composition/chaining but defers it. Multi-segment interpolation adds complexity (which segment is active? per-segment easing?) that downstream objectives can compose by chaining multiple `interpolate()` calls. Keeping the primitive simple makes it easier to reason about and test.

### D3: Clamp by default, extend as opt-in with linear extrapolation beyond boundaries

**Decision:** When `value` falls outside `inputRange`, the default behavior is to clamp `t` to `[0, 1]`, meaning the output saturates at the range endpoints. An `extrapolate: 'extend'` option allows linear extrapolation beyond the range. In extend mode, easing applies only within `[0, 1]`; extrapolation beyond boundaries is always linear.

**Rationale:** Clamping is safer for blind authoring (C-06). A camera that overshoots its time range should hold its final position, not fly off into space. The `extend` option exists for spring physics, where the spring response naturally starts at 0 and the `interpolate()` call may need to map spring values > 1.0 to output ranges. Linear extrapolation beyond boundaries prevents surprising behavior from easing functions evaluated outside their domain.

### D4: Easing as function or string name

**Decision:** The `easing` option in `interpolate()` accepts either an `EasingFn` or an `EasingName` string. If a string, it is resolved via `getEasing()`.

**Rationale:** Manifest-driven code paths pass easing names as strings from JSON. Internal engine code may want to pass function references directly. Supporting both eliminates a boilerplate `getEasing()` call at every callsite.

### D5: Spring uses physical units (frame + fps), not normalized time

**Decision:** `spring()` accepts `frame` and `fps` as separate arguments rather than a pre-computed `t`.

**Rationale:** This matches the seed's Section 8.5 signature exactly. The calling code (camera path presets) naturally has `frame` and `fps` available. Computing `t = frame / fps` internally keeps the API consistent with how the virtualized clock works (C-03): the orchestrator passes frame numbers, and all time is derived from frames.

### D6: No mutable state, no side effects

**Decision:** All exports are pure functions or immutable constants. No closures over mutable state, no caching, no singletons.

**Rationale:** Determinism (C-05). The same inputs must always produce the same output. These functions may be called millions of times per render — purity ensures thread safety if parallel rendering (OQ-10) is ever added.

### D7: Fail-fast on invalid numeric inputs

**Decision:** `interpolate()` throws on NaN `value` and on non-finite (NaN or +/-Infinity) range elements. `spring()` throws on non-finite intermediate physics results.

**Rationale:** Silent NaN propagation through the pipeline produces corrupt frames that are invisible to the blind-authoring LLM (violates C-06). A NaN camera position in Three.js renders garbage without error. Failing fast at the math primitive level is the last line of defense. +/-Infinity in `value` with clamp mode is acceptable (it clamps to a boundary) — this handles legitimate edge cases like division-by-zero upstream that accidentally produces Infinity but where clamping is the correct behavior. +/-Infinity in range elements is always a bug.

## Acceptance Criteria

**Floating-point tolerance rules:**
- For linear operations (no easing, or `linear` easing), exact equality (`===`) is expected.
- For eased and spring operations, tolerance is `+/-1e-10` unless the AC specifies otherwise.
- ACs that say "approximately" state their tolerance explicitly.

### Easing ACs

- [ ] **AC-01:** All six named easing functions are exported and satisfy `f(0) === 0` and `f(1) === 1` exactly.
- [ ] **AC-02:** All six easing functions are monotonically non-decreasing on `[0, 1]`, verified by sampling at 1000 evenly-spaced points and checking `f(t_n+1) >= f(t_n)`.
- [ ] **AC-16:** `getEasing('nonexistent')` throws an `Error` whose message includes `'nonexistent'` and lists valid easing names.
- [ ] **AC-17:** `isEasingName('ease_in')` returns `true`; `isEasingName('bounce')` returns `false`.

### Interpolate ACs

- [ ] **AC-03:** `interpolate(50, [0, 100], [0, 10])` returns `5.0` exactly.
- [ ] **AC-04:** `interpolate(-10, [0, 100], [0, 10])` returns `0.0` exactly (clamp default).
- [ ] **AC-05:** `interpolate(150, [0, 100], [0, 10])` returns `10.0` exactly (clamp default).
- [ ] **AC-06:** `interpolate(150, [0, 100], [0, 10], { extrapolate: 'extend' })` returns `15.0` exactly (linear extrapolation beyond endpoint).
- [ ] **AC-07:** `interpolate(50, [0, 100], [10, 0])` returns `5.0` exactly (reverse output range).
- [ ] **AC-08:** `interpolate(50, [0, 100], [0, 10], { easing: 'ease_in' })` returns `2.5` within `+/-1e-10` (quadratic: `0.5^2 = 0.25`, mapped to `0.25 * 10 = 2.5`).
- [ ] **AC-09:** `interpolate(50, [0, 100], [0, 10], { easing: 'invalid_name' })` throws an `Error` whose message includes `'invalid_name'` and lists valid names.
- [ ] **AC-10:** `interpolate(50, [100, 100], [0, 10])` throws (inputRange[0] not less than inputRange[1]).
- [ ] **AC-21:** `interpolate(NaN, [0, 100], [0, 10])` throws an `Error`.
- [ ] **AC-22:** `interpolate(50, [0, 100], [0, 10], { easing: (t) => t * t })` returns `2.5` within `+/-1e-10` (function reference path).
- [ ] **AC-23:** `interpolate(5, [0, Infinity], [0, 10])` throws an `Error` (non-finite range element).
- [ ] **AC-24:** `interpolate(120, [0, 100], [0, 10], { easing: 'ease_in', extrapolate: 'extend' })` returns `12.0` exactly. Derivation: `t = 1.2`, which is > 1, so linear extrapolation from the eased endpoint: `outputRange[1] + (t - 1) * (outputRange[1] - outputRange[0]) = 10 + 0.2 * 10 = 12.0`.
- [ ] **AC-26:** `interpolate(-20, [0, 100], [0, 10], { easing: 'ease_in', extrapolate: 'extend' })` returns `-2.0` exactly. Derivation: `t = -0.2`, which is < 0, so linear extrapolation from start: `outputRange[0] + t * (outputRange[1] - outputRange[0]) = 0 + (-0.2) * 10 = -2.0`.

### Spring ACs

- [ ] **AC-11:** `spring(0, 30)` returns `0.0` exactly.
- [ ] **AC-12:** `spring(300, 30)` with default config returns approximately `1.0` (within `+/-0.001`).
- [ ] **AC-13:** `spring()` with default config (damping: 200, mass: 0.5, stiffness: 10) is over-damped (zeta > 1), verified by checking that the response is monotonically non-decreasing over 300 frames.
- [ ] **AC-14:** `spring()` with under-damped config `{ damping: 5, mass: 0.5, stiffness: 100 }` produces a response exceeding 1.0 at some frame in `[0, 300]`.
- [ ] **AC-15:** `spring(-1, 30)` throws. `spring(0, 0)` throws. `spring(0, 30, { damping: 0 })` throws. `spring(0, 30, { mass: -1 })` throws.

### General ACs

- [ ] **AC-18:** The module has zero runtime dependencies (no imports outside `src/interpolation/`).
- [ ] **AC-19:** The module uses no Node.js-specific APIs (`process`, `fs`, `Buffer`, etc.) and no browser-specific APIs (`window`, `document`, `requestAnimationFrame`, etc.).
- [ ] **AC-20:** Calling `interpolate()` and `spring()` 100,000 times with identical inputs produces identical results across runs (determinism, C-05).

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `interpolate(NaN, ...)` | **Throws** `Error`: "interpolate: value must not be NaN" |
| `interpolate(5, [0, NaN], [0, 10])` | **Throws** `Error`: "interpolate: inputRange elements must be finite numbers" |
| `interpolate(5, [0, 100], [NaN, 10])` | **Throws** `Error`: "interpolate: outputRange elements must be finite numbers" |
| `interpolate(5, [0, Infinity], [0, 10])` | **Throws** `Error`: "interpolate: inputRange elements must be finite numbers" |
| `interpolate(Infinity, [0, 100], [0, 10])` | With clamp: returns `10.0`. With extend: returns `Infinity`. (+/-Infinity `value` is allowed.) |
| `inputRange[0] === inputRange[1]` | **Throws** `Error`: "interpolate: inputRange start must be less than end" |
| `inputRange[0] > inputRange[1]` | **Throws** same as above |
| `outputRange[0] === outputRange[1]` | Returns `outputRange[0]` for any valid input. No throw. |
| Easing boundary `t = 0` or `t = 1` | Returns exactly `0` or `1` via explicit boundary check in the easing function. |
| Extend mode, `t < 0` | Linear extrapolation (easing NOT applied). |
| Extend mode, `t > 1` | Linear extrapolation from eased endpoint (easing NOT applied). |
| `spring(0, fps)` any valid fps/config | Returns `0.0` exactly. |
| `spring()` with extreme config producing non-finite intermediate values | **Throws** `Error` describing degenerate config. |
| `spring()` under-damped, response > 1.0 | Valid. Output is NOT clamped. Caller's responsibility. |
| `spring()` very high damping | Converges slowly. Valid. No throw. |
| Custom `EasingFn` that returns values outside `[0,1]` | Output extends beyond `outputRange`. Valid — no output-side clamping. |

## Test Strategy

### Unit Tests (per function)

**Easing functions (per function x 6):**
- Boundary: `f(0) === 0`, `f(1) === 1`
- Known midpoint value (e.g., `ease_in(0.5) === 0.25`, `ease_out(0.5) === 0.75`, `ease_in_out(0.5) === 0.5`)
- Monotonicity: 1000-point sweep
- Registry lookup: `getEasing(name)` returns the same function as `easings[name]`

**`interpolate()`:**
- Linear identity, scale, offset, reverse range
- Clamp: below-range, above-range
- Extend: below-range (linear), above-range (linear), verify easing is NOT applied outside `[0,1]`
- Each named easing via string: spot-check one value
- Function reference easing: spot-check
- All error cases: NaN value, non-finite ranges, bad inputRange order, invalid easing string

**`spring()`:**
- Frame 0 = 0
- Convergence at high frame
- Over-damped monotonicity
- Under-damped overshoot detection
- All error cases: negative frame, zero fps, zero/negative config, degenerate config

### Determinism Test
- Every function called 1000x with same inputs, all outputs identical.

### Relevant Testable Claims
- **TC-06** (deterministic output) — interpolation determinism is a prerequisite; verified here.
- **TC-09** (eased paths feel natural) — partially validated by confirming eased outputs diverge meaningfully from linear.

## Integration Points

- **Depends on:** Nothing. Tier 0 foundation.
- **Consumed by:**
  - **OBJ-006** (Camera Path Presets) — `interpolate()` with easings for `position(t)` and `lookAt(t)`.
  - **OBJ-008** (Transition System) — `interpolate()` for opacity during crossfade/dip-to-black.
  - **OBJ-079** (downstream per index.json).
  - **Browser context** (`src/page/scene-renderer.js`) — same functions bundled into page JS for per-frame camera position computation.
  - **Node.js context** (`src/scenes/scene-sequencer.ts`) — transition timing calculations.
- **File placement:**
  ```
  src/interpolation/
  ├── easings.ts          # EasingFn type, all 6 named easings, registry, getEasing(), isEasingName()
  ├── interpolate.ts      # interpolate() function
  ├── spring.ts           # spring() function, SpringConfig, DEFAULT_SPRING_CONFIG
  └── index.ts            # barrel export
  ```
  Note: The seed's Section 4.5 places these under `src/scenes/cameras/interpolate.ts`. This spec proposes `src/interpolation/` as a top-level module instead, because these utilities are consumed by both the camera system AND the scene sequencer (transitions). They are not camera-specific. The downstream implementer of the build system must ensure this module is bundled into `src/page/` for browser use.

## Open Questions

- **OQ-A: Multi-segment `interpolate()`** — Deferred. Multi-segment ranges (e.g., `[0, 50, 100] -> [0, 10, 0]`) can be composed by chaining multiple `interpolate()` calls or by building a higher-level `interpolateSegments()` wrapper in a downstream objective. No changes needed to this spec.
- **OQ-B: `clampedSpring()` convenience** — Deferred. Trivially done with `Math.min(1, spring(...))` at the callsite. Will revisit if downstream objectives consistently need it.
