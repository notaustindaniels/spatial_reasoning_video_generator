# Depthkit Multi-Agent Harness

A peer-review-structured autonomous coding harness that decomposes the **depthkit** seed document into a DAG of testable objectives, then uses multiple agent roles to explore, review, visually tune, and converge on a production-quality 2.5D parallax video engine.

## Architecture

This harness implements the **Multi-Agent Seed Harness v2** framework:

- **Seed-Driven Coherence** — The seed document (`seed_v3.md`) provides binding vocabulary, constraints, testable claims, and success criteria. Every agent session loads it.
- **Multi-Agent Peer Review** — Explorer output is reviewed by independent Reviewer sessions with decorrelated blind spots.
- **DAG-Structured Progress** — Objectives are tracked as nodes in a directed acyclic graph. Each node is a directory containing metadata, output, reviews, and (for visual nodes) test renders and critiques.
- **Director Agent (Gemini)** — For visual-output objectives, Google Gemini reviews raw MP4 test renders and provides timestamped, directional feedback under a strict Human-in-the-Loop circuit breaker.

## Agent Roles

| Role | Purpose | Model |
|------|---------|-------|
| **Initializer** | Decomposes seed into DAG of 50-80 objectives | Claude |
| **Explorer** | Implements one objective per session | Claude |
| **Reviewer** | Independent peer review with constructive critique | Claude |
| **Director** | Visual tuning via multimodal video review (HITL gated) | Gemini |
| **Integrator** | Periodic coherence check across verified nodes | Claude |
| **Synthesizer** | Assembles verified nodes into final deliverable | Claude |

## Prerequisites

```bash
# Python 3.10+
python --version

# Install dependencies
pip install -r requirements.txt

# Install Claude Code CLI (latest)
npm install -g @anthropic-ai/claude-code
```

## Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Set your Claude Code OAuth token (REQUIRED)
#    Get it from: https://console.anthropic.com/
echo 'CLAUDE_CODE_OAUTH_TOKEN=your-token-here' >> .env

# 3. Optionally set Gemini API key for visual tuning
#    Get it from: https://aistudio.google.com/apikey
echo 'GEMINI_API_KEY=your-key-here' >> .env
```

## Quick Start

```bash
# Start from scratch — initializes DAG, then loops through explore → review → tune
python main.py --seed ./seed_v3.md

# Limit iterations for testing
python main.py --seed ./seed_v3.md --max-iterations 3

# Run only the initializer (decompose seed into DAG)
python main.py --seed ./seed_v3.md --role initializer --max-iterations 1

# Target a specific objective
python main.py --seed ./seed_v3.md --role explorer --node OBJ-005

# Force a review pass
python main.py --seed ./seed_v3.md --role reviewer --node OBJ-005

# Continue existing project
python main.py --seed ./seed_v3.md --project-dir generations/seed_v3
```

## How It Works

### Phase 1: Initialization

The initializer reads `seed_v3.md` and decomposes it into 50-80 discrete objectives organized as a DAG in `index.json`. Each objective gets its own directory under `nodes/` with a `meta.json` describing what needs to be built, its dependencies, and its priority.

### Phase 2: Explore → Review Loop

The orchestrator picks the highest-priority frontier objective (open, all deps satisfied), runs an Explorer session to implement it, then triggers a Reviewer session for independent peer review. Approved objectives are marked `verified`; rejected objectives go back for revision.

### Phase 3: Visual Tuning (HITL-Gated)

For objectives that produce visual output (scene geometries, camera presets), the approved node enters a Director Agent loop:

1. Explorer renders a test clip → `test_render.mp4`
2. Gemini reviews the video and produces a Visual Critique
3. **Human reviews and approves/modifies/rejects the critique** (HITL Circuit Breaker)
4. Explorer applies approved feedback and re-renders
5. Loop until human signs off → node marked `"visual_status": "tuned"`

### Phase 4: Convergence

When all objectives are verified (and visual ones tuned), the Synthesizer assembles the verified outputs into the final depthkit engine.

## Project Structure

```
depthkit-harness/
├── main.py                  # Entry point
├── orchestrator.py          # Session dispatch loop
├── client.py                # Claude SDK client factory
├── security.py              # Bash command allowlist
├── prompts_loader.py        # Prompt template loading + context assembly
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── dag/
│   ├── index.py             # Progress map (index.json) management
│   ├── frontier.py          # Frontier computation and objective claiming
│   └── nodes.py             # Per-node directory operations + context assembly
├── roles/
│   ├── session.py           # Claude Code SDK session runner
│   └── director.py          # Gemini visual tuning + HITL gate
└── prompts/
    ├── initializer_prompt.md
    ├── explorer_prompt.md
    ├── reviewer_prompt.md
    ├── integrator_prompt.md
    ├── synthesizer_prompt.md
    └── director_prompt.md
```

### Generated Project Structure (after initialization)

```
generations/seed_v3/
├── seed.md                  # Copy of the seed document
├── index.json               # DAG structure: IDs, edges, statuses
├── frontier.json            # Materialized work queue
├── claude-progress.txt      # Session progress notes
├── nodes/
│   ├── OBJ-001/
│   │   ├── meta.json        # Objective metadata
│   │   ├── output.md        # Work product
│   │   └── reviews/
│   │       └── REV-001.md
│   ├── OBJ-002/             # (visual-tuning node)
│   │   ├── meta.json
│   │   ├── output.md
│   │   ├── test_render.mp4
│   │   ├── critiques/
│   │   │   └── VC-001.md
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
| `--seed` | Path to seed document | **Required** |
| `--project-dir` | Project directory | `generations/<seed_name>` |
| `--max-iterations` | Max agent sessions | Unlimited |
| `--model` | Claude model | `claude-sonnet-4-5-20250929` |
| `--role` | Force a specific role | Auto-detected |
| `--node` | Target a specific node | Auto-selected from frontier |
| `--max-turns` | Max turns per session | 1000 |
| `--integrator-cadence` | Integrator frequency | Every 15 explorer completions |

## Key Design Decisions

**Why a DAG, not a linear task list?** Dependencies between objectives are load-bearing. A linear list can't express "the tunnel geometry depends on the interpolation utilities" or "the CLI depends on the manifest schema." The DAG encodes these relationships and ensures objectives are worked on in the right order.

**Why per-node directories instead of one big JSON file?** At scale, a monolithic file creates contention (parallel agents writing to the same file), wastes context (every session loads irrelevant nodes), and produces painful merge conflicts. The filesystem IS the distributed memory.

**Why the HITL Circuit Breaker?** Two AI agents giving each other aesthetic feedback will chase each other into increasingly bizarre parameter space. The human grounds the loop. This is a hard constraint, not a guideline.

**Why Gemini for the Director?** Gemini processes raw video as a first-class input — no frame extraction, no montages, no screenshots. It perceives temporal motion quality (easing, momentum, settling) that frame-by-frame analysis misses.

## Timing Expectations

- **Initializer session:** 5-15 minutes (generating 50-80 objective descriptions)
- **Explorer session:** 5-20 minutes per objective
- **Reviewer session:** 3-10 minutes per review
- **Director loop:** 5-15 minutes per tuning round (plus human review time)
- **Full convergence:** Many hours across dozens of sessions

## Resuming After Interruption

The harness is designed for interruption and resumption. All state is in the filesystem (index.json + node directories) and git. To resume:

```bash
python main.py --seed ./seed_v3.md --project-dir generations/seed_v3
```

The orchestrator reads the current DAG state and picks up where it left off.

## License

Internal use.
