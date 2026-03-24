# Deliberation Transcript: OBJ-052

---

## Round 1 — spec_author

Looking at OBJ-052's metadata, dependency (OBJ-015), and the relevant seed sections (4.8, OQ-02, TC-12, AP-04, C-09), let me first check the current codebase state to understand what exists.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me examine the existing codebase to understand the current state and relevant files.
[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*.js"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-052/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-052/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-015/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/transcript.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-052/meta.json"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-057/**/*"
}
[Tool Result]      1→{
     2→  "id": "OBJ-052",
     3→  "description": "Background removal integration -- rembg as Python subprocess from Node.js, chroma key alternative via Sharp, per-slot-type strategy (apply removal to subject and near_fg only; far_bg and mid_bg don't need it). Addresses OQ-02 (best strategy for images without alpha) and TC-12 (rembg viable as subprocess -- under 5 seconds per image, acceptable mask quality).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-015"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. Medium priority. Covers TC-12. Part of asset pipeline, not rendering engine (per AP-04)."
    12→}
    13→
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-057/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-057/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-057",
     3→  "description": "Asset orchestration pipeline -- coordinates TTS call (Chatterbox TTS for narration audio), image retrieval with semantic caching (OBJ-054), background removal routing (OBJ-052), and assembly of all manifest inputs (images, audio, manifest JSON) into the structure depthkit expects. This is the glue between manifest generation, asset generation, and rendering. Per Appendix A steps 2-4.",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-054", "OBJ-052", "OBJ-055", "OBJ-056"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. Medium priority. Split from original OBJ-055. The full pipeline orchestrator."
    12→}
    13→

[Tool: Grep]
  Input: {
  "pattern": "background.remov|rembg|chroma.key|sharp",
  "-i": true,
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit",
  "glob": "*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/package.json"
}
[Tool Result] No files found
Good — the engine code hasn't been built yet (specs only). Let me also check the OBJ-005 geometry types to understand `PlaneSlot.transparent`:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-005/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/transcript.md

