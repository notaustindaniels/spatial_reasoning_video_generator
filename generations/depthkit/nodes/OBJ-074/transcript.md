# Deliberation Transcript: OBJ-074

---

## Round 1 — spec_author

Looking at OBJ-074's metadata and dependencies, this is a benchmark procedure specification covering C-08 and TC-02. Let me read the existing codebase to understand what's already in place.
[Tool: ToolSearch]
  Input: {
  "query": "select:Glob,Read,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the existing codebase to understand what's already built and what the benchmark needs to interact with.
[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "depthkit/test/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-074/**/*"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-035/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-074/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-049/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-049/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-074/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-074",
     3→  "description": "Performance benchmark plan -- procedure for benchmarking a 60-second, 30fps, 5-plane video at 1920x1080. Per-frame timing measurement, software WebGL vs GPU acceleration comparison, identification of bottlenecks (capture time, encode time, render time). Covers C-08 (under 15 minutes on 4-core VPS) and TC-02 (under 500ms per frame with software WebGL).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035", "OBJ-049"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 6 validation plan. Covers C-08 and TC-02."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*"
}
[Tool Result] No files found

[Tool: Grep]
  Input: {
  "pattern": "OrchestratorResult|CaptureStats|RenderProgress",
  "glob": "**/*.ts",
  "output_mode": "files_with_matches"
}
[Tool Result] No files found
The codebase doesn't have implementation yet — this is spec-only at this stage. Good. I have the full dependency specs from OBJ-035 and OBJ-049 in the seed document above. Let me also check for any related benchmark or test nodes.
[Tool: Grep]
  Input: {
  "pattern": "benchmark|perf|TC-02|C-08",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes",
  "output_mode": "files_with_matches"
}
[Tool Result] Found 92 files
nodes/OBJ-069/transcript.md
nodes/OBJ-069/output.md
nodes/OBJ-039/transcript.md
nodes/OBJ-039/output.md
nodes/OBJ-071/transcript.md
nodes/OBJ-071/output.md
nodes/OBJ-077/transcript.md
nodes/OBJ-048/transcript.md
nodes/OBJ-077/meta.json
nodes/OBJ-077/output.md
nodes/OBJ-048/output.md
nodes/OBJ-037/transcript.md
nodes/OBJ-047/transcript.md
nodes/OBJ-047/output.md
nodes/OBJ-070/transcript.md
nodes/OBJ-070/output.md
nodes/OBJ-028/transcript.md
nodes/OBJ-017/transcript.md
nodes/OBJ-028/output.md
nodes/OBJ-017/output.md
nodes/OBJ-036/transcript.md
nodes/OBJ-036/output.md
nodes/OBJ-040/transcript.md
nodes/OBJ-040/output.md
nodes/OBJ-058/transcript.md
nodes/OBJ-058/meta.json
nodes/OBJ-058/output.md
nodes/OBJ-041/transcript.md
nodes/OBJ-041/meta.json
nodes/OBJ-041/output.md
nodes/OBJ-046/transcript.md
nodes/OBJ-046/output.md
nodes/OBJ-038/transcript.md
nodes/OBJ-038/output.md
nodes/OBJ-035/transcript.md
nodes/OBJ-035/output.md
nodes/OBJ-029/transcript.md
nodes/OBJ-029/output.md
n... [truncated]
Let me check the OBJ-012 (FrameCapture) spec for CaptureStats and OBJ-046 (CLI) for how benchmarks might be invoked:
[Tool: Grep]
  Input: {
  "pattern": "CaptureStats|FrameTimingBreakdown|per.frame",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-012/output.md",
  "output_mode": "content",
  "-C": 3
}
[Tool Result] 78-/**
79- * Aggregate capture statistics for performance monitoring.
80- */
81:export interface CaptureStats {
82-  /** Total number of frames captured. */
83-  captureCount: number;
84-
85-  /** Total capture time across all frames in milliseconds. */
86-  totalCaptureMs: number;
87-
88:  /** Average capture time per frame in milliseconds. 0 if no captures. */
89-  averageCaptureMs: number;
90-
91-  /** Minimum capture time across all frames. Infinity if no captures. */
--
170-   * Returns aggregate capture statistics.
171-   * Statistics accumulate over the lifetime of this FrameCapture instance.
172-   */
173:  getStats(): CaptureStats;
174-
175-  /**
176-   * Resets capture statistics to zero.
--
202-- Handles CSS animations and network idle (depthkit's virtualized clock means the page is always in a settled state after `renderFrame()`)
203-- Handles clip regions (depthkit captures the full viewport)
204-
205:By using CDP directly, we eliminate this overhead and gain access to the... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "benchmark|--bench",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "output_mode": "content",
  "-C": 3
}
[Tool Result] No matches found

[Tool: Grep]
  Input: {
  "pattern": "FFmpegEncoderResult|frameCount|encoderResult",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "output_mode": "content",
  "-C": 3
}
[Tool Result] 87-/**
88- * Result returned when encoding completes successfully.
89- */
90:export interface FFmpegEncoderResult {
91-  /** Absolute path to the output MP4 file. */
92-  outputPath: string;
93-
94-  /** Total number of frames written. */
95:  frameCount: number;
96-
97-  /** Total encoding duration in milliseconds (wall-clock time from start() to finalize()). */
98-  durationMs: number;
--
170-   * Returns the encoding result on success.
171-   * Throws FFmpegEncoderError if FFmpeg exits with a non-zero code.
172-   */
173:  finalize(): Promise<FFmpegEncoderResult>;
174-
175-  /**
176-   * Kills the FFmpeg process immediately (SIGKILL) and cleans up.
--
302-- [ ] **AC-06:** `writeFrame()` rejects with `FFmpegEncoderError` when called before `start()`.
303-- [ ] **AC-07:** `writeFrame()` rejects with `FFmpegEncoderError` when called after `finalize()`.
304-- [ ] **AC-08:** For `rgba` format, `writeFrame()` rejects with `FFmpegEncoderError` if the buffer size is not exactly `width * hei... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "RendererInfo|rendererInfo",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "output_mode": "content",
  "-C": 3
}
[Tool Result] 57-   *
58-   * If not initialized, returns a zeroed-out structure (see Edge Cases).
59-   */
60:  getRendererInfo(): RendererInfo;
61-
62-  /**
63-   * Renders the current scene with the current camera to the canvas.
--
156-  preserveDrawingBuffer?: boolean;
157-}
158-
159:interface RendererInfo {
160-  /** True if init() succeeded. */
161-  initialized: boolean;
162-  /** Canvas dimensions [width, height] in pixels. */
--
267-}
268-
269-/**
270: * Diagnostic info returned by the page's getRendererInfo() function.
271- */
272:export interface RendererInfo {
273-  initialized: boolean;
274-  canvasSize: [number, number];
275-  webglVersion: string;
--
364-
365-### D9: WebGL 2 Preferred, WebGL 1 Fallback Acceptable
366-
367:**Decision:** The `WebGLRenderer` is created without forcing a specific WebGL version. Three.js defaults to WebGL 2 when available, falls back to WebGL 1. `getRendererInfo()` reports the acquired version.
368-
369-**Rationale:** SwiftShader (C-11) supports WebGL 2. N... [truncated]
Now I have a solid understanding of the interfaces. Let me check what geometries are available for building a reference benchmark manifest:
[Tool: Grep]
  Input: {
  "pattern": "stage|tunnel|geometry.*slots",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "output_mode": "content",
  "-C": 2,
  "head_limit": 40
}
[Tool Result] 3-## Summary
4-
5:[Omitted long matching line]
6-
7-## Interface Contract
--
10-
11-```typescript
12:// src/scenes/geometries/stage.ts
13-
14-import type { SceneGeometry } from './types';
15-
16-/**
17: * The stage scene geometry — the default geometry for depthkit.
18- *
19- * Spatial arrangement: a large backdrop plane at deep Z, a floor
--
29- * SKILL.md examples.
30- */
31:export const stageGeometry: SceneGeometry;
32-```
33-
--
36-| Field | Value | Rationale |
37-|-------|-------|-----------|
38:| `name` | `'stage'` | Matches seed Section 4.2 naming |
39-| `description` | `'A classic subject-in-front-of-background setup. Large backdrop at depth, angled floor plane with real perspective foreshortening, and a subject plane at shallow Z. The most versatile geometry for general-purpose scenes.'` | Describes the spatial feel per OBJ-005's `description` contract |
40-| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes in or drifts laterally." Forward push is th... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "getGeometryRegistry|GeometryRegistry",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "output_mode": "content",
  "-C": 2,
  "head_limit": 30
}
[Tool Result] 202- *   geometry + camera compatibility.
203- */
204:export type GeometryRegistry = Record<string, SceneGeometry>;
205-```
206-
--
210-// src/scenes/geometries/registry.ts
211-
212:import type { SceneGeometry, GeometryRegistry } from './types';
213-
214-/**
--
216- *
217- * On first call, the registry is locked — no further registrations
218: * are accepted (see D10). Returns a deeply frozen GeometryRegistry.
219- * Subsequent calls return the same frozen object.
220- *
--
222- * (geometry, slot, position tuple) throw TypeError at runtime.
223- *
224: * @returns A deeply frozen GeometryRegistry.
225- */
226:export function getGeometryRegistry(): Readonly<GeometryRegistry>;
227-
228-/**
229- * Retrieves a single geometry by name.
230- *
231: * Implicitly locks the registry on first call (same as getGeometryRegistry).
232- *
233- * @param name - The geometry name (e.g., 'tunnel', 'stage').

[Showing results with pagination = limit: 30, offset: 0]
Good. I now have a thorough understanding of the dependencies and interfaces. Let me propose the spec.

---

# Proposed Specification: OBJ-074 — Performance Benchmark Plan

## Summary

OBJ-074 delivers a **benchmark runner module** (`src/benchmark/runner.ts`) and a **reference benchmark manifest** (`src/benchmark/fixtures/reference-manifest.json`) that together provide a reproducible procedure for measuring depthkit's rendering performance. The benchmark measures per-frame timing breakdown (render time, capture time, encode time), compares software WebGL vs. GPU acceleration, identifies bottlenecks, and validates compliance with C-08 (60-second, 30fps, 5-plane video renders in under 15 minutes on a 4-core VPS) and TC-02 (under 500ms per frame with software WebGL). The benchmark is invocable programmatically and produces a structured `BenchmarkReport` JSON for analysis, regression tracking, and CI gating.

## Interface Contract

### Module: `src/benchmark/runner.ts`

```typescript
import type { OrchestratorResult, RenderProgress } from '../engine/orchestrator.js';
import type { WebGLRendererInfo } from '../engine/rendering-config.js';
import type { CaptureStats } from '../engine/frame-capture.js';
import type { GpuMode } from '../engine/rendering-config.js';
import type { ManifestRegistry } from '../manifest/schema.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

// ────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────

/**
 * Configuration for a benchmark run.
 */
export interface BenchmarkConfig {
  /**
   * GPU rendering mode for this benchmark run.
   * Default: 'software' (C-11 baseline).
   */
  gpuMode?: GpuMode;

  /**
   * Output directory for benchmark artifacts:
   * - report JSON file
   * - rendered MP4 (retained for manual inspection)
   * - per-frame timing CSV (when collectFrameTimings is true)
   *
   * Created if it doesn't exist.
   * Default: './benchmark-results'
   */
  outputDir?: string;

  /**
   * Whether to collect per-frame timing data.
   * When true, the benchmark records individual frame durations
   * and writes a CSV file alongside the report.
   *
   * Adds marginal overhead (~0.1ms/frame for timestamp collection).
   * Default: true
   */
  collectFrameTimings?: boolean;

  /**
   * Path to FFmpeg binary. Default: resolved via resolveFFmpegPath().
   */
  ffmpegPath?: string;

  /**
   * Path to Chromium executable. Default: Puppeteer's bundled Chromium.
   */
  chromiumPath?: string;

  /**
   * The manifest registry for validation.
   * If not provided, the benchmark runner creates a default registry
   * populated with the reference geometry and camera registrations.
   */
  registry?: ManifestRegistry;

  /**
   * The geometry registry. If not provided, uses getGeometryRegistry().
   */
  geometryRegistry?: GeometryRegistry;

  /**
   * The camera path registry. If not provided, uses the default
   * camera registry from OBJ-006.
   */
  cameraRegistry?: CameraPathRegistry;

  /**
   * Progress callback. Forwarded to Orchestrator's onProgress.
   * Return false to cancel the benchmark.
   */
  onProgress?: (progress: RenderProgress) => boolean | void;
}

// ────────────────────────────────────────────
// Reference Manifest
// ────────────────────────────────────────────

/**
 * The canonical benchmark parameters, matching C-08 and TC-02
 * requirements exactly. Used by the reference manifest generator
 * and documented in the benchmark report for reproducibility.
 */
export interface BenchmarkParameters {
  /** Output resolution width. Reference: 1920 */
  width: number;
  /** Output resolution height. Reference: 1080 */
  height: number;
  /** Frames per second. Reference: 30 */
  fps: number;
  /** Total video duration in seconds. Reference: 60 */
  durationSeconds: number;
  /** Total frame count (fps * durationSeconds). Reference: 1800 */
  totalFrames: number;
  /** Number of scenes. Reference: 5 */
  sceneCount: number;
  /** Planes per scene. Reference: 5 */
  planesPerScene: number;
  /** Geometry used. Reference: 'stage' */
  geometry: string;
  /** Camera preset used. Reference: 'slow_push_forward' */
  cameraPreset: string;
}

/**
 * Returns the canonical benchmark parameters as a frozen object.
 * These match C-08 and TC-02 exactly:
 * - 1920x1080, 30fps, 60 seconds = 1800 frames
 * - 5 scenes, each 12 seconds, 5 planes per scene
 * - 'stage' geometry with 'slow_push_forward' camera
 */
export function getReferenceBenchmarkParameters(): Readonly<BenchmarkParameters>;

/**
 * Generates the reference benchmark manifest as a plain object.
 *
 * The manifest contains 5 consecutive scenes, each 12 seconds,
 * using the 'stage' geometry with all 6 slots populated (5
 * required: sky, backdrop, midground, subject, near_fg; plus
 * floor). Uses procedurally generated solid-color PNG test
 * images (no external asset dependencies).
 *
 * The manifest uses 'cut' transitions between scenes to isolate
 * render performance from transition compositing overhead.
 * No audio (isolates video rendering performance).
 *
 * @returns A manifest object ready to pass to Orchestrator.
 */
export function generateReferenceManifest(): Record<string, unknown>;

/**
 * Generates solid-color PNG test images for the benchmark manifest
 * and writes them to the specified directory.
 *
 * Creates one image per unique slot across all scenes. Images are
 * 1920x1080 solid-color PNGs (one distinct color per slot type:
 * sky=deep blue, backdrop=dark green, midground=brown, floor=gray,
 * subject=red, near_fg=semi-transparent white).
 *
 * Subject and near_fg images include alpha channels (transparent
 * backgrounds with a centered colored rectangle) to exercise the
 * alpha texture path.
 *
 * @param outputDir - Directory to write images. Created if missing.
 * @returns Map of slot-relative paths (as used in the manifest)
 *          to absolute file paths on disk.
 */
export function generateBenchmarkAssets(
  outputDir: string
): Promise<Map<string, string>>;

// ────────────────────────────────────────────
// Per-Frame Timing
// ────────────────────────────────────────────

/**
 * Timing breakdown for a single frame.
 * Collected via the onProgress callback's elapsed time and
 * internal high-resolution timestamps.
 */
export interface FrameTiming {
  /** Frame number (zero-indexed). */
  frame: number;
  /** Total wall-clock time for this frame in ms (from previous
   *  frame completion to this frame's completion). */
  totalMs: number;
  /** Scene ID(s) active for this frame. */
  activeSceneIds: string[];
}

// ────────────────────────────────────────────
// Benchmark Report
// ────────────────────────────────────────────

/**
 * Structured benchmark report produced by runBenchmark().
 * Serializable to JSON for storage and regression comparison.
 */
export interface BenchmarkReport {
  /** ISO 8601 timestamp when the benchmark started. */
  timestamp: string;

  /** Benchmark runner version. Matches depthkit package version. */
  version: string;

  /** The benchmark parameters used. */
  parameters: BenchmarkParameters;

  /** Environment information for reproducibility. */
  environment: EnvironmentInfo;

  /** WebGL renderer info from the browser instance. */
  webglInfo: WebGLRendererInfo;

  /** GPU mode requested and what was actually used. */
  gpuMode: {
    requested: GpuMode;
    actual: 'software' | 'hardware';
  };

  /** Aggregate timing results. */
  timing: TimingResults;

  /** Frame capture statistics from OBJ-012's CaptureStats. */
  captureStats: CaptureStats;

  /** Per-frame timings. Present only when collectFrameTimings is true. */
  frameTimings?: FrameTiming[];

  /** Pass/fail assessment against C-08 and TC-02. */
  compliance: ComplianceResult;

  /** Path to the rendered MP4 file (for manual inspection). */
  outputVideoPath: string;

  /** Path to the per-frame CSV file. null if not collected. */
  frameTimingsCsvPath: string | null;
}

/**
 * System environment information captured at benchmark start.
 */
export interface EnvironmentInfo {
  /** Node.js version string. */
  nodeVersion: string;

  /** OS platform (process.platform). */
  platform: string;

  /** OS architecture (process.arch). */
  arch: string;

  /** CPU model string (first entry from os.cpus()). */
  cpuModel: string;

  /** Number of CPU cores (os.cpus().length). */
  cpuCores: number;

  /** Total system memory in MB (os.totalmem() / 1024 / 1024). */
  totalMemoryMb: number;

  /** Free memory at benchmark start in MB. */
  freeMemoryMb: number;

  /** FFmpeg version string (from ffmpeg -version, first line). */
  ffmpegVersion: string;

  /** Chromium version string (from browser.version()). */
  chromiumVersion: string;
}

/**
 * Aggregate timing results.
 */
export interface TimingResults {
  /** Total wall-clock time for the entire benchmark run in ms.
   *  Includes asset generation, validation, rendering, finalization.
   *  From runBenchmark() entry to report generation. */
  totalBenchmarkMs: number;

  /** Wall-clock time for the render loop only in ms.
   *  Maps to OrchestratorResult.renderDurationMs. */
  renderLoopMs: number;

  /** Wall-clock time for the full orchestrator in ms.
   *  Maps to OrchestratorResult.totalDurationMs.
   *  Includes validation, browser launch, scene setup,
   *  render loop, FFmpeg finalization. */
  orchestratorTotalMs: number;

  /** Average time per frame in ms.
   *  Maps to OrchestratorResult.averageFrameMs. */
  averageFrameMs: number;

  /** Median time per frame in ms.
   *  Computed from per-frame timings. null if collectFrameTimings
   *  is false. */
  medianFrameMs: number | null;

  /** 95th percentile frame time in ms. null if not collected. */
  p95FrameMs: number | null;

  /** 99th percentile frame time in ms. null if not collected. */
  p99FrameMs: number | null;

  /** Maximum single-frame time in ms. null if not collected. */
  maxFrameMs: number | null;

  /** Minimum single-frame time in ms. null if not collected. */
  minFrameMs: number | null;

  /** Standard deviation of frame times in ms. null if not collected. */
  stddevFrameMs: number | null;

  /** Throughput: frames rendered per wall-clock second.
   *  totalFrames / (renderLoopMs / 1000). */
  throughputFps: number;

  /** Asset generation time in ms (generating test PNGs). */
  assetGenerationMs: number;

  /** Capture-only aggregate time from CaptureStats.totalCaptureMs. */
  totalCaptureMs: number;

  /** Average capture time from CaptureStats.averageCaptureMs. */
  averageCaptureMs: number;
}

/**
 * Pass/fail compliance assessment.
 */
export interface ComplianceResult {
  /** C-08: Total render time < 15 minutes (900,000ms). */
  c08: {
    /** Whether the benchmark passed C-08. */
    passed: boolean;
    /** The threshold in ms. Always 900000. */
    thresholdMs: number;
    /** The measured render loop time in ms. */
    measuredMs: number;
    /** Headroom: (thresholdMs - measuredMs) / thresholdMs as ratio. */
    headroom: number;
  };
  /** TC-02: Average frame time < 500ms. */
  tc02: {
    /** Whether the benchmark passed TC-02. */
    passed: boolean;
    /** The threshold in ms. Always 500. */
    thresholdMs: number;
    /** The measured average frame time in ms. */
    measuredMs: number;
    /** Headroom ratio. */
    headroom: number;
  };
}

// ────────────────────────────────────────────
// Runner
// ────────────────────────────────────────────

/**
 * Executes the reference benchmark and produces a BenchmarkReport.
 *
 * Procedure:
 * 1. Collect environment info (Node version, OS, CPU, memory,
 *    FFmpeg version).
 * 2. Generate solid-color test images to a temp directory inside
 *    outputDir.
 * 3. Generate the reference manifest (pointing to the test images).
 * 4. Resolve rendering config via OBJ-049's resolveRenderingConfig().
 * 5. Create Orchestrator with the manifest, registries, and config.
 * 6. Attach onProgress handler that records per-frame timings
 *    (if collectFrameTimings is true) and forwards to caller's
 *    onProgress.
 * 7. Call orchestrator.render().
 * 8. After render completes, probe WebGL renderer info from
 *    OrchestratorResult.rendererInfo.
 * 9. Compute aggregate statistics (median, p95, p99, stddev)
 *    from per-frame timings.
 * 10. Assess C-08 and TC-02 compliance.
 * 11. Write report JSON to outputDir/benchmark-report.json.
 * 12. Write per-frame CSV to outputDir/frame-timings.csv (if collected).
 * 13. Return the BenchmarkReport.
 *
 * The benchmark does NOT clean up the outputDir — the rendered
 * MP4 and report are retained for manual inspection and regression
 * comparison.
 *
 * @throws BenchmarkError if the render fails or environment
 *         collection fails.
 */
export function runBenchmark(
  config?: BenchmarkConfig
): Promise<BenchmarkReport>;

/**
 * Runs the benchmark twice (once in software mode, once in hardware
 * mode) and produces a comparison report.
 *
 * If hardware mode fails (e.g., no GPU available), the hardware
 * result is null and the comparison report documents the failure.
 *
 * @returns A comparison of software vs. hardware results.
 */
export function runComparisonBenchmark(
  config?: Omit<BenchmarkConfig, 'gpuMode'>
): Promise<ComparisonReport>;

/**
 * Comparison report for software vs. hardware benchmark runs.
 */
export interface ComparisonReport {
  /** Software rendering results. Always present. */
  software: BenchmarkReport;

  /** Hardware rendering results. null if hardware mode failed. */
  hardware: BenchmarkReport | null;

  /** If hardware run failed, the error message. */
  hardwareError?: string;

  /** Speedup ratio: software.renderLoopMs / hardware.renderLoopMs.
   *  null if hardware is unavailable. >1.0 means hardware is faster. */
  speedupRatio: number | null;

  /** Per-frame comparison summary. null if either lacks frame timings. */
  frameSummary: {
    softwareAvgMs: number;
    hardwareAvgMs: number | null;
    softwareP95Ms: number;
    hardwareP95Ms: number | null;
  } | null;
}

// ────────────────────────────────────────────
// Error
// ────────────────────────────────────────────

export type BenchmarkErrorCode =
  | 'ENVIRONMENT_PROBE_FAILED'
  | 'ASSET_GENERATION_FAILED'
  | 'RENDER_FAILED'
  | 'REPORT_WRITE_FAILED'
  ;

export class BenchmarkError extends Error {
  readonly code: BenchmarkErrorCode;
  readonly cause?: Error;

  constructor(
    code: BenchmarkErrorCode,
    message: string,
    cause?: Error
  );
}

// ────────────────────────────────────────────
// Utility
// ────────────────────────────────────────────

/**
 * Formats a BenchmarkReport as a human-readable summary string.
 * Suitable for terminal output or logging.
 *
 * Example output:
 * ```
 * ═══════════════════════════════════════════
 *  DEPTHKIT PERFORMANCE BENCHMARK
 * ═══════════════════════════════════════════
 *  Parameters: 1920x1080, 30fps, 60s (1800 frames)
 *  Geometry: stage (5 planes) × 5 scenes
 *  GPU Mode: software (SwiftShader)
 * ───────────────────────────────────────────
 *  TIMING
 *  Total render:       582,340 ms  (9m 42s)
 *  Avg frame:             323 ms
 *  Median frame:          318 ms
 *  P95 frame:             412 ms
 *  P99 frame:             487 ms
 *  Throughput:           3.09 fps
 *  Capture avg:           142 ms
 * ───────────────────────────────────────────
 *  COMPLIANCE
 *  C-08 (< 15 min):     ✅ PASS  (headroom: 35.3%)
 *  TC-02 (< 500ms/fr):  ✅ PASS  (headroom: 35.4%)
 * ───────────────────────────────────────────
 *  ENVIRONMENT
 *  Node: v20.11.0 | Linux x64
 *  CPU: Intel Xeon E-2236 (4 cores)
 *  Memory: 4096 MB total, 2847 MB free
 *  Chromium: 121.0.6167.85
 *  FFmpeg: 6.1.1
 *  WebGL: SwiftShader (software)
 * ═══════════════════════════════════════════
 * ```
 */
export function formatBenchmarkReport(report: BenchmarkReport): string;

/**
 * Formats a ComparisonReport as a human-readable summary.
 */
export function formatComparisonReport(report: ComparisonReport): string;
```

### Module: `src/benchmark/fixtures/generate-assets.ts`

This is an internal module used by `generateBenchmarkAssets()`. It creates solid-color PNG test images programmatically using a minimal PNG encoder (e.g., `sharp` if available, or raw PNG construction via `zlib`). No external image dependencies.

### Per-Frame CSV Format

```
frame,totalMs,activeSceneIds
0,328.4,"scene_001"
1,315.2,"scene_001"
...
359,312.1,"scene_001"
360,487.3,"scene_002"
...
```

Scene transition frames (if any were present) would show multiple scene IDs. The reference manifest uses `cut` transitions, so all frames have a single scene ID.

## Design Decisions

### D1: Self-Contained Benchmark With No External Assets

**Decision:** The benchmark generates its own solid-color PNG test images programmatically. No external image files, no network downloads, no asset pipeline dependencies.

**Rationale:** C-08 and TC-02 measure the rendering pipeline's performance, not asset loading speed. Self-contained assets ensure the benchmark is reproducible on any machine without setup. Solid-color PNGs are trivially small but exercise the full texture → plane → WebGL → capture → FFmpeg pipeline. The images include alpha channels on subject/near_fg slots to exercise the transparency path that's common in production.

### D2: Reference Manifest Uses `stage` Geometry With Cut Transitions

**Decision:** The reference manifest uses the `stage` geometry (verified in OBJ-018) with `slow_push_forward` camera (verified in OBJ-026), 5 scenes × 12 seconds each, cut transitions only.

**Rationale:** 
- `stage` is the most representative geometry — 6 slots (5 visible planes minimum per C-08's "5 textured planes per scene"), verified status.
- `slow_push_forward` is the default camera for stage, exercises camera interpolation per frame.
- Cut transitions isolate render performance from transition compositing. Transition performance is a separate concern.
- 5 scenes × 12 seconds = 60 seconds exactly, matching C-08.
- No audio — audio muxing is a trivial FFmpeg `-c:v copy` pass that doesn't test rendering performance.

### D3: Compliance Thresholds Are Constants, Not Configurable

**Decision:** C-08 threshold (15 minutes = 900,000ms) and TC-02 threshold (500ms/frame) are hardcoded constants, not configurable parameters.

**Rationale:** These are seed constraints. Making them configurable invites drift from the spec. The `BenchmarkReport` includes raw measurements; consumers can apply their own thresholds for regression tracking.

### D4: Per-Frame Timing via `onProgress` Callback Deltas

**Decision:** Per-frame timing is computed by recording `performance.now()` before and after each `onProgress` invocation, calculating deltas between consecutive frame completions.

**Rationale:** OBJ-035's `RenderProgress.elapsedMs` provides cumulative elapsed time. Frame N's duration = `elapsedMs[N] - elapsedMs[N-1]` (or `elapsedMs[0]` for frame 0). This captures the full frame pipeline cost (render + capture + encode write) without modifying the orchestrator. The orchestrator is a dependency, not something OBJ-074 modifies.

**Limitation:** This measures total frame time, not the render/capture/encode breakdown per frame. Per-component breakdown requires `CaptureStats` (aggregate only) and `FFmpegEncoderResult.durationMs` (aggregate only). Per-frame component breakdown would require instrumenting OBJ-035 or OBJ-012 internals — out of scope. The aggregate breakdown (total capture time vs. total render time vs. total encode time) is sufficient for bottleneck identification.

### D5: Report Is JSON — Not a Database

**Decision:** The benchmark report is a self-contained JSON file written to the output directory. No database, no time-series store.

**Rationale:** The benchmark is run manually or in CI. JSON is diffable, committable, and parseable by any tool. Regression comparison is done by diffing two report JSONs. A time-series database is premature for V1.

### D6: Comparison Benchmark Is Tolerant of Hardware Failure

**Decision:** `runComparisonBenchmark()` always runs software mode first. If hardware mode fails (no GPU, driver error), it returns `hardware: null` with the error captured. It does not throw.

**Rationale:** Most development and CI environments lack a GPU. The comparison should degrade gracefully to "software only" rather than failing entirely. The report clearly documents which modes succeeded.

### D7: No Parallel Rendering in Benchmark

**Decision:** The benchmark runs a single-instance render (one Puppeteer, one FFmpeg). It does not test parallelized multi-instance rendering (OBJ-082).

**Rationale:** C-08 says "The 15-minute target is for single-instance rendering only." Multi-instance benchmarking depends on OBJ-082 which is open and depends on OBJ-035.

### D8: Asset Generation Uses `sharp` or Raw PNG Construction

**Decision:** Test images are generated using `sharp` (if available as a dependency) or a minimal raw PNG encoder using Node.js `zlib`. The spec does not mandate a specific image library — the requirement is that the images are valid PNGs at 1920x1080 with correct alpha channels where needed.

**Rationale:** `sharp` is already a plausible dependency for depthkit (used in image processing). If not available, constructing a solid-color PNG from raw RGBA buffers + zlib deflate is straightforward (~50 lines). The benchmark must not introduce heavy dependencies.

### D9: Benchmark Output Directory Is Not Cleaned Up

**Decision:** The benchmark retains all artifacts (MP4, report JSON, CSV, test images) in the output directory.

**Rationale:** The rendered MP4 is useful for manual visual inspection. The report JSON is used for regression tracking. Cleanup is the caller's responsibility.

### D10: `EnvironmentInfo` Captures Reproducibility Context

**Decision:** The report includes Node.js version, OS, CPU model/cores, memory, FFmpeg version, and Chromium version. This provides the context needed to compare benchmarks across different machines.

**Rationale:** C-08 specifies "a standard 4-core VPS with at least 4GB RAM." The environment info lets reviewers verify whether a benchmark was run on qualifying hardware.

### D11: Statistical Percentiles For Frame Jitter Detection

**Decision:** The report includes median, p95, p99, max, min, and standard deviation of per-frame times.

**Rationale:** Average frame time can mask jitter. A benchmark that averages 300ms/frame but has p99 at 2000ms indicates a serious problem (GC pauses, Chromium throttling, memory pressure). Percentiles expose these outliers. The throttling-prevention flags from OBJ-049 should minimize jitter, but the benchmark must be able to detect it if it occurs.

## Acceptance Criteria

### Reference Manifest & Assets

- [ ] **AC-01:** `getReferenceBenchmarkParameters()` returns a frozen object with `width: 1920`, `height: 1080`, `fps: 30`, `durationSeconds: 60`, `totalFrames: 1800`, `sceneCount: 5`, `planesPerScene: 5`, `geometry: 'stage'`, `cameraPreset: 'slow_push_forward'`.
- [ ] **AC-02:** `generateReferenceManifest()` returns a manifest object that passes validation via `loadManifest()` with a registry containing the `stage` geometry and `slow_push_forward` camera.
- [ ] **AC-03:** The generated manifest contains exactly 5 scenes, each with `duration: 12`, `geometry: 'stage'`, `camera: 'slow_push_forward'`, and `transition_in`/`transition_out` of type `cut`.
- [ ] **AC-04:** `generateBenchmarkAssets()` creates PNG files on disk — one per unique slot. Each PNG is a valid image file readable by Three.js's texture loader.
- [ ] **AC-05:** Subject and near_fg test images have alpha channels. Sky, backdrop, midground, and floor images are opaque.

### Benchmark Execution

- [ ] **AC-06:** `runBenchmark()` with default config (software mode) produces a valid MP4 file at the output path. `ffprobe` reports 1920x1080, H.264, 30fps, approximately 60 seconds duration.
- [ ] **AC-07:** `runBenchmark()` completes without throwing on a machine with 4+ cores and 4GB+ RAM using software WebGL.
- [ ] **AC-08:** `BenchmarkReport.timing.renderLoopMs` matches `OrchestratorResult.renderDurationMs` (within 1ms tolerance for timestamp collection overhead).
- [ ] **AC-09:** `BenchmarkReport.captureStats` matches `OrchestratorResult.captureStats` exactly.

### Timing & Statistics

- [ ] **AC-10:** When `collectFrameTimings: true`, `BenchmarkReport.frameTimings` contains exactly 1800 entries (one per frame).
- [ ] **AC-11:** `timing.medianFrameMs`, `timing.p95FrameMs`, `timing.p99FrameMs`, `timing.maxFrameMs`, `timing.minFrameMs`, `timing.stddevFrameMs` are non-null when frame timings are collected.
- [ ] **AC-12:** `timing.medianFrameMs` is non-null and falls between `timing.minFrameMs` and `timing.maxFrameMs`.
- [ ] **AC-13:** `timing.throughputFps` equals `totalFrames / (renderLoopMs / 1000)` within floating-point tolerance.
- [ ] **AC-14:** When `collectFrameTimings: false`, percentile fields are null and `frameTimings` is undefined.

### Compliance Assessment

- [ ] **AC-15:** `compliance.c08.thresholdMs === 900000` (15 minutes in ms).
- [ ] **AC-16:** `compliance.tc02.thresholdMs === 500`.
- [ ] **AC-17:** `compliance.c08.passed === true` when `timing.orchestratorTotalMs < 900000`.
- [ ] **AC-18:** `compliance.tc02.passed === true` when `timing.averageFrameMs < 500`.
- [ ] **AC-19:** `compliance.c08.headroom` equals `(900000 - measuredMs) / 900000`.
- [ ] **AC-20:** `compliance.tc02.headroom` equals `(500 - measuredMs) / 500`.

### Environment Info

- [ ] **AC-21:** `environment.nodeVersion` is a non-empty string starting with 'v'.
- [ ] **AC-22:** `environment.cpuCores` is a positive integer.
- [ ] **AC-23:** `environment.totalMemoryMb` is a positive number.
- [ ] **AC-24:** `environment.ffmpegVersion` is a non-empty string.
- [ ] **AC-25:** `environment.chromiumVersion` is a non-empty string.

### WebGL Info

- [ ] **AC-26:** `webglInfo` is populated from OBJ-049's `probeWebGLRenderer()` or from `OrchestratorResult.rendererInfo`. In software mode, `webglInfo.isSoftwareRenderer === true` (maps from `rendererInfo`; see D12).
- [ ] **AC-27:** `gpuMode.requested` matches the config's `gpuMode`. `gpuMode.actual` reflects whether the renderer is software or hardware.

### Report Output

- [ ] **AC-28:** `runBenchmark()` writes `benchmark-report.json` to `outputDir`. The file is valid JSON that deserializes to a `BenchmarkReport`.
- [ ] **AC-29:** When `collectFrameTimings: true`, `runBenchmark()` writes `frame-timings.csv` to `outputDir`. The CSV has a header row and 1800 data rows.
- [ ] **AC-30:** `formatBenchmarkReport()` produces a non-empty string containing the C-08 and TC-02 pass/fail indicators.

### Comparison Benchmark

- [ ] **AC-31:** `runComparisonBenchmark()` in a software-only environment returns `software` as a valid report and `hardware: null` with a non-empty `hardwareError`.
- [ ] **AC-32:** `ComparisonReport.speedupRatio` is null when hardware is unavailable.

### Error Handling

- [ ] **AC-33:** If the orchestrator throws during the benchmark, `runBenchmark()` throws `BenchmarkError` with code `RENDER_FAILED` and the orchestrator error as `cause`.
- [ ] **AC-34:** If the output directory cannot be created, `runBenchmark()` throws `BenchmarkError` with code `REPORT_WRITE_FAILED`.

### Performance (C-08, TC-02 — The Actual Gate)

- [ ] **AC-35:** On a 4-core VPS with 4GB+ RAM using software WebGL, `compliance.c08.passed === true` (render completes in under 15 minutes). *This is a performance test — logged as a benchmark result, not enforced in CI on underpowered machines.*
- [ ] **AC-36:** On the same hardware, `compliance.tc02.passed === true` (average frame time under 500ms). *Same caveat.*

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Output directory doesn't exist | Created via `fs.mkdir(outputDir, { recursive: true })`. |
| Output directory not writable | `BenchmarkError` code `REPORT_WRITE_FAILED`. |
| FFmpeg not installed | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `ENCODE_FAILED`). |
| Chromium not available | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `BROWSER_LAUNCH_FAILED`). |
| Benchmark cancelled via `onProgress` returning false | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `CANCELLED`). Partial report is NOT generated — a cancelled benchmark is not a valid measurement. |
| Machine has < 4GB RAM | Benchmark runs but may be slower. `environment.totalMemoryMb` documents the constraint. `compliance.c08.passed` may be `false`. Report is still valid. |
| Concurrent benchmark runs to same outputDir | Last writer wins. The benchmark does not lock the output directory. Run in separate directories for concurrent benchmarks. |
| `generateBenchmarkAssets()` called with empty string path | Throws `BenchmarkError` code `ASSET_GENERATION_FAILED`. |
| Stage geometry not registered | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `GEOMETRY_NOT_FOUND`). The runner's default registry should include stage. |
| `collectFrameTimings: false` | Percentile fields are null. CSV is not written. `frameTimingsCsvPath` is null. Report is still valid. |
| First frame is unusually slow (cold start) | Captured in frame timings. The p95/p99 statistics naturally handle outliers. The median is a more robust central tendency than the mean. |
| Per-frame timing resolution | `performance.now()` provides sub-ms precision in Node.js. Sufficient for frames taking 100-500ms. |

## Test Strategy

### Unit Tests: `test/unit/benchmark-runner.test.ts`

1. **Reference parameters:** `getReferenceBenchmarkParameters()` returns frozen object matching C-08/TC-02 values. Verify all fields. Verify object is frozen.

2. **Reference manifest structure:** `generateReferenceManifest()` produces a manifest with version `'3.0'`, 5 scenes, correct geometry/camera assignments, cut transitions, no audio. Validate scene durations sum to 60s.

3. **Manifest validation:** The generated manifest passes `loadManifest()` validation with a mock registry that registers `stage` geometry with the expected slots and `slow_push_forward` camera.

4. **Compliance calculation — C-08 pass:** Given `orchestratorTotalMs = 600000` (10 min), verify `c08.passed === true`, `c08.headroom ≈ 0.333`.

5. **Compliance calculation — C-08 fail:** Given `orchestratorTotalMs = 1000000` (16.7 min), verify `c08.passed === false`, `c08.headroom < 0`.

6. **Compliance calculation — TC-02 pass:** Given `averageFrameMs = 323`, verify `tc02.passed === true`, `tc02.headroom ≈ 0.354`.

7. **Compliance calculation — TC-02 fail:** Given `averageFrameMs = 550`, verify `tc02.passed === false`.

8. **Percentile computation:** Given known frame timings `[100, 200, 300, 400, 500]` (sorted), verify median = 300, p95/p99 are correct, stddev is correct.

9. **Percentile computation — all equal:** Frame timings all 250ms. Verify median = 250, stddev = 0, min = max = 250.

10. **Format report:** `formatBenchmarkReport()` with a mock report returns a string containing "C-08", "TC-02", "PASS" or "FAIL", and the resolution.

11. **Comparison report — hardware null:** Verify `speedupRatio` is null, `frameSummary.hardwareAvgMs` is null.

12. **Comparison report — both present:** Software 600s, hardware 200s. Verify `speedupRatio === 3.0`.

13. **Frame timing CSV format:** Verify header row and data row format match spec.

### Integration Tests: `test/integration/benchmark-runner.test.ts`

Use a **scaled-down** benchmark for integration testing to keep test runtime reasonable: 320x240, 10fps, 3 seconds (30 frames), 1 scene, software mode.

14. **Scaled benchmark end-to-end:** Run `runBenchmark()` with a scaled-down config (override the reference manifest parameters via a test-only helper or pass a custom small manifest). Verify: MP4 exists, report JSON exists, report deserializes, `timing` fields are positive numbers, `compliance` fields are populated.

15. **Asset generation:** `generateBenchmarkAssets()` creates files. Verify each file exists, is a valid PNG (starts with PNG magic bytes `\x89PNG`), subject image has alpha channel.

16. **Per-frame CSV:** Run scaled benchmark with `collectFrameTimings: true`. Verify CSV exists, has header + 30 data rows, frame numbers 0-29.

17. **Software WebGL verification:** Run benchmark in software mode. Verify `gpuMode.actual === 'software'` and `webglInfo.isSoftwareRenderer === true`.

18. **Environment info populated:** Verify all `EnvironmentInfo` fields are non-empty/positive.

19. **Report JSON round-trip:** Write report, read it back, verify all fields match the in-memory report.

20. **Comparison in software-only environment:** Run `runComparisonBenchmark()`. Verify `software` report is valid, `hardware` is null, `hardwareError` is a non-empty string.

### Full-Scale Benchmark (Manual / CI on Qualifying Hardware)

21. **C-08 compliance:** Run `runBenchmark()` with default config on a 4-core, 4GB+ VPS. Assert `compliance.c08.passed === true`. Log the full formatted report.

22. **TC-02 compliance:** Same run as above. Assert `compliance.tc02.passed === true`.

23. **Frame jitter analysis:** Inspect `timing.stddevFrameMs` and `timing.p99FrameMs`. If p99 > 2× average, investigate throttling or GC causes. This is a diagnostic observation, not a pass/fail criterion.

24. **Bottleneck identification:** Compare `captureStats.averageCaptureMs` to `timing.averageFrameMs`. If capture accounts for >70% of frame time, document as the primary bottleneck (informing OBJ-012 OQ-A about the need for `canvas-rgba` strategy).

### Relevant Testable Claims

- **TC-02:** Tests 21-22 directly validate the 500ms/frame threshold.
- **C-08:** Tests 21-22 directly validate the 15-minute threshold.
- **TC-06:** Determinism is not directly tested by the benchmark (OBJ-035 test #28 covers this), but the benchmark's per-frame timing variance (stddev) provides indirect evidence.
- **TC-11:** Test 17 confirms software WebGL is used. Tests 21-22 on qualifying hardware validate that the software path meets performance targets.

## Integration Points

### Depends on

| Dependency | What OBJ-074 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class: creates instance with `OrchestratorConfig`, calls `render()`, consumes `OrchestratorResult` (timing, captureStats, encoderResult, rendererInfo, warnings). Uses `RenderProgress` from `onProgress` callback for per-frame timing. |
| **OBJ-049** (Software Rendering Config) | `resolveRenderingConfig()` to determine Chromium launch args. `probeWebGLRenderer()` to populate `webglInfo` (or reads equivalent data from `OrchestratorResult.rendererInfo`). `GpuMode` type. `WebGLRendererInfo` type. |
| **OBJ-016** (Manifest Loader) — transitive via OBJ-035 | `loadManifest()` for validating the generated reference manifest. |
| **OBJ-004** (Manifest Schema) — transitive via OBJ-035 | `ManifestRegistry`, `createRegistry()` for setting up validation. |
| **OBJ-005** (Geometry Registry) — transitive via OBJ-035 | `getGeometryRegistry()` to resolve stage geometry. |
| **OBJ-006** (Camera Registry) — transitive via OBJ-035 | Camera registry for resolving `slow_push_forward`. |
| **OBJ-018** (Stage Geometry) — transitive via OBJ-005 | The `stageGeometry` definition with its slots. The benchmark's reference manifest is built around this geometry. |
| **OBJ-012** (Frame Capture) — transitive via OBJ-035 | `CaptureStats` type for capture timing data. |
| **OBJ-013** (FFmpeg Encoder) — transitive via OBJ-035 | `FFmpegEncoderResult` for encoder stats. |

### Consumed by

| Downstream | How it uses OBJ-074 |
|---|---|
| **OBJ-073** (Docker integration) | Runs the benchmark inside a Docker container to validate C-11 + C-08 combined (software WebGL in Docker meets performance targets). |
| **CI pipeline** | Runs scaled-down benchmark on every PR. Full benchmark on qualifying hardware nightly or on-demand. |
| **OBJ-082** (Parallel rendering) | Uses OBJ-074's report format as a baseline. Parallel rendering benchmarks extend the same `BenchmarkReport` structure with multi-instance metrics. |
| **Human operators** | Run `runBenchmark()` on target deployment hardware to verify C-08 compliance before deploying to production. |

### File Placement

```
depthkit/
  src/
    benchmark/
      runner.ts                    # NEW — BenchmarkConfig, BenchmarkReport,
                                   #       ComplianceResult, EnvironmentInfo,
                                   #       TimingResults, FrameTiming,
                                   #       BenchmarkError, runBenchmark(),
                                   #       runComparisonBenchmark(),
                                   #       formatBenchmarkReport(),
                                   #       getReferenceBenchmarkParameters(),
                                   #       generateReferenceManifest(),
                                   #       generateBenchmarkAssets()
      fixtures/
        generate-assets.ts         # NEW — internal: solid-color PNG generation
  test/
    unit/
      benchmark-runner.test.ts     # NEW — unit tests (statistics, compliance, format)
    integration/
      benchmark-runner.test.ts     # NEW — integration tests (scaled-down renders)
```

## Open Questions

### OQ-A: Should the benchmark runner be exposed as a CLI subcommand?

OBJ-046 (CLI) is verified. Adding a `depthkit benchmark` subcommand would make benchmarks easier to run manually. However, OBJ-046's spec would need updating. For now, the benchmark is invocable programmatically via `runBenchmark()`. A CLI wrapper can be added later as a thin shell script or via OBJ-083 (extended CLI, which is open).

### OQ-B: Should the benchmark support custom manifests?

The current spec only supports the canonical reference manifest. Supporting arbitrary manifests would allow benchmarking specific scene types (e.g., "how fast does a 5-scene tunnel video render?"). This could be added via an optional `manifest` override in `BenchmarkConfig`, but the compliance assessment would only be meaningful against the reference parameters. Defer — custom manifest benchmarking can use the Orchestrator directly and measure `OrchestratorResult` timings manually.

### OQ-C: Per-component frame timing breakdown

The current design captures total frame time but cannot decompose it into render/capture/encode per frame. OBJ-012's `CaptureStats` provides aggregate capture timing. OBJ-013's `FFmpegEncoderResult` provides aggregate encode timing. Per-frame breakdown would require either: (a) extending OBJ-035's `onProgress` with per-component timings, or (b) instrumenting the page protocol. Neither is in scope for V1. The aggregate breakdown (capture total / encode total / render total = orchestrator total - capture total - encode total) is sufficient for identifying which component is the bottleneck.

### OQ-D: Regression threshold for CI gating

Should the benchmark define a "regression threshold" (e.g., "fail CI if average frame time increases by more than 10% compared to baseline")? This requires storing a baseline report and comparing against it. Useful but adds complexity. Defer — for V1, the benchmark reports raw numbers and the human decides if a regression has occurred.

### OQ-E: WebGLRendererInfo mapping from OrchestratorResult.rendererInfo

`OrchestratorResult.rendererInfo` (from OBJ-010) has type `RendererInfo` with fields: `initialized`, `canvasSize`, `webglVersion`, `vendor`, `gpuRenderer`, `maxTextureSize`, `antialias`. OBJ-049's `WebGLRendererInfo` has different fields: `renderer`, `vendor`, `version`, `isSoftwareRenderer`, `maxTextureSize`, `maxViewportDims`. The benchmark needs to map between these or call `probeWebGLRenderer()` directly. The simplest approach: call `probeWebGLRenderer()` from within the benchmark setup (after the orchestrator launches the browser but before the render loop — or more practically, run it as a pre-render step using a separate short-lived bridge, or after the render). Since OBJ-035's `render()` doesn't expose the bridge, the benchmark should either: (a) use OBJ-035's `rendererInfo` and construct a partial `WebGLRendererInfo` from it, or (b) call `probeWebGLRenderer()` separately. Decision: use `OrchestratorResult.rendererInfo` and construct a best-effort `WebGLRendererInfo`-compatible object. The `isSoftwareRenderer` field can be derived by checking if `rendererInfo.gpuRenderer` contains "SwiftShader"/"llvmpipe"/"softpipe" (same heuristic as OBJ-049 D7).

---

I believe this spec is comprehensive. I'd like the Challenger to review and verify. Key points for attention:

1. The benchmark is fully self-contained (no external assets)
2. It uses OBJ-035's Orchestrator as-is — no modifications to dependencies
3. Per-frame timing is derived from `onProgress` deltas, not from instrumenting internals
4. Compliance thresholds are hardcoded to match seed constraints exactly
5. The comparison benchmark gracefully handles missing GPUs
6. Statistical percentiles enable jitter detection beyond simple averages

---

## Round 2 — spec_challenger

I need to verify some details about the stage geometry slots and the orchestrator's rendererInfo type to check claims in the proposed spec.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "offset": 1,
  "limit": 120
}
[Tool Result]      1→# Specification: Stage Scene Geometry (OBJ-018)
     2→
     3→## Summary
     4→
     5→OBJ-018 defines the **stage** scene geometry — the default, most fundamental geometry in depthkit. It represents a classic "subject in front of a background" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/stage.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The stage scene g... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "slots|SlotName|backdrop|sky|midground|floor|subject|near_fg",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "output_mode": "content"
}
[Tool Result] 5:[Omitted long matching line]
19: * Spatial arrangement: a large backdrop plane at deep Z, a floor
21: * subject plane at shallow Z. Optional sky, midground, and
22: * near_fg planes provide additional depth layering.
24: * Classic "subject in front of a background" setup with real
25: * perspective on the floor. The floor's perspective foreshortening
39:| `description` | `'A classic subject-in-front-of-background setup. Large backdrop at depth, angled floor plane with real perspective foreshortening, and a subject plane at shallow Z. The most versatile geometry for general-purpose scenes.'` | Describes the spatial feel per OBJ-005's `description` contract |
42:| `fog` | `{ color: '#000000', near: 20, far: 60 }` | Subtle atmospheric fade on distant planes. `near: 20` leaves the subject (Z=-5, ~10 units from camera) completely unaffected. `far: 60` fades the sky plane gently. |
47:The stage geometry defines **6 slots** — 3 required, 3 optional. This follows the standard layered depth a... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "RendererInfo|rendererInfo|webglVersion|gpuRenderer",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "output_mode": "content"
}
[Tool Result] 50:   * - webglVersion: gl.getParameter(gl.VERSION) where gl = renderer.getContext()
51:   * - vendor / gpuRenderer: obtained via WEBGL_debug_renderer_info extension.
55:   *     gpuRenderer = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown';
60:  getRendererInfo(): RendererInfo;
159:interface RendererInfo {
165:  webglVersion: string;
169:  gpuRenderer: string;
270: * Diagnostic info returned by the page's getRendererInfo() function.
272:export interface RendererInfo {
275:  webglVersion: string;
277:  gpuRenderer: string;
367:**Decision:** The `WebGLRenderer` is created without forcing a specific WebGL version. Three.js defaults to WebGL 2 when available, falls back to WebGL 1. `getRendererInfo()` reports the acquired version.
381:- [ ] **AC-02:** `src/page/scene-renderer.js` imports Three.js, creates a `WebGLRenderer` bound to `#depthkit-canvas` during `init()`, and exposes `window.depthkit` with `init`, `dispose`, `isInitialized`, `getRendererInfo`, and `renderFrame` ... [truncated]
Now I have the full picture. Let me review the proposed spec systematically.

---

## Review: OBJ-074 — Performance Benchmark Plan

### What's Sound

- **Self-contained benchmark with generated assets** — correct approach. No external dependencies for reproducibility.
- **Using OBJ-035's Orchestrator as-is** — respects objective boundaries. No modifications to dependencies.
- **Per-frame timing via `onProgress` deltas** — pragmatic given that the orchestrator doesn't expose internals. D4 is well-reasoned.
- **Statistical percentiles** — median, p95, p99 are the right metrics for jitter detection. Average alone would mask GC pauses.
- **Compliance thresholds as hardcoded constants (D3)** — correct. These are seed constraints, not tunable knobs.
- **Comparison benchmark graceful degradation (D6)** — good design. Software-only environments shouldn't crash the comparison.
- **BenchmarkError with structured codes** — follows the pattern established by OrchestratorError.
- **formatBenchmarkReport()** — good for human consumption; the example output makes the intent unambiguous.
- **CSV output for frame timings** — simple, universal, diffable. Right choice.

### Issues

---

**Issue 1 (MAJOR): `planesPerScene: 5` contradicts the actual stage geometry slot count**

OBJ-018 defines the stage geometry with **6 slots**: `sky`, `backdrop`, `floor`, `midground`, `subject`, `near_fg` (3 required + 3 optional). AC-05 lists all 6 slot types as having generated images. But `BenchmarkParameters.planesPerScene` is `5`.

C-08 says "5 textured planes per scene." Using all 6 stage slots produces 6 planes — a stricter test, which is fine for compliance. But the `planesPerScene` field must match what the manifest actually uses. If the manifest populates all 6 slots, the field should say 6. If the benchmark intentionally omits one optional slot to hit exactly 5, that should be stated and AC-05 updated.

**Proposed fix:** Set `planesPerScene: 6` and add a note: "Exceeds C-08's 5-plane minimum, providing a stricter benchmark. All 6 stage slots (3 required + 3 optional) are populated." Update AC-01 accordingly.

---

**Issue 2 (MAJOR): `compliance.c08.measuredMs` description contradicts AC-17**

In the `ComplianceResult` type definition:
```typescript
c08: {
    measuredMs: number;  // "The measured render loop time in ms"
}
```

But AC-17 says: `compliance.c08.passed === true` when `timing.orchestratorTotalMs < 900000`.

These are different measurements. `renderLoopMs` is just the frame loop; `orchestratorTotalMs` includes validation, browser launch, scene setup, and FFmpeg finalization.

C-08 says the video "must render in under 15 minutes." The user experiences the total pipeline time, not just the frame loop. I believe `orchestratorTotalMs` is the correct measure (it's what OBJ-035 AC-30 says to measure).

**Proposed fix:** Change the `measuredMs` JSDoc comment to "The measured orchestrator total time in ms (includes validation, setup, render loop, finalization)" to match AC-17. Or if you intended to use render loop time, update AC-17 to check `timing.renderLoopMs`. Pick one, make it consistent.

---

**Issue 3 (MAJOR): `webglInfo` type mismatch left as OQ instead of design decision**

`BenchmarkReport.webglInfo` is typed as `WebGLRendererInfo` (from OBJ-049), but the only renderer info available at benchmark time comes from `OrchestratorResult.rendererInfo`, which is `RendererInfo` (from OBJ-010). These types are incompatible:

- OBJ-010 `RendererInfo`: `{ initialized, canvasSize, webglVersion, vendor, gpuRenderer, maxTextureSize, antialias }`
- OBJ-049 `WebGLRendererInfo`: `{ renderer, vendor, version, isSoftwareRenderer, maxTextureSize, maxViewportDims }`

OQ-E acknowledges this but doesn't resolve it. An implementer **must** decide how to get/construct this data. This is not an open question — it's a blocking design decision.

**Proposed fix:** Promote OQ-E to a design decision. The simplest approach: change `BenchmarkReport.webglInfo` to type `RendererInfo` (from OBJ-010) since that's what `OrchestratorResult.rendererInfo` provides. Add a derived boolean field `isSoftwareRenderer` that applies OBJ-049 D7's heuristic (check if `rendererInfo.gpuRenderer` contains "SwiftShader", "llvmpipe", or "softpipe"). This avoids constructing a fake `WebGLRendererInfo` from incomplete data.

The new type section would look like:
```typescript
/** WebGL renderer info from OrchestratorResult.rendererInfo (OBJ-010). */
rendererInfo: RendererInfo;

/** Whether the renderer is software-based, derived from 
 *  rendererInfo.gpuRenderer using OBJ-049 D7's heuristic. */
isSoftwareRenderer: boolean;
```

AC-26 should then reference `rendererInfo` instead of `webglInfo`.

---

**Issue 4 (MINOR): `generateReferenceManifest()` returns `Record<string, unknown>`**

This type is too loose. The function generates a known, fixed manifest structure. It should return the `Manifest` type from OBJ-004. If the reason is that `OrchestratorConfig.manifest` accepts `unknown`, that's the consumer's concern — the generator should be precise about what it produces. A typed return lets unit tests check manifest structure without casting.

**Proposed fix:** Return type `Manifest` (imported from `../manifest/schema.js`). The function constructs a valid manifest and can return it typed.

---

**Issue 5 (MINOR): `BenchmarkReport.version` source unspecified**

The JSDoc says "Matches depthkit package version" but doesn't specify how to obtain it. An implementer would have to guess: read `package.json`? Import a version constant? Hardcode?

**Proposed fix:** Add to D10 or a new D12: "The benchmark version is read from the `version` field of `depthkit/package.json`. The implementation reads and parses this file at benchmark start."

---

**Issue 6 (MINOR): Image generation approach not committed**

D8 says "sharp if available, or raw PNG construction via zlib." An implementer must choose. For reproducibility, the spec should commit.

**Proposed fix:** Commit to one approach. If `sharp` is expected in the dependency tree (seed Section 4.8 references "Sharp-based chroma key"), say "uses `sharp` to generate solid-color PNGs." If you want zero additional deps, say "constructs minimal valid PNGs using Node.js `zlib` — no image library required." I'd lean toward the zlib approach since it avoids a native dependency just for test assets.

---

**Issue 7 (MINOR): `runComparisonBenchmark` doesn't handle SwiftShader fallback in hardware mode**

If there's no GPU, Chromium with hardware flags silently falls back to SwiftShader (per OBJ-049 D4). The "hardware" benchmark would actually run on SwiftShader — the comparison becomes software-with-explicit-flags vs. software-with-hardware-flags, which is meaningless.

The spec already captures `gpuMode.actual` in each report, so the data is there. But the comparison report doesn't flag this scenario.

**Proposed fix:** Add to `ComparisonReport`:
```typescript
/** True if hardware mode was requested but the actual backend was software.
 *  When true, speedupRatio reflects flag-configuration differences, not 
 *  GPU vs CPU performance. */
hardwareFellBackToSoftware: boolean;
```
Set this when `hardware.gpuMode.actual === 'software'`. The `formatComparisonReport()` should note this clearly.

---

**Issue 8 (MINOR): Scene `start_time` values not explicit in the manifest description**

The spec says "5 consecutive scenes, each 12 seconds" but doesn't state the `start_time` values. These should be `0, 12, 24, 36, 48`. Cut transitions with no overlap means each scene starts exactly when the previous ends. This is inferrable but should be explicit since manifest validation (OBJ-016) checks scene timing.

**Proposed fix:** In D2 or in the `generateReferenceManifest()` JSDoc, add: "Scene start times are `[0, 12, 24, 36, 48]` seconds — consecutive with no overlap or gap."

---

### Summary

Three **major** issues and five **minor** issues. All are fixable without structural changes. The overall design is solid — the spec correctly scopes the benchmark as a consumer of OBJ-035 and OBJ-049, the statistical approach is appropriate, and the compliance assessment directly maps to seed constraints. Please revise and I'll verify.

---

## Round 3 — spec_author

All eight issues are valid. Here's the revised spec with every issue addressed:

---

# Specification: OBJ-074 — Performance Benchmark Plan

## Summary

OBJ-074 delivers a **benchmark runner module** (`src/benchmark/runner.ts`) and a **reference benchmark manifest** that together provide a reproducible procedure for measuring depthkit's rendering performance. The benchmark measures per-frame timing breakdown, compares software WebGL vs. GPU acceleration, identifies bottlenecks, and validates compliance with C-08 (60-second, 30fps, 5-plane video renders in under 15 minutes on a 4-core VPS) and TC-02 (under 500ms per frame with software WebGL). The benchmark is invocable programmatically and produces a structured `BenchmarkReport` JSON for analysis, regression tracking, and CI gating.

## Interface Contract

### Module: `src/benchmark/runner.ts`

```typescript
import type { OrchestratorResult, RenderProgress } from '../engine/orchestrator.js';
import type { RendererInfo } from '../page/protocol-types.js';
import type { CaptureStats } from '../engine/frame-capture.js';
import type { GpuMode } from '../engine/rendering-config.js';
import type { ManifestRegistry, Manifest } from '../manifest/schema.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

// ────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────

/**
 * Configuration for a benchmark run.
 */
export interface BenchmarkConfig {
  /**
   * GPU rendering mode for this benchmark run.
   * Default: 'software' (C-11 baseline).
   */
  gpuMode?: GpuMode;

  /**
   * Output directory for benchmark artifacts:
   * - report JSON file
   * - rendered MP4 (retained for manual inspection)
   * - per-frame timing CSV (when collectFrameTimings is true)
   *
   * Created if it doesn't exist.
   * Default: './benchmark-results'
   */
  outputDir?: string;

  /**
   * Whether to collect per-frame timing data.
   * When true, the benchmark records individual frame durations
   * and writes a CSV file alongside the report.
   *
   * Adds marginal overhead (~0.1ms/frame for timestamp collection).
   * Default: true
   */
  collectFrameTimings?: boolean;

  /**
   * Path to FFmpeg binary. Default: resolved via resolveFFmpegPath().
   */
  ffmpegPath?: string;

  /**
   * Path to Chromium executable. Default: Puppeteer's bundled Chromium.
   */
  chromiumPath?: string;

  /**
   * The manifest registry for validation.
   * If not provided, the benchmark runner creates a default registry
   * populated with the reference geometry and camera registrations.
   */
  registry?: ManifestRegistry;

  /**
   * The geometry registry. If not provided, uses getGeometryRegistry().
   */
  geometryRegistry?: GeometryRegistry;

  /**
   * The camera path registry. If not provided, uses the default
   * camera registry from OBJ-006.
   */
  cameraRegistry?: CameraPathRegistry;

  /**
   * Progress callback. Forwarded to Orchestrator's onProgress.
   * Return false to cancel the benchmark.
   */
  onProgress?: (progress: RenderProgress) => boolean | void;
}

// ────────────────────────────────────────────
// Reference Manifest
// ────────────────────────────────────────────

/**
 * The canonical benchmark parameters, matching C-08 and TC-02
 * requirements exactly. Used by the reference manifest generator
 * and documented in the benchmark report for reproducibility.
 */
export interface BenchmarkParameters {
  /** Output resolution width. Reference: 1920 */
  width: number;
  /** Output resolution height. Reference: 1080 */
  height: number;
  /** Frames per second. Reference: 30 */
  fps: number;
  /** Total video duration in seconds. Reference: 60 */
  durationSeconds: number;
  /** Total frame count (fps * durationSeconds). Reference: 1800 */
  totalFrames: number;
  /** Number of scenes. Reference: 5 */
  sceneCount: number;
  /**
   * Planes per scene. Reference: 6.
   * The stage geometry defines 6 slots (sky, backdrop, floor,
   * midground, subject, near_fg). All 6 are populated, exceeding
   * C-08's 5-plane minimum for a stricter benchmark.
   */
  planesPerScene: number;
  /** Geometry used. Reference: 'stage' */
  geometry: string;
  /** Camera preset used. Reference: 'slow_push_forward' */
  cameraPreset: string;
}

/**
 * Returns the canonical benchmark parameters as a frozen object.
 * These match C-08 and TC-02 exactly:
 * - 1920x1080, 30fps, 60 seconds = 1800 frames
 * - 5 scenes × 12 seconds each (start_times: 0, 12, 24, 36, 48)
 * - 6 planes per scene (all 6 stage slots populated)
 * - 'stage' geometry with 'slow_push_forward' camera
 */
export function getReferenceBenchmarkParameters(): Readonly<BenchmarkParameters>;

/**
 * Generates the reference benchmark manifest as a typed Manifest object.
 *
 * The manifest contains 5 consecutive scenes at start_times
 * [0, 12, 24, 36, 48] seconds, each 12 seconds, using the
 * 'stage' geometry with all 6 slots populated (sky, backdrop,
 * floor, midground, subject, near_fg). Uses procedurally
 * generated solid-color PNG test images (no external asset
 * dependencies).
 *
 * The manifest uses 'cut' transitions between scenes to isolate
 * render performance from transition compositing overhead.
 * No audio (isolates video rendering performance).
 *
 * @returns A validated Manifest object ready to pass to Orchestrator.
 */
export function generateReferenceManifest(): Manifest;

/**
 * Generates solid-color PNG test images for the benchmark manifest
 * and writes them to the specified directory.
 *
 * Creates one image per unique slot across all scenes. Images are
 * 1920x1080 solid-color PNGs constructed using Node.js `zlib`
 * (no image library dependency). One distinct color per slot type:
 * sky=deep blue (#001133), backdrop=dark green (#003311),
 * midground=brown (#553311), floor=gray (#444444),
 * subject=red (#CC0000), near_fg=semi-transparent white
 * (rgba 255,255,255,128).
 *
 * Subject and near_fg images include alpha channels (RGBA with
 * a centered colored rectangle on transparent background) to
 * exercise the alpha texture path.
 *
 * @param outputDir - Directory to write images. Created if missing.
 * @returns Map of slot-relative paths (as used in the manifest)
 *          to absolute file paths on disk.
 */
export function generateBenchmarkAssets(
  outputDir: string
): Promise<Map<string, string>>;

// ────────────────────────────────────────────
// Per-Frame Timing
// ────────────────────────────────────────────

/**
 * Timing breakdown for a single frame.
 * Collected via the onProgress callback's elapsed time deltas.
 */
export interface FrameTiming {
  /** Frame number (zero-indexed). */
  frame: number;
  /** Total wall-clock time for this frame in ms (from previous
   *  frame completion to this frame's completion). For frame 0,
   *  this is the time from render loop start to first frame
   *  completion. */
  totalMs: number;
  /** Scene ID(s) active for this frame. */
  activeSceneIds: string[];
}

// ────────────────────────────────────────────
// Benchmark Report
// ────────────────────────────────────────────

/**
 * Structured benchmark report produced by runBenchmark().
 * Serializable to JSON for storage and regression comparison.
 */
export interface BenchmarkReport {
  /** ISO 8601 timestamp when the benchmark started. */
  timestamp: string;

  /**
   * Benchmark runner version. Read from the `version` field
   * of depthkit's package.json at benchmark start.
   */
  version: string;

  /** The benchmark parameters used. */
  parameters: BenchmarkParameters;

  /** Environment information for reproducibility. */
  environment: EnvironmentInfo;

  /**
   * Renderer info from OrchestratorResult.rendererInfo (OBJ-010).
   * Contains initialized, canvasSize, webglVersion, vendor,
   * gpuRenderer, maxTextureSize, antialias.
   */
  rendererInfo: RendererInfo;

  /**
   * Whether the renderer is software-based, derived from
   * rendererInfo.gpuRenderer using OBJ-049 D7's heuristic:
   * checks if gpuRenderer contains "SwiftShader", "llvmpipe",
   * or "softpipe" (case-insensitive). False if gpuRenderer is
   * 'unknown' or unrecognized.
   */
  isSoftwareRenderer: boolean;

  /** GPU mode requested and what was actually used. */
  gpuMode: {
    requested: GpuMode;
    /** 'software' if isSoftwareRenderer is true, 'hardware' otherwise. */
    actual: 'software' | 'hardware';
  };

  /** Aggregate timing results. */
  timing: TimingResults;

  /** Frame capture statistics from OBJ-012's CaptureStats. */
  captureStats: CaptureStats;

  /** Per-frame timings. Present only when collectFrameTimings is true. */
  frameTimings?: FrameTiming[];

  /** Pass/fail assessment against C-08 and TC-02. */
  compliance: ComplianceResult;

  /** Path to the rendered MP4 file (for manual inspection). */
  outputVideoPath: string;

  /** Path to the per-frame CSV file. null if not collected. */
  frameTimingsCsvPath: string | null;
}

/**
 * System environment information captured at benchmark start.
 */
export interface EnvironmentInfo {
  /** Node.js version string (process.version). */
  nodeVersion: string;

  /** OS platform (process.platform). */
  platform: string;

  /** OS architecture (process.arch). */
  arch: string;

  /** CPU model string (first entry from os.cpus()). */
  cpuModel: string;

  /** Number of CPU cores (os.cpus().length). */
  cpuCores: number;

  /** Total system memory in MB (os.totalmem() / 1024 / 1024). */
  totalMemoryMb: number;

  /** Free memory at benchmark start in MB. */
  freeMemoryMb: number;

  /** FFmpeg version string (from ffmpeg -version, first line). */
  ffmpegVersion: string;

  /** Chromium version string (from browser.version()). */
  chromiumVersion: string;
}

/**
 * Aggregate timing results.
 */
export interface TimingResults {
  /** Total wall-clock time for the entire benchmark run in ms.
   *  Includes asset generation, validation, rendering, finalization.
   *  From runBenchmark() entry to report generation. */
  totalBenchmarkMs: number;

  /** Wall-clock time for the render loop only in ms.
   *  Maps to OrchestratorResult.renderDurationMs. */
  renderLoopMs: number;

  /**
   * Wall-clock time for the full orchestrator in ms.
   * Maps to OrchestratorResult.totalDurationMs.
   * Includes validation, browser launch, scene setup,
   * render loop, FFmpeg finalization.
   * THIS is the value compared against C-08's 15-minute threshold.
   */
  orchestratorTotalMs: number;

  /** Average time per frame in ms.
   *  Maps to OrchestratorResult.averageFrameMs.
   *  THIS is the value compared against TC-02's 500ms threshold. */
  averageFrameMs: number;

  /** Median time per frame in ms.
   *  Computed from per-frame timings. null if collectFrameTimings
   *  is false. */
  medianFrameMs: number | null;

  /** 95th percentile frame time in ms. null if not collected. */
  p95FrameMs: number | null;

  /** 99th percentile frame time in ms. null if not collected. */
  p99FrameMs: number | null;

  /** Maximum single-frame time in ms. null if not collected. */
  maxFrameMs: number | null;

  /** Minimum single-frame time in ms. null if not collected. */
  minFrameMs: number | null;

  /** Standard deviation of frame times in ms. null if not collected. */
  stddevFrameMs: number | null;

  /** Throughput: frames rendered per wall-clock second.
   *  totalFrames / (renderLoopMs / 1000). */
  throughputFps: number;

  /** Asset generation time in ms (generating test PNGs). */
  assetGenerationMs: number;

  /** Capture-only aggregate time from CaptureStats.totalCaptureMs. */
  totalCaptureMs: number;

  /** Average capture time from CaptureStats.averageCaptureMs. */
  averageCaptureMs: number;
}

/**
 * Pass/fail compliance assessment.
 */
export interface ComplianceResult {
  /** C-08: Total orchestrator time < 15 minutes (900,000ms). */
  c08: {
    /** Whether the benchmark passed C-08. */
    passed: boolean;
    /** The threshold in ms. Always 900000. */
    thresholdMs: number;
    /** The measured orchestrator total time in ms
     *  (timing.orchestratorTotalMs). */
    measuredMs: number;
    /** Headroom: (thresholdMs - measuredMs) / thresholdMs as ratio.
     *  Negative when threshold is exceeded. */
    headroom: number;
  };
  /** TC-02: Average frame time < 500ms. */
  tc02: {
    /** Whether the benchmark passed TC-02. */
    passed: boolean;
    /** The threshold in ms. Always 500. */
    thresholdMs: number;
    /** The measured average frame time in ms
     *  (timing.averageFrameMs). */
    measuredMs: number;
    /** Headroom ratio. Negative when threshold is exceeded. */
    headroom: number;
  };
}

// ────────────────────────────────────────────
// Runner
// ────────────────────────────────────────────

/**
 * Executes the reference benchmark and produces a BenchmarkReport.
 *
 * Procedure:
 * 1. Collect environment info (Node version, OS, CPU, memory,
 *    FFmpeg version).
 * 2. Generate solid-color test images to a temp directory inside
 *    outputDir via generateBenchmarkAssets().
 * 3. Generate the reference manifest via generateReferenceManifest(),
 *    with image paths pointing to the generated assets.
 * 4. Resolve rendering config via OBJ-049's resolveRenderingConfig().
 * 5. Create Orchestrator with the manifest, registries, and config.
 * 6. Attach onProgress handler that records per-frame timings
 *    (if collectFrameTimings is true) and forwards to caller's
 *    onProgress.
 * 7. Call orchestrator.render().
 * 8. Extract rendererInfo from OrchestratorResult.rendererInfo.
 *    Derive isSoftwareRenderer by checking if gpuRenderer contains
 *    "SwiftShader", "llvmpipe", or "softpipe" (case-insensitive).
 * 9. Compute aggregate statistics (median, p95, p99, stddev)
 *    from per-frame timings.
 * 10. Assess C-08 and TC-02 compliance.
 * 11. Read version from depthkit/package.json.
 * 12. Write report JSON to outputDir/benchmark-report.json.
 * 13. Write per-frame CSV to outputDir/frame-timings.csv (if collected).
 * 14. Return the BenchmarkReport.
 *
 * The benchmark does NOT clean up the outputDir — the rendered
 * MP4 and report are retained for manual inspection and regression
 * comparison.
 *
 * @throws BenchmarkError if the render fails or environment
 *         collection fails.
 */
export function runBenchmark(
  config?: BenchmarkConfig
): Promise<BenchmarkReport>;

/**
 * Runs the benchmark twice (once in software mode, once in hardware
 * mode) and produces a comparison report.
 *
 * Software mode runs first (always succeeds on any machine).
 * If hardware mode fails (e.g., no GPU available, browser crash),
 * the hardware result is null and the comparison report documents
 * the failure.
 *
 * If hardware mode launches but Chromium silently falls back to
 * SwiftShader (no GPU drivers available), the hardware run completes
 * successfully but hardwareFellBackToSoftware is set to true,
 * indicating that the speedupRatio reflects flag-configuration
 * differences rather than GPU vs. CPU performance.
 *
 * @returns A comparison of software vs. hardware results.
 */
export function runComparisonBenchmark(
  config?: Omit<BenchmarkConfig, 'gpuMode'>
): Promise<ComparisonReport>;

/**
 * Comparison report for software vs. hardware benchmark runs.
 */
export interface ComparisonReport {
  /** Software rendering results. Always present. */
  software: BenchmarkReport;

  /** Hardware rendering results. null if hardware mode failed
   *  (browser crash, launch failure). */
  hardware: BenchmarkReport | null;

  /** If hardware run failed, the error message. */
  hardwareError?: string;

  /**
   * True if hardware mode was requested but the actual backend
   * was software (Chromium fell back to SwiftShader).
   * When true, speedupRatio reflects flag-configuration
   * differences, not GPU vs. CPU performance. False if hardware
   * is null (didn't run at all).
   */
  hardwareFellBackToSoftware: boolean;

  /** Speedup ratio: software.timing.renderLoopMs / hardware.timing.renderLoopMs.
   *  null if hardware is unavailable. >1.0 means hardware is faster. */
  speedupRatio: number | null;

  /** Per-frame comparison summary. null if either lacks frame timings. */
  frameSummary: {
    softwareAvgMs: number;
    hardwareAvgMs: number | null;
    softwareP95Ms: number;
    hardwareP95Ms: number | null;
  } | null;
}

// ────────────────────────────────────────────
// Error
// ────────────────────────────────────────────

export type BenchmarkErrorCode =
  | 'ENVIRONMENT_PROBE_FAILED'
  | 'ASSET_GENERATION_FAILED'
  | 'RENDER_FAILED'
  | 'REPORT_WRITE_FAILED'
  ;

export class BenchmarkError extends Error {
  readonly code: BenchmarkErrorCode;
  readonly cause?: Error;

  constructor(
    code: BenchmarkErrorCode,
    message: string,
    cause?: Error
  );
}

// ────────────────────────────────────────────
// Utility
// ────────────────────────────────────────────

/**
 * Formats a BenchmarkReport as a human-readable summary string.
 * Suitable for terminal output or logging.
 *
 * Example output:
 * ```
 * ═══════════════════════════════════════════
 *  DEPTHKIT PERFORMANCE BENCHMARK
 * ═══════════════════════════════════════════
 *  Parameters: 1920x1080, 30fps, 60s (1800 frames)
 *  Geometry: stage (6 planes) × 5 scenes
 *  GPU Mode: software (SwiftShader)
 * ───────────────────────────────────────────
 *  TIMING
 *  Orchestrator total: 582,340 ms  (9m 42s)
 *  Render loop:        540,120 ms  (9m 00s)
 *  Avg frame:             300 ms
 *  Median frame:          295 ms
 *  P95 frame:             390 ms
 *  P99 frame:             465 ms
 *  Throughput:           3.33 fps
 *  Capture avg:           142 ms
 * ───────────────────────────────────────────
 *  COMPLIANCE
 *  C-08 (< 15 min):     ✅ PASS  (headroom: 35.3%)
 *  TC-02 (< 500ms/fr):  ✅ PASS  (headroom: 40.0%)
 * ───────────────────────────────────────────
 *  ENVIRONMENT
 *  Node: v20.11.0 | Linux x64
 *  CPU: Intel Xeon E-2236 (4 cores)
 *  Memory: 4096 MB total, 2847 MB free
 *  Chromium: 121.0.6167.85
 *  FFmpeg: 6.1.1
 *  WebGL: SwiftShader (software)
 * ═══════════════════════════════════════════
 * ```
 */
export function formatBenchmarkReport(report: BenchmarkReport): string;

/**
 * Formats a ComparisonReport as a human-readable summary.
 * When hardwareFellBackToSoftware is true, includes a warning:
 * "⚠ Hardware mode fell back to SwiftShader — comparison is
 *  not GPU vs CPU."
 */
export function formatComparisonReport(report: ComparisonReport): string;
```

### Per-Frame CSV Format

```
frame,totalMs,activeSceneIds
0,328.4,"scene_001"
1,315.2,"scene_001"
...
359,312.1,"scene_001"
360,487.3,"scene_002"
...
```

All frames have a single scene ID since the reference manifest uses `cut` transitions.

## Design Decisions

### D1: Self-Contained Benchmark With No External Assets

**Decision:** The benchmark generates its own solid-color PNG test images programmatically using Node.js `zlib` (raw RGBA buffer + deflate compression to produce valid PNG files). No image library dependency (no `sharp`, no `canvas`). No external image files, no network downloads, no asset pipeline dependencies.

**Rationale:** C-08 and TC-02 measure the rendering pipeline's performance, not asset loading speed. Self-contained assets ensure the benchmark is reproducible on any machine without setup. Solid-color PNGs are trivially small but exercise the full texture → plane → WebGL → capture → FFmpeg pipeline. The `zlib` approach adds zero native dependencies — constructing a valid PNG from raw RGBA data + zlib deflate is ~50 lines of straightforward Node.js. Subject and near_fg images include alpha channels (RGBA with a centered colored rectangle on transparent background) to exercise the transparency path common in production.

### D2: Reference Manifest Uses `stage` Geometry With Cut Transitions

**Decision:** The reference manifest uses the `stage` geometry (verified in OBJ-018) with `slow_push_forward` camera (verified in OBJ-026), 5 scenes × 12 seconds each, cut transitions only. Scene start times are `[0, 12, 24, 36, 48]` seconds — consecutive with no overlap or gap. All 6 stage geometry slots (sky, backdrop, floor, midground, subject, near_fg) are populated, exceeding C-08's 5-plane minimum for a stricter benchmark.

**Rationale:**
- `stage` is the most representative geometry — 6 slots (3 required + 3 optional), verified status.
- `slow_push_forward` is the default camera for stage, exercises camera interpolation per frame.
- Cut transitions isolate render performance from transition compositing. Transition performance is a separate concern.
- 5 scenes × 12 seconds = 60 seconds exactly, matching C-08.
- No audio — audio muxing is a trivial FFmpeg `-c:v copy` pass that doesn't test rendering performance.
- Consecutive scenes with no gaps or overlaps produce the simplest timing model.

### D3: Compliance Thresholds Are Constants, Not Configurable

**Decision:** C-08 threshold (15 minutes = 900,000ms) and TC-02 threshold (500ms/frame) are hardcoded constants, not configurable parameters.

**Rationale:** These are seed constraints. Making them configurable invites drift from the spec. The `BenchmarkReport` includes raw measurements; consumers can apply their own thresholds for regression tracking.

### D4: Per-Frame Timing via `onProgress` Callback Deltas

**Decision:** Per-frame timing is computed by recording `performance.now()` timestamps on each `onProgress` invocation and computing deltas between consecutive calls. Frame N's duration = `elapsedMs[N] - elapsedMs[N-1]` (for frame 0: `elapsedMs[0]` from the `RenderProgress` directly, which represents time since render loop start).

**Rationale:** OBJ-035's `RenderProgress.elapsedMs` provides cumulative elapsed time. Deltas capture the full frame pipeline cost (render + capture + encode write) without modifying the orchestrator.

**Limitation:** This measures total frame time, not the render/capture/encode breakdown per frame. Per-component breakdown per frame would require instrumenting OBJ-035 or OBJ-012 internals — out of scope. The aggregate breakdown (capture total from `CaptureStats`, encode total approximated from FFmpegEncoderResult, render total as the remainder) is sufficient for identifying which component is the primary bottleneck.

### D5: Report Is JSON — Not a Database

**Decision:** The benchmark report is a self-contained JSON file written to the output directory. No database, no time-series store.

**Rationale:** The benchmark is run manually or in CI. JSON is diffable, committable, and parseable by any tool. Regression comparison is done by diffing two report JSONs. A time-series database is premature for V1.

### D6: Comparison Benchmark Is Tolerant of Hardware Failure

**Decision:** `runComparisonBenchmark()` always runs software mode first. If hardware mode fails (no GPU, driver error, browser crash), it returns `hardware: null` with the error captured. It does not throw.

**Rationale:** Most development and CI environments lack a GPU. The comparison should degrade gracefully to "software only" rather than failing entirely. The report clearly documents which modes succeeded.

### D7: No Parallel Rendering in Benchmark

**Decision:** The benchmark runs a single-instance render (one Puppeteer, one FFmpeg). It does not test parallelized multi-instance rendering (OBJ-082).

**Rationale:** C-08 says "The 15-minute target is for single-instance rendering only." Multi-instance benchmarking depends on OBJ-082 which is open and depends on OBJ-035.

### D8: Benchmark Output Directory Is Not Cleaned Up

**Decision:** The benchmark retains all artifacts (MP4, report JSON, CSV, test images) in the output directory.

**Rationale:** The rendered MP4 is useful for manual visual inspection. The report JSON is used for regression tracking. Cleanup is the caller's responsibility.

### D9: `EnvironmentInfo` Captures Reproducibility Context

**Decision:** The report includes Node.js version, OS, CPU model/cores, memory, FFmpeg version, and Chromium version. This provides the context needed to compare benchmarks across different machines.

**Rationale:** C-08 specifies "a standard 4-core VPS with at least 4GB RAM." The environment info lets reviewers verify whether a benchmark was run on qualifying hardware.

### D10: Statistical Percentiles For Frame Jitter Detection

**Decision:** The report includes median, p95, p99, max, min, and standard deviation of per-frame times.

**Rationale:** Average frame time can mask jitter. A benchmark that averages 300ms/frame but has p99 at 2000ms indicates a serious problem (GC pauses, Chromium throttling, memory pressure). Percentiles expose these outliers. The throttling-prevention flags from OBJ-049 should minimize jitter, but the benchmark must be able to detect it if it occurs.

### D11: Renderer Info Uses OBJ-010's RendererInfo Type With Derived Software Detection

**Decision:** `BenchmarkReport.rendererInfo` uses OBJ-010's `RendererInfo` type (the type returned by `OrchestratorResult.rendererInfo`). A separate `isSoftwareRenderer` boolean is derived by applying OBJ-049 D7's heuristic to `rendererInfo.gpuRenderer`: check if the string contains "SwiftShader", "llvmpipe", or "softpipe" (case-insensitive). Returns `false` if `gpuRenderer` is `'unknown'` or unrecognized.

**Rationale:** The orchestrator's `render()` method does not expose the `PuppeteerBridge`, so calling OBJ-049's `probeWebGLRenderer()` directly is not possible during the benchmark. `OrchestratorResult.rendererInfo` is the only renderer data available post-render. Constructing a fake `WebGLRendererInfo` from partial `RendererInfo` data would be fragile and misleading. Using `RendererInfo` directly with a derived boolean is honest and complete.

### D12: Version Read From package.json

**Decision:** The benchmark version string (`BenchmarkReport.version`) is read from the `version` field of depthkit's `package.json` at benchmark start. The implementation reads the file relative to the module's location using `import { readFile } from 'fs/promises'` and `JSON.parse()`, or via Node.js's `import()` with `{ assert: { type: 'json' } }`.

**Rationale:** The version must reflect the actual engine version being benchmarked. Reading from `package.json` is the canonical Node.js approach and ensures the benchmark report stays in sync with the codebase.

## Acceptance Criteria

### Reference Manifest & Assets

- [ ] **AC-01:** `getReferenceBenchmarkParameters()` returns a frozen object with `width: 1920`, `height: 1080`, `fps: 30`, `durationSeconds: 60`, `totalFrames: 1800`, `sceneCount: 5`, `planesPerScene: 6`, `geometry: 'stage'`, `cameraPreset: 'slow_push_forward'`.
- [ ] **AC-02:** `generateReferenceManifest()` returns a `Manifest` object that passes validation via `loadManifest()` with a registry containing the `stage` geometry and `slow_push_forward` camera.
- [ ] **AC-03:** The generated manifest contains exactly 5 scenes, each with `duration: 12`, `geometry: 'stage'`, `camera: 'slow_push_forward'`, `start_time` values of `[0, 12, 24, 36, 48]`, and `transition_in`/`transition_out` of type `cut`.
- [ ] **AC-04:** `generateBenchmarkAssets()` creates PNG files on disk — one per unique slot across all scenes. Each PNG is a valid image file (starts with `\x89PNG` magic bytes) readable by Three.js's texture loader. No image library (e.g., `sharp`) is required.
- [ ] **AC-05:** Subject and near_fg test images have alpha channels (RGBA color type in PNG). Sky, backdrop, midground, and floor images are opaque (RGB color type in PNG).

### Benchmark Execution

- [ ] **AC-06:** `runBenchmark()` with default config (software mode) produces a valid MP4 file at the output path. `ffprobe` reports 1920x1080, H.264, 30fps, approximately 60 seconds duration.
- [ ] **AC-07:** `runBenchmark()` completes without throwing on a machine with 4+ cores and 4GB+ RAM using software WebGL.
- [ ] **AC-08:** `BenchmarkReport.timing.renderLoopMs` matches `OrchestratorResult.renderDurationMs` (within 1ms tolerance for timestamp collection overhead).
- [ ] **AC-09:** `BenchmarkReport.captureStats` matches `OrchestratorResult.captureStats` exactly.

### Timing & Statistics

- [ ] **AC-10:** When `collectFrameTimings: true`, `BenchmarkReport.frameTimings` contains exactly 1800 entries (one per frame).
- [ ] **AC-11:** `timing.medianFrameMs`, `timing.p95FrameMs`, `timing.p99FrameMs`, `timing.maxFrameMs`, `timing.minFrameMs`, `timing.stddevFrameMs` are non-null when frame timings are collected.
- [ ] **AC-12:** `timing.medianFrameMs` falls between `timing.minFrameMs` and `timing.maxFrameMs`.
- [ ] **AC-13:** `timing.throughputFps` equals `totalFrames / (renderLoopMs / 1000)` within floating-point tolerance.
- [ ] **AC-14:** When `collectFrameTimings: false`, percentile fields are null, `frameTimings` is undefined, and `frameTimingsCsvPath` is null.

### Compliance Assessment

- [ ] **AC-15:** `compliance.c08.thresholdMs === 900000` (15 minutes in ms).
- [ ] **AC-16:** `compliance.tc02.thresholdMs === 500`.
- [ ] **AC-17:** `compliance.c08.passed === true` when `timing.orchestratorTotalMs < 900000`. `compliance.c08.measuredMs === timing.orchestratorTotalMs`.
- [ ] **AC-18:** `compliance.tc02.passed === true` when `timing.averageFrameMs < 500`. `compliance.tc02.measuredMs === timing.averageFrameMs`.
- [ ] **AC-19:** `compliance.c08.headroom` equals `(900000 - measuredMs) / 900000`.
- [ ] **AC-20:** `compliance.tc02.headroom` equals `(500 - measuredMs) / 500`.

### Environment Info

- [ ] **AC-21:** `environment.nodeVersion` is a non-empty string starting with 'v'.
- [ ] **AC-22:** `environment.cpuCores` is a positive integer.
- [ ] **AC-23:** `environment.totalMemoryMb` is a positive number.
- [ ] **AC-24:** `environment.ffmpegVersion` is a non-empty string.
- [ ] **AC-25:** `environment.chromiumVersion` is a non-empty string.

### Renderer Info

- [ ] **AC-26:** `rendererInfo` is populated from `OrchestratorResult.rendererInfo`. In software mode, `isSoftwareRenderer === true` (derived from `rendererInfo.gpuRenderer` containing "SwiftShader").
- [ ] **AC-27:** `gpuMode.requested` matches the config's `gpuMode`. `gpuMode.actual` is `'software'` when `isSoftwareRenderer` is true, `'hardware'` otherwise.

### Report Output

- [ ] **AC-28:** `runBenchmark()` writes `benchmark-report.json` to `outputDir`. The file is valid JSON that deserializes to a `BenchmarkReport`.
- [ ] **AC-29:** When `collectFrameTimings: true`, `runBenchmark()` writes `frame-timings.csv` to `outputDir`. The CSV has a header row (`frame,totalMs,activeSceneIds`) and 1800 data rows.
- [ ] **AC-30:** `formatBenchmarkReport()` produces a non-empty string containing the C-08 and TC-02 pass/fail indicators and the resolution.

### Comparison Benchmark

- [ ] **AC-31:** `runComparisonBenchmark()` in a software-only environment returns `software` as a valid report and `hardware: null` with a non-empty `hardwareError`.
- [ ] **AC-32:** `ComparisonReport.speedupRatio` is null when hardware is unavailable.
- [ ] **AC-33:** When hardware mode runs but falls back to SwiftShader, `hardwareFellBackToSoftware === true`. `formatComparisonReport()` output includes a warning about the fallback.

### Error Handling

- [ ] **AC-34:** If the orchestrator throws during the benchmark, `runBenchmark()` throws `BenchmarkError` with code `RENDER_FAILED` and the orchestrator error as `cause`.
- [ ] **AC-35:** If the output directory cannot be created, `runBenchmark()` throws `BenchmarkError` with code `REPORT_WRITE_FAILED`.

### Performance (C-08, TC-02 — The Actual Gate)

- [ ] **AC-36:** On a 4-core VPS with 4GB+ RAM using software WebGL, `compliance.c08.passed === true` (orchestrator completes in under 15 minutes). *Performance test — logged as a benchmark result, not enforced in CI on underpowered machines.*
- [ ] **AC-37:** On the same hardware, `compliance.tc02.passed === true` (average frame time under 500ms). *Same caveat.*

### Version

- [ ] **AC-38:** `BenchmarkReport.version` is a non-empty string read from depthkit's `package.json` `version` field.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Output directory doesn't exist | Created via `fs.mkdir(outputDir, { recursive: true })`. |
| Output directory not writable | `BenchmarkError` code `REPORT_WRITE_FAILED`. |
| FFmpeg not installed | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `ENCODE_FAILED`). |
| Chromium not available | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `BROWSER_LAUNCH_FAILED`). |
| Benchmark cancelled via `onProgress` returning false | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `CANCELLED`). Partial report is NOT generated — a cancelled benchmark is not a valid measurement. |
| Machine has < 4GB RAM | Benchmark runs but may be slower. `environment.totalMemoryMb` documents the constraint. `compliance.c08.passed` may be `false`. Report is still valid. |
| Concurrent benchmark runs to same outputDir | Last writer wins. The benchmark does not lock the output directory. Run in separate directories for concurrent benchmarks. |
| `generateBenchmarkAssets()` called with empty string path | Throws `BenchmarkError` code `ASSET_GENERATION_FAILED`. |
| Stage geometry not registered | `BenchmarkError` code `RENDER_FAILED` (wraps OrchestratorError `GEOMETRY_NOT_FOUND`). The runner's default registry includes stage. |
| `collectFrameTimings: false` | Percentile fields are null. CSV is not written. `frameTimingsCsvPath` is null. `frameTimings` is undefined. Report is still valid. |
| First frame is unusually slow (cold start) | Captured in frame timings. The p95/p99 statistics naturally handle outliers. The median is a more robust central tendency than the mean. |
| `package.json` unreadable | `BenchmarkError` code `ENVIRONMENT_PROBE_FAILED`. |
| `rendererInfo.gpuRenderer` is `'unknown'` | `isSoftwareRenderer` is `false`. `gpuMode.actual` is `'hardware'`. The report documents the ambiguity. |
| Hardware comparison where Chromium falls back to SwiftShader | Hardware run completes. `hardware.isSoftwareRenderer === true`. `hardwareFellBackToSoftware === true`. `speedupRatio` is computed but the formatted report warns it's not meaningful. |

