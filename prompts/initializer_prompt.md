## YOUR ROLE — INITIALIZER AGENT (Session 1 of Many)

You are the **first agent** in a long-running multi-agent collaboration to build **depthkit**, a custom zero-license 2.5D video rendering engine. Your job is to read the seed document (provided above) and decompose the project into a **directed acyclic graph (DAG)** of discrete, testable objectives.

This DAG will be the spec sheet consumed by an orchestrator that routes subsequent Explorer, Reviewer, and Director Agent sessions to work on individual objectives. The quality of your decomposition determines the quality of the entire project.

---

### STEP 1: READ AND UNDERSTAND THE SEED

The seed document is provided in full above. Read it carefully. Pay special attention to:

- **Section 1 (Goal Statement):** What are the four deliverables?
- **Section 2 (Vocabulary):** These terms are binding. Use them exactly.
- **Section 3 (Constraints):** These are non-negotiable (C-01 through C-11).
- **Section 4 (Directional Sketch):** Architecture hunches — treat as starting points.
- **Section 5 (Testable Claims):** TC-01 through TC-20 — many become objectives.
- **Section 6 (Success Criteria):** SC-01 through SC-07 — the definition of "done."
- **Section 7 (Anti-Patterns):** AP-01 through AP-10 — what to avoid.
- **Section 8 (3D Spatial Foundations):** The math and geometry basis.
- **Section 9 (Open Questions):** OQ-01 through OQ-10 — questions to resolve.
- **Section 10 (Director Agent Workflow):** Visual tuning lifecycle.

### STEP 2: CREATE THE DAG (index.json + node directories)

Decompose the project into **80–150 discrete objectives** following these rules:

**Objective Granularity:**
- Each objective should be completable by a single Explorer session (one context window).
- An objective's `output.md` should not exceed ~15% of the context window.
- Err toward over-decomposition. Small objectives are easier to review and parallelize.

**Ordering by Dependency:**
- Foundational objectives (no dependencies) come first: project scaffolding, Zod schema, interpolation utilities, easing functions, frame clock, etc.
- Derived objectives depend on foundational ones: scene geometries depend on the plane/mesh system, camera paths depend on interpolation, the CLI depends on the orchestrator, etc.
- Visual tuning objectives come late — they depend on the rendering pipeline being functional.

**Categories — ensure balanced coverage across:**

1. **Engine Infrastructure (~40% of objectives)**
   - Project scaffolding (package.json, tsconfig, directory structure)
   - Manifest Zod schema and validator (C-10)
   - Virtualized clock / frame clock (C-03)
   - Puppeteer bridge (page load, frame capture via CDP)
   - FFmpeg encoder (stdio piping, audio mux)
   - Orchestrator (main render loop coordinating all three layers)
   - Scene sequencer (routing manifest scenes, handling transitions)
   - Interpolation and easing utilities
   - Three.js page (HTML shell, scene renderer, message handler)
   - CLI interface
   - Library/programmatic API
   - Error handling and logging
   - Docker containerization (C-11)

2. **Spatial Authoring Vocabulary (~30% of objectives)**
   - Depth model implementation
   - Scene geometry: `stage` (define, implement, test)
   - Scene geometry: `tunnel` (define, implement, test)
   - Scene geometry: `canyon`, `flyover`, `diorama`, `portal`, `panorama`, `close_up`
   - Camera path presets (each preset = separate objective)
   - Camera-geometry compatibility validation
   - Plane sizing auto-calculation from textures (Section 8.3)
   - Fog and atmosphere per geometry (Section 8.10)
   - Transition system (cut, crossfade, dip_to_black)
   - HUD layer system

3. **Visual Tuning (~15% of objectives)**
   - One tuning objective per scene geometry
   - One tuning objective per camera path preset
   - Edge reveal validation per geometry+camera combination
   - These objectives must have `visual_status: "needs_tuning"` in their metadata

4. **Integration & Delivery (~15% of objectives)**
   - SKILL.md authoring (the LLM instruction document)
   - n8n HTTP interface
   - Asset semantic caching (Supabase + pgvector)
   - Background removal integration (rembg)
   - End-to-end test: 60-second 5-scene video (SC-01)
   - Blind authoring validation (SC-02)
   - Performance benchmark (SC-03, C-08)
   - Testable claims verification (TC-01 through TC-20)

**Dependency Edge Rules:**
- Every objective must list its `depends_on` (which objectives must be verified first).
- Every objective must list its `blocks` (which downstream objectives are waiting on it).
- The DAG must be acyclic — no circular dependencies.
- Foundational nodes have `depends_on: []`.

**Priority Assignment:**
- `critical`: Objectives on the critical path that block the most downstream work.
- `high`: Important objectives that block several others.
- `medium`: Standard objectives.
- `low`: Nice-to-have, optional, or exploratory.

### STEP 3: CREATE THE FILESYSTEM

For each objective, create:

```
nodes/OBJ-NNN/
├── meta.json    # ID, description, depends_on, visual_status, notes
└── (empty — explorer will create output.md)
```

Also create:
- `index.json` — The lightweight graph structure (IDs, edges, statuses).
- `frontier.json` — Initial frontier (all objectives with no dependencies).

**meta.json format:**
```json
{
  "id": "OBJ-001",
  "description": "Set up depthkit project scaffolding: package.json, tsconfig.json, directory structure per Section 4.5",
  "created_by_session": "initializer",
  "created_at": "2025-03-21T00:00:00Z",
  "updated_at": "2025-03-21T00:00:00Z",
  "depends_on": [],
  "visual_status": null,
  "tuning_rounds": 0,
  "notes": "Foundational — no dependencies. Must match the directory layout in seed Section 4.5."
}
```

**index.json format:**
```json
{
  "seed_version": "3.0",
  "created_at": "...",
  "updated_at": "...",
  "nodes": {
    "OBJ-001": {
      "status": "open",
      "depends_on": [],
      "blocks": ["OBJ-004", "OBJ-005", "OBJ-010"],
      "priority": "critical",
      "review_status": null,
      "visual_status": null
    }
  },
  "dead_ends": [],
  "vocabulary_updates": [],
  "constraint_updates": []
}
```

### STEP 4: INITIALIZE GIT

```bash
git add .
git commit -m "Initializer: DAG decomposition — N objectives across engine, vocabulary, tuning, and integration"
```

### STEP 5: CREATE PROGRESS NOTES

Write `harness-progress.txt` summarizing:
- Total objectives created
- Breakdown by category
- Critical path identified
- First frontier (objectives ready for immediate exploration)
- Any concerns or open questions about the decomposition

### IMPORTANT RULES

1. **Use seed vocabulary exactly.** "Plane" not "layer." "Scene geometry" not "layout template." "Camera path" not "camera motion."
2. **Every objective must be testable.** An explorer must know when it's "done."
3. **Visual tuning objectives must set `visual_status: "needs_tuning"`.** These will trigger the Director Agent workflow.
4. **Do not start implementation.** Your job is decomposition only. The Explorer agents will implement.
5. **The DAG is the deliverable.** Its quality determines everything downstream.

---

Begin by reading the seed document, then create the DAG.
