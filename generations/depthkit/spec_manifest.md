# spec_manifest.md — Depthkit Specification DAG Navigator

**Generated:** 2026-03-23
**Seed Version:** 3.0
**Total Objectives:** 83 (72 verified, 11 approved awaiting visual tuning, 0 blocked, 0 dead ends)

---

## 1. What This DAG Is

This DAG is the complete **design specification** for **depthkit** — a zero-license Node.js video engine that renders 2.5D parallax video from declarative JSON manifests using Puppeteer, Three.js, and FFmpeg. It was produced by multi-agent deliberation: an initializer decomposed the seed document into objectives, explorer agents wrote specifications for each, and integrator/reviewer agents validated coherence across the graph.

**Each node is a design document, not code.** The DAG is the input to a downstream execution harness that will implement these specs as working software. The specs define interfaces, type contracts, algorithms, acceptance criteria, and integration points. An implementer reads the specs and writes the code.

The 83 objectives break down by category:
- **Engine** (24): Rendering pipeline, CLI, orchestrator, encoding, validation
- **Spatial** (26): Scene geometries, camera paths, depth model, coordinate math
- **Integration** (16): Cross-system wiring, Docker, SKILL.md, n8n, asset pipeline
- **Tuning** (11): Director Agent visual tuning cycles for each geometry + transitions
- **Exploration** (6): Low-priority deferred investigations (OBJ-079 through OBJ-083)

---

## 2. How to Read This DAG

### File Structure

```
depthkit/
├── seed.md                    # The authoritative seed document (read first, always)
├── index.json                 # Graph structure: nodes, edges, statuses, priorities
├── spec_manifest.md           # This file — the navigation map
├── nodes/
│   └── OBJ-NNN/
│       ├── meta.json          # What the objective is (description, deps, status)
│       ├── output.md          # The specification (the deliverable)
│       └── transcript.md      # The conversation that produced the spec
├── dead_ends/                 # Empty — no dead ends in this DAG
├── sessions/                  # Session logs from the deliberation process
└── feed.md                    # Chronological activity log
```

### Reading Order Rules

1. **Always start with `seed.md`.** It defines the vocabulary, constraints, and directional sketches that every spec references.
2. **Dependencies flow forward.** If OBJ-011 depends on OBJ-009, OBJ-010, and OBJ-005, read those three specs before reading OBJ-011's `output.md`.
3. **Each `output.md` is self-contained given the seed + its dependency specs.** You do not need to read the entire DAG to implement a single node.
4. **`transcript.md` is optional context.** It shows how the spec was developed — useful for understanding rationale behind design decisions, but not required for implementation.

### Status Definitions

| Status | Meaning |
|--------|---------|
| `verified` | Spec complete, reviewed, and approved. Ready for implementation. |
| `approved` | Spec complete and approved, but has a `visual_status` field indicating it requires Director Agent visual tuning during implementation. |
| `in_progress` | Spec being written. (None currently.) |
| `blocked` | Cannot proceed until dependencies are resolved. (None currently.) |

### Visual Status

Eleven objectives carry `visual_status: "needs_tuning"`. These are the tuning objectives (OBJ-059 through OBJ-069) that require the Director Agent workflow from Seed Section 10. They cannot be completed by a code agent alone — they require rendered test output reviewed by a vision-capable LLM, filtered through the HITL circuit breaker.

---

## 3. The Four Deliverables

The seed (Section 1) defines four deliverables. Below, each deliverable is broken into its constituent objectives, grouped by implementation layer, with recommended reading order.

---

### Deliverable 1: The Depthkit Rendering Engine

The custom Puppeteer + Three.js + FFmpeg pipeline that accepts a manifest and produces an MP4. This is the core product.

#### Foundation Layer (implement first)

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-001 | Project scaffolding and build system | critical | — | verified |
| OBJ-002 | Interpolation, easing, and spring utilities | critical | — | verified |
| OBJ-003 | Coordinate system and spatial math reference | critical | — | verified |

#### Schema and Validation Layer

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-004 | Manifest schema core (Zod) | critical | OBJ-001 | verified |
| OBJ-016 | Manifest loader and validator | critical | OBJ-004 | verified |
| OBJ-017 | Geometry-specific structural manifest validation | high | OBJ-004, OBJ-005 | verified |
| OBJ-048 | Error handling and reporting strategy | high | OBJ-016, OBJ-035 | verified |