## Test Strategy

### Unit Tests: `test/unit/benchmark-runner.test.ts`

1. **Reference parameters:** `getReferenceBenchmarkParameters()` returns frozen object with `planesPerScene: 6` and all other C-08/TC-02 values. Verify object is frozen.

2. **Reference manifest structure:** `generateReferenceManifest()` produces a `Manifest` with version `'3.0'`, 5 scenes, correct geometry/camera assignments, cut transitions, no audio. Scene start_times are `[0, 12, 24, 36, 48]`. Scene durations sum to 60s.

3. **Manifest validation:** The generated manifest passes `loadManifest()` validation with a mock registry that registers `stage` geometry with 6 slots and `slow_push_forward` camera.

4. **Compliance calculation — C-08 pass:** Given `orchestratorTotalMs = 600000` (10 min), verify `c08.passed === true`, `c08.measuredMs === 600000`, `c08.headroom ≈ 0.333`.

5. **Compliance calculation — C-08 fail:** Given `orchestratorTotalMs = 1000000` (16.7 min), verify `c08.passed === false`, `c08.headroom < 0`.

6. **Compliance calculation — TC-02 pass:** Given `averageFrameMs = 300`, verify `tc02.passed === true`, `tc02.measuredMs === 300`, `tc02.headroom === 0.4`.

