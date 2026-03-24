# Deliberation Transcript: OBJ-020

---

## Round 1 — spec_author

# Specification: Canyon Scene Geometry (OBJ-020)

## Summary

OBJ-020 defines the **canyon** scene geometry — a narrow, vertically dramatic 3D space with tall wall planes on left and right, a floor plane, an open sky above, and an optional end wall at depth. The camera pushes forward through the canyon or floats upward to reveal vertical scale. This geometry produces the feeling of traveling through a narrow gorge, alley, corridor between tall buildings, or any space defined by towering vertical boundaries. It registers itself via `registerGeometry()` from OBJ-005 and defines its `SlotSet` per OBJ-007's depth model contract.

## Interface Contract

### Geometry Definition

```typescript
// src/scenes/geometries/canyon.ts

import type { SceneGeometry, PlaneSlot, FogConfig } from './types';
import { registerGeometry } from './registry';
```

The module defines and registers a single `SceneGeometry` object with the following structure:

#### Geometry Name
```
name: 'canyon'
```

#### Slots

The canyon geometry defines **6 slots**. The spatial concept: two tall, deep wall planes forming a narrow corridor, a floor extending into depth, an open sky visible above, and an optional end wall providing a visual terminus. An optional `subject` slot places a focal element within the canyon.

| Slot | Position | Rotation | Size | Required | transparent | fogImmune | renderOrder | Description |
|------|----------|----------|------|----------|-------------|-----------|-------------|-------------|
| `sky` | `[0, 12, -20]` | `[Math.PI/2, 0, 0]` | `[12, 50]` | `true` | `false` | `true` | 0 | Open sky visible above the canyon walls. Horizontal plane facing downward, positioned high above the canyon floor. fogImmune because sky should remain vivid regardless of depth fog. |
| `left_wall` | `[-4, 3, -20]` | `[0, Math.PI/2, 0]` | `[50, 18]` | `true` | `false` | `false` | 1 | Left canyon wall. Tall vertical plane facing right. Width (50) extends deep along Z to prevent edge reveal during forward camera push. Height (18) provides vertical drama. |
| `right_wall` | `[4, 3, -20]` | `[0, -Math.PI/2, 0]` | `[50, 18]` | `true` | `false` | `false` | 1 | Right canyon wall. Tall vertical plane facing left. Mirrors left_wall placement. |
| `floor` | `[0, -3, -20]` | `[-Math.PI/2, 0, 0]` | `[8, 50]` | `true` | `false` | `false` | 2 | Canyon floor extending into depth. Horizontal plane facing upward. Width (8) matches the gap between walls. Depth (50) prevents edge reveal. |
| `end_wall` | `[0, 3, -45]` | `[0, 0, 0]` | `[8, 18]` | `false` | `false` | `false` | 3 | Distant terminus of the canyon. Optional — without it, the canyon appears to continue infinitely (fog handles the fade). Sized to match the gap between walls (8) and wall height (18). |
| `subject` | `[0, -1, -10]` | `[0, 0, 0]` | `[6, 6]` | `false` | `true` | `false` | 4 | Optional focal element within the canyon (person, creature, landmark). Positioned slightly below center (canyon floors are low), at mid-depth. Transparent to blend with the environment. |

#### Spatial Rationale

**Wall placement:** Walls are at X = ±4, creating an 8-unit-wide canyon. This is narrow relative to the camera FOV of 50°, which at the camera's starting Z=5 makes the walls clearly visible in peripheral vision, enhancing the "enclosed corridor" feeling. The walls are centered at Y=3 (shifted upward from the floor at Y=-3) with height 18, so they span from Y=-6 to Y=12, towering above and slightly below the camera's default Y position.

**Wall depth (Z-axis extent):** Each wall's width (the dimension along Z after rotation) is 50 units, centered at Z=-20, so they span from Z=5 to Z=-45. This ensures the camera never sees the near edge of the walls even at the starting position (Z=5), and the far edge extends well beyond the end wall.

**Floor:** 8 units wide (matching wall gap), 50 units deep (matching wall extent). At Y=-3, giving 8 units of space between floor and camera at default Y=0.

