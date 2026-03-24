# Specification: Scene Geometry Type Contract (OBJ-005)

## Summary

OBJ-005 defines the TypeScript type system for all scene geometries in depthkit: the `PlaneSlot` interface describing a single named position in a 3D scene, the `SceneGeometry` interface describing a complete spatial arrangement of planes, the `FogConfig` interface for depth-based atmospheric fading, a geometry registry with explicit registration and deep-freeze semantics, and the slot naming conventions that all 8 geometry implementations (OBJ-018 through OBJ-025) must follow. This is a pure type/contract module — it defines the shape of geometry data, not any specific geometry's values. It imports spatial primitives from OBJ-003 and is consumed by every downstream objective that creates, validates, instantiates, or queries scene geometries.

## Interface Contract

### Core Types

```typescript
// src/scenes/geometries/types.ts

import type { Vec3, EulerRotation, Size2D, PlaneTransform } from '../../spatial';

/**
 * Configuration for Three.js fog, providing depth-based atmospheric fading.
 * Enhances the 2.5D effect by hiding hard edges on distant planes
 * and creating atmospheric perspective (seed Section 8.10).
 */
export interface FogConfig {
  /**
   * CSS-style 6-digit hex color string for the fog (e.g., '#000000').
   * Constrained to #RRGGBB format for manifest serialization predictability
   * and LLM authorability. The renderer converts to THREE.Color at the boundary.
   */
  color: string;
  /** Distance from camera (in world units) where fog begins. Must be >= 0. */
  near: number;
  /** Distance from camera (in world units) where fog is fully opaque. Must be > near. */
  far: number;
}

/**
 * A single named position in a scene geometry's spatial layout.
 * Defines where a plane (textured mesh) is placed in 3D space.
 *
 * Extends PlaneTransform from OBJ-003, adding metadata fields specific
 * to the geometry contract (required, description, rendering hints).
 * Any function accepting PlaneTransform also accepts PlaneSlot.
 *
 * PlaneSlot values in a registered SceneGeometry are immutable templates
 * (see D9). The readonly tuple types (Vec3, EulerRotation, Size2D) enforce
 * this at compile time; deep freezing at registration enforces it at runtime.
 * These values are the geometry's defaults. Downstream consumers (OBJ-036,
 * OBJ-039) may apply per-scene overrides from the manifest by creating a
 * new PlaneTransform with the override applied, rather than mutating the
 * slot definition. The override mechanism is defined by the manifest schema
 * (OBJ-004), not by this contract.
 */
export interface PlaneSlot extends PlaneTransform {
  /**
   * Whether the manifest MUST provide an image for this slot.
   * If true, manifest validation (OBJ-017) rejects manifests that
   * omit this slot. If false, the slot is available but the geometry
   * renders correctly without it.
   */
  required: boolean;

  /**
   * Human-readable description of this slot's purpose.
   * Used in SKILL.md documentation and in validation error messages.
   * Must be non-empty.
   * Should describe the visual role, not the technical details.
   * Examples: "Ground surface", "Distant end of tunnel", "Primary subject"
   */
  description: string;

  /**
   * Render order hint. Planes with higher values render on top of
   * planes with lower values when they overlap from the camera's
   * perspective. Default: 0. Three.js uses this to resolve depth
   * fighting when planes are coplanar or nearly coplanar.
   *
   * The renderer (OBJ-039) maps this to mesh.renderOrder.
   * Not range-validated — geometry authors should use small relative
   * values (e.g., 0-10). Three.js accepts any number.
   */
  renderOrder?: number;

  /**
   * Whether this plane's material should be created with
   * transparent: true and expect an alpha channel in its texture.
   * When true, the renderer uses alpha blending.
   * When false, the texture is treated as fully opaque.
   *
   * Defaults to false. Typically true for subject and near_fg slots.
   */
  transparent?: boolean;

  /**
   * Whether this plane should be excluded from fog calculations.
   * When true, the plane uses meshBasicMaterial regardless of scene fog,
   * ensuring it renders at full brightness/opacity regardless of distance.
   *
   * Defaults to false. Typically true only for sky/backdrop planes
   * that should remain vivid at extreme distances.
   */
  fogImmune?: boolean;
}

/**
 * A complete scene geometry definition — the 3D spatial structure
 * of a scene type. Each geometry defines which planes exist, their
 * positions/rotations in 3D space, and which depth slots map to
 * which planes (seed Section 8.6).
 *
 * Geometries are registered by name and looked up at validation time
 * and at render time. The LLM author selects a geometry name and maps
 * images to its named slots; the geometry handles all 3D positioning
 * internally (seed C-06, AP-03).
 *
 * Once registered, all fields are deeply frozen and immutable (see D10).
 */
export interface SceneGeometry {
  /**
   * Unique identifier for this geometry. Must match the key used
   * in the geometry registry. Lowercase, underscore-separated.
   * Must match /^[a-z][a-z0-9_]*$/.
   * Examples: 'stage', 'tunnel', 'canyon', 'flyover'
   */
  name: string;

  /**
   * The named plane slots that make up this geometry.
   * Keys are slot names (lowercase, underscore-separated,
   * matching /^[a-z][a-z0-9_]*$/).
   * Values define the spatial placement of each slot.
   *
   * The manifest's planes object must use these exact keys.
   * Manifest validation (OBJ-017) checks that all required slots
   * have images and that no unrecognized slot keys are present.
   */
  slots: Record<string, PlaneSlot>;

  /**
   * Camera path preset names that are validated to work with this
   * geometry — meaning they produce no edge reveals and create
   * a visually coherent motion for this spatial arrangement.
   *
   * Manifest validation (OBJ-041) rejects camera paths not in this list.
   * Must contain at least one entry. Must include default_camera.
   * All entries must match /^[a-z][a-z0-9_]*$/.
   */
  compatible_cameras: readonly string[];

  /**
   * The camera path preset used when the manifest omits
   * the camera field. Must be a member of compatible_cameras.
   */
  default_camera: string;

  /**
   * Optional Three.js fog configuration for this geometry.
   * When present, the renderer adds fog to the scene.
   * Can be overridden per-scene in the manifest.
   */
  fog?: FogConfig;

  /**
   * Human-readable description of this geometry's visual character.
   * Must be non-empty. Used in SKILL.md documentation. Should describe
   * the spatial feel and typical use case, not the technical layout.
   * Example: "A corridor with floor, ceiling, and walls receding to
   * a vanishing point. Camera pushes forward for a 'traveling through
   * a space' effect."
   */
  description: string;

  /**
   * Suggested aspect ratio for this geometry.
   * 'landscape' means it's designed for 16:9,
   * 'portrait' means 9:16,
   * 'both' means it works well in either orientation.
   *
   * This is advisory — the geometry must render without errors in
   * any supported aspect ratio (seed C-04), but the SKILL.md can
   * use this to guide LLM selection. When the aspect ratio differs
   * from the preferred one, plane sizes may need adjustment per
   * OBJ-040's auto-sizing rules.
   */
  preferred_aspect?: 'landscape' | 'portrait' | 'both';
}
```

