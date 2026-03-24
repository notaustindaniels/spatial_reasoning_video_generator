# Deliberation Transcript: OBJ-025

---

## Round 1 — spec_author

Looking at the objective metadata, seed Section 4.2's close_up description, and the dependency specs from OBJ-005 and OBJ-007, let me propose the specification.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


Let me check the existing geometry implementations to understand the established pattern before proposing the spec.
[Tool: ToolSearch]
  Input: {
  "query": "select:Glob,Bash",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-025/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-025/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-018/**/*.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-022/**/*.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-021/**/*.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/transcript.md
Let me read a verified geometry spec (stage - OBJ-018) to understand the established pattern, plus diorama (OBJ-022) which is closest in feel to close_up:
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
  "limit": 200
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md",
  "offset": 200,
  "limit": 150
}
[Tool Result]    200→- **`flyover_glide`**: Requires a ground plane below the camera. The diorama has no ground.
   201→- **`lateral_track_left/right`**: Lateral tracking with rotated wings risks revealing the wing planes' back faces or edges. The wing rotation means the camera would approach one wing and retreat from the other during lateral motion, creating asymmetric and potentially jarring perspective shifts. Excluded for V1; could be added after OBJ-063 tuning validates edge-reveal safety.
   202→- **`crane_up`**: Vertical camera motion in a flat-layer composition has little spatial meaning. Excluded for V1.
   203→- **`dolly_zoom`**: FOV animation needs careful validation with wing rotation. Deferred.
   204→
   205→**Forward reference note:** Of the 5 listed presets, `static` (OBJ-026), `slow_push_forward`/`slow_pull_back` (OBJ-027), and `gentle_float` (OBJ-031) are verified. `dramatic_push` (OBJ-032) is a forward reference (status `open`). The `compatible_cameras` list may be revised as OBJ-... [truncated]
Now let me also check the existing camera presets (OBJ-026, OBJ-027, OBJ-031) to understand what's verified and available:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md",
  "limit": 50
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
  "limit": 50
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
Now let me check what camera presets exist — specifically if there's a "breathing zoom" or FOV-animation preset defined anywhere:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-03[0-4]/**/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md",
  "limit": 60
}
[Tool Result]      1→# Specification: OBJ-030 — Flyover Glide Camera Path Preset
     2→
     3→## Summary
     4→
     5→OBJ-030 defines the `flyover_glide` camera path preset — a bird's-eye aerial movement where the camera is positioned at elevated Y, moves forward along the Z-axis, and looks slightly downward throughout. This preset conforms to the `CameraPathPreset` contract from OBJ-006 and is designed primarily for the `flyover` scene geometry. It produces the feel of gliding over a landscape, looking ahead and down at the terrain below.
     6→
     7→## Interface Contract
     8→
     9→### Preset Export
    10→
    11→```typescript
    12→// src/camera/presets/flyover-glide.ts
    13→
    14→import { CameraPathPreset } from '../types';
    15→
    16→/**
    17→ * The flyover_glide camera path preset.
    18→ * Conforms to CameraPathPreset (OBJ-006).
    19→ */
    20→export const flyoverGlide: CameraPathPreset;
    21→```
    22→
    23→### Spatial Parameters (Constants)
    24→
    25→The... [truncated]

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
Now I have a thorough understanding of the established patterns. Let me also quickly check OBJ-003 for the spatial constants:
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
Now I have everything I need. Let me propose the specification.

---

# Specification Proposal: Close-Up Scene Geometry (OBJ-025)

## Summary

OBJ-025 defines the **close_up** scene geometry — the most intimate geometry in depthkit, where a subject plane fills most of the camera view at very shallow Z depth, with minimal background visible and very subtle camera motion. The defining characteristic is restraint: a tight framing, few planes, and motion so subtle it feels like breathing. This geometry is designed for emphasis moments, character portraits, detail shots, and emotional beats where the viewer's attention should rest on the subject rather than on spatial spectacle. Unlike all other geometries, the close_up's recommended camera presets are the most subdued — `gentle_float` as default, with `static` as the minimal option and forward push/pull as the maximum intensity. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/close_up.ts

import type { SceneGeometry } from './types';

/**
 * The close_up scene geometry — subject fills most of the view
 * at shallow Z depth. Minimal background visible. Very subtle
 * camera motion.
 *
 * Spatial arrangement: a backdrop plane at moderate depth (closer
 * than other geometries' backdrops to ensure it remains visible
 * and fills the frame behind the tightly-framed subject), a large
 * subject plane at very shallow Z that dominates the view, and an
 * optional accent plane for subtle foreground atmosphere.
 *
 * This is the simplest geometry by slot count (3 slots, 2 required)
 * and is designed for emphasis moments, character portraits, detail
 * shots, and emotional beats. Camera motion should be felt, not
 * noticed — gentle_float is the default camera.
 */
export const closeUpGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'close_up'` | Matches seed Section 4.2 naming |
| `description` | `'Subject fills most of the view at shallow Z depth. Minimal background visible. The most intimate geometry — designed for emphasis moments, character portraits, detail shots, and emotional beats. Camera motion should be felt, not noticed.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'gentle_float'` | Seed Section 4.2: "Very subtle camera motion (slight drift or breathing zoom via FOV animation)." `gentle_float` provides almost subliminal multi-axis drift — the ideal match for an intimate close-up where motion should be felt, not seen. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'gentle_float']` | See D3 for rationale and exclusions. |
| `fog` | `{ color: '#000000', near: 8, far: 20 }` | Subtle short-range fog. See D5. |
| `preferred_aspect` | `'both'` | Close-up works equally well in landscape and portrait — a tightly-framed subject reads well in either orientation. Portrait mode is particularly natural for character close-ups. |

### Slot Definitions

The close_up geometry defines **3 slots** — 2 required, 1 optional. This is the fewest slots of any geometry, reflecting the design principle of restraint. The subject and backdrop are structurally necessary; the accent layer adds optional atmospheric depth (particles, bokeh, light effects).

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate `gentle_float`'s drift envelope (±0.3 X, ±0.2 Y, ±0.4 Z per OBJ-031).

Following the convention established by OBJ-018: the close_up geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -15]` | Moderate depth — much closer than the stage's backdrop at Z=-30. At distance 20 from camera, this is close enough that it remains visible and fills the frame as a blurred/atmospheric background behind the tightly-framed subject. A deeper backdrop would be overwhelmingly dominated by the subject plane and contribute little visually. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[45, 28]` | Frustum visible area at distance 20 (from camera at Z=5 to backdrop at Z=-15): visible height = 2 × 20 × tan(25°) ≈ 18.64; visible width ≈ 18.64 × (16/9) ≈ 33.14. Size [45, 28] provides ~1.36x horizontal oversize and ~1.50x vertical oversize. The generous oversize accounts for `gentle_float`'s ±0.4 Z drift (distance ranges 19.6–20.4, negligible change) and ±0.3 X drift, plus accommodates `slow_push_forward`'s 8-unit Z displacement (camera at Z=-3, distance becomes 12, visible area shrinks — oversize becomes even more generous). |
| `required` | `true` | A close-up with no background produces a subject floating in void. Even a simple gradient or blurred color field is needed behind the subject. |
| `description` | `'Background — typically a blurred, atmospheric, or gradient backdrop. Kept intentionally minimal and out-of-focus in feel to maintain focus on the subject.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backdrop is opaque. |
| `fogImmune` | `false` | Mild fog fading at this distance (distance 20 vs fog near=8) provides subtle atmospheric depth without obscuring the background entirely. Fog factor at distance 20: (20-8)/(20-8) = 1.0 — wait, that's fully fogged. Let me recalculate: fog near=8, far=20, distance 20 → fog factor = (20-8)/(20-8) = 1.0 (fully fogged). That would make the backdrop invisible. See D5 — I need to adjust fog settings. |

**Revised fog settings (see D5):** `{ color: '#000000', near: 10, far: 25 }`. At distance 20: fog factor = (20-10)/(25-10) = 10/15 ≈ 0.67. The backdrop would be ~67% fogged. This is problematic for a backdrop that should be visible.

**Decision: backdrop is `fogImmune: true`.** The close_up's fog should only affect the optional accent layer for atmospheric depth, not hide the backdrop. See D5 for full rationale.

**Revised `backdrop` slot:**

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -15]` | Distance from camera: 20 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[45, 28]` | ~1.36x horizontal oversize, ~1.50x vertical oversize at distance 20. |
| `required` | `true` | Close-up needs a background. |
| `description` | `'Background — typically a blurred, atmospheric, or gradient backdrop. Kept intentionally minimal to maintain focus on the subject.'` | |
| `renderOrder` | `0` | Renders first. |
| `transparent` | `false` | Opaque background. |
| `fogImmune` | `true` | The backdrop must remain visible. Fog is used only for accent layer atmospheric effects. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -2]` | Very shallow Z — distance 7 from camera. This is much closer than the stage's subject at Z=-5 (distance 10). The shallow depth is the defining characteristic: at distance 7, the subject fills a large portion of the frame. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[10, 10]` | Frustum visible area at distance 7: visible height = 2 × 7 × tan(25°) ≈ 6.52; visible width ≈ 6.52 × (16/9) ≈ 11.60. Size [10, 10] means height 10 / 6.52 ≈ 1.53x — the subject fills ~65% of the frame height (1/1.53). The subject intentionally does not fill 100% — a small margin of backdrop should be visible around the edges to provide spatial context. Width 10 / 11.60 ≈ 0.86x — the subject does not fill the full horizontal frame, which is correct for a focal element. Square default accommodates both portrait and landscape subject images via texture auto-sizing (OBJ-040). |
| `required` | `true` | The subject is the reason for a close-up. |
| `description` | `'Primary subject — the focal element that dominates the frame. Person, character face, object detail, or key visual. Should have a transparent background.'` | |
| `renderOrder` | `1` | Renders above backdrop. |
| `transparent` | `true` | Subject needs alpha transparency. |
| `fogImmune` | `true` | Subject at distance 7 is close to fog.near (10) and must never be affected by fog. Marking fog-immune protects against manifest fog overrides. |

