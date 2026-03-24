# Deliberation Transcript: OBJ-024

---

## Round 1 — spec_author

Looking at the objective metadata, seed constraints, and dependency specs, I'll propose a complete specification for OBJ-024: Panorama Scene Geometry.

Let me first check the existing codebase for any relevant patterns from already-implemented geometries.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me look at existing geometry implementations for patterns to follow.
[Tool: Glob]
  Input: {
  "pattern": "**/geometries/*.ts"
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
  "pattern": "**/nodes/OBJ-022/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-024/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-024/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-022/output.md"
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
  "offset": 200
}
[Tool Result]    200→- **`flyover_glide`**: Requires a ground plane below the camera. The diorama has no ground.
   201→- **`lateral_track_left/right`**: Lateral tracking with rotated wings risks revealing the wing planes' back faces or edges. The wing rotation means the camera would approach one wing and retreat from the other during lateral motion, creating asymmetric and potentially jarring perspective shifts. Excluded for V1; could be added after OBJ-063 tuning validates edge-reveal safety.
   202→- **`crane_up`**: Vertical camera motion in a flat-layer composition has little spatial meaning. Excluded for V1.
   203→- **`dolly_zoom`**: FOV animation needs careful validation with wing rotation. Deferred.
   204→
   205→**Forward reference note:** Of the 5 listed presets, `static` (OBJ-026), `slow_push_forward`/`slow_pull_back` (OBJ-027), and `gentle_float` (OBJ-031) are verified. `dramatic_push` (OBJ-032) is a forward reference (status `open`). The `compatible_cameras` list may be revised as OBJ-... [truncated]
Now let me check the OBJ-003 spatial foundations and camera presets (OBJ-006):
[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-003/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-006/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
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
  "limit": 100
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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md",
  "offset": 250,
  "limit": 100
}
[Tool Result]    250→   * Can be overridden by CameraParams.easing in the manifest.
   251→   */
   252→  defaultEasing: EasingName;
   253→
   254→  /**
   255→   * Names of scene geometries this path is designed to work with.
   256→   * The geometry-camera compatibility validator (OBJ-041) uses this
   257→   * to reject invalid combinations in the manifest.
   258→   *
   259→   * Must be non-empty. List geometry names explicitly — no wildcards.
   260→   * Until OBJ-005 finalizes geometry names, use provisional names
   261→   * from seed Section 4.2: 'stage', 'tunnel', 'canyon', 'flyover',
   262→   * 'diorama', 'portal', 'panorama', 'close_up'.
   263→   *
   264→   * When a new geometry is added, each preset must explicitly declare
   265→   * compatibility with it (or not). This keeps compatibility auditable.
   266→   *
   267→   * NOTE: validateCameraPathPreset checks only for non-emptiness.
   268→   * Geometry name existence validation belongs to OBJ-041, which
   269→   * cross-referen... [truncated]
Now let me check what camera presets reference `panorama` as a compatible geometry:
[Tool: Grep]
  Input: {
  "pattern": "panorama",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes",
  "output_mode": "content",
  "glob": "**/output.md",
  "-C": 2,
  "head_limit": 60
}
[Tool Result] nodes/OBJ-075/output.md-97-### D7: TC-01 Evaluates Slot Count Per Scene Type, Not Per Geometry
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-075/output.md-98-
nodes/OBJ-075/output.md:99:**Decision:** TC-01's "15 scene types" are common video scene types (e.g., "person explaining a concept," "landscape panorama," "product showcase"). For each scene type, the evaluator determines: (a) which geometry best fits, (b) how many planes that geometry uses for the scene, and (c) whether 3–5 planes are sufficient or whether the scene feels flat/incomplete.
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-075/output.md-100-
nodes/OBJ-075/output.md-101-**Rationale:** TC-01's claim is "3-5 textured planes handles at least 90% of common YouTube/social media video scene types." The unit of analysis is the scene type, not the geometry. A scene type might map to different geometries — the question is whether any geometry can handle it with ≤... [truncated]
Now let me check what camera presets are verified and which ones list `panorama` compatibility:
[Tool: Grep]
  Input: {
  "pattern": "compatibleGeometries.*panorama|panorama.*compatible",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes",
  "output_mode": "content",
  "glob": "**/output.md"
}
[Tool Result] nodes/OBJ-071/output.md:247:- [ ] **AC-32:** Lateral track compatible geometries documented as: `stage`, `canyon`, `diorama`, `portal`, `panorama` — matching OBJ-028's `compatibleGeometries` exactly.
nodes/OBJ-026/output.md:39:| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']` | All eight geometries from seed Section 4.2. A static camera is universally safe. |
nodes/OBJ-026/output.md:147:- [ ] **AC-11:** `compatibleGeometries` contains exactly: `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'panorama', 'close_up']`.
nodes/OBJ-031/output.md:277:- [ ] **AC-20:** `compatibleGeometries` includes all 8 geometry names: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.
nodes/OBJ-028/output.md:100:compatibleGeometries: ['stage', 'canyon', 'diorama', 'portal', 'panorama']
nodes/OBJ-028/output.md:244:- [ ] **AC-25:** Both presets' `compatibleGeometries` include `'stage'`, `'canyon'`... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "panorama",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md",
  "output_mode": "content",
  "-C": 2
}
[Tool Result] No matches found