[Tool: Grep]
  Input: {
  "pattern": "transparent|PlaneSlot|slot_type|SlotType",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "output_mode": "content",
  "-C": 3
}
[Tool Result] 2-
3-## Summary
4-
5:[Omitted long matching line]
6-
7-## Interface Contract
8-
--
37- *
38- * Extends PlaneTransform from OBJ-003, adding metadata fields specific
39- * to the geometry contract (required, description, rendering hints).
40: * Any function accepting PlaneTransform also accepts PlaneSlot.
41- *
42: * PlaneSlot values in a registered SceneGeometry are immutable templates
43- * (see D9). The readonly tuple types (Vec3, EulerRotation, Size2D) enforce
44- * this at compile time; deep freezing at registration enforces it at runtime.
45- * These values are the geometry's defaults. Downstream consumers (OBJ-036,
--
48- * slot definition. The override mechanism is defined by the manifest schema
49- * (OBJ-004), not by this contract.
50- */
51:export interface PlaneSlot extends PlaneTransform {
52-  /**
53-   * Whether the manifest MUST provide an image for this slot.
54-   * If true, manifest validation (OBJ-017) rejects manifests that
--
80-
81-  /**
82-   * Whether this plane'... [truncated]
Now I have a clear picture. Let me understand the key points:

1. OBJ-015 provides texture loading + alpha detection (browser-side) + `checkTextureSlotCompatibility()` (Node-side warning utility)
2. OBJ-005 defines `PlaneSlot.transparent` which tells us which slots expect alpha
3. OBJ-052 is the actual background removal — the asset pipeline step that FIXES images without alpha before they reach the engine
4. AP-04 says this must be separate from the rendering engine
5. TC-12 says rembg must be under 5 seconds per image

Now let me propose the full specification.

---

# Specification Proposal: OBJ-052 — Background Removal Integration

## Summary

OBJ-052 defines a Node.js module for removing backgrounds from images as part of the asset preparation pipeline (not the rendering engine, per AP-04). It provides two removal strategies: **rembg** (Python subprocess, high-quality AI-based matting) as the primary strategy, and **Sharp-based chroma key** (pure Node.js, no Python dependency) as the fallback. A per-slot-type policy determines which images need background removal — only slots where `PlaneSlot.transparent === true` (typically `subject`, `near_fg`) are processed; opaque slots (`sky`, `floor`, `back_wall`, etc.) are passed through unchanged. This module directly addresses OQ-02 (best strategy for images without alpha) and TC-12 (rembg viability as subprocess).

## Interface Contract

### Module: `src/pipeline/background-removal.ts`

This module lives outside `src/engine/` per AP-04. It is consumed by the asset orchestration pipeline (OBJ-057) and is never imported by the rendering engine.

```typescript
// src/pipeline/background-removal.ts

import type { TextureSlotWarning } from '../engine/texture-types.js';

/**
 * The removal strategy to use.
 * - 'rembg': AI-based matting via Python subprocess. Best quality.
 * - 'chroma_key': Sharp-based color range removal. No Python dependency.
 * - 'none': Pass through unchanged.
 * - 'auto': Try rembg first; if unavailable, fall back to chroma_key.
 */
export type RemovalStrategy = 'rembg' | 'chroma_key' | 'none' | 'auto';

/**
 * Configuration for the background removal module.
 * Passed once at initialization; individual calls can override per-image.
 */
export interface BackgroundRemovalConfig {
  /**
   * Default strategy when not specified per-call.
   * Default: 'auto'.
   */
  defaultStrategy?: RemovalStrategy;

  /**
   * Path to the Python executable. Used when strategy is 'rembg'.
   * Default: 'python3'. Falls back to 'python' if 'python3' is not found.
   */
  pythonPath?: string;

  /**
   * The rembg model to use.
   * Default: 'u2net' (general purpose, good balance of speed and quality).
   * Other options: 'u2netp' (lightweight/faster), 'isnet-general-use'.
   * Passed to rembg as: `rembg i -m <model> <input> <output>`
   */
  rembgModel?: string;

  /**
   * Timeout in milliseconds for the rembg subprocess per image.
   * Default: 30000 (30 seconds).
   * If exceeded, the subprocess is killed and the call rejects.
   */
  rembgTimeout?: number;

  /**
   * Default chroma key settings, used when strategy is 'chroma_key'.
   */
  chromaKey?: ChromaKeyConfig;

  /**
   * Directory for writing processed output images.
   * If not specified, output is written alongside the input with a
   * '_removed' suffix before the extension (e.g., 'subject.png' -> 'subject_removed.png').
   * If specified, output files are written to this directory using the
   * input filename with '_removed' suffix.
   */
  outputDir?: string;
}

/**
 * Configuration for Sharp-based chroma key removal.
 */
export interface ChromaKeyConfig {
  /**
   * The target background color to remove, as a hex string.
   * Default: '#FFFFFF' (white — the most common AI-generated background).
   */
  color?: string;

  /**
   * Color distance threshold (0–255) in Euclidean RGB space.
   * Pixels within this distance of the target color become transparent.
   * Default: 30.
   * Lower = stricter matching (fewer pixels removed).
   * Higher = more aggressive removal (may eat into subject edges).
   */
  threshold?: number;

  /**
   * Feather radius in pixels for the alpha mask edge.
   * Softens the boundary between transparent and opaque regions.
   * Default: 1.
   * 0 = hard edge (no feathering).
   * 1-3 = subtle softening (recommended).
   * >3 = visible blur at edges.
   */
  feather?: number;
}

/**
 * Per-image options for a single removal call.
 * Overrides the module-level config for this specific image.
 */
export interface RemovalOptions {
  /**
   * Override the strategy for this image.
   */
  strategy?: RemovalStrategy;

  /**
   * Override chroma key config for this image.
   * Only used when effective strategy is 'chroma_key'.
   */
  chromaKey?: ChromaKeyConfig;

  /**
   * Explicit output path. Overrides the outputDir/suffix convention.
   */
  outputPath?: string;

  /**
   * Override rembg timeout for this image.
   */
  timeout?: number;
}

/**
 * Result of a single background removal operation.
 */
export interface RemovalResult {
  /** Absolute path to the input image. */
  inputPath: string;

  /** Absolute path to the output image (with alpha channel). */
  outputPath: string;

  /**
   * The strategy that was actually used.
   * If 'auto' was requested and rembg was available, this is 'rembg'.
   * If 'auto' was requested and rembg was unavailable, this is 'chroma_key'.
   * If the image already had alpha, this is 'none' (passthrough).
   */
  strategyUsed: 'rembg' | 'chroma_key' | 'none';

  /**
   * Whether the input image already had an alpha channel.
   * Determined by inspecting the image metadata via Sharp.
   * When true, strategyUsed is 'none' and the image is copied
   * (or symlinked) unchanged to outputPath.
   */
  inputHadAlpha: boolean;

  /** Processing duration in milliseconds. */
  durationMs: number;
}

/**
 * An entry in a batch removal request.
 */
export interface BatchRemovalEntry {
  /** Input image path (absolute or relative to cwd). */
  inputPath: string;

  /**
   * The slot type this image is destined for.
   * Used by processImagesForManifest() to decide whether removal is needed.
   * When calling removeBackground() directly, this is informational only.
   */
  slotType?: string;

  /** Per-image overrides. */
  options?: RemovalOptions;
}

/**
 * Result of a batch removal operation.
 */
export interface BatchRemovalResult {
  /** Results ordered to match input entries. */
  results: RemovalResult[];

  /** Total processing duration in milliseconds (wall clock for the whole batch). */
  totalDurationMs: number;

  /** Count of images that were processed (strategy != 'none'). */
  processedCount: number;

  /** Count of images that were skipped (already had alpha or slot didn't need it). */
  skippedCount: number;

  /** Count of images that failed. Only present when continueOnError is true. */
  failedCount: number;

  /** Errors for failed images, keyed by input path. Only present when continueOnError is true. */
  errors: Record<string, string>;
}

/**
 * Slot type categories and their default removal policy.
 * This is the per-slot-type strategy from the objective description.
 */
export const SLOT_REMOVAL_POLICY: Record<string, boolean> = {
  // Slots that typically need transparency
  subject: true,
  near_fg: true,

  // Slots that do NOT need transparency (opaque fills)
  sky: false,
  back_wall: false,
  midground: false,
  floor: false,
  ceiling: false,
  left_wall: false,
  right_wall: false,
  end_wall: false,
  backdrop: false,
};

// ── Exported Functions ──────────────────────────────────────────

/**
 * Checks whether rembg is installed and callable.
 *
 * Spawns `<pythonPath> -m rembg --help` (or `rembg --help`) and
 * checks for a zero exit code. Caches the result for the lifetime
 * of the process (rembg availability doesn't change mid-run).
 *
 * @param pythonPath - Path to Python executable. Default: 'python3'.
 * @returns Promise<boolean> - true if rembg is available and callable.
 */
export function isRembgAvailable(pythonPath?: string): Promise<boolean>;

/**
 * Creates a configured background removal instance.
 * Returns an object with bound methods that use the provided config.
 *
 * @param config - Module-level configuration. All fields optional.
 * @returns A BackgroundRemover instance with all removal methods.
 */
export function createBackgroundRemover(
  config?: BackgroundRemovalConfig
): BackgroundRemover;

/**
 * The configured background remover instance.
 */
export interface BackgroundRemover {
  /**
   * Removes the background from a single image.
   *
   * Workflow:
   * 1. Resolve inputPath to absolute path. Verify file exists.
   * 2. Check if the input already has an alpha channel (via Sharp metadata).
   *    If yes: copy/symlink to outputPath, return with strategyUsed='none'.
   * 3. Determine effective strategy:
   *    - If options.strategy is set, use it.
   *    - Else use config.defaultStrategy (default: 'auto').
   *    - If 'auto': check isRembgAvailable(). If yes, use 'rembg'. Else 'chroma_key'.
   *    - If 'none': copy to output unchanged.
   * 4. Execute the strategy:
   *    - 'rembg': spawn subprocess, wait for completion.
   *    - 'chroma_key': process via Sharp pipeline.
   * 5. Verify output file exists and is a valid PNG with alpha channel.
   * 6. Return RemovalResult.
   *
   * @throws Error if inputPath does not exist:
   *         "Background removal failed: input file not found: '{path}'"
   * @throws Error if inputPath is not a supported image format:
   *         "Background removal failed: unsupported format '{ext}' for '{path}'. Supported: png, jpg, jpeg, webp"
   * @throws Error if rembg strategy is requested but rembg is unavailable:
   *         "Background removal failed: rembg is not available. Install with: pip install rembg[cpu]"
   * @throws Error if rembg subprocess times out:
   *         "Background removal failed: rembg timed out after {ms}ms for '{path}'"
   * @throws Error if rembg subprocess exits with non-zero code:
   *         "Background removal failed: rembg exited with code {code} for '{path}': {stderr}"
   * @throws Error if Sharp processing fails:
   *         "Background removal failed: chroma key processing error for '{path}': {message}"
   */
  removeBackground(
    inputPath: string,
    options?: RemovalOptions
  ): Promise<RemovalResult>;

  /**
   * Processes multiple images sequentially.
   *
   * Images are processed one at a time (not in parallel) because
   * rembg is CPU-intensive and parallelism would cause memory pressure
   * and slower overall throughput on typical VPS hardware (4 cores, 4GB RAM).
   *
   * @param entries - Array of images to process.
   * @param continueOnError - If true, failures are collected in
   *        BatchRemovalResult.errors and processing continues.
   *        If false (default), the first failure rejects the promise.
   * @returns Promise<BatchRemovalResult>
   * @throws Error (if continueOnError is false) on first failure.
   */
  batchRemoveBackgrounds(
    entries: BatchRemovalEntry[],
    continueOnError?: boolean
  ): Promise<BatchRemovalResult>;

  /**
   * High-level function for the asset pipeline (OBJ-057).
   *
   * Takes a manifest's scene array (or a flat list of slot-type + image-path
   * pairs) and applies background removal ONLY to images assigned to slots
   * where removal is needed. The decision is made by:
   *
   * 1. Check SLOT_REMOVAL_POLICY for the slot type. If the slot type is
   *    not in the policy map, consult the geometry's PlaneSlot.transparent
   *    field (from OBJ-005) if a geometry lookup function is provided.
   *    If neither source indicates transparency is needed, skip removal.
   *
   * 2. For images that need removal: check if they already have alpha
   *    (via Sharp metadata). If yes, skip.
   *
   * 3. For remaining images: apply background removal using the
   *    configured strategy.
   *
   * Returns a mapping from original paths to processed paths, suitable
   * for the asset orchestrator to rewrite manifest image references.
   *
   * @param entries - Array of { inputPath, slotType } pairs.
   * @param geometryLookup - Optional function that returns PlaneSlot.transparent
   *        for a given geometry name + slot name. Used for custom geometries
   *        whose slot types aren't in SLOT_REMOVAL_POLICY.
   * @param continueOnError - Passed through to batchRemoveBackgrounds.
   * @returns Promise<BatchRemovalResult>
   */
  processImagesForManifest(
    entries: Array<{ inputPath: string; slotType: string; geometryName?: string; slotName?: string }>,
    geometryLookup?: (geometryName: string, slotName: string) => boolean | undefined,
    continueOnError?: boolean
  ): Promise<BatchRemovalResult>;

  /**
   * Returns the resolved configuration (defaults applied).
   * Useful for diagnostics and logging.
   */
  getConfig(): Required<Omit<BackgroundRemovalConfig, 'chromaKey'>> & { chromaKey: Required<ChromaKeyConfig> };
}
```

### Module: `src/pipeline/alpha-check.ts`

A lightweight utility that checks whether an image file has an alpha channel, using Sharp's metadata (Node-side only, no browser involvement). This complements OBJ-015's browser-side alpha detection with a Node-side file-based check used before rendering.

```typescript
// src/pipeline/alpha-check.ts

/**
 * Checks whether an image file has an alpha channel by reading
 * its metadata via Sharp. Does NOT decode the full image.
 *
 * Uses sharp(inputPath).metadata() and checks:
 * - metadata.channels === 4 (RGBA), OR
 * - metadata.hasAlpha === true (Sharp's built-in flag)
 *
 * @param inputPath - Path to the image file.
 * @returns Promise<boolean> - true if the image has an alpha channel.
 * @throws Error if file doesn't exist or Sharp can't read it.
 */
export function imageHasAlpha(inputPath: string): Promise<boolean>;
```

## Design Decisions

### D1: Asset Pipeline Module, Not Engine Module

**Decision:** All background removal code lives in `src/pipeline/`, not `src/engine/`. The rendering engine never imports this module.

**Rationale:** AP-04 mandates clean separation: "The rendering engine accepts a manifest and pre-existing image/audio files. Asset generation is a separate pipeline stage." Background removal is asset preparation — it transforms raw AI-generated images into engine-ready assets. OBJ-057 (asset orchestration pipeline) is the intended consumer.

### D2: Factory Pattern via `createBackgroundRemover()`

**Decision:** The module exports a `createBackgroundRemover()` factory that returns a configured `BackgroundRemover` instance, rather than exporting bare functions with a config parameter on every call.

**Rationale:** The config (Python path, rembg model, timeouts, chroma key defaults) is stable across a pipeline run. A factory captures this config once. Multiple calls to `removeBackground()` share the config without re-specifying it. This also makes testing easier — tests can create removers with different configs without global state.

### D3: rembg as Primary Strategy, Chroma Key as Fallback

**Decision:** The `'auto'` strategy (the default) tries rembg first and falls back to chroma key if rembg is not installed. rembg is not a hard dependency — the module works without Python installed, just at lower quality.

**Rationale:** rembg (using U²-Net) produces significantly better masks than color-based removal, especially for subjects with complex edges (hair, fur, translucent elements). But requiring Python installation would complicate Docker images and CI setups. The chroma key fallback ensures the pipeline always works. The `isRembgAvailable()` check is cached — the availability probe runs once per process.

**Alternatives considered:**
1. **rembg only** — simpler but breaks on machines without Python.
2. **Chroma key only** — no Python dependency but poor quality on non-white backgrounds.
3. **Auto with fallback** (chosen) — best of both worlds.

### D4: Sequential Batch Processing (Not Parallel)

**Decision:** `batchRemoveBackgrounds()` processes images one at a time, not in parallel.

**Rationale:** rembg loads a ~170MB neural network model into memory. Running multiple rembg subprocesses in parallel would consume multiple GB of RAM on a 4GB VPS (C-08 target hardware). Sequential processing is slower but stays within memory bounds. The rembg model is loaded once on the first call and reused for subsequent images within the same subprocess — but since we spawn a new subprocess per image (simplest approach), the model reloads each time. If TC-12 testing reveals this is too slow, a persistent rembg subprocess (stdin/stdout protocol) could be added as an optimization — but the spec defines sequential single-subprocess as the baseline.

**Performance note:** At ~3-5 seconds per image (TC-12 target), a 5-scene video with 2 images needing removal takes 6-10 seconds total. This is negligible relative to the 15-minute render time (C-08).

### D5: Alpha Pre-Check Avoids Redundant Processing

**Decision:** Before applying any removal strategy, `removeBackground()` checks whether the input image already has an alpha channel (via Sharp metadata). If it does, the image is copied to the output path unchanged with `strategyUsed: 'none'`.

**Rationale:** Some image generation models (e.g., Flux.1 with appropriate prompting) can produce PNG images with transparency directly. Re-processing these through rembg would degrade quality. The alpha check is near-instant (~1ms via Sharp metadata) and avoids wasting 3-5 seconds of CPU time on images that don't need it.

### D6: Per-Slot-Type Policy with Geometry Fallback

**Decision:** `SLOT_REMOVAL_POLICY` is a static map of known slot names to boolean "needs removal." For custom geometries with non-standard slot names, `processImagesForManifest()` accepts an optional `geometryLookup` function that resolves to `PlaneSlot.transparent` from OBJ-005.

**Rationale:** The seed defines ~10 canonical slot names (Section 4.1), and the policy is clear: `subject` and `near_fg` need transparency; everything else doesn't. Hardcoding these is simple and correct for all built-in geometries. The geometry lookup fallback handles extensibility without coupling this module to the geometry registry directly.

### D7: Output as PNG (Always)

**Decision:** Background removal always outputs PNG, regardless of input format. If the input is JPEG or WebP, the output is a new PNG file with the alpha channel.

**Rationale:** PNG is the only commonly-supported lossless format with alpha channels. JPEG doesn't support alpha at all. WebP supports alpha but Three.js texture loading handles PNG more predictably across browser versions.

### D8: Chroma Key Algorithm via Sharp

**Decision:** The chroma key removal uses Sharp's `raw()` pixel access to implement color-distance-based alpha masking:

1. Read the image into raw RGBA buffer via Sharp.
2. Parse the target color hex to RGB.
3. For each pixel, compute Euclidean distance in RGB space: `d = sqrt((r-tr)² + (g-tg)² + (b-tb)²)`.
4. If `d <= threshold`: set alpha to 0 (fully transparent).
5. If `d > threshold` and feathering is enabled: for pixels in the range `[threshold, threshold + feather_range]`, set alpha proportionally (soft edge).
6. Write the result as PNG via Sharp.

**Rationale:** Sharp operates on raw pixel buffers efficiently in native code. The Euclidean RGB distance is the simplest color similarity metric that works reasonably well for solid-color backgrounds (white, black, green). It won't handle gradient backgrounds or complex scenes — that's what rembg is for.

### D9: rembg Subprocess Protocol

**Decision:** rembg is invoked as:
```
<pythonPath> -m rembg i -m <model> <inputPath> <outputPath>
```

Via Node.js `child_process.execFile()` (not `exec()` — avoids shell injection). The subprocess is given a timeout via `execFile`'s `timeout` option. Stderr is captured for error reporting.

**Rationale:** The `rembg i` (image) CLI is the simplest interface — file in, file out. No stdin/stdout streaming needed. `execFile` is safer than `exec` and provides built-in timeout support.

**Alternative considered:** Running rembg as a persistent subprocess with stdin/stdout streaming to avoid model reload per image. Deferred to optimization phase — the simple approach meets TC-12 targets and the added complexity of managing a long-running subprocess (lifecycle, error recovery, zombie processes) isn't justified for V1.

### D10: `sharp` as an npm Dependency

**Decision:** The module depends on `sharp` (MIT licensed) for image metadata inspection and chroma key processing.

**Rationale:** Sharp is already a natural dependency for image processing in a Node.js pipeline. It's MIT licensed (compliant with C-01). It provides fast native-code image decoding and metadata reading. The alpha check (`imageHasAlpha`) and chroma key pipeline both use Sharp. Adding Sharp is much simpler than implementing raw PNG/JPEG parsing.

**Constraint check:** C-01 lists allowed dependencies: `three`, `puppeteer`, `ffmpeg-static`, and "standard npm utilities." Sharp is a standard npm image processing utility, widely used, MIT licensed. It fits within the spirit of C-01's allowances.

## Acceptance Criteria

- [ ] **AC-01:** `src/pipeline/background-removal.ts` exports `createBackgroundRemover`, `isRembgAvailable`, `SLOT_REMOVAL_POLICY`, and all associated types (`RemovalStrategy`, `BackgroundRemovalConfig`, `ChromaKeyConfig`, `RemovalOptions`, `RemovalResult`, `BatchRemovalEntry`, `BatchRemovalResult`, `BackgroundRemover`).

- [ ] **AC-02:** `src/pipeline/alpha-check.ts` exports `imageHasAlpha`.

- [ ] **AC-03:** `isRembgAvailable()` returns `true` on a system with Python and rembg installed, and `false` on a system without them. The result is cached — calling it twice does not spawn two subprocesses.

- [ ] **AC-04:** `removeBackground()` on a JPEG image (no alpha) with strategy `'rembg'` produces a PNG output file with an alpha channel. The output file exists at the expected path. `strategyUsed` is `'rembg'`. `durationMs` is populated.

- [ ] **AC-05:** `removeBackground()` on a JPEG image with strategy `'chroma_key'` and a white background produces a PNG output file where formerly-white regions are transparent. `strategyUsed` is `'chroma_key'`.

- [ ] **AC-06:** `removeBackground()` on a PNG image that already has alpha returns `strategyUsed: 'none'`, `inputHadAlpha: true`, and the output file is a copy of the input.

- [ ] **AC-07:** `removeBackground()` with strategy `'auto'` uses `'rembg'` when rembg is available, and `'chroma_key'` when it is not.

- [ ] **AC-08:** `removeBackground()` on a non-existent file throws with message containing `"input file not found"`.

- [ ] **AC-09:** `removeBackground()` with strategy `'rembg'` when rembg is not installed throws with message containing `"rembg is not available"`.

- [ ] **AC-10:** `removeBackground()` with rembg that exceeds the timeout throws with message containing `"timed out"`.

- [ ] **AC-11:** rembg subprocess completes in under 5 seconds per image for a typical 1024×1024 image on a 4-core machine (TC-12).

- [ ] **AC-12:** `batchRemoveBackgrounds()` with `continueOnError: false` rejects on the first failure. Successfully processed images prior to the failure remain on disk.

- [ ] **AC-13:** `batchRemoveBackgrounds()` with `continueOnError: true` processes all images, collecting failures in `errors`. `failedCount` and `errors` reflect the failures.

- [ ] **AC-14:** `processImagesForManifest()` skips removal for images assigned to slots in `SLOT_REMOVAL_POLICY` with value `false` (e.g., `sky`, `floor`). Those entries appear in results with `strategyUsed: 'none'`.

- [ ] **AC-15:** `processImagesForManifest()` applies removal for images assigned to slots in `SLOT_REMOVAL_POLICY` with value `true` (e.g., `subject`, `near_fg`).

- [ ] **AC-16:** `processImagesForManifest()` with a `geometryLookup` function correctly uses it for slot types not in `SLOT_REMOVAL_POLICY`.

- [ ] **AC-17:** All output images from removal (rembg or chroma key) are valid PNG files with 4 channels (RGBA), verifiable via Sharp metadata.

- [ ] **AC-18:** The chroma key strategy with default settings (white, threshold 30) removes a solid white background from a test image, producing transparent regions where white was.

- [ ] **AC-19:** The chroma key strategy with a custom color (e.g., `'#00FF00'` green screen) removes that color.

- [ ] **AC-20:** `imageHasAlpha()` returns `true` for a PNG with alpha channel and `false` for a JPEG.

- [ ] **AC-21:** No module in `src/engine/` imports from `src/pipeline/`. (AP-04 enforcement.)

- [ ] **AC-22:** The rembg subprocess is invoked via `execFile` (not `exec`), preventing shell injection.

- [ ] **AC-23:** Output file paths follow the convention: if `outputDir` is set, `<outputDir>/<basename>_removed.png`; if `options.outputPath` is set, that exact path; otherwise `<inputDir>/<basename>_removed.png`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Input file doesn't exist | Throws: `"Background removal failed: input file not found: '{path}'"` |
| Input is unsupported format (e.g., .bmp, .tiff) | Throws: `"Background removal failed: unsupported format '{ext}' for '{path}'. Supported: png, jpg, jpeg, webp"` |
| Input already has alpha | Returns `strategyUsed: 'none'`, `inputHadAlpha: true`, output is copy of input |
| Strategy `'rembg'` but rembg not installed | Throws: `"Background removal failed: rembg is not available. Install with: pip install rembg[cpu]"` |
| Strategy `'auto'` and rembg not installed | Falls back to `'chroma_key'` silently. `strategyUsed: 'chroma_key'`. |
| rembg subprocess times out | Kills subprocess, throws: `"Background removal failed: rembg timed out after {ms}ms for '{path}'"` |
| rembg subprocess exits with non-zero code | Throws with stderr content: `"Background removal failed: rembg exited with code {code} for '{path}': {stderr}"` |
| rembg subprocess produces empty/missing output file | Throws: `"Background removal failed: rembg produced no output for '{path}'"` |
| Sharp chroma key on image with no matching pixels | Output has no transparent pixels — the image is unchanged. Not an error. |
| Chroma key threshold 0 | Only exact color matches are removed (very strict). |
| Chroma key threshold 255 | All pixels become transparent (removes everything). Warning logged. |
| Output directory doesn't exist | Create it recursively (`fs.mkdir` with `recursive: true`) before writing. |
| Input and output path are the same | The output overwrites the input. No special handling — the caller chose this explicitly. |
| Corrupt/truncated input image | Sharp metadata read fails. Throws: `"Background removal failed: cannot read image '{path}': {message}"` |
| Very large image (e.g., 8000x6000) | rembg may take longer but should still work. Chroma key via Sharp handles large images natively. Timeout protects against indefinite hangs. |
| Batch with empty array | Returns `BatchRemovalResult` with all counts 0, empty results array. |
| `processImagesForManifest` with unknown slot type not in policy, no geometry lookup | Slot defaults to `false` (no removal). Log info: `"Unknown slot type '{type}', skipping background removal."` |
| `processImagesForManifest` with unknown slot type, geometry lookup returns `undefined` | Same as above — defaults to no removal. |
| Python path is wrong (e.g., `'python4'`) | `isRembgAvailable()` returns false. If strategy was `'rembg'`, throws. If `'auto'`, falls back to chroma key. |
| rembg installed but model not downloaded | rembg downloads the model on first use. This may cause the first call to exceed the timeout. The default 30-second timeout accommodates this. |

## Test Strategy

### Unit Tests (No subprocess, no Sharp — mock dependencies)

1. **Policy logic tests:**
   - `SLOT_REMOVAL_POLICY['subject']` is `true`.
   - `SLOT_REMOVAL_POLICY['sky']` is `false`.
   - `SLOT_REMOVAL_POLICY['floor']` is `false`.
   - Unknown slot type falls through correctly in `processImagesForManifest`.

2. **Strategy resolution tests (mock `isRembgAvailable`):**
   - `'auto'` + rembg available → resolves to `'rembg'`.
   - `'auto'` + rembg unavailable → resolves to `'chroma_key'`.
   - Explicit `'rembg'` + rembg unavailable → throws.
   - Explicit `'none'` → always passes through.

3. **Config defaults:**
   - `createBackgroundRemover()` with no args has sensible defaults (strategy `'auto'`, python path `'python3'`, model `'u2net'`, timeout 30000, chroma key color `'#FFFFFF'`, threshold 30, feather 1).

4. **Output path generation:**
   - No outputDir, no outputPath → `<dir>/<name>_removed.png`.
   - With outputDir → `<outputDir>/<name>_removed.png`.
   - With explicit outputPath → exact path used.

### Integration Tests (Require Sharp, test images on disk)

Test images needed:
- `test_opaque.jpg` — JPEG, no alpha (a simple colored rectangle).
- `test_opaque.png` — PNG, no alpha.
- `test_alpha.png` — PNG with transparent background (circle on transparency).
- `test_white_bg.png` — PNG with white background (for chroma key testing).
- `test_green_bg.png` — PNG with green (#00FF00) background.

5. **`imageHasAlpha` tests:**
   - JPEG → false.
   - Opaque PNG → false.
   - Transparent PNG → true.

6. **Chroma key removal tests:**
   - White background image + default chroma key → output has alpha channel, white regions transparent.
   - Green background image + color `'#00FF00'` → output has alpha, green regions transparent.
   - Opaque JPEG with no white → output has alpha channel added but no transparent pixels.
   - Threshold 0 → very few pixels removed (only exact matches).

7. **Alpha pre-check passthrough:**
   - Image with alpha → `strategyUsed: 'none'`, `inputHadAlpha: true`, output is copy.

8. **Output file validation:**
   - All removal outputs are valid PNG with 4 channels (check via Sharp metadata).

9. **Error condition tests:**
   - Non-existent file → expected error.
   - Unsupported format → expected error.

### Integration Tests (Require Python + rembg)

These tests are conditional — they skip if rembg is not installed. Marked with a `@requires-rembg` tag or similar skip mechanism.

10. **`isRembgAvailable` test:**
    - Returns true when rembg is installed.
    - Returns false when Python path is invalid.
    - Result is cached (second call doesn't spawn subprocess).

11. **rembg removal test:**
    - Subject image with white background → output has alpha, subject preserved.
    - `durationMs < 5000` (TC-12 target, on a 1024x1024 image).

12. **rembg timeout test:**
    - Set timeout to 1ms → throws timeout error.

13. **rembg error test:**
    - Pass corrupt file → throws with stderr content.

### Batch and Pipeline Tests

14. **Batch sequential processing:**
    - Batch of 3 images → results array has 3 entries, ordered correctly.
    - `processedCount` + `skippedCount` = total entries.

15. **Batch continueOnError:**
    - Batch with one bad file, continueOnError=true → error collected, others processed.
    - Batch with one bad file, continueOnError=false → rejects on failure.

16. **`processImagesForManifest` slot filtering:**
    - Entries with `slotType: 'subject'` → processed.
    - Entries with `slotType: 'sky'` → skipped.
    - Entries with `slotType: 'subject'` but image already has alpha → skipped.

17. **`processImagesForManifest` geometry lookup:**
    - Custom slot type not in policy + geometry lookup returns `true` → processed.
    - Custom slot type not in policy + geometry lookup returns `false` → skipped.
    - Custom slot type not in policy + no geometry lookup → skipped.

### Relevant Testable Claims

- **TC-12:** rembg as subprocess under 5 seconds per image, acceptable mask quality. Directly tested by integration test #11.
- **OQ-02:** Best strategy for images without alpha. Resolved by this module's two-strategy approach.
- **C-09:** Image format tolerance. This module ensures the engine receives images with correct alpha when needed.

## Integration Points

### Depends on

| Dependency | What OBJ-052 uses |
|---|---|
| **OBJ-015** (Texture loader) | Conceptual dependency: OBJ-015 defines `TextureMetadata.hasAlpha` and the browser-side alpha detection. OBJ-052's Node-side alpha check (`imageHasAlpha` via Sharp) complements this for the asset pipeline context. OBJ-052 also imports `TextureSlotWarning` type for consistency with the warning vocabulary, though it does not call `checkTextureSlotCompatibility()` (that runs at render time, not asset prep time). The primary value of this dependency is that OBJ-015 established the alpha detection contract (what "has alpha" means: any pixel with alpha < 250) and OBJ-052 aligns with it. |

### Consumed by

| Downstream | How it uses OBJ-052 |
|---|---|
| **OBJ-057** (Asset orchestration pipeline) | Calls `createBackgroundRemover()` and `processImagesForManifest()` as part of the asset preparation stage (Appendix A, between steps 4 and 5). Receives `BatchRemovalResult` with processed image paths and rewrites the manifest's image URLs to point to the processed files before passing the manifest to the rendering engine. |

### File Placement

```
depthkit/
  src/
    pipeline/                        # NEW directory — asset pipeline utilities (per AP-04)
      background-removal.ts          # NEW — createBackgroundRemover, isRembgAvailable,
                                     #        SLOT_REMOVAL_POLICY, all types
      alpha-check.ts                 # NEW — imageHasAlpha utility
```

### npm Dependencies

| Package | Version | License | Purpose |
|---|---|---|---|
| `sharp` | ^0.33.x | MIT | Image metadata reading, chroma key pixel processing |

`sharp` is added to `package.json` `dependencies`. No Python packages are added to package.json — rembg is a system-level dependency detected at runtime.

## Open Questions

### OQ-A: Should rembg use a persistent subprocess for batch processing?

Currently each `removeBackground()` call spawns a new `python -m rembg i` subprocess, which reloads the U²-Net model (~170MB) each time. For batch processing, a persistent subprocess that accepts images on stdin and returns results on stdout would amortize the model load time. However, rembg's CLI doesn't natively support this streaming mode — it would require a custom Python wrapper script.

**Recommendation:** Defer for V1. The per-image subprocess approach is simpler and TC-12 targets (< 5s per image) likely account for model loading. If batch performance becomes a bottleneck, a persistent subprocess wrapper can be added as an optimization in a later objective.

### OQ-B: Should the chroma key support multiple target colors per image?

Some AI-generated images have near-white backgrounds with slight color gradients rather than a uniform white. A single chroma key color with threshold handles this to some extent, but a multi-color mode (e.g., "remove white AND light gray") could improve coverage.

**Recommendation:** Defer. The single-color + threshold approach covers the vast majority of cases. For gradient backgrounds, rembg is the better tool. Adding multi-color chroma key adds complexity for a marginal improvement.

### OQ-C: Should the module integrate directly with OBJ-015's `checkTextureSlotCompatibility()`?

OBJ-015 defines a Node-side warning utility that checks texture alpha against slot expectations. OBJ-052 could call this after processing to validate that removal succeeded. However, `checkTextureSlotCompatibility` operates on `TextureMetadata` (browser-side concept), not on file metadata.

**Recommendation:** Keep them separate. OBJ-052 validates its own output (verifies the output PNG has 4 channels). OBJ-015's warning runs at render time after textures are loaded into the browser. The two checks serve different stages of the pipeline.

### OQ-D: Should `imageHasAlpha` use the same threshold as OBJ-015 (alpha < 250)?

OBJ-015's browser-side alpha detection considers an image to "have alpha" if any pixel has alpha < 250. OBJ-052's `imageHasAlpha` checks Sharp's `metadata.hasAlpha` / `metadata.channels === 4`, which is a format-level check (does the image have an alpha channel at all), not a pixel-level check.

An image can have 4 channels (RGBA) but all pixels at alpha 255 — OBJ-015 would say `hasAlpha: false` while OBJ-052's `imageHasAlpha` would say `true`. This discrepancy is acceptable because OBJ-052's check is a coarser pre-filter ("does this image even have an alpha channel to work with?"), while OBJ-015's check is the authoritative pixel-level determination at render time.

**Recommendation:** Accept the discrepancy. Document it. OBJ-052's `imageHasAlpha` is a cheap pre-filter to avoid re-processing images that already went through background removal. If an image has 4 channels but all pixels are opaque, the worst case is that OBJ-052 skips it (it already "has alpha"), and OBJ-015 later warns that the alpha channel has no meaningful transparency. This is a benign false negative.

---

I believe this covers all the required dimensions: interface contracts, design decisions with rationale, acceptance criteria, edge cases, test strategy, integration points, and open questions. I'd like the Challenger to review and identify any gaps, ambiguities, or constraint violations.

---

## Round 2 — spec_challenger

I'll review the proposed spec thoroughly. Let me first check a few things in the codebase.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Grep,Glob",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Grep'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]
Let me check the OBJ-005 spec for the `PlaneSlot.transparent` field details and also look at the downstream consumer OBJ-057.
[Tool: Grep]
  Input: {
  "pattern": "transparent|PlaneSlot|SLOT_REMOVAL|slot_type",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "output_mode": "content",
  "-C": 5
}
[Tool Result] 1-# Specification: Scene Geometry Type Contract (OBJ-005)
2-
3-## Summary
4-
5:[Omitted long matching line]
6-
7-## Interface Contract
8-
9-### Core Types
10-
--
35- * A single named position in a scene geometry's spatial layout.
36- * Defines where a plane (textured mesh) is placed in 3D space.
37- *
38- * Extends PlaneTransform from OBJ-003, adding metadata fields specific
39- * to the geometry contract (required, description, rendering hints).
40: * Any function accepting PlaneTransform also accepts PlaneSlot.
41- *
42: * PlaneSlot values in a registered SceneGeometry are immutable templates
43- * (see D9). The readonly tuple types (Vec3, EulerRotation, Size2D) enforce
44- * this at compile time; deep freezing at registration enforces it at runtime.
45- * These values are the geometry's defaults. Downstream consumers (OBJ-036,
46- * OBJ-039) may apply per-scene overrides from the manifest by creating a
47- * new PlaneTransform with the override applied, rather than mutating the
48- ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: Scene Geometry Type Contract (OBJ-005)
     2→
     3→## Summary
     4→
     5→OBJ-005 defines the TypeScript type system for all scene geometries in depthkit: the `PlaneSlot` interface describing a single named position in a 3D scene, the `SceneGeometry` interface describing a complete spatial arrangement of planes, the `FogConfig` interface for depth-based atmospheric fading, a geometry registry with explicit registration and deep-freeze semantics, and the slot naming conventions that all 8 geometry implementations (OBJ-018 through OBJ-025) must follow. This is a pure type/contract module — it defines the shape of geometry data, not any specific geometry's values. It imports spatial primitives from OBJ-003 and is consumed by every downstream objective that creates, validates, instantiates, or queries scene geometries.
     6→
     7→## Interface Contract
     8→
     9→### Core Types
    10→
    11→```typescript
    12→// src/scenes/geometries/types.ts
    13... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": 150,
  "limit": 50
}
[Tool Result]    150→   */
   151→  default_camera: string;
   152→
   153→  /**
   154→   * Optional Three.js fog configuration for this geometry.
   155→   * When present, the renderer adds fog to the scene.
   156→   * Can be overridden per-scene in the manifest.
   157→   */
   158→  fog?: FogConfig;
   159→
   160→  /**
   161→   * Human-readable description of this geometry's visual character.
   162→   * Must be non-empty. Used in SKILL.md documentation. Should describe
   163→   * the spatial feel and typical use case, not the technical layout.
   164→   * Example: "A corridor with floor, ceiling, and walls receding to
   165→   * a vanishing point. Camera pushes forward for a 'traveling through
   166→   * a space' effect."
   167→   */
   168→  description: string;
   169→
   170→  /**
   171→   * Suggested aspect ratio for this geometry.
   172→   * 'landscape' means it's designed for 16:9,
   173→   * 'portrait' means 9:16,
   174→   * 'both' means it works well in either orientation.
  ... [truncated]
Good, now I have a clear understanding of the type system. Let me also check what consumes OBJ-052 — specifically looking at the `Consumed by` section mentioning OBJ-057:
[Tool: Grep]
  Input: {
  "pattern": "OBJ-052",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit",
  "output_mode": "content",
  "-C": 2,
  "glob": "*.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/sessions/init-deliberation-transcript.md-158-|---|---|---|---|---|
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/sessions/init-deliberation-transcript.md-159-| **OBJ-051** | Image generation strategy — Flux.1 Schnell prompt engineering per slot type per §4.7, perspective-aware prompting for floor/wall/ceiling textures | integration | 007 | medium |
sessions/init-deliberation-transcript.md:160:| **OBJ-052** | Background removal integration — rembg subprocess, chroma key alternative, per-slot-type strategy; OQ-02, TC-12 | integration | 015 | medium |
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/sessions/init-deliberation-transcript.md-161-| **OBJ-053** | Semantic caching — database schema — AssetLibrary table, pgvector index, slot_type filtering per §4.10 | integration | 007 | medium |
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/sessions/init-delibe... [truncated]
Now I have a thorough understanding of the context. Let me deliver my review.

---

## Challenger Review — OBJ-052 Background Removal Integration

### Points of Agreement (What's Sound)

1. **AP-04 compliance is correctly handled.** Placing everything under `src/pipeline/` and never importing from `src/engine/` is correct. AC-21 explicitly tests this.
2. **Two-strategy approach (rembg + chroma key fallback) is well-reasoned.** D3's rationale is solid.
3. **Sequential batch processing (D4)** is the right call for the 4GB VPS target.
4. **Alpha pre-check (D5)** to avoid redundant processing is smart.
5. **Factory pattern (D2)** keeps config clean across calls.
6. **Edge cases table** is comprehensive — most failure modes are covered.
7. **OQ-D** honestly documents the `imageHasAlpha` vs OBJ-015 alpha detection discrepancy. Good.

### Issues

---

**Issue 1: `SLOT_REMOVAL_POLICY` is a static map of hardcoded slot names — this will rot as geometries are added.** — Major

The seed explicitly says (Section 4.2, D7 of OBJ-005) that slot names are extensible — any geometry can define arbitrary slot names matching `/^[a-z][a-z0-9_]*$/`. `SLOT_REMOVAL_POLICY` hardcodes 10 names. When OBJ-022 (diorama), OBJ-023 (portal), OBJ-024 (panorama), or OBJ-025 (close_up) introduce slots like `frame_inner`, `frame_outer`, `ground`, `landmark`, etc., this map silently misses them. The `processImagesForManifest` fall-through behavior (default to no removal) means new geometry slots that need transparency will silently NOT get background removal.

**Fix:** The primary decision mechanism should be the geometry's `PlaneSlot.transparent` field (from OBJ-005), not a hardcoded policy map. The `SLOT_REMOVAL_POLICY` can remain as a convenience/override layer, but `processImagesForManifest` should:
1. First check `SLOT_REMOVAL_POLICY` for an explicit override.
2. If not found, consult `geometryLookup` (which reads `PlaneSlot.transparent`).
3. If neither source has an answer, *then* default to no removal with a logged warning.

Currently the spec has this backwards — it checks the static map first, and geometry lookup is only for "custom geometries whose slot types aren't in SLOT_REMOVAL_POLICY." But `subject` in one geometry might have `transparent: false` (imagine a close_up where the subject fills the whole frame against a solid background). The geometry's `PlaneSlot.transparent` is the authoritative source; the policy map should be the fallback when no geometry info is available.

---

**Issue 2: `processImagesForManifest` signature requires `geometryName` and `slotName` but the entries only have `slotType` — vocabulary confusion.** — Major

The entry type is:
```typescript
Array<{ inputPath: string; slotType: string; geometryName?: string; slotName?: string }>
```

But `slotType` in the seed vocabulary (Section 4.10, `AssetLibrary` table) means the semantic category of the image (`'sky'`, `'subject'`, etc.) — which is the role in the asset cache, not the slot name in a geometry. Meanwhile `slotName` is the actual key in `SceneGeometry.slots` (e.g., `'left_wall'`, `'end_wall'`). These can differ: a geometry might have a slot named `ground` that is semantically a `floor` type.

The spec conflates `slotType` (asset cache category) with slot name (geometry key). This matters because `SLOT_REMOVAL_POLICY` uses seed slot names, while `geometryLookup` needs geometry name + slot name.

**Fix:** Clarify the entry type. If the primary use case is the asset pipeline (OBJ-057), the entry should carry both the slot name (geometry key) and optionally the geometry name:
```typescript
Array<{ inputPath: string; slotName: string; geometryName?: string }>
```
Drop `slotType` entirely — it belongs to the asset caching layer (OBJ-054), not background removal. `SLOT_REMOVAL_POLICY` should be keyed by slot name (which it already is — `subject`, `floor`, etc.), and `geometryLookup` takes `geometryName + slotName`.

---

**Issue 3: `TextureSlotWarning` import from `../engine/texture-types.js` is declared but never actually used.** — Minor

The interface contract imports `TextureSlotWarning` but no function in the module produces or consumes it. The spec says it's imported "for consistency with the warning vocabulary" but this is dead coupling. If the warning type is never used, don't import it.

**Fix:** Remove the `TextureSlotWarning` import. If a future version needs it, it can be added then. The spec should only define actual dependencies.

---

**Issue 4: Output file naming convention has an ambiguity for files without extensions.** — Minor

AC-23 says: `<inputDir>/<basename>_removed.png`. But what is "basename"? If input is `subject.jpg`, is the output `subject_removed.png` or `subject.jpg_removed.png`?

**Fix:** Explicitly state: "basename" means the filename without its extension. E.g., `subject.jpg` → `subject_removed.png`, `my.image.webp` → `my.image_removed.png`. The extension is always `.png` (per D7).

---

**Issue 5: The `chromaKey.feather` description says "radius in pixels" but the algorithm description (D8) mentions `feather_range` without defining it.** — Major

D8 step 5 says: "for pixels in the range `[threshold, threshold + feather_range]`, set alpha proportionally (soft edge)." But `feather_range` is never defined. Is it the same as `feather`? If `feather` is 1 pixel as default, what does "feather_range" in color-distance space mean? A pixel radius and a color-distance range are fundamentally different units.

**Fix:** The feathering algorithm needs clarification. One approach: after the binary threshold pass, apply a Gaussian blur of `feather` pixel radius to the alpha channel only. This is simpler and more predictable than mixing color-distance and pixel-radius concepts. Alternatively, define feathering as: pixels with color distance in `[threshold, threshold + feather * K]` (where K is a scaling constant) get proportional alpha `(d - threshold) / (feather * K)`. Either way, the spec must pin down the algorithm precisely enough that an implementer doesn't have to guess.

---

**Issue 6: No acceptance criterion for `getConfig()`.** — Minor

The `BackgroundRemover` interface declares `getConfig()` but no AC tests its return value or default resolution behavior.

**Fix:** Add an AC: "AC-24: `getConfig()` returns the resolved configuration with all defaults applied. A remover created with `createBackgroundRemover()` (no args) returns `{ defaultStrategy: 'auto', pythonPath: 'python3', rembgModel: 'u2net', rembgTimeout: 30000, outputDir: undefined, chromaKey: { color: '#FFFFFF', threshold: 30, feather: 1 } }`." (Adjust for the `outputDir` — it's optional, so should it appear as `undefined` or be omitted? Specify.)

---

**Issue 7: The dependency on OBJ-015 is tenuous and misdescribed.** — Major

The spec says OBJ-052 depends on OBJ-015 and imports `TextureSlotWarning` (which per Issue 3 is unused). The *actual* relationship is:
- OBJ-015 detects alpha at render time (browser-side).
- OBJ-052 applies background removal at asset-prep time (Node-side).
- They are complementary but don't share code.

The spec's "Depends on" section says the primary value is "OBJ-015 established the alpha detection contract (what 'has alpha' means: any pixel with alpha < 250) and OBJ-052 aligns with it." But OBJ-052's `imageHasAlpha` uses Sharp's `metadata.hasAlpha` (format-level 4-channel check), which does NOT align with OBJ-015's pixel-level threshold of 250. OQ-D acknowledges this discrepancy but the "Depends on" section claims alignment that doesn't exist.

The real dependency is on **OBJ-005** (for `PlaneSlot.transparent`) — that's where the authoritative "does this slot need alpha?" information lives. The progress map says OBJ-052 depends on OBJ-015, so we respect the DAG, but the spec should honestly describe the relationship.

**Fix:** Rewrite the "Depends on" section to be honest:
- **OBJ-015**: The progress map declares this dependency. The practical connection is conceptual: both modules deal with alpha detection, and OBJ-052's output (images with alpha) feeds into the browser where OBJ-015 loads them. OBJ-052 does NOT import any code from OBJ-015. The alpha detection methods are intentionally different (format-level vs pixel-level) and complementary.
- Also add OBJ-005 as a conceptual dependency (for `PlaneSlot.transparent`), noting that OBJ-052 doesn't directly import OBJ-005 types but its `geometryLookup` callback reads from OBJ-005's data.

---

**Issue 8: `batchRemoveBackgrounds` with empty array — spec says "returns BatchRemovalResult with all counts 0" but the edge case table doesn't list this and there's no AC for it.** — Minor

**Fix:** Add an AC: "AC-25: `batchRemoveBackgrounds([])` resolves with a `BatchRemovalResult` where `results` is empty, `processedCount` is 0, `skippedCount` is 0, `failedCount` is 0, and `totalDurationMs` is approximately 0."

---

**Issue 9: `RemovalResult.outputPath` when `strategyUsed: 'none'` and `inputHadAlpha: true` — is the file copied or is `outputPath === inputPath`?** — Major

D5 says "the image is copied to the output path unchanged." But copying a file just to say "we didn't change it" is wasteful I/O. In the asset pipeline (OBJ-057), what it actually needs is a path to use in the manifest. If the image is already good, the original path is fine.

The spec is ambiguous: "copied (or symlinked) to outputPath" — which one? And if copying, the output path is derived from the naming convention, so the caller gets a different path than the input. But if we return `outputPath === inputPath`, that's simpler.

**Fix:** Make an explicit design decision. Recommendation: when `strategyUsed: 'none'`, set `outputPath = inputPath` (no copy, no symlink). The original file is already usable. The caller (OBJ-057) can use the path directly. Add a note that no file I/O occurs in this case. Update the edge case table and acceptance criteria to match.

---

**Issue 10: `processImagesForManifest` returns `BatchRemovalResult` but this type has `failedCount` and `errors` fields described as "Only present when continueOnError is true." TypeScript doesn't support conditional field presence based on a runtime parameter.** — Minor

**Fix:** Make `failedCount` and `errors` always present on `BatchRemovalResult` (they're just 0 and `{}` when no errors). Remove the "only present when" language. The type should be unconditional.

---

**Issue 11: Supported input format list (`png, jpg, jpeg, webp`) doesn't mention whether the output of one removal can be the input to another.** — Minor (borderline nitpick, but worth specifying)

If an image has already been processed (output is `_removed.png`), and the pipeline runs again, the `_removed.png` will be detected as "has alpha" and skipped. This is correct behavior, but isn't documented.

**Fix:** Add a note in the edge case table: "Input is a previously processed `_removed.png` file → Detected as having alpha, returned as `strategyUsed: 'none'`. Idempotent."

---

**Issue 12: The spec says `sharp` is `^0.33.x` but doesn't verify that this version's `metadata()` returns `hasAlpha`.** — Minor

Sharp's `metadata().hasAlpha` has been available since much earlier versions, but the spec should confirm the specific API it relies on.

**Fix:** Just add a note that `metadata().channels` and `metadata().hasAlpha` are stable Sharp APIs available in all 0.3x releases. No code change needed, just documentation confidence.

---

### Summary of Issues by Severity

| # | Severity | Issue |
|---|----------|-------|
| 1 | Major | `SLOT_REMOVAL_POLICY` hardcoded map should be fallback, not primary; `PlaneSlot.transparent` is authoritative |
| 2 | Major | `slotType` vs `slotName` vocabulary confusion in `processImagesForManifest` entries |
| 5 | Major | Chroma key feathering algorithm is underspecified (`feather_range` undefined) |
| 7 | Major | Dependency on OBJ-015 is misdescribed; real dependency is conceptual + OBJ-005 |
| 9 | Major | Copy vs no-copy for passthrough images is ambiguous |
| 3 | Minor | Unused `TextureSlotWarning` import |
| 4 | Minor | Output basename definition ambiguous for multi-dot filenames |
| 6 | Minor | No AC for `getConfig()` |
| 8 | Minor | No AC for empty batch |
| 10 | Minor | `failedCount`/`errors` conditional presence impossible in TypeScript |
| 11 | Minor | Idempotency behavior undocumented |
| 12 | Minor | Sharp version API confidence |

Five major issues need resolution before convergence. Please revise.

---

## Round 3 — spec_author

All five major issues are valid. Let me address each systematically and present the revised spec.

## Issue-by-Issue Responses

**Issue 1 (Major): SLOT_REMOVAL_POLICY should be fallback, not primary.** ✅ Accepted. The challenger is right — `PlaneSlot.transparent` is the authoritative source from OBJ-005. I'm inverting the precedence: geometry lookup first, then static policy as fallback when no geometry info is available. The static map becomes a "best guess for common slots when the caller doesn't provide geometry context."

**Issue 2 (Major): slotType vs slotName vocabulary confusion.** ✅ Accepted. Dropping `slotType` from the entry type entirely. The entry carries `slotName` (the geometry slot key) and optionally `geometryName`. `SLOT_REMOVAL_POLICY` is already keyed by slot name, so this is consistent.

**Issue 3 (Minor): Unused TextureSlotWarning import.** ✅ Accepted. Removed.

**Issue 4 (Minor): Output basename ambiguity.** ✅ Accepted. Explicitly defined: basename = filename without its final extension. `subject.jpg` → `subject_removed.png`. `my.image.webp` → `my.image_removed.png`.

**Issue 5 (Major): Chroma key feathering underspecified.** ✅ Accepted. Replacing the mixed-unit approach with a clearer algorithm: after the binary threshold pass, apply a Gaussian blur of `feather` pixel radius to the alpha channel only via Sharp's `blur()`. This is well-defined and Sharp-native.

**Issue 6 (Minor): No AC for getConfig().** ✅ Accepted. Added AC-24.

**Issue 7 (Major): Dependency on OBJ-015 misdescribed.** ✅ Accepted. Rewritten to be honest about the relationship. Added OBJ-005 as a conceptual dependency.

**Issue 8 (Minor): No AC for empty batch.** ✅ Accepted. Added AC-25.

**Issue 9 (Major): Copy vs no-copy for passthrough.** ✅ Accepted. When `strategyUsed: 'none'`, `outputPath = inputPath`. No file I/O. This is simpler and the caller (OBJ-057) can use the path directly.

**Issue 10 (Minor): failedCount/errors conditional presence.** ✅ Accepted. Made unconditional — always present, default to `0` and `{}`.

**Issue 11 (Minor): Idempotency undocumented.** ✅ Accepted. Added to edge case table.

**Issue 12 (Minor): Sharp version confidence.** ✅ Accepted. Added note.

---

# Revised Specification: OBJ-052 — Background Removal Integration

## Summary

OBJ-052 defines a Node.js module for removing backgrounds from images as part of the asset preparation pipeline (not the rendering engine, per AP-04). It provides two removal strategies: **rembg** (Python subprocess, high-quality AI-based matting) as the primary strategy, and **Sharp-based chroma key** (pure Node.js, no Python dependency) as the fallback. A per-slot decision determines which images need background removal — the authoritative source is the geometry's `PlaneSlot.transparent` field (from OBJ-005), with a static policy map as fallback for when geometry info is unavailable. Only slots that expect transparency (typically `subject`, `near_fg`) are processed; opaque slots (`sky`, `floor`, `back_wall`, etc.) are passed through unchanged. This module directly addresses OQ-02 (best strategy for images without alpha) and TC-12 (rembg viability as subprocess).

## Interface Contract

### Module: `src/pipeline/background-removal.ts`

This module lives outside `src/engine/` per AP-04. It is consumed by the asset orchestration pipeline (OBJ-057) and is never imported by the rendering engine.

```typescript
// src/pipeline/background-removal.ts

/**
 * The removal strategy to use.
 * - 'rembg': AI-based matting via Python subprocess. Best quality.
 * - 'chroma_key': Sharp-based color range removal. No Python dependency.
 * - 'none': Pass through unchanged.
 * - 'auto': Try rembg first; if unavailable, fall back to chroma_key.
 */
