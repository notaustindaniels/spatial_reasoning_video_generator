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
| `size` | `[75, 45]` | Oversized to prevent edge reveals during camera push. Frustum visible area at distance 35: ~32.6h × 58.0w (16:9). Width 75 >= 58.0 (~1.29x oversize), height 45 >= 32.6 (~1.38x oversize). Sufficient for `slow_push_forward`'s 8-unit Z displacement. |
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
| `size` | `[18, 28]` | Tall and moderately wide. Height 28 ensures the wing fills the vertical frame at its distance (visible height at distance 23: ~21.5). Width 18 provides the scenic side panel. After rotation, the effective on-screen width narrows due to foreshortening (~18 x cos(pi/10) ~ 17.1), which is the intended visual effect. |
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
| `size` | `[35, 22]` | Frustum visible area at distance 17: ~15.9h x 28.2w. Width 35 >= 28.2 (~1.24x oversize), height 22 >= 15.9 (~1.38x oversize). |
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
| `size` | `[12, 12]` | Sized to fill roughly 50-65% of frame height. Frustum visible height at distance 10: ~9.33. Height 12 / 9.33 ~ 1.29x — provides margin. Square default accommodates both portrait and landscape subject images via texture aspect-ratio auto-sizing (OBJ-040). Focal element, not a coverage plane. |
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
| `size` | `[25, 16]` | Oversized relative to frustum at this distance (visible ~5.6h x 9.9w). Foreground framing extends beyond the frame edges. |
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

### D2: Wing rotation angle — PI/10 (~18 degrees)

The wings are rotated inward by PI/10 radians (~18 degrees) around the Y-axis. This angle was chosen as a balance between visual effect and practical constraints:

- **Too small (< 10 degrees):** The perspective foreshortening is barely noticeable, and the diorama loses its distinguishing characteristic versus a stage.
- **Too large (> 30 degrees):** The wings become nearly perpendicular to the camera, showing mostly their edge. Text or detailed imagery on the wing would be severely distorted. Also, more of the wing's surface faces away from the camera, increasing the chance of visible texture stretching.
- **~18 degrees (PI/10):** Produces visible foreshortening — the far edge of each wing visibly recedes as the camera pushes forward — while keeping the wing's imagery legible. The foreshortening factor is cos(18 degrees) ~ 0.95, meaning the wing loses only ~5% apparent width to rotation, but the perspective *change* during camera motion is the key visual (not the static appearance).

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
- `midground` (distance ~17) receives very light fog: (17-15)/(45-15) ~ 7%.
- `far: 45` fades distant elements. The backdrop at distance 35 would be ~67% fogged at these settings — hence `backdrop` is `fogImmune: true`.
- The wings at distance 23 receive light fog: (23-15)/(45-15) ~ 27%, which subtly separates them from the subject.

The dark blue tint (vs the stage's pure black or the flyover's light blue-gray) gives the diorama a distinctive mood — slightly nocturnal, theatrical. Authors can override via the manifest's fog settings.

### D6: Backdrop is fog-immune

The backdrop at Z=-30 (distance 35) falls squarely within the fog range (near=15 to far=45). Without fog immunity, it would be ~67% fogged, making it nearly invisible. Since the backdrop is the "painted scenery" of the paper theater and should remain vivid, it is marked `fogImmune: true`. The depth cue in a diorama comes from wing foreshortening and inter-layer parallax, not from atmospheric fading of the backdrop.

### D7: Wing positions at X=+-8, Z=-18

The wings are positioned at X=+-8, placing them near the left and right edges of the visible frame at their Z-distance. At Z=-18 (distance 23 from camera), the frustum half-width is approximately `23 x tan(25 degrees) x (16/9) ~ 19.1`. The wing center at X=+-8 with width 18 (half-width 9) means the wing extends from X=+-(8-9)=-+1 to X=+-(8+9)=+-17. The inner edge at X=-+1 overlaps the center of the frame slightly, while the outer edge at X=+-17 is within the frustum half-width of +-19.1.