### Geometry Registry Type

```typescript
// src/scenes/geometries/types.ts (continued)

/**
 * The geometry registry: a map from geometry name to its definition.
 * Populated by individual geometry modules (OBJ-018 through OBJ-025)
 * registering themselves.
 *
 * Used by:
 * - Manifest validation (OBJ-017) to check geometry name existence
 *   and validate plane slot keys.
 * - Scene sequencer (OBJ-036) to look up geometry for a scene.
 * - Page-side renderer (OBJ-039) to instantiate meshes from slots.
 * - Spatial compatibility validator (OBJ-041) to cross-reference
 *   geometry + camera compatibility.
 */
export type GeometryRegistry = Record<string, SceneGeometry>;
```

### Registry Access Functions

```typescript
// src/scenes/geometries/registry.ts

import type { SceneGeometry, GeometryRegistry } from './types';

/**
 * Returns the complete registry of all registered scene geometries.
 *
 * On first call, the registry is locked — no further registrations
 * are accepted (see D10). Returns a deeply frozen GeometryRegistry.
 * Subsequent calls return the same frozen object.
 *
 * Mutation attempts on the returned object or any nested object
 * (geometry, slot, position tuple) throw TypeError at runtime.
 *
 * @returns A deeply frozen GeometryRegistry.
 */
export function getGeometryRegistry(): Readonly<GeometryRegistry>;

/**
 * Retrieves a single geometry by name.
 *
 * Implicitly locks the registry on first call (same as getGeometryRegistry).
 *
 * @param name - The geometry name (e.g., 'tunnel', 'stage').
 * @returns The SceneGeometry definition, or undefined if not registered.
 */
export function getGeometry(name: string): SceneGeometry | undefined;

/**
 * Registers a scene geometry in the global registry.
 * Called by each geometry module (OBJ-018 through OBJ-025) at load time.
 *
 * Must be called before any read operation (getGeometryRegistry,
 * getGeometry, getGeometryNames). If called after the registry has
 * been locked by a read operation, throws an Error.
 *
 * @param geometry - A fully-defined SceneGeometry.
 * @throws Error if the registry has been locked by a prior read.
 * @throws Error if a geometry with the same name is already registered
 *         (prevents silent overwrites from duplicate registrations).
 * @throws Error if the geometry fails structural validation
 *         (see validateGeometryDefinition). The error message includes
 *         all validation errors formatted as:
 *         "Cannot register geometry '{name}': {error1}; {error2}; ..."
 */
export function registerGeometry(geometry: SceneGeometry): void;

/**
 * Returns an array of all registered geometry names.
 * Useful for validation error messages ("expected one of: stage, tunnel, ...").
 *
 * Implicitly locks the registry on first call.
 */
export function getGeometryNames(): readonly string[];
```

