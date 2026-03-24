# Deliberation Transcript: OBJ-069

---

## Round 1 — spec_author

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
} from './spatial-compatibility';
import type { Size2D, Vec3 } from '../spatial/types';

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
   * true only when:
   * - All facing-camera planes pass OBJ-040 sampling (safe: true)
   * - All planes pass OBJ-041 oversizing (sufficient: true,
   *   excluding skippedNonAxisAligned)
   * - No cameraPassesThrough on any plane
   */
  pass: boolean;

  /**
   * Slot names that failed, with failure details.
   * Empty if pass is true.
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

  /** Which check failed: 'sampling' (OBJ-040), 'oversizing' (OBJ-041), or 'both'. */
  failedCheck: 'sampling' | 'oversizing' | 'both';

  /**
   * The worst margin from OBJ-040 sampling (if applicable).
   * Negative value = how many world units the plane is undersized.
   * -Infinity if camera passes through the plane.
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
   * computeMinimumFacingPlaneSize (for facing-camera planes).
   * Null for rotated planes or camera-passes-through cases.
   */
  minimumSafeSize: Size2D | null;

  /**
   * Recommended adjusted size: minimumSafeSize * 1.05 safety margin.
   * Null when minimumSafeSize is null.
   */
  recommendedSize: Size2D | null;

  /** Whether the camera passes through this plane. */
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
 * Algorithm:
 * 1. Enumerate all geometry+camera pairs from the registries.
 *    Filter to bidirectionally compatible pairs (or all pairs
 *    if compatibleOnly is false).
 * 2. For each pair, for each (aspectRatio, speed, offset) combo:
 *    a. Run OBJ-040's validateGeometryEdgeReveal() for
 *       sampling-based facing-camera validation.
 *    b. Run OBJ-041's checkOversizingSufficiency() for
 *       analytical all-plane validation.
 *    c. For facing-camera slots that fail OBJ-040, compute
 *       minimumSafeSize via OBJ-040's
 *       computeMinimumFacingPlaneSize().
 *    d. Record results.
 * 3. Aggregate: compute per-pair summaries, deduplicate visual
 *    review items, compute maximum recommended sizes.
 * 4. Return EdgeRevealHarnessReport.
 *
 * @param config - Harness configuration.
 * @returns Complete report.
 */
export function runEdgeRevealHarness(
  config: EdgeRevealHarnessConfig
): EdgeRevealHarnessReport;

