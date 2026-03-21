"""
Reviewer Role
==============

Independent peer review with fresh context and decorrelated blind spots.
The reviewer has NO memory of producing the artifact under review.

Review evaluates:
- Structural soundness (does the artifact satisfy the objective?)
- Constraint compliance (does it respect the seed's constraints?)
- Vocabulary adherence (does it use the seed's terminology?)
- Gap analysis (what's missing? what assumptions are unstated?)
- Constructive critique (every weakness must include a proposed fix)

The reviewer can also challenge the progress map itself — proposing
restructuring, missing dependencies, or mis-specified objectives.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from client import create_client
from dag.progress_map import (
    ProgressMap, save_progress_map, load_progress_map,
    ReviewStatus, ObjectiveStatus,
)
from dag.session_log import SessionLog, generate_session_id, write_session_log


def load_prompt(prompts_dir: Path) -> str:
    return (prompts_dir / "reviewer_prompt.md").read_text()


async def run_agent_session(client, message: str) -> tuple[str, str]:
    """Run a single agent session, collect response."""
    print("Sending prompt to Claude Agent SDK...\n")
    try:
        await client.query(message)
        response_text = ""
        async for msg in client.receive_response():
            msg_type = type(msg).__name__
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__
                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]", flush=True)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    if type(block).__name__ == "ToolResultBlock":
                        content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)
                        if is_error:
                            print(f"   [Error] {str(content)[:500]}", flush=True)
                        else:
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text
    except Exception as e:
        print(f"Error during session: {e}")
        return "error", str(e)


async def run_reviewer(
    project_dir: Path,
    model: str,
    prompts_dir: Path,
    objective_id: Optional[str] = None,
) -> Optional[str]:
    """
    Run a review session on an objective waiting for review.

    The reviewer operates in a fresh context with NO memory of the
    exploration session that produced the artifact.

    Args:
        project_dir: Working directory
        model: Claude model to use
        prompts_dir: Path to prompts directory
        objective_id: Specific objective to review (auto-selects if None)

    Returns:
        The objective ID reviewed, or None if nothing needed review
    """
    pm_path = project_dir / "progress_map.json"
    pm = load_progress_map(pm_path)
    if pm is None:
        print("ERROR: No progress map found.")
        return None

    # Select objective needing review
    if objective_id:
        obj = pm.get_objective(objective_id)
        if obj is None or obj.status != ObjectiveStatus.REVIEW.value:
            print(f"ERROR: {objective_id} is not in review status.")
            return None
    else:
        review_queue = pm.get_objectives_needing_review()
        if not review_queue:
            print("No objectives awaiting review.")
            return None
        obj = review_queue[0]  # Take the first one

    objective_id = obj.id

    print("\n" + "=" * 70)
    print(f"  REVIEWER SESSION — {objective_id}")
    print(f"  {obj.description}")
    print(f"  Artifact: {obj.artifact_path}")
    print("=" * 70 + "\n")

    # Session setup
    pm.total_sessions += 1
    session_id = generate_session_id("review", pm.total_sessions, objective_id)
    log = SessionLog(
        session_id=session_id,
        role="reviewer",
        objective_id=objective_id,
        model=model,
    )
    log.start()

    # Build review prompt
    prompt_template = load_prompt(prompts_dir)
    objective_context = pm.get_context_for_objective(objective_id)

    full_prompt = prompt_template.replace("{{OBJECTIVE_CONTEXT}}", objective_context)
    full_prompt = full_prompt.replace("{{OBJECTIVE_ID}}", objective_id)
    full_prompt = full_prompt.replace("{{ARTIFACT_PATH}}", obj.artifact_path or "artifacts/" + objective_id)

    # Extra context: the acceptance criteria and seed references
    extra_context = f"""
## Review Target: {objective_id}
**Description:** {obj.description}
**Category:** {obj.category}
**Seed References:** {', '.join(obj.seed_references)}

## Acceptance Criteria (ALL must be satisfied for approval)
{chr(10).join(f'- {ac}' for ac in obj.acceptance_criteria)}

