# Deliberation Transcript: OBJ-029

---

## Round 1 — spec_author

Looking at the objective metadata, seed context, and the OBJ-006 dependency spec, I need to design a tunnel-specific camera path preset that pushes deep into Z-space with convincing perspective distortion on the tunnel walls.

Let me first check the existing codebase to understand what's already implemented.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me explore the existing codebase to understand what's been implemented for the dependencies and related presets.
[Tool: Glob]
  Input: {
  "pattern": "**/camera/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-029/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-006/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "**/geometry/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-005/**"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-027/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/transcript.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-018/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "**/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md"
}
[Tool Error] File content (10195 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md"
}
[Tool Error] File content (10960 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "limit": 100
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "limit": 200
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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "offset": 200,
  "limit": 200
}
[Tool Result]    200→**Oversize factor formula:** For a plane at distance `d_start` from the camera's start position and `d_end` from the camera's end position, the plane must be sized to fill the larger of the two frustums. If the plane is sized to fill the frustum at `d_start`, the oversize factor needed is `d_end / d_start` when `d_end > d_start`, or `1.0` when `d_end <= d_start`.
   201→
   202→**Push forward (camera approaches all planes):** As the camera moves from z=5 to z=-3, every plane in front of the camera (z < 5) gets closer. The frustum at each plane's location *narrows* as the camera approaches, so a plane sized for the start (farther) distance already overfills the end (closer) frustum. **No oversizing needed.** `recommendedOversizeFactor = 1.0`.
   203→
   204→**Pull back (camera retreats from all planes):** As the camera moves from z=-3 to z=5, every plane gets farther away. The frustum at each plane's location *widens*, so the plane must be larger than needed at the start distance... [truncated]
Now let me also check the tunnel geometry spec (OBJ-019) since this camera path is specifically tuned for it:
[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-019/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/transcript.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "limit": 200
}
[Tool Result]      1→# Specification: Tunnel Scene Geometry (OBJ-019)
     2→
     3→## Summary
     4→
     5→OBJ-019 defines the **tunnel scene geometry** -- the concrete `SceneGeometry` definition registered as `'tunnel'` in the geometry registry. The tunnel arranges five planes (floor, ceiling, left wall, right wall, end wall) into a box-like corridor receding along the negative Z-axis. When the camera pushes forward, walls undergo real perspective distortion -- converging to a vanishing point -- producing the signature 2.5D depth effect described in seed Section 4.2. This is the geometry that demonstrates depthkit's core differentiator: perspective projection that flat 2D parallax cannot replicate.
     6→
     7→## Interface Contract
     8→
     9→### Module Export
    10→
    11→```typescript
    12→// src/scenes/geometries/tunnel.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The tunnel scene geometry definition.
    18→ *
    19→ * Exported for... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "offset": 200,
  "limit": 200
}
[Tool Result]    200→### D4: Floor and ceiling size is [8, 50]; walls are [50, 6]
   201→
   202→Floor/ceiling planes are rotated to lie flat (X/Z plane), so their `size[0]=8` spans the tunnel width (X-axis) and `size[1]=50` spans the tunnel depth (Z-axis). Wall planes are rotated to stand vertically along the tunnel (Y/Z plane), so `size[0]=50` spans the depth (Z-axis) and `size[1]=6` spans the height (Y-axis).
   203→
   204→**Rationale:** After rotation, each plane's width dimension matches the tunnel's cross-section, and its height/depth dimension extends the full corridor length. The sizes are set to create seamless seams where floor meets walls and walls meet ceiling.
   205→
   206→### D5: End wall size is [8, 6] -- matching the cross-section
   207→
   208→The end wall is a standard camera-facing plane at Z=-45. Its size matches the tunnel cross-section (8 wide x 6 tall) so it "caps" the far end of the corridor without gaps.
   209→
   210→**Rationale:** A perfectly sized end wall prevents v... [truncated]
Now I have a thorough understanding of the dependencies. Let me propose the specification for OBJ-029.

---

# Proposed Specification: OBJ-029 — Tunnel Push Forward Camera Path Preset

## Summary

OBJ-029 defines the `tunnel_push_forward` camera path preset — a deep Z-axis push specifically tuned for the tunnel geometry (OBJ-019). Unlike `slow_push_forward` (OBJ-027), which covers 8 world units of generic Z-axis motion, `tunnel_push_forward` covers **25 world units** (z=5 to z=-20), pushing the camera deep into the tunnel corridor where walls, floor, and ceiling undergo dramatic perspective distortion — converging toward the end wall at z=-45. This preset includes a subtle Y-axis rise (from y=-0.3 to y=0) to simulate a slightly grounded starting perspective that levels out, and uses `ease_in_out_cubic` as its default easing for a heavier, more cinematic feel appropriate for the dramatic spatial motion. It implements the `CameraPathPreset` interface from OBJ-006 and is the default camera for the tunnel geometry.

## Interface Contract

### Exported Preset

```typescript
// src/camera/presets/tunnel_push.ts

import { CameraPathPreset } from '../types';

/**
 * tunnel_push_forward — Camera pushes deep into Z-space along
 * the tunnel corridor, from z=5 to z=-20 (25 world units at speed=1.0).
 * lookAt is fixed at [0, 0, -45], anchored to the end wall.
 * FOV is static at 50°.
 *
 * Includes a subtle Y-axis rise from y=-0.3 to y=0, simulating a
 * camera that starts with a slightly low, grounded perspective and
 * levels out as it moves through the tunnel. This prevents the
 * motion from feeling perfectly robotic while remaining subtle
 * enough to not draw attention away from the forward push.
 *
 * Default easing is ease_in_out_cubic, producing a heavier
 * cinematic feel — the camera accelerates smoothly, sustains
 * through the middle of the tunnel, and decelerates to a halt
 * before the end wall. The cubic curve has a longer sustained
 * middle section than ease_in_out, which suits longer spatial
 * traversals.
 *
 * This is the tunnel geometry's default camera and the preset
 * that produces the defining "traveling through a space" effect
 * described in seed Section 4.2 and tested by TC-05.
 */
