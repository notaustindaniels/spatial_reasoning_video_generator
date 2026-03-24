# Specification: OBJ-069 — Edge Reveal Systematic Validation

## Summary

OBJ-069 defines the **systematic edge-reveal validation harness** for depthkit: a test module and runner that enumerates every bidirectionally-compatible geometry+camera pair across the implemented registries, runs both analytical (OBJ-041) and sampling-based (OBJ-040) edge-reveal checks at standard aspect ratios and speed ranges, produces a structured report, and — where failures are found — computes and documents the minimum plane size adjustments required. For rotated planes (which OBJ-040 skips), the harness generates test render manifests for Director Agent visual review via OBJ-035. This objective addresses TC-03 (perspective projection produces convincing 2.5D) by validating that the spatial authoring vocabulary never reveals plane edges during normal use.

## Interface Contract

### Validation Harness Module

```typescript
// src/validation/edge-reveal-harness.ts

import type { GeometryRegistry, SceneGeometry } from '../scenes/geometries/types';
import type { CameraPathRegistry, CameraPathPreset, CameraParams } from '../camera/types';
import type {
  GeometryEdgeRevealReport,
  PlaneEdgeRevealResult,
} from '../spatial/edge-reveal';
import type {
  OversizingCheckResult,
  SpatialValidationError,
} from './spatial-compatibility';
import type { Size2D, Vec3 } from '../spatial/types';
import type { Manifest } from '../manifest/schema';

// ────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────

/**
 * Configuration for a single validation run.
 */
export interface EdgeRevealHarnessConfig {
  /** The geometry registry to validate. */
  geometryRegistry: Readonly<GeometryRegistry>;

  /** The camera path registry to validate. */
  cameraRegistry: Readonly<CameraPathRegistry>;

  /**
   * Aspect ratios to test. Each pair is validated at every listed
   * aspect ratio. Default: [16/9, 9/16] per C-04.
   */
  aspectRatios?: number[];

  /**
   * Speed values to test for each pair. Default: [0.5, 1.0, 1.5].
   * speed=1.0 is the standard. speed=0.5 is conservative.
   * speed=1.5 tests moderate aggression without going extreme.
   */
  speeds?: number[];

  /**
   * Offset values to test. Each pair is tested with each offset.
   * Default: [[0, 0, 0]] (no offset).
   * To test offset sensitivity, add entries like [2, 0, 0].
   */
  offsets?: Vec3[];

  /**
   * Number of sample points for OBJ-040's trajectory sampling.
   * Default: 100 (matches OBJ-040 default).
   */
  sampleCount?: number;

  /**
   * If true, only validate bidirectionally compatible pairs.
   * If false, also attempt pairs where only one side declares
   * compatibility (to detect whether the exclusion is warranted).
   * Default: true.
   */
  compatibleOnly?: boolean;
}

// ────────────────────────────────────────────
// Results
// ────────────────────────────────────────────

/**
 * Result for a single geometry+camera+params combination.
 */
export interface PairValidationResult {
  /** Geometry name. */
  geometryName: string;

  /** Camera path preset name. */
  cameraName: string;

  /** The speed value used for this test. */
  speed: number;

  /** The offset used for this test. */
  offset: Vec3;

  /** The aspect ratio used for this test. */
  aspectRatio: number;

  /** Human-readable aspect ratio label (e.g., '16:9', '9:16'). */
  aspectRatioLabel: string;

  /**
   * OBJ-040 sampling-based report for facing-camera planes.
   * Null if validateGeometryEdgeReveal was not called (e.g.,
   * the pair is not bidirectionally compatible and
   * compatibleOnly is true).
   */
  samplingReport: GeometryEdgeRevealReport | null;

  /**
   * OBJ-041 analytical oversizing check for ALL planes
   * (including rotated).
   */
  oversizingResults: OversizingCheckResult[];

  /**
   * Overall pass/fail for this combination.
   * true only when ALL of the following hold:
   *
   * 1. All facing-camera planes pass OBJ-040 sampling (safe: true).
   *    OBJ-041 failures for facing-camera planes that pass OBJ-040
   *    are non-blocking — logged as notes, not failures. OBJ-040
   *    is authoritative for facing-camera planes (see D2/D4).
   *
   * 2. All rotated axis-aligned planes (floor, ceiling, walls) pass
   *    OBJ-041 oversizing (sufficient: true).
   *
   * 3. No plane has cameraPassesThrough: true (from either check).
   *
   * 4. Non-axis-aligned planes (skippedNonAxisAligned in OBJ-041,
   *    skipped in OBJ-040) do not affect pass — they produce
   *    SkippedSlot entries for visual review instead.
   */
  pass: boolean;

  /**
   * Slot names that failed, with failure details.
   * Empty if pass is true.
   *
   * A facing-camera plane that passes OBJ-040 sampling but fails
   * OBJ-041 analytical does NOT appear here (OBJ-040 takes
   * precedence). Such cases are logged in the report's notes but
   * do not constitute failures.
   */
  failures: SlotFailure[];

  /**
   * Slot names that were skipped (rotated planes in OBJ-040,
   * non-axis-aligned in OBJ-041). These require visual review.
   */
  skippedSlots: SkippedSlot[];
}

/**
 * Details about a single slot failure.
 */
export interface SlotFailure {
  /** Slot name that failed. */
  slotName: string;

  /**
   * Which check failed:
   * - 'sampling': OBJ-040 sampling failed (facing-camera plane).
   * - 'oversizing': OBJ-041 analytical failed. This includes
   *   cases where OBJ-040 skipped the plane (rotated) and only
   *   OBJ-041 was applicable.
   * - 'both': Both OBJ-040 sampling AND OBJ-041 analytical
   *   failed for a facing-camera plane.
   */
  failedCheck: 'sampling' | 'oversizing' | 'both';

  /**
   * The worst margin from OBJ-040 sampling (if applicable).
   * Negative value = how many world units the plane is undersized.
   * -Infinity if camera passes through the plane.
   * Null if OBJ-040 did not validate this slot (rotated plane).
   */
  worstMargin: number | null;

  /**
   * The t value (normalized time) at which the worst edge reveal
   * occurs. Null if not a sampling failure.
   */
  worstT: number | null;

  /**
   * Current plane size from geometry definition.
   */
  currentSize: Size2D;

  /**
   * Minimum safe size computed by OBJ-040's
   * computeMinimumFacingPlaneSize (for facing-camera planes only).
   * Null for rotated planes (OBJ-040 does not apply) and for
   * camera-passes-through cases (structural, not sizing issue).
   */
  minimumSafeSize: Size2D | null;

  /**
   * Recommended adjusted size with 1.05 safety margin:
   * - For facing-camera planes: minimumSafeSize * 1.05.
   * - For rotated planes: OBJ-041's requiredSize * 1.05.
   * - Null only for camera-passes-through cases (structural
   *   incompatibility — no size adjustment can fix it).
   */
  recommendedSize: Size2D | null;

  /**
   * Whether the camera passes through or behind this plane.
   * True if OBJ-041 reports cameraPassesThrough: true for this
   * slot, OR if OBJ-040 sampling finds any sample point where
   * the view-axis distance to the plane is <= 0.
   */
  cameraPassesThrough: boolean;

  /** Human-readable description of the failure and recommended fix. */
  message: string;
}

/**
 * A slot that was skipped by automated validation and requires
 * visual review via the Director Agent workflow.
 */
export interface SkippedSlot {
  /** Slot name. */
  slotName: string;

  /** Why it was skipped (from OBJ-040's skipReason or OBJ-041's
   *  skippedNonAxisAligned). */
  reason: string;

  /**
   * Whether OBJ-041's axis-aligned oversizing check passed for
   * this slot (if applicable). true = analytical check passed,
   * but visual confirmation still recommended. false = analytical
   * check also failed. null = slot was non-axis-aligned, no
   * analytical check was possible.
   */
  analyticalCheckPassed: boolean | null;
}

/**
 * Complete harness report across all tested combinations.
 */
export interface EdgeRevealHarnessReport {
  /** Timestamp of the validation run. */
  timestamp: string;

  /**
   * Registry consistency errors from OBJ-041's
   * validateRegistryConsistency(). Empty if registries are
   * fully consistent. Non-empty entries indicate mismatches
   * between geometry and camera compatibility declarations
   * (e.g., geometry lists a camera that doesn't list the
   * geometry back). These are informational — the harness
   * proceeds with consistent pairs regardless.
   */
  registryConsistencyErrors: SpatialValidationError[];

  /** Total number of geometry+camera pairs tested. */
  totalPairsTested: number;

  /** Number of pairs that passed all checks at all tested params. */
  totalPairsPassed: number;

  /** Number of pairs that failed at least one check. */
  totalPairsFailed: number;

  /** Number of individual param combinations tested. */
  totalCombinationsTested: number;

  /** Number of individual combinations that passed. */
  totalCombinationsPassed: number;

  /**
   * Per-pair results, grouped by geometry+camera.
   * Key: `${geometryName}::${cameraName}`
   */
  pairs: Record<string, PairSummary>;

  /**
   * Slots across ALL pairs that require visual review
   * (rotated planes skipped by OBJ-040).
   * Deduplicated by geometry+slot name.
   */
  visualReviewRequired: VisualReviewItem[];

  /**
   * Size adjustments recommended to fix all failures.
   * Keyed by geometry name, then slot name.
   * The recommended size is the maximum across all failing
   * combinations — fixing to this size resolves all failures.
   */
  recommendedAdjustments: Record<string, Record<string, SizeAdjustment>>;
}

/**
 * Summary for a single geometry+camera pair across all tested
 * param combinations.
 */
export interface PairSummary {
  geometryName: string;
  cameraName: string;

  /** Whether ALL param combinations passed. */
  allPassed: boolean;

  /** Individual results per param combination. */
  results: PairValidationResult[];
}

/**
 * A slot in a specific geometry that needs visual review.
 */
export interface VisualReviewItem {
  geometryName: string;
  slotName: string;
  reason: string;
  /** Camera paths that interact with this slot. */
  relevantCameras: string[];
  analyticalCheckPassed: boolean | null;
}

/**
 * A recommended size adjustment for a slot in a geometry.
 */
export interface SizeAdjustment {
  slotName: string;
  currentSize: Size2D;
  /** The minimum size across all failing combinations, with
   *  1.05 safety margin applied. */
  recommendedSize: Size2D;
  /** Which camera+params combinations triggered this adjustment. */
  triggeringCombinations: string[];
}

// ────────────────────────────────────────────
// Harness Functions
// ────────────────────────────────────────────

/**
 * Runs the complete edge-reveal validation harness.
 *
 * **Config validation:** The harness validates its config at entry
 * before any pair is tested. All values in `speeds` must be > 0,
 * all values in `aspectRatios` must be > 0, and `sampleCount`
 * must be >= 1. Invalid config throws RangeError immediately.
 *
 * Algorithm:
 * 1. Validate config. Throw RangeError on invalid values.
 * 2. Run OBJ-041's validateRegistryConsistency(). Store results
 *    in report.registryConsistencyErrors. Proceed regardless.
 * 3. Enumerate all geometry+camera pairs using OBJ-041's
 *    analyzeCoverage(). Filter to bidirectionally compatible
 *    pairs (or all pairs if compatibleOnly is false).
 * 4. For each pair, for each (aspectRatio, speed, offset) combo:
 *    a. Run OBJ-040's validateGeometryEdgeReveal() for
 *       sampling-based facing-camera validation.
 *    b. Run OBJ-041's checkOversizingSufficiency() for
 *       analytical all-plane validation.
 *    c. Apply the precedence rule (D2/D4): for facing-camera
 *       planes, OBJ-040 sampling is authoritative. OBJ-041
 *       failures on facing-camera planes that pass OBJ-040
 *       are logged as notes, not failures.
 *    d. For facing-camera slots that fail OBJ-040, compute
 *       minimumSafeSize via OBJ-040's
 *       computeMinimumFacingPlaneSize().
 *    e. For rotated axis-aligned slots that fail OBJ-041,
 *       set recommendedSize to OBJ-041's requiredSize * 1.05.
 *       minimumSafeSize is null (OBJ-040 does not apply).
 *    f. Record results.
 * 5. Aggregate: compute per-pair summaries, deduplicate visual
 *    review items, compute maximum recommended sizes.
 * 6. Return EdgeRevealHarnessReport.
 *
 * @param config - Harness configuration.
 * @returns Complete report.
 * @throws RangeError if config contains invalid values (speed <= 0,
 *         aspectRatio <= 0, sampleCount < 1).
 */
export function runEdgeRevealHarness(
  config: EdgeRevealHarnessConfig
): EdgeRevealHarnessReport;

/**
 * Formats the harness report as a human-readable Markdown document.
 *
 * Includes:
 * - Executive summary (pass/fail counts)
 * - Registry consistency errors (if any)
 * - Per-pair results table
 * - Failure details with recommended fixes
 * - Visual review checklist for rotated planes
 * - Recommended geometry size adjustments
 *
 * @param report - The harness report to format.
 * @returns Markdown string.
 */
export function formatEdgeRevealReport(
  report: EdgeRevealHarnessReport
): string;

/**
 * Generates a minimal test manifest for visual review of a
 * specific geometry+camera pair. The manifest uses solid-color
 * placeholder images (generated as data: URIs) so that edge
 * reveals are maximally visible (bright colors on a black
 * background reveal edges instantly).
 *
 * The generated manifest is suitable for rendering via OBJ-035's
 * Orchestrator to produce a short test clip for Director Agent
 * review.
 *
 * The returned Manifest conforms to OBJ-004's schema. It includes
 * ALL slots defined by the geometry (both required and optional)
 * to test full edge-reveal coverage.
 *
 * @param geometryName - The geometry to test.
 * @param cameraName - The camera path to test.
 * @param geometry - The full SceneGeometry definition.
 * @param cameraPreset - The full CameraPathPreset definition.
 * @param options - Optional overrides.
 * @returns A valid Manifest object ready for rendering.
 */
export function generateTestManifest(
  geometryName: string,
  cameraName: string,
  geometry: SceneGeometry,
  cameraPreset: CameraPathPreset,
  options?: {
    /** Duration in seconds. Default: 5. */
    duration?: number;
    /** FPS. Default: 30. */
    fps?: number;
    /** Width. Default: 1920. */
    width?: number;
    /** Height. Default: 1080. */
    height?: number;
    /** Camera speed. Default: 1.0. */
    speed?: number;
    /** Camera offset. Default: [0,0,0]. */
    offset?: Vec3;
  }
): Manifest;
```

