"""
Security Hooks
==============

Pre-tool-use hooks that validate bash commands for security.
Uses an allowlist approach — only explicitly permitted commands can run.

Adapted from the Anthropic autonomous coding demo, extended for
the depthkit rendering pipeline (Node.js, FFmpeg, Puppeteer).
"""

import os
import re
import shlex


# Allowed commands for depthkit development
ALLOWED_COMMANDS = {
    # File inspection
    "ls", "cat", "head", "tail", "wc", "grep", "find", "stat",
    # File operations
    "cp", "mkdir", "chmod", "mv", "rm", "touch",
    # Directory
    "pwd", "cd",
    # Node.js / rendering pipeline
    "npm", "npx", "node",
    # Python (for rembg subprocess, embedding scripts)
    "python", "python3", "pip",
    # Version control
    "git",
    # Process management
    "ps", "lsof", "sleep", "pkill", "kill",
    # Media tools (core to depthkit)
    "ffmpeg", "ffprobe",
    # Script execution
    "init.sh", "bash", "sh",
    # Network (for fetching test assets)
    "curl", "wget",
    # Utilities
    "echo", "tee", "sort", "uniq", "jq", "xargs", "which",
    "sed", "awk", "diff", "tar", "unzip",
}

# Commands needing extra validation
COMMANDS_NEEDING_EXTRA_VALIDATION = {"pkill", "kill", "rm"}


def extract_commands(command_string: str) -> list[str]:
    """Extract command names from a shell command string."""
    commands = []
    segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', command_string)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            return []

        if not tokens:
            continue

        expect_command = True
        for token in tokens:
            if token in ("|", "||", "&&", "&"):
                expect_command = True
                continue
            if token in ("if", "then", "else", "elif", "fi", "for", "while",
                         "until", "do", "done", "case", "esac", "in", "!", "{", "}"):
                continue
            if token.startswith("-"):
                continue
            if "=" in token and not token.startswith("="):
                continue
            if expect_command:
                cmd = os.path.basename(token)
                commands.append(cmd)
                expect_command = False

    return commands


def validate_rm_command(command_string: str) -> tuple[bool, str]:
    """Validate rm commands — block recursive force on root-like paths."""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse rm command"

    has_recursive = any(t in ("-r", "-rf", "-fr", "--recursive") for t in tokens)
    args = [t for t in tokens[1:] if not t.startswith("-")]

    for arg in args:
        # Block rm -rf on root-like or parent paths
        if has_recursive and arg in ("/", "/*", "~", "~/*", "..", "../"):
            return False, f"rm -rf on '{arg}' is not allowed"

    return True, ""


def validate_pkill_command(command_string: str) -> tuple[bool, str]:
    """Validate pkill — only dev processes."""
    allowed_targets = {"node", "npm", "npx", "vite", "next", "python", "python3", "ffmpeg", "chromium"}
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse pkill command"

    args = [t for t in tokens[1:] if not t.startswith("-")]
    if not args:
        return False, "pkill requires a process name"

    target = args[-1].split()[0] if " " in args[-1] else args[-1]
    if target in allowed_targets:
        return True, ""
    return False, f"pkill only allowed for dev processes: {allowed_targets}"


async def bash_security_hook(input_data, tool_use_id=None, context=None):
    """
    Pre-tool-use hook that validates bash commands against the allowlist.
    Returns empty dict to allow, or {"decision": "block", ...} to block.
    """
    if input_data.get("tool_name") != "Bash":
        return {}

    command = input_data.get("tool_input", {}).get("command", "")
    if not command:
        return {}

    commands = extract_commands(command)
    if not commands:
        return {
            "decision": "block",
            "reason": f"Could not parse command for security validation: {command}",
        }

    for cmd in commands:
        if cmd not in ALLOWED_COMMANDS:
            return {
                "decision": "block",
                "reason": f"Command '{cmd}' is not in the allowed commands list",
            }

        if cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
            if cmd == "pkill":
                allowed, reason = validate_pkill_command(command)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "rm":
                allowed, reason = validate_rm_command(command)
                if not allowed:
                    return {"decision": "block", "reason": reason}

    return {}
