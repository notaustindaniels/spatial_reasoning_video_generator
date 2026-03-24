# Deliberation Transcript: OBJ-022

---

## Round 1 — spec_author

I'll start by reading the existing codebase to understand patterns from verified geometry implementations before proposing the spec.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me look at existing verified geometry implementations for patterns to follow.
[Tool: Glob]
  Input: {
  "pattern": "**/scenes/geometries/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-018/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-021/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-022/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md"
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
[Tool Error] File content (10209 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": 100,
  "limit": 150
}
[Tool Result]    100→| Field | Value | Notes |
   101→|-------|-------|-------|
   102→| `position` | `[-10, 0, -20]` | Left of center (X=-10), mid-depth. Y=0 places the bottom edge at Y=-6 (center 0 - half-height 6 = -6), which extends 2 units below the ground plane at Y=-4. The ground's opaque surface occludes this below-ground portion via Z-buffer: camera rays from above Y=-4 that would reach below the ground at this Z-depth hit the ground plane first. See D4. |
   103→| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
   104→| `size` | `[10, 12]` | Medium-sized landmark. Tall (12) to suggest a vertical feature rising from the ground. |
   105→| `required` | `false` | Optional — adds lateral interest. |
   106→| `description` | `'Left-side landmark rising from the terrain — building, tree cluster, or terrain feature. Passes by on the left as the camera moves forward.'` | |
   107→| `renderOrder` | `3` | Renders above far landmark. |
   108→| `transparent` | `true` | Needs alpha to blend with ground/... [truncated]
Now I have a strong understanding of the established patterns. Let me also check what camera presets exist (OBJ-026 and OBJ-027) since those are critical for the compatible_cameras list.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": 249
}
[Tool Result]    249→
   250→## Acceptance Criteria
   251→
   252→- [ ] **AC-01:** `flyoverGeometry.name` is `'flyover'`.
   253→- [ ] **AC-02:** `flyoverGeometry.slots` contains exactly 6 keys: `sky`, `ground`, `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.
   254→- [ ] **AC-03:** Required slots are exactly `sky`, `ground` (`required: true`). All others are `required: false`.
   255→- [ ] **AC-04:** `flyoverGeometry.default_camera` is `'slow_push_forward'`.
   256→- [ ] **AC-05:** `flyoverGeometry.default_camera` appears in `flyoverGeometry.compatible_cameras`.
   257→- [ ] **AC-06:** `flyoverGeometry.compatible_cameras` includes `'static'` and `'gentle_float'`.
   258→- [ ] **AC-07:** `flyoverGeometry.compatible_cameras` includes `'slow_push_forward'` and `'slow_pull_back'`.
   259→- [ ] **AC-08:** `flyoverGeometry.compatible_cameras` includes `'flyover_glide'` (forward reference).
   260→- [ ] **AC-09:** `flyoverGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'`... [truncated]
Now I have a thorough understanding of the patterns. Let me also check the verified camera presets to know what's available.
[Tool: Grep]
  Input: {
  "pattern": "compatible.*Geometries|compatibleGeometries",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes",
  "output_mode": "content",
  "-C": 1
}
[Tool Result] <persisted-output>
Output too large (88.3KB). Full output saved to: /Users/austin/.claude/projects/-Users-austin-spatial-reasoning-video-generator-generations-depthkit/c442ed96-4e33-4377-8761-663d1cb62138/tool-results/toolu_01NAaeoNnuBFmDhcTUhxPsPJ.txt