After the PI/10 rotation, the wing's projected footprint on screen shifts slightly. The near edge (closest to center) appears wider; the far edge (toward the frame edge) appears narrower. This is the intended foreshortening effect.

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
- [ ] **AC-14:** The `wing_left` slot rotation is `[0, Math.PI / 10, 0]` (positive Y rotation, ~18 degrees inward).
- [ ] **AC-15:** The `wing_right` slot rotation is `[0, -Math.PI / 10, 0]` (negative Y rotation, ~18 degrees inward, mirroring `wing_left`).
- [ ] **AC-16:** All non-wing slots use `FACING_CAMERA` rotation (`[0, 0, 0]`).
- [ ] **AC-17:** `wing_left`, `wing_right`, `midground`, `subject`, and `near_fg` have `transparent: true`. `backdrop` has `transparent: false`.
- [ ] **AC-18:** `backdrop` and `near_fg` have `fogImmune: true`. All other slots have `fogImmune: false`.
- [ ] **AC-19:** `renderOrder` values are: backdrop(0), wing_left(1), wing_right(1), midground(2), subject(3), near_fg(4). No other values.
- [ ] **AC-20:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-21:** `registerGeometry(dioramaGeometry)` succeeds without throwing when called before any registry reads.
- [ ] **AC-22:** All slot `description` fields are non-empty strings.
- [ ] **AC-23:** All slot `size` components are positive (> 0).
- [ ] **AC-24:** For the `backdrop` slot (coverage plane, distance 35): size [75, 45] >= frustum visible area (~58.0w x 32.6h at FOV=50 degrees, 16:9).
- [ ] **AC-25:** For the `midground` slot (coverage plane, distance 17): size [35, 22] >= frustum visible area (~28.2w x 15.9h).
- [ ] **AC-26:** For the `near_fg` slot (coverage plane, distance 6): size [25, 16] >= frustum visible area (~9.9w x 5.6h).
- [ ] **AC-27:** Wing slots and subject slot are exempt from full-frustum coverage check — wings are scenic side panels (not full-frame coverage), subject is a focal element.
- [ ] **AC-28:** Slot Z-positions decrease (go more negative) as depth increases: `near_fg` (-1) > `subject` (-5) > `midground` (-12) > wings (-18) > `backdrop` (-30).
- [ ] **AC-29:** The module self-registers via `registerGeometry(dioramaGeometry)` as a side effect of import.
- [ ] **AC-30:** The module exports `dioramaGeometry` as a named export.
- [ ] **AC-31:** The geometry definition has zero runtime dependencies beyond OBJ-005 types/registry and OBJ-003 constants.
- [ ] **AC-32:** All `PlaneSlot` optional fields (`renderOrder`, `transparent`, `fogImmune`) are explicitly set on every slot — none are omitted.
- [ ] **AC-33:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-34:** `wing_left.position[0]` is the negation of `wing_right.position[0]` (lateral symmetry: -8 vs 8).
- [ ] **AC-35:** `wing_left.size` equals `wing_right.size`.
- [ ] **AC-36:** `wing_left.rotation[1]` is the negation of `wing_right.rotation[1]` (rotation symmetry: PI/10 vs -PI/10).

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
| Camera pushes forward — vertical edge-reveal check | Wing height 28 at distance 23 (before push) fills ~130% of visible height. After an 8-unit push (camera at Z=-3), distance to wings is 15. Visible height at 15: ~14.0. Wing height 28 / 14.0 = 2.0x oversize — safe. |
| Camera pushes forward — horizontal edge-reveal check for wings | At maximum push (camera Z=-3, wing Z=-18, distance 15): frustum half-width ~ `15 x tan(25 degrees) x (16/9) ~ 12.4`. Wing center at X=-8 with half-width ~9 (pre-rotation), outer edge at X=-17. Frustum edge at X=-12.4. Wing extends 4.6 units past the visible area — safe. Full edge-reveal validation for rotated wings under all camera motions is deferred to OBJ-040, which performs formal frustum intersection calculations accounting for rotation. |
| Portrait mode (9:16) | Geometry renders correctly. Narrower width means wings at X=+-8 may be partially outside frame. `preferred_aspect: 'landscape'` guides LLMs away. |
| Wing back-face visibility | Wings rotated at PI/10 show only their front face. Even at maximum camera push (Z=-3), the camera is still in front of the wings (Z=-18). No risk of seeing the wing from behind. Three.js `side: THREE.FrontSide` (default for meshBasicMaterial) would additionally prevent back-face rendering. |
| Fog completely obscuring the wings | Wings at distance 23 with fog near=15, far=45: fog factor ~ (23-15)/(45-15) ~ 0.27 (27% fogged). Visible but subtly faded — intentional for depth separation. |

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
25. `backdrop` size [75, 45] >= visible area at Z-distance 35 with FOV=50 degrees and 16:9 (~58.0w x 32.6h).
26. `midground` size [35, 22] >= visible area at Z-distance 17 (~28.2w x 15.9h).
27. `near_fg` size [25, 16] >= visible area at Z-distance 6 (~9.9w x 5.6h).
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

### OQ-A: Is PI/10 (~18 degrees) the optimal wing rotation angle?

The angle is a heuristic starting point chosen for visible-but-not-excessive foreshortening. The Director Agent (OBJ-063) should evaluate:
- Whether the foreshortening is noticeable enough to justify the diorama as a distinct geometry from the stage.
- Whether wing imagery (text, detailed illustrations) remains legible at this rotation.
- Whether a slightly larger angle (PI/8 = 22.5 degrees) produces a more dramatic effect worth the extra distortion.

**Recommendation:** Start at PI/10. Adjust during OBJ-063 tuning based on visual feedback. Document the final tuned value.

### OQ-B: Should wings have different Z-positions for a staggered arrangement?

Currently both wings are at Z=-18. Staggering them (e.g., left at Z=-20, right at Z=-16) would create additional depth variety. However, this breaks the lateral symmetry and makes the paper-theater metaphor less clean.

**Recommendation:** Keep symmetric for V1. Staggered wings can be achieved via `position_override` in the manifest. If the Director Agent recommends staggering during tuning, adjust then.

### OQ-C: Should there be a `proscenium` slot?

A dedicated slot for a theatrical proscenium arch (the decorative frame around a stage opening) could reinforce the paper-theater metaphor. This would be at shallow Z, similar to `near_fg`, but specifically designed for an arch/frame effect.

**Recommendation:** `near_fg` already serves this purpose. The `description` explicitly mentions "a theatrical proscenium arch." Adding a separate slot would increase the slot count without meaningful spatial distinction. Defer.
