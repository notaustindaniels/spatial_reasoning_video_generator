# Specification: OBJ-073 — Deterministic Output Verification Plan

## Summary

OBJ-073 delivers the **deterministic output verification plan** — a comprehensive procedure and supporting utility module for verifying constraint C-05 (deterministic output) and testable claim TC-06 (virtualized clock produces deterministic output). This objective provides: (1) a systematic audit of all non-determinism sources in the depthkit pipeline, (2) a seeding strategy for any randomized elements, (3) a post-hoc checksum comparison methodology using FFmpeg's `framemd5` muxer and PSNR filter, (4) a reusable programmatic API (`src/engine/determinism.ts`) that automates N-run comparison, and (5) concrete pass/fail thresholds with escalation procedures when non-determinism is detected. The CLI sub-command is explicitly deferred — this objective delivers the module and procedure document, not CLI wiring.

## Interface Contract

### Module: `src/engine/determinism.ts`

```typescript
/**
 * Utility module for deterministic rendering verification.
 * Used programmatically by integration tests and available for
 * future CLI integration (deferred to OBJ-083 or similar).
 *
 * Verification strategy: post-hoc comparison. Render N times to
 * N output MP4s, then compare decoded frame content using FFmpeg's
 * framemd5 muxer and psnr filter. This avoids any modification to
 * the Orchestrator's internals (OBJ-035 D1: single render() method,
 * no exposed sub-components).
 */

import type { OrchestratorConfig, OrchestratorResult } from './orchestrator.js';

// ────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────

export interface VerifyDeterminismConfig {
  /**
   * Factory function that creates a fresh OrchestratorConfig for each run.
   * Called N times (once per run). The factory receives the run index
   * (0-based) and must return a config with a unique `outputPath` per run.
   *
   * All configs MUST share identical manifest, registry, geometryRegistry,
   * cameraRegistry, and assetsDir — only outputPath should differ.
   * The verification module does NOT enforce this; the caller is
   * responsible for producing equivalent configs.
   */
  createConfig: (runIndex: number) => OrchestratorConfig;

  /**
   * Number of render runs to compare. Default: 3. Minimum: 2. Maximum: 10.
   * Values outside [2, 10] throw a RangeError synchronously.
   */
  runs?: number;

  /**
   * Advisory flag indicating whether deterministic encoding (single-threaded
   * FFmpeg) is enabled on the configs produced by createConfig.
   * The verification module does NOT set this on the configs — it is the
   * caller's responsibility to set `deterministic: true` on the
   * FFmpegEncoder config within createConfig. This flag is recorded
   * in the report for documentation purposes only.
   * Default: true.
   */
  deterministicEncoding?: boolean;

  /**
   * Path to FFmpeg binary for framemd5 extraction and PSNR computation.
   * Default: resolved via resolveFFmpegPath() (OBJ-013).
   */
  ffmpegPath?: string;

  /**
   * Output directory for the verification report JSON.
   * Created recursively if it does not exist.
   * Default: process.cwd().
   */
  reportDir?: string;

  /**
   * Progress callback invoked after each run completes.
   */
  onRunComplete?: (runIndex: number, totalRuns: number, result: OrchestratorResult) => void;
}

// ────────────────────────────────────────────
// Results
// ────────────────────────────────────────────

export interface FrameComparisonResult {
  /** Total frames per run. */
  totalFrames: number;

  /** Number of frames identical across all runs. */
  identicalFrames: number;

  /** Number of frames that differ across at least one pair of runs. */
  divergentFrames: number;

  /**
   * For divergent frames: worst-case PSNR (dB) across all pairs.
   * Only populated if divergentFrames > 0.
   * Infinity means frames are identical (should not occur if divergent).
   */
  worstCasePsnrDb?: number;

  /** Frame indices that diverged (zero-indexed). */
  divergentFrameIndices: number[];

  /**
   * Verdict for this comparison:
   * - 'byte-identical': All frame MD5s match across all runs.
   * - 'visually-indistinguishable': MD5s differ but PSNR >= 60dB on all divergent frames.
   * - 'failed': PSNR < 60dB on at least one divergent frame.
   */
  verdict: 'byte-identical' | 'visually-indistinguishable' | 'failed';
}

export interface NonDeterminismSource {
  /** Layer where non-determinism was detected. */
  layer: 'rendering' | 'encoding' | 'container-metadata';
  /** Description of the source. */
  description: string;
  /** Severity: 'blocking' violates C-05; 'cosmetic' is metadata-only. */
  severity: 'blocking' | 'cosmetic';
}

export interface VerifyDeterminismReport {
  /** ISO timestamp of when the verification was run. */
  timestamp: string;

  /** Number of runs completed successfully. */
  runsCompleted: number;

  /** Number of runs requested. */
  runsRequested: number;

  /** Configuration flags recorded for documentation. */
  config: {
    deterministicEncoding: boolean;
    gpu: boolean;
  };

  /** Encoded frame MD5 comparison results (primary comparison). */
  encodedComparison: FrameComparisonResult;

  /** Per-run render durations (ms). Indexed by successful run order. */
  renderDurationsMs: number[];

  /** Per-run output file paths. Indexed by successful run order. */
  outputPaths: string[];

  /** Non-determinism sources identified (if any). */
  identifiedSources: NonDeterminismSource[];

  /** Overall pass/fail. True if verdict is 'byte-identical' or 'visually-indistinguishable'. */
  passed: boolean;

  /** Human-readable summary string. */
  summary: string;
}

// ────────────────────────────────────────────
// Errors
// ────────────────────────────────────────────

export type VerifyDeterminismError =
  | 'ALL_RUNS_FAILED'       // no successful renders
  | 'INSUFFICIENT_RUNS'     // fewer than 2 successful renders
  | 'FRAME_COUNT_MISMATCH'  // successful runs produced different frame counts
  | 'FFMPEG_ANALYSIS_FAILED'; // framemd5 or psnr extraction failed

export class DeterminismError extends Error {
  readonly code: VerifyDeterminismError;
  readonly cause?: Error;
  constructor(code: VerifyDeterminismError, message: string, cause?: Error);
}

// ────────────────────────────────────────────
// Primary Entry Point
// ────────────────────────────────────────────

/**
 * Runs the full deterministic output verification procedure.
 *
 * Procedure:
 * 1. Validate run count is in [2, 10]. Throw RangeError if not.
 * 2. For each run i in [0, runs):
 *    a. Call createConfig(i) to get an OrchestratorConfig.
 *    b. Create a new Orchestrator(config).
 *    c. Call orchestrator.render().
 *    d. Store the OrchestratorResult and output path.
 *    e. If render fails: log the error, mark run as failed, continue to next run.
 *    f. Call onRunComplete if provided (only for successful runs).
 * 3. If fewer than 2 runs succeeded: throw DeterminismError('INSUFFICIENT_RUNS')
 *    or DeterminismError('ALL_RUNS_FAILED') if zero succeeded.
 * 4. Verify all successful runs produced the same frame count
 *    (from OrchestratorResult.totalFrames).
 *    If not: throw DeterminismError('FRAME_COUNT_MISMATCH').
 * 5. Extract per-frame MD5 checksums from each output MP4 via extractFrameMd5s().
 * 6. Compare MD5s across all pairs of successful runs via compareFrameMd5s().
 * 7. If any frames diverge: compute per-frame PSNR between each divergent pair
 *    via computePerFramePsnr(). Record worst-case PSNR.
 * 8. Build FrameComparisonResult with verdict:
 *    - All MD5s match: 'byte-identical'.
 *    - MD5s differ, worst PSNR >= 60dB: 'visually-indistinguishable'.
 *    - Any PSNR < 60dB: 'failed'.
 * 9. Classify non-determinism sources into identifiedSources.
 * 10. Write VerifyDeterminismReport as JSON to reportDir/determinism-report.json.
 * 11. Return the report.
 *
 * @throws RangeError if runs is outside [2, 10].
 * @throws DeterminismError on procedural failures (not individual render failures).
 */
export function verifyDeterminism(
  config: VerifyDeterminismConfig
): Promise<VerifyDeterminismReport>;

// ────────────────────────────────────────────
// Lower-Level Utilities (exported for testing and for OBJ-077/OBJ-078)
// ────────────────────────────────────────────

/**
 * Extracts per-frame MD5 checksums from an encoded MP4 using
 * FFmpeg's framemd5 muxer.
 *
 * Command: ffmpeg -i <mp4Path> -f framemd5 -
 *
 * Parses output lines matching the framemd5 format:
 *   <stream_index>, <dts>, <pts>, <duration>, <size>, <md5>
 * Lines starting with '#' are comments and are skipped.
 * Extracts the md5 field (last column) from each data line.
 *
 * @returns Array of lowercase hex MD5 strings, one per frame, in decode order.
 * @throws DeterminismError('FFMPEG_ANALYSIS_FAILED') if FFmpeg exits non-zero
 *         or if output cannot be parsed.
 */
export function extractFrameMd5s(
  mp4Path: string,
  ffmpegPath?: string
): Promise<string[]>;

/**
 * Compares frame MD5 arrays across multiple runs (all-pairs comparison).
 *
 * For N runs, compares every pair (i, j) where i < j. A frame is
 * "divergent" if its MD5 differs in any pair.
 *
 * Preconditions:
 * - runs.length >= 2. Throws DeterminismError('INSUFFICIENT_RUNS') otherwise.
 * - All arrays must have the same length. Throws
 *   DeterminismError('FRAME_COUNT_MISMATCH') if lengths differ.
 *
 * @param runs - Array of runs; each run is an array of lowercase hex MD5 strings.
 *               Caller is responsible for passing only completed runs.
 * @returns FrameComparisonResult with verdict based on MD5 comparison only
 *          (worstCasePsnrDb is undefined — PSNR must be computed separately
 *          for divergent frames).
 */
export function compareFrameMd5s(
  runs: string[][]
): FrameComparisonResult;

/**
 * Computes per-frame PSNR between two MP4 files using FFmpeg's psnr filter.
 *
 * Command: ffmpeg -i <path1> -i <path2> -lavfi psnr=stats_file=<tmpFile> -f null -
 *
 * Parses the stats file. Each line contains: n:<frame> ... psnr_avg:<value> ...
 * Extracts psnr_avg per frame. The value "inf" is parsed as Infinity.
 *
 * The temporary stats file is created in os.tmpdir() and deleted after parsing.
 *
 * @returns Array of PSNR values (dB) per frame. Infinity for identical frames.
 * @throws DeterminismError('FFMPEG_ANALYSIS_FAILED') if FFmpeg exits non-zero
 *         or if stats file cannot be parsed.
 */
export function computePerFramePsnr(
  mp4Path1: string,
  mp4Path2: string,
  ffmpegPath?: string
): Promise<number[]>;

/**
 * Generates the human-readable summary string for a report.
 *
 * Examples:
 * - "Determinism check PASSED: All 60 frames byte-identical across 3 runs."
 * - "Determinism check PASSED: 2 of 60 frames diverged (worst PSNR: 72.3dB, visually indistinguishable) across 3 runs."
 * - "Determinism check FAILED: 5 of 60 frames diverged (worst PSNR: 42.1dB) across 3 runs."
 */
export function formatSummary(report: VerifyDeterminismReport): string;

// ────────────────────────────────────────────
// Seeding (Contingency — may never be needed)
// ────────────────────────────────────────────

/**
 * Deterministic PRNG for use if the code audit (D5) discovers
 * randomized elements in the rendering path that cannot be eliminated.
 *
 * Uses xorshift128 for reproducibility. Seeded from a string
 * (e.g., a manifest content hash via SHA-256).
 *
 * If the audit finds no randomized elements (expected outcome),
 * this class exists but is unused in the rendering pipeline.
 */
export class DeterministicRng {
  /**
   * Create from a seed string. The string is hashed (SHA-256)
   * to derive the 128-bit internal state.
   */
  static fromSeed(seed: string): DeterministicRng;

  /** Returns a float in [0, 1) deterministically. */
  next(): number;
}
```

