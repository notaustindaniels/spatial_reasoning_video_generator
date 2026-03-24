# Specification: OBJ-075 — Blind Authoring Test Plan

## Summary

OBJ-075 defines the **test plan** — procedures, topic lists, scoring rubrics, and pass/fail criteria — for validating four core claims about depthkit's blind-authoring capability: TC-08 (8 geometries cover the design space), TC-04 (geometries eliminate manual 3D positioning), TC-01 (3–5 planes per geometry handle 90% of common scenes), and SC-02 (an LLM authors 5 manifests for 5 topics using only SKILL.md, and at least 4 out of 5 look correct when rendered). The deliverable is a structured test plan document plus reusable evaluation artifacts (topic lists, scene types, scoring rubrics, prompt templates) — not implementation code. The plan is designed to be executed by a human operator assisted by an LLM, using `depthkit validate` (OBJ-046) for automated manifest validation and `depthkit render` for visual review renders.

## Interface Contract

OBJ-075 produces documentation artifacts, not code modules. The "interface" is the test plan structure itself — its procedures, inputs, outputs, and evaluation criteria.

### Deliverable: `nodes/OBJ-075/output.md`

The specification document (this document), containing the complete test plan.

### Deliverable: `test/plans/blind-authoring/`

A directory containing reusable test plan artifacts:

```
test/plans/blind-authoring/
  README.md                    # Test plan overview, prerequisites, execution instructions
  topics-25.md                 # The 25 topics for TC-08 geometry mapping test
  scene-types-15.md            # The 15 scene types for TC-01 plane sufficiency test
  scoring-rubric.md            # Scoring rubric for human visual review (SC-02)
  tc08-geometry-mapping.md     # Procedure for TC-08 (25-topic geometry mapping)
  tc04-manifest-validation.md  # Procedure for TC-04 (10 LLM-authored manifests)
  tc01-plane-sufficiency.md    # Procedure for TC-01 (15 scene types, 3-5 planes)
  sc02-blind-authoring.md      # Procedure for SC-02 (5 topics, 5 manifests, human review)
  results/                     # Directory for storing test run results (gitignored)
    .gitkeep
```

### Results File Format

Each test run produces a results file named `{procedure}-{date}.md` (e.g., `tc08-2026-03-25.md`) in the `results/` directory. Each results file records:

- **Test executor identity** (human name or agent ID)
- **Date** of execution
- **LLM model used** (for TC-04 and SC-02; exact model version, e.g., "Claude 3.5 Sonnet 2025-01-01")
- **Geometry availability** at time of execution (which geometries were registered)
- **Camera availability** at time of execution (which cameras were registered)
- **Per-item results** using the procedure's results template
- **Overall pass/fail determination** with summary rationale

### Test Execution Dependencies

The test plan requires the following to be available at execution time:

| Requirement | Source | Notes |
|---|---|---|
| `depthkit validate` CLI command | OBJ-046 | For automated manifest validation |
| `depthkit render` CLI command | OBJ-046 | For rendering test videos for visual review |
| SKILL.md + sub-files | OBJ-070 | The sole reference material provided to the LLM during blind authoring tests |
| At least `stage` geometry registered | OBJ-018 (verified) | Minimum geometry for tests |
| At least `slow_push_forward` camera registered | OBJ-027 (verified) | Minimum camera for tests |
| Placeholder test images | Provided by test executor | Solid-color PNGs suffice for validation; real images needed for visual review |
| An LLM with no prior depthkit context | Test executor provides | Claude (Sonnet-class or above) or equivalent; must not have seen engine source code. Record exact model version in results. |

## Design Decisions

### D1: Four Separate Test Procedures, One Shared Infrastructure

**Decision:** The plan defines four distinct test procedures (TC-08, TC-04, TC-01, SC-02), each with its own document, but they share common artifacts: the 25-topic list (used by TC-08, partially by SC-02), the 15 scene-type list (used by TC-01), and the scoring rubric (used by SC-02, optionally by TC-01).

**Rationale:** Each testable claim has different pass/fail criteria, different inputs, and different evaluation methods. Combining them into a single monolithic procedure would obscure what's being tested. Shared artifacts avoid duplication.

### D2: Topics Are Pre-Selected, Not Random

**Decision:** The 25 topics for TC-08 and the 5 topics for SC-02 are pre-selected and documented in the plan. TC-08's specification says "25 randomly selected video topics" — we interpret this as "25 diverse topics selected to represent the breadth of real-world video production," not as requiring a random number generator.

