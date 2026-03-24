# Deliberation Transcript: OBJ-006

---

## Round 1 — spec_author

Let me start by reviewing the existing codebase to understand what's already implemented for the dependencies.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the existing codebase to understand what's already built.
[Tool: Glob]
  Input: {
  "pattern": "**/src/spatial/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/interpolation/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-006/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-005/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-003/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-002/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-006",
     3→  "description": "Camera path type contract -- TypeScript interface for camera path presets. Defines position(t) and lookAt(t) as functions of normalized time t in [0,1], start/end position and lookAt vectors, FOV animation range (fov_start, fov_end), easing defaults, compatible_geometries list, and oversizing requirements metadata. Per Section 4.3.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-002", "OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Depends on interpolation utilities (OBJ-002) for easing references and coordinate system (OBJ-003) for spatial conventions."
    12→}
    13→

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
Let me check if OBJ-005 has an output yet and look at some key downstream consumers:
[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-005/output.md"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-026/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-040/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-040/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-041/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-041/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-026",
     3→  "description": "Static camera path preset -- fixed position and orientation, no movement. Defines start/end position (identical), lookAt target, FOV (no animation), compatible geometries (all), and oversizing requirements (minimal -- no camera motion means no edge reveal risk).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Simplest preset -- baseline for all geometries."
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
Let me also check some of the other downstream camera preset meta files to understand the range:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-027",
     3→  "description": "Push/pull camera path presets -- slow_push_forward (camera moves from z=5 toward negative Z, creating the 'moving into the scene' effect) and slow_pull_back (reverse). These are mathematical mirrors with swapped start/end positions; one spec covers both. The defining 2.5D motion per Section 4.3. Defines position(t), lookAt(t), easing defaults, compatible geometries, and oversizing requirements.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. The most important camera motion for 2.5D projection."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-029",
     3→  "description": "Tunnel push forward camera path preset -- deep Z-axis push specifically tuned for tunnel geometry. Appropriate near/far planes, speed calibrated so walls undergo convincing perspective distortion without flying through the end wall. Defines position(t), lookAt(t), easing defaults, compatible geometries (tunnel), and oversizing requirements.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Geometry-specific preset for the tunnel."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-030",
     3→  "description": "Flyover glide camera path preset -- camera moves forward on Z while positioned above the ground plane (elevated Y), looking slightly downward. Bird's-eye aerial movement feel. Defines position(t), lookAt(t), easing defaults, compatible geometries (flyover), and oversizing requirements.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Geometry-specific preset for flyover."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-031",
     3→  "description": "Gentle float camera path preset -- very slow, subtle movement in all three axes. Almost subliminal. Good for ambient scenes. Defines position(t), lookAt(t) with small-amplitude multi-axis drift, easing defaults, compatible geometries (most geometries), and oversizing requirements (minimal due to small motion range).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Universal ambient preset -- compatible with most geometries."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-034/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-034",
     3→  "description": "Dolly zoom camera path preset -- simultaneous Z push forward + FOV widen (or Z pull back + FOV narrow). The Hitchcock/Spielberg vertigo effect. Dramatic but use sparingly. Defines position(t), lookAt(t), fov_start/fov_end animation, easing defaults, compatible geometries, and oversizing requirements. Addresses TC-14 (FOV animation produces useful effects).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Medium priority. Currently a leaf node. May be deferred to post-V1."
    12→}
    13→
Now I have enough context to propose the spec. Let me also quickly check what other camera preset OBJs exist:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-028",
     3→  "description": "Lateral track camera path presets -- lateral_track_left (camera translates along negative X-axis, looking slightly ahead) and lateral_track_right (mirror). Cinematic tracking shots. Defines position(t), lookAt(t), easing defaults, compatible geometries, and oversizing requirements (significant X-axis oversizing needed).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Currently a leaf node -- no tuning objective directly references lateral tracks."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-032/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-032",
     3→  "description": "Dramatic push camera path preset -- faster forward push with ease-out for emphasis moments. More aggressive than slow_push_forward. Defines position(t), lookAt(t), easing defaults (strong ease-out), compatible geometries, and oversizing requirements.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Medium priority. Currently a leaf node."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-033/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-033",
     3→  "description": "Crane up camera path preset -- camera rises on Y-axis while keeping the lookAt target steady. Reveals vertical space. Defines position(t) with Y-axis rise, lookAt(t) targeting scene center, easing defaults, compatible geometries (canyon, stage), and oversizing requirements (vertical oversizing needed).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Medium priority. Currently a leaf node."
    12→}
    13→
Good. Now I have a complete picture. Here's my proposal for the OBJ-006 specification:

---

# Specification: OBJ-006 — Camera Path Type Contract

## Summary

OBJ-006 defines the TypeScript type system for camera path presets in depthkit. A camera path preset is a named, self-contained unit that maps normalized time `t ∈ [0, 1]` to a complete camera state (`position`, `lookAt`, `fov`) and carries metadata for validation, edge-reveal prevention, and blind authoring. This is the Tier 1 contract that all downstream camera path preset implementations (OBJ-026 through OBJ-034) conform to, and that the scene sequencer (OBJ-010), edge-reveal validator (OBJ-040), and geometry-camera compatibility validator (OBJ-041) consume.

## Interface Contract

### Core Types

```typescript
// src/camera/types.ts

import { Vec3, EulerRotation, Size2D } from '../spatial/types';
import { EasingName } from '../interpolation/easings';

/**
 * The complete camera state at a single moment in time.
 * Returned by a camera path's evaluate() function.
 */
export interface CameraFrameState {
  /** Camera position in world space [x, y, z] */
  position: Vec3;
  /** Camera lookAt target in world space [x, y, z] */
  lookAt: Vec3;
  /** Vertical field of view in degrees. Must be in (0, 180). */
  fov: number;
}

/**
 * Parameters the manifest author can pass to customize a camera path
 * at the scene level. These override the preset's defaults.
 *
 * Each preset defines which params it accepts. Unrecognized params
 * are ignored (not rejected) — this allows presets to evolve without
 * breaking existing manifests.
 */
export interface CameraParams {
  /**
   * Speed multiplier. 1.0 = preset's default motion range.
   * 0.5 = half the motion, 2.0 = double. Applied as a scalar
   * to the preset's total displacement.
   * Must be > 0. Default: 1.0.
   */
  speed?: number;

  /**
   * Easing override for the primary motion.
   * Replaces the preset's default easing.
   */
  easing?: EasingName;

  /**
   * Additive offset to the camera's start position, in world units.
   * Applied after the preset computes its base start position.
   * Allows subtle per-scene repositioning without defining a new preset.
   * Default: [0, 0, 0].
   */
  offset?: Vec3;
}

/**
 * Oversizing metadata that a camera path preset provides so that
 * OBJ-040 (edge-reveal validation) and geometry definitions can
 * compute the minimum plane sizes needed to prevent edge reveals.
 *
 * All values describe the MAXIMUM extent of camera motion in each
 * axis, in world units, at the preset's default speed (speed=1.0).
 * For speed != 1.0, multiply by the speed factor.
 */
export interface OversizeRequirements {
  /**
   * Maximum camera displacement along the X axis (world units).
   * Used to determine horizontal plane oversizing.
   */
  maxDisplacementX: number;

  /**
   * Maximum camera displacement along the Y axis (world units).
   * Used to determine vertical plane oversizing.
   */
  maxDisplacementY: number;

  /**
   * Maximum camera displacement along the Z axis (world units).
   * Used to determine depth-related visible area changes
   * (as camera moves forward, nearby planes need to be wider).
   */
  maxDisplacementZ: number;

  /**
   * The FOV range across the path's duration: [min, max] in degrees.
   * A wider max FOV means more visible area at that moment.
   * For paths with no FOV animation, min === max.
   */
  fovRange: readonly [number, number];

  /**
   * Recommended uniform oversize factor for "simple" plane sizing.
   * This is a convenience value — a single scalar >= 1.0 that is
   * sufficient to prevent edge reveals for ALL planes in all
   * compatible geometries, assuming planes are sized to the
   * frustum at their distance from the camera's start position.
   *
   * OBJ-040 may compute more precise per-plane factors using the
   * displacement values above. This scalar is a safe upper bound.
   */
  recommendedOversizeFactor: number;
}

/**
 * A camera path evaluation function.
 * Given normalized time t in [0, 1], returns the complete camera state.
 *
 * Contract:
 * - t = 0 returns the camera's start state.
 * - t = 1 returns the camera's end state.
 * - Values are continuous between 0 and 1 (no discontinuities).
 * - Behavior for t outside [0, 1] is undefined. Callers must clamp.
 *
 * The function receives CameraParams to allow manifest-level customization.
 * Implementations are responsible for applying speed, easing, and offset.
 */
export type CameraPathEvaluator = (
  t: number,
  params?: CameraParams
) => CameraFrameState;

/**
 * The complete definition of a camera path preset.
 * This is the type that all OBJ-026 through OBJ-034 implementations export.
 */
export interface CameraPathPreset {
  /** Unique preset name. Must match the key in the registry. Lowercase snake_case. */
  name: string;

  /**
   * Human-readable description for SKILL.md and error messages.
   * Should describe the visual effect in 1-2 sentences.
   */
  description: string;

  /**
   * The evaluation function. Given t in [0, 1] and optional params,
   * returns the camera state at that moment.
   */
  evaluate: CameraPathEvaluator;

  /**
   * The camera state at t=0 with default params.
   * Redundant with evaluate(0), but provided as static data for
   * fast access during validation without calling evaluate().
   */
  defaultStartState: CameraFrameState;

  /**
   * The camera state at t=1 with default params.
   * Redundant with evaluate(1), but provided as static data for
   * fast access during validation without calling evaluate().
   */
  defaultEndState: CameraFrameState;

  /**
   * Default easing applied to the primary motion.
   * Can be overridden by CameraParams.easing in the manifest.
   */
  defaultEasing: EasingName;

  /**
   * Names of scene geometries this path is designed to work with.
   * The geometry-camera compatibility validator (OBJ-041) uses this
   * to reject invalid combinations in the manifest.
   *
   * A path with ['stage', 'diorama'] should NOT be used with 'tunnel'.
   * A path with ['*'] (or an empty array — see design decision D5)
   * is compatible with all geometries.
   */
  compatibleGeometries: readonly string[];

  /**
   * Oversizing metadata for edge-reveal prevention.
   * Describes the spatial envelope of the camera's motion so that
   * planes can be sized to prevent edge reveals.
   */
  oversizeRequirements: OversizeRequirements;

  /**
   * Tags for categorizing and searching presets in the SKILL.md
   * and for LLM-assisted preset selection. Lowercase.
   * Examples: ['push', 'forward', 'dramatic'], ['ambient', 'subtle', 'float'].
   */
  tags: readonly string[];
}
```

### Registry

