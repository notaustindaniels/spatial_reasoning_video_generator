# Deliberation Transcript: OBJ-023

---

## Round 1 — spec_author

Looking at the objective metadata, dependencies (OBJ-005 geometry type contract, OBJ-007 depth model), and the seed's description of the portal geometry, I'll propose a complete specification.

Let me first check the existing geometry implementations for reference patterns:
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-018/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-02[0-2]/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-023/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-023/meta.json

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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md"
}
[Tool Error] File content (10808 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: Diorama Scene Geometry (OBJ-022)
     2→
     3→## Summary
     4→
     5→OBJ-022 defines the **diorama** scene geometry — a semicircle of upright planes arranged at varying Z-depths, like layers of a Victorian paper theater. The defining visual characteristic is that wing planes on the left and right sides are **slightly rotated inward**, creating a curved spatial envelope. As the camera pushes in gently, these angled wings exhibit real perspective foreshortening — their far edges visibly recede while their near edges stay closer — producing a richer depth illusion than flat parallel layers. This is the closest geometry to traditional parallax but distinguished by the perspective distortion on the outer planes. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/diorama.ts
    1... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: Flyover Scene Geometry (OBJ-021)
     2→
     3→## Summary
     4→
     5→OBJ-021 defines the **flyover** scene geometry — a spatial arrangement designed for aerial/bird's-eye perspective. A large ground plane lies below the camera (`FLOOR` rotation), a sky plane sits at extreme depth above, and optional landmark planes rise vertically from the ground at varying depths and lateral positions. The camera moves forward while positioned above the ground, producing an immersive "flying over terrain" effect where the ground plane undergoes strong perspective foreshortening and landmarks pass by on either side. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/flyover.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The flyover scene geometr... [truncated]
Now let me check the verified camera presets to know which ones to reference:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "limit": 55
}
[Tool Result]      1→# Specification: Canyon Scene Geometry (OBJ-020)
     2→
     3→## Summary
     4→
     5→OBJ-020 defines the **canyon** scene geometry — a narrow, vertically dramatic 3D space with tall wall planes on left and right, a floor plane, an open sky above, and an optional end wall at depth. The camera pushes forward through the canyon or floats upward to reveal vertical scale. This geometry produces the feeling of traveling through a narrow gorge, alley, corridor between tall buildings, or any space defined by towering vertical boundaries. It registers itself via `registerGeometry()` from OBJ-005 and defines its slot set per OBJ-007's depth model contract.
     6→
     7→## Interface Contract
     8→
     9→### Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/canyon.ts
    13→
    14→import type { SceneGeometry, PlaneSlot, FogConfig } from './types';
    15→import { registerGeometry } from './registry';
    16→```
    17→
    18→The module defines and ... [truncated]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-026/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-027/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-031/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "limit": 60
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md",
  "limit": 30
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
  "limit": 30
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
Now let me check OBJ-003 for spatial constants:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-003/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
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
Good. Now I have all the reference material I need. Let me compose the specification for OBJ-023 (Portal Scene Geometry).

---

# Specification: Portal Scene Geometry (OBJ-023)

## Summary

OBJ-023 defines the **portal** scene geometry — concentric frame planes at increasing Z-depth, creating a "looking through layers" effect like nested doorways, windows, or picture frames receding into depth. As the camera pushes forward, each frame fills the viewport and passes behind the camera, producing a dreamlike "traveling through portals" sensation. Every frame plane expects alpha transparency — the decorative border is opaque while the center is transparent, allowing deeper frames and the backdrop to show through. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/portal.ts

import type { SceneGeometry } from './types';

/**
 * The portal scene geometry — concentric frames at increasing Z-depth.
 *
 * Spatial arrangement: a deep backdrop plane visible through all
 * frames, three concentric frame planes (near, mid, far) at
 * increasing Z-depths, all facing the camera with transparent
 * centers. An optional subject plane sits between the mid and far
 * frames, and an optional near_fg provides foreground atmosphere.
 *
 * The defining visual effect is a "looking through nested portals"
 * sensation as the camera pushes forward. Each frame fills the
 * viewport momentarily, then passes behind the camera to reveal
 * the next frame and deeper layers. All frame planes require
 * images with alpha transparency (opaque border, transparent center).
 *
 * Best for transitions, dreamlike sequences, fantasy themes,
 * and abstract/artistic compositions.
 */
export const portalGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'portal'` | Matches seed Section 4.2 naming |
| `description` | `'Concentric frame planes at increasing Z-depth, like nested doorways or picture frames receding into the distance. Camera pushes through them for a dreamlike "traveling through portals" effect. Frame images should have transparent centers. Best for transitions, fantasy themes, and abstract compositions.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes through them." The forward push is the defining motion — it makes each frame fill and pass the viewport. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'gentle_float', 'dramatic_push']` | See D4. Excludes lateral tracks (would reveal frame edges laterally), tunnel_push_forward (tuned for enclosed corridor), flyover_glide (requires below-camera ground), crane_up (vertical motion misaligned with the concentric Z-axis arrangement). |
| `fog` | `{ color: '#0a0a14', near: 10, far: 55 }` | Very dark blue-black fog for dreamlike atmosphere. See D5. |
| `preferred_aspect` | `'both'` | Portal frames are centered and camera-facing — the concentric arrangement works in both 16:9 and 9:16. Frame images should be authored for the target aspect ratio but the geometry is structurally sound in either. |

### Slot Definitions

The portal geometry defines **6 slots** — 2 required, 4 optional. The backdrop and at least one frame provide the essential spatial structure; additional frames and foreground enhance the layered portal effect.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to ensure each frame fully fills the viewport at its distance from camera, so no frame edges are visible when the camera is far away.

Following the convention established by OBJ-018: the portal geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -45]` | Very deep Z — the final image visible through all frames. Distance from camera: 50 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA` — upright plane facing the camera. |
| `size` | `[110, 62]` | Oversized to fill the viewport at distance 50. Frustum visible area at distance 50: ~46.6h × 82.9w (16:9). Width 110 >= 82.9 (~1.33x oversize), height 62 >= 46.6 (~1.33x oversize). Large oversize because camera pushes forward significantly — at the farthest camera push position (z=-3, distance 42 from backdrop), visible area is ~39.2h × 69.7w, still well within the plane. |
| `required` | `true` | Every portal scene needs a final destination image visible through the nested frames. Without it, frames open onto nothing. |
| `description` | `'The deepest background — the destination visible through all portal frames. A complete scene or environment image.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backdrop is opaque — it fills the center of the deepest portal opening. |
| `fogImmune` | `true` | The backdrop at Z=-45 (distance 50) would be heavily fogged. Marking it fog-immune ensures the destination image remains visible through all frames — the visual promise of the portal is that there's something to reach. |

#### Slot: `frame_far`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -30]` | Deep Z, farthest frame. Distance from camera: 35 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[72, 42]` | Must fill the viewport at distance 35. Frustum visible area: ~32.6h × 58.0w. Width 72 >= 58.0 (~1.24x oversize), height 42 >= 32.6 (~1.29x oversize). Oversized to accommodate camera push — when camera reaches z=-3 (distance 27 from this frame), visible area is ~25.2h × 44.8w, still within the plane. |
| `required` | `false` | Optional — a portal scene can work with just `frame_near` and `backdrop`. However, three frames is the intended full effect. |
| `description` | `'Farthest portal frame — decorative border with transparent center. The smallest-appearing frame when viewed from the starting position.'` | |
| `renderOrder` | `1` | Renders above backdrop. |
| `transparent` | `true` | Frame images MUST have alpha — opaque decorative border, transparent center through which deeper frames and the backdrop are visible. |
| `fogImmune` | `false` | The subtle fog fading on distant frames enhances the sense of depth between layers. |

#### Slot: `frame_mid`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -15]` | Mid-depth. Distance from camera: 20 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[42, 24]` | Fills viewport at distance 20. Frustum visible area: ~18.6h × 33.1w. Width 42 >= 33.1 (~1.27x oversize), height 24 >= 18.6 (~1.29x oversize). When camera reaches z=-3 (distance 12), visible area is ~11.2h × 19.9w, still within plane. |
| `required` | `false` | Optional — enhances the layered effect. A portal can function with just one frame + backdrop. |
| `description` | `'Middle portal frame — decorative border with transparent center. Creates the key intermediate depth layer between near and far frames.'` | |
| `renderOrder` | `2` | Renders above frame_far. |
| `transparent` | `true` | Same alpha requirement as all frame slots. |
| `fogImmune` | `false` | At distance 20, fog begins to slightly affect this frame, creating gentle depth separation from `frame_near`. |

#### Slot: `frame_near`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -3]` | Shallow Z, closest frame to camera. Distance from camera: 8 units. The camera, starting at z=5 and pushing to z=-3, will approach and pass through this frame during a full `slow_push_forward` (camera reaches this frame's Z-position at the end of the push). |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[18, 11]` | Fills viewport at distance 8. Frustum visible area: ~7.5h × 13.3w. Width 18 >= 13.3 (~1.35x oversize), height 11 >= 7.5 (~1.47x oversize). Extra oversize because this is the frame the camera pushes through — at the moment of passing, any undersized edge would be dramatically visible. |
| `required` | `true` | The nearest frame is the most visually prominent — it creates the "entering the portal" sensation. Without at least one frame, there is no portal effect at all. |
| `description` | `'Nearest portal frame — the first frame the camera approaches and pushes through. Should be the most visually prominent and detailed frame. Decorative border with transparent center.'` | |
| `renderOrder` | `4` | Renders above subject and all other frames. Highest among frame slots. |
| `transparent` | `true` | Same alpha requirement as all frame slots. |
| `fogImmune` | `true` | At distance 8, fog should not affect the closest frame — it would look physically wrong for the nearest object to be hazed. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -20]` | Between `frame_mid` (z=-15) and `frame_far` (z=-30). Distance from camera: 25 units. Positioned so it's visible through the mid frame's transparent center. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[14, 14]` | Focal element — intentionally smaller than the full frustum visible area at this distance (~23.3h × 41.5w). Subject should occupy the center of the frame composition, not fill it edge-to-edge. Square default accommodates both portrait and landscape subject images via texture auto-sizing (OBJ-040). |
| `required` | `false` | Optional — many portal scenes are purely abstract/decorative without a specific subject. When included, the subject appears to float within the portal layers, drawing the eye to the center. |
| `description` | `'Optional focal element visible through the portal frames — a person, object, or symbol at the center of the composition. Should have a transparent background.'` | |
| `renderOrder` | `3` | Renders above frame_mid but below frame_near. The subject is visible through frame_near's transparent center and in front of frame_far. |
| `transparent` | `true` | Subject needs alpha to blend with the portal layers behind it. |
| `fogImmune` | `false` | Subject at distance 25 benefits from subtle fog — creates atmospheric depth separation from the frame_near. |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, 0]` | In front of `frame_near` (z=-3), very close to camera. Distance from camera: 5 units. Used for atmospheric particles, sparkles, mist, or light effects that drift between the viewer and the first portal frame. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[14, 9]` | Fills viewport at distance 5. Frustum visible area: ~4.7h × 8.3w. Width 14 >= 8.3 (~1.69x oversize), height 9 >= 4.7 (~1.91x oversize). Large oversize because the camera pushes toward this plane — at z=-3 (distance shrinks to 3 units), visible area narrows to ~2.8h × 5.0w, still within the plane. |
| `required` | `false` | Optional atmospheric enhancement. Many portal scenes work well without it. |
| `description` | `'Foreground atmospheric element — particles, sparkles, mist, or light effects between the viewer and the first portal frame. Should have a transparent background.'` | |
| `renderOrder` | `5` | Renders on top of everything. |
| `transparent` | `true` | Foreground atmospheric elements must be mostly transparent. |
| `fogImmune` | `true` | Foreground at distance 5 should never be fogged — fog represents atmospheric distance, and near_fg is the opposite of distant. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `backdrop` | `[0, 0, -45]` | `[0, 0, 0]` | `[110, 62]` | **yes** | no | **yes** | 0 |
| `frame_far` | `[0, 0, -30]` | `[0, 0, 0]` | `[72, 42]` | no | **yes** | no | 1 |
| `frame_mid` | `[0, 0, -15]` | `[0, 0, 0]` | `[42, 24]` | no | **yes** | no | 2 |
| `subject` | `[0, 0, -20]` | `[0, 0, 0]` | `[14, 14]` | no | **yes** | no | 3 |
| `frame_near` | `[0, 0, -3]` | `[0, 0, 0]` | `[18, 11]` | **yes** | **yes** | **yes** | 4 |
| `near_fg` | `[0, 0, 0]` | `[0, 0, 0]` | `[14, 9]` | no | **yes** | **yes** | 5 |