**Rationale:** True randomness could produce 25 variations of the same theme. The purpose is to stress-test geometry coverage across diverse domains. Pre-selecting ensures the topic list spans education, entertainment, nature, technology, history, abstract concepts, etc. The topics are documented so the test is repeatable.

### D3: TC-08 Is a Paper Exercise; SC-02 Requires Rendering

**Decision:** TC-08 (geometry mapping) is primarily a table-completion exercise — for each of 25 topics, the evaluator (an LLM or human) identifies which geometry best fits and whether the available geometries can handle the topic. No rendering required. SC-02 requires actual rendering and human visual review.

**Rationale:** TC-08 tests design-space coverage — "can these 8 geometries accommodate these topics?" This is a conceptual question answerable by analysis. SC-02 tests end-to-end quality — "does the rendered video look correct?" This requires actual output.

### D4: TC-04 Uses `depthkit validate` for Pass/Fail; No Rendering Required

**Decision:** TC-04 tests whether an LLM can produce a valid manifest without specifying raw 3D coordinates. The test runs each manifest through `depthkit validate` and checks for zero errors. No rendering is needed — if the manifest passes validation, the geometry definitions handle all 3D positioning.

**Rationale:** The testable claim is about authoring correctness, not visual quality. Manifest validation (OBJ-016 via OBJ-046) enforces that planes match geometry slots and cameras are compatible — which is exactly what TC-04 asserts.

### D5: SC-02 Scoring Uses a 1–5 Rubric with Minimum Threshold

**Decision:** SC-02's human review uses a structured 5-point scoring rubric per manifest. A manifest "looks correct and professional" (per SC-02's criterion) if it scores ≥ 3 on every dimension and ≥ 4 overall. The threshold is 4/5 manifests passing.

**Rationale:** "Looks correct" is subjective. A rubric makes it evaluable. The seed's SC-02 says "at least 4 out of 5 look correct and professional" — so 80% is the pass rate. The 5-point scale gives enough granularity to distinguish "broken" (1–2) from "acceptable" (3) from "good" (4–5).

### D6: Test Plan Accounts for Partially-Available Geometries

**Decision:** The test plan is designed to run with whatever geometries are verified at execution time. TC-08 evaluates all 8 proposed geometries conceptually (whether or not their code is verified). TC-04 and SC-02 use only verified, registered geometries. The plan documents which geometries must be registered for each test procedure.

**Rationale:** Per the progress map, only 4 of 8 geometries are verified (stage, tunnel, canyon, flyover). OBJ-022–025 are in_progress or open. The test plan must be executable now with available geometries, while also being re-runnable later when more geometries are available. TC-08 as a paper exercise can evaluate all 8 conceptually; TC-04 and SC-02 as validation/render tests require registered geometries.

### D7: TC-01 Evaluates Slot Count Per Scene Type, Not Per Geometry

**Decision:** TC-01's "15 scene types" are common video scene types (e.g., "person explaining a concept," "landscape panorama," "product showcase"). For each scene type, the evaluator determines: (a) which geometry best fits, (b) how many planes that geometry uses for the scene, and (c) whether 3–5 planes are sufficient or whether the scene feels flat/incomplete.

**Rationale:** TC-01's claim is "3-5 textured planes handles at least 90% of common YouTube/social media video scene types." The unit of analysis is the scene type, not the geometry. A scene type might map to different geometries — the question is whether any geometry can handle it with ≤5 planes.

### D8: SC-02 Topics Are a Subset of TC-08 Topics

**Decision:** The 5 topics for SC-02 are drawn from the 25 TC-08 topics, specifically chosen to span different geometries. The seed specifies the 5 topics: "deep sea creatures, space exploration, ancient Rome, cooking basics, jazz history."

**Rationale:** The seed explicitly lists these 5 topics in SC-02. Using them ensures consistency with the seed specification.

### D9: Placeholder Images for Validation-Only Tests

**Decision:** TC-04 (manifest validation) can use solid-color placeholder PNG images — one per required slot per scene. The test harness generates these automatically (e.g., 1920×1080 solid-color PNGs) or the test executor creates them manually. SC-02 (visual review) requires thematically appropriate images (either AI-generated or stock).

**Rationale:** `depthkit validate` does not check image file existence (per OBJ-046 OQ-B). So TC-04 technically doesn't even need the images to exist. However, having valid image paths makes the manifests more realistic. For SC-02, real images are essential — you can't evaluate visual quality with solid colors.

### D10: LLM Isolation Protocol

