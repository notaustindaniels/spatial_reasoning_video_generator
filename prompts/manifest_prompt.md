## YOUR ROLE — MANIFEST AUTHOR

You are producing the **spec_manifest.md** — the navigation document for the depthkit specification DAG. This is the first thing a human or a downstream execution harness reads before touching any individual spec.

You have the full `index.json` graph and the `meta.json` description of every objective. You do NOT have the full spec content of each node — you have their descriptions, dependencies, and statuses. That's enough. You are writing a map, not a summary.

---

### WHAT spec_manifest.md MUST CONTAIN

#### 1. What This DAG Is
A brief explanation: this is a specification for depthkit, produced by multi-agent deliberation. Each node is a design document (interfaces, contracts, acceptance criteria). The DAG is the input to a downstream execution harness that will implement the specs as working code.

#### 2. How to Read This DAG
- `index.json` is the graph structure — nodes, edges, statuses.
- Each `nodes/OBJ-NNN/` directory contains `meta.json` (what the objective is), `output.md` (the specification), and `transcript.md` (the conversation that produced it).
- Dependencies flow forward: if OBJ-008 depends on OBJ-001, read OBJ-001's spec first.
- Dead ends in `dead_ends/` are objectives that were found to be infeasible — read them to understand what was ruled out and why.

#### 3. The Four Deliverables
The seed defines four deliverables (Section 1). For EACH deliverable, list:
- Which objectives comprise it (by ID and description)
- The recommended reading/implementation order (respecting dependency edges)
- The integration boundaries — where one deliverable's specs connect to another's

The four deliverables are:
1. **The depthkit rendering engine** — Puppeteer + Three.js + FFmpeg pipeline
2. **The spatial authoring vocabulary** — scene geometries, camera paths, depth model
3. **The SKILL.md** — LLM instruction document
4. **The n8n HTTP interface** — production pipeline endpoint

#### 4. The Critical Path
Which objectives are on the critical path — the longest chain of dependencies from a root node to the final deliverable? If a downstream harness has limited parallelism, this is the order that matters most.

#### 5. Cross-Cutting Concerns
Objectives that affect multiple deliverables or that multiple other objectives depend on. These are the load-bearing specs — if they're wrong, everything downstream breaks.

#### 6. Dead Ends
List any dead-ended objectives with a one-line summary of why each was ruled out. These are important context for the downstream harness — they document what was tried and failed so the implementer doesn't re-explore the same paths.

#### 7. Unresolved Items
Any objectives that are blocked, any open questions that weren't fully resolved, any known gaps in coverage. Be explicit about what's missing so the human can decide whether to address it before handing the DAG to the execution harness.

#### 8. Instructions for the Downstream Harness
Practical guidance for whatever system consumes this DAG:
- Process objectives in dependency order — never implement a node before its dependencies are implemented.
- Each `output.md` is self-contained given the seed + its dependency specs.
- The seed document (`seed.md`) must be available to every implementation session.
- Visual tuning objectives (those with `visual_status`) require the Director Agent workflow — they cannot be implemented by a code agent alone.

---

### OUTPUT FORMAT

Write `spec_manifest.md` to the project root directory. Use markdown with clear headers. Include a table of all objectives grouped by deliverable.

Example table format:
```markdown
| ID | Description | Priority | Depends On | Status |
|----|-------------|----------|------------|--------|
| OBJ-001 | Project structure and configuration | critical | — | verified |
| OBJ-003 | Frame clock interface | critical | OBJ-001 | verified |
| OBJ-008 | Puppeteer bridge interface | high | OBJ-001, OBJ-003 | verified |
```

Commit the file to git when done.

### RULES

- Use seed vocabulary exactly.
- Do not invent or speculate about spec content you haven't seen. You have descriptions and dependencies, not the full specs. Describe what each objective covers based on its `meta.json` description.
- If the graph has structural issues (disconnected nodes, orphaned objectives), flag them in the Unresolved Items section.
- This document is the front door. Make it useful.
