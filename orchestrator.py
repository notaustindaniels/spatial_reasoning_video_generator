"""
Orchestrator
=============

The main session dispatch loop for the depthkit harness.

Responsibilities:
- Read the progress map and identify the current frontier.
- Route sessions to the appropriate role.
- Trigger review sessions after explorer sessions commit.
- Trigger Director Agent sessions after visual-output objectives pass review.
- Enforce the HITL Circuit Breaker.
- Assemble context for each session.
- Update the progress map when nodes change status.
- Manage concurrency (sequential in v1, parallel later).
"""

import asyncio
import json
import random
from pathlib import Path
from typing import Optional

from client import create_client
from dag.index import load_index, save_index, update_node_status, print_stats
from dag.frontier import (
    compute_frontier,
    refresh_frontier,
    claim_objective,
    release_objective,
)
from dag.nodes import (
    load_node_meta,
    save_node_meta,
    list_critiques,
    load_node_output,
)
from prompts_loader import (
    get_initializer_prompt,
    get_explorer_prompt,
    get_reviewer_prompt,
    get_integrator_prompt,
    get_synthesizer_prompt,
    copy_seed_to_project,
)
from roles.session import run_session, AUTO_CONTINUE_DELAY_SECONDS
from roles.director import run_director_review, hitl_gate, save_critique