/**
 * Formats the harness report as a human-readable Markdown document.
 *
 * Includes:
 * - Executive summary (pass/fail counts)
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
 * placeholder images (generated as data: URIs or referencing
 * test fixtures) so that edge reveals are maximally visible
 * (bright colors on a black background reveal edges instantly).
 *
 * The generated manifest is suitable for rendering via OBJ-035's
 * Orchestrator to produce a short test clip for Director Agent
 * review.
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
): object;
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

**Decision:** Every pair is validated by BOTH OBJ-040's `validateGeometryEdgeReveal()` (sampling-based, facing-camera only) and OBJ-041's `checkOversizingSufficiency()` (analytical, all orientations). A pair passes only if both checks pass.

**Rationale:** The two checks are complementary per OBJ-041 D9:
- OBJ-041 is conservative (symmetric envelope, may over-estimate) but covers rotated planes.
- OBJ-040 is precise (trajectory sampling) but only handles facing-camera planes.
- A pair that passes OBJ-041's analytical check but fails OBJ-040's sampling reveals that the analytical model was insufficient.
- A pair that passes OBJ-040 but fails OBJ-041 reveals that the analytical model is overly conservative (documented but not blocking — the sampling result is authoritative for facing-camera planes).

**Resolution rule:** For facing-camera planes, if OBJ-040 (sampling) says safe but OBJ-041 (analytical) says insufficient, the **OBJ-040 result takes precedence** (it's more precise). The OBJ-041 failure is logged as a note but does not mark the pair as failed. For rotated planes, only OBJ-041 applies; OBJ-040 skips them.

### D3: Default Parameter Matrix — Aspect Ratios × Speeds × Offsets

**Decision:** Default test matrix:
- Aspect ratios: `[16/9, 9/16]` — landscape and portrait per C-04.
- Speeds: `[0.5, 1.0, 1.5]` — conservative, standard, moderately aggressive.
- Offsets: `[[0, 0, 0]]` — no offset by default.

This produces 6 combinations per pair (2 aspects × 3 speeds × 1 offset). With N pairs, total combinations = 6N.

**Rationale:** Speed 2.0+ is extreme and likely to fail for close planes (OBJ-027 D2 shows subject at 5x apparent size change at speed=1.0). Testing speed=1.5 catches marginal cases. Speed=0.5 confirms that conservative use always works. Default offsets of [0,0,0] test the standard case; callers can add offset tests for specific debugging.

### D4: `pass` Criterion — Strict for Facing-Camera, Visual-Review for Rotated

**Decision:** A `PairValidationResult.pass` is `true` when:
1. ALL facing-camera planes have `safe: true` in OBJ-040's sampling report.
2. ALL axis-aligned planes (facing, floor, ceiling, wall) have `sufficient: true` in OBJ-041's oversizing check.
3. No plane has `cameraPassesThrough: true`.

Non-axis-aligned planes with `skippedNonAxisAligned: true` do NOT cause failure — they produce `SkippedSlot` entries for visual review.

**Exception per D2:** If OBJ-040 sampling says a facing-camera plane is safe but OBJ-041 analytical says it's insufficient, the plane is treated as **passing** (OBJ-040 is authoritative for facing-camera planes). A note is added to the result but `pass` remains `true`.

### D5: Minimum Safe Size Computation for Failures

**Decision:** When a facing-camera plane fails OBJ-040's sampling check, the harness calls `computeMinimumFacingPlaneSize()` from OBJ-040 to determine the exact minimum size, then applies a 1.05 safety margin (5%) as recommended by OBJ-040's JSDoc. The result is stored as `recommendedSize` in the `SlotFailure`.

For rotated planes that fail OBJ-041's analytical check, the `requiredSize` from `OversizingCheckResult` is used directly (already conservative).

**Rationale:** Geometry authors need actionable size adjustments, not just pass/fail. The 1.05 margin accounts for floating-point imprecision and frame-rate-dependent interpolation per OBJ-040's recommendation.

### D6: Aggregated Recommended Adjustments

**Decision:** The harness report includes a `recommendedAdjustments` map that aggregates across all failing combinations. For each geometry+slot that fails at ANY tested combination, the recommended size is the maximum of all recommended sizes across all failing combinations for that slot.

**Rationale:** A geometry author wants a single size adjustment per slot that fixes ALL edge reveals across all compatible cameras, aspect ratios, and reasonable speeds. Taking the maximum ensures one fix resolves all failures.

### D7: Visual Review Checklist for Rotated Planes

**Decision:** Rotated planes (floor, ceiling, walls) that are skipped by OBJ-040's sampling are collected into a `visualReviewRequired` list. Each entry names the geometry, slot, reason for skipping, relevant camera paths, and whether OBJ-041's analytical check passed. This checklist drives the Director Agent visual review workflow.

**Rationale:** OBJ-040 D1 explicitly states that rotated planes are validated through the Director Agent tuning workflow. OBJ-069 generates the checklist; the actual visual review happens during OBJ-059-066 tuning rounds or as a follow-up.

### D8: Test Manifest Generation for Visual Review

**Decision:** `generateTestManifest()` produces a minimal manifest with high-contrast placeholder images (e.g., bright red floor, bright green walls, bright blue backdrop on a black clear color) so edge reveals are instantly visible in a rendered clip. The manifest uses the geometry's required slots with data URI images (solid-color PNGs) — no external asset files needed.

**Rationale:** The Director Agent (or human reviewer) needs to see edge reveals clearly. Solid-color planes against a black background make any edge gap immediately obvious. Data URIs eliminate file dependencies for test rendering.

### D9: Report Format — Markdown for Human + Structured Object for Programmatic Use

**Decision:** The harness returns a structured `EdgeRevealHarnessReport` object. `formatEdgeRevealReport()` converts it to Markdown. The test suite uses the structured object for assertions; the CLI/development workflow uses the Markdown for human review.

### D10: Aspect Ratio Label Mapping

**Decision:** Common aspect ratios are labeled for readability: `16/9` → `'16:9'`, `9/16` → `'9:16'`, `4/3` → `'4:3'`. Non-standard ratios use decimal notation (e.g., `'2.35:1'`). The label is purely cosmetic — all math uses the numeric ratio.

### D11: Compatibility Filtering via OBJ-041

**Decision:** The harness calls OBJ-041's `validateRegistryConsistency()` first. If there are consistency errors, they are included in the report header but do not prevent validation from proceeding on consistent pairs. Pair enumeration uses OBJ-041's `analyzeCoverage()` to get the compatibility matrix, then filters to bidirectionally compatible pairs (unless `compatibleOnly: false`).

**Rationale:** Reuses OBJ-041's existing analysis rather than reimplementing pair enumeration. The coverage analysis also feeds TC-08.

## Acceptance Criteria

### Harness Execution

- [ ] **AC-01:** `runEdgeRevealHarness` with a registry containing the stage geometry (OBJ-018) and `slow_push_forward`/`slow_pull_back` (OBJ-027) camera presets produces a report with at least 2 pairs tested.
- [ ] **AC-02:** Each pair is tested at both 16:9 and 9:16 aspect ratios (default config), producing at least 6 `PairValidationResult` entries per pair (2 aspects × 3 speeds).
- [ ] **AC-03:** For a pair where all facing-camera planes are oversized sufficiently (e.g., stage + static camera at speed=1.0), `pass` is `true`.
- [ ] **AC-04:** For a pair where a facing-camera plane is deliberately undersized (e.g., a test geometry with a small backdrop), `pass` is `false`, and `failures` contains an entry for the undersized slot.
- [ ] **AC-05:** Failed slots include `minimumSafeSize` and `recommendedSize` (with 1.05 margin) for facing-camera planes.
- [ ] **AC-06:** Failed slots with `cameraPassesThrough: true` have `minimumSafeSize: null` and `recommendedSize: null`, with a message indicating the structural incompatibility.

### Dual Validation

- [ ] **AC-07:** Both `samplingReport` (OBJ-040) and `oversizingResults` (OBJ-041) are populated for each combination.
- [ ] **AC-08:** If OBJ-040 says a facing-camera plane is safe but OBJ-041 says it's insufficient, the pair is marked as `pass: true` (OBJ-040 takes precedence for facing-camera planes).
- [ ] **AC-09:** If OBJ-041 says a rotated plane is insufficient, the pair is marked as `pass: false` even if OBJ-040 skipped that plane.

### Rotated Plane Handling

- [ ] **AC-10:** Rotated planes (floor, ceiling, walls) appear in `skippedSlots` with a non-empty `reason` from OBJ-040.
- [ ] **AC-11:** `visualReviewRequired` in the report contains deduplicated entries for all rotated plane slots across all tested pairs.
- [ ] **AC-12:** Each `VisualReviewItem` lists all camera paths that are compatible with that geometry.

### Report Aggregation

- [ ] **AC-13:** `recommendedAdjustments` contains entries only for slots that failed at least one combination.
- [ ] **AC-14:** When a slot fails at multiple speed/aspect combinations, `recommendedAdjustments` uses the maximum recommended size across all failures.
- [ ] **AC-15:** `totalPairsTested` counts unique geometry+camera pairs (not individual param combinations). `totalCombinationsTested` counts individual param combinations.
- [ ] **AC-16:** A pair is counted in `totalPairsPassed` only if ALL its param combinations passed.

### Report Formatting

- [ ] **AC-17:** `formatEdgeRevealReport` produces valid Markdown with: executive summary, per-pair results table, failure details, visual review checklist, and recommended adjustments.
- [ ] **AC-18:** The Markdown report includes the harness run timestamp.

### Test Manifest Generation

- [ ] **AC-19:** `generateTestManifest` produces a manifest object with the correct geometry name, camera name, and one plane entry per required slot in the geometry.
- [ ] **AC-20:** Generated manifests use data URI images (`data:image/png;base64,...`) for all planes — no external file dependencies.
- [ ] **AC-21:** Each slot in the generated manifest uses a distinct solid color so edge reveals per-plane are visually distinguishable.
- [ ] **AC-22:** The generated manifest is structurally valid per OBJ-004's schema (can pass manifest validation).

### Specific Geometry+Camera Validations (Stage + Push/Pull)

- [ ] **AC-23:** Stage geometry + `slow_push_forward` at speed=1.0, aspect=16:9: all facing-camera planes (sky, backdrop, midground, subject, near_fg) pass OBJ-040 sampling. This validates that OBJ-018's plane sizes are sufficient for OBJ-027's default Z displacement.
- [ ] **AC-24:** Stage geometry + `slow_pull_back` at speed=1.0, aspect=16:9: all facing-camera planes pass. `slow_pull_back` has `recommendedOversizeFactor=1.7` — this confirms the stage's plane sizes accommodate the retreat.
- [ ] **AC-25:** Stage geometry + `slow_push_forward` at speed=1.0, aspect=9:16 (portrait): all facing-camera planes pass. Portrait mode narrows the horizontal frustum — plane widths must still exceed visible width.
- [ ] **AC-26:** Stage geometry floor slot (rotated) appears in `skippedSlots` for OBJ-040 and in `visualReviewRequired`. OBJ-041's analytical check for the floor provides the `analyticalCheckPassed` value.

### Determinism

- [ ] **AC-27:** Running `runEdgeRevealHarness` twice with the same config and registries produces identical reports (C-05).

## Edge Cases and Error Handling

### Registry Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty geometry registry | Report has 0 pairs tested. No errors thrown. |
| Empty camera registry | Report has 0 pairs tested. No errors thrown. |
| Geometry with no bidirectionally compatible cameras | Pair count is 0 for that geometry. If `compatibleOnly: false`, pairs are tested but noted as non-compatible. |
| Registry consistency errors (OBJ-041) | Logged in report header. Validation proceeds on consistent pairs. |

### Validation Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Camera path where camera passes through a facing-camera plane (e.g., high speed push through subject) | OBJ-040 returns `safe: false`, `worstMargin: -Infinity`. OBJ-041 returns `cameraPassesThrough: true`. Failure reported with `cameraPassesThrough: true`, `minimumSafeSize: null`. Message recommends reducing speed or moving the plane. |
| Camera path where near_fg ends up behind camera at end position | OBJ-040 catches this at the sample point where distance <= 0. Reported as failure with `worstMargin: -Infinity`. |
| Plane exactly at the boundary of the camera's position envelope | OBJ-041 uses EPSILON=0.001 for distance. OBJ-040 catches with sampling. Both report marginal results. |
| All planes pass OBJ-040 but a rotated plane fails OBJ-041 | `pass: false` because OBJ-041 failure on axis-aligned rotated planes is authoritative. |
| Non-axis-aligned rotation plane | OBJ-041 skips with `skippedNonAxisAligned: true`. OBJ-040 skips with rotation check. Both appear in `skippedSlots`. `pass` is not affected (benefit of the doubt). |

### Parameter Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `speeds` contains 0 | Throws RangeError: "speed must be > 0". |
| `speeds` is empty array | No combinations tested. Report has 0 combinations. |
| `aspectRatios` is empty | No combinations tested. |
| `sampleCount` < 1 | Propagated as RangeError from OBJ-040. |
| Very large speed (e.g., 10.0) | Valid. Many planes will fail. All failures reported with recommendations. |

### Test Manifest Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Geometry with only required slots | Manifest includes only required slots. |
| Geometry with all optional slots | Manifest includes ALL slots (required and optional) to test full coverage. |
| Geometry with 0 required slots | Manifest has empty `planes` — may fail validation. `generateTestManifest` should include at least all required slots; if none are required, includes all slots. |

## Test Strategy

### Unit Tests

**Harness logic tests (with mock registries):**

1. **Basic pair enumeration:** Register 2 geometries and 3 cameras with known compatibility. Verify the harness tests the correct number of pairs.

2. **Pass case:** Mock geometry with oversized planes and a static camera. All results should be `pass: true`, no failures, no adjustments.

3. **Facing-camera failure case:** Mock geometry with a deliberately small backdrop (e.g., size [10, 10] when the frustum needs [50, 30]). Verify `pass: false`, `failures` contains the backdrop slot, `minimumSafeSize` and `recommendedSize` are populated.

4. **Camera-passes-through case:** Mock geometry with subject at Z=-5, camera with maxDisplacementZ=20 starting at Z=5 (envelope reaches Z=-15, past subject). Verify `cameraPassesThrough: true`.

5. **Rotated plane skipping:** Include a floor slot. Verify it appears in `skippedSlots` and `visualReviewRequired`.

6. **OBJ-040/OBJ-041 precedence (D2/D4):** Mock a facing-camera plane that passes OBJ-040 sampling but fails OBJ-041 analytical. Verify `pass: true`.

7. **OBJ-041 rotated plane failure:** Mock a floor plane that fails OBJ-041 oversizing. Verify `pass: false` even though OBJ-040 skipped it.

8. **Multiple speeds:** Verify a plane that passes at speed=0.5 but fails at speed=1.5 results in `allPassed: false` for the pair.

9. **Aggregated adjustments:** Two camera paths cause the same slot to fail with different minimum sizes. Verify `recommendedAdjustments` uses the larger of the two.

10. **Aspect ratio sensitivity:** A plane that passes at 16:9 but fails at 9:16 (or vice versa). Verify per-combination results are correct.

11. **Determinism:** Run twice, compare reports for identity.

12. **Empty registries:** Verify no errors, 0 pairs tested.

**Report formatting tests:**

13. Verify `formatEdgeRevealReport` produces Markdown containing expected section headers.

14. Verify the Markdown includes geometry and camera names in the results table.

**Test manifest generation tests:**

15. Verify manifest structure matches OBJ-004 schema requirements.

16. Verify each required slot has a data URI image.

17. Verify distinct colors per slot (parse the data URIs or check they're different).

18. Verify optional slots are included.

### Integration Tests (with real registries)

19. **Stage + push/pull:** Load real stage geometry (OBJ-018) and push/pull presets (OBJ-027). Run harness at default config. Verify all facing-camera planes pass at speed=1.0, both aspect ratios. This is the core TC-03 validation.

20. **Stage + static:** Stage geometry with static camera (OBJ-026). All planes should trivially pass (zero displacement).

21. **Stage + gentle_float:** Stage with gentle_float (OBJ-031). Verify results.

22. **All verified geometries × all verified cameras:** Run harness against all currently verified geometries and cameras. Document pass/fail status. This is the comprehensive TC-03 validation for the implemented set.

23. **Generate and validate test manifests:** Generate test manifests for all bidirectionally compatible pairs. Validate each against the manifest schema (OBJ-016). Optionally render a subset via OBJ-035 and inspect output.

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
| **OBJ-041** (`src/validation/spatial-compatibility.ts`) | `checkOversizingSufficiency`, `validateRegistryConsistency`, `analyzeCoverage`, types (`OversizingCheckResult`, `CoverageAnalysis`) | Analytical oversizing validation for all planes including rotated. Registry consistency pre-check. Coverage matrix for pair enumeration. |
| **OBJ-018** (`src/scenes/geometries/stage.ts`) | `stageGeometry` (indirectly via registry) | The stage geometry is the primary validation target. Used in integration tests. |
| **OBJ-027** (`src/camera/presets/push_pull.ts`) | `slowPushForward`, `slowPullBack` (indirectly via registry) | Push/pull presets are the primary camera paths with significant Z displacement. Used in integration tests. |
| **OBJ-035** (`src/engine/orchestrator.ts`) | `Orchestrator` (used by callers, not by the harness directly) | Callers render `generateTestManifest()` output via the orchestrator for Director Agent visual review. |
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

---

I believe this covers the objective comprehensively. I'd welcome the Challenger's review on:
1. Whether the dual-validation precedence rule (D2/D4) is sound
2. Whether the default parameter matrix (D3) covers enough ground
3. Whether `generateTestManifest` belongs in this module or should be separate
4. Whether the acceptance criteria for specific geometry+camera pairs (AC-23 through AC-26) are appropriately scoped

---

## Round 2 — spec_challenger

I've reviewed the proposed specification for OBJ-069 carefully. The overall structure is solid — the dual-validation approach (OBJ-040 sampling + OBJ-041 analytical) is sound, the report types are well-designed, and the test strategy is comprehensive. Here are my challenges:

---

## Issue 1 — **Major**: `pass` criterion contradicts the D2/D4 precedence rule

The `PairValidationResult.pass` type comment says:

> true only when:
> - All facing-camera planes pass OBJ-040 sampling (safe: true)
> - **All planes pass OBJ-041 oversizing** (sufficient: true, excluding skippedNonAxisAligned)
> - No cameraPassesThrough on any plane

But D4 explicitly says: "If OBJ-040 sampling says a facing-camera plane is safe but OBJ-041 analytical says it's insufficient, the plane is treated as **passing**."

These contradict. The second bullet says "All planes" must pass OBJ-041, but the precedence rule exempts facing-camera planes that already passed OBJ-040. An implementer has two conflicting definitions of `pass`.

**Proposed fix:** Rewrite the `pass` comment to precisely state:

```
true only when:
- All facing-camera planes pass OBJ-040 sampling (safe: true).
  (OBJ-041 failures for facing-camera planes that pass OBJ-040
  are non-blocking — logged as notes, not failures.)
- All rotated axis-aligned planes (floor, ceiling, walls) pass
  OBJ-041 oversizing (sufficient: true).
- No plane has cameraPassesThrough: true (from either check).
- Non-axis-aligned planes (skippedNonAxisAligned) do not affect pass.
```

Similarly, the `failures` array description should clarify that a facing-camera plane which passes OBJ-040 but fails OBJ-041 does NOT appear in `failures`.

---

## Issue 2 — **Major**: `generateTestManifest` returns `object` and has no OBJ-004 dependency

The return type is `object`, but AC-22 says "The generated manifest is structurally valid per OBJ-004's schema." The function must produce something conforming to OBJ-004's `Manifest` type, but OBJ-004 is not listed in the dependencies.

Two options:

**Option A** (preferred): Add OBJ-004 as a dependency. Change the return type to the actual `Manifest` type (or at minimum, a type alias that references it). This makes the contract explicit.

**Option B**: Keep it as a plain JSON object and document that it is the caller's responsibility to validate. But then AC-22 is testing the wrong thing (it's testing that the function happens to produce valid JSON, not that the contract guarantees it).

**Proposed fix:** Add OBJ-004 to the dependency table. Change the return type:

```typescript
import type { Manifest } from '../manifest/schema';

export function generateTestManifest(
  ...
): Manifest;
```

And add a note in the integration points.

---

## Issue 3 — **Minor**: `cameraPassesThrough` source ambiguity in `SlotFailure`

OBJ-040 reports `-Infinity` margins when the camera is behind a plane at a sample point. OBJ-041 reports `cameraPassesThrough: true` when the symmetric position envelope includes the plane's perpendicular coordinate. These are different computations that can disagree (e.g., the symmetric envelope includes the plane but the actual trajectory never reaches it, or vice versa).

`SlotFailure.cameraPassesThrough` is a single boolean with no indication of which source set it. An implementer must decide: is it the OR of both? Only OBJ-041? Only OBJ-040 (when `worstMargin === -Infinity`)?

**Proposed fix:** Add a brief comment to `cameraPassesThrough`:

```typescript
/**
 * Whether the camera passes through or behind this plane.
 * True if OBJ-041 reports cameraPassesThrough: true for this slot,
 * OR if OBJ-040 sampling finds any sample point where the
 * view-axis distance to the plane is <= 0.
 */
