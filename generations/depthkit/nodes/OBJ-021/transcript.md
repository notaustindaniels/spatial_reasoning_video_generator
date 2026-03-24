# Deliberation Transcript: OBJ-021

---

## Round 1 — spec_author

I'll start by reviewing the existing implementation context to understand the patterns established by the already-verified geometries.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me look at the existing verified geometry implementations to understand the established patterns.
[Tool: Glob]
  Input: {
  "pattern": "**/scenes/geometries/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-018/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-021/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-019/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-020/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md"
}
[Tool Result]      1→# Specification: Stage Scene Geometry (OBJ-018)
     2→
     3→## Summary
     4→
     5→OBJ-018 defines the **stage** scene geometry — the default, most fundamental geometry in depthkit. It represents a classic "subject in front of a background" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/stage.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The stage scene g... [truncated]
Now let me also check the camera presets that are already verified to understand what's available:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-021",
     3→  "description": "Flyover scene geometry -- large ground plane below (rotation [-PI/2,0,0]), sky plane above, optional landmark planes rising from the ground. Camera moves forward and slightly downward-looking. Aerial/bird's-eye perspective feel. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 geometry."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-006/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-026/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-027/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-031/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-027 — Push/Pull Camera Path Presets
     2→
     3→## Summary
     4→
     5→OBJ-027 defines two camera path presets — `slow_push_forward` and `slow_pull_back` — the defining camera motions for 2.5D projection. `slow_push_forward` moves the camera from z=5 toward z=-3, creating the "moving into the scene" effect where WebGL's perspective projection naturally produces foreshortening, vanishing points, and depth separation. `slow_pull_back` is the mathematical mirror: same trajectory reversed, creating a "revealing the scene" effect as the camera retreats. Both implement the `CameraPathPreset` interface from OBJ-006 and share a common internal path function, differing only in the mapping of `t=0`/`t=1` to start/end positions. One specification covers both because they are structurally identical save for direction.
     6→
     7→## Interface Contract
     8→
     9→### Exported Presets
    10→
    11→```typescript
    12→// src/camera/presets/push_pull.ts
    ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-006 — Camera Path Type Contract
     2→
     3→## Summary
     4→
     5→OBJ-006 defines the TypeScript type system for camera path presets in depthkit. A camera path preset is a named, self-contained unit that maps normalized time `t ∈ [0, 1]` to a complete camera state (`position`, `lookAt`, `fov`) and carries metadata for validation, edge-reveal prevention, and blind authoring. This is the Tier 1 contract that all downstream camera path preset implementations (OBJ-026 through OBJ-034) conform to, and that the scene sequencer (OBJ-010), edge-reveal validator (OBJ-040), and geometry-camera compatibility validator (OBJ-041) consume.
     6→
     7→## Interface Contract
     8→
     9→### Core Types
    10→
    11→```typescript
    12→// src/camera/types.ts
    13→
    14→import { Vec3, CameraState } from '../spatial/types';
    15→import { EasingName, EasingFn } from '../interpolation/easings';
    16→
    17→/**
    18→ * The path-controlled subset of camer... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": 100,
  "limit": 150
}
[Tool Result]    100→   * looks at the scene's focal point. This is intentional for
   101→   * framing adjustments (e.g., shift camera right to reframe
   102→   * the subject).
   103→   *
   104→   * Edge-reveal implication: offset displaces the frustum.
   105→   * OBJ-040 must add abs(offset[i]) to the path's displacement
   106→   * in each axis when computing required plane sizes.
   107→   *
   108→   * Default: [0, 0, 0].
   109→   */
   110→  offset?: Vec3;
   111→}
   112→
   113→/**
   114→ * Resolved and validated CameraParams, ready for preset consumption.
   115→ * Produced by resolveCameraParams(). Presets receive this, not raw CameraParams.
   116→ *
   117→ * Note: offset is NOT included here because it is applied outside
   118→ * evaluate() by the renderer. Presets only need speed and easing.
   119→ */
   120→export interface ResolvedCameraParams {
   121→  /** Guaranteed > 0. */
   122→  speed: number;
   123→  /** Resolved easing function. */
   124→  easing: EasingFn;
   125→... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-026 — Static Camera Path Preset
     2→
     3→## Summary
     4→
     5→OBJ-026 defines the `static` camera path preset — the simplest possible camera path where the camera remains at a fixed position and orientation for the entire scene duration. It implements the `CameraPathPreset` interface from OBJ-006, returns identical `CameraFrameState` for all values of `t` in `[0, 1]`, declares compatibility with all eight scene geometries, and requires zero plane oversizing since no camera motion means no edge-reveal risk. This preset serves as the baseline for all geometries and the reference implementation for the OBJ-006 contract.
     6→
     7→## Interface Contract
     8→
     9→### Preset Definition
    10→
    11→```typescript
    12→// src/camera/presets/static.ts
    13→
    14→import { CameraPathPreset } from '../types';
    15→
    16→/**
    17→ * The static camera path preset.
    18→ * Camera remains at a fixed position looking at a fixed target.
  ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-031 — Gentle Float Camera Path Preset
     2→
     3→## Summary
     4→
     5→OBJ-031 defines the `gentle_float` camera path preset — a very slow, subtle multi-axis drift that produces an almost subliminal sense of life in otherwise static scenes. It is the universal ambient preset, compatible with most scene geometries, and designed for moments where camera motion should be felt rather than noticed. The preset implements the `CameraPathPreset` interface from OBJ-006 using incommensurate sinusoidal oscillations across X, Y, and Z axes to create organic, non-repeating drift within a single scene duration.
     6→
     7→## Interface Contract
     8→
     9→### Exported Preset
    10→
    11→```typescript
    12→// src/camera/presets/gentle_float.ts
    13→
    14→import { CameraPathPreset } from '../types';
    15→
    16→/**
    17→ * The gentle_float camera path preset.
    18→ *
    19→ * Produces very slow, subtle movement across all three axes using
   ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md",
  "offset": 80,
  "limit": 60
}
[Tool Result]     80→```
    81→lookAt.x(t) = startLookAtX + lookAtAmplitudeX * sin(2π * lookAtFreqX * t + lookAtPhaseX) * lookAtEnvelope(t)
    82→lookAt.y(t) = startLookAtY + lookAtAmplitudeY * sin(2π * lookAtFreqY * t + lookAtPhaseY) * lookAtEnvelope(t)
    83→lookAt.z(t) = startLookAtZ + lookAtAmplitudeZ * sin(2π * lookAtFreqZ * t + lookAtPhaseZ) * lookAtEnvelope(t)
    84→```
    85→
    86→Where `lookAtEnvelope(t) = sin(π * t)` (always raw `t`, never eased).
    87→
    88→The lookAt amplitudes are **not scaled by `speed`** and the lookAt envelope is **not affected by `easing`**. Rationale: lookAt drift is fully independent of author-controlled parameters, preserving a minimal sense of camera life even at extreme speed/easing values (see D5).
    89→
    90→**Default LookAt Parameters:**
    91→
    92→| Parameter | X-axis | Y-axis | Z-axis |
    93→|-----------|--------|--------|--------|
    94→| Amplitude (world units) | 0.15 | 0.1 | 0.2 |
    95→| Frequency (cycles per normalized t) | 0.9 ... [truncated]
Now let me also check the OBJ-003 spatial math for key constants:
[Tool: Grep]
  Input: {
  "pattern": "DEFAULT_CAMERA|PLANE_ROTATIONS",
  "glob": "**/nodes/OBJ-003/**/*",
  "output_mode": "content",
  "-A": 3
}
[Tool Result] nodes/OBJ-003/meta.json:11:[Omitted long matching line]
nodes/OBJ-003/meta.json-12-  "status": "specified"
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/meta.json-13-}
--
nodes/OBJ-003/output.md:25:export const DEFAULT_CAMERA = {
nodes/OBJ-003/output.md-26-  fov: 50,
nodes/OBJ-003/output.md-27-  near: 0.1,
nodes/OBJ-003/output.md-28-  far: 100,
--
nodes/OBJ-003/output.md:46:export const PLANE_ROTATIONS = {
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md-47-  /** Faces camera (normal along +Z). Default orientation. */
nodes/OBJ-003/output.md-48-  FACING_CAMERA: [0, 0, 0] as Vec3,
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md-49-  /** Lies flat, faces up. For floor planes. */
--
nodes/OBJ-003/output.md:303:- [ ] **AC-08:** `PLANE_ROTATIONS.FLOOR` equals `[-Math.PI / 2, 0, 0]` exactly.
nodes/OBJ-003/output.md-304-- [ ] **AC-09:** All exported constants are `read... [truncated]
Now I have enough context. Let me check the DEFAULT_CAMERA position:

The key constants:
- `DEFAULT_CAMERA.position` = `[0, 0, 5]`, FOV = 50°
- `PLANE_ROTATIONS.FLOOR` = `[-Math.PI/2, 0, 0]`
- `PLANE_ROTATIONS.FACING_CAMERA` = `[0, 0, 0]`

Now let me reason through the flyover geometry design and propose the spec.

For flyover, the key spatial difference from stage is that the camera is **elevated** and looking **down**. The ground is a large horizontal plane below, and the camera moves forward over it. This requires a different camera start position than the default `[0, 0, 5]`.

However — looking at the verified camera presets (static, gentle_float, slow_push_forward), they all use `[0, 0, 5]` as start position. The flyover needs a dedicated camera preset (`flyover_glide`) that positions the camera higher and angled down. But `flyover_glide` is not yet defined (it would be one of OBJ-028 through OBJ-034).

The geometry itself needs to work with whatever camera presets are compatible. Let me look at what the OBJ-027 push/pull presets say about flyover compatibility — they list `flyover` in their `compatibleGeometries`. So the flyover geometry needs to work with `slow_push_forward` (camera at [0,0,5] looking at [0,0,-30]) as well as a future `flyover_glide`.

This creates an interesting design challenge: if the camera is at [0,0,5] looking at [0,0,-30] (straight ahead, not down), the ground plane at Y=-2 needs to be visible in the lower portion of the frame. Let me verify this works.

With camera at [0,0,5], lookAt [0,0,-30], FOV 50°: the camera looks straight ahead. The visible vertical range at any Z is ±(d * tan(25°)). At the ground plane position, the ground Y=-2 is 2 units below the camera's Y=0 center line. This will be visible as long as 2 < d * tan(25°) at the relevant distance. At d=10 (Z=-5): visible half-height = 10 * 0.4663 = 4.66, so Y=-2 is well within view. Good.

Now I can design the flyover geometry. The key insight: unlike the stage where the floor extends *away* from camera, the flyover's ground plane is the **primary visual element** — a vast landscape viewed from above. The "aerial" feel comes from:
1. A large ground plane positioned lower than the stage's floor
2. Landmark elements rising from the ground
3. The `flyover_glide` camera (when built) will be elevated and down-angled

Let me now write the complete specification.

---

Here is my proposed specification for OBJ-021: Flyover Scene Geometry.

---

# Specification: Flyover Scene Geometry (OBJ-021)

## Summary

OBJ-021 defines the **flyover** scene geometry — a spatial arrangement designed for aerial/bird's-eye perspective. A large ground plane lies below the camera (`FLOOR` rotation), a sky plane sits at extreme depth above, and optional landmark planes rise vertically from the ground at varying depths and lateral positions. The camera moves forward while positioned above the ground, producing an immersive "flying over terrain" effect where the ground plane undergoes strong perspective foreshortening and landmarks pass by on either side. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/flyover.ts

import type { SceneGeometry } from './types';

/**
 * The flyover scene geometry — aerial/bird's-eye perspective.
 *
 * Spatial arrangement: a large ground plane below the camera
 * (FLOOR rotation), a distant sky backdrop above, and optional
 * landmark planes rising from the ground at varying depths.
 * Camera moves forward for a "flying over terrain" effect where
 * the ground undergoes strong perspective foreshortening and
 * landmarks pass by laterally.
 *
 * The ground plane is the defining spatial element — it provides
 * the primary depth cue through perspective convergence as the
 * camera moves forward. Landmarks add lateral interest and
 * depth layering.
 *
 * Best suited for landscape, environment, and travel themes.
 * Designed primarily for 16:9 landscape orientation where
 * the wide frame emphasizes the panoramic ground coverage.
 */
export const flyoverGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'flyover'` | Matches seed Section 4.2 naming |
| `description` | `'Aerial bird\'s-eye view. Large ground plane below with perspective foreshortening, sky backdrop above, and optional landmark elements rising from the terrain. Camera glides forward for a flyover effect. Best for landscapes, travel, and environment themes.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'flyover_glide'` | Seed Section 4.3: "Camera moves forward on Z while positioned above the ground plane, looking slightly down. Bird's-eye movement." This is the geometry's signature motion. |
| `compatible_cameras` | `['static', 'flyover_glide', 'slow_push_forward', 'gentle_float']` | See D3. |
| `fog` | `{ color: '#b8c6d4', near: 20, far: 55 }` | Light blue-gray atmospheric haze. See D5. |
| `preferred_aspect` | `'landscape'` | The wide ground plane and lateral landmarks read best in 16:9. Portrait would crop the lateral coverage significantly. |

### Slot Definitions

The flyover geometry defines **6 slots** — 2 required, 4 optional. The ground and sky provide the essential spatial structure; landmarks and foreground are compositional enhancements.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9. While the `flyover_glide` camera will position the camera higher (elevated Y) and angle it downward, the geometry must also work with `slow_push_forward` (camera at `[0, 0, 5]`, lookAt `[0, 0, -30]`) and `static` (camera at `[0, 0, 5]`, lookAt `[0, 0, 0]`). The ground plane positioning is designed to be visible in the lower portion of the frame with a straight-ahead camera and to become the dominant visual element with a downward-angled camera.

Following the convention established by OBJ-018: the flyover geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `sky`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 20, -50]` | Very deep Z, raised high (Y=20) to sit above the camera and fill the upper frame. Distance from camera: 55 units at Z, much further accounting for Y offset. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane facing the camera. Not a ceiling; a distant sky backdrop. |
| `size` | `[130, 60]` | Massively oversized. At distance ~59 units (√(55²+20²) ≈ 58.5, but Z-axis distance of 55 is what matters for frustum calculations): visible area ~51.3h × 91.1w at FOV 50°. Size provides ample margin for any camera motion. |
| `required` | `true` | Without a sky, the upper frame is empty in every flyover composition. The ground fills the lower portion; the sky fills the upper. Together they establish the environment. |
| `description` | `'Sky, atmosphere, or distant horizon. Fills the upper portion of the frame above the ground plane.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Sky is opaque background. |
| `fogImmune` | `true` | Sky should remain vivid regardless of fog — it represents infinite distance, not a surface that fades. |

#### Slot: `ground`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -4, -20]` | Below camera (Y=-4), centered at Z=-20. The floor extends symmetrically in X (width) and Z (depth after rotation). Y=-4 positions the ground well below the camera's Y=0 line, making it the dominant lower-frame element when the camera looks ahead and the entire view when the camera angles down. |
| `rotation` | `[-Math.PI / 2, 0, 0]` | `PLANE_ROTATIONS.FLOOR` — lies flat, faces up. After rotation, the plane's `width` maps to X-axis coverage and `height` maps to Z-axis coverage. |
| `size` | `[60, 80]` | Width=60 covers the X-axis broadly. Height=80 (Z-axis after rotation) extends from Z=20 to Z=-60 (centered at Z=-20), providing 80 units of forward coverage. With camera push from Z=5 to Z=-3 (slow_push_forward), the ground extends well beyond the camera's travel range. For flyover_glide with deeper Z travel, the 80-unit depth provides ample runway. |
| `required` | `true` | The ground plane is the defining element of the flyover geometry. Without it, there is no "terrain" to fly over and the aerial illusion fails. |
| `description` | `'Terrain, landscape, or ground surface seen from above. The defining visual element of the flyover — undergoes strong perspective foreshortening as the camera moves forward.'` | |
| `renderOrder` | `1` | Renders above sky. |
| `transparent` | `false` | Ground is opaque. |
| `fogImmune` | `false` | Distant portions of the ground fade with atmospheric haze — enhances aerial depth perception. |

#### Slot: `landmark_far`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 1, -35]` | Deep Z, centered laterally. Y=1 positions the bottom of the plane at Y=-4 (ground level) given height=10 and center at Y=1 → bottom = 1-5 = -4. Distance from camera: 40 units at Z. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane rising from the ground. |
| `size` | `[12, 10]` | Small and distant. At distance 40: visible area ~37.3h × 66.3w. This plane is intentionally small — it's a far-off landmark (mountain, tower, distant structure), not a coverage element. |
| `required` | `false` | Optional — adds depth and visual interest at the far end. Many flyovers work with just ground and sky. |
| `description` | `'Distant landmark rising from the terrain — mountain, tower, or far-off structure. Provides depth reference at the horizon.'` | |
| `renderOrder` | `2` | Renders above ground. |
| `transparent` | `true` | Landmarks should have transparent backgrounds to blend naturally with the ground and sky behind them. |
| `fogImmune` | `false` | Distant landmarks should fade with atmospheric haze — this is a key depth cue for aerial perspective. |

#### Slot: `landmark_left`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[-10, 0, -20]` | Left of center (X=-10), mid-depth. Y=0 positions the bottom of the plane at Y=-6 (given height=12, center at Y=0 → bottom = 0-6 = -6), which extends below the ground plane (Y=-4) — the ground texture occludes the below-ground portion naturally. Distance from camera: ~27 units (accounting for X offset via Pythagorean, but Z-axis distance of 25 is what matters for frustum calcs). |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[10, 12]` | Medium-sized landmark. Tall (12) to suggest a vertical feature rising from the ground. |
| `required` | `false` | Optional — adds lateral interest. |
| `description` | `'Left-side landmark rising from the terrain — building, tree cluster, or terrain feature. Passes by on the left as the camera moves forward.'` | |
| `renderOrder` | `3` | Renders above far landmark. |
| `transparent` | `true` | Needs alpha to blend with ground/sky. |
| `fogImmune` | `false` | Mid-distance fog fading is appropriate. |

#### Slot: `landmark_right`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[10, 0, -20]` | Right of center (X=10), mirrors `landmark_left`. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[10, 12]` | Matches `landmark_left` for symmetry. |
| `required` | `false` | Optional — adds lateral interest. |
| `description` | `'Right-side landmark rising from the terrain — building, tree cluster, or terrain feature. Passes by on the right as the camera moves forward.'` | |
| `renderOrder` | `3` | Same as `landmark_left` — they don't overlap so no ordering conflict. |
| `transparent` | `true` | Needs alpha. |
| `fogImmune` | `false` | Mid-distance fog fading is appropriate. |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 2, -2]` | Very close to camera, raised slightly (Y=2) to appear as overhead passing elements (clouds, birds, particles) rather than ground-level obstacles. Distance from camera: 7 units at Z. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[20, 14]` | Oversized relative to the frustum at this distance (visible area ~6.5h × 11.6w). Foreground elements typically extend beyond the frame. |
| `required` | `false` | Optional — adds atmosphere (clouds, birds, particles) passing close to the camera. |
| `description` | `'Close foreground element — clouds, birds, particles, or atmospheric effects passing near the camera. Creates a sense of speed and altitude.'` | |
| `renderOrder` | `5` | Renders on top of everything. |
| `transparent` | `true` | Must have alpha to not occlude the view below. |
| `fogImmune` | `true` | Foreground is close to camera — fog application would look physically incorrect. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `sky` | `[0, 20, -50]` | `[0, 0, 0]` | `[130, 60]` | **yes** | no | **yes** | 0 |
| `ground` | `[0, -4, -20]` | `[-PI/2, 0, 0]` | `[60, 80]` | **yes** | no | no | 1 |
| `landmark_far` | `[0, 1, -35]` | `[0, 0, 0]` | `[12, 10]` | no | yes | no | 2 |
| `landmark_left` | `[-10, 0, -20]` | `[0, 0, 0]` | `[10, 12]` | no | yes | no | 3 |
| `landmark_right` | `[10, 0, -20]` | `[0, 0, 0]` | `[10, 12]` | no | yes | no | 3 |
| `near_fg` | `[0, 2, -2]` | `[0, 0, 0]` | `[20, 14]` | no | yes | **yes** | 5 |