7. **Compliance calculation — TC-02 fail:** Given `averageFrameMs = 550`, verify `tc02.passed === false`.

8. **Percentile computation:** Given known frame timings `[100, 200, 300, 400, 500]` (sorted), verify median = 300, p95/p99 are correct, stddev is correct, min = 100, max = 500.

9. **Percentile computation — all equal:** Frame timings all 250ms. Verify median = 250, stddev = 0, min = max = 250.

10. **Format report:** `formatBenchmarkReport()` with a mock report returns a string containing "C-08", "TC-02", "PASS" or "FAIL", and the resolution "1920x1080".

11. **Comparison report — hardware null:** Verify `speedupRatio` is null, `hardwareFellBackToSoftware === false`.

12. **Comparison report — both present, hardware real GPU:** Software 600s, hardware 200s. Verify `speedupRatio === 3.0`, `hardwareFellBackToSoftware === false`.

13. **Comparison report — hardware fell back to SwiftShader:** Hardware `isSoftwareRenderer === true`. Verify `hardwareFellBackToSoftware === true`. `formatComparisonReport()` output contains "fell back" warning.

14. **Frame timing CSV format:** Verify header row `frame,totalMs,activeSceneIds` and data row format match spec.

15. **isSoftwareRenderer derivation:** `gpuRenderer = "Google SwiftShader"` → true. `gpuRenderer = "ANGLE (NVIDIA ...)"` → false. `gpuRenderer = "unknown"` → false. `gpuRenderer containing "llvmpipe"` → true.