cameraPassesThrough: boolean;
```

---

## Issue 4 — **Minor**: Config validation not specified

The edge case table says `speeds` containing 0 throws `RangeError`. But the spec doesn't say WHERE this validation happens. Does `runEdgeRevealHarness` validate its own config at the top of the function? Or does it let OBJ-040/OBJ-041 blow up somewhere deep in the call stack?

**Proposed fix:** Add a brief sentence to the `runEdgeRevealHarness` JSDoc or algorithm description:

> The harness validates its config at entry: speeds must all be > 0, aspectRatios must all be > 0, sampleCount must be >= 1. Invalid config throws RangeError before any pair is tested.

---

## Issue 5 — **Minor**: `SlotFailure.failedCheck` value when OBJ-041 fails a rotated plane but OBJ-040 skipped it

What is `failedCheck` for a rotated floor plane that fails OBJ-041? The enum values are `'sampling' | 'oversizing' | 'both'`. Since OBJ-040 skipped it, it should be `'oversizing'`. But a reader might expect `'both'` since the plane failed the only applicable check. The current enum is fine, but a sentence clarifying this scenario would help.

**Proposed fix:** Add to the `failedCheck` comment: `'oversizing'` includes cases where OBJ-040 skipped the plane (rotated) and only OBJ-041 was applicable.

---

## Points of Agreement

The following aspects are well-designed and I approve them:

- **D1 (synchronous validation module):** Correct separation from rendering. Clean.
- **D2/D4 precedence logic** (once the `pass` comment is fixed): OBJ-040 sampling is more precise than OBJ-041 analytical for facing-camera planes, so it should be authoritative. Sound.
- **D3 default parameter matrix:** 2 aspects × 3 speeds × 1 offset = 6 combos per pair. Reasonable coverage without being excessive.
- **D5/D6 minimum safe size and aggregated adjustments:** Actionable output for geometry authors. The 1.05 safety margin is well-sourced from OBJ-040's JSDoc.
- **D7 visual review checklist:** Bridges the gap between automated validation and Director Agent review for rotated planes. Correctly scoped.
- **D8 solid-color test manifests with data URIs:** Clever approach — maximally visible edge reveals with zero file dependencies.
- **D9 structured + Markdown dual output:** Right for both programmatic consumers and human reviewers.
- **D11 reusing OBJ-041's `analyzeCoverage`:** Good reuse, avoids reimplementing pair enumeration.
- **AC-23 through AC-26:** Specific, named geometry+camera validations. These are the core integration tests that validate the objective's purpose.
- **Test strategy:** Thorough. Unit tests with mocks + integration tests with real registries.
- **Open questions:** Appropriately scoped. OQ-A (no auto-apply) and OQ-B (no texture-adjusted sizes) are correct decisions.

---

Please address Issues 1-5 in your revision. Issues 1 and 2 are the ones I need to see structurally resolved before converging.

---

## Round 3 — spec_author

All five issues are valid. Here's my revised specification with each addressed:

---

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
   * computeMinimumFacingPlaneSize (for facing-camera planes).
   * Null for rotated planes or camera-passes-through cases.
   */
  minimumSafeSize: Size2D | null;

  /**
   * Recommended adjusted size: minimumSafeSize * 1.05 safety margin.
   * Null when minimumSafeSize is null.
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
 * 2. Run OBJ-041's validateRegistryConsistency(). Log any
 *    consistency errors in the report header but proceed.
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
 *    e. Record results.
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

### D3: Default Parameter Matrix — Aspect Ratios × Speeds × Offsets

**Decision:** Default test matrix:
- Aspect ratios: `[16/9, 9/16]` — landscape and portrait per C-04.
- Speeds: `[0.5, 1.0, 1.5]` — conservative, standard, moderately aggressive.
- Offsets: `[[0, 0, 0]]` — no offset by default.

This produces 6 combinations per pair (2 aspects × 3 speeds × 1 offset). With N pairs, total combinations = 6N.

**Rationale:** Speed 2.0+ is extreme and likely to fail for close planes (OBJ-027 D2 shows subject at 5x apparent size change at speed=1.0). Testing speed=1.5 catches marginal cases. Speed=0.5 confirms that conservative use always works. Default offsets of [0,0,0] test the standard case; callers can add offset tests for specific debugging.

### D4: `pass` Criterion — OBJ-040 Authoritative for Facing-Camera, OBJ-041 Authoritative for Rotated

**Decision:** A `PairValidationResult.pass` is `true` when ALL of the following hold:

1. All **facing-camera** planes pass OBJ-040 sampling (`safe: true`). If OBJ-040 says safe but OBJ-041 says insufficient for the same facing-camera plane, the plane is treated as **passing** — OBJ-040's precise trajectory sampling is authoritative over OBJ-041's conservative symmetric envelope for facing-camera planes. The OBJ-041 discrepancy is logged as a note but does NOT appear in `failures` and does NOT affect `pass`.

2. All **rotated axis-aligned** planes (floor, ceiling, walls) pass OBJ-041 oversizing (`sufficient: true`). OBJ-040 skips these; OBJ-041 is the only automated check.

3. **No plane** has `cameraPassesThrough: true` from either check.

4. **Non-axis-aligned** planes (`skippedNonAxisAligned` in OBJ-041, skipped in OBJ-040) do NOT affect `pass`. They produce `SkippedSlot` entries for visual review.

**Rationale:** OBJ-040 samples the actual trajectory at 100 points — it knows precisely whether the plane covers the frustum at each moment. OBJ-041 uses worst-case symmetric displacement envelopes that intentionally over-estimate. For facing-camera planes where both run, the more precise check wins. For rotated planes where only OBJ-041 runs, it's the sole authority.

### D5: Minimum Safe Size Computation for Failures

**Decision:** When a facing-camera plane fails OBJ-040's sampling check, the harness calls `computeMinimumFacingPlaneSize()` from OBJ-040 to determine the exact minimum size, then applies a 1.05 safety margin (5%) as recommended by OBJ-040's JSDoc. The result is stored as `recommendedSize` in the `SlotFailure`.

For rotated planes that fail OBJ-041's analytical check, the `requiredSize` from `OversizingCheckResult` is used directly (already conservative). `minimumSafeSize` is set to the `requiredSize`, and `recommendedSize` is `requiredSize * 1.05`.

**Rationale:** Geometry authors need actionable size adjustments, not just pass/fail. The 1.05 margin accounts for floating-point imprecision and frame-rate-dependent interpolation per OBJ-040's recommendation.

### D6: Aggregated Recommended Adjustments

**Decision:** The harness report includes a `recommendedAdjustments` map that aggregates across all failing combinations. For each geometry+slot that fails at ANY tested combination, the recommended size is the maximum of all recommended sizes across all failing combinations for that slot.

**Rationale:** A geometry author wants a single size adjustment per slot that fixes ALL edge reveals across all compatible cameras, aspect ratios, and reasonable speeds. Taking the maximum ensures one fix resolves all failures.

### D7: Visual Review Checklist for Rotated Planes

**Decision:** Rotated planes (floor, ceiling, walls) that are skipped by OBJ-040's sampling are collected into a `visualReviewRequired` list. Each entry names the geometry, slot, reason for skipping, relevant camera paths, and whether OBJ-041's analytical check passed. This checklist drives the Director Agent visual review workflow.

**Rationale:** OBJ-040 D1 explicitly states that rotated planes are validated through the Director Agent tuning workflow. OBJ-069 generates the checklist; the actual visual review happens during OBJ-059-066 tuning rounds or as a follow-up.

### D8: Test Manifest Generation for Visual Review

**Decision:** `generateTestManifest()` produces a valid `Manifest` (per OBJ-004's type) with high-contrast placeholder images (e.g., bright red floor, bright green walls, bright blue backdrop on a black clear color) so edge reveals are instantly visible in a rendered clip. The manifest uses ALL of the geometry's slots (required and optional) with data URI images (solid-color PNGs) — no external asset files needed.

**Color assignment:** Slots are assigned visually distinct colors from a fixed palette. The palette is deterministic (same slot name always gets the same color) so repeated runs produce visually comparable results. Example palette: backdrop=blue, floor=red, sky=cyan, midground=green, subject=yellow, near_fg=magenta, left_wall=green, right_wall=orange, ceiling=purple, end_wall=white.

**Rationale:** The Director Agent (or human reviewer) needs to see edge reveals clearly. Solid-color planes against a black background make any edge gap immediately obvious. Data URIs eliminate file dependencies for test rendering.

### D9: Report Format — Markdown for Human + Structured Object for Programmatic Use

**Decision:** The harness returns a structured `EdgeRevealHarnessReport` object. `formatEdgeRevealReport()` converts it to Markdown. The test suite uses the structured object for assertions; the CLI/development workflow uses the Markdown for human review.

### D10: Aspect Ratio Label Mapping

**Decision:** Common aspect ratios are labeled for readability: `16/9` → `'16:9'`, `9/16` → `'9:16'`, `4/3` → `'4:3'`. Non-standard ratios use decimal notation (e.g., `'2.35:1'`). The label is purely cosmetic — all math uses the numeric ratio.

### D11: Compatibility Filtering via OBJ-041

**Decision:** The harness calls OBJ-041's `validateRegistryConsistency()` first. If there are consistency errors, they are included in the report header but do not prevent validation from proceeding on consistent pairs. Pair enumeration uses OBJ-041's `analyzeCoverage()` to get the compatibility matrix, then filters to bidirectionally compatible pairs (unless `compatibleOnly: false`).

**Rationale:** Reuses OBJ-041's existing analysis rather than reimplementing pair enumeration. The coverage analysis also feeds TC-08.

## Acceptance Criteria

### Harness Execution

- [ ] **AC-01:** `runEdgeRevealHarness` with a registry containing the stage geometry (OBJ-018) and `slow_push_forward`/`slow_pull_back` (OBJ-027) camera presets produces a report with at least 2 pairs tested.
- [ ] **AC-02:** Each pair is tested at both 16:9 and 9:16 aspect ratios (default config), producing at least 6 `PairValidationResult` entries per pair (2 aspects × 3 speeds).
- [ ] **AC-03:** For a pair where all facing-camera planes are oversized sufficiently (e.g., stage + static camera at speed=1.0), `pass` is `true`.
- [ ] **AC-04:** For a pair where a facing-camera plane is deliberately undersized (e.g., a test geometry with a small backdrop), `pass` is `false`, and `failures` contains an entry for the undersized slot.
- [ ] **AC-05:** Failed slots include `minimumSafeSize` and `recommendedSize` (with 1.05 margin) for facing-camera planes.
- [ ] **AC-06:** Failed slots with `cameraPassesThrough: true` have `minimumSafeSize: null` and `recommendedSize: null`, with a message indicating the structural incompatibility.

### Config Validation

- [ ] **AC-07:** `runEdgeRevealHarness` with `speeds: [0]` throws `RangeError` before any pair is tested.
- [ ] **AC-08:** `runEdgeRevealHarness` with `aspectRatios: [-1]` throws `RangeError` before any pair is tested.
- [ ] **AC-09:** `runEdgeRevealHarness` with `sampleCount: 0` throws `RangeError` before any pair is tested.

### Dual Validation

- [ ] **AC-10:** Both `samplingReport` (OBJ-040) and `oversizingResults` (OBJ-041) are populated for each combination.
- [ ] **AC-11:** If OBJ-040 says a facing-camera plane is safe but OBJ-041 says it's insufficient, the pair is marked as `pass: true` (OBJ-040 takes precedence for facing-camera planes). The facing-camera plane does NOT appear in `failures`.
- [ ] **AC-12:** If OBJ-041 says a rotated axis-aligned plane is insufficient, the pair is marked as `pass: false` even if OBJ-040 skipped that plane. The rotated plane appears in `failures` with `failedCheck: 'oversizing'`.

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

- [ ] **AC-20:** `formatEdgeRevealReport` produces valid Markdown with: executive summary, per-pair results table, failure details, visual review checklist, and recommended adjustments.
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

### Determinism

- [ ] **AC-30:** Running `runEdgeRevealHarness` twice with the same config and registries produces identical reports (C-05).

## Edge Cases and Error Handling

### Registry Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty geometry registry | Report has 0 pairs tested. No errors thrown. |
| Empty camera registry | Report has 0 pairs tested. No errors thrown. |
| Geometry with no bidirectionally compatible cameras | Pair count is 0 for that geometry. If `compatibleOnly: false`, pairs are tested but noted as non-compatible. |
| Registry consistency errors (OBJ-041) | Logged in report header. Validation proceeds on consistent pairs. |

### Validation Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Camera path where camera passes through a facing-camera plane (e.g., high speed push through subject) | OBJ-040 returns `safe: false`, `worstMargin: -Infinity`. OBJ-041 returns `cameraPassesThrough: true`. `SlotFailure.cameraPassesThrough: true` (OR of both sources). `minimumSafeSize: null`. Message recommends reducing speed or moving the plane. |
| Camera path where near_fg ends up behind camera at end position | OBJ-040 catches this at the sample point where distance <= 0. Reported as failure with `worstMargin: -Infinity`. |
| Plane exactly at the boundary of the camera's position envelope | OBJ-041 uses EPSILON=0.001 for distance. OBJ-040 catches with sampling. Both report marginal results. |
| All planes pass OBJ-040 but a rotated plane fails OBJ-041 | `pass: false` because OBJ-041 failure on axis-aligned rotated planes is authoritative. |
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
| Geometry with only required slots | Manifest includes only required slots (plus all optional slots per D8). All slots are included. |
| Geometry with all optional slots | Manifest includes ALL slots (required and optional). |
| Geometry with 0 required slots | Manifest includes all optional slots. If no slots at all, manifest has empty `planes` record. |

## Test Strategy

### Unit Tests

**Harness logic tests (with mock registries):**

1. **Basic pair enumeration:** Register 2 geometries and 3 cameras with known compatibility. Verify the harness tests the correct number of pairs.

2. **Pass case:** Mock geometry with oversized planes and a static camera. All results should be `pass: true`, no failures, no adjustments.

3. **Facing-camera failure case:** Mock geometry with a deliberately small backdrop (e.g., size [10, 10] when the frustum needs [50, 30]). Verify `pass: false`, `failures` contains the backdrop slot, `minimumSafeSize` and `recommendedSize` are populated.

4. **Camera-passes-through case:** Mock geometry with subject at Z=-5, camera with maxDisplacementZ=20 starting at Z=5 (envelope reaches Z=-15, past subject). Verify `cameraPassesThrough: true`, `minimumSafeSize: null`, `recommendedSize: null`.

5. **Rotated plane skipping:** Include a floor slot. Verify it appears in `skippedSlots` and `visualReviewRequired`.

6. **OBJ-040/OBJ-041 precedence (D2/D4):** Mock a facing-camera plane that passes OBJ-040 sampling but fails OBJ-041 analytical. Verify `pass: true` and the plane does NOT appear in `failures`.

7. **OBJ-041 rotated plane failure:** Mock a floor plane that fails OBJ-041 oversizing. Verify `pass: false` even though OBJ-040 skipped it. Verify `failedCheck: 'oversizing'`.

8. **Multiple speeds:** Verify a plane that passes at speed=0.5 but fails at speed=1.5 results in `allPassed: false` for the pair.

9. **Aggregated adjustments:** Two camera paths cause the same slot to fail with different minimum sizes. Verify `recommendedAdjustments` uses the larger of the two.

10. **Aspect ratio sensitivity:** A plane that passes at 16:9 but fails at 9:16 (or vice versa). Verify per-combination results are correct.

11. **Determinism:** Run twice, compare reports for identity.

12. **Empty registries:** Verify no errors, 0 pairs tested.

13. **Config validation:** Verify `RangeError` for speeds containing 0, negative aspectRatios, sampleCount < 1.

**Report formatting tests:**

14. Verify `formatEdgeRevealReport` produces Markdown containing expected section headers (executive summary, per-pair results, failure details, visual review checklist, recommended adjustments).

15. Verify the Markdown includes geometry and camera names in the results table.

16. Verify the Markdown includes the run timestamp.

**Test manifest generation tests:**

17. Verify manifest has correct `version`, `composition` (width, height, fps), and `scenes` array with one scene.

18. Verify each slot in the geometry has a corresponding entry in the manifest's `planes` record.

19. Verify all plane `src` values are data URIs (`data:image/png;base64,...`).

20. Verify distinct colors per slot (data URIs for different slots are different).

21. Verify the manifest passes OBJ-004 Zod schema validation.

22. Verify optional geometry slots are included in the manifest.

### Integration Tests (with real registries)

23. **Stage + push/pull:** Load real stage geometry (OBJ-018) and push/pull presets (OBJ-027). Run harness at default config. Verify all facing-camera planes pass at speed=1.0, both aspect ratios. This is the core TC-03 validation.

24. **Stage + static:** Stage geometry with static camera (OBJ-026). All planes should trivially pass (zero displacement).

25. **Stage + gentle_float:** Stage with gentle_float (OBJ-031). Verify results.

26. **All verified geometries × all verified cameras:** Run harness against all currently verified geometries and cameras. Document pass/fail status. This is the comprehensive TC-03 validation for the implemented set.

27. **Generate and validate test manifests:** Generate test manifests for all bidirectionally compatible pairs. Validate each against the manifest schema (OBJ-016). Optionally render a subset via OBJ-035 and inspect output.

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
| **OBJ-041** (`src/validation/spatial-compatibility.ts`) | `checkOversizingSufficiency`, `validateRegistryConsistency`, `analyzeCoverage`, types (`OversizingCheckResult`, `CoverageAnalysis`) | Analytical oversizing validation for all planes including rotated. Registry consistency pre-check. Coverage matrix for pair enumeration. |
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

---

## Changes from Round 1 → Round 2 (addressing Challenger's issues)

**Issue 1 (Major) — `pass` criterion contradiction:** Rewrote `PairValidationResult.pass` comment with an explicit 4-point criteria list that incorporates the D4 precedence rule. Added clarification to `failures` that facing-camera planes passing OBJ-040 do not appear there even if OBJ-041 fails them. Added step 4c to the `runEdgeRevealHarness` algorithm description making the precedence rule explicit in the execution flow.

**Issue 2 (Major) — `generateTestManifest` return type and dependency:** Changed return type from `object` to `Manifest` (imported from `../manifest/schema`). Added OBJ-004 to the dependency table with explanation. Updated AC-25 to reference this typed return.

**Issue 3 (Minor) — `cameraPassesThrough` source ambiguity:** Added explicit JSDoc to `SlotFailure.cameraPassesThrough` stating it is the OR of OBJ-041's `cameraPassesThrough: true` and OBJ-040's view-axis distance <= 0 at any sample point.

**Issue 4 (Minor) — Config validation location:** Added a **Config validation** paragraph to the `runEdgeRevealHarness` JSDoc specifying that validation happens at entry before any pairs are tested. Added `@throws RangeError` to the JSDoc. Added three new acceptance criteria (AC-07, AC-08, AC-09) and a new unit test (test 13).

**Issue 5 (Minor) — `failedCheck` for rotated planes:** Added clarifying comment to `SlotFailure.failedCheck` for the `'oversizing'` value: "This includes cases where OBJ-040 skipped the plane (rotated) and only OBJ-041 was applicable."

---

I believe all five issues are now resolved. Challenger, please verify and approve if satisfied.

---

## Round 4 — spec_challenger

I've verified all five Round 2 issues against the revised spec:

- **Issue 1 (pass criterion):** Fixed. The 4-point criteria list in `pass` and the `failures` clarification are structurally present and consistent with D4. ✓
- **Issue 2 (return type + dependency):** Fixed. `Manifest` import present, return type changed, OBJ-004 in dependency table. ✓
- **Issue 3 (cameraPassesThrough source):** Fixed. JSDoc explicitly states OR of both sources. ✓
- **Issue 4 (config validation):** Fixed. JSDoc, @throws, AC-07/08/09, test 13 all present. ✓
- **Issue 5 (failedCheck for rotated):** Fixed. Clarifying comment added. ✓

All prior issues are resolved. Two new issues found in this pass:

---

## Issue 6 — **Major**: D5 contradicts `SlotFailure.minimumSafeSize` type comment for rotated planes

D5 states:

> For rotated planes that fail OBJ-041's analytical check, the `requiredSize` from `OversizingCheckResult` is used directly (already conservative). **`minimumSafeSize` is set to the `requiredSize`**, and `recommendedSize` is `requiredSize * 1.05`.

But `SlotFailure.minimumSafeSize` says:

> Minimum safe size computed by OBJ-040's `computeMinimumFacingPlaneSize` (for facing-camera planes). **Null for rotated planes** or camera-passes-through cases.

These directly contradict. An implementer has two conflicting instructions for rotated-plane failures: populate `minimumSafeSize` from OBJ-041's `requiredSize`, or set it to `null`.

**Proposed fix:** Pick one. I recommend keeping the type comment's "null for rotated planes" behavior for `minimumSafeSize` (since the field name references OBJ-040's function, which doesn't apply to rotated planes), and instead surfacing OBJ-041's `requiredSize` through the existing `currentSize` vs a new field, or simply rewriting D5 to match. Specifically:

Update D5's second paragraph to:

> For rotated planes that fail OBJ-041's analytical check, `minimumSafeSize` is null (OBJ-040's `computeMinimumFacingPlaneSize` does not apply to rotated planes). `recommendedSize` is set to the `requiredSize` from `OversizingCheckResult` multiplied by 1.05. The `message` field describes the OBJ-041 failure and the required size.

And update `recommendedSize`'s JSDoc from "Null when minimumSafeSize is null" to:

```typescript
/**
 * Recommended adjusted size:
 * - For facing-camera planes: minimumSafeSize * 1.05 safety margin.
 * - For rotated planes: OBJ-041's requiredSize * 1.05.
 * - Null only for camera-passes-through cases.
 */