### Registration Side Effect

```typescript
// src/scenes/geometries/portal.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(portalGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/portal.ts
export { portalGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./portal` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Three frame slots at logarithmically-spaced Z-depths

The portal uses three frame planes at Z = -3, -15, -30. The spacing is roughly logarithmic from the camera: distances of 8, 20, 35 units. This creates a perceptual effect where the frames appear evenly spaced in depth — linear spacing would make the far frames appear clumped together due to perspective compression. The three-frame design follows the seed's description ("concentric frames/planes at increasing Z-depth") while keeping the slot count within the 3-5 effective range per TC-01.

**Alternative considered:** Four or five frame slots. Rejected because more frames increase the image generation burden on the LLM author and because the visual effect of "looking through portals" is already strong with three nested frames. Authors who need more layers can use `PlaneOverride` to reposition the optional frames or use the `diorama` geometry for a different layering approach.

### D2: All planes face the camera — no rotated slots

Unlike tunnel (walls/floor/ceiling with various rotations) or canyon (walls), the portal geometry has every plane at `[0, 0, 0]` rotation (`FACING_CAMERA`). This is the defining characteristic of the portal: it's purely about depth layers along the Z-axis, not about surrounding spatial structure. The depth illusion comes entirely from Z-spacing and perspective projection, not from rotated surfaces.

**Rationale:** The portal's visual identity is concentric frames receding into depth. Rotating any plane would break the concentric alignment and undermine the "looking through doorways" metaphor.

### D3: Only `backdrop` and `frame_near` are required

The minimum viable portal scene needs exactly two things: a destination visible through the portal (`backdrop`) and at least one frame to create the portal boundary (`frame_near`). The nearest frame is chosen as required (rather than `frame_far` or `frame_mid`) because it's the most visually impactful — it's what the camera approaches and pushes through, creating the defining "entering the portal" moment.

`frame_mid` and `frame_far` are optional enhancements that add depth layering. `subject` is optional because many portal scenes are abstract/environmental without a focal element. This gives the minimum working portal 2 images to generate — keeping the LLM authoring burden low.

### D4: Compatible cameras — lateral tracks excluded

The portal's concentric Z-axis arrangement means all planes are centered at X=0. Lateral camera tracks (`lateral_track_left`, `lateral_track_right`) would shift the camera off-center, breaking the concentric alignment and potentially revealing frame edges on one side. The forward/backward cameras work perfectly because they move along the axis of symmetry.

`crane_up` is excluded because vertical motion would shift the concentric rings off-center vertically. `tunnel_push_forward` is excluded because it's tuned for enclosed corridor geometries with different Z-range and speed characteristics. `flyover_glide` requires a below-camera ground plane.

Included cameras: `static` (always safe), `slow_push_forward` (the defining motion), `slow_pull_back` (reverse reveal), `gentle_float` (subtle ambient drift within safe bounds), `dramatic_push` (faster version of the push-through for emphasis).

**Forward reference note:** `slow_push_forward` (OBJ-027) and `static` (OBJ-026) and `gentle_float` (OBJ-031) are verified. `slow_pull_back` (OBJ-027) is verified. `dramatic_push` (OBJ-029) is verified. The `compatible_cameras` list may be revised if OBJ-041 compatibility validation finds edge-reveal issues.

### D5: Dark blue-black fog for dreamlike atmosphere

Fog color `#0a0a14` (very dark blue-black) creates a moody, dreamlike atmosphere appropriate for the portal's typical use cases (transitions, fantasy sequences, abstract compositions). `near: 10` ensures `frame_near` (distance 8) and `near_fg` (distance 5) are completely clear. `far: 55` fades distant elements — `frame_far` (distance 35) is partially fogged, enhancing depth separation between the layers. The `backdrop` is `fogImmune` to remain vivid.

The blue tint distinguishes the portal's fog from the stage's neutral black fog and the canyon's neutral black fog, reinforcing the dreamlike character at the geometry level.

### D6: `frame_near` at Z=-3 — camera passes through it

With `slow_push_forward` moving the camera from z=5 to z=-3, the camera's endpoint exactly matches `frame_near`'s Z-position. This means at the end of the push, the camera has just passed through the nearest frame — the frame fills the viewport and then sweeps behind. This is the signature portal effect.

At `speed=1.0`, the camera reaches `frame_near`'s Z at exactly `t=1.0`. At lower speeds, the camera only approaches but doesn't fully pass through. At higher speeds, it passes through earlier and continues deeper. This creates a natural speed-dependent experience: gentle speeds give a "peering into the portal" feel, while full or fast speeds give a "plunging through" feel.

**Near-plane clipping consideration:** When the camera reaches z=-3, `near_fg` at z=0 is 3 units ahead of the camera, and `frame_near` at z=-3 is at the camera position (0 units — at the clipping plane or behind it). The near clipping plane (`DEFAULT_CAMERA.near = 0.1`) means the frame geometry is effectively behind the camera and no longer rendered. This is the desired behavior — the frame sweeps past and disappears.

### D7: Subject positioned between frame_mid and frame_far

The subject at z=-20 is intentionally placed between the mid (z=-15) and far (z=-30) frames. This means:
- Looking from the start position, the subject appears "within" the portal — visible through `frame_near` and `frame_mid` but in front of `frame_far`.
- The `renderOrder` (subject=3, frame_near=4) ensures frame_near renders on top of the subject when they visually overlap, maintaining the "looking through a frame at the subject" illusion.
- As the camera pushes forward and passes through `frame_near` and approaches `frame_mid`, the subject becomes more prominent — a natural narrative reveal.

### D8: `near_fg` at z=0 — in front of all frames

The foreground atmospheric element at z=0 is positioned between the camera (z=5) and the nearest frame (z=-3). This creates a layer of atmosphere (particles, sparkles, mist) that the viewer looks *through* before seeing the portal frames — enhancing the dreamlike, mystical quality. At 5 units from the camera start, it's close enough to produce strong parallax but far enough to avoid near-plane clipping.

### D9: All frames are transparent; backdrop is opaque

This is the defining material characteristic of the portal geometry. Frame planes (`frame_near`, `frame_mid`, `frame_far`) are `transparent: true` because the visual effect depends on seeing through each frame's center to the layers behind. The LLM author must generate images with opaque decorative borders and transparent centers. The `backdrop` is `transparent: false` — it's the solid destination image that fills the deepest portal opening.

The SKILL.md documentation (OBJ-071) should strongly emphasize this requirement. A frame image without alpha transparency would appear as a solid rectangle, completely occluding all deeper layers and destroying the portal effect.

### D10: Render order matches depth but subject intercedes

The render order `backdrop(0) < frame_far(1) < frame_mid(2) < subject(3) < frame_near(4) < near_fg(5)` generally tracks Z-depth (back to front). Three.js depth testing handles most ordering, but for transparent materials, explicit `renderOrder` ensures correct alpha compositing:
- Backdrop renders first (fully opaque, fills the deepest opening).
- Frame_far renders over backdrop (its transparent center reveals the backdrop).
- Frame_mid renders over frame_far (its transparent center reveals frame_far and backdrop).
- Subject renders over frame_mid but under frame_near.
- Frame_near renders over subject (its transparent center frames the subject and deeper layers).
- near_fg renders on top of everything.

### D11: PlaneSlot construction, not DepthSlot

Following the pattern from OBJ-018: the portal geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration. `DepthSlot` metadata fields like `promptGuidance` and `expectsAlpha` are surfaced via separate mechanisms for SKILL.md generation (OBJ-071) and the asset pipeline (OBJ-053), not via geometry registration.

### D12: Explicit optional field policy

Following OBJ-018's convention: all `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — no fields are omitted to rely on renderer defaults.

## Acceptance Criteria

