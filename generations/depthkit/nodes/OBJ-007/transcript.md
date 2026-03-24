# Deliberation Transcript: OBJ-007

---

## Round 1 — spec_author

Looking at OBJ-007's metadata, dependency (OBJ-003), and the seed document sections on depth models (4.1), scene geometry spatial contracts (8.6), and AP-08 (do not hard-code), let me propose the full specification.

---

# Specification: Depth Model — Semantic Slot Taxonomy and Override System (OBJ-007)

## Summary

OBJ-007 defines the **depth model**: the semantic mapping from named slot labels to 3D spatial transforms (position, rotation, size) that scene geometries use to place planes in the Three.js scene. It establishes a **default slot taxonomy** (sky, back_wall, midground, subject, near_fg) with default Z-positions per seed Section 4.1, defines the **rules by which scene geometries declare their own slot sets** (e.g., tunnel uses floor/ceiling/walls instead of the default taxonomy), and specifies the **`position_override` escape hatch** in the manifest schema that allows per-scene spatial tweaks without hard-coding the depth model (AP-08). This module is consumed by every scene geometry definition (OBJ-005, OBJ-018–OBJ-025) and by manifest validation (OBJ-010).

## Interface Contract

### Core Types

```typescript
// src/spatial/depth-model.ts

import type { Vec3, EulerRotation, Size2D } from './types';

/**
 * A single depth slot definition: the spatial contract for one named
 * plane position within a scene geometry.
 *
 * Seed Section 8.6: "Each scene geometry defines, for each plane slot..."
 */
export interface DepthSlot {
  /** Slot name, e.g., 'sky', 'floor', 'left_wall'. Used as the key in manifest planes. */
  readonly name: string;

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
   * E.g., "Wide atmospheric scene, no foreground objects" for sky slots.
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
 */
export type SlotSet = Readonly<Record<string, DepthSlot>>;
```

### Default Slot Taxonomy

```typescript
// src/spatial/depth-model.ts (continued)

/**
 * The default depth slot taxonomy from seed Section 4.1.
 * Used by geometries that follow the standard layered arrangement
 * (e.g., stage, diorama, close_up).
 *
 * Geometries that define fundamentally different spatial structures
 * (e.g., tunnel, canyon) declare their own SlotSet and do NOT use
 * these defaults.
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

### Slot Override Types (Manifest-Level)

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
 */
export interface PlaneOverride {
  /** Override position [x, y, z] in world units. */
  readonly position?: Vec3;

  /** Override rotation [rx, ry, rz] in radians. */
  readonly rotation?: EulerRotation;

  /** Override size [width, height] in world units. */
  readonly size?: Size2D;

  /**
   * Override opacity [0.0–1.0]. Default: 1.0.
   * Enables per-plane transparency for artistic effects
   * (e.g., ghostly foreground, semi-transparent overlays).
   * Addresses OQ-01 at the static level; per-frame animation
   * is deferred.
   */
  readonly opacity?: number;
}

/**
 * The plane entry in a manifest scene — the image source
 * plus optional spatial overrides.
 */
export interface ManifestPlane {
  /** Path or URL to the image file. */
  readonly src: string;

  /**
   * Optional spatial overrides. If omitted, the geometry's
   * default slot values are used unchanged.
   */
  readonly override?: PlaneOverride;
}

/**
 * The planes object in a manifest scene.
 * Keys are slot names defined by the scene's geometry.
 * Values are ManifestPlane entries.
 */
export type ManifestPlanes = Readonly<Record<string, ManifestPlane>>;
```

### Geometry Slot Registry

```typescript
// src/spatial/depth-model.ts (continued)

/**
 * A geometry's declaration of its slot set, compatible cameras,
 * and default camera. This is the contract between a geometry
 * module and the depth model system.
 *
 * Every geometry must register via this interface. The registry
 * is the single source of truth for manifest validation (OBJ-010)
 * to check that a manifest's planes match the geometry's slots.
 */
export interface GeometrySlotDeclaration {
  /** Geometry name. Must match the `geometry` field in manifests. */
  readonly name: string;

  /** The slot set this geometry defines. */
  readonly slots: SlotSet;

  /** Camera path preset names compatible with this geometry. */
  readonly compatibleCameras: readonly string[];

  /** Default camera path if none specified in the manifest. */
  readonly defaultCamera: string;

  /** Optional fog settings. */
  readonly fog?: {
    readonly color: string;
    readonly near: number;
    readonly far: number;
  };

  /**
   * Human-readable description for SKILL.md.
   * Describes the spatial feel: "A box-like tunnel with floor,
   * ceiling, and walls receding to a vanishing point."
   */
  readonly description: string;
}

/**
 * The geometry registry: a map from geometry names to their
 * slot declarations.
 *
 * Populated by each geometry module (OBJ-018–OBJ-025) calling
 * registerGeometry(). Queried by manifest validation (OBJ-010)
 * and the scene renderer.
 */
export interface GeometryRegistry {
  /**
   * Register a geometry's slot declaration.
   * @throws Error if a geometry with the same name is already registered.
   */
  register(declaration: GeometrySlotDeclaration): void;

  /**
   * Retrieve a geometry's declaration by name.
   * @returns The declaration, or undefined if not registered.
   */
  get(name: string): GeometrySlotDeclaration | undefined;

  /**
   * List all registered geometry names.
   */
  names(): readonly string[];

  /**
   * Check if a geometry name is registered.
   */
  has(name: string): boolean;
}

/**
 * Factory function to create a GeometryRegistry instance.
 * The engine creates one registry at startup and passes it
 * to all geometry modules for registration.
 */
export function createGeometryRegistry(): GeometryRegistry;
```

### Validation Utilities

