# Deliberation Transcript: OBJ-070

---

## Round 1 — spec_author

# Specification: OBJ-070 — SKILL.md Structure and Core Content

## Summary

OBJ-070 defines the SKILL.md document architecture and core content — the single authoritative reference that enables an LLM agent (with no visual perception) to produce valid depthkit manifests for arbitrary video topics. The document uses a modular structure: a primary `SKILL.md` file covering manifest authoring with a complete annotated example (using the `stage` geometry and `slow_push_forward` camera), plus sub-files for geometry reference, camera reference, and prompt templates. Per SC-04, an LLM reading only SKILL.md (and its sub-files) must be able to produce a valid manifest without access to engine source code. Per seed Section 4.9, the document must fit within a single LLM context window (primary file + loaded sub-files).

## Interface Contract

### Document Architecture

SKILL.md is not code — it's a structured Markdown document system. The "interface" is the file layout and the information contracts each file fulfills.

```
depthkit/
  SKILL.md                              # Primary entry point — manifest authoring guide
  docs/
    skill/
      geometry-reference.md             # All scene geometries: slots, descriptions, usage guidance
      camera-reference.md               # All camera path presets: motion descriptions, compatible geometries
      prompt-templates.md               # Image generation prompt templates per slot type
      manifest-schema-reference.md      # Complete schema field reference (types, defaults, constraints)
      patterns.md                       # Common multi-scene video patterns (explainer, social clip, etc.)
```

### Primary File: `SKILL.md`

The primary file is the entry point an LLM reads first. It must be **self-contained enough** that an LLM can produce a valid manifest reading only this file, but it references sub-files for extended detail. The primary file contains:

1. **Purpose Statement** — What depthkit is, what SKILL.md teaches, the blind-authoring constraint.
2. **Quick Start** — Minimal viable manifest (3-scene example using `stage` + `slow_push_forward`) with inline annotations explaining every field.
3. **Manifest Structure Overview** — Top-level shape (`version`, `composition`, `scenes`), field summary with types and defaults.
4. **Scene Authoring Workflow** — Step-by-step: choose geometry → choose camera → assign images to slots → set timing → set transitions.
5. **Geometry Summary Table** — One-row-per-geometry table with name, description, required slots, optional slots, default camera, and `when to use` guidance. Full details in `geometry-reference.md`.
6. **Camera Summary Table** — One-row-per-camera table with name, description, compatible geometries, motion type, and `when to use` guidance. Full details in `camera-reference.md`.
7. **Transitions Reference** — Inline (not a sub-file). The three transition types, duration guidance, adjacency rules.
8. **Easing Reference** — Inline. The six easing names, plain-English descriptions of their feel.
9. **Audio Synchronization** — How `start_time` and `duration` relate to audio, how to distribute scenes across audio duration.
10. **Anti-Patterns** — Critical mistakes to avoid (text in parallax layers, raw coordinates instead of presets, missing required slots, incompatible camera-geometry pairs).
11. **Sub-File Pointers** — Explicit references: "For full geometry details, see `docs/skill/geometry-reference.md`", etc.
12. **Complete Annotated Example** — A full, production-quality manifest (5 scenes, multiple geometries, transitions, audio) with line-by-line annotations.

**Size target:** The primary `SKILL.md` should be under 400 lines of Markdown (approximately 12-15KB). Sub-files add detail for when the LLM needs deeper reference. The combined total (primary + all sub-files) should stay under 2000 lines (~60KB) to fit comfortably within a single context window alongside a system prompt and conversation history.

### Sub-File: `docs/skill/geometry-reference.md`

One section per registered geometry. Each section contains:

```markdown
### `stage`

**Description:** [From geometry's `description` field]

**When to use:** [Authoring guidance — what kinds of scenes/topics suit this geometry]

**Required slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `backdrop` | Primary background — landscape, environment, or atmospheric backdrop. | Full-scene wide image. No foreground elements. No transparency needed. |
| `floor` | Ground surface with perspective foreshortening. | Top-down or tileable ground texture. No transparency needed. |
| `subject` | Primary focal element. | Isolated subject on transparent background. |

**Optional slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `sky` | Distant sky/gradient behind backdrop. | Wide atmospheric image. No transparency needed. |
| `midground` | Middle-distance environmental element. | Environmental prop or terrain. No transparency needed. |
| `near_fg` | Foreground framing element. | Particles, foliage, bokeh on transparent background. |

**Default camera:** `slow_push_forward`

**Compatible cameras:** `static`, `slow_push_forward`, `slow_pull_back`, `lateral_track_left`, `lateral_track_right`, `gentle_float`, `dramatic_push`, `crane_up`

**Fog:** Black fog, fades distant elements. Sky and near_fg are fog-immune.

**Tips:**
- The floor plane is what makes this geometry feel 3D — always provide a floor image.
- Subject images MUST have transparent backgrounds to avoid rectangular edges.
- [Additional authoring tips]
```

This section is generated/authored from the registered geometry data (OBJ-018's `stageGeometry` definition, OBJ-007's depth slot taxonomy for prompt guidance). The content must be **manually authored** for quality — not auto-generated — but must stay consistent with the registered geometry definitions.

### Sub-File: `docs/skill/camera-reference.md`

One section per registered camera preset. Each section contains:

```markdown
### `slow_push_forward`

**Motion:** Camera moves forward along the Z axis into the scene.

**Feel:** Cinematic dolly push. Gentle acceleration, sustained motion, gentle deceleration. The defining 2.5D motion — planes at different depths shift at different rates, creating natural parallax.

**When to use:** Default for most scenes. Creates depth and immersion. Good for revealing detail, building intensity, or simply adding life to a static composition.

**Compatible geometries:** stage, tunnel, canyon, flyover, diorama, portal, close_up

**Parameters:**
| Param | Default | Effect |
|-------|---------|--------|
| `speed` | `1.0` | Scale of camera displacement. 0.5 = subtle, 1.0 = standard, 1.5 = dramatic. |
| `easing` | `ease_in_out` | Timing curve. `linear` for uniform motion, `ease_in` for slow start. |

**Notes:**
- At speed > 1.5, the camera may pass through foreground elements — this is intentional for near_fg (particles exit the view) but avoid for subject planes.
- Pairs naturally with `ease_in_out` for a dolly feel or `ease_out` for a settling feel.
```

### Sub-File: `docs/skill/prompt-templates.md`

Prompt engineering templates organized by slot type (per seed Section 4.7). Each slot type has:

```markdown
### Slot Type: `backdrop` / `back_wall` / `sky`

**Purpose:** Full-scene background images. No foreground elements. Fill the entire frame.

**Prompt template:**
```
[scene description], wide angle, expansive, atmospheric, no objects in foreground, cinematic, 16:9 aspect ratio
```

**Examples:**
- "Expansive ocean horizon at sunset, wide angle, atmospheric, no objects in foreground, cinematic"
- "Dense bamboo forest interior, deep perspective, atmospheric haze, wide angle, no foreground objects"
- "Futuristic city skyline at night, neon lights, wide angle, atmospheric, cinematic"

**Key rules:**
- Always specify "no objects in foreground" or "no foreground elements"
- Include "wide angle" for spatial coverage
- Include "atmospheric" for depth-appropriate haze
```

Similar sections for `floor`, `subject` (with transparency instructions), `near_fg` (with transparency + bokeh/particle guidance), and `midground`.

### Sub-File: `docs/skill/manifest-schema-reference.md`

Complete field-by-field schema reference extracted from OBJ-004. Organized as a flat reference table — not a tutorial. Includes:

- Every field path (e.g., `composition.width`, `scenes[].camera_params.speed`)
- Type, default value, constraints (min/max/enum)
- Brief description
- Error code produced when invalid

This is the "man page" — consulted for specific questions, not read end-to-end.

### Sub-File: `docs/skill/patterns.md`

Common multi-scene video patterns:

```markdown
### 5-Scene Explainer Video (60-90 seconds)

**Structure:**
1. **Opening** (8-12s): `stage` + `slow_push_forward` — establish topic with a subject.
2. **Context** (10-15s): `diorama` or `canyon` + `gentle_float` — show environment/setting.
3. **Detail 1** (10-15s): `tunnel` + `tunnel_push_forward` — immersive detail exploration.
4. **Detail 2** (10-15s): `stage` + `lateral_track_left` — second angle on topic.
5. **Closing** (8-12s): `stage` + `slow_pull_back` — pull back to reveal, closing feel.

**Transitions:** `crossfade` (1.0s) between all scenes. `dip_to_black` (0.5s) on first scene's entry and last scene's exit.

**Audio:** Narration drives timing. Distribute scene durations to match narration segments.
```

Additional patterns: "30-Second Social Clip", "Ambient Loop", "Before/After Comparison".

## Design Decisions

### D1: Modular Document Architecture (Primary + Sub-Files)

**Decision:** A primary `SKILL.md` at the repo root with sub-files in `docs/skill/`.

**Rationale:** Seed Section 4.9 explicitly calls for "a single document (or primary document with modular sub-files)." SC-04 requires it to fit within a single context window. A monolithic file covering all 8 geometries, all camera presets, prompt templates, patterns, and schema reference would exceed 3000+ lines — too large for useful context alongside conversation history. The modular approach lets an LLM load only the sub-files relevant to its current task:
- Authoring a new manifest? Load `SKILL.md` (primary) + `geometry-reference.md` + `camera-reference.md`.
- Debugging image generation? Load `prompt-templates.md`.
- Checking a specific field constraint? Load `manifest-schema-reference.md`.

**Alternative rejected:** A single monolithic `SKILL.md`. Exceeds practical context limits when combined with system prompts and conversation.

### D2: Primary File Includes Complete Annotated Example Using `stage` + `slow_push_forward`