#### Rendering Pipeline Layer

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-009 | Virtualized clock + Puppeteer bridge | critical | OBJ-001 | verified |
| OBJ-010 | Three.js page shell, build/bundle, scene renderer skeleton | critical | OBJ-001, OBJ-003 | verified |
| OBJ-011 | Puppeteer-to-page message protocol | critical | OBJ-009, OBJ-010, OBJ-005 | verified |
| OBJ-012 | Frame capture pipeline (CDP screenshot) | critical | OBJ-011 | verified |
| OBJ-013 | FFmpeg encoder (stdin piping, H.264) | critical | OBJ-001 | verified |
| OBJ-014 | FFmpeg audio muxing | high | OBJ-013 | verified |
| OBJ-015 | Texture loader and format handling | high | OBJ-010 | verified |

#### Orchestration Layer

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-035 | Orchestrator — main render loop | critical | OBJ-009, OBJ-012, OBJ-013, OBJ-016 | verified |
| OBJ-036 | Scene sequencer | critical | OBJ-035, OBJ-005, OBJ-008 | verified |
| OBJ-037 | Transition renderer (crossfade, dip_to_black, cut) | high | OBJ-036, OBJ-008 | verified |
| OBJ-038 | Audio sync and scene timing | high | OBJ-009, OBJ-014, OBJ-016 | verified |
| OBJ-039 | Three.js page-side geometry instantiation | high | OBJ-010, OBJ-005, OBJ-015, OBJ-011 | verified |

#### Interface Layer

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-046 | CLI interface (render, validate, preview commands) | high | OBJ-035 | verified |
| OBJ-047 | Library API (programmatic interface) | high | OBJ-035 | verified |
| OBJ-049 | Software rendering configuration (SwiftShader flags) | high | OBJ-012 | verified |
| OBJ-050 | Docker containerization | medium | OBJ-046, OBJ-049 | verified |

#### Engine Explorations (low priority, deferrable)

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-082 | Browser preview mode (localhost real-time playback) | low | OBJ-010, OBJ-035 | verified |
| OBJ-083 | Parallel rendering exploration (multi-instance) | low | OBJ-035, OBJ-013 | verified |

**Recommended implementation order:** OBJ-001 → OBJ-003 → OBJ-002 → OBJ-010 → OBJ-009 → OBJ-013 → OBJ-004 → OBJ-016 → OBJ-005 → OBJ-011 → OBJ-012 → OBJ-015 → OBJ-035 → OBJ-036 → OBJ-037 → OBJ-038 → OBJ-046 → OBJ-047 → OBJ-049 → OBJ-050

---

### Deliverable 2: The Spatial Authoring Vocabulary

The library of scene geometries, camera paths, depth model, and composition rules that make blind authoring possible.

#### Type System

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-005 | Scene geometry type contract (SceneGeometry, PlaneSlot) | critical | OBJ-003 | verified |
| OBJ-006 | Camera path type contract (CameraPathPreset, CameraParams) | critical | OBJ-002, OBJ-003 | verified |
| OBJ-007 | Depth model specification (slot taxonomy, Z-positions) | critical | OBJ-003 | verified |
| OBJ-008 | Transition type contract (cut, crossfade, dip_to_black) | high | OBJ-002 | verified |

#### Scene Geometries (8 total)

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-018 | Stage geometry (default — backdrop + floor + subject) | high | OBJ-005, OBJ-007 | verified |
| OBJ-019 | Tunnel geometry (floor, ceiling, walls, end wall) | high | OBJ-005, OBJ-007 | verified |
| OBJ-020 | Canyon geometry (tall walls, floor, open sky) | high | OBJ-005, OBJ-007 | verified |
| OBJ-021 | Flyover geometry (ground plane, sky, landmarks) | high | OBJ-005, OBJ-007 | verified |
| OBJ-022 | Diorama geometry (semicircle of planes, paper theater) | medium | OBJ-005, OBJ-007 | verified |
| OBJ-023 | Portal geometry (concentric frames at increasing Z) | medium | OBJ-005, OBJ-007 | verified |
| OBJ-024 | Panorama geometry (wide backdrop, camera pans) | medium | OBJ-005, OBJ-007 | verified |
| OBJ-025 | Close-up geometry (tight subject, subtle motion) | medium | OBJ-005, OBJ-007 | verified |