```typescript
// src/camera/registry.ts

import { CameraPathPreset } from './types';

/**
 * Type-safe registry of all camera path presets.
 * Downstream objectives (OBJ-026 through OBJ-034) register their
 * presets here. The registry is frozen at build time — no runtime mutation.
 *
 * Keys are preset names (lowercase snake_case). Values are CameraPathPreset objects.
 */
export type CameraPathRegistry = Readonly<Record<string, CameraPathPreset>>;

/**
 * The canonical registry instance. Populated by preset implementations.
 * Initially empty — each preset module registers itself at import time.
 *
 * NOTE: The registry is built by the downstream module that assembles
 * all presets (e.g., src/camera/index.ts). This module defines the
 * lookup functions that operate on any CameraPathRegistry.
 */

/**
 * Retrieves a camera path preset by name.
 * @param registry - The camera path registry to search.
 * @param name - The preset name.
 * @returns The CameraPathPreset.
 * @throws {Error} if name is not found. Error message includes the
 *   invalid name and lists all available preset names.
 */
export function getCameraPath(
  registry: CameraPathRegistry,
  name: string
): CameraPathPreset;

/**
 * Type guard: checks if a name exists in the given registry.
 */
export function isCameraPathName(
  registry: CameraPathRegistry,
  name: string
): boolean;

/**
 * Returns all preset names in the registry, sorted alphabetically.
 * Used for error messages and SKILL.md generation.
 */
export function listCameraPathNames(
  registry: CameraPathRegistry
): readonly string[];

/**
 * Returns all presets compatible with a given geometry name.
 * @param registry - The camera path registry.
 * @param geometryName - The geometry to filter by.
 * @returns Array of compatible CameraPathPreset objects.
 */
export function getCameraPathsForGeometry(
  registry: CameraPathRegistry,
  geometryName: string
): readonly CameraPathPreset[];
```

### Module Exports

```typescript
// src/camera/index.ts

export type {
  CameraFrameState,
  CameraParams,
  OversizeRequirements,
  CameraPathEvaluator,
  CameraPathPreset,
} from './types';

export type { CameraPathRegistry } from './registry';

export {
  getCameraPath,
  isCameraPathName,
  listCameraPathNames,
  getCameraPathsForGeometry,
} from './registry';
```

### Validation Utility

```typescript
// src/camera/validate.ts

import { CameraPathPreset, CameraParams } from './types';

/**
 * Validates that a CameraPathPreset satisfies its own internal contract.
 * Used during development/testing — NOT runtime manifest validation.
 *
 * Checks:
 * 1. evaluate(0) matches defaultStartState (within tolerance).
 * 2. evaluate(1) matches defaultEndState (within tolerance).
 * 3. FOV is within (0, 180) at t=0, t=0.5, t=1.
 * 4. evaluate() returns finite values (no NaN/Infinity) at 100 sample points.
 * 5. oversizeRequirements.recommendedOversizeFactor >= 1.0.
 * 6. oversizeRequirements.fovRange[0] <= fovRange[1], both in (0, 180).
 * 7. oversizeRequirements displacement values are >= 0.
 * 8. name is non-empty, lowercase snake_case.
 * 9. compatibleGeometries is non-empty.
 * 10. defaultEasing is a valid EasingName.
 *
 * @param preset - The preset to validate.
 * @returns Array of validation error strings. Empty array = valid.
 */
export function validateCameraPathPreset(
  preset: CameraPathPreset
): readonly string[];

/**
 * Validates CameraParams from a manifest scene.
 * Checks:
 * 1. speed > 0 (if provided).
 * 2. easing is a valid EasingName (if provided).
 * 3. offset contains finite values (if provided).
 *
 * @param params - The params to validate.
 * @returns Array of validation error strings. Empty array = valid.
 */
export function validateCameraParams(
  params: CameraParams
): readonly string[];
```

## Design Decisions

### D1: Evaluation function over keyframe data

**Decision:** Camera path presets define an `evaluate(t, params) => CameraFrameState` function rather than exposing raw keyframe data (start/end positions) that the caller interpolates.

**Rationale:** The downstream presets vary dramatically in complexity. `static` (OBJ-026) is trivial — it returns the same state for all `t`. `slow_push_forward` (OBJ-027) is simple linear interpolation between two Z positions. But `gentle_float` (OBJ-031) involves multi-axis sinusoidal drift, and `dolly_zoom` (OBJ-034) requires coordinated Z-position and FOV animation. A keyframe-based interface would either be too simple for complex presets or too complex for simple ones. The evaluation function pattern lets each preset own its interpolation logic (using OBJ-002 utilities internally) while presenting a uniform interface to the scene renderer.

**Trade-off:** Callsite code cannot introspect the path's trajectory without sampling. Mitigated by `defaultStartState`, `defaultEndState`, and `oversizeRequirements` as static metadata for validation without sampling.

### D2: CameraParams as a manifest-level customization layer

**Decision:** The manifest's `camera_params` field maps to a `CameraParams` object that is passed into the `evaluate()` function. The preset is responsible for applying these overrides internally.

**Rationale:** The seed's manifest schema (Section 4.6) shows `camera_params: { speed: 1.0, easing: "ease_in_out" }` as per-scene overrides. This means the preset must be parameterizable without the manifest author defining new presets. The three params (`speed`, `easing`, `offset`) cover the most common adjustments an LLM author would need:
- `speed` scales motion intensity (C-06 blind authoring — "use slow_push_forward but slower")
- `easing` changes the feel without changing the trajectory
- `offset` allows minor repositioning ("shift camera slightly right for this scene")

Unrecognized params are ignored (not rejected) so that presets can add custom params in the future without breaking existing manifests.

### D3: OversizeRequirements as structured metadata, not a single scalar

**Decision:** Presets expose per-axis displacement maximums and FOV range, plus a convenience `recommendedOversizeFactor` scalar.

**Rationale:** OBJ-040 (edge-reveal validation) needs to compute whether each plane is large enough for the camera's full motion range. A single scalar would force worst-case oversizing in all directions. Per-axis displacements enable OBJ-040 to compute precise per-plane oversize factors — a lateral track only needs horizontal oversizing, not vertical. The `recommendedOversizeFactor` convenience scalar serves simpler consumers (e.g., geometry definitions that want a quick safe margin without running the full OBJ-040 algorithm). This scalar must be a safe upper bound — sufficient for the worst-case plane in any compatible geometry.

**Integration with CameraParams.speed:** When `speed != 1.0`, the effective displacements are `maxDisplacementX * speed`, etc. OBJ-040 must account for this.

### D4: Static defaultStartState and defaultEndState alongside evaluate()

**Decision:** Presets provide pre-computed start and end states as static data, redundant with `evaluate(0)` and `evaluate(1)`.

**Rationale:** Validation (OBJ-041, manifest schema) needs to check compatibility quickly — e.g., "does this camera start position make sense for this geometry?" Calling `evaluate(0)` is cheap, but having the data statically available means validators don't need to reason about whether `evaluate()` has side effects. It also serves as a self-documentation mechanism — a developer can read the start/end states without mentally executing the evaluate function. The validation utility (`validateCameraPathPreset`) checks that these are consistent with `evaluate()`.

### D5: compatibleGeometries as a string array, not an enum

**Decision:** `compatibleGeometries` is `readonly string[]` rather than a typed union of geometry names. An empty array means "compatible with no geometries" (invalid — caught by validation).

**Rationale:** OBJ-005 (scene geometry type contract) is in-progress and hasn't established its final geometry name set. Coupling this type to a geometry name enum would create a circular dependency or require both specs to finalize simultaneously. String-based names with runtime validation (OBJ-041) is the standard pattern used elsewhere in depthkit (easing names, preset names). The geometry-camera compatibility validator (OBJ-041) cross-references these at validation time.

**Universal compatibility:** Presets compatible with all geometries (like `static` and `gentle_float`) should list all known geometry names explicitly rather than using a wildcard convention. This keeps the compatibility contract auditable — when a new geometry is added, each preset must explicitly declare compatibility with it (or not). Implicit universal compatibility via `['*']` risks silent false-positive compatibility with untested geometries.

### D6: Registry takes the registry as a parameter (not a module-level singleton)

**Decision:** `getCameraPath(registry, name)` accepts the registry as an argument rather than reading from a module-level singleton.

**Rationale:** Testability. Unit tests for downstream consumers can pass a mock registry with only the presets under test. The canonical registry is assembled once by `src/camera/index.ts` and passed through the system. This avoids import-order dependency issues and makes the module tree deterministic (C-05).

### D7: CameraFrameState uses Vec3 from OBJ-003, not Three.js types

**Decision:** All spatial types reference `Vec3` from `src/spatial/types.ts`, consistent with OBJ-003's D1 (pure math module with no Three.js dependency).

**Rationale:** Camera path types are consumed in both Node.js (validation, scene sequencing) and potentially the browser (Three.js rendering). Using plain tuples ensures JSON-serializability for Puppeteer message passing and keeps the type contract renderer-agnostic. The browser-side renderer converts `Vec3` tuples to `THREE.Vector3` at the boundary.

### D8: FOV is always returned from evaluate(), even when static

**Decision:** `CameraFrameState` always includes `fov`, even for paths that don't animate FOV.

**Rationale:** The renderer needs the FOV at every frame to set the camera. If FOV were optional, the renderer would need to maintain fallback logic ("use the global default if the path doesn't provide FOV"). Making FOV always present eliminates that conditional. For paths with static FOV, `evaluate()` simply returns the same value for all `t`. The OversizeRequirements `fovRange` with `min === max` signals that FOV is not animated.

## Acceptance Criteria

### Type Contract ACs

