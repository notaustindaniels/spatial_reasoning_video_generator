"""
DAG Operations
==============

Manages the directed acyclic graph of objectives:
- index.json: lightweight graph structure (IDs, edges, statuses)
- frontier.json: materialized work queue of ready objectives
- nodes/OBJ-NNN/: per-objective directories with meta.json, output.md, reviews/
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ──────────────────────────────────────────────────────────────
# Status Constants
# ──────────────────────────────────────────────────────────────

STATUS_OPEN = "open"
STATUS_IN_PROGRESS = "in_progress"
STATUS_REVIEW = "review"
STATUS_REVISION_NEEDED = "revision_needed"
STATUS_APPROVED = "approved"
STATUS_VERIFIED = "verified"
STATUS_BLOCKED = "blocked"
STATUS_DEAD_END = "dead_end"

VISUAL_STATUS_NONE = None
VISUAL_STATUS_NEEDS_TUNING = "needs_tuning"
VISUAL_STATUS_IN_TUNING = "in_tuning"
VISUAL_STATUS_TUNED = "tuned"

PRIORITY_CRITICAL = "critical"
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"


# ──────────────────────────────────────────────────────────────
# Index Operations
# ──────────────────────────────────────────────────────────────

def create_empty_index(project_dir: Path, seed_version: str = "3.0") -> dict:
    """Create a fresh index.json."""
    index = {
        "seed_version": seed_version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "nodes": {},
        "dead_ends": [],
        "vocabulary_updates": [],
        "constraint_updates": [],
    }
    write_index(project_dir, index)
    return index


def read_index(project_dir: Path) -> dict:
    """Read the current index.json."""
    index_path = project_dir / "index.json"
    if not index_path.exists():
        return {}
    with open(index_path, "r") as f:
        return json.load(f)


def write_index(project_dir: Path, index: dict) -> None:
    """Write index.json atomically."""
    index["updated_at"] = datetime.now(timezone.utc).isoformat()
    index_path = project_dir / "index.json"
    # Write to temp then rename for atomicity
    tmp_path = index_path.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(index, f, indent=2)
    tmp_path.rename(index_path)


def add_node_to_index(
    project_dir: Path,
    node_id: str,
    depends_on: list[str],
    blocks: list[str],
    priority: str = PRIORITY_MEDIUM,
    visual_status: Optional[str] = None,
) -> None:
    """Add a new node to the index."""
    index = read_index(project_dir)
    index["nodes"][node_id] = {
        "status": STATUS_OPEN,
        "depends_on": depends_on,
        "blocks": blocks,
        "priority": priority,
        "review_status": None,
        "visual_status": visual_status,
    }
    write_index(project_dir, index)


def update_node_status(
    project_dir: Path,
    node_id: str,
    status: str,
    review_status: Optional[str] = None,
    visual_status: Optional[str] = None,
) -> None:
    """Update a node's status in the index."""
    index = read_index(project_dir)
    if node_id not in index.get("nodes", {}):
        raise KeyError(f"Node {node_id} not found in index")

    node = index["nodes"][node_id]
    node["status"] = status
    if review_status is not None:
        node["review_status"] = review_status
    if visual_status is not None:
        node["visual_status"] = visual_status

    write_index(project_dir, index)


def mark_dead_end(project_dir: Path, node_id: str) -> None:
    """Mark a node as a dead end and move it."""
    index = read_index(project_dir)
    if node_id in index.get("nodes", {}):
        index["nodes"][node_id]["status"] = STATUS_DEAD_END
    if node_id not in index.get("dead_ends", []):
        index.setdefault("dead_ends", []).append(node_id)
    write_index(project_dir, index)


# ──────────────────────────────────────────────────────────────
# Frontier Operations
# ──────────────────────────────────────────────────────────────

def compute_frontier(project_dir: Path) -> list[dict]:
    """
    Compute the frontier: open objectives whose dependencies are all satisfied.
    Returns list of {id, priority, depends_on, blocks} sorted by priority.
    """
    index = read_index(project_dir)
    nodes = index.get("nodes", {})

    # Set of nodes that are verified/approved (dependencies satisfied)
    satisfied = {
        nid for nid, n in nodes.items()
        if n["status"] in (STATUS_VERIFIED, STATUS_APPROVED)
    }

    priority_order = {
        PRIORITY_CRITICAL: 0,
        PRIORITY_HIGH: 1,
        PRIORITY_MEDIUM: 2,
        PRIORITY_LOW: 3,
    }

    frontier = []
    for nid, node in nodes.items():
        if node["status"] not in (STATUS_OPEN, STATUS_REVISION_NEEDED):
            continue
        deps = node.get("depends_on", [])
        if all(d in satisfied for d in deps):
            frontier.append({
                "id": nid,
                "priority": node.get("priority", PRIORITY_MEDIUM),
                "depends_on": deps,
                "blocks": node.get("blocks", []),
            })

    frontier.sort(key=lambda x: (
        priority_order.get(x["priority"], 99),
        -len(x["blocks"]),  # More blocking = higher priority
    ))

    return frontier


