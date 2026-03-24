# Specification: Depth Model — Semantic Slot Taxonomy and Override System (OBJ-007)

## Summary

OBJ-007 defines the **depth model**: the semantic mapping from named slot labels to 3D spatial transforms (position, rotation, size) that scene geometries use to place planes in the Three.js scene. It establishes a **default slot taxonomy** (sky, back_wall, midground, subject, near_fg) with default Z-positions per seed Section 4.1, defines the **rules and types that govern per-geometry slot sets** (e.g., tunnel uses floor/ceiling/walls instead of the default taxonomy), and specifies the **`PlaneOverride` escape hatch** in the manifest for per-scene spatial tweaks without hard-coding the depth model (AP-08). This module provides the slot contract that all scene geometries implement (OBJ-005) and that manifest validation (OBJ-010) enforces.

## Interface Contract

### Core Types

```typescript
// src/spatial/depth-model.ts

import type { Vec3, EulerRotation, Size2D } from './types';

/**
 * Slot names must match: lowercase alpha start, then lowercase
 * alphanumeric or underscores. This prevents empty strings, spaces,
 * leading digits, prototype-polluting keys, and non-ASCII characters.
 *
 * Pattern: /^[a-z][a-z0-9_]*$/
 *
 * This is a branded type alias for documentation. Runtime validation
 * is performed by validateSlotName() and validatePlaneSlots().
 */
export type SlotName = string;

/** Regex for valid slot names. Exported for reuse by OBJ-005 and OBJ-010. */
export const SLOT_NAME_PATTERN: RegExp; // = /^[a-z][a-z0-9_]*$/

/**
 * Validates a single slot name against SLOT_NAME_PATTERN.
 * @returns true if the name is valid, false otherwise.
 */
export function isValidSlotName(name: string): name is SlotName;

/**
 * A single depth slot definition: the spatial contract for one named
 * plane position within a scene geometry.
 *
 * This supersedes the seed's `PlaneSlot` sketch (Section 8.6).
 * Additions beyond the seed sketch:
 * - `name`: explicit slot identifier (seed sketch used Record keys only)
 * - `promptGuidance`: per-slot image generation guidance (seed Section 4.7)
 * - `expectsAlpha`: alpha channel requirement flag (seed Section 4.8)
 * - `renderOrder`: Three.js draw-order hint for correct transparency compositing
 */
export interface DepthSlot {
  /** Slot name. Must match SLOT_NAME_PATTERN. */
  readonly name: SlotName;

  /** Default position in world space [x, y, z]. */
  readonly position: Vec3;

  /** Default rotation in radians [rx, ry, rz]. */
  readonly rotation: EulerRotation;

  /** Default plane size in world units [width, height]. */
  readonly size: Size2D;

  /** Whether this slot must be filled in the manifest. */
  readonly required: boolean;

  /**
   * Human-readable description for SKILL.md and error messages.
   * Describes what kind of image content belongs in this slot.
   */
  readonly description: string;

  /**
   * Suggested image generation prompt guidance for this slot type.
   * Used by SKILL.md to help LLM authors generate appropriate images.
   */
  readonly promptGuidance: string;

  /**
   * Whether images in this slot typically need alpha transparency.
   * Informs the asset pipeline (background removal decisions).
   */
  readonly expectsAlpha: boolean;

  /**
   * Render order hint. Lower values render first (farther back).
   * Used by the renderer to ensure correct draw ordering for
   * transparent materials. Not a Z-position — purely a draw-order hint.
   */
  readonly renderOrder: number;
}

/**
 * The complete slot set for a scene geometry.
 * Maps slot names to their spatial definitions.
 * All keys must be valid SlotNames matching SLOT_NAME_PATTERN.
 */
export type SlotSet = Readonly<Record<SlotName, DepthSlot>>;
```

### Default Slot Taxonomy

