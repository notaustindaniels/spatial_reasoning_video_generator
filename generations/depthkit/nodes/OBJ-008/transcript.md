# Deliberation Transcript: OBJ-008

---

## Round 1 — spec_author

Looking at OBJ-008's metadata, dependencies, and the seed document sections on transitions (Section 2, 4.6, 8.8), let me propose the full specification.

---

# Specification: OBJ-008 — Transition Type Contract

## Summary

OBJ-008 defines the named transition preset system for depthkit: the type definitions, duration parameters, opacity computation logic, and overlap semantics that govern how one scene visually hands off to the next. This is a **contract-only** objective — it defines the `TransitionPreset` interface, the three built-in presets (`cut`, `crossfade`, `dip_to_black`), and the `computeTransitionOpacity()` function that downstream consumers (scene sequencer OBJ-036, transition renderer OBJ-037) use to determine per-frame opacity for the outgoing and incoming scenes during a transition window. It depends on OBJ-002's `interpolate()` and easing functions for all opacity interpolation.

## Interface Contract

### Module: `src/transitions/types.ts`

```typescript
import { EasingName } from '../interpolation/easings';

/**
 * Named transition type identifier.
 * These names appear in manifests under transition_in / transition_out.
 */
export type TransitionTypeName = 'cut' | 'crossfade' | 'dip_to_black';

/**
 * Transition specification as it appears in the manifest (per-scene).
 * This is the authored form — what the LLM writes.
 */
export interface TransitionSpec {
  /** The transition type name. */
  type: TransitionTypeName;

  /**
   * Duration of the transition in seconds.
   * Must be >= 0. A duration of 0 is valid and equivalent to 'cut'.
   * For 'cut', duration is ignored (always instantaneous).
   * For 'crossfade' and 'dip_to_black', must be > 0.
   */
  duration: number;

  /**
   * Easing applied to the opacity interpolation.
   * Defaults to 'linear' for crossfade, 'ease_in_out' for dip_to_black.
   * Ignored for 'cut'.
   */
  easing?: EasingName;
}

/**
 * Resolved transition metadata used internally by the scene sequencer
 * and transition renderer. Contains frame-level timing derived from
 * the manifest's second-based TransitionSpec.
 */
export interface ResolvedTransition {
  /** The transition type. */
  type: TransitionTypeName;

  /** Duration in frames (computed from seconds × fps). Always integer >= 0. */
  durationFrames: number;

  /** Easing function name for opacity interpolation. */
  easing: EasingName;

  /**
   * The absolute start frame of the transition window within the composition.
   * For a transition_out on scene A ending at frame 300 with durationFrames=30,
   * overlapStartFrame = 270.
   */
  overlapStartFrame: number;

  /**
   * The absolute end frame of the transition window (exclusive).
   * overlapEndFrame = overlapStartFrame + durationFrames.
   */
  overlapEndFrame: number;
}

/**
 * The opacity values for both scenes during a single frame of a transition.
 */
export interface TransitionOpacityResult {
  /** Opacity of the outgoing (previous) scene. Range [0, 1]. */
  outgoingOpacity: number;

  /** Opacity of the incoming (next) scene. Range [0, 1]. */
  incomingOpacity: number;
}
```

### Module: `src/transitions/presets.ts`

```typescript
import { TransitionTypeName, TransitionSpec } from './types';
import { EasingName } from '../interpolation/easings';

/**
 * Definition of a transition preset's default behavior.
 */
export interface TransitionPresetDefinition {
  /** Human-readable description for SKILL.md / documentation. */
  description: string;

  /** Default easing if not overridden in the manifest. */
  defaultEasing: EasingName;

  /**
   * Whether this transition type creates an overlap window
   * where both scenes must render simultaneously.
   * - 'cut': false (no overlap, instantaneous switch)
   * - 'crossfade': true (both scenes render with complementary opacity)
   * - 'dip_to_black': false (outgoing fades to black, then incoming fades from black;
   *   scenes never render simultaneously — only one scene is visible at any moment,
   *   composited over a black background)
   */
  requiresOverlap: boolean;

  /**
   * Whether this transition type requires a duration > 0.
   * 'cut' does not; 'crossfade' and 'dip_to_black' do.
   */
  requiresDuration: boolean;
}

/**
 * Registry of all built-in transition presets.
 */
export const transitionPresets: Record<TransitionTypeName, TransitionPresetDefinition>;

/**
 * Type guard: returns true if the input is a valid TransitionTypeName.
 */
export function isTransitionTypeName(name: string): name is TransitionTypeName;

/**
 * Retrieves a preset definition by name.
 * @throws {Error} if name is not a valid TransitionTypeName.
 *   Error message must include the invalid name and list valid names.
 */
export function getTransitionPreset(name: string): TransitionPresetDefinition;
```

### Preset Definitions

| Name | `defaultEasing` | `requiresOverlap` | `requiresDuration` | Description |
|------|-----------------|--------------------|--------------------|-------------|
| `cut` | `'linear'` | `false` | `false` | Instantaneous switch. Scene A's last frame is immediately followed by Scene B's first frame. No opacity animation. Duration is ignored (treated as 0). |
| `crossfade` | `'linear'` | `true` | `true` | During the overlap window, Scene A's opacity interpolates from 1→0 and Scene B's from 0→1. Both scenes render simultaneously. The opacity values are complementary: `outgoing + incoming = 1.0` at every frame. |
| `dip_to_black` | `'ease_in_out'` | `false` | `true` | Two-phase transition. **Phase 1** (first half of duration): Scene A's opacity interpolates from 1→0; Scene B is not rendered. **Phase 2** (second half of duration): Scene A is not rendered; Scene B's opacity interpolates from 0→1. At the midpoint, both opacities are 0 — the frame is fully black. Only one scene is ever active at a time. |

### Module: `src/transitions/compute.ts`

```typescript
import { TransitionTypeName, TransitionOpacityResult } from './types';
import { EasingName } from '../interpolation/easings';

/**
 * Computes the opacity of the outgoing and incoming scenes for a single frame
 * within a transition window.
 *
 * @param type - The transition type.
 * @param frame - The current absolute frame number within the composition.
 * @param overlapStartFrame - The first frame of the transition window.
 * @param overlapEndFrame - The frame after the last frame of the transition window (exclusive).
 * @param easing - The easing function name to apply to opacity interpolation.
 * @returns The opacity pair for this frame.
 *
 * @throws {Error} if type is not a valid TransitionTypeName.
 * @throws {Error} if overlapStartFrame >= overlapEndFrame (except for 'cut', where both may be equal).
 * @throws {Error} if frame < overlapStartFrame or frame >= overlapEndFrame.
 * @throws {Error} if easing is not a valid EasingName.
 *
 * Contracts:
 * - For 'cut': always returns { outgoingOpacity: 0, incomingOpacity: 1 }.
 *   (In practice, 'cut' has 0-frame duration, so this function is never called for it.
 *    But if called, it returns the post-cut state.)
 * - For 'crossfade': outgoingOpacity + incomingOpacity === 1.0 at every frame.
 * - For 'dip_to_black': at the midpoint frame, both opacities are 0.
 *   In phase 1: incomingOpacity === 0. In phase 2: outgoingOpacity === 0.
 * - All returned opacity values are in [0, 1].
 */
export function computeTransitionOpacity(
  type: TransitionTypeName,
  frame: number,
  overlapStartFrame: number,
  overlapEndFrame: number,
  easing: EasingName
): TransitionOpacityResult;
```

### Module: `src/transitions/resolve.ts`

```typescript
import { TransitionSpec, ResolvedTransition } from './types';

/**
 * Converts a manifest-level TransitionSpec (seconds-based) into a
 * ResolvedTransition (frame-based) for use by the scene sequencer.
 *
 * @param spec - The transition specification from the manifest.
 * @param fps - Composition frames per second. Must be > 0.
 * @param sceneEndFrame - The absolute frame number where the outgoing scene ends
 *   (for transition_out) or the incoming scene starts (for transition_in).
 *   Used to compute overlapStartFrame and overlapEndFrame.
 * @param direction - Whether this is an outgoing or incoming transition.
 *   'out': the overlap window ends at sceneEndFrame.
 *   'in': the overlap window starts at sceneEndFrame.
 *
 * @returns The resolved transition with frame-based timing.
 *
 * @throws {Error} if spec.type is not a valid TransitionTypeName.
 * @throws {Error} if spec.duration < 0.
 * @throws {Error} if spec.type requires a duration > 0 (crossfade, dip_to_black) and spec.duration <= 0.
 * @throws {Error} if fps <= 0.
 * @throws {Error} if spec.easing is provided and is not a valid EasingName.
 *
 * Duration-to-frames conversion:
 *   durationFrames = Math.round(spec.duration * fps)
 *
 * Overlap window computation:
 *   direction 'out': overlapStartFrame = sceneEndFrame - durationFrames
 *                    overlapEndFrame = sceneEndFrame
 *   direction 'in':  overlapStartFrame = sceneEndFrame
 *                    overlapEndFrame = sceneEndFrame + durationFrames
 */
export function resolveTransition(
  spec: TransitionSpec,
  fps: number,
  sceneEndFrame: number,
  direction: 'in' | 'out'
): ResolvedTransition;
```

### Module: `src/transitions/index.ts` (barrel export)

```typescript
export type {
  TransitionTypeName,
  TransitionSpec,
  ResolvedTransition,
  TransitionOpacityResult,
} from './types';
export type { TransitionPresetDefinition } from './presets';
export {
  transitionPresets,
  isTransitionTypeName,
  getTransitionPreset,
} from './presets';
export { computeTransitionOpacity } from './compute';
export { resolveTransition } from './resolve';
```

## Design Decisions

### D1: `crossfade` uses complementary opacity (outgoing + incoming = 1.0); `dip_to_black` uses two-phase non-overlapping opacity

**Decision:** Crossfade renders both scenes simultaneously with `outgoing = 1 - t'` and `incoming = t'`. Dip-to-black is a two-phase transition: in the first half, only the outgoing scene is visible (opacity 1→0); in the second half, only the incoming scene is visible (opacity 0→1). At the midpoint, both opacities are 0 (fully black frame).