#### Camera Path Presets (9 total)

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-026 | Static camera (no movement) | high | OBJ-006 | verified |
| OBJ-027 | Push/pull forward/back (defining 2.5D motion) | high | OBJ-006 | verified |
| OBJ-028 | Lateral track left/right | high | OBJ-006 | verified |
| OBJ-029 | Tunnel push forward (tuned for tunnel geometry) | high | OBJ-006 | verified |
| OBJ-030 | Flyover glide (elevated Y, downward look) | high | OBJ-006 | verified |
| OBJ-031 | Gentle float (subtle multi-axis drift) | high | OBJ-006 | verified |
| OBJ-032 | Dramatic push (fast forward with ease-out) | medium | OBJ-006 | verified |
| OBJ-033 | Crane up (Y-axis rise) | medium | OBJ-006 | verified |
| OBJ-034 | Dolly zoom (Z push + FOV animation) | medium | OBJ-006 | verified |

#### Spatial Systems

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-040 | Plane sizing and oversizing system | high | OBJ-005, OBJ-006, OBJ-003, OBJ-015 | verified |
| OBJ-041 | Geometry-camera spatial compatibility validation | high | OBJ-005, OBJ-006 | verified |
| OBJ-042 | Fog and atmosphere system | medium | OBJ-005, OBJ-010 | verified |
| OBJ-043 | HUD layer system (2D overlay for text) | medium | OBJ-010, OBJ-012 | verified |
| OBJ-044 | Per-frame plane opacity animation | medium | OBJ-005, OBJ-004, OBJ-010 | verified |
| OBJ-045 | Portrait/vertical (9:16) adaptation | medium | OBJ-005, OBJ-006, OBJ-004 | verified |

#### Spatial Explorations (low priority, deferrable)

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-079 | Camera path composition/chaining | low | OBJ-006, OBJ-002 | verified |
| OBJ-080 | Dynamic plane count per geometry | low | OBJ-005 | verified |
| OBJ-081 | Lighting system exploration | low | OBJ-010, OBJ-005 | verified |

**Recommended implementation order:** OBJ-003 → OBJ-002 → OBJ-005 → OBJ-006 → OBJ-007 → OBJ-008 → OBJ-018 → OBJ-019 → (OBJ-020 through OBJ-025 in parallel) → OBJ-026 → OBJ-027 → (OBJ-028 through OBJ-034 in parallel) → OBJ-040 → OBJ-041 → OBJ-042 → OBJ-043 → OBJ-044 → OBJ-045

**Integration boundary with Deliverable 1:** The type contracts (OBJ-005, OBJ-006, OBJ-008) are consumed by the engine's scene sequencer (OBJ-036), page-side geometry instantiation (OBJ-039), message protocol (OBJ-011), and manifest validation (OBJ-017). Implement the type contracts before the engine layers that consume them.

---

### Deliverable 3: The SKILL.md

The LLM instruction document that enables blind authoring of manifests.

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-070 | SKILL.md structure and core content | high | OBJ-004, OBJ-046, OBJ-018, OBJ-027 | verified |
| OBJ-071 | SKILL.md geometry and camera reference sections | high | OBJ-070, OBJ-005, OBJ-006, OBJ-018, OBJ-019 | verified |
| OBJ-072 | SKILL.md prompt templates, patterns, anti-patterns | medium | OBJ-070, OBJ-051 | verified |

**Recommended implementation order:** OBJ-070 → OBJ-071 → OBJ-072

**Integration boundary:** OBJ-070 depends on OBJ-046 (CLI) for documenting render commands, and on OBJ-018/OBJ-027 for the annotated example. OBJ-071 depends on the geometry and camera type contracts. OBJ-072 depends on the image generation strategy (OBJ-051). The SKILL.md is also consumed by OBJ-056 (manifest generation via Claude API) as the knowledge base for the generation prompt.

---

### Deliverable 4: The n8n-Compatible HTTP Interface

The production pipeline: HTTP endpoint → manifest generation → asset retrieval → rendering → MP4 delivery.

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-051 | Image generation strategy (Flux.1 prompt engineering) | medium | OBJ-007 | verified |
| OBJ-052 | Background removal integration (rembg) | medium | OBJ-015 | verified |
| OBJ-053 | Semantic caching database schema (Supabase/pgvector) | medium | OBJ-007 | verified |
| OBJ-054 | Semantic caching middleware logic (threshold gate) | medium | OBJ-053, OBJ-051 | verified |
| OBJ-055 | n8n HTTP endpoint and job lifecycle | medium | OBJ-047 | verified |
| OBJ-056 | Manifest generation via Claude API | medium | OBJ-004, OBJ-071 | verified |
| OBJ-057 | Asset orchestration pipeline (TTS + images + assembly) | medium | OBJ-054, OBJ-052, OBJ-055, OBJ-056 | verified |