## Your Review Must Include
1. VERDICT: "approved" or "revision_needed"
2. If revision_needed: specific, actionable revision instructions
3. For EVERY weakness identified: a proposed fix or alternative
4. Assessment of vocabulary/constraint compliance
"""

    # Create client — fresh context, read-only tools
    client = create_client(project_dir, model, "reviewer", extra_system_prompt=extra_context)

    # Run review session
    async with client:
        status, response = await run_agent_session(client, full_prompt)

    # Parse verdict from response
    # The agent should write a structured review to reviews/ directory
    # We also look for verdict signals in the response text
    verdict = _parse_verdict(response)

    # Apply verdict
    if verdict == "approved":
        pm.mark_review_approved(objective_id)
        log.add_dag_mutation(f"{objective_id}: review -> {'verified' if not obj.requires_visual_tuning else 'needs_tuning'}")
        print(f"\n✓ APPROVED: {objective_id}")
    elif verdict == "revision_needed":
        revision_instructions = _extract_revision_instructions(response)
        pm.mark_revision_needed(objective_id, revision_instructions)
        log.add_dag_mutation(f"{objective_id}: review -> open (revision needed)")
        print(f"\n✗ REVISION NEEDED: {objective_id}")
    else:
        # Couldn't parse verdict — leave in review status for human decision
        print(f"\n? VERDICT UNCLEAR for {objective_id} — requires human decision")
        log.add_decision("Could not parse automated verdict — flagged for human review")

    save_progress_map(pm, pm_path)

    # Write review report
    review_dir = project_dir / "reviews"
    review_dir.mkdir(exist_ok=True)
    review_path = review_dir / f"review_{objective_id}_{session_id}.md"
    with open(review_path, "w") as f:
        f.write(f"# Review: {objective_id}\n\n")
        f.write(f"**Reviewer Session:** {session_id}\n")
        f.write(f"**Verdict:** {verdict}\n\n")
        f.write("---\n\n")
        f.write(response)
    log.add_artifact(str(review_path.relative_to(project_dir)))

    # Finalize
    log.summary = f"Reviewed {objective_id}: verdict={verdict}"
    log.end("completed" if status != "error" else "error")
    write_session_log(log, project_dir / "sessions")

    # Git commit
    subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Review {objective_id}: {verdict}"],
        cwd=project_dir, capture_output=True,
    )

    return objective_id


def _parse_verdict(response: str) -> str:
    """Parse the reviewer's verdict from their response text."""
    response_lower = response.lower()

    # Look for explicit verdict markers
    if "verdict: approved" in response_lower or "**verdict:** approved" in response_lower:
        return "approved"
    if "verdict: revision_needed" in response_lower or "**verdict:** revision_needed" in response_lower:
        return "revision_needed"
    if "verdict: revision needed" in response_lower or "**verdict:** revision needed" in response_lower:
        return "revision_needed"

    # Heuristic fallback
    approval_signals = ["approve", "looks good", "satisfies", "meets the criteria", "well done"]
    revision_signals = ["revision needed", "needs revision", "does not satisfy", "missing", "incorrect", "incomplete"]

    approval_score = sum(1 for s in approval_signals if s in response_lower)
    revision_score = sum(1 for s in revision_signals if s in response_lower)

    if approval_score > revision_score:
        return "approved"
    elif revision_score > 0:
        return "revision_needed"

    return "unknown"


def _extract_revision_instructions(response: str) -> str:
    """Extract revision instructions from the review response."""
    # Look for a "Revision Instructions" section
    markers = [
        "## Revision Instructions",
        "## Required Changes",
        "## Revisions Needed",
        "### Revision Instructions",
        "### Required Changes",
    ]

    for marker in markers:
        if marker in response:
            idx = response.index(marker)
            # Extract from marker to next ## heading or end
            rest = response[idx + len(marker):]
            next_heading = rest.find("\n## ")
            if next_heading > 0:
                return rest[:next_heading].strip()
            return rest.strip()

    # Fallback: return the full response as context
    return response[:2000]