### Registration Side Effect

```typescript
// src/scenes/geometries/flyover.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(flyoverGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/flyover.ts
export { flyoverGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./flyover` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: `ground` instead of `floor` — semantic distinction from the stage geometry

The stage geometry uses a slot named `floor` — a horizontal surface that functions as a room floor or ground level at the base of a scene. The flyover geometry uses `ground` instead because the semantic role is different: this is a vast terrain/landscape viewed from above, not a surface the subject stands on. The LLM author choosing between `stage` and `flyover` should immediately understand from the slot names that `floor` is "standing surface" while `ground` is "terrain below."

This follows OBJ-005's convention that geometries may define custom slot names beyond the reserved set. The reserved name `floor` has the semantic role "Horizontal ground surface" with `FLOOR` rotation — the flyover's `ground` matches this rotation but differs in scale, positioning, and purpose.

### D2: Ground at Y=-4 — deeper than stage's floor at Y=-3

The flyover's ground is positioned at Y=-4 (vs stage's floor at Y=-3). This extra unit of depth serves two purposes: (a) with the default camera at Y=0, the ground is further below the eye line, emphasizing the aerial perspective even with a straight-ahead camera; (b) it provides more clearance for landmark planes whose bottom edges should visually meet the ground surface.

The ground plane size `[60, 80]` is substantially larger than the stage's floor `[20, 40]` because the flyover's camera looks down at a broader expanse of terrain. With width=60, the ground extends ±30 units in X. With depth=80 (Z-axis after rotation), it extends from Z=20 to Z=-60, providing ample coverage for forward camera travel.

### D3: Compatible cameras — conservative initial set

The flyover geometry lists four compatible cameras:

- **`static`** (OBJ-026, verified): Universal baseline. A static aerial shot.
- **`flyover_glide`** (not yet defined): The geometry's signature motion — elevated camera gliding forward with a downward look angle. This is a forward reference; the preset will be defined in a future OBJ (likely OBJ-030 or similar). Listed here because the geometry is meaningless without its intended camera.
- **`slow_push_forward`** (OBJ-027, verified): Forward Z push from `[0,0,5]` to `[0,0,-3]`. Works because the ground plane is visible in the lower frame and undergoes foreshortening as the camera pushes forward. Not as dramatic as `flyover_glide` (no elevated perspective), but produces a valid flyover-like effect.
- **`gentle_float`** (OBJ-031, verified): Subtle ambient drift. Works universally.

Excluded:
- **`tunnel_push_forward`**: Tuned for enclosed geometry with walls on all sides — would look wrong with a wide-open flyover.
- **`lateral_track_left/right`**: Lateral tracking over terrain risks revealing ground edges on the side the camera moves toward. Potentially addable after OBJ-040 edge-reveal validation confirms safety with the ground's width=60.
- **`crane_up`**: Rising camera would move away from the ground — potentially useful but needs tuning to avoid losing the aerial feel. Deferred.
- **`dramatic_push`**: Faster forward push might work but needs edge-reveal validation at the higher speed. Deferred.

### D4: Landmarks use custom slot names, not the default taxonomy

The flyover introduces three landmark slots (`landmark_far`, `landmark_left`, `landmark_right`) that are not in the default depth taxonomy. These are geometry-specific slots per OBJ-005's D8 (slot names enforced by regex, not enum). The `landmark_` prefix groups them semantically and alphabetically.

Landmarks are positioned so their bottom edges align with or extend slightly below the ground plane's Y-position. The ground texture naturally occludes the below-ground portion, creating a clean visual join without requiring precise Y alignment from the LLM author.

### D5: Light atmospheric fog — aerial haze, not cinematic darkness

The flyover uses light blue-gray fog (`#b8c6d4`) instead of the stage's black fog (`#000000`). This simulates aerial atmospheric haze — the natural phenomenon where distant objects appear lighter and bluer when viewed from altitude. The fog settings `near: 20, far: 55` create progressive haze on distant landmarks and the far end of the ground plane, enhancing depth perception.