Preview (first 2KB):
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/transcript.md-298-
nodes/OBJ-021/transcript.md:299:The geometry itself needs to work with whatever camera presets are compatible. Let me look at what the OBJ-027 push/pull presets say about flyover compatibility — they list `flyover` in their `compatibleGeometries`. So the flyover geometry needs to work with `slow_push_forward` (camera at [0,0,5] looking at [0,0,-30]) as well as a future `flyover_glide`.
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/transcript.md-300-
--
nodes/OBJ-021/transcript.md-796-  Input: {
nodes/OBJ-021/transcript.md:797:  "pattern": "compatible_geometries|compatibleGeometri... [truncated]

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-026/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-027/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md

[Tool: Grep]
  Input: {
  "pattern": "compatibleGeometries|diorama",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "output_mode": "content",
  "-C": 2
}
[Tool Result] 60-| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target. |
61-| `defaultEndState.fov` | `50` | No FOV animation. |
62:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | All geometries where forward Z motion is meaningful. Excludes `panorama` (rotation-based). See D4. |
63-| `tags` | `['push', 'forward', 'z_axis', 'depth', 'cinematic', 'defining_motion']` | |
64-
--
76-| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target. |
77-| `defaultEndState.fov` | `50` | |
78:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | Same as push_forward. |
79-| `tags` | `['pull', 'back', 'z_axis', 'reveal', 'cinematic']` | |
80-
--
215-### D4: Panorama excluded from compatible geometries
216-
217:**Decision:** Both presets exclude `panorama` from `compatibleGeometries`.
218-
219-**Rationale:** Panorama geometry (seed Section 4.2) uses a wide backdrop with camera rotation (panning... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "compatibleGeometries|diorama",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md",
  "output_mode": "content",
  "-C": 2
}
[Tool Result] 37-| `defaultStartState.fov` | `50` | Seed Section 8.2 default FOV |
38-| `defaultEndState` | Identical to `defaultStartState` | No motion — start and end are the same |
39:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']` | All eight geometries from seed Section 4.2. A static camera is universally safe. |
40-| `tags` | `['static', 'fixed', 'no_motion', 'baseline']` | Discoverability for LLM preset selection |
41-
--
112-### D5: Compatible with all eight geometries
113-
114:**Decision:** `compatibleGeometries` lists all eight geometries from seed Section 4.2.
115-
116-**Rationale:** A static camera produces zero displacement in all axes. It cannot cause edge reveals, cannot move outside a geometry's spatial envelope, and cannot conflict with any spatial arrangement. There is no geometry for which a static camera is invalid. Listing all eight explicitly (rather than using a wildcard, which OBJ-006 D6 prohibits) means each ... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "compatibleGeometries|diorama",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md",
  "output_mode": "content",
  "-C": 2
}
[Tool Result] 133-  defaultEasing: 'linear',  // See D2: easing affects position envelope only
134-
135:  compatibleGeometries: [
136-    'stage',
137-    'tunnel',
138-    'canyon',
139-    'flyover',
140:    'diorama',
141-    'portal',
142-    'panorama',
--
275-### Metadata
276-
277:- [ ] **AC-20:** `compatibleGeometries` includes all 8 geometry names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.
278-- [ ] **AC-21:** `oversizeRequirements.maxDisplacementX` equals 0.3.
279-- [ ] **AC-22:** `oversizeRequirements.maxDisplacementY` equals 0.2.
--
338-
339-**6. Metadata validation:**
340:- Verify all static fields (name, tags, compatibleGeometries, oversizeRequirements) match specified values.
341-- `validateCameraPathPreset(gentleFloat)` returns empty array.
342-
--
372-| **Scene sequencer** (OBJ-010) | Resolves `"camera": "gentle_float"` from manifest. |
373-| **Edge-reveal validator** (OBJ-040) | Uses `oversizeRequirements` (position displacements only; look... [truncated]
Good. Now I have all the context I need. Let me check the OBJ-003 spatial constants for reference:
[Tool: Grep]
  Input: {
  "pattern": "DEFAULT_CAMERA|PLANE_ROTATIONS|FACING_CAMERA",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003",
  "output_mode": "content",
  "-C": 2
}
[Tool Result] nodes/OBJ-003/meta.json-9-  "visual_status": null,
nodes/OBJ-003/meta.json-10-  "tuning_rounds": 0,
nodes/OBJ-003/meta.json:11:[Omitted long matching line]
nodes/OBJ-003/meta.json-12-  "status": "specified"
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/meta.json-13-}
--
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/transcript.md-32-
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/transcript.md-33-/** Default camera configuration (seed Section 8.2) */
nodes/OBJ-003/transcript.md:34:export const DEFAULT_CAMERA = {
nodes/OBJ-003/transcript.md-35-  fov: 50,           // vertical FOV in degrees
nodes/OBJ-003/transcript.md-36-  near: 0.1,         // near clipping plane in world units
--
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/transcript.md-53- * All values in radians.
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/... [truncated]
Now I have comprehensive context. Let me propose the complete specification.

---

# Specification: Diorama Scene Geometry (OBJ-022)

## Summary

OBJ-022 defines the **diorama** scene geometry — a semicircle of upright planes arranged at varying Z-depths, like layers of a Victorian paper theater. The defining visual characteristic is that wing planes on the left and right sides are **slightly rotated inward**, creating a curved spatial envelope. As the camera pushes in gently, these angled wings exhibit real perspective foreshortening — their far edges visibly recede while their near edges stay closer — producing a richer depth illusion than flat parallel layers. This is the closest geometry to traditional parallax but distinguished by the perspective distortion on the outer planes. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/diorama.ts

import type { SceneGeometry } from './types';

/**
 * The diorama scene geometry — a semicircle of planes at varying
 * Z-depths, like layers of a Victorian paper theater.
 *
 * Spatial arrangement: a large backdrop at deep Z, wing planes
 * on left and right at mid-depth rotated slightly inward (~18°),
 * a subject plane at shallow Z, and optional midground and
 * foreground planes. The wing rotation produces real perspective
 * foreshortening as the camera pushes in — the defining visual
 * distinction from flat layered parallax.
 *
 * This is the most traditional parallax-like geometry but with
 * genuine perspective distortion. Best for layered storytelling,
 * illustrated scenes, and theatrical compositions.
 */
export const dioramaGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'diorama'` | Matches seed Section 4.2 naming |
| `description` | `'A semicircle of planes at varying Z-depths, like a paper theater. Wing planes on left and right are rotated inward, producing real perspective foreshortening as the camera pushes in. The closest to traditional parallax but with genuine 3D depth distortion on the outer planes. Best for layered storytelling, illustrated scenes, and theatrical compositions.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes in gently." Forward push is the natural motion for a diorama — it enhances the perspective foreshortening on wing planes as the camera approaches. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'gentle_float', 'dramatic_push']` | See D4. Excludes geometry-specific cameras (tunnel_push_forward, flyover_glide) and lateral tracks (wing rotation makes lateral motion risky for edge reveals). |
| `fog` | `{ color: '#0d0d1a', near: 15, far: 45 }` | Dark blue-tinged fog for theatrical atmosphere. See D5. |
| `preferred_aspect` | `'landscape'` | The semicircular wing arrangement reads best in a wide frame. In portrait, the wings would be cropped or squeezed. |

### Slot Definitions

The diorama geometry defines **6 slots** — 2 required, 4 optional. The backdrop and subject provide the essential spatial structure; wings, midground, and foreground are compositional enhancements that create the full paper-theater effect.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate camera motion at `speed=1.0` for the default camera (`slow_push_forward`, which has `maxDisplacementZ = 8` per OBJ-027).

Following the convention established by OBJ-018: the diorama geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -30]` | Deep Z, serves as the "painted background" of the paper theater. Distance from camera: 35 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane facing the camera. |
| `size` | `[75, 45]` | Oversized to prevent edge reveals during camera push. Frustum visible area at distance 35: ~32.6h × 58.0w (16:9). Width 75 ≥ 58.0 (~1.29× oversize), height 45 ≥ 32.6 (~1.38× oversize). Sufficient for `slow_push_forward`'s 8-unit Z displacement. |
| `required` | `true` | Every diorama needs a background — it is the "painted backdrop" of the theater. |
| `description` | `'Painted backdrop — the background scene visible through and behind all other layers.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backdrop is opaque. |
| `fogImmune` | `true` | The backdrop at Z=-30 (distance 35) would be significantly faded by fog (near=15, far=45). Marking it fog-immune ensures it remains vivid — the visual depth cue comes from the wing foreshortening, not from backdrop fading. |

#### Slot: `wing_left`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[-8, 0, -18]` | Left of center (X=-8), mid-depth (Z=-18). Distance from camera on Z-axis: 23 units. |
| `rotation` | `[0, Math.PI / 10, 0]` | Rotated ~18° around the Y-axis, angling the plane to face slightly toward center-right. This inward rotation is the defining spatial feature of the diorama — it creates real perspective foreshortening as the camera pushes forward. |
| `size` | `[18, 28]` | Tall and moderately wide. Height 28 ensures the wing fills the vertical frame at its distance (visible height at distance 23: ~21.5). Width 18 provides the scenic side panel. After rotation, the effective on-screen width narrows due to foreshortening (~18 × cos(π/10) ≈ 17.1), which is the intended visual effect. |
| `required` | `false` | Optional — a diorama can function with just backdrop + subject. However, wings are what distinguish the diorama from a stage, so SKILL.md should strongly recommend including at least one wing pair. |
| `description` | `'Left scenic wing panel — angled inward like a theater wing flat. Undergoes perspective foreshortening as the camera pushes in.'` | |
| `renderOrder` | `1` | Renders above backdrop. |
| `transparent` | `true` | Wing images should have alpha transparency so the backdrop is visible through gaps/cutouts in the wing artwork (foliage edges, architectural elements). |
| `fogImmune` | `false` | Wings at mid-depth benefit from subtle fog to enhance depth separation from the subject. |

#### Slot: `wing_right`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[8, 0, -18]` | Right of center (X=8), mirrors `wing_left`. |
| `rotation` | `[0, -Math.PI / 10, 0]` | Rotated ~18° inward (negative Y rotation = faces slightly toward center-left). Mirror of `wing_left`'s rotation. |
| `size` | `[18, 28]` | Matches `wing_left` for symmetry. |
| `required` | `false` | Optional. Typically used as a symmetric pair with `wing_left`. |
| `description` | `'Right scenic wing panel — angled inward like a theater wing flat. Mirrors the left wing.'` | |
| `renderOrder` | `1` | Same as `wing_left` — they don't overlap laterally, so no ordering conflict. |
| `transparent` | `true` | Same rationale as `wing_left`. |
| `fogImmune` | `false` | Same as `wing_left`. |

#### Slot: `midground`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -12]` | Between wings and subject. Distance from camera: 17 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. The midground is a flat layer parallel to the camera, not rotated like the wings. This contrast between rotated wings and flat center layers enhances the paper-theater layering effect. |
| `size` | `[35, 22]` | Frustum visible area at distance 17: ~15.9h × 28.2w. Width 35 ≥ 28.2 (~1.24× oversize), height 22 ≥ 15.9 (~1.38× oversize). |
| `required` | `false` | Optional — adds an intermediate scenic layer between wings and subject. |
| `description` | `'Middle-distance scenic element — an intermediate layer between the wings and subject. Environmental details, secondary scenery.'` | |
| `renderOrder` | `2` | Renders above wings. |
| `transparent` | `true` | Midground elements should have alpha so backdrop/wings show through gaps. |
| `fogImmune` | `false` | Mid-distance fog fading is appropriate. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -0.5, -5]` | Shallow Z, slightly below center to appear grounded. Distance from camera: 10 units. Matches the stage geometry's subject position (OBJ-018) for consistency. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[12, 12]` | Sized to fill roughly 50-65% of frame height. Frustum visible height at distance 10: ~9.33. Height 12 / 9.33 ≈ 1.29× — provides margin. Square default accommodates both portrait and landscape subject images via texture aspect-ratio auto-sizing (OBJ-040). Focal element, not a coverage plane. |
| `required` | `true` | The subject is the focal point of every diorama scene. |
| `description` | `'Primary subject — person, character, object, or focal element. Should have a transparent background.'` | |
| `renderOrder` | `3` | Renders above midground and wings. |
| `transparent` | `true` | Subject images need alpha transparency. |
| `fogImmune` | `false` | Subject at distance 10 is within the fog-free zone (fog near=15). |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -1]` | Very close to camera. Distance from camera: 6 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
| `size` | `[25, 16]` | Oversized relative to frustum at this distance (visible ~5.6h × 9.9w). Foreground framing extends beyond the frame edges. |
| `required` | `false` | Optional — adds foreground framing that enhances the "looking through layers" paper-theater effect. |
| `description` | `'Foreground framing element — decorative edges, foliage, particles, or a theatrical proscenium arch. Should have a transparent background.'` | |
| `renderOrder` | `4` | Renders on top of everything. |
| `transparent` | `true` | Must have alpha to not occlude the scene behind it. |
| `fogImmune` | `true` | Foreground is close to camera — fog would look physically wrong. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `backdrop` | `[0, 0, -30]` | `[0, 0, 0]` | `[75, 45]` | **yes** | no | **yes** | 0 |
| `wing_left` | `[-8, 0, -18]` | `[0, PI/10, 0]` | `[18, 28]` | no | yes | no | 1 |
| `wing_right` | `[8, 0, -18]` | `[0, -PI/10, 0]` | `[18, 28]` | no | yes | no | 1 |
| `midground` | `[0, 0, -12]` | `[0, 0, 0]` | `[35, 22]` | no | no | no | 2 |
| `subject` | `[0, -0.5, -5]` | `[0, 0, 0]` | `[12, 12]` | **yes** | yes | no | 3 |
| `near_fg` | `[0, 0, -1]` | `[0, 0, 0]` | `[25, 16]` | no | yes | **yes** | 4 |

### Registration Side Effect

```typescript
// src/scenes/geometries/diorama.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(dioramaGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/diorama.ts
export { dioramaGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./diorama` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Six slots — backdrop, wing pair, midground, subject, near_fg

The diorama uses 6 slots with only 2 required (`backdrop`, `subject`). The minimum viable diorama is backdrop + subject — functionally similar to a simplified stage but with different fog and defaults. The full paper-theater effect requires the wing pair and ideally `near_fg` for a proscenium-arch framing effect.

Six slots is at the upper bound of TC-01's 3-5 range. With 4 optional, most compositions use 4-5 filled slots (backdrop + wings + subject, optionally midground and/or near_fg), which is squarely within the range.

**Why wings are optional, not required:** Making wings required would force every diorama manifest to include wing images, which is a higher authoring burden. An LLM might want a simple layered scene without the theatrical wing effect. By making wings optional but documenting them as "strongly recommended," SKILL.md can guide toward the full effect without rejecting simpler compositions.

### D2: Wing rotation angle — π/10 (~18°)

The wings are rotated inward by π/10 radians (~18°) around the Y-axis. This angle was chosen as a balance between visual effect and practical constraints:

- **Too small (< 10°):** The perspective foreshortening is barely noticeable, and the diorama loses its distinguishing characteristic versus a stage.
- **Too large (> 30°):** The wings become nearly perpendicular to the camera, showing mostly their edge. Text or detailed imagery on the wing would be severely distorted. Also, more of the wing's surface faces away from the camera, increasing the chance of visible texture stretching.
- **~18° (π/10):** Produces visible foreshortening — the far edge of each wing visibly recedes as the camera pushes forward — while keeping the wing's imagery legible. The foreshortening factor is cos(18°) ≈ 0.95, meaning the wing loses only ~5% apparent width to rotation, but the perspective *change* during camera motion is the key visual (not the static appearance).

This angle is a starting point for visual tuning (OBJ-063). The Director Agent may recommend adjustments.

### D3: No floor plane — the diorama is a flat-layer composition

Unlike the stage geometry (which has a `floor` slot), the diorama intentionally omits a floor. A paper theater / diorama is a composition of flat upright cutouts at varying depths — there is no ground surface. Adding a floor would conflate the diorama with the stage geometry.

If an author wants a floor-like element, they can use the `midground` slot with a `position_override` to place and rotate it as a floor, or they should choose the `stage` geometry instead. This keeps the diorama's identity clear and distinct.

### D4: Compatible cameras — excludes lateral tracks and geometry-specific presets

The diorama lists five compatible cameras:

- **`static`** (OBJ-026, verified): Universal baseline. A static paper-theater tableau.
- **`slow_push_forward`** (OBJ-027, verified): The defining motion for dioramas — pushing into the layered scene. **Serves as `default_camera`**. The forward push maximally exercises the wing foreshortening effect.
- **`slow_pull_back`** (OBJ-027, verified): Reverse pull-back reveals the full paper-theater composition. Listed in OBJ-027's `compatibleGeometries` for diorama.
- **`gentle_float`** (OBJ-031, verified): Subtle ambient drift. Works universally.
- **`dramatic_push`** (not yet verified): A faster forward push for emphasis moments. Forward reference — to be validated by OBJ-063 tuning.

Excluded:
- **`tunnel_push_forward`**: Tuned for enclosed corridor geometries. The diorama has no walls/ceiling/floor.
- **`flyover_glide`**: Requires a ground plane below the camera. The diorama has no ground.
- **`lateral_track_left/right`**: Lateral tracking with rotated wings risks revealing the wing planes' back faces or edges. The wing rotation means the camera would approach one wing and retreat from the other during lateral motion, creating asymmetric and potentially jarring perspective shifts. Excluded for V1; could be added after OBJ-063 tuning validates edge-reveal safety.
- **`crane_up`**: Vertical camera motion in a flat-layer composition has little spatial meaning. Excluded for V1.
- **`dolly_zoom`**: FOV animation needs careful validation with wing rotation. Deferred.

### D5: Fog settings — theatrical atmosphere

The diorama uses dark blue-tinged fog (`#0d0d1a`) with `near: 15, far: 45`. This creates a theatrical, slightly mysterious atmosphere appropriate for a paper-theater staging.

- `near: 15` leaves the subject (distance ~10), `near_fg` (distance ~6), and `midground` (distance ~17, barely touched) fully or nearly clear.
- `far: 45` fades distant elements. The backdrop at distance 35 would be ~67% fogged at these settings — hence `backdrop` is `fogImmune: true`.
- The wings at distance 23 receive light fog (~27%), which subtly separates them from the subject.

The dark blue tint (vs the stage's pure black or the flyover's light blue-gray) gives the diorama a distinctive mood — slightly nocturnal, theatrical. Authors can override via the manifest's fog settings.

### D6: Backdrop is fog-immune

The backdrop at Z=-30 (distance 35) falls squarely within the fog range (near=15 to far=45). Without fog immunity, it would be ~67% fogged, making it nearly invisible. Since the backdrop is the "painted scenery" of the paper theater and should remain vivid, it is marked `fogImmune: true`. The depth cue in a diorama comes from wing foreshortening and inter-layer parallax, not from atmospheric fading of the backdrop.

### D7: Wing positions at X=±8, Z=-18

The wings are positioned at X=±8, placing them near the left and right edges of the visible frame at their Z-distance. At Z=-18 (distance 23 from camera), the frustum half-width is approximately `23 × tan(25°) × (16/9) ≈ 19.1`. The wing center at X=±8 with width 18 (half-width 9) means the wing extends from X=±(8-9)=∓1 to X=±(8+9)=±17. The inner edge at X=∓1 overlaps the center of the frame slightly, while the outer edge at X=±17 is within the frustum half-width of ±19.1.

After the π/10 rotation, the wing's projected footprint on screen shifts slightly. The near edge (closest to center) appears wider; the far edge (toward the frame edge) appears narrower. This is the intended foreshortening effect.

### D8: midground is not transparent — design choice for coverage

The `midground` slot has `transparent: false`. Unlike the wings (which need alpha for scenic cutout effects), the midground serves as a solid intermediate scenic layer — a terrain feature, forest line, or architectural element that fills its region of the frame. This matches the stage geometry's midground treatment (OBJ-018). Authors who need a transparent midground can set `transparent: true` via a material override in a future extension, or use `near_fg` for transparent foreground elements.

**Revision note:** On further reflection, the midground in a diorama-style paper theater is typically a scenic cutout (e.g., a tree line, building silhouette) with irregular edges, where the backdrop should show through gaps. I'll mark `midground` as `transparent: true` to support this paper-theater aesthetic. This differs from the stage geometry where the midground is a full-width environmental band.

### D9: `preferred_aspect` is `landscape`

The semicircular wing arrangement is the diorama's defining feature. In landscape (16:9), the wings have room to spread laterally and the inward rotation is visible. In portrait (9:16), the narrow frame width means the wings would either crowd the center or be cropped off the sides, losing the semicircular effect. The geometry renders correctly in portrait (seed C-04), but SKILL.md should guide LLMs toward landscape.

### D10: Subject position matches stage geometry

The subject is at `[0, -0.5, -5]` — identical to the stage geometry (OBJ-018 D4). This consistency means LLMs can expect the subject to appear similarly framed across geometries, making geometry selection less error-prone. The slight Y=-0.5 offset places the subject slightly below center, a standard compositional choice.

### D11: PlaneSlot construction, not DepthSlot — follows OBJ-018 convention

Same as OBJ-018 and OBJ-021: the geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration. OBJ-007's `DepthSlot` fields (`promptGuidance`, `expectsAlpha`) are not part of the `PlaneSlot` type.

**Prompt guidance gap for geometry-specific slots:** The diorama introduces custom slots (`wing_left`, `wing_right`) not present in OBJ-007's `DEFAULT_SLOT_TAXONOMY`. Downstream consumers (OBJ-071 SKILL.md, OBJ-053) must derive prompt guidance from `PlaneSlot.description` fields. This is the same gap noted in OBJ-018 and OBJ-021.

### D12: Explicit optional field policy — follows OBJ-018 convention

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

### D13: Wing renderOrder tie is intentional

Both `wing_left` and `wing_right` share `renderOrder: 1`. Since they are laterally separated (X=-8 vs X=8) and the camera has no lateral track in the compatible cameras list, they occupy different screen regions and never compete for draw order. The Z-buffer handles any theoretical overlap correctly since they're at the same Z-depth.

## Acceptance Criteria

- [ ] **AC-01:** `dioramaGeometry.name` is `'diorama'`.
- [ ] **AC-02:** `dioramaGeometry.slots` contains exactly 6 keys: `backdrop`, `wing_left`, `wing_right`, `midground`, `subject`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `backdrop`, `subject` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `dioramaGeometry.default_camera` is `'slow_push_forward'`.
- [ ] **AC-05:** `dioramaGeometry.default_camera` appears in `dioramaGeometry.compatible_cameras`.
- [ ] **AC-06:** `dioramaGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (verified presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `dioramaGeometry.compatible_cameras` includes `'slow_push_forward'` and `'slow_pull_back'` (verified presets from OBJ-027).
- [ ] **AC-08:** `dioramaGeometry.compatible_cameras` includes `'dramatic_push'` (forward reference).
- [ ] **AC-09:** `dioramaGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, or `'lateral_track_right'`.
- [ ] **AC-10:** `dioramaGeometry.compatible_cameras` contains exactly 5 entries.
- [ ] **AC-11:** `dioramaGeometry.fog` is `{ color: '#0d0d1a', near: 15, far: 45 }`.
- [ ] **AC-12:** `dioramaGeometry.description` is non-empty and describes a paper-theater / semicircle-of-planes arrangement.
- [ ] **AC-13:** `dioramaGeometry.preferred_aspect` is `'landscape'`.
- [ ] **AC-14:** The `wing_left` slot rotation is `[0, Math.PI / 10, 0]` (positive Y rotation, ~18° inward).
- [ ] **AC-15:** The `wing_right` slot rotation is `[0, -Math.PI / 10, 0]` (negative Y rotation, ~18° inward, mirroring `wing_left`).
- [ ] **AC-16:** All non-wing slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-17:** `wing_left`, `wing_right`, `midground`, `subject`, and `near_fg` have `transparent: true`. `backdrop` has `transparent: false`.
- [ ] **AC-18:** `backdrop` and `near_fg` have `fogImmune: true`. All other slots have `fogImmune: false`.
- [ ] **AC-19:** `renderOrder` values are: backdrop(0), wing_left(1), wing_right(1), midground(2), subject(3), near_fg(4). No other values.
- [ ] **AC-20:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-21:** `registerGeometry(dioramaGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-22:** All slot `description` fields are non-empty strings.
- [ ] **AC-23:** All slot `size` components are positive (> 0).
- [ ] **AC-24:** For the `backdrop` slot (coverage plane, distance 35): size [75, 45] >= frustum visible area (~58.0w × 32.6h at FOV=50°, 16:9).
- [ ] **AC-25:** For the `midground` slot (coverage plane, distance 17): size [35, 22] >= frustum visible area (~28.2w × 15.9h).
- [ ] **AC-26:** For the `near_fg` slot (coverage plane, distance 6): size [25, 16] >= frustum visible area (~9.9w × 5.6h).
- [ ] **AC-27:** Wing slots and subject slot are exempt from full-frustum coverage check — wings are scenic side panels (not full-frame coverage), subject is a focal element.
- [ ] **AC-28:** Slot Z-positions decrease (go more negative) as depth increases: `near_fg` (-1) > `subject` (-5) > `midground` (-12) > wings (-18) > `backdrop` (-30).
- [ ] **AC-29:** The module self-registers via `registerGeometry(dioramaGeometry)` as a side effect of import.
- [ ] **AC-30:** The module exports `dioramaGeometry` as a named export.
- [ ] **AC-31:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants.
- [ ] **AC-32:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-33:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-34:** `wing_left.position[0]` is the negation of `wing_right.position[0]` (lateral symmetry: -8 vs 8).
- [ ] **AC-35:** `wing_left.size` equals `wing_right.size`.
- [ ] **AC-36:** `wing_left.rotation[1]` is the negation of `wing_right.rotation[1]` (rotation symmetry: π/10 vs -π/10).

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`backdrop`, `subject`) | Valid scene. Minimal diorama — functionally similar to a very simple stage but with different fog and description. No wing foreshortening. |
| Manifest provides all 6 slots | Valid scene. Full paper-theater effect with maximum depth layering. |
| Manifest provides `wing_left` but not `wing_right` | Valid. Asymmetric composition — only one side has a scenic wing. The scene is lopsided but artistically valid. |
| Manifest provides `wing_right` but not `wing_left` | Valid. Asymmetric composition. |
| Manifest provides wings but no midground | Valid. Common composition — wings and subject with no intermediate layer. |
| Manifest uses `floor` or `ceiling` (not diorama slots) | Rejected by manifest validation (OBJ-017). Error names the invalid key and lists valid diorama slot names. |
| Manifest uses `back_wall` instead of `backdrop` | Rejected — the diorama uses `backdrop`, not the default taxonomy's `back_wall`. |
| Camera pushes forward far enough that wing edges become visible | Wing height 28 at distance 23 (before push) fills ~130% of visible height. After an 8-unit push (camera at Z=-3), distance to wings is 15. Visible height at 15: ~14.0. Wing height 28 / 14.0 = 2.0× oversize — still safe. Horizontal coverage depends on wing position relative to frustum edge — OBJ-040 validates formally. |
| Portrait mode (9:16) | Geometry renders correctly. Narrower width means wings at X=±8 may be partially outside frame. `preferred_aspect: 'landscape'` guides LLMs away. |
| Wing back-face visibility | Wings rotated at π/10 show only their front face. Even at maximum camera push (Z=-3), the camera is still in front of the wings (Z=-18). No risk of seeing the wing from behind. Three.js `side: THREE.FrontSide` (default for meshBasicMaterial) would additionally prevent back-face rendering. |
| Fog completely obscuring the wings | Wings at distance 23 with fog near=15, far=45: fog factor ≈ (23-15)/(45-15) ≈ 0.27 (27% fogged). Visible but subtly faded — intentional for depth separation. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `diorama.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'diorama' is already registered." Module relies on Node.js module caching. |
| `diorama.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'diorama': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `dioramaGeometry.name` is `'diorama'`.
2. `dioramaGeometry.slots` has exactly 6 keys: `backdrop`, `wing_left`, `wing_right`, `midground`, `subject`, `near_fg`.
3. Required slots: `backdrop`, `subject`. Optional: `wing_left`, `wing_right`, `midground`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'slow_push_forward'` and is in `compatible_cameras`.
6. `compatible_cameras` contains exactly 5 entries, all matching `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` is `'#0d0d1a'`.
8. `description` is non-empty.
9. `preferred_aspect` is `'landscape'`.

**Slot spatial correctness tests:**
10. `wing_left` rotation is `[0, Math.PI / 10, 0]`.
11. `wing_right` rotation is `[0, -Math.PI / 10, 0]`.
12. All non-wing slots have rotation `[0, 0, 0]`.
13. Z-positions ordered: `near_fg` (-1) > `subject` (-5) > `midground` (-12) > wings (-18) > `backdrop` (-30).
14. `renderOrder` values: backdrop(0) < wings(1) < midground(2) < subject(3) < near_fg(4).
15. All `size` components are > 0.

**Slot metadata tests:**
16. `wing_left`, `wing_right`, `midground`, `subject`, `near_fg` have `transparent: true`.
17. `backdrop` has `transparent: false`.
18. `backdrop`, `near_fg` have `fogImmune: true`.
19. `wing_left`, `wing_right`, `midground`, `subject` have `fogImmune: false`.
20. All slot `description` fields are non-empty.
21. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
22. `validateGeometryDefinition(dioramaGeometry)` returns an empty error array.
23. `registerGeometry(dioramaGeometry)` does not throw (when registry is not locked).
24. After registration, `getGeometry('diorama')` returns the diorama geometry.

**Frustum size validation tests:**
25. `backdrop` size [75, 45] >= visible area at Z-distance 35 with FOV=50° and 16:9 (~58.0w × 32.6h).
26. `midground` size [35, 22] >= visible area at Z-distance 17 (~28.2w × 15.9h).
27. `near_fg` size [25, 16] >= visible area at Z-distance 6 (~9.9w × 5.6h).
28. Wing slots: exempt (scenic side panels, not full-frame coverage).
29. `subject` slot: exempt (focal element, not coverage plane).

**Compatible cameras tests:**
30. `compatible_cameras` includes `'static'`, `'slow_push_forward'`, `'slow_pull_back'`, `'gentle_float'`, `'dramatic_push'`.
31. `compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, `'lateral_track_right'`.

**Symmetry tests:**
32. `wing_left.position[0]` is the negation of `wing_right.position[0]`.
33. `wing_left.size` equals `wing_right.size`.
34. `wing_left.renderOrder` equals `wing_right.renderOrder`.
35. `wing_left.rotation[1]` is the negation of `wing_right.rotation[1]`.

### Relevant Testable Claims

- **TC-01** (partial): The diorama uses 6 slots (2 required, 4 optional), within the 3-5 effective range for most compositions.
- **TC-04** (partial): All spatial relationships defined by geometry. LLM specifies `geometry: 'diorama'` and maps images to slot names — no XYZ coordinates.
- **TC-08** (partial): The diorama covers layered/illustrated/theatrical scene types that other geometries (stage, tunnel) do not naturally express.

## Integration Points

### Depends on

| Upstream | What OBJ-022 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types. `registerGeometry` function. |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`). `DEFAULT_SLOT_TAXONOMY` for reference only (diorama shares `midground`, `subject`, `near_fg` concepts). |
| **OBJ-003** (Spatial math) | `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. `PLANE_ROTATIONS.FACING_CAMERA` for non-wing slot rotations (conceptually — the actual value `[0,0,0]` is trivial). |

### Consumed by

| Downstream | How it uses OBJ-022 |
|------------|---------------------|
| **OBJ-063** (Diorama visual tuning) | Director Agent reviews test renders; may adjust wing angle, positions, sizes, fog. |
| **OBJ-070** (End-to-end render test) | May use diorama as a test geometry. |
| **OBJ-071** (SKILL.md) | Documents diorama slot names, descriptions, usage guidance. Must source prompt guidance from `PlaneSlot.description` fields for geometry-specific slots (`wing_left`, `wing_right`). |
| **OBJ-017** (Manifest validation) | Looks up `getGeometry('diorama')` to validate manifest plane keys. |
| **OBJ-036** (Scene sequencer) | Resolves slot spatial data for diorama scenes. |
| **OBJ-039** (Page-side renderer) | Creates Three.js meshes from slot data — notably, wing slots require rotation to be correctly applied to the mesh. |
| **OBJ-040** (Edge-reveal validation) | Validates camera paths don't reveal plane edges. Wing planes with rotation require non-trivial frustum intersection calculations due to foreshortening. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatible_cameras`. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        diorama.ts        # dioramaGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./diorama
```

## Open Questions

### OQ-A: Is π/10 (~18°) the optimal wing rotation angle?

The angle is a heuristic starting point chosen for visible-but-not-excessive foreshortening. The Director Agent (OBJ-063) should evaluate:
- Whether the foreshortening is noticeable enough to justify the diorama as a distinct geometry from the stage.
- Whether wing imagery (text, detailed illustrations) remains legible at this rotation.
- Whether a slightly larger angle (π/8 = 22.5°) produces a more dramatic effect worth the extra distortion.

**Recommendation:** Start at π/10. Adjust during OBJ-063 tuning based on visual feedback. Document the final tuned value.

### OQ-B: Should wings have different Z-positions for a staggered arrangement?

Currently both wings are at Z=-18. Staggering them (e.g., left at Z=-20, right at Z=-16) would create additional depth variety. However, this breaks the lateral symmetry and makes the paper-theater metaphor less clean.

**Recommendation:** Keep symmetric for V1. Staggered wings can be achieved via `position_override` in the manifest. If the Director Agent recommends staggering during tuning, adjust then.

### OQ-C: Should there be a `proscenium` slot?

A dedicated slot for a theatrical proscenium arch (the decorative frame around a stage opening) could reinforce the paper-theater metaphor. This would be at shallow Z, similar to `near_fg`, but specifically designed for an arch/frame effect.

**Recommendation:** `near_fg` already serves this purpose. The `description` explicitly mentions "a theatrical proscenium arch." Adding a separate slot would increase the slot count without meaningful spatial distinction. Defer.

### OQ-D: Should the `midground` slot be transparent?

D8 initially set `midground` as not transparent, then revised to `transparent: true` for the paper-theater cutout aesthetic. This is a judgment call about the typical use case. If midground is more often a solid scenic band (like a hillside), `transparent: false` is better. If it's more often a scenic cutout (like a tree line with sky visible through gaps), `transparent: true` is better.

**Recommendation:** `transparent: true` is correct for the diorama's paper-theater identity. Stage's midground serves the "solid environmental band" use case. The diorama's midground is a scenic cutout.

---

I believe this specification is complete and consistent with the established patterns from OBJ-018 (stage) and OBJ-021 (flyover). I'd like the Challenger to review and verify, paying particular attention to:

1. The wing rotation angle choice (π/10) and its spatial implications
2. The fog immunity of the backdrop (a departure from the stage pattern where backdrop is NOT fog-immune)
3. The `midground` transparency choice
4. The compatible cameras list (especially the exclusion of lateral tracks and inclusion of `dramatic_push` as a forward reference)
5. Whether 2 required slots (backdrop + subject) is too minimal for a geometry whose identity depends on the wings

---

## Round 2 — spec_challenger

I'll review this spec carefully, checking against OBJ-005, OBJ-007, the seed, and the established patterns from OBJ-018 and OBJ-021.

Let me first verify a few details from the dependency specs and existing geometries.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Grep",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]
Let me check key details from OBJ-018 and the camera preset specs to verify claims in this proposal.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "limit": 120
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "limit": 120
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "offset": 120,
  "limit": 80
}
[Tool Result]    120→#### Slot: `near_fg`
   121→
   122→| Field | Value | Notes |
   123→|-------|-------|-------|
   124→| `position` | `[0, 0, -1]` | Very close to camera. Distance from camera: 6 units. |
   125→| `rotation` | `[0, 0, 0]` | `FACING_CAMERA`. |
   126→| `size` | `[25, 16]` | Oversized to fill the frame edge-to-edge at close range. Frustum visible area at distance 6: ~5.60 x 9.95. Dramatically oversized because foreground elements typically extend beyond the frame (particles, foliage edges). |
   127→| `required` | `false` | Optional — adds foreground framing but many scenes work without it. |
   128→| `description` | `'Foreground framing element — foliage, particles, bokeh, or decorative edges. Should have a transparent background.'` | |
   129→| `renderOrder` | `4` | Renders on top of everything. |
   130→| `transparent` | `true` | Foreground elements need alpha to not occlude the subject. |
   131→| `fogImmune` | `true` | Foreground is so close that any fog application would look... [truncated]
Now let me check the `dramatic_push` preset status — it's referenced as compatible but I need to verify its existence:
[Tool: Grep]
  Input: {
  "pattern": "dramatic_push",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes",
  "output_mode": "files_with_matches"
}
[Tool Result] Found 12 files
nodes/OBJ-071/transcript.md
nodes/OBJ-071/output.md
nodes/OBJ-070/transcript.md
nodes/OBJ-070/output.md
nodes/OBJ-021/transcript.md
nodes/OBJ-021/output.md
nodes/OBJ-020/transcript.md
nodes/OBJ-020/output.md
nodes/OBJ-018/transcript.md
nodes/OBJ-018/output.md
nodes/OBJ-006/transcript.md
nodes/OBJ-006/output.md

[Tool: Grep]
  Input: {
  "pattern": "dramatic_push\",\n<parameter name=\"path\">/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "output_mode": "content",
  "-C": 1
}
[Tool Result] No matches found

[Tool: Grep]
  Input: {
  "pattern": "OBJ-028|OBJ-029|OBJ-030|OBJ-033|OBJ-034",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "output_mode": "content",
  "-C": 1
}
[Tool Result] 195-
196:**Forward reference note:** Of the 8 listed presets, `static` (OBJ-026) and `gentle_float` (OBJ-031) are verified. The remaining 6 (`slow_push_forward`, `slow_pull_back`, `lateral_track_left`, `lateral_track_right`, `dramatic_push`, `crane_up`) are forward references to presets in OBJ-027 through OBJ-034 (open/in-progress). The `compatible_cameras` list may be revised as those presets are specified and OBJ-041 validates compatibility.
197-
Now let me check which OBJs correspond to `dramatic_push`:
[Tool: Grep]
  Input: {
  "pattern": "dramatic_push|dramatic.push",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "output_mode": "content",
  "-C": 1
}
[Tool Result] 715-| **OBJ-031** (`gentle_float`) | Implements `CameraPathPreset`. Multi-axis sinusoidal. |
716:| **OBJ-032** (`dramatic_push`) | Implements `CameraPathPreset`. Aggressive ease-out Z push. |
717-| **OBJ-033** (`crane_up`) | Implements `CameraPathPreset`. Y-axis rise. |
Good — `dramatic_push` is OBJ-032 which is status `open`. Now let me check the OBJ-018 summary table for midground transparency specifically:

Looking at OBJ-018's slot summary table (line 140), the stage `midground` has `transparent: false`. The proposed diorama spec has `midground` as `transparent: true` — which is fine as a different artistic choice, but D8 has a confusing self-contradiction. Let me now do a thorough review.

---

## Challenger Review — Round 1

Overall, this is a well-structured spec that follows established patterns from OBJ-018 and OBJ-021 faithfully. The spatial reasoning is sound, the acceptance criteria are numerous and specific, and the design decisions are well-documented. Here are my findings:

### APPROVED — Things That Work Well

1. **Pattern compliance**: The spec correctly follows OBJ-018's established conventions — `PlaneSlot` construction (not `DepthSlot`), explicit optional fields, self-registration, barrel export pattern.
2. **Wing rotation concept**: π/10 is a reasonable starting point. The spec correctly identifies this as the diorama's distinguishing spatial feature and defers final tuning to OBJ-063.
3. **Symmetry constraints**: AC-34, AC-35, AC-36 explicitly test wing symmetry. Good.
4. **Frustum math**: The oversize calculations are correct and well-documented.
5. **Compatible cameras**: The exclusion rationale is sound — lateral tracks with rotated wings are genuinely risky.
6. **Subject position consistency with stage**: Good for LLM authorability (D10).

### Issues

#### Issue 1: D8 self-contradicts — midground transparency flip is confusing (Minor)

D8 starts by arguing `midground` should be `transparent: false`, then adds a "Revision note" reversing to `transparent: true`. The final slot table and AC-17 correctly show `transparent: true`, so the spec is internally consistent on the *outcome*. But the design decision reads like a draft with tracked changes. 

**Fix**: Rewrite D8 to state the final decision directly, with the rationale for choosing `transparent: true` for the diorama (paper-theater cutout aesthetic) vs `transparent: false` for the stage (solid environmental band). Remove the "On further reflection" narrative. OQ-D then becomes unnecessary since D8 already made the call.

#### Issue 2: AC-17 says midground is transparent, but slot table says midground is NOT transparent (Critical)

Looking more carefully at the **Slot Summary Table**:

```
| `midground` | `[0, 0, -12]` | `[0, 0, 0]` | `[35, 22]` | no | **no** | no | 2 |
```

The midground column under "Transparent" shows **no**. But:
- AC-17 says: "`wing_left`, `wing_right`, `midground`, `subject`, and `near_fg` have `transparent: true`"
- The detailed midground slot section says: (D8 revision) `transparent: true`

The slot summary table has `midground` as NOT transparent, contradicting AC-17 and the revised D8 decision. One of these is wrong.

**Fix**: Update the slot summary table to show `midground` as `yes` under Transparent, consistent with AC-17 and the revised D8 decision.

#### Issue 3: `near_fg` fog immunity vs subject fog range — fog `near: 15` creates a dead zone for the subject (Minor)

The spec says fog `near: 15`. The subject is at distance 10 from the camera. That's correct — the subject is outside the fog range and renders clearly. But the spec says in the `subject` slot notes: "Subject at distance 10 is within the fog-free zone (fog near=15)." This is correct but the phrasing "within the fog-free zone" is slightly ambiguous — it could be misread as "within the fog zone." 

**Fix**: Rephrase to: "Subject at distance 10 is closer than fog.near (15), so fog has zero effect."

#### Issue 4: Wing oversize validation is hand-waved for camera push (Major)

The spec says (Edge Cases section): "After an 8-unit push (camera at Z=-3), distance to wings is 15. Visible height at 15: ~14.0. Wing height 28 / 14.0 = 2.0× oversize — still safe."

But this only validates the *vertical* dimension. The *horizontal* dimension is more interesting because the wings are rotated. The wing at X=-8 with rotation π/10 around Y projects differently as the camera approaches. The edge-reveal analysis should address the *lateral* extent of the wings relative to the frustum width at the wing's Z-depth as the camera pushes forward.

At the closest approach (camera Z=-3, wing Z=-18, distance 15):
- Frustum half-width at distance 15: `15 × tan(25°) × (16/9) ≈ 12.4`
- Wing center at X=-8, half-width ~9 (before rotation), so wing extends from X=+1 to X=-17.
- Frustum extends from X=-12.4 to X=+12.4.
- The wing's outer edge at X=-17 is *outside* the frustum (safely hidden). The inner edge at X=+1 is inside. So the wing is partially visible — correct for a scenic side panel.
- But does the outer edge of the wing reveal a hard boundary that breaks the illusion? The wing ends at X=-17, and the frustum shows up to X=-12.4, so the wing extends 4.6 units past the visible area. Safe.

The analysis is actually fine on closer examination, but the spec only does the vertical check. The wing's rotated projection makes the horizontal analysis non-trivial, and this is exactly what OBJ-040 is supposed to validate formally.

**Fix**: Add a note to the edge case section that says: "Full edge-reveal validation for rotated wings under camera motion is deferred to OBJ-040. The manual analysis above covers the vertical dimension; the horizontal dimension is safe because wings extend ~4.6 units past the visible frustum edge at maximum camera push." This documents the reasoning rather than leaving it implicit.

#### Issue 5: `dramatic_push` is OBJ-032, status `open` — forward reference should be noted consistently (Minor)

The spec notes `dramatic_push` as a forward reference in D4 but doesn't identify which OBJ it corresponds to (OBJ-032). OBJ-018 set a precedent of noting forward references with their OBJ numbers. This helps traceability.

**Fix**: In D4, add "(forward reference to OBJ-032)" after `dramatic_push`, matching OBJ-018's forward-reference convention.

#### Issue 6: Missing explicit statement about OBJ-003 constant usage (Minor)

OBJ-018 explicitly references `PLANE_ROTATIONS.FLOOR` and `PLANE_ROTATIONS.FACING_CAMERA` for rotation values. The diorama spec says `[0, 0, 0]` and "FACING_CAMERA" but doesn't use `PLANE_ROTATIONS.FACING_CAMERA` from OBJ-003 in the code interface. More importantly, the wing rotations (`[0, Math.PI/10, 0]` and `[0, -Math.PI/10, 0]`) are custom values not in OBJ-003's `PLANE_ROTATIONS` constants. This is fine — but the spec should clarify that wing rotations are geometry-specific values, not OBJ-003 constants.

**Fix**: Add a brief note under the slot definitions section (similar to OBJ-018's paragraph about PlaneSlot construction) stating that non-wing slots use `PLANE_ROTATIONS.FACING_CAMERA` (`[0, 0, 0]`) from OBJ-003, while wing rotations are diorama-specific values not present in OBJ-003's constants.

#### Issue 7: OQ-D is redundant with D8 (Minor)

OQ-D asks "Should the midground slot be transparent?" but D8 already answered this question (albeit in a confusing way). If D8 is rewritten per Issue 1, OQ-D should be removed.

**Fix**: Remove OQ-D, since the decision has been made in D8.

---

### Summary of Issues

| # | Severity | Issue |
|---|----------|-------|
| 1 | Minor | D8 self-contradicts with revision narrative |
| 2 | **Critical** | Slot summary table shows midground `transparent: no`, contradicting AC-17 |
| 3 | Minor | Fog-free zone phrasing for subject is slightly ambiguous |
| 4 | Major | Wing edge-reveal analysis only covers vertical dimension, needs horizontal note |
| 5 | Minor | `dramatic_push` forward reference missing OBJ number |
| 6 | Minor | No explicit note about wing rotations being geometry-specific (not from OBJ-003) |
| 7 | Minor | OQ-D is redundant with the D8 decision |

**One critical, one major, five minor.** The critical issue (#2) is a typo-level fix but it's the kind of contradiction that would confuse an implementer. The major issue (#4) needs a brief analysis addition. The minors are polish.

Please address issues 1-7 and present the revised spec. I'll verify the fixes before converging.

---

## Round 3 — spec_author

Thank you for the thorough review. All seven issues are valid. Here's the revised spec with each fix applied:

---

# Specification: Diorama Scene Geometry (OBJ-022)

## Summary

OBJ-022 defines the **diorama** scene geometry — a semicircle of upright planes arranged at varying Z-depths, like layers of a Victorian paper theater. The defining visual characteristic is that wing planes on the left and right sides are **slightly rotated inward**, creating a curved spatial envelope. As the camera pushes in gently, these angled wings exhibit real perspective foreshortening — their far edges visibly recede while their near edges stay closer — producing a richer depth illusion than flat parallel layers. This is the closest geometry to traditional parallax but distinguished by the perspective distortion on the outer planes. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/diorama.ts

import type { SceneGeometry } from './types';

/**
 * The diorama scene geometry — a semicircle of planes at varying
 * Z-depths, like layers of a Victorian paper theater.
 *
 * Spatial arrangement: a large backdrop at deep Z, wing planes
 * on left and right at mid-depth rotated slightly inward (~18°),
 * a subject plane at shallow Z, and optional midground and
 * foreground planes. The wing rotation produces real perspective
 * foreshortening as the camera pushes in — the defining visual
 * distinction from flat layered parallax.
 *
 * This is the most traditional parallax-like geometry but with
 * genuine perspective distortion. Best for layered storytelling,
 * illustrated scenes, and theatrical compositions.
 */
export const dioramaGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'diorama'` | Matches seed Section 4.2 naming |
| `description` | `'A semicircle of planes at varying Z-depths, like a paper theater. Wing planes on left and right are rotated inward, producing real perspective foreshortening as the camera pushes in. The closest to traditional parallax but with genuine 3D depth distortion on the outer planes. Best for layered storytelling, illustrated scenes, and theatrical compositions.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes in gently." Forward push is the natural motion for a diorama — it enhances the perspective foreshortening on wing planes as the camera approaches. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'gentle_float', 'dramatic_push']` | See D4. Excludes geometry-specific cameras (tunnel_push_forward, flyover_glide) and lateral tracks (wing rotation makes lateral motion risky for edge reveals). |
| `fog` | `{ color: '#0d0d1a', near: 15, far: 45 }` | Dark blue-tinged fog for theatrical atmosphere. See D5. |
| `preferred_aspect` | `'landscape'` | The semicircular wing arrangement reads best in a wide frame. In portrait, the wings would be cropped or squeezed. |