def write_frontier(project_dir: Path, frontier: list[dict]) -> None:
    """Write the materialized frontier.json."""
    frontier_path = project_dir / "frontier.json"
    with open(frontier_path, "w") as f:
        json.dump({
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "objectives": frontier,
        }, f, indent=2)


def refresh_frontier(project_dir: Path) -> list[dict]:
    """Recompute and write the frontier."""
    frontier = compute_frontier(project_dir)
    write_frontier(project_dir, frontier)
    return frontier


# ──────────────────────────────────────────────────────────────
# Node Directory Operations
# ──────────────────────────────────────────────────────────────

def get_node_dir(project_dir: Path, node_id: str) -> Path:
    """Get the directory for a node (under nodes/ or dead_ends/)."""
    node_dir = project_dir / "nodes" / node_id
    if node_dir.exists():
        return node_dir
    dead_dir = project_dir / "dead_ends" / node_id
    if dead_dir.exists():
        return dead_dir
    return node_dir  # Default to nodes/


def create_node_directory(
    project_dir: Path,
    node_id: str,
    description: str,
    depends_on: list[str],
    created_by_session: str = "initializer",
    visual_status: Optional[str] = None,
    notes: str = "",
) -> Path:
    """Create a node's directory with meta.json."""
    node_dir = project_dir / "nodes" / node_id
    node_dir.mkdir(parents=True, exist_ok=True)
    (node_dir / "reviews").mkdir(exist_ok=True)

    if visual_status:
        (node_dir / "critiques").mkdir(exist_ok=True)

    meta = {
        "id": node_id,
        "description": description,
        "created_by_session": created_by_session,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "depends_on": depends_on,
        "visual_status": visual_status,
        "tuning_rounds": 0,
        "notes": notes,
    }

    with open(node_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    return node_dir


def read_node_meta(project_dir: Path, node_id: str) -> dict:
    """Read a node's meta.json."""
    node_dir = get_node_dir(project_dir, node_id)
    meta_path = node_dir / "meta.json"
    if not meta_path.exists():
        return {}
    with open(meta_path, "r") as f:
        return json.load(f)


def read_node_output(project_dir: Path, node_id: str) -> str:
    """Read a node's output.md."""
    node_dir = get_node_dir(project_dir, node_id)
    output_path = node_dir / "output.md"
    if not output_path.exists():
        return ""
    return output_path.read_text()


def read_node_reviews(project_dir: Path, node_id: str) -> list[str]:
    """Read all reviews for a node."""
    node_dir = get_node_dir(project_dir, node_id)
    reviews_dir = node_dir / "reviews"
    if not reviews_dir.exists():
        return []
    reviews = []
    for f in sorted(reviews_dir.glob("*.md")):
        reviews.append(f.read_text())
    return reviews


# ──────────────────────────────────────────────────────────────
# Progress Summary
# ──────────────────────────────────────────────────────────────

def get_progress_summary(project_dir: Path) -> dict:
    """Get a summary of DAG progress."""
    index = read_index(project_dir)
    nodes = index.get("nodes", {})

    summary = {
        "total": len(nodes),
        "open": 0,
        "in_progress": 0,
        "review": 0,
        "revision_needed": 0,
        "approved": 0,
        "verified": 0,
        "blocked": 0,
        "dead_ends": len(index.get("dead_ends", [])),
        "visual_needs_tuning": 0,
        "visual_tuned": 0,
    }

    for node in nodes.values():
        status = node.get("status", STATUS_OPEN)
        if status in summary:
            summary[status] += 1

        vs = node.get("visual_status")
        if vs == VISUAL_STATUS_NEEDS_TUNING:
            summary["visual_needs_tuning"] += 1
        elif vs == VISUAL_STATUS_TUNED:
            summary["visual_tuned"] += 1

    return summary


def print_progress(project_dir: Path) -> None:
    """Print a formatted progress summary."""
    s = get_progress_summary(project_dir)
    total = s["total"]
    if total == 0:
        print("\n  Progress: No objectives created yet.")
        return

    verified = s["verified"]
    pct = (verified / total) * 100 if total > 0 else 0

    print(f"\n  Progress: {verified}/{total} objectives verified ({pct:.1f}%)")
    print(f"    Open: {s['open']} | In Progress: {s['in_progress']} | "
          f"Review: {s['review']} | Approved: {s['approved']}")
    print(f"    Revision Needed: {s['revision_needed']} | Blocked: {s['blocked']} | "
          f"Dead Ends: {s['dead_ends']}")
    if s["visual_needs_tuning"] > 0 or s["visual_tuned"] > 0:
        print(f"    Visual Tuning: {s['visual_tuned']} tuned, "
              f"{s['visual_needs_tuning']} awaiting")