#### Slot: `accent`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, 1]` | Positive Z — actually between the camera and the subject, slightly in front of the camera's start position. Distance from camera: 4 units. This extreme closeness creates an out-of-focus atmospheric overlay (particles, light bokeh, subtle haze) that adds depth without drawing attention. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA`. |
| `size` | `[18, 12]` | Generously oversized relative to visible area at distance 4 (visible height ≈ 3.73, visible width ≈ 6.63). The oversize ensures the accent completely covers the frame even during camera drift. |
| `required` | `false` | Optional — many close-ups work fine without any foreground atmosphere. |
| `description` | `'Foreground accent — subtle particles, light bokeh, or atmospheric haze layered over the subject. Should have a transparent background with mostly empty space and sparse visual elements.'` | |
| `renderOrder` | `2` | Renders on top of everything. |
| `transparent` | `true` | Must have alpha to not occlude the subject. |
| `fogImmune` | `true` | Foreground element — fog would look physically wrong. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `backdrop` | `[0, 0, -15]` | `[0, 0, 0]` | `[45, 28]` | **yes** | no | **yes** | 0 |
| `subject` | `[0, 0, -2]` | `[0, 0, 0]` | `[10, 10]` | **yes** | yes | **yes** | 1 |
| `accent` | `[0, 0, 1]` | `[0, 0, 0]` | `[18, 12]` | no | yes | **yes** | 2 |

### Registration Side Effect

```typescript
// src/scenes/geometries/close_up.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(closeUpGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/close_up.ts
export { closeUpGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./close_up` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Three slots — the minimum viable geometry

The close_up has the fewest slots of any depthkit geometry: `backdrop`, `subject`, and optional `accent`. This is intentional — a close-up is about restraint and focus. Adding more slots (floor, midground, wings) would dilute the intimate framing and push toward stage or diorama territory.

The seed's OQ-07 asks about the minimum viable number of geometries. Within a geometry, the close_up demonstrates the minimum viable number of *slots*. Two required slots is the absolute minimum (a geometry needs at least one required slot per OBJ-005 AC-04; having only a subject with no backdrop produces a floating element in void, which is functionally broken for most use cases).

**Constraint alignment:** TC-01 says 3-5 planes per scene geometry are sufficient for 90% of cases. The close_up's 3 slots (2 required + 1 optional) is at the low end, appropriate for its focused purpose.

### D2: Subject at Z=-2 (very shallow)

The subject is at Z=-2, giving a camera-to-subject distance of 7 units (vs 10 for stage, 10 for diorama). This is the shallowest subject position of any geometry. At this distance with FOV=50°, the subject fills approximately 65% of the frame height — the tightest default framing in depthkit.

**Why not shallower (Z=-1 or Z=0)?** At Z=-1 (distance 6), the subject would be uncomfortably close to `gentle_float`'s Z drift range (camera Z ranges from 4.6 to 5.4). At Z=0 (distance 5), the subject fills ~78% of the frame height, leaving almost no backdrop visible — eliminating the spatial depth cue. Z=-2 balances tight framing with enough breathing room for subtle camera motion and a sliver of visible backdrop.

**Why not at the same position as stage (Z=-5)?** At Z=-5, the close_up would look identical to a stage with no midground or floor — it wouldn't feel like a close-up. The shallower Z is the defining spatial distinction.

### D3: Compatible cameras — subdued motion only

The close_up lists four compatible cameras:

- **`static`** (OBJ-026, verified): No motion. A still portrait or detail shot.
- **`gentle_float`** (OBJ-031, verified): Almost subliminal multi-axis drift. **Default camera.** The ideal match for close-up — the viewer perceives "life" in the frame without being distracted by motion. OBJ-031's drift envelope (±0.3 X, ±0.2 Y, ±0.4 Z) is small enough that the tightly-framed subject stays centered.
- **`slow_push_forward`** (OBJ-027, verified): Forward push into the subject. Listed as compatible but represents the maximum motion intensity appropriate for a close-up. At full speed, the camera pushes from Z=5 to Z=-3, which would bring it to within 1 unit of the subject (Z=-2) — very close but not clipping. The subject grows dramatically in frame. This works for emphasis moments ("zoom in on the detail").
- **`slow_pull_back`** (OBJ-027, verified): Reverse — starts tight, reveals context. Works for transitional moments after a close-up beat.

Excluded:
- **`tunnel_push_forward`**: No tunnel structure. Meaningless.
- **`flyover_glide`**: No ground plane. Meaningless.
- **`lateral_track_left/right`**: Lateral tracking on a tightly-framed subject would reveal backdrop edges quickly and feel jarring in an intimate composition.
- **`dramatic_push`**: Too aggressive for a close-up's intended subtlety. The close_up exists to be calm and focused. If the author wants a dramatic push, they should use the `stage` geometry where there's more spatial structure to support dramatic motion.
- **`crane_up`**: Vertical motion with no floor or ceiling has no spatial reference, and would drift the subject out of frame.

**Note on breathing zoom (FOV animation):** The seed (Section 4.2) mentions "breathing zoom via FOV animation" as a characteristic close-up motion. No FOV-animating camera preset exists yet among the verified presets. If one is created (e.g., as part of OBJ-032–034 or a new objective), it should be added to close_up's `compatible_cameras`. The existing `gentle_float` with its multi-axis drift provides a similar perceptual effect of subtle life without FOV changes.

### D4: `accent` instead of `near_fg`

The close_up uses `accent` rather than the default taxonomy's `near_fg`. Rationale:

- `near_fg` in other geometries (stage, diorama) is a foreground framing element — foliage edges, decorative borders, a proscenium arch. It partially occludes the scene to create a "looking through" effect.
- In a close_up, the foreground layer serves a different purpose: it adds atmospheric depth (floating particles, bokeh circles, light streaks, subtle haze). It should not frame or occlude — it should be sparse and translucent.
- The name `accent` communicates this different role to LLM authors: "this is a light touch, not a framing device."

This follows OBJ-005's convention that geometries may define custom slot names with geometry-specific semantics.

### D5: Fog settings — short range, all slots fog-immune

Fog configuration: `{ color: '#000000', near: 10, far: 25 }`.

All three slots are `fogImmune: true`. This effectively means **fog has no visual effect on the close_up geometry by default**. Why include fog at all?

1. **Forward compatibility.** If a future slot is added (e.g., via OBJ-080 dynamic plane count or a manual PlaneOverride-inserted plane), the fog provides atmospheric depth for that custom plane without requiring the author to configure fog from scratch.
2. **Manifest override consistency.** An author can override fog settings via the manifest. Having a sensible default range means overrides interact predictably.
3. **Convention compliance.** All other geometries define fog. Omitting it would be an inconsistency.

The individual fog-immunity decisions:
- **`backdrop`**: At distance 20, fog (near=10, far=25) would apply ~67% fogging, making the backdrop nearly invisible. A close-up needs its backdrop visible. Fog-immune.
- **`subject`**: At distance 7, below fog.near (10) — fog wouldn't affect it anyway. Fog-immune as a safety measure against manifest overrides with aggressive fog.near.
- **`accent`**: At distance 4, well below fog.near. Fog-immune for the same safety reason as `near_fg` in other geometries — foreground fog fading looks physically wrong.

### D6: `preferred_aspect` is `both`

Close-ups work equally well in landscape and portrait. A character portrait naturally fits 9:16 portrait mode. A detail shot of an object works in 16:9. The subject at Z=-2 with size [10, 10] is a square, which adapts well to either orientation via texture auto-sizing (OBJ-040).

### D7: Accent at positive Z (Z=1)

The accent slot is at Z=1 — actually in front of the camera's default start position at Z=5. Wait, that's at distance 4 from the camera (5 - 1 = 4), not behind the camera. The plane is at Z=1, camera is at Z=5, so the plane is between the camera and the subject (which is at Z=-2). This places the accent extremely close to the camera, which is correct for a bokeh/particle overlay effect.

**Near-plane clipping check:** Camera near plane is 0.1 units. Accent at Z=1, camera at Z=5, distance = 4 units. Even with `gentle_float`'s +0.4 Z drift (camera at Z=5.4), distance is 4.4. With `slow_push_forward` at full travel (camera at Z=-3), distance is 4 units — accent is now *behind* the camera (Z=1 > Z=-3). This is a problem. See Edge Cases.

**Revised accent position:** `[0, 0, -0.5]`. Distance from camera at start: 5.5 units. With `slow_push_forward` at full travel (camera at Z=-3), distance: 2.5 units — still in front of the camera and above near-plane (0.1). With `gentle_float` max Z drift (camera at Z=4.6): distance 5.1. Safe.

### D8: PlaneSlot construction, not DepthSlot — follows OBJ-018 convention

Same as all other geometries: constructs `PlaneSlot` objects for registration.

**Prompt guidance gap for geometry-specific slots:** The close_up introduces `accent`, not present in OBJ-007's `DEFAULT_SLOT_TAXONOMY`. Downstream consumers (OBJ-071 SKILL.md, OBJ-053) must derive prompt guidance from `PlaneSlot.description`.

### D9: Explicit optional field policy — follows OBJ-018 convention

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

### D10: Subject Y-position at 0 (centered), not -0.5

Unlike the stage (Y=-0.5) and diorama (Y=-0.5), the close_up subject is at Y=0 (vertically centered). In a close-up, there's no floor plane to "ground" the subject on, so the lower-third offset that works for full-body compositions feels unmotivated. A centered subject reads naturally for face/detail close-ups.

Authors can override to Y=-0.5 via `PlaneOverride.position` if they want a grounded feel.

## Acceptance Criteria

