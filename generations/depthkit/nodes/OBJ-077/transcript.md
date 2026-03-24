# Deliberation Transcript: OBJ-077

---

## Round 1 — spec_author

# Proposed Specification: OBJ-077 — End-to-End Integration Test Plan

## Summary

OBJ-077 delivers a **test plan document** (`nodes/OBJ-077/test-plan.md`) that defines the procedures, fixtures, environment requirements, and pass/fail criteria for verifying four seed Success Criteria: SC-01 (end-to-end rendering), SC-03 (performance target), SC-05 (n8n integration), and SC-06 (manifest validation completeness). This is a specification of *what to test and how*, not test code — OBJ-078 executes these procedures. The plan must be precise enough that an agent executing OBJ-078 can follow it without ambiguity.

## Interface Contract

OBJ-077 produces no code module. Its deliverable is a structured test plan document. However, the plan specifies **test fixture contracts** — the manifests, images, and audio files that OBJ-078 must create or use.

### Deliverable: `nodes/OBJ-077/test-plan.md`

A markdown document containing four test suites (one per success criterion), each with:

```typescript
/**
 * Conceptual structure of each test procedure in the plan.
 * Not a runtime type — describes the shape of each documented procedure.
 */
interface TestProcedure {
  /** Unique identifier, e.g., "SC01-01" */
  id: string;
  /** Which success criterion this verifies */
  successCriterion: 'SC-01' | 'SC-03' | 'SC-05' | 'SC-06';
  /** Human-readable title */
  title: string;
  /** Preconditions that must be true before execution */
  preconditions: string[];
  /** Ordered steps to execute */
  steps: string[];
  /** What constitutes a pass */
  passConditions: string[];
  /** What constitutes a fail */
  failConditions: string[];
  /** Relevant testable claims from seed Section 5 */
  testableClaimRefs: string[];
  /** Relevant seed constraints */
  constraintRefs: string[];
}
```

### Test Fixture Contracts

The plan defines the following fixtures that OBJ-078 must prepare:

#### Fixture F-01: SC-01 Benchmark Manifest

A complete manifest exercising the full pipeline:

- **Scenes:** 5, using at least 3 distinct geometry types from the verified set (OBJ-018 stage, OBJ-019 tunnel, OBJ-020 canyon, OBJ-021 flyover are verified; diorama OBJ-022 and beyond are open — fixture must use only verified geometries).
- **Total duration:** 60 seconds (driven by audio file length in `audio_proportional` mode, or explicit scene durations summing to 60s).
- **Camera presets:** At least 3 distinct presets from the verified set (OBJ-026 `static`, OBJ-027 `slow_push_forward`, OBJ-028 `slow_pull_back`, OBJ-029 `lateral_track_left`, OBJ-030 `crane_up`, OBJ-031 `gentle_float` are verified).
- **Transitions:** At least one `crossfade` and one `dip_to_black` transition between scenes. At least one `cut`.
- **Audio:** A WAV or MP3 file of approximately 60 seconds. Can be silence, a tone, or actual narration — content irrelevant, duration critical.
- **Images:** One image per required slot per scene. Solid-color PNGs are acceptable for functional correctness; real AI-generated images are preferred for visual quality assessment but not required.
- **No manual coordinates:** The manifest uses only geometry names, slot keys, and camera preset names. No `position_override`, no `rotation_override`. This directly tests TC-04 and SC-02's constraint.
- **Resolution:** 1920×1080, 30fps.

#### Fixture F-02: SC-03 Performance Benchmark Manifest

Same as F-01 but with explicit constraints for benchmarking:

- **Images:** 5 textured planes per scene (the maximum typical load per C-08).
- **Resolution:** 1920×1080 at 30fps (1,800 frames total).
- **GPU mode:** `software` (SwiftShader) for the baseline benchmark. A second run with `hardware` or `auto` for the accelerated benchmark (if GPU available).

#### Fixture F-03: SC-06 Valid Manifest Corpus

A set of **at least 20 valid manifests** covering:

1. Single scene, single plane, no transitions, no audio.
2. Single scene, all slots filled for a geometry.
3. Multi-scene with `cut` transitions only.
4. Multi-scene with `crossfade` transitions.
5. Multi-scene with `dip_to_black` transitions.
6. Mixed transition types across scenes.
7. Audio with explicit scene durations matching audio length.
8. Audio with `audio_proportional` timing (durations as weights).
9. Portrait mode (1080×1920).
10. 24fps variant.
11. 30fps variant.
12. Minimum duration scene (0.1s — just a few frames).
13. Scene using `camera_params.speed` override.
14. Scene using `camera_params.easing` override.
15. Scene with optional slots omitted (only required slots filled).
16. Scene with `scale` on a `PlaneRef`.
17. Manifest with scenes not in `start_time` order (valid, triggers warning).
18. Every verified geometry type used at least once across the corpus.
19. Every verified camera preset used at least once across the corpus.
20. A manifest exercising the maximum scene count tested in development (10+ scenes).

Each manifest must render without error. The test verifies that `ffprobe` reports a valid H.264 MP4 with correct resolution, fps, and approximate duration.

#### Fixture F-04: SC-06 Invalid Manifest Corpus

A set of **at least 25 deliberately broken manifests**, each targeting a specific validation rule. Each manifest must fail validation with a specific, predictable error code:

1. Missing `version` field → structural validation error.
2. `version: "1.0"` (wrong version) → structural error.
3. Missing `composition` field → structural error.
4. `composition.width: 0` → structural error (non-positive).
5. `composition.fps: 0` → structural error.
6. Empty `scenes` array → structural error (min 1 scene).
7. Scene missing `geometry` field → structural error.
8. Scene missing `duration` → structural error.
9. Scene with `duration: -1` → structural error (non-positive).
10. Scene with unknown geometry name → `UNKNOWN_GEOMETRY`.
11. Scene with unknown camera name → `UNKNOWN_CAMERA`.
12. Scene with camera incompatible with geometry → `INCOMPATIBLE_CAMERA`.
13. Scene missing required slot for geometry → `MISSING_REQUIRED_SLOT`.
14. Scene with extra slot not defined by geometry → `UNKNOWN_SLOT`.
15. Scene with `transition_in: crossfade` on the first scene with no preceding scene → `CROSSFADE_NO_ADJACENT` (per OBJ-016).
16. Duplicate scene IDs → validation error.
17. Scene with `start_time` before previous scene's non-transition end (invalid overlap) — if OBJ-016 validates this.
18. `composition.audio.src` pointing to non-existent file — this is caught by OBJ-035's pre-flight, not schema validation. **Note: this tests the orchestrator's pre-flight check, not manifest validation.**
19. Image `src` pointing to non-existent file — same: OBJ-035 pre-flight.
20. Manifest is not valid JSON (syntax error).
21. Manifest is valid JSON but wrong type (array instead of object).
22. Manifest is valid JSON but a string `"hello"`.
23. Scene with `geometry: ""` (empty string) → validation error.
24. Scene with `camera: ""` (empty string) → validation error.
25. `composition.width: 1.5` (non-integer, if schema requires integer).

Each invalid manifest must produce a clear error message naming the problem. No invalid manifest may produce partial rendering output (C-10).

#### Fixture F-05: SC-05 n8n Test Payload

A JSON payload for the HTTP endpoint:

```json
{
  "topic": "Deep sea creatures",
  "duration": 30,
  "style": "cinematic documentary"
}
```

Note: SC-05 testing requires OBJ-075 (n8n HTTP interface) and OBJ-057 (full pipeline integration) to be complete. The test plan documents the procedure; OBJ-078 gates execution on those dependencies being ready.

## Design Decisions

### D1: Test Plan Document, Not Test Code

**Decision:** OBJ-077 produces a markdown test plan, not executable test files.

**Rationale:** The objective metadata explicitly states "documents test procedures only — OBJ-078 executes them." The plan is a specification that OBJ-078's implementer follows. This separation allows the plan to be reviewed and approved before any execution infrastructure exists.

### D2: Four Test Suites Mapping to Four Success Criteria

**Decision:** The test plan is organized into four suites: SC-01, SC-03, SC-05, SC-06. Each suite contains numbered test procedures.

**Rationale:** Direct mapping to seed Section 6 success criteria. Each procedure is independently executable and has unambiguous pass/fail conditions.

### D3: SC-05 Documented But Execution Gated

**Decision:** The SC-05 (n8n integration) test procedure is fully documented in the plan, but OBJ-077 acknowledges that execution requires OBJ-057 and OBJ-075. OBJ-078's dependency graph includes OBJ-057, ensuring it won't execute SC-05 tests prematurely.

**Rationale:** OBJ-077's own dependencies (OBJ-035, OBJ-046, OBJ-037, OBJ-038) do not include the n8n stack. The plan can be written now; execution is gated by OBJ-078's broader dependency set.

### D4: Fixture Manifests Use Only Verified Geometries and Cameras

**Decision:** All test fixtures reference only geometries and camera presets whose objectives have `status: "verified"` in the progress map. As of current state: stage (OBJ-018), tunnel (OBJ-019), canyon (OBJ-020), flyover (OBJ-021) for geometries; static (OBJ-026), slow_push_forward (OBJ-027), slow_pull_back (OBJ-028), lateral_track_left (OBJ-029), crane_up (OBJ-030), gentle_float (OBJ-031) for cameras.

**Rationale:** Using unverified presets would introduce confounds — a test failure might be caused by the fixture using a buggy preset rather than a pipeline defect. Verified presets have passed review and are known correct.

### D5: SC-06 Tests Both Directions of the Biconditional

**Decision:** SC-06 states "No manifest that passes validation produces a rendering error. No manifest that fails validation is a valid video description." The test plan verifies both directions:
- **Forward:** Every manifest in the valid corpus renders without error.
- **Backward:** Every manifest in the invalid corpus fails validation before rendering begins.

**Rationale:** SC-06 is a biconditional soundness claim. Testing only one direction leaves the other unverified.

### D6: Performance Benchmark Uses Wall-Clock Timing with Controlled Environment

**Decision:** SC-03 performance testing requires documenting the test machine's specifications (CPU model, core count, RAM, OS, disk type) alongside the timing results. The benchmark runs on software WebGL only for the baseline. GPU-accelerated runs are optional and documented separately.

**Rationale:** Performance results are meaningless without environment context. C-08 specifies "a standard 4-core VPS with at least 4GB RAM" — the benchmark machine must meet or exceed this spec, and the test report must confirm it does.

