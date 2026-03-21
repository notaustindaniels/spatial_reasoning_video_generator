"""
Progress Map — DAG Data Structures
====================================

The progress map is the harness's distributed memory. It tracks objectives,
their statuses, dependencies, blocking relationships, and review/visual
tuning state. No session needs to hold the entire DAG — each reads the
seed plus the local neighborhood relevant to its current objective.

The progress map is the primary output of this harness. It becomes
the spec sheet for the downstream build harness.
"""

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class ObjectiveStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    VERIFIED = "verified"
    BLOCKED = "blocked"
    DEAD_END = "dead_end"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REVISION_NEEDED = "revision_needed"


class VisualStatus(str, Enum):
    NEEDS_TUNING = "needs_tuning"
    IN_TUNING = "in_tuning"
    TUNED = "tuned"


# Categories that map to seed document sections
class ObjectiveCategory(str, Enum):
    ENGINE_CORE = "engine_core"              # Orchestrator, Puppeteer bridge, FFmpeg encoder
    SCENE_GEOMETRY = "scene_geometry"        # Stage, tunnel, canyon, etc.
    CAMERA_PATH = "camera_path"             # Camera path presets
    MANIFEST_SCHEMA = "manifest_schema"     # Zod validation, schema design
    RENDERING_PIPELINE = "rendering_pipeline"  # Frame capture, virtualized clock
    SCENE_SEQUENCER = "scene_sequencer"     # Transitions, scene timing
    SPATIAL_AUTHORING = "spatial_authoring"  # Depth model, slot contracts
    ASSET_CACHING = "asset_caching"         # Supabase pgvector, threshold gate
    HTTP_INTERFACE = "http_interface"        # n8n-compatible endpoint
    SKILL_DOCUMENT = "skill_document"       # SKILL.md authoring
    INTEGRATION_TEST = "integration_test"   # End-to-end tests
    VISUAL_TUNING = "visual_tuning"         # Director Agent tuning targets
    TESTABLE_CLAIM = "testable_claim"       # TC-01 through TC-20 verification
    OPEN_QUESTION = "open_question"         # OQ-01 through OQ-10 exploration


@dataclass
class Objective:
    id: str
    description: str
    category: str
    status: str = ObjectiveStatus.OPEN.value
    depends_on: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    priority: str = Priority.MEDIUM.value
    assigned_session: Optional[str] = None
    review_status: Optional[str] = None
    visual_status: Optional[str] = None
    requires_visual_tuning: bool = False
    seed_references: list[str] = field(default_factory=list)  # e.g., ["C-01", "TC-02", "Section 4.2"]
    acceptance_criteria: list[str] = field(default_factory=list)
    artifact_path: Optional[str] = None
    notes: str = ""
    dead_end_reason: Optional[str] = None
    revision_instructions: Optional[str] = None
    session_history: list[str] = field(default_factory=list)  # Session IDs that touched this


@dataclass
class DeadEnd:
    objective_id: str
    reason: str
    session_id: str
    alternative_suggested: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class VocabularyUpdate:
    term: str
    old_definition: Optional[str]
    new_definition: str
    proposed_by: str  # session ID
    status: str = "proposed"  # proposed | approved | rejected


@dataclass
class ConstraintUpdate:
    constraint_id: str
    description: str
    proposed_by: str
    status: str = "proposed"


