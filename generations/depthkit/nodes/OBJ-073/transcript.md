# Deliberation Transcript: OBJ-073

---

## Round 1 — spec_author

I'll start by reading the relevant files to understand the current state of the project and any existing implementation details.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the current project structure and relevant files to understand the implementation state.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-073/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-073/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-035/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "src/engine/orchestrator.*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/engine/ffmpeg-encoder.*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/engine/**/*.ts"
}

[Tool: Glob]
  Input: {
  "pattern": "**/test/**/*deterministic*"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-073/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-073",
     3→  "description": "Deterministic output verification plan -- procedure for comparing frame checksums across multiple render runs on the same hardware to verify C-05 (deterministic output). Covers seeding strategy for any randomized elements. Addresses TC-06 (virtualized clock produces deterministic output -- render same composition 3 times, compare checksums).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 6 validation plan. Covers C-05 and TC-06."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "**/src/**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/*.ts",
  "path": "/Users/austin/spatial_reasoning_video_generator"
}
[Tool Result] No files found

[Tool: Grep]
  Input: {
  "pattern": "deterministic",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit",
  "output_mode": "files_with_matches"
}
[Tool Result] Found 59 files
feed.md
nodes/OBJ-069/transcript.md
nodes/OBJ-069/output.md
nodes/OBJ-039/transcript.md
nodes/OBJ-039/output.md
nodes/OBJ-077/transcript.md
nodes/OBJ-048/transcript.md
nodes/OBJ-077/output.md
nodes/OBJ-048/output.md
nodes/OBJ-037/transcript.md
nodes/OBJ-047/transcript.md
nodes/OBJ-047/output.md
nodes/OBJ-070/transcript.md
nodes/OBJ-070/output.md
nodes/OBJ-017/transcript.md
nodes/OBJ-017/meta.json
nodes/OBJ-036/transcript.md
nodes/OBJ-041/transcript.md
nodes/OBJ-041/output.md
nodes/OBJ-038/transcript.md
nodes/OBJ-038/output.md
nodes/OBJ-035/transcript.md
nodes/OBJ-035/meta.json
nodes/OBJ-035/output.md
nodes/OBJ-049/transcript.md
nodes/OBJ-049/output.md
nodes/OBJ-012/transcript.md
nodes/OBJ-012/output.md
nodes/OBJ-014/transcript.md
nodes/OBJ-014/output.md
nodes/OBJ-011/transcript.md
nodes/OBJ-011/output.md
nodes/OBJ-015/transcript.md
nodes/OBJ-018/transcript.md
nodes/OBJ-008/transcript.md
nodes/OBJ-008/output.md
nodes/OBJ-009/transcript.md
nodes/OBJ-009/meta.json
nodes/OBJ... [truncated]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-009/output.md",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-013/output.md",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md
Let me read the key dependency specs to understand determinism-related interfaces:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-013 — FFmpeg Encoder
     2→
     3→## Summary
     4→
     5→OBJ-013 implements the FFmpeg encoding module (`src/engine/ffmpeg-encoder.ts`) — the final stage of the rendering pipeline that receives raw pixel buffers via its API, pipes them to an FFmpeg child process over stdin, and produces an H.264-encoded MP4 file. This module is deliberately independent of Puppeteer: it accepts `Buffer` data from any source, making it testable in isolation and reusable if the frame-capture mechanism changes. It implements the encoding half of constraint C-02 and supports the determinism guarantee of C-05.
     6→
     7→Audio muxing is **out of scope** — that is OBJ-014's responsibility. This module produces a video-only MP4.
     8→
     9→## Interface Contract
    10→
    11→```typescript
    12→// src/engine/ffmpeg-encoder.ts
    13→
    14→/**
    15→ * Supported input pixel formats for frame data piped to FFmpeg.
    16→ * - 'png': Each frame is a complete PNG-encod... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-009 — Virtualized Clock and Puppeteer Bridge
     2→
     3→## Summary
     4→
     5→OBJ-009 delivers two modules that together implement the virtualized clock mechanism defined in C-03. First, `FrameClock` (`src/engine/frame-clock.ts`) — a pure, stateless utility that maps frame numbers to timestamps and provides an iterator for deterministic frame stepping. It has no scene awareness; per-scene normalized time is OBJ-036's responsibility. Second, `PuppeteerBridge` (`src/engine/puppeteer-bridge.ts`) — the Puppeteer lifecycle manager that launches headless Chromium, loads the OBJ-010 page shell, exposes an `evaluate()` primitive for downstream message protocols (OBJ-011), and captures rendered frames as PNG pixel buffers via Puppeteer's screenshot API. Together, these two modules provide the building blocks that OBJ-035 (orchestrator) composes into the deterministic render loop from seed Section 4.4.
     6→
     7→## Interface Contract
     8→
     9→### Mo... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "offset": 70,
  "limit": 60
}
[Tool Result]     70→
    71→  /**
    72→   * If true, forces single-threaded encoding (-threads 1) for byte-identical
    73→   * video stream output across runs. Container metadata (creation timestamps,
    74→   * encoder version strings) may still differ between runs. For C-05's
    75→   * "byte-identical or visually indistinguishable" requirement, the default
    76→   * multithreaded mode produces visually indistinguishable output, which
    77→   * satisfies the constraint. Default: false.
    78→   */
    79→  deterministic?: boolean;
    80→
    81→  /**
    82→   * Optional path to FFmpeg binary. If not provided, resolves via resolveFFmpegPath().
    83→   */
    84→  ffmpegPath?: string;
    85→}
    86→
    87→/**
    88→ * Result returned when encoding completes successfully.
    89→ */
    90→export interface FFmpegEncoderResult {
    91→  /** Absolute path to the output MP4 file. */
    92→  outputPath: string;
    93→
    94→  /** Total number of frames written. */
    95→  frameCo... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: OBJ-077 — End-to-End Integration Test Plan
     2→
     3→## Summary
     4→
     5→OBJ-077 delivers the **end-to-end integration test plan** for depthkit — concrete, step-by-step procedures for verifying SC-01 (60-second, 5-scene video renders to valid MP4), SC-03 (performance target met), SC-05 (n8n POST/poll/download works), and SC-06 (manifest validation soundness). This document IS the test plan: it contains executable procedures with literal CLI commands, exact `ffprobe` invocations, and unambiguous pass/fail thresholds. OBJ-078 executes these procedures.
     6→
     7→## Interface Contract
     8→
     9→OBJ-077 produces no code module. Its deliverable is this test plan document (`output.md`). The plan specifies test fixtures, procedures, and validation commands that OBJ-078 follows.
    10→
    11→---
    12→
    13→## Resolved Design Questions
    14→
    15→**Determinism Comparison Method:** Frame MD5 comparison as primary method. Extract per-frame ch... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/output.md",
  "offset": 150,
  "limit": 200
}
[Tool Result]    150→| V-17 | Scenes not in start_time order (warning expected) | 2 scenes, scene[0].start_time > scene[1].start_time; expect `SCENE_ORDER_MISMATCH` warning |
   151→| V-18 | Tunnel geometry (OBJ-019) | Full 5-slot tunnel |
   152→| V-19 | Canyon geometry (OBJ-020) with crane_up camera (OBJ-030) | Tests geometry/camera compatibility |
   153→| V-20 | 10 scenes, each 0.3s, cuts only | Stress test for scene count |
   154→
   155→**For each valid manifest:** Generate matching solid-color test images at the manifest's resolution. Where audio is needed, generate a sine tone of the required duration.
   156→
   157→### Fixture F-04a: SC-06 Invalid Manifest Corpus -- Validation Failures
   158→
   159→These fail at manifest validation (before any rendering). Testable via `depthkit validate`.
   160→
   161→| ID | Description | Expected Error |
   162→|----|-------------|----------------|
   163→| E-01 | Missing `version` field | Zod structural error |
   164→| E-02 | `version: "1.0"` (wron... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-077/output.md",
  "offset": 340,
  "limit": 120
}
[Tool Result]    340→#### SC01-03: Deterministic Output (C-05, TC-06)
   341→
   342→**Preconditions:** SC01-01 passed.
   343→
   344→**Steps:**
   345→1. Render the benchmark manifest a second time to a different output path:
   346→   ```bash
   347→   depthkit render fixtures/benchmark/manifest.json \
   348→     -o fixtures/benchmark/output_run2.mp4 \
   349→     --gpu software
   350→   ```
   351→2. Extract frame MD5 checksums from both renders:
   352→   ```bash
   353→   ffmpeg -i fixtures/benchmark/output.mp4 -f framemd5 - > fixtures/benchmark/run1.md5
   354→   ffmpeg -i fixtures/benchmark/output_run2.mp4 -f framemd5 - > fixtures/benchmark/run2.md5
   355→   ```
   356→3. Compare:
   357→   ```bash
   358→   diff fixtures/benchmark/run1.md5 fixtures/benchmark/run2.md5
   359→   ```
   360→4. If `diff` reports no differences: **pass** (byte-identical frames).
   361→5. If `diff` reports differences: compute PSNR:
   362→   ```bash
   363→   ffmpeg -i fixtures/benchmark/output.mp4 \
   364→... [truncated]
