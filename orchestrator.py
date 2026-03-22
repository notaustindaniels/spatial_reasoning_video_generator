"""
Orchestrator
============

The main loop managing the harness lifecycle:
1. Initialization deliberation (two architects discover the decomposition)
2. Exploration deliberation loop (spec author + challenger per objective)
3. Periodic integration (monologue coherence checks)
4. Convergence detection + synthesis

All init and explore phases use deliberation (two-agent conversation).
Integrator and synthesizer remain monologue (single-agent).
"""

import asyncio
import os
import re
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo


# ──────────────────────────────────────────────────────────────
# Peak-Hour Scheduling
# ──────────────────────────────────────────────────────────────

ET = ZoneInfo("America/New_York")

# Anthropic peak pricing: 8 AM – 2 PM ET, weekdays
PEAK_START_HOUR = 8
PEAK_END_HOUR = 14


def _is_peak() -> bool:
    """Check if current time is within Anthropic peak pricing hours."""
    now_et = datetime.now(ET)
    weekday = now_et.weekday()  # 0=Mon, 6=Sun
    hour = now_et.hour
    return weekday < 5 and PEAK_START_HOUR <= hour < PEAK_END_HOUR


def _next_offpeak() -> datetime:
    """Return the next off-peak start time as a UTC datetime."""
    now_et = datetime.now(ET)
    # If peak today, off-peak starts at PEAK_END_HOUR today
    candidate = now_et.replace(hour=PEAK_END_HOUR, minute=0, second=0, microsecond=0)
    if candidate > now_et:
        return candidate.astimezone(timezone.utc)
    # Otherwise, check tomorrow
    tomorrow = now_et + timedelta(days=1)
    # Skip to Monday if tomorrow is weekend
    while tomorrow.weekday() >= 5:
        tomorrow += timedelta(days=1)
    # Off-peak resumes at midnight, but next peak is 8 AM — so 00:00 is fine
    # Actually, off-peak starts right at PEAK_END_HOUR, or at midnight after a weekend
    return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


async def _await_offpeak() -> None:
    """If currently in peak hours, sleep until off-peak resumes."""
    if os.environ.get("IGNORE_PEAK_HOURS", "").lower() in ("true", "1", "yes"):
        return

    if not _is_peak():
        return

    resume = _next_offpeak()
    now = datetime.now(timezone.utc)
    wait_seconds = (resume - now).total_seconds()

    if wait_seconds <= 0:
        return

    resume_et = resume.astimezone(ET)
    print(f"\n  ⏸  PEAK HOURS — Anthropic peak pricing is active (8 AM – 2 PM ET, weekdays).")
    print(f"     Pausing until {resume_et.strftime('%I:%M %p ET')} ({int(wait_seconds // 60)} minutes).")
    print(f"     Set IGNORE_PEAK_HOURS=true in .env to override.\n")

    await asyncio.sleep(wait_seconds)

from dag import (
    read_index,
    refresh_frontier,
    update_node_status,
    get_progress_summary,
    print_progress,
    mark_dead_end,
    read_integrator_coverage,
    write_integrator_coverage,
    read_node_meta,
    cluster_verified_by_category,
    STATUS_OPEN,
    STATUS_IN_PROGRESS,
    STATUS_REVIEW,
    STATUS_REVISION_NEEDED,
    STATUS_APPROVED,
    STATUS_VERIFIED,
    STATUS_BLOCKED,
)
from agent import (
    run_deliberation,
    run_integrator_session,
    run_synthesizer_chunk_session,
    run_synthesizer_rollup_session,
    run_manifest_session,
    write_session_log,
    append_to_feed,
    save_transcript,
    print_session_header,
)
from context import (
    build_init_deliberation_context,
    build_explore_deliberation_context,
    load_prompt,
    PROMPTS_DIR,
)


# ──────────────────────────────────────────────────────────────
# Orchestrator Main Loop
# ──────────────────────────────────────────────────────────────

