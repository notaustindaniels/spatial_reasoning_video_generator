# Consolidated Integration Specification — depthkit

**Category:** integration
**Synthesized from:** OBJ-050, OBJ-051, OBJ-052, OBJ-053, OBJ-054, OBJ-055, OBJ-056, OBJ-057, OBJ-058, OBJ-070, OBJ-071, OBJ-072, OBJ-073, OBJ-074, OBJ-075, OBJ-076, OBJ-077, OBJ-078

---

## Overview

The integration category covers everything that sits **outside the core rendering engine and spatial vocabulary** but is essential to making depthkit a usable, production-ready system. It spans six functional areas:

1. **SKILL.md Documentation System** (OBJ-070, OBJ-071, OBJ-072) — The authoritative reference enabling blind LLM authoring of manifests.
2. **Asset Pipeline** (OBJ-051, OBJ-052, OBJ-053, OBJ-054) — Image generation prompt engineering, background removal, and semantic caching infrastructure.
3. **Production Pipeline** (OBJ-055, OBJ-056, OBJ-057) — n8n HTTP interface, manifest generation via Claude API, and asset orchestration glue.
4. **Visual Tuning Workflow** (OBJ-058) — Director Agent process, HITL circuit breaker, test render utility, and convergence tracking.
5. **Deployment** (OBJ-050) — Docker containerization with software WebGL.
6. **Verification & Validation** (OBJ-073, OBJ-074, OBJ-075, OBJ-076, OBJ-077, OBJ-078) — Determinism verification, performance benchmarks, blind authoring tests, cache validation, and the end-to-end integration gate.

### Dependency Flow

```
                    ┌─────────────────────────────────────────────┐
                    │        ENGINE (spatial_spec, engine_spec)    │
                    │   OBJ-004 (Schema), OBJ-005 (Geometry),     │
                    │   OBJ-006 (Camera), OBJ-007 (Depth Model),  │
                    │   OBJ-035 (Orchestrator), OBJ-046 (CLI)     │
                    └──────────────────┬──────────────────────────┘
                                       │
          ┌────────────────────────────┼──────────────────────────────┐
          │                            │                              │
          ▼                            ▼                              ▼
   ┌──────────────┐         ┌──────────────────┐          ┌──────────────────┐
   │  SKILL.md    │         │  Asset Pipeline  │          │ Visual Tuning    │
   │  OBJ-070     │         │  OBJ-051 (Prompts)│          │ OBJ-058          │
   │  OBJ-071     │◄────────│  OBJ-053 (Schema)│          │ (Director Agent) │
   │  OBJ-072     │         │  OBJ-054 (Cache) │          └────────┬─────────┘
   └──────┬───────┘         │  OBJ-052 (Rembg) │                   │
          │                 └────────┬─────────┘                   │
          │                          │                              │
          ▼                          ▼                              │
   ┌──────────────┐         ┌──────────────────┐                   │
   │  Production  │         │  Deployment      │                   │
   │  Pipeline    │◄────────│  OBJ-050 (Docker)│                   │
   │  OBJ-055     │         └──────────────────┘                   │
   │  OBJ-056     │                                                │
   │  OBJ-057     │                                                │
   └──────┬───────┘                                                │
          │                                                        │
          ▼                                                        ▼
   ┌────────────────────────────────────────────────────────────────┐
   │              Verification & Validation                         │
   │  OBJ-073 (Determinism), OBJ-074 (Benchmark),                 │
   │  OBJ-075 (Blind Authoring), OBJ-076 (Cache Validation),      │
   │  OBJ-077 (E2E Test Plan), OBJ-078 (Execution Gate)           │
   └────────────────────────────────────────────────────────────────┘
```

### Integration Boundaries With Other Categories

| This Category | Depends On (from engine/spatial) | Consumed By |
|---|---|---|
| OBJ-051 (Prompts) | OBJ-007 (Depth Model), OBJ-018-021 (Geometries) — referenced, not imported | OBJ-054 (Cache), OBJ-072 (SKILL.md prompts), OBJ-056 (Manifest gen) |
| OBJ-058 (Director) | OBJ-035 (Orchestrator) | OBJ-059–066 (Geometry tuning, spatial category) |
| OBJ-070/071 (SKILL.md) | OBJ-004 (Schema), OBJ-046 (CLI), OBJ-018 (Stage), OBJ-027 (Push/Pull cameras) | OBJ-056 (Manifest gen), SC-02/SC-04 (Success criteria) |
| OBJ-073 (Determinism) | OBJ-035 (Orchestrator), OBJ-013 (FFmpeg) | OBJ-077/078 (E2E tests) |
| OBJ-074 (Benchmark) | OBJ-035 (Orchestrator), OBJ-049 (Rendering Config), OBJ-018 (Stage) | OBJ-078 (E2E gate) |

---

## Part 1: SKILL.md Documentation System

### 1.1 SKILL.md Structure and Core Content (OBJ-070)

**Status:** Verified spec
**Depends on:** OBJ-004 (Manifest Schema), OBJ-046 (CLI), OBJ-018 (Stage Geometry), OBJ-027 (Push/Pull Cameras)

OBJ-070 defines the **document architecture** and **core content** of the SKILL.md — the single authoritative reference enabling an LLM agent (with no visual perception) to produce valid depthkit manifests. Per SC-04, an LLM reading only SKILL.md (and its sub-files) must be able to produce a valid manifest without access to engine source code.

#### Document Architecture

```
depthkit/
  SKILL.md                              # Primary entry point (repo root)
  docs/
    skill/
      geometry-reference.md             # All scene geometries: slots, descriptions, usage guidance
      camera-reference.md               # All camera path presets: motion, compatible geometries
      prompt-templates.md               # Image generation prompt templates per slot type
      manifest-schema-reference.md      # Complete schema field reference
      patterns.md                       # Common multi-scene video patterns
```

#### Primary File (`SKILL.md`) Content Requirements

The primary file must contain (under 500 lines of Markdown):

1. **Purpose Statement** — What depthkit is, blind-authoring constraint.
2. **Quick Start** — Minimal single-scene example (stage + slow_push_forward, 3 required slots only).
3. **Manifest Structure Overview** — Top-level shape, field summary with types and defaults.
4. **Scene Authoring Workflow** — Numbered checklist: choose geometry → choose camera → assign images → set timing → set transitions.
5. **Geometry Summary Table** — One row per geometry (all 8), with name, required slots, default camera, "when to use."
6. **Camera Summary Table** — One row per camera, with compatible geometries and "when to use."
7. **Transitions Reference** — Inline. Three types (`cut`, `crossfade`, `dip_to_black`), adjacency rules.
8. **Easing Reference** — Inline. Six names with plain-English descriptions.
9. **Audio Synchronization** — How `start_time` and `duration` relate to audio.
10. **Anti-Patterns** — AP-03 (no manual coords), AP-07 (no text in parallax), escape hatch warnings.
11. **CLI Usage** — `depthkit render`, `depthkit validate`, `depthkit preview` with exact OBJ-046 flags.
12. **Sub-File Pointers** — Explicit loading instructions for LLM agents.
13. **Complete Annotated Example** — 5+ scenes, multiple geometries, transitions, audio.

**Size target:** Primary file < 500 lines. Combined total (primary + all sub-files) < 2000 lines / 60KB.

**Image path convention:** `./images/<scene_id>_<slot_name>.png` for images, `./audio/narration.mp3` for audio.

#### Design Decisions (OBJ-070)