### Slot Definitions

The diorama geometry defines **6 slots** — 2 required, 4 optional. The backdrop and subject provide the essential spatial structure; wings, midground, and foreground are compositional enhancements that create the full paper-theater effect.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate camera motion at `speed=1.0` for the default camera (`slow_push_forward`, which has `maxDisplacementZ = 8` per OBJ-027).

Following the convention established by OBJ-018: the diorama geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot. Non-wing slots use `PLANE_ROTATIONS.FACING_CAMERA` (`[0, 0, 0]`) from OBJ-003. Wing rotations (`[0, ±Math.PI/10, 0]`) are diorama-specific values not present in OBJ-003's `PLANE_ROTATIONS` constants — they are the geometry's defining spatial feature.

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -30]` | Deep Z, serves as the "painted background" of the paper theater. Distance from camera: 35 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA` — upright plane facing the camera. |
| `size` | `[75, 45]` | Oversized to prevent edge reveals during camera push. Frustum visible area at distance 35: ~32.6h × 58.0w (16:9). Width 75 ≥ 58.0 (~1.29× oversize), height 45 ≥ 32.6 (~1.38× oversize). Sufficient for `slow_push_forward`'s 8-unit Z displacement. |
| `required` | `true` | Every diorama needs a background — it is the "painted backdrop" of the theater. |
| `description` | `'Painted backdrop — the background scene visible through and behind all other layers.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backdrop is opaque. |
| `fogImmune` | `true` | The backdrop at Z=-30 (distance 35) would be significantly faded by fog (near=15, far=45). Marking it fog-immune ensures it remains vivid — the visual depth cue comes from the wing foreshortening, not from backdrop fading. |

#### Slot: `wing_left`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[-8, 0, -18]` | Left of center (X=-8), mid-depth (Z=-18). Distance from camera on Z-axis: 23 units. |
| `rotation` | `[0, Math.PI / 10, 0]` | Rotated ~18° around the Y-axis (diorama-specific, not an OBJ-003 `PLANE_ROTATIONS` constant), angling the plane to face slightly toward center-right. This inward rotation is the defining spatial feature of the diorama — it creates real perspective foreshortening as the camera pushes forward. |
| `size` | `[18, 28]` | Tall and moderately wide. Height 28 ensures the wing fills the vertical frame at its distance (visible height at distance 23: ~21.5). Width 18 provides the scenic side panel. After rotation, the effective on-screen width narrows due to foreshortening (~18 × cos(π/10) ≈ 17.1), which is the intended visual effect. |
| `required` | `false` | Optional — a diorama can function with just backdrop + subject. However, wings are what distinguish the diorama from a stage, so SKILL.md should strongly recommend including at least one wing pair. |
| `description` | `'Left scenic wing panel — angled inward like a theater wing flat. Undergoes perspective foreshortening as the camera pushes in.'` | |
| `renderOrder` | `1` | Renders above backdrop. |
| `transparent` | `true` | Wing images should have alpha transparency so the backdrop is visible through gaps/cutouts in the wing artwork (foliage edges, architectural elements). |
| `fogImmune` | `false` | Wings at mid-depth benefit from subtle fog to enhance depth separation from the subject. |

