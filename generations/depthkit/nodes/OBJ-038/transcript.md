# Deliberation Transcript: OBJ-038

---

## Round 1 — spec_author

Looking at OBJ-038's metadata, dependencies, and the seed document, I'll propose a complete specification for the audio sync and scene timing module.

Let me first check the current state of the relevant files to understand the project context.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-038/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json

[Tool: Glob]
  Input: {
  "pattern": "src/engine/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/manifest/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/engine/*.ts"
}

[Tool: Glob]
  Input: {
  "pattern": "**/src/manifest/schema.ts"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-038",
     3→  "description": "Audio sync and scene timing -- duration distribution algorithm per Section 8.7: audio-driven (T = audio_duration, scenes share proportionally), explicit (T = sum of scene durations + transition overlaps), or combined (explicit durations with audio mismatch warning). Timestamp-based scene boundary alignment to narration cues. Covers C-07 (audio synchronization) and TC-13 (audio duration drives total video length).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-014", "OBJ-016"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-004/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-035/output.md"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md"
}
[Tool Result]      1→# Specification: OBJ-004 — Manifest Schema Core
     2→
     3→## Summary
     4→
     5→OBJ-004 defines the Zod validation schema and loader for the depthkit manifest — the declarative JSON document that describes an entire video. This is the authoring contract between LLM manifest authors and the rendering engine. The schema enforces structural correctness (types, ranges, required fields) via Zod parsing and semantic correctness (geometry existence, camera compatibility, plane-slot matching) via a registry-backed validation pass. It satisfies C-04 (resolution/fps support) and C-10 (validate before rendering, fail fast with actionable errors).
     6→
     7→## Interface Contract
     8→
     9→### Module: `src/manifest/schema.ts`
    10→
    11→Exports Zod schemas, inferred TypeScript types, and the registry interfaces that downstream geometry/camera objectives use to register their definitions.
    12→
    13→```typescript
    14→// === Registry Interfaces ===
    15→
    16→... [truncated]
Now I have the full context from OBJ-004's verified schema spec. Let me note the critical finding from OBJ-004 E-10 and OQ-B:

- `duration` is **required** and `> 0` on every scene (Zod enforced)
- `start_time` is **required** and `>= 0`
- OBJ-004 E-10: "Audio-proportional timing is computed by the manifest *generator* before emitting the manifest"

This means OBJ-038 operates on manifests that always have resolved durations, but can **override** them when audio metadata is provided. Here is my complete proposed specification:

---

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
    | 'TRANSITION_TRUNCATED';
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
   * Ramps 0→1 during transition-in, 1→0 during transition-out.
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
       * Non-null only when two scenes' frame ranges overlap at this frame.
       * During crossfade: the incoming scene.
       * During dip_to_black: the incoming scene (both render against black).
       * null when no overlap is active.
       */
      secondary: FrameSceneState | null;
      /**
       * Active transition type during overlap, null if no transition.
       * Determines how the orchestrator composites primary + secondary:
       * - 'crossfade': alpha-blend both scenes.
       * - 'dip_to_black': render each scene independently against black,
       *   then composite (or render sequentially with black between).
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

**Rationale:** Timeline resolution is a single computation: manifest + audio → frame ranges. There is no streaming state to manage. Pure functions are trivially testable, composable, and have no hidden coupling. The `ResolvedTimeline` output is an immutable data structure consumed by OBJ-035.

### D-02: Caller Provides Audio Metadata — No I/O in This Module

**Choice:** OBJ-038 does NOT call `probeMedia()` or read files. The caller (OBJ-035 orchestrator) obtains `AudioInfo` via OBJ-014's `probeMedia()` and passes it in.

**Rationale:** Keeps the module pure — no filesystem access, no async I/O (except what the caller does). Testable with simple mock data. Respects AP-04 (don't conflate rendering with asset handling). The orchestrator already handles file resolution; audio probing naturally belongs there.

### D-03: Three Timing Modes Map to Seed Section 8.7

**Choice:**

| Section 8.7 Language | TimingMode | Behavior |
|---|---|---|
| "If audio is provided and no explicit scene durations" | `'audio_proportional'` | Scale manifest durations proportionally to fill audio length |
| "If explicit scene durations are provided" | `'explicit'` | Use manifest `start_time` and `duration` as-is |
| "If both audio and explicit durations" | `'explicit'` with `audioInfo` provided | Use manifest timing, emit `AUDIO_DURATION_MISMATCH` warning |
| "Timestamp-based scene boundary alignment to narration cues" (C-07) | `'audio_cue'` | Preserve manifest `start_time` as cue points, compute durations from gaps |

**Rationale:** Section 8.7 describes three scenarios. The third ("combined") is explicit mode with audio — the warning is sufficient. The cue mode addresses C-07's narration cue requirement.

**Relationship to OBJ-004 E-10:** OBJ-004 notes that "audio-proportional timing is computed by the manifest generator before emitting the manifest." OBJ-038 provides the algorithm for this computation. When a manifest generator pre-computes timing, the orchestrator uses `explicit` mode. When a manifest has placeholder durations (e.g., all equal weights) and audio should drive timing, the orchestrator uses `audio_proportional`. Both paths are valid.

### D-04: Default Mode Inferred from AudioInfo Presence

**Choice:** When `config.mode` is not specified:
- `audioInfo` provided → default `'audio_proportional'`
- `audioInfo` not provided → default `'explicit'`

**Rationale:** Satisfies TC-13's "automatically distributes" language. The most common audio scenario is: manifest has rough durations, audio file is the source of truth for total length.

### D-05: Manifest Durations Serve as Proportional Weights

**Choice:** In `audio_proportional` mode, each scene's manifest `duration` value is treated as a relative weight. A scene with `duration: 10` gets twice the resolved time as one with `duration: 5`.

**Rationale:** Elegant dual interpretation — `explicit` mode reads them as absolute seconds, `audio_proportional` reads them as relative weights. No schema change needed. The LLM manifest generator can set rough durations (e.g., 5, 10, 8, 12 for "short, long, medium, long" scenes) and the engine redistributes to match audio length.

### D-06: Transition Durations Are Fixed, Not Scaled

**Choice:** In `audio_proportional` and `audio_cue` modes, transition durations from the manifest are preserved as-is. Only scene content durations scale.

**Rationale:** Transitions are perceptual constants — a 0.5s crossfade feels right regardless of whether the scene is 5s or 15s. Scaling transitions proportionally would make them unnaturally short for short scenes or long for long scenes. If scaling makes a scene shorter than its combined transition durations, that's a `SCENE_TOO_SHORT` error.

### D-07: Audio-Proportional Scaling Algorithm

**Choice:** The algorithm preserves total video duration = audio duration while maintaining transition overlaps:

```
Given: scenes S[0..N-1] with manifest durations D[i], transition overlaps O[i] between S[i] and S[i+1], audio duration A.

