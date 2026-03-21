# The Multi-Agent Seed Harness — v2

**A general-purpose framework for autonomous AI collaboration on problems that exceed any single context window, any single session, and any single mind.**

**v2 Revision Note:** Adds the Director Agent role (Section 3.6) — powered by **Google Gemini** — used during development to provide visual feedback on rendered output, operating under a strict Human-in-the-Loop circuit breaker. Gemini's native multimodal video understanding allows the harness to pass raw MP4 test renders directly to the Director without frame extraction. This role is designed for domains where the primary coding agent cannot perceive the output it produces (e.g., video rendering, 3D scene composition, generative art).

---

## Part 1: What This Framework Is

This document describes a **harness architecture** — a method for orchestrating multiple AI agent instances (potentially different models, potentially the same model across sessions) to collaboratively explore, build, debate, refine, and converge on a solution to a complex problem.

The framework is seed-agnostic. It does not care whether the goal is building software, proving a theorem, designing a system, writing a book, or solving an open research question. It cares about the **shape of the collaboration** — how instances communicate, how progress persists, how disagreement generates value, and how the whole exceeds what any single instance could produce alone.

### 1.1 The Core Problem

Current AI agents operate within bounded context windows. A single session can hold roughly 100-200K tokens of working memory. Many worthwhile problems produce artifacts — codebases, proofs, designs, manuscripts — that exceed this by an order of magnitude or more. No single session can hold the whole.

The standard workaround is sequential handoff: session 1 does some work, writes a summary, session 2 reads the summary and continues. This works for linear tasks but fails for problems that require:

- **Exploration of multiple paths simultaneously.** A single sequential chain commits early and explores narrowly.
- **Genuine disagreement.** A single agent reviewing its own prior work has correlated blind spots. It tends to agree with itself.
- **Structural integrity across scale.** As the artifact grows, earlier decisions constrain later ones. A sequential chain has no mechanism to revisit early decisions in light of late discoveries — not without re-reading everything, which eventually exceeds the window.

The harness solves these problems by introducing three mechanisms that sequential handoff lacks: **multi-agent peer review**, **DAG-structured progress tracking**, and **seed-driven coherence**.

### 1.2 The Three Mechanisms

**Seed-Driven Coherence.** The harness begins with a **seed document** — a specification that fits within a single context window and provides everything an agent needs to orient itself and contribute meaningfully without reading the entire history. The seed provides:

- **Vocabulary.** The shared terminology that all agents use. This prevents drift — sessions using different words for the same concept, or the same word for different concepts.
- **Constraints.** The hard boundaries that all work must respect. These are the non-negotiable requirements, the laws of physics of the problem space.
- **Testable Claims.** Specific assertions that can be verified, refuted, or refined. These give each session a concrete objective rather than a vague direction.
- **Success Criteria.** What "done" looks like. Without this, the harness explores forever.
- **Directional Sketch.** A rough map of the solution space — not a detailed plan, but enough structure to prevent random walking. Intentionally open-ended so that agents can discover paths the seed author didn't anticipate.

**Multi-Agent Peer Review.** After an exploration session produces output, that output is reviewed by one or more independent agent instances — ideally different models or at minimum fresh context windows with no memory of producing the work. Reviewers evaluate:

- Is the reasoning sound?
- Are there gaps or unstated assumptions?
- Does this actually engage with the seed architecture, or has it drifted into tangential territory?
- Does it respect the constraints?
- Is any criticism **constructive** — does it name what should replace what it removes? (Critique without replacement is a gap, not a contribution.)

The value of peer review is not accuracy-checking alone. It is **decorrelating blind spots.** A single agent has systematic biases. Two agents have partially overlapping biases. Three agents using different models have substantially decorrelated biases. The disagreements between reviewers are often more informative than their agreements.

**DAG-Structured Progress.** As sessions accumulate, the harness builds a **directed acyclic graph** of results. Each node is a discrete unit of progress: a module built, a claim verified, a dead end documented, a dependency identified, a design decision made. Edges represent dependencies: "node B depends on node A" means B's validity requires A's. The DAG provides:

