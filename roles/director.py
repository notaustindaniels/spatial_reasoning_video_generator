"""
Director Agent Role (Gemini Multimodal)
========================================

The Director Agent addresses a fundamental limitation: text-based coding
agents cannot see rendered output. For depthkit — where visual quality IS
the product — the harness needs eyes during development.

**Model:** Google Gemini — selected for native multimodal video understanding.
Raw MP4 files are passed directly to Gemini's API. No frame extraction needed.

**HITL Circuit Breaker:** Every critique passes through human approval before
reaching the Code Agent. This is a HARD CONSTRAINT, not a guideline.
Advanced perception does not equal infallible taste.

**Scope:** Development-only. The Director is NEVER part of the production pipeline.
It exists to tune scene geometry parameters and camera path presets.
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from dag.progress_map import (
    ProgressMap, save_progress_map, load_progress_map,
    VisualStatus,
)
from dag.session_log import SessionLog, generate_session_id, write_session_log


DIRECTOR_SYSTEM_PROMPT = """You are the Director Agent in a multi-agent video engine development harness.

You review short test renders (10-30 seconds) of a 2.5D parallax video engine called "depthkit."
The engine maps AI-generated 2D images onto flat mesh planes in a Three.js 3D scene, then moves
a perspective camera through the scene to produce parallax depth effects.

Your role is EXCLUSIVELY visual feedback. You do NOT write code, modify manifests, or adjust
Three.js parameters directly. You describe what you see and which direction things should move.

## What You Evaluate
- Temporal flow: pacing, rhythm, whether the video feels rushed or lethargic
- 3D perspective projection: whether planes at different Z-depths produce convincing depth
- Camera easing and momentum: whether motions feel organic or robotic
- Edge reveals: whether camera motion exposes the edges of textured planes
- Depth separation: whether planes feel at distinct depths or collapsed together
- Fog and atmosphere: whether depth fog enhances or obscures the scene

## Feedback Rules (MANDATORY)
1. TIMESTAMP everything: "At 00:14-00:18" not "generally"
2. Use DIRECTIONAL DELTAS: "needs more ease-in" not "change Bezier to 0.8"
3. Use SPATIAL DESCRIPTIONS: "push further back" not "set z = -45"
4. Describe PHYSICS AND FEEL: "feels robotic — needs momentum"
5. Report EDGE REVEALS with spatial direction
6. PRESERVE what works — always note what should NOT change
7. Use COMPARATIVE LANGUAGE when possible

## Output Format
Your response MUST follow this structure:

# Visual Critique — [Geometry/Preset Name]
## Status: RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL

**Test Render:** [filename]
**Duration:** [X seconds]
**Geometry:** [name]
**Camera Path:** [name]

### Overall Impression
[1-2 sentences]

### Timestamped Observations
[Anchored to specific moments]

### Priority Tweaks (Ordered by Impact)
1. [Highest impact] — [directional fix]
2. [Second] — [directional fix]