### D7: `ffprobe` as the Primary Output Validator

**Decision:** All video output validation uses `ffprobe` (from FFmpeg) to verify container format, codec, resolution, fps, duration, and stream count. This is the authoritative tool for media file validation.

**Rationale:** `ffprobe` is already available (FFmpeg is a project dependency per C-01). It provides machine-parseable JSON output (`-print_format json`) for automated verification.

### D8: SC-01 Includes Browser Playback Check

**Decision:** SC-01 requires the output MP4 to "play correctly in VLC and web browsers" per seed SC-01. The test procedure specifies verifying playback via both `ffprobe` metadata checks (automated) and a manual playback step (human operator confirms visual correctness). The automated portion checks: valid H.264 stream, correct resolution/fps/duration, `movflags +faststart` present, audio stream present when audio was provided.

**Rationale:** Automated checks can verify structural correctness. Visual correctness (no artifacts, correct scene ordering, transitions render properly) requires human eyes — consistent with the HITL pattern used throughout the project.

### D9: Invalid Manifest Tests Must Not Launch Browser or FFmpeg

**Decision:** For SC-06 backward tests (invalid corpus), the test procedure verifies not only that validation fails, but that no browser process is launched and no FFmpeg process is spawned. This is verified by timing (validation failures should complete in <100ms) and by checking for zombie processes.

**Rationale:** C-10: "Invalid manifests must never produce partial output — fail fast, fail clearly." OBJ-035's D7 guarantees no resource allocation before validation passes. The test plan should verify this guarantee.

### D10: Test Plan References Specific Orchestrator Error Codes

**Decision:** Each invalid manifest test specifies the expected `OrchestratorErrorCode` or manifest validation error code. This makes the test plan a regression reference — if error codes change, the plan needs updating.

**Rationale:** "Actionable error messages" (C-10) means the test plan must verify that specific, correct error codes are returned, not just "some error."

## Acceptance Criteria

### Test Plan Document Quality

- [ ] **AC-01:** The test plan document exists at `nodes/OBJ-077/test-plan.md` and is a self-contained markdown document.
- [ ] **AC-02:** The plan contains four clearly delineated test suites: SC-01, SC-03, SC-05, SC-06.
- [ ] **AC-03:** Each test procedure has: unique ID, title, preconditions, ordered steps, pass conditions, fail conditions.
- [ ] **AC-04:** Every step is unambiguous — an implementer can follow the procedure without asking clarifying questions.

### SC-01 Suite Coverage

- [ ] **AC-05:** The SC-01 suite includes a procedure for rendering a 60-second, 5-scene video with narration audio to MP4.
- [ ] **AC-06:** The procedure specifies that only geometry names, slot keys, and camera preset names are used (no manual coordinates).
- [ ] **AC-07:** The procedure specifies `ffprobe` validation: H.264 codec, correct resolution (1920×1080), correct fps (30), duration within ±0.5s of 60s, audio stream present.
- [ ] **AC-08:** The procedure specifies `movflags +faststart` verification.
- [ ] **AC-09:** The procedure includes a manual playback verification step (human confirms visual correctness in VLC or browser).
- [ ] **AC-10:** The procedure verifies that at least 3 distinct geometry types and 3 distinct camera presets are used across the 5 scenes.
- [ ] **AC-11:** The procedure verifies at least one `crossfade`, one `dip_to_black`, and one `cut` transition are present.

### SC-03 Suite Coverage

- [ ] **AC-12:** The SC-03 suite specifies the benchmark environment requirements (4-core CPU, 4GB+ RAM, software WebGL).
- [ ] **AC-13:** The procedure specifies the benchmark manifest: 60s, 30fps, 1920×1080, 5 textured planes per scene.
- [ ] **AC-14:** The pass condition for the baseline benchmark is: total render time < 15 minutes (900,000ms).
- [ ] **AC-15:** The procedure requires logging: total render time, average frame time, `OrchestratorResult.captureStats`, and machine specs.
- [ ] **AC-16:** The procedure includes an optional GPU-accelerated run with a separate (softer) performance target documented.

### SC-05 Suite Coverage

- [ ] **AC-17:** The SC-05 suite documents the n8n HTTP endpoint test procedure: POST topic+duration, receive job ID, poll for completion, download MP4.
- [ ] **AC-18:** The procedure specifies the expected HTTP status codes at each step (e.g., 202 for job creation, 200 for completed poll, 200 for download).
- [ ] **AC-19:** The procedure specifies that the downloaded MP4 passes the same `ffprobe` validation as SC-01.
- [ ] **AC-20:** The procedure documents that execution requires OBJ-057 and OBJ-075 to be complete.

### SC-06 Suite Coverage

- [ ] **AC-21:** The SC-06 suite includes a valid manifest corpus of at least 20 manifests covering the scenarios listed in F-03.
- [ ] **AC-22:** The SC-06 suite includes an invalid manifest corpus of at least 25 manifests covering the scenarios listed in F-04.
- [ ] **AC-23:** Each valid manifest procedure specifies: run through orchestrator, verify render completes without error, verify output via `ffprobe`.
- [ ] **AC-24:** Each invalid manifest procedure specifies: the expected error code, that no browser/FFmpeg process is launched, that no partial output file exists.
- [ ] **AC-25:** The plan explicitly tests both directions of SC-06's biconditional (valid manifests render; invalid manifests fail validation).

### Fixture Specifications

- [ ] **AC-26:** All fixture manifests reference only verified geometries and camera presets per the current progress map.
- [ ] **AC-27:** Fixture specifications include enough detail (geometry names, slot assignments, durations, transition types) for OBJ-078 to construct them without guessing.
- [ ] **AC-28:** The plan specifies how to generate test images (solid-color PNGs at appropriate dimensions) and test audio (silent WAV or tone at specified duration).

### Traceability

- [ ] **AC-29:** Each test procedure references the seed testable claims (TC-xx) and constraints (C-xx) it verifies.
- [ ] **AC-30:** The plan includes a traceability matrix mapping each SC to its test procedures and the seed TCs/constraints they cover.

## Edge Cases and Error Handling

Since OBJ-077 is a test plan (not code), edge cases refer to scenarios the plan must account for:

### Environment Variability
| Scenario | Plan Response |
|---|---|
| Benchmark machine has <4GB RAM | Precondition check: procedure fails if `free -m` reports <4GB available. Document as prerequisite. |
| No FFmpeg installed | Precondition: verify `ffmpeg -version` and `ffprobe -version` succeed before any test. |
| No Chromium available | Precondition: verify Puppeteer can launch headless Chromium (a quick smoke test). |
| GPU not available for accelerated benchmark | The GPU benchmark is marked optional. Software-only baseline is the required test. |

### Flaky Timing
| Scenario | Plan Response |
|---|---|
| SC-03 benchmark slightly exceeds 15 minutes due to system load | Procedure requires: no other CPU-intensive processes running; run benchmark 3 times; take the median. If median < 15 min, pass. |
| Duration mismatch due to floating-point rounding | `ffprobe` duration comparison uses ±0.5s tolerance for 60s videos (< 1% error). |

### Partial Infrastructure
| Scenario | Plan Response |
|---|---|
| SC-05 tests cannot run because OBJ-075 isn't complete | Plan documents this as a gated test. OBJ-078 skips SC-05 suite if dependencies aren't met and reports it as "blocked." |
| Some geometries/cameras are verified after plan is written | Plan references verified geometries/cameras by OBJ-ID. If new ones are verified before OBJ-078 executes, the executor may add them to the valid corpus but is not required to. |

### Manifest Corpus Gaps
| Scenario | Plan Response |
|---|---|
| A valid manifest scenario is missing from F-03 | The plan specifies 20 as a minimum. OBJ-078 may add more if edge cases are discovered during execution. |
| An invalid manifest doesn't fail validation (false negative) | This is a test failure for SC-06. The plan requires documenting which specific manifest passed when it shouldn't have, and filing it as a bug against the validation layer (OBJ-016 or OBJ-004). |
| A valid manifest fails to render (false positive) | This is a test failure for SC-06 (forward direction). Document the error, the manifest, and which component failed. |

## Test Strategy

This section is meta — it describes how to verify that the test plan itself is correct and complete.

### Plan Verification (Pre-Execution)

1. **Coverage check:** Every clause in SC-01, SC-03, SC-05, SC-06 (seed Section 6) is addressed by at least one test procedure.
2. **Fixture feasibility:** Each fixture manifest can be constructed using only verified geometries and cameras. Cross-reference against the progress map.
3. **Dependency check:** All tools referenced in procedures (`ffprobe`, `depthkit render`, `depthkit validate`, `curl`) are available in the expected environment.
4. **Traceability completeness:** Every test procedure maps to at least one TC or C. Every TC referenced in seed Section 5 that relates to SC-01/03/05/06 is covered by at least one procedure.

### Relevant Testable Claims

The test plan covers these seed TCs:

| TC | Covered By |
|---|---|
| TC-02 (Puppeteer + Three.js render performance) | SC-03 suite |
| TC-04 (Scene geometries eliminate manual 3D positioning) | SC-01 suite (blind-authored manifest) |
| TC-06 (Virtualized clock produces deterministic output) | SC-01 suite (render twice, compare) |
| TC-07 (Manifest validation catches common errors) | SC-06 invalid corpus |
| TC-10 (Cross-scene transitions mask compositing seams) | SC-01 suite (transitions in benchmark manifest) |
| TC-11 (Engine runs in Docker with software WebGL) | SC-03 suite (software WebGL benchmark) |
| TC-13 (Audio duration drives total video length) | SC-01 suite (audio-driven duration) |

### Relevant Constraints

| Constraint | Verified By |
|---|---|
| C-02 (Puppeteer + Three.js + FFmpeg pipeline) | SC-01 end-to-end render |
| C-03 (Deterministic virtualized timing) | SC-01 determinism check |
| C-04 (Resolution and frame rate) | SC-06 valid corpus (portrait + landscape, 24fps + 30fps) |
| C-05 (Deterministic output) | SC-01 determinism procedure |
| C-07 (Audio synchronization) | SC-01 audio-synced render |
| C-08 (Render performance) | SC-03 benchmark |
| C-10 (Manifest validation) | SC-06 full suite |
| C-11 (Software rendering baseline) | SC-03 software WebGL benchmark |

## Integration Points

### Depends On