**Recommended implementation order:** OBJ-051 → OBJ-053 → OBJ-054 → OBJ-052 → OBJ-055 → OBJ-056 → OBJ-057

**Integration boundary:** OBJ-055 wraps the library API (OBJ-047). OBJ-056 uses the SKILL.md (OBJ-071) and the manifest schema (OBJ-004). OBJ-057 is the glue — it connects everything and is on the critical path to the capstone (OBJ-078).

---

### Visual Tuning Objectives (Director Agent Required)

These are approved specs but require the Director Agent visual tuning workflow (Seed Section 10) during implementation. They cannot be completed by a code agent alone.

| ID | Description | Priority | Depends On | Visual Status |
|----|-------------|----------|------------|---------------|
| OBJ-059 | Tune stage geometry | medium | OBJ-018, OBJ-026, OBJ-027, OBJ-031, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-060 | Tune tunnel geometry | medium | OBJ-019, OBJ-026, OBJ-029, OBJ-031, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-061 | Tune canyon geometry | medium | OBJ-020, OBJ-026, OBJ-027, OBJ-031, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-062 | Tune flyover geometry | medium | OBJ-021, OBJ-030, OBJ-031, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-063 | Tune diorama geometry | medium | OBJ-022, OBJ-026, OBJ-027, OBJ-031, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-064 | Tune portal geometry | medium | OBJ-023, OBJ-026, OBJ-027, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-065 | Tune panorama geometry | medium | OBJ-024, OBJ-026, OBJ-031, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-066 | Tune close-up geometry | medium | OBJ-025, OBJ-026, OBJ-031, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-067 | Cross-geometry camera path validation | medium | OBJ-059–OBJ-066 | needs_tuning |
| OBJ-068 | Transition visual validation | medium | OBJ-037, OBJ-035, OBJ-058 | needs_tuning |
| OBJ-069 | Edge reveal systematic validation | high | OBJ-018, OBJ-027, OBJ-040, OBJ-041, OBJ-035 | needs_tuning |

**All 8 geometry tuning objectives (OBJ-059–OBJ-066) can execute in parallel** once their dependencies are met. OBJ-067 (cross-geometry validation) is a convergence gate — it cannot start until all 8 are done. OBJ-068 and OBJ-069 can run in parallel with the geometry tuning.

---

### Validation and Test Plans

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-058 | Director Agent workflow specification | high | OBJ-035 | verified |
| OBJ-073 | Deterministic output verification plan | high | OBJ-035 | verified |
| OBJ-074 | Performance benchmark plan | high | OBJ-035, OBJ-049 | verified |
| OBJ-075 | Blind authoring test plan | high | OBJ-070, OBJ-046 | verified |
| OBJ-076 | Semantic cache validation plan | medium | OBJ-054 | verified |
| OBJ-077 | End-to-end integration test plan | high | OBJ-035, OBJ-046, OBJ-037, OBJ-038 | verified |

### Capstone

| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-078 | End-to-end validation execution gate | high | OBJ-077, OBJ-067, OBJ-068, OBJ-057, OBJ-038 | verified |

OBJ-078 is the final gate. The project is production-ready when this objective passes.

---

## 4. The Critical Path

The critical path is the longest dependency chain from a root node to OBJ-078 (the capstone). There are two competing long paths — one through the engine+tuning chain, one through the asset pipeline. The engine+tuning chain is longer.

### Primary Critical Path (Engine → Tuning → Capstone)

```
OBJ-001  Project scaffolding
  → OBJ-009  Virtualized clock + Puppeteer bridge
    → OBJ-011  Message protocol  (also needs OBJ-010, OBJ-005)
      → OBJ-012  Frame capture pipeline
        → OBJ-035  Orchestrator  (also needs OBJ-013, OBJ-016)
          → OBJ-058  Director Agent workflow spec
            → OBJ-059  Tune stage geometry  (also needs OBJ-018, OBJ-026, OBJ-027, OBJ-031)
              → OBJ-067  Cross-geometry camera validation  (also needs OBJ-060–OBJ-066)
                → OBJ-078  End-to-end validation gate  (also needs OBJ-077, OBJ-068, OBJ-057, OBJ-038)
```

**Length: 9 hops from root to capstone** (more when accounting for the 8 parallel geometry tunes that OBJ-067 waits on).

The bottleneck is the **tuning funnel**: OBJ-067 requires all 8 geometry tuning objectives (OBJ-059 through OBJ-066) to complete. Each tuning objective requires the orchestrator (OBJ-035), the Director workflow spec (OBJ-058), its specific geometry and camera path implementations, and at least one round of visual review. If parallelism is limited, prioritize **stage** (OBJ-059) and **tunnel** (OBJ-060) tuning first — they are the most-used geometries and unblock the SKILL.md content.