- **Visibility into what's blocking what.** If five nodes are waiting on one unresolved dependency, that dependency gets prioritized.
- **Safe parallel exploration.** Independent branches of the DAG can be explored by different sessions simultaneously without coordination.
- **Graceful handling of dead ends.** When a path fails, the DAG records it as a dead end — future sessions know not to re-explore it and can read *why* it failed.
- **The ability to exceed any single context window.** No session needs to hold the entire DAG. Each session reads the seed document plus the relevant subgraph of nodes for its current objective.

---

## Part 2: The Harness Lifecycle

### 2.1 Phase One — Initialization

The first session reads the seed document and generates the **progress map** — the initial structure that all subsequent sessions will build upon. The progress map is analogous to a `feature_list.json` in a coding harness, but generalized:

```
progress_map.json
{
  "seed_version": "2.0",
  "objectives": [
    {
      "id": "OBJ-001",
      "description": "...",
      "status": "open",           // open | in_progress | review | verified | blocked | dead_end
      "depends_on": [],            // IDs of prerequisite objectives
      "blocks": ["OBJ-004"],      // IDs of objectives waiting on this one
      "priority": "critical",      // critical | high | medium | low
      "assigned_session": null,
      "review_status": null,       // null | pending | approved | revision_needed
      "visual_status": null,       // null | needs_tuning | in_tuning | tuned (for geometry/camera objectives)
      "notes": ""
    }
  ],
  "dead_ends": [],
  "vocabulary_updates": [],
  "constraint_updates": []
}
```

The initializer session:

1. Reads the seed document.
2. Decomposes the goal into discrete, testable objectives ordered by dependency.
3. Identifies which objectives are **foundational** (no dependencies — can be started immediately) and which are **derived** (depend on foundational results).
4. Commits the progress map and any initial scaffolding.
5. Documents its reasoning in a `session_log.md` so reviewers can evaluate the decomposition itself.

### 2.2 Phase Two — Exploration Sessions

Each exploration session:

1. **Orients itself.** Reads the seed document and the current progress map. Does NOT attempt to read all prior session logs — only the ones relevant to its current objective.
2. **Selects an objective.** Picks the highest-priority open objective whose dependencies are satisfied. If multiple objectives are available, selects based on what would unblock the most downstream work.
3. **Explores.** Works on the objective. This might mean writing code, drafting a proof, designing a component, running an experiment, or producing any other artifact. The work is bounded by the session's context window — the agent should aim to complete a discrete, reviewable unit of work rather than attempting too much.
4. **Self-evaluates.** Before committing, the agent asks itself: Does this actually satisfy the objective? Does it respect the constraints? Have I made unstated assumptions? Would I approve this if I were reviewing someone else's work?
5. **Commits.** Updates the progress map (marks the objective as `review`), commits the artifact, and writes a session log documenting what was done, what decisions were made, and what open questions remain.

### 2.3 Phase Three — Peer Review

After an exploration session commits, the harness triggers one or more review sessions:

1. **Fresh context.** The reviewer loads the seed document, the progress map, and the specific artifact under review. The reviewer has NO memory of producing the artifact.
2. **Structural review.** Does the artifact satisfy its stated objective? Does it respect the seed's constraints? Does it engage with the seed's vocabulary or has it invented its own?
3. **Gap analysis.** What's missing? What assumptions are unstated? What edge cases are unhandled?
4. **Constructive critique.** If the reviewer identifies a problem, the review must include a proposed fix or alternative approach. Critique without replacement is flagged as incomplete.
5. **Verdict.** The reviewer marks the objective as `approved`, `revision_needed` (with specific revision instructions), or `blocked` (if a dependency has become invalid).

**Critical: reviewers can also challenge the progress map itself.** If a reviewer discovers that an objective is mis-specified, that a dependency is missing, or that the decomposition should be restructured, they can propose changes to the progress map. These meta-level contributions are often the most valuable.

