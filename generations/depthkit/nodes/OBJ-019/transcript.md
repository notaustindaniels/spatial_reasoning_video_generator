# Deliberation Transcript: OBJ-019

---

## Round 1 — spec_author

# Specification: Tunnel Scene Geometry (OBJ-019)

## Summary

OBJ-019 defines the **tunnel scene geometry** — the concrete `SceneGeometry` definition registered as `'tunnel'` in the geometry registry. The tunnel arranges five planes (floor, ceiling, left wall, right wall, end wall) into a box-like corridor receding along the negative Z-axis. When the camera pushes forward, walls undergo real perspective distortion — converging to a vanishing point — producing the signature 2.5D depth effect described in seed Section 4.2. This is the geometry that demonstrates depthkit's core differentiator: perspective projection that flat 2D parallax cannot replicate.

## Interface Contract

### Module Export

```typescript
// src/scenes/geometries/tunnel.ts

import type { SceneGeometry } from './types';

/**
 * The tunnel scene geometry definition.
 * 
 * Exported for direct reference in tests and documentation.
 * Also self-registers via registerGeometry() at module load time.
 */
export const tunnelGeometry: SceneGeometry;
```

### Side Effect: Registration

When `tunnel.ts` is imported, it calls `registerGeometry(tunnelGeometry)` as a module-level side effect, per the OBJ-005 registry pattern (D2). The barrel export `src/scenes/geometries/index.ts` must import `./tunnel` to trigger registration.

### Geometry Definition

```typescript
const tunnelGeometry: SceneGeometry = {
  name: 'tunnel',

  description:
    'A corridor with floor, ceiling, and walls receding to a vanishing point. ' +
    'Camera pushes forward on the Z-axis for a "traveling through a space" effect. ' +
    'Walls undergo real perspective distortion — converging toward the end wall. ' +
    'Best for: corridors, hallways, underwater passages, cave systems, sci-fi tunnels, ' +
    'forest paths, and any scene where the viewer moves through an enclosed space.',

  slots: {
    floor: {
      position: [0, -3, -20] as Vec3,
      rotation: [-Math.PI / 2, 0, 0] as EulerRotation,
      size: [8, 50] as Size2D,
      required: true,
      description: 'Ground surface extending forward into the tunnel.',
      renderOrder: 0,
      transparent: false,
      fogImmune: false,
    },
    ceiling: {
      position: [0, 3, -20] as Vec3,
      rotation: [Math.PI / 2, 0, 0] as EulerRotation,
      size: [8, 50] as Size2D,
      required: false,
      description: 'Overhead surface extending forward into the tunnel. Omit for open-air passages.',
      renderOrder: 0,
      transparent: false,
      fogImmune: false,
    },
    left_wall: {
      position: [-4, 0, -20] as Vec3,
      rotation: [0, Math.PI / 2, 0] as EulerRotation,
      size: [50, 6] as Size2D,
      required: true,
      description: 'Left boundary wall receding to the vanishing point.',
      renderOrder: 1,
      transparent: false,
      fogImmune: false,
    },
    right_wall: {
      position: [4, 0, -20] as Vec3,
      rotation: [0, -Math.PI / 2, 0] as EulerRotation,
      size: [50, 6] as Size2D,
      required: true,
      description: 'Right boundary wall receding to the vanishing point.',
      renderOrder: 1,
      transparent: false,
      fogImmune: false,
    },
    end_wall: {
      position: [0, 0, -45] as Vec3,
      rotation: [0, 0, 0] as EulerRotation,
      size: [8, 6] as Size2D,
      required: true,
      description: 'Distant terminus of the tunnel, visible as the vanishing point target.',
      renderOrder: 0,
      transparent: false,
      fogImmune: false,
    },
  },

  compatible_cameras: [
    'tunnel_push_forward',
    'slow_push_forward',
    'static',
    'gentle_float',
  ],
  default_camera: 'tunnel_push_forward',

  fog: {
    color: '#000000',
    near: 15,
    far: 50,
  },

  preferred_aspect: 'landscape',
};
```

### Barrel Export Addition

```typescript
// src/scenes/geometries/index.ts — add to existing barrel
import './tunnel'; // triggers registration side effect
export { tunnelGeometry } from './tunnel';
```

## Design Decisions

### D1: Slot positions centered at Z=-20 with depth span from camera to Z=-45

The seed example (Section 8.6) centers floor/walls at Z=-15 with the end wall at Z=-35. I've pushed all planes deeper: floor/ceiling/walls centered at Z=-20, end wall at Z=-45. This creates a 50-unit total depth corridor (camera starts at approximately Z=5 per `DEFAULT_CAMERA`, end wall at Z=-45).

**Rationale:** A longer corridor gives the camera more Z-travel before reaching the end wall, producing a more dramatic and sustained forward-push effect. The seed values were explicitly labeled as a sketch ("These Z values are defaults" — Section 4.1). With the camera default at Z=5 and a `tunnel_push_forward` preset likely traveling to around Z=-15 or Z=-20, the end wall at Z=-45 ensures it remains visible as a distant vanishing point target throughout the animation, never approached too closely. The fog (near=15, far=50) progressively fades the end wall, preventing it from looking flat.

These values are subject to the Director Agent tuning cycle (OBJ-060). The initial values are chosen to be mathematically safe (no clipping, no edge reveal with reasonable camera paths) while providing a strong starting point for visual tuning.

### D2: Tunnel cross-section is 8 units wide × 6 units tall

Floor and ceiling are at Y=-3 and Y=3 (6 units apart). Left and right walls are at X=-4 and X=4 (8 units apart). This creates a slightly wider-than-tall cross-section (4:3 ratio), which maps well to the landscape viewport and avoids a claustrophobic feel.

**Rationale:** A 1:1 or taller-than-wide cross-section would waste horizontal viewport space in 16:9. The 8×6 proportion means the walls, floor, and ceiling are all visible in the viewport at FOV=50° without extreme foreshortening of any single surface. The camera, centered at Y=0, sits at the vertical midpoint of the tunnel, giving equal visual weight to floor and ceiling.

### D3: Wall/floor/ceiling planes are 50 units deep (on their long axis)