async def run_harness(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
    auto_continue_delay: int = 3,
    integrator_cadence: int = 15,
    init_safety_cap: int = 50,
    explore_safety_cap: int = 30,
) -> None:
    """
    Run the full harness lifecycle.

    Args:
        project_dir: Root directory for the project.
        model: Claude model to use.
        max_iterations: Max explorer iterations (None = unlimited).
        auto_continue_delay: Seconds between sessions.
        integrator_cadence: Run integrator every N explorer completions.
        init_safety_cap: Max rounds for init deliberation (converges when agents agree).
        explore_safety_cap: Max rounds per explore deliberation (converges when agents agree).
    """
    print("\n" + "=" * 70)
    print("  DEPTHKIT MULTI-AGENT HARNESS (Deliberation Mode)")
    print("=" * 70)
    print(f"\n  Project directory: {project_dir}")
    print(f"  Model: {model}")
    print(f"  Max iterations: {max_iterations or 'Unlimited'}")
    print(f"  Init deliberation: converges when agreed (safety cap: {init_safety_cap})")
    print(f"  Explore deliberation: converges when agreed (safety cap: {explore_safety_cap})")
    print(f"  Integrator cadence: every {integrator_cadence} explorations")
    print(f"\n  Watch conclusions live:")
    print(f"    tail -f {project_dir}/feed.md")
    print()

    # ── Phase 1: Initialization Deliberation ─────────────────
    project_dir.mkdir(parents=True, exist_ok=True)

    index = read_index(project_dir)
    is_fresh = not index or not index.get("nodes")

    if is_fresh:
        await _await_offpeak()
        print_session_header("INITIALIZATION DELIBERATION", 1)
        print("  Two architects will converse to discover the project decomposition.")
        print("  The number of objectives is NOT predetermined — it emerges from the conversation.")
        print()
        _setup_project(project_dir)

        shared_context = build_init_deliberation_context(project_dir)
        prompt_a = load_prompt("architect_a_prompt")
        prompt_b = load_prompt("architect_b_prompt")

        status, conclusion, transcript = await run_deliberation(
            project_dir=project_dir,
            model=model,
            role_a="architect_a",
            role_b="architect_b",
            shared_context=shared_context,
            prompt_a=prompt_a,
            prompt_b=prompt_b,
            safety_cap=init_safety_cap,
            max_turns_per_round=300,
            max_turns_commit=2000,
            session_label="init-delib",
        )

        # Save transcript and feed
        t_path = save_transcript(project_dir, "INIT", transcript)
        append_to_feed(
            project_dir, "INIT", "Project decomposition",
            "architect_a", "architect_b",
            rounds=len(transcript),
            conclusion=conclusion,
            transcript_path=str(t_path.relative_to(project_dir)),
            status="converged" if status == "continue" else "error",
        )

        write_session_log(
            project_dir, "init-001", "deliberation:init", None, status,
            f"Init deliberation: {len(transcript)} rounds."
        )

        if status == "error":
            print("\n  Initialization deliberation failed. Check logs and retry.")
            return

        print("\n  Initialization deliberation complete.")
        print_progress(project_dir)
        _git_push(project_dir)
        await asyncio.sleep(auto_continue_delay)
    else:
        print("  Resuming existing project.")
        print_progress(project_dir)

    # ── Phase 2: Exploration Deliberation Loop ───────────────
    explorer_count = 0
    iteration = 0

    # Load explore prompts once
    prompt_author = load_prompt("spec_author_prompt")
    prompt_challenger = load_prompt("spec_challenger_prompt")

    while True:
        iteration += 1

        if max_iterations and iteration > max_iterations:
            print(f"\n  Reached max iterations ({max_iterations}).")
            break

        # Wait for off-peak pricing if needed
        await _await_offpeak()

        # Check for convergence
        summary = get_progress_summary(project_dir)
        if summary["total"] > 0 and summary["open"] == 0 and summary["in_progress"] == 0 \
                and summary["review"] == 0 and summary["revision_needed"] == 0:
            print("\n  ✓ CONVERGENCE: All objectives are verified, blocked, or dead-ended.")
            break

        # Refresh frontier
        frontier = refresh_frontier(project_dir)

        if not frontier:
            print("\n  Frontier is empty.")
            print("  Possible states: all nodes verified, blocked, or waiting on blocked deps.")
            break

        # Pick highest priority frontier objective
        target = frontier[0]
        node_id = target["id"]

        print(f"\n  Frontier has {len(frontier)} objectives. Picking: {node_id}")
        print(f"    Priority: {target['priority']} | "
              f"Blocks: {len(target['blocks'])} downstream nodes")

        # Mark in progress
        try:
            update_node_status(project_dir, node_id, STATUS_IN_PROGRESS)
        except KeyError:
            pass

        # ── Run Explore Deliberation ─────────────────────────
        explorer_count += 1
        meta = read_node_meta(project_dir, node_id)
        description = meta.get("description", node_id)

        print_session_header(f"EXPLORE DELIBERATION — {node_id}", iteration)
        print(f"  Spec Author + Spec Challenger will converse to produce the specification.")
        print(f"  Objective: {description[:100]}{'...' if len(description) > 100 else ''}")
        print()

        shared_context = build_explore_deliberation_context(project_dir, node_id)

        status, conclusion, transcript = await run_deliberation(
            project_dir=project_dir,
            model=model,
            role_a="spec_author",
            role_b="spec_challenger",
            shared_context=shared_context,
            prompt_a=prompt_author,
            prompt_b=prompt_challenger,
            safety_cap=explore_safety_cap,
            max_turns_per_round=200,
            max_turns_commit=1000,
            session_label=f"explore-{node_id}",
        )

        # Save transcript and feed
        t_path = save_transcript(project_dir, node_id, transcript)
        append_to_feed(
            project_dir, node_id, description,
            "spec_author", "spec_challenger",
            rounds=len(transcript),
            conclusion=conclusion,
            transcript_path=str(t_path.relative_to(project_dir)),
            status="converged" if status == "continue" else "error",
        )

        write_session_log(
            project_dir, f"exp-{iteration:03d}", "deliberation:explore",
            node_id, status,
            f"Explore deliberation for {node_id}: {len(transcript)} rounds."
        )

        if status == "error":
            print(f"  Deliberation failed for {node_id}. Returning to open.")
            try:
                update_node_status(project_dir, node_id, STATUS_OPEN)
            except KeyError:
                pass
            await asyncio.sleep(auto_continue_delay)
            continue

        # Check for dead end
        if _check_for_dead_end(conclusion):
            print(f"  Deliberation concluded {node_id} is a DEAD END.")
            mark_dead_end(project_dir, node_id)
            await asyncio.sleep(auto_continue_delay)
            continue

        # Mark as verified — the challenger's adversarial review is built into
        # the deliberation, so a converged conclusion is peer-reviewed by design.
        try:
            index = read_index(project_dir)
            node = index.get("nodes", {}).get(node_id, {})
            vs = node.get("visual_status")

            if vs and vs != "tuned":
                update_node_status(
                    project_dir, node_id, STATUS_APPROVED,
                    review_status="approved",
                    visual_status="needs_tuning",
                )
                print(f"  {node_id}: Approved (awaiting visual tuning)")
            else:
                update_node_status(
                    project_dir, node_id, STATUS_VERIFIED,
                    review_status="approved",
                )
                print(f"  {node_id}: Verified ✓")
        except KeyError:
            pass

        print_progress(project_dir)
        _git_push(project_dir)

        # ── Periodic Integrator (adaptive cadence) ────────────
        # Tighter early (every 5) to catch foundational drift,
        # relaxes to integrator_cadence once 25% of nodes are verified.
        total_nodes = summary["total"] if summary["total"] > 0 else 1
        verified_pct = summary["verified"] / total_nodes
        effective_cadence = integrator_cadence if verified_pct >= 0.25 else min(5, integrator_cadence)

        if explorer_count % effective_cadence == 0 and explorer_count > 0:
            print(f"\n  Integrator cadence reached ({explorer_count} explorations, "
                  f"cadence={effective_cadence}, {verified_pct:.0%} verified).")
            await _run_integrator(project_dir, model)

        await asyncio.sleep(auto_continue_delay)

    # ── Phase 3: Manifest + Synthesis ────────────────────────
    summary = get_progress_summary(project_dir)
    if summary["verified"] > 0:
        print("\n" + "=" * 70)
        print("  PHASE 3: MANIFEST + SYNTHESIS")
        print("=" * 70)

        # Step 1: Produce spec_manifest.md (the navigation document)
        # This uses index + meta.json descriptions only — fits in one context window.
        print(f"\n  Producing spec_manifest.md (navigation document for the DAG)...")
        man_status, man_response = await run_manifest_session(project_dir, model)
        write_session_log(
            project_dir, "manifest-001", "manifest_author",
            None, man_status,
            "Produced spec_manifest.md — the navigation document for the spec DAG."
        )
        if man_status == "error":
            print("  Manifest author failed. spec_manifest.md may need manual creation.")
        else:
            print("  spec_manifest.md created.")

        # Step 2: Map-Reduce Synthesis by category
        # Chunk pass: one synthesizer session per category
        # Rollup pass: one session that reads chunk outputs and produces final doc
        clusters = cluster_verified_by_category(project_dir)

        if clusters:
            print(f"\n  Synthesis plan (map-reduce):")
            for cat, ids in clusters.items():
                print(f"    {cat}: {len(ids)} nodes")

            # ── Map: per-category chunk passes ────────────────
            chunk_failures = []
            for cat, ids in clusters.items():
                print(f"\n  Synthesizing {cat} ({len(ids)} nodes)...")
                chunk_status, chunk_response = await run_synthesizer_chunk_session(
                    project_dir, cat, ids, model
                )
                write_session_log(
                    project_dir, f"syn-chunk-{cat}", "synthesizer",
                    None, chunk_status,
                    f"Chunk synthesis for {cat}: {len(ids)} nodes."
                )
                if chunk_status == "error":
                    print(f"  Chunk synthesis failed for {cat}.")
                    chunk_failures.append(cat)
                else:
                    print(f"  {cat}_spec.md created.")

            # ── Reduce: rollup pass ───────────────────────────
            if chunk_failures:
                print(f"\n  {len(chunk_failures)} chunk(s) failed: {', '.join(chunk_failures)}")
                print(f"  Rollup will proceed with available chunks.")

            synthesis_dir = project_dir / "synthesis"
            chunk_files = list(synthesis_dir.glob("*_spec.md"))
            if chunk_files:
                print(f"\n  Rolling up {len(chunk_files)} chunk specs into final_spec.md...")
                rollup_status, rollup_response = await run_synthesizer_rollup_session(
                    project_dir, model
                )
                write_session_log(
                    project_dir, "syn-rollup", "synthesizer",
                    None, rollup_status,
                    f"Rollup synthesis across {len(chunk_files)} category chunks."
                )
                if rollup_status == "error":
                    print("  Rollup failed. Per-category specs are still available in synthesis/.")
                else:
                    print("  final_spec.md created. Synthesis complete.")
            else:
                print("  No chunk specs produced. Skipping rollup.")

        _git_push(project_dir)

    # ── Final Summary ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  HARNESS COMPLETE")
    print("=" * 70)
    print(f"\n  Project: {project_dir}")
    print_progress(project_dir)
    print(f"\n  DAG output: {project_dir / 'index.json'}")
    print(f"  Navigation: {project_dir / 'spec_manifest.md'}")
    print(f"  Node specs: {project_dir / 'nodes/'}")
    print(f"  Conclusion feed: {project_dir / 'feed.md'}")
    print(f"  Session logs: {project_dir / 'sessions/'}")
    print()