Good. I can see that OBJ-077 already has a determinism test (SC01-03) that uses framemd5 comparison with PSNR fallback. OBJ-073 needs to be the deeper, more comprehensive **verification plan** that covers the full seeding strategy and systematic identification of non-determinism sources. Let me also check OBJ-074 to understand how it relates:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-074/output.md",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-010 — Three.js Page Shell, Build/Bundle Architecture, and Scene Renderer Skeleton
     2→
     3→## Summary
     4→
     5→OBJ-010 establishes the browser-side rendering foundation and the authoritative Node.js/browser code-split architecture for depthkit. It delivers: (1) the final HTML page shell with a properly sized WebGL canvas, (2) the Three.js `Scene` / `PerspectiveCamera` / `WebGLRenderer` initialization skeleton that all downstream rendering depends on, (3) the architectural decision that the browser page is a **data-driven renderer** — a "dumb page" that receives computed scene state from the Node.js orchestrator and executes Three.js calls accordingly, and (4) a minimal `renderFrame()` primitive that downstream objectives build upon. This objective also defines Node-side TypeScript types for data crossing the Node/browser boundary (excluding geometry serialization, which is deferred to OBJ-011).
     6→
     7→## Interface Contract
     8→
     9→... [truncated]
Now I have enough context. Let me draft the specification for OBJ-073.

---

# Proposed Specification: OBJ-073 — Deterministic Output Verification Plan

## Summary

OBJ-073 delivers the **deterministic output verification plan** — a comprehensive procedure and supporting utility for verifying constraint C-05 (deterministic output) and testable claim TC-06 (virtualized clock produces deterministic output). This objective goes beyond OBJ-077's SC01-03 test (which is a single two-run comparison) by providing: (1) a systematic audit of all non-determinism sources in the depthkit pipeline, (2) a seeding strategy for any randomized elements, (3) a multi-layer checksum comparison methodology (per-frame pixel checksums, encoded stream checksums, and container-level analysis), (4) a reusable CLI sub-command (`depthkit verify-determinism`) that automates N-run comparison, and (5) concrete pass/fail thresholds with escalation procedures when non-determinism is detected.

## Interface Contract

### CLI Sub-Command: `depthkit verify-determinism`

```typescript
// Added to CLI (OBJ-046) as a new sub-command.
// This is the user-facing interface for running deterministic verification.

interface VerifyDeterminismOptions {
  /** Path to the manifest JSON file to test. */
  manifest: string;

  /** Number of render runs to compare. Default: 3. Minimum: 2. Maximum: 10. */
  runs?: number;

  /** Output directory for render artifacts and comparison reports. Default: './determinism-check'. */
  outputDir?: string;

  /** 
   * Comparison granularity level:
   * - 'frame-pixel': Per-frame raw pixel hash before encoding (gold standard).
   * - 'frame-encoded': Per-frame MD5 from encoded MP4 via ffmpeg framemd5.
   * - 'both': Runs both comparisons.
   * Default: 'both'.
   */
  level?: 'frame-pixel' | 'frame-encoded' | 'both';

  /** Force software rendering (--gpu software). Default: true. */
  softwareOnly?: boolean;

  /** 
   * Enable FFmpeg deterministic mode (single-threaded encoding).
   * Default: true. When true, passes `deterministic: true` to FFmpegEncoder.
   */
  deterministicEncoding?: boolean;

  /**
   * Path to assets directory for resolving manifest image paths.
   * Default: directory containing the manifest file.
   */
  assetsDir?: string;
}

interface VerifyDeterminismResult {
  /** Number of runs completed. */
  runsCompleted: number;

  /** Per-frame pixel hash comparison result (if level includes 'frame-pixel'). */
  pixelComparison?: FrameComparisonResult;

  /** Per-frame encoded MD5 comparison result (if level includes 'frame-encoded'). */
  encodedComparison?: FrameComparisonResult;

  /** Overall pass/fail. */
  passed: boolean;

  /** Human-readable summary. */
  summary: string;

  /** Path to the full report JSON. */
  reportPath: string;
}

interface FrameComparisonResult {
  /** Total frames per run. */
  totalFrames: number;

  /** Number of frames identical across all runs. */
  identicalFrames: number;

  /** Number of frames that differ across runs. */
  divergentFrames: number;

  /** 
   * For divergent frames: PSNR between the worst-case pair.
   * Only populated if divergentFrames > 0.
   */
  worstCasePsnrDb?: number;

  /** Frame indices that diverged (zero-indexed). */
  divergentFrameIndices: number[];

  /** Pass/fail for this comparison level. */
  passed: boolean;

  /**
   * Pass criteria applied:
   * - 'byte-identical': All frame hashes match (ideal).
   * - 'visually-indistinguishable': PSNR >= 60dB on all frames (acceptable).
   * - 'failed': PSNR < 60dB on at least one frame.
   */
  verdict: 'byte-identical' | 'visually-indistinguishable' | 'failed';
}
```

### Module: `src/engine/determinism.ts`

```typescript
/**
 * Utility module for deterministic rendering verification.
 * Used by the `verify-determinism` CLI command and available
 * for programmatic use in integration tests.
 */

/**
 * Captures a per-frame pixel hash during rendering by intercepting
 * the frame buffer before it is piped to FFmpeg. This is implemented
 * as an onProgress-adjacent hook: the orchestrator's frame capture
 * buffer is hashed (SHA-256) and recorded.
 *
 * NOT a modification to the Orchestrator — implemented as a wrapper
 * that uses the existing onProgress callback to track frame indices,
 * and a parallel hash computation on the frame buffers.
 */
export interface FrameHashCollector {
  /**
   * Collect frame pixel hashes from a single render run.
   * Wraps Orchestrator.render() and captures SHA-256 hashes of each
   * frame's raw pixel buffer (PNG data from FrameCapture).
   *
   * Implementation approach: Uses a custom capture strategy wrapper
   * that intercepts the buffer returned by FrameCapture.capture(),
   * computes SHA-256, stores it, and passes the buffer through to
   * FFmpeg unchanged.
   *
   * @param config - Standard OrchestratorConfig.
   * @returns Frame hashes in order, plus the OrchestratorResult.
   */
  collectHashes(config: OrchestratorConfig): Promise<FrameHashResult>;
}

export interface FrameHashResult {
  /** SHA-256 hex hashes, one per frame, in frame order. */
  hashes: string[];
  /** The standard orchestrator result. */
  renderResult: OrchestratorResult;
}

/**
 * Compares frame hashes across multiple runs.
 */
export function compareFrameHashes(
  runs: string[][]  // Array of runs, each run is an array of hex hashes
): FrameComparisonResult;

/**
 * Extracts per-frame MD5 checksums from an encoded MP4 using FFmpeg's
 * framemd5 muxer.
 *
 * Runs: ffmpeg -i <mp4Path> -f framemd5 -
 * Parses the output lines to extract hex MD5 per frame.
 */
export function extractFrameMd5s(
  mp4Path: string,
  ffmpegPath?: string
): Promise<string[]>;

/**
 * Computes per-frame PSNR between two MP4 files using FFmpeg's psnr filter.
 *
 * Runs: ffmpeg -i <path1> -i <path2> -lavfi psnr=stats_file=<tempFile> -f null -
 * Parses the stats file to extract per-frame psnr_avg values.
 *
 * @returns Array of PSNR values (dB) per frame. Infinity means identical.
 */
export function computePerFramePsnr(
  mp4Path1: string,
  mp4Path2: string,
  ffmpegPath?: string
): Promise<number[]>;

/**
 * Generates a determinism verification report.
 */
export function generateReport(
  runs: FrameHashResult[],
  encodedMd5s: string[][],
  psnrResults: number[][] | null,
  config: { manifestPath: string; runCount: number; softwareOnly: boolean; deterministicEncoding: boolean }
): VerifyDeterminismReport;

export interface VerifyDeterminismReport {
  /** ISO timestamp of when the verification was run. */
  timestamp: string;
  /** Manifest path used. */
  manifestPath: string;
  /** Number of runs. */
  runCount: number;
  /** Configuration used. */
  config: {
    softwareOnly: boolean;
    deterministicEncoding: boolean;
    captureStrategy: string;
  };
  /** Pixel-level comparison results. */
  pixelComparison: FrameComparisonResult;
  /** Encoded frame comparison results. */
  encodedComparison: FrameComparisonResult;
  /** Per-run render durations (ms). */
  renderDurationsMs: number[];
  /** Non-determinism sources identified (if any). */
  identifiedSources: NonDeterminismSource[];
  /** Overall verdict. */
  passed: boolean;
}

export interface NonDeterminismSource {
  /** Layer where non-determinism was detected. */
  layer: 'pixel-capture' | 'encoding' | 'container-metadata';
  /** Description of the source. */
  description: string;
  /** Severity: 'blocking' (violates C-05) or 'cosmetic' (metadata only). */
  severity: 'blocking' | 'cosmetic';
}
```

## Design Decisions

### D1: Non-Determinism Source Audit — The Layered Model

**Decision:** The verification plan treats the pipeline as four distinct layers, each of which can independently introduce non-determinism. The verification procedure tests each layer in isolation where possible.

