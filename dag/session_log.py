"""
Session Logging
===============

Each harness session writes a structured log documenting what was done,
what decisions were made, and what open questions remain. Session logs
are the audit trail — they allow future sessions and human reviewers
to understand why decisions were made without re-reading all prior work.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class SessionLog:
    session_id: str
    role: str  # initializer | explorer | reviewer | director | integrator | synthesizer
    objective_id: Optional[str] = None
    model: str = ""
    started_at: str = ""
    ended_at: str = ""
    status: str = "in_progress"  # in_progress | completed | error
    summary: str = ""
    decisions_made: list[str] = field(default_factory=list)
    artifacts_produced: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    dag_mutations: list[str] = field(default_factory=list)  # e.g., "OBJ-003: open -> in_progress"
    error: Optional[str] = None

    def start(self) -> None:
        self.started_at = datetime.now(timezone.utc).isoformat()

    def end(self, status: str = "completed") -> None:
        self.ended_at = datetime.now(timezone.utc).isoformat()
        self.status = status

    def add_decision(self, decision: str) -> None:
        self.decisions_made.append(decision)

    def add_artifact(self, path: str) -> None:
        self.artifacts_produced.append(path)

    def add_dag_mutation(self, mutation: str) -> None:
        self.dag_mutations.append(mutation)


def generate_session_id(role: str, session_number: int, objective_id: Optional[str] = None) -> str:
    """Generate a human-readable session ID."""
    parts = [f"session_{session_number:03d}", role]
    if objective_id:
        parts.append(objective_id)
    return "_".join(parts)


def write_session_log(log: SessionLog, sessions_dir: Path) -> Path:
    """Write a session log to disk as both JSON and Markdown."""
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON (machine-readable)
    json_path = sessions_dir / f"{log.session_id}.json"
    with open(json_path, "w") as f:
        json.dump(asdict(log), f, indent=2)

    # Write Markdown (human-readable)
    md_path = sessions_dir / f"{log.session_id}.md"
    with open(md_path, "w") as f:
        f.write(f"# Session Log: {log.session_id}\n\n")
        f.write(f"**Role:** {log.role}\n")
        if log.objective_id:
            f.write(f"**Objective:** {log.objective_id}\n")
        f.write(f"**Model:** {log.model}\n")
        f.write(f"**Started:** {log.started_at}\n")
        f.write(f"**Ended:** {log.ended_at}\n")
        f.write(f"**Status:** {log.status}\n\n")

        if log.summary:
            f.write(f"## Summary\n\n{log.summary}\n\n")

        if log.decisions_made:
            f.write("## Decisions Made\n\n")
            for d in log.decisions_made:
                f.write(f"- {d}\n")
            f.write("\n")

        if log.artifacts_produced:
            f.write("## Artifacts Produced\n\n")
            for a in log.artifacts_produced:
                f.write(f"- `{a}`\n")
            f.write("\n")

        if log.dag_mutations:
            f.write("## DAG Mutations\n\n")
            for m in log.dag_mutations:
                f.write(f"- {m}\n")
            f.write("\n")

        if log.open_questions:
            f.write("## Open Questions\n\n")
            for q in log.open_questions:
                f.write(f"- {q}\n")
            f.write("\n")

        if log.error:
            f.write(f"## Error\n\n```\n{log.error}\n```\n")

    print(f"Session log written: {md_path}")
    return md_path