The `near: 20` threshold ensures the ground immediately below the camera (nearest portion at ~11 units from camera at default position) remains crisp. The `far: 55` allows the sky (at Z=-50, distance ~55) to be nearly fully fogged — which is why `sky` is `fogImmune: true`.

### D6: Sky at Y=20 — elevated to fill the upper frame

The sky plane is positioned at Y=20, much higher than the stage's sky at Y=5. With the camera at Y=0, the sky needs to be visible in the upper portion of the frame. At Y=20 and Z=-50 (distance 55 on Z-axis), the sky's Y offset of 20 units creates a viewing angle of arctan(20/55) ≈ 20°, which places it well within the upper half of the 50° FOV frustum. This ensures sky visibility even with a straight-ahead camera, and with a downward-angled `flyover_glide` camera, the sky remains visible at the top of the frame.

### D7: near_fg at Y=2 — overhead elements, not ground obstacles

Unlike the stage's `near_fg` at Y=0 (frame center for foliage/bokeh), the flyover's `near_fg` is elevated to Y=2. In an aerial context, close foreground elements are things passing overhead or at camera level — clouds, birds, particles. Positioning them above center reinforces the "high altitude" feel. The LLM author could override this to Y=-2 or below if they want ground-level passing elements.

### D8: `landmark_left` and `landmark_right` share renderOrder

Both lateral landmarks have `renderOrder: 3`. Since they're separated laterally (X=-10 and X=10), they occupy different screen regions and do not compete for draw order. If they overlapped from the camera's perspective, Z-buffer sorting would handle it correctly since they're at the same Z-depth. This follows OBJ-005's guidance that renderOrder resolves depth fighting for coplanar/nearly-coplanar planes — the landmarks are not coplanar (separated in X) so no conflict exists.

### D9: Only 2 required slots — minimum viable flyover

The flyover requires only `sky` and `ground`. A valid flyover can be authored with just two images — a ground texture and a sky backdrop. Landmarks and foreground are enhancements. This keeps the bar low for LLM authoring while allowing richer compositions with all 6 slots.

### D10: `preferred_aspect` is `landscape`

Unlike the stage geometry (`both`), the flyover is explicitly designed for landscape (16:9). The wide ground plane and lateral landmarks are the core visual appeal; in portrait (9:16), the lateral coverage shrinks dramatically and the landmarks may crowd or fall outside the frame. The geometry will still render correctly in portrait mode (seed C-04), but the SKILL.md should guide LLM authors toward landscape for this geometry.

### D11: PlaneSlot construction, not DepthSlot — follows OBJ-018 convention

Same as OBJ-018: the geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration. `DepthSlot` fields (`promptGuidance`, `expectsAlpha`) are surfaced via OBJ-007's mechanisms for SKILL.md and asset pipeline, not via geometry registration.

### D12: Explicit optional field policy — follows OBJ-018 convention

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot, following the convention established by OBJ-018 for all geometry implementations.

## Acceptance Criteria

- [ ] **AC-01:** `flyoverGeometry.name` is `'flyover'`.
- [ ] **AC-02:** `flyoverGeometry.slots` contains exactly 6 keys: `sky`, `ground`, `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `sky`, `ground` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `flyoverGeometry.default_camera` is `'flyover_glide'`.
- [ ] **AC-05:** `flyoverGeometry.default_camera` appears in `flyoverGeometry.compatible_cameras`.
- [ ] **AC-06:** `flyoverGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (the two verified camera presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `flyoverGeometry.compatible_cameras` includes `'slow_push_forward'` (verified OBJ-027).
- [ ] **AC-08:** `flyoverGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'`.
- [ ] **AC-09:** `flyoverGeometry.fog` is `{ color: '#b8c6d4', near: 20, far: 55 }`.
- [ ] **AC-10:** `flyoverGeometry.description` is non-empty and describes an aerial/bird's-eye perspective.
- [ ] **AC-11:** `flyoverGeometry.preferred_aspect` is `'landscape'`.
- [ ] **AC-12:** The `ground` slot uses `PLANE_ROTATIONS.FLOOR` (`[-Math.PI/2, 0, 0]`) as its rotation.
- [ ] **AC-13:** All non-ground slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-14:** `landmark_far`, `landmark_left`, `landmark_right`, and `near_fg` have `transparent: true`. `sky` and `ground` have `transparent: false`.
- [ ] **AC-15:** `sky` and `near_fg` have `fogImmune: true`. All other slots have `fogImmune: false`.
- [ ] **AC-16:** `renderOrder` values are non-decreasing from sky (0) to near_fg (5), with `landmark_left` and `landmark_right` sharing the same renderOrder (3).
- [ ] **AC-17:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-18:** `registerGeometry(flyoverGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-19:** All slot `description` fields are non-empty strings.
- [ ] **AC-20:** All slot `size` components are positive (> 0).
- [ ] **AC-21:** For the `sky` slot (coverage plane, distance ~55 on Z-axis from camera at Z=5): size width (130) >= frustum visible width at distance 55, size height (60) >= frustum visible height at distance 55 with FOV=50° and aspect 16:9. (visible ~51.3h × 91.1w)
- [ ] **AC-22:** For the `near_fg` slot (coverage plane, distance ~7 on Z-axis from camera at Z=5): size width (20) >= frustum visible width at distance 7, size height (14) >= frustum visible height at distance 7. (visible ~6.5h × 11.6w)
- [ ] **AC-23:** The `ground` slot and landmark slots are exempt from direct frustum-dimension comparison — `ground` due to rotated orientation (validated by OBJ-040) and landmarks because they are focal elements, not coverage planes.
- [ ] **AC-24:** Slot Z-positions decrease (go more negative) as depth increases: `near_fg` (-2) > `subject-area landmarks` (-20) > `landmark_far` (-35) > `sky` (-50). `ground` center is at Z=-20.
- [ ] **AC-25:** The module self-registers via `registerGeometry(flyoverGeometry)` as a side effect of import.
- [ ] **AC-26:** The module exports `flyoverGeometry` as a named export.
- [ ] **AC-27:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants (`PLANE_ROTATIONS`).
- [ ] **AC-28:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-29:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-30:** The `ground` slot Y-position (-4) is below the `landmark_left` and `landmark_right` Y-positions (0), ensuring landmarks appear to rise above the ground.

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`sky`, `ground`) | Valid scene. Optional slots absent — minimal flyover with just terrain and sky. No landmarks, no foreground. |
| Manifest provides all 6 slots | Valid scene. Full depth layering with landmarks and atmosphere. |
| Manifest provides `landmark_left` but not `landmark_right` | Valid. Asymmetric composition. The right side shows only ground and sky. |
| Manifest provides `landmark_right` but not `landmark_left` | Valid. Asymmetric composition. Mirror of above. |
| Manifest provides `landmark_far` without lateral landmarks | Valid. Single distant focal point over terrain. |
| Manifest uses `floor` instead of `ground` | Rejected by manifest validation (OBJ-017) — the flyover uses `ground`, not `floor`. Error message lists valid slot names. |
| Manifest uses `subject` (not a flyover slot) | Rejected — `subject` is not in the flyover's slot set. |
| Camera pushes forward far enough that ground's far edge becomes visible | Ground depth extent is 80 units (Z range approximately +20 to -60). With `slow_push_forward` traveling 8 units (Z=5 to Z=-3), the far edge is at Z=-60, 57 units ahead of the camera's closest position — safely invisible. For `flyover_glide` with potentially deeper travel, OBJ-040 validates. |
| Ground edge visible on sides during lateral camera motion | Ground width is 60 units (±30 in X). With `gentle_float`'s max X displacement of 0.3 units, lateral edge reveal is impossible. Lateral track cameras are excluded from compatible list for this reason. |
| Portrait mode (9:16) | Geometry renders correctly. The narrower width shows less ground laterally but the core effect (forward motion over terrain) still works. Landmarks at X=±10 may be partially or fully outside the frame — this is acceptable since they're optional. `preferred_aspect: 'landscape'` guides the LLM away from this. |
| Landmark bottom edge below ground Y-position | By design. `landmark_left` and `landmark_right` at Y=0 with height 12 have bottom edges at Y=-6, below ground at Y=-4. The ground texture visually occludes the below-ground portion. No rendering error occurs — Three.js Z-buffer handles the occlusion. |
| Sky plane fully obscured by fog | Cannot happen — `sky` is `fogImmune: true`. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `flyover.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'flyover' is already registered." Module should rely on Node.js module caching (single execution). |
| `flyover.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'flyover': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `flyoverGeometry.name` is `'flyover'`.
2. `flyoverGeometry.slots` has exactly 6 keys: `sky`, `ground`, `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.
3. Required slots: `sky`, `ground`. Optional: `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'flyover_glide'` and is in `compatible_cameras`.
6. `compatible_cameras` is non-empty, all entries match `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` matches hex pattern `#b8c6d4`.
8. `description` is non-empty.
9. `preferred_aspect` is `'landscape'`.

**Slot spatial correctness tests:**
10. `ground` slot rotation matches `PLANE_ROTATIONS.FLOOR` exactly (`[-Math.PI/2, 0, 0]`).
11. All non-ground slots have rotation `[0, 0, 0]`.
12. Z-positions are ordered from nearest to deepest: `near_fg` (-2) > landmarks (-20/-35) > `sky` (-50).
13. `renderOrder` values are non-decreasing: sky (0) <= ground (1) <= landmark_far (2) <= landmark_left (3) = landmark_right (3) <= near_fg (5).
14. All `size` components are > 0.
15. `ground` Y-position (-4) is below lateral landmark Y-positions (0).

**Slot metadata tests:**
16. `landmark_far`, `landmark_left`, `landmark_right`, `near_fg` have `transparent: true`.
17. `sky`, `ground` have `transparent: false`.
18. `sky`, `near_fg` have `fogImmune: true`.
19. `ground`, `landmark_far`, `landmark_left`, `landmark_right` have `fogImmune: false`.
20. All slot `description` fields are non-empty.
21. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
22. `validateGeometryDefinition(flyoverGeometry)` returns an empty error array.
23. `registerGeometry(flyoverGeometry)` does not throw (when registry is not locked).
24. After registration, `getGeometry('flyover')` returns the flyover geometry.

**Frustum size validation tests:**
25. For `sky` (coverage, Z-distance 55 from camera): size [130, 60] >= visible area at distance 55 with FOV=50° and 16:9 aspect (~91.1w × 51.3h). ✓
26. For `near_fg` (coverage, Z-distance 7 from camera): size [20, 14] >= visible area at distance 7 (~11.6w × 6.5h). ✓
27. `ground`: exempt from direct frustum comparison (rotated plane).
28. Landmark slots: exempt (focal elements, not coverage planes).

**Compatible cameras tests:**
29. `compatible_cameras` includes `'static'`, `'flyover_glide'`, `'slow_push_forward'`, `'gentle_float'`.
30. `compatible_cameras` does NOT include `'tunnel_push_forward'`.

**Symmetry tests:**
31. `landmark_left.position[0]` is the negation of `landmark_right.position[0]` (lateral symmetry).
32. `landmark_left.size` equals `landmark_right.size`.
33. `landmark_left.renderOrder` equals `landmark_right.renderOrder`.

### Relevant Testable Claims

- **TC-01** (partial): The flyover geometry uses 6 slots (2 required, 4 optional), within the 3-5 effective range for most compositions (ground + sky = 2, add landmarks for 4-5).
- **TC-04** (partial): The geometry defines all spatial relationships. An LLM specifies `geometry: 'flyover'` and maps images to slot names. No XYZ coordinates needed.
- **TC-08** (partial): The flyover is one of the 8 proposed geometries. Covers aerial/landscape/travel themes that the stage geometry cannot convey.

## Integration Points

### Depends on

| Upstream | What OBJ-021 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types for the geometry definition. `registerGeometry` function for self-registration. `validateGeometryDefinition` (used indirectly — `registerGeometry` calls it). |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`, `isValidSlotName`). `DEFAULT_SLOT_TAXONOMY` for reference (consulted for `near_fg` sizing, but the flyover constructs its own slot values). |
| **OBJ-003** (Spatial math) | `PLANE_ROTATIONS.FLOOR` constant for the ground slot rotation. `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. |

### Consumed by

| Downstream | How it uses OBJ-021 |
|------------|---------------------|
| **OBJ-062** (Flyover visual tuning) | The Director Agent reviews test renders of the flyover geometry and provides feedback on ground scale, landmark positioning, fog color/density, and camera compatibility. OBJ-062 may adjust numerical values in the slot definitions. |
| **OBJ-070** (End-to-end scene render test) | May use the flyover geometry as one of the test geometries in an end-to-end render pipeline test. |
| **OBJ-071** (SKILL.md) | Documents the flyover geometry — slot names, descriptions, and usage guidance. |
| **OBJ-017** (Manifest structural validation) | After registration, manifest validation looks up `getGeometry('flyover')` and validates that a manifest's `planes` keys match the flyover's slot names. |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('flyover')` to resolve slot spatial data when rendering a scene with `geometry: 'flyover'`. |
| **OBJ-039** (Page-side renderer) | Reads slot `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune` to create Three.js meshes. |
| **OBJ-040** (Edge-reveal validation) | Validates that compatible camera paths don't reveal ground edges or landmark clipping issues. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        flyover.ts        # flyoverGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./flyover
```

## Open Questions

### OQ-A: Should the ground plane be even larger?

The ground size `[60, 80]` provides generous coverage for the verified camera presets. When `flyover_glide` is defined (likely with deeper Z travel and a downward look angle), the ground may need to be larger — potentially `[80, 120]`. The current size is conservative for the known camera presets; OBJ-062 (visual tuning) will validate and adjust.

**Recommendation:** Keep the current size. OBJ-062 tuning will adjust if needed when `flyover_glide` is defined.

### OQ-B: Should there be a `landmark_center` slot in addition to far/left/right?

A central midground landmark (closer than `landmark_far` but centered) could add depth. However, a centered landmark at mid-depth could occlude `landmark_far` from many camera angles. Keeping the center clear with far landmark at deep Z creates a stronger vanishing-point depth cue.

**Recommendation:** Defer. If needed, the LLM can use `landmark_far` (which is centered) for a midground element by overriding its position via `PlaneOverride`.

### OQ-C: Should the fog color be configurable per-slot or only per-geometry?

The current atmospheric blue-gray fog color works well for outdoor aerial scenes. However, a flyover of a volcanic landscape might want orange-red haze, and a flyover of a snowy tundra might want white fog. The manifest's per-scene fog override (per OBJ-005's fog contract) handles this — the LLM can override `fog.color` in the manifest without changing the geometry definition.