### 2.4 Phase Four — Visual Tuning (Domain-Specific)

For objectives that involve scene geometries, camera path presets, or any artifact whose quality depends on visual perception, the harness triggers the **Director Agent workflow** after peer review approval:

1. **Render.** The Code Agent produces a short test render (10-30 seconds) and outputs `test_render.mp4`.
2. **Direct.** The orchestrator passes the raw MP4 file directly to the Gemini API. Gemini reviews the video natively (no frame extraction) and produces a Visual Critique — timestamped, directional feedback labeled "RECOMMENDED TWEAKS."
3. **Gate.** The Human reviews the Director's critique, modifies it if necessary, and explicitly approves it (the HITL Circuit Breaker).
4. **Adjust.** The Code Agent receives the human-approved feedback and adjusts parameters.
5. **Re-render.** Loop returns to step 1 until the Human signs off on the final render.
6. **Mark tuned.** The objective's `visual_status` is set to `"tuned"` in the progress map.

This phase is optional — it only applies to objectives that produce visual output. Code architecture, schema design, and pipeline integration objectives skip directly from peer review to verified status.

### 2.5 Phase Five — DAG Construction

As objectives are completed and reviewed, the progress map evolves into a richer structure:

- **Verified nodes** are objectives that have been completed and approved through peer review (and visual tuning, if applicable). These are the load-bearing results that downstream work can depend on.
- **Dead-end nodes** are paths that were explored and failed for documented reasons. Dead ends are as valuable as successes — they prevent future sessions from re-exploring the same failed path.
- **Blocking nodes** are objectives that multiple downstream objectives depend on. The harness prioritizes these.
- **Vocabulary updates** are refinements to the seed's terminology that emerged through exploration. These get propagated to the seed document itself — the seed is a living document that evolves with the harness.
- **Constraint updates** are newly discovered constraints that the original seed didn't anticipate. These also get propagated.

The DAG is the harness's memory — it is what allows the collaboration to exceed any single context window. No session needs to hold the entire DAG. Each session reads the seed plus the local neighborhood of the DAG relevant to its current objective.

### 2.6 Phase Six — Convergence

The harness converges when one of the following conditions is met:

- **Success.** The DAG connects a set of root nodes (foundational results) to a terminal node (the stated goal) through a complete chain of verified results. The goal has been achieved.
- **Documented impossibility.** The DAG reveals that all paths to the goal are blocked, and the pattern of blockages constitutes evidence that the goal cannot be achieved as specified. The harness documents *why* and *where* each path failed.
- **Scope revision.** The harness discovers through exploration that the original goal was mis-specified, and proposes a revised goal that is achievable. The seed is updated, the progress map is restructured, and the harness continues toward the revised goal.
- **Resource exhaustion.** The human operator decides the exploration has been sufficiently thorough. The harness produces a final summary of what was achieved, what remains open, and what the most promising unexplored paths are.

---

## Part 3: Agent Roles

The harness uses a small number of distinct agent roles. Each role has a specific prompt template and evaluation criteria.

### 3.1 The Initializer

**Runs once at the start.** Reads the seed document and produces the initial progress map. This is the most consequential single session — a bad decomposition cascades into wasted exploration sessions. The initializer should err toward over-decomposition (too many small objectives) rather than under-decomposition (too few large objectives), because small objectives are easier to review, easier to parallelize, and easier to mark as dead ends without losing much work.

### 3.2 The Explorer

**Runs repeatedly, one objective at a time.** The workhorse of the harness. Each explorer session picks an objective, works on it, and commits a discrete artifact. Explorers should be aggressive — they should attempt solutions, not just analyze problems. A failed attempt that documents *why* it failed is more valuable than a cautious analysis that identifies risks without testing them.

### 3.3 The Reviewer

**Runs after each exploration session.** Independent context, decorrelated blind spots. Reviewers are adversarial in the productive sense — they are looking for gaps, unstated assumptions, and structural weaknesses. But they are constructive: every identified weakness must come with a proposed fix or an alternative approach. A review that says "this is wrong" without saying "here's what would be right" is incomplete.