### Geometry Definition Validator

```typescript
// src/scenes/geometries/validate.ts

import type { SceneGeometry } from './types';

/**
 * Structural self-consistency errors found in a geometry definition.
 */
export interface GeometryValidationError {
  /** Which field or slot has the problem */
  path: string;
  /** Human-readable description of the problem */
  message: string;
}

/**
 * Validates a SceneGeometry definition for structural self-consistency.
 * This is NOT manifest validation (that's OBJ-017). This validates
 * the geometry definition itself — that it is internally coherent
 * before being registered.
 *
 * Checks performed:
 * 1.  name is non-empty and matches /^[a-z][a-z0-9_]*$/.
 * 2.  slots contains at least one entry.
 * 3.  All slot keys match /^[a-z][a-z0-9_]*$/.
 * 4.  At least one slot is marked required: true.
 * 5.  compatible_cameras is non-empty.
 * 6.  All entries in compatible_cameras match /^[a-z][a-z0-9_]*$/.
 * 7.  default_camera appears in compatible_cameras.
 * 8.  If fog is present: fog.near >= 0, fog.far > fog.near,
 *     fog.color matches /^#[0-9a-fA-F]{6}$/.
 * 9.  description is non-empty.
 * 10. All slot size components are > 0.
 * 11. All slot description fields are non-empty strings.
 *
 * @param geometry - The geometry definition to validate.
 * @returns An array of validation errors. Empty array = valid.
 */
export function validateGeometryDefinition(
  geometry: SceneGeometry
): GeometryValidationError[];
```

### Slot Utilities

```typescript
// src/scenes/geometries/slot-utils.ts

import type { SceneGeometry, PlaneSlot } from './types';

/**
 * Returns the names of all required slots for a geometry.
 * Used by manifest validation (OBJ-017) to check that all
 * required planes are provided.
 *
 * @param geometry - The scene geometry definition.
 * @returns Array of slot name strings where required === true.
 */
export function getRequiredSlotNames(geometry: SceneGeometry): string[];

/**
 * Returns the names of all optional slots for a geometry.
 *
 * @param geometry - The scene geometry definition.
 * @returns Array of slot name strings where required === false.
 */
export function getOptionalSlotNames(geometry: SceneGeometry): string[];

/**
 * Returns all valid slot names for a geometry (required + optional).
 * Used by manifest validation (OBJ-017) to reject unrecognized slot keys.
 *
 * @param geometry - The scene geometry definition.
 * @returns Array of all slot name strings.
 */
export function getAllSlotNames(geometry: SceneGeometry): string[];

/**
 * Checks whether a camera path name is compatible with a geometry.
 *
 * @param geometry - The scene geometry definition.
 * @param cameraPathName - The camera path preset name to check.
 * @returns true if the camera path is in the geometry's compatible_cameras list.
 */
export function isCameraCompatible(
  geometry: SceneGeometry,
  cameraPathName: string
): boolean;
```

### Module Exports

```typescript
// src/scenes/geometries/index.ts
// Barrel export

export type {
  PlaneSlot,
  SceneGeometry,
  FogConfig,
  GeometryRegistry,
  GeometryValidationError
} from './types';

export {
  getGeometryRegistry,
  getGeometry,
  registerGeometry,
  getGeometryNames
} from './registry';

export { validateGeometryDefinition } from './validate';

export {
  getRequiredSlotNames,
  getOptionalSlotNames,
  getAllSlotNames,
  isCameraCompatible
} from './slot-utils';
```

## Slot Naming Conventions

All slot names across all geometries must follow these conventions. They are enforced by `validateGeometryDefinition` and documented in SKILL.md.

### Format Rules

1. **Lowercase with underscores**: `/^[a-z][a-z0-9_]*$/`. Examples: `floor`, `left_wall`, `end_wall`, `near_fg`.
2. **No abbreviations except established ones**: `fg` (foreground), `bg` (background) are allowed. Do not invent new abbreviations.
3. **Directional slots use `left_`/`right_` prefix**: `left_wall`, `right_wall` — not `wall_left`, `wall_right`. This groups them alphabetically.
4. **Depth-indicating slots use established names from seed Section 4.1**: `sky`, `back_wall`, `midground`, `subject`, `near_fg` for standard depth positions. Geometries may define geometry-specific slots (e.g., `ceiling`, `floor`, `end_wall`) that don't appear in the default depth model.

### Reserved Slot Names

The following slot names have fixed semantic meaning across all geometries that use them. A geometry is not required to include any of these, but if it uses these names, their spatial role must match the description:

