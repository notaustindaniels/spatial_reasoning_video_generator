# Specification: OBJ-038 — Audio Sync and Scene Timing

## Summary

OBJ-038 implements the scene timing resolution module (`src/engine/scene-timing.ts`) — the bridge between the declarative manifest timing and concrete, frame-level rendering instructions. It takes a validated Manifest (from OBJ-016), optional audio metadata (from OBJ-014's `probeMedia()`), and a timing configuration, then resolves scene durations and start times according to one of three timing modes defined in seed Section 8.7: **explicit** (manifest values as-is), **audio-proportional** (scale durations to fit audio length), or **audio-cue** (manifest `start_time` values treated as narration cue timestamps). It computes exact frame ranges per scene including transition overlaps, creates a `FrameClock` (OBJ-009) for the resolved composition, and provides a per-frame lookup function that returns which scene(s) are active with their normalized time and opacity. This module satisfies C-07 (audio synchronization) and TC-13 (audio duration drives total video length).

## Interface Contract

### Module: `src/engine/scene-timing.ts`

```typescript
import type { Manifest, Scene } from '../manifest/schema.js';
import { FrameClock } from './frame-clock.js';

// ─── Configuration Types ───

/**
 * Timing resolution mode, per seed Section 8.7.
 *
 * - 'explicit': Use manifest start_time and duration values as-is.
 *   If audioInfo is provided, emit AUDIO_DURATION_MISMATCH warning
 *   when total scene duration differs from audio duration beyond tolerance.
 *
 * - 'audio_proportional': Total video duration = audio duration.
 *   Manifest scene durations are used as proportional weights.
 *   Manifest start_time values are IGNORED and recomputed sequentially.
 *   Each scene's resolved duration = (manifestDuration / sumManifestDurations)
 *   * (audioDuration + totalTransitionOverlap). start_time values are
 *   recomputed sequentially, accounting for transition overlaps.
 *   Requires audioInfo.
 *
 * - 'audio_cue': Total video duration = audio duration.
 *   Manifest start_time values are treated as narration cue timestamps
 *   and preserved. Durations are computed from cue gaps:
 *   duration[i] = start_time[i+1] - start_time[i] + overlap[i] (for non-last),
 *   duration[last] = audioDuration - start_time[last].
 *   Requires audioInfo. Requires start_times to be monotonically non-decreasing.
 */
export type TimingMode = 'explicit' | 'audio_proportional' | 'audio_cue';

/**
 * Audio metadata provided by the caller (obtained via OBJ-014's probeMedia).
 * OBJ-038 does NOT probe audio files — it receives pre-probed metadata.
 * This separation respects AP-04 (don't conflate rendering with asset handling)
 * and keeps the module pure (no I/O, fully testable).
 */
export interface AudioInfo {
  /** Audio file duration in seconds. Must be positive and finite. */
  durationSeconds: number;
}

/**
 * Configuration for timeline resolution.
 */
export interface ResolveTimelineConfig {
  /**
   * Timing resolution mode.
   * Default: 'audio_proportional' when audioInfo is provided, 'explicit' when not.
   */
  mode?: TimingMode;

  /**
   * Tolerance in milliseconds for AUDIO_DURATION_MISMATCH warnings
   * in 'explicit' mode. If the absolute difference between total scene
   * duration and audio duration is within this tolerance, no warning
   * is emitted.
   * Default: 100 (accommodates ±3 frames of rounding at 30fps).
   */
  audioDurationToleranceMs?: number;
}

// ─── Output Types ───

/**
 * A resolved transition region mapped to frame space.
 * Null for 'cut' transitions (instantaneous, no frame range).
 */
export interface ResolvedTransition {
  /** Transition type from the manifest. */
  type: 'crossfade' | 'dip_to_black';
  /** Duration in seconds (from manifest, NOT scaled). */
  durationSeconds: number;
  /** First frame of the transition region (inclusive). */
  startFrame: number;
  /** Last frame + 1 of the transition region (exclusive). */
  endFrame: number;
  /** Number of frames: endFrame - startFrame. */
  frameCount: number;
}

/**
 * A scene with fully resolved timing in both time and frame domains.
 */
export interface ResolvedScene {
  /** Scene ID from manifest. */
  id: string;
  /** Original zero-based array index in manifest.scenes. */
  sceneIndex: number;
  /** Geometry name from manifest (passed through for orchestrator). */
  geometry: string;
  /** Camera name from manifest (passed through for orchestrator). */
  camera: string;

  // ─── Time domain ───
  /** Resolved start time in seconds. */
  startTime: number;
  /** Resolved duration in seconds. */
  duration: number;
  /** Resolved end time: startTime + duration. */
  endTime: number;

  // ─── Frame domain ───
  /** First frame of this scene (inclusive). */
  startFrame: number;
  /** Last frame + 1 of this scene (exclusive). */
  endFrame: number;
  /** Total frames: endFrame - startFrame. */
  frameCount: number;

  // ─── Transitions ───
  /**
   * Resolved inbound transition. null when:
   * - No transition_in in manifest, or
   * - transition_in.type is 'cut' (instantaneous, no frame range).
   */
  transitionIn: ResolvedTransition | null;
  /**
   * Resolved outbound transition. null when:
   * - No transition_out in manifest, or
   * - transition_out.type is 'cut'.
   */
  transitionOut: ResolvedTransition | null;
}

/**
 * The complete resolved timeline for a composition.
 */
export interface ResolvedTimeline {
  /** Frames per second from the manifest composition. */
  fps: number;
  /** Total frames in the composition. */
  totalFrames: number;
  /** Total duration in seconds. */
  totalDuration: number;
  /** The timing mode that was applied. */
  mode: TimingMode;
  /** FrameClock instance for this timeline (from OBJ-009). */
  clock: FrameClock;
  /**
   * Resolved scenes sorted by startTime (ascending).
   * Stable sort preserves manifest array order for equal start_times.
   */
  scenes: ResolvedScene[];
  /** Audio duration in seconds if provided, null otherwise. */
  audioDurationSeconds: number | null;
  /** Non-fatal warnings generated during resolution. */
  warnings: TimingWarning[];
}

/**
 * Warning emitted during timeline resolution.
 */
export interface TimingWarning {
  /** Machine-readable warning code. */
  code:
    | 'AUDIO_DURATION_MISMATCH'
    | 'SCENE_DURATION_ADJUSTED'
    | 'TRANSITION_TRUNCATED'
    | 'START_TIMES_IGNORED';
  /** Human-readable description. */
  message: string;
}

/**
 * Error thrown when timeline resolution fails unrecoverably.
 */
export class TimingError extends Error {
  constructor(
    message: string,
    public readonly code: string,
  ) {
    super(message);
    this.name = 'TimingError';
  }
}

// ─── Per-Frame Lookup Types ───

/**
 * State of a single scene within a frame.
 */
export interface FrameSceneState {
  /** Reference to the resolved scene. */
  scene: ResolvedScene;
  /**
   * Normalized time within this scene's duration: [0.0, 1.0].
   * Computed as: (frameTimestamp - scene.startTime) / scene.duration.
   * Clamped to [0, 1].
   * Used by camera path interpolation in the orchestrator.
   */
  normalizedTime: number;
  /**
   * Opacity for this scene's rendering.
   * 1.0 when no transition is active.
   * See D-13 and D-14 for transition opacity formulas.
   * Uses linear interpolation (easing for transitions deferred to V2).
   */
  opacity: number;
}

/**
 * Rendering state for a single frame. Returned by resolveFrameState().
 * Discriminated union on `type`.
 */
export type FrameState =
  | {
      /** Normal rendering: one or two scenes active. */
      type: 'scene';
      /** Primary (or only) scene. During transitions, this is the outgoing scene. */
      primary: FrameSceneState;
      /**
       * Secondary scene during overlap transitions.
       * Non-null only when two scenes' frame ranges overlap at this frame
       * AND the overlap is a transition (crossfade or dip_to_black).
       * null during solo transitions or no-transition frames.
       */
      secondary: FrameSceneState | null;
      /**
       * Active transition type, null if no transition is active at this frame.
       * Set when the frame falls within ANY transition region (solo or overlap):
       * - 'crossfade': alpha-blend both scenes (overlap only).
       * - 'dip_to_black': render scene(s) against black.
       */
      transitionType: 'crossfade' | 'dip_to_black' | null;
    }
  | {
      /**
       * Frame falls in a gap between scenes.
       * The orchestrator should render a black frame.
       * Gaps are valid (OBJ-016 warns but doesn't error).
       */
      type: 'gap';
    };

// ─── Functions ───

/**
 * Resolves manifest scene timing into concrete frame-level ranges.
 *
 * This is the primary entry point. Called by the orchestrator (OBJ-035)
 * after manifest validation (OBJ-016) and optional audio probing (OBJ-014).
 *
 * @param manifest - A validated Manifest (has passed OBJ-016 validation).
 * @param audioInfo - Audio metadata. Required for 'audio_proportional' and 'audio_cue' modes.
 * @param config - Optional timing configuration. Defaults per field docs.
 * @returns ResolvedTimeline with frame-level scene ranges and a FrameClock.
 *
 * @throws TimingError code 'NO_AUDIO' if mode requires audio but audioInfo is not provided.
 * @throws TimingError code 'INVALID_AUDIO_DURATION' if audioInfo.durationSeconds <= 0 or non-finite.
 * @throws TimingError code 'SCENE_TOO_SHORT' if a scaled scene duration (in audio modes)
 *   is shorter than the sum of its transition-in and transition-out durations.
 * @throws TimingError code 'INVALID_CUE_ORDER' if in 'audio_cue' mode and manifest
 *   start_times (sorted) are not monotonically non-decreasing.
 * @throws TimingError code 'CUE_EXCEEDS_AUDIO' if in 'audio_cue' mode and any
 *   scene's start_time >= audioInfo.durationSeconds.
 * @throws TimingError code 'NO_SCENES' if manifest.scenes is empty (defensive —
 *   OBJ-004 schema requires min 1 scene, but guard anyway).
 * @throws TimingError code 'ZERO_DURATION' if the resolved total duration is 0
 *   (e.g., all scenes have negligible duration after scaling).
 */
export function resolveTimeline(
  manifest: Manifest,
  audioInfo?: AudioInfo,
  config?: ResolveTimelineConfig,
): ResolvedTimeline;

/**
 * Resolves the rendering state for a specific frame number.
 *
 * Determines which scene(s) are active at this frame, their normalized
 * time (for camera path interpolation), and opacity (for transition blending).
 * Used by the orchestrator's per-frame render loop.
 *
 * Implementation: linear scan of timeline.scenes (O(n) where n = scene count,
 * typically 5-15). A cursor-based optimization for sequential access is left
 * to the orchestrator if needed (AP-05).
 *
 * @param frame - Zero-indexed frame number.
 * @param timeline - A resolved timeline from resolveTimeline().
 * @returns FrameState describing what to render.
 *
 * @throws TimingError code 'FRAME_OUT_OF_RANGE' if frame < 0 or frame >= timeline.totalFrames.
 */
export function resolveFrameState(
  frame: number,
  timeline: ResolvedTimeline,
): FrameState;

/**
 * Computes the transition overlap duration in seconds between two
 * consecutive scenes.
 *
 * Returns min(outgoing.transition_out.duration, incoming.transition_in.duration)
 * when both transitions exist and are non-cut. Returns 0 otherwise.
 *
 * Exported for testing and for use by the orchestrator and future modules.
 *
 * @param outgoing - The earlier scene (or its transition config).
 * @param incoming - The later scene (or its transition config).
 * @returns Overlap duration in seconds (>= 0).
 */
export function computeTransitionOverlap(
  outgoing: Pick<Scene, 'transition_out'>,
  incoming: Pick<Scene, 'transition_in'>,
): number;
```

## Design Decisions

### D-01: Stateless Functions, Not a Class

**Choice:** All exports are pure functions (except `TimingError` class). No mutable state, no lifecycle.

**Rationale:** Timeline resolution is a single computation: manifest + audio -> frame ranges. There is no streaming state to manage. Pure functions are trivially testable, composable, and have no hidden coupling. The `ResolvedTimeline` output is an immutable data structure consumed by OBJ-035.

### D-02: Caller Provides Audio Metadata — No I/O in This Module

**Choice:** OBJ-038 does NOT call `probeMedia()` or read files. The caller (OBJ-035 orchestrator) obtains `AudioInfo` via OBJ-014's `probeMedia()` and passes it in.

**Rationale:** Keeps the module pure — no filesystem access, no async I/O. Testable with simple mock data. Respects AP-04 (don't conflate rendering with asset handling). The orchestrator already handles file resolution; audio probing naturally belongs there.

### D-03: Three Timing Modes Map to Seed Section 8.7

**Choice:**

| Section 8.7 Language | TimingMode | Behavior |
|---|---|---|
| "If audio is provided and no explicit scene durations" | `'audio_proportional'` | Scale manifest durations proportionally to fill audio length |
| "If explicit scene durations are provided" | `'explicit'` | Use manifest `start_time` and `duration` as-is |
| "If both audio and explicit durations" | `'explicit'` with `audioInfo` provided | Use manifest timing, emit `AUDIO_DURATION_MISMATCH` warning |
| "Timestamp-based scene boundary alignment to narration cues" (C-07) | `'audio_cue'` | Preserve manifest `start_time` as cue points, compute durations from gaps |

**Relationship to OBJ-004 E-10:** OBJ-004 notes that "audio-proportional timing is computed by the manifest generator before emitting the manifest." OBJ-038 provides the algorithm for this computation. When a manifest generator pre-computes timing, the orchestrator uses `explicit` mode. When a manifest has placeholder durations (e.g., all equal weights) and audio should drive timing, the orchestrator uses `audio_proportional`. Both paths are valid.

### D-04: Default Mode Inferred from AudioInfo Presence

**Choice:** When `config.mode` is not specified:
- `audioInfo` provided -> default `'audio_proportional'`
- `audioInfo` not provided -> default `'explicit'`

**Rationale:** Satisfies TC-13's "automatically distributes" language. The most common audio scenario is: manifest has rough durations, audio file is the source of truth for total length.

### D-05: Manifest Durations Serve as Proportional Weights

**Choice:** In `audio_proportional` mode, each scene's manifest `duration` value is treated as a relative weight. A scene with `duration: 10` gets twice the resolved time as one with `duration: 5`.

**Rationale:** Elegant dual interpretation — `explicit` mode reads them as absolute seconds, `audio_proportional` reads them as relative weights. No schema change needed.

### D-06: Transition Durations Are Fixed, Not Scaled

**Choice:** In `audio_proportional` and `audio_cue` modes, transition durations from the manifest are preserved as-is. Only scene content durations scale.

**Rationale:** Transitions are perceptual constants — a 0.5s crossfade feels right regardless of whether the scene is 5s or 15s. Scaling transitions proportionally would make them unnaturally short for short scenes or long for long scenes. If scaling makes a scene shorter than its combined transition durations, that's a `SCENE_TOO_SHORT` error.

### D-07: Audio-Proportional Scaling Algorithm

**Choice:** The algorithm preserves total video duration = audio duration while maintaining transition overlaps. **Manifest `start_time` values are ignored in this mode** — start times are recomputed sequentially from scene 0.

```
Given: scenes S[0..N-1] with manifest durations D[i], transition overlaps O[i] between S[i] and S[i+1], audio duration A.

Total video duration = sum(D'[i]) - sum(O[i]) = A
Therefore: sum(D'[i]) = A + sum(O[i])

Scale factor = (A + sum(O[i])) / sum(D[i])
D'[i] = D[i] * scale

Start times (recomputed):
  startTime[0] = 0
  startTime[i] = startTime[i-1] + D'[i-1] - O[i-1]   for i > 0

Verify: max(startTime[i] + D'[i]) = A
```

If the recomputed start times differ from the manifest's `start_time` values by more than 1ms for any scene, a `START_TIMES_IGNORED` warning is emitted: `"In audio_proportional mode, manifest start_time values are ignored. Start times have been recomputed sequentially. To preserve specific start times, use audio_cue mode."` This warning is emitted at most once, regardless of how many scenes are affected.

### D-08: Audio-Cue Algorithm

**Choice:** In `audio_cue` mode:

```
Given: scenes sorted by manifest start_time (cue timestamps c[i]), overlaps O[i], audio duration A.

Duration[i] = (c[i+1] - c[i]) + O[i]   for i < N-1
Duration[N-1] = A - c[N-1]

Start times = manifest start_times (preserved).
```

**Verification:** `max(c[i] + Duration[i])` for any scene:
- Last scene: `c[N-1] + (A - c[N-1]) = A`
- Non-last scene `i`: `c[i] + c[i+1] - c[i] + O[i] = c[i+1] + O[i]` — exceeds `c[i+1]` by `O[i]`, which is the overlap with scene `i+1`. Correct.

### D-09: FrameClock Created Internally

**Choice:** `resolveTimeline()` creates a `FrameClock` via `FrameClock.fromDuration(fps, totalDuration)` and returns it in the timeline.

**Rationale:** The clock's `totalFrames` is derived from the resolved duration, which may differ from what the manifest implies (in audio modes). Creating it here ensures a single source of truth for the composition's frame count.

### D-10: Frame Boundaries via `FrameClock.timestampToFrame()`

**Choice:** Scene `startFrame` and `endFrame` are computed using `clock.timestampToFrame(startTime)` and `clock.timestampToFrame(endTime)`. For the last scene (by `endTime`), `endFrame = clock.totalFrames` to prevent off-by-one from floating-point rounding.

**Cut-boundary tie-breaking:** Two sequential scenes A and B at a `cut` boundary where `A.endTime == B.startTime` may produce `A.endFrame == B.startFrame` (no gap/overlap — ideal) or a one-frame overlap. When a one-frame overlap occurs at a cut boundary (no non-cut transitions active), `resolveFrameState` assigns the overlapping frame to scene B (the incoming scene): it returns `{ type: 'scene', primary: B, secondary: null, transitionType: null }`. The outgoing scene A does not render for that frame.

### D-11: Per-Frame Lookup via Linear Scan

**Choice:** `resolveFrameState` uses linear scan of `timeline.scenes` to find active scenes.

**Rationale:** Scene counts are small (5-15 typical, 500 max). O(n) per frame with n <= 15 is negligible relative to the ~100ms+ per-frame render cost. Cursor optimization deferred per AP-05.

### D-12: Transition Opacity Uses Linear Interpolation

**Choice:** Transition opacity is computed with linear interpolation. No easing applied to transition blending.

**Rationale:** The manifest schema (OBJ-004) defines easing on `camera_params` (for camera paths), not on transitions. Linear opacity produces clean, predictable blends. Transition easing deferred to V2.

### D-13: Unified `dip_to_black` Opacity Formula

**Choice:** `dip_to_black` uses a single formula per scene applied to the scene's full `ResolvedTransition` frame range. There is no branching between "solo," "overlap," and "non-overlap" — one formula handles all cases:

```
dip_to_black transition_out (on any scene):
  p = (frame - transitionOut.startFrame) / (transitionOut.endFrame - transitionOut.startFrame)
  p in [0, 1]
  opacity = max(0, 1 - 2*p)
  // Fades from 1->0 over the first half of the transition range.
  // Stays at 0 for the second half.

dip_to_black transition_in (on any scene):
  p = (frame - transitionIn.startFrame) / (transitionIn.endFrame - transitionIn.startFrame)
  p in [0, 1]
  opacity = max(0, 2*p - 1)
  // Stays at 0 for the first half of the transition range.
  // Fades 0->1 over the second half.
```

This formula is universal — it produces correct behavior in all contexts:

- **Symmetric overlap** (both transitions equal overlap duration): At the overlap midpoint, outgoing reaches 0 (p=0.5 in its range) and incoming is still at 0 (p=0.5 in its range). Fully black frame. Identical to a classic dip-to-black.
- **Asymmetric overlap** (A: transition_out 2s, B: transition_in 1s, overlap 1s): A reaches opacity 0 at its midpoint (1s into its 2s range), which is exactly the overlap start. A stays at 0 during the overlap. B starts its transition at the overlap start; B stays at 0 for first 0.5s of overlap, then fades in. Result: continuous fade out -> black gap -> fade in. No discontinuity.
- **Solo transition** (first scene fading in, last scene fading out, no partner): A 1s dip_to_black transition_in stays at 0 for 0.5s, then fades in over 0.5s. A 1s transition_out fades out over 0.5s, then stays at 0 for 0.5s. Consistent "dip to/from black" semantics.

**Why `max(0, ...)` instead of `clamp`:** The formula naturally stays in [0, 1] for `p in [0, 1]`. The `max(0, ...)` handles the "stays at 0" region where `1 - 2p` goes negative.

Both `primary` (outgoing) and `secondary` (incoming) are returned in `FrameState` with `transitionType: 'dip_to_black'` during overlap regions. During non-overlap portions of a transition, only the solo scene is returned (`secondary: null`).

### D-14: Crossfade Opacity Formula

**Choice:** Crossfade opacity applies **only within the overlap region** between two scenes:

```
progress p = (frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)
p in [0, 1]

Outgoing scene: opacity = 1 - p
Incoming scene: opacity = p
Sum always = 1.0 (energy-preserving blend)
```

**Outside the overlap region**, a scene's opacity is 1.0 — even if the scene's own `ResolvedTransition` frame range extends beyond the overlap (asymmetric case). A crossfade is visually meaningless without a second scene to blend with, so the non-overlap portion simply renders at full opacity. The `TRANSITION_TRUNCATED` warning (D-20) alerts the author.

**For solo crossfade** (which should not reach OBJ-038 — OBJ-016 catches `CROSSFADE_NO_ADJACENT`): defensively treated as `dip_to_black` using D-13 formulas.

### D-15: `resolveFrameState` Opacity Decision Table

**Choice:** The following table fully specifies how `resolveFrameState` determines opacity for every possible frame context. The implementer should follow this table — there are no additional branching rules.

| Frame location | Transition type | In overlap with partner? | Opacity formula | `transitionType` | `secondary` |
|---|---|---|---|---|---|
| Outside all transitions | any | N/A | 1.0 | `null` | `null` |
| In transitionIn range | crossfade | Yes | Crossfade: incoming `p`, outgoing `1-p` (D-14) | `'crossfade'` | outgoing scene |
| In transitionIn range | crossfade | No (defensive solo) | Treated as dip_to_black: `max(0, 2p - 1)` (D-13) | `'dip_to_black'` | `null` |
| In transitionIn range | dip_to_black | Yes or No | `max(0, 2p - 1)` (D-13) | `'dip_to_black'` | partner if in overlap, else `null` |
| In transitionOut range | crossfade | Yes | Crossfade: outgoing `1-p`, incoming `p` (D-14) | `'crossfade'` | incoming scene |
| In transitionOut range | crossfade | No (non-overlap or solo) | 1.0 | `null` | `null` |
| In transitionOut range | dip_to_black | Yes or No | `max(0, 1 - 2p)` (D-13) | `'dip_to_black'` | partner if in overlap, else `null` |
| In both transitionIn AND transitionOut (degenerate) | any | varies | `min(opacityIn, opacityOut)` | whichever transition is active | per context |
| Cut-boundary 1-frame overlap | cut | N/A | Incoming scene: 1.0 | `null` | `null` (outgoing dropped) |
| Gap (no active scene) | N/A | N/A | N/A | N/A | Returns `{ type: 'gap' }` |

**Key:** `p` is always progress through the specific `ResolvedTransition` frame range, computed as `(frame - transition.startFrame) / (transition.endFrame - transition.startFrame)`.

**Note on crossfade non-overlap:** When a scene has `transition_out: crossfade` but the frame is in the non-overlap portion of that range, `transitionType` is `null` (not `'crossfade'`) and opacity is 1.0. The transition is effectively invisible for those frames. This is by design — crossfade without a partner is meaningless.

### D-16: Gap Handling

**Choice:** When a frame falls between scenes (in a time gap), `resolveFrameState` returns `{ type: 'gap' }`. The orchestrator renders a black frame.

**Rationale:** OBJ-016 emits `SCENE_GAP` as a warning, not an error. Gaps are valid. Returning a discriminated union lets the orchestrator handle it cleanly.

### D-17: Normalized Time Clamping

**Choice:** `normalizedTime = clamp((frameTimestamp - scene.startTime) / scene.duration, 0, 1)`.

**Rationale:** During transition overlaps, a scene may be active slightly beyond its nominal range due to frame rounding. Clamping prevents `normalizedTime` from going negative or exceeding 1.0, which would produce invalid camera path interpolation.

### D-18: `computeTransitionOverlap` Is Symmetric About Transition Type

**Choice:** Overlap = 0 if either side is `cut` or absent. Otherwise `min(outDuration, inDuration)`. Both `crossfade` and `dip_to_black` are treated identically for overlap computation.

**Rationale:** A `cut` is instantaneous — no overlap needed. When both sides have duration, the overlap is bounded by the shorter transition.

### D-19: Transition Frame Range Formulas

**Choice:** Transition frame ranges are computed from scene frame boundaries and transition duration, clamped to the scene's own frame range:

```
transitionIn:
  startFrame = scene.startFrame
  endFrame = min(
    clock.timestampToFrame(scene.startTime + transitionIn.durationSeconds),
    scene.endFrame
  )
  frameCount = endFrame - startFrame

transitionOut:
  startFrame = max(
    clock.timestampToFrame(scene.endTime - transitionOut.durationSeconds),
    scene.startFrame
  )
  endFrame = scene.endFrame
  frameCount = endFrame - startFrame
```

**Clamping:** If a transition's duration exceeds the scene's duration, the transition frame range is clamped to the scene's frame range. When both transitions overlap within a scene (combined duration > scene duration), their frame ranges overlap. For such frames, the minimum of the two computed opacities applies (D-15 degenerate row).

### D-20: `TRANSITION_TRUNCATED` Warning

**Choice:** Emitted when a `crossfade` transition's duration exceeds the overlap with its adjacent scene, meaning the visual crossfade effect will be shorter than the declared duration. Specifically:

- If `scene[i].transition_out.type === 'crossfade'` and `scene[i].transition_out.durationSeconds > computeTransitionOverlap(scene[i], scene[i+1])`, emit:
  `"Scene '{id}': transition_out crossfade duration ({dur}s) exceeds overlap with next scene ({overlap}s). The crossfade will only be visible for {overlap}s."`

- If `scene[i].transition_in.type === 'crossfade'` and `scene[i].transition_in.durationSeconds > computeTransitionOverlap(scene[i-1], scene[i])`, emit:
  `"Scene '{id}': transition_in crossfade duration ({dur}s) exceeds overlap with previous scene ({overlap}s). The crossfade will only be visible for {overlap}s."`

**Not emitted for `dip_to_black`** because dip_to_black renders its full ramp across the entire transition range (D-13). The visual effect always spans the full declared duration — the non-overlap portion fades solo against black.

**Not emitted for solo transitions** (first/last scene) — those are expected to be solo.

### D-21: `computeTotalDuration` Reimplemented Locally

**Choice:** OBJ-038 reimplements the one-line computation `Math.max(...scenes.map(s => s.start_time + s.duration))` as a private helper function, rather than importing `computeTotalDuration` from `src/manifest/loader.ts`.

**Rationale:** Avoids a code-level dependency on OBJ-016's loader module. OBJ-038's dependency on OBJ-016 is limited to types only (`Manifest`, `Scene` from `schema.ts`). The computation is trivial and reimplementing it is cleaner than importing from a module whose primary purpose is validation.

### D-22: Zero-Frame Scene Handling

**Choice:** If a scene resolves to zero frames (`startFrame === endFrame` after `timestampToFrame` rounding):
- If `startFrame < clock.totalFrames`: force `endFrame = startFrame + 1` to ensure at least one frame. Emit `SCENE_DURATION_ADJUSTED` warning: `"Scene '{id}' resolved to zero frames and was adjusted to 1 frame."`
- If `startFrame >= clock.totalFrames`: the scene falls entirely past the end of the composition. Drop it from the resolved timeline (do not include it in `timeline.scenes`). Emit `SCENE_DURATION_ADJUSTED` warning: `"Scene '{id}' resolved to zero frames beyond the composition end and was dropped."`

## Acceptance Criteria

### Timeline Resolution — Explicit Mode

- [ ] **AC-01:** `resolveTimeline(manifest)` with no audioInfo uses `'explicit'` mode. Returns scenes with manifest `start_time` and `duration` values preserved.
- [ ] **AC-02:** In explicit mode with audioInfo provided, if `|totalSceneDuration - audioDuration| > toleranceMs`, a warning with code `AUDIO_DURATION_MISMATCH` is emitted. `resolveTimeline` does not throw.
- [ ] **AC-03:** In explicit mode with audioInfo, if durations match within tolerance (default 100ms), no warning is emitted.
- [ ] **AC-04:** `resolveTimeline` returns scenes sorted by `startTime` (ascending). Each `ResolvedScene.sceneIndex` preserves the original manifest array index.

### Timeline Resolution — Audio-Proportional Mode

- [ ] **AC-05:** `resolveTimeline(manifest, { durationSeconds: 45 })` with default config uses `'audio_proportional'` mode. `timeline.totalDuration === 45`. `timeline.totalFrames === FrameClock.fromDuration(fps, 45).totalFrames`.
- [ ] **AC-06:** In audio-proportional mode, scene durations are scaled proportionally. A manifest with 3 scenes of duration [5, 10, 5] and audio 60s (no transitions) produces resolved durations [15, 30, 15].
- [ ] **AC-07:** In audio-proportional mode with transitions, transition durations are NOT scaled. Only scene durations scale.
- [ ] **AC-08:** In audio-proportional mode, start_times are recomputed: `startTime[0] = 0`, `startTime[i] = startTime[i-1] + duration[i-1] - overlap[i-1]`.
- [ ] **AC-09:** TC-13 verification: A 5-scene manifest with a 45-second audio file, no explicit mode override, produces output where `timeline.totalDuration` is exactly 45.0 seconds (within floating-point tolerance of 1ms).
- [ ] **AC-10:** In audio-proportional mode, when manifest start_times differ from recomputed values by more than 1ms, a `START_TIMES_IGNORED` warning is emitted exactly once.
- [ ] **AC-11:** In audio-proportional mode, when manifest start_times are all 0 (matching the recomputed value for scene 0), and other scenes' start_times match recomputed values, no `START_TIMES_IGNORED` warning is emitted.

### Timeline Resolution — Audio-Cue Mode

- [ ] **AC-12:** In `'audio_cue'` mode, manifest `start_time` values are preserved in the resolved scenes.
- [ ] **AC-13:** Scene durations are computed from cue gaps: `duration[i] = start_time[i+1] - start_time[i] + overlap[i]` for non-last, `duration[last] = audioDuration - start_time[last]`.
- [ ] **AC-14:** `timeline.totalDuration` equals `audioInfo.durationSeconds` in audio_cue mode.

### Frame Range Computation

- [ ] **AC-15:** Every `ResolvedScene` has `startFrame = clock.timestampToFrame(startTime)` and `endFrame` computed from `endTime` (with the last scene by endTime having endFrame = clock.totalFrames).
- [ ] **AC-16:** `frameCount === endFrame - startFrame` for all resolved scenes.
- [ ] **AC-17:** The `FrameClock` in the timeline has `fps` matching the manifest and `totalFrames` matching `FrameClock.fromDuration(fps, totalDuration).totalFrames`.

### Transition Resolution

- [ ] **AC-18:** A scene's `transitionIn` (non-cut) has `startFrame === scene.startFrame` and `endFrame = min(clock.timestampToFrame(scene.startTime + durationSeconds), scene.endFrame)`.
- [ ] **AC-19:** A scene's `transitionOut` (non-cut) has `endFrame === scene.endFrame` and `startFrame = max(clock.timestampToFrame(scene.endTime - durationSeconds), scene.startFrame)`.
- [ ] **AC-20:** Scenes with `transition_out: { type: 'cut' }` or no `transition_out` have `transitionOut === null`.
- [ ] **AC-21:** `computeTransitionOverlap` returns `min(out.duration, in.duration)` when both are non-cut. Returns 0 when either is cut or absent.
- [ ] **AC-22:** When a transition's duration exceeds the scene's duration, the transition frame range is clamped to the scene's frame range (not extended beyond it).
- [ ] **AC-23:** When a `crossfade` transition duration exceeds the overlap with its neighbor, a `TRANSITION_TRUNCATED` warning is emitted naming the scene and the actual vs. declared durations.
- [ ] **AC-24:** `TRANSITION_TRUNCATED` is NOT emitted for `dip_to_black` transitions.

### Per-Frame Lookup — `resolveFrameState`

- [ ] **AC-25:** For a frame within a single scene (no transition active), returns `{ type: 'scene', primary: { ..., opacity: 1.0 }, secondary: null, transitionType: null }`.
- [ ] **AC-26:** For a frame in the overlap of two scenes with crossfade, returns `{ type: 'scene', primary: outgoing scene, secondary: incoming scene, transitionType: 'crossfade' }`. Outgoing opacity + incoming opacity = 1.0.
- [ ] **AC-27:** For a frame in the overlap of two scenes with symmetric dip_to_black (equal transition durations = overlap duration): at the midpoint of the overlap, outgoing opacity = 0 and incoming opacity = 0 (fully black frame). `transitionType: 'dip_to_black'`.
- [ ] **AC-28:** For a frame in a gap between scenes, returns `{ type: 'gap' }`.
- [ ] **AC-29:** `normalizedTime` is clamped to `[0, 1]` for all returned scene states.
- [ ] **AC-30:** `normalizedTime` approximately 0.0 at the scene's first frame. `normalizedTime` approaches 1.0 at the scene's last frame.
- [ ] **AC-31:** `resolveFrameState` throws `TimingError` with code `FRAME_OUT_OF_RANGE` for `frame < 0` or `frame >= timeline.totalFrames`.

### Solo Transitions

- [ ] **AC-32:** First scene with `transition_in: dip_to_black, 1s` and no overlapping previous scene: at the scene's first frame (p=0), opacity = `max(0, 2*0 - 1) = 0`. At the midpoint of the transition range (p=0.5), opacity = 0. At the last frame of the transition range (p approximately 1), opacity approximately 1. `secondary: null`, `transitionType: 'dip_to_black'`.
- [ ] **AC-33:** Last scene with `transition_out: dip_to_black, 1s` and no overlapping next scene: at the start of the transitionOut range (p=0), opacity = `max(0, 1 - 0) = 1`. At the midpoint (p=0.5), opacity = 0. At the end (p approximately 1), opacity = 0. `secondary: null`, `transitionType: 'dip_to_black'`.

### Asymmetric Transitions

- [ ] **AC-34:** Crossfade non-overlap portion: scene A has `transition_out: crossfade 2s`, overlap with B is 1s. In the first 1s of A's transitionOut range (non-overlap), A's opacity is 1.0 and `transitionType` is `null`. In the last 1s (overlap), crossfade applies with `transitionType: 'crossfade'`.
- [ ] **AC-35:** Dip_to_black asymmetric: scene A has `transition_out: dip_to_black 2s`, overlap with B is 1s. A's opacity follows `max(0, 1 - 2p)` across its full 2s transitionOut range. At p=0.5 (1s in), A's opacity = 0. During the overlap (the second 1s of A's range), A is at 0 and B is fading in per its own `max(0, 2p - 1)` formula. No opacity discontinuity.

### Cut-Boundary Tie-Breaking

- [ ] **AC-36:** When a cut-boundary produces a one-frame overlap between scene A (outgoing) and scene B (incoming), `resolveFrameState` for that frame returns `primary: B, secondary: null, transitionType: null`. Scene A does not render.

### Error Cases

- [ ] **AC-37:** `resolveTimeline` with `mode: 'audio_proportional'` and no `audioInfo` throws `TimingError` with code `NO_AUDIO`.
- [ ] **AC-38:** `resolveTimeline` with `mode: 'audio_cue'` and no `audioInfo` throws `TimingError` with code `NO_AUDIO`.
- [ ] **AC-39:** `audioInfo.durationSeconds <= 0` throws `TimingError` with code `INVALID_AUDIO_DURATION`.
- [ ] **AC-40:** `audioInfo.durationSeconds` is `NaN` or `Infinity` throws `TimingError` with code `INVALID_AUDIO_DURATION`.
- [ ] **AC-41:** In audio_proportional mode, if scaling produces a scene duration < its total transition duration, throws `TimingError` with code `SCENE_TOO_SHORT` naming the scene ID.
- [ ] **AC-42:** In audio_cue mode, if start_times are not monotonically non-decreasing, throws `TimingError` with code `INVALID_CUE_ORDER`.
- [ ] **AC-43:** In audio_cue mode, if any `start_time >= audioInfo.durationSeconds`, throws `TimingError` with code `CUE_EXCEEDS_AUDIO`.
- [ ] **AC-44:** Empty scenes array throws `TimingError` with code `NO_SCENES`.
- [ ] **AC-45:** If the resolved total duration is 0 (e.g., audio duration approaches 0 after rounding), throws `TimingError` with code `ZERO_DURATION`.

### Zero-Frame Scene Handling

- [ ] **AC-46:** A scene that resolves to zero frames (`startFrame === endFrame`) within the composition (`startFrame < clock.totalFrames`) is adjusted to 1 frame (`endFrame = startFrame + 1`) with a `SCENE_DURATION_ADJUSTED` warning.
- [ ] **AC-47:** A scene that resolves to zero frames past the composition end (`startFrame >= clock.totalFrames`) is dropped from `timeline.scenes` with a `SCENE_DURATION_ADJUSTED` warning.

### General

- [ ] **AC-48:** All functions are synchronous (no async, no I/O). Pure computation only.
- [ ] **AC-49:** The module has no side effects on import. No global state.
- [ ] **AC-50:** `geometry` and `camera` fields are passed through to `ResolvedScene` from the manifest.

## Edge Cases and Error Handling

### EC-01: Single-Scene Video

One scene, no transitions. In explicit mode: straightforward. In audio_proportional: scene duration = audio duration. In audio_cue: scene starts at its `start_time`, duration = `audioDuration - start_time`.

### EC-02: All Cut Transitions

All scenes have `transition_in/out: cut` or omitted. All overlaps = 0. Scenes are sequential. Start times in audio_proportional: `startTime[i] = sum(duration[0..i-1])`.

### EC-03: Scene Duration Shorter Than Transitions After Scaling

Audio is very short, causing scaled duration of a scene to fall below its transition durations. E.g., manifest scene has `transition_in: 1.0s` + `transition_out: 1.0s` = 2.0s minimum, but scaling produces 1.5s. Throws `SCENE_TOO_SHORT`: `"Scene 'scene_003' has resolved duration 1.5s which is shorter than its combined transition durations of 2.0s. Increase audio duration or reduce transition durations."`.

### EC-04: Audio Duration Equals Manifest Duration

In explicit mode with audio: no mismatch, no warning. In audio_proportional: scale factor = 1.0, durations unchanged. Both modes produce identical results.

### EC-05: Very Short Audio (Sub-Second)

Valid as long as scaled scene durations exceed transition durations. A 0.5s audio with one scene and no transitions: scene duration = 0.5s. Frame count at 30fps: `Math.ceil(0.5 * 30) = 15` frames.

### EC-06: Floating-Point Precision in Duration Sums

Scene durations may not sum exactly to the target audio duration due to floating-point arithmetic. The FrameClock's `fromDuration()` uses `Math.ceil()` to ensure sufficient frames. The resolver should not assert exact equality — use tolerance (1ms) for internal verification.

### EC-07: Overlapping Scenes in Explicit Mode

Scenes A and B overlap in time (per manifest start_times). This is valid if OBJ-016 validated the overlap against transition durations. The resolver preserves these overlaps. `resolveFrameState` handles the overlap region.

### EC-08: Zero-Frame Scenes

A scene with very short duration may resolve to 0 frames after `timestampToFrame` rounding. Handled per D-22: if `startFrame < clock.totalFrames`, force `endFrame = startFrame + 1` with `SCENE_DURATION_ADJUSTED` warning. If `startFrame >= clock.totalFrames`, drop the scene with warning.

### EC-09: Cue Timestamps With Transitions in Audio-Cue Mode

Cues at [0, 10, 20], overlap 0.5s between each pair, audio = 30s. Durations: [10.5, 10.5, 10]. Scene 0 ends at 10.5s, Scene 1 starts at 10.0s -> 0.5s overlap. `max(endTime) = 30.0` = audio duration.

### EC-10: `start_time: 0` for All Scenes in Audio-Cue Mode

All cues at 0 means for i < N-1: `duration[i] = 0 + overlap[i]`. Non-last scenes equal their transition overlap duration. May trigger `SCENE_TOO_SHORT` if scenes have transitions longer than the computed duration.

### EC-11: Frame at Exact Transition Boundary

A frame exactly at the start of a transition region: progress p = 0. Linear interpolation naturally handles boundaries — opacity is the initial value for the transition direction.

### EC-12: Two Scenes With Identical Start Times in Explicit Mode

Both scenes overlap for the full duration of the shorter scene. Sort stability ensures consistent ordering. `resolveFrameState` returns the earlier-sorted scene as primary, later as secondary.

### EC-13: `config.audioDurationToleranceMs` = 0

Strictest tolerance. Any difference triggers a warning. Valid but may produce false positives from floating-point arithmetic.

### EC-14: Transition Duration Exceeds Scene Duration (Degenerate Case)

A scene has transitions whose combined duration exceeds the scene duration. In explicit mode, the transition frame ranges overlap within the scene (D-19 clamping). The minimum of the two computed opacities applies (D-15 degenerate row). In audio modes, `SCENE_TOO_SHORT` error is thrown.

### EC-15: Cut-Boundary One-Frame Overlap

Two sequential scenes A, B with `A.endTime == B.startTime`, cut transitions. `timestampToFrame` may round to produce a one-frame overlap. Per D-10, the overlapping frame is assigned to B.

### EC-16: Portrait vs. Landscape

Resolution does not affect timing. The resolver operates on time and frame counts only.

### EC-17: Asymmetric Crossfade — Non-Overlap Portion

Scene A: `transition_out: crossfade 2s`. Scene B: `transition_in: crossfade 1s`. Overlap = 1s. For frames in A's transitionOut range that precede the overlap (first 1s): A's opacity = 1.0, `transitionType = null`. Crossfade ramp only applies within the overlap. `TRANSITION_TRUNCATED` warning emitted for scene A.

### EC-18: Asymmetric dip_to_black — No Discontinuity

Scene A: `transition_out: dip_to_black 2s`. Scene B: `transition_in: dip_to_black 1s`. Overlap = 1s. A's opacity follows `max(0, 1 - 2p)` across its full 2s range (p over A's transitionOut). At p=0.5 (1s mark), A's opacity = 0. During the overlap (1s-2s of A's range), A is at 0. B's opacity follows `max(0, 2p - 1)` across its 1s range. B's first 0.5s: opacity = 0. B's last 0.5s: fades from 0 to 1. Result: continuous, no discontinuity, with a ~0.5s black gap in the overlap.

### EC-19: Total Duration Resolves to Zero

In audio_proportional mode with extremely short audio (e.g., 0.001s) where `FrameClock.fromDuration` would produce 1 frame via `Math.ceil()`, or if all scenes are dropped per D-22, the resolved total duration is 0. Throws `ZERO_DURATION`.

## Test Strategy

### Unit Tests: `test/unit/engine/scene-timing.test.ts`

**Mode inference and configuration:**
1. `resolveTimeline(manifest)` with no audio -> mode is `'explicit'`.
2. `resolveTimeline(manifest, { durationSeconds: 45 })` -> mode is `'audio_proportional'`.
3. `resolveTimeline(manifest, audio, { mode: 'explicit' })` -> mode is `'explicit'` (override).
4. `resolveTimeline(manifest, audio, { mode: 'audio_cue' })` -> mode is `'audio_cue'`.

**Explicit mode:**
5. 3 sequential scenes (no overlaps, no transitions): resolved timing matches manifest exactly.
6. 3 scenes with crossfade transitions and overlapping start_times: timing preserved, transition regions computed.
7. With audioInfo matching scene duration: no warning.
8. With audioInfo differing by 200ms (> 100ms default tolerance): `AUDIO_DURATION_MISMATCH` warning.
9. With audioInfo differing by 50ms (< 100ms tolerance): no warning.
10. With custom `audioDurationToleranceMs: 0` and 1ms difference: warning emitted.

**Audio-proportional mode:**
11. 3 scenes [5, 10, 5], no transitions, audio=60s: resolved durations [15, 30, 15]. Total = 60s.
12. 5 equal-weight scenes, audio=45s: each scene = 9s. TC-13 verification.
13. Scenes with crossfade transitions: transition durations preserved, scene durations scaled, total = audio duration.
14. Scale factor < 1 (audio shorter than manifest): durations shrink.
15. Scale factor > 1 (audio longer): durations grow.
16. Scene too short after scaling: `SCENE_TOO_SHORT` error.
17. Manifest start_times differ from recomputed: `START_TIMES_IGNORED` warning emitted once.
18. Manifest start_times all 0 and matching recomputed: no `START_TIMES_IGNORED` warning.

**Audio-cue mode:**
19. Cues at [0, 10, 20], audio=30s, no transitions: durations [10, 10, 10].
20. Cues at [0, 10, 20], audio=30s, with 0.5s crossfade transitions: durations [10.5, 10.5, 10].
21. Cues not in order: `INVALID_CUE_ORDER` error.
22. Cue at 35s with audio=30s: `CUE_EXCEEDS_AUDIO` error.

**Frame range computation:**
23. At 30fps, a 10s scene: ~300 frames. `startFrame` and `endFrame` correct.
24. Last scene's `endFrame === clock.totalFrames`.
25. Adjacent non-overlapping scenes: no frame gaps or overlaps (within +/-1 frame).

**Transition resolution:**
26. `transitionIn` with 1.0s duration: `startFrame === scene.startFrame`, `endFrame` spans ~30 frames at 30fps.
27. `transitionOut` with 0.5s duration: `endFrame === scene.endFrame`, `startFrame` ~15 frames before end at 30fps.
28. `cut` transition: `transitionIn/Out === null`.
29. Transition duration exceeding scene duration: frame range clamped to scene's range.
30. `computeTransitionOverlap`: crossfade 1.0s + crossfade 0.5s -> 0.5s.
31. `computeTransitionOverlap`: crossfade 1.0s + cut -> 0.
32. `computeTransitionOverlap`: both absent -> 0.
33. `TRANSITION_TRUNCATED` warning: crossfade 2s with overlap 1s -> warning emitted.
34. `TRANSITION_TRUNCATED` NOT emitted for dip_to_black with same asymmetry.

**Per-frame lookup (`resolveFrameState`):**
35. Frame in middle of a scene, no transitions: `type: 'scene'`, opacity 1.0, `secondary: null`.
36. Frame in crossfade overlap: `transitionType: 'crossfade'`, both primary and secondary present, opacities sum to 1.0.
37. Frame at start of crossfade overlap (progress=0): outgoing opacity=1.0, incoming opacity=0.0.
38. Frame at end of crossfade overlap (progress approximately 1): outgoing opacity approximately 0.0, incoming opacity approximately 1.0.
39. Frame in symmetric dip_to_black overlap, first quarter: outgoing opacity > 0, incoming opacity = 0.
40. Frame in symmetric dip_to_black overlap, midpoint: both opacities = 0.
41. Frame in symmetric dip_to_black overlap, last quarter: outgoing opacity = 0, incoming opacity > 0.
42. Frame in gap between scenes: `type: 'gap'`.
43. Frame in solo dip_to_black transition_in (first scene): first half opacity=0, second half ramps 0->1. `transitionType: 'dip_to_black'`.
44. Frame in solo dip_to_black transition_out (last scene): first half ramps 1->0, second half opacity=0.
45. `frame < 0`: `FRAME_OUT_OF_RANGE` error.
46. `frame >= totalFrames`: `FRAME_OUT_OF_RANGE` error.

**Asymmetric transitions:**
47. Crossfade non-overlap portion: outgoing scene opacity = 1.0, `transitionType = null`.
48. Dip_to_black asymmetric (A: 2s, B: 1s, overlap 1s): A's opacity follows `max(0, 1-2p)` across full 2s range continuously. At overlap start (1s into A's transition), A is at 0. B fades in per its formula. No discontinuity.

