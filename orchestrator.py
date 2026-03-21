"""
Orchestrator
=============

Manages the harness lifecycle: routes sessions to roles, triggers reviews
after explorations, manages the explore → review → (visual tuning) → verify
loop, and tracks overall convergence.

The orchestrator is the "main loop" of the harness. It:
1. Reads the progress map
2. Determines which role to run next
3. Launches the appropriate agent session
4. Handles the result (trigger review, mark verified, etc.)
5. Repeats until convergence or max iterations
"""

import asyncio
from pathlib import Path
from typing import Optional

from dag.progress_map import (
    ProgressMap,
    load_progress_map,
    save_progress_map,
    ObjectiveStatus,
    ReviewStatus,
)
from roles.initializer import run_initializer
from roles.explorer import run_explorer
from roles.reviewer import run_reviewer
from roles.director import run_director
from roles.integrator import run_integrator
from roles.synthesizer import run_synthesizer


# Run integrator every N sessions
INTEGRATOR_INTERVAL = 15

# Delay between sessions
INTER_SESSION_DELAY = 3


def print_harness_status(pm: ProgressMap) -> None:
    """Print a formatted status summary of the harness."""
    summary = pm.summary()
    total = summary["total_objectives"]
    by_status = summary["by_status"]

    verified = by_status.get("verified", 0)
    in_progress = by_status.get("in_progress", 0)
    review = by_status.get("review", 0)
    open_count = by_status.get("open", 0)
    blocked = by_status.get("blocked", 0)
    dead_end = by_status.get("dead_end", 0)

    pct = (verified / total * 100) if total > 0 else 0

    print(f"\n{'─' * 50}")
    print(f"  Progress: {verified}/{total} verified ({pct:.1f}%)")
    print(f"  Open: {open_count} | In progress: {in_progress} | Review: {review}")
    print(f"  Blocked: {blocked} | Dead ends: {dead_end}")
    print(f"  Sessions: {summary['total_sessions']}")
    print(f"{'─' * 50}\n")


async def run_explore_review_cycle(
    project_dir: Path,
    model: str,
    prompts_dir: Path,
    objective_id: Optional[str] = None,
) -> Optional[str]:
    """
    Run one complete explore → review cycle.

    1. Explorer works on an objective
    2. Reviewer evaluates the artifact
    3. If approved: objective moves toward verified
    4. If revision needed: objective goes back to open

    Returns:
        The objective ID, or None if no work was available
    """
    # Explore
    explored_id = await run_explorer(project_dir, model, prompts_dir, objective_id)
    if explored_id is None:
        return None

    # Small delay
    await asyncio.sleep(INTER_SESSION_DELAY)

    # Review
    reviewed_id = await run_reviewer(project_dir, model, prompts_dir, explored_id)

    return explored_id


async def run_harness_loop(
    project_dir: Path,
    model: str,
    prompts_dir: Path,
    seed_path: Path,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Main harness loop: explore → review → (visual tuning) → repeat.

    This is the primary entry point for running the harness in
    continuous mode. It will:
    1. Initialize if needed
    2. Run explore/review cycles
    3. Trigger integrator periodically
    4. Check for convergence

    Args:
        project_dir: Working directory
        model: Claude model to use
        prompts_dir: Path to prompts directory
        seed_path: Path to seed document
        max_iterations: Maximum iterations (None for unlimited)
    """
    print("\n" + "=" * 70)
    print("  DEPTHKIT PEER-REVIEW HARNESS")
    print("=" * 70)
    print(f"\nProject: {project_dir}")
    print(f"Model: {model}")
    print(f"Max iterations: {max_iterations or 'Unlimited'}")
    print()

    # Check if initialized
    pm_path = project_dir / "progress_map.json"
    if not pm_path.exists():
        print("No progress map found. Running initializer...\n")
        pm = await run_initializer(project_dir, model, seed_path, prompts_dir)
        await asyncio.sleep(INTER_SESSION_DELAY)
    else:
        pm = load_progress_map(pm_path)
        if pm is None:
            print("ERROR: Could not load progress map.")
            return
        print("Resuming from existing progress map.")
        print_harness_status(pm)

    # Main loop
    iteration = 0
    last_integrator = 0

    while True:
        iteration += 1

        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            break

        # Reload progress map
        pm = load_progress_map(pm_path)
        if pm is None:
            print("ERROR: Progress map corrupted.")
            break

        print_harness_status(pm)

        # Check convergence
        verified = pm.get_verified_count()
        total = len(pm.objectives)
        if total > 0 and verified == total:
            print("🎉 ALL OBJECTIVES VERIFIED — Harness converged!")
            break

        # Periodic integrator
        if pm.total_sessions - last_integrator >= INTEGRATOR_INTERVAL:
            print("\n--- Triggering integrator coherence check ---\n")
            await run_integrator(project_dir, model, prompts_dir)
            last_integrator = pm.total_sessions
            await asyncio.sleep(INTER_SESSION_DELAY)
            continue

        # Check for objectives needing visual tuning
        visual_queue = pm.get_objectives_needing_visual_tuning()
        if visual_queue:
            obj = visual_queue[0]
            print(f"\n--- Objective {obj.id} needs visual tuning ---")
            print(f"    {obj.description}")
            print("    Triggering Director Agent...")
            print()
            await run_director(project_dir, prompts_dir, obj.id)
            await asyncio.sleep(INTER_SESSION_DELAY)
            continue

        # Check for objectives needing review
        review_queue = pm.get_objectives_needing_review()
        if review_queue:
            obj = review_queue[0]
            print(f"\n--- Reviewing {obj.id} ---\n")
            await run_reviewer(project_dir, model, prompts_dir, obj.id)
            await asyncio.sleep(INTER_SESSION_DELAY)
            continue

        # Normal explore/review cycle
        result = await run_explore_review_cycle(project_dir, model, prompts_dir)

        if result is None:
            # Nothing to explore — check if we're stuck
            ready = pm.get_ready_objectives()
            blocked = [o for o in pm.objectives if o.status == ObjectiveStatus.BLOCKED.value]
            if not ready and blocked:
                print("\nAll remaining objectives are blocked.")
                print("Blocked objectives:")
                for b in blocked[:5]:
                    print(f"  {b.id}: {b.description}")
                    print(f"    Depends on: {b.depends_on}")
                break
            elif not ready:
                print("\nNo objectives available. Checking if converged...")
                remaining = [o for o in pm.objectives if o.status in ("open", "in_progress", "review")]
                if not remaining:
                    print("🎉 All objectives resolved. Harness converged!")
                else:
                    print(f"Remaining objectives in non-ready states: {len(remaining)}")
                break

        # Delay between iterations
        await asyncio.sleep(INTER_SESSION_DELAY)

    # Final status
    pm = load_progress_map(pm_path) or pm
    print("\n" + "=" * 70)
    print("  HARNESS SESSION COMPLETE")
    print("=" * 70)
    print_harness_status(pm)

    # Suggest next steps
    verified = pm.get_verified_count()
    total = len(pm.objectives)
    if verified < total:
        print("To continue: python harness.py --project-dir", project_dir, "--phase explore")
        print("To synthesize: python harness.py --project-dir", project_dir, "--phase synthesize")
    else:
        print("All objectives verified! Run synthesizer to produce the build spec:")
        print(f"  python harness.py --project-dir {project_dir} --phase synthesize")