**Sky:** Positioned at Y=12, just above the wall tops (walls reach Y=12). The sky is a horizontal plane facing downward (`rotation=[Math.PI/2, 0, 0]`), 12 units wide (slightly wider than the wall gap to prevent edge-peeking) and 50 units deep. Being fogImmune means the distant portions of sky remain visible even when fog obscures the far floor and walls, which is the natural atmospheric behavior (sky doesn't fog out in a canyon).

**End wall:** At Z=-45 (the far extent of walls/floor), sized to fill the gap between walls. Optional because some canyon scenes work better with implied infinite depth via fog.

**Subject:** At Z=-10, about 15 units ahead of the camera start. Slightly below center (Y=-1) to sit naturally on/near the canyon floor. Small (6×6) relative to the canyon to emphasize the scale of the environment.

**Camera start position assumption:** The default camera starts at approximately `[0, 0, 5]` per OBJ-003's `DEFAULT_CAMERA.position`. The canyon is designed around this, with the near edges of walls/floor at Z=5 (the camera start) and extending to Z=-45.

#### Compatible Cameras

```typescript
compatible_cameras: [
  'slow_push_forward',
  'crane_up',
  'dramatic_push',
  'gentle_float',
  'static',
] as const
```

**Rationale for each:**
- `slow_push_forward`: The primary canyon motion — camera glides forward through the space. Walls recede to vanishing point, floor skews into perspective. The defining 2.5D effect for this geometry.
- `crane_up`: Camera rises on Y-axis, revealing the vertical scale of the canyon walls and eventually the sky opening above. Dramatic reveal.
- `dramatic_push`: Faster forward push with ease-out. For emphasis or tension (e.g., approaching something at the end of the canyon).
- `gentle_float`: Subtle multi-axis drift. Good for ambient/atmospheric canyon scenes where the space itself is the subject.
- `static`: No movement. For scenes where the canyon framing is enough and a transition handles temporal interest.

**Excluded:** `lateral_track_left`/`lateral_track_right` — lateral movement in a narrow canyon risks revealing wall edges or breaking the enclosed-corridor illusion. `flyover_glide` — the camera is inside the canyon, not above it. `tunnel_push_forward` — similar motion to `slow_push_forward` but tuned for enclosed spaces with ceilings; canyon has open sky. `dolly_zoom` — FOV animation in a narrow space could cause walls to clip or distort unnaturally.

#### Default Camera

```typescript
default_camera: 'slow_push_forward'
```

The forward push is the most natural and dramatic motion for a canyon — it showcases the vanishing-point perspective on both walls and the floor simultaneously.

#### Fog

```typescript
fog: {
  color: '#1a1a2e',
  near: 15,
  far: 45,
}
```

**Rationale:** Dark blue-gray fog (`#1a1a2e`) suggests atmospheric haze and depth without being pure black (which would feel like a tunnel). Fog starts at distance 15 from camera (so the near portions of the canyon are crisp) and reaches full density at distance 45 (matching the end wall Z-position). This naturally obscures the far edges of walls/floor, preventing hard-edge visibility, and adds atmospheric perspective that enhances the depth illusion. If `end_wall` is omitted, fog provides a natural visual terminus.

#### Description

```
"Tall walls on left and right with a floor and open sky above. Camera pushes forward through a narrow dramatic space — a gorge, alley, or corridor between towering structures. Walls recede to a vanishing point with real perspective distortion. Good for dramatic, oppressive, or awe-inspiring environments."
```

#### Preferred Aspect

```typescript
preferred_aspect: 'landscape'
```

Canyon works in both orientations, but landscape (16:9) best showcases the horizontal depth and vanishing-point convergence of the walls. In portrait mode (9:16), the vertical extent of the walls becomes the dominant feature, which is also valid but less showcases the forward-depth effect. Marking as `landscape` for SKILL.md guidance.

### DepthSlot Definitions (OBJ-007 Contract)

Each slot in the canyon geometry is a `DepthSlot` per OBJ-007:

```typescript
// Slot-level DepthSlot details beyond what's in the table above

sky: {
  name: 'sky',
  promptGuidance: 'Wide sky or atmosphere, looking upward. Narrow strip of sky visible between canyon walls. Dramatic clouds, stars, or atmospheric gradient.',
  expectsAlpha: false,
}

left_wall: {
  name: 'left_wall',
  promptGuidance: 'Tall vertical surface texture — rock face, building facade, cliff wall, ice wall. Seamless/tileable preferred. Dramatic lighting from above.',
  expectsAlpha: false,
}

right_wall: {
  name: 'right_wall',
  promptGuidance: 'Tall vertical surface texture — matching or complementing left_wall. Can be identical or different for asymmetric canyons.',
  expectsAlpha: false,
}

floor: {
  name: 'floor',
  promptGuidance: 'Ground surface extending into distance — rocky path, sand, cobblestones, water, lava. Top-down or strongly receding perspective.',
  expectsAlpha: false,
}

end_wall: {
  name: 'end_wall',
  promptGuidance: 'Distant vista or terminus — light at end of canyon, distant landscape, doorway, or solid wall. Atmospheric, slightly hazy.',
  expectsAlpha: false,
}

subject: {
  name: 'subject',
  promptGuidance: 'Focal element within the canyon — person, creature, vehicle, landmark. Isolated on transparent background. Scale should feel small relative to canyon walls.',
  expectsAlpha: true,
}
```

### Module Exports

The module has no public exports beyond the side effect of calling `registerGeometry()` at import time. Consumers access the canyon geometry via `getGeometry('canyon')` from the OBJ-005 registry.

```typescript
// src/scenes/geometries/canyon.ts
// No named exports — registration is the side effect

import { registerGeometry } from './registry';
// ... define canyonGeometry ...
registerGeometry(canyonGeometry);
```

The geometry module must be imported (for its registration side effect) by the geometry barrel export `src/scenes/geometries/index.ts`.

## Design Decisions

### D1: 6 slots — structural + subject

The canyon has 4 structural slots (left_wall, right_wall, floor, sky) plus 2 content slots (end_wall, subject). This differs from the tunnel geometry (which has 5 structural slots: floor, ceiling, left_wall, right_wall, end_wall) by replacing `ceiling` with `sky` — the open sky is the canyon's defining spatial distinction from a tunnel.

The optional `subject` slot is included because canyons are often used to frame a focal element (explorer in a gorge, vehicle in an alley). Without it, the geometry is purely environmental — valid, but limiting. Making it optional means the LLM can choose.

**Seed alignment:** TC-01 asks whether 3-5 planes per scene are sufficient for 90% of cases. Canyon uses up to 6 but requires only 4, staying within the spirit of the constraint.

### D2: Walls centered at Y=3, not Y=0

The walls are vertically centered at Y=3 (spanning Y=-6 to Y=12), not at Y=0 (which would be Y=-9 to Y=9). This shifts the "towering above" emphasis upward — from camera height at Y=0, there's 12 units of wall above and 6 below. This matches human perception of canyons: we see far more wall above us than below. The floor at Y=-3 reinforces this asymmetry.

### D3: Sky is a horizontal plane, not a vertical backdrop

The sky uses `rotation=[Math.PI/2, 0, 0]` (horizontal, facing down) rather than the default camera-facing orientation. This is because the sky in a canyon is visible by looking up between the walls — it's overhead, not in front. As the camera moves forward, the sky plane doesn't exhibit parallax in the same way walls do; it simply scrolls overhead, which matches real canyon physics.

The sky is marked `fogImmune: true` because atmospheric fog doesn't obscure the sky in real canyons — it obscures distant ground-level objects. Without fog immunity, the far end of the sky plane would fade to the fog color, creating an unnatural dark band overhead.

### D4: Dark blue-gray fog rather than black

Pure black fog (`#000000`) reads as "underground" or "void." The dark blue-gray (`#1a1a2e`) suggests atmospheric haze, twilight, or natural distance. This is tunable — the manifest can override fog per-scene (OBJ-005's `FogConfig` override). The default is optimized for the most common canyon use case: a dramatic but naturalistic outdoor space.

### D5: No ceiling slot

The canyon's distinction from a tunnel is the open sky. Including a `ceiling` slot would make it a tunnel variant. If a content author needs an enclosed overhead space, they should use the tunnel geometry instead. This keeps the geometry vocabulary clear and non-overlapping (seed AP-06: don't invent synonyms).

### D6: Wall renderOrder equality

Both `left_wall` and `right_wall` share `renderOrder: 1` because they never overlap from any valid camera position (they're on opposite sides of X-space). If they were to overlap from an extreme camera angle, Three.js's depth buffer handles it correctly since they are opaque. Equal renderOrder avoids introducing an arbitrary left-before-right draw order.

### D7: Subject position at Y=-1

The subject is at Y=-1, slightly above the floor (Y=-3) rather than at Y=0 (camera height). This positions the subject's visual center near the lower third of the frame from the default camera, following the rule of thirds and suggesting the subject is standing on the canyon floor. The camera at Y=0 looks slightly down at the subject, which enhances the sense of vertical scale.

### D8: Compatible camera selection is conservative

Only 5 camera paths are marked compatible. This is intentionally conservative — lateral tracks and flyover paths risk breaking the spatial illusion in the narrow canyon. New camera paths designed for canyons (e.g., `canyon_crane_reveal` — starting low and rising to reveal the sky opening) can be added to `compatible_cameras` when they are defined and tuned. The geometry definition can be updated without changing its contract, since `compatible_cameras` is additive.

## Acceptance Criteria

- [ ] **AC-01:** A `SceneGeometry` object with `name: 'canyon'` is registered via `registerGeometry()` and retrievable via `getGeometry('canyon')`.
- [ ] **AC-02:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-03:** The geometry defines exactly 6 slots: `sky`, `left_wall`, `right_wall`, `floor`, `end_wall`, `subject`.
- [ ] **AC-04:** Required slots are: `sky`, `left_wall`, `right_wall`, `floor`. Optional slots are: `end_wall`, `subject`.
- [ ] **AC-05:** `left_wall` rotation is `[0, Math.PI/2, 0]` (facing right); `right_wall` rotation is `[0, -Math.PI/2, 0]` (facing left); `floor` rotation is `[-Math.PI/2, 0, 0]` (facing up); `sky` rotation is `[Math.PI/2, 0, 0]` (facing down); `end_wall` and `subject` rotation is `[0, 0, 0]` (facing camera).
- [ ] **AC-06:** Wall planes (`left_wall`, `right_wall`) have Z-extent (via size width after rotation) sufficient to span from the default camera start position (Z=5 per OBJ-003) to at least Z=-45, preventing edge reveal during forward camera push.
- [ ] **AC-07:** Floor plane has Z-extent (via size height after rotation) matching the wall Z-extent.
- [ ] **AC-08:** `sky` slot has `fogImmune: true`. All other slots have `fogImmune: false` (or omitted, defaulting to false).
- [ ] **AC-09:** `subject` slot has `transparent: true`. All structural slots have `transparent: false` (or omitted).
- [ ] **AC-10:** `compatible_cameras` contains at least: `'slow_push_forward'`, `'crane_up'`, `'gentle_float'`, `'static'`.
- [ ] **AC-11:** `default_camera` is `'slow_push_forward'` and is present in `compatible_cameras`.
- [ ] **AC-12:** `fog` is defined with `near >= 0`, `far > near`, and `color` matching `#RRGGBB` format.
- [ ] **AC-13:** `description` is non-empty and describes the canyon spatial concept.
- [ ] **AC-14:** `preferred_aspect` is `'landscape'`.
- [ ] **AC-15:** All slot `description` fields are non-empty strings.
- [ ] **AC-16:** All slot `name` fields match their key in the `slots` record.
- [ ] **AC-17:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-18:** `renderOrder` values ensure correct draw ordering: sky (0) < walls (1) < floor (2) < end_wall (3) < subject (4).
- [ ] **AC-19:** The canyon's wall gap (distance between left_wall X and right_wall X) matches the floor width and end_wall width, producing a spatially consistent corridor.
- [ ] **AC-20:** The geometry module registers itself as a side effect of import, with no named exports.
- [ ] **AC-21:** Each slot's `promptGuidance` is a non-empty string providing actionable image generation guidance.
- [ ] **AC-22:** Each slot's `expectsAlpha` is set: `true` for `subject`, `false` for all others.
- [ ] **AC-23:** The sky plane width is at least as wide as the wall gap to prevent sky-edge visibility when the camera is at default position looking upward.

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|---|---|
| All 4 required slots provided, both optional omitted | Valid. Canyon renders as environment-only: walls, floor, sky. Fog hides the far end naturally. |
| Only `subject` optional provided (no `end_wall`) | Valid. Subject appears in the canyon, fog provides depth terminus. |
| Only `end_wall` optional provided (no `subject`) | Valid. Canyon with a visible destination. |
| All 6 slots provided | Valid. Full canyon with environment, terminus, and focal element. |
| Camera at start position Z=5 | Near edges of walls/floor at Z=5 should not be visible. Walls span from Z=5 to Z=-45 (centered at Z=-20 with width 50 post-rotation). At camera Z=5, the near wall edge is at Z=5 — exactly at camera. This is a boundary condition; the wall extends to the camera plane, so no gap is visible. |
| Camera pushes forward to Z=-20 | Mid-canyon. Walls still extend 25 units behind and ahead of camera. Floor/sky likewise. No edge reveals. |
| Camera rises (crane_up) to Y=10 | Approaching wall tops at Y=12. Sky plane at Y=12 becomes more visible. Walls still have 2 units above camera. Subject below is foreshortened. |
| Portrait mode (9:16) | Walls will be more prominent in frame due to narrower horizontal FOV. The 8-unit wall gap at default camera distance is still sufficient. Vertical extent of walls (18 units) is a strength in portrait. The geometry works but is not optimized for portrait — `preferred_aspect: 'landscape'` is advisory. |

### Override Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Override moves left_wall to X=0 | Valid per `validatePlaneSlots` (finite coordinates), but walls overlap. This is an authoring error, not a validation error — the engine renders it as-is. SKILL.md should warn against moving structural walls. |
| Override sets subject size to `[20, 20]` | Valid. Subject becomes larger than the canyon gap, breaking immersion. Not a validation concern. |
| Override sets floor Y to Y=0 | Valid. Floor rises to camera height. Produces an unusual but renderable scene. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Canyon module imported after registry is locked | `registerGeometry` throws. The barrel export must import canyon before any read operations occur. |
| Canyon module imported twice | Second `registerGeometry('canyon')` throws duplicate name error per OBJ-005. Standard module caching prevents this in practice. |

## Test Strategy

### Unit Tests

**Registration and retrieval:**
1. After importing the canyon module, `getGeometry('canyon')` returns a defined `SceneGeometry`.
2. `getGeometry('canyon')?.name` equals `'canyon'`.
3. The returned geometry passes `validateGeometryDefinition()` with zero errors.

**Slot structure:**
4. `getAllSlotNames(canyonGeometry)` returns exactly `['end_wall', 'floor', 'left_wall', 'right_wall', 'sky', 'subject']` (alphabetical).
5. `getRequiredSlotNames(canyonGeometry)` returns exactly `['floor', 'left_wall', 'right_wall', 'sky']` (alphabetical).
6. `getOptionalSlotNames(canyonGeometry)` returns exactly `['end_wall', 'subject']` (alphabetical).

**Slot spatial correctness:**
7. `left_wall` position X is negative; `right_wall` position X is positive; they are symmetric about X=0.
8. `left_wall` and `right_wall` have equal absolute X positions (symmetric canyon).
9. `floor` rotation is `[-Math.PI/2, 0, 0]`; `sky` rotation is `[Math.PI/2, 0, 0]`.
10. `left_wall` rotation is `[0, Math.PI/2, 0]`; `right_wall` rotation is `[0, -Math.PI/2, 0]`.
11. `end_wall` and `subject` rotation is `[0, 0, 0]`.
12. `end_wall` Z-position is more negative than `subject` Z-position (further away).
13. `floor` Y-position is negative (below camera default Y=0).
14. `sky` Y-position is higher than wall center Y + wall height/2 (sky above wall tops) — or at minimum equal.

**Slot metadata:**
15. `sky.fogImmune` is `true`.
16. `subject.transparent` is `true`.
17. All slots have non-empty `description`.
18. All slot `name` fields match their record key.
19. `renderOrder` values: sky=0, left_wall=1, right_wall=1, floor=2, end_wall=3, subject=4.

**Camera compatibility:**
20. `isCameraCompatible(canyonGeometry, 'slow_push_forward')` returns `true`.
21. `isCameraCompatible(canyonGeometry, 'crane_up')` returns `true`.
22. `isCameraCompatible(canyonGeometry, 'static')` returns `true`.
23. `isCameraCompatible(canyonGeometry, 'tunnel_push_forward')` returns `false`.
24. `isCameraCompatible(canyonGeometry, 'lateral_track_left')` returns `false`.
25. `default_camera` is in `compatible_cameras`.

**Fog configuration:**
26. `fog` is defined, `fog.near >= 0`, `fog.far > fog.near`.
27. `fog.color` matches `/^#[0-9a-fA-F]{6}$/`.

**Spatial consistency:**
28. Wall gap (right_wall X - left_wall X, accounting for symmetry about center) approximately equals floor width.
29. End wall width approximately equals floor width (fills the gap between walls).
30. Wall Z-extent (size[0], which maps to Z after rotation) spans from at least Z=5 to at most Z=-45.

**Immutability:**
31. Attempting to mutate `getGeometry('canyon')?.slots.floor.position[0]` throws `TypeError` (deep freeze from OBJ-005 registry).

### Relevant Testable Claims

- **TC-01 (partial):** Canyon uses 4-6 planes, within the 3-5 sweet spot (4 required, 6 max), validating sufficiency for dramatic corridor scenes.
- **TC-04 (partial):** An LLM can author a canyon manifest using only slot names and geometry name — no XYZ coordinates needed.
- **TC-05 (analogous):** Though TC-05 is specifically about tunnels, the same "traveling through a space" claim applies to canyons — walls should visibly recede to a vanishing point with a forward camera push.
- **TC-08 (partial):** Canyon is one of the 8 proposed geometries. Its inclusion expands the design space coverage.

## Integration Points

### Depends on

| Upstream | What OBJ-020 imports |
|---|---|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types. `registerGeometry()` function. `getAllSlotNames`, `getRequiredSlotNames`, `getOptionalSlotNames`, `isCameraCompatible` for testing. |
| **OBJ-007** (Depth model) | `DepthSlot`, `SlotSet` types. `SLOT_NAME_PATTERN` for slot name compliance. `isValidSlotName` for validation. OBJ-007's `promptGuidance` and `expectsAlpha` field contracts inform the per-slot metadata. |

### Consumed by

| Downstream | How it uses OBJ-020 |
|---|---|
| **OBJ-061** (Canyon visual tuning) | Renders test videos with the canyon geometry and compatible camera paths. The Director Agent reviews and the HITL loop tunes spatial values (wall gap, wall height, fog settings, subject position). |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('canyon')` when a manifest scene specifies `geometry: 'canyon'`. Routes to the canyon slot definitions for mesh instantiation. |
| **OBJ-039** (Page-side geometry instantiation) | Creates Three.js meshes from canyon slot definitions — reads position, rotation, size, renderOrder, transparent, fogImmune for each slot. |
| **OBJ-040** (Plane sizing / edge-reveal validation) | Validates that canyon planes are oversized enough for compatible camera paths. May flag edge reveals and recommend size adjustments. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references canyon's `compatible_cameras` against defined camera path presets. |
| **OBJ-071** (SKILL.md) | Documents the canyon geometry: when to use it, what images to generate per slot, which cameras work with it. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        canyon.ts         # Canyon geometry definition + registerGeometry() call
        index.ts          # Updated barrel export to import './canyon' for side effect
```

## Open Questions

### OQ-A: Should wall textures be mirrored or independent?

The left and right wall accept independent textures, allowing asymmetric canyons (e.g., rock face on left, ice wall on right). However, many real canyons have visually similar walls. Should the geometry support a convenience mode where a single wall texture is automatically applied to both walls (mirrored)?

**Recommendation:** No. Keep slots independent. If the LLM wants matching walls, it assigns the same image to both slots. A `mirror_walls` flag adds manifest schema complexity for a trivial convenience. Defer to SKILL.md guidance: "For symmetric canyons, use the same image for left_wall and right_wall."

### OQ-B: Should the canyon support variable wall height?

The wall height is fixed at 18 world units in the geometry default. Some canyon scenes might want shorter walls (a shallow gully) or taller walls (a deep chasm). This is already handleable via `PlaneOverride` on the wall size, but is the default 18-unit height appropriate for most cases?

**Recommendation:** 18 units is a good starting point — it provides dramatic vertical scale relative to the 8-unit gap. Tuning during OBJ-061 (visual tuning) will validate or adjust this. The override escape hatch covers edge cases.

### OQ-C: Exact spatial values subject to visual tuning

All position, rotation, and size values in this spec are mathematically reasoned starting points. OBJ-061 (canyon visual tuning) will validate these through the Director Agent workflow and may adjust them. The acceptance criteria test structural relationships (symmetry, extent, consistency) rather than exact numeric values, so tuning adjustments won't break tests as long as spatial invariants hold.

---

I believe this specification covers all the required elements: the full spatial definition, slot metadata per both OBJ-005 and OBJ-007 contracts, camera compatibility, fog configuration, design rationale, comprehensive acceptance criteria, edge cases, and integration points. I'd like the Challenger to review and flag any gaps or issues.

---

## Round 2 — spec_challenger

I've reviewed the OBJ-020 canyon geometry spec carefully against the seed, OBJ-005, and OBJ-007. The spec is well-structured overall — the spatial rationale is thorough, the acceptance criteria cover structural invariants, and the design decisions are clearly reasoned. Here are my findings:

---

## Points of Agreement (Sound)

- **Slot selection and required/optional split** — 4 required structural slots + 2 optional content slots is well-reasoned. The distinction from tunnel (open sky vs ceiling) is clean and follows AP-06.
- **Wall symmetry, sky fogImmune, subject transparent** — correct per both dependency specs and spatial logic.
- **Conservative camera compatibility** — excluding lateral tracks and flyover from a narrow corridor is correct. Additive expansion is the right future strategy.
- **Fog rationale** — dark blue-gray vs black is a good default. The fog range matching end_wall Z is well-considered.
- **Design decisions D1-D8** — all solid, well-justified, and consistent with dependency specs.

---

## Issues

### Issue 1: Type relationship between `PlaneSlot` (OBJ-005) and `DepthSlot` (OBJ-007) is unresolved — **Major**

The spec imports `PlaneSlot` from OBJ-005 for `registerGeometry()`, and separately shows `DepthSlot` fields (`promptGuidance`, `expectsAlpha`, `name`) in a different section. These are **two different interfaces** with overlapping but non-identical fields:

- `PlaneSlot` has `transparent?`, `fogImmune?` — `DepthSlot` does not.
- `DepthSlot` has `name`, `promptGuidance`, `expectsAlpha` — `PlaneSlot` does not.

An implementer cannot determine: Does the single slot object have all fields from both interfaces? Is the DepthSlot data a separate structure? Does `registerGeometry()` accept extra properties beyond `PlaneSlot`?

**Proposed fix:** Add a design decision (or clarify in the Interface Contract section) that states: "Each slot object is constructed with the union of `PlaneSlot` fields (for `registerGeometry()`) and `DepthSlot` metadata fields (`name`, `promptGuidance`, `expectsAlpha`). TypeScript structural typing allows the object to satisfy both interfaces. The registered `SceneGeometry.slots` record satisfies `Record<string, PlaneSlot>` for the registry, while downstream consumers (OBJ-051 SKILL.md, OBJ-053 prompt templates) access the additional `DepthSlot` fields by casting or by importing the geometry definition directly before registration." Alternatively, if OBJ-018 (already verified) established a pattern, reference that pattern explicitly.

### Issue 2: Wall near-edge at exactly Z=5 creates zero safety margin — **Major**

Walls span Z=5 to Z=-45. Camera starts at Z=5. This means:

- At frame 0, the wall's near edge is **exactly at the camera position**. With the near clipping plane at 0.1, only wall portions at Z ≤ 4.9 are rendered. The wall starts visually at the camera — fine.
- But `gentle_float` is described in seed Section 4.3 as "very slow, subtle movement in **all three axes**." If the camera drifts to Z=5.5 or Z=6, the wall edge at Z=5 becomes a visible hard edge 0.5–1 unit in front of the camera.

The spec lists `gentle_float` as compatible but provides zero margin for backward Z drift.

**Proposed fix:** Either (a) extend wall/floor/sky Z-extent near-edge to Z=7 or Z=8 (providing a 2–3 unit safety margin at negligible cost — just increase size[0] from 50 to 54/56), or (b) add an acceptance criterion that wall Z-extent must exceed the camera start Z by at least 2 world units, and note in the spatial rationale that this margin accommodates `gentle_float` drift.

### Issue 3: Test #14 says "higher than" but sky Y equals wall top Y — **Minor**

Test #14: "`sky` Y-position is higher than wall center Y + wall height/2." Wall center Y=3, height/2=9, so wall top=12. Sky Y=12. The test as written **fails** (12 is not *higher than* 12). The spec parenthetically says "(or at minimum equal)" but the test text contradicts this.

**Proposed fix:** Change test #14 to: "`sky` Y-position is **greater than or equal to** wall center Y + wall height/2 (sky at or above wall tops)."

### Issue 4: DepthSlot section shows partial objects without context — **Minor**

The "DepthSlot Definitions (OBJ-007 Contract)" section shows objects with only `name`, `promptGuidance`, and `expectsAlpha`. These are not complete `DepthSlot` objects (missing position, rotation, size, required, description, renderOrder). An implementer may wonder if these are separate objects or supplementary metadata for the slot table above.

**Proposed fix:** Add a sentence before the DepthSlot section: "The following shows the OBJ-007–specific metadata fields for each slot. These are combined with the spatial and PlaneSlot fields from the table above to form the complete slot definitions." This makes it explicit that the two sections are complementary views of the same objects.

### Issue 5: AC-19 says "approximately equals" — **Minor**

"The canyon's wall gap … **approximately** equals floor width and end_wall width." This is untestable as written — what tolerance? In the spec, wall gap is exactly 8 (|4 - (-4)|), floor width is exactly 8, end_wall width is exactly 8. They're exactly equal by design.

**Proposed fix:** Change to: "The canyon's wall gap (distance between `left_wall` X-position and `right_wall` X-position) **equals** the `floor` slot's size width and the `end_wall` slot's size width."

Similarly, test #28–29 say "approximately equals." Change to "equals" since these are exact by design. If OBJ-061 tuning might change them, the criterion should specify the invariant precisely: "floor width equals end_wall width equals wall gap" — this is a structural invariant that should survive tuning.

---

## Summary

- **2 major issues:** Type ambiguity (PlaneSlot vs DepthSlot composition) and zero-margin wall edge at camera start.
- **3 minor issues:** Test #14 off-by-one wording, DepthSlot section context, AC-19/test imprecision.

All are fixable without restructuring. Please revise and I'll verify.

---

## Round 3 — spec_author

Thank you for the thorough review. All five issues are valid. Here's my revised specification with each addressed:

---

# Specification: Canyon Scene Geometry (OBJ-020)

## Summary

OBJ-020 defines the **canyon** scene geometry — a narrow, vertically dramatic 3D space with tall wall planes on left and right, a floor plane, an open sky above, and an optional end wall at depth. The camera pushes forward through the canyon or floats upward to reveal vertical scale. This geometry produces the feeling of traveling through a narrow gorge, alley, corridor between tall buildings, or any space defined by towering vertical boundaries. It registers itself via `registerGeometry()` from OBJ-005 and defines its slot set per OBJ-007's depth model contract.

## Interface Contract

### Geometry Definition

```typescript
// src/scenes/geometries/canyon.ts

import type { SceneGeometry, PlaneSlot, FogConfig } from './types';
import { registerGeometry } from './registry';
```

The module defines and registers a single `SceneGeometry` object with the following structure:

#### Geometry Name
```
name: 'canyon'
```

#### Slots

The canyon geometry defines **6 slots**. The spatial concept: two tall, deep wall planes forming a narrow corridor, a floor extending into depth, an open sky visible above, and an optional end wall providing a visual terminus. An optional `subject` slot places a focal element within the canyon.

Each slot object is constructed with all fields required by both the `PlaneSlot` interface (from OBJ-005, for `registerGeometry()`) and the `DepthSlot` metadata fields from OBJ-007 (`name`, `promptGuidance`, `expectsAlpha`). TypeScript's structural typing allows a single object literal to satisfy both interfaces. The `SceneGeometry.slots` record is typed as `Record<string, PlaneSlot>` for the registry; downstream consumers that need OBJ-007 metadata (OBJ-051 SKILL.md, OBJ-053 prompt templates) access the additional fields by importing the canyon geometry definition directly or by casting, following the same pattern established by OBJ-018 (stage geometry).

| Slot | Position | Rotation | Size | Required | transparent | fogImmune | renderOrder | Description |
|------|----------|----------|------|----------|-------------|-----------|-------------|-------------|
| `sky` | `[0, 12, -20]` | `[Math.PI/2, 0, 0]` | `[12, 56]` | `true` | `false` | `true` | 0 | Open sky visible above the canyon walls. Horizontal plane facing downward, positioned high above the canyon floor. fogImmune because sky should remain vivid regardless of depth fog. |
| `left_wall` | `[-4, 3, -20]` | `[0, Math.PI/2, 0]` | `[56, 18]` | `true` | `false` | `false` | 1 | Left canyon wall. Tall vertical plane facing right. Width (56) extends deep along Z to prevent edge reveal during forward camera push including gentle_float backward drift margin. Height (18) provides vertical drama. |
| `right_wall` | `[4, 3, -20]` | `[0, -Math.PI/2, 0]` | `[56, 18]` | `true` | `false` | `false` | 1 | Right canyon wall. Tall vertical plane facing left. Mirrors left_wall placement. |
| `floor` | `[0, -3, -20]` | `[-Math.PI/2, 0, 0]` | `[8, 56]` | `true` | `false` | `false` | 2 | Canyon floor extending into depth. Horizontal plane facing upward. Width (8) matches the gap between walls. Depth (56) prevents edge reveal. |
| `end_wall` | `[0, 3, -48]` | `[0, 0, 0]` | `[8, 18]` | `false` | `false` | `false` | 3 | Distant terminus of the canyon. Optional — without it, the canyon appears to continue infinitely (fog handles the fade). Sized to match the gap between walls (8) and wall height (18). |
| `subject` | `[0, -1, -10]` | `[0, 0, 0]` | `[6, 6]` | `false` | `true` | `false` | 4 | Optional focal element within the canyon (person, creature, landmark). Positioned slightly below center (canyon floors are low), at mid-depth. Transparent to blend with the environment. |

#### Spatial Rationale

**Wall placement:** Walls are at X = ±4, creating an 8-unit-wide canyon. This is narrow relative to the camera FOV of 50°, which at the camera's starting Z=5 makes the walls clearly visible in peripheral vision, enhancing the "enclosed corridor" feeling. The walls are centered at Y=3 (shifted upward from the floor at Y=-3) with height 18, so they span from Y=-6 to Y=12, towering above and slightly below the camera's default Y position.

**Wall depth (Z-axis extent) and safety margin:** Each wall's width (the dimension along Z after rotation) is 56 units, centered at Z=-20, so they span from Z=8 to Z=-48. The near edge at Z=8 provides a **3-unit safety margin** beyond the camera start at Z=5. This margin accommodates `gentle_float`'s subtle multi-axis drift (which may move the camera slightly backward on Z) without revealing wall edges. The far edge at Z=-48 extends well beyond the end wall at Z=-48 (end wall repositioned to Z=-48 to sit at the far boundary). Floor and sky use the same 56-unit depth for consistency.

**Floor:** 8 units wide (matching wall gap), 56 units deep (matching wall extent). At Y=-3, giving 3 units of space between floor and camera at default Y=0.

**Sky:** Positioned at Y=12, at the wall tops (walls reach Y=12). The sky is a horizontal plane facing downward (`rotation=[Math.PI/2, 0, 0]`), 12 units wide (50% wider than the wall gap to prevent edge-peeking from angled views or gentle camera drift) and 56 units deep. Being fogImmune means the distant portions of sky remain visible even when fog obscures the far floor and walls, which is the natural atmospheric behavior (sky doesn't fog out in a canyon).

**End wall:** At Z=-48 (the far extent of walls/floor), sized to fill the gap between walls. Optional because some canyon scenes work better with implied infinite depth via fog.

**Subject:** At Z=-10, about 15 units ahead of the camera start. Slightly below center (Y=-1) to sit naturally on/near the canyon floor. Small (6×6) relative to the canyon to emphasize the scale of the environment.

**Camera start position assumption:** The default camera starts at approximately `[0, 0, 5]` per OBJ-003's `DEFAULT_CAMERA.position`. The canyon is designed around this, with the near edges of walls/floor at Z=8 (3 units behind the camera start for safety margin) and extending to Z=-48.

#### Compatible Cameras

```typescript
compatible_cameras: [
  'slow_push_forward',
  'crane_up',
  'dramatic_push',
  'gentle_float',
  'static',
] as const
```

**Rationale for each:**
- `slow_push_forward`: The primary canyon motion — camera glides forward through the space. Walls recede to vanishing point, floor skews into perspective. The defining 2.5D effect for this geometry.
- `crane_up`: Camera rises on Y-axis, revealing the vertical scale of the canyon walls and eventually the sky opening above. Dramatic reveal.
- `dramatic_push`: Faster forward push with ease-out. For emphasis or tension (e.g., approaching something at the end of the canyon).
- `gentle_float`: Subtle multi-axis drift. Good for ambient/atmospheric canyon scenes where the space itself is the subject. The 3-unit near-edge safety margin accommodates this preset's backward Z drift.
- `static`: No movement. For scenes where the canyon framing is enough and a transition handles temporal interest.

**Excluded:** `lateral_track_left`/`lateral_track_right` — lateral movement in a narrow canyon risks revealing wall edges or breaking the enclosed-corridor illusion. `flyover_glide` — the camera is inside the canyon, not above it. `tunnel_push_forward` — similar motion to `slow_push_forward` but tuned for enclosed spaces with ceilings; canyon has open sky. `dolly_zoom` — FOV animation in a narrow space could cause walls to clip or distort unnaturally.

#### Default Camera

```typescript
default_camera: 'slow_push_forward'
```

The forward push is the most natural and dramatic motion for a canyon — it showcases the vanishing-point perspective on both walls and the floor simultaneously.

#### Fog

```typescript
fog: {
  color: '#1a1a2e',
  near: 15,
  far: 48,
}
```

**Rationale:** Dark blue-gray fog (`#1a1a2e`) suggests atmospheric haze and twilight without being pure black (which would feel like a tunnel). Fog starts at distance 15 from camera (so the near portions of the canyon are crisp) and reaches full density at distance 48 (matching the end wall Z-position at Z=-48, which is 53 units from the camera at Z=5 — fog.far of 48 provides near-complete density before the end wall). This naturally obscures the far edges of walls/floor, preventing hard-edge visibility, and adds atmospheric perspective that enhances the depth illusion. If `end_wall` is omitted, fog provides a natural visual terminus.

#### Description

```
"Tall walls on left and right with a floor and open sky above. Camera pushes forward through a narrow dramatic space — a gorge, alley, or corridor between towering structures. Walls recede to a vanishing point with real perspective distortion. Good for dramatic, oppressive, or awe-inspiring environments."
```

#### Preferred Aspect

```typescript
preferred_aspect: 'landscape'
```

Canyon works in both orientations, but landscape (16:9) best showcases the horizontal depth and vanishing-point convergence of the walls. In portrait mode (9:16), the vertical extent of the walls becomes the dominant feature, which is also valid but less showcases the forward-depth effect. Marking as `landscape` for SKILL.md guidance.

### Slot DepthSlot Metadata (OBJ-007 Contract)

The following shows the OBJ-007–specific metadata fields for each slot. These are combined with the spatial and `PlaneSlot` fields from the table above into single slot object literals that satisfy both `PlaneSlot` (OBJ-005) and `DepthSlot` (OBJ-007) interfaces via structural typing.

```typescript
sky: {
  // ... PlaneSlot fields from table above ...
  name: 'sky',
  promptGuidance: 'Wide sky or atmosphere, looking upward. Narrow strip of sky visible between canyon walls. Dramatic clouds, stars, or atmospheric gradient.',
  expectsAlpha: false,
}

left_wall: {
  // ... PlaneSlot fields from table above ...
  name: 'left_wall',
  promptGuidance: 'Tall vertical surface texture — rock face, building facade, cliff wall, ice wall. Seamless/tileable preferred. Dramatic lighting from above.',
  expectsAlpha: false,
}

right_wall: {
  // ... PlaneSlot fields from table above ...
  name: 'right_wall',
  promptGuidance: 'Tall vertical surface texture — matching or complementing left_wall. Can be identical or different for asymmetric canyons.',
  expectsAlpha: false,
}

floor: {
  // ... PlaneSlot fields from table above ...
  name: 'floor',
  promptGuidance: 'Ground surface extending into distance — rocky path, sand, cobblestones, water, lava. Top-down or strongly receding perspective.',
  expectsAlpha: false,
}

end_wall: {
  // ... PlaneSlot fields from table above ...
  name: 'end_wall',
  promptGuidance: 'Distant vista or terminus — light at end of canyon, distant landscape, doorway, or solid wall. Atmospheric, slightly hazy.',
  expectsAlpha: false,
}

subject: {
  // ... PlaneSlot fields from table above ...
  name: 'subject',
  promptGuidance: 'Focal element within the canyon — person, creature, vehicle, landmark. Isolated on transparent background. Scale should feel small relative to canyon walls.',
  expectsAlpha: true,
}
```

### Module Exports

The module has no public exports beyond the side effect of calling `registerGeometry()` at import time. Consumers access the canyon geometry via `getGeometry('canyon')` from the OBJ-005 registry.

```typescript
// src/scenes/geometries/canyon.ts
// No named exports — registration is the side effect

import { registerGeometry } from './registry';
// ... define canyonGeometry ...
registerGeometry(canyonGeometry);
```

The geometry module must be imported (for its registration side effect) by the geometry barrel export `src/scenes/geometries/index.ts`.

## Design Decisions

### D1: 6 slots — structural + subject

The canyon has 4 structural slots (left_wall, right_wall, floor, sky) plus 2 content slots (end_wall, subject). This differs from the tunnel geometry (which has 5 structural slots: floor, ceiling, left_wall, right_wall, end_wall) by replacing `ceiling` with `sky` — the open sky is the canyon's defining spatial distinction from a tunnel.

The optional `subject` slot is included because canyons are often used to frame a focal element (explorer in a gorge, vehicle in an alley). Without it, the geometry is purely environmental — valid, but limiting. Making it optional means the LLM can choose.

**Seed alignment:** TC-01 asks whether 3-5 planes per scene are sufficient for 90% of cases. Canyon uses up to 6 but requires only 4, staying within the spirit of the constraint.

### D2: Walls centered at Y=3, not Y=0

The walls are vertically centered at Y=3 (spanning Y=-6 to Y=12), not at Y=0 (which would be Y=-9 to Y=9). This shifts the "towering above" emphasis upward — from camera height at Y=0, there's 12 units of wall above and 6 below. This matches human perception of canyons: we see far more wall above us than below. The floor at Y=-3 reinforces this asymmetry.

### D3: Sky is a horizontal plane, not a vertical backdrop

The sky uses `rotation=[Math.PI/2, 0, 0]` (horizontal, facing down) rather than the default camera-facing orientation. This is because the sky in a canyon is visible by looking up between the walls — it's overhead, not in front. As the camera moves forward, the sky plane doesn't exhibit parallax in the same way walls do; it simply scrolls overhead, which matches real canyon physics.

The sky is marked `fogImmune: true` because atmospheric fog doesn't obscure the sky in real canyons — it obscures distant ground-level objects. Without fog immunity, the far end of the sky plane would fade to the fog color, creating an unnatural dark band overhead.

### D4: Dark blue-gray fog rather than black

Pure black fog (`#000000`) reads as "underground" or "void." The dark blue-gray (`#1a1a2e`) suggests atmospheric haze, twilight, or natural distance. This is tunable — the manifest can override fog per-scene (OBJ-005's `FogConfig` override). The default is optimized for the most common canyon use case: a dramatic but naturalistic outdoor space.

### D5: No ceiling slot

The canyon's distinction from a tunnel is the open sky. Including a `ceiling` slot would make it a tunnel variant. If a content author needs an enclosed overhead space, they should use the tunnel geometry instead. This keeps the geometry vocabulary clear and non-overlapping (seed AP-06: don't invent synonyms).

### D6: Wall renderOrder equality

Both `left_wall` and `right_wall` share `renderOrder: 1` because they never overlap from any valid camera position (they're on opposite sides of X-space). If they were to overlap from an extreme camera angle, Three.js's depth buffer handles it correctly since they are opaque. Equal renderOrder avoids introducing an arbitrary left-before-right draw order.

### D7: Subject position at Y=-1

The subject is at Y=-1, slightly above the floor (Y=-3) rather than at Y=0 (camera height). This positions the subject's visual center near the lower third of the frame from the default camera, following the rule of thirds and suggesting the subject is standing on the canyon floor. The camera at Y=0 looks slightly down at the subject, which enhances the sense of vertical scale.

### D8: Compatible camera selection is conservative

Only 5 camera paths are marked compatible. This is intentionally conservative — lateral tracks and flyover paths risk breaking the spatial illusion in the narrow canyon. New camera paths designed for canyons (e.g., `canyon_crane_reveal` — starting low and rising to reveal the sky opening) can be added to `compatible_cameras` when they are defined and tuned. The geometry definition can be updated without changing its contract, since `compatible_cameras` is additive.

### D9: Slot objects satisfy both PlaneSlot and DepthSlot via structural typing

Each slot is a single object literal that includes all fields from `PlaneSlot` (OBJ-005: position, rotation, size, required, description, renderOrder, transparent, fogImmune) and all fields from `DepthSlot` (OBJ-007: name, promptGuidance, expectsAlpha). TypeScript structural typing allows this object to satisfy both interfaces without explicit intersection types. The `registerGeometry()` call accepts it as `Record<string, PlaneSlot>` (extra properties are allowed by structural subtyping); downstream OBJ-007 consumers cast or import directly to access the additional metadata. This follows the same pattern established by OBJ-018 (stage geometry).

### D10: 3-unit near-edge safety margin for wall Z-extent

Walls, floor, and sky all extend to Z=8 on their near edge (56 units wide, centered at Z=-20). With the camera starting at Z=5, this provides a 3-unit backward margin. The `gentle_float` camera preset involves subtle multi-axis drift that may push the camera slightly backward; 3 units accommodates this without revealing hard edges. This margin is validated by AC-06's requirement that wall Z-extent exceeds the camera start position by at least 2 world units.

## Acceptance Criteria

- [ ] **AC-01:** A `SceneGeometry` object with `name: 'canyon'` is registered via `registerGeometry()` and retrievable via `getGeometry('canyon')`.
- [ ] **AC-02:** The geometry passes `validateGeometryDefinition()` from OBJ-005 with zero errors.
- [ ] **AC-03:** The geometry defines exactly 6 slots: `sky`, `left_wall`, `right_wall`, `floor`, `end_wall`, `subject`.
- [ ] **AC-04:** Required slots are: `sky`, `left_wall`, `right_wall`, `floor`. Optional slots are: `end_wall`, `subject`.
- [ ] **AC-05:** `left_wall` rotation is `[0, Math.PI/2, 0]` (facing right); `right_wall` rotation is `[0, -Math.PI/2, 0]` (facing left); `floor` rotation is `[-Math.PI/2, 0, 0]` (facing up); `sky` rotation is `[Math.PI/2, 0, 0]` (facing down); `end_wall` and `subject` rotation is `[0, 0, 0]` (facing camera).
- [ ] **AC-06:** Wall planes (`left_wall`, `right_wall`) have Z-extent (via size width after rotation) such that the near edge exceeds the default camera start position (Z=5 per OBJ-003) by at least 2 world units, preventing edge reveal during backward camera drift. The far edge extends to at least Z=-45.
- [ ] **AC-07:** Floor and sky planes have Z-extent (via the appropriate size dimension after rotation) matching the wall Z-extent.
- [ ] **AC-08:** `sky` slot has `fogImmune: true`. All other slots have `fogImmune: false` (or omitted, defaulting to false).
- [ ] **AC-09:** `subject` slot has `transparent: true`. All structural slots have `transparent: false` (or omitted).
- [ ] **AC-10:** `compatible_cameras` contains at least: `'slow_push_forward'`, `'crane_up'`, `'gentle_float'`, `'static'`.
- [ ] **AC-11:** `default_camera` is `'slow_push_forward'` and is present in `compatible_cameras`.
- [ ] **AC-12:** `fog` is defined with `near >= 0`, `far > near`, and `color` matching `#RRGGBB` format.
- [ ] **AC-13:** `description` is non-empty and describes the canyon spatial concept.
- [ ] **AC-14:** `preferred_aspect` is `'landscape'`.
- [ ] **AC-15:** All slot `description` fields are non-empty strings.
- [ ] **AC-16:** All slot `name` fields match their key in the `slots` record.
- [ ] **AC-17:** All slot names match `/^[a-z][a-z0-9_]*$/`.
- [ ] **AC-18:** `renderOrder` values ensure correct draw ordering: sky (0) < walls (1) < floor (2) < end_wall (3) < subject (4).
- [ ] **AC-19:** The canyon's wall gap (distance between `right_wall` X-position and `left_wall` X-position) equals the `floor` slot's size width and equals the `end_wall` slot's size width, producing a spatially consistent corridor.
- [ ] **AC-20:** The geometry module registers itself as a side effect of import, with no named exports.
- [ ] **AC-21:** Each slot has a non-empty `promptGuidance` string providing actionable image generation guidance.
- [ ] **AC-22:** Each slot's `expectsAlpha` is set: `true` for `subject`, `false` for all others.
- [ ] **AC-23:** The sky plane width is at least as wide as the wall gap to prevent sky-edge visibility when the camera is at default position looking upward.

## Edge Cases and Error Handling

### Spatial Edge Cases

| Scenario | Expected Behavior |
|---|---|
| All 4 required slots provided, both optional omitted | Valid. Canyon renders as environment-only: walls, floor, sky. Fog hides the far end naturally. |
| Only `subject` optional provided (no `end_wall`) | Valid. Subject appears in the canyon, fog provides depth terminus. |
| Only `end_wall` optional provided (no `subject`) | Valid. Canyon with a visible destination. |
| All 6 slots provided | Valid. Full canyon with environment, terminus, and focal element. |
| Camera at start position Z=5 | Near edges of walls/floor at Z=8 extend 3 units behind camera. No edge visible — walls begin well behind the camera's position. |
| Camera drifts backward to Z=7 (gentle_float) | Still 1 unit of margin before wall near edge at Z=8. No edge reveal. |
| Camera pushes forward to Z=-20 | Mid-canyon. Walls still extend 28 units ahead of camera. Floor/sky likewise. No edge reveals. |
| Camera rises (crane_up) to Y=10 | Approaching wall tops at Y=12. Sky plane at Y=12 becomes more visible. Walls still have 2 units above camera. Subject below is foreshortened. |
| Portrait mode (9:16) | Walls will be more prominent in frame due to narrower horizontal FOV. The 8-unit wall gap at default camera distance is still sufficient. Vertical extent of walls (18 units) is a strength in portrait. The geometry works but is not optimized for portrait — `preferred_aspect: 'landscape'` is advisory. |

### Override Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Override moves left_wall to X=0 | Valid per `validatePlaneSlots` (finite coordinates), but walls overlap. This is an authoring error, not a validation error — the engine renders it as-is. SKILL.md should warn against moving structural walls. |
| Override sets subject size to `[20, 20]` | Valid. Subject becomes larger than the canyon gap, breaking immersion. Not a validation concern. |
| Override sets floor Y to Y=0 | Valid. Floor rises to camera height. Produces an unusual but renderable scene. |

### Registration Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Canyon module imported after registry is locked | `registerGeometry` throws. The barrel export must import canyon before any read operations occur. |
| Canyon module imported twice | Second `registerGeometry('canyon')` throws duplicate name error per OBJ-005. Standard module caching prevents this in practice. |

## Test Strategy

### Unit Tests

**Registration and retrieval:**
1. After importing the canyon module, `getGeometry('canyon')` returns a defined `SceneGeometry`.
2. `getGeometry('canyon')?.name` equals `'canyon'`.
3. The returned geometry passes `validateGeometryDefinition()` with zero errors.

**Slot structure:**
4. `getAllSlotNames(canyonGeometry)` returns exactly `['end_wall', 'floor', 'left_wall', 'right_wall', 'sky', 'subject']` (alphabetical).
5. `getRequiredSlotNames(canyonGeometry)` returns exactly `['floor', 'left_wall', 'right_wall', 'sky']` (alphabetical).
6. `getOptionalSlotNames(canyonGeometry)` returns exactly `['end_wall', 'subject']` (alphabetical).

**Slot spatial correctness:**
7. `left_wall` position X is negative; `right_wall` position X is positive; they are symmetric about X=0.
8. `left_wall` and `right_wall` have equal absolute X positions (symmetric canyon).
9. `floor` rotation is `[-Math.PI/2, 0, 0]`; `sky` rotation is `[Math.PI/2, 0, 0]`.
10. `left_wall` rotation is `[0, Math.PI/2, 0]`; `right_wall` rotation is `[0, -Math.PI/2, 0]`.
11. `end_wall` and `subject` rotation is `[0, 0, 0]`.
12. `end_wall` Z-position is more negative than `subject` Z-position (further away).
13. `floor` Y-position is negative (below camera default Y=0).
14. `sky` Y-position is greater than or equal to wall center Y + wall height/2 (sky at or above wall tops).

**Slot metadata:**
15. `sky.fogImmune` is `true`.
16. `subject.transparent` is `true`.
17. All slots have non-empty `description`.
18. All slot `name` fields match their record key.
19. `renderOrder` values: sky=0, left_wall=1, right_wall=1, floor=2, end_wall=3, subject=4.

**Camera compatibility:**
20. `isCameraCompatible(canyonGeometry, 'slow_push_forward')` returns `true`.
21. `isCameraCompatible(canyonGeometry, 'crane_up')` returns `true`.
22. `isCameraCompatible(canyonGeometry, 'static')` returns `true`.
23. `isCameraCompatible(canyonGeometry, 'tunnel_push_forward')` returns `false`.
24. `isCameraCompatible(canyonGeometry, 'lateral_track_left')` returns `false`.
25. `default_camera` is in `compatible_cameras`.

**Fog configuration:**
26. `fog` is defined, `fog.near >= 0`, `fog.far > fog.near`.
27. `fog.color` matches `/^#[0-9a-fA-F]{6}$/`.

**Spatial consistency:**
28. Wall gap (right_wall X - left_wall X) equals floor width (size[0]).
29. End wall width (size[0]) equals floor width (size[0]).
30. Wall Z-extent (size[0], which maps to Z after rotation, centered at wall Z-position) spans near edge at least 2 units beyond Z=5 (camera start), and far edge at least to Z=-45.

**Immutability:**
31. Attempting to mutate `getGeometry('canyon')?.slots.floor.position[0]` throws `TypeError` (deep freeze from OBJ-005 registry).

### Relevant Testable Claims

- **TC-01 (partial):** Canyon uses 4-6 planes, within the 3-5 sweet spot (4 required, 6 max), validating sufficiency for dramatic corridor scenes.
- **TC-04 (partial):** An LLM can author a canyon manifest using only slot names and geometry name — no XYZ coordinates needed.
- **TC-05 (analogous):** Though TC-05 is specifically about tunnels, the same "traveling through a space" claim applies to canyons — walls should visibly recede to a vanishing point with a forward camera push.
- **TC-08 (partial):** Canyon is one of the 8 proposed geometries. Its inclusion expands the design space coverage.

## Integration Points

### Depends on

| Upstream | What OBJ-020 imports |
|---|---|
| **OBJ-005** (Scene geometry type contract) | `SceneGeometry`, `PlaneSlot`, `FogConfig` types. `registerGeometry()` function. `getAllSlotNames`, `getRequiredSlotNames`, `getOptionalSlotNames`, `isCameraCompatible` for testing. |
| **OBJ-007** (Depth model) | `DepthSlot`, `SlotSet` types. `SLOT_NAME_PATTERN` for slot name compliance. `isValidSlotName` for validation. OBJ-007's `promptGuidance` and `expectsAlpha` field contracts inform the per-slot metadata. |

### Consumed by

| Downstream | How it uses OBJ-020 |
|---|---|
| **OBJ-061** (Canyon visual tuning) | Renders test videos with the canyon geometry and compatible camera paths. The Director Agent reviews and the HITL loop tunes spatial values (wall gap, wall height, fog settings, subject position). |
| **OBJ-036** (Scene sequencer) | Looks up `getGeometry('canyon')` when a manifest scene specifies `geometry: 'canyon'`. Routes to the canyon slot definitions for mesh instantiation. |
| **OBJ-039** (Page-side geometry instantiation) | Creates Three.js meshes from canyon slot definitions — reads position, rotation, size, renderOrder, transparent, fogImmune for each slot. |
| **OBJ-040** (Plane sizing / edge-reveal validation) | Validates that canyon planes are oversized enough for compatible camera paths. May flag edge reveals and recommend size adjustments. |
| **OBJ-041** (Geometry-camera compatibility) | Cross-references canyon's `compatible_cameras` against defined camera path presets. |
| **OBJ-071** (SKILL.md) | Documents the canyon geometry: when to use it, what images to generate per slot, which cameras work with it. |

### File Placement

```
depthkit/
  src/
    scenes/
      geometries/
        canyon.ts         # Canyon geometry definition + registerGeometry() call
        index.ts          # Updated barrel export to import './canyon' for side effect
```

## Open Questions

### OQ-A: Should wall textures be mirrored or independent?

The left and right wall accept independent textures, allowing asymmetric canyons (e.g., rock face on left, ice wall on right). However, many real canyons have visually similar walls. Should the geometry support a convenience mode where a single wall texture is automatically applied to both walls (mirrored)?

**Recommendation:** No. Keep slots independent. If the LLM wants matching walls, it assigns the same image to both slots. A `mirror_walls` flag adds manifest schema complexity for a trivial convenience. Defer to SKILL.md guidance: "For symmetric canyons, use the same image for left_wall and right_wall."

### OQ-B: Should the canyon support variable wall height?

The wall height is fixed at 18 world units in the geometry default. Some canyon scenes might want shorter walls (a shallow gully) or taller walls (a deep chasm). This is already handleable via `PlaneOverride` on the wall size, but is the default 18-unit height appropriate for most cases?

**Recommendation:** 18 units is a good starting point — it provides dramatic vertical scale relative to the 8-unit gap. Tuning during OBJ-061 (visual tuning) will validate or adjust this. The override escape hatch covers edge cases.

### OQ-C: Exact spatial values subject to visual tuning

All position, rotation, and size values in this spec are mathematically reasoned starting points. OBJ-061 (canyon visual tuning) will validate these through the Director Agent workflow and may adjust them. The acceptance criteria test structural relationships (symmetry, extent, consistency) rather than exact numeric values, so tuning adjustments won't break tests as long as spatial invariants hold.

---

## Changes from Round 1

**Issue 1 (Major — PlaneSlot/DepthSlot type ambiguity):** Added D9 design decision explaining that each slot object satisfies both interfaces via structural typing, following OBJ-018's established pattern. Added a clarifying paragraph at the start of the Interface Contract's Slots section. Added introductory sentence to the DepthSlot Metadata section making the complementary-views relationship explicit.

**Issue 2 (Major — zero safety margin at Z=5):** Increased wall/floor/sky size from 50 to 56 units, shifting near edge from Z=5 to Z=8 (3-unit margin). Moved end_wall from Z=-45 to Z=-48 (at far boundary). Updated fog.far from 45 to 48. Added D10 design decision documenting the margin rationale. Updated AC-06 to require "at least 2 world units" beyond camera start. Updated spatial edge cases table with backward-drift scenario.

**Issue 3 (Minor — test #14 wording):** Changed test #14 to "greater than or equal to."

**Issue 4 (Minor — DepthSlot section context):** Added introductory sentence: "The following shows the OBJ-007–specific metadata fields... These are combined with the spatial and PlaneSlot fields from the table above..."

**Issue 5 (Minor — AC-19 and tests 28-29 imprecision):** Changed "approximately equals" to "equals" in AC-19, test #28, and test #29. These are exact structural invariants.

---

I believe all five issues are now addressed. Challenger, please verify the revisions and confirm whether additional changes are needed.

---

## Round 4 — spec_challenger

I've carefully verified all five revisions from Round 2 against the Round 3 spec:

**Issue 1 (PlaneSlot/DepthSlot type ambiguity):** ✓ D9 added with clear structural typing explanation. Slots section has clarifying paragraph. DepthSlot Metadata section has introductory context sentence. Pattern explicitly references OBJ-018 precedent.

**Issue 2 (Zero safety margin):** ✓ Sizes increased 50→56 (near edge Z=8, 3-unit margin). End wall moved to Z=-48. Fog.far updated to 48. D10 added. AC-06 now requires "at least 2 world units" beyond camera start. Edge cases table includes backward-drift scenario at Z=7. All internally consistent.

**Issue 3 (Test #14):** ✓ Changed to "greater than or equal to."

**Issue 4 (DepthSlot section context):** ✓ Introductory sentence added.

**Issue 5 (AC-19/tests imprecision):** ✓ Changed to "equals." Tests 28-29 updated to exact equality.

I did a fresh pass looking for new issues introduced by the revisions:

**Observation: end_wall fully obscured by default fog** — Camera at Z=5, fog.far=48, end_wall at Z=-48 = 53 units from camera. The end_wall is past full fog density by 5 units, making it invisible with default settings. This is a minor quirk, not a bug: end_wall is optional, fog is overridable, and the spec already documents this interaction. I'll note it as an open question in the final spec rather than requiring a revision.

All rotations verified against Three.js coordinate system. All spatial relationships are self-consistent. Acceptance criteria are specific and testable. Vocabulary is seed-compliant. The spec stays within OBJ-020's boundaries (geometry definition, no rendering code). Integration points match dependency contracts.

CONCLUSION:

The canyon geometry spec is complete and ready for implementation. It defines a 6-slot geometry (4 required: sky, left_wall, right_wall, floor; 2 optional: end_wall, subject) with 56-unit depth planes providing a 3-unit safety margin, conservative camera compatibility, dark blue-gray fog, and clear structural invariants in acceptance criteria. All five issues from Round 2 have been satisfactorily resolved.

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me first check the current state of the meta.json and any existing files:
[Tool: Read]
  Input: {
  "file_path": "/home/user/repos/depthkit/nodes/OBJ-020/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "ls nodes/OBJ-020/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-020 node directory exists"
}

[Tool: Bash]
  Input: {
  "command": "cat nodes/OBJ-020/meta.json 2>/dev/null || echo \"No meta.json\"",
  "description": "Check current meta.json contents"
}
[Tool Result] meta.json
[Tool Result] {
  "id": "OBJ-020",
  "description": "Canyon scene geometry -- tall wall planes on left and right, floor plane, open sky above. Camera pushes forward or floats upward. Good for narrow dramatic spaces. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.",
  "category": "spatial",
  "created_by_session": "initializer",
  "created_at": "2026-03-22T00:00:00Z",
  "updated_at": "2026-03-22T00:00:00Z",
  "depends_on": ["OBJ-005", "OBJ-007"],
  "visual_status": null,
  "tuning_rounds": 0,
  "notes": "Tier 2 geometry."
}
Good. Now let me write the final spec and update meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "content": "# Specification: Canyon Scene Geometry (OBJ-020)\n\n## Summary\n\nOBJ-020 defines the **canyon** scene geometry \u2014 a narrow, vertically dramatic 3D space with tall wall planes on left and right, a floor plane, an open sky above, and an optional end wall at depth. The camera pushes forward through the canyon or floats upward to reveal vertical scale. This geometry produces the feeling of traveling through a narrow gorge, alley, corridor between tall buildings, or any space defined by towering vertical boundaries. It registers itself via `registerGeometry()` from OBJ-005 and defines its slot set per OBJ-007's depth model contract.\n\n## Interface Contract\n\n### Geometry Definition\n\n```typescript\n// src/scenes/geometries/canyon.ts\n\nimport type { SceneGeometry, PlaneSlot, FogConfig } from './types';\nimport { registerGeometry } from './registry';\n```\n\nThe module defines and registers a single `SceneGeometry` object with the following structure:\n\n#### Geometry Name\n```\nname: 'canyon'\n```\n\n#### Slots\n\nThe canyon geometry defines **6 slots**. The spatial concept: two tall, deep wall planes forming a narrow corridor, a floor extending into depth, an open sky visible above, and an optional end wall providing a visual terminus. An optional `subject` slot places a focal element within the canyon.\n\nEach slot object is constructed with all fields required by both the `PlaneSlot` interface (from OBJ-005, for `registerGeometry()`) and the `DepthSlot` metadata fields from OBJ-007 (`name`, `promptGuidance`, `expectsAlpha`). TypeScript's structural typing allows a single object literal to satisfy both interfaces. The `SceneGeometry.slots` record is typed as `Record<string, PlaneSlot>` for the registry; downstream consumers that need OBJ-007 metadata (OBJ-051 SKILL.md, OBJ-053 prompt templates) access the additional fields by importing 
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md
Now update meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-020",
     3→  "description": "Canyon scene geometry -- tall wall planes on left and right, floor plane, open sky above. Camera pushes forward or floats upward. Good for narrow dramatic spaces. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-005", "OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 geometry."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/meta.json",
  "content": "{\n  \"id\": \"OBJ-020\",\n  \"description\": \"Canyon scene geometry -- tall wall planes on left and right, floor plane, open sky above. Camera pushes forward or floats upward. Good for narrow dramatic spaces. Defines slot positions, rotations, sizes, required/optional flags, compatible cameras, default camera, and fog settings per Section 4.2.\",\n  \"category\": \"spatial\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T03:00:00Z\",\n  \"depends_on\": [\"OBJ-005\", \"OBJ-007\"],\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 geometry. Spec deliberation completed: 6 slots (4 required: sky, left_wall, right_wall, floor; 2 optional: end_wall, subject), 56-unit depth planes with 3-unit safety margin, 5 compatible cameras, dark blue-gray fog. All spatial values are starting points subject to OBJ-061 visual tuning.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/meta.json has been updated successfully.
Now commit:
[Tool: Bash]
  Input: {
  "command": "git status --short nodes/OBJ-020/",
  "description": "Check git status for OBJ-020 files"
}
[Tool Result]  M nodes/OBJ-020/meta.json
?? nodes/OBJ-020/output.md

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Check recent commit style"
}
[Tool Result] 85a7d42 spec(OBJ-019): tunnel scene geometry specification
9ea9d41 spec(OBJ-011): Puppeteer-to-page message protocol
d9a7835 OBJ-027: Push/pull camera path preset specification
6c02bd2 spec(OBJ-015): Texture loader and format handling specification
af6acf5 spec(OBJ-018): stage scene geometry -- default geometry with 6 slots

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-020/output.md nodes/OBJ-020/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-020): canyon scene geometry specification\n\n6-slot geometry (4 required: sky, left_wall, right_wall, floor; 2 optional:\nend_wall, subject) with 56-unit depth planes providing 3-unit safety margin\nfor backward camera drift. Conservative 5-camera compatibility, dark\nblue-gray fog defaults, structural invariant acceptance criteria.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-020 spec files"
}
[Tool Error] Could not parse command for security validation: git add nodes/OBJ-020/output.md nodes/OBJ-020/meta.json && git commit -m "$(cat <<'EOF'
spec(OBJ-020): canyon scene geometry specification

6-slot geometry (4 required: sky, left_wall, right_wall, floor; 2 optional:
end_wall, subject) with 56-unit depth planes providing 3-unit safety margin
for backward camera drift. Conservative 5-camera compatibility, dark
blue-gray fog defaults, structural invariant acceptance criteria.

Co-Authored-By: Claude 

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-020/output.md nodes/OBJ-020/meta.json",
  "description": "Stage OBJ-020 files"
}
[Tool Result] (Bash completed with no output)

[Tool: Bash]
  Input: {
  "command": "git commit -m \"spec(OBJ-020): canyon scene geometry specification\" -m \"6-slot geometry (4 required: sky, left_wall, right_wall, floor; 2 optional: end_wall, subject) with 56-unit depth planes providing 3-unit safety margin for backward camera drift. Conservative 5-camera compatibility, dark blue-gray fog defaults, structural invariant acceptance criteria.\" -m \"Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\"",
  "description": "Commit OBJ-020 spec"
}
[Tool Error] Could not parse command for security validation: git commit -m "spec(OBJ-020): canyon scene geometry specification" -m "6-slot geometry (4 required: sky, left_wall, right_wall, floor; 2 optional: end_wall, subject) with 56-unit depth planes providing 3-unit safety margin for backward camera drift. Conservative 5-camera compatibility, dark blue-gray fog defaults, structural invariant acceptance criteria." -m "Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

[Tool: Bash]
  Input: {
  "command": "git commit -m \"spec(OBJ-020): canyon scene geometry specification\"",
  "description": "Commit OBJ-020 spec"
}
[Tool Result] [master fd55d28] spec(OBJ-020): canyon scene geometry specification
 2 files changed, 392 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-020/output.md
Spec written and committed. The OBJ-020 canyon geometry specification is finalized with all issues resolved:

- **2 major issues fixed:** PlaneSlot/DepthSlot type composition clarified via D9; wall Z-extent increased from 50→56 units providing 3-unit safety margin (D10)
- **3 minor issues fixed:** Test #14 corrected to "greater than or equal to"; DepthSlot section given context; AC-19 and tests 28-29 changed from "approximately" to "equals"
- **1 new open question added:** OQ-D documents that end_wall is fully obscured by default fog settings, for OBJ-061 tuning consideration