```typescript
// src/spatial/depth-model.ts (continued)

/**
 * Result of validating manifest planes against a geometry's slot set.
 */
export interface SlotValidationResult {
  /** True if validation passed with no errors. */
  readonly valid: boolean;

  /** Error messages (empty if valid). */
  readonly errors: readonly string[];

  /** Warning messages (non-fatal issues). */
  readonly warnings: readonly string[];
}

/**
 * Validates that a manifest scene's planes match its geometry's
 * slot declarations.
 *
 * Checks:
 * 1. All required slots in the geometry have a corresponding plane entry.
 * 2. No plane keys exist that aren't in the geometry's slot set.
 * 3. If PlaneOverride values are present, they are within safe ranges.
 *
 * This function does NOT validate that image files exist — that's
 * a separate validation concern (OBJ-010 manifest loader).
 *
 * @param planes - The manifest scene's planes object.
 * @param slots - The geometry's slot set.
 * @param geometryName - For error messages.
 * @returns SlotValidationResult with errors and warnings.
 */
export function validatePlaneSlots(
  planes: ManifestPlanes,
  slots: SlotSet,
  geometryName: string
): SlotValidationResult;

/**
 * Resolves a manifest plane's effective spatial transform by
 * merging the geometry's default slot values with any overrides.
 *
 * For each field in PlaneOverride:
 *   - If present in override: use the override value.
 *   - If absent: use the geometry's default from the SlotSet.
 *
 * @param slot - The geometry's default slot definition.
 * @param override - The manifest's optional overrides (may be undefined).
 * @returns The resolved PlaneTransform + opacity.
 */
export function resolveSlotTransform(
  slot: DepthSlot,
  override?: PlaneOverride
): ResolvedSlot;

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

### Module Exports

```typescript
// src/spatial/depth-model.ts exports (added to src/spatial/index.ts barrel)