**Recommendation:** No change needed. The geometry's fog settings are defaults; manifest overrides handle per-scene variation.

### OQ-D: How will `flyover_glide` camera interact with this geometry?

The `flyover_glide` camera preset is not yet defined. It will likely position the camera at elevated Y (e.g., [0, 8, 5]) with a downward lookAt target (e.g., [0, -2, -20]). This dramatically changes the frustum's intersection with the ground plane, potentially requiring ground size adjustments. The compatible_cameras list includes `flyover_glide` as a forward reference — when that preset is specified, its OversizeRequirements will be used by OBJ-040 to validate the ground plane size.

**Recommendation:** Document the forward reference. The flyover geometry and `flyover_glide` preset must be co-tuned during OBJ-062.

---

I believe this spec is complete. It follows the patterns established by the verified OBJ-018 (stage geometry) — same structure, same conventions for PlaneSlot construction, explicit optional fields, and comparable depth of spatial reasoning. The key differentiators are the elevated ground plane, atmospheric fog, landmark system, and landscape-preferred aspect ratio.

I'd like the Challenger to review and verify. Key areas I'd particularly welcome scrutiny on:
1. The ground plane size and position — is Y=-4 and `[60, 80]` appropriate?
2. The landmark positioning — do the Y values create a clean visual join with the ground?
3. The compatible cameras list — is `slow_push_forward` truly compatible with this geometry, given it looks straight ahead rather than down?
4. The fog color choice — is `#b8c6d4` a good default for atmospheric haze?

---

## Round 2 — spec_challenger


[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md"
}
[Tool Result]      1→# Specification: Stage Scene Geometry (OBJ-018)
     2→
     3→## Summary
     4→
     5→OBJ-018 defines the **stage** scene geometry — the default, most fundamental geometry in depthkit. It represents a classic "subject in front of a background" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/stage.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The stage scene g... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md"
}
[Tool Error] File content (11307 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": "0",
  "limit": "100"
}
[Tool Result]      0→# Specification: OBJ-006 — Camera Path Type Contract
     1→
     2→## Summary
     3→
     4→OBJ-006 defines the TypeScript type system for camera path presets in depthkit. A camera path preset is a named, self-contained unit that maps normalized time `t ∈ [0, 1]` to a complete camera state (`position`, `lookAt`, `fov`) and carries metadata for validation, edge-reveal prevention, and blind authoring. This is the Tier 1 contract that all downstream camera path preset implementations (OBJ-026 through OBJ-034) conform to, and that the scene sequencer (OBJ-010), edge-reveal validator (OBJ-040), and geometry-camera compatibility validator (OBJ-041) consume.
     5→
     6→## Interface Contract
     7→
     8→### Core Types
     9→
    10→```typescript
    11→// src/camera/types.ts
    12→
    13→import { Vec3, CameraState } from '../spatial/types';
    14→import { EasingName, EasingFn } from '../interpolation/easings';
    15→
    16→/**
    17→ * The path-controlled subset of camer... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "compatible_geometries|compatibleGeometries|OversizeRequirements|oversizeRequirements",
  "glob": "**/nodes/OBJ-006/output.md",
  "output_mode": "content"
}
[Tool Result] nodes/OBJ-006/output.md:155:export interface OversizeRequirements {
nodes/OBJ-006/output.md:271:  compatibleGeometries: readonly string[];
nodes/OBJ-006/output.md:277:  oversizeRequirements: OversizeRequirements;
nodes/OBJ-006/output.md:361: * 5. oversizeRequirements.recommendedOversizeFactor >= 1.0.
nodes/OBJ-006/output.md:362: * 6. oversizeRequirements.fovRange[0] <= fovRange[1], both in (0, 180).
nodes/OBJ-006/output.md:363: * 7. oversizeRequirements displacement values are >= 0.
nodes/OBJ-006/output.md:365: * 9. compatibleGeometries is non-empty.
nodes/OBJ-006/output.md:368: * 11. All sampled FOV values fall within oversizeRequirements.fovRange (tolerance 1e-6).
nodes/OBJ-006/output.md:401:  OversizeRequirements,
nodes/OBJ-006/output.md:434:**Trade-off:** Callers cannot introspect the trajectory without sampling. Mitigated by `defaultStartState`, `defaultEndState`, and `oversizeRequirements` as static metadata.
nodes/OBJ-006/output.md:462:### D4: OversizeRequirements as structured ... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "compatible_geometries|compatibleGeometries|flyover",
  "glob": "**/nodes/OBJ-027/output.md",
  "output_mode": "content"
}
[Tool Result] nodes/OBJ-027/output.md:62:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | All geometries where forward Z motion is meaningful. Excludes `panorama` (rotation-based). See D4. |
nodes/OBJ-027/output.md:78:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | Same as push_forward. |
nodes/OBJ-027/output.md:217:**Decision:** Both presets exclude `panorama` from `compatibleGeometries`.
nodes/OBJ-027/output.md:301:- [ ] **AC-32:** Both presets have `compatibleGeometries` containing exactly `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` — 7 entries, excluding `panorama`.
nodes/OBJ-027/output.md:434:| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatibleGeometries` — 7 of 8 geometries (all except panorama). |

