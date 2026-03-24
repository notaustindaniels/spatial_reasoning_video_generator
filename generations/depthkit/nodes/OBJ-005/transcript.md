# Deliberation Transcript: OBJ-005

---

## Round 1 — spec_author

I'll start by examining the existing codebase to understand what OBJ-003 has already implemented, then propose a complete spec for OBJ-005.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me examine the existing codebase structure and OBJ-003's implementation to understand what's already in place.
[Tool: Glob]
  Input: {
  "pattern": "**/spatial/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-005/**/*"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-003/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/transcript.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md"
}
[Tool Result]      1→# Specification: Coordinate System and Spatial Math Reference (OBJ-003)
     2→
     3→## Summary
     4→
     5→OBJ-003 codifies the spatial foundation for all depthkit geometry and camera work: the Three.js right-handed coordinate conventions, the relationship between camera FOV / distance and visible area, plane sizing math, and utility functions for computing spatial relationships. This module is a pure-math reference library with zero rendering dependencies — it exports constants, types, and deterministic computation functions that every downstream geometry definition (OBJ-005), camera path preset (OBJ-006), easing/interpolation module (OBJ-007), scene sequencer (OBJ-010), and edge-reveal validator (OBJ-040) will import.
     6→
     7→## Interface Contract
     8→
     9→### Constants
    10→
    11→```typescript
    12→// src/spatial/constants.ts
    13→
    14→/** Three.js right-handed coordinate system conventions */
    15→export const AXIS = {
    16→  RIGHT: [1, 0, 0... [truncated]

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**/*.ts"
}
[Tool Result] No files found
Now let me check the meta files for key downstream objectives that depend on OBJ-005 to understand what they need from this contract:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-005",
     3→  "description": "Scene geometry type contract -- TypeScript interfaces for SceneGeometry and PlaneSlot per Section 8.6. PlaneSlot defines position [x,y,z], rotation [rx,ry,rz], size [w,h], required flag, and description. SceneGeometry defines name, slots record, compatible_cameras list, default_camera, and optional fog config. Establishes slot naming conventions and required-vs-optional plane semantics.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Defines the type system for all 8 scene geometry implementations."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-018/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-040/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-010/meta.json"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-011/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-018",
     3→  "description": "Stage scene geometry -- the default geometry. Large backdrop plane at z=-30, floor plane angled down from camera (rotation [-PI/2,0,0]), subject plane at z=-5. Classic 'subject in front of a background' setup with real perspective on the floor. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2. Addresses TC-01 (five planes sufficient).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 geometry. The simplest, most fundamental geometry -- used as the basis for SKILL.md examples."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-040",
     3→  "description": "Plane sizing and oversizing system -- visible area calculation per Section 8.3 (visible_height = 2 * d * tan(FOV/2)), camera-motion-dependent oversizing factors to prevent edge reveals during camera movement, edge-reveal prevention math, AND texture-to-plane auto-sizing algorithm per Section 8.9 (how planes adapt dimensions from loaded texture aspect ratios while maintaining geometry spatial structure -- letterbox vs crop vs scale decisions).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-006", "OBJ-003", "OBJ-015"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 spatial feature. Expanded to include texture auto-sizing per Round 2 Issue 6. OBJ-015 dep added for texture aspect ratio data."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-010",
     3→  "description": "Three.js page shell, build/bundle strategy, and scene renderer skeleton -- HTML shell (src/page/index.html), page-side module loading strategy (CDN vs bundled Three.js, ESM vs build step via esbuild/vite), mechanism for making TypeScript geometry definitions available to the browser page, Three.js Scene/PerspectiveCamera/WebGLRenderer initialization, and WebGL canvas setup. This is the authoritative decision point for the Node.js/browser code-split architecture.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001", "OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Expanded to cover build/bundle strategy per Round 2 Issue 5."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-011",
     3→  "description": "Full Puppeteer-to-page message protocol -- defines every message type crossing the Node.js/browser boundary. Includes: frame step commands (frame number, fps, totalFrames), scene setup/teardown commands (geometry instantiation, texture URLs, slot assignments), texture loading completion signals, transition signals (prepare next scene, start overlap rendering), and error reporting from page back to orchestrator. Single source of truth for the cross-boundary contract.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-010", "OBJ-005"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Expanded scope per Round 2 Issue 7 to cover full protocol, not just frame stepping. Depends on OBJ-005 for geometry slot structures in sce... [truncated]
Let me also check the meta for a few more key downstream consumers:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-036/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-036",
     3→  "description": "Scene sequencer -- routes manifest scenes to geometries, computes per-scene normalized time from the global frame/timestamp (absorbs per-scene time normalization from the virtualized clock), manages scene lifecycle (setup, active rendering, teardown), handles transition timing windows and overlap scheduling. Uses the transition contract (OBJ-008) to compute when scenes overlap.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-035", "OBJ-005", "OBJ-008"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration. Absorbs per-scene time normalization (moved from OBJ-009 per Round 2 Issue 8). Depends on OBJ-008 per Round 2 Issue 2."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-039/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-039",
     3→  "description": "Three.js page-side geometry instantiation -- how geometry definitions are loaded and instantiated in the browser page, mesh creation from PlaneSlot definitions (position, rotation, size), texture application to meshBasicMaterial, and scene graph construction. Responds to scene setup commands from the message protocol (OBJ-011).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-010", "OBJ-005", "OBJ-015", "OBJ-011"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration. Added OBJ-011 dep per Round 4 Issue B -- needs message protocol for scene setup commands."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-041",
     3→  "description": "Geometry-camera spatial compatibility validation -- cross-reference validation ensuring camera paths are compatible with chosen geometries (a tunnel_push doesn't work on a stage geometry), oversizing sufficiency checks. Produces spatial validation rules that feed into the manifest validation pipeline (OBJ-017 handles structural validation; OBJ-041 handles spatial compatibility). TC-08 coverage analysis (do 8 geometries cover the design space).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 spatial feature. Boundary clarification: structural validation = OBJ-017, spatial compatibility = OBJ-041."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-044/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-044",
     3→  "description": "Per-frame plane opacity animation -- manifest schema extension to support per-plane opacity keyframes, meshBasicMaterial transparent mode handling, use cases (foreground fog fading in/out, subject materializing). Addresses OQ-01 (should planes support per-frame opacity animation).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-004", "OBJ-010"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 spatial feature. Medium priority. Addresses OQ-01."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-017/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-017",
     3→  "description": "Geometry-specific structural manifest validation -- per-geometry Zod refinements ensuring plane keys in the manifest match the geometry's expected slot requirements (e.g., tunnel requires floor, left_wall, right_wall, end_wall). Enforces required vs optional slots, validates geometry name existence. Structural validation only -- spatial compatibility rules (camera+geometry compatibility) come from OBJ-041 and are additive. Covers TC-07.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-004", "OBJ-005"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Boundary clarification: OBJ-017 = structural correctness, OBJ-041 = spatial correctness."
    12→}
    13→
Now I have a thorough understanding of the dependency and downstream landscape. Let me propose the complete specification.

---

# Proposed Specification: Scene Geometry Type Contract (OBJ-005)

## Summary

OBJ-005 defines the TypeScript type system for all scene geometries in depthkit: the `PlaneSlot` interface describing a single named position in a 3D scene, the `SceneGeometry` interface describing a complete spatial arrangement of planes, the `FogConfig` interface for depth-based atmospheric fading, a geometry registry type for runtime lookup, and the slot naming conventions that all 8 geometry implementations (OBJ-018 through OBJ-025) must follow. This is a pure type/contract module — it defines the shape of geometry data, not any specific geometry's values. It imports spatial primitives from OBJ-003 and is consumed by every downstream objective that creates, validates, instantiates, or queries scene geometries.

## Interface Contract

### Core Types

```typescript
// src/scenes/geometries/types.ts

