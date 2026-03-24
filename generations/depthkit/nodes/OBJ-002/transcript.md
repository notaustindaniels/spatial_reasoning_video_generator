# Deliberation Transcript: OBJ-002

---

## Round 1 — spec_author

# Proposed Specification: OBJ-002 — Interpolation, Easing, and Spring Utilities

## Summary

OBJ-002 defines the math primitives that underpin all animation in depthkit: an `interpolate()` function for mapping frame numbers to output values, a `spring()` function for organic/physics-based motion, and six named easing functions. These utilities are isomorphic — they must run identically in both the Node.js orchestrator (scene sequencer transition timing) and the headless Chromium browser (Three.js camera interpolation). This is a Tier 0 foundation with no dependencies; every camera path preset, scene transition, and FOV animation consumes these primitives.

## Interface Contract

### Module: `src/interpolation/easings.ts`

```typescript
/**
 * An easing function maps normalized time t ∈ [0,1] to eased time t' ∈ [0,1].
 * For inputs outside [0,1], behavior is defined per-function (see edge cases).
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
| `ease_in` | `t' = t²` | Quadratic ease-in |
| `ease_out` | `t' = 1 - (1-t)²` | Quadratic ease-out |
| `ease_in_out` | `t < 0.5 ? 2t² : 1 - (-2t+2)²/2` | Quadratic ease-in-out |
| `ease_out_cubic` | `t' = 1 - (1-t)³` | Cubic ease-out |
| `ease_in_out_cubic` | `t < 0.5 ? 4t³ : 1 - (-2t+2)³/2` | Cubic ease-in-out |

All easing functions must satisfy:
- `f(0) === 0` (exactly)
- `f(1) === 1` (exactly)
- Monotonically non-decreasing on `[0, 1]`

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
   * 'extend': allow extrapolation beyond outputRange.
   */
  extrapolate?: 'clamp' | 'extend';
}