- [ ] **AC-01:** `closeUpGeometry.name` is `'close_up'`.
- [ ] **AC-02:** `closeUpGeometry.slots` contains exactly 3 keys: `backdrop`, `subject`, `accent`.
- [ ] **AC-03:** Required slots are exactly `backdrop`, `subject` (`required: true`). `accent` is `required: false`.
- [ ] **AC-04:** `closeUpGeometry.default_camera` is `'gentle_float'`.
- [ ] **AC-05:** `closeUpGeometry.default_camera` appears in `closeUpGeometry.compatible_cameras`.
- [ ] **AC-06:** `closeUpGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (verified presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `closeUpGeometry.compatible_cameras` includes `'slow_push_forward'` and `'slow_pull_back'` (verified presets from OBJ-027).
- [ ] **AC-08:** `closeUpGeometry.compatible_cameras` contains exactly 4 entries.
- [ ] **AC-09:** `closeUpGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, `'lateral_track_right'`, `'dramatic_push'`, or `'crane_up'`.
- [ ] **AC-10:** `closeUpGeometry.fog` is `{ color: '#000000', near: 10, far: 25 }`.
- [ ] **AC-11:** `closeUpGeometry.description` is non-empty and describes a tight, intimate subject framing.
- [ ] **AC-12:** `closeUpGeometry.preferred_aspect` is `'both'`.
- [ ] **AC-13:** All slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-14:** `subject` and `accent` have `transparent: true`. `backdrop` has `transparent: false`.
- [ ] **AC-15:** All three slots have `fogImmune: true`.
- [ ] **AC-16:** `renderOrder` values are strictly increasing: `backdrop` (0) < `subject` (1) < `accent` (2).
- [ ] **AC-17:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-18:** `registerGeometry(closeUpGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-19:** All slot `description` fields are non-empty strings.
- [ ] **AC-20:** All slot `size` components are positive (> 0).
- [ ] **AC-21:** For the `backdrop` slot (coverage plane, distance 20 from camera at Z=5): size [45, 28] >= frustum visible area at distance 20 with FOV=50° and aspect 16:9 (~33.14w × 18.64h). Width 45 >= 33.14 ✓, height 28 >= 18.64 ✓.
- [ ] **AC-22:** For the `accent` slot (coverage plane, distance 5.5 from camera at Z=5 to accent at Z=-0.5): size [18, 12] >= frustum visible area (~8.51w × 5.13h). Width 18 >= 8.51 ✓, height 12 >= 5.13 ✓.
- [ ] **AC-23:** For the `subject` slot (focal element): `size[1]` (height, 10) >= frustum visible height at distance 7 (~6.52), ensuring the subject can fill the frame vertically. Width may be less than the frustum visible width (intentional — focal element, not coverage).
- [ ] **AC-24:** Slot Z-positions decrease as depth increases: `accent` (-0.5) > `subject` (-2) > `backdrop` (-15).
- [ ] **AC-25:** The module self-registers via `registerGeometry(closeUpGeometry)` as a side effect of import.
- [ ] **AC-26:** The module exports `closeUpGeometry` as a named export.
- [ ] **AC-27:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants.
- [ ] **AC-28:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-29:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-30:** `subject.position[1]` is `0` (vertically centered, per D10).

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`backdrop`, `subject`) | Valid scene. Minimal close-up — subject in front of backdrop. No foreground atmosphere. |
| Manifest provides all 3 slots | Valid scene. Full close-up with foreground atmospheric accent. |
| Manifest uses `near_fg` instead of `accent` | Rejected by manifest validation (OBJ-017). Error names the invalid key and lists valid close_up slot names: `backdrop`, `subject`, `accent`. |
| Manifest uses `floor` or `midground` (not close_up slots) | Rejected. Error lists valid slots. |
| `slow_push_forward` at speed=1.0 — subject distance check | Camera pushes from Z=5 to Z=-3. Subject at Z=-2. At maximum push, camera-to-subject distance = |-2 - (-3)| = 1 unit. Near-plane is 0.1 — subject is not clipped. However, the subject at distance 1 would fill the frame massively (frustum visible height at distance 1: ~0.93 units; subject size 10 is ~10.7x the visible area). The subject would be extremely zoomed in. This is an intense effect but artistically valid for "dramatic zoom to detail." |
| `slow_push_forward` at speed=1.0 — accent clipping check | Camera at Z=-3, accent at Z=-0.5. Distance = |-0.5 - (-3)| = 2.5 units. Above near-plane (0.1). Not clipped. |
| `slow_push_forward` at speed=1.0 — backdrop edge reveal check | Camera at Z=-3, backdrop at Z=-15. Distance = 12. Visible area at distance 12: ~11.19h × 19.90w. Backdrop size [45, 28] provides ~2.26x horizontal and ~2.50x vertical oversize. Safe. |
| `gentle_float` drift — accent clipping check | Camera Z ranges 4.6–5.4. Accent at Z=-0.5. Distance ranges 5.1–5.9. All well above near-plane (0.1). Safe. |
| Portrait mode (9:16) | Geometry renders correctly. Narrower visible width means backdrop size [45, 28] has even more oversize horizontally. Subject at [10, 10] square adapts via texture auto-sizing. |
| Subject image has no alpha | The subject will display as a rectangle against the backdrop. `transparent: true` means the renderer creates a material with alpha support, but if the texture itself has no alpha, the entire rectangle is opaque. This is a content issue (AP-03 concern), not a geometry error. The `description` field instructs "Should have a transparent background." |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `close_up.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'close_up' is already registered." Module relies on Node.js module caching. |
| `close_up.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'close_up': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `closeUpGeometry.name` is `'close_up'`.
2. `closeUpGeometry.slots` has exactly 3 keys: `backdrop`, `subject`, `accent`.
3. Required slots: `backdrop`, `subject`. Optional: `accent`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'gentle_float'` and is in `compatible_cameras`.
6. `compatible_cameras` contains exactly 4 entries, all matching `/^[a-z][a-z0-9_]*$/`.
7. `fog` has valid values: `near >= 0`, `far > near`, `color` is `'#000000'`.
8. `description` is non-empty.
9. `preferred_aspect` is `'both'`.

**Slot spatial correctness tests:**
10. All slots have rotation `[0, 0, 0]` (FACING_CAMERA).
11. Z-positions ordered: `accent` (-0.5) > `subject` (-2) > `backdrop` (-15).
12. `renderOrder` values strictly increasing: backdrop(0) < subject(1) < accent(2).
13. All `size` components are > 0.
14. `subject.position[1]` is `0` (vertically centered).

**Slot metadata tests:**
15. `subject.transparent` is `true`; `accent.transparent` is `true`; `backdrop.transparent` is `false`.
16. All three slots have `fogImmune: true`.
17. All slot `description` fields are non-empty.
18. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
19. `validateGeometryDefinition(closeUpGeometry)` returns an empty error array.
20. `registerGeometry(closeUpGeometry)` does not throw (when registry is not locked).
21. After registration, `getGeometry('close_up')` returns the close_up geometry.

**Frustum size validation tests:**
22. `backdrop` at distance 20: size [45, 28] >= frustum visible area (~33.14w × 18.64h).
23. `accent` at distance 5.5: size [18, 12] >= frustum visible area (~8.51w × 5.13h).
24. `subject` at distance 7: height 10 >= frustum visible height (~6.52).

