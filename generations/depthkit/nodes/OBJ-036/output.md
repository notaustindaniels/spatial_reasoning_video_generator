# Specification: OBJ-036 — Scene Sequencer

## Summary

OBJ-036 delivers the `SceneSequencer` class (`src/scenes/scene-sequencer.ts`) — the component that converts a manifest's ordered list of scenes into per-frame rendering plans. It takes scene timing data and transition specifications, builds an internal timeline with resolved transition boundaries, and provides a `planFrame(frame)` method that returns the complete rendering plan for any frame: which scenes are active, their per-scene normalized time, their opacity, and which scenes must be available on the page. This extracts the inline scene iteration logic from the Orchestrator (OBJ-035 D3) into a dedicated, independently testable module. It resolves the transition boundary conflict question posed by OBJ-008 OQ-A by defining an explicit boundary resolution policy. It supports easing on transitions, fulfilling the deferral from OBJ-035 D13 ("Transition easing can be added in OBJ-036").

## Interface Contract

### Module: `src/scenes/scene-sequencer.ts`

```typescript
import type { TransitionSpec, TransitionTypeName } from '../transitions/types';
import type { EasingName } from '../interpolation/easings';

// ────────────────────────────────────────────
// Input Types
// ────────────────────────────────────────────

/**
 * Minimal scene timing input for the sequencer.
 * A projection of the manifest's Scene type — only timing
 * and transition fields, no geometry/camera/planes.
 *
 * The orchestrator constructs these from the validated manifest
 * scenes before passing them to the sequencer.
 *
 * When `transition_in` or `transition_out` is undefined, it is
 * treated as `{ type: 'cut', duration: 0 }` for boundary
 * resolution purposes.
 */
export interface SequencerSceneInput {
  /** Unique scene identifier. Must be non-empty. */
  id: string;
  /** Scene start time in seconds. Must be >= 0. */
  start_time: number;
  /** Scene duration in seconds. Must be > 0. */
  duration: number;
  /** Transition applied when this scene enters. Optional. Absent = cut. */
  transition_in?: TransitionSpec;
  /** Transition applied when this scene exits. Optional. Absent = cut. */
  transition_out?: TransitionSpec;
}

/**
 * Configuration for the SceneSequencer.
 */
export interface SequencerConfig {
  /**
   * Scene timing data. Must contain at least one scene.
   * Scenes need not be sorted — the sequencer sorts by start_time
   * internally (stable sort, preserving original order for ties).
   */
  scenes: SequencerSceneInput[];
  /** Frames per second. Must be > 0 and finite. */
  fps: number;
}

// ────────────────────────────────────────────
// Output Types
// ────────────────────────────────────────────

/**
 * A single render pass within a frame plan.
 * Multiple passes occur during crossfade transitions (outgoing first).
 * For non-crossfade frames, there is exactly one pass (or zero for gap frames).
 */
export interface RenderPassPlan {
  /** The scene to render. */
  sceneId: string;

  /**
   * Per-scene normalized time: t in [0, 1].
   * Computed as: clamp((timestamp - scene.start_time) / scene.duration, 0, 1)
   * where timestamp = frame / fps.
   *
   * The camera path preset evaluates at this value to determine
   * camera position, lookAt, and FOV for this pass.
   */
  normalizedTime: number;

  /**
   * Scene opacity for this pass. Range [0, 1].
   * 1.0 during normal rendering (no active transition).
   * Animated during transitions per the resolved boundary or edge transition.
   *
   * The orchestrator maps this to RenderPass.opacity in the
   * RenderFrameCommand sent to the page protocol (OBJ-011).
   */
  opacity: number;
}

/**
 * The complete rendering plan for a single frame.
 * Returned by SceneSequencer.planFrame().
 */
export interface FramePlan {
  /** The frame number this plan is for (zero-indexed). */
  frame: number;

  /** Timestamp in seconds: frame / fps. */
  timestamp: number;

  /**
   * Render passes for this frame, in compositing order.
   * - Empty array: gap frame (no scene active — render black).
   * - Single element: normal frame or scene in a fade.
   * - Two elements: crossfade transition (outgoing scene first,
   *   incoming scene second). Or two scenes whose independent
   *   fades overlap in time.
   *
   * The orchestrator iterates these in order to construct
   * RenderFrameCommand passes for OBJ-011.
   */
  passes: RenderPassPlan[];

  /**
   * Scene IDs that must be set up (loaded) on the page for this frame.
   * Equal to the unique scene IDs in `passes`.
   * The orchestrator diffs this against its tracked active set
   * to determine which scenes to set up and which to tear down.
   */
  requiredSceneIds: string[];

  /**
   * Scene IDs being actively rendered, for progress reporting.
   * Maps directly to OrchestratorResult's RenderProgress.activeSceneIds.
   * Equal to requiredSceneIds in V1.
   */
  activeSceneIds: string[];

  /** True if no scene is active at this frame (time gap between scenes). */
  isGap: boolean;
}

// ────────────────────────────────────────────
// Warning Types
// ────────────────────────────────────────────

export type SequencerWarningCode =
  | 'CROSSFADE_NO_OVERLAP'         // crossfade specified but scenes don't overlap in time
  | 'CROSSFADE_FIRST_SCENE'        // crossfade transition_in on first scene (no preceding scene)
  | 'CROSSFADE_LAST_SCENE'         // crossfade transition_out on last scene (no following scene)
  | 'TRANSITION_CONFLICT'          // adjacent scenes specify incompatible transition types
  | 'TRANSITION_EXCEEDS_SCENE'     // transition duration longer than scene duration (clamped)
  | 'TRANSITION_OVERLAP_INTERNAL'  // combined in+out fade durations exceed scene duration (both clamped)
  | 'OVERLAP_EXCEEDS_TWO'          // more than 2 scenes overlap at some point in time
  | 'TRANSITION_DURATION_MISMATCH' // crossfade spec duration differs from actual scene overlap
  | 'INVALID_EASING_FALLBACK'      // easing name in TransitionSpec was invalid; fell back to default
  | 'ZERO_DURATION_FADE_FALLBACK'  // dip_to_black with duration <= 0 treated as cut
  ;

export interface SequencerWarning {
  /** Warning classification code. */
  code: SequencerWarningCode;
  /** Scene ID(s) involved. For boundary warnings, the outgoing scene ID. */
  sceneId: string;
  /** Human-readable description of the warning. */
  message: string;
}

// ────────────────────────────────────────────
// Diagnostic Types
// ────────────────────────────────────────────

/**
 * A timeline entry representing a scene's frame range in the composition.
 * Exposed via SceneSequencer.timeline for debugging and test inspection.
 */
export interface TimelineEntry {
  sceneId: string;
  /** First frame of this scene (inclusive). */
  startFrame: number;
  /** Last frame + 1 of this scene (exclusive). */
  endFrame: number;
  /** Scene start time in seconds (from manifest). */
  startTime: number;
  /** Scene end time in seconds (start_time + duration). */
  endTime: number;
  /** Scene duration in seconds (from manifest). */
  durationSeconds: number;
}

/**
 * A resolved boundary between two consecutive scenes (by start_time).
 * Exposed via SceneSequencer.boundaries for debugging and test inspection.
 *
 * Field semantics for overlapStartFrame/overlapEndFrame vary by effectiveType:
 * - 'cut': both are -1 (no transition window).
 * - 'crossfade': the crossfade overlap window [B.startFrame, A.endFrame).
 * - 'independent_fades': the union of both fade windows — overlapStartFrame
 *   is the earliest frame where any fade in this boundary is active
 *   (min of outgoing fade start, incoming fade start); overlapEndFrame is
 *   the latest frame + 1 (max of outgoing fade end, incoming fade end).
 */
export interface ResolvedBoundary {
  /** Scene ID of the outgoing (earlier) scene. */
  outgoingSceneId: string;
  /** Scene ID of the incoming (later) scene. */
  incomingSceneId: string;
  /**
   * The effective transition type resolved for this boundary
   * after conflict resolution (see D2).
   * 'crossfade': both scenes render with complementary opacity.
   * 'independent_fades': each scene fades independently (out/in).
   * 'cut': instant switch, no animation.
   */
  effectiveType: 'cut' | 'crossfade' | 'independent_fades';
  /** Resolved easing for this boundary's transition. */
  effectiveEasing: EasingName;
  /**
   * First frame of the transition window (inclusive).
   * -1 for cut transitions. See type-level JSDoc for semantics per effectiveType.
   */
  overlapStartFrame: number;
  /**
   * Last frame + 1 of the transition window (exclusive).
   * -1 for cut transitions. See type-level JSDoc for semantics per effectiveType.
   */
  overlapEndFrame: number;
}

/**
 * A resolved edge transition (first scene fade-in or last scene fade-out).
 * Exposed via SceneSequencer.edgeTransitions for debugging and test inspection.
 */
export interface ResolvedEdgeTransition {
  sceneId: string;
  direction: 'in' | 'out';
  /** Always a simple fade — crossfade at edges is downgraded (see D7). */
  effectiveType: 'fade';
  /** First frame of the fade window (inclusive). */
  fadeStartFrame: number;
  /** Last frame + 1 of the fade window (exclusive). */
  fadeEndFrame: number;
  easing: EasingName;
}

// ────────────────────────────────────────────
// Errors
// ────────────────────────────────────────────

export type SequencerErrorCode =
  | 'NO_SCENES'              // scenes array is empty
  | 'INVALID_FPS'            // fps <= 0 or non-finite
  | 'INVALID_SCENE_TIMING'   // scene has start_time < 0 or duration <= 0 or non-finite
  | 'DUPLICATE_SCENE_ID'     // two scenes share the same id
  | 'FRAME_OUT_OF_RANGE'     // planFrame called with frame < 0 or >= totalFrames
  ;

/**
 * Structured error from the scene sequencer.
 */
export class SequencerError extends Error {
  readonly code: SequencerErrorCode;
  /** Scene ID involved, if applicable. */
  readonly sceneId?: string;

  constructor(code: SequencerErrorCode, message: string, sceneId?: string);
}

// ────────────────────────────────────────────
// Main Class
// ────────────────────────────────────────────

/**
 * Converts manifest scene timing into per-frame rendering plans.
 *
 * Construction phase (synchronous):
 * 1. Validates input (non-empty scenes, positive fps, unique IDs, valid timing).
 * 2. Validates easing names in TransitionSpecs (D18).
 * 3. Normalizes degenerate TransitionSpecs (D17).
 * 4. Sorts scenes by start_time (stable sort).
 * 5. Converts scene times to frame ranges (TimelineEntry[]).
 * 6. Resolves boundaries between consecutive scenes (D2 policy).
 * 7. Resolves edge transitions for first/last scene (D7).
 * 8. Clamps transition durations that exceed scene durations (D8).
 * 9. Validates concurrent scene count (D11).
 * 10. Collects all warnings.
 *
 * Query phase:
 * planFrame() is the primary method, called once per frame by the
 * orchestrator's render loop. It is a pure function of the frame
 * number and the precomputed timeline — no mutable state.
 *
 * Thread-safe for concurrent reads. Suitable for parallel rendering (OBJ-082).
 * Immutable after construction.
 */
export class SceneSequencer {
  /** Total number of frames in the composition. */
  readonly totalFrames: number;

  /** Total duration in seconds. */
  readonly totalDuration: number;

  /** Frames per second (from config). */
  readonly fps: number;

  /** Warnings collected during timeline construction. */
  readonly warnings: readonly SequencerWarning[];

  /** Scene timeline entries, sorted by startFrame. */
  readonly timeline: readonly TimelineEntry[];

  /** Resolved boundaries between consecutive scenes. */
  readonly boundaries: readonly ResolvedBoundary[];

  /** Resolved edge transitions (first scene fade-in, last scene fade-out). */
  readonly edgeTransitions: readonly ResolvedEdgeTransition[];

  /**
   * Constructs a SceneSequencer from scene timing data.
   *
   * @param config - Sequencer configuration with scenes and fps.
   * @throws SequencerError with code 'NO_SCENES' if scenes array is empty.
   * @throws SequencerError with code 'INVALID_FPS' if fps <= 0 or is not finite.
   * @throws SequencerError with code 'INVALID_SCENE_TIMING' if any scene
   *         has start_time < 0, duration <= 0, or non-finite values.
   * @throws SequencerError with code 'DUPLICATE_SCENE_ID' if two scenes
   *         share the same id. Error message names the duplicate ID.
   */
  constructor(config: SequencerConfig);

  /**
   * Returns the rendering plan for a specific frame.
   *
   * Pure function: same frame number always returns the same FramePlan.
   * No side effects. O(log n + k) time where n = scene count, k = active scenes.
   *
   * @param frame - Frame number (zero-indexed). Must be in [0, totalFrames).
   * @returns FramePlan for the requested frame.
   * @throws SequencerError with code 'FRAME_OUT_OF_RANGE' if
   *         frame < 0 or frame >= totalFrames. Error message includes
   *         the invalid frame and the valid range.
   */
  planFrame(frame: number): FramePlan;
}
```