**Rationale:** Seed Section 8.8 states: "Scene A's opacity interpolates from 1 to 0; scene B's from 0 to 1." This describes crossfade. Dip-to-black by definition passes through black — meaning there's a moment where neither scene is visible. This is the standard After Effects / Premiere behavior. Having `requiresOverlap: false` for dip-to-black means the scene sequencer (OBJ-036) can optimize by only rendering one scene per frame during a dip-to-black, while crossfade requires rendering both.

**Alternative considered:** Additive blending where both opacities can sum > 1.0 during crossfade (produces a "flash" at the midpoint). Rejected: the flash is usually an unwanted artifact and the seed's description implies complementary blending.

### D2: Transition timing is symmetric for dip_to_black

**Decision:** Dip-to-black splits its duration exactly in half: the midpoint frame is `overlapStartFrame + Math.floor(durationFrames / 2)`. Phase 1 runs from `overlapStartFrame` to the midpoint (exclusive); phase 2 runs from the midpoint to `overlapEndFrame` (exclusive). If `durationFrames` is odd, phase 1 gets the extra frame (the midpoint frame has both opacities at 0).

**Rationale:** Symmetric dip-to-black is the standard behavior. The midpoint frame being fully black is the defining characteristic of this transition type. Giving phase 1 the extra frame on odd durations ensures the "dip" moment happens, and the convention is arbitrary but must be deterministic.

### D3: `cut` has zero duration and no opacity computation

**Decision:** A `cut` transition is instantaneous — `durationFrames` is always 0 regardless of what `duration` the manifest specifies. The scene sequencer switches scenes between frames with no overlap window. `computeTransitionOpacity` can be called for `cut` but always returns `{ outgoingOpacity: 0, incomingOpacity: 1 }` — this is a safety fallback, not the expected path.

**Rationale:** A cut is the absence of a transition. Making `duration` ignored (not rejected) for `cut` simplifies manifest authoring — the LLM doesn't need to remember to omit the duration field.

### D4: Easing is applied to the normalized progress, not the opacity value

**Decision:** The easing function transforms the normalized time `t ∈ [0,1]` within the transition window before mapping to opacity. For crossfade: `t' = easing(t)`, then `outgoing = 1 - t'`, `incoming = t'`. For dip-to-black phase 1: `t' = easing(t_phase)`, then `outgoing = 1 - t'`, `incoming = 0`. For phase 2: `t' = easing(t_phase)`, then `outgoing = 0`, `incoming = t'`.

**Rationale:** This is the standard approach — easing controls the *rate* of the transition, not the *shape* of the opacity curve. An `ease_in_out` crossfade starts slow, speeds up in the middle, and slows at the end. The OBJ-002 `interpolate()` function naturally handles this by accepting an easing parameter.

### D5: `resolveTransition()` uses `Math.round()` for duration-to-frames conversion

**Decision:** `durationFrames = Math.round(spec.duration * fps)`. Not `Math.floor()`, not `Math.ceil()`.

**Rationale:** A 1-second transition at 30fps is exactly 30 frames. A 0.5-second transition at 30fps is exactly 15 frames. A 0.7-second transition at 30fps is `Math.round(21)` = 21 frames. Rounding minimizes the perceptual error between the authored duration and the actual duration. Floor would systematically shorten transitions; ceil would systematically lengthen them.

### D6: Transition direction (`in`/`out`) is resolved per-scene, not per-boundary

**Decision:** The manifest specifies `transition_in` and `transition_out` per scene (per seed Section 4.6). The `resolveTransition()` function takes a `direction` parameter to correctly position the overlap window relative to a scene boundary. The scene sequencer (OBJ-036) is responsible for pairing adjacent scenes' `transition_out` / `transition_in` and resolving potential conflicts.

**Rationale:** The seed's manifest schema (Section 4.6) shows `transition_in` and `transition_out` as per-scene properties. This objective defines the contract for a single transition spec; the sequencer handles the multi-scene orchestration. Conflict resolution (e.g., scene A has `transition_out: crossfade 1s` but scene B has `transition_in: dip_to_black 2s`) is deferred to OBJ-036.

### D7: Separation of `computeTransitionOpacity` from `resolveTransition`

**Decision:** Resolution (seconds→frames, positioning in the composition timeline) is separated from computation (frame→opacity pair). `resolveTransition()` produces a `ResolvedTransition` with frame-based timing. `computeTransitionOpacity()` takes frame-level parameters and returns opacity values.

**Rationale:** The scene sequencer (OBJ-036) needs `resolveTransition()` during manifest processing to build the composition timeline. The transition renderer (OBJ-037) needs `computeTransitionOpacity()` on a per-frame basis during rendering. Different consumers, different call patterns, clean separation.

### D8: This module is pure and isomorphic (same as OBJ-002)

**Decision:** All functions are pure, stateless, and use only OBJ-002 imports plus basic math. No Node.js or browser APIs. Can run in both the orchestrator (Node.js) and the headless browser page.

**Rationale:** The scene sequencer runs in Node.js; the transition renderer may need opacity values in the browser context for Three.js material animation. Same sharing strategy as OBJ-002 (D1).

## Acceptance Criteria

### Preset Registry ACs

- [ ] **AC-01:** `isTransitionTypeName('cut')`, `isTransitionTypeName('crossfade')`, and `isTransitionTypeName('dip_to_black')` all return `true`.
- [ ] **AC-02:** `isTransitionTypeName('wipe')` returns `false`.
- [ ] **AC-03:** `getTransitionPreset('crossfade')` returns a `TransitionPresetDefinition` with `requiresOverlap: true` and `defaultEasing: 'linear'`.
- [ ] **AC-04:** `getTransitionPreset('invalid')` throws an `Error` whose message includes `'invalid'` and lists the three valid transition type names.
- [ ] **AC-05:** `transitionPresets` contains exactly three entries: `cut`, `crossfade`, `dip_to_black`.

### Cut ACs

- [ ] **AC-06:** `computeTransitionOpacity('cut', 0, 0, 0, 'linear')` returns `{ outgoingOpacity: 0, incomingOpacity: 1 }`.
- [ ] **AC-07:** `resolveTransition({ type: 'cut', duration: 5.0 }, 30, 100, 'out')` returns a `ResolvedTransition` with `durationFrames: 0` (duration ignored for cut).

### Crossfade ACs

- [ ] **AC-08:** For a 30-frame crossfade (1 second at 30fps) with `linear` easing, `computeTransitionOpacity('crossfade', overlapStart, overlapStart, overlapStart + 30, 'linear')` returns `{ outgoingOpacity: 1.0, incomingOpacity: 0.0 }` (first frame).
- [ ] **AC-09:** For the same 30-frame crossfade, `computeTransitionOpacity('crossfade', overlapStart + 29, overlapStart, overlapStart + 30, 'linear')` returns `{ outgoingOpacity: ≈0.0333, incomingOpacity: ≈0.9667 }` (last frame, within ±1e-10).
- [ ] **AC-10:** For the same 30-frame crossfade, at every frame `f` in `[overlapStart, overlapStart + 30)`, `outgoingOpacity + incomingOpacity === 1.0` within ±1e-10.
- [ ] **AC-11:** For a crossfade at the midpoint frame (frame 15 of 30), `computeTransitionOpacity('crossfade', overlapStart + 15, overlapStart, overlapStart + 30, 'linear')` returns `{ outgoingOpacity: 0.5, incomingOpacity: 0.5 }` within ±1e-10.
- [ ] **AC-12:** For a crossfade with `ease_in_out` easing at the midpoint, the opacity values differ from the linear case (verifying easing is applied).

### Dip-to-Black ACs

- [ ] **AC-13:** For a 30-frame dip-to-black, at frame `overlapStart` (first frame): `outgoingOpacity === 1.0`, `incomingOpacity === 0.0`.
- [ ] **AC-14:** At the midpoint frame (`overlapStart + 15`): `outgoingOpacity === 0.0`, `incomingOpacity === 0.0` (fully black).
- [ ] **AC-15:** At the last frame (`overlapStart + 29`): `outgoingOpacity === 0.0`, `incomingOpacity` is close to `1.0` (within ±0.05, accounting for easing and discrete frame steps).
- [ ] **AC-16:** At every frame in a dip-to-black transition, at most one of `outgoingOpacity` or `incomingOpacity` is > 0 (they are never both visible simultaneously).
- [ ] **AC-17:** For a dip-to-black with odd `durationFrames` (e.g., 31), the midpoint frame (`overlapStart + 15`) has both opacities at 0.

### Resolve ACs

- [ ] **AC-18:** `resolveTransition({ type: 'crossfade', duration: 1.0 }, 30, 300, 'out')` returns `{ durationFrames: 30, overlapStartFrame: 270, overlapEndFrame: 300, easing: 'linear', type: 'crossfade' }`.
- [ ] **AC-19:** `resolveTransition({ type: 'crossfade', duration: 1.0 }, 30, 300, 'in')` returns `{ durationFrames: 30, overlapStartFrame: 300, overlapEndFrame: 330, easing: 'linear', type: 'crossfade' }`.
- [ ] **AC-20:** `resolveTransition({ type: 'dip_to_black', duration: 0.5 }, 30, 100, 'out')` returns `{ durationFrames: 15, overlapStartFrame: 85, overlapEndFrame: 100, easing: 'ease_in_out', type: 'dip_to_black' }` (default easing applied).
- [ ] **AC-21:** `resolveTransition({ type: 'crossfade', duration: 1.0, easing: 'ease_out' }, 30, 300, 'out')` returns `easing: 'ease_out'` (manifest easing overrides default).
- [ ] **AC-22:** `resolveTransition({ type: 'crossfade', duration: 0.7 }, 30, 300, 'out')` returns `durationFrames: 21` (`Math.round(0.7 * 30) = 21`).

### Error Handling ACs

