# Deliberation Transcript: OBJ-058

---

## Round 1 — spec_author

I'll start by reading the existing OBJ-058 node directory and any relevant dependency outputs to understand what's already in place.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-058/**/*"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-035/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-058/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-058/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-058",
     3→  "description": "Director Agent workflow specification -- critique format per Sections 10.4-10.5 (timestamped observations, directional deltas not absolute values, edge reveal reporting, physics/motion feel descriptions). HITL circuit breaker process per Section 10.3 (human reviews, approves/modifies/rejects/overrides). Convergence criteria per Section 10.7 (no Priority 1 issues, human sign-off, visual_status marked tuned). Visual Critique template. Covers TC-15 (convergence in <=5 iterations) and TC-16 (Director-tuned presets outperform blind-authored).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. High priority. All 8 tuning objectives (OBJ-059 through OBJ-066) depend on this."
... [truncated]
Now let me check what the tuning objectives look like to understand the downstream consumers:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-059/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-059/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-068/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-068/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-059/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-059",
     3→  "description": "Tune stage geometry with default camera paths (static, slow_push_forward/pull_back, gentle_float). Produce test renders, submit to Director Agent for Visual Critique, pass through HITL circuit breaker, adjust parameters, iterate until convergence. Mark visual_status as tuned when human signs off. Per SC-07 (all geometries visually tuned).",
     4→  "category": "tuning",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-018", "OBJ-026", "OBJ-027", "OBJ-031", "OBJ-035", "OBJ-058"],
     9→  "visual_status": "needs_tuning",
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 tuning. Requires orchestrator + geometry + camera implementations + Director workflow."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-068/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-068",
     3→  "description": "Transition visual validation -- crossfade and dip_to_black quality across scene boundaries. Test whether 0.5-1.0 second crossfade masks visible artifacts at scene boundaries per TC-10. Submit transition test renders to Director Agent, iterate through HITL.",
     4→  "category": "tuning",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-037", "OBJ-035", "OBJ-058"],
     9→  "visual_status": "needs_tuning",
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 tuning. Covers TC-10."
    12→}
    13→
