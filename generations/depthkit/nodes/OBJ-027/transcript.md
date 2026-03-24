# Deliberation Transcript: OBJ-027

---

## Round 1 — spec_author

Looking at the objective metadata, seed sections, and the OBJ-006 dependency spec, let me propose the specification for OBJ-027.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


Let me check the current state of relevant files to understand the existing implementation context.
[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-027/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-006/output.md",
  "limit": 50
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-005/output.md",
  "limit": 100
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-026/output.md",
  "limit": 100
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: ToolSearch]
  Input: {
  "query": "select:Bash,Glob",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}, {'type': 'tool_reference', 'tool_name': 'Glob'}]

[Tool: Bash]
  Input: {
  "command": "find . -type d -name \"nodes\" 2>/dev/null | head -5",
  "description": "Find nodes directory location"
}

[Tool: Glob]
  Input: {
  "pattern": "**/OBJ-027/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/OBJ-006/output.md"
}
[Tool Result] ./nodes
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/OBJ-026/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md

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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md"
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
Now let me check the OBJ-005 geometry contract spec to understand the geometry slots and compatible geometries:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md"
}
[Tool Error] File content (10960 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "limit": 150
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
  "offset": 150,
  "limit": 100
}
[Tool Result]    150→   */
   151→  default_camera: string;
   152→
   153→  /**
   154→   * Optional Three.js fog configuration for this geometry.
   155→   * When present, the renderer adds fog to the scene.
   156→   * Can be overridden per-scene in the manifest.
   157→   */
   158→  fog?: FogConfig;
   159→
   160→  /**
   161→   * Human-readable description of this geometry's visual character.
   162→   * Must be non-empty. Used in SKILL.md documentation. Should describe
   163→   * the spatial feel and typical use case, not the technical layout.
   164→   * Example: "A corridor with floor, ceiling, and walls receding to
   165→   * a vanishing point. Camera pushes forward for a 'traveling through
   166→   * a space' effect."
   167→   */
   168→  description: string;
   169→
   170→  /**
   171→   * Suggested aspect ratio for this geometry.
   172→   * 'landscape' means it's designed for 16:9,
   173→   * 'portrait' means 9:16,
   174→   * 'both' means it works well in either orientation.
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

[Tool: Glob]
  Input: {
  "pattern": "**/OBJ-018/output.md"
}
[Tool Result] No files found
OBJ-018 (stage geometry) is in_progress and has no output yet. That's fine — I have enough context. Let me now propose the full specification for OBJ-027.

---

# Proposed Specification: OBJ-027 — Push/Pull Camera Path Presets

## Summary

OBJ-027 defines two camera path presets — `slow_push_forward` and `slow_pull_back` — the defining camera motions for 2.5D projection. `slow_push_forward` moves the camera from its start position toward negative Z, creating the "moving into the scene" effect where WebGL's perspective projection naturally produces foreshortening, vanishing points, and depth separation. `slow_pull_back` is the mathematical mirror: same trajectory reversed, creating a "revealing the scene" effect as the camera retreats. Both implement the `CameraPathPreset` interface from OBJ-006 and share a common internal path function, differing only in the mapping of `t=0`/`t=1` to start/end positions. One specification covers both because they are structurally identical save for direction.

## Interface Contract

### Exported Presets

```typescript
// src/camera/presets/push_pull.ts

import { CameraPathPreset } from '../types';

/**
 * slow_push_forward — Camera moves from z=5 toward z=-3 along
 * the Z axis (default speed=1.0, 8 world units of displacement).
 * lookAt is fixed at [0, 0, -30], deep in the scene.
 * FOV is static at 50°.
 *
 * This is the defining 2.5D motion. As the camera pushes forward,
 * planes at different Z-depths undergo differential perspective
 * shift — near planes grow faster, far planes grow slower —
 * producing the parallax depth illusion natively via WebGL's
 * perspective projection matrix.
 *
 * The default easing is ease_in_out, producing a cinematic feel
 * where the camera gently accelerates, sustains, and gently
 * decelerates. Linear easing feels robotic; ease_in_out feels
 * like a dolly on a track.
 */
export const slowPushForward: CameraPathPreset;

/**
 * slow_pull_back — Mathematical mirror of slow_push_forward.
 * Camera starts at z=-3 and retreats to z=5.
 * lookAt remains fixed at [0, 0, -30].
 * FOV is static at 50°.
 *
 * Creates a "scene reveal" — the viewer begins close to the
 * subject/environment and gradually pulls back to reveal the
 * full spatial arrangement. Effective for opening shots and
 * establishing context after a close-up.
 */
export const slowPullBack: CameraPathPreset;
```

### Preset Values — `slow_push_forward`

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'slow_push_forward'` | Seed Section 4.3 naming |
| `description` | `'Camera pushes forward along the Z axis into the scene. The defining 2.5D motion — produces natural parallax through perspective projection.'` | |
| `defaultEasing` | `'ease_in_out'` | Cinematic dolly feel. Seed 4.3: listed with no explicit easing, but TC-09 asserts eased > linear. ease_in_out is the standard "dolly" feel. |
| `defaultStartState.position` | `[0, 0, 5]` | Three.js default camera position per seed Section 8.1. Camera begins in front of the scene. |
| `defaultStartState.lookAt` | `[0, 0, -30]` | Fixed deep target. At 35 units from start, produces nearly straight-on viewing angle with minimal tilt change during push. |
| `defaultStartState.fov` | `50` | Seed Section 8.2 default |
| `defaultEndState.position` | `[0, 0, -3]` | 8 units of Z displacement at speed=1.0. Camera ends well inside the scene but does not reach the typical midground (z=-15) or subject (z=-5) positions defined in seed Section 4.1. |
| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target — lookAt does not move. |
| `defaultEndState.fov` | `50` | No FOV animation |
| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | All geometries where forward Z motion is meaningful. Excludes `panorama` (rotation-based, not translation-based). |
| `tags` | `['push', 'forward', 'z_axis', 'depth', 'cinematic', 'defining_motion']` | |

### Preset Values — `slow_pull_back`

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'slow_pull_back'` | Seed Section 4.3 naming |
| `description` | `'Camera pulls back along the Z axis away from the scene. Reveals the full spatial arrangement. The reverse of slow_push_forward.'` | |
| `defaultEasing` | `'ease_in_out'` | Same dolly feel, reversed direction |
| `defaultStartState.position` | `[0, 0, -3]` | Begins where push_forward ends |
| `defaultStartState.lookAt` | `[0, 0, -30]` | Same fixed target |
| `defaultStartState.fov` | `50` | |
| `defaultEndState.position` | `[0, 0, 5]` | Ends where push_forward begins |
| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target |
| `defaultEndState.fov` | `50` | |
| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | Same as push_forward — same trajectory, different direction. |
| `tags` | `['pull', 'back', 'z_axis', 'reveal', 'cinematic']` | |

### OversizeRequirements (shared by both presets)

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement |
| `maxDisplacementY` | `0` | No vertical displacement |
| `maxDisplacementZ` | `8` | Total Z travel: from z=5 to z=-3 = 8 world units at speed=1.0 |
| `fovRange` | `[50, 50]` | FOV is constant |
| `recommendedOversizeFactor` | `1.4` | See D3 for derivation |

### evaluate() Behavior

```typescript
evaluate(t: number, params?: CameraParams): CameraFrameState
```

#### Core motion model

Both presets use a single-axis linear interpolation on Z, modulated by the resolved easing function:

```
For slow_push_forward:
  startZ = 5
  endZ   = 5 - (8 * speed)     // speed scales displacement per OBJ-006 D3
  easedT = easing(t)
  camZ   = startZ + (endZ - startZ) * easedT
         = 5 - (8 * speed * easedT)

  position(t) = [0, 0, camZ]
  lookAt(t)   = [0, 0, -30]     // constant
  fov(t)      = 50               // constant

For slow_pull_back:
  startZ = 5 - (8 * speed)     // mirror: starts where push ends
  endZ   = 5
  easedT = easing(t)
  camZ   = startZ + (endZ - startZ) * easedT
         = (5 - 8*speed) + (8 * speed * easedT)

  position(t) = [0, 0, camZ]
  lookAt(t)   = [0, 0, -30]     // constant
  fov(t)      = 50               // constant
```

#### CameraParams handling

- **`speed`**: Scales total Z displacement. `speed=0.5` → 4 units of travel. `speed=2.0` → 16 units. Resolved via `resolveCameraParams()`. Must be > 0.
- **`easing`**: Replaces the default `ease_in_out` for the Z interpolation. Resolved via `resolveCameraParams()`.
- **`offset`**: Not handled inside `evaluate()`. Applied by the renderer post-evaluate, per OBJ-006 D2.

#### `defaultStartState` / `defaultEndState` consistency

The static metadata corresponds to `evaluate(0)` and `evaluate(1)` with default params (speed=1.0, ease_in_out easing). Since easing(0) = 0 and easing(1) = 1 for all valid easing functions, the boundary values are easing-independent:

- `evaluate(0, defaults)` → `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }` = `defaultStartState` ✓
- `evaluate(1, defaults)` → `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }` = `defaultEndState` ✓

This holds because all valid easing functions satisfy `easing(0) = 0` and `easing(1) = 1`.

### Module Exports

```typescript
// src/camera/presets/push_pull.ts
export { slowPushForward, slowPullBack };
```

### Registry Integration

The assembly module imports both presets and registers them under keys `'slow_push_forward'` and `'slow_pull_back'`. Registry assembly is not this objective's responsibility. Keys must match each preset's `name` field.

## Design Decisions

### D1: Fixed lookAt at [0, 0, -30] — not tracking with camera

**Decision:** The lookAt target is a constant [0, 0, -30] for all values of `t`, regardless of camera position.

**Alternatives considered:**
- **Tracking lookAt** (e.g., `lookAt.z = camZ - 35`): Camera always points exactly down -Z. Viewing direction is perfectly constant. Mathematically cleaner.
- **Fixed lookAt at origin** [0, 0, 0]: Viewing angle changes significantly as camera moves — tilts progressively downward (in the -Z sense) as camera passes origin.

**Rationale for fixed [0, 0, -30]:** A fixed lookAt deep in the scene produces a very slight, natural viewing-angle shift as the camera pushes forward. At the start (z=5), the camera-to-target distance is 35 units; at the end (z=-3), it's 27 units. The angular change is approximately `atan(0/35) - atan(0/27) = 0` on X and Y since both camera and lookAt are on the Z axis — the angle in the XZ/YZ planes doesn't actually change for a pure Z push. The camera simply points more "into" the scene as it approaches. This is physically correct for a dolly on a straight track looking at a fixed point ahead.

Choosing z=-30 specifically: this is in the vicinity of the `back_wall` depth slot (seed Section 4.1). The lookAt is always deeper than the camera's end position (-3), ensuring the camera never looks "behind itself." A very deep lookAt (e.g., z=-100) would make the viewing direction nearly identical to a tracking lookAt; z=-30 is a reasonable compromise that creates a natural focal anchor within the scene's spatial range.

### D2: 8 world units of Z displacement at speed=1.0