- [ ] **AC-23:** `resolveTransition({ type: 'crossfade', duration: -1 }, 30, 100, 'out')` throws an `Error` mentioning negative duration.
- [ ] **AC-24:** `resolveTransition({ type: 'crossfade', duration: 0 }, 30, 100, 'out')` throws an `Error` mentioning that crossfade requires duration > 0.
- [ ] **AC-25:** `resolveTransition({ type: 'dip_to_black', duration: 0 }, 30, 100, 'out')` throws an `Error` mentioning that dip_to_black requires duration > 0.
- [ ] **AC-26:** `resolveTransition({ type: 'wipe' as any, duration: 1 }, 30, 100, 'out')` throws an `Error` listing valid transition types.
- [ ] **AC-27:** `computeTransitionOpacity('crossfade', 50, 60, 90, 'linear')` throws (frame < overlapStartFrame).
- [ ] **AC-28:** `computeTransitionOpacity('crossfade', 90, 60, 90, 'linear')` throws (frame >= overlapEndFrame).
- [ ] **AC-29:** `resolveTransition({ type: 'crossfade', duration: 1, easing: 'bounce' as any }, 30, 100, 'out')` throws an `Error` mentioning invalid easing name.

### General ACs

- [ ] **AC-30:** The module has no runtime dependencies outside `src/interpolation/` (OBJ-002).
- [ ] **AC-31:** The module uses no Node.js-specific or browser-specific APIs (isomorphic, per D8).
- [ ] **AC-32:** All functions are pure — no mutable state, no side effects. Calling the same function with the same arguments always returns the same result.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `cut` with non-zero duration in manifest | Duration is silently ignored; `durationFrames` resolved to 0. No error. |
| `crossfade` with `duration: 0` | **Throws**: crossfade requires `duration > 0`. |
| `dip_to_black` with `duration: 0` | **Throws**: dip_to_black requires `duration > 0`. |
| Negative duration | **Throws**: duration must be >= 0. |
| Unknown transition type | **Throws** with message listing valid types. |
| Unknown easing name in TransitionSpec | **Throws** with message listing valid easing names (delegates to OBJ-002's `getEasing()`). |
| `fps <= 0` in `resolveTransition` | **Throws**: fps must be > 0. |
| Very short crossfade (`durationFrames` = 1) | Valid. Single frame where `outgoingOpacity` and `incomingOpacity` are both computed. For 1-frame crossfade with linear easing: at frame 0 of 1, `t = 0/1 = 0`, so `outgoing = 1.0`, `incoming = 0.0`. This is effectively a cut that happens one frame early. Technically correct but may look odd — the SKILL.md should recommend minimum 0.25s. |
| Very short dip-to-black (`durationFrames` = 2) | Phase 1 is frame 0 (midpoint = `Math.floor(2/2)` = frame 1). Frame 0: outgoing fades; frame 1 starts phase 2: incoming fades in. Valid but abrupt. |
| `dip_to_black` with `durationFrames` = 1 | Midpoint = `Math.floor(1/2)` = 0. Phase 1 has 0 frames (empty). Phase 2 runs frame 0. Result: `outgoing = 0, incoming = 0` at the only frame (the midpoint). Edge case: the midpoint IS the only frame, so the screen is black for 1 frame. Valid but degenerate. |
| `computeTransitionOpacity` called for frame outside the overlap window | **Throws**: frame must be within `[overlapStartFrame, overlapEndFrame)`. The scene sequencer should never call this for frames outside the window. |
| `overlapStartFrame` is negative (scene starts before composition) | No special handling — frame math works with any integers. The scene sequencer (OBJ-036) is responsible for ensuring overlap windows don't extend before frame 0. |
| `dip_to_black` midpoint calculation with even vs odd `durationFrames` | Midpoint frame index within the window = `Math.floor(durationFrames / 2)`. Phase 1: frames `[0, midpoint)`. Phase 2: frames `[midpoint, durationFrames)`. At exactly the midpoint frame, we are in phase 2 with `t_phase2 = 0`, so `incoming = 0`. Combined with outgoing already being 0 (not in phase 1), this frame is fully black. |

## Test Strategy

### Unit Tests

**Preset registry:**
- All three presets exist with correct metadata fields.
- `isTransitionTypeName` positive/negative cases.
- `getTransitionPreset` valid/invalid lookups.

**`computeTransitionOpacity` — crossfade:**
- First frame, last frame, midpoint, quarter-points with linear easing.
- Complementary opacity invariant (`out + in = 1.0`) checked across all frames of a 30-frame crossfade.
- Same tests with `ease_in_out` easing — verify values differ from linear.
- 1-frame crossfade edge case.

**`computeTransitionOpacity` — dip_to_black:**
- First frame (outgoing = 1, incoming = 0), midpoint (both 0), last frame (outgoing = 0, incoming ≈ 1).
- Non-overlap invariant: at every frame, `min(outgoingOpacity, incomingOpacity) === 0`.
- Even and odd `durationFrames` midpoint behavior.
- 1-frame and 2-frame edge cases.

**`computeTransitionOpacity` — cut:**
- Returns `{ outgoing: 0, incoming: 1 }` for any valid call.

**`resolveTransition`:**
- All three types with standard values.
- Direction `in` vs `out` positioning.
- Duration rounding (`Math.round`).
- Default easing assignment per type.
- Manifest easing override.
- All error cases (negative duration, zero duration on crossfade/dip, bad type, bad easing, bad fps).

**Determinism:**
- All functions called 1000x with identical inputs produce identical results.

### Relevant Testable Claims
- **TC-10** (cross-scene transitions mask compositing seams) — this objective provides the opacity computation contract; TC-10 validation requires the renderer (OBJ-037) and visual review.
- **TC-06** (deterministic output) — pure functions guarantee deterministic opacity values.

## Integration Points

### Depends on:
- **OBJ-002** (`src/interpolation/`) — `interpolate()` for opacity mapping, `getEasing()` / `isEasingName()` for easing validation, `EasingName` type.

### Consumed by:
- **OBJ-036** (Scene Sequencer) — uses `resolveTransition()` to build the composition timeline, determining which frames require overlap rendering. Uses `TransitionSpec` and `ResolvedTransition` types for its internal data model.
- **OBJ-037** (Transition Renderer) — uses `computeTransitionOpacity()` per-frame during rendering to set Three.js material opacity on outgoing/incoming scenes.
- **OBJ-010** (Manifest Schema) — the `TransitionSpec` type and `TransitionTypeName` type should be referenced by the Zod manifest schema for validation of `transition_in`/`transition_out` fields. (Note: OBJ-010 is already verified; it may need a minor update or it may already accommodate this type. The implementer should check.)

### File placement:
```
src/transitions/
├── types.ts          # TransitionTypeName, TransitionSpec, ResolvedTransition, TransitionOpacityResult
├── presets.ts        # TransitionPresetDefinition, transitionPresets registry, isTransitionTypeName, getTransitionPreset
├── compute.ts        # computeTransitionOpacity()
├── resolve.ts        # resolveTransition()
└── index.ts          # barrel export
```

## Open Questions

- **OQ-A: Conflict resolution between adjacent scenes' transitions.** If scene A has `transition_out: { type: 'crossfade', duration: 1.0 }` and scene B has `transition_in: { type: 'dip_to_black', duration: 2.0 }`, which takes precedence? This is a scene sequencer concern (OBJ-036), not a transition contract concern. This spec defines the building blocks; OBJ-036 must specify the conflict resolution policy.

- **OQ-B: Should transition duration be capped relative to scene duration?** A 5-second crossfade on a 3-second scene is problematic. This is a validation concern for OBJ-010/OBJ-036, not this module. `resolveTransition()` does not receive scene duration and does not validate against it.

- **OQ-C: Custom transition types.** The seed defines three types. Should the contract support user-defined transitions? Deferred — the current three types cover the vast majority of video transition needs, and extensibility can be added later by expanding `TransitionTypeName` and the presets registry.

---

I believe this spec is complete and ready for challenger review. It covers all three named transition types from the seed vocabulary, defines clear opacity computation semantics for each, separates resolution (seconds→frames) from computation (frame→opacity), and specifies the integration boundaries with OBJ-002 (upstream) and OBJ-036/OBJ-037 (downstream). Please verify and let me know if anything needs revision.

---

## Round 2 — spec_challenger

I've carefully reviewed the OBJ-008 spec against the seed, the OBJ-002 dependency spec, and the downstream consumers (OBJ-036, OBJ-037). Here's my assessment.

---

## What's Sound

- **Overall structure and scope** are correct. The separation between resolution (seconds→frames) and computation (frame→opacity) is clean and well-motivated. This stays within its objective's boundaries without bleeding into OBJ-036/OBJ-037 territory.
- **Vocabulary compliance** is clean — uses seed terms correctly throughout.
- **Design decisions D1, D5, D6, D7, D8** are well-reasoned with clear rationale.
- **The `resolveTransition()` contract** is precise and testable. Direction semantics are unambiguous.
- **Error handling** is thorough for `resolveTransition()`.
- **Constraint compliance** is fine: pure math, deterministic, isomorphic, zero external deps beyond OBJ-002.

---

## Issues

### ISSUE 1 — CRITICAL: Missing computation contract for `computeTransitionOpacity`

OBJ-002 explicitly pinned down its computation contract in numbered steps (compute raw `t`, branch on extrapolation mode, apply easing, map to output). OBJ-008's `computeTransitionOpacity` has no equivalent. The implementer must reconstruct the formula from scattered references across D4, the preset table, the edge cases table, and the ACs.

Specifically, these questions are unanswered:

- **What is `t` for crossfade?** Is it `(frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)` or `(frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame - 1)`? The former means the last frame in the window (frame = overlapEndFrame - 1) has `t = (N-1)/N`, never reaching 1.0. The latter means the last frame has `t = 1.0`. AC-09 implies the former (t = 29/30 = 0.9667), but this is only inferrable — it's not stated.

- **What is `t_phase` for dip_to_black?** For phase 1 with frames `[overlapStartFrame, overlapStartFrame + midpoint)`, is the normalized progress `(frame - overlapStartFrame) / midpoint`? For phase 2 with frames `[overlapStartFrame + midpoint, overlapEndFrame)`, is it `(frame - overlapStartFrame - midpoint) / (durationFrames - midpoint)`?

- **How does `interpolate()` from OBJ-002 get used?** The spec says in its summary that it uses `interpolate()` for all opacity interpolation, but never shows the actual call. Is it `interpolate(frame, [overlapStartFrame, overlapEndFrame], [1, 0], { easing })`? Or does the implementer compute `t` manually and call the easing function directly?

**Proposed fix:** Add a "Computation Contract" section (matching OBJ-002's style) that specifies the exact algorithm for each transition type in numbered steps. Example:

```
Crossfade computation contract:
1. Compute t = (frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)
2. Apply easing: t' = getEasing(easing)(t)
3. outgoingOpacity = 1 - t'
4. incomingOpacity = t'

Dip-to-black computation contract:
1. Compute midpoint = Math.floor(durationFrames / 2)
   where durationFrames = overlapEndFrame - overlapStartFrame
2. Compute relativeFrame = frame - overlapStartFrame
3. If relativeFrame < midpoint (Phase 1):
   a. t = relativeFrame / midpoint
   b. t' = getEasing(easing)(t)
   c. outgoingOpacity = 1 - t'
   d. incomingOpacity = 0
4. If relativeFrame >= midpoint (Phase 2):
   a. t = (relativeFrame - midpoint) / (durationFrames - midpoint)
   b. t' = getEasing(easing)(t)
   c. outgoingOpacity = 0
   d. incomingOpacity = t'
```

This eliminates all guesswork.

---

### ISSUE 2 — CRITICAL: Contradiction in `cut` handling within `computeTransitionOpacity`

The function signature documents two throw conditions:
- `overlapStartFrame >= overlapEndFrame (except for 'cut', where both may be equal)`
- `frame < overlapStartFrame or frame >= overlapEndFrame`

AC-06 tests: `computeTransitionOpacity('cut', 0, 0, 0, 'linear')` and expects a return value.

But with `overlapStartFrame = 0` and `overlapEndFrame = 0`, the second throw condition evaluates: `0 < 0` (false) OR `0 >= 0` (true) → **throws**. This contradicts AC-06 which expects `{ outgoingOpacity: 0, incomingOpacity: 1 }`.

D3 says "computeTransitionOpacity can be called for cut but always returns the fixed result" — but the throws contract doesn't carve out this exception.

**Proposed fix:** One of:

**(a) Preferred:** Explicitly state that for `type === 'cut'`, all parameter validation is skipped and the function immediately returns `{ outgoingOpacity: 0, incomingOpacity: 1 }` regardless of `frame`, `overlapStartFrame`, `overlapEndFrame`, and `easing` values. The throw conditions apply only to `crossfade` and `dip_to_black`. This matches the intent in D3.

**(b) Alternative:** Remove `cut` from `computeTransitionOpacity` entirely. Document that the scene sequencer handles cuts without calling this function. Remove AC-06. This is cleaner but changes the API contract.

---

### ISSUE 3 — MAJOR: `t` never reaches 1.0 within the overlap window — consequences unstated

With `t = (frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)`, the last valid frame (overlapEndFrame - 1) produces `t = (N-1)/N`, not 1.0. This means:

- For crossfade: `incomingOpacity` never reaches 1.0 within the window. At 30 frames, the max is 0.9667.
- For dip_to_black phase 2: `incomingOpacity` never reaches 1.0 within the window.

This is probably correct behavior (the scene sequencer renders at full opacity on the first frame after the window), but it's a non-obvious consequence that should be explicitly documented. An implementer might "fix" this by using `(N-1)` as the denominator, which would break the complementary opacity invariant for crossfade at the first frame (t=0 would still be 0/29 = 0 only if frame=overlapStartFrame, which would give 0/29... no, wait, that's still 0).

Actually let me re-examine: if they used `t = (frame - start) / (end - start - 1)`:
- frame = start: t = 0/(N-1) = 0 ✓
- frame = end-1: t = (N-1)/(N-1) = 1.0 ✓
- But frame = start+1: t = 1/(N-1), not 1/N. Different values throughout.

The choice matters for all intermediate frames. It MUST be pinned down.

**Proposed fix:** In the computation contract (from Issue 1), explicitly state: `t = (frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)`. Add a design note: "The last frame in the overlap window has `t = (N-1)/N`, not 1.0. Full opacity transition completes on the first frame after the overlap window, which is the scene sequencer's responsibility (OBJ-036). This design avoids a 1-frame visual pop and ensures smooth handoff."

---

### ISSUE 4 — MAJOR: AC-08/AC-09/AC-11/AC-12 use undefined variables

These ACs reference `overlapStart` as a free variable:

> `computeTransitionOpacity('crossfade', overlapStart, overlapStart, overlapStart + 30, 'linear')`

For a testable acceptance criterion, either use concrete numbers or explicitly state "for any valid `overlapStart` value (e.g., `overlapStart = 100`)."

**Proposed fix:** Substitute concrete values. E.g., AC-08:
> `computeTransitionOpacity('crossfade', 100, 100, 130, 'linear')` returns `{ outgoingOpacity: 1.0, incomingOpacity: 0.0 }`.

---

### ISSUE 5 — MINOR: AC-15 tolerance of ±0.05 is unnecessarily loose

For a 30-frame dip-to-black with `ease_in_out` easing, phase 2 has 15 frames. Last frame: `t = 14/15 ≈ 0.9333`. Quadratic ease_in_out(0.9333) = `1 - (-2*0.9333+2)²/2 = 1 - (0.1334)²/2 = 1 - 0.0089 = 0.9911`. So `incomingOpacity ≈ 0.991`.

**Proposed fix:** Change AC-15 to: "incomingOpacity is approximately 0.991 (within ±1e-3)" and show the derivation in a parenthetical.

---

### ISSUE 6 — MINOR: `dip_to_black` phase boundary when `midpoint = 0` (1-frame edge case)

The edge case table says for `durationFrames = 1`: "Midpoint = Math.floor(1/2) = 0. Phase 1 has 0 frames (empty). Phase 2 runs frame 0." But in the computation contract (once added per Issue 1), if phase 2 has `t = (relativeFrame - midpoint) / (durationFrames - midpoint) = (0 - 0) / (1 - 0) = 0`, then `incoming = easing(0) = 0`, and `outgoing = 0` (not in phase 1). Both are 0. The only frame is fully black. This is documented in the edge case table but should also be an AC.

**Proposed fix:** Add AC-33: `computeTransitionOpacity('dip_to_black', 100, 100, 101, 'ease_in_out')` returns `{ outgoingOpacity: 0.0, incomingOpacity: 0.0 }` (1-frame dip-to-black: fully black).

---

### ISSUE 7 — MINOR: No guidance on whether `computeTransitionOpacity` uses OBJ-002's `interpolate()` internally or calls easing directly

The summary says it "depends on OBJ-002's `interpolate()` and easing functions." But the computation (once spelled out) might only need `getEasing()` — using `interpolate()` would add unnecessary overhead for what's a simple `t → eased_t` computation.

**Proposed fix:** Clarify in the computation contract whether the implementation should use `interpolate()` (with `[overlapStartFrame, overlapEndFrame]` as input range and `[1, 0]`/`[0, 1]` as output range) or compute `t` manually and apply `getEasing()` directly. Either is valid, but the spec should state which is the expected approach, or explicitly say "either approach is acceptable as long as the numerical results match the computation contract."

---

That's 3 critical/major and 4 minor issues. Issues 1 and 2 are blockers — without the explicit computation contract and the cut contradiction fix, an implementer would be guessing. Issue 3 is major because the `t` formula affects every opacity value.

Please revise.

---

## Round 3 — spec_author

All seven issues are valid. Here's the revised spec with every issue addressed.

---

# Specification: OBJ-008 — Transition Type Contract

## Summary

OBJ-008 defines the named transition preset system for depthkit: the type definitions, duration parameters, opacity computation logic, and overlap semantics that govern how one scene visually hands off to the next. This is a **contract-only** objective — it defines the `TransitionPreset` interface, the three built-in presets (`cut`, `crossfade`, `dip_to_black`), and the `computeTransitionOpacity()` function that downstream consumers (scene sequencer OBJ-036, transition renderer OBJ-037) use to determine per-frame opacity for the outgoing and incoming scenes during a transition window. It depends on OBJ-002's easing functions for all opacity interpolation.

## Interface Contract

### Module: `src/transitions/types.ts`

```typescript
import { EasingName } from '../interpolation/easings';

/**
 * Named transition type identifier.
 * These names appear in manifests under transition_in / transition_out.
 */
export type TransitionTypeName = 'cut' | 'crossfade' | 'dip_to_black';

/**
 * Transition specification as it appears in the manifest (per-scene).
 * This is the authored form — what the LLM writes.
 */
export interface TransitionSpec {
  /** The transition type name. */
  type: TransitionTypeName;

  /**
   * Duration of the transition in seconds.
   * Must be >= 0. A duration of 0 is valid and equivalent to 'cut'.
   * For 'cut', duration is ignored (always instantaneous).
   * For 'crossfade' and 'dip_to_black', must be > 0.
   */
  duration: number;

  /**
   * Easing applied to the opacity interpolation.
   * Defaults to 'linear' for crossfade, 'ease_in_out' for dip_to_black.
   * Ignored for 'cut'.
   */
  easing?: EasingName;
}

/**
 * Resolved transition metadata used internally by the scene sequencer
 * and transition renderer. Contains frame-level timing derived from
 * the manifest's second-based TransitionSpec.
 */
export interface ResolvedTransition {
  /** The transition type. */
  type: TransitionTypeName;

  /** Duration in frames (computed from seconds × fps). Always integer >= 0. */
  durationFrames: number;

  /** Easing function name for opacity interpolation. */
  easing: EasingName;

  /**
   * The absolute start frame of the transition window within the composition.
   * For a transition_out on scene A ending at frame 300 with durationFrames=30,
   * overlapStartFrame = 270.
   */
  overlapStartFrame: number;

  /**
   * The absolute end frame of the transition window (exclusive).
   * overlapEndFrame = overlapStartFrame + durationFrames.
   */
  overlapEndFrame: number;
}

/**
 * The opacity values for both scenes during a single frame of a transition.
 */
export interface TransitionOpacityResult {
  /** Opacity of the outgoing (previous) scene. Range [0, 1]. */
  outgoingOpacity: number;

  /** Opacity of the incoming (next) scene. Range [0, 1]. */
  incomingOpacity: number;
}
```

### Module: `src/transitions/presets.ts`

```typescript
import { TransitionTypeName } from './types';
import { EasingName } from '../interpolation/easings';

/**
 * Definition of a transition preset's default behavior.
 */
export interface TransitionPresetDefinition {
  /** Human-readable description for SKILL.md / documentation. */
  description: string;

  /** Default easing if not overridden in the manifest. */
  defaultEasing: EasingName;

  /**
   * Whether this transition type creates an overlap window
   * where both scenes must render simultaneously.
   * - 'cut': false (no overlap, instantaneous switch)
   * - 'crossfade': true (both scenes render with complementary opacity)
   * - 'dip_to_black': false (scenes never render simultaneously)
   */
  requiresOverlap: boolean;

  /**
   * Whether this transition type requires a duration > 0.
   * 'cut' does not; 'crossfade' and 'dip_to_black' do.
   */
  requiresDuration: boolean;
}

/**
 * Registry of all built-in transition presets.
 */
export const transitionPresets: Record<TransitionTypeName, TransitionPresetDefinition>;

/**
 * Type guard: returns true if the input is a valid TransitionTypeName.
 */
export function isTransitionTypeName(name: string): name is TransitionTypeName;

/**
 * Retrieves a preset definition by name.
 * @throws {Error} if name is not a valid TransitionTypeName.
 *   Error message must include the invalid name and list valid names.
 */
export function getTransitionPreset(name: string): TransitionPresetDefinition;
```

### Preset Definitions

| Name | `defaultEasing` | `requiresOverlap` | `requiresDuration` | Description |
|------|-----------------|--------------------|--------------------|-------------|
| `cut` | `'linear'` | `false` | `false` | Instantaneous switch. Scene A's last frame is immediately followed by Scene B's first frame. No opacity animation. Duration is ignored (treated as 0). |
| `crossfade` | `'linear'` | `true` | `true` | During the overlap window, Scene A's opacity interpolates from 1→0 and Scene B's from 0→1. Both scenes render simultaneously. The opacity values are complementary: `outgoing + incoming = 1.0` at every frame. |
| `dip_to_black` | `'ease_in_out'` | `false` | `true` | Two-phase transition. **Phase 1** (first half of duration): Scene A's opacity interpolates from 1→0; Scene B is not rendered. **Phase 2** (second half of duration): Scene A is not rendered; Scene B's opacity interpolates from 0→1. At the midpoint, both opacities are 0 — the frame is fully black. Only one scene is ever active at a time. |

### Module: `src/transitions/compute.ts`

```typescript
import { TransitionTypeName, TransitionOpacityResult } from './types';
import { EasingName } from '../interpolation/easings';

/**
 * Computes the opacity of the outgoing and incoming scenes for a single frame
 * within a transition window.
 *
 * @param type - The transition type.
 * @param frame - The current absolute frame number within the composition.
 * @param overlapStartFrame - The first frame of the transition window.
 * @param overlapEndFrame - The frame after the last frame of the transition window (exclusive).
 * @param easing - The easing function name to apply to opacity interpolation.
 * @returns The opacity pair for this frame.
 *
 * @throws {Error} if type is not a valid TransitionTypeName.
 * @throws {Error} if easing is not a valid EasingName (for crossfade/dip_to_black only).
 *
 * For type === 'cut':
 *   All parameter validation is skipped. Returns { outgoingOpacity: 0, incomingOpacity: 1 }
 *   immediately regardless of frame, overlapStartFrame, overlapEndFrame, or easing values.
 *
 * For type === 'crossfade' or 'dip_to_black':
 * @throws {Error} if overlapStartFrame >= overlapEndFrame.
 * @throws {Error} if frame < overlapStartFrame or frame >= overlapEndFrame.
 *
 * See Computation Contract section for the exact algorithm.
 */
export function computeTransitionOpacity(
  type: TransitionTypeName,
  frame: number,
  overlapStartFrame: number,
  overlapEndFrame: number,
  easing: EasingName
): TransitionOpacityResult;
```

### Module: `src/transitions/resolve.ts`

```typescript
import { TransitionSpec, ResolvedTransition } from './types';

/**
 * Converts a manifest-level TransitionSpec (seconds-based) into a
 * ResolvedTransition (frame-based) for use by the scene sequencer.
 *
 * @param spec - The transition specification from the manifest.
 * @param fps - Composition frames per second. Must be > 0.
 * @param sceneEndFrame - The absolute frame number where the outgoing scene ends
 *   (for transition_out) or the incoming scene starts (for transition_in).
 *   Used to compute overlapStartFrame and overlapEndFrame.
 * @param direction - Whether this is an outgoing or incoming transition.
 *   'out': the overlap window ends at sceneEndFrame.
 *   'in': the overlap window starts at sceneEndFrame.
 *
 * @returns The resolved transition with frame-based timing.
 *
 * @throws {Error} if spec.type is not a valid TransitionTypeName.
 * @throws {Error} if spec.duration < 0.
 * @throws {Error} if spec.type requires a duration > 0 (crossfade, dip_to_black) and spec.duration <= 0.
 * @throws {Error} if fps <= 0.
 * @throws {Error} if spec.easing is provided and is not a valid EasingName.
 *
 * Duration-to-frames conversion:
 *   durationFrames = Math.round(spec.duration * fps)
 *
 * Overlap window computation:
 *   direction 'out': overlapStartFrame = sceneEndFrame - durationFrames
 *                    overlapEndFrame = sceneEndFrame
 *   direction 'in':  overlapStartFrame = sceneEndFrame
 *                    overlapEndFrame = sceneEndFrame + durationFrames
 */
export function resolveTransition(
  spec: TransitionSpec,
  fps: number,
  sceneEndFrame: number,
  direction: 'in' | 'out'
): ResolvedTransition;
```

### Module: `src/transitions/index.ts` (barrel export)

```typescript
export type {
  TransitionTypeName,
  TransitionSpec,
  ResolvedTransition,
  TransitionOpacityResult,
} from './types';
export type { TransitionPresetDefinition } from './presets';
export {
  transitionPresets,
  isTransitionTypeName,
  getTransitionPreset,
} from './presets';
export { computeTransitionOpacity } from './compute';
export { resolveTransition } from './resolve';
```

## Computation Contract

This section defines the exact algorithm for each transition type. The implementer may use OBJ-002's `interpolate()` or compute `t` manually and call `getEasing()` directly — either approach is acceptable as long as the numerical results are identical to the steps below.

### `cut`

```
1. Return { outgoingOpacity: 0, incomingOpacity: 1 } immediately.
   No parameter validation. No computation.
```

### `crossfade`

```
1. Validate: overlapStartFrame < overlapEndFrame.
   Validate: overlapStartFrame <= frame < overlapEndFrame.
   Validate: easing is a valid EasingName.
2. Let durationFrames = overlapEndFrame - overlapStartFrame.
3. Compute t = (frame - overlapStartFrame) / durationFrames.
   Note: t ranges from 0 (at first frame) to (durationFrames-1)/durationFrames
   (at last frame). t never reaches 1.0 within the window. Full handoff to
   the incoming scene at opacity 1.0 occurs on the first frame AFTER the
   overlap window — that is the scene sequencer's responsibility (OBJ-036).
4. Apply easing: t' = getEasing(easing)(t).
5. outgoingOpacity = 1 - t'.
6. incomingOpacity = t'.
7. Return { outgoingOpacity, incomingOpacity }.
```

**Invariant:** `outgoingOpacity + incomingOpacity === 1.0` at every frame (within floating-point tolerance ±1e-10).

### `dip_to_black`

```
1. Validate: overlapStartFrame < overlapEndFrame.
   Validate: overlapStartFrame <= frame < overlapEndFrame.
   Validate: easing is a valid EasingName.
2. Let durationFrames = overlapEndFrame - overlapStartFrame.
3. Let midpoint = Math.floor(durationFrames / 2).
   midpoint is the frame index (relative to overlapStartFrame) where Phase 2 begins.
   Phase 1: relative frames [0, midpoint)     — outgoing fades out.
   Phase 2: relative frames [midpoint, durationFrames) — incoming fades in.
4. Let relativeFrame = frame - overlapStartFrame.
5. If relativeFrame < midpoint (Phase 1):
   a. If midpoint === 0: impossible (relativeFrame < 0 is already rejected by validation).
   b. t = relativeFrame / midpoint.
   c. t' = getEasing(easing)(t).
   d. outgoingOpacity = 1 - t'.
   e. incomingOpacity = 0.
6. If relativeFrame >= midpoint (Phase 2):
   a. Let phase2Length = durationFrames - midpoint.
   b. t = (relativeFrame - midpoint) / phase2Length.
      Note: same as crossfade, t ranges from 0 to (phase2Length-1)/phase2Length.
      t never reaches 1.0 within phase 2.
   c. t' = getEasing(easing)(t).
   d. outgoingOpacity = 0.
   e. incomingOpacity = t'.
7. Return { outgoingOpacity, incomingOpacity }.
```

**Invariant:** At every frame, `Math.min(outgoingOpacity, incomingOpacity) === 0` — the two scenes are never simultaneously visible.

**Midpoint behavior:** At `relativeFrame === midpoint`, we are in Phase 2 step 6 with `t = 0`, so `t' = getEasing(easing)(0) = 0`, giving `incomingOpacity = 0`. Since `outgoingOpacity = 0` (Phase 2), the midpoint frame is fully black.

**Design note on `t` never reaching 1.0:** The formula `t = (frame - start) / (end - start)` means the last frame in any window has `t = (N-1)/N`. The incoming scene reaches full opacity (1.0) on the first frame *after* the overlap window, when the scene sequencer renders only the incoming scene at full opacity. This design ensures smooth handoff — if `t` reached 1.0 on the last overlap frame, the incoming scene would render at full opacity twice in a row (last overlap frame + first post-overlap frame), which is correct but wastes a frame of the transition effect. Using `t = (frame - start) / (end - start - 1)` would make `t = 1.0` on the last frame but `t = 0` on the first frame would map to `0/(N-2)` for subsequent frames, breaking linearity. The chosen formula is standard and matches video editing conventions.

## Design Decisions

### D1: `crossfade` uses complementary opacity (outgoing + incoming = 1.0); `dip_to_black` uses two-phase non-overlapping opacity

**Decision:** Crossfade renders both scenes simultaneously with `outgoing = 1 - t'` and `incoming = t'`. Dip-to-black is a two-phase transition: in the first half, only the outgoing scene is visible (opacity 1→0); in the second half, only the incoming scene is visible (opacity 0→1). At the midpoint, both opacities are 0 (fully black frame).

**Rationale:** Seed Section 8.8 states: "Scene A's opacity interpolates from 1 to 0; scene B's from 0 to 1." This describes crossfade. Dip-to-black by definition passes through black — meaning there's a moment where neither scene is visible. This is the standard After Effects / Premiere behavior. Having `requiresOverlap: false` for dip-to-black means the scene sequencer (OBJ-036) can optimize by only rendering one scene per frame during a dip-to-black, while crossfade requires rendering both.

**Alternative considered:** Additive blending where both opacities can sum > 1.0 during crossfade (produces a "flash" at the midpoint). Rejected: the flash is usually an unwanted artifact and the seed's description implies complementary blending.

### D2: Transition timing is symmetric for dip_to_black

**Decision:** Dip-to-black splits its duration by `midpoint = Math.floor(durationFrames / 2)`. Phase 1 runs from relative frame 0 to midpoint (exclusive); phase 2 runs from midpoint to durationFrames (exclusive). If `durationFrames` is odd, phase 2 gets the extra frame.

**Rationale:** Symmetric dip-to-black is the standard behavior. The midpoint frame being fully black is the defining characteristic. With `Math.floor`, an odd duration like 31 yields midpoint=15: phase 1 has 15 frames, phase 2 has 16 frames. Phase 2 getting the extra frame is slightly more natural — viewers notice the incoming scene lingering slightly longer than the outgoing fade, which feels like "arriving."

### D3: `cut` bypasses all validation in `computeTransitionOpacity`

**Decision:** When `type === 'cut'`, `computeTransitionOpacity` immediately returns `{ outgoingOpacity: 0, incomingOpacity: 1 }` without validating `frame`, `overlapStartFrame`, `overlapEndFrame`, or `easing`. The throw conditions (frame range, overlap ordering, easing validity) apply only to `crossfade` and `dip_to_black`.

**Rationale:** A cut has `durationFrames = 0`, meaning `overlapStartFrame === overlapEndFrame`. Under normal validation rules, any `frame` value would fail the `frame < overlapStartFrame || frame >= overlapEndFrame` check. Rather than adding a special "allow degenerate range for cut" carve-out to the validation logic, we skip it entirely. In practice, the scene sequencer (OBJ-036) should never call `computeTransitionOpacity` for cuts — it simply switches scenes. This function's cut path exists as a defensive fallback.

### D4: Easing is applied to the normalized progress, not the opacity value

**Decision:** The easing function transforms the normalized time `t ∈ [0,1]` within the transition window before mapping to opacity. See Computation Contract for the exact algorithm per type.

**Rationale:** This is the standard approach — easing controls the *rate* of the transition, not the *shape* of the opacity curve. An `ease_in_out` crossfade starts slow, speeds up in the middle, and slows at the end.

### D5: `resolveTransition()` uses `Math.round()` for duration-to-frames conversion

**Decision:** `durationFrames = Math.round(spec.duration * fps)`. Not `Math.floor()`, not `Math.ceil()`.

**Rationale:** A 1-second transition at 30fps is exactly 30 frames. A 0.5-second transition at 30fps is exactly 15 frames. A 0.7-second transition at 30fps is `Math.round(21)` = 21 frames. Rounding minimizes the perceptual error between the authored duration and the actual duration. Floor would systematically shorten transitions; ceil would systematically lengthen them.

### D6: Transition direction (`in`/`out`) is resolved per-scene, not per-boundary

**Decision:** The manifest specifies `transition_in` and `transition_out` per scene (per seed Section 4.6). The `resolveTransition()` function takes a `direction` parameter to correctly position the overlap window relative to a scene boundary. The scene sequencer (OBJ-036) is responsible for pairing adjacent scenes' `transition_out` / `transition_in` and resolving potential conflicts.

**Rationale:** The seed's manifest schema (Section 4.6) shows `transition_in` and `transition_out` as per-scene properties. This objective defines the contract for a single transition spec; the sequencer handles the multi-scene orchestration.

### D7: Separation of `computeTransitionOpacity` from `resolveTransition`

**Decision:** Resolution (seconds→frames, positioning in the composition timeline) is separated from computation (frame→opacity pair). `resolveTransition()` produces a `ResolvedTransition` with frame-based timing. `computeTransitionOpacity()` takes frame-level parameters and returns opacity values.

**Rationale:** The scene sequencer (OBJ-036) needs `resolveTransition()` during manifest processing to build the composition timeline. The transition renderer (OBJ-037) needs `computeTransitionOpacity()` on a per-frame basis during rendering. Different consumers, different call patterns, clean separation.

### D8: This module is pure and isomorphic (same as OBJ-002)

**Decision:** All functions are pure, stateless, and use only OBJ-002 imports plus basic math. No Node.js or browser APIs. Can run in both the orchestrator (Node.js) and the headless browser page.

**Rationale:** The scene sequencer runs in Node.js; the transition renderer may need opacity values in the browser context for Three.js material animation. Same sharing strategy as OBJ-002 (D1).

### D9: Implementation may use `interpolate()` or `getEasing()` directly

**Decision:** The Computation Contract defines the algorithm in terms of `getEasing(easing)(t)`. The implementer may equivalently use OBJ-002's `interpolate()` (e.g., `interpolate(frame, [overlapStartFrame, overlapEndFrame], [1, 0], { easing })`) as long as numerical results match the Computation Contract exactly. Either approach is acceptable.

**Rationale:** Using `interpolate()` is more concise for simple cases like crossfade, but dip-to-black's two-phase structure may be clearer with manual `t` computation + `getEasing()`. The spec should not over-constrain the implementation path.

## Acceptance Criteria

### Preset Registry ACs

- [ ] **AC-01:** `isTransitionTypeName('cut')`, `isTransitionTypeName('crossfade')`, and `isTransitionTypeName('dip_to_black')` all return `true`.
- [ ] **AC-02:** `isTransitionTypeName('wipe')` returns `false`.
- [ ] **AC-03:** `getTransitionPreset('crossfade')` returns a `TransitionPresetDefinition` with `requiresOverlap: true` and `defaultEasing: 'linear'`.
- [ ] **AC-04:** `getTransitionPreset('invalid')` throws an `Error` whose message includes `'invalid'` and lists the three valid transition type names.
- [ ] **AC-05:** `transitionPresets` contains exactly three entries: `cut`, `crossfade`, `dip_to_black`.

### Cut ACs

- [ ] **AC-06:** `computeTransitionOpacity('cut', 0, 0, 0, 'linear')` returns `{ outgoingOpacity: 0, incomingOpacity: 1 }`. (No throw — cut bypasses validation per D3.)
- [ ] **AC-07:** `resolveTransition({ type: 'cut', duration: 5.0 }, 30, 100, 'out')` returns a `ResolvedTransition` with `durationFrames: 0` (duration ignored for cut).

### Crossfade ACs

- [ ] **AC-08:** `computeTransitionOpacity('crossfade', 100, 100, 130, 'linear')` returns `{ outgoingOpacity: 1.0, incomingOpacity: 0.0 }`. (First frame: `t = 0/30 = 0`.)
- [ ] **AC-09:** `computeTransitionOpacity('crossfade', 129, 100, 130, 'linear')` returns `{ outgoingOpacity: ≈0.0333, incomingOpacity: ≈0.9667 }` within ±1e-10. (Last frame: `t = 29/30`.)
- [ ] **AC-10:** For a crossfade from frame 100 to 130 with `linear` easing, at every frame `f` in `[100, 130)`, `outgoingOpacity + incomingOpacity === 1.0` within ±1e-10.
- [ ] **AC-11:** `computeTransitionOpacity('crossfade', 115, 100, 130, 'linear')` returns `{ outgoingOpacity: 0.5, incomingOpacity: 0.5 }` within ±1e-10. (Midpoint: `t = 15/30 = 0.5`.)
- [ ] **AC-12:** `computeTransitionOpacity('crossfade', 115, 100, 130, 'ease_in_out')` returns opacity values that differ from the linear case (verifying easing is applied). Specifically, `ease_in_out(0.5) = 0.5`, so this particular midpoint is the same — use frame 108 instead: `linear t = 8/30 ≈ 0.2667` giving `incomingOpacity ≈ 0.2667`, vs `ease_in_out(0.2667) = 2*(0.2667)^2 ≈ 0.1422` giving `incomingOpacity ≈ 0.1422`. Verify `incomingOpacity ≈ 0.1422` within ±1e-3.

### Dip-to-Black ACs

- [ ] **AC-13:** `computeTransitionOpacity('dip_to_black', 200, 200, 230, 'ease_in_out')` returns `{ outgoingOpacity: 1.0, incomingOpacity: 0.0 }`. (First frame, phase 1: `t = 0/15 = 0`, `ease_in_out(0) = 0`, `outgoing = 1 - 0 = 1`.)
- [ ] **AC-14:** `computeTransitionOpacity('dip_to_black', 215, 200, 230, 'ease_in_out')` returns `{ outgoingOpacity: 0.0, incomingOpacity: 0.0 }`. (Midpoint frame: `midpoint = Math.floor(30/2) = 15`, `relativeFrame = 15 >= midpoint`, phase 2 `t = 0/15 = 0`, `incoming = 0`.)
- [ ] **AC-15:** `computeTransitionOpacity('dip_to_black', 229, 200, 230, 'ease_in_out')` returns `{ outgoingOpacity: 0.0, incomingOpacity: ≈0.9911 }` within ±1e-3. (Last frame, phase 2: `t = 14/15 ≈ 0.9333`, `ease_in_out(0.9333) = 1 - (-2*0.9333+2)^2/2 = 1 - (0.1334)^2/2 ≈ 0.9911`.)
- [ ] **AC-16:** For a dip-to-black from frame 200 to 230, at every frame `f` in `[200, 230)`, `Math.min(outgoingOpacity, incomingOpacity) === 0` (scenes are never both visible simultaneously).
- [ ] **AC-17:** For a dip-to-black with odd `durationFrames` = 31 (frames 200-231): `midpoint = Math.floor(31/2) = 15`. At frame 215 (`relativeFrame = 15 = midpoint`): phase 2 with `t = 0`, both opacities are 0. Phase 1 has 15 frames, phase 2 has 16 frames.

### Resolve ACs

- [ ] **AC-18:** `resolveTransition({ type: 'crossfade', duration: 1.0 }, 30, 300, 'out')` returns `{ type: 'crossfade', durationFrames: 30, overlapStartFrame: 270, overlapEndFrame: 300, easing: 'linear' }`.
- [ ] **AC-19:** `resolveTransition({ type: 'crossfade', duration: 1.0 }, 30, 300, 'in')` returns `{ type: 'crossfade', durationFrames: 30, overlapStartFrame: 300, overlapEndFrame: 330, easing: 'linear' }`.
- [ ] **AC-20:** `resolveTransition({ type: 'dip_to_black', duration: 0.5 }, 30, 100, 'out')` returns `{ type: 'dip_to_black', durationFrames: 15, overlapStartFrame: 85, overlapEndFrame: 100, easing: 'ease_in_out' }` (default easing applied).
- [ ] **AC-21:** `resolveTransition({ type: 'crossfade', duration: 1.0, easing: 'ease_out' }, 30, 300, 'out')` returns `easing: 'ease_out'` (manifest easing overrides default).
- [ ] **AC-22:** `resolveTransition({ type: 'crossfade', duration: 0.7 }, 30, 300, 'out')` returns `durationFrames: 21` (`Math.round(0.7 * 30) = 21`).

### Error Handling ACs

- [ ] **AC-23:** `resolveTransition({ type: 'crossfade', duration: -1 }, 30, 100, 'out')` throws an `Error` mentioning negative duration.
- [ ] **AC-24:** `resolveTransition({ type: 'crossfade', duration: 0 }, 30, 100, 'out')` throws an `Error` mentioning that crossfade requires duration > 0.
- [ ] **AC-25:** `resolveTransition({ type: 'dip_to_black', duration: 0 }, 30, 100, 'out')` throws an `Error` mentioning that dip_to_black requires duration > 0.
- [ ] **AC-26:** `resolveTransition({ type: 'wipe' as any, duration: 1 }, 30, 100, 'out')` throws an `Error` listing valid transition types.
- [ ] **AC-27:** `computeTransitionOpacity('crossfade', 50, 60, 90, 'linear')` throws (frame < overlapStartFrame).
- [ ] **AC-28:** `computeTransitionOpacity('crossfade', 90, 60, 90, 'linear')` throws (frame >= overlapEndFrame).
- [ ] **AC-29:** `resolveTransition({ type: 'crossfade', duration: 1, easing: 'bounce' as any }, 30, 100, 'out')` throws an `Error` mentioning invalid easing name.

### Degenerate Edge Case ACs

- [ ] **AC-30:** `computeTransitionOpacity('dip_to_black', 100, 100, 101, 'ease_in_out')` returns `{ outgoingOpacity: 0.0, incomingOpacity: 0.0 }`. (1-frame dip-to-black: `midpoint = Math.floor(1/2) = 0`, phase 1 has 0 frames, phase 2 has 1 frame. `relativeFrame = 0 >= midpoint = 0` → phase 2. `t = 0/1 = 0`, `incoming = 0`. Fully black.)

### General ACs

- [ ] **AC-31:** The module has no runtime dependencies outside `src/interpolation/` (OBJ-002).
- [ ] **AC-32:** The module uses no Node.js-specific or browser-specific APIs (isomorphic, per D8).
- [ ] **AC-33:** All functions are pure — no mutable state, no side effects. Calling the same function with the same arguments always returns the same result.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `cut` with non-zero duration in manifest | Duration is silently ignored; `durationFrames` resolved to 0. No error. |
| `cut` passed to `computeTransitionOpacity` with any arguments | Returns `{ outgoingOpacity: 0, incomingOpacity: 1 }`. No validation, no throw. |
| `crossfade` with `duration: 0` | **Throws**: crossfade requires `duration > 0`. |
| `dip_to_black` with `duration: 0` | **Throws**: dip_to_black requires `duration > 0`. |
| Negative duration | **Throws**: duration must be >= 0. |
| Unknown transition type | **Throws** with message listing valid types. |
| Unknown easing name in TransitionSpec | **Throws** with message listing valid easing names (delegates to OBJ-002's `getEasing()`). |
| `fps <= 0` in `resolveTransition` | **Throws**: fps must be > 0. |
| Very short crossfade (`durationFrames` = 1) | Valid. Single frame: `t = 0/1 = 0`, so `outgoing = 1.0`, `incoming = 0.0`. Effectively a cut. The SKILL.md should recommend minimum 0.25s for perceptible transitions. |
| Very short dip-to-black (`durationFrames` = 2) | Valid. `midpoint = 1`. Phase 1: frame 0 (`t = 0/1 = 0`, outgoing=1). Phase 2: frame 1 (`t = 0/1 = 0`, incoming=0). Both frames have either outgoing=1 or fully black. Abrupt but valid. |
| `dip_to_black` with `durationFrames` = 1 | Valid but degenerate. `midpoint = 0`. Phase 1 is empty. Phase 2: frame 0 (`t = 0/1 = 0`, incoming=0, outgoing=0). The only frame is fully black. See AC-30. |
| `computeTransitionOpacity` called for frame outside the overlap window | **Throws**: frame must be within `[overlapStartFrame, overlapEndFrame)`. The scene sequencer should never call this for frames outside the window. |
| `overlapStartFrame` is negative (scene starts before composition) | No special handling — frame math works with any integers. The scene sequencer (OBJ-036) is responsible for ensuring overlap windows don't extend before frame 0. |
| `dip_to_black` midpoint with even vs odd `durationFrames` | `midpoint = Math.floor(durationFrames / 2)`. Even (30): phase 1 has 15 frames, phase 2 has 15 frames. Odd (31): phase 1 has 15 frames, phase 2 has 16 frames. |

## Test Strategy

### Unit Tests

**Preset registry:**
- All three presets exist with correct metadata fields.
- `isTransitionTypeName` positive/negative cases.
- `getTransitionPreset` valid/invalid lookups.

**`computeTransitionOpacity` — crossfade:**
- First frame, last frame, midpoint, quarter-points with linear easing (concrete values per ACs).
- Complementary opacity invariant (`out + in = 1.0`) checked across all frames of a 30-frame crossfade.
- Same sweep with `ease_in_out` easing — verify values differ from linear at non-midpoint frames.
- 1-frame crossfade edge case.

**`computeTransitionOpacity` — dip_to_black:**
- First frame (outgoing = 1, incoming = 0), midpoint (both 0), last frame (outgoing = 0, incoming ≈ 0.991).
- Non-overlap invariant: at every frame, `min(outgoingOpacity, incomingOpacity) === 0`.
- Even and odd `durationFrames` midpoint behavior.
- 1-frame and 2-frame edge cases.

**`computeTransitionOpacity` — cut:**
- Returns `{ outgoing: 0, incoming: 1 }` regardless of frame/range/easing arguments.

**`resolveTransition`:**
- All three types with standard values.
- Direction `in` vs `out` positioning.
- Duration rounding (`Math.round`).
- Default easing assignment per type.
- Manifest easing override.
- All error cases (negative duration, zero duration on crossfade/dip, bad type, bad easing, bad fps).

**Determinism:**
- All functions called 1000x with identical inputs produce identical results.

### Relevant Testable Claims
- **TC-10** (cross-scene transitions mask compositing seams) — this objective provides the opacity computation contract; TC-10 validation requires the renderer (OBJ-037) and visual review.
- **TC-06** (deterministic output) — pure functions guarantee deterministic opacity values.

## Integration Points

### Depends on:
- **OBJ-002** (`src/interpolation/`) — `getEasing()` / `isEasingName()` for easing function lookup and validation, `EasingName` type. Optionally `interpolate()` if the implementer prefers it over manual `t` computation (see D9).

### Consumed by:
- **OBJ-036** (Scene Sequencer) — uses `resolveTransition()` to build the composition timeline, determining which frames require overlap rendering. Uses `TransitionSpec` and `ResolvedTransition` types for its internal data model.
- **OBJ-037** (Transition Renderer) — uses `computeTransitionOpacity()` per-frame during rendering to set Three.js material opacity on outgoing/incoming scenes.
- **OBJ-010** (Manifest Schema) — the `TransitionSpec` type and `TransitionTypeName` type should be referenced by the Zod manifest schema for validation of `transition_in`/`transition_out` fields. (Note: OBJ-010 is already verified; it may already define compatible types. The implementer should check for alignment.)

### File placement:
```
src/transitions/
├── types.ts          # TransitionTypeName, TransitionSpec, ResolvedTransition, TransitionOpacityResult
├── presets.ts        # TransitionPresetDefinition, transitionPresets registry, isTransitionTypeName, getTransitionPreset
├── compute.ts        # computeTransitionOpacity()
├── resolve.ts        # resolveTransition()
└── index.ts          # barrel export
```

## Open Questions

- **OQ-A: Conflict resolution between adjacent scenes' transitions.** If scene A has `transition_out: { type: 'crossfade', duration: 1.0 }` and scene B has `transition_in: { type: 'dip_to_black', duration: 2.0 }`, which takes precedence? This is a scene sequencer concern (OBJ-036), not a transition contract concern. This spec defines the building blocks; OBJ-036 must specify the conflict resolution policy.

- **OQ-B: Should transition duration be capped relative to scene duration?** A 5-second crossfade on a 3-second scene is problematic. This is a validation concern for OBJ-010/OBJ-036, not this module. `resolveTransition()` does not receive scene duration and does not validate against it.

- **OQ-C: Custom transition types.** The seed defines three types. Should the contract support user-defined transitions? Deferred — the current three types cover the vast majority of video transition needs, and extensibility can be added later by expanding `TransitionTypeName` and the presets registry.

---

I believe this revision addresses all seven issues raised:

1. **Issue 1 (computation contract):** Added the full "Computation Contract" section with numbered steps for all three types.
2. **Issue 2 (cut contradiction):** Rewrote D3 and the `computeTransitionOpacity` JSDoc to explicitly state cut bypasses all validation. Updated AC-06's comment to reference D3.
3. **Issue 3 (t never reaches 1.0):** Documented in the computation contract (crossfade step 3, dip_to_black step 6b) with a design note explaining why.
4. **Issue 4 (undefined variables in ACs):** All ACs now use concrete frame numbers (100/130 for crossfade, 200/230 for dip-to-black).
5. **Issue 5 (AC-15 tolerance):** Tightened to ±1e-3 with full derivation showing ≈0.9911.
6. **Issue 6 (1-frame dip-to-black AC):** Added AC-30 with exact values and derivation.
7. **Issue 7 (interpolate vs getEasing):** Added D9 explicitly stating either approach is acceptable.

Please verify and approve if satisfied, or raise any remaining concerns.

---

## Round 4 — spec_challenger

## Verification of Round 3 Revisions

I've verified each of the seven issues against the revised spec:

1. **Issue 1 (Computation Contract):** ✅ Present. Numbered steps for all three types. Crossfade steps 1-7, dip_to_black steps 1-7, cut step 1. Unambiguous.

2. **Issue 2 (Cut contradiction):** ✅ Fixed. JSDoc now explicitly states cut bypasses all validation. D3 rewritten. AC-06 works.

3. **Issue 3 (t never reaches 1.0):** ✅ Documented in computation contract (crossfade step 3 note, dip_to_black step 6b note) plus the design note paragraph.

4. **Issue 4 (Undefined variables in ACs):** ✅ All ACs use concrete frame numbers (100/130, 200/230).

5. **Issue 5 (AC-15 tolerance):** ✅ Tightened to ±1e-3 with correct derivation (verified: ease_in_out(14/15) ≈ 0.9911).

6. **Issue 6 (1-frame dip-to-black):** ✅ AC-30 added with full derivation.

7. **Issue 7 (interpolate vs getEasing):** ✅ D9 added.

I also verified:
- AC-12's revision correctly catches the ease_in_out(0.5)=0.5 problem and switches to frame 108. Math checks out: 2*(8/30)² ≈ 0.1422. ✅
- D2's odd-duration claim: Math.floor(31/2)=15, phase 1 has 15 frames, phase 2 has 16. ✅
- Computation contract step 5a's "impossible" claim for midpoint=0 is correct (relativeFrame can't be < 0). ✅

### One Minor Remaining Note

The `resolveTransition` JSDoc says:

```
Duration-to-frames conversion:
  durationFrames = Math.round(spec.duration * fps)
```

This formula doesn't carve out the `cut` exception (where `durationFrames` is always 0 regardless of `spec.duration`). The intent is unambiguous from D3, AC-07, and the edge case table, but the JSDoc formula technically contradicts them. 

**Fix:** Add one line to the JSDoc:

```
Duration-to-frames conversion:
  For 'cut': durationFrames = 0 (duration ignored).
  For 'crossfade' and 'dip_to_black': durationFrames = Math.round(spec.duration * fps)
```

I'll incorporate this into the final version.

---

Everything else is sound. The spec is precise, testable, stays within scope, uses seed vocabulary correctly, integrates cleanly with OBJ-002, and provides clear contracts for OBJ-036/OBJ-037. 

CONCLUSION: The spec is approved with the one minor JSDoc fix incorporated. Writing to disk now.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me first check the existing meta.json and see the current directory structure.
[Tool: Read]
  Input: {
  "file_path": "/home/user/repos/depthkit/nodes/OBJ-008/meta.json"
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
  "command": "ls /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-008/",
  "description": "List OBJ-008 node directory"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-008/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-008",
     3→  "description": "Transition type contract -- named transition preset definitions (cut, crossfade, dip_to_black), duration parameters, and overlap semantics per Section 8.8. Specifies how transition duration creates an overlap window where both scenes render simultaneously with animated opacity. Defines the transition interface that the scene sequencer (OBJ-036) and transition renderer (OBJ-037) implement.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-002"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Depends on easing utilities (OBJ-002) for opacity interpolation."
    12→}
    13→
[Tool Result] meta.json
Now let me write the final spec to `output.md` and update `meta.json`:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-008/output.md",
  "content": "# Specification: OBJ-008 \u2014 Transition Type Contract\n\n## Summary\n\nOBJ-008 defines the named transition preset system for depthkit: the type definitions, duration parameters, opacity computation logic, and overlap semantics that govern how one scene visually hands off to the next. This is a **contract-only** objective \u2014 it defines the `TransitionPreset` interface, the three built-in presets (`cut`, `crossfade`, `dip_to_black`), and the `computeTransitionOpacity()` function that downstream consumers (scene sequencer OBJ-036, transition renderer OBJ-037) use to determine per-frame opacity for the outgoing and incoming scenes during a transition window. It depends on OBJ-002's easing functions for all opacity interpolation.\n\n## Interface Contract\n\n### Module: `src/transitions/types.ts`\n\n```typescript\nimport { EasingName } from '../interpolation/easings';\n\n/**\n * Named transition type identifier.\n * These names appear in manifests under transition_in / transition_out.\n */\nexport type TransitionTypeName = 'cut' | 'crossfade' | 'dip_to_black';\n\n/**\n * Transition specification as it appears in the manifest (per-scene).\n * This is the authored form \u2014 what the LLM writes.\n */\nexport interface TransitionSpec {\n  /** The transition type name. */\n  type: TransitionTypeName;\n\n  /**\n   * Duration of the transition in seconds.\n   * Must be >= 0. A duration of 0 is valid and equivalent to 'cut'.\n   * For 'cut', duration is ignored (always instantaneous).\n   * For 'crossfade' and 'dip_to_black', must be > 0.\n   */\n  duration: number;\n\n  /**\n   * Easing applied to the opacity interpolation.\n   * Defaults to 'linear' for crossfade, 'ease_in_out' for dip_to_black.\n   * Ignored for 'cut'.\n   */\n  easing?: EasingName;\n}\n\n/**\n * Resolved transition metadata used internally by the scene sequencer\n * and tran
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-008/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-008/meta.json",
  "content": "{\n  \"id\": \"OBJ-008\",\n  \"description\": \"Transition type contract -- named transition preset definitions (cut, crossfade, dip_to_black), duration parameters, and overlap semantics per Section 8.8. Specifies how transition duration creates an overlap window where both scenes render simultaneously with animated opacity. Defines the transition interface that the scene sequencer (OBJ-036) and transition renderer (OBJ-037) implement.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-002\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 1 contract. Depends on easing utilities (OBJ-002) for opacity interpolation. Spec defines three transition presets (cut, crossfade, dip_to_black), explicit computation contracts for opacity per frame, resolveTransition for seconds-to-frames conversion, and computeTransitionOpacity for per-frame opacity pairs. Pure/isomorphic module under src/transitions/.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-008/meta.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-008/output.md nodes/OBJ-008/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-008): transition type contract \u2014 cut, crossfade, dip_to_black\n\nDefines the named transition preset system: TransitionSpec/ResolvedTransition\ntypes, computeTransitionOpacity() with explicit computation contracts for all\nthree transition types, resolveTransition() for seconds-to-frames conversion,\nand preset registry. Pure isomorphic module under src/transitions/ consuming\nOBJ-002 easing utilities. 33 acceptance criteria covering opacity invariants,\nphase boundary behavior, edge cases, and error handling.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-008 spec and updated meta.json"
}
[Tool Result] [master 7a64c90] spec(OBJ-008): transition type contract — cut, crossfade, dip_to_black
 2 files changed, 516 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-008/output.md