[Tool: Grep]
  Input: {
  "pattern": "panorama",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md",
  "output_mode": "content",
  "-C": 2
}
[Tool Result] No matches found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md",
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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md",
  "limit": 15
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
Now I have a comprehensive understanding of the patterns. Let me also quickly check the OBJ-028 output to understand how lateral tracking interacts with panorama:
[Tool: Grep]
  Input: {
  "pattern": "panorama",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "output_mode": "content",
  "-C": 4
}
[Tool Result] 96-
97-### Compatible Geometries
98-
99-```typescript
100:compatibleGeometries: ['stage', 'canyon', 'diorama', 'portal', 'panorama']
101-```
102-
103-**Rationale for each:**
104-- **`stage`** — Classic tracking shot past a subject against a backdrop. The primary use case.
105-- **`canyon`** — Tracking between tall walls. X displacement slides past the walls, revealing depth.
106-- **`diorama`** — Lateral motion across layered planes produces strong parallax separation — the defining visual of a diorama.
107-- **`portal`** — Lateral track across concentric frames creates interesting asymmetric reveal.
108:- **`panorama`** — Lateral translation across a wide backdrop is natural for panoramic environments.
109-
110-**Excluded geometries and rationale:**
111-- **`tunnel`** — A tunnel is designed for forward motion (Z-axis push). Lateral tracking inside a tunnel would slide the camera toward a wall, breaking the spatial illusion. The tunnel's walls are sized for forward motion, not lateral.... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "limit": 90
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
Now I have a comprehensive understanding of the patterns, dependencies, and existing geometry conventions. Let me propose the complete specification for OBJ-024.

---

# Specification: Panorama Scene Geometry (OBJ-024)

## Summary

OBJ-024 defines the **panorama** scene geometry — a multi-panel panoramic environment where three flat backdrop planes are arranged in a 180° arc, approximating a cylinder around the camera position. The defining characteristic is that the camera **rotates (pans)** rather than translates through Z-space, creating sweeping environmental survey shots. This is a "pure environment" geometry with no foreground subjects — all three backdrop panels are required. The curved arrangement means that existing translation-based camera presets (lateral track) produce inter-panel parallax as a natural bonus, since the side panels are geometrically closer to the camera than the center panel. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.

## Interface Contract

### Exported Geometry Definition

```typescript
// src/scenes/geometries/panorama.ts

import type { SceneGeometry } from './types';

/**
 * The panorama scene geometry — three flat backdrop panels arranged
 * in a 180° arc approximating a cylinder around the camera position.
 *
 * Spatial arrangement: three flat planes at 60° intervals in a
 * semicircle at radius 25 from the camera. The center panel faces
 * the camera directly; the left and right panels are rotated ±60°
 * (±PI/3) around the Y-axis to face inward toward the camera.
 * Camera pans (rotates) horizontally across the arc, or translates
 * laterally for a parallax-enriched sweep.
 *
 * Pure environment — no foreground elements, no subjects. Best for
 * wide landscapes, cityscapes, astronomical panoramas, and
 * atmospheric establishing shots.
 */
export const panoramaGeometry: SceneGeometry;
```