### Things That Work Well (Preserve These)
- [What should NOT change]
"""


async def run_director(
    project_dir: Path,
    prompts_dir: Path,
    objective_id: str,
    render_path: Optional[str] = None,
) -> Optional[str]:
    """
    Run a Director Agent session using Gemini for visual critique.

    This function:
    1. Locates the test render for the objective
    2. Sends it to Gemini for visual analysis
    3. Writes the Visual Critique to critiques/
    4. Prompts the human for HITL approval
    5. Returns the approved/modified feedback

    Args:
        project_dir: Working directory
        prompts_dir: Path to prompts directory
        objective_id: The objective being visually tuned
        render_path: Explicit path to test render (auto-discovers if None)

    Returns:
        Path to the approved critique file, or None
    """
    pm_path = project_dir / "progress_map.json"
    pm = load_progress_map(pm_path)
    if pm is None:
        print("ERROR: No progress map found.")
        return None

    obj = pm.get_objective(objective_id)
    if obj is None:
        print(f"ERROR: Objective {objective_id} not found.")
        return None

    if not obj.requires_visual_tuning:
        print(f"WARNING: {objective_id} does not require visual tuning.")
        return None

    # Check for Gemini API key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY not set. Director Agent requires Gemini.")
        print("Set: export GEMINI_API_KEY='your-key'")
        return None

    # Find test render
    if render_path is None:
        renders_dir = project_dir / "renders"
        candidates = sorted(renders_dir.glob(f"{objective_id}*.mp4"))
        if not candidates:
            candidates = sorted(renders_dir.glob("test_render*.mp4"))
        if not candidates:
            print(f"ERROR: No test render found for {objective_id}")
            print(f"Expected in: {renders_dir}")
            return None
        render_path = str(candidates[-1])  # Latest render

    print("\n" + "=" * 70)
    print(f"  DIRECTOR AGENT SESSION — {objective_id}")
    print(f"  Reviewing: {render_path}")
    print("  Model: Google Gemini (multimodal)")
    print("=" * 70 + "\n")

    # Session setup
    pm.total_sessions += 1
    session_id = generate_session_id("direct", pm.total_sessions, objective_id)
    log = SessionLog(
        session_id=session_id,
        role="director",
        objective_id=objective_id,
        model="gemini",
    )
    log.start()

    # Mark visual status
    obj.visual_status = VisualStatus.IN_TUNING.value
    save_progress_map(pm, pm_path)

    # Send to Gemini
    critique_text = await _call_gemini(gemini_key, render_path, obj.description)

    if critique_text is None:
        log.error = "Gemini API call failed"
        log.end("error")
        write_session_log(log, project_dir / "sessions")
        return None

    # Write raw critique
    critiques_dir = project_dir / "critiques"
    critiques_dir.mkdir(exist_ok=True)
    raw_critique_path = critiques_dir / f"critique_{objective_id}_{session_id}_raw.md"
    with open(raw_critique_path, "w") as f:
        f.write(critique_text)

    print("\n" + "=" * 70)
    print("  VISUAL CRITIQUE (from Gemini)")
    print("=" * 70)
    print(critique_text)
    print("\n" + "=" * 70)

    # ═══════════════════════════════════════════════════
    #  HITL CIRCUIT BREAKER — HUMAN APPROVAL REQUIRED
    # ═══════════════════════════════════════════════════
    print("\n" + "!" * 70)
    print("  HITL CIRCUIT BREAKER — HUMAN APPROVAL REQUIRED")
    print("!" * 70)
    print("\nThe Director Agent's critique is above.")
    print("Options:")
    print("  (a) APPROVE as-is")
    print("  (b) MODIFY and approve (opens editor)")
    print("  (c) REJECT (discard critique)")
    print("  (d) OVERRIDE with your own notes")
    print()

    choice = input("Your choice [a/b/c/d]: ").strip().lower()

    approved_critique_path = critiques_dir / f"critique_{objective_id}_{session_id}_approved.md"

    if choice == "a":
        # Approve as-is
        with open(approved_critique_path, "w") as f:
            f.write("# HUMAN-APPROVED CRITIQUE\n\n")
            f.write(critique_text)
        print("✓ Critique approved as-is.")
        log.add_decision("HITL: Approved as-is")

    elif choice == "b":
        # Modify and approve
        print("\nPaste your modifications (end with a line containing only 'END'):")
        modifications = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            modifications.append(line)
        modified_text = "\n".join(modifications)

        with open(approved_critique_path, "w") as f:
            f.write("# HUMAN-MODIFIED CRITIQUE\n\n")
            f.write("## Original (Gemini)\n\n")
            f.write(critique_text)
            f.write("\n\n## Human Modifications\n\n")
            f.write(modified_text)
        print("✓ Modified critique approved.")
        log.add_decision(f"HITL: Modified and approved. Modifications: {modified_text[:200]}")

    elif choice == "c":
        # Reject
        print("✗ Critique rejected. No feedback will reach the Code Agent.")
        log.add_decision("HITL: Rejected critique entirely")
        log.end("completed")
        write_session_log(log, project_dir / "sessions")
        return None

    elif choice == "d":
        # Override with human notes
        print("\nPaste your override notes (end with a line containing only 'END'):")
        override_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            override_lines.append(line)
        override_text = "\n".join(override_lines)

        with open(approved_critique_path, "w") as f:
            f.write("# HUMAN OVERRIDE — Director critique replaced\n\n")
            f.write(override_text)
        print("✓ Human override recorded.")
        log.add_decision(f"HITL: Override with human notes: {override_text[:200]}")

    else:
        print("Invalid choice. Treating as reject.")
        log.add_decision("HITL: Invalid choice, treated as reject")
        log.end("completed")
        write_session_log(log, project_dir / "sessions")
        return None

    # Finalize
    log.add_artifact(str(raw_critique_path.relative_to(project_dir)))
    log.add_artifact(str(approved_critique_path.relative_to(project_dir)))
    log.summary = f"Director reviewed {objective_id}, HITL decision: {choice}"
    log.end("completed")
    write_session_log(log, project_dir / "sessions")

    # Git commit
    subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Director critique for {objective_id} (HITL: {choice})"],
        cwd=project_dir, capture_output=True,
    )

    return str(approved_critique_path)


async def _call_gemini(api_key: str, video_path: str, objective_description: str) -> Optional[str]:
    """
    Call Gemini API with a video file for visual critique.

    Uses the google-genai SDK to pass the raw MP4 directly to Gemini.
    No frame extraction needed — Gemini processes video natively.
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # Upload the video file
        print(f"Uploading {video_path} to Gemini...")
        video_file = client.files.upload(file=video_path)
        print(f"Upload complete: {video_file.name}")

        # Wait for file processing
        import time
        while video_file.state.name == "PROCESSING":
            print("  Waiting for video processing...")
            time.sleep(5)
            video_file = client.files.get(name=video_file.name)

        if video_file.state.name != "ACTIVE":
            print(f"ERROR: Video processing failed with state: {video_file.state.name}")
            return None

        # Generate critique
        print("Requesting visual critique from Gemini...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=video_file.uri,
                            mime_type=video_file.mime_type,
                        ),
                        types.Part.from_text(
                            f"Review this test render for the following objective:\n\n"
                            f"{objective_description}\n\n"
                            f"Follow the Visual Critique format exactly as specified "
                            f"in your system instructions."
                        ),
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=DIRECTOR_SYSTEM_PROMPT,
                temperature=0.4,
                max_output_tokens=4096,
            ),
        )

        return response.text

    except ImportError:
        print("ERROR: google-genai not installed. Run: pip install google-genai")
        return None
    except Exception as e:
        print(f"ERROR calling Gemini: {e}")
        return None