### Integration Tests: `test/integration/benchmark-runner.test.ts`

Use a **scaled-down** benchmark for integration testing: 320x240, 10fps, 3 seconds (30 frames), 1 scene, software mode. The scaled-down test requires a test-only helper that overrides `generateReferenceManifest()` parameters (or accepts a custom manifest in `BenchmarkConfig` — see OQ-B).

16. **Scaled benchmark end-to-end:** Run `runBenchmark()` with scaled-down parameters. Verify: MP4 exists, report JSON exists, report deserializes, `timing` fields are positive numbers, `compliance` fields are populated.

17. **Asset generation:** `generateBenchmarkAssets()` creates files. Verify each file exists, starts with PNG magic bytes `\x89PNG`, subject image has alpha channel (RGBA).

18. **Per-frame CSV:** Run scaled benchmark with `collectFrameTimings: true`. Verify CSV exists, has header + 30 data rows, frame numbers 0-29.

19. **Software WebGL verification:** Run benchmark in software mode. Verify `gpuMode.actual === 'software'` and `isSoftwareRenderer === true`.

20. **Environment info populated:** Verify all `EnvironmentInfo` fields are non-empty/positive.

21. **Report JSON round-trip:** Write report, read it back via `JSON.parse()`, verify key fields match the in-memory report.