| Slot Name | Semantic Role | Typical Orientation |
|-----------|--------------|---------------------|
| `sky` | Distant sky/space backdrop | `FACING_CAMERA` |
| `backdrop` | Primary background plane | `FACING_CAMERA` |
| `back_wall` | Distant vertical surface | `FACING_CAMERA` |
| `floor` | Horizontal ground surface | `FLOOR` rotation |
| `ceiling` | Horizontal overhead surface | `CEILING` rotation |
| `left_wall` | Left boundary surface | `LEFT_WALL` rotation |
| `right_wall` | Right boundary surface | `RIGHT_WALL` rotation |
| `end_wall` | Distant terminus (tunnel/canyon end) | `FACING_CAMERA` |
| `midground` | Middle-distance environmental element | Varies |
| `subject` | Primary focal element | `FACING_CAMERA` |
| `near_fg` | Close foreground element | `FACING_CAMERA` |

Geometries may define additional slots not in this table (e.g., `ground` for flyover, `frame_inner`/`frame_outer` for portal). These custom slots must follow the format rules but have no cross-geometry semantic constraint.

### Required vs Optional Semantics

- A **required** slot (`required: true`) means the geometry's spatial structure depends on this plane being present. Without it, the scene has a visible gap or the spatial illusion breaks. Manifest validation rejects manifests missing required slots.
- An **optional** slot (`required: false`) enhances the scene but is not structurally necessary. The geometry renders correctly without it. Examples: `ceiling` in a tunnel (open-air tunnel), `near_fg` in a stage (no foreground framing).

A geometry must have at least one required slot. A geometry with all-optional slots would mean an empty scene is valid, which violates the engine's purpose.

## Design Decisions

### D1: Types-only module with no rendering dependency

This module exports TypeScript interfaces, type definitions, a simple in-memory registry, and validation/utility functions. It does NOT import Three.js, Puppeteer, or any rendering library. The `PlaneSlot.position` is a `Vec3` (plain readonly tuple from OBJ-003), not a `THREE.Vector3`. Conversion to Three.js types happens at the rendering boundary (OBJ-039).

**Rationale:** The geometry type contract is consumed on both sides of the Node.js/browser split. Manifest validation (OBJ-017) runs in Node.js before Puppeteer launches. Page-side instantiation (OBJ-039) runs in the browser. Keeping the contract free of rendering dependencies ensures it works in both contexts. Follows the same pattern as OBJ-003.

### D2: Registry pattern with explicit registration and lock-on-first-read

Geometries register themselves via `registerGeometry()` rather than being hardcoded in a central map. Each geometry module (OBJ-018 through OBJ-025) calls `registerGeometry(stageGeometry)` at import time. The registry locks on first read (see D10).

**Rationale:** (a) Decoupled — adding a new geometry doesn't require modifying a central file. (b) Self-validating — `registerGeometry` validates the definition before accepting it, catching definition errors at load time. (c) Prevents silent overwrites — duplicate names throw immediately.

### D3: `renderOrder` and `transparent` on PlaneSlot rather than deferring to texture metadata

PlaneSlot includes `renderOrder` and `transparent` hints because these are spatial/compositional properties of the slot's role in the geometry, not properties of the individual image assigned to it. A `subject` slot in a `stage` geometry is always transparent (expects alpha) regardless of which specific subject image is loaded. A `near_fg` always renders on top of `subject`.

**Rationale:** This makes the geometry definition self-documenting and enables the page-side renderer (OBJ-039) to configure materials correctly without inspecting the texture. It also gives the SKILL.md clear guidance: "subject slots expect transparent images."

### D4: `fogImmune` rather than a per-material override

Some planes (like distant sky backdrops) should not fade with fog — they represent infinite distance and should remain vivid. Rather than requiring downstream consumers to handle this per-material, the slot declares its fog immunity.

**Rationale:** The alternative is having the renderer check slot names against a hardcoded list of "fog immune" names, which is fragile. Making it a slot property keeps the logic data-driven and visible in the geometry definition.

### D5: `preferred_aspect` is advisory, not restrictive

The geometry must render without errors in any supported aspect ratio (seed C-04). The `preferred_aspect` field is purely for SKILL.md guidance and LLM selection heuristics. It does not trigger validation errors.

**Rationale:** Seed OQ-04 asks how vertical video should differ from horizontal. The full answer (auto-adapting plane sizes) is OBJ-040's responsibility. OBJ-005 provides the advisory hook so that downstream systems know which orientation was the geometry's design target.

### D6: Validation of geometry definitions is separate from manifest validation

