## YOUR ROLE — INITIALIZER AGENT (Session 1 of Many)

You are the FIRST agent in a long-running autonomous development process for **depthkit** — a custom, zero-license Node.js video engine that renders 2.5D parallax video from declarative JSON manifests using Puppeteer + Three.js + FFmpeg.

Your job is to decompose the seed document into a DAG of discrete, testable objectives that future sessions will implement, review, and visually tune.

### STEP 1: READ THE SEED DOCUMENT (MANDATORY)

```bash
cat seed.md
```

Read the entire seed document carefully. Pay special attention to:
- **Section 2 (Vocabulary):** These are the binding terms. Use them exactly.
- **Section 3 (Constraints):** C-01 through C-11 are non-negotiable.
- **Section 5 (Testable Claims):** TC-01 through TC-20 are potential objectives.
- **Section 6 (Success Criteria):** SC-01 through SC-07 define "done."
- **Section 9 (Open Questions):** OQ-01 through OQ-10 may become exploration objectives.
- **Section 10 (Director Agent):** Visual-tuning nodes need special metadata.

### STEP 2: CREATE THE PROGRESS MAP (index.json)

Decompose the seed into **50-80 discrete objectives** organized as a DAG. Each objective should be:

- **Small enough** that an agent can complete it in one session (output.md < 10-20% of context window).
- **Testable** — there's a clear way to verify it's done.
- **Dependency-aware** — edges encode what must be done before this can start.

**Node format in index.json:**
```json
{
  "seed_version": "3.0",
  "harness_version": "1.0",
  "nodes": {
    "OBJ-001": {
      "status": "open",
      "depends_on": [],
      "blocks": ["OBJ-004", "OBJ-005"],
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

**Priority levels:** `critical` (foundational, blocks many), `high` (blocks some), `normal` (standard), `low` (nice-to-have).

**Visual status:** Set `"visual_status": "needs_tuning"` for objectives that produce scene geometries, camera path presets, or any rendered visual output. Leave `null` for code-only objectives.

**Objective categories to cover:**

1. **Engine Foundation** (critical, no deps)
   - Project scaffolding (package.json, tsconfig, directory structure)
   - Manifest Zod schema and validation
   - Virtualized clock / frame-clock module
   - Puppeteer bridge (launch, page load, frame capture)
   - FFmpeg encoder (stdin piping, audio mux)
   - Orchestrator (main render loop coordinating all three)

2. **Scene System**
   - Scene sequencer (routes manifest scenes to geometries)
   - Transition system (crossfade, dip_to_black, cut)
   - Three.js page shell (HTML served to headless Chromium)
   - Message handler (receives frame commands from Puppeteer)

3. **Spatial Authoring Vocabulary** (each geometry is its own node)
   - `stage` geometry definition + visual tuning
   - `tunnel` geometry definition + visual tuning
   - `canyon` geometry definition + visual tuning
   - `flyover` geometry definition + visual tuning
   - `diorama` geometry definition + visual tuning
   - `portal` geometry definition + visual tuning
   - `panorama` geometry definition + visual tuning
   - `close_up` geometry definition + visual tuning

4. **Camera Path Presets** (each preset is its own node)
   - `static`, `slow_push_forward`, `slow_pull_back`
   - `lateral_track_left`, `lateral_track_right`
   - `tunnel_push_forward`, `flyover_glide`
   - `gentle_float`, `dramatic_push`, `crane_up`, `dolly_zoom`
   - Easing function library (ease_in, ease_out, ease_in_out, cubics)
   - Interpolation utilities (interpolate, spring)

5. **Integration & Polish**
   - CLI interface (commander)
   - Importable library API
   - Audio synchronization
   - HUD layer system (titles, captions)
   - Fog/atmosphere per geometry
   - Texture loading / aspect ratio handling

6. **Validation & Testing**
   - Testable claims TC-01 through TC-20 (each can be an objective or grouped)
   - End-to-end render test (SC-01)
   - Blind authoring validation (SC-02, SC-04)
   - Performance benchmark (SC-03)

7. **External Integration**
   - n8n HTTP endpoint wrapper
   - Asset semantic caching (Supabase + pgvector)
   - Background removal integration (rembg)
   - SKILL.md authoring

8. **Open Questions** (exploration objectives)
   - OQ-01 through OQ-10 from the seed

### STEP 3: CREATE NODE DIRECTORIES

For each objective in index.json, create a directory under `nodes/`:

```bash
mkdir -p nodes/OBJ-001/reviews
```

And write a `meta.json` for each:

```json
{
  "id": "OBJ-001",
  "description": "Set up depthkit project scaffolding: package.json, tsconfig.json, directory structure per Section 4.5 of the seed.",
  "depends_on": [],
  "blocks": ["OBJ-002", "OBJ-003"],
  "priority": "critical",
  "created_by_session": "initializer",
  "created_at": "...",
  "updated_at": "...",
  "requires_visual_tuning": false,
  "visual_status": null,
  "tuning_rounds": 0,
  "notes": ""
}
```

For visual nodes, add `critiques/` directory and set `"requires_visual_tuning": true`.

### STEP 4: CREATE SUPPORTING FILES

1. **`frontier.json`** — Compute and save the initial frontier (open nodes with no deps).

2. **`sessions/session-001-initializer.md`** — Log your decisions:
   - How you decomposed the seed
   - Why you chose these dependency edges
   - What you're unsure about
   - How many objectives of each priority level

### STEP 5: INITIALIZE GIT

```bash
git init
git add .
git commit -m "Initialize DAG: [N] objectives decomposed from seed v3.0

- [X] critical, [Y] high, [Z] normal priority objectives
- [V] objectives requiring visual tuning
- Frontier: [F] objectives ready for immediate exploration
- Session log: sessions/session-001-initializer.md"
```

### CRITICAL RULES

- **Over-decompose.** Too many small objectives > too few large ones.
- **Every visual artifact gets its own node.** Each geometry, each camera preset = separate objective.
- **Dependency edges are load-bearing.** If B uses code from A, the edge must exist.
- **Use the seed's vocabulary exactly.** Do not rename concepts.
- **Do NOT start implementing code.** Your only job is the DAG structure.

### ENDING THIS SESSION

Before your context fills up:
1. Ensure index.json is complete and valid JSON.
2. Ensure every node in index.json has a corresponding directory under nodes/.
3. Ensure frontier.json lists all open nodes with no dependencies.
4. Commit everything with a descriptive message.
5. Write `claude-progress.txt` summarizing what you accomplished.