**Cut-boundary tie-breaking:**
49. One-frame overlap at cut boundary: incoming scene B is primary, outgoing A not rendered.

**normalizedTime:**
50. First frame of scene: `normalizedTime` approximately 0.0.
51. Last frame of scene: `normalizedTime` approaches 1.0.
52. Clamped to [0, 1] even during transition overlap beyond nominal range.

**Edge cases:**
53. Single-scene video, explicit mode: one resolved scene, no transitions.
54. Single-scene video, audio-proportional: scene duration = audio duration.
55. All cut transitions, audio-proportional: sequential, no overlaps.
56. Very short audio (0.5s, 1 scene, no transitions): valid.
57. Scene rounding to zero frames within composition: `SCENE_DURATION_ADJUSTED` warning, minimum 1 frame.
58. Scene rounding to zero frames past composition end: dropped with `SCENE_DURATION_ADJUSTED` warning.

**Error cases:**
59. `mode: 'audio_proportional'` without audio: `NO_AUDIO`.
60. `mode: 'audio_cue'` without audio: `NO_AUDIO`.
61. `audioInfo.durationSeconds = 0`: `INVALID_AUDIO_DURATION`.
62. `audioInfo.durationSeconds = -1`: `INVALID_AUDIO_DURATION`.
63. `audioInfo.durationSeconds = NaN`: `INVALID_AUDIO_DURATION`.
64. `audioInfo.durationSeconds = Infinity`: `INVALID_AUDIO_DURATION`.
65. Empty scenes array: `NO_SCENES`.
66. Resolved total duration = 0: `ZERO_DURATION`.