export type RemovalStrategy = 'rembg' | 'chroma_key' | 'none' | 'auto';

/**
 * Configuration for the background removal module.
 * Passed once at initialization; individual calls can override per-image.
 */
export interface BackgroundRemovalConfig {
  /**
   * Default strategy when not specified per-call.
   * Default: 'auto'.
   */
  defaultStrategy?: RemovalStrategy;

  /**
   * Path to the Python executable. Used when strategy is 'rembg'.
   * Default: 'python3'. Falls back to 'python' if 'python3' is not found.
   */
  pythonPath?: string;

  /**
   * The rembg model to use.
   * Default: 'u2net' (general purpose, good balance of speed and quality).
   * Other options: 'u2netp' (lightweight/faster), 'isnet-general-use'.
   * Passed to rembg as: `rembg i -m <model> <input> <output>`
   */
  rembgModel?: string;

  /**
   * Timeout in milliseconds for the rembg subprocess per image.
   * Default: 30000 (30 seconds).
   * If exceeded, the subprocess is killed and the call rejects.
   */
  rembgTimeout?: number;

  /**
   * Default chroma key settings, used when strategy is 'chroma_key'.
   */
  chromaKey?: ChromaKeyConfig;

  /**
   * Directory for writing processed output images.
   * If not specified, output is written alongside the input with a
   * '_removed' suffix before the final extension, with .png extension.
   * E.g., 'subject.jpg' → 'subject_removed.png'.
   * If specified, output files are written to this directory using the
   * same naming convention.
   */
  outputDir?: string;
}