#### Slot: `wing_right`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[8, 0, -18]` | Right of center (X=8), mirrors `wing_left`. |
| `rotation` | `[0, -Math.PI / 10, 0]` | Rotated ~18° inward (negative Y rotation = faces slightly toward center-left). Diorama-specific rotation, mirror of `wing_left`. |
| `size` | `[18, 28]` | Matches `wing_left` for symmetry. |
| `required` | `false` | Optional. Typically used as a symmetric pair with `wing_left`. |
| `description` | `'Right scenic wing panel — angled inward like a theater wing flat. Mirrors the left wing.'` | |
| `renderOrder` | `1` | Same as `wing_left` — they don't overlap laterally, so no ordering conflict. |
| `transparent` | `true` | Same rationale as `wing_left`. |
| `fogImmune` | `false` | Same as `wing_left`. |

#### Slot: `midground`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -12]` | Between wings and subject. Distance from camera: 17 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. The midground is a flat layer parallel to the camera, not rotated like the wings. This contrast between rotated wings and flat center layers enhances the paper-theater layering effect. |
| `size` | `[35, 22]` | Frustum visible area at distance 17: ~15.9h × 28.2w. Width 35 ≥ 28.2 (~1.24× oversize), height 22 ≥ 15.9 (~1.38× oversize). |
| `required` | `false` | Optional — adds an intermediate scenic layer between wings and subject. |
| `description` | `'Middle-distance scenic element — an intermediate layer between the wings and subject. Environmental details, secondary scenery. Typically a scenic cutout with transparent background.'` | |
| `renderOrder` | `2` | Renders above wings. |
| `transparent` | `true` | In the diorama's paper-theater aesthetic, midground elements are scenic cutouts (tree lines, building silhouettes, terrain features) with irregular edges where the backdrop should show through gaps. This differs from the stage geometry where `midground` is `transparent: false` because the stage's midground serves as a solid environmental band. |
| `fogImmune` | `false` | Mid-distance fog fading is appropriate. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -0.5, -5]` | Shallow Z, slightly below center to appear grounded. Distance from camera: 10 units. Matches the stage geometry's subject position (OBJ-018) for consistency. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[12, 12]` | Sized to fill roughly 50-65% of frame height. Frustum visible height at distance 10: ~9.33. Height 12 / 9.33 ≈ 1.29× — provides margin. Square default accommodates both portrait and landscape subject images via texture aspect-ratio auto-sizing (OBJ-040). Focal element, not a coverage plane. |
| `required` | `true` | The subject is the focal point of every diorama scene. |
| `description` | `'Primary subject — person, character, object, or focal element. Should have a transparent background.'` | |
| `renderOrder` | `3` | Renders above midground and wings. |
| `transparent` | `true` | Subject images need alpha transparency. |
| `fogImmune` | `false` | Subject at distance 10 is closer than fog.near (15), so fog has zero effect. |