### Module Exports: `src/scenes/index.ts`

```typescript
export {
  SceneSequencer,
  SequencerError,
} from './scene-sequencer';

export type {
  SequencerSceneInput,
  SequencerConfig,
  RenderPassPlan,
  FramePlan,
  SequencerWarning,
  SequencerWarningCode,
  TimelineEntry,
  ResolvedBoundary,
  ResolvedEdgeTransition,
  SequencerErrorCode,
} from './scene-sequencer';
```

## Design Decisions

### D1: Stateless Query Model — Pure `planFrame`

**Decision:** The `SceneSequencer` precomputes the full timeline, boundaries, and edge transitions during construction. `planFrame(frame)` is a pure function of the frame number — it carries no mutable state between calls.

**Rationale:** (a) The orchestrator independently tracks which scenes are currently set up on the page (OBJ-035 D14), diffing `requiredSceneIds` against its own tracked set. A stateful sequencer emitting setup/teardown commands would duplicate lifecycle tracking and create tight coupling. (b) Pure queries enable parallel rendering (OBJ-082) where arbitrary frame ranges can be planned without sequential state dependency. (c) Easier to test — each frame can be validated independently without setup/teardown ordering.

### D2: Transition Boundary Resolution Policy (resolves OBJ-008 OQ-A)