| Dependency | What OBJ-077 Uses |
|---|---|
| **OBJ-035** (Orchestrator) | The plan references `Orchestrator.render()`, `OrchestratorResult`, `OrchestratorError`, `OrchestratorErrorCode`, and `RenderProgress` in its procedures. The plan's SC-01 and SC-03 procedures call the orchestrator (via CLI or programmatic API). |
| **OBJ-046** (CLI) | The plan's procedures use `depthkit render` and `depthkit validate` CLI commands. CLI output formats (from `src/cli/format.ts`) are referenced for expected output verification. |
| **OBJ-037** (Scene Sequencer) | The plan's transition tests (crossfade, dip_to_black) rely on OBJ-037's sequencer being integrated into the orchestrator. The plan does not reference OBJ-037 directly — it's consumed through OBJ-035. |
| **OBJ-038** (Audio Sync / Scene Timing) | The plan's SC-01 audio synchronization tests rely on OBJ-038's `resolveTimeline()` being integrated into the orchestrator. Referenced indirectly through OBJ-035. |

### Consumed By

| Consumer | How It Uses OBJ-077 |
|---|---|
| **OBJ-078** (E2E Test Execution) | Primary consumer. OBJ-078 implements and executes the procedures defined in this plan. It creates the fixture manifests, runs the tests, collects results, and reports pass/fail. |

### File Placement

```
nodes/
  OBJ-077/
    meta.json              # UPDATED — status, notes
    output.md              # NEW — specification (this document)
    test-plan.md           # NEW — the actual test plan deliverable
```

Wait — actually, re-reading the objective, the deliverable IS the specification itself. The test plan IS the output. Let me reconsider.

The objective says: "This is the test plan document; actual execution is OBJ-078." So the `output.md` IS the test plan specification. There's no separate `test-plan.md` — the specification for this objective IS the test plan.

Revised file placement:

```
nodes/
  OBJ-077/
    meta.json              # UPDATED — status, notes
    output.md              # NEW — the test plan specification
```

