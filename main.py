#!/usr/bin/env python3
"""
Depthkit Multi-Agent Harness
=============================

A deliberation-structured harness that decomposes the depthkit seed document
into a DAG of specification objectives through two-agent conversations,
then produces peer-reviewed specs for each objective.

The output DAG (index.json + node directories) serves as the spec sheet
for a downstream execution harness.

Usage:
    python main.py                                    # Run with defaults
    python main.py --project-dir ./my-depthkit        # Custom project dir
    python main.py --max-iterations 5                 # Limit iterations
    python main.py --init-rounds 6                    # More init deliberation
    python main.py --explore-rounds 4                 # Rounds per objective

Environment Variables:
    CLAUDE_CODE_OAUTH_TOKEN   Required. Your Claude Code OAuth token.
    CLAUDE_MODEL              Optional. Override the default model.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from orchestrator import run_harness


DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_PROJECT_DIR = "./depthkit"
DEFAULT_AUTO_CONTINUE_DELAY = 3
DEFAULT_INTEGRATOR_CADENCE = 15
DEFAULT_INIT_ROUNDS = 6
DEFAULT_EXPLORE_ROUNDS = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Depthkit Multi-Agent Harness — deliberation-based spec DAG builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --project-dir ./depthkit
  python main.py --project-dir ./depthkit --max-iterations 5
  python main.py --init-rounds 8 --explore-rounds 6   # More deliberation

Watch conclusions live (in another terminal):
  tail -f generations/depthkit/feed.md
        """,
    )

    parser.add_argument("--project-dir", type=Path, default=None,
        help=f"Project directory (default: {DEFAULT_PROJECT_DIR})")
    parser.add_argument("--max-iterations", type=int, default=None,
        help="Max explore deliberations (default: unlimited)")
    parser.add_argument("--model", type=str, default=None,
        help=f"Claude model (default: {DEFAULT_MODEL})")
    parser.add_argument("--auto-continue-delay", type=int, default=None,
        help=f"Seconds between sessions (default: {DEFAULT_AUTO_CONTINUE_DELAY})")
    parser.add_argument("--integrator-cadence", type=int, default=None,
        help=f"Integrator every N explorations (default: {DEFAULT_INTEGRATOR_CADENCE})")
    parser.add_argument("--init-rounds", type=int, default=None,
        help=f"Deliberation rounds for initialization (default: {DEFAULT_INIT_ROUNDS})")
    parser.add_argument("--explore-rounds", type=int, default=None,
        help=f"Deliberation rounds per objective (default: {DEFAULT_EXPLORE_ROUNDS})")

    return parser.parse_args()


def resolve_config(args: argparse.Namespace) -> dict:
    config = {}

    config["model"] = args.model or os.environ.get("CLAUDE_MODEL") or DEFAULT_MODEL

    project_dir_str = (
        str(args.project_dir) if args.project_dir
        else os.environ.get("PROJECT_DIR") or DEFAULT_PROJECT_DIR
    )
    project_dir = Path(project_dir_str)
    if not project_dir.is_absolute() and not str(project_dir).startswith("generations/"):
        project_dir = Path("generations") / project_dir
    config["project_dir"] = project_dir

    max_iter_env = os.environ.get("MAX_ITERATIONS")
    config["max_iterations"] = args.max_iterations or (int(max_iter_env) if max_iter_env else None)

    delay_env = os.environ.get("AUTO_CONTINUE_DELAY")
    config["auto_continue_delay"] = (
        args.auto_continue_delay
        or (int(delay_env) if delay_env else DEFAULT_AUTO_CONTINUE_DELAY)
    )

    cadence_env = os.environ.get("INTEGRATOR_CADENCE")
    config["integrator_cadence"] = (
        args.integrator_cadence
        or (int(cadence_env) if cadence_env else DEFAULT_INTEGRATOR_CADENCE)
    )

    init_env = os.environ.get("INIT_ROUNDS")
    config["init_rounds"] = (
        args.init_rounds
        or (int(init_env) if init_env else DEFAULT_INIT_ROUNDS)
    )

    explore_env = os.environ.get("EXPLORE_ROUNDS")
    config["explore_rounds"] = (
        args.explore_rounds
        or (int(explore_env) if explore_env else DEFAULT_EXPLORE_ROUNDS)
    )

    return config


def main() -> None:
    load_dotenv()
    args = parse_args()
    config = resolve_config(args)

    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("Error: CLAUDE_CODE_OAUTH_TOKEN not set.")
        print("  export CLAUDE_CODE_OAUTH_TOKEN='your-token'")
        print("  or set it in .env")
        sys.exit(1)

    print()
    print("  Configuration:")
    print(f"    Model:              {config['model']}")
    print(f"    Project dir:        {config['project_dir']}")
    print(f"    Max iterations:     {config['max_iterations'] or 'unlimited'}")
    print(f"    Init rounds:        {config['init_rounds']}")
    print(f"    Explore rounds:     {config['explore_rounds']}")
    print(f"    Continue delay:     {config['auto_continue_delay']}s")
    print(f"    Integrator cadence: every {config['integrator_cadence']} explorations")
    print()
    print(f"  Watch conclusions live:")
    print(f"    tail -f {config['project_dir']}/feed.md")
    print()

    try:
        asyncio.run(
            run_harness(
                project_dir=config["project_dir"],
                model=config["model"],
                max_iterations=config["max_iterations"],
                auto_continue_delay=config["auto_continue_delay"],
                integrator_cadence=config["integrator_cadence"],
                init_rounds=config["init_rounds"],
                explore_rounds=config["explore_rounds"],
            )
        )
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Resume with the same command.")
    except Exception as e:
        print(f"\n  Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