- [ ] **AC-01:** `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `OversizeRequirements`, `CameraPathEvaluator` are all exported from `src/camera/index.ts` as types.
- [ ] **AC-02:** `CameraFrameState.position` and `CameraFrameState.lookAt` use the `Vec3` type from `src/spatial/types.ts`.
- [ ] **AC-03:** `CameraFrameState.fov` is `number` (degrees), not optional.
- [ ] **AC-04:** `CameraPathPreset.evaluate` accepts `(t: number, params?: CameraParams)` and returns `CameraFrameState`.
- [ ] **AC-05:** `CameraPathPreset.compatibleGeometries` is `readonly string[]`.
- [ ] **AC-06:** `CameraPathPreset.oversizeRequirements` includes `maxDisplacementX`, `maxDisplacementY`, `maxDisplacementZ`, `fovRange`, and `recommendedOversizeFactor`.
- [ ] **AC-07:** `CameraParams.speed`, `CameraParams.easing`, and `CameraParams.offset` are all optional.
- [ ] **AC-08:** `OversizeRequirements.fovRange` is `readonly [number, number]`.

### Registry ACs

- [ ] **AC-09:** `getCameraPath(registry, 'nonexistent')` throws an `Error` whose message includes `'nonexistent'` and lists all available preset names in the registry.
- [ ] **AC-10:** `isCameraPathName(registry, name)` returns `true` for registered names, `false` for unregistered.
- [ ] **AC-11:** `listCameraPathNames(registry)` returns names in alphabetical order.
- [ ] **AC-12:** `getCameraPathsForGeometry(registry, 'tunnel')` returns only presets whose `compatibleGeometries` includes `'tunnel'`.
- [ ] **AC-13:** `getCameraPathsForGeometry(registry, 'nonexistent_geometry')` returns an empty array (no throw).

### Validation ACs

- [ ] **AC-14:** `validateCameraPathPreset` detects a preset where `evaluate(0)` disagrees with `defaultStartState` (position differs by > 1e-6 in any axis).
- [ ] **AC-15:** `validateCameraPathPreset` detects a preset where FOV at any of 100 evenly-spaced sample points is <= 0 or >= 180.
- [ ] **AC-16:** `validateCameraPathPreset` detects a preset where `evaluate()` returns NaN or Infinity for position, lookAt, or fov at any of 100 sample points.
- [ ] **AC-17:** `validateCameraPathPreset` detects `recommendedOversizeFactor < 1.0`.
- [ ] **AC-18:** `validateCameraPathPreset` detects an empty `compatibleGeometries` array.
- [ ] **AC-19:** `validateCameraPathPreset` detects a `name` that is empty or not lowercase snake_case (regex: `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`).
- [ ] **AC-20:** `validateCameraPathPreset` detects a `defaultEasing` that is not a valid `EasingName`.
- [ ] **AC-21:** `validateCameraPathPreset` returns an empty array for a well-formed preset.
- [ ] **AC-22:** `validateCameraParams` detects `speed <= 0`, invalid `easing` names, and non-finite `offset` values.
- [ ] **AC-23:** `validateCameraParams` returns an empty array for `{}` (all-defaults params).
- [ ] **AC-24:** `validateCameraParams` returns an empty array for `undefined` input (treats as all defaults).

### Determinism ACs

- [ ] **AC-25:** For any valid `CameraPathPreset`, calling `evaluate(t)` with the same `t` and same `params` 1000 times produces identical `CameraFrameState` values every time (C-05).

## Edge Cases and Error Handling

### CameraPathEvaluator

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState` (within tolerance 1e-6) |
| `t = 1` | Returns `defaultEndState` (within tolerance 1e-6) |
| `t = 0.5` | Returns a valid intermediate state (no NaN, no Infinity) |
| `t < 0` or `t > 1` | **Undefined behavior.** Callers (scene renderer) must clamp `t` to `[0, 1]` before calling. Presets may clamp internally as a safety measure, but are not required to. |
| `params` is `undefined` | Uses all defaults (speed=1.0, preset's default easing, offset=[0,0,0]) |
| `params.speed = 0` | Invalid. Caught by `validateCameraParams`. Behavior of `evaluate()` is undefined for speed <= 0. |
| `params.speed = 0.5` | Camera moves half the default displacement. Preset scales its internal displacement accordingly. |
| `params.speed = 2.0` | Camera moves double the default displacement. **Warning:** may cause edge reveals that `oversizeRequirements` at speed=1.0 didn't account for. OBJ-040 must use `displacement * speed` for validation. |
| `params.offset = [1, 0, 0]` | Camera path is shifted 1 unit right in world space. Applied additively to position; lookAt is NOT shifted (it's relative to the scene, not the camera). |
| `params.easing = 'ease_out_cubic'` | Overrides the preset's default easing. The preset must use this easing for its primary interpolation. |

### Registry

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty registry | `getCameraPath` throws. `listCameraPathNames` returns `[]`. `getCameraPathsForGeometry` returns `[]`. |
| Name collision (two presets with same name) | The registry is a `Record<string, CameraPathPreset>` — the last one wins. The assembly module (downstream) must ensure uniqueness. |

### OversizeRequirements

| Scenario | Expected Behavior |
|----------|-------------------|
| Static camera (no motion) | All displacement values are `0`. `recommendedOversizeFactor` is `1.0`. `fovRange` is `[fov, fov]`. |
| FOV animation path (dolly zoom) | `fovRange[0] < fovRange[1]`. The wider FOV frame determines the larger visible area. |
| `recommendedOversizeFactor < 1.0` | Caught by `validateCameraPathPreset` — indicates a bug in the preset definition. |
| Displacement values are negative | Caught by `validateCameraPathPreset`. Displacements are absolute magnitudes. |

### CameraParams Validation

| Scenario | Expected Behavior |
|----------|-------------------|
| `speed: -1` | `validateCameraParams` returns error: "speed must be greater than 0" |
| `speed: 0` | `validateCameraParams` returns error: "speed must be greater than 0" |
| `easing: 'invalid'` | `validateCameraParams` returns error listing valid easing names |
| `offset: [NaN, 0, 0]` | `validateCameraParams` returns error: "offset must contain finite values" |
| `offset: [Infinity, 0, 0]` | `validateCameraParams` returns error: "offset must contain finite values" |
| Unknown fields (e.g., `{ speed: 1.0, custom_param: true }`) | Ignored. No error. Future presets may define custom params. |

## Test Strategy

### Unit Tests

**Registry functions:**
- Build a mock registry with 3 presets (one compatible with `'tunnel'`, one with `'stage'`, one with both).
- `getCameraPath` returns correct preset by name.
- `getCameraPath` throws with informative message for unknown name.
- `isCameraPathName` true/false for known/unknown.
- `listCameraPathNames` returns sorted array.
- `getCameraPathsForGeometry('tunnel')` returns only tunnel-compatible presets.
- `getCameraPathsForGeometry('unknown')` returns empty array.
- Empty registry edge cases.

**Validation (`validateCameraPathPreset`):**
- Create a valid mock preset → returns empty array.
- Mutate one field at a time (bad name, empty compatible geometries, FOV out of range, NaN in evaluate, start/end mismatch, oversize factor < 1.0, negative displacements, invalid easing) → each produces exactly the expected error.
- Preset with FOV animation where mid-path FOV is 0 or 180 → detected.

**Validation (`validateCameraParams`):**
- `{}` → valid.
- `undefined` → valid.
- Various invalid params → correct errors.
- Valid params with all fields → valid.

### Contract Conformance Test Pattern

Each downstream preset (OBJ-026 through OBJ-034) should run a standard contract conformance test suite:

1. **Evaluate boundary:** `evaluate(0)` matches `defaultStartState` within 1e-6.
2. **Evaluate boundary:** `evaluate(1)` matches `defaultEndState` within 1e-6.
3. **Continuity:** Sample 100 points in [0, 1]; no NaN/Infinity in any field.
4. **FOV range:** All sampled FOV values fall within `oversizeRequirements.fovRange` (with tolerance 1e-6).
5. **Determinism:** 100 calls with same `t` produce identical output.
6. **Validation:** `validateCameraPathPreset(preset)` returns empty array.
7. **Speed scaling:** `evaluate(0.5, { speed: 0.5 })` produces less displacement from start than `evaluate(0.5)`.
8. **Easing override:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` (unless the path is static).

This test pattern should be exported as a reusable utility for downstream presets to consume.

### Relevant Testable Claims

- **TC-04** (partial): The type contract ensures LLM authors select preset names, not XYZ coordinates.
- **TC-05** (prerequisite): Tunnel camera path (OBJ-029) will conform to this contract.
- **TC-08** (partial): `compatibleGeometries` metadata enables coverage analysis.
- **TC-09** (prerequisite): Easing override in `CameraParams` enables A/B comparison.

## Integration Points

### Depends on

| Dependency | What is imported |
|---|---|
| **OBJ-002** (`src/interpolation/`) | `EasingName` type for `CameraParams.easing` and `CameraPathPreset.defaultEasing`. `isEasingName()` for validation. |
| **OBJ-003** (`src/spatial/`) | `Vec3` type for positions, lookAt, and offset. No computation functions are used — those are consumed by the preset implementations, not the type contract. |

### Consumed by

| Downstream | How it uses OBJ-006 |
|---|---|
| **OBJ-026** (`static` preset) | Implements `CameraPathPreset` with zero displacement. |
| **OBJ-027** (`slow_push_forward`, `slow_pull_back`) | Implements `CameraPathPreset` with Z-axis interpolation. |
| **OBJ-028** (`lateral_track_left`, `lateral_track_right`) | Implements `CameraPathPreset` with X-axis interpolation. |
| **OBJ-029** (`tunnel_push_forward`) | Implements `CameraPathPreset` tuned for tunnel geometry. |
| **OBJ-030** (`flyover_glide`) | Implements `CameraPathPreset` with elevated Y + forward Z. |
| **OBJ-031** (`gentle_float`) | Implements `CameraPathPreset` with multi-axis sinusoidal drift. |
| **OBJ-032** (`dramatic_push`) | Implements `CameraPathPreset` with aggressive ease-out. |
| **OBJ-033** (`crane_up`) | Implements `CameraPathPreset` with Y-axis rise. |
| **OBJ-034** (`dolly_zoom`) | Implements `CameraPathPreset` with FOV animation. |
| **OBJ-040** (Edge-reveal validation) | Reads `OversizeRequirements` to compute per-plane minimum sizes. Uses `evaluate()` for trajectory sampling. |
| **OBJ-041** (Geometry-camera compatibility) | Reads `compatibleGeometries` for cross-reference validation. |
| **OBJ-045** | Uses registry and types. |
| **OBJ-071** | Uses registry and types. |
| **OBJ-079** | Uses registry and types. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t, params)` each frame to set camera state. |
| **Scene sequencer** (OBJ-010) | Resolves camera preset names from manifest, passes `CameraParams`. |

### File Placement

```
depthkit/
  src/
    camera/
      index.ts          # Barrel export of all types and registry functions
      types.ts          # CameraFrameState, CameraParams, OversizeRequirements,
                        # CameraPathEvaluator, CameraPathPreset
      registry.ts       # getCameraPath, isCameraPathName, listCameraPathNames,
                        # getCameraPathsForGeometry, CameraPathRegistry type
      validate.ts       # validateCameraPathPreset, validateCameraParams
```

**NOTE:** The seed's Section 4.5 places camera code under `src/scenes/cameras/`. This spec proposes `src/camera/` as a top-level module instead, because camera types are consumed by the scene sequencer, the manifest validator, the edge-reveal validator, and the page renderer — they are not scoped to the `scenes/` subdirectory. If OBJ-005 (scene geometry contract) is placed at `src/geometry/`, the parallel structure would be `src/camera/`. If the integrator prefers `src/scenes/cameras/`, the type contract is unaffected — only the import paths change.

## Open Questions

1. **Should `CameraParams` support a `fov_override` for paths with static FOV?** A manifest author might want to use `slow_push_forward` but at a different FOV than the preset's default. Currently, only FOV-animating presets expose FOV control. A simple `fov_override: number` in `CameraParams` would let any path use a custom static FOV. **Recommendation:** Defer to the first preset implementation round (OBJ-027). If the need is confirmed, add `fovOverride?: number` to `CameraParams` — it's backward-compatible.

2. **Should `CameraParams.offset` shift `lookAt` as well as `position`?** The current spec says offset shifts position only. This means `offset: [1, 0, 0]` shifts the camera right but it still looks at the original target — creating a slight angle. An alternative is to shift both, preserving the camera's viewing direction. **Recommendation:** Position-only shift (current design) is more useful for framing adjustments. If both need to shift, the manifest author can override the lookAt in a custom preset. Document this behavior clearly in SKILL.md.

3. **Should there be a `CameraPathPresetFactory` for parameterized preset families?** E.g., `createPushPreset({ axis: 'z', distance: 25 })` to generate variants without writing separate preset objects. **Recommendation:** Defer. The downstream presets (OBJ-027, etc.) can use internal factory functions, but the external type contract doesn't need to expose this pattern. The registry contains concrete `CameraPathPreset` instances, not factories.

4. **Should `evaluate()` accept the scene's total duration or fps?** Currently it only receives `t ∈ [0,1]`. Some presets (like `gentle_float`) might want to vary their sinusoidal frequency based on scene duration — a 5-second scene shouldn't have the same number of oscillations as a 30-second scene. **Recommendation:** This is a valid concern. However, adding duration/fps to the evaluate signature complicates the interface for the 90% case where presets are duration-independent. Presets that need duration awareness can accept it via an additional field in `CameraParams` (e.g., `duration?: number`). Defer to OBJ-031 implementation.

---

I believe this specification is complete and covers all the requirements from the objective metadata, seed sections, dependency contracts, and downstream consumer needs. I'd like the Challenger to review and verify.

---

## Round 2 — spec_challenger

I've read the proposal carefully. It's a solid first draft — the overall structure is sound, the type contract is well-thought-out, and the design decisions are mostly well-reasoned. But I have several issues that need addressing before this is implementable without guessing.

---

## Issues

### Issue 1: `CameraFrameState` vs `CameraState` from OBJ-003 — vocabulary collision (Major)

OBJ-003 already exports a `CameraState` type:

```typescript
export interface CameraState {
  position: Vec3;
  lookAt: Vec3;
  fov: number;
  aspectRatio: number;
  near: number;
  far: number;
}
```

The proposed `CameraFrameState` is a subset (position, lookAt, fov). This creates two overlapping types for "camera state at a moment in time." Downstream consumers (OBJ-040, scene renderer) will need to juggle both. An implementer will ask: "when do I use `CameraState` vs `CameraFrameState`?"

**Proposed fix:** Explicitly document the relationship. `CameraFrameState` is the **path-controlled** subset — what the camera path is responsible for. `CameraState` from OBJ-003 is the **complete** camera state including aspect ratio and near/far (which are composition-level, not path-level). Add a note to the spec stating that the scene renderer constructs a `CameraState` by combining `CameraFrameState` from the path with `aspectRatio`/`near`/`far` from the composition. Optionally, add a utility function signature:

```typescript
/** Combines path output with composition-level camera config. */
export function toCameraState(
  frame: CameraFrameState,
  aspectRatio: number,
  near: number,
  far: number
): CameraState;
```

This makes the boundary explicit rather than leaving each consumer to figure it out.

---

### Issue 2: `CameraParams.offset` applies to position but not lookAt — underspecified visual consequence (Major)

The spec says offset shifts position but not lookAt. The edge case table mentions this creates "a slight angle." But this has a significant consequence for implementers of presets and for the scene renderer.

Consider `slow_push_forward` with `offset: [2, 0, 0]`. The camera starts 2 units right but still looks at `[0, 0, -30]`. That's a diagonal look — the entire scene appears angled. For a tunnel geometry, this means the camera is no longer centered in the tunnel. This is probably the *intended* use case (framing adjustment), but:

1. **Edge-reveal implications are not documented.** A lateral offset shifts the frustum, meaning planes that were safely sized for centered camera may now reveal edges on one side. Does OBJ-040 need to account for offset? The oversizeRequirements section mentions `speed` scaling but never mentions `offset`.

2. **Should presets internally support offset, or should it be applied externally?** If the scene renderer applies offset *after* calling `evaluate()`, presets don't need to know about it. If presets apply it internally, every preset must implement offset logic.

**Proposed fix:** 
- State explicitly whether offset is applied **inside** `evaluate()` (preset responsibility) or **outside** (renderer responsibility, post-evaluate transform). I'd recommend outside — it's a uniform operation that shouldn't be reimplemented per-preset.
- If outside: remove `params` from `CameraPathEvaluator` signature and instead document that the renderer applies `CameraParams` transforms. Actually, `speed` and `easing` clearly need to be inside `evaluate()`, so the split would be: speed+easing inside, offset outside. Document this split.
- Add to `OversizeRequirements` documentation: "Does not account for `CameraParams.offset`. OBJ-040 must add the offset magnitude to displacement calculations."

---

### Issue 3: `speed` semantics are ambiguous for non-linear paths (Major)

The spec says speed is "applied as a scalar to the preset's total displacement." For `slow_push_forward` (linear Z push), this is clear: camera moves `distance * speed` instead of `distance`.

But for `gentle_float` (multi-axis sinusoidal drift) or `dolly_zoom` (coordinated position + FOV), what does `speed = 0.5` mean?

- Half the amplitude of oscillation? (less displacement)
- Half the frequency? (slower oscillation, same displacement)
- Time remapping (play the path at half speed, only reaching t=0.5 at the end)?

Each interpretation produces a completely different visual result. An implementer of OBJ-031 will have to guess.

**Proposed fix:** Define `speed` precisely. I'd recommend: **`speed` scales the total displacement/amplitude of the path's motion, NOT the temporal rate.** A `speed: 0.5` gentle_float drifts half as far in each axis. A `speed: 0.5` dolly_zoom pushes half as far forward and animates FOV half as much. This keeps the path's temporal feel (its easing curve) intact while scaling its spatial intensity. Add this definition to the `CameraParams.speed` docstring.

---

### Issue 4: Contract conformance test for `speed` is wrong (Minor)

AC pattern item 7: "Speed scaling: `evaluate(0.5, { speed: 0.5 })` produces less displacement from start than `evaluate(0.5)`."

This is not necessarily true for oscillating paths. At t=0.5, a sinusoidal drift might be at zero displacement regardless of speed. The test should compare the *maximum* displacement across the full path, not a single point.

**Proposed fix:** Restate as: "Speed scaling: the maximum Euclidean distance between `evaluate(t, { speed: 0.5 }).position` and `defaultStartState.position` over 100 samples is less than the maximum distance with default params (unless the preset is static)."

---

### Issue 5: Missing snake_case validation regex escape (Minor)

AC-19 says the name regex is `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`. This forbids names that start with a digit after the first character in a segment... actually, looking more carefully, it requires each `_`-separated segment to start with `[a-z0-9]`. Wait — the first segment requires `[a-z]` start, subsequent segments allow `[a-z0-9]` start. That's fine. But it forbids single-character names like `"a"` — wait, no, `[a-z][a-z0-9]*` matches `"a"`. OK, the regex is correct. I withdraw this issue.

---

### Issue 6: `compatibleGeometries` — no wildcard, explicit enumeration, but geometry names not yet known (Major)

D5 says "list all known geometry names explicitly rather than using a wildcard." But OBJ-005 (which defines geometry names) is `in_progress` and has no output yet. This means:

1. Downstream preset implementers (OBJ-026–034) can't fill in `compatibleGeometries` because the geometry names aren't finalized.
2. The validation function checks for non-empty `compatibleGeometries`, but can't validate that the geometry names are real.

The spec acknowledges this ("OBJ-005 is in-progress") but the consequence is underspecified.

**Proposed fix:** Add a note: "Preset implementations should use the geometry names from OBJ-005's finalized spec. Until OBJ-005 is finalized, preset implementations may use provisional names matching the seed's Section 4.2 names (`stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`). When OBJ-005 finalizes, OBJ-041 (compatibility validation) will cross-reference these." Also: the validation function `validateCameraPathPreset` cannot validate geometry name correctness — only non-emptiness. State this explicitly and note that geometry name validation belongs to OBJ-041.

---

### Issue 7: `evaluate()` receiving `CameraParams` means presets must parse/validate params (Minor-to-Major)

Every preset implementation must:
1. Handle `params` being undefined
2. Resolve `easing` from string to function via `getEasing()`
3. Apply `speed` scaling
4. Apply `offset` (if kept inside evaluate)

This is boilerplate that will be duplicated across 10+ presets. The spec should either:
- Define a helper that preprocesses `CameraParams` into resolved values, or
- Acknowledge this as expected boilerplate and note that preset implementers should create their own shared utility

**Proposed fix:** Add a utility signature to `src/camera/validate.ts` or a new `src/camera/params.ts`:

```typescript
export interface ResolvedCameraParams {
  speed: number;       // guaranteed > 0
  easing: EasingFn;    // resolved from name or function
  offset: Vec3;        // guaranteed finite
}

/**
 * Resolves and validates CameraParams, applying defaults.
 * @throws if params are invalid (speed <= 0, bad easing, non-finite offset)
 */
export function resolveCameraParams(
  params: CameraParams | undefined,
  defaultEasing: EasingName
): ResolvedCameraParams;
```

This gives preset implementers a clean, validated input. The `defaultEasing` parameter lets each preset pass its own default.

---

### Issue 8: No mention of how the browser-side renderer accesses presets (Minor)

The seed's architecture splits code between Node.js (`src/engine/`) and browser (`src/page/`). The scene renderer in the browser needs to call `evaluate(t, params)` every frame. The spec places all camera code in `src/camera/` but doesn't mention the isomorphism requirement.

OBJ-002 explicitly addresses this (D1: "Isomorphic module shared via build-time bundling"). OBJ-006 should state the same constraint since `evaluate()` runs in the browser.

**Proposed fix:** Add a design decision or integration note: "Like OBJ-002's interpolation module, the camera module must be isomorphic — it runs in both Node.js (validation, scene sequencing) and headless Chromium (frame rendering). All code in `src/camera/` must use only pure JavaScript/TypeScript with no Node.js-specific or browser-specific APIs. The build system bundles this module into the page payload alongside `src/interpolation/`."

---

### Issue 9: `OversizeRequirements.maxDisplacementZ` description is misleading (Minor)

The description says "Used to determine depth-related visible area changes (as camera moves forward, nearby planes need to be wider)." This implies a specific computation that isn't defined here. The relationship between Z displacement and required plane width is non-trivial (it depends on the plane's Z position relative to the camera, which changes as the camera moves).

**Proposed fix:** Simplify the description: "Maximum camera displacement along the Z axis (world units). Consumed by OBJ-040 to compute worst-case visible area at each plane's depth." Don't describe *how* it's used — that's OBJ-040's responsibility.

---

### Issue 10: Missing AC for `toCameraState` (if added per Issue 1) (Conditional)

If Issue 1's fix is adopted, an AC should verify `toCameraState` correctly merges the two sources.

---

## Points of Agreement

These are sound and I'd like to preserve them in the final spec:

1. **D1 (evaluation function over keyframes)** — excellent choice. The diversity of preset behaviors (static, linear, sinusoidal, coordinated) makes a functional interface the right call.

2. **D6 (registry as parameter)** — clean testability pattern. Good.

3. **D7 (Vec3 from OBJ-003)** — correct reuse of spatial primitives.

4. **D8 (FOV always present)** — eliminates conditionals in the renderer. Good.

5. **The contract conformance test pattern** — reusable test suite for all presets is exactly the right approach. With the fix from Issue 4.

6. **File placement at `src/camera/`** — correct scoping.

7. **Validation returning error arrays** — clean, composable, no exceptions for expected validation failures.

---

## Summary

**Critical issues:** None (nothing blocks implementation entirely).

**Major issues (must fix):**
- Issue 1: CameraFrameState vs CameraState relationship
- Issue 2: Offset application — inside or outside evaluate()
- Issue 3: Speed semantics for non-linear paths
- Issue 6: compatibleGeometries provisional names
- Issue 7: CameraParams resolution boilerplate

**Minor issues (should fix):**
- Issue 4: Contract conformance test for speed
- Issue 8: Isomorphism constraint
- Issue 9: maxDisplacementZ description

Please revise and I'll verify the fixes.

---

## Round 3 — spec_author

Thank you for the thorough review. All issues are valid. Here's the revised specification with each issue addressed:

---

# Specification: OBJ-006 — Camera Path Type Contract

## Summary

OBJ-006 defines the TypeScript type system for camera path presets in depthkit. A camera path preset is a named, self-contained unit that maps normalized time `t ∈ [0, 1]` to a complete camera state (`position`, `lookAt`, `fov`) and carries metadata for validation, edge-reveal prevention, and blind authoring. This is the Tier 1 contract that all downstream camera path preset implementations (OBJ-026 through OBJ-034) conform to, and that the scene sequencer (OBJ-010), edge-reveal validator (OBJ-040), and geometry-camera compatibility validator (OBJ-041) consume.

## Interface Contract

### Core Types

```typescript
// src/camera/types.ts

import { Vec3, CameraState } from '../spatial/types';
import { EasingName, EasingFn } from '../interpolation/easings';

/**
 * The path-controlled subset of camera state at a single moment in time.
 * Returned by a camera path's evaluate() function.
 *
 * Relationship to CameraState (OBJ-003): CameraFrameState contains only
 * the properties that a camera PATH controls — position, lookAt, fov.
 * The complete CameraState also includes aspectRatio, near, and far,
 * which are composition-level constants (set from the manifest's
 * composition.width/height and the geometry's near/far recommendations).
 * The scene renderer constructs a full CameraState by combining
 * CameraFrameState from the path with composition-level values.
 * Use toCameraState() to perform this merge.
 */
export interface CameraFrameState {
  /** Camera position in world space [x, y, z] */
  position: Vec3;
  /** Camera lookAt target in world space [x, y, z] */
  lookAt: Vec3;
  /** Vertical field of view in degrees. Must be in (0, 180). */
  fov: number;
}

/**
 * Combines path-controlled camera state with composition-level constants
 * to produce a complete CameraState (as defined by OBJ-003).
 *
 * @param frame - Path output from evaluate().
 * @param aspectRatio - Composition width / height (e.g., 16/9).
 * @param near - Near clipping plane distance. Default: 0.1.
 * @param far - Far clipping plane distance. Default: 100.
 * @returns Complete CameraState suitable for Three.js camera configuration.
 */
export function toCameraState(
  frame: CameraFrameState,
  aspectRatio: number,
  near?: number,
  far?: number
): CameraState;

/**
 * Parameters the manifest author can pass to customize a camera path
 * at the scene level. These override the preset's defaults.
 *
 * Presets receive RESOLVED params (via resolveCameraParams), never raw
 * CameraParams. See ResolvedCameraParams.
 *
 * Unrecognized fields are ignored (not rejected) — this allows presets
 * to evolve without breaking existing manifests.
 */
export interface CameraParams {
  /**
   * Amplitude/displacement multiplier. Scales the spatial intensity
   * of the path's motion, NOT its temporal rate.
   *
   * For linear paths (push/pull/track): scales total displacement.
   *   speed=0.5 on a 25-unit Z push → 12.5-unit push.
   * For oscillating paths (gentle_float): scales amplitude.
   *   speed=0.5 → half the drift range in each axis.
   * For FOV-animating paths (dolly_zoom): scales FOV delta.
   *   speed=0.5 → half the FOV change.
   *
   * The temporal easing curve is unaffected. A speed=0.5 path still
   * starts and ends at the same normalized times — it just covers
   * less spatial ground.
   *
   * Must be > 0. Default: 1.0.
   */
  speed?: number;

  /**
   * Easing override for the primary motion.
   * Replaces the preset's default easing.
   */
  easing?: EasingName;

  /**
   * Additive offset to the camera's position, in world units.
   * Applied OUTSIDE evaluate() by the scene renderer — presets
   * never see this value. The renderer adds offset to the position
   * returned by evaluate() before setting the Three.js camera.
   *
   * lookAt is NOT shifted. This means offset creates a slight
   * viewing angle change — the camera is displaced but still
   * looks at the scene's focal point. This is intentional for
   * framing adjustments (e.g., shift camera right to reframe
   * the subject).
   *
   * Edge-reveal implication: offset displaces the frustum.
   * OBJ-040 must add abs(offset[i]) to the path's displacement
   * in each axis when computing required plane sizes.
   *
   * Default: [0, 0, 0].
   */
  offset?: Vec3;
}

/**
 * Resolved and validated CameraParams, ready for preset consumption.
 * Produced by resolveCameraParams(). Presets receive this, not raw CameraParams.
 *
 * Note: offset is NOT included here because it is applied outside
 * evaluate() by the renderer. Presets only need speed and easing.
 */
export interface ResolvedCameraParams {
  /** Guaranteed > 0. */
  speed: number;
  /** Resolved easing function. */
  easing: EasingFn;
}

/**
 * Resolves raw CameraParams into validated, defaulted values.
 * Presets call this at the top of their evaluate() to get clean inputs.
 *
 * @param params - Raw params from manifest (may be undefined).
 * @param defaultEasing - The preset's own default easing name.
 * @returns Resolved params with defaults applied.
 * @throws {Error} if speed <= 0, easing is invalid, or offset is non-finite.
 */
export function resolveCameraParams(
  params: CameraParams | undefined,
  defaultEasing: EasingName
): ResolvedCameraParams;

/**
 * Oversizing metadata that a camera path preset provides so that
 * OBJ-040 (edge-reveal validation) and geometry definitions can
 * compute the minimum plane sizes needed to prevent edge reveals.
 *
 * All displacement values describe the MAXIMUM extent of camera motion
 * in each axis, in world units, at the preset's default speed (speed=1.0).
 *
 * For speed != 1.0, effective displacements scale linearly:
 *   effectiveDisplacement = maxDisplacement * speed
 *
 * These values do NOT account for CameraParams.offset. OBJ-040 must
 * add abs(offset[i]) to each axis displacement when validating.
 */
export interface OversizeRequirements {
  /**
   * Maximum camera displacement along the X axis (world units).
   * Must be >= 0.
   */
  maxDisplacementX: number;

  /**
   * Maximum camera displacement along the Y axis (world units).
   * Must be >= 0.
   */
  maxDisplacementY: number;

  /**
   * Maximum camera displacement along the Z axis (world units).
   * Must be >= 0. Consumed by OBJ-040 to compute worst-case
   * visible area at each plane's depth.
   */
  maxDisplacementZ: number;

  /**
   * The FOV range across the path's duration: [min, max] in degrees.
   * Both values must be in (0, 180). min <= max.
   * For paths with no FOV animation, min === max.
   */
  fovRange: readonly [number, number];

  /**
   * Recommended uniform oversize factor for "simple" plane sizing.
   * A single scalar >= 1.0 that is sufficient to prevent edge reveals
   * for ALL planes in all compatible geometries, assuming planes are
   * sized to the frustum at their distance from the camera's start
   * position and speed=1.0.
   *
   * OBJ-040 may compute more precise per-plane factors using the
   * displacement values above. This scalar is a safe upper bound.
   */
  recommendedOversizeFactor: number;
}

/**
 * A camera path evaluation function.
 * Given normalized time t in [0, 1], returns the path-controlled camera state.
 *
 * Contract:
 * - t = 0 returns the camera's start state.
 * - t = 1 returns the camera's end state.
 * - Values are continuous between 0 and 1 (no discontinuities).
 * - Behavior for t outside [0, 1] is undefined. Callers must clamp.
 * - CameraParams.offset is NOT handled here — it is applied by the
 *   scene renderer after evaluate() returns.
 *
 * Implementations should call resolveCameraParams() at the top of
 * their function body to get validated speed and easing values.
 */
export type CameraPathEvaluator = (
  t: number,
  params?: CameraParams
) => CameraFrameState;

/**
 * The complete definition of a camera path preset.
 * This is the type that all OBJ-026 through OBJ-034 implementations export.
 */
export interface CameraPathPreset {
  /** Unique preset name. Must match the key in the registry. Lowercase snake_case. */
  name: string;

  /**
   * Human-readable description for SKILL.md and error messages.
   * Should describe the visual effect in 1-2 sentences.
   */
  description: string;

  /**
   * The evaluation function. Given t in [0, 1] and optional params,
   * returns the path-controlled camera state.
   */
  evaluate: CameraPathEvaluator;

  /**
   * The camera state at t=0 with default params (speed=1, default easing, no offset).
   * Redundant with evaluate(0), but provided as static data for
   * fast access during validation without calling evaluate().
   */
  defaultStartState: CameraFrameState;

  /**
   * The camera state at t=1 with default params.
   * Redundant with evaluate(1), but provided as static data.
   */
  defaultEndState: CameraFrameState;

  /**
   * Default easing applied to the primary motion.
   * Can be overridden by CameraParams.easing in the manifest.
   */
  defaultEasing: EasingName;

  /**
   * Names of scene geometries this path is designed to work with.
   * The geometry-camera compatibility validator (OBJ-041) uses this
   * to reject invalid combinations in the manifest.
   *
   * Must be non-empty. List geometry names explicitly — no wildcards.
   * Until OBJ-005 finalizes geometry names, use provisional names
   * from seed Section 4.2: 'stage', 'tunnel', 'canyon', 'flyover',
   * 'diorama', 'portal', 'panorama', 'close_up'.
   *
   * When a new geometry is added, each preset must explicitly declare
   * compatibility with it (or not). This keeps compatibility auditable.
   *
   * NOTE: validateCameraPathPreset checks only for non-emptiness.
   * Geometry name existence validation belongs to OBJ-041, which
   * cross-references against the geometry registry.
   */
  compatibleGeometries: readonly string[];

  /**
   * Oversizing metadata for edge-reveal prevention.
   * Describes the spatial envelope of the camera's motion.
   */
  oversizeRequirements: OversizeRequirements;

  /**
   * Tags for categorizing and searching presets in SKILL.md
   * and for LLM-assisted preset selection. Lowercase.
   * Examples: ['push', 'forward', 'dramatic'], ['ambient', 'subtle', 'float'].
   */
  tags: readonly string[];
}
```

### Registry

```typescript
// src/camera/registry.ts

import { CameraPathPreset } from './types';

/**
 * Type-safe registry of all camera path presets.
 * Downstream objectives (OBJ-026 through OBJ-034) register their
 * presets here. The registry is frozen at build time — no runtime mutation.
 *
 * Keys are preset names (lowercase snake_case). Values are CameraPathPreset objects.
 */
export type CameraPathRegistry = Readonly<Record<string, CameraPathPreset>>;

/**
 * Retrieves a camera path preset by name.
 * @param registry - The camera path registry to search.
 * @param name - The preset name.
 * @returns The CameraPathPreset.
 * @throws {Error} if name is not found. Error message includes the
 *   invalid name and lists all available preset names.
 */
export function getCameraPath(
  registry: CameraPathRegistry,
  name: string
): CameraPathPreset;

/**
 * Type guard: checks if a name exists in the given registry.
 */
export function isCameraPathName(
  registry: CameraPathRegistry,
  name: string
): boolean;

/**
 * Returns all preset names in the registry, sorted alphabetically.
 */
export function listCameraPathNames(
  registry: CameraPathRegistry
): readonly string[];

/**
 * Returns all presets compatible with a given geometry name.
 * @param registry - The camera path registry.
 * @param geometryName - The geometry to filter by.
 * @returns Array of compatible CameraPathPreset objects. Empty if none match.
 */
export function getCameraPathsForGeometry(
  registry: CameraPathRegistry,
  geometryName: string
): readonly CameraPathPreset[];
```

### Validation Utility

```typescript
// src/camera/validate.ts

import { CameraPathPreset, CameraParams } from './types';

/**
 * Validates that a CameraPathPreset satisfies its own internal contract.
 * Used during development/testing — NOT runtime manifest validation.
 *
 * Checks:
 * 1. evaluate(0) matches defaultStartState (within tolerance 1e-6 per component).
 * 2. evaluate(1) matches defaultEndState (within tolerance 1e-6 per component).
 * 3. FOV is within (0, 180) at 100 evenly-spaced sample points in [0, 1].
 * 4. evaluate() returns finite values (no NaN/Infinity) for position, lookAt,
 *    and fov at 100 sample points.
 * 5. oversizeRequirements.recommendedOversizeFactor >= 1.0.
 * 6. oversizeRequirements.fovRange[0] <= fovRange[1], both in (0, 180).
 * 7. oversizeRequirements displacement values are >= 0.
 * 8. name is non-empty, lowercase snake_case (regex: /^[a-z][a-z0-9]*(_[a-z0-9]+)*$/).
 * 9. compatibleGeometries is non-empty.
 *    NOTE: does NOT validate that geometry names are real — that's OBJ-041.
 * 10. defaultEasing is a valid EasingName.
 * 11. All sampled FOV values fall within oversizeRequirements.fovRange (tolerance 1e-6).
 *
 * @param preset - The preset to validate.
 * @returns Array of validation error strings. Empty array = valid.
 */
export function validateCameraPathPreset(
  preset: CameraPathPreset
): readonly string[];

/**
 * Validates CameraParams from a manifest scene.
 * Checks:
 * 1. speed > 0 (if provided).
 * 2. easing is a valid EasingName (if provided).
 * 3. offset contains finite values (if provided).
 *
 * @param params - The params to validate. undefined treated as all-defaults (valid).
 * @returns Array of validation error strings. Empty array = valid.
 */
export function validateCameraParams(
  params: CameraParams | undefined
): readonly string[];
```

### Module Exports

```typescript
// src/camera/index.ts

export type {
  CameraFrameState,
  CameraParams,
  ResolvedCameraParams,
  OversizeRequirements,
  CameraPathEvaluator,
  CameraPathPreset,
} from './types';

export {
  toCameraState,
  resolveCameraParams,
} from './types';

export type { CameraPathRegistry } from './registry';

export {
  getCameraPath,
  isCameraPathName,
  listCameraPathNames,
  getCameraPathsForGeometry,
} from './registry';

export {
  validateCameraPathPreset,
  validateCameraParams,
} from './validate';
```

## Design Decisions

### D1: Evaluation function over keyframe data

**Decision:** Camera path presets define an `evaluate(t, params) => CameraFrameState` function rather than exposing raw keyframe data that the caller interpolates.

**Rationale:** Downstream presets vary dramatically in complexity. `static` (OBJ-026) returns the same state for all `t`. `slow_push_forward` (OBJ-027) is linear Z interpolation. `gentle_float` (OBJ-031) involves multi-axis sinusoidal drift. `dolly_zoom` (OBJ-034) requires coordinated position + FOV animation. A keyframe-based interface would either be too simple for complex presets or too complex for simple ones. The evaluation function lets each preset own its interpolation logic (using OBJ-002 utilities internally) while presenting a uniform interface.

**Trade-off:** Callers cannot introspect the trajectory without sampling. Mitigated by `defaultStartState`, `defaultEndState`, and `oversizeRequirements` as static metadata.

### D2: CameraParams split — speed and easing inside evaluate(), offset outside

**Decision:** `CameraParams` has three fields: `speed`, `easing`, and `offset`. Speed and easing are handled inside `evaluate()` (via `resolveCameraParams()`). Offset is applied by the scene renderer *after* `evaluate()` returns — presets never see it.

**Rationale for the split:**
- **Speed** must be inside `evaluate()` because it changes how the preset computes positions (scaling displacement/amplitude). Only the preset knows its internal motion structure.
- **Easing** must be inside `evaluate()` because it changes the temporal mapping from `t` to eased time. Only the preset knows where to apply it.
- **Offset** is a uniform post-transform — add `[ox, oy, oz]` to position. This is identical for every preset. Putting it inside `evaluate()` would force every preset to implement the same addition, creating boilerplate. Putting it outside means one line in the renderer: `position = add(evaluate(t, params).position, resolvedOffset)`.

**Consequence:** `ResolvedCameraParams` contains only `speed` and `easing` (not offset). The renderer resolves offset separately and applies it post-evaluate. OBJ-040 must account for offset when computing edge-reveal margins (add `abs(offset[i])` to each axis displacement).

### D3: Speed scales spatial amplitude, not temporal rate

**Decision:** `speed` is a displacement/amplitude multiplier. `speed: 0.5` means the camera covers half the spatial distance/range. The temporal easing curve is unaffected — the path still starts at t=0 and ends at t=1 with the same easing shape.

**Rationale:** For linear paths (push/pull/track), both interpretations (half displacement vs. time remapping) produce similar results. But for oscillating paths (`gentle_float`), they diverge dramatically:
- Half amplitude: same number of oscillations, smaller range. The path feels "calmer."
- Half speed (time remap): reaches only the midpoint of the oscillation pattern. The path feels "cut short."

Amplitude scaling is more intuitive for LLM authors: "make it more/less intense" maps naturally to speed. Time remapping is harder to reason about ("play half the animation" — what happens to the easing?). The seed's manifest example shows `"speed": 1.0` as an intensity control, not a playback rate.

**Per-preset application:** Each preset applies speed to its own motion structure:
- Linear Z push: `totalDisplacement * speed`
- Sinusoidal drift: `amplitude * speed` per axis
- Dolly zoom: `zDisplacement * speed` for position, `fovDelta * speed` for FOV

### D4: OversizeRequirements as structured metadata, not a single scalar

**Decision:** Presets expose per-axis displacement maximums and FOV range, plus a convenience `recommendedOversizeFactor` scalar.

**Rationale:** OBJ-040 needs per-axis displacements to compute precise per-plane oversize factors. A lateral track only needs horizontal oversizing, not vertical. The `recommendedOversizeFactor` convenience scalar serves simpler consumers that want a safe margin without the full OBJ-040 algorithm. It must be a safe upper bound for the worst-case plane in any compatible geometry at speed=1.0.

**Interaction with CameraParams:** Effective displacements are `maxDisplacement * speed`. Offset adds `abs(offset[i])` per axis. OBJ-040 must account for both.

### D5: Static defaultStartState and defaultEndState alongside evaluate()

**Decision:** Presets provide pre-computed start and end states as static data, redundant with `evaluate(0)` and `evaluate(1)`.

**Rationale:** Validation (OBJ-041) needs quick compatibility checks. Having start/end states as static data means validators don't need to reason about evaluate()'s side effects. Also serves as self-documentation. `validateCameraPathPreset` checks consistency between the static data and `evaluate()`.

### D6: compatibleGeometries as explicit string enumeration

**Decision:** `compatibleGeometries` is `readonly string[]` with explicit geometry name enumeration. No wildcards. Must be non-empty.

**Rationale:** Explicit enumeration keeps compatibility auditable. When a new geometry is added, each preset must explicitly declare compatibility. Implicit universal compatibility via `['*']` risks silent false-positive compatibility with untested geometries.

**Provisional names:** Until OBJ-005 finalizes, presets use seed Section 4.2 names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`. `validateCameraPathPreset` checks only for non-emptiness. Geometry name existence validation belongs to OBJ-041.

### D7: Registry takes registry as parameter, not a singleton

**Decision:** `getCameraPath(registry, name)` accepts the registry as an argument.

**Rationale:** Testability. Unit tests can pass mock registries. Avoids import-order issues.

### D8: Vec3 from OBJ-003, not Three.js types

**Decision:** All spatial types use `Vec3` from `src/spatial/types.ts`.

**Rationale:** JSON-serializable for Puppeteer message passing. Renderer-agnostic. Consistent with OBJ-003's D1.

### D9: FOV always returned from evaluate()

**Decision:** `CameraFrameState` always includes `fov`, even for static-FOV paths.

**Rationale:** Eliminates conditionals in the renderer. For static-FOV paths, `evaluate()` returns the same value for all `t`. `OversizeRequirements.fovRange` with `min === max` signals no animation.

### D10: CameraFrameState is path-controlled subset of CameraState

**Decision:** `CameraFrameState` (position, lookAt, fov) is the path-controlled subset. `CameraState` from OBJ-003 adds aspectRatio, near, far (composition-level). `toCameraState()` merges them.

**Rationale:** Camera paths should not concern themselves with aspect ratio or clipping planes — these are determined by the manifest's composition settings and the geometry's spatial bounds. The clean separation avoids coupling paths to composition config. The explicit `toCameraState()` bridge function makes the merge point visible rather than leaving each consumer to figure it out.

### D11: resolveCameraParams() eliminates boilerplate across presets

**Decision:** A shared `resolveCameraParams(params, defaultEasing)` function resolves raw `CameraParams` into a `ResolvedCameraParams` with validated `speed: number` and `easing: EasingFn`.

**Rationale:** Without this, every preset must: check if params is undefined, default speed to 1.0, resolve easing name to function via `getEasing()`. This is ~5 lines of boilerplate duplicated across 10+ presets. `resolveCameraParams` centralizes it. The `defaultEasing` parameter lets each preset supply its own default.

### D12: Isomorphic module — no platform-specific APIs

**Decision:** All code in `src/camera/` must be pure JavaScript/TypeScript with no Node.js-specific APIs (`process`, `fs`, `Buffer`) and no browser-specific APIs (`window`, `document`, `requestAnimationFrame`).

**Rationale:** Like OBJ-002's interpolation module (D1), the camera module runs in both Node.js (validation, scene sequencing) and headless Chromium (frame rendering via evaluate()). The build system bundles this module into the page payload alongside `src/interpolation/`. Platform-specific code would break one context or the other.

## Acceptance Criteria

### Type Contract ACs

- [ ] **AC-01:** `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `ResolvedCameraParams`, `OversizeRequirements`, `CameraPathEvaluator` are all exported from `src/camera/index.ts`.
- [ ] **AC-02:** `CameraFrameState.position` and `CameraFrameState.lookAt` use the `Vec3` type from `src/spatial/types.ts`.
- [ ] **AC-03:** `CameraFrameState.fov` is `number` (degrees), not optional.
- [ ] **AC-04:** `CameraPathPreset.evaluate` accepts `(t: number, params?: CameraParams)` and returns `CameraFrameState`.
- [ ] **AC-05:** `CameraPathPreset.compatibleGeometries` is `readonly string[]`.
- [ ] **AC-06:** `CameraPathPreset.oversizeRequirements` includes `maxDisplacementX`, `maxDisplacementY`, `maxDisplacementZ`, `fovRange`, and `recommendedOversizeFactor`.
- [ ] **AC-07:** `CameraParams.speed`, `CameraParams.easing`, and `CameraParams.offset` are all optional.
- [ ] **AC-08:** `OversizeRequirements.fovRange` is `readonly [number, number]`.

### toCameraState ACs

- [ ] **AC-09:** `toCameraState({ position: [0,0,5], lookAt: [0,0,0], fov: 50 }, 16/9)` returns a `CameraState` with `position: [0,0,5]`, `lookAt: [0,0,0]`, `fov: 50`, `aspectRatio: 16/9`, `near: 0.1`, `far: 100`.
- [ ] **AC-10:** `toCameraState(frame, 16/9, 0.5, 200)` returns `near: 0.5` and `far: 200` (overriding defaults).

### resolveCameraParams ACs

- [ ] **AC-11:** `resolveCameraParams(undefined, 'ease_in_out')` returns `{ speed: 1.0, easing: <ease_in_out function> }`.
- [ ] **AC-12:** `resolveCameraParams({ speed: 2.0, easing: 'linear' }, 'ease_in_out')` returns `{ speed: 2.0, easing: <linear function> }`.
- [ ] **AC-13:** `resolveCameraParams({ speed: -1 }, 'linear')` throws an `Error`.
- [ ] **AC-14:** `resolveCameraParams({ speed: 0 }, 'linear')` throws an `Error`.
- [ ] **AC-15:** `resolveCameraParams({ easing: 'invalid' }, 'linear')` throws an `Error` whose message includes `'invalid'` and lists valid easing names.

### Registry ACs

- [ ] **AC-16:** `getCameraPath(registry, 'nonexistent')` throws an `Error` whose message includes `'nonexistent'` and lists all available preset names.
- [ ] **AC-17:** `isCameraPathName(registry, name)` returns `true` for registered names, `false` for unregistered.
- [ ] **AC-18:** `listCameraPathNames(registry)` returns names in alphabetical order.
- [ ] **AC-19:** `getCameraPathsForGeometry(registry, 'tunnel')` returns only presets whose `compatibleGeometries` includes `'tunnel'`.
- [ ] **AC-20:** `getCameraPathsForGeometry(registry, 'nonexistent_geometry')` returns an empty array (no throw).

### Validation ACs

- [ ] **AC-21:** `validateCameraPathPreset` detects a preset where `evaluate(0).position` disagrees with `defaultStartState.position` by > 1e-6 in any component.
- [ ] **AC-22:** `validateCameraPathPreset` detects a preset where FOV at any of 100 evenly-spaced sample points is <= 0 or >= 180.
- [ ] **AC-23:** `validateCameraPathPreset` detects a preset where `evaluate()` returns NaN or Infinity for position, lookAt, or fov at any of 100 sample points.
- [ ] **AC-24:** `validateCameraPathPreset` detects `recommendedOversizeFactor < 1.0`.
- [ ] **AC-25:** `validateCameraPathPreset` detects an empty `compatibleGeometries` array.
- [ ] **AC-26:** `validateCameraPathPreset` detects a `name` that is empty or not lowercase snake_case (regex: `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`).
- [ ] **AC-27:** `validateCameraPathPreset` detects a `defaultEasing` that is not a valid `EasingName`.
- [ ] **AC-28:** `validateCameraPathPreset` returns an empty array for a well-formed preset.
- [ ] **AC-29:** `validateCameraPathPreset` detects negative displacement values in `oversizeRequirements`.
- [ ] **AC-30:** `validateCameraPathPreset` detects sampled FOV values outside the declared `oversizeRequirements.fovRange` (tolerance 1e-6).
- [ ] **AC-31:** `validateCameraParams` detects `speed <= 0`, invalid `easing` names, and non-finite `offset` values.
- [ ] **AC-32:** `validateCameraParams` returns an empty array for `{}` (all-defaults).
- [ ] **AC-33:** `validateCameraParams` returns an empty array for `undefined` input.

### Determinism ACs

- [ ] **AC-34:** For any valid `CameraPathPreset`, calling `evaluate(t)` with the same `t` and same `params` 1000 times produces identical `CameraFrameState` values every time (C-05).

### Isomorphism ACs

- [ ] **AC-35:** The module has zero runtime imports outside `src/camera/`, `src/spatial/`, and `src/interpolation/`.
- [ ] **AC-36:** The module uses no Node.js-specific APIs and no browser-specific APIs.

## Edge Cases and Error Handling

### CameraPathEvaluator

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns values matching `defaultStartState` (within 1e-6 per component) |
| `t = 1` | Returns values matching `defaultEndState` (within 1e-6 per component) |
| `t = 0.5` | Returns a valid intermediate state (no NaN, no Infinity, FOV in (0,180)) |
| `t < 0` or `t > 1` | **Undefined behavior.** Callers must clamp before calling. Presets may clamp internally as a safety measure but are not required to. |
| `params` is `undefined` | Uses all defaults (speed=1.0, preset's default easing). Offset not applicable (applied externally). |
| `params.speed = 0` | Invalid. `resolveCameraParams` throws. |
| `params.speed = 0.5` | Camera's spatial amplitude/displacement is halved. Temporal easing unchanged. |
| `params.speed = 2.0` | Camera's spatial amplitude/displacement is doubled. **Warning:** may cause edge reveals. OBJ-040 must use `displacement * speed`. |
| `params.easing = 'ease_out_cubic'` | Overrides the preset's default easing for the primary interpolation. |

### Offset (applied by renderer, post-evaluate)

| Scenario | Expected Behavior |
|----------|-------------------|
| `offset = [0, 0, 0]` | No change to evaluate() output. |
| `offset = [1, 0, 0]` | Renderer adds [1,0,0] to position. lookAt unchanged → slight viewing angle shift. |
| `offset = [NaN, 0, 0]` | Caught by `validateCameraParams`. Renderer should not receive invalid offset. |
| Large offset (e.g., [10, 0, 0]) | Valid but likely causes edge reveals. OBJ-040 accounts for this. |

### Registry

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty registry | `getCameraPath` throws. `listCameraPathNames` returns `[]`. `getCameraPathsForGeometry` returns `[]`. |
| Name collision | `Record<string, ...>` — last assignment wins. Assembly module must ensure uniqueness. |

### OversizeRequirements

| Scenario | Expected Behavior |
|----------|-------------------|
| Static camera (no motion) | All displacements = `0`. `recommendedOversizeFactor` = `1.0`. `fovRange` = `[fov, fov]`. |
| FOV animation | `fovRange[0] < fovRange[1]`. Wider FOV moment determines larger visible area. |
| `recommendedOversizeFactor < 1.0` | Caught by `validateCameraPathPreset`. |
| Negative displacement | Caught by `validateCameraPathPreset`. Displacements are absolute magnitudes, always >= 0. |

### resolveCameraParams

| Scenario | Expected Behavior |
|----------|-------------------|
| `undefined` | Returns `{ speed: 1.0, easing: <defaultEasing function> }` |
| `{}` | Same as undefined — all defaults. |
| `{ speed: -1 }` | Throws: "speed must be greater than 0, got -1" |
| `{ speed: 0 }` | Throws: "speed must be greater than 0, got 0" |
| `{ easing: 'invalid' }` | Throws: includes `'invalid'` and lists valid easing names |
| `{ speed: 1.5, easing: 'ease_out' }` | Returns `{ speed: 1.5, easing: <ease_out function> }` |

### toCameraState

| Scenario | Expected Behavior |
|----------|-------------------|
| All defaults | `near: 0.1`, `far: 100` (from OBJ-003 `DEFAULT_CAMERA`) |
| Custom near/far | Uses provided values |
| `aspectRatio <= 0` | Undefined behavior — composition validation catches this upstream |

## Test Strategy

### Unit Tests

**Registry functions:**
- Build a mock registry with 3 presets (one compatible with `'tunnel'`, one with `'stage'`, one with both).
- `getCameraPath` returns correct preset by name.
- `getCameraPath` throws with informative message for unknown name.
- `isCameraPathName` true/false for known/unknown.
- `listCameraPathNames` returns sorted array.
- `getCameraPathsForGeometry('tunnel')` returns only tunnel-compatible presets.
- `getCameraPathsForGeometry('unknown')` returns empty array.
- Empty registry edge cases.

**resolveCameraParams:**
- `undefined` → defaults.
- `{}` → defaults.
- Valid speed + easing → resolved correctly.
- Speed <= 0 → throws.
- Invalid easing → throws with valid names listed.
- Verify returned easing function is callable and matches expected behavior.

**toCameraState:**
- Default near/far applied.
- Custom near/far used.
- All CameraFrameState fields pass through unchanged.

**Validation (`validateCameraPathPreset`):**
- Create a valid mock preset (with evaluate function, matching start/end states, valid oversize requirements) → returns empty array.
- Mutate one field at a time: bad name, empty compatibleGeometries, FOV out of range at sampled point, NaN in evaluate, start/end mismatch, oversize factor < 1.0, negative displacements, invalid easing, FOV outside declared fovRange → each produces the expected error.

**Validation (`validateCameraParams`):**
- `undefined` → valid.
- `{}` → valid.
- Various invalid params → correct errors.
- Valid params with all fields → valid.
- Non-finite offset → error.

### Contract Conformance Test Pattern

Each downstream preset (OBJ-026 through OBJ-034) should run a standard conformance suite. This pattern should be exported as a reusable test utility:

1. **Boundary start:** `evaluate(0)` matches `defaultStartState` within 1e-6 per component.
2. **Boundary end:** `evaluate(1)` matches `defaultEndState` within 1e-6 per component.
3. **Continuity:** Sample 100 points in [0, 1]; no NaN/Infinity in any field.
4. **FOV range:** All sampled FOV values fall within `oversizeRequirements.fovRange` (tolerance 1e-6).
5. **Determinism:** 100 calls with same `t` produce identical output.
6. **Full validation:** `validateCameraPathPreset(preset)` returns empty array.
7. **Speed scaling:** The maximum Euclidean distance between `evaluate(t, { speed: 0.5 }).position` and `defaultStartState.position` over 100 samples is strictly less than the maximum distance with default params. (Exception: static presets where both are zero.)
8. **Easing override:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in at least one position component. (Exception: static presets.)

### Relevant Testable Claims

- **TC-04** (partial): The type contract ensures LLM authors select preset names, not XYZ coordinates.
- **TC-05** (prerequisite): Tunnel camera path (OBJ-029) will conform to this contract.
- **TC-08** (partial): `compatibleGeometries` metadata enables coverage analysis.
- **TC-09** (prerequisite): Easing override in `CameraParams` enables A/B comparison.

## Integration Points

### Depends on

| Dependency | What is imported |
|---|---|
| **OBJ-002** (`src/interpolation/`) | `EasingName`, `EasingFn` types for `CameraParams.easing`, `CameraPathPreset.defaultEasing`, `ResolvedCameraParams.easing`. `getEasing()` and `isEasingName()` used by `resolveCameraParams` and `validateCameraParams`. |
| **OBJ-003** (`src/spatial/`) | `Vec3` type for positions, lookAt, offset. `CameraState` type as the output of `toCameraState()`. `DEFAULT_CAMERA` constants for `toCameraState()` defaults. |

### Consumed by

| Downstream | How it uses OBJ-006 |
|---|---|
| **OBJ-026** (`static`) | Implements `CameraPathPreset`. Zero displacement. |
| **OBJ-027** (`slow_push_forward`, `slow_pull_back`) | Implements `CameraPathPreset`. Z-axis interpolation. |
| **OBJ-028** (`lateral_track_left`, `lateral_track_right`) | Implements `CameraPathPreset`. X-axis interpolation. |
| **OBJ-029** (`tunnel_push_forward`) | Implements `CameraPathPreset`. Tunnel-specific Z push. |
| **OBJ-030** (`flyover_glide`) | Implements `CameraPathPreset`. Elevated Y + forward Z. |
| **OBJ-031** (`gentle_float`) | Implements `CameraPathPreset`. Multi-axis sinusoidal. |
| **OBJ-032** (`dramatic_push`) | Implements `CameraPathPreset`. Aggressive ease-out Z push. |
| **OBJ-033** (`crane_up`) | Implements `CameraPathPreset`. Y-axis rise. |
| **OBJ-034** (`dolly_zoom`) | Implements `CameraPathPreset`. Z + FOV animation. |
| **OBJ-040** (Edge-reveal validation) | Reads `OversizeRequirements`, accounts for speed and offset. Uses `evaluate()` for trajectory sampling. |
| **OBJ-041** (Geometry-camera compatibility) | Reads `compatibleGeometries`. Cross-references against geometry registry. |
| **OBJ-045**, **OBJ-071**, **OBJ-079** | Use registry and types. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t, params)`, applies offset, calls `toCameraState()`, sets Three.js camera. |
| **Scene sequencer** (OBJ-010) | Resolves preset names from manifest, passes `CameraParams`. |

### File Placement

```
depthkit/
  src/
    camera/
      index.ts          # Barrel export
      types.ts          # CameraFrameState, CameraParams, ResolvedCameraParams,
                        # OversizeRequirements, CameraPathEvaluator, CameraPathPreset,
                        # toCameraState(), resolveCameraParams()
      registry.ts       # CameraPathRegistry type, getCameraPath, isCameraPathName,
                        # listCameraPathNames, getCameraPathsForGeometry
      validate.ts       # validateCameraPathPreset, validateCameraParams
```

## Open Questions

1. **Should `CameraParams` support a `fovOverride` for static-FOV paths?** A manifest author might want `slow_push_forward` at 35° instead of 50°. Currently only FOV-animating presets control FOV. A simple `fovOverride?: number` in `CameraParams` would let any path use a custom static FOV. **Recommendation:** Defer to OBJ-027 implementation round. Backward-compatible addition.

2. **Should `evaluate()` receive scene duration for duration-dependent paths?** `gentle_float` (OBJ-031) might want to vary oscillation frequency based on scene length — a 5-second scene shouldn't have the same number of oscillations as a 30-second scene. **Recommendation:** Presets that need duration can accept it via `CameraParams` extension (e.g., `{ duration?: number }`). Since unrecognized params are ignored, this is backward-compatible. Defer to OBJ-031 implementation.

3. **Should there be a `CameraPathPresetFactory` for parameterized preset families?** E.g., `createPushPreset({ axis: 'z', distance: 25 })`. **Recommendation:** Defer. Preset implementations can use internal factories, but the external registry contains concrete `CameraPathPreset` instances. The type contract doesn't need to expose factories.

---

I believe this revision addresses all nine issues raised by the Challenger:

- **Issue 1** → D10 + `toCameraState()` + AC-09/AC-10
- **Issue 2** → D2 (offset applied outside evaluate, documented in CameraParams.offset docstring, OversizeRequirements notes)
- **Issue 3** → D3 + detailed CameraParams.speed docstring with per-path-type examples
- **Issue 4** → Conformance test #7 rewritten to compare max displacement over 100 samples
- **Issue 6** → D6 expanded with provisional names from seed Section 4.2, validation scope note
- **Issue 7** → D11 + `resolveCameraParams()` + `ResolvedCameraParams` + AC-11 through AC-15
- **Issue 8** → D12 + AC-35/AC-36
- **Issue 9** → `maxDisplacementZ` description simplified

I'd like the Challenger to verify and approve.

---

## Round 4 — spec_challenger

I've carefully verified the revised spec against every issue from Round 2. Let me go through them:

**Issue 1 (CameraFrameState vs CameraState):** ✅ D10 documents the relationship. `toCameraState()` added with ACs 09-10. Docstring on `CameraFrameState` is explicit.

**Issue 2 (Offset inside/outside evaluate):** ✅ D2 clearly says offset is outside. `ResolvedCameraParams` excludes offset. OversizeRequirements notes mention OBJ-040 accounting for offset.

**Issue 3 (Speed semantics):** ✅ D3 is precise. Per-path-type examples in the docstring.

**Issue 4 (Speed conformance test):** ✅ Test #7 now uses max displacement over 100 samples.

**Issue 6 (Provisional geometry names):** ✅ Expanded with seed Section 4.2 names and validation scope note.

**Issue 7 (Boilerplate):** ✅ `resolveCameraParams()` + `ResolvedCameraParams` with ACs 11-15.

**Issue 8 (Isomorphism):** ✅ D12 + AC-35/AC-36.

**Issue 9 (maxDisplacementZ):** ✅ Simplified.

---

**One minor inconsistency to fix in the final write:**

`resolveCameraParams` docstring says `@throws {Error} if speed <= 0, easing is invalid, or offset is non-finite.` But `ResolvedCameraParams` doesn't include offset, presets never see offset, and no AC tests offset throwing from `resolveCameraParams`. Offset validation belongs in `validateCameraParams` (pre-flight manifest check) and the renderer reads `params?.offset ?? [0,0,0]` after validation. I'll remove "or offset is non-finite" from the `resolveCameraParams` docstring in the final version.

Everything else is sound. This spec is implementable without guessing.

CONCLUSION:

The spec defines the complete TypeScript type system for camera path presets in depthkit: `CameraPathPreset` as the core type with `evaluate(t, params)`, `CameraFrameState` as the path-controlled camera state subset, `CameraParams` for manifest-level customization (speed scales amplitude, easing overrides temporal feel, offset applied externally by renderer), `OversizeRequirements` for edge-reveal metadata, a parameterized registry pattern, `toCameraState()` bridging to OBJ-003's `CameraState`, `resolveCameraParams()` eliminating preset boilerplate, and comprehensive validation utilities. 36 acceptance criteria cover type contracts, registry operations, resolution, validation, determinism, and isomorphism.

Let me write the final spec to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the final spec and update meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "content": "# Specification: OBJ-006 \u2014 Camera Path Type Contract\n\n## Summary\n\nOBJ-006 defines the TypeScript type system for camera path presets in depthkit. A camera path preset is a named, self-contained unit that maps normalized time `t \u2208 [0, 1]` to a complete camera state (`position`, `lookAt`, `fov`) and carries metadata for validation, edge-reveal prevention, and blind authoring. This is the Tier 1 contract that all downstream camera path preset implementations (OBJ-026 through OBJ-034) conform to, and that the scene sequencer (OBJ-010), edge-reveal validator (OBJ-040), and geometry-camera compatibility validator (OBJ-041) consume.\n\n## Interface Contract\n\n### Core Types\n\n```typescript\n// src/camera/types.ts\n\nimport { Vec3, CameraState } from '../spatial/types';\nimport { EasingName, EasingFn } from '../interpolation/easings';\n\n/**\n * The path-controlled subset of camera state at a single moment in time.\n * Returned by a camera path's evaluate() function.\n *\n * Relationship to CameraState (OBJ-003): CameraFrameState contains only\n * the properties that a camera PATH controls \u2014 position, lookAt, fov.\n * The complete CameraState also includes aspectRatio, near, and far,\n * which are composition-level constants (set from the manifest's\n * composition.width/height and the geometry's near/far recommendations).\n * The scene renderer constructs a full CameraState by combining\n * CameraFrameState from the path with composition-level values.\n * Use toCameraState() to perform this merge.\n */\nexport interface CameraFrameState {\n  /** Camera position in world space [x, y, z] */\n  position: Vec3;\n  /** Camera lookAt target in world space [x, y, z] */\n  lookAt: Vec3;\n  /** Vertical field of view in degrees. Must be in (0, 180). */\n  fov: number;\n}\n\n/**\n * Combines path-controlled camera state with composition-
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-006",
     3→  "description": "Camera path type contract -- TypeScript interface for camera path presets. Defines position(t) and lookAt(t) as functions of normalized time t in [0,1], start/end position and lookAt vectors, FOV animation range (fov_start, fov_end), easing defaults, compatible_geometries list, and oversizing requirements metadata. Per Section 4.3.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-002", "OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Depends on interpolation utilities (OBJ-002) for easing references and coordinate system (OBJ-003) for spatial conventions."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/meta.json",
  "content": "{\n  \"id\": \"OBJ-006\",\n  \"description\": \"Camera path type contract -- TypeScript interface for camera path presets. Defines CameraPathPreset with evaluate(t, params) => CameraFrameState, CameraParams (speed/easing/offset), OversizeRequirements, CameraPathRegistry with lookup functions, resolveCameraParams() helper, toCameraState() bridge to OBJ-003 CameraState, and validateCameraPathPreset/validateCameraParams validation utilities. Per Section 4.3.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"spec_deliberation\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T01:30:00Z\",\n  \"depends_on\": [\"OBJ-002\", \"OBJ-003\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 1 contract. Speed scales spatial amplitude (not temporal rate). Offset applied outside evaluate() by renderer. CameraFrameState is path-controlled subset of OBJ-003 CameraState. Registry parameterized for testability. Isomorphic module (Node.js + browser). 36 acceptance criteria. Provisional geometry names from seed Section 4.2 until OBJ-005 finalizes.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/meta.json has been updated successfully.
Now commit to git:
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
[Tool Result] bcaf2c5 spec(OBJ-010): Three.js page shell, build/bundle architecture, and scene renderer skeleton
dcf4d08 spec(OBJ-007): depth model — semantic slot taxonomy and override system
dc13dd4 spec(OBJ-004): Manifest schema core — Zod validation and registry contract
90a2c38 spec(OBJ-002): interpolation, easing, and spring utilities
28fe944 spec(OBJ-001): Project scaffolding and build system specification
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-006/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/transcript.md
	nodes/OBJ-002/transcript.md
	nodes/OBJ-003/transcript.md
	nodes/OBJ-004/transcript.md
	nodes/OBJ-006/output.md
	nodes/OBJ-007/transcript.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-006/output.md nodes/OBJ-006/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-006): camera path type contract \u2014 presets, registry, and validation\n\nDefines CameraPathPreset with evaluate(t, params) => CameraFrameState,\nCameraParams (speed scales amplitude, easing overrides feel, offset applied\nexternally by renderer), OversizeRequirements for edge-reveal metadata,\nparameterized CameraPathRegistry, toCameraState() bridge to OBJ-003,\nresolveCameraParams() to eliminate preset boilerplate, and validation\nutilities. 36 acceptance criteria. Isomorphic module for Node.js + browser.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-006 spec files"
}
[Tool Result] [master 04524be] spec(OBJ-006): camera path type contract — presets, registry, and validation
 2 files changed, 752 insertions(+), 4 deletions(-)
 create mode 100644 nodes/OBJ-006/output.md