export {
  // Types
  DepthSlot,
  SlotSet,
  PlaneOverride,
  ManifestPlane,
  ManifestPlanes,
  GeometrySlotDeclaration,
  GeometryRegistry,
  SlotValidationResult,
  ResolvedSlot,

  // Constants
  DEFAULT_SLOT_TAXONOMY,

  // Functions
  createGeometryRegistry,
  validatePlaneSlots,
  resolveSlotTransform,
};
```

## Design Decisions

### D1: Two-tier slot model — default taxonomy + per-geometry overrides

The seed (Section 4.1) defines a default 5-slot taxonomy (sky, back_wall, midground, subject, near_fg) but also notes that geometries like tunnel need entirely different slot names (floor, ceiling, left_wall, right_wall, end_wall). Rather than forcing all geometries to map into the default taxonomy, each geometry declares its own `SlotSet`. The `DEFAULT_SLOT_TAXONOMY` is a convenience for geometries that follow the standard layered arrangement (stage, diorama, close_up) — they can spread it or pick slots from it. Geometries like tunnel define completely independent slot sets.

**Rationale:** The seed explicitly asks (Section 4.1): "whether scene geometries should define their own slot sets (e.g., a tunnel needs `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall` — 5 slots but different ones)." The answer is yes. A tunnel's `floor` and a stage's `sky` have nothing in common spatially. Forcing both into the same taxonomy would produce incorrect defaults and confusing SKILL.md documentation.

**Constraint alignment:** Seed C-06 (blind-authorable). The LLM picks a geometry name and fills its declared slots. The slot names are geometry-specific and self-documenting. No raw coordinates needed.

### D2: GeometryRegistry as a runtime lookup, not a static map

Geometries register themselves into a `GeometryRegistry` at startup. This avoids a single file that imports all geometry modules (which would create circular dependencies and a bottleneck for adding new geometries). Each geometry module calls `registry.register(...)` with its declaration.

**Rationale:** The seed expects 8 geometries initially (Section 4.2), potentially more. A registration pattern scales cleanly. Manifest validation queries the registry to check whether a geometry name exists and whether the manifest's plane keys match its slots.

### D3: PlaneOverride as partial merge, not replacement

The `PlaneOverride` in the manifest lets authors adjust individual spatial properties without replacing the entire slot definition. If only `position` is overridden, rotation and size retain the geometry's defaults. This satisfies AP-08 ("do not hard-code the depth model") by allowing escape-hatch tweaks while keeping the 90% case zero-config.

**Rationale:** The seed says defaults should be "good enough for 90% of cases, but the engine must not break if they're overridden via `position_override` in the manifest." Partial merge is the natural expression of this: override only what you need.

### D4: Override validation constrains values to safe ranges

`validatePlaneSlots` checks override values for safety:
- `opacity` must be in `[0.0, 1.0]`.
- `position` components must be finite numbers (not NaN/Infinity).
- `rotation` components must be finite numbers.
- `size` components must be positive finite numbers.

It does NOT constrain overrides to "reasonable" spatial ranges (e.g., it won't reject a plane at Z=-1000). That's the author's intent. But it rejects values that would produce rendering errors.

**Rationale:** AP-08 says don't hard-code, but C-10 says validate before rendering. The compromise: validate for mathematical correctness (finite, positive where needed), not for artistic judgment.

### D5: `renderOrder` is metadata, not Z-position

Three.js requires explicit render ordering for correct transparency compositing. Planes with alpha need to be drawn back-to-front. `renderOrder` is a hint from the depth model, not a duplicate of Z-position. A slot at Z=-50 with `renderOrder: 0` renders before a slot at Z=-5 with `renderOrder: 3`, ensuring correct alpha blending.

**Rationale:** Three.js's default depth sorting can fail for intersecting or closely-spaced transparent planes. Explicit render order, defined once per slot in the geometry, prevents visual artifacts without requiring the LLM author to understand WebGL draw ordering.

### D6: `promptGuidance` and `expectsAlpha` belong in the depth model

These fields are consumed by SKILL.md generation and the asset pipeline, not by the renderer. Including them in `DepthSlot` keeps all slot-related knowledge in one place rather than scattering it across separate prompt-template files.

**Rationale:** Seed Section 4.7 defines per-slot prompt guidance. Seed Section 4.8 notes alpha requirements vary by slot. Collocating this with spatial data makes each geometry's slot declaration a self-contained reference for both rendering and authoring.

### D7: No per-frame opacity animation in V1

`PlaneOverride.opacity` is static (set once per scene). Per-frame opacity animation (OQ-01) is deferred. The manifest schema supports a static opacity value, which handles the common cases (semi-transparent fog layer, faded overlay). Animation would require a keyframe system, which adds significant schema and engine complexity.

**Rationale:** OQ-01 explicitly flags this as an open question. Static opacity covers the most common needs. If animation is needed later, it can be added as an `opacityAnimation` field without breaking the existing `opacity` field.

### D8: Slot names are plain strings, not an enum

Slot names are `string` keys in a `Record`, not members of a union type or enum. Each geometry defines its own slot names. There is no global enum of all possible slot names.

**Rationale:** A global enum would need updating every time a new geometry is added. String keys with per-geometry validation (via `SlotSet`) achieve the same type safety at the manifest validation boundary without creating a maintenance bottleneck.

### D9: Default slot sizes are pre-computed for the default camera

The sizes in `DEFAULT_SLOT_TAXONOMY` are pre-computed to overfill the visible frustum at each slot's Z-position, assuming `DEFAULT_CAMERA` from OBJ-003 (FOV=50°, camera at `[0,0,5]`). For example, the `sky` slot at Z=-50 (distance of 55 from default camera) needs:
- `visibleHeight = 2 × 55 × tan(25°) ≈ 51.27`
- `visibleWidth ≈ 51.27 × (16/9) ≈ 91.14`

The defined size of `[120, 70]` provides ~30% oversize horizontally and ~36% vertically, accommodating typical camera motion ranges. Individual geometries and camera presets may need larger or smaller margins; that's why `computePlaneSize` from OBJ-003 exists.

**Note:** These default sizes are approximate starting points tuned during the initial implementation. The exact values should be validated when the first geometry (OBJ-018, stage) is built and tested against its camera paths. The sizes must prevent edge reveal for all compatible camera presets — OBJ-040 (edge-reveal validation) formally verifies this.

## Acceptance Criteria

- [ ] **AC-01:** `DEFAULT_SLOT_TAXONOMY` contains exactly 5 slots: `sky`, `back_wall`, `midground`, `subject`, `near_fg`, with Z-positions matching seed Section 4.1 (-50, -30, -15, -5, -1 respectively).
- [ ] **AC-02:** `DEFAULT_SLOT_TAXONOMY.sky.required` is `true`; `DEFAULT_SLOT_TAXONOMY.back_wall.required` is `false`; `DEFAULT_SLOT_TAXONOMY.subject.required` is `true`. At minimum, the two anchoring slots (furthest background and primary subject) are required.
- [ ] **AC-03:** `createGeometryRegistry()` returns a registry. Calling `register()` twice with the same geometry name throws an `Error`.
- [ ] **AC-04:** `registry.get('nonexistent')` returns `undefined`. `registry.has('nonexistent')` returns `false`.
- [ ] **AC-05:** `validatePlaneSlots` with all required slots present and no unknown keys returns `{ valid: true, errors: [], warnings: [] }`.
- [ ] **AC-06:** `validatePlaneSlots` with a missing required slot returns `valid: false` with an error message naming the missing slot and the geometry: e.g., `"Geometry 'tunnel' requires slot 'floor' but it was not provided"`.
- [ ] **AC-07:** `validatePlaneSlots` with an unknown plane key (not in the geometry's SlotSet) returns `valid: false` with an error message naming the unknown key and listing the valid slot names: e.g., `"Plane 'ceiling_fan' is not a valid slot for geometry 'stage'. Valid slots: backdrop, floor, subject"`.
- [ ] **AC-08:** `validatePlaneSlots` with a missing optional slot returns `valid: true` with a warning: e.g., `"Optional slot 'near_fg' not provided for geometry 'stage'. It will be empty."`.
- [ ] **AC-09:** `validatePlaneSlots` with `override.opacity` outside `[0.0, 1.0]` returns `valid: false` with a descriptive error.
- [ ] **AC-10:** `validatePlaneSlots` with `override.size` containing a non-positive value returns `valid: false`.
- [ ] **AC-11:** `validatePlaneSlots` with `override.position` containing `NaN` or `Infinity` returns `valid: false`.
- [ ] **AC-12:** `resolveSlotTransform` with no override returns the slot's defaults exactly: position, rotation, size from the `DepthSlot`, opacity `1.0`, renderOrder from the slot.
- [ ] **AC-13:** `resolveSlotTransform` with `override: { position: [1, 2, 3] }` returns position `[1, 2, 3]` but rotation, size, opacity, and renderOrder from the slot defaults.
- [ ] **AC-14:** `resolveSlotTransform` with `override: { opacity: 0.5 }` returns opacity `0.5` with all spatial values from slot defaults.
- [ ] **AC-15:** Every `DepthSlot` in `DEFAULT_SLOT_TAXONOMY` has a non-empty `description` and `promptGuidance` string.
- [ ] **AC-16:** `DEFAULT_SLOT_TAXONOMY.subject.expectsAlpha` is `true`; `DEFAULT_SLOT_TAXONOMY.sky.expectsAlpha` is `false`.
- [ ] **AC-17:** The module has zero runtime dependencies beyond OBJ-003's spatial types (Vec3, EulerRotation, Size2D) and standard JavaScript.
- [ ] **AC-18:** All types and functions are accessible via the `src/spatial/index.ts` barrel export.
- [ ] **AC-19:** `renderOrder` values in `DEFAULT_SLOT_TAXONOMY` increase monotonically from sky (0) to near_fg (4), matching depth order (farthest to nearest).

## Edge Cases and Error Handling

### validatePlaneSlots Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Empty `planes` object `{}` with geometry that has required slots | `valid: false`, error for each missing required slot |
| Empty `planes` object `{}` with geometry that has NO required slots | `valid: true`, warnings for each missing optional slot |
| All slots provided, all optional | `valid: true`, no errors, no warnings |
| Extra unknown slot keys alongside all required slots | `valid: false` — unknown keys are errors, not warnings, because they indicate an authoring mistake (likely a typo or geometry mismatch) |
| `override` with all fields set | All override values used, geometry defaults fully replaced |
| `override` with empty object `{}` | Treated as no override — all geometry defaults used |
| `override.position` with `[0, 0, 0]` | Valid — zero is a legitimate coordinate |
| `override.size` with `[0, 5]` | `valid: false` — size components must be positive (> 0, not >= 0) |
| `override.opacity` of exactly `0.0` | Valid — fully transparent is a legitimate artistic choice |
| `override.opacity` of exactly `1.0` | Valid — fully opaque is the default |

### GeometryRegistry Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `register()` with duplicate name | Throws `Error`: `"Geometry 'tunnel' is already registered"` |
| `register()` with empty `slots` object | Allowed — a geometry with no slots is valid (though useless). The implementer of such a geometry owns the consequences. |
| `register()` with `compatibleCameras` that includes names not yet registered in any camera registry | Allowed — camera validation is a cross-cutting concern for OBJ-010, not for the geometry registry. |
| `register()` with `defaultCamera` not in `compatibleCameras` | This is a bug in the geometry definition. The registry does NOT enforce this — it's a static declaration contract that geometry authors must honor. OBJ-010 manifest validation checks consistency. |

### resolveSlotTransform Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `override` is `undefined` | Returns slot defaults with `opacity: 1.0` |
| `override` has only some fields | Partial merge: specified fields override, unspecified retain defaults |
| Slot has `renderOrder: 3`, override doesn't touch it | Resolved `renderOrder` is `3` — overrides cannot change renderOrder (it's not in `PlaneOverride`) |

**Design note on renderOrder immutability:** `renderOrder` is intentionally NOT overridable via the manifest. It's a rendering implementation detail that the geometry author sets based on the slot's depth position. Exposing it to LLM authors would violate C-06 (blind-authorable) — an author would need to understand WebGL draw order to use it correctly.

## Test Strategy

### Unit Tests

**DEFAULT_SLOT_TAXONOMY structure:**
1. Contains exactly the 5 expected keys.
2. Z-positions match seed Section 4.1 values.
3. Required flags are correct (sky=true, back_wall=false, midground=false, subject=true, near_fg=false).
4. expectsAlpha flags are correct (sky=false, back_wall=false, midground=false, subject=true, near_fg=true).
5. renderOrder values are monotonically increasing from 0 to 4.
6. All description and promptGuidance strings are non-empty.
7. All rotations are `[0, 0, 0]` (default taxonomy slots face camera).

**GeometryRegistry:**
1. Fresh registry has no geometries — `names()` returns `[]`.
2. `register()` adds a geometry; `get()` returns it; `has()` returns `true`.
3. `register()` with duplicate name throws descriptive Error.
4. `names()` returns all registered names in insertion order (or any deterministic order).
5. `get()` for unregistered name returns `undefined`.

**validatePlaneSlots:**
1. All required slots present, no extras → `valid: true, errors: []`.
2. Missing one required slot → `valid: false`, error names the slot.
3. Missing multiple required slots → `valid: false`, one error per slot.
4. Unknown slot key → `valid: false`, error names the key and lists valid slots.
5. Missing optional slot → `valid: true`, warning produced.
6. Override with valid values → `valid: true`.
7. Override with `opacity: 1.5` → `valid: false`.
8. Override with `opacity: -0.1` → `valid: false`.
9. Override with `size: [0, 5]` → `valid: false`.
10. Override with `position: [NaN, 0, 0]` → `valid: false`.
11. Override with `position: [Infinity, 0, 0]` → `valid: false`.
12. Empty planes against geometry with only optional slots → `valid: true`.
13. Empty planes against geometry with required slots → `valid: false`.

**resolveSlotTransform:**
1. No override → exact slot defaults, opacity 1.0.
2. Position-only override → position overridden, rest from defaults.
3. Full override (position, rotation, size, opacity) → all overridden.
4. Empty override object `{}` → same as no override.
5. renderOrder always comes from the slot, never affected by override.

### Relevant Testable Claims

- **TC-04** (partial): This module defines the slot contract that enables "no manual 3D positioning." The LLM author refers to slot names, not coordinates. Validated here by confirming that `resolveSlotTransform` produces correct spatial values from just a slot name.
- **TC-07** (partial): `validatePlaneSlots` catches planes that don't match the geometry's expected slots. This is one of the validation checks TC-07 expects.
- **TC-08** (partial): The `GeometryRegistry` and per-geometry `SlotSet` architecture enables the 8-geometry design. Each geometry defines its own slots, validated against this contract.

## Integration Points

### Depends on

| Upstream | What OBJ-007 imports |
|---|---|
| **OBJ-003** (Coordinate system & spatial math) | `Vec3`, `EulerRotation`, `Size2D` types. `PLANE_ROTATIONS` constant (used by geometry-specific slot definitions, not by the default taxonomy which is all camera-facing). |

### Consumed by

| Downstream | How it uses OBJ-007 |
|---|---|
| **OBJ-005** (Scene geometry base module) | Imports `DepthSlot`, `SlotSet`, `GeometrySlotDeclaration`, `GeometryRegistry` to define the base interface that all geometries implement. |
| **OBJ-010** (Manifest validation / scene sequencer) | Imports `GeometryRegistry`, `validatePlaneSlots`, `resolveSlotTransform`, `ManifestPlane`, `ManifestPlanes` to validate manifest scenes and resolve runtime spatial state. |
| **OBJ-018–OBJ-025** (Individual scene geometries) | Each imports `DepthSlot`, `SlotSet`, `GeometrySlotDeclaration`, and optionally `DEFAULT_SLOT_TAXONOMY` (for geometries that use the default layered arrangement). Each calls `registry.register()` with its declaration. |
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
      depth-model.ts     # NEW: DepthSlot, SlotSet, DEFAULT_SLOT_TAXONOMY,
                         #   PlaneOverride, ManifestPlane, ManifestPlanes,
                         #   GeometrySlotDeclaration, GeometryRegistry,
                         #   createGeometryRegistry, validatePlaneSlots,
                         #   resolveSlotTransform, ResolvedSlot
```

