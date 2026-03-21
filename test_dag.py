#!/usr/bin/env python3
"""
Quick smoke test for DAG logic — verifies index, frontier, and node management
work correctly without needing the Claude SDK or Gemini API.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dag.index import load_index, save_index, update_node_status, get_stats, print_stats
from dag.frontier import compute_frontier, refresh_frontier, claim_objective, release_objective
from dag.nodes import (
    create_node_dir,
    load_node_meta,
    save_node_meta,
    load_node_output,
    assemble_explorer_context,
    assemble_reviewer_context,
    create_dead_end,
)


def test_all():
    """Run all DAG logic tests."""
    passed = 0
    failed = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)

        # ── Test 1: Empty index ──
        print("\n  Test 1: Load empty index")
        index = load_index(project)
        assert index["nodes"] == {}, f"Expected empty nodes, got {index['nodes']}"
        print("    PASS")
        passed += 1

        # ── Test 2: Create nodes ──
        print("  Test 2: Create node directories")
        create_node_dir(project, "OBJ-001", "Project scaffolding", [], ["OBJ-002", "OBJ-003"], "critical")
        create_node_dir(project, "OBJ-002", "Manifest schema", ["OBJ-001"], ["OBJ-004"], "high")
        create_node_dir(project, "OBJ-003", "Virtualized clock", ["OBJ-001"], ["OBJ-004"], "high")
        create_node_dir(project, "OBJ-004", "Orchestrator", ["OBJ-002", "OBJ-003"], [], "normal")
        create_node_dir(
            project, "OBJ-005", "Tunnel geometry",
            ["OBJ-001"], [], "high",
            requires_visual_tuning=True,
        )

        meta = load_node_meta(project, "OBJ-001")
        assert meta["id"] == "OBJ-001"
        assert meta["priority"] == "critical"
        meta5 = load_node_meta(project, "OBJ-005")
        assert meta5["requires_visual_tuning"] is True
        assert meta5["visual_status"] == "needs_tuning"
        print("    PASS")
        passed += 1

        # ── Test 3: Build index ──
        print("  Test 3: Build and save index")
        index = {
            "seed_version": "3.0",
            "harness_version": "1.0",
            "nodes": {
                "OBJ-001": {"status": "open", "depends_on": [], "blocks": ["OBJ-002", "OBJ-003", "OBJ-005"], "priority": "critical", "review_status": None, "visual_status": None},
                "OBJ-002": {"status": "open", "depends_on": ["OBJ-001"], "blocks": ["OBJ-004"], "priority": "high", "review_status": None, "visual_status": None},
                "OBJ-003": {"status": "open", "depends_on": ["OBJ-001"], "blocks": ["OBJ-004"], "priority": "high", "review_status": None, "visual_status": None},
                "OBJ-004": {"status": "open", "depends_on": ["OBJ-002", "OBJ-003"], "blocks": [], "priority": "normal", "review_status": None, "visual_status": None},
                "OBJ-005": {"status": "open", "depends_on": ["OBJ-001"], "blocks": [], "priority": "high", "review_status": None, "visual_status": "needs_tuning"},
            },
            "dead_ends": [],
            "vocabulary_updates": [],
            "constraint_updates": [],
        }
        save_index(project, index)

        loaded = load_index(project)
        assert len(loaded["nodes"]) == 5
        print("    PASS")
        passed += 1

        # ── Test 4: Compute frontier ──
        print("  Test 4: Compute initial frontier")
        frontier = compute_frontier(index)
        assert len(frontier) == 1, f"Expected 1 frontier node (OBJ-001), got {len(frontier)}: {[f['id'] for f in frontier]}"
        assert frontier[0]["id"] == "OBJ-001"
        assert frontier[0]["priority"] == "critical"
        print(f"    Frontier: {[f['id'] for f in frontier]}")
        print("    PASS")
        passed += 1

        # ── Test 5: Claim and release ──
        print("  Test 5: Claim objective")
        claimed = claim_objective(project)
        assert claimed == "OBJ-001"
        idx = load_index(project)
        assert idx["nodes"]["OBJ-001"]["status"] == "in_progress"

        # Frontier should be empty now
        frontier = compute_frontier(idx)
        assert len(frontier) == 0
        print("    PASS")
        passed += 1

        # ── Test 6: Complete OBJ-001, check frontier expands ──
        print("  Test 6: Complete OBJ-001, verify frontier expands")
        update_node_status(project, "OBJ-001", "verified")
        idx = load_index(project)
        frontier = compute_frontier(idx)
        frontier_ids = [f["id"] for f in frontier]
        assert "OBJ-002" in frontier_ids
        assert "OBJ-003" in frontier_ids
        assert "OBJ-005" in frontier_ids
        assert "OBJ-004" not in frontier_ids  # Still blocked by OBJ-002 and OBJ-003
        assert len(frontier_ids) == 3
        print(f"    Frontier: {frontier_ids}")
        print("    PASS")
        passed += 1

        # ── Test 7: Complete OBJ-002 and OBJ-003, OBJ-004 unblocks ──
        print("  Test 7: Complete deps, verify OBJ-004 unblocks")
        update_node_status(project, "OBJ-002", "verified")
        update_node_status(project, "OBJ-003", "verified")
        idx = load_index(project)
        frontier = compute_frontier(idx)
        frontier_ids = [f["id"] for f in frontier]
        assert "OBJ-004" in frontier_ids
        assert "OBJ-005" in frontier_ids
        print(f"    Frontier: {frontier_ids}")
        print("    PASS")
        passed += 1

        # ── Test 8: Write node output and assemble context ──
        print("  Test 8: Write output and assemble explorer context")
        output_path = project / "nodes" / "OBJ-001" / "output.md"
        output_path.write_text("# OBJ-001: Project Scaffolding\n\nCreated package.json and tsconfig.\n")

        context = assemble_explorer_context(project, "OBJ-002")
        assert "OBJ-002" in context
        assert "OBJ-001" in context  # Dependency output included
        assert "Project Scaffolding" in context
        print("    PASS")
        passed += 1

        # ── Test 9: Reviewer context includes output + reviews ──
        print("  Test 9: Assemble reviewer context")
        (project / "nodes" / "OBJ-002" / "output.md").write_text("# OBJ-002: Manifest Schema\n\nZod validation.\n")
        review_dir = project / "nodes" / "OBJ-002" / "reviews"
        review_dir.mkdir(exist_ok=True)
        (review_dir / "REV-001.md").write_text("# Review: Approved\nLooks good.\n")

        context = assemble_reviewer_context(project, "OBJ-002")
        assert "Manifest Schema" in context
        assert "Zod validation" in context
        assert "REV-001" in context
        print("    PASS")
        passed += 1

        # ── Test 10: Dead end creation ──
        print("  Test 10: Create dead end")
        de_path = create_dead_end(
            project, "DE-001",
            "Tried using Sharp for compositing",
            "Sharp cannot handle 3D perspective projection. Need Three.js.",
            original_node_id="OBJ-099",
        )
        assert (de_path / "meta.json").exists()
        assert (de_path / "output.md").exists()
        de_output = (de_path / "output.md").read_text()
        assert "Sharp cannot handle" in de_output
        print("    PASS")
        passed += 1

        # ── Test 11: Stats ──
        print("  Test 11: Get stats")
        idx = load_index(project)
        stats = get_stats(idx)
        assert stats["total_nodes"] == 5
        assert stats["status_counts"]["verified"] == 3
        assert stats["status_counts"]["open"] == 2
        print(f"    Stats: {stats}")
        print("    PASS")
        passed += 1

        # ── Test 12: Priority sorting ──
        print("  Test 12: Frontier priority sorting")
        idx = load_index(project)
        frontier = compute_frontier(idx)
        # OBJ-005 is high priority, OBJ-004 is normal → OBJ-005 should be first
        assert frontier[0]["id"] == "OBJ-005", f"Expected OBJ-005 first, got {frontier[0]['id']}"
        print(f"    Order: {[f['id'] + ' (' + f['priority'] + ')' for f in frontier]}")
        print("    PASS")
        passed += 1

        # ── Test 13: Release objective ──
        print("  Test 13: Release claimed objective")
        claimed = claim_objective(project, "OBJ-004")
        assert claimed == "OBJ-004"
        idx = load_index(project)
        assert idx["nodes"]["OBJ-004"]["status"] == "in_progress"
        release_objective(project, "OBJ-004")
        idx = load_index(project)
        assert idx["nodes"]["OBJ-004"]["status"] == "open"
        print("    PASS")
        passed += 1

        # ── Test 14: Visual status tracking ──
        print("  Test 14: Visual status transitions")
        update_node_status(project, "OBJ-005", "approved", visual_status="needs_tuning")
        idx = load_index(project)
        assert idx["nodes"]["OBJ-005"]["visual_status"] == "needs_tuning"
        update_node_status(project, "OBJ-005", "verified", visual_status="tuned")
        idx = load_index(project)
        assert idx["nodes"]["OBJ-005"]["visual_status"] == "tuned"
        print("    PASS")
        passed += 1

    # ── Summary ──
    print("\n" + "-" * 50)
    print(f"  Results: {passed} passed, {failed} failed")
    print("-" * 50)

    if failed == 0:
        print("\n  ALL TESTS PASSED")
        return 0
    else:
        print(f"\n  {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    print("=" * 50)
    print("  DEPTHKIT HARNESS — DAG LOGIC TESTS")
    print("=" * 50)
    sys.exit(test_all())
