"""
Claude SDK Client Configuration
================================

Creates role-specific Claude Agent SDK clients for each harness role.
Each role gets a tailored system prompt, tool set, and security configuration.
"""

import json
import os
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from security import bash_security_hook


# Puppeteer MCP tools for browser-based testing / preview
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_fill",
    "mcp__puppeteer__puppeteer_select",
    "mcp__puppeteer__puppeteer_hover",
    "mcp__puppeteer__puppeteer_evaluate",
]

# Built-in tools available to all roles
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]


def create_client(
    project_dir: Path,
    model: str,
    role: str,
    system_prompt: str,
    max_turns: int = 1000,
) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client configured for a specific harness role.

    Args:
        project_dir: Working directory for the agent session
        model: Claude model identifier
        role: Harness role name (initializer, explorer, reviewer, integrator, synthesizer)
        system_prompt: The full system prompt for this session
        max_turns: Maximum conversation turns

    Returns:
        Configured ClaudeSDKClient
    """
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": [
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                "Bash(*)",
                *PUPPETEER_TOOLS,
            ],
        },
    }

    project_dir.mkdir(parents=True, exist_ok=True)
    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    # Only explorers get browser tools (for preview mode testing)
    allowed_tools = list(BUILTIN_TOOLS)
    mcp_servers = {}

    if role in ("explorer", "initializer"):
        allowed_tools.extend(PUPPETEER_TOOLS)
        mcp_servers["puppeteer"] = {
            "command": "npx",
            "args": ["puppeteer-mcp-server"],
        }

    print(f"  [{role.upper()}] Client configured:")
    print(f"    Model: {model}")
    print(f"    CWD: {project_dir.resolve()}")
    print(f"    Sandbox: enabled")
    print(f"    MCP servers: {list(mcp_servers.keys()) or 'none'}")
    print()

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            mcp_servers=mcp_servers if mcp_servers else None,
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
                ],
            },
            max_turns=max_turns,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),
        )
    )
