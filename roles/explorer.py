"""
Explorer Role
==============

The workhorse of the harness. Each explorer session:
1. Reads the seed + progress map
2. Picks the highest-priority ready objective
3. Works on it, producing a discrete artifact
4. Self-evaluates against acceptance criteria
5. Commits and marks the objective for review

Explorers are aggressive — they attempt solutions, not just analyses.
A documented failure is more valuable than cautious inaction.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from client import create_client
from dag.progress_map import ProgressMap, save_progress_map, load_progress_map
from dag.session_log import SessionLog, generate_session_id, write_session_log


def load_prompt(prompts_dir: Path) -> str:
    return (prompts_dir / "explorer_prompt.md").read_text()


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
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   Input: {input_str}", flush=True)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    if type(block).__name__ == "ToolResultBlock":
                        content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)
                        if "blocked" in str(content).lower():
                            print(f"   [BLOCKED] {content}", flush=True)
                        elif is_error:
                            print(f"   [Error] {str(content)[:500]}", flush=True)
                        else:
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text
    except Exception as e:
        print(f"Error during session: {e}")
        return "error", str(e)


async def run_explorer(
    project_dir: Path,
    model: str,
    prompts_dir: Path,
    objective_id: Optional[str] = None,
) -> Optional[str]:
    """
    Run an explorer session on the next available objective.

    Args:
        project_dir: Working directory
        model: Claude model to use
        prompts_dir: Path to prompts directory
        objective_id: Specific objective to work on (auto-selects if None)

    Returns:
        The objective ID that was worked on, or None if nothing was available
    """
    pm_path = project_dir / "progress_map.json"
    pm = load_progress_map(pm_path)
    if pm is None:
        print("ERROR: No progress map found. Run initializer first.")
        return None

    # Select objective
    if objective_id:
        obj = pm.get_objective(objective_id)
        if obj is None:
            print(f"ERROR: Objective {objective_id} not found.")
            return None
    else:
        obj = pm.get_next_objective()
        if obj is None:
            print("No ready objectives available.")
            blockers = pm.get_blocking_objectives()
            if blockers:
                print(f"Blocked objectives: {[b.id for b in blockers[:5]]}")
            return None

    objective_id = obj.id

    print("\n" + "=" * 70)
    print(f"  EXPLORER SESSION — {objective_id}")
    print(f"  {obj.description}")
    print(f"  Priority: {obj.priority} | Category: {obj.category}")
    print("=" * 70 + "\n")

    # Session setup
    pm.total_sessions += 1
    session_id = generate_session_id("explore", pm.total_sessions, objective_id)
    log = SessionLog(
        session_id=session_id,
        role="explorer",
        objective_id=objective_id,
        model=model,
    )
    log.start()

    # Mark in progress
    pm.mark_in_progress(objective_id, session_id)
    save_progress_map(pm, pm_path)
    log.add_dag_mutation(f"{objective_id}: open -> in_progress")

    # Create artifact directory
    artifact_dir = project_dir / "artifacts" / objective_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # Build context-aware prompt
    prompt_template = load_prompt(prompts_dir)
    objective_context = pm.get_context_for_objective(objective_id)

    # Read the seed for injection
    seed_text = ""
    seed_path = project_dir / "seed.md"
    if seed_path.exists():
        seed_text = seed_path.read_text()

    full_prompt = prompt_template.replace("{{OBJECTIVE_CONTEXT}}", objective_context)
    full_prompt = full_prompt.replace("{{OBJECTIVE_ID}}", objective_id)
    full_prompt = full_prompt.replace("{{ARTIFACT_DIR}}", str(artifact_dir.relative_to(project_dir)))

    # Extra system context: seed references
    extra_context = f"""
## Seed References for This Objective
The following seed sections are relevant: {', '.join(obj.seed_references)}

## Acceptance Criteria
{chr(10).join(f'- {ac}' for ac in obj.acceptance_criteria)}
"""

    # Create client with extra context
    client = create_client(project_dir, model, "explorer", extra_system_prompt=extra_context)

    # Run session
    async with client:
        status, response = await run_agent_session(client, full_prompt)

    # Reload progress map (agent may have modified it)
    pm = load_progress_map(pm_path) or pm

    # If the agent didn't update status, mark for review
    obj = pm.get_objective(objective_id)
    if obj and obj.status == "in_progress":
        pm.mark_for_review(objective_id, str(artifact_dir))
        log.add_dag_mutation(f"{objective_id}: in_progress -> review")
        save_progress_map(pm, pm_path)

    # Finalize session log
    log.summary = f"Explored objective {objective_id}: {obj.description if obj else 'unknown'}"
    log.add_artifact(str(artifact_dir))
    log.end("completed" if status != "error" else "error")
    if status == "error":
        log.error = response
    write_session_log(log, project_dir / "sessions")

    # Git commit
    subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Explore {objective_id}: {obj.description[:60] if obj else 'unknown'}"],
        cwd=project_dir, capture_output=True,
    )

    return objective_id
