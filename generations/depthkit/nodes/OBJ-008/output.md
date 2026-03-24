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

  /** Duration in frames (computed from seconds x fps). Always integer >= 0. */
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
| `crossfade` | `'linear'` | `true` | `true` | During the overlap window, Scene A's opacity interpolates from 1 to 0 and Scene B's from 0 to 1. Both scenes render simultaneously. The opacity values are complementary: `outgoing + incoming = 1.0` at every frame. |
| `dip_to_black` | `'ease_in_out'` | `false` | `true` | Two-phase transition. **Phase 1** (first half of duration): Scene A's opacity interpolates from 1 to 0; Scene B is not rendered. **Phase 2** (second half of duration): Scene A is not rendered; Scene B's opacity interpolates from 0 to 1. At the midpoint, both opacities are 0 — the frame is fully black. Only one scene is ever active at a time. |

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
 *   For 'cut': durationFrames = 0 (duration ignored).
 *   For 'crossfade' and 'dip_to_black': durationFrames = Math.round(spec.duration * fps)
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

**Invariant:** `outgoingOpacity + incomingOpacity === 1.0` at every frame (within floating-point tolerance +/-1e-10).

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

**Design note on `t` never reaching 1.0:** The formula `t = (frame - start) / (end - start)` means the last frame in any window has `t = (N-1)/N`. The incoming scene reaches full opacity (1.0) on the first frame *after* the overlap window, when the scene sequencer renders only the incoming scene at full opacity. This design ensures smooth handoff — if `t` reached 1.0 on the last overlap frame, the incoming scene would render at full opacity twice in a row (last overlap frame + first post-overlap frame), which is correct but wastes a frame of the transition effect. Using `t = (frame - start) / (end - start - 1)` would make `t = 1.0` on the last frame but break linearity for intermediate frames. The chosen formula is standard and matches video editing conventions.

## Design Decisions

### D1: `crossfade` uses complementary opacity (outgoing + incoming = 1.0); `dip_to_black` uses two-phase non-overlapping opacity

**Decision:** Crossfade renders both scenes simultaneously with `outgoing = 1 - t'` and `incoming = t'`. Dip-to-black is a two-phase transition: in the first half, only the outgoing scene is visible (opacity 1 to 0); in the second half, only the incoming scene is visible (opacity 0 to 1). At the midpoint, both opacities are 0 (fully black frame).

**Rationale:** Seed Section 8.8 states: "Scene A's opacity interpolates from 1 to 0; scene B's from 0 to 1." This describes crossfade. Dip-to-black by definition passes through black — meaning there's a moment where neither scene is visible. This is the standard After Effects / Premiere behavior. Having `requiresOverlap: false` for dip-to-black means the scene sequencer (OBJ-036) can optimize by only rendering one scene per frame during a dip-to-black, while crossfade requires rendering both.

**Alternative considered:** Additive blending where both opacities can sum > 1.0 during crossfade (produces a "flash" at the midpoint). Rejected: the flash is usually an unwanted artifact and the seed's description implies complementary blending.

### D2: Transition timing is symmetric for dip_to_black

**Decision:** Dip-to-black splits its duration by `midpoint = Math.floor(durationFrames / 2)`. Phase 1 runs from relative frame 0 to midpoint (exclusive); phase 2 runs from midpoint to durationFrames (exclusive). If `durationFrames` is odd, phase 2 gets the extra frame.

**Rationale:** Symmetric dip-to-black is the standard behavior. The midpoint frame being fully black is the defining characteristic. With `Math.floor`, an odd duration like 31 yields midpoint=15: phase 1 has 15 frames, phase 2 has 16 frames. Phase 2 getting the extra frame is slightly more natural — viewers notice the incoming scene lingering slightly longer than the outgoing fade, which feels like "arriving."

### D3: `cut` bypasses all validation in `computeTransitionOpacity`

**Decision:** When `type === 'cut'`, `computeTransitionOpacity` immediately returns `{ outgoingOpacity: 0, incomingOpacity: 1 }` without validating `frame`, `overlapStartFrame`, `overlapEndFrame`, or `easing`. The throw conditions (frame range, overlap ordering, easing validity) apply only to `crossfade` and `dip_to_black`.

**Rationale:** A cut has `durationFrames = 0`, meaning `overlapStartFrame === overlapEndFrame`. Under normal validation rules, any `frame` value would fail the `frame < overlapStartFrame || frame >= overlapEndFrame` check. Rather than adding a special "allow degenerate range for cut" carve-out to the validation logic, we skip it entirely. In practice, the scene sequencer (OBJ-036) should never call `computeTransitionOpacity` for cuts — it simply switches scenes. This function's cut path exists as a defensive fallback.

### D4: Easing is applied to the normalized progress, not the opacity value

**Decision:** The easing function transforms the normalized time `t` within the transition window before mapping to opacity. See Computation Contract for the exact algorithm per type.