22. **Comparison in software-only environment:** Run `runComparisonBenchmark()`. Verify `software` report is valid, `hardware` is null, `hardwareError` is a non-empty string, `hardwareFellBackToSoftware === false`.

23. **Version field populated:** Verify `BenchmarkReport.version` is a non-empty semver-like string.

### Full-Scale Benchmark (Manual / CI on Qualifying Hardware)

24. **C-08 compliance:** Run `runBenchmark()` with default config on a 4-core, 4GB+ VPS. Assert `compliance.c08.passed === true`. Log the full formatted report.

25. **TC-02 compliance:** Same run as above. Assert `compliance.tc02.passed === true`.

26. **Frame jitter analysis:** Inspect `timing.stddevFrameMs` and `timing.p99FrameMs`. If p99 > 2× average, investigate throttling or GC causes. This is a diagnostic observation, not a pass/fail criterion.

27. **Bottleneck identification:** Compare `captureStats.averageCaptureMs` to `timing.averageFrameMs`. If capture accounts for >70% of frame time, document as the primary bottleneck (informing potential optimization of the capture strategy to `canvas-rgba`).

### Relevant Testable Claims

- **TC-02:** Tests 24-25 directly validate the 500ms/frame threshold.
- **C-08:** Tests 24-25 directly validate the 15-minute threshold.
- **TC-06:** Determinism is not directly tested by the benchmark (OBJ-035 test #28 covers this), but the benchmark's per-frame timing variance (stddev) provides indirect evidence.
- **TC-11:** Test 19 confirms software WebGL is used. Tests 24-25 on qualifying hardware validate that the software path meets performance targets.

## Integration Points

### Depends on

| Dependency | What OBJ-074 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class: creates instance with `OrchestratorConfig`, calls `render()`, consumes `OrchestratorResult` (timing, captureStats, encoderResult, rendererInfo, warnings). Uses `RenderProgress` from `onProgress` callback for per-frame timing. |
| **OBJ-049** (Software Rendering Config) | `resolveRenderingConfig()` to determine Chromium launch args and `bridgeGpu` flag. `GpuMode` type. |
| **OBJ-016** (Manifest Loader) — transitive via OBJ-035 | `loadManifest()` for validating the generated reference manifest. |
| **OBJ-004** (Manifest Schema) — transitive via OBJ-035 | `ManifestRegistry`, `Manifest`, `createRegistry()` for setting up validation. |
| **OBJ-005** (Geometry Registry) — transitive via OBJ-035 | `getGeometryRegistry()` to resolve stage geometry. `GeometryRegistry` type. |
| **OBJ-006** (Camera Registry) — transitive via OBJ-035 | Camera registry for resolving `slow_push_forward`. `CameraPathRegistry` type. |
| **OBJ-018** (Stage Geometry) — transitive via OBJ-005 | The `stageGeometry` definition with its 6 slots. The benchmark's reference manifest is built around this geometry. |
| **OBJ-010** (Page Shell) — transitive via OBJ-035 | `RendererInfo` type for renderer diagnostics. |
| **OBJ-012** (Frame Capture) — transitive via OBJ-035 | `CaptureStats` type for capture timing data. |
| **OBJ-013** (FFmpeg Encoder) — transitive via OBJ-035 | `FFmpegEncoderResult` type for encoder stats. |

### Consumed by

| Downstream | How it uses OBJ-074 |
|---|---|
| **OBJ-073** (Docker integration) | Runs the benchmark inside a Docker container to validate C-11 + C-08 combined (software WebGL in Docker meets performance targets). |
| **CI pipeline** | Runs scaled-down benchmark on every PR. Full benchmark on qualifying hardware nightly or on-demand. |
| **OBJ-082** (Parallel rendering) | Uses OBJ-074's report format as a baseline. Parallel rendering benchmarks extend the same `BenchmarkReport` structure with multi-instance metrics. |
| **Human operators** | Run `runBenchmark()` on target deployment hardware to verify C-08 compliance before deploying to production. |

### File Placement

```
depthkit/
  src/
    benchmark/
      runner.ts                    # NEW — BenchmarkConfig, BenchmarkReport,
                                   #       ComplianceResult, EnvironmentInfo,
                                   #       TimingResults, FrameTiming,
                                   #       BenchmarkError, runBenchmark(),
                                   #       runComparisonBenchmark(),
                                   #       formatBenchmarkReport(),
                                   #       getReferenceBenchmarkParameters(),
                                   #       generateReferenceManifest(),
                                   #       generateBenchmarkAssets()
      fixtures/
        generate-assets.ts         # NEW — internal: solid-color PNG generation
                                   #       using Node.js zlib (no image library)
  test/
    unit/
      benchmark-runner.test.ts     # NEW — unit tests (statistics, compliance, format)
    integration/
      benchmark-runner.test.ts     # NEW — integration tests (scaled-down renders)
```

## Open Questions

### OQ-A: Should the benchmark runner be exposed as a CLI subcommand?

OBJ-046 (CLI) is verified. Adding a `depthkit benchmark` subcommand would make benchmarks easier to run manually. However, OBJ-046's spec would need updating. For now, the benchmark is invocable programmatically via `runBenchmark()`. A CLI wrapper can be added later as a thin shell script or via OBJ-083 (extended CLI, which is open).

### OQ-B: Should the benchmark support custom manifests or scaled parameters?

The current spec only supports the canonical reference manifest. Integration tests need a scaled-down variant (320x240, 10fps, 3s). Two approaches: (a) add an optional `manifestOverride` or `parametersOverride` to `BenchmarkConfig`, or (b) integration tests call `generateReferenceManifest()` and the orchestrator separately with modified parameters, bypassing `runBenchmark()`. Approach (b) keeps the runner simple but duplicates wiring; approach (a) is more flexible. The implementer should choose (a) if the wiring is non-trivial. Compliance assessment only applies to the reference parameters regardless.

### OQ-C: Per-component frame timing breakdown

The current design captures total frame time but cannot decompose it into render/capture/encode per frame. `CaptureStats` provides aggregate capture timing. `FFmpegEncoderResult.durationMs` provides aggregate encode timing. Per-frame breakdown would require extending OBJ-035's `onProgress` with per-component timings. Deferred — the aggregate breakdown is sufficient for bottleneck identification in V1.

### OQ-D: Regression threshold for CI gating

Should the benchmark define a "regression threshold" (e.g., "fail CI if average frame time increases by more than 10% compared to baseline")? This requires storing a baseline report and comparing against it. Useful but adds complexity. Deferred — for V1, the benchmark reports raw numbers and the human decides if a regression has occurred.

---

I believe all 8 issues from the challenger's review are now addressed:

1. **planesPerScene: 6** — updated throughout (AC-01, D2, parameters, formatted output)
2. **c08.measuredMs uses orchestratorTotalMs** — consistent in type definition, JSDoc, and AC-17
3. **webglInfo → rendererInfo + isSoftwareRenderer** — promoted to D11, using OBJ-010's RendererInfo type, AC-26 updated
4. **generateReferenceManifest() returns Manifest** — updated return type
5. **version source** — new D12 specifying package.json
6. **PNG generation via zlib** — committed in D1, no image library
7. **hardwareFellBackToSoftware** — added to ComparisonReport, AC-33, test case 13, formatComparisonReport
8. **Explicit start_times** — stated in D2 and AC-03

Challenger, please verify and approve if you're satisfied.

---

## Round 4 — spec_challenger

Let me verify each fix against the revised spec systematically.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Write,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]
## Verification of Round 2 Fixes