```typescript
// src/spatial/depth-model.ts (continued)

/**
 * The default depth slot taxonomy from seed Section 4.1.
 * Used by geometries that follow the standard layered arrangement
 * (e.g., stage, diorama, close_up). Geometries may use all, some,
 * or none of these slots — the default taxonomy is a convenience
 * grab-bag, not a mandatory complete set.
 *
 * Geometries that define fundamentally different spatial structures
 * (e.g., tunnel, canyon) declare their own SlotSet and do NOT use
 * these defaults.
 *
 * SIZE ASSUMPTION: All sizes are pre-computed assuming the camera
 * starts at DEFAULT_CAMERA.position ([0, 0, 5]) from OBJ-003, with
 * FOV=50 degrees and aspect ratio 16:9. Geometries that use a different
 * camera start position MUST recompute sizes using OBJ-003's
 * computePlaneSize(). These values are approximate starting points
 * subject to validation when the first geometries and camera paths
 * are built (OBJ-018+, OBJ-040).
 */
export const DEFAULT_SLOT_TAXONOMY: SlotSet = {
  sky: {
    name: 'sky',
    position: [0, 0, -50],
    rotation: [0, 0, 0],
    size: [120, 70],
    required: true,
    description: 'Sky, space, distant gradient. Large plane filling the far background.',
    promptGuidance: 'Wide atmospheric scene, no foreground objects, expansive horizon or sky.',
    expectsAlpha: false,
    renderOrder: 0,
  },
  back_wall: {
    name: 'back_wall',
    position: [0, 0, -30],
    rotation: [0, 0, 0],
    size: [70, 40],
    required: false,
    description: 'Distant landscape, city skyline, or environmental backdrop.',
    promptGuidance: 'Environmental backdrop element, atmospheric perspective, slightly hazy.',
    expectsAlpha: false,
    renderOrder: 1,
  },
  midground: {
    name: 'midground',
    position: [0, 0, -15],
    rotation: [0, 0, 0],
    size: [40, 25],
    required: false,
    description: 'Buildings, terrain, environmental props at middle distance.',
    promptGuidance: 'Mid-distance environmental element. May need transparent background if isolated object.',
    expectsAlpha: false,
    renderOrder: 2,
  },
  subject: {
    name: 'subject',
    position: [0, 0, -5],
    rotation: [0, 0, 0],
    size: [12, 12],
    required: true,
    description: 'Primary subject (person, object, animal). Upright plane facing camera.',
    promptGuidance: 'Primary subject, isolated on transparent background, dramatic lighting.',
    expectsAlpha: true,
    renderOrder: 3,
  },
  near_fg: {
    name: 'near_fg',
    position: [0, 0, -1],
    rotation: [0, 0, 0],
    size: [25, 16],
    required: false,
    description: 'Foreground foliage, particles, framing elements. Close to camera.',
    promptGuidance: 'Foreground element, transparent background, may be partially blurred/bokeh.',
    expectsAlpha: true,
    renderOrder: 4,
  },
} as const;
```

### Slot Override Types

```typescript
// src/spatial/depth-model.ts (continued)

/**
 * Per-plane spatial override that a manifest author can specify
 * to adjust a slot's default position/rotation/size without
 * defining a custom geometry. Per AP-08: "do not hard-code the
 * depth model."
 *
 * All fields are optional — only specified fields override the
 * geometry's defaults. Unspecified fields retain the geometry's
 * default values.
 *
 * This type is imported by OBJ-010 (manifest schema) to compose
 * the full manifest plane entry type (which adds `src` and other
 * manifest-specific fields).
 */
export interface PlaneOverride {
  /** Override position [x, y, z] in world units. */
  readonly position?: Vec3;

  /** Override rotation [rx, ry, rz] in radians. */
  readonly rotation?: EulerRotation;

  /** Override size [width, height] in world units. */
  readonly size?: Size2D;

  /**
   * Override opacity [0.0-1.0]. Default: 1.0.
   * Enables per-plane transparency for artistic effects
   * (e.g., ghostly foreground, semi-transparent overlays).
   * Static per scene — per-frame animation is deferred (OQ-01).
   */
  readonly opacity?: number;
}

/**
 * The fully resolved spatial state of a plane, after merging
 * geometry defaults with manifest overrides.
 */
export interface ResolvedSlot {
  readonly position: Vec3;
  readonly rotation: EulerRotation;
  readonly size: Size2D;
  readonly opacity: number;
  readonly renderOrder: number;
}
```

### Validation and Resolution Functions

