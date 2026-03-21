"""
Orchestrator
============

The main loop managing the harness lifecycle:
1. Initialization (runs once — decomposes seed into DAG)
2. Exploration loop (picks frontier objectives, runs explorer → reviewer)
3. Periodic integration (coherence checks)
4. Convergence detection

This is the "brain" that routes sessions to roles, manages the frontier,
and enforces the explore → review → verify pipeline.
"""

import asyncio
import random
import shutil
from pathlib import Path
from typing import Optional

from dag import (
    read_index,
    refresh_frontier,
    update_node_status,
    get_progress_summary,
    print_progress,
    STATUS_OPEN,
    STATUS_IN_PROGRESS,
    STATUS_REVIEW,
    STATUS_REVISION_NEEDED,
    STATUS_APPROVED,
    STATUS_VERIFIED,
    STATUS_BLOCKED,
)
from agent import (
    run_initializer_session,
    run_explorer_session,
    run_reviewer_session,
    run_integrator_session,
    write_session_log,
)
from context import PROMPTS_DIR


# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────

AUTO_CONTINUE_DELAY = 3       # Seconds between sessions
INTEGRATOR_CADENCE = 15       # Run integrator every N explorer completions
MAX_REVIEWS_PER_NODE = 2      # Max review rounds before auto-approve


# ──────────────────────────────────────────────────────────────
# Orchestrator Main Loop
# ──────────────────────────────────────────────────────────────

async def run_harness(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
    auto_continue_delay: int = AUTO_CONTINUE_DELAY,
    review_after_explore: bool = True,
    integrator_cadence: int = INTEGRATOR_CADENCE,
) -> None:
    """
    Run the full harness lifecycle.

    Args:
        project_dir: Root directory for the project.
        model: Claude model to use for all roles.
        max_iterations: Max explorer iterations (None = unlimited).
        auto_continue_delay: Seconds between sessions.
        review_after_explore: Whether to trigger review after each explorer.
        integrator_cadence: Run integrator every N explorer completions.
    """
    print("\n" + "=" * 70)
    print("  DEPTHKIT MULTI-AGENT HARNESS")
    print("=" * 70)
    print(f"\n  Project directory: {project_dir}")
    print(f"  Model: {model}")
    if max_iterations:
        print(f"  Max iterations: {max_iterations}")
    else:
        print(f"  Max iterations: Unlimited")
    print(f"  Review after explore: {review_after_explore}")
    print(f"  Integrator cadence: every {integrator_cadence} explorer completions")
    print()

    # ── Phase 1: Initialization ──────────────────────────────
    project_dir.mkdir(parents=True, exist_ok=True)

    index = read_index(project_dir)
    is_fresh = not index or not index.get("nodes")

    if is_fresh:
        print("  Phase 1: INITIALIZATION (first run)")
        print("  " + "-" * 50)
        _setup_project(project_dir)

        status, response = await run_initializer_session(
            project_dir, model, max_turns=1000
        )

        write_session_log(
            project_dir, "init-001", "initializer", None, status,
            "Initial decomposition of seed into DAG."
        )

        if status == "error":
            print("\n  Initializer failed. Check logs and retry.")
            return

        print("\n  Initialization complete.")
        print_progress(project_dir)
        await asyncio.sleep(auto_continue_delay)
    else:
        print("  Resuming existing project.")
        print_progress(project_dir)

    # ── Phase 2+3: Exploration + Review Loop ─────────────────
    explorer_count = 0
    iteration = 0

    while True:
        iteration += 1

        if max_iterations and iteration > max_iterations:
            print(f"\n  Reached max iterations ({max_iterations}).")
            break

        # Check for convergence
        summary = get_progress_summary(project_dir)
        if summary["total"] > 0 and summary["open"] == 0 and summary["in_progress"] == 0 \
                and summary["review"] == 0 and summary["revision_needed"] == 0:
            print("\n  ✓ CONVERGENCE: All objectives are verified, blocked, or dead-ended.")
            break

        # Refresh frontier
        frontier = refresh_frontier(project_dir)

        if not frontier:
            # Check if there are nodes in review that need processing
            index = read_index(project_dir)
            review_nodes = [
                nid for nid, n in index.get("nodes", {}).items()
                if n["status"] == STATUS_REVIEW
            ]

            if review_nodes and review_after_explore:
                # Run reviewer for the first node in review
                node_id = review_nodes[0]
                print(f"\n  No frontier objectives. Running review for {node_id}.")

                status, response = await run_reviewer_session(
                    project_dir, node_id, model
                )

                write_session_log(
                    project_dir, f"rev-{iteration:03d}", "reviewer",
                    node_id, status, f"Review of {node_id}."
                )

                # Parse reviewer verdict from response
                _process_review_verdict(project_dir, node_id, response)

                await asyncio.sleep(auto_continue_delay)
                continue
            else:
                print("\n  Frontier is empty and no reviews pending.")
                print("  Possible states: all nodes blocked or all verified.")
                break

        # Pick highest priority frontier objective
        target = frontier[0]
        node_id = target["id"]

        print(f"\n  Frontier has {len(frontier)} objectives. Picking: {node_id}")
        print(f"    Priority: {target['priority']} | "
              f"Blocks: {len(target['blocks'])} downstream nodes")

        # ── Run Explorer Session ─────────────────────────────
        explorer_count += 1

        status, response = await run_explorer_session(
            project_dir, node_id, model,
            session_number=iteration,
        )

        write_session_log(
            project_dir, f"exp-{iteration:03d}", "explorer",
            node_id, status, f"Explorer working on {node_id}."
        )

        if status == "error":
            print(f"  Explorer session failed for {node_id}. Returning to open.")
            try:
                update_node_status(project_dir, node_id, STATUS_OPEN)
            except KeyError:
                pass
            await asyncio.sleep(auto_continue_delay)
            continue

        print_progress(project_dir)

        # ── Run Reviewer Session (if enabled) ────────────────
        if review_after_explore:
            await asyncio.sleep(auto_continue_delay)

            print(f"\n  Triggering review for {node_id}...")

            rev_status, rev_response = await run_reviewer_session(
                project_dir, node_id, model
            )

            write_session_log(
                project_dir, f"rev-{iteration:03d}", "reviewer",
                node_id, rev_status, f"Review of {node_id} after explorer session."
            )

            _process_review_verdict(project_dir, node_id, rev_response)

        # ── Periodic Integrator Check ────────────────────────
        if explorer_count % integrator_cadence == 0 and explorer_count > 0:
            print(f"\n  Integrator cadence reached ({explorer_count} explorations).")
            await _run_integrator(project_dir, model)

        # ── Auto-continue ────────────────────────────────────
        await asyncio.sleep(auto_continue_delay)

    # ── Final Summary ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  HARNESS COMPLETE")
    print("=" * 70)
    print(f"\n  Project: {project_dir}")
    print_progress(project_dir)

    # Print the DAG output location
    print(f"\n  DAG output: {project_dir / 'index.json'}")
    print(f"  Node artifacts: {project_dir / 'nodes/'}")
    print(f"  Session logs: {project_dir / 'sessions/'}")
    print()