I'll systematically verify each of my 8 original issues against the revised spec.

**Issue 1 (planesPerScene: 6):** ✅ VERIFIED. `BenchmarkParameters.planesPerScene` JSDoc says "Reference: 6". AC-01 specifies `planesPerScene: 6`. D2 says "All 6 stage geometry slots... populated, exceeding C-08's 5-plane minimum." Format example shows "stage (6 planes) × 5 scenes."

**Issue 2 (c08.measuredMs consistency):** ✅ VERIFIED. `ComplianceResult.c08.measuredMs` JSDoc now says "The measured orchestrator total time in ms (timing.orchestratorTotalMs)." `TimingResults.orchestratorTotalMs` JSDoc says "THIS is the value compared against C-08's 15-minute threshold." AC-17 explicitly states `compliance.c08.measuredMs === timing.orchestratorTotalMs`. All three are consistent.

**Issue 3 (webglInfo → rendererInfo + isSoftwareRenderer):** ✅ VERIFIED. `BenchmarkReport` now has `rendererInfo: RendererInfo` (OBJ-010 type) + `isSoftwareRenderer: boolean` (derived via OBJ-049 D7 heuristic). D11 promoted from OQ-E. AC-26 references both fields correctly.

**Issue 4 (return type Manifest):** ✅ VERIFIED. `generateReferenceManifest(): Manifest`. Import includes `Manifest` from `'../manifest/schema.js'`.