## Open Questions

1. **Should `DEFAULT_SLOT_TAXONOMY` sizes be auto-computed from OBJ-003's `computePlaneSize`?** Currently they're hardcoded based on manual calculation against the default camera. An alternative is to compute them at module load time using `computePlaneSize({ distanceFromCamera: 55, fov: 50, aspectRatio: 16/9, oversizeFactor: 1.3 })`. **Recommendation:** Keep them hardcoded for now. Auto-computation adds a runtime dependency on which aspect ratio to use (16:9 vs 9:16), and the values need manual tuning anyway once camera paths are defined. The hardcoded values serve as documented starting points.

2. **Should geometries that use the default taxonomy be able to omit slots?** E.g., a `close_up` geometry might only use `subject` and `sky` from the default taxonomy, ignoring `back_wall`, `midground`, and `near_fg`. **Recommendation:** Yes — geometries pick the slots they need. They can spread `DEFAULT_SLOT_TAXONOMY` and delete unwanted keys, or construct their own `SlotSet` from scratch. The default taxonomy is a grab-bag of pre-defined slots, not a mandatory complete set.

3. **Should `PlaneOverride` support a `visible: boolean` field?** This would let the author hide a default slot without removing it from the planes object. **Recommendation:** Not for V1. The author can achieve the same effect by setting `opacity: 0` or by simply not including the optional slot in the manifest's planes.