**Decision:** Default displacement is 8 units (z=5 to z=-3).

**Rationale:** The displacement must balance three concerns:
1. **Perceptible depth effect** — Too little displacement (e.g., 2 units) and the parallax effect is barely noticeable. The whole point of this preset is to showcase the 2.5D projection.
2. **Safety with typical geometries** — Too much displacement and the camera collides with or passes through scene planes. The near_fg slot is at z=-1 (seed Section 4.1); the camera ends at z=-3, which is 2 units past near_fg. However, near_fg planes are typically edge-framing elements expected to be partially off-screen or transparent. The subject slot at z=-5 remains 2 units in front of the end position.
3. **Controllable via speed** — At speed=0.5 (4 units, z=5 to z=1), the push is very conservative — camera stays well clear of all planes. At speed=1.5 (12 units, z=5 to z=-7), the camera passes beyond the subject slot. OBJ-040 validates edge reveals per geometry and flags unsafe speed values.

**Visible area change at key planes (speed=1.0, FOV=50°):**

| Plane (Z) | Distance at start (z=5) | Distance at end (z=-3) | Visible height ratio | Apparent size change |
|-----------|------------------------|----------------------|---------------------|---------------------|
| sky (z=-50) | 55 | 47 | 1.17 | +17% |
| back_wall (z=-30) | 35 | 27 | 1.30 | +30% |
| midground (z=-15) | 20 | 12 | 1.67 | +67% |
| subject (z=-5) | 10 | 2 | 5.00 | +400% |
| near_fg (z=-1) | 6 | 2 (*behind* camera) | N/A | Behind camera |

The near_fg plane passes behind the camera during the push. This is expected — near_fg elements are foreground framing (particles, foliage edges) designed to slide out of view. Geometries that use near_fg with this preset should mark near_fg as non-required or accept that it's a transient framing element.

The subject plane has a 5x size change — dramatic, which is the point. Subjects will grow from "context" framing to "close focus" as the camera pushes in. OBJ-040 must validate that subject planes are oversized enough or that the geometry accepts the framing change.

### D3: recommendedOversizeFactor = 1.4

**Decision:** The single-scalar convenience factor is 1.4.

**Derivation:** The recommended oversize factor is defined by OBJ-006 as "sufficient to prevent edge reveals for ALL planes in all compatible geometries, assuming planes are sized to the frustum at their distance from the camera's start position and speed=1.0."

For planes sized to the visible frustum at the camera's start position:
- A plane at distance `d` from the start position is sized to `visible_height = 2 * d * tan(25°)`.
- At the camera's end position, the distance is `d - 8` (for planes deeper than z=-3).
- The actual visible height at the end is `2 * (d - 8) * tan(25°)` — but this is **smaller** than at the start because the camera is closer and the frustum is narrower at that distance.

Wait — this is wrong. The visible area at a given plane depends on the camera's distance TO that plane. As the camera gets closer to a plane, the plane needs to be LARGER to fill the (now wider) frustum at that close distance. Let me recalculate:

Plane sized to fill the frustum at start distance `d`:
- Size = `2 * d * tan(25°)`

Visible area at end distance `d - 8`:
- Required size = `2 * (d - 8) * tan(25°)` — NO, this would be smaller.

Actually, I was confusing myself. The visible AREA at a given distance from the camera is `2 * distance * tan(FOV/2)`. A plane at distance `d` at start, sized to `2 * d * tan(25°)`, exactly fills the view. When the camera moves 8 units closer, the plane is now at distance `d - 8`. The visible area at distance `d - 8` is `2 * (d - 8) * tan(25°)`. The plane is still `2 * d * tan(25°)` wide. The plane is now **larger than the visible area** — it overflows the viewport. So the plane has **more** coverage, not less. No edge reveal!

This is because pushing the camera closer to a plane makes the plane appear LARGER relative to the viewport. The edge-reveal risk is for planes that are **behind** the camera's starting position or for planes at the **periphery** that the camera moves away from laterally.

For pure Z-axis motion, the only edge-reveal risk is:
1. **Planes far from the camera**: As the camera moves forward, planes behind the camera's start position (z > 5) would move further away and appear smaller. But no standard planes are at z > 5.
2. **Lateral edge reveal**: As the camera moves closer to a plane, the visible WIDTH at that plane increases. A plane that was exactly viewport-width at start distance `d` would need to be `d / (d - 8)` times wider at end distance `d - 8` to still fill the view.

So the oversize factor for a plane at distance `d` is `d / (d - 8)`:
- back_wall (d=35): 35/27 = 1.30
- midground (d=20): 20/12 = 1.67
- subject (d=10): 10/2 = 5.0

For background planes (d >= 20), a factor of 1.4 is insufficient for midground (needs 1.67). However, the `recommendedOversizeFactor` per OBJ-006 says it must be sufficient for "ALL planes in all compatible geometries." A factor of 5.0 (for the subject plane) is impractical.

**Revised approach:** The `recommendedOversizeFactor` is meant as a safe upper bound for common use. I'll set it to **1.3** and document clearly that this covers background/far-midground planes only. OBJ-040 MUST compute per-plane factors using the displacement metadata for nearer planes. The scalar is a convenience for simple sizing, not a substitute for per-plane validation.

Actually, re-reading OBJ-006: "A single scalar >= 1.0 that is sufficient to prevent edge reveals for ALL planes in all compatible geometries." This is an impossible requirement if taken literally for a push preset where near planes need 5x oversizing. 

Looking at OBJ-026 (static), it sets `recommendedOversizeFactor = 1.0` because there's no motion. For the push, let me think about what's practical.

The issue is that the recommended factor is supposed to be a safe upper bound for ALL planes. For planes that the camera approaches very closely (subject at d=10, ending at d=2), the factor would be 5.0. That's too large for distant planes (they'd be 5x oversized unnecessarily).

I think the intent is that `recommendedOversizeFactor` covers the **common case** — background and midground planes — and that close-approach planes are handled by OBJ-040's per-plane calculation. Let me set it to **1.7** as a reasonable bound that covers midground (1.67) and everything farther, while acknowledging that subject/near_fg planes need per-plane OBJ-040 validation.

Actually, let me re-read OBJ-006 one more time on this... "A single scalar >= 1.0 that is sufficient to prevent edge reveals for ALL planes in all compatible geometries, assuming planes are sized to the frustum at their distance from the camera's start position and speed=1.0."

If I take this literally, the factor must be the worst case across all planes across all compatible geometries. For a tunnel geometry where all planes are walls/floors (the camera moves alongside them, not toward them), the oversize factor is different. For a stage geometry with a subject at z=-5 and camera approaching to z=-3, the factor is 5.0.

I think the practical answer is: set it to the worst case that geometry authors should plan for (say 1.7 for midground-distance planes), document that it does NOT cover close-approach planes (subject/near_fg), and state that OBJ-040 must be the authoritative edge-reveal validator.

Alternatively, I could reduce the displacement to make the factor more uniform. But 8 units is already a compromise.

Let me just set `recommendedOversizeFactor = 1.7` with clear documentation that this covers planes at midground distance (20 units from start) and farther. Subject and near_fg planes at closer distances require per-plane factors computed by OBJ-040. This is an acknowledged limitation of the single-scalar model — OBJ-006's Open Questions could address adding per-slot-category factors in the future.

OK, I've spent enough time on this. Let me finalize the spec.

### D4: Panorama excluded from compatible geometries

**Decision:** Both presets exclude `panorama` from `compatibleGeometries`.

**Rationale:** Panorama geometry (seed Section 4.2) uses a wide backdrop with camera rotation (panning), not translation. A forward Z push on a panorama creates an inappropriate approach toward the cylindrical backdrop rather than the intended panning motion. The panorama geometry has its own rotation-based camera presets. Including panorama would produce a technically renderable but visually wrong result — violating C-06 (blind-authorable correctness).

### D5: Both presets in a single file — shared internal helper

**Decision:** Both presets live in `src/camera/presets/push_pull.ts` and share a common internal interpolation function. They are structurally identical — the only difference is which end of the trajectory is `t=0` vs `t=1`.

**Rationale:** The seed metadata states "These are mathematical mirrors with swapped start/end positions; one spec covers both." Sharing an internal helper prevents drift between the two presets and makes the mirror relationship explicit. The internal helper is not exported — only the two `CameraPathPreset` objects are.

### D6: No Y-axis drift — pure Z-axis motion

**Decision:** Position interpolates only on Z. X and Y remain at 0 throughout.

**Alternatives considered:** Seed Section 8.5 shows a slight Y drift (`camY` from 0 to 0.5) alongside the Z push. This adds a subtle "rising as you approach" feel.

**Rationale for excluding:** The Y drift in the seed is an illustrative example, not a definition of `slow_push_forward`. Multi-axis motion belongs to presets like `gentle_float` (OBJ-031) or `crane_up` (OBJ-033). Keeping push/pull as pure Z-axis makes them composable: an author who wants Z push + Y drift can apply `CameraParams.offset` for static Y shift, or a future camera composition system (OQ-06) could chain push + rise. Single-axis motion is also easier to reason about for blind authoring (C-06) — "the camera moves forward" is unambiguous.

### D7: ease_in_out as default easing (not linear)

**Decision:** Default easing is `ease_in_out`.

**Rationale:** TC-09 asserts that eased camera paths feel more natural than linear. A physical camera dolly accelerates from rest, sustains, and decelerates to rest. `ease_in_out` maps this directly. Linear motion feels robotic — like a constant-speed conveyor belt rather than a cinematographer's dolly push. The author can override to `linear` via `CameraParams.easing` if desired.

### D8: Return a new object per evaluate() call

**Decision:** Each call to `evaluate()` returns a freshly constructed `CameraFrameState` object with new `Vec3` arrays for position and lookAt.

**Rationale:** Per OBJ-026 Open Question 3, returning a shared/cached object risks mutation by consumers (e.g., the renderer adding offset to position). Unlike the static preset where the return value never varies, push/pull presets return different positions for different `t` values, so caching would require a per-t lookup — more complex than simply constructing a new object. Fresh objects eliminate mutation hazards with zero meaningful performance cost (the object is three small arrays and a number).

## Acceptance Criteria

### Contract Conformance (OBJ-006 test pattern)

- [ ] **AC-01:** `slowPushForward.evaluate(0)` returns `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-02:** `slowPushForward.evaluate(1)` returns `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-03:** `slowPushForward.evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-04:** `slowPushForward.evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-05:** `slowPullBack.evaluate(0)` returns `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-06:** `slowPullBack.evaluate(1)` returns `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-07:** `slowPullBack.evaluate(0)` matches its `defaultStartState` within 1e-6.
- [ ] **AC-08:** `slowPullBack.evaluate(1)` matches its `defaultEndState` within 1e-6.
- [ ] **AC-09:** For both presets, `evaluate(t)` at 100 evenly-spaced `t` in [0,1] returns no NaN, no Infinity, and FOV in (0, 180).
- [ ] **AC-10:** 1000 calls to `evaluate(0.5)` with the same params produce identical results (determinism, C-05).

### Mirror Relationship