# ──────────────────────────────────────────────────────────────
# Internal Helpers
# ──────────────────────────────────────────────────────────────

def _setup_project(project_dir: Path) -> None:
    """Set up the initial project structure."""
    (project_dir / "nodes").mkdir(parents=True, exist_ok=True)
    (project_dir / "dead_ends").mkdir(parents=True, exist_ok=True)
    (project_dir / "sessions").mkdir(parents=True, exist_ok=True)
    (project_dir / "synthesis").mkdir(parents=True, exist_ok=True)

    seed_source = PROMPTS_DIR / "seed.md"
    seed_dest = project_dir / "seed.md"
    if seed_source.exists() and not seed_dest.exists():
        shutil.copy(seed_source, seed_dest)
        print("  Copied seed.md into project directory.")
    elif not seed_dest.exists():
        print("  WARNING: No seed.md found.")

    import subprocess
    if not (project_dir / ".git").exists():
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial project setup"], cwd=project_dir, capture_output=True)
        print("  Initialized git repository.")


def _git_push(project_dir: Path) -> None:
    """Push to remote via Claude Code's SSH key: git push claude master."""
    import subprocess
    remote = os.environ.get("GIT_PUSH_REMOTE", "claude")
    branch = os.environ.get("GIT_PUSH_BRANCH", "master")

    result = subprocess.run(
        ["git", "push", remote, branch],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"  → Pushed to {remote}/{branch}")
    else:
        stderr = result.stderr.strip()
        if "No configured push destination" in stderr or "does not appear to be a git repository" in stderr:
            print(f"  → Push skipped (remote '{remote}' not configured — add it with git remote add {remote} <url>)")
        else:
            print(f"  → Push failed: {stderr[:200]}")