import type { Vec3, EulerRotation, Size2D } from '../../spatial';

/**
 * Configuration for Three.js fog, providing depth-based atmospheric fading.
 * Enhances the 2.5D effect by hiding hard edges on distant planes
 * and creating atmospheric perspective (seed Section 8.10).
 */
export interface FogConfig {
  /** CSS-style hex color string for the fog (e.g., '#000000'). */
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
 * PlaneSlots are authored once per geometry definition and do not change
 * at runtime. The position, rotation, and size values are defaults —
 * the manifest may override them via `position_override` (seed AP-08),
 * but the slot definition provides the proven-safe baseline.
 */
export interface PlaneSlot {
  /**
   * Position in world space [x, y, z].
   * Uses OBJ-003 coordinate conventions: +X right, +Y up, +Z toward viewer.
   */
  position: Vec3;

  /**
   * Euler rotation in radians [rx, ry, rz].
   * Applied in Three.js default order (XYZ).
   * Use PLANE_ROTATIONS constants from OBJ-003 for standard orientations.
   */
  rotation: EulerRotation;

  /**
   * Plane dimensions in world units [width, height].
   * This is the geometry size of the mesh, not the texture resolution.
   * Textures are mapped onto this plane; the renderer (OBJ-039) may
   * adjust the plane's aspect ratio to match the loaded texture
   * per OBJ-040's auto-sizing rules, within bounds set by this size.
   */
  size: Size2D;

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
   * The renderer (OBJ-039) maps this to `mesh.renderOrder`.
   */
  renderOrder?: number;

  /**
   * Whether this plane's material should be created with
   * `transparent: true` and expect an alpha channel in its texture.
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
 */
export interface SceneGeometry {
  /**
   * Unique identifier for this geometry. Must match the key used
   * in the geometry registry. Lowercase, underscore-separated.
   * Examples: 'stage', 'tunnel', 'canyon', 'flyover'
   */
  name: string;

  /**
   * The named plane slots that make up this geometry.
   * Keys are slot names (lowercase, underscore-separated).
   * Values define the spatial placement of each slot.
   *
   * The manifest's `planes` object must use these exact keys.
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
   * Must contain at least one entry. Must include `default_camera`.
   */
  compatible_cameras: readonly string[];

