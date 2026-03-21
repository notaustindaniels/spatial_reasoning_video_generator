#!/usr/bin/env python3
"""Security hook tests for the depthkit harness."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from security import bash_security_hook


def test_hook(command: str, should_block: bool) -> bool:
    input_data = {"tool_name": "Bash", "tool_input": {"command": command}}
    result = asyncio.run(bash_security_hook(input_data))
    was_blocked = result.get("decision") == "block"

    if was_blocked == should_block:
        status = "PASS"
    else:
        expected = "blocked" if should_block else "allowed"
        actual = "blocked" if was_blocked else "allowed"
        reason = result.get("reason", "")
        print(f"  FAIL: {command!r} — expected {expected}, got {actual}")
        if reason:
            print(f"        Reason: {reason}")
        return False

    print(f"  PASS: {command!r}")
    return True


def main():
    print("=" * 50)
    print("  SECURITY HOOK TESTS")
    print("=" * 50)

    passed = 0
    failed = 0

    # Commands that SHOULD be ALLOWED
    print("\nAllowed commands:\n")
    allowed = [
        "ls -la",
        "cat README.md",
        "npm install",
        "node server.js",
        "npx puppeteer-mcp-server",
        "git status",
        "git add . && git commit -m 'test'",
        "ffmpeg -version",
        "ffprobe input.mp4",
        "python3 -m rembg",
        "pip install three",
        "mkdir -p src/engine",
        "cp file1 file2",
        "pkill node",
        "pkill ffmpeg",
        "rm test.txt",
        "rm -rf node_modules",
        "echo hello",
        "curl https://example.com",
        "chmod +x init.sh && ./init.sh",
        "find . -name '*.ts'",
        "tree src/",
    ]
    for cmd in allowed:
        if test_hook(cmd, should_block=False):
            passed += 1
        else:
            failed += 1

    # Commands that SHOULD be BLOCKED
    print("\nBlocked commands:\n")
    blocked = [
        "shutdown now",
        "reboot",
        "dd if=/dev/zero of=/dev/sda",
        "pkill bash",
        "pkill chrome-not-in-list-actually-wait",  # not in allowed targets
        "rm -rf /",
    ]
    for cmd in blocked:
        if test_hook(cmd, should_block=True):
            passed += 1
        else:
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("  ALL TESTS PASSED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