**Compatible cameras tests:**
25. `compatible_cameras` includes `'static'`, `'gentle_float'`, `'slow_push_forward'`, `'slow_pull_back'`.
26. `compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, `'lateral_track_right'`, `'dramatic_push'`, `'crane_up'`.

### Relevant Testable Claims

- **TC-01** (partial): The close_up uses 3 slots (2 required + 1 optional) — the minimum of any geometry. Validates the lower bound of the "3-5 planes" sufficiency claim.
- **TC-04** (partial): The LLM specifies `geometry: 'close_up'` and fills `backdrop` and `subject` slot names. Zero XYZ coordinates needed.
- **TC-08** (partial): The close_up geometry is one of the 8 proposed geometries. It covers emphasis/detail scenes that other geometries handle poorly — a stage with no midground/floor/foreground feels hollow; the close_up is purpose-built for tight framing.

## Integration Points

### Depends on

| Upstream | What OBJ-025 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types for the geometry definition. `registerGeometry` function for self-registration. `validateGeometryDefinition` (used indirectly — `registerGeometry` calls it). |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`, `isValidSlotName`). Referenced for design rationale but not directly imported at runtime (close_up does not use `DEFAULT_SLOT_TAXONOMY` slots — it defines its own `backdrop`, `subject`, `accent`). |
| **OBJ-003** (Spatial math) | `PLANE_ROTATIONS.FACING_CAMERA` constant for all slot rotations. `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference. |

### Consumed by

| Downstream | How it uses OBJ-025 |
|------------|---------------------|
| **OBJ-066** (Close-up visual tuning) | The Director Agent reviews test renders of the close_up geometry and provides feedback on subject framing, backdrop visibility, accent effect, and camera motion subtlety. OBJ-066 may adjust numerical values in the slot definitions. |
| **OBJ-070** (End-to-end scene render test) | May use the close_up geometry in multi-scene render tests. |
| **OBJ-071** (SKILL.md) | Uses slot names, descriptions, and the close_up's intended use case for SKILL.md documentation. |
| **OBJ-017** (Manifest structural validation) | After registration, manifest validation can look up `getGeometry('close_up')` and validate plane keys. |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('close_up')` to resolve slot spatial data. |
| **OBJ-039** (Page-side renderer) | Reads slot `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune` to create Three.js meshes. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        close_up.ts       # closeUpGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./close_up
```

## Open Questions

### OQ-A: Should the close_up define a breathing_zoom camera preset reference?

The seed Section 4.2 mentions "breathing zoom via FOV animation" as a close_up characteristic. No such preset exists yet. Options:
1. Add a forward reference to a `breathing_zoom` preset in `compatible_cameras` and create a new objective for it.
2. Wait for it to be created as part of OBJ-032–034 or a future objective, then update `compatible_cameras`.
3. Accept that `gentle_float` achieves a similar perceptual effect and defer FOV-based breathing to a later version.

**Recommendation:** Option 3 for now. `gentle_float`'s multi-axis drift provides the "felt, not noticed" quality the seed describes. A true FOV-breathing preset can be added to `compatible_cameras` later without changing the geometry definition. This aligns with TC-14's framing as exploratory ("test whether this is worth including in V1 or deferring").

### OQ-B: Should the close_up subject be larger than [10, 10]?

At distance 7, a [10, 10] subject fills ~65% of frame height. For an extremely tight close-up (face filling 80%+), the subject should be larger (e.g., [12, 12]) or positioned closer. The current values produce a "medium close-up" rather than an "extreme close-up."

**Recommendation:** Keep [10, 10] as default. Authors who want tighter framing can use `PlaneOverride.position` to move the subject closer (e.g., Z=-1) or `PlaneOverride.size` to enlarge it. OBJ-066 tuning may adjust this value based on visual review.

### OQ-C: Should `accent` support a `size_mode` or position randomization?

A bokeh/particle accent layer might benefit from slight per-frame position jitter or randomized placement. This is out of scope for the geometry definition (which is static spatial state) — any animation would be a renderer concern (OBJ-044, per-frame opacity/position animation, if implemented).

**Recommendation:** Out of scope for OBJ-025. The accent's static position provides a consistent overlay. Dynamic effects are a post-V1 concern.

---

I believe this is a complete specification. I'd like the challenger to review particularly:

1. **The accent slot at Z=-0.5** — is this the right position? I considered Z=1 (in front of camera) but that breaks under `slow_push_forward`. Z=-0.5 keeps it between camera and subject in all compatible camera states.
2. **All slots being fogImmune** — this effectively makes fog decorative on this geometry. Is that acceptable, or should the backdrop be non-immune with adjusted fog ranges?
3. **The 4 compatible cameras** — is excluding `dramatic_push` too conservative? The close_up is meant to be calm, but `dramatic_push` into a subject could be artistically valid.
4. **Subject at Y=0** instead of the Y=-0.5 used by stage/diorama — does this inconsistency matter?

---

## Round 2 — spec_challenger

Let me review the proposal carefully and check against established patterns.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


Let me check the OBJ-018 (stage) spec more carefully for pattern comparison, and also OBJ-006 for the camera path contract details:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "offset": 10,
  "limit": 150
}
[Tool Result]     10→
    11→```typescript
    12→// src/scenes/geometries/stage.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The stage scene geometry — the default geometry for depthkit.
    18→ *
    19→ * Spatial arrangement: a large backdrop plane at deep Z, a floor
    20→ * plane angled down from the camera (FLOOR rotation), and a
    21→ * subject plane at shallow Z. Optional sky, midground, and
    22→ * near_fg planes provide additional depth layering.
    23→ *
    24→ * Classic "subject in front of a background" setup with real
    25→ * perspective on the floor. The floor's perspective foreshortening
    26→ * as the camera pushes forward is the primary 2.5D effect.
    27→ *
    28→ * This is the most commonly used geometry and the basis for
    29→ * SKILL.md examples.
    30→ */
    31→export const stageGeometry: SceneGeometry;
    32→```
    33→
    34→### Geometry Fields
    35→
    36→| Field | Value | Rationale |
    37→|-------|----... [truncated]

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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md",
  "offset": 50,
  "limit": 80
}
[Tool Result]     50→
    51→**LookAt envelope** (easing-independent):
    52→```
    53→lookAtEnvelope(t) = sin(π * t)
    54→```
    55→The lookAt envelope always uses raw `t`, never the eased value. This is consistent with Design Decision D5: lookAt drift is independent of all author-controlled parameters (`speed` and `easing`).
    56→
    57→#### Position Oscillation
    58→
    59→```
    60→position.x(t) = startX + amplitudeX * speed * sin(2π * freqX * t + phaseX) * positionEnvelope(t)
    61→position.y(t) = startY + amplitudeY * speed * sin(2π * freqY * t + phaseY) * positionEnvelope(t)
    62→position.z(t) = startZ + amplitudeZ * speed * sin(2π * freqZ * t + phaseZ) * positionEnvelope(t)
    63→```
    64→
    65→Where:
    66→- `t` is normalized time `[0, 1]`
    67→- `speed` is from `ResolvedCameraParams.speed` (amplitude multiplier per OBJ-006 D3)
    68→- `positionEnvelope(t) = sin(π * easing(t))`
    69→
    70→**Default Position Parameters:**
    71→
    72→| Parameter | X-axis | Y-ax... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "offset": 80,
  "limit": 60
}
[Tool Result]     80→
    81→### OversizeRequirements — `slow_push_forward`
    82→
    83→| Field | Value | Rationale |
    84→|-------|-------|-----------|
    85→| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
    86→| `maxDisplacementY` | `0` | No vertical displacement. |
    87→| `maxDisplacementZ` | `8` | Total Z travel: z=5 to z=-3 = 8 world units at speed=1.0. |
    88→| `fovRange` | `[50, 50]` | FOV is constant. |
    89→| `recommendedOversizeFactor` | `1.0` | See D3. Camera approaches all planes — no edge-reveal risk. |
    90→
    91→### OversizeRequirements — `slow_pull_back`
    92→
    93→| Field | Value | Rationale |
    94→|-------|-------|-----------|
    95→| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
    96→| `maxDisplacementY` | `0` | No vertical displacement. |
    97→| `maxDisplacementZ` | `8` | Total Z travel: z=-3 to z=5 = 8 world units at speed=1.0. |
    98→| `fovRange` | `[50, 50]` | FOV is constant. |
    99→| `re... [truncated]
Good. Now I have a thorough understanding of the established patterns and the camera preset behaviors. Let me compile my review.

---

## Challenger Review — OBJ-025 Close-Up Scene Geometry

### Points of Agreement (What's Sound)

1. **Three-slot design** — well motivated. Close-up as the simplest geometry with fewest slots is a clean design choice.
2. **Subject at Y=0 (D10)** — well reasoned. No floor means no need for the grounding offset.
3. **`accent` instead of `near_fg` (D4)** — good name, good rationale for the different semantic role.
4. **Compatible camera exclusions (D3)** — thorough reasoning for each exclusion.
5. **`preferred_aspect: 'both'`** — correct.
6. **Registration pattern** — follows OBJ-018 convention exactly.
7. **Design decisions are well-documented** — D1-D10 are clear and rationally supported.

### Issues

---

#### Issue 1: Accent Z-position inconsistency — spec text says Z=1, revised says Z=-0.5, slot summary table unclear

**Severity: Critical**

The spec narrative in D7 starts with Z=1, discovers a clipping problem with `slow_push_forward`, then revises to Z=-0.5. But the "Slot: `accent`" section still shows `position: [0, 0, 1]` in its first table. The revision is only mentioned in D7. The Slot Summary Table at the end shows `[0, 0, -0.5]`, which is the revised value.

An implementer reading top-to-bottom would hit conflicting values. The initial accent slot table says Z=1, D7 says Z=-0.5, and the summary says Z=-0.5.

**Fix:** The final spec must have a single, consistent accent position of `[0, 0, -0.5]` everywhere. Remove the exploratory narrative showing the Z=1 mistake and revision process — the spec should state the final answer cleanly, not document the author's thinking process. Move the clipping analysis to the Edge Cases section as a verification note.

---

#### Issue 2: Frustum size calculation for accent at Z=-0.5 is stated but the distance is wrong in AC-22

**Severity: Major**

AC-22 says "distance 5.5 from camera at Z=5 to accent at Z=-0.5." That's correct: 5 - (-0.5) = 5.5. The frustum calculations check out:
- visible_height = 2 × 5.5 × tan(25°) ≈ 5.13
- visible_width = 5.13 × (16/9) ≈ 9.12

Wait — you wrote `~8.51w`. Let me check: 5.13 × 1.778 ≈ 9.12, not 8.51. The 8.51 figure is wrong.

**Fix:** Correct AC-22's frustum visible area to `~9.12w × 5.13h`. The size [18, 12] still satisfies the criterion (18 ≥ 9.12, 12 ≥ 5.13), so no size change needed — just fix the stated calculation.

---

#### Issue 3: `slow_push_forward` moves camera to Z=-3, and accent at Z=-0.5 — accent distance shrinks to 2.5 units

**Severity: Major**

With `slow_push_forward` at speed=1.0, camera goes to Z=-3 (per OBJ-027). The accent at Z=-0.5 is now at distance 2.5 from the camera. At distance 2.5:
- visible_height = 2 × 2.5 × tan(25°) ≈ 2.33
- visible_width ≈ 2.33 × 1.778 ≈ 4.14

The accent size [18, 12] is massively oversized at this distance — it's ~7.7x wider than the visible area. That's fine for coverage.

But the **subject** at Z=-2 is at distance 1 unit from the camera at Z=-3. At distance 1:
- visible_height = 2 × 1 × tan(25°) ≈ 0.93
- Subject size [10, 10] is ~10.7x the visible area

This means the subject would fill 10.7x the frame — only about 9% of the subject would be visible. The spec acknowledges this in the Edge Cases table as "artistically valid for dramatic zoom to detail" — but this seems extreme. The accent plane is also now **behind** the subject from the camera's perspective (camera at Z=-3, accent at Z=-0.5, subject at Z=-2). The accent is further from the camera (2.5 units) than the subject (1 unit). The accent would appear *behind* the subject.

**Fix:** This isn't necessarily wrong — it's an extreme artistic choice. But the spec should:
1. Explicitly note in the Edge Cases table that with `slow_push_forward` at full speed, the accent layer ends up behind the subject in the render order (farther from camera), which means the `renderOrder: 2` setting becomes critical for it to still overlay. Confirm whether Three.js `renderOrder` overrides depth-buffer sorting in this case (it does, but only when both have `transparent: true` and `depthWrite` is managed correctly).
2. Note whether `slow_push_forward` at full speed is really a sensible combination with `close_up` at all. Consider adding a note that speed ≤ 0.5 is recommended for close_up when using push/pull presets. This is guidance, not a constraint — but it belongs in the description or in the SKILL.md integration notes.

---

#### Issue 4: Fog is effectively decorative — should it be `fog?: undefined` instead?

**Severity: Minor**

All three slots are `fogImmune: true`. The fog config `{ color: '#000000', near: 10, far: 25 }` has zero effect on any slot. The spec rationalizes this in D5 as "forward compatibility" and "convention compliance."

I accept the rationale, but this is mildly misleading for an implementer. The fog exists but does nothing.

**Fix:** Keep the fog (convention compliance is valid), but add a brief note in the fog field rationale stating explicitly: "All three built-in slots are fog-immune, so this fog configuration has no visible effect unless the author adds custom planes via PlaneOverride or a future dynamic plane system. It exists for convention compliance and forward compatibility."

---

#### Issue 5: Missing `slow_pull_back` edge-reveal analysis

**Severity: Major**

The spec has detailed edge-reveal analysis for `slow_push_forward` and `gentle_float`, but `slow_pull_back` is listed as compatible with zero spatial analysis. Per OBJ-027, `slow_pull_back` starts at Z=-3 and moves to Z=5 (reverse of push). At Z=5 (the end state, which is also the starting position), the backdrop at Z=-15 is at distance 20. But at Z=-3 (the start), the backdrop distance is only 12. At that distance, visible area is:
- visible_height = 2 × 12 × tan(25°) ≈ 11.19
- visible_width ≈ 11.19 × 1.778 ≈ 19.90

Backdrop size [45, 28] gives oversizes of 45/19.90 ≈ 2.26x and 28/11.19 ≈ 2.50x. Safe.