4. **Should the default slot Z-positions account for portrait mode?** The default sizes assume 16:9. A 9:16 composition has a much taller-than-wide visible area. **Recommendation:** Z-positions are fine for both orientations (depth doesn't change). Sizes need adjustment — this is OQ-04 from the seed and should be handled by per-geometry aspect-ratio adaptation (OBJ-005), not by duplicating the default taxonomy.

---

I believe this covers the full scope of OBJ-007. The key architectural decisions are:
1. Per-geometry slot sets (not a forced universal taxonomy)
2. Registry pattern for geometry lookup
3. Partial-merge overrides as the escape hatch
4. Validation at the slot level before rendering

I'd like the Challenger to review whether the `GeometryRegistry` belongs here in OBJ-007 or should live in OBJ-005 (scene geometry base module), and whether the override validation ranges are appropriate. Please verify and let me know what needs revision.

---

## Round 2 — spec_challenger

I've reviewed the spec carefully against the seed, OBJ-003, and the objective metadata. There's solid work here — the two-tier slot model, partial-merge overrides, and validation utilities are well-designed. But I have several issues, two of which are critical.

---

## Critical Issues

### C1: GeometryRegistry and GeometrySlotDeclaration exceed OBJ-007's scope

The objective metadata says:

> "Depth model specification -- semantic slot taxonomy (sky, back_wall, midground, subject, near_fg), default Z-positions per Section 4.1, rules for per-geometry slot overrides (tunnel uses floor/ceiling/walls instead of the default taxonomy), and the position_override escape hatch in the manifest for edge cases per AP-08"

The `GeometryRegistry` is a **geometry registration system**, not a depth model. The `GeometrySlotDeclaration` interface bundles camera compatibility, fog settings, and geometry descriptions — those are scene geometry concerns (OBJ-005 territory). OBJ-005 in the progress map has description "Scene geometry base module" and is the natural home for this registry.

OBJ-007 should define the **slot types and rules** that geometries must follow. OBJ-005 should define the **registration system** that geometries use to declare their slot sets.

**Proposed fix:** 
- Keep `DepthSlot`, `SlotSet`, `DEFAULT_SLOT_TAXONOMY`, `PlaneOverride`, `ResolvedSlot`, `resolveSlotTransform`, `validatePlaneSlots`, and `SlotValidationResult` in OBJ-007.
- Move `GeometrySlotDeclaration`, `GeometryRegistry`, and `createGeometryRegistry` to OBJ-005's scope. OBJ-007 defines the slot contract; OBJ-005 defines how geometries register their compliance with it.
- In OBJ-007, document that OBJ-005 will provide a registry, and that `validatePlaneSlots` takes a `SlotSet` (not a registry reference), keeping it registry-agnostic.

### C2: ManifestPlane and ManifestPlanes are manifest schema types, not depth model types

`ManifestPlane` (with `src` field) and `ManifestPlanes` are manifest schema concerns — they describe the JSON structure of a manifest document. That's OBJ-010 (manifest validation / schema) territory.

OBJ-007 should define `PlaneOverride` (the spatial override shape) because that's depth-model knowledge. But the manifest's representation of a plane entry — including `src` — is a manifest schema concern.

**Proposed fix:**
- Keep `PlaneOverride` in OBJ-007 — it defines what spatial overrides are legal.
- Move `ManifestPlane` and `ManifestPlanes` to OBJ-010's scope. OBJ-010 imports `PlaneOverride` from OBJ-007 and composes the full manifest plane type with `src` and `override`.
- Adjust `validatePlaneSlots` signature to accept a `Record<string, { override?: PlaneOverride }>` or a simpler shape that doesn't require `src`. The function validates slot-key matching and override ranges — it doesn't need to know about image sources.

---

## Major Issues

### M1: No slot name format constraint

Slot names are `string` keys. What's legal? Can a geometry define a slot named `""`, `"left wall"` (space), `"123"`, `"__proto__"`? An implementer would need to guess at validation rules.

**Proposed fix:** Define a slot name format constraint: `SlotName` must match `/^[a-z][a-z0-9_]*$/` (lowercase alphanumeric with underscores, starting with a letter). Add an acceptance criterion that `validatePlaneSlots` rejects keys not matching this pattern. Add a type alias: `type SlotName = string` with the constraint documented in JSDoc. This also protects against prototype pollution from user-supplied JSON keys.

### M2: `validatePlaneSlots` signature is ambiguous after removing ManifestPlanes

If we accept C2 and remove `ManifestPlanes`, the function signature needs redesign. Even without C2, the current signature combines two responsibilities: (1) checking slot key membership and (2) validating override values. These are separable and the function should clearly specify its first parameter type.

**Proposed fix:** Change the first parameter to `Record<string, PlaneOverride | undefined>` — a map from provided slot names to their optional overrides. The caller (OBJ-010) extracts this from the manifest's plane entries and passes it in. The function validates keys against the `SlotSet` and override values against safety ranges. This keeps OBJ-007 manifest-agnostic.

### M3: Relationship to seed Section 8.6's `PlaneSlot` and `SceneGeometry` interfaces is unacknowledged

The seed defines `PlaneSlot` and `SceneGeometry` interfaces in Section 8.6. OBJ-007's `DepthSlot` and `GeometrySlotDeclaration` are enhanced versions of these. The spec should explicitly state that `DepthSlot` supersedes the seed's `PlaneSlot` sketch, and document which fields were added and why.

**Proposed fix:** Add a design decision (or a note in D1) stating: "The seed's `PlaneSlot` (Section 8.6) is the directional sketch for this module's `DepthSlot`. `DepthSlot` adds `name`, `promptGuidance`, `expectsAlpha`, and `renderOrder` fields not present in the sketch, based on the needs identified in seed Sections 4.7, 4.8, and the Three.js transparency requirements."

### M4: Default slot sizes don't account for the camera's default Z-position

D9 correctly notes the camera is at `[0,0,5]` and sky is at `[0,0,-50]`, giving distance = 55. But the slot sizes are pre-baked constants that **only work for the default camera position**. If a geometry uses the `DEFAULT_SLOT_TAXONOMY` slots but positions its camera differently (say at `[0,0,10]`), the sizes may be wrong.

The spec should make explicit that `DEFAULT_SLOT_TAXONOMY` sizes are tied to `DEFAULT_CAMERA.position` from OBJ-003, and that any geometry using a different camera start position must recompute sizes using `computePlaneSize`.

**Proposed fix:** Add a prominent note to `DEFAULT_SLOT_TAXONOMY` documentation and to D9 stating: "These sizes assume the camera starts at `DEFAULT_CAMERA.position` ([0,0,5]). Geometries with different camera positions must compute their own plane sizes using OBJ-003's `computePlaneSize`." Add an acceptance criterion verifying that each default slot size is at least as large as the frustum visible area at that slot's distance from `DEFAULT_CAMERA.position`.

---

## Minor Issues

### m1: `near_fg` default Z-position creates near-plane clipping risk

`near_fg` is at Z=-1. With the camera at Z=5, the distance is 6 units — well within the near plane (0.1). But if the camera pushes forward (common for many presets), it could reach Z=0 or beyond, putting `near_fg` at distance=1 from the camera. With extreme forward pushes, `near_fg` might approach or cross the near clipping plane.

**Proposed fix:** Add a note that near_fg's Z=-1 assumes the camera doesn't push past approximately Z=0. Camera path presets (OBJ-006) are responsible for ensuring the camera doesn't clip through foreground planes.

### m2: D9 oversize commentary is inverted

D9 says `[120, 70]` provides "~30% oversize horizontally and ~36% vertically." But 120/91.14 ≈ 1.317 (31.7% horizontal) and 70/51.27 ≈ 1.366 (36.6% vertical) — the vertical oversize is *larger*, which is backwards from what you'd want for typical horizontal camera motion. This isn't wrong (it's a starting point to be tuned), but the commentary should note this asymmetry rather than implying it's intentional.

**Proposed fix:** Adjust the commentary to note that these are approximate starting values and that the oversize distribution should be validated against camera motion ranges during geometry tuning.

### m3: Missing: what order does `validatePlaneSlots` report errors?

If there are 3 missing required slots and 2 unknown keys, what order are the errors listed? This matters for testing determinism.

**Proposed fix:** Specify that errors are reported in a stable order: missing required slots first (alphabetical by slot name), then unknown keys (alphabetical by key name). Warnings after errors, also alphabetical.

---

## What's Sound

- **D1 (two-tier model):** The per-geometry slot sets with an optional default taxonomy is exactly right. The seed asked this question and this is the correct answer.
- **D3 (partial merge):** Clean, unsurprising. Satisfies AP-08 properly.
- **D4 (override validation ranges):** Correct scoping — validate math safety, don't constrain artistic intent.
- **D5 (renderOrder as metadata):** Smart to separate this from Z-position. The decision not to expose it in `PlaneOverride` is correct for C-06.
- **D7 (no per-frame animation):** Right scope decision for V1.
- **D8 (string keys, not enum):** Correct. Enums would be a maintenance nightmare with extensible geometries.
- **Acceptance criteria AC-01 through AC-19:** Mostly well-specified and testable.
- **Edge case table for `validatePlaneSlots`:** Thorough.

---

Please revise addressing C1, C2, M1–M4, and ideally the minor issues. I'll verify the fixes structurally before converging.

---

## Round 3 — spec_author

All of the challenger's points are valid. Here's the revised spec with every issue addressed.

---

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
 * FOV=50° and aspect ratio 16:9. Geometries that use a different
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
   * Override opacity [0.0–1.0]. Default: 1.0.
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
   * then unknown keys (alphabetical by key name), then override
   * validation errors (alphabetical by slot name).
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
 * 2. All required slots in `slots` have a corresponding key in `planes`.
 * 3. No keys in `planes` exist that aren't in `slots`.
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

The sizes in `DEFAULT_SLOT_TAXONOMY` are pre-computed assuming `DEFAULT_CAMERA.position` from OBJ-003 ([0, 0, 5]), FOV=50°, and aspect ratio 16:9. For the `sky` slot at Z=-50 (distance 55 from camera):
- `visibleHeight = 2 × 55 × tan(25°) ≈ 51.27`
- `visibleWidth ≈ 51.27 × (16/9) ≈ 91.14`

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
- [ ] **AC-12:** `validatePlaneSlots` with a plane key that doesn't match `SLOT_NAME_PATTERN` returns `valid: false` with a descriptive error.
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
- [ ] **AC-23:** Each default slot size is at least as large as the frustum visible area at that slot's distance from `DEFAULT_CAMERA.position` ([0,0,5]) with FOV=50° and aspect ratio 16:9 (i.e., oversize factor ≥ 1.0 in both dimensions).

## Edge Cases and Error Handling

### validatePlaneSlots Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Empty `planes` object `{}` with geometry that has required slots | `valid: false`, error for each missing required slot |
| Empty `planes` object `{}` with geometry that has NO required slots | `valid: true`, warnings for each missing optional slot |
| All slots provided, all optional | `valid: true`, no errors, no warnings |
| Extra unknown slot keys alongside all required slots | `valid: false` — unknown keys are errors, not warnings, because they indicate an authoring mistake (likely a typo or geometry mismatch) |
| Plane key that violates `SLOT_NAME_PATTERN` (e.g., `"Left Wall"`, `"__proto__"`) | `valid: false`, error about invalid slot name format |
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
1. Valid: `'sky'`, `'back_wall'`, `'left_wall_2'`, `'a'` → `true`.
2. Invalid: `''`, `'Left'`, `'123'`, `'has space'`, `'__proto__'`, `'constructor'`, `'_leading'`, `'-dash'`, `'UPPER'` → `false`.

**DEFAULT_SLOT_TAXONOMY structure:**
1. Contains exactly 5 keys: `sky`, `back_wall`, `midground`, `subject`, `near_fg`.
2. Z-positions match seed Section 4.1: -50, -30, -15, -5, -1.
3. Required flags: sky=true, back_wall=false, midground=false, subject=true, near_fg=false.
4. expectsAlpha: sky=false, back_wall=false, midground=false, subject=true, near_fg=true.
5. renderOrder values monotonically increasing 0→4.
6. All description and promptGuidance strings non-empty.
7. All rotations are `[0, 0, 0]` (default taxonomy slots face camera).
8. All slot names match `SLOT_NAME_PATTERN`.
9. Each slot's `name` field matches its key in the Record.
10. Each slot size is >= frustum visible area at its distance from DEFAULT_CAMERA (AC-23).

**validatePlaneSlots:**
1. All required slots present, no extras → `valid: true, errors: [], warnings: []`.
2. Missing one required slot → `valid: false`, error names the slot and geometry.
3. Missing multiple required slots → `valid: false`, one error per slot, alphabetically ordered.
4. Unknown slot key → `valid: false`, error names the key and lists valid slots.
5. Slot key violating SLOT_NAME_PATTERN → `valid: false`, format error.
6. Missing optional slot → `valid: true`, warning produced, alphabetically ordered.
7. Override with valid values → `valid: true`.
8. Override with `opacity: 1.5` → `valid: false`.
9. Override with `opacity: -0.1` → `valid: false`.
10. Override with `size: [0, 5]` → `valid: false`.
11. Override with `size: [-1, 5]` → `valid: false`.
12. Override with `position: [NaN, 0, 0]` → `valid: false`.
13. Override with `position: [Infinity, 0, 0]` → `valid: false`.
14. Override with `rotation: [0, NaN, 0]` → `valid: false`.
15. Empty planes against geometry with only optional slots → `valid: true`, warnings only.
16. Empty planes against geometry with required slots → `valid: false`.
17. Error ordering: missing required (alpha) → invalid format (alpha) → unknown keys (alpha) → override errors (alpha). Then warnings (alpha).
18. Multiple error types in one call: verify stable ordering.

**resolveSlotTransform:**
1. No override → exact slot defaults, opacity 1.0, renderOrder from slot.
2. Position-only override → position overridden, rest from defaults.
3. Full override (position, rotation, size, opacity) → all overridden, renderOrder from slot.
4. Empty override object `{}` → same as no override.
5. Opacity-only override → opacity overridden, spatial values from defaults.
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
| **OBJ-018–OBJ-025** (Individual scene geometries) | Each imports `DepthSlot`, `SlotSet`, and optionally `DEFAULT_SLOT_TAXONOMY` (for geometries using the standard layered arrangement). Each defines its own `SlotSet` per the contract. |
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

---

I believe this revision addresses all issues raised:

- **C1:** `GeometrySlotDeclaration`, `GeometryRegistry`, and `createGeometryRegistry` removed. D10 explicitly scopes OBJ-007 vs OBJ-005.
- **C2:** `ManifestPlane` and `ManifestPlanes` removed. `validatePlaneSlots` accepts `Record<string, PlaneOverride | undefined>`. D11 explains the manifest-agnostic design.
- **M1:** `SlotName` type alias, `SLOT_NAME_PATTERN` regex, `isValidSlotName()` function, AC-03/AC-04/AC-12 for testing, D8 rationale.
- **M2:** `validatePlaneSlots` first parameter changed to `Record<string, PlaneOverride | undefined>`.
- **M3:** D2 explicitly states that `DepthSlot` supersedes seed Section 8.6's `PlaneSlot`, lists added fields with rationale.
- **M4:** D9 includes the camera assumption note. `DEFAULT_SLOT_TAXONOMY` JSDoc has a prominent SIZE ASSUMPTION block. AC-23 verifies sizes against frustum.
- **m1:** Near-plane clipping note added in Edge Cases section.
- **m2:** D9 revised — notes values are "approximate starting values" and oversize distribution "should be validated against actual camera motion ranges during geometry tuning."
- **m3:** AC-13 specifies stable error ordering. `SlotValidationResult.errors` JSDoc specifies the order. Test strategy includes ordering verification.

Challenger, please verify and let me know if anything remains.

---

## Round 4 — spec_challenger

I've verified every fix from Round 2 against the revised spec. Let me run through them systematically.

## Verification of Round 2 Fixes

**C1 (GeometryRegistry scope):** ✓ `GeometrySlotDeclaration`, `GeometryRegistry`, `createGeometryRegistry` all removed. D10 explicitly draws the OBJ-007/OBJ-005 boundary. `validatePlaneSlots` takes `SlotSet` directly.

**C2 (ManifestPlane/ManifestPlanes):** ✓ Both types removed. `validatePlaneSlots` accepts `Record<string, PlaneOverride | undefined>`. D11 explains manifest-agnostic design.

**M1 (Slot name format):** ✓ `SlotName`, `SLOT_NAME_PATTERN`, `isValidSlotName()` added. AC-03/AC-04 cover valid/invalid examples including `__proto__`. AC-12 verifies `validatePlaneSlots` rejects bad names. D8 provides rationale.

**M2 (validatePlaneSlots signature):** ✓ First param is `Readonly<Record<string, PlaneOverride | undefined>>`.

**M3 (Seed Section 8.6 relationship):** ✓ D2 explicitly acknowledges and lists additions.

**M4 (Default sizes tied to camera):** ✓ D9 revised, prominent SIZE ASSUMPTION note in `DEFAULT_SLOT_TAXONOMY` JSDoc, AC-23 validates sizes against frustum.

**m1 (near_fg clipping):** ✓ Documented in Edge Cases.

**m2 (D9 oversize asymmetry):** ✓ Revised to "approximate starting values."

**m3 (Error ordering):** ✓ AC-13 specifies full stable ordering. JSDoc on `errors` field matches.

## One Remaining Minor Issue

**m4: Mutual exclusivity of "invalid format" and "unknown key" error categories**

AC-13 lists four error categories in order: missing required → invalid slot name format → unknown keys → override errors. But a key with invalid format (e.g., `"Left Wall"`) is also necessarily not in the geometry's `SlotSet`, so it could be reported as both "invalid format" AND "unknown key." The spec should state that a key failing the format check is reported **only** as a format error, not additionally as an unknown key. Without this, an implementer could reasonably produce either one error or two errors per bad-format key.

**Proposed fix:** Add a note to `validatePlaneSlots` JSDoc or to the edge cases table: "A plane key that fails SLOT_NAME_PATTERN validation is reported as a format error only, not additionally as an unknown key."

---

This is minor enough that I'll incorporate the fix directly into the final output rather than requesting another round.

## What's Sound (everything else)

The spec is clean, well-scoped, and implementable. The two-tier slot model, partial-merge overrides, manifest-agnostic validation, and the clear OBJ-005/OBJ-007 boundary are all architecturally correct. Acceptance criteria are specific and testable. Edge cases are thorough. Integration points accurately reflect the dependency graph.

CONCLUSION:

The specification for OBJ-007 defines the depth model's semantic slot taxonomy, per-geometry slot override rules, and the `PlaneOverride` manifest escape hatch. It exports types (`DepthSlot`, `SlotSet`, `SlotName`, `PlaneOverride`, `ResolvedSlot`), constants (`DEFAULT_SLOT_TAXONOMY`, `SLOT_NAME_PATTERN`), and functions (`isValidSlotName`, `validatePlaneSlots`, `resolveSlotTransform`). Key design decisions: two-tier slot model (default taxonomy + per-geometry sets), partial-merge overrides, manifest-schema-agnostic validation, render order as non-overridable metadata. Scope is correctly bounded — geometry registration belongs to OBJ-005, manifest plane types belong to OBJ-010.

Let me write the final spec and update meta.json.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me check the current state of the repository and existing files.
[Tool: Bash]
  Input: {
  "command": "ls nodes/OBJ-007/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check OBJ-007 node directory"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-007",
     3→  "description": "Depth model specification -- semantic slot taxonomy (sky, back_wall, midground, subject, near_fg), default Z-positions per Section 4.1, rules for per-geometry slot overrides (tunnel uses floor/ceiling/walls instead of the default taxonomy), and the position_override escape hatch in the manifest for edge cases per AP-08 (do not hard-code the depth model).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Defines the semantic mapping from slot names to 3D positions that all geometries implement."
    12→}
    13→
[Tool Result] meta.json
Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/output.md",
  "content": "# Specification: Depth Model \u2014 Semantic Slot Taxonomy and Override System (OBJ-007)\n\n## Summary\n\nOBJ-007 defines the **depth model**: the semantic mapping from named slot labels to 3D spatial transforms (position, rotation, size) that scene geometries use to place planes in the Three.js scene. It establishes a **default slot taxonomy** (sky, back_wall, midground, subject, near_fg) with default Z-positions per seed Section 4.1, defines the **rules and types that govern per-geometry slot sets** (e.g., tunnel uses floor/ceiling/walls instead of the default taxonomy), and specifies the **`PlaneOverride` escape hatch** in the manifest for per-scene spatial tweaks without hard-coding the depth model (AP-08). This module provides the slot contract that all scene geometries implement (OBJ-005) and that manifest validation (OBJ-010) enforces.\n\n## Interface Contract\n\n### Core Types\n\n```typescript\n// src/spatial/depth-model.ts\n\nimport type { Vec3, EulerRotation, Size2D } from './types';\n\n/**\n * Slot names must match: lowercase alpha start, then lowercase\n * alphanumeric or underscores. This prevents empty strings, spaces,\n * leading digits, prototype-polluting keys, and non-ASCII characters.\n *\n * Pattern: /^[a-z][a-z0-9_]*$/\n *\n * This is a branded type alias for documentation. Runtime validation\n * is performed by validateSlotName() and validatePlaneSlots().\n */\nexport type SlotName = string;\n\n/** Regex for valid slot names. Exported for reuse by OBJ-005 and OBJ-010. */\nexport const SLOT_NAME_PATTERN: RegExp; // = /^[a-z][a-z0-9_]*$/\n\n/**\n * Validates a single slot name against SLOT_NAME_PATTERN.\n * @returns true if the name is valid, false otherwise.\n */\nexport function isValidSlotName(name: string): name is SlotName;\n\n/**\n * A single depth slot definition: the spatial contract for one named\n * plane positi
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/meta.json",
  "content": "{\n  \"id\": \"OBJ-007\",\n  \"description\": \"Depth model specification -- semantic slot taxonomy (sky, back_wall, midground, subject, near_fg), default Z-positions per Section 4.1, rules for per-geometry slot overrides (tunnel uses floor/ceiling/walls instead of the default taxonomy), and the position_override escape hatch in the manifest for edge cases per AP-08 (do not hard-code the depth model).\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T01:30:00Z\",\n  \"depends_on\": [\"OBJ-003\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 1 contract. Defines the semantic mapping from slot names to 3D positions that all geometries implement. Spec defines: DepthSlot/SlotSet types, DEFAULT_SLOT_TAXONOMY (5 slots), PlaneOverride partial-merge escape hatch, validatePlaneSlots and resolveSlotTransform functions. Geometry registry deferred to OBJ-005; manifest plane types deferred to OBJ-010.\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/meta.json has been updated successfully.

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-007/output.md nodes/OBJ-007/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-007): depth model \u2014 semantic slot taxonomy and override system\n\nDefines the depth model contract: DepthSlot/SlotSet types, DEFAULT_SLOT_TAXONOMY\nwith 5 slots (sky, back_wall, midground, subject, near_fg) at seed Section 4.1\nZ-positions, PlaneOverride partial-merge escape hatch (AP-08), SlotName format\nconstraint (/^[a-z][a-z0-9_]*$/), validatePlaneSlots for manifest validation,\nand resolveSlotTransform for runtime spatial state resolution.\n\nKey scoping decisions:\n- Geometry registry (GeometrySlotDeclaration, GeometryRegistry) deferred to OBJ-005\n- Manifest plane types (src field) deferred to OBJ-010\n- validatePlaneSlots is manifest-schema-agnostic, accepts Record<string, PlaneOverride | undefined>\n- renderOrder is not overridable via manifest (C-06 blind-authorable)\n- Default sizes tied to DEFAULT_CAMERA.position, documented for recomputation\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-007 spec and meta.json"
}
[Tool Result] [master dcf4d08] spec(OBJ-007): depth model — semantic slot taxonomy and override system
 2 files changed, 571 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-007/output.md