- [ ] **AC-11:** `slowPushForward.defaultStartState` deep-equals `slowPullBack.defaultEndState`.
- [ ] **AC-12:** `slowPushForward.defaultEndState` deep-equals `slowPullBack.defaultStartState`.
- [ ] **AC-13:** For every `t` in {0, 0.25, 0.5, 0.75, 1.0}: `slowPushForward.evaluate(t).position` deep-equals `slowPullBack.evaluate(1 - t).position` (within 1e-6) when both use identical params (default params, same speed, same easing).

### Z-Axis Interpolation

- [ ] **AC-14:** `slowPushForward.evaluate(0.5)` with default params returns a Z position between 5 and -3 (exclusive). The exact value depends on `ease_in_out(0.5)` — for a symmetric ease_in_out, it should be near the midpoint `z ≈ 1`.
- [ ] **AC-15:** Z position is monotonically non-increasing across `t` in [0,1] for `slow_push_forward` with any valid easing (camera always moves forward, never reverses).
- [ ] **AC-16:** Z position is monotonically non-decreasing across `t` in [0,1] for `slow_pull_back` with any valid easing.
- [ ] **AC-17:** X and Y components of position are exactly 0 for all `t` values (pure Z-axis motion).

### lookAt and FOV Invariance

- [ ] **AC-18:** lookAt is `[0, 0, -30]` for all `t` in [0,1] for both presets.
- [ ] **AC-19:** FOV is exactly 50 for all `t` in [0,1] for both presets.

### Speed Scaling

- [ ] **AC-20:** `slowPushForward.evaluate(1, { speed: 0.5 })` returns Z position of `5 - (8 * 0.5) = 1.0`.
- [ ] **AC-21:** `slowPushForward.evaluate(1, { speed: 2.0 })` returns Z position of `5 - (8 * 2.0) = -11.0`.
- [ ] **AC-22:** The maximum Euclidean distance from start across 100 samples with `speed: 0.5` is strictly less than with `speed: 1.0` (OBJ-006 conformance pattern, speed scaling check).

### Easing Override

- [ ] **AC-23:** `slowPushForward.evaluate(0.5, { easing: 'linear' })` returns Z = `5 - (8 * 0.5) = 1.0` (linear midpoint).
- [ ] **AC-24:** `slowPushForward.evaluate(0.5, { easing: 'ease_in' })` returns a Z value > 1.0 (ease_in is slow at start, so at t=0.5 eased time < 0.5, less displacement).
- [ ] **AC-25:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in the Z position component (OBJ-006 conformance pattern, easing override check).

### Invalid Params Rejection

- [ ] **AC-26:** `evaluate(0.5, { speed: -1 })` throws an Error (via `resolveCameraParams`).
- [ ] **AC-27:** `evaluate(0.5, { speed: 0 })` throws an Error.
- [ ] **AC-28:** `evaluate(0.5, { easing: 'invalid_name' as any })` throws an Error whose message includes `'invalid_name'`.

### Preset Metadata

- [ ] **AC-29:** `slowPushForward.name` is `'slow_push_forward'` and matches `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`.
- [ ] **AC-30:** `slowPullBack.name` is `'slow_pull_back'` and matches the same regex.
- [ ] **AC-31:** Both presets have `defaultEasing` of `'ease_in_out'`.
- [ ] **AC-32:** Both presets have `compatibleGeometries` containing `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` — exactly 7 entries, excluding `panorama`.
- [ ] **AC-33:** `slowPushForward.tags` includes `'push'` and `'forward'`.
- [ ] **AC-34:** `slowPullBack.tags` includes `'pull'` and `'back'`.

### OversizeRequirements

- [ ] **AC-35:** Both presets have `maxDisplacementX === 0` and `maxDisplacementY === 0`.
- [ ] **AC-36:** Both presets have `maxDisplacementZ === 8`.
- [ ] **AC-37:** Both presets have `fovRange` of `[50, 50]`.
- [ ] **AC-38:** Both presets have `recommendedOversizeFactor === 1.7`.
- [ ] **AC-39:** All sampled FOV values (100 points) fall within `fovRange` (tolerance 1e-6).

### Full Validation

- [ ] **AC-40:** `validateCameraPathPreset(slowPushForward)` returns an empty array.
- [ ] **AC-41:** `validateCameraPathPreset(slowPullBack)` returns an empty array.

## Edge Cases and Error Handling

### evaluate() Boundary and Parameter Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState` (start of trajectory) |
| `t = 1` | Returns `defaultEndState` (end of trajectory) |
| `t = 0.5` (push, default params) | Z near midpoint of eased curve. For symmetric ease_in_out, approximately z=1 |
| `t < 0` (e.g., -0.1) | Undefined behavior per OBJ-006. Callers must clamp. Preset may extrapolate (camera position beyond start) but this is not guaranteed. |
| `t > 1` (e.g., 1.5) | Undefined behavior. Preset may extrapolate beyond end position. |
| `params = undefined` | Uses defaults: speed=1.0, ease_in_out easing. |
| `params = {}` | Same as undefined — all defaults. |
| `params = { speed: 0.001 }` | Valid. Camera moves 0.008 units — nearly imperceptible push. |
| `params = { speed: 0.5 }` | Camera moves 4 units (z=5 to z=1). Conservative, safe with all typical geometries. |
| `params = { speed: 2.0 }` | Camera moves 16 units (z=5 to z=-11). Passes through subject (z=-5) and midground (z=-15). OBJ-040 must flag edge reveals per geometry. |
| `params = { speed: 5.0 }` | Camera moves 40 units (z=5 to z=-35). Passes through most scene planes. Valid per CameraParams contract (speed > 0) but will fail OBJ-040 validation for most geometries. |
| `params = { speed: -1 }` | Throws Error via `resolveCameraParams`. |
| `params = { speed: 0 }` | Throws Error via `resolveCameraParams`. |
| `params = { easing: 'linear' }` | Valid. Linear interpolation — uniform velocity. |
| `params = { easing: 'ease_out_cubic' }` | Valid. Fast start, slow end — camera decelerates dramatically. |
| `params = { easing: 'nonexistent' }` | Throws Error via `resolveCameraParams`, listing valid names. |
| `params = { offset: [2, 0, 0] }` | Not processed inside evaluate(). Renderer applies post-evaluate. |

### Near-Plane Collision Awareness

| Scenario | Behavior |
|----------|----------|
| Camera at z=-3, near_fg plane at z=-1 | near_fg is 2 units BEHIND the camera (in front, camera-relative). Plane is between camera and lookAt. This is geometrically valid — the plane simply appears very large/close or partially clips through the near frustum. |
| Camera at z=-3, subject at z=-5 | Subject is 2 units in front of the camera. At FOV=50°, visible height at distance 2 is `2 * 2 * tan(25°) ≈ 1.86 units`. Subject plane must be at least this size or it won't fill the view. |
| Camera passes through a plane (high speed) | WebGL renders the plane from behind (showing the back face). `meshBasicMaterial` is double-sided by default. The plane appears mirror-flipped. This is a visual artifact — OBJ-040 should prevent this combination. |

### Mirror Relationship Edge Cases

| Scenario | Behavior |
|----------|----------|
| Same speed, different presets | `pushForward.evaluate(t, { speed: s })` position === `pullBack.evaluate(1-t, { speed: s })` position, for any valid `s` and `t`. |
| Different easing, mirror test | The mirror relationship holds for the same easing on both sides. Using different easings on push vs. pull breaks the symmetry — this is expected. |

## Test Strategy

### Unit Tests

**1. Boundary values:** For each preset, verify `evaluate(0)` and `evaluate(1)` match `defaultStartState` and `defaultEndState` exactly. Use per-component comparison with 1e-6 tolerance.

**2. Mirror symmetry:** For `t` in {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}, verify `pushForward.evaluate(t).position` equals `pullBack.evaluate(1-t).position` within 1e-6 (both with default params).

**3. Monotonic Z:** Sample 100 points for push_forward. Verify each successive Z value is ≤ the previous (non-increasing). Same for pull_back (non-decreasing).

**4. X/Y invariance:** For 100 sample points, verify position[0] === 0 and position[1] === 0 for both presets.

**5. lookAt/FOV invariance:** For 100 sample points, verify lookAt is exactly [0, 0, -30] and fov is exactly 50.

**6. Speed scaling:** Verify `evaluate(1, { speed: 0.5 })` gives Z = 1.0 for push_forward. Verify `evaluate(1, { speed: 2.0 })` gives Z = -11.0. Verify that max distance from start is less at speed=0.5 than at speed=1.0.

**7. Easing override:** Verify `evaluate(0.5, { easing: 'linear' })` gives Z = 1.0 (exact linear midpoint) for push_forward. Verify different easing produces different Z at t=0.5.

**8. Invalid params:** Verify throws for speed ≤ 0 and invalid easing names.

**9. Determinism:** 100 calls with same `t` and same params produce bit-identical results.

**10. OBJ-006 conformance suite:** Run the reusable conformance test pattern from `src/camera/` against both presets.

### Relevant Testable Claims

- **TC-03:** These presets are the primary vehicle for verifying that perspective projection produces convincing 2.5D. Test renders with push_forward should show walls receding to vanishing points, floors foreshortening, and depth-dependent apparent motion rates.
- **TC-04:** An LLM selects `"camera": "slow_push_forward"` — no XYZ coordinates required.
- **TC-05:** Push_forward on a tunnel geometry is the core testable claim for convincing depth. (Though OBJ-029 `tunnel_push_forward` is the specialized version, `slow_push_forward` is also tunnel-compatible.)
- **TC-09:** Comparing push_forward with `ease_in_out` vs `linear` easing validates that eased paths feel more natural.

## Integration Points

### Depends On

| Dependency | What is imported | How it's used |
|---|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `resolveCameraParams` | Both presets conform to `CameraPathPreset`. `evaluate()` calls `resolveCameraParams()` for param validation and easing resolution. |
| **OBJ-006** (`src/camera/validate.ts`) | `validateCameraPathPreset` | Used in tests to verify both presets pass full validation. |
| **OBJ-002** (`src/interpolation/`) | `EasingName`, `EasingFn` (transitively via OBJ-006) | `defaultEasing: 'ease_in_out'` uses `EasingName`. The resolved easing function is applied to `t` inside `evaluate()`. No direct import of `interpolate()` is required — the interpolation is a single lerp formula `start + (end - start) * easedT`. |
| **OBJ-003** (`src/spatial/`) | `Vec3` (transitively via OBJ-006) | Position and lookAt values are `Vec3` tuples. |

### Consumed By