## Design Decisions

### D1: Non-Determinism Source Audit — The Layered Model

**Decision:** The verification plan treats the pipeline as four distinct layers, each of which can independently introduce non-determinism.

| Layer | Component | Potential Non-Determinism Sources | Mitigation |
|-------|-----------|----------------------------------|------------|
| **L1: Scene State** | FrameClock, camera interpolation, easing functions | `Math.random()`, `Date.now()`, uninitialized variables | Audit: no `Math.random()` or `Date.now()` calls in the render path. All state is derived from frame number. |
| **L2: WebGL Rendering** | Three.js + Chromium's WebGL (SwiftShader in software mode) | GPU driver differences, floating-point rounding, texture upload order, async operations | Mitigate: software rendering (SwiftShader) is deterministic for same Chromium version on same architecture. Pin Chromium version via Puppeteer. |
| **L3: Frame Capture** | CDP `Page.captureScreenshot` or `canvas.toDataURL()` | PNG compression non-determinism, async capture timing | Mitigate: the virtualized clock (C-03) ensures each frame is fully rendered before capture. PNG compression is deterministic for same input pixels. |
| **L4: FFmpeg Encoding** | H.264 encoding, MP4 container | Multithreaded encoding race conditions, container creation timestamps, encoder version differences | Mitigate: `deterministic: true` on FFmpegEncoder (single-threaded). Container metadata (creation_time) will differ but is not part of the video stream. |