**Issue 5 (version source):** ✅ VERIFIED. D12 specifies reading from `package.json`. AC-38 tests it.

**Issue 6 (zlib, no sharp):** ✅ VERIFIED. D1 commits to "Node.js `zlib` (raw RGBA buffer + deflate compression)". AC-04 explicitly says "No image library (e.g., `sharp`) is required."

**Issue 7 (hardwareFellBackToSoftware):** ✅ VERIFIED. Field added to `ComparisonReport` with correct JSDoc. AC-33 tests it. Test case 13 covers it. `formatComparisonReport()` mentions the warning. Edge case table documents the scenario.

**Issue 8 (explicit start_times):** ✅ VERIFIED. D2: "Scene start times are `[0, 12, 24, 36, 48]` seconds." AC-03 includes `start_time` values. `generateReferenceManifest()` JSDoc matches.

---

### New Issues Found in Revision

**Issue 9 (MINOR): Import path for `RendererInfo` is wrong**

The import statement says:
```typescript
import type { RendererInfo } from '../page/protocol-types.js';
```

But OBJ-035 imports `RendererInfo` from `'./protocol-types.js'` (i.e., `src/engine/protocol-types.ts`). The benchmark is at `src/benchmark/runner.ts`, so the correct import path is `'../engine/protocol-types.js'`, not `'../page/protocol-types.js'`.

