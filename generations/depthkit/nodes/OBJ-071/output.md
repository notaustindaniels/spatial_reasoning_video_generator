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
- `tunnel_push_forward`: "Scales Z displacement **and Y-axis rise amplitude proportionally**. Default 1.0 = 25 units of Z travel, 0.3 units of Y rise. speed=0.5 -> 12.5 units Z, 0.15 units Y rise."
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
- [ ] **AC-40:** Speed parameter documented as scaling Z displacement **and Y-axis rise amplitude proportionally**. Default 1.0 = 25 units of Z travel, 0.3 units of Y rise. speed=0.5 -> 12.5 units Z, 0.15 units Y rise.
- [ ] **AC-41:** Motion description notes the deep Z-axis push, the subtle Y-axis rise, and the wall convergence toward a vanishing point.

#### Flyover Glide — Full Section

- [ ] **AC-42:** Contains a full section for `flyover_glide` following the camera section template.
- [ ] **AC-43:** Flyover glide compatible geometries listed as: `flyover` — matching OBJ-030.
- [ ] **AC-44:** Default easing documented as `ease_in_out` — matching OBJ-030.
- [ ] **AC-45:** Speed parameter documented as scaling Z displacement only; camera elevation (Y) is constant. Default 1.0 = 30 units of Z travel.
- [ ] **AC-46:** Motion description notes the elevated camera position, constant downward viewing angle (~34 degrees below horizontal), and the co-moving lookAt that maintains consistent aerial perspective.

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
| Visual tuning (OBJ-059-OBJ-066) changes slot positions/sizes | Positions and sizes are NOT documented in SKILL.md (LLMs don't need them — they use slot names, not coordinates). Fog colors, compatible cameras, and slot names ARE documented and must be updated if tuning changes them. |
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
| **OBJ-059-OBJ-066** (Visual tuning) | If visual tuning changes compatible cameras or fog settings, the corresponding sections in geometry-reference.md and camera-reference.md must be updated. OBJ-071 establishes the content that tuning may revise. |
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

### OQ-D: Should the Lateral Track / Canyon Asymmetry Be Escalated?

The one-directional compatibility claim (OBJ-028 claims canyon, OBJ-020 doesn't reciprocate) may indicate a spec-level inconsistency that should be resolved upstream — either canyon should add lateral tracks to `compatible_cameras`, or OBJ-028 should remove canyon from `compatibleGeometries`. This is beyond OBJ-071's scope (documentation reflects verified specs, doesn't resolve spec conflicts). **Recommendation:** Flag this asymmetry for the integrator/reviewer. OBJ-071 documents it transparently per D9.
