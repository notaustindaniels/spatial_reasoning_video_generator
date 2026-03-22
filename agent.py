"""
Agent Session Logic
===================

Core functions for running agent sessions:
- run_session: single-agent monologue (integrator, synthesizer)
- run_deliberation: two-agent conversation (init, explore)
- append_to_feed: real-time conclusion visibility
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from claude_code_sdk import ClaudeSDKClient
from claude_code_sdk._errors import MessageParseError
from claude_code_sdk.types import ResultMessage, SystemMessage

from client import create_client
from dag import (
    update_node_status,
    print_progress,
    STATUS_IN_PROGRESS,
    STATUS_REVIEW,
)


# ──────────────────────────────────────────────────────────────
# Safe SDK Message Receiver
# ──────────────────────────────────────────────────────────────

async def _safe_receive(client: ClaudeSDKClient):
    """Wrap client.receive_response() to handle SDK parse errors gracefully."""
    from claude_code_sdk._internal.message_parser import parse_message

    if not client._query:
        return

    async for data in client._query.receive_messages():
        try:
            msg = parse_message(data)
        except MessageParseError:
            msg_type = data.get("type", "unknown") if isinstance(data, dict) else "unknown"
            print(f"  [SDK warning: unhandled message type '{msg_type}', skipping]", flush=True)
            msg = SystemMessage(subtype=f"sdk_unknown_{msg_type}", data=data if isinstance(data, dict) else {})

        yield msg
        if isinstance(msg, ResultMessage):
            return


# ──────────────────────────────────────────────────────────────
# Single-Agent Session (integrator, synthesizer)
# ──────────────────────────────────────────────────────────────

async def run_session(
    client: ClaudeSDKClient,
    message: str,
    session_label: str = "session",
) -> tuple[str, str]:
    """Run a single agent session. Returns (status, response_text)."""
    print(f"  [{session_label}] Sending prompt...\n")

    try:
        await client.query(message)

        response_text = ""
        async for msg in _safe_receive(client):
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
                            print(f"    Input: {input_str[:200]}{'...' if len(input_str) > 200 else ''}", flush=True)

            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    if type(block).__name__ == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)
                        if "blocked" in str(result_content).lower():
                            print(f"    [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            print(f"    [Error] {str(result_content)[:500]}", flush=True)
                        else:
                            print("    [Done]", flush=True)

            elif msg_type == "ResultMessage":
                is_error = getattr(msg, "is_error", False)
                num_turns = getattr(msg, "num_turns", 0)
                duration = getattr(msg, "duration_ms", 0)
                cost = getattr(msg, "total_cost_usd", None)
                cost_str = f" | Cost: ${cost:.4f}" if cost else ""
                print(f"\n  [Result] turns={num_turns} duration={duration}ms error={is_error}{cost_str}", flush=True)

            elif msg_type == "SystemMessage":
                subtype = getattr(msg, "subtype", "unknown")
                print(f"  [System: {subtype}]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text

    except Exception as e:
        print(f"\n  [{session_label}] Error: {e}")
        return "error", str(e)


# ──────────────────────────────────────────────────────────────
# Two-Agent Deliberation
# ──────────────────────────────────────────────────────────────

async def run_deliberation(
    project_dir: Path,
    model: str,
    role_a: str,
    role_b: str,
    shared_context: str,
    prompt_a: str,
    prompt_b: str,
    min_rounds: int = 4,
    max_rounds: int = 20,
    max_turns_per_round: int = 200,
    max_turns_final: int = 500,
    session_label: str = "deliberation",
) -> tuple[str, str, list[dict]]:
    """
    Run a multi-turn deliberation between two agents until convergence.

    Agent A and Agent B alternate turns. Each turn is a fresh Claude Code
    SDK session with the full shared context + conversation history.
    The deliberation runs until an agent produces a CONCLUSION: marker
    (earliest at min_rounds), or until max_rounds is hit as a safety ceiling.

    Returns:
        (status, conclusion, transcript) where transcript is a list of
        {"round": int, "role": str, "content": str} dicts.
    """
    transcript = []
    conclusion = ""
    status = "continue"

    print(f"\n  Starting deliberation: {role_a} vs {role_b} "
          f"(converge after {min_rounds}+ rounds, ceiling {max_rounds})")

    for round_num in range(1, max_rounds + 1):
        is_ceiling = (round_num == max_rounds)
        eligible_to_converge = (round_num >= min_rounds)
        is_odd = (round_num % 2 == 1)

        current_role = role_a if is_odd else role_b
        current_prompt = prompt_a if is_odd else prompt_b
        max_turns = max_turns_final if (is_ceiling or eligible_to_converge) else max_turns_per_round

        # ── Build turn context ───────────────────────────────
        turn_context = _build_turn_context(
            shared_context=shared_context,
            role_prompt=current_prompt,
            transcript=transcript,
            round_num=round_num,
            max_rounds=max_rounds,
            is_final=is_ceiling,
            eligible_to_converge=eligible_to_converge,
        )

        # ── Run the turn ─────────────────────────────────────
        label = f"{session_label}:R{round_num}:{current_role}"
        print(f"\n  {'─' * 50}")
        round_label = f"  Round {round_num}/{max_rounds}: {current_role}"
        if is_ceiling:
            round_label += " (CEILING — must write conclusion)"
        elif eligible_to_converge:
            round_label += " (convergence eligible)"
        print(round_label)
        print(f"  {'─' * 50}")

        client = create_client(project_dir, model, role=current_role, max_turns=max_turns)
        async with client:
            turn_status, response = await run_session(client, turn_context, label)

        if turn_status == "error":
            status = "error"
            transcript.append({"round": round_num, "role": current_role, "content": f"[ERROR: {response}]"})
            break

        transcript.append({"round": round_num, "role": current_role, "content": response})

        # ── Check for convergence ─────────────────────────────
        if _has_conclusion_marker(response):
            print(f"\n  Converged at round {round_num}.")
            conclusion = _extract_conclusion(response)
            break

    # ── Extract conclusion ────────────────────────────────────
    if not conclusion and transcript:
        last_response = transcript[-1]["content"]
        conclusion = _extract_conclusion(last_response)
        if not conclusion:
            conclusion = last_response

    return status, conclusion, transcript


def _build_turn_context(
    shared_context: str,
    role_prompt: str,
    transcript: list[dict],
    round_num: int,
    max_rounds: int,
    is_final: bool,
    eligible_to_converge: bool = False,
) -> str:
    """Assemble the full prompt for one deliberation turn."""

    # Format prior turns
    history = "_This is the opening round. No prior discussion._"
    if transcript:
        parts = []
        for entry in transcript:
            parts.append(f"### Round {entry['round']} — {entry['role']}:\n\n{entry['content']}")
        history = "\n\n---\n\n".join(parts)

    convergence_instructions = ""
    if is_final:
        convergence_instructions = """