[Tool: Grep]
  Input: {
  "pattern": "oversizeRequirements|maxDisplacement|fovRange",
  "glob": "**/nodes/OBJ-027/output.md",
  "output_mode": "content"
}
[Tool Result] nodes/OBJ-027/output.md:85:| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
nodes/OBJ-027/output.md:86:| `maxDisplacementY` | `0` | No vertical displacement. |
nodes/OBJ-027/output.md:87:| `maxDisplacementZ` | `8` | Total Z travel: z=5 to z=-3 = 8 world units at speed=1.0. |
nodes/OBJ-027/output.md:88:| `fovRange` | `[50, 50]` | FOV is constant. |
nodes/OBJ-027/output.md:95:| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
nodes/OBJ-027/output.md:96:| `maxDisplacementY` | `0` | No vertical displacement. |
nodes/OBJ-027/output.md:97:| `maxDisplacementZ` | `8` | Total Z travel: z=-3 to z=5 = 8 world units at speed=1.0. |
nodes/OBJ-027/output.md:98:| `fovRange` | `[50, 50]` | FOV is constant. |
nodes/OBJ-027/output.md:307:- [ ] **AC-35:** `slowPushForward.oversizeRequirements.maxDisplacementX === 0`.
nodes/OBJ-027/output.md:308:- [ ] **AC-36:** `slowPushForward.oversizeRequirements.maxDisplacementY === 0`.
nodes/OBJ-027/output.md:309:- ... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "oversizeRequirements|maxDisplacement|fovRange",
  "glob": "**/nodes/OBJ-031/output.md",
  "output_mode": "content"
}
[Tool Result] nodes/OBJ-031/output.md:146:  oversizeRequirements: {
nodes/OBJ-031/output.md:147:    maxDisplacementX: 0.3,   // amplitude_X at speed=1.0
nodes/OBJ-031/output.md:148:    maxDisplacementY: 0.2,   // amplitude_Y at speed=1.0
nodes/OBJ-031/output.md:149:    maxDisplacementZ: 0.4,   // amplitude_Z at speed=1.0
nodes/OBJ-031/output.md:150:    fovRange: [50, 50],      // No FOV animation
nodes/OBJ-031/output.md:204:[Omitted long matching line]
nodes/OBJ-031/output.md:278:- [ ] **AC-21:** `oversizeRequirements.maxDisplacementX` equals 0.3.
nodes/OBJ-031/output.md:279:- [ ] **AC-22:** `oversizeRequirements.maxDisplacementY` equals 0.2.
nodes/OBJ-031/output.md:280:- [ ] **AC-23:** `oversizeRequirements.maxDisplacementZ` equals 0.4.
nodes/OBJ-031/output.md:281:- [ ] **AC-24:** `oversizeRequirements.fovRange` equals `[50, 50]`.
nodes/OBJ-031/output.md:282:- [ ] **AC-25:** `oversizeRequirements.recommendedOversizeFactor` equals 1.05.
nodes/OBJ-031/output.md:340:- Verify all static fields (name, t... [truncated]
Now let me check what OBJ-027's `slow_push_forward` camera actually does — specifically its start/end positions and compatibility with flyover:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "offset": "30",
  "limit": "80"
}
[Tool Result]     30→ * decelerates. Linear easing feels robotic; ease_in_out feels
    31→ * like a dolly on a track.
    32→ */
    33→export const slowPushForward: CameraPathPreset;
    34→
    35→/**
    36→ * slow_pull_back — Mathematical mirror of slow_push_forward.
    37→ * Camera starts at z=-3 and retreats to z=5.
    38→ * lookAt remains fixed at [0, 0, -30].
    39→ * FOV is static at 50°.
    40→ *
    41→ * Creates a "scene reveal" — the viewer begins close to the
    42→ * subject/environment and gradually pulls back to reveal the
    43→ * full spatial arrangement. Effective for opening shots and
    44→ * establishing context after a close-up.
    45→ */
    46→export const slowPullBack: CameraPathPreset;
    47→```
    48→
    49→### Preset Values — `slow_push_forward`
    50→
    51→| Field | Value | Rationale |
    52→|-------|-------|-----------|
    53→| `name` | `'slow_push_forward'` | Seed Section 4.3 naming |
    54→| `description` | `'Camera pushes forward along the Z axis ... [truncated]
Good. Now I have a thorough understanding of the patterns. Let me formulate my critique.

---

I've reviewed the proposed spec thoroughly against the seed, dependency specs (OBJ-005, OBJ-007, OBJ-003), and the reference implementation (OBJ-018). Here's my assessment:

## What's Sound

1. **Structure and conventions**: Follows OBJ-018's format closely — slot tables, design decisions, registration pattern, barrel export. Good.
2. **Slot naming**: `ground`, `landmark_far`, `landmark_left`, `landmark_right`, `near_fg` all match `/^[a-z][a-z0-9_]*$/`. `ground` instead of `floor` is a reasonable semantic distinction (D1).
3. **Rotation assignments**: Ground uses `PLANE_ROTATIONS.FLOOR`, all others `FACING_CAMERA`. Correct.
4. **fogImmune/transparent assignments**: Logically consistent.
5. **Registration side effect pattern**: Matches OBJ-018.
6. **Required/optional split**: 2 required (sky, ground) is reasonable for a minimal flyover.

## Issues

### Issue 1: `slow_push_forward` compatibility is dubious — spec acknowledges it but doesn't validate it (Major)

The spec says `slow_push_forward` is compatible, and D3 argues the ground at Y=-4 is visible in the lower frame with a straight-ahead camera at Y=0. Let me verify.

Camera at `[0, 0, 5]`, lookAt `[0, 0, -30]`. The camera looks straight ahead along -Z. The vertical frustum half-angle is 25° (FOV/2). The bottom of the visible frame at the ground's Z-center (-20) is at distance 25 on Z, so:

- Visible bottom at Z=-20: `y_bottom = 0 - 25 * tan(25°) ≈ -11.66`

The ground is at Y=-4. So yes, the ground plane is **well within** the visible frame — it occupies roughly the bottom 1/3 of the frame at that depth. That math checks out.

However, the `slow_push_forward` camera moves from `[0,0,5]` to `[0,0,-3]`, still looking at `[0,0,-30]`. At the end position, the ground's nearest visible portion is at Z ≈ -3 + some near distance. The ground plane center is at Z=-20 with the plane extending (after rotation) from roughly Z=+20 to Z=-60. The camera at Z=-3 is inside the ground plane's Z-extent — this works, the floor extends behind and ahead.

**Verdict**: Actually fine. I'll withdraw this as a concern after checking the math. But the spec's validation reasoning in the slot definition is thin — it hand-waves "visible in the lower portion of the frame" without showing the math I just did. 

**Fix**: Add a brief calculation note in the ground slot or D2 showing that at distance 25 (from camera Z=5 to ground Z=-20), `y_bottom = -11.66`, and ground at Y=-4 is comfortably within the frustum.

**Severity**: Minor.

### Issue 2: `slow_pull_back` is NOT in `compatible_cameras` but OBJ-027 lists `flyover` as compatible (Major)

OBJ-027's `slow_pull_back` preset has `compatibleGeometries: ['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']`. But OBJ-021's `compatible_cameras` is `['static', 'flyover_glide', 'slow_push_forward', 'gentle_float']` — no `slow_pull_back`.

This creates a **cross-reference inconsistency**: the camera says it's compatible with `flyover`, but the geometry doesn't say it's compatible with the camera. OBJ-041 (geometry-camera compatibility validator) cross-references both. Who's right?

**Fix**: Either add `'slow_pull_back'` to `compatible_cameras` (it works the same geometry — just reversed), or document why it's excluded and note that OBJ-027 should update its `compatibleGeometries` to exclude `flyover` for `slow_pull_back`. Given that pull_back starts at Z=-3 and retreats to Z=5, the flyover ground should be equally visible, so adding it seems correct.

**Severity**: Major — produces a validation contradiction at OBJ-041.

### Issue 3: `flyover_glide` is undefined — forward reference risk (Major)

The `default_camera` is `'flyover_glide'`, which doesn't exist yet. If someone registers and reads this geometry before `flyover_glide` is defined, `validateGeometryDefinition()` won't catch this (OBJ-005's validator only checks structural validity of the geometry, not that camera names actually exist in the camera registry — that's OBJ-041's job).

But this means: **if someone writes a manifest using `geometry: 'flyover'` and omits the `camera` field, the engine will try to use `flyover_glide` as the default, and it won't exist.** This is a runtime failure.

OBJ-018 has the same pattern (listing forward-reference cameras), BUT its `default_camera` is `'slow_push_forward'` which is **verified** (OBJ-027). The flyover's default points to something that may not exist for a long time.

**Fix**: Change `default_camera` to `'slow_push_forward'` (verified, and already in the compatible list). Keep `flyover_glide` in `compatible_cameras` as a forward reference. Document that `default_camera` should be changed to `'flyover_glide'` once that preset is defined and verified. This follows the principle that verified presets are safer defaults.

**Severity**: Major — a manifest with `geometry: 'flyover'` and no explicit camera would fail at runtime until `flyover_glide` is implemented.

### Issue 4: Missing `OversizeRequirements` cross-validation for ground plane (Minor)

The spec says ground size `[60, 80]` is sufficient for `slow_push_forward` (8 units of Z displacement). But it doesn't verify the ground's **X-axis coverage** against the frustum at the camera's closest approach.

With camera at Z=-3 (end of push_forward), looking at Z=-30, the nearest edge of the ground is where the frustum's bottom intersects the ground plane at Y=-4. The ground extends ±30 in X. At the camera's closest approach to the ground (nearest point where the ground is visible), the visible width depends on the ground's Y-position relative to the frustum. This is complex geometry (rotated plane intersection), and the spec correctly defers to OBJ-040 for edge-reveal validation. But it should **explicitly** note this deferral.

**Fix**: Already addressed in AC-23 which exempts ground from direct frustum comparison. This is fine. Withdrawn.

### Issue 5: Landmark Y-position and ground occlusion claim needs precision (Minor)

D4 says: "Landmarks are positioned so their bottom edges align with or extend slightly below the ground plane's Y-position. The ground texture naturally occludes the below-ground portion."

For `landmark_left`: position Y=0, size height=12. Bottom edge at Y = 0 - 12/2 = -6. Ground at Y=-4.

But the ground plane is rotated (lies flat). Its visible surface IS at Y=-4 — it doesn't "occlude" things below Y=-4 in the traditional sense. What actually happens: the ground texture is rendered at Y=-4 as a horizontal plane. The landmark's below-ground portion (Y=-6 to Y=-4) would be visible behind/through the ground only if the camera looks from below. With the camera at Y=0 looking straight ahead, the ground plane will Z-buffer occlude the landmark's below-ground portion **only if the ground is between the camera and that portion of the landmark in screen space**.

Actually: the ground plane extends in X and Z at Y=-4. The landmark at X=-10, Z=-20 has its bottom at Y=-6. From a camera at [0,0,5], the ground at Z=-20 is at Y=-4. The landmark bottom at Y=-6 is below the ground. Z-buffer will render whichever is closer to camera — at Z=-20, both the ground and landmark are at the same Z, but the ground is at Y=-4 and the landmark extends to Y=-6. The camera ray from [0,0,5] passing through the ground at Z=-20, Y=-4 hits the ground first (Y=-4), then the landmark extends below (Y=-6). The ground is an opaque plane, so it will occlude the landmark below Y=-4.

Wait — no. The ground is a horizontal plane at Y=-4. A camera ray going downward to hit Y=-6 would first hit the ground plane at Y=-4 (same Z). The Z-buffer would show the ground (closer to camera along the viewing ray in terms of screen-space depth). So yes, occlusion works, but only because the ground is opaque and the camera is above Y=-4.

**Fix**: The spec's claim is correct but imprecise. Add a sentence: "The Z-buffer handles occlusion naturally: camera rays reaching below Y=-4 at the landmark's Z-depth hit the ground plane first, since the ground's opaque material renders at a nearer screen-space depth." Or simply note that this only works when the camera is above Y=-4 (which is always true for all compatible cameras).

**Severity**: Minor — the claim is correct, just imprecisely stated.

### Issue 6: `near_fg` renderOrder jumps from 3 to 5 — gap at 4 (Minor)

OBJ-018's stage uses renderOrder 0-4 with strict sequential ordering. The flyover uses 0, 1, 2, 3, 3, 5 — skipping 4. This isn't technically wrong (Three.js accepts any number), but it's inconsistent with OBJ-018's pattern and raises the question: why skip 4?

**Fix**: Either use 4 for `near_fg` (matching sequential pattern) or add a rationale for the gap. If the gap is intentional to leave room for future slots between landmarks and near_fg, say so.

**Severity**: Minor.

### Issue 7: No `DepthSlot` / `promptGuidance` mapping for geometry-specific slots (Observation)

The flyover introduces custom slots (`ground`, `landmark_far`, `landmark_left`, `landmark_right`) that are not in `DEFAULT_SLOT_TAXONOMY`. OBJ-007 provides `promptGuidance` and `expectsAlpha` via `DepthSlot`, but only for the 5 default taxonomy slots. How do downstream consumers (OBJ-071 SKILL.md, OBJ-053 prompt templates) get prompt guidance for `ground` and the landmarks?

OBJ-018's D11 says `promptGuidance` and `expectsAlpha` are "surfaced via OBJ-007's `DEFAULT_SLOT_TAXONOMY`" — but the stage uses `backdrop` (not in the default taxonomy either). So this gap exists for OBJ-018 too.

**Fix**: This is a cross-cutting concern, not something OBJ-021 should solve. But the spec should **acknowledge** that prompt guidance for geometry-specific slots (`ground`, `landmark_*`) must be provided by a mechanism outside OBJ-007's `DEFAULT_SLOT_TAXONOMY`, and note that OBJ-071 (SKILL.md) will need to source this from the `PlaneSlot.description` fields or a separate lookup. OBJ-018 already has this gap without acknowledging it — OBJ-021 should at least document the limitation.

**Severity**: Minor — already an established gap from OBJ-018, but should be documented.

### Issue 8: No mention of `slow_pull_back` compatibility despite OBJ-027 listing flyover (Major — duplicate of Issue 2)

Already covered above.

---

## Summary of Required Fixes

| # | Severity | Issue | Proposed Fix |
|---|----------|-------|-------------|
| 2 | **Major** | `slow_pull_back` missing from `compatible_cameras` despite OBJ-027 listing `flyover` | Add `'slow_pull_back'` to `compatible_cameras`, or document exclusion and flag OBJ-027 inconsistency |
| 3 | **Major** | `default_camera: 'flyover_glide'` points to non-existent preset | Change `default_camera` to `'slow_push_forward'` (verified). Keep `flyover_glide` in compatible list as forward ref. |
| 1 | Minor | Ground visibility math not shown | Add brief frustum math for ground visibility |
| 5 | Minor | Landmark/ground occlusion claim imprecise | Add camera-above-ground precondition note |
| 6 | Minor | renderOrder gap (3→5, skipping 4) | Use 4 for near_fg or explain the gap |
| 7 | Minor | No prompt guidance path for custom slots | Acknowledge the gap and reference OBJ-071 |

I need the two major issues resolved before convergence. The minor issues I'd accept as open questions if the Author pushes back, but I prefer they're addressed.

---

## Round 3 — spec_author

All six issues are valid. Here's the revised spec with every concern addressed:

---

# Specification: Flyover Scene Geometry (OBJ-021)

## Summary

OBJ-021 defines the **flyover** scene geometry — a spatial arrangement designed for aerial/bird's-eye perspective. A large ground plane lies below the camera (`FLOOR` rotation), a sky plane sits at extreme depth above, and optional landmark planes rise vertically from the ground at varying depths and lateral positions. The camera moves forward while positioned above the ground, producing an immersive "flying over terrain" effect where the ground plane undergoes strong perspective foreshortening and landmarks pass by on either side. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/flyover.ts

import type { SceneGeometry } from './types';

/**
 * The flyover scene geometry — aerial/bird's-eye perspective.
 *
 * Spatial arrangement: a large ground plane below the camera
 * (FLOOR rotation), a distant sky backdrop above, and optional
 * landmark planes rising from the ground at varying depths.
 * Camera moves forward for a "flying over terrain" effect where
 * the ground undergoes strong perspective foreshortening and
 * landmarks pass by laterally.
 *
 * The ground plane is the defining spatial element — it provides
 * the primary depth cue through perspective convergence as the
 * camera moves forward. Landmarks add lateral interest and
 * depth layering.
 *
 * Best suited for landscape, environment, and travel themes.
 * Designed primarily for 16:9 landscape orientation where
 * the wide frame emphasizes the panoramic ground coverage.
 */
export const flyoverGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'flyover'` | Matches seed Section 4.2 naming |
| `description` | `'Aerial bird\'s-eye view. Large ground plane below with perspective foreshortening, sky backdrop above, and optional landmark elements rising from the terrain. Camera glides forward for a flyover effect. Best for landscapes, travel, and environment themes.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'slow_push_forward'` | The only verified forward-motion camera preset (OBJ-027). Produces a valid flyover-like effect with ground foreshortening. When `flyover_glide` is defined and verified, `default_camera` should be updated to `'flyover_glide'` for the full elevated-perspective aerial feel. See D3. |
| `compatible_cameras` | `['static', 'flyover_glide', 'slow_push_forward', 'slow_pull_back', 'gentle_float']` | See D3. |
| `fog` | `{ color: '#b8c6d4', near: 20, far: 55 }` | Light blue-gray atmospheric haze. See D5. |
| `preferred_aspect` | `'landscape'` | The wide ground plane and lateral landmarks read best in 16:9. Portrait would crop the lateral coverage significantly. |

### Slot Definitions

The flyover geometry defines **6 slots** — 2 required, 4 optional. The ground and sky provide the essential spatial structure; landmarks and foreground are compositional enhancements.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9. While the `flyover_glide` camera will position the camera higher (elevated Y) and angle it downward, the geometry must also work with `slow_push_forward` (camera at `[0, 0, 5]`, lookAt `[0, 0, -30]`) and `static` (camera at `[0, 0, 5]`, lookAt `[0, 0, 0]`).

**Ground visibility with straight-ahead camera:** With camera at `[0, 0, 5]` looking at `[0, 0, -30]` (straight along -Z), the frustum bottom at the ground's Z-center (-20) — distance 25 on Z — is `y_bottom = 0 - 25 × tan(25°) ≈ -11.66`. The ground at Y=-4 is well within the frustum, occupying roughly the bottom third of the frame. As the camera pushes to Z=-3 (end of `slow_push_forward`), the ground remains fully visible — the frustum widens with proximity to the nearest ground segments.

Following the convention established by OBJ-018: the flyover geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `sky`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 20, -50]` | Very deep Z, raised high (Y=20) to sit above the camera and fill the upper frame. Z-axis distance from camera: 55 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane facing the camera. Not a ceiling; a distant sky backdrop. |
| `size` | `[130, 60]` | At Z-distance 55: visible area ≈ 51.3h × 91.1w at FOV 50°, 16:9. Provides ~43% oversize in width and ~17% in height. |
| `required` | `true` | Without a sky, the upper frame is empty in every flyover composition. |
| `description` | `'Sky, atmosphere, or distant horizon. Fills the upper portion of the frame above the ground plane.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Sky is opaque background. |
| `fogImmune` | `true` | Sky should remain vivid regardless of fog — it represents infinite distance, not a surface that fades. |

#### Slot: `ground`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -4, -20]` | Below camera (Y=-4), centered at Z=-20. After FLOOR rotation, `width` (60) maps to X-axis and `height` (80) maps to Z-axis, so the plane covers X ∈ [-30, +30] and Z ∈ [-60, +20]. |
| `rotation` | `[-Math.PI / 2, 0, 0]` | `PLANE_ROTATIONS.FLOOR` — lies flat, faces up. |
| `size` | `[60, 80]` | Width=60 covers ±30 units in X. Depth=80 (Z-axis after rotation) extends from Z=+20 to Z=-60, providing ample coverage for `slow_push_forward`'s 8-unit Z travel (Z=5 to Z=-3). Far edge at Z=-60 is 57 units ahead of camera's deepest position. |
| `required` | `true` | The ground plane is the defining element. Without it, there is no "terrain" to fly over and the aerial illusion fails. |
| `description` | `'Terrain, landscape, or ground surface seen from above. The defining visual element of the flyover — undergoes strong perspective foreshortening as the camera moves forward.'` | |
| `renderOrder` | `1` | Renders above sky. |
| `transparent` | `false` | Ground is opaque. |
| `fogImmune` | `false` | Distant portions of the ground fade with atmospheric haze — enhances aerial depth perception. |

#### Slot: `landmark_far`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 1, -35]` | Deep Z, centered laterally. Y=1 positions the bottom edge at Y=-4 (center 1 − half-height 5 = -4), aligned with the ground surface. Distance from camera: 40 units on Z. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane rising from the ground. |
| `size` | `[12, 10]` | Intentionally small and distant — a far-off landmark (mountain, tower, distant structure), not a coverage element. |
| `required` | `false` | Optional — adds depth and visual interest at the far end. |
| `description` | `'Distant landmark rising from the terrain — mountain, tower, or far-off structure. Provides depth reference at the horizon.'` | |
| `renderOrder` | `2` | Renders above ground. |
| `transparent` | `true` | Landmarks should have transparent backgrounds to blend with ground and sky. |
| `fogImmune` | `false` | Distant landmarks fade with atmospheric haze — a key aerial depth cue. |

#### Slot: `landmark_left`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[-10, 0, -20]` | Left of center (X=-10), mid-depth. Y=0 places the bottom edge at Y=-6 (center 0 − half-height 6 = -6), which extends 2 units below the ground plane at Y=-4. The ground's opaque surface occludes this below-ground portion via Z-buffer: camera rays from above Y=-4 that would reach below the ground at this Z-depth hit the ground plane first. See D4. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[10, 12]` | Medium-sized landmark. Tall (12) to suggest a vertical feature rising from the ground. |
| `required` | `false` | Optional — adds lateral interest. |
| `description` | `'Left-side landmark rising from the terrain — building, tree cluster, or terrain feature. Passes by on the left as the camera moves forward.'` | |
| `renderOrder` | `3` | Renders above far landmark. |
| `transparent` | `true` | Needs alpha to blend with ground/sky. |
| `fogImmune` | `false` | Mid-distance fog fading is appropriate. |

#### Slot: `landmark_right`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[10, 0, -20]` | Right of center (X=10), mirrors `landmark_left`. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[10, 12]` | Matches `landmark_left` for symmetry. |
| `required` | `false` | Optional — adds lateral interest. |
| `description` | `'Right-side landmark rising from the terrain — building, tree cluster, or terrain feature. Passes by on the right as the camera moves forward.'` | |
| `renderOrder` | `3` | Same as `landmark_left` — they don't overlap laterally so no ordering conflict. |
| `transparent` | `true` | Needs alpha. |
| `fogImmune` | `false` | Mid-distance fog fading is appropriate. |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 2, -2]` | Very close to camera, raised slightly (Y=2) to appear as overhead passing elements (clouds, birds, particles). Distance from camera: 7 units on Z. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[20, 14]` | Oversized relative to the frustum at this distance (visible area ≈ 6.5h × 11.6w). Foreground elements typically extend beyond the frame. |
| `required` | `false` | Optional — adds atmosphere (clouds, birds, particles) passing near the camera. |
| `description` | `'Close foreground element — clouds, birds, particles, or atmospheric effects passing near the camera. Creates a sense of speed and altitude.'` | |
| `renderOrder` | `4` | Renders on top of everything. |
| `transparent` | `true` | Must have alpha to not occlude the view below. |
| `fogImmune` | `true` | Foreground is close to camera — fog application would look physically incorrect. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `sky` | `[0, 20, -50]` | `[0, 0, 0]` | `[130, 60]` | **yes** | no | **yes** | 0 |
| `ground` | `[0, -4, -20]` | `[-PI/2, 0, 0]` | `[60, 80]` | **yes** | no | no | 1 |
| `landmark_far` | `[0, 1, -35]` | `[0, 0, 0]` | `[12, 10]` | no | yes | no | 2 |
| `landmark_left` | `[-10, 0, -20]` | `[0, 0, 0]` | `[10, 12]` | no | yes | no | 3 |
| `landmark_right` | `[10, 0, -20]` | `[0, 0, 0]` | `[10, 12]` | no | yes | no | 3 |
| `near_fg` | `[0, 2, -2]` | `[0, 0, 0]` | `[20, 14]` | no | yes | **yes** | 4 |