### 3.4 The Integrator

**Runs periodically to maintain coherence.** As the DAG grows, the integrator reads the seed document and a broad (but not exhaustive) sample of verified nodes to check for:

- **Drift.** Have recent sessions diverged from the seed's constraints or vocabulary?
- **Inconsistency.** Do two verified nodes contradict each other?
- **Missed connections.** Are there verified nodes that should be connected but aren't?
- **Seed staleness.** Does the seed document need updating to reflect what the harness has learned?

The integrator produces a **coherence report** and, if needed, proposes updates to the seed document or restructuring of the progress map.

### 3.5 The Synthesizer

**Runs at convergence or on request.** Takes the DAG of verified results and synthesizes them into a coherent final artifact — the deliverable that the human operator actually wants. The synthesizer does not produce new results; it assembles existing ones into their final form.

### 3.6 The Director Agent (Gemini)

**Runs during visual tuning phases only. Development tool, not a production component.**

The Director Agent addresses a fundamental limitation of text-based coding agents: they cannot see the output they produce. For domains where visual quality is the primary success criterion — video rendering, 3D scene composition, animation, generative art — the harness needs a way to close the gap between "structurally correct" and "cinematically compelling."

**Model: Google Gemini (multimodal).** The Director Agent is powered by Gemini, selected specifically for its **native multimodal video understanding**. Unlike vision models that can only analyze individual frames or image grids, Gemini can process raw video files as a first-class input modality. This is a critical architectural choice:

- **No frame extraction required.** The harness does not need to use FFmpeg to extract frame grids, stitch screenshot montages, or sample keyframes for the Director's review. The raw `test_render.mp4` file is passed directly to Gemini's API as a video input.
- **Temporal understanding.** Gemini can evaluate motion quality, easing curves, and camera physics across time — not just static composition. It can perceive whether a camera push "feels" linear vs. eased, whether a transition is jarring, and whether motion has appropriate momentum and deceleration.
- **The Director is selected for visual perception quality, not coding ability.** It does not need to write or understand Three.js code. It needs to watch a video and articulate what it sees in directional, temporal terms that the Code Agent (Claude) can translate into parameter adjustments.

**Evaluation capabilities.** The Director Agent specifically evaluates:
- **Temporal flow** — pacing, rhythm, scene-to-scene continuity, whether the video feels rushed or lethargic.
- **3D WebGL perspective projection** — whether planes at different Z-depths produce a convincing depth illusion, whether vanishing points read correctly, whether the tunnel/flyover/canyon geometry feels spatially coherent.
- **Camera easing and momentum** — whether camera motions feel organic or robotic, whether ease-in/ease-out curves simulate physical mass and inertia, whether the camera "settles" naturally at the end of a move.
- **Post-processing quality** — depth of field (bokeh), fog/atmosphere, whether blur targets the correct focal plane, whether fog enhances depth or obscures the subject.
- **Edge reveals and plane sizing** — whether camera motion exposes the edges of any textured plane, breaking the illusion.

**Invocation scope:** The Director Agent is invoked only for objectives that produce visual output requiring subjective quality evaluation:
- Tuning scene geometry parameters (plane positions, rotations, sizes).
- Tuning camera path presets (motion curves, easing, speed, trajectory).
- Validating edge safety (no planes reveal edges during camera motion).
- Final visual sign-off before a geometry/camera preset is marked as `"tuned"`.

The Director Agent is **never** invoked for code architecture, schema design, API integration, manifest validation, or any non-visual objective.

**The HITL Circuit Breaker — a hard constraint, not a guideline:**

Despite Gemini's advanced multimodal capabilities, the Director Agent operates under the same strict Human-in-the-Loop approval gate as any other subjective evaluator. Advanced perception does not equal infallible taste. Gemini may confidently recommend changes that a human director would reject — aesthetic judgment is not a solved problem in AI, and compounding AI-to-AI aesthetic feedback without human grounding is the fastest path to uncanny, overprocessed output.

