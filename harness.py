#!/usr/bin/env python3
"""
Depthkit Peer-Review Harness
==============================

A multi-agent, DAG-structured harness for building the depthkit 2.5D video
rendering engine. Implements the Multi-Agent Seed Harness architecture with
peer review, visual tuning (via Gemini Director Agent), and HITL circuit breaker.

Usage:
    # Initialize (decompose seed into DAG)
    python harness.py --project-dir ./depthkit --phase init

    # Run explore/review cycles
    python harness.py --project-dir ./depthkit --phase explore

    # Run with iteration limit
    python harness.py --project-dir ./depthkit --phase explore --max-iterations 10

    # Run integrator coherence check
    python harness.py --project-dir ./depthkit --phase integrate

    # Trigger Director Agent visual tuning
    python harness.py --project-dir ./depthkit --phase direct --objective OBJ-042

    # Synthesize final build specification
    python harness.py --project-dir ./depthkit --phase synthesize

    # Review a specific objective
    python harness.py --project-dir ./depthkit --phase review --objective OBJ-003

    # Explore a specific objective
    python harness.py --project-dir ./depthkit --phase explore --objective OBJ-007

Environment Variables:
    ANTHROPIC_API_KEY       Required for Claude agents
    CLAUDE_CODE_OAUTH_TOKEN Alternative auth for Claude Code
    GEMINI_API_KEY          Required for Director Agent (visual tuning only)
"""

import argparse
import asyncio
import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
PROMPTS_DIR = Path(__file__).parent / "prompts"
DEFAULT_SEED = PROMPTS_DIR / "seed.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Depthkit Peer-Review Harness — Multi-agent DAG builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Phases:
  init        Initialize: decompose seed into DAG of objectives
  explore     Run explore → review cycles (the main loop)
  review      Review a specific objective
  direct      Trigger Director Agent visual tuning (requires GEMINI_API_KEY)
  integrate   Run integrator coherence check
  synthesize  Assemble verified results into build specification

Examples:
  python harness.py --project-dir ./depthkit --phase init
  python harness.py --project-dir ./depthkit --phase explore --max-iterations 5
  python harness.py --project-dir ./depthkit --phase direct --objective OBJ-042
  python harness.py --project-dir ./depthkit --phase synthesize
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./depthkit"),
        help="Working directory for the project (default: ./depthkit)",
    )

    parser.add_argument(
        "--phase",
        choices=["init", "explore", "review", "direct", "integrate", "synthesize"],
        default="explore",
        help="Harness phase to run (default: explore)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of session iterations (default: unlimited)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--objective",
        type=str,
        default=None,
        help="Specific objective ID to work on (auto-selects if omitted)",
    )

    parser.add_argument(
        "--seed",
        type=Path,
        default=DEFAULT_SEED,
        help="Path to seed document (default: prompts/seed.md)",
    )

    parser.add_argument(
        "--render",
        type=str,
        default=None,
        help="Path to test render MP4 for Director Agent (auto-discovers if omitted)",
    )

    return parser.parse_args()


def check_auth() -> bool:
    """Check that required authentication is configured."""
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return True
    print("ERROR: No authentication configured.")
    print()
    print("Set one of:")
    print("  export ANTHROPIC_API_KEY='your-api-key'")
    print("  export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token'")
    return False


def ensure_seed(seed_path: Path, project_dir: Path) -> Path:
    """Ensure the seed document is available in the project directory."""
    dest = project_dir / "seed.md"
    if dest.exists():
        return dest

    if seed_path.exists():
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(seed_path, dest)
        print(f"Copied seed to {dest}")
        return dest

    print(f"ERROR: Seed document not found at {seed_path}")
    print("Provide a seed with: --seed /path/to/seed.md")
    sys.exit(1)


async def main_async(args: argparse.Namespace) -> None:
    """Async main — dispatches to the appropriate phase."""
    project_dir = args.project_dir.resolve()

    if args.phase == "init":
        # ─── INITIALIZATION ───
        from roles.initializer import run_initializer

        seed_path = ensure_seed(args.seed, project_dir)
        pm = await run_initializer(project_dir, args.model, seed_path, PROMPTS_DIR)
        print(f"\nInitialization complete. {len(pm.objectives)} objectives created.")
        print(f"Next: python harness.py --project-dir {project_dir} --phase explore")

    elif args.phase == "explore":
        # ─── EXPLORATION (main loop) ───
        if args.objective:
            # Single objective mode
            from roles.explorer import run_explorer
            result = await run_explorer(project_dir, args.model, PROMPTS_DIR, args.objective)
            if result:
                print(f"\nExploration complete for {result}.")
                print(f"Review with: python harness.py --project-dir {project_dir} --phase review --objective {result}")
        else:
            # Full loop mode
            from orchestrator import run_harness_loop
            seed_path = ensure_seed(args.seed, project_dir)
            await run_harness_loop(
                project_dir, args.model, PROMPTS_DIR, seed_path,
                max_iterations=args.max_iterations,
            )

    elif args.phase == "review":
        # ─── PEER REVIEW ───
        from roles.reviewer import run_reviewer
        result = await run_reviewer(project_dir, args.model, PROMPTS_DIR, args.objective)
        if result:
            print(f"\nReview complete for {result}.")

    elif args.phase == "direct":
        # ─── DIRECTOR AGENT (VISUAL TUNING) ───
        if not args.objective:
            # Auto-select objective needing tuning
            from dag.progress_map import load_progress_map
            pm = load_progress_map(project_dir / "progress_map.json")
            if pm:
                visual_queue = pm.get_objectives_needing_visual_tuning()
                if visual_queue:
                    args.objective = visual_queue[0].id
                    print(f"Auto-selected objective for visual tuning: {args.objective}")
                else:
                    print("No objectives need visual tuning.")
                    return

        if not os.environ.get("GEMINI_API_KEY"):
            print("ERROR: GEMINI_API_KEY required for Director Agent.")
            print("Set: export GEMINI_API_KEY='your-key'")
            return

        from roles.director import run_director
        result = await run_director(project_dir, PROMPTS_DIR, args.objective, args.render)
        if result:
            print(f"\nDirector critique written to: {result}")
            print("Next: feed approved critique to explorer for parameter adjustment.")

    elif args.phase == "integrate":
        # ─── INTEGRATOR ───
        from roles.integrator import run_integrator
        result = await run_integrator(project_dir, args.model, PROMPTS_DIR)
        if result:
            print(f"\nCoherence report: {result}")

    elif args.phase == "synthesize":
        # ─── SYNTHESIZER ───
        from roles.synthesizer import run_synthesizer
        result = await run_synthesizer(project_dir, args.model, PROMPTS_DIR)
        if result:
            print(f"\nBuild specification: {result}")
            print("This is the input for the downstream build harness.")


def main() -> None:
    load_dotenv()
    args = parse_args()

    # Check auth (not needed for synthesize/integrate if progress map exists)
    if args.phase in ("init", "explore", "review"):
        if not check_auth():
            sys.exit(1)

    if args.phase == "direct":
        if not os.environ.get("GEMINI_API_KEY"):
            print("WARNING: GEMINI_API_KEY not set. Director Agent will fail.")

    # Run
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        print("To resume: python harness.py --project-dir", args.project_dir, "--phase", args.phase)
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
