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

All positions and sizes assume the camera starts at `DEFAULT_CAMERA.position` = `[0, 0, 5]` with FOV = 50 degrees and aspect ratio 16:9 (seed Section 8.2). Sizes are computed using the frustum formula from OBJ-003 with oversizing to accommodate camera motion envelopes.

Following the convention established by OBJ-018: the close_up geometry constructs `PlaneSlot` objects (OBJ-005's type) for registration, and all optional `PlaneSlot` fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot.

#### Slot: `backdrop`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -15]` | Distance from camera at start (Z=5): 20 units. Much closer than the stage's backdrop (Z=-30, distance 35). At distance 20, the backdrop fills the frame behind the tightly-framed subject. A deeper backdrop would contribute little visually — dominated by the subject plane. |
| `rotation` | `[0, 0, 0]` | Facing camera. |
| `size` | `[45, 28]` | Frustum visible area at distance 20: height = 2 x 20 x tan(25 degrees) = 18.64; width = 18.64 x (16/9) = 33.14. Size [45, 28] provides ~1.36x horizontal and ~1.50x vertical oversize. See D6 for `slow_pull_back` oversize analysis. |
| `required` | `true` | A close-up with no background produces a subject floating in void. Even a simple gradient or color field is needed. |
| `description` | `'Background — typically a blurred, atmospheric, or gradient backdrop. Kept intentionally minimal to maintain focus on the subject.'` | |
| `renderOrder` | `0` | Renders first (farthest back). |
| `transparent` | `false` | Backdrop is opaque. |
| `fogImmune` | `true` | At distance 20, fog (near=10, far=25) would apply ~67% opacity — nearly hiding the backdrop. A close-up needs its backdrop visible. Fog-immune. |

#### Slot: `subject`

| Field | Value | Notes |
|-------|-------|-------|
| `position` | `[0, 0, -2]` | Very shallow Z — distance 7 from camera. This is the shallowest subject position of any geometry (stage: Z=-5, distance 10). At distance 7 with FOV=50 degrees, the subject fills approximately 65% of the frame height — the tightest default framing in depthkit. |
| `rotation` | `[0, 0, 0]` | Facing camera. |
| `size` | `[10, 10]` | Frustum visible area at distance 7: height = 2 x 7 x tan(25 degrees) = 6.52; width = 6.52 x (16/9) = 11.60. Height 10/6.52 = 1.53x means the subject fills ~65% of the frame height. Width 10/11.60 = 0.86x — the subject does not fill the full horizontal frame, which is correct for a focal element. Square default accommodates both portrait and landscape subject images via texture auto-sizing (OBJ-040). |
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
| `size` | `[18, 12]` | Frustum visible area at distance 5.5: height = 2 x 5.5 x tan(25 degrees) = 5.13; width = 5.13 x (16/9) = 9.12. Size [18, 12] provides ~1.97x horizontal and ~2.34x vertical oversize, ensuring full-frame coverage during camera drift. |
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

The subject is at Z=-2, giving a camera-to-subject distance of 7 units (vs 10 for stage, 10 for diorama). This is the shallowest subject position of any geometry. At this distance with FOV=50 degrees, the subject fills approximately 65% of the frame height — the tightest default framing in depthkit.

Why not shallower (Z=-1 or Z=0)? At Z=-1 (distance 6), the subject would be uncomfortably close to `gentle_float`'s Z drift range (camera Z ranges from 4.6 to 5.4). At Z=0 (distance 5), the subject fills ~78% of the frame height, leaving almost no backdrop visible. Z=-2 balances tight framing with breathing room for subtle camera motion and a sliver of visible backdrop.

Why not at the same position as stage (Z=-5)? At Z=-5, the close_up would look identical to a stage with no midground or floor — it wouldn't feel like a close-up.

### D3: Compatible cameras — subdued motion only

The close_up lists four compatible cameras:

- **`static`** (OBJ-026, verified): No motion. A still portrait or detail shot.
- **`gentle_float`** (OBJ-031, verified): Almost subliminal multi-axis drift. **Default camera.** OBJ-031's drift envelope (+/-0.3 X, +/-0.2 Y, +/-0.4 Z) is small enough that the tightly-framed subject stays centered.
- **`slow_push_forward`** (OBJ-027, verified): Forward push into the subject. Represents the maximum motion intensity appropriate for a close-up. At full speed (1.0), creates an intense zoom-to-detail effect. **Recommended speed <= 0.5** for close_up to avoid extreme magnification — at speed=1.0 the subject at distance 1 from the camera fills ~10.7x the visible area (see Edge Cases). SKILL.md should document this recommendation.
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

- **At `slow_pull_back` start** (camera Z=-3, distance 12): visible area ~19.90w x 11.19h. Backdrop [45, 28] oversize: 2.26x x 2.50x. Generous.
- **At `slow_pull_back` end** (camera Z=5, distance 20): visible area ~33.14w x 18.64h. Backdrop [45, 28] oversize: 1.36x x 1.50x.

The 1.36x horizontal oversize at the end state provides 6 units of margin on each side (45 - 33.14 = 11.86, /2 = 5.93 units). `slow_pull_back` is pure Z-axis motion with zero X/Y displacement, so the only edge-reveal risk is from the frustum growing larger as the camera retreats. At 1.36x oversize, the backdrop extends ~5.93 world units beyond the frustum edge on each side — sufficient for zero-displacement motion.

For comparison, `gentle_float` adds +/-0.3 X drift at most. Even combining `slow_pull_back` end position with `gentle_float`-scale drift (hypothetically), the effective visible width at distance 20 with 0.3 unit lateral offset is ~33.7 units — still within 45. Safe.

The 1.7x recommendation from OBJ-027 accounts for lateral camera presets (which the close_up excludes) and larger-distance backdrops (stage at Z=-30, distance 35). The close_up's tighter Z-range and pure Z-axis compatible cameras justify the lower oversize.

### D7: Accent at Z=-0.5 — between camera and subject

The accent is at Z=-0.5, placing it between the camera start (Z=5) and the subject (Z=-2), at distance 5.5 from the camera.

A more extreme position (positive Z, e.g., Z=1) was considered but rejected: when `slow_push_forward` drives the camera to Z=-3, a plane at Z=1 would be behind the camera (Z=1 > Z=-3). Even Z=0 would result in the camera passing through the plane during push forward. Z=-0.5 keeps the accent in front of the camera in all compatible camera states:

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
- [ ] **AC-21:** `backdrop` (distance 20 from camera): size `[45, 28]` >= frustum visible area at distance 20 with FOV=50 degrees and aspect 16:9 (~33.14w x 18.64h).
- [ ] **AC-22:** `accent` (distance 5.5 from camera): size `[18, 12]` >= frustum visible area at distance 5.5 (~9.12w x 5.13h).
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
| `slow_push_forward` speed=1.0 — subject at extreme distance | Camera at Z=-3, subject at Z=-2. Distance = 1 unit. Visible height = 0.93 units. Subject size [10, 10] is ~10.7x the visible area — only ~9% of the subject visible. Extreme but not broken. | Artistically valid for "dramatic zoom to detail." SKILL.md should recommend speed <= 0.5 for close_up push/pull. |
| `slow_push_forward` speed=1.0 — accent behind subject | Camera at Z=-3, accent at Z=-0.5, subject at Z=-2. Accent distance from camera = 2.5; subject distance = 1. The accent is farther from the camera than the subject — it is geometrically behind the subject from the camera's perspective. | `renderOrder: 2` on accent and `transparent: true` on both planes cause Three.js to render the accent after the subject (on top), overriding depth-buffer sorting. The accent composites correctly as an overlay. This depends on the renderer (OBJ-039) not setting `depthWrite: true` on transparent materials — standard Three.js behavior for `MeshBasicMaterial` with `transparent: true` is `depthWrite: false`. |
| `slow_push_forward` speed=1.0 — accent near-plane clipping | Camera at Z=-3, accent at Z=-0.5. Distance = 2.5 units. Near-plane = 0.1. Not clipped. | Safe. |
| `slow_push_forward` speed=1.0 — backdrop edge reveal | Camera at Z=-3, backdrop at Z=-15. Distance = 12. Visible area: ~19.90w x 11.19h. Backdrop [45, 28]: oversize 2.26x x 2.50x. | Safe — generous oversize. |
| `slow_pull_back` speed=1.0 — backdrop edge reveal at max retreat | Camera at Z=5 (end), backdrop at Z=-15. Distance = 20. Visible area: ~33.14w x 18.64h. Backdrop [45, 28]: oversize 1.36x x 1.50x. Pure Z-axis motion (zero X/Y displacement). | Safe — 5.93 units of margin per side with no lateral camera motion. See D6 for full analysis. |
| `slow_pull_back` speed=1.0 — accent at start position | Camera at Z=-3 (start), accent at Z=-0.5. Distance = 2.5. Accent behind subject geometrically. | Same renderOrder behavior as `slow_push_forward` end state. Accent composites correctly as overlay. |
| `gentle_float` — accent clipping | Camera Z ranges 4.6-5.4. Accent at Z=-0.5. Distance ranges 5.1-5.9. | All well above near-plane (0.1). Safe. |
| `gentle_float` — backdrop edge reveal | Camera at max X drift (+/-0.3). Backdrop visible width at distance ~20 = 33.14 + (0.3 x 2 x 33.14/20) = 34.13 effective. Backdrop width 45. | Safe — ~10.87 units margin. |
| Portrait mode (9:16) | Geometry renders correctly. Aspect ratio 9/16 = 0.5625. At distance 20: visible width = 18.64 x 0.5625 = 10.48. Backdrop width 45 provides ~4.29x horizontal oversize. | Even more oversized in portrait. Safe. |

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
23. `backdrop` at distance 20: size [45, 28] >= frustum visible area (~33.14w x 18.64h).
24. `accent` at distance 5.5: size [18, 12] >= frustum visible area (~9.12w x 5.13h).
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
| **OBJ-071** (SKILL.md) | Uses slot names, descriptions, compatible cameras, and use-case guidance for documentation. Should include recommendation that speed <= 0.5 is preferred for push/pull presets on close_up. |
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

A simpler FOV-only breathing preset (e.g., FOV oscillating between 48 degrees and 52 degrees over the scene duration) would produce a subtle "inhale/exhale" visual rhythm without camera translation. This would pair naturally with the close_up geometry.

**Recommendation:** Defer to a future objective. `gentle_float`'s multi-axis drift achieves a similar perceptual effect. A FOV-breathing preset can be added to `compatible_cameras` later without changing the geometry definition. Aligns with TC-14's framing as exploratory.

### OQ-B: Should the close_up subject be larger than [10, 10]?

At distance 7, a [10, 10] subject fills ~65% of frame height. For an extremely tight close-up (face filling 80%+), the subject should be larger or positioned closer. The current values produce a "medium close-up" rather than an "extreme close-up."

**Recommendation:** Keep [10, 10] as default. Authors can use `PlaneOverride.position` to move the subject closer (e.g., Z=-1) or `PlaneOverride.size` to enlarge it. OBJ-066 tuning may adjust this based on visual review.

### OQ-C: Should the accent layer support position jitter or animation?

A bokeh/particle accent might benefit from slight per-frame position variation. This is out of scope for the geometry definition (static spatial state). Any animation would be a renderer concern (OBJ-044, per-frame opacity/position animation, if implemented).

**Recommendation:** Out of scope for OBJ-025. The accent's static position provides a consistent overlay. Dynamic effects are post-V1.