The specification for OBJ-008 has been written to disk and committed. Here's a summary of what was agreed:

**OBJ-008 — Transition Type Contract** defines three named transition presets (`cut`, `crossfade`, `dip_to_black`) with:

- **Explicit computation contracts** — numbered algorithmic steps for each type, eliminating all implementer guesswork
- **`crossfade`**: complementary opacity (`outgoing + incoming = 1.0`), both scenes render simultaneously
- **`dip_to_black`**: two-phase non-overlapping opacity (only one scene visible at any time), midpoint frame is fully black
- **`cut`**: bypasses all validation, returns fixed result immediately
- **`resolveTransition()`** for seconds-to-frames conversion with `Math.round()`, direction-aware overlap window positioning, and cut-specific `durationFrames = 0` override
- **`computeTransitionOpacity()`** for per-frame opacity pairs with the `t = (frame - start) / (end - start)` formula (t never reaches 1.0 — documented and justified)
- **33 acceptance criteria** with concrete frame numbers, derived expected values, and explicit tolerances
- **9 design decisions** covering complementary vs additive blending, symmetric timing, cut bypass semantics, easing application, rounding, direction resolution, separation of concerns, isomorphic purity, and implementation flexibility (interpolate vs getEasing)
- **Pure isomorphic module** under `src/transitions/` with zero dependencies beyond OBJ-002