The `output.md` for OBJ-077 serves dual purpose: it is both the specification (as required by the harness) and the test plan (the objective's deliverable). The document structure follows the spec format but its content IS the test procedures.

## Open Questions

### OQ-A: Should the SC-01 Determinism Test Compare Byte-Identical Output?

C-05 says "byte-identical (or visually indistinguishable)." Byte-identical MP4s require deterministic FFmpeg encoding, which depends on exact FFmpeg version, build flags, and encoder state. The plan should specify: compare frame checksums extracted from the MP4 (via `ffmpeg -i output.mp4 -f framemd5 -`), not the MP4 file bytes themselves. If frame checksums differ, compare PSNR (peak signal-to-noise ratio) — PSNR > 60dB constitutes "visually indistinguishable."

**Proposed resolution:** Frame MD5 comparison as primary. PSNR > 60dB as fallback acceptance criterion.

### OQ-B: How Many Runs for SC-03 Benchmark Reliability?

A single run may be affected by system load, disk cache state, or thermal throttling. Three runs with median reporting is standard benchmarking practice.

**Proposed resolution:** 3 runs, median value is the reported result.

### OQ-C: Should SC-05 Procedures Include Timeout Specifications?

The n8n endpoint will run async rendering. The poll step needs a timeout. What's reasonable?

**Proposed resolution:** Poll for up to 20 minutes (conservative, >15 min render target) at 10-second intervals. Timeout is a fail condition.

### OQ-D: Should the Plan Include a Smoke Test That Runs Before the Full Suites?

A quick (<30 second) smoke test rendering a 2-second, 1-scene video at 320×240 would catch catastrophic pipeline failures before committing to the full 60-second benchmark.

**Proposed resolution:** Yes — include a "Suite 0: Smoke Test" that validates the pipeline is functional before running the full suites. Not mapped to any SC but prevents wasted time.

---

I believe this covers the objective thoroughly. I'd like the Challenger to review and provide feedback, particularly on:

1. Whether the fixture specifications (F-01 through F-05) are detailed enough for OBJ-078's implementer.
2. Whether the SC-05 scoping (documented but gated) is appropriate given OBJ-077's dependency graph.
3. Whether the 20-valid / 25-invalid manifest corpus sizes are sufficient for SC-06.
4. Whether the open questions should be resolved in the spec or left open for OBJ-078.

---

## Round 2 — spec_challenger

I've carefully reviewed the proposed specification. Here are my findings, organized by severity.

---

## Points of Agreement (What's Sound)

- **D1 (test plan, not test code)** — Correct interpretation of the objective metadata.
- **D3 (SC-05 gated)** — Appropriate scoping given OBJ-077's dependency graph.
- **D4 (verified-only fixtures)** — Smart constraint that isolates pipeline defects from preset defects.
- **D5 (biconditional SC-06)** — Correct reading of the success criterion.
- **D7 (`ffprobe` as validator)** — Correct tool choice.
- **F-04 (invalid corpus)** — Good enumeration of failure modes.
- **Traceability tables** — TC and constraint mapping is thorough.

---

## Critical Issues

### C1: The spec is a meta-spec, not the actual test plan

**Problem:** The objective deliverable IS the test plan. OBJ-078 must follow it. But the current proposal describes *what the plan should contain* (fixture contracts, quality AC) rather than containing the actual test procedures with concrete steps. For example, AC-05 says "The SC-01 suite includes a procedure for rendering a 60-second, 5-scene video" — but where is that procedure? There are no numbered steps like "Step 1: Run `depthkit validate ./fixtures/sc01-benchmark.json`; Step 2: Run `depthkit render ...`; Step 3: Run `ffprobe -v quiet -print_format json ...`."

An OBJ-078 implementer reading this spec would still need to invent all the actual test procedures. That's the one thing this objective is supposed to deliver.

**Severity:** Critical — the primary deliverable is missing.

**Fix:** The `output.md` must contain the actual test procedures inline, not just meta-criteria about what they should contain. Each procedure needs: ID, preconditions, concrete CLI commands or API calls, exact `ffprobe` command lines with the JSON fields to check, and literal pass/fail thresholds. The AC should verify the spec's content, but the content itself must be the procedures.

### C2: Open questions OQ-A through OQ-D must be resolved

**Problem:** All four open questions directly affect test procedure content:
- OQ-A (determinism comparison method) determines the SC-01 determinism procedure steps.
- OQ-B (benchmark run count) determines the SC-03 procedure.
- OQ-C (poll timeout) determines the SC-05 procedure.
- OQ-D (smoke test inclusion) determines whether a Suite 0 exists.

Leaving these open means OBJ-078 must make design decisions that belong in the plan.

**Severity:** Critical — without resolving these, OBJ-078 can't execute faithfully.

**Fix:** Resolve all four in the spec body:
- OQ-A → Frame MD5 primary, PSNR ≥ 60dB fallback. Specify the exact `ffmpeg` command: `ffmpeg -i output1.mp4 -f framemd5 - > run1.md5`.
- OQ-B → 3 runs, median, as proposed.
- OQ-C → 20-minute timeout, 10-second poll interval, as proposed.
- OQ-D → Include the smoke test. It's cheap insurance and should be a concrete procedure.

---

## Major Issues

### M1: No concrete `ffprobe` validation commands

**Problem:** The plan says "verify via `ffprobe`" at least 8 times but never specifies the exact command, output format, or JSON field paths. Different `ffprobe` invocations produce wildly different output. An implementer would need to research `ffprobe` usage independently.

**Severity:** Major — ambiguous verification steps make tests unreproducible.

**Fix:** Specify the canonical `ffprobe` invocation and the exact JSON assertions:

```bash
ffprobe -v quiet -print_format json -show_format -show_streams output.mp4
```

Then specify field checks:
- H.264: `streams[i].codec_type === "video" && streams[i].codec_name === "h264"`
- Resolution: `streams[i].width === 1920 && streams[i].height === 1080`
- FPS: `streams[i].r_frame_rate === "30/1"` (or parse as ratio)
- Duration: `|parseFloat(format.duration) - 60.0| < 0.5`
- Audio present: `streams.some(s => s.codec_type === "audio")`
- `movflags +faststart`: `format.tags?.compatible_brands` contains `"isom"` OR check atom order via `ffprobe -v trace` (specify which method)

### M2: Audio-proportional timing mode may not be exercisable

**Problem:** F-03 item 8 specifies a manifest testing `audio_proportional` timing. But OBJ-035's spec (D17) computes duration as `Math.max(...scenes.map(s => s.start_time + s.duration))` — it doesn't call OBJ-038's `resolveTimeline()`. OBJ-046's CLI has no `--timing-mode` flag. So how does the test exercise `audio_proportional` mode through the rendering pipeline?

If OBJ-035's implementation integrates OBJ-038 (which is likely since OBJ-038 is a dependency), the spec should document how. If it doesn't, F-03 item 8 is untestable.

**Severity:** Major — a fixture that can't be tested is noise.

**Fix:** Either:
(a) Remove F-03 item 8 and note it as untestable until OBJ-035 explicitly integrates OBJ-038's timing modes, OR
(b) Document that the test exercises `resolveTimeline()` directly (via programmatic API, not CLI) as a unit-level integration test, separate from the end-to-end pipeline test, OR
(c) Note that OBJ-035's implementation is expected to adopt OBJ-038 internally, and the test validates that audio-proportional behavior is observable (output duration matches audio duration when scene durations are clearly different weights).

Option (c) is most pragmatic: don't test the mode flag — test the observable behavior. If the manifest has scenes with durations [5, 10, 5] and an audio file of 45s, verify the output is 45s regardless of how the orchestrator achieves it.

### M3: F-04 items 18-19 conflate validation with pre-flight checks

**Problem:** Items 18-19 (non-existent audio/image files) are orchestrator pre-flight failures (OBJ-035 D15), not manifest validation failures. The spec correctly notes this but still includes them in the "Invalid Manifest Corpus" (F-04). This conflation means the pass criteria ("validation fails before rendering") is wrong for these items — they fail at pre-flight, after validation passes.

**Severity:** Major — wrong pass criteria lead to false test results.

**Fix:** Split F-04 into two sub-categories:
- **F-04a: Schema/semantic validation failures** (items 1-17, 20-25): Expected to throw `MANIFEST_INVALID` before any resource allocation. Verified by `depthkit validate`.
- **F-04b: Pre-flight failures** (items 18-19): Expected to pass validation but fail at orchestrator pre-flight (`SCENE_SETUP_FAILED`). Verified by `depthkit render`, not `depthkit validate`. No browser launched, but validation does pass.

### M4: Benchmark manifest F-02 is identical to F-01

**Problem:** D says F-02 is "Same as F-01 but with explicit constraints for benchmarking." But F-01 already specifies 1920×1080, 30fps, 5 scenes. The only real difference is "5 textured planes per scene" — but F-01's scenes using tunnel geometry already require 5 planes (floor, ceiling, left_wall, right_wall, end_wall). Are these the same fixture or not?

**Severity:** Major — ambiguity about whether OBJ-078 creates one fixture or two.

**Fix:** Either merge F-01 and F-02 into a single fixture used for both SC-01 and SC-03, or specify concrete differences (e.g., F-02 uses all-tunnel scenes to maximize consistent plane count, while F-01 uses mixed geometries for coverage). My recommendation: merge. One fixture serves both purposes — it tests correctness AND benchmarks performance.

### M5: SC-01 determinism procedure needs concrete steps

**Problem:** The spec mentions TC-06 and C-05 in the traceability table and in OQ-A, but there's no concrete test procedure for determinism. SC-01 in the seed says "the same manifest + the same input images + the same audio file must produce byte-identical (or visually indistinguishable) output." This needs a dedicated procedure with exact comparison methodology.

**Severity:** Major — a key success criterion has no procedure.

**Fix:** Add a dedicated SC-01 determinism procedure:
1. Render the benchmark manifest twice to separate output paths.
2. Extract frame MD5s from both: `ffmpeg -i output1.mp4 -f framemd5 - > run1.md5`
3. Compare the two MD5 files: `diff run1.md5 run2.md5`
4. If identical: pass.
5. If different: compute PSNR per differing frame. If all PSNR ≥ 60dB: pass. Otherwise: fail.

---

## Minor Issues

### m1: F-03 item 12 "Minimum duration scene (0.1s)" may produce zero frames

At 24fps, 0.1s = 2.4 frames → rounds to 2-3 frames. At 30fps, 0.1s = 3 frames. This is fine. But the plan should specify the minimum meaningful duration: `ceil(1/fps)` seconds (1 frame). 0.1s is fine as a test value but document why.

### m2: No specification for test image generation

AC-28 says "The plan specifies how to generate test images (solid-color PNGs at appropriate dimensions)" but the spec never says what dimensions. Tunnel floor planes need images matching the plane aspect ratio to avoid distortion (per seed 8.9). The plan should specify: generate 1920×1080 solid-color PNGs for backdrop/wall slots, and specify that the engine auto-adapts per seed 8.9.

**Fix:** Add a concrete fixture preparation step: "Generate solid-color PNG test images at 1920×1080 in distinct colors per slot (e.g., red floor, blue ceiling, green left wall) using ImageMagick: `convert -size 1920x1080 xc:red floor.png`." Distinct colors per slot make visual verification easier.

### m3: The "Test Strategy" section is recursive

The section describes "how to verify the test plan is correct" — this is meta and not actionable. It should be repurposed as a coverage summary or removed.

### m4: Missing SC-01 check for total frame count

The `ffprobe` checks cover codec, resolution, fps, duration, and audio stream. But they don't verify total frame count. For a 60s video at 30fps, there should be exactly 1800 frames. This is verifiable via `ffprobe -v quiet -count_frames -show_entries stream=nb_read_frames`.

---

## Summary of Required Changes

| ID | Severity | Issue | Required Fix |
|----|----------|-------|-------------|
| C1 | Critical | No actual test procedures, only meta-spec | Write concrete procedures with literal CLI commands and field checks |
| C2 | Critical | Open questions unresolved | Resolve OQ-A through OQ-D in the spec body |
| M1 | Major | No `ffprobe` command syntax | Specify exact commands and JSON field assertions |
| M2 | Major | Audio-proportional mode untestable via CLI | Clarify how it's exercised or reframe as observable behavior test |
| M3 | Major | Pre-flight failures mixed with validation failures | Split F-04 into validation vs. pre-flight categories |
| M4 | Major | F-01 and F-02 are redundant | Merge or specify concrete differences |
| M5 | Major | No determinism procedure | Add concrete frame-comparison steps |
| m1-m4 | Minor | Various | As described above |

Please revise the spec to address all critical and major issues. I'll verify the fixes structurally in the next round.

---

## Round 3 — spec_author

# Revised Specification: OBJ-077 — End-to-End Integration Test Plan

## Summary

OBJ-077 delivers the **end-to-end integration test plan** for depthkit — the concrete, step-by-step procedures for verifying SC-01 (60-second, 5-scene video renders to valid MP4), SC-03 (performance target met), SC-05 (n8n POST/poll/download works), and SC-06 (manifest validation soundness). This document IS the test plan: it contains executable procedures with literal CLI commands, exact `ffprobe` invocations, and unambiguous pass/fail thresholds. OBJ-078 executes these procedures.

## Interface Contract

OBJ-077 produces no code module. Its deliverable is the test plan document itself (`output.md`). The plan specifies test fixtures, procedures, and validation commands.

---

## Resolved Open Questions

These are resolved here and incorporated into the procedures below.

**OQ-A (Determinism Comparison Method):** Frame MD5 comparison as primary method. Extract per-frame checksums via `ffmpeg -i output.mp4 -f framemd5 -`. If frame MD5s differ, compute per-frame PSNR via `ffmpeg -i output1.mp4 -i output2.mp4 -lavfi psnr -f null -`. PSNR ≥ 60dB on all frames constitutes "visually indistinguishable." Below 60dB on any frame is a fail.

**OQ-B (Benchmark Run Count):** 3 runs, report median. No other CPU-intensive processes running during benchmark. Document all three values.

**OQ-C (SC-05 Poll Timeout):** 20-minute timeout, 10-second poll interval. Timeout is a fail condition.

**OQ-D (Smoke Test):** Include as Suite 0. A quick (<30 second) 2-second, 1-scene render at 320×240 validates the pipeline is functional before committing to full suites.

---

## Test Fixtures

### Fixture F-01: Benchmark Manifest

A single manifest used for both SC-01 (correctness) and SC-03 (performance). This manifest exercises the full pipeline:

**Composition:**
```json
{
  "version": "3.0",
  "composition": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "audio": {
      "src": "./audio/test-60s.wav",
      "volume": 1.0
    }
  }
}
```

**Scene Layout (5 scenes, 60s total, explicit timing):**

| Scene | Geometry | Camera | Duration | start_time | transition_in | transition_out | Planes (slots) |
|-------|----------|--------|----------|------------|---------------|----------------|----------------|
| scene_001 | `tunnel` (OBJ-019) | `slow_push_forward` (OBJ-027) | 13.0s | 0.0 | `{ type: "dip_to_black", duration: 1.0 }` | `{ type: "crossfade", duration: 1.0 }` | floor, ceiling, left_wall, right_wall, end_wall (5 planes) |
| scene_002 | `stage` (OBJ-018) | `gentle_float` (OBJ-031) | 13.0s | 12.0 | `{ type: "crossfade", duration: 1.0 }` | `{ type: "cut" }` | backdrop, floor, subject (3 planes, only required) |
| scene_003 | `canyon` (OBJ-020) | `lateral_track_left` (OBJ-029) | 12.0s | 25.0 | `{ type: "cut" }` | `{ type: "dip_to_black", duration: 0.5 }` | floor, left_wall, right_wall, end_wall, sky (5 planes) |
| scene_004 | `flyover` (OBJ-021) | `crane_up` (OBJ-030) | 12.0s | 36.5 | `{ type: "dip_to_black", duration: 0.5 }` | `{ type: "crossfade", duration: 1.0 }` | ground, sky, landmark_1 (3+ planes per flyover geometry) |
| scene_005 | `stage` (OBJ-018) | `static` (OBJ-026) | 12.5s | 47.5 | `{ type: "crossfade", duration: 1.0 }` | `{ type: "dip_to_black", duration: 1.0 }` | backdrop, floor, subject (3 planes) |

**Coverage achieved:**
- 4 distinct geometry types: tunnel, stage, canyon, flyover (≥3 required).
- 5 distinct camera presets: slow_push_forward, gentle_float, lateral_track_left, crane_up, static (≥3 required).
- Transitions: 2 crossfade, 3 dip_to_black, 1 cut (all three types present).
- No manual coordinates: only geometry names, slot keys, camera preset names.
- 5 textured planes in scenes 1 and 3 (maximum typical load per C-08).

**Note on slot names:** The exact slot names depend on the verified geometry definitions (OBJ-018 through OBJ-021). OBJ-078 must consult each geometry's `PlaneSlot` definitions and adjust the manifest accordingly. The table above uses expected slot names; if a geometry defines different names, substitute them.

### Fixture F-01-AUDIO: Test Audio File

A 60-second WAV file. Generate via:
```bash
ffmpeg -f lavfi -i "sine=frequency=440:duration=60" -ar 44100 -ac 1 ./audio/test-60s.wav
```
A 440Hz tone. Content is irrelevant; duration is critical. Must be exactly 60.0s (±0.01s).

### Fixture F-01-IMAGES: Test Images

Generate solid-color 1920×1080 PNGs in distinct colors per slot for visual identification. Use ImageMagick:

```bash
mkdir -p images
convert -size 1920x1080 xc:'#8B0000' images/s1_floor.png      # dark red
convert -size 1920x1080 xc:'#00008B' images/s1_ceiling.png     # dark blue
convert -size 1920x1080 xc:'#006400' images/s1_left_wall.png   # dark green
convert -size 1920x1080 xc:'#4B0082' images/s1_right_wall.png  # indigo
convert -size 1920x1080 xc:'#FF8C00' images/s1_end_wall.png    # dark orange
# ... repeat for each scene with different color palettes
```

Use distinct color families per scene (scene 1: warm, scene 2: cool, etc.) so human visual inspection can confirm correct scene ordering.

The engine auto-adapts plane sizing from texture aspect ratio per seed Section 8.9, so 1920×1080 images are acceptable for all slot types.

### Fixture F-02: Smoke Test Manifest

A minimal manifest for the Suite 0 smoke test:

```json
{
  "version": "3.0",
  "composition": { "width": 320, "height": 240, "fps": 10 },
  "scenes": [{
    "id": "smoke_001",
    "duration": 2.0,
    "start_time": 0.0,
    "geometry": "stage",
    "camera": "static",
    "planes": {
      "backdrop": { "src": "./images/smoke_bg.png" },
      "subject": { "src": "./images/smoke_subject.png" }
    }
  }]
}
```

Generate 320×240 test images:
```bash
convert -size 320x240 xc:blue images/smoke_bg.png
convert -size 320x240 xc:red images/smoke_subject.png
```

Only required slots for `stage` geometry. No audio. Expected: 20 frames, ~2s video.

### Fixture F-03: SC-06 Valid Manifest Corpus

20 manifests exercising valid variations. Each is a separate JSON file. All use small resolutions (320×240) and short durations (1–3s at 10fps) for fast rendering.

| ID | Description | Key Properties |
|----|-------------|----------------|
| V-01 | Single scene, single required slot, no transitions, no audio | stage, static, 1.0s |
| V-02 | Single scene, all slots filled for tunnel geometry | tunnel, slow_push_forward, 2.0s, 5 planes |
| V-03 | 3 scenes with cut transitions only | stage×3, 1.0s each |
| V-04 | 2 scenes with crossfade transition (1.0s overlap) | stage, tunnel, 2.0s each |
| V-05 | 2 scenes with dip_to_black transitions | canyon, flyover, 2.0s each |
| V-06 | Mixed transitions: cut, crossfade, dip_to_black across 3 scenes | stage, tunnel, canyon |
| V-07 | Audio with explicit scene durations matching audio length | 3.0s audio, 3 scenes × 1.0s |
| V-08 | Audio present, scene durations sum to different value (warning expected) | 3.0s audio, scenes sum to 4.0s → `AUDIO_DURATION_MISMATCH` warning |
| V-09 | Portrait mode 240×320 (swapped) | stage, 1.0s |
| V-10 | 24fps variant | stage, 1.0s, 24fps |
| V-11 | 30fps variant | tunnel, 2.0s, 30fps |
| V-12 | Short scene 0.1s (3 frames at 30fps) | stage, static, 0.1s |
| V-13 | Scene with `camera_params.speed` override | tunnel, slow_push_forward, speed: 0.5 |
| V-14 | Scene with `camera_params.easing` override | stage, gentle_float, easing: "ease_out_cubic" |
| V-15 | Scene with optional slots omitted | stage with only required slots |
| V-16 | Scene with `scale: 1.5` on a PlaneRef | stage, subject plane scaled |
| V-17 | Scenes not in start_time order (warning expected) | 2 scenes, scene[0].start_time > scene[1].start_time |
| V-18 | Tunnel geometry (OBJ-019) | Full 5-slot tunnel |
| V-19 | Canyon geometry (OBJ-020) with crane_up camera (OBJ-030) | Tests geometry/camera compatibility |
| V-20 | 10 scenes, each 0.3s, cuts only | Stress test for scene count |

**For each valid manifest:** Generate matching solid-color test images at the manifest's resolution. Where audio is needed, generate a sine tone of the required duration.

### Fixture F-04a: SC-06 Invalid Manifest Corpus — Validation Failures

These fail at manifest validation (before any rendering). Testable via `depthkit validate`.

| ID | Description | Expected Error Code |
|----|-------------|-------------------|
| E-01 | Missing `version` field | Zod structural error |
| E-02 | `version: "1.0"` (wrong version) | Zod structural error |
| E-03 | Missing `composition` field | Zod structural error |
| E-04 | `composition.width: 0` | Zod structural error (non-positive) |
| E-05 | `composition.fps: 0` | Zod structural error |
| E-06 | Empty `scenes` array | Zod structural error (min 1) |
| E-07 | Scene missing `geometry` field | Zod structural error |
| E-08 | Scene missing `duration` | Zod structural error |
| E-09 | Scene with `duration: -1` | Zod structural error |
| E-10 | Unknown geometry name `"tunl"` | `UNKNOWN_GEOMETRY` |
| E-11 | Unknown camera name `"push_fast"` | `UNKNOWN_CAMERA` |
| E-12 | Camera incompatible with geometry | `INCOMPATIBLE_CAMERA` |
| E-13 | Missing required slot for geometry | `MISSING_REQUIRED_SLOT` |
| E-14 | Extra slot not defined by geometry | `UNKNOWN_SLOT` |
| E-15 | Crossfade transition_in on first scene (no predecessor) | `CROSSFADE_NO_ADJACENT` |
| E-16 | Duplicate scene IDs | Validation error |
| E-17 | Not valid JSON (syntax error in file) | `INVALID_JSON` |
| E-18 | Valid JSON but array instead of object | Zod structural error |
| E-19 | Valid JSON but a string `"hello"` | Zod structural error |
| E-20 | `geometry: ""` (empty string) | Validation error |
| E-21 | `camera: ""` (empty string) | Validation error |
| E-22 | `composition.width: 1.5` (non-integer if schema requires int) | Zod structural error |

### Fixture F-04b: SC-06 Pre-Flight Failures

These pass manifest validation but fail at orchestrator pre-flight. Must be tested via `depthkit render`, not `depthkit validate`.

| ID | Description | Expected Error Code |
|----|-------------|-------------------|
| P-01 | Image `src` pointing to non-existent file | `SCENE_SETUP_FAILED` |
| P-02 | Multiple missing images across scenes | `SCENE_SETUP_FAILED` (lists all missing) |
| P-03 | Audio `src` pointing to non-existent file | `AUDIO_MUX_FAILED` (or caught at pre-flight if OBJ-035 checks audio) |

### Fixture F-05: SC-05 n8n Test Payload

```json
{
  "topic": "Deep sea creatures",
  "duration": 30,
  "style": "cinematic documentary"
}
```

Execution gated on OBJ-057 and OBJ-075.

---

## Test Procedures

### Suite 0: Smoke Test

**Purpose:** Validate the pipeline is functional before committing to full suites. Not mapped to any SC.

#### SMOKE-01: Minimal Pipeline Smoke Test

**Preconditions:**
- `depthkit` CLI is installed and on PATH (or invokable via `npx`).
- `ffmpeg` and `ffprobe` are available: `ffmpeg -version` and `ffprobe -version` succeed.
- Puppeteer can launch headless Chromium: `node -e "const p = require('puppeteer'); p.launch({headless:true}).then(b => { console.log('OK'); b.close(); })"` succeeds.
- Smoke test fixtures (F-02) are generated.

**Steps:**
1. Generate test images:
   ```bash
   convert -size 320x240 xc:blue fixtures/smoke/images/smoke_bg.png
   convert -size 320x240 xc:red fixtures/smoke/images/smoke_subject.png
   ```
2. Validate the manifest:
   ```bash
   depthkit validate fixtures/smoke/manifest.json
   ```
   Expected: exit code 0, stdout contains "valid".
3. Render the manifest:
   ```bash
   depthkit render fixtures/smoke/manifest.json -o fixtures/smoke/output.mp4 --gpu software
   ```
   Expected: exit code 0, stdout contains "Rendered".
4. Validate output with `ffprobe`:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/smoke/output.mp4
   ```
5. Assert on `ffprobe` JSON output:
   - `streams[0].codec_type === "video"`
   - `streams[0].codec_name === "h264"`
   - `streams[0].width === 320`
   - `streams[0].height === 240`
   - `parseFloat(format.duration)` is within `[1.5, 2.5]` (2.0s ± 0.5s)
   - No audio stream (no audio in manifest).

**Pass:** All assertions hold. Output MP4 exists and is >0 bytes.

**Fail:** Any assertion fails, CLI exits non-zero, or output is 0 bytes.

**Time budget:** <30 seconds.

---

### Suite 1: SC-01 — End-to-End Rendering

#### SC01-01: 60-Second 5-Scene Video Renders to Valid MP4

**Preconditions:**
- SMOKE-01 passed.
- Benchmark fixtures (F-01, F-01-AUDIO, F-01-IMAGES) are generated.

**Steps:**
1. Generate the 60s audio file:
   ```bash
   ffmpeg -f lavfi -i "sine=frequency=440:duration=60" -ar 44100 -ac 1 fixtures/benchmark/audio/test-60s.wav
   ```
2. Generate all scene images (distinct colors per scene — see F-01-IMAGES).
3. Validate the benchmark manifest:
   ```bash
   depthkit validate fixtures/benchmark/manifest.json
   ```
   Expected: exit code 0.
4. Render:
   ```bash
   depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/output.mp4 \
     --gpu software \
     --verbose
   ```
   Expected: exit code 0. Note the render summary for SC-03.
5. Validate output with `ffprobe`:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/benchmark/output.mp4
   ```
6. Assert on `ffprobe` JSON — video stream:
   - `streams` contains an entry with `codec_type === "video"`
   - Video stream: `codec_name === "h264"`
   - Video stream: `width === 1920`
   - Video stream: `height === 1080`
   - Video stream: parse `r_frame_rate` as fraction → equals 30 (e.g., `"30/1"` or `"30000/1001"` — accept either, but numerator/denominator must evaluate to ~30.0 ± 0.1)
7. Assert on `ffprobe` JSON — duration:
   - `|parseFloat(format.duration) - 60.0| < 0.5`
8. Assert on `ffprobe` JSON — audio stream:
   - `streams` contains an entry with `codec_type === "audio"`
9. Assert on `ffprobe` JSON — faststart:
   - Run: `ffprobe -v trace fixtures/benchmark/output.mp4 2>&1 | head -50`
   - Verify `moov` atom appears before `mdat` atom in the trace output (this indicates `movflags +faststart`).
10. Count frames:
    ```bash
    ffprobe -v quiet -count_frames -select_streams v:0 \
      -show_entries stream=nb_read_frames \
      -print_format csv=p=0 fixtures/benchmark/output.mp4
    ```
    Expected: value is within `[1790, 1810]` (1800 ± 10 frames, accounting for rounding).

**Pass:** All assertions in steps 6–10 hold. CLI exited with code 0.

**Fail:** Any assertion fails or CLI exited non-zero.

**Constraint refs:** C-02, C-04, C-07, C-11.
**TC refs:** TC-04, TC-10, TC-13.

#### SC01-02: Manual Playback Verification

**Preconditions:** SC01-01 passed. Output MP4 exists.

**Steps:**
1. Open `fixtures/benchmark/output.mp4` in VLC (or any media player).
2. Verify:
   - Video plays from beginning to end without errors or corruption.
   - 5 distinct scenes are visible (identifiable by color palette).
   - Scene transitions are visible: at least one smooth crossfade blend, at least one fade-through-black, at least one instant cut.
   - Camera motion is visible in at least 3 scenes (not all static).
   - Audio tone plays throughout.
3. Open the same file in a web browser (drag into Chrome/Firefox tab or use `<video>` element).
4. Verify playback starts without download prompt (faststart working).

**Pass:** Human operator confirms all items in step 2 and step 4.

**Fail:** Any visual artifact, corrupt frame, missing scene, or playback failure.

**Note:** This is a human verification step. Record pass/fail and any observations.

#### SC01-03: Deterministic Output (C-05, TC-06)

**Preconditions:** SC01-01 passed.

**Steps:**
1. Render the benchmark manifest a second time to a different output path:
   ```bash
   depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/output_run2.mp4 \
     --gpu software
   ```
2. Extract frame MD5 checksums from both renders:
   ```bash
   ffmpeg -i fixtures/benchmark/output.mp4 -f framemd5 - > fixtures/benchmark/run1.md5
   ffmpeg -i fixtures/benchmark/output_run2.mp4 -f framemd5 - > fixtures/benchmark/run2.md5
   ```
3. Compare:
   ```bash
   diff fixtures/benchmark/run1.md5 fixtures/benchmark/run2.md5
   ```
4. If `diff` reports no differences: **pass** (byte-identical frames).
5. If `diff` reports differences: compute PSNR:
   ```bash
   ffmpeg -i fixtures/benchmark/output.mp4 \
     -i fixtures/benchmark/output_run2.mp4 \
     -lavfi psnr=stats_file=fixtures/benchmark/psnr.log \
     -f null -
   ```
6. Inspect `psnr.log`. If all frames have `psnr_avg >= 60.0`: **pass** (visually indistinguishable).
7. If any frame has `psnr_avg < 60.0`: **fail** (non-deterministic rendering).

**Pass:** Step 4 (identical) or step 6 (PSNR ≥ 60dB on all frames).

**Fail:** Step 7.

**Constraint refs:** C-03, C-05.
**TC refs:** TC-06.

#### SC01-04: Audio Duration Drives Video Length (TC-13)

**Preconditions:** SMOKE-01 passed.

**Steps:**
1. Generate a 45-second audio file:
   ```bash
   ffmpeg -f lavfi -i "sine=frequency=440:duration=45" -ar 44100 -ac 1 fixtures/sc01-04/audio.wav
   ```
2. Create a manifest with 5 scenes, each with `duration: 1.0` (as proportional weights), all `start_time: 0` (to be overridden by audio-proportional mode if OBJ-035 integrates OBJ-038), OR with explicit durations summing to 45s (9.0s each). Use 320×240 at 10fps for speed.
3. Render:
   ```bash
   depthkit render fixtures/sc01-04/manifest.json \
     -o fixtures/sc01-04/output.mp4 --gpu software
   ```
4. Verify output duration:
   ```bash
   ffprobe -v quiet -print_format json -show_format fixtures/sc01-04/output.mp4
   ```
5. Assert `|parseFloat(format.duration) - 45.0| < 0.5`.

**Pass:** Output duration matches audio duration within tolerance.

**Fail:** Duration mismatch >0.5s, or render error.

**Note:** If the orchestrator does not support `audio_proportional` mode via a flag, construct the manifest with explicit durations summing to 45.0s. The key test is that audio is present in the output and video duration matches audio duration.

**TC refs:** TC-13.
**Constraint refs:** C-07.

---

### Suite 2: SC-03 — Performance Target

#### SC03-01: Benchmark Environment Verification

**Preconditions:** None.

**Steps:**
1. Document machine specs:
   ```bash
   echo "=== CPU ===" && nproc && cat /proc/cpuinfo | grep "model name" | head -1
   echo "=== RAM ===" && free -m | grep Mem
   echo "=== OS ===" && uname -a
   echo "=== FFmpeg ===" && ffmpeg -version | head -1
   echo "=== Node ===" && node --version
   ```
2. Assert:
   - CPU cores ≥ 4 (`nproc` ≥ 4).
   - Available RAM ≥ 4096 MB.
3. Record all values in the test report.

**Pass:** Machine meets minimum spec.

**Fail:** Machine below spec — benchmark results are informational only, not pass/fail.

#### SC03-02: Software WebGL Baseline Benchmark

**Preconditions:** SC03-01 passed. SC01-01 fixtures generated.

**Steps:**
1. Ensure no other CPU-intensive processes are running: `top -b -n1 | head -20` (document load average).
2. Run benchmark — iteration 1:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_run1.mp4 \
     --gpu software --verbose
   ```
   Record: total wall-clock time (from `time`), render duration from CLI verbose output, average frame time.
3. Run benchmark — iteration 2:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_run2.mp4 \
     --gpu software --verbose
   ```
4. Run benchmark — iteration 3:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_run3.mp4 \
     --gpu software --verbose
   ```
5. Compute median of the 3 total wall-clock times.
6. Assert: median < 900,000ms (15 minutes).
7. Record all three times plus median in the test report. Also record average frame time from verbose output.

**Pass:** Median of 3 runs < 15 minutes.

**Fail:** Median ≥ 15 minutes. Document all values — this informs whether the target needs revision or the pipeline needs optimization.

**Constraint refs:** C-08, C-11.
**TC refs:** TC-02, TC-11.

#### SC03-03: GPU-Accelerated Benchmark (Optional)

**Preconditions:** SC03-02 completed. GPU available on test machine.

**Steps:**
1. Run:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_gpu.mp4 \
     --gpu hardware --verbose
   ```
2. Record wall-clock time and average frame time.
3. Compare to SC03-02 median. Document the speedup ratio.

**Pass/Fail:** Informational only. No hard target for GPU. Document results.

**Note:** Per C-08, GPU acceleration should render in under 3 minutes, but this is aspirational, not a gate.

---

### Suite 3: SC-05 — n8n Integration

**Execution gate:** OBJ-057 (full pipeline integration) and OBJ-075 (n8n HTTP interface) must both be `status: "verified"`. If either is not verified, this entire suite is **blocked** — skip and report as "blocked on OBJ-057/OBJ-075."

#### SC05-01: POST Topic and Receive Job ID

**Preconditions:** n8n workflow is running. HTTP endpoint URL is known (e.g., `http://localhost:5678/webhook/depthkit`).

**Steps:**
1. POST the test payload:
   ```bash
   curl -s -w "\n%{http_code}" -X POST \
     -H "Content-Type: application/json" \
     -d '{"topic":"Deep sea creatures","duration":30,"style":"cinematic documentary"}' \
     http://localhost:5678/webhook/depthkit
   ```
2. Assert HTTP status code is `200` or `202` (accepted).
3. Parse response body. Assert it contains a `job_id` field (string, non-empty).
4. Record `job_id` for subsequent steps.

**Pass:** Status 200/202, `job_id` present.

**Fail:** Non-2xx status, missing `job_id`, or connection refused.

#### SC05-02: Poll for Completion

**Preconditions:** SC05-01 passed. `job_id` obtained.

**Steps:**
1. Poll every 10 seconds for up to 20 minutes (120 polls max):
   ```bash
   JOB_ID="<from SC05-01>"
   for i in $(seq 1 120); do
     RESPONSE=$(curl -s http://localhost:5678/webhook/depthkit/status/$JOB_ID)
     STATUS=$(echo $RESPONSE | jq -r '.status')
     echo "Poll $i: status=$STATUS"
     if [ "$STATUS" = "completed" ]; then
       echo "Job completed."
       break
     elif [ "$STATUS" = "failed" ]; then
       echo "Job failed."
       exit 1
     fi
     sleep 10
   done
   ```
2. Assert: loop exited with `status === "completed"` within 120 polls.
3. Parse response: assert it contains a `download_url` field.

**Pass:** Status reached `"completed"` within 20 minutes. `download_url` present.

**Fail:** Timeout (120 polls without completion), `"failed"` status, or missing `download_url`.

#### SC05-03: Download and Validate MP4

**Preconditions:** SC05-02 passed. `download_url` obtained.

**Steps:**
1. Download:
   ```bash
   curl -s -o fixtures/sc05/output.mp4 "$DOWNLOAD_URL"
   ```
2. Assert file exists and is >0 bytes.
3. Validate with `ffprobe`:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/sc05/output.mp4
   ```
4. Assert:
   - Video stream: `codec_name === "h264"`, resolution is valid (any supported resolution).
   - `parseFloat(format.duration)` is within `[25.0, 35.0]` (~30s ± 5s tolerance for pipeline variability).
   - Audio stream is present.

**Pass:** All assertions hold.

**Fail:** Any assertion fails.

**Constraint refs:** SC-05.

---

### Suite 4: SC-06 — Manifest Validation Soundness

SC-06 is a biconditional: "No manifest that passes validation produces a rendering error. No manifest that fails validation is a valid video description."

#### SC06-FORWARD: Valid Manifests Render Without Error

**Preconditions:** SMOKE-01 passed. Valid corpus (F-03) manifests and matching images generated.

**Procedure (repeated for each manifest V-01 through V-20):**

1. Validate:
   ```bash
   depthkit validate fixtures/valid/V-XX.json
   ```
   - Expected: exit code 0.
   - For V-08 and V-17: exit code 0 WITH warnings in stdout. Record warnings.

2. Render:
   ```bash
   depthkit render fixtures/valid/V-XX.json \
     -o fixtures/valid/output/V-XX.mp4 \
     --gpu software
   ```
   - Expected: exit code 0.

3. Validate output:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/valid/output/V-XX.mp4
   ```
   Assert:
   - Video stream: `codec_name === "h264"`.
   - Resolution matches manifest's `composition.width` and `composition.height`.
   - FPS: `r_frame_rate` evaluates to manifest's `composition.fps` (± 0.1).
   - Duration: `|parseFloat(format.duration) - expectedDuration| < 0.5` where `expectedDuration` = sum of scene durations minus transition overlaps.
   - If manifest has audio: audio stream present.

**Pass for the suite:** All 20 valid manifests render without error and pass `ffprobe` validation.

**Fail:** Any valid manifest fails validation, fails rendering, or produces an invalid MP4.

**Constraint refs:** C-04, C-10.
**TC refs:** TC-07.

#### SC06-BACKWARD-A: Invalid Manifests Fail Validation

**Preconditions:** Invalid corpus F-04a (E-01 through E-22) created.

**Procedure (repeated for each manifest E-01 through E-22):**

1. Run validation:
   ```bash
   depthkit validate fixtures/invalid/E-XX.json
   ```
2. Assert:
   - Exit code is 1.
   - Stderr contains an error message.
   - Error message contains the expected error code or a recognizable description matching the F-04a table.
3. Verify no rendering occurred:
   - Time the command: `time depthkit validate ...`. Assert completes in < 1 second (validation is synchronous, no browser or FFmpeg).
   - Verify no output file was created.

**Pass for the suite:** All 22 invalid manifests fail validation with appropriate error messages.

**Fail:** Any invalid manifest passes validation (exit code 0), or error message is unhelpful/incorrect.

#### SC06-BACKWARD-B: Pre-Flight Failures Prevent Rendering

**Preconditions:** Pre-flight failure corpus F-04b (P-01 through P-03) created.

**Procedure (repeated for each manifest P-01 through P-03):**

1. Verify the manifest passes validation:
   ```bash
   depthkit validate fixtures/preflight/P-XX.json
   ```
   Expected: exit code 0 (manifest structure is valid).

2. Attempt to render:
   ```bash
   depthkit render fixtures/preflight/P-XX.json \
     -o fixtures/preflight/output/P-XX.mp4 \
     --gpu software 2>fixtures/preflight/P-XX.stderr
   ```
3. Assert:
   - Exit code is 1.
   - Stderr contains the expected error code (`SCENE_SETUP_FAILED` for P-01/P-02).
   - For P-02: error message lists **all** missing file paths, not just the first.
   - No output MP4 file exists at the output path.
4. Verify no browser was launched for an extended period:
   - Time the render command. Assert it completes in < 5 seconds (pre-flight check happens before browser launch per OBJ-035 D15).

**Pass:** All pre-flight failure manifests fail before rendering with appropriate errors. No partial output.

**Fail:** Render proceeds despite missing files, or error message is incomplete.

**Constraint refs:** C-10.
**TC refs:** TC-07.

---

## Design Decisions

### D1: Test Plan Document, Not Test Code

**Decision:** OBJ-077's `output.md` IS the test plan — concrete procedures with literal commands.

**Rationale:** Objective metadata: "documents test procedures only — OBJ-078 executes them." OBJ-078 can follow these procedures directly or convert them into automated test scripts.

### D2: Merged Benchmark Fixture (F-01)

**Decision:** A single fixture serves both SC-01 (correctness) and SC-03 (performance).

**Rationale:** The SC-01 benchmark manifest already specifies 1920×1080, 30fps, 5 scenes with 5 planes in tunnel/canyon scenes. This matches C-08's performance target conditions exactly. Separate fixtures would be redundant.

### D3: SC-05 Gated on Dependencies

**Decision:** Suite 3 (SC-05) is fully documented but execution is gated on OBJ-057 and OBJ-075 being verified.

**Rationale:** OBJ-077's own dependencies don't include the n8n stack. The plan is written now; OBJ-078 skips the suite if dependencies aren't met.

### D4: Verified-Only Fixtures

**Decision:** All fixtures use only geometries (OBJ-018 stage, OBJ-019 tunnel, OBJ-020 canyon, OBJ-021 flyover) and cameras (OBJ-026 static, OBJ-027 slow_push_forward, OBJ-028 slow_pull_back, OBJ-029 lateral_track_left, OBJ-030 crane_up, OBJ-031 gentle_float) with `status: "verified"`.

**Rationale:** Isolates pipeline defects from preset bugs.

### D5: Split Invalid Corpus (F-04a / F-04b)

**Decision:** Schema/semantic validation failures (F-04a) are tested via `depthkit validate`. Pre-flight failures (F-04b) are tested via `depthkit render`. Different tools, different expected behaviors.

**Rationale:** Validation failures never launch a browser (OBJ-035 D7). Pre-flight failures pass validation but fail before rendering. Conflating them produces wrong pass criteria.

### D6: Frame MD5 for Determinism, PSNR as Fallback

**Decision:** SC01-03 compares frame MD5 checksums. If different, PSNR ≥ 60dB on all frames is the fallback acceptance threshold.

**Rationale:** C-05 says "byte-identical (or visually indistinguishable)." Frame MD5 tests the former; PSNR tests the latter. 60dB PSNR means the maximum pixel difference is imperceptible.

### D7: Three Benchmark Runs With Median

**Decision:** SC03-02 runs the benchmark 3 times, reports the median.

**Rationale:** Single runs are affected by system load, cache state, thermal throttling. Median of 3 is standard benchmarking practice and smooths outliers.

### D8: `ffprobe` JSON as Canonical Validation

**Decision:** All output validation uses `ffprobe -v quiet -print_format json -show_format -show_streams`. This is the canonical invocation for all procedures.

**Rationale:** JSON output is machine-parseable and field paths are unambiguous. OBJ-078 can implement automated assertions against JSON fields.

### D9: Small Fixtures for SC-06 Corpus

**Decision:** SC-06 valid corpus manifests use 320×240 at 10fps with 1–3s durations.

**Rationale:** The valid corpus has 20 manifests, each of which must actually render. At 1920×1080/30fps, that would take hours. Small resolutions and short durations keep the total suite time under 20 minutes while still exercising the full pipeline.

### D10: Audio-Proportional Testing via Observable Behavior

**Decision:** SC01-04 tests audio synchronization by verifying the output video duration matches the audio duration, regardless of whether the orchestrator implements `audio_proportional` mode explicitly or the manifest author pre-computes durations.

**Rationale:** OBJ-035's current spec computes duration from scene `start_time + duration`. OBJ-038 provides `resolveTimeline()` with audio-proportional mode, but whether OBJ-035 integrates it is an implementation detail. The test validates the observable behavior (C-07: audio synchronization) — not the internal mechanism.

## Acceptance Criteria

### Test Plan Completeness

- [ ] **AC-01:** The plan contains five suites: Suite 0 (Smoke), Suite 1 (SC-01), Suite 2 (SC-03), Suite 3 (SC-05), Suite 4 (SC-06).
- [ ] **AC-02:** Each procedure has: unique ID, preconditions, literal CLI commands, exact assertion conditions, pass/fail thresholds.
- [ ] **AC-03:** Every clause in SC-01 is addressed: 60s 5-scene rendering, 3+ geometry types, 3+ camera presets, crossfade/dip_to_black/cut transitions, audio sync, manual playback check, VLC + browser playback.
- [ ] **AC-04:** SC-03 specifies environment requirements, 3-run median, and the 15-minute threshold.
- [ ] **AC-05:** SC-05 documents POST/poll/download with HTTP status codes, timeout, and ffprobe validation.
- [ ] **AC-06:** SC-06 tests both directions: 20+ valid manifests render successfully; 22+ invalid manifests fail validation; 3 pre-flight failures fail before rendering.
- [ ] **AC-07:** SC01-03 provides a determinism procedure with frame MD5 comparison and PSNR fallback.
- [ ] **AC-08:** All fixtures reference only verified geometries and cameras.
- [ ] **AC-09:** The plan specifies how to generate test images and audio files (literal commands).
- [ ] **AC-10:** `ffprobe` validation uses a single canonical invocation with explicit JSON field assertions.

### Traceability

- [ ] **AC-11:** Each procedure references relevant TC and C identifiers.
- [ ] **AC-12:** The traceability matrix (below) maps all covered TCs and Cs to procedures.

## Edge Cases and Error Handling

### Environment Issues

| Scenario | Plan Response |
|---|---|
| Machine has <4GB RAM | SC03-01 detects and reports. Benchmark results are informational, not pass/fail. |
| No FFmpeg installed | SMOKE-01 precondition fails. All suites blocked. |
| No Chromium available | SMOKE-01 precondition fails. All suites blocked. |
| GPU not available for SC03-03 | SC03-03 is optional. Skip and note. |

### Timing Variability

| Scenario | Plan Response |
|---|---|
| SC-03 benchmark marginally exceeds 15 min | Median of 3 runs is the value. If median < 15 min, pass. |
| Duration tolerance (ffprobe vs expected) | ±0.5s for 60s videos. ±0.5s for short SC-06 videos. |
| Frame count rounding | ±10 frames tolerance for the 60s benchmark (1800 ±10). |

### Partial Infrastructure

| Scenario | Plan Response |
|---|---|
| OBJ-075 not complete | Suite 3 (SC-05) is blocked. Report as "blocked." |
| New geometries verified after plan written | OBJ-078 may add them to the valid corpus but is not required. |

### Test Failures

| Scenario | Plan Response |
|---|---|
| Valid manifest fails to render | SC-06 forward direction failure. Document error, manifest ID, and component that failed. File as bug. |
| Invalid manifest passes validation | SC-06 backward direction failure. Document manifest ID and which validation rule is missing. File as bug against OBJ-016/OBJ-004. |
| Determinism check fails | SC01-03 failure. Document the differing frames and PSNR values. Investigate source of non-determinism (likely FFmpeg encoder or Three.js rounding). |

## Traceability Matrix

| TC/Constraint | Procedures |
|---|---|
| TC-02 (Render performance) | SC03-02 |
| TC-04 (Geometries eliminate manual positioning) | SC01-01 (no manual coords in fixture) |
| TC-06 (Deterministic output) | SC01-03 |
| TC-07 (Validation catches errors) | SC06-BACKWARD-A, SC06-BACKWARD-B |
| TC-10 (Transitions mask seams) | SC01-01, SC01-02 (visual check) |
| TC-11 (Docker/software WebGL) | SC03-02 (software WebGL) |
| TC-13 (Audio drives video length) | SC01-04 |
| C-02 (Puppeteer+Three.js+FFmpeg) | SC01-01 |
| C-03 (Deterministic timing) | SC01-03 |
| C-04 (Resolution/frame rate) | SC06-FORWARD (V-09 portrait, V-10 24fps, V-11 30fps) |
| C-05 (Deterministic output) | SC01-03 |
| C-07 (Audio sync) | SC01-01, SC01-04 |
| C-08 (Render performance) | SC03-02 |
| C-10 (Manifest validation) | SC06-BACKWARD-A, SC06-BACKWARD-B |
| C-11 (Software rendering) | SC03-02 |

## Integration Points

### Depends On

| Dependency | What This Plan Uses |
|---|---|
| **OBJ-035** (Orchestrator) | SC-01 and SC-03 procedures render via the orchestrator (through CLI). SC-06 pre-flight tests rely on OBJ-035's error codes. |
| **OBJ-046** (CLI) | All procedures use `depthkit render` and `depthkit validate`. CLI output format is referenced for assertion patterns. |
| **OBJ-037** (Scene Sequencer) | Transition tests (crossfade, dip_to_black) rely on OBJ-037 through OBJ-035. |
| **OBJ-038** (Scene Timing) | Audio sync tests rely on OBJ-038 through OBJ-035. |

### Consumed By

| Consumer | How |
|---|---|
| **OBJ-078** (E2E Test Execution) | Primary consumer. Creates fixtures, executes procedures, reports results. |

### File Placement

```
nodes/
  OBJ-077/
    meta.json    # UPDATED — status: "complete"
    output.md    # NEW — this specification / test plan
```

## Open Questions

None. All open questions from Round 1 have been resolved and incorporated into the procedures.

---

I believe this revision addresses all critical and major issues raised by the Challenger:

- **C1 (no actual procedures):** Every procedure now has literal CLI commands, exact `ffprobe` field assertions, and concrete pass/fail thresholds.
- **C2 (unresolved OQs):** All four resolved at the top and woven into procedures.
- **M1 (no ffprobe commands):** Canonical invocation specified; JSON field paths listed per procedure.
- **M2 (audio-proportional untestable):** Reframed as observable behavior test (D10, SC01-04).
- **M3 (pre-flight conflation):** Split into F-04a and F-04b with separate procedures (SC06-BACKWARD-A vs SC06-BACKWARD-B).
- **M4 (redundant fixtures):** Merged into single F-01 (D2).
- **M5 (no determinism procedure):** SC01-03 added with frame MD5 + PSNR fallback.
- **m1 (0.1s scene):** Documented in F-03 V-12 as 3 frames at 30fps.
- **m2 (image dimensions):** Literal ImageMagick commands specified.
- **m3 (recursive test strategy):** Replaced with traceability matrix.
- **m4 (frame count check):** Added to SC01-01 step 10.

Challenger, please review and verify.

---

## Round 4 — spec_challenger

I've carefully verified the Round 3 revision against every objection from Round 2.

## Verification of Fixes

| Issue | Status | Verification |
|-------|--------|-------------|
| C1 (no actual procedures) | ✅ Fixed | SMOKE-01, SC01-01 through SC01-04, SC03-01 through SC03-03, SC05-01 through SC05-03, SC06-FORWARD, SC06-BACKWARD-A, SC06-BACKWARD-B all have literal CLI commands, exact ffprobe assertions, and pass/fail thresholds. |
| C2 (unresolved OQs) | ✅ Fixed | All four resolved at the top and woven into procedures. |
| M1 (no ffprobe commands) | ✅ Fixed | Canonical invocation specified. JSON field paths listed per procedure. |
| M2 (audio-proportional untestable) | ✅ Fixed | Reframed as observable behavior test (D10, SC01-04). |
| M3 (pre-flight conflation) | ✅ Fixed | Split into F-04a (validation, tested via `validate`) and F-04b (pre-flight, tested via `render`). |
| M4 (redundant fixtures) | ✅ Fixed | Merged into single F-01 per D2. |
| M5 (no determinism procedure) | ✅ Fixed | SC01-03 with frame MD5 primary and PSNR ≥ 60dB fallback. |
| m1-m4 | ✅ Fixed | All addressed (0.1s scene, image dimensions with ImageMagick, recursive section replaced, frame count check added). |

## Remaining Minor Issues (Non-Blocking)

**m-A: SC01-04 step 2 has an OR that OBJ-078 must resolve.** "Create a manifest with 5 scenes, each with `duration: 1.0` (as proportional weights)... OR with explicit durations summing to 45s." D10 already says to test observable behavior. I'll clean this up in the final spec by choosing explicit durations, since that's the guaranteed path.

**m-B: P-03 error code is uncertain** ("AUDIO_MUX_FAILED or caught at pre-flight"). Minor — I'll note both as acceptable.

**m-C: V-08 and V-17 warning codes not asserted.** The procedure says "record warnings" but doesn't assert specific codes. I'll add expected codes.

These are trivial editorial fixes I can make in the final write. No structural changes needed.

The spec is structurally sound, procedures are concrete and executable, fixtures are detailed, traceability is complete, and all critical/major issues have been satisfactorily resolved.

CONCLUSION:

The spec defines the end-to-end integration test plan for depthkit, covering SC-01 (60s 5-scene render), SC-03 (performance benchmark), SC-05 (n8n integration, gated), and SC-06 (manifest validation soundness). It delivers concrete test procedures with literal CLI commands, exact ffprobe assertions, and unambiguous pass/fail criteria. A single merged benchmark fixture (F-01) serves both SC-01 and SC-03. The invalid manifest corpus is correctly split into validation failures (F-04a, tested via `depthkit validate`) and pre-flight failures (F-04b, tested via `depthkit render`). Determinism is tested via frame MD5 comparison with PSNR ≥ 60dB fallback. Performance benchmarking uses 3-run median against the 15-minute threshold on software WebGL.

Let me now write the final spec and update meta.json.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Write,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me check the current state of the node directory and meta.json before writing.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-077",
     3→  "description": "End-to-end integration test plan -- documents test procedures for SC-01 (60-second, 5-scene video renders to valid MP4), SC-03 (performance target met), SC-05 (n8n POST/poll/download works), SC-06 (no valid manifest produces render error, no invalid manifest passes validation). This is the test plan document; actual execution is OBJ-078.",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035", "OBJ-046", "OBJ-037", "OBJ-038"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 6 validation plan. Documents procedures only -- OBJ-078 executes them."
    12→}
    13→

