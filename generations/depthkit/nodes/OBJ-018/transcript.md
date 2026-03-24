# Deliberation Transcript: OBJ-018

---

## Round 1 — spec_author

Let me first check the current state of the project files and any existing work on OBJ-018.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me check the existing project structure and any relevant files.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-018/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json

[Tool: Glob]
  Input: {
  "pattern": "src/scenes/geometries/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/spatial/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-005/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-007/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-003/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md

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
Now let me also check the OBJ-006 spec since camera paths are closely related to the stage geometry:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-006/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md"
}
[Tool Error] File content (11307 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "limit": 150
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
  "offset": 150,
  "limit": 150
}
[Tool Result]    150→ *   effectiveDisplacement = maxDisplacement * speed
   151→ *
   152→ * These values do NOT account for CameraParams.offset. OBJ-040 must
   153→ * add abs(offset[i]) to each axis displacement when validating.
   154→ */
   155→export interface OversizeRequirements {
   156→  /**
   157→   * Maximum camera displacement along the X axis (world units).
   158→   * Must be >= 0.
   159→   */
   160→  maxDisplacementX: number;
   161→
   162→  /**
   163→   * Maximum camera displacement along the Y axis (world units).
   164→   * Must be >= 0.
   165→   */
   166→  maxDisplacementY: number;
   167→
   168→  /**
   169→   * Maximum camera displacement along the Z axis (world units).
   170→   * Must be >= 0. Consumed by OBJ-040 to compute worst-case
   171→   * visible area at each plane's depth.
   172→   */
   173→  maxDisplacementZ: number;
   174→
   175→  /**
   176→   * The FOV range across the path's duration: [min, max] in degrees.
   177→   * Both values must be in (0, 180)... [truncated]
Good, I now have enough context. Let me also check if there are any existing camera path implementations that reference the stage geometry:
[Tool: Grep]
  Input: {
  "pattern": "stage",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026",
  "output_mode": "content"
}
[Tool Result] nodes/OBJ-026/output.md:39:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']` | All eight geometries from seed Section 4.2. A static camera is universally safe. |
nodes/OBJ-026/output.md:147:- [ ] **AC-11:** `compatibleGeometries` contains exactly: `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']`.
nodes/OBJ-026/transcript.md:45:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']` | All eight geometries from seed Section 4.2. A static camera is universally safe. |
nodes/OBJ-026/transcript.md:158:- [ ] **AC-11:** `compatibleGeometries` contains exactly: `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']`.

[Tool: Grep]
  Input: {
  "pattern": "stage",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027",
  "output_mode": "content"
}
[Tool Result] No matches found

[Tool: Grep]
  Input: {
  "pattern": "stage",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031",
  "output_mode": "content"
}
[Tool Result] nodes/OBJ-031/transcript.md:136:    'stage',
nodes/OBJ-031/transcript.md:275:- [ ] **AC-20:** `compatibleGeometries` includes all 8 geometry names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.
nodes/OBJ-031/transcript.md:616:    'stage',
nodes/OBJ-031/transcript.md:757:- [ ] **AC-20:** `compatibleGeometries` includes all 8 geometry names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.
nodes/OBJ-031/output.md:136:    'stage',
nodes/OBJ-031/output.md:277:- [ ] **AC-20:** `compatibleGeometries` includes all 8 geometry names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.

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
Now let me check OBJ-027 (slow_push_forward) since that's specifically mentioned as a stage-compatible camera in the seed:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "limit": 120
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-027/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/meta.json
OBJ-027 is in_progress with no output yet. Let me check its meta:
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
Good. OBJ-027 is in_progress but has no output.md yet. Now I have enough context to draft the spec. Let me synthesize everything.

---

Here is my proposed specification for **OBJ-018: Stage Scene Geometry**.

---

# Specification: Stage Scene Geometry (OBJ-018)

## Summary

OBJ-018 defines the **stage** scene geometry — the default, most fundamental geometry in depthkit. It represents a classic "subject in front of a background" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/stage.ts

import type { SceneGeometry } from './types';

/**
 * The stage scene geometry — the default geometry for depthkit.
 *
 * Spatial arrangement: a large backdrop plane at deep Z, a floor
 * plane angled down from the camera (FLOOR rotation), and a
 * subject plane at shallow Z. Optional sky, midground, and
 * near_fg planes provide additional depth layering.
 *
 * Classic "subject in front of a background" setup with real
 * perspective on the floor. The floor's perspective foreshortening
 * as the camera pushes forward is the primary 2.5D effect.
 *
 * This is the most commonly used geometry and the basis for
 * SKILL.md examples.
 */
export const stageGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'stage'` | Matches seed Section 4.2 naming |
| `description` | `'A classic subject-in-front-of-background setup. Large backdrop at depth, angled floor plane with real perspective foreshortening, and a subject plane at shallow Z. The most versatile geometry for general-purpose scenes.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes in or drifts laterally." Forward push is the defining 2.5D motion. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'lateral_track_left', 'lateral_track_right', 'gentle_float', 'dramatic_push', 'crane_up']` | Stage supports most camera motions except geometry-specific ones (tunnel_push_forward, flyover_glide). Panorama rotation doesn't suit a stage with a flat backdrop. Dolly zoom may be added post-tuning. |
| `fog` | `{ color: '#000000', near: 20, far: 60 }` | Subtle atmospheric fade on distant planes. `near: 20` leaves the subject (Z=-5, ~10 units from camera) completely unaffected. `far: 60` fades the sky plane gently. |
| `preferred_aspect` | `'both'` | Stage works in landscape and portrait — plane sizes are designed for 16:9 but are oversized enough for 9:16 with camera-default FOV. |

### Slot Definitions

The stage geometry defines **6 slots** — 3 required, 3 optional. This follows the standard layered depth arrangement from seed Section 4.1 but adds a `floor` slot (which is not in the default taxonomy) for the perspective-foreshortened ground plane.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate camera motion at `speed=1.0` for the default camera (`slow_push_forward`).

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -30]` | Deep Z, serves as primary background. Distance from camera: 35 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane facing the camera. |
| `size` | `[75, 45]` | Oversized to prevent edge reveals during camera push. Frustum visible area at distance 35: ~32.6 × 58.0 (16:9). Oversized ~1.3× horizontally, ~1.38× vertically, accommodating ±5 unit Z push + lateral drift. |
| `required` | `true` | Every stage scene needs a background. |
| `description` | `'Primary background — landscape, environment, or atmospheric backdrop.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backgrounds are opaque. |
| `fogImmune` | `false` | Fades naturally with distance. |

#### Slot: `sky`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 5, -50]` | Very deep Z, raised slightly above center to fill the upper portion of the frame behind the backdrop. Distance from camera: 55 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[120, 70]` | Matches `DEFAULT_SLOT_TAXONOMY.sky`. Massively oversized for this distance — provides safety margin for all camera motions. |
| `required` | `false` | Optional — many stage scenes work with just a backdrop. Useful when the backdrop doesn't fill the full frame at all camera positions, or for a sky gradient visible above the backdrop. |
| `description` | `'Distant sky or gradient visible behind the backdrop. Use when the backdrop does not fill the entire frame.'` | |
| `renderOrder` | `-1` | Renders behind the backdrop. (Negative renderOrder is valid in Three.js.) |
| `transparent` | `false` | Sky planes are opaque. |
| `fogImmune` | `true` | Sky should remain vivid at extreme distance — fog would make it invisible. |

#### Slot: `floor`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -3, -10]` | Below the camera, centered in Z between camera and backdrop. Y=-3 positions the floor plane below the frame center; the `FLOOR` rotation makes it extend away from the camera. |
| `rotation` | `[-Math.PI / 2, 0, 0]` | `PLANE_ROTATIONS.FLOOR` — lies flat, faces up. This is the key plane that produces perspective foreshortening as the camera moves forward. |
| `size` | `[20, 40]` | Width=20 fills the horizontal view at floor level. Height=40 (depth extent, since the plane is rotated) extends from near the camera to behind the backdrop, preventing the floor from ending visibly. |
| `required` | `true` | The floor plane is the defining spatial element of the stage geometry — without it, there's no perspective reference and the scene reads as flat. |
| `description` | `'Ground surface — the floor plane that provides perspective foreshortening. The defining spatial element of the stage geometry.'` | |
| `renderOrder` | `1` | Renders above the backdrop. |
| `transparent` | `false` | Floors are opaque. |
| `fogImmune` | `false` | Distant portions of the floor fade naturally — enhances depth illusion. |