**Rationale:** Understanding *where* non-determinism can enter allows targeted verification. The `framemd5` muxer decodes the video stream and checksums each decoded frame, isolating video content from container metadata. If framemd5 checksums match, L1-L4 video content is deterministic. If they differ, PSNR localizes the severity.

### D2: Post-Hoc Comparison Only — No Orchestrator Modification

**Decision:** The verification uses exclusively **post-hoc comparison** of rendered MP4 files. It does not intercept pixel buffers mid-pipeline and does not modify or extend the Orchestrator's interface.

The procedure is: render N times -> extract per-frame MD5 from each MP4 via `ffmpeg -f framemd5` -> compare -> compute PSNR if divergent.

Pre-encoding pixel hash interception (comparing raw PNG buffers before FFmpeg) is deferred to OQ-A. It would require either modifying OBJ-035's interface (adding a frame buffer callback) or reimplementing the orchestrator's render loop — both are out of scope for OBJ-073.

**Rationale:** OBJ-035 D1 mandates a single `render()` method with no exposed sub-components. Adding a `onFrameBuffer` callback would modify a verified spec. Reimplementing the loop would create maintenance coupling. Post-hoc comparison via `framemd5` is sufficient: it decodes the H.264 stream and checksums each decoded frame, which tests the full L1-L4 pipeline. When combined with `deterministic: true` encoding (single-threaded), any non-determinism in L1-L3 propagates to the decoded frames and is detected.