@dataclass
class ProgressMap:
    seed_version: str = "3.0"
    harness_version: str = "1.0"
    total_sessions: int = 0
    objectives: list[Objective] = field(default_factory=list)
    dead_ends: list[DeadEnd] = field(default_factory=list)
    vocabulary_updates: list[VocabularyUpdate] = field(default_factory=list)
    constraint_updates: list[ConstraintUpdate] = field(default_factory=list)

    # --- Query helpers ---

    def get_objective(self, obj_id: str) -> Optional[Objective]:
        for obj in self.objectives:
            if obj.id == obj_id:
                return obj
        return None

    def get_open_objectives(self) -> list[Objective]:
        return [o for o in self.objectives if o.status == ObjectiveStatus.OPEN.value]

    def get_ready_objectives(self) -> list[Objective]:
        """Return open objectives whose dependencies are all verified."""
        verified_ids = {o.id for o in self.objectives if o.status == ObjectiveStatus.VERIFIED.value}
        ready = []
        for obj in self.objectives:
            if obj.status != ObjectiveStatus.OPEN.value:
                continue
            if all(dep in verified_ids for dep in obj.depends_on):
                ready.append(obj)
        return ready

    def get_next_objective(self) -> Optional[Objective]:
        """Select the highest-priority ready objective that unblocks the most work."""
        ready = self.get_ready_objectives()
        if not ready:
            return None

        priority_order = {
            Priority.CRITICAL.value: 0,
            Priority.HIGH.value: 1,
            Priority.MEDIUM.value: 2,
            Priority.LOW.value: 3,
        }

        def sort_key(obj: Objective) -> tuple:
            pri = priority_order.get(obj.priority, 99)
            blocks_count = -len(obj.blocks)  # More blocks = higher priority
            return (pri, blocks_count)

        ready.sort(key=sort_key)
        return ready[0]

    def get_objectives_needing_review(self) -> list[Objective]:
        return [o for o in self.objectives if o.status == ObjectiveStatus.REVIEW.value]

    def get_objectives_needing_visual_tuning(self) -> list[Objective]:
        return [
            o for o in self.objectives
            if o.requires_visual_tuning
            and o.review_status == ReviewStatus.APPROVED.value
            and o.visual_status != VisualStatus.TUNED.value
        ]

    def get_blocking_objectives(self) -> list[Objective]:
        """Objectives that block the most downstream work."""
        blockers = [o for o in self.objectives if len(o.blocks) > 0 and o.status != ObjectiveStatus.VERIFIED.value]
        blockers.sort(key=lambda o: -len(o.blocks))
        return blockers

    def get_verified_count(self) -> int:
        return sum(1 for o in self.objectives if o.status == ObjectiveStatus.VERIFIED.value)

    def get_dead_end_count(self) -> int:
        return sum(1 for o in self.objectives if o.status == ObjectiveStatus.DEAD_END.value)

    def summary(self) -> dict:
        status_counts = {}
        for obj in self.objectives:
            status_counts[obj.status] = status_counts.get(obj.status, 0) + 1
        return {
            "total_objectives": len(self.objectives),
            "by_status": status_counts,
            "dead_ends": len(self.dead_ends),
            "vocabulary_updates": len(self.vocabulary_updates),
            "constraint_updates": len(self.constraint_updates),
            "total_sessions": self.total_sessions,
        }

    # --- Mutation helpers ---

    def mark_in_progress(self, obj_id: str, session_id: str) -> None:
        obj = self.get_objective(obj_id)
        if obj:
            obj.status = ObjectiveStatus.IN_PROGRESS.value
            obj.assigned_session = session_id
            obj.session_history.append(session_id)

    def mark_for_review(self, obj_id: str, artifact_path: Optional[str] = None) -> None:
        obj = self.get_objective(obj_id)
        if obj:
            obj.status = ObjectiveStatus.REVIEW.value
            obj.review_status = ReviewStatus.PENDING.value
            if artifact_path:
                obj.artifact_path = artifact_path

    def mark_review_approved(self, obj_id: str) -> None:
        obj = self.get_objective(obj_id)
        if obj:
            obj.review_status = ReviewStatus.APPROVED.value
            # If it doesn't need visual tuning, it's verified
            if not obj.requires_visual_tuning:
                obj.status = ObjectiveStatus.VERIFIED.value
            else:
                obj.visual_status = VisualStatus.NEEDS_TUNING.value

    def mark_revision_needed(self, obj_id: str, instructions: str) -> None:
        obj = self.get_objective(obj_id)
        if obj:
            obj.review_status = ReviewStatus.REVISION_NEEDED.value
            obj.revision_instructions = instructions
            obj.status = ObjectiveStatus.OPEN.value  # Back to open for rework

    def mark_visually_tuned(self, obj_id: str) -> None:
        obj = self.get_objective(obj_id)
        if obj:
            obj.visual_status = VisualStatus.TUNED.value
            obj.status = ObjectiveStatus.VERIFIED.value

    def mark_dead_end(self, obj_id: str, reason: str, session_id: str, alternative: Optional[str] = None) -> None:
        obj = self.get_objective(obj_id)
        if obj:
            obj.status = ObjectiveStatus.DEAD_END.value
            obj.dead_end_reason = reason
        self.dead_ends.append(DeadEnd(
            objective_id=obj_id,
            reason=reason,
            session_id=session_id,
            alternative_suggested=alternative,
        ))

    def mark_blocked(self, obj_id: str, reason: str) -> None:
        obj = self.get_objective(obj_id)
        if obj:
            obj.status = ObjectiveStatus.BLOCKED.value
            obj.notes = reason

    # --- DAG neighborhood extraction ---

    def get_neighborhood(self, obj_id: str, depth: int = 2) -> list[Objective]:
        """Get an objective and its dependency/blocker neighborhood up to `depth` hops."""
        visited = set()
        to_visit = {obj_id}

        for _ in range(depth):
            next_visit = set()
            for oid in to_visit:
                if oid in visited:
                    continue
                visited.add(oid)
                obj = self.get_objective(oid)
                if obj:
                    next_visit.update(obj.depends_on)
                    next_visit.update(obj.blocks)
            to_visit = next_visit

        visited.update(to_visit)
        return [o for o in self.objectives if o.id in visited]

    def get_context_for_objective(self, obj_id: str) -> str:
        """Produce a compact text summary of the neighborhood for injection into agent context."""
        neighborhood = self.get_neighborhood(obj_id)
        obj = self.get_objective(obj_id)
        if not obj:
            return f"Objective {obj_id} not found."

        lines = [
            f"## Current Objective: {obj.id}",
            f"**Description:** {obj.description}",
            f"**Category:** {obj.category}",
            f"**Priority:** {obj.priority}",
            f"**Status:** {obj.status}",
            f"**Seed References:** {', '.join(obj.seed_references)}",
            f"**Acceptance Criteria:**",
        ]
        for ac in obj.acceptance_criteria:
            lines.append(f"  - {ac}")

        if obj.depends_on:
            lines.append(f"\n### Dependencies (must be verified first):")
            for dep_id in obj.depends_on:
                dep = self.get_objective(dep_id)
                if dep:
                    lines.append(f"  - {dep.id} [{dep.status}]: {dep.description}")

        if obj.blocks:
            lines.append(f"\n### Blocks (waiting on this objective):")
            for blk_id in obj.blocks:
                blk = self.get_objective(blk_id)
                if blk:
                    lines.append(f"  - {blk.id}: {blk.description}")

        if obj.revision_instructions:
            lines.append(f"\n### Revision Instructions (from reviewer):")
            lines.append(obj.revision_instructions)

        if obj.notes:
            lines.append(f"\n### Notes:")
            lines.append(obj.notes)

        # Add nearby dead ends as warnings
        nearby_dead_ends = [
            de for de in self.dead_ends
            if de.objective_id in {o.id for o in neighborhood}
        ]
        if nearby_dead_ends:
            lines.append(f"\n### Nearby Dead Ends (avoid re-exploring):")
            for de in nearby_dead_ends:
                lines.append(f"  - {de.objective_id}: {de.reason}")
                if de.alternative_suggested:
                    lines.append(f"    Alternative suggested: {de.alternative_suggested}")

        return "\n".join(lines)