**Decision:** At a boundary between consecutive scenes A (outgoing) and B (incoming), resolved after sorting by `start_time`:

| A.transition_out | B.transition_in | Effective Type | Behavior |
|---|---|---|---|
| `cut` / absent | `cut` / absent | `cut` | Instant switch at boundary. |
| `crossfade` | `crossfade` / `cut` / absent | `crossfade` | Overlap window = `[B.startFrame, A.endFrame)`. Both render with complementary opacity via OBJ-008. |
| `crossfade` | `dip_to_black` | `crossfade` | Crossfade takes precedence. `TRANSITION_CONFLICT` warning. |
| `dip_to_black` | `dip_to_black` | `independent_fades` | Each scene fades independently. A fades out; B fades in. |
| `dip_to_black` | `crossfade` | `independent_fades` | Independent fades. `TRANSITION_CONFLICT` warning. B's entry treated as fade-in (not crossfade). |
| `dip_to_black` | `cut` / absent | `independent_fades` | A fades out; B appears at full opacity immediately. Only A's fade-out is active. |
| `cut` / absent | `crossfade` | `independent_fades` | Crossfade needs A, but A has cut. `TRANSITION_CONFLICT` warning. B's entry treated as fade-in. |
| `cut` / absent | `dip_to_black` | `independent_fades` | A cuts out; B fades in independently. |

**"Absent" means undefined:** When `transition_in` or `transition_out` is `undefined` on a `SequencerSceneInput`, it is treated as `{ type: 'cut', duration: 0 }` for boundary resolution.

**Priority rule:** The outgoing scene's `transition_out` takes precedence because the outgoing scene "owns" its exit. Crossfade is the only type that requires both scenes to render simultaneously — it can only occur if the outgoing scene specifies it.

**Crossfade requires time overlap:** If A.transition_out is `crossfade` but `B.start_time >= A.end_time` (no overlap), emit `CROSSFADE_NO_OVERLAP` warning and fall back to `cut`.

**Naming: `independent_fades` not `dip_to_black`:** The effective type `independent_fades` is used instead of `dip_to_black` because the sequencer does not use OBJ-008's two-phase dip_to_black algorithm. See D4 for details.

### D3: Crossfade Overlap Derived from Scene Timing

**Decision:** Crossfade duration equals the actual time overlap between scenes: `A.end_time - B.start_time`, converted to frames as `actualOverlapFrames = A.endFrame - B.startFrame`. The `duration` field in the crossfade `TransitionSpec` is treated as documentation/intent — the actual crossfade window is always derived from scene timing.

**Warning threshold:** Emit `TRANSITION_DURATION_MISMATCH` if `Math.abs(Math.round(spec.duration * fps) - actualOverlapFrames) > 1`.

**Crossfade opacity computation:** Uses `computeTransitionOpacity('crossfade', frame, overlapStartFrame, overlapEndFrame, easing)` from OBJ-008 directly. This returns complementary opacities: `outgoing = 1 - eased_t`, `incoming = eased_t`.

**Easing resolution for crossfade:** `A.transition_out.easing ?? B.transition_in.easing ?? 'linear'` where `'linear'` is OBJ-008's crossfade preset default.

**Rationale:** Seed manifest example (Section 4.6) shows scene_001 ending at 8.5s and scene_002 starting at 8.0s — the 0.5s overlap IS the crossfade. OBJ-035 D13 uses the same derivation: `[B.start_time, A.start_time + A.duration]`.

### D4: Independent Fades — Simple Single-Phase Opacity Ramps

**Decision:** When the boundary effective type is `independent_fades`, each scene's opacity is computed as a **simple single-phase fade**, not OBJ-008's two-phase `dip_to_black` algorithm. Specifically:

- **Fade-out** (scene ending): `opacity = 1 - getEasing(easing)(t)` where `t = (frame - fadeStartFrame) / (fadeEndFrame - fadeStartFrame)`.
- **Fade-in** (scene starting): `opacity = getEasing(easing)(t)` where `t = (frame - fadeStartFrame) / (fadeEndFrame - fadeStartFrame)`.

These are simple ramps: fade-out goes from 1 to 0, fade-in goes from 0 to 1, each over its own duration.

Fade-out window: `[endFrame - durationFrames, endFrame)` within the scene's time range.
Fade-in window: `[startFrame, startFrame + durationFrames)` within the scene's time range.

Where `durationFrames = Math.round(transitionSpec.duration * fps)`.

If two scenes' fade windows overlap in time (A fading out while B fading in), both render in separate passes at their respective independent opacities. Near the crossover point, both are at low opacity, producing a brief dim passage consistent with a "dip to black" visual feel — but this is emergent behavior from independent fades, not OBJ-008's two-phase algorithm.

**This is not OBJ-008's `dip_to_black`.** OBJ-008 defines `dip_to_black` as a single two-phase transition with a fully-black midpoint and the invariant `min(outgoing, incoming) === 0` (never both visible). The independent fade approach intentionally relaxes that invariant — when two fades overlap in time, both scenes may be visible simultaneously at low opacity. This is a deliberate difference: per-scene fades give each scene its own duration and easing, which is more flexible and matches the manifest's per-scene `TransitionSpec` model.

### D5: Easing on Transitions (fulfills OBJ-035 D13 deferral)

**Decision:** The sequencer applies easing to all transition opacity computations:
- **Crossfade:** Easing resolved per D3. Applied via `computeTransitionOpacity('crossfade', ...)` from OBJ-008.
- **Independent fades:** Easing from the scene's own `TransitionSpec.easing`, defaulting to `'ease_in_out'` (OBJ-008's dip_to_black preset default). Applied via `getEasing()` from OBJ-002.

OBJ-035 D13 stated: "Transition progress values are NOT eased in V1 — linear opacity ramps. Transition easing can be added in OBJ-036." This objective fulfills that deferral.

### D6: Per-Scene Normalized Time Computation

**Decision:** For a scene with `start_time` and `duration`, at timestamp `t_s = frame / fps`:

```
normalizedTime = clamp((t_s - start_time) / duration, 0, 1)
```

The `clamp` ensures normalizedTime stays in [0, 1] even when a scene is referenced during a transition window that extends slightly beyond its nominal time range.