- [ ] **AC-01:** `portalGeometry.name` is `'portal'`.
- [ ] **AC-02:** `portalGeometry.slots` contains exactly 6 keys: `backdrop`, `frame_far`, `frame_mid`, `frame_near`, `subject`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `backdrop` and `frame_near` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `portalGeometry.default_camera` is `'slow_push_forward'`.
- [ ] **AC-05:** `portalGeometry.default_camera` appears in `portalGeometry.compatible_cameras`.
- [ ] **AC-06:** `portalGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (verified camera presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `portalGeometry.compatible_cameras` does NOT include `'lateral_track_left'`, `'lateral_track_right'`, `'tunnel_push_forward'`, `'flyover_glide'`, or `'crane_up'`.
- [ ] **AC-08:** `portalGeometry.fog` is `{ color: '#0a0a14', near: 10, far: 55 }`.
- [ ] **AC-09:** `portalGeometry.description` is non-empty and describes concentric frames at increasing Z-depth.
- [ ] **AC-10:** `portalGeometry.preferred_aspect` is `'both'`.
- [ ] **AC-11:** All 6 slots use `PLANE_ROTATIONS.FACING_CAMERA` (`[0, 0, 0]`) as their rotation.
- [ ] **AC-12:** All frame slots (`frame_near`, `frame_mid`, `frame_far`) and `subject` and `near_fg` have `transparent: true`. Only `backdrop` has `transparent: false`.
- [ ] **AC-13:** `backdrop` and `frame_near` and `near_fg` have `fogImmune: true`. `frame_far`, `frame_mid`, and `subject` have `fogImmune: false`.
- [ ] **AC-14:** `renderOrder` values are strictly increasing from backdrop (0) through near_fg (5), with no duplicates.
- [ ] **AC-15:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-16:** `registerGeometry(portalGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-17:** All slot `description` fields are non-empty strings.
- [ ] **AC-18:** All slot `size` components are positive (> 0).
- [ ] **AC-19:** For all slots except `subject`, both size dimensions are >= the frustum visible dimensions at that slot's distance from `DEFAULT_CAMERA.position` ([0, 0, 5]) with FOV=50 degrees and aspect ratio 16:9. Specifically:
  - `backdrop` at distance 50: visible ~46.6h × 82.9w → size [110, 62] ✓
  - `frame_far` at distance 35: visible ~32.6h × 58.0w → size [72, 42] ✓
  - `frame_mid` at distance 20: visible ~18.6h × 33.1w → size [42, 24] ✓
  - `frame_near` at distance 8: visible ~7.5h × 13.3w → size [18, 11] ✓
  - `near_fg` at distance 5: visible ~4.7h × 8.3w → size [14, 9] ✓
- [ ] **AC-20:** For the `subject` slot (a focal element, not a coverage plane), `size[1]` (height, 14) >= frustum visible height at distance 25 (~23.3). *(Note: This AC expects subject to NOT fill the full frustum — 14 < 23.3 — because it is intentionally a focal element. The subject does NOT need to cover the viewport.)*
- [ ] **AC-21:** Slot Z-positions decrease (go more negative) from nearest to deepest: `near_fg` (0) > `frame_near` (-3) > `frame_mid` (-15) > `subject` (-20) > `frame_far` (-30) > `backdrop` (-45).
- [ ] **AC-22:** The module self-registers via `registerGeometry(portalGeometry)` as a side effect of import.
- [ ] **AC-23:** The module exports `portalGeometry` as a named export.
- [ ] **AC-24:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants (`PLANE_ROTATIONS`).
- [ ] **AC-25:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-26:** `frame_near` at Z=-3 matches the end position of `slow_push_forward` (z=-3 per OBJ-027), ensuring the camera passes through the nearest frame during a full-speed forward push.

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`backdrop`, `frame_near`) | Valid scene. Minimal portal effect — a single frame the camera pushes through, revealing the backdrop. No intermediate depth layering but the spatial illusion still works. |
| Manifest provides all 6 slots | Valid scene. Full layered portal with maximum depth richness, subject at center, and foreground atmosphere. |
| Manifest provides an unknown slot key (e.g., `ceiling`) | Rejected by manifest validation (OBJ-017) — `ceiling` is not in the portal geometry's slot set. |
| Manifest provides `frame_near` + `frame_mid` but not `frame_far` | Valid — all frame slots are optional except `frame_near`. The mid frame adds one layer of depth; the missing far frame means the backdrop is visible through the mid frame's center with no intervening frame. |
| Frame image without alpha transparency | The frame plane renders as a solid rectangle, fully occluding deeper layers. Not a validation error (the engine cannot inspect image content at validation time) but a visual defect. The SKILL.md must strongly emphasize the alpha requirement for frame slots. |
| Camera pushes through `frame_near` (z=-3) | At the moment the camera reaches z=-3, `frame_near` is at the camera position. With `near: 0.1` clipping, the frame is behind the camera and stops rendering. This is the intended "passing through the portal" behavior. |
| Camera pushes beyond `frame_near` at speed > 1.0 | At higher speeds, the camera travels deeper than z=-3, passing through `frame_near` before t=1.0 and potentially approaching `frame_mid`. This is valid and enhances the portal-diving effect. The frame planes are sized to fill the viewport at their respective distances from the camera's *start* position — the oversizing factor handles the camera approaching. |
| Portrait mode (9:16) | The geometry renders correctly. All planes are centered at X=0, Y=0 with `FACING_CAMERA` rotation. In portrait, visible width narrows but all plane widths exceed the narrower visible width. OBJ-040 validates this formally. |
| `near_fg` near-plane clipping at aggressive camera push | `near_fg` is at z=0. If camera pushes to z=-3, distance is 3 units — above the near clipping plane (0.1). If the camera pushes further (speed > 1.0), it may approach z=-5 or beyond, and `near_fg` at z=0 would be 5+ units away — no clipping risk. Clipping only occurs if the camera overshoots to z > -0.1, which would mean the camera is practically at z=0 — `near_fg` would be behind or at the camera. The `slow_push_forward` endpoint of z=-3 keeps 3 units of clearance. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `portal.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'portal' is already registered." The module should guard against double-registration using a module-level flag or rely on Node.js module caching (single execution). |
| `portal.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'portal': registry is locked." This is an initialization ordering error — geometry modules must be imported before any registry reads. |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `portalGeometry.name` is `'portal'`.
2. `portalGeometry.slots` has exactly 6 keys.
3. Required slots: `backdrop`, `frame_near`. Optional: `frame_far`, `frame_mid`, `subject`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'slow_push_forward'` and is in `compatible_cameras`.
6. `compatible_cameras` is non-empty, all entries match `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` matches hex pattern.
8. `description` is non-empty.
9. `preferred_aspect` is `'both'`.

**Slot spatial correctness tests:**
10. All 6 slots have rotation `[0, 0, 0]` (`PLANE_ROTATIONS.FACING_CAMERA`).
11. Z-positions are ordered from nearest (`near_fg`: 0) to deepest (`backdrop`: -45).
12. `renderOrder` values are strictly ordered: backdrop(0) < frame_far(1) < frame_mid(2) < subject(3) < frame_near(4) < near_fg(5).
13. All `size` components are > 0.
14. `frame_near` Z-position (-3) matches `slow_push_forward` end position per OBJ-027.

**Slot metadata tests:**
15. All frame slots + `subject` + `near_fg` have `transparent: true` (5 of 6 slots).
16. `backdrop.transparent` is `false`.
17. `backdrop.fogImmune` is `true`; `frame_near.fogImmune` is `true`; `near_fg.fogImmune` is `true`.
18. `frame_far.fogImmune` is `false`; `frame_mid.fogImmune` is `false`; `subject.fogImmune` is `false`.
19. All slot `description` fields are non-empty.
20. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
21. `validateGeometryDefinition(portalGeometry)` returns an empty error array.
22. `registerGeometry(portalGeometry)` does not throw (when registry is not locked).
23. After registration, `getGeometry('portal')` returns the portal geometry.

**Frustum size validation tests:**
24. For each coverage slot (`backdrop`, `frame_far`, `frame_mid`, `frame_near`, `near_fg`): verify that slot `size[0]` >= frustum visible width and `size[1]` >= frustum visible height at the slot's distance from `DEFAULT_CAMERA.position`, with FOV=50 degrees and aspect 16:9.
25. For `subject`: confirm it is intentionally smaller than the full frustum visible area at its distance (14 < 23.3 for height; 14 < 41.5 for width).

**Compatible cameras tests:**
26. `compatible_cameras` includes `'static'`, `'slow_push_forward'`, `'gentle_float'`, `'slow_pull_back'`, `'dramatic_push'`.
27. `compatible_cameras` does NOT include `'lateral_track_left'`, `'lateral_track_right'`, `'tunnel_push_forward'`, `'flyover_glide'`, `'crane_up'`.

### Relevant Testable Claims

- **TC-01** (partial): The portal geometry uses 6 slots (2 required, 4 optional), within the 3-5 effective range. The minimum working scene uses 2 images (`backdrop` + `frame_near`).
- **TC-04** (partial): The portal geometry defines all spatial relationships — an LLM specifies `geometry: 'portal'` and fills slot names. No XYZ coordinates needed in the manifest.
- **TC-08** (partial): The portal geometry is one of the 8 proposed geometries. It covers transitions, dreamlike sequences, fantasy themes, and abstract compositions.

## Integration Points

### Depends on

| Upstream | What OBJ-023 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types for the geometry definition. `registerGeometry` function for self-registration. `validateGeometryDefinition` (used indirectly — `registerGeometry` calls it). |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`, `isValidSlotName`). Referenced for documentation consistency — slot names follow the reserved name conventions where applicable (`backdrop`, `subject`, `near_fg`). |
| **OBJ-003** (Spatial math) | `PLANE_ROTATIONS.FACING_CAMERA` constant for all slot rotations. `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. |

### Consumed by

| Downstream | How it uses OBJ-023 |
|------------|---------------------|
| **OBJ-064** (Portal visual tuning) | The Director Agent reviews test renders of the portal geometry and provides feedback on frame Z-spacing, sizes, fog settings, and the "push through" effect quality. OBJ-064 may adjust numerical values in the slot definitions. |
| **OBJ-071** (SKILL.md) | Documents the portal geometry's slot names, descriptions, and usage guidance. Should strongly emphasize the alpha transparency requirement for frame slots. |
| **OBJ-017** (Manifest structural validation) | After registration, manifest validation can look up `getGeometry('portal')` and validate that a manifest's `planes` keys match the portal's slot names. |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('portal')` to resolve slot spatial data when rendering a scene with `geometry: 'portal'`. |
| **OBJ-039** (Page-side renderer) | Reads slot `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune` to create Three.js meshes. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        portal.ts         # portalGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./portal
```

## Open Questions

### OQ-A: Should the frame spacing be adjustable via camera speed?

Currently the frame Z-positions are fixed. With `slow_push_forward` at speed=1.0, the camera reaches `frame_near` at exactly t=1.0. At speed=0.5, the camera only travels 4 units (z=5 to z=1), never reaching `frame_near` (z=-3). This means slower speeds produce a "peering into the portal" effect rather than "pushing through," which may or may not be the desired behavior.

**Recommendation:** Keep positions fixed. The speed-dependent behavior is a feature, not a bug — it gives the LLM author natural control over the portal's intensity. Document this in SKILL.md: "At lower camera speeds, the portal effect is subtler (approaching but not passing through frames). At higher speeds, the camera pushes through multiple frames."

### OQ-B: Should there be a `frame_extra` slot for a fourth frame?

Three frames may feel sparse for very long scenes (>10 seconds). A fourth frame at Z=-8 would add another layer of depth. However, this increases the image generation burden and the slot count to 7.

**Recommendation:** Defer. Three frames cover the portal concept well. If visual tuning (OBJ-064) reveals that three frames feels thin, a fourth slot can be added. The LLM author can also use `PlaneOverride` to reposition existing frames for tighter or wider spacing.

### OQ-C: Should frame images be required to have alpha, or just recommended?

The engine cannot validate image content at manifest validation time. A frame image without alpha would render as a solid rectangle — functionally correct but visually wrong.

**Recommendation:** Keep as a strong recommendation in SKILL.md and slot descriptions, not a validation rule. The engine treats `transparent: true` as a material hint (enable alpha blending), which is correct regardless of whether the actual image has alpha data.

---

I believe this specification is comprehensive and follows the established patterns from OBJ-018 (stage), OBJ-020 (canyon), OBJ-021 (flyover), and OBJ-022 (diorama). The key distinguishing characteristics of the portal geometry — all planes camera-facing, three concentric frame slots with alpha, the camera push-through effect at z=-3 — are clearly documented with spatial rationale.

I'd like the Challenger to verify and approve. Key areas I'd welcome scrutiny on:
1. Whether 2 required slots (backdrop + frame_near) is sufficient or too minimal
2. Whether the frame Z-spacing (-3, -15, -30) produces the right visual layering
3. Whether `near_fg` at z=0 is too close to the camera or positioned correctly
4. Whether the fog settings appropriately serve the dreamlike aesthetic

---

## Round 2 — spec_challenger


[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


Let me verify the OBJ-027 slow_push_forward endpoint and OBJ-003 constants to check the spec's spatial claims.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "offset": 1,
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md",
  "limit": 60
}
[Tool Result]      1→# Specification: OBJ-029 — Tunnel Push Forward Camera Path Preset
     2→
     3→## Summary
     4→
     5→OBJ-029 defines the `tunnel_push_forward` camera path preset — a deep Z-axis push specifically tuned for the tunnel geometry (OBJ-019). Unlike `slow_push_forward` (OBJ-027), which covers 8 world units of generic Z-axis motion, `tunnel_push_forward` covers **25 world units** (z=5 to z=-20), pushing the camera deep into the tunnel corridor where walls, floor, and ceiling undergo dramatic perspective distortion — converging toward the end wall at z=-45. This preset includes a subtle Y-axis rise (from y=-0.3 to y=0) to simulate a slightly grounded starting perspective that levels out, and uses `ease_in_out_cubic` as its default easing for a heavier, more cinematic feel appropriate for the dramatic spatial motion. It implements the `CameraPathPreset` interface from OBJ-006 and is the default camera for the tunnel geometry.
     6→
     7→## Interface Contract
     8→
     9→### ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md",
  "offset": 1,
  "limit": 15
}
[Tool Result]      1→# Specification: OBJ-029 — Tunnel Push Forward Camera Path Preset
     2→
     3→## Summary
     4→
     5→OBJ-029 defines the `tunnel_push_forward` camera path preset — a deep Z-axis push specifically tuned for the tunnel geometry (OBJ-019). Unlike `slow_push_forward` (OBJ-027), which covers 8 world units of generic Z-axis motion, `tunnel_push_forward` covers **25 world units** (z=5 to z=-20), pushing the camera deep into the tunnel corridor where walls, floor, and ceiling undergo dramatic perspective distortion — converging toward the end wall at z=-45. This preset includes a subtle Y-axis rise (from y=-0.3 to y=0) to simulate a slightly grounded starting perspective that levels out, and uses `ease_in_out_cubic` as its default easing for a heavier, more cinematic feel appropriate for the dramatic spatial motion. It implements the `CameraPathPreset` interface from OBJ-006 and is the default camera for the tunnel geometry.
     6→
     7→## Interface Contract
     8→
     9→### ... [truncated]
Good. Now let me check the OBJ-006 camera path type contract and the OBJ-018 stage spec for pattern comparison:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "offset": 1,
  "limit": 200
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
Now let me check the `dramatic_push` preset (OBJ-029 was tunnel_push_forward, not dramatic_push). Let me find the right one:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-02[6-9]/meta.json"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-03[0-4]/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-032/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-033/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-034/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/meta.json

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
     7→  "updated_at": "2026-03-23T04:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Currently a leaf node -- no tuning objective directly references lateral tracks. Spec complete: two presets (lateral_track_left, lateral_track_right), 6-unit X displacement, static lookAt with 1-unit lead, FOV 50, ease_in_out default, recommendedOversizeFactor 2.5 (covers 9:16 portrait + lookAt rotation swe... [truncated]

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
     7→  "updated_at": "2026-03-23T03:00:00Z",
     8→  "depends_on": ["OBJ-006"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 camera path. Geometry-specific preset for flyover. Spec completed via 4-round deliberation.",
    12→  "status": "specified",
    13→  "review_status": "approved"
    14→}
    15→

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-032/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-033/output.md"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-034/output.md"
}
[Tool Result] No files found

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
Now I have enough context. Let me also check the OBJ-028 spec to see if `dramatic_push` is `OBJ-032` (open, no output.md) and if it's listed as compatible with portal in the lateral track spec:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "limit": 40
}
[Tool Result]      1→# Specification: OBJ-028 — Lateral Track Camera Path Presets
     2→
     3→## Summary
     4→
     5→OBJ-028 defines two camera path presets — `lateral_track_left` and `lateral_track_right` — that translate the camera along the X-axis to produce cinematic tracking shots. The camera slides horizontally while looking slightly ahead of its travel direction, creating the classic dolly-track effect where foreground planes move faster than background planes due to perspective projection. These presets conform to the `CameraPathPreset` contract from OBJ-006 and require significant X-axis plane oversizing to prevent edge reveals.
     6→
     7→## Interface Contract
     8→
     9→### Preset Definitions
    10→
    11→```typescript
    12→// src/camera/presets/lateral_track.ts
    13→
    14→import { CameraPathPreset } from '../types';
    15→
    16→/**
    17→ * Camera translates along the NEGATIVE X-axis (right to left in screen space).
    18→ * The camera starts at a positive X of... [truncated]
Good. Now I have full context. Let me review the proposed spec.

---

## Review of OBJ-023 Portal Scene Geometry Specification

Overall, this is a well-structured spec that follows the established patterns (OBJ-018, OBJ-020, OBJ-021, OBJ-022) closely. The spatial reasoning is sound, and most design decisions are well-justified. However, I have several issues of varying severity:

### Issue 1: `dramatic_push` is NOT verified — it's `open` (OBJ-032, status: `open`, no `output.md`)

**Severity: Major**

The spec lists `'dramatic_push'` in `compatible_cameras` and AC-26 makes a claim tied to it. But OBJ-032 (dramatic push) is status `open` with no output.md — it hasn't been specified yet. The spec's D4 states "`dramatic_push` (OBJ-029) is verified" — but OBJ-029 is actually `tunnel_push_forward`, not `dramatic_push`. This is a factual error.

Other verified geometry specs handle unspecified presets via a **forward reference note** (see OBJ-018's D5: "The `compatible_cameras` list may be revised as those presets are specified"). The portal spec must do the same.

**Fix:** 
1. Correct D4's false claim: remove "`dramatic_push` (OBJ-029) is verified." OBJ-029 is `tunnel_push_forward`.
2. Add a forward-reference note in D4 clarifying which cameras are verified vs. forward-referenced: `static` (OBJ-026 verified), `slow_push_forward` + `slow_pull_back` (OBJ-027 verified), `gentle_float` (OBJ-031 verified), `dramatic_push` (OBJ-032 **open — forward reference**).
3. AC-06 already covers verified presets correctly, but add a note in AC that `dramatic_push` inclusion is provisional pending OBJ-032 specification.

### Issue 2: Lateral track exclusion may be incorrect — OBJ-028 lists `portal` as compatible

**Severity: Major**

The OBJ-028 (lateral track) meta.json notes say: "Compatible with stage, canyon, diorama, **portal**, panorama." This means the lateral track preset was designed with portal compatibility in mind. But the portal spec's D4 excludes lateral tracks because they "would shift the camera off-center, breaking the concentric alignment and potentially revealing frame edges on one side."

This is a legitimate design tension, but the spec needs to **acknowledge the conflict** rather than silently contradict OBJ-028. Either:
- The portal spec is correct and OBJ-028's compatibility list should be revised (document this as a required update), OR
- Lateral tracks could work if the frame plane oversizing accounts for X-axis displacement (the portal planes ARE significantly oversized)

**Fix:** Add a note in D4 acknowledging OBJ-028 claims portal compatibility. State that this spec disagrees and that OBJ-041 (geometry-camera compatibility validation) should be the final arbiter. If the decision stands to exclude, note that OBJ-028's `compatibleGeometries` should be updated to remove `'portal'`.

### Issue 3: Frustum math spot-check — `frame_near` size may be insufficient during camera approach

**Severity: Major**

The spec says `frame_near` at z=-3, size `[18, 11]`, is adequate at distance 8 (camera at z=5). But `slow_push_forward` pushes the camera from z=5 to z=-3. As the camera approaches `frame_near`, the distance shrinks to 0. At, say, distance 1 unit (camera at z=-2):

```
visible_height = 2 × 1 × tan(25°) ≈ 0.93
visible_width = 0.93 × 1.778 ≈ 1.65
```

The plane at 18×11 is still larger. So no edge reveals from frustum growth — good.

BUT: this is a **frame** with a transparent center. The visual effect is that the camera sees the *border* (opaque part) fill the screen, not the whole plane. The plane is 18×11 but the opaque border might only be, say, 1-2 units wide around the edge. As the camera approaches very close, the border fills the whole screen, which is the desired "passing through" effect. This seems correct.

Actually, I'll downgrade this — the math checks out. The plane is always larger than the frustum at any distance from 8 to 0. **Withdrawn.**

### Issue 4: `near_fg` at z=0 with camera pushing to z=-3 — the camera passes THROUGH the `near_fg` plane

**Severity: Major**

The camera starts at z=5 and pushes to z=-3. `near_fg` is at z=0. At t ≈ 0.625 (when the camera passes z=0), the camera is AT the `near_fg` plane, and for the remainder of the push, `near_fg` is BEHIND the camera. This means:

1. `near_fg` will visually flip/distort as the camera passes through it
2. For the last ~37.5% of the scene, `near_fg` is behind the camera and invisible

The edge case table mentions this obliquely ("distance shrinks to 3 units") but actually understates the problem — the distance shrinks to 0 at z=0, and then `near_fg` goes behind the camera entirely.

Is this intentional? For `frame_near` at z=-3, passing through is the signature effect. But for `near_fg` (foreground atmosphere), passing through it mid-scene and having it vanish for the back third seems like a visual defect, not a feature.

**Fix:** Either:
- Move `near_fg` to z=2 or z=3 (in front of the camera start at z=5 is wrong — that's behind the camera at start). Actually, `near_fg` should be at a Z-value that the camera doesn't pass through during the default camera push. Something like z=1 to z=3 keeps it ahead of z=-3 but behind z=5. But wait — at z=3, the camera starts 2 units behind it. The camera would pass it at early t.

Actually, the fundamental issue is: with a camera push from z=5 to z=-3, there is NO Z-position for `near_fg` where it stays between the camera and the scene for the entire duration. The camera moves 8 units forward, so anything within that 8-unit range will be passed.

Better fix: **Document explicitly** in the edge case table that `near_fg` is passed through during a `slow_push_forward` at speed >= ~0.625, making it visible for only part of the scene. Recommend in SKILL.md that `near_fg` works best with `static` or `gentle_float` for portal geometry, and may produce partial-visibility with push cameras. Alternatively, state that this is a design choice: the foreground atmosphere creates a "veil" the viewer passes through as they enter the portal, which is actually poetically appropriate for the dreamlike theme.

The spec should be explicit about this behavior rather than glossing over it.

### Issue 5: AC-20 is self-contradicting

**Severity: Minor**

AC-20 reads: "For the `subject` slot, `size[1]` (height, 14) >= frustum visible height at distance 25 (~23.3). *(Note: This AC expects subject to NOT fill the full frustum — 14 < 23.3...)*"

The AC says `size[1] >= visible_height` but the note says `14 < 23.3`. These directly contradict. The AC as written is a failing test (14 is NOT >= 23.3).

**Fix:** Rewrite AC-20 to test what's actually intended: "For the `subject` slot, the plane size is intentionally smaller than the frustum visible area at its distance (14 < 23.3 height, 14 < 41.5 width), confirming it is a focal element that does NOT need full-frame coverage." Or simply remove AC-20 and rely on the exception clause in AC-19 ("for all slots except `subject`").

### Issue 6: Missing `OversizeRequirements` section

**Severity: Minor**

Looking at OBJ-029 (tunnel_push_forward), it includes an `OversizeRequirements` section specifying how much plane oversizing each camera path needs. The portal geometry doesn't define per-camera oversizing requirements. The slot sizes are designed with oversizing baked in, but the spec doesn't document the *required* minimum oversize factor for each compatible camera path, which OBJ-040 (edge-reveal validation) and OBJ-064 (visual tuning) will need.

**Fix:** This isn't strictly the geometry's responsibility (it's the camera preset's), but the spec should at minimum note that the baked-in oversizing was computed against `slow_push_forward`'s z=5→z=-3 range and that OBJ-040 should validate all compatible cameras. The current spec already does this implicitly in the size notes, so this is minor. Add a brief note in D1 or a new D-section.

### Issue 7: `subject` at z=-20 is between `frame_mid` (z=-15) and `frame_far` (z=-30), but renderOrder subject(3) > frame_mid(2) means subject renders ON TOP of frame_mid

**Severity: Minor (possibly by-design)**

If the subject is at z=-20 (behind frame_mid at z=-15), the depth buffer would naturally occlude the subject behind frame_mid's opaque parts. But `renderOrder=3` > `frame_mid.renderOrder=2` means the subject explicitly renders after frame_mid. For transparent materials with alpha blending, this could cause the subject to render on top of frame_mid's transparent portions incorrectly — the subject would "show through" from behind frame_mid even though it's geometrically behind it.

Wait — actually Three.js depth testing still works even with explicit renderOrder for opaque portions. The renderOrder only affects the draw order within the same depth, and for transparent objects, back-to-front is the correct order. Since subject IS behind frame_mid in Z-space, and frame_mid is transparent, the depth test should let the subject show through frame_mid's transparent center while being occluded by frame_mid's opaque border. The renderOrder ensures the subject is drawn after frame_mid, which is correct for alpha compositing (draw farther transparent objects first, then nearer ones on top).

Actually, for correct alpha compositing, you draw back-to-front: backdrop(0) → frame_far(1) → frame_mid(2) → subject(3) → frame_near(4) → near_fg(5). Since subject is at z=-20 (behind frame_mid at z=-15), drawing it AFTER frame_mid means it would be drawn on top of frame_mid in screen space, which is WRONG — the subject should appear through frame_mid's transparent center but behind frame_mid's opaque parts.

This is actually a real problem with transparency rendering. When using `renderOrder` to force draw order and `transparent: true`, Three.js typically disables depth writing for transparent objects. So subject drawn at renderOrder=3 would paint ON TOP of frame_mid's opaque parts if depth writing is disabled for transparent materials.

**Severity upgrade: Major**

The subject at z=-20 is BEHIND frame_mid at z=-15. With transparency rendering and renderOrder subject(3) > frame_mid(2), the subject would be drawn AFTER frame_mid. If depth writing is enabled for transparent materials (non-default in Three.js), the depth buffer would correctly occlude. If depth writing is disabled (Three.js default for transparent materials), the subject pixels would overwrite frame_mid's opaque pixels.

**Fix:** One of:
1. Document that the renderer (OBJ-039) must enable `depthWrite: true` on transparent materials for this geometry to work correctly, or
2. Set subject `renderOrder` to 1.5 (between frame_far and frame_mid) so it draws BEFORE frame_mid — then frame_mid's opaque border naturally overwrites the subject. But `renderOrder` should be an integer...actually Three.js accepts any number.
3. Reorder: backdrop(0) → frame_far(1) → subject(2) → frame_mid(3) → frame_near(4) → near_fg(5). This draws subject BEFORE frame_mid, so frame_mid's opaque border correctly covers the subject. frame_mid's transparent center lets the subject show through because no pixels were written there.

Option 3 is the correct fix. The renderOrder should match the DRAW order for correct alpha compositing: things farther from the camera should be drawn first, and subject (z=-20) is farther than frame_mid (z=-15).

### Summary of Issues

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | `dramatic_push` misidentified as OBJ-029/verified; it's OBJ-032/open | Major | Needs fix |
| 2 | OBJ-028 (lateral track) claims portal compatibility — contradiction | Major | Needs acknowledgment |
| 3 | ~~Frustum math at close range~~ | ~~Major~~ | Withdrawn |
| 4 | `near_fg` at z=0 is passed through by camera during push | Major | Needs explicit documentation |
| 5 | AC-20 self-contradicting | Minor | Needs rewrite |
| 6 | No explicit oversize requirements documentation | Minor | Nice-to-have |
| 7 | Subject renderOrder(3) > frame_mid(2) breaks alpha compositing — subject should draw BEFORE frame_mid | Major | Needs renderOrder reorder |

I need fixes for issues 1, 2, 4, 5, and 7 before I can converge. Issue 7 is the most technically important — incorrect renderOrder will produce visible rendering artifacts.

---

## Round 3 — spec_author

All five issues are valid. Here's the revised specification with fixes for each:

---

# Specification: Portal Scene Geometry (OBJ-023)

## Summary

OBJ-023 defines the **portal** scene geometry — concentric frame planes at increasing Z-depth, creating a "looking through layers" effect like nested doorways, windows, or picture frames receding into depth. As the camera pushes forward, each frame fills the viewport and passes behind the camera, producing a dreamlike "traveling through portals" sensation. Every frame plane expects alpha transparency — the decorative border is opaque while the center is transparent, allowing deeper frames and the backdrop to show through. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/portal.ts

import type { SceneGeometry } from './types';

/**
 * The portal scene geometry — concentric frames at increasing Z-depth.
 *
 * Spatial arrangement: a deep backdrop plane visible through all
 * frames, three concentric frame planes (near, mid, far) at
 * increasing Z-depths, all facing the camera with transparent
 * centers. An optional subject plane sits between the mid and far
 * frames, and an optional near_fg provides foreground atmosphere.
 *
 * The defining visual effect is a "looking through nested portals"
 * sensation as the camera pushes forward. Each frame fills the
 * viewport momentarily, then passes behind the camera to reveal
 * the next frame and deeper layers. All frame planes require
 * images with alpha transparency (opaque border, transparent center).
 *
 * Best for transitions, dreamlike sequences, fantasy themes,
 * and abstract/artistic compositions.
 */