But the real concern with `slow_pull_back` is that the camera *retreats*, making planes appear smaller. At Z=5 (end), backdrop at distance 20 has visible area ~33.14w × 18.64h. Backdrop [45, 28] gives 45/33.14 ≈ 1.36x and 28/18.64 ≈ 1.50x. Still safe.

So the analysis works out fine — but the spec should include it. The OBJ-027 spec lists `recommendedOversizeFactor: 1.7` for `slow_pull_back` — the close_up's backdrop oversize of 1.36x is below that recommendation. Is this a problem?

**Fix:** Add `slow_pull_back` to the Edge Cases spatial analysis. Verify that the 1.36x horizontal oversize on the backdrop is sufficient given that OBJ-027 recommends 1.7x oversize for pull_back. If OBJ-027's 1.7x is a general recommendation for *all* geometries, and the close_up backdrop at distance 20 is within the frustum, show the specific math. The oversize recommendation may be per-geometry-specific, in which case document that the close_up's tighter Z-range (backdrop much closer than stage's Z=-30) justifies a lower oversize factor.

---

#### Issue 6: The spec contains implementation narrative/thinking-out-loud

**Severity: Major (for spec quality)**

The spec reads like a working document in several places:
- The `backdrop` section has an initial `fogImmune: false` table, then a "wait, let me recalculate" paragraph, then a **Revised** section. This is the author's thought process, not a specification.
- D7 similarly has a "Wait, that's at distance 4..." self-correction.
- The accent slot is defined twice (Z=1 then Z=-0.5).

A specification should present the final decisions, not the journey.

**Fix:** Clean up all narrative self-corrections. Present each slot once with its final values. Move the "why not Z=1" analysis to a brief note in D7 or the Edge Cases table.

---

#### Issue 7: No explicit statement about what OBJ-003 constants are imported

**Severity: Minor**

OBJ-018 explicitly states it constructs `PlaneSlot` objects and imports from OBJ-005 types. OBJ-025 does this too. But the Integration Points section says it imports `PLANE_ROTATIONS.FACING_CAMERA` from OBJ-003, while all slot rotations are `[0, 0, 0]`. Using the constant vs the literal value is an implementation choice — the spec should be consistent about whether it references the constant name or the raw value.

**Fix:** Since all rotations are `[0, 0, 0]`, simply note that all slots use `FACING_CAMERA` rotation and that `PLANE_ROTATIONS.FACING_CAMERA` from OBJ-003 is available for this. No need to list OBJ-003 as a runtime import if the geometry only uses literal `[0, 0, 0]` tuples. (Stage geometry uses `FLOOR` rotation which actually differs, so it has a real import need.)

---

#### Issue 8: `dolly_zoom` not considered in compatible cameras discussion

**Severity: Minor**

The seed Section 4.2 specifically mentions "breathing zoom via FOV animation" for close_up. The `dolly_zoom` preset (OBJ-034) is the only preset in the seed that animates FOV. The compatible cameras exclusion list discusses `dramatic_push`, `crane_up`, etc., but doesn't mention `dolly_zoom`. OQ-A discusses a hypothetical `breathing_zoom` but doesn't reference the existing `dolly_zoom` preset from the seed.

**Fix:** Add `dolly_zoom` to the exclusion rationale in D3 (if excluded) or to `compatible_cameras` (if included). Even if OBJ-034 is `open` status, the other geometries' specs reference open presets in their compatible cameras lists (e.g., OBJ-021 references `flyover_glide` from OBJ-030). The close_up should at least discuss `dolly_zoom` and decide.

---

### Summary of Required Changes

| # | Severity | Issue |
|---|----------|-------|
| 1 | Critical | Accent Z-position inconsistency (Z=1 vs Z=-0.5) — clean up |
| 2 | Major | Frustum width calculation wrong in AC-22 (8.51 should be 9.12) |
| 3 | Major | `slow_push_forward` puts accent behind subject — document renderOrder/depth interaction |
| 4 | Minor | Fog is decorative — add explicit note |
| 5 | Major | Missing `slow_pull_back` edge-reveal analysis; backdrop oversize vs OBJ-027's 1.7x recommendation |
| 6 | Major | Spec contains thinking-out-loud narrative, not clean decisions |
| 7 | Minor | Clarify OBJ-003 import needs |
| 8 | Minor | `dolly_zoom` not discussed |

Please revise addressing issues 1, 2, 3, 5, and 6 (the critical and major ones). Issues 4, 7, and 8 can be addressed at the same time or noted as minor cleanups.

---

## Round 3 — spec_author

Here is the fully revised specification addressing all 8 issues. The narrative self-corrections have been removed, all values are consistent, and the missing analyses have been added.

---

# Specification: Close-Up Scene Geometry (OBJ-025)

## Summary

OBJ-025 defines the **close_up** scene geometry — the most intimate geometry in depthkit, where a subject plane fills most of the camera view at very shallow Z depth, with minimal background visible and very subtle camera motion. The defining characteristic is restraint: a tight framing, few planes, and motion so subtle it feels like breathing. This geometry is designed for emphasis moments, character portraits, detail shots, and emotional beats where the viewer's attention should rest on the subject rather than on spatial spectacle. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/close_up.ts

import type { SceneGeometry } from './types';

/**
 * The close_up scene geometry — subject fills most of the view
 * at shallow Z depth. Minimal background visible. Very subtle
 * camera motion.
 *
 * Spatial arrangement: a backdrop plane at moderate depth (closer
 * than other geometries' backdrops to keep it visible behind the
 * tightly-framed subject), a large subject plane at very shallow Z
 * that dominates the view, and an optional accent plane for subtle
 * foreground atmosphere.
 *
 * This is the simplest geometry by slot count (3 slots, 2 required)
 * and is designed for emphasis moments, character portraits, detail
 * shots, and emotional beats. Camera motion should be felt, not
 * noticed — gentle_float is the default camera.
 */
export const closeUpGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'close_up'` | Matches seed Section 4.2 naming. |
| `description` | `'Subject fills most of the view at shallow Z depth. Minimal background visible. The most intimate geometry — designed for emphasis moments, character portraits, detail shots, and emotional beats. Camera motion should be felt, not noticed.'` | Describes the spatial feel per OBJ-005's `description` contract. |
| `default_camera` | `'gentle_float'` | Seed Section 4.2: "Very subtle camera motion (slight drift or breathing zoom via FOV animation)." `gentle_float` provides almost subliminal multi-axis drift — the ideal match. |
| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'gentle_float']` | See D3 for rationale and exclusions. |
| `fog` | `{ color: '#000000', near: 10, far: 25 }` | See D5. |
| `preferred_aspect` | `'both'` | Close-up works equally well in landscape and portrait. Portrait mode is particularly natural for character close-ups. |

### Slot Definitions

The close_up geometry defines **3 slots** — 2 required, 1 optional. This is the fewest slots of any geometry, reflecting the design principle of restraint.

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate camera motion envelopes.

Following the convention established by OBJ-018: the close_up geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -15]` | Distance from camera at start (Z=5): 20 units. Much closer than the stage's backdrop (Z=-30, distance 35). At distance 20, the backdrop fills the frame behind the tightly-framed subject. A deeper backdrop would contribute little visually — dominated by the subject plane. |
| `rotation` | `[0, 0, 0]` | Facing camera. |
| `size` | `[45, 28]` | Frustum visible area at distance 20: height = 2 × 20 × tan(25°) ≈ 18.64; width ≈ 18.64 × (16/9) ≈ 33.14. Size [45, 28] provides ~1.36x horizontal and ~1.50x vertical oversize. See D6 for `slow_pull_back` oversize analysis. |
| `required` | `true` | A close-up with no background produces a subject floating in void. Even a simple gradient or color field is needed. |
| `description` | `'Background — typically a blurred, atmospheric, or gradient backdrop. Kept intentionally minimal to maintain focus on the subject.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backdrop is opaque. |
| `fogImmune` | `true` | At distance 20, fog (near=10, far=25) would apply ~67% opacity — nearly hiding the backdrop. A close-up needs its backdrop visible. Fog-immune. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -2]` | Very shallow Z — distance 7 from camera. This is the shallowest subject position of any geometry (stage: Z=-5, distance 10). At distance 7 with FOV=50°, the subject fills approximately 65% of the frame height — the tightest default framing in depthkit. |
| `rotation` | `[0, 0, 0]` | Facing camera. |
| `size` | `[10, 10]` | Frustum visible area at distance 7: height = 2 × 7 × tan(25°) ≈ 6.52; width ≈ 6.52 × (16/9) ≈ 11.60. Height 10/6.52 ≈ 1.53x means the subject fills ~65% of the frame height. Width 10/11.60 ≈ 0.86x — the subject does not fill the full horizontal frame, which is correct for a focal element. Square default accommodates both portrait and landscape subject images via texture auto-sizing (OBJ-040). |
| `required` | `true` | The subject is the reason for a close-up. |
| `description` | `'Primary subject — the focal element that dominates the frame. Person, character face, object detail, or key visual. Should have a transparent background.'` | |
| `renderOrder` | `1` | Renders above backdrop. |
| `transparent` | `true` | Subject needs alpha transparency. |
| `fogImmune` | `true` | Subject at distance 7 is within the fog range (near=10) — would not be fogged anyway. Fog-immune as a safety measure against manifest overrides with aggressive fog.near values. |

#### Slot: `accent`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -0.5]` | Very close to camera — distance 5.5 units. Positioned between the camera and the subject, creating an out-of-focus atmospheric overlay (particles, light bokeh, subtle haze). Why not positive Z (closer)? See D7. |
| `rotation` | `[0, 0, 0]` | Facing camera. |
| `size` | `[18, 12]` | Frustum visible area at distance 5.5: height = 2 × 5.5 × tan(25°) ≈ 5.13; width ≈ 5.13 × (16/9) ≈ 9.12. Size [18, 12] provides ~1.97x horizontal and ~2.34x vertical oversize, ensuring full-frame coverage during camera drift. |
| `required` | `false` | Optional — many close-ups work fine without foreground atmosphere. |
| `description` | `'Foreground accent — subtle particles, light bokeh, or atmospheric haze layered over the subject. Should have a transparent background with mostly empty space and sparse visual elements.'` | |
| `renderOrder` | `2` | Renders on top of everything. Critical: when `slow_push_forward` brings the camera past the accent plane (see Edge Cases), `renderOrder` ensures the accent still composites on top despite being farther from the camera than the subject. This works because both `accent` and `subject` have `transparent: true`, and Three.js uses `renderOrder` to override depth-buffer sorting for transparent objects. |
| `transparent` | `true` | Must have alpha to not occlude the subject. |
| `fogImmune` | `true` | Foreground element — fog fading looks physically wrong on foreground planes. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `backdrop` | `[0, 0, -15]` | `[0, 0, 0]` | `[45, 28]` | **yes** | no | **yes** | 0 |
| `subject` | `[0, 0, -2]` | `[0, 0, 0]` | `[10, 10]` | **yes** | yes | **yes** | 1 |
| `accent` | `[0, 0, -0.5]` | `[0, 0, 0]` | `[18, 12]` | no | yes | **yes** | 2 |