### Secondary Critical Path (Asset Pipeline → Capstone)

```
OBJ-001  Project scaffolding
  → OBJ-004  Manifest schema
    → OBJ-016  Manifest loader
      → OBJ-035  Orchestrator
        → OBJ-047  Library API
          → OBJ-055  n8n HTTP endpoint
            → OBJ-057  Asset orchestration pipeline  (also needs OBJ-054, OBJ-052, OBJ-056)
              → OBJ-078  End-to-end validation gate
```

This path is shorter (7 hops) but joins OBJ-078 as a required dependency. The asset pipeline can be built in parallel with the tuning work.

### Minimum Viable Path (to first rendered video)

To produce a single rendered MP4 as fast as possible:

```
OBJ-001 → OBJ-003 → OBJ-005 → OBJ-007 → OBJ-018 (stage geometry)
OBJ-001 → OBJ-009 → (need OBJ-010, OBJ-011) → OBJ-012
OBJ-001 → OBJ-013
OBJ-001 → OBJ-004 → OBJ-016
All above → OBJ-035 (orchestrator) → OBJ-046 (CLI) → render a test video
```

This gives you a CLI that can render a single-scene stage geometry video. Approximately 13 objectives.

---

## 5. Cross-Cutting Concerns

These objectives are load-bearing — they are depended upon by many downstream nodes. If their specs are wrong, large sections of the DAG break.

| ID | Description | Blocks (count) | Why It's Critical |
|----|-------------|-----------------|-------------------|
| OBJ-005 | Scene geometry type contract | 20 objectives | Every geometry, the sequencer, page-side instantiation, manifest validation, and multiple spatial systems depend on it. |
| OBJ-006 | Camera path type contract | 14 objectives | Every camera preset, compatibility validation, oversizing, and the SKILL.md reference depend on it. |
| OBJ-035 | Orchestrator | 20 objectives | Every downstream integration — CLI, library API, Docker, tuning, test plans, and the capstone — depends on it. |
| OBJ-003 | Coordinate system and spatial math | 5 objectives | Foundational spatial math referenced by all geometry and camera specs. |
| OBJ-001 | Project scaffolding | 4 objectives | Build system underpins everything. |
| OBJ-010 | Three.js page shell + build strategy | 8 objectives | The Node.js/browser code-split architecture decision affects all page-side code. |
| OBJ-004 | Manifest schema core | 6 objectives | The manifest is the contract between LLM authors and the engine. |

**Key coupling points:**
- **OBJ-005 ↔ OBJ-006**: Geometry and camera contracts must agree on spatial units, coordinate conventions, and the `compatible_cameras` / `OversizeRequirements` handshake.
- **OBJ-010 ↔ OBJ-011**: The page shell architecture constrains the message protocol design (ESM vs bundled, how geometry code gets into the browser).
- **OBJ-035 ↔ OBJ-036**: The orchestrator drives the scene sequencer's frame-by-frame iteration; their frame/time contracts must be identical.
- **OBJ-004 ↔ OBJ-017 ↔ OBJ-041**: Three layers of manifest validation — structural schema (OBJ-004), geometry-specific slot matching (OBJ-017), and spatial compatibility (OBJ-041). They must compose cleanly.

---

## 6. Dead Ends

**None.** The `dead_ends/` directory is empty and `index.json` reports zero dead ends. No explored approach was ruled out as infeasible.

---

## 7. Unresolved Items

### Visual Tuning Backlog

All 11 tuning objectives (OBJ-059 through OBJ-069) have `visual_status: "needs_tuning"` and status `approved` (not `verified`). They are fully specified but have not been executed. Per SC-07, every scene geometry must be visually tuned before the engine is production-ready. **The tuning work is the primary remaining blocker for the capstone (OBJ-078).**

### Open Questions from the Seed

The following seed open questions were addressed by specific objectives but their resolution depends on implementation:

| Open Question | Addressed By | Notes |
|---------------|-------------|-------|
| OQ-01: Per-frame plane opacity | OBJ-044 (verified) | Spec written; scope decision made |
| OQ-02: Images without alpha | OBJ-015, OBJ-052 (both verified) | Texture handling + rembg integration |
| OQ-03: Subtitle/caption overlay | OBJ-043 (verified) | HUD layer system specified |
| OQ-04: Vertical (9:16) adaptation | OBJ-045 (verified) | Portrait adaptation specified |
| OQ-05: Browser preview mode | OBJ-082 (verified, low priority) | Deferred exploration |
| OQ-06: Camera path composition | OBJ-079 (verified, low priority) | Deferred exploration |
| OQ-07: Minimum viable geometries | Addressed across OBJ-018–025 | All 8 specified; stage+tunnel are high priority |
| OQ-08: Dynamic plane count | OBJ-080 (verified, low priority) | Deferred exploration |
| OQ-09: Lighting system | OBJ-081 (verified, low priority) | Deferred exploration |
| OQ-10: Parallel rendering | OBJ-083 (verified, low priority) | Deferred exploration |

### Structural Observations

- **No orphaned nodes.** Every objective either has dependents or is a leaf (terminal) node.
- **No disconnected subgraphs.** All objectives trace back to one of the three root nodes (OBJ-001, OBJ-002, OBJ-003).
- **OBJ-078 is reachable from all critical-path nodes.** The capstone gate properly aggregates all major work streams.
- **Low-priority explorations (OBJ-079–OBJ-083) do not block any other objective.** They are safe to defer indefinitely.

---

## 8. Instructions for the Downstream Execution Harness

### Prerequisites

1. **The seed document (`seed.md`) must be available to every implementation session.** It defines binding vocabulary, constraints, and anti-patterns. An implementer without the seed will misinterpret spec terminology.
2. **Process objectives in strict dependency order.** Never implement a node before all of its `depends_on` nodes are implemented. The `index.json` graph is the source of truth for edges.
3. **Each `output.md` is the implementation spec.** Read the seed, read the dependency specs' `output.md` files, then implement. The `transcript.md` is optional context.

### Implementation Strategy

- **Maximize parallelism on root nodes.** OBJ-001, OBJ-002, and OBJ-003 have no dependencies and can be implemented simultaneously.
- **The three root nodes unlock a wide fan-out.** After roots, OBJ-004, OBJ-005, OBJ-006, OBJ-007, OBJ-008, OBJ-009, OBJ-010 can all proceed (respecting their individual dependencies).
- **All 8 scene geometries (OBJ-018–025) can be implemented in parallel** once OBJ-005 and OBJ-007 are done. Similarly, all 9 camera path presets (OBJ-026–034) can parallelize after OBJ-006.
- **The orchestrator (OBJ-035) is the convergence point.** It requires 4 dependencies (OBJ-009, OBJ-012, OBJ-013, OBJ-016) and is the gateway to all downstream integration, CLI, and tuning work. Prioritize its dependency chain.

### Visual Tuning Objectives

Objectives with `visual_status: "needs_tuning"` (OBJ-059 through OBJ-069) require the **Director Agent workflow** defined in OBJ-058 (Seed Section 10):

1. The code agent implements the geometry/camera code and renders a test video.
2. A vision-capable LLM (Director Agent) reviews the render and produces a Visual Critique.
3. A **human** reviews the critique (HITL circuit breaker), approves/modifies/rejects.
4. The code agent applies approved feedback and re-renders.
5. Loop until the human signs off. Mark `visual_status: "tuned"` in `meta.json` and `index.json`.

**Do not skip the HITL gate.** The Director Agent's output must never reach the code agent unfiltered (AP-09).

### Testable Claims and Success Criteria

The seed defines 20 testable claims (TC-01 through TC-20) and 7 success criteria (SC-01 through SC-07). These are mapped to specific objectives:

| Claim/Criterion | Validated By |
|-----------------|-------------|
| TC-01 (5 planes sufficient) | OBJ-018, OBJ-075 |
| TC-02 (render performance) | OBJ-074 |
| TC-03 (perspective projection convincing) | OBJ-069 |
| TC-04 (geometries eliminate manual positioning) | OBJ-075 |
| TC-05 (tunnel produces convincing depth) | OBJ-060 |
| TC-06 (deterministic output) | OBJ-073 |
| TC-07 (validation catches errors) | OBJ-017 |
| TC-08 (8 geometries cover design space) | OBJ-075 |
| TC-09 (eased paths feel natural) | OBJ-067 |
| TC-10 (transitions mask seams) | OBJ-068 |
| TC-11 (Docker with software WebGL) | OBJ-050 |
| TC-12 (rembg viable) | OBJ-052 |
| TC-13 (audio drives video length) | OBJ-038 |
| TC-14 (FOV animation useful) | OBJ-034 |
| TC-15 (Director converges in ≤5 iterations) | OBJ-058 |
| TC-16 (Director-tuned > blind-authored) | OBJ-058 |
| TC-17 (0.92 threshold acceptable) | OBJ-076 |
| TC-18 (slot-type filter prevents contamination) | OBJ-076 |
| TC-19 (cache hit rates 30-60%) | OBJ-076 |
| TC-20 (embedding latency negligible) | OBJ-076 |
| SC-01 (end-to-end rendering) | OBJ-078 |
| SC-02 (blind authoring) | OBJ-075 |
| SC-03 (performance target) | OBJ-074 |
| SC-04 (SKILL.md self-sufficient) | OBJ-075 |
| SC-05 (n8n integration) | OBJ-078 |
| SC-06 (validation comprehensive) | OBJ-078 |
| SC-07 (all geometries tuned) | OBJ-067 |