export const portalGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'portal'` | Matches seed Section 4.2 naming |
| `description` | `'Concentric frame planes at increasing Z-depth, like nested doorways or picture frames receding into the distance. Camera pushes through them for a dreamlike "traveling through portals" effect. Frame images should have transparent centers. Best for transitions, fantasy themes, and abstract compositions.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes through them." The forward push is the defining motion — it makes each frame fill and pass the viewport. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'gentle_float', 'dramatic_push']` | See D4. |
| `fog` | `{ color: '#0a0a14', near: 10, far: 55 }` | Very dark blue-black fog for dreamlike atmosphere. See D5. |
| `preferred_aspect` | `'both'` | Portal frames are centered and camera-facing — the concentric arrangement works in both 16:9 and 9:16. |

### Slot Definitions

The portal geometry defines **6 slots** — 2 required, 4 optional. The backdrop and at least one frame provide the essential spatial structure; additional frames and foreground enhance the layered portal effect.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to ensure each frame fully fills the viewport at its distance from camera.

Following the convention established by OBJ-018: the portal geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -45]` | Very deep Z — the final image visible through all frames. Distance from camera: 50 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[110, 62]` | Oversized to fill the viewport at distance 50. Frustum visible area at distance 50: ~46.6h × 82.9w. Width 110 ≈ 1.33x oversize, height 62 ≈ 1.33x oversize. |
| `required` | `true` | Every portal scene needs a destination image visible through the nested frames. |
| `description` | `'The deepest background — the destination visible through all portal frames. A complete scene or environment image.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backdrop is opaque — it fills the center of the deepest portal opening. |
| `fogImmune` | `true` | At distance 50 would be heavily fogged. Fog immunity ensures the destination image remains visible — the visual promise of the portal is that there's something to reach. |

#### Slot: `frame_far`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -30]` | Deep Z, farthest frame. Distance from camera: 35 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[72, 42]` | Fills viewport at distance 35. Frustum visible area: ~32.6h × 58.0w. Width 72 ≈ 1.24x oversize, height 42 ≈ 1.29x oversize. |
| `required` | `false` | Optional — a portal scene can work with just `frame_near` and `backdrop`. |
| `description` | `'Farthest portal frame — decorative border with transparent center. The smallest-appearing frame when viewed from the starting position.'` | |
| `renderOrder` | `1` | Renders above backdrop. |
| `transparent` | `true` | Frame images MUST have alpha — opaque border, transparent center. |
| `fogImmune` | `false` | Subtle fog fading on distant frames enhances depth separation. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -20]` | Between `frame_mid` (z=-15) and `frame_far` (z=-30). Distance from camera: 25 units. Visible through the mid frame's transparent center. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[14, 14]` | Focal element — intentionally smaller than the full frustum visible area at this distance (~23.3h × 41.5w). Subject occupies the center of the composition, not edge-to-edge. Square default accommodates both portrait and landscape subject images via texture auto-sizing (OBJ-040). |
| `required` | `false` | Optional — many portal scenes are abstract/decorative without a focal element. |
| `description` | `'Optional focal element visible through the portal frames — a person, object, or symbol at the center of the composition. Should have a transparent background.'` | |
| `renderOrder` | `2` | Renders after frame_far, **before** frame_mid. See D10. |
| `transparent` | `true` | Subject needs alpha to blend with the portal layers behind it. |
| `fogImmune` | `false` | Subtle fog at distance 25 creates atmospheric depth separation. |