  /**
   * The camera path preset used when the manifest omits
   * the `camera` field. Must be a member of `compatible_cameras`.
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
   * Used in SKILL.md documentation. Should describe the spatial
   * feel and typical use case, not the technical layout.
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
 * Individual geometry modules register themselves by calling
 * `registerGeometry()` at module load time.
 *
 * @returns A frozen GeometryRegistry. Mutation attempts throw at runtime.
 */
export function getGeometryRegistry(): Readonly<GeometryRegistry>;

/**
 * Retrieves a single geometry by name.
 *
 * @param name - The geometry name (e.g., 'tunnel', 'stage').
 * @returns The SceneGeometry definition, or undefined if not registered.
 */
export function getGeometry(name: string): SceneGeometry | undefined;

/**
 * Registers a scene geometry in the global registry.
 * Called by each geometry module (OBJ-018 through OBJ-025) at load time.
 *
 * @param geometry - A fully-defined SceneGeometry.
 * @throws Error if a geometry with the same name is already registered
 *         (prevents silent overwrites from duplicate registrations).
 * @throws Error if the geometry fails structural validation
 *         (see validateGeometryDefinition).
 */
export function registerGeometry(geometry: SceneGeometry): void;

/**
 * Returns an array of all registered geometry names.
 * Useful for validation error messages ("expected one of: stage, tunnel, ...").
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
 * 1. `name` is non-empty, lowercase, underscore-separated (matches /^[a-z][a-z0-9_]*$/).
 * 2. `slots` contains at least one entry.
 * 3. All slot keys match the naming convention (lowercase, underscore-separated: /^[a-z][a-z0-9_]*$/).
 * 4. At least one slot is marked `required: true`.
 * 5. `compatible_cameras` is non-empty.
 * 6. `default_camera` appears in `compatible_cameras`.
 * 7. If `fog` is present: `fog.near >= 0`, `fog.far > fog.near`,
 *    `fog.color` matches /^#[0-9a-fA-F]{6}$/.
 * 8. `description` is non-empty.
 * 9. All slot `size` components are > 0.
 * 10. No duplicate slot keys (enforced by Record type but verified at runtime
 *     in case of programmatic construction).
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
 * @returns Array of slot name strings where `required === true`.
 */
export function getRequiredSlotNames(geometry: SceneGeometry): string[];

/**
 * Returns the names of all optional slots for a geometry.
 *
 * @param geometry - The scene geometry definition.
 * @returns Array of slot name strings where `required === false`.
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

export type { PlaneSlot, SceneGeometry, FogConfig, GeometryRegistry, GeometryValidationError } from './types';
export { getGeometryRegistry, getGeometry, registerGeometry, getGeometryNames } from './registry';
export { validateGeometryDefinition } from './validate';
export { getRequiredSlotNames, getOptionalSlotNames, getAllSlotNames, isCameraCompatible } from './slot-utils';
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

This module exports TypeScript interfaces, type definitions, a simple in-memory registry, and validation/utility functions. It does NOT import Three.js, Puppeteer, or any rendering library. The `PlaneSlot.position` is a `Vec3` (plain tuple from OBJ-003), not a `THREE.Vector3`. Conversion to Three.js types happens at the rendering boundary (OBJ-039).

**Rationale:** The geometry type contract is consumed on both sides of the Node.js/browser split. Manifest validation (OBJ-017) runs in Node.js before Puppeteer launches. Page-side instantiation (OBJ-039) runs in the browser. Keeping the contract free of rendering dependencies ensures it works in both contexts. Follows the same pattern as OBJ-003.

### D2: Registry pattern with explicit registration

Geometries register themselves via `registerGeometry()` rather than being hardcoded in a central map. Each geometry module (OBJ-018 through OBJ-025) calls `registerGeometry(stageGeometry)` at import time. The registry is then frozen after all registrations.

**Rationale:** (a) Decoupled — adding a new geometry doesn't require modifying a central file. (b) Self-validating — `registerGeometry` validates the definition before accepting it, catching definition errors at load time. (c) Prevents silent overwrites — duplicate names throw immediately. (d) The registry must be populated before manifest validation runs; the engine's initialization sequence guarantees this.

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

## Acceptance Criteria

- [ ] **AC-01:** `PlaneSlot` interface includes fields `position: Vec3`, `rotation: EulerRotation`, `size: Size2D`, `required: boolean`, `description: string` — all matching the types defined in OBJ-003.
- [ ] **AC-02:** `SceneGeometry` interface includes fields `name: string`, `slots: Record<string, PlaneSlot>`, `compatible_cameras: readonly string[]`, `default_camera: string`, `fog?: FogConfig`, `description: string`.
- [ ] **AC-03:** `registerGeometry()` throws an `Error` when called with a geometry whose `name` is already registered.
- [ ] **AC-04:** `registerGeometry()` throws an `Error` when the geometry definition fails `validateGeometryDefinition` (i.e., has structural errors).
- [ ] **AC-05:** `validateGeometryDefinition` returns errors for: empty `name`, name not matching `/^[a-z][a-z0-9_]*$/`, empty `slots`, slot keys not matching `/^[a-z][a-z0-9_]*$/`, no required slot, empty `compatible_cameras`, `default_camera` not in `compatible_cameras`, `fog.far <= fog.near`, `fog.near < 0`, `fog.color` not matching hex pattern, empty `description`, slot `size` components `<= 0`.
- [ ] **AC-06:** `getRequiredSlotNames` for a geometry with 3 required and 2 optional slots returns exactly the 3 required slot names.
- [ ] **AC-07:** `getAllSlotNames` returns every key in the geometry's `slots` record.
- [ ] **AC-08:** `isCameraCompatible` returns `true` only for camera names in the geometry's `compatible_cameras` list.
- [ ] **AC-09:** `getGeometry('nonexistent')` returns `undefined`, does not throw.
- [ ] **AC-10:** The seed's tunnel geometry example (Section 8.6) can be expressed using these interfaces without modification — specifically, a geometry with slots `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall` with the positions, rotations, and sizes from the seed passes `validateGeometryDefinition`.
- [ ] **AC-11:** The module has zero runtime dependencies beyond OBJ-003's spatial types and standard JavaScript.
- [ ] **AC-12:** All types and functions are accessible via `import { ... } from './scenes/geometries'` (barrel export).
- [ ] **AC-13:** `getGeometryRegistry()` returns a frozen object — attempting to add/modify properties at runtime throws a `TypeError`.
- [ ] **AC-14:** `PlaneSlot.renderOrder`, `PlaneSlot.transparent`, and `PlaneSlot.fogImmune` are optional fields (TypeScript `?:`). Omitting them does not cause validation errors.
- [ ] **AC-15:** `SceneGeometry.preferred_aspect` is optional. Omitting it does not cause validation errors.

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
| default_camera not in list | `default_camera` | `"default_camera 'slow_push' must be in compatible_cameras"` |
| Fog near < 0 | `fog.near` | `"fog.near must be >= 0, got -5"` |
| Fog far <= near | `fog.far` | `"fog.far must be > fog.near (got near=10, far=5)"` |
| Fog color invalid | `fog.color` | `"fog.color must be a hex color (#RRGGBB), got 'black'"` |
| Empty description | `description` | `"description must be non-empty"` |
| Slot size zero/negative | `slots.floor.size` | `"slot 'floor' size components must be > 0, got [0, 30]"` |

### Registry Errors

| Condition | Error Type | Message Pattern |
|---|---|---|
| Duplicate registration | `Error` | `"Geometry 'tunnel' is already registered"` |
| Invalid geometry | `Error` | `"Cannot register geometry 'tunnel': {validation error details}"` |

### Boundary Behaviors

- **Geometry with only one slot:** Valid if that slot is `required: true`. Unusual but not invalid — the `close_up` geometry might have only a `subject` slot.
- **Geometry with many slots (>10):** No upper limit enforced. The geometry definition validator does not restrict slot count. Seed TC-01 says 3-5 is sufficient for 90% of cases, but the type system allows more.
- **Slot with `renderOrder: 0`:** Valid. This is the default Three.js render order. Specifying it explicitly is harmless.
- **Fog with `near: 0`:** Valid. Means fog starts immediately at the camera.
- **`compatible_cameras` with one entry:** Valid. Means only one camera path works with this geometry.
- **Calling `getGeometryRegistry()` before any registrations:** Returns an empty frozen object. Not an error — the engine's initialization sequence should register geometries before validation.
- **`getGeometry` with empty string:** Returns `undefined`. Not a special case.

## Test Strategy

### Unit Tests

**PlaneSlot construction tests:**
1. A PlaneSlot with all required fields and no optional fields is type-valid.
2. A PlaneSlot with all fields (including `renderOrder`, `transparent`, `fogImmune`) is type-valid.
3. The seed tunnel geometry's slot definitions (Section 8.6) conform to the `PlaneSlot` interface.

**SceneGeometry construction tests:**
1. The seed tunnel geometry example (Section 8.6) conforms to the `SceneGeometry` interface.
2. A minimal geometry (1 required slot, 1 compatible camera, description) is valid.
3. A geometry with fog configuration passes validation.
4. A geometry without fog passes validation.

**Geometry definition validation tests:**
1. A valid geometry definition (the seed tunnel example) returns empty error array.
2. Each validation rule (10 rules listed in AC-05) is tested individually — one error condition per test, verify the error path and message.
3. Multiple errors in a single geometry return all errors (not just the first).
4. Edge case: geometry name with hyphens (`'my-geometry'`) is rejected.
5. Edge case: slot key starting with underscore (`'_floor'`) is rejected.

**Registry tests:**
1. `registerGeometry` followed by `getGeometry` returns the registered geometry.
2. `registerGeometry` with duplicate name throws with geometry name in message.
3. `registerGeometry` with invalid definition throws with validation details.
4. `getGeometryNames` after registering 3 geometries returns all 3 names.
5. `getGeometryRegistry` returns a frozen object — assignment throws `TypeError`.
6. `getGeometry` with unregistered name returns `undefined`.

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
| **OBJ-003** (Spatial math) | `Vec3`, `EulerRotation`, `Size2D` types for PlaneSlot fields. No runtime functions imported — types only. |

### Consumed by

| Downstream | How it uses OBJ-005 |
|---|---|
| **OBJ-011** (Puppeteer-to-page message protocol) | References `SceneGeometry` and `PlaneSlot` types in scene setup messages (geometry name, slot assignments, slot spatial data sent to the browser page). |
| **OBJ-017** (Manifest structural validation) | Imports `getGeometry`, `getRequiredSlotNames`, `getAllSlotNames` to validate that manifest plane keys match the geometry's slot contract. |
| **OBJ-018–025** (Individual geometry implementations) | Each imports `SceneGeometry`, `PlaneSlot`, `FogConfig` types and `registerGeometry` to define and register a concrete geometry. |
| **OBJ-036** (Scene sequencer) | Imports `getGeometry` to look up the geometry for each scene when routing manifest scenes. |
| **OBJ-039** (Page-side geometry instantiation) | Imports `PlaneSlot` to create Three.js meshes from slot definitions — reads `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune`. |
| **OBJ-040** (Plane sizing / edge-reveal validation) | Imports `SceneGeometry`, `PlaneSlot` to compute required plane oversizing and validate that camera paths don't reveal plane edges. |
| **OBJ-041** (Geometry-camera compatibility validation) | Imports `SceneGeometry`, `isCameraCompatible`, `getGeometryRegistry` to cross-reference geometry and camera path compatibility. |
| **OBJ-044** (Per-frame opacity animation) | May extend `PlaneSlot` or reference its structure for opacity keyframe targeting. |
| **OBJ-045** (Additional spatial features) | References `PlaneSlot` for any extended plane properties. |
| **OBJ-071** (SKILL.md geometry reference) | Uses `SceneGeometry.description`, `PlaneSlot.description`, slot names, and `preferred_aspect` to generate documentation. |
| **OBJ-080** (Dynamic plane count) | May extend `PlaneSlot` or `SceneGeometry` if dynamic slot counts are supported. |
| **OBJ-081** (Lighting) | May reference `PlaneSlot` for material type decisions. |

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

---

I believe this specification is complete and covers the full scope of OBJ-005. I'd like the Challenger to review and verify. Key decisions I'd like scrutiny on:

1. The addition of `renderOrder`, `transparent`, and `fogImmune` to PlaneSlot (beyond what the seed's Section 8.6 defines) — are these justified at this layer, or should they be deferred to downstream consumers?
2. The registry pattern (register at import time, validate on registration, freeze on access) — is this robust enough for the dual Node.js/browser context?
3. The slot naming conventions and reserved-name table — is this the right level of constraint, or is it over/under-specifying?

---

## Round 2 — spec_challenger

I'll review the proposed spec systematically. Let me first verify a few things in the codebase.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]
Let me check a few more downstream consumers to verify integration assumptions.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-045/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-045",
     3→  "description": "Portrait/vertical adaptation -- how scene geometries adapt to 9:16 (1080x1920) aspect ratio. FOV adjustments, plane resizing strategy (taller walls, narrower floors for tunnel in portrait), whether geometries need parallel variants or can auto-adapt based on composition aspect ratio. Addresses OQ-04 and C-04 (must support 1080x1920).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-006", "OBJ-004"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 spatial feature. Medium priority. Addresses OQ-04."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-080/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-080",
     3→  "description": "Dynamic plane count exploration -- variable slot counts per geometry instance (e.g., stage with 1-3 background planes at varying Z-depths instead of a fixed single backdrop). Adds flexibility but complicates the slot contract. Addresses OQ-08. Low priority -- may be deferred to post-V1.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 6 exploration. Low priority. Addresses OQ-08."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-081/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-081",
     3→  "description": "Lighting system exploration -- ambient and directional lights with meshStandardMaterial for more atmospheric scenes (e.g., dark tunnel with light at the end). Currently the engine uses meshBasicMaterial (unlit). Adds complexity but enables dramatic lighting. Addresses OQ-09. Low priority -- may be deferred to post-V1.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-010", "OBJ-005"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 6 exploration. Low priority. Addresses OQ-09."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-071/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-071",
     3→  "description": "SKILL.md geometry and camera reference sections -- per-geometry documentation (description, slots, when to use, visual effect), per-camera-path documentation (description, motion type, compatible geometries, when to use). At minimum covers stage and tunnel geometries in detail. Per Section 4.9.",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-070", "OBJ-005", "OBJ-006", "OBJ-018", "OBJ-019"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 integration. High priority. OBJ-056 (manifest generation via Claude API) depends on this."
    12→}
    13→
Good. Now let me review the OBJ-003 spec more carefully for type compatibility:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": 1,
  "limit": 80
}
[Tool Result]      1→# Specification: Coordinate System and Spatial Math Reference (OBJ-003)
     2→
     3→## Summary
     4→
     5→OBJ-003 codifies the spatial foundation for all depthkit geometry and camera work: the Three.js right-handed coordinate conventions, the relationship between camera FOV / distance and visible area, plane sizing math, and utility functions for computing spatial relationships. This module is a pure-math reference library with zero rendering dependencies — it exports constants, types, and deterministic computation functions that every downstream geometry definition (OBJ-005), camera path preset (OBJ-006), easing/interpolation module (OBJ-007), scene sequencer (OBJ-010), and edge-reveal validator (OBJ-040) will import.
     6→
     7→## Interface Contract
     8→
     9→### Constants
    10→
    11→```typescript
    12→// src/spatial/constants.ts
    13→
    14→/** Three.js right-handed coordinate system conventions */
    15→export const AXIS = {
    16→  RIGHT: [1, 0, 0... [truncated]
Now I have a thorough picture. Here's my review:

---

## Challenger Review — Round 2

### Points of Agreement (what's sound)

1. **D1 (types-only, no Three.js dependency)** — Correct. Matches OBJ-003's pattern and the dual Node.js/browser constraint.
2. **D7 (string-based camera references)** — Correct. Avoids circular dep between OBJ-005 and OBJ-006.
3. **D8 (regex not enum for slot names)** — Correct. The seed shows different geometries need different slots.
4. **D6 (separation of geometry validation from manifest validation)** — Clean boundary. OBJ-005 validates definitions, OBJ-017 validates manifests.
5. **Reserved slot name table** — Useful, well-scoped, and correctly advisory rather than enforced by the type system.
6. **File placement** — Clean, follows the seed's project structure (Section 4.5).
7. **OQ-A, OQ-B, OQ-C** — All correctly deferred. Good judgment.

### Issues

---

#### Issue 1: `Vec3` is `readonly` in OBJ-003 but `PlaneSlot` fields use it mutably (MAJOR)

OBJ-003 defines `Vec3 = readonly [number, number, number]`. The `PlaneSlot` interface uses `position: Vec3` and `rotation: EulerRotation` — both readonly tuples. But the seed's Section 8.6 `PlaneSlot` interface uses plain `[number, number, number]` (mutable). More importantly, the spec says in AP-08 that the manifest may override positions via `position_override`. If the geometry definition's `PlaneSlot.position` is `readonly`, then any code that wants to apply overrides needs to create a new tuple rather than mutating — which is fine, but the spec never addresses how overrides interact with the readonly contract.

**Severity:** Major. An implementer won't know whether `PlaneSlot` values are treated as immutable templates (clone-then-modify for overrides) or mutable state.

**Proposed fix:** Add a design decision (or a note on `PlaneSlot.position`) explicitly stating: "PlaneSlot values in a registered SceneGeometry are immutable templates. When the manifest provides `position_override`, the scene sequencer (OBJ-036) or page-side renderer (OBJ-039) creates a new `PlaneTransform` with the override applied, rather than mutating the slot definition. The `readonly` tuple type enforces this at compile time." This also aligns with the registry being frozen.

---

#### Issue 2: `FogConfig.color` validation is too narrow (MINOR)

The spec validates `fog.color` against `/^#[0-9a-fA-F]{6}$/`. Three.js `Fog` constructor accepts a `THREE.ColorRepresentation`, which includes hex integers (`0x000000`), CSS color names (`'black'`), and RGB strings. However, the spec is a *type contract*, not a rendering module — and constraining to 6-digit hex is reasonable for manifest authoring by an LLM. 

**Severity:** Minor. The constraint is reasonable but the spec should explicitly state *why* only `#RRGGBB` is accepted.

**Proposed fix:** Add a one-line note to `FogConfig.color`: "Constrained to `#RRGGBB` hex format for manifest serialization predictability and LLM authorability. The renderer converts to `THREE.Color` at the boundary."

---

#### Issue 3: Registry freezing semantics are underspecified (MAJOR)

The spec says `getGeometryRegistry()` returns a frozen object (AC-13). But it doesn't specify:
- **When** does freezing happen? On first call to `getGeometryRegistry()`? After a specific initialization step? 
- Can `registerGeometry()` be called *after* `getGeometryRegistry()` has been called? If the registry is frozen on first access, late registrations silently fail (no error, just not visible). If the registry is frozen at a specific point, what triggers it?
- What about the `PlaneSlot` objects inside? `Object.freeze` is shallow — the returned `GeometryRegistry` has frozen top-level keys, but `geometry.slots.floor.position` could still be mutated unless deep-frozen.

**Severity:** Major. An implementer must decide freezing strategy without guidance, and shallow vs deep freeze is a correctness issue (mutation of a registered geometry's slot positions would be a silent, catastrophic bug).

**Proposed fix:** Add to D2 or a new design decision:
- "The registry returns a **deep-frozen** snapshot. All `SceneGeometry` objects and their nested `PlaneSlot` values are recursively frozen. `readonly` types enforce this at compile time; `Object.freeze` (deep) enforces it at runtime."
- "`registerGeometry()` may be called at any time before or after `getGeometryRegistry()`. Each call to `getGeometryRegistry()` returns a fresh frozen snapshot of the current registry state. Late registrations are visible in subsequent calls."
- OR: "The registry is append-only. `registerGeometry()` throws after `getGeometryRegistry()` has been called, enforcing a clear initialization phase." (Pick one — both are valid, but the spec must choose.)

---

#### Issue 4: `position_override` mentioned but not defined (MAJOR)

The spec references `position_override` from the seed (AP-08) in the `PlaneSlot` doc comment: "the manifest may override them via `position_override`." But OBJ-005's scope is the *geometry type contract*. The manifest schema (OBJ-004) defines what override fields exist. This spec should not reference a manifest field that it doesn't define and that may or may not exist yet.

More critically: does the `PlaneSlot` interface need to accommodate overrides? If a manifest can override `position`, `rotation`, and `size`, does there need to be a "resolved PlaneSlot" type that represents the merged result? Or is that OBJ-036/OBJ-039's problem?

**Severity:** Major. The reference creates an implicit dependency on an undefined manifest field.

**Proposed fix:** Either:
(a) Remove the `position_override` reference entirely. Replace with: "These values are the geometry's defaults. Downstream consumers (OBJ-036, OBJ-039) may apply per-scene overrides from the manifest, producing a resolved transform. The override mechanism is defined by the manifest schema (OBJ-004), not by this contract." Or:
(b) Define a `ResolvedPlaneSlot` type here (extending `PlaneSlot` with the override applied). But this feels like scope creep — I'd recommend (a).

---

#### Issue 5: No validation of `renderOrder` range (MINOR)

`PlaneSlot.renderOrder` is `number` with no range constraint. Three.js `renderOrder` accepts any integer, but the spec's `validateGeometryDefinition` doesn't check it. Should it be non-negative? Integer-only? 

**Severity:** Minor. Three.js handles any number, so this won't break rendering. But an LLM could author `renderOrder: 999999` or `renderOrder: -50` without feedback.

**Proposed fix:** Add a note that `renderOrder` is not range-validated by `validateGeometryDefinition` — it is the geometry author's responsibility to use small, relative values (e.g., 0-10). Or add validation that it must be a non-negative integer. I'd lean toward the note — keeping validation simple.

---

#### Issue 6: Seed Section 8.6 has `PlaneTransform` in OBJ-003, but OBJ-005 doesn't reference it (MINOR)

OBJ-003 exports a `PlaneTransform` type: `{ position: Vec3; rotation: EulerRotation; size: Size2D; }`. This is essentially the spatial subset of `PlaneSlot`. The spec doesn't mention whether `PlaneSlot` extends `PlaneTransform` or is a separate type that happens to have the same fields. 

If `PlaneSlot extends PlaneTransform`, then downstream consumers (OBJ-039, OBJ-040) that only need the spatial data can accept `PlaneTransform` and work with both raw transforms and full slots. If they're separate types with coincidentally identical fields, duck typing works in TypeScript but the relationship is undocumented.

**Severity:** Minor but worth clarifying. Affects downstream ergonomics.

**Proposed fix:** Add to D1 or as a note: "`PlaneSlot` structurally includes all fields of `PlaneTransform` (from OBJ-003) plus additional metadata. It does NOT formally extend `PlaneTransform` via `extends` — this avoids coupling the type hierarchy. However, any function accepting `PlaneTransform` will also accept `PlaneSlot` due to TypeScript's structural typing." Or do formally extend it — either way, make the decision explicit.

---

#### Issue 7: `compatible_cameras` is `readonly string[]` on the interface but `string[]` in acceptance criteria narrative (MINOR)

AC-02 says `compatible_cameras: readonly string[]`, which matches the interface. Consistent. However, the `validateGeometryDefinition` spec (item 5) says "compatible_cameras is non-empty" — it should also verify each entry matches the camera name format. What format? The spec doesn't state camera path naming conventions. Are they also `/^[a-z][a-z0-9_]*$/`?

**Severity:** Minor. Without format validation, a geometry could declare `compatible_cameras: ['Tunnel Push Forward!!!']` and pass validation, only to fail at OBJ-041's cross-reference step.

**Proposed fix:** Add validation item: "All entries in `compatible_cameras` match `/^[a-z][a-z0-9_]*$/`." This mirrors the slot naming convention and the seed's camera preset names (all lowercase underscore: `tunnel_push_forward`, `slow_push_forward`, etc.).

---

#### Issue 8: Missing AC for `description` on `PlaneSlot` (MINOR)

The `PlaneSlot` has a `description` field. The `validateGeometryDefinition` checks the geometry-level `description` is non-empty (item 8), but doesn't check slot-level `description`. Should slot descriptions also be non-empty? They're used in SKILL.md docs and validation error messages — empty slot descriptions would produce poor error messages.

**Severity:** Minor.

**Proposed fix:** Add validation item 11: "All slot `description` fields are non-empty strings." Add corresponding error row to the table.

---

#### Issue 9: The `registerGeometry` function validates but doesn't specify what validation errors look like in the thrown Error (MINOR)

AC-04 says `registerGeometry` throws when validation fails. But how does it present potentially multiple validation errors? Does it throw with all errors concatenated? Just the first?

**Severity:** Minor.

**Proposed fix:** Specify: "The thrown Error's message includes all validation errors, formatted as: `'Cannot register geometry \'{name}\': {error1}; {error2}; ...'`." This matches the error table pattern already in the spec.

---

#### Issue 10: `getGeometryRegistry` return type semantics (MINOR)

The signature says `Readonly<GeometryRegistry>` which is `Readonly<Record<string, SceneGeometry>>`. TypeScript's `Readonly` only prevents reassignment of top-level keys — you can still mutate `registry.tunnel.slots.floor.description = 'hacked'`. This connects to Issue 3 (shallow vs deep freeze).

**Severity:** Covered by Issue 3's fix. Just noting the TypeScript-level implication.

---

### Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | Readonly/mutability contract for override scenarios | Major | Needs fix |
| 2 | FogConfig.color format rationale | Minor | Needs note |
| 3 | Registry freezing semantics (when, shallow vs deep, post-freeze registration) | Major | Needs fix |
| 4 | `position_override` reference to undefined manifest field | Major | Needs fix |
| 5 | `renderOrder` range validation | Minor | Needs note |
| 6 | Relationship to OBJ-003's `PlaneTransform` | Minor | Needs clarification |
| 7 | Camera name format validation in `compatible_cameras` | Minor | Needs fix |
| 8 | Slot-level `description` non-empty validation | Minor | Needs fix |
| 9 | Multi-error formatting in `registerGeometry` thrown Error | Minor | Needs spec |

Three major issues (1, 3, 4) need resolution before I can converge. The minor issues are real but individually wouldn't block convergence — I'd accept them as open questions if the author disagrees. But I'd prefer them fixed.

**Not raising as issues** (things I considered and approved):
- The addition of `renderOrder`, `transparent`, `fogImmune` to `PlaneSlot` — justified. These are spatial/compositional properties of the slot role, not per-image properties. Good call.
- The registry pattern itself — sound for this use case.
- Slot naming conventions — appropriate level of constraint.
- The barrel export structure — clean, follows OBJ-003 pattern.
- AC-10 (seed tunnel example works) — good integration test.

---

## Round 3 — spec_author

Thank you for the thorough review. All 9 issues are valid. Let me address each and present the revised specification.

---

## Issue Responses

**Issue 1 (Readonly/mutability — MAJOR):** Agreed. PlaneSlot values in a registered geometry are immutable templates. I'll add a new design decision (D9) making this explicit, stating that overrides produce new objects rather than mutating the template.

**Issue 2 (FogConfig.color rationale — MINOR):** Agreed. Adding rationale note to FogConfig.color.

**Issue 3 (Registry freezing semantics — MAJOR):** Agreed. I'll choose the "append-only, lock on first read" strategy with deep freeze, and add a design decision (D10) specifying this. Rationale: the engine has a clear initialization phase (register all geometries → validate manifest → render). A lock-on-first-read model enforces this naturally. Late registrations after the registry has been read indicate a bug in initialization order, not a valid use case.

**Issue 4 (position_override reference — MAJOR):** Agreed. Removing the reference entirely, replacing with the challenger's option (a): "These values are the geometry's defaults. Downstream consumers may apply per-scene overrides from the manifest, producing a resolved transform. The override mechanism is defined by the manifest schema (OBJ-004), not by this contract."

**Issue 5 (renderOrder range — MINOR):** Adding a note rather than validation. Three.js accepts any number; constraining it adds complexity without preventing real bugs.

**Issue 6 (PlaneTransform relationship — MINOR):** I'll make PlaneSlot formally `extends PlaneTransform`. This gives downstream consumers (OBJ-039, OBJ-040) the ability to accept the narrower type. It's a clean structural relationship, not coupling — PlaneTransform is just `{position, rotation, size}`.

**Issue 7 (Camera name format validation — MINOR):** Agreed. Adding validation that each entry in `compatible_cameras` matches `/^[a-z][a-z0-9_]*$/`.

**Issue 8 (Slot description non-empty — MINOR):** Agreed. Adding validation item.

**Issue 9 (Multi-error formatting — MINOR):** Agreed. Specifying concatenation format.

---

# Revised Specification: Scene Geometry Type Contract (OBJ-005)

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

**Rationale:** The engine has a deterministic initialization sequence: import geometry modules (which register themselves) → validate the manifest (which reads the registry) → render. Lock-on-first-read enforces this ordering naturally. Returning a fresh snapshot per call (the alternative) would require deep-cloning + deep-freezing on every access, which is wasteful for a registry that never changes after initialization. Deep freeze (not shallow) prevents mutation of nested objects like `slot.position`, which TypeScript's `Readonly` utility type does not protect at runtime.

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
| **OBJ-018–025** (Individual geometry implementations) | Each imports `SceneGeometry`, `PlaneSlot`, `FogConfig` types and `registerGeometry` to define and register a concrete geometry. |
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

---

I believe this revision addresses all 9 issues raised in Round 2. Here's a summary of changes:

| Issue | Resolution |
|---|---|
| 1 (Readonly/mutability) | Added D9 explicitly stating immutable template semantics. Updated PlaneSlot doc comments. |
| 2 (FogConfig.color rationale) | Added rationale note to `FogConfig.color` doc comment. |
| 3 (Registry freezing) | Added D10 specifying lock-on-first-read with deep freeze. Updated registry function signatures and docs. Added AC-05 and AC-14. Added registry lock tests. |
| 4 (position_override reference) | Removed all references to `position_override`. PlaneSlot comment now references downstream consumers generically. |
| 5 (renderOrder range) | Added note to `renderOrder` doc comment that it's not range-validated; geometry authors should use small values. |
| 6 (PlaneTransform relationship) | PlaneSlot now formally `extends PlaneTransform`. Added D11. Updated AC-01. Added structural subtyping test. |
| 7 (Camera name format) | Added validation rule 6: camera names must match `/^[a-z][a-z0-9_]*$/`. Updated AC-06. Added error table row. Added test case. |
| 8 (Slot description non-empty) | Added validation rule 11. Updated AC-06. Added error table row. Added test case. |
| 9 (Multi-error formatting) | Specified format in `registerGeometry` doc: `"Cannot register geometry '{name}': {error1}; {error2}; ..."`. Updated AC-04. |

Challenger — please verify and approve if satisfied.

---

## Round 4 — spec_challenger

## Challenger Review — Round 4

Let me verify each Round 2 fix is structurally present, then check for any new issues introduced by the revisions.

### Verification of Round 2 Fixes

**Issue 1 (Readonly/mutability) — ✅ FIXED.** D9 is present and explicit. PlaneSlot doc comment says "immutable templates" and explains that overrides create new objects. The `extends PlaneTransform` means the readonly tuple types flow through from OBJ-003. Good.

**Issue 2 (FogConfig.color rationale) — ✅ FIXED.** The `color` field doc comment now includes: "Constrained to #RRGGBB format for manifest serialization predictability and LLM authorability. The renderer converts to THREE.Color at the boundary." Good.

**Issue 3 (Registry freezing) — ✅ FIXED.** D10 specifies lock-on-first-read, deep freeze, cached snapshot, and the error for late registration. AC-05 tests the lock. AC-14 tests deep freeze. Registry test cases 8-10 cover the lock scenarios. The boundary behavior section includes the subtle case of `getGeometry('nonexistent')` locking the registry. Thorough.

**Issue 4 (position_override reference) — ✅ FIXED.** PlaneSlot doc comment now says "Downstream consumers (OBJ-036, OBJ-039) may apply per-scene overrides from the manifest by creating a new PlaneTransform with the override applied, rather than mutating the slot definition. The override mechanism is defined by the manifest schema (OBJ-004), not by this contract." No mention of `position_override` as a specific field. Good.

**Issue 5 (renderOrder range) — ✅ FIXED.** Note added to `renderOrder` doc comment. Adequate for a minor issue.

**Issue 6 (PlaneTransform relationship) — ✅ FIXED.** `PlaneSlot extends PlaneTransform` is explicit. D11 explains the rationale. AC-01 references the extension. Test case 4 in PlaneSlot tests checks structural subtyping. Good.

**Issue 7 (Camera name format) — ✅ FIXED.** Validation rule 6 added. AC-06 updated. Error table has the row. Test case added.

**Issue 8 (Slot description non-empty) — ✅ FIXED.** Validation rule 11 added. AC-06 updated. Error table has the row. Test case added.

**Issue 9 (Multi-error formatting) — ✅ FIXED.** `registerGeometry` doc specifies the format. AC-04 includes the pattern. Good.

### New Issues Check

Let me look for anything introduced by the revisions or that I missed in Round 2.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]
Let me verify the `PlaneTransform` type in OBJ-003 to confirm the `extends` relationship is correct.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": 30,
  "limit": 50
}
[Tool Result]     30→  lookAt: [0, 0, 0] as Vec3,
    31→} as const;
    32→
    33→/** Supported composition presets (seed C-04) */
    34→export const COMPOSITION_PRESETS = {
    35→  LANDSCAPE_1080P: { width: 1920, height: 1080, aspectRatio: 16 / 9 },
    36→  PORTRAIT_1080P:  { width: 1080, height: 1920, aspectRatio: 9 / 16 },
    37→} as const;
    38→
    39→/** Standard frame rates (seed C-04) */
    40→export const FRAME_RATES = [24, 30] as const;
    41→
    42→/**
    43→ * Standard plane rotations for common orientations (seed Section 8.4).
    44→ * All values in radians.
    45→ */
    46→export const PLANE_ROTATIONS = {
    47→  /** Faces camera (normal along +Z). Default orientation. */
    48→  FACING_CAMERA: [0, 0, 0] as Vec3,
    49→  /** Lies flat, faces up. For floor planes. */
    50→  FLOOR: [-Math.PI / 2, 0, 0] as Vec3,
    51→  /** Lies flat, faces down. For ceiling planes. */
    52→  CEILING: [Math.PI / 2, 0, 0] as Vec3,
    53→  /** Faces right. For left-side wall planes. ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": 80,
  "limit": 30
}
[Tool Result]     80→  /** Distance from camera used for this calculation */
    81→  distance: number;
    82→  /** FOV used for this calculation (degrees) */
    83→  fov: number;
    84→  /** Aspect ratio used for this calculation */
    85→  aspectRatio: number;
    86→}
    87→
    88→/** Describes a plane's complete spatial state */
    89→export interface PlaneTransform {
    90→  position: Vec3;
    91→  rotation: EulerRotation;
    92→  size: Size2D;
    93→}
    94→
    95→/** Input for plane sizing calculations. */
    96→export interface PlaneSizingInput {
    97→  /** Distance from camera to plane along the view axis (positive number) */
    98→  distanceFromCamera: number;
    99→  /** Camera vertical FOV in degrees */
   100→  fov: number;
   101→  /** Composition aspect ratio (width / height) */
   102→  aspectRatio: number;
   103→  /**
   104→   * Scalar multiplier to oversize the plane beyond the visible area.
   105→   * 1.0 = exact fit, 1.2 = 20% larger in both dimensions.
   10... [truncated]
Good. `PlaneTransform` in OBJ-003 is `{ position: Vec3; rotation: EulerRotation; size: Size2D; }` — exactly what `PlaneSlot extends PlaneTransform` needs. Confirmed.

Now let me check OBJ-003's barrel export to make sure `PlaneTransform` is actually exported:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": 155,
  "limit": 20
}
[Tool Result]    155→ */
   156→export function computeFrustumRect(
   157→  distance: number,
   158→  fov: number,
   159→  aspectRatio: number
   160→): FrustumRect;
   161→
   162→/**
   163→ * Computes the recommended plane size to fill (or overfill) the camera's
   164→ * visible area at a given distance.
   165→ *
   166→ * @param input - PlaneSizingInput with distance, FOV, aspect ratio, and optional oversize factor.
   167→ * @returns PlaneSizingResult with the recommended [width, height] and frustum data.
   168→ * @throws RangeError if oversizeFactor < 1.0 or other params out of range.
   169→ */
   170→export function computePlaneSize(input: PlaneSizingInput): PlaneSizingResult;
   171→
   172→/**
   173→ * Computes the signed distance from a camera position to a plane position
   174→ * projected along the camera's forward direction (from camera toward lookAt).

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": 240,
  "limit": 30
}
[Tool Result]    240→
   241→/** Subtracts vector b from vector a: a - b. */
   242→export function subtract(a: Vec3, b: Vec3): Vec3;
   243→
   244→/** Scales a Vec3 by a scalar. */
   245→export function scale(v: Vec3, s: number): Vec3;
   246→
   247→/** Adds two Vec3s. */
   248→export function add(a: Vec3, b: Vec3): Vec3;
   249→```
   250→
   251→### Module Exports
   252→
   253→```typescript
   254→// src/spatial/index.ts
   255→// Barrel export -- the single import point for all downstream consumers
   256→
   257→export * from './types';
   258→export * from './constants';
   259→export * from './math';
   260→```
   261→
   262→## Design Decisions
   263→
   264→### D1: Pure math module with no Three.js dependency
   265→
   266→This module runs in Node.js (orchestrator side) and could also be bundled for the browser page side. It must NOT import `three` or any rendering library. The types use plain tuples (`[number, number, number]`) rather than `THREE.Vector3`. Downstream consumers conv... [truncated]
Good — `export * from './types'` means `PlaneTransform` is exported from the barrel. The `extends` relationship is valid.

---

### Final Review — Round 4

All 9 Round 2 issues are verified as structurally fixed. Let me do one final scan for anything I may have missed or any new issues introduced by the revisions.

**Checking for new issues:**

1. **The import statement in types.ts** — `import type { Vec3, EulerRotation, Size2D, PlaneTransform } from '../../spatial';` — this path assumes `src/scenes/geometries/types.ts` importing from `src/spatial/index.ts`. That's correct per the file placement of both modules. ✅

2. **`getGeometry` locks the registry** — the spec says "Implicitly locks the registry on first call (same as getGeometryRegistry)." This is clear but means an implementer of the test suite needs to be careful — each test that tests registration-after-lock needs a fresh registry. The spec doesn't mention a `resetRegistry()` for testing. This is a **minor** gap — test infrastructure, not contract. I'll note it as an open question rather than blocking.

3. **`validateGeometryDefinition` is called by `registerGeometry` but also exported independently** — could someone call `validateGeometryDefinition` on an object that doesn't match the `SceneGeometry` interface at runtime (e.g., missing fields entirely)? The function signature says it takes `SceneGeometry`, so TypeScript would catch this at compile time. At runtime (JavaScript), it would need to handle `undefined` fields gracefully. The validation rules cover the cases (empty name, empty slots, etc.) but don't explicitly handle `null`/`undefined` for top-level fields. This is **minor** — TypeScript enforcement is the primary guard, and runtime JavaScript callers who bypass types are outside the contract.

4. **Slot utility functions accept `SceneGeometry` not the registry** — meaning they work on pre-registration geometry objects too. That's fine and useful for testing.

5. **No AC for `getGeometryNames` returning correct data** — AC-07/08/09/10 test other read functions but there's no AC that `getGeometryNames()` after registering `['stage', 'tunnel', 'canyon']` returns exactly those three names. This is covered in the test strategy (registry test 4) but not as a formal AC. **Trivially minor** — the test strategy is sufficient.

None of these rise to major severity. The spec is solid, implementable, and well-integrated with both its dependency (OBJ-003) and its many downstream consumers.

---

CONCLUSION:

The specification for OBJ-005 (Scene Geometry Type Contract) is approved. All 9 issues from Round 2 have been verified as structurally resolved in the Round 3 revision. The spec defines:

1. **Core types**: `PlaneSlot` (extending OBJ-003's `PlaneTransform`), `SceneGeometry`, `FogConfig`, `GeometryRegistry`, `GeometryValidationError`
2. **Registry**: append-only with lock-on-first-read semantics and deep freeze (D10)
3. **Validation**: 11-rule structural validator for geometry definitions, separate from manifest validation
4. **Slot utilities**: required/optional/all slot name queries, camera compatibility check
5. **Naming conventions**: regex-enforced `/^[a-z][a-z0-9_]*$/` with reserved semantic names
6. **11 design decisions** covering immutability (D9), registry lifecycle (D10), PlaneTransform extension (D11), and other key choices
7. **16 acceptance criteria**, all specific and testable
8. **Comprehensive edge cases** and error message patterns

Minor open item for implementers: test suites will need a mechanism to reset the registry between tests (not part of the public API contract — an internal testing concern). This is noted but does not block convergence.

Let me write the final spec to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "content": "# Specification: Scene Geometry Type Contract (OBJ-005)\n\n## Summary\n\nOBJ-005 defines the TypeScript type system for all scene geometries in depthkit: the `PlaneSlot` interface describing a single named position in a 3D scene, the `SceneGeometry` interface describing a complete spatial arrangement of planes, the `FogConfig` interface for depth-based atmospheric fading, a geometry registry with explicit registration and deep-freeze semantics, and the slot naming conventions that all 8 geometry implementations (OBJ-018 through OBJ-025) must follow. This is a pure type/contract module \u2014 it defines the shape of geometry data, not any specific geometry's values. It imports spatial primitives from OBJ-003 and is consumed by every downstream objective that creates, validates, instantiates, or queries scene geometries.\n\n## Interface Contract\n\n### Core Types\n\n```typescript\n// src/scenes/geometries/types.ts\n\nimport type { Vec3, EulerRotation, Size2D, PlaneTransform } from '../../spatial';\n\n/**\n * Configuration for Three.js fog, providing depth-based atmospheric fading.\n * Enhances the 2.5D effect by hiding hard edges on distant planes\n * and creating atmospheric perspective (seed Section 8.10).\n */\nexport interface FogConfig {\n  /**\n   * CSS-style 6-digit hex color string for the fog (e.g., '#000000').\n   * Constrained to #RRGGBB format for manifest serialization predictability\n   * and LLM authorability. The renderer converts to THREE.Color at the boundary.\n   */\n  color: string;\n  /** Distance from camera (in world units) where fog begins. Must be >= 0. */\n  near: number;\n  /** Distance from camera (in world units) where fog is fully opaque. Must be > near. */\n  far: number;\n}\n\n/**\n * A single named position in a scene geometry's spatial layout.\n * Defines where a plane (textured mesh) is placed in 3D space.\n 
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-005",
     3→  "description": "Scene geometry type contract -- TypeScript interfaces for SceneGeometry and PlaneSlot per Section 8.6. PlaneSlot defines position [x,y,z], rotation [rx,ry,rz], size [w,h], required flag, and description. SceneGeometry defines name, slots record, compatible_cameras list, default_camera, and optional fog config. Establishes slot naming conventions and required-vs-optional plane semantics.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Defines the type system for all 8 scene geometry implementations."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json",
  "content": "{\n  \"id\": \"OBJ-005\",\n  \"description\": \"Scene geometry type contract -- TypeScript interfaces for SceneGeometry and PlaneSlot per Section 8.6. PlaneSlot extends PlaneTransform from OBJ-003, adding required flag, description, renderOrder, transparent, and fogImmune fields. SceneGeometry defines name, slots record, compatible_cameras list, default_camera, optional fog config, description, and advisory preferred_aspect. Includes geometry registry with lock-on-first-read deep-freeze semantics, structural validation (11 rules), slot naming conventions (/^[a-z][a-z0-9_]*$/), and slot utility functions.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"spec-deliberation\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T01:30:00Z\",\n  \"depends_on\": [\"OBJ-003\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 1 contract. Defines the type system for all 8 scene geometry implementations. Key decisions: PlaneSlot extends PlaneTransform (D11), immutable templates with deep freeze (D9/D10), registry locks on first read (D10), string-based camera references to avoid circular deps with OBJ-006 (D7), regex-based slot naming not enum (D8). 4-round deliberation converged with 9 issues identified and resolved.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json has been updated successfully.
Now commit:
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
[Tool Result] 04524be spec(OBJ-006): camera path type contract — presets, registry, and validation
bcaf2c5 spec(OBJ-010): Three.js page shell, build/bundle architecture, and scene renderer skeleton
dcf4d08 spec(OBJ-007): depth model — semantic slot taxonomy and override system
dc13dd4 spec(OBJ-004): Manifest schema core — Zod validation and registry contract
90a2c38 spec(OBJ-002): interpolation, easing, and spring utilities
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-005/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/transcript.md
	nodes/OBJ-002/transcript.md
	nodes/OBJ-003/transcript.md
	nodes/OBJ-004/transcript.md
	nodes/OBJ-005/output.md
	nodes/OBJ-006/transcript.md
	nodes/OBJ-007/transcript.md
	nodes/OBJ-010/transcript.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-005/output.md nodes/OBJ-005/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-005): scene geometry type contract \u2014 PlaneSlot, SceneGeometry, registry\n\nDefines the TypeScript type system for all scene geometries: PlaneSlot\n(extending PlaneTransform from OBJ-003), SceneGeometry, FogConfig, and\na geometry registry with lock-on-first-read deep-freeze semantics.\nIncludes 11-rule structural validator, slot naming conventions, and\nutility functions. 4-round deliberation resolved 9 issues covering\nimmutability semantics, registry lifecycle, PlaneTransform extension,\nand camera name format validation.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-005 spec output and meta"
}
[Tool Result] [master 065cb85] spec(OBJ-005): scene geometry type contract — PlaneSlot, SceneGeometry, registry
 2 files changed, 686 insertions(+), 4 deletions(-)
 create mode 100644 nodes/OBJ-005/output.md
Committed. The OBJ-005 specification is finalized and written to disk. 

**Summary of the converged spec:**

- **PlaneSlot** extends `PlaneTransform` from OBJ-003, adding `required`, `description`, and optional rendering hints (`renderOrder`, `transparent`, `fogImmune`)
- **SceneGeometry** defines `name`, `slots`, `compatible_cameras`, `default_camera`, optional `fog`/`preferred_aspect`, and `description`
- **Registry** uses lock-on-first-read with recursive deep freeze — registration phase then locked phase, enforced at runtime
- **Validation** has 11 structural rules with specific error paths and message patterns
- **Slot naming** enforced via `/^[a-z][a-z0-9_]*$/` with a reserved-name semantic table
- **16 acceptance criteria**, all specific and testable
- **11 design decisions** documenting key architectural choices and their rationale
- **4 open questions** properly deferred (size_mode, wildcards, resolved-defaults type, test registry reset)