# ──────────────────────────────────────────────────────────────
# Internal Helpers
# ──────────────────────────────────────────────────────────────

def _setup_project(project_dir: Path) -> None:
    """Set up the initial project structure."""
    # Create directories
    (project_dir / "nodes").mkdir(parents=True, exist_ok=True)
    (project_dir / "dead_ends").mkdir(parents=True, exist_ok=True)
    (project_dir / "sessions").mkdir(parents=True, exist_ok=True)
    (project_dir / "synthesis").mkdir(parents=True, exist_ok=True)

    # Copy seed document into the project
    seed_source = PROMPTS_DIR / "seed.md"
    seed_dest = project_dir / "seed.md"
    if seed_source.exists() and not seed_dest.exists():
        shutil.copy(seed_source, seed_dest)
        print("  Copied seed.md into project directory.")
    elif not seed_dest.exists():
        print("  WARNING: No seed.md found. The initializer will need it.")

    # Initialize git if not already
    import subprocess
    if not (project_dir / ".git").exists():
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            capture_output=True,
        )
        subprocess.run(
            ["git", "add", "."],
            cwd=project_dir,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial project setup"],
            cwd=project_dir,
            capture_output=True,
        )
        print("  Initialized git repository.")


def _process_review_verdict(project_dir: Path, node_id: str, review_response: str) -> None:
    """
    Parse the reviewer's verdict from the response and update node status.

    The reviewer should include a verdict line like:
      VERDICT: approved
      VERDICT: revision_needed
      VERDICT: blocked

    If no clear verdict is found, default to approved (assume the reviewer
    didn't find blocking issues).
    """
    response_lower = review_response.lower()

    if "verdict: revision_needed" in response_lower or "verdict:revision_needed" in response_lower:
        print(f"  Review verdict: REVISION NEEDED for {node_id}")
        try:
            update_node_status(project_dir, node_id, STATUS_REVISION_NEEDED)
        except KeyError:
            pass
    elif "verdict: blocked" in response_lower or "verdict:blocked" in response_lower:
        print(f"  Review verdict: BLOCKED for {node_id}")
        try:
            update_node_status(project_dir, node_id, STATUS_BLOCKED)
        except KeyError:
            pass
    else:
        # Default: approved → verified (peer review passed)
        print(f"  Review verdict: APPROVED for {node_id}")
        try:
            # Check if this node needs visual tuning
            index = read_index(project_dir)
            node = index.get("nodes", {}).get(node_id, {})
            vs = node.get("visual_status")

            if vs and vs != "tuned":
                # Approved but needs visual tuning before verification
                update_node_status(
                    project_dir, node_id, STATUS_APPROVED,
                    review_status="approved",
                    visual_status="needs_tuning",
                )
                print(f"    (Node requires visual tuning before verification)")
            else:
                update_node_status(
                    project_dir, node_id, STATUS_VERIFIED,
                    review_status="approved",
                )
        except KeyError:
            pass


async def _run_integrator(project_dir: Path, model: str) -> None:
    """Run an integrator session with a sample of verified nodes."""
    index = read_index(project_dir)
    verified = [
        nid for nid, n in index.get("nodes", {}).items()
        if n["status"] == STATUS_VERIFIED
    ]

    if len(verified) < 3:
        print("  Skipping integrator — fewer than 3 verified nodes.")
        return

    # Sample up to 20 verified nodes, prioritizing high fan-out
    sample_size = min(20, len(verified))
    # Sort by number of blocks (fan-out) descending
    nodes = index["nodes"]
    scored = [(nid, len(nodes.get(nid, {}).get("blocks", []))) for nid in verified]
    scored.sort(key=lambda x: -x[1])

    # Take top half by fan-out, fill rest randomly
    high_fanout = [nid for nid, _ in scored[:sample_size // 2]]
    remaining = [nid for nid in verified if nid not in high_fanout]
    random_sample = random.sample(remaining, min(sample_size - len(high_fanout), len(remaining)))
    sample = high_fanout + random_sample

    print(f"  Running integrator with {len(sample)} sampled nodes...")

    status, response = await run_integrator_session(project_dir, sample, model)

    write_session_log(
        project_dir, f"int-{len(verified):03d}", "integrator",
        None, status, f"Coherence check across {len(sample)} verified nodes."
    )