**Decision:** For TC-04 and SC-02, the LLM must operate in a fresh context with no prior depthkit knowledge. The protocol is:
1. Start a new LLM conversation (no prior messages).
2. Provide SKILL.md as system context or first message.
3. Optionally provide sub-files if the LLM requests them or if the procedure specifies.
4. Issue the authoring prompt (topic + duration + any constraints).
5. Collect the manifest output.
6. Do not provide corrections or guidance — the manifest must be accepted as-is.

**Rationale:** SC-04 says "An LLM that has never seen the engine's source code can, using only the SKILL.md, produce a valid manifest." The isolation protocol ensures this condition is met.

### D11: TC-04 Hard Rule on No Manual Coordinates

**Decision:** TC-04 manifests must contain zero instances of `position_override` or `rotation_override`. Any manifest containing these fields counts as a validation failure for TC-04 purposes, even if `depthkit validate` accepts it (since overrides are valid schema fields). This is checked by a simple text search on the JSON output.

**Rationale:** TC-04's claim is specifically "An LLM can produce a valid manifest using only geometry names and plane slot keys — without ever specifying XYZ coordinates." Allowing even 2 override uses dilutes the claim. If the LLM resorts to manual coordinates, that's a signal that SKILL.md or the geometry vocabulary is insufficient.

### D12: SC-02 Prompt Handles Unregistered Geometries Gracefully

**Decision:** The SC-02 procedure includes a note: if the LLM selects a geometry that is stubbed as "Details pending" in SKILL.md and is not registered in the engine, this counts as a SKILL.md clarity issue, not an LLM authoring failure. The evaluator documents the finding, then re-runs that single topic with a clarifying note to the LLM specifying which geometries have full documentation. Both the original and re-run results are recorded. The SC-02 pass/fail uses the re-run result, but the original result is preserved as a SKILL.md improvement finding.

**Rationale:** The purpose of SC-02 is to test whether SKILL.md enables blind authoring. If SKILL.md's stub sections are clear enough that the LLM avoids them, great. If not, that's a documentation bug in SKILL.md/OBJ-070, not a failure of the LLM's authoring ability.

### D13: Prompt Templates List Available Resources at Execution Time

**Decision:** The TC-04 prompt template includes an "Available geometries" and "Available cameras" line that must be updated by the test executor to match the currently registered geometries and cameras at execution time. The documented lists are the baseline (reflecting currently verified objectives). The SC-02 prompt template includes a single line: "Use only geometries with full documentation in the SKILL.md geometry reference (not those marked 'Details pending')."

**Rationale:** As more geometries and cameras are verified (OBJ-022–034), the available set grows. Hard-coding the list in the spec would make it stale. The executor-update instruction keeps the plan current.

## Acceptance Criteria

### Test Plan Structure

- [ ] **AC-01:** `test/plans/blind-authoring/README.md` exists and describes the purpose, prerequisites, execution order for all four test procedures, and results file naming convention (`{procedure}-{date}.md`).
- [ ] **AC-02:** `test/plans/blind-authoring/topics-25.md` exists and contains exactly 25 distinct video topics spanning at least 8 different subject domains (e.g., nature, history, technology, arts, science, food, sports, abstract concepts).
- [ ] **AC-03:** `test/plans/blind-authoring/scene-types-15.md` exists and contains exactly 15 common YouTube/social media video scene types with descriptions.
- [ ] **AC-04:** `test/plans/blind-authoring/scoring-rubric.md` exists and defines the 5-point visual quality scoring rubric with dimension definitions, score descriptions, and pass/fail thresholds.
- [ ] **AC-05:** Each of the four procedure documents (tc08, tc04, tc01, sc02) exists and contains: purpose, prerequisites, step-by-step procedure, evaluation criteria, pass/fail threshold, and results recording template.
- [ ] **AC-06:** `test/plans/blind-authoring/results/` directory exists with a `.gitkeep` file.

### TC-08: 25-Topic Geometry Mapping Test

- [ ] **AC-07:** The TC-08 procedure defines a mapping exercise: for each of 25 topics, identify the best-fit geometry and record whether the topic can be accommodated by one of the 8 proposed geometries (stage, tunnel, canyon, flyover, diorama, portal, panorama, close_up).
- [ ] **AC-08:** The TC-08 pass criterion is: at least 20 of 25 topics (80%) can be mapped to a geometry without requiring raw 3D coordinates or a new geometry type.
- [ ] **AC-09:** The TC-08 results template includes columns for: topic, best-fit geometry, alternative geometry (if any), accommodated (yes/no), and notes (e.g., "would benefit from a geometry not yet defined").
- [ ] **AC-10:** Topics that cannot be accommodated are documented with a rationale explaining what spatial structure is missing.
- [ ] **AC-11:** The TC-08 procedure notes that it should be re-executed when the geometry set changes (e.g., when OBJ-022–025 are verified), and each run's results are stored with geometry availability noted.