### Registration Side Effect

```typescript
// src/scenes/geometries/flyover.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(flyoverGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/flyover.ts
export { flyoverGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./flyover` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: `ground` instead of `floor` — semantic distinction from the stage geometry

The stage geometry uses a slot named `floor` — a horizontal surface that functions as a room floor or ground level at the base of a scene. The flyover geometry uses `ground` instead because the semantic role is different: this is a vast terrain/landscape viewed from above, not a surface the subject stands on. The LLM author choosing between `stage` and `flyover` should immediately understand from the slot names that `floor` is "standing surface" while `ground` is "terrain below."

This follows OBJ-005's convention that geometries may define custom slot names beyond the reserved set. The reserved name `floor` has the semantic role "Horizontal ground surface" with `FLOOR` rotation — the flyover's `ground` matches this rotation but differs in scale, positioning, and purpose.

### D2: Ground at Y=-4 — deeper than stage's floor at Y=-3

The flyover's ground is positioned at Y=-4 (vs stage's floor at Y=-3). This extra unit of depth serves two purposes: (a) with the default camera at Y=0, the ground is further below the eye line, emphasizing the aerial perspective even with a straight-ahead camera; (b) it provides more clearance for landmark planes whose bottom edges should visually meet the ground surface.

The ground plane size `[60, 80]` is substantially larger than the stage's floor `[20, 40]` because the flyover emphasizes a vast expanse of terrain. With width=60 (±30 in X) and depth=80 (Z ∈ [+20, -60] after rotation centered at Z=-20), the ground extends well beyond the camera's travel range for all compatible camera presets. With `slow_push_forward`'s 8-unit Z displacement (Z=5 to Z=-3), the far edge at Z=-60 remains 57 units ahead of the camera's deepest position — safely invisible. OBJ-040 validates edge-reveal safety for all compatible cameras including the future `flyover_glide`.

### D3: Compatible cameras — includes `slow_pull_back`, defaults to verified preset

The flyover geometry lists five compatible cameras:

- **`static`** (OBJ-026, verified): Universal baseline. A static aerial shot.
- **`slow_push_forward`** (OBJ-027, verified): Forward Z push from `[0,0,5]` to `[0,0,-3]`. Works because the ground plane is visible in the lower frame and undergoes foreshortening as the camera pushes forward. **Serves as `default_camera`** because it is the only verified forward-motion preset.
- **`slow_pull_back`** (OBJ-027, verified): Reverse of push forward — camera retreats from `[0,0,-3]` to `[0,0,5]`. OBJ-027 lists `flyover` in its `compatibleGeometries` for both push and pull presets. The same ground visibility math applies in reverse: the ground at Y=-4 is within the frustum at all points along the trajectory. Produces a "scene reveal" effect that works for flyover — starting close to terrain and pulling back to reveal the landscape.
- **`gentle_float`** (OBJ-031, verified): Subtle ambient drift. Works universally.
- **`flyover_glide`** (not yet defined): The geometry's intended signature motion — elevated camera gliding forward with a downward look angle. Listed as a forward reference. When defined and verified, `default_camera` should be updated from `'slow_push_forward'` to `'flyover_glide'` for the full aerial experience.

Excluded:
- **`tunnel_push_forward`**: Tuned for enclosed geometry with walls on all sides — would look wrong with a wide-open flyover.
- **`lateral_track_left/right`**: Lateral tracking over terrain risks revealing ground edges on the side the camera moves toward. Potentially addable after OBJ-040 edge-reveal validation confirms safety with the ground's width=60.
- **`crane_up`**: Rising camera would move away from the ground — potentially useful but needs tuning. Deferred.
- **`dramatic_push`**: Faster forward push needs edge-reveal validation at the higher speed. Deferred.

**Default camera rationale:** The seed pattern (Section 4.2) implies `flyover_glide` is the flyover's natural camera. However, seed C-06 (blind-authorable) requires that a manifest omitting the `camera` field produces a valid render. Since `flyover_glide` does not yet exist, `default_camera` must point to a verified preset. `slow_push_forward` is the best verified option — it produces forward motion with ground foreshortening. This is a pragmatic choice; a TODO note accompanies OQ-D to update the default once `flyover_glide` ships.

### D4: Landmarks use custom slot names with ground-occlusion design

