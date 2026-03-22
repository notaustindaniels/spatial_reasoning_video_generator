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
                        tool_line = f"\n[Tool: {block.name}]\n"
                        if hasattr(block, "input"):
                            input_repr = json.dumps(block.input, indent=2) if isinstance(block.input, (dict, list)) else str(block.input)
                            if len(input_repr) > 2000:
                                input_repr = input_repr[:2000] + "\n... [truncated]"
                            tool_line += f"  Input: {input_repr}\n"
                        response_text += tool_line
                        print(f"\n  [Tool: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            print(f"    Input: {input_str[:200]}{'...' if len(input_str) > 200 else ''}", flush=True)

            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    if type(block).__name__ == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)
                        result_str = str(result_content)
                        if "blocked" in result_str.lower():
                            response_text += f"[Tool BLOCKED] {result_str[:500]}\n"
                            print(f"    [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            response_text += f"[Tool Error] {result_str[:500]}\n"
                            print(f"    [Error] {result_str[:500]}", flush=True)
                        else:
                            if len(result_str) > 1000:
                                response_text += f"[Tool Result] {result_str[:1000]}... [truncated]\n"
                            else:
                                response_text += f"[Tool Result] {result_str}\n"
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
    safety_cap: int = 50,
    max_turns_per_round: int = 200,
    max_turns_commit: int = 500,
    session_label: str = "deliberation",
) -> tuple[str, str, list[dict]]:
    """
    Run a convergence-driven deliberation between two agents.

    Agent A (proposer) and Agent B (challenger) alternate turns. Only the
    challenger can signal convergence by writing CONCLUSION:. The proposer
    is explicitly forbidden from doing so.

    The safety_cap prevents infinite loops but is NOT a target — most
    deliberations should converge well before hitting it. If the cap is
    hit, a forced commit round is given to the challenger.

    Returns:
        (status, conclusion, transcript) where transcript is a list of
        {"round": int, "role": str, "content": str} dicts.
    """
    transcript = []
    conclusion = ""
    status = "continue"
    converged = False

    print(f"\n  Starting deliberation: {role_a} (proposer) vs {role_b} (challenger)")
    print(f"    Only {role_b} can signal convergence. Safety cap: {safety_cap}")

    round_num = 0

    while round_num < safety_cap:
        round_num += 1
        is_odd = (round_num % 2 == 1)

        current_role = role_a if is_odd else role_b
        current_prompt = prompt_a if is_odd else prompt_b
        is_proposer = is_odd  # role_a (odd rounds) = proposer, role_b (even) = challenger
        max_turns = max_turns_per_round

        # ── Build turn context ───────────────────────────────
        turn_context = _build_turn_context(
            shared_context=shared_context,
            role_prompt=current_prompt,
            transcript=transcript,
            round_num=round_num,
            is_proposer=is_proposer,
            is_commit=False,
        )

        # ── Run the turn ─────────────────────────────────────
        label = f"{session_label}:R{round_num}:{current_role}"
        print(f"\n  {'─' * 50}")
        print(f"  Round {round_num}: {current_role} ({'proposer' if is_proposer else 'CHALLENGER — can converge'})")
        print(f"  {'─' * 50}")

        client = create_client(project_dir, model, role=current_role, max_turns=max_turns)
        async with client:
            turn_status, response = await run_session(client, turn_context, label)

        if turn_status == "error":
            status = "error"
            transcript.append({"round": round_num, "role": current_role, "content": f"[ERROR: {response}]"})
            break

        transcript.append({"round": round_num, "role": current_role, "content": response})

        # ── Check for convergence ────────────────────────────
        # Only the challenger (even rounds) should write CONCLUSION:
        # If the proposer accidentally does it, log a warning but still break
        # (the prompt strongly forbids this, but we handle it gracefully)
        if _has_conclusion_marker(response):
            if is_proposer:
                print(f"\n  ⚠  WARNING: Proposer ({current_role}) wrote CONCLUSION: at round {round_num}.")
                print(f"     This should not happen — the proposer cannot declare convergence.")
                print(f"     Accepting it to avoid losing work, but the challenger did not verify.")
            else:
                print(f"\n  ✓ Convergence signaled at round {round_num} by {current_role} (challenger).")
            conclusion = _extract_conclusion(response)
            converged = True
            break

    # ── If safety cap hit without convergence, force commit to CHALLENGER ──
    if not converged and status != "error":
        round_num += 1
        # Always give forced commit to the challenger (role_b), regardless of whose turn it would be
        current_role = role_b
        current_prompt = prompt_b

        print(f"\n  {'─' * 50}")
        print(f"  Round {round_num}: {current_role} (SAFETY CAP — forced commit to challenger)")
        print(f"  {'─' * 50}")

        turn_context = _build_turn_context(
            shared_context=shared_context,
            role_prompt=current_prompt,
            transcript=transcript,
            round_num=round_num,
            is_proposer=False,  # Challenger
            is_commit=True,
        )

        client = create_client(project_dir, model, role=current_role, max_turns=max_turns_commit)
        async with client:
            turn_status, response = await run_session(client, turn_context, f"{session_label}:R{round_num}:COMMIT:{current_role}")

        if turn_status != "error":
            transcript.append({"round": round_num, "role": current_role, "content": response})
            conclusion = _extract_conclusion(response)
            if not conclusion:
                conclusion = response

    # ── Extract conclusion if not already captured ────────────
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
    is_proposer: bool,
    is_commit: bool = False,
) -> str:
    """Assemble the full prompt for one deliberation turn."""

    # Format prior turns
    history = "_This is the opening round. No prior discussion._"
    if transcript:
        parts = []
        for entry in transcript:
            parts.append(f"### Round {entry['round']} — {entry['role']}:\n\n{entry['content']}")
        history = "\n\n---\n\n".join(parts)

    commit_instructions = ""
    if is_commit:
        # Safety cap forced commit — always given to the challenger
        commit_instructions = """

---

## COMMIT ROUND — SAFETY CAP REACHED

The deliberation has reached its safety cap without an explicit convergence signal.
You MUST now produce the conclusion based on the current state of the discussion:

1. **Synthesize** the discussion into the best conclusion given what both sides have argued.
2. **Mark the conclusion** by writing `CONCLUSION:` on its own line, followed by the distilled result.
3. **Write to disk** — commit the agreed-upon output to the appropriate files (output.md for specs, index.json + node directories for initialization).
4. **Document any remaining disagreements** as explicit open questions — not as unresolved ambiguity.

The conclusion must stand on its own without requiring the transcript.
"""

    convergence_instructions = ""
    if not is_commit:
        if is_proposer:
            convergence_instructions = """

## CONVERGENCE RULES — PROPOSER

This deliberation runs until the **challenger** (the other agent) is satisfied — there is no predetermined round limit.

- **You CANNOT signal convergence.** Do NOT write `CONCLUSION:` under any circumstances. If you do, the deliberation will terminate before the challenger can verify your work.
- **You CANNOT write final files to disk** (output.md, index.json, node directories). The challenger is responsible for committing the agreed result.
- **Your job this round:** Propose, revise, or defend your work. If you believe you have addressed all the challenger's objections, present your revised proposal clearly and explicitly ask the challenger to verify and approve.
"""
        else:
            convergence_instructions = """

## CONVERGENCE RULES — CHALLENGER (YOU DECIDE)

This deliberation runs until **you** are satisfied — there is no predetermined round limit. You are the sole authority on convergence. The proposer cannot write `CONCLUSION:` or commit files.

- **If you have verified that all your critical and major objections have been satisfactorily addressed**, signal convergence by writing `CONCLUSION:` on its own line, followed by the agreed result. Then **write the conclusion to disk** (output.md for specs, index.json + node directories for initialization) and commit to git.
- **If issues remain**, state them clearly. The deliberation continues.
- **Actually verify fixes** — do not take the proposer's word that something is addressed. Check that the revised proposal structurally reflects the fix.
- Do NOT converge out of politeness or fatigue. You are the quality gate.
"""

    return f"""{shared_context}

---

# DELIBERATION — ROUND {round_num}
{convergence_instructions}
## Prior Discussion

{history}

---

## YOUR ROLE THIS ROUND

{role_prompt}
{commit_instructions}"""


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


async def run_synthesizer_chunk_session(
    project_dir: Path,
    category: str,
    node_ids: list[str],
    model: str,
    max_turns: int = 500,
) -> tuple[str, str]:
    """Run a synthesizer CHUNK session for one deliverable category."""
    from context import build_synthesizer_chunk_context

    print_session_header(f"SYNTHESIZER — CHUNK: {category} ({len(node_ids)} nodes)", 0)
    context = build_synthesizer_chunk_context(project_dir, category, node_ids)
    client = create_client(project_dir, model, role="synthesizer", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, f"synthesizer-chunk-{category}")

    return status, response


async def run_synthesizer_rollup_session(
    project_dir: Path,
    model: str,
    max_turns: int = 500,
) -> tuple[str, str]:
    """Run a synthesizer ROLLUP session to assemble chunk specs into final doc."""
    from context import build_synthesizer_rollup_context

    print_session_header("SYNTHESIZER — ROLLUP (final assembly)", 0)
    context = build_synthesizer_rollup_context(project_dir)
    client = create_client(project_dir, model, role="synthesizer", max_turns=max_turns)

    async with client:
        status, response = await run_session(client, context, "synthesizer-rollup")

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