#### Slot: `frame_mid`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -15]` | Mid-depth. Distance from camera: 20 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[42, 24]` | Fills viewport at distance 20. Frustum visible area: ~18.6h × 33.1w. Width 42 ≈ 1.27x oversize, height 24 ≈ 1.29x oversize. |
| `required` | `false` | Optional — enhances the layered effect. |
| `description` | `'Middle portal frame — decorative border with transparent center. Creates the key intermediate depth layer between near and far frames.'` | |
| `renderOrder` | `3` | Renders after subject. frame_mid's opaque border correctly occludes the subject behind it; its transparent center reveals the subject. See D10. |
| `transparent` | `true` | Same alpha requirement as all frame slots. |
| `fogImmune` | `false` | At distance 20, fog begins to slightly affect this frame. |

#### Slot: `frame_near`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -3]` | Shallow Z, closest frame. Distance from camera: 8 units. Camera pushes through this frame during a full `slow_push_forward`. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[18, 11]` | Fills viewport at distance 8. Frustum visible area: ~7.5h × 13.3w. Width 18 ≈ 1.35x oversize, height 11 ≈ 1.47x oversize. Extra oversize because the camera pushes through this frame. |
| `required` | `true` | The nearest frame is the most visually prominent — it creates the "entering the portal" sensation. |
| `description` | `'Nearest portal frame — the first frame the camera approaches and pushes through. Should be the most visually prominent and detailed frame. Decorative border with transparent center.'` | |
| `renderOrder` | `4` | Renders above subject and all other frames. |
| `transparent` | `true` | Same alpha requirement as all frame slots. |
| `fogImmune` | `true` | At distance 8, fog should not affect the closest frame. |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, 0]` | In front of `frame_near` (z=-3), close to camera. Distance from camera at start: 5 units. **Note:** With `slow_push_forward` (z=5 → z=-3), the camera passes through this plane at approximately t=0.625. See D8. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[14, 9]` | Fills viewport at distance 5. Frustum visible area: ~4.7h × 8.3w. Width 14 ≈ 1.69x oversize, height 9 ≈ 1.91x oversize. |
| `required` | `false` | Optional atmospheric enhancement. |
| `description` | `'Foreground atmospheric element — particles, sparkles, mist, or light effects. Acts as a veil the viewer passes through when entering the portal. Best used with static or gentle_float cameras; with push cameras, this layer is passed through mid-scene and disappears, creating a deliberate threshold-crossing effect. Should have a transparent background.'` | |
| `renderOrder` | `5` | Renders on top of everything. |
| `transparent` | `true` | Foreground atmospheric elements must be mostly transparent. |
| `fogImmune` | `true` | Foreground should never be fogged. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `backdrop` | `[0, 0, -45]` | `[0, 0, 0]` | `[110, 62]` | **yes** | no | **yes** | 0 |
| `frame_far` | `[0, 0, -30]` | `[0, 0, 0]` | `[72, 42]` | no | **yes** | no | 1 |
| `subject` | `[0, 0, -20]` | `[0, 0, 0]` | `[14, 14]` | no | **yes** | no | 2 |
| `frame_mid` | `[0, 0, -15]` | `[0, 0, 0]` | `[42, 24]` | no | **yes** | no | 3 |
| `frame_near` | `[0, 0, -3]` | `[0, 0, 0]` | `[18, 11]` | **yes** | **yes** | **yes** | 4 |
| `near_fg` | `[0, 0, 0]` | `[0, 0, 0]` | `[14, 9]` | no | **yes** | **yes** | 5 |