/**
 * Maps a value from an input range to an output range, applying an easing function.
 *
 * @param value - The current value (e.g., frame number)
 * @param inputRange - [start, end] — the domain. Must have exactly 2 elements, start < end.
 * @param outputRange - [start, end] — the codomain. May have start > end (reverse interpolation).
 * @param options - Easing and extrapolation behavior.
 * @returns The interpolated output value.
 * @throws {Error} if inputRange has fewer or more than 2 elements.
 * @throws {Error} if inputRange[0] >= inputRange[1].
 * @throws {Error} if outputRange has fewer or more than 2 elements.
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
1. Compute raw `t = (value - inputRange[0]) / (inputRange[1] - inputRange[0])`
2. If `extrapolate === 'clamp'` (default): clamp `t` to `[0, 1]`
3. Apply easing: `t' = easingFn(t)`
4. Map to output: `result = outputRange[0] + t' * (outputRange[1] - outputRange[0])`

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

/**
 * Computes the response of a damped spring system at a given frame.
 * Returns a value in [0, ~1] representing progress from rest to target.
 * 
 * The spring always starts at 0 and settles toward 1.
 * For critically/over-damped springs (zeta >= 1), the response is monotonic.
 * For under-damped springs (zeta < 1), the response may overshoot 1 before settling.
 *
 * @param frame - Current frame number (0-based). Must be >= 0.
 * @param fps - Frames per second. Must be > 0.
 * @param config - Spring parameters. All values must be > 0.
 * @returns Spring response value. May exceed 1.0 transiently for under-damped springs.
 * @throws {Error} if frame < 0, fps <= 0, or any config value <= 0.
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
ω = √(stiffness / mass)
ζ = damping / (2 × √(stiffness × mass))

If ζ ≥ 1 (critically/over-damped):
  response = 1 - e^(-ωt) × (1 + ωt)

If ζ < 1 (under-damped):
  ωd = ω × √(1 - ζ²)
  response = 1 - e^(-ζωt) × cos(ωd × t)
```

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
3. **Build-time inclusion** — the module is authored once and the build system includes it in the page bundle. This is effectively the same as option 1 — the module is isomorphic, and the build system handles getting it into the browser.

Options 1 and 3 converge to the same thing. The module must be written as pure ES module code (no CommonJS-only patterns) so it can be bundled for the browser.

**Constraint alignment:** C-01 (zero-license) — pure math, no dependencies. C-05 (deterministic) — pure functions, no randomness, no state.

### D2: Two-element inputRange/outputRange (not multi-segment)

**Decision:** `interpolate()` accepts exactly two-element tuples for input and output ranges. Multi-segment interpolation (e.g., `[0, 50, 100] → [0, 10, 0]`) is explicitly deferred.

**Rationale:** Seed Section 8.5 shows only two-point interpolation. OQ-06 asks whether camera paths should support composition/chaining but defers it. Multi-segment interpolation adds complexity (which segment is active? per-segment easing?) that downstream objectives can compose by chaining multiple `interpolate()` calls. Keeping the primitive simple makes it easier to reason about and test.

### D3: Clamp by default, extend as opt-in

**Decision:** When `value` falls outside `inputRange`, the default behavior is to clamp `t` to `[0, 1]`, meaning the output saturates at the range endpoints. An `extrapolate: 'extend'` option allows linear extrapolation beyond the range.

**Rationale:** Clamping is safer for blind authoring (C-06). A camera that overshoots its time range should hold its final position, not fly off into space. The `extend` option exists for spring physics, where the spring response naturally starts at 0 and the `interpolate()` call may need to map spring values > 1.0 to output ranges.

### D4: Easing as function or string name

**Decision:** The `easing` option in `interpolate()` accepts either an `EasingFn` or an `EasingName` string. If a string, it is resolved via `getEasing()`.

**Rationale:** Manifest-driven code paths pass easing names as strings from JSON. Internal engine code may want to pass function references directly. Supporting both eliminates a boilerplate `getEasing()` call at every callsite.

### D5: Spring uses physical units (frame + fps), not normalized time

**Decision:** `spring()` accepts `frame` and `fps` as separate arguments rather than a pre-computed `t`. 

**Rationale:** This matches the seed's Section 8.5 signature exactly. The calling code (camera path presets) naturally has `frame` and `fps` available. Computing `t = frame / fps` internally keeps the API consistent with how the virtualized clock works (C-03): the orchestrator passes frame numbers, and all time is derived from frames.

### D6: No mutable state, no side effects

**Decision:** All exports are pure functions or immutable constants. No closures over mutable state, no caching, no singletons.

**Rationale:** Determinism (C-05). The same inputs must always produce the same output. These functions may be called millions of times per render — purity ensures thread safety if parallel rendering (OQ-10) is ever added.

## Acceptance Criteria

- [ ] **AC-01:** All six named easing functions are exported and satisfy `f(0) === 0` and `f(1) === 1` exactly (no floating-point drift at boundaries — use explicit boundary checks).
- [ ] **AC-02:** All six easing functions are monotonically non-decreasing on `[0, 1]`, verified by sampling at 1000 evenly-spaced points and checking `f(t_n+1) >= f(t_n)`.
- [ ] **AC-03:** `interpolate(50, [0, 100], [0, 10])` returns `5.0` (linear default).
- [ ] **AC-04:** `interpolate(-10, [0, 100], [0, 10])` returns `0.0` (clamp default).
- [ ] **AC-05:** `interpolate(150, [0, 100], [0, 10])` returns `10.0` (clamp default).
- [ ] **AC-06:** `interpolate(150, [0, 100], [0, 10], { extrapolate: 'extend' })` returns `15.0`.
- [ ] **AC-07:** `interpolate(50, [0, 100], [10, 0])` returns `5.0` (reverse output range).
- [ ] **AC-08:** `interpolate()` with `easing: 'ease_in'` produces a value < 5.0 at the midpoint (since quadratic ease-in lags behind linear).
- [ ] **AC-09:** `interpolate()` with an invalid easing name string throws an `Error` whose message includes the invalid name and lists valid names.
- [ ] **AC-10:** `interpolate()` throws if `inputRange[0] >= inputRange[1]`.
- [ ] **AC-11:** `spring(0, 30)` returns `0.0` (spring at rest at frame 0).
- [ ] **AC-12:** `spring(frame, 30)` for large `frame` (e.g., 300) converges to approximately `1.0` (within 0.001) with default config.
- [ ] **AC-13:** `spring()` with default config (damping: 200, mass: 0.5, stiffness: 10) is over-damped (ζ > 1), producing a monotonically increasing response.
- [ ] **AC-14:** `spring()` with an under-damped config (e.g., damping: 5, mass: 0.5, stiffness: 100) produces a response that exceeds 1.0 at some frame (overshoot).
- [ ] **AC-15:** `spring()` throws if `frame < 0`, `fps <= 0`, or any config value `<= 0`.
- [ ] **AC-16:** `getEasing('nonexistent')` throws an `Error` whose message includes `'nonexistent'` and lists valid easing names.
- [ ] **AC-17:** `isEasingName('ease_in')` returns `true`; `isEasingName('bounce')` returns `false`.
- [ ] **AC-18:** The module has zero runtime dependencies (no imports outside `src/interpolation/`).
- [ ] **AC-19:** The module uses no Node.js-specific APIs (no `process`, `fs`, `Buffer`, etc.) and no browser-specific APIs (no `window`, `document`, `requestAnimationFrame`, etc.) — confirming isomorphic compatibility.
- [ ] **AC-20:** Calling `interpolate()` and `spring()` 100,000 times with varying inputs produces identical results on repeated runs (determinism, C-05).

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `interpolate(NaN, ...)` | Returns `NaN` (IEEE 754 propagation). No throw. |
| `interpolate(Infinity, [0, 100], [0, 10])` | With clamp (default): returns `10.0`. With extend: returns `Infinity`. |
| `inputRange[0] === inputRange[1]` | Throws `Error`: "inputRange start must be less than end" |
| `outputRange[0] === outputRange[1]` | Returns `outputRange[0]` for any input (valid degenerate case, no throw). |
| Easing input `t` exactly at 0 or 1 | Must return exactly 0 or 1, not `0.9999999` due to float math. Implementer should special-case boundaries. |
| Easing input `t` slightly outside `[0, 1]` due to float precision | Clamped `interpolate` prevents this. For `extend` mode, the easing function receives the raw `t` — implementer should document that easing behavior outside `[0,1]` is undefined but not throwing. |
| `spring(0, fps)` for any valid fps | Returns `0.0` exactly (e^0 = 1, so `1 - 1*(1+0) = 0` for over-damped, `1 - 1*cos(0) = 0` for under-damped). |
| `spring()` with extremely high damping | Converges very slowly but never throws. Response stays near 0 for many frames before rising. |
| `spring()` with extremely low mass | ω becomes very large, spring oscillates rapidly (under-damped) or converges very fast (over-damped). Valid behavior. |
| All `spring()` config values at minimum (near zero but > 0) | Must not produce `Infinity` or `NaN`. If the physics formula produces `Infinity` (e.g., `sqrt(stiffness/mass)` with extreme values), clamp the response to `[0, 2]` and document the guard. |
| `interpolate` called with easing function that returns values outside `[0,1]` | The output will extend beyond `outputRange`. This is valid — custom easing functions (e.g., overshoot/bounce) may intentionally do this. No clamping on the output side. |

## Test Strategy

### Unit Tests (per function)

**Easing functions:** For each of the 6 easings:
- Boundary test: `f(0) === 0`, `f(1) === 1`
- Midpoint test: verify against known formula value (e.g., `ease_in(0.5) === 0.25`)
- Monotonicity: sample 1000 points, verify non-decreasing
- Symmetry where applicable: `ease_in_out(0.5) === 0.5`

**`interpolate()`:**
- Linear identity: `interpolate(t, [0, 1], [0, 1]) === t` for t ∈ {0, 0.25, 0.5, 0.75, 1}
- Scale and offset: `interpolate(5, [0, 10], [100, 200]) === 150`
- Reverse range: `interpolate(5, [0, 10], [200, 100]) === 150`
- Clamp behavior: out-of-range inputs
- Extend behavior: out-of-range inputs
- Each named easing via string: spot-check one value per easing
- Error cases: bad inputRange, bad easing name

**`spring()`:**
- Frame 0 returns 0
- Convergence: high frame returns ≈1.0
- Over-damped (default config): monotonically increasing over 100 frames
- Under-damped config: overshoot detected
- Error cases: negative frame, zero fps, zero/negative config values

### Determinism Test
- Call every function 1000 times with the same inputs, verify all outputs are identical.

### Relevant Testable Claims
- **TC-06** (deterministic output) — the interpolation utilities are a prerequisite for this; their determinism is tested here.
- **TC-09** (eased camera paths feel more natural) — partially validated here by verifying that eased outputs differ meaningfully from linear.

## Integration Points

- **Depends on:** Nothing. Tier 0 foundation.
- **Consumed by:**
  - **OBJ-006** (Camera Path Presets) — uses `interpolate()` with various easings to compute `position(t)` and `lookAt(t)`.
  - **OBJ-008** (Transition System) — uses `interpolate()` to compute opacity values during crossfade/dip-to-black transitions.
  - **OBJ-079** — (downstream consumer per index.json).
  - **Browser context** (`src/page/scene-renderer.js`) — the same functions are bundled into the page JS for per-frame camera position computation.
  - **Node.js context** (`src/scenes/scene-sequencer.ts`) — for transition timing calculations.
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

- **OQ-A: Should `interpolate()` support multi-segment ranges in the future?** This spec explicitly defers multi-segment to keep the primitive simple. Downstream objectives that need multi-segment (e.g., OQ-06 camera path composition) can compose multiple `interpolate()` calls or build a higher-level `interpolateSegments()` wrapper. No changes needed to this spec for that.
- **OQ-B: Should there be a `clampedSpring()` variant?** Some callers may want the spring response clamped to `[0, 1]` (no overshoot). This could be a convenience wrapper, but it's trivially done with `Math.min(1, spring(...))` at the callsite. Deferred unless downstream objectives request it.

---

I believe this covers the full scope of OBJ-002. I'd like the Challenger to verify:

1. The isomorphic sharing decision (D1) and proposed file placement outside the cameras directory.
2. Whether the six easing formulas are correct and sufficient.
3. Whether the `interpolate()` API surface (two-element ranges only, clamp/extend) is the right level of abstraction.
4. Whether the spring physics formula and API are correct per the seed.
5. Whether the edge case table is thorough enough.

Please review and let me know if anything needs tightening.

---

## Round 2 — spec_challenger

## Challenger Review — Round 2

I've reviewed the proposal carefully. This is a solid first draft — the scope is right, the math is right, and the isomorphic decision is well-reasoned. I have a handful of issues, mostly major, one critical.

---

### Points of Agreement (explicitly approved)

- **D1 (isomorphic module):** Correct decision. Pure math functions with zero platform deps — single source of truth is the only sane option.
- **D2 (two-element ranges):** Correct scoping. Seed Section 8.5 only shows two-point. Multi-segment is composable. Good call deferring.
- **D5 (frame + fps for spring):** Matches seed exactly.
- **D6 (no mutable state):** Correct for C-05 determinism.
- **File placement at `src/interpolation/`:** Better than `src/scenes/cameras/` since transitions also consume these. Agreed.
- **Easing formulas:** I checked all six against standard easing references. They're correct.
- **Spring physics formulas:** Match seed Section 8.5 exactly.

---

### Issues

#### Issue 1 — CRITICAL: `NaN` propagation is the wrong choice for `interpolate()`

**Problem:** The edge case table says `interpolate(NaN, ...)` returns `NaN` via IEEE 754 propagation with "No throw." This silently poisons the entire downstream pipeline. A NaN camera position in Three.js doesn't throw — it renders a black frame or garbage. The orchestrator captures the garbage frame, pipes it to FFmpeg, and the corrupt frame ends up in the final video. Nobody finds out until a human watches it, which violates C-06 (blind authorable — the engine must make it structurally difficult to produce broken video).

This is a manifest validation concern, yes, but `interpolate()` is the last line of defense. If a camera path preset has a bug that passes NaN, the damage is silent and total.

**Proposed fix:** `interpolate()` must throw on NaN input value. Add to the throws list:
- `@throws {Error} if value is NaN`

And add acceptance criterion:
- `AC-21: interpolate(NaN, [0, 100], [0, 10]) throws an Error`

The same applies to NaN in inputRange or outputRange elements. All four numeric inputs must be finite numbers (not NaN, not ±Infinity for ranges). For the `value` parameter, ±Infinity with clamp is acceptable (it clamps). For ranges, Infinity makes no mathematical sense.

**Proposed contract:**
- `inputRange` and `outputRange` elements must be finite (not NaN, not ±Infinity). Throw if not.
- `value` must not be NaN. Throw if NaN. ±Infinity is allowed (clamps or extends per option).

#### Issue 2 — MAJOR: Spring response guard of `[0, 2]` is arbitrary and undocumented

**Problem:** The edge case table says "If the physics formula produces Infinity... clamp the response to `[0, 2]` and document the guard." The number 2 appears from nowhere. Why 2? What happens when a downstream caller chains `spring()` into `interpolate()` with `extrapolate: 'extend'`? An under-damped spring with overshoot might naturally hit 1.15 — that's fine. But clamping to 2 is a magic number that the implementer will guess about.

**Proposed fix:** Don't clamp the spring response to an arbitrary range. Instead:
1. Validate that the physics computation produces a finite number. If `ω`, `ζ`, or the response is NaN/Infinity (due to extreme config values), throw an error describing the degenerate config.
2. Document that under-damped springs may overshoot 1.0. Do NOT clamp the output — callers (camera path presets) are responsible for deciding how to handle overshoot (e.g., `Math.min(1, spring(...))` if they want it clamped).
3. Remove the `[0, 2]` clamp language entirely.

Update the edge case row to: "If config values produce non-finite intermediate results (e.g., `sqrt(stiffness/mass)` overflows), throw `Error` describing the degenerate configuration."

#### Issue 3 — MAJOR: Missing acceptance criterion for `interpolate()` with `EasingFn` (function reference)

**Problem:** D4 says `easing` accepts either a string or a function. AC-08 only tests with a string name. There's no AC verifying that passing an `EasingFn` directly works. An implementer could forget the function path and only implement string lookup.

**Proposed fix:** Add:
- `AC-22: interpolate(50, [0, 100], [0, 10], { easing: (t) => t * t }) returns 2.5` (quadratic ease-in, same as `ease_in`, verifying function path works)

#### Issue 4 — MAJOR: `Infinity` handling in edge cases is inconsistent

**Problem:** The table says `interpolate(Infinity, [0, 100], [0, 10])` with clamp returns `10.0`, and with extend returns `Infinity`. But the spec also says inputRange/outputRange could contain Infinity? There's no explicit prohibition. `interpolate(5, [0, Infinity], [0, 10])` — what happens? `t = 5/Infinity = 0`, so it returns 0. Is that intended? It's mathematically "correct" but almost certainly a bug at the callsite.

**Proposed fix:** Per my note in Issue 1 — range elements must be finite. Add:
- `@throws {Error} if any element of inputRange or outputRange is NaN or ±Infinity`
- `AC-23: interpolate(5, [0, Infinity], [0, 10]) throws an Error`

#### Issue 5 — MINOR: `extrapolate: 'extend'` behavior with easing is under-specified

**Problem:** When `extrapolate: 'extend'` is set and `value` is outside the inputRange, `t` can be negative or > 1. The spec says "the easing function receives the raw `t`." But the easing functions are only mathematically defined on `[0, 1]`. What does `ease_in(-0.5)` return? `(-0.5)² = 0.25` — which is _positive_, meaning the output moves in the wrong direction. This is surprising and could produce broken camera motion.

**Proposed fix:** Document explicitly in the computation contract that when `extrapolate: 'extend'`, the easing function is NOT applied to values outside `[0, 1]`. Instead, linear extrapolation is used beyond the boundaries:
- If `t < 0`: `result = outputRange[0] + t * (outputRange[1] - outputRange[0])` (linear, no easing)
- If `t > 1`: `result = outputRange[0] + (easingFn(1) + (t - 1)) * (outputRange[1] - outputRange[0])` 

Actually, that's getting complicated. Simpler: when `extrapolate: 'extend'`, extrapolation beyond the range is always **linear** regardless of easing. The easing only applies to the `[0, 1]` interior. This is how Remotion's `interpolate()` and React Native Reanimated work — it's the standard approach.

Add acceptance criterion:
- `AC-24: interpolate(120, [0, 100], [0, 10], { easing: 'ease_in', extrapolate: 'extend' }) returns a value derived from linear extrapolation beyond the eased endpoint, not from applying ease_in to t=1.2`

Specify the exact expected value so the implementer doesn't guess.

#### Issue 6 — MINOR: No guidance on floating-point tolerance in acceptance criteria

**Problem:** AC-03 says `interpolate(50, [0, 100], [0, 10])` returns `5.0`. AC-12 says spring converges "within 0.001." But there's no general statement about floating-point tolerance for ACs. Is `5.000000000000001` a pass or fail for AC-03? For linear interpolation it should be exact, but for eased values the formulas involve powers and divisions.

**Proposed fix:** Add a preamble to the AC section:
- For linear operations (no easing, or linear easing), exact equality is expected.
- For eased/spring operations, tolerance is `±1e-10` unless otherwise stated.
- ACs that use "approximately" specify their tolerance explicitly.

#### Issue 7 — MINOR: Missing `spring()` behavior at frame 0 boundary in acceptance criteria

**Problem:** AC-11 checks `spring(0, 30)` returns `0.0`. Good. But the physics formula at t=0: for over-damped, `1 - e^0 * (1 + 0) = 1 - 1 = 0`. For under-damped, `1 - e^0 * cos(0) = 1 - 1 = 0`. Both correct. But there's no AC for an under-damped spring at frame 0 — AC-11 uses the default (over-damped) config.

This is a trivial nitpick since the math works out the same, but for completeness:
- `AC-25: spring(0, 30, { damping: 5, mass: 0.5, stiffness: 100 }) returns 0.0` (under-damped at frame 0)

Actually, I'll mark this as non-blocking. The math guarantees it. Move on.

---

### Summary of Required Changes

| # | Severity | Issue | Required Fix |
|---|----------|-------|-------------|
| 1 | Critical | NaN propagation silently corrupts output | Throw on NaN inputs. Require finite range elements. Add AC-21, AC-23. |
| 2 | Major | Spring `[0, 2]` clamp is arbitrary | Remove clamp. Throw on non-finite intermediate results. |
| 3 | Major | No AC for EasingFn (function) path | Add AC-22 testing function reference. |
| 4 | Major | Infinity in ranges is unaddressed | Require finite range elements. Add throw + AC. |
| 5 | Minor | `extend` mode + easing outside `[0,1]` produces surprising results | Linear extrapolation beyond boundaries regardless of easing. Add AC-24. |
| 6 | Minor | No float tolerance guidance for ACs | Add tolerance preamble. |

Please revise and I'll verify the structural fixes before converging. Issues 1-4 must be resolved; issues 5-6 should be but I could live with them documented as open questions if you disagree.

---

## Round 3 — spec_author

# Revised Specification: OBJ-002 — Interpolation, Easing, and Spring Utilities

All six issues from the Challenger are valid. I'm accepting every one and incorporating them below. Here's the revised spec with changes marked.

## Summary

OBJ-002 defines the math primitives that underpin all animation in depthkit: an `interpolate()` function for mapping frame numbers to output values, a `spring()` function for organic/physics-based motion, and six named easing functions. These utilities are isomorphic — they must run identically in both the Node.js orchestrator (scene sequencer transition timing) and the headless Chromium browser (Three.js camera interpolation). This is a Tier 0 foundation with no dependencies; every camera path preset, scene transition, and FOV animation consumes these primitives.

## Interface Contract

### Module: `src/interpolation/easings.ts`

```typescript
export type EasingFn = (t: number) => number;

export type EasingName =
  | 'linear'
  | 'ease_in'
  | 'ease_out'
  | 'ease_in_out'
  | 'ease_out_cubic'
  | 'ease_in_out_cubic';

export const easings: Record<EasingName, EasingFn>;

/**
 * @throws {Error} if name is not a valid EasingName. Message includes
 *   the invalid name and the list of valid names.
 */