The HITL constraint is **not relaxed** because the model is capable. It is **reinforced** because a more capable model produces more confident recommendations, which are more likely to be accepted uncritically if the human isn't actively reviewing them.

The workflow:

1. The Explorer (Code Agent) renders a short test clip (10-30 seconds) to `test_render.mp4`.
2. The orchestrator passes the raw MP4 file directly to the Gemini API as a video input, along with the Director's system prompt and the objective's description.
3. Gemini produces a **Visual Critique** labeled "RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL."
4. The Human reviews the critique and either: **(a)** approves as-is, **(b)** modifies and approves, **(c)** rejects entirely, or **(d)** overrides with their own notes.
5. Only human-approved feedback reaches the Code Agent.
6. The Code Agent adjusts parameters and re-renders.
7. The loop repeats until the Human signs off.

**Feedback philosophy — empathetic, directional, temporal:**

The Director Agent must empathize with the Code Agent's blindness. It does not prescribe code changes. It describes *what it sees* and *which direction* things should move, anchored to specific timestamps. The Code Agent — which understands its own parameter space intimately — translates directional feedback into parameter adjustments.

Guidelines for Director feedback:
- **Timestamp everything.** "At 00:14-00:18" not "generally."
- **Directional deltas.** "Needs more ease-in" not "change Bezier to 0.8."
- **Spatial descriptions.** "Push the background further back" not "set z = -45."
- **Physics and feel.** "Feels robotic — needs momentum" not "add spring physics."
- **Edge reveals.** "Right edge of sky visible at 00:22 — restrict X or scale plane."
- **Depth/focus.** "Blur hitting subject instead of background — focal distance mismatch."
- **Comparative language.** "Feels like a security cam, not a dolly — add subtle Y float."
- **Preserve what works.** Always note what should NOT change to prevent regression.
- **Temporal motion quality.** "The drone whip feels too linear — needs a sharper ease-out to simulate momentum and air resistance."
- **Perspective projection coherence.** "The floor plane's perspective distortion doesn't match the wall planes — they appear to converge at different vanishing points."

**What the Director Agent is NOT:**
- A code reviewer. It does not evaluate code quality, architecture, or implementation approach.
- A production component. It does not run during video generation at scale.
- An autonomous loop participant. It does not send feedback directly to the Code Agent.
- A replacement for human taste. It is a tool that helps the human articulate what they see.
- Infallible. Its advanced capabilities make its recommendations *more persuasive*, not *more correct*. The HITL gate exists precisely because confident-but-wrong feedback is the most dangerous kind.

---

## Part 4: Design Principles

### 4.1 The Seed Is a Living Document

The seed document evolves through the harness. Vocabulary gets refined. Constraints get updated. The directional sketch gets sharpened as exploration reveals which directions are productive and which are dead ends. However, changes to the seed must be explicitly proposed, reviewed, and documented — not silently drifted into. The seed's version history is part of the harness's record.

### 4.2 Intentional Openness

The seed provides vocabulary, constraints, and a directional sketch. It does **not** provide a step-by-step plan. This is deliberate. An over-specified seed turns explorers into lab technicians executing a protocol. An open seed turns them into researchers navigating a problem space. The openness is what allows the harness to discover solutions the seed author didn't anticipate.

The balance: constrain enough to prevent random walking, but leave enough open to enable genuine discovery. The constraints say "you must stay within this territory." The directional sketch says "this area looks promising." The explorer decides where to dig.

### 4.3 Constructive Opposition

Criticism within the harness must be **structural**: if you identify a weakness, you must propose what replaces it. This is not a rule of politeness — it is a rule of progress. An identified weakness without a proposed fix is a gap in the structure. The gap is the critic's responsibility as much as the original builder's.

This applies at every level:

- If a reviewer rejects an artifact, the review must include revision guidance.
- If an integrator identifies drift, the coherence report must include a proposed correction.
- If an explorer abandons an objective as a dead end, the session log must explain *why* it failed and *what approach might work instead*.
- If the Director Agent identifies a visual problem, the critique must describe the direction of the fix, not just the problem.

