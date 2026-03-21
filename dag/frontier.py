"""
Frontier Manager
================

Computes and materializes the frontier — the set of open objectives
whose dependencies are all satisfied (verified or dead-ended).

The frontier is the scheduling backbone: the orchestrator picks
the next session's work from the frontier.
"""

import json
from pathlib import Path
from typing import Optional

from dag.index import load_index, save_index


def compute_frontier(index: dict) -> list[dict]:
    """
    Compute the frontier: open objectives whose dependencies are all satisfied.

    A dependency is "satisfied" if its status is 'verified' or 'dead_end'.
    An objective is "available" if its status is 'open' and all deps are satisfied.

    Returns a list of frontier entries sorted by priority, each containing:
        - id: The objective ID
        - priority: The priority level
        - blocks_count: How many downstream objectives this unblocks
        - depends_on: List of dependency IDs
    """
    nodes = index.get("nodes", {})
    satisfied_ids = set()

    for node_id, node in nodes.items():
        if node.get("status") in ("verified", "dead_end"):
            satisfied_ids.add(node_id)

    # Also count dead ends from the dead_ends list
    for de_id in index.get("dead_ends", []):
        satisfied_ids.add(de_id)

    frontier = []
    for node_id, node in nodes.items():
        if node.get("status") != "open":
            continue

        deps = node.get("depends_on", [])
        if all(dep in satisfied_ids for dep in deps):
            blocks = node.get("blocks", [])
            priority_rank = _priority_rank(node.get("priority", "normal"))

            frontier.append({
                "id": node_id,
                "priority": node.get("priority", "normal"),
                "priority_rank": priority_rank,
                "blocks_count": len(blocks),
                "depends_on": deps,
            })

    # Sort: higher priority first, then by how many things it unblocks
    frontier.sort(key=lambda x: (-x["priority_rank"], -x["blocks_count"]))

    return frontier


def save_frontier(project_dir: Path, frontier: list[dict]) -> None:
    """Materialize the frontier to frontier.json."""
    path = project_dir / "frontier.json"
    with open(path, "w") as f:
        json.dump(frontier, f, indent=2)


def load_frontier(project_dir: Path) -> list[dict]:
    """Load the materialized frontier."""
    path = project_dir / "frontier.json"
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def refresh_frontier(project_dir: Path) -> list[dict]:
    """Recompute the frontier from the index and save it."""
    index = load_index(project_dir)
    frontier = compute_frontier(index)
    save_frontier(project_dir, frontier)
    return frontier


def claim_objective(project_dir: Path, node_id: Optional[str] = None) -> Optional[str]:
    """
    Claim the highest-priority frontier objective for an explorer session.

    If node_id is provided, claim that specific objective.
    Otherwise, claim the top of the frontier.

    Returns the claimed objective ID, or None if the frontier is empty.
    """
    index = load_index(project_dir)
    frontier = compute_frontier(index)

    if not frontier:
        return None

    if node_id:
        # Verify it's in the frontier
        if not any(f["id"] == node_id for f in frontier):
            print(f"  Warning: {node_id} is not in the frontier. Skipping.")
            return None
        target_id = node_id
    else:
        target_id = frontier[0]["id"]

    # Mark as in_progress
    index["nodes"][target_id]["status"] = "in_progress"
    save_index(project_dir, index)

    # Refresh the materialized frontier
    new_frontier = compute_frontier(index)
    save_frontier(project_dir, new_frontier)

    return target_id


def release_objective(project_dir: Path, node_id: str) -> None:
    """Release a claimed objective back to open status (e.g., on agent failure)."""
    index = load_index(project_dir)
    if node_id in index["nodes"] and index["nodes"][node_id]["status"] == "in_progress":
        index["nodes"][node_id]["status"] = "open"
        save_index(project_dir, index)
        refresh_frontier(project_dir)


def _priority_rank(priority: str) -> int:
    """Convert priority string to numeric rank for sorting."""
    return {
        "critical": 4,
        "high": 3,
        "normal": 2,
        "low": 1,
    }.get(priority, 2)