```typescript
// src/spatial/depth-model.ts (continued)

/**
 * Result of validating manifest plane keys and overrides against
 * a geometry's slot set.
 */
export interface SlotValidationResult {
  /** True if validation passed with no errors. */
  readonly valid: boolean;

  /**
   * Error messages (empty if valid).
   * Ordering: missing required slots first (alphabetical by slot name),
   * then invalid slot name format errors (alphabetical by key name),
   * then unknown keys (alphabetical by key name), then override
   * validation errors (alphabetical by slot name).
   *
   * A key that fails SLOT_NAME_PATTERN validation is reported as a
   * format error ONLY, not additionally as an unknown key.
   */
  readonly errors: readonly string[];

  /**
   * Warning messages (non-fatal issues).
   * Ordering: alphabetical by slot name.
   */
  readonly warnings: readonly string[];
}

/**
 * Validates that a manifest scene's plane keys match its geometry's
 * slot declarations and that any overrides are within safe ranges.
 *
 * @param planes - Map from provided slot names to their optional
 *   PlaneOverride values. The caller (OBJ-010 manifest validation)
 *   extracts this from the manifest's plane entries. This function
 *   is manifest-schema-agnostic — it does not know about `src` or
 *   other manifest-specific fields.
 * @param slots - The geometry's slot set (from the geometry's
 *   declaration, provided via OBJ-005's registry).
 * @param geometryName - For error messages.
 * @returns SlotValidationResult with errors and warnings.
 *
 * Checks performed:
 * 1. All keys in `planes` are valid SlotNames (match SLOT_NAME_PATTERN).
 *    Keys failing the format check are reported as format errors ONLY,
 *    not additionally as unknown keys.
 * 2. All required slots in `slots` have a corresponding key in `planes`.
 * 3. No keys in `planes` exist that aren't in `slots` (excluding keys
 *    already reported as format errors).
 * 4. For each plane with a PlaneOverride:
 *    - opacity, if present, is in [0.0, 1.0] and finite.
 *    - position components, if present, are finite (not NaN/Infinity).
 *    - rotation components, if present, are finite.
 *    - size components, if present, are positive (> 0) and finite.
 * 5. Missing optional slots produce warnings.
 */
export function validatePlaneSlots(
  planes: Readonly<Record<string, PlaneOverride | undefined>>,
  slots: SlotSet,
  geometryName: string
): SlotValidationResult;

/**
 * Resolves a manifest plane's effective spatial transform by
 * merging the geometry's default slot values with any overrides.
 *
 * For each field in PlaneOverride:
 *   - If present in override: use the override value.
 *   - If absent: use the geometry's default from the DepthSlot.
 *
 * renderOrder always comes from the DepthSlot — it is not
 * overridable via the manifest (not exposed in PlaneOverride).
 *
 * @param slot - The geometry's default slot definition.
 * @param override - The manifest's optional overrides (may be undefined).
 * @returns The resolved spatial state.
 */
export function resolveSlotTransform(
  slot: DepthSlot,
  override?: PlaneOverride
): ResolvedSlot;
```

### Module Exports

```typescript
// Added to src/spatial/index.ts barrel export

export {
  // Types
  type SlotName,
  type DepthSlot,
  type SlotSet,
  type PlaneOverride,
  type ResolvedSlot,
  type SlotValidationResult,

  // Constants
  SLOT_NAME_PATTERN,
  DEFAULT_SLOT_TAXONOMY,

  // Functions
  isValidSlotName,
  validatePlaneSlots,
  resolveSlotTransform,
};
```

## Design Decisions

### D1: Two-tier slot model — default taxonomy + per-geometry slot sets

The seed (Section 4.1) defines a default 5-slot taxonomy (sky, back_wall, midground, subject, near_fg) but also notes that geometries like tunnel need entirely different slot names (floor, ceiling, left_wall, right_wall, end_wall). Rather than forcing all geometries into the default taxonomy, each geometry declares its own `SlotSet`. The `DEFAULT_SLOT_TAXONOMY` is a convenience for geometries that follow the standard layered arrangement (stage, diorama, close_up) — they can spread it and pick slots from it. Geometries like tunnel define completely independent slot sets.