#### Slot: `near_fg`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -1]` | Very close to camera. Distance from camera: 6 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[25, 16]` | Oversized relative to frustum at this distance (visible ~5.6h × 9.9w). Foreground framing extends beyond the frame edges. |
| `required` | `false` | Optional — adds foreground framing that enhances the "looking through layers" paper-theater effect. |
| `description` | `'Foreground framing element — decorative edges, foliage, particles, or a theatrical proscenium arch. Should have a transparent background.'` | |
| `renderOrder` | `4` | Renders on top of everything. |
| `transparent` | `true` | Must have alpha to not occlude the scene behind it. |
| `fogImmune` | `true` | Foreground is close to camera — fog would look physically wrong. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `backdrop` | `[0, 0, -30]` | `[0, 0, 0]` | `[75, 45]` | **yes** | no | **yes** | 0 |
| `wing_left` | `[-8, 0, -18]` | `[0, PI/10, 0]` | `[18, 28]` | no | yes | no | 1 |
| `wing_right` | `[8, 0, -18]` | `[0, -PI/10, 0]` | `[18, 28]` | no | yes | no | 1 |
| `midground` | `[0, 0, -12]` | `[0, 0, 0]` | `[35, 22]` | no | **yes** | no | 2 |
| `subject` | `[0, -0.5, -5]` | `[0, 0, 0]` | `[12, 12]` | **yes** | yes | no | 3 |
| `near_fg` | `[0, 0, -1]` | `[0, 0, 0]` | `[25, 16]` | no | yes | **yes** | 4 |