### Geometry Fields

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'panorama'` | Matches seed Section 4.2 naming |
| `description` | `'A multi-panel panoramic environment. Three backdrop panels arranged in a 180° arc approximate a cylinder around the camera. Camera sweeps across the wide environment via lateral tracking or horizontal panning. No foreground subjects — pure environment. Best for wide landscapes, cityscapes, astronomical panoramas, and atmospheric establishing shots.'` | Describes the spatial feel per OBJ-005's `description` contract |
| `default_camera` | `'gentle_float'` | See D4. No rotation-based pan preset exists yet; `gentle_float` provides subtle ambient motion universally. |
| `compatible_cameras` | `['static', 'lateral_track_left', 'lateral_track_right', 'gentle_float']` | See D5. All four are verified presets. |
| `fog` | `undefined` (omitted) | See D6. Fog creates brightness discontinuity between panels at different distances. |
| `preferred_aspect` | `'landscape'` | The 180° horizontal arc reads best in a wide frame. In portrait, the narrow horizontal FOV severely limits panning range. |

### Slot Definitions

The panorama geometry defines **3 slots — all required**. This is the minimum and maximum — the panorama is structurally a 3-panel cylindrical environment with no optional embellishments. The "pure environment, no foreground" design (seed Section 4.2) is enforced structurally by having no subject, near_fg, or floor slots.

All positions assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50° (seed Section 8.2). The arc of radius R=25 is centered on the camera's starting position, placing panels at distance 25 from the camera. Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate lateral track camera motion (OBJ-028: 6 world units of X displacement at `speed=1.0`).

Following the convention established by OBJ-018: the panorama geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

### Arc Geometry Derivation

The three panels are arranged at 60° intervals in a semicircle of radius R=25, centered on the camera position `[0, 0, 5]`. For a panel at angle θ (measured counter-clockwise from the forward -Z direction when viewed from above):

```
position = [R × sin(θ),  0,  5 - R × cos(θ)]
rotation = [0,  -θ,  0]     // rotated around Y so the panel's normal faces the camera
```

| Panel | θ (degrees) | θ (radians) | Position | Rotation |
|-------|-------------|-------------|----------|----------|
| `backdrop_left` | -60° | -π/3 | `[-21.65, 0, -7.5]` | `[0, π/3, 0]` |
| `backdrop_center` | 0° | 0 | `[0, 0, -20]` | `[0, 0, 0]` |
| `backdrop_right` | +60° | +π/3 | `[21.65, 0, -7.5]` | `[0, -π/3, 0]` |

Panel width: Each panel covers a 60° arc. The panel width needed to fully cover 60° at radius 25 is `2 × R × tan(30°) ≈ 28.87`. Using width=30 provides approximately 1° of angular overlap at each inter-panel seam, preventing visible gaps.

Panel height: At distance 25 from the camera with FOV=50°, visible height = `2 × 25 × tan(25°) ≈ 23.3`. Using height=28 provides ~20% oversizing vertically for camera Y-drift during `gentle_float`.

#### Slot: `backdrop_left`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[-21.65, 0, -7.5]` | Left panel of arc. Arc position at θ = -60°. Distance from camera: 25 units. |
| `rotation` | `[0, Math.PI / 3, 0]` | Rotated +60° around Y to face inward toward the camera. This is the arc tangent angle, NOT a `PLANE_ROTATIONS` constant — it is panorama-specific. |
| `size` | `[30, 28]` | Width 30 covers 60° arc with ~1° overlap. Height 28 is ~20% oversized vs visible height at distance 25 (~23.3). |
| `required` | `true` | All three panels are required. Without the left panel, the camera's static FOV (~79° horizontal) exceeds the center panel's coverage (~62°), creating edge reveals. See D3. |
| `description` | `'Left panel of the panoramic arc. Should contain the left third of a wide environmental scene.'` | |
| `renderOrder` | `0` | All panels share renderOrder 0. The Z-buffer naturally resolves overlap since side panels (Z=-7.5) are closer than center (Z=-20). See D7. |
| `transparent` | `false` | Environment backdrops are opaque. |
| `fogImmune` | `true` | See D6. Prevents brightness discontinuity between panels at different distances if fog is overridden in manifest. |

#### Slot: `backdrop_center`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -20]` | Center panel, straight ahead. Arc position at θ = 0°. Distance from camera: 25 units. |
| `rotation` | `[0, 0, 0]` | `PLANE_ROTATIONS.FACING_CAMERA` — faces the camera directly. |
| `size` | `[30, 28]` | Same as side panels for uniform panel sizing. |
| `required` | `true` | The center panel is the primary environmental backdrop. |
| `description` | `'Center panel of the panoramic arc. Should contain the central portion of a wide environmental scene.'` | |
| `renderOrder` | `0` | Shared with side panels. See D7. |
| `transparent` | `false` | Opaque. |
| `fogImmune` | `true` | Same rationale as backdrop_left. |

#### Slot: `backdrop_right`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[21.65, 0, -7.5]` | Right panel. Arc position at θ = +60°. Mirror of backdrop_left. |
| `rotation` | `[0, -Math.PI / 3, 0]` | Rotated -60° around Y. Mirror of backdrop_left's rotation. |
| `size` | `[30, 28]` | Same as other panels. |
| `required` | `true` | Required for full FOV coverage. See D3. |
| `description` | `'Right panel of the panoramic arc. Should contain the right third of a wide environmental scene.'` | |
| `renderOrder` | `0` | Shared. |
| `transparent` | `false` | Opaque. |
| `fogImmune` | `true` | Same rationale. |

### Slot Summary Table

| Slot | Position | Rotation | Size | Required | Transparent | Fog Immune | Render Order |
|------|----------|----------|------|----------|-------------|------------|-------------|
| `backdrop_left` | `[-21.65, 0, -7.5]` | `[0, PI/3, 0]` | `[30, 28]` | **yes** | no | **yes** | 0 |
| `backdrop_center` | `[0, 0, -20]` | `[0, 0, 0]` | `[30, 28]` | **yes** | no | **yes** | 0 |
| `backdrop_right` | `[21.65, 0, -7.5]` | `[0, -PI/3, 0]` | `[30, 28]` | **yes** | no | **yes** | 0 |

### Registration Side Effect

```typescript
// src/scenes/geometries/panorama.ts (bottom of file)

import { registerGeometry } from './registry';

// Self-registers when the module is imported.
registerGeometry(panoramaGeometry);
```

### Module Exports

```typescript
// src/scenes/geometries/panorama.ts
export { panoramaGeometry };
```