### Anti-Patterns to Enforce

The seed defines 10 anti-patterns (AP-01 through AP-10). The most implementation-relevant:

- **AP-02**: All rendering goes through the virtualized clock. No `requestAnimationFrame` for frame timing.
- **AP-03**: If the LLM has to specify pixel coordinates, the abstraction has failed.
- **AP-04**: The rendering engine does not generate images or call external APIs. Asset generation is a separate pipeline stage.
- **AP-06**: Use seed vocabulary exactly. Do not introduce synonyms.
- **AP-09**: Director Agent output must pass through the human before reaching the code agent. No exceptions.

---

## Appendix: Complete Objective Index

| ID | Category | Priority | Status | Visual | Depends On | Blocks |
|----|----------|----------|--------|--------|------------|--------|
| OBJ-001 | engine | critical | verified | — | — | 004, 009, 010, 013 |
| OBJ-002 | engine | critical | verified | — | — | 006, 008, 079 |
| OBJ-003 | spatial | critical | verified | — | — | 005, 006, 007, 010, 040 |
| OBJ-004 | engine | critical | verified | — | 001 | 016, 017, 044, 045, 056, 070 |
| OBJ-005 | spatial | critical | verified | — | 003 | 011, 017–025, 036, 039–042, 044, 045, 071, 080, 081 |
| OBJ-006 | spatial | critical | verified | — | 002, 003 | 026–034, 040, 041, 045, 071, 079 |
| OBJ-007 | spatial | critical | verified | — | 003 | 018–025, 051, 053 |
| OBJ-008 | spatial | high | verified | — | 002 | 036, 037 |
| OBJ-009 | engine | critical | verified | — | 001 | 011, 035, 038 |
| OBJ-010 | engine | critical | verified | — | 001, 003 | 011, 015, 039, 042–044, 081, 082 |
| OBJ-011 | engine | critical | verified | — | 009, 010, 005 | 012, 039 |
| OBJ-012 | engine | critical | verified | — | 011 | 035, 043, 049 |
| OBJ-013 | engine | critical | verified | — | 001 | 014, 035, 083 |
| OBJ-014 | engine | high | verified | — | 013 | 038 |
| OBJ-015 | engine | high | verified | — | 010 | 039, 040, 052 |
| OBJ-016 | engine | critical | verified | — | 004 | 035, 038, 048 |
| OBJ-017 | engine | high | verified | — | 004, 005 | — |
| OBJ-018 | spatial | high | verified | — | 005, 007 | 059, 069, 070, 071 |
| OBJ-019 | spatial | high | verified | — | 005, 007 | 060, 071 |
| OBJ-020 | spatial | high | verified | — | 005, 007 | 061 |
| OBJ-021 | spatial | high | verified | — | 005, 007 | 062 |
| OBJ-022 | spatial | medium | verified | — | 005, 007 | 063 |
| OBJ-023 | spatial | medium | verified | — | 005, 007 | 064 |
| OBJ-024 | spatial | medium | verified | — | 005, 007 | 065 |
| OBJ-025 | spatial | medium | verified | — | 005, 007 | 066 |
| OBJ-026 | spatial | high | verified | — | 006 | 059–061, 063–066 |
| OBJ-027 | spatial | high | verified | — | 006 | 059, 061, 063, 064, 069, 070 |
| OBJ-028 | spatial | high | verified | — | 006 | — |
| OBJ-029 | spatial | high | verified | — | 006 | 060 |
| OBJ-030 | spatial | high | verified | — | 006 | 062 |
| OBJ-031 | spatial | high | verified | — | 006 | 059–063, 065, 066 |
| OBJ-032 | spatial | medium | verified | — | 006 | — |
| OBJ-033 | spatial | medium | verified | — | 006 | — |
| OBJ-034 | spatial | medium | verified | — | 006 | — |
| OBJ-035 | engine | critical | verified | — | 009, 012, 013, 016 | 036, 046–048, 058–066, 068, 069, 073, 074, 077, 082, 083 |
| OBJ-036 | engine | critical | verified | — | 035, 005, 008 | 037 |
| OBJ-037 | engine | high | verified | — | 036, 008 | 068, 077 |
| OBJ-038 | engine | high | verified | — | 009, 014, 016 | 077, 078 |
| OBJ-039 | engine | high | verified | — | 010, 005, 015, 011 | — |
| OBJ-040 | spatial | high | verified | — | 005, 006, 003, 015 | 069 |
| OBJ-041 | spatial | high | verified | — | 005, 006 | 069 |
| OBJ-042 | spatial | medium | verified | — | 005, 010 | — |
| OBJ-043 | spatial | medium | verified | — | 010, 012 | — |
| OBJ-044 | spatial | medium | verified | — | 005, 004, 010 | — |
| OBJ-045 | spatial | medium | verified | — | 005, 006, 004 | — |
| OBJ-046 | engine | high | verified | — | 035 | 050, 070, 075, 077 |
| OBJ-047 | engine | high | verified | — | 035 | 055 |
| OBJ-048 | engine | high | verified | — | 016, 035 | — |
| OBJ-049 | engine | high | verified | — | 012 | 050, 074 |
| OBJ-050 | integration | medium | verified | — | 046, 049 | — |
| OBJ-051 | integration | medium | verified | — | 007 | 054, 072 |
| OBJ-052 | integration | medium | verified | — | 015 | 057 |
| OBJ-053 | integration | medium | verified | — | 007 | 054 |
| OBJ-054 | integration | medium | verified | — | 053, 051 | 057, 076 |
| OBJ-055 | integration | medium | verified | — | 047 | 057 |
| OBJ-056 | integration | medium | verified | — | 004, 071 | 057 |
| OBJ-057 | integration | medium | verified | — | 054, 052, 055, 056 | 078 |
| OBJ-058 | integration | high | verified | — | 035 | 059–066, 068 |
| OBJ-059 | tuning | medium | approved | needs_tuning | 018, 026, 027, 031, 035, 058 | 067 |
| OBJ-060 | tuning | medium | approved | needs_tuning | 019, 026, 029, 031, 035, 058 | 067 |
| OBJ-061 | tuning | medium | approved | needs_tuning | 020, 026, 027, 031, 035, 058 | 067 |
| OBJ-062 | tuning | medium | approved | needs_tuning | 021, 030, 031, 035, 058 | 067 |
| OBJ-063 | tuning | medium | approved | needs_tuning | 022, 026, 027, 031, 035, 058 | 067 |
| OBJ-064 | tuning | medium | approved | needs_tuning | 023, 026, 027, 035, 058 | 067 |
| OBJ-065 | tuning | medium | approved | needs_tuning | 024, 026, 031, 035, 058 | 067 |
| OBJ-066 | tuning | medium | approved | needs_tuning | 025, 026, 031, 035, 058 | 067 |
| OBJ-067 | tuning | medium | approved | needs_tuning | 059–066 | 078 |
| OBJ-068 | tuning | medium | approved | needs_tuning | 037, 035, 058 | 078 |
| OBJ-069 | tuning | high | approved | needs_tuning | 018, 027, 040, 041, 035 | — |
| OBJ-070 | integration | high | verified | — | 004, 046, 018, 027 | 071, 072, 075 |
| OBJ-071 | integration | high | verified | — | 070, 005, 006, 018, 019 | 056 |
| OBJ-072 | integration | medium | verified | — | 070, 051 | — |
| OBJ-073 | integration | high | verified | — | 035 | — |
| OBJ-074 | integration | high | verified | — | 035, 049 | — |
| OBJ-075 | integration | high | verified | — | 070, 046 | — |
| OBJ-076 | integration | medium | verified | — | 054 | — |
| OBJ-077 | integration | high | verified | — | 035, 046, 037, 038 | 078 |
| OBJ-078 | integration | high | verified | — | 077, 067, 068, 057, 038 | — |
| OBJ-079 | spatial | low | verified | — | 006, 002 | — |
| OBJ-080 | spatial | low | verified | — | 005 | — |
| OBJ-081 | spatial | low | verified | — | 010, 005 | — |
| OBJ-082 | engine | low | verified | — | 010, 035 | — |
| OBJ-083 | engine | low | verified | — | 035, 013 | — |