The seed explicitly asks (Section 4.1): "whether scene geometries should define their own slot sets (e.g., a tunnel needs `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall` — 5 slots but different ones)." The answer is yes. A tunnel's `floor` and a stage's `sky` have nothing in common spatially. Forcing both into the same taxonomy would produce incorrect defaults and confusing SKILL.md documentation.

**Constraint alignment:** Seed C-06 (blind-authorable). The LLM picks a geometry name and fills its declared slots. The slot names are geometry-specific and self-documenting.

### D2: DepthSlot supersedes seed Section 8.6's PlaneSlot sketch

The seed defines a `PlaneSlot` interface in Section 8.6. OBJ-007's `DepthSlot` is the refined version. Fields added beyond the seed sketch:
- `name`: explicit identifier (seed sketch used Record keys only).
- `promptGuidance`: per-slot image generation guidance (seed Section 4.7).
- `expectsAlpha`: alpha channel requirement flag (seed Section 4.8, OQ-02).
- `renderOrder`: Three.js draw-order hint for correct transparency compositing.

The seed's `SceneGeometry` interface (Section 8.6) — which bundles slots with camera compatibility, fog, and description — is **not** part of OBJ-007. That interface is a geometry registration concern belonging to OBJ-005 (Scene geometry base module). OBJ-007 defines the slot types and rules; OBJ-005 defines how geometries register their compliance with those types.

### D3: PlaneOverride as partial merge, not replacement

The `PlaneOverride` in the manifest lets authors adjust individual spatial properties without replacing the entire slot definition. If only `position` is overridden, rotation and size retain the geometry's defaults. This satisfies AP-08 ("do not hard-code the depth model") by allowing escape-hatch tweaks while keeping the 90% case zero-config.

### D4: Override validation constrains values to mathematical safety, not artistic judgment

`validatePlaneSlots` checks override values for safety:
- `opacity` must be in `[0.0, 1.0]` and finite.
- `position` components must be finite numbers (not NaN/Infinity).
- `rotation` components must be finite numbers.
- `size` components must be positive (> 0) and finite.

