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
| `size` | `[75, 45]` | Oversized to prevent edge reveals during camera push. Frustum visible area at distance 35: ~32.6 × 58.0 (16:9). Oversized ~1.3x horizontally, ~1.38x vertically, accommodating +/-5 unit Z push + lateral drift. |
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
| `size` | `[12, 12]` | Sized to fill roughly 50-65% of the frame height at this distance. Frustum visible height at distance 10: ~9.33 units. 12/9.33 = 1.29x — provides margin without overwhelming the frame. Square default accommodates both portrait and landscape subject images via texture aspect-ratio auto-sizing (OBJ-040). The subject is intentionally smaller than the full frustum visible width (~16.6) — it is a focal element, not a full-frame background. |
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
| `size` | `[25, 16]` | Oversized to fill the frame edge-to-edge at close range. Frustum visible area at distance 6: ~5.60 x 9.95. Dramatically oversized because foreground elements typically extend beyond the frame (particles, foliage edges). |
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
| `floor` | `[0, -3, -10]` | `[-PI/2, 0, 0]` | `[20, 40]` | **yes** | no | no | 1 |
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
- [ ] **AC-20:** For coverage slots (`sky`, `backdrop`, `midground`, `near_fg`), both size dimensions are >= the frustum visible dimensions at that slot's distance from `DEFAULT_CAMERA.position` ([0, 0, 5]) with FOV=50 degrees and aspect ratio 16:9. Specifically:
  - `sky` at distance 55: visible ~51.3h x 91.1w -> size [120, 70] (width 120 >= 91.1, height 70 >= 51.3)
  - `backdrop` at distance 35: visible ~32.6h x 58.0w -> size [75, 45] (width 75 >= 58.0, height 45 >= 32.6)
  - `midground` at distance 20: visible ~18.6h x 33.2w -> size [40, 25] (width 40 >= 33.2, height 25 >= 18.6)
  - `near_fg` at distance 6: visible ~5.6h x 9.9w -> size [25, 16] (width 25 >= 9.9, height 16 >= 5.6)
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
24. For each coverage slot (`sky`, `backdrop`, `midground`, `near_fg`): verify that slot `size[0]` >= frustum visible width and `size[1]` >= frustum visible height at the slot's distance from `DEFAULT_CAMERA.position`, with FOV=50 degrees and aspect 16:9.
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
