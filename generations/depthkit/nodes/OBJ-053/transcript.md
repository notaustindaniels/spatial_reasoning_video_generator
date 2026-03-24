# Deliberation Transcript: OBJ-053

---

## Round 1 — spec_author

I'll start by reviewing the relevant files to understand the current project state.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me review the existing project structure and relevant files to understand the current state.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-053/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-053/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-007/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-051/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-054/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-054/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-054/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-054",
     3→  "description": "Semantic caching middleware logic -- embed prompt (via text embedding model), query Supabase AssetLibrary filtered by slot_type, apply threshold gate (cosine similarity > 0.92 = cache hit, skip generation; <= 0.92 = cache miss, generate and cache). Cache hit: return image_url, increment usage_count. Cache miss: call Flux.1 API, apply background removal if needed, upload to R2, INSERT into AssetLibrary. Covers TC-17 (threshold acceptable), TC-18 (slot-type filtering prevents contamination), TC-19 (hit rates 30-60%), TC-20 (query latency negligible).",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-053", "OBJ-051"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. Medium priority."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md"
}
[Tool Error] File content (14034 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: Image Generation Strategy — Flux.1 Schnell Prompt Engineering Per Slot Type (OBJ-051)
     2→
     3→## Summary
     4→
     5→OBJ-051 defines the **image generation prompt engineering strategy** for depthkit — the prompt templates, perspective-aware prompting rules, transparency handling guidelines, and per-slot-type generation guidance that enable an LLM to produce Flux.1 Schnell image prompts that are spatially appropriate for each slot in each geometry. This is a knowledge artifact with a thin programmatic interface: a `SlotPromptGuidance` type system and a `SLOT_PROMPT_REGISTRY` data structure that maps `(geometry, slot_name)` pairs to structured prompt guidance. It is consumed by OBJ-072 (SKILL.md prompt templates section), OBJ-054 (semantic caching middleware — uses `slot_type` categorization for cache queries), and indirectly by any LLM authoring pipeline that needs to generate images for a manifest.
     6→
     7→## Interface Contract
     8→
     9→##... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md",
  "offset": 80,
  "limit": 80
}
[Tool Result]     80→
    81→  /**
    82→   * How the plane is oriented in 3D space.
    83→   * Drives the perspective-aware prompting rules.
    84→   */
    85→  readonly perspective: PerspectiveOrientation;
    86→
    87→  /**
    88→   * Whether the generated image should have a transparent
    89→   * background (alpha channel). Maps to DepthSlot.expectsAlpha
    90→   * from OBJ-007.
    91→   */
    92→  readonly requiresAlpha: boolean;
    93→
    94→  /**
    95→   * A reusable prompt suffix/instruction for requesting transparency.
    96→   * Empty string if requiresAlpha is false.
    97→   * Example: ", isolated on transparent background, PNG"
    98→   */
    99→  readonly alphaSuffix: string;
   100→
   101→  /**
   102→   * General description of what kind of image content belongs in
   103→   * this slot. 1-2 sentences.
   104→   */
   105→  readonly contentDescription: string;
   106→
   107→  /**
   108→   * Concrete prompt template with a `{theme}` placeholder.
   109→   * The ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md",
  "offset": 155,
  "limit": 100
}
[Tool Result]    155→   * category for the AssetLibrary's slot_type column.
   156→   *
   157→   * This enables cross-geometry cache sharing: a 'floor' texture
   158→   * generated for a tunnel can be reused for a canyon's 'floor'
   159→   * because they share the same cache category.
   160→   */
   161→  readonly cacheCategory: SlotCacheCategory;
   162→}
   163→```
   164→
   165→### Registry Structure
   166→
   167→```typescript
   168→// src/prompts/slot-prompt-registry.ts
   169→
   170→import type { SlotPromptGuidance, SlotCacheCategory } from './types';
   171→
   172→/**
   173→ * The complete registry of prompt guidance for all geometry/slot
   174→ * combinations.
   175→ *
   176→ * Structure: Map<geometryName, Map<slotName, SlotPromptGuidance>>
   177→ *
   178→ * Includes a 'default' geometry key for the default slot taxonomy
   179→ * (OBJ-007's DEFAULT_SLOT_TAXONOMY). Geometry-specific entries
   180→ * override defaults when both exist for the same slot name.
   181→ */
   182→e... [truncated]
Now I have a good understanding of the ecosystem. OBJ-051 defines `SlotCacheCategory` — the canonical categories used in the `AssetLibrary.slot_type` column. Let me also quickly check the existing spatial types from OBJ-003:
[Tool: Glob]
  Input: {
  "pattern": "**/src/spatial/**"
}
[Tool Result] No files found

[Tool: Grep]
  Input: {
  "pattern": "SlotCacheCategory",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md",
  "output_mode": "content"
}
[Tool Result] 49:export type SlotCacheCategory =
161:  readonly cacheCategory: SlotCacheCategory;
170:import type { SlotPromptGuidance, SlotCacheCategory } from './types';
241: * @returns The SlotCacheCategory, or undefined if no guidance exists.
246:): SlotCacheCategory | undefined;
257:  SlotCacheCategory,
654:**Extensibility:** `SlotCacheCategory` is a union type. New geometries may introduce new categories (additive, non-breaking change). Existing cache entries are unaffected.
831:                                  #   SlotCacheCategory
Good. Now I have all the context I need. Let me propose the specification.

---

# Specification Proposal: OBJ-053 — Semantic Caching Database Schema

## Summary

OBJ-053 defines the **AssetLibrary database schema** for Supabase (PostgreSQL + pgvector) that powers depthkit's semantic image caching layer. It specifies the table structure, column definitions, indexes, constraints, the R2/S3 storage convention for cached images, and the SQL query patterns that OBJ-054 (the middleware logic) will use. This is a schema-only objective — it produces SQL DDL, a TypeScript row type mirroring the table, and documented query patterns. It does not implement the middleware, embedding logic, or threshold gate (those are OBJ-054).

## Interface Contract

### Database Schema (SQL DDL)

```sql
-- =============================================================
-- AssetLibrary table — semantic cache for generated image assets
-- Requires: pgvector extension enabled in Supabase project
-- =============================================================

-- Ensure pgvector is available
CREATE EXTENSION IF NOT EXISTS vector;

-- Core table
CREATE TABLE asset_library (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Canonical slot category (not raw geometry slot name).
  -- Values correspond to OBJ-051's SlotCacheCategory union:
  -- 'sky' | 'backdrop' | 'floor' | 'ceiling' | 'wall' |
  -- 'midground' | 'subject' | 'foreground' | 'landmark'
  -- TEXT (not ENUM) to allow additive expansion without migrations.
  slot_type       TEXT NOT NULL
                  CHECK (char_length(slot_type) > 0 AND char_length(slot_type) <= 50),

  -- The exact prompt used to generate this image.
  original_prompt TEXT NOT NULL
                  CHECK (char_length(original_prompt) > 0 AND char_length(original_prompt) <= 2000),

  -- Embedding of original_prompt. Dimension 1536 matches
  -- OpenAI text-embedding-3-small. If a different embedding model
  -- is used, the dimension must match. The column dimension is
  -- enforced by pgvector at INSERT time.
  prompt_embedding VECTOR(1536) NOT NULL,

  -- URL to the cached image in R2/S3.
  -- Must be a valid URL (https:// or s3://).
  image_url       TEXT NOT NULL
                  CHECK (char_length(image_url) > 0 AND char_length(image_url) <= 2048),

  -- Whether background removal was applied (rembg or equivalent).
  has_alpha       BOOLEAN NOT NULL DEFAULT false,

  -- Source image dimensions for sizing validation.
  -- Nullable: may not always be known at insert time
  -- (e.g., if generation API doesn't return dimensions).
  width           INT CHECK (width IS NULL OR width > 0),
  height          INT CHECK (height IS NULL OR height > 0),

  -- Tracks reuse frequency for analytics and cache eviction heuristics.
  usage_count     INT NOT NULL DEFAULT 1
                  CHECK (usage_count >= 1),

  -- The embedding model identifier used to generate prompt_embedding.
  -- Enables safe re-embedding or mixed-model queries.
  -- e.g., 'text-embedding-3-small', 'text-embedding-3-large'
  embedding_model TEXT NOT NULL DEFAULT 'text-embedding-3-small'
                  CHECK (char_length(embedding_model) > 0 AND char_length(embedding_model) <= 100),

  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_used_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================
-- Indexes
-- ============================

-- Primary similarity search index: IVFFlat on prompt_embedding
-- using cosine distance, scoped by slot_type via WHERE clause
-- in queries. lists=100 is appropriate for up to ~100k rows;
-- should be increased if the table grows significantly.
--
-- NOTE: IVFFlat requires training data to build the index.
-- For an empty or small table (<1000 rows), pgvector falls back
-- to sequential scan, which is acceptable for cold-start. The
-- index becomes effective once sufficient rows exist.
CREATE INDEX idx_asset_embedding ON asset_library
  USING ivfflat (prompt_embedding vector_cosine_ops)
  WITH (lists = 100);

-- Btree index on slot_type for the WHERE filter in similarity queries.
CREATE INDEX idx_asset_slot_type ON asset_library (slot_type);

-- Composite index for the most common query pattern:
-- filter by slot_type + embedding_model, then vector search.
CREATE INDEX idx_asset_slot_model ON asset_library (slot_type, embedding_model);

-- Index on last_used_at for cache eviction queries (LRU).
CREATE INDEX idx_asset_last_used ON asset_library (last_used_at);

-- ============================
-- Row-Level Security (RLS)
-- ============================
-- Supabase requires RLS to be enabled for tables accessed via
-- the REST API. The pipeline uses the service_role key, which
-- bypasses RLS, but the policy must still exist for Supabase
-- to allow table creation via the dashboard.

ALTER TABLE asset_library ENABLE ROW LEVEL SECURITY;

-- Service role can do everything (n8n pipeline uses service_role key)
CREATE POLICY "service_role_all" ON asset_library
  FOR ALL
  USING (true)
  WITH CHECK (true);
```

### TypeScript Row Type