### 4.4 Dead Ends Are Progress

A well-documented dead end is as valuable as a successful result. It narrows the search space. It prevents future sessions from re-exploring the same failed path. It may reveal structural features of the problem that inform the next approach.

The harness should never treat dead ends as failures. They are verified negative results. The only true failure is an undocumented dead end — work that was done, failed, and left no record of why.

### 4.5 Scale Through Structure, Not Memory

The harness does not require any session to hold the entire project in memory. Each session reads the seed document (which fits in one context window) plus the local neighborhood of the DAG relevant to its current objective. The DAG's structure — its dependency edges, its blocking relationships, its dead-end markers — is what allows coherent progress at scale without global memory.

This is the fundamental insight: **the DAG is the distributed memory.** Each node is a bounded unit of verified work. The edges encode relationships between units. The whole structure can grow far beyond any single context window because no single session needs to see all of it — only the part that matters for the work at hand.

### 4.6 The Human Grounds Subjective Quality

For domains with subjective quality criteria (visual aesthetics, narrative quality, musical feel), the harness provides AI tools (like the Director Agent) to help the human articulate and communicate their judgment, but the human retains final authority. AI agents can identify problems, propose directions, and generate options, but the decision of "is this good enough" belongs to the human. The HITL Circuit Breaker is the structural embodiment of this principle.

---

## Part 5: The Seed Document Template

Every harness begins with a seed document. The seed should contain the following sections, adapted to the specific domain:

### Section 1: Goal Statement

What is the harness trying to produce? Be specific about the deliverable but open about the method. "Build a video rendering engine that accepts JSON scene manifests and outputs MP4 files" is good. "Build it using Sharp and FFmpeg with a specific module structure" is over-specified.

### Section 2: Vocabulary

Define the terms that all agents will use. This prevents drift and miscommunication across sessions. The vocabulary will evolve — that's expected — but starting with a shared lexicon is essential.

### Section 3: Constraints

The hard boundaries. Things that must be true of the final artifact regardless of how it's built. "Must run on Node.js 18+." "Must render 1080p video at 30fps." "Must handle 16:9 and 9:16 aspect ratios." Constraints are non-negotiable unless formally revised through the harness's review process.

### Section 4: Directional Sketch

A rough map of the solution space. Not a plan — a set of hunches, intuitions, and promising directions. "The depth model should probably use 5-7 canonical layers." "Camera motions should be parametric functions of frame number." "The compositor should use Sharp for image manipulation." The directional sketch explicitly invites the harness to deviate if exploration reveals a better path.

### Section 5: Testable Claims

Specific assertions that exploration sessions can verify or refute. "A 7-layer depth model is sufficient for visually convincing parallax." "Sharp can composite 4 PNG layers onto a 1920×1080 canvas in under 50ms per frame." "Eased camera motions feel more natural than linear ones." Each claim is a potential objective in the progress map.

### Section 6: Success Criteria

What does "done" look like? Be specific enough that the synthesizer knows when to stop, but flexible enough that the harness can adjust scope if exploration reveals the original criteria were mis-calibrated.

### Section 7: Anti-Patterns

What should the harness explicitly avoid? "Do not use a headless browser for rendering." "Do not require GPU acceleration." "Do not build a general-purpose video editor — this is a parallax engine." Anti-patterns prevent well-intentioned explorers from going down paths that are technically interesting but strategically wrong.

---

## Part 6: Implementation Notes

### 6.1 Orchestration

The harness needs an orchestration layer that:

- Manages the progress map (reads, updates, commits).
- Routes sessions to the appropriate role (initializer, explorer, reviewer, director, integrator, synthesizer).
- Triggers review sessions after exploration sessions commit.
- Triggers Director Agent sessions after visual-output objectives pass peer review.
- Enforces the HITL Circuit Breaker by gating Director feedback behind human approval.
- Tracks which objectives are open, blocked, verified, or tuned.
- Provides each session with the seed document plus the relevant DAG subgraph.