recommendedSize: Size2D | null;
```

This way `recommendedSize` is always actionable for fixable failures, while `minimumSafeSize` stays semantically accurate (it's the OBJ-040-derived value, null when OBJ-040 doesn't apply).

---

## Issue 7 — **Minor**: `EdgeRevealHarnessReport` has no field for registry consistency errors

D11 says: "If there are consistency errors, they are included in the report header." Algorithm step 2 says: "Log any consistency errors in the report header but proceed."

But `EdgeRevealHarnessReport` has no field to carry registry consistency errors. An implementer must either add an undocumented field or silently discard the results of `validateRegistryConsistency()`.

**Proposed fix:** Add a field:

```typescript
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
```

And import `SpatialValidationError` from OBJ-041.

---

Please address Issues 6 and 7, and I'll converge.

---

## Round 5 — spec_author

Both issues are valid. Here are the targeted fixes:

---

## Issue 6 Fix — D5 and `SlotFailure` field consistency

The challenger is right: `minimumSafeSize` is semantically tied to OBJ-040's `computeMinimumFacingPlaneSize`, so it should remain null for rotated planes. The actionable sizing data for rotated planes comes from OBJ-041's `requiredSize` and flows through `recommendedSize`.

**Revised D5:**

### D5: Minimum Safe Size Computation for Failures

**Decision:** When a facing-camera plane fails OBJ-040's sampling check, the harness calls `computeMinimumFacingPlaneSize()` from OBJ-040 to determine the exact minimum size, then applies a 1.05 safety margin (5%) as recommended by OBJ-040's JSDoc. The results are stored as `minimumSafeSize` and `recommendedSize` in the `SlotFailure`.

For rotated planes that fail OBJ-041's analytical check, `minimumSafeSize` is null — OBJ-040's `computeMinimumFacingPlaneSize` does not apply to rotated planes. `recommendedSize` is set to the `requiredSize` from `OversizingCheckResult` multiplied by 1.05. The `message` field describes the OBJ-041 failure and the required size.

For `cameraPassesThrough` failures (any orientation), both `minimumSafeSize` and `recommendedSize` are null — the problem is structural (camera trajectory intersects the plane), not a sizing issue.

**Revised `SlotFailure` fields:**

```typescript
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
```

**Impact on AC-05:** Already correct — "Failed slots include `minimumSafeSize` and `recommendedSize` (with 1.05 margin) for facing-camera planes." The phrase "for facing-camera planes" scopes `minimumSafeSize` correctly.

**New AC for rotated-plane failures:** Adding **AC-12a** (renumbering not needed, inserting after AC-12):

- [ ] **AC-12a:** For a rotated axis-aligned plane that fails OBJ-041 oversizing, `SlotFailure.minimumSafeSize` is `null`, and `SlotFailure.recommendedSize` is OBJ-041's `requiredSize * 1.05` (non-null, actionable).

---

## Issue 7 Fix — Registry consistency errors field

**Added to `EdgeRevealHarnessReport`:**

```typescript
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
```

This requires importing `SpatialValidationError` from OBJ-041, which is already in the dependency table.

**New AC:**

- [ ] **AC-31:** When registries have bidirectional consistency errors (e.g., geometry lists camera X but camera X doesn't list geometry), `report.registryConsistencyErrors` contains the errors from `validateRegistryConsistency()`. The harness still validates all consistent pairs.
- [ ] **AC-32:** When registries are fully consistent, `report.registryConsistencyErrors` is an empty array.

---

## Full Revised Specification

For clarity, here is the complete specification incorporating all fixes from Rounds 1-5:

---

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

### D3: Default Parameter Matrix — Aspect Ratios × Speeds × Offsets

**Decision:** Default test matrix:
- Aspect ratios: `[16/9, 9/16]` — landscape and portrait per C-04.
- Speeds: `[0.5, 1.0, 1.5]` — conservative, standard, moderately aggressive.
- Offsets: `[[0, 0, 0]]` — no offset by default.

This produces 6 combinations per pair (2 aspects × 3 speeds × 1 offset). With N pairs, total combinations = 6N.

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

**Color assignment:** Slots are assigned visually distinct colors from a fixed palette. The palette is deterministic (same slot name always gets the same color) so repeated runs produce visually comparable results. Example palette: backdrop=blue, floor=red, sky=cyan, midground=green, subject=yellow, near_fg=magenta, left_wall=green, right_wall=orange, ceiling=purple, end_wall=white.

**Rationale:** The Director Agent (or human reviewer) needs to see edge reveals clearly. Solid-color planes against a black background make any edge gap immediately obvious. Data URIs eliminate file dependencies for test rendering.

### D9: Report Format — Markdown for Human + Structured Object for Programmatic Use

**Decision:** The harness returns a structured `EdgeRevealHarnessReport` object. `formatEdgeRevealReport()` converts it to Markdown. The test suite uses the structured object for assertions; the CLI/development workflow uses the Markdown for human review.

### D10: Aspect Ratio Label Mapping

**Decision:** Common aspect ratios are labeled for readability: `16/9` → `'16:9'`, `9/16` → `'9:16'`, `4/3` → `'4:3'`. Non-standard ratios use decimal notation (e.g., `'2.35:1'`). The label is purely cosmetic — all math uses the numeric ratio.

### D11: Compatibility Filtering via OBJ-041

**Decision:** The harness calls OBJ-041's `validateRegistryConsistency()` first. Results are stored in `report.registryConsistencyErrors`. If there are consistency errors, validation proceeds on consistent pairs regardless. Pair enumeration uses OBJ-041's `analyzeCoverage()` to get the compatibility matrix, then filters to bidirectionally compatible pairs (unless `compatibleOnly: false`).

**Rationale:** Reuses OBJ-041's existing analysis rather than reimplementing pair enumeration. The coverage analysis also feeds TC-08. Storing consistency errors in the report ensures they're visible without blocking validation.

## Acceptance Criteria

### Harness Execution

- [ ] **AC-01:** `runEdgeRevealHarness` with a registry containing the stage geometry (OBJ-018) and `slow_push_forward`/`slow_pull_back` (OBJ-027) camera presets produces a report with at least 2 pairs tested.
- [ ] **AC-02:** Each pair is tested at both 16:9 and 9:16 aspect ratios (default config), producing at least 6 `PairValidationResult` entries per pair (2 aspects × 3 speeds).
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

28. **All verified geometries × all verified cameras:** Run harness against all currently verified geometries and cameras. Document pass/fail status. This is the comprehensive TC-03 validation for the implemented set.

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

---

## Changes from Round 3 → Round 5 (addressing Challenger's Issues 6 and 7)

**Issue 6 (Major) — D5/minimumSafeSize contradiction for rotated planes:**
- Rewrote D5 to explicitly state `minimumSafeSize` is null for rotated planes, while `recommendedSize` is populated from OBJ-041's `requiredSize * 1.05`.
- Updated `SlotFailure.recommendedSize` JSDoc to document three cases: facing-camera (from minimumSafeSize), rotated (from OBJ-041 requiredSize), camera-passes-through (null).
- Added AC-12a testing the rotated plane case specifically.
- Updated unit test 7 to verify `minimumSafeSize: null` and `recommendedSize` non-null for rotated plane failures.
- Updated edge case table entry for "All planes pass OBJ-040 but a rotated plane fails OBJ-041" to document both fields.

**Issue 7 (Minor) — Missing registryConsistencyErrors field:**
- Added `registryConsistencyErrors: SpatialValidationError[]` field to `EdgeRevealHarnessReport`.
- Added `SpatialValidationError` to OBJ-041 import list.
- Updated D11 to reference the new field.
- Updated algorithm step 2 to say "Store results in report.registryConsistencyErrors."
- Updated `formatEdgeRevealReport` JSDoc to include "Registry consistency errors (if any)" in its output sections.
- Added AC-31 and AC-32 for the new field.
- Added unit test 14 for registry consistency errors in report.
- Added unit test 18 for Markdown formatting of consistency errors.
- Updated AC-20 to include "registry consistency errors (if any)" in the Markdown sections list.
- Updated empty registries edge case to note `registryConsistencyErrors` is empty.

---

Challenger, both issues are addressed. Please verify and approve if satisfied.

---

## Round 6 — spec_challenger

I've verified both Issue 6 and Issue 7 fixes structurally:

**Issue 6 verification:**
- D5 now explicitly states `minimumSafeSize` is null for rotated planes ✓
- `SlotFailure.minimumSafeSize` JSDoc: "Null for rotated planes (OBJ-040 does not apply)" ✓
- `SlotFailure.recommendedSize` JSDoc: three-case breakdown (facing-camera / rotated / camera-passes-through) ✓
- AC-12a tests the rotated case specifically ✓
- Unit test 7 checks `minimumSafeSize: null` + `recommendedSize` non-null ✓
- Edge case table consistent ✓
- No remaining contradiction between D5 and the type comments ✓

**Issue 7 verification:**
- `registryConsistencyErrors: SpatialValidationError[]` present in `EdgeRevealHarnessReport` ✓
- `SpatialValidationError` in import list ✓
- D11 references the field ✓
- Algorithm step 2 says "Store results in report.registryConsistencyErrors" ✓
- AC-31/AC-32 test the field ✓
- Unit tests 14 and 18 cover it ✓
- AC-20 includes it in Markdown sections ✓

One minor note for the record — D8's example color palette assigns green to both `midground` and `left_wall`. AC-24 requires distinct colors per slot, so the implementation must use a palette with no duplicates. This is clear from the AC; the example palette is illustrative. Not blocking.

All seven issues from Rounds 2, 4, and 4 are resolved. The spec is implementable, constraint-compliant, vocabulary-clean, and well-integrated with its dependencies.

CONCLUSION:

The specification for OBJ-069 — Edge Reveal Systematic Validation — is agreed. It defines a synchronous validation harness (`runEdgeRevealHarness`) that enumerates all bidirectionally-compatible geometry+camera pairs, runs dual validation (OBJ-040 sampling for facing-camera planes, OBJ-041 analytical for all planes including rotated), produces structured reports with actionable size adjustment recommendations, and generates test manifests for Director Agent visual review of rotated planes. Key design decisions: OBJ-040 is authoritative for facing-camera planes (D4 precedence rule); rotated plane failures use OBJ-041's `requiredSize * 1.05` for `recommendedSize` while `minimumSafeSize` stays null (D5); registry consistency errors are stored in the report without blocking validation (D11). The spec includes 32 acceptance criteria, comprehensive edge cases, and a test strategy with both unit tests (mock registries) and integration tests (real stage geometry + push/pull presets).

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me check the current state of the node directory and meta.json:
[Tool: Read]
  Input: {
  "file_path": "/home/user/repos/depthkit/nodes/OBJ-069/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "ls -la nodes/OBJ-069/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-069 node directory exists"
}

[Tool: Bash]
  Input: {
  "command": "pwd",
  "description": "Check current working directory"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:29 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   841 Mar 22 19:29 meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-069/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-069",
     3→  "description": "Edge reveal systematic validation -- test all geometry+camera combinations for edge reveals with the oversizing system applied. Verify that no camera path reveals the edge of any plane during its full motion range. Requires concrete geometry (OBJ-018) and camera (OBJ-027) implementations plus the oversizing system (OBJ-040) and compatibility rules (OBJ-041). Addresses TC-03 (perspective projection convincing).",
     4→  "category": "tuning",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-018", "OBJ-027", "OBJ-040", "OBJ-041", "OBJ-035"],
     9→  "visual_status": "needs_tuning",
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 tuning. High priority. Fixed deps per Round 2 Issue 3 to include concrete implementations."
    12→}
    13→
Good. Now let me write the output.md and update meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-069/output.md",
  "content": "# Specification: OBJ-069 \u2014 Edge Reveal Systematic Validation\n\n## Summary\n\nOBJ-069 defines the **systematic edge-reveal validation harness** for depthkit: a test module and runner that enumerates every bidirectionally-compatible geometry+camera pair across the implemented registries, runs both analytical (OBJ-041) and sampling-based (OBJ-040) edge-reveal checks at standard aspect ratios and speed ranges, produces a structured report, and \u2014 where failures are found \u2014 computes and documents the minimum plane size adjustments required. For rotated planes (which OBJ-040 skips), the harness generates test render manifests for Director Agent visual review via OBJ-035. This objective addresses TC-03 (perspective projection produces convincing 2.5D) by validating that the spatial authoring vocabulary never reveals plane edges during normal use.\n\n## Interface Contract\n\n### Validation Harness Module\n\n```typescript\n// src/validation/edge-reveal-harness.ts\n\nimport type { GeometryRegistry, SceneGeometry } from '../scenes/geometries/types';\nimport type { CameraPathRegistry, CameraPathPreset, CameraParams } from '../camera/types';\nimport type {\n  GeometryEdgeRevealReport,\n  PlaneEdgeRevealResult,\n} from '../spatial/edge-reveal';\nimport type {\n  OversizingCheckResult,\n  SpatialValidationError,\n} from './spatial-compatibility';\nimport type { Size2D, Vec3 } from '../spatial/types';\nimport type { Manifest } from '../manifest/schema';\n\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n// Configuration\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-069/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-069/meta.json",
  "content": "{\n  \"id\": \"OBJ-069\",\n  \"description\": \"Edge reveal systematic validation -- test all geometry+camera combinations for edge reveals with the oversizing system applied. Verify that no camera path reveals the edge of any plane during its full motion range. Requires concrete geometry (OBJ-018) and camera (OBJ-027) implementations plus the oversizing system (OBJ-040) and compatibility rules (OBJ-041). Addresses TC-03 (perspective projection convincing).\",\n  \"category\": \"tuning\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:00:00Z\",\n  \"depends_on\": [\"OBJ-018\", \"OBJ-027\", \"OBJ-040\", \"OBJ-041\", \"OBJ-035\"],\n  \"visual_status\": \"needs_tuning\",\n  \"tuning_rounds\": 0,\n  \"spec_status\": \"specified\",\n  \"deliberation_rounds\": 6,\n  \"notes\": \"Tier 5 tuning. High priority. Fixed deps per Round 2 Issue 3 to include concrete implementations. Spec defines a systematic edge-reveal validation harness (runEdgeRevealHarness) with dual validation: OBJ-040 sampling (authoritative for facing-camera planes) + OBJ-041 analytical (authoritative for rotated planes). Produces structured reports with actionable size adjustments and visual review checklists for Director Agent workflow. Also includes generateTestManifest for rendering test clips with solid-color data URI images.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-069/meta.json has been updated successfully.
