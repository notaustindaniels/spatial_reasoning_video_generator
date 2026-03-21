"""
DAG Index Manager
=================

Reads and writes the progress map index (index.json).
The index holds only graph structure: node IDs, edges, statuses.
Node content lives in per-node directories.
"""

import json
from pathlib import Path
from typing import Optional

# Valid node statuses (ordered by lifecycle)
STATUSES = [
    "open",             # Ready for exploration
    "in_progress",      # Claimed by an explorer
    "review",           # Exploration done, awaiting peer review
    "revision_needed",  # Reviewer requested changes
    "approved",         # Peer review passed
    "visual_tuning",   # Awaiting Director Agent tuning (visual nodes only)
    "verified",         # Fully verified (and visually tuned if applicable)
    "blocked",          # Dependency became invalid
    "dead_end",         # Explored and documented as unviable
]

VISUAL_STATUSES = [None, "needs_tuning", "in_progress", "tuned"]


def load_index(project_dir: Path) -> dict:
    """Load the progress map index from index.json."""
    index_path = project_dir / "index.json"
    if not index_path.exists():
        return {
            "seed_version": "3.0",
            "harness_version": "1.0",
            "nodes": {},
            "dead_ends": [],
            "vocabulary_updates": [],
            "constraint_updates": [],
        }
    with open(index_path, "r") as f:
        return json.load(f)


def save_index(project_dir: Path, index: dict) -> None:
    """Save the progress map index to index.json."""
    index_path = project_dir / "index.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


def get_node(index: dict, node_id: str) -> Optional[dict]:
    """Get a node's entry from the index."""
    return index.get("nodes", {}).get(node_id)


def update_node_status(
    project_dir: Path,
    node_id: str,
    status: str,
    visual_status: Optional[str] = None,
) -> dict:
    """
    Update a node's status in the index. Returns the updated index.

    Args:
        project_dir: Project root directory
        node_id: The objective ID (e.g., "OBJ-001")
        status: New status value
        visual_status: Optional visual tuning status
    """
    if status not in STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {STATUSES}")
    if visual_status is not None and visual_status not in VISUAL_STATUSES:
        raise ValueError(
            f"Invalid visual_status '{visual_status}'. Must be one of: {VISUAL_STATUSES}"
        )

    index = load_index(project_dir)

    if node_id not in index["nodes"]:
        raise KeyError(f"Node '{node_id}' not found in index")

    index["nodes"][node_id]["status"] = status
    if visual_status is not None:
        index["nodes"][node_id]["visual_status"] = visual_status

    save_index(project_dir, index)
    return index


def get_stats(index: dict) -> dict:
    """Get summary statistics from the index."""
    nodes = index.get("nodes", {})
    status_counts = {}
    for node in nodes.values():
        s = node.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    visual_counts = {}
    for node in nodes.values():
        vs = node.get("visual_status")
        if vs is not None:
            visual_counts[vs] = visual_counts.get(vs, 0) + 1

    return {
        "total_nodes": len(nodes),
        "status_counts": status_counts,
        "visual_counts": visual_counts,
        "dead_ends": len(index.get("dead_ends", [])),
    }


def print_stats(index: dict) -> None:
    """Print a formatted summary of DAG progress."""
    stats = get_stats(index)
    total = stats["total_nodes"]

    if total == 0:
        print("  Progress: No objectives created yet.")
        return

    verified = stats["status_counts"].get("verified", 0)
    pct = (verified / total) * 100 if total > 0 else 0

    print(f"  Progress: {verified}/{total} objectives verified ({pct:.1f}%)")

    for status, count in sorted(stats["status_counts"].items()):
        print(f"    {status}: {count}")

    if stats["visual_counts"]:
        print(f"  Visual tuning:")
        for vs, count in sorted(stats["visual_counts"].items()):
            print(f"    {vs}: {count}")

    if stats["dead_ends"] > 0:
        print(f"  Dead ends: {stats['dead_ends']}")
