"""
Node Directory Manager
======================

Manages per-objective directories under nodes/.
Each node has: meta.json, output.md, reviews/, and optionally
critiques/ and test_render.mp4 for visual-tuning nodes.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def create_node_dir(
    project_dir: Path,
    node_id: str,
    description: str,
    depends_on: list[str],
    blocks: list[str],
    priority: str = "normal",
    requires_visual_tuning: bool = False,
    created_by_session: str = "initializer",
) -> Path:
    """
    Create a node directory with meta.json.

    Returns the path to the created directory.
    """
    node_dir = project_dir / "nodes" / node_id
    node_dir.mkdir(parents=True, exist_ok=True)
    (node_dir / "reviews").mkdir(exist_ok=True)

    if requires_visual_tuning:
        (node_dir / "critiques").mkdir(exist_ok=True)

    meta = {
        "id": node_id,
        "description": description,
        "depends_on": depends_on,
        "blocks": blocks,
        "priority": priority,
        "created_by_session": created_by_session,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "requires_visual_tuning": requires_visual_tuning,
        "visual_status": "needs_tuning" if requires_visual_tuning else None,
        "tuning_rounds": 0,
        "notes": "",
    }

    with open(node_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    return node_dir


def load_node_meta(project_dir: Path, node_id: str) -> Optional[dict]:
    """Load a node's meta.json."""
    meta_path = project_dir / "nodes" / node_id / "meta.json"
    if not meta_path.exists():
        return None
    with open(meta_path, "r") as f:
        return json.load(f)


def save_node_meta(project_dir: Path, node_id: str, meta: dict) -> None:
    """Save a node's meta.json."""
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path = project_dir / "nodes" / node_id / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)


def load_node_output(project_dir: Path, node_id: str) -> Optional[str]:
    """Load a node's output.md content."""
    output_path = project_dir / "nodes" / node_id / "output.md"
    if not output_path.exists():
        return None
    return output_path.read_text()


def list_reviews(project_dir: Path, node_id: str) -> list[str]:
    """List review filenames for a node."""
    review_dir = project_dir / "nodes" / node_id / "reviews"
    if not review_dir.exists():
        return []
    return sorted(f.name for f in review_dir.glob("REV-*.md"))


def list_critiques(project_dir: Path, node_id: str) -> list[str]:
    """List visual critique filenames for a node."""
    critique_dir = project_dir / "nodes" / node_id / "critiques"
    if not critique_dir.exists():
        return []
    return sorted(f.name for f in critique_dir.glob("VC-*.md"))


def create_dead_end(
    project_dir: Path,
    dead_end_id: str,
    description: str,
    reason: str,
    original_node_id: Optional[str] = None,
) -> Path:
    """Create a dead-end directory documenting a failed path."""
    de_dir = project_dir / "dead_ends" / dead_end_id
    de_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "id": dead_end_id,
        "description": description,
        "original_node_id": original_node_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(de_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    (de_dir / "output.md").write_text(
        f"# Dead End: {dead_end_id}\n\n"
        f"## What Was Tried\n{description}\n\n"
        f"## Why It Failed\n{reason}\n"
    )

    return de_dir


def assemble_explorer_context(project_dir: Path, node_id: str) -> str:
    """
    Assemble the context files an explorer needs for a given objective.

    Returns a formatted string containing:
    - The target node's meta.json
    - The output.md of each dependency node
    """
    parts = []

    # Target node meta
    meta = load_node_meta(project_dir, node_id)
    if meta:
        parts.append(f"## Target Objective: {node_id}\n```json\n{json.dumps(meta, indent=2)}\n```\n")

    # Dependency outputs
    deps = meta.get("depends_on", []) if meta else []
    for dep_id in deps:
        dep_output = load_node_output(project_dir, dep_id)
        if dep_output:
            parts.append(f"## Dependency Output: {dep_id}\n{dep_output}\n")
        else:
            dep_meta = load_node_meta(project_dir, dep_id)
            if dep_meta:
                parts.append(
                    f"## Dependency: {dep_id} (no output yet)\n"
                    f"Description: {dep_meta.get('description', 'N/A')}\n"
                )

    return "\n---\n\n".join(parts)


def assemble_reviewer_context(project_dir: Path, node_id: str) -> str:
    """
    Assemble the context files a reviewer needs.

    Returns a formatted string containing:
    - The target node's meta.json and output.md
    - The output.md of each dependency for context
    """
    parts = []

    # Target node meta + output
    meta = load_node_meta(project_dir, node_id)
    if meta:
        parts.append(f"## Node Under Review: {node_id}\n```json\n{json.dumps(meta, indent=2)}\n```\n")

    output = load_node_output(project_dir, node_id)
    if output:
        parts.append(f"## Node Output\n{output}\n")
    else:
        parts.append("## Node Output\n*No output.md found — the explorer may not have committed yet.*\n")

    # Dependency outputs for context
    deps = meta.get("depends_on", []) if meta else []
    for dep_id in deps:
        dep_output = load_node_output(project_dir, dep_id)
        if dep_output:
            parts.append(f"## Dependency Context: {dep_id}\n{dep_output}\n")

    # Prior reviews
    reviews = list_reviews(project_dir, node_id)
    if reviews:
        review_dir = project_dir / "nodes" / node_id / "reviews"
        for rev_name in reviews:
            rev_text = (review_dir / rev_name).read_text()
            parts.append(f"## Prior Review: {rev_name}\n{rev_text}\n")

    return "\n---\n\n".join(parts)


def assemble_integrator_context(project_dir: Path, sample_ids: list[str]) -> str:
    """
    Assemble context for an integrator session from a sample of verified nodes.
    """
    parts = []
    for node_id in sample_ids:
        meta = load_node_meta(project_dir, node_id)
        output = load_node_output(project_dir, node_id)
        if meta:
            parts.append(
                f"## {node_id}: {meta.get('description', 'N/A')}\n"
                f"Status: {meta.get('visual_status', 'N/A') or 'non-visual'}\n"
            )
        if output:
            # Truncate long outputs for integrator breadth
            if len(output) > 3000:
                output = output[:3000] + "\n\n*[truncated for integrator context]*"
            parts.append(output + "\n")

    return "\n---\n\n".join(parts)