- **D1: Modular architecture** — Primary + sub-files, not monolithic.
- **D2: Two examples** — Quick start (minimal) and complete (production-quality).
- **D3: Stage + slow_push_forward as reference** — OBJ-018 is "the default, most fundamental geometry."
- **D4: Summaries inline, details in sub-files** — LLM selects quickly from summary tables.
- **D5: Prompt templates separate** — Rendering engine is separate from asset generation (AP-04).
- **D8: Content manually authored** — Not auto-generated from registries.
- **D10: Transition rules inline** — Common error source, belongs next to workflow.
- **D13: CLI flags match OBJ-046 exactly** — `-W` (uppercase) for width, `-H` for height, `-o`, `-v`.

#### Acceptance Criteria (OBJ-070)

- [ ] **AC-01 through AC-06:** All files exist at specified paths.
- [ ] **AC-07 through AC-22:** Primary file contains all required sections (purpose, quick-start example, complete example, workflow checklist, summary tables, transitions, easing, audio sync, anti-patterns, CLI, sub-file pointers, version "3.0").
- [ ] **AC-08/AC-09:** Quick-start example is valid JSON passing `loadManifest()` with stage + slow_push_forward registered.
- [ ] **AC-10/AC-11:** Complete example is valid JSON passing `loadManifest()` with all referenced geometries/cameras registered.
- [ ] **AC-23 through AC-28:** Geometry reference sub-file has full `stage` section matching OBJ-018 exactly (slot names, required flags, compatible cameras, fog, transparency) plus stub sections for all other geometries.
- [ ] **AC-29 through AC-32:** Camera reference sub-file has full sections for `slow_push_forward`, `slow_pull_back`, `static`, `gentle_float`, plus stubs for others.
- [ ] **AC-33 through AC-35:** Prompt templates sub-file covers backgrounds, floors, subjects, foreground.
- [ ] **AC-36 through AC-38:** Schema reference documents every OBJ-004 field.
- [ ] **AC-39 through AC-41:** Patterns sub-file has 3+ patterns, at least one with complete JSON.
- [ ] **AC-42 through AC-47:** Cross-consistency with OBJ-004 field names, geometry names, camera names, easing enum, transition enum, seed vocabulary.
- [ ] **AC-48:** Total combined size under 2000 lines / 60KB.

---

### 1.2 SKILL.md Geometry and Camera Reference Sections (OBJ-071)

**Status:** Verified spec
**Depends on:** OBJ-070 (SKILL.md structure), OBJ-005 (Geometry type), OBJ-006 (Camera type), OBJ-018 (Stage), OBJ-019 (Tunnel)

OBJ-071 fills in the stub sections created by OBJ-070 with **full documentation for all verified geometries and cameras**.

#### Geometry Full Sections Added

| Geometry | Source | Required Slots | Default Camera | Fog |
|---|---|---|---|---|
| `tunnel` | OBJ-019 | floor, left_wall, right_wall, end_wall | tunnel_push_forward | #000000, near:15, far:50 |
| `canyon` | OBJ-020 | sky, left_wall, right_wall, floor | slow_push_forward | #1a1a2e, near:15, far:48 |
| `flyover` | OBJ-021 | sky, ground | slow_push_forward | #b8c6d4, near:20, far:55 |

**Critical note:** Flyover uses `ground` not `floor` (OBJ-021 D1).

#### Camera Full Sections Added

| Camera | Source | Compatible Geometries | Default Easing | Speed Scaling |
|---|---|---|---|---|
| `lateral_track_left/right` | OBJ-028 | stage, canyon*, diorama, portal, panorama | ease_in_out | X displacement (6 units) |
| `tunnel_push_forward` | OBJ-029 | tunnel only | ease_in_out_cubic | Z (25 units) AND Y rise (0.3 units) proportionally |
| `flyover_glide` | OBJ-030 | flyover only | ease_in_out | Z displacement (30 units), Y constant |

**\*Known compatibility asymmetry (D9):** `lateral_track_left/right` (OBJ-028) claims `canyon` compatibility, but `canyon` (OBJ-020) does NOT list lateral tracks in its `compatible_cameras`. **The geometry's list is authoritative for manifest validation.** Both the camera and canyon sections must include warning notes about this asymmetry.

#### Design Decisions (OBJ-071)

- **D1:** Full sections only for verified objectives. Stubs remain for diorama, portal, panorama, close_up (unverified).
- **D4:** Camera sections document speed scaling behavior per preset including ALL affected axes (not just primary).
- **D9:** Geometry's `compatible_cameras` is authoritative for validation; camera's `compatibleGeometries` is aspirational. Asymmetries documented with warnings.
- **D10:** Existing OBJ-070 content (stage, static, push/pull, gentle_float) preserved unchanged.

#### Acceptance Criteria (OBJ-071)

- [ ] **AC-01 through AC-09:** Tunnel full section with correct slots, cameras, fog, aspect, transparency, image guidance from `tunnelSlotGuidance`.
- [ ] **AC-10 through AC-18:** Canyon full section with correct data from OBJ-020.
- [ ] **AC-19 through AC-28:** Flyover full section with `ground` (not `floor`), correct cameras, fog, landmarks transparency.
- [ ] **AC-29/AC-30:** Updated stubs for unverified geometries.
- [ ] **AC-31 through AC-48:** Camera sections with correct compatible geometries, easing, speed scaling. Lateral track canyon caveat documented. Stubs for dramatic_push, crane_up, dolly_zoom.
- [ ] **AC-49 through AC-52:** SKILL.md summary tables updated for new content.
- [ ] **AC-53 through AC-59:** Cross-consistency (slot names, camera names, easing, fog hex values, vocabulary).
- [ ] **AC-60:** Total size under 2000 lines / 60KB.
- [ ] **AC-61:** OBJ-070 content preserved unchanged.

---

### 1.3 SKILL.md Prompt Templates, Patterns, and Anti-Patterns (OBJ-072)

**Status:** Description only (no full spec provided)
**Depends on:** OBJ-051 (Prompt guidance registry)

OBJ-072 extends `docs/skill/prompt-templates.md` with empirically tested prompt patterns and adds recipe patterns for common video types:

- **Prompt templates per depth slot type:** far_bg, mid_bg, midground, subject, near_fg (per seed Section 4.7). Sources content from OBJ-051's `SLOT_PROMPT_REGISTRY` via `getGuidanceForSlots()`.
- **Recipe patterns:** "5-scene explainer", "30-second social clip", other common types.
- **Anti-patterns:** AP-07 (no text in parallax planes), and additional authoring anti-patterns.

**Integration note:** OBJ-072 consumes OBJ-051's `getGuidanceForSlots()` to auto-generate prompt template documentation, surfacing `promptTemplate`, `themeUsageNote`, `examplePrompts`, `avoidList`, `perspectiveNotes` for each slot.

---

## Part 2: Asset Pipeline

### 2.1 Image Generation Strategy — Prompt Engineering (OBJ-051)

**Status:** Verified spec
**Depends on:** OBJ-007 (Depth Model), OBJ-018–021 (Geometries) — referenced, not imported
**Consumed by:** OBJ-054 (Cache), OBJ-072 (SKILL.md prompts), OBJ-056 (Manifest gen)

OBJ-051 defines the **prompt engineering knowledge base** for Flux.1 Schnell image generation. It provides structured prompt guidance per (geometry, slot) combination via a programmatic registry.

#### Core Types

```typescript
// src/prompts/types.ts

type PerspectiveOrientation = 'frontal' | 'top_down' | 'bottom_up' | 'side';

type SlotCacheCategory =
  | 'sky' | 'backdrop' | 'floor' | 'ceiling' | 'wall'
  | 'midground' | 'subject' | 'foreground' | 'landmark';

interface SlotPromptGuidance {
  readonly slotName: string;
  readonly geometryName: string;
  readonly perspective: PerspectiveOrientation;
  readonly requiresAlpha: boolean;
  readonly alphaSuffix: string;
  readonly contentDescription: string;
  readonly promptTemplate: string;           // Contains {theme} placeholder
  readonly themeUsageNote: string;
  readonly perspectiveNotes: string;
  readonly examplePrompts: readonly string[];
  readonly avoidList: readonly string[];
  readonly cacheCategory: SlotCacheCategory;
}
```