export function getEasing(name: string): EasingFn;

export function isEasingName(name: string): name is EasingName;
```

### Easing Function Definitions

| Name | Formula | Notes |
|------|---------|-------|
| `linear` | `t' = t` | Identity |
| `ease_in` | `t' = t²` | Quadratic ease-in |
| `ease_out` | `t' = 1 - (1-t)²` | Quadratic ease-out |
| `ease_in_out` | `t < 0.5 ? 2t² : 1 - (-2t+2)²/2` | Quadratic ease-in-out |
| `ease_out_cubic` | `t' = 1 - (1-t)³` | Cubic ease-out |
| `ease_in_out_cubic` | `t < 0.5 ? 4t³ : 1 - (-2t+2)³/2` | Cubic ease-in-out |

**Invariants (all six):**
- `f(0) === 0` exactly (boundary special-case, not computed from formula)
- `f(1) === 1` exactly (boundary special-case, not computed from formula)
- Monotonically non-decreasing on `[0, 1]`

**Behavior outside `[0, 1]`:** Undefined. Easing functions are never called with values outside `[0, 1]` by `interpolate()` (see computation contract below). Direct callers who pass out-of-range values get formula results — no throw, no clamp, but no guarantees about monotonicity or range.

### Module: `src/interpolation/interpolate.ts`