Note: `normalizedTime` approaches but may not exactly reach 1.0 on the scene's last frame, because `timestamp = (endFrame - 1) / fps < start_time + duration`. For a 30fps, 5-second scene, the last frame's normalizedTime is approximately 0.9933. This is imperceptible in camera animation and consistent with OBJ-008's convention where `t` never reaches 1.0 within a window.

### D7: Edge Transitions (First and Last Scene)

**Decision:**

- **First scene's `transition_in`:**
  - `cut` or absent: Scene starts at full opacity (1.0) on its first frame.
  - `dip_to_black`: Scene fades in from black. Resolved as a `ResolvedEdgeTransition` with `effectiveType: 'fade'`.
  - `crossfade`: Emit `CROSSFADE_FIRST_SCENE` warning (no preceding scene). Treated as a fade-in with the same duration and easing.

- **Last scene's `transition_out`:**
  - `cut` or absent: Scene ends at full opacity on its last frame.
  - `dip_to_black`: Scene fades to black. Resolved as a `ResolvedEdgeTransition` with `effectiveType: 'fade'`.
  - `crossfade`: Emit `CROSSFADE_LAST_SCENE` warning (no following scene). Treated as a fade-out with the same duration and easing.

Edge transitions use the same simple single-phase fade formula as D4 (fade-in: `opacity = eased(t)`, fade-out: `opacity = 1 - eased(t)`).

### D8: Transition Duration Clamping

**Decision:** If a single fade's duration exceeds the scene's frame count:
1. Emit `TRANSITION_EXCEEDS_SCENE` warning.
2. Clamp `durationFrames` to the scene's frame count.

If a scene has both a fade-in and a fade-out (from any combination of edge transitions and boundary fades), and their combined `durationFrames` exceeds the scene's frame count:
1. Emit `TRANSITION_OVERLAP_INTERNAL` warning.
2. Clamp each to `Math.floor(sceneFrameCount / 2)`.

Crossfade durations are not clamped — they are derived from scene overlap (D3), which is inherently bounded by scene timing.

### D9: Scene Sorting

**Decision:** Scenes are sorted by `start_time` using a stable sort. Ties are broken by original array order.

### D10: Total Duration and Total Frames

**Decision:**
- `totalDuration = Math.max(...scenes.map(s => s.start_time + s.duration))`
- `totalFrames = Math.round(totalDuration * fps)`

Matches OBJ-035 D17 and OBJ-016's `computeTotalDuration()`.

### D11: Concurrent Scene Limit Warning

**Decision:** During construction, the sequencer checks if more than 2 scenes' time ranges overlap at any point. If so, it emits an `OVERLAP_EXCEEDS_TWO` warning. The sequencer still functions correctly — `planFrame` includes all active scenes in `passes`.

**Check algorithm:** For each scene's start frame, count how many scenes' frame ranges `[startFrame, endFrame)` contain that frame. If the count exceeds 2 at any point, emit the warning.

### D12: `planFrame` Performance

**Decision:** `planFrame()` must execute in O(log n + k) time where n = scene count and k = active scenes at that frame (typically 1-2). The implementation should use binary search on the sorted timeline to find candidate scenes.

### D13: The Sequencer Does Not Access Geometry or Camera Registries

**Decision:** The sequencer operates exclusively on timing and transition data. It does not import or query `GeometryRegistry` (OBJ-005) or `CameraPathRegistry` (OBJ-006). Geometry resolution, camera state computation, and scene setup construction remain in the orchestrator.

**Note on OBJ-005 dependency:** The objective metadata lists OBJ-005 as a dependency. This dependency is satisfied transitively — the orchestrator uses both the sequencer (timing) and the geometry registry (spatial data). The sequencer's `planFrame` output provides scene IDs and normalized time; the orchestrator maps those to geometry definitions and camera evaluations.

### D14: Crossfade Boundaries Override Independent Fade Modifiers

**Decision:** If a scene is involved in a crossfade boundary AND has an active independent fade (e.g., a fade-in from a prior boundary or an edge transition), the crossfade opacity takes precedence for frames within the crossfade window. The independent fade applies only to frames outside the crossfade window.

**Example:** Scene B has a fade-in (from its boundary with A) covering frames 100-115, AND a crossfade (with scene C) covering frames 110-130. During frames 110-115, both modifiers could apply. The crossfade opacity is used — B's opacity is determined solely by the crossfade formula with C. During frames 100-109, the fade-in applies normally.

**Note on potential discontinuity:** At the boundary where crossfade takes over from the independent fade (frame 110 in the example), there may be a visible opacity jump if the fade-in has not yet reached 1.0. This is an inherent tradeoff — the alternative (multiplying fade and crossfade opacities) would break the complementary opacity invariant (`out + in = 1.0`) that crossfade guarantees. In practice, the SKILL.md should advise LLM authors to avoid configurations where a scene's fade-in overlaps with a subsequent crossfade-out for the same scene.

**Rationale:** Crossfade defines a precise complementary opacity relationship between two scenes (`out + in = 1.0`). Multiplying an additional fade modifier would violate this invariant and create unexpected brightness dips.

### D15: Frame-to-Time and Time-to-Frame Conversion

**Decision:** Consistent conversion formulas:
- Time to frame: `Math.round(time * fps)` — matches OBJ-008 convention.
- Frame to time: `frame / fps` — exact division, no rounding.

Scene frame ranges:
- `startFrame = Math.round(scene.start_time * fps)`
- `endFrame = Math.round((scene.start_time + scene.duration) * fps)`

### D16: OBJ-008 Function Usage Contract

**Decision:** The sequencer uses the following from OBJ-008:

| Function / Type | Used? | How |
|---|---|---|
| `TransitionSpec` | Yes | Input type in `SequencerSceneInput`. |
| `TransitionTypeName` | Yes | Type guard and branching in boundary resolution. |
| `isTransitionTypeName` | Yes | Validation during construction. |
| `getTransitionPreset` | Yes | Reading `defaultEasing` for easing resolution. |
| `transitionPresets` | Yes | Reading preset metadata. |
| `computeTransitionOpacity('crossfade', ...)` | **Yes** | Crossfade opacity computation in `planFrame`. |
| `computeTransitionOpacity('dip_to_black', ...)` | **No** | Not used. Independent fades use D4's simple ramp formula instead. |
| `computeTransitionOpacity('cut', ...)` | **No** | Not needed. Cuts have no opacity animation. |
| `resolveTransition` | **No** | The sequencer computes frame ranges directly from scene timing (D3, D15). |
| `ResolvedTransition` | **No** | Not used — the sequencer has its own `ResolvedBoundary` type. |

**Rationale:** OBJ-008's `computeTransitionOpacity('dip_to_black', ...)` models a single two-phase window with a midpoint-black invariant. The sequencer's independent fades model (D4) is a different algorithm that gives each scene its own fade duration and easing. Using OBJ-008's dip_to_black function would require synthesizing a single artificial window that doesn't correspond to either scene's timing, which is awkward and loses per-scene control.

