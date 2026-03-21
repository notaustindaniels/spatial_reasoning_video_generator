"""
Security Hooks for Depthkit Harness
====================================

Pre-tool-use hooks that validate bash commands for security.
Uses an allowlist approach — only explicitly permitted commands can run.

Extends the base autonomous-coding security model with depthkit-specific
commands (ffmpeg, puppeteer/chromium, three.js dev server, python/rembg).
"""

import os
import re
import shlex


# Allowed commands for depthkit development
ALLOWED_COMMANDS = {
    # File inspection
    "ls", "cat", "head", "tail", "wc", "grep", "find", "tree",
    # File operations
    "cp", "mv", "mkdir", "chmod", "rm", "touch",
    # Directory
    "pwd", "cd",
    # Node.js development (Three.js, Puppeteer, bundler)
    "npm", "npx", "node",
    # Python (for rembg, embedding scripts, etc.)
    "python", "python3", "pip", "pip3",
    # Version control
    "git",
    # Process management
    "ps", "lsof", "sleep", "pkill", "kill",
    # Media pipeline (FFmpeg is a core depthkit dependency)
    "ffmpeg", "ffprobe",
    # Shell utilities used in init scripts
    "echo", "export", "which", "env", "source", "bash", "sh",
    "sed", "awk", "sort", "uniq", "tr", "cut", "tee",
    "curl", "wget",
    # Archive / compression
    "tar", "unzip",
    # Script execution
    "init.sh",
}

# Commands that need additional validation
COMMANDS_NEEDING_EXTRA_VALIDATION = {"pkill", "kill", "rm"}

# Allowed process names for pkill/kill
ALLOWED_KILL_TARGETS = {
    "node", "npm", "npx", "vite", "next", "esbuild",
    "puppeteer", "chromium", "chrome", "python", "python3",
    "ffmpeg",
}


def split_command_segments(command_string: str) -> list[str]:
    """Split a compound command into individual segments on &&, ||, ;"""
    segments = re.split(r"\s*(?:&&|\|\|)\s*", command_string)
    result = []
    for segment in segments:
        sub_segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', segment)
        for sub in sub_segments:
            sub = sub.strip()
            if sub:
                result.append(sub)
    return result


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
            if token in (
                "if", "then", "else", "elif", "fi", "for", "while",
                "until", "do", "done", "case", "esac", "in", "!",
                "{", "}", "[", "]", "[[", "]]",
            ):
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
    """Validate rm commands — block recursive force deletion of critical paths."""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse rm command"

    has_recursive = any(t in ("-r", "-rf", "-fr", "-R", "--recursive") for t in tokens)
    targets = [t for t in tokens[1:] if not t.startswith("-")]

    dangerous_paths = ["/", "/*", "~", "~/*", "..", "../"]
    for target in targets:
        if target in dangerous_paths:
            return False, f"rm targeting dangerous path: {target}"

    # Allow rm -rf for node_modules, build dirs, temp files
    return True, ""


def validate_kill_command(command_string: str) -> tuple[bool, str]:
    """Validate pkill/kill — only allow killing dev-related processes."""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse kill command"

    cmd = tokens[0] if tokens else ""

    if cmd == "kill":
        # kill with PID is ok (the agent needs to manage its own processes)
        return True, ""

    if cmd == "pkill":
        args = [t for t in tokens[1:] if not t.startswith("-")]
        if not args:
            return False, "pkill requires a process name"
        target = args[-1]
        if " " in target:
            target = target.split()[0]
        if target in ALLOWED_KILL_TARGETS:
            return True, ""
        return False, f"pkill only allowed for dev processes: {ALLOWED_KILL_TARGETS}"

    return True, ""


async def bash_security_hook(input_data, tool_use_id=None, context=None):
    """
    Pre-tool-use hook that validates bash commands against the allowlist.

    Returns empty dict to allow, or {"decision": "block", "reason": "..."} to block.
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

    segments = split_command_segments(command)

    for cmd in commands:
        if cmd not in ALLOWED_COMMANDS:
            return {
                "decision": "block",
                "reason": f"Command '{cmd}' is not in the allowed commands list",
            }

        if cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
            cmd_segment = _get_segment_for_command(cmd, segments) or command

            if cmd in ("pkill", "kill"):
                allowed, reason = validate_kill_command(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "rm":
                allowed, reason = validate_rm_command(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}

    return {}


def _get_segment_for_command(cmd: str, segments: list[str]) -> str:
    """Find the specific command segment containing the given command."""
    for segment in segments:
        segment_commands = extract_commands(segment)
        if cmd in segment_commands:
            return segment
    return ""