#### Registry API

```typescript
// src/prompts/slot-prompt-registry.ts

const SLOT_PROMPT_REGISTRY: ReadonlyMap<string, ReadonlyMap<string, SlotPromptGuidance>>;

function resolvePromptGuidance(geometryName: string, slotName: string): SlotPromptGuidance | undefined;
function getGuidanceForSlots(geometryName: string, slotNames: readonly string[]): ReadonlyMap<string, SlotPromptGuidance>;
function getCacheCategory(geometryName: string, slotName: string): SlotCacheCategory | undefined;
```

**Resolution order:** Geometry-specific entry → default taxonomy fallback → undefined.

#### Registry Coverage

| Geometry | Entries | Notes |
|---|---|---|
| `default` | 5 (sky, back_wall, midground, subject, near_fg) | Full reference implementations provided |
| `tunnel` | 5 (floor, ceiling, left_wall, right_wall, end_wall) | Full reference implementations provided |
| `stage` | 2 geometry-specific (backdrop, floor) + 4 default fallbacks | |
| `canyon` | 4+ geometry-specific (sky, left_wall, right_wall, floor) | Canyon sky is `bottom_up` (not frontal like default) |
| `flyover` | 4+ geometry-specific (ground, landmark_far, landmark_left, landmark_right) | |

#### Perspective-Aware Prompting Rules

| Rule | Orientation | Key Guidance |
|---|---|---|
| P1 | `top_down` (floors) | Request receding perspective or top-down textures; seamless/repeating patterns; avoid centered focal compositions |
| P2 | `bottom_up` (ceilings) | Overhead/architectural textures from below; same seamless requirements as floor |
| P3 | `side` (walls) | Elongated horizontal textures; horizontally seamless; scale matters (corridor vs cliff) |
| P4 | `frontal` (camera-facing) | Standard composition; transparency for subjects/foreground |

#### Cache Category Normalization

Multiple geometry-specific slot names map to the same cache category for cross-geometry reuse:

| Slot Name(s) | Cache Category | Cross-Geometry Sharing |
|---|---|---|
| sky | `sky` | Default sky, canyon sky share category (but different perspectives prevent bad reuse) |
| backdrop, back_wall, end_wall | `backdrop` | Tunnel end_wall shares with stage backdrop |
| floor, ground | `floor` | Tunnel floor, stage floor, flyover ground |
| ceiling | `ceiling` | |
| left_wall, right_wall | `wall` | Tunnel walls and canyon walls share category (prompt differentiation separates embeddings) |
| midground | `midground` | |
| subject | `subject` | |
| near_fg | `foreground` | |
| landmark_far, landmark_left, landmark_right | `landmark` | |

**Design decision D6:** Canyon walls (~14 units tall, cliff faces) and tunnel walls (~4 units tall, corridor panels) share `cacheCategory: 'wall'`. Differentiation is via prompt engineering, which naturally pushes embeddings apart below the 0.92 threshold.

#### Transparency Handling

- **Request alpha:** Subjects (all geometries), foreground elements, landmarks. Suffix: `", isolated on transparent background, PNG"`
- **Do NOT request alpha:** Sky, backdrop, floor, ceiling, wall, end_wall, ground.
- **Fallback:** When Flux.1 produces no alpha despite request, asset pipeline applies rembg for `subject`, `foreground`, `landmark` categories.

#### Module Structure

```
src/prompts/
  index.ts                    # Barrel export
  types.ts                    # PerspectiveOrientation, SlotPromptGuidance, SlotCacheCategory
  slot-prompt-registry.ts     # SLOT_PROMPT_REGISTRY, resolvePromptGuidance, getGuidanceForSlots, getCacheCategory
```

**Self-contained:** No imports from `src/spatial/` or `src/scenes/` (AC-36).

#### Acceptance Criteria (OBJ-051)

- [ ] **AC-01 through AC-05:** Registry completeness for default (5 slots), tunnel (5 slots), stage (2+), canyon (4+), flyover (4+).
- [ ] **AC-06 through AC-10:** Perspective correctness — every slot's perspective matches its geometry rotation.
- [ ] **AC-11 through AC-14:** Alpha/transparency flags match geometry definitions.
- [ ] **AC-15 through AC-17:** Cache category mappings correct.
- [ ] **AC-18 through AC-24:** Resolution functions work correctly (geometry-specific override, default fallback, unknown returns undefined).
- [ ] **AC-25 through AC-33:** Content quality (non-empty descriptions, templates with {theme}, example prompts, avoid lists, perspective notes for non-frontal).
- [ ] **AC-34 through AC-36:** Module structure (barrel export, zero runtime deps, no spatial imports).

---

### 2.2 Semantic Caching Database Schema (OBJ-053)

**Status:** Verified spec
**Depends on:** OBJ-007 (Depth Model — conceptual)
**Consumed by:** OBJ-054 (Cache middleware)

OBJ-053 defines the **AssetLibrary table** in Supabase (PostgreSQL + pgvector) that powers semantic image caching.