```typescript
import { EasingFn, EasingName } from './easings';

export interface InterpolateOptions {
  easing?: EasingFn | EasingName;
  extrapolate?: 'clamp' | 'extend';
}

/**
 * Maps a value from an input range to an output range with easing.
 *
 * @param value - The current value (e.g., frame number). Must not be NaN.
 * @param inputRange - [start, end]. Both must be finite. start < end.
 * @param outputRange - [start, end]. Both must be finite. start may equal or exceed end.
 * @param options - Easing and extrapolation behavior.
 * @returns The interpolated output value.
 * @throws {Error} if value is NaN.
 * @throws {Error} if any element of inputRange or outputRange is NaN or ±Infinity.
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
   - **`'extend'`:** If `t` is within `[0, 1]`, apply easing normally as above. If `t < 0` or `t > 1`, use **linear extrapolation** from the nearest eased boundary — easing is NOT applied outside `[0, 1]`:
     - If `t < 0`: `result = outputRange[0] + t * (outputRange[1] - outputRange[0])` (linear from the start)
     - If `t > 1`: `result = outputRange[1] + (t - 1) * (outputRange[1] - outputRange[0])` (linear from the eased endpoint)

**Rationale for linear extrapolation in extend mode (Issue 5 fix):** Applying easing functions outside their defined domain `[0, 1]` produces mathematically surprising results (e.g., `ease_in(-0.5) = 0.25`, moving in the wrong direction). Linear extrapolation is the standard approach used by Remotion's `interpolate()` and React Native Reanimated. It guarantees continuous, predictable behavior at the boundaries.

### Module: `src/interpolation/spring.ts`

```typescript
export interface SpringConfig {
  damping: number;   // > 0. Default: 200.
  mass: number;      // > 0. Default: 0.5.
  stiffness: number; // > 0. Default: 10.
}