/**
 * Configuration for Sharp-based chroma key removal.
 */
export interface ChromaKeyConfig {
  /**
   * The target background color to remove, as a hex string.
   * Default: '#FFFFFF' (white — the most common AI-generated background).
   */
  color?: string;

  /**
   * Color distance threshold (0–255) in Euclidean RGB space.
   * Pixels within this distance of the target color become fully transparent.
   * Default: 30.
   * Lower = stricter matching (fewer pixels removed).
   * Higher = more aggressive removal (may eat into subject edges).
   */
  threshold?: number;

  /**
   * Gaussian blur radius in pixels applied to the alpha channel after
   * the binary threshold pass. Softens the boundary between transparent
   * and opaque regions.
   * Default: 1.
   * 0 = hard edge (no feathering).
   * 1-3 = subtle softening (recommended).
   * >3 = visible blur at edges.
   *
   * Implementation: After the binary alpha mask is computed (pixels below
   * threshold → alpha 0, above → alpha 255), extract the alpha channel,
   * apply Sharp's blur(feather) to it, then recombine with the RGB channels.
   */
  feather?: number;
}

/**
 * Per-image options for a single removal call.
 * Overrides the module-level config for this specific image.
 */
export interface RemovalOptions {
  /** Override the strategy for this image. */
  strategy?: RemovalStrategy;