export const tunnelPushForward: CameraPathPreset;
```

### Preset Values

| Field | Value | Rationale |
|-------|-------|-----------|
| `name` | `'tunnel_push_forward'` | Seed Section 4.3 naming. Matches `tunnelGeometry.default_camera`. |
| `description` | `'Deep Z-axis push through a tunnel corridor. Walls, floor, and ceiling converge to a vanishing point as the camera travels forward. The defining motion for enclosed-space scenes.'` | |
| `defaultEasing` | `'ease_in_out_cubic'` | Heavier feel than `ease_in_out`. See D2. |
| `defaultStartState.position` | `[0, -0.3, 5]` | Camera starts at default Z with slight downward offset. See D3. |
| `defaultStartState.lookAt` | `[0, 0, -45]` | Anchored to end wall position. See D1. |
| `defaultStartState.fov` | `50` | Seed Section 8.2 default. |
| `defaultEndState.position` | `[0, 0, -20]` | 25 units of Z displacement, Y rises to center. See D4. |
| `defaultEndState.lookAt` | `[0, 0, -45]` | Same fixed target throughout. |
| `defaultEndState.fov` | `50` | No FOV animation. |
| `compatibleGeometries` | `['tunnel']` | Tunnel-specific preset. See D5. |
| `tags` | `['push', 'forward', 'tunnel', 'z_axis', 'deep', 'corridor', 'vanishing_point', 'dramatic']` | |

### OversizeRequirements

| Field | Value | Rationale |
|-------|-------|-----------|
| `maxDisplacementX` | `0` | No lateral displacement. |
| `maxDisplacementY` | `0.3` | Subtle Y rise from -0.3 to 0. |
| `maxDisplacementZ` | `25` | Total Z travel: z=5 to z=-20. |
| `fovRange` | `[50, 50]` | FOV is constant. |
| `recommendedOversizeFactor` | `1.0` | Camera approaches all planes (push direction). See D6. |

### evaluate() Behavior

```typescript
evaluate(t: number, params?: CameraParams): CameraFrameState
```

Calls `resolveCameraParams(params, 'ease_in_out_cubic')` at the top to validate and resolve params.

#### Core motion model

```
Given resolved speed and easing:

  easedT = easing(t)

  Z interpolation:
    startZ = 5
    endZ   = 5 - (25 * speed)
    camZ   = startZ + (endZ - startZ) * easedT
           = 5 - (25 * speed * easedT)

  Y interpolation (same easing):
    startY = -0.3 * speed    // Y offset scales with speed
    endY   = 0
    camY   = startY + (endY - startY) * easedT
           = (-0.3 * speed) + (0.3 * speed * easedT)
           = -0.3 * speed * (1 - easedT)

  position(t) = [0, camY, camZ]
  lookAt(t)   = [0, 0, -45]      // constant
  fov(t)      = 50                // constant