The flyover introduces three landmark slots (`landmark_far`, `landmark_left`, `landmark_right`) not in the default depth taxonomy. These are geometry-specific slots per OBJ-005's D8.

Landmarks are positioned so their bottom edges align with or extend slightly below the ground plane's Y-position (-4). The `landmark_far` bottom edge is at Y = 1 - 5 = -4 (exact alignment). The lateral landmarks' bottom edges are at Y = 0 - 6 = -6, extending 2 units below ground.

**Occlusion mechanism:** The ground is an opaque horizontal plane at Y=-4. All compatible cameras position the camera above Y=-4 (the default camera is at Y=0; even `gentle_float` with 0.2 unit Y displacement stays above Y=-4). From any camera position above Y=-4, camera rays passing through screen coordinates below the ground's horizon hit the ground plane first in the Z-buffer before reaching the landmark's below-ground portions. Three.js's Z-buffer naturally occludes the below-ground portions without any special handling. This design means landmark images don't need precise bottom-edge cropping — the ground visually trims them.

**Precondition:** This occlusion only works when the camera Y > -4. All compatible cameras satisfy this (default Y=0, gentle_float minimum Y ≈ -0.2). The future `flyover_glide` will be elevated (Y > 0), strengthening this invariant. OBJ-040 should verify this camera-above-ground precondition for any new camera added to the compatible list.

### D5: Light atmospheric fog — aerial haze, not cinematic darkness

The flyover uses light blue-gray fog (`#b8c6d4`) instead of the stage's black fog (`#000000`). This simulates aerial atmospheric haze — the natural phenomenon where distant objects appear lighter and bluer when viewed from altitude. The fog settings `near: 20, far: 55` create progressive haze on distant landmarks and the far end of the ground plane, enhancing depth perception.

The `near: 20` threshold ensures the ground immediately below the camera (nearest visible portion at ~11 units from camera at default position) remains crisp. The `far: 55` allows the sky (at Z=-50, distance ~55) to be nearly fully fogged — which is why `sky` is `fogImmune: true`.

### D6: Sky at Y=20 — elevated to fill the upper frame

The sky plane is positioned at Y=20, much higher than the stage's sky at Y=5. With the camera at Y=0, the sky's Y offset of 20 units at Z-distance 55 creates a viewing angle of arctan(20/55) ≈ 20°, which places it well within the upper half of the 50° FOV frustum. This ensures sky visibility even with a straight-ahead camera, and with a downward-angled `flyover_glide` camera, the sky remains visible at the top of the frame.

### D7: near_fg at Y=2 — overhead elements, not ground obstacles

Unlike the stage's `near_fg` at Y=0, the flyover's `near_fg` is elevated to Y=2. In an aerial context, close foreground elements are things passing overhead or at camera level — clouds, birds, particles. Positioning them above center reinforces the "high altitude" feel.

### D8: `landmark_left` and `landmark_right` share renderOrder

Both lateral landmarks have `renderOrder: 3`. Since they're separated laterally (X=-10 and X=10), they occupy different screen regions and do not compete for draw order. If they overlapped from the camera's perspective, Z-buffer sorting would handle it correctly since they're at the same Z-depth.

### D9: Only 2 required slots — minimum viable flyover

The flyover requires only `sky` and `ground`. A valid flyover can be authored with just two images — a ground texture and a sky backdrop. Landmarks and foreground are enhancements. This keeps the bar low for LLM authoring while allowing richer compositions with all 6 slots.

### D10: `preferred_aspect` is `landscape`

Unlike the stage geometry (`both`), the flyover is explicitly designed for landscape (16:9). The wide ground plane and lateral landmarks are the core visual appeal; in portrait (9:16), the lateral coverage shrinks dramatically and the landmarks may crowd or fall outside the frame. The geometry will still render correctly in portrait mode (seed C-04), but the SKILL.md should guide LLM authors toward landscape.

### D11: PlaneSlot construction, not DepthSlot — follows OBJ-018 convention

Same as OBJ-018: the geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration. OBJ-007's `DepthSlot` fields (`promptGuidance`, `expectsAlpha`) are not part of the `PlaneSlot` type and are not set here.

**Prompt guidance gap for geometry-specific slots:** The flyover introduces custom slots (`ground`, `landmark_far`, `landmark_left`, `landmark_right`) not present in OBJ-007's `DEFAULT_SLOT_TAXONOMY`. OBJ-007 provides `promptGuidance` and `expectsAlpha` only for the 5 default taxonomy slots. This means downstream consumers (OBJ-071 SKILL.md, OBJ-053 prompt template library) cannot source prompt guidance for these custom slots from `DEFAULT_SLOT_TAXONOMY`. They must instead derive guidance from the `PlaneSlot.description` field plus any geometry-specific documentation provided by OBJ-071. This gap also exists in OBJ-018 (which defines `backdrop`, not in the default taxonomy). A cross-cutting solution — such as extending OBJ-005's `PlaneSlot` to include `promptGuidance` or adding a per-geometry prompt guidance map — is out of scope for individual geometry specs and should be addressed when OBJ-071 (SKILL.md) is specified.

### D12: Explicit optional field policy — follows OBJ-018 convention

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot, following the convention established by OBJ-018.

### D13: Sequential renderOrder values 0–4

The renderOrder progresses sequentially: sky(0), ground(1), landmark_far(2), landmark_left/right(3), near_fg(4). This follows OBJ-018's convention of sequential, gapless ordering from back to front.

## Acceptance Criteria

- [ ] **AC-01:** `flyoverGeometry.name` is `'flyover'`.
- [ ] **AC-02:** `flyoverGeometry.slots` contains exactly 6 keys: `sky`, `ground`, `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `sky`, `ground` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `flyoverGeometry.default_camera` is `'slow_push_forward'`.
- [ ] **AC-05:** `flyoverGeometry.default_camera` appears in `flyoverGeometry.compatible_cameras`.
- [ ] **AC-06:** `flyoverGeometry.compatible_cameras` includes `'static'` and `'gentle_float'`.
- [ ] **AC-07:** `flyoverGeometry.compatible_cameras` includes `'slow_push_forward'` and `'slow_pull_back'`.
- [ ] **AC-08:** `flyoverGeometry.compatible_cameras` includes `'flyover_glide'` (forward reference).
- [ ] **AC-09:** `flyoverGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'`.
- [ ] **AC-10:** `flyoverGeometry.compatible_cameras` contains exactly 5 entries.
- [ ] **AC-11:** `flyoverGeometry.fog` is `{ color: '#b8c6d4', near: 20, far: 55 }`.
- [ ] **AC-12:** `flyoverGeometry.description` is non-empty and describes an aerial/bird's-eye perspective.
- [ ] **AC-13:** `flyoverGeometry.preferred_aspect` is `'landscape'`.
- [ ] **AC-14:** The `ground` slot uses `PLANE_ROTATIONS.FLOOR` (`[-Math.PI/2, 0, 0]`) as its rotation.
- [ ] **AC-15:** All non-ground slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-16:** `landmark_far`, `landmark_left`, `landmark_right`, and `near_fg` have `transparent: true`. `sky` and `ground` have `transparent: false`.
- [ ] **AC-17:** `sky` and `near_fg` have `fogImmune: true`. All other slots have `fogImmune: false`.
- [ ] **AC-18:** `renderOrder` values are sequential: sky(0), ground(1), landmark_far(2), landmark_left(3), landmark_right(3), near_fg(4).
- [ ] **AC-19:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-20:** `registerGeometry(flyoverGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-21:** All slot `description` fields are non-empty strings.
- [ ] **AC-22:** All slot `size` components are positive (> 0).
- [ ] **AC-23:** For the `sky` slot (Z-distance 55 from camera at Z=5): size [130, 60] >= frustum visible area (≈91.1w × 51.3h at FOV=50°, 16:9).
- [ ] **AC-24:** For the `near_fg` slot (Z-distance 7 from camera at Z=5): size [20, 14] >= frustum visible area (≈11.6w × 6.5h).
- [ ] **AC-25:** The `ground` slot and landmark slots are exempt from direct frustum-dimension comparison — `ground` due to rotated orientation (validated by OBJ-040) and landmarks because they are focal elements, not coverage planes.
- [ ] **AC-26:** Slot Z-positions decrease (go more negative) as depth increases: `near_fg` (-2) > lateral landmarks (-20) > `landmark_far` (-35) > `sky` (-50). `ground` center is at Z=-20.
- [ ] **AC-27:** The module self-registers via `registerGeometry(flyoverGeometry)` as a side effect of import.
- [ ] **AC-28:** The module exports `flyoverGeometry` as a named export.
- [ ] **AC-29:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants (`PLANE_ROTATIONS`).
- [ ] **AC-30:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-31:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-32:** The `ground` slot Y-position (-4) is below the `landmark_left` and `landmark_right` Y-positions (0), ensuring landmarks appear to rise above the ground.
- [ ] **AC-33:** `landmark_left.position[0]` is the negation of `landmark_right.position[0]` (lateral symmetry: -10 vs 10).
- [ ] **AC-34:** `landmark_left.size` equals `landmark_right.size`.

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`sky`, `ground`) | Valid scene. Minimal flyover with just terrain and sky. |
| Manifest provides all 6 slots | Valid scene. Full depth layering. |
| Manifest provides `landmark_left` but not `landmark_right` | Valid. Asymmetric composition. |
| Manifest provides `landmark_right` but not `landmark_left` | Valid. Asymmetric composition. |
| Manifest provides `landmark_far` without lateral landmarks | Valid. Single distant focal point. |
| Manifest uses `floor` instead of `ground` | Rejected by manifest validation (OBJ-017). Error names the invalid key and lists valid flyover slot names. |
| Manifest uses `subject` (not a flyover slot) | Rejected — `subject` is not in the flyover's slot set. |
| Camera pushes forward far enough to reveal ground's far edge | Ground Z-extent is [+20, -60]. With `slow_push_forward` ending at Z=-3, the far edge at Z=-60 is 57 units ahead — safely invisible. For `flyover_glide`, OBJ-040 validates. |
| Ground edge visible on sides during lateral camera motion | Ground width is 60 units (±30 in X). With `gentle_float`'s max X displacement of 0.3 units, lateral edge reveal is impossible. Lateral track cameras excluded. |
| Portrait mode (9:16) | Geometry renders correctly. Narrower width shows less ground laterally. Landmarks at X=±10 may be partially outside the frame. `preferred_aspect: 'landscape'` guides LLMs away. |
| Landmark bottom edge below ground Y-position | By design. Z-buffer handles occlusion: camera above Y=-4 sees ground before landmark below-ground portions. See D4. |
| Sky plane fully obscured by fog | Cannot happen — `sky` is `fogImmune: true`. |
| Camera dips below Y=-4 | No compatible camera does this. All verified cameras have Y ≥ -0.2. If a future camera is added, OBJ-040 must verify the camera-above-ground invariant. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `flyover.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'flyover' is already registered." Module relies on Node.js module caching. |
| `flyover.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'flyover': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `flyoverGeometry.name` is `'flyover'`.
2. `flyoverGeometry.slots` has exactly 6 keys: `sky`, `ground`, `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.
3. Required slots: `sky`, `ground`. Optional: `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'slow_push_forward'` and is in `compatible_cameras`.
6. `compatible_cameras` contains exactly 5 entries, all matching `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` is `'#b8c6d4'`.
8. `description` is non-empty.
9. `preferred_aspect` is `'landscape'`.

**Slot spatial correctness tests:**
10. `ground` slot rotation matches `PLANE_ROTATIONS.FLOOR` exactly (`[-Math.PI/2, 0, 0]`).
11. All non-ground slots have rotation `[0, 0, 0]`.
12. Z-positions ordered: `near_fg` (-2) > lateral landmarks (-20) > `landmark_far` (-35) > `sky` (-50).
13. `renderOrder` values: sky(0), ground(1), landmark_far(2), landmark_left(3), landmark_right(3), near_fg(4).
14. All `size` components are > 0.
15. `ground` Y-position (-4) is below lateral landmark Y-positions (0).

