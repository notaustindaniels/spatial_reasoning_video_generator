# Depthkit Peer-Review Harness

A multi-agent, DAG-structured test harness for autonomously building the **depthkit** 2.5D video rendering engine. Implements the architecture described in the Multi-Agent Seed Harness Spec v2, domain-configured for the depthkit seed v3.

## What This Produces

The harness's primary output is a **`progress_map.json`** — a directed acyclic graph (DAG) of objectives, their statuses, dependencies, and review results. This DAG becomes the spec sheet for a downstream build harness that will execute the actual implementation work.

## Architecture

The harness orchestrates six agent roles across multiple sessions:

| Role | Model | Purpose |
|---|---|---|
| **Initializer** | Claude | Reads the seed, decomposes it into ~80-120 objectives, produces the initial `progress_map.json` |
| **Explorer** | Claude | Picks an open objective, produces a discrete artifact (code, design doc, validation result) |
| **Reviewer** | Claude (fresh context) | Adversarial-but-constructive peer review of explorer output. Decorrelates blind spots. |
| **Director** | Gemini (multimodal) | Reviews test renders for visual quality. Development-only. Operates under HITL circuit breaker. |
| **Integrator** | Claude | Periodic coherence check across the DAG. Detects drift, inconsistency, missed connections. |
| **Synthesizer** | Claude | Assembles verified results into final deliverables at convergence. |

## Prerequisites

```bash
# Claude Code CLI (latest)
npm install -g @anthropic-ai/claude-code

# Python dependencies
pip install -r requirements.txt
```

**Required environment variables:**
```bash
export ANTHROPIC_API_KEY='your-key'        # For Claude agents
export GEMINI_API_KEY='your-key'           # For Director Agent (optional, visual tuning only)
```

## Quick Start

```bash
# Initialize: decompose seed into DAG
python harness.py --project-dir ./depthkit --phase init

# Run exploration + review cycles
python harness.py --project-dir ./depthkit --phase explore

# Run with iteration limit (for testing)
python harness.py --project-dir ./depthkit --phase explore --max-iterations 5

# Run integrator coherence check
python harness.py --project-dir ./depthkit --phase integrate

# Trigger visual tuning for a specific objective (requires GEMINI_API_KEY)
python harness.py --project-dir ./depthkit --phase direct --objective OBJ-042

# Synthesize final output
python harness.py --project-dir ./depthkit --phase synthesize
```

## Workflow

```
  ┌─────────────┐
  │  seed_v3.md  │
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │  Initializer  │── produces ──▶ progress_map.json (DAG)
  └──────┬───────┘
         │
  ┌──────▼───────┐      ┌───────────┐
  │   Explorer    │─────▶│  Reviewer  │──┐
  └──────┬───────┘      └───────────┘  │
         │                              │ approved / revision_needed
         │◀─────────────────────────────┘
         │
  ┌──────▼───────┐   (visual objectives only)
  │   Director    │──▶ HITL Gate ──▶ Code Agent adjusts
  └──────┬───────┘
         │
  ┌──────▼───────┐   (periodic)
  │  Integrator   │──▶ coherence report, seed updates
  └──────┬───────┘
         │
  ┌──────▼───────┐   (at convergence)
  │  Synthesizer  │──▶ final deliverables
  └──────────────┘
```

## Project Structure

```
depthkit-harness/
├── harness.py              # CLI entry point
├── orchestrator.py         # Session management, role routing
├── client.py               # Claude SDK client configuration
├── security.py             # Bash command allowlist
├── dag/
│   ├── __init__.py
│   ├── progress_map.py     # DAG data structures and CRUD
│   └── session_log.py      # Session logging utilities
├── roles/
│   ├── __init__.py
│   ├── initializer.py      # Seed → initial DAG decomposition
│   ├── explorer.py         # Objective implementation
│   ├── reviewer.py         # Peer review
│   ├── director.py         # Visual tuning (Gemini)
│   ├── integrator.py       # Coherence checking
│   └── synthesizer.py      # Final assembly
├── prompts/
│   ├── seed.md             # Copy of seed_v3.md
│   ├── initializer_prompt.md
│   ├── explorer_prompt.md
│   ├── reviewer_prompt.md
│   ├── director_prompt.md
│   ├── integrator_prompt.md
│   └── synthesizer_prompt.md
├── requirements.txt
└── README.md
```

## Generated Project Structure

After running, your project directory will contain:

```
depthkit/
├── progress_map.json       # The DAG (primary output)
├── seed.md                 # Copy of the seed document
├── sessions/               # One log per session
│   ├── session_001_init.md
│   ├── session_002_explore_OBJ-001.md
│   ├── session_003_review_OBJ-001.md
│   └── ...
├── artifacts/              # Work products per objective
│   ├── OBJ-001/
│   ├── OBJ-002/
│   └── ...
├── reviews/                # Review reports
├── critiques/              # Director visual critiques
├── renders/                # Test render clips
├── .claude_settings.json   # Security settings
└── .git/                   # Full audit trail
```

## Key Design Decisions

1. **DAG-first**: Every session reads seed + progress_map, never full history. The DAG is the distributed memory.

2. **Peer review is mandatory**: No objective moves to `verified` without an independent review from a fresh context window.

3. **HITL circuit breaker**: Director Agent (Gemini) feedback always passes through human approval before reaching the Code Agent. This is a hard constraint.

4. **Constructive opposition**: All critique must propose a replacement. "This is wrong" without "here's what's right" is flagged as incomplete.

5. **Dead ends are progress**: Failed explorations are recorded in the DAG to prevent re-exploration.

## Command Line Options

| Option | Description | Default |
|---|---|---|
| `--project-dir` | Working directory | `./depthkit` |
| `--phase` | Harness phase to run | `explore` |
| `--max-iterations` | Max session iterations | Unlimited |
| `--model` | Claude model | `claude-sonnet-4-5-20250929` |
| `--objective` | Specific objective ID | Auto-select |
| `--seed` | Path to seed document | `prompts/seed.md` |

## License

Internal use.
