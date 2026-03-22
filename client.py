"""
Claude SDK Client Configuration
================================

Creates and configures Claude Agent SDK clients for each harness role.
Includes deliberation role pairs (architect_a/b, spec_author/challenger)
and monologue roles (integrator, synthesizer).
"""

import json
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from security import bash_security_hook


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
    role: str = "spec_author",
    max_turns: int = 500,
    system_prompt_override: str = "",
) -> ClaudeSDKClient:
    """Create a Claude Agent SDK client configured for the given role."""

    system_prompts = {
        # ── Deliberation roles: Initialization ────────────────
        "architect_a": (
            "You are Architect A in a two-agent deliberation to decompose "
            "the depthkit project into a DAG of specification objectives. "
            "You are the proposer — you analyze the seed document and propose "
            "decomposition structure, objective boundaries, dependency edges, "
            "and priority assignments. You think in terms of what the project "
            "needs and how to break it into reviewable, specifiable units. "
            "You are thorough but open to challenge."
        ),
        "architect_b": (
            "You are Architect B in a two-agent deliberation to decompose "
            "the depthkit project into a DAG of specification objectives. "
            "You are the challenger — you stress-test Architect A's proposals. "
            "You look for: objectives that are too large to spec in one session, "
            "objectives that are too granular to justify their overhead, missing "
            "dependencies, circular dependencies, missing coverage of seed "
            "constraints and testable claims, incorrect priority assignments, "
            "and vocabulary drift. You propose specific improvements, not just "
            "objections. The decomposition must be rigorous enough that each "
            "objective can be specified by a downstream agent working from only "
            "the seed + its dependencies."
        ),

        # ── Deliberation roles: Exploration ───────────────────
        "spec_author": (
            "You are the Spec Author in a two-agent deliberation to produce "
            "the specification for a single depthkit objective. You are an "
            "expert systems architect specializing in Node.js, Three.js, "
            "Puppeteer, and FFmpeg pipelines. You propose the specification: "
            "interface contracts, design decisions and rationale, acceptance "
            "criteria, edge cases, error handling strategy, test strategy, "
            "and integration points. You do NOT write implementation code — "
            "you write the blueprint that a downstream code agent will follow. "
            "Be precise enough that an implementer can build from your spec "
            "without guessing your intent."
        ),
        "spec_challenger": (
            "You are the Spec Challenger in a two-agent deliberation to produce "
            "the specification for a single depthkit objective. You are a "
            "skeptical senior architect. Your job is to find every gap, "
            "ambiguity, unstated assumption, constraint violation, vocabulary "
            "drift, and downstream incompatibility in the proposed spec. "
            "Your key question: could a competent implementer build from this "
            "spec alone (plus the seed and dependency specs) without guessing? "
            "Every criticism must include a proposed fix. You also check: does "
            "the spec stay within its objective's boundaries? Does it use seed "
            "vocabulary correctly? Are acceptance criteria specific and testable? "
            "Do the interfaces integrate cleanly with dependency specs?"
        ),

        # ── Monologue roles ───────────────────────────────
        "manifest_author": (
            "You are the Manifest Author for the depthkit specification DAG. "
            "You produce spec_manifest.md — the navigation document that explains "
            "what the DAG contains, how to read it, which objectives comprise each "
            "deliverable, the critical path, dead ends, and unresolved items. "
            "You work from the index.json graph and meta.json descriptions — "
            "you are writing a map, not summarizing content."
        ),
        "integrator": (
            "You are an Integrator Agent for the depthkit multi-agent harness. "
            "You read a rotating sample of verified node specs and check for "
            "drift, inconsistency, missed connections, and seed staleness. "
            "You produce a coherence report and propose corrections. Your "
            "findings are actionable — if you find drift or inconsistency, "
            "state which specific nodes need re-review and why."
        ),
        "synthesizer": (
            "You are a Synthesizer Agent for the depthkit multi-agent harness. "
            "You assemble verified node specifications into consolidated "
            "specification documents. You do not produce new designs — you "
            "organize and integrate existing verified specs into their final "
            "form for consumption by a downstream execution harness."
        ),
    }

    system_prompt = system_prompt_override or system_prompts.get(role, system_prompts["spec_author"])

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