export const DEFAULT_SPRING_CONFIG: Readonly<SpringConfig>;

/**
 * Computes damped spring response at a given frame.
 * Starts at 0, settles toward 1.
 * Under-damped springs may overshoot 1.0 — output is NOT clamped.
 *
 * @param frame - Current frame (0-based). Must be >= 0.
 * @param fps - Frames per second. Must be > 0.
 * @param config - Spring parameters. All must be > 0.
 * @returns Spring response value (unclamped).
 * @throws {Error} if frame < 0, fps <= 0, or any config value <= 0.
 * @throws {Error} if intermediate physics computation produces NaN or ±Infinity
 *   (degenerate config). Message describes which config values caused the issue.
 */
export function spring(
  frame: number,
  fps: number,
  config?: Partial<SpringConfig>
): number;
```

**Physics contract (unchanged from seed Section 8.5):**
```
t = frame / fps
ω = √(stiffness / mass)
ζ = damping / (2 × √(stiffness × mass))

If ζ ≥ 1 (critically/over-damped):
  response = 1 - e^(-ωt) × (1 + ωt)

If ζ < 1 (under-damped):
  ωd = ω × √(1 - ζ²)
  response = 1 - e^(-ζωt) × cos(ωd × t)
```

**Non-finite guard (Issue 2 fix):** After computing the response, if the result is NaN or ±Infinity, throw an `Error` describing the degenerate configuration. Do NOT clamp to an arbitrary range. The `[0, 2]` language from the prior draft is removed.

### Module: `src/interpolation/index.ts` (barrel export)

```typescript
export { interpolate, InterpolateOptions } from './interpolate';
export { spring, SpringConfig, DEFAULT_SPRING_CONFIG } from './spring';
export { easings, getEasing, isEasingName, EasingFn, EasingName } from './easings';
```

## Design Decisions

### D1: Isomorphic module shared via build-time bundling
*(Unchanged — Challenger approved.)*

The module lives once in `src/interpolation/`. Consumed by Node.js via normal imports. For the browser context (`src/page/`), the build step bundles it into the page JS. Uses only pure math — no Node.js APIs, no DOM APIs. Written as pure ES module code.

### D2: Two-element inputRange/outputRange only
*(Unchanged — Challenger approved.)*

Multi-segment deferred per OQ-06. Composable via chaining.

### D3: Clamp by default, extend as opt-in with linear extrapolation beyond boundaries
*(Revised per Issue 5.)*

Clamp is the default for safety (C-06). In `extend` mode, easing applies only within `[0, 1]`; extrapolation beyond boundaries is always linear. This prevents surprising behavior from easing functions evaluated outside their domain.

### D4: Easing as function or string name
*(Unchanged — Challenger approved.)*

### D5: Spring uses physical units (frame + fps)
*(Unchanged — Challenger approved.)*

### D6: No mutable state, no side effects
*(Unchanged — Challenger approved.)*

### D7: Fail-fast on invalid numeric inputs *(NEW — Issue 1 fix)*

**Decision:** `interpolate()` throws on NaN `value` and on non-finite (NaN or ±Infinity) range elements. `spring()` throws on non-finite intermediate physics results.

**Rationale:** Silent NaN propagation through the pipeline produces corrupt frames that are invisible to the blind-authoring LLM (violates C-06). A NaN camera position in Three.js renders garbage without error. Failing fast at the math primitive level is the last line of defense. ±Infinity in `value` with clamp mode is acceptable (it clamps to a boundary) — this handles legitimate edge cases like division-by-zero upstream that accidentally produces Infinity but where clamping is the correct behavior. ±Infinity in range elements is always a bug.

## Acceptance Criteria

**Floating-point tolerance preamble (Issue 6 fix):**
- For linear operations (no easing, or `linear` easing), exact equality (`===`) is expected.
- For eased and spring operations, tolerance is `±1e-10` unless the AC specifies otherwise.
- ACs that say "approximately" state their tolerance explicitly.

### Easing ACs

- [ ] **AC-01:** All six named easing functions are exported and satisfy `f(0) === 0` and `f(1) === 1` exactly.
- [ ] **AC-02:** All six easing functions are monotonically non-decreasing on `[0, 1]`, verified by sampling at 1000 evenly-spaced points.
- [ ] **AC-17:** `isEasingName('ease_in')` returns `true`; `isEasingName('bounce')` returns `false`.
- [ ] **AC-16:** `getEasing('nonexistent')` throws an `Error` whose message includes `'nonexistent'` and lists valid easing names.

### Interpolate ACs

- [ ] **AC-03:** `interpolate(50, [0, 100], [0, 10])` returns `5.0` exactly.
- [ ] **AC-04:** `interpolate(-10, [0, 100], [0, 10])` returns `0.0` exactly (clamp default).
- [ ] **AC-05:** `interpolate(150, [0, 100], [0, 10])` returns `10.0` exactly (clamp default).
- [ ] **AC-06:** `interpolate(150, [0, 100], [0, 10], { extrapolate: 'extend' })` returns `15.0` exactly (linear extrapolation beyond endpoint).
- [ ] **AC-07:** `interpolate(50, [0, 100], [10, 0])` returns `5.0` exactly (reverse output range).
- [ ] **AC-08:** `interpolate(50, [0, 100], [0, 10], { easing: 'ease_in' })` returns `2.5` within `±1e-10` (quadratic: `0.5² = 0.25`, mapped to `0.25 * 10 = 2.5`).
- [ ] **AC-09:** `interpolate(50, [0, 100], [0, 10], { easing: 'invalid_name' })` throws an `Error` whose message includes `'invalid_name'` and lists valid names.
- [ ] **AC-10:** `interpolate(50, [100, 100], [0, 10])` throws (inputRange[0] not less than inputRange[1]).
- [ ] **AC-21:** `interpolate(NaN, [0, 100], [0, 10])` throws an `Error`. *(Issue 1 fix)*
- [ ] **AC-22:** `interpolate(50, [0, 100], [0, 10], { easing: (t) => t * t })` returns `2.5` within `±1e-10` (function reference path). *(Issue 3 fix)*
- [ ] **AC-23:** `interpolate(5, [0, Infinity], [0, 10])` throws an `Error` (non-finite range element). *(Issue 4 fix)*
- [ ] **AC-24:** `interpolate(120, [0, 100], [0, 10], { easing: 'ease_in', extrapolate: 'extend' })` returns `12.0` exactly. Derivation: `t = 1.2`, which is > 1, so linear extrapolation from the eased endpoint: `outputRange[1] + (t - 1) * (outputRange[1] - outputRange[0]) = 10 + 0.2 * 10 = 12.0`. *(Issue 5 fix)*
- [ ] **AC-26:** `interpolate(-20, [0, 100], [0, 10], { easing: 'ease_in', extrapolate: 'extend' })` returns `-2.0` exactly. Derivation: `t = -0.2`, which is < 0, so linear extrapolation from start: `outputRange[0] + t * (outputRange[1] - outputRange[0]) = 0 + (-0.2) * 10 = -2.0`. *(Additional extend test for negative side)*

### Spring ACs

- [ ] **AC-11:** `spring(0, 30)` returns `0.0` exactly.
- [ ] **AC-12:** `spring(300, 30)` with default config returns approximately `1.0` (within `±0.001`).
- [ ] **AC-13:** `spring()` with default config (damping: 200, mass: 0.5, stiffness: 10) is over-damped (ζ > 1), verified by checking that the response is monotonically non-decreasing over 300 frames.
- [ ] **AC-14:** `spring()` with under-damped config `{ damping: 5, mass: 0.5, stiffness: 100 }` produces a response exceeding 1.0 at some frame in `[0, 300]`.
- [ ] **AC-15:** `spring(-1, 30)` throws. `spring(0, 0)` throws. `spring(0, 30, { damping: 0 })` throws. `spring(0, 30, { mass: -1 })` throws.

### General ACs

- [ ] **AC-18:** The module has zero runtime dependencies (no imports outside `src/interpolation/`).
- [ ] **AC-19:** The module uses no Node.js-specific APIs and no browser-specific APIs.
- [ ] **AC-20:** Calling `interpolate()` and `spring()` 100,000 times with identical inputs produces identical results across runs.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `interpolate(NaN, ...)` | **Throws** `Error`: "interpolate: value must not be NaN" |
| `interpolate(5, [0, NaN], [0, 10])` | **Throws** `Error`: "interpolate: inputRange elements must be finite numbers" |
| `interpolate(5, [0, 100], [NaN, 10])` | **Throws** `Error`: "interpolate: outputRange elements must be finite numbers" |
| `interpolate(5, [0, Infinity], [0, 10])` | **Throws** `Error`: "interpolate: inputRange elements must be finite numbers" |
| `interpolate(Infinity, [0, 100], [0, 10])` | With clamp: returns `10.0`. With extend: returns `Infinity`. (±Infinity `value` is allowed.) |
| `inputRange[0] === inputRange[1]` | **Throws** `Error`: "interpolate: inputRange start must be less than end" |
| `inputRange[0] > inputRange[1]` | **Throws** same as above |
| `outputRange[0] === outputRange[1]` | Returns `outputRange[0]` for any valid input. No throw. |
| Easing boundary `t = 0` or `t = 1` | Returns exactly `0` or `1` via explicit boundary check. |
| Extend mode, `t < 0` | Linear extrapolation (easing NOT applied). |
| Extend mode, `t > 1` | Linear extrapolation from eased endpoint (easing NOT applied). |
| `spring(0, fps)` any valid fps/config | Returns `0.0` exactly. |
| `spring()` with extreme config producing non-finite ω or response | **Throws** `Error` describing degenerate config. |
| `spring()` under-damped, response > 1.0 | Valid. Output is NOT clamped. Caller's responsibility. |
| `spring()` very high damping | Converges slowly. Valid. No throw. |
| Custom `EasingFn` that returns values outside `[0,1]` | Output extends beyond `outputRange`. Valid — no output-side clamping. |

## Test Strategy

### Unit Tests

**Easing functions (per function × 6):**
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
- Every function called 1000× with same inputs → all outputs identical.

### Relevant Testable Claims
- **TC-06** (deterministic output) — interpolation determinism is a prerequisite.
- **TC-09** (eased paths feel natural) — partially validated by confirming eased outputs diverge meaningfully from linear.

## Integration Points

- **Depends on:** Nothing. Tier 0 foundation.
- **Consumed by:**
  - **OBJ-006** (Camera Path Presets) — `interpolate()` with easings for `position(t)` and `lookAt(t)`.
  - **OBJ-008** (Transition System) — `interpolate()` for opacity during crossfade/dip-to-black.
  - **OBJ-079** (downstream per index.json).
  - **Browser context** (`src/page/scene-renderer.js`) — same functions bundled into page JS.
  - **Node.js context** (`src/scenes/scene-sequencer.ts`) — transition timing.
- **File placement:**
  ```
  src/interpolation/
  ├── easings.ts
  ├── interpolate.ts
  ├── spring.ts
  └── index.ts
  ```
  Note: Seed Section 4.5 places these under `src/scenes/cameras/`. This spec proposes `src/interpolation/` instead because these utilities serve both cameras AND transitions — they are not camera-specific. The build system must bundle this module into `src/page/` for browser use.

## Open Questions

- **OQ-A:** Multi-segment `interpolate()` deferred. Composable via chaining multiple calls or a future `interpolateSegments()` wrapper.
- **OQ-B:** `clampedSpring()` convenience deferred. Trivially done with `Math.min(1, spring(...))` at callsite.

---

Challenger — I believe this addresses all six issues:

1. **Critical (NaN):** `interpolate()` now throws on NaN value and non-finite range elements. AC-21 and AC-23 added.
2. **Major (spring clamp):** `[0, 2]` clamp removed. Spring throws on non-finite intermediate results. Output is unclamped.
3. **Major (EasingFn path):** AC-22 added testing function reference.
4. **Major (Infinity in ranges):** Range elements must be finite. AC-23 covers this. ±Infinity `value` is still allowed (clamps or extends).
5. **Minor (extend + easing):** Computation contract now specifies linear extrapolation outside `[0, 1]` regardless of easing. AC-24 and AC-26 verify both sides.
6. **Minor (float tolerance):** Preamble added to AC section with explicit tolerance rules.

Please verify and approve if this is ready for `output.md`.

---

## Round 4 — spec_challenger

## Challenger Review — Round 4 (Verification)

I'm going through the revised spec systematically, verifying each fix and checking for new issues.

### Verification of Issue Fixes

**Issue 1 (Critical — NaN propagation):** ✅ Fixed. The computation contract now starts with "Validate inputs. Throw on NaN `value`, non-finite range elements." The throws list includes NaN and ±Infinity for ranges. AC-21 tests NaN value. AC-23 tests Infinity in range. Edge case table has explicit rows for NaN in value, inputRange, and outputRange. ±Infinity in `value` is still allowed with clamp (returns boundary) — this is the right call.

**Issue 2 (Major — Spring clamp):** ✅ Fixed. The `[0, 2]` clamp is gone. The spring docstring says "output is NOT clamped." The throws clause says it throws on non-finite intermediate results. Edge case table confirms unclamped overshoot is valid.

**Issue 3 (Major — EasingFn path):** ✅ Fixed. AC-22 tests `{ easing: (t) => t * t }` and expects `2.5`.

**Issue 4 (Major — Infinity in ranges):** ✅ Fixed. Throws clause explicitly lists non-finite range elements. AC-23 covers it.

**Issue 5 (Minor — extend + easing):** ✅ Fixed. Computation contract specifies linear extrapolation outside `[0, 1]` for both sides. AC-24 tests positive extrapolation with derivation. AC-26 tests negative extrapolation with derivation. The formulas are correct — I checked the math.

**Issue 6 (Minor — float tolerance):** ✅ Fixed. Preamble added with explicit rules: exact for linear, ±1e-10 for eased/spring.

All six original issues are structurally addressed. Good.

### New Issue Scan

**Checking for issues introduced by revisions:**

**Issue 7 — MINOR: ±Infinity `value` with `extend` mode returns `Infinity` — is this actually safe?**

The edge case table says `interpolate(Infinity, [0, 100], [0, 10])` with extend returns `Infinity`. The computation would be: `t = (Infinity - 0) / 100 = Infinity`, then since `t > 1`, linear extrapolation: `10 + (Infinity - 1) * 10 = Infinity`. That's IEEE 754 correct. But should the spec document this explicitly since it means extend mode has a different failure profile than clamp mode? ... Actually, this is fine. The caller opted into extend mode. If they pass Infinity, they get Infinity back. That's the contract. Not blocking.

**Issue 8 — MINOR: AC-08 expected value derivation should be explicit**

AC-08 states `interpolate(50, [0, 100], [0, 10], { easing: 'ease_in' })` returns `2.5` and includes the derivation `(0.5² = 0.25, mapped to 0.25 * 10 = 2.5)`. Good — the derivation is there. No issue.

**Checking vocabulary compliance:** The spec uses "easing" consistently with seed Section 2. Uses "camera path" not "camera motion." No vocabulary drift detected.

**Checking scope discipline:** The spec defines math primitives only. No scene geometry logic, no camera path logic, no rendering logic. Clean boundaries.

**Checking constraint compliance:** C-01 (zero-license) — pure math, zero deps. C-05 (deterministic) — pure functions, AC-20 verifies. C-06 (blind authorable) — fail-fast on bad inputs supports this. All good.

**Checking downstream compatibility:** OBJ-006 (camera paths) will need `interpolate()` with easing names from manifests — the string-or-function API handles this. OBJ-008 (transitions) needs opacity interpolation — `interpolate(frame, [startFrame, endFrame], [1, 0])` works cleanly. The barrel export provides everything downstream needs.

**One last check — the `spring()` at frame 0 with config merging:** The signature says `config?: Partial<SpringConfig>`. AC-11 calls `spring(0, 30)` with no config. The spec says defaults are damping: 200, mass: 0.5, stiffness: 10. But the merging behavior isn't spelled out — does it do `{ ...DEFAULT_SPRING_CONFIG, ...config }` shallow merge? For `Partial<SpringConfig>`, if someone passes `{ damping: 5 }`, do mass and stiffness keep defaults? This is obvious enough from `Partial<>` semantics and `DEFAULT_SPRING_CONFIG` — an implementer wouldn't guess wrong. Not blocking.

---

I'm satisfied. All critical and major issues from Round 2 are verified as fixed. The spec is precise enough for a competent implementer to build from without guessing. Let me write it to disk.

CONCLUSION:

The specification for OBJ-002 is approved. It defines three modules (`easings.ts`, `interpolate.ts`, `spring.ts`) with a barrel export under `src/interpolation/`. Key decisions: isomorphic pure-math module shared via build-time bundling; two-element ranges only; clamp by default with linear extrapolation in extend mode; fail-fast on NaN/non-finite inputs; unclamped spring output. Twenty-two acceptance criteria cover all paths including error cases, with explicit floating-point tolerance rules.

Let me write the files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Write,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me check the existing file structure first.
[Tool: Bash]
  Input: {
  "command": "ls -la nodes/OBJ-002/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-002 node directory exists"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-002",
     3→  "description": "Interpolation, easing, and spring utilities -- interpolate(), spring(), all named easing functions (linear, ease_in, ease_out, ease_in_out, ease_out_cubic, ease_in_out_cubic) per Section 8.5. Must specify whether these utilities are shared between Node.js (scene sequencer transition timing) and browser (camera interpolation) contexts, and the sharing mechanism (isomorphic module, duplication, or build-time inclusion in page bundle).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": [],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 0 foundation. No dependencies. Math primitives used by every camera path and transition."
    12→}
    13→
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:15 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   797 Mar 22 19:15 meta.json
Good. Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md",
  "content": "# Specification: OBJ-002 \u2014 Interpolation, Easing, and Spring Utilities\n\n## Summary\n\nOBJ-002 defines the math primitives that underpin all animation in depthkit: an `interpolate()` function for mapping frame numbers to output values, a `spring()` function for organic/physics-based motion, and six named easing functions. These utilities are isomorphic \u2014 they must run identically in both the Node.js orchestrator (scene sequencer transition timing) and the headless Chromium browser (Three.js camera interpolation). This is a Tier 0 foundation with no dependencies; every camera path preset, scene transition, and FOV animation consumes these primitives.\n\n## Interface Contract\n\n### Module: `src/interpolation/easings.ts`\n\n```typescript\n/**\n * An easing function maps normalized time t in [0,1] to eased time t' in [0,1].\n * Behavior outside [0,1] is undefined (see design notes).\n */\nexport type EasingFn = (t: number) => number;\n\n/** Named easing registry key. These names appear in manifests. */\nexport type EasingName =\n  | 'linear'\n  | 'ease_in'\n  | 'ease_out'\n  | 'ease_in_out'\n  | 'ease_out_cubic'\n  | 'ease_in_out_cubic';\n\n/**\n * Registry mapping easing names to functions.\n * Keyed by EasingName. Used for manifest-driven lookups.\n */\nexport const easings: Record<EasingName, EasingFn>;\n\n/**\n * Retrieves an easing function by name.\n * @throws {Error} if name is not a valid EasingName. Error message must include\n *   the invalid name and the list of valid names.\n */\nexport function getEasing(name: string): EasingFn;\n\n/**\n * Type guard: returns true if input is a valid EasingName.\n */\nexport function isEasingName(name: string): name is EasingName;\n```\n\n### Easing Function Definitions (mathematical contracts)\n\n| Name | Formula | Notes |\n|------|---------|-------|\n| `linear` | `t' = t` | Identity |\
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/meta.json",
  "content": "{\n  \"id\": \"OBJ-002\",\n  \"description\": \"Interpolation, easing, and spring utilities -- interpolate(), spring(), all named easing functions (linear, ease_in, ease_out, ease_in_out, ease_out_cubic, ease_in_out_cubic) per Section 8.5. Must specify whether these utilities are shared between Node.js (scene sequencer transition timing) and browser (camera interpolation) contexts, and the sharing mechanism (isomorphic module, duplication, or build-time inclusion in page bundle).\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-22T23:45:00Z\",\n  \"depends_on\": [],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 0 foundation. No dependencies. Math primitives used by every camera path and transition.\",\n  \"status\": \"spec_complete\",\n  \"spec_version\": \"1.0\",\n  \"deliberation_rounds\": 4\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/meta.json has been updated successfully.