The barrel export `src/scenes/geometries/index.ts` must re-export from `./panorama` so that importing the geometries barrel triggers registration.

## Design Decisions

### D1: Three required panels — the minimum viable panorama

The panorama is defined by its multi-panel cylindrical arrangement. All three panels are required — there are no optional slots. This is the leanest geometry in depthkit (3 slots vs stage's 6, tunnel's 5, diorama's 6).

**Why all required?** With FOV=50° vertical, the horizontal FOV for 16:9 is approximately 79°. Each panel subtends ~62° of arc. A single center panel does NOT cover the full horizontal FOV — the camera would see past the panel edges even when looking straight ahead. The minimum panel count for full static coverage is 2, but 3 panels provide the ~180° arc needed for meaningful panning/tracking. Making any panel optional would require complex conditional validation ("this camera preset requires panels X and Y") that the `compatible_cameras` system doesn't support.

3 slots is squarely within TC-01's 3-5 range.

### D2: Curved panel arrangement at R=25, 60° spacing

Three flat panels arranged at 60° intervals in a semicircle of radius 25 from the camera position. This approximates a cylinder with minimal panel count while providing:

- **180° of angular coverage**: allows ±50° of panning from center (180° - 79° hFOV ≈ 101° of travel).
- **Natural inter-panel parallax during lateral translation**: the side panels (distance ~12.5 along Z from camera) are closer than the center panel (distance 25), so they move faster during lateral tracking. This parallax enhances the immersive feel without requiring additional planes.
- **Clean seam handling**: the ~2° of angular overlap between adjacent panels prevents visible gaps. The Z-buffer naturally resolves overlap (closer side panels render on top). See D7.

**Why R=25?** This places the center panel at Z=-20 (distance 25), similar to the backdrop distance in stage/diorama geometries. The panoramic environment feels spacious — distant enough for landscapes, close enough to retain texture detail. Smaller radii (R=15) would make the cylinder feel cramped; larger radii (R=40) would push panels beyond comfortable fog/visibility ranges.

**Alternative considered — single wide flat plane:** A single plane of width ~100 at Z=-25 could cover the same angular range. Rejected because: (a) it produces no inter-panel parallax during lateral tracking (feels flat), (b) it doesn't approximate a cylinder (the edges undergo severe perspective distortion), and (c) the seed explicitly mentions "curved set of planes approximating a cylinder" as the intended approach. A single wide plane is better served by the stage geometry with a wide backdrop.

### D3: All panels required eliminates per-slot camera conditioning

Making all panels required means every compatible camera preset can assume full 180° coverage. This avoids a gap in the `compatible_cameras` system, which validates camera names at the geometry level, not conditioned on which optional slots are filled. If panels were optional, a panning camera would be listed as "compatible" but would fail if the author omitted the side panels — an authorability trap that violates C-06.

### D4: `gentle_float` as default camera — placeholder for future pan presets

The seed describes the panorama as "camera rotates (pans) rather than translates." However, no rotation-based camera preset exists in the current DAG. OBJ-026-034 define translation-based presets (push, pull, track, crane) and the universal static/float presets. The panorama's ideal default camera would be a `slow_pan` or `pan_right` preset that rotates the camera around Y while keeping position fixed.

`gentle_float` is chosen as default because it's verified (OBJ-031), universal, and provides subtle ambient motion. It is a temporary default — when rotation-based pan presets are defined (see OQ-A), the default should be updated to a pan preset.

### D5: Compatible cameras — existing verified presets only, plus forward references

The panorama lists 4 compatible cameras, all verified:

- **`static`** (OBJ-026): Universal baseline. A still panoramic tableau.
- **`lateral_track_left`** (OBJ-028): Lateral translation across the panoramic arc. OBJ-028 explicitly lists `panorama` in its `compatibleGeometries`. The 6-unit X displacement at speed=1.0 produces a sweeping effect across the 180° arc, with inter-panel parallax.
- **`lateral_track_right`** (OBJ-028): Mirror of above.
- **`gentle_float`** (OBJ-031): Subtle ambient drift. Universal.

**Excluded:**
- **`slow_push_forward` / `slow_pull_back`** (OBJ-027): Forward Z push makes no sense for a cylindrical arrangement — the camera would push into the center panel while the side panels retreat. OBJ-027 explicitly excludes `panorama`.
- **`tunnel_push_forward`** (OBJ-029): Tunnel-specific.
- **`flyover_glide`** (OBJ-030): Requires below-camera ground plane.
- **`crane_up`** (OBJ-033): Vertical motion has limited value in a pure horizontal panorama.
- **`dramatic_push`** (OBJ-032, open): Forward Z push, same exclusion as slow_push.
- **`dolly_zoom`** (OBJ-034, open): Z push + FOV animation — same exclusion.

**Forward references:** Rotation-based pan presets (`pan_left`, `pan_right`, `slow_pan`) are the natural camera motions for this geometry but are not yet defined in the DAG. When defined, they should be added to `compatible_cameras` and one should replace `gentle_float` as the default. See OQ-A.

### D6: No default fog — prevents inter-panel brightness discontinuity

The three panels are at different distances from the camera: center at distance 25, sides at distance ~12.5 (along Z from camera). Fog operates on distance from camera, so with fog enabled, the center panel would fade significantly more than the side panels. This creates a visible brightness step at the panel seams — the side panel's edge is bright while the center panel's adjacent region is fogged. This artifact is unique to the curved arrangement and unacceptable.

All panels are marked `fogImmune: true` as a safety measure. If an author overrides fog in the manifest, the panorama panels remain at full brightness. The fog immunity prevents the brightness discontinuity regardless of fog settings.

**Why not just omit fog and leave fogImmune as false?** Because the manifest's per-scene fog override (seed Section 8.6, OBJ-005's fog contract) allows an author to add fog to any scene. Without fogImmune, an author who casually adds fog to a panorama scene would get the brightness discontinuity — a subtle, confusing visual artifact that violates C-06 (blind-authorable). Making all panels fogImmune prevents this trap.

