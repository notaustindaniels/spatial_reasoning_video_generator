"""
Agent Session Runner
====================

Runs a single agent session using the Claude Code SDK.
Handles message streaming, tool use display, and status reporting.
"""

import asyncio
from pathlib import Path

from claude_code_sdk import ClaudeSDKClient


# Delay between auto-continuing sessions
AUTO_CONTINUE_DELAY_SECONDS = 3


async def run_session(
    client: ClaudeSDKClient,
    message: str,
    role: str,
) -> tuple[str, str]:
    """
    Run a single agent session.

    Args:
        client: Configured Claude SDK client
        message: The prompt to send
        role: The agent role (for display purposes)

    Returns:
        (status, response_text) where status is "continue" or "error"
    """
    print(f"  [{role.upper()}] Sending prompt to Claude Code SDK...\n")

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
        print(f"\n  [{role.upper()}] Error during session: {e}")
        return "error", str(e)