```typescript
// src/cache/asset-library.types.ts

import type { SlotCacheCategory } from '../prompts/types';

/**
 * TypeScript representation of a row in the asset_library table.
 * Used by OBJ-054 (semantic caching middleware) for type-safe
 * database interactions.
 *
 * This type mirrors the SQL schema exactly. Fields are camelCase
 * per TypeScript convention; the Supabase client maps snake_case
 * columns to these names via a column alias or the raw snake_case
 * names can be used depending on the client configuration.
 */
export interface AssetLibraryRow {
  /** UUID primary key. Auto-generated on INSERT. */
  readonly id: string;

  /**
   * Canonical slot category from OBJ-051's SlotCacheCategory.
   * Used as the primary filter dimension for similarity queries.
   * NOT the raw geometry slot name — multiple geometry-specific
   * slots map to the same category (e.g., tunnel.left_wall and
   * canyon.left_wall both → 'wall').
   */
  readonly slot_type: SlotCacheCategory;

  /** The exact prompt used to generate this image. */
  readonly original_prompt: string;

  /**
   * Vector embedding of original_prompt.
   * Represented as number[] in TypeScript (pgvector returns
   * arrays via the Supabase JS client).
   * Dimension: 1536 (text-embedding-3-small).
   */
  readonly prompt_embedding: number[];

  /** R2/S3 URL to the cached PNG image. */
  readonly image_url: string;

  /** Whether background removal was applied. */
  readonly has_alpha: boolean;

  /** Source image width in pixels. Nullable. */
  readonly width: number | null;

  /** Source image height in pixels. Nullable. */
  readonly height: number | null;

  /** Number of times this asset has been reused. Minimum 1. */
  readonly usage_count: number;

  /** Identifier of the embedding model used. */
  readonly embedding_model: string;

  /** Timestamp of initial creation. */
  readonly created_at: string; // ISO 8601

  /** Timestamp of most recent cache hit. */
  readonly last_used_at: string; // ISO 8601
}

/**
 * Fields required when inserting a new asset into the cache.
 * id, created_at, last_used_at, and usage_count have defaults.
 */
export interface AssetLibraryInsert {
  readonly slot_type: SlotCacheCategory;
  readonly original_prompt: string;
  readonly prompt_embedding: number[];
  readonly image_url: string;
  readonly has_alpha: boolean;
  readonly width?: number | null;
  readonly height?: number | null;
  readonly embedding_model?: string; // defaults to 'text-embedding-3-small'
}

/**
 * Fields returned by the similarity search query.
 * Extends the core row fields with computed similarity score.
 */
export interface AssetSimilarityResult {
  readonly id: string;
  readonly image_url: string;
  readonly original_prompt: string;
  readonly has_alpha: boolean;
  readonly width: number | null;
  readonly height: number | null;

  /**
   * Cosine similarity score: 1 - (prompt_embedding <=> query_embedding).
   * Range [0, 1] where 1 = identical, 0 = orthogonal.
   * The threshold gate (OBJ-054) compares this against 0.92.
   */
  readonly similarity: number;
}
```

### Documented Query Patterns

These are the SQL query patterns that OBJ-054 will use. They are documented here as part of the schema contract — the schema is designed to support these queries efficiently.

```sql
-- =============================================================
-- QUERY 1: Similarity search (the threshold gate query)
-- Used by OBJ-054 on every image request before generation.
-- =============================================================
-- Parameters:
--   $1: VECTOR(1536) — the embedded prompt
--   $2: TEXT          — the slot_type (SlotCacheCategory value)
--   $3: TEXT          — the embedding_model (must match $1's model)
--
-- Returns: 0 or 1 rows. The caller applies the threshold gate
--   (similarity > 0.92 → cache hit) in application code.
--
-- Performance: The WHERE on slot_type + embedding_model narrows
--   the search space before the vector scan. IVFFlat index on
--   prompt_embedding accelerates the nearest-neighbor lookup.
--   Expected latency: <100ms for tables up to 100k rows.

SELECT
  id,
  image_url,
  original_prompt,
  has_alpha,
  width,
  height,
  1 - (prompt_embedding <=> $1) AS similarity
FROM asset_library
WHERE slot_type = $2
  AND embedding_model = $3
ORDER BY prompt_embedding <=> $1
LIMIT 1;


-- =============================================================
-- QUERY 2: Cache hit — update usage stats
-- Called by OBJ-054 when similarity > threshold (cache hit).
-- =============================================================
-- Parameters:
--   $1: UUID — the matched row's id

UPDATE asset_library
SET
  usage_count = usage_count + 1,
  last_used_at = now()
WHERE id = $1;


-- =============================================================
-- QUERY 3: Cache miss — insert new asset
-- Called by OBJ-054 after generating and uploading a new image.
-- =============================================================
-- Parameters:
--   $1: TEXT          — slot_type
--   $2: TEXT          — original_prompt
--   $3: VECTOR(1536) — prompt_embedding
--   $4: TEXT          — image_url
--   $5: BOOLEAN       — has_alpha
--   $6: INT (nullable) — width
--   $7: INT (nullable) — height
--   $8: TEXT          — embedding_model

INSERT INTO asset_library (
  slot_type, original_prompt, prompt_embedding,
  image_url, has_alpha, width, height, embedding_model
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING id;


-- =============================================================
-- QUERY 4: Cache analytics — hit rate estimation
-- Used for monitoring and threshold tuning (TC-19).
-- =============================================================

SELECT
  slot_type,
  COUNT(*) AS total_assets,
  AVG(usage_count) AS avg_reuse,
  SUM(usage_count) - COUNT(*) AS total_cache_hits
FROM asset_library
GROUP BY slot_type
ORDER BY slot_type;


-- =============================================================
-- QUERY 5: Cache eviction — remove least-recently-used assets
-- Optional maintenance query. Not part of the hot path.
-- =============================================================
-- Parameters:
--   $1: INTERVAL — age threshold (e.g., '90 days')
--   $2: INT      — minimum usage_count to protect from eviction

DELETE FROM asset_library
WHERE last_used_at < now() - $1
  AND usage_count < $2
RETURNING id, image_url;
-- Caller must also delete the image from R2/S3 using returned image_url.
```

### Supabase RPC Function (Optional Performance Optimization)

```sql
-- =============================================================
-- RPC function wrapping the similarity search for use via
-- Supabase's .rpc() client method. This avoids sending the
-- raw vector over the REST API query string.
-- =============================================================

CREATE OR REPLACE FUNCTION match_asset(
  query_embedding VECTOR(1536),
  query_slot_type TEXT,
  query_embedding_model TEXT DEFAULT 'text-embedding-3-small',
  match_count INT DEFAULT 1
)
RETURNS TABLE (
  id UUID,
  image_url TEXT,
  original_prompt TEXT,
  has_alpha BOOLEAN,
  width INT,
  height INT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    a.id,
    a.image_url,
    a.original_prompt,
    a.has_alpha,
    a.width,
    a.height,
    (1 - (a.prompt_embedding <=> query_embedding))::FLOAT AS similarity
  FROM asset_library a
  WHERE a.slot_type = query_slot_type
    AND a.embedding_model = query_embedding_model
  ORDER BY a.prompt_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### R2/S3 Storage Convention

```typescript
// src/cache/storage.types.ts

/**
 * R2/S3 storage path convention for cached image assets.
 *
 * Bucket: configurable, default 'depthkit-assets'
 *
 * Object key pattern:
 *   assets/{slot_type}/{id}.png
 *
 * Examples:
 *   assets/sky/a1b2c3d4-e5f6-7890-abcd-ef1234567890.png
 *   assets/subject/f9e8d7c6-b5a4-3210-fedc-ba9876543210.png
 *
 * Rationale:
 * - slot_type prefix enables per-category lifecycle policies
 *   (e.g., 'sky' assets with longer TTL since they're more reusable).
 * - UUID filename prevents collisions and aligns with the DB primary key.
 * - .png extension is always used (all cached images are PNG, with
 *   or without alpha, for consistent texture loading in Three.js).
 *
 * The full URL stored in asset_library.image_url is constructed as:
 *   {R2_PUBLIC_URL}/{bucket}/{key}
 * e.g.:
 *   https://pub-xyz.r2.dev/depthkit-assets/assets/sky/a1b2c3d4-....png
 *
 * The pipeline must have R2_PUBLIC_URL, R2_ACCESS_KEY_ID,
 * R2_SECRET_ACCESS_KEY, and R2_BUCKET_NAME configured as
 * environment variables.
 */
export interface StorageConfig {
  /** R2/S3 public base URL. */
  readonly publicUrl: string;

  /** Bucket name. Default: 'depthkit-assets'. */
  readonly bucketName: string;
}

/**
 * Constructs the R2/S3 object key for a cached asset.
 *
 * @param slotType - The SlotCacheCategory value.
 * @param assetId - The UUID from asset_library.id.
 * @returns Object key string, e.g., 'assets/sky/uuid.png'
 */
export function buildAssetKey(slotType: string, assetId: string): string;

/**
 * Constructs the full public URL for a cached asset.
 *
 * @param config - Storage configuration.
 * @param slotType - The SlotCacheCategory value.
 * @param assetId - The UUID from asset_library.id.
 * @returns Full URL string.
 */
export function buildAssetUrl(
  config: StorageConfig,
  slotType: string,
  assetId: string
): string;
```

### Module Exports

```typescript
// src/cache/index.ts (barrel export)

export type {
  AssetLibraryRow,
  AssetLibraryInsert,
  AssetSimilarityResult,
} from './asset-library.types';

export type { StorageConfig } from './storage.types';

