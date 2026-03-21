"""
Agent Session Logic
===================

Core agent interaction functions for running sessions across all roles.
Each session: send prompt → stream response → collect output → return status.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from claude_code_sdk import ClaudeSDKClient

from client import create_client
from context import (
    build_initializer_context,
    build_explorer_context,
    build_reviewer_context,
    build_integrator_context,
    build_synthesizer_context,
)
from dag import (
    read_index,
    read_node_meta,
    update_node_status,
    refresh_frontier,
    print_progress,
    STATUS_OPEN,
    STATUS_IN_PROGRESS,
    STATUS_REVIEW,
    STATUS_REVISION_NEEDED,
    STATUS_VERIFIED,
)


# ──────────────────────────────────────────────────────────────
# Session Runner (shared across all roles)
# ──────────────────────────────────────────────────────────────

async def run_session(
    client: ClaudeSDKClient,
    message: str,
    session_label: str = "session",
) -> tuple[str, str]:
    """
    Run a single agent session using the Claude Agent SDK.

    Args:
        client: Configured Claude SDK client.
        message: The full prompt to send.
        session_label: Label for logging.

    Returns:
        (status, response_text) where status is "continue" or "error".
    """
    print(f"  [{session_label}] Sending prompt to Claude Agent SDK...\n")

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
                        print(f"\n  [Tool: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"    Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"    Input: {input_str}", flush=True)

            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__
                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)
                        if "blocked" in str(result_content).lower():
                            print(f"    [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            error_str = str(result_content)[:500]
                            print(f"    [Error] {error_str}", flush=True)
                        else:
                            print("    [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text

    except Exception as e:
        print(f"\n  [{session_label}] Error: {e}")
        return "error", str(e)


# ──────────────────────────────────────────────────────────────
# Role-Specific Session Launchers
# ──────────────────────────────────────────────────────────────

async def run_initializer_session(
    project_dir: Path,
    model: str,
    max_turns: int = 1000,
) -> tuple[str, str]:
    """Run the initializer session (Phase 1 — runs once)."""
    print_session_header("INITIALIZER", 1)

    context = build_initializer_context(project_dir)
    client = create_client(project_dir, model, role="initializer", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, "initializer")

    return status, response


async def run_explorer_session(
    project_dir: Path,
    node_id: str,
    model: str,
    session_number: int = 1,
    max_turns: int = 500,
) -> tuple[str, str]:
    """Run an explorer session targeting a specific node."""
    print_session_header(f"EXPLORER — {node_id}", session_number)

    # Mark node as in progress
    try:
        update_node_status(project_dir, node_id, STATUS_IN_PROGRESS)
    except KeyError:
        print(f"  Warning: Node {node_id} not found in index, proceeding anyway.")

    context = build_explorer_context(project_dir, node_id)
    client = create_client(project_dir, model, role="explorer", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, f"explorer:{node_id}")

    # After explorer commits, mark for review
    if status == "continue":
        try:
            update_node_status(project_dir, node_id, STATUS_REVIEW)
        except KeyError:
            pass

    return status, response


async def run_reviewer_session(
    project_dir: Path,
    node_id: str,
    model: str,
    review_number: int = 1,
    max_turns: int = 200,
) -> tuple[str, str]:
    """Run a reviewer session evaluating a specific node."""
    print_session_header(f"REVIEWER — {node_id} (review #{review_number})", 0)

    context = build_reviewer_context(project_dir, node_id)
    client = create_client(project_dir, model, role="reviewer", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, f"reviewer:{node_id}")

    return status, response


async def run_integrator_session(
    project_dir: Path,
    sample_node_ids: list[str],
    model: str,
    max_turns: int = 300,
) -> tuple[str, str]:
    """Run an integrator session for coherence checking."""
    print_session_header("INTEGRATOR", 0)

    context = build_integrator_context(project_dir, sample_node_ids)
    client = create_client(project_dir, model, role="integrator", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, "integrator")

    return status, response


async def run_synthesizer_session(
    project_dir: Path,
    cluster_node_ids: list[str],
    model: str,
    max_turns: int = 500,
) -> tuple[str, str]:
    """Run a synthesizer session to assemble deliverables."""
    print_session_header("SYNTHESIZER", 0)

    context = build_synthesizer_context(project_dir, cluster_node_ids)
    client = create_client(project_dir, model, role="synthesizer", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, "synthesizer")

    return status, response


# ──────────────────────────────────────────────────────────────
# Session Log Writing
# ──────────────────────────────────────────────────────────────

def write_session_log(
    project_dir: Path,
    session_id: str,
    role: str,
    target_node: Optional[str],
    status: str,
    notes: str = "",
) -> Path:
    """Write a session log entry to sessions/ directory."""
    sessions_dir = project_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_file = sessions_dir / f"{timestamp}_{role}_{session_id}.md"

    content = f"""# Session Log: {session_id}

**Role:** {role}
**Target Node:** {target_node or "N/A"}
**Status:** {status}
**Timestamp:** {datetime.now(timezone.utc).isoformat()}

## Notes

{notes}
"""
    log_file.write_text(content)
    return log_file


# ──────────────────────────────────────────────────────────────
# Display Helpers
# ──────────────────────────────────────────────────────────────

def print_session_header(label: str, session_num: int) -> None:
    """Print a formatted header for a session."""
    print("\n" + "=" * 70)
    if session_num > 0:
        print(f"  SESSION {session_num}: {label}")
    else:
        print(f"  {label}")
    print("=" * 70 + "\n")
