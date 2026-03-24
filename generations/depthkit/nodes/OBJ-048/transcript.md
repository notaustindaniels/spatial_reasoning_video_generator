# Deliberation Transcript: OBJ-048

---

## Round 1 — spec_author


[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the existing codebase to understand what's already implemented for error handling across the engine.
[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-048/**/*"
}
[Tool Result] No files found
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-048/meta.json

[Tool: Grep]
  Input: {
  "pattern": "ManifestError|OrchestratorError|ErrorCode",
  "glob": "depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/manifest/**/*.ts"
}

[Tool: Glob]
  Input: {
  "pattern": "**/src/engine/**/*.ts"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-016/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-035/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-016/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-004/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-013/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md
Let me read the OBJ-004, OBJ-013, and OBJ-046 specs to understand the full error surface before proposing.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-004/output.md",
  "limit": 150
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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "limit": 150
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

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-046/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "limit": 200
}
[Tool Result]      1→# Specification: OBJ-046 — CLI Interface
     2→
     3→## Summary
     4→
     5→OBJ-046 delivers the Commander-based CLI for depthkit (`src/cli.ts`) — the primary human-facing entry point for rendering, validating, and previewing manifests. It exposes three commands (`render`, `validate`, `preview`), handles argument parsing for manifest paths, output paths, resolution/fps overrides, GPU mode, encoding presets, verbose/debug output, and provides structured progress reporting and timing statistics during renders. It composes the Orchestrator (OBJ-035), manifest loader (OBJ-016), geometry registry (OBJ-005), and camera registry (OBJ-006) into a user-friendly terminal experience. The `package.json` `bin` field points to this module.
     6→
     7→## Interface Contract
     8→
     9→### Module: `src/cli.ts`
    10→
    11→This is the executable entry point. The source file begins with `#!/usr/bin/env node` (preserved by the TypeScript compiler or prepended by the build step). It... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "offset": 150,
  "limit": 100
}
[Tool Result]    150→  /**
   151→   * Writes a single frame's pixel data to FFmpeg's stdin.
   152→   *
   153→   * Handles backpressure: if stream.write() returns false (FFmpeg's stdin
   154→   * buffer is full), awaits the 'drain' event before resolving.
   155→   *
   156→   * NOT safe to call concurrently. The orchestrator's deterministic frame
   157→   * loop (C-03) guarantees sequential calls. Concurrent calls produce
   158→   * undefined behavior (interleaved frame data).
   159→   *
   160→   * Throws FFmpegEncoderError if:
   161→   * - start() has not been called
   162→   * - finalize() has already been called
   163→   * - FFmpeg process has exited unexpectedly (checked before write)
   164→   * - For 'rgba' format: buffer size !== width * height * 4
   165→   */
   166→  writeFrame(data: Buffer): Promise<void>;
   167→
   168→  /**
   169→   * Closes FFmpeg's stdin and waits for the process to exit.
   170→   * Returns the encoding result on success.
   171→   * Throws FFmpegEncoder... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-046/output.md",
  "offset": 200,
  "limit": 300
}
[Tool Result]    200→
   201→/**
   202→ * Formats validation errors into a human-readable error report.
   203→ *
   204→ * @param errors - All ManifestError objects from validation.
   205→ * @param color - Whether to include ANSI color codes.
   206→ * @returns Formatted multi-line string.
   207→ */
   208→export function formatValidationErrors(
   209→  errors: ManifestError[],
   210→  color: boolean,
   211→): string;
   212→
   213→/**
   214→ * Formats an OrchestratorError into a human-readable error message.
   215→ * Includes the error code, message, and context (frame number, validation errors).
   216→ *
   217→ * @param error - The orchestrator error.
   218→ * @param verbose - Whether to include stack trace and cause chain.
   219→ * @param color - Whether to include ANSI color codes.
   220→ * @returns Formatted multi-line string.
   221→ */
   222→export function formatOrchestratorError(
   223→  error: OrchestratorError,
   224→  verbose: boolean,
   225→  color: boolean,
   226→):... [truncated]
