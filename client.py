"""
Claude SDK Client Configuration
================================

Creates and configures Claude Agent SDK clients for each harness role.
Uses defense-in-depth security: sandbox + filesystem restrictions + bash allowlist.
"""

import json
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from security import bash_security_hook


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
    role: str = "explorer",
    max_turns: int = 500,
    system_prompt_override: str = "",
) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client configured for the given role.

    Args:
        project_dir: The working directory for this session.
        model: Claude model identifier.
        role: Agent role (explorer, reviewer, integrator, synthesizer).
        max_turns: Maximum tool-use turns per session.
        system_prompt_override: Optional custom system prompt.

    Returns:
        A configured ClaudeSDKClient instance.
    """
    # Role-specific system prompts
    system_prompts = {
        "initializer": (
            "You are the Initializer Agent for the depthkit multi-agent harness. "
            "Your job is to read the seed document and decompose the project into "
            "a DAG of discrete, testable objectives. You create index.json, node "
            "directories, and the initial project scaffolding."
        ),
        "explorer": (
            "You are an Explorer Agent for the depthkit multi-agent harness. "
            "You are an expert full-stack developer specializing in Node.js, "
            "Three.js, Puppeteer, and FFmpeg pipelines. You pick up a single "
            "objective, implement it thoroughly, test it, and commit a discrete "
            "reviewable artifact to the node directory."
        ),
        "reviewer": (
            "You are a Reviewer Agent for the depthkit multi-agent harness. "
            "You have a fresh context with no memory of producing the artifact "
            "under review. Your job is adversarial-but-constructive evaluation: "
            "find gaps, unstated assumptions, structural weaknesses, constraint "
            "violations, and vocabulary drift. Every criticism must include a "
            "proposed fix."
        ),
        "integrator": (
            "You are an Integrator Agent for the depthkit multi-agent harness. "
            "You read a rotating sample of verified nodes and check for drift, "
            "inconsistency, missed connections, and seed staleness. You produce "
            "a coherence report and propose corrections."
        ),
        "synthesizer": (
            "You are a Synthesizer Agent for the depthkit multi-agent harness. "
            "You assemble verified node outputs into coherent deliverables. "
            "You do not produce new results — you organize and integrate "
            "existing ones into their final form."
        ),
    }

    system_prompt = system_prompt_override or system_prompts.get(role, system_prompts["explorer"])

    # Security settings
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
            ],
        },
    }

    project_dir.mkdir(parents=True, exist_ok=True)

    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt=system_prompt,
            allowed_tools=BUILTIN_TOOLS,
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