#### Slot: `midground`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -1, -15]` | Between backdrop and subject. Slightly below center to sit on the floor plane visually. Distance from camera: 20 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[40, 25]` | Matches `DEFAULT_SLOT_TAXONOMY.midground`. Oversized for camera motion. |
| `required` | `false` | Optional — adds depth layering but many stage scenes work fine without it. |
| `description` | `'Middle-distance element — buildings, terrain, or environmental props between backdrop and subject.'` | |
| `renderOrder` | `2` | Renders above floor. |
| `transparent` | `false` | Midground elements are typically opaque full-width environmental elements. |
| `fogImmune` | `false` | Fades with distance. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -0.5, -5]` | Shallow Z, slightly below center to appear grounded on the floor. Distance from camera: 10 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[12, 12]` | Sized to fill roughly 50-65% of the frame height at this distance. Frustum visible height at distance 10: ~9.33 units. 12/9.33 ≈ 1.29× — provides margin without overwhelming the frame. Square default accommodates both portrait and landscape subject images via texture aspect-ratio auto-sizing (OBJ-040). |
| `required` | `true` | The subject is the focal point of every stage scene. |
| `description` | `'Primary subject — person, animal, object, or focal element. Should be generated with a transparent background.'` | |
| `renderOrder` | `3` | Renders above midground. |
| `transparent` | `true` | Subject images need alpha transparency to avoid rectangular edges (seed OQ-02, Section 4.8). |
| `fogImmune` | `false` | Subject is close enough that fog has minimal effect with default fog settings (near=20 > distance 10). |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -1]` | Very close to camera. Distance from camera: 6 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[25, 16]` | Oversized to fill the frame edge-to-edge at close range. Frustum visible area at distance 6: ~5.60 × 9.95. Dramatically oversized because foreground elements typically extend beyond the frame (particles, foliage edges). |
| `required` | `false` | Optional — adds foreground framing but many scenes work without it. |
| `description` | `'Foreground framing element — foliage, particles, bokeh, or decorative edges. Should have a transparent background.'` | |
| `renderOrder` | `4` | Renders on top of everything. |
| `transparent` | `true` | Foreground elements need alpha to not occlude the subject. |
| `fogImmune` | `true` | Foreground is so close that any fog application would look wrong — fog represents atmospheric distance, and near_fg is the opposite of distant. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `sky` | `[0, 5, -50]` | `[0, 0, 0]` | `[120, 70]` | no | no | **yes** | -1 |
| `backdrop` | `[0, 0, -30]` | `[0, 0, 0]` | `[75, 45]` | **yes** | no | no | 0 |
| `floor` | `[0, -3, -10]` | `[-π/2, 0, 0]` | `[20, 40]` | **yes** | no | no | 1 |
| `midground` | `[0, -1, -15]` | `[0, 0, 0]` | `[40, 25]` | no | no | no | 2 |
| `subject` | `[0, -0.5, -5]` | `[0, 0, 0]` | `[12, 12]` | **yes** | yes | no | 3 |
| `near_fg` | `[0, 0, -1]` | `[0, 0, 0]` | `[25, 16]` | no | yes | no | 4 |

### Registration Side Effect

```typescript
// src/scenes/geometries/stage.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(stageGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/stage.ts
export { stageGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./stage` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Six slots — the default taxonomy plus `floor`

The seed's default depth taxonomy (Section 4.1) has 5 slots: `sky`, `back_wall`, `midground`, `subject`, `near_fg`. The stage geometry uses `backdrop` instead of `back_wall` (more descriptive for a stage's flat background), drops `sky` to optional, and **adds `floor`** — a horizontal plane with `FLOOR` rotation that provides perspective foreshortening. This is the core visual feature that distinguishes 2.5D from flat parallax.

Six slots falls within the 3-5 range that TC-01 considers sufficient for 90% of cases (the count is at the upper bound, but `sky` and `near_fg` are optional, so the minimum working scene uses 3: `backdrop`, `floor`, `subject`).

**Rationale:** Without the floor, a stage scene is just layered flat images — no better than 2D parallax. The floor plane, undergoing perspective distortion as the camera pushes forward, is what produces the "real 3D space" illusion that is depthkit's value proposition.

### D2: Floor position and size

The floor plane is at `Y=-3` (below the frame center) with `FLOOR` rotation and a size of `[20, 40]`. The 40-unit depth extent (measured along the Z-axis after rotation) ensures the floor extends from near the camera all the way past the backdrop.

The floor's Y-position of -3 was chosen so that with the default camera at `[0, 0, 5]` looking at `[0, 0, 0]`, the floor is visible in the lower portion of the frame. The perspective convergence point is roughly where the floor meets the backdrop plane, creating a natural vanishing effect.

**Trade-off:** Raising the floor (e.g., Y=-2) shows more floor area but pushes the subject higher in the frame. Lowering it (Y=-4) reduces visible floor but gives the subject more room. Y=-3 is a starting point for visual tuning (OBJ-059).

### D3: `backdrop` instead of `back_wall`

The seed's reserved slot name `back_wall` implies a vertical surface in an enclosed space. A stage's primary background is more often an open landscape, gradient, or scene — `backdrop` better communicates its role. This follows OBJ-005's convention that geometries may define custom slot names beyond the reserved set.

### D4: Subject at Y=-0.5 (slightly below center)

The subject is positioned 0.5 units below the Y-axis center. This places the subject's visual center at roughly the lower third of the frame — a classic photographic/cinematographic composition rule. Combined with the floor at Y=-3, the subject appears to "stand on" the floor.

### D5: Compatible cameras exclude geometry-specific presets