The specification for OBJ-006 has been written to `nodes/OBJ-006/output.md`, the meta.json updated, and committed as `04524be`.

**Summary of the agreed specification:**

The camera path type contract defines the complete TypeScript type system for depthkit's camera path presets across 4 files in `src/camera/`:

- **`CameraPathPreset`** — the core type with `evaluate(t, params)`, static start/end states, `compatibleGeometries`, `oversizeRequirements`, `defaultEasing`, `tags`
- **`CameraFrameState`** — path-controlled subset (position, lookAt, fov) bridging to OBJ-003's `CameraState` via `toCameraState()`
- **`CameraParams`** — manifest-level customization: `speed` (amplitude scaling, not temporal), `easing` (override), `offset` (applied externally by renderer)
- **`ResolvedCameraParams`** + `resolveCameraParams()` — eliminates boilerplate across 10+ preset implementations
- **`CameraPathRegistry`** — parameterized for testability, with `getCameraPath`, `getCameraPathsForGeometry`, etc.
- **Validation utilities** — `validateCameraPathPreset` (11 checks) and `validateCameraParams` (3 checks), returning error arrays
- **Contract conformance test pattern** — 8-point reusable suite for all downstream presets

Key design decisions resolved during deliberation: offset applied outside `evaluate()` by renderer (D2), speed scales spatial amplitude not temporal rate (D3), `CameraFrameState` vs `CameraState` relationship explicitly bridged (D10), isomorphic module constraint (D12), provisional geometry names from seed until OBJ-005 finalizes (D6).