### D7: Shared renderOrder 0 — Z-buffer resolves panel overlap

All three panels share `renderOrder: 0`. At the ~2° overlap between adjacent panels, both panels project to similar screen positions. The Z-buffer determines which pixel wins based on distance to camera. Since the side panels (Z=-7.5, distance ~12.5) are closer than the center panel (Z=-20, distance 25), the Z-buffer shows the side panel content in the overlap zone. This creates a clean, consistent transition: the center panel is only visible in the angular range not covered by the (closer) side panels.

Z-fighting is not a concern because the panels are at very different distances (12.5 vs 25) — well beyond the Z-buffer's precision limits.

**Alternative considered — staggered renderOrder:** Setting side panels to renderOrder 1 and center to 0 would explicitly force sides on top. This is equivalent to the Z-buffer behavior for this arrangement, so it's unnecessary. Using shared renderOrder 0 is simpler and more transparent.

### D8: No subject, no foreground, no floor — structural enforcement of "pure environment"

The seed explicitly says panorama has "No foreground elements. Pure environment." Rather than having subject/near_fg slots that are optional (which an LLM might fill anyway), the panorama enforces this by simply not defining those slots. An LLM that tries to add a `subject` plane to a panorama scene gets a manifest validation error — the slot doesn't exist.

This is a structural rather than advisory constraint, which is more robust for blind authoring (C-06).

### D9: Panel positions use exact trigonometric values

The panel positions use `sin(60°) = √3/2 ≈ 0.8660254...` truncated to `21.65`. The exact value is `25 × √3/2 = 21.650635...`. Truncating to 2 decimal places introduces less than 0.001 world units of error, which is invisible at any rendering resolution. The implementer should use `25 * Math.sin(Math.PI / 3)` for precision, but the spec documents the truncated value for readability. The spec-level position is `[-21.65, 0, -7.5]`; the implementation should compute it from the arc formula.

### D10: PlaneSlot construction, not DepthSlot — follows OBJ-018 convention

Same as OBJ-018 and OBJ-022: the geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration. OBJ-007's `DepthSlot` fields (`promptGuidance`, `expectsAlpha`) are not part of the `PlaneSlot` type.

**Prompt guidance gap:** The panorama introduces custom slots (`backdrop_left`, `backdrop_center`, `backdrop_right`) not present in OBJ-007's `DEFAULT_SLOT_TAXONOMY`. Downstream consumers (OBJ-071 SKILL.md, OBJ-053) must derive prompt guidance from `PlaneSlot.description` fields. Same gap noted in OBJ-018 and OBJ-022.

### D11: Explicit optional field policy — follows OBJ-018 convention

All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

### D12: `preferred_aspect` is `landscape`

The 180° horizontal arc is the panorama's defining feature. In landscape (16:9), the ~79° horizontal FOV allows meaningful panning across the arc. In portrait (9:16), the horizontal FOV narrows to approximately `2 × atan(tan(25°) × 9/16) ≈ 27°` — barely covering half of a single panel's angular width. Panning in portrait would be extremely limited (180° - 27° = 153° of travel, but each frame shows only a narrow slice). The geometry renders correctly in portrait (seed C-04), but SKILL.md should strongly guide LLMs toward landscape.

## Acceptance Criteria