---

## CEILING REACHED — PRODUCE THE CONCLUSION NOW

This is the maximum round. You MUST conclude now:

1. **Synthesize the discussion** into a clear conclusion incorporating the strongest points from both sides.
2. **Mark the conclusion** by writing `CONCLUSION:` on its own line, followed by the distilled result.
3. **Write the conclusion to disk** — commit the agreed-upon output to the appropriate files (output.md for specs, index.json + node directories for initialization).
4. **Document any remaining disagreements** as open questions in the conclusion, not as unresolved ambiguity.

The conclusion must stand on its own without requiring the transcript.
"""
    elif eligible_to_converge:
        convergence_instructions = """

---

## CONVERGENCE CHECK

You have had sufficient discussion rounds. If you believe the discussion has reached a point where:
- The key design decisions are agreed upon
- Remaining disagreements are minor or documented as open questions
- The conclusion is ready to be written

Then **write your conclusion now**: write `CONCLUSION:` on its own line, followed by the distilled result, and **write it to disk** (output.md for specs, index.json + node directories for initialization).

If substantive disagreements remain or important aspects haven't been addressed yet, continue the discussion — there are more rounds available. Don't rush to conclude if the design isn't ready.
"""
    else:
        convergence_instructions = "\n_Focus on the discussion. Convergence is not expected yet — work through the design thoroughly._\n"

    return f"""{shared_context}

---

# DELIBERATION — ROUND {round_num} of {max_rounds}
{convergence_instructions}
## Prior Discussion

{history}

---

## YOUR ROLE THIS ROUND

{role_prompt}"""


def _has_conclusion_marker(text: str) -> bool:
    """Check if the response contains an explicit CONCLUSION: marker."""
    for line in text.split("\n"):
        stripped = line.strip().replace("*", "").replace("#", "").replace("`", "")
        if stripped.upper().startswith("CONCLUSION:"):
            return True
    return False


def _extract_conclusion(text: str) -> str:
    """Extract text after the CONCLUSION: marker."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip().replace("*", "").replace("#", "").replace("`", "")
        if stripped.upper().startswith("CONCLUSION:"):
            after_marker = stripped[len("CONCLUSION:"):].strip()
            remaining = "\n".join(lines[i + 1:]).strip()
            if after_marker:
                return after_marker + ("\n" + remaining if remaining else "")
            return remaining
    return ""


