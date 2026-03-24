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

**Ground visibility with straight-ahead camera:** With camera at `[0, 0, 5]` looking at `[0, 0, -30]` (straight along -Z), the frustum bottom at the ground's Z-center (-20) — distance 25 on Z — is `y_bottom = 0 - 25 * tan(25°) ≈ -11.66`. The ground at Y=-4 is well within the frustum, occupying roughly the bottom third of the frame. As the camera pushes to Z=-3 (end of `slow_push_forward`), the ground remains fully visible — the frustum widens with proximity to the nearest ground segments.

Following the convention established by OBJ-018: the flyover geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `sky`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 20, -50]` | Very deep Z, raised high (Y=20) to sit above the camera and fill the upper frame. Z-axis distance from camera: 55 units. |
| `rotation` | `[0, 0, 0]` | `FACING_CAMERA` — upright plane facing the camera. Not a ceiling; a distant sky backdrop. |
| `size` | `[130, 60]` | At Z-distance 55: visible area ≈ 51.3h x 91.1w at FOV 50°, 16:9. Provides ~43% oversize in width and ~17% in height. |
| `required` | `true` | Without a sky, the upper frame is empty in every flyover composition. |
| `description` | `'Sky, atmosphere, or distant horizon. Fills the upper portion of the frame above the ground plane.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Sky is opaque background. |
| `fogImmune` | `true` | Sky should remain vivid regardless of fog — it represents infinite distance, not a surface that fades. |

#### Slot: `ground`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, -4, -20]` | Below camera (Y=-4), centered at Z=-20. After FLOOR rotation, `width` (60) maps to X-axis and `height` (80) maps to Z-axis, so the plane covers X in [-30, +30] and Z in [-60, +20]. |
| `rotation` | `[-Math.PI / 2, 0, 0]` | `PLANE_ROTATIONS.FLOOR` — lies flat, faces up. |
| `size` | `[60, 80]` | Width=60 covers +/-30 units in X. Depth=80 (Z-axis after rotation) extends from Z=+20 to Z=-60, providing ample coverage for `slow_push_forward`'s 8-unit Z travel (Z=5 to Z=-3). Far edge at Z=-60 is 57 units ahead of camera's deepest position. |
| `required` | `true` | The ground plane is the defining element. Without it, there is no "terrain" to fly over and the aerial illusion fails. |
| `description` | `'Terrain, landscape, or ground surface seen from above. The defining visual element of the flyover — undergoes strong perspective foreshortening as the camera moves forward.'` | |
| `renderOrder` | `1` | Renders above sky. |
| `transparent` | `false` | Ground is opaque. |
| `fogImmune` | `false` | Distant portions of the ground fade with atmospheric haze — enhances aerial depth perception. |

#### Slot: `landmark_far`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 1, -35]` | Deep Z, centered laterally. Y=1 positions the bottom edge at Y=-4 (center 1 - half-height 5 = -4), aligned with the ground surface. Distance from camera: 40 units on Z. |
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
| `position` | `[-10, 0, -20]` | Left of center (X=-10), mid-depth. Y=0 places the bottom edge at Y=-6 (center 0 - half-height 6 = -6), which extends 2 units below the ground plane at Y=-4. The ground's opaque surface occludes this below-ground portion via Z-buffer: camera rays from above Y=-4 that would reach below the ground at this Z-depth hit the ground plane first. See D4. |
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
| `size` | `[20, 14]` | Oversized relative to the frustum at this distance (visible area ≈ 6.5h x 11.6w). Foreground elements typically extend beyond the frame. |
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

The ground plane size `[60, 80]` is substantially larger than the stage's floor `[20, 40]` because the flyover emphasizes a vast expanse of terrain. With width=60 (+/-30 in X) and depth=80 (Z in [+20, -60] after rotation centered at Z=-20), the ground extends well beyond the camera's travel range for all compatible camera presets. With `slow_push_forward`'s 8-unit Z displacement (Z=5 to Z=-3), the far edge at Z=-60 remains 57 units ahead of the camera's deepest position — safely invisible. OBJ-040 validates edge-reveal safety for all compatible cameras including the future `flyover_glide`.

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

### D13: Sequential renderOrder values 0-4

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
- [ ] **AC-23:** For the `sky` slot (Z-distance 55 from camera at Z=5): size [130, 60] >= frustum visible area (approximately 91.1w x 51.3h at FOV=50 degrees, 16:9).
- [ ] **AC-24:** For the `near_fg` slot (Z-distance 7 from camera at Z=5): size [20, 14] >= frustum visible area (approximately 11.6w x 6.5h).
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
| Ground edge visible on sides during lateral camera motion | Ground width is 60 units (+/-30 in X). With `gentle_float`'s max X displacement of 0.3 units, lateral edge reveal is impossible. Lateral track cameras excluded. |
| Portrait mode (9:16) | Geometry renders correctly. Narrower width shows less ground laterally. Landmarks at X=+/-10 may be partially outside the frame. `preferred_aspect: 'landscape'` guides LLMs away. |
| Landmark bottom edge below ground Y-position | By design. Z-buffer handles occlusion: camera above Y=-4 sees ground before landmark below-ground portions. See D4. |
| Sky plane fully obscured by fog | Cannot happen — `sky` is `fogImmune: true`. |
| Camera dips below Y=-4 | No compatible camera does this. All verified cameras have Y >= -0.2. If a future camera is added, OBJ-040 must verify the camera-above-ground invariant. |

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
25. `sky` size [130, 60] >= visible area at Z-distance 55 with FOV=50 degrees and 16:9 (approximately 91.1w x 51.3h).
26. `near_fg` size [20, 14] >= visible area at Z-distance 7 (approximately 11.6w x 6.5h).
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