Total video duration = sum(D'[i]) - sum(O[i]) = A
Therefore: sum(D'[i]) = A + sum(O[i])

Scale factor = (A + sum(O[i])) / sum(D[i])
D'[i] = D[i] * scale

Start times:
  startTime[0] = 0
  startTime[i] = startTime[i-1] + D'[i-1] - O[i-1]   for i > 0

Verify: max(startTime[i] + D'[i]) = A  ✓
```

**Rationale:** Overlap durations are computed from the manifest's fixed transition durations (D-06), then subtracted from the total content time to obtain the video duration. Scaling the scene durations (not the overlaps) ensures transitions are preserved while total duration matches audio.

### D-08: Audio-Cue Algorithm

**Choice:** In `audio_cue` mode:

```
Given: scenes sorted by manifest start_time (cue timestamps c[i]), overlaps O[i], audio duration A.

Duration[i] = (c[i+1] - c[i]) + O[i]   for i < N-1
Duration[N-1] = A - c[N-1]

Start times = manifest start_times (preserved).
```

**Rationale:** Cue timestamps mark when each scene becomes the primary scene. The `+ O[i]` extension on non-last scenes creates the overlap region where the transition between scenes occurs. The last scene runs from its cue to the end of audio.

**Verification:** `max(c[i] + Duration[i])` for any scene:
- Last scene: `c[N-1] + (A - c[N-1]) = A` ✓
- Non-last scene `i`: `c[i] + c[i+1] - c[i] + O[i] = c[i+1] + O[i]` — this exceeds `c[i+1]` by `O[i]`, which is the overlap with scene `i+1`. Correct.

### D-09: FrameClock Created Internally

**Choice:** `resolveTimeline()` creates a `FrameClock` via `FrameClock.fromDuration(fps, totalDuration)` and returns it in the timeline.

**Rationale:** The clock's `totalFrames` is derived from the resolved duration, which may differ from what the manifest implies (in audio modes). Creating it here ensures a single source of truth for the composition's frame count.

### D-10: Frame Boundaries via `FrameClock.timestampToFrame()`

**Choice:** Scene `startFrame` and `endFrame` are computed using `clock.timestampToFrame(startTime)` and `clock.timestampToFrame(endTime)`. For the last scene, `endFrame = clock.totalFrames` (prevents off-by-one from floating-point rounding).

**Rationale:** `timestampToFrame` uses `Math.round()` + clamping (per OBJ-009 D4), which produces the nearest frame. Clamping to the clock's range prevents out-of-bounds frames.

**Edge case — frame overlap in adjacent scenes:** Two sequential scenes A and B with `A.endTime == B.startTime` might produce `A.endFrame == B.startFrame` (no gap) or `A.endFrame == B.startFrame + 1` (one-frame overlap) depending on rounding. This is acceptable — the per-frame lookup (`resolveFrameState`) handles overlapping ranges correctly. A one-frame overlap at a `cut` boundary is resolved by giving the frame to scene B (the incoming scene).

### D-11: Per-Frame Lookup via Linear Scan

**Choice:** `resolveFrameState` uses linear scan of `timeline.scenes` to find active scenes.

**Rationale:** Scene counts are small (5-15 typical, 500 max per E-08). O(n) per frame with n ≤ 15 is negligible relative to the ~100ms+ per-frame render cost. Binary search or cursor optimization deferred per AP-05. The orchestrator may maintain its own cursor for sequential access.

### D-12: Transition Opacity Uses Linear Interpolation

**Choice:** Transition opacity is computed with linear interpolation. No easing applied to transition blending.

**Rationale:** The manifest schema (OBJ-004) defines easing on `camera_params` (for camera paths), not on transitions. Transition easing could be added in a future schema version. Linear opacity produces clean, predictable blends.

### D-13: `dip_to_black` Renders Scenes Independently Against Black

**Choice:** During a `dip_to_black` overlap, both scenes have independent opacity curves:
- Outgoing scene: opacity ramps 1→0 over first half of overlap
- Incoming scene: opacity ramps 0→1 over second half of overlap
- There is a "black moment" at the midpoint where both opacities are low

Both `primary` and `secondary` are returned in `FrameState`, with `transitionType: 'dip_to_black'`. The orchestrator renders each against a black background (not blended with each other).

**Rationale:** This matches the seed definition: "fade out then fade in." The combined effect is A fading to black, a moment of darkness, then B emerging from black. The `FrameState` gives the orchestrator all the information it needs without prescribing the exact compositing method.

**Opacity formulas during `dip_to_black` overlap (duration = d seconds, progress p ∈ [0, 1]):**
- Outgoing: `opacity = max(0, 1 - 2*p)` — reaches 0 at p=0.5
- Incoming: `opacity = max(0, 2*p - 1)` — starts at 0, reaches 1 at p=1.0

### D-14: Crossfade Opacity Formulas

**Choice:** During a `crossfade` overlap:
- Outgoing: `opacity = 1 - p` (where `p` = progress through overlap, 0→1)
- Incoming: `opacity = p`
- Sum always = 1.0 (energy-preserving blend)

**Rationale:** Standard crossfade. The orchestrator alpha-blends the two scenes.

### D-15: Solo Transitions (No Overlapping Partner)

**Choice:** When a scene has a `transition_in` or `transition_out` that is `dip_to_black` but there is no overlapping adjacent scene (e.g., first scene fading in from black, last scene fading out to black), the frame state returns:
- `type: 'scene'`, `primary` = the solo scene with ramping opacity
- `secondary: null`
- `transitionType: 'dip_to_black'`

The orchestrator renders the scene against black at the given opacity. This is valid for `dip_to_black` (OBJ-004 D-10 allows it on first/last scenes).

**For `crossfade` without an adjacent scene:** OBJ-016 catches this as `CROSSFADE_NO_ADJACENT` error, so it should never reach OBJ-038. Defensively, treat as `dip_to_black`.

### D-16: Gap Handling

**Choice:** When a frame falls between scenes (in a time gap), `resolveFrameState` returns `{ type: 'gap' }`. The orchestrator renders a black frame.

**Rationale:** OBJ-016 emits `SCENE_GAP` as a warning, not an error. Gaps are valid. Throwing would halt the render for a warning-level condition. Returning a discriminated union lets the orchestrator handle it cleanly.

### D-17: Normalized Time Clamping

**Choice:** `normalizedTime = clamp((frameTimestamp - scene.startTime) / scene.duration, 0, 1)`.

**Rationale:** During transition overlaps, a scene may be active slightly beyond its nominal range (e.g., one frame before `startTime` due to rounding). Clamping prevents `normalizedTime` from going negative or exceeding 1.0, which would produce invalid camera path interpolation.

### D-18: `computeTransitionOverlap` Is Symmetric About Transition Type

**Choice:** Overlap = 0 if either side is `cut` or absent. Otherwise `min(outDuration, inDuration)`.

**Rationale:** A `cut` is instantaneous — no overlap needed. When both sides have duration, the overlap is bounded by the shorter transition (the longer transition may extend beyond the overlap into its own scene's solo rendering time, which is valid — the transition effect runs for its full duration, but only the overlap portion involves both scenes).

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

### Timeline Resolution — Audio-Cue Mode

- [ ] **AC-10:** In `'audio_cue'` mode, manifest `start_time` values are preserved in the resolved scenes.
- [ ] **AC-11:** Scene durations are computed from cue gaps: `duration[i] = start_time[i+1] - start_time[i] + overlap[i]` for non-last, `duration[last] = audioDuration - start_time[last]`.
- [ ] **AC-12:** `timeline.totalDuration` equals `audioInfo.durationSeconds` in audio_cue mode.

### Frame Range Computation

- [ ] **AC-13:** Every `ResolvedScene` has `startFrame = clock.timestampToFrame(startTime)` and `endFrame` computed from `endTime` (with last scene's endFrame = clock.totalFrames).
- [ ] **AC-14:** `frameCount === endFrame - startFrame` for all resolved scenes.
- [ ] **AC-15:** The `FrameClock` in the timeline has `fps` matching the manifest and `totalFrames` matching `FrameClock.fromDuration(fps, totalDuration).totalFrames`.

### Transition Resolution

- [ ] **AC-16:** Scenes with `transition_in: { type: 'crossfade', duration: 1.0 }` have `transitionIn = { type: 'crossfade', durationSeconds: 1.0, startFrame, endFrame, frameCount }` where `startFrame === scene.startFrame` and the transition spans approximately 1.0 second of frames.
- [ ] **AC-17:** Scenes with `transition_out: { type: 'cut' }` or no `transition_out` have `transitionOut === null`.
- [ ] **AC-18:** `computeTransitionOverlap` returns `min(out.duration, in.duration)` when both are non-cut. Returns 0 when either is cut or absent.

### Per-Frame Lookup — `resolveFrameState`

- [ ] **AC-19:** For a frame within a single scene (no transition), returns `{ type: 'scene', primary: { ..., opacity: 1.0 }, secondary: null, transitionType: null }`.
- [ ] **AC-20:** For a frame in the overlap of two scenes with crossfade, returns `{ type: 'scene', primary: outgoing scene, secondary: incoming scene, transitionType: 'crossfade' }`. Outgoing opacity + incoming opacity = 1.0.
- [ ] **AC-21:** For a frame in the overlap of two scenes with dip_to_black, returns `transitionType: 'dip_to_black'`. At the overlap midpoint, both opacities are near 0.
- [ ] **AC-22:** For a frame in a gap between scenes, returns `{ type: 'gap' }`.
- [ ] **AC-23:** `normalizedTime` is clamped to `[0, 1]` for all returned scene states.
- [ ] **AC-24:** `normalizedTime === 0` at the scene's first frame. `normalizedTime` approaches 1.0 at the scene's last frame.
- [ ] **AC-25:** `resolveFrameState` throws `TimingError` with code `FRAME_OUT_OF_RANGE` for `frame < 0` or `frame >= timeline.totalFrames`.

### Solo Transitions

- [ ] **AC-26:** A scene's `transition_in: dip_to_black` with no overlapping previous scene: `resolveFrameState` returns `primary` with ramping opacity 0→1, `secondary: null`, `transitionType: 'dip_to_black'`.
- [ ] **AC-27:** A scene's `transition_out: dip_to_black` with no overlapping next scene: `resolveFrameState` returns `primary` with ramping opacity 1→0, `secondary: null`, `transitionType: 'dip_to_black'`.

### Error Cases

- [ ] **AC-28:** `resolveTimeline` with `mode: 'audio_proportional'` and no `audioInfo` throws `TimingError` with code `NO_AUDIO`.
- [ ] **AC-29:** `resolveTimeline` with `mode: 'audio_cue'` and no `audioInfo` throws `TimingError` with code `NO_AUDIO`.
- [ ] **AC-30:** `audioInfo.durationSeconds <= 0` throws `TimingError` with code `INVALID_AUDIO_DURATION`.
- [ ] **AC-31:** `audioInfo.durationSeconds` is `NaN` or `Infinity` throws `TimingError` with code `INVALID_AUDIO_DURATION`.
- [ ] **AC-32:** In audio_proportional mode, if scaling produces a scene duration < its total transition duration, throws `TimingError` with code `SCENE_TOO_SHORT` naming the scene ID.
- [ ] **AC-33:** In audio_cue mode, if start_times are not monotonically non-decreasing, throws `TimingError` with code `INVALID_CUE_ORDER`.
- [ ] **AC-34:** In audio_cue mode, if any `start_time >= audioInfo.durationSeconds`, throws `TimingError` with code `CUE_EXCEEDS_AUDIO`.
- [ ] **AC-35:** Empty scenes array throws `TimingError` with code `NO_SCENES`.

### General

- [ ] **AC-36:** All functions are synchronous (no async, no I/O). Pure computation only.
- [ ] **AC-37:** The module has no side effects on import. No global state.
- [ ] **AC-38:** `geometry` and `camera` fields are passed through to `ResolvedScene` from the manifest (the orchestrator needs them to set up the Three.js scene).

## Edge Cases and Error Handling

### EC-01: Single-Scene Video

One scene, no transitions. `resolveTimeline` produces a timeline with one `ResolvedScene`. In explicit mode: straightforward. In audio_proportional: scene duration = audio duration. In audio_cue: scene starts at its `start_time`, duration = `audioDuration - start_time`.

### EC-02: All Cut Transitions

All scenes have `transition_in/out: cut` or omitted. All overlaps = 0. Scenes are sequential. Start times in audio_proportional: `startTime[i] = sum(duration[0..i-1])`.

### EC-03: Scene Duration Shorter Than Transitions After Scaling

Audio is very short, causing scaled duration of a scene to fall below its transition durations. E.g., manifest scene has `transition_in: 1.0s` + `transition_out: 1.0s` = 2.0s minimum, but scaling produces 1.5s. Throws `SCENE_TOO_SHORT`: `"Scene 'scene_003' has resolved duration 1.5s which is shorter than its combined transition durations of 2.0s. Increase audio duration or reduce transition durations."`.

### EC-04: Audio Duration Equals Manifest Duration

In explicit mode with audio: no mismatch, no warning. In audio_proportional: scale factor = 1.0, durations unchanged. Both modes produce identical results.

### EC-05: Very Short Audio (Sub-Second)

Valid as long as scaled scene durations exceed transition durations. A 0.5s audio with one scene and no transitions: scene duration = 0.5s, which is valid (`duration > 0` per schema). Frame count may be very small (e.g., 15 frames at 30fps).

### EC-06: Floating-Point Precision in Duration Sums

Scene durations may not sum exactly to the target audio duration due to floating-point arithmetic. The FrameClock's `fromDuration()` uses `Math.ceil()` to ensure sufficient frames. The resolver should not assert exact equality — use tolerance (1ms) for verification assertions.

### EC-07: Overlapping Scenes in Explicit Mode

Scenes A and B overlap in time (per manifest start_times). This is valid if OBJ-016 validated the overlap against transition durations. The resolver preserves these overlaps. Frame ranges for A and B will overlap, and `resolveFrameState` handles the overlap region.

### EC-08: One-Frame Scenes

A scene with very short duration (e.g., 0.001s) may resolve to 1 frame (via `Math.round(0.001 * 30) = 0`, clamped to at least 1). `normalizedTime` for that frame = 0.0 (or 0.5 if the frame falls at the midpoint). The module does not reject this — OBJ-004 schema requires `duration > 0`, and the minimum frame count is 1.

Special handling: if `startFrame === endFrame` after rounding (scene is zero frames), force `endFrame = startFrame + 1` to ensure at least one frame. Emit `SCENE_DURATION_ADJUSTED` warning.

### EC-09: Cue Timestamps With Transitions in Audio-Cue Mode

Cues at [0, 10, 20], overlap 0.5s between each pair, audio = 30s. Durations: [10.5, 10.5, 10]. Scene 0 ends at 10.5s, Scene 1 starts at 10.0s → 0.5s overlap. Scene 1 ends at 20.5s, Scene 2 starts at 20.0s → 0.5s overlap. `max(endTime) = 30.0` = audio duration. ✓

### EC-10: `start_time: 0` for All Scenes in Audio-Cue Mode

All cues at 0 means all scenes overlap entirely. Durations are 0 + overlap (for non-last) and audioDuration (for last). This is degenerate but not invalid. The resolver computes it; the per-frame lookup handles the overlaps.

Actually, if all start_times are 0, then for i < N-1: `duration[i] = start_time[i+1] - start_time[i] + overlap[i] = 0 + overlap[i]`. This makes non-last scenes equal to their transition overlap duration. This may trigger `SCENE_TOO_SHORT` if the scene has transitions longer than its overlap. In practice this would be unusual.

### EC-11: Frame at Exact Transition Boundary

A frame exactly at the start of a transition region: opacity should be 0 (for transition_in) or 1 (for transition_out), with the transition starting from the next frame's values. The linear interpolation naturally handles this: progress = 0 at the start → opacity = initial value.

### EC-12: Two Scenes With Identical Start Times in Explicit Mode

Both scenes have the same `start_time`. Overlap = full duration of the shorter scene. If transitions justify this overlap (per OBJ-016 validation), it's valid. `resolveFrameState` returns both scenes as primary/secondary for all overlapping frames. Sort stability ensures consistent ordering.

### EC-13: `config.audioDurationToleranceMs` = 0

Strictest tolerance. Any difference between scene and audio duration triggers a warning. Valid but may produce false positives from floating-point arithmetic.

### EC-14: Transition Duration Exceeds Scene Duration (Manifest Bug)

A scene has `duration: 2.0s` but `transition_in: 1.5s` and `transition_out: 1.0s` (combined 2.5s > 2.0s). In explicit mode, the resolver preserves the manifest timing — the transition regions overlap within the scene. The per-frame lookup may produce frames that are simultaneously in both `transitionIn` and `transitionOut` range. For such frames, the lower of the two opacities applies (the scene is simultaneously fading in and fading out). This is a degenerate case; OBJ-016 should have warned about it.

In audio modes, if scaling makes this worse, `SCENE_TOO_SHORT` error is thrown.

### EC-15: Portrait vs. Landscape

Resolution does not affect timing. The resolver operates on time and frame counts, which are resolution-independent. C-04 compliance is the renderer's concern.

## Test Strategy

### Unit Tests: `test/unit/engine/scene-timing.test.ts`

**Mode inference and configuration:**
1. `resolveTimeline(manifest)` with no audio → mode is `'explicit'`.
2. `resolveTimeline(manifest, { durationSeconds: 45 })` → mode is `'audio_proportional'`.
3. `resolveTimeline(manifest, audio, { mode: 'explicit' })` → mode is `'explicit'` (override).
4. `resolveTimeline(manifest, audio, { mode: 'audio_cue' })` → mode is `'audio_cue'`.

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

**Audio-cue mode:**
17. Cues at [0, 10, 20], audio=30s, no transitions: durations [10, 10, 10].
18. Cues at [0, 10, 20], audio=30s, with 0.5s crossfade transitions: durations [10.5, 10.5, 10].
19. Cues not in order: `INVALID_CUE_ORDER` error.
20. Cue at 35s with audio=30s: `CUE_EXCEEDS_AUDIO` error.

**Frame range computation:**
21. At 30fps, a 10s scene: ~300 frames. `startFrame` and `endFrame` correct.
22. Last scene's `endFrame === clock.totalFrames`.
23. Adjacent non-overlapping scenes: no frame gaps or overlaps (within ±1 frame).

**Transition resolution:**
24. `crossfade` transition with 1.0s duration: `transitionIn` spans ~30 frames at 30fps.
25. `cut` transition: `transitionIn/Out === null`.
26. `dip_to_black` transition: resolved like crossfade (has frame range).
27. `computeTransitionOverlap`: crossfade 1.0s + crossfade 0.5s → 0.5s.
28. `computeTransitionOverlap`: crossfade 1.0s + cut → 0.
29. `computeTransitionOverlap`: both absent → 0.

**Per-frame lookup (`resolveFrameState`):**
30. Frame in middle of a scene, no transitions: `type: 'scene'`, opacity 1.0, `secondary: null`.
31. Frame in crossfade overlap: `transitionType: 'crossfade'`, both primary and secondary present, opacities sum to 1.0.
32. Frame at start of crossfade overlap (progress=0): outgoing opacity=1.0, incoming opacity=0.0.
33. Frame at end of crossfade overlap (progress=1): outgoing opacity=0.0, incoming opacity=1.0.
34. Frame in dip_to_black overlap, first half: outgoing opacity > 0, incoming opacity = 0.
35. Frame in dip_to_black overlap, midpoint: both opacities near 0.
36. Frame in dip_to_black overlap, second half: outgoing opacity = 0, incoming opacity > 0.
37. Frame in gap between scenes: `type: 'gap'`.
38. Frame in solo dip_to_black transition_in (first scene): opacity ramps 0→1, `transitionType: 'dip_to_black'`.
39. Frame in solo dip_to_black transition_out (last scene): opacity ramps 1→0.
40. `frame < 0`: `FRAME_OUT_OF_RANGE` error.
41. `frame >= totalFrames`: `FRAME_OUT_OF_RANGE` error.

**normalizedTime:**
42. First frame of scene: `normalizedTime` ≈ 0.0.
43. Last frame of scene: `normalizedTime` approaches 1.0.
44. Clamped to [0, 1] even during transition overlap beyond nominal range.

**Edge cases:**
45. Single-scene video, explicit mode: one resolved scene, no transitions.
46. Single-scene video, audio-proportional: scene duration = audio duration.
47. All cut transitions, audio-proportional: sequential, no overlaps.
48. Very short audio (0.5s, 1 scene, no transitions): valid.
49. Scene rounding to zero frames: `SCENE_DURATION_ADJUSTED` warning, minimum 1 frame.

**Error cases:**
50. `mode: 'audio_proportional'` without audio: `NO_AUDIO`.
51. `mode: 'audio_cue'` without audio: `NO_AUDIO`.
52. `audioInfo.durationSeconds = 0`: `INVALID_AUDIO_DURATION`.
53. `audioInfo.durationSeconds = -1`: `INVALID_AUDIO_DURATION`.
54. `audioInfo.durationSeconds = NaN`: `INVALID_AUDIO_DURATION`.
55. `audioInfo.durationSeconds = Infinity`: `INVALID_AUDIO_DURATION`.
56. Empty scenes array: `NO_SCENES`.

### Integration Test: `test/integration/scene-timing.test.ts`

57. Load a valid manifest from `test/fixtures/valid-manifest.json`, probe a short test audio file via OBJ-014's `probeMedia()`, pass both to `resolveTimeline()` in audio-proportional mode. Verify: `timeline.totalDuration` matches probed audio duration. All frame ranges are contiguous. `resolveFrameState` returns valid states for frames 0 through `totalFrames - 1`.

### Relevant Testable Claims

- **TC-06** (deterministic output): Same manifest + same audio info + same config → identical `ResolvedTimeline`. Trivially true for pure functions, but worth asserting.
- **TC-13** (audio duration drives total video length): Test 12 directly verifies this — 5-scene manifest + 45s audio → output exactly 45 seconds.
- **C-07** (audio synchronization): Audio_proportional and audio_cue modes satisfy this constraint.

## Integration Points

### Depends On

| Dependency | What OBJ-038 Uses |
|---|---|
| **OBJ-009** (`FrameClock`) | `FrameClock.fromDuration(fps, totalDuration)` to create the composition clock. `clock.timestampToFrame()` for converting resolved scene times to frame numbers. `FrameClock` is returned in `ResolvedTimeline`. |
| **OBJ-014** (`probeMedia`, `AudioMuxerError`) | OBJ-038 does NOT import OBJ-014 directly. The caller (OBJ-035) uses `probeMedia()` to obtain `AudioInfo.durationSeconds` and passes it to OBJ-038. OBJ-038 receives audio metadata as a plain object. |
| **OBJ-016** (`Manifest` type, `computeTotalDuration`) | Imports `Manifest` and `Scene` types from `src/manifest/schema.ts`. May use `computeTotalDuration()` from `src/manifest/loader.ts` for audio mismatch checks in explicit mode. Alternatively, reimplements the simple `max(start_time + duration)` computation. |

### Consumed By

| Consumer | How It Uses OBJ-038 |
|---|---|
| **OBJ-035** (Orchestrator) | Primary consumer. After loading the manifest and probing audio, calls `resolveTimeline()` to get frame-level timing. Iterates `clock.frames()` and calls `resolveFrameState()` per frame to determine what to render. Uses `ResolvedScene.geometry` and `camera` to set up each scene's Three.js environment. |
| **OBJ-077** (Integration: full pipeline) | Indirect consumer via OBJ-035. Validates that the full pipeline (manifest → timing → render → encode) produces correct output. |
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

OBJ-004 requires `duration > 0` on every scene. This means the manifest generator must always provide durations, even for audio-proportional mode (where they serve as weights). An alternative design would define a `PartialManifest` type with optional durations, resolved by OBJ-038 before full OBJ-016 validation. This was rejected for V1 to avoid duplicating schema types, but could be revisited if manifest generators find it burdensome to supply placeholder durations.

### OQ-B: Should Transition Easing Be Supported in V1?

Transition opacity uses linear interpolation (D-12). Adding easing (e.g., `ease_in_out` for crossfades) would require either extending the manifest's `TransitionSchema` with an `easing` field or hardcoding a default easing curve. Deferred to V2 — linear blending is standard and produces clean results.

### OQ-C: Should `resolveFrameState` Return an Easing Function for the Camera?

Currently, `normalizedTime` is a raw linear value. The `camera_params.easing` from the manifest is not applied here — it's the camera path's responsibility (OBJ-006). But the orchestrator needs to know the easing to apply it. Should OBJ-038 pass through the manifest's `camera_params` in `FrameSceneState`? Or is that the orchestrator's concern?

Current design: OBJ-038 passes through `geometry` and `camera` on `ResolvedScene`. The orchestrator looks up `camera_params` from the original manifest scene. This avoids coupling OBJ-038 to camera path concerns.

### OQ-D: Should `resolveFrameState` Support a Cursor for Sequential Access?

For the orchestrator's frame loop (frame 0, 1, 2, ...), a cursor that remembers the last active scene would make lookups O(1) instead of O(n). Given small n (5-15 scenes), this is premature. But if future manifests support hundreds of scenes, a cursor API could be added. Deferred per AP-05.

---

I believe this spec is complete and covers all the requirements from OBJ-038's description, the seed constraints (C-07, Section 8.7, Section 8.8), the testable claims (TC-13), and the integration points with OBJ-009, OBJ-014, and OBJ-016. I'd like the challenger to verify and identify any gaps or issues.

---

## Round 2 — spec_challenger

I've read the proposed spec carefully. Let me work through it systematically.

## What's Sound

The overall architecture is good:
- **Stateless pure functions (D-01, D-02)** — correct choice, makes testing trivial.
- **Three timing modes mapping to Section 8.7 (D-03)** — clean and complete.
- **Caller provides AudioInfo, no I/O (D-02)** — respects AP-04 and keeps the module testable.
- **Transition durations fixed, not scaled (D-06)** — correct perceptual reasoning.
- **FrameState discriminated union** — clean API for the orchestrator.
- **D-07 scaling algorithm** — mathematically sound, verification checks out.
- **D-08 cue algorithm** — mathematically sound.

The acceptance criteria are comprehensive and the test strategy is thorough. Now for the problems:

---

## Critical Issues

### C1: `TRANSITION_TRUNCATED` warning is declared in the type but never specified

`TimingWarning.code` includes `'TRANSITION_TRUNCATED'` but the spec never describes when this warning is emitted. No design decision, no edge case, no acceptance criterion mentions it. An implementer would have to guess what triggers it.

**Proposed fix:** Either (a) specify the condition — e.g., "emitted when a scene's transition duration exceeds the overlap with its neighbor, meaning the transition will be visually truncated at the overlap boundary" — and add an acceptance criterion, OR (b) remove it from the type union if it's not needed for V1. My preference is (a): define it as emitted when a scene's `transition_out.duration > computeTransitionOverlap(...)` or `transition_in.duration > computeTransitionOverlap(...)`, since the visual transition beyond the overlap region is effectively a solo fade (which may surprise the manifest author). Add AC for this.

### C2: Transition frame range computation formulas are missing

`ResolvedTransition` has `startFrame`, `endFrame`, `frameCount`, but the spec never gives the exact formulas. AC-16 says `startFrame === scene.startFrame` for transitionIn, but doesn't specify `endFrame`. For transitionOut, nothing at all.

An implementer must know:
- **transitionIn:** `startFrame = scene.startFrame`, `endFrame = clock.timestampToFrame(scene.startTime + transition.durationSeconds)` — is that right?
- **transitionOut:** `startFrame = clock.timestampToFrame(scene.endTime - transition.durationSeconds)`, `endFrame = scene.endFrame`?
- What if the computed transition range exceeds the scene's frame range (transition longer than scene)? Clamped?

**Proposed fix:** Add a design decision (e.g., D-19) with explicit formulas:
```
transitionIn:
  startFrame = scene.startFrame
  endFrame = min(clock.timestampToFrame(scene.startTime + durationSeconds), scene.endFrame)
  
transitionOut:
  startFrame = max(clock.timestampToFrame(scene.endTime - durationSeconds), scene.startFrame)
  endFrame = scene.endFrame
```
And add ACs verifying the clamping behavior when transition exceeds scene duration.

---

## Major Issues

### M1: Asymmetric transition + solo transition opacity formulas missing

D-13 and D-14 give opacity formulas for the **overlap region** between two scenes. D-15 mentions solo transitions with "ramping opacity" but gives no formula. There are actually three distinct opacity contexts an implementer needs to handle:

1. **Overlap region** (two scenes active): D-13/D-14 cover this ✓
2. **Solo transition** (first scene's transition_in from black, last scene's transition_out to black): D-15 mentions but doesn't specify. Is it `opacity = p` for fade-in and `opacity = 1 - p` for fade-out, where `p` = progress through the transition's frame range?
3. **Non-overlap portion of an asymmetric transition**: Scene A has `transition_out: 2s`, scene B has `transition_in: 1s`, overlap = 1s. For the first 1s of A's transition_out, A is fading but B hasn't started yet. What opacity does A have? Is it fading against black? Or does A remain at full opacity until the overlap begins?

Case 3 is the most ambiguous. The spec's D-18 says "the longer transition may extend beyond the overlap into its own scene's solo rendering time" but doesn't say what that means for opacity.

**Proposed fix:** Add a design decision specifying:
- Solo transitions (case 2): explicit opacity formulas (simple ramp).
- Asymmetric transitions (case 3): specify whether the non-overlap portion of the longer transition fades solo (against black) or remains at full opacity. My recommendation: the transition opacity ramp spans its full `ResolvedTransition` frame range regardless of overlap. During the non-overlap portion, only one scene renders at reduced opacity (which visually matches `dip_to_black` but may look odd for `crossfade`). Alternatively: for `crossfade`, the opacity ramp only applies within the overlap; outside the overlap, opacity is 1.0. State the choice explicitly.

### M2: `audio_proportional` mode silently discards manifest `start_time` values — not documented

D-07's algorithm recomputes `startTime[0] = 0, startTime[i] = startTime[i-1] + D'[i-1] - O[i-1]`. This means manifest `start_time` values are completely ignored. An LLM author who sets `start_time` values AND expects proportional scaling will be surprised.

**Proposed fix:** Add to D-07: "In `audio_proportional` mode, manifest `start_time` values are ignored. Start times are recomputed sequentially from scene 0. If the manifest author needs to preserve specific start times, use `audio_cue` mode." Also add a `START_TIMES_IGNORED` warning (or use `SCENE_DURATION_ADJUSTED`) when the recomputed start times differ from the manifest values.

### M3: Whether to import or reimplement `computeTotalDuration` is left to the implementer

The "Depends On" table says: "May use `computeTotalDuration()` from `src/manifest/loader.ts`. Alternatively, reimplements the simple `max(start_time + duration)` computation."

A spec should not leave this choice to the implementer — it affects the import graph and coupling.

**Proposed fix:** Pick one. Since the function is a one-liner (`Math.max(...scenes.map(s => s.start_time + s.duration))`), I recommend reimplementing it locally as a private helper. This avoids importing from `loader.ts` (which is primarily a validation module), keeping OBJ-038's dependency on OBJ-016 limited to types only. State this in the design decisions.

### M4: `resolveFrameState` does not specify tie-breaking for overlapping scenes at cut boundaries

D-10 notes: "A one-frame overlap at a `cut` boundary is resolved by giving the frame to scene B (the incoming scene)." But `resolveFrameState`'s return type only has `primary` and `secondary`. How does "giving the frame to scene B" manifest in the return value?

**Proposed fix:** State explicitly: when a frame falls at a `cut` boundary where two scenes' frame ranges overlap by exactly 1 frame, `resolveFrameState` returns `{ type: 'scene', primary: incomingScene, secondary: null, transitionType: null }` — the outgoing scene is not rendered for that frame. Add an AC for this.

---

## Minor Issues

### m1: EC-08 zero-frame scene fix-up imprecision

EC-08 says "if `startFrame === endFrame` after rounding (scene is zero frames), force `endFrame = startFrame + 1`." But what if `startFrame === clock.totalFrames`? Then `startFrame + 1` exceeds the frame range. This edge case isn't addressed.

**Proposed fix:** Add: "If `startFrame >= clock.totalFrames`, the scene is entirely past the end of the composition and is dropped with a `SCENE_DURATION_ADJUSTED` warning. Otherwise, `endFrame = min(startFrame + 1, clock.totalFrames)`."

### m2: OBJ-014 dependency is architectural only — could confuse implementers

The meta.json lists `OBJ-014` as a dependency, but the spec says "OBJ-038 does NOT import OBJ-014 directly." This could confuse someone checking the dependency graph.

**Proposed fix:** Add a note in "Depends On" table: "OBJ-014 is an architectural dependency — OBJ-038's `AudioInfo` interface is designed to accept the output of `probeMedia()`, but there is no code-level import. The dependency ensures OBJ-014 is built before OBJ-038 so the caller (OBJ-035) has `probeMedia()` available."

### m3: `computeTransitionOverlap` — should it handle `dip_to_black` differently from `crossfade`?

The spec treats both identically for overlap computation (D-18). But the seed's transition vocabulary defines `dip_to_black` as "fade out then fade in" — which could in theory NOT require overlap (scene A fades to black entirely, then scene B fades in from black). OBJ-004 D-10 explicitly allows `dip_to_black` without an adjacent scene. Should `dip_to_black` between two adjacent scenes have zero overlap (sequential with black gap) or have overlap (simultaneous rendering)?

The spec's D-13 defines `dip_to_black` with overlap (both scenes rendered against black simultaneously). This is a valid choice, but it means `dip_to_black` transitions between adjacent scenes will never produce a fully-black frame (outgoing hits 0 at p=0.5, incoming starts from 0 at p=0.5, so at the midpoint both are 0 — OK, there IS a black moment). So this actually works. Never mind, this is fine. Withdrawing this as an issue.

### m4: Vocabulary: `TimingMode` values use underscores (`audio_proportional`, `audio_cue`)

This is consistent with the seed's vocabulary style (e.g., `ease_in_out`, `dip_to_black`). Fine.

---

## Summary

| # | Severity | Issue | 
|---|----------|-------|
| C1 | Critical | `TRANSITION_TRUNCATED` warning declared but never specified |
| C2 | Critical | Transition frame range computation formulas missing |
| M1 | Major | Solo and asymmetric transition opacity formulas missing |
| M2 | Major | `audio_proportional` silently discards `start_time` — undocumented |
| M3 | Major | Import vs. reimplement `computeTotalDuration` left to implementer |
| M4 | Major | Cut-boundary tie-breaking not reflected in return value |
| m1 | Minor | Zero-frame scene fix-up doesn't handle edge at end of composition |
| m2 | Minor | OBJ-014 architectural dependency should be explicitly noted |
| m3 | Minor | (Withdrawn) |

Please revise the spec addressing at minimum C1, C2, M1-M4. I'll verify the fixes in the next round.

---

## Round 3 — spec_author

Here is the revised specification addressing all issues raised by the challenger.

---

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
   * Ramps 0→1 during transition-in, 1→0 during transition-out.
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

**Rationale:** Timeline resolution is a single computation: manifest + audio → frame ranges. There is no streaming state to manage. Pure functions are trivially testable, composable, and have no hidden coupling. The `ResolvedTimeline` output is an immutable data structure consumed by OBJ-035.

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
- `audioInfo` provided → default `'audio_proportional'`
- `audioInfo` not provided → default `'explicit'`

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

Verify: max(startTime[i] + D'[i]) = A  ✓
```

If the recomputed start times differ from the manifest's `start_time` values by more than 1ms for any scene, a `START_TIMES_IGNORED` warning is emitted: `"In audio_proportional mode, manifest start_time values are ignored. Start times have been recomputed sequentially. To preserve specific start times, use audio_cue mode."` This warning is emitted at most once, regardless of how many scenes are affected.

**Rationale:** Proportional scaling produces new durations that make the original start_times meaningless. Recomputing sequentially is the only consistent approach. The warning alerts authors who may have expected their start_times to be preserved.

### D-08: Audio-Cue Algorithm

**Choice:** In `audio_cue` mode:

```
Given: scenes sorted by manifest start_time (cue timestamps c[i]), overlaps O[i], audio duration A.

Duration[i] = (c[i+1] - c[i]) + O[i]   for i < N-1
Duration[N-1] = A - c[N-1]

Start times = manifest start_times (preserved).
```

**Verification:** `max(c[i] + Duration[i])` for any scene:
- Last scene: `c[N-1] + (A - c[N-1]) = A` ✓
- Non-last scene `i`: `c[i] + c[i+1] - c[i] + O[i] = c[i+1] + O[i]` — exceeds `c[i+1]` by `O[i]`, which is the overlap with scene `i+1`. Correct.

### D-09: FrameClock Created Internally

**Choice:** `resolveTimeline()` creates a `FrameClock` via `FrameClock.fromDuration(fps, totalDuration)` and returns it in the timeline.

**Rationale:** The clock's `totalFrames` is derived from the resolved duration, which may differ from what the manifest implies (in audio modes). Creating it here ensures a single source of truth for the composition's frame count.

### D-10: Frame Boundaries via `FrameClock.timestampToFrame()`

**Choice:** Scene `startFrame` and `endFrame` are computed using `clock.timestampToFrame(startTime)` and `clock.timestampToFrame(endTime)`. For the last scene (by `endTime`), `endFrame = clock.totalFrames` to prevent off-by-one from floating-point rounding.

**Rationale:** `timestampToFrame` uses `Math.round()` + clamping (per OBJ-009 D4), which produces the nearest frame.

**Cut-boundary tie-breaking:** Two sequential scenes A and B at a `cut` boundary where `A.endTime == B.startTime` may produce `A.endFrame == B.startFrame` (no gap/overlap — ideal) or a one-frame overlap. When a one-frame overlap occurs at a cut boundary (no non-cut transitions active), `resolveFrameState` assigns the overlapping frame to scene B (the incoming scene): it returns `{ type: 'scene', primary: B, secondary: null, transitionType: null }`. The outgoing scene A does not render for that frame.

### D-11: Per-Frame Lookup via Linear Scan

**Choice:** `resolveFrameState` uses linear scan of `timeline.scenes` to find active scenes.

**Rationale:** Scene counts are small (5-15 typical, 500 max). O(n) per frame with n ≤ 15 is negligible relative to the ~100ms+ per-frame render cost. Cursor optimization deferred per AP-05.

### D-12: Transition Opacity Uses Linear Interpolation

**Choice:** Transition opacity is computed with linear interpolation. No easing applied to transition blending.

**Rationale:** The manifest schema (OBJ-004) defines easing on `camera_params` (for camera paths), not on transitions. Linear opacity produces clean, predictable blends. Transition easing deferred to V2.

### D-13: `dip_to_black` Opacity During Overlap

**Choice:** During a `dip_to_black` overlap between two scenes, both scenes render against black with independent opacity curves:

```
progress p = (frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)
p ∈ [0, 1]

Outgoing scene: opacity = max(0, 1 - 2*p)   — reaches 0 at p=0.5
Incoming scene: opacity = max(0, 2*p - 1)    — starts at 0, reaches 1 at p=1.0
```

At the midpoint (p=0.5), both opacities are 0 — a fully black frame. The orchestrator renders each scene independently against a black background.

Both `primary` (outgoing) and `secondary` (incoming) are returned in `FrameState` with `transitionType: 'dip_to_black'`.

### D-14: Crossfade Opacity During Overlap

**Choice:** During a `crossfade` overlap:

```
progress p = (frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)
p ∈ [0, 1]

Outgoing scene: opacity = 1 - p
Incoming scene: opacity = p
Sum always = 1.0 (energy-preserving blend)
```

The orchestrator alpha-blends the two scenes.

**Crossfade opacity applies ONLY within the overlap region.** Outside the overlap, a scene's opacity is 1.0 — even if the scene's own `ResolvedTransition` frame range extends beyond the overlap. See D-20 for full treatment of asymmetric transitions.

### D-15: Solo Transitions (No Overlapping Partner)

**Choice:** When a scene has a `dip_to_black` transition with no overlapping adjacent scene (first scene's transition_in, or last scene's transition_out), the frame state returns:
- `type: 'scene'`, `primary` = the solo scene with ramping opacity
- `secondary: null`
- `transitionType: 'dip_to_black'`

**Solo transition opacity formulas:**

```
Solo transition_in (dip_to_black):
  transition frame range: [scene.transitionIn.startFrame, scene.transitionIn.endFrame)
  progress p = (frame - startFrame) / (endFrame - startFrame), p ∈ [0, 1]
  opacity = p  (ramps 0→1: fade in from black)

Solo transition_out (dip_to_black):
  transition frame range: [scene.transitionOut.startFrame, scene.transitionOut.endFrame)
  progress p = (frame - startFrame) / (endFrame - startFrame), p ∈ [0, 1]
  opacity = 1 - p  (ramps 1→0: fade out to black)
```

The orchestrator renders the scene against black at the given opacity.

**For `crossfade` without an adjacent scene:** OBJ-016 catches this as `CROSSFADE_NO_ADJACENT` error, so it should never reach OBJ-038. Defensively, if encountered, treat as `dip_to_black` with the same opacity formulas.

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

**Clamping:** If a transition's duration exceeds the scene's duration, the transition frame range is clamped to the scene's frame range. This means:
- A transitionIn that exceeds scene duration: `endFrame` clamps to `scene.endFrame`, so the transition spans the entire scene.
- A transitionOut that exceeds scene duration: `startFrame` clamps to `scene.startFrame`, so the transition spans the entire scene.
- When both transitions overlap within a scene (combined duration > scene duration), their frame ranges overlap. For such frames, the minimum of the two computed opacities applies (the scene is simultaneously fading in and fading out). This is a degenerate case that OBJ-016 should have warned about, but the module handles it gracefully.

### D-20: Asymmetric Transitions — Non-Overlap Portion

**Choice:** When adjacent scenes have asymmetric transition durations (e.g., scene A has `transition_out: 2s`, scene B has `transition_in: 1s`, overlap = 1s), the non-overlap portion of the longer transition behaves as follows:

- **For `crossfade`:** Opacity is 1.0 outside the overlap region. The crossfade ramp applies ONLY within the overlap. Scene A's transition_out covers 2s of frames, but only the last 1s (the overlap) has reduced opacity. The first 1s of A's transition_out region renders at full opacity. This is visually correct — a crossfade is meaningless without a second scene to blend with.

- **For `dip_to_black`:** Opacity ramps across the full transition frame range, including the non-overlap portion. Scene A's 2s dip_to_black starts fading at the beginning of its transition_out region. During the first 1s (non-overlap), A fades solo against black. During the last 1s (overlap), both A and B render against black with their respective opacities.

**Implementation detail for `resolveFrameState`:** The function checks whether a frame falls in a transition region (via `ResolvedTransition` frame ranges) and whether it falls in an overlap region (where two scenes' frame ranges intersect). The combination determines opacity:

| Frame location | Transition type | Overlap? | Behavior |
|---|---|---|---|
| In transitionIn range | crossfade | Yes (overlap with prev scene) | Crossfade opacity (D-14) |
| In transitionIn range | crossfade | No (solo — shouldn't happen per OBJ-016, defensive) | opacity = 1.0 |
| In transitionIn range | dip_to_black | Yes (overlap with prev scene) | dip_to_black overlap opacity (D-13) |
| In transitionIn range | dip_to_black | No (solo, e.g., first scene) | Solo ramp opacity = p (D-15) |
| In transitionOut range | crossfade | Yes (overlap with next scene) | Crossfade opacity (D-14) |
| In transitionOut range | crossfade | No (non-overlap portion of asymmetric) | opacity = 1.0 |
| In transitionOut range | dip_to_black | Yes (overlap with next scene) | dip_to_black overlap opacity (D-13) |
| In transitionOut range | dip_to_black | No (solo or non-overlap portion) | Solo ramp opacity = 1 - p (D-15) |
| Outside all transitions | any | N/A | opacity = 1.0 |

**Note on crossfade non-overlap:** When scene A has `transition_out: crossfade, 2s` and scene B has `transition_in: crossfade, 1s` with overlap = 1s, frames in the non-overlap portion of A's transition_out (the first 1s) render A at opacity 1.0. The `TRANSITION_TRUNCATED` warning (D-21) alerts the manifest author that the visual crossfade effect is shorter than the declared duration.

### D-21: `TRANSITION_TRUNCATED` Warning

**Choice:** Emitted when a scene's transition duration exceeds the overlap with its adjacent scene, meaning the visual transition effect will be shorter than the declared duration. Specifically:

- If `scene[i].transition_out.durationSeconds > computeTransitionOverlap(scene[i], scene[i+1])` and the transition is `crossfade`, emit:
  `"Scene '{id}': transition_out crossfade duration ({dur}s) exceeds overlap with next scene ({overlap}s). The crossfade will only be visible for {overlap}s."`

- If `scene[i].transition_in.durationSeconds > computeTransitionOverlap(scene[i-1], scene[i])` and the transition is `crossfade`, emit:
  `"Scene '{id}': transition_in crossfade duration ({dur}s) exceeds overlap with previous scene ({overlap}s). The crossfade will only be visible for {overlap}s."`

**Not emitted for `dip_to_black`** because dip_to_black renders its full ramp as a solo fade in the non-overlap portion (D-20). The visual effect spans the full declared duration.

**Not emitted for solo transitions** (first/last scene) — those are expected to be solo.

**Rationale:** A manifest author declaring a 2s crossfade that only visually fades for 1s may be surprised. The warning tells them to either increase overlap (adjust start_times) or reduce the transition duration.

### D-22: `computeTotalDuration` Reimplemented Locally

**Choice:** OBJ-038 reimplements the one-line computation `Math.max(...scenes.map(s => s.start_time + s.duration))` as a private helper function, rather than importing `computeTotalDuration` from `src/manifest/loader.ts`.

**Rationale:** Avoids a code-level dependency on OBJ-016's loader module, which is primarily a validation module. OBJ-038's dependency on OBJ-016 is limited to types only (`Manifest`, `Scene` from `schema.ts`). The computation is trivial — one line — and reimplementing it is cleaner than importing from a module whose primary purpose is different.

### D-23: Zero-Frame Scene Handling

**Choice:** If a scene resolves to zero frames (`startFrame === endFrame` after `timestampToFrame` rounding):
- If `startFrame < clock.totalFrames`: force `endFrame = startFrame + 1` to ensure at least one frame. Emit `SCENE_DURATION_ADJUSTED` warning: `"Scene '{id}' resolved to zero frames and was adjusted to 1 frame."`
- If `startFrame >= clock.totalFrames`: the scene falls entirely past the end of the composition. Drop it from the resolved timeline (do not include it in `timeline.scenes`). Emit `SCENE_DURATION_ADJUSTED` warning: `"Scene '{id}' resolved to zero frames beyond the composition end and was dropped."`

**Rationale:** A zero-frame scene cannot be rendered. Adjusting to 1 frame preserves the scene's presence. Dropping scenes past the end prevents out-of-range frame access.

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
- [ ] **AC-24:** `TRANSITION_TRUNCATED` is NOT emitted for `dip_to_black` transitions (they render their full duration as solo fades).

### Per-Frame Lookup — `resolveFrameState`

- [ ] **AC-25:** For a frame within a single scene (no transition), returns `{ type: 'scene', primary: { ..., opacity: 1.0 }, secondary: null, transitionType: null }`.
- [ ] **AC-26:** For a frame in the overlap of two scenes with crossfade, returns `{ type: 'scene', primary: outgoing scene, secondary: incoming scene, transitionType: 'crossfade' }`. Outgoing opacity + incoming opacity = 1.0.
- [ ] **AC-27:** For a frame in the overlap of two scenes with dip_to_black, returns `transitionType: 'dip_to_black'`. At the overlap midpoint, both opacities are 0 (fully black frame).
- [ ] **AC-28:** For a frame in a gap between scenes, returns `{ type: 'gap' }`.
- [ ] **AC-29:** `normalizedTime` is clamped to `[0, 1]` for all returned scene states.
- [ ] **AC-30:** `normalizedTime` ≈ 0.0 at the scene's first frame. `normalizedTime` approaches 1.0 at the scene's last frame.
- [ ] **AC-31:** `resolveFrameState` throws `TimingError` with code `FRAME_OUT_OF_RANGE` for `frame < 0` or `frame >= timeline.totalFrames`.

### Solo Transitions

- [ ] **AC-32:** First scene with `transition_in: dip_to_black` and no overlapping previous scene: `resolveFrameState` returns `primary` with opacity ramping 0→1 (p), `secondary: null`, `transitionType: 'dip_to_black'`.
- [ ] **AC-33:** Last scene with `transition_out: dip_to_black` and no overlapping next scene: `resolveFrameState` returns `primary` with opacity ramping 1→0 (1-p), `secondary: null`, `transitionType: 'dip_to_black'`.

### Asymmetric Transitions

- [ ] **AC-34:** Crossfade non-overlap portion: scene A has `transition_out: crossfade 2s`, overlap with B is 1s. In the first 1s of A's transitionOut range (non-overlap), A's opacity is 1.0. In the last 1s (overlap), crossfade applies.
- [ ] **AC-35:** Dip_to_black non-overlap portion: scene A has `transition_out: dip_to_black 2s`, overlap with B is 1s. In the first 1s (non-overlap), A's opacity ramps down solo. In the last 1s (overlap), dip_to_black overlap formulas apply.

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

### General

- [ ] **AC-45:** All functions are synchronous (no async, no I/O). Pure computation only.
- [ ] **AC-46:** The module has no side effects on import. No global state.
- [ ] **AC-47:** `geometry` and `camera` fields are passed through to `ResolvedScene` from the manifest.

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

A scene with very short duration may resolve to 0 frames after `timestampToFrame` rounding. Handled per D-23: if `startFrame < clock.totalFrames`, force `endFrame = startFrame + 1` with `SCENE_DURATION_ADJUSTED` warning. If `startFrame >= clock.totalFrames`, drop the scene with warning.

### EC-09: Cue Timestamps With Transitions in Audio-Cue Mode

Cues at [0, 10, 20], overlap 0.5s between each pair, audio = 30s. Durations: [10.5, 10.5, 10]. Scene 0 ends at 10.5s, Scene 1 starts at 10.0s → 0.5s overlap. `max(endTime) = 30.0` = audio duration. ✓

### EC-10: `start_time: 0` for All Scenes in Audio-Cue Mode

All cues at 0 means for i < N-1: `duration[i] = 0 + overlap[i]`. Non-last scenes equal their transition overlap duration. May trigger `SCENE_TOO_SHORT` if scenes have transitions longer than the computed duration.

### EC-11: Frame at Exact Transition Boundary

A frame exactly at the start of a transition region: progress p = 0. For transition_in: opacity = 0 (for dip_to_black solo) or depends on crossfade context. Linear interpolation naturally handles boundaries.

### EC-12: Two Scenes With Identical Start Times in Explicit Mode

Both scenes overlap for the full duration of the shorter scene. Sort stability ensures consistent ordering. `resolveFrameState` returns the earlier-sorted scene as primary, later as secondary.

### EC-13: `config.audioDurationToleranceMs` = 0

Strictest tolerance. Any difference triggers a warning. Valid but may produce false positives from floating-point arithmetic.

### EC-14: Transition Duration Exceeds Scene Duration (Degenerate Case)

A scene has transitions whose combined duration exceeds the scene duration. In explicit mode, the transition frame ranges overlap within the scene (D-19 clamping). The minimum of the two computed opacities applies. In audio modes, `SCENE_TOO_SHORT` error is thrown.

### EC-15: Cut-Boundary One-Frame Overlap

Two sequential scenes A, B with `A.endTime == B.startTime`, cut transitions. `timestampToFrame` may round to produce `A.endFrame == B.startFrame + 1` (one-frame overlap). Per D-10, the overlapping frame is assigned to B. A does not render for that frame.

### EC-16: Portrait vs. Landscape

Resolution does not affect timing. The resolver operates on time and frame counts only.

### EC-17: Asymmetric Crossfade — Non-Overlap Portion

Scene A: `transition_out: crossfade 2s`. Scene B: `transition_in: crossfade 1s`. Overlap = 1s. For frames in A's transitionOut range that precede the overlap (first 1s): A's opacity = 1.0. Crossfade ramp only applies within the overlap. `TRANSITION_TRUNCATED` warning emitted for scene A.

### EC-18: Asymmetric dip_to_black — Non-Overlap Portion

Scene A: `transition_out: dip_to_black 2s`. Scene B: `transition_in: dip_to_black 1s`. Overlap = 1s. For frames in A's transitionOut range that precede the overlap (first 1s): A fades solo against black (opacity ramps from 1 toward ~0.5). During the overlap (second 1s): dip_to_black overlap formulas apply. No `TRANSITION_TRUNCATED` warning for dip_to_black.

## Test Strategy

### Unit Tests: `test/unit/engine/scene-timing.test.ts`

**Mode inference and configuration:**
1. `resolveTimeline(manifest)` with no audio → mode is `'explicit'`.
2. `resolveTimeline(manifest, { durationSeconds: 45 })` → mode is `'audio_proportional'`.
3. `resolveTimeline(manifest, audio, { mode: 'explicit' })` → mode is `'explicit'` (override).
4. `resolveTimeline(manifest, audio, { mode: 'audio_cue' })` → mode is `'audio_cue'`.

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
25. Adjacent non-overlapping scenes: no frame gaps or overlaps (within ±1 frame).

**Transition resolution:**
26. `transitionIn` with 1.0s duration: `startFrame === scene.startFrame`, `endFrame` spans ~30 frames at 30fps.
27. `transitionOut` with 0.5s duration: `endFrame === scene.endFrame`, `startFrame` ~15 frames before end at 30fps.
28. `cut` transition: `transitionIn/Out === null`.
29. Transition duration exceeding scene duration: frame range clamped to scene's range.
30. `computeTransitionOverlap`: crossfade 1.0s + crossfade 0.5s → 0.5s.
31. `computeTransitionOverlap`: crossfade 1.0s + cut → 0.
32. `computeTransitionOverlap`: both absent → 0.
33. `TRANSITION_TRUNCATED` warning: crossfade 2s with overlap 1s → warning emitted.
34. `TRANSITION_TRUNCATED` NOT emitted for dip_to_black with same asymmetry.

**Per-frame lookup (`resolveFrameState`):**
35. Frame in middle of a scene, no transitions: `type: 'scene'`, opacity 1.0, `secondary: null`.
36. Frame in crossfade overlap: `transitionType: 'crossfade'`, both primary and secondary present, opacities sum to 1.0.
37. Frame at start of crossfade overlap (progress=0): outgoing opacity=1.0, incoming opacity=0.0.
38. Frame at end of crossfade overlap (progress≈1): outgoing opacity≈0.0, incoming opacity≈1.0.
39. Frame in dip_to_black overlap, first half: outgoing opacity > 0, incoming opacity = 0.
40. Frame in dip_to_black overlap, midpoint: both opacities = 0.
41. Frame in dip_to_black overlap, second half: outgoing opacity = 0, incoming opacity > 0.
42. Frame in gap between scenes: `type: 'gap'`.
43. Frame in solo dip_to_black transition_in (first scene): opacity ramps 0→1, `transitionType: 'dip_to_black'`.
44. Frame in solo dip_to_black transition_out (last scene): opacity ramps 1→0.
45. `frame < 0`: `FRAME_OUT_OF_RANGE` error.
46. `frame >= totalFrames`: `FRAME_OUT_OF_RANGE` error.

**Asymmetric transitions:**
47. Crossfade non-overlap portion: outgoing scene opacity = 1.0.
48. Dip_to_black non-overlap portion: outgoing scene opacity ramps solo.

**Cut-boundary tie-breaking:**
49. One-frame overlap at cut boundary: incoming scene B is primary, outgoing A not rendered.

**normalizedTime:**
50. First frame of scene: `normalizedTime` ≈ 0.0.
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

### Integration Test: `test/integration/scene-timing.test.ts`

66. Load a valid manifest from `test/fixtures/valid-manifest.json`, create an `AudioInfo` with a known duration, pass both to `resolveTimeline()` in audio-proportional mode. Verify: `timeline.totalDuration` matches audio duration. All frame ranges are contiguous. `resolveFrameState` returns valid states for frames 0 through `totalFrames - 1`.

### Relevant Testable Claims

- **TC-06** (deterministic output): Same manifest + same audio info + same config → identical `ResolvedTimeline`. Trivially true for pure functions, but worth asserting.
- **TC-13** (audio duration drives total video length): Test 12 directly verifies this — 5-scene manifest + 45s audio → output exactly 45 seconds.
- **C-07** (audio synchronization): Audio_proportional and audio_cue modes satisfy this constraint.

## Integration Points

### Depends On

| Dependency | What OBJ-038 Uses |
|---|---|
| **OBJ-009** (`FrameClock`) | `FrameClock.fromDuration(fps, totalDuration)` to create the composition clock. `clock.timestampToFrame()` for converting resolved scene times to frame numbers. `FrameClock` is returned in `ResolvedTimeline`. Code-level import. |
| **OBJ-014** (Audio muxer) | **Architectural dependency only** — OBJ-038 does NOT import OBJ-014. OBJ-038's `AudioInfo` interface is designed to accept the output of OBJ-014's `probeMedia()` (`MediaProbeResult.durationSeconds`), but the caller (OBJ-035) performs the probing and passes the result to OBJ-038. The dependency in `meta.json` ensures OBJ-014 is built before OBJ-038 so the caller has `probeMedia()` available. |
| **OBJ-016** (Manifest loader) | **Types only** — imports `Manifest` and `Scene` types from `src/manifest/schema.ts` (which is OBJ-004's module). No code-level import from `src/manifest/loader.ts`. The `computeTotalDuration` logic is reimplemented locally as a private helper (D-22). |

### Consumed By

| Consumer | How It Uses OBJ-038 |
|---|---|
| **OBJ-035** (Orchestrator) | Primary consumer. After loading the manifest and probing audio, calls `resolveTimeline()` to get frame-level timing. Iterates `clock.frames()` and calls `resolveFrameState()` per frame to determine what to render. Uses `ResolvedScene.geometry` and `camera` to set up each scene's Three.js environment. |
| **OBJ-077** (Integration: full pipeline) | Indirect consumer via OBJ-035. Validates that the full pipeline (manifest → timing → render → encode) produces correct output. |
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

---

I believe this revision addresses all issues raised:

- **C1** → D-21 fully specifies `TRANSITION_TRUNCATED`: when it's emitted, what it says, and that it's NOT emitted for dip_to_black. AC-23 and AC-24 cover it.
- **C2** → D-19 provides explicit formulas for transitionIn/Out frame ranges with clamping behavior. AC-18, AC-19, AC-22 cover it.
- **M1** → D-15 has explicit solo opacity formulas. D-20 has the full asymmetric transition table covering all combinations of transition type × overlap/non-overlap. AC-32–35 cover it.
- **M2** → D-07 now explicitly states start_times are ignored and emits `START_TIMES_IGNORED` warning. `START_TIMES_IGNORED` added to `TimingWarning.code` union. AC-10 and AC-11 cover it.
- **M3** → D-22 specifies reimplementing locally, types-only dependency on OBJ-016. Integration points table updated.
- **M4** → D-10 specifies cut-boundary tie-breaking explicitly (incoming scene wins). AC-36 covers it.
- **m1** → D-23 handles both cases: within composition (force 1 frame) and past end (drop). EC-08 updated.
- **m2** → Integration points table explicitly notes OBJ-014 as architectural dependency with explanation.

I'd like the challenger to verify these changes and approve if satisfied.

---

## Round 4 — spec_challenger

I've verified the Round 3 revision against my Round 2 objections. Let me confirm the fixes and check for new issues.

## Verification of Round 2 Fixes

| Issue | Status | Verification |
|---|---|---|
| **C1** (`TRANSITION_TRUNCATED` unspecified) | ✅ Fixed | D-21 fully specifies conditions, messages, and crossfade-only scope. AC-23, AC-24 cover it. |
| **C2** (Transition frame range formulas missing) | ✅ Fixed | D-19 provides explicit formulas with clamping. AC-18, AC-19, AC-22 cover it. |
| **M1** (Solo/asymmetric opacity formulas) | ⚠️ Partially fixed — **new critical issue** discovered. See C3 below. |
| **M2** (`audio_proportional` discards start_times) | ✅ Fixed | D-07 updated, `START_TIMES_IGNORED` warning added, AC-10/AC-11 cover it. |
| **M3** (Import vs. reimplement) | ✅ Fixed | D-22 specifies local reimplementation. Types-only dependency clear. |
| **M4** (Cut-boundary tie-breaking) | ✅ Fixed | D-10 specifies incoming scene wins. AC-36 covers it. |
| **m1** (Zero-frame scene at end) | ✅ Fixed | D-23 handles both cases. |
| **m2** (OBJ-014 architectural dep) | ✅ Fixed | Integration table clarified. |

Good work on the revisions. However, I found one new critical issue introduced by the interaction between D-13, D-15, and D-20.

---

## New Critical Issue

### C3: `dip_to_black` opacity has a discontinuity between non-overlap and overlap portions

D-20's table prescribes **different formulas** for the non-overlap and overlap portions of a `dip_to_black` transition, and these formulas produce different values at the boundary between them.

**Concrete example:** Scene A has `transition_out: dip_to_black, 2s`. Scene B has `transition_in: dip_to_black, 1s`. Overlap = 1s. Non-overlap portion of A's transition = first 1s.

At the boundary (end of non-overlap / start of overlap):

- **D-15 formula** (non-overlap): `p` = progress through A's full transitionOut frame range. At 1s into a 2s transition, `p = 0.5`. Opacity = `1 - 0.5 = 0.5`.

- **D-13 formula** (overlap): `p` = progress through the overlap region. At the overlap start, `p = 0`. Opacity = `max(0, 1 - 2*0) = 1.0`.

**Result:** Scene A's opacity jumps from **0.5 to 1.0** at the overlap boundary. This is a visible flash — a rendering artifact that would be visible in the output video.

Note: crossfade does NOT have this problem because D-14/D-20 specify opacity = 1.0 for the non-overlap portion, which is continuous with crossfade opacity = `1 - p` at `p = 0` in the overlap.

**Proposed fix:** Unify `dip_to_black` opacity into a single formula per scene applied to its own full transition frame range, eliminating the overlap/non-overlap split:

```
dip_to_black transition_out:
  p = progress through scene's full transitionOut frame range, [0, 1]
  opacity = max(0, 1 - 2*p)
  // Reaches 0 at p=0.5. Stays at 0 for p > 0.5.

dip_to_black transition_in:
  p = progress through scene's full transitionIn frame range, [0, 1]
  opacity = max(0, 2*p - 1)
  // Stays at 0 for p < 0.5. Reaches 1 at p=1.
```

This formula:
- **Symmetric case** (both transitions equal overlap): identical to current D-13. Midpoint both = 0. ✓
- **Asymmetric case** (A: 2s, B: 1s, overlap 1s): A reaches 0 at 1s (the overlap boundary), stays at 0. B is invisible for first 0.5s of overlap, then fades in. Creates a 0.5s black gap. Clean dip-to-black. No discontinuity. ✓
- **Solo transitions** (first/last scene): A 1s `dip_to_black` transition_in = 0.5s black + 0.5s fade-in. A 1s transition_out = 0.5s fade-out + 0.5s black. Consistent with "dip to/from black" semantics. ✓

This means D-13 becomes the universal dip_to_black formula, D-15 is replaced by the same formula for solo cases, and D-20's table no longer needs separate dip_to_black rows for overlap vs. non-overlap. One formula, no branching, no discontinuity.

**Impact on ACs:** AC-32 would change — solo transition_in opacity at frame 0 is 0, and it stays at 0 until the halfway point of the transition. AC-33 similarly: opacity is 1 at frame 0, reaches 0 at the halfway point, stays at 0. The AC formulas need updating from `opacity = p` / `opacity = 1 - p` to `opacity = max(0, 2p - 1)` / `opacity = max(0, 1 - 2p)`.

---

## Minor Issues

### m3: No acceptance criterion for `ZERO_DURATION` error

The `@throws` doc on `resolveTimeline` lists `TimingError` with code `'ZERO_DURATION'`, but there is no AC verifying this. Tests 57-58 cover zero-frame scenes (which is different — that's `SCENE_DURATION_ADJUSTED`), but nothing tests the case where the total resolved duration is 0.

**Proposed fix:** Add AC-48: `"If all scenes resolve to zero duration after scaling (e.g., audio duration approaches 0 with rounding), resolveTimeline throws TimingError with code 'ZERO_DURATION'."`

### m4: No acceptance criteria for D-23 zero-frame scene handling

D-23 is only covered in EC-08 and tests 57-58. There should be explicit ACs.

**Proposed fix:** Add:
- AC-49: `"A scene that resolves to zero frames (startFrame === endFrame) within the composition is adjusted to 1 frame (endFrame = startFrame + 1) with a SCENE_DURATION_ADJUSTED warning."`
- AC-50: `"A scene that resolves to zero frames past the composition end (startFrame >= clock.totalFrames) is dropped from timeline.scenes with a SCENE_DURATION_ADJUSTED warning."`

---

## Summary

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| C3 | Critical | `dip_to_black` opacity discontinuity at overlap boundary | New — must fix |
| m3 | Minor | No AC for `ZERO_DURATION` | New |
| m4 | Minor | No ACs for D-23 zero-frame handling | New |

**C3 is the only blocker.** The minor issues are real but small — they could be added as ACs quickly. Once C3 is resolved with the unified formula approach (or an equivalent fix that eliminates the discontinuity), and the minor ACs are added, I'll converge.

---

## Round 5 — spec_author

Here is the revised specification addressing C3, m3, and m4.

I'll focus on the specific changes rather than reprinting the entire spec, then present the complete revised spec at the end.

---

## Changes Made

### C3 Fix: Unified `dip_to_black` Opacity Formula

The challenger correctly identified a discontinuity at the overlap/non-overlap boundary. The fix is to use a single formula per scene applied to its **full** transition frame range, with no overlap/non-overlap branching:

**Revised D-13:** `dip_to_black` uses a single formula per scene, applied across the scene's full `ResolvedTransition` frame range:

```
dip_to_black transition_out (on any scene):
  p = progress through scene's transitionOut frame range, [0, 1]
  opacity = max(0, 1 - 2*p)
  // Fades from 1→0 over the first half. Stays at 0 for the second half.

dip_to_black transition_in (on any scene):
  p = progress through scene's transitionIn frame range, [0, 1]
  opacity = max(0, 2*p - 1)
  // Stays at 0 for the first half. Fades 0→1 over the second half.
```

This formula is universal — it applies identically to solo transitions (first/last scene with no partner), symmetric overlaps (equal transition durations), and asymmetric overlaps. No branching required.

**Revised D-15:** Solo transitions now use the same formula as D-13. No special case needed.

**Revised D-20:** The asymmetric transition table simplifies — `dip_to_black` has one row (formula applied to full transition range), not separate overlap/non-overlap rows. Crossfade retains the overlap-only ramp.

**Revised ACs:**
- AC-27 updated: midpoint of the *overlap* may not be exactly black anymore (depends on symmetry), but the midpoint of each scene's *transition range* is the zero-opacity point.
- AC-32 updated: solo transition_in opacity starts at 0 and stays at 0 for the first half, then ramps 0→1.
- AC-33 updated: solo transition_out opacity starts at 1, reaches 0 at the halfway point, stays at 0.

### m3 Fix: Added AC for `ZERO_DURATION`

New AC-48.

### m4 Fix: Added ACs for D-23 zero-frame handling

New AC-49 and AC-50.

---

Now here is the complete revised spec:

---

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

**Rationale:** Timeline resolution is a single computation: manifest + audio → frame ranges. There is no streaming state to manage. Pure functions are trivially testable, composable, and have no hidden coupling. The `ResolvedTimeline` output is an immutable data structure consumed by OBJ-035.

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
- `audioInfo` provided → default `'audio_proportional'`
- `audioInfo` not provided → default `'explicit'`

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

Verify: max(startTime[i] + D'[i]) = A  ✓
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
- Last scene: `c[N-1] + (A - c[N-1]) = A` ✓
- Non-last scene `i`: `c[i] + c[i+1] - c[i] + O[i] = c[i+1] + O[i]` — exceeds `c[i+1]` by `O[i]`, which is the overlap with scene `i+1`. Correct.

### D-09: FrameClock Created Internally

**Choice:** `resolveTimeline()` creates a `FrameClock` via `FrameClock.fromDuration(fps, totalDuration)` and returns it in the timeline.

**Rationale:** The clock's `totalFrames` is derived from the resolved duration, which may differ from what the manifest implies (in audio modes). Creating it here ensures a single source of truth for the composition's frame count.

### D-10: Frame Boundaries via `FrameClock.timestampToFrame()`

**Choice:** Scene `startFrame` and `endFrame` are computed using `clock.timestampToFrame(startTime)` and `clock.timestampToFrame(endTime)`. For the last scene (by `endTime`), `endFrame = clock.totalFrames` to prevent off-by-one from floating-point rounding.

**Cut-boundary tie-breaking:** Two sequential scenes A and B at a `cut` boundary where `A.endTime == B.startTime` may produce `A.endFrame == B.startFrame` (no gap/overlap — ideal) or a one-frame overlap. When a one-frame overlap occurs at a cut boundary (no non-cut transitions active), `resolveFrameState` assigns the overlapping frame to scene B (the incoming scene): it returns `{ type: 'scene', primary: B, secondary: null, transitionType: null }`. The outgoing scene A does not render for that frame.

### D-11: Per-Frame Lookup via Linear Scan

**Choice:** `resolveFrameState` uses linear scan of `timeline.scenes` to find active scenes.

**Rationale:** Scene counts are small (5-15 typical, 500 max). O(n) per frame with n ≤ 15 is negligible relative to the ~100ms+ per-frame render cost. Cursor optimization deferred per AP-05.

### D-12: Transition Opacity Uses Linear Interpolation

**Choice:** Transition opacity is computed with linear interpolation. No easing applied to transition blending.

**Rationale:** The manifest schema (OBJ-004) defines easing on `camera_params` (for camera paths), not on transitions. Linear opacity produces clean, predictable blends. Transition easing deferred to V2.

### D-13: Unified `dip_to_black` Opacity Formula

**Choice:** `dip_to_black` uses a single formula per scene applied to the scene's full `ResolvedTransition` frame range. There is no branching between "solo," "overlap," and "non-overlap" — one formula handles all cases:

```
dip_to_black transition_out (on any scene):
  p = (frame - transitionOut.startFrame) / (transitionOut.endFrame - transitionOut.startFrame)
  p ∈ [0, 1]
  opacity = max(0, 1 - 2*p)
  // Fades from 1→0 over the first half of the transition range.
  // Stays at 0 for the second half.

dip_to_black transition_in (on any scene):
  p = (frame - transitionIn.startFrame) / (transitionIn.endFrame - transitionIn.startFrame)
  p ∈ [0, 1]
  opacity = max(0, 2*p - 1)
  // Stays at 0 for the first half of the transition range.
  // Fades 0→1 over the second half.
```

This formula is universal — it produces correct behavior in all contexts:

- **Symmetric overlap** (both transitions equal overlap duration): At the overlap midpoint, outgoing reaches 0 (p=0.5 in its range) and incoming is still at 0 (p=0.5 in its range). Fully black frame. Identical to a classic dip-to-black. ✓
- **Asymmetric overlap** (A: transition_out 2s, B: transition_in 1s, overlap 1s): A reaches opacity 0 at its midpoint (1s into its 2s range), which is exactly the overlap start. A stays at 0 during the overlap. B starts its transition at the overlap start; B stays at 0 for first 0.5s of overlap, then fades in. Result: continuous fade out → black gap → fade in. No discontinuity. ✓
- **Solo transition** (first scene fading in, last scene fading out, no partner): A 1s dip_to_black transition_in stays at 0 for 0.5s, then fades in over 0.5s. A 1s transition_out fades out over 0.5s, then stays at 0 for 0.5s. Consistent "dip to/from black" semantics. ✓

**Why `max(0, ...)` instead of `clamp`:** The formula naturally stays in [0, 1] for `p ∈ [0, 1]`. The `max(0, ...)` handles the "stays at 0" region where `1 - 2p` goes negative.

Both `primary` (outgoing) and `secondary` (incoming) are returned in `FrameState` with `transitionType: 'dip_to_black'` during overlap regions. During non-overlap portions of a transition, only the solo scene is returned (`secondary: null`).

### D-14: Crossfade Opacity Formula

**Choice:** Crossfade opacity applies **only within the overlap region** between two scenes:

```
progress p = (frame - overlapStartFrame) / (overlapEndFrame - overlapStartFrame)
p ∈ [0, 1]

Outgoing scene: opacity = 1 - p
Incoming scene: opacity = p
Sum always = 1.0 (energy-preserving blend)
```

**Outside the overlap region**, a scene's opacity is 1.0 — even if the scene's own `ResolvedTransition` frame range extends beyond the overlap (asymmetric case). A crossfade is visually meaningless without a second scene to blend with, so the non-overlap portion simply renders at full opacity. The `TRANSITION_TRUNCATED` warning (D-21) alerts the author.

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
- [ ] **AC-30:** `normalizedTime` ≈ 0.0 at the scene's first frame. `normalizedTime` approaches 1.0 at the scene's last frame.
- [ ] **AC-31:** `resolveFrameState` throws `TimingError` with code `FRAME_OUT_OF_RANGE` for `frame < 0` or `frame >= timeline.totalFrames`.

### Solo Transitions

- [ ] **AC-32:** First scene with `transition_in: dip_to_black, 1s` and no overlapping previous scene: at the scene's first frame (p=0), opacity = `max(0, 2*0 - 1) = 0`. At the midpoint of the transition range (p=0.5), opacity = 0. At the last frame of the transition range (p≈1), opacity ≈ 1. `secondary: null`, `transitionType: 'dip_to_black'`.
- [ ] **AC-33:** Last scene with `transition_out: dip_to_black, 1s` and no overlapping next scene: at the start of the transitionOut range (p=0), opacity = `max(0, 1 - 0) = 1`. At the midpoint (p=0.5), opacity = 0. At the end (p≈1), opacity = 0. `secondary: null`, `transitionType: 'dip_to_black'`.

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

Cues at [0, 10, 20], overlap 0.5s between each pair, audio = 30s. Durations: [10.5, 10.5, 10]. Scene 0 ends at 10.5s, Scene 1 starts at 10.0s → 0.5s overlap. `max(endTime) = 30.0` = audio duration. ✓

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

Scene A: `transition_out: dip_to_black 2s`. Scene B: `transition_in: dip_to_black 1s`. Overlap = 1s. A's opacity follows `max(0, 1 - 2p)` across its full 2s range (p over A's transitionOut). At p=0.5 (1s mark), A's opacity = 0. During the overlap (1s–2s of A's range), A is at 0. B's opacity follows `max(0, 2p - 1)` across its 1s range. B's first 0.5s: opacity = 0. B's last 0.5s: fades from 0 to 1. Result: continuous, no discontinuity, with a ~0.5s black gap in the overlap. ✓

### EC-19: Total Duration Resolves to Zero

In audio_proportional mode with extremely short audio (e.g., 0.001s) where `FrameClock.fromDuration` would produce 0 frames (impossible since `Math.ceil(0.001 * 30) = 1`), or if all scenes are dropped per D-22, the resolved total duration is 0. Throws `ZERO_DURATION`.

## Test Strategy

### Unit Tests: `test/unit/engine/scene-timing.test.ts`

**Mode inference and configuration:**
1. `resolveTimeline(manifest)` with no audio → mode is `'explicit'`.
2. `resolveTimeline(manifest, { durationSeconds: 45 })` → mode is `'audio_proportional'`.
3. `resolveTimeline(manifest, audio, { mode: 'explicit' })` → mode is `'explicit'` (override).
4. `resolveTimeline(manifest, audio, { mode: 'audio_cue' })` → mode is `'audio_cue'`.

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
25. Adjacent non-overlapping scenes: no frame gaps or overlaps (within ±1 frame).

**Transition resolution:**
26. `transitionIn` with 1.0s duration: `startFrame === scene.startFrame`, `endFrame` spans ~30 frames at 30fps.
27. `transitionOut` with 0.5s duration: `endFrame === scene.endFrame`, `startFrame` ~15 frames before end at 30fps.
28. `cut` transition: `transitionIn/Out === null`.
29. Transition duration exceeding scene duration: frame range clamped to scene's range.
30. `computeTransitionOverlap`: crossfade 1.0s + crossfade 0.5s → 0.5s.
31. `computeTransitionOverlap`: crossfade 1.0s + cut → 0.
32. `computeTransitionOverlap`: both absent → 0.
33. `TRANSITION_TRUNCATED` warning: crossfade 2s with overlap 1s → warning emitted.
34. `TRANSITION_TRUNCATED` NOT emitted for dip_to_black with same asymmetry.

**Per-frame lookup (`resolveFrameState`):**
35. Frame in middle of a scene, no transitions: `type: 'scene'`, opacity 1.0, `secondary: null`.
36. Frame in crossfade overlap: `transitionType: 'crossfade'`, both primary and secondary present, opacities sum to 1.0.
37. Frame at start of crossfade overlap (progress=0): outgoing opacity=1.0, incoming opacity=0.0.
38. Frame at end of crossfade overlap (progress≈1): outgoing opacity≈0.0, incoming opacity≈1.0.
39. Frame in symmetric dip_to_black overlap, first quarter: outgoing opacity > 0, incoming opacity = 0.
40. Frame in symmetric dip_to_black overlap, midpoint: both opacities = 0.
41. Frame in symmetric dip_to_black overlap, last quarter: outgoing opacity = 0, incoming opacity > 0.
42. Frame in gap between scenes: `type: 'gap'`.
43. Frame in solo dip_to_black transition_in (first scene): first half opacity=0, second half ramps 0→1. `transitionType: 'dip_to_black'`.
44. Frame in solo dip_to_black transition_out (last scene): first half ramps 1→0, second half opacity=0.
45. `frame < 0`: `FRAME_OUT_OF_RANGE` error.
46. `frame >= totalFrames`: `FRAME_OUT_OF_RANGE` error.

**Asymmetric transitions:**
47. Crossfade non-overlap portion: outgoing scene opacity = 1.0, `transitionType = null`.
48. Dip_to_black asymmetric (A: 2s, B: 1s, overlap 1s): A's opacity follows `max(0, 1-2p)` across full 2s range continuously. At overlap start (1s into A's transition), A is at 0. B fades in per its formula. No discontinuity.

**Cut-boundary tie-breaking:**
49. One-frame overlap at cut boundary: incoming scene B is primary, outgoing A not rendered.

**normalizedTime:**
50. First frame of scene: `normalizedTime` ≈ 0.0.
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

- **TC-06** (deterministic output): Same manifest + same audio info + same config → identical `ResolvedTimeline`. Trivially true for pure functions, but worth asserting.
- **TC-13** (audio duration drives total video length): Test 12 directly verifies this — 5-scene manifest + 45s audio → output exactly 45 seconds.
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
| **OBJ-077** (Integration: full pipeline) | Indirect consumer via OBJ-035. Validates that the full pipeline (manifest → timing → render → encode) produces correct output. |
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

---

I believe this revision fully addresses C3, m3, and m4:

- **C3** → D-13 is now a unified formula with no overlap/non-overlap branching for `dip_to_black`. D-15 is replaced with a complete decision table. I verified continuity for the challenger's concrete example: A (2s dip_to_black out) reaches 0 at the 1s mark (p=0.5 of its 2s range), which is exactly the overlap start. B starts its 1s range at the overlap start. B stays at 0 for its first 0.5s, then fades in. No discontinuity. AC-27, AC-32, AC-33, AC-35 are updated with correct formulas.
- **m3** → AC-45 covers `ZERO_DURATION`. EC-19 describes the scenario. Test 66 covers it.
- **m4** → AC-46 and AC-47 explicitly cover the two D-22 scenarios.

I'd like the challenger to verify these changes and approve if satisfied.

---

## Round 6 — spec_challenger

I've verified the Round 5 revision against all prior objections.

## Verification of Round 4 Fixes

| Issue | Status | Verification |
|---|---|---|
| **C3** (dip_to_black discontinuity) | ✅ Fixed | Traced the concrete example: A (2s dip_to_black out, `max(0, 1-2p)`), B (1s dip_to_black in, `max(0, 2p-1)`). At overlap boundary: A reaches 0 at p=0.5 of its 2s range (= 1s = overlap start). B starts at 0. Continuous. No discontinuity. D-13 is now a single universal formula. D-15 decision table covers all combinations. AC-27, AC-32, AC-33, AC-35 updated with correct formulas. |
| **m3** (No AC for ZERO_DURATION) | ✅ Fixed | AC-45 covers it. EC-19 describes the scenario. Test 66 covers it. |
| **m4** (No ACs for D-22/D-23) | ✅ Fixed | AC-46 (zero-frame within composition → adjust to 1) and AC-47 (past end → drop). Tests 57-58 cover them. |

## Final Sweep — No New Issues Found

I did a final comprehensive check:

1. **D-15 decision table completeness:** All frame contexts are covered — no-transition, crossfade overlap, crossfade non-overlap, dip_to_black (any context), degenerate (both transitions overlapping), cut boundary, gap. The `p` variable is unambiguous (progress through the specific `ResolvedTransition` frame range). ✓
2. **D-07 scaling algorithm correctness:** Overlaps `O[i]` computed from fixed manifest transitions before scaling. Scale factor formula verified. Start times recomputed sequentially. `START_TIMES_IGNORED` warning specified. ✓
3. **D-08 cue algorithm:** Verified math. Last scene reaches audio duration. Non-last scenes' overlap extensions are correct. ✓
4. **`computeTransitionOverlap` signature:** Uses `Pick<Scene, 'transition_out'>` — handles optional fields (returns 0 when absent). ✓
5. **`SCENE_TOO_SHORT` scope:** Only thrown in audio modes (explicitly stated in @throws: "in audio modes"). Explicit mode degrades gracefully via D-19 clamping. ✓
6. **Import graph clean:** Only code-level import is `FrameClock` from OBJ-009. Types from OBJ-004's `schema.ts`. No import from `loader.ts`. OBJ-014 is architectural only. ✓
7. **Constraint compliance:** C-07 ✓, TC-13 ✓, AP-04 (no I/O) ✓, AP-05 (no premature optimization — linear scan) ✓. No licensing concerns (pure computation). ✓
8. **Vocabulary:** Uses seed terms correctly throughout. No drift. ✓

The spec is complete, unambiguous, and implementable. 50 acceptance criteria, 19 edge cases, 67 tests, 22 design decisions with rationale.

CONCLUSION:

The specification for OBJ-038 — Audio Sync and Scene Timing — is approved. It defines a pure, synchronous, stateless timing resolution module (`src/engine/scene-timing.ts`) with three timing modes (explicit, audio_proportional, audio_cue), frame-level scene resolution, and a per-frame lookup function with unified opacity formulas. All critical and major issues from prior rounds have been verified as resolved.

Let me write the files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/output.md",
  "content": "# Specification: OBJ-038 \u2014 Audio Sync and Scene Timing\n\n## Summary\n\nOBJ-038 implements the scene timing resolution module (`src/engine/scene-timing.ts`) \u2014 the bridge between the declarative manifest timing and concrete, frame-level rendering instructions. It takes a validated Manifest (from OBJ-016), optional audio metadata (from OBJ-014's `probeMedia()`), and a timing configuration, then resolves scene durations and start times according to one of three timing modes defined in seed Section 8.7: **explicit** (manifest values as-is), **audio-proportional** (scale durations to fit audio length), or **audio-cue** (manifest `start_time` values treated as narration cue timestamps). It computes exact frame ranges per scene including transition overlaps, creates a `FrameClock` (OBJ-009) for the resolved composition, and provides a per-frame lookup function that returns which scene(s) are active with their normalized time and opacity. This module satisfies C-07 (audio synchronization) and TC-13 (audio duration drives total video length).\n\n## Interface Contract\n\n### Module: `src/engine/scene-timing.ts`\n\n```typescript\nimport type { Manifest, Scene } from '../manifest/schema.js';\nimport { FrameClock } from './frame-clock.js';\n\n// \u2500\u2500\u2500 Configuration Types \u2500\u2500\u2500\n\n/**\n * Timing resolution mode, per seed Section 8.7.\n *\n * - 'explicit': Use manifest start_time and duration values as-is.\n *   If audioInfo is provided, emit AUDIO_DURATION_MISMATCH warning\n *   when total scene duration differs from audio duration beyond tolerance.\n *\n * - 'audio_proportional': Total video duration = audio duration.\n *   Manifest scene durations are used as proportional weights.\n *   Manifest start_time values are IGNORED and recomputed sequentially.\n *   Each scene's resolved duration = (manifestDuration / sumMan
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/output.md
Now update meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-038",
     3→  "description": "Audio sync and scene timing -- duration distribution algorithm per Section 8.7: audio-driven (T = audio_duration, scenes share proportionally), explicit (T = sum of scene durations + transition overlaps), or combined (explicit durations with audio mismatch warning). Timestamp-based scene boundary alignment to narration cues. Covers C-07 (audio synchronization) and TC-13 (audio duration drives total video length).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-014", "OBJ-016"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json",
  "content": "{\n  \"id\": \"OBJ-038\",\n  \"description\": \"Audio sync and scene timing -- duration distribution algorithm per Section 8.7: audio-driven (T = audio_duration, scenes share proportionally), explicit (T = sum of scene durations + transition overlaps), or combined (explicit durations with audio mismatch warning). Timestamp-based scene boundary alignment to narration cues. Covers C-07 (audio synchronization) and TC-13 (audio duration drives total video length).\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:15:00.000000+00:00\",\n  \"depends_on\": [\"OBJ-009\", \"OBJ-014\", \"OBJ-016\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"notes\": \"Tier 3 engine integration. Spec defines scene-timing.ts with three timing modes (explicit, audio_proportional, audio_cue), frame-level scene resolution via FrameClock, and per-frame lookup with unified dip_to_black opacity formula. 50 acceptance criteria, 22 design decisions.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json has been updated successfully.
Now commit:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Show working tree status"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commit messages"
}
[Tool Result] f831439 OBJ-035: Orchestrator spec - main render loop coordinating Puppeteer, FFmpeg, virtualized clock
6939369 OBJ-029: Tunnel push forward camera path preset specification
f54a115 spec(OBJ-049): software rendering configuration specification
55e99d9 spec(OBJ-030): flyover_glide camera path preset specification
a17e226 spec(OBJ-012): frame capture pipeline specification
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-038/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/transcript.md
	nodes/OBJ-002/transcript.md
	nodes/OBJ-003/transcript.md
	nodes/OBJ-004/transcript.md
	nodes/OBJ-005/transcript.md
	nodes/OBJ-006/transcript.md
	nodes/OBJ-007/transcript.md
	nodes/OBJ-008/transcript.md
	nodes/OBJ-009/transcript.md
	nodes/OBJ-010/transcript.md
	nodes/OBJ-011/transcript.md
	nodes/OBJ-012/transcript.md
	nodes/OBJ-013/transcript.md
	nodes/OBJ-014/transcript.md
	nodes/OBJ-015/transcript.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-019/transcript.md
	nodes/OBJ-020/transcript.md
	nodes/OBJ-021/transcript.md
	nodes/OBJ-026/transcript.md
	nodes/... [truncated]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-038/output.md nodes/OBJ-038/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-038): audio sync and scene timing specification\n\nDefines scene-timing.ts with three timing modes (explicit, audio_proportional,\naudio_cue) per seed Section 8.7. Includes frame-level scene resolution via\nFrameClock, per-frame lookup with unified dip_to_black opacity formula,\ncrossfade overlap handling, and 50 acceptance criteria. Covers C-07 (audio\nsynchronization) and TC-13 (audio duration drives total video length).\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-038 spec files"
}
[Tool Result] [master 593383f] spec(OBJ-038): audio sync and scene timing specification
 2 files changed, 887 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-038/output.md
The specification for OBJ-038 has been written to disk and committed. 

**Summary of the agreed specification:**

- **Module:** `src/engine/scene-timing.ts` — a pure, synchronous, stateless timing resolution module
- **Three timing modes** mapping to seed Section 8.7: `explicit` (manifest as-is), `audio_proportional` (scale to audio duration), `audio_cue` (narration cue timestamps)
- **Key functions:** `resolveTimeline()` (manifest + audio → frame-level ranges), `resolveFrameState()` (per-frame lookup for active scenes, opacity, normalized time), `computeTransitionOverlap()` (helper)
- **22 design decisions** covering: unified `dip_to_black` opacity formula (no discontinuity), crossfade overlap-only ramp, asymmetric transition handling via complete decision table, cut-boundary tie-breaking, zero-frame scene handling, local `computeTotalDuration` reimplementation
- **50 acceptance criteria**, 19 edge cases, 67 tests
- **No I/O** — caller provides `AudioInfo` via OBJ-014's `probeMedia()`, keeping the module pure and testable
