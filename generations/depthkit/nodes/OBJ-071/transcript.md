# Deliberation Transcript: OBJ-071

---

## Round 1 — spec_author

Looking at the objective metadata, dependencies, and the progress map, let me understand what OBJ-071 needs to deliver.

OBJ-070 (verified) established the document architecture and created:
- Full geometry section for `stage` 
- Stub sections for all other geometries
- Full camera sections for `slow_push_forward`, `slow_pull_back`, `static`, `gentle_float`
- Stub sections for all other cameras

OBJ-071 must expand those stubs into full sections for all **verified** geometries and cameras, and update the SKILL.md summary tables accordingly.

Let me check which upstream objectives are verified to determine scope:
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]

[Tool: ToolSearch]
  Input: {
  "query": "select:Glob",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Glob'}]


Let me check the existing SKILL.md files and the verified dependency specs I don't have inline.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-071/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-071/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-070/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "SKILL.md"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "docs/skill/*.md"
}
[Tool Result] No files found
SKILL.md doesn't exist yet — OBJ-070 is a spec, not implementation. Let me check the verified specs for the geometries and cameras I need to document but don't have inline:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-020/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-021/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md

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
  "pattern": "nodes/OBJ-028/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-029/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-030/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-031/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md
Good — all verified specs exist. Let me read the ones I need (the geometries and cameras not provided inline):
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "limit": 150
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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "limit": 150
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "limit": 150
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md",
  "limit": 150
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
  "limit": 150
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
Let me get the remaining data I need — the rest of the flyover, canyon, and the verified camera specs for completeness:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "offset": 148,
  "limit": 60
}
[Tool Result]    148→  expectsAlpha: false,
   149→}
   150→
   151→subject: {
   152→  // ... PlaneSlot fields from table above ...
   153→  name: 'subject',
   154→  promptGuidance: 'Focal element within the canyon — person, creature, vehicle, landmark. Isolated on transparent background. Scale should feel small relative to canyon walls.',
   155→  expectsAlpha: true,
   156→}
   157→```
   158→
   159→### Module Exports
   160→
   161→The module has no public exports beyond the side effect of calling `registerGeometry()` at import time. Consumers access the canyon geometry via `getGeometry('canyon')` from the OBJ-005 registry.
   162→
   163→```typescript
   164→// src/scenes/geometries/canyon.ts
   165→// No named exports — registration is the side effect
   166→
   167→import { registerGeometry } from './registry';
   168→// ... define canyonGeometry ...
   169→registerGeometry(canyonGeometry);
   170→```
   171→
   172→The geometry module must be imported (for its registration side effect) by ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": 148,
  "limit": 100
}
[Tool Result]    148→### Registration Side Effect
   149→
   150→```typescript
   151→// src/scenes/geometries/flyover.ts (bottom of file)
   152→
   153→import { registerGeometry } from './registry';
   154→
   155→// Self-registers when the module is imported.
   156→registerGeometry(flyoverGeometry);
   157→```
   158→
   159→### Module Exports
   160→
   161→```typescript
   162→// src/scenes/geometries/flyover.ts
   163→export { flyoverGeometry };
   164→```
   165→
   166→The barrel export `src/scenes/geometries/index.ts` must re-export from `./flyover` so that importing the geometries barrel triggers registration.
   167→
   168→## Design Decisions
   169→
   170→### D1: `ground` instead of `floor` — semantic distinction from the stage geometry
   171→
   172→The stage geometry uses a slot named `floor` — a horizontal surface that functions as a room floor or ground level at the base of a scene. The flyover geometry uses `ground` instead because the semantic role is different: this is a vast ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md",
  "limit": 100
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "limit": 100
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md",
  "limit": 100
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
Now let me get a bit more from OBJ-031 and OBJ-046 (CLI interface) for CLI flag reference:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-031/output.md",
  "offset": 100,
  "limit": 50
}
[Tool Result]    100→```
   101→startPosition = [0, 0, 5]
   102→startLookAt   = [0, 0, 0]
   103→fov           = 50  (static, no animation)
   104→```
   105→
   106→These match the Three.js camera defaults from Seed Section 8.1–8.2. The gentle_float is geometry-agnostic — geometries place planes relative to the camera's start position, so the default `[0, 0, 5]` works universally.
   107→
   108→### Preset Definition (Static Fields)
   109→
   110→```typescript
   111→{
   112→  name: 'gentle_float',
   113→
   114→  description: 'Very slow, subtle drift in all three axes. Almost subliminal. ' +
   115→    'Creates a sense of life without drawing attention to camera movement. ' +
   116→    'Good for ambient scenes, close-ups, and any geometry where stillness ' +
   117→    'would feel lifeless.',
   118→
   119→  // evaluate: <implementation per motion model above>
   120→
   121→  defaultStartState: {
   122→    position: [0, 0, 5],
   123→    lookAt: [0, 0, 0],
   124→    fov: 50,
   125→  },
 ... [truncated]
Good. I now have sufficient data from all verified dependencies. Let me compose the specification.

---

Here is my proposed specification for OBJ-071:

---

# Specification: OBJ-071 — SKILL.md Geometry and Camera Reference Sections

## Summary

OBJ-071 fills in the geometry and camera reference sub-files (`docs/skill/geometry-reference.md` and `docs/skill/camera-reference.md`) created as scaffolding by OBJ-070. OBJ-070 established the document architecture and provided a full section for the `stage` geometry and full sections for `slow_push_forward`, `slow_pull_back`, `static`, and `gentle_float` cameras, with stub sections for everything else. OBJ-071 expands stubs to full sections for all verified geometries (`tunnel`, `canyon`, `flyover`) and all verified camera presets (`lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, `flyover_glide`), updates the SKILL.md summary tables to reflect the new content, and updates the complete annotated example in SKILL.md to use at least one newly-documented geometry. Stub sections remain for unverified geometries and cameras. This objective is the primary blocker for OBJ-056 (manifest generation via Claude API), which requires comprehensive reference documentation for LLM-driven authoring.

## Interface Contract

OBJ-071 is a documentation objective. Its "interface" is the content structure of Markdown files. No TypeScript code is produced.

### Files Modified

| File | Action | Content Added |
|------|--------|---------------|
| `docs/skill/geometry-reference.md` | Modify | Full sections for `tunnel`, `canyon`, `flyover`. Update stubs for `diorama`, `portal`, `panorama`, `close_up` with verified slot names where available. |
| `docs/skill/camera-reference.md` | Modify | Full sections for `lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, `flyover_glide`. Update stubs for `dramatic_push`, `crane_up`, `dolly_zoom` with seed descriptions. |
| `SKILL.md` | Modify | Update geometry summary table (rows for tunnel, canyon, flyover now include required slots and compatible cameras). Update camera summary table (rows for newly documented cameras). Optionally update the complete annotated example to use a verified geometry beyond `stage`. |

### Geometry Full Section Template

Each full geometry section follows the pattern established by OBJ-070 AC-23 for `stage`. The structure is:

```markdown
### `{geometry_name}`

**Description:** [From the verified geometry spec's `description` field]

**When to use:** [Authoring guidance — what kinds of scenes/topics suit this geometry. Derived from the geometry spec's description and design rationale.]

**Required slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `{slot_name}` | [From slot's `description` field] | [Derived from slot guidance export or PlaneSlot description + transparency requirements] |

**Optional slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `{slot_name}` | [From slot's `description` field] | [Same derivation] |

**Default camera:** `{default_camera}`

**Compatible cameras:** [List from geometry spec's `compatible_cameras`]

**Fog:** [Color, near, far from geometry spec. Plain-English description of the fog's visual effect.]

**Transparency:** [Which slots require transparent background images, matching `transparent: true` slots]

**Aspect ratio:** [From `preferred_aspect`. Guidance on landscape vs portrait suitability.]

**Tips:**
- [Authoring tips specific to this geometry — what makes it look good, common mistakes]
```

### Camera Full Section Template

Each full camera section follows the pattern established by OBJ-070 AC-29 for `slow_push_forward`. The structure is:

```markdown
### `{camera_name}`

**Motion:** [1-2 sentence motion description from the camera spec]

**Feel:** [Qualitative description of the cinematic feel — how it reads emotionally/visually]

**When to use:** [Authoring guidance — what kinds of scenes/moments suit this camera]

**Compatible geometries:** [List from camera spec's `compatibleGeometries`]

**Parameters:**
| Param | Default | Effect |
|-------|---------|--------|
| `speed` | `1.0` | [Effect description specific to this preset] |
| `easing` | `{defaultEasing}` | [Effect description] |

**Notes:**
- [Usage notes, cautions, interaction with specific geometries]
```

### Geometry Summary Table Update (in SKILL.md)

The summary table in the primary SKILL.md (per OBJ-070 AC-13) must be updated so that rows for `tunnel`, `canyon`, and `flyover` include accurate data sourced from their verified specs. Specifically:

| Geometry | Required Slots | Default Camera | When to Use |
|----------|---------------|----------------|-------------|
| `stage` | `backdrop`, `floor`, `subject` | `slow_push_forward` | *(existing from OBJ-070)* |
| `tunnel` | `floor`, `left_wall`, `right_wall`, `end_wall` | `tunnel_push_forward` | Corridors, hallways, enclosed passages |
| `canyon` | `sky`, `left_wall`, `right_wall`, `floor` | `slow_push_forward` | Gorges, alleys, narrow dramatic spaces |
| `flyover` | `sky`, `ground` | `slow_push_forward` | Landscapes, aerial views, travel themes |
| `diorama` | *(TBD — not verified)* | *(TBD)* | Paper-theater layered scenes |
| `portal` | *(TBD — not verified)* | *(TBD)* | Concentric frames, dreamlike sequences |
| `panorama` | *(TBD — not verified)* | *(TBD)* | Wide environments with camera pan |
| `close_up` | *(TBD — not verified)* | *(TBD)* | Tight focus, minimal background |

### Camera Summary Table Update (in SKILL.md)

The camera summary table (per OBJ-070 AC-14) must be updated with rows for newly documented cameras:

| Camera | Motion Type | Compatible Geometries | When to Use |
|--------|------------|----------------------|-------------|
| *(existing OBJ-070 entries for static, slow_push_forward, slow_pull_back, gentle_float)* | | | |
| `lateral_track_left` | Horizontal slide left | stage, canyon, diorama, portal, panorama | Tracking shots, revealing lateral depth |
| `lateral_track_right` | Horizontal slide right | stage, canyon, diorama, portal, panorama | Mirror of lateral_track_left |
| `tunnel_push_forward` | Deep Z-axis push | tunnel | Traveling through enclosed spaces |
| `flyover_glide` | Elevated forward glide | flyover | Aerial/bird's-eye establishing shots |
| `dramatic_push` | *(stub — details pending)* | *(TBD)* | Emphasis, tension |
| `crane_up` | *(stub — details pending)* | *(TBD)* | Vertical reveals |
| `dolly_zoom` | *(stub — details pending)* | *(TBD)* | Dramatic Hitchcock effect |

## Design Decisions

### D1: Scope — Full Sections Only for Verified Objectives

**Decision:** Full sections are written only for geometries and cameras whose defining objectives are verified in the progress map. Unverified objectives retain stub sections.

**Verified geometries for full sections:** `tunnel` (OBJ-019), `canyon` (OBJ-020), `flyover` (OBJ-021). Stage already has a full section from OBJ-070.

**Verified cameras for full sections:** `lateral_track_left` and `lateral_track_right` (OBJ-028), `tunnel_push_forward` (OBJ-029), `flyover_glide` (OBJ-030). Static, slow_push_forward, slow_pull_back, and gentle_float already have full sections from OBJ-070.

**Stub-only geometries:** `diorama` (OBJ-022, open), `portal` (OBJ-023, open), `panorama` (OBJ-024, open), `close_up` (OBJ-025, open).

**Stub-only cameras:** `dramatic_push` (OBJ-032, open), `crane_up` (OBJ-033, open), `dolly_zoom` (OBJ-034, open).

**Rationale:** Writing full documentation for unverified objectives would require speculating about slot names, spatial parameters, and compatible cameras that don't yet exist in code. This violates the seed's principle that documentation must match implementation. Stubs clearly mark "details pending" and prevent the LLM from attempting to use undocumented features.

### D2: Image Guidance Sourced from Multiple Places

**Decision:** Per-slot image guidance is sourced from:
1. **Tunnel:** The `tunnelSlotGuidance` companion export defined in OBJ-019.
2. **Canyon:** The `DepthSlot` metadata (`promptGuidance`, `expectsAlpha`) defined inline in OBJ-020.
3. **Flyover:** The `PlaneSlot.description` field plus transparency flags, since OBJ-021 follows OBJ-018's pattern of not exporting a separate guidance object (per OBJ-021 D11). The implementer must derive image guidance from slot descriptions, transparency flags, and the geometry's description.

**Rationale:** There is no single unified mechanism for prompt guidance across all geometries. OBJ-019 introduced a `tunnelSlotGuidance` companion export. OBJ-020 merged DepthSlot metadata into the slot objects. OBJ-021 defers guidance to SKILL.md. The implementer must handle all three patterns. This is documented here so the implementer knows where to look for each geometry.

### D3: Tunnel Documentation Notes `preferred_aspect: 'landscape'`

**Decision:** The tunnel and canyon geometry sections include an "Aspect ratio" note recommending landscape orientation, and the flyover section does likewise. This follows the `preferred_aspect` field from each verified spec.

**Rationale:** OBJ-005 defines `preferred_aspect` as advisory guidance for SKILL.md. Surfacing it in the geometry reference helps LLMs make orientation decisions.

### D4: Camera Sections Document Speed Scaling Behavior per Preset

**Decision:** Each camera section's `speed` parameter description is specific to that preset, not generic. For example:
- `tunnel_push_forward`: "Scales Z displacement. speed=0.5 → 12.5-unit push. speed=2.0 → 50-unit push."
- `lateral_track_left`: "Scales X displacement. speed=0.5 → 3-unit track. speed=2.0 → 12-unit track."
- `flyover_glide`: "Scales Z displacement. Y elevation and viewing angle are unaffected."

**Rationale:** Per OBJ-006 D3, speed scales "spatial amplitude" but the meaning varies per preset. Generic documentation like "scales the motion" doesn't help an LLM predict the visual result.

### D5: Complete Annotated Example May Be Updated to Include Tunnel or Canyon

**Decision:** The complete annotated example in SKILL.md (OBJ-070 AC-10) may be updated to use `tunnel` or `canyon` as one of its scenes, demonstrating that an LLM can use multiple geometries in a single manifest. If updated, the example must remain valid JSON that passes `loadManifest()` with all referenced geometries and cameras registered.

**Rationale:** OBJ-070 AC-10 says the example "MAY use verified geometries beyond stage." OBJ-071 provides the documented reference that makes such usage meaningful. Including a tunnel or canyon scene in the example demonstrates geometry diversity and gives the LLM a concrete multi-geometry authoring pattern.

### D6: Stub Sections Updated with Known Data from Seed

**Decision:** Stub sections for unverified geometries are updated to include any data available from the seed (Section 4.2 descriptions) but continue to mark slot names and compatible cameras as "TBD" unless the geometry happens to appear in a verified camera's `compatibleGeometries` list.

For example, `diorama` appears in the `compatibleGeometries` of `lateral_track_left` (OBJ-028), `slow_push_forward` (OBJ-027), `gentle_float` (OBJ-031), and `static` (OBJ-026). The stub can note these known compatible cameras even though the geometry itself is not verified. However, slot names remain "TBD" since no verified spec defines them.

**Rationale:** Cross-referencing verified camera specs gives stubs more useful content without speculating about unverified geometry definitions.

### D7: Content is Manually Authored, Not Auto-Generated

**Decision:** Carried forward from OBJ-070 D8. All content is authored by the implementer for pedagogical clarity, not generated from registry data. Content must be **consistent** with the verified specs (acceptance criteria verify this) but the prose is crafted for LLM readability.

### D8: Combined Size Budget Remains Under 2000 Lines / 60KB

**Decision:** OBJ-071 adds substantial content (3 full geometry sections, 4 full camera sections). The implementer must ensure the combined total of SKILL.md + all sub-files stays under the 2000-line / 60KB target from OBJ-070 AC-48.

**Rationale:** SC-04 requires the document to fit within a single LLM context window alongside system prompts and conversation. Each full geometry section is approximately 40-60 lines; each full camera section is approximately 25-35 lines. The additions total roughly 250-350 lines, which should fit within the budget if the existing content from OBJ-070 is approximately 700-900 lines.

## Acceptance Criteria

### Geometry Reference Sub-File (`docs/skill/geometry-reference.md`)

#### Tunnel Geometry — Full Section

- [ ] **AC-01:** Contains a full section for `tunnel` with the section structure defined in the Interface Contract (description, when to use, required slots table, optional slots table, default camera, compatible cameras, fog, transparency, aspect ratio, tips).
- [ ] **AC-02:** Tunnel required slots listed as: `floor`, `left_wall`, `right_wall`, `end_wall` — matching OBJ-019 exactly.
- [ ] **AC-03:** Tunnel optional slot listed as: `ceiling` — matching OBJ-019 exactly.
- [ ] **AC-04:** Tunnel default camera documented as `tunnel_push_forward` — matching OBJ-019.
- [ ] **AC-05:** Tunnel compatible cameras listed as: `tunnel_push_forward`, `slow_push_forward`, `static`, `gentle_float` — matching OBJ-019 exactly.
- [ ] **AC-06:** Tunnel fog documented as: color `#000000`, near `15`, far `50` — matching OBJ-019.
- [ ] **AC-07:** Tunnel `preferred_aspect` documented as `landscape`.
- [ ] **AC-08:** Tunnel transparency note states that all slots use opaque images (no slot has `transparent: true` in OBJ-019).
- [ ] **AC-09:** Tunnel image guidance per slot is sourced from `tunnelSlotGuidance` (OBJ-019's companion export) and accurately reflects `promptGuidance` content for each slot.

#### Canyon Geometry — Full Section

- [ ] **AC-10:** Contains a full section for `canyon` with the section structure defined in the Interface Contract.
- [ ] **AC-11:** Canyon required slots listed as: `sky`, `left_wall`, `right_wall`, `floor` — matching OBJ-020.
- [ ] **AC-12:** Canyon optional slots listed as: `end_wall`, `subject` — matching OBJ-020.
- [ ] **AC-13:** Canyon default camera documented as `slow_push_forward` — matching OBJ-020.
- [ ] **AC-14:** Canyon compatible cameras listed as: `slow_push_forward`, `crane_up`, `dramatic_push`, `gentle_float`, `static` — matching OBJ-020.
- [ ] **AC-15:** Canyon fog documented as: color `#1a1a2e`, near `15`, far `48` — matching OBJ-020.
- [ ] **AC-16:** Canyon `preferred_aspect` documented as `landscape`.
- [ ] **AC-17:** Canyon transparency note states that `subject` requires transparent background. All other slots are opaque.
- [ ] **AC-18:** Canyon image guidance per slot is sourced from OBJ-020's inline DepthSlot metadata (`promptGuidance` fields).

#### Flyover Geometry — Full Section

- [ ] **AC-19:** Contains a full section for `flyover` with the section structure defined in the Interface Contract.
- [ ] **AC-20:** Flyover required slots listed as: `sky`, `ground` — matching OBJ-021.
- [ ] **AC-21:** Flyover optional slots listed as: `landmark_far`, `landmark_left`, `landmark_right`, `near_fg` — matching OBJ-021.
- [ ] **AC-22:** Flyover slot named `ground` (not `floor`) — matching OBJ-021 D1.
- [ ] **AC-23:** Flyover default camera documented as `slow_push_forward` — matching OBJ-021 (with a note that `flyover_glide` is the intended future default).
- [ ] **AC-24:** Flyover compatible cameras listed as: `static`, `flyover_glide`, `slow_push_forward`, `slow_pull_back`, `gentle_float` — matching OBJ-021.
- [ ] **AC-25:** Flyover fog documented as: color `#b8c6d4`, near `20`, far `55` — matching OBJ-021.
- [ ] **AC-26:** Flyover `preferred_aspect` documented as `landscape`.
- [ ] **AC-27:** Flyover transparency note states that `landmark_far`, `landmark_left`, `landmark_right`, and `near_fg` require transparent backgrounds. `sky` and `ground` are opaque.
- [ ] **AC-28:** Flyover image guidance derived from OBJ-021 slot descriptions and OBJ-021 D11 guidance note.

#### Stub Sections — Updated

- [ ] **AC-29:** Stub sections exist for `diorama`, `portal`, `panorama`, `close_up`. Each retains the stub structure from OBJ-070 AC-28 (heading, status note, description, slot names as TBD or listed if inferable, default camera as TBD).
- [ ] **AC-30:** Stub descriptions match seed Section 4.2 for each geometry.

### Camera Reference Sub-File (`docs/skill/camera-reference.md`)

#### Lateral Track Cameras — Full Sections

- [ ] **AC-31:** Contains full sections for both `lateral_track_left` and `lateral_track_right` following the camera section template.
- [ ] **AC-32:** Lateral track compatible geometries listed as: `stage`, `canyon`, `diorama`, `portal`, `panorama` — matching OBJ-028.
- [ ] **AC-33:** Lateral track default easing documented as `ease_in_out` — matching OBJ-028.
- [ ] **AC-34:** Speed parameter documented as scaling X-axis displacement. Default 1.0 = 6 units of horizontal travel.
- [ ] **AC-35:** Motion descriptions note that the camera slides horizontally while looking slightly ahead of travel direction, and that background planes move in the opposite direction while foreground planes move faster.

#### Tunnel Push Forward — Full Section

- [ ] **AC-36:** Contains a full section for `tunnel_push_forward` following the camera section template.
- [ ] **AC-37:** Tunnel push forward compatible geometries listed as: `tunnel` — matching OBJ-029 (tunnel-only preset).
- [ ] **AC-38:** Default easing documented as `ease_in_out_cubic` — matching OBJ-029.
- [ ] **AC-39:** Speed parameter documented as scaling Z displacement. Default 1.0 = 25 units of Z travel. speed=0.5 → 12.5 units.
- [ ] **AC-40:** Motion description notes the deep Z-axis push, the subtle Y-axis rise, and the wall convergence toward a vanishing point.

#### Flyover Glide — Full Section

- [ ] **AC-41:** Contains a full section for `flyover_glide` following the camera section template.
- [ ] **AC-42:** Flyover glide compatible geometries listed as: `flyover` — matching OBJ-030.
- [ ] **AC-43:** Default easing documented as `ease_in_out` — matching OBJ-030.
- [ ] **AC-44:** Speed parameter documented as scaling Z displacement only; camera elevation (Y) is constant. Default 1.0 = 30 units of Z travel.
- [ ] **AC-45:** Motion description notes the elevated camera position, constant downward viewing angle (~34° below horizontal), and the co-moving lookAt that maintains consistent aerial perspective.

#### Stub Sections — Updated

- [ ] **AC-46:** Stub sections exist for `dramatic_push`, `crane_up`, `dolly_zoom`. Each has heading, status note, and 1-sentence motion description from seed Section 4.3.
- [ ] **AC-47:** Stubs for `dramatic_push` and `crane_up` note they appear in the canyon's `compatible_cameras` list (from OBJ-020) as forward references.

### Primary File (`SKILL.md`) Updates

- [ ] **AC-48:** The geometry summary table includes rows for `tunnel`, `canyon`, and `flyover` with accurate required slots, default camera, and "when to use" text.
- [ ] **AC-49:** The camera summary table includes rows for `lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, and `flyover_glide` with accurate compatible geometries and "when to use" text.
- [ ] **AC-50:** If the complete annotated example is updated to include a non-`stage` geometry, the example remains valid JSON that passes `loadManifest()` when all referenced geometries and cameras are registered.

### Cross-Consistency

- [ ] **AC-51:** All geometry slot names in geometry-reference.md match the verified specs exactly (e.g., flyover uses `ground` not `floor`, canyon uses `sky` not `ceiling`).
- [ ] **AC-52:** All camera preset names match registered names (e.g., `tunnel_push_forward` not `tunnel_push`, `flyover_glide` not `flyover_push`).
- [ ] **AC-53:** All compatible cameras listed for each geometry match the geometry spec's `compatible_cameras` field exactly.
- [ ] **AC-54:** All compatible geometries listed for each camera match the camera spec's `compatibleGeometries` field exactly.
- [ ] **AC-55:** All easing names referenced match OBJ-004's enum: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`.
- [ ] **AC-56:** The vocabulary used throughout matches seed Section 2 definitions (plane not layer, scene geometry not layout template, etc.).
- [ ] **AC-57:** Fog colors in documentation match exact hex values from geometry specs (e.g., canyon fog is `#1a1a2e`, not "dark blue-gray").

### Size Budget

- [ ] **AC-58:** The total combined size of `SKILL.md` + all sub-files remains under 2000 lines / 60KB (per OBJ-070 AC-48).

## Edge Cases and Error Handling

OBJ-071 is a documentation artifact. "Edge cases" are authoring scenarios the new content must address.

### Authoring Scenarios the New Content Must Cover

| Scenario | How the Documentation Handles It |
|----------|----------------------------------|
| LLM uses `floor` slot name with flyover geometry | Flyover geometry section explicitly notes the slot is named `ground`, not `floor`. The slot table makes this unambiguous. Tips section warns: "The flyover's ground slot is named `ground`, not `floor` — do not confuse with the stage or tunnel `floor` slot." |
| LLM uses `tunnel_push_forward` camera with stage geometry | Camera section for `tunnel_push_forward` explicitly lists compatible geometries as `tunnel` only. Stage section lists its compatible cameras — `tunnel_push_forward` is not among them. |
| LLM uses `lateral_track_left` with tunnel geometry | Camera section explicitly lists excluded geometries. Tunnel geometry section lists its compatible cameras — lateral tracks are not among them. |
| LLM uses a stub geometry (e.g., `diorama`) | Stub section has a clear status note: "Details pending." The LLM should be able to determine that slot names are not yet available and choose a documented geometry instead. |
| LLM wants canyon with a subject element | Canyon's optional `subject` slot is documented in the full section with transparency requirements and image guidance. |
| LLM wants flyover without landmarks | Flyover section shows only `sky` and `ground` as required. Tips note: "A valid flyover needs only two images — a ground texture and a sky backdrop." |
| LLM wants tunnel without ceiling | Tunnel section marks `ceiling` as optional with description: "Omit for open-air passages." |
| LLM confuses canyon with tunnel | Both sections include a "When to use" that distinguishes them: canyon has open sky above, tunnel is fully enclosed (or open-ceiling variant). Tips in each section reference the other for comparison. |
| LLM uses `flyover_glide` as default camera for flyover | Flyover section notes that `slow_push_forward` is the current default camera and `flyover_glide` is the intended future default. Both are in the compatible list. Either works. |

### Document Maintenance Considerations

| Scenario | Handling |
|----------|----------|
| OBJ-022 (portal) is verified after OBJ-071 | Replace the portal stub in geometry-reference.md with a full section using OBJ-022's verified data. Update the summary table in SKILL.md. This is a follow-on change, not OBJ-071's responsibility. |
| Visual tuning (OBJ-059–OBJ-066) changes slot positions/sizes | Positions and sizes are NOT documented in SKILL.md (LLMs don't need them — they use slot names, not coordinates). Fog colors, compatible cameras, and slot names ARE documented and must be updated if tuning changes them. |
| Camera compatibility list updated after tuning | Update both geometry-reference.md (geometry's compatible cameras) and camera-reference.md (camera's compatible geometries). Verify bidirectional consistency. |

## Test Strategy

### Implementer Tests (run before marking objective complete)

**1. Slot Name Cross-Check — Tunnel:**
Verify that the documented required and optional slot names for `tunnel` match OBJ-019's `tunnelGeometry.slots` exactly. Required: `floor`, `left_wall`, `right_wall`, `end_wall`. Optional: `ceiling`.

**2. Slot Name Cross-Check — Canyon:**
Verify that the documented slots for `canyon` match OBJ-020. Required: `sky`, `left_wall`, `right_wall`, `floor`. Optional: `end_wall`, `subject`.

**3. Slot Name Cross-Check — Flyover:**
Verify that the documented slots for `flyover` match OBJ-021. Required: `sky`, `ground`. Optional: `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`. Confirm the slot is named `ground` not `floor`.

**4. Camera Compatibility Cross-Check — Tunnel:**
Verify tunnel's documented compatible cameras match OBJ-019's `compatible_cameras`: `tunnel_push_forward`, `slow_push_forward`, `static`, `gentle_float`.

**5. Camera Compatibility Cross-Check — Canyon:**
Verify canyon's documented compatible cameras match OBJ-020's `compatible_cameras`: `slow_push_forward`, `crane_up`, `dramatic_push`, `gentle_float`, `static`.

**6. Camera Compatibility Cross-Check — Flyover:**
Verify flyover's documented compatible cameras match OBJ-021's `compatible_cameras`: `static`, `flyover_glide`, `slow_push_forward`, `slow_pull_back`, `gentle_float`.

**7. Camera Compatible Geometries Cross-Check — Lateral Tracks:**
Verify `lateral_track_left`/`lateral_track_right` documented compatible geometries match OBJ-028: `stage`, `canyon`, `diorama`, `portal`, `panorama`.

**8. Camera Compatible Geometries Cross-Check — Tunnel Push:**
Verify `tunnel_push_forward` documented compatible geometries match OBJ-029: `tunnel` only.

**9. Camera Compatible Geometries Cross-Check — Flyover Glide:**
Verify `flyover_glide` documented compatible geometries match OBJ-030: `flyover` only.

**10. Bidirectional Compatibility Verification:**
For every geometry-camera pairing documented: verify the camera appears in the geometry's compatible list AND the geometry appears in the camera's compatible list. Flag any one-directional entries. Known exceptions: `crane_up` and `dramatic_push` appear in canyon's compatible list but are stub cameras — document this asymmetry without treating it as an error.

**11. Fog Value Cross-Check:**
- Tunnel fog: `#000000`, near=15, far=50 (OBJ-019)
- Canyon fog: `#1a1a2e`, near=15, far=48 (OBJ-020)
- Flyover fog: `#b8c6d4`, near=20, far=55 (OBJ-021)

**12. Easing Cross-Check:**
- `tunnel_push_forward` default easing: `ease_in_out_cubic` (OBJ-029)
- `lateral_track_left/right` default easing: `ease_in_out` (OBJ-028)
- `flyover_glide` default easing: `ease_in_out` (OBJ-030)

**13. Vocabulary Check:**
Search all modified files for vocabulary violations: "layer" (should be "plane"), "layout template" (should be "scene geometry"), "z-level" (should be "depth slot").

**14. Size Budget Check:**
Count total lines across SKILL.md + all sub-files. Verify under 2000 lines / 60KB.

**15. Complete Example Validation (if updated):**
If the complete annotated example is updated to include a non-`stage` geometry, extract the JSON, register all referenced geometries and cameras, and run through `loadManifest()`. Must return `success: true` with zero errors.

### Relevant Testable Claims

- **TC-04:** The expanded geometry reference enables LLMs to author valid manifests for tunnel, canyon, and flyover scenes using only slot names — no XYZ coordinates.
- **TC-07:** The documented compatible cameras and slot names match implementation, ensuring validation catches common errors the LLM might make.
- **TC-08:** With 4 fully documented geometries (stage, tunnel, canyon, flyover) plus 4 stubs, tests 13-15 and 17 verify that documentation coverage tracks geometry availability.
- **SC-02:** The expanded SKILL.md enables the 5-topic blind authoring test to use diverse geometries beyond just `stage`.
- **SC-04:** OBJ-071 is the primary content expansion that makes SKILL.md comprehensive enough for self-sufficient authoring.

## Integration Points

### Depends On

| Dependency | What OBJ-071 Uses |
|---|---|
| **OBJ-070** (SKILL.md structure) | Document architecture, existing full sections (stage geometry, 4 camera presets), summary table structure, size budget, section templates. OBJ-071 follows OBJ-070's established patterns exactly. |
| **OBJ-005** (Geometry type contract) | `SceneGeometry` interface structure — informs what fields to document (slots, compatible_cameras, default_camera, fog, preferred_aspect, description). |
| **OBJ-006** (Camera path type contract) | `CameraPathPreset` interface structure — informs what fields to document (name, description, compatibleGeometries, defaultEasing, oversizeRequirements, tags). `CameraParams` fields (speed, easing, offset) documented in parameter tables. |
| **OBJ-018** (Stage geometry) | Verified. Already documented by OBJ-070. OBJ-071 does not modify the stage section but cross-references it. |
| **OBJ-019** (Tunnel geometry) | Verified. Source for tunnel full section: slot names, descriptions, rotations, required/optional flags, compatible cameras, fog, preferred_aspect, description. `tunnelSlotGuidance` companion export for image guidance. |

**Non-dependency verified objectives consulted for content:**

| Objective | What OBJ-071 Uses |
|---|---|
| **OBJ-020** (Canyon geometry, verified) | Source for canyon full section: slot names, required/optional, compatible cameras, fog, preferred_aspect, description, inline DepthSlot `promptGuidance`. |
| **OBJ-021** (Flyover geometry, verified) | Source for flyover full section: slot names (including custom `ground`), required/optional, compatible cameras, fog, preferred_aspect, description. |
| **OBJ-026** (Static camera, verified) | Already documented by OBJ-070. Cross-referenced for compatibility lists. |
| **OBJ-027** (Push/pull cameras, verified) | Already documented by OBJ-070. Cross-referenced for compatibility lists. |
| **OBJ-028** (Lateral track cameras, verified) | Source for lateral track full sections: motion model, compatible geometries, default easing, speed scaling, description. |
| **OBJ-029** (Tunnel push forward, verified) | Source for tunnel push full section: motion model, compatible geometries, default easing, speed scaling, Y-axis rise, description. |
| **OBJ-030** (Flyover glide, verified) | Source for flyover glide full section: motion model, compatible geometries, default easing, speed scaling, elevation, viewing angle, description. |
| **OBJ-031** (Gentle float, verified) | Already documented by OBJ-070. Cross-referenced for compatibility lists. |

### Consumed By

| Downstream | How It Uses OBJ-071 |
|---|---|
| **OBJ-056** (Manifest generation via Claude API) | Depends on OBJ-071 for comprehensive geometry and camera documentation that enables the Claude API to generate valid manifests using diverse geometries. This is the primary blocker relationship. |
| **OBJ-059–OBJ-066** (Visual tuning) | If visual tuning changes compatible cameras or fog settings, the corresponding sections in geometry-reference.md and camera-reference.md must be updated. OBJ-071 establishes the content that tuning may revise. |
| **SC-02** (Blind authoring validation) | Uses SKILL.md + sub-files as the sole reference. OBJ-071's expanded content enables authoring beyond `stage`-only manifests. |
| **SC-04** (SKILL.md self-sufficiency) | OBJ-071 is the primary content expansion needed for the self-sufficiency criterion. |

### File Placement

```
depthkit/
  SKILL.md                              # MODIFIED: summary tables updated
  docs/
    skill/
      geometry-reference.md             # MODIFIED: tunnel, canyon, flyover full sections added
      camera-reference.md               # MODIFIED: lateral tracks, tunnel push, flyover glide full sections added
```

No new files are created. OBJ-071 modifies files created by OBJ-070's implementation.

## Open Questions

### OQ-A: Should Geometry Sections Include Spatial Diagrams?

Carried forward from OBJ-070 OQ-B. ASCII art diagrams showing tunnel cross-section or canyon wall arrangement could help human readers. LLMs may not reliably interpret ASCII art. **Recommendation:** Use plain-English spatial descriptions (e.g., "Two tall walls on left and right with a floor between them and open sky above"). If human readers request diagrams, they can be added as a follow-on enhancement.

### OQ-B: Should Camera Sections Document the offset Parameter?

The `offset` parameter (from `CameraParams`) is universal across all cameras — it's applied post-evaluate by the renderer (OBJ-006 D2). OBJ-070's camera sections document `speed` and `easing` per-preset. Should each camera section also document `offset`? **Recommendation:** Document `offset` once in the primary SKILL.md (in the camera summary or the scene authoring workflow) rather than repeating it in every camera section. Note: OBJ-070 may already cover this in the manifest-schema-reference.md under `camera_params`.

### OQ-C: Canyon Lists `crane_up` and `dramatic_push` as Compatible but These Are Stub Cameras

Canyon's `compatible_cameras` (OBJ-020) includes `crane_up` and `dramatic_push`, which are unverified (OBJ-032, OBJ-033 are open). The canyon full section must list them as compatible, but the camera-reference.md only has stubs for these presets. **Recommendation:** List them in the canyon section with a note: "See camera reference — details pending for `crane_up` and `dramatic_push`." This is accurate and prevents the LLM from being surprised by an "incompatible camera" validation error when using these (since the engine will accept them if they're registered).

---

I believe this spec is comprehensive and internally consistent. I'd like the Challenger to verify the following key aspects:

1. **Scope boundaries** — Is it clear which geometries/cameras get full sections vs stubs?
2. **Data sourcing** — Are the references to specific fields in OBJ-019, OBJ-020, OBJ-021, OBJ-028, OBJ-029, OBJ-030 accurate and complete?
3. **Acceptance criteria** — Are the cross-check criteria sufficient to ensure consistency without being redundant with OBJ-070's existing criteria?
4. **Size budget** — Is the 2000-line target realistic with the added content?

---

## Round 2 — spec_challenger

Let me verify the key claims in the spec against the actual dependency data.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "offset": "0",
  "limit": "250"
}
[Tool Result]      0→# Specification: Canyon Scene Geometry (OBJ-020)
     1→
     2→## Summary
     3→
     4→OBJ-020 defines the **canyon** scene geometry — a narrow, vertically dramatic 3D space with tall wall planes on left and right, a floor plane, an open sky above, and an optional end wall at depth. The camera pushes forward through the canyon or floats upward to reveal vertical scale. This geometry produces the feeling of traveling through a narrow gorge, alley, corridor between tall buildings, or any space defined by towering vertical boundaries. It registers itself via `registerGeometry()` from OBJ-005 and defines its slot set per OBJ-007's depth model contract.
     5→
     6→## Interface Contract
     7→
     8→### Geometry Definition
     9→
    10→```typescript
    11→// src/scenes/geometries/canyon.ts
    12→
    13→import type { SceneGeometry, PlaneSlot, FogConfig } from './types';
    14→import { registerGeometry } from './registry';
    15→```
    16→
    17→The module defines and ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": "0",
  "limit": "250"
}
[Tool Result]      0→# Specification: Flyover Scene Geometry (OBJ-021)
     1→
     2→## Summary
     3→
     4→OBJ-021 defines the **flyover** scene geometry — a spatial arrangement designed for aerial/bird's-eye perspective. A large ground plane lies below the camera (`FLOOR` rotation), a sky plane sits at extreme depth above, and optional landmark planes rise vertically from the ground at varying depths and lateral positions. The camera moves forward while positioned above the ground, producing an immersive "flying over terrain" effect where the ground plane undergoes strong perspective foreshortening and landmarks pass by on either side. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.
     5→
     6→## Interface Contract
     7→
     8→### Exported Geometry Definition
     9→
    10→```typescript
    11→// src/scenes/geometries/flyover.ts
    12→
    13→import type { SceneGeometry } from './types';
    14→
    15→/**
    16→ * The flyover scene geometr... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "offset": "0",
  "limit": "250"
}
[Tool Result]      0→# Specification: OBJ-028 — Lateral Track Camera Path Presets
     1→
     2→## Summary
     3→
     4→OBJ-028 defines two camera path presets — `lateral_track_left` and `lateral_track_right` — that translate the camera along the X-axis to produce cinematic tracking shots. The camera slides horizontally while looking slightly ahead of its travel direction, creating the classic dolly-track effect where foreground planes move faster than background planes due to perspective projection. These presets conform to the `CameraPathPreset` contract from OBJ-006 and require significant X-axis plane oversizing to prevent edge reveals.
     5→
     6→## Interface Contract
     7→
     8→### Preset Definitions
     9→
    10→```typescript
    11→// src/camera/presets/lateral_track.ts
    12→
    13→import { CameraPathPreset } from '../types';
    14→
    15→/**
    16→ * Camera translates along the NEGATIVE X-axis (right to left in screen space).
    17→ * The camera starts at a positive X of... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md",
  "offset": "0",
  "limit": "120"
}
[Tool Result]      0→# Specification: OBJ-029 — Tunnel Push Forward Camera Path Preset
     1→
     2→## Summary
     3→
     4→OBJ-029 defines the `tunnel_push_forward` camera path preset — a deep Z-axis push specifically tuned for the tunnel geometry (OBJ-019). Unlike `slow_push_forward` (OBJ-027), which covers 8 world units of generic Z-axis motion, `tunnel_push_forward` covers **25 world units** (z=5 to z=-20), pushing the camera deep into the tunnel corridor where walls, floor, and ceiling undergo dramatic perspective distortion — converging toward the end wall at z=-45. This preset includes a subtle Y-axis rise (from y=-0.3 to y=0) to simulate a slightly grounded starting perspective that levels out, and uses `ease_in_out_cubic` as its default easing for a heavier, more cinematic feel appropriate for the dramatic spatial motion. It implements the `CameraPathPreset` interface from OBJ-006 and is the default camera for the tunnel geometry.
     5→
     6→## Interface Contract
     7→
     8→### ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md",
  "offset": "0",
  "limit": "150"
}
[Tool Result]      0→# Specification: OBJ-030 — Flyover Glide Camera Path Preset
     1→
     2→## Summary
     3→
     4→OBJ-030 defines the `flyover_glide` camera path preset — a bird's-eye aerial movement where the camera is positioned at elevated Y, moves forward along the Z-axis, and looks slightly downward throughout. This preset conforms to the `CameraPathPreset` contract from OBJ-006 and is designed primarily for the `flyover` scene geometry. It produces the feel of gliding over a landscape, looking ahead and down at the terrain below.
     5→
     6→## Interface Contract
     7→
     8→### Preset Export
     9→
    10→```typescript
    11→// src/camera/presets/flyover-glide.ts
    12→
    13→import { CameraPathPreset } from '../types';
    14→
    15→/**
    16→ * The flyover_glide camera path preset.
    17→ * Conforms to CameraPathPreset (OBJ-006).
    18→ */
    19→export const flyoverGlide: CameraPathPreset;
    20→```
    21→
    22→### Spatial Parameters (Constants)
    23→
    24→The... [truncated]
Good spec overall. The data sourcing for tunnel (OBJ-019), flyover (OBJ-021), tunnel_push (OBJ-029), and flyover_glide (OBJ-030) all check out. The section templates are consistent with OBJ-070's established patterns. The scope boundaries are clear.

I have **one critical issue, one major issue, and two minor issues.**

---

### Issue 1: CRITICAL — Bidirectional Compatibility Mismatch (lateral tracks ↔ canyon)

**AC-32** documents lateral track compatible geometries as `stage, canyon, diorama, portal, panorama` — sourced from OBJ-028. **AC-14** documents canyon's compatible cameras as `slow_push_forward, crane_up, dramatic_push, gentle_float, static` — sourced from OBJ-020.

These contradict each other. The lateral tracks claim canyon compatibility, but the canyon does NOT list lateral tracks as compatible cameras. Per OBJ-005: *"Manifest validation (OBJ-041) rejects camera paths not in this list"* — the **geometry's** `compatible_cameras` is the authoritative validation gate. An LLM following SKILL.md that sees `lateral_track_left` as compatible with `canyon` and uses that combination will get a validation error.

This means **AC-54** ("All compatible geometries listed for each camera match the camera spec's `compatibleGeometries` field exactly") and **Test Strategy item 10** (bidirectional check) are in direct tension with what will actually pass validation.

**Proposed fix:** 
1. Add a design decision **D9** explaining the compatibility resolution rule: "When a camera's `compatibleGeometries` lists a geometry that does NOT reciprocate (i.e., the geometry's `compatible_cameras` doesn't include the camera), the pairing is documented as a **known one-directional claim** that will fail manifest validation. The camera-reference section documents what the camera *claims*. The geometry-reference section documents what the geometry *accepts*. An LLM should trust the geometry-reference for selecting cameras for a scene."
2. In the lateral track camera section, add a note: "Listed as compatible with `canyon` per OBJ-028, but `canyon` geometry does not currently list `lateral_track_left`/`lateral_track_right` in its compatible cameras — this pairing will fail manifest validation. See `canyon` geometry reference for its accepted cameras."
3. Revise **AC-54** to read: "All compatible geometries listed for each camera match the camera spec's `compatibleGeometries` field exactly. Any geometry-camera pairing where the camera claims compatibility but the geometry does not reciprocate is documented with a warning note in both the camera and geometry sections."
4. Revise **Test Strategy item 10** to document the specific one-directional entries as known asymmetries rather than treating them as errors.

---

### Issue 2: MAJOR — `tunnel_push_forward` speed scaling documentation incomplete

**AC-39** says: "Speed parameter documented as scaling Z displacement. Default 1.0 = 25 units of Z travel. speed=0.5 → 12.5 units."

But OBJ-029 explicitly specifies that speed **also** scales the Y-axis offset: `startY = -0.3 * speed`. At speed=0.5, Y rises from -0.15 to 0. At speed=2.0, Y rises from -0.6 to 0. OBJ-029 devotes a specific paragraph to this ("Note on Y-axis scaling with speed").

If the SKILL.md only documents Z scaling, an LLM won't know that increasing speed also increases the vertical rise — which could matter for tight tunnel compositions.

**Proposed fix:** Revise AC-39 to: "Speed parameter documented as scaling Z displacement **and Y-axis rise amplitude proportionally**. Default 1.0 = 25 units of Z travel, 0.3 units of Y rise. speed=0.5 → 12.5 units Z, 0.15 units Y."

---

### Issue 3: MINOR — No explicit preservation policy for existing OBJ-070 content

The spec says "Files Modified" for all three files but doesn't state whether OBJ-070's existing full sections (stage geometry, 4 camera presets) are preserved as-is or may be edited. An implementer could reasonably wonder: "Can I rewrite the stage section while I'm in there?"

**Proposed fix:** Add a brief design decision: "Existing full sections from OBJ-070 (stage geometry, static/slow_push_forward/slow_pull_back/gentle_float cameras) are preserved unchanged unless a cross-consistency error is discovered (e.g., a compatible cameras list that contradicts a newly-documented geometry's data). Any such corrections must be noted in the implementation commit message."

---

### Issue 4: MINOR — File existence ambiguity

The spec says "Files Modified" but the proposer's own `Glob` calls showed `SKILL.md` and `docs/skill/*.md` don't exist. OBJ-070's spec is "verified" but its files haven't been implemented. An implementer starting OBJ-071 may find empty ground.

**Proposed fix:** Add a note under "Files Modified": "If OBJ-070's implementation has not yet landed, OBJ-071 creates all files from scratch following both OBJ-070's spec (for structure, stage content, and initial camera content) and OBJ-071's spec (for expanded geometry and camera content). The combined result must satisfy both specs' acceptance criteria."

---

### What's sound

- **Data accuracy:** I verified every slot name, compatible cameras list, fog value, default easing, and speed scaling claim against the source specs. All check out (except the lateral-track/canyon bidirectional issue).
- **Scope discipline:** The spec stays cleanly within "documentation content" territory. No implementation code. No bleed into rendering, validation, or asset generation.
- **Test strategy:** The cross-check tests are well-designed and cover the right verification points.
- **Edge cases table:** Practical and useful — the flyover `ground` vs `floor` confusion and canyon vs tunnel disambiguation are exactly the authoring errors the document needs to prevent.
- **Size budget:** The 250-350 line addition estimate is reasonable for 3 geometry sections + 4 camera sections.

Please address the critical and major issues. The minor ones can be handled with brief additions.

---

## Round 3 — spec_author

All four issues are valid. Here's my revised spec with the fixes integrated:

---

# Specification: OBJ-071 — SKILL.md Geometry and Camera Reference Sections

## Summary

OBJ-071 fills in the geometry and camera reference sub-files (`docs/skill/geometry-reference.md` and `docs/skill/camera-reference.md`) created as scaffolding by OBJ-070. OBJ-070 established the document architecture and provided a full section for the `stage` geometry and full sections for `slow_push_forward`, `slow_pull_back`, `static`, and `gentle_float` cameras, with stub sections for everything else. OBJ-071 expands stubs to full sections for all verified geometries (`tunnel`, `canyon`, `flyover`) and all verified camera presets (`lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, `flyover_glide`), updates the SKILL.md summary tables to reflect the new content, and updates the complete annotated example in SKILL.md to use at least one newly-documented geometry. Stub sections remain for unverified geometries and cameras. This objective is the primary blocker for OBJ-056 (manifest generation via Claude API), which requires comprehensive reference documentation for LLM-driven authoring.

## Interface Contract

OBJ-071 is a documentation objective. Its "interface" is the content structure of Markdown files. No TypeScript code is produced.

### Files Modified (or Created)

| File | Action | Content Added |
|------|--------|---------------|
| `docs/skill/geometry-reference.md` | Modify | Full sections for `tunnel`, `canyon`, `flyover`. Update stubs for `diorama`, `portal`, `panorama`, `close_up` with verified slot names where available. |
| `docs/skill/camera-reference.md` | Modify | Full sections for `lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, `flyover_glide`. Update stubs for `dramatic_push`, `crane_up`, `dolly_zoom` with seed descriptions. |
| `SKILL.md` | Modify | Update geometry summary table (rows for tunnel, canyon, flyover now include required slots and compatible cameras). Update camera summary table (rows for newly documented cameras). Optionally update the complete annotated example to use a verified geometry beyond `stage`. |

**File existence note:** If OBJ-070's implementation has not yet landed (i.e., these files do not yet exist on disk), OBJ-071 creates all files from scratch following both OBJ-070's spec (for structure, stage content, and initial camera content) and OBJ-071's spec (for expanded geometry and camera content). The combined result must satisfy both specs' acceptance criteria. OBJ-070 is verified as a *spec*, meaning its design is approved — the implementer of OBJ-071 may be the first to create the actual files.

### Geometry Full Section Template

Each full geometry section follows the pattern established by OBJ-070 AC-23 for `stage`. The structure is:

```markdown
### `{geometry_name}`

**Description:** [From the verified geometry spec's `description` field]

**When to use:** [Authoring guidance — what kinds of scenes/topics suit this geometry. Derived from the geometry spec's description and design rationale.]

**Required slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `{slot_name}` | [From slot's `description` field] | [Derived from slot guidance export or PlaneSlot description + transparency requirements] |

**Optional slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `{slot_name}` | [From slot's `description` field] | [Same derivation] |

**Default camera:** `{default_camera}`

**Compatible cameras:** [List from geometry spec's `compatible_cameras`]

**Fog:** [Color, near, far from geometry spec. Plain-English description of the fog's visual effect.]

**Transparency:** [Which slots require transparent background images, matching `transparent: true` slots]

**Aspect ratio:** [From `preferred_aspect`. Guidance on landscape vs portrait suitability.]

**Tips:**
- [Authoring tips specific to this geometry — what makes it look good, common mistakes]
```

### Camera Full Section Template

Each full camera section follows the pattern established by OBJ-070 AC-29 for `slow_push_forward`. The structure is:

```markdown
### `{camera_name}`

**Motion:** [1-2 sentence motion description from the camera spec]

**Feel:** [Qualitative description of the cinematic feel — how it reads emotionally/visually]

**When to use:** [Authoring guidance — what kinds of scenes/moments suit this camera]

**Compatible geometries:** [List from camera spec's `compatibleGeometries`]

**Parameters:**
| Param | Default | Effect |
|-------|---------|--------|
| `speed` | `1.0` | [Effect description specific to this preset — all axes affected] |
| `easing` | `{defaultEasing}` | [Effect description] |

**Notes:**
- [Usage notes, cautions, interaction with specific geometries]
- [Compatibility warnings if any geometry claims are one-directional — see D9]
```

### Geometry Summary Table Update (in SKILL.md)

The summary table in the primary SKILL.md (per OBJ-070 AC-13) must be updated so that rows for `tunnel`, `canyon`, and `flyover` include accurate data sourced from their verified specs. Specifically:

| Geometry | Required Slots | Default Camera | When to Use |
|----------|---------------|----------------|-------------|
| `stage` | `backdrop`, `floor`, `subject` | `slow_push_forward` | *(existing from OBJ-070)* |
| `tunnel` | `floor`, `left_wall`, `right_wall`, `end_wall` | `tunnel_push_forward` | Corridors, hallways, enclosed passages |
| `canyon` | `sky`, `left_wall`, `right_wall`, `floor` | `slow_push_forward` | Gorges, alleys, narrow dramatic spaces |
| `flyover` | `sky`, `ground` | `slow_push_forward` | Landscapes, aerial views, travel themes |
| `diorama` | *(TBD — not verified)* | *(TBD)* | Paper-theater layered scenes |
| `portal` | *(TBD — not verified)* | *(TBD)* | Concentric frames, dreamlike sequences |
| `panorama` | *(TBD — not verified)* | *(TBD)* | Wide environments with camera pan |
| `close_up` | *(TBD — not verified)* | *(TBD)* | Tight focus, minimal background |

### Camera Summary Table Update (in SKILL.md)

The camera summary table (per OBJ-070 AC-14) must be updated with rows for newly documented cameras:

| Camera | Motion Type | Compatible Geometries | When to Use |
|--------|------------|----------------------|-------------|
| *(existing OBJ-070 entries for static, slow_push_forward, slow_pull_back, gentle_float)* | | | |
| `lateral_track_left` | Horizontal slide left | stage, diorama, portal, panorama *(see notes)* | Tracking shots, revealing lateral depth |
| `lateral_track_right` | Horizontal slide right | stage, diorama, portal, panorama *(see notes)* | Mirror of lateral_track_left |
| `tunnel_push_forward` | Deep Z-axis push | tunnel | Traveling through enclosed spaces |
| `flyover_glide` | Elevated forward glide | flyover | Aerial/bird's-eye establishing shots |
| `dramatic_push` | *(stub — details pending)* | *(TBD)* | Emphasis, tension |
| `crane_up` | *(stub — details pending)* | *(TBD)* | Vertical reveals |
| `dolly_zoom` | *(stub — details pending)* | *(TBD)* | Dramatic Hitchcock effect |

## Design Decisions

### D1: Scope — Full Sections Only for Verified Objectives

**Decision:** Full sections are written only for geometries and cameras whose defining objectives are verified in the progress map. Unverified objectives retain stub sections.

**Verified geometries for full sections:** `tunnel` (OBJ-019), `canyon` (OBJ-020), `flyover` (OBJ-021). Stage already has a full section from OBJ-070.

**Verified cameras for full sections:** `lateral_track_left` and `lateral_track_right` (OBJ-028), `tunnel_push_forward` (OBJ-029), `flyover_glide` (OBJ-030). Static, slow_push_forward, slow_pull_back, and gentle_float already have full sections from OBJ-070.

**Stub-only geometries:** `diorama` (OBJ-022, open), `portal` (OBJ-023, open), `panorama` (OBJ-024, open), `close_up` (OBJ-025, open).

**Stub-only cameras:** `dramatic_push` (OBJ-032, open), `crane_up` (OBJ-033, open), `dolly_zoom` (OBJ-034, open).

**Rationale:** Writing full documentation for unverified objectives would require speculating about slot names, spatial parameters, and compatible cameras that don't yet exist in code. This violates the seed's principle that documentation must match implementation. Stubs clearly mark "details pending" and prevent the LLM from attempting to use undocumented features.

### D2: Image Guidance Sourced from Multiple Places

**Decision:** Per-slot image guidance is sourced from:
1. **Tunnel:** The `tunnelSlotGuidance` companion export defined in OBJ-019.
2. **Canyon:** The `DepthSlot` metadata (`promptGuidance`, `expectsAlpha`) defined inline in OBJ-020.
3. **Flyover:** The `PlaneSlot.description` field plus transparency flags, since OBJ-021 follows OBJ-018's pattern of not exporting a separate guidance object (per OBJ-021 D11). The implementer must derive image guidance from slot descriptions, transparency flags, and the geometry's description.

**Rationale:** There is no single unified mechanism for prompt guidance across all geometries. OBJ-019 introduced a `tunnelSlotGuidance` companion export. OBJ-020 merged DepthSlot metadata into the slot objects. OBJ-021 defers guidance to SKILL.md. The implementer must handle all three patterns. This is documented here so the implementer knows where to look for each geometry.

### D3: Tunnel Documentation Notes `preferred_aspect: 'landscape'`

**Decision:** The tunnel, canyon, and flyover geometry sections each include an "Aspect ratio" note sourced from their respective `preferred_aspect` field.

**Rationale:** OBJ-005 defines `preferred_aspect` as advisory guidance for SKILL.md. Surfacing it in the geometry reference helps LLMs make orientation decisions.

### D4: Camera Sections Document Speed Scaling Behavior per Preset — All Affected Axes

**Decision:** Each camera section's `speed` parameter description is specific to that preset and covers **all axes affected**, not just the primary motion axis. For example:
- `tunnel_push_forward`: "Scales Z displacement **and Y-axis rise amplitude proportionally**. Default 1.0 = 25 units of Z travel, 0.3 units of Y rise. speed=0.5 → 12.5 units Z, 0.15 units Y rise."
- `lateral_track_left`: "Scales X displacement. Default 1.0 = 6 units of horizontal travel."
- `flyover_glide`: "Scales Z displacement only; camera elevation (Y) is constant."

**Rationale:** Per OBJ-006 D3, speed scales "spatial amplitude" but the meaning varies per preset. OBJ-029 explicitly documents that speed scales both Z displacement and Y offset. Generic documentation like "scales the motion" doesn't help an LLM predict the visual result. Documenting all affected axes prevents surprise behavior at non-default speed values.

### D5: Complete Annotated Example May Be Updated to Include Tunnel or Canyon

**Decision:** The complete annotated example in SKILL.md (OBJ-070 AC-10) may be updated to use `tunnel` or `canyon` as one of its scenes, demonstrating that an LLM can use multiple geometries in a single manifest. If updated, the example must remain valid JSON that passes `loadManifest()` with all referenced geometries and cameras registered.

**Rationale:** OBJ-070 AC-10 says the example "MAY use verified geometries beyond stage." OBJ-071 provides the documented reference that makes such usage meaningful. Including a tunnel or canyon scene in the example demonstrates geometry diversity and gives the LLM a concrete multi-geometry authoring pattern.

### D6: Stub Sections Updated with Known Data from Seed

**Decision:** Stub sections for unverified geometries are updated to include any data available from the seed (Section 4.2 descriptions) but continue to mark slot names and compatible cameras as "TBD" unless the geometry happens to appear in a verified camera's `compatibleGeometries` list.

For example, `diorama` appears in the `compatibleGeometries` of `lateral_track_left` (OBJ-028), `slow_push_forward` (OBJ-027), `gentle_float` (OBJ-031), and `static` (OBJ-026). The stub can note these known compatible cameras even though the geometry itself is not verified. However, slot names remain "TBD" since no verified spec defines them.

**Rationale:** Cross-referencing verified camera specs gives stubs more useful content without speculating about unverified geometry definitions.

### D7: Content is Manually Authored, Not Auto-Generated

**Decision:** Carried forward from OBJ-070 D8. All content is authored by the implementer for pedagogical clarity, not generated from registry data. Content must be **consistent** with the verified specs (acceptance criteria verify this) but the prose is crafted for LLM readability.

### D8: Combined Size Budget Remains Under 2000 Lines / 60KB

**Decision:** OBJ-071 adds substantial content (3 full geometry sections, 4 full camera sections). The implementer must ensure the combined total of SKILL.md + all sub-files stays under the 2000-line / 60KB target from OBJ-070 AC-48.

**Rationale:** SC-04 requires the document to fit within a single LLM context window alongside system prompts and conversation. Each full geometry section is approximately 40-60 lines; each full camera section is approximately 25-35 lines. The additions total roughly 250-350 lines, which should fit within the budget if the existing content from OBJ-070 is approximately 700-900 lines.

### D9: Compatibility Resolution Rule — Geometry Is Authoritative for Validation

**Decision:** When a camera's `compatibleGeometries` lists a geometry that does NOT reciprocate (i.e., the geometry's `compatible_cameras` does not include that camera), the documentation treats the **geometry's list as authoritative for manifest validation**. OBJ-005 states: *"Manifest validation (OBJ-041) rejects camera paths not in this list"* — the geometry's `compatible_cameras` is the validation gate.

In practice, this means:
- The **geometry-reference** section documents the geometry's `compatible_cameras` as the definitive list of cameras an LLM should choose from for that geometry.
- The **camera-reference** section documents the camera's `compatibleGeometries` as the camera's *claimed* compatibility, with a **warning note** on any geometry that does not reciprocate: *"Listed as compatible per [camera spec], but [geometry] does not list this camera in its compatible cameras — this pairing will fail manifest validation."*
- An LLM should **always trust the geometry-reference** when selecting cameras for a scene.

**Known one-directional claims as of this spec:**
- `lateral_track_left` and `lateral_track_right` (OBJ-028) claim `canyon` compatibility, but `canyon` (OBJ-020) does NOT list lateral tracks in its `compatible_cameras`. This pairing will fail validation.

**Rationale:** The geometry defines the validated spatial envelope. A camera claiming compatibility with a geometry it hasn't been spatially validated against is aspirational — the geometry author may have excluded it due to edge-reveal risk or spatial mismatch. The SKILL.md must not mislead the LLM into using a combination that will be rejected. Documenting the asymmetry transparently serves both accuracy and trust.

### D10: Preservation Policy for Existing OBJ-070 Content

**Decision:** Existing full sections from OBJ-070 (stage geometry, static/slow_push_forward/slow_pull_back/gentle_float cameras) are preserved unchanged unless a cross-consistency error is discovered (e.g., a compatible cameras list that contradicts a newly-documented geometry's data). Any such corrections must be noted in the implementation commit message with a reference to the contradicting spec.

**Rationale:** OBJ-070 is verified. Its content was validated against OBJ-018, OBJ-026, OBJ-027, OBJ-031. Rewriting verified content without cause risks introducing errors.

## Acceptance Criteria

### Geometry Reference Sub-File (`docs/skill/geometry-reference.md`)

#### Tunnel Geometry — Full Section

- [ ] **AC-01:** Contains a full section for `tunnel` with the section structure defined in the Interface Contract (description, when to use, required slots table, optional slots table, default camera, compatible cameras, fog, transparency, aspect ratio, tips).
- [ ] **AC-02:** Tunnel required slots listed as: `floor`, `left_wall`, `right_wall`, `end_wall` — matching OBJ-019 exactly.
- [ ] **AC-03:** Tunnel optional slot listed as: `ceiling` — matching OBJ-019 exactly.
- [ ] **AC-04:** Tunnel default camera documented as `tunnel_push_forward` — matching OBJ-019.
- [ ] **AC-05:** Tunnel compatible cameras listed as: `tunnel_push_forward`, `slow_push_forward`, `static`, `gentle_float` — matching OBJ-019 exactly.
- [ ] **AC-06:** Tunnel fog documented as: color `#000000`, near `15`, far `50` — matching OBJ-019.
- [ ] **AC-07:** Tunnel `preferred_aspect` documented as `landscape`.
- [ ] **AC-08:** Tunnel transparency note states that all slots use opaque images (no slot has `transparent: true` in OBJ-019).
- [ ] **AC-09:** Tunnel image guidance per slot is sourced from `tunnelSlotGuidance` (OBJ-019's companion export) and accurately reflects `promptGuidance` content for each slot.

#### Canyon Geometry — Full Section

- [ ] **AC-10:** Contains a full section for `canyon` with the section structure defined in the Interface Contract.
- [ ] **AC-11:** Canyon required slots listed as: `sky`, `left_wall`, `right_wall`, `floor` — matching OBJ-020.
- [ ] **AC-12:** Canyon optional slots listed as: `end_wall`, `subject` — matching OBJ-020.
- [ ] **AC-13:** Canyon default camera documented as `slow_push_forward` — matching OBJ-020.
- [ ] **AC-14:** Canyon compatible cameras listed as: `slow_push_forward`, `crane_up`, `dramatic_push`, `gentle_float`, `static` — matching OBJ-020 exactly.
- [ ] **AC-15:** Canyon fog documented as: color `#1a1a2e`, near `15`, far `48` — matching OBJ-020.
- [ ] **AC-16:** Canyon `preferred_aspect` documented as `landscape`.
- [ ] **AC-17:** Canyon transparency note states that `subject` requires transparent background. All other slots are opaque.
- [ ] **AC-18:** Canyon image guidance per slot is sourced from OBJ-020's inline DepthSlot metadata (`promptGuidance` fields).

#### Flyover Geometry — Full Section

- [ ] **AC-19:** Contains a full section for `flyover` with the section structure defined in the Interface Contract.
- [ ] **AC-20:** Flyover required slots listed as: `sky`, `ground` — matching OBJ-021.
- [ ] **AC-21:** Flyover optional slots listed as: `landmark_far`, `landmark_left`, `landmark_right`, `near_fg` — matching OBJ-021.
- [ ] **AC-22:** Flyover slot named `ground` (not `floor`) — matching OBJ-021 D1.
- [ ] **AC-23:** Flyover default camera documented as `slow_push_forward` — matching OBJ-021 (with a note that `flyover_glide` is the intended future default).
- [ ] **AC-24:** Flyover compatible cameras listed as: `static`, `flyover_glide`, `slow_push_forward`, `slow_pull_back`, `gentle_float` — matching OBJ-021.
- [ ] **AC-25:** Flyover fog documented as: color `#b8c6d4`, near `20`, far `55` — matching OBJ-021.
- [ ] **AC-26:** Flyover `preferred_aspect` documented as `landscape`.
- [ ] **AC-27:** Flyover transparency note states that `landmark_far`, `landmark_left`, `landmark_right`, and `near_fg` require transparent backgrounds. `sky` and `ground` are opaque.
- [ ] **AC-28:** Flyover image guidance derived from OBJ-021 slot descriptions and OBJ-021 D11 guidance note.

#### Stub Sections — Updated

- [ ] **AC-29:** Stub sections exist for `diorama`, `portal`, `panorama`, `close_up`. Each retains the stub structure from OBJ-070 AC-28 (heading, status note, description, slot names as TBD or listed if inferable, default camera as TBD).
- [ ] **AC-30:** Stub descriptions match seed Section 4.2 for each geometry.

### Camera Reference Sub-File (`docs/skill/camera-reference.md`)

#### Lateral Track Cameras — Full Sections

- [ ] **AC-31:** Contains full sections for both `lateral_track_left` and `lateral_track_right` following the camera section template.
- [ ] **AC-32:** Lateral track compatible geometries documented as: `stage`, `canyon`, `diorama`, `portal`, `panorama` — matching OBJ-028's `compatibleGeometries` exactly.
- [ ] **AC-33:** A warning note in the lateral track sections states that `canyon` is listed per OBJ-028 but the canyon geometry (OBJ-020) does NOT list lateral tracks in its `compatible_cameras`, and this pairing will fail manifest validation. Per D9, the LLM should trust the geometry-reference for camera selection.
- [ ] **AC-34:** Lateral track default easing documented as `ease_in_out` — matching OBJ-028.
- [ ] **AC-35:** Speed parameter documented as scaling X-axis displacement. Default 1.0 = 6 units of horizontal travel.
- [ ] **AC-36:** Motion descriptions note that the camera slides horizontally while looking slightly ahead of travel direction, and that background planes move in the opposite direction while foreground planes move faster.

#### Tunnel Push Forward — Full Section

- [ ] **AC-37:** Contains a full section for `tunnel_push_forward` following the camera section template.
- [ ] **AC-38:** Tunnel push forward compatible geometries listed as: `tunnel` — matching OBJ-029 (tunnel-only preset).
- [ ] **AC-39:** Default easing documented as `ease_in_out_cubic` — matching OBJ-029.
- [ ] **AC-40:** Speed parameter documented as scaling Z displacement **and Y-axis rise amplitude proportionally**. Default 1.0 = 25 units of Z travel, 0.3 units of Y rise. speed=0.5 → 12.5 units Z, 0.15 units Y rise.
- [ ] **AC-41:** Motion description notes the deep Z-axis push, the subtle Y-axis rise, and the wall convergence toward a vanishing point.

#### Flyover Glide — Full Section

- [ ] **AC-42:** Contains a full section for `flyover_glide` following the camera section template.
- [ ] **AC-43:** Flyover glide compatible geometries listed as: `flyover` — matching OBJ-030.
- [ ] **AC-44:** Default easing documented as `ease_in_out` — matching OBJ-030.
- [ ] **AC-45:** Speed parameter documented as scaling Z displacement only; camera elevation (Y) is constant. Default 1.0 = 30 units of Z travel.
- [ ] **AC-46:** Motion description notes the elevated camera position, constant downward viewing angle (~34° below horizontal), and the co-moving lookAt that maintains consistent aerial perspective.

#### Stub Sections — Updated

- [ ] **AC-47:** Stub sections exist for `dramatic_push`, `crane_up`, `dolly_zoom`. Each has heading, status note, and 1-sentence motion description from seed Section 4.3.
- [ ] **AC-48:** Stubs for `dramatic_push` and `crane_up` note they appear in the canyon's `compatible_cameras` list (from OBJ-020) as forward references.

### Primary File (`SKILL.md`) Updates

- [ ] **AC-49:** The geometry summary table includes rows for `tunnel`, `canyon`, and `flyover` with accurate required slots, default camera, and "when to use" text.
- [ ] **AC-50:** The camera summary table includes rows for `lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, and `flyover_glide` with accurate compatible geometries and "when to use" text.
- [ ] **AC-51:** The camera summary table for lateral tracks notes the canyon compatibility caveat (per D9) — e.g., with an asterisk and footnote, or by listing only geometries that reciprocate in the summary table and noting the full claimed list in the camera-reference sub-file.
- [ ] **AC-52:** If the complete annotated example is updated to include a non-`stage` geometry, the example remains valid JSON that passes `loadManifest()` when all referenced geometries and cameras are registered.

### Cross-Consistency

- [ ] **AC-53:** All geometry slot names in geometry-reference.md match the verified specs exactly (e.g., flyover uses `ground` not `floor`, canyon uses `sky` not `ceiling`).
- [ ] **AC-54:** All camera preset names match registered names (e.g., `tunnel_push_forward` not `tunnel_push`, `flyover_glide` not `flyover_push`).
- [ ] **AC-55:** All compatible cameras listed for each geometry match the geometry spec's `compatible_cameras` field exactly.
- [ ] **AC-56:** All compatible geometries listed for each camera match the camera spec's `compatibleGeometries` field exactly. Any geometry-camera pairing where the camera claims compatibility but the geometry does not reciprocate is documented with a warning note in both the camera and geometry sections, per D9.
- [ ] **AC-57:** All easing names referenced match OBJ-004's enum: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`.
- [ ] **AC-58:** The vocabulary used throughout matches seed Section 2 definitions (plane not layer, scene geometry not layout template, etc.).
- [ ] **AC-59:** Fog colors in documentation match exact hex values from geometry specs (e.g., canyon fog is `#1a1a2e`, not "dark blue-gray").

### Size Budget

- [ ] **AC-60:** The total combined size of `SKILL.md` + all sub-files remains under 2000 lines / 60KB (per OBJ-070 AC-48).

### Content Preservation

- [ ] **AC-61:** Existing full sections from OBJ-070 (stage geometry, static/slow_push_forward/slow_pull_back/gentle_float cameras) are preserved unchanged unless a cross-consistency error requires correction. Any corrections are documented in commit messages.

## Edge Cases and Error Handling

OBJ-071 is a documentation artifact. "Edge cases" are authoring scenarios the new content must address.

### Authoring Scenarios the New Content Must Cover

| Scenario | How the Documentation Handles It |
|----------|----------------------------------|
| LLM uses `floor` slot name with flyover geometry | Flyover geometry section explicitly notes the slot is named `ground`, not `floor`. The slot table makes this unambiguous. Tips section warns: "The flyover's ground slot is named `ground`, not `floor` — do not confuse with the stage or tunnel `floor` slot." |
| LLM uses `tunnel_push_forward` camera with stage geometry | Camera section for `tunnel_push_forward` explicitly lists compatible geometries as `tunnel` only. Stage section lists its compatible cameras — `tunnel_push_forward` is not among them. |
| LLM uses `lateral_track_left` with tunnel geometry | Camera section explicitly lists compatible geometries. Tunnel geometry section lists its compatible cameras — lateral tracks are not among them. |
| LLM uses `lateral_track_left` with canyon geometry | Camera section lists `canyon` in compatible geometries but includes a **warning**: canyon does not reciprocate. Canyon geometry section does NOT list lateral tracks. The LLM should see from the canyon section that lateral tracks are not valid cameras for canyon scenes. Per D9, the geometry-reference is authoritative for camera selection. |
| LLM uses a stub geometry (e.g., `diorama`) | Stub section has a clear status note: "Details pending." The LLM should be able to determine that slot names are not yet available and choose a documented geometry instead. |
| LLM wants canyon with a subject element | Canyon's optional `subject` slot is documented in the full section with transparency requirements and image guidance. |
| LLM wants flyover without landmarks | Flyover section shows only `sky` and `ground` as required. Tips note: "A valid flyover needs only two images — a ground texture and a sky backdrop." |
| LLM wants tunnel without ceiling | Tunnel section marks `ceiling` as optional with description: "Omit for open-air passages." |
| LLM confuses canyon with tunnel | Both sections include a "When to use" that distinguishes them: canyon has open sky above, tunnel is fully enclosed (or open-ceiling variant). Tips in each section reference the other for comparison. |
| LLM uses `flyover_glide` as default camera for flyover | Flyover section notes that `slow_push_forward` is the current default camera and `flyover_glide` is the intended future default. Both are in the compatible list. Either works. |
| LLM sets `tunnel_push_forward` speed=2.0 and doesn't expect the Y-axis rise to double | Tunnel push camera section documents that speed scales **both** Z displacement and Y-axis rise proportionally. At speed=2.0, Y rises from -0.6 to 0 instead of -0.3 to 0. |

### Document Maintenance Considerations

| Scenario | Handling |
|----------|----------|
| OBJ-022 (portal) is verified after OBJ-071 | Replace the portal stub in geometry-reference.md with a full section using OBJ-022's verified data. Update the summary table in SKILL.md. This is a follow-on change, not OBJ-071's responsibility. |
| Visual tuning (OBJ-059–OBJ-066) changes slot positions/sizes | Positions and sizes are NOT documented in SKILL.md (LLMs don't need them — they use slot names, not coordinates). Fog colors, compatible cameras, and slot names ARE documented and must be updated if tuning changes them. |
| Camera compatibility list updated after tuning | Update both geometry-reference.md (geometry's compatible cameras) and camera-reference.md (camera's compatible geometries). Verify bidirectional consistency per D9. |
| Canyon adds lateral tracks to `compatible_cameras` after OBJ-041 validation | Remove the one-directional warning from the lateral track camera section. Update canyon geometry section to include lateral tracks. The asymmetry is resolved. |

## Test Strategy

### Implementer Tests (run before marking objective complete)

**1. Slot Name Cross-Check — Tunnel:**
Verify that the documented required and optional slot names for `tunnel` match OBJ-019's `tunnelGeometry.slots` exactly. Required: `floor`, `left_wall`, `right_wall`, `end_wall`. Optional: `ceiling`.

**2. Slot Name Cross-Check — Canyon:**
Verify that the documented slots for `canyon` match OBJ-020. Required: `sky`, `left_wall`, `right_wall`, `floor`. Optional: `end_wall`, `subject`.

**3. Slot Name Cross-Check — Flyover:**
Verify that the documented slots for `flyover` match OBJ-021. Required: `sky`, `ground`. Optional: `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`. Confirm the slot is named `ground` not `floor`.

**4. Camera Compatibility Cross-Check — Tunnel:**
Verify tunnel's documented compatible cameras match OBJ-019's `compatible_cameras`: `tunnel_push_forward`, `slow_push_forward`, `static`, `gentle_float`.

**5. Camera Compatibility Cross-Check — Canyon:**
Verify canyon's documented compatible cameras match OBJ-020's `compatible_cameras`: `slow_push_forward`, `crane_up`, `dramatic_push`, `gentle_float`, `static`.

**6. Camera Compatibility Cross-Check — Flyover:**
Verify flyover's documented compatible cameras match OBJ-021's `compatible_cameras`: `static`, `flyover_glide`, `slow_push_forward`, `slow_pull_back`, `gentle_float`.

**7. Camera Compatible Geometries Cross-Check — Lateral Tracks:**
Verify `lateral_track_left`/`lateral_track_right` documented compatible geometries match OBJ-028: `stage`, `canyon`, `diorama`, `portal`, `panorama`.

**8. Camera Compatible Geometries Cross-Check — Tunnel Push:**
Verify `tunnel_push_forward` documented compatible geometries match OBJ-029: `tunnel` only.

**9. Camera Compatible Geometries Cross-Check — Flyover Glide:**
Verify `flyover_glide` documented compatible geometries match OBJ-030: `flyover` only.

**10. Bidirectional Compatibility Verification:**
For every geometry-camera pairing documented: verify the camera appears in the geometry's compatible list AND the geometry appears in the camera's compatible list. Document specific one-directional entries as known asymmetries with warning notes per D9:
- **Known asymmetry:** `lateral_track_left`/`lateral_track_right` claim `canyon` compatibility (OBJ-028), but `canyon` (OBJ-020) does not list them. Verify this asymmetry is documented with warnings in both the camera sections and the canyon geometry section.
- **Known forward references:** `crane_up` and `dramatic_push` appear in canyon's `compatible_cameras` but are stub cameras. Verify this is noted in both the canyon section and the camera stubs.

**11. Fog Value Cross-Check:**
- Tunnel fog: `#000000`, near=15, far=50 (OBJ-019)
- Canyon fog: `#1a1a2e`, near=15, far=48 (OBJ-020)
- Flyover fog: `#b8c6d4`, near=20, far=55 (OBJ-021)

**12. Easing Cross-Check:**
- `tunnel_push_forward` default easing: `ease_in_out_cubic` (OBJ-029)
- `lateral_track_left/right` default easing: `ease_in_out` (OBJ-028)
- `flyover_glide` default easing: `ease_in_out` (OBJ-030)

**13. Speed Scaling Cross-Check:**
- `tunnel_push_forward`: Verify documentation states speed scales **both** Z displacement (25 units) **and** Y-axis rise (0.3 units) proportionally, per OBJ-029.
- `lateral_track_left/right`: Verify documentation states speed scales X displacement (6 units), per OBJ-028.
- `flyover_glide`: Verify documentation states speed scales Z displacement (30 units) only; Y elevation is constant, per OBJ-030.

**14. Vocabulary Check:**
Search all modified files for vocabulary violations: "layer" (should be "plane"), "layout template" (should be "scene geometry"), "z-level" (should be "depth slot").

**15. Size Budget Check:**
Count total lines across SKILL.md + all sub-files. Verify under 2000 lines / 60KB.

**16. Complete Example Validation (if updated):**
If the complete annotated example is updated to include a non-`stage` geometry, extract the JSON, register all referenced geometries and cameras, and run through `loadManifest()`. Must return `success: true` with zero errors.

**17. Content Preservation Check:**
Verify that the stage geometry section and the static/slow_push_forward/slow_pull_back/gentle_float camera sections are unchanged from OBJ-070's spec (or document any corrections with rationale).

### Relevant Testable Claims

- **TC-04:** The expanded geometry reference enables LLMs to author valid manifests for tunnel, canyon, and flyover scenes using only slot names — no XYZ coordinates.
- **TC-07:** The documented compatible cameras and slot names match implementation, ensuring validation catches common errors the LLM might make.
- **TC-08:** With 4 fully documented geometries (stage, tunnel, canyon, flyover) plus 4 stubs, the documentation tracks geometry availability for the design-space coverage test.
- **SC-02:** The expanded SKILL.md enables the 5-topic blind authoring test to use diverse geometries beyond just `stage`.
- **SC-04:** OBJ-071 is the primary content expansion that makes SKILL.md comprehensive enough for self-sufficient authoring.

## Integration Points

### Depends On

| Dependency | What OBJ-071 Uses |
|---|---|
| **OBJ-070** (SKILL.md structure) | Document architecture, existing full sections (stage geometry, 4 camera presets), summary table structure, size budget, section templates. OBJ-071 follows OBJ-070's established patterns exactly. |
| **OBJ-005** (Geometry type contract) | `SceneGeometry` interface structure — informs what fields to document (slots, compatible_cameras, default_camera, fog, preferred_aspect, description). |
| **OBJ-006** (Camera path type contract) | `CameraPathPreset` interface structure — informs what fields to document (name, description, compatibleGeometries, defaultEasing, oversizeRequirements, tags). `CameraParams` fields (speed, easing, offset) documented in parameter tables. |
| **OBJ-018** (Stage geometry) | Verified. Already documented by OBJ-070. OBJ-071 does not modify the stage section but cross-references it. |
| **OBJ-019** (Tunnel geometry) | Verified. Source for tunnel full section: slot names, descriptions, rotations, required/optional flags, compatible cameras, fog, preferred_aspect, description. `tunnelSlotGuidance` companion export for image guidance. |

**Non-dependency verified objectives consulted for content:**

| Objective | What OBJ-071 Uses |
|---|---|
| **OBJ-020** (Canyon geometry, verified) | Source for canyon full section: slot names, required/optional, compatible cameras, fog, preferred_aspect, description, inline DepthSlot `promptGuidance`. |
| **OBJ-021** (Flyover geometry, verified) | Source for flyover full section: slot names (including custom `ground`), required/optional, compatible cameras, fog, preferred_aspect, description. |
| **OBJ-026** (Static camera, verified) | Already documented by OBJ-070. Cross-referenced for compatibility lists. |
| **OBJ-027** (Push/pull cameras, verified) | Already documented by OBJ-070. Cross-referenced for compatibility lists. |
| **OBJ-028** (Lateral track cameras, verified) | Source for lateral track full sections: motion model, compatible geometries, default easing, speed scaling, description. |
| **OBJ-029** (Tunnel push forward, verified) | Source for tunnel push full section: motion model, compatible geometries, default easing, speed scaling (Z + Y), Y-axis rise, description. |
| **OBJ-030** (Flyover glide, verified) | Source for flyover glide full section: motion model, compatible geometries, default easing, speed scaling, elevation, viewing angle, description. |
| **OBJ-031** (Gentle float, verified) | Already documented by OBJ-070. Cross-referenced for compatibility lists. |

### Consumed By

| Downstream | How It Uses OBJ-071 |
|---|---|
| **OBJ-056** (Manifest generation via Claude API) | Depends on OBJ-071 for comprehensive geometry and camera documentation that enables the Claude API to generate valid manifests using diverse geometries. This is the primary blocker relationship. |
| **OBJ-059–OBJ-066** (Visual tuning) | If visual tuning changes compatible cameras or fog settings, the corresponding sections in geometry-reference.md and camera-reference.md must be updated. OBJ-071 establishes the content that tuning may revise. |
| **SC-02** (Blind authoring validation) | Uses SKILL.md + sub-files as the sole reference. OBJ-071's expanded content enables authoring beyond `stage`-only manifests. |
| **SC-04** (SKILL.md self-sufficiency) | OBJ-071 is the primary content expansion needed for the self-sufficiency criterion. |

### File Placement

```
depthkit/
  SKILL.md                              # MODIFIED (or CREATED): summary tables updated
  docs/
    skill/
      geometry-reference.md             # MODIFIED (or CREATED): tunnel, canyon, flyover full sections
      camera-reference.md               # MODIFIED (or CREATED): lateral tracks, tunnel push, flyover glide full sections
```

No new files beyond those specified by OBJ-070's architecture are created. OBJ-071 modifies (or initially creates) files defined by OBJ-070's spec.

## Open Questions

### OQ-A: Should Geometry Sections Include Spatial Diagrams?

Carried forward from OBJ-070 OQ-B. ASCII art diagrams showing tunnel cross-section or canyon wall arrangement could help human readers. LLMs may not reliably interpret ASCII art. **Recommendation:** Use plain-English spatial descriptions (e.g., "Two tall walls on left and right with a floor between them and open sky above"). If human readers request diagrams, they can be added as a follow-on enhancement.

### OQ-B: Should Camera Sections Document the offset Parameter?

The `offset` parameter (from `CameraParams`) is universal across all cameras — it's applied post-evaluate by the renderer (OBJ-006 D2). OBJ-070's camera sections document `speed` and `easing` per-preset. Should each camera section also document `offset`? **Recommendation:** Document `offset` once in the primary SKILL.md (in the camera summary or the scene authoring workflow) rather than repeating it in every camera section. Note: OBJ-070 may already cover this in the manifest-schema-reference.md under `camera_params`.

### OQ-C: Canyon Lists `crane_up` and `dramatic_push` as Compatible but These Are Stub Cameras

Canyon's `compatible_cameras` (OBJ-020) includes `crane_up` and `dramatic_push`, which are unverified (OBJ-032, OBJ-033 are open). The canyon full section must list them as compatible, but the camera-reference.md only has stubs for these presets. **Recommendation:** List them in the canyon section with a note: "See camera reference — details pending for `crane_up` and `dramatic_push`." This is accurate and prevents the LLM from being surprised by an "incompatible camera" validation error when using these (since the engine will accept them if they're registered).

### OQ-D: Should the Lateral Track ↔ Canyon Asymmetry Be Escalated?

The one-directional compatibility claim (OBJ-028 claims canyon, OBJ-020 doesn't reciprocate) may indicate a spec-level inconsistency that should be resolved upstream — either canyon should add lateral tracks to `compatible_cameras`, or OBJ-028 should remove canyon from `compatibleGeometries`. This is beyond OBJ-071's scope (documentation reflects verified specs, doesn't resolve spec conflicts). **Recommendation:** Flag this asymmetry for the integrator/reviewer. OBJ-071 documents it transparently per D9.

---

I believe all four issues from the challenger have been addressed:

1. **CRITICAL (bidirectional compatibility):** Added D9 (compatibility resolution rule), added AC-33 (warning note on lateral tracks), revised AC-56 (documents one-directional claims), revised Test Strategy item 10 (specific known asymmetries), added OQ-D (escalation recommendation), added edge case row for lateral_track + canyon.

2. **MAJOR (tunnel_push speed scaling Y-axis):** Revised D4 to cover all affected axes, revised AC-40 to explicitly state Z + Y scaling with concrete numbers, added Test Strategy item 13 (speed scaling cross-check), added edge case row for speed=2.0 Y-axis surprise.

3. **MINOR (preservation policy):** Added D10 (preservation policy), added AC-61 (preservation check), added Test Strategy item 17.

4. **MINOR (file existence):** Added note under "Files Modified" table, updated File Placement to note "(or CREATED)".

I ask the Challenger to verify these revisions and approve if satisfied.

---

## Round 4 — spec_challenger

Let me verify the remaining data claims before converging.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-030/output.md",
  "offset": "20",
  "limit": "80"
}
[Tool Result]     20→export const flyoverGlide: CameraPathPreset;
    21→```
    22→
    23→### Spatial Parameters (Constants)
    24→
    25→These are the defining spatial values for the preset at `speed = 1.0`. They are **module-private named constants** (not exported). They are tested indirectly via `defaultStartState`, `defaultEndState`, and the spatial behavior acceptance criteria. OBJ-062 modifies them in-source during visual tuning rounds.
    26→
    27→| Parameter | Value | Rationale |
    28→|-----------|-------|-----------|
    29→| `Y_CAMERA` | `8` | Elevated above ground plane. Flyover geometry places ground at approximately Y=-2; this gives ~10 units of clearance — high enough for aerial feel without losing ground detail. |
    30→| `Z_START` | `5` | Camera starts slightly in front of origin, consistent with Three.js default camera convention. |
    31→| `Z_END` | `-25` | 30 world-units of forward travel. Provides substantial forward motion for scenes up to ~15s without feeling rushed.... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "offset": "15",
  "limit": "80"
}
[Tool Result]     15→
    16→/**
    17→ * Camera translates along the NEGATIVE X-axis (right to left in screen space).
    18→ * The camera starts at a positive X offset and ends at a negative X offset,
    19→ * producing apparent scene motion from left to right.
    20→ *
    21→ * lookAt is static, offset slightly toward the travel direction by
    22→ * lookAtLeadX, creating subtle anticipatory framing rather than a
    23→ * flat perpendicular view.
    24→ *
    25→ * Y and Z positions are constant. FOV is constant at 50 degrees.
    26→ */
    27→export const lateralTrackLeft: CameraPathPreset;
    28→
    29→/**
    30→ * Mirror of lateral_track_left. Camera translates along the POSITIVE X-axis
    31→ * (left to right in screen space). The camera starts at a negative X offset
    32→ * and ends at a positive X offset.
    33→ *
    34→ * lookAt leads toward positive X.
    35→ */
    36→export const lateralTrackRight: CameraPathPreset;
    37→```
    38→
    39→### Spatial Parameters
    4... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-028/output.md",
  "offset": "94",
  "limit": "60"
}
[Tool Result]     94→
    95→**Important:** `maxDisplacementX = 6` describes camera *positional* displacement only. It does NOT account for the additional frustum sweep caused by the lookAt rotation (~22 degrees across the full track). OBJ-040 MUST sample `evaluate()` at multiple `t` values to compute actual frustum coverage at each plane's depth, rather than relying solely on `maxDisplacementX` for per-plane calculations.
    96→
    97→### Compatible Geometries
    98→
    99→```typescript
   100→compatibleGeometries: ['stage', 'canyon', 'diorama', 'portal', 'panorama']
   101→```
   102→
   103→**Rationale for each:**
   104→- **`stage`** — Classic tracking shot past a subject against a backdrop. The primary use case.
   105→- **`canyon`** — Tracking between tall walls. X displacement slides past the walls, revealing depth.
   106→- **`diorama`** — Lateral motion across layered planes produces strong parallax separation — the defining visual of a diorama.
   107→- **`portal`** — Lateral track acr... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": "40",
  "limit": "110"
}
[Tool Result]     40→| Field | Value | Rationale |
    41→|-------|-------|-----------|
    42→| `name` | `'flyover'` | Matches seed Section 4.2 naming |
    43→| `description` | `'Aerial bird\'s-eye view. Large ground plane below with perspective foreshortening, sky backdrop above, and optional landmark elements rising from the terrain. Camera glides forward for a flyover effect. Best for landscapes, travel, and environment themes.'` | Describes the spatial feel per OBJ-005's `description` contract |
    44→| `default_camera` | `'slow_push_forward'` | The only verified forward-motion camera preset (OBJ-027). Produces a valid flyover-like effect with ground foreshortening. When `flyover_glide` is defined and verified, `default_camera` should be updated to `'flyover_glide'` for the full elevated-perspective aerial feel. See D3. |
    45→| `compatible_cameras` | `['static', 'flyover_glide', 'slow_push_forward', 'slow_pull_back', 'gentle_float']` | See D3. |
    46→| `fog` | `{ color: '#b8c6d4', near: ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "offset": "15",
  "limit": "135"
}
[Tool Result]     15→import { registerGeometry } from './registry';
    16→```
    17→
    18→The module defines and registers a single `SceneGeometry` object with the following structure:
    19→
    20→#### Geometry Name
    21→```
    22→name: 'canyon'
    23→```
    24→
    25→#### Slots
    26→
    27→The canyon geometry defines **6 slots**. The spatial concept: two tall, deep wall planes forming a narrow corridor, a floor extending into depth, an open sky visible above, and an optional end wall providing a visual terminus. An optional `subject` slot places a focal element within the canyon.
    28→
    29→Each slot object is constructed with all fields required by both the `PlaneSlot` interface (from OBJ-005, for `registerGeometry()`) and the `DepthSlot` metadata fields from OBJ-007 (`name`, `promptGuidance`, `expectsAlpha`). TypeScript's structural typing allows a single object literal to satisfy both interfaces. The `SceneGeometry.slots` record is typed as `Record<string, PlaneSlot>` for the... [truncated]
All data verified against source specs. Let me do final verification of the four fixes:

**Issue 1 (CRITICAL — bidirectional compatibility):** ✓ Verified.
- D9 added with clear resolution rule (geometry is authoritative)
- AC-33 requires warning note on lateral tracks re: canyon
- AC-56 revised to require documentation of one-directional claims
- Test Strategy item 10 lists specific known asymmetries
- Camera summary table drops canyon from lateral track row (shows "*(see notes)*")
- OQ-D added for upstream escalation
- Edge case table includes lateral_track + canyon scenario

**Issue 2 (MAJOR — tunnel_push Y-axis scaling):** ✓ Verified.
- D4 revised with explicit all-axes language and tunnel_push example showing Z + Y
- AC-40 revised: "scales Z displacement **and Y-axis rise amplitude proportionally**. Default 1.0 = 25 units of Z travel, 0.3 units of Y rise. speed=0.5 → 12.5 units Z, 0.15 units Y rise."
- Test Strategy item 13 added with per-preset speed scaling cross-checks
- Edge case table includes speed=2.0 Y-axis surprise

**Issue 3 (MINOR — preservation policy):** ✓ Verified.
- D10 added with explicit preservation rule and exception clause
- AC-61 added
- Test Strategy item 17 added

**Issue 4 (MINOR — file existence):** ✓ Verified.
- File existence note added under "Files Modified" table
- File Placement updated with "(or CREATED)" notation

No new issues introduced by the revisions. The spec is accurate, implementable, and stays within scope.

CONCLUSION:

The spec for OBJ-071 is approved. It defines the expansion of SKILL.md geometry and camera reference sub-files with full sections for verified geometries (tunnel, canyon, flyover) and verified cameras (lateral_track_left, lateral_track_right, tunnel_push_forward, flyover_glide), with clear data sourcing from verified dependency specs, a compatibility resolution rule (D9) for handling bidirectional mismatches, preservation policy for existing OBJ-070 content, and comprehensive cross-check test strategy.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-071/output.md",
  "content": "# Specification: OBJ-071 \u2014 SKILL.md Geometry and Camera Reference Sections\n\n## Summary\n\nOBJ-071 fills in the geometry and camera reference sub-files (`docs/skill/geometry-reference.md` and `docs/skill/camera-reference.md`) created as scaffolding by OBJ-070. OBJ-070 established the document architecture and provided a full section for the `stage` geometry and full sections for `slow_push_forward`, `slow_pull_back`, `static`, and `gentle_float` cameras, with stub sections for everything else. OBJ-071 expands stubs to full sections for all verified geometries (`tunnel`, `canyon`, `flyover`) and all verified camera presets (`lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, `flyover_glide`), updates the SKILL.md summary tables to reflect the new content, and updates the complete annotated example in SKILL.md to use at least one newly-documented geometry. Stub sections remain for unverified geometries and cameras. This objective is the primary blocker for OBJ-056 (manifest generation via Claude API), which requires comprehensive reference documentation for LLM-driven authoring.\n\n## Interface Contract\n\nOBJ-071 is a documentation objective. Its \"interface\" is the content structure of Markdown files. No TypeScript code is produced.\n\n### Files Modified (or Created)\n\n| File | Action | Content Added |\n|------|--------|---------------|\n| `docs/skill/geometry-reference.md` | Modify | Full sections for `tunnel`, `canyon`, `flyover`. Update stubs for `diorama`, `portal`, `panorama`, `close_up` with verified slot names where available. |\n| `docs/skill/camera-reference.md` | Modify | Full sections for `lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, `flyover_glide`. Update stubs for `dramatic_push`, `crane_up`, `dolly_zoom` with seed descriptions. |\n| `SKILL.md` | Modify | Update geometry summary tab
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-071/output.md
Now update the meta.json:
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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-071/meta.json",
  "content": "{\n  \"id\": \"OBJ-071\",\n  \"description\": \"SKILL.md geometry and camera reference sections -- per-geometry documentation (description, slots, when to use, visual effect), per-camera-path documentation (description, motion type, compatible geometries, when to use). At minimum covers stage and tunnel geometries in detail. Per Section 4.9.\",\n  \"category\": \"integration\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:15:00Z\",\n  \"depends_on\": [\"OBJ-070\", \"OBJ-005\", \"OBJ-006\", \"OBJ-018\", \"OBJ-019\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"notes\": \"Tier 5 integration. High priority. OBJ-056 (manifest generation via Claude API) depends on this. Spec covers full sections for tunnel/canyon/flyover geometries and lateral_track/tunnel_push_forward/flyover_glide cameras. Stubs for unverified geometries and cameras. Includes D9 compatibility resolution rule for lateral_track/canyon asymmetry.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-071/meta.json has been updated successfully.

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-071/output.md nodes/OBJ-071/meta.json && git commit -m \"OBJ-071: Spec for SKILL.md geometry and camera reference sections\n\nExpands geometry-reference.md with full sections for tunnel (OBJ-019),\ncanyon (OBJ-020), flyover (OBJ-021). Expands camera-reference.md with\nfull sections for lateral_track_left/right (OBJ-028), tunnel_push_forward\n(OBJ-029), flyover_glide (OBJ-030). Stubs retained for unverified\ngeometries (diorama, portal, panorama, close_up) and cameras\n(dramatic_push, crane_up, dolly_zoom).\n\nKey design decisions:\n- D9: Geometry is authoritative for validation when camera/geometry\n  compatibility claims are one-directional (lateral_track claims canyon\n  but canyon doesn't reciprocate)\n- D4: Speed scaling docs cover all affected axes per preset\n  (tunnel_push scales Z + Y, flyover_glide scales Z only)\n- D10: Preservation policy for existing OBJ-070 content\n\n61 acceptance criteria. 17 implementer tests.\""
}
[Tool Result] [master de8ffe4] OBJ-071: Spec for SKILL.md geometry and camera reference sections
 2 files changed, 466 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-071/output.md
Spec committed. The deliberation is complete. The final specification for OBJ-071 covers:

- **3 full geometry sections** (tunnel, canyon, flyover) with slot tables, compatible cameras, fog settings, transparency requirements, aspect ratio guidance, and image generation tips — all cross-checked against verified source specs
- **4 full camera sections** (lateral_track_left/right, tunnel_push_forward, flyover_glide) with motion descriptions, speed scaling behavior per-axis, compatible geometries, and default easings
- **D9 compatibility resolution rule** handling the lateral_track ↔ canyon one-directional claim transparently
- **61 acceptance criteria** and **17 implementer cross-check tests** ensuring data accuracy against source specs