The floor, ceiling, left wall, and right wall all use 50 units on the axis that extends into the tunnel (the depth axis when rotated). Since these planes are centered at Z=-20, they span from approximately Z=+5 (behind the camera's start position) to Z=-45 (coinciding with the end wall).

**Rationale:** The plane must extend behind the camera's starting position to prevent the near edge from being visible in the initial frames. And it must reach the end wall so there's no visible gap between the corridor and the terminus. The 50-unit depth provides margin for camera motion — even if the camera starts slightly behind Z=5 or pushes past Z=-20, the plane edges won't be revealed. This directly addresses TC-05's requirement for "convincing depth" and the seed's emphasis on no edge reveals.

### D4: Floor and ceiling size is [8, 50]; walls are [50, 6]

Floor/ceiling planes are rotated to lie flat (X/Z plane), so their `size[0]=8` spans the tunnel width (X-axis) and `size[1]=50` spans the tunnel depth (Z-axis). Wall planes are rotated to stand vertically along the tunnel (Y/Z plane), so `size[0]=50` spans the depth (Z-axis) and `size[1]=6` spans the height (Y-axis).

**Rationale:** After rotation, each plane's width dimension matches the tunnel's cross-section, and its height/depth dimension extends the full corridor length. The sizes are set to create seamless seams where floor meets walls and walls meet ceiling.

### D5: End wall size is [8, 6] — matching the cross-section

The end wall is a standard camera-facing plane at Z=-45. Its size matches the tunnel cross-section (8 wide × 6 tall) so it "caps" the far end of the corridor without gaps.

**Rationale:** A perfectly sized end wall prevents visible gaps at the joints where walls/floor/ceiling meet the terminus. As the camera pushes forward, the end wall grows larger in the viewport due to perspective — this is the core vanishing-point effect.

### D6: Ceiling is optional; all other slots are required

An open-air tunnel (no ceiling) is a valid and common scene type — think canyon paths, open corridors, forest trails. Making ceiling optional enables this variation without a separate geometry. Floor and both walls are structurally essential to the tunnel illusion; the end wall provides the vanishing point target.

**Rationale:** Seed Section 8.6 shows `ceiling.required: false` in the tunnel example. This preserves the geometry's spatial integrity when ceiling is omitted — the floor and walls still create converging perspective lines. Dropping floor or either wall would break the tunnel illusion.

### D7: Fog defaults to black, near=15, far=50

Black fog starting at distance 15 from the camera and reaching full opacity at distance 50. This is darker and starts closer than the seed sketch (which used near=10, far=40).

**Rationale:** The tunnel is a naturally enclosed, dimly lit space. Black fog:
1. Hides the hard edge of the end wall at Z=-45 by fading it into darkness.
2. Creates natural atmospheric depth — closer surfaces are vivid, distant surfaces fade.
3. Masks any texture seams at far distances where wall/floor/ceiling meet the end wall.

Near=15 means fog only starts affecting objects more than 15 units from the camera (10 units into the scene from the camera's default Z=5 position). This keeps the immediate tunnel environment crisp while fading the deep end. Far=50 means objects 50+ units from the camera are fully fogged — the end wall at distance ~50 units from the start position is nearly invisible, appearing as a dark terminus.

The fog is overridable per-scene via the manifest (per OBJ-005's `SceneGeometry.fog` + manifest override mechanism in OBJ-004).

### D8: Compatible cameras include both tunnel-specific and generic presets

`tunnel_push_forward` is the signature motion. `slow_push_forward` provides a gentler, more generic forward push. `static` allows a frozen establishing shot. `gentle_float` enables subtle, ambient movement for atmospheric scenes.

**Rationale:** These four presets span the common use cases — dramatic forward movement, gentle forward movement, no movement, and ambient drift. Camera presets like `lateral_track_left` are excluded because lateral tracking in a narrow tunnel would reveal the side edges of the floor/ceiling planes. The `compatible_cameras` list acts as a safety net (seed C-06, AP-03) — only cameras validated to not cause edge reveals are allowed. Additional presets can be added to this list as they are implemented and validated (OBJ-026+).

### D9: preferred_aspect is 'landscape'

Tunnels work best in landscape orientation where the horizontal viewport maps to the tunnel's wider cross-section. In portrait mode, the tall narrow viewport would show mostly floor and ceiling with very thin wall slivers, reducing the vanishing-point impact.

**Rationale:** The tunnel cross-section (8:6) is landscape-proportioned. Portrait mode would require significantly different plane proportions to maintain the effect — that adaptation is OBJ-040/OBJ-045's responsibility. The advisory `preferred_aspect: 'landscape'` guides SKILL.md (OBJ-071) to recommend landscape orientation for tunnel scenes.

### D10: No use of DEFAULT_SLOT_TAXONOMY

The tunnel geometry defines a completely independent `SlotSet`. The default taxonomy (sky, back_wall, midground, subject, near_fg) describes a layered backdrop arrangement — fundamentally different from a tunnel's corridor structure. The tunnel's floor/ceiling/walls have no meaningful correspondence to the default slots.

**Rationale:** Per OBJ-007 D1 (two-tier slot model), geometries with fundamentally different spatial structures define their own slot sets. A tunnel's `floor` is a horizontal plane at Y=-3 with rotation `[-PI/2, 0, 0]`; the default taxonomy's slots are all upright planes facing the camera. Forcing the tunnel into the default taxonomy would produce incorrect spatial relationships and confusing slot names.

### D11: renderOrder values — end_wall and floor/ceiling at 0, walls at 1

End wall, floor, and ceiling are at renderOrder 0. Left and right walls are at renderOrder 1. This hierarchy ensures that when walls overlap with floor/ceiling at the edges (due to perspective convergence), the walls draw on top.

**Rationale:** In practice, depth-buffer testing handles most overlap correctly. But for cases where planes are nearly coplanar at joints (wall-floor seam), explicit renderOrder prevents z-fighting artifacts. Walls drawing on top of floor/ceiling at the seams produces the cleaner visual result because wall edges are more visually prominent.

### D12: No transparency on any slot

All tunnel slots use `transparent: false`. Tunnel surfaces are solid environmental surfaces — they are not meant to be seen through. Subject elements or particles in a tunnel scene would require a separate geometry (or a future extension adding optional transparent overlay slots).

**Rationale:** Transparent materials with large plane overlap (as in a tunnel where all surfaces converge at the vanishing point) cause significant draw-order complexity and potential visual artifacts. Keeping all materials opaque simplifies rendering and aligns with the tunnel's spatial concept — you're inside an enclosed space, not looking through translucent layers.

### D13: All slots have fogImmune: false

Every slot in the tunnel is subject to fog. Unlike a stage geometry where a sky backdrop might need fogImmune to remain vivid at extreme distance, the tunnel's aesthetic depends on fog fading all surfaces uniformly to create depth.

**Rationale:** The end wall at Z=-45 should fade into darkness, not stand out as a flat rectangle. Floor and walls should progressively darken into the distance. Fog immunity would break the tunnel's depth illusion.

## Acceptance Criteria

- [ ] **AC-01:** A module `src/scenes/geometries/tunnel.ts` exports `tunnelGeometry` as a `SceneGeometry` conforming to OBJ-005's interface.
- [ ] **AC-02:** Importing `tunnel.ts` calls `registerGeometry(tunnelGeometry)` as a module-level side effect, registering the geometry under the name `'tunnel'`.
- [ ] **AC-03:** `tunnelGeometry.name` is `'tunnel'`.
- [ ] **AC-04:** `tunnelGeometry.slots` contains exactly 5 keys: `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`.
- [ ] **AC-05:** `floor` slot has `rotation: [-Math.PI/2, 0, 0]` (lies flat, facing up), `required: true`.
- [ ] **AC-06:** `ceiling` slot has `rotation: [Math.PI/2, 0, 0]` (lies flat, facing down), `required: false`.
- [ ] **AC-07:** `left_wall` slot has `rotation: [0, Math.PI/2, 0]` (faces right), `required: true`.
- [ ] **AC-08:** `right_wall` slot has `rotation: [0, -Math.PI/2, 0]` (faces left), `required: true`.
- [ ] **AC-09:** `end_wall` slot has `rotation: [0, 0, 0]` (faces camera), `required: true`.
- [ ] **AC-10:** Floor and ceiling Y-positions are symmetric about Y=0 (i.e., `floor.position[1] === -ceiling.position[1]`).
- [ ] **AC-11:** Left and right wall X-positions are symmetric about X=0 (i.e., `left_wall.position[0] === -right_wall.position[0]`).
- [ ] **AC-12:** End wall size matches the tunnel cross-section: `end_wall.size[0]` equals the distance between left and right walls, and `end_wall.size[1]` equals the distance between floor and ceiling.
- [ ] **AC-13:** Floor/ceiling plane width (`size[0]`) matches the tunnel width (distance between left and right walls).
- [ ] **AC-14:** Wall plane height (`size[1]`) matches the tunnel height (distance between floor and ceiling).
- [ ] **AC-15:** All corridor planes (floor, ceiling, left_wall, right_wall) extend from behind the default camera start position (Z ≥ `DEFAULT_CAMERA.position[2]`) to at least the end wall's Z-position.
- [ ] **AC-16:** `tunnelGeometry.compatible_cameras` contains `'tunnel_push_forward'` and at least `'static'`.
- [ ] **AC-17:** `tunnelGeometry.default_camera` is `'tunnel_push_forward'` and appears in `compatible_cameras`.
- [ ] **AC-18:** `tunnelGeometry.fog` is defined with `color` matching `/^#[0-9a-fA-F]{6}$/`, `near >= 0`, and `far > near`.
- [ ] **AC-19:** `tunnelGeometry.description` is non-empty and mentions corridor/tunnel and vanishing point.
- [ ] **AC-20:** `tunnelGeometry.preferred_aspect` is `'landscape'`.
- [ ] **AC-21:** `tunnelGeometry` passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-22:** After importing `tunnel.ts`, `getGeometry('tunnel')` returns the registered geometry.
- [ ] **AC-23:** All slot names match `/^[a-z][a-z0-9_]*$/` (SLOT_NAME_PATTERN from OBJ-007).
- [ ] **AC-24:** All slot `description` fields are non-empty strings.
- [ ] **AC-25:** All slot `size` components are > 0.
- [ ] **AC-26:** No slot has `transparent: true` (all tunnel surfaces are opaque).
- [ ] **AC-27:** No slot has `fogImmune: true` (all surfaces participate in fog).
- [ ] **AC-28:** The geometry has exactly 4 required slots and 1 optional slot (ceiling).

## Edge Cases and Error Handling

### Structural Consistency

| Condition | Expected Behavior |
|---|---|
| Ceiling omitted by manifest author | Tunnel renders as open-top corridor. Floor, walls, and end wall create sufficient depth illusion. No rendering error. |
| All 5 slots provided | Full enclosed tunnel with all surfaces textured. |
| Manifest provides plane key not in slots (e.g., `subject`) | Caught by manifest validation (OBJ-017 via OBJ-005 `getAllSlotNames`) — error: `"Plane 'subject' is not a valid slot for geometry 'tunnel'. Valid slots: ceiling, end_wall, floor, left_wall, right_wall"` |
| Manifest uses incompatible camera (e.g., `lateral_track_left`) | Caught by manifest validation (OBJ-041 via OBJ-005 `isCameraCompatible`) — error naming the incompatible camera and listing compatible options. |
| Manifest overrides floor position via PlaneOverride | Valid per OBJ-007's override mechanism. The override produces a new `ResolvedSlot`; the geometry's registered definition is not mutated (OBJ-005 D9). |

### Spatial Boundary Conditions

| Condition | Notes |
|---|---|
| Camera at default position [0, 0, 5] looking at [0, 0, -30] | All four corridor planes extend behind Z=5 (plane center at Z=-20 with 50-unit depth → rear edge at approximately Z=+5). Floor/ceiling/wall near edges are at or behind the camera — they fill the viewport without revealing back edges. |
| Camera pushes forward to Z=-15 | The camera is now 30 units from the end wall. Corridor planes still extend 5 units behind (their rear edge at Z≈+5, camera at Z=-15 → 20 units of plane behind the camera). No rear edge reveal. |
| Camera pushes very deep (Z=-30) | The camera is 15 units from the end wall. Corridor planes rear edge at Z≈+5, 35 units behind the camera. Front edges at Z≈-45, coinciding with end wall. The forward camera push reveals more of the end wall as it grows in the viewport. Camera path presets must cap forward travel to avoid clipping through the end wall. |
| Portrait mode (9:16) | The 8-unit tunnel width is narrower than the 6-unit height in viewport terms. With a 9:16 aspect ratio and FOV=50°, the visible width at the camera's position is narrower than in landscape, so the walls may be more prominent and the floor/ceiling less visible. The geometry renders correctly but may not look ideal — `preferred_aspect: 'landscape'` advises against this. OBJ-045 handles portrait adaptation. |

### Texture Considerations

| Condition | Notes |
|---|---|
| Floor/ceiling textures with non-matching aspect ratios | The texture stretches to fill the plane geometry. For a floor plane of size [8, 50], a 1:1 image would appear stretched along the depth axis. SKILL.md (OBJ-071) should advise generating elongated textures or using repeating patterns for corridor surfaces. |
| Left and right wall textures are the same image | Valid and common — symmetrical tunnels. The right wall's `[0, -PI/2, 0]` rotation mirrors the left wall's perspective naturally. |
| End wall texture aspect ratio vs slot size | End wall is [8, 6] (4:3). A 16:9 image would appear slightly compressed vertically. Since the end wall is distant and fog-faded, minor distortion is usually invisible. |

## Test Strategy

### Unit Tests

**Geometry definition validity:**
1. `tunnelGeometry` passes `validateGeometryDefinition()` with empty error array.
2. `tunnelGeometry.name` is `'tunnel'`.
3. `tunnelGeometry.slots` has exactly 5 entries.
4. Each slot name matches `SLOT_NAME_PATTERN`.
5. Each slot has non-empty `description`.
6. Each slot `size` components are > 0.

**Slot spatial correctness:**
7. Floor rotation is `[-Math.PI/2, 0, 0]`.
8. Ceiling rotation is `[Math.PI/2, 0, 0]`.
9. Left wall rotation is `[0, Math.PI/2, 0]`.
10. Right wall rotation is `[0, -Math.PI/2, 0]`.
11. End wall rotation is `[0, 0, 0]`.
12. Floor and ceiling Y-positions are symmetric about Y=0.
13. Left and right wall X-positions are symmetric about X=0.
14. End wall width equals tunnel width (distance between wall X-positions).
15. End wall height equals tunnel height (distance between floor and ceiling Y-positions).
16. Floor/ceiling width (`size[0]`) equals tunnel width.
17. Wall height (`size[1]`) equals tunnel height.

**Required/optional correctness:**
18. `floor.required` is `true`.
19. `ceiling.required` is `false`.
20. `left_wall.required` is `true`.
21. `right_wall.required` is `true`.
22. `end_wall.required` is `true`.
23. Exactly 4 required slots and 1 optional slot.

**Camera compatibility:**
24. `compatible_cameras` includes `'tunnel_push_forward'`.
25. `compatible_cameras` includes `'static'`.
26. `default_camera` is `'tunnel_push_forward'`.
27. `default_camera` is in `compatible_cameras`.
28. All camera names match `/^[a-z][a-z0-9_]*$/`.

**Fog configuration:**
29. `fog` is defined.
30. `fog.color` matches `/^#[0-9a-fA-F]{6}$/`.
31. `fog.near >= 0`.
32. `fog.far > fog.near`.

**Metadata:**
33. `description` is non-empty.
34. `preferred_aspect` is `'landscape'`.

**Material hints:**
35. No slot has `transparent: true`.
36. No slot has `fogImmune: true`.

**Registry integration:**
37. After importing `tunnel.ts`, `getGeometry('tunnel')` returns the geometry.
38. `getGeometryNames()` includes `'tunnel'`.
39. The returned geometry is deeply frozen (mutation throws TypeError).

**Slot utility integration:**
40. `getRequiredSlotNames(tunnelGeometry)` returns `['end_wall', 'floor', 'left_wall', 'right_wall']` (alphabetical order, 4 items).
41. `getOptionalSlotNames(tunnelGeometry)` returns `['ceiling']` (1 item).
42. `getAllSlotNames(tunnelGeometry)` returns all 5 slot names.
43. `isCameraCompatible(tunnelGeometry, 'tunnel_push_forward')` is `true`.
44. `isCameraCompatible(tunnelGeometry, 'lateral_track_left')` is `false`.

**Corridor plane coverage (AC-15):**
45. For each corridor plane (floor, ceiling, left_wall, right_wall): verify that the plane extends from Z ≥ `DEFAULT_CAMERA.position[2]` (Z=5) to Z ≤ end wall Z-position. This is computed from `position[2]` (center Z) ± `size[depth_axis] / 2`, accounting for rotation. For floor/ceiling (rotated into X/Z plane), depth axis is `size[1]`. For walls (rotated into Y/Z plane), depth axis is `size[0]`.

### Relevant Testable Claims

- **TC-05:** "The tunnel geometry produces convincing depth." This OBJ-019 spec provides the geometry definition. Visual validation of "convincing depth" is OBJ-060's responsibility (tuning cycle with Director Agent). OBJ-019's tests verify the spatial correctness preconditions — correct rotations, symmetric cross-section, sufficient plane coverage, no gaps.
- **TC-04:** The tunnel can be authored by slot name alone — no XYZ coordinates needed (manifest specifies `geometry: "tunnel"` and maps images to `floor`, `ceiling`, etc.).
- **TC-08:** The tunnel is one of the 8 proposed geometries. Its successful implementation contributes to validating that 8 geometries cover the design space.

## Integration Points

### Depends on

| Upstream | What OBJ-019 imports |
|---|---|
| **OBJ-005** (Scene Geometry Type Contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types from `./types`. `registerGeometry` function from `./registry`. `validateGeometryDefinition` (used internally by `registerGeometry`). |
| **OBJ-007** (Depth Model) | `SLOT_NAME_PATTERN` (for documentation/verification only — name validation is handled by `registerGeometry` calling `validateGeometryDefinition`). No runtime functions imported directly. |
| **OBJ-003** (Spatial math — via OBJ-005) | `Vec3`, `EulerRotation`, `Size2D` types used in slot definitions. `DEFAULT_CAMERA` constant referenced for plane sizing calculations. `PLANE_ROTATIONS` constants (if defined) for standard rotation values. |

### Consumed by

| Downstream | How it uses OBJ-019 |
|---|---|
| **OBJ-060** (Tunnel visual tuning) | Renders test videos with the tunnel geometry to tune spatial values via the Director Agent workflow. May propose modifications to slot positions/sizes based on visual feedback. |
| **OBJ-071** (SKILL.md geometry reference) | Documents the tunnel geometry: slot names, descriptions, compatible cameras, use cases, and image generation guidance for tunnel surfaces. |
| **OBJ-017** (Manifest validation) | Validates that manifests using `geometry: "tunnel"` provide correct plane keys (`floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`) via OBJ-005's registry lookup. |
| **OBJ-036** (Scene sequencer) | Looks up the tunnel geometry via `getGeometry('tunnel')` when rendering scenes that specify this geometry. |
| **OBJ-039** (Page-side renderer) | Creates Three.js meshes from the tunnel's slot definitions — positions planes, applies rotations, sets material properties based on `transparent` and `fogImmune` flags. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references tunnel's `compatible_cameras` against available camera path presets. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        tunnel.ts          # NEW: tunnelGeometry definition + registerGeometry() call
        index.ts           # MODIFIED: add `import './tunnel'` and re-export
```

## Open Questions

### OQ-A: Should the tunnel support an optional `subject` slot?

The tunnel currently defines only environmental surfaces — no dedicated slot for a subject (person, object) placed within the corridor. A manifest author wanting a subject in a tunnel scene would need to use `PlaneOverride` on one of the existing slots, which is awkward since wall/floor slots have rotations unsuitable for an upright subject.

**Recommendation:** Consider adding an optional `subject` slot at approximately `[0, -1, -10]` with rotation `[0, 0, 0]` (facing camera), `transparent: true`, `renderOrder: 2`. This would be the natural place for a character or object standing in the tunnel. Defer to OBJ-060 (tuning) to validate whether this slot enhances or clutters the tunnel scene. If added, the tunnel would have 6 slots (5 environmental + 1 subject), still within the 3-5 typical range with one bonus.

### OQ-B: Exact camera path travel range for `tunnel_push_forward`

The geometry's plane coverage is designed to support forward camera travel from approximately Z=5 to Z=-20 without edge reveals. The exact travel range is defined by the `tunnel_push_forward` camera path preset (OBJ-029), which has not yet been implemented. If the camera path pushes further than Z=-20, the fog should mask any near-clipping issues, but the corridor plane coverage should be validated against the actual camera path during OBJ-060 tuning.

### OQ-C: Should left/right wall textures be horizontally flipped?

When the same image is used for both walls (a common convenience), the left wall's `[0, PI/2, 0]` rotation and the right wall's `[0, -PI/2, 0]` rotation naturally display the texture mirrored. This may look correct (symmetrical tunnel) or wrong (text or asymmetric details appear reversed on one side). This is a SKILL.md guidance issue (OBJ-071), not a geometry issue — the geometry renders whatever textures are assigned.

---

I believe this specification fully defines the tunnel geometry. I'd like the challenger to verify the spatial math (particularly plane coverage and cross-section consistency), the acceptance criteria completeness, and whether the open questions need resolution before implementation.

---

## Round 2 — spec_challenger

I've read the proposed spec carefully. Let me evaluate it against the seed, the dependency specs, and implementability standards.

## Points of Agreement

The spec is well-structured overall. Specifically:

- **Spatial math is correct.** Cross-section consistency (8×6), symmetry about origin, end wall sizing matching the cross-section, rotation values per seed Section 8.4 — all verified and sound.
- **Required/optional slot choices are well-reasoned.** Ceiling optional for open-air corridors makes sense per the seed's own example in Section 8.6.
- **Fog configuration is sensible.** Black fog, near=15/far=50, consistent with a corridor aesthetic.
- **Design decisions are thorough and well-justified.** D1–D13 cover the key rationale.
- **Reserved slot name compliance is correct.** All five names appear in OBJ-005's reserved table with matching orientations.

## Issues

### Issue 1 — Major: PlaneSlot vs DepthSlot type ambiguity

OBJ-005 defines `SceneGeometry.slots` as `Record<string, PlaneSlot>`. OBJ-007 defines a separate `DepthSlot` type with additional fields (`name`, `promptGuidance`, `expectsAlpha`) and its own `SlotSet = Record<SlotName, DepthSlot>`. OBJ-007's "Consumed by" table explicitly states: **"OBJ-018-025: Each imports `DepthSlot`, `SlotSet`, and optionally `DEFAULT_SLOT_TAXONOMY`."**

The tunnel spec uses OBJ-005's `PlaneSlot` only. An implementer reading OBJ-007's integration table would expect to also define a `SlotSet` with `DepthSlot` entries. These are structurally different types:

| Field | PlaneSlot (OBJ-005) | DepthSlot (OBJ-007) |
|---|---|---|
| `name` | ❌ (key-only) | ✅ |
| `promptGuidance` | ❌ | ✅ |
| `expectsAlpha` | ❌ | ✅ |
| `transparent` | ✅ | ❌ |
| `fogImmune` | ✅ | ❌ |

**Proposed fix:** Add an explicit Design Decision (D14 or similar) that states:
1. The canonical type for `SceneGeometry.slots` is OBJ-005's `PlaneSlot` — that's what `registerGeometry()` accepts and validates.
2. OBJ-007's `DepthSlot` overlaps but is not the same type. The two verified dependency specs have an unresolved type gap. OBJ-019 follows OBJ-005 as the authoritative interface for geometry registration.
3. The fields unique to `DepthSlot` (`name`, `promptGuidance`, `expectsAlpha`) are addressed as follows: `name` is redundant (it's the Record key), `promptGuidance` and `expectsAlpha` are provided via a companion export (see Issue 2).

This prevents implementer confusion about which imports to use.

### Issue 2 — Major: No image generation guidance for tunnel slots

OBJ-007's integration table says OBJ-051 (SKILL.md) and OBJ-053 (Prompt template library) consume `promptGuidance` and `expectsAlpha` from slot declarations. The tunnel spec provides neither. For the blind-authoring constraint (C-06), an LLM needs to know:
- What kind of image to generate for a tunnel `floor` (elongated perspective texture? repeating pattern?)
- Whether `end_wall` needs transparency (no — it's a distant backdrop)
- How `left_wall` and `right_wall` images should be composed

Without this, OBJ-071 and OBJ-053 have nothing to work with for tunnel-specific guidance.

**Proposed fix:** Add a `tunnelSlotGuidance` companion export (or a documentation section) that provides per-slot:

```typescript
export const tunnelSlotGuidance: Record<string, {
  promptGuidance: string;
  expectsAlpha: boolean;
}>;
```

With entries like:
- `floor`: `{ promptGuidance: "Ground/floor surface texture, elongated perspective, repeating pattern works well. Stone, dirt, water, metal grating.", expectsAlpha: false }`
- `end_wall`: `{ promptGuidance: "Distant scene visible at the end of the corridor. Light source, exit, vanishing point target.", expectsAlpha: false }`
- etc.

This keeps the `SceneGeometry` registration using `PlaneSlot` (per OBJ-005) while providing the metadata OBJ-051/OBJ-053 need.

### Issue 3 — Minor: AC-15 lacks computation method for verifying Z-extent of rotated planes

AC-15 says corridor planes "extend from behind the default camera start position" but doesn't specify how to compute a rotated plane's Z-extent. The test strategy (test 45) explains the computation, but acceptance criteria should be self-contained — an implementer writing tests from ACs alone would need to guess the math.

**Proposed fix:** Revise AC-15 to:

> **AC-15:** For each corridor plane (floor, ceiling, left_wall, right_wall), the Z-extent — computed as `position[2] ± size[depthAxis]/2` where `depthAxis` is index 1 for floor/ceiling and index 0 for walls — spans from at least `DEFAULT_CAMERA.position[2]` (inclusive) to at most `end_wall.position[2]` (inclusive).

### Issue 4 — Minor: Zero rear-edge margin warrants an explicit constraint on camera paths

Floor/ceiling/walls have their rear edge at exactly Z=+5, which is `DEFAULT_CAMERA.position[2]`. The spec's spatial boundary table acknowledges this is at the limit. While forward-looking cameras won't reveal this edge, the margin is exactly zero.

**Proposed fix:** Add a note in the "Spatial Boundary Conditions" table or as a new design decision stating: "Camera path presets in `compatible_cameras` must not position the camera at Z > `DEFAULT_CAMERA.position[2]` (Z=5). This is a constraint that OBJ-029 (tunnel_push_forward) and other tunnel-compatible camera implementations must respect." This makes the implicit assumption explicit for downstream implementers.

### Issue 5 — Minor: OQ-A (subject slot) should have a stronger recommendation

The open question about an optional `subject` slot is important for usability. A tunnel with no subject slot means the LLM author has no standard way to place a character in the corridor. The recommendation says "defer to OBJ-060," but OBJ-060 is visual tuning — it shouldn't be making structural decisions about slot definitions.

**Proposed fix:** Either (a) resolve it now by including an optional `subject` slot with specific position/rotation/size values (the spec already proposes `[0, -1, -10]` with `[0,0,0]` rotation and `transparent: true`), or (b) explicitly defer it with a concrete follow-up mechanism: "If a subject slot is needed, it should be added as a revision to OBJ-019 after OBJ-060 validates the base tunnel, not as part of the OBJ-060 tuning cycle." The current wording blurs the boundary between geometry definition and visual tuning.

### Issue 6 — Nit: Test 40 assumes alphabetical ordering not guaranteed by OBJ-005

Test 40 asserts `getRequiredSlotNames(tunnelGeometry)` returns `['end_wall', 'floor', 'left_wall', 'right_wall']` in alphabetical order. OBJ-005's spec for `getRequiredSlotNames` says "Returns Array of slot name strings where required === true" with no ordering guarantee.

**Proposed fix:** Either note that the test should sort both arrays before comparison, or document that the assertion is order-independent (set equality). This is just a test strategy clarity issue.

---

**Summary:** Two major issues (type ambiguity and missing prompt guidance), four minor issues. The major issues are both about the gap between OBJ-005 and OBJ-007 — they need explicit resolution in this spec since OBJ-019 depends on both. Please address Issues 1 and 2 before I'll consider convergence. Issues 3–6 are fixable in a single pass.

---

## Round 3 — spec_author

# Revised Specification: Tunnel Scene Geometry (OBJ-019)

All six issues addressed. Here's the complete revised spec:

---

## Summary

OBJ-019 defines the **tunnel scene geometry** — the concrete `SceneGeometry` definition registered as `'tunnel'` in the geometry registry. The tunnel arranges five planes (floor, ceiling, left wall, right wall, end wall) into a box-like corridor receding along the negative Z-axis. When the camera pushes forward, walls undergo real perspective distortion — converging to a vanishing point — producing the signature 2.5D depth effect described in seed Section 4.2. This is the geometry that demonstrates depthkit's core differentiator: perspective projection that flat 2D parallax cannot replicate.

## Interface Contract

### Module Export

```typescript
// src/scenes/geometries/tunnel.ts

import type { SceneGeometry } from './types';

/**
 * The tunnel scene geometry definition.
 * 
 * Exported for direct reference in tests and documentation.
 * Also self-registers via registerGeometry() at module load time.
 */
export const tunnelGeometry: SceneGeometry;

/**
 * Per-slot image generation guidance for the tunnel geometry.
 * Consumed by OBJ-051 (SKILL.md) and OBJ-053 (prompt template library)
 * to provide LLM authors with tunnel-specific image prompting advice.
 *
 * Keys match tunnelGeometry.slots keys exactly.
 */
export const tunnelSlotGuidance: Record<string, {
  promptGuidance: string;
  expectsAlpha: boolean;
}>;
```

### Side Effect: Registration

When `tunnel.ts` is imported, it calls `registerGeometry(tunnelGeometry)` as a module-level side effect, per the OBJ-005 registry pattern (D2). The barrel export `src/scenes/geometries/index.ts` must import `./tunnel` to trigger registration.

### Geometry Definition

```typescript
const tunnelGeometry: SceneGeometry = {
  name: 'tunnel',

  description:
    'A corridor with floor, ceiling, and walls receding to a vanishing point. ' +
    'Camera pushes forward on the Z-axis for a "traveling through a space" effect. ' +
    'Walls undergo real perspective distortion — converging toward the end wall. ' +
    'Best for: corridors, hallways, underwater passages, cave systems, sci-fi tunnels, ' +
    'forest paths, and any scene where the viewer moves through an enclosed space.',

  slots: {
    floor: {
      position: [0, -3, -20] as Vec3,
      rotation: [-Math.PI / 2, 0, 0] as EulerRotation,
      size: [8, 50] as Size2D,
      required: true,
      description: 'Ground surface extending forward into the tunnel.',
      renderOrder: 0,
      transparent: false,
      fogImmune: false,
    },
    ceiling: {
      position: [0, 3, -20] as Vec3,
      rotation: [Math.PI / 2, 0, 0] as EulerRotation,
      size: [8, 50] as Size2D,
      required: false,
      description: 'Overhead surface extending forward into the tunnel. Omit for open-air passages.',
      renderOrder: 0,
      transparent: false,
      fogImmune: false,
    },
    left_wall: {
      position: [-4, 0, -20] as Vec3,
      rotation: [0, Math.PI / 2, 0] as EulerRotation,
      size: [50, 6] as Size2D,
      required: true,
      description: 'Left boundary wall receding to the vanishing point.',
      renderOrder: 1,
      transparent: false,
      fogImmune: false,
    },
    right_wall: {
      position: [4, 0, -20] as Vec3,
      rotation: [0, -Math.PI / 2, 0] as EulerRotation,
      size: [50, 6] as Size2D,
      required: true,
      description: 'Right boundary wall receding to the vanishing point.',
      renderOrder: 1,
      transparent: false,
      fogImmune: false,
    },
    end_wall: {
      position: [0, 0, -45] as Vec3,
      rotation: [0, 0, 0] as EulerRotation,
      size: [8, 6] as Size2D,
      required: true,
      description: 'Distant terminus of the tunnel, visible as the vanishing point target.',
      renderOrder: 0,
      transparent: false,
      fogImmune: false,
    },
  },

  compatible_cameras: [
    'tunnel_push_forward',
    'slow_push_forward',
    'static',
    'gentle_float',
  ],
  default_camera: 'tunnel_push_forward',

  fog: {
    color: '#000000',
    near: 15,
    far: 50,
  },

  preferred_aspect: 'landscape',
};
```

### Slot Guidance Definition

```typescript
const tunnelSlotGuidance: Record<string, {
  promptGuidance: string;
  expectsAlpha: boolean;
}> = {
  floor: {
    promptGuidance:
      'Ground/floor surface texture viewed in perspective. Elongated or repeating patterns work well ' +
      '(stone tiles, dirt path, water surface, metal grating, wooden planks). Avoid centered compositions — ' +
      'the texture will be stretched along the depth axis. Wide, seamless textures are ideal.',
    expectsAlpha: false,
  },
  ceiling: {
    promptGuidance:
      'Overhead surface texture viewed in perspective. Similar to floor — repeating patterns, ' +
      'architectural details (rock ceiling, pipes, vines, stalactites, industrial beams). ' +
      'Can be omitted for open-air passages.',
    expectsAlpha: false,
  },
  left_wall: {
    promptGuidance:
      'Wall surface texture viewed in side perspective, receding to a vanishing point. ' +
      'Elongated textures with horizontal detail work well (brick, stone, coral, tree trunks, panels). ' +
      'Avoid text or asymmetric details that look wrong when mirrored on the opposite wall.',
    expectsAlpha: false,
  },
  right_wall: {
    promptGuidance:
      'Wall surface texture viewed in side perspective, receding to a vanishing point. ' +
      'Same guidance as left_wall. Often the same image is used for both walls to create a symmetrical corridor. ' +
      'If using different images, ensure similar style/palette for visual coherence.',
    expectsAlpha: false,
  },
  end_wall: {
    promptGuidance:
      'Distant scene visible at the far end of the corridor — the vanishing point target. ' +
      'A light source, exit doorway, distant landscape, portal, or glowing terminus. ' +
      'Will be heavily fog-faded by default, so high-contrast or bright images read best at distance.',
    expectsAlpha: false,
  },
};
```

### Barrel Export Addition

```typescript
// src/scenes/geometries/index.ts — add to existing barrel
import './tunnel'; // triggers registration side effect
export { tunnelGeometry, tunnelSlotGuidance } from './tunnel';
```

## Design Decisions

### D1: Slot positions centered at Z=-20 with depth span from camera to Z=-45

The seed example (Section 8.6) centers floor/walls at Z=-15 with the end wall at Z=-35. I've pushed all planes deeper: floor/ceiling/walls centered at Z=-20, end wall at Z=-45. This creates a 50-unit total depth corridor (camera starts at approximately Z=5 per `DEFAULT_CAMERA`, end wall at Z=-45).

**Rationale:** A longer corridor gives the camera more Z-travel before reaching the end wall, producing a more dramatic and sustained forward-push effect. The seed values were explicitly labeled as a sketch ("These Z values are defaults" — Section 4.1). With the camera default at Z=5 and a `tunnel_push_forward` preset likely traveling to around Z=-15 or Z=-20, the end wall at Z=-45 ensures it remains visible as a distant vanishing point target throughout the animation, never approached too closely. The fog (near=15, far=50) progressively fades the end wall, preventing it from looking flat.

These values are subject to the Director Agent tuning cycle (OBJ-060). The initial values are chosen to be mathematically safe (no clipping, no edge reveal with reasonable camera paths) while providing a strong starting point for visual tuning.

### D2: Tunnel cross-section is 8 units wide × 6 units tall

Floor and ceiling are at Y=-3 and Y=3 (6 units apart). Left and right walls are at X=-4 and X=4 (8 units apart). This creates a slightly wider-than-tall cross-section (4:3 ratio), which maps well to the landscape viewport and avoids a claustrophobic feel.

**Rationale:** A 1:1 or taller-than-wide cross-section would waste horizontal viewport space in 16:9. The 8×6 proportion means the walls, floor, and ceiling are all visible in the viewport at FOV=50° without extreme foreshortening of any single surface. The camera, centered at Y=0, sits at the vertical midpoint of the tunnel, giving equal visual weight to floor and ceiling.

### D3: Wall/floor/ceiling planes are 50 units deep (on their long axis)

The floor, ceiling, left wall, and right wall all use 50 units on the axis that extends into the tunnel (the depth axis when rotated). Since these planes are centered at Z=-20, they span from approximately Z=+5 (behind the camera's start position) to Z=-45 (coinciding with the end wall).

**Rationale:** The plane must extend behind the camera's starting position to prevent the near edge from being visible in the initial frames. And it must reach the end wall so there's no visible gap between the corridor and the terminus. The 50-unit depth provides margin for camera motion — even if the camera starts slightly behind Z=5 or pushes past Z=-20, the plane edges won't be revealed. This directly addresses TC-05's requirement for "convincing depth" and the seed's emphasis on no edge reveals.

### D4: Floor and ceiling size is [8, 50]; walls are [50, 6]

Floor/ceiling planes are rotated to lie flat (X/Z plane), so their `size[0]=8` spans the tunnel width (X-axis) and `size[1]=50` spans the tunnel depth (Z-axis). Wall planes are rotated to stand vertically along the tunnel (Y/Z plane), so `size[0]=50` spans the depth (Z-axis) and `size[1]=6` spans the height (Y-axis).

**Rationale:** After rotation, each plane's width dimension matches the tunnel's cross-section, and its height/depth dimension extends the full corridor length. The sizes are set to create seamless seams where floor meets walls and walls meet ceiling.

### D5: End wall size is [8, 6] — matching the cross-section

The end wall is a standard camera-facing plane at Z=-45. Its size matches the tunnel cross-section (8 wide × 6 tall) so it "caps" the far end of the corridor without gaps.

**Rationale:** A perfectly sized end wall prevents visible gaps at the joints where walls/floor/ceiling meet the terminus. As the camera pushes forward, the end wall grows larger in the viewport due to perspective — this is the core vanishing-point effect.

### D6: Ceiling is optional; all other slots are required

An open-air tunnel (no ceiling) is a valid and common scene type — think canyon paths, open corridors, forest trails. Making ceiling optional enables this variation without a separate geometry. Floor and both walls are structurally essential to the tunnel illusion; the end wall provides the vanishing point target.

**Rationale:** Seed Section 8.6 shows `ceiling.required: false` in the tunnel example. This preserves the geometry's spatial integrity when ceiling is omitted — the floor and walls still create converging perspective lines. Dropping floor or either wall would break the tunnel illusion.

### D7: Fog defaults to black, near=15, far=50

Black fog starting at distance 15 from the camera and reaching full opacity at distance 50. This is darker and starts closer than the seed sketch (which used near=10, far=40).

**Rationale:** The tunnel is a naturally enclosed, dimly lit space. Black fog:
1. Hides the hard edge of the end wall at Z=-45 by fading it into darkness.
2. Creates natural atmospheric depth — closer surfaces are vivid, distant surfaces fade.
3. Masks any texture seams at far distances where wall/floor/ceiling meet the end wall.

Near=15 means fog only starts affecting objects more than 15 units from the camera (10 units into the scene from the camera's default Z=5 position). This keeps the immediate tunnel environment crisp while fading the deep end. Far=50 means objects 50+ units from the camera are fully fogged — the end wall at distance ~50 units from the start position is nearly invisible, appearing as a dark terminus.

The fog is overridable per-scene via the manifest (per OBJ-005's `SceneGeometry.fog` + manifest override mechanism in OBJ-004).

### D8: Compatible cameras include both tunnel-specific and generic presets

`tunnel_push_forward` is the signature motion. `slow_push_forward` provides a gentler, more generic forward push. `static` allows a frozen establishing shot. `gentle_float` enables subtle, ambient movement for atmospheric scenes.

**Rationale:** These four presets span the common use cases — dramatic forward movement, gentle forward movement, no movement, and ambient drift. Camera presets like `lateral_track_left` are excluded because lateral tracking in a narrow tunnel would reveal the side edges of the floor/ceiling planes. The `compatible_cameras` list acts as a safety net (seed C-06, AP-03) — only cameras validated to not cause edge reveals are allowed. Additional presets can be added to this list as they are implemented and validated (OBJ-026+).

**Constraint on compatible camera paths:** All camera path presets listed in `compatible_cameras` must not position the camera at Z > `DEFAULT_CAMERA.position[2]` (Z=5). The corridor planes' rear edges are at exactly Z=+5 (zero margin). Any camera starting behind Z=5 or drifting backward past Z=5 would reveal the rear edges of the corridor planes. This is a binding constraint that OBJ-029 (`tunnel_push_forward`) and any other tunnel-compatible camera implementations must respect. The constraint should be documented in the camera path presets' own acceptance criteria.

### D9: preferred_aspect is 'landscape'

Tunnels work best in landscape orientation where the horizontal viewport maps to the tunnel's wider cross-section. In portrait mode, the tall narrow viewport would show mostly floor and ceiling with very thin wall slivers, reducing the vanishing-point impact.

**Rationale:** The tunnel cross-section (8:6) is landscape-proportioned. Portrait mode would require significantly different plane proportions to maintain the effect — that adaptation is OBJ-040/OBJ-045's responsibility. The advisory `preferred_aspect: 'landscape'` guides SKILL.md (OBJ-071) to recommend landscape orientation for tunnel scenes.

### D10: No use of DEFAULT_SLOT_TAXONOMY

The tunnel geometry defines a completely independent `SlotSet`. The default taxonomy (sky, back_wall, midground, subject, near_fg) describes a layered backdrop arrangement — fundamentally different from a tunnel's corridor structure. The tunnel's floor/ceiling/walls have no meaningful correspondence to the default slots.

**Rationale:** Per OBJ-007 D1 (two-tier slot model), geometries with fundamentally different spatial structures define their own slot sets. A tunnel's `floor` is a horizontal plane at Y=-3 with rotation `[-PI/2, 0, 0]`; the default taxonomy's slots are all upright planes facing the camera. Forcing the tunnel into the default taxonomy would produce incorrect spatial relationships and confusing slot names.

### D11: renderOrder values — end_wall and floor/ceiling at 0, walls at 1

End wall, floor, and ceiling are at renderOrder 0. Left and right walls are at renderOrder 1. This hierarchy ensures that when walls overlap with floor/ceiling at the edges (due to perspective convergence), the walls draw on top.

**Rationale:** In practice, depth-buffer testing handles most overlap correctly. But for cases where planes are nearly coplanar at joints (wall-floor seam), explicit renderOrder prevents z-fighting artifacts. Walls drawing on top of floor/ceiling at the seams produces the cleaner visual result because wall edges are more visually prominent.

### D12: No transparency on any slot

All tunnel slots use `transparent: false`. Tunnel surfaces are solid environmental surfaces — they are not meant to be seen through. Subject elements or particles in a tunnel scene would require a separate geometry (or a future revision adding an optional transparent overlay slot — see OQ-A).

**Rationale:** Transparent materials with large plane overlap (as in a tunnel where all surfaces converge at the vanishing point) cause significant draw-order complexity and potential visual artifacts. Keeping all materials opaque simplifies rendering and aligns with the tunnel's spatial concept — you're inside an enclosed space, not looking through translucent layers.

### D13: All slots have fogImmune: false

Every slot in the tunnel is subject to fog. Unlike a stage geometry where a sky backdrop might need fogImmune to remain vivid at extreme distance, the tunnel's aesthetic depends on fog fading all surfaces uniformly to create depth.

**Rationale:** The end wall at Z=-45 should fade into darkness, not stand out as a flat rectangle. Floor and walls should progressively darken into the distance. Fog immunity would break the tunnel's depth illusion.

### D14: OBJ-005's PlaneSlot is the authoritative type for geometry registration; OBJ-007 guidance is a companion export

OBJ-005 defines `SceneGeometry.slots` as `Record<string, PlaneSlot>`. OBJ-007 defines `DepthSlot` with additional fields (`name`, `promptGuidance`, `expectsAlpha`). These are overlapping but distinct types — an unresolved gap between the two dependency specs.

OBJ-019 follows **OBJ-005 as the authoritative interface** for geometry registration, because `registerGeometry()` accepts `SceneGeometry` whose `slots` are `Record<string, PlaneSlot>`. The fields unique to OBJ-007's `DepthSlot` that are absent from `PlaneSlot` are addressed as follows:

- **`name`:** Redundant — it duplicates the Record key. OBJ-005's design (D8) intentionally uses Record keys rather than a `name` field.
- **`promptGuidance` and `expectsAlpha`:** These are image-generation metadata, not spatial data needed by the renderer. They are provided via a **companion export** (`tunnelSlotGuidance`) that maps slot names to their prompt guidance and alpha expectations. This keeps the `SceneGeometry` registration clean (spatial data only) while satisfying OBJ-051 (SKILL.md) and OBJ-053 (prompt template library) needs.

**Rationale:** Mixing rendering-irrelevant metadata (`promptGuidance`) into the `PlaneSlot` interface that gets frozen in the geometry registry would bloat the contract with data the renderer never reads. The companion export pattern keeps concerns separated: `tunnelGeometry` for spatial/rendering data, `tunnelSlotGuidance` for authoring/documentation data. Both are keyed by the same slot names, ensuring consistency.

### D15: No subject slot in V1; deferred as a post-tuning revision

The tunnel currently defines only environmental surfaces — no dedicated slot for a subject (person, object) placed within the corridor. Adding a subject slot is a **geometry definition change**, not a visual tuning parameter, and therefore does not belong in OBJ-060's scope.

**Resolution:** A subject slot is **not included in the initial tunnel definition**. If user testing or OBJ-060 visual tuning reveals that a subject slot is needed for common tunnel use cases, it should be added as a **revision to OBJ-019** (updating the geometry definition with a new optional slot), not as a side effect of the OBJ-060 tuning cycle. The revision would add an optional `subject` slot at approximately `[0, -1, -10]` with rotation `[0, 0, 0]`, `transparent: true`, `renderOrder: 2`.

**Rationale:** Including an unvalidated subject slot now adds complexity without proven value. The tunnel's primary purpose is the corridor flythrough effect (TC-05). Subjects placed arbitrarily in a deep corridor may look awkward — the position needs to be tuned relative to the camera path's focal point, which isn't known until `tunnel_push_forward` (OBJ-029) is implemented. Deferring to a specific revision keeps the initial definition focused and testable.

## Acceptance Criteria

- [ ] **AC-01:** A module `src/scenes/geometries/tunnel.ts` exports `tunnelGeometry` as a `SceneGeometry` conforming to OBJ-005's interface.
- [ ] **AC-02:** Importing `tunnel.ts` calls `registerGeometry(tunnelGeometry)` as a module-level side effect, registering the geometry under the name `'tunnel'`.
- [ ] **AC-03:** `tunnelGeometry.name` is `'tunnel'`.
- [ ] **AC-04:** `tunnelGeometry.slots` contains exactly 5 keys: `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`.
- [ ] **AC-05:** `floor` slot has `rotation: [-Math.PI/2, 0, 0]` (lies flat, facing up), `required: true`.
- [ ] **AC-06:** `ceiling` slot has `rotation: [Math.PI/2, 0, 0]` (lies flat, facing down), `required: false`.
- [ ] **AC-07:** `left_wall` slot has `rotation: [0, Math.PI/2, 0]` (faces right), `required: true`.
- [ ] **AC-08:** `right_wall` slot has `rotation: [0, -Math.PI/2, 0]` (faces left), `required: true`.
- [ ] **AC-09:** `end_wall` slot has `rotation: [0, 0, 0]` (faces camera), `required: true`.
- [ ] **AC-10:** Floor and ceiling Y-positions are symmetric about Y=0 (i.e., `floor.position[1] === -ceiling.position[1]`).
- [ ] **AC-11:** Left and right wall X-positions are symmetric about X=0 (i.e., `left_wall.position[0] === -right_wall.position[0]`).
- [ ] **AC-12:** End wall size matches the tunnel cross-section: `end_wall.size[0]` equals the distance between left and right walls (`Math.abs(left_wall.position[0]) + Math.abs(right_wall.position[0])`), and `end_wall.size[1]` equals the distance between floor and ceiling (`Math.abs(floor.position[1]) + Math.abs(ceiling.position[1])`).
- [ ] **AC-13:** Floor/ceiling plane width (`size[0]`) equals the tunnel width (distance between left and right wall X-positions).
- [ ] **AC-14:** Wall plane height (`size[1]`) equals the tunnel height (distance between floor and ceiling Y-positions).
- [ ] **AC-15:** For each corridor plane (floor, ceiling, left_wall, right_wall), the Z-extent — computed as `position[2] ± size[depthAxis]/2` where `depthAxis` is index 1 for floor/ceiling and index 0 for walls — spans from at least `DEFAULT_CAMERA.position[2]` (Z=5, inclusive) to at most `end_wall.position[2]` (inclusive).
- [ ] **AC-16:** `tunnelGeometry.compatible_cameras` contains `'tunnel_push_forward'` and at least `'static'`.
- [ ] **AC-17:** `tunnelGeometry.default_camera` is `'tunnel_push_forward'` and appears in `compatible_cameras`.
- [ ] **AC-18:** `tunnelGeometry.fog` is defined with `color` matching `/^#[0-9a-fA-F]{6}$/`, `near >= 0`, and `far > near`.
- [ ] **AC-19:** `tunnelGeometry.description` is non-empty and mentions corridor/tunnel and vanishing point.
- [ ] **AC-20:** `tunnelGeometry.preferred_aspect` is `'landscape'`.
- [ ] **AC-21:** `tunnelGeometry` passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-22:** After importing `tunnel.ts`, `getGeometry('tunnel')` returns the registered geometry.
- [ ] **AC-23:** All slot names match `/^[a-z][a-z0-9_]*$/` (SLOT_NAME_PATTERN from OBJ-007).
- [ ] **AC-24:** All slot `description` fields are non-empty strings.
- [ ] **AC-25:** All slot `size` components are > 0.
- [ ] **AC-26:** No slot has `transparent: true` (all tunnel surfaces are opaque).
- [ ] **AC-27:** No slot has `fogImmune: true` (all surfaces participate in fog).
- [ ] **AC-28:** The geometry has exactly 4 required slots and 1 optional slot (ceiling).
- [ ] **AC-29:** `tunnelSlotGuidance` is exported and contains exactly the same keys as `tunnelGeometry.slots`.
- [ ] **AC-30:** Every entry in `tunnelSlotGuidance` has a non-empty `promptGuidance` string and a boolean `expectsAlpha` field.
- [ ] **AC-31:** All `tunnelSlotGuidance` entries have `expectsAlpha: false` (tunnel surfaces are opaque environmental textures).

## Edge Cases and Error Handling

### Structural Consistency

| Condition | Expected Behavior |
|---|---|
| Ceiling omitted by manifest author | Tunnel renders as open-top corridor. Floor, walls, and end wall create sufficient depth illusion. No rendering error. |
| All 5 slots provided | Full enclosed tunnel with all surfaces textured. |
| Manifest provides plane key not in slots (e.g., `subject`) | Caught by manifest validation (OBJ-017 via OBJ-005 `getAllSlotNames`) — error: `"Plane 'subject' is not a valid slot for geometry 'tunnel'. Valid slots: ceiling, end_wall, floor, left_wall, right_wall"` |
| Manifest uses incompatible camera (e.g., `lateral_track_left`) | Caught by manifest validation (OBJ-041 via OBJ-005 `isCameraCompatible`) — error naming the incompatible camera and listing compatible options. |
| Manifest overrides floor position via PlaneOverride | Valid per OBJ-007's override mechanism. The override produces a new `ResolvedSlot`; the geometry's registered definition is not mutated (OBJ-005 D9). |

### Spatial Boundary Conditions

| Condition | Notes |
|---|---|
| Camera at default position [0, 0, 5] looking at [0, 0, -30] | All four corridor planes extend behind Z=5 (plane center at Z=-20 with 50-unit depth → rear edge at approximately Z=+5). Floor/ceiling/wall near edges are at or behind the camera — they fill the viewport without revealing back edges. |
| Camera pushes forward to Z=-15 | The camera is now 30 units from the end wall. Corridor planes still extend 5 units behind (their rear edge at Z≈+5, camera at Z=-15 → 20 units of plane behind the camera). No rear edge reveal. |
| Camera pushes very deep (Z=-30) | The camera is 15 units from the end wall. Corridor planes rear edge at Z≈+5, 35 units behind the camera. Front edges at Z≈-45, coinciding with end wall. The forward camera push reveals more of the end wall as it grows in the viewport. Camera path presets must cap forward travel to avoid clipping through the end wall. |
| Camera positioned at Z > 5 (behind corridor rear edge) | **Violated constraint.** Rear edges of corridor planes would be visible. All tunnel-compatible camera paths are prohibited from positioning the camera at Z > `DEFAULT_CAMERA.position[2]` (see D8). |
| Portrait mode (9:16) | The 8-unit tunnel width is narrower than the 6-unit height in viewport terms. With a 9:16 aspect ratio and FOV=50°, the visible width at the camera's position is narrower than in landscape, so the walls may be more prominent and the floor/ceiling less visible. The geometry renders correctly but may not look ideal — `preferred_aspect: 'landscape'` advises against this. OBJ-045 handles portrait adaptation. |

### Texture Considerations

| Condition | Notes |
|---|---|
| Floor/ceiling textures with non-matching aspect ratios | The texture stretches to fill the plane geometry. For a floor plane of size [8, 50], a 1:1 image would appear stretched along the depth axis. `tunnelSlotGuidance.floor.promptGuidance` advises generating elongated or repeating patterns. |
| Left and right wall textures are the same image | Valid and common — symmetrical tunnels. The right wall's `[0, -PI/2, 0]` rotation mirrors the left wall's perspective naturally. `tunnelSlotGuidance` notes this pattern. |
| End wall texture aspect ratio vs slot size | End wall is [8, 6] (4:3). A 16:9 image would appear slightly compressed vertically. Since the end wall is distant and fog-faded, minor distortion is usually invisible. |

## Test Strategy

### Unit Tests

**Geometry definition validity:**
1. `tunnelGeometry` passes `validateGeometryDefinition()` with empty error array.
2. `tunnelGeometry.name` is `'tunnel'`.
3. `tunnelGeometry.slots` has exactly 5 entries.
4. Each slot name matches `SLOT_NAME_PATTERN`.
5. Each slot has non-empty `description`.
6. Each slot `size` components are > 0.

**Slot spatial correctness:**
7. Floor rotation is `[-Math.PI/2, 0, 0]`.
8. Ceiling rotation is `[Math.PI/2, 0, 0]`.
9. Left wall rotation is `[0, Math.PI/2, 0]`.
10. Right wall rotation is `[0, -Math.PI/2, 0]`.
11. End wall rotation is `[0, 0, 0]`.
12. Floor and ceiling Y-positions are symmetric about Y=0.
13. Left and right wall X-positions are symmetric about X=0.
14. End wall width equals tunnel width (distance between wall X-positions).
15. End wall height equals tunnel height (distance between floor and ceiling Y-positions).
16. Floor/ceiling width (`size[0]`) equals tunnel width.
17. Wall height (`size[1]`) equals tunnel height.

**Required/optional correctness:**
18. `floor.required` is `true`.
19. `ceiling.required` is `false`.
20. `left_wall.required` is `true`.
21. `right_wall.required` is `true`.
22. `end_wall.required` is `true`.
23. Exactly 4 required slots and 1 optional slot.

**Camera compatibility:**
24. `compatible_cameras` includes `'tunnel_push_forward'`.
25. `compatible_cameras` includes `'static'`.
26. `default_camera` is `'tunnel_push_forward'`.
27. `default_camera` is in `compatible_cameras`.
28. All camera names match `/^[a-z][a-z0-9_]*$/`.

**Fog configuration:**
29. `fog` is defined.
30. `fog.color` matches `/^#[0-9a-fA-F]{6}$/`.
31. `fog.near >= 0`.
32. `fog.far > fog.near`.

**Metadata:**
33. `description` is non-empty.
34. `preferred_aspect` is `'landscape'`.

**Material hints:**
35. No slot has `transparent: true`.
36. No slot has `fogImmune: true`.

**Registry integration:**
37. After importing `tunnel.ts`, `getGeometry('tunnel')` returns the geometry.
38. `getGeometryNames()` includes `'tunnel'`.
39. The returned geometry is deeply frozen (mutation throws TypeError).

**Slot utility integration (order-independent comparisons — sort both arrays before asserting):**
40. `getRequiredSlotNames(tunnelGeometry)` returns a set equal to `{'end_wall', 'floor', 'left_wall', 'right_wall'}` (4 items).
41. `getOptionalSlotNames(tunnelGeometry)` returns a set equal to `{'ceiling'}` (1 item).
42. `getAllSlotNames(tunnelGeometry)` returns all 5 slot names (set equality).
43. `isCameraCompatible(tunnelGeometry, 'tunnel_push_forward')` is `true`.
44. `isCameraCompatible(tunnelGeometry, 'lateral_track_left')` is `false`.

**Corridor plane Z-coverage (AC-15):**
45. For each corridor plane (floor, ceiling, left_wall, right_wall): compute Z-extent as `position[2] ± size[depthAxis]/2` where `depthAxis` is index 1 for floor/ceiling and index 0 for walls. Verify rear edge Z ≥ `DEFAULT_CAMERA.position[2]` (5) and front edge Z ≤ `end_wall.position[2]` (-45).

**Slot guidance companion export:**
46. `tunnelSlotGuidance` has exactly the same keys as `tunnelGeometry.slots`.
47. Every entry in `tunnelSlotGuidance` has a non-empty `promptGuidance` string.
48. Every entry in `tunnelSlotGuidance` has `expectsAlpha` as `false`.

### Relevant Testable Claims

- **TC-05:** "The tunnel geometry produces convincing depth." This OBJ-019 spec provides the geometry definition. Visual validation of "convincing depth" is OBJ-060's responsibility (tuning cycle with Director Agent). OBJ-019's tests verify the spatial correctness preconditions — correct rotations, symmetric cross-section, sufficient plane coverage, no gaps.
- **TC-04:** The tunnel can be authored by slot name alone — no XYZ coordinates needed (manifest specifies `geometry: "tunnel"` and maps images to `floor`, `ceiling`, etc.).
- **TC-08:** The tunnel is one of the 8 proposed geometries. Its successful implementation contributes to validating that 8 geometries cover the design space.

## Integration Points

### Depends on

| Upstream | What OBJ-019 imports |
|---|---|
| **OBJ-005** (Scene Geometry Type Contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types from `./types`. `registerGeometry` function from `./registry`. `validateGeometryDefinition` (used internally by `registerGeometry`). |
| **OBJ-007** (Depth Model) | `SLOT_NAME_PATTERN` (for documentation/verification only — name validation is handled by `registerGeometry` calling `validateGeometryDefinition`). No runtime functions imported directly. |
| **OBJ-003** (Spatial math — via OBJ-005) | `Vec3`, `EulerRotation`, `Size2D` types used in slot definitions. `DEFAULT_CAMERA` constant referenced for plane sizing calculations and the Z=5 rear-edge constraint. |

### Consumed by

| Downstream | How it uses OBJ-019 |
|---|---|
| **OBJ-060** (Tunnel visual tuning) | Renders test videos with the tunnel geometry to tune spatial values via the Director Agent workflow. May propose modifications to slot positions/sizes, which would be implemented as a revision to OBJ-019 (not as OBJ-060 output). |
| **OBJ-071** (SKILL.md geometry reference) | Documents the tunnel geometry: slot names, descriptions, compatible cameras, use cases. Imports `tunnelSlotGuidance` for per-slot image generation advice. |
| **OBJ-053** (Prompt template library) | Imports `tunnelSlotGuidance` for per-slot `promptGuidance` and `expectsAlpha` values. |
| **OBJ-017** (Manifest validation) | Validates that manifests using `geometry: "tunnel"` provide correct plane keys (`floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`) via OBJ-005's registry lookup. |
| **OBJ-029** (tunnel_push_forward camera path) | Must respect the constraint that camera Z ≤ `DEFAULT_CAMERA.position[2]` (Z=5) to avoid revealing corridor rear edges. |
| **OBJ-036** (Scene sequencer) | Looks up the tunnel geometry via `getGeometry('tunnel')` when rendering scenes that specify this geometry. |
| **OBJ-039** (Page-side renderer) | Creates Three.js meshes from the tunnel's slot definitions — positions planes, applies rotations, sets material properties based on `transparent` and `fogImmune` flags. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references tunnel's `compatible_cameras` against available camera path presets. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        tunnel.ts          # NEW: tunnelGeometry + tunnelSlotGuidance definitions
                           #      + registerGeometry() side effect
        index.ts           # MODIFIED: add `import './tunnel'` and re-export
                           #   tunnelGeometry, tunnelSlotGuidance
```

## Open Questions

### OQ-A: Subject slot deferred — tracked as potential OBJ-019 revision

See D15. A dedicated optional `subject` slot (upright, transparent, at approximately `[0, -1, -10]`) may be needed for common tunnel use cases where a character or object is placed in the corridor. This is explicitly deferred from the initial definition. If OBJ-060 tuning or user testing reveals the need, it should be added as a revision to OBJ-019 with its own acceptance criteria and test updates.

### OQ-B: Exact camera path travel range for `tunnel_push_forward`

The geometry's plane coverage supports forward camera travel from Z=5 to approximately Z=-20 without edge reveals (the corridor extends from Z=+5 to Z=-45). The exact travel range is defined by the `tunnel_push_forward` camera path preset (OBJ-029), which has not yet been implemented. The camera must not exceed Z=5 (D8 constraint) and should not approach closer than a safe margin from the end wall. Recommend camera travel stop at or before Z=-25 to maintain at least 20 units of distance from the end wall.

### OQ-C: Should left/right wall textures be horizontally flipped?

When the same image is used for both walls, the rotations naturally display the texture mirrored. This may look correct (symmetrical tunnel) or wrong (asymmetric details appear reversed). This is a SKILL.md guidance issue (OBJ-071), not a geometry issue. `tunnelSlotGuidance` advises avoiding text or asymmetric details in wall textures when using the same image for both walls.

---

I believe this revision addresses all six issues raised. Specifically:

1. **Issue 1 (PlaneSlot vs DepthSlot):** New D14 explicitly resolves the type ambiguity — OBJ-005's `PlaneSlot` is authoritative for registration, OBJ-007's additional fields are provided via `tunnelSlotGuidance`.
2. **Issue 2 (Missing prompt guidance):** `tunnelSlotGuidance` companion export added with per-slot `promptGuidance` and `expectsAlpha`. AC-29 through AC-31 verify it. Tests 46-48 cover it.
3. **Issue 3 (AC-15 computation):** Revised with explicit formula: `position[2] ± size[depthAxis]/2` where `depthAxis` is index 1 for floor/ceiling and index 0 for walls.
4. **Issue 4 (Zero rear-edge margin):** Explicit constraint added in D8 — camera paths must not exceed Z=5. Added to "Spatial Boundary Conditions" table as a violation case. OBJ-029 added to "Consumed by" with the constraint noted.
5. **Issue 5 (Subject slot):** Resolved via D15 — explicitly deferred from initial definition with a concrete follow-up mechanism (OBJ-019 revision, not OBJ-060 scope). OQ-A updated accordingly.
6. **Issue 6 (Test ordering):** Tests 40-42 now explicitly specify order-independent comparison (set equality, sort before asserting).

I'd like the challenger to verify these changes and approve if satisfied.

---

## Round 4 — spec_challenger

I've verified all six revisions against my Round 2 objections:

1. **Issue 1 (PlaneSlot vs DepthSlot):** D14 is present, clearly resolves the type ambiguity. ✓
2. **Issue 2 (Prompt guidance):** `tunnelSlotGuidance` companion export added with all 5 slots, AC-29–31 verify it, tests 46–48 cover it. ✓
3. **Issue 3 (AC-15 computation):** Explicit formula with `depthAxis` index specification. ✓
4. **Issue 4 (Rear-edge margin):** D8 now contains the binding constraint, spatial boundary table has the violation case, OBJ-029 appears in consumed-by with the constraint noted. ✓
5. **Issue 5 (Subject slot):** D15 cleanly separates geometry definition from tuning scope. ✓
6. **Issue 6 (Test ordering):** Tests 40–42 explicitly state order-independent/set-equality comparison. ✓

No new issues introduced by the revisions. The spec is implementable from its text alone plus the seed and dependency specs.

CONCLUSION:

The tunnel scene geometry spec (OBJ-019) defines the `'tunnel'` `SceneGeometry` with 5 slots (floor, ceiling, left_wall, right_wall, end_wall) forming a corridor receding along -Z. Key decisions: 8×6 cross-section, planes centered at Z=-20 with 50-unit depth, end wall at Z=-45, ceiling optional, black fog (near=15, far=50), `PlaneSlot` (OBJ-005) as authoritative type with `tunnelSlotGuidance` companion for prompt metadata, camera Z ≤ 5 constraint for compatible paths, subject slot explicitly deferred. 31 acceptance criteria, 48 unit tests, all testable without visual rendering.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Write,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me check the current state of the files I need to write to.
[Tool: Bash]
  Input: {
  "command": "ls -la nodes/OBJ-019/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-019 node directory exists"
}

[Tool: Bash]
  Input: {
  "command": "pwd",
  "description": "Check current working directory"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:17 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   728 Mar 22 19:17 meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-019",
     3→  "description": "Tunnel scene geometry -- floor (rotation [-PI/2,0,0]), ceiling (rotation [PI/2,0,0]), left wall (rotation [0,PI/2,0]), right wall (rotation [0,-PI/2,0]), and end wall at deep Z. Camera pushes forward on Z-axis; walls undergo real perspective distortion receding to vanishing point. Per Sections 4.2 and 8.4. Addresses TC-05 (tunnel produces convincing depth).",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 geometry. The signature 2.5D effect -- walls receding to vanishing point."
    12→}
    13→
Now let me write the final spec and update the meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "content": "# Specification: Tunnel Scene Geometry (OBJ-019)\n\n## Summary\n\nOBJ-019 defines the **tunnel scene geometry** -- the concrete `SceneGeometry` definition registered as `'tunnel'` in the geometry registry. The tunnel arranges five planes (floor, ceiling, left wall, right wall, end wall) into a box-like corridor receding along the negative Z-axis. When the camera pushes forward, walls undergo real perspective distortion -- converging to a vanishing point -- producing the signature 2.5D depth effect described in seed Section 4.2. This is the geometry that demonstrates depthkit's core differentiator: perspective projection that flat 2D parallax cannot replicate.\n\n## Interface Contract\n\n### Module Export\n\n```typescript\n// src/scenes/geometries/tunnel.ts\n\nimport type { SceneGeometry } from './types';\n\n/**\n * The tunnel scene geometry definition.\n *\n * Exported for direct reference in tests and documentation.\n * Also self-registers via registerGeometry() at module load time.\n */\nexport const tunnelGeometry: SceneGeometry;\n\n/**\n * Per-slot image generation guidance for the tunnel geometry.\n * Consumed by OBJ-051 (SKILL.md) and OBJ-053 (prompt template library)\n * to provide LLM authors with tunnel-specific image prompting advice.\n *\n * Keys match tunnelGeometry.slots keys exactly.\n */\nexport const tunnelSlotGuidance: Record<string, {\n  promptGuidance: string;\n  expectsAlpha: boolean;\n}>;\n```\n\n### Side Effect: Registration\n\nWhen `tunnel.ts` is imported, it calls `registerGeometry(tunnelGeometry)` as a module-level side effect, per the OBJ-005 registry pattern (D2). The barrel export `src/scenes/geometries/index.ts` must import `./tunnel` to trigger registration.\n\n### Geometry Definition\n\n```typescript\nconst tunnelGeometry: SceneGeometry = {\n  name: 'tunnel',\n\n  description:\n    'A corridor with floor, ceili
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/meta.json",
  "content": "{\n  \"id\": \"OBJ-019\",\n  \"description\": \"Tunnel scene geometry -- floor (rotation [-PI/2,0,0]), ceiling (rotation [PI/2,0,0]), left wall (rotation [0,PI/2,0]), right wall (rotation [0,-PI/2,0]), and end wall at deep Z. Camera pushes forward on Z-axis; walls undergo real perspective distortion receding to vanishing point. Per Sections 4.2 and 8.4. Addresses TC-05 (tunnel produces convincing depth).\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-005\", \"OBJ-007\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 geometry. The signature 2.5D effect -- walls receding to vanishing point. Spec complete: 5 slots (floor, ceiling, left_wall, right_wall, end_wall), 8x6 cross-section, fog black near=15 far=50, companion tunnelSlotGuidance export for prompt metadata. Ceiling optional. Camera Z <= 5 constraint for compatible paths.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/meta.json has been updated successfully.

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-019/output.md nodes/OBJ-019/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-019): tunnel scene geometry specification\n\nDefine the tunnel SceneGeometry with 5 slots (floor, ceiling, left_wall,\nright_wall, end_wall) forming an 8x6 corridor at Z=-20 with end wall at\nZ=-45. Ceiling optional. Black fog near=15/far=50. Companion\ntunnelSlotGuidance export for image generation metadata. 31 acceptance\ncriteria, 48 unit tests. Resolves PlaneSlot/DepthSlot type gap via D14.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-019 spec files"
}
[Tool Result] [master 85a7d42] spec(OBJ-019): tunnel scene geometry specification
 2 files changed, 484 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-019/output.md
The specification for OBJ-019 (Tunnel Scene Geometry) has been written to `nodes/OBJ-019/output.md`, `meta.json` updated, and committed. The spec defines a complete, implementable tunnel geometry with 31 acceptance criteria, 48 unit tests, and clear resolution of the PlaneSlot/DepthSlot type gap between OBJ-005 and OBJ-007.