### Registration Side Effect

```typescript
// src/scenes/geometries/diorama.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(dioramaGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/diorama.ts
export { dioramaGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./diorama` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Six slots — backdrop, wing pair, midground, subject, near_fg

The diorama uses 6 slots with only 2 required (`backdrop`, `subject`). The minimum viable diorama is backdrop + subject — functionally similar to a simplified stage but with different fog and defaults. The full paper-theater effect requires the wing pair and ideally `near_fg` for a proscenium-arch framing effect.

Six slots is at the upper bound of TC-01's 3-5 range. With 4 optional, most compositions use 4-5 filled slots (backdrop + wings + subject, optionally midground and/or near_fg), which is squarely within the range.

**Why wings are optional, not required:** Making wings required would force every diorama manifest to include wing images, which is a higher authoring burden. An LLM might want a simple layered scene without the theatrical wing effect. By making wings optional but documenting them as "strongly recommended," SKILL.md can guide toward the full effect without rejecting simpler compositions.

### D2: Wing rotation angle — π/10 (~18°)

The wings are rotated inward by π/10 radians (~18°) around the Y-axis. This angle was chosen as a balance between visual effect and practical constraints:

- **Too small (< 10°):** The perspective foreshortening is barely noticeable, and the diorama loses its distinguishing characteristic versus a stage.
- **Too large (> 30°):** The wings become nearly perpendicular to the camera, showing mostly their edge. Text or detailed imagery on the wing would be severely distorted. Also, more of the wing's surface faces away from the camera, increasing the chance of visible texture stretching.
- **~18° (π/10):** Produces visible foreshortening — the far edge of each wing visibly recedes as the camera pushes forward — while keeping the wing's imagery legible. The foreshortening factor is cos(18°) ≈ 0.95, meaning the wing loses only ~5% apparent width to rotation, but the perspective *change* during camera motion is the key visual (not the static appearance).

This angle is a starting point for visual tuning (OBJ-063). The Director Agent may recommend adjustments.

### D3: No floor plane — the diorama is a flat-layer composition

Unlike the stage geometry (which has a `floor` slot), the diorama intentionally omits a floor. A paper theater / diorama is a composition of flat upright cutouts at varying depths — there is no ground surface. Adding a floor would conflate the diorama with the stage geometry.

If an author wants a floor-like element, they can use the `midground` slot with a `position_override` to place and rotate it as a floor, or they should choose the `stage` geometry instead. This keeps the diorama's identity clear and distinct.

### D4: Compatible cameras — excludes lateral tracks and geometry-specific presets

The diorama lists five compatible cameras:

- **`static`** (OBJ-026, verified): Universal baseline. A static paper-theater tableau.
- **`slow_push_forward`** (OBJ-027, verified): The defining motion for dioramas — pushing into the layered scene. **Serves as `default_camera`**. The forward push maximally exercises the wing foreshortening effect.
- **`slow_pull_back`** (OBJ-027, verified): Reverse pull-back reveals the full paper-theater composition. Listed in OBJ-027's `compatibleGeometries` for diorama.
- **`gentle_float`** (OBJ-031, verified): Subtle ambient drift. Works universally.
- **`dramatic_push`** (forward reference to OBJ-032, status `open`): A faster forward push for emphasis moments. To be validated by OBJ-063 tuning.

Excluded:
- **`tunnel_push_forward`**: Tuned for enclosed corridor geometries. The diorama has no walls/ceiling/floor.
- **`flyover_glide`**: Requires a ground plane below the camera. The diorama has no ground.
- **`lateral_track_left/right`**: Lateral tracking with rotated wings risks revealing the wing planes' back faces or edges. The wing rotation means the camera would approach one wing and retreat from the other during lateral motion, creating asymmetric and potentially jarring perspective shifts. Excluded for V1; could be added after OBJ-063 tuning validates edge-reveal safety.
- **`crane_up`**: Vertical camera motion in a flat-layer composition has little spatial meaning. Excluded for V1.
- **`dolly_zoom`**: FOV animation needs careful validation with wing rotation. Deferred.

**Forward reference note:** Of the 5 listed presets, `static` (OBJ-026), `slow_push_forward`/`slow_pull_back` (OBJ-027), and `gentle_float` (OBJ-031) are verified. `dramatic_push` (OBJ-032) is a forward reference (status `open`). The `compatible_cameras` list may be revised as OBJ-032 is specified and OBJ-063 validates compatibility.

### D5: Fog settings — theatrical atmosphere

The diorama uses dark blue-tinged fog (`#0d0d1a`) with `near: 15, far: 45`. This creates a theatrical, slightly mysterious atmosphere appropriate for a paper-theater staging.

- `near: 15` leaves the subject (distance ~10) and `near_fg` (distance ~6) fully clear — both are closer to the camera than fog.near, so fog has zero effect on them.
- `midground` (distance ~17) receives very light fog: (17-15)/(45-15) ≈ 7%.
- `far: 45` fades distant elements. The backdrop at distance 35 would be ~67% fogged at these settings — hence `backdrop` is `fogImmune: true`.
- The wings at distance 23 receive light fog: (23-15)/(45-15) ≈ 27%, which subtly separates them from the subject.

The dark blue tint (vs the stage's pure black or the flyover's light blue-gray) gives the diorama a distinctive mood — slightly nocturnal, theatrical. Authors can override via the manifest's fog settings.

### D6: Backdrop is fog-immune

The backdrop at Z=-30 (distance 35) falls squarely within the fog range (near=15 to far=45). Without fog immunity, it would be ~67% fogged, making it nearly invisible. Since the backdrop is the "painted scenery" of the paper theater and should remain vivid, it is marked `fogImmune: true`. The depth cue in a diorama comes from wing foreshortening and inter-layer parallax, not from atmospheric fading of the backdrop.

### D7: Wing positions at X=±8, Z=-18

The wings are positioned at X=±8, placing them near the left and right edges of the visible frame at their Z-distance. At Z=-18 (distance 23 from camera), the frustum half-width is approximately `23 × tan(25°) × (16/9) ≈ 19.1`. The wing center at X=±8 with width 18 (half-width 9) means the wing extends from X=±(8-9)=∓1 to X=±(8+9)=±17. The inner edge at X=∓1 overlaps the center of the frame slightly, while the outer edge at X=±17 is within the frustum half-width of ±19.1.