Now commit:
[Tool: Bash]
  Input: {
  "command": "git status -s nodes/OBJ-069/",
  "description": "Check git status for OBJ-069 files"
}
[Tool Result]  M nodes/OBJ-069/meta.json
?? nodes/OBJ-069/output.md

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Check recent commit style"
}
[Tool Result] f281cf8 spec(OBJ-039): Three.js page-side geometry instantiation
de8ffe4 OBJ-071: Spec for SKILL.md geometry and camera reference sections
3c78409 OBJ-077: End-to-end integration test plan specification
eb84b19 spec(OBJ-048): error handling and reporting strategy — ErrorReport for programmatic consumers, classifyError/generateSuggestions utilities, DEGRADATION_RULES exported constant, consolidated error taxonomy
7788a22 spec(OBJ-047): Library API — importable programmatic interface for depthkit

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-069/output.md nodes/OBJ-069/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-069): Edge reveal systematic validation harness\n\nDefines runEdgeRevealHarness that enumerates all bidirectionally-compatible\ngeometry+camera pairs, runs dual validation (OBJ-040 sampling for facing-camera\nplanes, OBJ-041 analytical for rotated planes), and produces structured reports\nwith actionable size adjustments. Includes generateTestManifest for Director\nAgent visual review of rotated planes using solid-color data URI images.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-069 spec files"
}
[Tool Result] [master 8c0844d] spec(OBJ-069): Edge reveal systematic validation harness
 2 files changed, 805 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-069/output.md
The specification for OBJ-069 has been written to `nodes/OBJ-069/output.md`, `meta.json` updated, and committed. 

**Deliberation summary:** 6 rounds, 7 issues raised and resolved:
- **Round 2:** Issue 1 (major: `pass` criterion contradicted D4 precedence rule), Issue 2 (major: `generateTestManifest` returned `object` not `Manifest`), Issue 3 (minor: `cameraPassesThrough` source ambiguity), Issue 4 (minor: config validation unspecified), Issue 5 (minor: `failedCheck` for rotated planes unclear)
- **Round 4:** Issue 6 (major: D5 contradicted `minimumSafeSize` JSDoc for rotated planes), Issue 7 (minor: missing `registryConsistencyErrors` field in report type)
