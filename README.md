# Depthkit Multi-Agent Harness

A peer-review-structured harness that decomposes the **depthkit** seed document into a directed acyclic graph (DAG) of testable objectives, then uses a multi-agent loop (Explorer → Reviewer → Director) to build the engine incrementally.

The output DAG (`index.json` + node directories) serves as the **spec sheet** for a downstream execution harness.

## What is Depthkit?

Depthkit is a custom, zero-license Node.js video engine that renders 2.5D parallax videos. It uses **Puppeteer** to load a **Three.js** WebGL canvas in headless Chromium, deterministically steps through frames using a virtualized clock, and pipes pixel buffers into **FFmpeg** to produce MP4 output. The engine maps AI-generated 2D images onto flat mesh planes in 3D space, then moves a perspective camera through that scene to create real parallax depth effects.

## How the Harness Works

The harness implements the **Multi-Agent Seed Harness** architecture:

1. **Initialization** — The Initializer agent reads the seed document and decomposes the project into 80–150 discrete objectives, creating a DAG with dependency edges.

2. **Exploration** — Explorer agents pick objectives from the frontier (open objectives whose dependencies are satisfied) and implement them one at a time.

3. **Peer Review** — Reviewer agents evaluate each explorer's artifact in a fresh context window, checking for constraint compliance, vocabulary drift, and quality.

4. **Integration** — Integrator agents periodically sample verified nodes to check for drift, inconsistency, and missed connections across the growing DAG.

5. **Visual Tuning** (optional) — For scene geometry and camera path objectives, the Director Agent (Gemini) provides visual feedback on test renders, gated by human approval (HITL Circuit Breaker).

6. **Convergence** — When all objectives are verified (or documented as dead ends), the DAG is complete.

## Agent Roles

| Role | Model | Purpose |
|------|-------|---------|
| **Initializer** | Claude | Decomposes seed into DAG (runs once) |
| **Explorer** | Claude | Implements a single objective |
| **Reviewer** | Claude | Adversarial-but-constructive peer review |
| **Integrator** | Claude | Periodic coherence check across DAG |
| **Synthesizer** | Claude | Assembles verified results into deliverables |
| **Director** | Gemini | Visual feedback on renders (HITL-gated) |

## Prerequisites

**Required:**

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Install Python dependencies
pip install -r requirements.txt
```

**OAuth Token:**

```bash
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'
```

Or copy `.env.example` to `.env` and fill in your token.

## Quick Start

```bash
# Copy environment template
cp .env.example .env
# Edit .env — set CLAUDE_CODE_OAUTH_TOKEN

# Run the harness
python main.py --project-dir ./depthkit
```

For testing with limited iterations:

```bash
python main.py --project-dir ./depthkit --max-iterations 3
```

Skip peer review for faster iteration:

```bash
python main.py --project-dir ./depthkit --no-review
```

## Timing Expectations

- **Initialization (Session 1):** 10–30 minutes. The Initializer generates 80–150 objectives with full metadata. This may appear to hang — it's working.
- **Explorer sessions:** 5–15 minutes each, depending on objective complexity.
- **Reviewer sessions:** 3–8 minutes each.
- **Full DAG:** Building all objectives typically requires many hours across multiple sessions.

**Tip:** Use `--max-iterations 3` for a quick test run.

## Project Structure

```
depthkit-harness/
├── main.py                    # CLI entry point
├── orchestrator.py            # Main lifecycle loop
├── agent.py                   # Session runner for all roles
├── client.py                  # Claude SDK client configuration
├── context.py                 # Context assembly per role
├── dag.py                     # DAG operations (index, frontier, nodes)
├── security.py                # Bash command allowlist
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── prompts/
│   ├── seed.md                # The depthkit seed document (v3.0)
│   ├── initializer_prompt.md  # First session instructions
│   ├── explorer_prompt.md     # Explorer instructions
│   ├── reviewer_prompt.md     # Reviewer instructions
│   ├── integrator_prompt.md   # Integrator instructions
│   └── synthesizer_prompt.md  # Synthesizer instructions
└── generations/               # Output projects (gitignored)
    └── depthkit/              # The generated DAG + artifacts
        ├── seed.md
        ├── index.json         # Graph structure
        ├── frontier.json      # Ready objectives
        ├── harness-progress.txt
        ├── nodes/
        │   ├── OBJ-001/
        │   │   ├── meta.json
        │   │   ├── output.md
        │   │   └── reviews/
        │   └── ...
        ├── dead_ends/
        ├── sessions/
        ├── synthesis/
        └── .git
```

## DAG Output Format

The primary output is `index.json`, which contains the lightweight graph structure:

```json
{
  "seed_version": "3.0",
  "nodes": {
    "OBJ-001": {
      "status": "verified",
      "depends_on": [],
      "blocks": ["OBJ-004", "OBJ-005"],
      "priority": "critical",
      "review_status": "approved",
      "visual_status": null
    }
  },
  "dead_ends": [],
  "vocabulary_updates": [],
  "constraint_updates": []
}
```

Each node directory contains the full context:

```
nodes/OBJ-001/
├── meta.json      # Objective description, deps, notes
├── output.md      # The work product (code, docs, test results)
└── reviews/
    └── REV-001.md # Peer review feedback
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Project output directory | `./depthkit` |
| `--max-iterations` | Max explorer iterations | Unlimited |
| `--model` | Claude model | `claude-sonnet-4-5-20250929` |
| `--no-review` | Skip peer review | Review enabled |
| `--auto-continue-delay` | Seconds between sessions | 3 |
| `--integrator-cadence` | Run integrator every N explorations | 15 |

## Environment Variables

All options can also be set via `.env`:

| Variable | Description |
|----------|-------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | **Required.** OAuth token for Claude Code. |
| `CLAUDE_MODEL` | Model override. |
| `PROJECT_DIR` | Project directory override. |
| `MAX_ITERATIONS` | Max iterations override. |
| `REVIEW_AFTER_EXPLORE` | `true`/`false` — enable peer review. |
| `AUTO_CONTINUE_DELAY` | Seconds between sessions. |
| `INTEGRATOR_CADENCE` | Integrator frequency. |
| `GEMINI_API_KEY` | For Director Agent visual tuning (optional). |

## Security Model

Defense-in-depth security, adapted from Anthropic's autonomous coding demo:

1. **OS-level sandbox** — Bash commands run in an isolated environment.
2. **Filesystem restrictions** — File operations restricted to the project directory.
3. **Bash allowlist** — Only specific commands are permitted (see `security.py`). The allowlist includes Node.js, FFmpeg, git, Python, and standard file inspection tools.
4. **Write isolation** — Each agent writes only to its own node directory. The orchestrator is the sole writer to `index.json`.

## Resuming

The harness is designed for interruption and resumption:

```bash
# Start
python main.py --project-dir ./depthkit

# Ctrl+C to pause at any time

# Resume (same command — picks up where it left off)
python main.py --project-dir ./depthkit
```

Progress is persisted via:
- `index.json` (graph state)
- `frontier.json` (ready objectives)
- Node directories (artifacts, reviews)
- Git commits (full history)

## Relationship to the Downstream Harness

This harness produces the **spec sheet** (the DAG) that a downstream execution harness consumes. The downstream harness:
- Reads `index.json` and node directories
- Routes work to agents based on the DAG's dependency structure
- Uses the verified `output.md` artifacts as implementation specifications
- Follows the same seed document and vocabulary

This harness focuses on **decomposition and peer review** — producing a high-quality, validated plan. The downstream harness focuses on **execution** — turning that plan into working code.