### Registration Side Effect

```typescript
// src/scenes/geometries/portal.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(portalGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/portal.ts
export { portalGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./portal` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Three frame slots at logarithmically-spaced Z-depths

The portal uses three frame planes at Z = -3, -15, -30. The spacing is roughly logarithmic from the camera: distances of 8, 20, 35 units. This creates a perceptual effect where the frames appear evenly spaced in depth — linear spacing would make the far frames appear clumped together due to perspective compression. The three-frame design follows the seed's description ("concentric frames/planes at increasing Z-depth") while keeping the slot count within the 3-5 effective range per TC-01.

**Alternative considered:** Four or five frame slots. Rejected because more frames increase the image generation burden and the visual effect is already strong with three nested frames.

**Oversizing note:** All slot sizes are computed against the `slow_push_forward` camera range (z=5 to z=-3). As the camera pushes forward, the distance to each plane decreases, which decreases the frustum visible area at that plane — the plane becomes *more* oversized, not less. Therefore the initial oversizing (at camera start position z=5) is the minimum. OBJ-040 should validate this for all compatible cameras.

### D2: All planes face the camera — no rotated slots

Unlike tunnel or canyon geometries with rotated walls/floors, the portal geometry has every plane at `[0, 0, 0]` rotation (`FACING_CAMERA`). The depth illusion comes entirely from Z-spacing and perspective projection, not from rotated surfaces.

### D3: Only `backdrop` and `frame_near` are required

The minimum viable portal scene needs a destination (`backdrop`) and at least one frame boundary (`frame_near`). The nearest frame is required because it's the most visually impactful — it creates the "entering the portal" moment. This gives the minimum working portal 2 images to generate.

### D4: Compatible cameras — lateral tracks and vertical motion excluded

The portal's concentric Z-axis arrangement means all planes are centered at X=0. Lateral camera tracks would shift the camera off-center, breaking the concentric alignment and potentially revealing frame edges on one side. Vertical motion (crane_up) would similarly break the concentric centering.

**Verified presets in `compatible_cameras`:** `static` (OBJ-026, verified), `slow_push_forward` and `slow_pull_back` (OBJ-027, verified), `gentle_float` (OBJ-031, verified).

**Forward-referenced preset:** `dramatic_push` (OBJ-032, status: open — not yet specified). Included provisionally because a faster forward push is a natural fit for the portal's push-through effect. If OBJ-032's specification reveals spatial characteristics incompatible with the portal (e.g., excessive X/Y displacement), this entry should be removed. The `compatible_cameras` list may be revised when OBJ-032 is specified and when OBJ-041 (compatibility validation) performs formal edge-reveal checks.

**Excluded presets:** `lateral_track_left`/`lateral_track_right` (X-axis displacement breaks concentric alignment), `tunnel_push_forward` (tuned for enclosed corridor with different Z-range), `flyover_glide` (requires below-camera ground), `crane_up` (vertical displacement breaks concentric centering).

**Conflict note regarding OBJ-028:** OBJ-028's lateral track specification lists `portal` in its compatible geometries. This specification disagrees — the portal's frame planes are not oversized for X-axis displacement, and lateral motion disrupts the concentric "looking through" illusion that is the geometry's raison d'être. OBJ-041 (geometry-camera compatibility validation) should be the final arbiter. If this exclusion stands, OBJ-028's `compatibleGeometries` list should be updated to remove `'portal'`.

### D5: Dark blue-black fog for dreamlike atmosphere

Fog color `#0a0a14` (very dark blue-black) creates a moody, dreamlike atmosphere. `near: 10` ensures `frame_near` (distance 8) and `near_fg` (distance 5) are completely clear. `far: 55` fades distant elements — `frame_far` (distance 35) is partially fogged, enhancing depth separation between layers. The `backdrop` is `fogImmune` to remain vivid.

### D6: `frame_near` at Z=-3 — camera passes through it

With `slow_push_forward` moving the camera from z=5 to z=-3, the camera's endpoint exactly matches `frame_near`'s Z-position. At the end of the push, the frame fills the viewport and sweeps behind the camera — the near clipping plane (`DEFAULT_CAMERA.near = 0.1`) causes it to stop rendering. This is the signature portal effect.

At lower speeds, the camera approaches but doesn't fully pass through, giving a "peering into the portal" feel. At higher speeds, it passes through earlier and continues deeper.

### D7: Subject positioned between frame_mid and frame_far

The subject at z=-20 is between the mid (z=-15) and far (z=-30) frames. Looking from the start position, the subject appears "within" the portal — visible through `frame_near` and `frame_mid` but in front of `frame_far`. As the camera pushes forward and passes through frames, the subject becomes more prominent — a natural narrative reveal.

### D8: `near_fg` at z=0 — deliberate threshold-crossing behavior with push cameras