# ──────────────────────────────────────────────────────────────
# Live Feed
# ──────────────────────────────────────────────────────────────

def append_to_feed(
    project_dir: Path,
    node_id: str,
    description: str,
    role_a: str,
    role_b: str,
    rounds: int,
    conclusion: str,
    transcript_path: str = "",
    status: str = "converged",
) -> None:
    """
    Append a conclusion summary to feed.md for real-time visibility.
    Watch live with: tail -f generations/depthkit/feed.md
    """
    feed_path = project_dir / "feed.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Truncate for scannability
    conclusion_preview = conclusion[:2000]
    if len(conclusion) > 2000:
        conclusion_preview += "\n\n_[Truncated — see full spec in output.md]_"

    entry = f"""
---

## [{timestamp}] {node_id}: {description}

**Participants:** {role_a}, {role_b}
**Rounds:** {rounds}
**Status:** {status}

### Conclusion

{conclusion_preview}

**Full transcript:** {transcript_path}
**Full spec:** nodes/{node_id}/output.md

"""

    if not feed_path.exists():
        header = """# Depthkit Harness — Deliberation Feed

_Live feed of conclusions as they are produced._
```
tail -f generations/depthkit/feed.md
```

"""
        feed_path.write_text(header)

    with open(feed_path, "a") as f:
        f.write(entry)

    print(f"  → Conclusion appended to feed.md")


def save_transcript(
    project_dir: Path,
    node_id: str,
    transcript: list[dict],
) -> Path:
    """Save the full deliberation transcript to the node or sessions directory."""
    if node_id == "INIT":
        dest_dir = project_dir / "sessions"
        transcript_path = dest_dir / "init-deliberation-transcript.md"
    else:
        dest_dir = project_dir / "nodes" / node_id
        transcript_path = dest_dir / "transcript.md"

    dest_dir.mkdir(parents=True, exist_ok=True)

    parts = [f"# Deliberation Transcript: {node_id}\n"]
    for entry in transcript:
        parts.append(f"## Round {entry['round']} — {entry['role']}\n\n{entry['content']}\n")

    transcript_path.write_text("\n---\n\n".join(parts))
    return transcript_path


# ──────────────────────────────────────────────────────────────
# Monologue Session Launchers (integrator, synthesizer)
# ──────────────────────────────────────────────────────────────

async def run_integrator_session(
    project_dir: Path,
    sample_node_ids: list[str],
    model: str,
    max_turns: int = 300,
) -> tuple[str, str]:
    """Run an integrator session for coherence checking."""
    from context import build_integrator_context

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
    from context import build_synthesizer_context

    print_session_header("SYNTHESIZER", 0)
    context = build_synthesizer_context(project_dir, cluster_node_ids)
    client = create_client(project_dir, model, role="synthesizer", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, "synthesizer")

    return status, response


async def run_manifest_session(
    project_dir: Path,
    model: str,
    max_turns: int = 500,
) -> tuple[str, str]:
    """Run the manifest author session to produce spec_manifest.md."""
    from context import build_manifest_context

    print_session_header("MANIFEST AUTHOR", 0)
    context = build_manifest_context(project_dir)
    client = create_client(project_dir, model, role="manifest_author", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, "manifest")

    return status, response


# ──────────────────────────────────────────────────────────────
# Session Log + Display
# ──────────────────────────────────────────────────────────────

def write_session_log(
    project_dir: Path,
    session_id: str,
    role: str,
    target_node: Optional[str],
    status: str,
    notes: str = "",
) -> Path:
    sessions_dir = project_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_file = sessions_dir / f"{timestamp}_{role}_{session_id}.md"
    log_file.write_text(f"""# Session Log: {session_id}

**Role:** {role}
**Target Node:** {target_node or "N/A"}
**Status:** {status}
**Timestamp:** {datetime.now(timezone.utc).isoformat()}

## Notes

{notes}
""")
    return log_file


def print_session_header(label: str, session_num: int) -> None:
    print("\n" + "=" * 70)
    if session_num > 0:
        print(f"  SESSION {session_num}: {label}")
    else:
        print(f"  {label}")
    print("=" * 70 + "\n")