- [ ] **AC-01:** `panoramaGeometry.name` is `'panorama'`.
- [ ] **AC-02:** `panoramaGeometry.slots` contains exactly 3 keys: `backdrop_left`, `backdrop_center`, `backdrop_right`.
- [ ] **AC-03:** All 3 slots have `required: true`. There are no optional slots.
- [ ] **AC-04:** `panoramaGeometry.default_camera` is `'gentle_float'`.
- [ ] **AC-05:** `panoramaGeometry.default_camera` appears in `panoramaGeometry.compatible_cameras`.
- [ ] **AC-06:** `panoramaGeometry.compatible_cameras` includes `'static'` and `'gentle_float'` (verified presets from OBJ-026 and OBJ-031).
- [ ] **AC-07:** `panoramaGeometry.compatible_cameras` includes `'lateral_track_left'` and `'lateral_track_right'` (verified presets from OBJ-028).
- [ ] **AC-08:** `panoramaGeometry.compatible_cameras` does NOT include `'slow_push_forward'`, `'slow_pull_back'`, `'tunnel_push_forward'`, or `'flyover_glide'`.
- [ ] **AC-09:** `panoramaGeometry.compatible_cameras` contains exactly 4 entries.
- [ ] **AC-10:** `panoramaGeometry.fog` is `undefined` (no default fog).
- [ ] **AC-11:** `panoramaGeometry.description` is non-empty and describes a multi-panel panoramic environment.
- [ ] **AC-12:** `panoramaGeometry.preferred_aspect` is `'landscape'`.
- [ ] **AC-13:** The `backdrop_left` slot rotation is `[0, Math.PI / 3, 0]` (positive Y rotation, 60° inward).
- [ ] **AC-14:** The `backdrop_right` slot rotation is `[0, -Math.PI / 3, 0]` (negative Y rotation, 60° inward, mirroring `backdrop_left`).
- [ ] **AC-15:** The `backdrop_center` slot rotation is `[0, 0, 0]` (`PLANE_ROTATIONS.FACING_CAMERA`).
- [ ] **AC-16:** All 3 slots have `transparent: false`.
- [ ] **AC-17:** All 3 slots have `fogImmune: true`.
- [ ] **AC-18:** All 3 slots have `renderOrder: 0`.
- [ ] **AC-19:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-20:** `registerGeometry(panoramaGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-21:** All slot `description` fields are non-empty strings.
- [ ] **AC-22:** All slot `size` components are positive (> 0).
- [ ] **AC-23:** All 3 slots have identical `size` values (`[30, 28]`).
- [ ] **AC-24:** Panel height (28) >= frustum visible height at distance 25 with FOV=50° (~23.3). Oversizing factor >= 1.0.
- [ ] **AC-25:** Panel width (30) >= arc chord width for 60° at R=25 (`2 × 25 × tan(30°) ≈ 28.87`). Panels slightly overlap.
- [ ] **AC-26:** `backdrop_left.position[0]` is the negation of `backdrop_right.position[0]` (lateral symmetry).
- [ ] **AC-27:** `backdrop_left.position[1]` equals `backdrop_right.position[1]` equals `backdrop_center.position[1]` (all at same Y=0).
- [ ] **AC-28:** `backdrop_left.position[2]` equals `backdrop_right.position[2]` (side panels at same Z).
- [ ] **AC-29:** `backdrop_left.rotation[1]` is the negation of `backdrop_right.rotation[1]` (rotation symmetry).
- [ ] **AC-30:** `backdrop_left.size` equals `backdrop_right.size` (size symmetry).
- [ ] **AC-31:** The module self-registers via `registerGeometry(panoramaGeometry)` as a side effect of import.
- [ ] **AC-32:** The module exports `panoramaGeometry` as a named export.
- [ ] **AC-33:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants.
- [ ] **AC-34:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-35:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-36:** Side panel positions are consistent with arc formula: `position[0] ≈ ±25 × sin(60°)` and `position[2] ≈ 5 - 25 × cos(60°)` (camera at z=5, R=25).

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Manifest provides all 3 required slots | Valid scene. Full panoramic environment. This is the only valid configuration — there are no optional slots. |
| Manifest omits any of the 3 slots | Rejected by manifest validation (OBJ-017) — all slots are required. Error names the missing slot. |
| Manifest provides an extra unknown slot (e.g., `subject`, `floor`, `sky`) | Rejected by manifest validation. Error names the invalid key and lists valid slot names: `backdrop_left`, `backdrop_center`, `backdrop_right`. |
| Manifest uses `backdrop` instead of `backdrop_center` | Rejected — `backdrop` is not a panorama slot name. Error suggests valid names. |
| Lateral track camera at maximum displacement — edge reveal check | Camera at [3, 0, 5] (rightmost position in `lateral_track_left`). Side panels at Z=-7.5 are ~12.7 units from camera. Visible half-width at that distance ≈ `12.7 × tan(39.6°) ≈ 10.5`. Right panel center at X=21.65, camera at X=3, so panel appears at relative X=18.65. Panel half-width = 15. Panel right edge at relative X = 18.65+15 = 33.65, well beyond visible half-width 10.5+3 = 13.5. Panel extends past frame. Left edge at relative X = 18.65-15 = 3.65, well within frame. Safe. Full edge-reveal validation deferred to OBJ-040. |
| Portrait mode (9:16) | Geometry renders correctly (C-04). Horizontal FOV narrows to ~27°, showing only a small fraction of the 180° arc. Panning would reveal most content but each frame is very narrow. `preferred_aspect: 'landscape'` guides LLMs away. |
| Panel seam visibility | At the ~2° overlap zone between adjacent panels, the Z-buffer shows the closer side panel. If images are continuous (split panoramic photo), the seam is invisible. If images are independently generated, a slight discontinuity may be visible at the side panel's edge. SKILL.md should guide authors to use visually continuous images. |
| Fog override in manifest | All panels are `fogImmune: true`. Fog has no effect on the panorama panels, preventing brightness discontinuity. Other scene elements (if any were added via manifest extensions) would still be affected. |
| Camera at arc center looking directly at left panel | Camera at [0, 0, 5] with lookAt rotated 60° left. Center panel at [0, 0, -20] is now off to the right in the view. Left panel at [-21.65, 0, -7.5] is centered. The 180° arc provides ~50° of panning in each direction before the edge of the opposite panel would be revealed. Safe for rotation-based cameras with up to ±50° of pan. |
| Back-face visibility for side panels | Side panels rotated ±60° show only their front face when the camera is at the arc center. The camera would need to be behind a side panel to see its back face — impossible when the camera stays within the arc. Three.js `side: THREE.FrontSide` (default) additionally prevents back-face rendering. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `panorama.ts` imported multiple times | `registerGeometry` throws on second call: "Geometry 'panorama' is already registered." Module relies on Node.js module caching. |
| `panorama.ts` imported after registry is locked | `registerGeometry` throws: "Cannot register geometry 'panorama': registry is locked." |

## Test Strategy

### Unit Tests

**Geometry structure tests:**
1. `panoramaGeometry.name` is `'panorama'`.
2. `panoramaGeometry.slots` has exactly 3 keys: `backdrop_left`, `backdrop_center`, `backdrop_right`.
3. All 3 slots have `required: true`.
4. All slot names match `/^[a-z][a-z0-9_]*$/`.
5. `default_camera` is `'gentle_float'` and is in `compatible_cameras`.
6. `compatible_cameras` contains exactly 4 entries, all matching `/^[a-z][a-z0-9_]*$/`.
7. `fog` is `undefined` (not present).
8. `description` is non-empty.
9. `preferred_aspect` is `'landscape'`.

**Slot spatial correctness tests:**
10. `backdrop_left` rotation is `[0, Math.PI / 3, 0]`.
11. `backdrop_right` rotation is `[0, -Math.PI / 3, 0]`.
12. `backdrop_center` rotation is `[0, 0, 0]`.
13. All `size` components are > 0.
14. All 3 slots have identical size `[30, 28]`.
15. Panel height (28) >= visible height at distance 25 with FOV=50° (≈23.3).
16. Panel width (30) >= arc chord width for 60° at R=25 (≈28.87).

**Slot metadata tests:**
17. All 3 slots have `transparent: false`.
18. All 3 slots have `fogImmune: true`.
19. All 3 slots have `renderOrder: 0`.
20. All slot `description` fields are non-empty.
21. All optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly present (not `undefined`) on every slot.

**OBJ-005 validation integration test:**
22. `validateGeometryDefinition(panoramaGeometry)` returns an empty error array.
23. `registerGeometry(panoramaGeometry)` does not throw (when registry is not locked).
24. After registration, `getGeometry('panorama')` returns the panorama geometry.

**Compatible cameras tests:**
25. `compatible_cameras` includes `'static'`, `'lateral_track_left'`, `'lateral_track_right'`, `'gentle_float'`.
26. `compatible_cameras` does NOT include `'slow_push_forward'`, `'slow_pull_back'`, `'tunnel_push_forward'`, `'flyover_glide'`.

**Symmetry tests:**
27. `backdrop_left.position[0]` is the negation of `backdrop_right.position[0]`.
28. `backdrop_left.position[2]` equals `backdrop_right.position[2]`.
29. `backdrop_left.size` equals `backdrop_right.size`.
30. `backdrop_left.rotation[1]` is the negation of `backdrop_right.rotation[1]`.
31. All Y-positions are 0.

**Arc geometry tests:**
32. Side panel X-position ≈ `25 × sin(60°)` (±0.01 tolerance for truncation).
33. Side panel Z-position ≈ `5 - 25 × cos(60°)` = -7.5 (exact).
34. Center panel Z-position = `5 - 25` = -20 (exact).

### Relevant Testable Claims

- **TC-01** (partial): The panorama uses exactly 3 slots, all required — within the 3-5 range. This geometry handles "wide landscape panorama" and "environmental ambiance" scene types that other geometries don't naturally express.
- **TC-04** (partial): All spatial relationships defined by geometry. LLM specifies `geometry: 'panorama'` and maps images to slot names — no XYZ coordinates.
- **TC-08** (partial): The panorama covers pure-environment scene types (landscape surveys, cityscapes, astronomical views) distinct from all other geometries.

## Integration Points

### Depends on

| Upstream | What OBJ-024 imports |
|----------|---------------------|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types. `registerGeometry` function. |
| **OBJ-007** (Depth model) | Slot naming conventions (`SLOT_NAME_PATTERN`). `DEFAULT_SLOT_TAXONOMY` NOT used — panorama defines entirely custom slot names. |
| **OBJ-003** (Spatial math) | `Vec3`, `EulerRotation`, `Size2D` types. `DEFAULT_CAMERA` for camera position reference (arc center). `PLANE_ROTATIONS.FACING_CAMERA` for center panel rotation. |

### Consumed by

| Downstream | How it uses OBJ-024 |
|------------|---------------------|
| **OBJ-065** (Panorama visual tuning) | Director Agent reviews test renders; may adjust arc radius, panel sizes, spacing. |
| **OBJ-070** (End-to-end render test) | May use panorama as a test geometry. |
| **OBJ-071** (SKILL.md) | Documents panorama slot names, descriptions, usage guidance. Must note that panorama images should be visually continuous across panels. Prompt guidance derived from `PlaneSlot.description` fields. |
| **OBJ-017** (Manifest validation) | Looks up `getGeometry('panorama')` to validate manifest plane keys. Verifies all 3 required slots are present. |
| **OBJ-036** (Scene sequencer) | Resolves slot spatial data for panorama scenes. |
| **OBJ-039** (Page-side renderer) | Creates Three.js meshes from slot data. Side panel rotations (±π/3) must be correctly applied. |
| **OBJ-040** (Edge-reveal validation) | Validates camera paths don't reveal panel edges. Side panels at different Z distances require per-panel frustum checks. Rotated panels require non-trivial frustum intersection. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatible_cameras`. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        panorama.ts       # panoramaGeometry definition + registerGeometry() call
        index.ts          # Updated barrel export to include ./panorama