The foreground atmospheric element at z=0 is between the camera start (z=5) and `frame_near` (z=-3). With `slow_push_forward`, the camera passes through `near_fg` at approximately t=0.625 (when camera reaches z=0). For the remaining ~37.5% of the scene, `near_fg` is behind the camera and invisible.

**This is intentional and thematically appropriate:** the foreground atmosphere acts as a "veil" or "threshold" the viewer passes through when entering the portal. The veil disappears as the viewer crosses into the portal space, reinforcing the dreamlike transition. The slot description explicitly documents this behavior.

**Camera-specific behavior:**
- With `static` or `gentle_float`: `near_fg` remains visible throughout the scene (no Z-axis pass-through). Best for sustained atmospheric effects.
- With `slow_push_forward` at speed=1.0: `near_fg` is visible for approximately the first 62.5% of the scene, then passed through. Creates the threshold-crossing effect.
- With `slow_pull_back`: `near_fg` starts behind the camera (camera starts at z=-3) and comes into view as the camera retreats. Creates a "veil descending" exit effect.

SKILL.md (OBJ-071) should document these behaviors so the LLM author can choose accordingly.

### D9: All frames are transparent; backdrop is opaque

Frame planes (`frame_near`, `frame_mid`, `frame_far`) are `transparent: true` because the effect depends on seeing through each frame's center. The `backdrop` is `transparent: false` — it's the solid destination. A frame image without alpha transparency would appear as a solid rectangle, destroying the portal effect. SKILL.md must strongly emphasize this.

### D10: Render order follows strict back-to-front draw order for correct alpha compositing

**Critical for transparency rendering:** Three.js default behavior for transparent materials disables depth writing (`depthWrite: false`). This means the draw order (determined by `renderOrder`) controls which pixels appear on top. For correct alpha compositing, planes must be drawn strictly back-to-front — farther planes first, nearer planes last.

The render order is: `backdrop(0) → frame_far(1) → subject(2) → frame_mid(3) → frame_near(4) → near_fg(5)`.

**Key detail:** `subject` (z=-20) is drawn BEFORE `frame_mid` (z=-15) even though the subject is positioned deeper in Z-space. This is correct because:
1. Subject is drawn first (renderOrder 2), painting its pixels onto the canvas.
2. frame_mid is drawn second (renderOrder 3). Its opaque border pixels overwrite the subject pixels where they overlap — correctly occluding the subject behind the frame border.
3. frame_mid's transparent center pixels do NOT overwrite the subject (alpha=0 means nothing is drawn there), allowing the subject to remain visible through the transparent opening.

If the order were reversed (frame_mid drawn first, subject drawn after), the subject's pixels would overwrite frame_mid's opaque border, making the subject appear incorrectly IN FRONT OF the frame border.

This back-to-front draw order is a standard requirement for alpha-blended transparent rendering. The OBJ-039 page-side renderer must NOT enable `depthWrite: true` on transparent materials — the renderOrder-based compositing depends on the default `depthWrite: false` behavior.

### D11: PlaneSlot construction, not DepthSlot

Following the pattern from OBJ-018: the portal geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration.

### D12: Explicit optional field policy

Following OBJ-018's convention: all `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — no fields are omitted to rely on renderer defaults.

## Acceptance Criteria

- [ ] **AC-01:** `portalGeometry.name` is `'portal'`.
- [ ] **AC-02:** `portalGeometry.slots` contains exactly 6 keys: `backdrop`, `frame_far`, `frame_mid`, `frame_near`, `subject`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `backdrop` and `frame_near` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `portalGeometry.default_camera` is `'slow_push_forward'`.
- [ ] **AC-05:** `portalGeometry.default_camera` appears in `portalGeometry.compatible_cameras`.
- [ ] **AC-06:** `portalGeometry.compatible_cameras` includes `'static'`, `'slow_push_forward'`, `'slow_pull_back'`, and `'gentle_float'` (all verified presets).
- [ ] **AC-07:** `portalGeometry.compatible_cameras` includes `'dramatic_push'` as a provisional forward reference (OBJ-032 is open; inclusion is subject to revision when OBJ-032 is specified and OBJ-041 validates compatibility).
- [ ] **AC-08:** `portalGeometry.compatible_cameras` does NOT include `'lateral_track_left'`, `'lateral_track_right'`, `'tunnel_push_forward'`, `'flyover_glide'`, or `'crane_up'`.
- [ ] **AC-09:** `portalGeometry.fog` is `{ color: '#0a0a14', near: 10, far: 55 }`.
- [ ] **AC-10:** `portalGeometry.description` is non-empty and describes concentric frames at increasing Z-depth.
- [ ] **AC-11:** `portalGeometry.preferred_aspect` is `'both'`.
- [ ] **AC-12:** All 6 slots use `PLANE_ROTATIONS.FACING_CAMERA` (`[0, 0, 0]`) as their rotation.
- [ ] **AC-13:** All frame slots (`frame_near`, `frame_mid`, `frame_far`) and `subject` and `near_fg` have `transparent: true`. Only `backdrop` has `transparent: false`.
- [ ] **AC-14:** `backdrop` and `frame_near` and `near_fg` have `fogImmune: true`. `frame_far`, `frame_mid`, and `subject` have `fogImmune: false`.
- [ ] **AC-15:** `renderOrder` values are strictly increasing from backdrop (0) through near_fg (5), with no duplicates. The specific order is: `backdrop(0)`, `frame_far(1)`, `subject(2)`, `frame_mid(3)`, `frame_near(4)`, `near_fg(5)`.
- [ ] **AC-16:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-17:** `registerGeometry(portalGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-18:** All slot `description` fields are non-empty strings.
- [ ] **AC-19:** All slot `size` components are positive (> 0).
- [ ] **AC-20:** For all coverage slots (`backdrop`, `frame_far`, `frame_mid`, `frame_near`, `near_fg`), both size dimensions are >= the frustum visible dimensions at that slot's distance from `DEFAULT_CAMERA.position` ([0, 0, 5]) with FOV=50° and aspect ratio 16:9. Specifically:
  - `backdrop` at distance 50: visible ~46.6h × 82.9w → size [110, 62] ✓
  - `frame_far` at distance 35: visible ~32.6h × 58.0w → size [72, 42] ✓
  - `frame_mid` at distance 20: visible ~18.6h × 33.1w → size [42, 24] ✓
  - `frame_near` at distance 8: visible ~7.5h × 13.3w → size [18, 11] ✓
  - `near_fg` at distance 5: visible ~4.7h × 8.3w → size [14, 9] ✓
- [ ] **AC-21:** The `subject` slot is intentionally smaller than the frustum visible area at its distance (size [14, 14] vs visible ~23.3h × 41.5w at distance 25), confirming it is a focal element that does not need full-frame coverage.
- [ ] **AC-22:** Slot Z-positions decrease (go more negative) from nearest to deepest: `near_fg` (0) > `frame_near` (-3) > `frame_mid` (-15) > `subject` (-20) > `frame_far` (-30) > `backdrop` (-45).
- [ ] **AC-23:** The module self-registers via `registerGeometry(portalGeometry)` as a side effect of import.
- [ ] **AC-24:** The module exports `portalGeometry` as a named export.
- [ ] **AC-25:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants (`PLANE_ROTATIONS`).
- [ ] **AC-26:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-27:** `frame_near` at Z=-3 matches the end position of `slow_push_forward` (z=-3 per OBJ-027), ensuring the camera passes through the nearest frame during a full-speed forward push.
- [ ] **AC-28:** `renderOrder` for `subject` (2) is less than `renderOrder` for `frame_mid` (3), ensuring the subject is drawn BEFORE frame_mid for correct alpha compositing (frame_mid's opaque border occludes the subject behind it).
- [ ] **AC-29:** The `near_fg` slot description explicitly documents that with push cameras, this layer is passed through mid-scene.

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`backdrop`, `frame_near`) | Valid scene. Minimal portal effect — a single frame the camera pushes through, revealing the backdrop. No intermediate depth layering but the spatial illusion still works. |
| Manifest provides all 6 slots | Valid scene. Full layered portal with maximum depth richness, subject at center, and foreground atmosphere. |
| Manifest provides an unknown slot key (e.g., `ceiling`) | Rejected by manifest validation (OBJ-017) — `ceiling` is not in the portal geometry's slot set. |
| Manifest provides `frame_near` + `frame_mid` but not `frame_far` | Valid — all frame slots are optional except `frame_near`. The mid frame adds one layer; the missing far frame means the backdrop is visible through the mid frame's center with no intervening frame. |
| Frame image without alpha transparency | The frame plane renders as a solid rectangle, fully occluding deeper layers. Not a validation error (the engine cannot inspect image content at validation time) but a visual defect. The SKILL.md must strongly emphasize the alpha requirement for frame slots. |
| Camera pushes through `frame_near` (z=-3) | At the moment the camera reaches z=-3, `frame_near` is at the camera position. With `near: 0.1` clipping, the frame is behind the camera and stops rendering. This is the intended "passing through the portal" behavior. |
| Camera pushes through `near_fg` (z=0) with `slow_push_forward` | At approximately t=0.625 (camera at z=0), the camera passes through `near_fg`. For the remaining ~37.5% of the scene, `near_fg` is behind the camera and invisible. This is intentional — a "threshold crossing" effect. See D8. |
| Camera pushes beyond `frame_near` at speed > 1.0 | At higher speeds, the camera travels deeper than z=-3, passing through `frame_near` before t=1.0 and potentially approaching `frame_mid`. Valid and enhances the portal-diving effect. |
| `slow_pull_back` camera with `near_fg` | Camera starts at z=-3 with `near_fg` at z=0 — `near_fg` is 3 units in front of the camera at the start, then moves progressively farther ahead as the camera retreats to z=5. `near_fg` is visible for the entire scene, growing more distant. Creates a "veil receding" effect. |
| Portrait mode (9:16) | The geometry renders correctly. All planes are centered at X=0, Y=0 with `FACING_CAMERA` rotation. In portrait, visible width narrows but all plane widths exceed the narrower visible width. OBJ-040 validates this formally. |

### Transparency Rendering Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Subject and frame_mid overlap in screen space | frame_mid (renderOrder 3) draws AFTER subject (renderOrder 2). frame_mid's opaque border overwrites subject pixels; frame_mid's transparent center preserves subject pixels. Correct occlusion. |
| All frame slots provided, all transparent | Back-to-front draw order (0→1→2→3→4→5) ensures correct alpha compositing. Each frame's transparent center reveals all layers drawn before it. |
| Renderer enables `depthWrite: true` on transparent materials | Breaks the compositing model. subject (drawn at renderOrder 2) would write to the depth buffer, causing frame_mid (drawn at renderOrder 3, but at z=-15 which is "farther" in camera space) to be depth-culled — frame_mid would incorrectly disappear behind the subject. OBJ-039 must use `depthWrite: false` for transparent materials (Three.js default). |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `portal.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'portal' is already registered." Module should rely on Node.js module caching. |
| `portal.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'portal': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `portalGeometry.name` is `'portal'`.
2. `portalGeometry.slots` has exactly 6 keys.
3. Required slots: `backdrop`, `frame_near`. Optional: `frame_far`, `frame_mid`, `subject`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'slow_push_forward'` and is in `compatible_cameras`.
6. `compatible_cameras` is non-empty, all entries match `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` matches hex pattern.
8. `description` is non-empty.
9. `preferred_aspect` is `'both'`.

