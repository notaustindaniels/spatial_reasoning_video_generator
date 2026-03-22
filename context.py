"""
Context Assembly
================

Assembles the shared context for deliberations and monologue sessions.
The shared context is what both agents see — the seed, index, and relevant
node data. Role-specific prompts are layered on per-turn by agent.py.
"""

import json
from pathlib import Path

from dag import (
    read_index,
    read_node_meta,
    read_node_output,
    read_node_reviews,
    get_progress_summary,
)


PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_seed(project_dir: Path) -> str:
    """Load the seed document from the project directory."""
    seed_path = project_dir / "seed.md"
    if seed_path.exists():
        return seed_path.read_text()
    fallback = PROMPTS_DIR / "seed.md"
    if fallback.exists():
        return fallback.read_text()
    return ""


def load_index_summary(project_dir: Path) -> str:
    """Load index.json as a formatted string."""
    index = read_index(project_dir)
    if not index:
        return "No index.json found — this is a fresh project."
    return json.dumps(index, indent=2)


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    if prompt_path.exists():
        return prompt_path.read_text()
    raise FileNotFoundError(f"Prompt template not found: {prompt_path}")


# ──────────────────────────────────────────────────────────────
# Deliberation Context Builders (shared context — both agents see this)
# ──────────────────────────────────────────────────────────────

def build_init_deliberation_context(project_dir: Path) -> str:
    """
    Build the shared context for the initialization deliberation.
    Both architects see: seed document + fresh project state.
    """
    seed = load_seed(project_dir)

    return f"""# SEED DOCUMENT

{seed}

---

# PROJECT STATE

This is a fresh project. No objectives exist yet. Your deliberation will
determine the decomposition — the number, scope, boundaries, dependencies,
and priorities of all objectives.

The output of this deliberation is:
1. `index.json` — the graph structure (IDs, edges, statuses)
2. `nodes/OBJ-NNN/meta.json` — per-objective metadata
3. `frontier.json` — initial ready objectives
4. `harness-progress.txt` — summary notes

The number of objectives is NOT predetermined. It emerges from your conversation.
"""


def build_explore_deliberation_context(project_dir: Path, node_id: str) -> str:
    """
    Build the shared context for an exploration deliberation.
    Both agents see: seed, index, target node, dependency outputs.
    """
    seed = load_seed(project_dir)
    index_str = load_index_summary(project_dir)

    # Target node metadata
    meta = read_node_meta(project_dir, node_id)
    meta_str = json.dumps(meta, indent=2) if meta else "No meta.json found."

    # Dependency outputs
    dep_outputs = []
    for dep_id in meta.get("depends_on", []):
        output = read_node_output(project_dir, dep_id)
        if output:
            dep_outputs.append(f"### Dependency: {dep_id}\n\n{output}")

    deps_str = "\n\n---\n\n".join(dep_outputs) if dep_outputs else "No dependencies — foundational objective."

    # Prior reviews (if revision_needed)
    reviews = read_node_reviews(project_dir, node_id)
    reviews_str = ""
    if reviews:
        reviews_str = "\n\n## PRIOR REVIEWS (address these)\n\n" + "\n\n---\n\n".join(reviews)

    # Existing output (if revising)
    existing_output = read_node_output(project_dir, node_id)
    existing_str = ""
    if existing_output:
        existing_str = f"\n\n## PRIOR SPEC OUTPUT (revise as needed)\n\n{existing_output}"

    return f"""# SEED DOCUMENT

{seed}

---

# PROGRESS MAP INDEX

```json
{index_str}
```

---

# TARGET OBJECTIVE: {node_id}

## Metadata
```json
{meta_str}
```

## Dependency Specs

{deps_str}
{reviews_str}
{existing_str}

---

# DELIBERATION OBJECTIVE

Your conversation should produce a complete specification for **{node_id}**.
The spec must define interface contracts, design decisions, acceptance criteria,
edge cases, test strategy, and integration points — NOT implementation code.

The final round must write the agreed specification to `nodes/{node_id}/output.md`
and update `nodes/{node_id}/meta.json`.
"""


# ──────────────────────────────────────────────────────────────
# Monologue Context Builders (integrator, synthesizer — unchanged)
# ──────────────────────────────────────────────────────────────