```

## Open Questions

### OQ-A: Rotation-based pan camera presets are missing from the DAG

The panorama's defining camera motion — horizontal rotation/panning — has no corresponding camera preset in the current DAG. OBJ-026-034 provide only translation-based and universal presets. Rotation-based presets (`pan_left`, `pan_right`, `slow_pan`) would:

- Keep the camera at a fixed position (arc center, [0, 0, 5])
- Rotate the lookAt target horizontally: `lookAt(t) = [R × sin(θ(t)), 0, 5 - R × cos(θ(t))]`
- Use ease_in_out for smooth pan feel

**Recommendation:** These presets should be defined as a new objective (or objectives) that depends on OBJ-006 and lists `panorama` in `compatibleGeometries`. Until then, `lateral_track_left/right` and `gentle_float` serve as functional substitutes. When pan presets are added, update `panoramaGeometry.default_camera` to the canonical pan preset and add them to `compatible_cameras`.

### OQ-B: Should the arc radius be configurable via the manifest?

The R=25 radius is hardcoded in the slot positions. An author might want a tighter (R=15, more intimate) or wider (R=35, more spacious) panorama. This could be supported via `position_override` in the manifest (AP-08), but overriding all 3 panel positions coherently requires understanding the arc math — which violates C-06 (blind-authorable).

**Recommendation:** Keep R=25 as the fixed default. If demand exists, add a `radius` parameter to the panorama's camera_params in a future objective, with the geometry auto-computing positions from the radius. This is beyond V1 scope.

### OQ-C: Should there be 5 panels for full 300° coverage?

Adding `backdrop_far_left` and `backdrop_far_right` at ±120° would extend coverage to 300° and allow near-360° panning. This would increase slot count to 5 (still within TC-01 range) but require 5 images per scene.

**Recommendation:** Defer. 180° coverage with 3 panels serves the vast majority of panoramic use cases. A 5-panel variant could be a separate geometry (`panorama_wide`) if demand exists.

### OQ-D: How should SKILL.md guide image creation for panorama panels?

Since the three panels are meant to form a continuous panoramic view, the images should have matching horizons, color temperature, and style at their edges. The SKILL.md should include specific guidance:
- Generate a single wide panoramic concept, then prompt for left/center/right segments
- Or generate three images with explicit edge-matching instructions
- Include guidance on which third of the scene goes in which panel

**Recommendation:** Address in OBJ-071 (SKILL.md). The `PlaneSlot.description` fields ("left third", "central portion", "right third") provide the initial guidance.

---

I believe this specification is complete and consistent with the patterns established by OBJ-018 (stage) and OBJ-022 (diorama). I'd like the Challenger to verify:

1. The arc geometry math (R=25, 60° spacing, positions derived from camera at [0,0,5])
2. The decision to make all 3 slots required (driven by horizontal FOV coverage analysis)
3. The fogImmune=true decision (driven by inter-panel distance discrepancy)
4. The compatible cameras list (only verified presets, noting the gap for rotation-based presets)
5. The absence of sky/ground/subject/foreground slots (structural enforcement of "pure environment")

Please review and let me know if any aspects need revision.

---

## Round 2 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 3 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 4 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 5 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 6 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 7 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 8 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 9 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 10 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 11 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 12 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 13 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 14 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 15 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 16 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 17 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 18 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 19 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 20 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 21 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 22 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 23 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 24 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 25 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 26 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 27 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 28 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 29 — spec_author

You've hit your limit · resets 1am (America/New_York)

---

## Round 30 — spec_challenger

You've hit your limit · resets 1am (America/New_York)

---

## Round 31 — spec_challenger

You've hit your limit · resets 1am (America/New_York)