The stage excludes `tunnel_push_forward` (tuned for enclosed corridor geometries) and `flyover_glide` (requires a below-camera ground plane — stage's floor extends *away* from the camera, not *below* it). `panorama` rotation doesn't work because the backdrop is a flat plane — panning would reveal its edge immediately.

`dolly_zoom` is excluded from the initial compatible list because it requires careful FOV range coordination with plane sizes. It can be added after tuning (OBJ-059) validates edge-reveal safety.

### D6: Fog settings: near=20, far=60

Fog `near: 20` ensures the subject (distance ~10 units from camera) and floor (nearest portion ~8 units) are fully clear. Fog `near: 20` begins to fade the midground (distance ~20) very slightly and progressively fades the backdrop (distance ~35) and sky (distance ~55). `far: 60` means the sky is nearly fully fogged — which is why the sky slot is `fogImmune: true`, preventing it from disappearing.

Black fog (`#000000`) creates a cinematic depth fade. Scene authors can override to match their scene's mood via the manifest's fog override (per OBJ-005's fog contract).

### D7: Sky slot is fog-immune and has negative renderOrder

The sky at Z=-50 would be nearly invisible with fog (near=20, far=60). Marking it `fogImmune: true` ensures it renders at full brightness. It renders at `renderOrder: -1` (behind the backdrop) so the backdrop can partially occlude it — the sky fills any gaps the backdrop doesn't cover at extreme camera positions.

### D8: near_fg is fog-immune

Foreground elements at Z=-1 (distance 6 from camera) are well within the fog's `near: 20` threshold, so fog wouldn't affect them with these defaults. However, marking them `fogImmune: true` protects against manifest authors who override fog settings to more aggressive values — a near-fog of 5 would partially fog the foreground, which looks physically wrong (foreground elements should never fade as if distant).

### D9: This geometry is the reference for SKILL.md

As the simplest and most versatile geometry, `stage` is the one used in SKILL.md examples (OBJ-071). Every design choice prioritizes clarity and generality. The slot names, descriptions, and prompt guidance should be immediately understandable to an LLM reading the SKILL.md.

### D10: Size validation against frustum

All plane sizes are validated to be at least as large as the frustum visible area at their distance from the default camera position. The oversize factor varies per slot based on the expected camera motion range of `slow_push_forward` at `speed=1.0`. These specific sizes are starting points — OBJ-040 (edge-reveal validation) will verify them against actual camera path displacements, and OBJ-059 (visual tuning) will refine them based on Director Agent feedback.

## Acceptance Criteria

- [ ] **AC-01:** `stageGeometry.name` is `'stage'`.
- [ ] **AC-02:** `stageGeometry.slots` contains exactly 6 keys: `sky`, `backdrop`, `floor`, `midground`, `subject`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `backdrop`, `floor`, `subject` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `stageGeometry.default_camera` is `'slow_push_forward'`.
- [ ] **AC-05:** `stageGeometry.default_camera` appears in `stageGeometry.compatible_cameras`.
- [ ] **AC-06:** `stageGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (the two verified camera presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `stageGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'` or `'flyover_glide'`.
- [ ] **AC-08:** `stageGeometry.fog` is `{ color: '#000000', near: 20, far: 60 }`.
- [ ] **AC-09:** `stageGeometry.description` is non-empty and describes a subject-in-front-of-background setup.
- [ ] **AC-10:** `stageGeometry.preferred_aspect` is `'both'`.
- [ ] **AC-11:** The `floor` slot uses `PLANE_ROTATIONS.FLOOR` (`[-Math.PI/2, 0, 0]`) as its rotation.
- [ ] **AC-12:** All non-floor slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-13:** `subject` and `near_fg` have `transparent: true`. All other slots have `transparent: false`.
- [ ] **AC-14:** `sky` and `near_fg` have `fogImmune: true`. All other slots have `fogImmune: false`.
- [ ] **AC-15:** `renderOrder` values are strictly increasing from sky (-1) through near_fg (4), with no duplicates.
- [ ] **AC-16:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-17:** `registerGeometry(stageGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-18:** All slot `description` fields are non-empty strings.
- [ ] **AC-19:** All slot `size` components are positive (> 0).
- [ ] **AC-20:** Each slot's plane size (width and height) is >= the frustum visible dimension at that slot's distance from `DEFAULT_CAMERA.position` ([0, 0, 5]) with FOV=50° and aspect ratio 16:9. Specifically:
  - `sky` at distance 55: visible ~51.3 × 91.1 → size [120, 70] ✓
  - `backdrop` at distance 35: visible ~32.6 × 58.0 → size [75, 45] ✓
  - `floor` at distance ~8-13 (varies due to rotation): size [20, 40] extends well beyond the visible floor area.
  - `midground` at distance 20: visible ~18.6 × 33.2 → size [40, 25] ✓
  - `subject` at distance 10: visible ~9.3 × 16.6 → size [12, 12] (subject intentionally does NOT fill the full frame — it is a focal element, not a background).
  - `near_fg` at distance 6: visible ~5.6 × 9.9 → size [25, 16] ✓
- [ ] **AC-21:** Slot Z-positions decrease (go more negative) as depth increases: `near_fg` (-1) > `subject` (-5) > `floor` center (-10) > `midground` (-15) > `backdrop` (-30) > `sky` (-50).
- [ ] **AC-22:** The module self-registers via `registerGeometry(stageGeometry)` as a side effect of import.
- [ ] **AC-23:** The module exports `stageGeometry` as a named export.
- [ ] **AC-24:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants (`PLANE_ROTATIONS`).

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 3 required slots (`backdrop`, `floor`, `subject`) | Valid scene. Optional slots (`sky`, `midground`, `near_fg`) are simply absent — no planes created for them. The backdrop fills the background; floor provides perspective; subject is the focal point. |
| Manifest provides all 6 slots | Valid scene. Full depth layering with maximum visual richness. |
| Manifest provides an unknown slot key (e.g., `ceiling`) | Rejected by manifest validation (OBJ-017) — `ceiling` is not in the stage geometry's slot set. |
| Manifest uses `back_wall` instead of `backdrop` | Rejected — the stage uses `backdrop`, not the default taxonomy's `back_wall`. Error message should suggest the valid slot names. |
| Camera pushes forward far enough that `near_fg` clips the near plane | Near-plane clipping is a camera path responsibility (OBJ-027/OBJ-040). The `near_fg` at Z=-1 with camera starting at Z=5 has 6 units of clearance. A `slow_push_forward` with 25-unit Z displacement would bring the camera to Z=-20, moving it well past `near_fg`. Camera paths must limit their Z displacement to avoid passing through foreground planes. |
| Portrait mode (9:16) | The geometry renders correctly but backdrop width (75) may need to be larger relative to the narrower visible width. Since 9:16 flips the aspect, visible width at distance 35 becomes ~18.4 (much narrower), and 75 >> 18.4, so the backdrop is safe. The floor width of 20 exceeds 9:16 visible width at floor distance. Subject height of 12 needs checking against 9:16 visible height at distance 10: ~16.6 — subject fits. OBJ-040 validates this formally. |
| Floor plane visibility from above | If the camera has no downward tilt (lookAt.y >= camera.y), the floor might not be visible. With camera at [0, 0, 5] looking at [0, 0, 0], the floor at Y=-3 is below the look-at line, so the lower portion of the frustum reveals the floor. Camera paths that crane upward should maintain a lookAt with negative Y component to keep the floor visible. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `stage.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'stage' is already registered." The module should guard against double-registration using a module-level flag or rely on Node.js module caching (single execution). |
| `stage.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'stage': registry is locked." This is an initialization ordering error — geometry modules must be imported before any registry reads. |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `stageGeometry.name` is `'stage'`.
2. `stageGeometry.slots` has exactly 6 keys.
3. Required slots: `backdrop`, `floor`, `subject`. Optional: `sky`, `midground`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'slow_push_forward'` and is in `compatible_cameras`.
6. `compatible_cameras` is non-empty, all entries match `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` matches hex pattern.
8. `description` is non-empty.
9. `preferred_aspect` is `'both'`.

**Slot spatial correctness tests:**
10. `floor` slot rotation matches `PLANE_ROTATIONS.FLOOR` exactly.
11. All non-floor slots have rotation `[0, 0, 0]`.
12. Z-positions are ordered from nearest (near_fg: -1) to deepest (sky: -50).
13. `renderOrder` values are strictly ordered: sky < backdrop < floor < midground < subject < near_fg.
14. All `size` components are > 0.

**Slot metadata tests:**
15. `subject.transparent` is `true`; `near_fg.transparent` is `true`.
16. `backdrop.transparent` is `false`; `floor.transparent` is `false`.
17. `sky.fogImmune` is `true`; `near_fg.fogImmune` is `true`.
18. `backdrop.fogImmune` is `false`; `subject.fogImmune` is `false`.
19. All slot `description` fields are non-empty.

**OBJ-005 validation integration test:**
20. `validateGeometryDefinition(stageGeometry)` returns an empty error array.
21. `registerGeometry(stageGeometry)` does not throw (when registry is not locked).
22. After registration, `getGeometry('stage')` returns the stage geometry.

**Frustum size validation tests:**
23. For each non-subject, non-floor slot: verify that slot `size[0]` >= frustum visible width and `size[1]` >= frustum visible height at the slot's distance from `DEFAULT_CAMERA.position`, with FOV=50° and aspect 16:9. (Subject is intentionally smaller than the full frustum.)
24. `floor` slot: verify that `size[0]` (width) >= frustum visible width at the nearest visible floor distance.

**Compatible cameras tests:**
25. `compatible_cameras` includes `'static'`, `'slow_push_forward'`, `'gentle_float'`.
26. `compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`.

### Relevant Testable Claims

- **TC-01** (partial): The stage geometry uses 6 slots (3 required, 3 optional), within the 3-5 effective range. This single geometry should handle a large percentage of common "subject + background" video scenes.
- **TC-04** (partial): The stage geometry defines all spatial relationships — an LLM specifies `geometry: 'stage'` and fills slot names. No XYZ coordinates needed in the manifest.
- **TC-08** (partial): The stage geometry is one of the 8 proposed geometries. Its flexibility (general-purpose subject+background) should cover the most topics of any single geometry.

## Integration Points

### Depends on

| Upstream | What OBJ-018 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types for the geometry definition. `registerGeometry` function for self-registration. `validateGeometryDefinition` (used indirectly — `registerGeometry` calls it). |
| **OBJ-007** (Depth model) | `DepthSlot` type contract. `DEFAULT_SLOT_TAXONOMY` for reference values (sky, midground, subject, near_fg sizes). Slot naming conventions. |
| **OBJ-003** (Spatial math) | `PLANE_ROTATIONS.FLOOR` constant for the floor slot rotation. `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. |

### Consumed by

| Downstream | How it uses OBJ-018 |
|------------|---------------------|
| **OBJ-059** (Stage visual tuning) | The Director Agent reviews test renders of the stage geometry and provides feedback on slot positions, sizes, fog settings, and camera compatibility. OBJ-059 may adjust numerical values in the slot definitions. |
| **OBJ-069** (Edge-reveal tuning) | Validates that no compatible camera path reveals plane edges with the stage's slot sizes. May require size adjustments. |
| **OBJ-070** (End-to-end scene render test) | Uses the stage geometry as the first geometry in an end-to-end render pipeline test. |
| **OBJ-071** (SKILL.md) | Uses the stage geometry as the primary example in SKILL.md — slot names, descriptions, and prompt guidance are surfaced to LLM authors. |
| **OBJ-017** (Manifest structural validation) | After registration, manifest validation can look up `getGeometry('stage')` and validate that a manifest's `planes` keys match the stage's slot names. |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('stage')` to resolve slot spatial data when rendering a scene with `geometry: 'stage'`. |
| **OBJ-039** (Page-side renderer) | Reads slot `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune` to create Three.js meshes. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        stage.ts          # stageGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./stage
```

## Open Questions

### OQ-A: Should `floor` size be dynamically computed from camera push range?

The floor's size (`[20, 40]`) is a heuristic. The 40-unit depth extent should be validated against the maximum Z displacement of `slow_push_forward` — if the camera pushes 25 units forward, the floor needs to extend at least 25 units behind the camera's furthest position. Currently the floor extends from Y=-3 (position) with 40 units of depth (after rotation), reaching from roughly Z=10 to Z=-30 along the Z-axis. This should be sufficient for a 25-unit camera push starting at Z=5 (camera reaches Z=-20, floor extends to Z=-30).

**Recommendation:** Keep as a static value. Validate during OBJ-059 tuning. If the floor edge is visible at maximum camera push, increase the depth extent.

### OQ-B: Should `midground` support multiple instances?

The seed (OQ-08) asks whether geometries should support dynamic plane counts — e.g., 2-3 midground planes at varying Z-depths. The stage geometry defines a single `midground` slot.

**Recommendation:** Defer to OBJ-080 (dynamic plane count). For V1, a single midground slot is sufficient. If multiple depth layers are needed, the LLM can use the `diorama` geometry instead.

### OQ-C: Should `subject` be Y-centered or offset?

Currently at Y=-0.5. This places it slightly below center — a compositional choice. An alternative is Y=0 (centered) which is more neutral. The offset works well for subjects that appear "grounded" on the floor, but floating subjects (e.g., a planet, a logo) might look better centered.

**Recommendation:** Keep Y=-0.5 as default. Authors can override via `PlaneOverride.position` in the manifest for floating subjects. This is exactly the escape hatch that AP-08 and OBJ-007 provide.

---

I believe this specification is complete. It defines all 6 slots with precise spatial values, justifies each design choice against the seed and dependency contracts, provides testable acceptance criteria, and maps integration points clearly. I'm asking the Challenger to review and identify any gaps, ambiguities, or constraint violations.

---

## Round 2 — spec_challenger

I've read the proposed spec carefully. Let me check a few things against the dependency specs before rendering my verdict.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": 1,
  "limit": 120
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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": 1,
  "limit": 80
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
  "offset": 80,
  "limit": 40
}
[Tool Result]     80→
    81→  /**
    82→   * Whether this plane's material should be created with
    83→   * transparent: true and expect an alpha channel in its texture.
    84→   * When true, the renderer uses alpha blending.
    85→   * When false, the texture is treated as fully opaque.
    86→   *
    87→   * Defaults to false. Typically true for subject and near_fg slots.
    88→   */
    89→  transparent?: boolean;
    90→
    91→  /**
    92→   * Whether this plane should be excluded from fog calculations.
    93→   * When true, the plane uses meshBasicMaterial regardless of scene fog,
    94→   * ensuring it renders at full brightness/opacity regardless of distance.
    95→   *
    96→   * Defaults to false. Typically true only for sky/backdrop planes
    97→   * that should remain vivid at extreme distances.
    98→   */
    99→  fogImmune?: boolean;
   100→}
   101→
   102→/**
   103→ * A complete scene geometry definition — the 3D spatial structure
   104→ * of a scene type. Each geom... [truncated]
Now let me check what OBJ-007's `DepthSlot` looks like versus OBJ-005's `PlaneSlot` — since the spec claims to import from both:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/output.md",
  "offset": 1,
  "limit": 100
}
[Tool Result]      1→# Specification: Depth Model — Semantic Slot Taxonomy and Override System (OBJ-007)
     2→
     3→## Summary
     4→
     5→OBJ-007 defines the **depth model**: the semantic mapping from named slot labels to 3D spatial transforms (position, rotation, size) that scene geometries use to place planes in the Three.js scene. It establishes a **default slot taxonomy** (sky, back_wall, midground, subject, near_fg) with default Z-positions per seed Section 4.1, defines the **rules and types that govern per-geometry slot sets** (e.g., tunnel uses floor/ceiling/walls instead of the default taxonomy), and specifies the **`PlaneOverride` escape hatch** in the manifest for per-scene spatial tweaks without hard-coding the depth model (AP-08). This module provides the slot contract that all scene geometries implement (OBJ-005) and that manifest validation (OBJ-010) enforces.
     6→
     7→## Interface Contract
     8→
     9→### Core Types
    10→
    11→```typescript
    12→// src/spatial/d... [truncated]
Good, I now have a clear picture of the type landscape. Here's my review.

---

## Challenger Review — OBJ-018 Round 2

### What's Sound

The overall structure is solid. The 6-slot design with 3 required / 3 optional is well-reasoned. The floor-as-defining-element rationale (D1) is the right call. The slot spatial values are backed by frustum math. The compatible_cameras list is sensible. Fog settings are well-justified (D6). Design decisions D2-D9 are clear and defensible. The edge cases table covers the important scenarios.

I have **2 major** and **3 minor** issues.

---

### Issue 1: AC-20 Self-Contradiction (Major)

AC-20 states: *"Each slot's plane size (width and height) is >= the frustum visible dimension"* — then immediately shows `subject` at size `[12, 12]` with frustum visible width ~16.6, and says *"(subject intentionally does NOT fill the full frame — it is a focal element, not a background)"*.

The subject's width (12) is **less than** the visible width (16.6). AC-20 as written fails for subject. A tester reading this criterion literally would mark it as failed.

**Proposed fix:** Split AC-20 into two criteria:

- **AC-20a:** For slots intended as full-coverage planes (`sky`, `backdrop`, `midground`, `near_fg`), both size dimensions are >= the frustum visible dimensions at that slot's distance from `DEFAULT_CAMERA.position` with FOV=50° and aspect ratio 16:9.
- **AC-20b:** For the `subject` slot, the size is intentionally smaller than the full frustum — it is a focal element. Verify that `subject.size[1]` (height, 12) >= frustum visible height at distance 10 (~9.33), so the subject can fill the frame vertically. Width may be less than visible width. (The `floor` slot is exempt from this check because its rotated orientation makes frustum comparison non-trivial; edge-reveal safety is validated by OBJ-040.)

This makes both criteria pass/fail testable without hedging.

---

### Issue 2: Type Confusion — PlaneSlot vs DepthSlot in Dependencies (Major)

The "Depends on" table says OBJ-018 imports `DepthSlot type contract` from OBJ-007. But `SceneGeometry.slots` (from OBJ-005) is `Record<string, PlaneSlot>`, not `Record<string, DepthSlot>`. These are **structurally different interfaces**:

- `PlaneSlot` (OBJ-005): extends `PlaneTransform`, adds `required`, `description`, `renderOrder?`, `transparent?`, `fogImmune?`. No `name`, no `promptGuidance`, no `expectsAlpha`.
- `DepthSlot` (OBJ-007): has `name`, `position`, `rotation`, `size`, `required`, `description`, `promptGuidance`, `expectsAlpha`, `renderOrder`. No `transparent`, no `fogImmune`.

The spec's slot definitions match `PlaneSlot`, not `DepthSlot`. This is correct — `registerGeometry()` requires `SceneGeometry` which requires `PlaneSlot` objects. But the dependency table is misleading. An implementer might try to construct `DepthSlot` objects and then wonder why `transparent` and `fogImmune` aren't in the type.

**Proposed fix:**

1. In the "Depends on" table, change the OBJ-007 row to: *"Slot naming conventions (`SLOT_NAME_PATTERN`, `isValidSlotName`). `DEFAULT_SLOT_TAXONOMY` for reference sizes (not directly used as slot objects — `DEFAULT_SLOT_TAXONOMY` contains `DepthSlot` objects; the stage geometry constructs `PlaneSlot` objects per OBJ-005)."* Remove the claim of importing `DepthSlot type contract`.

2. Add a brief design decision (or note in D1) clarifying the relationship: "The stage geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, not `DepthSlot` objects (OBJ-007's type). `DepthSlot` fields like `promptGuidance` and `expectsAlpha` are surfaced via OBJ-007's `DEFAULT_SLOT_TAXONOMY` for SKILL.md generation (OBJ-071) and asset pipeline (OBJ-053), not via the geometry registration."

This matters because OBJ-007's "Consumed by" table says individual geometries import `DepthSlot` and `SlotSet`, which is inaccurate for how registration actually works. OBJ-018 should be precise about which type it actually constructs, so that it doesn't propagate the confusion to OBJ-019 through OBJ-025.

---

### Issue 3: Forward-Reference Camera Presets Not Flagged (Minor)

`compatible_cameras` lists 8 presets. Only 2 are verified (OBJ-026 `static`, OBJ-031 `gentle_float`). The other 6 (`slow_push_forward`, `slow_pull_back`, `lateral_track_left`, `lateral_track_right`, `dramatic_push`, `crane_up`) reference OBJ-027–OBJ-034, most of which are `open` status.

OBJ-005 D7 says these are string references resolved downstream by OBJ-041. So the strings are fine. But the spec should explicitly note these are forward references to unverified presets, so that:
- The implementer knows the list may change as those presets are specified.
- OBJ-059 (visual tuning) knows which cameras need validation.

**Proposed fix:** Add a sentence in D5 or a note after the `compatible_cameras` value: *"Of these, `static` (OBJ-026) and `gentle_float` (OBJ-031) are verified. The remaining 6 are forward references to presets in OBJ-027 through OBJ-034 (open/in-progress). The list may be revised as those presets are specified and OBJ-041 validates compatibility."*

---

### Issue 4: Slot Definitions Missing Explicit Field Listing per PlaneSlot Interface (Minor)

The slot definition tables show `position`, `rotation`, `size`, `required`, `description`, `renderOrder`, `transparent`, `fogImmune`. But `PlaneSlot` extends `PlaneTransform` which is `{position: Vec3; rotation: EulerRotation; size: Size2D}`. The optional fields on `PlaneSlot` are `renderOrder?`, `transparent?`, `fogImmune?`.

For slots where `transparent: false` and `fogImmune: false` (backdrop, floor, midground), should the implementation explicitly set these fields, or omit them (relying on the renderer's default behavior per OBJ-005 which says "Defaults to false")?

This is technically an implementation choice, but since the spec is the reference implementation for all 8 geometries, it should be explicit.

**Proposed fix:** Add a note: *"All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — no fields are omitted to rely on renderer defaults. This makes the geometry definition self-documenting and ensures consistent behavior regardless of how the renderer interprets absent optional fields."*

---

### Issue 5: Floor Frustum Validation in AC-20 is Untestable (Minor)

AC-20's floor entry says: *"floor at distance ~8-13 (varies due to rotation): size [20, 40] extends well beyond the visible floor area."* This is not a pass/fail criterion — "extends well beyond" is vague and the distance range is approximate.

**Proposed fix:** Either:
(a) Exempt floor from AC-20 explicitly (as I suggested in the AC-20 fix above) with a note that OBJ-040 handles edge-reveal validation for rotated planes, or
(b) State a specific testable claim: *"Floor width (20) >= frustum visible width at the closest floor-to-camera distance when camera is at DEFAULT_CAMERA.position (floor Y=-3, camera Y=0, so vertical distance = 3; the closest visible floor point is approximately 3/tan(25°) ≈ 6.4 units away on the Z-axis; frustum visible width at distance 6.4 ≈ 11.9; 20 > 11.9 ✓)."*

I prefer option (a) — exempting floor and deferring to OBJ-040 — because the rotated-plane frustum math is genuinely complex and is exactly OBJ-040's job.

---

### Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | AC-20 self-contradiction (subject fails its own criterion) | Major | Needs fix |
| 2 | PlaneSlot vs DepthSlot type confusion in dependency table | Major | Needs fix |
| 3 | Forward-reference camera presets not flagged | Minor | Needs fix |
| 4 | Explicit field setting policy for optional PlaneSlot fields | Minor | Needs fix |
| 5 | Floor frustum validation is untestable | Minor | Addressed by Issue 1 fix |

Please revise the spec addressing issues 1-4 (issue 5 is resolved by the AC-20 split in issue 1). I'll verify the fixes before converging.

---

## Round 3 — spec_author

All four issues are valid. Here's the revised spec with targeted fixes.

---

# Specification: Stage Scene Geometry (OBJ-018) — Revised

## Summary

OBJ-018 defines the **stage** scene geometry — the default, most fundamental geometry in depthkit. It represents a classic "subject in front of a background" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/stage.ts

import type { SceneGeometry } from './types';

/**
 * The stage scene geometry — the default geometry for depthkit.
 *
 * Spatial arrangement: a large backdrop plane at deep Z, a floor
 * plane angled down from the camera (FLOOR rotation), and a
 * subject plane at shallow Z. Optional sky, midground, and
 * near_fg planes provide additional depth layering.
 *
 * Classic "subject in front of a background" setup with real
 * perspective on the floor. The floor's perspective foreshortening
 * as the camera pushes forward is the primary 2.5D effect.
 *
 * This is the most commonly used geometry and the basis for
 * SKILL.md examples.
 */
export const stageGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'stage'` | Matches seed Section 4.2 naming |
| `description` | `'A classic subject-in-front-of-background setup. Large backdrop at depth, angled floor plane with real perspective foreshortening, and a subject plane at shallow Z. The most versatile geometry for general-purpose scenes.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes in or drifts laterally." Forward push is the defining 2.5D motion. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'lateral_track_left', 'lateral_track_right', 'gentle_float', 'dramatic_push', 'crane_up']` | Stage supports most camera motions except geometry-specific ones (tunnel_push_forward, flyover_glide). See D5 for exclusion rationale and forward-reference note. |
| `fog` | `{ color: '#000000', near: 20, far: 60 }` | Subtle atmospheric fade on distant planes. `near: 20` leaves the subject (Z=-5, ~10 units from camera) completely unaffected. `far: 60` fades the sky plane gently. |
| `preferred_aspect` | `'both'` | Stage works in landscape and portrait — plane sizes are designed for 16:9 but are oversized enough for 9:16 with camera-default FOV. |

### Slot Definitions

The stage geometry defines **6 slots** — 3 required, 3 optional. This follows the standard layered depth arrangement from seed Section 4.1 but adds a `floor` slot (which is not in the default taxonomy) for the perspective-foreshortened ground plane.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate camera motion at `speed=1.0` for the default camera (`slow_push_forward`).

The stage geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, **not** `DepthSlot` objects (OBJ-007's type). `DepthSlot` fields like `promptGuidance` and `expectsAlpha` are surfaced via OBJ-007's `DEFAULT_SLOT_TAXONOMY` for SKILL.md generation (OBJ-071) and the asset pipeline (OBJ-053), not via geometry registration. The `PlaneSlot` type extends `PlaneTransform` (position, rotation, size) and adds `required`, `description`, and optional `renderOrder`, `transparent`, `fogImmune`.

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are **explicitly set on every slot** — no fields are omitted to rely on renderer defaults. This makes the geometry definition self-documenting and ensures consistent behavior regardless of how the renderer interprets absent optional fields. This convention should be followed by all geometry implementations (OBJ-019 through OBJ-025).

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -30]` | Deep Z, serves as primary background. Distance from camera: 35 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane facing the camera. |
| `size` | `[75, 45]` | Oversized to prevent edge reveals during camera push. Frustum visible area at distance 35: ~32.6 × 58.0 (16:9). Oversized ~1.3× horizontally, ~1.38× vertically, accommodating ±5 unit Z push + lateral drift. |
| `required` | `true` | Every stage scene needs a background. |
| `description` | `'Primary background — landscape, environment, or atmospheric backdrop.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backgrounds are opaque. |
| `fogImmune` | `false` | Fades naturally with distance. |

#### Slot: `sky`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 5, -50]` | Very deep Z, raised slightly above center to fill the upper portion of the frame behind the backdrop. Distance from camera: 55 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[120, 70]` | Matches `DEFAULT_SLOT_TAXONOMY.sky`. Massively oversized for this distance — provides safety margin for all camera motions. |
| `required` | `false` | Optional — many stage scenes work with just a backdrop. Useful when the backdrop doesn't fill the full frame at all camera positions, or for a sky gradient visible above the backdrop. |
| `description` | `'Distant sky or gradient visible behind the backdrop. Use when the backdrop does not fill the entire frame.'` | |
| `renderOrder` | `-1` | Renders behind the backdrop. (Negative renderOrder is valid in Three.js.) |
| `transparent` | `false` | Sky planes are opaque. |
| `fogImmune` | `true` | Sky should remain vivid at extreme distance — fog would make it invisible. |

#### Slot: `floor`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -3, -10]` | Below the camera, centered in Z between camera and backdrop. Y=-3 positions the floor plane below the frame center; the `FLOOR` rotation makes it extend away from the camera. |
| `rotation` | `[-Math.PI / 2, 0, 0]` | `PLANE_ROTATIONS.FLOOR` — lies flat, faces up. This is the key plane that produces perspective foreshortening as the camera moves forward. |
| `size` | `[20, 40]` | Width=20 fills the horizontal view at floor level. Height=40 (depth extent, since the plane is rotated) extends from near the camera to behind the backdrop, preventing the floor from ending visibly. |
| `required` | `true` | The floor plane is the defining spatial element of the stage geometry — without it, there's no perspective reference and the scene reads as flat. |
| `description` | `'Ground surface — the floor plane that provides perspective foreshortening. The defining spatial element of the stage geometry.'` | |
| `renderOrder` | `1` | Renders above the backdrop. |
| `transparent` | `false` | Floors are opaque. |
| `fogImmune` | `false` | Distant portions of the floor fade naturally — enhances depth illusion. |

#### Slot: `midground`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -1, -15]` | Between backdrop and subject. Slightly below center to sit on the floor plane visually. Distance from camera: 20 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[40, 25]` | Matches `DEFAULT_SLOT_TAXONOMY.midground`. Oversized for camera motion. |
| `required` | `false` | Optional — adds depth layering but many stage scenes work fine without it. |
| `description` | `'Middle-distance element — buildings, terrain, or environmental props between backdrop and subject.'` | |
| `renderOrder` | `2` | Renders above floor. |
| `transparent` | `false` | Midground elements are typically opaque full-width environmental elements. |
| `fogImmune` | `false` | Fades with distance. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -0.5, -5]` | Shallow Z, slightly below center to appear grounded on the floor. Distance from camera: 10 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[12, 12]` | Sized to fill roughly 50-65% of the frame height at this distance. Frustum visible height at distance 10: ~9.33 units. 12/9.33 ≈ 1.29× — provides margin without overwhelming the frame. Square default accommodates both portrait and landscape subject images via texture aspect-ratio auto-sizing (OBJ-040). The subject is intentionally smaller than the full frustum visible width (~16.6) — it is a focal element, not a full-frame background. |
| `required` | `true` | The subject is the focal point of every stage scene. |
| `description` | `'Primary subject — person, animal, object, or focal element. Should be generated with a transparent background.'` | |
| `renderOrder` | `3` | Renders above midground. |
| `transparent` | `true` | Subject images need alpha transparency to avoid rectangular edges (seed OQ-02, Section 4.8). |
| `fogImmune` | `false` | Subject is close enough that fog has minimal effect with default fog settings (near=20 > distance 10). |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -1]` | Very close to camera. Distance from camera: 6 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[25, 16]` | Oversized to fill the frame edge-to-edge at close range. Frustum visible area at distance 6: ~5.60 × 9.95. Dramatically oversized because foreground elements typically extend beyond the frame (particles, foliage edges). |
| `required` | `false` | Optional — adds foreground framing but many scenes work without it. |
| `description` | `'Foreground framing element — foliage, particles, bokeh, or decorative edges. Should have a transparent background.'` | |
| `renderOrder` | `4` | Renders on top of everything. |
| `transparent` | `true` | Foreground elements need alpha to not occlude the subject. |
| `fogImmune` | `true` | Foreground is so close that any fog application would look wrong — fog represents atmospheric distance, and near_fg is the opposite of distant. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `sky` | `[0, 5, -50]` | `[0, 0, 0]` | `[120, 70]` | no | no | **yes** | -1 |
| `backdrop` | `[0, 0, -30]` | `[0, 0, 0]` | `[75, 45]` | **yes** | no | no | 0 |
| `floor` | `[0, -3, -10]` | `[-π/2, 0, 0]` | `[20, 40]` | **yes** | no | no | 1 |
| `midground` | `[0, -1, -15]` | `[0, 0, 0]` | `[40, 25]` | no | no | no | 2 |
| `subject` | `[0, -0.5, -5]` | `[0, 0, 0]` | `[12, 12]` | **yes** | yes | no | 3 |
| `near_fg` | `[0, 0, -1]` | `[0, 0, 0]` | `[25, 16]` | no | yes | no | 4 |

### Registration Side Effect

```typescript
// src/scenes/geometries/stage.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(stageGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/stage.ts
export { stageGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./stage` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Six slots — the default taxonomy plus `floor`

The seed's default depth taxonomy (Section 4.1) has 5 slots: `sky`, `back_wall`, `midground`, `subject`, `near_fg`. The stage geometry uses `backdrop` instead of `back_wall` (more descriptive for a stage's flat background), drops `sky` to optional, and **adds `floor`** — a horizontal plane with `FLOOR` rotation that provides perspective foreshortening. This is the core visual feature that distinguishes 2.5D from flat parallax.