### Module Exports

```typescript
// src/validation/edge-reveal-harness.ts exports
export type {
  EdgeRevealHarnessConfig,
  PairValidationResult,
  SlotFailure,
  SkippedSlot,
  EdgeRevealHarnessReport,
  PairSummary,
  VisualReviewItem,
  SizeAdjustment,
};
export {
  runEdgeRevealHarness,
  formatEdgeRevealReport,
  generateTestManifest,
};

// Re-exported from src/validation/index.ts
```

## Design Decisions

### D1: Harness Is a Synchronous Validation Module, Not a CLI Command

**Decision:** The harness is a pure function (`runEdgeRevealHarness`) that takes registries and configuration, returns a report object. It does NOT launch Puppeteer, render videos, or produce visual output. Visual review manifests are generated as data structures by `generateTestManifest()` — rendering them is the caller's responsibility.

**Rationale:** Separation of concerns per AP-04. The harness performs mathematical validation. The test runner (in `test/`) or a CLI script calls the harness, renders test manifests via OBJ-035 when needed, and orchestrates the Director Agent review cycle. This keeps the harness testable without heavyweight dependencies.

### D2: Dual Validation — OBJ-040 Sampling + OBJ-041 Analytical

**Decision:** Every pair is validated by BOTH OBJ-040's `validateGeometryEdgeReveal()` (sampling-based, facing-camera only) and OBJ-041's `checkOversizingSufficiency()` (analytical, all orientations). A pair passes only if both checks pass — with the precedence exception defined in D4.