  /** Override chroma key config for this image. Only used when effective strategy is 'chroma_key'. */
  chromaKey?: ChromaKeyConfig;

  /**
   * Explicit output path. Overrides the outputDir/suffix convention.
   * Must end with '.png' (per D7: all removal output is PNG).
   */
  outputPath?: string;

  /** Override rembg timeout for this image. */
  timeout?: number;
}

/**
 * Result of a single background removal operation.
 */
export interface RemovalResult {
  /** Absolute path to the input image. */
  inputPath: string;

  /**
   * Absolute path to the output image (with alpha channel).
   * When strategyUsed is 'none' (image already had alpha or slot doesn't
   * need removal), this equals inputPath — no file copy occurs.
   */
  outputPath: string;

  /**
   * The strategy that was actually used.
   * If 'auto' was requested and rembg was available, this is 'rembg'.
   * If 'auto' was requested and rembg was unavailable, this is 'chroma_key'.
   * If the image already had alpha, this is 'none' (passthrough).
   * If the slot doesn't need removal, this is 'none'.
   */
  strategyUsed: 'rembg' | 'chroma_key' | 'none';

  /**
   * Whether the input image already had an alpha channel.
   * Determined by inspecting the image metadata via Sharp
   * (metadata.channels === 4 OR metadata.hasAlpha === true).
   * When true, strategyUsed is 'none' and outputPath === inputPath.
   */
  inputHadAlpha: boolean;