```

**Note on Y-axis scaling with speed:** The Y offset scales with `speed` to maintain proportional motion. At `speed=0.5`, the Y rise is from -0.15 to 0 (half as noticeable). At `speed=2.0`, the Y rise is from -0.6 to 0 (more pronounced). This keeps the Y drift perceptually proportional to the forward push magnitude, preventing situations where a short push has a disproportionately large vertical drift.

#### CameraParams handling

- **`speed`**: Scales total Z displacement AND Y offset amplitude. `speed=0.5` → 12.5 units of Z travel, 0.15 units of Y travel. `speed=2.0` → 50 units of Z travel, 0.6 units of Y travel. Must be > 0.
- **`easing`**: Replaces the default `ease_in_out_cubic` for both Z and Y interpolation (same easing function applied to both axes).
- **`offset`**: Not handled inside `evaluate()`. Applied by the renderer post-evaluate, per OBJ-006 D2.

#### defaultStartState / defaultEndState consistency

Since all valid easing functions satisfy `easing(0) = 0` and `easing(1) = 1`, boundary values are easing-independent at default speed:

- `evaluate(0, defaults)` → `{ position: [0, -0.3, 5], lookAt: [0, 0, -45], fov: 50 }` = `defaultStartState` ✓
- `evaluate(1, defaults)` → `{ position: [0, 0, -20], lookAt: [0, 0, -45], fov: 50 }` = `defaultEndState` ✓

### Module Exports

```typescript
// src/camera/presets/tunnel_push.ts
export { tunnelPushForward };
```

### Registry Integration

The assembly module imports the preset and registers it under key `'tunnel_push_forward'`. Registry assembly is not this objective's responsibility. The key must match `tunnelPushForward.name`.

## Design Decisions

### D1: Fixed lookAt at [0, 0, -45] — anchored to end wall

**Decision:** The lookAt target is a constant `[0, 0, -45]`, coinciding with the tunnel geometry's end wall position.

**Rationale:** The end wall at z=-45 is the vanishing point of the tunnel. Anchoring lookAt to it means the camera always stares down the corridor toward the terminus. As the camera pushes forward, the viewing angle remains essentially unchanged (both camera and lookAt are on the Z-axis, differing only by the subtle Y offset).

**Why not [0, 0, -30] like OBJ-027?** The `slow_push_forward` preset uses lookAt `[0, 0, -30]`, which was chosen as a generic "deep in the scene" anchor. The tunnel's end wall is at z=-45, much deeper. Using z=-30 would still produce a `-Z` viewing direction (because camera is always at Z > -30), but anchoring to the actual end wall makes the geometric relationship explicit and ensures that when `CameraParams.offset` displaces the camera laterally, the viewing direction converges toward the tunnel's actual vanishing point.

### D2: ease_in_out_cubic as default easing (not ease_in_out)

**Decision:** Default easing is `ease_in_out_cubic`, a heavier cubic curve.

**Rationale:** The tunnel push covers 25 world units — over 3× the displacement of `slow_push_forward` (8 units). The longer traversal benefits from a more gradual acceleration/deceleration profile. `ease_in_out` (quadratic) transitions relatively quickly through the acceleration phase; `ease_in_out_cubic` has a longer sustained middle velocity, which creates a sense of coasting through the tunnel's center section. This gives the viewer more time to appreciate the perspective convergence of the walls at full speed before the camera begins decelerating.

The author can override to any easing via `CameraParams.easing` if a different feel is desired (e.g., `ease_out` for a burst-then-settle motion).

### D3: Subtle Y-axis rise from -0.3 to 0

**Decision:** The camera starts 0.3 units below the tunnel's vertical center (y=-0.3) and rises to the center (y=0) during the push.

**Rationale:** A perfectly centered, single-axis Z push feels robotic. The subtle Y drift adds organic quality — as if the camera is mounted on a physical dolly that rises slightly as it accelerates. The 0.3-unit offset is small relative to the tunnel's 6-unit height (5% of the cross-section), keeping it subliminal. The starting low position slightly emphasizes the floor perspective (the viewer sees slightly more floor, slightly less ceiling), which grounds the scene and enhances the spatial feel.

**Why not add X-axis drift?** Lateral drift in a narrow tunnel (8 units wide) risks asymmetric wall visibility. At x=0.3, one wall is 3.7 units away and the other 4.3 units — a noticeable asymmetry. Keeping X=0 maintains the tunnel's symmetry. X-axis displacement is available via `CameraParams.offset` if the author wants it.

**Why scale Y with speed?** At `speed=2.0`, the Z displacement doubles to 50 units. If Y remained at a fixed 0.3 offset, the rise would be barely perceptible relative to the massive forward movement. Scaling Y proportionally keeps the vertical drift's visual contribution consistent across speed values.

### D4: 25 units of Z displacement — calibrated to tunnel depth

**Decision:** The camera travels from z=5 to z=-20 at speed=1.0 (25 world units).

**Rationale and safety analysis:**

The tunnel geometry (OBJ-019) has:
- Corridor planes (floor, ceiling, walls) centered at z=-20 with 50-unit depth, spanning approximately z=+5 to z=-45
- End wall at z=-45
- Camera default start at z=5

At the end position z=-20:
- **Distance to end wall:** 25 units. Comfortable margin.
- **Visible cross-section at end wall** (distance=25, FOV=50°, 16:9): Height ≈ 2×25×tan(25°) ≈ 23.3 units. Width ≈ 41.5 units. The end wall is 8×6 — it fills only a fraction of the view, surrounded by the converging corridor planes. This is the intended vanishing-point effect.
- **Corridor rear edges:** At z=+5, now 25 units behind the camera. Well outside the rear frustum.
- **Wall proximity at end:** The camera is centered (x=0, y=0), walls are at x=±4, floor at y=-3, ceiling at y=+3. No risk of clipping through surfaces.

**Speed safety bounds:**

| Speed | End Z | Distance to End Wall | Risk |
|-------|-------|---------------------|------|
| 0.5 | -7.5 | 37.5 | Safe — conservative push |
| 1.0 | -20 | 25 | Safe — intended default |
| 1.5 | -32.5 | 12.5 | Cautious — end wall visible area approaches tunnel cross-section |
| 1.8 | -40 | 5 | **Risky** — camera very close to end wall |
| 2.0 | -45 | 0 | **Unsafe** — camera reaches end wall |
| >2.0 | <-45 | negative | **Broken** — camera passes through end wall |

OBJ-040 (edge-reveal validation) is responsible for flagging unsafe speed values per geometry. This preset does not clamp speed — it provides displacement metadata for OBJ-040 to compute safety.

**Recommended safe speed range for tunnel:** `0.1 ≤ speed ≤ 1.6`. At speed=1.6, end Z = 5 - 40 = -35, with 10 units of clearance to the end wall. This recommendation should be documented in SKILL.md (OBJ-071) but is NOT enforced by the preset or `resolveCameraParams()` — enforcement belongs to OBJ-040.

### D5: Compatible only with 'tunnel' geometry

**Decision:** `compatibleGeometries` contains only `['tunnel']`.

**Rationale:** This preset is specifically tuned for the tunnel geometry's spatial structure:
- The 25-unit displacement is calibrated to the tunnel's 50-unit corridor depth.
- The lookAt at z=-45 targets the tunnel's end wall.
- The Y-axis starting offset of -0.3 assumes the tunnel's ±3 unit vertical range.
- The `recommendedOversizeFactor` of 1.0 assumes corridor planes that extend behind the camera start position.

Using this preset with a `stage` geometry would push the camera 25 units forward through a scene designed for 8 units of Z travel — flying past the subject, through the backdrop, and beyond. Using it with `flyover` would push horizontally through a scene designed for vertical movement. Every aspect of this preset's calibration is tunnel-specific.

If a future geometry has similar corridor structure (e.g., a `canyon` geometry), it could be added to `compatibleGeometries` after OBJ-041 validates the combination.

### D6: recommendedOversizeFactor of 1.0 — camera approaches all planes

**Decision:** `recommendedOversizeFactor` is 1.0.

**Rationale:** Following OBJ-027's D3 logic — when the camera pushes forward (approaches scene planes), the frustum at each plane's location narrows as the camera gets closer. Planes sized to fill the frustum at the camera's start distance (farthest) automatically overfill the frustum when the camera is closer. No oversizing beyond the start-distance frustum is needed.

The tunnel geometry's corridor planes are already designed (OBJ-019) to extend from z=+5 to z=-45, encompassing the camera's full range of motion. The end wall is sized to match the tunnel cross-section. Edge-reveal prevention for the tunnel depends on the planes' longitudinal extent (their 50-unit depth) rather than a width/height oversize factor.

### D7: New object per evaluate() call

**Decision:** Each call to `evaluate()` returns a freshly constructed `CameraFrameState` with new `Vec3` arrays.

**Rationale:** Position varies with both `t` and `speed`, so caching is impractical. Fresh objects prevent mutation hazards (e.g., renderer adding offset to position). Consistent with OBJ-027's D8.

### D8: Single file for a single preset

**Decision:** `tunnel_push_forward` lives in its own file `src/camera/presets/tunnel_push.ts`, not combined with other presets.

**Rationale:** Unlike OBJ-027 which pairs `slow_push_forward` and `slow_pull_back` as mathematical mirrors sharing an internal helper, `tunnel_push_forward` has no natural counterpart. A `tunnel_pull_back` preset is conceivable but would have fundamentally different spatial concerns (retreating from inside a tunnel, revealing the corridor opening behind) and would need independent tuning. If it's added later, it can share the file or get its own.

## Acceptance Criteria

### Contract Conformance (OBJ-006 test pattern)

- [ ] **AC-01:** `tunnelPushForward.evaluate(0)` returns `{ position: [0, -0.3, 5], lookAt: [0, 0, -45], fov: 50 }`.
- [ ] **AC-02:** `tunnelPushForward.evaluate(1)` returns `{ position: [0, 0, -20], lookAt: [0, 0, -45], fov: 50 }`.
- [ ] **AC-03:** `tunnelPushForward.evaluate(0)` matches `defaultStartState` within 1e-6 per component.
- [ ] **AC-04:** `tunnelPushForward.evaluate(1)` matches `defaultEndState` within 1e-6 per component.
- [ ] **AC-05:** For 100 evenly-spaced `t` in [0,1], `evaluate(t)` returns no NaN, no Infinity, and FOV in (0, 180).
- [ ] **AC-06:** 1000 calls to `evaluate(0.5)` with the same params produce identical results (determinism, C-05).

### Z-Axis Interpolation

- [ ] **AC-07:** Z position is monotonically non-increasing across 100 evenly-spaced `t` in [0,1] with default params (camera always moves forward, never reverses).
- [ ] **AC-08:** `evaluate(0.5, { easing: 'linear' })` returns Z = `5 - (25 * 0.5) = -7.5` (exact linear midpoint).
- [ ] **AC-09:** X component of position is exactly 0 for all `t` values (no lateral motion).

### Y-Axis Interpolation

- [ ] **AC-10:** Y position at t=0 with default params is exactly -0.3.
- [ ] **AC-11:** Y position at t=1 with default params is exactly 0.
- [ ] **AC-12:** Y position is monotonically non-decreasing across 100 evenly-spaced `t` in [0,1] with default params (camera always rises, never dips).
- [ ] **AC-13:** At `speed=0.5`, Y position at t=0 is -0.15 (Y offset scales with speed).
- [ ] **AC-14:** At `speed=2.0`, Y position at t=0 is -0.6 (Y offset scales with speed).

### lookAt and FOV Invariance

- [ ] **AC-15:** lookAt is `[0, 0, -45]` for all `t` in [0,1].
- [ ] **AC-16:** FOV is exactly 50 for all `t` in [0,1].

### Speed Scaling

- [ ] **AC-17:** `evaluate(1, { speed: 0.5 })` returns position Z of `5 - (25 * 0.5) = -7.5`.
- [ ] **AC-18:** `evaluate(1, { speed: 2.0 })` returns position Z of `5 - (25 * 2.0) = -45`.
- [ ] **AC-19:** The maximum Euclidean distance from `defaultStartState.position` across 100 samples with `speed: 0.5` is strictly less than with `speed: 1.0` (OBJ-006 conformance pattern).

### Easing Override

- [ ] **AC-20:** `evaluate(0.5, { easing: 'linear' })` returns Z = -7.5 and Y = -0.15 (linear midpoints).
- [ ] **AC-21:** `evaluate(0.5, { easing: 'ease_in' })` returns a Z value > -7.5 (ease_in is slow at start, so at t=0.5 eased time < 0.5, less displacement).
- [ ] **AC-22:** `evaluate(0.5, { easing: 'linear' })` differs from `evaluate(0.5, { easing: 'ease_in' })` in position components (OBJ-006 conformance pattern).

### Invalid Params Rejection

- [ ] **AC-23:** `evaluate(0.5, { speed: -1 })` throws an Error (via `resolveCameraParams`).
- [ ] **AC-24:** `evaluate(0.5, { speed: 0 })` throws an Error.
- [ ] **AC-25:** `evaluate(0.5, { easing: 'invalid_name' as any })` throws an Error whose message includes `'invalid_name'`.

### Preset Metadata

- [ ] **AC-26:** `tunnelPushForward.name` is `'tunnel_push_forward'` and matches `/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/`.
- [ ] **AC-27:** `tunnelPushForward.defaultEasing` is `'ease_in_out_cubic'`.
- [ ] **AC-28:** `tunnelPushForward.compatibleGeometries` deep-equals `['tunnel']`.
- [ ] **AC-29:** `tunnelPushForward.tags` includes `'push'`, `'forward'`, and `'tunnel'`.
- [ ] **AC-30:** `tunnelPushForward.description` is non-empty and mentions tunnel/corridor and vanishing point.

### OversizeRequirements

- [ ] **AC-31:** `oversizeRequirements.maxDisplacementX === 0`.
- [ ] **AC-32:** `oversizeRequirements.maxDisplacementY === 0.3`.
- [ ] **AC-33:** `oversizeRequirements.maxDisplacementZ === 25`.
- [ ] **AC-34:** `oversizeRequirements.fovRange` deep-equals `[50, 50]`.
- [ ] **AC-35:** `oversizeRequirements.recommendedOversizeFactor === 1.0`.

### FOV Range Conformance

- [ ] **AC-36:** All sampled FOV values (100 points) fall within declared `fovRange` (tolerance 1e-6).

### Full Validation

- [ ] **AC-37:** `validateCameraPathPreset(tunnelPushForward)` returns an empty array.

### Tunnel Geometry Compatibility

- [ ] **AC-38:** The camera's start Z position (5) does not exceed `DEFAULT_CAMERA.position[2]` (5), satisfying OBJ-019's D8 constraint that tunnel-compatible cameras must not position the camera at Z > 5.
- [ ] **AC-39:** At default speed=1.0, the camera's end Z position (-20) is at least 10 world units from the tunnel's end wall (z=-45). This maintains 25 units of clearance.
- [ ] **AC-40:** At speed=1.0, the camera remains within the tunnel cross-section at all times: X=0 is within [-4, 4] (wall bounds), Y ranges from -0.3 to 0 which is within [-3, 3] (floor/ceiling bounds).

## Edge Cases and Error Handling

### evaluate()

| Scenario | Expected Behavior |
|----------|-------------------|
| `t = 0` | Returns `defaultStartState`: position `[0, -0.3, 5]` |
| `t = 1` | Returns `defaultEndState`: position `[0, 0, -20]` |
| `t = 0.5` (default params) | Z near eased midpoint. For `ease_in_out_cubic`, Z is approximately -7.5 (cubic ease's midpoint is close to linear midpoint). Y is approximately -0.15. |
| `t < 0` (e.g., -0.1) | Undefined behavior per OBJ-006. Callers must clamp. |
| `t > 1` (e.g., 1.5) | Undefined behavior. Preset may extrapolate beyond end position. |
| `params = undefined` | Uses defaults: speed=1.0, ease_in_out_cubic easing. |
| `params = {}` | Same as undefined — all defaults. |
| `params = { speed: 0.5 }` | Camera moves 12.5 units Z (z=5 to z=-7.5). Y rises from -0.15 to 0. Conservative, safe push. |
| `params = { speed: 1.0 }` | Default: 25 units Z (z=5 to z=-20). Safe. |
| `params = { speed: 1.5 }` | Camera moves 37.5 units Z (z=5 to z=-32.5). 12.5 units from end wall. Cautious — OBJ-040 should validate. |
| `params = { speed: 2.0 }` | Camera reaches z=-45 — coincides with end wall. **Unsafe.** OBJ-040 must flag. |
| `params = { speed: 3.0 }` | Camera at z=-70 — past end wall and corridor planes. **Broken.** OBJ-040 must reject. |
| `params = { speed: 0.001 }` | Valid. Camera moves 0.025 units. Nearly imperceptible. |
| `params = { speed: -1 }` | Throws Error via `resolveCameraParams`. |
| `params = { speed: 0 }` | Throws Error via `resolveCameraParams`. |
| `params = { easing: 'linear' }` | Valid. Uniform velocity. No acceleration/deceleration. |
| `params = { easing: 'ease_out' }` | Valid. Fast start, slow end — "launch into the tunnel" feel. |
| `params = { easing: 'nonexistent' }` | Throws Error via `resolveCameraParams`, listing valid names. |
| `params = { offset: [1, 0, 0] }` | Not processed inside evaluate(). Renderer applies post-evaluate. Shifts camera laterally in the tunnel — one wall closer, one wall farther. OBJ-040 must verify the offset doesn't move the camera outside the tunnel cross-section. |

### Near-Plane Collision Awareness

| Scenario | Behavior |
|----------|----------|
| Camera at z=-20, end wall at z=-45 | 25 units of clearance. End wall visible as a small rectangle at the vanishing point, heavily fogged. |
| High speed (1.8): camera at z=-40, end wall at z=-45 | 5 units of clearance. End wall fills a large portion of the viewport. May look flat if fog is insufficient. |
| Speed 2.0: camera at z=-45 | Camera is at the end wall plane. The plane may clip or render as a full-screen fill. OBJ-040 should prevent this. |
| Speed >2.0: camera past z=-45 | Camera is behind the end wall. The end wall renders from behind (back face of meshBasicMaterial, double-sided by default). Corridor planes' far edges (at z=-45) are now behind the camera. Visual artifacts guaranteed. |

### Offset Interactions

| Scenario | Behavior |
|----------|----------|
| `offset = [0, 0, 0]` | No change. |
| `offset = [2, 0, 0]` | Camera shifts right. Left wall at x=-4 is now 6 units away, right wall at x=4 is 2 units away. Asymmetric but valid if walls are wide enough. lookAt remains at [0,0,-45] so viewing direction angles slightly left. |
| `offset = [4, 0, 0]` | Camera at right wall position. **Risky** — wall may clip or not be visible. OBJ-040 should flag. |
| `offset = [0, 2.5, 0]` | Camera near ceiling (y=0+2.5=2.5, ceiling at y=3). 0.5 units clearance. lookAt at [0,0,-45] angles the view slightly downward. |

## Test Strategy

### Unit Tests

**1. Boundary values:** Verify `evaluate(0)` and `evaluate(1)` match `defaultStartState` and `defaultEndState` exactly (1e-6 tolerance per component).

**2. Monotonic Z:** Sample 100 points. Verify each successive Z value ≤ previous (non-increasing) with default params.

**3. Monotonic Y:** Sample 100 points. Verify each successive Y value ≥ previous (non-decreasing) with default params.

**4. X invariance:** For 100 sample points, verify position[0] === 0.

**5. lookAt/FOV invariance:** For 100 sample points, verify lookAt is `[0, 0, -45]` and fov is exactly 50.

**6. Speed scaling — Z:** Verify `evaluate(1, { speed: 0.5 }).position[2]` is -7.5. Verify `evaluate(1, { speed: 2.0 }).position[2]` is -45.

**7. Speed scaling — Y:** Verify `evaluate(0, { speed: 0.5 }).position[1]` is -0.15. Verify `evaluate(0, { speed: 2.0 }).position[1]` is -0.6.

**8. Speed scaling — max distance:** Verify maximum Euclidean distance from start at speed=0.5 < distance at speed=1.0.

**9. Easing override:** Verify `evaluate(0.5, { easing: 'linear' })` gives Z=-7.5, Y=-0.15. Verify different easing produces different position at t=0.5.

**10. Invalid params:** Verify throws for speed ≤ 0 and invalid easing names.

**11. Determinism:** 1000 calls to `evaluate(0.5)` produce identical results.

**12. Full preset validation:** `validateCameraPathPreset(tunnelPushForward)` returns empty array.

**13. Tunnel geometry constraint:** Camera start Z (5) ≤ DEFAULT_CAMERA.position[2] (5). Camera end Z at default speed (-20) is well above end wall Z (-45).

**14. OBJ-006 conformance suite:** Run the reusable conformance test pattern from OBJ-006's test strategy against `tunnelPushForward`.

### Relevant Testable Claims

- **TC-05:** "The tunnel geometry with a forward camera push produces a convincing 'traveling through a space' effect where walls visibly recede to a vanishing point." This preset is the primary test vehicle.
- **TC-04** (partial): An LLM specifies `"camera": "tunnel_push_forward"` — no XYZ coordinates needed.
- **TC-09** (partial): The `ease_in_out_cubic` default can be A/B tested against `linear` to validate TC-09's claim.

## Integration Points

### Depends on

| Upstream | What OBJ-029 imports |
|----------|---------------------|
| **OBJ-006** (Camera path type contract) | `CameraPathPreset`, `CameraFrameState`, `CameraParams`, `ResolvedCameraParams`, `OversizeRequirements` types. `resolveCameraParams()` function for param resolution. `CameraPathEvaluator` type for the evaluate signature. |
| **OBJ-002** (`src/interpolation/`) | `EasingName` type (used by `resolveCameraParams`). Easing functions are accessed indirectly via `resolveCameraParams()`, not imported directly. |
| **OBJ-003** (`src/spatial/`) | `Vec3` type for position/lookAt tuples. `DEFAULT_CAMERA` constant for reference (camera start Z = 5). |

### Consumed by

| Downstream | How it uses OBJ-029 |
|------------|---------------------|
| **OBJ-060** (Tunnel visual tuning) | The Director Agent reviews test renders using this preset with the tunnel geometry. May recommend adjustments to displacement, Y offset, easing, or speed bounds. |
| **OBJ-019** (Tunnel geometry) | Lists `'tunnel_push_forward'` in `compatible_cameras` and `default_camera`. OBJ-019 is already verified — the name was a forward reference that this preset fulfills. |
| **OBJ-040** (Edge-reveal validation) | Reads `oversizeRequirements` to compute whether tunnel geometry planes are large enough. Uses `evaluate()` to sample the trajectory for per-frame frustum analysis. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references `compatibleGeometries: ['tunnel']` against the geometry registry. |
| **OBJ-071** (SKILL.md) | Documents this preset as the default/recommended camera for tunnel scenes, with speed guidance (recommended 0.5–1.5). |
| **Camera registry assembly** | Imports `tunnelPushForward` and registers under key `'tunnel_push_forward'`. |
| **Scene renderer** (`src/page/`) | Calls `evaluate(t, params)`, applies offset, calls `toCameraState()`, sets Three.js camera. |

### File Placement

```
depthkit/
  src/
    camera/
      presets/
        tunnel_push.ts    # tunnelPushForward preset definition