After the π/10 rotation, the wing's projected footprint on screen shifts slightly. The near edge (closest to center) appears wider; the far edge (toward the frame edge) appears narrower. This is the intended foreshortening effect.

### D8: Midground is transparent — paper-theater cutout aesthetic

The `midground` slot has `transparent: true`. In the diorama's paper-theater aesthetic, midground elements are scenic cutouts — tree lines, building silhouettes, terrain features — with irregular edges where the backdrop should show through gaps. This is a deliberate differentiation from the stage geometry (OBJ-018), where `midground` is `transparent: false` because the stage's midground serves as a solid full-width environmental band. The diorama's midground is a flat scenic piece in a layered diorama, not a continuous background layer.

### D9: `preferred_aspect` is `landscape`

The semicircular wing arrangement is the diorama's defining feature. In landscape (16:9), the wings have room to spread laterally and the inward rotation is visible. In portrait (9:16), the narrow frame width means the wings would either crowd the center or be cropped off the sides, losing the semicircular effect. The geometry renders correctly in portrait (seed C-04), but SKILL.md should guide LLMs toward landscape.

### D10: Subject position matches stage geometry

The subject is at `[0, -0.5, -5]` — identical to the stage geometry (OBJ-018 D4). This consistency means LLMs can expect the subject to appear similarly framed across geometries, making geometry selection less error-prone. The slight Y=-0.5 offset places the subject slightly below center, a standard compositional choice.

### D11: PlaneSlot construction, not DepthSlot — follows OBJ-018 convention

Same as OBJ-018 and OBJ-021: the geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration. OBJ-007's `DepthSlot` fields (`promptGuidance`, `expectsAlpha`) are not part of the `PlaneSlot` type.

**Prompt guidance gap for geometry-specific slots:** The diorama introduces custom slots (`wing_left`, `wing_right`) not present in OBJ-007's `DEFAULT_SLOT_TAXONOMY`. Downstream consumers (OBJ-071 SKILL.md, OBJ-053) must derive prompt guidance from `PlaneSlot.description` fields. This is the same gap noted in OBJ-018 and OBJ-021.

### D12: Explicit optional field policy — follows OBJ-018 convention

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

### D13: Wing renderOrder tie is intentional

Both `wing_left` and `wing_right` share `renderOrder: 1`. Since they are laterally separated (X=-8 vs X=8) and the camera has no lateral track in the compatible cameras list, they occupy different screen regions and never compete for draw order. The Z-buffer handles any theoretical overlap correctly since they're at the same Z-depth.

## Acceptance Criteria

- [ ] **AC-01:** `dioramaGeometry.name` is `'diorama'`.
- [ ] **AC-02:** `dioramaGeometry.slots` contains exactly 6 keys: `backdrop`, `wing_left`, `wing_right`, `midground`, `subject`, `near_fg`.
- [ ] **AC-03:** Required slots are exactly `backdrop`, `subject` (`required: true`). All others are `required: false`.
- [ ] **AC-04:** `dioramaGeometry.default_camera` is `'slow_push_forward'`.
- [ ] **AC-05:** `dioramaGeometry.default_camera` appears in `dioramaGeometry.compatible_cameras`.
- [ ] **AC-06:** `dioramaGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (verified presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `dioramaGeometry.compatible_cameras` includes `'slow_push_forward'` and `'slow_pull_back'` (verified presets from OBJ-027).
- [ ] **AC-08:** `dioramaGeometry.compatible_cameras` includes `'dramatic_push'` (forward reference to OBJ-032).
- [ ] **AC-09:** `dioramaGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, or `'lateral_track_right'`.
- [ ] **AC-10:** `dioramaGeometry.compatible_cameras` contains exactly 5 entries.
- [ ] **AC-11:** `dioramaGeometry.fog` is `{ color: '#0d0d1a', near: 15, far: 45 }`.
- [ ] **AC-12:** `dioramaGeometry.description` is non-empty and describes a paper-theater / semicircle-of-planes arrangement.
- [ ] **AC-13:** `dioramaGeometry.preferred_aspect` is `'landscape'`.
- [ ] **AC-14:** The `wing_left` slot rotation is `[0, Math.PI / 10, 0]` (positive Y rotation, ~18° inward).
- [ ] **AC-15:** The `wing_right` slot rotation is `[0, -Math.PI / 10, 0]` (negative Y rotation, ~18° inward, mirroring `wing_left`).
- [ ] **AC-16:** All non-wing slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-17:** `wing_left`, `wing_right`, `midground`, `subject`, and `near_fg` have `transparent: true`. `backdrop` has `transparent: false`.
- [ ] **AC-18:** `backdrop` and `near_fg` have `fogImmune: true`. All other slots have `fogImmune: false`.
- [ ] **AC-19:** `renderOrder` values are: backdrop(0), wing_left(1), wing_right(1), midground(2), subject(3), near_fg(4). No other values.
- [ ] **AC-20:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-21:** `registerGeometry(dioramaGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-22:** All slot `description` fields are non-empty strings.
- [ ] **AC-23:** All slot `size` components are positive (> 0).
- [ ] **AC-24:** For the `backdrop` slot (coverage plane, distance 35): size [75, 45] >= frustum visible area (~58.0w × 32.6h at FOV=50°, 16:9).
- [ ] **AC-25:** For the `midground` slot (coverage plane, distance 17): size [35, 22] >= frustum visible area (~28.2w × 15.9h).
- [ ] **AC-26:** For the `near_fg` slot (coverage plane, distance 6): size [25, 16] >= frustum visible area (~9.9w × 5.6h).
- [ ] **AC-27:** Wing slots and subject slot are exempt from full-frustum coverage check — wings are scenic side panels (not full-frame coverage), subject is a focal element.
- [ ] **AC-28:** Slot Z-positions decrease (go more negative) as depth increases: `near_fg` (-1) > `subject` (-5) > `midground` (-12) > wings (-18) > `backdrop` (-30).
- [ ] **AC-29:** The module self-registers via `registerGeometry(dioramaGeometry)` as a side effect of import.
- [ ] **AC-30:** The module exports `dioramaGeometry` as a named export.
- [ ] **AC-31:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants.
- [ ] **AC-32:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-33:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-34:** `wing_left.position[0]` is the negation of `wing_right.position[0]` (lateral symmetry: -8 vs 8).
- [ ] **AC-35:** `wing_left.size` equals `wing_right.size`.
- [ ] **AC-36:** `wing_left.rotation[1]` is the negation of `wing_right.rotation[1]` (rotation symmetry: π/10 vs -π/10).

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`backdrop`, `subject`) | Valid scene. Minimal diorama — functionally similar to a very simple stage but with different fog and description. No wing foreshortening. |
| Manifest provides all 6 slots | Valid scene. Full paper-theater effect with maximum depth layering. |
| Manifest provides `wing_left` but not `wing_right` | Valid. Asymmetric composition — only one side has a scenic wing. The scene is lopsided but artistically valid. |
| Manifest provides `wing_right` but not `wing_left` | Valid. Asymmetric composition. |
| Manifest provides wings but no midground | Valid. Common composition — wings and subject with no intermediate layer. |
| Manifest uses `floor` or `ceiling` (not diorama slots) | Rejected by manifest validation (OBJ-017). Error names the invalid key and lists valid diorama slot names. |
| Manifest uses `back_wall` instead of `backdrop` | Rejected — the diorama uses `backdrop`, not the default taxonomy's `back_wall`. |
| Camera pushes forward — vertical edge-reveal check | Wing height 28 at distance 23 (before push) fills ~130% of visible height. After an 8-unit push (camera at Z=-3), distance to wings is 15. Visible height at 15: ~14.0. Wing height 28 / 14.0 = 2.0× oversize — safe. |
| Camera pushes forward — horizontal edge-reveal check for wings | At maximum push (camera Z=-3, wing Z=-18, distance 15): frustum half-width ≈ `15 × tan(25°) × (16/9) ≈ 12.4`. Wing center at X=-8 with half-width ~9 (pre-rotation), outer edge at X=-17. Frustum edge at X=-12.4. Wing extends 4.6 units past the visible area — safe. Full edge-reveal validation for rotated wings under all camera motions is deferred to OBJ-040, which performs formal frustum intersection calculations accounting for rotation. |
| Portrait mode (9:16) | Geometry renders correctly. Narrower width means wings at X=±8 may be partially outside frame. `preferred_aspect: 'landscape'` guides LLMs away. |
| Wing back-face visibility | Wings rotated at π/10 show only their front face. Even at maximum camera push (Z=-3), the camera is still in front of the wings (Z=-18). No risk of seeing the wing from behind. Three.js `side: THREE.FrontSide` (default for meshBasicMaterial) would additionally prevent back-face rendering. |
| Fog completely obscuring the wings | Wings at distance 23 with fog near=15, far=45: fog factor ≈ (23-15)/(45-15) ≈ 0.27 (27% fogged). Visible but subtly faded — intentional for depth separation. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `diorama.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'diorama' is already registered." Module relies on Node.js module caching. |
| `diorama.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'diorama': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `dioramaGeometry.name` is `'diorama'`.
2. `dioramaGeometry.slots` has exactly 6 keys: `backdrop`, `wing_left`, `wing_right`, `midground`, `subject`, `near_fg`.
3. Required slots: `backdrop`, `subject`. Optional: `wing_left`, `wing_right`, `midground`, `near_fg`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'slow_push_forward'` and is in `compatible_cameras`.
6. `compatible_cameras` contains exactly 5 entries, all matching `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` is `'#0d0d1a'`.
8. `description` is non-empty.
9. `preferred_aspect` is `'landscape'`.

**Slot spatial correctness tests:**
10. `wing_left` rotation is `[0, Math.PI / 10, 0]`.
11. `wing_right` rotation is `[0, -Math.PI / 10, 0]`.
12. All non-wing slots have rotation `[0, 0, 0]`.
13. Z-positions ordered: `near_fg` (-1) > `subject` (-5) > `midground` (-12) > wings (-18) > `backdrop` (-30).
14. `renderOrder` values: backdrop(0) < wings(1) < midground(2) < subject(3) < near_fg(4).
15. All `size` components are > 0.

**Slot metadata tests:**
16. `wing_left`, `wing_right`, `midground`, `subject`, `near_fg` have `transparent: true`.
17. `backdrop` has `transparent: false`.
18. `backdrop`, `near_fg` have `fogImmune: true`.
19. `wing_left`, `wing_right`, `midground`, `subject` have `fogImmune: false`.
20. All slot `description` fields are non-empty.
21. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
22. `validateGeometryDefinition(dioramaGeometry)` returns an empty error array.
23. `registerGeometry(dioramaGeometry)` does not throw (when registry is not locked).
24. After registration, `getGeometry('diorama')` returns the diorama geometry.

**Frustum size validation tests:**
25. `backdrop` size [75, 45] >= visible area at Z-distance 35 with FOV=50° and 16:9 (~58.0w × 32.6h).
26. `midground` size [35, 22] >= visible area at Z-distance 17 (~28.2w × 15.9h).
27. `near_fg` size [25, 16] >= visible area at Z-distance 6 (~9.9w × 5.6h).
28. Wing slots: exempt (scenic side panels, not full-frame coverage).
29. `subject` slot: exempt (focal element, not coverage plane).