**Slot metadata tests:**
16. `landmark_far`, `landmark_left`, `landmark_right`, `near_fg` have `transparent: true`.
17. `sky`, `ground` have `transparent: false`.
18. `sky`, `near_fg` have `fogImmune: true`.
19. `ground`, `landmark_far`, `landmark_left`, `landmark_right` have `fogImmune: false`.
20. All slot `description` fields are non-empty.
21. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
22. `validateGeometryDefinition(flyoverGeometry)` returns an empty error array.
23. `registerGeometry(flyoverGeometry)` does not throw (when registry is not locked).
24. After registration, `getGeometry('flyover')` returns the flyover geometry.

**Frustum size validation tests:**
25. `sky` size [130, 60] >= visible area at Z-distance 55 with FOV=50° and 16:9 (≈91.1w × 51.3h). ✓
26. `near_fg` size [20, 14] >= visible area at Z-distance 7 (≈11.6w × 6.5h). ✓
27. `ground`: exempt from direct frustum comparison (rotated plane, validated by OBJ-040).
28. Landmark slots: exempt (focal elements, not coverage planes).

**Compatible cameras tests:**
29. `compatible_cameras` includes `'static'`, `'flyover_glide'`, `'slow_push_forward'`, `'slow_pull_back'`, `'gentle_float'`.
30. `compatible_cameras` does NOT include `'tunnel_push_forward'`.

**Symmetry tests:**
31. `landmark_left.position[0]` is the negation of `landmark_right.position[0]`.
32. `landmark_left.size` equals `landmark_right.size`.
33. `landmark_left.renderOrder` equals `landmark_right.renderOrder`.

### Relevant Testable Claims

- **TC-01** (partial): The flyover geometry uses 6 slots (2 required, 4 optional), within the 3-5 effective range for most compositions.
- **TC-04** (partial): All spatial relationships defined by geometry. LLM specifies `geometry: 'flyover'` and maps images to slot names.
- **TC-08** (partial): The flyover covers aerial/landscape/travel themes that other geometries cannot.

## Integration Points

### Depends on

| Upstream | What OBJ-021 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types. `registerGeometry` function. |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`). `DEFAULT_SLOT_TAXONOMY` for reference only. |
| **OBJ-003** (Spatial math) | `PLANE_ROTATIONS.FLOOR` constant. `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for position reference. |

### Consumed by

| Downstream | How it uses OBJ-021 |
|------------|---------------------|
| **OBJ-062** (Flyover visual tuning) | Director Agent reviews test renders; may adjust numerical values. |
| **OBJ-070** (End-to-end render test) | May use flyover as a test geometry. |
| **OBJ-071** (SKILL.md) | Documents flyover slot names, descriptions, usage guidance. Must source prompt guidance from `PlaneSlot.description` fields for geometry-specific slots not in `DEFAULT_SLOT_TAXONOMY`. |
| **OBJ-017** (Manifest validation) | Looks up `getGeometry('flyover')` to validate manifest plane keys. |
| **OBJ-036** (Scene sequencer) | Resolves slot spatial data for flyover scenes. |
| **OBJ-039** (Page-side renderer) | Creates Three.js meshes from slot data. |
| **OBJ-040** (Edge-reveal validation) | Validates camera paths don't reveal ground edges. Must also verify camera-above-ground invariant (camera Y > -4) for all compatible cameras. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        flyover.ts        # flyoverGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./flyover
```

## Open Questions

### OQ-A: Should the ground plane be larger for `flyover_glide`?

The ground size `[60, 80]` is validated for `slow_push_forward` (8 units Z travel). When `flyover_glide` is defined with deeper Z travel and a downward look angle, the ground may need expansion — potentially `[80, 120]`. OBJ-062 (visual tuning) will validate and adjust.

**Recommendation:** Keep the current size. OBJ-062 tuning adjusts when `flyover_glide` is defined.

### OQ-B: Should there be a `landmark_center` slot?

A centered midground landmark could add depth but risks occluding `landmark_far`. Keeping center clear creates a stronger vanishing-point depth cue.

**Recommendation:** Defer. The LLM can use `landmark_far` with position override for a midground element.

### OQ-C: Fog color configurability

The manifest's per-scene fog override (per OBJ-005's fog contract) already handles per-scene variation — the LLM can override `fog.color` without changing the geometry.

**Recommendation:** No change needed.

### OQ-D: `default_camera` update when `flyover_glide` ships

When `flyover_glide` is defined and verified, `default_camera` should be changed from `'slow_push_forward'` to `'flyover_glide'` for the full aerial experience. This is a planned update, not a design gap.

**Recommendation:** Track as a TODO in the flyover geometry source file. OBJ-062 (visual tuning) is the natural point to make this change, since tuning validates the geometry + camera combination.

---

## Changes from Round 1

| Issue | Resolution |
|-------|------------|
| **#2 (Major): `slow_pull_back` missing** | Added `'slow_pull_back'` to `compatible_cameras`. Updated D3 with rationale. Updated AC-07, AC-10. |
| **#3 (Major): `default_camera` points to undefined preset** | Changed `default_camera` from `'flyover_glide'` to `'slow_push_forward'`. Updated AC-04. Added D3 paragraph on default camera rationale. Added OQ-D for planned update. |
| **#1 (Minor): Ground visibility math** | Added explicit frustum calculation in slot definitions section: `y_bottom = 0 - 25 × tan(25°) ≈ -11.66`, ground at Y=-4 is within frustum. |
| **#5 (Minor): Occlusion claim imprecise** | Expanded D4 with explicit occlusion mechanism: camera-above-ground precondition, Z-buffer behavior, and note that OBJ-040 should verify this invariant for future cameras. |
| **#6 (Minor): renderOrder gap** | Changed `near_fg` renderOrder from 5 to 4, making the sequence gapless (0,1,2,3,3,4). Added D13 explaining the sequential pattern. |
| **#7 (Minor): Prompt guidance gap** | Added paragraph to D11 acknowledging the gap, explaining it exists in OBJ-018 too, and noting it's a cross-cutting concern for OBJ-071 to solve. |

I believe all six issues are now resolved. I'd like the Challenger to verify and approve.

---

## Round 4 — spec_challenger

I've carefully verified every fix against my Round 2 objections. Let me confirm:

**Issue 2 (Major): `slow_pull_back` missing** — ✅ Verified. Added to `compatible_cameras`. D3 expanded. AC-07 and AC-10 updated. Cross-reference with OBJ-027's `compatibleGeometries` is now consistent.

**Issue 3 (Major): `default_camera` pointing to undefined preset** — ✅ Verified. Changed to `'slow_push_forward'` (verified OBJ-027). AC-04 updated. OQ-D tracks the planned update to `flyover_glide`.

**Issue 1 (Minor): Ground visibility math** — ✅ Verified. Explicit frustum calculation in slot definitions preamble: `y_bottom ≈ -11.66`, ground at Y=-4 is within.

**Issue 5 (Minor): Occlusion imprecision** — ✅ Verified. D4 now explains Z-buffer mechanism and camera-above-ground precondition, with note for OBJ-040.

**Issue 6 (Minor): renderOrder gap** — ✅ Verified. near_fg now 4 (was 5). Slot summary table, AC-18, and D13 all consistent.

**Issue 7 (Minor): Prompt guidance gap** — ✅ Verified. D11 now explicitly acknowledges the cross-cutting gap and defers to OBJ-071.

No new issues introduced by the revisions. The spec is precise, follows OBJ-018 conventions, addresses all dependency contracts correctly, and is implementable without guessing.

CONCLUSION:

The flyover scene geometry (OBJ-021) specification defines a 6-slot aerial/bird's-eye geometry with a large FLOOR-rotated ground plane, elevated sky backdrop, three optional landmark slots, and a near foreground slot. It defaults to `slow_push_forward` camera (verified) while listing `flyover_glide` as a forward reference. Key design choices: light atmospheric fog, ground occlusion of landmark bottom edges, landscape-preferred aspect, and sequential renderOrder. All Round 2 issues resolved.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the final spec and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "content": "# Specification: Flyover Scene Geometry (OBJ-021)\n\n## Summary\n\nOBJ-021 defines the **flyover** scene geometry \u2014 a spatial arrangement designed for aerial/bird's-eye perspective. A large ground plane lies below the camera (`FLOOR` rotation), a sky plane sits at extreme depth above, and optional landmark planes rise vertically from the ground at varying depths and lateral positions. The camera moves forward while positioned above the ground, producing an immersive \"flying over terrain\" effect where the ground plane undergoes strong perspective foreshortening and landmarks pass by on either side. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.\n\n## Interface Contract\n\n### Exported Geometry Definition\n\n```typescript\n// src/scenes/geometries/flyover.ts\n\nimport type { SceneGeometry } from './types';\n\n/**\n * The flyover scene geometry \u2014 aerial/bird's-eye perspective.\n *\n * Spatial arrangement: a large ground plane below the camera\n * (FLOOR rotation), a distant sky backdrop above, and optional\n * landmark planes rising from the ground at varying depths.\n * Camera moves forward for a \"flying over terrain\" effect where\n * the ground undergoes strong perspective foreshortening and\n * landmarks pass by laterally.\n *\n * The ground plane is the defining spatial element \u2014 it provides\n * the primary depth cue through perspective convergence as the\n * camera moves forward. Landmarks add lateral interest and\n * depth layering.\n *\n * Best suited for landscape, environment, and travel themes.\n * Designed primarily for 16:9 landscape orientation where\n * the wide frame emphasizes the panoramic ground coverage.\n */\nexport const flyoverGeometry: SceneGeometry;\n```\n\n### Geometry Fields\n\n| Field | Value | Rationale |\n|-------|-------|-----------|\n| `name` | `'flyo
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-021",
     3→  "description": "Flyover scene geometry -- large ground plane below (rotation [-PI/2,0,0]), sky plane above, optional landmark planes rising from the ground. Camera moves forward and slightly downward-looking. Aerial/bird's-eye perspective feel. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 geometry."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/meta.json",
  "content": "{\n  \"id\": \"OBJ-021\",\n  \"description\": \"Flyover scene geometry -- large ground plane below (rotation [-PI/2,0,0]), sky plane above, optional landmark planes rising from the ground. Camera moves forward and slightly downward-looking. Aerial/bird's-eye perspective feel. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:00:00Z\",\n  \"depends_on\": [\"OBJ-005\", \"OBJ-007\"],\n  \"status\": \"specified\",\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 geometry. 6 slots (sky, ground, landmark_far, landmark_left, landmark_right, near_fg). 2 required (sky, ground). Default camera: slow_push_forward (verified). flyover_glide listed as forward reference. Light atmospheric fog #b8c6d4. Landscape preferred.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/meta.json has been updated successfully.
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
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-021/meta.json

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
	nodes/OBJ-013/transcript.md
	nodes/OBJ-014/transcript.md
	nodes/OBJ-015/transcript.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-019/transcript.md
	nodes/OBJ-020/transcript.md
	nodes/OBJ-021/output.md
	nodes/OBJ-026/transcript.md
	nodes/OBJ-027/transcript.md
	nodes/OBJ-... [truncated]

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commit messages"
}
[Tool Result] fd55d28 spec(OBJ-020): canyon scene geometry specification
4fb72b7 spec(OBJ-014): FFmpeg audio muxing specification
85a7d42 spec(OBJ-019): tunnel scene geometry specification
9ea9d41 spec(OBJ-011): Puppeteer-to-page message protocol
d9a7835 OBJ-027: Push/pull camera path preset specification

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-021/output.md nodes/OBJ-021/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-021): flyover scene geometry specification\n\nDefines the flyover geometry \u2014 aerial/bird's-eye perspective with 6 slots\n(sky, ground, landmark_far, landmark_left, landmark_right, near_fg).\n2 required (sky, ground), 4 optional. Default camera: slow_push_forward\n(verified). flyover_glide listed as forward reference. Light atmospheric\nfog (#b8c6d4). Landscape preferred aspect.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-021 spec files"
}
[Tool Result] [master 6dbb8fc] spec(OBJ-021): flyover scene geometry specification
 2 files changed, 431 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-021/output.md
Spec committed. The OBJ-021 flyover scene geometry specification is finalized and written to disk at `nodes/OBJ-021/output.md` with updated `meta.json`. Commit `6dbb8fc`.