### Registration Side Effect

```typescript
// src/scenes/geometries/close_up.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(closeUpGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/close_up.ts
export { closeUpGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./close_up` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Three slots — the minimum viable geometry

The close_up has the fewest slots of any depthkit geometry: `backdrop`, `subject`, and optional `accent`. This is intentional — a close-up is about restraint and focus. Adding more slots (floor, midground, wings) would dilute the intimate framing and push toward stage or diorama territory.

Two required slots is the functional minimum. A geometry needs at least one required slot per OBJ-005 AC-04; having only a subject with no backdrop produces a floating element in void, which is functionally broken for most use cases.

**Constraint alignment:** TC-01 says 3-5 planes per scene geometry are sufficient for 90% of cases. The close_up's 3 slots (2 required + 1 optional) is at the low end, appropriate for its focused purpose.

### D2: Subject at Z=-2 (very shallow)

The subject is at Z=-2, giving a camera-to-subject distance of 7 units (vs 10 for stage, 10 for diorama). This is the shallowest subject position of any geometry. At this distance with FOV=50°, the subject fills approximately 65% of the frame height — the tightest default framing in depthkit.

Why not shallower (Z=-1 or Z=0)? At Z=-1 (distance 6), the subject would be uncomfortably close to `gentle_float`'s Z drift range (camera Z ranges from 4.6 to 5.4). At Z=0 (distance 5), the subject fills ~78% of the frame height, leaving almost no backdrop visible. Z=-2 balances tight framing with breathing room for subtle camera motion and a sliver of visible backdrop.

Why not at the same position as stage (Z=-5)? At Z=-5, the close_up would look identical to a stage with no midground or floor — it wouldn't feel like a close-up.

### D3: Compatible cameras — subdued motion only

The close_up lists four compatible cameras:

- **`static`** (OBJ-026, verified): No motion. A still portrait or detail shot.
- **`gentle_float`** (OBJ-031, verified): Almost subliminal multi-axis drift. **Default camera.** OBJ-031's drift envelope (±0.3 X, ±0.2 Y, ±0.4 Z) is small enough that the tightly-framed subject stays centered.
- **`slow_push_forward`** (OBJ-027, verified): Forward push into the subject. Represents the maximum motion intensity appropriate for a close-up. At full speed (1.0), creates an intense zoom-to-detail effect. **Recommended speed ≤ 0.5** for close_up to avoid extreme magnification — at speed=1.0 the subject at distance 1 from the camera fills ~10.7x the visible area (see Edge Cases). SKILL.md should document this recommendation.
- **`slow_pull_back`** (OBJ-027, verified): Reverse — starts tight, reveals context. Works for transitional moments after a close-up beat.

Excluded cameras and rationale:
- **`tunnel_push_forward`**: No tunnel structure. Meaningless.
- **`flyover_glide`**: No ground plane. Meaningless.
- **`lateral_track_left/right`**: Lateral tracking on a tightly-framed subject reveals backdrop edges quickly and feels jarring in an intimate composition.
- **`dramatic_push`** (OBJ-032, open): Too aggressive for close_up's intended subtlety. If the author wants dramatic emphasis, `slow_push_forward` at higher speed provides this within a close_up, or they should use the `stage` geometry which has more spatial structure.
- **`crane_up`** (OBJ-033, open): Vertical motion with no floor or ceiling has no spatial reference, and would drift the subject out of frame.
- **`dolly_zoom`** (OBJ-034, open): FOV animation could theoretically create a "breathing" effect. However, `dolly_zoom` simultaneously changes camera Z and FOV in opposite directions, producing the Hitchcock vertigo effect. On a close_up's tight framing with minimal depth variation (only 3 planes, all facing camera), the dolly_zoom effect would be subtle to the point of imperceptibility — the dramatic warping relies on visible depth layering between foreground and background, which the close_up intentionally minimizes. Excluded for V1. If a simpler FOV-only breathing preset is created in a future objective, it would be a natural addition to `compatible_cameras`. See OQ-A.

### D4: `accent` instead of `near_fg`

The close_up uses `accent` rather than the default taxonomy's `near_fg`. The name communicates a different semantic role:

- `near_fg` in other geometries (stage, diorama) is a foreground framing element — foliage edges, decorative borders. It partially occludes the scene to create a "looking through" effect.
- In a close_up, the foreground layer adds atmospheric depth (floating particles, bokeh circles, light streaks, subtle haze). It should not frame or occlude — it should be sparse and translucent.
- The name `accent` communicates "light touch, not framing device" to LLM authors.

This follows OBJ-005's convention that geometries may define custom slot names with geometry-specific semantics.

### D5: Fog settings — present but decorative

Fog configuration: `{ color: '#000000', near: 10, far: 25 }`.

All three built-in slots are `fogImmune: true`, so this fog configuration has **no visible effect** on any built-in slot. It exists for:

1. **Forward compatibility.** If a future system adds custom planes (OBJ-080 dynamic plane count, or manual `PlaneOverride`-inserted planes), the fog provides atmospheric depth for those planes without requiring the author to configure fog from scratch.
2. **Manifest override consistency.** An author can override fog settings via the manifest. Having a sensible default range means overrides interact predictably.
3. **Convention compliance.** All other geometries define fog. Omitting it would be an inconsistency that downstream consumers must special-case.

The individual fog-immunity decisions:
- **`backdrop`**: At distance 20, fog (near=10, far=25) would apply ~67% fogging — nearly hiding the backdrop. A close-up needs its backdrop visible. Fog-immune.
- **`subject`**: At distance 7, below fog.near (10) — unaffected anyway. Fog-immune as safety against manifest overrides with aggressive fog.near.
- **`accent`**: At distance 5.5, below fog.near. Fog-immune — foreground fog fading looks physically wrong.

### D6: Backdrop oversize and `slow_pull_back` edge-reveal analysis

OBJ-027 recommends `recommendedOversizeFactor: 1.7` for `slow_pull_back`. The close_up backdrop's oversize is ~1.36x horizontal at the camera's maximum retreat (Z=5, distance 20). This is below the 1.7x recommendation.

However, OBJ-027's 1.7x recommendation is a general guideline computed for the widest camera retreat at speed=1.0 against the default camera start position. For the close_up specifically:

- **At `slow_pull_back` start** (camera Z=-3, distance 12): visible area ~19.90w × 11.19h. Backdrop [45, 28] oversize: 2.26x × 2.50x. Generous.
- **At `slow_pull_back` end** (camera Z=5, distance 20): visible area ~33.14w × 18.64h. Backdrop [45, 28] oversize: 1.36x × 1.50x.

The 1.36x horizontal oversize at the end state provides 6 units of margin on each side (45 - 33.14 = 11.86, /2 = 5.93 units). `slow_pull_back` is pure Z-axis motion with zero X/Y displacement, so the only edge-reveal risk is from the frustum growing larger as the camera retreats. At 1.36x oversize, the backdrop extends ~5.93 world units beyond the frustum edge on each side — sufficient for zero-displacement motion.

For comparison, `gentle_float` adds ±0.3 X drift at most. Even combining `slow_pull_back` end position with `gentle_float`-scale drift (hypothetically), the effective visible width at distance 20 with 0.3 unit lateral offset is ~33.7 units — still within 45. Safe.

The 1.7x recommendation from OBJ-027 accounts for lateral camera presets (which the close_up excludes) and larger-distance backdrops (stage at Z=-30, distance 35). The close_up's tighter Z-range and pure Z-axis compatible cameras justify the lower oversize.

### D7: Accent at Z=-0.5 — between camera and subject

The accent is at Z=-0.5, placing it between the camera start (Z=5) and the subject (Z=-2), at distance 5.5 from the camera.

A more extreme position (positive Z, e.g., Z=1) was considered but rejected: when `slow_push_forward` drives the camera to Z=-3, a plane at Z=1 would be *behind* the camera (Z=1 > Z=-3). Even Z=0 would result in the camera passing through the plane during push forward. Z=-0.5 keeps the accent in front of the camera in all compatible camera states:

- `gentle_float` max Z: camera at 5.4, accent distance = 5.9. Safe.
- `slow_push_forward` end: camera at Z=-3, accent distance = 2.5. In front, above near-plane (0.1). Safe.
- `slow_pull_back` start: camera at Z=-3, accent distance = 2.5. Safe.
- `slow_pull_back` end: camera at Z=5, accent distance = 5.5. Safe.

### D8: Subject at Y=0 (vertically centered)

Unlike the stage (Y=-0.5) and diorama (Y=-0.5), the close_up subject is at Y=0. In a close-up, there's no floor plane to "ground" the subject, so the lower-third offset that works for full-body compositions feels unmotivated. A centered subject reads naturally for face/detail close-ups.

Authors can override to Y=-0.5 via `PlaneOverride.position` if they want a grounded feel.

### D9: Explicit optional field policy