Six slots falls within the 3-5 range that TC-01 considers sufficient for 90% of cases (the count is at the upper bound, but `sky` and `near_fg` are optional, so the minimum working scene uses 3: `backdrop`, `floor`, `subject`).

**Rationale:** Without the floor, a stage scene is just layered flat images — no better than 2D parallax. The floor plane, undergoing perspective distortion as the camera pushes forward, is what produces the "real 3D space" illusion that is depthkit's value proposition.

### D2: Floor position and size

The floor plane is at `Y=-3` (below the frame center) with `FLOOR` rotation and a size of `[20, 40]`. The 40-unit depth extent (measured along the Z-axis after rotation) ensures the floor extends from near the camera all the way past the backdrop.

The floor's Y-position of -3 was chosen so that with the default camera at `[0, 0, 5]` looking at `[0, 0, 0]`, the floor is visible in the lower portion of the frame. The perspective convergence point is roughly where the floor meets the backdrop plane, creating a natural vanishing effect.

**Trade-off:** Raising the floor (e.g., Y=-2) shows more floor area but pushes the subject higher in the frame. Lowering it (Y=-4) reduces visible floor but gives the subject more room. Y=-3 is a starting point for visual tuning (OBJ-059).

### D3: `backdrop` instead of `back_wall`

The seed's reserved slot name `back_wall` implies a vertical surface in an enclosed space. A stage's primary background is more often an open landscape, gradient, or scene — `backdrop` better communicates its role. This follows OBJ-005's convention that geometries may define custom slot names beyond the reserved set.