**Decision:** The primary `SKILL.md` contains a full annotated manifest example using `stage` geometry with `slow_push_forward` camera as the primary example, since these are the reference implementations (OBJ-018 is "the default, most fundamental geometry"; OBJ-027's `slow_push_forward` is "the defining camera motion for 2.5D projection").

**Rationale:** Per the objective description: "manifest authoring guide with a complete, annotated example using stage geometry and slow_push_forward camera path." An LLM learns best from complete, correct examples. The `stage` + `slow_push_forward` combination is the simplest correct configuration — 3 required slots, pure Z-axis motion, no complex spatial reasoning needed.

### D3: Two Examples — Quick Start (Minimal) and Complete (Production-Quality)

**Decision:** The primary file includes TWO manifest examples:
1. A **minimal quick-start example** — single scene, `stage` geometry, `slow_push_forward` camera, 3 required slots only, no transitions, no audio. This is the "hello world" that teaches manifest structure.
2. A **complete annotated example** — 5 scenes, multiple geometries, transitions, audio sync, camera parameter overrides. This demonstrates production usage.

**Rationale:** A single complex example overwhelms. A single trivial example doesn't teach real usage. Two examples serve different learning stages. The minimal example teaches structure; the complete example teaches composition.

### D4: Geometry and Camera Summaries Inline; Details in Sub-Files

**Decision:** The primary `SKILL.md` includes summary tables for all geometries and cameras (one row per entry — name, description, key slots, when to use). Full slot definitions, spatial details, and authoring tips live in sub-files.

**Rationale:** An LLM authoring a manifest needs to select a geometry and camera quickly. A summary table supports this without forcing the LLM to load and parse full sub-files. When more detail is needed (e.g., "what optional slots does `tunnel` have?"), the sub-file provides it.

### D5: Prompt Templates as a Separate Sub-File

**Decision:** Image generation prompt templates are in `docs/skill/prompt-templates.md`, not inline in `SKILL.md`.

**Rationale:** Per AP-04, the rendering engine is separate from asset generation. SKILL.md focuses on manifest authoring (the engine's input contract). Prompt templates serve a different pipeline stage (image generation). Separating them keeps the primary file focused and allows the prompt templates to be loaded independently by the asset generation pipeline without pulling in the full manifest authoring guide.

### D6: Anti-Patterns Section Mirrors Seed Section 7 (Selective)

**Decision:** The anti-patterns section in SKILL.md surfaces the **author-facing** anti-patterns from the seed: AP-03 (no manual coordinates), AP-07 (no text in parallax layers), AP-08 context (position_override is an escape hatch, not primary), plus manifest-specific anti-patterns discovered during the authoring of this spec.

**Rationale:** Not all seed anti-patterns are relevant to manifest authors. AP-01 (don't build a general-purpose editor), AP-02 (don't bypass Puppeteer frame loop), AP-09/AP-10 (Director Agent rules) are engine-developer concerns, not manifest-author concerns. SKILL.md surfaces only what affects authoring decisions.

### D7: Scene Authoring Workflow as a Numbered Checklist

**Decision:** A step-by-step numbered workflow: (1) Choose geometry, (2) Choose camera, (3) Assign images to slots, (4) Set duration and start_time, (5) Set transitions, (6) Repeat for each scene, (7) Set composition globals, (8) Validate.

**Rationale:** LLMs follow structured procedures well. A numbered checklist reduces the likelihood of missing steps (e.g., forgetting to check camera-geometry compatibility, or forgetting `transition_in` on the first scene should not be `crossfade`).

### D8: Content Is Manually Authored, Not Auto-Generated

**Decision:** SKILL.md content is written by hand (by the implementing agent), not auto-generated from registry data.

**Rationale:** Auto-generated documentation from type definitions produces technically correct but pedagogically poor results. SKILL.md's purpose is to teach — it needs plain-English explanations, "when to use" guidance, authoring tips, and worked examples that reflect human (or Director Agent) insight into what makes good scenes. The content must stay **consistent** with the registered definitions (acceptance criteria verify this), but the prose is authored for clarity, not derived from code.

### D9: Version Field and Forward Compatibility

**Decision:** SKILL.md includes a version indicator at the top (e.g., `Depthkit SKILL Reference — v3.0`) and notes that manifests must specify `"version": "3.0"`.

**Rationale:** As geometries and cameras are added (OBJ-019 through OBJ-025, OBJ-028 through OBJ-034), sub-files will be updated. A version indicator helps LLMs and humans know which revision they're working with. The manifest version `"3.0"` is enforced by OBJ-004's `z.literal("3.0")`.

### D10: Transition Adjacency Rules Documented Inline

**Decision:** Transition rules (crossfade requires adjacent scene, dip_to_black doesn't, cut is instant) are documented inline in the primary file, not in a sub-file.

**Rationale:** Transition errors (`CROSSFADE_NO_ADJACENT`) are among the most common manifest authoring mistakes. The rules are compact (3 transition types, 2 adjacency rules) and belong next to the scene authoring workflow where the LLM will encounter them.

### D11: Sub-File Loading Guidance via Explicit Instructions

**Decision:** The primary SKILL.md includes explicit loading instructions for LLM agents:

```markdown
## Sub-File Loading Guide

When authoring a manifest, load these files as needed:
- **Always load:** This file (`SKILL.md`)
- **For geometry selection:** `docs/skill/geometry-reference.md`
- **For camera selection:** `docs/skill/camera-reference.md`  
- **For image generation:** `docs/skill/prompt-templates.md`
- **For schema details:** `docs/skill/manifest-schema-reference.md`
- **For multi-scene patterns:** `docs/skill/patterns.md`
```

**Rationale:** LLM agents using tool-use (file reading) need to know which files to load and when. Explicit instructions prevent the agent from either loading everything (wasting context) or loading nothing (missing critical reference).

### D12: Geometry and Camera Data Sourced from Verified Dependencies

**Decision:** The stage geometry section uses data from OBJ-018 (verified). Camera data uses OBJ-027 (verified) for push/pull and OBJ-026/OBJ-031 for static/gentle_float (verified). Other geometries and cameras referenced in summary tables use forward references with a note that details will be added as those objectives are verified.

**Rationale:** OBJ-070 depends on OBJ-004, OBJ-046, OBJ-018, and OBJ-027 — all verified. The SKILL.md must be accurate for these. Other geometries (OBJ-019 through OBJ-025) and cameras (OBJ-028 through OBJ-034) are at various stages. The initial SKILL.md covers the verified content fully and includes stub sections for unverified content, clearly marked.

### D13: CLI Usage Section

**Decision:** The primary SKILL.md includes a brief CLI usage section referencing OBJ-046's three commands (`render`, `validate`, `preview`) with example invocations.

**Rationale:** SC-04 requires self-sufficiency. An LLM that has authored a manifest needs to know how to render it. CLI commands are the final step of the authoring workflow.

### D14: `position_override` and `rotation_override` Documented as Escape Hatches

**Decision:** The SKILL.md documents `position_override` and `rotation_override` on `PlaneRef` in the schema reference sub-file, with a prominent warning: "These are escape hatches for edge cases. If you need them for most planes, you've chosen the wrong geometry."

**Rationale:** AP-03 (do not require manual coordinate entry) and AP-08 (do not hard-code the depth model — allow overrides). The documentation must balance both: overrides exist, but they're not the primary authoring path.

## Acceptance Criteria

### Document Existence and Structure

- [ ] **AC-01:** `SKILL.md` exists at the repository root.
- [ ] **AC-02:** `docs/skill/geometry-reference.md` exists.
- [ ] **AC-03:** `docs/skill/camera-reference.md` exists.
- [ ] **AC-04:** `docs/skill/prompt-templates.md` exists.
- [ ] **AC-05:** `docs/skill/manifest-schema-reference.md` exists.
- [ ] **AC-06:** `docs/skill/patterns.md` exists.

### Primary File Content (SKILL.md)

- [ ] **AC-07:** Contains a purpose statement explaining depthkit's 2.5D parallax video generation and the blind-authoring constraint.
- [ ] **AC-08:** Contains a minimal quick-start manifest example using `stage` geometry and `slow_push_forward` camera with only the 3 required slots (`backdrop`, `floor`, `subject`).
- [ ] **AC-09:** The quick-start example is a valid JSON manifest that passes `loadManifest()` validation when the `stage` geometry and `slow_push_forward` camera are registered.
- [ ] **AC-10:** Contains a complete annotated production example with at least 3 scenes, at least 2 different geometries, transitions, and audio configuration.
- [ ] **AC-11:** The complete annotated example is valid JSON that passes `loadManifest()` validation against registered geometries and cameras.
- [ ] **AC-12:** Contains a scene authoring workflow as a numbered step-by-step checklist covering: geometry selection, camera selection, slot assignment, timing, and transitions.
- [ ] **AC-13:** Contains a geometry summary table listing at minimum `stage` with its required/optional slots, default camera, and "when to use" guidance.
- [ ] **AC-14:** Contains a camera summary table listing at minimum `slow_push_forward`, `slow_pull_back`, `static`, and `gentle_float` with their compatible geometries and "when to use" guidance.
- [ ] **AC-15:** Contains inline transition reference documenting `cut`, `crossfade`, and `dip_to_black` with adjacency rules (crossfade requires adjacent scene).
- [ ] **AC-16:** Contains inline easing reference listing all 6 easing names (`linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`) with plain-English descriptions.
- [ ] **AC-17:** Contains an anti-patterns section that includes: no text in parallax layers (AP-07), no manual coordinates as primary method (AP-03), and `position_override` is an escape hatch.
- [ ] **AC-18:** Contains CLI usage section with `depthkit render`, `depthkit validate`, and `depthkit preview` example invocations.
- [ ] **AC-19:** Contains sub-file loading guide with explicit instructions for which sub-files to load for which tasks.
- [ ] **AC-20:** The primary file is under 500 lines of Markdown.
- [ ] **AC-21:** Specifies `"version": "3.0"` as the required manifest version.

### Geometry Reference Sub-File

- [ ] **AC-22:** Contains a complete section for `stage` geometry with all 6 slots (3 required, 3 optional), descriptions, image guidance per slot, default camera, compatible cameras, fog description, and authoring tips.
- [ ] **AC-23:** The `stage` section's slot names match exactly: `sky`, `backdrop`, `floor`, `midground`, `subject`, `near_fg` (from OBJ-018).
- [ ] **AC-24:** The `stage` section's required slots match OBJ-018: `backdrop`, `floor`, `subject`.
- [ ] **AC-25:** The `stage` section's compatible cameras match OBJ-018's `compatible_cameras` list.
- [ ] **AC-26:** Contains stub sections for other geometries (tunnel, canyon, flyover, diorama, portal, panorama, close_up) clearly marked as "details pending" with brief descriptions from seed Section 4.2.
- [ ] **AC-27:** Each geometry section states which slot images require transparent backgrounds.

### Camera Reference Sub-File

- [ ] **AC-28:** Contains complete sections for `slow_push_forward` and `slow_pull_back` documenting: motion description, feel, when to use, compatible geometries, parameters (speed, easing), and usage notes.
- [ ] **AC-29:** The `slow_push_forward` section's compatible geometries match OBJ-027: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `close_up`.
- [ ] **AC-30:** Contains complete sections for `static` (OBJ-026) and `gentle_float` (OBJ-031) with available details.
- [ ] **AC-31:** Contains stub sections for other camera presets clearly marked as "details pending."
- [ ] **AC-32:** Each camera section documents the `speed` and `easing` parameters with default values and effect descriptions.

### Prompt Templates Sub-File

- [ ] **AC-33:** Contains prompt template sections for at least: `backdrop`/`sky`/`back_wall` (backgrounds), `floor` (ground surfaces), `subject` (focal elements with transparency), and `near_fg` (foreground with transparency).
- [ ] **AC-34:** Each slot type section includes: purpose, prompt template pattern, at least 3 example prompts, and key rules.
- [ ] **AC-35:** Subject and near_fg sections explicitly instruct to prompt for transparent backgrounds (per seed Section 4.7 and OBJ-018's `transparent: true` on those slots).

### Schema Reference Sub-File

- [ ] **AC-36:** Documents every manifest field from OBJ-004: `version`, `composition` (width, height, fps, audio), `scenes[]` (id, duration, start_time, geometry, camera, camera_params, transition_in, transition_out, planes), `PlaneRef` fields (src, opacity, scale, position_override, rotation_override).
- [ ] **AC-37:** Each field lists: type, default value (if any), constraints (min/max/enum values), and the error code produced when invalid.
- [ ] **AC-38:** Documents camera_params fields: speed (default 1.0, must be > 0), easing (enum of 6 values, default ease_in_out), fov_start/fov_end (10-120, optional).

### Patterns Sub-File

- [ ] **AC-39:** Contains at least 3 multi-scene video patterns (e.g., "Explainer Video", "Social Media Clip", "Ambient/Mood Video").
- [ ] **AC-40:** Each pattern specifies: scene count, geometry + camera per scene, transition recommendations, timing guidance, and audio strategy.

### Cross-Consistency

- [ ] **AC-41:** All manifest field names in SKILL.md match OBJ-004's schema exactly (e.g., `start_time` not `startTime`, `transition_in` not `transitionIn`, `camera_params` not `cameraParams`).
- [ ] **AC-42:** All geometry names in SKILL.md match registered geometry names (e.g., `stage` not `Stage`).
- [ ] **AC-43:** All camera preset names match registered names (e.g., `slow_push_forward` not `slowPushForward`).
- [ ] **AC-44:** All easing names match OBJ-004's enum: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`.
- [ ] **AC-45:** All transition type names match OBJ-004's enum: `cut`, `crossfade`, `dip_to_black`.
- [ ] **AC-46:** The vocabulary used throughout matches seed Section 2 definitions (plane not layer, scene geometry not layout template, etc.).

### Self-Sufficiency (SC-04)

- [ ] **AC-47:** An LLM reading only `SKILL.md` (without sub-files) can produce a structurally valid single-scene manifest using the quick-start example as a template.
- [ ] **AC-48:** An LLM reading `SKILL.md` + `geometry-reference.md` + `camera-reference.md` can produce a valid multi-scene manifest for an arbitrary topic.
- [ ] **AC-49:** The total combined size of `SKILL.md` + all sub-files is under 2000 lines / 60KB.

## Edge Cases and Error Handling

SKILL.md is a documentation artifact, not code. "Edge cases" here are authoring scenarios the document must address to prevent common mistakes.

### Manifest Authoring Edge Cases the Document Must Address

| Scenario | How SKILL.md Handles It |
|----------|------------------------|
| LLM uses `crossfade` as `transition_in` on the first scene | Transition rules section explicitly states: "crossfade requires an adjacent scene to blend with. Use `dip_to_black` for the first scene's entry and last scene's exit." |
| LLM provides plane slot keys that don't match the geometry | Scene authoring workflow step 3 says: "Consult the geometry's slot table. Use only the listed slot names." Quick-start example demonstrates correct slot keys. |
| LLM specifies an incompatible camera for a geometry | Scene authoring workflow step 2 says: "Check the camera's compatible geometries list, or the geometry's compatible cameras list." Summary tables show compatibility. |
| LLM puts text on a parallax plane | Anti-patterns section explicitly warns: "Never place text content on scene planes. Text should be a HUD layer (not yet supported in V1) or composited as a post-processing step." |
| LLM uses raw XYZ coordinates instead of geometry presets | Anti-patterns section warns against this. `position_override` is documented in schema reference with "escape hatch" warning. |
| LLM generates images without transparency for subject/near_fg slots | Prompt templates sub-file explicitly instructs on transparency. Geometry reference marks which slots expect transparent images. |
| LLM omits `start_time` | Schema reference documents `start_time` as required (nonnegative number). Quick-start example shows it. |
| LLM provides scenes out of time order | The document notes: "Scenes should be ordered by `start_time` in the array. Out-of-order scenes produce a `SCENE_ORDER_MISMATCH` warning but are still valid — the engine sorts by `start_time` internally." |
| LLM needs 9:16 (portrait) video | Composition section shows both `{width: 1920, height: 1080}` (landscape) and `{width: 1080, height: 1920}` (portrait). Notes that all geometries with `preferred_aspect: 'both'` work in either orientation. |
| Overlapping scene timings | Transition section explains overlap rules: "When two scenes overlap in time, both must have compatible transitions (crossfade or dip_to_black) with durations >= the overlap." |
| Audio duration doesn't match scene total | Audio section notes: "If audio duration differs from the sum of scene durations, the engine renders the scene durations as specified and emits a warning. Adjust scene durations to match audio length." |

### Document Maintenance Edge Cases

| Scenario | Handling |
|----------|----------|
| New geometry added (e.g., OBJ-022 `portal`) | Add a full section to `geometry-reference.md`, update the summary table in `SKILL.md`, update patterns if applicable. The stub section is replaced with full content. |
| New camera preset added | Same pattern: full section in `camera-reference.md`, update summary table. |
| Schema field added/changed | Update `manifest-schema-reference.md`. If it affects authoring workflow, update `SKILL.md` primary file. |
| Camera compatibility list changes after visual tuning (OBJ-059, OBJ-069) | Update both `geometry-reference.md` (geometry's compatible cameras) and `camera-reference.md` (camera's compatible geometries). Cross-check. |

## Test Strategy

SKILL.md is a documentation artifact. Testing verifies **correctness** (does the documented information match the implementation?) and **self-sufficiency** (can an LLM produce valid manifests from it alone?).

### Correctness Tests

1. **Example Manifest Validation:** Extract the quick-start example JSON from `SKILL.md`, parse it, and run it through `loadManifest()` with a fully populated registry. It must return `success: true` with zero errors. Repeat for the complete annotated example.

2. **Slot Name Cross-Check:** For every geometry documented in `geometry-reference.md`, verify that the documented slot names (required and optional) match the actual registered geometry's slot definitions. Specifically: for `stage`, verify slots match OBJ-018's definition exactly.

3. **Camera Compatibility Cross-Check:** For every camera documented in `camera-reference.md`, verify that the documented compatible geometries match the preset's `compatibleGeometries` field. For `slow_push_forward`, verify against OBJ-027.

4. **Schema Field Cross-Check:** For every field documented in `manifest-schema-reference.md`, verify that the documented type, default, and constraints match OBJ-004's Zod schemas.

5. **Easing Name Cross-Check:** Verify the 6 documented easing names match OBJ-004's `CameraParamsSchema` enum exactly.

6. **Transition Name Cross-Check:** Verify the 3 documented transition types match OBJ-004's `TransitionSchema` enum exactly.

### Self-Sufficiency Tests (SC-04 / TC-04)

7. **Blind Authoring Test:** Provide an LLM with only `SKILL.md` + geometry and camera reference sub-files. Ask it to produce manifests for 5 diverse topics (per SC-02: deep sea creatures, space exploration, ancient Rome, cooking basics, jazz history). Validate each manifest via `loadManifest()`. All 5 must pass validation.

8. **Minimal Knowledge Test:** Provide an LLM with only `SKILL.md` (no sub-files). Ask it to produce a single-scene manifest. It must pass validation, demonstrating the primary file alone is sufficient for basic usage.

### Relevant Testable Claims

- **TC-04:** Tests 7 and 8 directly verify that an LLM can produce valid manifests using only geometry names and slot keys, without specifying XYZ coordinates.
- **TC-07:** Tests 1 and 2 indirectly verify that SKILL.md-guided manifests don't produce validation errors for correct usage.
- **TC-08:** Test 7 verifies that the documented geometries cover diverse topics.
- **SC-02:** Test 7 maps directly to SC-02's 5-topic blind authoring test.
- **SC-04:** Tests 7 and 8 directly verify SC-04.

## Integration Points

### Depends On

| Dependency | What OBJ-070 Uses |
|---|---|
| **OBJ-004** (Manifest Schema) | Zod schema field names, types, defaults, constraints, error codes. The entire `manifest-schema-reference.md` is derived from OBJ-004. Manifest examples must conform to OBJ-004's schema. |
| **OBJ-046** (CLI Interface) | Command names (`render`, `validate`, `preview`), flag names (`--output`, `--width`, `--height`, `--fps`, `--gpu`, `--verbose`), usage syntax. CLI section of SKILL.md documents these. |
| **OBJ-018** (Stage Geometry) | Slot names, required/optional flags, descriptions, compatible cameras, default camera, fog settings. The stage section in `geometry-reference.md` and the primary examples in `SKILL.md` are derived from OBJ-018. |
| **OBJ-027** (Push/Pull Cameras) | Preset names, motion descriptions, compatible geometries, default easing, parameter effects. The push/pull sections in `camera-reference.md` and the primary examples in `SKILL.md` use OBJ-027 data. |

### Consumed By

| Downstream | How It Uses OBJ-070 |
|---|---|
| **OBJ-071** (SKILL.md full content — all geometries and cameras) | OBJ-071 fills in the stub sections created by OBJ-070, adding full geometry and camera detail as those objectives are verified. OBJ-070 establishes the document structure and content patterns that OBJ-071 follows. |
| **OBJ-072** (Prompt template refinement) | Extends/refines `prompt-templates.md` with empirically tested prompt patterns. |
| **OBJ-075** (n8n HTTP Interface) | May reference SKILL.md for manifest generation guidance when the n8n workflow calls Claude API to generate manifests. |
| **OBJ-056** (SKILL.md completeness for production) | Validates that the complete SKILL.md (after OBJ-071) meets SC-04 self-sufficiency. |
| **SC-02** (Blind Authoring Validation) | Uses SKILL.md as the sole reference for the 5-topic blind authoring test. |

### File Placement

```
depthkit/
  SKILL.md                              # Primary entry point (repo root)
  docs/
    skill/
      geometry-reference.md             # Geometry details
      camera-reference.md               # Camera preset details
      prompt-templates.md               # Image prompt templates
      manifest-schema-reference.md      # Full schema reference
      patterns.md                       # Multi-scene video patterns
```

## Open Questions

### OQ-A: Should SKILL.md Document HUD Layers?

HUD layers (seed Section 2) are defined in the vocabulary but not yet implemented. SKILL.md could mention them as "planned — not yet available in V1" to set expectations, or omit them entirely to avoid confusion. **Recommendation:** Include a brief "Not Yet Available" section listing HUD layers and per-frame opacity animation as planned features. This prevents the LLM from trying to use them and wondering why they don't work.

### OQ-B: Should the Patterns Sub-File Include Complete Manifest JSON?

Each pattern could include a full JSON manifest example, or just a structured description. Full JSON adds ~50-100 lines per pattern but provides copy-paste templates. **Recommendation:** Include at least one full JSON manifest in the patterns file (the "Explainer Video" pattern). Other patterns use structured descriptions (geometry + camera per scene) without full JSON.

### OQ-C: Should Geometry-Reference Sections Include Spatial Diagrams?

ASCII art diagrams showing plane arrangement (top-down view, side view) could help LLMs understand spatial relationships. However, LLMs may not interpret ASCII art reliably. **Recommendation:** Use plain-English spatial descriptions ("the floor extends from the camera toward the backdrop, creating a receding ground surface") rather than ASCII diagrams. Test during SC-02 validation whether this is sufficient.

### OQ-D: How Should Unverified Geometries/Cameras Be Documented?

OBJ-019 (tunnel), OBJ-020 (canyon), OBJ-021 (flyover) are verified but are not direct dependencies of OBJ-070. Should their content be included in full, or only as stubs? **Recommendation:** Include stub sections with brief descriptions from seed Section 4.2 and slot names from the verified geometry definitions. Full sections are OBJ-071's responsibility. This gives OBJ-070 a complete document structure without requiring content accuracy for objectives it doesn't depend on.

### OQ-E: Context Window Budget

The 2000-line / 60KB combined limit is a guideline based on typical LLM context windows (128K-200K tokens). If the LLM agent loading SKILL.md also needs substantial system prompts and conversation history, the budget may need to be tighter. **Recommendation:** Target the conservative end — primary file under 400 lines, total under 1500 lines. Measure empirically during SC-02 testing.

---

I believe this specification is comprehensive enough for an implementer to produce the full SKILL.md document system. I'd like the Challenger to review and verify — particularly the document structure decisions, the acceptance criteria coverage of SC-04, and whether the integration points with verified vs. unverified dependencies are handled correctly.

---

## Round 2 — spec_challenger

I've read the proposed specification carefully. Here's my assessment.

## Points of Agreement

The overall document architecture (primary file + sub-files in `docs/skill/`) is sound and well-motivated. D1's rationale is solid — a monolithic file would blow context budgets. The two-example approach (D3) is smart. The scene authoring workflow as a numbered checklist (D7) is exactly right for LLM consumers. The anti-patterns selection (D6) correctly filters for author-facing concerns. The cross-consistency acceptance criteria (AC-41 through AC-46) are excellent — vocabulary drift is the #1 risk for this kind of document.

## Issues

### Issue 1: Line count inconsistency — D1 says 400, AC-20 says 500

**Severity:** Minor

D1 states "primary `SKILL.md` should be under 400 lines." AC-20 states "under 500 lines." These disagree. An implementer doesn't know which target to hit.

**Fix:** Pick one. I'd say AC-20 (500 lines) is the binding one since acceptance criteria are what get tested. Update D1 to say "under 500 lines" or tighten AC-20 to 400. Just make them agree.

### Issue 2: Complete annotated example uses non-dependency geometries

**Severity:** Major

AC-10 requires "at least 3 scenes, at least 2 different geometries." OBJ-070's only geometry dependency is OBJ-018 (`stage`). If the example uses `tunnel` (OBJ-019), the implementer must consult OBJ-019's spec to get correct slot names — but OBJ-019 is not a declared dependency. AC-11 then requires the example to pass `loadManifest()` validation, which means the slot names must be exact.

Options:
- (a) Restrict the complete example to use only `stage` geometry across all scenes (disappointing for a "production" example but safe).
- (b) Allow the example to use `tunnel` and add OBJ-019 as a dependency.
- (c) Allow the example to use non-dependency geometries but make the validation test register those geometries correctly. Document that the implementer should consult the verified OBJ-019 spec.

**Fix:** I'd recommend (c) with explicit specification: "The complete example MAY use geometries beyond `stage` (e.g., `tunnel` from verified OBJ-019) provided the implementer consults those verified specs for slot names. The validation test in Test Strategy must register all geometries used in the example." Add a note to AC-11 that the test must register all geometries referenced in the example. This avoids a formal dependency addition while being explicit about what the implementer needs.

### Issue 3: AC-47 and AC-48 are not implementer-testable acceptance criteria

**Severity:** Major

AC-47 says "An LLM reading only `SKILL.md`... can produce a structurally valid single-scene manifest." AC-48 is similar for multi-scene. These are *aspirational goals*, not testable acceptance criteria. An implementer cannot write a deterministic pass/fail test for "an LLM can produce X." LLM outputs are non-deterministic and depend on model, temperature, prompting.

**Fix:** Reframe these as validation goals referenced by SC-04, not as acceptance criteria. Replace them with criteria the implementer CAN verify:

- **AC-47 (revised):** "The quick-start example in SKILL.md, if copied verbatim and modified only by changing image `src` paths, produces a valid manifest."
- **AC-48 (revised):** "The complete annotated example, if copied verbatim and modified only by changing image `src` paths and scene durations, produces a valid manifest."

The actual LLM blind-authoring test belongs in the Test Strategy under "Self-Sufficiency Tests" as a separate validation step (which it already is as Test 7/8), not as a hard AC.

### Issue 4: OBJ-026 and OBJ-031 content without formal dependency

**Severity:** Major

AC-30 requires "complete sections for `static` (OBJ-026) and `gentle_float` (OBJ-031) with available details." But OBJ-026 and OBJ-031 are NOT in OBJ-070's `depends_on` list. The implementer has no guaranteed access to those specs.

Yet the progress map shows both OBJ-026 and OBJ-031 as verified. The stage geometry (OBJ-018) lists both in its `compatible_cameras`. So the data is available — it's just not a formal dependency.

**Fix:** Either:
- (a) Add OBJ-026 and OBJ-031 to `depends_on` in meta.json, OR
- (b) Downgrade AC-30 from "complete sections" to "stub sections with brief descriptions from seed Section 4.3" — consistent with how unverified cameras are handled.

I lean toward (a) since both are verified and the SKILL.md camera summary table (AC-14) already requires listing them. If we're listing them in the primary file's summary table, the camera reference sub-file should have at minimum their key data. Either way, the spec must be consistent about what depth of coverage is expected for cameras that aren't formal dependencies.

### Issue 5: Stub section content is underspecified

**Severity:** Major

AC-26 says "stub sections for other geometries... clearly marked as 'details pending' with brief descriptions from seed Section 4.2." But what does a stub look like? Does it include:
- Just a heading and "Details pending"?
- The slot names (if the geometry is verified, e.g., OBJ-019 tunnel)?
- A brief "when to use" sentence?
- Compatible cameras?

An implementer will make different choices here, and downstream OBJ-071 needs a predictable structure to fill in.

**Fix:** Define the minimal stub structure explicitly:

```markdown
### `tunnel`
> **Status:** Details pending — see OBJ-019

**Description:** [1-2 sentences from seed Section 4.2]

**Required slots:** [Listed if geometry is verified; "TBD" if not]

**Default camera:** [Listed if geometry is verified; "TBD" if not]
```

This gives OBJ-071 a consistent skeleton to fill.

### Issue 6: No specification of image path conventions for examples

**Severity:** Minor

Both example manifests need `src` values for images and audio. The spec doesn't say what path convention to use. Should they be `"./images/scene1_backdrop.png"`? `"./assets/images/backdrop.png"`? Relative to what?

**Fix:** Specify a convention: "Example manifests use relative paths in the form `./images/<scene_id>_<slot_name>.png` for images and `./audio/narration.mp3` for audio. These match the default `--assets-dir` resolution behavior documented in OBJ-046 (manifest's parent directory)."

### Issue 7: CLI flags must match OBJ-046 exactly

**Severity:** Minor

AC-18 requires CLI usage with `depthkit render`, `depthkit validate`, `depthkit preview` examples. OBJ-046 uses `-W` (uppercase) for width and `-H` (uppercase) for height, not `-w`/`-h`. The spec doesn't call out these specifics, creating risk of incorrect documentation.

**Fix:** Add to AC-18 or as a separate AC: "CLI flag names and short aliases in SKILL.md match OBJ-046 exactly (e.g., `-W` for width, `-H` for height, `-o` for output)."

### Issue 8: Test Strategy conflates implementer tests with system validation tests

**Severity:** Minor

Tests 7 and 8 ("Blind Authoring Test", "Minimal Knowledge Test") require running LLM experiments. These are SC-04 validation activities, not tests the OBJ-070 implementer runs as part of their deliverable. Tests 1-6 (correctness checks) are what the implementer actually executes.

**Fix:** Split the test strategy into:
- **Implementer Tests** (1-6): Things the implementer runs before marking the objective complete.
- **Validation Tests** (7-8): System-level validation run as part of SC-02/SC-04, not the implementer's responsibility.

### Issue 9: No AC verifies that documented fog/spatial values match OBJ-018

**Severity:** Minor

AC-22 says "fog description" but doesn't require the documented fog values to match OBJ-018's `{ color: '#000000', near: 20, far: 60 }`. The geometry reference could say "subtle fog" without giving the actual values, and AC-22 would pass. Similarly, no AC checks that the documented compatible cameras list is complete and accurate against OBJ-018's definition.

**Fix:** AC-25 already covers compatible cameras. Strengthen AC-22 to: "Contains a complete section for `stage` geometry with all 6 slots... fog settings matching OBJ-018's definition (`color: '#000000'`, `near: 20`, `far: 60`)..."

---

## Summary

**Critical issues:** 0
**Major issues:** 4 (Issues 2, 3, 4, 5)
**Minor issues:** 5 (Issues 1, 6, 7, 8, 9)

The spec is solid overall. The four major issues all have clear fixes. Please address them and I'll verify in the next round.

---

## Round 3 — spec_author

# Revised Specification: OBJ-070 — SKILL.md Structure and Core Content

I've addressed all 9 issues. Here's the revised spec with changes marked.

## Summary

OBJ-070 defines the SKILL.md document architecture and core content — the single authoritative reference that enables an LLM agent (with no visual perception) to produce valid depthkit manifests for arbitrary video topics. The document uses a modular structure: a primary `SKILL.md` file covering manifest authoring with a complete annotated example (using the `stage` geometry and `slow_push_forward` camera), plus sub-files for geometry reference, camera reference, and prompt templates. Per SC-04, an LLM reading only SKILL.md (and its sub-files) must be able to produce a valid manifest without access to engine source code. Per seed Section 4.9, the document must fit within a single LLM context window (primary file + loaded sub-files).

## Interface Contract

### Document Architecture

SKILL.md is not code — it's a structured Markdown document system. The "interface" is the file layout and the information contracts each file fulfills.

```
depthkit/
  SKILL.md                              # Primary entry point — manifest authoring guide
  docs/
    skill/
      geometry-reference.md             # All scene geometries: slots, descriptions, usage guidance
      camera-reference.md               # All camera path presets: motion descriptions, compatible geometries
      prompt-templates.md               # Image generation prompt templates per slot type
      manifest-schema-reference.md      # Complete schema field reference (types, defaults, constraints)
      patterns.md                       # Common multi-scene video patterns (explainer, social clip, etc.)
```

### Primary File: `SKILL.md`

The primary file is the entry point an LLM reads first. It must be **self-contained enough** that an LLM can produce a valid manifest reading only this file, but it references sub-files for extended detail. The primary file contains:

1. **Purpose Statement** — What depthkit is, what SKILL.md teaches, the blind-authoring constraint.
2. **Quick Start** — Minimal viable manifest (single-scene example using `stage` + `slow_push_forward`) with inline annotations explaining every field.
3. **Manifest Structure Overview** — Top-level shape (`version`, `composition`, `scenes`), field summary with types and defaults.
4. **Scene Authoring Workflow** — Step-by-step: choose geometry → choose camera → assign images to slots → set timing → set transitions.
5. **Geometry Summary Table** — One-row-per-geometry table with name, description, required slots, optional slots, default camera, and `when to use` guidance. Full details in `geometry-reference.md`.
6. **Camera Summary Table** — One-row-per-camera table with name, description, compatible geometries, motion type, and `when to use` guidance. Full details in `camera-reference.md`.
7. **Transitions Reference** — Inline (not a sub-file). The three transition types, duration guidance, adjacency rules.
8. **Easing Reference** — Inline. The six easing names, plain-English descriptions of their feel.
9. **Audio Synchronization** — How `start_time` and `duration` relate to audio, how to distribute scenes across audio duration.
10. **Anti-Patterns** — Critical mistakes to avoid (text in parallax layers, raw coordinates instead of presets, missing required slots, incompatible camera-geometry pairs).
11. **CLI Usage** — Brief section with `depthkit render`, `depthkit validate`, `depthkit preview` example invocations, matching OBJ-046 flag names exactly.
12. **Sub-File Pointers** — Explicit references with loading guidance for LLM agents.
13. **Complete Annotated Example** — A full, production-quality manifest (5 scenes, multiple geometries, transitions, audio) with line-by-line annotations.

**Size target:** The primary `SKILL.md` should be under 500 lines of Markdown (approximately 15-18KB). Sub-files add detail for when the LLM needs deeper reference. The combined total (primary + all sub-files) should stay under 2000 lines (~60KB) to fit comfortably within a single context window alongside a system prompt and conversation history.

**Image path convention:** Example manifests use relative paths in the form `./images/<scene_id>_<slot_name>.png` for images and `./audio/narration.mp3` for audio. These match the default `--assets-dir` resolution behavior documented in OBJ-046 (manifest's parent directory).

### Sub-File: `docs/skill/geometry-reference.md`

One section per registered geometry. **Full sections** are provided for geometries whose objectives are formal dependencies or are verified and needed for example accuracy. **Stub sections** are provided for all other geometries.

#### Full Section Structure (for `stage` and any other verified geometry used in examples)

```markdown
### `stage`

**Description:** [From geometry's `description` field]

**When to use:** [Authoring guidance — what kinds of scenes/topics suit this geometry]

**Required slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `backdrop` | Primary background — landscape, environment, or atmospheric backdrop. | Full-scene wide image. No foreground elements. No transparency needed. |
| `floor` | Ground surface with perspective foreshortening. | Top-down or tileable ground texture. No transparency needed. |
| `subject` | Primary focal element. | Isolated subject on transparent background. |

**Optional slots:**
| Slot | Description | Image guidance |
|------|-------------|----------------|
| `sky` | Distant sky/gradient behind backdrop. | Wide atmospheric image. No transparency needed. |
| `midground` | Middle-distance environmental element. | Environmental prop or terrain. No transparency needed. |
| `near_fg` | Foreground framing element. | Particles, foliage, bokeh on transparent background. |

**Default camera:** `slow_push_forward`

**Compatible cameras:** `static`, `slow_push_forward`, `slow_pull_back`, `lateral_track_left`, `lateral_track_right`, `gentle_float`, `dramatic_push`, `crane_up`

**Fog:** Black fog (`#000000`, near: 20, far: 60). Fades distant elements. Sky and near_fg are fog-immune.

**Transparency:** `subject` and `near_fg` require transparent background images. All other slots use opaque images.

**Tips:**
- The floor plane is what makes this geometry feel 3D — always provide a floor image.
- Subject images MUST have transparent backgrounds to avoid rectangular edges.
- [Additional authoring tips]
```

#### Stub Section Structure (for geometries not yet fully documented)

```markdown
### `tunnel`
> **Status:** Details pending — full documentation will be added when visual tuning is complete.

**Description:** Floor, ceiling, left wall, right wall receding to a vanishing point. Camera pushes forward through an enclosed corridor. Produces dramatic perspective convergence.

**Required slots:** `floor`, `left_wall`, `right_wall`, `end_wall`

**Optional slots:** `ceiling`

**Default camera:** `tunnel_push_forward`

**Compatible cameras:** [See `camera-reference.md` for compatibility details]
```

The stub structure must include: heading, status note, 1-2 sentence description (from seed Section 4.2 or verified geometry spec), required slot names (if geometry is verified — listed; if not verified — "TBD"), optional slot names (same rule), and default camera (same rule). This gives OBJ-071 a consistent skeleton to fill in.

### Sub-File: `docs/skill/camera-reference.md`

One section per registered camera preset. **Full sections** are provided for presets that are formal dependencies of OBJ-070 (`slow_push_forward`, `slow_pull_back` from OBJ-027) and for `static` (OBJ-026) and `gentle_float` (OBJ-031), which are verified and listed in OBJ-018's `compatible_cameras`. **Stub sections** for all others.

#### Full Section Structure

```markdown
### `slow_push_forward`

**Motion:** Camera moves forward along the Z axis into the scene.

**Feel:** Cinematic dolly push. Gentle acceleration, sustained motion, gentle deceleration. The defining 2.5D motion — planes at different depths shift at different rates, creating natural parallax.

**When to use:** Default for most scenes. Creates depth and immersion. Good for revealing detail, building intensity, or simply adding life to a static composition.

**Compatible geometries:** stage, tunnel, canyon, flyover, diorama, portal, close_up

**Parameters:**
| Param | Default | Effect |
|-------|---------|--------|
| `speed` | `1.0` | Scale of camera displacement. 0.5 = subtle, 1.0 = standard, 1.5 = dramatic. |
| `easing` | `ease_in_out` | Timing curve. `linear` for uniform motion, `ease_in` for slow start. |

**Notes:**
- At speed > 1.5, the camera may pass through foreground elements — this is intentional for near_fg (particles exit the view) but avoid for subject planes.
- Pairs naturally with `ease_in_out` for a dolly feel or `ease_out` for a settling feel.
```

#### Stub Section Structure

```markdown
### `lateral_track_left`
> **Status:** Details pending — full documentation will be added when implemented and tuned.

**Motion:** Camera translates left along the X axis.

**Compatible geometries:** [TBD — see geometry `compatible_cameras` lists]
```

### Sub-File: `docs/skill/prompt-templates.md`

Prompt engineering templates organized by slot type (per seed Section 4.7). Each slot type has purpose, prompt template pattern, at least 3 example prompts, and key rules. Sections for: `backdrop`/`sky`/`back_wall` (backgrounds), `floor` (ground surfaces), `subject` (focal elements with transparency), `near_fg` (foreground with transparency), and `midground` (environmental elements).

### Sub-File: `docs/skill/manifest-schema-reference.md`

Complete field-by-field schema reference extracted from OBJ-004. Organized as a flat reference table. Includes every field path, type, default value, constraints, and error code. This is the "man page" — consulted for specific questions.

### Sub-File: `docs/skill/patterns.md`

Common multi-scene video patterns. At least 3 patterns. Each specifies scene count, geometry + camera per scene, transition recommendations, timing guidance, and audio strategy. At least one pattern includes a complete JSON manifest example.

## Design Decisions

### D1: Modular Document Architecture (Primary + Sub-Files)

**Decision:** A primary `SKILL.md` at the repo root with sub-files in `docs/skill/`.

**Rationale:** Seed Section 4.9 explicitly calls for "a single document (or primary document with modular sub-files)." SC-04 requires it to fit within a single context window. A monolithic file covering all 8 geometries, all camera presets, prompt templates, patterns, and schema reference would exceed 3000+ lines — too large for useful context alongside conversation history. The modular approach lets an LLM load only the sub-files relevant to its current task.

**Alternative rejected:** A single monolithic `SKILL.md`. Exceeds practical context limits when combined with system prompts and conversation.

### D2: Primary File Includes Complete Annotated Example Using `stage` + `slow_push_forward`

**Decision:** The primary `SKILL.md` contains a full annotated manifest example using `stage` geometry with `slow_push_forward` camera as the primary example, since these are the reference implementations (OBJ-018 is "the default, most fundamental geometry"; OBJ-027's `slow_push_forward` is "the defining camera motion for 2.5D projection").

**Rationale:** Per the objective description: "manifest authoring guide with a complete, annotated example using stage geometry and slow_push_forward camera path." An LLM learns best from complete, correct examples.

### D3: Two Examples — Quick Start (Minimal) and Complete (Production-Quality)

**Decision:** The primary file includes TWO manifest examples:
1. A **minimal quick-start example** — single scene, `stage` geometry, `slow_push_forward` camera, 3 required slots only, no transitions, no audio. This is the "hello world" that teaches manifest structure.
2. A **complete annotated example** — 5 scenes, multiple geometries, transitions, audio sync, camera parameter overrides. This demonstrates production usage.

The complete example MAY use geometries beyond `stage` (e.g., `tunnel` from verified OBJ-019, `flyover` from verified OBJ-021) provided the implementer consults those verified objective specs for correct slot names. The validation test (Test Strategy item 1) must register all geometries used in the example. The implementer should reference the verified specs for OBJ-019 through OBJ-021 (all verified per the progress map) to ensure slot name accuracy, even though those are not formal dependencies of OBJ-070.

**Rationale:** A single complex example overwhelms. A single trivial example doesn't teach real usage. Two examples serve different learning stages.

### D4: Geometry and Camera Summaries Inline; Details in Sub-Files

**Decision:** The primary `SKILL.md` includes summary tables for all geometries and cameras (one row per entry — name, description, key slots, when to use). Full slot definitions, spatial details, and authoring tips live in sub-files.

**Rationale:** An LLM authoring a manifest needs to select a geometry and camera quickly. A summary table supports this without forcing the LLM to load and parse full sub-files.

### D5: Prompt Templates as a Separate Sub-File

**Decision:** Image generation prompt templates are in `docs/skill/prompt-templates.md`, not inline in `SKILL.md`.

**Rationale:** Per AP-04, the rendering engine is separate from asset generation. SKILL.md focuses on manifest authoring. Prompt templates serve the image generation pipeline stage. Separating them keeps the primary file focused.

### D6: Anti-Patterns Section — Author-Facing Only

**Decision:** The anti-patterns section surfaces the **author-facing** anti-patterns from the seed: AP-03 (no manual coordinates), AP-07 (no text in parallax layers), AP-08 context (position_override is an escape hatch), plus manifest-specific anti-patterns.

**Rationale:** Engine-developer anti-patterns (AP-01, AP-02, AP-09/AP-10) don't apply to manifest authors.

### D7: Scene Authoring Workflow as a Numbered Checklist

**Decision:** A step-by-step numbered workflow: (1) Choose geometry, (2) Choose camera (check compatibility), (3) Assign images to slots (consult slot table), (4) Set duration and start_time, (5) Set transitions (check adjacency rules), (6) Repeat for each scene, (7) Set composition globals, (8) Validate with `depthkit validate`.

**Rationale:** LLMs follow structured procedures well. A numbered checklist reduces the likelihood of missing steps.

### D8: Content Is Manually Authored, Not Auto-Generated

**Decision:** SKILL.md content is written by hand (by the implementing agent), not auto-generated from registry data.

**Rationale:** Auto-generated documentation produces technically correct but pedagogically poor results. SKILL.md's purpose is to teach. The content must stay **consistent** with the registered definitions (acceptance criteria verify this), but the prose is authored for clarity.

### D9: Version Field and Forward Compatibility

**Decision:** SKILL.md includes a version indicator at the top (e.g., `Depthkit SKILL Reference — v3.0`) and notes that manifests must specify `"version": "3.0"`.

### D10: Transition Adjacency Rules Documented Inline

**Decision:** Transition rules are inline in the primary file, not a sub-file.

**Rationale:** Transition errors (`CROSSFADE_NO_ADJACENT`) are among the most common manifest authoring mistakes. The rules are compact and belong next to the scene authoring workflow.

### D11: Sub-File Loading Guidance via Explicit Instructions

**Decision:** The primary SKILL.md includes explicit loading instructions for LLM agents:

```markdown
## Sub-File Loading Guide

When authoring a manifest, load these files as needed:
- **Always load:** This file (`SKILL.md`)
- **For geometry selection:** `docs/skill/geometry-reference.md`
- **For camera selection:** `docs/skill/camera-reference.md`  
- **For image generation:** `docs/skill/prompt-templates.md`
- **For schema details:** `docs/skill/manifest-schema-reference.md`
- **For multi-scene patterns:** `docs/skill/patterns.md`
```

### D12: Geometry and Camera Data Sourced from Verified Dependencies and Verified Objectives

**Decision:** The stage geometry section uses data from OBJ-018 (formal dependency, verified). Camera data uses OBJ-027 (formal dependency, verified) for push/pull. Camera data for `static` and `gentle_float` uses OBJ-026 and OBJ-031 respectively — both are verified and listed in OBJ-018's `compatible_cameras` list, but are not formal dependencies. The implementer should consult their verified specs for accurate documentation. Other geometries and cameras use stub sections.

**Rationale:** OBJ-026 and OBJ-031 are both verified per the progress map and are referenced by OBJ-018's `compatible_cameras`. Including them as full camera-reference sections (rather than stubs) provides a more useful camera reference for the most common geometry (`stage`). The implementer can access their verified output specs without a formal dependency chain since the data needed is limited to: name, motion description, compatible geometries, and parameter defaults — all available from their verified specs.

### D13: CLI Flags Match OBJ-046 Exactly

**Decision:** The CLI usage section uses flag names and short aliases exactly as specified in OBJ-046: `-W` (uppercase) for width, `-H` (uppercase) for height, `-o` for output, `-v` for verbose, etc.

**Rationale:** Incorrect flag documentation would cause manifest authors to issue wrong CLI commands. OBJ-046 is a formal dependency, so flag names are fully specified.

### D14: `position_override` and `rotation_override` Documented as Escape Hatches

**Decision:** Documented in schema reference sub-file with prominent warning: "These are escape hatches for edge cases. If you need them for most planes, you've chosen the wrong geometry."

## Acceptance Criteria

### Document Existence and Structure

- [ ] **AC-01:** `SKILL.md` exists at the repository root.
- [ ] **AC-02:** `docs/skill/geometry-reference.md` exists.
- [ ] **AC-03:** `docs/skill/camera-reference.md` exists.
- [ ] **AC-04:** `docs/skill/prompt-templates.md` exists.
- [ ] **AC-05:** `docs/skill/manifest-schema-reference.md` exists.
- [ ] **AC-06:** `docs/skill/patterns.md` exists.

### Primary File Content (SKILL.md)

- [ ] **AC-07:** Contains a purpose statement explaining depthkit's 2.5D parallax video generation and the blind-authoring constraint.
- [ ] **AC-08:** Contains a minimal quick-start manifest example using `stage` geometry and `slow_push_forward` camera with only the 3 required slots (`backdrop`, `floor`, `subject`).
- [ ] **AC-09:** The quick-start example is a valid, complete JSON manifest that passes `loadManifest()` validation when the `stage` geometry and `slow_push_forward` camera are registered. If copied verbatim and modified only by changing image `src` paths, it remains valid.
- [ ] **AC-10:** Contains a complete annotated production example with at least 3 scenes, at least 2 different geometries, transitions, and audio configuration. The example MAY use verified geometries beyond `stage` (e.g., `tunnel` from OBJ-019, `flyover` from OBJ-021); the implementer must consult those verified specs for correct slot names.
- [ ] **AC-11:** The complete annotated example is valid JSON that passes `loadManifest()` validation when all geometries and cameras used in the example are registered. The validation test must register all geometries and cameras referenced.
- [ ] **AC-12:** Contains a scene authoring workflow as a numbered step-by-step checklist covering: geometry selection, camera selection (with compatibility check), slot assignment, timing (duration + start_time), and transitions (with adjacency rules).
- [ ] **AC-13:** Contains a geometry summary table listing all 8 geometries (stage, tunnel, canyon, flyover, diorama, portal, panorama, close_up) with their required slots, default camera, and "when to use" guidance.
- [ ] **AC-14:** Contains a camera summary table listing at minimum `slow_push_forward`, `slow_pull_back`, `static`, and `gentle_float` with their compatible geometries and "when to use" guidance.
- [ ] **AC-15:** Contains inline transition reference documenting `cut`, `crossfade`, and `dip_to_black` with adjacency rules (crossfade requires adjacent scene; dip_to_black and cut work on any scene).
- [ ] **AC-16:** Contains inline easing reference listing all 6 easing names (`linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`) with plain-English descriptions of their feel.
- [ ] **AC-17:** Contains an anti-patterns section that includes: no text in parallax layers (AP-07), no manual coordinates as primary method (AP-03), and `position_override` is an escape hatch not the primary authoring path.
- [ ] **AC-18:** Contains CLI usage section with `depthkit render`, `depthkit validate`, and `depthkit preview` example invocations. CLI flag names and short aliases match OBJ-046 exactly (e.g., `-W` for width, `-H` for height, `-o` for output, `-v` for verbose).
- [ ] **AC-19:** Contains sub-file loading guide with explicit instructions for which sub-files to load for which tasks.
- [ ] **AC-20:** The primary file is under 500 lines of Markdown.
- [ ] **AC-21:** Specifies `"version": "3.0"` as the required manifest version.
- [ ] **AC-22:** Example manifests use relative paths in the form `./images/<scene_id>_<slot_name>.png` for images and `./audio/narration.mp3` for audio.

### Geometry Reference Sub-File

- [ ] **AC-23:** Contains a full section for `stage` geometry with all 6 slots (3 required, 3 optional), descriptions, image guidance per slot, default camera, compatible cameras, fog settings matching OBJ-018's definition (`color: '#000000'`, `near: 20`, `far: 60`), transparency requirements per slot, and authoring tips.
- [ ] **AC-24:** The `stage` section's slot names match OBJ-018 exactly: `sky`, `backdrop`, `floor`, `midground`, `subject`, `near_fg`.
- [ ] **AC-25:** The `stage` section's required slots match OBJ-018: `backdrop`, `floor`, `subject`.
- [ ] **AC-26:** The `stage` section's compatible cameras match OBJ-018's `compatible_cameras` list exactly.
- [ ] **AC-27:** The `stage` section documents which slots require transparent background images (`subject`, `near_fg`) matching OBJ-018's `transparent: true` slots.
- [ ] **AC-28:** Contains stub sections for all other geometries (tunnel, canyon, flyover, diorama, portal, panorama, close_up). Each stub includes: heading, status note ("Details pending"), 1-2 sentence description from seed Section 4.2 or verified geometry spec, required slot names (listed if geometry is verified, "TBD" if not), optional slot names (same rule), and default camera (same rule).

### Camera Reference Sub-File

- [ ] **AC-29:** Contains full sections for `slow_push_forward` and `slow_pull_back` documenting: motion description, feel, when to use, compatible geometries (matching OBJ-027: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `close_up`), parameters (speed default 1.0, easing default `ease_in_out`), and usage notes.
- [ ] **AC-30:** Contains sections for `static` and `gentle_float` with at minimum: motion description, when to use, and compatible geometries. The implementer should consult verified OBJ-026 and OBJ-031 specs for accurate data. These may be full sections or detailed stubs — full sections are preferred if the verified specs provide sufficient data.
- [ ] **AC-31:** Contains stub sections for all other camera presets (lateral_track_left, lateral_track_right, tunnel_push_forward, flyover_glide, dramatic_push, crane_up, dolly_zoom) clearly marked as "details pending." Each stub includes: heading, status note, 1-sentence motion description from seed Section 4.3.
- [ ] **AC-32:** Each full camera section documents the `speed` and `easing` parameters with default values and effect descriptions.

### Prompt Templates Sub-File

- [ ] **AC-33:** Contains prompt template sections for at least: `backdrop`/`sky`/`back_wall` (backgrounds), `floor` (ground surfaces), `subject` (focal elements with transparency), and `near_fg` (foreground with transparency).
- [ ] **AC-34:** Each slot type section includes: purpose, prompt template pattern, at least 3 example prompts, and key rules.
- [ ] **AC-35:** Subject and near_fg sections explicitly instruct to prompt for transparent backgrounds.

### Schema Reference Sub-File

- [ ] **AC-36:** Documents every manifest field from OBJ-004: `version`, `composition` (width, height, fps, audio), `scenes[]` (id, duration, start_time, geometry, camera, camera_params, transition_in, transition_out, planes), `PlaneRef` fields (src, opacity, scale, position_override, rotation_override), `metadata`.
- [ ] **AC-37:** Each field lists: type, default value (if any), constraints (min/max/enum values), and the error code produced when invalid.
- [ ] **AC-38:** Documents camera_params fields: speed (default 1.0, must be > 0), easing (enum of 6 values, default ease_in_out), fov_start/fov_end (10-120, optional).

### Patterns Sub-File

- [ ] **AC-39:** Contains at least 3 multi-scene video patterns (e.g., "Explainer Video", "Social Media Clip", "Ambient/Mood Video").
- [ ] **AC-40:** Each pattern specifies: scene count, geometry + camera per scene, transition recommendations, timing guidance, and audio strategy.
- [ ] **AC-41:** At least one pattern includes a complete JSON manifest example.

### Cross-Consistency

- [ ] **AC-42:** All manifest field names in SKILL.md and sub-files match OBJ-004's schema exactly (e.g., `start_time` not `startTime`, `transition_in` not `transitionIn`, `camera_params` not `cameraParams`).
- [ ] **AC-43:** All geometry names match registered geometry names (e.g., `stage` not `Stage`).
- [ ] **AC-44:** All camera preset names match registered names (e.g., `slow_push_forward` not `slowPushForward`).
- [ ] **AC-45:** All easing names match OBJ-004's enum: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`.
- [ ] **AC-46:** All transition type names match OBJ-004's enum: `cut`, `crossfade`, `dip_to_black`.
- [ ] **AC-47:** The vocabulary used throughout matches seed Section 2 definitions (plane not layer, scene geometry not layout template, etc.).

### Size Budget

- [ ] **AC-48:** The total combined size of `SKILL.md` + all sub-files is under 2000 lines / 60KB.

## Edge Cases and Error Handling

SKILL.md is a documentation artifact, not code. "Edge cases" here are authoring scenarios the document must address to prevent common mistakes.

### Manifest Authoring Edge Cases the Document Must Address

| Scenario | How SKILL.md Handles It |
|----------|------------------------|
| LLM uses `crossfade` as `transition_in` on the first scene | Transition rules section explicitly states: "crossfade requires an adjacent scene to blend with. Use `dip_to_black` for the first scene's entry and last scene's exit." |
| LLM provides plane slot keys that don't match the geometry | Scene authoring workflow step 3 says: "Consult the geometry's slot table. Use only the listed slot names." Quick-start example demonstrates correct slot keys. |
| LLM specifies an incompatible camera for a geometry | Scene authoring workflow step 2 says: "Check the camera's compatible geometries list, or the geometry's compatible cameras list." Summary tables show compatibility. |
| LLM puts text on a parallax plane | Anti-patterns section explicitly warns: "Never place text content on scene planes. Text should be a HUD layer (not yet supported in V1) or composited as a post-processing step." |
| LLM uses raw XYZ coordinates instead of geometry presets | Anti-patterns section warns against this. `position_override` is documented in schema reference with "escape hatch" warning. |
| LLM generates images without transparency for subject/near_fg slots | Prompt templates sub-file explicitly instructs on transparency. Geometry reference marks which slots expect transparent images. |
| LLM omits `start_time` | Schema reference documents `start_time` as required (nonnegative number). Quick-start example shows it. |
| LLM provides scenes out of time order | The document notes: "Scenes should be ordered by `start_time` in the array. Out-of-order scenes produce a `SCENE_ORDER_MISMATCH` warning but are still valid — the engine sorts by `start_time` internally." |
| LLM needs 9:16 (portrait) video | Composition section shows both `{width: 1920, height: 1080}` (landscape) and `{width: 1080, height: 1920}` (portrait). Notes that all geometries with `preferred_aspect: 'both'` work in either orientation. |
| Overlapping scene timings | Transition section explains overlap rules: "When two scenes overlap in time, both must have compatible transitions (crossfade or dip_to_black) with durations >= the overlap." |
| Audio duration doesn't match scene total | Audio section notes: "If audio duration differs from the sum of scene durations, the engine renders the scene durations as specified and emits a warning. Adjust scene durations to match audio length." |

### Document Maintenance Edge Cases

| Scenario | Handling |
|----------|----------|
| New geometry added (e.g., OBJ-022 `portal`) | Replace the stub section in `geometry-reference.md` with a full section, update the summary table in `SKILL.md`, update patterns if applicable. |
| New camera preset added | Same pattern: replace stub in `camera-reference.md`, update summary table. |
| Schema field added/changed | Update `manifest-schema-reference.md`. If it affects authoring workflow, update `SKILL.md` primary file. |
| Camera compatibility list changes after visual tuning (OBJ-059, OBJ-069) | Update both `geometry-reference.md` (geometry's compatible cameras) and `camera-reference.md` (camera's compatible geometries). Cross-check. |

## Test Strategy

### Implementer Tests (run before marking objective complete)

These are deterministic checks the implementer can execute.

**1. Quick-Start Example Validation:** Extract the quick-start example JSON from `SKILL.md`, parse it, register the `stage` geometry and `slow_push_forward` camera, and run it through `loadManifest()`. It must return `success: true` with zero errors.

**2. Complete Example Validation:** Extract the complete annotated example JSON from `SKILL.md`, register all geometries and cameras referenced in the example (consulting verified specs for slot names), and run it through `loadManifest()`. It must return `success: true` with zero errors.

**3. Slot Name Cross-Check:** For the `stage` geometry documented in `geometry-reference.md`, verify that the documented slot names (required and optional) match OBJ-018's definition exactly: `sky`, `backdrop`, `floor`, `midground`, `subject`, `near_fg`, with required flags matching.

**4. Camera Compatibility Cross-Check:** For `slow_push_forward` and `slow_pull_back` documented in `camera-reference.md`, verify that the documented compatible geometries match OBJ-027's `compatibleGeometries` field exactly.

**5. Schema Field Cross-Check:** For every field documented in `manifest-schema-reference.md`, verify the documented type, default, and constraints match OBJ-004's Zod schemas. Spot-check at minimum: `version` (literal "3.0"), `composition.fps` (int, 1-120), `scenes[].duration` (positive number), `camera_params.easing` (enum of 6 values), `PlaneRef.opacity` (0-1, default 1.0).

**6. Vocabulary Cross-Check:** Search all SKILL.md files for vocabulary violations: "layer" (should be "plane"), "layout template" (should be "scene geometry"), "z-level" (should be "depth slot" or slot name).

**7. CLI Flag Cross-Check:** Verify that every CLI flag mentioned in SKILL.md matches OBJ-046's specification: `-W` (not `-w`), `-H` (not `-h`), `-o`, `-v`, `--gpu`, `--preset`, `--crf`, etc.

### System Validation Tests (SC-04 / SC-02 — not the implementer's responsibility)

These are run as part of the broader success criteria validation, not as part of OBJ-070's deliverable.

**8. Blind Authoring Test (SC-02):** Provide an LLM with only `SKILL.md` + geometry and camera reference sub-files. Ask it to produce manifests for 5 diverse topics (deep sea creatures, space exploration, ancient Rome, cooking basics, jazz history). Validate each via `loadManifest()`. All 5 must pass.

**9. Minimal Knowledge Test (SC-04):** Provide an LLM with only `SKILL.md` (no sub-files). Ask it to produce a single-scene manifest. It must pass validation.

### Relevant Testable Claims

- **TC-04:** Tests 1, 2, 8 verify that an LLM can produce valid manifests using only geometry names and slot keys, without specifying XYZ coordinates.
- **TC-07:** Tests 1 and 2 verify that SKILL.md-guided manifests don't produce validation errors.
- **TC-08:** Test 8 verifies the documented geometries cover diverse topics.
- **SC-02:** Test 8 maps directly to SC-02's 5-topic blind authoring test.
- **SC-04:** Tests 8 and 9 verify SC-04.

## Integration Points

### Depends On

| Dependency | What OBJ-070 Uses |
|---|---|
| **OBJ-004** (Manifest Schema) | Zod schema field names, types, defaults, constraints, error codes. The entire `manifest-schema-reference.md` is derived from OBJ-004. Manifest examples must conform to OBJ-004's schema. |
| **OBJ-046** (CLI Interface) | Command names (`render`, `validate`, `preview`), flag names and short aliases (`-W`, `-H`, `-o`, `-v`, `--gpu`, `--preset`, `--crf`, `--ffmpeg-path`, `--chromium-path`), usage syntax. |
| **OBJ-018** (Stage Geometry) | Slot names, required/optional flags, descriptions, compatible cameras, default camera, fog settings, transparency flags. The stage section in `geometry-reference.md` and the primary examples are derived from OBJ-018. |
| **OBJ-027** (Push/Pull Cameras) | Preset names, motion descriptions, compatible geometries, default easing, parameter effects, speed behavior. The push/pull sections in `camera-reference.md` and the primary examples use OBJ-027 data. |

**Non-dependency verified objectives consulted for content accuracy:**
- **OBJ-026** (Static Camera) — verified, for `static` camera section in camera-reference.md.
- **OBJ-031** (Gentle Float Camera) — verified, for `gentle_float` camera section in camera-reference.md.
- **OBJ-019** (Tunnel Geometry) — verified, for tunnel stub section and optionally the complete example.
- **OBJ-020** (Canyon Geometry) — verified, for canyon stub section.
- **OBJ-021** (Flyover Geometry) — verified, for flyover stub section.

These are not formal dependencies because OBJ-070 only requires stub-level information from them (slot names, descriptions). The implementer should consult their verified output specs for accuracy.

### Consumed By

| Downstream | How It Uses OBJ-070 |
|---|---|
| **OBJ-071** (SKILL.md full content — all geometries and cameras) | OBJ-071 fills in the stub sections created by OBJ-070, adding full geometry and camera detail as those objectives are verified. OBJ-070 establishes the document structure and content patterns that OBJ-071 follows. |
| **OBJ-072** (Prompt template refinement) | Extends/refines `prompt-templates.md` with empirically tested prompt patterns. |
| **OBJ-075** (n8n HTTP Interface) | May reference SKILL.md for manifest generation guidance when the n8n workflow calls Claude API to generate manifests. |
| **OBJ-056** (SKILL.md completeness for production) | Validates that the complete SKILL.md (after OBJ-071) meets SC-04 self-sufficiency. |
| **SC-02** (Blind Authoring Validation) | Uses SKILL.md as the sole reference for the 5-topic blind authoring test. |

### File Placement

```
depthkit/
  SKILL.md                              # Primary entry point (repo root)
  docs/
    skill/
      geometry-reference.md             # Geometry details (full + stubs)
      camera-reference.md               # Camera preset details (full + stubs)
      prompt-templates.md               # Image prompt templates by slot type
      manifest-schema-reference.md      # Full schema reference
      patterns.md                       # Multi-scene video patterns
```

## Open Questions

### OQ-A: Should SKILL.md Document HUD Layers?

HUD layers (seed Section 2) are defined in the vocabulary but not yet implemented. **Recommendation:** Include a brief "Not Yet Available in V1" section listing HUD layers, per-frame opacity animation, and camera path composition as planned features. This prevents the LLM from trying to use them.

### OQ-B: Should the Patterns Sub-File Include Complete Manifest JSON?

**Decision (resolved):** Yes — AC-41 requires at least one pattern to include a complete JSON manifest example. Other patterns use structured descriptions without full JSON to save space.

### OQ-C: Should Geometry-Reference Sections Include Spatial Diagrams?

ASCII art diagrams showing plane arrangement could help, but LLMs may not interpret ASCII art reliably. **Recommendation:** Use plain-English spatial descriptions rather than ASCII diagrams. Test during SC-02 validation whether this is sufficient.

### OQ-D: How Should Unverified Geometries/Cameras Be Documented?

**Decision (resolved):** Stub sections with a defined minimal structure (see "Stub Section Structure" in the interface contract). Stubs include: heading, status note, description, slot names (if verified), default camera. OBJ-071 replaces stubs with full content.

### OQ-E: Context Window Budget

The 2000-line / 60KB combined limit is a guideline. **Recommendation:** Target the conservative end — primary file under 500 lines, total under 1500 lines. Measure empirically during SC-02 testing.

---

## Changes from Round 1

**Issue 1 (line count):** Unified to 500 lines throughout. D1 updated to match AC-20.

**Issue 2 (non-dependency geometries in example):** D3 revised — explicitly states the complete example MAY use verified geometries beyond `stage`, with the implementer consulting those verified specs. AC-10 and AC-11 updated to document this allowance and require the validation test to register all referenced geometries.

**Issue 3 (untestable ACs):** Former AC-47/AC-48 ("an LLM can produce...") removed as acceptance criteria. Replaced with AC-09 (quick-start is valid if copied verbatim with src changes) and AC-11 (complete example passes validation with correct registrations). The LLM blind-authoring tests remain in Test Strategy as system validation tests (8, 9), clearly labeled as not the implementer's responsibility.

**Issue 4 (OBJ-026/OBJ-031 without formal dependency):** D12 revised. AC-30 now says "sections with at minimum: motion description, when to use, and compatible geometries" and notes the implementer should consult verified OBJ-026 and OBJ-031 specs. "Full sections are preferred if the verified specs provide sufficient data" — gives implementer discretion without requiring a formal dependency.

**Issue 5 (stub structure underspecified):** Added explicit "Stub Section Structure" definitions for both geometries and cameras in the Interface Contract section, with example Markdown. AC-28 revised to reference the defined stub structure.

**Issue 6 (image path conventions):** Added to Interface Contract under Primary File section and as AC-22.

**Issue 7 (CLI flag accuracy):** AC-18 now explicitly requires flag names and short aliases to match OBJ-046. D13 added. Test Strategy item 7 added as a CLI flag cross-check.

**Issue 8 (test strategy conflation):** Test Strategy split into "Implementer Tests" (1-7, deterministic, run by implementer) and "System Validation Tests" (8-9, SC-02/SC-04, not implementer's responsibility).

**Issue 9 (fog values not verified):** AC-23 (formerly AC-22) now explicitly requires fog settings matching OBJ-018's definition: `color: '#000000'`, `near: 20`, `far: 60`.

---

I believe all 9 issues have been addressed. I'd like the Challenger to verify these changes and approve.

---

## Round 4 — spec_challenger

I've verified all 9 issues from Round 2 against the revised spec. Let me confirm each fix:

1. **Line count:** ✅ D1 and AC-20 both say 500 lines.
2. **Non-dependency geometries:** ✅ D3 explicitly allows with consulting verified specs. AC-10/11 updated.
3. **Untestable ACs:** ✅ Old AC-47/48 replaced with deterministic AC-09/AC-11. LLM tests moved to system validation.
4. **OBJ-026/OBJ-031:** ✅ D12 revised, AC-30 gives discretion, non-dependencies listed explicitly.
5. **Stub structure:** ✅ Defined with example Markdown for both geometries and cameras.
6. **Image paths:** ✅ Convention in Interface Contract + AC-22.
7. **CLI flags:** ✅ AC-18 explicit, D13 added, Test 7 added.
8. **Test conflation:** ✅ Split into Implementer Tests (1-7) and System Validation Tests (8-9).
9. **Fog values:** ✅ AC-23 requires exact OBJ-018 fog values.

No new issues introduced by the revisions. The spec is clean, implementable, and stays within scope.

CONCLUSION:

The specification for OBJ-070 defines the SKILL.md document architecture — a primary file at the repo root plus 5 sub-files in `docs/skill/` — that enables blind manifest authoring by LLM agents. Core content covers the `stage` geometry and `slow_push_forward`/`slow_pull_back` cameras with two worked examples (minimal quick-start and production multi-scene). Stub structures are defined for unverified geometries/cameras. 48 acceptance criteria cover document structure, content accuracy against verified dependency specs (OBJ-004, OBJ-018, OBJ-027, OBJ-046), cross-consistency, and size budget. The test strategy separates implementer-runnable tests (7 deterministic checks) from system validation tests (SC-02/SC-04 LLM experiments).

Let me write the files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Write,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me check the current state of the node directory and meta.json.
[Tool: Bash]
  Input: {
  "command": "ls -la nodes/OBJ-070/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check OBJ-070 node directory"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-070",
     3→  "description": "SKILL.md structure and core content -- manifest authoring guide with a complete, annotated example using stage geometry and slow_push_forward camera path. Document architecture (primary file with modular sub-files for geometry reference, camera reference, prompt templates). Per SC-04 (SKILL.md is self-sufficient for an LLM to produce valid manifests). Per Section 4.9.",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-004", "OBJ-046", "OBJ-018", "OBJ-027"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 integration. High priority. Depends on stage geometry + push/pull cameras for the core annotated example."
    12→}
    13→
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:29 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   797 Mar 22 19:29 meta.json
Good. Now let me write the final specification and update meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/output.md",
  "content": "# Specification: OBJ-070 \u2014 SKILL.md Structure and Core Content\n\n## Summary\n\nOBJ-070 defines the SKILL.md document architecture and core content \u2014 the single authoritative reference that enables an LLM agent (with no visual perception) to produce valid depthkit manifests for arbitrary video topics. The document uses a modular structure: a primary `SKILL.md` file covering manifest authoring with a complete annotated example (using the `stage` geometry and `slow_push_forward` camera), plus sub-files for geometry reference, camera reference, and prompt templates. Per SC-04, an LLM reading only SKILL.md (and its sub-files) must be able to produce a valid manifest without access to engine source code. Per seed Section 4.9, the document must fit within a single LLM context window (primary file + loaded sub-files).\n\n## Interface Contract\n\n### Document Architecture\n\nSKILL.md is not code \u2014 it's a structured Markdown document system. The \"interface\" is the file layout and the information contracts each file fulfills.\n\n```\ndepthkit/\n  SKILL.md                              # Primary entry point \u2014 manifest authoring guide\n  docs/\n    skill/\n      geometry-reference.md             # All scene geometries: slots, descriptions, usage guidance\n      camera-reference.md               # All camera path presets: motion descriptions, compatible geometries\n      prompt-templates.md               # Image generation prompt templates per slot type\n      manifest-schema-reference.md      # Complete schema field reference (types, defaults, constraints)\n      patterns.md                       # Common multi-scene video patterns (explainer, social clip, etc.)\n```\n\n### Primary File: `SKILL.md`\n\nThe primary file is the entry point an LLM reads first. It must be **self-contained enough** that an LLM can produce a valid manifest
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/meta.json",
  "content": "{\n  \"id\": \"OBJ-070\",\n  \"description\": \"SKILL.md structure and core content -- manifest authoring guide with a complete, annotated example using stage geometry and slow_push_forward camera path. Document architecture (primary file with modular sub-files for geometry reference, camera reference, prompt templates). Per SC-04 (SKILL.md is self-sufficient for an LLM to produce valid manifests). Per Section 4.9.\",\n  \"category\": \"integration\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:00:00Z\",\n  \"depends_on\": [\"OBJ-004\", \"OBJ-046\", \"OBJ-018\", \"OBJ-027\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 5 integration. High priority. Depends on stage geometry + push/pull cameras for the core annotated example. Spec complete after 4-round deliberation.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-070/meta.json has been updated successfully.

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-070/output.md nodes/OBJ-070/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-070): SKILL.md structure and core content\n\nDefines the document architecture for depthkit's SKILL.md \u2014 the\nauthoritative reference enabling blind manifest authoring by LLM agents.\n\nArchitecture: primary SKILL.md at repo root + 5 sub-files in docs/skill/\n(geometry-reference, camera-reference, prompt-templates, schema-reference,\npatterns). 48 acceptance criteria covering structure, content accuracy\nagainst OBJ-004/OBJ-018/OBJ-027/OBJ-046, cross-consistency, and size\nbudget. Two worked examples (minimal quick-start, production multi-scene).\nStub structure defined for unverified geometries/cameras (OBJ-071 fills).\n\nDeliberation: 4 rounds. 9 issues raised and resolved (line count\nconsistency, non-dependency geometry usage in examples, testable vs\naspirational ACs, OBJ-026/031 coverage depth, stub structure definition,\nimage path conventions, CLI flag accuracy, test strategy separation,\nfog value verification).\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-070 spec and meta.json"
}
[Tool Result] [master c16726a] spec(OBJ-070): SKILL.md structure and core content
 2 files changed, 458 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-070/output.md
The specification for OBJ-070 has been written to disk and committed. 

**Deliberation summary:** 4 rounds, 9 issues raised in Round 2 (0 critical, 4 major, 5 minor), all resolved in Round 3 and verified in Round 4. The spec defines a modular SKILL.md document system with 48 testable acceptance criteria, clear stub structures for forward compatibility, and a clean separation between implementer tests and system validation tests.