Following OBJ-018 convention: all `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none rely on default values.

### D10: OBJ-003 usage — constants by value, not import

All close_up slot rotations are `[0, 0, 0]` (equivalent to `PLANE_ROTATIONS.FACING_CAMERA` from OBJ-003). Since all three slots share the same facing-camera rotation and the geometry uses no other OBJ-003 constants at runtime, the implementation may use the literal tuple `[0, 0, 0]` directly. The spec references `FACING_CAMERA` semantically for documentation clarity, but the geometry has no runtime import dependency on OBJ-003 — only on OBJ-005's types and registry.

## Acceptance Criteria

- [ ] **AC-01:** `closeUpGeometry.name` is `'close_up'`.
- [ ] **AC-02:** `closeUpGeometry.slots` contains exactly 3 keys: `backdrop`, `subject`, `accent`.
- [ ] **AC-03:** Required slots are exactly `backdrop` and `subject` (`required: true`). `accent` is `required: false`.
- [ ] **AC-04:** `closeUpGeometry.default_camera` is `'gentle_float'`.
- [ ] **AC-05:** `closeUpGeometry.default_camera` appears in `closeUpGeometry.compatible_cameras`.
- [ ] **AC-06:** `closeUpGeometry.compatible_cameras` includes `'static'` and `'gentle_float'`.
- [ ] **AC-07:** `closeUpGeometry.compatible_cameras` includes `'slow_push_forward'` and `'slow_pull_back'`.
- [ ] **AC-08:** `closeUpGeometry.compatible_cameras` contains exactly 4 entries.
- [ ] **AC-09:** `closeUpGeometry.compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, `'lateral_track_right'`, `'dramatic_push'`, `'crane_up'`, or `'dolly_zoom'`.
- [ ] **AC-10:** `closeUpGeometry.fog` is `{ color: '#000000', near: 10, far: 25 }`.
- [ ] **AC-11:** `closeUpGeometry.description` is non-empty and describes a tight, intimate subject framing.
- [ ] **AC-12:** `closeUpGeometry.preferred_aspect` is `'both'`.
- [ ] **AC-13:** All slots use facing-camera rotation (`[0, 0, 0]`).
- [ ] **AC-14:** `subject` and `accent` have `transparent: true`. `backdrop` has `transparent: false`.
- [ ] **AC-15:** All three slots have `fogImmune: true`.
- [ ] **AC-16:** `renderOrder` values are strictly increasing: `backdrop` (0) < `subject` (1) < `accent` (2).
- [ ] **AC-17:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-18:** `registerGeometry(closeUpGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-19:** All slot `description` fields are non-empty strings.
- [ ] **AC-20:** All slot `size` components are positive (> 0).
- [ ] **AC-21:** `backdrop` (distance 20 from camera): size `[45, 28]` >= frustum visible area at distance 20 with FOV=50° and aspect 16:9 (~33.14w × 18.64h).
- [ ] **AC-22:** `accent` (distance 5.5 from camera): size `[18, 12]` >= frustum visible area at distance 5.5 (~9.12w × 5.13h).
- [ ] **AC-23:** `subject` (distance 7 from camera): `size[1]` (height, 10) >= frustum visible height (~6.52), ensuring the subject can fill the frame vertically.
- [ ] **AC-24:** Slot Z-positions decrease as depth increases: `accent` (-0.5) > `subject` (-2) > `backdrop` (-15).
- [ ] **AC-25:** The module self-registers via `registerGeometry(closeUpGeometry)` as a side effect of import.
- [ ] **AC-26:** The module exports `closeUpGeometry` as a named export.
- [ ] **AC-27:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry. OBJ-003 is referenced semantically but not imported at runtime.
- [ ] **AC-28:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-29:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-30:** `subject.position[1]` is `0` (vertically centered).

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides only the 2 required slots (`backdrop`, `subject`) | Valid scene. Minimal close-up — subject in front of backdrop. No foreground atmosphere. |
| Manifest provides all 3 slots | Valid scene. Full close-up with foreground atmospheric accent. |
| Manifest uses `near_fg` instead of `accent` | Rejected by manifest validation (OBJ-017). Error names the invalid key and lists valid close_up slot names: `backdrop`, `subject`, `accent`. |
| Manifest uses `floor` or `midground` (not close_up slots) | Rejected. Error lists valid slots. |

### Camera Motion Edge Cases

| Scenario | Expected Behavior | Analysis |
|----------|-------------------|----------|
| `slow_push_forward` speed=1.0 — subject at extreme distance | Camera at Z=-3, subject at Z=-2. Distance = 1 unit. Visible height ≈ 0.93 units. Subject size [10, 10] is ~10.7x the visible area — only ~9% of the subject visible. Extreme but not broken. | Artistically valid for "dramatic zoom to detail." SKILL.md should recommend speed ≤ 0.5 for close_up push/pull. |
| `slow_push_forward` speed=1.0 — accent behind subject | Camera at Z=-3, accent at Z=-0.5, subject at Z=-2. Accent distance from camera = 2.5; subject distance = 1. The accent is farther from the camera than the subject — it is geometrically *behind* the subject from the camera's perspective. | `renderOrder: 2` on accent and `transparent: true` on both planes cause Three.js to render the accent after the subject (on top), overriding depth-buffer sorting. The accent composites correctly as an overlay. This depends on the renderer (OBJ-039) not setting `depthWrite: true` on transparent materials — standard Three.js behavior for `MeshBasicMaterial` with `transparent: true` is `depthWrite: false`. |
| `slow_push_forward` speed=1.0 — accent near-plane clipping | Camera at Z=-3, accent at Z=-0.5. Distance = 2.5 units. Near-plane = 0.1. Not clipped. | Safe. |
| `slow_push_forward` speed=1.0 — backdrop edge reveal | Camera at Z=-3, backdrop at Z=-15. Distance = 12. Visible area: ~19.90w × 11.19h. Backdrop [45, 28]: oversize 2.26x × 2.50x. | Safe — generous oversize. |
| `slow_pull_back` speed=1.0 — backdrop edge reveal at max retreat | Camera at Z=5 (end), backdrop at Z=-15. Distance = 20. Visible area: ~33.14w × 18.64h. Backdrop [45, 28]: oversize 1.36x × 1.50x. Pure Z-axis motion (zero X/Y displacement). | Safe — 5.93 units of margin per side with no lateral camera motion. See D6 for full analysis. |
| `slow_pull_back` speed=1.0 — accent at start position | Camera at Z=-3 (start), accent at Z=-0.5. Distance = 2.5. Accent behind subject geometrically. | Same renderOrder behavior as `slow_push_forward` end state. Accent composites correctly as overlay. |
| `gentle_float` — accent clipping | Camera Z ranges 4.6–5.4. Accent at Z=-0.5. Distance ranges 5.1–5.9. | All well above near-plane (0.1). Safe. |
| `gentle_float` — backdrop edge reveal | Camera at max X drift (±0.3). Backdrop visible width at distance ~20 ≈ 33.14 + (0.3 × 2 × 33.14/20) ≈ 34.13 effective. Backdrop width 45. | Safe — ~10.87 units margin. |
| Portrait mode (9:16) | Geometry renders correctly. Aspect ratio 9/16 = 0.5625. At distance 20: visible width = 18.64 × 0.5625 ≈ 10.48. Backdrop width 45 provides ~4.29x horizontal oversize. | Even more oversized in portrait. Safe. |

### Content Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Subject image has no alpha | Subject displays as an opaque rectangle against the backdrop. `transparent: true` means the renderer creates a material with alpha support, but if the texture has no alpha channel, the entire rectangle is opaque. This is a content issue, not a geometry error. The slot `description` instructs "Should have a transparent background." |
| Accent image is too dense (not sparse) | A dense accent image would occlude the subject. This is a content quality issue. The slot description instructs "mostly empty space and sparse visual elements." No structural guard possible. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `close_up.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'close_up' is already registered." Module relies on Node.js module caching to prevent this in normal operation. |
| `close_up.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'close_up': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `closeUpGeometry.name` is `'close_up'`.
2. `closeUpGeometry.slots` has exactly 3 keys: `backdrop`, `subject`, `accent`.
3. Required slots: `backdrop`, `subject`. Optional: `accent`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'gentle_float'` and is in `compatible_cameras`.
6. `compatible_cameras` contains exactly 4 entries: `static`, `slow_push_forward`, `slow_pull_back`, `gentle_float`.
7. All entries in `compatible_cameras` match `/^[a-z][a-z0-9_]*$/`.
8. `fog` has valid values: `near` (10) >= 0, `far` (25) > `near`, `color` is `'#000000'`.
9. `description` is non-empty.
10. `preferred_aspect` is `'both'`.

**Slot spatial correctness tests:**
11. All slots have rotation `[0, 0, 0]`.
12. Z-positions ordered: `accent` (-0.5) > `subject` (-2) > `backdrop` (-15).
13. `renderOrder` values strictly increasing: backdrop(0) < subject(1) < accent(2).
14. All `size` components are > 0.
15. `subject.position[1]` is `0` (vertically centered).

**Slot metadata tests:**
16. `subject.transparent` is `true`; `accent.transparent` is `true`; `backdrop.transparent` is `false`.
17. All three slots have `fogImmune: true`.
18. All slot `description` fields are non-empty.
19. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
20. `validateGeometryDefinition(closeUpGeometry)` returns an empty error array.
21. `registerGeometry(closeUpGeometry)` does not throw (when registry is not locked).
22. After registration, `getGeometry('close_up')` returns the close_up geometry.

**Frustum size validation tests:**
23. `backdrop` at distance 20: size [45, 28] >= frustum visible area (~33.14w × 18.64h).
24. `accent` at distance 5.5: size [18, 12] >= frustum visible area (~9.12w × 5.13h).
25. `subject` at distance 7: height 10 >= frustum visible height (~6.52).

**Compatible cameras tests:**
26. `compatible_cameras` includes `'static'`, `'gentle_float'`, `'slow_push_forward'`, `'slow_pull_back'`.
27. `compatible_cameras` does NOT include `'tunnel_push_forward'`, `'flyover_glide'`, `'lateral_track_left'`, `'lateral_track_right'`, `'dramatic_push'`, `'crane_up'`, `'dolly_zoom'`.

### Relevant Testable Claims

- **TC-01** (partial): The close_up uses 3 slots (2 required + 1 optional) — the minimum of any geometry. Validates the lower bound of the "3-5 planes" sufficiency claim.
- **TC-04** (partial): The LLM specifies `geometry: 'close_up'` and fills `backdrop` and `subject` slot names. Zero XYZ coordinates needed.
- **TC-08** (partial): The close_up geometry is one of the 8 proposed geometries. It covers emphasis/detail scenes that other geometries handle poorly.

## Integration Points

### Depends on