Now let me commit.
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-002/output.md nodes/OBJ-002/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-002): interpolation, easing, and spring utilities\n\nDefines interface contracts for interpolate(), spring(), and 6 named\neasing functions. Key decisions: isomorphic pure-math module at\nsrc/interpolation/, fail-fast on NaN/non-finite inputs, clamp by\ndefault with linear extrapolation in extend mode, unclamped spring\noutput. 22 acceptance criteria covering all paths and error cases.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-002 spec and updated meta.json"
}
[Tool Result] [master 90a2c38] spec(OBJ-002): interpolation, easing, and spring utilities
 2 files changed, 356 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-002/output.md
The spec is committed. Here's a summary of the deliberation outcome:

## Deliberation Result

**Converged in 4 rounds.** The final specification for OBJ-002 defines three modules under `src/interpolation/`:

1. **`easings.ts`** — 6 named easing functions with exact boundary guarantees, a registry, `getEasing()` lookup, and `isEasingName()` type guard
2. **`interpolate.ts`** — Two-element range interpolation with clamp/extend modes, string-or-function easing, and fail-fast validation on NaN/non-finite inputs
3. **`spring.ts`** — Damped spring physics (over-damped and under-damped) with unclamped output and degenerate-config guards

**Key decisions resolved through deliberation:**
- **Issue 1 (Critical):** NaN propagation → changed to throw (silent corruption violated C-06)
- **Issue 2 (Major):** Arbitrary `[0, 2]` spring clamp → removed; throw on non-finite results instead
- **Issue 3 (Major):** Missing test for `EasingFn` function path → AC-22 added
- **Issue 4 (Major):** Infinity in ranges unaddressed → ranges must be finite, AC-23 added
- **Issue 5 (Minor):** Easing outside `[0,1]` in extend mode → linear extrapolation beyond boundaries
- **Issue 6 (Minor):** No float tolerance guidance → explicit preamble added
