"""
Initializer Role
=================

Runs once at the start. Reads the seed document and produces the initial
progress_map.json — the DAG of objectives that all subsequent sessions build upon.

This is the most consequential single session. A bad decomposition cascades
into wasted exploration. The initializer errs toward over-decomposition.
"""

import asyncio
from pathlib import Path
from typing import Optional

from client import create_client
from dag.progress_map import ProgressMap, save_progress_map
from dag.session_log import SessionLog, generate_session_id, write_session_log


def load_prompt(prompts_dir: Path) -> str:
    return (prompts_dir / "initializer_prompt.md").read_text()


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


async def run_initializer(
    project_dir: Path,
    model: str,
    seed_path: Path,
    prompts_dir: Path,
) -> ProgressMap:
    """
    Run the initializer session.

    1. Copies seed into project directory
    2. Sends the initializer prompt to Claude
    3. Claude reads the seed, produces progress_map.json
    4. Returns the loaded progress map

    Args:
        project_dir: Working directory for the project
        model: Claude model to use
        seed_path: Path to the seed document
        prompts_dir: Path to prompts directory

    Returns:
        The initial ProgressMap
    """
    print("\n" + "=" * 70)
    print("  INITIALIZER SESSION")
    print("  Decomposing seed into DAG of objectives...")
    print("=" * 70 + "\n")

    # Setup
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "sessions").mkdir(exist_ok=True)
    (project_dir / "artifacts").mkdir(exist_ok=True)
    (project_dir / "reviews").mkdir(exist_ok=True)
    (project_dir / "critiques").mkdir(exist_ok=True)
    (project_dir / "renders").mkdir(exist_ok=True)

    # Copy seed into project
    seed_dest = project_dir / "seed.md"
    if not seed_dest.exists():
        import shutil
        shutil.copy(seed_path, seed_dest)
        print(f"Copied seed to {seed_dest}")

    # Session log
    session_id = generate_session_id("init", 1)
    log = SessionLog(session_id=session_id, role="initializer", model=model)
    log.start()

    # Load prompt
    prompt = load_prompt(prompts_dir)

    # Create client and run
    client = create_client(project_dir, model, "initializer")

    async with client:
        status, response = await run_agent_session(client, prompt)

    # Load the progress map that the agent should have created
    pm_path = project_dir / "progress_map.json"
    pm = None
    if pm_path.exists():
        from dag.progress_map import load_progress_map
        pm = load_progress_map(pm_path)

    if pm is None:
        print("WARNING: Agent did not produce progress_map.json. Creating empty map.")
        pm = ProgressMap()
        save_progress_map(pm, pm_path)

    pm.total_sessions = 1

    # Finalize session log
    log.summary = f"Initialized progress map with {len(pm.objectives)} objectives"
    log.add_artifact("progress_map.json")
    log.add_artifact("seed.md")
    log.end("completed" if status != "error" else "error")
    if status == "error":
        log.error = response
    write_session_log(log, project_dir / "sessions")

    # Git init
    import subprocess
    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Initialize harness: {len(pm.objectives)} objectives"],
        cwd=project_dir, capture_output=True
    )

    # Print summary
    summary = pm.summary()
    print(f"\nInitialization complete:")
    print(f"  Total objectives: {summary['total_objectives']}")
    print(f"  By status: {summary['by_status']}")

    return pm