**Compatible cameras tests:**
30. `compatible_cameras` includes `'static'`, `'slow_push_forward'`, `'slow_pull_back'`, `'gentle_float'`, `'dramatic_push'`.
31. `compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, `'lateral_track_right'`.

**Symmetry tests:**
32. `wing_left.position[0]` is the negation of `wing_right.position[0]`.
33. `wing_left.size` equals `wing_right.size`.
34. `wing_left.renderOrder` equals `wing_right.renderOrder`.
35. `wing_left.rotation[1]` is the negation of `wing_right.rotation[1]`.

### Relevant Testable Claims

- **TC-01** (partial): The diorama uses 6 slots (2 required, 4 optional), within the 3-5 effective range for most compositions.
- **TC-04** (partial): All spatial relationships defined by geometry. LLM specifies `geometry: 'diorama'` and maps images to slot names — no XYZ coordinates.
- **TC-08** (partial): The diorama covers layered/illustrated/theatrical scene types that other geometries (stage, tunnel) do not naturally express.

## Integration Points

### Depends on

| Upstream | What OBJ-022 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types. `registerGeometry` function. |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`). `DEFAULT_SLOT_TAXONOMY` for reference only (diorama shares `midground`, `subject`, `near_fg` concepts). |
| **OBJ-003** (Spatial math) | `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. `PLANE_ROTATIONS.FACING_CAMERA` for non-wing slot rotations. |

### Consumed by

| Downstream | How it uses OBJ-022 |
|------------|---------------------|
| **OBJ-063** (Diorama visual tuning) | Director Agent reviews test renders; may adjust wing angle, positions, sizes, fog. |
| **OBJ-070** (End-to-end render test) | May use diorama as a test geometry. |
| **OBJ-071** (SKILL.md) | Documents diorama slot names, descriptions, usage guidance. Must source prompt guidance from `PlaneSlot.description` fields for geometry-specific slots (`wing_left`, `wing_right`). |
| **OBJ-017** (Manifest validation) | Looks up `getGeometry('diorama')` to validate manifest plane keys. |
| **OBJ-036** (Scene sequencer) | Resolves slot spatial data for diorama scenes. |
| **OBJ-039** (Page-side renderer) | Creates Three.js meshes from slot data — notably, wing slots require rotation to be correctly applied to the mesh. |
| **OBJ-040** (Edge-reveal validation) | Validates camera paths don't reveal plane edges. Wing planes with rotation require non-trivial frustum intersection calculations due to foreshortening. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatible_cameras`. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        diorama.ts        # dioramaGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./diorama
```

## Open Questions

### OQ-A: Is π/10 (~18°) the optimal wing rotation angle?

The angle is a heuristic starting point chosen for visible-but-not-excessive foreshortening. The Director Agent (OBJ-063) should evaluate:
- Whether the foreshortening is noticeable enough to justify the diorama as a distinct geometry from the stage.
- Whether wing imagery (text, detailed illustrations) remains legible at this rotation.
- Whether a slightly larger angle (π/8 = 22.5°) produces a more dramatic effect worth the extra distortion.

**Recommendation:** Start at π/10. Adjust during OBJ-063 tuning based on visual feedback. Document the final tuned value.

### OQ-B: Should wings have different Z-positions for a staggered arrangement?

Currently both wings are at Z=-18. Staggering them (e.g., left at Z=-20, right at Z=-16) would create additional depth variety. However, this breaks the lateral symmetry and makes the paper-theater metaphor less clean.

**Recommendation:** Keep symmetric for V1. Staggered wings can be achieved via `position_override` in the manifest. If the Director Agent recommends staggering during tuning, adjust then.

### OQ-C: Should there be a `proscenium` slot?

A dedicated slot for a theatrical proscenium arch (the decorative frame around a stage opening) could reinforce the paper-theater metaphor. This would be at shallow Z, similar to `near_fg`, but specifically designed for an arch/frame effect.

**Recommendation:** `near_fg` already serves this purpose. The `description` explicitly mentions "a theatrical proscenium arch." Adding a separate slot would increase the slot count without meaningful spatial distinction. Defer.

---

All seven issues from the challenger's review have been addressed:

1. **D8 rewritten** — no more self-contradicting revision narrative; states the final decision directly with rationale.
2. **Slot summary table fixed** — midground now correctly shows `yes` under Transparent.
3. **Fog phrasing clarified** — subject slot notes now say "closer than fog.near (15), so fog has zero effect."
4. **Wing horizontal edge-reveal analysis added** — new row in edge cases table with explicit horizontal frustum math and deferral to OBJ-040 for formal validation.
5. **`dramatic_push` OBJ number added** — D4 now says "(forward reference to OBJ-032, status `open`)" and includes a forward reference note paragraph.
6. **OBJ-003 constant usage clarified** — slot definitions preamble now explicitly states non-wing slots use `PLANE_ROTATIONS.FACING_CAMERA` and wing rotations are diorama-specific values. Individual slot tables reference the constant name.
7. **OQ-D removed** — since D8 now makes a clear decision, the open question is redundant.

Challenger, please verify these fixes and approve if satisfied.

---

## Round 4 — spec_challenger

I'll verify each claimed fix against the revised spec.

**Issue 1 (D8 self-contradiction):** ✅ Fixed. D8 now reads as a clean decision statement: "The `midground` slot has `transparent: true`. In the diorama's paper-theater aesthetic, midground elements are scenic cutouts..." No more "On further reflection" narrative.

**Issue 2 (Slot summary table midground transparency):** ✅ Fixed. The table now shows `**yes**` under Transparent for midground. Consistent with AC-17 and D8.

**Issue 3 (Fog phrasing):** ✅ Fixed. Subject slot notes now say "closer than fog.near (15), so fog has zero effect." D5 also updated consistently.

**Issue 4 (Wing horizontal edge-reveal):** ✅ Fixed. New edge case row "Camera pushes forward — horizontal edge-reveal check for wings" with explicit frustum math and deferral to OBJ-040.

**Issue 5 (dramatic_push OBJ number):** ✅ Fixed. D4 now says "(forward reference to OBJ-032, status `open`)" and includes a forward reference note paragraph matching OBJ-018's convention.

**Issue 6 (OBJ-003 constant usage):** ✅ Fixed. Slot definitions preamble now explicitly notes the distinction. Individual slot tables reference `PLANE_ROTATIONS.FACING_CAMERA`.

**Issue 7 (OQ-D removed):** ✅ Fixed. Only OQ-A, OQ-B, OQ-C remain.

All seven fixes are structurally present and correct. No new issues introduced by the revisions. The spec is complete, internally consistent, and implementable.

CONCLUSION:

The diorama scene geometry spec (OBJ-022) defines a 6-slot paper-theater arrangement with rotated wing planes as its distinguishing spatial feature. Two required slots (backdrop, subject), four optional (wing_left, wing_right, midground, near_fg). Wings rotated ±π/10 inward for perspective foreshortening. Five compatible cameras (static, slow_push_forward, slow_pull_back, gentle_float, dramatic_push). Theatrical dark-blue fog. 36 specific acceptance criteria covering structure, spatial correctness, metadata, frustum sizing, symmetry, and registration. All issues from review resolved.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md",
  "content": "# Specification: Diorama Scene Geometry (OBJ-022)\n\n## Summary\n\nOBJ-022 defines the **diorama** scene geometry \u2014 a semicircle of upright planes arranged at varying Z-depths, like layers of a Victorian paper theater. The defining visual characteristic is that wing planes on the left and right sides are **slightly rotated inward**, creating a curved spatial envelope. As the camera pushes in gently, these angled wings exhibit real perspective foreshortening \u2014 their far edges visibly recede while their near edges stay closer \u2014 producing a richer depth illusion than flat parallel layers. This is the closest geometry to traditional parallax but distinguished by the perspective distortion on the outer planes. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.\n\n## Interface Contract\n\n### Exported Geometry Definition\n\n```typescript\n// src/scenes/geometries/diorama.ts\n\nimport type { SceneGeometry } from './types';\n\n/**\n * The diorama scene geometry \u2014 a semicircle of planes at varying\n * Z-depths, like layers of a Victorian paper theater.\n *\n * Spatial arrangement: a large backdrop at deep Z, wing planes\n * on left and right at mid-depth rotated slightly inward (~18\u00b0),\n * a subject plane at shallow Z, and optional midground and\n * foreground planes. The wing rotation produces real perspective\n * foreshortening as the camera pushes in \u2014 the defining visual\n * distinction from flat layered parallax.\n *\n * This is the most traditional parallax-like geometry but with\n * genuine perspective distortion. Best for layered storytelling,\n * illustrated scenes, and theatrical compositions.\n */\nexport const dioramaGeometry: SceneGeometry;\n```\n\n### Geometry Fields\n\n| Field | Value | Rationale |\n|-------|-------|-----------|\n| `name` | `'diorama'` | Matches see
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-022",
     3→  "description": "Diorama scene geometry -- semicircle of planes arranged at varying Z-depths, like layers of a paper theater. Camera pushes in gently. Closest to traditional parallax but with real perspective foreshortening on the outer planes. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 geometry. Medium priority."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/meta.json",
  "content": "{\n  \"id\": \"OBJ-022\",\n  \"description\": \"Diorama scene geometry -- semicircle of planes arranged at varying Z-depths, like layers of a paper theater. Camera pushes in gently. Closest to traditional parallax but with real perspective foreshortening on the outer planes. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T00:00:00Z\",\n  \"depends_on\": [\"OBJ-005\", \"OBJ-007\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 geometry. Medium priority. 6 slots (2 required: backdrop, subject; 4 optional: wing_left, wing_right, midground, near_fg). Wings rotated +-PI/10 inward. 5 compatible cameras. Theatrical dark-blue fog.\",\n  \"status\": \"specified\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/meta.json has been updated successfully.
Now commit to git:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-022/output.md nodes/OBJ-022/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-022): Define diorama scene geometry specification\n\n6-slot paper-theater arrangement with rotated wing planes as the\ndistinguishing spatial feature. 2 required (backdrop, subject),\n4 optional (wing_left, wing_right, midground, near_fg). Wings\nrotated +-PI/10 inward for perspective foreshortening. 5 compatible\ncameras. Theatrical dark-blue fog. 36 acceptance criteria.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-022 spec files"
}
[Tool Result] [master 253f897] spec(OBJ-022): Define diorama scene geometry specification
 2 files changed, 436 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-022/output.md
The specification for OBJ-022 (Diorama Scene Geometry) has been written to disk and committed. The deliberation converged after all 7 issues from round 2 were verified as resolved in the round 3 revision:

1. **D8 self-contradiction** → Rewritten as clean decision
2. **Slot table midground transparency** → Fixed to `yes`
3. **Fog phrasing** → Clarified ("closer than fog.near")
4. **Wing horizontal edge-reveal** → Analysis added with OBJ-040 deferral
5. **dramatic_push OBJ number** → Added "(forward reference to OBJ-032)"
6. **OBJ-003 constant usage** → Explicit note about diorama-specific rotations
7. **Redundant OQ-D** → Removed