  /** Processing duration in milliseconds. */
  durationMs: number;
}

/**
 * An entry in a batch removal request.
 */
export interface BatchRemovalEntry {
  /** Input image path (absolute or relative to cwd). */
  inputPath: string;

  /**
   * The slot name this image is destined for (the key in SceneGeometry.slots).
   * E.g., 'subject', 'floor', 'left_wall'.
   * Used by processImagesForManifest() to decide whether removal is needed.
   * When calling removeBackground() directly, this field is not used.
   */
  slotName?: string;

  /** Per-image overrides. */
  options?: RemovalOptions;
}

/**
 * Result of a batch removal operation.
 */
export interface BatchRemovalResult {
  /** Results ordered to match input entries. */
  results: RemovalResult[];

  /** Total processing duration in milliseconds (wall clock for the whole batch). */
  totalDurationMs: number;

  /** Count of images that were processed (strategy != 'none'). */
  processedCount: number;

  /** Count of images that were skipped (already had alpha or slot didn't need it). */
  skippedCount: number;

  /** Count of images that failed. 0 when no errors occurred. */
  failedCount: number;

  /** Errors for failed images, keyed by input path. Empty object when no errors. */
  errors: Record<string, string>;
}

/**
 * Fallback removal policy for common slot names.
 * Used ONLY when no geometry lookup is provided or the geometry lookup
 * returns undefined for a given slot. The authoritative source for
 * "does this slot need transparency?" is PlaneSlot.transparent (OBJ-005),
 * accessed via the geometryLookup callback.
 *
 * This map provides reasonable defaults for the canonical slot names
 * defined in the seed (Sections 4.1, 4.2) so that callers without
 * geometry context (e.g., standalone CLI usage) get sensible behavior.
 */
export const SLOT_REMOVAL_POLICY: Readonly<Record<string, boolean>> = {
  // Slots that typically need transparency
  subject: true,
  near_fg: true,

  // Slots that do NOT need transparency (opaque fills)
  sky: false,
  back_wall: false,
  midground: false,
  floor: false,
  ceiling: false,
  left_wall: false,
  right_wall: false,
  end_wall: false,
  backdrop: false,
};

// ── Exported Functions ──────────────────────────────────────────

/**
 * Checks whether rembg is installed and callable.
 *
 * Spawns `<pythonPath> -m rembg --help` and checks for a zero exit code.
 * Caches the result for the lifetime of the process.
 *
 * @param pythonPath - Path to Python executable. Default: 'python3'.
 * @returns Promise<boolean> - true if rembg is available and callable.
 */
export function isRembgAvailable(pythonPath?: string): Promise<boolean>;

/**
 * Creates a configured background removal instance.
 *
 * @param config - Module-level configuration. All fields optional.
 * @returns A BackgroundRemover instance with all removal methods.
 */
export function createBackgroundRemover(
  config?: BackgroundRemovalConfig
): BackgroundRemover;

/**
 * The configured background remover instance.
 */
export interface BackgroundRemover {
  /**
   * Removes the background from a single image.
   *
   * Workflow:
   * 1. Resolve inputPath to absolute path. Verify file exists.
   * 2. Verify file extension is supported (png, jpg, jpeg, webp).
   * 3. Check if the input already has an alpha channel (via Sharp metadata).
   *    If yes: return with strategyUsed='none', outputPath=inputPath.
   * 4. Determine effective strategy:
   *    - If options.strategy is set, use it.
   *    - Else use config.defaultStrategy (default: 'auto').
   *    - If 'auto': check isRembgAvailable(). If yes → 'rembg'. Else → 'chroma_key'.
   *    - If 'none': return with outputPath=inputPath.
   * 5. Execute the strategy:
   *    - 'rembg': spawn subprocess, wait for completion.
   *    - 'chroma_key': process via Sharp pipeline.
   * 6. Verify output file exists and is a valid PNG with alpha channel.
   * 7. Return RemovalResult.
   *
   * @throws Error if inputPath does not exist:
   *         "Background removal failed: input file not found: '{path}'"
   * @throws Error if inputPath is not a supported image format:
   *         "Background removal failed: unsupported format '{ext}' for '{path}'. Supported: png, jpg, jpeg, webp"
   * @throws Error if rembg strategy is requested but rembg is unavailable:
   *         "Background removal failed: rembg is not available. Install with: pip install rembg[cpu]"
   * @throws Error if rembg subprocess times out:
   *         "Background removal failed: rembg timed out after {ms}ms for '{path}'"
   * @throws Error if rembg subprocess exits with non-zero code:
   *         "Background removal failed: rembg exited with code {code} for '{path}': {stderr}"
   * @throws Error if Sharp processing fails:
   *         "Background removal failed: chroma key processing error for '{path}': {message}"
   */
  removeBackground(
    inputPath: string,
    options?: RemovalOptions
  ): Promise<RemovalResult>;

  /**
   * Processes multiple images sequentially.
   *
   * Sequential (not parallel) because rembg is CPU-intensive and
   * parallelism would cause memory pressure on 4GB VPS target hardware.
   *
   * @param entries - Array of images to process. Empty array is valid (returns empty results).
   * @param continueOnError - If true, failures are collected in errors.
   *        If false (default), the first failure rejects the promise.
   * @returns Promise<BatchRemovalResult>
   */
  batchRemoveBackgrounds(
    entries: BatchRemovalEntry[],
    continueOnError?: boolean
  ): Promise<BatchRemovalResult>;

  /**
   * High-level function for the asset pipeline (OBJ-057).
   *
   * Takes a list of slot-name + image-path pairs and applies background
   * removal ONLY to images assigned to slots that need transparency.
   *
   * Decision precedence for whether a slot needs removal:
   * 1. If geometryLookup is provided and returns a boolean for
   *    (geometryName, slotName): use that value. This reads
   *    PlaneSlot.transparent from OBJ-005, which is authoritative.
   * 2. Else if slotName is in SLOT_REMOVAL_POLICY: use that value.
   *    This is the fallback for when geometry info is unavailable.
   * 3. Else: default to false (no removal). Log info:
   *    "Unknown slot '{slotName}', skipping background removal."
   *
   * For images that need removal: check if they already have alpha
   * (via Sharp metadata). If yes, skip (return strategyUsed='none').
   *
   * Returns a BatchRemovalResult. The caller (OBJ-057) uses
   * result.results[i].outputPath to rewrite manifest image references.
   *
   * @param entries - Array of { inputPath, slotName, geometryName? } pairs.
   * @param geometryLookup - Optional function that returns PlaneSlot.transparent
   *        for a given geometry name + slot name. Returns boolean or undefined.
   *        When undefined, falls through to SLOT_REMOVAL_POLICY.
   * @param continueOnError - Passed through to batchRemoveBackgrounds.
   */
  processImagesForManifest(
    entries: Array<{ inputPath: string; slotName: string; geometryName?: string }>,
    geometryLookup?: (geometryName: string, slotName: string) => boolean | undefined,
    continueOnError?: boolean
  ): Promise<BatchRemovalResult>;

  /**
   * Returns the resolved configuration with all defaults applied.
   */
  getConfig(): ResolvedBackgroundRemovalConfig;
}

/**
 * The fully resolved configuration with all defaults applied.
 * All fields are defined (no optionals).
 */
export interface ResolvedBackgroundRemovalConfig {
  defaultStrategy: RemovalStrategy;
  pythonPath: string;
  rembgModel: string;
  rembgTimeout: number;
  outputDir: string | undefined;
  chromaKey: Required<ChromaKeyConfig>;
}
```

### Module: `src/pipeline/alpha-check.ts`

```typescript
// src/pipeline/alpha-check.ts

/**
 * Checks whether an image file has an alpha channel by reading
 * its metadata via Sharp. Does NOT decode the full image.
 *
 * Uses sharp(inputPath).metadata() and checks:
 * - metadata.channels === 4 (RGBA), OR
 * - metadata.hasAlpha === true (Sharp's built-in flag)
 *
 * Note: This is a format-level check, not a pixel-level check.
 * An image can have 4 channels with all pixels at alpha 255.
 * OBJ-015's browser-side detection uses pixel sampling (alpha < 250)
 * for the authoritative render-time check. This function is a
 * cheaper pre-filter for the asset pipeline — see OQ-D.
 *
 * @param inputPath - Path to the image file.
 * @returns Promise<boolean> - true if the image has an alpha channel.
 * @throws Error if file doesn't exist or Sharp can't read it.
 */