def _objective_to_dict(obj: Objective) -> dict:
    d = asdict(obj)
    # Remove None values for cleaner JSON
    return {k: v for k, v in d.items() if v is not None and v != [] and v != ""}


def _progress_map_to_dict(pm: ProgressMap) -> dict:
    return {
        "seed_version": pm.seed_version,
        "harness_version": pm.harness_version,
        "total_sessions": pm.total_sessions,
        "objectives": [_objective_to_dict(o) for o in pm.objectives],
        "dead_ends": [asdict(de) for de in pm.dead_ends],
        "vocabulary_updates": [asdict(vu) for vu in pm.vocabulary_updates],
        "constraint_updates": [asdict(cu) for cu in pm.constraint_updates],
    }


def _dict_to_objective(d: dict) -> Objective:
    return Objective(
        id=d["id"],
        description=d["description"],
        category=d.get("category", ""),
        status=d.get("status", ObjectiveStatus.OPEN.value),
        depends_on=d.get("depends_on", []),
        blocks=d.get("blocks", []),
        priority=d.get("priority", Priority.MEDIUM.value),
        assigned_session=d.get("assigned_session"),
        review_status=d.get("review_status"),
        visual_status=d.get("visual_status"),
        requires_visual_tuning=d.get("requires_visual_tuning", False),
        seed_references=d.get("seed_references", []),
        acceptance_criteria=d.get("acceptance_criteria", []),
        artifact_path=d.get("artifact_path"),
        notes=d.get("notes", ""),
        dead_end_reason=d.get("dead_end_reason"),
        revision_instructions=d.get("revision_instructions"),
        session_history=d.get("session_history", []),
    )


def load_progress_map(path: Path) -> Optional[ProgressMap]:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        pm = ProgressMap(
            seed_version=data.get("seed_version", "3.0"),
            harness_version=data.get("harness_version", "1.0"),
            total_sessions=data.get("total_sessions", 0),
        )
        pm.objectives = [_dict_to_objective(o) for o in data.get("objectives", [])]
        pm.dead_ends = [DeadEnd(**de) for de in data.get("dead_ends", [])]
        pm.vocabulary_updates = [VocabularyUpdate(**vu) for vu in data.get("vocabulary_updates", [])]
        pm.constraint_updates = [ConstraintUpdate(**cu) for cu in data.get("constraint_updates", [])]
        return pm
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error loading progress map: {e}")
        return None


def save_progress_map(pm: ProgressMap, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(_progress_map_to_dict(pm), f, indent=2)
    print(f"Progress map saved: {len(pm.objectives)} objectives")