```

The barrel export `src/camera/presets/index.ts` (or wherever presets are aggregated) must re-export from `./tunnel_push`.

## Open Questions

### OQ-A: Should the Y-axis drift be configurable via CameraParams?

The current design hard-codes the Y drift ratio (0.3 units per unit of speed) into the preset. An alternative would be to accept a `yDrift?: number` in `CameraParams`. However, `CameraParams` is intentionally minimal (speed, easing, offset) per OBJ-006 D2 — adding preset-specific fields muddies the universal contract. The author can use `offset: [0, -0.3, 0]` to start low and the renderer's static offset won't animate, but that's a different effect (constant displacement vs. animated rise).

**Recommendation:** Keep Y drift as a preset-internal behavior. If tuning (OBJ-060) reveals that the 0.3 value is wrong, revise the preset. If per-scene Y drift control becomes a requirement, consider extending `CameraParams` in a backward-compatible way (unrecognized fields are ignored per OBJ-006).

### OQ-B: Should a `tunnel_pull_back` preset be defined alongside this?

A reverse tunnel push (retreating out of the tunnel) is a natural complement. However, it has different spatial concerns (revealing the tunnel mouth behind the camera, oversizing the opening, potentially needing to see "outside" the tunnel). It should be a separate objective if needed, not bundled here.

### OQ-C: Should the preset enforce a max safe speed?

The analysis shows speed > ~1.8 puts the camera dangerously close to the end wall. The current design relies on OBJ-040 to validate speed per geometry. An alternative is for the preset to clamp speed internally. However, this would violate OBJ-006's contract where `speed` is a pure amplitude multiplier and presets apply it uniformly. Clamping would make the preset's behavior non-linear with respect to the author's intent. **Recommendation:** Keep validation in OBJ-040, document safe range in SKILL.md.

---

I believe this spec is complete and covers all the dimensions required. I'd like the Challenger to verify:
1. The spatial math (especially the Z displacement calibration against OBJ-019's tunnel geometry)
2. The Y-axis scaling-with-speed decision
3. The `ease_in_out_cubic` easing choice
4. The single-geometry compatibility restriction
5. Completeness of acceptance criteria and edge cases

---

## Round 2 — spec_challenger

Let me verify the tunnel geometry spec and the OBJ-027 spec more carefully before challenging.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "offset": "0",
  "limit": "200"
}
[Tool Result]      0→# Specification: Tunnel Scene Geometry (OBJ-019)
     1→
     2→## Summary
     3→
     4→OBJ-019 defines the **tunnel scene geometry** -- the concrete `SceneGeometry` definition registered as `'tunnel'` in the geometry registry. The tunnel arranges five planes (floor, ceiling, left wall, right wall, end wall) into a box-like corridor receding along the negative Z-axis. When the camera pushes forward, walls undergo real perspective distortion -- converging to a vanishing point -- producing the signature 2.5D depth effect described in seed Section 4.2. This is the geometry that demonstrates depthkit's core differentiator: perspective projection that flat 2D parallax cannot replicate.
     5→
     6→## Interface Contract
     7→
     8→### Module Export
     9→
    10→```typescript
    11→// src/scenes/geometries/tunnel.ts
    12→
    13→import type { SceneGeometry } from './types';
    14→
    15→/**
    16→ * The tunnel scene geometry definition.
    17→ *
    18→ * Exported for... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-027/output.md",
  "offset": "0",
  "limit": "200"
}
[Tool Result]      0→# Specification: OBJ-027 — Push/Pull Camera Path Presets
     1→
     2→## Summary
     3→
     4→OBJ-027 defines two camera path presets — `slow_push_forward` and `slow_pull_back` — the defining camera motions for 2.5D projection. `slow_push_forward` moves the camera from z=5 toward z=-3, creating the "moving into the scene" effect where WebGL's perspective projection naturally produces foreshortening, vanishing points, and depth separation. `slow_pull_back` is the mathematical mirror: same trajectory reversed, creating a "revealing the scene" effect as the camera retreats. Both implement the `CameraPathPreset` interface from OBJ-006 and share a common internal path function, differing only in the mapping of `t=0`/`t=1` to start/end positions. One specification covers both because they are structurally identical save for direction.
     5→
     6→## Interface Contract
     7→
     8→### Exported Presets
     9→
    10→```typescript
    11→// src/camera/presets/push_pull.ts
    ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "offset": "200",
  "limit": "150"
}
[Tool Result]    200→### D4: Floor and ceiling size is [8, 50]; walls are [50, 6]
   201→
   202→Floor/ceiling planes are rotated to lie flat (X/Z plane), so their `size[0]=8` spans the tunnel width (X-axis) and `size[1]=50` spans the tunnel depth (Z-axis). Wall planes are rotated to stand vertically along the tunnel (Y/Z plane), so `size[0]=50` spans the depth (Z-axis) and `size[1]=6` spans the height (Y-axis).
   203→
   204→**Rationale:** After rotation, each plane's width dimension matches the tunnel's cross-section, and its height/depth dimension extends the full corridor length. The sizes are set to create seamless seams where floor meets walls and walls meet ceiling.
   205→
   206→### D5: End wall size is [8, 6] -- matching the cross-section
   207→
   208→The end wall is a standard camera-facing plane at Z=-45. Its size matches the tunnel cross-section (8 wide x 6 tall) so it "caps" the far end of the corridor without gaps.
   209→
   210→**Rationale:** A perfectly sized end wall prevents v... [truncated]
I've thoroughly reviewed the proposed specification against the seed document, OBJ-006, OBJ-019, and OBJ-027. Here's my assessment.

## What's Sound

1. **Spatial math is correct.** The 25-unit Z displacement (Z=5 to Z=-20) is well-calibrated against OBJ-019's tunnel (end wall Z=-45, corridor planes spanning Z=+5 to Z=-45). The safety analysis with the speed bounds table is thorough.

2. **OBJ-006 contract conformance is complete.** The spec follows OBJ-027's pattern faithfully — `evaluate()` calls `resolveCameraParams()`, the boundary consistency proof is correct (easing(0)=0, easing(1)=1), and the OversizeRequirements logic is sound (push direction → factor 1.0).

3. **Acceptance criteria are comprehensive.** 40 ACs covering boundary values, monotonicity, speed scaling, easing overrides, invalid params, metadata, oversize requirements, and tunnel-specific spatial constraints. Each is individually testable without guesswork.

4. **Edge cases are well-enumerated.** Speed safety bounds, offset interactions, near-plane collision scenarios — all documented with expected behavior.

5. **Design decisions are well-reasoned.** D1 (lookAt at end wall), D2 (ease_in_out_cubic for heavier feel), D4 (calibration rationale), D5 (tunnel-only compatibility), D6 (oversize factor logic) — all sound.

## Issues to Address

### Issue 1 — Minor: OBJ-019 is a value dependency not reflected in Integration Points

**The problem:** The spec's "Depends on" table lists only OBJ-006, OBJ-002, and OBJ-003. But nearly every concrete value in the spec (lookAt Z=-45, end wall position, cross-section bounds ±4/±3, corridor depth 50) is derived from OBJ-019's frozen geometry definition. If an implementer doesn't know to read OBJ-019, they won't understand *why* these values are what they are.

**Severity:** Minor — the values are stated explicitly in the spec, so an implementer can build without reading OBJ-019. But it's an undocumented coupling.

**Proposed fix:** Add OBJ-019 to the "Depends on" table as a **value dependency** (not a code/type dependency):

| Upstream | What OBJ-029 imports |
|----------|---------------------|
| **OBJ-019** (Tunnel geometry) | No code imports. Values calibrated to OBJ-019's frozen geometry: end wall at Z=-45 (lookAt target), cross-section 8×6 (lateral/vertical safety bounds), corridor depth 50 spanning Z=+5 to Z=-45 (displacement range). |

### Issue 2 — Minor: Subtle viewing direction tilt from Y offset is undocumented

**The problem:** With the camera at `[0, -0.3, 5]` looking at `[0, 0, -45]`, the viewing direction is `[0, 0.3, -50]` — a 0.34° upward tilt. By t=1 (camera at `[0, 0, -20]`, lookAt `[0, 0, -45]`), the direction is `[0, 0, -25]` — perfectly level. This means the camera starts with a barely perceptible upward tilt that corrects during the push.

This is actually a nice organic touch (consistent with D3's "grounded perspective that levels out"), but the spec never mentions it. An implementer debugging the preset might wonder why the viewing angle is not perfectly constant (unlike OBJ-027's pure Z-axis motion where camera and lookAt are both on the Z-axis, producing a constant direction of exactly `[0, 0, -1]`).

**Severity:** Minor — the effect is 0.34° and imperceptible. But undocumented behavior is still a gap.

**Proposed fix:** Add a note to D1 or D3 acknowledging this consequence:

> Because the camera starts at Y=-0.3 while lookAt is at Y=0, the viewing direction at t=0 has a ~0.34° upward tilt that corrects to perfectly level by t=1. This tilt is imperceptible but contributes to the organic "leveling out" feel. Unlike OBJ-027's pure Z-axis motion (constant `[0,0,-1]` direction), this preset's viewing angle is not perfectly constant.

### Issue 3 — Minor: AC-39 has a misleading double threshold

**The problem:** AC-39 reads: *"At default speed=1.0, the camera's end Z position (-20) is at least 10 world units from the tunnel's end wall (z=-45). This maintains 25 units of clearance."*

The AC threshold is 10 but the actual clearance is 25. The comment "maintains 25 units of clearance" makes the reader wonder why the threshold isn't 25. If the intent is "must have at least 10 units of margin to account for future tuning headroom," that rationale should be explicit.

**Severity:** Minor — the test passes either way.

**Proposed fix:** Either raise the threshold to 25 (testing the actual invariant) or add rationale for 10:

> At default speed=1.0, the camera's end Z position (-20) maintains at least 25 units of clearance from the tunnel's end wall (z=-45).

### Issue 4 — Minor: Y-varying-start diverges from OBJ-027 pattern without explicit callout

**The problem:** OBJ-027's `slow_push_forward` has a fixed start position `[0, 0, 5]` regardless of speed — speed only changes the end position. OBJ-029 has a speed-varying start Y: `evaluate(0, {speed: 0.5})` returns `[0, -0.15, 5]`, not `[0, -0.3, 5]`. This is explained in D3 but not called out as a divergence from the OBJ-027 pattern. An implementer familiar with OBJ-027 might assume all push presets keep their start positions fixed.

**Severity:** Minor — D3 and the ACs (AC-13, AC-14) fully specify the behavior. But a one-line note improves implementer orientation.

**Proposed fix:** Add to D3:

> Note: This differs from OBJ-027's pattern, where the start position is invariant with speed. Here, the Y start position varies because the Y drift is anchored at the end (Y=0) rather than the start, ensuring the camera always levels out regardless of speed.

---

## Verdict

All four issues are **minor**. None blocks implementation. The spec is thorough, mathematically consistent, correctly calibrated to the tunnel geometry, and follows OBJ-006's contract pattern faithfully. The acceptance criteria are specific and testable. The edge cases cover the important scenarios including speed safety bounds and offset interactions.

I'm satisfied that a competent implementer could build from this spec without guessing. I'll converge after incorporating these four minor fixes as editorial adjustments in the final output.

CONCLUSION:

The specification for OBJ-029 (Tunnel Push Forward Camera Path Preset) defines a `tunnel_push_forward` preset implementing OBJ-006's `CameraPathPreset` interface. The camera pushes from `[0, -0.3, 5]` to `[0, 0, -20]` (25 world units of Z displacement with a subtle 0.3-unit Y rise), lookAt fixed at `[0, 0, -45]` (tunnel end wall), FOV constant at 50°, default easing `ease_in_out_cubic`. Compatible only with the `tunnel` geometry. Speed scales both Z displacement and Y offset amplitude. OversizeRequirements: maxDisplacementZ=25, maxDisplacementY=0.3, maxDisplacementX=0, fovRange=[50,50], recommendedOversizeFactor=1.0.

The four minor editorial issues (OBJ-019 value dependency in integration points, viewing direction tilt documentation, AC-39 threshold cleanup, Y-start-varying-with-speed callout) are incorporated in the final output.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md",
  "content": "# Specification: OBJ-029 \u2014 Tunnel Push Forward Camera Path Preset\n\n## Summary\n\nOBJ-029 defines the `tunnel_push_forward` camera path preset \u2014 a deep Z-axis push specifically tuned for the tunnel geometry (OBJ-019). Unlike `slow_push_forward` (OBJ-027), which covers 8 world units of generic Z-axis motion, `tunnel_push_forward` covers **25 world units** (z=5 to z=-20), pushing the camera deep into the tunnel corridor where walls, floor, and ceiling undergo dramatic perspective distortion \u2014 converging toward the end wall at z=-45. This preset includes a subtle Y-axis rise (from y=-0.3 to y=0) to simulate a slightly grounded starting perspective that levels out, and uses `ease_in_out_cubic` as its default easing for a heavier, more cinematic feel appropriate for the dramatic spatial motion. It implements the `CameraPathPreset` interface from OBJ-006 and is the default camera for the tunnel geometry.\n\n## Interface Contract\n\n### Exported Preset\n\n```typescript\n// src/camera/presets/tunnel_push.ts\n\nimport { CameraPathPreset } from '../types';\n\n/**\n * tunnel_push_forward \u2014 Camera pushes deep into Z-space along\n * the tunnel corridor, from z=5 to z=-20 (25 world units at speed=1.0).\n * lookAt is fixed at [0, 0, -45], anchored to the end wall.\n * FOV is static at 50\u00b0.\n *\n * Includes a subtle Y-axis rise from y=-0.3 to y=0, simulating a\n * camera that starts with a slightly low, grounded perspective and\n * levels out as it moves through the tunnel. This prevents the\n * motion from feeling perfectly robotic while remaining subtle\n * enough to not draw attention away from the forward push.\n *\n * Default easing is ease_in_out_cubic, producing a heavier\n * cinematic feel \u2014 the camera accelerates smoothly, sustains\n * through the middle of the tunnel, and decelerates to a halt\n * before the end wall
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/output.md
Now update the meta.json:
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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/meta.json",
  "content": "{\n  \"id\": \"OBJ-029\",\n  \"description\": \"Tunnel push forward camera path preset -- deep Z-axis push specifically tuned for tunnel geometry. Appropriate near/far planes, speed calibrated so walls undergo convincing perspective distortion without flying through the end wall. Defines position(t), lookAt(t), easing defaults, compatible geometries (tunnel), and oversizing requirements.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:00:00Z\",\n  \"depends_on\": [\"OBJ-006\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 camera path. Geometry-specific preset for the tunnel. Values calibrated to OBJ-019 tunnel geometry (end wall Z=-45, cross-section 8x6, corridor depth 50). Spec reviewed and approved via deliberation.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-029/meta.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-029/output.md nodes/OBJ-029/meta.json && git commit -m \"OBJ-029: Tunnel push forward camera path preset specification\n\nDefines tunnel_push_forward CameraPathPreset:\n- Z-axis push from z=5 to z=-20 (25 world units at speed=1.0)\n- Subtle Y-axis rise from y=-0.3 to y=0\n- lookAt fixed at [0, 0, -45] (tunnel end wall)\n- FOV constant at 50 degrees\n- Default easing: ease_in_out_cubic\n- Compatible geometries: ['tunnel'] only\n- OversizeRequirements: maxDisplacementZ=25, maxDisplacementY=0.3, factor=1.0\n\nValues calibrated to OBJ-019 tunnel geometry.\nImplements CameraPathPreset interface from OBJ-006.\n40 acceptance criteria covering contract conformance, spatial\ninterpolation, speed scaling, easing overrides, and tunnel safety.\""
}
[Tool Result] [master 6939369] OBJ-029: Tunnel push forward camera path preset specification
 2 files changed, 440 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-029/output.md
The specification for OBJ-029 has been written, committed, and is now final. 

**Summary of deliberation outcome:** The proposer's spec was well-constructed and required only four minor editorial improvements, all incorporated in the final output:

1. **OBJ-019 added as a value dependency** in Integration Points — the spec's spatial calibration is tightly coupled to the tunnel geometry's frozen values.
2. **Viewing direction tilt documented** — the ~0.34° upward tilt at t=0 from the Y offset is now explicitly noted as a design consequence.
3. **AC-39 threshold clarified** — changed from the confusing "at least 10... maintains 25" to a clean "at least 25 units of clearance."
4. **Y-start-varying-with-speed divergence from OBJ-027 called out** — explicitly noted in both D3 and the evaluate() behavior notes so implementers understand the pattern difference.
