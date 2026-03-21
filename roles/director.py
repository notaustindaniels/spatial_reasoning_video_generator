"""
Director Agent — Gemini Visual Tuning
======================================

Uses Google Gemini's native multimodal video understanding to review
test renders and produce Visual Critiques. Operates under a strict
Human-in-the-Loop circuit breaker.

The Director Agent is a DEVELOPMENT tool. It never runs in production.
"""

import os
import json
from pathlib import Path
from typing import Optional


def run_director_review(
    test_render_path: Path,
    objective_description: str,
    geometry_name: str = "unknown",
    camera_path_name: str = "unknown",
    prior_critiques: list[str] = None,
    gemini_model: str = "gemini-2.5-pro",
) -> Optional[str]:
    """
    Send a test render to Gemini for visual critique.

    Args:
        test_render_path: Path to the test_render.mp4 file
        objective_description: What this node is trying to achieve
        geometry_name: The scene geometry being tuned
        camera_path_name: The camera path preset being tuned
        prior_critiques: List of prior Visual Critique texts for context
        gemini_model: Gemini model to use

    Returns:
        The Visual Critique text, or None if Gemini is not configured.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("  [DIRECTOR] GEMINI_API_KEY not set. Skipping director review.")
        print("  [DIRECTOR] Set GEMINI_API_KEY in .env to enable visual tuning.")
        return None

    if not test_render_path.exists():
        print(f"  [DIRECTOR] Test render not found: {test_render_path}")
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
    except ImportError:
        print("  [DIRECTOR] google-genai package not installed. Run: pip install google-genai")
        return None

    # Load the director prompt template
    prompt_path = Path(__file__).parent.parent / "prompts" / "director_prompt.md"
    director_prompt = prompt_path.read_text()

    # Fill in template variables
    director_prompt = director_prompt.replace("{objective_description}", objective_description)
    director_prompt = director_prompt.replace("{geometry_name}", geometry_name)
    director_prompt = director_prompt.replace("{camera_path_name}", camera_path_name)
    director_prompt = director_prompt.replace("{geometry/preset name}", f"{geometry_name} / {camera_path_name}")
    director_prompt = director_prompt.replace("{filename}", test_render_path.name)

    # Add prior critiques for context
    if prior_critiques:
        critique_context = "\n\n---\n\n## Prior Critiques (for context on what has been addressed)\n\n"
        for i, critique in enumerate(prior_critiques, 1):
            critique_context += f"### Round {i}\n{critique}\n\n"
        director_prompt += critique_context

    print(f"  [DIRECTOR] Uploading {test_render_path.name} to Gemini...")

    try:
        # Upload the video file
        video_file = client.files.upload(
            file=test_render_path,
            config=types.UploadFileConfig(
                mime_type="video/mp4",
            ),
        )

        print(f"  [DIRECTOR] File uploaded. Requesting visual critique...")

        # Send to Gemini with the video
        response = client.models.generate_content(
            model=gemini_model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=video_file.uri,
                            mime_type="video/mp4",
                        ),
                        types.Part.from_text(text=director_prompt),
                    ],
                ),
            ],
        )

        critique_text = response.text
        print(f"  [DIRECTOR] Visual critique received ({len(critique_text)} chars).")
        return critique_text

    except Exception as e:
        print(f"  [DIRECTOR] Gemini API error: {e}")
        return None


def hitl_gate(critique_text: str) -> tuple[str, str]:
    """
    Human-in-the-Loop circuit breaker.

    Presents the Director's critique to the human and waits for approval.

    Returns:
        (decision, approved_text) where decision is one of:
        - "approve" — use critique as-is
        - "modify" — human edited the critique (approved_text is the modified version)
        - "reject" — discard the critique entirely
        - "override" — human provides their own notes (approved_text is the override)
    """
    hitl_enabled = os.environ.get("HITL_ENABLED", "true").lower() == "true"

    if not hitl_enabled:
        print("  [HITL] Circuit breaker DISABLED (dry-run mode). Auto-approving.")
        return "approve", critique_text

    print("\n" + "=" * 70)
    print("  HITL CIRCUIT BREAKER — DIRECTOR AGENT VISUAL CRITIQUE")
    print("=" * 70)
    print()
    print(critique_text)
    print()
    print("=" * 70)
    print("  OPTIONS:")
    print("    [a] APPROVE as-is — pass this critique to the Code Agent")
    print("    [m] MODIFY — edit the critique before passing it along")
    print("    [r] REJECT — discard this critique entirely")
    print("    [o] OVERRIDE — provide your own notes instead")
    print("=" * 70)

    while True:
        choice = input("\n  Your decision (a/m/r/o): ").strip().lower()

        if choice == "a":
            print("  [HITL] Critique APPROVED.")
            return "approve", critique_text

        elif choice == "m":
            print("  [HITL] Enter your modified critique (end with a line containing only 'END'):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            modified = "\n".join(lines)
            print("  [HITL] Modified critique APPROVED.")
            return "modify", modified

        elif choice == "r":
            print("  [HITL] Critique REJECTED. Skipping this tuning round.")
            return "reject", ""

        elif choice == "o":
            print("  [HITL] Enter your override notes (end with a line containing only 'END'):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            override = "\n".join(lines)
            print("  [HITL] Override notes APPROVED.")
            return "override", override

        else:
            print("  Invalid choice. Enter a, m, r, or o.")


def save_critique(
    project_dir: Path,
    node_id: str,
    critique_text: str,
    round_number: int,
) -> Path:
    """Save a visual critique to the node's critiques directory."""
    critique_dir = project_dir / "nodes" / node_id / "critiques"
    critique_dir.mkdir(parents=True, exist_ok=True)

    critique_id = f"VC-{round_number:03d}"
    critique_path = critique_dir / f"{critique_id}.md"
    critique_path.write_text(critique_text)

    print(f"  [DIRECTOR] Critique saved to {critique_path}")
    return critique_path