**Rationale:** The two checks are complementary per OBJ-041 D9:
- OBJ-041 is conservative (symmetric envelope, may over-estimate) but covers rotated planes.
- OBJ-040 is precise (trajectory sampling) but only handles facing-camera planes.
- A pair that passes OBJ-041's analytical check but fails OBJ-040's sampling reveals that the analytical model was insufficient.
- A pair that passes OBJ-040 but fails OBJ-041 reveals that the analytical model is overly conservative (documented but not blocking for facing-camera planes — the sampling result is authoritative).

### D3: Default Parameter Matrix — Aspect Ratios x Speeds x Offsets

**Decision:** Default test matrix:
- Aspect ratios: `[16/9, 9/16]` — landscape and portrait per C-04.
- Speeds: `[0.5, 1.0, 1.5]` — conservative, standard, moderately aggressive.
- Offsets: `[[0, 0, 0]]` — no offset by default.

This produces 6 combinations per pair (2 aspects x 3 speeds x 1 offset). With N pairs, total combinations = 6N.

**Rationale:** Speed 2.0+ is extreme and likely to fail for close planes (OBJ-027 D2 shows subject at 5x apparent size change at speed=1.0). Testing speed=1.5 catches marginal cases. Speed=0.5 confirms that conservative use always works. Default offsets of [0,0,0] test the standard case; callers can add offset tests for specific debugging.

