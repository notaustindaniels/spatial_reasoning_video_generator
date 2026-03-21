"""
Context Assembly
================

Assembles the context payload for each agent role from the filesystem.
Follows the context assembly rules from the harness spec (Section 6.3):

- Always: seed.md + index.json
- Explorer: target node meta + dependency outputs
- Reviewer: target node meta + output + dependency outputs
- Integrator: rotating sample of verified node outputs
- Synthesizer: cluster of node outputs for current pass
"""

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
    # Fall back to prompts directory
    fallback = PROMPTS_DIR / "seed.md"
    if fallback.exists():
        return fallback.read_text()
    return ""


def load_index_summary(project_dir: Path) -> str:
    """Load index.json as a formatted string for context."""
    import json
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
# Role-Specific Context Builders
# ──────────────────────────────────────────────────────────────

def build_initializer_context(project_dir: Path) -> str:
    """Build the full prompt for the initializer session."""
    seed = load_seed(project_dir)
    prompt = load_prompt("initializer_prompt")

    return f"""# SEED DOCUMENT

{seed}

---

# YOUR INSTRUCTIONS

{prompt}
"""


def build_explorer_context(project_dir: Path, node_id: str) -> str:
    """
    Build context for an explorer session working on a specific node.
    Includes: seed, index, target meta, dependency outputs.
    """
    seed = load_seed(project_dir)
    index_str = load_index_summary(project_dir)
    prompt = load_prompt("explorer_prompt")

    # Target node metadata
    meta = read_node_meta(project_dir, node_id)
    import json
    meta_str = json.dumps(meta, indent=2) if meta else "No meta.json found for this node."

    # Dependency outputs
    dep_outputs = []
    for dep_id in meta.get("depends_on", []):
        output = read_node_output(project_dir, dep_id)
        if output:
            dep_outputs.append(f"### Dependency: {dep_id}\n\n{output}")

    deps_str = "\n\n---\n\n".join(dep_outputs) if dep_outputs else "No dependencies — this is a foundational objective."

    # Any prior reviews (if revision_needed)
    reviews = read_node_reviews(project_dir, node_id)
    reviews_str = ""
    if reviews:
        reviews_str = "\n\n## PRIOR REVIEWS (address these)\n\n" + "\n\n---\n\n".join(reviews)

    # Existing output (if revising)
    existing_output = read_node_output(project_dir, node_id)
    existing_str = ""
    if existing_output:
        existing_str = f"\n\n## YOUR PRIOR OUTPUT (revise as needed)\n\n{existing_output}"

    return f"""# SEED DOCUMENT

{seed}

---

# PROGRESS MAP INDEX

```json
{index_str}
```

---

# YOUR TARGET OBJECTIVE: {node_id}

## Metadata
```json
{meta_str}
```

## Dependency Outputs

{deps_str}
{reviews_str}
{existing_str}

---

# YOUR INSTRUCTIONS

{prompt}
"""


def build_reviewer_context(project_dir: Path, node_id: str) -> str:
    """
    Build context for a reviewer session evaluating a node.
    Includes: seed, target meta + output, dependency outputs.
    """
    seed = load_seed(project_dir)
    prompt = load_prompt("reviewer_prompt")

    meta = read_node_meta(project_dir, node_id)
    import json
    meta_str = json.dumps(meta, indent=2) if meta else "{}"

    output = read_node_output(project_dir, node_id)
    output_str = output if output else "No output.md found — the explorer may not have committed."

    # Dependency outputs for context
    dep_outputs = []
    for dep_id in meta.get("depends_on", []):
        dep_out = read_node_output(project_dir, dep_id)
        if dep_out:
            dep_outputs.append(f"### Dependency: {dep_id}\n\n{dep_out}")

    deps_str = "\n\n---\n\n".join(dep_outputs) if dep_outputs else "No dependencies."

    return f"""# SEED DOCUMENT

{seed}

---

# NODE UNDER REVIEW: {node_id}

## Metadata
```json
{meta_str}
```

## Output (the artifact to review)

{output_str}

## Dependency Outputs (for context)

{deps_str}

---

# YOUR INSTRUCTIONS

{prompt}
"""


def build_integrator_context(project_dir: Path, sample_node_ids: list[str]) -> str:
    """
    Build context for an integrator session.
    Includes: seed, index, sample of verified node outputs.
    """
    seed = load_seed(project_dir)
    index_str = load_index_summary(project_dir)
    prompt = load_prompt("integrator_prompt")
    summary = get_progress_summary(project_dir)

    sample_outputs = []
    for nid in sample_node_ids:
        meta = read_node_meta(project_dir, nid)
        output = read_node_output(project_dir, nid)
        import json
        sample_outputs.append(
            f"### Node: {nid}\n**Description:** {meta.get('description', 'N/A')}\n\n{output}"
        )

    samples_str = "\n\n---\n\n".join(sample_outputs) if sample_outputs else "No nodes to sample."

    import json
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


def build_synthesizer_context(project_dir: Path, cluster_node_ids: list[str]) -> str:
    """
    Build context for a synthesizer session.
    Includes: seed, cluster of verified node outputs.
    """
    seed = load_seed(project_dir)
    prompt = load_prompt("synthesizer_prompt")

    cluster_outputs = []
    for nid in cluster_node_ids:
        meta = read_node_meta(project_dir, nid)
        output = read_node_output(project_dir, nid)
        import json
        cluster_outputs.append(
            f"### Node: {nid}\n**Description:** {meta.get('description', 'N/A')}\n\n{output}"
        )

    cluster_str = "\n\n---\n\n".join(cluster_outputs) if cluster_outputs else "No nodes in cluster."

    return f"""# SEED DOCUMENT

{seed}

---

# VERIFIED NODE OUTPUTS TO SYNTHESIZE

{cluster_str}

---

# YOUR INSTRUCTIONS

{prompt}
"""