**Rationale:** This is the standard approach — easing controls the *rate* of the transition, not the *shape* of the opacity curve. An `ease_in_out` crossfade starts slow, speeds up in the middle, and slows at the end.

### D5: `resolveTransition()` uses `Math.round()` for duration-to-frames conversion

**Decision:** `durationFrames = Math.round(spec.duration * fps)`. Not `Math.floor()`, not `Math.ceil()`.

**Rationale:** A 1-second transition at 30fps is exactly 30 frames. A 0.5-second transition at 30fps is exactly 15 frames. A 0.7-second transition at 30fps is `Math.round(21)` = 21 frames. Rounding minimizes the perceptual error between the authored duration and the actual duration. Floor would systematically shorten transitions; ceil would systematically lengthen them.

### D6: Transition direction (`in`/`out`) is resolved per-scene, not per-boundary

**Decision:** The manifest specifies `transition_in` and `transition_out` per scene (per seed Section 4.6). The `resolveTransition()` function takes a `direction` parameter to correctly position the overlap window relative to a scene boundary. The scene sequencer (OBJ-036) is responsible for pairing adjacent scenes' `transition_out` / `transition_in` and resolving potential conflicts.

**Rationale:** The seed's manifest schema (Section 4.6) shows `transition_in` and `transition_out` as per-scene properties. This objective defines the contract for a single transition spec; the sequencer handles the multi-scene orchestration.

### D7: Separation of `computeTransitionOpacity` from `resolveTransition`

**Decision:** Resolution (seconds to frames, positioning in the composition timeline) is separated from computation (frame to opacity pair). `resolveTransition()` produces a `ResolvedTransition` with frame-based timing. `computeTransitionOpacity()` takes frame-level parameters and returns opacity values.

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
- [ ] **AC-09:** `computeTransitionOpacity('crossfade', 129, 100, 130, 'linear')` returns `{ outgoingOpacity: ~0.0333, incomingOpacity: ~0.9667 }` within +/-1e-10. (Last frame: `t = 29/30`.)
- [ ] **AC-10:** For a crossfade from frame 100 to 130 with `linear` easing, at every frame `f` in `[100, 130)`, `outgoingOpacity + incomingOpacity === 1.0` within +/-1e-10.
- [ ] **AC-11:** `computeTransitionOpacity('crossfade', 115, 100, 130, 'linear')` returns `{ outgoingOpacity: 0.5, incomingOpacity: 0.5 }` within +/-1e-10. (Midpoint: `t = 15/30 = 0.5`.)
- [ ] **AC-12:** `computeTransitionOpacity('crossfade', 108, 100, 130, 'ease_in_out')` returns `incomingOpacity ~= 0.1422` within +/-1e-3 (verifying easing is applied). Derivation: `t = 8/30 ~= 0.2667`, `ease_in_out(0.2667) = 2*(0.2667)^2 ~= 0.1422`.

### Dip-to-Black ACs

- [ ] **AC-13:** `computeTransitionOpacity('dip_to_black', 200, 200, 230, 'ease_in_out')` returns `{ outgoingOpacity: 1.0, incomingOpacity: 0.0 }`. (First frame, phase 1: `t = 0/15 = 0`, `ease_in_out(0) = 0`, `outgoing = 1 - 0 = 1`.)
- [ ] **AC-14:** `computeTransitionOpacity('dip_to_black', 215, 200, 230, 'ease_in_out')` returns `{ outgoingOpacity: 0.0, incomingOpacity: 0.0 }`. (Midpoint frame: `midpoint = Math.floor(30/2) = 15`, `relativeFrame = 15 >= midpoint`, phase 2 `t = 0/15 = 0`, `incoming = 0`.)
- [ ] **AC-15:** `computeTransitionOpacity('dip_to_black', 229, 200, 230, 'ease_in_out')` returns `{ outgoingOpacity: 0.0, incomingOpacity: ~0.9911 }` within +/-1e-3. (Last frame, phase 2: `t = 14/15 ~= 0.9333`, `ease_in_out(0.9333) = 1 - (-2*0.9333+2)^2/2 = 1 - (0.1334)^2/2 ~= 0.9911`.)
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

- [ ] **AC-30:** `computeTransitionOpacity('dip_to_black', 100, 100, 101, 'ease_in_out')` returns `{ outgoingOpacity: 0.0, incomingOpacity: 0.0 }`. (1-frame dip-to-black: `midpoint = Math.floor(1/2) = 0`, phase 1 has 0 frames, phase 2 has 1 frame. `relativeFrame = 0 >= midpoint = 0` so phase 2. `t = 0/1 = 0`, `incoming = 0`. Fully black.)

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
- First frame (outgoing = 1, incoming = 0), midpoint (both 0), last frame (outgoing = 0, incoming ~= 0.991).
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
