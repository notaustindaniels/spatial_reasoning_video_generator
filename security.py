"""
Security Hooks for Depthkit Harness
====================================

Pre-tool-use hooks that validate bash commands for security.
Uses an allowlist approach — only explicitly permitted commands can run.

Extended from the Anthropic autonomous coding demo to include
Three.js/Puppeteer/FFmpeg development commands.
"""

import os
import re
import shlex


ALLOWED_COMMANDS = {
    # File inspection
    "ls", "cat", "head", "tail", "wc", "grep", "find", "tree",
    # File operations
    "cp", "mkdir", "chmod", "mv", "rm",
    # Directory
    "pwd", "cd",
    # Node.js development
    "npm", "npx", "node", "pnpm",
    # Version control
    "git",
    # Process management
    "ps", "lsof", "sleep", "pkill",
    # Script execution
    "init.sh",
    # FFmpeg (needed for depthkit rendering pipeline)
    "ffmpeg", "ffprobe",
    # Python (needed for rembg and utility scripts)
    "python", "python3", "pip",
    # Testing
    "jest", "vitest",
}

COMMANDS_NEEDING_EXTRA_VALIDATION = {"pkill", "chmod", "rm"}


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
    """Only allow rm for specific safe patterns (no -rf /, no system dirs)."""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse rm command"

    # Block rm -rf with root or system paths
    full_cmd = " ".join(tokens)
    dangerous_patterns = ["/", "~", "$HOME", "/usr", "/etc", "/var", "/tmp"]
    for pattern in dangerous_patterns:
        if f"rm -rf {pattern}" in full_cmd or f"rm -r {pattern}" in full_cmd:
            return False, f"rm with dangerous path pattern: {pattern}"

    return True, ""


def validate_pkill_command(command_string: str) -> tuple[bool, str]:
    """Only allow killing dev-related processes."""
    allowed_processes = {"node", "npm", "npx", "vite", "next", "puppeteer", "chromium", "ffmpeg"}
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse pkill command"

    args = [t for t in tokens[1:] if not t.startswith("-")]
    if not args:
        return False, "pkill requires a process name"

    target = args[-1].split()[0] if " " in args[-1] else args[-1]
    if target in allowed_processes:
        return True, ""
    return False, f"pkill only allowed for dev processes: {allowed_processes}"


def validate_chmod_command(command_string: str) -> tuple[bool, str]:
    """Only allow making files executable with +x."""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse chmod command"

    if not tokens or tokens[0] != "chmod":
        return False, "Not a chmod command"

    mode = None
    for token in tokens[1:]:
        if token.startswith("-"):
            return False, "chmod flags are not allowed"
        elif mode is None:
            mode = token
        # else it's a file argument

    if mode is None:
        return False, "chmod requires a mode"

    if not re.match(r"^[ugoa]*\+x$", mode):
        return False, f"chmod only allowed with +x mode, got: {mode}"

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
            elif cmd == "chmod":
                allowed, reason = validate_chmod_command(command)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "rm":
                allowed, reason = validate_rm_command(command)
                if not allowed:
                    return {"decision": "block", "reason": reason}

    return {}