| Layer | Component | Potential Non-Determinism Sources | Mitigation |
|-------|-----------|----------------------------------|------------|
| **L1: Scene State** | FrameClock, camera interpolation, easing functions | `Math.random()`, `Date.now()`, uninitialized variables | Audit: no `Math.random()` or `Date.now()` calls in the render path. All state is derived from frame number. |
| **L2: WebGL Rendering** | Three.js + Chromium's WebGL (SwiftShader in software mode) | GPU driver differences, floating-point rounding, texture upload order, async operations | Mitigate: software rendering (SwiftShader) is deterministic for same Chromium version on same architecture. Pin Chromium version via Puppeteer. |
| **L3: Frame Capture** | CDP `Page.captureScreenshot` or `canvas.toDataURL()` | PNG compression non-determinism, async capture timing | Mitigate: the virtualized clock (C-03) ensures each frame is fully rendered before capture. PNG compression is deterministic for same input pixels. |
| **L4: FFmpeg Encoding** | H.264 encoding, MP4 container | Multithreaded encoding race conditions, container creation timestamps, encoder version differences | Mitigate: `deterministic: true` on FFmpegEncoder (single-threaded). Container metadata (creation_time) will differ but is not part of the video stream. |

**Rationale:** Understanding *where* non-determinism can enter allows targeted verification. If pixel hashes match but encoded frame MD5s differ, the issue is in L4. If pixel hashes differ, the issue is in L1-L3. This layered approach makes root-cause analysis tractable.

### D2: Two-Tier Comparison Strategy

**Decision:** The verification runs two independent comparison methods:

1. **Frame-pixel hashes (L1-L3):** SHA-256 of raw PNG frame buffers captured by `FrameCapture`, computed before the buffer reaches FFmpeg. These hashes test whether the rendering + capture pipeline is deterministic, independent of the encoder.

2. **Encoded frame MD5s (L1-L4):** MD5 checksums extracted from the final MP4 via `ffmpeg -f framemd5`. These test whether the full pipeline including encoding is deterministic.

If frame-pixel hashes match across runs but encoded MD5s differ, the non-determinism is in FFmpeg encoding (L4) — resolvable by enabling `deterministic: true`. If frame-pixel hashes differ, the non-determinism is in the rendering pipeline itself — a more serious issue requiring investigation.

**Rationale:** The two-tier approach isolates encoding from rendering. C-05 says "byte-identical or visually indistinguishable" — the primary goal is byte-identical pixels, with PSNR as a fallback acceptance criterion.

### D3: SHA-256 for Pixel Hashes, MD5 for Encoded Frames

