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
 *   MANIFEST_INVALID        -> 'validation'
 *   SCENE_SETUP_FAILED      -> 'asset'
 *   BROWSER_LAUNCH_FAILED   -> 'browser'
 *   PAGE_INIT_FAILED        -> 'browser'
 *   RENDER_FAILED           -> 'render'
 *   CAPTURE_FAILED          -> 'render'
 *   ENCODE_FAILED           -> 'encode'
 *   AUDIO_MUX_FAILED        -> 'audio'
 *   CANCELLED               -> 'cancelled'
 *   GEOMETRY_NOT_FOUND      -> 'validation'
 *   CAMERA_NOT_FOUND        -> 'validation'
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

/**
 * Maps each ManifestError code to its degradation rule key.
 * Used by unit tests to verify consistency between OBJ-016's
 * error severities and OBJ-048's degradation rules.
 */
export const MANIFEST_CODE_TO_DEGRADATION: Record<string, string>;
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

**Consequence for non-CLI consumers:** The n8n HTTP endpoint and library API callers use `createErrorReport()` -> `formatErrorReportJson()` to produce JSON error responses. They do not need plain-text formatting. If a future non-CLI consumer needs plain-text error rendering, it can consume the `ErrorReport` fields directly and format them as needed.

### D-05: Conservative Degradation Policy

**Decision:** The degradation strategy is heavily biased toward `fail`. Only manifest-level warnings and the per-plane opacity V1 limitation produce `warn` outcomes. All runtime failures are fatal.

**Rationale:** C-10 ("fail fast, fail clearly") and AP-04 ("do not conflate rendering with asset generation") mean the engine should never attempt to "fix" broken inputs. A production pipeline that silently degrades produces videos with missing planes or broken scenes — worse than failing and telling the user what's wrong.

### D-06: FFmpeg Log Excerpt Length

**Decision:** `extractFFmpegLogTail()` defaults to the last 20 lines.

**Rationale:** FFmpeg's error messages appear at the end of stderr. The encoding progress lines (`frame= ... fps= ...`) are noise when diagnosing a failure. 20 lines captures the error context while excluding the progress spam.

### D-07: Consolidated Error Taxonomy as Documentation

**Decision:** OBJ-048 documents the complete taxonomy of all error codes defined by other modules as a reference. It does NOT define new error codes. The taxonomy is reproduced in the spec so that downstream consumers have a single reference document.

**Rationale:** A single reference table prevents downstream consumers from having to read 5+ spec documents to understand the error space.

### D-08: DEGRADATION_RULES as Exported Runtime Constant

**Decision:** The degradation rules are exported as a `Record<string, DegradationRule>` constant, not just documentation. The `MANIFEST_CODE_TO_DEGRADATION` mapping connects ManifestError codes to degradation rule keys. Both are programmatically testable.

**Rationale:** Exporting as runtime constants allows unit tests to verify that every `ManifestError` code with `severity: "error"` maps to a rule with `action: "fail"`, and every code with `severity: "warning"` maps to `action: "warn"`. This prevents drift between OBJ-016's error severities and OBJ-048's degradation policy.

### D-09: Cause Chain Inspection via instanceof with Duck-Typing Fallback

**Decision:** `createErrorReport()` inspects `OrchestratorError.cause` using `instanceof` checks against the imported error classes (`FFmpegEncoderError`, `AudioMuxerError`, `PageProtocolError`). The module imports these classes (not just types) to enable `instanceof`.

**Fallback:** If `instanceof` fails (e.g., the error was serialized/reconstructed across a process boundary, or two copies of a module exist), the function falls back to duck-typing:
- Property `ffmpegLog` is a string AND property `exitCode` exists -> treat as FFmpeg-family error. Extract log via `extractFFmpegLogTail()`.
- Property `code` is a string matching a known `PageErrorCode` value -> treat as page protocol error.
- Otherwise -> treat as generic `Error`.

**Rationale:** `instanceof` is the correct approach for a single-process Node.js application (depthkit's normal operating mode). The duck-typing fallback is defensive against edge cases like duplicate module installations or future serialization scenarios.

### D-10: Cause Chain Traversal Depth Limit

**Decision:** When building the `detail` string in `createErrorReport()`, the function traverses the `.cause` chain up to **5 levels deep**. Each level's message is appended to `detail`, separated by ` -> `. This prevents infinite output from hypothetical circular cause chains and keeps the `detail` field manageable.

**Example detail string:** `"FFmpeg exited with code 1 -> pipe broken -> EPIPE: write failed"`

**Rationale:** In practice, depthkit error chains are 1-2 levels deep (OrchestratorError -> FFmpegEncoderError, or OrchestratorError -> PageProtocolError). The 5-level limit is defensive. A limit is better than no limit because `Error.cause` is a general-purpose field with no depth guarantee.

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
| `SCENE_ORDER_MISMATCH` | warning | Array order != start_time order |
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
- [ ] **AC-39:** `createErrorReport()` for an error with a 3-level cause chain produces a `detail` string containing messages from all 3 levels separated by ` -> `.

## Edge Cases and Error Handling

### EC-01: OrchestratorError with No Cause
`createErrorReport()` where `error.cause` is `undefined`. `detail` is `null`. No FFmpeg log excerpt. Suggestions still generated based on code alone.

### EC-02: OrchestratorError with Deeply Nested Cause Chain
Cause chain is 7 levels deep. `detail` includes only the first 5 levels (per D-10), joined by ` -> `. Remaining levels are silently truncated.

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
14. Error with 3-level cause chain — verify `detail` contains messages from all 3 levels joined by ` -> `.
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
| **OBJ-046** (CLI) | OBJ-046 does NOT depend on OBJ-048 (OBJ-046 is verified). OBJ-046's `src/cli/format.ts` has its own formatting functions. However, future revisions of the CLI could optionally adopt `createErrorReport()` -> `formatErrorReportJson()` for structured output (e.g., a `--json` flag). This is not required. |
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