The spec is committed. Here's a summary of what was agreed and the one minor clarification I incorporated in the final version:

**Agreed specification for OBJ-007** defines:

- **Types:** `SlotName` (constrained string), `DepthSlot` (supersedes seed's `PlaneSlot`), `SlotSet`, `PlaneOverride` (partial-merge override), `ResolvedSlot`, `SlotValidationResult`
- **Constants:** `SLOT_NAME_PATTERN` (`/^[a-z][a-z0-9_]*$/`), `DEFAULT_SLOT_TAXONOMY` (5 slots at seed Section 4.1 Z-positions)
- **Functions:** `isValidSlotName()`, `validatePlaneSlots()` (manifest-schema-agnostic), `resolveSlotTransform()` (partial merge with geometry defaults)
- **23 acceptance criteria**, all specific and testable

**Key scope boundaries enforced:**
- Geometry registration system → OBJ-005 (not here)
- Manifest plane types with `src` → OBJ-010 (not here)
- `validatePlaneSlots` takes `SlotSet` directly, no registry coupling

**Minor fix incorporated at convergence:** Clarified in `SlotValidationResult.errors` JSDoc and `validatePlaneSlots` check list that keys failing `SLOT_NAME_PATTERN` are reported as format errors **only**, not additionally as unknown keys. This was added to AC-12 and the edge case table to prevent implementer ambiguity.