def _check_for_dead_end(text: str) -> bool:
    """Check if the conclusion indicates a dead end.

    Catches:
    - Explicit markers: DEAD_END: true, DEAD_END: yes
    - Verdict style: VERDICT: dead_end
    - Natural language: "this path is a dead end", "this objective is infeasible"
    - Conclusion style: "CONCLUSION: DEAD END" or "CONCLUSION: This is a dead end"
    """
    cleaned = re.sub(r'\*+', '', text)
    cleaned = re.sub(r'`+', '', cleaned)
    cleaned = re.sub(r'#+\s*', '', cleaned)

    # Explicit flag: DEAD_END: true/yes
    if re.search(
        r'(?:dead[_\s-]?end|infeasible|unachievable)\s*[:—\-]\s*(?:true|yes)',
        cleaned, re.IGNORECASE,
    ):
        return True

    # Verdict style: VERDICT: dead_end
    if re.search(
        r'verdict\s*[:—\-]\s*dead[_\s-]?end',
        cleaned, re.IGNORECASE,
    ):
        return True

    # Natural language in conclusion marker: "CONCLUSION: DEAD END ..." or
    # "CONCLUSION: This objective is a dead end / infeasible / unachievable"
    if re.search(
        r'conclusion\s*[:—\-]\s*(?:dead[_\s-]?end|.*?\b(?:dead\s+end|infeasible|unachievable)\b)',
        cleaned, re.IGNORECASE,
    ):
        return True

    # Standalone sentence patterns: "this is a dead end" / "this path is infeasible"
    if re.search(
        r'this\s+(?:path|objective|approach|direction)\s+is\s+(?:a\s+)?(?:dead[_\s-]?end|infeasible|unachievable|not\s+viable)',
        cleaned, re.IGNORECASE,
    ):
        return True

    return False


async def _run_integrator(project_dir: Path, model: str) -> None:
    """Run an integrator session with rotating coverage."""
    index = read_index(project_dir)
    verified = [nid for nid, n in index.get("nodes", {}).items() if n["status"] == STATUS_VERIFIED]

    if len(verified) < 3:
        print("  Skipping integrator — fewer than 3 verified nodes.")
        return

    sample_size = min(20, len(verified))
    coverage = read_integrator_coverage(project_dir)
    now = datetime.now(timezone.utc).isoformat()

    def sort_key(nid):
        last = coverage.get(nid)
        return "" if last is None else last

    sample = sorted(verified, key=sort_key)[:sample_size]
    never_sampled = sum(1 for nid in verified if nid not in coverage)
    print(f"  Running integrator with {len(sample)} sampled nodes...")
    print(f"    ({never_sampled} never sampled, {len(verified) - never_sampled} previously sampled)")

    status, response = await run_integrator_session(project_dir, sample, model)

    for nid in sample:
        coverage[nid] = now
    write_integrator_coverage(project_dir, coverage)

    write_session_log(
        project_dir, f"int-{len(verified):03d}", "integrator",
        None, status, f"Coherence check across {len(sample)} verified nodes."
    )