async def run_orchestrator(
    project_dir: Path,
    seed_path: Path,
    model: str,
    max_iterations: Optional[int] = None,
    max_turns: int = 1000,
    integrator_cadence: int = 15,
    target_node: Optional[str] = None,
    role_override: Optional[str] = None,
) -> None:
    """
    Run the orchestrator loop.

    Args:
        project_dir: Root directory for the project
        seed_path: Path to the seed document
        model: Claude model for agent sessions
        max_iterations: Maximum number of sessions (None for unlimited)
        max_turns: Max turns per session
        integrator_cadence: Run integrator every N explorer completions
        target_node: If set, work on this specific node instead of auto-selecting
        role_override: If set, force this role instead of auto-detecting
    """
    print("\n" + "=" * 70)
    print("  DEPTHKIT MULTI-AGENT HARNESS")
    print("=" * 70)
    print(f"\n  Project: {project_dir}")
    print(f"  Seed: {seed_path}")
    print(f"  Model: {model}")
    if max_iterations:
        print(f"  Max iterations: {max_iterations}")
    else:
        print(f"  Max iterations: unlimited")
    print()

    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Copy seed into project
    copy_seed_to_project(project_dir, seed_path)

    # Determine current state
    index = load_index(project_dir)
    is_initialized = bool(index.get("nodes"))

    if not is_initialized and role_override not in ("initializer",):
        print("  Project not initialized. Running initializer first.")
        role_override = "initializer"

    # Create required directories
    (project_dir / "nodes").mkdir(exist_ok=True)
    (project_dir / "dead_ends").mkdir(exist_ok=True)
    (project_dir / "sessions").mkdir(exist_ok=True)
    (project_dir / "synthesis").mkdir(exist_ok=True)

    # Tracking
    iteration = 0
    explorer_completions_since_integrator = 0

    while True:
        iteration += 1

        if max_iterations and iteration > max_iterations:
            print(f"\n  Reached max iterations ({max_iterations}).")
            break

        # Refresh state
        index = load_index(project_dir)
        is_initialized = bool(index.get("nodes"))

        # ── Determine role for this iteration ──

        if role_override:
            role = role_override
            role_override = None  # Only override once
        elif not is_initialized:
            role = "initializer"
        elif _needs_review(index):
            role = "reviewer"
        elif _needs_visual_tuning(index, project_dir):
            role = "director"
        elif explorer_completions_since_integrator >= integrator_cadence:
            role = "integrator"
        elif _has_frontier(index):
            role = "explorer"
        elif _all_verified(index):
            role = "synthesizer"
        else:
            print("\n  No work available. All frontier nodes are claimed or blocked.")
            print("  Waiting for in-progress nodes to complete...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)
            continue

        # ── Print session header ──

        _print_session_header(iteration, role, index)

        # ── Dispatch by role ──

        if role == "initializer":
            await _run_initializer(project_dir, model, max_turns)

        elif role == "explorer":
            node_id = target_node or _pick_explorer_target(project_dir, index)
            if node_id:
                status = await _run_explorer(project_dir, model, max_turns, node_id)
                if status == "continue":
                    explorer_completions_since_integrator += 1
            else:
                print("  No frontier objectives available.")

        elif role == "reviewer":
            node_id = target_node or _pick_review_target(index)
            if node_id:
                await _run_reviewer(project_dir, model, max_turns, node_id)
            else:
                print("  No nodes awaiting review.")

        elif role == "director":
            node_id = target_node or _pick_visual_tuning_target(index)
            if node_id:
                await _run_director(project_dir, model, max_turns, node_id)
            else:
                print("  No nodes awaiting visual tuning.")

        elif role == "integrator":
            await _run_integrator(project_dir, model, max_turns, index)
            explorer_completions_since_integrator = 0

        elif role == "synthesizer":
            await _run_synthesizer(project_dir, model, max_turns, index)
            break  # Synthesis is the final step

        # Reset target_node after first use
        target_node = None

        # Auto-continue delay
        print(f"\n  Next session in {AUTO_CONTINUE_DELAY_SECONDS}s...")
        print_stats(load_index(project_dir))
        await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

    # ── Final summary ──
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\n  Project: {project_dir}")
    print_stats(load_index(project_dir))
    print("\n  Done!")


# ── Role dispatch helpers ──


async def _run_initializer(project_dir: Path, model: str, max_turns: int) -> None:
    """Run the initializer session."""
    prompt = get_initializer_prompt()
    client = create_client(project_dir, model, "initializer", prompt, max_turns)

    async with client:
        status, response = await run_session(client, prompt, "initializer")


async def _run_explorer(
    project_dir: Path, model: str, max_turns: int, node_id: str
) -> str:
    """Run an explorer session for a specific objective."""
    # Claim the objective
    claimed = claim_objective(project_dir, node_id)
    if not claimed:
        print(f"  Could not claim {node_id}.")
        return "error"

    prompt = get_explorer_prompt(project_dir, node_id)

    system = (
        f"You are an expert full-stack developer building depthkit — "
        f"a custom Node.js 2.5D video engine. "
        f"Your current objective is {node_id}."
    )

    client = create_client(project_dir, model, "explorer", system, max_turns)

    try:
        async with client:
            status, response = await run_session(client, prompt, "explorer")

        if status == "continue":
            # Move to review status
            update_node_status(project_dir, node_id, "review")
            refresh_frontier(project_dir)
        else:
            # Release on error
            release_objective(project_dir, node_id)

        return status

    except Exception as e:
        print(f"  Explorer error: {e}")
        release_objective(project_dir, node_id)
        return "error"


async def _run_reviewer(
    project_dir: Path, model: str, max_turns: int, node_id: str
) -> None:
    """Run a reviewer session for a specific node."""
    prompt = get_reviewer_prompt(project_dir, node_id)

    system = (
        f"You are an independent peer reviewer for depthkit. "
        f"You are reviewing objective {node_id}. "
        f"You did NOT produce this work. Be constructive but thorough."
    )

    client = create_client(project_dir, model, "reviewer", system, max_turns)

    async with client:
        status, response = await run_session(client, prompt, "reviewer")

    # After review, check if the reviewer's verdict is in the response
    # and update status accordingly
    response_lower = response.lower()
    if "verdict: approved" in response_lower or "## verdict: approved" in response_lower:
        meta = load_node_meta(project_dir, node_id)
        if meta and meta.get("requires_visual_tuning"):
            update_node_status(project_dir, node_id, "approved", visual_status="needs_tuning")
        else:
            update_node_status(project_dir, node_id, "verified")
        print(f"  [REVIEWER] {node_id} → approved")
    elif "verdict: revision_needed" in response_lower:
        update_node_status(project_dir, node_id, "revision_needed")
        print(f"  [REVIEWER] {node_id} → revision_needed")
    elif "verdict: blocked" in response_lower:
        update_node_status(project_dir, node_id, "blocked")
        print(f"  [REVIEWER] {node_id} → blocked")
    else:
        # Default: mark as approved if we can't parse the verdict
        print(f"  [REVIEWER] Could not parse verdict from response. Defaulting to approved.")
        meta = load_node_meta(project_dir, node_id)
        if meta and meta.get("requires_visual_tuning"):
            update_node_status(project_dir, node_id, "approved", visual_status="needs_tuning")
        else:
            update_node_status(project_dir, node_id, "verified")

    refresh_frontier(project_dir)


async def _run_director(
    project_dir: Path, model: str, max_turns: int, node_id: str
) -> None:
    """Run the Director Agent visual tuning loop for a node."""
    meta = load_node_meta(project_dir, node_id)
    if not meta:
        print(f"  [DIRECTOR] Node {node_id} not found.")
        return

    test_render_path = project_dir / "nodes" / node_id / "test_render.mp4"

    if not test_render_path.exists():
        # Need the explorer to render a test clip first
        print(f"  [DIRECTOR] No test_render.mp4 for {node_id}. Running explorer to generate one.")

        prompt = get_explorer_prompt(project_dir, node_id)
        prompt += (
            "\n\n## ADDITIONAL INSTRUCTION: RENDER A TEST CLIP\n\n"
            "After implementing/updating this objective, render a short test video "
            "(10-30 seconds) and save it as `test_render.mp4` in your node directory "
            f"(`nodes/{node_id}/test_render.mp4`). This will be reviewed by the "
            "Director Agent for visual quality."
        )

        system = f"You are building depthkit. Render a test clip for {node_id}."
        client = create_client(project_dir, model, "explorer", system, max_turns)

        async with client:
            await run_session(client, prompt, "explorer")

    if not test_render_path.exists():
        print(f"  [DIRECTOR] Still no test_render.mp4. Skipping visual tuning.")
        return

    # Load prior critiques
    critique_files = list_critiques(project_dir, node_id)
    prior_critiques = []
    critique_dir = project_dir / "nodes" / node_id / "critiques"
    for cf in critique_files:
        prior_critiques.append((critique_dir / cf).read_text())

    tuning_round = meta.get("tuning_rounds", 0) + 1

    # Run Gemini review
    critique = run_director_review(
        test_render_path=test_render_path,
        objective_description=meta.get("description", ""),
        geometry_name=_extract_geometry_name(meta),
        camera_path_name=_extract_camera_name(meta),
        prior_critiques=prior_critiques,
    )

    if not critique:
        print("  [DIRECTOR] No critique generated. Skipping.")
        return

    # HITL Gate
    decision, approved_text = hitl_gate(critique)

    if decision in ("approve", "modify", "override"):
        # Save the critique
        save_critique(project_dir, node_id, approved_text, tuning_round)

        # Update tuning round count
        meta["tuning_rounds"] = tuning_round
        save_node_meta(project_dir, node_id, meta)

        # Now run the explorer to apply the feedback
        feedback_prompt = get_explorer_prompt(project_dir, node_id)
        feedback_prompt += (
            f"\n\n## DIRECTOR AGENT FEEDBACK (HUMAN-APPROVED)\n\n"
            f"The following visual feedback has been approved by the human reviewer. "
            f"Apply these adjustments to the geometry/camera parameters and re-render.\n\n"
            f"{approved_text}\n\n"
            f"After adjusting, render a new test_render.mp4 to `nodes/{node_id}/test_render.mp4`."
        )

        system = f"You are applying Director feedback to {node_id}."
        client = create_client(project_dir, model, "explorer", system, max_turns)

        async with client:
            await run_session(client, feedback_prompt, "explorer")

        # Check if the human wants to sign off
        print("\n  [HITL] Is the visual quality acceptable?")
        signoff = input("  Sign off and mark as tuned? (y/n): ").strip().lower()

        if signoff == "y":
            update_node_status(project_dir, node_id, "verified", visual_status="tuned")
            print(f"  [DIRECTOR] {node_id} → verified (visually tuned)")
        else:
            update_node_status(project_dir, node_id, "approved", visual_status="in_progress")
            print(f"  [DIRECTOR] {node_id} → continuing tuning")

    elif decision == "reject":
        print(f"  [DIRECTOR] Critique rejected. {node_id} remains in visual tuning.")

    refresh_frontier(project_dir)


async def _run_integrator(
    project_dir: Path, model: str, max_turns: int, index: dict
) -> None:
    """Run an integrator coherence check."""
    # Sample verified nodes for review
    verified_ids = [
        nid for nid, node in index.get("nodes", {}).items()
        if node.get("status") == "verified"
    ]

    if not verified_ids:
        print("  No verified nodes to integrate.")
        return

    # Sample up to 20 nodes, prioritizing high-fan-out nodes
    sample_size = min(20, len(verified_ids))
    sample = random.sample(verified_ids, sample_size)

    prompt = get_integrator_prompt(project_dir, sample)
    system = "You are the integrator agent for depthkit. Check for coherence across verified nodes."
    client = create_client(project_dir, model, "integrator", system, max_turns)

    async with client:
        await run_session(client, prompt, "integrator")


async def _run_synthesizer(
    project_dir: Path, model: str, max_turns: int, index: dict
) -> None:
    """Run the synthesizer to assemble final deliverables."""
    verified_ids = [
        nid for nid, node in index.get("nodes", {}).items()
        if node.get("status") == "verified"
    ]

    if not verified_ids:
        print("  No verified nodes to synthesize.")
        return

    prompt = get_synthesizer_prompt(project_dir, verified_ids)
    system = "You are the synthesizer for depthkit. Assemble verified outputs into the final engine."
    client = create_client(project_dir, model, "synthesizer", system, max_turns)

    async with client:
        await run_session(client, prompt, "synthesizer")


# ── State inspection helpers ──


def _needs_review(index: dict) -> bool:
    """Check if any nodes are awaiting review."""
    return any(
        n.get("status") == "review"
        for n in index.get("nodes", {}).values()
    )


def _needs_visual_tuning(index: dict, project_dir: Path) -> bool:
    """Check if any approved nodes need visual tuning."""
    for nid, node in index.get("nodes", {}).items():
        if (
            node.get("status") == "approved"
            and node.get("visual_status") in ("needs_tuning", "in_progress")
        ):
            return True
    return False


def _has_frontier(index: dict) -> bool:
    """Check if the frontier has any available objectives."""
    frontier = compute_frontier(index)
    return len(frontier) > 0


def _all_verified(index: dict) -> bool:
    """Check if all nodes are verified (or dead-ended)."""
    return all(
        n.get("status") in ("verified", "dead_end")
        for n in index.get("nodes", {}).values()
    )


def _pick_explorer_target(project_dir: Path, index: dict) -> Optional[str]:
    """Pick the highest-priority frontier objective."""
    frontier = compute_frontier(index)
    if not frontier:
        return None
    return frontier[0]["id"]


def _pick_review_target(index: dict) -> Optional[str]:
    """Pick a node awaiting review."""
    for nid, node in index.get("nodes", {}).items():
        if node.get("status") == "review":
            return nid
    return None


def _pick_visual_tuning_target(index: dict) -> Optional[str]:
    """Pick a node awaiting visual tuning."""
    for nid, node in index.get("nodes", {}).items():
        if (
            node.get("status") == "approved"
            and node.get("visual_status") in ("needs_tuning", "in_progress")
        ):
            return nid
    return None


def _extract_geometry_name(meta: dict) -> str:
    """Try to extract geometry name from node description."""
    desc = meta.get("description", "").lower()
    for geo in ["stage", "tunnel", "canyon", "flyover", "diorama", "portal", "panorama", "close_up"]:
        if geo in desc:
            return geo
    return "unknown"


def _extract_camera_name(meta: dict) -> str:
    """Try to extract camera path name from node description."""
    desc = meta.get("description", "").lower()
    presets = [
        "static", "slow_push_forward", "slow_pull_back",
        "lateral_track_left", "lateral_track_right",
        "tunnel_push_forward", "flyover_glide",
        "gentle_float", "dramatic_push", "crane_up", "dolly_zoom",
    ]
    for preset in presets:
        if preset.replace("_", " ") in desc or preset in desc:
            return preset
    return "unknown"


def _print_session_header(iteration: int, role: str, index: dict) -> None:
    """Print a formatted session header."""
    print("\n" + "=" * 70)
    print(f"  SESSION {iteration}: {role.upper()}")
    print("=" * 70)
    print_stats(index)
    print()
