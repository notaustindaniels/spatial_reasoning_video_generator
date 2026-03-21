"""
Synthesizer Role
=================

Runs at convergence or on request. Takes the DAG of verified results
and synthesizes them into a coherent final artifact — the deliverable
that the human operator actually wants.

For depthkit, the synthesizer produces:
1. A finalized progress_map.json as the build spec
2. A dependency-ordered implementation plan
3. A summary of all decisions, dead ends, and open questions
"""

import asyncio
import subprocess
from pathlib import Path

from client import create_client
from dag.progress_map import ProgressMap, save_progress_map, load_progress_map
from dag.session_log import SessionLog, generate_session_id, write_session_log


def load_prompt(prompts_dir: Path) -> str:
    return (prompts_dir / "synthesizer_prompt.md").read_text()


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


async def run_synthesizer(
    project_dir: Path,
    model: str,
    prompts_dir: Path,
) -> str:
    """
    Run the synthesizer to produce final deliverables.

    The synthesizer:
    1. Reads the full progress map and seed
    2. Groups verified objectives into implementation phases
    3. Produces a dependency-ordered build plan
    4. Summarizes dead ends and open questions
    5. Writes the final spec document

    Returns:
        Path to the synthesis output
    """
    pm_path = project_dir / "progress_map.json"
    pm = load_progress_map(pm_path)
    if pm is None:
        print("ERROR: No progress map found.")
        return ""

    summary = pm.summary()
    verified_count = pm.get_verified_count()
    total = len(pm.objectives)

    print("\n" + "=" * 70)
    print("  SYNTHESIZER SESSION — Final Assembly")
    print(f"  Verified: {verified_count}/{total} objectives")
    print(f"  Dead ends: {pm.get_dead_end_count()}")
    print("=" * 70 + "\n")

    # Session setup
    pm.total_sessions += 1
    session_id = generate_session_id("synthesize", pm.total_sessions)
    log = SessionLog(session_id=session_id, role="synthesizer", model=model)
    log.start()

    # Build comprehensive context
    verified = [o for o in pm.objectives if o.status == "verified"]
    dead_ends = [o for o in pm.objectives if o.status == "dead_end"]
    open_objs = [o for o in pm.objectives if o.status == "open"]
    blocked = [o for o in pm.objectives if o.status == "blocked"]

    context = f"""
## Synthesis Context

**Total objectives:** {total}
**Verified:** {verified_count}
**Dead ends:** {len(dead_ends)}
**Still open:** {len(open_objs)}
**Blocked:** {len(blocked)}

### Verified Objectives (by category)
"""
    # Group by category
    by_category = {}
    for obj in verified:
        cat = obj.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(obj)

    for cat, objs in sorted(by_category.items()):
        context += f"\n#### {cat}\n"
        for obj in objs:
            context += f"- **{obj.id}**: {obj.description}\n"
            if obj.acceptance_criteria:
                for ac in obj.acceptance_criteria:
                    context += f"  ✓ {ac}\n"

    if dead_ends:
        context += "\n### Dead Ends (documented failures)\n"
        for obj in dead_ends:
            context += f"- **{obj.id}**: {obj.description}\n"
            context += f"  Reason: {obj.dead_end_reason}\n"

    if blocked:
        context += "\n### Blocked (unresolved)\n"
        for obj in blocked:
            context += f"- **{obj.id}**: {obj.description}\n"
            context += f"  Blocked: {obj.notes}\n"

    if open_objs:
        context += "\n### Remaining Open Work\n"
        for obj in open_objs:
            context += f"- **{obj.id}** [{obj.priority}]: {obj.description}\n"

    # Load prompt
    prompt_template = load_prompt(prompts_dir)
    full_prompt = prompt_template.replace("{{SYNTHESIS_CONTEXT}}", context)

    # Create client
    client = create_client(project_dir, model, "synthesizer", extra_system_prompt=context)

    async with client:
        status, response = await run_agent_session(client, full_prompt)

    # Write synthesis output
    output_dir = project_dir / "synthesis"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"build_spec_{session_id}.md"
    with open(output_path, "w") as f:
        f.write(f"# Depthkit Build Specification\n\n")
        f.write(f"*Generated by synthesizer session {session_id}*\n\n")
        f.write(response)

    # Finalize
    log.summary = f"Synthesis complete: {verified_count}/{total} objectives verified"
    log.add_artifact(str(output_path.relative_to(project_dir)))
    log.end("completed" if status != "error" else "error")
    write_session_log(log, project_dir / "sessions")

    save_progress_map(pm, pm_path)

    subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Synthesis: build spec from {verified_count}/{total} verified objectives"],
        cwd=project_dir, capture_output=True,
    )

    print(f"\nSynthesis output: {output_path}")
    return str(output_path)