**Decision:** Use SHA-256 for raw pixel buffer hashes (our own computation) and MD5 for encoded frame comparison (because FFmpeg's `framemd5` muxer uses MD5 and we cannot change it).

**Rationale:** SHA-256 has zero collision risk at our scale. MD5 is forced by FFmpeg's tooling — it's fine for comparison purposes where both inputs are known.

### D4: Frame Hash Collection via Capture Interception

**Decision:** Frame pixel hashes are collected by wrapping the `FrameCapture` module's output. The `FrameHashCollector` does not modify the Orchestrator — it creates a thin wrapper around the frame buffer flow:

1. Orchestrator calls `capture.capture()` which returns the PNG buffer.
2. Before `encoder.writeFrame(buffer)`, the hash collector computes `SHA-256(buffer)` and stores it.
3. The buffer is passed to the encoder unchanged.

**Implementation approach:** The `FrameHashCollector` constructs the Orchestrator with a modified pipeline where frame buffers are intercepted. This can be done by:
- Subclassing or wrapping the capture module to add a hash side-effect.
- Or: having the collector perform the full orchestration itself, calling the same sub-components (PuppeteerBridge, FrameCapture, FFmpegEncoder) directly, inserting hash computation between capture and encode.

The second approach is preferred because it avoids modifying the Orchestrator's internals while still using the same deterministic pipeline.

**Rationale:** The Orchestrator is intentionally opaque (OBJ-035 D1). Rather than adding hooks to it, the collector wraps the same sub-components at the same abstraction level. This keeps OBJ-035 unchanged.

### D5: PSNR Threshold — 60 dB

**Decision:** When frame hashes differ, the fallback acceptance criterion is PSNR ≥ 60 dB on every frame between every pair of runs. This threshold is inherited from OBJ-077's SC01-03 procedure.

**Rationale:** 60 dB means peak signal-to-noise ratio is extremely high — differences are invisible to the human eye (typical "lossless" threshold is 40-50 dB). At 60 dB, the maximum per-pixel error is negligible (sub-pixel rounding). This aligns with C-05's "visually indistinguishable" fallback.

### D6: Seeding Strategy for Randomized Elements

**Decision:** The verification plan mandates a **code audit checklist** for randomized elements, not a runtime seeding mechanism. The depthkit render path should contain **zero** calls to `Math.random()`, `Date.now()`, `crypto.getRandomValues()`, or any non-deterministic function. The audit verifies this via static analysis (grep).

If any randomized element is discovered during the audit, the resolution is:
1. **Remove it** if it's unnecessary (preferred).
2. **Replace it** with a deterministic alternative derived from the frame number or a manifest-provided seed.
3. **Seed it** with a fixed seed derived from the manifest's content hash, only if removal/replacement is impossible.

**Seeding interface (if needed):**

```typescript
/**
 * Deterministic PRNG seeded from a manifest content hash.
 * Only used if a randomized element cannot be eliminated.
 * Uses a simple xorshift128 algorithm for reproducibility.
 */
export interface DeterministicRng {
  /** Returns a float in [0, 1) deterministically. */
  next(): number;
  /** Create from a seed string (e.g., JSON.stringify(manifest)). */
  static fromSeed(seed: string): DeterministicRng;
}
```

**Current assessment:** Based on the existing specs (OBJ-009, OBJ-010, OBJ-011, OBJ-013, OBJ-035), no component uses `Math.random()` or non-deterministic functions. The FrameClock is pure arithmetic. Camera interpolation is pure math on frame numbers. Three.js's `WebGLRenderer.render()` is deterministic for the same scene state and same WebGL implementation. The `DeterministicRng` is a contingency — it may never be needed.

**Rationale:** Seeding random number generators is a band-aid. The correct approach for a deterministic pipeline is to have no randomness. The audit proves this property; the seeding interface exists as a safety net.

### D7: Container Metadata Differences Are Cosmetic, Not Blocking

**Decision:** MP4 container metadata (creation timestamps, encoder version strings, UUID atoms) will differ between runs. These differences are explicitly classified as **cosmetic** (severity: `'cosmetic'` in `NonDeterminismSource`) and do not constitute a C-05 violation.

C-05 states "byte-identical or visually indistinguishable output." The visual output is the decoded video frames and audio stream, not container metadata. The verification plan compares decoded frame content, not raw file bytes.

**Rationale:** FFmpeg writes `creation_time` metadata from the system clock. Suppressing this requires non-standard FFmpeg flags that may vary across versions. Since C-05 is about visual output, container metadata differences are irrelevant.

### D8: Run Count — 3 by Default, Configurable up to 10

**Decision:** Default 3 runs (matching TC-06's requirement: "render same composition 3 times, compare checksums"). Maximum 10 to prevent accidental resource exhaustion. Minimum 2 (comparison requires at least two runs).

Comparison is all-pairs: for N runs, every pair of runs is compared. This catches intermittent non-determinism that might only manifest between specific pairs (e.g., if the first run initializes state differently from subsequent runs).

**Rationale:** 3 runs is the minimum for TC-06. All-pairs comparison (not just adjacent runs) catches first-run initialization effects.

### D9: Verification Report as JSON

**Decision:** The verification produces a JSON report (`determinism-report.json`) in the output directory, containing all comparison results, frame-by-frame hash tables, any divergent frame indices, PSNR values for divergent frames, and the overall pass/fail verdict. The CLI prints a human-readable summary to stdout and writes the full report to disk.

**Rationale:** JSON is machine-parseable for CI integration. The human-readable summary covers the common case. The full report supports debugging when non-determinism is found.

### D10: Relationship to OBJ-077's SC01-03

**Decision:** OBJ-073 is the **comprehensive verification plan**; OBJ-077's SC01-03 is a **quick check** that uses a subset of OBJ-073's methodology. Specifically:
- OBJ-077 SC01-03 does 2 runs, uses only encoded frame MD5s, and has a simple pass/fail.
- OBJ-073 does N runs (default 3), uses both pixel hashes and encoded MD5s, provides root-cause diagnosis, and produces a detailed report.

OBJ-077's SC01-03 procedure references the framemd5 + PSNR methodology that OBJ-073 formalizes. OBJ-078 (which executes OBJ-077's tests) may call `depthkit verify-determinism` as the implementation of SC01-03.

### D11: Software Rendering Required for Cross-Run Determinism

**Decision:** The verification procedure defaults to `softwareOnly: true` (SwiftShader). GPU-accelerated WebGL is **not guaranteed** to produce identical output across runs due to GPU driver scheduling non-determinism and parallel execution order. The `verify-determinism` command warns if `softwareOnly: false` is used and frame-pixel hashes diverge.

**Rationale:** C-11 requires software rendering as baseline. SwiftShader is single-threaded and deterministic for same inputs on same architecture. GPU rendering may be faster but sacrifices the byte-identical guarantee.

## Acceptance Criteria

### Code Audit

- [ ] **AC-01:** A static analysis grep of all source files in `src/` confirms zero occurrences of `Math.random()` in the rendering path (files under `src/engine/`, `src/page/`, `src/scenes/`, `src/camera/`). Test utility files and non-render-path code are excluded from this constraint.
- [ ] **AC-02:** A static analysis grep confirms zero occurrences of `Date.now()` or `new Date()` in the rendering path, except in diagnostic/logging code that does not affect output.
- [ ] **AC-03:** A static analysis grep confirms zero occurrences of `crypto.getRandomValues()` or `crypto.randomUUID()` in the rendering path.

### Frame-Pixel Determinism

- [ ] **AC-04:** Rendering the same single-scene manifest (stage geometry, static camera, 1 plane, 10 frames at 320×240) 3 times with software WebGL produces byte-identical SHA-256 pixel hashes for all 10 frames across all 3 runs. Zero divergent frames.
- [ ] **AC-05:** Rendering the same multi-scene manifest (2 scenes with crossfade transition, 20 frames at 320×240) 3 times with software WebGL produces byte-identical SHA-256 pixel hashes for all 20 frames across all 3 runs.
- [ ] **AC-06:** Rendering the same manifest with `deterministicEncoding: true` produces byte-identical per-frame MD5 checksums (via `ffmpeg -f framemd5`) across all runs.

### CLI Command

- [ ] **AC-07:** `depthkit verify-determinism <manifest.json>` with default options renders the manifest 3 times, compares pixel hashes and encoded MD5s, prints a human-readable summary to stdout, and writes `determinism-report.json` to the output directory.
- [ ] **AC-08:** The command exits with code 0 if the verification passes and code 1 if it fails.
- [ ] **AC-09:** `--runs 5` renders 5 times and compares all pairs (10 comparisons).
- [ ] **AC-10:** `--runs 1` is rejected with an error message ("minimum 2 runs required").
- [ ] **AC-11:** `--level frame-pixel` skips encoded MD5 comparison and only computes pixel hashes.

### Report

- [ ] **AC-12:** The JSON report contains: `timestamp`, `manifestPath`, `runCount`, `config`, `pixelComparison`, `encodedComparison`, `renderDurationsMs`, `identifiedSources`, `passed`.
- [ ] **AC-13:** When non-determinism is detected at the encoding layer only (pixel hashes match, encoded MD5s differ), the report's `identifiedSources` includes an entry with `layer: 'encoding'` and `severity: 'cosmetic'` if only metadata differs, or `severity: 'blocking'` if frame content differs.
- [ ] **AC-14:** When pixel-level non-determinism is detected, the report's `identifiedSources` includes an entry with `layer: 'pixel-capture'` and `severity: 'blocking'`, and the `divergentFrameIndices` lists the affected frames.

### Seeding (Contingency)

- [ ] **AC-15:** If the code audit (AC-01 through AC-03) finds randomized elements in the render path, a `DeterministicRng` seeded from the manifest content hash replaces them. After replacement, AC-04 through AC-06 pass.
- [ ] **AC-16:** If no randomized elements are found (expected outcome), the `DeterministicRng` module exists but is unused in the rendering pipeline. The audit result is documented in the verification report.

### PSNR Fallback

- [ ] **AC-17:** When frame-pixel hashes diverge but PSNR ≥ 60 dB on all divergent frames, the verdict is `'visually-indistinguishable'` and the overall result is `passed: true`.
- [ ] **AC-18:** When any frame has PSNR < 60 dB, the verdict is `'failed'` and the overall result is `passed: false`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Manifest references missing images | First render fails with `SCENE_SETUP_FAILED`. The verification command reports the error and exits with code 1 without attempting further runs. |
| One of N runs fails mid-render (e.g., FFmpeg crashes) | The failed run is logged. If fewer than 2 runs completed, exit with code 1 and report "insufficient runs for comparison." If 2+ runs completed, compare available runs and note the failed run in the report. |
| Manifest has zero frames (e.g., 0-duration scene) | Manifest validation rejects it (OBJ-016). Verification command reports validation error and exits. |
| Two runs produce different frame counts | This is a critical non-determinism failure. Report immediately as `severity: 'blocking'`, `layer: 'pixel-capture'`, with description "Frame count mismatch: run 1 produced N frames, run 2 produced M frames." `passed: false`. |
| Output directory already exists with previous report | Overwrite previous report. Render output files are named with run index (`run_1.mp4`, `run_2.mp4`, etc.). |
| Disk runs out of space during multi-run verification | The render fails. Partial runs are cleaned up. Report what completed. Exit with code 1. |
| `--level frame-pixel` but no way to intercept pixel buffers | Falls back to encoded MD5 comparison only with a warning. This should not happen if the module is implemented correctly but is a graceful degradation path. |
| Same manifest rendered on two different machines | NOT in scope. C-05 specifies "same hardware." Cross-machine determinism is not guaranteed due to CPU architecture, SSE/AVX differences, and Chromium version differences. The verification plan explicitly documents this exclusion. |
| Container metadata (creation_time) differs between runs | Classified as cosmetic. Does not affect pass/fail. Noted in report under `identifiedSources` with `severity: 'cosmetic'`. |

## Test Strategy

### Unit Tests: `test/unit/determinism.test.ts`

1. **compareFrameHashes — all identical:** 3 runs with identical hash arrays → `{ passed: true, verdict: 'byte-identical', divergentFrames: 0 }`.
2. **compareFrameHashes — one frame differs:** 3 runs, frame 5 differs in run 2 → `{ passed: false, divergentFrames: 1, divergentFrameIndices: [5] }`. (Pass/fail determined after PSNR check.)
3. **compareFrameHashes — frame count mismatch:** Runs with different hash array lengths → throws or returns a distinct error result.
4. **compareFrameHashes — 2 runs (minimum):** Works correctly with exactly 2 runs.
5. **extractFrameMd5s — parse FFmpeg output:** Given mock FFmpeg framemd5 output, parses correct number of MD5 hex strings.
6. **computePerFramePsnr — parse stats file:** Given a mock PSNR stats file, returns correct dB values per frame.
7. **generateReport — happy path:** Given matching results across runs, produces a valid report with `passed: true`.
8. **generateReport — non-determinism detected:** Given divergent hashes and PSNR < 60dB, produces a report with `passed: false` and correct `identifiedSources`.

### Integration Tests: `test/integration/determinism.test.ts`

9. **End-to-end pixel determinism:** Render a minimal manifest (1 scene, 1 plane, 5 frames, 320×240, software WebGL) 3 times via `FrameHashCollector`. Assert all pixel hashes identical across runs.
10. **End-to-end encoded determinism:** Same manifest, 3 runs with `deterministic: true` on encoder. Extract framemd5 from each output. Assert all match.
11. **Static analysis audit:** Run grep against `src/` for `Math.random`, `Date.now`, `new Date`, `crypto.getRandomValues`. Assert zero matches in render-path files (use file path allowlist/denylist).

### CLI Tests: `test/integration/cli-determinism.test.ts`

12. **CLI happy path:** Run `depthkit verify-determinism` on a smoke manifest. Assert exit code 0, report file exists, report JSON is valid.
13. **CLI with failed determinism:** (Difficult to trigger naturally — may require a mock that introduces intentional non-determinism.) Assert exit code 1.
14. **CLI with --runs 1:** Assert exit code 1 with error about minimum runs.

### Relevant Testable Claims

- **TC-06:** Tests 9 and 10 directly verify this claim: "render same composition 3 times, compare checksums."
- **C-05:** The entire objective validates C-05.
- **C-03:** Deterministic output is a consequence of the virtualized clock. If TC-06 passes, it provides evidence for C-03 correctness.

## Integration Points

### Depends on

| Dependency | What OBJ-073 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class and `OrchestratorConfig` for performing render runs. `OrchestratorResult` for collecting render durations and capture stats. Sub-components (PuppeteerBridge, FrameCapture, FFmpegEncoder) are accessed indirectly — the `FrameHashCollector` may compose them directly for pixel hash interception. |

### Consumed by

| Downstream | How it uses OBJ-073 |
|---|---|
| **OBJ-077** (End-to-end test plan) | SC01-03 references the determinism verification methodology. OBJ-078 may call `depthkit verify-determinism` to execute SC01-03. |
| **OBJ-046** (CLI) | Registers the `verify-determinism` sub-command. |
| **CI/CD pipelines** | Can run `depthkit verify-determinism` as a regression gate. |

### File Placement

```
depthkit/
  src/
    engine/
      determinism.ts            # NEW — FrameHashCollector, compareFrameHashes,
                                #       extractFrameMd5s, computePerFramePsnr,
                                #       generateReport, DeterministicRng
    cli/
      commands/
        verify-determinism.ts   # NEW — CLI sub-command implementation
  test/
    unit/
      determinism.test.ts       # NEW — unit tests for comparison/report logic
    integration/
      determinism.test.ts       # NEW — end-to-end determinism verification
      cli-determinism.test.ts   # NEW — CLI command tests
```

## Non-Determinism Audit Checklist

This checklist must be executed as part of the implementation and its results documented in the verification report. It is a static analysis procedure, not a runtime check.

### Rendering Path Files to Audit

All files under these directories are in the rendering path:
- `src/engine/` — orchestrator, frame-clock, puppeteer-bridge, frame-capture, ffmpeg-encoder, audio-muxer
- `src/page/` — scene-renderer, geometry-library, message-handler
- `src/scenes/` — all geometry definitions
- `src/camera/` — all camera path presets and interpolation utilities

### Prohibited Patterns

| Pattern | Grep Command | Allowed Exceptions |
|---|---|---|
| `Math.random` | `grep -rn "Math\.random" src/engine/ src/page/ src/scenes/ src/camera/` | None in render path. Test files excluded. |
| `Date.now()` | `grep -rn "Date\.now\(\)" src/engine/ src/page/ src/scenes/ src/camera/` | Timing/diagnostics that write to logs only and do not affect pixel output (e.g., `elapsedMs` in `RenderProgress`). |
| `new Date()` | `grep -rn "new Date()" src/engine/ src/page/ src/scenes/ src/camera/` | Same as above — logging/diagnostics only. |
| `crypto.getRandomValues` | `grep -rn "crypto\.getRandomValues\|crypto\.randomUUID" src/engine/ src/page/ src/scenes/ src/camera/` | None. |
| `performance.now()` | `grep -rn "performance\.now()" src/page/` | Diagnostics only, not used for timing render state. |
| `requestAnimationFrame` | `grep -rn "requestAnimationFrame" src/page/` | None in production render path (AP-02). Preview mode only. |

### Three.js-Specific Concerns

| Concern | Verification |
|---|---|
| Texture upload order | Three.js loads textures synchronously when passed as pre-loaded `Image` objects. Verify that `setupScene` loads all textures before any render call. Confirmed by OBJ-011 spec: scene setup waits for all texture loads before returning `success: true`. |
| Shader compilation caching | Chromium's shader cache may cause first-frame timing differences but not pixel differences, since the virtualized clock waits for render completion. Not a determinism concern. |
| Floating-point consistency | SwiftShader (software WebGL) uses IEEE 754 on the CPU — deterministic for same architecture. GPU rendering may vary. This is why `softwareOnly: true` is the default. |
| `renderer.autoClear` | Must be consistent across runs. Verified by OBJ-010 spec: renderer is configured once during `init()`. |

## Open Questions

### OQ-A: Should the FrameHashCollector bypass the Orchestrator entirely?

The collector needs to intercept pixel buffers between capture and encoding. Two approaches:
1. Compose the same sub-components (PuppeteerBridge, FrameCapture, FFmpegEncoder) directly, replicating the orchestrator's loop with hash insertion.
2. Extend the Orchestrator with an optional `onFrameBuffer?: (frame: number, buffer: Buffer) => void` callback.

Approach 1 avoids modifying OBJ-035 but risks drift if the orchestrator's loop logic changes. Approach 2 is cleaner but adds an interface to OBJ-035 that exists solely for testing. Recommendation: Approach 2 — a simple callback is low-impact and useful for other diagnostics. The implementer should decide based on practical complexity.

### OQ-B: Should cross-GPU-vs-software comparison be in scope?

Verifying that GPU-rendered output matches software-rendered output is a stronger guarantee than C-05 requires. C-05 says "same manifest + same images + same audio" — it does not specify "across different rendering backends." This is deferred but the report format supports it (you could add `layer: 'gpu-vs-software'`).

### OQ-C: Should the verification plan cover audio determinism?

Audio is muxed by OBJ-014 as a passthrough (`-c:a copy` or re-encode). The audio file itself is an input, not generated by the pipeline. Audio muxing should produce identical audio streams if the input file is identical. The verification plan currently focuses on video frames. Audio stream comparison (e.g., extracting audio MD5) could be added but is low priority.

---

I believe this covers the full scope of OBJ-073. The spec provides:
- A systematic non-determinism source audit (the layered model)
- A seeding strategy (audit-first, seed-as-contingency)
- A multi-layer checksum methodology (pixel hashes + encoded MD5s)
- A reusable CLI command and programmatic API
- Clear pass/fail thresholds (byte-identical preferred, PSNR ≥ 60dB acceptable)
- Integration with OBJ-077's SC01-03

I'd like the challenger to review whether the scope, interface design, and the relationship to OBJ-077 are well-calibrated. Does this specification provide enough precision for an implementer to build from?

---

## Round 2 — spec_challenger

I've reviewed the proposed spec carefully. There's solid thinking here — the layered non-determinism model (D1), the two-tier comparison strategy (D2), and the code audit checklist are well-conceived. But there are several issues that would force an implementer to guess. Let me enumerate them.

---

## Issues

### 1. CRITICAL: FrameHashCollector intercept mechanism is self-contradictory

D4 says the "second approach is preferred" — composing sub-components (PuppeteerBridge, FrameCapture, FFmpegEncoder) directly, replicating the orchestrator's loop with hash insertion. But then OQ-A reverses course and recommends Approach 2 — extending the Orchestrator with an `onFrameBuffer` callback. These are opposite decisions.

Worse: Approach 1 (reimplementing the orchestrator loop) means reimplementing scene iteration, transition handling, lazy setup/teardown, gap frame rendering, camera state computation — essentially all of OBJ-035's private logic. That's a maintenance nightmare and will drift from OBJ-035 immediately.

Approach 2 (adding a callback to OBJ-035) is architecturally clean but modifies OBJ-035's interface, which this spec cannot unilaterally do.

**Proposed fix:** Drop the `FrameHashCollector` abstraction entirely. Instead, specify that the `verify-determinism` procedure uses **only post-hoc comparison** — it renders N times to N output MP4s, then compares them using `extractFrameMd5s` and `computePerFramePsnr`. This matches exactly what OBJ-077's SC01-03 already does, just automated and extended. The "pixel hash before encoding" tier (L1-L3 isolation) is a nice-to-have diagnostic, but it requires either modifying OBJ-035 or reimplementing it. Defer pixel-hash interception to OQ-A. The encoded-frame comparison via `framemd5` already isolates video content from container metadata, so it satisfies the C-05 check.

If you keep the pixel-hash tier, you must commit to one approach and specify it precisely — including which OBJ-035 sub-components are used, how transitions/gaps are handled, and a clear acknowledgment that this creates a maintenance coupling with OBJ-035's internals.

**Severity:** Critical — AC-04 and AC-05 are untestable without resolving this.

### 2. MAJOR: CLI sub-command creates an undeclared dependency on OBJ-046

OBJ-073 depends only on OBJ-035 per the progress map. But the spec delivers a CLI sub-command (`depthkit verify-determinism`) that must be registered in the CLI entry point (OBJ-046). OBJ-046 is listed under "Consumed by" — meaning OBJ-046 would consume OBJ-073, not the other way around.

But OBJ-046 is already `status: "verified"`. You can't add a sub-command to a verified objective without a change proposal. And if OBJ-073 delivers the command implementation in `src/cli/commands/verify-determinism.ts`, who wires it into the CLI? OBJ-073 can't modify OBJ-046's code.

**Proposed fix:** Either:
- (A) Declare that OBJ-073 delivers the `determinism.ts` module and the verification *procedure* (as a document), and that the CLI sub-command is deferred to a follow-up objective or OBJ-083 (extended CLI, which is `status: "open"`). The integration tests call the module programmatically.
- (B) Add OBJ-046 as a dependency and specify exactly how the sub-command is registered — but this requires acknowledging a change to a verified spec.

I recommend (A). The core value of OBJ-073 is the verification plan and utility module, not the CLI wrapper.

**Severity:** Major — file placement and integration are broken as written.

### 3. MAJOR: AC-04/AC-05 vs AC-17 — contradictory pass criteria

AC-04: "byte-identical SHA-256 pixel hashes for all 10 frames across all 3 runs. **Zero divergent frames.**"

AC-17: "When frame-pixel hashes diverge but PSNR ≥ 60 dB... the overall result is `passed: true`."

These contradict. Is byte-identical required or not? C-05 says "byte-identical **or** visually indistinguishable" — so the correct reading is: byte-identical is the goal, PSNR ≥ 60dB is acceptable. But then AC-04 should be "expects byte-identical, and if not, falls through to AC-17." The acceptance criteria as written create two incompatible pass/fail definitions.

**Proposed fix:** Restructure the ACs:
- AC-04: "Rendering the same manifest 3 times... produces byte-identical pixel hashes OR, if hashes diverge, all divergent frames have PSNR ≥ 60dB." Remove the "Zero divergent frames" absolute.
- Add a new AC: "When byte-identical pixel hashes are achieved, the verdict is `'byte-identical'`. When hashes diverge but PSNR ≥ 60dB, verdict is `'visually-indistinguishable'`. Both are passing."

Alternatively, keep AC-04 as the strict expectation (byte-identical is expected for software WebGL on same hardware) and AC-17 as the documented fallback. But then AC-04 should say "expected to produce byte-identical hashes; if not, see AC-17 for fallback criteria."

**Severity:** Major — an implementer doesn't know whether to fail or pass a test.

### 4. MAJOR: `DeterministicRng` interface has a TypeScript error

```typescript
export interface DeterministicRng {
  next(): number;
  static fromSeed(seed: string): DeterministicRng;  // ← interfaces can't have static methods
}
```

TypeScript interfaces cannot define static methods. This needs to be a class declaration or a separate factory function.

**Proposed fix:**
```typescript
export class DeterministicRng {
  next(): number;
  static fromSeed(seed: string): DeterministicRng;
}
```
Or split into interface + factory:
```typescript
export interface DeterministicRng { next(): number; }
export function createDeterministicRng(seed: string): DeterministicRng;
```

**Severity:** Major — an implementer can't compile this.

### 5. MINOR: File placement assumes CLI directory structure that may not exist

The spec places files at `src/cli/commands/verify-determinism.ts`. The seed's Section 4.5 shows `src/cli.ts` as a flat file, not a `cli/commands/` directory. OBJ-046 may have established a different structure, but since this spec doesn't depend on OBJ-046, it's guessing.

**Proposed fix:** If you keep the CLI command (per issue #2), either read OBJ-046's output to confirm the directory structure, or simply place the command logic inside `src/engine/determinism.ts` as an exported function that a CLI command can call — leaving the CLI wiring to whoever integrates it.

### 6. MINOR: Edge case "One of N runs fails" — comparison function doesn't handle partial runs

The edge case table says "If 2+ runs completed, compare available runs." But `compareFrameHashes(runs: string[][])` takes an array and compares all pairs. Does it handle 2 out of 3 requested runs? The spec should clarify that the caller filters to completed runs before calling the comparison function.

**Proposed fix:** Add a note: "The caller is responsible for passing only completed runs to `compareFrameHashes()`. The function requires `runs.length >= 2` and throws if fewer are provided."

### 7. MINOR: `softwareOnly: true` mapping to `gpu: false` is implicit

OBJ-035's config uses `gpu?: boolean` (default `false`). The verification CLI uses `softwareOnly?: boolean` (default `true`). These are semantic inverses. The mapping should be documented explicitly.

**Proposed fix:** Add a note in the CLI interface: "`softwareOnly: true` maps to `OrchestratorConfig.gpu = false`; `softwareOnly: false` maps to `gpu = true`."

---

## What's Sound

- **D1 (Layered non-determinism model):** Excellent. The four-layer taxonomy makes root-cause analysis tractable.
- **D3 (SHA-256 vs MD5):** Correct reasoning on FFmpeg's tooling constraint.
- **D5 (60dB PSNR threshold):** Aligned with OBJ-077 and well-justified.
- **D6 (Seeding strategy as audit-first):** Exactly right. The render path should have zero randomness; seeding is a contingency.
- **D7 (Container metadata is cosmetic):** Correct. C-05 is about visual output.
- **D10 (Relationship to OBJ-077):** Clear delineation.
- **D11 (Software rendering for determinism):** Correct — GPU scheduling is a known non-determinism source.
- **Non-determinism audit checklist:** Comprehensive and actionable. The grep commands and Three.js-specific concerns are well-specified.
- **Edge case table:** Thorough, especially the "different frame counts = critical failure" case.

---

## Summary

Three issues need resolution before convergence:

1. **Critical:** Resolve the FrameHashCollector mechanism or drop it in favor of post-hoc comparison only.
2. **Major:** Resolve the CLI sub-command dependency on OBJ-046 (recommend deferring CLI to another objective).
3. **Major:** Resolve the contradictory pass criteria between AC-04/AC-05 and AC-17.
4. **Major:** Fix the TypeScript interface error on `DeterministicRng`.

Please revise and I'll verify.

---

## Round 3 — spec_author

All seven issues are valid. Here's the revised spec with each addressed:

---

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
   * Enable FFmpeg deterministic mode (single-threaded encoding) on each run.
   * When true, the factory-produced configs should set deterministic: true
   * on the FFmpegEncoder. This config flag is advisory — it's the caller's
   * responsibility to set it in createConfig. The verification module
   * records this value in the report for documentation purposes.
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

  /** Number of runs completed. */
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

  /** Per-run render durations (ms). Indexed by run. */
  renderDurationsMs: number[];

  /** Per-run output file paths. */
  outputPaths: string[];

  /** Non-determinism sources identified (if any). */
  identifiedSources: NonDeterminismSource[];

  /** Overall pass/fail. True if verdict is 'byte-identical' or 'visually-indistinguishable'. */
  passed: boolean;

  /** Human-readable summary string. */
  summary: string;
}

export type VerifyDeterminismError =
  | 'INVALID_RUN_COUNT'     // runs < 2 or > 10
  | 'ALL_RUNS_FAILED'       // no successful runs
  | 'INSUFFICIENT_RUNS'     // fewer than 2 successful runs
  | 'FRAME_COUNT_MISMATCH'  // runs produced different frame counts
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
 * 1. Validate run count (2-10).
 * 2. For each run i in [0, runs):
 *    a. Call createConfig(i) to get an OrchestratorConfig.
 *    b. Create a new Orchestrator(config).
 *    c. Call orchestrator.render().
 *    d. Store the OrchestratorResult and output path.
 *    e. If render fails: log the error, mark run as failed, continue.
 *    f. Call onRunComplete if provided.
 * 3. If fewer than 2 runs succeeded: throw DeterminismError('INSUFFICIENT_RUNS').
 * 4. Verify all successful runs produced the same frame count.
 *    If not: throw DeterminismError('FRAME_COUNT_MISMATCH').
 * 5. Extract per-frame MD5 checksums from each output MP4 via extractFrameMd5s().
 * 6. Compare MD5s across all pairs of successful runs via compareFrameMd5s().
 * 7. If any frames diverge: compute per-frame PSNR between divergent pairs
 *    via computePerFramePsnr(). Determine worst-case PSNR.
 * 8. Build FrameComparisonResult with verdict.
 * 9. Classify non-determinism sources into identifiedSources.
 * 10. Write VerifyDeterminismReport to reportDir/determinism-report.json.
 * 11. Return the report.
 *
 * @throws DeterminismError on procedural failures (not render failures).
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
 * Extracts the md5 field from each line.
 *
 * @returns Array of lowercase hex MD5 strings, one per frame, in decode order.
 * @throws DeterminismError('FFMPEG_ANALYSIS_FAILED') if FFmpeg exits non-zero.
 */
export function extractFrameMd5s(
  mp4Path: string,
  ffmpegPath?: string
): Promise<string[]>;

/**
 * Compares frame MD5 arrays across multiple runs (all-pairs comparison).
 *
 * Precondition: all arrays in `runs` must have the same length.
 * Throws DeterminismError('FRAME_COUNT_MISMATCH') if lengths differ.
 *
 * @param runs - Array of runs; each run is an array of MD5 hex strings.
 *               Minimum 2 runs. Caller is responsible for filtering
 *               to only completed runs before calling.
 * @returns FrameComparisonResult (without PSNR — worstCasePsnrDb is undefined).
 */
export function compareFrameMd5s(
  runs: string[][]
): FrameComparisonResult;

/**
 * Computes per-frame PSNR between two MP4 files using FFmpeg's psnr filter.
 *
 * Command: ffmpeg -i <path1> -i <path2> -lavfi psnr=stats_file=<tmpFile> -f null -
 *
 * Parses the stats file. Each line has: n:<frame> ... psnr_avg:<value> ...
 * Extracts psnr_avg per frame.
 *
 * @returns Array of PSNR values (dB) per frame. `Infinity` for identical frames.
 * @throws DeterminismError('FFMPEG_ANALYSIS_FAILED') if FFmpeg exits non-zero.
 */
export function computePerFramePsnr(
  mp4Path1: string,
  mp4Path2: string,
  ffmpegPath?: string
): Promise<number[]>;

/**
 * Generates the human-readable summary string for a report.
 */
export function formatSummary(report: VerifyDeterminismReport): string;

// ────────────────────────────────────────────
// Seeding (Contingency — may never be needed)
// ────────────────────────────────────────────

/**
 * Deterministic PRNG for use if the code audit (D6) discovers
 * randomized elements in the rendering path that cannot be eliminated.
 *
 * Uses xorshift128 for reproducibility. Seeded from a string
 * (e.g., a manifest content hash).
 *
 * If the audit finds no randomized elements (expected outcome),
 * this class exists but is unused in the rendering pipeline.
 */
export class DeterministicRng {
  /** Create from a seed string. Hashes the string to derive internal state. */
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

The procedure is: render N times → extract per-frame MD5 from each MP4 via `ffmpeg -f framemd5` → compare → compute PSNR if divergent.

Pre-encoding pixel hash interception (comparing raw PNG buffers before FFmpeg) is deferred to OQ-A. It would require either modifying OBJ-035's interface (adding a frame buffer callback) or reimplementing the orchestrator's render loop — both are out of scope for OBJ-073.

**Rationale:** OBJ-035 D1 mandates a single `render()` method with no exposed sub-components. Adding a `onFrameBuffer` callback would modify a verified spec. Reimplementing the loop would create maintenance coupling. Post-hoc comparison via `framemd5` is sufficient: it decodes the H.264 stream and checksums each decoded frame, which tests the full L1-L4 pipeline. When combined with `deterministic: true` encoding (single-threaded), any non-determinism in L1-L3 propagates to the decoded frames and is detected.

**Diagnostic gap:** If encoded MD5s differ, we cannot directly distinguish L1-L3 (rendering) from L4 (encoding) non-determinism. The report notes this limitation. A two-run comparison — one with `deterministic: true` and one without — can isolate L4 issues: if deterministic encoding makes the divergence disappear, the source was L4.

### D3: MD5 for Frame Comparison (FFmpeg-Driven)

**Decision:** Use MD5 checksums from FFmpeg's `framemd5` muxer as the primary comparison method. FFmpeg's muxer is authoritative and uses MD5 — we use what it provides.

**Rationale:** `framemd5` decodes the video stream and checksums each decoded frame's raw pixel data. This is the decoded pixel content, not the encoded bitstream. Two H.264 streams that decode to identical pixels will produce identical framemd5 output even if the encoded bytes differ (e.g., due to different NAL unit packaging). This makes framemd5 the right tool for C-05 verification.

### D4: PSNR Threshold — 60 dB

**Decision:** When frame MD5s differ, the fallback acceptance criterion is PSNR ≥ 60 dB on every divergent frame across every pair of runs. Inherited from OBJ-077's SC01-03.

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

**Decision:** If a render run fails (Orchestrator throws), the failure is logged and that run is skipped. If fewer than 2 runs succeed, `verifyDeterminism()` throws `DeterminismError('INSUFFICIENT_RUNS')`. If 2+ runs succeed, comparison proceeds on successful runs only. Failed runs are noted in the report (`runsCompleted < runsRequested`).

The lower-level `compareFrameMd5s(runs)` requires `runs.length >= 2` and throws `DeterminismError('FRAME_COUNT_MISMATCH')` if any array has a different length from the others. The caller (`verifyDeterminism`) is responsible for filtering to completed runs before calling comparison functions.

## Acceptance Criteria

### Code Audit

- [ ] **AC-01:** A grep of all source files under `src/engine/`, `src/page/`, `src/scenes/`, `src/camera/` confirms zero occurrences of `Math.random()` in the rendering path. Test utility files and non-render-path code (e.g., `src/engine/determinism.ts` itself) are excluded.
- [ ] **AC-02:** A grep confirms zero occurrences of `Date.now()` or `new Date()` in the rendering path, except in diagnostic/logging code that does not affect rendered pixel output (e.g., `elapsedMs` in `RenderProgress`).
- [ ] **AC-03:** A grep confirms zero occurrences of `crypto.getRandomValues()` or `crypto.randomUUID()` in the rendering path.

### Determinism Verification

- [ ] **AC-04:** Rendering the same single-scene manifest (stage geometry, static camera, 1 plane, 10 frames at 320×240) 3 times with software WebGL and `deterministic: true` encoding produces byte-identical per-frame MD5 checksums (via `extractFrameMd5s`). Verdict: `'byte-identical'`.
- [ ] **AC-05:** Rendering the same multi-scene manifest (2 scenes with crossfade transition, 20 frames at 320×240) 3 times with software WebGL and `deterministic: true` encoding produces byte-identical per-frame MD5 checksums. Verdict: `'byte-identical'`.
- [ ] **AC-06:** If frame MD5s diverge on any frame but PSNR ≥ 60 dB on all divergent frames, the verdict is `'visually-indistinguishable'` and `report.passed` is `true`.
- [ ] **AC-07:** If any divergent frame has PSNR < 60 dB, the verdict is `'failed'` and `report.passed` is `false`.

**Note on AC-04/AC-05:** Byte-identical MD5s are the **expected** outcome for software WebGL + deterministic encoding on the same hardware. AC-06 and AC-07 define the fallback acceptance logic if byte-identical is not achieved. Both `'byte-identical'` and `'visually-indistinguishable'` satisfy C-05.

### Module API

- [ ] **AC-08:** `verifyDeterminism()` with default config (3 runs) calls the config factory 3 times, renders 3 MP4s, extracts frame MD5s from each, compares all 3 pairs, and returns a `VerifyDeterminismReport` with `passed: true` for a deterministic manifest.
- [ ] **AC-09:** `verifyDeterminism()` with `runs: 1` throws `RangeError` synchronously. No renders are attempted.
- [ ] **AC-10:** `verifyDeterminism()` writes `determinism-report.json` to `reportDir`.
- [ ] **AC-11:** When one of 3 runs fails, `verifyDeterminism()` compares the 2 successful runs and returns a report with `runsCompleted: 2`, `runsRequested: 3`.
- [ ] **AC-12:** When all runs fail, `verifyDeterminism()` throws `DeterminismError('ALL_RUNS_FAILED')`.
- [ ] **AC-13:** When 2 successful runs produce different frame counts, `verifyDeterminism()` throws `DeterminismError('FRAME_COUNT_MISMATCH')`.

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
- [ ] **AC-22:** When MD5s match, `identifiedSources` is empty and `summary` includes "All frames byte-identical across N runs."
- [ ] **AC-23:** When MD5s diverge, `identifiedSources` includes at least one entry identifying the layer and severity.

### Seeding (Contingency)

- [ ] **AC-24:** If the code audit (AC-01–AC-03) discovers randomized elements in the render path, a `DeterministicRng` seeded from the manifest content hash replaces them, and AC-04/AC-05 pass afterward.
- [ ] **AC-25:** If no randomized elements are found (expected outcome), the audit result is documented in the verification report. `DeterministicRng` exists as an exported class but is unused in the rendering pipeline.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `runs` = 0, 1, 11, -1 | `RangeError` thrown synchronously. No renders attempted. |
| `createConfig` returns configs with different manifests | Undefined behavior (documented). Comparison may produce divergent frames that are expected differences, not non-determinism. The caller is responsible for config equivalence. |
| First render succeeds, second fails, third succeeds | Two successful runs compared. Report shows `runsCompleted: 2`, `runsRequested: 3`. |
| All renders fail | `DeterminismError('ALL_RUNS_FAILED')`. No report written. |
| Two successful runs produce different frame counts | `DeterminismError('FRAME_COUNT_MISMATCH')` with both counts in the error message. This is a critical non-determinism failure. |
| FFmpeg not found for `extractFrameMd5s` | `DeterminismError('FFMPEG_ANALYSIS_FAILED')` with cause. |
| FFmpeg `framemd5` output has unexpected format | `DeterminismError('FFMPEG_ANALYSIS_FAILED')` with descriptive message about parse failure. |
| Output directory for report doesn't exist | `fs.mkdirSync(reportDir, { recursive: true })` before writing. |
| Report file already exists | Overwritten. |
| `compareFrameMd5s` called with 0 or 1 runs | Throws `DeterminismError('INSUFFICIENT_RUNS')`. |
| Same manifest rendered on different machines | NOT in scope. C-05 specifies same inputs on same environment. Cross-machine determinism is not guaranteed. Documented in the report config. |
| Container metadata (creation_time) differs | Not detected by `framemd5` (which checksums decoded pixels, not container). Classified as cosmetic. Documented as a known non-determinism source in the audit checklist. |

## Test Strategy

### Unit Tests: `test/unit/determinism.test.ts`

1. **compareFrameMd5s — all identical:** 3 runs with identical MD5 arrays → `{ verdict: 'byte-identical', divergentFrames: 0, identicalFrames: N }`.
2. **compareFrameMd5s — one frame differs in one run:** 3 runs, frame 5 differs in run 2 → `{ divergentFrames: 1, divergentFrameIndices: [5] }`.
3. **compareFrameMd5s — multiple frames differ:** Frames 0, 3, 7 differ → `{ divergentFrames: 3, divergentFrameIndices: [0, 3, 7] }`.
4. **compareFrameMd5s — frame count mismatch:** Arrays of length 10 and 12 → throws `FRAME_COUNT_MISMATCH`.
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
15. **verifyDeterminism — run count validation:** `runs: 1` → RangeError. `runs: 11` → RangeError.

### Integration Tests: `test/integration/determinism.test.ts`

16. **End-to-end determinism — single scene:** Register a test geometry with 1 slot. Create a solid-color test image. Use `verifyDeterminism()` with `runs: 3`, 5 frames at 320×240, software WebGL, `deterministic: true`. Assert `report.passed === true` and `report.encodedComparison.verdict === 'byte-identical'`.
17. **End-to-end determinism — multi-scene with crossfade:** 2 scenes, crossfade transition, 10 frames total. Assert `report.passed === true`.
18. **extractFrameMd5s — real MP4:** Render a short MP4 via Orchestrator. Call `extractFrameMd5s`. Assert returns array of expected length with valid hex MD5 strings (32 chars, hex chars only).
19. **computePerFramePsnr — identical files:** Render one MP4. Call `computePerFramePsnr(mp4, mp4)`. Assert all values are `Infinity`.
20. **Partial run failure:** Mock one render to fail. Assert 2 remaining runs are compared and report shows `runsCompleted: 2`.
21. **Static analysis audit:** Run grep against `src/engine/`, `src/page/`, `src/scenes/`, `src/camera/` for `Math.random`, `Date.now`, `new Date`, `crypto.getRandomValues`, `crypto.randomUUID`. Assert zero matches (excluding comments and the `determinism.ts` file itself).

### Relevant Testable Claims

- **TC-06:** Tests 16 and 17 directly verify: "render same composition 3 times, compare checksums."
- **C-05:** The entire objective validates C-05.
- **C-03:** Deterministic output is a consequence of the virtualized clock. TC-06 passing provides evidence for C-03 correctness.

## Integration Points

### Depends on

| Dependency | What OBJ-073 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class and `OrchestratorConfig` for performing render runs. `OrchestratorResult` for collecting render durations. The module creates a fresh `Orchestrator` per run and calls `render()`. |
| **OBJ-013** (FFmpegEncoder — transitive via OBJ-035) | `resolveFFmpegPath()` for locating FFmpeg binary. `deterministic` config flag for single-threaded encoding. |

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
                                  #       formatSummary(), DeterministicRng
  test/
    unit/
      determinism.test.ts         # NEW — unit tests for comparison/report logic
    integration/
      determinism.test.ts         # NEW — end-to-end determinism verification
```

## Non-Determinism Audit Checklist

This checklist must be executed as part of the implementation and its results documented in the verification report.

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

---

I believe this revision addresses all seven of the challenger's issues:

1. **FrameHashCollector removed** — replaced with post-hoc comparison via `extractFrameMd5s()` and `computePerFramePsnr()`. No Orchestrator modification needed. (D2)
2. **CLI sub-command deferred** — module only, CLI wiring left to OBJ-083. (D8)
3. **Pass criteria clarified** — AC-04/AC-05 expect byte-identical (the expected outcome); AC-06/AC-07 define the fallback logic. Both `'byte-identical'` and `'visually-indistinguishable'` are passing. Explicit note added under AC-04/AC-05.
4. **DeterministicRng fixed** — now a `class` with `static fromSeed()`, not an `interface`.
5. **File placement simplified** — no `src/cli/commands/` directory.
6. **Partial runs clarified** — D11 explicitly states caller filters to completed runs; `compareFrameMd5s` documents its precondition.
7. **softwareOnly mapping removed** — no CLI, so no mapping needed. The `config.gpu` boolean is recorded in the report directly.

I'd like the challenger to verify and approve this revision.

---

## Round 4 — spec_challenger

I've verified the revised spec against all seven issues from Round 2.

## Verification of Fixes

1. **FrameHashCollector removed** ✅ — D2 is clear: post-hoc comparison only via `extractFrameMd5s` and `computePerFramePsnr`. No Orchestrator modification. The diagnostic gap (can't isolate L1-L3 from L4) is honestly documented.

2. **CLI sub-command deferred** ✅ — D8 explicitly defers to OBJ-083. File placement has no `src/cli/` directory. Clean.

3. **Pass criteria clarified** ✅ — AC-04/AC-05 set byte-identical as expected outcome. AC-06/AC-07 define fallback. The note under AC-04/AC-05 connects them clearly. Both `'byte-identical'` and `'visually-indistinguishable'` are passing.

4. **DeterministicRng** ✅ — Now a class with `static fromSeed()`. Compiles.

5. **File placement** ✅ — Simplified to just `src/engine/determinism.ts` and test files.

6. **Partial runs** ✅ — D11 is explicit. `compareFrameMd5s` documents its `runs.length >= 2` precondition.

7. **softwareOnly mapping** ✅ — Eliminated with the CLI. Report records `config.gpu` directly.

## One Remaining Minor Issue

**`RangeError` vs `DeterminismError('INVALID_RUN_COUNT')`:** D7, AC-09, and the edge case table all say `RangeError` for invalid run counts. But `VerifyDeterminismError` includes `'INVALID_RUN_COUNT'` — a code that's never thrown. An implementer would see both and not know which to use.

**Fix:** Remove `'INVALID_RUN_COUNT'` from the `VerifyDeterminismError` union. The `RangeError` is the correct choice for a simple bounds check — it's a standard JS idiom that doesn't need a custom error class. I'll apply this in the final write.

## Assessment

The spec is solid. All critical and major issues are resolved. The single minor inconsistency above has a clear fix. The layered non-determinism model, the post-hoc comparison strategy, the audit checklist, and the acceptance criteria are all well-specified and implementable. An implementer can build from this without guessing.

CONCLUSION:

OBJ-073 specifies a deterministic output verification plan comprising: (1) a `src/engine/determinism.ts` module with `verifyDeterminism()`, `extractFrameMd5s()`, `compareFrameMd5s()`, `computePerFramePsnr()`, and `DeterministicRng`; (2) a systematic non-determinism audit checklist covering four pipeline layers; (3) post-hoc comparison using FFmpeg's `framemd5` muxer with 60dB PSNR fallback; (4) acceptance criteria that verify C-05 and TC-06 through N-run comparison. CLI integration is deferred to OBJ-083. The `INVALID_RUN_COUNT` error code is removed — `RangeError` is used for bounds checking instead.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-073/output.md",
  "content": "# Specification: OBJ-073 \u2014 Deterministic Output Verification Plan\n\n## Summary\n\nOBJ-073 delivers the **deterministic output verification plan** \u2014 a comprehensive procedure and supporting utility module for verifying constraint C-05 (deterministic output) and testable claim TC-06 (virtualized clock produces deterministic output). This objective provides: (1) a systematic audit of all non-determinism sources in the depthkit pipeline, (2) a seeding strategy for any randomized elements, (3) a post-hoc checksum comparison methodology using FFmpeg's `framemd5` muxer and PSNR filter, (4) a reusable programmatic API (`src/engine/determinism.ts`) that automates N-run comparison, and (5) concrete pass/fail thresholds with escalation procedures when non-determinism is detected. The CLI sub-command is explicitly deferred \u2014 this objective delivers the module and procedure document, not CLI wiring.\n\n## Interface Contract\n\n### Module: `src/engine/determinism.ts`\n\n```typescript\n/**\n * Utility module for deterministic rendering verification.\n * Used programmatically by integration tests and available for\n * future CLI integration (deferred to OBJ-083 or similar).\n *\n * Verification strategy: post-hoc comparison. Render N times to\n * N output MP4s, then compare decoded frame content using FFmpeg's\n * framemd5 muxer and psnr filter. This avoids any modification to\n * the Orchestrator's internals (OBJ-035 D1: single render() method,\n * no exposed sub-components).\n */\n\nimport type { OrchestratorConfig, OrchestratorResult } from './orchestrator.js';\n\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n// Configu
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-073/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-073/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-073",
     3→  "description": "Deterministic output verification plan -- procedure for comparing frame checksums across multiple render runs on the same hardware to verify C-05 (deterministic output). Covers seeding strategy for any randomized elements. Addresses TC-06 (virtualized clock produces deterministic output -- render same composition 3 times, compare checksums).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 6 validation plan. Covers C-05 and TC-06."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-073/meta.json",
  "content": "{\n  \"id\": \"OBJ-073\",\n  \"description\": \"Deterministic output verification plan -- procedure for comparing frame checksums across multiple render runs on the same hardware to verify C-05 (deterministic output). Covers seeding strategy for any randomized elements. Addresses TC-06 (virtualized clock produces deterministic output -- render same composition 3 times, compare checksums).\",\n  \"category\": \"integration\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T00:00:00Z\",\n  \"depends_on\": [\"OBJ-035\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 6 validation plan. Covers C-05 and TC-06. Delivers src/engine/determinism.ts module with verifyDeterminism(), extractFrameMd5s(), compareFrameMd5s(), computePerFramePsnr(), DeterministicRng. CLI sub-command deferred to OBJ-083. Uses post-hoc framemd5 comparison (no Orchestrator modification). Pass criteria: byte-identical MD5s expected; PSNR >= 60dB fallback acceptable.\",\n  \"status\": \"complete\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-073/meta.json has been updated successfully.
Now commit to git:
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
[Tool Result] 5157902 spec(OBJ-075): blind authoring test plan for TC-01, TC-04, TC-08, SC-02
8c0844d spec(OBJ-069): Edge reveal systematic validation harness
f281cf8 spec(OBJ-039): Three.js page-side geometry instantiation
de8ffe4 OBJ-071: Spec for SKILL.md geometry and camera reference sections
3c78409 OBJ-077: End-to-end integration test plan specification
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-073/meta.json

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
  "command": "git add nodes/OBJ-073/output.md nodes/OBJ-073/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-073): Deterministic output verification plan for C-05 and TC-06\n\nDelivers src/engine/determinism.ts module specification with verifyDeterminism(),\nextractFrameMd5s(), compareFrameMd5s(), computePerFramePsnr(), and DeterministicRng.\nUses post-hoc framemd5 comparison without modifying the Orchestrator. Pass criteria:\nbyte-identical MD5s expected, PSNR >= 60dB fallback acceptable. CLI deferred to OBJ-083.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-073 spec files"
}
[Tool Result] [master e5db634] spec(OBJ-073): Deterministic output verification plan for C-05 and TC-06
 2 files changed, 583 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-073/output.md
The specification for OBJ-073 has been written to disk and committed. Here's a summary of the final agreed spec:

**OBJ-073 — Deterministic Output Verification Plan** delivers:

1. **`src/engine/determinism.ts` module** with:
   - `verifyDeterminism()` — primary entry point that renders N times, extracts per-frame MD5s via FFmpeg's `framemd5` muxer, compares all pairs, and produces a structured report
   - `extractFrameMd5s()`, `compareFrameMd5s()`, `computePerFramePsnr()` — lower-level utilities usable by OBJ-077/OBJ-078
   - `DeterministicRng` — contingency PRNG class (expected unused)
   - `DeterminismError` — structured error class

2. **Non-determinism audit checklist** covering four pipeline layers (scene state, WebGL rendering, frame capture, FFmpeg encoding) with specific grep commands and Three.js-specific concerns

3. **Pass/fail criteria**: byte-identical frame MD5s expected for software WebGL + deterministic encoding; PSNR >= 60dB fallback acceptable per C-05's "visually indistinguishable" clause

**Key design decisions resolved during deliberation:**
- Post-hoc comparison only (no Orchestrator modification) — respects OBJ-035 D1
- CLI sub-command deferred to OBJ-083 (avoids undeclared dependency on verified OBJ-046)
- `RangeError` for bounds checking (removed unused `INVALID_RUN_COUNT` error code)
- `DeterministicRng` as a class (not interface — TypeScript compliance)
- Clear separation between byte-identical expectation and PSNR fallback in acceptance criteria