`validateGeometryDefinition` checks the geometry itself (is the definition coherent?). Manifest validation (OBJ-017) checks a manifest against a geometry (do the provided plane keys match the geometry's slots?). These are distinct concerns with distinct timing — geometry validation runs once at registration; manifest validation runs per-render.

**Rationale:** Separating these avoids circular dependencies and keeps validation fast. Geometry definition errors are developer bugs caught at load time. Manifest errors are authoring errors caught per-invocation.

### D7: `compatible_cameras` is a string array, not a type-safe reference

Camera path preset names are plain strings, not references to camera preset objects. This avoids a circular dependency between geometry definitions (OBJ-005) and camera path definitions (OBJ-006). The cross-reference validation — "does this camera name actually exist?" — is performed by OBJ-041 (spatial compatibility validation), which depends on both OBJ-005 and OBJ-006.

**Rationale:** OBJ-005 and OBJ-006 are both Tier 1 contracts that depend only on OBJ-003. Neither should depend on the other. The string-based reference is resolved downstream.

### D8: Slot key naming enforced by regex, not by enum

Slot keys are validated against `/^[a-z][a-z0-9_]*$/` rather than restricted to a fixed enum of allowed names. This allows geometry authors to define geometry-specific slots (e.g., `ground` in flyover, `frame_inner` in portal) without modifying the type contract.

**Rationale:** Seed Section 4.2 shows that different geometries need different slot names. A tunnel has `ceiling`; a stage has `backdrop`. Restricting to a fixed set would require OBJ-005 to know all geometry slot names in advance, which defeats the extensibility goal.

### D9: PlaneSlot values are immutable templates

PlaneSlot values in a registered SceneGeometry are immutable templates. The `readonly` tuple types (`Vec3`, `EulerRotation`, `Size2D`) enforce immutability at compile time. Deep freezing at registration time (D10) enforces it at runtime.

When the manifest provides per-scene overrides (defined by the manifest schema OBJ-004, not by this contract), the consuming code (OBJ-036 scene sequencer, OBJ-039 page-side renderer) creates a **new** `PlaneTransform` with the override applied, rather than mutating the slot definition. The original geometry definition is never modified.

**Rationale:** The geometry registry is a shared, global data structure. Any mutation of a registered geometry's slot values would silently corrupt all subsequent reads — a catastrophic bug. The readonly types and deep freeze together provide defense-in-depth (compile-time + runtime). This also aligns with the registry being a frozen singleton (D10).

### D10: Registry locks on first read, deep-freezes all data

The registry has two phases:

1. **Registration phase:** `registerGeometry()` accepts new geometries. No read operations have been called yet.
2. **Locked phase:** The first call to any read operation (`getGeometryRegistry()`, `getGeometry()`, `getGeometryNames()`) transitions the registry to locked state. All registered `SceneGeometry` objects and their nested `PlaneSlot` values, including `Vec3` tuples inside positions/rotations/sizes, are **recursively deep-frozen** via `Object.freeze`. The frozen snapshot is cached and returned on all subsequent read calls.

Once locked, calling `registerGeometry()` throws an `Error`: `"Cannot register geometry '{name}': registry is locked. All registrations must occur before the first read."`.

**Rationale:** The engine has a deterministic initialization sequence: import geometry modules (which register themselves) -> validate the manifest (which reads the registry) -> render. Lock-on-first-read enforces this ordering naturally. Returning a fresh snapshot per call (the alternative) would require deep-cloning + deep-freezing on every access, which is wasteful for a registry that never changes after initialization. Deep freeze (not shallow) prevents mutation of nested objects like `slot.position`, which TypeScript's `Readonly` utility type does not protect at runtime.

### D11: PlaneSlot extends PlaneTransform from OBJ-003

`PlaneSlot` formally extends OBJ-003's `PlaneTransform` interface (`{ position: Vec3; rotation: EulerRotation; size: Size2D }`), adding the metadata fields `required`, `description`, `renderOrder`, `transparent`, and `fogImmune`.

**Rationale:** This gives downstream consumers that only need spatial data (OBJ-039 mesh creation, OBJ-040 edge-reveal validation) the ability to accept the narrower `PlaneTransform` type. Any function accepting `PlaneTransform` also accepts `PlaneSlot` due to structural subtyping. This is a clean, stable relationship — `PlaneTransform` is a foundational OBJ-003 type that will not change.

## Acceptance Criteria

- [ ] **AC-01:** `PlaneSlot` interface extends `PlaneTransform` (from OBJ-003) and includes additional fields `required: boolean`, `description: string`, and optional fields `renderOrder?: number`, `transparent?: boolean`, `fogImmune?: boolean`.
- [ ] **AC-02:** `SceneGeometry` interface includes fields `name: string`, `slots: Record<string, PlaneSlot>`, `compatible_cameras: readonly string[]`, `default_camera: string`, `fog?: FogConfig`, `description: string`, `preferred_aspect?: 'landscape' | 'portrait' | 'both'`.
- [ ] **AC-03:** `registerGeometry()` throws an `Error` when called with a geometry whose `name` is already registered, with message containing the geometry name.
- [ ] **AC-04:** `registerGeometry()` throws an `Error` when the geometry definition fails `validateGeometryDefinition`. The error message includes all validation errors formatted as: `"Cannot register geometry '{name}': {error1}; {error2}; ..."`.
- [ ] **AC-05:** `registerGeometry()` throws an `Error` when called after the registry has been locked by a read operation, with message: `"Cannot register geometry '{name}': registry is locked. All registrations must occur before the first read."`.
- [ ] **AC-06:** `validateGeometryDefinition` returns errors for: empty `name`, name not matching `/^[a-z][a-z0-9_]*$/`, empty `slots`, slot keys not matching `/^[a-z][a-z0-9_]*$/`, no required slot, empty `compatible_cameras`, camera entries not matching `/^[a-z][a-z0-9_]*$/`, `default_camera` not in `compatible_cameras`, `fog.far <= fog.near`, `fog.near < 0`, `fog.color` not matching hex pattern, empty geometry `description`, empty slot `description`, slot `size` components `<= 0`.
- [ ] **AC-07:** `getRequiredSlotNames` for a geometry with 3 required and 2 optional slots returns exactly the 3 required slot names.
- [ ] **AC-08:** `getAllSlotNames` returns every key in the geometry's `slots` record.
- [ ] **AC-09:** `isCameraCompatible` returns `true` only for camera names in the geometry's `compatible_cameras` list.
- [ ] **AC-10:** `getGeometry('nonexistent')` returns `undefined`, does not throw.
- [ ] **AC-11:** The seed's tunnel geometry example (Section 8.6) can be expressed using these interfaces without modification — specifically, a geometry with slots `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall` with the positions, rotations, and sizes from the seed passes `validateGeometryDefinition`.
- [ ] **AC-12:** The module has zero runtime dependencies beyond OBJ-003's spatial types/interfaces and standard JavaScript.
- [ ] **AC-13:** All types and functions are accessible via `import { ... } from './scenes/geometries'` (barrel export).
- [ ] **AC-14:** After any read operation, the returned registry and all nested objects (SceneGeometry, PlaneSlot, Vec3 tuples) are deeply frozen — attempting to mutate any property at any nesting level throws a `TypeError`.
- [ ] **AC-15:** `PlaneSlot.renderOrder`, `PlaneSlot.transparent`, and `PlaneSlot.fogImmune` are optional fields (TypeScript `?:`). Omitting them does not cause validation errors.
- [ ] **AC-16:** `SceneGeometry.preferred_aspect` is optional. Omitting it does not cause validation errors.

## Edge Cases and Error Handling

### Geometry Definition Validation Errors

| Condition | Error Path | Error Message Pattern |
|---|---|---|
| Empty geometry name | `name` | `"name must be non-empty and match /^[a-z][a-z0-9_]*$/"` |
| Name with uppercase | `name` | `"name must be non-empty and match /^[a-z][a-z0-9_]*$/, got 'Tunnel'"` |
| Name starting with number | `name` | `"name must be non-empty and match /^[a-z][a-z0-9_]*$/, got '3d_stage'"` |
| No slots defined | `slots` | `"slots must contain at least one entry"` |
| Slot key with uppercase | `slots.LeftWall` | `"slot key must match /^[a-z][a-z0-9_]*$/, got 'LeftWall'"` |
| All slots optional | `slots` | `"at least one slot must be required"` |
| Empty compatible_cameras | `compatible_cameras` | `"compatible_cameras must contain at least one entry"` |
| Camera name with uppercase | `compatible_cameras[0]` | `"camera name must match /^[a-z][a-z0-9_]*$/, got 'TunnelPush'"` |
| default_camera not in list | `default_camera` | `"default_camera 'slow_push' must be in compatible_cameras"` |
| Fog near < 0 | `fog.near` | `"fog.near must be >= 0, got -5"` |
| Fog far <= near | `fog.far` | `"fog.far must be > fog.near (got near=10, far=5)"` |
| Fog color invalid | `fog.color` | `"fog.color must be a hex color (#RRGGBB), got 'black'"` |
| Empty geometry description | `description` | `"description must be non-empty"` |
| Empty slot description | `slots.floor.description` | `"slot 'floor' description must be non-empty"` |
| Slot size zero/negative | `slots.floor.size` | `"slot 'floor' size components must be > 0, got [0, 30]"` |

### Registry Errors

| Condition | Error Type | Message Pattern |
|---|---|---|
| Duplicate registration | `Error` | `"Geometry 'tunnel' is already registered"` |
| Invalid geometry | `Error` | `"Cannot register geometry 'tunnel': {error1}; {error2}; ..."` |
| Registration after lock | `Error` | `"Cannot register geometry 'tunnel': registry is locked. All registrations must occur before the first read."` |

### Boundary Behaviors

- **Geometry with only one slot:** Valid if that slot is `required: true`. The `close_up` geometry might have only a `subject` slot.
- **Geometry with many slots (>10):** No upper limit enforced. Seed TC-01 says 3-5 is sufficient for 90% of cases, but the type system allows more.
- **Slot with `renderOrder: 0`:** Valid. This is the default Three.js render order. Not range-validated — geometry authors should use small relative values (e.g., 0-10).
- **Fog with `near: 0`:** Valid. Means fog starts immediately at the camera.
- **`compatible_cameras` with one entry:** Valid. Means only one camera path works with this geometry.
- **Calling `getGeometryRegistry()` before any registrations:** Returns an empty frozen object. Locks the registry. Not an error — but the engine's initialization sequence should register geometries before any reads.
- **Calling `registerGeometry()` after `getGeometry('nonexistent')` returns undefined:** Throws. The `getGeometry` call locked the registry, even though it returned undefined.
- **`getGeometry` with empty string:** Returns `undefined`. Not a special case.
- **Multiple validation errors in a single geometry:** `validateGeometryDefinition` returns ALL errors, not just the first. `registerGeometry` includes all of them in the thrown Error message, semicolon-separated.

## Test Strategy

### Unit Tests

**PlaneSlot construction tests:**
1. A PlaneSlot with all required fields and no optional fields is type-valid.
2. A PlaneSlot with all fields (including `renderOrder`, `transparent`, `fogImmune`) is type-valid.
3. The seed tunnel geometry's slot definitions (Section 8.6) conform to the `PlaneSlot` interface.
4. A PlaneSlot is assignable to a `PlaneTransform` variable (structural subtyping).

**SceneGeometry construction tests:**
1. The seed tunnel geometry example (Section 8.6) conforms to the `SceneGeometry` interface and passes `validateGeometryDefinition`.
2. A minimal geometry (1 required slot, 1 compatible camera, description) is valid.
3. A geometry with fog configuration passes validation.
4. A geometry without fog passes validation.
5. A geometry with `preferred_aspect` passes validation.

**Geometry definition validation tests:**
1. A valid geometry definition (the seed tunnel example) returns empty error array.
2. Each validation rule (11 rules listed) is tested individually — one error condition per test, verify the error path and message.
3. Multiple errors in a single geometry return all errors (not just the first).
4. Edge case: geometry name with hyphens (`'my-geometry'`) is rejected.
5. Edge case: slot key starting with underscore (`'_floor'`) is rejected.
6. Edge case: camera name with hyphens (`'tunnel-push'`) is rejected.
7. Edge case: slot description is empty string — rejected.

**Registry tests:**
1. `registerGeometry` followed by `getGeometry` returns the registered geometry.
2. `registerGeometry` with duplicate name throws with geometry name in message.
3. `registerGeometry` with invalid definition throws with all validation error details.
4. `getGeometryNames` after registering 3 geometries returns all 3 names.
5. `getGeometryRegistry` returns a deeply frozen object — assignment to nested properties (e.g., `registry.tunnel.slots.floor.description = 'hacked'`) throws `TypeError`.
6. Mutation of a returned geometry's slot position tuple (e.g., `geo.slots.floor.position[0] = 99`) throws `TypeError`.
7. `getGeometry` with unregistered name returns `undefined`.
8. `registerGeometry` after `getGeometryRegistry()` has been called throws with "registry is locked" message.
9. `registerGeometry` after `getGeometry()` has been called (even with unregistered name) throws with "registry is locked" message.
10. `registerGeometry` after `getGeometryNames()` has been called throws with "registry is locked" message.

**Slot utility tests:**
1. `getRequiredSlotNames` for the tunnel geometry returns `['floor', 'left_wall', 'right_wall', 'end_wall']` (4 required slots per seed).
2. `getOptionalSlotNames` for the tunnel geometry returns `['ceiling']` (1 optional slot per seed).
3. `getAllSlotNames` returns the union of required and optional.
4. `isCameraCompatible` returns `true` for a camera in the list, `false` for one not in the list.

**Slot naming convention tests:**
1. Valid names: `floor`, `left_wall`, `near_fg`, `end_wall`, `back_wall`.
2. Invalid names: `Floor`, `left-wall`, `3d_floor`, `_private`, `wall left`, ``.

### Relevant Testable Claims
- **TC-04** (partial): The type system ensures that geometries define all spatial relationships, validating that an LLM never specifies raw XYZ coordinates.
- **TC-07** (partial): `validateGeometryDefinition` catches internal definition errors. Manifest-level validation (TC-07's primary scope) is OBJ-017.
- **TC-08** (partial): The type system must be flexible enough to express all 8 proposed geometries without modification.

## Integration Points

### Depends on

| Dependency | What OBJ-005 imports |
|---|---|
| **OBJ-003** (Spatial math) | `Vec3`, `EulerRotation`, `Size2D` types for PlaneSlot fields. `PlaneTransform` interface as the base type for `PlaneSlot`. No runtime functions imported — types only. |

### Consumed by

| Downstream | How it uses OBJ-005 |
|---|---|
| **OBJ-011** (Puppeteer-to-page message protocol) | References `SceneGeometry` and `PlaneSlot` types in scene setup messages (geometry name, slot assignments, slot spatial data sent to the browser page). |
| **OBJ-017** (Manifest structural validation) | Imports `getGeometry`, `getRequiredSlotNames`, `getAllSlotNames` to validate that manifest plane keys match the geometry's slot contract. |
| **OBJ-018-025** (Individual geometry implementations) | Each imports `SceneGeometry`, `PlaneSlot`, `FogConfig` types and `registerGeometry` to define and register a concrete geometry. |
| **OBJ-036** (Scene sequencer) | Imports `getGeometry` to look up the geometry for each scene when routing manifest scenes. |
| **OBJ-039** (Page-side geometry instantiation) | Imports `PlaneSlot` (and accepts `PlaneTransform` subset) to create Three.js meshes from slot definitions — reads `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune`. |
| **OBJ-040** (Plane sizing / edge-reveal validation) | Imports `SceneGeometry`, `PlaneSlot` (and accepts `PlaneTransform` subset) to compute required plane oversizing and validate that camera paths don't reveal plane edges. |
| **OBJ-041** (Geometry-camera compatibility validation) | Imports `SceneGeometry`, `isCameraCompatible`, `getGeometryRegistry` to cross-reference geometry and camera path compatibility. |
| **OBJ-044** (Per-frame opacity animation) | May extend `PlaneSlot` or reference its structure for opacity keyframe targeting. |
| **OBJ-045** (Portrait/vertical adaptation) | References `SceneGeometry.preferred_aspect` and `PlaneSlot.size` for aspect ratio adaptation logic. |
| **OBJ-071** (SKILL.md geometry reference) | Uses `SceneGeometry.description`, `PlaneSlot.description`, slot names, and `preferred_aspect` to generate documentation. |
| **OBJ-080** (Dynamic plane count) | May extend `PlaneSlot` or `SceneGeometry` if dynamic slot counts are supported. |
| **OBJ-081** (Lighting) | May reference `PlaneSlot` for material type decisions (fogImmune, transparent affect material choice). |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        index.ts           # Barrel export
        types.ts           # PlaneSlot, SceneGeometry, FogConfig, GeometryRegistry,
                           # GeometryValidationError
        registry.ts        # registerGeometry, getGeometry, getGeometryRegistry,
                           # getGeometryNames
        validate.ts        # validateGeometryDefinition
        slot-utils.ts      # getRequiredSlotNames, getOptionalSlotNames,
                           # getAllSlotNames, isCameraCompatible
```

Individual geometry implementations (OBJ-018 through OBJ-025) will add files like `stage.ts`, `tunnel.ts`, etc. in this same directory, each importing from `./types` and calling `registerGeometry()`.

## Open Questions

### OQ-A: Should PlaneSlot support `size_mode` for texture auto-sizing?

Currently `PlaneSlot.size` defines the plane's world-unit dimensions. OBJ-040 handles auto-sizing planes from texture aspect ratios. Should the slot define *how* to reconcile texture aspect ratio vs slot size — e.g., `size_mode: 'fill' | 'contain' | 'stretch'`?

**Recommendation:** Defer to OBJ-040. The slot's `size` is the maximum bounding box; how textures fit within it is OBJ-040's responsibility. Adding `size_mode` here would prematurely couple the type contract to rendering behavior.

### OQ-B: Should `compatible_cameras` support wildcard entries?

Some geometries might work with "any lateral track" or "any static camera." A wildcard like `'lateral_track_*'` could reduce maintenance.

**Recommendation:** No. Keep it as explicit string list. Wildcards add regex complexity and make it harder for LLMs and validators to reason about compatibility. If a geometry works with many cameras, list them all. The list is finite and small (seed proposes ~11 camera presets total).

### OQ-C: Should there be a `SceneGeometryWithDefaults` type that includes resolved default values?

When the manifest omits optional fields (e.g., `fog`, `camera_params`), the engine needs to fill in defaults. Should there be a separate type representing "a geometry with all optionals resolved"?

**Recommendation:** Not at this layer. Default resolution is the scene sequencer's job (OBJ-036). The type contract defines the shape; the sequencer fills gaps.

### OQ-D: Registry reset for testing

The lock-on-first-read registry design means unit tests that test both registration and post-lock behavior need a way to reset registry state between tests. This is an internal testing concern, not a public API contract. The implementation should expose a non-exported or test-only `_resetRegistry()` function (prefixed with underscore to signal internal use), or use module-level isolation via Jest's `jest.isolateModules()` or equivalent.