### D17: Degenerate TransitionSpec Normalization

**Decision:** During construction, the sequencer normalizes degenerate `TransitionSpec` values:

- `dip_to_black` with `duration <= 0`: Treated as `cut`. Emit `ZERO_DURATION_FADE_FALLBACK` warning.
- `crossfade` with `duration <= 0`: Duration field is ignored for crossfade (D3 derives duration from overlap). No special handling needed.
- `cut` with any duration: Duration ignored per OBJ-008 spec.

**Rationale:** OBJ-008's `resolveTransition` would throw for `dip_to_black` with `duration: 0`. The sequencer catches this upstream and gracefully degrades rather than propagating the error.

### D18: Easing Validation at Construction

**Decision:** During construction, easing names in all `TransitionSpec` objects are validated using `isEasingName()` from OBJ-002. If an easing name is invalid:
1. Emit `INVALID_EASING_FALLBACK` warning naming the invalid easing and the scene.
2. Fall back to the preset's `defaultEasing` (from `getTransitionPreset(spec.type)`).

This prevents runtime errors during `planFrame` — all easing functions are validated and resolved during construction.

## Orchestrator Integration Contract

This section specifies how the orchestrator (OBJ-035) integrates the scene sequencer. The orchestrator's public API (`Orchestrator.render()`, `OrchestratorConfig`, `OrchestratorResult`) does not change.

### Phase A Integration (Validation & Pre-Flight)

After manifest validation (OBJ-035 D7) and geometry/camera resolution (OBJ-035 D12), the orchestrator:

1. **Constructs `SequencerSceneInput[]`** from the validated manifest's `scenes` array:
   ```typescript
   const sequencerScenes: SequencerSceneInput[] = manifest.scenes.map(s => ({
     id: s.id,
     start_time: s.start_time,
     duration: s.duration,
     transition_in: s.transition_in,
     transition_out: s.transition_out,
   }));
   ```

2. **Creates a `SceneSequencer` instance** once:
   ```typescript
   const sequencer = new SceneSequencer({
     scenes: sequencerScenes,
     fps: manifest.composition.fps,
   });
   ```

3. **Merges sequencer warnings** into the orchestrator's warnings list for `OrchestratorResult.warnings`.

4. **Uses `sequencer.totalFrames`** to verify agreement with `FrameClock.totalFrames`. If they differ, the orchestrator should use the FrameClock's value (authoritative for frame iteration) and log a debug warning.

### Phase C Integration (Frame Render Loop)

The orchestrator's frame render loop changes from inline scene determination to `planFrame` calls:

**For each frame tick from `FrameClock.frames()`:**

1. **Call `sequencer.planFrame(tick.frame)`** to get a `FramePlan`.

2. **Handle gap frames:** If `plan.isGap === true`, explicitly clear the canvas via `bridge.evaluate(...)` (existing D16 behavior), capture the frame, pipe to FFmpeg. Skip to next frame.

3. **Manage scene lifecycle:** Diff `plan.requiredSceneIds` against the orchestrator's tracked `activeSceneIds: Set<string>`:
   - Scene IDs in `requiredSceneIds` but not in `activeSceneIds`: call `protocol.setupScene(...)` for those scenes (OBJ-035 D5).
   - Scene IDs in `activeSceneIds` but not in `requiredSceneIds`: call `protocol.teardownScene(sceneId)`.
   - Update `activeSceneIds`.

4. **Construct `RenderFrameCommand`:** Map `plan.passes` to `RenderPass[]`:
   ```typescript
   const passes: RenderPass[] = plan.passes.map(pass => ({
     sceneId: pass.sceneId,
     opacity: pass.opacity,
     camera: computeCameraState(pass.sceneId, pass.normalizedTime),
   }));
   ```
   Where `computeCameraState` uses the camera registry (OBJ-006) and `CameraParams` from the manifest, identical to OBJ-035 D4 but using `pass.normalizedTime` instead of computing `t` inline.

5. **Send to page protocol:** `protocol.renderFrame({ passes })`.

6. **Capture and encode:** Same as before — `capture.capture()`, `encoder.writeFrame(...)`.

7. **Progress callback:** `onProgress({ ..., activeSceneIds: plan.activeSceneIds })`.

### What the Sequencer Replaces in the Orchestrator

| OBJ-035 Section | Before (Inline) | After (Sequencer) |
|---|---|---|
| D3 step 2 (scene timeline) | Orchestrator builds timeline internally | `sequencer.timeline` |
| D3 step 3a (find active scene) | Orchestrator scans scenes per frame | `sequencer.planFrame(frame).passes` |
| D3 step 3c (transition windows) | Orchestrator computes overlap inline | `sequencer.planFrame(frame).passes[].opacity` |
| D3 step 3d (gap frames) | Orchestrator detects gaps inline | `plan.isGap` |
| D4 (per-scene normalized time) | Orchestrator computes `t = clamp(...)` | `pass.normalizedTime` |
| D13 (transition rendering) | Orchestrator computes crossfade/dip opacity inline | `pass.opacity` (pre-computed by sequencer) |
| D14 (lazy setup, eager teardown) | Orchestrator tracks active scenes | Orchestrator still tracks, but diffs against `plan.requiredSceneIds` |

### What Remains in the Orchestrator

- Scene setup construction (geometry + image resolution to `SceneSetupConfig`): OBJ-035 D5.
- Camera state computation from `normalizedTime`: OBJ-035 D4 (formula unchanged, input source changes).
- Gap frame canvas clearing: OBJ-035 D16.
- All resource lifecycle management: browser, FFmpeg, page protocol.
- Progress callback invocation.
- Error handling and cleanup.

## Acceptance Criteria

### Construction Validation

- [ ] **AC-01:** Constructor with empty `scenes` array throws `SequencerError` with code `NO_SCENES`.
- [ ] **AC-02:** Constructor with `fps <= 0` throws `SequencerError` with code `INVALID_FPS`.
- [ ] **AC-03:** Constructor with a scene having `duration <= 0` throws `SequencerError` with code `INVALID_SCENE_TIMING`. Error message names the scene ID.
- [ ] **AC-04:** Constructor with a scene having `start_time < 0` throws `SequencerError` with code `INVALID_SCENE_TIMING`.
- [ ] **AC-05:** Constructor with two scenes sharing the same `id` throws `SequencerError` with code `DUPLICATE_SCENE_ID`. Error message names the duplicate ID.
- [ ] **AC-06:** Scenes provided out of `start_time` order are sorted correctly. `timeline[0]` has the earliest `startFrame`.
- [ ] **AC-07:** Constructor with `fps` of `NaN` or `Infinity` throws `SequencerError` with code `INVALID_FPS`.
- [ ] **AC-08:** Constructor with a scene having `start_time: NaN` throws `SequencerError` with code `INVALID_SCENE_TIMING`.