### Integration Test: `test/integration/scene-timing.test.ts`

67. Load a valid manifest from `test/fixtures/valid-manifest.json`, create an `AudioInfo` with a known duration, pass both to `resolveTimeline()` in audio-proportional mode. Verify: `timeline.totalDuration` matches audio duration. All frame ranges are contiguous. `resolveFrameState` returns valid states for frames 0 through `totalFrames - 1`.

### Relevant Testable Claims

- **TC-06** (deterministic output): Same manifest + same audio info + same config -> identical `ResolvedTimeline`. Trivially true for pure functions, but worth asserting.
- **TC-13** (audio duration drives total video length): Test 12 directly verifies this — 5-scene manifest + 45s audio -> output exactly 45 seconds.
- **C-07** (audio synchronization): Audio_proportional and audio_cue modes satisfy this constraint.

## Integration Points

### Depends On

| Dependency | What OBJ-038 Uses |
|---|---|
| **OBJ-009** (`FrameClock`) | `FrameClock.fromDuration(fps, totalDuration)` to create the composition clock. `clock.timestampToFrame()` for converting resolved scene times to frame numbers. `FrameClock` is returned in `ResolvedTimeline`. Code-level import. |
| **OBJ-014** (Audio muxer) | **Architectural dependency only** — OBJ-038 does NOT import OBJ-014. OBJ-038's `AudioInfo` interface is designed to accept the output of OBJ-014's `probeMedia()` (`MediaProbeResult.durationSeconds`), but the caller (OBJ-035) performs the probing and passes the result to OBJ-038. The dependency in `meta.json` ensures OBJ-014 is built before OBJ-038 so the caller has `probeMedia()` available. |
| **OBJ-016** (Manifest loader) | **Types only** — imports `Manifest` and `Scene` types from `src/manifest/schema.ts` (which is OBJ-004's module). No code-level import from `src/manifest/loader.ts`. The `computeTotalDuration` logic is reimplemented locally as a private helper (D-21). |

### Consumed By

| Consumer | How It Uses OBJ-038 |
|---|---|
| **OBJ-035** (Orchestrator) | Primary consumer. After loading the manifest and probing audio, calls `resolveTimeline()` to get frame-level timing. Iterates `clock.frames()` and calls `resolveFrameState()` per frame to determine what to render. Uses `ResolvedScene.geometry` and `camera` to set up each scene's Three.js environment. |
| **OBJ-077** (Integration: full pipeline) | Indirect consumer via OBJ-035. Validates that the full pipeline (manifest -> timing -> render -> encode) produces correct output. |
| **OBJ-078** (End-to-end acceptance) | Indirect consumer. SC-01 and SC-03 depend on correct timing resolution. |

### File Placement

```
depthkit/
  src/
    engine/
      scene-timing.ts           # NEW — timing resolution module
  test/
    unit/
      engine/
        scene-timing.test.ts    # NEW — unit tests (pure, no I/O)
    integration/
      scene-timing.test.ts      # NEW — integration test with FrameClock + manifest
```

## Open Questions

### OQ-A: Should `resolveTimeline` Accept a Partial Manifest With Optional Durations?

OBJ-004 requires `duration > 0` on every scene. This means the manifest generator must always provide durations, even for audio-proportional mode (where they serve as weights). An alternative design would define a `PartialManifest` type with optional durations, resolved by OBJ-038 before full OBJ-016 validation. Rejected for V1 to avoid duplicating schema types.

### OQ-B: Should Transition Easing Be Supported in V1?

Transition opacity uses linear interpolation (D-12). Adding easing would require extending the manifest's `TransitionSchema` with an `easing` field. Deferred to V2 — linear blending is standard and produces clean results.

### OQ-C: Should `resolveFrameState` Return Camera Parameters?

Currently, `normalizedTime` is a raw linear value. The orchestrator looks up `camera_params` from the original manifest scene. This avoids coupling OBJ-038 to camera path concerns. The orchestrator has access to the manifest and can cross-reference by `sceneIndex`.

### OQ-D: Should `resolveFrameState` Support a Cursor for Sequential Access?

For the orchestrator's frame loop, a cursor that remembers the last active scene would make lookups O(1). Given small n (5-15 scenes), this is premature. Deferred per AP-05.
