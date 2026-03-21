"""
Claude SDK Client Configuration
=================================

Creates and configures Claude Agent SDK clients for each harness role.
Each role gets a tailored system prompt and tool set.
"""

import json
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from security import bash_security_hook


# Tool sets per role
CORE_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]

EXPLORER_TOOLS = [
    *CORE_TOOLS,
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_fill",
    "mcp__puppeteer__puppeteer_evaluate",
]

REVIEWER_TOOLS = ["Read", "Glob", "Grep"]  # Reviewers read, don't write

INTEGRATOR_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep"]

SYNTHESIZER_TOOLS = [*CORE_TOOLS]


ROLE_SYSTEM_PROMPTS = {
    "initializer": (
        "You are the Initializer Agent in a multi-agent development harness. "
        "You read a seed document and decompose it into a DAG of discrete, "
        "testable objectives. Your output is a progress_map.json — the single "
        "source of truth for all subsequent agents. Prioritize thorough "
        "decomposition over speed. Over-decompose rather than under-decompose."
    ),
    "explorer": (
        "You are an Explorer Agent in a multi-agent development harness. "
        "You pick a single objective from the progress map, work on it, "
        "and produce a discrete, reviewable artifact. You are aggressive — "
        "you attempt solutions, not just analyze problems. A documented "
        "failure is more valuable than cautious inaction."
    ),
    "reviewer": (
        "You are a Reviewer Agent in a multi-agent development harness. "
        "You have NO memory of producing the artifact under review. "
        "You evaluate structural soundness, constraint compliance, and "
        "gap analysis. Every weakness you identify MUST come with a "
        "proposed fix. Critique without replacement is incomplete."
    ),
    "integrator": (
        "You are an Integrator Agent in a multi-agent development harness. "
        "You check for drift from the seed's vocabulary and constraints, "
        "inconsistencies between verified objectives, and missed connections "
        "in the DAG. You produce a coherence report and propose corrections."
    ),
    "synthesizer": (
        "You are a Synthesizer Agent in a multi-agent development harness. "
        "You assemble verified results from the DAG into coherent final "
        "deliverables. You do not produce new results — you organize and "
        "integrate existing verified work."
    ),
}


def get_tools_for_role(role: str) -> list[str]:
    """Return the appropriate tool set for a given role."""
    return {
        "initializer": CORE_TOOLS,
        "explorer": EXPLORER_TOOLS,
        "reviewer": REVIEWER_TOOLS,
        "integrator": INTEGRATOR_TOOLS,
        "synthesizer": SYNTHESIZER_TOOLS,
    }.get(role, CORE_TOOLS)


def create_security_settings(project_dir: Path, role: str) -> Path:
    """Create role-appropriate security settings file."""
    if role == "reviewer":
        settings = {
            "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
            "permissions": {
                "defaultMode": "deny",
                "allow": [
                    "Read(./**)",
                    "Glob(./**)",
                    "Grep(./**)",
                ],
            },
        }
    else:
        settings = {
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
                ],
            },
        }

    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)

    return settings_file


def create_client(
    project_dir: Path,
    model: str,
    role: str,
    extra_system_prompt: str = "",
) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client configured for a specific harness role.

    Args:
        project_dir: Working directory for the session
        model: Claude model to use
        role: Agent role (initializer, explorer, reviewer, integrator, synthesizer)
        extra_system_prompt: Additional context injected after the role prompt

    Returns:
        Configured ClaudeSDKClient
    """
    project_dir.mkdir(parents=True, exist_ok=True)
    settings_file = create_security_settings(project_dir, role)

    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, "")
    if extra_system_prompt:
        system_prompt = f"{system_prompt}\n\n{extra_system_prompt}"

    tools = get_tools_for_role(role)
    mcp_servers = {}
    hooks = {}

    # Explorer sessions get Puppeteer for browser testing
    if role == "explorer":
        mcp_servers["puppeteer"] = {"command": "npx", "args": ["puppeteer-mcp-server"]}

    # Non-reviewer roles get bash security hooks
    if role != "reviewer":
        hooks["PreToolUse"] = [
            HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
        ]

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt=system_prompt,
            allowed_tools=tools,
            mcp_servers=mcp_servers if mcp_servers else None,
            hooks=hooks if hooks else None,
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),
        )
    )