### Total Duration and Frames

- [ ] **AC-09:** For a single scene with `start_time: 0, duration: 2.0` at 30fps: `totalDuration === 2.0`, `totalFrames === 60`.
- [ ] **AC-10:** For two scenes where scene B ends later than scene A: `totalDuration` equals `Math.max(A.end, B.end)`.
- [ ] **AC-11:** `totalFrames === Math.round(totalDuration * fps)`.

### Normal Frame Planning (Single Scene, No Transitions)

- [ ] **AC-12:** For a single-scene composition (no transitions), `planFrame(0)` returns one pass with `opacity: 1.0` and `normalizedTime: 0.0`.
- [ ] **AC-13:** For a single scene at 30fps, 2.0s duration, `planFrame(30)` returns `normalizedTime` of `0.5` (= `(30/30 - 0) / 2.0`).
- [ ] **AC-14:** `planFrame(totalFrames - 1)` for a single scene returns `normalizedTime` close to but less than `1.0`.
- [ ] **AC-15:** `requiredSceneIds` contains exactly the scene ID from the pass. `isGap` is `false`.

### Gap Frames

- [ ] **AC-16:** For two scenes with a gap (B.start_time > A.end_time), frames in the gap have `passes: []`, `isGap: true`, `requiredSceneIds: []`.
- [ ] **AC-17:** The frame immediately before the gap (last frame of scene A) has `isGap: false`. The frame immediately after the gap (first frame of scene B) has `isGap: false`.

### Crossfade Transitions

- [ ] **AC-18:** Two scenes with time overlap (B starts before A ends), A with `transition_out: { type: 'crossfade', duration: 1.0 }`: frames in the overlap window have 2 passes. The first pass is the outgoing scene, the second is the incoming scene.
- [ ] **AC-19:** At the first frame of a crossfade overlap, outgoing opacity is approximately 1.0 and incoming opacity is approximately 0.0.
- [ ] **AC-20:** At the last frame of a crossfade overlap, outgoing opacity is near 0.0 and incoming opacity is near 1.0.
- [ ] **AC-21:** At every frame within a crossfade, `passes[0].opacity + passes[1].opacity` equals 1.0 within +/-1e-10 (complementary opacity invariant).
- [ ] **AC-22:** Frames before the overlap window have only the outgoing scene at opacity 1.0. Frames after have only the incoming scene at opacity 1.0.
- [ ] **AC-23:** Crossfade with `easing: 'ease_in_out'` produces different opacity values than with `easing: 'linear'` at non-boundary frames.
- [ ] **AC-24:** Crossfade where `TransitionSpec.duration` differs from actual overlap by 3+ frames: `warnings` contains `TRANSITION_DURATION_MISMATCH`.

### Independent Fade Transitions

- [ ] **AC-25:** Last scene with `transition_out: { type: 'dip_to_black', duration: 1.0 }` at 30fps: the last 30 frames have opacity decreasing from approximately 1.0 toward 0.0. Frames before the fade window have opacity 1.0. Only one pass per frame.
- [ ] **AC-26:** First scene with `transition_in: { type: 'dip_to_black', duration: 0.5 }` at 30fps: the first 15 frames have opacity increasing from approximately 0.0 toward approximately 1.0. Only one pass per frame.
- [ ] **AC-27:** Two consecutive scenes with `dip_to_black` exit (A) and `dip_to_black` entry (B), no time overlap: during A's fade-out, only A appears in passes. During B's fade-in, only B appears. If there's a gap between fade windows, gap frames appear.
- [ ] **AC-28:** Two consecutive scenes with `dip_to_black` fades that overlap in time: both scenes appear in passes during the overlap, each at their independent opacity. The two opacities are NOT complementary (they do not sum to 1.0).

### Boundary Conflict Resolution (D2)

- [ ] **AC-29:** A.transition_out = `crossfade`, B.transition_in = `dip_to_black`, scenes overlap: effective type is `crossfade`. `warnings` contains a `TRANSITION_CONFLICT` entry.
- [ ] **AC-30:** A.transition_out = `cut`, B.transition_in = `crossfade`: effective type for boundary is `independent_fades`. `warnings` contains a `TRANSITION_CONFLICT` entry. B fades in instead of crossfading.
- [ ] **AC-31:** A.transition_out = `crossfade` but scenes don't overlap: effective type is `cut`. `warnings` contains `CROSSFADE_NO_OVERLAP`.
- [ ] **AC-32:** A.transition_out = `dip_to_black`, B.transition_in = `crossfade`: effective type is `independent_fades`. `warnings` contains `TRANSITION_CONFLICT`.

### Edge Transitions (D7)

- [ ] **AC-33:** First scene with `transition_in: { type: 'crossfade', duration: 1.0 }`: `edgeTransitions` contains an entry with `effectiveType: 'fade'` and `direction: 'in'`. `warnings` contains `CROSSFADE_FIRST_SCENE`.
- [ ] **AC-34:** Last scene with `transition_out: { type: 'crossfade', duration: 0.5 }`: `edgeTransitions` contains an entry with `effectiveType: 'fade'` and `direction: 'out'`. `warnings` contains `CROSSFADE_LAST_SCENE`.
- [ ] **AC-35:** First scene with no `transition_in`: no edge transition for that scene. Scene starts at opacity 1.0.

### Duration Clamping (D8)

