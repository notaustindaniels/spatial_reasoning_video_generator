# Specification: Semantic Caching Database Schema — AssetLibrary Table (OBJ-053)

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

  /** Timestamp of initial creation. ISO 8601 string (Supabase JS returns TIMESTAMPTZ as strings). */
  readonly created_at: string;

  /** Timestamp of most recent cache hit. ISO 8601 string (Supabase JS returns TIMESTAMPTZ as strings). */
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
- [ ] **AC-02:** CHECK constraints enforce: `slot_type` length 1-50, `original_prompt` length 1-2000, `image_url` length 1-2048, `width > 0` (when not null), `height > 0` (when not null), `usage_count >= 1`, `embedding_model` length 1-100.
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

7. **Basic insertion and retrieval**: Insert an asset, query with the same embedding, verify `similarity ~ 1.0`.
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
| **OBJ-054** (Semantic caching middleware) | Uses the SQL schema as its data store. Imports `AssetLibraryRow`, and optionally `AssetLibraryInsert`/`AssetSimilarityResult` as consumption type guidance. Calls `match_asset` RPC or raw Query 1 for similarity search. Uses the documented R2/S3 storage convention for path construction. Implements the threshold gate logic (> 0.92 -> hit, <= 0.92 -> miss) against the `similarity` value. OBJ-054 also depends on OBJ-051 and performs the type narrowing from `string` to `SlotCacheCategory`. |
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