### TC-04: LLM-Authored Manifest Validation

- [ ] **AC-12:** The TC-04 procedure requires 10 manifests authored by an LLM in isolated context (fresh conversation, SKILL.md only, no corrections).
- [ ] **AC-13:** The TC-04 procedure specifies that each manifest must contain zero instances of `position_override` or `rotation_override`. Presence of either field in any manifest counts as a TC-04 failure for that manifest, verified by text search on the JSON output.
- [ ] **AC-14:** The TC-04 pass criterion is: all 10 manifests pass `depthkit validate` with zero errors AND contain no `position_override` or `rotation_override` fields. Warnings are acceptable.
- [ ] **AC-15:** The TC-04 results template records: topic, geometry used, camera used, validation result (pass/fail), error codes (if any), and whether the LLM included any override fields.
- [ ] **AC-16:** The TC-04 procedure includes 8 of 10 manifests in landscape (1920×1080) and 2 of 10 in portrait (1080×1920).
- [ ] **AC-17:** The TC-04 prompt template includes "Available geometries" and "Available cameras" lines with a note that the executor must update these to match currently registered resources at execution time.

### TC-01: 15-Scene-Type Plane Sufficiency

- [ ] **AC-18:** The TC-01 procedure defines 15 common scene types and asks whether each can be adequately represented by a geometry with 3–5 planes.
- [ ] **AC-19:** The TC-01 pass criterion is: at least 14 of 15 scene types (≥90%) can be handled with ≤5 planes.
- [ ] **AC-20:** For each scene type, the evaluation records: scene type, best-fit geometry, number of planes used, sufficiency rating (sufficient / borderline / insufficient), and notes on what additional planes would improve.

### SC-02: Blind Authoring Visual Validation

- [ ] **AC-21:** The SC-02 procedure uses exactly the 5 topics specified in the seed: deep sea creatures, space exploration, ancient Rome, cooking basics, jazz history.
- [ ] **AC-22:** The SC-02 procedure requires the LLM to produce a complete manifest for each topic (at least 3 scenes, approximately 60 seconds) using only SKILL.md as reference.
- [ ] **AC-23:** All 5 manifests must pass `depthkit validate` with zero errors, and all 5 must render to a playable MP4 via `depthkit render` without producing an `OrchestratorError`. Render failures are documented as depthkit bugs (per SC-06) but still count as SC-02 failures.
- [ ] **AC-24:** The SC-02 procedure requires rendering each manifest to MP4 via `depthkit render` and human visual review using the scoring rubric.
- [ ] **AC-25:** The SC-02 pass criterion is: at least 4 of 5 rendered videos score ≥ 4 on the overall impression dimension of the rubric (i.e., "correct and professional" per the seed), with no dimension scoring below 3.
- [ ] **AC-26:** The SC-02 procedure specifies that thematically appropriate images must be provided (either AI-generated via Flux.1 Schnell using `docs/skill/prompt-templates.md`, or stock photos cropped to appropriate dimensions). Solid-color placeholders are not acceptable for visual review.
- [ ] **AC-27:** The SC-02 procedure includes handling for unregistered geometry selection: if the LLM selects a geometry stubbed as "Details pending" in SKILL.md, this is documented as a SKILL.md clarity finding; the evaluator re-runs that topic with a clarifying note specifying available geometries; both results are recorded; the re-run result is used for pass/fail.
- [ ] **AC-28:** The SC-02 prompt template includes a line directing the LLM to use only geometries with full documentation (not those marked "Details pending").

### Scoring Rubric

- [ ] **AC-29:** The scoring rubric defines at least 4 dimensions: spatial correctness (planes in reasonable positions, no obvious z-fighting or clipping), camera motion quality (smooth, appropriate speed, no edge reveals), scene composition (reasonable geometry choice for the topic, appropriate slot usage), and overall impression (professional, watchable, not broken).
- [ ] **AC-30:** Each dimension uses a 1–5 scale with descriptions for each score level.
- [ ] **AC-31:** The rubric defines "looks correct and professional" as scoring ≥ 3 on every dimension and ≥ 4 on overall impression.

### Cross-Consistency

