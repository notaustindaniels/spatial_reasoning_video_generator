"""
Integrator Role
================

Runs periodically to maintain coherence as the DAG grows. Reads the seed
and a broad sample of verified nodes to check for:

- Drift from seed vocabulary and constraints
- Inconsistencies between verified nodes
- Missed connections in the DAG
- Seed staleness (should the seed be updated?)

Produces a coherence report and proposes corrections.
"""

import asyncio
import subprocess
from pathlib import Path

from client import create_client
from dag.progress_map import ProgressMap, save_progress_map, load_progress_map
from dag.session_log import SessionLog, generate_session_id, write_session_log


def load_prompt(prompts_dir: Path) -> str:
    return (prompts_dir / "integrator_prompt.md").read_text()


async def run_agent_session(client, message: str) -> tuple[str, str]:
    """Run a single agent session, collect response."""
    print("Sending prompt to Claude Agent SDK...\n")
    try:
        await client.query(message)
        response_text = ""
        async for msg in client.receive_response():
            msg_type = type(msg).__name__
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__
                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]", flush=True)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    if type(block).__name__ == "ToolResultBlock":
                        is_error = getattr(block, "is_error", False)
                        if is_error:
                            print(f"   [Error]", flush=True)
                        else:
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text
    except Exception as e:
        print(f"Error during session: {e}")
        return "error", str(e)


async def run_integrator(
    project_dir: Path,
    model: str,
    prompts_dir: Path,
) -> str:
    """
    Run an integrator session for coherence checking.

    The integrator reads:
    - The seed document
    - The full progress map
    - A sample of verified artifacts (breadth over depth)
    - Recent session logs

    And produces a coherence report addressing drift, inconsistencies,
    missed connections, and seed staleness.

    Returns:
        Path to the coherence report
    """
    pm_path = project_dir / "progress_map.json"
    pm = load_progress_map(pm_path)
    if pm is None:
        print("ERROR: No progress map found.")
        return ""

    print("\n" + "=" * 70)
    print("  INTEGRATOR SESSION — Coherence Check")
    print(f"  Total objectives: {len(pm.objectives)}")
    print(f"  Verified: {pm.get_verified_count()}")
    print(f"  Dead ends: {pm.get_dead_end_count()}")
    print("=" * 70 + "\n")

    # Session setup
    pm.total_sessions += 1
    session_id = generate_session_id("integrate", pm.total_sessions)
    log = SessionLog(session_id=session_id, role="integrator", model=model)
    log.start()

    # Build context: summary of DAG state
    summary = pm.summary()
    verified_objectives = [o for o in pm.objectives if o.status == "verified"]
    blocked_objectives = [o for o in pm.objectives if o.status == "blocked"]

    dag_summary = f"""
## DAG State Summary

**Total objectives:** {summary['total_objectives']}
**By status:** {summary['by_status']}
**Dead ends:** {summary['dead_ends']}
**Sessions run:** {summary['total_sessions']}

### Verified Objectives (sample — check these for consistency)
"""
    for obj in verified_objectives[:20]:  # Sample up to 20
        dag_summary += f"- **{obj.id}** [{obj.category}]: {obj.description}\n"
        if obj.seed_references:
            dag_summary += f"  Seed refs: {', '.join(obj.seed_references)}\n"

    if blocked_objectives:
        dag_summary += "\n### Blocked Objectives (investigate why)\n"
        for obj in blocked_objectives[:10]:
            dag_summary += f"- **{obj.id}**: {obj.description}\n"
            dag_summary += f"  Blocked because: {obj.notes}\n"

    if pm.dead_ends:
        dag_summary += "\n### Dead Ends\n"
        for de in pm.dead_ends:
            dag_summary += f"- **{de.objective_id}**: {de.reason}\n"

    if pm.vocabulary_updates:
        dag_summary += "\n### Vocabulary Updates (proposed)\n"
        for vu in pm.vocabulary_updates:
            dag_summary += f"- **{vu.term}**: {vu.new_definition} (status: {vu.status})\n"

    # Load and inject prompt
    prompt_template = load_prompt(prompts_dir)
    full_prompt = prompt_template.replace("{{DAG_SUMMARY}}", dag_summary)

    # Create client
    client = create_client(project_dir, model, "integrator", extra_system_prompt=dag_summary)

    async with client:
        status, response = await run_agent_session(client, full_prompt)

    # Write coherence report
    report_path = project_dir / "sessions" / f"coherence_report_{session_id}.md"
    with open(report_path, "w") as f:
        f.write(f"# Coherence Report — {session_id}\n\n")
        f.write(response)

    # Finalize
    log.summary = "Coherence check completed"
    log.add_artifact(str(report_path.relative_to(project_dir)))
    log.end("completed" if status != "error" else "error")
    write_session_log(log, project_dir / "sessions")

    save_progress_map(pm, pm_path)

    subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Integrator coherence check: {session_id}"],
        cwd=project_dir, capture_output=True,
    )

    return str(report_path)