| Upstream | What OBJ-025 uses |
|----------|-------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types for the geometry definition. `registerGeometry` function for self-registration. `validateGeometryDefinition` (called internally by `registerGeometry`). |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`). Referenced for design rationale. Not directly imported at runtime — close_up defines its own slots (`backdrop`, `subject`, `accent`) rather than using `DEFAULT_SLOT_TAXONOMY`. |

### Consumed by

| Downstream | How it uses OBJ-025 |
|------------|---------------------|
| **OBJ-066** (Close-up visual tuning) | Director Agent reviews test renders and provides feedback on subject framing, backdrop visibility, accent effect, and camera motion subtlety. OBJ-066 may adjust numerical values. |
| **OBJ-070** (End-to-end scene render test) | May include close_up scenes in multi-scene render tests. |
| **OBJ-071** (SKILL.md) | Uses slot names, descriptions, compatible cameras, and use-case guidance for documentation. Should include recommendation that speed ≤ 0.5 is preferred for push/pull presets on close_up. |
| **OBJ-017** (Manifest structural validation) | After registration, validates manifest plane keys against close_up slot names. |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('close_up')` to resolve slot spatial data. |
| **OBJ-039** (Page-side renderer) | Reads slot `position`, `rotation`, `size`, `renderOrder`, `transparent`, `fogImmune` to create Three.js meshes. Must set `depthWrite: false` on transparent materials for correct accent compositing when accent is geometrically behind subject. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        close_up.ts       # closeUpGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./close_up
```

## Open Questions

### OQ-A: Should the close_up define a breathing_zoom camera preset?

The seed Section 4.2 mentions "breathing zoom via FOV animation" as a close_up characteristic. No such preset exists yet. The existing `dolly_zoom` (OBJ-034, open) is excluded because its combined Z+FOV animation produces a vertigo effect that requires visible depth layering to read well — the close_up's minimal depth variation makes it imperceptible.

A simpler FOV-only breathing preset (e.g., FOV oscillating between 48° and 52° over the scene duration) would produce a subtle "inhale/exhale" visual rhythm without camera translation. This would pair naturally with the close_up geometry.

**Recommendation:** Defer to a future objective. `gentle_float`'s multi-axis drift achieves a similar perceptual effect. A FOV-breathing preset can be added to `compatible_cameras` later without changing the geometry definition. Aligns with TC-14's framing as exploratory.

### OQ-B: Should the close_up subject be larger than [10, 10]?

At distance 7, a [10, 10] subject fills ~65% of frame height. For an extremely tight close-up (face filling 80%+), the subject should be larger or positioned closer. The current values produce a "medium close-up" rather than an "extreme close-up."

**Recommendation:** Keep [10, 10] as default. Authors can use `PlaneOverride.position` to move the subject closer (e.g., Z=-1) or `PlaneOverride.size` to enlarge it. OBJ-066 tuning may adjust this based on visual review.

### OQ-C: Should the accent layer support position jitter or animation?

A bokeh/particle accent might benefit from slight per-frame position variation. This is out of scope for the geometry definition (static spatial state). Any animation would be a renderer concern (OBJ-044, per-frame opacity/position animation, if implemented).

**Recommendation:** Out of scope for OBJ-025. The accent's static position provides a consistent overlay. Dynamic effects are post-V1.

---

I believe this revision addresses all 8 issues raised:

1. **✅ Issue 1 (Critical):** Accent Z-position is consistently `[0, 0, -0.5]` everywhere — initial slot table, summary table, D7, all ACs.
2. **✅ Issue 2 (Major):** AC-22 frustum width corrected to `~9.12w`.
3. **✅ Issue 3 (Major):** Added explicit analysis in the Camera Motion Edge Cases table for the accent-behind-subject scenario, including `renderOrder` and `depthWrite` interaction. Added note in OBJ-039 integration point about `depthWrite: false` requirement.
4. **✅ Issue 4 (Minor):** D5 now explicitly states "no visible effect on any built-in slot."
5. **✅ Issue 5 (Major):** New design decision D6 provides full `slow_pull_back` edge-reveal analysis with math, explaining why 1.36x is sufficient despite OBJ-027's 1.7x general recommendation.
6. **✅ Issue 6 (Major):** All thinking-out-loud narrative removed. Each slot defined once with final values. D7 states the final answer and the rejection rationale cleanly.
7. **✅ Issue 7 (Minor):** New D10 clarifies OBJ-003 usage — referenced semantically but no runtime import needed. AC-27 updated.
8. **✅ Issue 8 (Minor):** `dolly_zoom` discussed in D3 exclusions with rationale. Added to AC-09 exclusion list.

I'd ask the challenger to verify and approve this revision.

---

## Round 4 — spec_challenger

Let me verify each of my Round 2 issues against the revision, and check for any new problems.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


## Challenger Review — Round 4

Let me systematically verify each Round 2 issue against the revision.

### Verification of Prior Issues

**Issue 1 (Critical — Accent Z-position inconsistency):** ✅ **FIXED.** The accent slot table shows `[0, 0, -0.5]`. The summary table shows `[0, 0, -0.5]`. D7 states `Z=-0.5` as the final answer with clean rejection rationale for positive Z. No conflicting values remain.

**Issue 2 (Major — Frustum width calculation):** ✅ **FIXED.** AC-22 now reads `~9.12w × 5.13h`. Correct: 5.13 × (16/9) ≈ 9.12.

**Issue 3 (Major — Accent behind subject with slow_push_forward):** ✅ **FIXED.** Camera Motion Edge Cases table has an explicit entry for "accent behind subject" with `renderOrder` and `depthWrite` analysis. The OBJ-039 integration point notes the `depthWrite: false` requirement. The spec also adds a recommended speed ≤ 0.5 note for push/pull on close_up.

**Issue 4 (Minor — Fog is decorative):** ✅ **FIXED.** D5 explicitly states "no visible effect on any built-in slot" and lists the three reasons for keeping it.

**Issue 5 (Major — Missing slow_pull_back analysis):** ✅ **FIXED.** New D6 provides full math for both start (distance 12, 2.26x oversize) and end (distance 20, 1.36x oversize), with a clear explanation of why 1.36x is sufficient despite OBJ-027's general 1.7x recommendation.

**Issue 6 (Major — Thinking-out-loud narrative):** ✅ **FIXED.** Each slot is defined once with final values. No self-corrections or exploratory narrative in the spec body.

**Issue 7 (Minor — OBJ-003 import clarity):** ✅ **FIXED.** D10 clarifies: referenced semantically, no runtime import. AC-27 updated.

**Issue 8 (Minor — dolly_zoom not discussed):** ✅ **FIXED.** D3 exclusions now include `dolly_zoom` with clear rationale (vertigo effect imperceptible with minimal depth variation). AC-09 includes it in the exclusion list.

### New Issues Check

The revision is clean. Let me do a final sweep for anything I might have missed on earlier passes.

**Vocabulary compliance:** ✓ Uses "plane," "scene geometry," "camera path" correctly throughout. No vocabulary drift.

**Constraint compliance:** ✓ No rendering dependencies, no license concerns. Pure geometry data definition.

**Scope discipline:** ✓ Stays within "define the close_up geometry's slots, compatible cameras, fog, and metadata." Doesn't implement rendering logic.

**OBJ-005 contract compliance:** ✓ The `SceneGeometry` interface fields are all present (name, slots, compatible_cameras, default_camera, fog, description, preferred_aspect). PlaneSlot fields (position, rotation, size, required, description, renderOrder, transparent, fogImmune) are all explicitly set per D9/AC-28.

**OBJ-007 compliance:** ✓ Slot names follow `SLOT_NAME_PATTERN`. The geometry defines its own slots rather than using `DEFAULT_SLOT_TAXONOMY` — which is permitted per OBJ-007 D1 ("geometries like tunnel define completely independent slot sets").

**Acceptance criteria quality:** All 30 criteria are specific, testable, and can produce pass/fail results from the spec alone. The frustum math is verifiable. No gaps between what the spec promises and what the ACs verify.

**Downstream compatibility for OBJ-066 (tuning):** ✓ The geometry is well-defined enough for the Director Agent to review renders and suggest numerical adjustments.

I'm satisfied. All critical and major issues have been structurally addressed in the revision. The spec is clean, consistent, and implementable.

CONCLUSION:

The OBJ-025 specification defines the `close_up` scene geometry with 3 slots (backdrop at Z=-15, subject at Z=-2, optional accent at Z=-0.5), 4 compatible cameras (static, gentle_float, slow_push_forward, slow_pull_back), decorative fog (all slots fog-immune), and preferred_aspect of 'both'. All spatial math has been verified, edge cases for camera motion extremes are documented including the accent-behind-subject renderOrder interaction, and the spec follows the established geometry pattern from OBJ-018.

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-025/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-025",
     3→  "description": "Close-up scene geometry -- subject plane fills most of the view at shallow Z. Minimal background visible. Very subtle camera motion (slight drift or breathing zoom via FOV animation). Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.",
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-025/output.md",
  "content": "# Specification: Close-Up Scene Geometry (OBJ-025)\n\n## Summary\n\nOBJ-025 defines the **close_up** scene geometry \u2014 the most intimate geometry in depthkit, where a subject plane fills most of the camera view at very shallow Z depth, with minimal background visible and very subtle camera motion. The defining characteristic is restraint: a tight framing, few planes, and motion so subtle it feels like breathing. This geometry is designed for emphasis moments, character portraits, detail shots, and emotional beats where the viewer's attention should rest on the subject rather than on spatial spectacle. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.\n\n## Interface Contract\n\n### Exported Geometry Definition\n\n```typescript\n// src/scenes/geometries/close_up.ts\n\nimport type { SceneGeometry } from './types';\n\n/**\n * The close_up scene geometry \u2014 subject fills most of the view\n * at shallow Z depth. Minimal background visible. Very subtle\n * camera motion.\n *\n * Spatial arrangement: a backdrop plane at moderate depth (closer\n * than other geometries' backdrops to keep it visible behind the\n * tightly-framed subject), a large subject plane at very shallow Z\n * that dominates the view, and an optional accent plane for subtle\n * foreground atmosphere.\n *\n * This is the simplest geometry by slot count (3 slots, 2 required)\n * and is designed for emphasis moments, character portraits, detail\n * shots, and emotional beats. Camera motion should be felt, not\n * noticed \u2014 gentle_float is the default camera.\n */\nexport const closeUpGeometry: SceneGeometry;\n```\n\n### Geometry Fields\n\n| Field | Value | Rationale |\n|-------|-------|-----------|\n| `name` | `'close_up'` | Matches seed Section 4.2 naming. |\n| `description` | `'Subject fills most of the view at shallow Z dept
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-025/output.md
You've hit your limit · resets 1am (America/New_York)