Now let me check some relevant source files to understand what tooling already exists:
[Tool: Glob]
  Input: {
  "pattern": "src/engine/orchestrator.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found
Good — the source code doesn't exist yet; we're at the specification-only stage. OBJ-058 is a process/workflow specification with supporting tooling, not a pure code module. Let me now propose the full spec.

---

# Proposed Specification: OBJ-058 — Director Agent Workflow Specification

## Summary

OBJ-058 defines the complete Director Agent visual tuning workflow — the process, document formats, supporting tooling, and convergence tracking that enable the 8 geometry tuning objectives (OBJ-059 through OBJ-066) and the transition tuning objective (OBJ-068) to systematically improve scene presets using vision-capable LLM feedback gated by human approval. It codifies seed Sections 10.3–10.7 into actionable protocols, a structured critique format, a test-render utility that wraps OBJ-035's Orchestrator for quick clip generation, and a meta.json schema extension for tracking tuning rounds. It also defines the measurement frameworks for TC-15 (convergence ≤ 5 iterations) and TC-16 (Director-tuned presets outperform blind-authored).

## Deliverables

OBJ-058 produces three categories of artifact:

1. **Process Protocol** — The step-by-step HITL workflow, convergence criteria, scope rules, and anti-patterns. Lives as documentation consumed by all tuning sessions.
2. **Document Formats** — The Visual Critique template, the HITL Approval Record format, and the Tuning Round Log format. These are structured markdown/JSON templates that tuning sessions fill in.
3. **Test Render Utility** — A thin Node.js module (`src/tools/test-render.ts`) and companion CLI subcommand that wraps OBJ-035's Orchestrator to render short test clips optimized for Director review (small resolution, short duration, fast turnaround).

---

## Interface Contract

### Module: `src/tools/test-render.ts`

```typescript
import type { OrchestratorResult } from '../engine/orchestrator.js';
import type { ManifestRegistry } from '../manifest/schema.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

/**
 * Configuration for a test render — optimized for fast
 * Director Agent review, not production quality.
 */
export interface TestRenderConfig {
  /**
   * The manifest to render. Can be a full Manifest object
   * or a path to a JSON file.
   */
  manifest: unknown | string;

  /** ManifestRegistry for validation. */
  registry: ManifestRegistry;

  /** GeometryRegistry for spatial data. */
  geometryRegistry: GeometryRegistry;

  /** CameraPathRegistry for camera presets. */
  cameraRegistry: CameraPathRegistry;

  /** Output path for the rendered MP4. */
  outputPath: string;

  /**
   * Base directory for resolving relative image paths.
   * Default: process.cwd()
   */
  assetsDir?: string;

  /**
   * Render quality preset. Controls resolution and encoding settings.
   *
   * - 'draft': 640x360, crf 28. Fastest. For initial iteration.
   * - 'review': 1280x720, crf 23. For Director Agent review.
   * - 'proof': 1920x1080, crf 20. Near-production. For final sign-off.
   *
   * Default: 'review'
   */
  quality?: 'draft' | 'review' | 'proof';

  /**
   * Maximum duration in seconds to render. If the manifest
   * is longer, only the first `maxDuration` seconds are rendered.
   * Useful for testing a specific camera path without rendering
   * the full composition.
   *
   * Default: 30 (per seed Section 10.3: "short test renders,
   * 10-30 seconds").
   */
  maxDuration?: number;

  /**
   * Scene ID to isolate. If provided, only this scene is rendered
   * (with its full duration up to maxDuration). Other scenes are
   * ignored. Useful for tuning a single geometry+camera combination.
   *
   * Default: undefined (render all scenes).
   */
  isolateScene?: string;

  /**
   * Whether to extract keyframe thumbnails alongside the MP4.
   * When true, produces PNG files at 25%, 50%, 75% of duration
   * in the same directory as outputPath, named:
   *   {basename}_025.png, {basename}_050.png, {basename}_075.png
   *
   * Useful for Director Agent review when video playback is
   * unavailable — the Director can analyze still frames.
   *
   * Default: true
   */
  extractKeyframes?: boolean;

  /**
   * Enable GPU acceleration. Default: false (software WebGL
   * per C-11 — test renders should match production behavior).
   */
  gpu?: boolean;

  /**
   * Forward browser console to stdout. Default: true
   * (test renders are debug-oriented).
   */
  debug?: boolean;
}

/**
 * Resolution presets for each quality level.
 * These are NOT configurable — they are fixed to ensure
 * consistent review conditions across tuning sessions.
 */
export const QUALITY_PRESETS: Record<
  'draft' | 'review' | 'proof',
  { width: number; height: number; crf: number; fps: number }
> = {
  draft:  { width: 640,  height: 360,  crf: 28, fps: 24 },
  review: { width: 1280, height: 720,  crf: 23, fps: 30 },
  proof:  { width: 1920, height: 1080, crf: 20, fps: 30 },
};

/**
 * Result from a test render, extending OrchestratorResult
 * with review-specific metadata.
 */
export interface TestRenderResult {
  /** The underlying orchestrator result. */
  orchestratorResult: OrchestratorResult;

  /** Quality preset used. */
  quality: 'draft' | 'review' | 'proof';

  /** Resolution rendered at (may differ from manifest). */
  renderedResolution: { width: number; height: number };

  /**
   * Paths to extracted keyframe PNGs. Empty array if
   * extractKeyframes was false.
   */
  keyframePaths: string[];

  /**
   * Duration actually rendered (may be less than manifest
   * total duration if maxDuration was applied).
   */
  renderedDurationSeconds: number;

  /**
   * Scene IDs that were rendered (all scenes, or just the
   * isolated scene).
   */
  renderedSceneIds: string[];
}

/**
 * Render a test clip for Director Agent review.
 *
 * This is a thin wrapper around OBJ-035's Orchestrator that:
 * 1. Overrides manifest resolution/fps with the quality preset.
 * 2. Truncates duration to maxDuration.
 * 3. Optionally isolates a single scene.
 * 4. Extracts keyframe thumbnails.
 *
 * The manifest is cloned and mutated — the original is not modified.
 *
 * @throws OrchestratorError — all errors from the underlying
 *   Orchestrator are propagated without wrapping.
 */
export async function renderTestClip(
  config: TestRenderConfig
): Promise<TestRenderResult>;
```

### CLI Subcommand: `depthkit test-render`

```
depthkit test-render <manifest> [options]

Arguments:
  manifest              Path to manifest JSON file

Options:
  --output, -o <path>   Output MP4 path (default: ./test-render-{timestamp}.mp4)
  --quality, -q <level> draft|review|proof (default: review)
  --max-duration <sec>  Maximum seconds to render (default: 30)
  --scene <id>          Isolate a single scene by ID
  --no-keyframes        Skip keyframe extraction
  --gpu                 Enable GPU acceleration
  --assets-dir <path>   Base directory for image resolution
```

---

### Tuning Round Log: JSON Schema

Each tuning objective (OBJ-059 through OBJ-066, OBJ-068) tracks its rounds in a `tuning-log.json` file within its node directory. This file is the machine-readable record of the HITL loop.

```typescript
/**
 * A single round of the Director Agent → HITL → Code Agent loop.
 */
export interface TuningRound {
  /** Round number, 1-indexed. */
  round: number;

  /** ISO 8601 timestamp when the test render was produced. */
  rendered_at: string;

  /** Path to the test render MP4 (relative to the node directory). */
  render_path: string;

  /** Paths to extracted keyframe PNGs. */
  keyframe_paths: string[];

  /** Quality preset used for the test render. */
  quality: 'draft' | 'review' | 'proof';

  /** Duration of the test render in seconds. */
  render_duration_seconds: number;

  /**
   * The Director Agent's Visual Critique.
   * Stored as a markdown string following the Visual Critique Template.
   * null if the Director has not yet reviewed this round.
   */
  director_critique: string | null;

  /**
   * The number of Priority 1 issues identified by the Director.
   * null if not yet reviewed.
   */
  priority_1_count: number | null;

  /**
   * HITL disposition of the Director's critique.
   * null if human has not yet reviewed.
   */
  hitl_disposition: 'approved' | 'modified' | 'rejected' | 'overridden' | null;

  /**
   * Human's notes on the disposition. Required for 'modified',
   * 'rejected', and 'overridden'. Optional for 'approved'.
   */
  hitl_notes: string | null;

  /**
   * The feedback actually passed to the Code Agent.
   * - If disposition is 'approved': same as director_critique.
   * - If 'modified': the human's edited version.
   * - If 'rejected': null (no feedback passed).
   * - If 'overridden': the human's own feedback (director_critique ignored).
   */
  approved_feedback: string | null;

  /**
   * Summary of parameter changes made by the Code Agent in
   * response to approved_feedback. Populated after the Code Agent
   * acts on the feedback.
   */
  changes_made: string | null;
}

/**
 * The complete tuning log for a tuning objective.
 */
export interface TuningLog {
  /** The objective ID (e.g., 'OBJ-059'). */
  objective_id: string;

  /** The geometry or preset being tuned. */
  target: string;

  /** The camera path(s) being tested. */
  camera_paths: string[];

  /** Ordered list of tuning rounds. */
  rounds: TuningRound[];

  /**
   * Current convergence status.
   * 'in_progress' — rounds are ongoing.
   * 'converged' — human has signed off (no Priority 1 issues).
   * 'abandoned' — tuning was stopped without convergence.
   */
  status: 'in_progress' | 'converged' | 'abandoned';

  /** ISO 8601 timestamp of last update. */
  updated_at: string;
}
```

### meta.json Schema Extension for Tuning Objectives

Tuning objectives (OBJ-059 through OBJ-066, OBJ-068) extend the standard `meta.json` with tuning-specific fields. These fields already exist in the seed's meta.json schema (`visual_status`, `tuning_rounds`) but their semantics are formalized here:

```typescript
interface TuningObjectiveMeta {
  // ... standard meta.json fields ...

  /**
   * Visual tuning status.
   * - null: not a tuning objective (or not yet started).
   * - 'needs_tuning': initial state for tuning objectives.
   * - 'in_progress': at least one tuning round has started.
   * - 'tuned': human has signed off. Convergence criteria met per Section 10.7.
   */
  visual_status: null | 'needs_tuning' | 'in_progress' | 'tuned';

  /**
   * Number of completed tuning rounds (where the Code Agent has
   * acted on approved feedback and produced a new test render).
   * Tracks TC-15 compliance (should reach convergence in ≤ 5).
   */
  tuning_rounds: number;
}
```

When a tuning objective converges, the session updates:
1. `meta.json`: `visual_status` → `'tuned'`, `tuning_rounds` → final count.
2. `index.json`: `visual_status` → `'tuned'` (mirrored from meta.json, managed by orchestrator).

---

## Visual Critique Template

The following markdown template is the **required format** for all Director Agent critiques. Tuning sessions provide this template to the Director Agent as part of its system prompt.

```markdown
# Visual Critique — {geometry_or_preset_name}
## Status: RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL

**Objective:** {objective_id}
**Round:** {round_number}
**Test Render:** {render_filename}
**Duration:** {duration_seconds}s
**Geometry:** {geometry_name}
**Camera Path(s):** {camera_path_names}
**Quality:** {quality_preset}

### Overall Impression
{1-2 sentences on general quality and feel. Is this convincingly 2.5D?
Does the camera motion feel cinematic or mechanical?}

### Timestamped Observations

#### {HH:MM:SS} – {HH:MM:SS} ({phase_label})
- {Observation. Must be timestamped to a specific moment.}
- {Use directional deltas: "push further back", "needs more ease-in".}
- {Do NOT prescribe coordinate values or Bezier control points.}

#### {HH:MM:SS} – {HH:MM:SS} ({phase_label})
- {Continue for each notable segment.}

### Edge Reveals
{List any moments where plane edges become visible. Include:
- Timestamp
- Which plane (by slot name)
- Direction of reveal (left/right/top/bottom edge)
- Suggested fix direction (wider plane, constrained camera range, etc.)}

### Depth and Separation
{Assessment of whether planes feel at distinct depths or flattened.
Note any planes that need to move closer/farther for better parallax.}

### Motion Feel
{Assessment of camera motion quality. Does it feel physical or
robotic? Note easing, speed, and organic quality issues.}

### Priority Tweaks (Ordered by Impact)
1. **P1: {Highest impact issue}** — {Directional fix description}
2. **P1/P2: {Next issue}** — {Directional fix description}
3. **P2: {Lower priority}** — {Directional fix description}
{Label each as P1 (must fix before convergence) or P2 (improvement, not blocking)}

### Things That Work Well (PRESERVE THESE)
- {What should NOT be changed. Critical for preventing regression.}
- {Be specific: "The floor perspective distortion at 00:08-00:15 reads correctly."}

### Convergence Assessment
{Can this converge in the next round? What is the single most impactful change?}
```

**Priority levels:**
- **P1 (Priority 1):** Must be resolved before the preset can be marked `tuned`. These are issues that would make the preset unsuitable for production: edge reveals, broken perspective, mechanical camera motion, clearly wrong depth placement.
- **P2 (Priority 2):** Desirable improvements that are not blocking. Polish-level tweaks: slightly better easing, minor depth adjustments, subtle motion refinements.

Convergence requires **zero P1 issues** in the most recent critique (per seed Section 10.7).

---

## HITL Approval Record Format

When the human reviews a Visual Critique, they produce a disposition recorded in the tuning log. The format for human feedback within the HITL step is:

```markdown
# HITL Approval — {objective_id} Round {N}

**Disposition:** {approved | modified | rejected | overridden}

## Notes
{Human's explanation of their decision. Required for modified/rejected/overridden.}

## Approved Feedback
{The actual feedback the Code Agent receives. For 'approved': copy of
Director critique. For 'modified': edited version. For 'overridden':
human's own notes. For 'rejected': this section is absent.}
```

---

## Director Agent System Prompt Template

Tuning sessions must provide the Director Agent with this system prompt (or equivalent) to constrain its behavior:

```markdown
You are the Director Agent for depthkit — a visual reviewer for 2.5D
parallax video presets. You review short test renders and produce
structured Visual Critiques.

## Your Constraints
1. You produce ONLY Visual Critiques using the provided template.
2. Every observation MUST be timestamped to a specific moment.
3. Use DIRECTIONAL DELTAS ("push further back", "needs more ease-in"),
   never absolute values ("set z=-45", "change to 0.8").
4. You do NOT write code, modify manifests, or prescribe parameter values.
5. Your critiques are RECOMMENDATIONS. A human will review and approve
   them before any Code Agent sees them.
6. Note what WORKS WELL — not just problems. Preventing regression is
   as important as fixing issues.
7. Assess against these qualities:
   - Convincing 2.5D depth (not flat, not exaggerated)
   - No edge reveals (plane boundaries never visible)
   - Camera motion feels physical (has weight, inertia, organic easing)
   - Depth separation between planes is readable
   - Overall cinematic quality appropriate for the geometry type

## You Are Reviewing
- Geometry: {geometry_name}
- Camera Path: {camera_path_name}
- Round: {round_number}
- Prior feedback (if any): {summary_of_prior_round_feedback}

Use the Visual Critique template provided.
```

---

## Workflow Protocol

### Step-by-Step HITL Tuning Loop

This protocol is followed by every tuning objective (OBJ-059 through OBJ-066, OBJ-068):

**Step 1: Prepare Test Render**
The Code Agent (Explorer session working on the tuning objective):
1. Creates or updates a test manifest using the geometry + camera path being tuned, with placeholder test images (solid colors or simple gradients are acceptable for spatial tuning — the geometry's spatial structure matters more than image content).
2. Calls `renderTestClip()` (or `depthkit test-render` CLI) with `quality: 'review'` and `maxDuration: 30`.
3. Records the render in `tuning-log.json` as a new round entry.

**Step 2: Director Agent Review**
A session with a vision-capable LLM:
1. Receives the Director Agent System Prompt.
2. Receives the test render MP4 (or keyframe PNGs if video input is unavailable).
3. If this is round > 1, receives a summary of prior-round feedback and changes.
4. Produces a Visual Critique following the template exactly.
5. The critique is saved in the tuning log's `director_critique` field.

**Step 3: HITL Circuit Breaker**
The human operator:
1. Reviews the Director's Visual Critique.
2. Optionally watches the test render themselves.
3. Chooses a disposition:
   - **Approve:** Passes the critique to the Code Agent as-is.
   - **Modify:** Edits the critique (removing hallucinated suggestions, adjusting priorities, adding own observations) and passes the modified version.
   - **Reject:** Discards the critique entirely (e.g., if the Director clearly misunderstood the geometry). No feedback is passed. The human may request a re-review or skip directly to Override.
   - **Override:** Ignores the critique and writes their own feedback from scratch.
4. Records the disposition in the tuning log.

**Step 4: Code Agent Implementation**
The Code Agent:
1. Receives **only** the human-approved feedback (never raw Director output — AP-09).
2. Translates directional descriptions into parameter adjustments using knowledge of the geometry/camera codebase.
3. Does NOT modify parameters that the feedback marked as "working well" unless required to fix a higher-priority issue.
4. Updates the geometry/camera preset code.
5. Records changes in the tuning log's `changes_made` field.
6. Returns to Step 1 with a new test render.

**Step 5: Convergence Check**
After each round, check the convergence criteria (Section 10.7):
1. The Director's most recent critique contains **zero P1 issues**.
2. The Human has reviewed the final render and **explicitly signed off**.
3. The Code Agent has committed the tuned parameters.
4. The tuning objective's `meta.json` is updated: `visual_status: 'tuned'`, `tuning_rounds: N`.

If converged: the tuning objective is marked `status: 'complete'` and proceeds to review.
If not converged: return to Step 1.

### Convergence Budget (TC-15)

Per TC-15, each geometry+camera combination should converge within **≤ 5 rounds**. If round 5 completes and P1 issues remain:

1. **Log the failure** in the tuning log with `status: 'abandoned'` and a note explaining why convergence failed.
2. **Escalate** by updating `meta.json` with a note: "Convergence exceeded 5 rounds. Possible causes: [geometry parameterization too rigid, camera path needs restructuring, Director feedback quality declining]."
3. **Do not continue indefinitely.** The human decides whether to:
   - Allow additional rounds (with a new 3-round budget).
   - Restructure the geometry/camera preset and restart.
   - Accept the current state as "good enough" and mark `tuned` with a caveat note.

This budget prevents the hallucination-loop risk described in AP-09 — even with the HITL gate, diminishing returns set in after ~5 iterations as changes become increasingly subjective.

### Scope Rules (per Section 10.6)

The Director Agent is invoked **only** for:
- Tuning a new scene geometry (OBJ-059 through OBJ-066).
- Tuning a new camera path preset within a geometry context.
- Validating that a geometry + camera combination produces no edge reveals.
- Validating transition visual quality (OBJ-068).
- Final visual sign-off before marking a preset as `tuned`.

The Director Agent is **never** invoked for:
- Manifest schema design, Zod validation, or code architecture.
- n8n pipeline integration, audio sync, or rendering pipeline logic.
- Any production rendering (AP-10).

---

## Design Decisions

### D1: Test Render Utility as a Thin Orchestrator Wrapper

**Decision:** `renderTestClip()` wraps OBJ-035's `Orchestrator` rather than implementing a separate render path. It clones the manifest, overrides `composition.width`, `composition.height`, `composition.fps`, and truncates `scenes` to fit `maxDuration`.

**Rationale:** The tuning workflow must validate the same rendering path that production uses. A separate "preview renderer" risks divergence — a preset that looks good in preview but breaks in production. The quality presets only adjust resolution and encoding settings, not the spatial pipeline.

### D2: Three Quality Tiers Instead of Arbitrary Resolution

**Decision:** Fixed `draft`/`review`/`proof` presets rather than arbitrary resolution overrides.

**Rationale:** Consistent review conditions across tuning sessions. If one geometry was tuned at 480p and another at 1080p, edge-reveal detection would be inconsistent. The `review` tier (720p) balances render speed with visual clarity sufficient for Director analysis.

### D3: Keyframe Extraction for Non-Video Director Input

**Decision:** Extract 3 keyframe PNGs (at 25%, 50%, 75% of duration) alongside the MP4.

**Rationale:** Some vision LLMs handle still images better than video, or cannot accept video input at all. Keyframes provide a fallback review medium. Three frames at quartile positions capture the beginning-of-motion, peak-motion, and end-of-motion states, which are sufficient to assess depth placement, edge reveals, and overall composition. The Director Agent should still prefer video when available.

### D4: Tuning Log as JSON, Not Markdown

**Decision:** `tuning-log.json` is machine-readable JSON. The Visual Critiques and HITL notes are stored as markdown strings within JSON fields.

**Rationale:** Machine-readable format enables TC-15 measurement (count rounds to convergence), TC-16 measurement (associate rounds with quality ratings), and automated reporting. Markdown within fields preserves human readability of the critique content.

### D5: Director Agent Receives Prior-Round Summary, Not Full History

**Decision:** On round N > 1, the Director receives a summary of round N-1's feedback and the Code Agent's changes — not the full tuning log.

**Rationale:** Prevents context bloat in the Director's prompt. Full history biases the Director toward incremental nit-picking rather than fresh evaluation. Each round should be a largely independent assessment of the current render state.

### D6: Rejected Critiques Do Not Count Toward Convergence Budget

**Decision:** If the HITL disposition is `rejected`, the round is recorded but does not count toward the 5-round convergence budget. Only rounds where feedback was passed to the Code Agent count.

**Rationale:** A rejection means the Director's feedback was unusable (hallucinated, off-topic, or fundamentally wrong). The Code Agent made no changes, so no progress was possible. Counting this against the budget would penalize the tuning process for Director failures rather than genuine non-convergence.

### D7: Test Images for Spatial Tuning

**Decision:** Tuning sessions MAY use simple solid-color or gradient test images rather than AI-generated art. The geometry's spatial structure, camera motion quality, and edge-reveal behavior are independent of image content.

**Rationale:** Decouples spatial tuning from asset generation. Per AP-04, the rendering engine accepts pre-existing images — tuning should not require Flux.1 API calls. A solid red floor and solid blue walls reveal perspective distortion just as clearly as textured images. Exception: the `proof` quality final sign-off render SHOULD use realistic images to verify that the preset looks good with real content.

### D8: Manifest Mutation for Scene Isolation

**Decision:** When `isolateScene` is set, `renderTestClip()` filters the manifest's `scenes` array to only the matching scene, resets its `start_time` to 0, and removes transition settings (since there are no adjacent scenes).

**Rationale:** Tuning a single geometry+camera combination should not require rendering the entire multi-scene composition. Isolation produces a focused clip that the Director can evaluate without distraction from other scenes.

---

## Acceptance Criteria

### Visual Critique Format

- [ ] **AC-01:** The Visual Critique template includes all sections from seed Section 10.5: Overall Impression, Timestamped Observations, Priority Tweaks, Things That Work Well.
- [ ] **AC-02:** The template adds required sections beyond the seed sketch: Edge Reveals, Depth and Separation, Motion Feel, Convergence Assessment — all derived from seed Section 10.4 guidelines.
- [ ] **AC-03:** Priority labels use P1/P2 classification. P1 blocks convergence; P2 does not.
- [ ] **AC-04:** The template enforces the seed's directional-delta rule (Section 10.4 guideline 2): the format explicitly instructs the Director to use directional language, not absolute values.
- [ ] **AC-05:** The template includes a "Status: RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL" header per Section 10.3.

### HITL Circuit Breaker

- [ ] **AC-06:** The workflow protocol defines exactly four HITL dispositions: approved, modified, rejected, overridden — matching seed Section 10.3.
- [ ] **AC-07:** The protocol explicitly states that the Code Agent **never** receives unfiltered Director output (AP-09 enforcement).
- [ ] **AC-08:** The protocol includes a human sign-off step as a hard requirement for convergence (not optional, not skippable).

### Convergence Criteria

- [ ] **AC-09:** Convergence requires zero P1 issues in the most recent Director critique, per Section 10.7 criterion 1.
- [ ] **AC-10:** Convergence requires explicit human sign-off, per Section 10.7 criterion 2.
- [ ] **AC-11:** Upon convergence, `meta.json` is updated with `visual_status: 'tuned'` and `tuning_rounds: N`, per Section 10.7 criterion 4.
- [ ] **AC-12:** The convergence budget enforces ≤ 5 rounds per TC-15, with a defined escalation protocol when exceeded.

### Test Render Utility

- [ ] **AC-13:** `renderTestClip()` accepts a full manifest and produces a valid MP4 using OBJ-035's Orchestrator.
- [ ] **AC-14:** Quality presets override the manifest's resolution and fps: `draft` → 640×360@24fps, `review` → 1280×720@30fps, `proof` → 1920×1080@30fps.
- [ ] **AC-15:** `maxDuration` truncates the rendered output to at most the specified seconds. A 60-second manifest with `maxDuration: 15` renders ≤ 15 seconds.
- [ ] **AC-16:** `isolateScene` filters to a single scene. The output contains only that scene's visual content.
- [ ] **AC-17:** When `extractKeyframes` is true, 3 PNG files are written alongside the MP4 at 25%, 50%, 75% of rendered duration.
- [ ] **AC-18:** `renderTestClip()` propagates `OrchestratorError` without wrapping — error codes and causes are preserved from OBJ-035.
- [ ] **AC-19:** The `depthkit test-render` CLI subcommand accepts all `TestRenderConfig` options and prints `TestRenderResult` summary to stdout.

### Tuning Log

- [ ] **AC-20:** Each tuning objective maintains a `tuning-log.json` in its node directory conforming to the `TuningLog` schema.
- [ ] **AC-21:** Each round records: render path, Director critique (or null), HITL disposition (or null), approved feedback (or null), changes made (or null).
- [ ] **AC-22:** The tuning log's `status` transitions: `in_progress` → `converged` (on successful convergence) or `in_progress` → `abandoned` (on budget exhaustion without convergence).
- [ ] **AC-23:** Rejected rounds (HITL disposition `rejected`) do not count toward the 5-round convergence budget.

### TC-15: Convergence ≤ 5 Iterations

- [ ] **AC-24:** The measurement framework for TC-15 is defined: count `tuning_rounds` from each completed tuning objective's `meta.json`. TC-15 passes if ≥ 6 of 8 geometry tuning objectives (OBJ-059 through OBJ-066) converge in ≤ 5 rounds.
- [ ] **AC-25:** The escalation protocol for > 5 rounds is documented: log failure, escalate to human, do not continue indefinitely.

### TC-16: Director-Tuned Outperforms Blind-Authored

- [ ] **AC-26:** The measurement framework for TC-16 is defined: for at least 3 geometries, render the same scene using (a) the initial blind-authored preset (round 0, before any Director feedback) and (b) the final tuned preset (after convergence). A human evaluator rates both on a 1–5 cinematic quality scale. TC-16 passes if the tuned version scores higher in ≥ 2 of 3 comparisons.
- [ ] **AC-27:** The test render utility supports rendering with a specific version of a preset by accepting the manifest directly (the tuning session is responsible for constructing the manifest with the appropriate preset version).

### Scope Enforcement

- [ ] **AC-28:** The workflow specification explicitly lists which objective types invoke the Director Agent (tuning objectives only) and which do not (all engine, schema, integration objectives), per Section 10.6.
- [ ] **AC-29:** The specification explicitly prohibits Director Agent invocation in production rendering paths, per AP-10.

---

## Edge Cases and Error Handling

### Test Render Utility

| Scenario | Expected Behavior |
|---|---|
| `isolateScene` references a non-existent scene ID | `renderTestClip()` throws `OrchestratorError` with code `MANIFEST_INVALID`. Error message names the missing scene ID. |
| `maxDuration` is less than any single scene's duration | The first scene is truncated. Scenes that start beyond `maxDuration` are excluded. At least 1 frame is always rendered. |
| `maxDuration` is 0 or negative | Throws `Error` with message "maxDuration must be positive". Not an `OrchestratorError` — this is a config validation error, not a pipeline error. |
| Manifest has portrait orientation (1080×1920) with `quality: 'review'` | Quality preset computes dimensions respecting the manifest's aspect ratio. For 9:16: `review` → 720×1280 (height and width swapped to maintain portrait). |
| `extractKeyframes: true` but render is only 1 frame | Extract only 1 keyframe at frame 0. Output: single PNG file `{basename}_000.png`. |
| `quality: 'proof'` matches manifest's native resolution | No override needed. Resolution is unchanged. |

### Tuning Workflow

| Scenario | Expected Behavior |
|---|---|
| Director Agent produces critique without timestamps | HITL human should **reject** or **modify** to add timestamps. The protocol documents this as a common Director failure mode. |
| Director Agent prescribes absolute coordinate values | HITL human should **modify** to replace with directional deltas, or **reject**. |
| Two consecutive rounds produce identical critiques | Likely a sign the Code Agent's changes didn't address the feedback, or the Director is stuck. Human should **override** with fresh perspective or restructure the preset. |
| Human signs off but Code Agent discovers the committed parameters break a different camera path | The geometry is NOT marked `tuned` until all compatible camera paths pass. A geometry tuning objective is responsible for testing all compatible paths. |
| Director Agent is unavailable (API down, model deprecated) | The HITL human can **override** for every round, providing their own visual feedback. The Director Agent is helpful but not required — the human can be the "eyes." |

### Convergence Budget

| Scenario | Expected Behavior |
|---|---|
| Round 5 has P1 issues remaining | Escalation per D6. Human decides: extend budget, restructure, or accept-with-caveat. |
| Round 3 has zero P1 but human is not satisfied | Human does NOT sign off. Convergence is not declared. Additional rounds proceed (human uses **override** to provide their own feedback). These rounds count toward the budget. |
| All 5 rounds were `rejected` dispositions | 0 rounds count toward budget (per D6). The human should recognize the Director Agent is not providing useful feedback and switch to **override** mode. |

---

## Test Strategy

### Unit Tests: `test/unit/test-render.test.ts`

1. **Manifest cloning:** Verify `renderTestClip()` does not mutate the original manifest object. Clone a manifest, render, then assert the original is unchanged.

2. **Quality preset application — landscape:** For a 1920×1080 manifest with `quality: 'draft'`, verify the cloned manifest has `width: 640, height: 360, fps: 24`.

3. **Quality preset application — portrait:** For a 1080×1920 manifest with `quality: 'review'`, verify the cloned manifest has `width: 720, height: 1280, fps: 30` (aspect ratio preserved).

4. **maxDuration truncation:** For a manifest with 3 scenes totaling 45 seconds and `maxDuration: 15`, verify only scenes within the first 15 seconds are included, and the last included scene's duration is truncated.

5. **Scene isolation:** For a 3-scene manifest with `isolateScene: 'scene_002'`, verify the cloned manifest contains only `scene_002` with `start_time: 0` and no transitions.

6. **Invalid isolateScene:** Verify that an unknown scene ID throws `OrchestratorError` with `MANIFEST_INVALID`.

7. **maxDuration validation:** Verify `maxDuration: 0` and `maxDuration: -5` throw an error.

8. **Keyframe position calculation:** For a 10-second render at 30fps (300 frames), verify keyframe extraction targets frames 75, 150, 225 (25%, 50%, 75%).

### Integration Tests: `test/integration/test-render.test.ts`

9. **End-to-end test render:** Register a test geometry, create test images, render with `quality: 'draft'`. Verify output MP4 exists and has correct resolution via ffprobe.

10. **Keyframe extraction:** Render with `extractKeyframes: true`. Verify 3 PNG files exist with expected naming convention.

11. **Scene isolation end-to-end:** Render with `isolateScene` set. Verify the output duration matches only the isolated scene.

### Tuning Log Validation

12. **Schema compliance:** Validate a sample `tuning-log.json` against the `TuningLog` TypeScript interface (via Zod schema or type assertion).

13. **Round counting — rejected rounds excluded:** Create a tuning log with 3 rounds: round 1 approved, round 2 rejected, round 3 approved. Verify the budget-counted rounds = 2.

### TC-15 Measurement

14. **Convergence count:** After all tuning objectives complete, read `tuning_rounds` from each `meta.json`. Verify ≥ 6 of 8 have `tuning_rounds ≤ 5`.

### TC-16 Measurement

15. **Paired comparison:** For 3 geometries, human rates blind-authored (round 0) vs. tuned (final round) renders on 1–5 scale. Verify tuned > blind in ≥ 2 of 3.

---

## Integration Points

### Depends on

| Dependency | What OBJ-058 Uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`. The test render utility wraps the Orchestrator to produce test clips. All render infrastructure flows through OBJ-035. |

### Consumed by

| Downstream | How It Uses OBJ-058 |
|---|---|
| **OBJ-059** (Tune stage geometry) | Follows the HITL workflow protocol. Uses `renderTestClip()` for test renders. Records rounds in `tuning-log.json`. Uses Visual Critique template for Director feedback. Marks `visual_status: 'tuned'` on convergence. |
| **OBJ-060** (Tune tunnel geometry) | Same as OBJ-059. |
| **OBJ-061** (Tune canyon geometry) | Same as OBJ-059. |
| **OBJ-062** (Tune flyover geometry) | Same as OBJ-059. |
| **OBJ-063** (Tune diorama geometry) | Same as OBJ-059. |
| **OBJ-064** (Tune portal geometry) | Same as OBJ-059. |
| **OBJ-065** (Tune panorama geometry) | Same as OBJ-059. |
| **OBJ-066** (Tune close_up geometry) | Same as OBJ-059. |
| **OBJ-068** (Transition visual validation) | Follows the same HITL workflow. Uses `renderTestClip()` for transition test renders. Evaluates crossfade/dip_to_black quality per TC-10. |

### File Placement

```
depthkit/
  src/
    tools/
      test-render.ts              # NEW — TestRenderConfig, TestRenderResult,
                                  #       renderTestClip(), QUALITY_PRESETS
  docs/
    director-workflow.md          # NEW — Full workflow protocol (process docs)
    visual-critique-template.md   # NEW — The Visual Critique template
    director-system-prompt.md     # NEW — System prompt template for Director Agent
  nodes/
    OBJ-058/
      output.md                   # This specification
      meta.json                   # Updated with status
    OBJ-059/
      tuning-log.json             # Created by OBJ-059 session (example)
    ...
  test/
    unit/
      test-render.test.ts         # NEW — unit tests
    integration/
      test-render.test.ts         # NEW — integration tests
```

---

## Open Questions

### OQ-A: Should `renderTestClip()` support frame-range rendering?

If OBJ-035 adds `frameRange` support (OQ-B in OBJ-035), the test render utility could expose a `timeRange?: { start: number; end: number }` option for rendering a specific time window within a scene. Currently deferred — `maxDuration` + `isolateScene` covers the primary use cases.

### OQ-B: Should keyframe extraction use FFmpeg or the capture pipeline?

Two options: (a) Extract keyframes by capturing specific frames during the render loop and writing them as PNGs directly. (b) Post-process the MP4 with FFmpeg (`-vf "select='eq(n,75)'"`) to extract frames. Option (a) avoids re-decoding but requires modifying the render loop. Option (b) is simpler — a separate FFmpeg pass after the MP4 is produced. **Recommendation: option (b)** for simplicity. The FFmpeg extraction adds <1 second for 3 frames.

### OQ-C: Should the tuning log track image assets used?

Recording which test images were used in each round would enable reproducibility. Currently not specified — the render path in the tuning log implicitly captures this (the MP4 can be re-examined). Add if reproducibility becomes an issue.

### OQ-D: How should portrait-mode quality presets be computed?

Current proposal: swap width/height when the manifest's aspect ratio is < 1.0 (portrait). Alternative: always use the preset dimensions and let the orchestrator letterbox. **Recommendation: swap to maintain aspect ratio.** The Director needs to evaluate the actual viewport, not a letterboxed version.

### OQ-E: Should the workflow support asynchronous Director review?

The current protocol assumes synchronous steps (render → review → approve → implement). In practice, the Director review might happen in a separate session hours later. The tuning log's nullable fields (`director_critique: null`, `hitl_disposition: null`) support this naturally — a round can be partially completed across sessions. No additional mechanism needed.

---

I believe this spec is comprehensive and ready for challenger review. It covers all aspects of OBJ-058: the process protocol (HITL workflow, convergence criteria, scope rules), the document formats (Visual Critique template, HITL Approval Record, Director system prompt), the supporting tooling (`renderTestClip()` with quality presets), the tracking infrastructure (tuning log JSON schema, meta.json extensions), and the measurement frameworks for TC-15 and TC-16.

I'd like the challenger to verify:
1. Whether the three quality presets are well-calibrated for their purposes.
2. Whether the convergence budget (5 rounds, rejected rounds excluded) is sound.
3. Whether the test render utility's manifest mutation approach (clone + override) is correct.
4. Whether the tuning log schema captures enough information for the downstream tuning objectives.

---

## Round 2 — spec_challenger

I've reviewed the proposal carefully against the seed, the OBJ-035 dependency spec, and the downstream tuning objectives. This is a solid spec for what's fundamentally a process/workflow specification with a thin tooling layer. The Visual Critique template, HITL protocol, and convergence criteria are well-grounded in seed Sections 10.3–10.7.

Here are my challenges, ordered by severity:

---

## Major Issues

### M1: Portrait Aspect Ratio — `QUALITY_PRESETS` Contradicts Described Behavior

The spec defines `QUALITY_PRESETS` as a **fixed constant** with hardcoded dimensions:
```typescript
review: { width: 1280, height: 720, crf: 23, fps: 30 },
```

But the edge case table says: "For 9:16: `review` → 720×1280 (height and width swapped to maintain portrait)." And test strategy #3 says: "verify the cloned manifest has `width: 720, height: 1280, fps: 30`."

These are contradictory. The constant says 1280×720. The behavior says 720×1280 for portrait. An implementer looking at the constant would produce landscape output for portrait manifests.

**Fix:** Add a function signature to the interface contract that resolves quality presets with aspect-ratio awareness:

```typescript
/**
 * Resolves quality preset dimensions for a given manifest aspect ratio.
 * If manifest aspect ratio < 1.0 (portrait), width and height are swapped.
 */
export function resolveQualityDimensions(
  quality: 'draft' | 'review' | 'proof',
  manifestWidth: number,
  manifestHeight: number
): { width: number; height: number; crf: number; fps: number };
```

And update the `QUALITY_PRESETS` doc comment to say these are the **landscape** base values, with portrait computed by swapping.

### M2: `maxDuration` Truncation Algorithm Is Underspecified

The spec says `renderTestClip()` "truncates `scenes` to fit `maxDuration`" (D1) and test #4 says "the last included scene's duration is truncated." But the actual algorithm isn't defined. An implementer must decide:

1. Are scenes fully excluded if they *start* after `maxDuration`, or if they *end* after it?
2. Is the last scene's `duration` reduced, or is a `totalFrames` cap applied?
3. What happens to `transition_out` on the truncated scene? It was designed to blend into the next scene, which no longer exists.
4. What about `transition_in` on the first excluded scene that had a crossfade with the last included scene?

**Fix:** Add a design decision (D9) specifying the algorithm:

> **D9: maxDuration Truncation Algorithm**
> 
> 1. Compute each scene's end time: `end = start_time + duration`.
> 2. Include all scenes where `start_time < maxDuration`.
> 3. For the last included scene, if `end > maxDuration`, set `duration = maxDuration - start_time`.
> 4. Strip `transition_out` from the last included scene (no subsequent scene to blend into).
> 5. Strip `transition_in` from the first included scene if it was a crossfade (no preceding scene).
> 6. If no scenes have `start_time < maxDuration`, throw an error (this shouldn't happen with valid positive `maxDuration` and valid scenes).

### M3: TC-15 Pass Criteria Deviates From Seed

AC-24 defines TC-15 as: "≥ 6 of 8 geometry tuning objectives converge in ≤ 5 rounds."

But seed TC-15 says: "For a given scene geometry + camera path combination, the Director Agent → HITL → Code Agent loop reaches 'no Priority 1 issues' within 5 or fewer iterations. If it consistently takes more, the feedback format or the geometry's parameterization needs restructuring. Test on at least 3 different geometries."

The seed defines TC-15 per-combination and requires testing on ≥ 3 geometries. The spec introduces a 6/8 aggregate threshold that doesn't exist in the seed. It also ignores that each geometry may have multiple compatible camera paths — the seed says "geometry + camera path combination," not "geometry."

**Fix:** Revise AC-24 to match the seed:

> **AC-24:** TC-15 is measured per geometry+camera-path combination: each combination should converge in ≤ 5 rounds. TC-15 passes if this holds for at least 3 of the tuned geometries (each tested with their default camera path). If any combination exceeds 5 rounds, the escalation protocol is triggered and the failure is documented.

### M4: TC-16 "Round 0" Baseline Has No Capture Mechanism

AC-26 says to compare "the initial blind-authored preset (round 0, before any Director feedback)" vs. the final tuned preset. But:

1. The `TuningLog` starts at round 1. There's no "round 0" entry.
2. Nothing in the workflow protocol tells the Code Agent to save a pre-tuning render before beginning the loop.
3. The preset code will be modified in-place during tuning. Without versioning, the original preset state is lost.

**Fix:** Add a Step 0 to the workflow protocol:

> **Step 0: Baseline Capture (First Round Only)**
> Before the first Director review, the Code Agent renders a "round 0" baseline clip using the initial blind-authored preset. This render is stored in the tuning log as round 0 with `director_critique: null`, `hitl_disposition: null`, `approved_feedback: null`, `changes_made: null`. The render serves as the TC-16 comparison baseline. The Code Agent also commits a snapshot of the initial preset parameters in the `changes_made` field (or as a separate note) so the baseline can be reconstructed later.

And update the `TuningRound` interface doc to note that round 0 is the baseline round with all nullable fields set to null.

### M5: CLI Subcommand Scope Bleeds Into OBJ-046

The spec defines `depthkit test-render` as a CLI subcommand. But OBJ-046 is "CLI render command" and is listed as consuming OBJ-035. The progress map shows OBJ-046 depends on OBJ-035 and blocks OBJ-050, OBJ-070, OBJ-075, OBJ-077 — but NOT on OBJ-058.

If OBJ-058 defines a CLI subcommand, either:
- OBJ-046 should depend on OBJ-058 (but the progress map doesn't show this), or
- OBJ-058 shouldn't define CLI behavior and should leave that to OBJ-046 or a future objective.

**Fix:** Remove the CLI subcommand from OBJ-058's interface contract. OBJ-058 delivers the `renderTestClip()` library function. The CLI subcommand is noted as a recommendation for OBJ-046 (or a separate objective) in an open question. Add:

> **OQ-F: CLI subcommand for test rendering.** The `depthkit test-render` subcommand should be implemented as part of OBJ-046 or a subsequent CLI objective. This spec defines the library function `renderTestClip()` that the CLI subcommand would wrap. The recommended CLI interface is documented here for reference but is not part of OBJ-058's deliverables.

---

## Minor Issues

### m1: Keyframe Extraction Mechanism Not Committed

OQ-B discusses two approaches and recommends FFmpeg post-processing, but doesn't commit. AC-17 says keyframes are extracted but doesn't specify how. An implementer would need to decide.

**Fix:** Promote the OQ-B recommendation to a design decision. It's a simple choice with clear rationale.

### m2: `docs/` Directory Not in Seed Project Structure

The file placement puts workflow docs in `docs/`. The seed's project structure (Section 4.5) has no `docs/` directory. This isn't technically a violation (the seed structure is directional), but it introduces a new convention.

**Fix:** Either justify the `docs/` directory as a legitimate addition, or place these files in `nodes/OBJ-058/` since they're reference material for the workflow, not engine source code.

### m3: Who Initiates the Director Agent Session?

The workflow says "A session with a vision-capable LLM" but doesn't specify the operational mechanics. Is the human running a separate chat window? Is there an automated script? Does the Code Agent session pause and hand off?

**Fix:** Add a brief note to the workflow protocol clarifying that the Director review happens in a **separate LLM session** (not the Code Agent's session), initiated by the human operator. The human copies the render file/keyframes to the Director session, receives the critique, and brings it back through the HITL gate.

### m4: Audio Handling When `maxDuration` Truncates

If the manifest has audio and `maxDuration` shortens the video, the audio duration won't match. The Orchestrator will emit an `AUDIO_DURATION_MISMATCH` warning.

**Fix:** Add to the truncation algorithm: if `maxDuration` is applied, strip `composition.audio` from the cloned manifest. Test renders are for visual tuning — audio sync is irrelevant. This also speeds up the render (no muxing step).

### m5: No Zod Schema for `tuning-log.json`

The tuning log is a JSON file written and read by multiple sessions. Without validation, any session could write a malformed log that breaks subsequent sessions.

**Fix:** Add a note to the deliverables: "A Zod schema for `TuningLog` validation is provided alongside the TypeScript interfaces. Tuning sessions validate the log on read and write."

### m6: Tuning Session Startup Checklist Missing

The seed defines orientation checklists (Appendix B) for all sessions, Director sessions, and Code Agent sessions receiving feedback. OBJ-058 should define the specific checklist for tuning sessions that ties these together.

**Fix:** Add a brief "Tuning Session Checklist" to the workflow protocol that references the seed checklists and adds tuning-specific items (read the tuning log, load the current preset code, identify which camera paths to test).

---

## What's Sound

- **The Visual Critique template** is well-structured and faithfully extends seed Section 10.5. The P1/P2 classification is a good addition.
- **The HITL protocol** correctly implements all four dispositions from seed Section 10.3.
- **D6 (rejected rounds don't count)** is a smart policy decision with clear rationale.
- **D7 (test images for spatial tuning)** correctly decouples tuning from asset generation per AP-04.
- **The TuningLog schema** captures the right information for tracking the workflow.
- **The convergence budget with escalation** is practical and well-reasoned.
- **The Director Agent System Prompt template** properly constrains Director behavior.
- **The `renderTestClip()` wrapper approach** (D1) is the right call — using the real Orchestrator prevents test/production divergence.

---

Please address the 5 major and 6 minor issues. I'll verify the fixes in the next round.

---

## Round 3 — spec_author

All five major and six minor issues are valid. Here's my revised spec addressing each one:

---

# Revised Specification: OBJ-058 — Director Agent Workflow Specification

## Summary

OBJ-058 defines the complete Director Agent visual tuning workflow — the process, document formats, supporting tooling, and convergence tracking that enable the 8 geometry tuning objectives (OBJ-059 through OBJ-066) and the transition tuning objective (OBJ-068) to systematically improve scene presets using vision-capable LLM feedback gated by human approval. It codifies seed Sections 10.3–10.7 into actionable protocols, a structured critique format, a test-render utility that wraps OBJ-035's Orchestrator for quick clip generation, and a meta.json schema extension for tracking tuning rounds. It also defines the measurement frameworks for TC-15 (convergence ≤ 5 iterations) and TC-16 (Director-tuned presets outperform blind-authored).

## Deliverables

OBJ-058 produces three categories of artifact:

1. **Process Protocol** — The step-by-step HITL workflow, convergence criteria, scope rules, and anti-patterns. Lives as documentation within the OBJ-058 node directory, consumed by all tuning sessions.
2. **Document Formats** — The Visual Critique template, the HITL Approval Record format, the Director Agent system prompt template, and the Tuning Round Log format. These are structured markdown/JSON templates that tuning sessions fill in.
3. **Test Render Utility** — A Node.js module (`src/tools/test-render.ts`) that wraps OBJ-035's Orchestrator to render short test clips optimized for Director review (reduced resolution, short duration, fast turnaround).

---

## Interface Contract

### Module: `src/tools/test-render.ts`

```typescript
import type { OrchestratorResult } from '../engine/orchestrator.js';
import type { ManifestRegistry } from '../manifest/schema.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

/**
 * Configuration for a test render — optimized for fast
 * Director Agent review, not production quality.
 */
export interface TestRenderConfig {
  /**
   * The manifest to render. Can be a full Manifest object
   * or a path to a JSON file.
   */
  manifest: unknown | string;

  /** ManifestRegistry for validation. */
  registry: ManifestRegistry;

  /** GeometryRegistry for spatial data. */
  geometryRegistry: GeometryRegistry;

  /** CameraPathRegistry for camera presets. */
  cameraRegistry: CameraPathRegistry;

  /** Output path for the rendered MP4. */
  outputPath: string;

  /**
   * Base directory for resolving relative image paths.
   * Default: process.cwd()
   */
  assetsDir?: string;

  /**
   * Render quality preset. Controls resolution and encoding settings.
   *
   * - 'draft': 640×360 (landscape base), crf 28, 24fps. Fastest. For initial iteration.
   * - 'review': 1280×720 (landscape base), crf 23, 30fps. For Director Agent review.
   * - 'proof': 1920×1080 (landscape base), crf 20, 30fps. Near-production. For final sign-off.
   *
   * For portrait manifests (aspect ratio < 1.0), width and height are
   * swapped automatically via resolveQualityDimensions().
   *
   * Default: 'review'
   */
  quality?: 'draft' | 'review' | 'proof';

  /**
   * Maximum duration in seconds to render. If the manifest
   * is longer, only the first `maxDuration` seconds are rendered.
   * Useful for testing a specific camera path without rendering
   * the full composition.
   *
   * Must be positive. Throws Error if ≤ 0.
   *
   * Default: 30 (per seed Section 10.3: "short test renders,
   * 10-30 seconds").
   */
  maxDuration?: number;

  /**
   * Scene ID to isolate. If provided, only this scene is rendered
   * (with its full duration up to maxDuration). Other scenes are
   * ignored. Transitions are stripped since there are no adjacent scenes.
   *
   * Throws OrchestratorError with MANIFEST_INVALID if the scene ID
   * does not exist in the manifest.
   *
   * Default: undefined (render all scenes).
   */
  isolateScene?: string;

  /**
   * Whether to extract keyframe thumbnails alongside the MP4.
   * When true, produces PNG files at 25%, 50%, 75% of duration
   * via FFmpeg post-processing of the rendered MP4.
   *
   * Useful for Director Agent review when video playback is
   * unavailable — the Director can analyze still frames.
   *
   * Default: true
   */
  extractKeyframes?: boolean;

  /**
   * Enable GPU acceleration. Default: false (software WebGL
   * per C-11 — test renders should match production behavior).
   */
  gpu?: boolean;

  /**
   * Forward browser console to stdout. Default: true
   * (test renders are debug-oriented).
   */
  debug?: boolean;
}

/**
 * Landscape base resolution presets. For portrait manifests
 * (aspect ratio < 1.0), use resolveQualityDimensions() which
 * swaps width and height.
 */
export const QUALITY_PRESETS: Record<
  'draft' | 'review' | 'proof',
  { width: number; height: number; crf: number; fps: number }
> = {
  draft:  { width: 640,  height: 360,  crf: 28, fps: 24 },
  review: { width: 1280, height: 720,  crf: 23, fps: 30 },
  proof:  { width: 1920, height: 1080, crf: 20, fps: 30 },
};

/**
 * Resolves quality preset dimensions for a given manifest aspect ratio.
 * If the manifest's aspect ratio is < 1.0 (portrait), width and height
 * from the base preset are swapped.
 *
 * @param quality - The quality tier.
 * @param manifestWidth - The manifest's composition width.
 * @param manifestHeight - The manifest's composition height.
 * @returns Resolved dimensions, crf, and fps.
 */
export function resolveQualityDimensions(
  quality: 'draft' | 'review' | 'proof',
  manifestWidth: number,
  manifestHeight: number,
): { width: number; height: number; crf: number; fps: number };

/**
 * Result from a test render, extending OrchestratorResult
 * with review-specific metadata.
 */
export interface TestRenderResult {
  /** The underlying orchestrator result. */
  orchestratorResult: OrchestratorResult;

  /** Quality preset used. */
  quality: 'draft' | 'review' | 'proof';

  /** Resolution rendered at (may differ from manifest). */
  renderedResolution: { width: number; height: number };

  /**
   * Paths to extracted keyframe PNGs. Empty array if
   * extractKeyframes was false.
   */
  keyframePaths: string[];

  /**
   * Duration actually rendered (may be less than manifest
   * total duration if maxDuration was applied).
   */
  renderedDurationSeconds: number;

  /**
   * Scene IDs that were rendered (all scenes, or just the
   * isolated scene).
   */
  renderedSceneIds: string[];
}

/**
 * Render a test clip for Director Agent review.
 *
 * This is a thin wrapper around OBJ-035's Orchestrator that:
 * 1. Clones the manifest (original is never mutated).
 * 2. Overrides composition resolution/fps with the quality preset
 *    (via resolveQualityDimensions).
 * 3. Strips composition.audio (test renders are visual-only).
 * 4. Truncates scenes to maxDuration (per D9 algorithm).
 * 5. Optionally isolates a single scene (per D8).
 * 6. Renders via OBJ-035's Orchestrator.
 * 7. Extracts keyframe thumbnails via FFmpeg post-processing (per D10).
 *
 * @throws OrchestratorError — all errors from the underlying
 *   Orchestrator are propagated without wrapping.
 * @throws Error — if maxDuration ≤ 0.
 */
export async function renderTestClip(
  config: TestRenderConfig
): Promise<TestRenderResult>;
```

### Tuning Round Log: JSON Schema

Each tuning objective (OBJ-059 through OBJ-066, OBJ-068) tracks its rounds in a `tuning-log.json` file within its node directory. A Zod schema for `TuningLog` validation is provided alongside the TypeScript interfaces. Tuning sessions validate the log on read and write.

```typescript
/**
 * A single round of the Director Agent → HITL → Code Agent loop.
 *
 * Round 0 is the baseline capture (Step 0 of the workflow):
 * all feedback fields are null. The render serves as the TC-16
 * comparison baseline.
 *
 * Rounds 1+ are active tuning rounds with Director review and
 * HITL gating.
 */
export interface TuningRound {
  /** Round number, 0-indexed. Round 0 = baseline. */
  round: number;

  /** ISO 8601 timestamp when the test render was produced. */
  rendered_at: string;

  /** Path to the test render MP4 (relative to the node directory). */
  render_path: string;

  /** Paths to extracted keyframe PNGs. */
  keyframe_paths: string[];

  /** Quality preset used for the test render. */
  quality: 'draft' | 'review' | 'proof';

  /** Duration of the test render in seconds. */
  render_duration_seconds: number;

  /**
   * Snapshot of the initial preset parameters at the START of this round
   * (before any changes). For round 0, this captures the blind-authored
   * baseline. Stored as a JSON-serializable object whose shape is
   * specific to the geometry or camera preset being tuned.
   *
   * Required for round 0 (baseline). Optional for subsequent rounds
   * (the changes_made field captures what changed).
   */
  preset_snapshot: Record<string, unknown> | null;

  /**
   * The Director Agent's Visual Critique.
   * Stored as a markdown string following the Visual Critique Template.
   * null for round 0 (baseline) and if the Director has not yet reviewed.
   */
  director_critique: string | null;

  /**
   * The number of Priority 1 issues identified by the Director.
   * null if not yet reviewed or if round 0.
   */
  priority_1_count: number | null;

  /**
   * HITL disposition of the Director's critique.
   * null for round 0 and if human has not yet reviewed.
   */
  hitl_disposition: 'approved' | 'modified' | 'rejected' | 'overridden' | null;

  /**
   * Human's notes on the disposition. Required for 'modified',
   * 'rejected', and 'overridden'. Optional for 'approved'.
   */
  hitl_notes: string | null;

  /**
   * The feedback actually passed to the Code Agent.
   * - If disposition is 'approved': same as director_critique.
   * - If 'modified': the human's edited version.
   * - If 'rejected': null (no feedback passed).
   * - If 'overridden': the human's own feedback (director_critique ignored).
   * - Round 0: null.
   */
  approved_feedback: string | null;

  /**
   * Summary of parameter changes made by the Code Agent in
   * response to approved_feedback. Populated after the Code Agent
   * acts on the feedback. null for round 0.
   */
  changes_made: string | null;
}

/**
 * The complete tuning log for a tuning objective.
 */
export interface TuningLog {
  /** The objective ID (e.g., 'OBJ-059'). */
  objective_id: string;

  /** The geometry or preset being tuned. */
  target: string;

  /** The camera path(s) being tested. */
  camera_paths: string[];

  /** Ordered list of tuning rounds. Round 0 is the baseline. */
  rounds: TuningRound[];

  /**
   * Current convergence status.
   * 'in_progress' — rounds are ongoing.
   * 'converged' — human has signed off (no P1 issues).
   * 'abandoned' — tuning was stopped without convergence.
   */
  status: 'in_progress' | 'converged' | 'abandoned';

  /** ISO 8601 timestamp of last update. */
  updated_at: string;
}
```

### meta.json Schema Extension for Tuning Objectives

Tuning objectives (OBJ-059 through OBJ-066, OBJ-068) extend the standard `meta.json` with tuning-specific fields. These fields already exist in the seed's meta.json schema (`visual_status`, `tuning_rounds`) but their semantics are formalized here:

```typescript
interface TuningObjectiveMeta {
  // ... standard meta.json fields ...

  /**
   * Visual tuning status.
   * - null: not a tuning objective (or not yet started).
   * - 'needs_tuning': initial state for tuning objectives.
   * - 'in_progress': at least one tuning round has started.
   * - 'tuned': human has signed off. Convergence criteria met per Section 10.7.
   */
  visual_status: null | 'needs_tuning' | 'in_progress' | 'tuned';

  /**
   * Number of completed tuning rounds where feedback was passed to
   * the Code Agent (excludes round 0 baseline and rejected rounds).
   * Tracks TC-15 compliance (should reach convergence in ≤ 5).
   */
  tuning_rounds: number;
}
```

When a tuning objective converges, the session updates:
1. `meta.json`: `visual_status` → `'tuned'`, `tuning_rounds` → final count.
2. `index.json`: `visual_status` → `'tuned'` (mirrored from meta.json, managed by orchestrator).

---

## Visual Critique Template

The following markdown template is the **required format** for all Director Agent critiques. Tuning sessions provide this template to the Director Agent as part of its system prompt.

```markdown
# Visual Critique — {geometry_or_preset_name}
## Status: RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL

**Objective:** {objective_id}
**Round:** {round_number}
**Test Render:** {render_filename}
**Duration:** {duration_seconds}s
**Geometry:** {geometry_name}
**Camera Path(s):** {camera_path_names}
**Quality:** {quality_preset}

### Overall Impression
{1-2 sentences on general quality and feel. Is this convincingly 2.5D?
Does the camera motion feel cinematic or mechanical?}

### Timestamped Observations

#### {HH:MM:SS} – {HH:MM:SS} ({phase_label})
- {Observation. Must be timestamped to a specific moment.}
- {Use directional deltas: "push further back", "needs more ease-in".}
- {Do NOT prescribe coordinate values or Bezier control points.}

#### {HH:MM:SS} – {HH:MM:SS} ({phase_label})
- {Continue for each notable segment.}

### Edge Reveals
{List any moments where plane edges become visible. Include:
- Timestamp
- Which plane (by slot name)
- Direction of reveal (left/right/top/bottom edge)
- Suggested fix direction (wider plane, constrained camera range, etc.)}

### Depth and Separation
{Assessment of whether planes feel at distinct depths or flattened.
Note any planes that need to move closer/farther for better parallax.}

### Motion Feel
{Assessment of camera motion quality. Does it feel physical or
robotic? Note easing, speed, and organic quality issues.}

### Priority Tweaks (Ordered by Impact)
1. **P1: {Highest impact issue}** — {Directional fix description}
2. **P1/P2: {Next issue}** — {Directional fix description}
3. **P2: {Lower priority}** — {Directional fix description}
{Label each as P1 (must fix before convergence) or P2 (improvement, not blocking)}

### Things That Work Well (PRESERVE THESE)
- {What should NOT be changed. Critical for preventing regression.}
- {Be specific: "The floor perspective distortion at 00:08-00:15 reads correctly."}

### Convergence Assessment
{Can this converge in the next round? What is the single most impactful change?}
```

**Priority levels:**
- **P1 (Priority 1):** Must be resolved before the preset can be marked `tuned`. These are issues that would make the preset unsuitable for production: edge reveals, broken perspective, mechanical camera motion, clearly wrong depth placement.
- **P2 (Priority 2):** Desirable improvements that are not blocking. Polish-level tweaks: slightly better easing, minor depth adjustments, subtle motion refinements.

Convergence requires **zero P1 issues** in the most recent critique (per seed Section 10.7).

---

## HITL Approval Record Format

When the human reviews a Visual Critique, they produce a disposition recorded in the tuning log. The format for human feedback within the HITL step is:

```markdown
# HITL Approval — {objective_id} Round {N}

**Disposition:** {approved | modified | rejected | overridden}

## Notes
{Human's explanation of their decision. Required for modified/rejected/overridden.}

## Approved Feedback
{The actual feedback the Code Agent receives. For 'approved': copy of
Director critique. For 'modified': edited version. For 'overridden':
human's own notes. For 'rejected': this section is absent.}
```

---

## Director Agent System Prompt Template

Tuning sessions must provide the Director Agent with this system prompt (or equivalent) to constrain its behavior:

```markdown
You are the Director Agent for depthkit — a visual reviewer for 2.5D
parallax video presets. You review short test renders and produce
structured Visual Critiques.

## Your Constraints
1. You produce ONLY Visual Critiques using the provided template.
2. Every observation MUST be timestamped to a specific moment.
3. Use DIRECTIONAL DELTAS ("push further back", "needs more ease-in"),
   never absolute values ("set z=-45", "change to 0.8").
4. You do NOT write code, modify manifests, or prescribe parameter values.
5. Your critiques are RECOMMENDATIONS. A human will review and approve
   them before any Code Agent sees them.
6. Note what WORKS WELL — not just problems. Preventing regression is
   as important as fixing issues.
7. Assess against these qualities:
   - Convincing 2.5D depth (not flat, not exaggerated)
   - No edge reveals (plane boundaries never visible)
   - Camera motion feels physical (has weight, inertia, organic easing)
   - Depth separation between planes is readable
   - Overall cinematic quality appropriate for the geometry type

## You Are Reviewing
- Geometry: {geometry_name}
- Camera Path: {camera_path_name}
- Round: {round_number}
- Prior feedback (if any): {summary_of_prior_round_feedback}

Use the Visual Critique template provided.
```

---

## Workflow Protocol

### Tuning Session Startup Checklist

Every tuning session (OBJ-059 through OBJ-066, OBJ-068) begins by confirming:

- [ ] I have completed the standard session checklist (seed Appendix B.1).
- [ ] I have read this OBJ-058 workflow specification.
- [ ] I have read the `tuning-log.json` for my objective (or confirmed it does not yet exist for round 0).
- [ ] I have loaded the current preset code for the geometry/camera being tuned.
- [ ] I know which camera paths are compatible with this geometry and which are being tested this session.
- [ ] If this is round > 0: I have read the previous round's approved feedback and the changes_made summary.
- [ ] If this session will receive Director feedback: I will only accept human-approved feedback, never raw Director output (AP-09).

### Step-by-Step HITL Tuning Loop

This protocol is followed by every tuning objective (OBJ-059 through OBJ-066, OBJ-068):

**Step 0: Baseline Capture (First Round Only)**
Before the first Director review, the Code Agent:
1. Creates a test manifest using the geometry + default camera path with placeholder test images.
2. Renders a "round 0" baseline clip via `renderTestClip()` with `quality: 'review'`.
3. Records the render in `tuning-log.json` as round 0 with all feedback fields set to `null`.
4. Records a `preset_snapshot` of the initial blind-authored preset parameters (geometry slot positions/rotations/sizes, camera path start/end positions, easing, etc.) so the baseline can be reconstructed for TC-16 comparison.

This round 0 render is the TC-16 comparison baseline — the "blind-authored" version before any Director feedback.

**Step 1: Prepare Test Render**
The Code Agent (Explorer session working on the tuning objective):
1. Creates or updates a test manifest using the geometry + camera path being tuned, with placeholder test images (solid colors or simple gradients are acceptable for spatial tuning — see D7).
2. Calls `renderTestClip()` with `quality: 'review'` and `maxDuration: 30`.
3. Records the render in `tuning-log.json` as a new round entry.

**Step 2: Director Agent Review**
A **separate LLM session** with a vision-capable model (not the Code Agent's session), initiated by the human operator:
1. The human provides the Director Agent System Prompt to the vision LLM.
2. The human provides the test render MP4 (or keyframe PNGs if video input is unavailable).
3. If this is round > 1, the human provides a summary of prior-round feedback and changes.
4. The Director produces a Visual Critique following the template exactly.
5. The critique is saved in the tuning log's `director_critique` field.

**Operational note:** The human operator is the bridge between sessions. They copy render files to the Director session, receive the critique output, and bring it back to the HITL gate. The Code Agent session and the Director Agent session never communicate directly.

**Step 3: HITL Circuit Breaker**
The human operator:
1. Reviews the Director's Visual Critique.
2. Optionally watches the test render themselves.
3. Chooses a disposition:
   - **Approve:** Passes the critique to the Code Agent as-is.
   - **Modify:** Edits the critique (removing hallucinated suggestions, adjusting priorities, adding own observations) and passes the modified version.
   - **Reject:** Discards the critique entirely (e.g., if the Director clearly misunderstood the geometry or produced untimestamped vague feedback). No feedback is passed. The human may request a re-review or skip directly to Override.
   - **Override:** Ignores the critique and writes their own feedback from scratch.
4. Records the disposition in the tuning log.

**Step 4: Code Agent Implementation**
The Code Agent:
1. Receives **only** the human-approved feedback (never raw Director output — AP-09).
2. Translates directional descriptions into parameter adjustments using knowledge of the geometry/camera codebase.
3. Does NOT modify parameters that the feedback marked as "working well" unless required to fix a higher-priority issue.
4. Updates the geometry/camera preset code.
5. Records changes in the tuning log's `changes_made` field.
6. Returns to Step 1 with a new test render.

**Step 5: Convergence Check**
After each round, check the convergence criteria (Section 10.7):
1. The Director's most recent critique contains **zero P1 issues**.
2. The Human has reviewed the final render and **explicitly signed off**.
3. The Code Agent has committed the tuned parameters.
4. The tuning objective's `meta.json` is updated: `visual_status: 'tuned'`, `tuning_rounds: N`.

If converged: the tuning objective is marked `status: 'complete'` and proceeds to review.
If not converged: return to Step 1.

### Convergence Budget (TC-15)

Per TC-15, each geometry+camera-path combination should converge within **≤ 5 rounds**. Only rounds where feedback was passed to the Code Agent count toward the budget (rejected rounds do not count — see D6). Round 0 (baseline) does not count.

If the 5th budget-counted round completes and P1 issues remain:

1. **Log the failure** in the tuning log with `status: 'abandoned'` and a note explaining why convergence failed.
2. **Escalate** by updating `meta.json` with a note: "Convergence exceeded 5 rounds. Possible causes: [geometry parameterization too rigid, camera path needs restructuring, Director feedback quality declining]."
3. **Do not continue indefinitely.** The human decides whether to:
   - Allow additional rounds (with a new 3-round budget).
   - Restructure the geometry/camera preset and restart.
   - Accept the current state as "good enough" and mark `tuned` with a caveat note.

This budget prevents the hallucination-loop risk described in AP-09 — even with the HITL gate, diminishing returns set in after ~5 iterations as changes become increasingly subjective.

### Scope Rules (per Section 10.6)

The Director Agent is invoked **only** for:
- Tuning a new scene geometry (OBJ-059 through OBJ-066).
- Tuning a new camera path preset within a geometry context.
- Validating that a geometry + camera combination produces no edge reveals.
- Validating transition visual quality (OBJ-068).
- Final visual sign-off before marking a preset as `tuned`.

The Director Agent is **never** invoked for:
- Manifest schema design, Zod validation, or code architecture.
- n8n pipeline integration, audio sync, or rendering pipeline logic.
- Any production rendering (AP-10).

---

## Design Decisions

### D1: Test Render Utility as a Thin Orchestrator Wrapper

**Decision:** `renderTestClip()` wraps OBJ-035's `Orchestrator` rather than implementing a separate render path. It clones the manifest, overrides `composition.width`, `composition.height`, `composition.fps`, strips `composition.audio`, and truncates `scenes` to fit `maxDuration`.

**Rationale:** The tuning workflow must validate the same rendering path that production uses. A separate "preview renderer" risks divergence — a preset that looks good in preview but breaks in production. The quality presets only adjust resolution and encoding settings, not the spatial pipeline.

### D2: Three Quality Tiers Instead of Arbitrary Resolution

**Decision:** Fixed `draft`/`review`/`proof` presets rather than arbitrary resolution overrides.

**Rationale:** Consistent review conditions across tuning sessions. If one geometry was tuned at 480p and another at 1080p, edge-reveal detection would be inconsistent. The `review` tier (720p) balances render speed with visual clarity sufficient for Director analysis.

### D3: Keyframe Extraction for Non-Video Director Input

**Decision:** Extract 3 keyframe PNGs (at 25%, 50%, 75% of duration) alongside the MP4.

**Rationale:** Some vision LLMs handle still images better than video, or cannot accept video input at all. Keyframes provide a fallback review medium. Three frames at quartile positions capture the beginning-of-motion, peak-motion, and end-of-motion states, which are sufficient to assess depth placement, edge reveals, and overall composition. The Director Agent should still prefer video when available.

### D4: Tuning Log as JSON, Not Markdown

**Decision:** `tuning-log.json` is machine-readable JSON validated by a Zod schema. The Visual Critiques and HITL notes are stored as markdown strings within JSON fields.

**Rationale:** Machine-readable format enables TC-15 measurement (count rounds to convergence), TC-16 measurement (associate rounds with quality ratings), and automated reporting. Markdown within fields preserves human readability of the critique content. The Zod schema prevents malformed logs from propagating across sessions.

### D5: Director Agent Receives Prior-Round Summary, Not Full History

**Decision:** On round N > 1, the Director receives a summary of round N-1's feedback and the Code Agent's changes — not the full tuning log.

**Rationale:** Prevents context bloat in the Director's prompt. Full history biases the Director toward incremental nit-picking rather than fresh evaluation. Each round should be a largely independent assessment of the current render state.

### D6: Rejected Critiques Do Not Count Toward Convergence Budget

**Decision:** If the HITL disposition is `rejected`, the round is recorded but does not count toward the 5-round convergence budget. Only rounds where feedback was passed to the Code Agent (dispositions: `approved`, `modified`, `overridden`) count.

**Rationale:** A rejection means the Director's feedback was unusable (hallucinated, off-topic, or fundamentally wrong). The Code Agent made no changes, so no progress was possible. Counting this against the budget would penalize the tuning process for Director failures rather than genuine non-convergence.

### D7: Test Images for Spatial Tuning

**Decision:** Tuning sessions MAY use simple solid-color or gradient test images rather than AI-generated art. The geometry's spatial structure, camera motion quality, and edge-reveal behavior are independent of image content.

**Rationale:** Decouples spatial tuning from asset generation. Per AP-04, the rendering engine accepts pre-existing images — tuning should not require Flux.1 API calls. A solid red floor and solid blue walls reveal perspective distortion just as clearly as textured images. Exception: the `proof` quality final sign-off render SHOULD use realistic images to verify that the preset looks good with real content.

### D8: Manifest Mutation for Scene Isolation

**Decision:** When `isolateScene` is set, `renderTestClip()` filters the manifest's `scenes` array to only the matching scene, resets its `start_time` to 0, strips `transition_in` and `transition_out` (since there are no adjacent scenes), and applies `maxDuration` truncation to the isolated scene's duration.

**Rationale:** Tuning a single geometry+camera combination should not require rendering the entire multi-scene composition. Isolation produces a focused clip that the Director can evaluate without distraction from other scenes.

### D9: maxDuration Truncation Algorithm

**Decision:** When `maxDuration` is set and the manifest's total duration exceeds it, `renderTestClip()` truncates the cloned manifest as follows:

1. Compute each scene's end time: `end = start_time + duration`.
2. Include all scenes where `start_time < maxDuration`.
3. For the last included scene, if `end > maxDuration`, set `duration = maxDuration - start_time`.
4. Strip `transition_out` from the last included scene (no subsequent scene to blend into).
5. If the first included scene's `transition_in` is a `crossfade`, strip it (no preceding scene in the truncated composition).
6. Exclude all scenes where `start_time >= maxDuration`.
7. If no scenes have `start_time < maxDuration`, this is an error — impossible with positive `maxDuration` and valid scenes (which must have non-negative `start_time`).

**Rationale:** Clean truncation without dangling transitions. The truncated composition must be a valid manifest that the Orchestrator can render without errors.

### D10: Keyframe Extraction via FFmpeg Post-Processing

**Decision:** Keyframes are extracted by running a separate FFmpeg process on the rendered MP4 after the Orchestrator completes. FFmpeg seeks to the target timestamps (25%, 50%, 75% of duration) and writes single-frame PNGs.

**Rationale:** Simpler than modifying the render loop to capture specific frames. The FFmpeg extraction adds < 1 second for 3 frames and does not couple keyframe logic to the orchestrator's frame pipeline.

**Output naming:** Keyframe PNGs are written to the same directory as the output MP4, named `{basename}_025.png`, `{basename}_050.png`, `{basename}_075.png`. For a render with only 1 frame, a single keyframe `{basename}_000.png` is extracted at frame 0.

### D11: Audio Stripped from Test Renders

**Decision:** `renderTestClip()` always strips `composition.audio` from the cloned manifest before rendering.

**Rationale:** Test renders are for visual tuning — audio sync is irrelevant. Stripping audio avoids `AUDIO_DURATION_MISMATCH` warnings when `maxDuration` truncates the video, and skips the muxing step for faster turnaround.

---

## Acceptance Criteria

### Visual Critique Format

- [ ] **AC-01:** The Visual Critique template includes all sections from seed Section 10.5: Overall Impression, Timestamped Observations, Priority Tweaks, Things That Work Well.
- [ ] **AC-02:** The template adds required sections beyond the seed sketch: Edge Reveals, Depth and Separation, Motion Feel, Convergence Assessment — all derived from seed Section 10.4 guidelines.
- [ ] **AC-03:** Priority labels use P1/P2 classification. P1 blocks convergence; P2 does not.
- [ ] **AC-04:** The template enforces the seed's directional-delta rule (Section 10.4 guideline 2): the format explicitly instructs the Director to use directional language, not absolute values.
- [ ] **AC-05:** The template includes a "Status: RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL" header per Section 10.3.

### HITL Circuit Breaker

- [ ] **AC-06:** The workflow protocol defines exactly four HITL dispositions: approved, modified, rejected, overridden — matching seed Section 10.3.
- [ ] **AC-07:** The protocol explicitly states that the Code Agent **never** receives unfiltered Director output (AP-09 enforcement).
- [ ] **AC-08:** The protocol includes a human sign-off step as a hard requirement for convergence (not optional, not skippable).

### Convergence Criteria

- [ ] **AC-09:** Convergence requires zero P1 issues in the most recent Director critique, per Section 10.7 criterion 1.
- [ ] **AC-10:** Convergence requires explicit human sign-off, per Section 10.7 criterion 2.
- [ ] **AC-11:** Upon convergence, `meta.json` is updated with `visual_status: 'tuned'` and `tuning_rounds: N`, per Section 10.7 criterion 4.
- [ ] **AC-12:** The convergence budget enforces ≤ 5 rounds per TC-15, with a defined escalation protocol when exceeded.

### Test Render Utility

- [ ] **AC-13:** `renderTestClip()` accepts a full manifest and produces a valid MP4 using OBJ-035's Orchestrator.
- [ ] **AC-14:** Quality presets override the manifest's resolution and fps. For landscape manifests: `draft` → 640×360@24fps, `review` → 1280×720@30fps, `proof` → 1920×1080@30fps. For portrait manifests: width and height are swapped (e.g., `review` → 720×1280@30fps).
- [ ] **AC-15:** `maxDuration` truncates the rendered output per the D9 algorithm. A 60-second manifest with `maxDuration: 15` renders ≤ 15 seconds. Transitions on truncated boundaries are stripped.
- [ ] **AC-16:** `isolateScene` filters to a single scene. The output contains only that scene's visual content. The isolated scene's `start_time` is reset to 0 and transitions are stripped.
- [ ] **AC-17:** When `extractKeyframes` is true, PNG files are written alongside the MP4 at 25%, 50%, 75% of rendered duration via FFmpeg post-processing.
- [ ] **AC-18:** `renderTestClip()` propagates `OrchestratorError` without wrapping — error codes and causes are preserved from OBJ-035.
- [ ] **AC-19:** `renderTestClip()` does not mutate the original manifest object — it operates on a deep clone.
- [ ] **AC-20:** `renderTestClip()` always strips `composition.audio` from the cloned manifest (D11).

### Tuning Log

- [ ] **AC-21:** Each tuning objective maintains a `tuning-log.json` in its node directory conforming to the `TuningLog` Zod schema.
- [ ] **AC-22:** Round 0 is the baseline capture with all feedback fields set to `null` and `preset_snapshot` populated with the initial blind-authored preset parameters.
- [ ] **AC-23:** Each round ≥ 1 records: render path, Director critique (or null), HITL disposition (or null), approved feedback (or null), changes made (or null).
- [ ] **AC-24:** The tuning log's `status` transitions: `in_progress` → `converged` (on successful convergence) or `in_progress` → `abandoned` (on budget exhaustion without convergence).
- [ ] **AC-25:** Rejected rounds (HITL disposition `rejected`) and round 0 (baseline) do not count toward the 5-round convergence budget.

### TC-15: Convergence ≤ 5 Iterations

- [ ] **AC-26:** TC-15 is measured per geometry+camera-path combination: each combination should converge in ≤ 5 budget-counted rounds. TC-15 passes if this holds for at least 3 of the tuned geometries (each tested with their default camera path). If any combination exceeds 5 rounds, the escalation protocol is triggered and the failure is documented.
- [ ] **AC-27:** The escalation protocol for > 5 rounds is documented: log failure, escalate to human, do not continue indefinitely.

### TC-16: Director-Tuned Outperforms Blind-Authored

- [ ] **AC-28:** The measurement framework for TC-16 is defined: for at least 3 geometries, render the same scene using (a) the round 0 baseline preset snapshot and (b) the final tuned preset. A human evaluator rates both on a 1–5 cinematic quality scale. TC-16 passes if the tuned version scores higher in ≥ 2 of 3 comparisons.
- [ ] **AC-29:** Round 0 baseline presets are preserved in `tuning-log.json` via the `preset_snapshot` field, enabling reconstruction for TC-16 comparison.

### Scope Enforcement

- [ ] **AC-30:** The workflow specification explicitly lists which objective types invoke the Director Agent (tuning objectives only) and which do not (all engine, schema, integration objectives), per Section 10.6.
- [ ] **AC-31:** The specification explicitly prohibits Director Agent invocation in production rendering paths, per AP-10.

---

## Edge Cases and Error Handling

### Test Render Utility

| Scenario | Expected Behavior |
|---|---|
| `isolateScene` references a non-existent scene ID | `renderTestClip()` throws `OrchestratorError` with code `MANIFEST_INVALID`. Error message names the missing scene ID. |
| `maxDuration` is less than any single scene's duration | The first scene is truncated to `maxDuration` seconds. Scenes that start at or beyond `maxDuration` are excluded. At least 1 frame is always rendered. |
| `maxDuration` is 0 or negative | Throws `Error` with message "maxDuration must be positive". Not an `OrchestratorError` — this is a config validation error, not a pipeline error. |
| Manifest has portrait orientation (1080×1920) with `quality: 'review'` | `resolveQualityDimensions()` detects aspect ratio < 1.0, swaps width/height → 720×1280@30fps. |
| `extractKeyframes: true` but render is only 1 frame | Extract only 1 keyframe at frame 0. Output: single PNG file `{basename}_000.png`. |
| `quality: 'proof'` with a 1920×1080 landscape manifest | Resolution matches — no override needed. CRF and fps are still applied from the preset. |
| Manifest has `composition.audio` defined | Audio is stripped from the clone. No audio-related warnings or muxing. |
| `isolateScene` + `maxDuration` both set | Scene is isolated first (reset to `start_time: 0`), then its duration is truncated to `maxDuration` if needed. |
| Manifest string path provided instead of object | `renderTestClip()` loads the file first (via `loadManifestFromFile`), then clones and mutates. |

### Tuning Workflow

| Scenario | Expected Behavior |
|---|---|
| Director Agent produces critique without timestamps | HITL human should **reject** or **modify** to add timestamps. The protocol documents this as a common Director failure mode. |
| Director Agent prescribes absolute coordinate values | HITL human should **modify** to replace with directional deltas, or **reject**. |
| Two consecutive rounds produce identical critiques | Likely a sign the Code Agent's changes didn't address the feedback, or the Director is stuck. Human should **override** with fresh perspective or restructure the preset. |
| Human signs off but Code Agent discovers the committed parameters break a different camera path | The geometry is NOT marked `tuned` until all compatible camera paths pass. A geometry tuning objective is responsible for testing all compatible paths. |
| Director Agent is unavailable (API down, model deprecated) | The HITL human can **override** for every round, providing their own visual feedback. The Director Agent is helpful but not required — the human can serve as the "eyes" directly. |

### Convergence Budget

| Scenario | Expected Behavior |
|---|---|
| Round 5 (budget-counted) has P1 issues remaining | Escalation per the convergence budget protocol. Human decides: extend budget, restructure, or accept-with-caveat. |
| Round 3 has zero P1 but human is not satisfied | Human does NOT sign off. Convergence is not declared. Additional rounds proceed (human uses **override** to provide their own feedback). These rounds count toward the budget. |
| All 5 rounds were `rejected` dispositions | 0 rounds count toward budget (per D6). The human should recognize the Director Agent is not providing useful feedback and switch to **override** mode. |

---

## Test Strategy

### Unit Tests: `test/unit/test-render.test.ts`

1. **Manifest cloning:** Verify `renderTestClip()` does not mutate the original manifest object. Clone a manifest, render, then assert the original is unchanged.

2. **Quality preset application — landscape:** For a 1920×1080 manifest with `quality: 'draft'`, verify the cloned manifest has `width: 640, height: 360, fps: 24`.

3. **Quality preset application — portrait:** For a 1080×1920 manifest with `quality: 'review'`, verify `resolveQualityDimensions()` returns `{ width: 720, height: 1280, crf: 23, fps: 30 }`.

4. **maxDuration truncation — basic:** For a manifest with 3 scenes totaling 45 seconds and `maxDuration: 15`, verify only scenes within the first 15 seconds are included, and the last included scene's duration is truncated to fit.

5. **maxDuration truncation — transition stripping:** Verify `transition_out` is stripped from the last included scene when the manifest is truncated.

6. **Scene isolation:** For a 3-scene manifest with `isolateScene: 'scene_002'`, verify the cloned manifest contains only `scene_002` with `start_time: 0` and no transitions.

7. **Invalid isolateScene:** Verify that an unknown scene ID throws `OrchestratorError` with `MANIFEST_INVALID`.

8. **maxDuration validation:** Verify `maxDuration: 0` and `maxDuration: -5` throw an `Error` with the message "maxDuration must be positive".

9. **Audio stripping:** Verify that a manifest with `composition.audio` set has it removed in the clone.

10. **Keyframe position calculation:** For a 10-second render at 30fps (300 frames), verify keyframe extraction targets timestamps at 2.5s, 5.0s, 7.5s.

11. **resolveQualityDimensions — landscape:** `resolveQualityDimensions('review', 1920, 1080)` returns `{ width: 1280, height: 720, crf: 23, fps: 30 }`.

12. **resolveQualityDimensions — portrait:** `resolveQualityDimensions('review', 1080, 1920)` returns `{ width: 720, height: 1280, crf: 23, fps: 30 }`.

13. **resolveQualityDimensions — square:** `resolveQualityDimensions('review', 1080, 1080)` returns `{ width: 1280, height: 720, crf: 23, fps: 30 }` (landscape base, aspect ratio = 1.0 is not < 1.0).

### Integration Tests: `test/integration/test-render.test.ts`

14. **End-to-end test render:** Register a test geometry, create test images, render with `quality: 'draft'`. Verify output MP4 exists and has correct resolution via ffprobe.

15. **Keyframe extraction:** Render with `extractKeyframes: true`. Verify 3 PNG files exist with expected naming convention (`_025.png`, `_050.png`, `_075.png`).

16. **Scene isolation end-to-end:** Render with `isolateScene` set. Verify the output duration matches only the isolated scene.

17. **maxDuration end-to-end:** Render a multi-scene manifest with `maxDuration: 5`. Verify output duration ≤ 5 seconds.

### Tuning Log Validation

18. **Zod schema compliance:** Validate a sample `tuning-log.json` against the `TuningLog` Zod schema. Verify it accepts valid logs and rejects malformed ones (missing required fields, invalid enum values).

19. **Round counting — rejected rounds excluded:** Create a tuning log with rounds 0, 1, 2, 3. Round 0 is baseline, round 1 approved, round 2 rejected, round 3 approved. Budget-counted rounds = 2.

### TC-15 Measurement

20. **Convergence count:** After all tuning objectives complete, read `tuning_rounds` from each `meta.json`. Verify the count per geometry+default-camera-path combination is ≤ 5 for at least 3 geometries.

### TC-16 Measurement

21. **Paired comparison:** For 3 geometries, human rates round 0 baseline render vs. final tuned render on 1–5 scale. Verify tuned > blind in ≥ 2 of 3.

---

## Integration Points

### Depends on

| Dependency | What OBJ-058 Uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`. The test render utility wraps the Orchestrator to produce test clips. All render infrastructure flows through OBJ-035. |

### Consumed by

| Downstream | How It Uses OBJ-058 |
|---|---|
| **OBJ-059** (Tune stage geometry) | Follows the HITL workflow protocol. Uses `renderTestClip()` for test renders. Records rounds in `tuning-log.json`. Uses Visual Critique template for Director feedback. Marks `visual_status: 'tuned'` on convergence. |
| **OBJ-060** (Tune tunnel geometry) | Same as OBJ-059. |
| **OBJ-061** (Tune canyon geometry) | Same as OBJ-059. |
| **OBJ-062** (Tune flyover geometry) | Same as OBJ-059. |
| **OBJ-063** (Tune diorama geometry) | Same as OBJ-059. |
| **OBJ-064** (Tune portal geometry) | Same as OBJ-059. |
| **OBJ-065** (Tune panorama geometry) | Same as OBJ-059. |
| **OBJ-066** (Tune close_up geometry) | Same as OBJ-059. |
| **OBJ-068** (Transition visual validation) | Follows the same HITL workflow. Uses `renderTestClip()` for transition test renders. Evaluates crossfade/dip_to_black quality per TC-10. |

### File Placement

```
depthkit/
  src/
    tools/
      test-render.ts              # NEW — TestRenderConfig, TestRenderResult,
                                  #       renderTestClip(), QUALITY_PRESETS,
                                  #       resolveQualityDimensions()
      tuning-log-schema.ts        # NEW — Zod schema for TuningLog validation
  nodes/
    OBJ-058/
      output.md                   # This specification
      meta.json                   # Updated with status
      director-workflow.md        # Full workflow protocol (process docs)
      visual-critique-template.md # The Visual Critique template
      director-system-prompt.md   # System prompt template for Director Agent
    OBJ-059/
      tuning-log.json             # Created by OBJ-059 session (example)
    ...
  test/
    unit/
      test-render.test.ts         # NEW — unit tests
    integration/
      test-render.test.ts         # NEW — integration tests
```

**Note on file placement:** Process documentation (workflow protocol, templates, system prompt) lives in `nodes/OBJ-058/` rather than a `docs/` directory because these are reference material for the workflow, not engine source code. The seed's project structure (Section 4.5) has no `docs/` directory, and these files are logically part of OBJ-058's output artifacts. Downstream tuning sessions reference them from the node directory.

---

## Open Questions

### OQ-A: Should `renderTestClip()` support frame-range rendering?

If OBJ-035 adds `frameRange` support (OQ-B in OBJ-035), the test render utility could expose a `timeRange?: { start: number; end: number }` option for rendering a specific time window within a scene. Currently deferred — `maxDuration` + `isolateScene` covers the primary use cases.

### OQ-B: Should the tuning log track image assets used?

Recording which test images were used in each round would enable reproducibility. Currently not specified — the render path in the tuning log implicitly captures this (the MP4 can be re-examined). Add if reproducibility becomes an issue.

### OQ-C: Should the workflow support asynchronous Director review?

The current protocol assumes synchronous steps (render → review → approve → implement). In practice, the Director review might happen in a separate session hours later. The tuning log's nullable fields (`director_critique: null`, `hitl_disposition: null`) support this naturally — a round can be partially completed across sessions. No additional mechanism needed.

### OQ-D: How should square (1:1) aspect ratios be handled?

Current decision: aspect ratio ≥ 1.0 uses landscape base dimensions. For 1:1 manifests (e.g., 1080×1080), `resolveQualityDimensions()` returns the landscape preset (1280×720 for `review`). This doesn't preserve the 1:1 ratio. If 1:1 video becomes important, add a third branch: `min(preset.width, preset.height) × min(preset.width, preset.height)`. Deferred — no 1:1 requirement in the seed.

### OQ-E: CLI subcommand for test rendering

The `depthkit test-render` subcommand should be implemented as part of OBJ-046 or a subsequent CLI objective. This spec defines the library function `renderTestClip()` that the CLI subcommand would wrap. The recommended CLI interface is:

```
depthkit test-render <manifest> [options]

Arguments:
  manifest              Path to manifest JSON file

Options:
  --output, -o <path>   Output MP4 path (default: ./test-render-{timestamp}.mp4)
  --quality, -q <level> draft|review|proof (default: review)
  --max-duration <sec>  Maximum seconds to render (default: 30)
  --scene <id>          Isolate a single scene by ID
  --no-keyframes        Skip keyframe extraction
  --gpu                 Enable GPU acceleration
  --assets-dir <path>   Base directory for image resolution
```

This is documented here for reference but is not part of OBJ-058's deliverables.

---

## Changes from Round 1 (Addressing Challenger Feedback)

| Issue | Resolution |
|---|---|
| **M1:** Portrait aspect ratio — `QUALITY_PRESETS` contradiction | Added `resolveQualityDimensions()` function. Updated `QUALITY_PRESETS` doc comment to say "landscape base values." Added unit tests #11, #12, #13 for all aspect ratio cases. |
| **M2:** maxDuration truncation underspecified | Added D9 with full algorithm: include scenes where `start_time < maxDuration`, truncate last scene, strip dangling transitions. Added unit test #5. |
| **M3:** TC-15 pass criteria deviates from seed | Revised AC-26 to match seed: per geometry+camera-path combination, tested on ≥ 3 geometries. Removed the 6/8 aggregate threshold. |
| **M4:** TC-16 round 0 baseline not captured | Added Step 0 (Baseline Capture) to the workflow protocol. Added `preset_snapshot` field to `TuningRound`. Updated `TuningRound` doc comment to note round 0. Added AC-22, AC-29. |
| **M5:** CLI subcommand scope bleeds into OBJ-046 | Removed CLI subcommand from interface contract and acceptance criteria. Moved to OQ-E as a recommendation for OBJ-046. |
| **m1:** Keyframe extraction not committed | Promoted to D10: FFmpeg post-processing approach committed with rationale. |
| **m2:** `docs/` directory not in seed | Moved all process docs to `nodes/OBJ-058/` directory. Added justification note. |
| **m3:** Who initiates Director session | Added operational note to Step 2 clarifying separate session initiated by human operator. |
| **m4:** Audio handling with maxDuration | Added D11: audio always stripped from test renders. Added AC-20. Added unit test #9. |
| **m5:** No Zod schema for tuning-log.json | Added `tuning-log-schema.ts` to file placement. Updated D4 to mention Zod schema. Updated AC-21 to reference Zod schema. |
| **m6:** Tuning session startup checklist | Added "Tuning Session Startup Checklist" section to workflow protocol. |

---

I believe all 5 major and 6 minor issues have been addressed. I'd like the challenger to verify each resolution and approve the spec if satisfactory.

---

## Round 4 — spec_challenger

I've verified every Round 2 issue against the Round 3 revision. All 5 major and 6 minor issues are structurally resolved in the revised spec. Let me do a final sweep for any new issues introduced by the revisions...

**Verification results:**

| Issue | Status | Verified How |
|---|---|---|
| M1 (Portrait) | ✅ Fixed | `resolveQualityDimensions()` in interface contract; `QUALITY_PRESETS` marked "landscape base"; tests 11-13 cover landscape/portrait/square |
| M2 (maxDuration) | ✅ Fixed | D9 has complete 7-step algorithm; test #5 covers truncation + transition stripping |
| M3 (TC-15) | ✅ Fixed | AC-26 now says "per geometry+camera-path combination… at least 3 geometries" matching seed |
| M4 (TC-16 baseline) | ✅ Fixed | Step 0 added; `preset_snapshot` field on `TuningRound`; AC-22 and AC-29 verify |
| M5 (CLI scope) | ✅ Fixed | CLI removed from deliverables/ACs, lives in OQ-E as recommendation |
| m1-m6 | ✅ All fixed | D10 commits keyframes via FFmpeg; docs in `nodes/OBJ-058/`; Step 2 operational note; D11 strips audio; Zod schema in file placement; checklist added |

No new issues introduced. The spec is clean, implementable, and stays within scope.

CONCLUSION:

The specification for OBJ-058 defines the Director Agent visual tuning workflow comprising: (1) a process protocol with HITL circuit breaker, convergence criteria, and scope rules grounded in seed Sections 10.3–10.7; (2) structured document formats including Visual Critique template, HITL Approval Record, Director system prompt, and TuningLog JSON schema; (3) a `renderTestClip()` utility wrapping OBJ-035's Orchestrator with quality presets, duration truncation, scene isolation, and keyframe extraction. It provides measurement frameworks for TC-15 (≤5 round convergence) and TC-16 (tuned vs. blind-authored comparison via round-0 baseline capture). All 9 downstream tuning objectives (OBJ-059–066, OBJ-068) consume this spec.

Let me write the files now.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Now let me read the current meta.json before updating it:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-058/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-058",
     3→  "description": "Director Agent workflow specification -- critique format per Sections 10.4-10.5 (timestamped observations, directional deltas not absolute values, edge reveal reporting, physics/motion feel descriptions). HITL circuit breaker process per Section 10.3 (human reviews, approves/modifies/rejects/overrides). Convergence criteria per Section 10.7 (no Priority 1 issues, human sign-off, visual_status marked tuned). Visual Critique template. Covers TC-15 (convergence in <=5 iterations) and TC-16 (Director-tuned presets outperform blind-authored).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. High priority. All 8 tuning objectives (OBJ-059 through OBJ-066) depend on this."
... [truncated]
Now let me write the output.md and updated meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-058/output.md",
  "content": "# Specification: OBJ-058 \u2014 Director Agent Workflow Specification\n\n## Summary\n\nOBJ-058 defines the complete Director Agent visual tuning workflow \u2014 the process, document formats, supporting tooling, and convergence tracking that enable the 8 geometry tuning objectives (OBJ-059 through OBJ-066) and the transition tuning objective (OBJ-068) to systematically improve scene presets using vision-capable LLM feedback gated by human approval. It codifies seed Sections 10.3\u201310.7 into actionable protocols, a structured critique format, a test-render utility that wraps OBJ-035's Orchestrator for quick clip generation, and a meta.json schema extension for tracking tuning rounds. It also defines the measurement frameworks for TC-15 (convergence in \u2264 5 iterations) and TC-16 (Director-tuned presets outperform blind-authored).\n\n## Deliverables\n\nOBJ-058 produces three categories of artifact:\n\n1. **Process Protocol** \u2014 The step-by-step HITL workflow, convergence criteria, scope rules, and anti-patterns. Lives as documentation within the OBJ-058 node directory, consumed by all tuning sessions.\n2. **Document Formats** \u2014 The Visual Critique template, the HITL Approval Record format, the Director Agent system prompt template, and the Tuning Round Log format. These are structured markdown/JSON templates that tuning sessions fill in.\n3. **Test Render Utility** \u2014 A Node.js module (`src/tools/test-render.ts`) that wraps OBJ-035's Orchestrator to render short test clips optimized for Director review (reduced resolution, short duration, fast turnaround).\n\n---\n\n## Interface Contract\n\n### Module: `src/tools/test-render.ts`\n\n```typescript\nimport type { OrchestratorResult } from '../engine/orchestrator.js';\nimport type { ManifestRegistry } from '../manifest/schema.js';\nimport type { GeometryRegistry } from '../scene
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-058/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-058/meta.json",
  "content": "{\n  \"id\": \"OBJ-058\",\n  \"description\": \"Director Agent workflow specification -- critique format per Sections 10.4-10.5 (timestamped observations, directional deltas not absolute values, edge reveal reporting, physics/motion feel descriptions). HITL circuit breaker process per Section 10.3 (human reviews, approves/modifies/rejects/overrides). Convergence criteria per Section 10.7 (no Priority 1 issues, human sign-off, visual_status marked tuned). Visual Critique template. Covers TC-15 (convergence in <=5 iterations) and TC-16 (Director-tuned presets outperform blind-authored).\",\n  \"category\": \"integration\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:00:00Z\",\n  \"depends_on\": [\"OBJ-035\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 4 integration. High priority. All 8 tuning objectives (OBJ-059 through OBJ-066) plus OBJ-068 depend on this. Spec defines: (1) HITL workflow protocol with 4 dispositions, (2) Visual Critique template with P1/P2 classification, (3) renderTestClip() utility wrapping OBJ-035 Orchestrator, (4) TuningLog JSON schema with Zod validation, (5) TC-15/TC-16 measurement frameworks, (6) Director Agent system prompt template.\",\n  \"status\": \"complete\",\n  \"review_status\": \"pending\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-058/meta.json has been updated successfully.
Now let me commit:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git status -u",
  "description": "Show working tree status"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commits"
}
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-058/meta.json

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
[Tool Result] bd72df5 OBJ-041: Geometry-camera spatial compatibility validation spec
37cb4b1 spec(OBJ-046): CLI interface specification — render, validate, preview commands
593383f spec(OBJ-038): audio sync and scene timing specification
f831439 OBJ-035: Orchestrator spec - main render loop coordinating Puppeteer, FFmpeg, virtualized clock
6939369 OBJ-029: Tunnel push forward camera path preset specification

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-058/output.md nodes/OBJ-058/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-058): Director Agent workflow specification \u2014 HITL tuning protocol, Visual Critique template, test render utility\n\nDefines the complete Director Agent visual tuning workflow for OBJ-059\u2013066 and OBJ-068:\n- HITL circuit breaker with 4 dispositions (approve/modify/reject/override)\n- Visual Critique template with P1/P2 priority classification\n- renderTestClip() utility wrapping OBJ-035 Orchestrator (draft/review/proof quality tiers)\n- TuningLog JSON schema with Zod validation for round tracking\n- TC-15 (<=5 round convergence) and TC-16 (tuned vs blind comparison) measurement frameworks\n- Director Agent system prompt template constraining feedback to directional deltas\n- Round 0 baseline capture for TC-16 paired comparison\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-058 spec files"
}
[Tool Result] [master 7bceeb2] spec(OBJ-058): Director Agent workflow specification — HITL tuning protocol, Visual Critique template, test render utility
 2 files changed, 913 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-058/output.md
Committed. The specification for OBJ-058 is now written to `nodes/OBJ-058/output.md` and `meta.json` updated, with commit `7bceeb2`.