**Diagnostic gap:** If encoded MD5s differ, we cannot directly distinguish L1-L3 (rendering) from L4 (encoding) non-determinism. The report notes this limitation. A two-run comparison — one with `deterministic: true` and one without — can isolate L4 issues: if deterministic encoding makes the divergence disappear, the source was L4.

### D3: MD5 for Frame Comparison (FFmpeg-Driven)

**Decision:** Use MD5 checksums from FFmpeg's `framemd5` muxer as the primary comparison method. FFmpeg's muxer is authoritative and uses MD5 — we use what it provides.

**Rationale:** `framemd5` decodes the video stream and checksums each decoded frame's raw pixel data. This is the decoded pixel content, not the encoded bitstream. Two H.264 streams that decode to identical pixels will produce identical framemd5 output even if the encoded bytes differ (e.g., due to different NAL unit packaging). This makes framemd5 the right tool for C-05 verification.

### D4: PSNR Threshold — 60 dB

**Decision:** When frame MD5s differ, the fallback acceptance criterion is PSNR >= 60 dB on every divergent frame across every pair of runs. Inherited from OBJ-077's SC01-03.

**Rationale:** 60 dB means sub-pixel-level differences invisible to human perception. C-05's "visually indistinguishable" criterion is satisfied. The threshold is conservative — typical "visually lossless" starts at 40 dB.

### D5: Seeding Strategy — Audit-First, Seed-As-Contingency

**Decision:** The verification plan mandates a **code audit** for randomized elements. The depthkit render path should contain **zero** calls to `Math.random()`, `Date.now()` (for state), `crypto.getRandomValues()`, or any non-deterministic function.

If any randomized element is discovered:
1. **Remove it** if unnecessary (preferred).
2. **Replace it** with a deterministic alternative derived from the frame number.
3. **Seed it** with `DeterministicRng.fromSeed(manifestContentHash)` only if removal/replacement is impossible.

**Current assessment:** Based on existing specs (OBJ-009, OBJ-010, OBJ-011, OBJ-013, OBJ-035), no component uses `Math.random()` or non-deterministic functions in the render path. The `DeterministicRng` class exists as a contingency.

### D6: Container Metadata Differences Are Cosmetic

**Decision:** MP4 container metadata (creation timestamps, encoder version strings) will differ between runs. These are classified as **cosmetic** (`severity: 'cosmetic'`) and do not constitute a C-05 violation. The `framemd5` muxer ignores container metadata — it only checksums decoded frame pixels.

### D7: Run Count — 3 Default, [2, 10] Range

**Decision:** Default 3 runs (per TC-06: "render same composition 3 times, compare checksums"). Minimum 2 (need at least one pair). Maximum 10 (prevent resource exhaustion). Out-of-range values throw `RangeError` synchronously from `verifyDeterminism()`.

Comparison is all-pairs: for N successful runs, every pair `(i, j)` where `i < j` is compared. For 3 runs, that's 3 pairs; for 5 runs, 10 pairs.

### D8: CLI Sub-Command Deferred

