# Depthkit Multi-Agent Harness

A deliberation-structured harness that decomposes the **depthkit** seed document into a directed acyclic graph (DAG) of specification objectives through **two-agent conversations**, then produces peer-reviewed specs for each objective.

Every decision — how many objectives, what each objective covers, what the spec should say — emerges from a conversation between two Claude instances with complementary roles (proposer + challenger). Nothing is hardcoded.

The output DAG (`index.json` + node directories) is the **spec sheet** for a downstream execution harness that builds the actual software.

## How It Works

### Phase 1: Initialization Deliberation

Two architects converse to discover the project decomposition:

- **Architect A** (proposer) analyzes the seed and proposes objective boundaries, dependency edges, and priorities.
- **Architect B** (challenger) stress-tests the proposal — finds missing coverage, granularity problems, dependency errors, and scope gaps.
- They alternate for 6 rounds (configurable). The number of objectives is **not predetermined** — it emerges from their conversation.
- The final round commits the agreed DAG to disk.

### Phase 2: Exploration Deliberation (per objective)

For each objective, two agents converse to produce its specification:

- **Spec Author** (proposer) drafts the spec: interface contracts, design decisions, acceptance criteria, edge cases, test strategy.
- **Spec Challenger** (adversarial reviewer) finds gaps, ambiguities, constraint violations, and downstream incompatibilities. Every criticism includes a proposed fix.
- They alternate for 4 rounds (configurable). The Challenger's adversarial pressure is built into the conversation — there is no separate review pass.
- The final round writes the agreed spec to `output.md`.

### Phase 3: Integration + Synthesis

- **Integrator** (monologue) periodically samples verified nodes to check for drift and inconsistency.
- **Synthesizer** (monologue) assembles verified specs into consolidated deliverables.

## Watching Conclusions Live

Every deliberation appends its conclusion to `feed.md` the moment it finishes. Watch in real-time:

```bash
tail -f generations/depthkit/feed.md
```

Each entry shows: timestamp, objective ID, participants, round count, conclusion summary, and links to the full transcript and spec. You can check in at any point during the run without reading everything at once.

## Agent Roles

| Role | Type | Purpose |
|------|------|---------|
| **Architect A** | Deliberation pair | Proposes project decomposition |
| **Architect B** | Deliberation pair | Challenges decomposition |
| **Spec Author** | Deliberation pair | Proposes specification per objective |
| **Spec Challenger** | Deliberation pair | Challenges specification |
| **Integrator** | Monologue | Periodic coherence check across DAG |
| **Synthesizer** | Monologue | Assembles verified specs into deliverables |
| **Director** | Gemini (future) | Visual feedback on renders (HITL-gated) |

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set CLAUDE_CODE_OAUTH_TOKEN

# Run the harness
python main.py --project-dir ./depthkit

# In another terminal, watch conclusions arrive:
tail -f generations/depthkit/feed.md
```

For testing:
```bash
python main.py --project-dir ./depthkit --max-iterations 3
```

## Timing Expectations

- **Initialization deliberation:** 30–60 minutes (6 rounds, each a full SDK session).
- **Explore deliberation per objective:** 15–30 minutes (4 rounds).
- **Full DAG:** Many hours across all objectives. The number of objectives is discovered during initialization — typically 80–150 for a project of depthkit's scope.

## Project Structure

```
depthkit-harness/
├── main.py                    # CLI entry point
├── orchestrator.py            # Lifecycle: init deliberation → explore loop → synthesis
├── agent.py                   # run_deliberation + run_session + feed
├── client.py                  # Role-pair system prompts
├── context.py                 # Shared context assembly per deliberation type
├── dag.py                     # DAG operations (index, frontier, nodes)
├── security.py                # Bash command allowlist
├── requirements.txt
├── .env.example
├── prompts/
│   ├── seed.md                # The depthkit seed document (v3.0)
│   ├── architect_a_prompt.md  # Init deliberation: proposer
│   ├── architect_b_prompt.md  # Init deliberation: challenger
│   ├── spec_author_prompt.md  # Explore deliberation: proposer
│   ├── spec_challenger_prompt.md  # Explore deliberation: challenger
│   ├── integrator_prompt.md   # Coherence check (monologue)
│   └── synthesizer_prompt.md  # Assembly (monologue)
└── generations/
    └── depthkit/              # Output
        ├── seed.md
        ├── index.json
        ├── frontier.json
        ├── feed.md            # ← Watch this with tail -f
        ├── nodes/
        │   ├── OBJ-001/
        │   │   ├── meta.json
        │   │   ├── output.md      # The specification
        │   │   ├── transcript.md  # Full deliberation conversation
        │   │   └── reviews/
        │   └── ...
        ├── dead_ends/
        ├── sessions/
        ├── synthesis/
        └── .git
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Output directory | `./depthkit` |
| `--max-iterations` | Max explore deliberations | Unlimited |
| `--model` | Claude model | `claude-sonnet-4-5-20250929` |
| `--init-rounds` | Architect A/B conversation rounds | 6 |
| `--explore-rounds` | Author/Challenger rounds per objective | 4 |
| `--auto-continue-delay` | Seconds between sessions | 3 |
| `--integrator-cadence` | Integrator every N explorations | 15 |

## What This Produces vs. What Builds the Software

This harness produces **specifications** — a DAG where each node's `output.md` is a design document (interfaces, contracts, acceptance criteria). It does not produce code.

A separate downstream execution harness reads the DAG and implements each spec. You can review, edit, add to, or remove from the DAG before handing it to the execution harness. The DAG is yours to customize.

## Resuming

```bash
# Ctrl+C to pause at any time
# Same command to resume — picks up where it left off
python main.py --project-dir ./depthkit
```

Progress persists via `index.json`, `frontier.json`, node directories, `feed.md`, and git commits.