### D4: `pass` Criterion — OBJ-040 Authoritative for Facing-Camera, OBJ-041 Authoritative for Rotated

**Decision:** A `PairValidationResult.pass` is `true` when ALL of the following hold:

1. All **facing-camera** planes pass OBJ-040 sampling (`safe: true`). If OBJ-040 says safe but OBJ-041 says insufficient for the same facing-camera plane, the plane is treated as **passing** — OBJ-040's precise trajectory sampling is authoritative over OBJ-041's conservative symmetric envelope for facing-camera planes. The OBJ-041 discrepancy is logged as a note but does NOT appear in `failures` and does NOT affect `pass`.

2. All **rotated axis-aligned** planes (floor, ceiling, walls) pass OBJ-041 oversizing (`sufficient: true`). OBJ-040 skips these; OBJ-041 is the only automated check.

3. **No plane** has `cameraPassesThrough: true` from either check.

4. **Non-axis-aligned** planes (`skippedNonAxisAligned` in OBJ-041, skipped in OBJ-040) do NOT affect `pass`. They produce `SkippedSlot` entries for visual review.

**Rationale:** OBJ-040 samples the actual trajectory at 100 points — it knows precisely whether the plane covers the frustum at each moment. OBJ-041 uses worst-case symmetric displacement envelopes that intentionally over-estimate. For facing-camera planes where both run, the more precise check wins. For rotated planes where only OBJ-041 runs, it's the sole authority.

### D5: Minimum Safe Size Computation for Failures

**Decision:** When a facing-camera plane fails OBJ-040's sampling check, the harness calls `computeMinimumFacingPlaneSize()` from OBJ-040 to determine the exact minimum size, then applies a 1.05 safety margin (5%) as recommended by OBJ-040's JSDoc. The results are stored as `minimumSafeSize` and `recommendedSize` in the `SlotFailure`.

For rotated planes that fail OBJ-041's analytical check, `minimumSafeSize` is null — OBJ-040's `computeMinimumFacingPlaneSize` does not apply to rotated planes. `recommendedSize` is set to the `requiredSize` from `OversizingCheckResult` multiplied by 1.05. The `message` field describes the OBJ-041 failure and the required size.

For `cameraPassesThrough` failures (any orientation), both `minimumSafeSize` and `recommendedSize` are null — the problem is structural (camera trajectory intersects the plane), not a sizing issue.

**Rationale:** Geometry authors need actionable size adjustments, not just pass/fail. The 1.05 margin accounts for floating-point imprecision and frame-rate-dependent interpolation per OBJ-040's recommendation. Keeping `minimumSafeSize` null for rotated planes maintains semantic accuracy (it represents OBJ-040's output), while `recommendedSize` is always populated for fixable failures regardless of plane orientation.

### D6: Aggregated Recommended Adjustments

**Decision:** The harness report includes a `recommendedAdjustments` map that aggregates across all failing combinations. For each geometry+slot that fails at ANY tested combination, the recommended size is the maximum of all recommended sizes across all failing combinations for that slot.

**Rationale:** A geometry author wants a single size adjustment per slot that fixes ALL edge reveals across all compatible cameras, aspect ratios, and reasonable speeds. Taking the maximum ensures one fix resolves all failures.

### D7: Visual Review Checklist for Rotated Planes

**Decision:** Rotated planes (floor, ceiling, walls) that are skipped by OBJ-040's sampling are collected into a `visualReviewRequired` list. Each entry names the geometry, slot, reason for skipping, relevant camera paths, and whether OBJ-041's analytical check passed. This checklist drives the Director Agent visual review workflow.

**Rationale:** OBJ-040 D1 explicitly states that rotated planes are validated through the Director Agent tuning workflow. OBJ-069 generates the checklist; the actual visual review happens during OBJ-059-066 tuning rounds or as a follow-up.