### D4: Subject at Y=-0.5 (slightly below center)

The subject is positioned 0.5 units below the Y-axis center. This places the subject's visual center at roughly the lower third of the frame — a classic photographic/cinematographic composition rule. Combined with the floor at Y=-3, the subject appears to "stand on" the floor.

### D5: Compatible cameras — exclusions and forward references

The stage excludes `tunnel_push_forward` (tuned for enclosed corridor geometries) and `flyover_glide` (requires a below-camera ground plane — stage's floor extends *away* from the camera, not *below* it). `panorama` rotation doesn't work because the backdrop is a flat plane — panning would reveal its edge immediately.

`dolly_zoom` is excluded from the initial compatible list because it requires careful FOV range coordination with plane sizes. It can be added after tuning (OBJ-059) validates edge-reveal safety.

**Forward reference note:** Of the 8 listed presets, `static` (OBJ-026) and `gentle_float` (OBJ-031) are verified. The remaining 6 (`slow_push_forward`, `slow_pull_back`, `lateral_track_left`, `lateral_track_right`, `dramatic_push`, `crane_up`) are forward references to presets in OBJ-027 through OBJ-034 (open/in-progress). The `compatible_cameras` list may be revised as those presets are specified and OBJ-041 validates compatibility.

### D6: Fog settings: near=20, far=60

Fog `near: 20` ensures the subject (distance ~10 units from camera) and floor (nearest portion ~8 units) are fully clear. Fog begins to fade the midground (distance ~20) very slightly and progressively fades the backdrop (distance ~35) and sky (distance ~55). `far: 60` means the sky is nearly fully fogged — which is why the sky slot is `fogImmune: true`, preventing it from disappearing.

Black fog (`#000000`) creates a cinematic depth fade. Scene authors can override to match their scene's mood via the manifest's fog override (per OBJ-005's fog contract).

### D7: Sky slot is fog-immune and has negative renderOrder

The sky at Z=-50 would be nearly invisible with fog (near=20, far=60). Marking it `fogImmune: true` ensures it renders at full brightness. It renders at `renderOrder: -1` (behind the backdrop) so the backdrop can partially occlude it — the sky fills any gaps the backdrop doesn't cover at extreme camera positions.

### D8: near_fg is fog-immune

Foreground elements at Z=-1 (distance 6 from camera) are well within the fog's `near: 20` threshold, so fog wouldn't affect them with these defaults. However, marking them `fogImmune: true` protects against manifest authors who override fog settings to more aggressive values — a near-fog of 5 would partially fog the foreground, which looks physically wrong (foreground elements should never fade as if distant).

### D9: This geometry is the reference for SKILL.md

As the simplest and most versatile geometry, `stage` is the one used in SKILL.md examples (OBJ-071). Every design choice prioritizes clarity and generality. The slot names, descriptions, and prompt guidance should be immediately understandable to an LLM reading the SKILL.md.

### D10: Size validation — coverage planes vs focal planes

Plane sizes follow two different sizing rules depending on their role:

- **Coverage planes** (`sky`, `backdrop`, `midground`, `near_fg`): sized to fill the full frustum visible area at their distance, plus oversizing margin for camera motion. These must be >= the frustum visible dimensions to prevent edge reveals.
- **Focal planes** (`subject`): intentionally smaller than the full frustum. The subject is a focal element that occupies a portion of the frame, not a background that must fill it edge-to-edge. Its height (12) exceeds the frustum visible height at its distance (~9.33), ensuring it *can* fill the frame vertically, but its width (12) is less than the frustum visible width (~16.6) — this is intentional.
- **Rotated planes** (`floor`): frustum intersection is non-trivial due to the rotation. Edge-reveal safety for the floor is validated by OBJ-040, not by simple frustum-dimension comparison.

### D11: PlaneSlot construction, not DepthSlot

The stage geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration. `PlaneSlot` extends `PlaneTransform` from OBJ-003 and adds `required`, `description`, and optional `renderOrder`, `transparent`, `fogImmune`. This is distinct from OBJ-007's `DepthSlot`, which carries `name`, `promptGuidance`, `expectsAlpha`, and `renderOrder` but not `transparent` or `fogImmune`. The `DepthSlot` fields relevant to SKILL.md and asset generation (`promptGuidance`, `expectsAlpha`) are surfaced via OBJ-007's `DEFAULT_SLOT_TAXONOMY` for downstream consumers (OBJ-071, OBJ-053), not via geometry registration.

### D12: Explicit optional field policy

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — no fields are omitted to rely on renderer defaults. This makes the geometry definition self-documenting and ensures consistent behavior regardless of how the renderer interprets absent optional fields. This convention should be followed by all geometry implementations (OBJ-019 through OBJ-025).

## Acceptance Criteria

- [ ] **AC-01:** `stageGeometry.name` is `'stage'`.
- [ ] **AC-02:** `stageGeometry.slots` contains exactly 6 keys: `sky`, `backdrop`, `floor`, `midground`, `subject`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `backdrop`, `floor`, `subject` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `stageGeometry.default_camera` is `'slow_push_forward'`.
- [ ] **AC-05:** `stageGeometry.default_camera` appears in `stageGeometry.compatible_cameras`.
- [ ] **AC-06:** `stageGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (the two verified camera presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `stageGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'` or `'flyover_glide'`.
- [ ] **AC-08:** `stageGeometry.fog` is `{ color: '#000000', near: 20, far: 60 }`.
- [ ] **AC-09:** `stageGeometry.description` is non-empty and describes a subject-in-front-of-background setup.
- [ ] **AC-10:** `stageGeometry.preferred_aspect` is `'both'`.
- [ ] **AC-11:** The `floor` slot uses `PLANE_ROTATIONS.FLOOR` (`[-Math.PI/2, 0, 0]`) as its rotation.
- [ ] **AC-12:** All non-floor slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-13:** `subject` and `near_fg` have `transparent: true`. All other slots have `transparent: false`.
- [ ] **AC-14:** `sky` and `near_fg` have `fogImmune: true`. All other slots have `fogImmune: false`.
- [ ] **AC-15:** `renderOrder` values are strictly increasing from sky (-1) through near_fg (4), with no duplicates.
- [ ] **AC-16:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-17:** `registerGeometry(stageGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-18:** All slot `description` fields are non-empty strings.
- [ ] **AC-19:** All slot `size` components are positive (> 0).
- [ ] **AC-20:** For coverage slots (`sky`, `backdrop`, `midground`, `near_fg`), both size dimensions are >= the frustum visible dimensions at that slot's distance from `DEFAULT_CAMERA.position` ([0, 0, 5]) with FOV=50° and aspect ratio 16:9. Specifically:
  - `sky` at distance 55: visible ~51.3 × 91.1 → size [120, 70] ✓
  - `backdrop` at distance 35: visible ~32.6 × 58.0 → size [75, 45] ✓
  - `midground` at distance 20: visible ~18.6 × 33.2 → size [40, 25] ✓
  - `near_fg` at distance 6: visible ~5.6 × 9.9 → size [25, 16] ✓
- [ ] **AC-21:** For the `subject` slot (a focal element, not a coverage plane), `size[1]` (height, 12) >= frustum visible height at distance 10 (~9.33), ensuring the subject can fill the frame vertically. Width may be less than the frustum visible width.
- [ ] **AC-22:** The `floor` slot is exempt from frustum-dimension comparison due to its rotated orientation. Edge-reveal safety for the floor is validated by OBJ-040.
- [ ] **AC-23:** Slot Z-positions decrease (go more negative) as depth increases: `near_fg` (-1) > `subject` (-5) > `floor` center (-10) > `midground` (-15) > `backdrop` (-30) > `sky` (-50).
- [ ] **AC-24:** The module self-registers via `registerGeometry(stageGeometry)` as a side effect of import.
- [ ] **AC-25:** The module exports `stageGeometry` as a named export.
- [ ] **AC-26:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants (`PLANE_ROTATIONS`).
- [ ] **AC-27:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 3 required slots (`backdrop`, `floor`, `subject`) | Valid scene. Optional slots (`sky`, `midground`, `near_fg`) are simply absent — no planes created for them. The backdrop fills the background; floor provides perspective; subject is the focal point. |
| Manifest provides all 6 slots | Valid scene. Full depth layering with maximum visual richness. |
| Manifest provides an unknown slot key (e.g., `ceiling`) | Rejected by manifest validation (OBJ-017) — `ceiling` is not in the stage geometry's slot set. |
| Manifest uses `back_wall` instead of `backdrop` | Rejected — the stage uses `backdrop`, not the default taxonomy's `back_wall`. Error message should suggest the valid slot names. |
| Camera pushes forward far enough that `near_fg` clips the near plane | Near-plane clipping is a camera path responsibility (OBJ-027/OBJ-040). The `near_fg` at Z=-1 with camera starting at Z=5 has 6 units of clearance. Camera paths must limit their Z displacement to avoid passing through foreground planes. |
| Portrait mode (9:16) | The geometry renders correctly. In 9:16, visible width narrows significantly but all plane widths far exceed the narrower visible width. OBJ-040 validates this formally. |
| Floor plane visibility from above | If the camera has no downward tilt (lookAt.y >= camera.y), the floor might not be visible. With camera at [0, 0, 5] looking at [0, 0, 0], the floor at Y=-3 is below the look-at line, so the lower portion of the frustum reveals the floor. Camera paths that crane upward should maintain a lookAt with negative Y component to keep the floor visible. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `stage.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'stage' is already registered." The module should guard against double-registration using a module-level flag or rely on Node.js module caching (single execution). |
| `stage.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'stage': registry is locked." This is an initialization ordering error — geometry modules must be imported before any registry reads. |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `stageGeometry.name` is `'stage'`.
2. `stageGeometry.slots` has exactly 6 keys.
3. Required slots: `backdrop`, `floor`, `subject`. Optional: `sky`, `midground`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'slow_push_forward'` and is in `compatible_cameras`.
6. `compatible_cameras` is non-empty, all entries match `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` matches hex pattern.
8. `description` is non-empty.
9. `preferred_aspect` is `'both'`.

**Slot spatial correctness tests:**
10. `floor` slot rotation matches `PLANE_ROTATIONS.FLOOR` exactly.
11. All non-floor slots have rotation `[0, 0, 0]`.
12. Z-positions are ordered from nearest (near_fg: -1) to deepest (sky: -50).
13. `renderOrder` values are strictly ordered: sky < backdrop < floor < midground < subject < near_fg.
14. All `size` components are > 0.

**Slot metadata tests:**
15. `subject.transparent` is `true`; `near_fg.transparent` is `true`.
16. `backdrop.transparent` is `false`; `floor.transparent` is `false`.
17. `sky.fogImmune` is `true`; `near_fg.fogImmune` is `true`.
18. `backdrop.fogImmune` is `false`; `subject.fogImmune` is `false`.
19. All slot `description` fields are non-empty.
20. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
21. `validateGeometryDefinition(stageGeometry)` returns an empty error array.
22. `registerGeometry(stageGeometry)` does not throw (when registry is not locked).
23. After registration, `getGeometry('stage')` returns the stage geometry.

**Frustum size validation tests:**
24. For each coverage slot (`sky`, `backdrop`, `midground`, `near_fg`): verify that slot `size[0]` >= frustum visible width and `size[1]` >= frustum visible height at the slot's distance from `DEFAULT_CAMERA.position`, with FOV=50° and aspect 16:9.
25. For `subject`: verify `size[1]` >= frustum visible height at distance 10.
26. `floor` slot: exempt from direct frustum comparison (rotated plane — deferred to OBJ-040).

**Compatible cameras tests:**
27. `compatible_cameras` includes `'static'`, `'slow_push_forward'`, `'gentle_float'`.
28. `compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`.

### Relevant Testable Claims

- **TC-01** (partial): The stage geometry uses 6 slots (3 required, 3 optional), within the 3-5 effective range. This single geometry should handle a large percentage of common "subject + background" video scenes.
- **TC-04** (partial): The stage geometry defines all spatial relationships — an LLM specifies `geometry: 'stage'` and fills slot names. No XYZ coordinates needed in the manifest.
- **TC-08** (partial): The stage geometry is one of the 8 proposed geometries. Its flexibility (general-purpose subject+background) should cover the most topics of any single geometry.

## Integration Points

### Depends on

| Upstream | What OBJ-018 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types for the geometry definition. `registerGeometry` function for self-registration. `validateGeometryDefinition` (used indirectly — `registerGeometry` calls it). |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`, `isValidSlotName`). `DEFAULT_SLOT_TAXONOMY` for reference sizes (not directly used as slot objects — `DEFAULT_SLOT_TAXONOMY` contains `DepthSlot` objects; the stage geometry constructs `PlaneSlot` objects per OBJ-005). |
| **OBJ-003** (Spatial math) | `PLANE_ROTATIONS.FLOOR` constant for the floor slot rotation. `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. |

### Consumed by

| Downstream | How it uses OBJ-018 |
|------------|---------------------|
| **OBJ-059** (Stage visual tuning) | The Director Agent reviews test renders of the stage geometry and provides feedback on slot positions, sizes, fog settings, and camera compatibility. OBJ-059 may adjust numerical values in the slot definitions. |
| **OBJ-069** (Edge-reveal tuning) | Validates that no compatible camera path reveals plane edges with the stage's slot sizes. May require size adjustments. |
| **OBJ-070** (End-to-end scene render test) | Uses the stage geometry as the first geometry in an end-to-end render pipeline test. |
| **OBJ-071** (SKILL.md) | Uses the stage geometry as the primary example in SKILL.md — slot names, descriptions, and prompt guidance are surfaced to LLM authors. |
| **OBJ-017** (Manifest structural validation) | After registration, manifest validation can look up `getGeometry('stage')` and validate that a manifest's `planes` keys match the stage's slot names. |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('stage')` to resolve slot spatial data when rendering a scene with `geometry: 'stage'`. |
| **OBJ-039** (Page-side renderer) | Reads slot `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune` to create Three.js meshes. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        stage.ts          # stageGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./stage
```

## Open Questions

### OQ-A: Should `floor` size be dynamically computed from camera push range?

The floor's size (`[20, 40]`) is a heuristic. The 40-unit depth extent should be validated against the maximum Z displacement of `slow_push_forward` — if the camera pushes 25 units forward, the floor needs to extend at least 25 units behind the camera's furthest position. Currently the floor extends from Y=-3 (position) with 40 units of depth (after rotation), reaching from roughly Z=10 to Z=-30 along the Z-axis. This should be sufficient for a 25-unit camera push starting at Z=5 (camera reaches Z=-20, floor extends to Z=-30).

**Recommendation:** Keep as a static value. Validate during OBJ-059 tuning. If the floor edge is visible at maximum camera push, increase the depth extent.

### OQ-B: Should `midground` support multiple instances?

The seed (OQ-08) asks whether geometries should support dynamic plane counts — e.g., 2-3 midground planes at varying Z-depths. The stage geometry defines a single `midground` slot.

**Recommendation:** Defer to OBJ-080 (dynamic plane count). For V1, a single midground slot is sufficient. If multiple depth layers are needed, the LLM can use the `diorama` geometry instead.

### OQ-C: Should `subject` be Y-centered or offset?

Currently at Y=-0.5. This places it slightly below center — a compositional choice. An alternative is Y=0 (centered) which is more neutral. The offset works well for subjects that appear "grounded" on the floor, but floating subjects (e.g., a planet, a logo) might look better centered.

**Recommendation:** Keep Y=-0.5 as default. Authors can override via `PlaneOverride.position` in the manifest for floating subjects. This is exactly the escape hatch that AP-08 and OBJ-007 provide.

---

## Changes from Round 1

Here's a summary of what changed to address the challenger's 4 issues:

**Issue 1 (AC-20 self-contradiction):** Split AC-20 into three criteria: **AC-20** for coverage planes (sky, backdrop, midground, near_fg), **AC-21** for the subject focal plane (height check only), and **AC-22** exempting the floor from frustum comparison (deferred to OBJ-040). Added **D10** (Size validation — coverage planes vs focal planes) to explain the sizing philosophy.

**Issue 2 (PlaneSlot vs DepthSlot type confusion):** Rewrote the OBJ-007 dependency row to clarify it provides slot naming conventions and reference sizes, not the construction type. Added **D11** explicitly documenting that the geometry constructs `PlaneSlot` objects (OBJ-005's type), not `DepthSlot` objects (OBJ-007's type). Added a paragraph at the top of the Slot Definitions section making this clear.

**Issue 3 (Forward-reference camera presets):** Added a forward-reference note to **D5** explicitly listing which presets are verified (static, gentle_float) and noting the remaining 6 are forward references to open/in-progress OBJs that may be revised.

**Issue 4 (Explicit optional field policy):** Added **D12** stating all optional `PlaneSlot` fields are explicitly set on every slot. Added **AC-27** as a testable criterion. Added test case #20 verifying no optional fields are `undefined`. Added a paragraph at the top of the Slot Definitions section establishing this convention for all geometry implementations.

---

I believe all four issues are now addressed. Challenger, please verify the fixes and approve if satisfied.

---

## Round 4 — spec_challenger

## Challenger Review — Round 4

I've verified all four fixes against the revised spec:

**Issue 1 (AC-20):** ✓ Confirmed. AC-20 now scopes to coverage slots only with explicit frustum values. AC-21 covers subject with height-only check. AC-22 exempts floor with OBJ-040 deferral. D10 documents the sizing philosophy. All three criteria are pass/fail testable.

**Issue 2 (PlaneSlot vs DepthSlot):** ✓ Confirmed. The OBJ-007 dependency row now correctly says "Slot naming conventions... `DEFAULT_SLOT_TAXONOMY` for reference sizes (not directly used as slot objects)." D11 explicitly documents the type distinction. The paragraph at the top of Slot Definitions makes the construction type clear.

**Issue 3 (Forward references):** ✓ Confirmed. D5's "Forward reference note" paragraph names the two verified presets and flags the remaining 6 as forward references with potential revision.

**Issue 4 (Explicit optional fields):** ✓ Confirmed. D12 states the policy. AC-27 makes it testable. Test case #20 verifies no `undefined` optional fields.

I've also verified the frustum math in AC-20 against the seed's formula (`visible_height = 2 × d × tan(FOV/2)`, `visible_width = visible_height × aspect_ratio`):
- sky @ d=55: 51.3h × 91.1w → [120, 70] ✓
- backdrop @ d=35: 32.6h × 58.0w → [75, 45] ✓  
- midground @ d=20: 18.6h × 33.2w → [40, 25] ✓
- near_fg @ d=6: 5.6h × 9.9w → [25, 16] ✓

No new issues introduced by the revisions. The spec is implementable, internally consistent, compliant with seed vocabulary and constraints, and integrates cleanly with OBJ-003, OBJ-005, and OBJ-007.

CONCLUSION:

The OBJ-018 Stage Scene Geometry specification is approved. It defines 6 slots (3 required: backdrop, floor, subject; 3 optional: sky, midground, near_fg), 8 compatible camera presets (2 verified, 6 forward-referenced), fog settings, and the complete spatial contract for the default depthkit geometry. All acceptance criteria are specific and testable. Type relationships with OBJ-005 (PlaneSlot) and OBJ-007 (naming conventions, reference sizes) are precisely documented.

Let me write the final spec and update meta.json.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "content": "# Specification: Stage Scene Geometry (OBJ-018)\n\n## Summary\n\nOBJ-018 defines the **stage** scene geometry \u2014 the default, most fundamental geometry in depthkit. It represents a classic \"subject in front of a background\" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.\n\n## Interface Contract\n\n### Exported Geometry Definition\n\n```typescript\n// src/scenes/geometries/stage.ts\n\nimport type { SceneGeometry } from './types';\n\n/**\n * The stage scene geometry \u2014 the default geometry for depthkit.\n *\n * Spatial arrangement: a large backdrop plane at deep Z, a floor\n * plane angled down from the camera (FLOOR rotation), and a\n * subject plane at shallow Z. Optional sky, midground, and\n * near_fg planes provide additional depth layering.\n *\n * Classic \"subject in front of a background\" setup with real\n * perspective on the floor. The floor's perspective foreshortening\n * as the camera pushes forward is the primary 2.5D effect.\n *\n * This is the most commonly used geometry and the basis for\n * SKILL.md examples.\n */\nexport const stageGeometry: SceneGeometry;\n```\n\n### Geometry Fields\n\n| Field | Value | Rationale |\n|-------|-------|-----------|\n| `name` | `'stage'` | Matches seed Section 4.2 naming |\n| `description` | `'A classic subject-in-front-of-background setup. Large backdrop at depth, angled floor plane with real perspective foreshortening, and a subject plane at shallow Z.
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md
Now update the meta.json:
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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json",
  "content": "{\n  \"id\": \"OBJ-018\",\n  \"description\": \"Stage scene geometry -- the default geometry. Large backdrop plane at z=-30, floor plane angled down from camera (rotation [-PI/2,0,0]), subject plane at z=-5. Classic 'subject in front of a background' setup with real perspective on the floor. Defines 6 slots (3 required: backdrop, floor, subject; 3 optional: sky, midground, near_fg), compatible cameras, default camera (slow_push_forward), and fog settings per Section 4.2. Addresses TC-01 (five planes sufficient).\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-005\", \"OBJ-007\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 geometry. The simplest, most fundamental geometry -- used as the basis for SKILL.md examples. Spec approved after 4-round deliberation. Constructs PlaneSlot objects (OBJ-005 type), not DepthSlot (OBJ-007 type). All optional PlaneSlot fields explicitly set.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json has been updated successfully.
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
[Tool Result] 7a64c90 spec(OBJ-008): transition type contract — cut, crossfade, dip_to_black
82035d9 spec(OBJ-009): virtualized clock and Puppeteer bridge specification
e320132 spec(OBJ-016): manifest loader and validator behavioral specification
baa00bf spec(OBJ-013): FFmpeg encoder specification -- approved after 4-round deliberation
306fe35 spec(OBJ-031): gentle_float camera path preset specification
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-018/meta.json

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
	nodes/OBJ-013/transcript.md
	nodes/OBJ-015/output.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-018/output.md
	nodes/OBJ-026/transcript.md
	nodes/OBJ-031/transcript.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-018/output.md nodes/OBJ-018/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-018): stage scene geometry -- default geometry with 6 slots\n\nDefines the stage geometry: backdrop (z=-30), floor (rotated, z=-10),\nsubject (z=-5), plus optional sky, midground, and near_fg planes.\n3 required / 3 optional slots, 8 compatible cameras, fog settings.\nApproved after 4-round deliberation resolving AC-20 frustum split,\nPlaneSlot vs DepthSlot type clarity, forward-reference flagging,\nand explicit optional field policy.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-018 spec files"
}
[Tool Result] [master af6acf5] spec(OBJ-018): stage scene geometry -- default geometry with 6 slots
 2 files changed, 391 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-018/output.md
OBJ-018 specification committed. The stage scene geometry spec defines:

- **6 slots**: 3 required (`backdrop`, `floor`, `subject`), 3 optional (`sky`, `midground`, `near_fg`)
- **8 compatible cameras**: `static`, `slow_push_forward`, `slow_pull_back`, `lateral_track_left`, `lateral_track_right`, `gentle_float`, `dramatic_push`, `crane_up`
- **Fog**: `{ color: '#000000', near: 20, far: 60 }`
- **27 acceptance criteria**, all pass/fail testable
- **12 design decisions** documenting rationale

Key deliberation outcomes:
1. AC-20 split into coverage planes vs focal planes vs rotated planes (3 separate criteria)
2. PlaneSlot (OBJ-005) vs DepthSlot (OBJ-007) type confusion resolved in dependency table and D11
3. Forward-reference camera presets flagged in D5
4. Explicit optional field policy established in D12 + AC-27
