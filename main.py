#!/usr/bin/env python3
"""
Depthkit Multi-Agent Harness
=============================

A peer-review-structured harness that produces a DAG of testable objectives
for building depthkit — a custom Node.js 2.5D parallax video engine.

Architecture (from video_multi_agent_harness_spec_v2):
- Seed-driven coherence (seed_v3.md)
- Multi-agent peer review (Explorer → Reviewer → Director)
- DAG-structured progress tracking (index.json + per-node directories)

Agent Roles:
- Initializer: Decomposes seed into DAG of objectives (runs once)
- Explorer: Implements one objective per session
- Reviewer: Independent peer review with constructive critique
- Director: Gemini-powered visual tuning (HITL circuit breaker)
- Integrator: Periodic coherence check across verified nodes
- Synthesizer: Assembles verified nodes into final deliverable

Usage:
    # Initialize and start autonomous loop
    python main.py --seed ./seed_v3.md

    # Run specific role
    python main.py --seed ./seed_v3.md --role explorer --node OBJ-042

    # Limit iterations for testing
    python main.py --seed ./seed_v3.md --max-iterations 5

    # Continue existing project
    python main.py --seed ./seed_v3.md --project-dir ./generations/depthkit
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from orchestrator import run_orchestrator


# Load .env from the harness directory
load_dotenv(Path(__file__).parent / ".env")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Depthkit Multi-Agent Harness — DAG-structured autonomous development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start from scratch (initializes DAG, then explores)
  python main.py --seed ./seed_v3.md

  # Continue existing project
  python main.py --seed ./seed_v3.md --project-dir generations/depthkit

  # Run a specific role on a specific node
  python main.py --seed ./seed_v3.md --role reviewer --node OBJ-003

  # Run only the initializer (decompose seed into DAG)
  python main.py --seed ./seed_v3.md --role initializer --max-iterations 1

  # Run with limited iterations for testing
  python main.py --seed ./seed_v3.md --max-iterations 5

  # Use a different model
  python main.py --seed ./seed_v3.md --model claude-sonnet-4-5-20250929

Environment Variables (set in .env or export):
  CLAUDE_CODE_OAUTH_TOKEN   Required. Claude Code OAuth token.
  GEMINI_API_KEY            Optional. For Director Agent visual tuning.
  CLAUDE_MODEL              Default model (overridden by --model).
  HITL_ENABLED              Enable/disable HITL circuit breaker (default: true).
        """,
    )

    parser.add_argument(
        "--seed",
        type=Path,
        required=True,
        help="Path to the seed document (e.g., ./seed_v3.md)",
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help="Project directory (default: generations/<seed_name>)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent sessions (default: unlimited)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Claude model to use (default: from .env or claude-sonnet-4-5-20250929)",
    )

    parser.add_argument(
        "--role",
        type=str,
        choices=["initializer", "explorer", "reviewer", "director", "integrator", "synthesizer"],
        default=None,
        help="Force a specific role for this run",
    )

    parser.add_argument(
        "--node",
        type=str,
        default=None,
        help="Target a specific node ID (e.g., OBJ-042)",
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Max turns per agent session (default: from .env or 1000)",
    )

    parser.add_argument(
        "--integrator-cadence",
        type=int,
        default=None,
        help="Run integrator every N explorer completions (default: from .env or 15)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Validate environment ──

    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("Error: CLAUDE_CODE_OAUTH_TOKEN not set.")
        print()
        print("Set it in .env or export it:")
        print("  export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'")
        print()
        print("Get your token from: https://console.anthropic.com/")
        sys.exit(1)

    if not args.seed.exists():
        print(f"Error: Seed file not found: {args.seed}")
        sys.exit(1)

    # ── Resolve configuration ──

    model = args.model or os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
    max_turns = args.max_turns or int(os.environ.get("MAX_TURNS", "1000"))
    integrator_cadence = args.integrator_cadence or int(os.environ.get("INTEGRATOR_CADENCE", "15"))

    # Resolve project directory
    if args.project_dir:
        project_dir = args.project_dir
    else:
        # Default: generations/<seed_stem>
        project_dir = Path("generations") / args.seed.stem

    # Normalize relative paths under generations/
    if not project_dir.is_absolute() and not str(project_dir).startswith("generations/"):
        project_dir = Path("generations") / project_dir

    # ── Check Gemini if director role is requested ──

    if args.role == "director" and not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not set. Director visual tuning will be skipped.")
        print("Set it in .env to enable: GEMINI_API_KEY=your-key-here")
        print()

    # ── Run ──

    try:
        asyncio.run(
            run_orchestrator(
                project_dir=project_dir,
                seed_path=args.seed.resolve(),
                model=model,
                max_iterations=args.max_iterations,
                max_turns=max_turns,
                integrator_cadence=integrator_cadence,
                target_node=args.node,
                role_override=args.role,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        print("To resume, run the same command again.")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
