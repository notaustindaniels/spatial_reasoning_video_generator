#!/usr/bin/env python3
"""
Depthkit Multi-Agent Harness
=============================

A peer-review-structured harness that decomposes the depthkit seed document
into a DAG of testable objectives, then uses Explorer → Reviewer → (Director)
agent loops to build the engine incrementally.

The output DAG (index.json + node directories) serves as the spec sheet
for a downstream execution harness.

Usage:
    python main.py                                    # Run with defaults
    python main.py --project-dir ./my-depthkit        # Custom project dir
    python main.py --max-iterations 5                 # Limit iterations
    python main.py --no-review                        # Skip peer review
    python main.py --model claude-sonnet-4-5-20250929 # Specific model

Environment Variables:
    CLAUDE_CODE_OAUTH_TOKEN   Required. Your Claude Code OAuth token.
    CLAUDE_MODEL              Optional. Override the default model.
    PROJECT_DIR               Optional. Override the default project dir.
    MAX_ITERATIONS            Optional. Max explorer iterations.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from orchestrator import run_harness


# ──────────────────────────────────────────────────────────────
# Defaults
# ──────────────────────────────────────────────────────────────

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_PROJECT_DIR = "./depthkit"
DEFAULT_AUTO_CONTINUE_DELAY = 3
DEFAULT_INTEGRATOR_CADENCE = 15


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Depthkit Multi-Agent Harness — builds a DAG of objectives from the seed document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fresh start
  python main.py --project-dir ./depthkit

  # Resume existing project
  python main.py --project-dir ./depthkit

  # Limit to 5 explorer iterations (good for testing)
  python main.py --project-dir ./depthkit --max-iterations 5

  # Skip peer review (faster, less thorough)
  python main.py --project-dir ./depthkit --no-review

  # Use a specific model
  python main.py --model claude-sonnet-4-5-20250929

Environment Variables:
  CLAUDE_CODE_OAUTH_TOKEN    Your Claude Code OAuth token (required)
  CLAUDE_MODEL               Override the model (optional)
  PROJECT_DIR                Override the project directory (optional)
  MAX_ITERATIONS             Override max iterations (optional)
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help=f"Project directory (default: from .env or {DEFAULT_PROJECT_DIR}). "
             "Relative paths placed under generations/.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum explorer iterations (default: unlimited or from .env)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Claude model to use (default: from .env or {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Skip peer review after explorer sessions",
    )

    parser.add_argument(
        "--auto-continue-delay",
        type=int,
        default=None,
        help=f"Seconds between sessions (default: {DEFAULT_AUTO_CONTINUE_DELAY})",
    )

    parser.add_argument(
        "--integrator-cadence",
        type=int,
        default=None,
        help=f"Run integrator every N explorer completions (default: {DEFAULT_INTEGRATOR_CADENCE})",
    )

    return parser.parse_args()


def resolve_config(args: argparse.Namespace) -> dict:
    """Resolve configuration from args → env → defaults."""
    config = {}

    # Model
    config["model"] = (
        args.model
        or os.environ.get("CLAUDE_MODEL")
        or DEFAULT_MODEL
    )

    # Project directory
    project_dir_str = (
        str(args.project_dir) if args.project_dir
        else os.environ.get("PROJECT_DIR")
        or DEFAULT_PROJECT_DIR
    )
    project_dir = Path(project_dir_str)

    # Place relative paths under generations/
    if not project_dir.is_absolute() and not str(project_dir).startswith("generations/"):
        project_dir = Path("generations") / project_dir
    config["project_dir"] = project_dir

    # Max iterations
    max_iter_env = os.environ.get("MAX_ITERATIONS")
    config["max_iterations"] = (
        args.max_iterations
        or (int(max_iter_env) if max_iter_env else None)
    )

    # Review
    config["review_after_explore"] = not args.no_review
    if os.environ.get("REVIEW_AFTER_EXPLORE", "").lower() == "false":
        config["review_after_explore"] = False

    # Auto-continue delay
    delay_env = os.environ.get("AUTO_CONTINUE_DELAY")
    config["auto_continue_delay"] = (
        args.auto_continue_delay
        or (int(delay_env) if delay_env else DEFAULT_AUTO_CONTINUE_DELAY)
    )

    # Integrator cadence
    cadence_env = os.environ.get("INTEGRATOR_CADENCE")
    config["integrator_cadence"] = (
        args.integrator_cadence
        or (int(cadence_env) if cadence_env else DEFAULT_INTEGRATOR_CADENCE)
    )

    return config


def main() -> None:
    """Main entry point."""
    # Load .env file
    load_dotenv()

    args = parse_args()
    config = resolve_config(args)

    # Verify OAuth token
    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("Error: CLAUDE_CODE_OAUTH_TOKEN environment variable not set.")
        print()
        print("Set it in your .env file or export it:")
        print("  export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'")
        print()
        print("Or copy .env.example to .env and fill in the value.")
        sys.exit(1)

    # Print configuration
    print()
    print("  Configuration:")
    print(f"    Model:              {config['model']}")
    print(f"    Project dir:        {config['project_dir']}")
    print(f"    Max iterations:     {config['max_iterations'] or 'unlimited'}")
    print(f"    Peer review:        {'enabled' if config['review_after_explore'] else 'disabled'}")
    print(f"    Continue delay:     {config['auto_continue_delay']}s")
    print(f"    Integrator cadence: every {config['integrator_cadence']} explorations")
    print()

    # Run the harness
    try:
        asyncio.run(
            run_harness(
                project_dir=config["project_dir"],
                model=config["model"],
                max_iterations=config["max_iterations"],
                auto_continue_delay=config["auto_continue_delay"],
                review_after_explore=config["review_after_explore"],
                integrator_cadence=config["integrator_cadence"],
            )
        )
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user.")
        print("  To resume, run the same command again — the harness picks up where it left off.")
        print()
    except Exception as e:
        print(f"\n  Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