| Downstream | How it uses OBJ-027 |
|---|---|
| **Registry assembly** | Imports `slowPushForward` and `slowPullBack`, registers under keys `'slow_push_forward'` and `'slow_pull_back'`. |
| **OBJ-059** (Stage geometry tuning) | `slow_push_forward` is the primary motion for stage geometry — the default visual test for "does the stage feel like you're approaching the scene?" |
| **OBJ-069** (Edge-reveal tuning) | Push/pull presets have the most significant Z displacement among common presets. Edge-reveal validation is critical. |
| **OBJ-070/071** (SKILL.md) | Documents both presets as the primary camera motions. push_forward is the recommended default for most geometries. |
| **OBJ-040** (Edge-reveal validation) | Uses `oversizeRequirements.maxDisplacementZ = 8` and the evaluate function for trajectory sampling. Must compute per-plane oversize factors since the `recommendedOversizeFactor` (1.7) does not cover close-approach planes. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatibleGeometries` — push/pull are compatible with 7 of 8 geometries (all except panorama). |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "slow_push_forward"` or `"camera": "slow_pull_back"` from manifest, calls `evaluate(t)` per frame. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t)`, applies offset, calls `toCameraState()`, sets Three.js camera position and lookAt. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        push_pull.ts     # slowPushForward and slowPullBack definitions
        static.ts        # (OBJ-026)
        index.ts         # Re-exports all presets
```

Both presets reside in a single file because they share an internal helper and are logically a single unit (mirror pair). The filename `push_pull.ts` reflects this pairing.

## Open Questions

1. **Should `recommendedOversizeFactor` be larger to cover subject-distance planes?** At speed=1.0, a subject plane at distance 10 (from start) ending at distance 2 needs a 5.0 oversize factor. The current 1.7 covers midground and farther. Setting it to 5.0 would make background planes wastefully oversized. This tension is inherent to the single-scalar model — OBJ-040's per-plane computation is the real safety mechanism. **Recommendation:** Keep 1.7, document the limitation, let OBJ-040 handle close-approach planes.

2. **Should pull_back use `ease_out_in` instead of `ease_in_out`?** A pull_back with `ease_in_out` starts slow (at the close position) and ends slow (at the far position). An `ease_out_in` would start fast and end fast, with a slow middle. For a "reveal" shot, starting with quick retreat then slowing to let the viewer absorb might be more cinematic. **Recommendation:** Keep `ease_in_out` for consistency with push_forward. The author can override via `CameraParams.easing`. The default should be the most predictable choice.

3. **Near_fg plane behavior during push.** At speed=1.0, near_fg (z=-1) ends up behind the camera (z=-3). Should the preset document a recommended max speed for geometries with near_fg planes? **Recommendation:** This is OBJ-040's responsibility. The preset provides the displacement metadata; the validator checks per-geometry safety. The SKILL.md should note that near_fg planes are designed to be transient framing elements that may exit the view during aggressive camera pushes.

---

I believe this specification is complete and ready for the Challenger to review. The key design choices are:
- **8 units of Z displacement** (z=5 to z=-3) balancing perceptibility with geometric safety
- **Fixed lookAt at [0, 0, -30]** for stable viewing angle
- **Pure Z-axis motion** keeping the presets simple and composable
- **`ease_in_out` default** for cinematic dolly feel
- **`recommendedOversizeFactor = 1.7`** covering midground+ planes, with OBJ-040 handling close-approach planes
- **Mirror relationship** making pull_back a time-reversal of push_forward

I'd like the Challenger to verify the mathematical model, the oversize factor rationale, and the compatible geometry list.

---

## Round 2 — spec_challenger

I'll review this spec carefully against the seed, OBJ-006 contract, and OBJ-026 reference.