#### SQL DDL

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE asset_library (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slot_type       TEXT NOT NULL CHECK (char_length(slot_type) > 0 AND char_length(slot_type) <= 50),
  original_prompt TEXT NOT NULL CHECK (char_length(original_prompt) > 0 AND char_length(original_prompt) <= 2000),
  prompt_embedding VECTOR(1536) NOT NULL,
  image_url       TEXT NOT NULL CHECK (char_length(image_url) > 0 AND char_length(image_url) <= 2048),
  has_alpha       BOOLEAN NOT NULL DEFAULT false,
  width           INT CHECK (width IS NULL OR width > 0),
  height          INT CHECK (height IS NULL OR height > 0),
  usage_count     INT NOT NULL DEFAULT 1 CHECK (usage_count >= 1),
  embedding_model TEXT NOT NULL DEFAULT 'text-embedding-3-small'
                  CHECK (char_length(embedding_model) > 0 AND char_length(embedding_model) <= 100),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_used_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_asset_embedding ON asset_library
  USING ivfflat (prompt_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_asset_slot_type ON asset_library (slot_type);
CREATE INDEX idx_asset_slot_model ON asset_library (slot_type, embedding_model);
CREATE INDEX idx_asset_last_used ON asset_library (last_used_at);

ALTER TABLE asset_library ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON asset_library FOR ALL USING (true) WITH CHECK (true);
```

#### Optional RPC Function

```sql
CREATE OR REPLACE FUNCTION match_asset(
  query_embedding VECTOR(1536),
  query_slot_type TEXT,
  query_embedding_model TEXT DEFAULT 'text-embedding-3-small',
  match_count INT DEFAULT 1
) RETURNS TABLE (id UUID, image_url TEXT, original_prompt TEXT, has_alpha BOOLEAN,
                 width INT, height INT, similarity FLOAT)
LANGUAGE plpgsql AS $$ ... $$;
```

#### TypeScript Types

```typescript
// src/cache/asset-library.types.ts

interface AssetLibraryRow {
  readonly id: string;
  readonly slot_type: string;           // String, not SlotCacheCategory (no OBJ-051 import)
  readonly original_prompt: string;
  readonly prompt_embedding: number[];
  readonly image_url: string;
  readonly has_alpha: boolean;
  readonly width: number | null;
  readonly height: number | null;
  readonly usage_count: number;
  readonly embedding_model: string;
  readonly created_at: string;          // ISO 8601 (Supabase returns strings)
  readonly last_used_at: string;
}

// Recommended consumption types (guidance for OBJ-054)
interface AssetLibraryInsert { ... }
interface AssetSimilarityResult { ... }
```

#### Documented Query Patterns

| Query | Purpose | Key Filter |
|---|---|---|
| Query 1 | Similarity search (threshold gate) | `WHERE slot_type = $2 AND embedding_model = $3 ORDER BY prompt_embedding <=> $1 LIMIT 1` |
| Query 2 | Cache hit update | `UPDATE ... SET usage_count = usage_count + 1, last_used_at = now()` |
| Query 3 | Cache miss insert | `INSERT INTO ... RETURNING id` |
| Query 4 | Analytics | `GROUP BY slot_type` with avg reuse and total hits |
| Query 5 | LRU eviction (optional, not V1) | `DELETE WHERE last_used_at < now() - $1 AND usage_count < $2 RETURNING id, image_url` |

#### R2/S3 Storage Convention

- **Key pattern:** `assets/{slot_type}/{id}.png`
- **Full URL:** `{R2_PUBLIC_URL}/{bucket_name}/assets/{slot_type}/{id}.png`
- **Required env vars:** `R2_PUBLIC_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`

#### Key Design Decisions (OBJ-053)

- **D1:** `slot_type` uses OBJ-051's `SlotCacheCategory` values, stored as TEXT (not ENUM) for additive expansion.
- **D2:** `embedding_model` column added for safe model migration.
- **D3:** IVFFlat index (not HNSW) — appropriate for expected scale, faster inserts.
- **D7:** No uniqueness constraint on (slot_type, original_prompt) — non-deterministic generation means duplicates are valid.
- **D9:** TypeScript types use `string` for `slot_type`, not `SlotCacheCategory` — type narrowing happens in OBJ-054.

#### Acceptance Criteria (OBJ-053)

- [ ] **AC-01:** Table created with all specified columns and defaults.
- [ ] **AC-02:** CHECK constraints enforce all documented bounds.
- [ ] **AC-03 through AC-06:** All 4 indexes exist (IVFFlat embedding, btree slot_type, composite slot+model, btree last_used_at).
- [ ] **AC-07:** RLS enabled with permissive policy.
- [ ] **AC-08:** Optional match_asset RPC function (if deployed) has correct signature.
- [ ] **AC-09/AC-10:** Similarity query filters by slot_type + embedding_model, computes `1 - (embedding <=> query)`.
- [ ] **AC-11/AC-12:** Cache hit increments usage_count; cache miss returns id.
- [ ] **AC-13 through AC-15:** TypeScript types match schema, use string for slot_type, timestamps as strings.
- [ ] **AC-16/AC-17:** R2 storage convention documented with examples and env vars.
- [ ] **AC-18:** DDL includes `CREATE EXTENSION IF NOT EXISTS vector`.
- [ ] **AC-19:** Eviction query returns id + image_url for R2 cleanup.
- [ ] **AC-20:** No compile-time dependency on OBJ-051 in `src/cache/`.

#### File Placement

```
src/cache/
  index.ts                    # Barrel export
  asset-library.types.ts      # AssetLibraryRow, AssetLibraryInsert, AssetSimilarityResult
sql/
  001_create_asset_library.sql
  002_create_match_asset.sql  # Optional
```

---

### 2.3 Semantic Caching Middleware Logic (OBJ-054)

**Status:** Description only (no full spec provided)
**Depends on:** OBJ-053 (Schema), OBJ-051 (Prompt guidance)
**Validates:** TC-17, TC-18, TC-19, TC-20

OBJ-054 implements the threshold gate logic:

1. **Embed the prompt** via text embedding model (e.g., OpenAI `text-embedding-3-small`).
2. **Query Supabase** — calls `getCacheCategory()` from OBJ-051 to determine the `slot_type`, then executes Query 1 from OBJ-053 filtered by `slot_type` and `embedding_model`.
3. **Apply threshold:**
   - **Cosine similarity > 0.92** → Cache hit. Return `image_url`, execute Query 2 (increment usage).
   - **Cosine similarity ≤ 0.92** → Cache miss. Generate via Flux.1 API, apply background removal if `requiresAlpha: true` (OBJ-052), upload to R2 per convention, execute Query 3 (insert).

**Key responsibilities:**
- Type narrowing from `string` to `SlotCacheCategory` (since OBJ-053 uses string)
- Background removal routing based on `requiresAlpha` from OBJ-051
- Orphan handling (HTTP 404 from cached image_url → treat as miss, optionally delete row)
- Embedding + query latency target: < 500ms per image (TC-20)

---

### 2.4 Background Removal Integration (OBJ-052)

**Status:** Description only (no full spec provided)
**Validates:** TC-12 (rembg viable as subprocess, < 5s per image)

OBJ-052 provides background removal for images without alpha channels:

- **Primary:** `rembg` as a Python subprocess from Node.js.
- **Alternative:** Sharp-based chroma key (simpler but less robust).
- **Per-slot strategy:** Apply removal ONLY to `subject`, `foreground`, and `landmark` slots. `sky`, `backdrop`, `floor`, `ceiling`, `wall`, `midground` never need it.

Addresses OQ-02 from the seed (best strategy for images without alpha).

---

## Part 3: Production Pipeline

### 3.1 n8n HTTP Endpoint and Job Lifecycle (OBJ-055)

**Status:** Description only (no full spec provided)
**Validates:** SC-05

OBJ-055 wraps the depthkit library API in an Express/Fastify server:

- **POST endpoint:** Accepts `{ topic, duration, style }`, returns `{ job_id }`.
- **Poll endpoint:** Returns `{ status: "queued" | "rendering" | "completed" | "failed" }`.
- **Download endpoint:** Returns the rendered MP4.
- **Async job queue** for managing concurrent render requests.

Maps to Appendix A step 6 in the seed.

### 3.2 Manifest Generation via Claude API (OBJ-056)

**Status:** Description only (no full spec provided)
**Depends on:** OBJ-071 (SKILL.md geometry/camera reference)

OBJ-056 designs the prompt for generating structured manifest JSON from a topic and duration:

- Uses SKILL.md geometry reference (OBJ-071) as the knowledge base.
- Output must pass Zod validation from OBJ-004.
- Geometry and camera selection logic maps topic semantics to appropriate scene geometries.

Maps to Appendix A step 2 in the seed.

### 3.3 Asset Orchestration Pipeline (OBJ-057)

**Status:** Description only (no full spec provided)
**Depends on:** OBJ-054 (Cache), OBJ-052 (Background removal)

OBJ-057 is the **glue** between manifest generation, asset generation, and rendering:

1. Coordinate TTS call (Chatterbox TTS for narration audio).
2. Image retrieval with semantic caching (OBJ-054).
3. Background removal routing (OBJ-052).
4. Assembly of all inputs (images, audio, manifest JSON) into the structure depthkit expects.

Maps to Appendix A steps 2–4 in the seed.

---

## Part 4: Visual Tuning Workflow (OBJ-058)

**Status:** Verified spec
**Depends on:** OBJ-035 (Orchestrator)
**Consumed by:** OBJ-059–066 (Geometry tuning), OBJ-068 (Transition tuning)

OBJ-058 codifies the Director Agent visual tuning workflow from seed Sections 10.3–10.7.

### Test Render Utility

```typescript
// src/tools/test-render.ts

interface TestRenderConfig {
  manifest: unknown | string;
  registry: ManifestRegistry;
  geometryRegistry: GeometryRegistry;
  cameraRegistry: CameraPathRegistry;
  outputPath: string;
  assetsDir?: string;
  quality?: 'draft' | 'review' | 'proof';  // Default: 'review'
  maxDuration?: number;                      // Default: 30s
  isolateScene?: string;
  extractKeyframes?: boolean;                // Default: true
  gpu?: boolean;                             // Default: false
  debug?: boolean;                           // Default: true
}

const QUALITY_PRESETS = {
  draft:  { width: 640,  height: 360,  crf: 28, fps: 24 },
  review: { width: 1280, height: 720,  crf: 23, fps: 30 },
  proof:  { width: 1920, height: 1080, crf: 20, fps: 30 },
};

function resolveQualityDimensions(quality, manifestWidth, manifestHeight): { width, height, crf, fps };
async function renderTestClip(config: TestRenderConfig): Promise<TestRenderResult>;
```

**Key behaviors:**
- Clones manifest (never mutates original).
- Overrides resolution/fps per quality preset. Portrait manifests (aspect < 1.0) swap width/height.
- Always strips `composition.audio` (visual-only test renders).
- Truncates to `maxDuration` per D9 algorithm (strips trailing transitions).
- Isolates single scene if `isolateScene` set.
- Extracts keyframe PNGs at 25%, 50%, 75% of duration via FFmpeg post-processing.
- Propagates `OrchestratorError` without wrapping.

### HITL Tuning Loop Protocol

```
Step 0: Baseline Capture (Round 0)
  → Code Agent renders baseline clip, records preset_snapshot for TC-16 comparison

Step 1: Prepare Test Render
  → Code Agent calls renderTestClip() with quality: 'review', maxDuration: 30

Step 2: Director Agent Review (separate vision LLM session)
  → Human provides render to Director → Director produces Visual Critique

Step 3: HITL Circuit Breaker
  → Human reviews critique → approve / modify / reject / override
  → CRITICAL: Code Agent NEVER receives unfiltered Director output (AP-09)

Step 4: Code Agent Implementation
  → Receives only human-approved feedback
  → Translates directional deltas into parameter adjustments
  → Does NOT modify "working well" items unless required for higher-priority fix

Step 5: Convergence Check
  → Zero P1 issues + Human sign-off → visual_status: 'tuned'
  → Otherwise → return to Step 1
```

### Convergence Budget (TC-15)

- **≤ 5 budget-counted rounds** per geometry+camera combination.
- Round 0 (baseline) and rejected rounds do NOT count.
- If 5th round still has P1 issues → escalation (log failure, human decides: extend, restructure, or accept-with-caveat).

### Visual Critique Template

Required format for all Director Agent output:

```markdown
# Visual Critique — {geometry_or_preset_name}
## Status: RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL

**Objective:** {objective_id}
**Round:** {round_number}
...

### Overall Impression
### Timestamped Observations
### Edge Reveals
### Depth and Separation
### Motion Feel
### Priority Tweaks (Ordered by Impact)
  - P1: Must fix before convergence
  - P2: Improvement, not blocking
### Things That Work Well (PRESERVE THESE)
### Convergence Assessment
```

### Tuning Log Schema

```typescript
// src/tools/tuning-log-schema.ts

interface TuningRound {
  round: number;
  rendered_at: string;
  render_path: string;
  keyframe_paths: string[];
  quality: 'draft' | 'review' | 'proof';
  render_duration_seconds: number;
  preset_snapshot: Record<string, unknown> | null;  // Round 0 captures baseline for TC-16
  director_critique: string | null;
  priority_1_count: number | null;
  hitl_disposition: 'approved' | 'modified' | 'rejected' | 'overridden' | null;
  hitl_notes: string | null;
  approved_feedback: string | null;
  changes_made: string | null;
}

interface TuningLog {
  objective_id: string;
  target: string;
  camera_paths: string[];
  rounds: TuningRound[];
  status: 'in_progress' | 'converged' | 'abandoned';
  updated_at: string;
}
```

### meta.json Extension

```typescript
interface TuningObjectiveMeta {
  visual_status: null | 'needs_tuning' | 'in_progress' | 'tuned';
  tuning_rounds: number;  // Excludes round 0 and rejected rounds
}
```

### Acceptance Criteria (OBJ-058)

- [ ] **AC-01 through AC-05:** Visual Critique format includes all required sections.
- [ ] **AC-06 through AC-08:** HITL protocol defines four dispositions; Code Agent never receives unfiltered Director output; human sign-off required.
- [ ] **AC-09 through AC-12:** Convergence requires zero P1 issues + human sign-off; ≤ 5 rounds budget with escalation.
- [ ] **AC-13 through AC-20:** Test render utility (quality presets, maxDuration truncation, scene isolation, keyframe extraction, audio stripping, error propagation, no mutation).
- [ ] **AC-21 through AC-25:** Tuning log (round 0 baseline, per-round fields, status transitions, rejected rounds excluded from budget).
- [ ] **AC-26/AC-27:** TC-15 measurement framework defined.
- [ ] **AC-28/AC-29:** TC-16 measurement framework (round 0 baseline vs final, human 1-5 rating).
- [ ] **AC-30/AC-31:** Scope enforcement (tuning objectives only, never production).

### File Placement

```
src/tools/
  test-render.ts              # TestRenderConfig, renderTestClip(), QUALITY_PRESETS
  tuning-log-schema.ts        # Zod schema for TuningLog validation
```

---

## Part 5: Deployment (OBJ-050)

**Status:** Description only (no full spec provided)
**Validates:** TC-11 (engine runs in Docker with software WebGL)

OBJ-050 covers Docker containerization:

- Dockerfile with Chromium + FFmpeg dependencies
- Software WebGL (SwiftShader) in container
- Docker layer optimization for image size
- Health checks
- Must meet C-08 performance target in containerized environment

---

## Part 6: Verification & Validation

### 6.1 Deterministic Output Verification (OBJ-073)

**Status:** Verified spec
**Depends on:** OBJ-035 (Orchestrator), OBJ-013 (FFmpeg)
**Validates:** C-05, TC-06

#### Non-Determinism Source Audit

| Layer | Component | Sources | Mitigation |
|---|---|---|---|
| L1: Scene State | FrameClock, camera, easing | Math.random, Date.now | Audit: zero occurrences in render path |
| L2: WebGL | Three.js + SwiftShader | FP rounding, driver differences | Software rendering deterministic for same Chromium+arch |
| L3: Frame Capture | CDP captureScreenshot | PNG compression, async timing | Virtualized clock ensures completion before capture |
| L4: FFmpeg | H.264 encoding | Multithreaded races, timestamps | `deterministic: true` (single-threaded) |

#### Module API

```typescript
// src/engine/determinism.ts

interface VerifyDeterminismConfig {
  createConfig: (runIndex: number) => OrchestratorConfig;  // Must return unique outputPath per run
  runs?: number;              // Default: 3, range [2, 10]
  deterministicEncoding?: boolean;  // Advisory flag (default: true)
  ffmpegPath?: string;
  reportDir?: string;
  onRunComplete?: (runIndex: number, totalRuns: number, result: OrchestratorResult) => void;
}

interface FrameComparisonResult {
  totalFrames: number;
  identicalFrames: number;
  divergentFrames: number;
  worstCasePsnrDb?: number;
  divergentFrameIndices: number[];
  verdict: 'byte-identical' | 'visually-indistinguishable' | 'failed';
}

interface VerifyDeterminismReport {
  timestamp: string;
  runsCompleted: number;
  runsRequested: number;
  config: { deterministicEncoding: boolean; gpu: boolean };
  encodedComparison: FrameComparisonResult;
  renderDurationsMs: number[];
  outputPaths: string[];
  identifiedSources: NonDeterminismSource[];
  passed: boolean;
  summary: string;
}

async function verifyDeterminism(config: VerifyDeterminismConfig): Promise<VerifyDeterminismReport>;

// Lower-level utilities
async function extractFrameMd5s(mp4Path: string, ffmpegPath?: string): Promise<string[]>;
function compareFrameMd5s(runs: string[][]): FrameComparisonResult;
async function computePerFramePsnr(mp4Path1: string, mp4Path2: string, ffmpegPath?: string): Promise<number[]>;
function formatSummary(report: VerifyDeterminismReport): string;

class DeterministicRng {  // Contingency — xorshift128, may never be needed
  static fromSeed(seed: string): DeterministicRng;
  next(): number;
}
```

#### Verdict Thresholds

- **Byte-identical:** All frame MD5s match across all runs → PASS
- **Visually-indistinguishable:** MD5s differ but PSNR ≥ 60dB on all divergent frames → PASS
- **Failed:** Any frame with PSNR < 60dB → FAIL

#### Seeding Strategy

**Audit-first, seed-as-contingency.** Expected outcome: zero `Math.random()`, `Date.now()` (for state), or `crypto.getRandomValues()` in the render path. `DeterministicRng` exists as contingency only.

#### Non-Determinism Audit Checklist

Grep `src/engine/`, `src/page/`, `src/scenes/`, `src/camera/` for prohibited patterns:
- `Math.random` — None allowed
- `Date.now()` / `new Date()` — Logging only
- `crypto.getRandomValues` / `crypto.randomUUID` — None
- `requestAnimationFrame` — None in production render path (AP-02)

#### Acceptance Criteria (OBJ-073)

- [ ] **AC-01 through AC-03:** Code audit confirms zero prohibited patterns in render path.
- [ ] **AC-04/AC-05:** Same manifest rendered 3× with software WebGL + deterministic encoding → byte-identical MD5s.
- [ ] **AC-06/AC-07:** Verdict logic correct for PSNR fallback.
- [ ] **AC-08 through AC-13:** Module API (3-run default, RangeError for invalid counts, partial failure handling, frame count mismatch detection).
- [ ] **AC-14 through AC-20:** Lower-level utilities (extractFrameMd5s, compareFrameMd5s, computePerFramePsnr).
- [ ] **AC-21 through AC-23:** Report structure complete.
- [ ] **AC-24/AC-25:** Seeding contingency exists, audit documented.

#### File Placement

```
src/engine/
  determinism.ts
```

---

### 6.2 Performance Benchmark (OBJ-074)

**Status:** Verified spec
**Depends on:** OBJ-035 (Orchestrator), OBJ-049 (Rendering Config), OBJ-018 (Stage)
**Validates:** C-08, TC-02

#### Reference Benchmark Parameters

| Parameter | Value | Source |
|---|---|---|
| Resolution | 1920×1080 | C-08 |
| FPS | 30 | C-08 |
| Duration | 60 seconds (1800 frames) | C-08 |
| Scenes | 5 × 12 seconds | C-08 |
| Planes per scene | 6 (all stage slots) | Exceeds C-08's 5-plane minimum |
| Geometry | `stage` | Most representative |
| Camera | `slow_push_forward` | Default for stage |
| Transitions | `cut` only | Isolate render performance |
| Audio | None | Isolate video rendering |

#### Module API

```typescript
// src/benchmark/runner.ts

function getReferenceBenchmarkParameters(): Readonly<BenchmarkParameters>;
function generateReferenceManifest(): Manifest;
async function generateBenchmarkAssets(outputDir: string): Promise<Map<string, string>>;

async function runBenchmark(config?: BenchmarkConfig): Promise<BenchmarkReport>;
async function runComparisonBenchmark(config?): Promise<ComparisonReport>;

function formatBenchmarkReport(report: BenchmarkReport): string;
function formatComparisonReport(report: ComparisonReport): string;
```

**Self-contained assets:** Solid-color PNGs generated via Node.js `zlib` (no image library dependency). Subject and near_fg include alpha channels.

#### Compliance Thresholds (Constants, Not Configurable)

| Constraint | Threshold | Measured Value |
|---|---|---|
| C-08 | < 900,000ms (15 min) | `timing.orchestratorTotalMs` |
| TC-02 | < 500ms/frame | `timing.averageFrameMs` |

#### BenchmarkReport Structure

```typescript
interface BenchmarkReport {
  timestamp: string;
  version: string;                    // From package.json
  parameters: BenchmarkParameters;
  environment: EnvironmentInfo;       // Node, OS, CPU, RAM, FFmpeg, Chromium versions
  rendererInfo: RendererInfo;         // From OBJ-010
  isSoftwareRenderer: boolean;        // Derived from gpuRenderer string
  gpuMode: { requested: GpuMode; actual: 'software' | 'hardware' };
  timing: TimingResults;              // Total, render loop, avg/median/p95/p99/max/min/stddev, throughput
  captureStats: CaptureStats;         // From OBJ-012
  frameTimings?: FrameTiming[];       // Per-frame when collected
  compliance: ComplianceResult;       // C-08 and TC-02 pass/fail with headroom
  outputVideoPath: string;
  frameTimingsCsvPath: string | null;
}
```

#### Comparison Benchmark

`runComparisonBenchmark()` runs software first (always succeeds), then hardware (may fail). If hardware falls back to SwiftShader, `hardwareFellBackToSoftware: true` with warning in formatted output.

#### Acceptance Criteria (OBJ-074)

- [ ] **AC-01 through AC-05:** Reference manifest and assets correct.
- [ ] **AC-06 through AC-09:** Benchmark execution produces valid MP4.
- [ ] **AC-10 through AC-14:** Timing and statistics (1800 frame timings, percentiles, throughput).
- [ ] **AC-15 through AC-20:** Compliance assessment (hardcoded thresholds, correct headroom formula).
- [ ] **AC-21 through AC-27:** Environment and renderer info populated.
- [ ] **AC-28 through AC-30:** Report output (JSON + CSV + formatted string).
- [ ] **AC-31 through AC-33:** Comparison benchmark tolerant of hardware failure.
- [ ] **AC-34/AC-35:** Error handling (render failure, write failure).
- [ ] **AC-36/AC-37:** Performance gate on qualifying hardware.
- [ ] **AC-38:** Version from package.json.

#### File Placement

```
src/benchmark/
  runner.ts
  fixtures/
    generate-assets.ts          # Solid-color PNG generation via zlib
```

---

### 6.3 Blind Authoring Test Plan (OBJ-075)

**Status:** Verified spec
**Depends on:** OBJ-070 (SKILL.md), OBJ-046 (CLI)
**Validates:** TC-08, TC-04, TC-01, SC-02

OBJ-075 defines test procedures (not code) for validating blind-authoring capability.

#### Four Test Procedures

| Procedure | Claim | Method | Pass Criterion |
|---|---|---|---|
| TC-08: 25-Topic Geometry Mapping | 8 geometries cover the design space | Paper exercise — map each topic to best-fit geometry | ≥ 20/25 (80%) accommodated |
| TC-04: 10 LLM Manifests | Geometries eliminate manual 3D positioning | LLM authors 10 manifests in isolation, validated via `depthkit validate` | All 10 pass validation AND zero `position_override`/`rotation_override` |
| TC-01: 15 Scene Types | 3-5 planes handle 90% of common scenes | Evaluate each scene type against geometry slot counts | ≥ 14/15 (≥90%) handled with ≤5 planes |
| SC-02: 5-Topic Visual Review | Blind authoring produces correct video | LLM authors 5 manifests, rendered, human scores | All 5 render; ≥ 4/5 score "correct and professional" |

#### 25 Topics (Appendix A in OBJ-075)

Spans 8+ domains: Nature (deep sea creatures, coral reefs, volcanoes, African savanna, rainforest, northern lights), Science (space exploration, quantum computing, Mars colonization), History (ancient Rome, medieval castles, samurai, Egyptian pyramids), Technology (AI, EVs, cryptocurrency), Arts (Renaissance art, jazz, ballet, street photography), Food (cooking basics, coffee journey), Medicine (human heart), Health (pandemic preparedness), Mythology (Greek mythology).

#### SC-02 Scoring Rubric

4 dimensions, 1-5 scale each:

1. **Spatial Correctness** — Planes positioned correctly, no z-fighting.
2. **Camera Motion Quality** — Smooth, appropriate speed, no edge reveals.
3. **Scene Composition** — Appropriate geometry choice, effective slot usage.
4. **Overall Impression** — Professional, watchable, "correct and professional."

**Pass:** Every dimension ≥ 3 AND Overall Impression ≥ 4.

#### LLM Isolation Protocol (D10)

1. Start fresh LLM conversation (no prior depthkit context).
2. Provide SKILL.md as sole reference.
3. Issue authoring prompt.
4. Accept manifest as-is — no corrections or guidance.

#### Acceptance Criteria (OBJ-075)

- [ ] **AC-01 through AC-06:** All test plan files exist.
- [ ] **AC-07 through AC-11:** TC-08 procedure with mapping exercise, 80% threshold.
- [ ] **AC-12 through AC-17:** TC-04 procedure with 10 manifests, zero overrides, 8 landscape + 2 portrait.
- [ ] **AC-18 through AC-20:** TC-01 procedure with 15 scene types, 90% threshold.
- [ ] **AC-21 through AC-28:** SC-02 procedure with 5 seed topics, rendering + scoring, unregistered geometry handling.
- [ ] **AC-29 through AC-31:** Scoring rubric with 4 dimensions, 1-5 scale, threshold definitions.
- [ ] **AC-32 through AC-37:** Cross-consistency and executability.

#### File Placement

```
test/plans/blind-authoring/
  README.md
  topics-25.md
  scene-types-15.md
  scoring-rubric.md
  tc08-geometry-mapping.md
  tc04-manifest-validation.md
  tc01-plane-sufficiency.md
  sc02-blind-authoring.md
  results/
```

---

### 6.4 Semantic Cache Validation Plan (OBJ-076)

**Status:** Description only (no full spec provided)
**Validates:** TC-17, TC-18, TC-19, TC-20

OBJ-076 defines procedures for:

- **TC-17:** Threshold tuning — 50+ cache hit pairs judged by human, ≥90% acceptable.
- **TC-18:** Cross-slot contamination — confusable prompts across slot types, filter prevents mismatches.
- **TC-19:** Hit rate at steady state — ≥30% after 50+ videos.
- **TC-20:** Query latency — embed + query + return < 500ms per image.

---

### 6.5 End-to-End Integration Test Plan (OBJ-077)

**Status:** Verified spec
**Depends on:** OBJ-035 (Orchestrator), OBJ-046 (CLI), OBJ-037 (Sequencer), OBJ-038 (Timing)
**Consumed by:** OBJ-078 (Execution Gate)

OBJ-077 is the concrete, step-by-step test plan executed by OBJ-078.

#### Test Suites

| Suite | Success Criterion | Procedures |
|---|---|---|
| Suite 0: Smoke | Pipeline functional | SMOKE-01: 2s, 320x240, 1 scene → valid MP4 |
| Suite 1: SC-01 | 60s 5-scene video renders | SC01-01: ffprobe validation (codec, resolution, fps, duration, audio, frame count, faststart) |
| | | SC01-02: Manual playback in VLC + browser |
| | | SC01-03: Determinism (frame MD5 × 2 runs, PSNR ≥ 60dB fallback) |
| | | SC01-04: Audio drives video length (45s audio → 45s output) |
| Suite 2: SC-03 | Performance target | SC03-01: Environment verification (4 cores, 4GB+ RAM) |
| | | SC03-02: 3 runs median < 15 min (software WebGL) |
| | | SC03-03: GPU comparison (optional, informational) |
| Suite 3: SC-05 | n8n integration | SC05-01: POST → job_id |
| | | SC05-02: Poll → completed (20 min timeout, 10s interval) |
| | | SC05-03: Download → valid MP4 |
| Suite 4: SC-06 | Validation soundness | SC06-FORWARD: 20 valid manifests all render successfully |
| | | SC06-BACKWARD-A: 22 invalid manifests all fail validation |
| | | SC06-BACKWARD-B: 3 pre-flight failures fail before rendering |

#### Benchmark Fixture (F-01)

5 scenes × 60 seconds using 4 verified geometries and 5 camera presets:

| Scene | Geometry | Camera | Duration | Planes |
|---|---|---|---|---|
| scene_001 | tunnel | slow_push_forward | 13.0s | 5 (floor, ceiling, left_wall, right_wall, end_wall) |
| scene_002 | stage | gentle_float | 13.0s | 3 (backdrop, floor, subject) |
| scene_003 | canyon | lateral_track_left | 12.0s | 5 (floor, left_wall, right_wall, end_wall, sky) |
| scene_004 | flyover | crane_up | 12.0s | 3+ (ground, sky, landmark) |
| scene_005 | stage | static | 12.5s | 3 (backdrop, floor, subject) |

Transitions: 2 crossfade, 3 dip_to_black, 1 cut. Audio: 60s 440Hz sine tone.

#### SC-06 Invalid Manifest Corpus (F-04a: 22 manifests)

Covers: missing fields, wrong version, zero dimensions, empty scenes, unknown geometry/camera, incompatible camera, missing required slots, extra slots, crossfade on first scene, duplicate IDs, invalid JSON, wrong JSON type, empty strings, non-integer dimensions.

#### SC-06 Pre-Flight Corpus (F-04b: 3 manifests)

Pass validation but fail at render: non-existent image files, multiple missing images, non-existent audio.

#### Key Design Decisions (OBJ-077)

- **D2:** Merged benchmark fixture serves both SC-01 (correctness) and SC-03 (performance).
- **D3:** SC-05 (n8n) gated on OBJ-057/OBJ-075 verification status.
- **D4:** All fixtures use only verified geometries and cameras.
- **D5:** Split invalid corpus — schema failures (validate) vs pre-flight failures (render).
- **D6:** Frame MD5 primary, PSNR ≥ 60dB fallback for determinism.
- **D7:** 3 benchmark runs, report median.
- **D8:** `ffprobe -v quiet -print_format json -show_format -show_streams` as canonical validation.

#### Traceability Matrix

| Constraint/Claim | Procedures |
|---|---|
| C-02 (Pipeline) | SC01-01 |
| C-03/C-05 (Determinism) | SC01-03 |
| C-04 (Resolution/FPS) | SC06-FORWARD (V-09, V-10, V-11) |
| C-07 (Audio sync) | SC01-01, SC01-04 |
| C-08 (Performance) | SC03-02 |
| C-10 (Validation) | SC06-BACKWARD-A, SC06-BACKWARD-B |
| C-11 (Software WebGL) | SC03-02 |
| TC-02 (< 500ms/frame) | SC03-02 |
| TC-06 (Deterministic) | SC01-03 |
| TC-07 (Validation catches errors) | SC06-BACKWARD-A, SC06-BACKWARD-B |
| TC-10 (Transitions) | SC01-01, SC01-02 |
| TC-13 (Audio drives length) | SC01-04 |

#### Acceptance Criteria (OBJ-077)

- [ ] **AC-01:** Five suites defined (Smoke, SC-01, SC-03, SC-05, SC-06).
- [ ] **AC-02:** Each procedure has unique ID, preconditions, literal CLI commands, exact assertions, pass/fail.
- [ ] **AC-03:** SC-01 covers 60s 5-scene, 3+ geometries, 3+ cameras, all transition types, audio, playback, determinism, audio-driven duration.
- [ ] **AC-04:** SC-03 specifies 3-run median, 15-minute threshold.
- [ ] **AC-05:** SC-05 documents POST/poll/download with 20-min timeout.
- [ ] **AC-06:** SC-06 tests both directions with 20 valid + 22 invalid + 3 pre-flight.
- [ ] **AC-07:** Determinism uses frame MD5 + PSNR ≥ 60dB fallback.
- [ ] **AC-08:** Fixtures reference only verified geometries/cameras.
- [ ] **AC-09:** Test image/audio generation commands provided.
- [ ] **AC-10:** ffprobe canonical invocation specified.
- [ ] **AC-11:** Each procedure references TC/C identifiers.
- [ ] **AC-12:** V-08 and V-17 assert specific warning codes.

---

### 6.6 End-to-End Validation Execution Gate (OBJ-078)

**Status:** Description only (no full spec provided)

OBJ-078 is the **capstone objective**. It executes OBJ-077's test plans against:
- All tuned geometries (via OBJ-067)
- Validated transitions (via OBJ-068)
- Full asset orchestration pipeline (OBJ-057)
- Audio sync (OBJ-038)

This is the SC-01/SC-03/SC-05/SC-06/SC-07 gate. **The project is production-ready when OBJ-078 passes.**

---

## Cross-Category Integration Points

### Engine → Integration

| Engine Component | Integration Consumer | Interface |
|---|---|---|
| OBJ-035 (Orchestrator) | OBJ-058 (Test Render), OBJ-073 (Determinism), OBJ-074 (Benchmark) | `Orchestrator` class, `render()`, `OrchestratorResult` |
| OBJ-004 (Schema) | OBJ-070 (SKILL.md), OBJ-056 (Manifest gen) | Field names, types, Zod validation, `loadManifest()` |
| OBJ-046 (CLI) | OBJ-070 (SKILL.md), OBJ-077 (E2E tests) | Command names, flag conventions (`-W`, `-H`, `-o`, `-v`) |
| OBJ-013 (FFmpeg) | OBJ-073 (Determinism) | `resolveFFmpegPath()`, `deterministic` config flag |
| OBJ-049 (Rendering Config) | OBJ-074 (Benchmark) | `resolveRenderingConfig()`, `GpuMode` |

### Spatial → Integration

| Spatial Component | Integration Consumer | Interface |
|---|---|---|
| OBJ-007 (Depth Model) | OBJ-051 (Prompts), OBJ-053 (Schema) | Slot taxonomy, `expectsAlpha` |
| OBJ-018 (Stage) | OBJ-070 (SKILL.md), OBJ-074 (Benchmark) | Slot names, compatible_cameras, fog, description |
| OBJ-019 (Tunnel) | OBJ-051 (Prompts), OBJ-071 (SKILL.md) | Slot names, `tunnelSlotGuidance`, compatible_cameras |
| OBJ-020 (Canyon) | OBJ-051 (Prompts), OBJ-071 (SKILL.md) | Slot metadata, compatible_cameras |
| OBJ-021 (Flyover) | OBJ-051 (Prompts), OBJ-071 (SKILL.md) | Slot names (`ground` not `floor`), compatible_cameras |

### Integration → Tuning (spatial category)

| Integration Component | Tuning Consumer | Interface |
|---|---|---|
| OBJ-058 (Director workflow) | OBJ-059–066 (Geometry tuning) | `renderTestClip()`, Visual Critique template, TuningLog schema, HITL protocol |

---

## Noted Inconsistencies

### 1. Lateral Track / Canyon Compatibility Asymmetry

**OBJ-028** (lateral tracks) claims `canyon` in `compatibleGeometries`. **OBJ-020** (canyon) does NOT list lateral tracks in `compatible_cameras`. OBJ-071 D9 resolves this: **geometry is authoritative for validation**. Both SKILL.md sections must include warning notes. This asymmetry may indicate a spec-level conflict that should be resolved upstream — either canyon should add lateral tracks, or OBJ-028 should remove canyon.

### 2. OBJ-051 `promptGuidance` vs OBJ-007/Geometry Specs

OBJ-007's `DEFAULT_SLOT_TAXONOMY` and geometry specs (OBJ-018–021) include preliminary `promptGuidance` strings. OBJ-051's `SLOT_PROMPT_REGISTRY` **supersedes all of them** as the single source of truth (OBJ-051 D8). Downstream consumers (OBJ-072, OBJ-054) import from `src/prompts/`, not from `promptGuidance` fields on spatial types.

### 3. Camera Names in OBJ-077 Fixture F-01

OBJ-077's benchmark fixture lists `lateral_track_left` for scene_003 (canyon) and `crane_up` for scene_004 (flyover). However:
- Canyon does not list `lateral_track_left` as compatible (per OBJ-020). The fixture should use a canyon-compatible camera (e.g., `slow_push_forward`).
- `crane_up` (OBJ-033) is listed as `status: "open"` — not yet verified. The fixture should use a verified flyover-compatible camera (e.g., `flyover_glide` from OBJ-030, or `slow_push_forward`).

**Resolution:** OBJ-078 (the executor) must adjust the F-01 manifest to use only verified cameras that are compatible with each scene's geometry. OBJ-077 already notes this: "OBJ-078 must consult each geometry's PlaneSlot definitions and adjust the manifest accordingly."

### 4. OBJ-077 Camera Reference Numbers

OBJ-077 references OBJ-029 as `lateral_track_left` and OBJ-030 as `crane_up`. Per the spatial spec, OBJ-028 is lateral tracks, OBJ-029 is tunnel_push_forward, OBJ-030 is flyover_glide. The F-01 fixture table lists camera OBJ numbers that don't match the actual camera names. This is a documentation error in the fixture table's parenthetical references, not a functional issue — the camera names themselves are what matter for the manifest.

### 5. SC-05 Endpoint Contract

OBJ-077's SC-05 procedures assume endpoint URL `http://localhost:5678/webhook/depthkit` and response fields `job_id`, `status`, `download_url`. OBJ-055 (n8n HTTP endpoint) has no full spec — these are placeholders. OBJ-078 must consult OBJ-055's actual specification when available.

---

## Implementation Order Guidance

### Phase 1: Documentation Foundation (can start immediately)
1. **OBJ-070** — SKILL.md structure and core content
2. **OBJ-071** — Geometry and camera reference sections (depends on OBJ-070)
3. **OBJ-072** — Prompt templates and patterns (depends on OBJ-051)

### Phase 2: Asset Pipeline (can start immediately, parallel with Phase 1)
1. **OBJ-051** — Prompt engineering registry (`src/prompts/`)
2. **OBJ-053** — Database schema (`sql/`, `src/cache/`)
3. **OBJ-052** — Background removal integration
4. **OBJ-054** — Caching middleware (depends on OBJ-051, OBJ-053)

### Phase 3: Visual Tuning Infrastructure (requires engine Orchestrator)
1. **OBJ-058** — Director Agent workflow + test render utility (depends on OBJ-035)

### Phase 4: Verification Tools (requires engine Orchestrator)
1. **OBJ-073** — Deterministic output verification (depends on OBJ-035)
2. **OBJ-074** — Performance benchmark (depends on OBJ-035, OBJ-049)

### Phase 5: Production Pipeline (requires SKILL.md + Asset Pipeline)
1. **OBJ-055** — n8n HTTP endpoint
2. **OBJ-056** — Manifest generation via Claude API (depends on OBJ-071)
3. **OBJ-057** — Asset orchestration pipeline (depends on OBJ-054, OBJ-052)

### Phase 6: Deployment
1. **OBJ-050** — Docker containerization

### Phase 7: Validation (requires everything above)
1. **OBJ-075** — Blind authoring test plan (depends on OBJ-070, OBJ-046)
2. **OBJ-076** — Semantic cache validation plan
3. **OBJ-077** — E2E integration test plan (depends on OBJ-035, OBJ-046)
4. **OBJ-078** — Execution gate (capstone — depends on everything)