def build_integrator_context(project_dir: Path, sample_node_ids: list[str]) -> str:
    """Build context for an integrator session."""
    seed = load_seed(project_dir)
    index_str = load_index_summary(project_dir)
    prompt = load_prompt("integrator_prompt")
    summary = get_progress_summary(project_dir)

    sample_outputs = []
    for nid in sample_node_ids:
        meta = read_node_meta(project_dir, nid)
        output = read_node_output(project_dir, nid)
        sample_outputs.append(
            f"### Node: {nid}\n**Description:** {meta.get('description', 'N/A')}\n\n{output}"
        )

    samples_str = "\n\n---\n\n".join(sample_outputs) if sample_outputs else "No nodes to sample."
    summary_str = json.dumps(summary, indent=2)

    return f"""# SEED DOCUMENT

{seed}

---

# PROGRESS MAP INDEX

```json
{index_str}
```

# PROGRESS SUMMARY

```json
{summary_str}
```

---

# SAMPLED NODE OUTPUTS (for coherence review)

{samples_str}

---

# YOUR INSTRUCTIONS

{prompt}
"""


def build_synthesizer_chunk_context(
    project_dir: Path,
    category: str,
    node_ids: list[str],
) -> str:
    """
    Build context for a synthesizer CHUNK session — one deliverable category.
    Includes: seed, the specs for all nodes in this category.
    """
    seed = load_seed(project_dir)
    prompt = load_prompt("synthesizer_prompt")

    chunk_outputs = []
    for nid in node_ids:
        meta = read_node_meta(project_dir, nid)
        output = read_node_output(project_dir, nid)
        chunk_outputs.append(
            f"### Node: {nid}\n**Category:** {category}\n"
            f"**Description:** {meta.get('description', 'N/A')}\n\n{output}"
        )

    chunk_str = "\n\n---\n\n".join(chunk_outputs) if chunk_outputs else "No nodes in this category."

    return f"""# SEED DOCUMENT

{seed}

---

# MODE: CHUNK — Category: {category}

You are consolidating the **{category}** specs into a single document.
Write your output to `synthesis/{category}_spec.md`.

---

# VERIFIED NODE SPECS ({category})

{chunk_str}

---

# YOUR INSTRUCTIONS

{prompt}
"""


def build_synthesizer_rollup_context(project_dir: Path) -> str:
    """
    Build context for a synthesizer ROLLUP session — assembles chunk summaries.
    Reads the per-category consolidated specs from synthesis/ directory.
    """
    seed = load_seed(project_dir)
    prompt = load_prompt("synthesizer_prompt")

    synthesis_dir = project_dir / "synthesis"
    chunk_docs = []
    for spec_file in sorted(synthesis_dir.glob("*_spec.md")):
        content = spec_file.read_text()
        category = spec_file.stem.replace("_spec", "")
        chunk_docs.append(f"### Category: {category}\n\n{content}")

    chunks_str = "\n\n---\n\n".join(chunk_docs) if chunk_docs else "No chunk specs found."

    return f"""# SEED DOCUMENT

{seed}

---

# MODE: ROLLUP — Final Assembly

You are reading the per-category consolidated specs and producing the final
deliverable document. Write your output to `synthesis/final_spec.md`.

---

# PER-CATEGORY CONSOLIDATED SPECS

{chunks_str}

---

# YOUR INSTRUCTIONS

{prompt}
"""


def build_manifest_context(project_dir: Path) -> str:
    """
    Build context for the manifest author session.
    Includes: seed, full index, ALL node descriptions (meta.json only, not output.md).
    This is lightweight — descriptions and edges, not full spec content.
    """
    seed = load_seed(project_dir)
    index = read_index(project_dir)
    index_str = json.dumps(index, indent=2)
    prompt = load_prompt("manifest_prompt")
    summary = get_progress_summary(project_dir)
    summary_str = json.dumps(summary, indent=2)

    # Collect all meta.json descriptions — this is the map, not the territory
    node_descriptions = []
    for nid in sorted(index.get("nodes", {}).keys()):
        meta = read_node_meta(project_dir, nid)
        if meta:
            node_descriptions.append(
                f"- **{nid}**: {meta.get('description', 'N/A')} "
                f"[depends_on: {', '.join(meta.get('depends_on', [])) or 'none'}]"
            )

    nodes_str = "\n".join(node_descriptions) if node_descriptions else "No nodes found."

    # Collect dead ends
    dead_end_descriptions = []
    for de_id in index.get("dead_ends", []):
        meta = read_node_meta(project_dir, de_id)
        if meta:
            dead_end_descriptions.append(
                f"- **{de_id}**: {meta.get('description', 'N/A')} — {meta.get('notes', 'no notes')}"
            )

    dead_ends_str = "\n".join(dead_end_descriptions) if dead_end_descriptions else "No dead ends."

    return f"""# SEED DOCUMENT

{seed}

---

# FULL PROGRESS MAP INDEX

```json
{index_str}
```

# PROGRESS SUMMARY

```json
{summary_str}
```

---

# ALL OBJECTIVES (description + dependencies)

{nodes_str}

---

# DEAD ENDS

{dead_ends_str}

---

# YOUR INSTRUCTIONS

{prompt}
"""