[Tool: Bash]
  Input: {
  "command": "ls -la /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/",
  "description": "List OBJ-077 node directory contents"
}
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:30 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   729 Mar 22 19:30 meta.json
Good. Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/output.md",
  "content": "# Specification: OBJ-077 \u2014 End-to-End Integration Test Plan\n\n## Summary\n\nOBJ-077 delivers the **end-to-end integration test plan** for depthkit \u2014 concrete, step-by-step procedures for verifying SC-01 (60-second, 5-scene video renders to valid MP4), SC-03 (performance target met), SC-05 (n8n POST/poll/download works), and SC-06 (manifest validation soundness). This document IS the test plan: it contains executable procedures with literal CLI commands, exact `ffprobe` invocations, and unambiguous pass/fail thresholds. OBJ-078 executes these procedures.\n\n## Interface Contract\n\nOBJ-077 produces no code module. Its deliverable is this test plan document (`output.md`). The plan specifies test fixtures, procedures, and validation commands that OBJ-078 follows.\n\n---\n\n## Resolved Design Questions\n\n**Determinism Comparison Method:** Frame MD5 comparison as primary method. Extract per-frame checksums via `ffmpeg -i output.mp4 -f framemd5 -`. If frame MD5s differ, compute per-frame PSNR via `ffmpeg -i output1.mp4 -i output2.mp4 -lavfi psnr -f null -`. PSNR >= 60dB on all frames constitutes \"visually indistinguishable.\" Below 60dB on any frame is a fail.\n\n**Benchmark Run Count:** 3 runs, report median. No other CPU-intensive processes running during benchmark. Document all three values.\n\n**SC-05 Poll Timeout:** 20-minute timeout, 10-second poll interval. Timeout is a fail condition.\n\n**Smoke Test:** Included as Suite 0. A quick (<30 second) 2-second, 1-scene render at 320x240 validates the pipeline is functional before committing to full suites.\n\n---\n\n## Test Fixtures\n\n### Fixture F-01: Benchmark Manifest\n\nA single manifest used for both SC-01 (correctness) and SC-03 (performance). Exercises the full pipeline.\n\n**Composition:**\n```json\n{\n  \"version\": \"3.0\",\n  \"composition\": {\n    \"width\": 1920,\n    
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/meta.json",
  "content": "{\n  \"id\": \"OBJ-077\",\n  \"description\": \"End-to-end integration test plan -- documents test procedures for SC-01 (60-second, 5-scene video renders to valid MP4), SC-03 (performance target met), SC-05 (n8n POST/poll/download works), SC-06 (no valid manifest produces render error, no invalid manifest passes validation). This is the test plan document; actual execution is OBJ-078.\",\n  \"category\": \"integration\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:00:00Z\",\n  \"depends_on\": [\"OBJ-035\", \"OBJ-046\", \"OBJ-037\", \"OBJ-038\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 6 validation plan. Delivers concrete test procedures with literal CLI commands, ffprobe assertions, and pass/fail thresholds across 5 suites (Smoke, SC-01, SC-03, SC-05, SC-06). SC-05 suite gated on OBJ-057/OBJ-075. All fixtures use only verified geometries and cameras. OBJ-078 executes these procedures.\",\n  \"status\": \"complete\",\n  \"review_status\": null\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/meta.json has been updated successfully.