export function imageHasAlpha(inputPath: string): Promise<boolean>;
```

## Design Decisions

### D1: Asset Pipeline Module, Not Engine Module

**Decision:** All background removal code lives in `src/pipeline/`, not `src/engine/`. The rendering engine never imports this module.

**Rationale:** AP-04 mandates clean separation: "The rendering engine accepts a manifest and pre-existing image/audio files. Asset generation is a separate pipeline stage."

### D2: Factory Pattern via `createBackgroundRemover()`

**Decision:** The module exports a `createBackgroundRemover()` factory that returns a configured `BackgroundRemover` instance.

**Rationale:** The config (Python path, rembg model, timeouts, chroma key defaults) is stable across a pipeline run. A factory captures this once. Also simplifies testing — create removers with different configs without global state.

### D3: rembg as Primary Strategy, Chroma Key as Fallback

**Decision:** The `'auto'` strategy (the default) tries rembg first and falls back to chroma key if rembg is not installed. rembg is not a hard dependency.

**Rationale:** rembg (U²-Net) produces significantly better masks than color-based removal, especially for complex edges (hair, fur, translucent elements). But requiring Python would complicate Docker/CI setups. The chroma key fallback ensures the pipeline always works. `isRembgAvailable()` is cached per process.

**Alternatives considered:**
1. **rembg only** — breaks on machines without Python.
2. **Chroma key only** — no Python dependency but poor quality on non-white backgrounds.
3. **Auto with fallback** (chosen) — best of both worlds.

### D4: Sequential Batch Processing (Not Parallel)

**Decision:** `batchRemoveBackgrounds()` processes images one at a time.

**Rationale:** rembg loads a ~170MB neural network model. Parallel subprocesses would consume multiple GB of RAM on a 4GB VPS (C-08 target). Sequential processing stays within memory bounds. At ~3-5 seconds per image (TC-12), a 5-scene video with 2 images needing removal takes 6-10 seconds — negligible relative to the 15-minute render time.

### D5: Alpha Pre-Check Avoids Redundant Processing

**Decision:** Before applying any removal strategy, `removeBackground()` checks whether the input image already has an alpha channel via Sharp metadata. If it does, `outputPath = inputPath` with `strategyUsed: 'none'`. No file copy or symlink — no I/O at all.

**Rationale:** Some image generators produce PNGs with transparency directly. Re-processing through rembg would degrade quality. The alpha check is near-instant (~1ms via Sharp metadata). Returning `outputPath = inputPath` avoids wasteful file copies — the caller just uses the original path.

### D6: Geometry Lookup First, Static Policy as Fallback

**Decision:** `processImagesForManifest()` determines whether a slot needs removal by checking three sources in precedence order:
1. `geometryLookup(geometryName, slotName)` → reads `PlaneSlot.transparent` from OBJ-005. **This is authoritative.**
2. `SLOT_REMOVAL_POLICY[slotName]` → hardcoded map of canonical slot names. **This is the fallback** for standalone usage without geometry context.
3. Default to `false` (no removal) with an info log.

**Rationale:** `PlaneSlot.transparent` is the authoritative source from OBJ-005. It covers all geometries including future ones (OBJ-022 through OBJ-025) with non-canonical slot names. The static map exists for convenience when the caller doesn't have geometry context (e.g., standalone CLI usage or unit testing). This inversion from the original proposal fixes the extensibility problem: new geometries with custom slot names automatically get correct behavior via geometry lookup.

### D7: Output as PNG (Always)

**Decision:** Background removal always outputs PNG, regardless of input format.

**Rationale:** PNG is the only commonly-supported lossless format with alpha channels. JPEG doesn't support alpha. WebP supports alpha but PNG is more predictable across Three.js browser versions.

### D8: Chroma Key Algorithm via Sharp

**Decision:** The chroma key removal pipeline:

1. Read the image into raw RGBA buffer via Sharp (`sharp(input).ensureAlpha().raw()`).
2. Parse the target color hex to RGB.
3. For each pixel, compute Euclidean distance in RGB space: `d = sqrt((r-tr)² + (g-tg)² + (b-tb)²)`.
4. If `d <= threshold`: set alpha to 0 (fully transparent). Else: alpha remains 255.
5. Extract the alpha channel as a separate single-channel buffer.
6. If `feather > 0`: apply Sharp's `blur(feather)` to the alpha channel. This is a Gaussian blur with sigma = `feather`, operating on the alpha channel only.
7. Recombine the RGB channels with the blurred alpha channel.
8. Write the result as PNG via Sharp.

**Rationale:** Sharp's native `blur()` provides a well-defined Gaussian kernel. Applying it to the alpha channel after the binary threshold creates a smooth feathered edge. This avoids mixing color-distance and pixel-radius concepts — the threshold operates in color space, the feather operates in pixel space, and they are cleanly separated.

### D9: rembg Subprocess Protocol

**Decision:** rembg is invoked as:
```
<pythonPath> -m rembg i -m <model> <inputPath> <outputPath>
```
Via Node.js `child_process.execFile()` (not `exec()`). Timeout via `execFile`'s `timeout` option. Stderr captured for error reporting.

**Rationale:** `rembg i` CLI is the simplest interface — file in, file out. `execFile` is safer than `exec` (no shell injection) and provides built-in timeout.

### D10: `sharp` as an npm Dependency

**Decision:** The module depends on `sharp` (MIT licensed) for image metadata inspection and chroma key processing.

**Rationale:** Sharp is MIT licensed (C-01 compliant), widely used, and provides fast native-code image decoding and metadata reading. Both `imageHasAlpha` and the chroma key pipeline use it. The `metadata()`, `hasAlpha`, and `channels` APIs have been stable across all Sharp 0.3x releases.

### D11: No-Copy Passthrough for Already-Alpha Images

**Decision:** When an image already has alpha (or the slot doesn't need removal), `removeBackground()` returns `outputPath = inputPath`. No file copy, symlink, or I/O occurs.

**Rationale:** Copying a file just to produce a different path is wasteful. The caller (OBJ-057) needs a path to put in the manifest — the original path works. This also makes the operation idempotent: running removal on an already-processed `_removed.png` file detects it has alpha and returns the same path unchanged.

### D12: Output Basename Convention

**Decision:** "Basename" means the filename without its final extension. The output extension is always `.png`.

Examples:
- `subject.jpg` → `subject_removed.png`
- `my.image.webp` → `my.image_removed.png`
- `photo.png` → `photo_removed.png`

When `outputDir` is set: the output is placed in that directory. When `options.outputPath` is set: that exact path is used (must end with `.png`). Otherwise: output is alongside the input.

## Acceptance Criteria

- [ ] **AC-01:** `src/pipeline/background-removal.ts` exports `createBackgroundRemover`, `isRembgAvailable`, `SLOT_REMOVAL_POLICY`, and all associated types (`RemovalStrategy`, `BackgroundRemovalConfig`, `ChromaKeyConfig`, `RemovalOptions`, `RemovalResult`, `BatchRemovalEntry`, `BatchRemovalResult`, `BackgroundRemover`, `ResolvedBackgroundRemovalConfig`).

- [ ] **AC-02:** `src/pipeline/alpha-check.ts` exports `imageHasAlpha`.

- [ ] **AC-03:** `isRembgAvailable()` returns `true` on a system with Python and rembg installed, and `false` on a system without them. The result is cached — calling it twice does not spawn two subprocesses.

- [ ] **AC-04:** `removeBackground()` on a JPEG image (no alpha) with strategy `'rembg'` produces a PNG output file with an alpha channel. The output file exists at the expected path. `strategyUsed` is `'rembg'`. `durationMs` is populated.

- [ ] **AC-05:** `removeBackground()` on a JPEG image with strategy `'chroma_key'` and a white background produces a PNG output file where formerly-white regions are transparent. `strategyUsed` is `'chroma_key'`.

- [ ] **AC-06:** `removeBackground()` on a PNG image that already has alpha returns `strategyUsed: 'none'`, `inputHadAlpha: true`, and `outputPath === inputPath`. No new file is created.

- [ ] **AC-07:** `removeBackground()` with strategy `'auto'` uses `'rembg'` when rembg is available, and `'chroma_key'` when it is not.

- [ ] **AC-08:** `removeBackground()` on a non-existent file throws with message containing `"input file not found"`.

- [ ] **AC-09:** `removeBackground()` with strategy `'rembg'` when rembg is not installed throws with message containing `"rembg is not available"`.

- [ ] **AC-10:** `removeBackground()` with rembg that exceeds the timeout throws with message containing `"timed out"`.

- [ ] **AC-11:** rembg subprocess completes in under 5 seconds per image for a typical 1024×1024 image on a 4-core machine (TC-12).

- [ ] **AC-12:** `batchRemoveBackgrounds()` with `continueOnError: false` rejects on the first failure. Successfully processed images prior to the failure remain on disk.

- [ ] **AC-13:** `batchRemoveBackgrounds()` with `continueOnError: true` processes all images, collecting failures in `errors`. `failedCount` and `errors` reflect the failures.

- [ ] **AC-14:** `processImagesForManifest()` with a `geometryLookup` that returns `false` for a slot: skips removal for that slot. Entry appears in results with `strategyUsed: 'none'`.

- [ ] **AC-15:** `processImagesForManifest()` with a `geometryLookup` that returns `true` for a slot: applies removal to that slot's image.

- [ ] **AC-16:** `processImagesForManifest()` without `geometryLookup` falls back to `SLOT_REMOVAL_POLICY`. Slot name `'subject'` → processed. Slot name `'sky'` → skipped.

- [ ] **AC-17:** `processImagesForManifest()` with a slot name not in `SLOT_REMOVAL_POLICY` and no `geometryLookup` (or lookup returns `undefined`): defaults to no removal. Info logged mentioning the unknown slot name.

- [ ] **AC-18:** All output images from removal (rembg or chroma key) are valid PNG files with 4 channels (RGBA), verifiable via Sharp metadata.

- [ ] **AC-19:** The chroma key strategy with default settings (white, threshold 30) removes a solid white background from a test image, producing transparent regions where white was.

- [ ] **AC-20:** The chroma key strategy with a custom color (e.g., `'#00FF00'` green screen) removes that color.

- [ ] **AC-21:** `imageHasAlpha()` returns `true` for a PNG with alpha channel and `false` for a JPEG.

- [ ] **AC-22:** No module in `src/engine/` imports from `src/pipeline/`. (AP-04 enforcement.)

- [ ] **AC-23:** The rembg subprocess is invoked via `execFile` (not `exec`), preventing shell injection.

- [ ] **AC-24:** Output file paths follow the convention: basename is filename without final extension, suffix is `_removed`, extension is always `.png`. E.g., `subject.jpg` → `subject_removed.png`. When `outputDir` is set, output goes to that directory. When `options.outputPath` is set, that exact path is used.

- [ ] **AC-25:** `getConfig()` returns a `ResolvedBackgroundRemovalConfig` with all defaults applied. A remover created with `createBackgroundRemover()` (no args) returns `{ defaultStrategy: 'auto', pythonPath: 'python3', rembgModel: 'u2net', rembgTimeout: 30000, outputDir: undefined, chromaKey: { color: '#FFFFFF', threshold: 30, feather: 1 } }`.

- [ ] **AC-26:** `batchRemoveBackgrounds([])` resolves with a `BatchRemovalResult` where `results` is empty, `processedCount` is 0, `skippedCount` is 0, `failedCount` is 0, and `totalDurationMs` is approximately 0.

- [ ] **AC-27:** Chroma key with `feather: 0` produces hard-edged alpha (no blur). With `feather: 2`, the alpha channel boundary is visibly softer than with `feather: 0`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Input file doesn't exist | Throws: `"Background removal failed: input file not found: '{path}'"` |
| Input is unsupported format (e.g., .bmp, .tiff) | Throws: `"Background removal failed: unsupported format '{ext}' for '{path}'. Supported: png, jpg, jpeg, webp"` |
| Input already has alpha | Returns `strategyUsed: 'none'`, `inputHadAlpha: true`, `outputPath === inputPath`. No file I/O. |
| Strategy `'rembg'` but rembg not installed | Throws: `"Background removal failed: rembg is not available. Install with: pip install rembg[cpu]"` |
| Strategy `'auto'` and rembg not installed | Falls back to `'chroma_key'` silently. `strategyUsed: 'chroma_key'`. |
| rembg subprocess times out | Kills subprocess, throws: `"Background removal failed: rembg timed out after {ms}ms for '{path}'"` |
| rembg subprocess exits with non-zero code | Throws with stderr: `"Background removal failed: rembg exited with code {code} for '{path}': {stderr}"` |
| rembg subprocess produces empty/missing output file | Throws: `"Background removal failed: rembg produced no output for '{path}'"` |
| Sharp chroma key on image with no matching pixels | Output has no transparent pixels — image exported as PNG with alpha channel (all 255). Not an error. |
| Chroma key threshold 0 | Only exact color matches removed (very strict). |
| Chroma key threshold 255 | Virtually all pixels become transparent. Not an error (caller's choice). |
| Output directory doesn't exist | Create it recursively (`fs.mkdir` with `recursive: true`) before writing. |
| Input and output path are the same (via explicit outputPath) | Output overwrites input. No special handling. |
| Corrupt/truncated input image | Sharp metadata read fails. Throws: `"Background removal failed: cannot read image '{path}': {message}"` |
| Very large image (e.g., 8000x6000) | rembg may take longer. Timeout protects against indefinite hangs. Sharp handles large images natively. |
| Batch with empty array | Returns `BatchRemovalResult` with all counts 0, empty results array. |
| `processImagesForManifest` with unknown slot name, no geometry lookup | Defaults to no removal. Info logged: `"Unknown slot '{name}', skipping background removal."` |
| `processImagesForManifest` with unknown slot name, geometry lookup returns `undefined` | Same — falls through to SLOT_REMOVAL_POLICY, then default. |
| Python path is wrong (e.g., `'python4'`) | `isRembgAvailable()` returns false. `'rembg'` strategy → throws. `'auto'` → falls back to chroma key. |
| rembg installed but model not downloaded | rembg downloads model on first use. Default 30s timeout accommodates this. |
| Input is a previously processed `_removed.png` with alpha | Detected as having alpha → `strategyUsed: 'none'`, `outputPath === inputPath`. Idempotent. |
| `options.outputPath` doesn't end with `.png` | Throws: `"Background removal failed: outputPath must end with '.png', got '{path}'"` |

## Test Strategy

### Unit Tests (Mock Sharp and child_process)

1. **SLOT_REMOVAL_POLICY value tests:**
   - `SLOT_REMOVAL_POLICY['subject']` is `true`.
   - `SLOT_REMOVAL_POLICY['sky']` is `false`.
   - `SLOT_REMOVAL_POLICY['floor']` is `false`.
   - `SLOT_REMOVAL_POLICY['near_fg']` is `true`.

2. **Strategy resolution tests (mock `isRembgAvailable`):**
   - `'auto'` + rembg available → resolves to `'rembg'`.
   - `'auto'` + rembg unavailable → resolves to `'chroma_key'`.
   - Explicit `'rembg'` + rembg unavailable → throws.
   - Explicit `'none'` → passthrough.

3. **Config defaults:**
   - `createBackgroundRemover()` with no args → `getConfig()` returns expected defaults.

4. **Output path generation:**
   - No outputDir, no outputPath: `subject.jpg` → `<dir>/subject_removed.png`.
   - With outputDir `/tmp/out`: → `/tmp/out/subject_removed.png`.
   - With explicit outputPath `/tmp/out/custom.png` → exact path.
   - Multi-dot filename: `my.image.webp` → `my.image_removed.png`.

5. **processImagesForManifest decision precedence (mock removeBackground):**
   - geometryLookup returns `true` → removal applied.
   - geometryLookup returns `false` → skipped.
   - geometryLookup returns `undefined` for slot, slot in SLOT_REMOVAL_POLICY → uses policy.
   - No geometryLookup, slot in policy → uses policy.
   - No geometryLookup, slot not in policy → defaults to no removal, info logged.

### Integration Tests (Require Sharp, test images on disk)

Test images needed:
- `test_opaque.jpg` — JPEG, no alpha.
- `test_opaque.png` — PNG, no alpha.
- `test_alpha.png` — PNG with transparent background.
- `test_white_bg.png` — PNG with solid white background (for chroma key).
- `test_green_bg.png` — PNG with green (#00FF00) background.

6. **`imageHasAlpha` tests:**
   - JPEG → false.
   - Opaque PNG → false (Sharp reports channels=3 or hasAlpha=false).
   - Transparent PNG → true.

7. **Chroma key removal tests:**
   - White bg image + default settings → output PNG has alpha, white regions transparent.
   - Green bg image + color `'#00FF00'` → output PNG has alpha, green regions transparent.
   - Feather 0 → hard alpha edges.
   - Feather 2 → softer alpha edges (verify alpha values between 0 and 255 exist at boundaries).

8. **Alpha pre-check passthrough:**
   - Image with alpha → `strategyUsed: 'none'`, `outputPath === inputPath`, no new file created.

9. **Output file validation:**
   - All removal outputs are valid PNG with 4 channels (Sharp metadata check).

10. **Error condition tests:**
    - Non-existent file → expected error.
    - Unsupported format `.bmp` → expected error.
    - outputPath not ending `.png` → expected error.

11. **Batch tests:**
    - Batch of 3 images → results array length 3, ordered correctly.
    - `processedCount` + `skippedCount` = total entries (when no errors).
    - Empty batch → empty results, all counts 0.

12. **Batch error handling:**
    - Batch with one bad file, continueOnError=true → errors collected, others processed.
    - Batch with one bad file, continueOnError=false → rejects on failure.

### Integration Tests (Require Python + rembg — conditional)

These skip if rembg is not installed. Tagged `@requires-rembg`.

13. **`isRembgAvailable` tests:**
    - Returns true with valid Python + rembg.
    - Returns false with invalid pythonPath.
    - Result is cached (verify via mock or spy).

14. **rembg removal test:**
    - Subject with white bg → output has alpha, subject preserved.
    - `durationMs < 5000` (TC-12).

15. **rembg timeout test:**
    - Timeout 1ms → throws timeout error.

16. **rembg error test:**
    - Corrupt file → throws with stderr content.

### processImagesForManifest Integration Tests

17. **Geometry lookup precedence:**
    - Geometry says `transparent: true` for a slot that SLOT_REMOVAL_POLICY says `false` → removal IS applied (geometry wins).
    - Geometry says `transparent: false` for `subject` slot → removal is NOT applied (geometry wins over policy).

18. **End-to-end manifest processing:**
    - Mixed entries: 2 subjects (need removal), 3 backgrounds (skip) → `processedCount: 2`, `skippedCount: 3`.

### Relevant Testable Claims

- **TC-12:** rembg as subprocess under 5 seconds per image, acceptable mask quality. Directly tested by integration test #14.
- **OQ-02:** Best strategy for images without alpha. Resolved by this module's two-strategy approach with geometry-aware slot routing.
- **C-09:** Image format tolerance. This module ensures the engine receives images with correct alpha when needed.

## Integration Points

### Depends on

| Dependency | What OBJ-052 uses |
|---|---|
| **OBJ-015** (Texture loader) | Progress map dependency. The practical connection is conceptual: both modules deal with alpha detection, and OBJ-052's output (images with alpha) feeds into the browser where OBJ-015 loads them. OBJ-052 does NOT import any code from OBJ-015. The alpha detection methods are intentionally different — OBJ-052 uses Sharp's format-level `metadata.hasAlpha` as a cheap pre-filter; OBJ-015 uses pixel sampling (alpha < 250) as the authoritative render-time check. See OQ-D for why this discrepancy is acceptable. |
| **OBJ-005** (Scene geometry types) | Conceptual dependency (not in progress map `depends_on`). OBJ-052's `geometryLookup` callback reads `PlaneSlot.transparent` from OBJ-005's data. OBJ-052 does not directly import OBJ-005 types — the callback abstracts the access. The caller (OBJ-057) bridges the two by providing the lookup function. |

### Consumed by

| Downstream | How it uses OBJ-052 |
|---|---|
| **OBJ-057** (Asset orchestration pipeline) | Calls `createBackgroundRemover()` and `processImagesForManifest()` as part of asset preparation (Appendix A, between steps 4 and 5). Provides a `geometryLookup` callback that reads from the geometry registry (OBJ-005). Uses `BatchRemovalResult.results[i].outputPath` to rewrite manifest image URLs before passing the manifest to the rendering engine. |

### File Placement

```
depthkit/
  src/
    pipeline/                        # NEW directory — asset pipeline utilities (per AP-04)
      background-removal.ts          # NEW — createBackgroundRemover, isRembgAvailable,
                                     #        SLOT_REMOVAL_POLICY, all types
      alpha-check.ts                 # NEW — imageHasAlpha utility