- [ ] **AC-32:** All geometry names referenced in the test plan match registered geometry names exactly: `stage`, `tunnel`, `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`.
- [ ] **AC-33:** All camera preset names referenced match registered camera names.
- [ ] **AC-34:** The test plan uses seed vocabulary consistently (plane not layer, scene geometry not layout template, etc.).
- [ ] **AC-35:** The 5 SC-02 topics match the seed's SC-02 specification exactly.

### Executability

- [ ] **AC-36:** Each procedure can be executed with only the currently verified geometries (stage, tunnel, canyon, flyover) and cameras (static, slow_push_forward, slow_pull_back, gentle_float, lateral_track_left, lateral_track_right, tunnel_push_forward, flyover_glide). Procedures note which results may change when additional geometries are verified.
- [ ] **AC-37:** The TC-04 and SC-02 procedures include the exact LLM prompt templates to use for manifest generation, ensuring repeatability.

## Edge Cases and Error Handling

### Test Execution Edge Cases

| Scenario | Handling |
|---|---|
| LLM produces invalid JSON (not parseable) | TC-04: counts as a validation failure. SC-02: the evaluator extracts the JSON block from the LLM response (LLMs often wrap JSON in markdown code blocks). If still unparseable, the manifest fails. |
| LLM uses a geometry that isn't registered yet (e.g., `portal`) | TC-04: `depthkit validate` reports `UNKNOWN_GEOMETRY`. Counts as a failure. Document which geometry the LLM attempted. SC-02: handled per D12 — document as SKILL.md clarity finding, re-run with clarification, record both results. |
| LLM uses `position_override` or `rotation_override` | TC-04: counts as a failure for that manifest per D11, regardless of whether `depthkit validate` accepts it. Document the finding as evidence that SKILL.md or the geometry vocabulary may need improvement. |
| A topic genuinely cannot be mapped to any geometry (TC-08) | Record as "not accommodated" with rationale. If > 5 topics can't be mapped, TC-08 fails and the rationale informs which new geometries are needed. |
| LLM produces a manifest with 0 scenes or negative durations | `depthkit validate` catches this. Counts as a validation failure in TC-04. |
| Human reviewer disagrees on scoring (SC-02) | The plan recommends a single reviewer for consistency. If multiple reviewers are used, scores are averaged. |
| Test images aren't available for SC-02 | The procedure includes guidance on image preparation with two options: (1) generate images via Flux.1 Schnell using prompts from `docs/skill/prompt-templates.md`, or (2) use stock photos cropped to appropriate dimensions. Without appropriate images, SC-02 cannot be executed. |
| LLM requests sub-files during SC-02 | The procedure allows it — SKILL.md's sub-file loading guide tells the LLM when to request additional files. This is part of the SKILL.md system being tested. |
| Manifest passes validation but render crashes | This is a depthkit engine bug, not a test plan issue. Document it. Per AC-23, render failures still count as SC-02 failures (the manifest didn't produce a watchable video), but the root cause is flagged for SC-06 investigation. |

### Topic Selection Edge Cases

| Scenario | Handling |
|---|---|
| A topic is ambiguous (e.g., "music" — is it a performance, a history lesson, an instrument showcase?) | Topics in the list include 1-sentence descriptions to reduce ambiguity. The LLM prompt for SC-02 includes the topic and a brief context ("a 60-second cinematic documentary about..."). |
| A topic strongly favors one geometry (e.g., "tunnel exploration") | This is intentional for some topics — they validate that the geometry works for its intended use case. The 25-topic list balances between geometry-obvious topics and geometry-ambiguous topics. |
| A topic requires features not in V1 (e.g., "sports highlights" needing video clips, not images) | TC-08 documents this as a limitation. The topic is scored as "accommodated with caveats" if a geometry can produce a reasonable static-image-based video, or "not accommodated" if the topic fundamentally requires video/animation. |

## Test Strategy

This section describes how to validate that the test plan itself is correct and complete — meta-testing.

### Plan Validation Checks (before first execution)

1. **Topic diversity check:** Verify the 25 topics span at least 8 subject domains by categorizing each topic.
2. **Scene type coverage check:** Verify the 15 scene types represent distinct visual compositions, not synonyms (e.g., "person talking to camera" and "interview" should be consolidated).
3. **Rubric calibration:** Before SC-02 execution, the human reviewer scores 2 sample videos (one known-good, one known-bad) using the rubric to verify the scale produces expected results.
4. **LLM prompt template validation:** Run each LLM prompt template through `depthkit validate` with a manually-constructed expected manifest to verify the prompt produces the right structure.
5. **Cross-reference with seed:** Verify TC-08 pass criterion (20/25 ≥ 80%) matches the seed's TC-08 claim ("at least 20 out of 25"). Verify SC-02 threshold (4/5) matches the seed. Verify TC-01 pass criterion (14/15 ≥ 90%) matches the seed's TC-01 claim ("at least 90%").

### Testable Claims Covered

| Claim | Test Procedure | How Verified |
|---|---|---|
| **TC-01:** 3-5 planes per geometry handle ≥90% of common scenes | `tc01-plane-sufficiency.md` | 15 scene types evaluated; ≥14 handled with ≤5 planes |
| **TC-04:** Geometries eliminate manual 3D positioning | `tc04-manifest-validation.md` | 10 LLM-authored manifests validated; all 10 pass without `position_override`/`rotation_override` |
| **TC-08:** 8 geometries cover the design space | `tc08-geometry-mapping.md` | 25 topics mapped; ≥20 accommodated |
| **SC-02:** Blind authoring produces correct video | `sc02-blind-authoring.md` | 5 topics: all 5 render successfully; ≥4 score "correct and professional" |
| **SC-04:** SKILL.md is self-sufficient | Implicitly tested by TC-04 and SC-02 | LLM uses only SKILL.md; manifests pass validation |

## Integration Points

### Depends On

| Dependency | What OBJ-075 Uses |
|---|---|
| **OBJ-070** (SKILL.md) | The sole reference material provided to the LLM during blind authoring tests (TC-04, SC-02). The test plan assumes SKILL.md exists at the repo root with sub-files in `docs/skill/`. The test plan validates that SKILL.md is sufficient for blind authoring. |
| **OBJ-046** (CLI Interface) | `depthkit validate <manifest>` for TC-04 automated validation. `depthkit render <manifest> -o <output>` for SC-02 rendered output. The test plan documents exact CLI invocations using OBJ-046's flag conventions (`-W`, `-H`, `-o`, `-v`). |

### Non-Dependency Verified Objectives Used at Execution Time

These are not formal dependencies of OBJ-075 (the test plan document), but they must be available when the test plan is *executed*:

| Objective | Role at Execution Time |
|---|---|
| **OBJ-018** (stage), **OBJ-019** (tunnel), **OBJ-020** (canyon), **OBJ-021** (flyover) | Verified geometries that must be registered for `depthkit validate` and `depthkit render` to work. |
| **OBJ-026–031** | Verified camera presets that must be registered. |
| **OBJ-035** (Orchestrator) | Required for `depthkit render` to function. |

### Consumed By

| Downstream | How It Uses OBJ-075 |
|---|---|
| **OBJ-078** (Final Integration) | OBJ-078 depends on OBJ-075's test results as evidence that blind authoring works. OBJ-078 does not re-run these tests — it references OBJ-075's stored results. |
| **SC-02** (Success Criterion) | The SC-02 procedure and results directly determine whether SC-02 is met. |
| **Human operators** | Execute the test plan during integration validation. |

### File Placement

```
test/plans/blind-authoring/
  README.md
  topics-25.md
  scene-types-15.md
  scoring-rubric.md
  tc08-geometry-mapping.md
  tc04-manifest-validation.md
  tc01-plane-sufficiency.md
  sc02-blind-authoring.md
  results/
    .gitkeep
```

## Appendix A: The 25 Topics (TC-08)

Organized by domain to demonstrate breadth. Each topic includes a 1-sentence context to reduce ambiguity.

| # | Topic | Context | Domain |
|---|---|---|---|
| 1 | Deep sea creatures | Educational video about bioluminescent creatures of the deep ocean. | Nature |
| 2 | Space exploration | Overview of humanity's journey from first satellites to Mars missions. | Science |
| 3 | Ancient Rome | Tour of daily life in the Roman Empire at its height. | History |
| 4 | Cooking basics | Beginner's guide to essential kitchen techniques. | Food |
| 5 | Jazz history | Evolution of jazz from New Orleans to modern fusion. | Arts |
| 6 | Volcanic eruptions | How volcanoes form and the world's most dramatic eruptions. | Earth Science |
| 7 | Renaissance art | Masterworks of the Italian Renaissance and their cultural significance. | Arts |
| 8 | Artificial intelligence | How AI works, from neural networks to large language models. | Technology |
| 9 | Coral reef ecosystems | The biodiversity and fragility of coral reef environments. | Nature |
| 10 | Medieval castles | Architecture and defensive design of European castles. | History |
| 11 | Electric vehicles | How EVs work and the future of sustainable transportation. | Technology |
| 12 | African savanna wildlife | The big five and the ecosystem of the African plains. | Nature |
| 13 | Greek mythology | The gods, heroes, and legends of ancient Greece. | Mythology |
| 14 | Cryptocurrency explained | How blockchain and digital currencies function. | Finance |
| 15 | Rainforest canopy layers | The vertical structure of tropical rainforests, from floor to emergent layer. | Nature |
| 16 | Human heart anatomy | How the heart pumps blood and the circulatory system works. | Medicine |
| 17 | Samurai warriors | The code, weapons, and daily life of feudal Japanese warriors. | History |
| 18 | Northern lights | The science behind the aurora borealis. | Science |
| 19 | Coffee bean journey | From farm to cup — how coffee is grown, processed, and roasted. | Food |
| 20 | Quantum computing | What makes quantum computers different from classical ones. | Technology |
| 21 | Ancient Egyptian pyramids | How the pyramids were built and what they contained. | History |
| 22 | Ballet fundamentals | The core positions, movements, and history of classical ballet. | Arts |
| 23 | Mars colonization | Challenges and plans for establishing a human settlement on Mars. | Science |
| 24 | Street photography | Techniques and ethics of candid urban photography. | Arts |
| 25 | Pandemic preparedness | How societies prepare for and respond to disease outbreaks. | Health |

## Appendix B: The 15 Scene Types (TC-01)

These represent common YouTube/social media video compositions, independent of topic.

| # | Scene Type | Description | Typical Geometry |
|---|---|---|---|
| 1 | Subject presentation | A person, animal, or object centered in frame with a background. | stage |
| 2 | Landscape panorama | Wide environmental shot — mountains, ocean, city skyline. | stage / panorama |
| 3 | Corridor/path walkthrough | Camera moves through a corridor, tunnel, path, or hallway. | tunnel |
| 4 | Aerial overview | Bird's-eye view of terrain, a city, or a landscape. | flyover |
| 5 | Dramatic reveal | Camera pushes into a scene to reveal a subject or environment. | stage / diorama |
| 6 | Side-by-side comparison | Two subjects shown together for contrast. | stage (2 subjects) |
| 7 | Layered depth showcase | Multiple elements at different depths creating paper-theater effect. | diorama |
| 8 | Enclosed space | Interior of a room, cave, underwater cavern, or building interior. | tunnel / canyon |
| 9 | Vertical scale | Tall structures, waterfalls, canyon walls — emphasizing height. | canyon |
| 10 | Title/intro card | Opening sequence with text overlay on atmospheric background. | stage / close_up |
| 11 | Close-up detail | Tight shot on a detail — texture, face, small object. | close_up |
| 12 | Environmental ambiance | Mood piece — no central subject, just atmosphere and motion. | panorama / stage |
| 13 | Transition/portal | Visual journey from one space to another through concentric frames. | portal |
| 14 | Product showcase | A product centered with clean background and subtle camera motion. | stage / close_up |
| 15 | Historical scene | Reconstruction of a historical setting with figures and environment. | stage / tunnel |

## Appendix C: SC-02 Scoring Rubric

### Dimensions

#### 1. Spatial Correctness (1–5)

| Score | Description |
|---|---|
| 1 | **Broken.** Planes visibly overlap incorrectly, z-fighting, planes facing wrong direction, or scene is unintelligible. |
| 2 | **Major issues.** One or more planes are clearly in the wrong position (e.g., floor floating above subject, background in front of foreground). |
| 3 | **Acceptable.** Planes are in reasonable positions. Minor spatial issues (e.g., slight depth mismatch) but the scene reads correctly. |
| 4 | **Good.** All planes are correctly positioned. Depth ordering is natural. No spatial artifacts. |
| 5 | **Excellent.** Depth relationships feel natural and immersive. Perspective foreshortening enhances the 3D illusion. |

#### 2. Camera Motion Quality (1–5)

| Score | Description |
|---|---|
| 1 | **Broken.** Camera doesn't move when it should, moves erratically, or reveals plane edges. |
| 2 | **Poor.** Motion is technically functional but feels robotic, too fast, or too slow for the content. |
| 3 | **Acceptable.** Motion is smooth and doesn't reveal edges. Speed is reasonable for the content. |
| 4 | **Good.** Motion feels intentional and cinematic. Easing is appropriate. Enhances the scene. |
| 5 | **Excellent.** Camera motion feels professional — smooth, well-paced, emotionally appropriate for the content. |

#### 3. Scene Composition (1–5)

| Score | Description |
|---|---|
| 1 | **Wrong geometry.** The chosen geometry makes no sense for the topic (e.g., tunnel for a landscape panorama). |
| 2 | **Poor fit.** Geometry choice is defensible but clearly suboptimal. Key visual elements are missing or poorly placed. |
| 3 | **Acceptable.** Geometry fits the topic. Slot assignments are reasonable. The scene communicates its subject. |
| 4 | **Good.** Geometry is well-chosen. Slots are used effectively. The composition tells a clear visual story. |
| 5 | **Excellent.** Geometry perfectly suits the content. Every slot contributes meaningfully. The composition is visually compelling. |

#### 4. Overall Impression (1–5)

| Score | Description |
|---|---|
| 1 | **Unwatchable.** Would not be usable in any context. |
| 2 | **Amateur.** Recognizable as a video but clearly broken or unprofessional. |
| 3 | **Passable.** Could be used in a low-stakes context. Noticeable issues but functional. |
| 4 | **Professional.** Looks like a competent video production. Minor imperfections at most. Meets the "correct and professional" bar. |
| 5 | **Impressive.** Would compete with manually-produced parallax videos. Demonstrates clear 2.5D depth quality. |

### Pass Threshold

A manifest **passes** SC-02 if:
- Every dimension scores ≥ 3 (no broken dimensions), AND
- Overall Impression scores ≥ 4 ("correct and professional")

SC-02 overall **passes** if:
- All 5 manifests validate and render successfully (per AC-23), AND
- ≥ 4 of 5 rendered videos pass the scoring threshold above.

## Appendix D: LLM Prompt Templates

### TC-04 Prompt Template (Manifest Validation)

```
You are a video producer using depthkit to create 2.5D parallax videos.

Using only the SKILL.md reference provided, create a complete depthkit manifest JSON for:

Topic: {TOPIC}
Duration: 45 seconds
Orientation: {ORIENTATION — "landscape (1920x1080)" for 8 manifests, "portrait (1080x1920)" for 2 manifests}

Requirements:
- At least 3 scenes
- Use only geometry names and slot keys from the SKILL.md reference
- Do NOT use position_override or rotation_override
- Use appropriate transitions between scenes
- Include audio configuration (use "./audio/narration.mp3" as the audio path)
- Use image paths in the format ./images/{scene_id}_{slot_name}.png

Available geometries: {UPDATE THIS LIST to match currently registered geometries at execution time. Baseline: stage, tunnel, canyon, flyover}
Available cameras: {UPDATE THIS LIST to match currently registered cameras at execution time. Baseline: static, slow_push_forward, slow_pull_back, gentle_float, lateral_track_left, lateral_track_right, tunnel_push_forward, flyover_glide}

Output only the JSON manifest, no explanation.
```

### SC-02 Prompt Template (Blind Authoring)

```
You are a video producer using depthkit to create 2.5D parallax videos.

Using only the SKILL.md reference provided, create a complete depthkit manifest JSON for:

Topic: {TOPIC}
Duration: 60 seconds
Style: cinematic documentary
Orientation: landscape (1920x1080)

Requirements:
- At least 3 scenes with appropriate durations
- Choose geometries that best fit each scene's visual content
- Use only geometries with full documentation in the SKILL.md geometry reference (not those marked "Details pending")
- Use transitions between scenes
- Include audio configuration (use "./audio/narration.mp3" as the audio path)
- Use image paths in the format ./images/{scene_id}_{slot_name}.png

Create the most visually compelling video you can for this topic using the available geometries and camera presets.

Output only the JSON manifest, no explanation.
```

## Open Questions

### OQ-A: Should TC-04 and SC-02 specify which LLM model to use?

The seed says "An LLM (Claude)" for SC-02. **Recommendation:** Specify "Claude (Sonnet-class or above)" and record the exact model version used in each test run's results. This is reflected in the Test Execution Dependencies table.

### OQ-B: How should AI-generated images for SC-02 be produced?

SC-02 requires thematically appropriate images. The test plan doesn't specify the image generation pipeline (that's outside depthkit's scope per AP-04). **Recommendation:** The SC-02 procedure includes a brief section on image preparation with two options: (1) generate images via Flux.1 Schnell using prompts from `docs/skill/prompt-templates.md`, or (2) use stock photos cropped to appropriate dimensions. The evaluator chooses based on what's available. This is reflected in AC-26.

### OQ-C: Should TC-08 be re-run when new geometries are verified?

**Yes.** This is reflected in AC-11. TC-08 results may change as OBJ-022–025 are verified. Each run stores results with a timestamp and geometry availability note.

### OQ-D: Should TC-04 test portrait (9:16) manifests?

**Yes.** 2 of 10 manifests are portrait mode. This is reflected in AC-16 and the TC-04 prompt template.