export { buildAssetKey, buildAssetUrl } from './storage.types';
```

## Design Decisions

### D1: `slot_type` uses `SlotCacheCategory` (from OBJ-051), not raw geometry slot names

The seed's schema sketch (Section 4.10) uses `slot_type TEXT` with examples like `'sky'`, `'subject'`, `'floor'`, `'left_wall'`. OBJ-051 refined this by defining a `SlotCacheCategory` union type that maps multiple geometry-specific slot names to canonical categories (e.g., tunnel's `left_wall` and canyon's `left_wall` both map to `'wall'`). This enables cross-geometry cache reuse — a wall texture generated for a tunnel can be a cache hit for a canyon query.

The column is `TEXT NOT NULL` rather than a PostgreSQL `ENUM` because `SlotCacheCategory` is explicitly additive-only (OBJ-051: "Adding a category is a non-breaking change"). TEXT avoids ALTER TYPE migrations when new geometries introduce new categories.

**Constraint alignment:** Seed Section 4.10 ("queried by cosine similarity... filtered by slot_type"). TC-18 (slot-type filtering prevents cross-category contamination).

### D2: `embedding_model` column added beyond the seed sketch

The seed's schema (Section 4.10) does not include an `embedding_model` column. This addition is necessary because:
- If the embedding model is ever changed (e.g., upgrading from `text-embedding-3-small` to `text-embedding-3-large`), existing embeddings become incomparable — different models produce different vector spaces.
- The column enables safe mixed-model queries: filter by `embedding_model` to only compare embeddings from the same model.
- Enables a migration path: re-embed old entries without downtime, then swap the query filter.

**Trade-off:** One extra column and filter per query. Cost is negligible. Prevents a subtle, hard-to-debug accuracy degradation if models are switched.

### D3: IVFFlat index with lists=100, not HNSW

The seed specifies IVFFlat (Section 4.10). HNSW is the newer alternative in pgvector with better recall at the cost of higher memory usage and slower inserts. IVFFlat is the correct choice for this use case because:
- The expected table size is modest (thousands to low tens-of-thousands of rows over the first year).
- Insert speed matters — every cache miss writes a new row in the hot path.
- IVFFlat with `lists=100` provides adequate recall for top-1 queries on this scale.
- HNSW can be swapped in later if scale demands it — the query patterns are identical.

**Note on cold start:** IVFFlat requires training data. On an empty or very small table (<~1000 rows), pgvector performs a sequential scan instead, which is acceptable for cold-start. The index becomes effective as the table populates. This is not a bug — it's expected IVFFlat behavior.

### D4: Vector dimension 1536 matches `text-embedding-3-small`

The seed specifies `VECTOR(1536)` (Section 4.10). This matches OpenAI's `text-embedding-3-small` model, which is the recommended starting point due to its balance of quality, speed, and cost ($0.00002/1K tokens). The `embedding_model` column (D2) provides a migration path to other models/dimensions.

If a model with a different dimension is needed, the column type must be altered (`ALTER TABLE asset_library ALTER COLUMN prompt_embedding TYPE VECTOR(new_dim)`), and all existing rows re-embedded. This is a deliberate one-way door — documented, not prevented.

### D5: `width` and `height` are nullable

Image dimensions are useful for sizing validation (ensuring an image generated for a floor slot has appropriate aspect ratio) but may not always be available at insert time (e.g., if the image generation API returns only a URL and the pipeline doesn't inspect the image before caching). Making them nullable avoids blocking inserts.

### D6: Row-Level Security (RLS) with permissive policy

Supabase requires RLS to be enabled for REST API access. The depthkit pipeline uses the `service_role` key (which bypasses RLS), so the policy is permissive. If the pipeline is later exposed to client-side access (e.g., a dashboard showing cache analytics), more restrictive policies can be added without changing the schema.

### D7: R2/S3 key structure uses `slot_type` prefix and UUID filename

The `assets/{slot_type}/{uuid}.png` pattern:
- Enables per-category R2 lifecycle rules (e.g., `sky/` assets might have a 1-year TTL while `subject/` assets have 90 days).
- UUID filenames align with the DB primary key, making orphan cleanup trivial (`SELECT id FROM asset_library` vs `LIST objects in R2` → diff).
- `.png` is always used because Three.js's `TextureLoader` handles PNG consistently across alpha and non-alpha images.

### D8: Supabase RPC function for similarity search

Passing a 1536-dimensional vector through the Supabase REST API query string is awkward and may hit URL length limits. The `match_asset` RPC function wraps the similarity query so OBJ-054 can call `supabase.rpc('match_asset', { ... })` with the vector in the request body. This is a performance and ergonomics choice, not strictly required.

### D9: Cache eviction is documented but not mandated for V1

Query 5 (LRU eviction) is provided as a maintenance pattern. For V1, the expected table size (thousands of rows) does not require automatic eviction. The query is documented so that a cron job or manual process can be added later. OBJ-054 does not need to implement eviction logic — it only needs INSERT and SELECT.

### D10: No uniqueness constraint on (slot_type, original_prompt)

Two different generation calls with the exact same prompt could produce visually different images (non-deterministic generation). Both are valid cache entries. A uniqueness constraint would block legitimate re-generation (e.g., if the first result was poor and the pipeline retries). Deduplication, if desired, is an application-level concern in OBJ-054, not a schema constraint.

## Acceptance Criteria

- [ ] **AC-01:** The SQL DDL creates the `asset_library` table with all columns specified: `id` (UUID PK), `slot_type` (TEXT NOT NULL), `original_prompt` (TEXT NOT NULL), `prompt_embedding` (VECTOR(1536) NOT NULL), `image_url` (TEXT NOT NULL), `has_alpha` (BOOLEAN NOT NULL DEFAULT false), `width` (INT nullable), `height` (INT nullable), `usage_count` (INT NOT NULL DEFAULT 1), `embedding_model` (TEXT NOT NULL DEFAULT 'text-embedding-3-small'), `created_at` (TIMESTAMPTZ NOT NULL DEFAULT now()), `last_used_at` (TIMESTAMPTZ NOT NULL DEFAULT now()).
- [ ] **AC-02:** CHECK constraints enforce: `slot_type` length 1–50, `original_prompt` length 1–2000, `image_url` length 1–2048, `width > 0` (when not null), `height > 0` (when not null), `usage_count >= 1`, `embedding_model` length 1–100.
- [ ] **AC-03:** An IVFFlat index exists on `prompt_embedding` using `vector_cosine_ops` with `lists = 100`.
- [ ] **AC-04:** A btree index exists on `slot_type`.
- [ ] **AC-05:** A composite btree index exists on `(slot_type, embedding_model)`.
- [ ] **AC-06:** A btree index exists on `last_used_at`.
- [ ] **AC-07:** Row-Level Security is enabled on the table with a permissive policy for all operations.
- [ ] **AC-08:** The `match_asset` RPC function accepts parameters `(query_embedding VECTOR(1536), query_slot_type TEXT, query_embedding_model TEXT, match_count INT)` and returns rows with columns `(id, image_url, original_prompt, has_alpha, width, height, similarity)`.
- [ ] **AC-09:** The similarity search query (Query 1) filters by both `slot_type` and `embedding_model`, orders by cosine distance ascending, and limits to 1 row.
- [ ] **AC-10:** The similarity score is computed as `1 - (prompt_embedding <=> query_embedding)`, yielding a value in [0, 1] where 1 = identical.
- [ ] **AC-11:** The cache-hit update query (Query 2) increments `usage_count` by 1 and sets `last_used_at` to `now()`.
- [ ] **AC-12:** The cache-miss insert query (Query 3) returns the generated `id` via `RETURNING id`.
- [ ] **AC-13:** The `AssetLibraryRow` TypeScript type has fields matching all SQL columns, with `slot_type` typed as `SlotCacheCategory` (imported from OBJ-051's `src/prompts/types.ts`).
- [ ] **AC-14:** The `AssetLibraryInsert` type includes only non-defaulted required fields, with optional fields for columns that have SQL defaults.
- [ ] **AC-15:** The `AssetSimilarityResult` type includes `similarity: number` alongside the row fields needed by OBJ-054's threshold gate logic.
- [ ] **AC-16:** `buildAssetKey('sky', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')` returns `'assets/sky/a1b2c3d4-e5f6-7890-abcd-ef1234567890.png'`.
- [ ] **AC-17:** `buildAssetUrl({ publicUrl: 'https://pub.r2.dev', bucketName: 'depthkit-assets' }, 'subject', 'abc-123')` returns `'https://pub.r2.dev/depthkit-assets/assets/subject/abc-123.png'`.
- [ ] **AC-18:** All `.png` extension is hardcoded — the storage convention produces PNG URLs exclusively.
- [ ] **AC-19:** The DDL includes `CREATE EXTENSION IF NOT EXISTS vector;` before the table creation.
- [ ] **AC-20:** The eviction query (Query 5) returns `id` and `image_url` of deleted rows so the caller can clean up R2/S3 objects.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| INSERT with `prompt_embedding` of wrong dimension (e.g., 768-d vector into 1536-d column) | PostgreSQL/pgvector rejects the INSERT with a dimension mismatch error. OBJ-054 must catch this and report a clear error naming the expected vs. actual dimension. |
| INSERT with empty `slot_type` (`''`) | CHECK constraint violation. Rejected at DB level. |
| INSERT with `original_prompt` exceeding 2000 chars | CHECK constraint violation. OBJ-054 should truncate or reject before sending to DB. |
| INSERT with `width: 0` or `width: -1` | CHECK constraint violation (`width > 0`). |
| INSERT with `width: null` | Allowed (nullable column). |
| Similarity query on an empty table | Returns 0 rows. OBJ-054 treats this as a cache miss. |
| Similarity query with a `slot_type` that has no entries | Returns 0 rows. Cache miss. |
| Similarity query with `slot_type` value not in `SlotCacheCategory` | Query executes normally (TEXT column, no enum). Returns 0 rows since no entries match. OBJ-054 should validate `slot_type` against `SlotCacheCategory` before querying. |
| Concurrent INSERTs with the same prompt | Both succeed (no uniqueness constraint per D10). Results in two rows — acceptable. |
| IVFFlat index on table with <100 rows | pgvector falls back to sequential scan. Performance is fine for small tables. No error. |
| R2 image deleted but `asset_library` row still exists (orphan reference) | OBJ-054's cache-hit path should handle HTTP 404 from the image URL gracefully — treat as cache miss, optionally DELETE the orphan row, then generate fresh. |
| `embedding_model` mismatch between query and stored rows | The `WHERE embedding_model = $3` filter in the similarity query excludes rows from different models. Returns 0 rows if no rows match the current model — treated as cache miss. This is correct: cross-model similarity is meaningless. |
| Very long image_url (>2048 chars) | CHECK constraint violation. R2/S3 URLs are typically <200 chars, so this is a safety rail against data corruption, not a realistic scenario. |

## Test Strategy

### Schema Validation Tests (against a test Supabase instance or local PostgreSQL + pgvector)

1. **Table creation**: DDL executes without errors on a fresh database with pgvector enabled.
2. **Column types**: Introspect `information_schema.columns` to verify each column's type, nullability, and defaults match the spec.
3. **CHECK constraints**: Attempt INSERTs with boundary values (empty strings, null where not allowed, zero/negative dimensions, `usage_count: 0`) and verify rejection.
4. **Index existence**: Query `pg_indexes` to verify all 4 indexes exist with correct methods (ivfflat, btree).
5. **RLS**: Verify `pg_tables.rowsecurity` is `true` for `asset_library`.
6. **RPC function**: Call `match_asset` with a known embedding and verify correct return shape.

### Similarity Query Tests

7. **Basic insertion and retrieval**: Insert an asset, query with the same embedding, verify `similarity ≈ 1.0`.
8. **Slot-type filtering**: Insert assets in different slot_types with similar embeddings. Query for one slot_type and verify only matching slot_type rows are returned. (TC-18)
9. **Embedding model filtering**: Insert two rows with the same prompt but different `embedding_model` values. Query with one model and verify only that model's row is returned.
10. **Cache hit update**: After a cache hit, verify `usage_count` incremented and `last_used_at` updated.
11. **Eviction query**: Insert old rows (manually set `last_used_at` to past), run eviction query, verify correct rows deleted and returned.

### TypeScript Type Tests

12. **AssetLibraryInsert** accepts a minimal valid insert (required fields only).
13. **AssetLibraryInsert** rejects missing required fields at compile time.
14. **AssetSimilarityResult** includes `similarity` field of type `number`.

### Storage Convention Tests

15. `buildAssetKey` produces correct path format.
16. `buildAssetUrl` concatenates config + key correctly.
17. `buildAssetKey` with special characters in slot_type (though `SlotCacheCategory` values are all safe ASCII, defensive test).

### Relevant Testable Claims

- **TC-17** (threshold acceptance): This schema provides the data model; OBJ-054 implements the threshold gate. The schema must support Query 1 returning a similarity score for OBJ-054 to evaluate.
- **TC-18** (slot-type filtering prevents contamination): Validated by test #8 — the WHERE clause on `slot_type` prevents cross-category results.
- **TC-19** (cache hit rates 30-60%): The analytics query (Query 4) enables measuring this. OBJ-054 uses it for reporting.
- **TC-20** (query latency negligible): The IVFFlat index + slot_type btree index support the <500ms target. Benchmark test #7 against a populated table.

## Integration Points

### Depends on

| Upstream | What OBJ-053 imports |
|---|---|
| **OBJ-007** (Depth model / slot taxonomy) | Indirect dependency via OBJ-051. OBJ-007 defines slot names per geometry; OBJ-051 maps them to `SlotCacheCategory`. OBJ-053 uses `SlotCacheCategory` as the type for `slot_type`. |
| **OBJ-051** (Prompt engineering / slot prompt registry) | `SlotCacheCategory` type — the union of canonical categories used in `asset_library.slot_type`. `getCacheCategory()` function — used by OBJ-054 to resolve a (geometry, slot) pair to the cache category for queries. |

### Consumed by

| Downstream | How it uses OBJ-053 |
|---|---|
| **OBJ-054** (Semantic caching middleware) | Uses the SQL schema as its data store. Imports `AssetLibraryRow`, `AssetLibraryInsert`, `AssetSimilarityResult` types. Calls `match_asset` RPC for similarity search. Uses `buildAssetKey`/`buildAssetUrl` for R2 storage paths. Implements the threshold gate logic (> 0.92 → hit, ≤ 0.92 → miss) against the `similarity` value returned by Query 1. |
| **OBJ-076** (Cache analytics / monitoring) | Uses Query 4 for hit-rate estimation and per-slot-type usage statistics. |

### File Placement

```
depthkit/
  src/
    cache/
      index.ts                    # Barrel export
      asset-library.types.ts      # AssetLibraryRow, AssetLibraryInsert,
                                  #   AssetSimilarityResult
      storage.types.ts            # StorageConfig, buildAssetKey, buildAssetUrl
  sql/
    001_create_asset_library.sql  # DDL: table, indexes, RLS, extension
    002_create_match_asset.sql    # RPC function
  docs/
    asset-cache-queries.md        # Documented query patterns for OBJ-054 reference
```

## Open Questions

1. **Should the threshold (0.92) be stored in the database as a configurable parameter?** The seed hardcodes 0.92 but notes it should be tuned. A `cache_config` table or a simple key-value row could make this runtime-configurable. **Recommendation:** No — keep it as an application-level constant in OBJ-054. A DB round-trip to read config on every cache query is unnecessary overhead. Environment variable or code constant is simpler.

2. **Should duplicate detection be added (same prompt + same slot_type)?** Per D10, no uniqueness constraint. But OBJ-054 could check for exact prompt matches before embedding + similarity search, as a fast path. **Recommendation:** Defer to OBJ-054. The schema should not enforce uniqueness, but OBJ-054 could implement an exact-match fast path as an optimization.

3. **Should there be a `style` or `theme` column for filtering cache queries by visual style?** E.g., "watercolor" vs "photorealistic" images in the same slot category. **Recommendation:** Not for V1. The embedding space should capture style differences — "watercolor sunset sky" and "photorealistic sunset sky" will have different embeddings. If style-based filtering is needed later, a `style` column can be added without migration (just nullable TEXT).

4. **What happens when the IVFFlat index needs rebuilding after significant data changes?** pgvector IVFFlat indexes are not automatically maintained when the data distribution shifts significantly. A `REINDEX INDEX idx_asset_embedding;` may be needed periodically. **Recommendation:** Document this as an operational note. Not a V1 automation concern.

---

I believe this specification is comprehensive. It covers the DDL, TypeScript types, query patterns, storage convention, and all the edge cases relevant to the schema layer. I've drawn the boundary clearly: OBJ-053 defines the data model and storage convention; OBJ-054 implements the middleware logic that uses it.

I'd like the Challenger to review and verify. Key areas I'd especially appreciate scrutiny on:

1. The `embedding_model` column addition (not in the seed sketch) — is this justified?
2. The RPC function — is it overreach for a schema-only objective?
3. The `buildAssetKey`/`buildAssetUrl` functions — should they be here or in OBJ-054?
4. Completeness of the edge case table against TC-17 through TC-20.

---

## Round 2 — spec_challenger

I'll review the proposed spec carefully against my checklist.

---

## Challenger Review — Round 1

### Points of Agreement (Sound Elements)

1. **SQL DDL quality is high.** CHECK constraints, nullable strategy, index choices — all well-reasoned. The IVFFlat vs HNSW decision (D3) is correctly justified for the expected scale.
2. **Design decisions D1, D4, D5, D9, D10 are solid** and well-aligned with the seed. Particularly D10 (no uniqueness constraint) — good call, correctly reasoned.
3. **Edge case table is thorough.** The orphan reference case (R2 deleted but row exists), IVFFlat cold-start, embedding model mismatch — these are the kinds of things an implementer would otherwise have to guess about.
4. **The `embedding_model` column addition (D2) is justified.** Model migration is a real concern. This is a low-cost insurance column. Approved.
5. **Query patterns as part of the schema contract** — agreed, this is the right place to document them since the schema is *designed to support* these patterns.

---

### Issues

#### Issue 1 — CRITICAL: Undeclared dependency on OBJ-051 breaks the dependency graph

**Problem:** OBJ-053's `meta.json` declares `depends_on: ["OBJ-007"]`. But the spec imports `SlotCacheCategory` from OBJ-051 (`src/prompts/types.ts`) and the TypeScript type `AssetLibraryRow.slot_type` is typed as `SlotCacheCategory`. This creates a compile-time dependency on OBJ-051 that isn't in the declared dependency graph.

The progress map shows OBJ-054 depends on both OBJ-053 *and* OBJ-051. That's the correct place for the type narrowing to happen — OBJ-054 sees both.

**Why this matters:** An implementer building OBJ-053 from the meta.json would not know to consult OBJ-051. The progress map wouldn't track the blocking relationship. If OBJ-051 were reverted or changed, OBJ-053 would break silently.

**Proposed fix:** Two options (I recommend Option A):

**Option A (preferred):** Remove the OBJ-051 type dependency from OBJ-053. The SQL schema already uses `TEXT` — that's correct. Change the TypeScript types to use `string` for `slot_type`:
```typescript
readonly slot_type: string; // Valid values defined by OBJ-051's SlotCacheCategory
```
Add a doc comment noting the valid values come from OBJ-051. OBJ-054 (which depends on both) performs the type narrowing. This keeps OBJ-053's dependency graph clean.

**Option B:** Add OBJ-051 to `depends_on` in both the meta.json and the index.json. This is a graph change that needs orchestrator approval.

#### Issue 2 — MAJOR: `buildAssetKey` and `buildAssetUrl` are implementation functions, not schema

**Problem:** The objective description in meta.json says: *"Database schema only — middleware logic is OBJ-054."* The `buildAssetKey` and `buildAssetUrl` functions are utility functions for constructing R2 paths. They're consumed by middleware logic (uploading and resolving cached images) — that's OBJ-054's territory.

The **storage convention** (the path pattern `assets/{slot_type}/{id}.png`) absolutely belongs in OBJ-053 as a documented convention. But the functions that implement it belong in OBJ-054 or a shared utility.

**Proposed fix:** 
- Keep `StorageConfig` type and the **documented convention** (the path pattern, rationale, environment variables) in OBJ-053.
- Remove `buildAssetKey` and `buildAssetUrl` function signatures. Document the path pattern as a prose convention + examples.
- Remove `storage.types.ts` as a code file. The convention goes in the spec text and in `docs/asset-cache-queries.md`.
- Update the barrel export to remove the function exports.
- If you feel strongly that these functions need a home, put them in a "Recommendations for OBJ-054" section, not in OBJ-053's interface contract.

#### Issue 3 — MAJOR: `AssetSimilarityResult` and `AssetLibraryInsert` straddle the schema/middleware boundary

**Problem:** `AssetLibraryRow` mirrors the SQL schema — clear OBJ-053 territory. But `AssetLibraryInsert` (which fields to provide on insert) and `AssetSimilarityResult` (a query-shaped projection with computed `similarity`) are consumption patterns that OBJ-054 will use. They encode assumptions about *how* the schema is queried, not *what* the schema is.

This isn't as clear-cut as Issue 2 — there's a reasonable argument that providing "row type + insert type + query result type" as a package ensures the schema contract is complete. But the insert/query types could change independently of the schema if OBJ-054 decides to query differently.

**Proposed fix:** Keep all three types but **explicitly label them** in the spec. Add a note to `AssetLibraryInsert` and `AssetSimilarityResult` that they are **recommended consumption types** for OBJ-054, not schema-level contracts. If OBJ-054 needs different projections, it can define its own types. This way the types serve as guidance without creating a rigid coupling.

Alternatively, move them into a `// Recommended types for OBJ-054 consumption` section rather than mixing them with the schema-level `AssetLibraryRow`.

#### Issue 4 — MINOR: AC-16 and AC-17 test functions that shouldn't exist in this objective (per Issue 2)

**Problem:** If `buildAssetKey` and `buildAssetUrl` are removed per Issue 2, AC-16 and AC-17 become orphans. They test functions that don't belong here.

**Proposed fix:** Replace AC-16/AC-17 with acceptance criteria that validate the **documented storage convention** — e.g., "AC-16: The storage convention specifies the object key pattern `assets/{slot_type}/{id}.png` with examples for at least two slot types." This tests documentation completeness, not function output.

#### Issue 5 — MINOR: The `match_asset` RPC function is a reasonable addition but should be explicitly marked as optional

**Problem:** The RPC function is an optimization (D8 says "not strictly required"). But the DDL file `002_create_match_asset.sql` and AC-08 make it look mandatory. An implementer might waste time ensuring this function exists in all environments, even if OBJ-054 could use the raw SQL query instead.

**Proposed fix:** In AC-08, change to: "AC-08: If the `match_asset` RPC function is deployed, it accepts parameters `(...)` and returns rows with columns `(...)`. The function is optional — OBJ-054 may use either the RPC function or the equivalent raw SQL query (Query 1)."

#### Issue 6 — MINOR: `created_at` and `last_used_at` typed as `string` needs justification

**Problem:** The TypeScript types use `string` (ISO 8601) for timestamp fields. This is pragmatically correct (Supabase JS client returns dates as strings) but undocumented. An implementer might try to use `Date` and be surprised.

**Proposed fix:** Add a one-line comment: `// Supabase JS client returns TIMESTAMPTZ as ISO 8601 strings`. 

#### Issue 7 — MINOR: No documented migration path for vector dimension changes

**Problem:** D4 mentions that changing embedding models requires `ALTER TABLE ... ALTER COLUMN prompt_embedding TYPE VECTOR(new_dim)` and re-embedding. But this isn't in the edge cases table or operational notes. An implementer might not realize dimension changes require a migration + full re-embedding.

**Proposed fix:** Add to edge cases table: "Embedding model change requiring different vector dimension → Requires `ALTER TABLE` migration + re-embedding all existing rows. This is a destructive operation; plan for downtime or shadow-table migration. The `embedding_model` column (D2) allows mixed-model coexistence during transition."

---

### Summary of Required Changes

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| 1 | CRITICAL | Undeclared dependency on OBJ-051 | Needs fix |
| 2 | MAJOR | `buildAssetKey`/`buildAssetUrl` functions exceed schema scope | Needs fix |
| 3 | MAJOR | Insert/query types should be labeled as consumption guidance | Needs fix |
| 4 | MINOR | AC-16/AC-17 orphaned if functions removed | Needs fix |
| 5 | MINOR | RPC function should be marked optional | Needs fix |
| 6 | MINOR | Timestamp string type needs justification comment | Needs fix |
| 7 | MINOR | Missing migration path for dimension changes | Needs fix |

I need Issues 1, 2, and 3 addressed before I'll converge. The minors (4-7) I'd prefer addressed but could accept as open questions if the author disagrees.

---

## Round 3 — spec_author

All seven issues are valid. I'll address each and present the revised spec.

---

# Revised Specification: OBJ-053 — Semantic Caching Database Schema

## Summary

OBJ-053 defines the **AssetLibrary database schema** for Supabase (PostgreSQL + pgvector) that powers depthkit's semantic image caching layer. It specifies the table structure, column definitions, indexes, constraints, the R2/S3 storage convention for cached images, and the documented query patterns that OBJ-054 (the middleware logic) will use. This is a schema-only objective — it produces SQL DDL, a TypeScript row type mirroring the table, recommended consumption types for OBJ-054, and documented query patterns. It does not implement the middleware, embedding logic, or threshold gate (those are OBJ-054).

## Interface Contract

### Database Schema (SQL DDL)

```sql
-- =============================================================
-- AssetLibrary table — semantic cache for generated image assets
-- Requires: pgvector extension enabled in Supabase project
-- File: sql/001_create_asset_library.sql
-- =============================================================

-- Ensure pgvector is available
CREATE EXTENSION IF NOT EXISTS vector;

-- Core table
CREATE TABLE asset_library (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Canonical slot category (not raw geometry slot name).
  -- Valid values are defined by OBJ-051's SlotCacheCategory union:
  -- 'sky' | 'backdrop' | 'floor' | 'ceiling' | 'wall' |
  -- 'midground' | 'subject' | 'foreground' | 'landmark'
  -- TEXT (not ENUM) to allow additive expansion without migrations.
  slot_type       TEXT NOT NULL
                  CHECK (char_length(slot_type) > 0 AND char_length(slot_type) <= 50),

  -- The exact prompt used to generate this image.
  original_prompt TEXT NOT NULL
                  CHECK (char_length(original_prompt) > 0 AND char_length(original_prompt) <= 2000),

  -- Embedding of original_prompt. Dimension 1536 matches
  -- OpenAI text-embedding-3-small. If a different embedding model
  -- is used, the dimension must match. The column dimension is
  -- enforced by pgvector at INSERT time.
  prompt_embedding VECTOR(1536) NOT NULL,

  -- URL to the cached image in R2/S3.
  image_url       TEXT NOT NULL
                  CHECK (char_length(image_url) > 0 AND char_length(image_url) <= 2048),

  -- Whether background removal was applied (rembg or equivalent).
  has_alpha       BOOLEAN NOT NULL DEFAULT false,

  -- Source image dimensions for sizing validation.
  -- Nullable: may not always be known at insert time.
  width           INT CHECK (width IS NULL OR width > 0),
  height          INT CHECK (height IS NULL OR height > 0),

  -- Tracks reuse frequency for analytics and cache eviction heuristics.
  usage_count     INT NOT NULL DEFAULT 1
                  CHECK (usage_count >= 1),

  -- The embedding model identifier used to generate prompt_embedding.
  -- Enables safe re-embedding or mixed-model queries during migration.
  embedding_model TEXT NOT NULL DEFAULT 'text-embedding-3-small'
                  CHECK (char_length(embedding_model) > 0 AND char_length(embedding_model) <= 100),

  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_used_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================
-- Indexes
-- ============================

-- Primary similarity search index: IVFFlat on prompt_embedding
-- using cosine distance. lists=100 is appropriate for up to ~100k rows;
-- should be increased if the table grows significantly.
--
-- NOTE: IVFFlat requires training data to build the index.
-- For an empty or small table (<1000 rows), pgvector falls back
-- to sequential scan, which is acceptable for cold-start.
CREATE INDEX idx_asset_embedding ON asset_library
  USING ivfflat (prompt_embedding vector_cosine_ops)
  WITH (lists = 100);

-- Btree index on slot_type for the WHERE filter in similarity queries.
CREATE INDEX idx_asset_slot_type ON asset_library (slot_type);

-- Composite index for the most common query pattern:
-- filter by slot_type + embedding_model, then vector search.
CREATE INDEX idx_asset_slot_model ON asset_library (slot_type, embedding_model);

-- Index on last_used_at for cache eviction queries (LRU).
CREATE INDEX idx_asset_last_used ON asset_library (last_used_at);

-- ============================
-- Row-Level Security (RLS)
-- ============================
-- Supabase requires RLS to be enabled for tables accessed via
-- the REST API. The pipeline uses the service_role key, which
-- bypasses RLS, but RLS must still be enabled.

ALTER TABLE asset_library ENABLE ROW LEVEL SECURITY;

-- Service role can do everything (n8n pipeline uses service_role key)
CREATE POLICY "service_role_all" ON asset_library
  FOR ALL
  USING (true)
  WITH CHECK (true);
```

### Optional RPC Function

```sql
-- =============================================================
-- Optional RPC function wrapping the similarity search.
-- File: sql/002_create_match_asset.sql
--
-- This function is OPTIONAL. OBJ-054 may use either this RPC
-- function (via supabase.rpc('match_asset', {...})) or the
-- equivalent raw SQL query (Query 1 below). The RPC function
-- avoids sending a 1536-dimensional vector through the REST API
-- query string.
-- =============================================================

CREATE OR REPLACE FUNCTION match_asset(
  query_embedding VECTOR(1536),
  query_slot_type TEXT,
  query_embedding_model TEXT DEFAULT 'text-embedding-3-small',
  match_count INT DEFAULT 1
)
RETURNS TABLE (
  id UUID,
  image_url TEXT,
  original_prompt TEXT,
  has_alpha BOOLEAN,
  width INT,
  height INT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    a.id,
    a.image_url,
    a.original_prompt,
    a.has_alpha,
    a.width,
    a.height,
    (1 - (a.prompt_embedding <=> query_embedding))::FLOAT AS similarity
  FROM asset_library a
  WHERE a.slot_type = query_slot_type
    AND a.embedding_model = query_embedding_model
  ORDER BY a.prompt_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### TypeScript Row Type (Schema-Level Contract)

```typescript
// src/cache/asset-library.types.ts

/**
 * TypeScript representation of a row in the asset_library table.
 * This type mirrors the SQL schema exactly and is the authoritative
 * schema-level contract for OBJ-053.
 *
 * NOTE: slot_type is typed as `string`, not as OBJ-051's
 * SlotCacheCategory. OBJ-053 depends only on OBJ-007; the
 * type narrowing to SlotCacheCategory happens in OBJ-054,
 * which depends on both OBJ-053 and OBJ-051. Valid slot_type
 * values are documented in the SQL DDL comments.
 *
 * NOTE: Supabase JS client returns TIMESTAMPTZ columns as
 * ISO 8601 strings, not Date objects. The string type here
 * reflects the actual runtime representation.
 */
export interface AssetLibraryRow {
  /** UUID primary key. Auto-generated on INSERT. */
  readonly id: string;

  /**
   * Canonical slot category. Valid values are defined by
   * OBJ-051's SlotCacheCategory union type:
   * 'sky' | 'backdrop' | 'floor' | 'ceiling' | 'wall' |
   * 'midground' | 'subject' | 'foreground' | 'landmark'
   *
   * Typed as string here; OBJ-054 narrows to SlotCacheCategory.
   */
  readonly slot_type: string;

  /** The exact prompt used to generate this image. */
  readonly original_prompt: string;

  /**
   * Vector embedding of original_prompt.
   * Represented as number[] in TypeScript (pgvector returns
   * arrays via the Supabase JS client).
   * Dimension: 1536 (text-embedding-3-small).
   */
  readonly prompt_embedding: number[];

  /** R2/S3 URL to the cached PNG image. */
  readonly image_url: string;

  /** Whether background removal was applied. */
  readonly has_alpha: boolean;

  /** Source image width in pixels. Nullable. */
  readonly width: number | null;

  /** Source image height in pixels. Nullable. */
  readonly height: number | null;

  /** Number of times this asset has been reused. Minimum 1. */
  readonly usage_count: number;

  /** Identifier of the embedding model used. */
  readonly embedding_model: string;

  /** Timestamp of initial creation. ISO 8601 string. */
  readonly created_at: string;

  /** Timestamp of most recent cache hit. ISO 8601 string. */
  readonly last_used_at: string;
}
```

### Recommended Consumption Types for OBJ-054

These types encode recommended query and insert patterns. They are **guidance for OBJ-054**, not rigid schema-level contracts. OBJ-054 may define its own projections if its query patterns diverge.

```typescript
// src/cache/asset-library.types.ts (continued)

/**
 * RECOMMENDED CONSUMPTION TYPE — guidance for OBJ-054.
 *
 * Fields required when inserting a new asset into the cache.
 * id, created_at, last_used_at, and usage_count have SQL defaults.
 *
 * OBJ-054 may define its own insert type if its needs differ.
 */
export interface AssetLibraryInsert {
  readonly slot_type: string;
  readonly original_prompt: string;
  readonly prompt_embedding: number[];
  readonly image_url: string;
  readonly has_alpha: boolean;
  readonly width?: number | null;
  readonly height?: number | null;
  readonly embedding_model?: string; // defaults to 'text-embedding-3-small'
}

/**
 * RECOMMENDED CONSUMPTION TYPE — guidance for OBJ-054.
 *
 * Fields returned by the similarity search query (Query 1)
 * or the match_asset RPC function.
 *
 * OBJ-054 may define its own result type if its needs differ.
 */
export interface AssetSimilarityResult {
  readonly id: string;
  readonly image_url: string;
  readonly original_prompt: string;
  readonly has_alpha: boolean;
  readonly width: number | null;
  readonly height: number | null;

  /**
   * Cosine similarity score: 1 - (prompt_embedding <=> query_embedding).
   * Range [0, 1] where 1 = identical, 0 = orthogonal.
   * The threshold gate (OBJ-054) compares this against 0.92 (seed default).
   */
  readonly similarity: number;
}
```

### Module Exports

```typescript
// src/cache/index.ts (barrel export)

export type {
  AssetLibraryRow,
  AssetLibraryInsert,
  AssetSimilarityResult,
} from './asset-library.types';
```

### Documented Query Patterns

These are the SQL query patterns that OBJ-054 will use. They are documented here as part of the schema contract — the schema is designed to support these queries efficiently.

```sql
-- =============================================================
-- QUERY 1: Similarity search (the threshold gate query)
-- Used by OBJ-054 on every image request before generation.
-- =============================================================
-- Parameters:
--   $1: VECTOR(1536) — the embedded prompt
--   $2: TEXT          — the slot_type (SlotCacheCategory value)
--   $3: TEXT          — the embedding_model (must match $1's model)
--
-- Returns: 0 or 1 rows. The caller applies the threshold gate
--   (similarity > 0.92 → cache hit) in application code.

SELECT
  id,
  image_url,
  original_prompt,
  has_alpha,
  width,
  height,
  1 - (prompt_embedding <=> $1) AS similarity
FROM asset_library
WHERE slot_type = $2
  AND embedding_model = $3
ORDER BY prompt_embedding <=> $1
LIMIT 1;


-- =============================================================
-- QUERY 2: Cache hit — update usage stats
-- Called by OBJ-054 when similarity > threshold (cache hit).
-- =============================================================
-- Parameters:
--   $1: UUID — the matched row's id

UPDATE asset_library
SET
  usage_count = usage_count + 1,
  last_used_at = now()
WHERE id = $1;


-- =============================================================
-- QUERY 3: Cache miss — insert new asset
-- Called by OBJ-054 after generating and uploading a new image.
-- =============================================================
-- Parameters:
--   $1: TEXT          — slot_type
--   $2: TEXT          — original_prompt
--   $3: VECTOR(1536) — prompt_embedding
--   $4: TEXT          — image_url
--   $5: BOOLEAN       — has_alpha
--   $6: INT (nullable) — width
--   $7: INT (nullable) — height
--   $8: TEXT          — embedding_model

INSERT INTO asset_library (
  slot_type, original_prompt, prompt_embedding,
  image_url, has_alpha, width, height, embedding_model
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING id;


-- =============================================================
-- QUERY 4: Cache analytics — hit rate estimation
-- Used for monitoring and threshold tuning (TC-19).
-- =============================================================

SELECT
  slot_type,
  COUNT(*) AS total_assets,
  AVG(usage_count) AS avg_reuse,
  SUM(usage_count) - COUNT(*) AS total_cache_hits
FROM asset_library
GROUP BY slot_type
ORDER BY slot_type;


-- =============================================================
-- QUERY 5: Cache eviction — remove least-recently-used assets
-- Optional maintenance query. Not part of the hot path.
-- Not required for V1.
-- =============================================================
-- Parameters:
--   $1: INTERVAL — age threshold (e.g., '90 days')
--   $2: INT      — minimum usage_count to protect from eviction

DELETE FROM asset_library
WHERE last_used_at < now() - $1
  AND usage_count < $2
RETURNING id, image_url;
-- Caller must also delete the image from R2/S3 using returned image_url.
```

### R2/S3 Storage Convention

**Object key pattern:**
```
assets/{slot_type}/{id}.png
```

**Examples:**
```
assets/sky/a1b2c3d4-e5f6-7890-abcd-ef1234567890.png
assets/subject/f9e8d7c6-b5a4-3210-fedc-ba9876543210.png
assets/wall/12345678-abcd-ef01-2345-678901234567.png
```

**Full URL pattern:**
```
{R2_PUBLIC_URL}/{bucket_name}/assets/{slot_type}/{id}.png
```
Example: `https://pub-xyz.r2.dev/depthkit-assets/assets/sky/a1b2c3d4-....png`

**Rationale:**
- `slot_type` prefix enables per-category R2 lifecycle policies (e.g., `sky/` assets with longer TTL since they're more reusable).
- UUID filename aligns with the DB primary key, making orphan cleanup trivial (diff DB ids vs R2 object listing).
- `.png` extension is always used — all cached images are PNG (with or without alpha) for consistent texture loading in Three.js.

**Required environment variables for R2 access:**
- `R2_PUBLIC_URL` — the public base URL for the R2 bucket
- `R2_ACCESS_KEY_ID` — R2 API access key
- `R2_SECRET_ACCESS_KEY` — R2 API secret key
- `R2_BUCKET_NAME` — bucket name (default: `depthkit-assets`)

OBJ-054 is responsible for implementing the path construction and upload logic using this convention.

## Design Decisions

### D1: `slot_type` uses OBJ-051's `SlotCacheCategory` values, not raw geometry slot names

The seed's schema sketch (Section 4.10) uses `slot_type TEXT` with examples like `'sky'`, `'subject'`, `'floor'`, `'left_wall'`. OBJ-051 refined this by defining a `SlotCacheCategory` union type that maps multiple geometry-specific slot names to canonical categories (e.g., tunnel's `left_wall` and canyon's `left_wall` both map to `'wall'`). This enables cross-geometry cache reuse.

The column is `TEXT NOT NULL` rather than a PostgreSQL `ENUM` because `SlotCacheCategory` is explicitly additive-only (OBJ-051: "Adding a category is a non-breaking change"). TEXT avoids ALTER TYPE migrations when new geometries introduce new categories.

**Constraint alignment:** Seed Section 4.10 ("queried by cosine similarity... filtered by slot_type"). TC-18 (slot-type filtering prevents cross-category contamination).

### D2: `embedding_model` column added beyond the seed sketch

The seed's schema (Section 4.10) does not include an `embedding_model` column. This addition is necessary because:
- If the embedding model is ever changed (e.g., upgrading from `text-embedding-3-small` to `text-embedding-3-large`), existing embeddings become incomparable — different models produce different vector spaces.
- The column enables safe mixed-model queries: filter by `embedding_model` to only compare embeddings from the same model.
- Enables a migration path: re-embed old entries without downtime, then swap the query filter.

**Trade-off:** One extra column and filter per query. Cost is negligible. Prevents a subtle, hard-to-debug accuracy degradation if models are switched.

### D3: IVFFlat index with lists=100, not HNSW

The seed specifies IVFFlat (Section 4.10). HNSW is the newer alternative in pgvector with better recall at the cost of higher memory usage and slower inserts. IVFFlat is the correct choice for this use case because:
- The expected table size is modest (thousands to low tens-of-thousands of rows over the first year).
- Insert speed matters — every cache miss writes a new row in the hot path.
- IVFFlat with `lists=100` provides adequate recall for top-1 queries on this scale.
- HNSW can be swapped in later if scale demands it — the query patterns are identical.

**Note on cold start:** IVFFlat requires training data. On an empty or very small table (<~1000 rows), pgvector performs a sequential scan instead, which is acceptable for cold-start. The index becomes effective as the table populates.

### D4: Vector dimension 1536 matches `text-embedding-3-small`

The seed specifies `VECTOR(1536)` (Section 4.10). This matches OpenAI's `text-embedding-3-small` model, the recommended starting point due to its balance of quality, speed, and cost ($0.00002/1K tokens). The `embedding_model` column (D2) provides a migration path to other models/dimensions. See edge case table for dimension change migration notes.

### D5: `width` and `height` are nullable

Image dimensions are useful for sizing validation but may not always be available at insert time. Making them nullable avoids blocking inserts.

### D6: Row-Level Security (RLS) with permissive policy

Supabase requires RLS to be enabled for REST API access. The depthkit pipeline uses the `service_role` key (which bypasses RLS), so the policy is permissive. More restrictive policies can be added later without schema changes.

### D7: No uniqueness constraint on (slot_type, original_prompt)

Two different generation calls with the exact same prompt could produce visually different images (non-deterministic generation). Both are valid cache entries. A uniqueness constraint would block legitimate re-generation. Deduplication, if desired, is an application-level concern in OBJ-054.

### D8: Cache eviction is documented but not mandated for V1

Query 5 (LRU eviction) is provided as a maintenance pattern. For V1, the expected table size does not require automatic eviction. The query is documented so that a cron job or manual process can be added later.

### D9: TypeScript types use `string` for `slot_type`, not `SlotCacheCategory`

OBJ-053's declared dependency is OBJ-007 only. OBJ-051 (which defines `SlotCacheCategory`) is not a declared dependency. The TypeScript row type uses `string` for `slot_type` with documentation comments listing the valid values. Type narrowing to `SlotCacheCategory` happens in OBJ-054, which depends on both OBJ-053 and OBJ-051. This keeps OBJ-053's dependency graph accurate and avoids an undeclared compile-time dependency.

### D10: `match_asset` RPC function is optional

The RPC function is a convenience and performance optimization (avoids sending a 1536-d vector through the REST query string). OBJ-054 may use either the RPC function or the equivalent raw SQL query (Query 1). The function is provided in a separate SQL file and its acceptance criterion is conditional.

### D11: Insert and query result types are recommended consumption guidance

`AssetLibraryInsert` and `AssetSimilarityResult` encode recommended patterns for OBJ-054. They are explicitly labeled as consumption guidance, not rigid contracts. OBJ-054 may define its own types if its query patterns diverge. `AssetLibraryRow` is the authoritative schema-level contract.

### D12: Storage convention is documented prose, not utility functions

The R2/S3 path pattern (`assets/{slot_type}/{id}.png`) is a documented convention. Utility functions to construct paths are OBJ-054's implementation concern, not a schema-level contract. The convention, rationale, and required environment variables are specified as prose.

## Acceptance Criteria

- [ ] **AC-01:** The SQL DDL creates the `asset_library` table with all columns specified: `id` (UUID PK), `slot_type` (TEXT NOT NULL), `original_prompt` (TEXT NOT NULL), `prompt_embedding` (VECTOR(1536) NOT NULL), `image_url` (TEXT NOT NULL), `has_alpha` (BOOLEAN NOT NULL DEFAULT false), `width` (INT nullable), `height` (INT nullable), `usage_count` (INT NOT NULL DEFAULT 1), `embedding_model` (TEXT NOT NULL DEFAULT 'text-embedding-3-small'), `created_at` (TIMESTAMPTZ NOT NULL DEFAULT now()), `last_used_at` (TIMESTAMPTZ NOT NULL DEFAULT now()).
- [ ] **AC-02:** CHECK constraints enforce: `slot_type` length 1–50, `original_prompt` length 1–2000, `image_url` length 1–2048, `width > 0` (when not null), `height > 0` (when not null), `usage_count >= 1`, `embedding_model` length 1–100.
- [ ] **AC-03:** An IVFFlat index exists on `prompt_embedding` using `vector_cosine_ops` with `lists = 100`.
- [ ] **AC-04:** A btree index exists on `slot_type`.
- [ ] **AC-05:** A composite btree index exists on `(slot_type, embedding_model)`.
- [ ] **AC-06:** A btree index exists on `last_used_at`.
- [ ] **AC-07:** Row-Level Security is enabled on the table with a permissive policy for all operations.
- [ ] **AC-08:** If the optional `match_asset` RPC function is deployed, it accepts parameters `(query_embedding VECTOR(1536), query_slot_type TEXT, query_embedding_model TEXT, match_count INT)` and returns rows with columns `(id, image_url, original_prompt, has_alpha, width, height, similarity)`. The function is optional — OBJ-054 may use either the RPC function or the equivalent raw SQL query (Query 1).
- [ ] **AC-09:** The similarity search query (Query 1) filters by both `slot_type` and `embedding_model`, orders by cosine distance ascending, and limits to 1 row.
- [ ] **AC-10:** The similarity score is computed as `1 - (prompt_embedding <=> query_embedding)`, yielding a value in [0, 1] where 1 = identical.
- [ ] **AC-11:** The cache-hit update query (Query 2) increments `usage_count` by 1 and sets `last_used_at` to `now()`.
- [ ] **AC-12:** The cache-miss insert query (Query 3) returns the generated `id` via `RETURNING id`.
- [ ] **AC-13:** The `AssetLibraryRow` TypeScript type has fields matching all SQL columns, with `slot_type` typed as `string` (not `SlotCacheCategory`). A doc comment lists the valid values from OBJ-051.
- [ ] **AC-14:** The `AssetLibraryInsert` and `AssetSimilarityResult` types are explicitly labeled as recommended consumption types for OBJ-054.
- [ ] **AC-15:** Timestamp fields (`created_at`, `last_used_at`) are typed as `string` with a doc comment noting Supabase JS returns TIMESTAMPTZ as ISO 8601 strings.
- [ ] **AC-16:** The R2/S3 storage convention documents the object key pattern `assets/{slot_type}/{id}.png` with examples for at least two slot types and the full URL pattern.
- [ ] **AC-17:** The storage convention documents all required environment variables (`R2_PUBLIC_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`).
- [ ] **AC-18:** The DDL includes `CREATE EXTENSION IF NOT EXISTS vector;` before the table creation.
- [ ] **AC-19:** The eviction query (Query 5) returns `id` and `image_url` of deleted rows so the caller can clean up R2/S3 objects.
- [ ] **AC-20:** The `AssetLibraryRow` type does not import from OBJ-051. No compile-time dependency on OBJ-051 exists in `src/cache/`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| INSERT with `prompt_embedding` of wrong dimension (e.g., 768-d vector into 1536-d column) | PostgreSQL/pgvector rejects the INSERT with a dimension mismatch error. OBJ-054 must catch this and report a clear error naming the expected vs. actual dimension. |
| INSERT with empty `slot_type` (`''`) | CHECK constraint violation. Rejected at DB level. |
| INSERT with `original_prompt` exceeding 2000 chars | CHECK constraint violation. OBJ-054 should truncate or reject before sending to DB. |
| INSERT with `width: 0` or `width: -1` | CHECK constraint violation (`width > 0`). |
| INSERT with `width: null` | Allowed (nullable column). |
| Similarity query on an empty table | Returns 0 rows. OBJ-054 treats this as a cache miss. |
| Similarity query with a `slot_type` that has no entries | Returns 0 rows. Cache miss. |
| Similarity query with `slot_type` value not in `SlotCacheCategory` | Query executes normally (TEXT column, no enum). Returns 0 rows since no entries match. OBJ-054 should validate `slot_type` against `SlotCacheCategory` before querying. |
| Concurrent INSERTs with the same prompt | Both succeed (no uniqueness constraint per D7). Results in two rows — acceptable. |
| IVFFlat index on table with <100 rows | pgvector falls back to sequential scan. Performance is fine for small tables. No error. |
| R2 image deleted but `asset_library` row still exists (orphan reference) | OBJ-054's cache-hit path should handle HTTP 404 from the image URL gracefully — treat as cache miss, optionally DELETE the orphan row, then generate fresh. |
| `embedding_model` mismatch between query and stored rows | The `WHERE embedding_model = $3` filter in the similarity query excludes rows from different models. Returns 0 rows if no rows match the current model — treated as cache miss. This is correct: cross-model similarity is meaningless. |
| Very long image_url (>2048 chars) | CHECK constraint violation. R2/S3 URLs are typically <200 chars; this is a safety rail. |
| Embedding model change requiring different vector dimension | Requires `ALTER TABLE asset_library ALTER COLUMN prompt_embedding TYPE VECTOR(new_dim)` migration + re-embedding all existing rows. This is a destructive operation; plan for downtime or shadow-table migration. The `embedding_model` column (D2) allows mixed-model coexistence during the transition period (old rows filtered out by the `embedding_model` WHERE clause, then re-embedded or evicted). |

## Test Strategy

### Schema Validation Tests (against a test Supabase instance or local PostgreSQL + pgvector)

1. **Table creation**: DDL executes without errors on a fresh database with pgvector enabled.
2. **Column types**: Introspect `information_schema.columns` to verify each column's type, nullability, and defaults match the spec.
3. **CHECK constraints**: Attempt INSERTs with boundary values (empty strings, null where not allowed, zero/negative dimensions, `usage_count: 0`) and verify rejection.
4. **Index existence**: Query `pg_indexes` to verify all 4 indexes exist with correct methods (ivfflat, btree).
5. **RLS**: Verify `pg_tables.rowsecurity` is `true` for `asset_library`.
6. **RPC function** (if deployed): Call `match_asset` with a known embedding and verify correct return shape.

### Similarity Query Tests

7. **Basic insertion and retrieval**: Insert an asset, query with the same embedding, verify `similarity ≈ 1.0`.
8. **Slot-type filtering**: Insert assets in different slot_types with similar embeddings. Query for one slot_type and verify only matching slot_type rows are returned. (TC-18)
9. **Embedding model filtering**: Insert two rows with the same prompt but different `embedding_model` values. Query with one model and verify only that model's row is returned.
10. **Cache hit update**: After a cache hit, verify `usage_count` incremented and `last_used_at` updated.
11. **Eviction query**: Insert old rows (manually set `last_used_at` to past), run eviction query, verify correct rows deleted and returned.

### TypeScript Type Tests

12. **AssetLibraryRow** compiles with `slot_type: string` (not `SlotCacheCategory`).
13. **AssetLibraryInsert** accepts a minimal valid insert (required fields only).
14. **No import from OBJ-051** exists in `src/cache/` files.

### Relevant Testable Claims

- **TC-17** (threshold acceptance): This schema provides the data model; OBJ-054 implements the threshold gate. The schema must support Query 1 returning a similarity score for OBJ-054 to evaluate.
- **TC-18** (slot-type filtering prevents contamination): Validated by test #8 — the WHERE clause on `slot_type` prevents cross-category results.
- **TC-19** (cache hit rates 30-60%): The analytics query (Query 4) enables measuring this. OBJ-054 uses it for reporting.
- **TC-20** (query latency negligible): The IVFFlat index + slot_type btree index support the <500ms target. Benchmark test #7 against a populated table.

## Integration Points

### Depends on

| Upstream | What OBJ-053 uses |
|---|---|
| **OBJ-007** (Depth model / slot taxonomy) | Conceptual dependency. OBJ-007 defines the slot taxonomy that underpins the caching categories. OBJ-053 does not import any OBJ-007 code at compile time — the relationship is that the `slot_type` column values (sky, wall, floor, etc.) derive from the slot taxonomy OBJ-007 established, as further refined by OBJ-051's `SlotCacheCategory`. |

### Consumed by

| Downstream | How it uses OBJ-053 |
|---|---|
| **OBJ-054** (Semantic caching middleware) | Uses the SQL schema as its data store. Imports `AssetLibraryRow`, and optionally `AssetLibraryInsert`/`AssetSimilarityResult` as consumption type guidance. Calls `match_asset` RPC or raw Query 1 for similarity search. Uses the documented R2/S3 storage convention for path construction. Implements the threshold gate logic (> 0.92 → hit, ≤ 0.92 → miss) against the `similarity` value. OBJ-054 also depends on OBJ-051 and performs the type narrowing from `string` to `SlotCacheCategory`. |
| **OBJ-076** (Cache analytics / monitoring) | Uses Query 4 for hit-rate estimation and per-slot-type usage statistics. |

### File Placement

```
depthkit/
  src/
    cache/
      index.ts                    # Barrel export
      asset-library.types.ts      # AssetLibraryRow, AssetLibraryInsert (recommended),
                                  #   AssetSimilarityResult (recommended)
  sql/
    001_create_asset_library.sql  # DDL: table, indexes, RLS, extension
    002_create_match_asset.sql    # Optional RPC function
  docs/
    asset-cache-queries.md        # Documented query patterns for OBJ-054 reference
```

## Open Questions

1. **Should the threshold (0.92) be stored in the database as a configurable parameter?** The seed hardcodes 0.92 but notes it should be tuned. **Recommendation:** No — keep it as an application-level constant in OBJ-054. A DB round-trip to read config on every cache query is unnecessary overhead.

2. **Should duplicate detection be added (same prompt + same slot_type)?** Per D7, no uniqueness constraint. But OBJ-054 could implement an exact-match fast path as an optimization. **Recommendation:** Defer to OBJ-054.

3. **Should there be a `style` or `theme` column for filtering cache queries by visual style?** **Recommendation:** Not for V1. The embedding space should capture style differences. If needed later, a nullable TEXT column can be added without migration.

4. **IVFFlat index rebuild after significant data distribution changes?** pgvector IVFFlat indexes are not automatically maintained when data distribution shifts. `REINDEX INDEX idx_asset_embedding;` may be needed periodically. **Recommendation:** Document as an operational note, not a V1 automation concern.

---

## Changes from Round 1 → Round 2

| Issue | Resolution |
|---|---|
| #1 CRITICAL: Undeclared OBJ-051 dependency | **Fixed.** `slot_type` typed as `string` in TypeScript. No import from OBJ-051. Doc comments list valid values. Type narrowing deferred to OBJ-054. Added D9, AC-13 updated, AC-20 added, test #14 added. |
| #2 MAJOR: `buildAssetKey`/`buildAssetUrl` exceed scope | **Fixed.** Functions removed. Storage convention documented as prose with pattern, examples, rationale, and env vars. Added D12. |
| #3 MAJOR: Insert/query types straddle boundary | **Fixed.** `AssetLibraryInsert` and `AssetSimilarityResult` explicitly labeled "RECOMMENDED CONSUMPTION TYPE — guidance for OBJ-054" with note that OBJ-054 may define its own. Added D11, AC-14 updated. |
| #4 MINOR: AC-16/AC-17 orphaned | **Fixed.** AC-16 now validates documented storage convention pattern with examples. AC-17 validates documented env vars. |
| #5 MINOR: RPC function marked optional | **Fixed.** AC-08 now conditional ("If the optional `match_asset` RPC function is deployed..."). SQL file header notes optionality. Added D10. |
| #6 MINOR: Timestamp string justification | **Fixed.** Doc comment added to `AssetLibraryRow`: "Supabase JS client returns TIMESTAMPTZ as ISO 8601 strings." AC-15 added. |
| #7 MINOR: Missing dimension migration path | **Fixed.** Added to edge cases table: "Embedding model change requiring different vector dimension" with migration steps and `embedding_model` column's role during transition. |

---

I believe all seven issues from the Challenger's review have been addressed. I'd like the Challenger to verify each resolution and approve if satisfied.

---

## Round 4 — spec_challenger

## Challenger Review — Round 2 (Verification)

Let me verify each fix systematically.

### Issue 1 (CRITICAL): Undeclared OBJ-051 dependency → **VERIFIED FIXED**

- `AssetLibraryRow.slot_type` is now `string` ✓
- Doc comment lists valid values without importing the type ✓
- D9 documents the rationale ✓
- AC-13 says "typed as `string` (not `SlotCacheCategory`)" ✓
- AC-20 says "does not import from OBJ-051" ✓
- Test #14 checks no import exists ✓
- Integration Points table correctly notes OBJ-054 does the narrowing ✓

### Issue 2 (MAJOR): Functions exceed scope → **VERIFIED FIXED**

- `buildAssetKey`/`buildAssetUrl` removed from interface contract ✓
- Storage convention documented as prose with pattern, examples, env vars ✓
- D12 documents the rationale ✓
- Module exports no longer include function exports ✓
- `storage.types.ts` removed from file placement ✓

### Issue 3 (MAJOR): Insert/query types labeled as guidance → **VERIFIED FIXED**

- Both types have `RECOMMENDED CONSUMPTION TYPE — guidance for OBJ-054` header ✓
- Both doc comments say "OBJ-054 may define its own types if its needs differ" ✓
- D11 documents the rationale ✓
- AC-14 explicitly tests the labeling ✓

### Issue 4 (MINOR): AC-16/AC-17 updated → **VERIFIED FIXED**

- AC-16 now tests documented storage convention pattern ✓
- AC-17 now tests documented env vars ✓

### Issue 5 (MINOR): RPC optional → **VERIFIED FIXED**

- AC-08 now conditional: "If the optional `match_asset` RPC function is deployed..." ✓
- SQL header says "OPTIONAL" ✓
- D10 documents the rationale ✓

### Issue 6 (MINOR): Timestamp justification → **VERIFIED FIXED**

- Doc comment on `AssetLibraryRow`: "Supabase JS client returns TIMESTAMPTZ as ISO 8601 strings" ✓
- AC-15 tests this ✓

### Issue 7 (MINOR): Dimension migration → **VERIFIED FIXED**

- Edge case table includes "Embedding model change requiring different vector dimension" with `ALTER TABLE` steps and `embedding_model` column's transition role ✓

---

All 7 issues are structurally resolved. Now let me do a final pass for any new issues introduced in the revision or things I missed in Round 1.

### Final Pass — New/Missed Issues

**No new issues found.** The revision is clean — it didn't introduce regressions. Let me confirm a few final things:

1. **Scope discipline:** Schema + types + query patterns + storage convention. No implementation code. No middleware logic. ✓
2. **Vocabulary compliance:** Uses seed terms correctly. "slot_type" aligns with seed Section 4.10. No vocabulary drift. ✓
3. **Constraint compliance:** This is an integration/infrastructure objective. C-01 through C-11 are rendering pipeline constraints — not directly applicable to the DB schema. No violations. ✓
4. **Downstream compatibility for OBJ-054:** Query patterns are documented, types are provided as guidance, storage convention is clear. An implementer of OBJ-054 has everything they need from this spec. ✓
5. **Acceptance criteria testability:** All 20 ACs are specific and pass/fail testable. ✓

The spec is ready.

CONCLUSION:

The specification for OBJ-053 defines the AssetLibrary database schema for Supabase (PostgreSQL + pgvector), including SQL DDL, TypeScript row types, documented query patterns, and R2/S3 storage convention. All seven issues from Round 2 review have been verified as resolved: the undeclared OBJ-051 dependency was eliminated (slot_type typed as string), utility functions were removed in favor of documented prose convention, consumption types were properly labeled as guidance, the RPC function was marked optional, and edge cases were expanded to cover dimension migration. The spec stays cleanly within its schema-only scope and provides everything OBJ-054 needs downstream.

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me read the existing meta.json before updating it.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-053/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-053",
     3→  "description": "Semantic caching database schema -- AssetLibrary table in Supabase (PostgreSQL + pgvector) per Section 4.10. Columns: id, slot_type, original_prompt, prompt_embedding (VECTOR(1536)), image_url, has_alpha, width, height, usage_count, created_at, last_used_at. Indexes: ivfflat on prompt_embedding with vector_cosine_ops, btree on slot_type. R2/S3 storage strategy for cached images.",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. Medium priority. Database schema only -- middleware logic is OBJ-054."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-053/output.md",
  "content": "# Specification: Semantic Caching Database Schema \u2014 AssetLibrary Table (OBJ-053)\n\n## Summary\n\nOBJ-053 defines the **AssetLibrary database schema** for Supabase (PostgreSQL + pgvector) that powers depthkit's semantic image caching layer. It specifies the table structure, column definitions, indexes, constraints, the R2/S3 storage convention for cached images, and the documented query patterns that OBJ-054 (the middleware logic) will use. This is a schema-only objective \u2014 it produces SQL DDL, a TypeScript row type mirroring the table, recommended consumption types for OBJ-054, and documented query patterns. It does not implement the middleware, embedding logic, or threshold gate (those are OBJ-054).\n\n## Interface Contract\n\n### Database Schema (SQL DDL)\n\n```sql\n-- =============================================================\n-- AssetLibrary table \u2014 semantic cache for generated image assets\n-- Requires: pgvector extension enabled in Supabase project\n-- File: sql/001_create_asset_library.sql\n-- =============================================================\n\n-- Ensure pgvector is available\nCREATE EXTENSION IF NOT EXISTS vector;\n\n-- Core table\nCREATE TABLE asset_library (\n  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n\n  -- Canonical slot category (not raw geometry slot name).\n  -- Valid values are defined by OBJ-051's SlotCacheCategory union:\n  -- 'sky' | 'backdrop' | 'floor' | 'ceiling' | 'wall' |\n  -- 'midground' | 'subject' | 'foreground' | 'landmark'\n  -- TEXT (not ENUM) to allow additive expansion without migrations.\n  slot_type       TEXT NOT NULL\n                  CHECK (char_length(slot_type) > 0 AND char_length(slot_type) <= 50),\n\n  -- The exact prompt used to generate this image.\n  original_prompt TEXT NOT NULL\n                  CHECK (char_length(original_prompt) > 0 AND cha
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-053/output.md
You've hit your limit · resets 1am (America/New_York)