### D8: Test Manifest Generation for Visual Review

**Decision:** `generateTestManifest()` produces a valid `Manifest` (per OBJ-004's type) with high-contrast placeholder images (e.g., bright red floor, bright green walls, bright blue backdrop on a black clear color) so edge reveals are instantly visible in a rendered clip. The manifest uses ALL of the geometry's slots (required and optional) with data URI images (solid-color PNGs) — no external asset files needed.

**Color assignment:** Slots are assigned visually distinct colors from a fixed palette. The palette is deterministic (same slot name always gets the same color) so repeated runs produce visually comparable results. Each slot must receive a unique color — no two slots in the same geometry may share a color.

**Rationale:** The Director Agent (or human reviewer) needs to see edge reveals clearly. Solid-color planes against a black background make any edge gap immediately obvious. Data URIs eliminate file dependencies for test rendering.

### D9: Report Format — Markdown for Human + Structured Object for Programmatic Use

**Decision:** The harness returns a structured `EdgeRevealHarnessReport` object. `formatEdgeRevealReport()` converts it to Markdown. The test suite uses the structured object for assertions; the CLI/development workflow uses the Markdown for human review.

### D10: Aspect Ratio Label Mapping

**Decision:** Common aspect ratios are labeled for readability: `16/9` -> `'16:9'`, `9/16` -> `'9:16'`, `4/3` -> `'4:3'`. Non-standard ratios use decimal notation (e.g., `'2.35:1'`). The label is purely cosmetic — all math uses the numeric ratio.

### D11: Compatibility Filtering via OBJ-041

**Decision:** The harness calls OBJ-041's `validateRegistryConsistency()` first. Results are stored in `report.registryConsistencyErrors`. If there are consistency errors, validation proceeds on consistent pairs regardless. Pair enumeration uses OBJ-041's `analyzeCoverage()` to get the compatibility matrix, then filters to bidirectionally compatible pairs (unless `compatibleOnly: false`).

**Rationale:** Reuses OBJ-041's existing analysis rather than reimplementing pair enumeration. The coverage analysis also feeds TC-08. Storing consistency errors in the report ensures they're visible without blocking validation.

## Acceptance Criteria

### Harness Execution

- [ ] **AC-01:** `runEdgeRevealHarness` with a registry containing the stage geometry (OBJ-018) and `slow_push_forward`/`slow_pull_back` (OBJ-027) camera presets produces a report with at least 2 pairs tested.
- [ ] **AC-02:** Each pair is tested at both 16:9 and 9:16 aspect ratios (default config), producing at least 6 `PairValidationResult` entries per pair (2 aspects x 3 speeds).
- [ ] **AC-03:** For a pair where all facing-camera planes are oversized sufficiently (e.g., stage + static camera at speed=1.0), `pass` is `true`.
- [ ] **AC-04:** For a pair where a facing-camera plane is deliberately undersized (e.g., a test geometry with a small backdrop), `pass` is `false`, and `failures` contains an entry for the undersized slot.
- [ ] **AC-05:** Failed facing-camera slots include `minimumSafeSize` (non-null) and `recommendedSize` (minimumSafeSize * 1.05).
- [ ] **AC-06:** Failed slots with `cameraPassesThrough: true` have `minimumSafeSize: null` and `recommendedSize: null`, with a message indicating the structural incompatibility.

### Config Validation

- [ ] **AC-07:** `runEdgeRevealHarness` with `speeds: [0]` throws `RangeError` before any pair is tested.
- [ ] **AC-08:** `runEdgeRevealHarness` with `aspectRatios: [-1]` throws `RangeError` before any pair is tested.
- [ ] **AC-09:** `runEdgeRevealHarness` with `sampleCount: 0` throws `RangeError` before any pair is tested.

### Dual Validation

- [ ] **AC-10:** Both `samplingReport` (OBJ-040) and `oversizingResults` (OBJ-041) are populated for each combination.
- [ ] **AC-11:** If OBJ-040 says a facing-camera plane is safe but OBJ-041 says it's insufficient, the pair is marked as `pass: true` (OBJ-040 takes precedence for facing-camera planes). The facing-camera plane does NOT appear in `failures`.
- [ ] **AC-12:** If OBJ-041 says a rotated axis-aligned plane is insufficient, the pair is marked as `pass: false` even if OBJ-040 skipped that plane. The rotated plane appears in `failures` with `failedCheck: 'oversizing'`.
- [ ] **AC-12a:** For a rotated axis-aligned plane that fails OBJ-041 oversizing, `SlotFailure.minimumSafeSize` is `null`, and `SlotFailure.recommendedSize` is OBJ-041's `requiredSize * 1.05` (non-null, actionable).

### Rotated Plane Handling

- [ ] **AC-13:** Rotated planes (floor, ceiling, walls) appear in `skippedSlots` with a non-empty `reason` from OBJ-040.
- [ ] **AC-14:** `visualReviewRequired` in the report contains deduplicated entries for all rotated plane slots across all tested pairs.
- [ ] **AC-15:** Each `VisualReviewItem` lists all camera paths that are compatible with that geometry.

### Report Aggregation

- [ ] **AC-16:** `recommendedAdjustments` contains entries only for slots that failed at least one combination.
- [ ] **AC-17:** When a slot fails at multiple speed/aspect combinations, `recommendedAdjustments` uses the maximum recommended size across all failures.
- [ ] **AC-18:** `totalPairsTested` counts unique geometry+camera pairs (not individual param combinations). `totalCombinationsTested` counts individual param combinations.
- [ ] **AC-19:** A pair is counted in `totalPairsPassed` only if ALL its param combinations passed.

### Report Formatting

- [ ] **AC-20:** `formatEdgeRevealReport` produces valid Markdown with: executive summary, registry consistency errors (if any), per-pair results table, failure details, visual review checklist, and recommended adjustments.
- [ ] **AC-21:** The Markdown report includes the harness run timestamp.

### Test Manifest Generation

- [ ] **AC-22:** `generateTestManifest` produces a `Manifest` object with the correct geometry name, camera name, and one plane entry per slot (both required and optional) in the geometry.
- [ ] **AC-23:** Generated manifests use data URI images (`data:image/png;base64,...`) for all planes — no external file dependencies.
- [ ] **AC-24:** Each slot in the generated manifest uses a distinct solid color so edge reveals per-plane are visually distinguishable.
- [ ] **AC-25:** The generated manifest passes OBJ-004 schema validation (structurally valid `Manifest`).

### Specific Geometry+Camera Validations (Stage + Push/Pull)

- [ ] **AC-26:** Stage geometry + `slow_push_forward` at speed=1.0, aspect=16:9: all facing-camera planes (sky, backdrop, midground, subject, near_fg) pass OBJ-040 sampling. This validates that OBJ-018's plane sizes are sufficient for OBJ-027's default Z displacement.
- [ ] **AC-27:** Stage geometry + `slow_pull_back` at speed=1.0, aspect=16:9: all facing-camera planes pass. `slow_pull_back` has `recommendedOversizeFactor=1.7` — this confirms the stage's plane sizes accommodate the retreat.
- [ ] **AC-28:** Stage geometry + `slow_push_forward` at speed=1.0, aspect=9:16 (portrait): all facing-camera planes pass. Portrait mode narrows the horizontal frustum — plane widths must still exceed visible width.
- [ ] **AC-29:** Stage geometry floor slot (rotated) appears in `skippedSlots` for OBJ-040 and in `visualReviewRequired`. OBJ-041's analytical check for the floor provides the `analyticalCheckPassed` value.

### Registry Consistency

- [ ] **AC-30:** Running `runEdgeRevealHarness` twice with the same config and registries produces identical reports (C-05).
- [ ] **AC-31:** When registries have bidirectional consistency errors (e.g., geometry lists camera X but camera X doesn't list geometry), `report.registryConsistencyErrors` contains the errors from `validateRegistryConsistency()`. The harness still validates all consistent pairs.
- [ ] **AC-32:** When registries are fully consistent, `report.registryConsistencyErrors` is an empty array.

## Edge Cases and Error Handling

### Registry Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty geometry registry | Report has 0 pairs tested. `registryConsistencyErrors` is empty. No errors thrown. |
| Empty camera registry | Report has 0 pairs tested. No errors thrown. |
| Geometry with no bidirectionally compatible cameras | Pair count is 0 for that geometry. If `compatibleOnly: false`, pairs are tested but noted as non-compatible. |
| Registry consistency errors (OBJ-041) | Stored in `report.registryConsistencyErrors`. Validation proceeds on consistent pairs. |

### Validation Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Camera path where camera passes through a facing-camera plane (e.g., high speed push through subject) | OBJ-040 returns `safe: false`, `worstMargin: -Infinity`. OBJ-041 returns `cameraPassesThrough: true`. `SlotFailure.cameraPassesThrough: true` (OR of both sources). `minimumSafeSize: null`, `recommendedSize: null`. Message recommends reducing speed or moving the plane. |
| Camera path where near_fg ends up behind camera at end position | OBJ-040 catches this at the sample point where distance <= 0. Reported as failure with `worstMargin: -Infinity`. |
| Plane exactly at the boundary of the camera's position envelope | OBJ-041 uses EPSILON=0.001 for distance. OBJ-040 catches with sampling. Both report marginal results. |
| All planes pass OBJ-040 but a rotated plane fails OBJ-041 | `pass: false` because OBJ-041 failure on axis-aligned rotated planes is authoritative. `SlotFailure.minimumSafeSize: null`, `SlotFailure.recommendedSize` is OBJ-041's `requiredSize * 1.05`. |
| Facing-camera plane passes OBJ-040 but fails OBJ-041 | `pass: true` for this plane (D4 precedence). Plane does NOT appear in `failures`. Discrepancy logged as note in report. |
| Non-axis-aligned rotation plane | OBJ-041 skips with `skippedNonAxisAligned: true`. OBJ-040 skips with rotation check. Both appear in `skippedSlots`. `pass` is not affected (benefit of the doubt). |

### Parameter Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `speeds` contains 0 | `runEdgeRevealHarness` throws `RangeError: "All speed values must be > 0"` at entry, before any pair is tested. |
| `speeds` contains negative value | Same `RangeError`. |
| `speeds` is empty array | No combinations tested. Report has 0 combinations. Not an error. |
| `aspectRatios` is empty | No combinations tested. Not an error. |
| `aspectRatios` contains 0 or negative | Throws `RangeError: "All aspectRatio values must be > 0"`. |
| `sampleCount` < 1 | Throws `RangeError: "sampleCount must be >= 1"`. |
| Very large speed (e.g., 10.0) | Valid. Many planes will fail. All failures reported with recommendations. |

### Test Manifest Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Geometry with only required slots | Manifest includes all slots (required and optional per D8). |
| Geometry with all optional slots | Manifest includes ALL slots (required and optional). |
| Geometry with 0 required slots | Manifest includes all optional slots. If no slots at all, manifest has empty `planes` record. |

## Test Strategy

### Unit Tests

**Harness logic tests (with mock registries):**

1. **Basic pair enumeration:** Register 2 geometries and 3 cameras with known compatibility. Verify the harness tests the correct number of pairs.

2. **Pass case:** Mock geometry with oversized planes and a static camera. All results should be `pass: true`, no failures, no adjustments.

3. **Facing-camera failure case:** Mock geometry with a deliberately small backdrop (e.g., size [10, 10] when the frustum needs [50, 30]). Verify `pass: false`, `failures` contains the backdrop slot, `minimumSafeSize` and `recommendedSize` are populated (both non-null).

4. **Camera-passes-through case:** Mock geometry with subject at Z=-5, camera with maxDisplacementZ=20 starting at Z=5 (envelope reaches Z=-15, past subject). Verify `cameraPassesThrough: true`, `minimumSafeSize: null`, `recommendedSize: null`.

5. **Rotated plane skipping:** Include a floor slot. Verify it appears in `skippedSlots` and `visualReviewRequired`.

6. **OBJ-040/OBJ-041 precedence (D2/D4):** Mock a facing-camera plane that passes OBJ-040 sampling but fails OBJ-041 analytical. Verify `pass: true` and the plane does NOT appear in `failures`.

7. **OBJ-041 rotated plane failure:** Mock a floor plane that fails OBJ-041 oversizing. Verify `pass: false` even though OBJ-040 skipped it. Verify `failedCheck: 'oversizing'`, `minimumSafeSize: null`, `recommendedSize` is OBJ-041's `requiredSize * 1.05` (non-null).

8. **Multiple speeds:** Verify a plane that passes at speed=0.5 but fails at speed=1.5 results in `allPassed: false` for the pair.

9. **Aggregated adjustments:** Two camera paths cause the same slot to fail with different minimum sizes. Verify `recommendedAdjustments` uses the larger of the two.

10. **Aspect ratio sensitivity:** A plane that passes at 16:9 but fails at 9:16 (or vice versa). Verify per-combination results are correct.

11. **Determinism:** Run twice, compare reports for identity.

12. **Empty registries:** Verify no errors, 0 pairs tested, `registryConsistencyErrors` is empty.

13. **Config validation:** Verify `RangeError` for speeds containing 0, negative aspectRatios, sampleCount < 1.

14. **Registry consistency errors:** Mock registries with a bidirectional mismatch. Verify `registryConsistencyErrors` is non-empty. Verify harness still tests consistent pairs.

**Report formatting tests:**

15. Verify `formatEdgeRevealReport` produces Markdown containing expected section headers (executive summary, registry consistency, per-pair results, failure details, visual review checklist, recommended adjustments).

16. Verify the Markdown includes geometry and camera names in the results table.

17. Verify the Markdown includes the run timestamp.

18. Verify the Markdown includes registry consistency errors when present.

**Test manifest generation tests:**

19. Verify manifest has correct `version`, `composition` (width, height, fps), and `scenes` array with one scene.

20. Verify each slot in the geometry has a corresponding entry in the manifest's `planes` record.

21. Verify all plane `src` values are data URIs (`data:image/png;base64,...`).

22. Verify distinct colors per slot (data URIs for different slots are different).

23. Verify the manifest passes OBJ-004 Zod schema validation.

24. Verify optional geometry slots are included in the manifest.

### Integration Tests (with real registries)

25. **Stage + push/pull:** Load real stage geometry (OBJ-018) and push/pull presets (OBJ-027). Run harness at default config. Verify all facing-camera planes pass at speed=1.0, both aspect ratios. This is the core TC-03 validation.

26. **Stage + static:** Stage geometry with static camera (OBJ-026). All planes should trivially pass (zero displacement).

27. **Stage + gentle_float:** Stage with gentle_float (OBJ-031). Verify results.

28. **All verified geometries x all verified cameras:** Run harness against all currently verified geometries and cameras. Document pass/fail status. This is the comprehensive TC-03 validation for the implemented set.

29. **Generate and validate test manifests:** Generate test manifests for all bidirectionally compatible pairs. Validate each against the manifest schema (OBJ-016). Optionally render a subset via OBJ-035 and inspect output.

### Relevant Testable Claims

- **TC-03** (direct): The harness validates that perspective projection produces correct 2.5D by confirming no edge reveals across all geometry+camera combinations.
- **TC-04** (partial): Edge-reveal freedom confirms that the spatial vocabulary works — an LLM selecting geometry+camera never encounters edge artifacts.
- **TC-05** (partial): The tunnel geometry + forward push is validated here alongside stage.
- **TC-08** (partial): The coverage analysis from OBJ-041 (invoked during harness setup) contributes data for TC-08.

## Integration Points

### Depends on

| Dependency | What OBJ-069 imports | How used |
|---|---|---|
| **OBJ-040** (`src/spatial/edge-reveal.ts`) | `validateGeometryEdgeReveal`, `computeMinimumFacingPlaneSize`, `isFacingCameraRotation`, types (`GeometryEdgeRevealReport`, `PlaneEdgeRevealResult`, `EdgeRevealCheck`) | Sampling-based edge-reveal validation for facing-camera planes. Minimum size computation for failure remediation. |
| **OBJ-041** (`src/validation/spatial-compatibility.ts`) | `checkOversizingSufficiency`, `validateRegistryConsistency`, `analyzeCoverage`, types (`OversizingCheckResult`, `SpatialValidationError`, `CoverageAnalysis`) | Analytical oversizing validation for all planes including rotated. Registry consistency pre-check. Coverage matrix for pair enumeration. `SpatialValidationError` type for `registryConsistencyErrors`. |
| **OBJ-004** (`src/manifest/schema.ts`) | `Manifest` type | Return type of `generateTestManifest`. Ensures generated test manifests conform to the manifest schema. |
| **OBJ-018** (`src/scenes/geometries/stage.ts`) | `stageGeometry` (indirectly via registry) | The stage geometry is the primary validation target. Used in integration tests. |
| **OBJ-027** (`src/camera/presets/push_pull.ts`) | `slowPushForward`, `slowPullBack` (indirectly via registry) | Push/pull presets are the primary camera paths with significant Z displacement. Used in integration tests. |
| **OBJ-035** (`src/engine/orchestrator.ts`) | `Orchestrator` (used by callers, not by the harness directly) | Callers render `generateTestManifest()` output via the orchestrator for Director Agent visual review. The harness itself does not import or invoke the orchestrator. |
| **OBJ-005** (`src/scenes/geometries/types.ts`) | `SceneGeometry`, `PlaneSlot`, `GeometryRegistry` types | Geometry type definitions for traversing slots. |
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraPathRegistry`, `CameraParams`, `OversizeRequirements` types | Camera type definitions for preset evaluation. |
| **OBJ-003** (`src/spatial/types.ts`) | `Vec3`, `Size2D` types | Core spatial types used throughout. |

### Consumed by

| Downstream | How it uses OBJ-069 |
|---|---|
| **OBJ-059-066** (Geometry visual tuning) | Uses `visualReviewRequired` to identify which rotated planes need Director Agent review. Uses `recommendedAdjustments` to adjust plane sizes before tuning begins. |
| **OBJ-067** (Final visual sign-off) | Depends on OBJ-069 confirming that all geometry+camera combinations are edge-reveal-free. OBJ-067 cannot be verified until OBJ-069 passes. |
| **OBJ-071** (SKILL.md) | References OBJ-069's validation results to document which geometry+camera combinations are safe. |
| **Development/CI** | `runEdgeRevealHarness` can be run as a CI check whenever geometries or camera presets change, catching regressions. |

### File Placement

```
depthkit/
  src/
    validation/
      edge-reveal-harness.ts    # NEW — runEdgeRevealHarness,
                                #       formatEdgeRevealReport,
                                #       generateTestManifest,
                                #       all types
      index.ts                  # MODIFY — add re-exports
  test/
    unit/
      edge-reveal-harness.test.ts   # Unit tests with mock registries
    integration/
      edge-reveal-harness.test.ts   # Integration tests with real registries
```

## Open Questions

### OQ-A: Should the harness auto-apply recommended size adjustments?

Currently the harness only recommends adjustments. It could optionally modify geometry definitions in place (mutating `PlaneSlot.size`). **Recommendation:** No. Geometry definitions are static module-level constants. Adjustments should be applied by the geometry author (human or Code Agent) after reviewing the report. The harness is a diagnostic tool, not a fixer.

### OQ-B: Should the harness validate texture-adjusted sizes?

OBJ-040's `validateGeometryEdgeReveal()` accepts `textureSizeOverrides`. The harness currently validates against geometry slot definition sizes only. If textures are available (e.g., test fixtures), the harness could also validate against texture-adjusted sizes (in 'contain' mode, which may produce smaller planes). **Recommendation:** Defer. Slot definition sizes represent the geometry author's sizing intent. Texture-adjusted validation belongs at render time (OBJ-039) or manifest validation time (OBJ-017). The harness validates the geometry's spatial design, not specific image content.

### OQ-C: Should offset testing be more systematic?

The default config tests only `[0, 0, 0]` offset. Real manifests may use offsets like `[2, 0, 0]` for lateral camera shifts. Should the harness test a grid of offsets? **Recommendation:** Keep the default simple. Callers concerned about offset sensitivity can add specific offsets to the config. Edge-reveal risk from offset is linear (OBJ-040's margin formulas show offset adds directly to the frustum shift), so if a plane has >2 units of margin at zero offset, it survives a [2, 0, 0] offset.

### OQ-D: How should the harness handle geometries/cameras that are open (not yet implemented)?

The harness operates on whatever is in the registries at call time. Open objectives (OBJ-022 through OBJ-025, OBJ-032 through OBJ-034) won't be registered. The harness simply doesn't test them. When they're implemented and registered, re-running the harness picks them up automatically. No special handling needed.

### OQ-E: Should the harness test with FOV overrides?

Some camera presets may support FOV animation. The harness tests at the preset's declared FOV range (captured in `OversizeRequirements.fovRange`). Manifest-level FOV overrides are not part of the camera params schema. If FOV overrides are added later, the harness config can be extended.