- [ ] **AC-36:** Scene with duration 1.0s and `transition_out: { type: 'dip_to_black', duration: 2.0 }` at 30fps: `warnings` contains `TRANSITION_EXCEEDS_SCENE`. Fade-out applies over at most 30 frames (the scene's frame count).
- [ ] **AC-37:** Scene with duration 1.0s, `transition_in: dip_to_black 0.8s`, `transition_out: dip_to_black 0.8s` (combined 1.6s > 1.0s): `warnings` contains `TRANSITION_OVERLAP_INTERNAL`. Both clamped to 15 frames each.

### Concurrent Scene Warning (D11)

- [ ] **AC-38:** Three scenes whose time ranges all overlap at some frame: `warnings` contains `OVERLAP_EXCEEDS_TWO`. `planFrame` for the overlap frame returns all three scenes in `passes`.

### Frame Range Validation

- [ ] **AC-39:** `planFrame(-1)` throws `SequencerError` with code `FRAME_OUT_OF_RANGE`.
- [ ] **AC-40:** `planFrame(totalFrames)` throws `SequencerError` with code `FRAME_OUT_OF_RANGE`.
- [ ] **AC-41:** `planFrame(0)` and `planFrame(totalFrames - 1)` do not throw.

### Crossfade Override of Independent Fade (D14)

- [ ] **AC-42:** Scene B has a fade-in (from boundary with A, covering frames 100-115) and is in a crossfade (with scene C, covering frames 110-130). At frame 105 (fade-in only), B's opacity is determined by the fade-in formula. At frame 112 (within both the fade-in window and the crossfade window), B's opacity is determined solely by the crossfade formula with C — the fade-in modifier is not applied.

### Degenerate TransitionSpec Handling (D17, D18)

- [ ] **AC-43:** Scene with `transition_out: { type: 'dip_to_black', duration: 0 }`: treated as `cut`. `warnings` contains `ZERO_DURATION_FADE_FALLBACK`. No fade-out animation.
- [ ] **AC-44:** Scene with `transition_in: { type: 'dip_to_black', duration: -1.0 }`: treated as `cut`. `warnings` contains `ZERO_DURATION_FADE_FALLBACK`.
- [ ] **AC-45:** Scene with `transition_out: { type: 'crossfade', duration: 1.0, easing: 'bounce' as any }`: `warnings` contains `INVALID_EASING_FALLBACK`. Easing falls back to `'linear'` (crossfade default). Crossfade renders correctly with linear easing.

### Determinism

- [ ] **AC-46:** `planFrame(N)` called 100 times with the same arguments returns identical `FramePlan` objects every time (pure function).
- [ ] **AC-47:** Two `SceneSequencer` instances constructed with identical configs produce identical `planFrame` results for all frames.

### Performance

- [ ] **AC-48:** `planFrame` for a 10-scene composition completes in under 0.1ms per call (measured over 1000 calls).

## Edge Cases and Error Handling

### Construction Errors

| Scenario | Expected Behavior |
|---|---|
| Empty scenes array | Throws `SequencerError` code `NO_SCENES`. |
| `fps` is 0 | Throws `SequencerError` code `INVALID_FPS`. |
| `fps` is negative | Throws `SequencerError` code `INVALID_FPS`. |
| `fps` is `NaN` or `Infinity` | Throws `SequencerError` code `INVALID_FPS`. |
| Scene with `duration: 0` | Throws `SequencerError` code `INVALID_SCENE_TIMING`. |
| Scene with `duration: -1` | Throws `SequencerError` code `INVALID_SCENE_TIMING`. |
| Scene with `start_time: -0.5` | Throws `SequencerError` code `INVALID_SCENE_TIMING`. |
| Scene with `start_time: NaN` | Throws `SequencerError` code `INVALID_SCENE_TIMING`. |
| Two scenes with `id: 'scene_001'` | Throws `SequencerError` code `DUPLICATE_SCENE_ID`. |

### Transition Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `cut` with non-zero duration | Duration ignored. No animation. Instant switch. |
| `crossfade` where scenes don't overlap | Falls back to `cut` + `CROSSFADE_NO_OVERLAP` warning. |
| `crossfade` with `duration: 0` in TransitionSpec | Duration ignored for crossfade (derived from overlap per D3). If overlap exists, crossfade works normally. |
| Crossfade where overlap is exactly 1 frame | Valid. Single transition frame: outgoing opacity = 1.0 (t=0), incoming = 0.0. Effectively a cut with blend setup. |
| `dip_to_black` with `duration: 0` | Treated as `cut` + `ZERO_DURATION_FADE_FALLBACK` warning. |
| `dip_to_black` with `duration: -1` | Treated as `cut` + `ZERO_DURATION_FADE_FALLBACK` warning. |
| Scene shorter than its fade durations | Clamped per D8. Warning emitted. |
| Two adjacent scenes, no gap, no overlap, both `cut` | Instant switch. Frame at `A.endFrame` is the first frame of B (if B.startFrame === A.endFrame). |
| Scene with `start_time: 0, duration: 0.01` at 30fps | `startFrame = 0`, `endFrame = Math.round(0.01 * 30) = 0`. Scene has 0 frames. No frames rendered for this scene. If it has transitions, they're clamped to 0. |
| Invalid easing name in TransitionSpec | Warning + fallback to preset default per D18. |

### planFrame Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Frame 0 of a composition starting at `start_time: 0` | normalizedTime = 0.0, opacity per transition (1.0 if no fade-in). |
| Last frame of composition | normalizedTime close to 1.0 for the last scene. Opacity per transition. |
| Frame in a gap between scenes | `isGap: true`, `passes: []`, `requiredSceneIds: []`. |
| Frame where a crossfade starts (first overlap frame) | Two passes. Outgoing opacity approximately 1.0, incoming approximately 0.0. |
| Frame immediately after crossfade ends | Single pass with incoming scene at opacity 1.0. |
| Composition with a single scene, no transitions | Every frame has one pass with opacity 1.0. |
| Scene starting at `start_time > 0` with no prior scene | Frames before `startFrame` are gap frames. |

### Opacity Boundary Behavior

| Scenario | Expected Behavior |
|---|---|
| Crossfade: frame === overlapStartFrame | `t = 0`, outgoing opacity = 1.0, incoming = 0.0. |
| Crossfade: frame === overlapEndFrame - 1 | `t = (N-1)/N`, outgoing near 0, incoming near 1.0. |
| Crossfade: frame === overlapEndFrame (first post-overlap) | Only incoming scene, opacity 1.0. |
| Fade-out: frame === fadeStartFrame | `t = 0`, opacity = 1.0. |
| Fade-out: frame === fadeEndFrame - 1 | `t = (N-1)/N`, opacity near 0. |
| Fade-in: frame === fadeStartFrame | `t = 0`, opacity = 0.0 (for linear easing; `getEasing('ease_in_out')(0) = 0` also). |
| Fade-in: frame === fadeEndFrame | Opacity 1.0 (outside fade window). |

## Test Strategy

### Unit Tests: `test/unit/scene-sequencer.test.ts`

**Construction validation (AC-01 through AC-08):**
1. Empty scenes -> `NO_SCENES` error.
2. Invalid fps (0, -1, NaN, Infinity) -> `INVALID_FPS` error.
3. Scene with duration <= 0 -> `INVALID_SCENE_TIMING` error with scene ID.
4. Scene with start_time < 0 -> `INVALID_SCENE_TIMING` error.
5. Scene with NaN start_time -> `INVALID_SCENE_TIMING` error.
6. Duplicate scene IDs -> `DUPLICATE_SCENE_ID` error with ID in message.
7. Scenes out of order -> timeline sorted by startFrame.

**Total duration and frames (AC-09 through AC-11):**
8. Single scene: totalDuration and totalFrames computed correctly.
9. Two scenes: totalDuration = max end time.
10. Three scenes with gaps: totalDuration includes all scenes.

**Normal frame planning (AC-12 through AC-15):**
11. Single scene, no transitions: planFrame(0) -> opacity 1.0, normalizedTime 0.0.
12. Single scene: normalizedTime at midpoint = 0.5.
13. Single scene: last frame normalizedTime close to 1.0.
14. requiredSceneIds and activeSceneIds contain the scene ID.

**Gap frames (AC-16, AC-17):**
15. Two scenes with 1-second gap at 30fps: frames in gap return isGap:true, empty passes.
16. Boundary frames adjacent to gap are not gaps.

**Crossfade transitions (AC-18 through AC-24):**
17. Two overlapping scenes with crossfade: overlap frames have 2 passes.
18. Crossfade first frame: outgoing approximately 1.0, incoming approximately 0.0.
19. Crossfade last frame: outgoing near 0, incoming near 1.0.
20. Complementary invariant: out + in = 1.0 +/- 1e-10 at every overlap frame.
21. Pre-overlap: single scene. Post-overlap: single scene.
22. Crossfade with ease_in_out vs linear: different mid-transition opacities.
23. Crossfade with 1-frame overlap: degenerate but valid.
24. Crossfade spec duration mismatch: warning emitted when `|specFrames - actualFrames| > 1`.

**Independent fade transitions (AC-25 through AC-28):**
25. Last scene fade-out: final N frames have decreasing opacity. Single pass.
26. First scene fade-in: first N frames have increasing opacity. Single pass.
27. Two scenes with independent fades at boundary, no time overlap.
28. Two scenes with overlapping independent fades: both in passes, opacities NOT complementary.

**Boundary conflict resolution (AC-29 through AC-32):**
29. All combinations from the D2 matrix: verify effectiveType and warnings.
30. Crossfade with no overlap -> cut + warning.
31. Crossfade on first scene transition_in -> fade-in edge transition + warning.
32. Crossfade on last scene transition_out -> fade-out edge transition + warning.

**Duration clamping (AC-36, AC-37):**
33. Transition exceeding scene duration: clamped + warning.
34. Combined in+out exceeding scene: both clamped to half + warning.

**Concurrent scene warning (AC-38):**
35. Three overlapping scenes: OVERLAP_EXCEEDS_TWO warning. All three in passes.

**Frame range validation (AC-39 through AC-41):**
36. planFrame(-1) throws FRAME_OUT_OF_RANGE.
37. planFrame(totalFrames) throws FRAME_OUT_OF_RANGE.
38. planFrame(0) and planFrame(totalFrames - 1) succeed.

**Crossfade override of independent fade (AC-42):**
39. Scene B with fade-in + crossfade overlap: verify crossfade takes precedence in overlap window, fade-in applies outside.

**Degenerate TransitionSpec handling (AC-43 through AC-45):**
40. dip_to_black with duration 0: treated as cut + warning.
41. dip_to_black with negative duration: treated as cut + warning.
42. Invalid easing name: warning + fallback to default.

**Determinism (AC-46, AC-47):**
43. Same planFrame called repeatedly -> identical results.
44. Two identical sequencers -> identical results.

**Performance (AC-48):**
45. Benchmark: 10 scenes, 1000 planFrame calls < 100ms total.

### Integration Tests: `test/integration/scene-sequencer.test.ts`

These test the sequencer with real OBJ-008 and OBJ-002 functions (not mocked).

46. **5-scene composition with mixed transitions:** Scenes 1->2 crossfade, 2->3 cut, 3->4 independent fades, 4->5 crossfade. Verify every frame produces a valid FramePlan with correct opacities.
47. **Full sweep:** Create a 3-second, 30fps, 3-scene composition. Iterate all 90 frames via planFrame. Verify: no gaps where scenes should be active, no overlapping scene IDs outside transition windows, all opacities in [0, 1].
48. **Round-trip with OBJ-008:** Use `computeTransitionOpacity('crossfade', ...)` directly for crossfade frames and verify the sequencer's opacity matches.

### Relevant Testable Claims

- **TC-06** (Deterministic output): Tests 43-44 verify sequencer determinism.
- **TC-10** (Cross-scene transitions mask compositing seams): Tests 17-28 verify transition opacity computation.
- **TC-07** (Manifest validation catches errors): Construction validation tests verify rejection of invalid input.

## Integration Points

### Depends on

| Dependency | What OBJ-036 imports | Usage |
|---|---|---|
| **OBJ-008** (Transition contract) | `TransitionSpec`, `TransitionTypeName`, `isTransitionTypeName`, `getTransitionPreset`, `transitionPresets`, `computeTransitionOpacity` | Crossfade opacity via `computeTransitionOpacity('crossfade', ...)`. Preset metadata for default easing. Type guards. See D16 for full usage matrix. |
| **OBJ-002** (Interpolation/Easing) | `getEasing`, `isEasingName`, `EasingName` type. | Independent fade opacity computation (D4). Easing validation during construction (D18). |
| **OBJ-035** (Orchestrator) | No direct import. Architectural dependency — the orchestrator creates and uses the sequencer internally. See Orchestrator Integration Contract section. | The orchestrator constructs `SequencerSceneInput[]` from the validated manifest and passes it to the sequencer. |
| **OBJ-005** (Geometry types) | No direct import. Listed in objective metadata. Dependency satisfied transitively — the orchestrator uses both the sequencer (timing) and geometry registry (spatial data). See D13. | N/A. |

### Consumed by

| Downstream | How it uses OBJ-036 |
|---|---|
| **OBJ-037** (Transition renderer) | May use `FramePlan` and `RenderPassPlan` types. The transition renderer implements the Three.js side of opacity application; the sequencer provides the per-frame opacity values. |
| **OBJ-035** (Orchestrator -- integration) | Creates `SceneSequencer` in Phase A. Calls `planFrame(frame)` per frame in Phase C. Maps `FramePlan` to `RenderFrameCommand`. See Orchestrator Integration Contract. |

### File Placement

```
depthkit/
  src/
    scenes/
      scene-sequencer.ts       # NEW — SceneSequencer class, all types,
                                #       SequencerError, construction logic,
                                #       planFrame implementation
      index.ts                  # NEW or UPDATED — barrel export
  test/
    unit/
      scene-sequencer.test.ts   # NEW — unit tests
    integration/
      scene-sequencer.test.ts   # NEW — integration tests with real OBJ-008/OBJ-002
```

## Open Questions

### OQ-A: Should the sequencer accept a `totalFrames` override?

The orchestrator creates a `FrameClock` (OBJ-009) that computes `totalFrames` from duration and fps. The sequencer independently computes `totalFrames = Math.round(totalDuration * fps)`. If the formulas differ (e.g., FrameClock uses `Math.ceil`), there could be an off-by-one disagreement. Should `SequencerConfig` accept an optional `totalFrames?: number` override?

**Recommendation:** Defer. Document the formula (`Math.round`) and verify alignment with FrameClock during integration testing (OBJ-077). The Orchestrator Integration Contract specifies that on disagreement, FrameClock is authoritative. If `planFrame` is called with a frame >= sequencer's totalFrames but < FrameClock's totalFrames, the sequencer throws `FRAME_OUT_OF_RANGE`, which the orchestrator must handle (e.g., by treating as a gap frame).

### OQ-B: Should `planFrame` handle non-integer frame numbers?

**Recommendation:** No. Keep frame numbers as integers per the FrameClock contract.