**Slot spatial correctness tests:**
10. All 6 slots have rotation `[0, 0, 0]` (`PLANE_ROTATIONS.FACING_CAMERA`).
11. Z-positions are ordered from nearest (`near_fg`: 0) to deepest (`backdrop`: -45).
12. `renderOrder` values are strictly ordered: `backdrop(0)` < `frame_far(1)` < `subject(2)` < `frame_mid(3)` < `frame_near(4)` < `near_fg(5)`.
13. All `size` components are > 0.
14. `frame_near` Z-position (-3) matches `slow_push_forward` end position per OBJ-027.

**Render order and alpha compositing tests:**
15. `subject.renderOrder` (2) < `frame_mid.renderOrder` (3) — subject draws before frame_mid for correct occlusion.
16. `frame_far.renderOrder` (1) < `subject.renderOrder` (2) — frame_far draws before subject.
17. `frame_mid.renderOrder` (3) < `frame_near.renderOrder` (4) — frame_mid draws before frame_near.

**Slot metadata tests:**
18. All frame slots + `subject` + `near_fg` have `transparent: true` (5 of 6 slots).
19. `backdrop.transparent` is `false`.
20. `backdrop.fogImmune` is `true`; `frame_near.fogImmune` is `true`; `near_fg.fogImmune` is `true`.
21. `frame_far.fogImmune` is `false`; `frame_mid.fogImmune` is `false`; `subject.fogImmune` is `false`.
22. All slot `description` fields are non-empty.
23. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.
24. `near_fg` slot description mentions pass-through behavior with push cameras.

**OBJ-005 validation integration test:**
25. `validateGeometryDefinition(portalGeometry)` returns an empty error array.
26. `registerGeometry(portalGeometry)` does not throw (when registry is not locked).
27. After registration, `getGeometry('portal')` returns the portal geometry.

**Frustum size validation tests:**
28. For each coverage slot (`backdrop`, `frame_far`, `frame_mid`, `frame_near`, `near_fg`): verify that slot `size[0]` >= frustum visible width and `size[1]` >= frustum visible height at the slot's distance from `DEFAULT_CAMERA.position`, with FOV=50° and aspect 16:9.
29. For `subject`: confirm it is intentionally smaller than the full frustum visible area at its distance.

**Compatible cameras tests:**
30. `compatible_cameras` includes `'static'`, `'slow_push_forward'`, `'gentle_float'`, `'slow_pull_back'`, `'dramatic_push'`.
31. `compatible_cameras` does NOT include `'lateral_track_left'`, `'lateral_track_right'`, `'tunnel_push_forward'`, `'flyover_glide'`, `'crane_up'`.

### Relevant Testable Claims

- **TC-01** (partial): The portal geometry uses 6 slots (2 required, 4 optional). The minimum working scene uses 2 images.
- **TC-04** (partial): The portal geometry defines all spatial relationships — an LLM specifies `geometry: 'portal'` and fills slot names. No XYZ coordinates needed.
- **TC-08** (partial): The portal geometry is one of the 8 proposed geometries, covering transitions, dreamlike sequences, and abstract compositions.

## Integration Points

### Depends on

| Upstream | What OBJ-023 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types. `registerGeometry` function. |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`). Referenced for documentation consistency. |
| **OBJ-003** (Spatial math) | `PLANE_ROTATIONS.FACING_CAMERA` constant. `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. |

### Consumed by

| Downstream | How it uses OBJ-023 |
|------------|---------------------|
| **OBJ-064** (Portal visual tuning) | Director Agent reviews test renders. May adjust frame Z-spacing, sizes, fog settings, render order. |
| **OBJ-071** (SKILL.md) | Documents portal slot names, descriptions, alpha transparency requirement for frames, and `near_fg` pass-through behavior with push cameras. |
| **OBJ-017** (Manifest structural validation) | Validates manifest plane keys against portal's slot names after registration. |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('portal')` to resolve slot spatial data. |
| **OBJ-039** (Page-side renderer) | Reads slot spatial and rendering properties. **Must use `depthWrite: false` for transparent materials** (Three.js default) to ensure the render-order-based alpha compositing works correctly. |
| **OBJ-041** (Geometry-camera compatibility) | Validates that listed compatible cameras don't produce edge reveals. Should resolve the conflict with OBJ-028 regarding lateral track compatibility. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        portal.ts         # portalGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./portal
```

## Open Questions

### OQ-A: Should the frame spacing be adjustable via camera speed?

Currently the frame Z-positions are fixed. At lower speeds the camera doesn't pass through frames; at higher speeds it passes through earlier. This is a feature, not a bug. **Recommendation:** Keep positions fixed. Document speed-dependent behavior in SKILL.md.

### OQ-B: Should there be a `frame_extra` slot for a fourth frame?

Three frames may feel sparse for very long scenes (>10 seconds). **Recommendation:** Defer. Three frames cover the concept well. If OBJ-064 visual tuning reveals thinness, a fourth can be added.

### OQ-C: Should frame images be required to have alpha, or just recommended?

The engine cannot validate image content at manifest validation time. **Recommendation:** Keep as a strong recommendation in SKILL.md and slot descriptions. The engine's `transparent: true` material hint is correct regardless.

### OQ-D: Should the OBJ-028 lateral track compatibility conflict be resolved here or deferred to OBJ-041?

OBJ-028 lists portal as compatible; this spec excludes lateral tracks. **Recommendation:** Defer to OBJ-041. This spec documents its rationale for exclusion and flags the conflict. OBJ-041 can perform formal edge-reveal analysis and make the final determination.

---

## Summary of Changes from Round 1

| Issue | Fix Applied |
|-------|-------------|
| **#1: `dramatic_push` misidentified** | Corrected D4: removed false claim that OBJ-029 is `dramatic_push`. Added explicit forward-reference note for OBJ-032 (open). Split AC-06/AC-07 to distinguish verified vs. provisional cameras. |
| **#2: OBJ-028 lateral track conflict** | Added conflict note in D4 acknowledging OBJ-028 claims portal compatibility. Documented rationale for disagreement. Added OQ-D and noted OBJ-041 as the arbiter. Added OBJ-041 to integration points. |
| **#4: `near_fg` pass-through behavior** | Rewrote D8 to explicitly document that `near_fg` is passed through at t≈0.625 with `slow_push_forward`. Updated `near_fg` slot description to document this behavior and recommend `static`/`gentle_float` for sustained atmosphere. Added edge case table entries for `near_fg` pass-through and `slow_pull_back` reverse behavior. Added AC-29. |
| **#5: AC-20 self-contradiction** | Replaced with two clear ACs: AC-20 (coverage slots >= frustum) and AC-21 (subject intentionally smaller, with explicit values). |
| **#7: Subject renderOrder breaks alpha compositing** | Reordered: `subject` renderOrder changed from 3 to 2; `frame_mid` changed from 2 to 3. Added D10 explaining back-to-front draw order requirement for transparent materials. Added transparency rendering edge cases table. Added AC-28 verifying subject < frame_mid renderOrder. Updated slot summary table. Added OBJ-039 `depthWrite: false` requirement in integration points. Added render-order-specific tests (15-17). |

I believe all five challenger issues are now resolved. I'd like the Challenger to verify and approve.

---

## Round 4 — spec_challenger

I've carefully verified each fix against my original objections.

## Verification of Fixes

| Issue | Claimed Fix | Verified? |
|-------|------------|-----------|
| **#1: `dramatic_push` misidentified** | D4 corrected: removed false OBJ-029 claim, added explicit forward-reference note for OBJ-032. AC-07 separated as provisional. | ✅ Confirmed in D4 and AC-06/AC-07 split |
| **#2: OBJ-028 lateral track conflict** | Conflict note added in D4, OQ-D added, OBJ-041 in integration points. | ✅ Confirmed in D4, OQ-D, and integration table |
| **#4: `near_fg` pass-through** | D8 rewritten with t≈0.625 math, slot description updated, edge cases added, AC-29 added. | ✅ Confirmed — math checks out (5/8 = 0.625), slot description explicitly documents behavior, three separate edge case rows |
| **#5: AC-20 self-contradiction** | Split into AC-20 (coverage slots ≥ frustum) and AC-21 (subject intentionally smaller with explicit values). | ✅ Confirmed — no contradiction, both are now testable pass/fail |
| **#7: renderOrder alpha compositing** | subject→2, frame_mid→3. D10 explains back-to-front. Transparency edge cases table added. AC-28 added. AC-15 updated. Tests 15-17 added. | ✅ Confirmed — slot summary table shows correct order, D10 reasoning is sound, depthWrite requirement documented |

No new issues introduced by the revisions. The spec is complete, implementable, and consistent with dependency specs.

CONCLUSION:

The portal scene geometry specification (OBJ-023) defines 6 slots (2 required: `backdrop` + `frame_near`; 4 optional: `frame_far`, `frame_mid`, `subject`, `near_fg`) arranged concentrically along the Z-axis with all planes facing the camera. The key design choices are: (1) logarithmic Z-spacing for perceptually even depth distribution, (2) back-to-front renderOrder with subject(2) drawn before frame_mid(3) for correct alpha compositing, (3) `frame_near` at z=-3 matching `slow_push_forward` endpoint for the signature push-through effect, (4) explicit documentation of `near_fg` threshold-crossing behavior with push cameras, and (5) exclusion of lateral track cameras (with OBJ-028 conflict flagged for OBJ-041 resolution). The spec includes 29 acceptance criteria, comprehensive edge cases including transparency rendering, and 31 unit tests.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]
You've hit your limit · resets 1am (America/New_York)