This orchestration can be implemented as a simple script (Python, TypeScript) that wraps the Claude Code SDK or the Anthropic API. The Anthropic autonomous coding demo provides a minimal reference implementation of the session management loop; the harness extends it with role differentiation, the DAG structure, and the Director Agent workflow.

### 6.2 Persistence

All state persists on disk:

- `seed.md` — The living seed document.
- `progress_map.json` — The DAG of objectives and their statuses (including `visual_status`).
- `sessions/` — A directory of session logs, one per session.
- `artifacts/` — The actual work products (code, documents, designs, etc.).
- `reviews/` — Review reports, linked to the sessions they review.
- `critiques/` — Visual Critiques from Director Agent sessions, linked to the objectives they evaluate.
- `renders/` — Test renders used for Director Agent review. Short clips, not full videos.
- `.git` — Version control over all of the above. Every session commits its work. The git log is the harness's audit trail.

### 6.3 Session Context Assembly

When launching a session, the orchestrator assembles its context:

1. **Always include:** The seed document.
2. **Always include:** The current progress map.
3. **Include if explorer:** The specific objective being worked on, plus any verified artifacts it depends on.
4. **Include if reviewer:** The artifact under review, plus the objective it claims to satisfy.
5. **Include if director:** The raw `test_render.mp4` file (passed directly to Gemini as a video input — no frame extraction needed), plus the objective's description and any prior Visual Critiques for context on what has already been addressed.
6. **Include if integrator:** A representative sample of recently verified nodes (breadth over depth).
7. **Never include:** The full session history. Sessions should be able to orient from the seed + progress map without reading every prior session log.

### 6.4 Human-in-the-Loop

The harness supports (but does not require) human participation at any point:

- **As seed author.** The human writes the initial seed document.
- **As reviewer.** The human reviews agent-produced artifacts, especially for subjective quality judgments that agents struggle with (visual aesthetics, narrative quality, etc.).
- **As HITL Circuit Breaker.** The human reviews and approves Director Agent visual feedback before it reaches the Code Agent. This role is **required** whenever the Director Agent is used — it is not optional.
- **As tiebreaker.** When agents disagree and the disagreement cannot be resolved through further exploration, the human decides.
- **As scope adjuster.** The human can revise the seed, reprioritize objectives, or call convergence.

---

## Summary

| Component | Role |
|---|---|
| Seed Document | Fits in one context window. Provides vocabulary, constraints, testable claims, success criteria, and a directional sketch. Living document that evolves with the harness. |
| Progress Map | DAG of objectives with statuses, dependencies, blocking relationships, and visual tuning status. The harness's distributed memory. |
| Initializer | Reads seed, produces initial progress map. Runs once. |
| Explorer | Picks an objective, works on it, commits a discrete artifact. The workhorse. |
| Reviewer | Independent context, adversarial-but-constructive evaluation. Decorrelates blind spots. |
| Director Agent | Gemini (multimodal) reviews raw test_render.mp4 files and provides timestamped, directional visual feedback on temporal flow, perspective projection, camera easing, and post-processing quality. Development-only. Operates under HITL Circuit Breaker. |
| Integrator | Periodic coherence check. Detects drift, inconsistency, and missed connections. |
| Synthesizer | Assembles verified results into the final deliverable. |
| Dead Ends | Documented failures that narrow the search space. As valuable as successes. |
| Constructive Opposition | All critique must propose a replacement. Critique without replacement is a gap, not a contribution. |
| HITL Circuit Breaker | Human approval gate between Director Agent and Code Agent. Prevents subjective hallucination loops. Required, not optional. |
| Convergence | The DAG connects roots to the goal through verified (and visually tuned) results — or documents why it can't. |

**This document is the meta-seed — the seed for building seeds. The vocabulary is roles and DAGs. The constraint is that the whole must exceed any single context window. The success criterion is a framework that works for any domain. The directional sketch is everything above. What grows from it is up to the harness.**