Now I have a comprehensive understanding of the existing error handling landscape. Let me also check if there are any existing implementations or specs for the page-side errors:
[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-009/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-011/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-014/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md",
  "limit": 80
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-014 — FFmpeg Audio Muxing
     2→
     3→## Summary
     4→
     5→OBJ-014 implements the audio muxing module (`src/engine/audio-muxer.ts`) — the post-encoding stage that combines OBJ-013's video-only MP4 with an audio file (WAV or MP3) to produce the final deliverable MP4 with synchronized audio. This module covers constraint C-07 (audio synchronization) at the encoding level, making the single-pass vs. two-pass decision, handling format differences between WAV and MP3 inputs, and managing duration mismatches between video and audio streams.
     6→
     7→This module is deliberately separate from OBJ-013's `FFmpegEncoder` — it operates on completed files, not on streaming frame data. It accepts file paths, not buffers.
     8→
     9→## Interface Contract
    10→
    11→```typescript
    12→// src/engine/audio-muxer.ts
    13→
    14→/**
    15→ * Strategy for handling duration mismatches between video and audio.
    16→ *
    17→ * - 'match_shortest': Out... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-011 — Puppeteer-to-Page Message Protocol
     2→
     3→## Summary
     4→
     5→OBJ-011 defines the complete cross-boundary message protocol between the Node.js orchestrator and the headless Chromium page. It delivers: (1) a `PageProtocol` class on the Node side that wraps `PuppeteerBridge.evaluate()` with typed, high-level commands — initialization, scene setup/teardown, frame rendering (with multi-pass support for transitions), and disposal; (2) page-side extensions to `window.depthkit` that implement the protocol handlers — scene management (creating/removing THREE.Group instances with textured meshes), texture loading via THREE.TextureLoader, and multi-pass compositing for transitions; and (3) shared protocol types (`src/engine/protocol-types.ts`) that define every data structure crossing the boundary. This is the single source of truth for the Node.js/browser contract, building on OBJ-009's `evaluate()` primitive, OBJ-010's renderer skeleton, and OBJ-... [truncated]
Now I have a thorough understanding of the error landscape. Let me read the OBJ-014 error types too:
[Tool: Grep]
  Input: {
  "pattern": "AudioMuxerError|class.*Error",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/output.md",
  "output_mode": "content",
  "-A": 5
}
[Tool Result] 59:   * fails with AudioMuxerError. Ignored for other strategies.
60-   * Default: 100 (allows up to 100ms drift from frame rounding).
61-   */
62-  toleranceMs?: number;
63-
64-  /**
--
152:export class AudioMuxerError extends Error {
153-  constructor(
154-    message: string,
155-    public readonly exitCode: number | null,
156-    public readonly ffmpegLog: string,
157-  ) {
--
159:    this.name = 'AudioMuxerError';
160-  }
161-}
162-
163-/**
164- * Threshold in milliseconds below which video and audio durations are
--
188: * Throws AudioMuxerError if no working ffprobe binary is found.
189- */
190-export function resolveFFprobePath(ffmpegPath?: string, ffprobePath?: string): Promise<string>;
191-
192-/**
193- * Probes a media file using ffprobe, returning duration and stream info.
--
202: * Throws AudioMuxerError if:
203- * - ffprobe binary cannot be found
204- * - The file does not exist or is unreadable
205- * - ffprobe exits with non-zero code
206- * - ffprobe output cannot be ... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "PageProtocolError|error|throw",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "head_limit": 30
}
[Tool Result] 164:  status: 'loaded' | 'error';
169:  /** Error message if status='error'. */
170:  error?: string;
288: * Structured error from the page, surfaced through evaluate().
289: * Page-side handlers throw errors with this shape serialized
293: * PageProtocolError instances.
298:  /** Human-readable error description. */
305: * Error codes for page-side errors.
313:  | 'WEBGL_ERROR'            // WebGL context error
335: * Error thrown by PageProtocol methods when a page-side error occurs.
338:export class PageProtocolError extends Error {
339:  /** Structured error code from the page. */
378:   * @throws PageProtocolError with code 'ALREADY_INITIALIZED' if called twice.
379:   * @throws Error if bridge is not launched.
403:   * @throws PageProtocolError with code 'NOT_INITIALIZED' if init not called.
404:   * @throws PageProtocolError with code 'SCENE_EXISTS' if sceneId already set up.
405:   * @throws PageProtocolError with code 'INVALID_COMMAND' if sceneId is empty.
452:   * @throws Pag... [truncated]
Now I have a complete picture. Let me synthesize the full error landscape and propose the spec.

---

# Specification Proposal: OBJ-048 — Error Handling and Reporting Strategy

## Summary

OBJ-048 defines the unified error handling and reporting strategy across the entire depthkit engine. It specifies: (1) a consolidated error taxonomy cataloguing every error type from manifest validation (OBJ-016), page protocol (OBJ-011), FFmpeg encoding (OBJ-013), audio muxing (OBJ-014), and orchestration (OBJ-035); (2) a `formatErrors()` utility module (`src/engine/errors.ts`) that converts any depthkit error into a structured, actionable report for both CLI and programmatic consumers; (3) graceful degradation rules (when to warn vs. when to fail); (4) an error code registry that programmatic consumers (n8n HTTP endpoint, future APIs) can switch on; and (5) integration with OBJ-046's CLI formatting layer. This is the "error formatting" utility that OBJ-016 explicitly deferred to OBJ-048.

## Interface Contract

### Module: `src/engine/errors.ts`

This module provides the engine-level error formatting and classification utilities. It does NOT define new error classes — those are defined by their originating modules (OBJ-004, OBJ-011, OBJ-013, OBJ-014, OBJ-035). This module provides tools for consuming, classifying, and formatting those errors uniformly.

```typescript
// src/engine/errors.ts

import type { ManifestError } from '../manifest/schema.js';
import type { OrchestratorError, OrchestratorErrorCode } from './orchestrator.js';
import type { FFmpegEncoderError } from './ffmpeg-encoder.js';
import type { AudioMuxerError } from './audio-muxer.js';
import type { PageProtocolError, PageErrorCode } from './protocol-types.js';

// ────────────────────────────────────────────
// Error Classification
// ────────────────────────────────────────────

/**
 * Top-level error categories for programmatic consumers.
 * Maps the diverse error types across the engine into a small
 * set of buckets that an HTTP API or n8n workflow can switch on.
 */
export type ErrorCategory =
  | 'validation'     // Manifest is invalid (schema or semantic)
  | 'asset'          // Image/audio files missing or unreadable
  | 'browser'        // Puppeteer/Chromium launch or page init failure
  | 'render'         // Three.js page-side rendering failure
  | 'encode'         // FFmpeg encoding failure
  | 'audio'          // Audio muxing failure
  | 'cancelled'      // User-initiated cancellation
  | 'internal'       // Unexpected/unclassified error
  ;

/**
 * A structured error report suitable for JSON serialization.
 * This is the canonical error output format for programmatic consumers
 * (n8n HTTP endpoint, library API callers).
 */
export interface ErrorReport {
  /** Whether the operation succeeded. Always false for error reports. */
  success: false;

  /** Top-level error category for routing/switching. */
  category: ErrorCategory;

  /**
   * Machine-readable error code. For OrchestratorErrors, this is the
   * OrchestratorErrorCode. For standalone ManifestErrors, this is 'MANIFEST_INVALID'.
   * For unexpected errors, this is 'INTERNAL_ERROR'.
   */
  code: string;

  /** Human-readable summary of the error. One sentence. */
  message: string;

  /**
   * Detailed validation errors, if category is 'validation'.
   * Each entry is a ManifestError from OBJ-016.
   * Empty array for non-validation errors.
   */
  validationErrors: ManifestError[];

  /**
   * Frame number where the error occurred, if applicable.
   * -1 if not frame-related.
   */
  frame: number;

  /**
   * Human-readable detail string with contextual information.
   * For encode errors: includes FFmpeg stderr excerpt.
   * For asset errors: lists missing file paths.
   * For render errors: includes the page error code and details.
   * null if no additional detail is available.
   */
  detail: string | null;

  /**
   * Suggested remediation action(s) for the user.
   * Each string is a single actionable suggestion.
   * Empty array if no specific remediation is known.
   */
  suggestions: string[];
}

// ────────────────────────────────────────────
// Classification Functions
// ────────────────────────────────────────────

/**
 * Classifies an OrchestratorErrorCode into an ErrorCategory.
 *
 * Mapping:
 *   MANIFEST_INVALID        → 'validation'
 *   SCENE_SETUP_FAILED      → 'asset'
 *   BROWSER_LAUNCH_FAILED   → 'browser'
 *   PAGE_INIT_FAILED        → 'browser'
 *   RENDER_FAILED           → 'render'
 *   CAPTURE_FAILED          → 'render'
 *   ENCODE_FAILED           → 'encode'
 *   AUDIO_MUX_FAILED        → 'audio'
 *   CANCELLED               → 'cancelled'
 *   GEOMETRY_NOT_FOUND      → 'validation'
 *   CAMERA_NOT_FOUND        → 'validation'
 */
export function classifyError(code: OrchestratorErrorCode): ErrorCategory;

/**
 * Creates a structured ErrorReport from an OrchestratorError.
 *
 * Extracts the error code, message, frame number, validation errors
 * (if MANIFEST_INVALID), and generates context-specific detail and
 * suggestions based on the error code and cause chain.
 */
export function createErrorReport(error: OrchestratorError): ErrorReport;

/**
 * Creates a structured ErrorReport from a ManifestResult with
 * success: false. Used by the `validate` command which doesn't
 * go through the orchestrator.
 */
export function createValidationErrorReport(errors: ManifestError[]): ErrorReport;

/**
 * Creates a structured ErrorReport from an unknown/unexpected error.
 * Used as a catch-all for errors that aren't OrchestratorError.
 */
export function createUnexpectedErrorReport(error: unknown): ErrorReport;

// ────────────────────────────────────────────
// Formatting Functions (Plain Text)
// ────────────────────────────────────────────

/**
 * Formats a ManifestError array into a human-readable multi-line string.
 * This is the utility deferred by OBJ-016 (OQ-B: "Should There Be a
 * formatErrors() Utility? Deferred to OBJ-048").
 *
 * Format per error:
 *   "  ✗ {path}: {message} ({code})"         — for severity: "error"
 *   "  ⚠ {path}: {message} ({code})"         — for severity: "warning"
 *
 * When path is empty string (file-level errors), the path prefix is omitted:
 *   "  ✗ {message} ({code})"
 *
 * Errors are listed first, then warnings, each group in original order.
 *
 * @param errors — ManifestError array from OBJ-016.
 * @param options — Formatting options.
 * @returns Multi-line string. No trailing newline.
 */
export function formatManifestErrors(
  errors: ManifestError[],
  options?: { color?: boolean },
): string;

/**
 * Formats an OrchestratorError into a human-readable multi-line string.
 *
 * Structure:
 *   "Error: {message} [{code}]"
 *   "  Frame: {frame}"                      — if frame >= 0
 *   "  Validation errors:"                  — if MANIFEST_INVALID
 *   "    ✗ {path}: {message} ({code})"      — for each validation error
 *   "  Detail: {cause.message}"             — if cause exists
 *   "  FFmpeg log (last 20 lines):"         — if cause is FFmpegEncoderError
 *   "    {ffmpegLog excerpt}"
 *   ""
 *   "Suggestions:"
 *   "  • {suggestion}"                      — for each applicable suggestion
 *
 * @param error — OrchestratorError from OBJ-035.
 * @param options — Formatting options.
 * @returns Multi-line string. No trailing newline.
 */
export function formatOrchestratorError(
  error: OrchestratorError,
  options?: { color?: boolean; verbose?: boolean },
): string;

/**
 * Formats an ErrorReport as a JSON string.
 * Suitable for HTTP API responses and structured logging.
 * Uses JSON.stringify with 2-space indentation.
 */
export function formatErrorReportJson(report: ErrorReport): string;

// ────────────────────────────────────────────
// Suggestion Generation
// ────────────────────────────────────────────

/**
 * Generates actionable remediation suggestions for an error.
 * The suggestions are context-specific based on the error code,
 * cause chain, and any nested error details.
 *
 * Returns an array of plain-text suggestion strings.
 */
export function generateSuggestions(error: OrchestratorError): string[];
```

### Suggestion Rules (Exhaustive)

The `generateSuggestions()` function applies the following rules, returning all matching suggestions:

| OrchestratorErrorCode | Condition | Suggestion |
|---|---|---|
| `MANIFEST_INVALID` | Always | `"Run 'depthkit validate <manifest>' to see all errors."` |
| `MANIFEST_INVALID` | Any error with code `UNKNOWN_GEOMETRY` | `"Check the geometry name against the available list in the error message."` |
| `MANIFEST_INVALID` | Any error with code `UNKNOWN_CAMERA` | `"Check the camera name against the available list in the error message."` |
| `MANIFEST_INVALID` | Any error with code `FILE_NOT_FOUND` | `"Verify the manifest file path exists and is readable."` |
| `MANIFEST_INVALID` | Any error with code `INVALID_JSON` | `"Check for syntax errors: trailing commas, unquoted keys, or missing brackets."` |
| `SCENE_SETUP_FAILED` | Cause message contains file path(s) | `"Verify that all image files exist at the paths specified in the manifest."` |
| `SCENE_SETUP_FAILED` | Cause message contains "timeout" or "network" | `"Check network connectivity for remote image URLs."` |
| `BROWSER_LAUNCH_FAILED` | Always | `"Ensure Chromium is installed. Run 'npx puppeteer browsers install chrome' to install."` |
| `BROWSER_LAUNCH_FAILED` | Running in Docker (detected via cause message containing "ENOENT" or "chrome") | `"In Docker, ensure the Chromium dependencies are installed (e.g., apt-get install chromium)."` |
| `PAGE_INIT_FAILED` | Always | `"Ensure headless Chromium supports WebGL. Use --gpu software for SwiftShader fallback."` |
| `RENDER_FAILED` | Always | `"This may be a Three.js scene error. Re-run with --debug to see browser console output."` |
| `CAPTURE_FAILED` | Always | `"Frame capture failed. Re-run with --debug. If persistent, try --capture-strategy viewport-png."` |
| `ENCODE_FAILED` | Always | `"Verify FFmpeg is installed and accessible. Run 'ffmpeg -version' to check."` |
| `ENCODE_FAILED` | Cause is `FFmpegEncoderError` with non-null `exitCode` | `"FFmpeg exited with code {exitCode}. Check the FFmpeg log above for details."` |
| `ENCODE_FAILED` | Cause message contains "No such file or directory" for output | `"Ensure the output directory exists."` |
| `AUDIO_MUX_FAILED` | Always | `"Verify the audio file exists, is a valid WAV or MP3, and is not corrupted."` |
| `AUDIO_MUX_FAILED` | Cause message contains "ffprobe" | `"Ensure ffprobe is installed alongside FFmpeg."` |
| `CANCELLED` | Always | `"Render was cancelled. Re-run to try again."` |
| `GEOMETRY_NOT_FOUND` | Always | `"The geometry registry is inconsistent with the manifest registry. Ensure all geometry modules are imported."` |
| `CAMERA_NOT_FOUND` | Always | `"The camera registry is inconsistent with the manifest registry. Ensure all camera preset modules are imported."` |

### Graceful Degradation Rules

These define the boundary between "warn and continue" vs. "fail immediately":

```typescript
/**
 * Enumeration of degradation decisions.
 * 'fail' = throw / abort rendering.
 * 'warn' = emit a warning, continue with a described fallback behavior.
 */
export type DegradationAction = 'fail' | 'warn';

/**
 * Decides the degradation action for a given condition.
 * These rules are referenced by the orchestrator (OBJ-035) and
 * manifest loader (OBJ-016) — they don't call this function directly,
 * but their behavior MUST match these rules.
 *
 * This is a reference specification, not a runtime function.
 */
```

| Condition | Action | Fallback Behavior | Rationale |
|---|---|---|---|
| Manifest structural validation error (Zod) | `fail` | N/A — rendering never starts | C-10: fail fast, fail clearly |
| Manifest semantic error (unknown geometry, missing required slot, etc.) | `fail` | N/A — rendering never starts | C-10 |
| Manifest semantic warning (SCENE_GAP, SCENE_ORDER_MISMATCH, AUDIO_DURATION_MISMATCH, FOV_WITHOUT_SUPPORT) | `warn` | Continue rendering; warning included in result | Warnings are informational, not blocking |
| Optional plane slot missing from manifest | `warn` | Slot is simply not created — geometry renders without it | Optional slots exist specifically for this case |
| Required plane slot missing from manifest | `fail` | N/A — caught by manifest validation | C-10 |
| Per-plane `opacity !== 1.0` in manifest | `warn` | Plane renders at full opacity; warning in result | V1 limitation (OBJ-035 D18) |
| Image file missing on disk (pre-flight check) | `fail` | N/A — rendering never starts | C-10 extended to assets |
| Texture load failure during `setupScene()` | `fail` | N/A — orchestrator aborts | Production pipeline uses local files; failures are genuine |
| HTTP/data: URL texture load failure | `fail` | N/A — orchestrator aborts | Network errors are not transient in a render pipeline |
| FFmpeg process crashes mid-encode | `fail` | Cleanup all resources, delete partial output | No partial output allowed |
| Chromium/page crash | `fail` | Cleanup all resources, delete partial output | No recovery possible |
| Audio file missing or corrupt | `fail` | N/A — muxing aborts | Audio is specified in manifest; absence is an error |
| Audio duration mismatch vs. scene duration | `warn` | OBJ-014 handles via duration strategy; warning in validation | Non-blocking per OBJ-016 |
| `onProgress` callback throws | `fail` | Treated as cancellation (CANCELLED) | Per OBJ-035 D9 |
| Unknown keys in manifest JSON (at any level) | `fail` | Zod `.strict()` rejects them | Prevents silent typos (`durration` instead of `duration`) |

### FFmpeg Log Excerpt Utility

```typescript
/**
 * Extracts the last N lines from an FFmpeg stderr log string.
 * Used when formatting ENCODE_FAILED and AUDIO_MUX_FAILED errors
 * to show the most relevant portion of FFmpeg's output.
 *
 * @param ffmpegLog — Full FFmpeg stderr string.
 * @param maxLines — Maximum lines to return. Default: 20.
 * @returns The last maxLines lines, or the full log if shorter.
 */
export function extractFFmpegLogTail(ffmpegLog: string, maxLines?: number): string;
```

## Design Decisions

### D-01: No New Error Classes

**Decision:** OBJ-048 does NOT introduce new error classes. Each module (OBJ-011, OBJ-013, OBJ-014, OBJ-035) defines its own error class. OBJ-048 provides classification, formatting, and reporting utilities that operate on those existing types.

**Rationale:** Adding a `DepthkitError` base class or wrapper would require refactoring all existing error classes. The existing error types are well-structured (each has a code, message, and domain-specific fields). OBJ-048's role is to unify their presentation, not their representation.

### D-02: ErrorReport as the Canonical Programmatic Output

**Decision:** `ErrorReport` is the canonical structured error format for programmatic consumers (n8n HTTP endpoint, library API callers). It is JSON-serializable and contains all information needed for both human display and machine routing.

**Rationale:** The n8n endpoint (Appendix A step 5) needs a stable JSON error format to decide whether to retry, report to the user, or escalate. `ErrorReport` provides the `category` field for routing and the `validationErrors` array for detailed diagnostics.

**Key trade-off:** `ErrorReport` deliberately flattens the cause chain into `detail` (a string) rather than nesting error objects. This keeps the JSON output simple and avoids serialization issues with Error instances.

### D-03: Suggestion Generation is Rule-Based, Not LLM-Based

**Decision:** Suggestions are generated by deterministic pattern matching on error codes and cause messages. There is no LLM in the error handling path.

**Rationale:** AP-10 ("Do Not Use the Director Agent in Production") extends to all AI in the runtime path. Suggestions must be instant, deterministic, and useful without network calls.

### D-04: formatManifestErrors Fulfills OBJ-016's Deferred OQ-B

**Decision:** `formatManifestErrors()` is the `formatErrors()` utility that OBJ-016 explicitly deferred: "Deferred to OBJ-048 (CLI error formatting). The loader returns structured data only."

**Rationale:** OBJ-016 correctly separates concerns — it returns structured `ManifestError[]` objects. OBJ-048 provides the formatting layer that both the CLI (OBJ-046) and the programmatic API consume. OBJ-046's `src/cli/format.ts` module already defines `formatValidationErrors()` and `formatOrchestratorError()` — OBJ-048's engine-level formatters provide the underlying implementation that OBJ-046's CLI-specific formatters can delegate to or wrap with color/TTY handling.

### D-05: Relationship to OBJ-046's format.ts

**Decision:** OBJ-048's `src/engine/errors.ts` provides engine-level formatting (no ANSI colors, no TTY awareness, no progress bars). OBJ-046's `src/cli/format.ts` wraps these with CLI-specific concerns (color via `src/cli/colors.ts`, TTY detection, progress bar rendering). The boundary is:
- `src/engine/errors.ts` — pure formatting, usable by any consumer (CLI, HTTP API, tests). Accepts `{ color?: boolean }` option but defaults to false.
- `src/cli/format.ts` — CLI-specific, imports from `src/engine/errors.ts`, adds ANSI escapes, progress bar, file size formatting.

**Rationale:** The n8n HTTP endpoint and programmatic library users need error formatting without CLI dependencies. Separating the layers prevents the engine from depending on CLI utilities.

### D-06: Graceful Degradation is Conservative

**Decision:** The degradation strategy is heavily biased toward `fail`. Only manifest-level warnings and the per-plane opacity V1 limitation produce `warn` outcomes. All runtime failures (texture load, FFmpeg crash, page crash) are fatal.

**Rationale:** C-10 ("fail fast, fail clearly") and AP-04 ("do not conflate rendering with asset generation") mean the engine should never attempt to "fix" broken inputs. The manifest validates upfront; the rendering pipeline assumes valid inputs. A production pipeline that silently degrades produces videos with missing planes or broken scenes — worse than failing and telling the user what's wrong. The one exception (optional plane slots) is by design: geometries explicitly mark slots as optional to support simpler scenes.

### D-07: FFmpeg Log Excerpt Length

**Decision:** `extractFFmpegLogTail()` defaults to the last 20 lines. This is sufficient to capture FFmpeg's error summary without flooding the terminal with encoding statistics.

**Rationale:** FFmpeg's error messages appear at the end of stderr. The encoding progress lines (frame= ... fps= ... ) are noise when diagnosing a failure. 20 lines captures the error context while excluding the progress spam.

### D-08: Error Code Completeness — Consolidated Taxonomy

**Decision:** OBJ-048 does NOT define new error codes. It documents the complete taxonomy of all error codes defined by other modules as a reference. The taxonomy is:

**Manifest Validation Codes (OBJ-004 + OBJ-016):**
| Code | Severity | Description |
|---|---|---|
| `SCHEMA_VALIDATION` | error | Zod structural validation failure |
| `UNKNOWN_GEOMETRY` | error | Scene geometry not registered |
| `UNKNOWN_CAMERA` | error | Scene camera not registered |
| `INCOMPATIBLE_CAMERA` | error | Camera not compatible with geometry |
| `MISSING_REQUIRED_SLOT` | error | Required plane slot missing |
| `UNKNOWN_SLOT` | error | Plane key not in geometry's slots |
| `DUPLICATE_SCENE_ID` | error | Two+ scenes share same id |
| `SCENE_OVERLAP` | error | Invalid scene time overlap |
| `CROSSFADE_NO_ADJACENT` | error | Crossfade without adjacent scene |
| `SCENE_GAP` | warning | Time gap between consecutive scenes |
| `SCENE_ORDER_MISMATCH` | warning | Array order ≠ start_time order |
| `AUDIO_DURATION_MISMATCH` | warning | Audio vs scene duration differ |
| `FOV_WITHOUT_SUPPORT` | warning | FOV params on non-FOV camera |
| `FILE_NOT_FOUND` | error | ENOENT on file read |
| `FILE_READ_ERROR` | error | Non-ENOENT file read failure |
| `INVALID_JSON` | error | File contains unparseable JSON |

**Orchestrator Codes (OBJ-035):**
| Code | Category | Description |
|---|---|---|
| `MANIFEST_INVALID` | validation | Manifest validation failed |
| `BROWSER_LAUNCH_FAILED` | browser | Puppeteer/Chromium failed to start |
| `PAGE_INIT_FAILED` | browser | Three.js page initialization failed |
| `SCENE_SETUP_FAILED` | asset | Scene setup failed (texture load or missing images) |
| `RENDER_FAILED` | render | Frame rendering failed on the page |
| `CAPTURE_FAILED` | render | Frame capture failed |
| `ENCODE_FAILED` | encode | FFmpeg encoding failed |
| `AUDIO_MUX_FAILED` | audio | Audio muxing failed |
| `CANCELLED` | cancelled | Cancelled via onProgress callback |
| `GEOMETRY_NOT_FOUND` | validation | Geometry missing from geometryRegistry |
| `CAMERA_NOT_FOUND` | validation | Camera preset missing from cameraRegistry |

**Page Protocol Codes (OBJ-011):**
| Code | Description |
|---|---|
| `NOT_INITIALIZED` | Page not initialized |
| `ALREADY_INITIALIZED` | Page already initialized |
| `SCENE_EXISTS` | Scene ID already set up |
| `SCENE_NOT_FOUND` | Scene ID not found |
| `INVALID_COMMAND` | Invalid command (empty passes, empty sceneId) |
| `TEXTURE_LOAD_FAILED` | Texture failed to load |
| `RENDER_ERROR` | Three.js render error |
| `WEBGL_ERROR` | WebGL context error |

**FFmpeg Encoder Errors (OBJ-013):** `FFmpegEncoderError` with `exitCode` and `ffmpegLog`.

**Audio Muxer Errors (OBJ-014):** `AudioMuxerError` with `exitCode` and `ffmpegLog`.

**Rationale:** A single reference table prevents downstream consumers from having to read 5+ spec documents to understand the error space. The taxonomy is documentation, not new code.

## Acceptance Criteria

### Error Classification

- [ ] **AC-01:** `classifyError('MANIFEST_INVALID')` returns `'validation'`.
- [ ] **AC-02:** `classifyError('SCENE_SETUP_FAILED')` returns `'asset'`.
- [ ] **AC-03:** `classifyError('BROWSER_LAUNCH_FAILED')` returns `'browser'`.
- [ ] **AC-04:** `classifyError('PAGE_INIT_FAILED')` returns `'browser'`.
- [ ] **AC-05:** `classifyError('RENDER_FAILED')` returns `'render'`.
- [ ] **AC-06:** `classifyError('CAPTURE_FAILED')` returns `'render'`.
- [ ] **AC-07:** `classifyError('ENCODE_FAILED')` returns `'encode'`.
- [ ] **AC-08:** `classifyError('AUDIO_MUX_FAILED')` returns `'audio'`.
- [ ] **AC-09:** `classifyError('CANCELLED')` returns `'cancelled'`.
- [ ] **AC-10:** `classifyError('GEOMETRY_NOT_FOUND')` returns `'validation'`.
- [ ] **AC-11:** `classifyError('CAMERA_NOT_FOUND')` returns `'validation'`.
- [ ] **AC-12:** Every `OrchestratorErrorCode` value is covered by `classifyError` — no unhandled codes.

### Error Report Creation

- [ ] **AC-13:** `createErrorReport()` from an `OrchestratorError` with code `MANIFEST_INVALID` produces an `ErrorReport` with `category: 'validation'`, `code: 'MANIFEST_INVALID'`, and `validationErrors` populated from `error.validationErrors`.
- [ ] **AC-14:** `createErrorReport()` from an `OrchestratorError` with code `ENCODE_FAILED` whose cause is an `FFmpegEncoderError` includes the FFmpeg log tail (up to 20 lines) in `detail`.
- [ ] **AC-15:** `createErrorReport()` from an `OrchestratorError` with `frame >= 0` includes the frame number in `frame`.
- [ ] **AC-16:** `createValidationErrorReport()` produces `category: 'validation'`, `code: 'MANIFEST_INVALID'`, and the full `ManifestError[]` in `validationErrors`.
- [ ] **AC-17:** `createUnexpectedErrorReport()` from a plain `Error` produces `category: 'internal'`, `code: 'INTERNAL_ERROR'`, and the error message in `message`.
- [ ] **AC-18:** `createUnexpectedErrorReport()` from a non-Error value (e.g., string, null) produces `category: 'internal'` and a descriptive message.
- [ ] **AC-19:** All `ErrorReport` objects produced by any `create*` function are JSON-serializable (no circular references, no functions, no class instances in the output).

### Manifest Error Formatting

- [ ] **AC-20:** `formatManifestErrors()` with a single error produces `"  ✗ scenes[0].geometry: Scene 'scene_001': geometry 'tunl' is not registered. ... (UNKNOWN_GEOMETRY)"`.
- [ ] **AC-21:** `formatManifestErrors()` with mixed errors and warnings lists errors first, then warnings.
- [ ] **AC-22:** `formatManifestErrors()` with a file-level error (empty `path`) omits the path prefix: `"  ✗ Manifest file not found: ./bad.json (FILE_NOT_FOUND)"`.
- [ ] **AC-23:** `formatManifestErrors()` with `{ color: true }` wraps error lines in red and warning lines in yellow (ANSI escape codes present in output).
- [ ] **AC-24:** `formatManifestErrors()` with `{ color: false }` or default produces no ANSI escape codes.

### Orchestrator Error Formatting

- [ ] **AC-25:** `formatOrchestratorError()` for `MANIFEST_INVALID` includes all validation errors formatted via `formatManifestErrors()`.
- [ ] **AC-26:** `formatOrchestratorError()` for `ENCODE_FAILED` with an `FFmpegEncoderError` cause includes the FFmpeg log tail.
- [ ] **AC-27:** `formatOrchestratorError()` for `RENDER_FAILED` with `frame: 42` includes `"Frame: 42"` in the output.
- [ ] **AC-28:** `formatOrchestratorError()` with `{ verbose: true }` includes the full cause chain (cause.message, cause.cause.message, etc.).
- [ ] **AC-29:** `formatOrchestratorError()` with `{ verbose: false }` (default) includes only the top-level cause message (one level deep).

### Suggestion Generation

- [ ] **AC-30:** `generateSuggestions()` for `MANIFEST_INVALID` always includes the `"Run 'depthkit validate'"` suggestion.
- [ ] **AC-31:** `generateSuggestions()` for `ENCODE_FAILED` always includes the FFmpeg version check suggestion.
- [ ] **AC-32:** `generateSuggestions()` for `BROWSER_LAUNCH_FAILED` always includes the Chromium installation suggestion.
- [ ] **AC-33:** `generateSuggestions()` for `RENDER_FAILED` always includes the `--debug` suggestion.
- [ ] **AC-34:** `generateSuggestions()` for `CANCELLED` includes the re-run suggestion.
- [ ] **AC-35:** `generateSuggestions()` returns an empty array for error codes with no matching rules (should not happen with exhaustive rules, but a defensive default).

### FFmpeg Log Utility

- [ ] **AC-36:** `extractFFmpegLogTail("line1\nline2\n...line25", 20)` returns the last 20 lines.
- [ ] **AC-37:** `extractFFmpegLogTail("short\nlog", 20)` returns both lines (full log when shorter than maxLines).
- [ ] **AC-38:** `extractFFmpegLogTail("", 20)` returns empty string.
- [ ] **AC-39:** `extractFFmpegLogTail(log)` with no maxLines argument defaults to 20 lines.

### Graceful Degradation

- [ ] **AC-40:** The degradation rules table is consistent with OBJ-016's error severities — every `severity: "warning"` code maps to `warn`, every `severity: "error"` code maps to `fail`.
- [ ] **AC-41:** The degradation rules table is consistent with OBJ-035's behavior — SCENE_SETUP_FAILED is fatal, per-plane opacity is a warning.

### JSON Serialization

- [ ] **AC-42:** `formatErrorReportJson()` produces valid JSON parseable by `JSON.parse()`.
- [ ] **AC-43:** `formatErrorReportJson()` uses 2-space indentation.

## Edge Cases and Error Handling

### EC-01: OrchestratorError with No Cause
`createErrorReport()` where `error.cause` is `undefined`. `detail` is `null`. No FFmpeg log excerpt. Suggestions still generated based on code alone.

### EC-02: OrchestratorError with Deeply Nested Cause Chain
`error.cause` is an `FFmpegEncoderError`, whose own cause may exist. `formatOrchestratorError()` with `verbose: true` walks the chain up to 5 levels deep, printing each level. With `verbose: false`, only `error.cause.message` is shown.

### EC-03: MANIFEST_INVALID with Zero validationErrors
Theoretically impossible (OBJ-035 only throws MANIFEST_INVALID when `loadManifest` returns `success: false` with errors), but defensively handled: `ErrorReport.validationErrors` is `[]`, `detail` is `null`, suggestions still include the validate command.

### EC-04: FFmpegEncoderError with Empty ffmpegLog
`extractFFmpegLogTail("")` returns `""`. `detail` in the ErrorReport says "FFmpeg log is empty."

### EC-05: createUnexpectedErrorReport with null
`createUnexpectedErrorReport(null)` produces `message: "An unexpected error occurred (null)"`, `category: 'internal'`.

### EC-06: createUnexpectedErrorReport with a string
`createUnexpectedErrorReport("something broke")` produces `message: "An unexpected error occurred: something broke"`, `category: 'internal'`.

### EC-07: formatManifestErrors with Empty Array
Returns empty string. No header, no content.

### EC-08: Very Long Validation Error List (100+ errors)
No truncation. All errors are formatted. The CLI layer (OBJ-046) may choose to truncate display, but the engine formatting layer is complete.

### EC-09: ManifestError with Very Long Message
No truncation in engine formatter. CLI layer may wrap lines.

### EC-10: Concurrent Error Report Creation
All functions are pure and stateless. No shared mutable state. Thread-safe by construction.

### EC-11: ENCODE_FAILED Where Cause is Not FFmpegEncoderError
The cause may be any Error (e.g., from output directory not existing). `detail` shows `cause.message`. No FFmpeg log excerpt. Suggestions still include the FFmpeg check.

### EC-12: AUDIO_MUX_FAILED Where Cause is AudioMuxerError with ffmpegLog
`detail` includes `extractFFmpegLogTail(cause.ffmpegLog)`, same treatment as ENCODE_FAILED.

## Test Strategy

### Unit Tests: `test/unit/engine/errors.test.ts`

**Classification tests (AC-01 through AC-12):**
1. Test each `OrchestratorErrorCode` value against `classifyError()`. Assert correct `ErrorCategory`.
2. Test exhaustiveness: iterate all `OrchestratorErrorCode` values (obtained from the type) and verify `classifyError` returns a valid `ErrorCategory` for each.

**ErrorReport creation tests (AC-13 through AC-19):**
3. Create `OrchestratorError` with `MANIFEST_INVALID` and mock `validationErrors`. Call `createErrorReport()`. Assert `category`, `code`, `validationErrors`, `frame`.
4. Create `OrchestratorError` with `ENCODE_FAILED`, cause is `FFmpegEncoderError` with a 30-line log. Assert `detail` contains 20-line excerpt.
5. Create `OrchestratorError` with `RENDER_FAILED`, frame=42. Assert `frame: 42`.
6. Create `OrchestratorError` with `SCENE_SETUP_FAILED`, cause message lists missing files. Assert `detail` contains file paths.
7. `createValidationErrorReport([...errors])` — assert structure.
8. `createUnexpectedErrorReport(new Error("boom"))` — assert `category: 'internal'`.
9. `createUnexpectedErrorReport(null)` — assert `category: 'internal'`, message mentions null.
10. `createUnexpectedErrorReport("string error")` — assert message includes the string.
11. JSON-serialize every ErrorReport from tests 3-10 via `formatErrorReportJson()` and `JSON.parse()` the result — no throws.

**Manifest error formatting tests (AC-20 through AC-24):**
12. Single `ManifestError` with path `"scenes[0].geometry"` — verify format.
13. Mixed errors and warnings — verify ordering (errors first).
14. File-level error (empty path) — verify path prefix omitted.
15. Color enabled — verify ANSI escape codes present.
16. Color disabled — verify no ANSI codes.
17. Empty array — verify empty string returned.

**Orchestrator error formatting tests (AC-25 through AC-29):**
18. `MANIFEST_INVALID` — verify validation errors embedded.
19. `ENCODE_FAILED` with `FFmpegEncoderError` cause — verify FFmpeg log tail.
20. `RENDER_FAILED` at frame 42 — verify frame line.
21. Verbose mode — verify cause chain (create a 3-level chain).
22. Non-verbose mode — verify only one level of cause shown.

**Suggestion generation tests (AC-30 through AC-35):**
23. Each OrchestratorErrorCode: verify at least one suggestion returned.
24. `MANIFEST_INVALID` — verify validate command suggestion.
25. `ENCODE_FAILED` — verify FFmpeg check suggestion.
26. `BROWSER_LAUNCH_FAILED` — verify Chromium install suggestion.
27. `RENDER_FAILED` — verify `--debug` suggestion.
28. `ENCODE_FAILED` with FFmpegEncoderError cause with `exitCode: 1` — verify exit code mentioned in suggestion.
29. `MANIFEST_INVALID` with nested `INVALID_JSON` error — verify JSON syntax suggestion.

**FFmpeg log utility tests (AC-36 through AC-39):**
30. 25-line log, maxLines=20 — returns last 20.
31. 5-line log, maxLines=20 — returns all 5.
32. Empty string — returns empty string.
33. Default maxLines — verify 20.
34. Single-line log — returns the single line.

### Relevant Testable Claims

- **TC-07:** The `formatManifestErrors()` tests verify that validation errors are presented with actionable messages (the "actionable error messages with context" part of OBJ-048's description).
- **SC-06:** The degradation rules table and AC-40/AC-41 ensure "no manifest that passes validation produces a rendering error" by documenting the complete boundary between warnings and fatal errors.

## Integration Points

### Depends On

| Dependency | What OBJ-048 Uses |
|---|---|
| **OBJ-016** (Manifest Loader) | `ManifestError` type for formatting. Error code values for suggestion matching. |
| **OBJ-035** (Orchestrator) | `OrchestratorError` class, `OrchestratorErrorCode` type, `OrchestratorResult.warnings` for degradation verification. |
| **OBJ-004** (Manifest Schema) | `ManifestError` type definition. |
| **OBJ-013** (FFmpeg Encoder) | `FFmpegEncoderError` class for cause inspection and FFmpeg log extraction. |
| **OBJ-014** (Audio Muxer) | `AudioMuxerError` class for cause inspection and FFmpeg log extraction. |
| **OBJ-011** (Page Protocol) | `PageProtocolError` class for cause inspection. `PageErrorCode` for taxonomy documentation. |

### Consumed By

| Downstream | How It Uses OBJ-048 |
|---|---|
| **OBJ-046** (CLI) | `src/cli/format.ts` delegates to `formatManifestErrors()` and `formatOrchestratorError()` for the core formatting, wrapping with CLI-specific color and TTY handling. `formatValidationErrors()` in OBJ-046 can call `formatManifestErrors()` directly. `formatOrchestratorError()` in OBJ-046 can call OBJ-048's `formatOrchestratorError()` with appropriate options. |
| **n8n HTTP endpoint** (future) | Calls `createErrorReport()` or `createValidationErrorReport()` and returns `formatErrorReportJson()` as the HTTP response body. |
| **OBJ-077** (End-to-end integration) | Uses `ErrorReport` to verify error behavior in integration tests. |
| **OBJ-078** (Production readiness) | References the degradation rules and error taxonomy. |

### File Placement

```
depthkit/
  src/
    engine/
      errors.ts              # NEW — Error classification, formatting,
                             #       suggestions, ErrorReport, degradation rules
  test/
    unit/
      engine/
        errors.test.ts       # NEW — All unit tests for error utilities
```

## Open Questions

### OQ-A: Should ErrorReport include a `stack` field?
Stack traces are useful for debugging but leak implementation details. Current decision: omit from ErrorReport (JSON API output). `formatOrchestratorError()` with `verbose: true` shows the stack in CLI output via the cause chain, but the structured `ErrorReport` does not include it. This can be revisited if the n8n endpoint needs it for logging.

### OQ-B: Should there be a `DepthkitError` base class?
All existing error classes (`OrchestratorError`, `FFmpegEncoderError`, `AudioMuxerError`, `PageProtocolError`) extend `Error` independently. A shared base class would enable `instanceof DepthkitError` checks. Current decision: no — the `createErrorReport()` function already handles all known types via duck-typing (checking for `.code`, `.validationErrors`, `.ffmpegLog` properties). A base class adds a refactoring cost with no clear benefit.

### OQ-C: Should formatManifestErrors truncate at a threshold?
With 100+ validation errors (possible with a massively broken manifest), the formatted output could be very long. Current decision: no truncation in the engine layer. The CLI layer (OBJ-046) may add truncation with "... and N more errors" if needed.

---

I believe this spec covers the complete scope of OBJ-048: the consolidated error taxonomy, the formatting utility deferred by OBJ-016, structured error reports for programmatic consumers, graceful degradation rules, suggestion generation, and clear integration with OBJ-046's CLI layer. I'd like the challenger to review and identify any gaps, ambiguities, or inconsistencies.

---

## Round 2 — spec_challenger

I've carefully reviewed the OBJ-048 proposal against the seed, both dependency specs, and OBJ-046's verified spec. The spec is well-structured and covers the right surface area. I'll explicitly approve what's sound, then enumerate the issues.

## What's Sound

- **D-01 (No new error classes)**: Correct call. The existing error classes are well-defined by their originating modules. Adding a base class would be a cross-cutting refactor with no payoff.
- **D-03 (Rule-based suggestions, not LLM)**: Correct per AP-10.
- **D-06 (Conservative degradation)**: Correct per C-10. The bias toward `fail` is right.
- **D-08 (Consolidated taxonomy as documentation)**: Valuable. Having the complete error landscape in one place is exactly what a consumer needs.
- **ErrorReport structure**: Clean, JSON-serializable, sufficient for n8n routing. The `category` + `code` + `suggestions` pattern is practical.
- **Edge cases EC-01 through EC-12**: Thorough coverage.
- **Test strategy**: Comprehensive, maps well to acceptance criteria.

## Issues

### Issue 1 — Major: Name collision and ambiguous relationship with OBJ-046

OBJ-046 (status: `verified`, review: `approved`) already exports from `src/cli/format.ts`:
```typescript
export function formatValidationErrors(errors: ManifestError[], color: boolean): string;
export function formatOrchestratorError(error: OrchestratorError, verbose: boolean, color: boolean): string;
```

OBJ-048 proposes in `src/engine/errors.ts`:
```typescript
export function formatManifestErrors(errors: ManifestError[], options?: { color?: boolean }): string;
export function formatOrchestratorError(error: OrchestratorError, options?: { color?: boolean; verbose?: boolean }): string;
```

`formatOrchestratorError` is defined in both modules with different signatures. D-05 says "OBJ-046's `src/cli/format.ts` wraps these with CLI-specific concerns" and the Consumed By table says OBJ-046 "delegates to" OBJ-048. But **OBJ-046 does not depend on OBJ-048** in the progress map, and OBJ-046 is already verified. OBJ-048 cannot retroactively become an upstream dependency of a verified objective.

An implementer will ask: do I implement `formatOrchestratorError` twice (once in engine, once in CLI)? Does OBJ-046's implementation call OBJ-048? The spec creates ambiguity that invites guessing.

**Proposed fix**: 
1. Remove `formatOrchestratorError` and `formatManifestErrors` from OBJ-048's interface. OBJ-046 already owns CLI-facing formatting.
2. OBJ-048's unique value is: `ErrorReport` (structured JSON for programmatic consumers), `classifyError()`, `createErrorReport()` / `createValidationErrorReport()` / `createUnexpectedErrorReport()`, `generateSuggestions()`, `extractFFmpegLogTail()`, and the degradation rules documentation. These do not overlap with OBJ-046.
3. If engine-level plain-text formatting is truly needed (for cases where OBJ-046 isn't available, e.g., the n8n endpoint), name them distinctly: `renderErrorText()` and `renderValidationErrorsText()`, and document that these exist for non-CLI consumers only.

Alternatively, if you want to keep the formatters, the spec must explicitly state: "OBJ-046 was specified before OBJ-048. OBJ-048's formatting functions are independent, parallel implementations for non-CLI consumers. OBJ-046's functions are NOT required to delegate to OBJ-048. Both may coexist."

### Issue 2 — Major: Degradation rules acceptance criteria are untestable

AC-40: "The degradation rules table is consistent with OBJ-016's error severities."  
AC-41: "The degradation rules table is consistent with OBJ-035's behavior."

The degradation rules are described as "a reference specification, not a runtime function." If there's no runtime artifact, these ACs can only be verified by someone reading two documents side-by-side. That's a review checklist item, not a testable acceptance criterion.

**Proposed fix**: Either:
- **(a)** Export a runtime constant `DEGRADATION_RULES: Record<string, DegradationAction>` mapping every known error code/condition to its action, and write unit tests that verify every `ManifestError` code with `severity: "error"` maps to `'fail'` and every code with `severity: "warning"` maps to `'warn'`. This makes AC-40/AC-41 programmatically testable.
- **(b)** Reclassify AC-40/AC-41 as documentation review criteria (not checkboxes in a test suite) and remove them from the numbered AC list. Add a note in the test strategy: "Degradation rules are verified by spec review, not automated tests."

I'd lean toward (a) — a small data structure is cheap and prevents drift.

### Issue 3 — Minor: Cause chain type detection strategy unspecified

`createErrorReport()` must distinguish between `FFmpegEncoderError` (has `.ffmpegLog`, `.exitCode`), `AudioMuxerError` (has `.ffmpegLog`, `.exitCode`), `PageProtocolError` (has `.code` as `PageErrorCode`), and generic `Error`. The spec says in D-02 that it inspects the cause chain but never says *how*.

An implementer choosing `instanceof` gets different behavior from one choosing duck-typing (`'ffmpegLog' in error`). This matters because `OrchestratorError.cause` is typed as `Error | undefined`, not as a union of the specific error types.

**Proposed fix**: Add a design decision: "D-09: Cause chain inspection uses `instanceof` checks against the imported error classes (`FFmpegEncoderError`, `AudioMuxerError`, `PageProtocolError`). The module imports these classes. If `instanceof` fails (e.g., error was serialized/reconstructed across a process boundary), the function falls back to duck-typing: checking for `ffmpegLog` property (string) → treat as FFmpeg error, checking for `code` property matching a `PageErrorCode` value → treat as page error."

### Issue 4 — Minor: Verbose cause chain depth limit buried in edge cases

EC-02 says "walks the chain up to 5 levels deep" for `verbose: true`. This is a behavioral contract that belongs in the interface specification or a design decision, not hidden in edge cases where an implementer might miss it.

**Proposed fix**: Create D-09 (or D-10 if D-09 is used above): "Cause chain traversal depth limit: `formatOrchestratorError()` with `verbose: true` traverses `cause` references up to 5 levels. This prevents infinite output from hypothetical circular cause chains and keeps output manageable. Each level is indented and prefixed with 'Caused by:'."

### Issue 5 — Minor: `color` option on engine-level formatters contradicts D-05

D-05 says: "OBJ-048's `src/engine/errors.ts` provides engine-level formatting (no ANSI colors, no TTY awareness)." But then `formatManifestErrors` and `formatOrchestratorError` accept `{ color?: boolean }` and AC-23 tests for ANSI escape codes.

These two statements are contradictory. Either the engine layer is color-free, or it supports color via an explicit opt-in. Both are valid designs, but the spec says both simultaneously.

**Proposed fix**: If you keep the formatters (see Issue 1), amend D-05 to: "The engine layer does not auto-detect TTY or default to color. When `color: true` is explicitly passed, it emits ANSI escape codes. The default is `color: false` (no ANSI codes). This is distinct from OBJ-046, which auto-detects TTY and defaults to color when stdout is a terminal."

### Issue 6 — Minor: Suggestion rules based on cause message string matching are fragile

Multiple suggestion rules check `cause.message` for substrings like `"timeout"`, `"network"`, `"ENOENT"`, `"chrome"`. If an upstream module changes its error wording, these rules silently produce worse suggestions.

This is acknowledged as best-effort, which is fine. But the spec should document this fragility explicitly so maintainers know.

**Proposed fix**: Add a note to the suggestion rules section: "Suggestion rules that match on `cause.message` substrings are best-effort heuristics. If an upstream module changes its error message format, the worst-case outcome is a missing suggestion (the base suggestion for the error code still applies). There is no correctness risk — only a UX degradation."

---

Those are my issues: 2 major, 4 minor. Please address Issues 1 and 2 substantively. Issues 3–6 need explicit resolution but are straightforward.

---

## Round 3 — spec_author

Here is the revised specification addressing all six issues.

---

# Specification: OBJ-048 — Error Handling and Reporting Strategy

## Summary

OBJ-048 defines the unified error handling and reporting strategy across the entire depthkit engine. It specifies: (1) a consolidated error taxonomy cataloguing every error type from manifest validation (OBJ-016), page protocol (OBJ-011), FFmpeg encoding (OBJ-013), audio muxing (OBJ-014), and orchestration (OBJ-035); (2) an `ErrorReport` structure and creation utilities for programmatic consumers (n8n HTTP endpoint, library API); (3) error classification and suggestion generation; (4) an exported `DEGRADATION_RULES` constant for testable graceful degradation policy; (5) an `extractFFmpegLogTail()` utility; and (6) documentation of the complete error code registry. Plain-text formatting for CLI display is OBJ-046's responsibility — OBJ-048 provides the structured data layer that OBJ-046 and other consumers build on.

## Interface Contract

### Module: `src/engine/errors.ts`

This module provides error classification, structured reporting, and suggestion generation. It does NOT define new error classes — those are defined by their originating modules (OBJ-004, OBJ-011, OBJ-013, OBJ-014, OBJ-035). It does NOT provide plain-text formatting for CLI display — that is OBJ-046's `src/cli/format.ts`. This module provides the structured data layer that all consumers (CLI, HTTP API, tests) build on.

```typescript
// src/engine/errors.ts

import type { ManifestError } from '../manifest/schema.js';
import type { OrchestratorError, OrchestratorErrorCode } from './orchestrator.js';
import { FFmpegEncoderError } from './ffmpeg-encoder.js';
import { AudioMuxerError } from './audio-muxer.js';
import { PageProtocolError } from './protocol-types.js';
import type { PageErrorCode } from './protocol-types.js';

// ────────────────────────────────────────────
// Error Classification
// ────────────────────────────────────────────

/**
 * Top-level error categories for programmatic consumers.
 * Maps the diverse error types across the engine into a small
 * set of buckets that an HTTP API or n8n workflow can switch on.
 */
export type ErrorCategory =
  | 'validation'     // Manifest is invalid (schema or semantic)
  | 'asset'          // Image/audio files missing or unreadable
  | 'browser'        // Puppeteer/Chromium launch or page init failure
  | 'render'         // Three.js page-side rendering failure
  | 'encode'         // FFmpeg encoding failure
  | 'audio'          // Audio muxing failure
  | 'cancelled'      // User-initiated cancellation
  | 'internal'       // Unexpected/unclassified error
  ;

/**
 * A structured error report suitable for JSON serialization.
 * This is the canonical error output format for programmatic consumers
 * (n8n HTTP endpoint, library API callers).
 */
export interface ErrorReport {
  /** Whether the operation succeeded. Always false for error reports. */
  success: false;

  /** Top-level error category for routing/switching. */
  category: ErrorCategory;

  /**
   * Machine-readable error code. For OrchestratorErrors, this is the
   * OrchestratorErrorCode. For standalone ManifestErrors, this is
   * 'MANIFEST_INVALID'. For unexpected errors, this is 'INTERNAL_ERROR'.
   */
  code: string;

  /** Human-readable summary of the error. One sentence. */
  message: string;

  /**
   * Detailed validation errors, if category is 'validation'.
   * Each entry is a ManifestError from OBJ-016.
   * Empty array for non-validation errors.
   */
  validationErrors: ManifestError[];

  /**
   * Frame number where the error occurred, if applicable.
   * -1 if not frame-related.
   */
  frame: number;

  /**
   * Human-readable detail string with contextual information.
   * For encode errors: includes FFmpeg stderr excerpt.
   * For asset errors: lists missing file paths.
   * For render errors: includes the page error code and details.
   * null if no additional detail is available.
   */
  detail: string | null;

  /**
   * Suggested remediation action(s) for the user.
   * Each string is a single actionable suggestion.
   * Empty array if no specific remediation is known.
   */
  suggestions: string[];
}

// ────────────────────────────────────────────
// Classification Functions
// ────────────────────────────────────────────

/**
 * Classifies an OrchestratorErrorCode into an ErrorCategory.
 *
 * Mapping:
 *   MANIFEST_INVALID        → 'validation'
 *   SCENE_SETUP_FAILED      → 'asset'
 *   BROWSER_LAUNCH_FAILED   → 'browser'
 *   PAGE_INIT_FAILED        → 'browser'
 *   RENDER_FAILED           → 'render'
 *   CAPTURE_FAILED          → 'render'
 *   ENCODE_FAILED           → 'encode'
 *   AUDIO_MUX_FAILED        → 'audio'
 *   CANCELLED               → 'cancelled'
 *   GEOMETRY_NOT_FOUND      → 'validation'
 *   CAMERA_NOT_FOUND        → 'validation'
 */
export function classifyError(code: OrchestratorErrorCode): ErrorCategory;

// ────────────────────────────────────────────
// Error Report Creation
// ────────────────────────────────────────────

/**
 * Creates a structured ErrorReport from an OrchestratorError.
 *
 * Extracts the error code, message, frame number, validation errors
 * (if MANIFEST_INVALID), and generates context-specific detail and
 * suggestions based on the error code and cause chain.
 *
 * Cause chain inspection: uses `instanceof` checks against imported
 * error classes (FFmpegEncoderError, AudioMuxerError, PageProtocolError).
 * See D-09 for fallback behavior.
 */
export function createErrorReport(error: OrchestratorError): ErrorReport;

/**
 * Creates a structured ErrorReport from a ManifestResult with
 * success: false. Used by the `validate` command which doesn't
 * go through the orchestrator.
 */
export function createValidationErrorReport(errors: ManifestError[]): ErrorReport;

/**
 * Creates a structured ErrorReport from an unknown/unexpected error.
 * Used as a catch-all for errors that aren't OrchestratorError.
 */
export function createUnexpectedErrorReport(error: unknown): ErrorReport;

// ────────────────────────────────────────────
// Suggestion Generation
// ────────────────────────────────────────────

/**
 * Generates actionable remediation suggestions for an error.
 * The suggestions are context-specific based on the error code,
 * cause chain, and any nested error details.
 *
 * Returns an array of plain-text suggestion strings.
 *
 * Note: Rules that match on `cause.message` substrings are best-effort
 * heuristics. If an upstream module changes its error message format,
 * the worst-case outcome is a missing context-specific suggestion (the
 * base suggestion for the error code still applies). There is no
 * correctness risk — only a UX degradation.
 */
export function generateSuggestions(error: OrchestratorError): string[];

// ────────────────────────────────────────────
// FFmpeg Log Utility
// ────────────────────────────────────────────

/**
 * Extracts the last N lines from an FFmpeg stderr log string.
 * Used when creating ErrorReports for ENCODE_FAILED and AUDIO_MUX_FAILED
 * errors to include the most relevant portion of FFmpeg's output.
 *
 * @param ffmpegLog — Full FFmpeg stderr string.
 * @param maxLines — Maximum lines to return. Default: 20.
 * @returns The last maxLines lines, or the full log if shorter.
 *          Empty string if input is empty.
 */
export function extractFFmpegLogTail(ffmpegLog: string, maxLines?: number): string;

// ────────────────────────────────────────────
// JSON Serialization
// ────────────────────────────────────────────

/**
 * Formats an ErrorReport as a JSON string.
 * Suitable for HTTP API responses and structured logging.
 * Uses JSON.stringify with 2-space indentation.
 */
export function formatErrorReportJson(report: ErrorReport): string;

// ────────────────────────────────────────────
// Degradation Rules
// ────────────────────────────────────────────

/**
 * The action to take for a given error condition.
 * 'fail' = throw / abort rendering.
 * 'warn' = emit a warning, continue with described fallback behavior.
 */
export type DegradationAction = 'fail' | 'warn';

/**
 * A single degradation rule entry.
 */
export interface DegradationRule {
  /** The action: fail or warn. */
  action: DegradationAction;
  /** Description of the fallback behavior when action is 'warn'. 
   *  null when action is 'fail'. */
  fallback: string | null;
}

/**
 * Exported constant mapping condition keys to degradation actions.
 * This is the single source of truth for the fail-vs-warn boundary.
 *
 * Keys are descriptive condition identifiers (not error codes, because
 * some conditions span multiple codes or are not errors at all).
 *
 * Programmatically testable: unit tests verify every ManifestError code
 * with severity "error" maps to a condition with action "fail", and
 * every code with severity "warning" maps to action "warn".
 */
export const DEGRADATION_RULES: Record<string, DegradationRule>;
```

### Degradation Rules (Complete Table)

The `DEGRADATION_RULES` constant contains the following entries:

| Key | Action | Fallback | Rationale |
|---|---|---|---|
| `manifest_structural_error` | `fail` | null | C-10: fail fast |
| `manifest_semantic_error` | `fail` | null | C-10: fail fast |
| `manifest_scene_gap_warning` | `warn` | `"Engine renders black frames during the gap"` | Informational |
| `manifest_scene_order_warning` | `warn` | `"Engine sorts scenes by start_time internally"` | Informational |
| `manifest_audio_duration_mismatch` | `warn` | `"Engine uses scene durations as specified; audio muxer handles alignment"` | Non-blocking |
| `manifest_fov_without_support` | `warn` | `"FOV values are ignored for this camera preset"` | Non-blocking |
| `optional_plane_slot_missing` | `warn` | `"Slot is not created; geometry renders without it"` | Optional slots exist for this |
| `per_plane_opacity_unsupported` | `warn` | `"Plane renders at full opacity (V1 limitation)"` | OBJ-035 D18 |
| `required_plane_slot_missing` | `fail` | null | C-10 via manifest validation |
| `image_file_missing` | `fail` | null | C-10 extended to assets |
| `texture_load_failure` | `fail` | null | Production uses local files |
| `http_texture_load_failure` | `fail` | null | Network errors not transient in render |
| `ffmpeg_crash` | `fail` | null | No partial output |
| `chromium_crash` | `fail` | null | No recovery possible |
| `audio_file_missing_or_corrupt` | `fail` | null | Specified in manifest; absence is error |
| `onprogress_throws` | `fail` | null | OBJ-035 D9: treated as cancellation |
| `unknown_manifest_keys` | `fail` | null | Zod `.strict()` prevents typos |

### Manifest Error Code to Degradation Mapping

For programmatic testability, the following mapping connects ManifestError codes to degradation rule keys:

| ManifestError Code | Severity | Degradation Rule Key |
|---|---|---|
| `SCHEMA_VALIDATION` | error | `manifest_structural_error` |
| `UNKNOWN_GEOMETRY` | error | `manifest_semantic_error` |
| `UNKNOWN_CAMERA` | error | `manifest_semantic_error` |
| `INCOMPATIBLE_CAMERA` | error | `manifest_semantic_error` |
| `MISSING_REQUIRED_SLOT` | error | `required_plane_slot_missing` |
| `UNKNOWN_SLOT` | error | `manifest_semantic_error` |
| `DUPLICATE_SCENE_ID` | error | `manifest_semantic_error` |
| `SCENE_OVERLAP` | error | `manifest_semantic_error` |
| `CROSSFADE_NO_ADJACENT` | error | `manifest_semantic_error` |
| `SCENE_GAP` | warning | `manifest_scene_gap_warning` |
| `SCENE_ORDER_MISMATCH` | warning | `manifest_scene_order_warning` |
| `AUDIO_DURATION_MISMATCH` | warning | `manifest_audio_duration_mismatch` |
| `FOV_WITHOUT_SUPPORT` | warning | `manifest_fov_without_support` |
| `FILE_NOT_FOUND` | error | `manifest_structural_error` |
| `FILE_READ_ERROR` | error | `manifest_structural_error` |
| `INVALID_JSON` | error | `manifest_structural_error` |

This mapping is exported as a constant for test verification:

```typescript
/**
 * Maps each ManifestError code to its degradation rule key.
 * Used by unit tests to verify consistency between OBJ-016's
 * error severities and OBJ-048's degradation rules.
 */
export const MANIFEST_CODE_TO_DEGRADATION: Record<string, string>;
```

### Suggestion Rules (Exhaustive)

The `generateSuggestions()` function applies the following rules, returning all matching suggestions:

| OrchestratorErrorCode | Condition | Suggestion |
|---|---|---|
| `MANIFEST_INVALID` | Always | `"Run 'depthkit validate <manifest>' to see all errors."` |
| `MANIFEST_INVALID` | Any error with code `UNKNOWN_GEOMETRY` | `"Check the geometry name against the available list in the error message."` |
| `MANIFEST_INVALID` | Any error with code `UNKNOWN_CAMERA` | `"Check the camera name against the available list in the error message."` |
| `MANIFEST_INVALID` | Any error with code `FILE_NOT_FOUND` | `"Verify the manifest file path exists and is readable."` |
| `MANIFEST_INVALID` | Any error with code `INVALID_JSON` | `"Check for syntax errors: trailing commas, unquoted keys, or missing brackets."` |
| `SCENE_SETUP_FAILED` | Always | `"Verify that all image files exist at the paths specified in the manifest."` |
| `SCENE_SETUP_FAILED` | Cause message contains "timeout" or "network" | `"Check network connectivity for remote image URLs."` |
| `BROWSER_LAUNCH_FAILED` | Always | `"Ensure Chromium is installed. Run 'npx puppeteer browsers install chrome' to install."` |
| `BROWSER_LAUNCH_FAILED` | Cause message contains "ENOENT" or "chrome" | `"In Docker, ensure Chromium dependencies are installed (e.g., apt-get install chromium)."` |
| `PAGE_INIT_FAILED` | Always | `"Ensure headless Chromium supports WebGL. Use --gpu flag for hardware acceleration, or verify SwiftShader is available."` |
| `RENDER_FAILED` | Always | `"This may be a Three.js scene error. Re-run with --debug to see browser console output."` |
| `CAPTURE_FAILED` | Always | `"Frame capture failed. Re-run with --debug. If persistent, try --capture-strategy viewport-png."` |
| `ENCODE_FAILED` | Always | `"Verify FFmpeg is installed and accessible. Run 'ffmpeg -version' to check."` |
| `ENCODE_FAILED` | Cause is `FFmpegEncoderError` with non-null `exitCode` | `"FFmpeg exited with code {exitCode}. Check the FFmpeg log in the error detail."` |
| `ENCODE_FAILED` | Cause message contains "No such file or directory" | `"Ensure the output directory exists."` |
| `AUDIO_MUX_FAILED` | Always | `"Verify the audio file exists, is a valid WAV or MP3, and is not corrupted."` |
| `AUDIO_MUX_FAILED` | Cause message contains "ffprobe" | `"Ensure ffprobe is installed alongside FFmpeg."` |
| `CANCELLED` | Always | `"Render was cancelled. Re-run to try again."` |
| `GEOMETRY_NOT_FOUND` | Always | `"The geometry registry is inconsistent with the manifest registry. Ensure all geometry modules are imported."` |
| `CAMERA_NOT_FOUND` | Always | `"The camera registry is inconsistent with the manifest registry. Ensure all camera preset modules are imported."` |

**Fragility note:** Suggestion rules that match on `cause.message` substrings are best-effort heuristics. If an upstream module changes its error message format, the worst-case outcome is a missing context-specific suggestion — the base suggestion for the error code still applies. There is no correctness risk, only a UX degradation. Maintainers should update substring patterns when upstream error messages change.

## Design Decisions

### D-01: No New Error Classes

**Decision:** OBJ-048 does NOT introduce new error classes. Each module (OBJ-011, OBJ-013, OBJ-014, OBJ-035) defines its own error class. OBJ-048 provides classification, reporting, and suggestion utilities that operate on those existing types.

**Rationale:** Adding a `DepthkitError` base class would require refactoring all existing error classes. The existing error types are well-structured (each has a code, message, and domain-specific fields). OBJ-048's role is to unify their presentation, not their representation.

### D-02: ErrorReport as the Canonical Programmatic Output

**Decision:** `ErrorReport` is the canonical structured error format for programmatic consumers (n8n HTTP endpoint, library API callers). It is JSON-serializable and contains all information needed for both human display and machine routing.

**Rationale:** The n8n endpoint (Appendix A step 5) needs a stable JSON error format to decide whether to retry, report to the user, or escalate. `ErrorReport` provides the `category` field for routing and the `validationErrors` array for detailed diagnostics.

**Key trade-off:** `ErrorReport` deliberately flattens the cause chain into `detail` (a string) rather than nesting error objects. This keeps the JSON output simple and avoids serialization issues with Error instances.

### D-03: Suggestion Generation is Rule-Based, Not LLM-Based

**Decision:** Suggestions are generated by deterministic pattern matching on error codes and cause messages. There is no LLM in the error handling path.

**Rationale:** AP-10 ("Do Not Use the Director Agent in Production") extends to all AI in the runtime path. Suggestions must be instant, deterministic, and useful without network calls.

### D-04: No Plain-Text Formatting — OBJ-046 Owns CLI Display

**Decision:** OBJ-048 does NOT export plain-text formatting functions (`formatManifestErrors`, `formatOrchestratorError`). OBJ-046 (status: verified, review: approved) already exports `formatValidationErrors()` and `formatOrchestratorError()` from `src/cli/format.ts`. OBJ-048 provides the structured data layer (`ErrorReport`, `classifyError`, `generateSuggestions`, `extractFFmpegLogTail`) that OBJ-046 and other consumers build on.

**Rationale:** OBJ-046 was specified and verified before OBJ-048. OBJ-046 does not depend on OBJ-048 in the dependency graph, and retroactively introducing a dependency would violate the progress map's verified status. OBJ-046's formatting functions are self-contained. OBJ-048's unique value is the structured `ErrorReport` for programmatic consumers, the classification taxonomy, the suggestion engine, and the degradation rules — none of which overlap with OBJ-046.

**Consequence for non-CLI consumers:** The n8n HTTP endpoint and library API callers use `createErrorReport()` → `formatErrorReportJson()` to produce JSON error responses. They do not need plain-text formatting. If a future non-CLI consumer needs plain-text error rendering, it can consume the `ErrorReport` fields directly and format them as needed.

### D-05: Conservative Degradation Policy

**Decision:** The degradation strategy is heavily biased toward `fail`. Only manifest-level warnings and the per-plane opacity V1 limitation produce `warn` outcomes. All runtime failures are fatal.

**Rationale:** C-10 ("fail fast, fail clearly") and AP-04 ("do not conflate rendering with asset generation") mean the engine should never attempt to "fix" broken inputs. A production pipeline that silently degrades produces videos with missing planes or broken scenes — worse than failing and telling the user what's wrong.

### D-06: FFmpeg Log Excerpt Length

**Decision:** `extractFFmpegLogTail()` defaults to the last 20 lines.

**Rationale:** FFmpeg's error messages appear at the end of stderr. The encoding progress lines (`frame= ... fps= ...`) are noise when diagnosing a failure. 20 lines captures the error context while excluding the progress spam.

### D-07: Consolidated Error Taxonomy as Documentation

**Decision:** OBJ-048 documents the complete taxonomy of all error codes defined by other modules as a reference. It does NOT define new error codes. The taxonomy is reproduced in the spec (see section below) so that downstream consumers have a single reference document.

**Rationale:** A single reference table prevents downstream consumers from having to read 5+ spec documents to understand the error space.

### D-08: DEGRADATION_RULES as Exported Runtime Constant

**Decision:** The degradation rules are exported as a `Record<string, DegradationRule>` constant, not just documentation. The `MANIFEST_CODE_TO_DEGRADATION` mapping connects ManifestError codes to degradation rule keys. Both are programmatically testable.

**Rationale:** Exporting as runtime constants allows unit tests to verify that every `ManifestError` code with `severity: "error"` maps to a rule with `action: "fail"`, and every code with `severity: "warning"` maps to `action: "warn"`. This prevents drift between OBJ-016's error severities and OBJ-048's degradation policy.

### D-09: Cause Chain Inspection via instanceof with Duck-Typing Fallback

**Decision:** `createErrorReport()` inspects `OrchestratorError.cause` using `instanceof` checks against the imported error classes (`FFmpegEncoderError`, `AudioMuxerError`, `PageProtocolError`). The module imports these classes (not just types) to enable `instanceof`.

**Fallback:** If `instanceof` fails (e.g., the error was serialized/reconstructed across a process boundary, or two copies of a module exist), the function falls back to duck-typing:
- Property `ffmpegLog` is a string AND property `exitCode` exists → treat as FFmpeg-family error. Extract log via `extractFFmpegLogTail()`.
- Property `code` is a string matching a known `PageErrorCode` value → treat as page protocol error.
- Otherwise → treat as generic `Error`.

**Rationale:** `instanceof` is the correct approach for a single-process Node.js application (depthkit's normal operating mode). The duck-typing fallback is defensive against edge cases like duplicate module installations or future serialization scenarios.

### D-10: Cause Chain Traversal Depth Limit

**Decision:** When building the `detail` string in `createErrorReport()`, the function traverses the `.cause` chain up to **5 levels deep**. Each level's message is appended to `detail`, separated by ` → `. This prevents infinite output from hypothetical circular cause chains and keeps the `detail` field manageable.

**Example detail string:** `"FFmpeg exited with code 1 → pipe broken → EPIPE: write failed"`

**Rationale:** In practice, depthkit error chains are 1-2 levels deep (OrchestratorError → FFmpegEncoderError, or OrchestratorError → PageProtocolError). The 5-level limit is defensive. A limit is better than no limit because `Error.cause` is a general-purpose field with no depth guarantee.

## Consolidated Error Taxonomy

This section documents every error code across the engine for reference. OBJ-048 does not define these codes — they are defined by their originating modules.

**Manifest Validation Codes (OBJ-004 + OBJ-016):**

| Code | Severity | Description |
|---|---|---|
| `SCHEMA_VALIDATION` | error | Zod structural validation failure |
| `UNKNOWN_GEOMETRY` | error | Scene geometry not registered |
| `UNKNOWN_CAMERA` | error | Scene camera not registered |
| `INCOMPATIBLE_CAMERA` | error | Camera not compatible with geometry |
| `MISSING_REQUIRED_SLOT` | error | Required plane slot missing |
| `UNKNOWN_SLOT` | error | Plane key not in geometry's slots |
| `DUPLICATE_SCENE_ID` | error | Two+ scenes share same id |
| `SCENE_OVERLAP` | error | Invalid scene time overlap |
| `CROSSFADE_NO_ADJACENT` | error | Crossfade without adjacent scene |
| `SCENE_GAP` | warning | Time gap between consecutive scenes |
| `SCENE_ORDER_MISMATCH` | warning | Array order ≠ start_time order |
| `AUDIO_DURATION_MISMATCH` | warning | Audio vs scene duration differ |
| `FOV_WITHOUT_SUPPORT` | warning | FOV params on non-FOV camera |
| `FILE_NOT_FOUND` | error | ENOENT on file read |
| `FILE_READ_ERROR` | error | Non-ENOENT file read failure |
| `INVALID_JSON` | error | File contains unparseable JSON |

**Orchestrator Codes (OBJ-035):**

| Code | Category | Description |
|---|---|---|
| `MANIFEST_INVALID` | validation | Manifest validation failed |
| `BROWSER_LAUNCH_FAILED` | browser | Puppeteer/Chromium failed to start |
| `PAGE_INIT_FAILED` | browser | Three.js page initialization failed |
| `SCENE_SETUP_FAILED` | asset | Scene setup failed (texture load or missing images) |
| `RENDER_FAILED` | render | Frame rendering failed on the page |
| `CAPTURE_FAILED` | render | Frame capture failed |
| `ENCODE_FAILED` | encode | FFmpeg encoding failed |
| `AUDIO_MUX_FAILED` | audio | Audio muxing failed |
| `CANCELLED` | cancelled | Cancelled via onProgress callback |
| `GEOMETRY_NOT_FOUND` | validation | Geometry missing from geometryRegistry |
| `CAMERA_NOT_FOUND` | validation | Camera preset missing from cameraRegistry |

**Page Protocol Codes (OBJ-011):**

| Code | Description |
|---|---|
| `NOT_INITIALIZED` | Page not initialized |
| `ALREADY_INITIALIZED` | Page already initialized |
| `SCENE_EXISTS` | Scene ID already set up |
| `SCENE_NOT_FOUND` | Scene ID not found |
| `INVALID_COMMAND` | Invalid command (empty passes, empty sceneId) |
| `TEXTURE_LOAD_FAILED` | Texture failed to load |
| `RENDER_ERROR` | Three.js render error |
| `WEBGL_ERROR` | WebGL context error |

**FFmpeg Encoder Errors (OBJ-013):** `FFmpegEncoderError` with `exitCode` and `ffmpegLog`.

**Audio Muxer Errors (OBJ-014):** `AudioMuxerError` with `exitCode` and `ffmpegLog`.

## Acceptance Criteria

### Error Classification (AC-01 through AC-12)

- [ ] **AC-01:** `classifyError('MANIFEST_INVALID')` returns `'validation'`.
- [ ] **AC-02:** `classifyError('SCENE_SETUP_FAILED')` returns `'asset'`.
- [ ] **AC-03:** `classifyError('BROWSER_LAUNCH_FAILED')` returns `'browser'`.
- [ ] **AC-04:** `classifyError('PAGE_INIT_FAILED')` returns `'browser'`.
- [ ] **AC-05:** `classifyError('RENDER_FAILED')` returns `'render'`.
- [ ] **AC-06:** `classifyError('CAPTURE_FAILED')` returns `'render'`.
- [ ] **AC-07:** `classifyError('ENCODE_FAILED')` returns `'encode'`.
- [ ] **AC-08:** `classifyError('AUDIO_MUX_FAILED')` returns `'audio'`.
- [ ] **AC-09:** `classifyError('CANCELLED')` returns `'cancelled'`.
- [ ] **AC-10:** `classifyError('GEOMETRY_NOT_FOUND')` returns `'validation'`.
- [ ] **AC-11:** `classifyError('CAMERA_NOT_FOUND')` returns `'validation'`.
- [ ] **AC-12:** Every `OrchestratorErrorCode` value is covered by `classifyError` — no unhandled codes.

### Error Report Creation (AC-13 through AC-19)

- [ ] **AC-13:** `createErrorReport()` from an `OrchestratorError` with code `MANIFEST_INVALID` produces an `ErrorReport` with `category: 'validation'`, `code: 'MANIFEST_INVALID'`, and `validationErrors` populated from `error.validationErrors`.
- [ ] **AC-14:** `createErrorReport()` from an `OrchestratorError` with code `ENCODE_FAILED` whose cause is an `FFmpegEncoderError` includes the FFmpeg log tail (up to 20 lines) in `detail`.
- [ ] **AC-15:** `createErrorReport()` from an `OrchestratorError` with `frame >= 0` includes the frame number in `frame`.
- [ ] **AC-16:** `createValidationErrorReport()` produces `category: 'validation'`, `code: 'MANIFEST_INVALID'`, and the full `ManifestError[]` in `validationErrors`.
- [ ] **AC-17:** `createUnexpectedErrorReport()` from a plain `Error` produces `category: 'internal'`, `code: 'INTERNAL_ERROR'`, and the error message in `message`.
- [ ] **AC-18:** `createUnexpectedErrorReport()` from a non-Error value (e.g., string, null) produces `category: 'internal'` and a descriptive message.
- [ ] **AC-19:** All `ErrorReport` objects produced by any `create*` function are JSON-serializable (no circular references, no functions, no class instances in the output).

### Suggestion Generation (AC-20 through AC-26)

- [ ] **AC-20:** `generateSuggestions()` for `MANIFEST_INVALID` always includes the `"Run 'depthkit validate'"` suggestion.
- [ ] **AC-21:** `generateSuggestions()` for `ENCODE_FAILED` always includes the FFmpeg version check suggestion.
- [ ] **AC-22:** `generateSuggestions()` for `BROWSER_LAUNCH_FAILED` always includes the Chromium installation suggestion.
- [ ] **AC-23:** `generateSuggestions()` for `RENDER_FAILED` always includes the `--debug` suggestion.
- [ ] **AC-24:** `generateSuggestions()` for `CANCELLED` includes the re-run suggestion.
- [ ] **AC-25:** `generateSuggestions()` for `ENCODE_FAILED` with `FFmpegEncoderError` cause with `exitCode: 1` includes exit code in suggestion text.
- [ ] **AC-26:** `generateSuggestions()` for `MANIFEST_INVALID` with nested `INVALID_JSON` validation error includes JSON syntax suggestion.

### FFmpeg Log Utility (AC-27 through AC-30)

- [ ] **AC-27:** `extractFFmpegLogTail("line1\nline2\n...line25", 20)` returns the last 20 lines.
- [ ] **AC-28:** `extractFFmpegLogTail("short\nlog", 20)` returns both lines (full log when shorter than maxLines).
- [ ] **AC-29:** `extractFFmpegLogTail("", 20)` returns empty string.
- [ ] **AC-30:** `extractFFmpegLogTail(log)` with no maxLines argument defaults to 20 lines.

### Degradation Rules (AC-31 through AC-34)

- [ ] **AC-31:** Every ManifestError code with `severity: "error"` maps via `MANIFEST_CODE_TO_DEGRADATION` to a key in `DEGRADATION_RULES` with `action: "fail"`.
- [ ] **AC-32:** Every ManifestError code with `severity: "warning"` maps via `MANIFEST_CODE_TO_DEGRADATION` to a key in `DEGRADATION_RULES` with `action: "warn"`.
- [ ] **AC-33:** `DEGRADATION_RULES['per_plane_opacity_unsupported'].action` is `'warn'` (consistent with OBJ-035 D18).
- [ ] **AC-34:** `DEGRADATION_RULES['texture_load_failure'].action` is `'fail'` (consistent with OBJ-035 D5).

### JSON Serialization (AC-35 through AC-36)

- [ ] **AC-35:** `formatErrorReportJson()` produces valid JSON parseable by `JSON.parse()`.
- [ ] **AC-36:** `formatErrorReportJson()` uses 2-space indentation.

### Cause Chain Handling (AC-37 through AC-39)

- [ ] **AC-37:** `createErrorReport()` for `ENCODE_FAILED` where cause is an `FFmpegEncoderError` (verified by `instanceof`) extracts `ffmpegLog` and `exitCode`.
- [ ] **AC-38:** `createErrorReport()` where cause is a plain `Error` with a property `ffmpegLog` (duck-typing fallback) extracts the log.
- [ ] **AC-39:** `createErrorReport()` for an error with a 3-level cause chain produces a `detail` string containing messages from all 3 levels separated by ` → `.

## Edge Cases and Error Handling

### EC-01: OrchestratorError with No Cause
`createErrorReport()` where `error.cause` is `undefined`. `detail` is `null`. No FFmpeg log excerpt. Suggestions still generated based on code alone.

### EC-02: OrchestratorError with Deeply Nested Cause Chain
Cause chain is 7 levels deep. `detail` includes only the first 5 levels (per D-10), joined by ` → `. Remaining levels are silently truncated.

### EC-03: MANIFEST_INVALID with Zero validationErrors
Theoretically impossible (OBJ-035 only throws MANIFEST_INVALID when `loadManifest` returns `success: false` with errors), but defensively handled: `ErrorReport.validationErrors` is `[]`, `detail` is `null`, suggestions still include the validate command.

### EC-04: FFmpegEncoderError with Empty ffmpegLog
`extractFFmpegLogTail("")` returns `""`. `detail` in the ErrorReport says `"FFmpeg failed but produced no log output."`.

### EC-05: createUnexpectedErrorReport with null
`createUnexpectedErrorReport(null)` produces `message: "An unexpected error occurred (null)"`, `category: 'internal'`, `code: 'INTERNAL_ERROR'`.

### EC-06: createUnexpectedErrorReport with a string
`createUnexpectedErrorReport("something broke")` produces `message: "An unexpected error occurred: something broke"`, `category: 'internal'`.

### EC-07: createUnexpectedErrorReport with an OrchestratorError
If accidentally called with an `OrchestratorError`, produces `category: 'internal'`. This is the wrong function — callers should use `createErrorReport()`. However, it does not throw; it returns a valid `ErrorReport` with the error message.

### EC-08: Very Long FFmpeg Log (10,000+ lines)
`extractFFmpegLogTail()` with default `maxLines=20` efficiently returns only the last 20 lines. Implementation should split on `\n` and slice from the end, not iterate from the beginning.

### EC-09: Cause Chain with Circular Reference
Hypothetical: `error.cause.cause === error`. The 5-level depth limit (D-10) prevents infinite traversal. The `detail` string will contain repeated messages but terminates after 5 levels.

### EC-10: Concurrent ErrorReport Creation
All functions are pure and stateless. No shared mutable state. Thread-safe by construction.

### EC-11: ENCODE_FAILED Where Cause is Not FFmpegEncoderError
The cause may be any Error (e.g., from output directory not existing). `instanceof FFmpegEncoderError` fails, duck-typing finds no `ffmpegLog` property. `detail` shows the cause message chain per D-10. Suggestions still include the FFmpeg check (base suggestion for the code).

### EC-12: AUDIO_MUX_FAILED Where Cause is AudioMuxerError with ffmpegLog
`instanceof AudioMuxerError` succeeds. `detail` includes `extractFFmpegLogTail(cause.ffmpegLog)`. Same treatment as ENCODE_FAILED with FFmpegEncoderError.

## Test Strategy

### Unit Tests: `test/unit/engine/errors.test.ts`

**Classification tests (AC-01 through AC-12):**
1. Test each `OrchestratorErrorCode` value against `classifyError()`. Assert correct `ErrorCategory`.
2. Exhaustiveness: enumerate all known `OrchestratorErrorCode` values and verify `classifyError` returns a valid `ErrorCategory` for each.

**ErrorReport creation tests (AC-13 through AC-19):**
3. Create `OrchestratorError` with `MANIFEST_INVALID` and mock `validationErrors`. Call `createErrorReport()`. Assert `category`, `code`, `validationErrors`, `frame: -1`.
4. Create `OrchestratorError` with `ENCODE_FAILED`, cause is `FFmpegEncoderError` with a 30-line log. Assert `detail` contains 20-line excerpt.
5. Create `OrchestratorError` with `RENDER_FAILED`, frame=42. Assert `frame: 42`.
6. Create `OrchestratorError` with `SCENE_SETUP_FAILED`, cause message lists missing files. Assert `detail` contains the cause message.
7. `createValidationErrorReport([...errors])` — assert `category: 'validation'`, `code: 'MANIFEST_INVALID'`, errors in `validationErrors`.
8. `createUnexpectedErrorReport(new Error("boom"))` — assert `category: 'internal'`, `code: 'INTERNAL_ERROR'`.
9. `createUnexpectedErrorReport(null)` — assert `category: 'internal'`, message mentions null.
10. `createUnexpectedErrorReport("string error")` — assert message includes the string.
11. JSON-serialize every ErrorReport from tests 3-10 via `formatErrorReportJson()` and `JSON.parse()` the result — no throws, valid JSON.

**Cause chain inspection tests (AC-37 through AC-39):**
12. `ENCODE_FAILED` with `FFmpegEncoderError` cause — verify `instanceof` path extracts `ffmpegLog`.
13. `ENCODE_FAILED` with a plain `Error` that has a `ffmpegLog` string property — verify duck-typing fallback extracts the log.
14. Error with 3-level cause chain — verify `detail` contains messages from all 3 levels joined by ` → `.
15. Error with 7-level cause chain — verify `detail` contains only 5 levels.
16. Error with no cause — verify `detail` is null.

**Suggestion generation tests (AC-20 through AC-26):**
17. Each OrchestratorErrorCode: verify at least one suggestion returned.
18. `MANIFEST_INVALID` — verify validate command suggestion present.
19. `ENCODE_FAILED` — verify FFmpeg check suggestion present.
20. `BROWSER_LAUNCH_FAILED` — verify Chromium install suggestion present.
21. `RENDER_FAILED` — verify `--debug` suggestion present.
22. `CANCELLED` — verify re-run suggestion.
23. `ENCODE_FAILED` with FFmpegEncoderError cause with `exitCode: 1` — verify exit code mentioned in suggestion.
24. `MANIFEST_INVALID` with nested `INVALID_JSON` error — verify JSON syntax suggestion.
25. `BROWSER_LAUNCH_FAILED` with cause message containing "ENOENT" — verify Docker suggestion.
26. `SCENE_SETUP_FAILED` with cause message containing "timeout" — verify network suggestion.

**FFmpeg log utility tests (AC-27 through AC-30):**
27. 25-line log, maxLines=20 — returns last 20.
28. 5-line log, maxLines=20 — returns all 5.
29. Empty string — returns empty string.
30. Default maxLines — verify 20.
31. Single-line log — returns the single line.

**Degradation rules tests (AC-31 through AC-34):**
32. Iterate all ManifestError codes with `severity: "error"` (from the taxonomy), look up in `MANIFEST_CODE_TO_DEGRADATION`, then look up in `DEGRADATION_RULES`. Assert `action: "fail"` for each.
33. Iterate all ManifestError codes with `severity: "warning"`, same lookup chain. Assert `action: "warn"` for each.
34. Verify `DEGRADATION_RULES['per_plane_opacity_unsupported'].action === 'warn'`.
35. Verify `DEGRADATION_RULES['texture_load_failure'].action === 'fail'`.
36. Verify every key in `MANIFEST_CODE_TO_DEGRADATION` maps to a key that exists in `DEGRADATION_RULES`.

**JSON serialization tests (AC-35 through AC-36):**
37. `formatErrorReportJson(report)` output is valid JSON.
38. Output uses 2-space indentation (check for `\n  ` pattern).

### Relevant Testable Claims

- **TC-07:** The `ErrorReport` and suggestion engine verify that validation errors are presented with actionable messages (the "actionable error messages with context" part of OBJ-048's description).
- **SC-06:** The `DEGRADATION_RULES` constant and tests 32-36 ensure consistency between error severities and the fail/warn boundary, supporting "no manifest that passes validation produces a rendering error."

## Integration Points

### Depends On

| Dependency | What OBJ-048 Uses |
|---|---|
| **OBJ-016** (Manifest Loader) | `ManifestError` type. Error code values for degradation mapping and suggestion matching. |
| **OBJ-035** (Orchestrator) | `OrchestratorError` class, `OrchestratorErrorCode` type. |
| **OBJ-004** (Manifest Schema) | `ManifestError` type definition. |
| **OBJ-013** (FFmpeg Encoder) | `FFmpegEncoderError` class (imported for `instanceof` checks and `ffmpegLog`/`exitCode` access). |
| **OBJ-014** (Audio Muxer) | `AudioMuxerError` class (imported for `instanceof` checks and `ffmpegLog`/`exitCode` access). |
| **OBJ-011** (Page Protocol) | `PageProtocolError` class (imported for `instanceof` checks). `PageErrorCode` type for taxonomy documentation. |

### Consumed By

| Downstream | How It Uses OBJ-048 |
|---|---|
| **OBJ-046** (CLI) | OBJ-046 does NOT depend on OBJ-048 (OBJ-046 is verified). OBJ-046's `src/cli/format.ts` has its own formatting functions. However, future revisions of the CLI could optionally adopt `createErrorReport()` → `formatErrorReportJson()` for structured output (e.g., a `--json` flag). This is not required. |
| **n8n HTTP endpoint** (future) | Calls `createErrorReport()` or `createValidationErrorReport()` or `createUnexpectedErrorReport()` on caught errors, then returns `formatErrorReportJson()` as the HTTP response body. The `category` field enables routing (e.g., retry on `'encode'`, fail immediately on `'validation'`). |
| **OBJ-077** (End-to-end integration) | May use `ErrorReport` to verify error behavior in integration tests. |
| **OBJ-078** (Production readiness) | References the degradation rules and error taxonomy. |

### File Placement

```
depthkit/
  src/
    engine/
      errors.ts              # NEW — ErrorReport, ErrorCategory,
                             #       DegradationAction, DegradationRule,
                             #       DEGRADATION_RULES, MANIFEST_CODE_TO_DEGRADATION,
                             #       classifyError(), createErrorReport(),
                             #       createValidationErrorReport(),
                             #       createUnexpectedErrorReport(),
                             #       generateSuggestions(),
                             #       extractFFmpegLogTail(),
                             #       formatErrorReportJson()
  test/
    unit/
      engine/
        errors.test.ts       # NEW — All unit tests
```

## Open Questions

### OQ-A: Should ErrorReport include a `stack` field?
Stack traces are useful for debugging but leak implementation details. Current decision: omit from ErrorReport (JSON API output). If the n8n endpoint needs stack traces for server-side logging, it can capture them separately before creating the ErrorReport. The `detail` field (which includes the cause chain) provides diagnostic context without exposing implementation internals.

### OQ-B: Should there be a `DepthkitError` base class?
All existing error classes extend `Error` independently. A shared base class would enable `instanceof DepthkitError` checks. Current decision: no — `createErrorReport()` already handles all known types via `instanceof` with duck-typing fallback (D-09). A base class adds refactoring cost with no clear benefit for the current consumer set.

### OQ-C: Should the n8n HTTP endpoint also return suggestions?
The `ErrorReport.suggestions` field is populated for all error types. Whether the n8n endpoint surfaces these to the end user or uses them only for logging is an integration decision outside OBJ-048's scope. The suggestions are available in the ErrorReport regardless.

---

I believe this revision addresses all six issues raised by the challenger:

1. **Issue 1 (Major):** Removed all plain-text formatting functions. OBJ-048 no longer overlaps with OBJ-046. D-04 explicitly documents the boundary.
2. **Issue 2 (Major):** `DEGRADATION_RULES` and `MANIFEST_CODE_TO_DEGRADATION` are exported runtime constants with programmatic tests (AC-31 through AC-34, tests 32-36).
3. **Issue 3 (Minor):** D-09 specifies `instanceof` with duck-typing fallback, including the specific properties checked.
4. **Issue 4 (Minor):** D-10 promotes the 5-level depth limit to a design decision with rationale and example.
5. **Issue 5 (Minor):** Moot — plain-text formatters with `color` option were removed entirely per Issue 1.
6. **Issue 6 (Minor):** Fragility note added to the suggestion rules section, explicitly documenting that substring matching is best-effort with a bounded failure mode.

I'd like the challenger to verify and approve this revised spec.

---

## Round 4 — spec_challenger

I've carefully verified the revised spec against all six of my original issues:

1. **Issue 1 (Major - OBJ-046 overlap):** ✅ Fixed. Plain-text formatters removed entirely. D-04 explicitly documents that OBJ-046 owns CLI formatting and does not depend on OBJ-048. The "Consumed By" table correctly states OBJ-046 is independent. No naming collision remains.

2. **Issue 2 (Major - Untestable degradation rules):** ✅ Fixed. `DEGRADATION_RULES` and `MANIFEST_CODE_TO_DEGRADATION` are exported runtime constants. AC-31/AC-32 programmatically verify consistency with OBJ-016 severities. Tests 32-36 cover this thoroughly.

3. **Issue 3 (Minor - Cause chain type detection):** ✅ Fixed. D-09 specifies `instanceof` primary path with duck-typing fallback, including the specific properties checked (`ffmpegLog`, `exitCode`, `code`).

4. **Issue 4 (Minor - Depth limit):** ✅ Fixed. D-10 promotes the 5-level limit to a first-class design decision with rationale and example output format.

5. **Issue 5 (Minor - Color contradiction):** ✅ Moot — formatters removed.

6. **Issue 6 (Minor - Fragility note):** ✅ Fixed. Fragility note added to the suggestion rules section with explicit bounded-failure-mode description.

No new issues were introduced by the revision. The spec is clean, well-scoped, and implementable. An implementer has everything they need.

CONCLUSION:

The agreed specification for OBJ-048 defines: (1) `ErrorReport` as the canonical structured error output for programmatic consumers, with `classifyError()`, `createErrorReport()`, `createValidationErrorReport()`, and `createUnexpectedErrorReport()` factory functions; (2) `generateSuggestions()` with exhaustive rule-based suggestion generation; (3) `DEGRADATION_RULES` and `MANIFEST_CODE_TO_DEGRADATION` as exported runtime constants for testable fail/warn policy; (4) `extractFFmpegLogTail()` utility; (5) `formatErrorReportJson()` for JSON serialization; (6) the consolidated error taxonomy across all engine modules; and (7) clear boundary with OBJ-046 (OBJ-048 provides structured data, OBJ-046 owns CLI formatting).

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me read the existing meta.json before updating it:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-048/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-048",
     3→  "description": "Error handling and reporting strategy -- validation errors (from manifest loader), render errors (from Puppeteer/Three.js/FFmpeg), actionable error messages with context (file paths, field names, expected vs actual), error codes for programmatic consumers, graceful degradation strategies (e.g., skip optional planes, warn on non-fatal issues).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-016", "OBJ-035"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 interface."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-048/output.md",
  "content": "# Specification: OBJ-048 \u2014 Error Handling and Reporting Strategy\n\n## Summary\n\nOBJ-048 defines the unified error handling and reporting strategy across the entire depthkit engine. It specifies: (1) a consolidated error taxonomy cataloguing every error type from manifest validation (OBJ-016), page protocol (OBJ-011), FFmpeg encoding (OBJ-013), audio muxing (OBJ-014), and orchestration (OBJ-035); (2) an `ErrorReport` structure and creation utilities for programmatic consumers (n8n HTTP endpoint, library API); (3) error classification and suggestion generation; (4) an exported `DEGRADATION_RULES` constant for testable graceful degradation policy; (5) an `extractFFmpegLogTail()` utility; and (6) documentation of the complete error code registry. Plain-text formatting for CLI display is OBJ-046's responsibility \u2014 OBJ-048 provides the structured data layer that OBJ-046 and other consumers build on.\n\n## Interface Contract\n\n### Module: `src/engine/errors.ts`\n\nThis module provides error classification, structured reporting, and suggestion generation. It does NOT define new error classes \u2014 those are defined by their originating modules (OBJ-004, OBJ-011, OBJ-013, OBJ-014, OBJ-035). It does NOT provide plain-text formatting for CLI display \u2014 that is OBJ-046's `src/cli/format.ts`. This module provides the structured data layer that all consumers (CLI, HTTP API, tests) build on.\n\n```typescript\n// src/engine/errors.ts\n\nimport type { ManifestError } from '../manifest/schema.js';\nimport type { OrchestratorError, OrchestratorErrorCode } from './orchestrator.js';\nimport { FFmpegEncoderError } from './ffmpeg-encoder.js';\nimport { AudioMuxerError } from './audio-muxer.js';\nimport { PageProtocolError } from './protocol-types.js';\nimport type { PageErrorCode } from './protocol-types.js';\n\n// \u2500\u2500\u2500\u2500\u2500\
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-048/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-048/meta.json",
  "content": "{\n  \"id\": \"OBJ-048\",\n  \"description\": \"Error handling and reporting strategy -- validation errors (from manifest loader), render errors (from Puppeteer/Three.js/FFmpeg), actionable error messages with context (file paths, field names, expected vs actual), error codes for programmatic consumers, graceful degradation strategies (e.g., skip optional planes, warn on non-fatal issues).\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:15:00Z\",\n  \"depends_on\": [\"OBJ-016\", \"OBJ-035\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 4 interface. Spec complete: ErrorReport for programmatic consumers, classifyError/generateSuggestions/extractFFmpegLogTail utilities, DEGRADATION_RULES and MANIFEST_CODE_TO_DEGRADATION exported constants, consolidated error taxonomy. Plain-text CLI formatting is OBJ-046's responsibility (no overlap). Does not introduce new error classes.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-048/meta.json has been updated successfully.
Now commit to git:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git status -u",
  "description": "Check git status for changed files"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commits for message style"
}
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-048/meta.json

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
[Tool Result] 7788a22 spec(OBJ-047): Library API — importable programmatic interface for depthkit
c16726a spec(OBJ-070): SKILL.md structure and core content
0d39d2e spec(OBJ-028): lateral track camera path presets
326107f spec(OBJ-017): geometry-specific structural manifest validation - minimal ValidatableGeometry interface, function injection, deterministic error ordering. Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
2e80bae spec(OBJ-036): scene sequencer — stateless planFrame model, boundary resolution, independent fades

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-048/output.md nodes/OBJ-048/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-048): error handling and reporting strategy \u2014 ErrorReport for programmatic consumers, classifyError/generateSuggestions utilities, DEGRADATION_RULES exported constant, consolidated error taxonomy\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-048 spec files"
}
[Tool Result] [master eb84b19] spec(OBJ-048): error handling and reporting strategy — ErrorReport for programmatic consumers, classifyError/generateSuggestions utilities, DEGRADATION_RULES exported constant, consolidated error taxonomy
 2 files changed, 658 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-048/output.md
The specification for OBJ-048 has been written to `nodes/OBJ-048/output.md`, meta.json updated, and committed at `eb84b19`.

**Summary of what was agreed:**

- **`src/engine/errors.ts`** provides the structured data layer for error handling — no plain-text formatting (that's OBJ-046's domain)
- **`ErrorReport`** is the canonical JSON-serializable error output for programmatic consumers (n8n, library API), with `category` for routing, `code` for switching, `validationErrors` for detail, `suggestions` for remediation
- **`classifyError()`** maps all 11 `OrchestratorErrorCode` values to 8 `ErrorCategory` buckets
- **`generateSuggestions()`** uses deterministic rule-based pattern matching (not LLM) with best-effort cause-message substring heuristics
- **`DEGRADATION_RULES`** and **`MANIFEST_CODE_TO_DEGRADATION`** are exported runtime constants enabling programmatic verification that error severities and fail/warn boundaries stay consistent
- **D-09** specifies `instanceof` with duck-typing fallback for cause chain inspection
- **D-10** caps cause chain traversal at 5 levels
- **39 acceptance criteria** covering classification, report creation, suggestions, FFmpeg log utility, degradation rules, JSON serialization, and cause chain handling