**Decision:** OBJ-073 delivers the `src/engine/determinism.ts` module and this verification procedure document. The CLI sub-command (`depthkit verify-determinism`) is **not** delivered by OBJ-073. CLI integration is deferred to OBJ-083 (Extended CLI, `status: "open"`) or a new objective.

**Rationale:** OBJ-046 (CLI) is `status: "verified"`. OBJ-073 depends only on OBJ-035, not OBJ-046. Adding a CLI sub-command would create an undeclared dependency on OBJ-046's registration mechanism and directory structure. The core value of OBJ-073 is the verification module and procedure, which integration tests and OBJ-078 can consume programmatically.

### D9: Relationship to OBJ-077's SC01-03

**Decision:** OBJ-073 is the **comprehensive verification module and procedure**; OBJ-077's SC01-03 is a **quick check** that can use OBJ-073's utilities. Specifically:
- OBJ-077 SC01-03 does 2 runs, compares encoded frame MD5s, has a simple pass/fail.
- OBJ-073's `verifyDeterminism()` does N runs (default 3), computes PSNR on divergent frames, classifies non-determinism sources, and produces a detailed report.

OBJ-078 (which executes OBJ-077's tests) can call `verifyDeterminism()` or use the lower-level utilities (`extractFrameMd5s`, `compareFrameMd5s`, `computePerFramePsnr`) directly.

### D10: Software Rendering Required for Cross-Run Determinism

**Decision:** The verification procedure assumes software WebGL (SwiftShader) for determinism guarantees. GPU-accelerated WebGL is **not guaranteed** to produce identical output across runs due to driver scheduling non-determinism. The report records the `gpu` flag for documentation. If GPU mode is used and MD5s diverge, the report notes this as a likely cause under `identifiedSources`.

### D11: Graceful Handling of Partial Run Failures

**Decision:** If a render run fails (Orchestrator throws), the failure is logged and that run is skipped. If fewer than 2 runs succeed, `verifyDeterminism()` throws `DeterminismError('INSUFFICIENT_RUNS')` (or `'ALL_RUNS_FAILED'` if zero succeeded). If 2+ runs succeed, comparison proceeds on successful runs only. Failed runs are noted in the report (`runsCompleted < runsRequested`).

The lower-level `compareFrameMd5s(runs)` requires `runs.length >= 2` and throws `DeterminismError('INSUFFICIENT_RUNS')` if fewer are provided. It throws `DeterminismError('FRAME_COUNT_MISMATCH')` if any array has a different length from the others. The caller (`verifyDeterminism`) is responsible for filtering to completed runs before calling comparison functions.

## Acceptance Criteria

### Code Audit

- [ ] **AC-01:** A grep of all source files under `src/engine/`, `src/page/`, `src/scenes/`, `src/camera/` confirms zero occurrences of `Math.random()` in the rendering path. Test utility files and non-render-path code (e.g., `src/engine/determinism.ts` itself) are excluded.
- [ ] **AC-02:** A grep confirms zero occurrences of `Date.now()` or `new Date()` in the rendering path, except in diagnostic/logging code that does not affect rendered pixel output (e.g., `elapsedMs` in `RenderProgress`).
- [ ] **AC-03:** A grep confirms zero occurrences of `crypto.getRandomValues()` or `crypto.randomUUID()` in the rendering path.

### Determinism Verification

- [ ] **AC-04:** Rendering the same single-scene manifest (stage geometry, static camera, 1 plane, 10 frames at 320x240) 3 times with software WebGL and `deterministic: true` encoding produces byte-identical per-frame MD5 checksums (via `extractFrameMd5s`). Verdict: `'byte-identical'`.
- [ ] **AC-05:** Rendering the same multi-scene manifest (2 scenes with crossfade transition, 20 frames at 320x240) 3 times with software WebGL and `deterministic: true` encoding produces byte-identical per-frame MD5 checksums. Verdict: `'byte-identical'`.
- [ ] **AC-06:** If frame MD5s diverge on any frame but PSNR >= 60 dB on all divergent frames, the verdict is `'visually-indistinguishable'` and `report.passed` is `true`.
- [ ] **AC-07:** If any divergent frame has PSNR < 60 dB, the verdict is `'failed'` and `report.passed` is `false`.

**Note on AC-04/AC-05:** Byte-identical MD5s are the **expected** outcome for software WebGL + deterministic encoding on the same hardware. AC-06 and AC-07 define the fallback acceptance logic if byte-identical is not achieved. Both `'byte-identical'` and `'visually-indistinguishable'` satisfy C-05.

### Module API

- [ ] **AC-08:** `verifyDeterminism()` with default config (3 runs) calls the config factory 3 times, renders 3 MP4s, extracts frame MD5s from each, compares all 3 pairs, and returns a `VerifyDeterminismReport` with `passed: true` for a deterministic manifest.
- [ ] **AC-09:** `verifyDeterminism()` with `runs: 1` throws `RangeError` synchronously. No renders are attempted.
- [ ] **AC-10:** `verifyDeterminism()` writes `determinism-report.json` to `reportDir`.
- [ ] **AC-11:** When one of 3 runs fails, `verifyDeterminism()` compares the 2 successful runs and returns a report with `runsCompleted: 2`, `runsRequested: 3`.
- [ ] **AC-12:** When all runs fail, `verifyDeterminism()` throws `DeterminismError('ALL_RUNS_FAILED')`.
- [ ] **AC-13:** When 2 successful runs produce different frame counts (different `OrchestratorResult.totalFrames`), `verifyDeterminism()` throws `DeterminismError('FRAME_COUNT_MISMATCH')`.

### Lower-Level Utilities

- [ ] **AC-14:** `extractFrameMd5s()` for a valid MP4 with 10 frames returns an array of 10 lowercase hex MD5 strings.
- [ ] **AC-15:** `extractFrameMd5s()` for a non-existent file throws `DeterminismError('FFMPEG_ANALYSIS_FAILED')`.
- [ ] **AC-16:** `compareFrameMd5s()` with 3 identical MD5 arrays returns `{ verdict: 'byte-identical', divergentFrames: 0 }`.
- [ ] **AC-17:** `compareFrameMd5s()` with arrays where frame 5 differs in one run returns `{ divergentFrames: 1, divergentFrameIndices: [5] }`.
- [ ] **AC-18:** `compareFrameMd5s()` with arrays of different lengths throws `DeterminismError('FRAME_COUNT_MISMATCH')`.
- [ ] **AC-19:** `computePerFramePsnr()` for two identical MP4s returns an array of `Infinity` values.
- [ ] **AC-20:** `computePerFramePsnr()` for two visually different MP4s returns finite dB values.

### Report Structure

- [ ] **AC-21:** The JSON report contains all fields defined in `VerifyDeterminismReport`: `timestamp`, `runsCompleted`, `runsRequested`, `config`, `encodedComparison`, `renderDurationsMs`, `outputPaths`, `identifiedSources`, `passed`, `summary`.
- [ ] **AC-22:** When MD5s match, `identifiedSources` is empty and `summary` includes "byte-identical".
- [ ] **AC-23:** When MD5s diverge, `identifiedSources` includes at least one entry identifying the layer and severity.

### Seeding (Contingency)

- [ ] **AC-24:** If the code audit (AC-01 through AC-03) discovers randomized elements in the render path, a `DeterministicRng` seeded from the manifest content hash replaces them, and AC-04/AC-05 pass afterward.
- [ ] **AC-25:** If no randomized elements are found (expected outcome), the audit result is documented in the verification report. `DeterministicRng` exists as an exported class but is unused in the rendering pipeline.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `runs` = 0, 1, 11, -1 | `RangeError` thrown synchronously from `verifyDeterminism()`. No renders attempted. |
| `createConfig` returns configs with different manifests | Undefined behavior (documented). Comparison may produce divergent frames that are expected differences, not non-determinism. The caller is responsible for config equivalence. |
| First render succeeds, second fails, third succeeds | Two successful runs compared. Report shows `runsCompleted: 2`, `runsRequested: 3`. |
| All renders fail | `DeterminismError('ALL_RUNS_FAILED')`. No report written. |
| Two successful runs produce different frame counts | `DeterminismError('FRAME_COUNT_MISMATCH')` with both counts in the error message. This is a critical non-determinism failure. |
| FFmpeg not found for `extractFrameMd5s` | `DeterminismError('FFMPEG_ANALYSIS_FAILED')` with cause. |
| FFmpeg `framemd5` output has unexpected format | `DeterminismError('FFMPEG_ANALYSIS_FAILED')` with descriptive message about parse failure. |
| Output directory for report doesn't exist | `fs.mkdirSync(reportDir, { recursive: true })` before writing. |
| Report file already exists | Overwritten. |
| `compareFrameMd5s` called with 0 or 1 runs | Throws `DeterminismError('INSUFFICIENT_RUNS')`. |
| Same manifest rendered on different machines | NOT in scope. C-05 specifies same inputs on same environment. Cross-machine determinism is not guaranteed due to CPU architecture, SSE/AVX differences, and Chromium version differences. Documented in the report config. |
| Container metadata (creation_time) differs between runs | Not detected by `framemd5` (which checksums decoded pixels, not container). Classified as cosmetic. Documented as a known non-determinism source in the audit checklist. |
| Disk runs out of space during multi-run verification | The render fails. Partial runs are cleaned up by the Orchestrator (OBJ-035 D2). Surviving runs are compared if 2+ succeeded. |

## Test Strategy

### Unit Tests: `test/unit/determinism.test.ts`

1. **compareFrameMd5s — all identical:** 3 runs with identical MD5 arrays -> `{ verdict: 'byte-identical', divergentFrames: 0, identicalFrames: N }`.
2. **compareFrameMd5s — one frame differs in one run:** 3 runs, frame 5 differs in run 2 -> `{ divergentFrames: 1, divergentFrameIndices: [5] }`.
3. **compareFrameMd5s — multiple frames differ:** Frames 0, 3, 7 differ -> `{ divergentFrames: 3, divergentFrameIndices: [0, 3, 7] }`.
4. **compareFrameMd5s — frame count mismatch:** Arrays of length 10 and 12 -> throws `FRAME_COUNT_MISMATCH`.
5. **compareFrameMd5s — exactly 2 runs:** Works correctly.
6. **compareFrameMd5s — 1 run:** Throws `INSUFFICIENT_RUNS`.
7. **extractFrameMd5s — parse real framemd5 output:** Given mock FFmpeg stdout matching the format `0,          0,          0,        1,   460800, a1b2c3d4...`, extracts correct MD5s.
8. **extractFrameMd5s — empty output:** Throws `FFMPEG_ANALYSIS_FAILED`.
9. **computePerFramePsnr — parse stats file:** Given mock psnr stats content `n:1 mse_avg:0.00 mse_y:0.00 ... psnr_avg:inf ...`, returns `[Infinity]`.
10. **computePerFramePsnr — finite PSNR values:** Returns correct dB.
11. **formatSummary — byte-identical:** Summary contains "byte-identical" and run count.
12. **formatSummary — divergent:** Summary lists divergent frame count and PSNR.
13. **DeterministicRng — same seed produces same sequence:** Two instances with same seed produce identical `next()` sequences over 1000 calls.
14. **DeterministicRng — different seeds produce different sequences:** Verified over first 10 calls.
15. **verifyDeterminism — run count validation:** `runs: 1` -> RangeError. `runs: 11` -> RangeError. `runs: 0` -> RangeError.

### Integration Tests: `test/integration/determinism.test.ts`

16. **End-to-end determinism — single scene:** Register a test geometry with 1 slot. Create a solid-color test image. Use `verifyDeterminism()` with `runs: 3`, 5 frames at 320x240, software WebGL, `deterministic: true`. Assert `report.passed === true` and `report.encodedComparison.verdict === 'byte-identical'`.
17. **End-to-end determinism — multi-scene with crossfade:** 2 scenes, crossfade transition, 10 frames total. Assert `report.passed === true`.
18. **extractFrameMd5s — real MP4:** Render a short MP4 via Orchestrator. Call `extractFrameMd5s`. Assert returns array of expected length with valid hex MD5 strings (32 chars, hex chars only).
19. **computePerFramePsnr — identical files:** Render one MP4. Call `computePerFramePsnr(mp4, mp4)`. Assert all values are `Infinity`.
20. **Partial run failure:** Mock one render to fail. Assert 2 remaining runs are compared and report shows `runsCompleted: 2`.
21. **Static analysis audit:** Run grep against `src/engine/`, `src/page/`, `src/scenes/`, `src/camera/` for `Math.random`, `Date.now`, `new Date`, `crypto.getRandomValues`, `crypto.randomUUID`. Assert zero matches in render-path files (excluding comments and the `determinism.ts` file itself).

### Relevant Testable Claims

- **TC-06:** Tests 16 and 17 directly verify: "render same composition 3 times, compare checksums."
- **C-05:** The entire objective validates C-05.
- **C-03:** Deterministic output is a consequence of the virtualized clock. TC-06 passing provides evidence for C-03 correctness.

## Integration Points

### Depends on

| Dependency | What OBJ-073 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class and `OrchestratorConfig` for performing render runs. `OrchestratorResult` for collecting render durations and `totalFrames`. The module creates a fresh `Orchestrator` per run and calls `render()`. |
| **OBJ-013** (FFmpegEncoder — transitive via OBJ-035) | `resolveFFmpegPath()` for locating FFmpeg binary used by `extractFrameMd5s` and `computePerFramePsnr`. The `deterministic` config flag on `FFmpegEncoderConfig` for single-threaded encoding. |

### Consumed by

| Downstream | How it uses OBJ-073 |
|---|---|
| **OBJ-077 / OBJ-078** (End-to-end test plan / execution) | SC01-03 can use `extractFrameMd5s()` and `compareFrameMd5s()` or the full `verifyDeterminism()` function. |
| **OBJ-083** (Extended CLI) | Can wire `verifyDeterminism()` into a `depthkit verify-determinism` CLI sub-command. |
| **CI/CD pipelines** | Can call `verifyDeterminism()` programmatically as a regression gate. |

### File Placement

```
depthkit/
  src/
    engine/
      determinism.ts              # NEW — verifyDeterminism(), extractFrameMd5s(),
                                  #       compareFrameMd5s(), computePerFramePsnr(),
                                  #       formatSummary(), DeterministicRng,
                                  #       DeterminismError, types
  test/
    unit/
      determinism.test.ts         # NEW — unit tests for comparison/report logic
    integration/
      determinism.test.ts         # NEW — end-to-end determinism verification
```

## Non-Determinism Audit Checklist

This checklist must be executed as part of the implementation and its results documented in the verification report. It is a static analysis procedure, not a runtime check.

### Rendering Path Files to Audit

All files under these directories are in the rendering path:
- `src/engine/` (excluding `determinism.ts` itself)
- `src/page/`
- `src/scenes/`
- `src/camera/`

### Prohibited Patterns

| Pattern | Grep Command | Allowed Exceptions |
|---|---|---|
| `Math.random` | `grep -rn "Math\.random" src/engine/ src/page/ src/scenes/ src/camera/` | None in render path. |
| `Date.now()` | `grep -rn "Date\.now()" src/engine/ src/page/ src/scenes/ src/camera/` | Timing/diagnostics that write to logs only and do not affect pixel output (e.g., `elapsedMs` in `RenderProgress`). |
| `new Date()` | `grep -rn "new Date()" src/engine/ src/page/ src/scenes/ src/camera/` | Same — logging/diagnostics only. |
| `crypto.getRandomValues` | `grep -rn "crypto\.getRandomValues\|crypto\.randomUUID" src/engine/ src/page/ src/scenes/ src/camera/` | None. |
| `performance.now()` | `grep -rn "performance\.now()" src/page/` | Diagnostics only, not used for timing render state. |
| `requestAnimationFrame` | `grep -rn "requestAnimationFrame" src/page/` | None in production render path (AP-02). Preview mode only. |

### Three.js-Specific Concerns

| Concern | Verification |
|---|---|
| Texture upload order | Three.js texture loading is synchronized by OBJ-011's `setupScene`, which waits for all texture loads before returning `success: true`. Deterministic. |
| Shader compilation caching | Chromium's shader cache may affect timing but not pixel output. The virtualized clock waits for render completion. Not a determinism concern. |
| Floating-point consistency | SwiftShader uses IEEE 754 on the CPU — deterministic for same architecture. GPU rendering may vary. This is why software WebGL is the default for verification. |
| `renderer.autoClear` | Configured once during `init()` per OBJ-010. Consistent across runs. |
| Object insertion order in scene graph | Three.js renders children in insertion order. As long as `setupScene` adds meshes in the same order (which it does — iterating the slots record), render order is deterministic. |

## Open Questions

### OQ-A: Should pre-encoding pixel hash interception be added later?

Comparing raw pixel buffers (SHA-256 of PNG data from FrameCapture) before encoding would isolate L1-L3 from L4 non-determinism definitively. This requires either:
- Adding an `onFrameBuffer` callback to OBJ-035's `OrchestratorConfig`, or
- A specialized test harness that composes PuppeteerBridge + FrameCapture directly.

Deferred. The post-hoc `framemd5` approach combined with `deterministic: true` encoding is sufficient for C-05 verification. If encoding-layer non-determinism is suspected, a two-run comparison (one with deterministic encoding, one without) can isolate it.

### OQ-B: Should cross-GPU-vs-software comparison be in scope?

Verifying that GPU-rendered output matches software-rendered output is stronger than C-05 requires. Deferred — the report format supports adding this as an `identifiedSources` layer in the future.

### OQ-C: Should audio stream determinism be verified?

Audio is an input file muxed via `-c:a copy` (passthrough) by OBJ-014. The audio stream in the output should be byte-identical to the input. Verifying this is low priority but could be added as an `ffmpeg -f streamhash` check. Deferred.