This would cause a compile error. It's clearly a typo, and I'll fix it in the final write.

---

All 8 original issues are satisfactorily addressed. The one new issue is a trivial import path typo that I can correct in the final output. The spec is implementable, correctly scoped, and uses seed vocabulary consistently.

CONCLUSION:

The specification for OBJ-074 — Performance Benchmark Plan — is agreed. It defines a self-contained benchmark runner that uses OBJ-035's Orchestrator to render a canonical 60-second, 30fps, 6-plane-per-scene reference video at 1920x1080, measures per-frame timing via `onProgress` deltas, computes statistical percentiles, and assesses compliance against C-08 (< 15 min) and TC-02 (< 500ms/frame). Key design decisions: no external asset dependencies (zlib-generated PNGs), `RendererInfo` from OBJ-010 with derived `isSoftwareRenderer` boolean, hardcoded compliance thresholds, graceful degradation in hardware comparison mode with `hardwareFellBackToSoftware` detection. One import path typo corrected in final output.

Let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-074/output.md",
  "content": "# Specification: OBJ-074 \u2014 Performance Benchmark Plan\n\n## Summary\n\nOBJ-074 delivers a **benchmark runner module** (`src/benchmark/runner.ts`) and a **reference benchmark manifest** that together provide a reproducible procedure for measuring depthkit's rendering performance. The benchmark measures per-frame timing breakdown, compares software WebGL vs. GPU acceleration, identifies bottlenecks, and validates compliance with C-08 (60-second, 30fps, 5-plane video renders in under 15 minutes on a 4-core VPS) and TC-02 (under 500ms per frame with software WebGL). The benchmark is invocable programmatically and produces a structured `BenchmarkReport` JSON for analysis, regression tracking, and CI gating.\n\n## Interface Contract\n\n### Module: `src/benchmark/runner.ts`\n\n```typescript\nimport type { OrchestratorResult, RenderProgress } from '../engine/orchestrator.js';\nimport type { RendererInfo } from '../engine/protocol-types.js';\nimport type { CaptureStats } from '../engine/frame-capture.js';\nimport type { GpuMode } from '../engine/rendering-config.js';\nimport type { ManifestRegistry, Manifest } from '../manifest/schema.js';\nimport type { GeometryRegistry } from '../scenes/geometries/types.js';\nimport type { CameraPathRegistry } from '../camera/types.js';\n\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n// Configuration\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n\n/**\n * Configuration f
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-074/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-074/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-074",
     3→  "description": "Performance benchmark plan -- procedure for benchmarking a 60-second, 30fps, 5-plane video at 1920x1080. Per-frame timing measurement, software WebGL vs GPU acceleration comparison, identification of bottlenecks (capture time, encode time, render time). Covers C-08 (under 15 minutes on 4-core VPS) and TC-02 (under 500ms per frame with software WebGL).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035", "OBJ-049"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 6 validation plan. Covers C-08 and TC-02."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-074/meta.json",
  "content": "{\n  \"id\": \"OBJ-074\",\n  \"description\": \"Performance benchmark plan -- procedure for benchmarking a 60-second, 30fps, 6-plane video at 1920x1080. Per-frame timing measurement, software WebGL vs GPU acceleration comparison, identification of bottlenecks (capture time, encode time, render time). Covers C-08 (under 15 minutes on 4-core VPS) and TC-02 (under 500ms per frame with software WebGL).\",\n  \"category\": \"integration\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T12:00:00Z\",\n  \"depends_on\": [\"OBJ-035\", \"OBJ-049\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 6 validation plan. Covers C-08 and TC-02. Delivers benchmark runner module (src/benchmark/runner.ts) with self-contained reference manifest using stage geometry, zlib-generated test PNGs, per-frame timing collection, statistical percentiles, and C-08/TC-02 compliance assessment.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-074/meta.json has been updated successfully.
Now commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-074/output.md nodes/OBJ-074/meta.json && git commit -m \"$(cat <<'EOF'\nAdd specification for OBJ-074: Performance Benchmark Plan\n\nDefines benchmark runner module (src/benchmark/runner.ts) that measures\ndepthkit rendering performance against C-08 (< 15 min) and TC-02\n(< 500ms/frame) thresholds. Self-contained with zlib-generated test\nPNGs, uses OBJ-035 Orchestrator as-is, collects per-frame timings\nvia onProgress deltas, computes statistical percentiles for jitter\ndetection, and supports software vs. hardware comparison with\nSwiftShader fallback detection.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-074 spec and updated meta.json"
}
[Tool Result] [master a6185dc] Add specification for OBJ-074: Performance Benchmark Plan
 2 files changed, 889 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-074/output.md
Specification for OBJ-074 is committed. The deliberation converged after 4 rounds with all 8 issues from my review verified as fixed, plus one import path typo corrected in the final output. The spec is implementable, correctly scoped to its objective boundaries, and uses seed vocabulary consistently.
