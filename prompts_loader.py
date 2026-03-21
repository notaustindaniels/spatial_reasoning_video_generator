"""
Prompt Loading Utilities
========================

Loads prompt templates from the prompts/ directory and assembles
them with context from the DAG for each agent role.
"""

import shutil
from pathlib import Path

from dag.nodes import (
    assemble_explorer_context,
    assemble_reviewer_context,
    assemble_integrator_context,
)

PROMPTS_DIR = Path(__file__).parent / "prompts"
SEED_FILENAME = "seed.md"


def load_prompt(name: str) -> str:
    """Load a raw prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def get_initializer_prompt() -> str:
    """Load the initializer prompt (no context injection needed)."""
    return load_prompt("initializer_prompt")


def get_explorer_prompt(project_dir: Path, node_id: str) -> str:
    """Load the explorer prompt with injected node context."""
    template = load_prompt("explorer_prompt")
    context = assemble_explorer_context(project_dir, node_id)
    return template.replace("{node_context}", context)


def get_reviewer_prompt(project_dir: Path, node_id: str) -> str:
    """Load the reviewer prompt with injected review context."""
    template = load_prompt("reviewer_prompt")
    template = template.replace("{node_id}", node_id)
    context = assemble_reviewer_context(project_dir, node_id)
    return template.replace("{reviewer_context}", context)


def get_integrator_prompt(project_dir: Path, sample_ids: list[str]) -> str:
    """Load the integrator prompt with injected sample context."""
    template = load_prompt("integrator_prompt")
    context = assemble_integrator_context(project_dir, sample_ids)
    return template.replace("{integrator_context}", context)


def get_synthesizer_prompt(project_dir: Path, cluster_ids: list[str]) -> str:
    """Load the synthesizer prompt with injected cluster context."""
    template = load_prompt("synthesizer_prompt")
    context = assemble_integrator_context(project_dir, cluster_ids)  # Same assembly logic
    return template.replace("{synthesizer_context}", context)


def copy_seed_to_project(project_dir: Path, seed_path: Path) -> None:
    """Copy the seed document into the project directory."""
    dest = project_dir / SEED_FILENAME
    if not dest.exists():
        shutil.copy(seed_path, dest)
        print(f"  Copied seed document to {dest}")