Let me first check the OBJ-026 spec more thoroughly for consistency patterns:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md",
  "offset": "18",
  "limit": "150"
}
[Tool Result]     18→ * Camera remains at a fixed position looking at a fixed target.
    19→ * FOV does not animate. All oversizing requirements are zero.
    20→ *
    21→ * This is the canonical reference implementation of CameraPathPreset.
    22→ * Every geometry is compatible because a static camera cannot
    23→ * cause edge reveals, depth mismatches, or spatial conflicts.
    24→ */
    25→export const staticPreset: CameraPathPreset;
    26→```
    27→
    28→### Preset Values
    29→
    30→| Field | Value | Rationale |
    31→|-------|-------|-----------|
    32→| `name` | `'static'` | Matches seed Section 4.3 naming |
    33→| `description` | `'Camera at fixed position and orientation. No movement.'` | Seed Section 4.3 description verbatim |
    34→| `defaultEasing` | `'linear'` | Easing is irrelevant (no interpolation occurs), but `linear` is the simplest valid value |
    35→| `defaultStartState.position` | `[0, 0, 5]` | Three.js default camera position per seed Section 8.1 |
    36→| ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": "0",
  "limit": "80"
}
[Tool Result]      0→# Specification: Scene Geometry Type Contract (OBJ-005)
     1→
     2→## Summary
     3→
     4→OBJ-005 defines the TypeScript type system for all scene geometries in depthkit: the `PlaneSlot` interface describing a single named position in a 3D scene, the `SceneGeometry` interface describing a complete spatial arrangement of planes, the `FogConfig` interface for depth-based atmospheric fading, a geometry registry with explicit registration and deep-freeze semantics, and the slot naming conventions that all 8 geometry implementations (OBJ-018 through OBJ-025) must follow. This is a pure type/contract module — it defines the shape of geometry data, not any specific geometry's values. It imports spatial primitives from OBJ-003 and is consumed by every downstream objective that creates, validates, instantiates, or queries scene geometries.
     5→
     6→## Interface Contract
     7→
     8→### Core Types
     9→
    10→```typescript
    11→// src/scenes/geometries/types.ts
    12... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-026/output.md",
  "offset": "167",
  "limit": "100"
}
[Tool Result]    167→### Validation
   168→
   169→- [ ] **AC-24:** `validateCameraPathPreset(staticPreset)` returns an empty array (no errors).
   170→
   171→### OBJ-006 Conformance Test Pattern (all must pass)
   172→
   173→- [ ] **AC-25:** Boundary start check passes.
   174→- [ ] **AC-26:** Boundary end check passes.
   175→- [ ] **AC-27:** Continuity check (100 points, no NaN/Infinity) passes.
   176→- [ ] **AC-28:** FOV range check passes.
   177→- [ ] **AC-29:** Determinism check (100 calls, same t, same output) passes.
   178→- [ ] **AC-30:** Full `validateCameraPathPreset` passes.
   179→- [ ] **AC-31:** Speed scaling check: max Euclidean distance between `evaluate(t, { speed: 0.5 }).position` and `defaultStartState.position` over 100 samples equals 0 (both maximums are zero — the exception case in OBJ-006's conformance pattern).
   180→- [ ] **AC-32:** Easing override check: `evaluate(0.5, { easing: 'linear' })` equals `evaluate(0.5, { easing: 'ease_in' })` (the exception case for static... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": "80",
  "limit": "80"
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
Now let me check the OBJ-002 spec for easing function details:
[Tool: Glob]
  Input: {
  "pattern": "**/OBJ-002/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md",
  "offset": "0",
  "limit": "80"
}
[Tool Result]      0→# Specification: OBJ-002 — Interpolation, Easing, and Spring Utilities
     1→
     2→## Summary
     3→
     4→OBJ-002 defines the math primitives that underpin all animation in depthkit: an `interpolate()` function for mapping frame numbers to output values, a `spring()` function for organic/physics-based motion, and six named easing functions. These utilities are isomorphic — they must run identically in both the Node.js orchestrator (scene sequencer transition timing) and the headless Chromium browser (Three.js camera interpolation). This is a Tier 0 foundation with no dependencies; every camera path preset, scene transition, and FOV animation consumes these primitives.
     5→
     6→## Interface Contract
     7→
     8→### Module: `src/interpolation/easings.ts`
     9→
    10→```typescript
    11→/**
    12→ * An easing function maps normalized time t in [0,1] to eased time t' in [0,1].
    13→ * Behavior outside [0,1] is undefined (see design notes).
    14→ */
    15→exp... [truncated]
Good. I see that `ease_in_out` is quadratic: `t < 0.5 ? 2t² : 1 - (-2t+2)²/2`. Let me verify: is this symmetric? f(t) + f(1-t) should = 1 for a symmetric easing.

f(0.25) = 2*(0.25)² = 0.125
f(0.75) = 1 - (-2*0.75+2)²/2 = 1 - (0.5)²/2 = 1 - 0.125 = 0.875
Sum = 1.0 ✓ — symmetric.

Now let me formalize my review.

---

## Challenger Review — OBJ-027

### Points of Agreement (what's sound)

1. **Two presets, one file, shared helper** — structurally correct. The mirror relationship is real and one spec covering both is the right call.
2. **Pure Z-axis motion** — clean separation of concerns. D6's rationale is solid.
3. **Fixed lookAt** — correct choice. The seed's Y drift in Section 8.5 is illustrative, not prescriptive.
4. **ease_in_out default** — well-justified by TC-09 and cinematic convention.
5. **Panorama exclusion** — correct. Rotation-based geometry doesn't suit translation-based paths.
6. **Return new object per call** — sensible for non-static presets.
7. **Most acceptance criteria are specific and testable** — AC-14 through AC-25 are particularly well-constructed.

### Issues

---

#### Issue 1: OversizeRequirements are DIFFERENT for push vs. pull — cannot be shared (CRITICAL)

The spec declares shared `OversizeRequirements` for both presets with `recommendedOversizeFactor = 1.7`. This is wrong.

**For `slow_push_forward`:** The camera approaches all planes. A plane sized to fill the frustum at the camera's *start* position (farthest distance) will *overflow* the view as the camera gets closer (frustum narrows at that plane's distance). The oversize factor needed is **1.0** — no oversizing required at all for backdrop-facing planes.

**For `slow_pull_back`:** The camera retreats from all planes. A plane sized to fill the frustum at the camera's *start* position (closest distance, z=-3) will be *too small* as the camera retreats to z=5 (frustum widens at that plane's distance). For a plane at z=-30: start distance = 27, end distance = 35, factor needed = 35/27 ≈ **1.30**. For midground at z=-15: start distance = 12, end distance = 20, factor needed = 20/12 ≈ **1.67**.

The displacement values (`maxDisplacementZ = 8`) are identical, but `recommendedOversizeFactor` should differ because the *direction* of motion matters. Push approaches planes (safe), pull retreats (needs oversizing).

**Proposed fix:** Each preset gets its own `OversizeRequirements`:

- `slowPushForward.oversizeRequirements.recommendedOversizeFactor = 1.0` (camera approaches all planes — no edge-reveal risk for standard facing-camera planes)
- `slowPullBack.oversizeRequirements.recommendedOversizeFactor = 1.7` (camera retreats — planes at midground distance and farther need this margin; closer planes need OBJ-040 per-plane computation)

All other fields (`maxDisplacementX/Y/Z`, `fovRange`) remain shared at the same values.

---

#### Issue 2: D3 derivation is a stream-of-consciousness mess, not a clean spec (MAJOR)

D3 contains visible self-correction, confusion, and "wait, this is wrong" moments. The spec is a deliverable to an implementer, not a thinking-out-loud notebook. An implementer reading D3 would be confused about what the final answer actually is and whether the author trusts their own math.

**Proposed fix:** Replace D3 entirely with a clean derivation that:
1. States the formula: for a plane at distance `d_start` from camera start and `d_end` from camera end, the oversize factor is `max(d_start, d_end) / min(d_start, d_end)`.
2. Notes that for push_forward, `d_start > d_end` for all planes in front of the camera, so the plane is always oversized relative to the end view — factor = 1.0.
3. Notes that for pull_back, `d_end > d_start` for all planes, so factor = `d_end / d_start`.
4. Provides the table of factors for pull_back at key plane distances.
5. States the chosen `recommendedOversizeFactor` per preset with rationale.

---

#### Issue 3: AC-13 mirror relationship only holds for symmetric easings — constraint is implicit (MAJOR)

AC-13 states: "slowPushForward.evaluate(t).position deep-equals slowPullBack.evaluate(1 - t).position (within 1e-6) when both use identical params (default params, same speed, same easing)."

The mathematical requirement is `easing(t) + easing(1-t) = 1`, which only holds for **symmetric** easings (`linear`, `ease_in_out`, `ease_in_out_cubic`). It does NOT hold for `ease_in`, `ease_out`, or `ease_out_cubic`.

AC-13 says "default params" which uses `ease_in_out` (symmetric), so it *passes*. But the spec text and the Mirror Relationship Edge Cases table says "The mirror relationship holds for the same easing on both sides" — this is misleading because it's only true for symmetric easings.

**Proposed fix:** 
1. Tighten AC-13's language: "...when both use default params (speed=1.0, easing=ease_in_out). Note: this relationship holds only for symmetric easings where `e(t) + e(1-t) = 1`. Asymmetric easings (ease_in, ease_out, ease_out_cubic) break the mirror."
2. Update the Mirror Relationship Edge Cases table to explicitly state which easings are symmetric and which aren't.

---

#### Issue 4: D1 rationale about viewing angle change is misleading (MINOR)

D1 says: "A fixed lookAt deep in the scene produces a very slight, natural viewing-angle shift as the camera pushes forward." Then immediately proves there is NO angular change: "the angle in the XZ/YZ planes doesn't actually change for a pure Z push."

For a camera moving along the Z axis looking at a point on the Z axis, the viewing direction is always (0, 0, -1) regardless of position or lookAt distance. There is zero viewing angle shift. The rationale contradicts itself.

**Proposed fix:** Remove the claim about "slight viewing-angle shift." State plainly: "For pure Z-axis motion, the viewing direction is always (0, 0, -1) regardless of lookAt distance. The lookAt target at z=-30 only matters when `CameraParams.offset` displaces the camera off-axis, in which case it anchors the viewing direction to the scene's depth center."

---

#### Issue 5: Missing edge cases for pull_back with high speed (MINOR)

The Edge Cases table documents push_forward at speed 2.0 and 5.0 but doesn't document the corresponding pull_back scenarios. For pull_back with speed=2.0: startZ = 5 - 16 = -11 (camera begins deep in the scene, behind midground). This is just as important to document.

**Proposed fix:** Add pull_back-specific rows to the edge cases table:
- `pullBack, speed: 2.0`: Camera starts at z=-11 (behind midground and subject planes). Several planes will be behind the camera at scene start.
- `pullBack, speed: 5.0`: Camera starts at z=-35 (near back_wall). Most scene planes are behind the camera initially.

---

#### Issue 6: The `defaultStartState`/`defaultEndState` for pull_back should be documented as speed-dependent in the same way as evaluate() (MINOR)

The spec correctly says `defaultStartState` for pull_back is `[0, 0, -3]` (matching push_forward's `defaultEndState`). But the evaluate() formula shows `startZ = 5 - (8 * speed)`, which only equals -3 when speed=1.0. An implementer might be confused about whether the formula or the static metadata is the source of truth.

**Proposed fix:** Add a note after the evaluate() formula clarifying: "The `defaultStartState` and `defaultEndState` are static metadata for speed=1.0 only (per OBJ-006 contract). The evaluate() function computes actual positions using the resolved speed parameter, which may differ from the static metadata when speed ≠ 1.0. OBJ-006's validation only checks evaluate(0) and evaluate(1) with default params (speed=1.0)."

---

#### Issue 7: No explicit statement about `resolveCameraParams()` being called inside evaluate() (MINOR)

OBJ-026 explicitly states in its evaluate() section: "resolveCameraParams() is called (to validate params and throw on invalid inputs)." OBJ-027's evaluate() section describes CameraParams handling but never explicitly says `resolveCameraParams()` is called first. This is implied by "Resolved via resolveCameraParams()" but should be an explicit step.

**Proposed fix:** Add to the evaluate() behavior section: "Both presets call `resolveCameraParams(params, 'ease_in_out')` at the top of evaluate() to validate and resolve params. Invalid params (speed ≤ 0, invalid easing name) cause an immediate throw, consistent with all presets per OBJ-006 D11."

---

### Summary

| # | Severity | Issue |
|---|----------|-------|
| 1 | **Critical** | OversizeRequirements differ for push vs. pull — cannot share a single factor |
| 2 | **Major** | D3 derivation is a mess — needs clean rewrite |
| 3 | **Major** | AC-13 mirror relationship is easing-dependent — needs explicit constraint |
| 4 | Minor | D1 viewing angle claim contradicts itself |
| 5 | Minor | Missing pull_back high-speed edge cases |
| 6 | Minor | defaultStartState vs evaluate() speed-dependence needs clarification |
| 7 | Minor | Missing explicit resolveCameraParams() call statement |

**Issues 1-3 must be resolved before convergence.** Please revise and I'll verify the fixes are structurally present.

---

## Round 3 — spec_author

All seven issues are valid. Let me present the revised specification with clean fixes for each.

---

# Revised Specification: OBJ-027 — Push/Pull Camera Path Presets

## Summary

OBJ-027 defines two camera path presets — `slow_push_forward` and `slow_pull_back` — the defining camera motions for 2.5D projection. `slow_push_forward` moves the camera from z=5 toward z=-3, creating the "moving into the scene" effect where WebGL's perspective projection naturally produces foreshortening, vanishing points, and depth separation. `slow_pull_back` is the mathematical mirror: same trajectory reversed, creating a "revealing the scene" effect as the camera retreats. Both implement the `CameraPathPreset` interface from OBJ-006 and share a common internal path function, differing only in the mapping of `t=0`/`t=1` to start/end positions. One specification covers both because they are structurally identical save for direction.

## Interface Contract

### Exported Presets

```typescript
// src/camera/presets/push_pull.ts

import { CameraPathPreset } from '../types';

/**
 * slow_push_forward — Camera moves from z=5 toward z=-3 along
 * the Z axis (default speed=1.0, 8 world units of displacement).
 * lookAt is fixed at [0, 0, -30], deep in the scene.
 * FOV is static at 50°.
 *
 * This is the defining 2.5D motion. As the camera pushes forward,
 * planes at different Z-depths undergo differential perspective
 * shift — near planes grow faster, far planes grow slower —
 * producing the parallax depth illusion natively via WebGL's
 * perspective projection matrix.
 *
 * The default easing is ease_in_out, producing a cinematic feel
 * where the camera gently accelerates, sustains, and gently
 * decelerates. Linear easing feels robotic; ease_in_out feels
 * like a dolly on a track.
 */
export const slowPushForward: CameraPathPreset;

/**
 * slow_pull_back — Mathematical mirror of slow_push_forward.
 * Camera starts at z=-3 and retreats to z=5.
 * lookAt remains fixed at [0, 0, -30].
 * FOV is static at 50°.
 *
 * Creates a "scene reveal" — the viewer begins close to the
 * subject/environment and gradually pulls back to reveal the
 * full spatial arrangement. Effective for opening shots and
 * establishing context after a close-up.
 */
export const slowPullBack: CameraPathPreset;
```

### Preset Values — `slow_push_forward`

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'slow_push_forward'` | Seed Section 4.3 naming |
| `description` | `'Camera pushes forward along the Z axis into the scene. The defining 2.5D motion — produces natural parallax through perspective projection.'` | |
| `defaultEasing` | `'ease_in_out'` | Cinematic dolly feel. TC-09 asserts eased > linear. ease_in_out is the standard dolly feel. |
| `defaultStartState.position` | `[0, 0, 5]` | Three.js default camera position per seed Section 8.1. |
| `defaultStartState.lookAt` | `[0, 0, -30]` | Fixed deep target. See D1. |
| `defaultStartState.fov` | `50` | Seed Section 8.2 default. |
| `defaultEndState.position` | `[0, 0, -3]` | 8 units of Z displacement at speed=1.0. See D2. |
| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target. |
| `defaultEndState.fov` | `50` | No FOV animation. |
| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | All geometries where forward Z motion is meaningful. Excludes `panorama` (rotation-based). See D4. |
| `tags` | `['push', 'forward', 'z_axis', 'depth', 'cinematic', 'defining_motion']` | |

### Preset Values — `slow_pull_back`

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'slow_pull_back'` | Seed Section 4.3 naming |
| `description` | `'Camera pulls back along the Z axis away from the scene. Reveals the full spatial arrangement. The reverse of slow_push_forward.'` | |
| `defaultEasing` | `'ease_in_out'` | Same dolly feel, reversed direction. |
| `defaultStartState.position` | `[0, 0, -3]` | Begins where push_forward ends. |
| `defaultStartState.lookAt` | `[0, 0, -30]` | Same fixed target. |
| `defaultStartState.fov` | `50` | |
| `defaultEndState.position` | `[0, 0, 5]` | Ends where push_forward begins. |
| `defaultEndState.lookAt` | `[0, 0, -30]` | Same fixed target. |
| `defaultEndState.fov` | `50` | |
| `compatibleGeometries` | `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` | Same as push_forward. |
| `tags` | `['pull', 'back', 'z_axis', 'reveal', 'cinematic']` | |

### OversizeRequirements — `slow_push_forward`

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
| `maxDisplacementY` | `0` | No vertical displacement. |
| `maxDisplacementZ` | `8` | Total Z travel: z=5 to z=-3 = 8 world units at speed=1.0. |
| `fovRange` | `[50, 50]` | FOV is constant. |
| `recommendedOversizeFactor` | `1.0` | See D3. Camera approaches all planes — no edge-reveal risk. |

### OversizeRequirements — `slow_pull_back`

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | Pure Z-axis motion, no lateral displacement. |
| `maxDisplacementY` | `0` | No vertical displacement. |
| `maxDisplacementZ` | `8` | Total Z travel: z=-3 to z=5 = 8 world units at speed=1.0. |
| `fovRange` | `[50, 50]` | FOV is constant. |
| `recommendedOversizeFactor` | `1.7` | See D3. Camera retreats from all planes — planes must be oversized to fill the widening frustum. |

### evaluate() Behavior

```typescript
evaluate(t: number, params?: CameraParams): CameraFrameState
```

Both presets call `resolveCameraParams(params, 'ease_in_out')` at the top of `evaluate()` to validate and resolve params. Invalid params (speed ≤ 0, invalid easing name) cause an immediate throw, consistent with all presets per OBJ-006 D11.

#### Core motion model

Both presets use a single-axis linear interpolation on Z, modulated by the resolved easing function:

```
For slow_push_forward:
  startZ = 5
  endZ   = 5 - (8 * speed)
  easedT = easing(t)
  camZ   = startZ + (endZ - startZ) * easedT
         = 5 - (8 * speed * easedT)

  position(t) = [0, 0, camZ]
  lookAt(t)   = [0, 0, -30]     // constant
  fov(t)      = 50               // constant

For slow_pull_back:
  startZ = 5 - (8 * speed)
  endZ   = 5
  easedT = easing(t)
  camZ   = startZ + (endZ - startZ) * easedT
         = (5 - 8*speed) + (8 * speed * easedT)

  position(t) = [0, 0, camZ]
  lookAt(t)   = [0, 0, -30]     // constant
  fov(t)      = 50               // constant
```

**Note on `defaultStartState`/`defaultEndState` vs speed:** The static metadata corresponds to `evaluate(0)` and `evaluate(1)` with default params (speed=1.0) only. The `evaluate()` function computes actual positions using the resolved speed parameter, which may produce different boundary positions when speed ≠ 1.0. OBJ-006's `validateCameraPathPreset` only checks evaluate(0) and evaluate(1) against static metadata with default params.

#### CameraParams handling

- **`speed`**: Scales total Z displacement. `speed=0.5` → 4 units of travel. `speed=2.0` → 16 units. Resolved via `resolveCameraParams()`. Must be > 0.
- **`easing`**: Replaces the default `ease_in_out` for the Z interpolation. Resolved via `resolveCameraParams()`.
- **`offset`**: Not handled inside `evaluate()`. Applied by the renderer post-evaluate, per OBJ-006 D2.

#### `defaultStartState` / `defaultEndState` consistency

Since all valid easing functions satisfy `easing(0) = 0` and `easing(1) = 1`, boundary values are easing-independent at default speed:

- push_forward: `evaluate(0, defaults)` → `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }` = `defaultStartState` ✓
- push_forward: `evaluate(1, defaults)` → `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }` = `defaultEndState` ✓
- pull_back: `evaluate(0, defaults)` → `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }` = `defaultStartState` ✓
- pull_back: `evaluate(1, defaults)` → `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }` = `defaultEndState` ✓

### Module Exports

```typescript
// src/camera/presets/push_pull.ts
export { slowPushForward, slowPullBack };
```

### Registry Integration

The assembly module imports both presets and registers them under keys `'slow_push_forward'` and `'slow_pull_back'`. Registry assembly is not this objective's responsibility. Keys must match each preset's `name` field.

## Design Decisions

### D1: Fixed lookAt at [0, 0, -30] — not tracking with camera

**Decision:** The lookAt target is a constant `[0, 0, -30]` for all values of `t`, regardless of camera position.

**Alternatives considered:**
- **Tracking lookAt** (e.g., `lookAt.z = camZ - 35`): Camera always points exactly down -Z. Viewing direction is perfectly constant at `(0, 0, -1)`.
- **Fixed lookAt at origin** `[0, 0, 0]`: Viewing angle changes significantly as camera moves past origin.

**Rationale:** For pure Z-axis motion where both camera and lookAt are on the Z axis, the viewing direction is always `(0, 0, -1)` regardless of lookAt distance — so a fixed lookAt and a tracking lookAt produce identical results. The choice of z=-30 matters only when `CameraParams.offset` displaces the camera off-axis (e.g., `offset: [2, 0, 0]`), in which case the lookAt anchors the viewing direction toward the scene's depth center (the `back_wall` region per seed Section 4.1). A very deep lookAt (z=-100) would minimize the viewing angle shift from offset; z=-30 provides a natural focal anchor within the scene's spatial range.

### D2: 8 world units of Z displacement at speed=1.0

**Decision:** Default displacement is 8 units (z=5 to z=-3).

**Rationale:** Balances three concerns:
1. **Perceptible depth effect** — Too little displacement (e.g., 2 units) and the parallax effect is barely noticeable.
2. **Safety with typical geometries** — The subject slot at z=-5 (seed Section 4.1) remains 2 units ahead of the end position at z=-3. The near_fg slot at z=-1 ends up 2 units behind the camera — this is expected behavior for foreground framing elements (particles, foliage) that slide out of view.
3. **Controllable via speed** — At speed=0.5 (4 units), the push is very conservative. At speed=1.5 (12 units), the camera passes the subject slot. OBJ-040 validates per-geometry safety.

**Visible area change at key planes (push_forward, speed=1.0, FOV=50°):**

| Plane (Z) | Distance at start (cam z=5) | Distance at end (cam z=-3) | Apparent size ratio (end/start) |
|-----------|---------------------------|--------------------------|-------------------------------|
| sky (z=-50) | 55 | 47 | 1.17× |
| back_wall (z=-30) | 35 | 27 | 1.30× |
| midground (z=-15) | 20 | 12 | 1.67× |
| subject (z=-5) | 10 | 2 | 5.00× |
| near_fg (z=-1) | 6 | behind camera | N/A |

### D3: OversizeRequirements — direction-dependent factors

**Decision:** Push and pull presets have different `recommendedOversizeFactor` values because the direction of motion determines edge-reveal risk.

**Oversize factor formula:** For a plane at distance `d_start` from the camera's start position and `d_end` from the camera's end position, the plane must be sized to fill the larger of the two frustums. If the plane is sized to fill the frustum at `d_start`, the oversize factor needed is `d_end / d_start` when `d_end > d_start`, or `1.0` when `d_end ≤ d_start`.

**Push forward (camera approaches all planes):** As the camera moves from z=5 to z=-3, every plane in front of the camera (z < 5) gets closer. The frustum at each plane's location *narrows* as the camera approaches, so a plane sized for the start (farther) distance already overfills the end (closer) frustum. **No oversizing needed.** `recommendedOversizeFactor = 1.0`.

**Pull back (camera retreats from all planes):** As the camera moves from z=-3 to z=5, every plane gets farther away. The frustum at each plane's location *widens*, so the plane must be larger than needed at the start distance. Per-plane factors at default speed:

| Plane (Z) | d_start (cam z=-3) | d_end (cam z=5) | Factor (d_end / d_start) |
|-----------|-------------------|-----------------|--------------------------|
| sky (z=-50) | 47 | 55 | 1.17 |
| back_wall (z=-30) | 27 | 35 | 1.30 |
| midground (z=-15) | 12 | 20 | 1.67 |
| subject (z=-5) | 2 | 10 | 5.00 |

`recommendedOversizeFactor = 1.7` covers midground-distance planes (factor 1.67) and everything farther. Subject and near_fg planes at closer distances require per-plane factors computed by OBJ-040 — the single-scalar model cannot practically cover them (a factor of 5.0 would make distant planes wastefully oversized).

### D4: Panorama excluded from compatible geometries

**Decision:** Both presets exclude `panorama` from `compatibleGeometries`.

**Rationale:** Panorama geometry (seed Section 4.2) uses a wide backdrop with camera rotation (panning), not translation. A forward Z push on a panorama creates an inappropriate approach toward the cylindrical backdrop rather than the intended panning motion. Including panorama would produce a technically renderable but visually wrong result — violating C-06 (blind-authorable correctness).

### D5: Both presets in a single file — shared internal helper

**Decision:** Both presets live in `src/camera/presets/push_pull.ts` and share a common internal interpolation function. The only difference is which end of the trajectory maps to `t=0` vs `t=1`.

**Rationale:** The seed metadata states "These are mathematical mirrors with swapped start/end positions; one spec covers both." Sharing an internal helper prevents drift between the two presets and makes the mirror relationship explicit. The internal helper is not exported.

### D6: No Y-axis drift — pure Z-axis motion

**Decision:** Position interpolates only on Z. X and Y remain at 0 throughout.

**Rationale:** Seed Section 8.5 shows a slight Y drift alongside Z push as an illustrative example, not a definition of `slow_push_forward`. Multi-axis motion belongs to presets like `gentle_float` (OBJ-031) or `crane_up` (OBJ-033). Pure Z-axis makes these presets composable: `CameraParams.offset` provides static displacement, and future camera composition (OQ-06) could chain push + rise. Single-axis motion is unambiguous for blind authoring (C-06).

### D7: ease_in_out as default easing (not linear)

**Decision:** Default easing is `ease_in_out`.

**Rationale:** TC-09 asserts that eased camera paths feel more natural than linear. A physical camera dolly accelerates from rest, sustains, and decelerates to rest. `ease_in_out` maps this directly. Linear motion feels robotic. The author can override via `CameraParams.easing` if desired.

### D8: Return a new object per evaluate() call

**Decision:** Each call to `evaluate()` returns a freshly constructed `CameraFrameState` object with new `Vec3` arrays for position and lookAt.

**Rationale:** Unlike the static preset where a cached object could suffice, push/pull presets return different positions for different `t` values. Fresh objects eliminate mutation hazards (e.g., the renderer adding offset to position) with zero meaningful performance cost.

## Acceptance Criteria

### Contract Conformance (OBJ-006 test pattern)

- [ ] **AC-01:** `slowPushForward.evaluate(0)` returns `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-02:** `slowPushForward.evaluate(1)` returns `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-03:** `slowPushForward.evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-04:** `slowPushForward.evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-05:** `slowPullBack.evaluate(0)` returns `{ position: [0, 0, -3], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-06:** `slowPullBack.evaluate(1)` returns `{ position: [0, 0, 5], lookAt: [0, 0, -30], fov: 50 }`.
- [ ] **AC-07:** `slowPullBack.evaluate(0)` matches its `defaultStartState` within 1e-6.
- [ ] **AC-08:** `slowPullBack.evaluate(1)` matches its `defaultEndState` within 1e-6.
- [ ] **AC-09:** For both presets, `evaluate(t)` at 100 evenly-spaced `t` in [0,1] returns no NaN, no Infinity, and FOV in (0, 180).
- [ ] **AC-10:** 1000 calls to `evaluate(0.5)` with the same params produce identical results (determinism, C-05).

### Mirror Relationship

- [ ] **AC-11:** `slowPushForward.defaultStartState` deep-equals `slowPullBack.defaultEndState`.
- [ ] **AC-12:** `slowPushForward.defaultEndState` deep-equals `slowPullBack.defaultStartState`.
- [ ] **AC-13:** For every `t` in {0, 0.25, 0.5, 0.75, 1.0}: `slowPushForward.evaluate(t).position` deep-equals `slowPullBack.evaluate(1 - t).position` (within 1e-6), when both use default params (speed=1.0, easing=ease_in_out). **Note:** This mirror relationship holds because `ease_in_out` is symmetric (`e(t) + e(1-t) = 1`). Asymmetric easings (`ease_in`, `ease_out`, `ease_out_cubic`) do NOT satisfy this property, so the mirror relationship breaks when asymmetric easings are applied via `CameraParams.easing`. This AC tests only the default symmetric easing.

### Z-Axis Interpolation

- [ ] **AC-14:** `slowPushForward.evaluate(0.5)` with default params returns a Z position between 5 and -3 (exclusive). For symmetric `ease_in_out`, Z should be approximately 1.0 (the spatial midpoint).
- [ ] **AC-15:** Z position is monotonically non-increasing across `t` in [0,1] for `slow_push_forward` with any monotonic easing (camera always moves forward, never reverses).
- [ ] **AC-16:** Z position is monotonically non-decreasing across `t` in [0,1] for `slow_pull_back` with any monotonic easing.
- [ ] **AC-17:** X and Y components of position are exactly 0 for all `t` values (pure Z-axis motion).

### lookAt and FOV Invariance

- [ ] **AC-18:** lookAt is `[0, 0, -30]` for all `t` in [0,1] for both presets.
- [ ] **AC-19:** FOV is exactly 50 for all `t` in [0,1] for both presets.

### Speed Scaling

- [ ] **AC-20:** `slowPushForward.evaluate(1, { speed: 0.5 })` returns Z position of `5 - (8 * 0.5) = 1.0`.
- [ ] **AC-21:** `slowPushForward.evaluate(1, { speed: 2.0 })` returns Z position of `5 - (8 * 2.0) = -11.0`.
- [ ] **AC-22:** The maximum Euclidean distance from start across 100 samples with `speed: 0.5` is strictly less than with `speed: 1.0` (OBJ-006 conformance pattern).

### Easing Override

- [ ] **AC-23:** `slowPushForward.evaluate(0.5, { easing: 'linear' })` returns Z = `5 - (8 * 0.5) = 1.0` (linear midpoint).
- [ ] **AC-24:** `slowPushForward.evaluate(0.5, { easing: 'ease_in' })` returns a Z value > 1.0 (ease_in is slow at start, so at t=0.5 eased time < 0.5, less displacement).
- [ ] **AC-25:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in the Z position component (OBJ-006 conformance pattern).

### Invalid Params Rejection

- [ ] **AC-26:** `evaluate(0.5, { speed: -1 })` throws an Error (via `resolveCameraParams`).
- [ ] **AC-27:** `evaluate(0.5, { speed: 0 })` throws an Error.
- [ ] **AC-28:** `evaluate(0.5, { easing: 'invalid_name' as any })` throws an Error whose message includes `'invalid_name'`.

### Preset Metadata

- [ ] **AC-29:** `slowPushForward.name` is `'slow_push_forward'` and matches `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`.
- [ ] **AC-30:** `slowPullBack.name` is `'slow_pull_back'` and matches the same regex.
- [ ] **AC-31:** Both presets have `defaultEasing` of `'ease_in_out'`.
- [ ] **AC-32:** Both presets have `compatibleGeometries` containing exactly `['stage', 'tunnel', 'canyon', 'flyover', 'diorama', 'portal', 'close_up']` — 7 entries, excluding `panorama`.
- [ ] **AC-33:** `slowPushForward.tags` includes `'push'` and `'forward'`.
- [ ] **AC-34:** `slowPullBack.tags` includes `'pull'` and `'back'`.

### OversizeRequirements — push_forward

- [ ] **AC-35:** `slowPushForward.oversizeRequirements.maxDisplacementX === 0`.
- [ ] **AC-36:** `slowPushForward.oversizeRequirements.maxDisplacementY === 0`.
- [ ] **AC-37:** `slowPushForward.oversizeRequirements.maxDisplacementZ === 8`.
- [ ] **AC-38:** `slowPushForward.oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-39:** `slowPushForward.oversizeRequirements.recommendedOversizeFactor === 1.0`.

### OversizeRequirements — pull_back

- [ ] **AC-40:** `slowPullBack.oversizeRequirements.maxDisplacementX === 0`.
- [ ] **AC-41:** `slowPullBack.oversizeRequirements.maxDisplacementY === 0`.
- [ ] **AC-42:** `slowPullBack.oversizeRequirements.maxDisplacementZ === 8`.
- [ ] **AC-43:** `slowPullBack.oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-44:** `slowPullBack.oversizeRequirements.recommendedOversizeFactor === 1.7`.

### FOV Range Conformance

- [ ] **AC-45:** All sampled FOV values (100 points) for both presets fall within their declared `fovRange` (tolerance 1e-6).

### Full Validation

- [ ] **AC-46:** `validateCameraPathPreset(slowPushForward)` returns an empty array.
- [ ] **AC-47:** `validateCameraPathPreset(slowPullBack)` returns an empty array.

## Edge Cases and Error Handling

### evaluate() — Push Forward

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState`: position `[0, 0, 5]` |
| `t = 1` | Returns `defaultEndState`: position `[0, 0, -3]` |
| `t = 0.5` (default params) | Z near midpoint of eased curve. For symmetric `ease_in_out`, approximately z=1 |
| `t < 0` (e.g., -0.1) | Undefined behavior per OBJ-006. Callers must clamp. |
| `t > 1` (e.g., 1.5) | Undefined behavior. Preset may extrapolate beyond end position. |
| `params = undefined` | Uses defaults: speed=1.0, ease_in_out easing. |
| `params = {}` | Same as undefined — all defaults. |
| `params = { speed: 0.001 }` | Valid. Camera moves 0.008 units — nearly imperceptible. |
| `params = { speed: 0.5 }` | Camera moves 4 units (z=5 to z=1). Conservative, safe with all typical geometries. |
| `params = { speed: 2.0 }` | Camera moves 16 units (z=5 to z=-11). Passes through subject (z=-5) and midground (z=-15). OBJ-040 must flag edge reveals per geometry. |
| `params = { speed: 5.0 }` | Camera moves 40 units (z=5 to z=-35). Passes through most scene planes. Valid per CameraParams contract but will fail OBJ-040 validation for most geometries. |
| `params = { speed: -1 }` | Throws Error via `resolveCameraParams`. |
| `params = { speed: 0 }` | Throws Error via `resolveCameraParams`. |
| `params = { easing: 'linear' }` | Valid. Uniform velocity. |
| `params = { easing: 'ease_out_cubic' }` | Valid. Fast start, slow end. |
| `params = { easing: 'nonexistent' }` | Throws Error via `resolveCameraParams`, listing valid names. |
| `params = { offset: [2, 0, 0] }` | Not processed inside evaluate(). Renderer applies post-evaluate. |

### evaluate() — Pull Back

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState`: position `[0, 0, -3]` |
| `t = 1` | Returns `defaultEndState`: position `[0, 0, 5]` |
| `params = { speed: 0.5 }` | Camera starts at z=1, retreats to z=5. 4 units of travel. |
| `params = { speed: 2.0 }` | Camera starts at z=-11 (behind midground z=-15 and subject z=-5). Multiple planes begin behind the camera and gradually enter view as it retreats. |
| `params = { speed: 5.0 }` | Camera starts at z=-35 (near back_wall z=-30). Most scene planes are initially behind the camera. They come into view progressively as the camera retreats. |

### Near-Plane Collision Awareness

| Scenario | Behavior |
|----------|----------|
| Push: camera at z=-3, near_fg plane at z=-1 | near_fg is 2 units between camera and lookAt. Plane appears very large/close or partially clips through the near frustum (0.1 units). |
| Push: camera at z=-3, subject at z=-5 | Subject is 2 units ahead. At FOV=50°, visible height at distance 2 is `2 * 2 * tan(25°) ≈ 1.86 units`. Subject plane must be at least this size to fill the view. |
| Camera passes through a plane (high speed) | WebGL renders the plane from behind (back face). `meshBasicMaterial` is double-sided by default — the plane appears mirror-flipped. This is a visual artifact — OBJ-040 should prevent this combination. |
| Pull back: camera starts behind planes (high speed) | Planes initially behind the camera are not visible. They enter view as the camera retreats past them. |

### Mirror Relationship Edge Cases

| Scenario | Behavior |
|----------|----------|
| Same speed, same symmetric easing (linear, ease_in_out, ease_in_out_cubic) | `pushForward.evaluate(t).position` equals `pullBack.evaluate(1-t).position` for all t. Symmetric easings satisfy `e(t) + e(1-t) = 1`. |
| Same speed, asymmetric easing (ease_in, ease_out, ease_out_cubic) | Mirror relationship does NOT hold. `e(t) + e(1-t) ≠ 1` for asymmetric easings. Both presets still individually satisfy start/end boundary conditions. |
| Different speed values on push vs. pull | Mirror relationship breaks — different displacement ranges. |

## Test Strategy

### Unit Tests

**1. Boundary values:** For each preset, verify `evaluate(0)` and `evaluate(1)` match `defaultStartState` and `defaultEndState` exactly (1e-6 tolerance per component).

**2. Mirror symmetry (symmetric easing only):** For `t` in {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}, verify `pushForward.evaluate(t).position` equals `pullBack.evaluate(1-t).position` within 1e-6 (both with default params, which use symmetric `ease_in_out`). Additionally test with `{ easing: 'linear' }` (also symmetric). Verify the mirror does NOT hold with `{ easing: 'ease_in' }` — positions should differ.

**3. Monotonic Z:** Sample 100 points for push_forward with default easing. Verify each successive Z value is ≤ the previous (non-increasing). Same for pull_back (non-decreasing).

**4. X/Y invariance:** For 100 sample points, verify position[0] === 0 and position[1] === 0 for both presets.

**5. lookAt/FOV invariance:** For 100 sample points, verify lookAt is exactly [0, 0, -30] and fov is exactly 50.

**6. Speed scaling:** Verify `evaluate(1, { speed: 0.5 })` gives Z = 1.0 for push_forward. Verify `evaluate(1, { speed: 2.0 })` gives Z = -11.0. Verify max distance from start is less at speed=0.5 than at speed=1.0.

**7. Easing override:** Verify `evaluate(0.5, { easing: 'linear' })` gives Z = 1.0 (exact linear midpoint) for push_forward. Verify different easing produces different Z at t=0.5.

**8. Invalid params:** Verify throws for speed ≤ 0 and invalid easing names.

**9. Determinism:** 100 calls with same `t` and same params produce bit-identical results.

**10. OBJ-006 conformance suite:** Run the reusable conformance test pattern from `src/camera/` against both presets.

**11. OversizeRequirements differentiation:** Verify `slowPushForward.oversizeRequirements.recommendedOversizeFactor === 1.0` and `slowPullBack.oversizeRequirements.recommendedOversizeFactor === 1.7`. Verify all other oversize fields are identical between the two presets.

### Relevant Testable Claims

- **TC-03:** These presets are the primary vehicle for verifying that perspective projection produces convincing 2.5D. Test renders with push_forward should show planes undergoing natural perspective shift.
- **TC-04:** An LLM selects `"camera": "slow_push_forward"` — no XYZ coordinates required.
- **TC-05:** Push_forward on a tunnel geometry is the core test for convincing depth. (OBJ-029 `tunnel_push_forward` is the specialized version; `slow_push_forward` is also tunnel-compatible.)
- **TC-09:** Comparing push_forward with `ease_in_out` vs `linear` easing validates that eased paths feel more natural.

## Integration Points

### Depends On

| Dependency | What is imported | How it's used |
|---|---|---|
| **OBJ-006** (`src/camera/types.ts`) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `resolveCameraParams` | Both presets conform to `CameraPathPreset`. `evaluate()` calls `resolveCameraParams()` for param validation and easing resolution. |
| **OBJ-006** (`src/camera/validate.ts`) | `validateCameraPathPreset` | Used in tests to verify both presets pass full validation. |
| **OBJ-002** (`src/interpolation/`) | `EasingName`, `EasingFn` (transitively via OBJ-006) | `defaultEasing: 'ease_in_out'` uses `EasingName`. The resolved easing function is applied to `t` inside `evaluate()`. No direct import of `interpolate()` — the interpolation is a single lerp `start + (end - start) * easedT`. |
| **OBJ-003** (`src/spatial/`) | `Vec3` (transitively via OBJ-006) | Position and lookAt values are `Vec3` tuples. |

### Consumed By

| Downstream | How it uses OBJ-027 |
|---|---|
| **Registry assembly** | Imports `slowPushForward` and `slowPullBack`, registers under keys `'slow_push_forward'` and `'slow_pull_back'`. |
| **OBJ-059** (Stage geometry tuning) | `slow_push_forward` is the primary motion for stage geometry. |
| **OBJ-069** (Edge-reveal tuning) | Push/pull presets have the most significant Z displacement among common presets. Edge-reveal validation is critical. |
| **OBJ-070/071** (SKILL.md) | Documents both presets as the primary camera motions. |
| **OBJ-040** (Edge-reveal validation) | Uses `oversizeRequirements.maxDisplacementZ = 8` and the evaluate function for trajectory sampling. Must compute per-plane factors for close-approach planes since pull_back's `recommendedOversizeFactor` (1.7) does not cover them, and push_forward's (1.0) only applies because approach direction is safe. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatibleGeometries` — 7 of 8 geometries (all except panorama). |
| **Scene sequencer** (OBJ-010) | Resolves `"camera": "slow_push_forward"` or `"camera": "slow_pull_back"` from manifest, calls `evaluate(t)` per frame. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t)`, applies offset, calls `toCameraState()`, sets Three.js camera. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        push_pull.ts     # slowPushForward and slowPullBack definitions
        static.ts        # (OBJ-026)
        index.ts         # Re-exports all presets
```

## Open Questions

1. **Should pull_back use a different default easing than push_forward?** A pull_back with `ease_in_out` starts slow (at the close position) and ends slow (at the far position). An `ease_out_in` would start fast and end fast, with a slow middle — potentially more dramatic for a "reveal" shot. **Recommendation:** Keep `ease_in_out` for consistency. The author can override via `CameraParams.easing`.

2. **Near_fg plane behavior during push.** At speed=1.0, near_fg (z=-1) ends up behind the camera. Should the SKILL.md warn about this? **Recommendation:** This is OBJ-040's responsibility for validation; the SKILL.md (OBJ-070/071) should note that near_fg planes are transient framing elements that may exit the view during camera pushes.

3. **Should `recommendedOversizeFactor` for pull_back be increased to cover subject-distance planes?** At speed=1.0, subject (z=-5) at start distance 2, end distance 10, needs factor 5.0. The current 1.7 covers midground and farther. **Recommendation:** Keep 1.7; OBJ-040's per-plane computation is the real safety mechanism. A factor of 5.0 would make distant planes wastefully oversized.

---

I believe this revision addresses all seven of the Challenger's issues:

1. **✅ Issue 1 (Critical):** OversizeRequirements are now separate. Push gets `recommendedOversizeFactor = 1.0`, pull gets `1.7`. Separate AC groups (AC-35 through AC-44) verify each.
2. **✅ Issue 2 (Major):** D3 is completely rewritten — clean formula, clean per-plane table for pull_back, no stream-of-consciousness.
3. **✅ Issue 3 (Major):** AC-13 now explicitly states the mirror holds only for symmetric easings, names the symmetric vs asymmetric easings, and test strategy item #2 includes a negative test (verify mirror does NOT hold with `ease_in`).
4. **✅ Issue 4 (Minor):** D1 no longer claims a viewing angle shift. States plainly that viewing direction is always `(0, 0, -1)` for pure Z-axis motion and that lookAt distance only matters with off-axis offset.
5. **✅ Issue 5 (Minor):** Pull_back edge cases table added with speed=2.0 and speed=5.0 scenarios.
6. **✅ Issue 6 (Minor):** Note added after the evaluate() formulas clarifying that defaultStartState/defaultEndState are speed=1.0 only.
7. **✅ Issue 7 (Minor):** Explicit statement added that both presets call `resolveCameraParams(params, 'ease_in_out')` at the top of evaluate().

I'd like the Challenger to verify these fixes and approve if satisfied.

---

## Round 4 — spec_challenger

I'll verify each fix systematically against the revised spec.

**Issue 1 (Critical) — Separate OversizeRequirements:** ✓ Verified. Two separate tables: push gets `recommendedOversizeFactor = 1.0`, pull gets `1.7`. Separate AC groups (AC-35–39 for push, AC-40–44 for pull). D3 has a clean directional derivation.

**Issue 2 (Major) — D3 rewrite:** ✓ Verified. Clean formula, clean per-plane table for pull_back only (since push doesn't need one), no self-correction artifacts.

**Issue 3 (Major) — AC-13 easing symmetry:** ✓ Verified. AC-13 explicitly names `ease_in_out` as symmetric, states the `e(t) + e(1-t) = 1` property, and calls out that asymmetric easings break the mirror. Test strategy #2 includes a negative test with `ease_in`.

**Issue 4 (Minor) — D1 viewing angle:** ✓ Verified. States "viewing direction is always `(0, 0, -1)`" — no contradiction.

**Issue 5 (Minor) — Pull back high-speed edge cases:** ✓ Verified. Dedicated pull_back edge case table with speed 2.0 (z=-11) and speed 5.0 (z=-35).

**Issue 6 (Minor) — defaultStartState vs speed:** ✓ Verified. Note after formulas: "The static metadata corresponds to evaluate(0) and evaluate(1) with default params (speed=1.0) only."

**Issue 7 (Minor) — Explicit resolveCameraParams:** ✓ Verified. "Both presets call `resolveCameraParams(params, 'ease_in_out')` at the top of `evaluate()`" — stated before the motion model.

No new issues introduced by the revisions. The spec is clean, implementable, and structurally sound.

CONCLUSION:

The specification for OBJ-027 defines two camera path presets (`slow_push_forward` and `slow_pull_back`) as mathematical mirrors sharing a common internal helper. Key agreed design points:
- **8 world units of Z displacement** (z=5 to z=-3) at default speed
- **Fixed lookAt at [0, 0, -30]**, pure Z-axis motion
- **Direction-dependent OversizeRequirements**: push_forward gets factor 1.0 (approach = safe), pull_back gets factor 1.7 (retreat = needs oversizing for midground+ planes)
- **ease_in_out default easing** for cinematic dolly feel
- **Mirror symmetry** holds only for symmetric easings
- **47 acceptance criteria** covering contract conformance, mirror relationship, interpolation, speed scaling, easing override, params rejection, metadata, and oversize requirements

Let me write the files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "content": "# Specification: OBJ-027 \u2014 Push/Pull Camera Path Presets\n\n## Summary\n\nOBJ-027 defines two camera path presets \u2014 `slow_push_forward` and `slow_pull_back` \u2014 the defining camera motions for 2.5D projection. `slow_push_forward` moves the camera from z=5 toward z=-3, creating the \"moving into the scene\" effect where WebGL's perspective projection naturally produces foreshortening, vanishing points, and depth separation. `slow_pull_back` is the mathematical mirror: same trajectory reversed, creating a \"revealing the scene\" effect as the camera retreats. Both implement the `CameraPathPreset` interface from OBJ-006 and share a common internal path function, differing only in the mapping of `t=0`/`t=1` to start/end positions. One specification covers both because they are structurally identical save for direction.\n\n## Interface Contract\n\n### Exported Presets\n\n```typescript\n// src/camera/presets/push_pull.ts\n\nimport { CameraPathPreset } from '../types';\n\n/**\n * slow_push_forward \u2014 Camera moves from z=5 toward z=-3 along\n * the Z axis (default speed=1.0, 8 world units of displacement).\n * lookAt is fixed at [0, 0, -30], deep in the scene.\n * FOV is static at 50\u00b0.\n *\n * This is the defining 2.5D motion. As the camera pushes forward,\n * planes at different Z-depths undergo differential perspective\n * shift \u2014 near planes grow faster, far planes grow slower \u2014\n * producing the parallax depth illusion natively via WebGL's\n * perspective projection matrix.\n *\n * The default easing is ease_in_out, producing a cinematic feel\n * where the camera gently accelerates, sustains, and gently\n * decelerates. Linear easing feels robotic; ease_in_out feels\n * like a dolly on a track.\n */\nexport const slowPushForward: CameraPathPreset;\n\n/**\n * slow_pull_back \u2014 Mathematical mirror of slow_push_f
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md
Now update the meta.json:
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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/meta.json",
  "content": "{\n  \"id\": \"OBJ-027\",\n  \"description\": \"Push/pull camera path presets -- slow_push_forward (camera moves from z=5 toward z=-3, creating the 'moving into the scene' effect) and slow_pull_back (reverse). Mathematical mirrors with swapped start/end positions; one spec covers both. The defining 2.5D motion per Section 4.3. Defines position(t), lookAt(t), easing defaults, compatible geometries, and direction-dependent oversizing requirements.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-006\"],\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 camera path. The most important camera motion for 2.5D projection. Spec deliberation resolved: direction-dependent oversize factors (push=1.0, pull=1.7), symmetric-easing-only mirror relationship, pure Z-axis motion with fixed lookAt at [0,0,-30].\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/meta.json has been updated successfully.

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-027/output.md nodes/OBJ-027/meta.json && git commit -m \"OBJ-027: Push/pull camera path preset specification\n\nDefines slow_push_forward and slow_pull_back presets - the defining\n2.5D camera motions. Key design decisions:\n\n- 8 world units Z displacement (z=5 to z=-3) at default speed\n- Fixed lookAt at [0,0,-30], pure Z-axis motion\n- Direction-dependent OversizeRequirements: push=1.0, pull=1.7\n- ease_in_out default easing for cinematic dolly feel\n- Mirror symmetry holds only for symmetric easings\n- Compatible with 7/8 geometries (excludes panorama)\n- 47 acceptance criteria covering contract conformance, mirror\n  relationship, interpolation, speed scaling, and validation\n\nDeliberation resolved 7 issues across 4 rounds.\"",
  "description": "Commit OBJ-027 spec"
}
[Tool Result] [master d9a7835] OBJ-027: Push/pull camera path preset specification
 2 files changed, 463 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-027/output.md
Spec committed. The deliberation converged after 4 rounds with all 7 issues (1 critical, 2 major, 4 minor) resolved. The key fixes were:

1. **Direction-dependent oversize factors** — push_forward gets 1.0 (approach = safe), pull_back gets 1.7 (retreat = needs margin)
2. **Clean D3 derivation** replacing stream-of-consciousness with a crisp formula and per-plane table
3. **Explicit symmetric-easing constraint** on the mirror relationship AC
4. **Corrected D1** removing contradictory viewing-angle claims
5. **Pull-back edge cases** for high speed values
6. **Static metadata vs speed clarification**
7. **Explicit resolveCameraParams() call** at evaluate() entry