It does NOT constrain overrides to "reasonable" spatial ranges (e.g., it won't reject a plane at Z=-1000). That's the author's intent. But it rejects values that would produce rendering errors.

**Constraint alignment:** AP-08 says don't hard-code; C-10 says validate before rendering. The compromise: validate mathematical correctness (finite, positive where needed), not artistic judgment.

### D5: renderOrder is metadata, not Z-position, and not overridable

Three.js requires explicit render ordering for correct transparency compositing. Planes with alpha need to be drawn back-to-front. `renderOrder` is a hint from the depth model, set by the geometry author based on the slot's intended depth position. It is intentionally NOT part of `PlaneOverride` — exposing it to LLM authors would violate C-06 (blind-authorable), since an author would need to understand WebGL draw order to use it correctly.

### D6: promptGuidance and expectsAlpha belong in the depth model

These fields are consumed by SKILL.md generation (OBJ-051) and the asset pipeline (OBJ-053), not by the renderer. Including them in `DepthSlot` keeps all slot-related knowledge in one place rather than scattering it across separate prompt-template files. Seed Section 4.7 defines per-slot prompt guidance; seed Section 4.8 notes alpha requirements vary by slot.

### D7: No per-frame opacity animation in V1

`PlaneOverride.opacity` is static (set once per scene). Per-frame opacity animation (OQ-01) is deferred. The manifest schema supports a static opacity value, which handles the common cases (semi-transparent fog layer, faded overlay). Animation would require a keyframe system adding significant schema and engine complexity.

### D8: Slot names are constrained strings, not an enum

Slot names are `string` keys matching `/^[a-z][a-z0-9_]*$/` — lowercase alphanumeric with underscores, starting with a letter. This prevents empty strings, spaces, leading digits, prototype-polluting keys (`__proto__`, `constructor`), and non-ASCII characters. There is no global enum of all possible slot names, because each geometry defines its own slot names. String keys with per-geometry validation (via `SlotSet`) and the name pattern constraint achieve type safety at the manifest validation boundary without creating a maintenance bottleneck.

### D9: Default slot sizes are tied to DEFAULT_CAMERA.position

The sizes in `DEFAULT_SLOT_TAXONOMY` are pre-computed assuming `DEFAULT_CAMERA.position` from OBJ-003 ([0, 0, 5]), FOV=50 degrees, and aspect ratio 16:9. For the `sky` slot at Z=-50 (distance 55 from camera):
- `visibleHeight = 2 * 55 * tan(25 degrees) ~= 51.27`
- `visibleWidth ~= 51.27 * (16/9) ~= 91.14`

The defined size of `[120, 70]` provides approximately 32% oversize horizontally and 37% vertically. These are approximate starting values — the oversize distribution should be validated against actual camera motion ranges during geometry tuning (OBJ-018+, OBJ-040). Any geometry that uses the default taxonomy slots but positions its camera differently from `DEFAULT_CAMERA.position` **must** recompute sizes using OBJ-003's `computePlaneSize()`.

### D10: OBJ-007 owns slot types and rules; OBJ-005 owns the geometry registry

This module defines `DepthSlot`, `SlotSet`, `PlaneOverride`, `ResolvedSlot`, the `DEFAULT_SLOT_TAXONOMY`, and the validation/resolution functions. It does **not** define the geometry registration system (`GeometryRegistry`, `GeometrySlotDeclaration`) — those are OBJ-005 concerns. `validatePlaneSlots` accepts a `SlotSet` directly, keeping it registry-agnostic. OBJ-005 imports these types to define its registration contract; OBJ-010 imports from both OBJ-005 (registry lookup) and OBJ-007 (validation/resolution).

### D11: Manifest-schema-agnostic validation

`validatePlaneSlots` accepts `Record<string, PlaneOverride | undefined>`, not a manifest-specific type with `src` fields. The manifest plane type (which includes `src`, and composes `PlaneOverride` under an `override` key) is defined by OBJ-010 (manifest schema). OBJ-010's validation logic extracts the slot-name-to-override mapping from the manifest and passes it to `validatePlaneSlots`. This keeps OBJ-007 free of manifest schema concerns.

## Acceptance Criteria

- [ ] **AC-01:** `DEFAULT_SLOT_TAXONOMY` contains exactly 5 slots: `sky`, `back_wall`, `midground`, `subject`, `near_fg`, with Z-positions matching seed Section 4.1 (-50, -30, -15, -5, -1 respectively).
- [ ] **AC-02:** `DEFAULT_SLOT_TAXONOMY.sky.required` is `true`; `DEFAULT_SLOT_TAXONOMY.back_wall.required` is `false`; `DEFAULT_SLOT_TAXONOMY.midground.required` is `false`; `DEFAULT_SLOT_TAXONOMY.subject.required` is `true`; `DEFAULT_SLOT_TAXONOMY.near_fg.required` is `false`.
- [ ] **AC-03:** `isValidSlotName('sky')` returns `true`; `isValidSlotName('left_wall')` returns `true`; `isValidSlotName('back_wall_2')` returns `true`.
- [ ] **AC-04:** `isValidSlotName('')` returns `false`; `isValidSlotName('Left_Wall')` returns `false`; `isValidSlotName('123abc')` returns `false`; `isValidSlotName('has space')` returns `false`; `isValidSlotName('__proto__')` returns `false`; `isValidSlotName('_leading')` returns `false`.
- [ ] **AC-05:** `validatePlaneSlots` with all required slots present and no unknown keys returns `{ valid: true, errors: [], warnings: [] }`.
- [ ] **AC-06:** `validatePlaneSlots` with a missing required slot returns `valid: false` with an error message naming the missing slot and the geometry: e.g., `"Geometry 'tunnel' requires slot 'floor' but it was not provided"`.
- [ ] **AC-07:** `validatePlaneSlots` with an unknown plane key (not in the geometry's SlotSet) returns `valid: false` with an error message naming the unknown key and listing the valid slot names: e.g., `"Plane 'ceiling_fan' is not a valid slot for geometry 'stage'. Valid slots: backdrop, floor, subject"`.
- [ ] **AC-08:** `validatePlaneSlots` with a missing optional slot returns `valid: true` with a warning: e.g., `"Optional slot 'near_fg' not provided for geometry 'stage'. It will be empty."`.
- [ ] **AC-09:** `validatePlaneSlots` with `override.opacity` outside `[0.0, 1.0]` (e.g., `1.5` or `-0.1`) returns `valid: false` with a descriptive error.
- [ ] **AC-10:** `validatePlaneSlots` with `override.size` containing a non-positive value (e.g., `[0, 5]` or `[-1, 5]`) returns `valid: false`.
- [ ] **AC-11:** `validatePlaneSlots` with `override.position` containing `NaN` or `Infinity` returns `valid: false`.
- [ ] **AC-12:** `validatePlaneSlots` with a plane key that doesn't match `SLOT_NAME_PATTERN` returns `valid: false` with a descriptive error. That key is reported as a format error only, not additionally as an unknown key.
- [ ] **AC-13:** `validatePlaneSlots` errors are reported in stable order: missing required slots first (alphabetical), then invalid slot name format (alphabetical), then unknown keys (alphabetical), then override validation errors (alphabetical by slot name). Warnings are alphabetical by slot name.
- [ ] **AC-14:** `resolveSlotTransform` with no override returns the slot's defaults exactly: position, rotation, size from the `DepthSlot`, opacity `1.0`, renderOrder from the slot.
- [ ] **AC-15:** `resolveSlotTransform` with `override: { position: [1, 2, 3] }` returns position `[1, 2, 3]` but rotation, size, opacity, and renderOrder from the slot defaults.
- [ ] **AC-16:** `resolveSlotTransform` with `override: { opacity: 0.5 }` returns opacity `0.5` with all spatial values from slot defaults.
- [ ] **AC-17:** `resolveSlotTransform` with `override: { position: [1,2,3], rotation: [0,0,1], size: [10,10], opacity: 0.7 }` returns all override values, with renderOrder from the slot.
- [ ] **AC-18:** Every `DepthSlot` in `DEFAULT_SLOT_TAXONOMY` has a non-empty `description` and `promptGuidance` string.
- [ ] **AC-19:** `DEFAULT_SLOT_TAXONOMY.subject.expectsAlpha` is `true`; `DEFAULT_SLOT_TAXONOMY.near_fg.expectsAlpha` is `true`; `DEFAULT_SLOT_TAXONOMY.sky.expectsAlpha` is `false`.
- [ ] **AC-20:** `renderOrder` values in `DEFAULT_SLOT_TAXONOMY` increase monotonically from sky (0) to near_fg (4).
- [ ] **AC-21:** The module has zero runtime dependencies beyond OBJ-003's spatial types (Vec3, EulerRotation, Size2D) and standard JavaScript.
- [ ] **AC-22:** All types and functions are accessible via the `src/spatial/index.ts` barrel export.
- [ ] **AC-23:** Each default slot size is at least as large as the frustum visible area at that slot's distance from `DEFAULT_CAMERA.position` ([0,0,5]) with FOV=50 degrees and aspect ratio 16:9 (i.e., oversize factor >= 1.0 in both dimensions).

## Edge Cases and Error Handling

### validatePlaneSlots Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Empty `planes` object `{}` with geometry that has required slots | `valid: false`, error for each missing required slot |
| Empty `planes` object `{}` with geometry that has NO required slots | `valid: true`, warnings for each missing optional slot |
| All slots provided, all optional | `valid: true`, no errors, no warnings |
| Extra unknown slot keys alongside all required slots | `valid: false` — unknown keys are errors, not warnings, because they indicate an authoring mistake (likely a typo or geometry mismatch) |
| Plane key that violates `SLOT_NAME_PATTERN` (e.g., `"Left Wall"`, `"__proto__"`) | `valid: false`, format error only — NOT additionally reported as unknown key |
| `override` with all fields set | All override values used, geometry defaults fully replaced |
| `override` with empty object `{}` | Treated as no override — all geometry defaults used |
| `override: undefined` for a plane entry | No override — geometry defaults used |
| `override.position` with `[0, 0, 0]` | Valid — zero is a legitimate coordinate |
| `override.size` with `[0, 5]` | `valid: false` — size components must be positive (> 0, not >= 0) |
| `override.opacity` of exactly `0.0` | Valid — fully transparent is a legitimate artistic choice |
| `override.opacity` of exactly `1.0` | Valid — fully opaque is the default |
| `override.rotation` with very large values (e.g., `[100, 0, 0]`) | Valid — large rotations are mathematically fine (wrapping). Constraining would be artistic judgment, not safety. |

### resolveSlotTransform Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `override` is `undefined` | Returns slot defaults with `opacity: 1.0` |
| `override` has only some fields | Partial merge: specified fields override, unspecified retain defaults |
| Slot has `renderOrder: 3`, override doesn't touch it | Resolved `renderOrder` is `3` — overrides cannot change renderOrder (it's not in `PlaneOverride`) |
| Empty override object `{}` | Same as `undefined` — all defaults |

### Near-Plane Clipping Note

`near_fg` is at Z=-1. With the camera at `DEFAULT_CAMERA.position` Z=5, the distance is 6 units — well within the frustum. However, if the camera pushes forward (common for many presets), it could approach Z=0 or beyond, reducing the distance to `near_fg` to 1 unit or less, risking near-plane clipping. Camera path presets (OBJ-006) are responsible for ensuring the camera doesn't clip through foreground planes. OBJ-040 (edge-reveal validation) should also verify near-plane clearance.

## Test Strategy

### Unit Tests

**isValidSlotName:**
1. Valid: `'sky'`, `'back_wall'`, `'left_wall_2'`, `'a'` -> `true`.
2. Invalid: `''`, `'Left'`, `'123'`, `'has space'`, `'__proto__'`, `'constructor'`, `'_leading'`, `'-dash'`, `'UPPER'` -> `false`.

**DEFAULT_SLOT_TAXONOMY structure:**
1. Contains exactly 5 keys: `sky`, `back_wall`, `midground`, `subject`, `near_fg`.
2. Z-positions match seed Section 4.1: -50, -30, -15, -5, -1.
3. Required flags: sky=true, back_wall=false, midground=false, subject=true, near_fg=false.
4. expectsAlpha: sky=false, back_wall=false, midground=false, subject=true, near_fg=true.
5. renderOrder values monotonically increasing 0 through 4.
6. All description and promptGuidance strings non-empty.
7. All rotations are `[0, 0, 0]` (default taxonomy slots face camera).
8. All slot names match `SLOT_NAME_PATTERN`.
9. Each slot's `name` field matches its key in the Record.
10. Each slot size is >= frustum visible area at its distance from DEFAULT_CAMERA (AC-23).

**validatePlaneSlots:**
1. All required slots present, no extras -> `valid: true, errors: [], warnings: []`.
2. Missing one required slot -> `valid: false`, error names the slot and geometry.
3. Missing multiple required slots -> `valid: false`, one error per slot, alphabetically ordered.
4. Unknown slot key -> `valid: false`, error names the key and lists valid slots.
5. Slot key violating SLOT_NAME_PATTERN -> `valid: false`, format error only (not also unknown key).
6. Missing optional slot -> `valid: true`, warning produced, alphabetically ordered.
7. Override with valid values -> `valid: true`.
8. Override with `opacity: 1.5` -> `valid: false`.
9. Override with `opacity: -0.1` -> `valid: false`.
10. Override with `size: [0, 5]` -> `valid: false`.
11. Override with `size: [-1, 5]` -> `valid: false`.
12. Override with `position: [NaN, 0, 0]` -> `valid: false`.
13. Override with `position: [Infinity, 0, 0]` -> `valid: false`.
14. Override with `rotation: [0, NaN, 0]` -> `valid: false`.
15. Empty planes against geometry with only optional slots -> `valid: true`, warnings only.
16. Empty planes against geometry with required slots -> `valid: false`.
17. Error ordering: missing required (alpha) -> invalid format (alpha) -> unknown keys (alpha) -> override errors (alpha). Then warnings (alpha).
18. Multiple error types in one call: verify stable ordering.

**resolveSlotTransform:**
1. No override -> exact slot defaults, opacity 1.0, renderOrder from slot.
2. Position-only override -> position overridden, rest from defaults.
3. Full override (position, rotation, size, opacity) -> all overridden, renderOrder from slot.
4. Empty override object `{}` -> same as no override.
5. Opacity-only override -> opacity overridden, spatial values from defaults.
6. renderOrder always from slot.

### Relevant Testable Claims

- **TC-04** (partial): This module defines the slot contract enabling "no manual 3D positioning." The LLM refers to slot names, not coordinates. Validated here by confirming `resolveSlotTransform` produces correct spatial values from just a slot name.
- **TC-07** (partial): `validatePlaneSlots` catches planes that don't match the geometry's expected slots — one of the validation checks TC-07 expects.
- **TC-08** (partial): The per-geometry `SlotSet` architecture enables the 8-geometry design. Each geometry defines its own slots, validated against this contract.

## Integration Points

### Depends on

| Upstream | What OBJ-007 imports |
|---|---|
| **OBJ-003** (Coordinate system & spatial math) | `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` and `PLANE_ROTATIONS` constants (referenced in documentation and used by geometry-specific slot definitions downstream, not directly by the default taxonomy which is all camera-facing). |

### Consumed by

| Downstream | How it uses OBJ-007 |
|---|---|
| **OBJ-005** (Scene geometry base module) | Imports `DepthSlot`, `SlotSet`, `SlotName`, `SLOT_NAME_PATTERN`, `isValidSlotName` to define the geometry registration contract. The `GeometrySlotDeclaration` interface (OBJ-005's concern) composes a `SlotSet` with camera compatibility and other geometry metadata. |
| **OBJ-010** (Manifest validation / scene sequencer) | Imports `PlaneOverride`, `validatePlaneSlots`, `resolveSlotTransform`, `ResolvedSlot`, `SlotValidationResult` to validate manifest scenes and resolve runtime spatial state. OBJ-010 defines the manifest plane type (with `src` field) and extracts the `Record<string, PlaneOverride | undefined>` for validation. |
| **OBJ-018-OBJ-025** (Individual scene geometries) | Each imports `DepthSlot`, `SlotSet`, and optionally `DEFAULT_SLOT_TAXONOMY` (for geometries using the standard layered arrangement). Each defines its own `SlotSet` per the contract. |
| **OBJ-040** (Edge-reveal validation) | Imports `ResolvedSlot`, `resolveSlotTransform` to get the final spatial state of each plane for frustum-boundary checks. |
| **OBJ-051** (SKILL.md) | Reads `description`, `promptGuidance`, and `expectsAlpha` from slot declarations to generate authoring documentation. |
| **OBJ-053** (Prompt template library) | Reads `promptGuidance` and `expectsAlpha` from slot declarations for image generation guidance. |

### File Placement

```
depthkit/
  src/
    spatial/
      index.ts          # Barrel export (add OBJ-007 exports)
      types.ts           # (OBJ-003, unchanged)
      constants.ts       # (OBJ-003, unchanged)
      math.ts            # (OBJ-003, unchanged)
      depth-model.ts     # NEW: SlotName, SLOT_NAME_PATTERN, isValidSlotName,
                         #   DepthSlot, SlotSet, DEFAULT_SLOT_TAXONOMY,
                         #   PlaneOverride, ResolvedSlot, SlotValidationResult,
                         #   validatePlaneSlots, resolveSlotTransform
```

## Open Questions

1. **Should `DEFAULT_SLOT_TAXONOMY` sizes be auto-computed from OBJ-003's `computePlaneSize`?** Currently they're hardcoded based on manual calculation against the default camera. An alternative is to compute them at module load time. **Recommendation:** Keep them hardcoded. Auto-computation adds a runtime dependency on which aspect ratio to use (16:9 vs 9:16), and the values need manual tuning against camera paths anyway. The hardcoded values serve as documented starting points validated by AC-23.

2. **Should geometries that use the default taxonomy be able to use a subset of slots?** E.g., a `close_up` geometry might only use `subject` and `sky`. **Recommendation:** Yes — geometries pick the slots they need. They can spread `DEFAULT_SLOT_TAXONOMY` and delete unwanted keys, or construct their own `SlotSet` from scratch.

3. **Should `PlaneOverride` support a `visible: boolean` field?** **Recommendation:** Not for V1. The author can set `opacity: 0` or simply omit the optional slot.

4. **Should the default slot Z-positions account for portrait mode?** Z-positions are fine for both orientations (depth doesn't change). Sizes may need adjustment — this is OQ-04 from the seed and should be handled by per-geometry aspect-ratio adaptation (OBJ-005), not by duplicating the taxonomy.