Now commit:
[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Check git status"
}
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-077/meta.json

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
	nodes/OBJ-017/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-019/transcript.md
	nodes/OBJ-020/transcript.md
	nodes/OBJ-021/transcript.md
	nodes/... [truncated]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-077/output.md nodes/OBJ-077/meta.json && git commit -m \"$(cat <<'EOF'\nOBJ-077: End-to-end integration test plan specification\n\nDelivers concrete test procedures for SC-01, SC-03, SC-05, SC-06 across\n5 suites (Smoke, SC-01 rendering, SC-03 performance, SC-05 n8n, SC-06\nvalidation soundness). Includes literal CLI commands, ffprobe assertions,\npass/fail thresholds, fixture specifications, and traceability matrix.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-077 spec and meta.json"
}
[Tool Result] [master 3c78409] OBJ-077: End-to-end integration test plan specification
 2 files changed, 850 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-077/output.md
The specification for OBJ-077 has been written to `nodes/OBJ-077/output.md` and committed. Here's what was delivered:

**5 test suites** with concrete, executable procedures:
- **Suite 0 (Smoke):** Quick 2s render at 320x240 to validate pipeline health
- **Suite 1 (SC-01):** 60s 5-scene benchmark render with ffprobe validation, manual playback check, frame-level determinism test (MD5 + PSNR fallback), and audio-duration-drives-video-length test
- **Suite 2 (SC-03):** 3-run median benchmark on 4-core/4GB+ machine, 15-minute threshold on software WebGL
- **Suite 3 (SC-05):** n8n POST/poll/download procedure, gated on OBJ-057/OBJ-075
- **Suite 4 (SC-06):** 20 valid manifests (forward direction), 22 validation failures (backward-A), 3 pre-flight failures (backward-B)

**Key design decisions:** merged benchmark fixture, split invalid corpus into validation vs. pre-flight categories, verified-only geometries/cameras in all fixtures, small resolutions for SC-06 corpus speed, observable-behavior testing for audio sync.