```

### npm Dependencies

| Package | Version | License | Purpose |
|---|---|---|---|
| `sharp` | ^0.33.x | MIT | Image metadata reading, chroma key pixel processing. `metadata()`, `hasAlpha`, `channels`, `raw()`, `blur()`, `ensureAlpha()` — all stable APIs across 0.3x releases. |

`sharp` is added to `package.json` `dependencies`. No Python packages are added — rembg is a system-level dependency detected at runtime.

## Open Questions

### OQ-A: Should rembg use a persistent subprocess for batch processing?

Currently each `removeBackground()` call spawns a new subprocess, reloading the U²-Net model (~170MB) each time. A persistent subprocess would amortize model load time but requires a custom Python wrapper script and lifecycle management.

**Recommendation:** Defer for V1. Per-image subprocess meets TC-12 targets. Revisit if batch performance becomes a bottleneck.

### OQ-B: Should the chroma key support multiple target colors per image?

**Recommendation:** Defer. Single-color + threshold covers the majority case. For gradient backgrounds, rembg is the better tool.

### OQ-C: Should `imageHasAlpha` use pixel-level sampling like OBJ-015?

**Recommendation:** No. Keep them at different fidelity levels for different purposes. OBJ-052's format-level check is a cheap pre-filter for the asset pipeline. OBJ-015's pixel-level check is the authoritative render-time determination. The worst case of the discrepancy (4-channel image with all-opaque pixels skipped by OBJ-052) is benign — OBJ-015 later warns at render time. See D5.

---

I believe this revision addresses all 12 issues raised by the challenger. The key changes are:

1. **Issue 1:** Inverted precedence — geometry lookup is now primary, SLOT_REMOVAL_POLICY is fallback. D6 fully rewritten.
2. **Issue 2:** Replaced `slotType` with `slotName` throughout. `processImagesForManifest` entries now carry `slotName` + optional `geometryName`.
3. **Issue 3:** Removed `TextureSlotWarning` import entirely.
4. **Issue 4:** D12 added with explicit basename convention and examples.
5. **Issue 5:** D8 rewritten with clear two-phase algorithm: binary threshold in color space, then Gaussian blur in pixel space via Sharp's `blur()`. AC-27 added to test feathering.
6. **Issue 6:** AC-25 added for `getConfig()`. Added `ResolvedBackgroundRemovalConfig` type.
7. **Issue 7:** Depends-on section rewritten honestly. OBJ-005 added as conceptual dependency.
8. **Issue 8:** AC-26 added for empty batch.
9. **Issue 9:** D11 added. `outputPath = inputPath` for passthrough. AC-06 updated. No file I/O.
10. **Issue 10:** `failedCount` and `errors` are always present on `BatchRemovalResult` (defaulting to 0 and `{}`).
11. **Issue 11:** Edge case table includes idempotency row.
12. **Issue 12:** Sharp API stability note added in npm dependencies table.

Challenger, please verify these changes address all your concerns.

---

## Round 4 — spec_challenger

I've carefully verified all 12 issues against the revised spec. Every major and minor issue has been structurally addressed in the revision. Let me do a final check before converging.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Write,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]
You've hit your limit · resets 1am (America/New_York)

---

## Round 5 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 6 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 7 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 8 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 9 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 10 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 11 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 12 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 13 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 14 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 15 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 16 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 17 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 18 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 19 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 20 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 21 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 22 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 23 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 24 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 25 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 26 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 27 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 28 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 29 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 30 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 31 — spec_challenger

You've hit your limit · resets 1am (America/New_York)
