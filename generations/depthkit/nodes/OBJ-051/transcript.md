# Deliberation Transcript: OBJ-051

---

## Round 1 — spec_author

Looking at OBJ-051's metadata, dependency (OBJ-007), and the seed sections (4.7, 4.8, OQ-02), let me first check the current codebase state for context.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-051/**/*"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-007/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-007/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "src/spatial/depth-model.*"
}
[Tool Result] No files found

[Tool: Grep]
  Input: {
  "pattern": "promptGuidance",
  "output_mode": "files_with_matches"
}
[Tool Result] Found 12 files
nodes/OBJ-071/transcript.md
nodes/OBJ-071/output.md
nodes/OBJ-021/transcript.md
nodes/OBJ-021/output.md
nodes/OBJ-020/transcript.md
nodes/OBJ-019/transcript.md
nodes/OBJ-020/output.md
nodes/OBJ-019/output.md
nodes/OBJ-018/transcript.md
nodes/OBJ-018/output.md
nodes/OBJ-007/transcript.md
nodes/OBJ-007/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-018/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md

[Tool: Glob]
  Input: {
  "pattern": "src/spatial/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/scenes/geometries/**/*"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: Stage Scene Geometry (OBJ-018)
     2→
     3→## Summary
     4→
     5→OBJ-018 defines the **stage** scene geometry — the default, most fundamental geometry in depthkit. It represents a classic "subject in front of a background" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/stage.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The stage scene g... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: Tunnel Scene Geometry (OBJ-019)
     2→
     3→## Summary
     4→
     5→OBJ-019 defines the **tunnel scene geometry** -- the concrete `SceneGeometry` definition registered as `'tunnel'` in the geometry registry. The tunnel arranges five planes (floor, ceiling, left wall, right wall, end wall) into a box-like corridor receding along the negative Z-axis. When the camera pushes forward, walls undergo real perspective distortion -- converging to a vanishing point -- producing the signature 2.5D depth effect described in seed Section 4.2. This is the geometry that demonstrates depthkit's core differentiator: perspective projection that flat 2D parallax cannot replicate.
     6→
     7→## Interface Contract
     8→
     9→### Module Export
    10→
    11→```typescript
    12→// src/scenes/geometries/tunnel.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The tunnel scene geometry definition.
    18→ *
    19→ * Exported for... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: Canyon Scene Geometry (OBJ-020)
     2→
     3→## Summary
     4→
     5→OBJ-020 defines the **canyon** scene geometry — a narrow, vertically dramatic 3D space with tall wall planes on left and right, a floor plane, an open sky above, and an optional end wall at depth. The camera pushes forward through the canyon or floats upward to reveal vertical scale. This geometry produces the feeling of traveling through a narrow gorge, alley, corridor between tall buildings, or any space defined by towering vertical boundaries. It registers itself via `registerGeometry()` from OBJ-005 and defines its slot set per OBJ-007's depth model contract.
     6→
     7→## Interface Contract
     8→
     9→### Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/canyon.ts
    13→
    14→import type { SceneGeometry, PlaneSlot, FogConfig } from './types';
    15→import { registerGeometry } from './registry';
    16→```
    17→
    18→The module defines and ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "limit": 150
}
[Tool Result]      1→# Specification: Flyover Scene Geometry (OBJ-021)
     2→
     3→## Summary
     4→
     5→OBJ-021 defines the **flyover** scene geometry — a spatial arrangement designed for aerial/bird's-eye perspective. A large ground plane lies below the camera (`FLOOR` rotation), a sky plane sits at extreme depth above, and optional landmark planes rise vertically from the ground at varying depths and lateral positions. The camera moves forward while positioned above the ground, producing an immersive "flying over terrain" effect where the ground plane undergoes strong perspective foreshortening and landmarks pass by on either side. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/flyover.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The flyover scene geometr... [truncated]
Now let me check the other geometry outputs and the OBJ-022 (diorama, in progress) to understand the full slot landscape:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "offset": 150,
  "limit": 80
}
[Tool Result]    150→      'Avoid text or asymmetric details that look wrong when mirrored on the opposite wall.',
   151→    expectsAlpha: false,
   152→  },
   153→  right_wall: {
   154→    promptGuidance:
   155→      'Wall surface texture viewed in side perspective, receding to a vanishing point. ' +
   156→      'Same guidance as left_wall. Often the same image is used for both walls to create a symmetrical corridor. ' +
   157→      'If using different images, ensure similar style/palette for visual coherence.',
   158→    expectsAlpha: false,
   159→  },
   160→  end_wall: {
   161→    promptGuidance:
   162→      'Distant scene visible at the far end of the corridor -- the vanishing point target. ' +
   163→      'A light source, exit doorway, distant landscape, portal, or glowing terminus. ' +
   164→      'Will be heavily fog-faded by default, so high-contrast or bright images read best at distance.',
   165→    expectsAlpha: false,
   166→  },
   167→};
   168→```
   169→
   170→### Barr... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": 150,
  "limit": 100
}
[Tool Result]    150→```typescript
   151→// src/scenes/geometries/flyover.ts (bottom of file)
   152→
   153→import { registerGeometry } from './registry';
   154→
   155→// Self-registers when the module is imported.
   156→registerGeometry(flyoverGeometry);
   157→```
   158→
   159→### Module Exports
   160→
   161→```typescript
   162→// src/scenes/geometries/flyover.ts
   163→export { flyoverGeometry };
   164→```
   165→
   166→The barrel export `src/scenes/geometries/index.ts` must re-export from `./flyover` so that importing the geometries barrel triggers registration.
   167→
   168→## Design Decisions
   169→
   170→### D1: `ground` instead of `floor` — semantic distinction from the stage geometry
   171→
   172→The stage geometry uses a slot named `floor` — a horizontal surface that functions as a room floor or ground level at the base of a scene. The flyover geometry uses `ground` instead because the semantic role is different: this is a vast terrain/landscape viewed from above, not a s... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-071/output.md",
  "limit": 200
}
[Tool Result]      1→# Specification: OBJ-071 — SKILL.md Geometry and Camera Reference Sections
     2→
     3→## Summary
     4→
     5→OBJ-071 fills in the geometry and camera reference sub-files (`docs/skill/geometry-reference.md` and `docs/skill/camera-reference.md`) created as scaffolding by OBJ-070. OBJ-070 established the document architecture and provided a full section for the `stage` geometry and full sections for `slow_push_forward`, `slow_pull_back`, `static`, and `gentle_float` cameras, with stub sections for everything else. OBJ-071 expands stubs to full sections for all verified geometries (`tunnel`, `canyon`, `flyover`) and all verified camera presets (`lateral_track_left`, `lateral_track_right`, `tunnel_push_forward`, `flyover_glide`), updates the SKILL.md summary tables to reflect the new content, and updates the complete annotated example in SKILL.md to use at least one newly-documented geometry. Stub sections remain for unverified geometries and cameras. This objective is the pri... [truncated]
Now let me check how OBJ-053 and OBJ-054 (downstream consumers) relate to OBJ-051:
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-053/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-053/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-054/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-054/meta.json

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-072/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-072/meta.json

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
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-072/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-072",
     3→  "description": "SKILL.md prompt templates, common patterns, and anti-patterns -- image generation prompt templates per depth slot type (far_bg, mid_bg, midground, subject, near_fg per Section 4.7), recipe patterns for common video types ('5-scene explainer', '30-second social clip'), and anti-patterns (AP-07: never put text in parallax planes, etc). Per Section 4.9.",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-070", "OBJ-051"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 integration. Medium priority."
    12→}
    13→
Now I have a clear picture. Let me also quickly check the existing slot guidance patterns from OBJ-019 (tunnel) to understand the established pattern:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "offset": 150,
  "limit": 30
}
[Tool Result]    150→
   151→subject: {
   152→  // ... PlaneSlot fields from table above ...
   153→  name: 'subject',
   154→  promptGuidance: 'Focal element within the canyon — person, creature, vehicle, landmark. Isolated on transparent background. Scale should feel small relative to canyon walls.',
   155→  expectsAlpha: true,
   156→}
   157→```
   158→
   159→### Module Exports
   160→
   161→The module has no public exports beyond the side effect of calling `registerGeometry()` at import time. Consumers access the canyon geometry via `getGeometry('canyon')` from the OBJ-005 registry.
   162→
   163→```typescript
   164→// src/scenes/geometries/canyon.ts
   165→// No named exports — registration is the side effect
   166→
   167→import { registerGeometry } from './registry';
   168→// ... define canyonGeometry ...
   169→registerGeometry(canyonGeometry);
   170→```
   171→
   172→The geometry module must be imported (for its registration side effect) by the geometry barrel export `src/scenes/... [truncated]
I now have comprehensive context. Let me propose the specification for OBJ-051.

---

# Proposed Specification: OBJ-051 — Image Generation Strategy: Flux.1 Schnell Prompt Engineering Per Slot Type

## Summary

OBJ-051 defines the **image generation prompt engineering strategy** for depthkit — the prompt templates, perspective-aware prompting rules, transparency handling guidelines, and per-slot-type generation guidance that enable an LLM to produce Flux.1 Schnell image prompts that are spatially appropriate for each slot in each geometry. This is a knowledge artifact with a thin programmatic interface: a `PromptTemplate` type system and a `SLOT_PROMPT_REGISTRY` data structure that maps `(geometry, slot_name)` pairs to structured prompt guidance. It is consumed by OBJ-072 (SKILL.md prompt templates section), OBJ-054 (semantic caching middleware — uses `slot_type` categorization for cache queries), and indirectly by any LLM authoring pipeline that needs to generate images for a manifest.

## Interface Contract

### Core Types

```typescript
// src/prompts/types.ts

/**
 * Perspective orientation of the generated image.
 * Controls prompt engineering to match how the plane is
 * rotated in 3D space.
 *
 * - 'frontal': Image viewed straight-on (camera-facing planes).
 *   Standard composition. Used for backdrops, subjects, end walls.
 *
 * - 'top_down': Image viewed from above, mapped onto a floor plane
 *   (rotation [-PI/2, 0, 0]). Texture should look correct when
 *   viewed in perspective from a forward-looking or downward-angled
 *   camera. NOT a bird's-eye map — the texture is stretched along
 *   the depth axis by perspective projection.
 *
 * - 'bottom_up': Image viewed from below, mapped onto a ceiling
 *   plane (rotation [PI/2, 0, 0]). Similar to top_down but inverted.
 *
 * - 'side': Image viewed from the side, mapped onto a wall plane
 *   (rotation [0, ±PI/2, 0]). Texture recedes to a vanishing point
 *   along one axis. Horizontally repeating/seamless textures work best.
 */
export type PerspectiveOrientation = 'frontal' | 'top_down' | 'bottom_up' | 'side';

/**
 * Structured prompt guidance for a single slot within a geometry.
 *
 * This is the core data type that OBJ-051 produces. Each entry
 * provides everything an LLM needs to craft a Flux.1 Schnell prompt
 * for a specific slot in a specific geometry context.
 */
export interface SlotPromptGuidance {
  /**
   * The slot name within the geometry.
   * Must match the geometry's registered slot key.
   */
  readonly slotName: string;

  /**
   * The geometry this guidance applies to, or 'default' for
   * guidance that applies to the default slot taxonomy
   * (used when no geometry-specific override exists).
   */
  readonly geometryName: string;

  /**
   * How the plane is oriented in 3D space.
   * Drives the perspective-aware prompting rules.
   */
  readonly perspective: PerspectiveOrientation;

  /**
   * Whether the generated image should have a transparent
   * background (alpha channel). Maps to DepthSlot.expectsAlpha
   * from OBJ-007.
   */
  readonly requiresAlpha: boolean;

  /**
   * A reusable prompt suffix/instruction for requesting transparency.
   * Empty string if requiresAlpha is false.
   * Example: ", isolated on transparent background, PNG"
   */
  readonly alphaSuffix: string;

  /**
   * General description of what kind of image content belongs in
   * this slot. 1-2 sentences.
   */
  readonly contentDescription: string;

  /**
   * Concrete prompt template with a `{subject}` placeholder.
   * The LLM fills in the topic-specific content.
   * Example: "Expansive {subject} landscape, wide angle, atmospheric,
   *           no foreground objects, cinematic lighting"
   */
  readonly promptTemplate: string;

  /**
   * Perspective-specific prompting instructions. Explains WHY
   * the prompt is structured this way and what to avoid.
   * Critical for non-frontal orientations where naive prompting
   * produces images that look wrong on rotated planes.
   */
  readonly perspectiveNotes: string;

  /**
   * 2-3 concrete example prompts demonstrating correct usage
   * for different topics/themes.
   */
  readonly examplePrompts: readonly string[];

  /**
   * Things to explicitly avoid in prompts for this slot.
   * Anti-patterns that produce poor results.
   */
  readonly avoidList: readonly string[];

  /**
   * The normalized slot category for semantic caching (OBJ-054).
   * Maps potentially geometry-specific slot names to a canonical
   * category for the AssetLibrary's slot_type column.
   *
   * This enables cross-geometry cache sharing: a 'floor' texture
   * generated for a tunnel can be reused for a canyon's 'floor'
   * because they share the same cache category.
   *
   * Categories: 'sky', 'backdrop', 'floor', 'ceiling', 'wall',
   *             'midground', 'subject', 'foreground', 'landmark'
   */
  readonly cacheCategory: SlotCacheCategory;
}

/**
 * Canonical slot categories for the semantic cache.
 * These map to the AssetLibrary.slot_type column (OBJ-053).
 *
 * Multiple geometry-specific slot names may map to the same
 * category (e.g., tunnel's 'left_wall' and canyon's 'left_wall'
 * both map to 'wall'), enabling cross-geometry cache reuse.
 */
export type SlotCacheCategory =
  | 'sky'
  | 'backdrop'
  | 'floor'
  | 'ceiling'
  | 'wall'
  | 'midground'
  | 'subject'
  | 'foreground'
  | 'landmark';
```

### Registry Structure

```typescript
// src/prompts/slot-prompt-registry.ts

import type { SlotPromptGuidance } from './types';

/**
 * The complete registry of prompt guidance for all geometry/slot
 * combinations.
 *
 * Structure: Map<geometryName, Map<slotName, SlotPromptGuidance>>
 *
 * Includes a 'default' geometry key for the default slot taxonomy
 * (OBJ-007's DEFAULT_SLOT_TAXONOMY). Geometry-specific entries
 * override defaults when both exist for the same slot name.
 */
export const SLOT_PROMPT_REGISTRY: ReadonlyMap<
  string,
  ReadonlyMap<string, SlotPromptGuidance>
>;

/**
 * Resolves the prompt guidance for a specific geometry + slot
 * combination.
 *
 * Resolution order:
 * 1. If SLOT_PROMPT_REGISTRY has an entry for (geometryName, slotName),
 *    return it.
 * 2. Else if SLOT_PROMPT_REGISTRY has an entry for ('default', slotName),
 *    return it.
 * 3. Else return undefined — the caller must handle the missing case.
 *
 * @param geometryName - The geometry name (e.g., 'tunnel', 'stage').
 * @param slotName - The slot name within that geometry.
 * @returns The resolved SlotPromptGuidance, or undefined if no
 *   guidance exists for this combination.
 */
export function resolvePromptGuidance(
  geometryName: string,
  slotName: string
): SlotPromptGuidance | undefined;

/**
 * Returns all prompt guidance entries for a given geometry,
 * merging geometry-specific entries with default fallbacks
 * for any slots not explicitly overridden.
 *
 * Used by SKILL.md generation (OBJ-072) to produce the complete
 * prompt guidance table for a geometry section.
 *
 * @param geometryName - The geometry name.
 * @returns Map of slotName -> SlotPromptGuidance, with defaults
 *   merged in for any slots not geometry-specifically defined.
 *   Returns empty map if the geometry is unknown.
 */
export function getAllGuidanceForGeometry(
  geometryName: string
): ReadonlyMap<string, SlotPromptGuidance>;

/**
 * Returns the cache category for a given geometry + slot combination.
 * Convenience wrapper around resolvePromptGuidance().cacheCategory.
 *
 * Used by OBJ-054 (semantic caching middleware) to determine the
 * slot_type for AssetLibrary queries.
 *
 * @returns The SlotCacheCategory, or undefined if no guidance exists.
 */
export function getCacheCategory(
  geometryName: string,
  slotName: string
): SlotCacheCategory | undefined;
```

### Module Exports

```typescript
// src/prompts/index.ts (barrel export)

export type {
  PerspectiveOrientation,
  SlotPromptGuidance,
  SlotCacheCategory,
} from './types';

export {
  SLOT_PROMPT_REGISTRY,
  resolvePromptGuidance,
  getAllGuidanceForGeometry,
  getCacheCategory,
} from './slot-prompt-registry';
```

### Prompt Guidance Data

The registry must contain entries for the following geometries and slots. This section defines the **content requirements** — the actual `SlotPromptGuidance` values.

#### Default Taxonomy (geometry = `'default'`)

These provide fallback guidance for the 5 default slots from OBJ-007's `DEFAULT_SLOT_TAXONOMY`. Used when no geometry-specific override exists.

| Slot | perspective | requiresAlpha | cacheCategory | promptTemplate (representative) |
|------|------------|---------------|---------------|-------------------------------|
| `sky` | `frontal` | `false` | `sky` | `"Expansive {subject} sky, wide angle, atmospheric, no foreground objects, cinematic"` |
| `back_wall` | `frontal` | `false` | `backdrop` | `"Distant {subject} landscape, atmospheric perspective, slightly hazy, wide composition"` |
| `midground` | `frontal` | `false` | `midground` | `"Mid-distance {subject} element, environmental detail, natural setting"` |
| `subject` | `frontal` | `true` | `subject` | `"{subject}, dramatic lighting, isolated on transparent background, PNG, high detail"` |
| `near_fg` | `frontal` | `true` | `foreground` | `"Foreground {subject} elements, scattered, transparent background, bokeh, particles"` |

#### Stage Geometry (geometry = `'stage'`)

| Slot | perspective | requiresAlpha | cacheCategory | Key prompt notes |
|------|------------|---------------|---------------|-----------------|
| `backdrop` | `frontal` | `false` | `backdrop` | Full-scene background. Wide, atmospheric. No foreground objects. |
| `sky` | `frontal` | `false` | `sky` | Inherits default. Distant gradient/atmosphere behind backdrop. |
| `floor` | `top_down` | `false` | `floor` | **Perspective-aware:** ground surface viewed at an angle. Elongated/repeating textures. NOT a bird's-eye map. Avoid centered compositions — texture stretches along depth. |
| `midground` | `frontal` | `false` | `midground` | Inherits default. Environmental element between backdrop and subject. |
| `subject` | `frontal` | `true` | `subject` | Inherits default. Primary focal element, transparent background. |
| `near_fg` | `frontal` | `true` | `foreground` | Inherits default. Foreground framing, transparent. |

#### Tunnel Geometry (geometry = `'tunnel'`)

| Slot | perspective | requiresAlpha | cacheCategory | Key prompt notes |
|------|------------|---------------|---------------|-----------------|
| `floor` | `top_down` | `false` | `floor` | Ground surface texture in perspective. Elongated/repeating patterns (stone tiles, dirt path, water, metal grating). Wide, seamless. |
| `ceiling` | `bottom_up` | `false` | `ceiling` | Overhead surface texture in perspective. Repeating patterns (rock, pipes, vines, stalactites). |
| `left_wall` | `side` | `false` | `wall` | Wall surface texture receding to vanishing point. Elongated horizontal detail (brick, stone, coral, panels). Avoid text/asymmetric details. |
| `right_wall` | `side` | `false` | `wall` | Same as left_wall. Often same image mirrored. Ensure matching style/palette. |
| `end_wall` | `frontal` | `false` | `backdrop` | Distant terminus — light source, exit, landscape, portal. High-contrast (heavily fog-faded). |

#### Canyon Geometry (geometry = `'canyon'`)

| Slot | perspective | requiresAlpha | cacheCategory | Key prompt notes |
|------|------------|---------------|---------------|-----------------|
| `sky` | `bottom_up` | `false` | `sky` | Narrow strip of sky between canyon walls. Dramatic clouds, stars, atmosphere. Looking upward. |
| `left_wall` | `side` | `false` | `wall` | Tall vertical surface — rock face, cliff, building facade. Seamless/tileable. Dramatic lighting from above. |
| `right_wall` | `side` | `false` | `wall` | Matches or complements left_wall. Same or coordinated style/palette. |
| `floor` | `top_down` | `false` | `floor` | Ground surface extending into distance — rocky path, sand, cobblestones, water. Top-down or strongly receding perspective. |
| `end_wall` | `frontal` | `false` | `backdrop` | Distant vista or terminus — light at end, distant landscape, doorway. Atmospheric, slightly hazy. |
| `subject` | `frontal` | `true` | `subject` | Focal element within the canyon. Isolated, transparent background. Scale should feel small relative to walls. |

#### Flyover Geometry (geometry = `'flyover'`)

| Slot | perspective | requiresAlpha | cacheCategory | Key prompt notes |
|------|------------|---------------|---------------|-----------------|
| `sky` | `frontal` | `false` | `sky` | Wide sky, atmosphere, distant horizon. Fills upper frame. |
| `ground` | `top_down` | `false` | `floor` | Terrain/landscape from above. Strong top-down perspective. Vast, expansive. Repeating natural patterns (fields, forests, ocean, desert). NOT a flat map — should have texture depth. |
| `landmark_far` | `frontal` | `true` | `landmark` | Distant landmark — mountain, tower, distant structure. Transparent background. Small and atmospheric. |
| `landmark_left` | `frontal` | `true` | `landmark` | Left-side landmark rising from terrain. Transparent background. Vertical feature (building, tree cluster). |
| `landmark_right` | `frontal` | `true` | `landmark` | Right-side landmark. Transparent background. Matches or complements landmark_left in style. |
| `near_fg` | `frontal` | `true` | `foreground` | Close atmospheric elements — clouds, birds, particles. Transparent background. Emphasizes speed/altitude. |

### Perspective-Aware Prompting Rules

These are the core knowledge artifact — the rules that transform naive prompts into spatially correct ones.

#### Rule P1: `top_down` (Floor/Ground Planes)

Floor and ground planes are rotated `[-PI/2, 0, 0]` and viewed at an angle through the perspective camera. The texture is stretched along the depth axis (Z after rotation). Naive prompts like "a beautiful stone floor" produce images with eye-level composition that look wrong when projected onto a horizontal plane.

**Prompt strategy:**
- Request textures with a **receding perspective** or **top-down view**: "stone path extending into the distance", "top-down view of forest floor", "cobblestone road in perspective"
- Use **repeating/seamless patterns** that tolerate stretching: tiles, planks, gravel, water ripples, grass
- Avoid **centered focal-point compositions** — there should be no single "hero" element in the center
- Avoid **horizon lines** within the image — the 3D scene provides its own horizon
- Request **wide aspect ratios** or compositions that read well when stretched horizontally

**Why this matters:** The perspective projection matrix compresses the far end of a floor texture into a narrow band near the horizon and expands the near end to fill the bottom of the frame. Images with centered compositions produce a visible "sweet spot" that breaks the illusion. Seamless, pattern-based textures maintain the illusion under distortion.

#### Rule P2: `bottom_up` (Ceiling Planes)

Ceiling planes are rotated `[PI/2, 0, 0]`. Similar constraints to `top_down` but inverted — the texture is seen from below.

**Prompt strategy:**
- Request **overhead/architectural textures** viewed from below: "cave ceiling with stalactites, looking upward", "industrial pipes and beams overhead"
- Same seamless/repeating requirements as floor
- Avoid images with sky or horizon — the ceiling IS the overhead enclosure

#### Rule P3: `side` (Wall Planes)

Wall planes are rotated `[0, ±PI/2, 0]` and recede to a vanishing point along the Z-axis. The texture is compressed toward the far end and expanded at the near end.

**Prompt strategy:**
- Request **elongated horizontal textures**: "brick wall extending into the distance", "rock face with horizontal striations"
- **Horizontally seamless/tileable** textures are ideal — they prevent visible seaming at the near edge
- Avoid **text, signage, or asymmetric details** that become distorted or illegible under perspective
- Avoid **strong vertical center compositions** — the vanishing point distortion makes centered elements look off-center
- If left and right walls use different images, ensure **matching style and palette** for visual coherence

#### Rule P4: `frontal` (Camera-Facing Planes)

Camera-facing planes have no rotation (`[0, 0, 0]`). The image is displayed as-is, with perspective scaling (smaller at distance, larger nearby) but no angular distortion.

**Prompt strategy:**
- Standard composition rules apply — this is the most forgiving orientation
- For **subjects**: request transparent background ("isolated on transparent background, PNG")
- For **backdrops**: request wide, atmospheric scenes without foreground elements
- For **end walls**: request high-contrast images that remain readable through fog

### Transparency Handling Guidelines

#### Guideline T1: When to Request Alpha

Request transparent backgrounds for:
- **Subjects** (all geometries): always. Rectangular edges are immediately visible in 3D, especially with perspective distortion amplifying the corner geometry.
- **Foreground elements** (near_fg, atmospheric particles): always. Opaque foregrounds occlude the entire scene.
- **Landmarks** (flyover's landmark_far, landmark_left, landmark_right): always. They must blend with the ground and sky behind them.

Do NOT request transparent backgrounds for:
- **Sky/backdrop planes**: they fill the frame edge-to-edge. Transparency serves no purpose and some generators produce artifacts when forced to create transparent full-scene images.
- **Floor/ceiling/wall textures**: they fill their plane completely. Transparency would reveal the void behind them.

#### Guideline T2: Prompt Phrasing for Transparency

Flux.1 Schnell responds best to explicit transparency instructions appended to the prompt:
- **Strong**: `", isolated on transparent background, PNG"`
- **Medium**: `", on transparent background"`
- **Weak** (avoid): `", no background"` (often produces white/gray instead of alpha)

The `alphaSuffix` field in `SlotPromptGuidance` provides the standardized suffix. Always append it verbatim — do not rephrase.

#### Guideline T3: Fallback When Alpha Fails

When Flux.1 produces an image without alpha despite the transparency request (white or colored background instead of transparency):
- The asset pipeline (OBJ-054) should apply **background removal** (rembg or equivalent) as a post-processing step for any slot where `requiresAlpha: true`
- The slot's `cacheCategory` should be used to determine whether removal is needed — categories `subject`, `foreground`, and `landmark` always get background removal post-processing if no alpha channel is detected
- Categories `sky`, `backdrop`, `floor`, `ceiling`, `wall` never need background removal

### Prompt Composition Formula

An LLM generating image prompts should follow this formula:

```
[content description specific to the topic]
+ [perspective-orientation keywords from the guidance]
+ [style/mood modifiers]
+ [alpha suffix if requiresAlpha]
```

Example for a tunnel floor with topic "underwater cave":
```
"Ancient ocean floor with scattered shells and coral fragments,
 stone texture extending into the distance, top-down perspective,
 seamless repeating pattern, teal and dark blue tones, cinematic lighting"
```

Example for a stage subject with topic "deep sea anglerfish":
```
"Deep sea anglerfish with bioluminescent lure glowing,
 dramatic underwater lighting, high detail,
 isolated on transparent background, PNG"
```

## Design Decisions

### D1: Two-level registry with default fallback

The registry uses `(geometry, slot)` lookup with a `'default'` geometry fallback. This means:
- Slots with the same name and same spatial behavior across geometries (e.g., `subject` in both stage and canyon) can share default guidance
- Geometries with unique spatial requirements override the defaults (e.g., tunnel's `floor` needs different guidance than stage's `floor` because the tunnel cross-section creates different perspective distortion patterns)
- New geometries (OBJ-022–025, not yet verified) automatically get reasonable guidance for any standard slot names via defaults

**Alternatives considered:** (a) Flat map keyed by `geometryName:slotName` — simpler but no fallback, requiring duplicate entries for every shared slot. (b) Single slot-name-only map — ignores geometry context, producing wrong guidance for the same slot name across different geometries (tunnel floor vs flyover ground have different perspective behaviors even though both are `top_down`). The two-level approach balances specificity with DRY.

### D2: `cacheCategory` normalizes geometry-specific slot names for cross-geometry caching

OBJ-054 (semantic caching) queries the AssetLibrary filtered by `slot_type`. Without normalization, a floor texture generated for a tunnel (slot name `floor`) and a canyon (also slot name `floor`) would naturally share cache space, but a flyover's `ground` (functionally identical to `floor`) would not. The `cacheCategory` field provides the normalization layer.

The 9 categories (`sky`, `backdrop`, `floor`, `ceiling`, `wall`, `midground`, `subject`, `foreground`, `landmark`) cover all slots across all 4 verified geometries. New geometries should map their slots to existing categories wherever possible, introducing new categories only for fundamentally novel spatial roles.

**Constraint alignment:** Seed Section 4.10 specifies `slot_type` as the filter column. OBJ-053 defines the AssetLibrary with `slot_type TEXT NOT NULL`. The `cacheCategory` is what gets stored there.

### D3: `PerspectiveOrientation` as an explicit enum, not inferred from rotation

The perspective orientation could theoretically be computed from a slot's rotation values. However:
- The prompt strategy depends on human-understandable spatial reasoning ("this is a floor seen from above"), not on Euler angles
- A rotation of `[-PI/2, 0, 0]` is `top_down`, but `[-PI/2, 0, PI]` is also `top_down` (same orientation, just rotated 180° around X) — inference from rotation is fragile
- Making it explicit in the guidance record ensures the LLM can reason about prompt engineering without understanding Three.js rotation semantics

### D4: Prompt templates use `{subject}` as the single placeholder

Keeping one placeholder (`{subject}`) makes templates simple for LLM consumption. The LLM fills in the topic-specific content. More complex templating (multiple placeholders for mood, color, etc.) was considered but rejected — the LLM is better at composing prompts than following complex template grammars. The template provides structure; the LLM provides creativity.

### D5: This is both a programmatic module and a knowledge artifact

OBJ-051 lives in `src/prompts/` as importable TypeScript so that:
- OBJ-054 (semantic caching) can call `getCacheCategory()` at runtime to determine the `slot_type` for AssetLibrary queries
- OBJ-072 (SKILL.md) can import the registry to auto-generate prompt guidance documentation
- The manifest generation pipeline (OBJ-056) can import `resolvePromptGuidance()` to compose prompts programmatically

But the primary value is the _content_ — the perspective-aware rules, example prompts, and avoidance lists. These are the knowledge that makes blind image generation produce spatially correct results.

### D6: Guidance for unverified geometries is deferred

OBJ-022 (diorama), OBJ-023 (portal), OBJ-024 (panorama), OBJ-025 (close_up) are not yet verified. The registry does not include entries for them. When they are verified, their geometry specs should define slot guidance (following the pattern established by OBJ-019's `tunnelSlotGuidance` and OBJ-020's inline `DepthSlot` metadata), and this registry should be extended. The `'default'` fallback ensures any standard slot names in new geometries get reasonable guidance immediately.

### D7: Background removal determination is by `cacheCategory`, not by image analysis

Rather than analyzing each generated image for alpha channel presence, the pipeline uses `cacheCategory` (and `requiresAlpha`) to determine whether background removal should be applied. This is simpler, faster, and deterministic. Categories `subject`, `foreground`, and `landmark` always trigger background removal if the generated image lacks alpha. This aligns with seed Section 4.8's guidance.

### D8: Prompt guidance content is authoritative over OBJ-007's `promptGuidance` field and OBJ-019's `tunnelSlotGuidance`

OBJ-007's `DEFAULT_SLOT_TAXONOMY` includes `promptGuidance` strings per slot. OBJ-019 exports `tunnelSlotGuidance`. OBJ-020 embeds `promptGuidance` inline. These were written as preliminary guidance before the perspective-aware prompting rules existed. OBJ-051's `SLOT_PROMPT_REGISTRY` supersedes all of them as the single source of truth for image generation prompting. Downstream consumers (OBJ-072, OBJ-054) should import from `src/prompts/`, not from `DEFAULT_SLOT_TAXONOMY.promptGuidance` or `tunnelSlotGuidance`.

This does NOT mean OBJ-007 or OBJ-019 should be modified — their `promptGuidance` fields remain for backwards compatibility and as human-readable documentation within the spatial module. But the definitive, production-quality prompt guidance lives in OBJ-051's registry.

## Acceptance Criteria

### Registry Completeness

- [ ] **AC-01:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'default'` with exactly 5 slots: `sky`, `back_wall`, `midground`, `subject`, `near_fg`.
- [ ] **AC-02:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'stage'` with at least the geometry-specific slots: `backdrop`, `floor`. Other stage slots (`sky`, `midground`, `subject`, `near_fg`) may use defaults or explicit overrides.
- [ ] **AC-03:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'tunnel'` with exactly 5 slots: `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`.
- [ ] **AC-04:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'canyon'` with exactly 6 slots: `sky`, `left_wall`, `right_wall`, `floor`, `end_wall`, `subject`.
- [ ] **AC-05:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'flyover'` with exactly 6 slots: `sky`, `ground`, `landmark_far`, `landmark_left`, `landmark_right`, `near_fg`.

### Perspective Correctness

- [ ] **AC-06:** Every slot whose geometry definition uses `FLOOR` rotation (`[-PI/2, 0, 0]`) has `perspective: 'top_down'`. This includes: stage `floor`, tunnel `floor`, canyon `floor`, flyover `ground`.
- [ ] **AC-07:** Every slot whose geometry definition uses `CEILING` rotation (`[PI/2, 0, 0]`) has `perspective: 'bottom_up'`. This includes: tunnel `ceiling`.
- [ ] **AC-08:** Every slot whose geometry definition uses `LEFT_WALL` rotation (`[0, PI/2, 0]`) or `RIGHT_WALL` rotation (`[0, -PI/2, 0]`) has `perspective: 'side'`. This includes: tunnel `left_wall`, tunnel `right_wall`, canyon `left_wall`, canyon `right_wall`.
- [ ] **AC-09:** Every slot whose geometry definition uses `FACING_CAMERA` rotation (`[0, 0, 0]`) has `perspective: 'frontal'`. This includes all backdrop, subject, sky (except canyon sky which is `bottom_up`), end_wall, landmark, and near_fg slots.
- [ ] **AC-10:** Canyon `sky` has `perspective: 'bottom_up'` because the canyon sky plane uses rotation `[PI/2, 0, 0]` (horizontal plane facing downward, per OBJ-020).

### Alpha/Transparency

- [ ] **AC-11:** Every entry with `requiresAlpha: true` has a non-empty `alphaSuffix` containing the phrase "transparent background".
- [ ] **AC-12:** Every entry with `requiresAlpha: false` has `alphaSuffix` equal to `""` (empty string).
- [ ] **AC-13:** `requiresAlpha` is `true` for all slots where the corresponding geometry definition has `transparent: true` in its `PlaneSlot`. This includes: stage `subject`, stage `near_fg`, canyon `subject`, flyover `landmark_far`, flyover `landmark_left`, flyover `landmark_right`, flyover `near_fg`.
- [ ] **AC-14:** `requiresAlpha` is `false` for all sky, backdrop, floor, ceiling, wall, end_wall, and ground slots.

### Cache Categories

- [ ] **AC-15:** `cacheCategory` mappings are: sky→`'sky'`; backdrop/back_wall→`'backdrop'`; floor/ground→`'floor'`; ceiling→`'ceiling'`; left_wall/right_wall→`'wall'`; midground→`'midground'`; subject→`'subject'`; near_fg→`'foreground'`; landmark_far/landmark_left/landmark_right→`'landmark'`; end_wall→`'backdrop'`.
- [ ] **AC-16:** `getCacheCategory('tunnel', 'left_wall')` returns `'wall'`. `getCacheCategory('canyon', 'left_wall')` also returns `'wall'` — demonstrating cross-geometry cache sharing.
- [ ] **AC-17:** `getCacheCategory('flyover', 'ground')` returns `'floor'` — demonstrating normalization of geometry-specific slot names to canonical categories.

### Resolution Functions

- [ ] **AC-18:** `resolvePromptGuidance('tunnel', 'floor')` returns the tunnel-specific floor guidance (not the default taxonomy's guidance).
- [ ] **AC-19:** `resolvePromptGuidance('stage', 'subject')` returns guidance (either stage-specific or default fallback).
- [ ] **AC-20:** `resolvePromptGuidance('unknown_geometry', 'sky')` returns the default `sky` guidance (fallback to `'default'` geometry).
- [ ] **AC-21:** `resolvePromptGuidance('unknown_geometry', 'unknown_slot')` returns `undefined`.
- [ ] **AC-22:** `getAllGuidanceForGeometry('tunnel')` returns a map with all 5 tunnel slots, each with tunnel-specific guidance.
- [ ] **AC-23:** `getAllGuidanceForGeometry('stage')` returns a map with all 6 stage slots. Slots with geometry-specific overrides use those; slots without overrides use default fallbacks.

### Content Quality

- [ ] **AC-24:** Every `SlotPromptGuidance` entry has a non-empty `contentDescription`.
- [ ] **AC-25:** Every `SlotPromptGuidance` entry has a non-empty `promptTemplate` containing the `{subject}` placeholder.
- [ ] **AC-26:** Every `SlotPromptGuidance` entry with `perspective` !== `'frontal'` has a non-empty `perspectiveNotes` explaining the spatial constraints.
- [ ] **AC-27:** Every `SlotPromptGuidance` entry has at least 2 entries in `examplePrompts`.
- [ ] **AC-28:** Every `SlotPromptGuidance` entry has at least 1 entry in `avoidList`.
- [ ] **AC-29:** No `examplePrompts` entry for a `top_down` perspective slot contains horizon lines, centered compositions, or eye-level viewpoints.
- [ ] **AC-30:** No `examplePrompts` entry for a `side` perspective slot contains text, signage, or strongly vertical center compositions.

### Module Structure

- [ ] **AC-31:** All types and functions are accessible via the `src/prompts/index.ts` barrel export.
- [ ] **AC-32:** The module has zero runtime dependencies beyond standard JavaScript built-ins (Map, string operations).
- [ ] **AC-33:** The module does NOT import from `src/spatial/` or `src/scenes/` — it is self-contained. The perspective and requiresAlpha values are authored based on knowledge of the geometry specs, not computed from them at runtime.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `resolvePromptGuidance` for a geometry that exists but a slot that doesn't | Returns `undefined`. No error thrown. |
| `resolvePromptGuidance` for `('default', 'some_slot')` where 'some_slot' is not in default taxonomy | Returns `undefined`. |
| `getAllGuidanceForGeometry` for an unknown geometry | Returns empty `Map`. |
| `getAllGuidanceForGeometry` for `'stage'` where some slots use defaults | Returns merged map — stage-specific entries plus default fallbacks for non-overridden slots. Merging logic: for each slot name in the stage-specific map, use stage entry. For each remaining slot name in the default map that also appears in the stage geometry's registered slots, use default. Does NOT include default slots that the stage geometry doesn't define. |
| `getCacheCategory` for unknown geometry/slot | Returns `undefined`. |
| Same slot name, different geometries, different `perspective` | Expected — e.g., canyon `sky` is `bottom_up` but default `sky` is `frontal`. The geometry-specific entry takes precedence via `resolvePromptGuidance`. |
| Stage `floor` and tunnel `floor` have same `cacheCategory: 'floor'` | Correct — cross-geometry cache reuse is intentional. A stone floor texture works for both. The semantic caching threshold (0.92) handles cases where the prompt content is too different. |
| `{subject}` placeholder not filled in a template | Templates are documentation artifacts consumed by LLMs. The LLM replaces `{subject}`. If an automated pipeline uses the template, it must substitute `{subject}` before calling the image generator. Missing substitution is a pipeline bug, not an OBJ-051 concern. |

## Test Strategy

### Unit Tests

**resolvePromptGuidance:**
1. Known geometry + known slot → returns specific guidance.
2. Unknown geometry + known default slot → returns default guidance.
3. Known geometry + unknown slot → returns `undefined`.
4. Unknown geometry + unknown slot → returns `undefined`.
5. Geometry-specific entry overrides default for same slot name (e.g., `resolvePromptGuidance('tunnel', 'floor')` returns tunnel-specific guidance, not default — verify by checking `geometryName` field).

**getAllGuidanceForGeometry:**
1. `'tunnel'` → map with 5 entries (all tunnel-specific).
2. `'stage'` → map with 6 entries (mix of stage-specific and default fallbacks).
3. Unknown geometry → empty map.
4. `'default'` → map with 5 default taxonomy entries.

**getCacheCategory:**
1. `('tunnel', 'left_wall')` → `'wall'`.
2. `('tunnel', 'right_wall')` → `'wall'`.
3. `('flyover', 'ground')` → `'floor'`.
4. `('stage', 'backdrop')` → `'backdrop'`.
5. `('canyon', 'end_wall')` → `'backdrop'`.
6. Unknown combination → `undefined`.

**Registry content validation (static assertions):**
1. Every entry's `perspective` matches the corresponding geometry's rotation for that slot (per AC-06 through AC-10).
2. Every entry's `requiresAlpha` matches the corresponding geometry's `transparent` flag (per AC-13, AC-14).
3. Every entry has non-empty `contentDescription`, `promptTemplate` with `{subject}`, `examplePrompts` (≥2), `avoidList` (≥1).
4. Every non-frontal entry has non-empty `perspectiveNotes`.
5. Every `requiresAlpha: true` entry has non-empty `alphaSuffix`.

### Relevant Testable Claims

- **TC-04** (partial): The prompt templates are part of enabling "no manual 3D positioning" — the LLM uses slot names and prompt templates, never raw coordinates.
- **TC-08** (partial): The cache categories support the 8-geometry coverage goal by normalizing slot names across geometries.

## Integration Points

### Depends on

| Upstream | What OBJ-051 imports/references |
|---|---|
| **OBJ-007** (Depth model) | **Referenced, not imported.** The `DEFAULT_SLOT_TAXONOMY` slot names, `promptGuidance`, and `expectsAlpha` values inform OBJ-051's default prompt guidance content. OBJ-051 supersedes OBJ-007's `promptGuidance` as the definitive source for image generation prompting. |
| **OBJ-018** (Stage geometry) | **Referenced, not imported.** Slot names, rotations, and `transparent` flags inform OBJ-051's stage-specific guidance entries. |
| **OBJ-019** (Tunnel geometry) | **Referenced, not imported.** `tunnelSlotGuidance` content is incorporated (and possibly expanded) into OBJ-051's tunnel entries. |
| **OBJ-020** (Canyon geometry) | **Referenced, not imported.** Inline `DepthSlot` metadata is incorporated into OBJ-051's canyon entries. |
| **OBJ-021** (Flyover geometry) | **Referenced, not imported.** Slot descriptions and transparency flags inform OBJ-051's flyover entries. |

Note: OBJ-051's only formal dependency in the DAG is OBJ-007. The geometry specs (OBJ-018–021) are not formal dependencies but are verified and their content is consumed. This is acceptable because OBJ-051 doesn't import their code — it references their specifications to author content.

### Consumed by

| Downstream | How it uses OBJ-051 |
|---|---|
| **OBJ-054** (Semantic caching middleware) | Calls `getCacheCategory(geometry, slot)` to determine the `slot_type` value for AssetLibrary queries. Uses `requiresAlpha` to determine whether background removal post-processing is needed. |
| **OBJ-072** (SKILL.md prompt templates) | Imports `getAllGuidanceForGeometry()` or reads `SLOT_PROMPT_REGISTRY` to auto-generate the prompt template section of SKILL.md. Surfaces `promptTemplate`, `examplePrompts`, `avoidList`, and `perspectiveNotes` as LLM-facing documentation. |
| **OBJ-056** (Manifest generation via Claude API) | The Claude API pipeline references prompt templates and perspective rules (via SKILL.md or direct import) to compose Flux.1 prompts for each slot when generating a manifest from a topic. |

### File Placement

```
depthkit/
  src/
    prompts/
      index.ts                    # Barrel export
      types.ts                    # PerspectiveOrientation, SlotPromptGuidance,
                                  #   SlotCacheCategory
      slot-prompt-registry.ts     # SLOT_PROMPT_REGISTRY, resolvePromptGuidance,
                                  #   getAllGuidanceForGeometry, getCacheCategory
```

## Open Questions

1. **Should `getAllGuidanceForGeometry` require knowledge of which slots a geometry defines?** Currently it merges geometry-specific entries with default fallbacks. But without importing the geometry registry, it can't know which default slots apply to a given geometry. Options: (a) return all geometry-specific entries plus ALL defaults (may include irrelevant slots), (b) accept an optional `slotNames: string[]` parameter so callers can scope the merge, (c) just return geometry-specific entries and let callers handle defaults. **Recommendation:** Option (b) — accept an optional slot name list. If provided, only return guidance for those slots. If omitted, return all geometry-specific entries merged with all defaults (callers filter as needed).

2. **Should the module also define "style modifier" templates?** E.g., "cinematic documentary", "watercolor illustration", "pixel art" — consistent style tags appended to all prompts for a video. This would support brand coherence (seed Section 4.10 "consistency benefit"). **Recommendation:** Defer to OBJ-072. Style modifiers are a SKILL.md documentation concern, not a spatial/slot concern. OBJ-051 handles _what_ to generate for each slot; the style is a per-video choice made at authoring time.

3. **Should `end_wall` cache category be `'backdrop'` or a dedicated `'terminus'` category?** End walls serve a different spatial role than backdrops, but visually they often contain similar content (distant vistas, atmospheric scenes). **Recommendation:** `'backdrop'` — maximizes cache reuse. A distant landscape works as either a stage backdrop or a tunnel end wall. The semantic similarity threshold handles cases where the content diverges.

4. **How should this module evolve when OBJ-022–025 (diorama, portal, panorama, close_up) are verified?** Each new geometry spec should define its slot names and rotations. The implementer then adds entries to `SLOT_PROMPT_REGISTRY`. If a new slot maps naturally to an existing `cacheCategory`, use it. If truly novel (e.g., a cylindrical panorama plane), introduce a new category. **No architectural change needed** — the registry is designed for extension.

---

I believe this spec is comprehensive. It covers:
- The programmatic interface (`SlotPromptGuidance`, `SLOT_PROMPT_REGISTRY`, resolution functions)
- The knowledge content (perspective-aware rules P1–P4, transparency guidelines T1–T3, prompt composition formula)
- All 4 verified geometries with geometry-specific guidance
- Cache category normalization for OBJ-054
- Clear acceptance criteria traceable to geometry specs

I'd like the Challenger to verify and assess whether I've missed any edge cases or whether the `getAllGuidanceForGeometry` merge semantics need tightening.

---

## Round 2 — spec_challenger

I'll review the proposed spec carefully, checking against the seed, OBJ-007, the verified geometry specs (OBJ-018–021), and the downstream consumers (OBJ-054, OBJ-072).
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


Let me check the actual geometry specs to verify the perspective mappings and slot names claimed in the proposal.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "offset": 1,
  "limit": 250
}
[Tool Result]      1→# Specification: Stage Scene Geometry (OBJ-018)
     2→
     3→## Summary
     4→
     5→OBJ-018 defines the **stage** scene geometry — the default, most fundamental geometry in depthkit. It represents a classic "subject in front of a background" setup: a large backdrop plane at deep Z, a floor plane angled down from the camera using `FLOOR` rotation, and a subject plane at shallow Z, with optional midground, foreground, and sky planes. Unlike flat 2D compositing, the floor plane undergoes real perspective foreshortening as the camera moves, creating the defining 2.5D illusion. This geometry registers itself via OBJ-005's `registerGeometry()` and serves as the reference implementation and the basis for SKILL.md examples.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/stage.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The stage scene g... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-019/output.md",
  "offset": 1,
  "limit": 250
}
[Tool Result]      1→# Specification: Tunnel Scene Geometry (OBJ-019)
     2→
     3→## Summary
     4→
     5→OBJ-019 defines the **tunnel scene geometry** -- the concrete `SceneGeometry` definition registered as `'tunnel'` in the geometry registry. The tunnel arranges five planes (floor, ceiling, left wall, right wall, end wall) into a box-like corridor receding along the negative Z-axis. When the camera pushes forward, walls undergo real perspective distortion -- converging to a vanishing point -- producing the signature 2.5D depth effect described in seed Section 4.2. This is the geometry that demonstrates depthkit's core differentiator: perspective projection that flat 2D parallax cannot replicate.
     6→
     7→## Interface Contract
     8→
     9→### Module Export
    10→
    11→```typescript
    12→// src/scenes/geometries/tunnel.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The tunnel scene geometry definition.
    18→ *
    19→ * Exported for... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "offset": 1,
  "limit": 300
}
[Tool Result]      1→# Specification: Canyon Scene Geometry (OBJ-020)
     2→
     3→## Summary
     4→
     5→OBJ-020 defines the **canyon** scene geometry — a narrow, vertically dramatic 3D space with tall wall planes on left and right, a floor plane, an open sky above, and an optional end wall at depth. The camera pushes forward through the canyon or floats upward to reveal vertical scale. This geometry produces the feeling of traveling through a narrow gorge, alley, corridor between tall buildings, or any space defined by towering vertical boundaries. It registers itself via `registerGeometry()` from OBJ-005 and defines its slot set per OBJ-007's depth model contract.
     6→
     7→## Interface Contract
     8→
     9→### Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/canyon.ts
    13→
    14→import type { SceneGeometry, PlaneSlot, FogConfig } from './types';
    15→import { registerGeometry } from './registry';
    16→```
    17→
    18→The module defines and ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": 1,
  "limit": 300
}
[Tool Result]      1→# Specification: Flyover Scene Geometry (OBJ-021)
     2→
     3→## Summary
     4→
     5→OBJ-021 defines the **flyover** scene geometry — a spatial arrangement designed for aerial/bird's-eye perspective. A large ground plane lies below the camera (`FLOOR` rotation), a sky plane sits at extreme depth above, and optional landmark planes rise vertically from the ground at varying depths and lateral positions. The camera moves forward while positioned above the ground, producing an immersive "flying over terrain" effect where the ground plane undergoes strong perspective foreshortening and landmarks pass by on either side. This geometry registers itself via OBJ-005's `registerGeometry()` and is a Tier 2 geometry.
     6→
     7→## Interface Contract
     8→
     9→### Exported Geometry Definition
    10→
    11→```typescript
    12→// src/scenes/geometries/flyover.ts
    13→
    14→import type { SceneGeometry } from './types';
    15→
    16→/**
    17→ * The flyover scene geometr... [truncated]
Now I have a thorough picture of all four geometry specs. Let me verify a critical claim in the proposal — the canyon sky perspective orientation:

The proposal claims in AC-10: "Canyon `sky` has `perspective: 'bottom_up'` because the canyon sky plane uses rotation `[PI/2, 0, 0]`"

From OBJ-020: canyon sky rotation is indeed `[Math.PI/2, 0, 0]` — confirmed.

Now let me also verify the flyover sky: OBJ-021 says flyover sky rotation is `[0, 0, 0]` (FACING_CAMERA), NOT a ceiling plane. The proposal correctly has flyover sky as `frontal`. Good.

Now let me check the stage geometry's `midground` slot — the proposal claims it inherits the default guidance. But the stage `midground` has `transparent: false` per OBJ-018 line 104. The proposal's stage table doesn't show `midground` as a geometry-specific entry, so the default fallback would apply — and the default has `requiresAlpha: false`. That's consistent.

Let me now do a systematic review:

---

Here's my assessment of the proposed OBJ-051 specification:

## Points of Agreement (What's Sound)

1. **The two-level registry design (D1)** is well-motivated. Default fallback with geometry-specific overrides is the right pattern. Approved.

2. **`PerspectiveOrientation` as an explicit enum (D3)** rather than inferred from rotation — correct call. Approved.

3. **The `cacheCategory` normalization layer (D2)** is necessary and the 9 categories cover verified geometries well. Approved.

4. **Perspective mappings (AC-06 through AC-10)** — I verified against all four geometry specs. The rotation-to-perspective claims are correct, including the non-obvious canyon sky as `bottom_up`. Approved.

5. **Transparency mappings (AC-11–AC-14)** — I cross-checked `transparent` flags across all four geometry specs. Correct. Approved.

6. **The prompt composition formula and rules P1-P4** are the core knowledge artifact and are well-structured. Approved.

7. **Design decision D8** (superseding OBJ-007's `promptGuidance` without modifying OBJ-007) is the right approach. Approved.

---

## Issues

### Issue 1: `getAllGuidanceForGeometry` merge semantics are undefined without geometry slot knowledge (CRITICAL)

**Problem:** The spec says `getAllGuidanceForGeometry('stage')` should return 6 entries — stage-specific entries merged with default fallbacks. But the function has no way to know which slots the stage geometry defines. The function signature takes only `geometryName: string` and has zero imports from `src/spatial/` or `src/scenes/` (per AC-33). 

Open Question 1 acknowledges this problem. But the recommended answer — "accept an optional `slotNames: string[]` parameter" — is buried in an open question, not reflected in the function signature.

Without this, here's what happens:
- Callers like OBJ-072 get a blob of stage-specific + ALL default entries, including defaults for slots that don't exist in the stage geometry (e.g., `back_wall` — stage uses `backdrop` instead). This is actively misleading.
- Or the function only returns geometry-specific entries (no defaults), which breaks the stated behavior.

**Severity:** Critical — the function signature doesn't match the described behavior.

**Proposed fix:** Promote Open Question 1's recommendation (b) into the interface contract. Update the signature:

```typescript
export function getAllGuidanceForGeometry(
  geometryName: string,
  slotNames?: readonly string[]
): ReadonlyMap<string, SlotPromptGuidance>;
```

Document the merge behavior precisely:
- If `slotNames` is provided: return guidance for only those slots (geometry-specific preferred, default fallback).
- If `slotNames` is omitted: return only entries explicitly in the registry for this geometry (no default merge). This is the safe default — callers who want merging must know the slot names.

Update AC-22 and AC-23 to specify that `slotNames` is passed by the caller.

### Issue 2: The stage geometry has `midground` with `transparent: false` but the default taxonomy has `midground` with `requiresAlpha: false` — these match. However, the stage `midground` might sometimes need alpha (MINOR)

The spec's default `midground` has `requiresAlpha: false`. OBJ-018's slot description says "Environmental element between backdrop and subject." This is fine — the geometry says opaque, so the prompt guidance agrees. No actual conflict.

Actually, on review this isn't a real issue. Withdrawn.

### Issue 3: Canyon walls use `side` perspective but have different spatial behavior from tunnel walls (MAJOR)

**Problem:** The proposal maps both canyon `left_wall`/`right_wall` and tunnel `left_wall`/`right_wall` to `perspective: 'side'` and `cacheCategory: 'wall'`. However, the canyon walls are **18 units tall** (towering vertical surfaces) while tunnel walls are **6 units tall** (corridor-height). Canyon walls are visually "cliff faces" while tunnel walls are "corridor panels." A cached wall texture generated for "brick wall corridor panel" (tunnel) would look spatially wrong on a towering canyon cliff.

The semantic cache threshold (0.92) handles *prompt-level* dissimilarity, but the `cacheCategory` being the same means the cache *will* attempt to match them. If someone prompts "stone wall receding into distance" for a tunnel, and then later "stone wall receding into distance" for a canyon, the cache hits — but the image proportions and visual characteristics should be different.

**Severity:** Major — could produce visually incorrect cache reuse at scale.

**Proposed fix:** Two options:
1. Split `wall` category into `wall_corridor` and `wall_cliff` — high specificity but low cache reuse.
2. Keep `wall` as the cache category (maximizing reuse) but document this as a known limitation in the spec, and add to the `perspectiveNotes` for canyon walls that the image should be **vertically oriented/tall** while tunnel wall prompts should emphasize **horizontal elongation**. The prompt difference should naturally push the embeddings apart below the 0.92 threshold.

I recommend option 2 — it's pragmatic and the prompt engineering naturally differentiates them. But the spec must **explicitly document** this design choice and add it to the `perspectiveNotes` for canyon wall guidance, rather than leaving it as an implicit assumption.

### Issue 4: `{subject}` placeholder is underspecified (MAJOR)

**Problem:** The prompt templates use `{subject}` as the sole placeholder. But what does `{subject}` mean in different contexts?

- For a `subject` slot: `{subject}` is the focal element (e.g., "deep sea anglerfish"). Clear.
- For a `sky` slot: the template is `"Expansive {subject} sky..."` — does `{subject}` mean the topic theme? So "Expansive deep sea creatures sky"? That's awkward/wrong.
- For a `floor` slot in a tunnel: `{subject}` would be... "underwater cave"? So "Ancient {subject} floor with scattered shells"? → "Ancient underwater cave floor with scattered shells"? Maybe.

The placeholder semantics are ambiguous. Is `{subject}` the video's overall topic/theme, or the specific content for this slot? The two produce very different prompts.

**Severity:** Major — an LLM consuming these templates needs unambiguous instructions on what to substitute.

**Proposed fix:** 
1. Rename `{subject}` to `{theme}` to indicate it's the video's overall topic/theme, not the slot's specific content.
2. Add a field `placeholderDescription: string` to `SlotPromptGuidance` that explains what the placeholder represents for this specific template.
3. OR: use two placeholders — `{theme}` for the overall video topic and make the templates smart enough that `{theme}` reads naturally in context. E.g., sky template: `"Expansive sky with {theme} atmosphere, wide angle..."` → "Expansive sky with underwater cave atmosphere, wide angle..."

At minimum, add a `placeholderDescription` field or a clear note in the `promptTemplate` documentation about what `{subject}` means per slot type.

### Issue 5: AC-09 — canyon sky `perspective` value needs updating in the stage/default table (MINOR)

**Problem:** AC-09 says "Every slot whose geometry definition uses `FACING_CAMERA` rotation (`[0, 0, 0]`) has `perspective: 'frontal'`. This includes all backdrop, subject, sky (except canyon sky which is `bottom_up`)..."

This parenthetical exception is buried in the middle of AC-09 and makes the criterion harder to verify mechanically. Canyon sky is separately covered by AC-10.

**Proposed fix:** Reword AC-09 to remove the parenthetical and just say "...includes all slots with `[0, 0, 0]` rotation" — then AC-10 handles the canyon sky exception independently.

### Issue 6: The `examplePrompts` and `avoidList` content isn't specified (MAJOR)

**Problem:** AC-27 requires "at least 2 entries in `examplePrompts`." AC-28 requires "at least 1 entry in `avoidList`." AC-29 and AC-30 constrain content quality. But the spec never provides the actual content — only a few inline examples scattered through the rules.

This means every implementer will write different example prompts and avoid lists. For a knowledge artifact, the content IS the deliverable. Geometry slot tables provide `promptTemplate` representatives but not actual `examplePrompts` or `avoidList` content.

**Severity:** Major — the core knowledge artifact is underspecified. Two implementers would produce different prompt registries.

**Proposed fix:** Either:
1. Provide complete `examplePrompts` and `avoidList` for each slot in the spec (this is a lot of content but it's the actual deliverable), OR
2. Provide them for at least the `'default'` taxonomy and tunnel geometry (as reference implementations), and state explicit rules the remaining entries must follow. E.g., "Every `top_down` slot must include one example with 'texture extending into the distance' phrasing and one with 'seamless repeating pattern' phrasing."

I'd accept option 2 — full content for default + tunnel as reference, with structural rules for the rest.

### Issue 7: `resolvePromptGuidance` for stage `midground` — which wins? (MINOR)

**Problem:** The proposal says stage slots that aren't geometry-specifically overridden use defaults. But it also says `SLOT_PROMPT_REGISTRY` contains entries for geometry `'stage'` with "at least the geometry-specific slots: `backdrop`, `floor`." If `midground` is NOT in the stage-specific map, then `resolvePromptGuidance('stage', 'midground')` would fall through to the default. But the stage's `midground` has `transparent: false` — same as default `midground` `requiresAlpha: false`. No conflict here.

But what about `sky`? Stage's sky is `FACING_CAMERA` at `[0, 0, 0]`. Default sky is also `frontal`. So falling through to default is correct. Good.

What about `near_fg`? Stage's `near_fg` is `FACING_CAMERA`, `transparent: true`. Default `near_fg` is `frontal`, `requiresAlpha: true`. Matches. Fine.

Actually, no issue here — just confirming the fallback logic works. Withdrawn.

### Issue 8: Missing guidance for when `flyover_glide` camera is used with ground plane (MINOR)

**Problem:** The flyover's `ground` slot has `perspective: 'top_down'`, but the spec's Rule P1 describes floor textures viewed "at an angle through the perspective camera." With `flyover_glide` (elevated camera, looking down), the ground is viewed much more directly from above than with `slow_push_forward`. The prompt guidance should note this — a texture that works for "receding perspective" may look different when viewed more directly from above.

**Severity:** Minor — `flyover_glide` isn't verified yet, but the guidance should be forward-compatible.

**Proposed fix:** Add a note to the flyover `ground` slot's `perspectiveNotes` that the texture should work well both in receding perspective (forward camera) and more direct top-down view (elevated camera).

### Issue 9: No versioning or extensibility story for `SlotCacheCategory` (MINOR)

**Problem:** `SlotCacheCategory` is a union type with 9 string literals. When OBJ-022–025 add new geometries, they might need new categories (e.g., panorama might need `'panoramic_surface'`). The spec's OQ-4 mentions this but doesn't define what happens to the type when a new category is added.

**Severity:** Minor — it's a simple union type that can be extended.

**Proposed fix:** Add a sentence in the extensibility section: "New categories are added to the `SlotCacheCategory` union type. Existing cache entries are unaffected — new categories are additive. Adding a category is a minor change, not a breaking change."

### Issue 10: AC-15's `end_wall → 'backdrop'` mapping needs justification in the spec body (MINOR)

**Problem:** AC-15 lists `end_wall→'backdrop'`. Open Question 3 discusses this, but the recommendation is in the OQ section, not a design decision. The actual decision should be stated authoritatively.

**Proposed fix:** Move OQ-3's recommendation into a design decision (or into the `cacheCategory` discussion in the tables). State: "end_wall maps to 'backdrop' because end walls and backdrops serve visually similar roles (distant vistas, atmospheric scenes), maximizing cache reuse."

---

## Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | `getAllGuidanceForGeometry` merge semantics undefined without slot knowledge | Critical | Needs fix |
| 3 | Canyon walls vs tunnel walls share `cacheCategory: 'wall'` without differentiation guidance | Major | Needs documentation |
| 4 | `{subject}` placeholder semantics ambiguous across slot types | Major | Needs fix |
| 6 | `examplePrompts` and `avoidList` content unspecified | Major | Needs at least reference implementations |
| 5 | AC-09 parenthetical exception for canyon sky | Minor | Cleanup |
| 8 | Flyover ground needs forward-compatible perspective notes | Minor | Additive |
| 9 | No extensibility note for `SlotCacheCategory` | Minor | Additive |
| 10 | `end_wall→'backdrop'` mapping justification misplaced | Minor | Move from OQ to decision |

Please address the critical (#1) and major (#3, #4, #6) issues. The minors can be folded in during revision.

---

## Round 3 — spec_author

Thank you for the thorough review. All issues are valid. Let me address each one and present the revised specification.

---

# Revised Specification: OBJ-051 — Image Generation Strategy: Flux.1 Schnell Prompt Engineering Per Slot Type

## Summary

OBJ-051 defines the **image generation prompt engineering strategy** for depthkit — the prompt templates, perspective-aware prompting rules, transparency handling guidelines, and per-slot-type generation guidance that enable an LLM to produce Flux.1 Schnell image prompts that are spatially appropriate for each slot in each geometry. This is a knowledge artifact with a thin programmatic interface: a `SlotPromptGuidance` type system and a `SLOT_PROMPT_REGISTRY` data structure that maps `(geometry, slot_name)` pairs to structured prompt guidance. It is consumed by OBJ-072 (SKILL.md prompt templates section), OBJ-054 (semantic caching middleware — uses `slot_type` categorization for cache queries), and indirectly by any LLM authoring pipeline that needs to generate images for a manifest.

## Interface Contract

### Core Types

```typescript
// src/prompts/types.ts

/**
 * Perspective orientation of the generated image.
 * Controls prompt engineering to match how the plane is
 * rotated in 3D space.
 *
 * - 'frontal': Image viewed straight-on (camera-facing planes).
 *   Standard composition. Used for backdrops, subjects, end walls.
 *
 * - 'top_down': Image viewed from above, mapped onto a floor plane
 *   (rotation [-PI/2, 0, 0]). Texture should look correct when
 *   viewed in perspective from a forward-looking or downward-angled
 *   camera. NOT a bird's-eye map — the texture is stretched along
 *   the depth axis by perspective projection.
 *
 * - 'bottom_up': Image viewed from below, mapped onto a ceiling
 *   plane (rotation [PI/2, 0, 0]). Similar to top_down but inverted.
 *
 * - 'side': Image viewed from the side, mapped onto a wall plane
 *   (rotation [0, ±PI/2, 0]). Texture recedes to a vanishing point
 *   along one axis. Horizontally repeating/seamless textures work best.
 */
export type PerspectiveOrientation = 'frontal' | 'top_down' | 'bottom_up' | 'side';

/**
 * Canonical slot categories for the semantic cache.
 * These map to the AssetLibrary.slot_type column (OBJ-053).
 *
 * Multiple geometry-specific slot names may map to the same
 * category (e.g., tunnel's 'left_wall' and canyon's 'left_wall'
 * both map to 'wall'), enabling cross-geometry cache reuse.
 *
 * This union is additive-only: new geometries (OBJ-022–025) may
 * introduce new categories. Adding a category is a non-breaking
 * change — existing cache entries are unaffected.
 */
export type SlotCacheCategory =
  | 'sky'
  | 'backdrop'
  | 'floor'
  | 'ceiling'
  | 'wall'
  | 'midground'
  | 'subject'
  | 'foreground'
  | 'landmark';

/**
 * Structured prompt guidance for a single slot within a geometry.
 *
 * This is the core data type that OBJ-051 produces. Each entry
 * provides everything an LLM needs to craft a Flux.1 Schnell prompt
 * for a specific slot in a specific geometry context.
 */
export interface SlotPromptGuidance {
  /**
   * The slot name within the geometry.
   * Must match the geometry's registered slot key.
   */
  readonly slotName: string;

  /**
   * The geometry this guidance applies to, or 'default' for
   * guidance that applies to the default slot taxonomy
   * (used when no geometry-specific override exists).
   */
  readonly geometryName: string;

  /**
   * How the plane is oriented in 3D space.
   * Drives the perspective-aware prompting rules.
   */
  readonly perspective: PerspectiveOrientation;

  /**
   * Whether the generated image should have a transparent
   * background (alpha channel). Maps to DepthSlot.expectsAlpha
   * from OBJ-007.
   */
  readonly requiresAlpha: boolean;

  /**
   * A reusable prompt suffix/instruction for requesting transparency.
   * Empty string if requiresAlpha is false.
   * Example: ", isolated on transparent background, PNG"
   */
  readonly alphaSuffix: string;

  /**
   * General description of what kind of image content belongs in
   * this slot. 1-2 sentences.
   */
  readonly contentDescription: string;

  /**
   * Concrete prompt template with a `{theme}` placeholder.
   * The LLM substitutes the video's overall topic/theme.
   *
   * `{theme}` is the video's topic (e.g., "underwater caves",
   * "ancient Rome", "jazz history") — NOT the specific content
   * for this slot. The template is written so that {theme} reads
   * naturally as a thematic modifier. See `themeUsageNote` for
   * per-slot guidance on how {theme} integrates.
   */
  readonly promptTemplate: string;

  /**
   * Explains how {theme} is used in this slot's template.
   * Helps the LLM understand whether {theme} modifies style,
   * setting, content, or atmosphere.
   *
   * Example: "The {theme} modifies the atmosphere and color
   * palette of the sky, not the sky's content itself."
   */
  readonly themeUsageNote: string;

  /**
   * Perspective-specific prompting instructions. Explains WHY
   * the prompt is structured this way and what to avoid.
   * Critical for non-frontal orientations where naive prompting
   * produces images that look wrong on rotated planes.
   * May be empty string for 'frontal' orientation slots where
   * no special perspective considerations apply.
   */
  readonly perspectiveNotes: string;

  /**
   * 2-3 concrete example prompts demonstrating correct usage
   * for different topics/themes. Each example shows {theme}
   * already substituted with a specific topic.
   */
  readonly examplePrompts: readonly string[];

  /**
   * Things to explicitly avoid in prompts for this slot.
   * Anti-patterns that produce poor results.
   */
  readonly avoidList: readonly string[];

  /**
   * The normalized slot category for semantic caching (OBJ-054).
   * Maps potentially geometry-specific slot names to a canonical
   * category for the AssetLibrary's slot_type column.
   *
   * This enables cross-geometry cache sharing: a 'floor' texture
   * generated for a tunnel can be reused for a canyon's 'floor'
   * because they share the same cache category.
   */
  readonly cacheCategory: SlotCacheCategory;
}
```

### Registry Structure

```typescript
// src/prompts/slot-prompt-registry.ts

import type { SlotPromptGuidance, SlotCacheCategory } from './types';

/**
 * The complete registry of prompt guidance for all geometry/slot
 * combinations.
 *
 * Structure: Map<geometryName, Map<slotName, SlotPromptGuidance>>
 *
 * Includes a 'default' geometry key for the default slot taxonomy
 * (OBJ-007's DEFAULT_SLOT_TAXONOMY). Geometry-specific entries
 * override defaults when both exist for the same slot name.
 */
export const SLOT_PROMPT_REGISTRY: ReadonlyMap<
  string,
  ReadonlyMap<string, SlotPromptGuidance>
>;

/**
 * Resolves the prompt guidance for a specific geometry + slot
 * combination.
 *
 * Resolution order:
 * 1. If SLOT_PROMPT_REGISTRY has an entry for (geometryName, slotName),
 *    return it.
 * 2. Else if SLOT_PROMPT_REGISTRY has an entry for ('default', slotName),
 *    return it.
 * 3. Else return undefined — the caller must handle the missing case.
 *
 * @param geometryName - The geometry name (e.g., 'tunnel', 'stage').
 * @param slotName - The slot name within that geometry.
 * @returns The resolved SlotPromptGuidance, or undefined if no
 *   guidance exists for this combination.
 */
export function resolvePromptGuidance(
  geometryName: string,
  slotName: string
): SlotPromptGuidance | undefined;

/**
 * Returns prompt guidance for a given geometry, scoped to the
 * provided slot names.
 *
 * For each slot name in `slotNames`:
 * - If a geometry-specific entry exists, use it.
 * - Else if a default entry exists, use it.
 * - Else the slot is omitted from the result.
 *
 * This scoping is necessary because this module does not import
 * the geometry registry (AC-33) and therefore cannot know which
 * slots a geometry defines. Callers (OBJ-072, OBJ-056) obtain
 * the slot list from the geometry registry and pass it here.
 *
 * @param geometryName - The geometry name.
 * @param slotNames - The slot names to include. Typically obtained
 *   from the geometry's registered slot set.
 * @returns Map of slotName -> SlotPromptGuidance for the requested
 *   slots that have guidance available. Slots with no guidance
 *   (geometry-specific or default) are omitted.
 */
export function getGuidanceForSlots(
  geometryName: string,
  slotNames: readonly string[]
): ReadonlyMap<string, SlotPromptGuidance>;

/**
 * Returns the cache category for a given geometry + slot combination.
 * Convenience wrapper around resolvePromptGuidance().cacheCategory.
 *
 * Used by OBJ-054 (semantic caching middleware) to determine the
 * slot_type for AssetLibrary queries.
 *
 * @returns The SlotCacheCategory, or undefined if no guidance exists.
 */
export function getCacheCategory(
  geometryName: string,
  slotName: string
): SlotCacheCategory | undefined;
```

### Module Exports

```typescript
// src/prompts/index.ts (barrel export)

export type {
  PerspectiveOrientation,
  SlotPromptGuidance,
  SlotCacheCategory,
} from './types';

export {
  SLOT_PROMPT_REGISTRY,
  resolvePromptGuidance,
  getGuidanceForSlots,
  getCacheCategory,
} from './slot-prompt-registry';
```

### Prompt Guidance Data — Reference Implementations

The registry must contain entries for the following geometries and slots. The **default taxonomy** and **tunnel geometry** entries are provided in full as reference implementations. Stage, canyon, and flyover entries must follow the same structure and content quality standards.

#### Default Taxonomy (geometry = `'default'`) — Full Reference

```typescript
// Provided in full as the reference implementation.
// All other entries must match this level of content quality.

{
  slotName: 'sky',
  geometryName: 'default',
  perspective: 'frontal',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Sky, space, distant gradient. Large plane filling the far background. Should be atmospheric and expansive with no foreground objects.',
  promptTemplate: 'Expansive {theme} sky, wide angle, atmospheric, no foreground objects, cinematic lighting, vibrant colors',
  themeUsageNote: '{theme} sets the atmosphere and color palette of the sky. For "underwater caves" this becomes a deep ocean gradient; for "ancient Rome" a Mediterranean sunset.',
  perspectiveNotes: '',
  examplePrompts: [
    'Expansive deep ocean sky gradient, dark blue fading to teal, bioluminescent particles scattered, wide angle, atmospheric, no foreground objects, cinematic lighting',
    'Expansive ancient Roman sunset sky, warm golden and orange hues, wispy clouds, Mediterranean atmosphere, wide angle, no foreground objects, cinematic',
    'Expansive cosmic nebula sky, deep purple and blue starfield, distant galaxies, wide angle, atmospheric, no foreground objects, cinematic lighting',
  ],
  avoidList: [
    'Foreground objects, trees, buildings, or any ground-level elements',
    'Horizon lines with terrain (the 3D scene provides its own horizon)',
    'Text or logos',
    'Narrow or cropped compositions — sky planes are very large',
  ],
  cacheCategory: 'sky',
}

{
  slotName: 'back_wall',
  geometryName: 'default',
  perspective: 'frontal',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Distant landscape, city skyline, or environmental backdrop at medium depth. Slightly hazy to convey atmospheric perspective.',
  promptTemplate: 'Distant {theme} landscape, atmospheric perspective, slightly hazy, wide composition, cinematic depth',
  themeUsageNote: '{theme} defines the environment type. For "jazz history" this becomes a city skyline; for "space exploration" a distant planet surface.',
  perspectiveNotes: '',
  examplePrompts: [
    'Distant coral reef landscape, atmospheric underwater haze, blue-green tones, wide composition, cinematic depth, soft ambient light',
    'Distant ancient Roman cityscape, marble columns and temples on horizon, golden hour haze, wide composition, atmospheric perspective',
    'Distant mountain range silhouette, layers of atmospheric haze, purple and blue tones, wide panoramic composition',
  ],
  avoidList: [
    'Close-up details or textures (this is a distant element)',
    'Foreground framing elements',
    'Strong focal subjects that compete with the subject slot',
  ],
  cacheCategory: 'backdrop',
}

{
  slotName: 'midground',
  geometryName: 'default',
  perspective: 'frontal',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Environmental element at middle distance — buildings, terrain features, props. Bridges the gap between backdrop and subject.',
  promptTemplate: 'Mid-distance {theme} environmental element, natural setting, moderate detail, atmospheric lighting',
  themeUsageNote: '{theme} determines what kind of environmental feature appears. For "cooking basics" this might be a kitchen counter; for "deep sea creatures" a coral formation.',
  perspectiveNotes: '',
  examplePrompts: [
    'Mid-distance coral reef formation, colorful sea fans and anemones, moderate detail, soft underwater lighting, natural ocean setting',
    'Mid-distance Roman forum ruins, broken columns and archways, golden afternoon light, moderate detail',
    'Mid-distance jazz club interior elements, tables and chairs in soft focus, warm ambient lighting, smoky atmosphere',
  ],
  avoidList: [
    'Isolated subjects on transparent backgrounds (that is the subject slot)',
    'Full-scene panoramas (that is the backdrop slot)',
    'Elements that would look wrong without ground contact — use subject slot for standing figures',
  ],
  cacheCategory: 'midground',
}

{
  slotName: 'subject',
  geometryName: 'default',
  perspective: 'frontal',
  requiresAlpha: true,
  alphaSuffix: ', isolated on transparent background, PNG',
  contentDescription: 'Primary focal element — person, creature, object. Always on transparent background. This is what the viewer looks at.',
  promptTemplate: '{theme} focal subject, dramatic lighting, high detail, isolated on transparent background, PNG',
  themeUsageNote: '{theme} IS the subject content here. For "deep sea anglerfish" the theme directly describes what to generate. The LLM should adapt {theme} to name the specific subject.',
  perspectiveNotes: '',
  examplePrompts: [
    'Deep sea anglerfish with bioluminescent lure glowing blue, dramatic underwater lighting, high detail, isolated on transparent background, PNG',
    'Roman centurion in full armor, dramatic side lighting, oil painting style, high detail, isolated on transparent background, PNG',
    'Jazz saxophone player mid-performance, warm spotlight, dynamic pose, high detail, isolated on transparent background, PNG',
  ],
  avoidList: [
    'Backgrounds of any kind — must be transparent/alpha',
    'Multiple subjects competing for attention',
    'Text, labels, or watermarks',
    'Full-body shots where feet are cut off (the plane has a bottom edge)',
  ],
  cacheCategory: 'subject',
}

{
  slotName: 'near_fg',
  geometryName: 'default',
  perspective: 'frontal',
  requiresAlpha: true,
  alphaSuffix: ', isolated on transparent background, PNG',
  contentDescription: 'Foreground framing elements close to camera — particles, foliage, atmospheric effects. Always transparent. Often slightly blurred.',
  promptTemplate: 'Foreground {theme} particles and atmospheric elements, scattered, bokeh, transparent background, PNG',
  themeUsageNote: '{theme} flavors the particle/atmospheric type. For "underwater caves" these are bubbles and sediment; for "space" these are dust motes and lens flares.',
  perspectiveNotes: '',
  examplePrompts: [
    'Foreground underwater bubbles and floating sediment particles, scattered, bokeh blur, soft blue tint, transparent background, PNG',
    'Foreground autumn leaves and dust motes, scattered, warm golden bokeh, transparent background, PNG',
    'Foreground musical notes and smoke wisps, scattered, warm amber bokeh, transparent background, PNG',
  ],
  avoidList: [
    'Opaque backgrounds — this MUST be transparent',
    'Solid objects that would fully occlude the scene behind them',
    'Centered compositions — these elements should be scattered across the frame edges',
    'Text or readable symbols',
  ],
  cacheCategory: 'foreground',
}
```

#### Tunnel Geometry (geometry = `'tunnel'`) — Full Reference

```typescript
{
  slotName: 'floor',
  geometryName: 'tunnel',
  perspective: 'top_down',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Ground surface texture for a corridor/tunnel floor. Viewed at a steep angle through perspective projection — the near end is stretched wide, the far end compressed to a vanishing point.',
  promptTemplate: '{theme} ground surface texture, extending into the distance, top-down perspective, seamless repeating pattern, cinematic lighting',
  themeUsageNote: '{theme} sets the material/environment. For "underwater caves" this becomes "ancient ocean floor stone"; for "sci-fi corridor" this becomes "metallic grating panels".',
  perspectiveNotes: 'CRITICAL: This texture is mapped onto a horizontal plane (rotation [-PI/2, 0, 0]) and viewed through a perspective camera. The projection stretches the near end and compresses the far end. Prompts MUST request textures with repeating/seamless patterns that tolerate this distortion. Avoid centered focal-point compositions — there should be no single "hero" element. Avoid horizon lines within the image (the 3D scene creates its own). Request elongated or top-down perspective textures.',
  examplePrompts: [
    'Ancient ocean floor with scattered shells and coral fragments, wet stone texture extending into the distance, top-down perspective, seamless repeating pattern, teal and dark blue tones, cinematic lighting',
    'Worn cobblestone dungeon floor, moss in cracks, damp surface reflecting torchlight, top-down perspective, seamless repeating stone pattern, dark medieval tones',
    'Futuristic metallic floor panels with glowing grid lines, brushed steel texture, top-down perspective, seamless repeating pattern, blue-white accent lighting',
  ],
  avoidList: [
    'Centered focal compositions — no single "hero" element in the middle',
    'Horizon lines within the image',
    'Eye-level perspective photos of floors (need top-down or receding angle)',
    'Highly detailed unique patterns that break when perspective-stretched',
    'Text, symbols, or directional markings that distort under projection',
  ],
  cacheCategory: 'floor',
}

{
  slotName: 'ceiling',
  geometryName: 'tunnel',
  perspective: 'bottom_up',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Overhead surface texture for a tunnel ceiling. Viewed from below through perspective projection with the same distortion characteristics as the floor.',
  promptTemplate: '{theme} overhead ceiling texture, looking upward, seamless repeating pattern, atmospheric lighting',
  themeUsageNote: '{theme} sets the overhead environment. For "underwater caves" this becomes "cave ceiling with stalactites"; for "gothic cathedral" this becomes "vaulted stone arches".',
  perspectiveNotes: 'Same projection distortion as top_down but inverted — viewed from below. Textures should be seamless and repeating. Avoid images with sky or ground — the ceiling IS the overhead enclosure. Architectural overhead textures (beams, pipes, cave formations, vaulted ceilings) work best.',
  examplePrompts: [
    'Underwater cave ceiling with stalactites and mineral deposits, looking upward, bioluminescent patches, seamless repeating rocky texture, dark atmospheric lighting',
    'Industrial tunnel ceiling with pipes and exposed wiring, looking upward, rusted metal beams, seamless repeating pattern, harsh fluorescent lighting',
    'Ancient stone vault ceiling with carved reliefs, looking upward, torch-lit shadows, seamless repeating architectural pattern, warm amber tones',
  ],
  avoidList: [
    'Sky or open air — this is an enclosed overhead surface',
    'Ground-level or eye-level perspectives',
    'Centered focal compositions',
    'Horizon lines',
  ],
  cacheCategory: 'ceiling',
}

{
  slotName: 'left_wall',
  geometryName: 'tunnel',
  perspective: 'side',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Wall surface texture for a corridor wall. Recedes to a vanishing point along the depth axis. Should be horizontally elongated and seamless.',
  promptTemplate: '{theme} wall surface texture, extending into the distance, horizontal elongation, seamless repeating pattern, corridor-scale proportions',
  themeUsageNote: '{theme} sets the wall material/environment. For "underwater caves" this becomes "cave wall with mineral veins"; for "spaceship" this becomes "bulkhead panels". Tunnel walls are corridor-height (compact), not cliff-face-tall.',
  perspectiveNotes: 'Wall planes are rotated [0, PI/2, 0] and recede to the vanishing point. The near end of the wall is stretched wide; the far end compresses. Horizontally seamless/tileable textures prevent visible seaming at the near edge. Avoid text, signage, or asymmetric details that become distorted or illegible under perspective. Avoid strong vertical center compositions. Tunnel walls are corridor-scale (~4 units tall) — prompt for enclosed, human-scale wall surfaces, not towering cliff faces.',
  examplePrompts: [
    'Underwater cave wall with mineral veins and embedded crystals, rock texture extending into the distance, horizontal striations, seamless repeating pattern, bioluminescent accent, dark teal tones',
    'Dungeon stone wall with iron torch sconces, rough-hewn blocks, horizontal elongation, seamless repeating masonry pattern, warm torchlight glow',
    'Spaceship corridor bulkhead panels, riveted metal plates, horizontal elongation, seamless repeating industrial pattern, cool blue accent lighting',
  ],
  avoidList: [
    'Text, signage, or readable symbols',
    'Asymmetric details that look wrong when mirrored on the opposite wall',
    'Strong vertical center compositions',
    'Vertically tall/cliff-face compositions — tunnel walls are corridor-height',
    'Window-like openings (breaks the enclosed tunnel illusion)',
  ],
  cacheCategory: 'wall',
}

{
  slotName: 'right_wall',
  geometryName: 'tunnel',
  perspective: 'side',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Right corridor wall. Same spatial characteristics as left_wall. Often the same image is used for both walls for symmetry, or a complementary image with matching style.',
  promptTemplate: '{theme} wall surface texture, extending into the distance, horizontal elongation, seamless repeating pattern, corridor-scale proportions',
  themeUsageNote: 'Same as left_wall. Often the same image or a stylistically matching variant. If using different images, ensure matching palette and material density.',
  perspectiveNotes: 'Same as left_wall. Wall is rotated [0, -PI/2, 0] (mirrored). Same seamless/elongation requirements. If using the same image as left_wall, the visual symmetry enhances the corridor effect.',
  examplePrompts: [
    'Underwater cave wall with smooth water-worn stone, mineral deposits, horizontal elongation, seamless repeating pattern, matching teal and dark blue tones',
    'Dungeon stone wall with drainage channels, rough-hewn blocks matching opposite wall, horizontal elongation, seamless repeating masonry pattern',
    'Spaceship corridor panel wall, matching industrial style, riveted metal, seamless repeating pattern, cool blue accent lighting',
  ],
  avoidList: [
    'Text, signage, or readable symbols',
    'Dramatically different style/palette from left_wall',
    'Strong vertical center compositions',
    'Vertically tall/cliff-face compositions — tunnel walls are corridor-height',
  ],
  cacheCategory: 'wall',
}

{
  slotName: 'end_wall',
  geometryName: 'tunnel',
  perspective: 'frontal',
  requiresAlpha: false,
  alphaSuffix: '',
  contentDescription: 'Distant terminus at the far end of the tunnel — the vanishing point target. Heavily fog-faded by default, so high-contrast or bright images read best.',
  promptTemplate: 'Distant {theme} terminus, bright focal point, high contrast, glowing light source or distant vista, atmospheric',
  themeUsageNote: '{theme} defines what lies at the end of the tunnel. For "underwater caves" this is a glowing underwater grotto; for "sci-fi" this is a portal or distant starfield. Should be luminous — fog will heavily fade it.',
  perspectiveNotes: '',
  examplePrompts: [
    'Distant underwater grotto with bioluminescent glow, turquoise light emanating from cave opening, high contrast, ethereal atmosphere',
    'Distant light at end of stone dungeon corridor, warm golden torchlight, high contrast against darkness, atmospheric haze',
    'Distant portal of swirling energy, bright blue-white glow, sci-fi terminus, high contrast, atmospheric light rays',
  ],
  avoidList: [
    'Subtle or low-contrast images (fog will make them invisible)',
    'Complex detailed scenes (too small at distance to read)',
    'Dark images without a bright focal element',
  ],
  cacheCategory: 'backdrop',
}
```

#### Stage Geometry (geometry = `'stage'`) — Content Requirements

The stage-specific entries override defaults for slots with different spatial behavior. Slots not listed use the default taxonomy fallback.

| Slot | perspective | requiresAlpha | cacheCategory | Geometry-specific or default | Content requirements |
|------|------------|---------------|---------------|-----|------|
| `backdrop` | `frontal` | `false` | `backdrop` | **Geometry-specific** | Full-scene background for a stage setup. Wide, atmospheric. No foreground. Must include `examplePrompts` showing stage-appropriate wide backdrops (e.g., panoramic landscape, interior room, abstract gradient). Must include `avoidList` entry about avoiding foreground elements. |
| `sky` | `frontal` | `false` | `sky` | Default fallback | Uses default `sky` guidance. |
| `floor` | `top_down` | `false` | `floor` | **Geometry-specific** | Stage floor surface. Same perspective rules as tunnel floor (Rule P1), but the `perspectiveNotes` should note that the stage floor is shallower (less depth extension) than the tunnel floor — textures with moderate repetition work well. Must include `themeUsageNote` explaining that stage floors are "room floors or ground surfaces" (not corridors). |
| `midground` | `frontal` | `false` | `midground` | Default fallback | Uses default `midground` guidance. |
| `subject` | `frontal` | `true` | `subject` | Default fallback | Uses default `subject` guidance. |
| `near_fg` | `frontal` | `true` | `foreground` | Default fallback | Uses default `near_fg` guidance. |

Must produce: 2 geometry-specific entries (`backdrop`, `floor`), with the remaining 4 slots served by default fallbacks. Each geometry-specific entry must meet the same content quality standards as the reference implementations (≥2 example prompts, ≥1 avoid list entry, etc.).

#### Canyon Geometry (geometry = `'canyon'`) — Content Requirements

| Slot | perspective | requiresAlpha | cacheCategory | Content requirements |
|------|------------|---------------|---------------|------|
| `sky` | `bottom_up` | `false` | `sky` | **Geometry-specific** (different perspective from default sky). Narrow strip of sky between towering walls. Must note in `perspectiveNotes` that this is a ceiling-mounted plane looking downward — prompt for "sky viewed from bottom of a canyon/gorge, looking upward." |
| `left_wall` | `side` | `false` | `wall` | **Geometry-specific**. Must differentiate from tunnel walls in `perspectiveNotes`: canyon walls are towering cliff faces (~14 units tall vs tunnel's ~4 units), so prompt for **vertically dramatic, tall surfaces** — cliff faces, building facades, vertical rock formations. This prompt differentiation naturally pushes embeddings apart from tunnel wall prompts, preventing inappropriate cache reuse at the 0.92 threshold. |
| `right_wall` | `side` | `false` | `wall` | **Geometry-specific**. Same as canyon `left_wall` with matching/complementary style guidance. |
| `floor` | `top_down` | `false` | `floor` | **Geometry-specific**. Canyon floor is a narrow path/gorge bottom, distinct from tunnel's wider corridor floor. `perspectiveNotes` should emphasize narrow, constrained ground surfaces. |
| `end_wall` | `frontal` | `false` | `backdrop` | Default fallback or geometry-specific. Distant vista at canyon's end. |
| `subject` | `frontal` | `true` | `subject` | Default fallback. Scale note: `perspectiveNotes` should mention the subject should feel small relative to the canyon walls. If geometry-specific, add this note; if default, this guidance can be documented in SKILL.md (OBJ-072) instead. |

#### Flyover Geometry (geometry = `'flyover'`) — Content Requirements

| Slot | perspective | requiresAlpha | cacheCategory | Content requirements |
|------|------------|---------------|---------------|------|
| `sky` | `frontal` | `false` | `sky` | Default fallback | 
| `ground` | `top_down` | `false` | `floor` | **Geometry-specific**. Vast terrain from above. `perspectiveNotes` must note that the flyover camera is elevated and may view the ground more directly from above than a standard forward-looking camera — textures should work in both strong receding perspective AND a more direct overhead view. Prompt for sprawling natural terrain patterns (fields, forests, ocean, desert). |
| `landmark_far` | `frontal` | `true` | `landmark` | **Geometry-specific**. Distant landmark rising from terrain. Transparent background. Small and atmospheric. |
| `landmark_left` | `frontal` | `true` | `landmark` | **Geometry-specific**. Left-side landmark. Transparent. Vertical feature. |
| `landmark_right` | `frontal` | `true` | `landmark` | **Geometry-specific**. Right-side landmark. Transparent. Complementary style. |
| `near_fg` | `frontal` | `true` | `foreground` | Default fallback or geometry-specific. If geometry-specific, emphasize speed/altitude (clouds, birds, wind particles). |

### Perspective-Aware Prompting Rules

These are the core knowledge artifact — the rules that transform naive prompts into spatially correct ones.

#### Rule P1: `top_down` (Floor/Ground Planes)

Floor and ground planes are rotated `[-PI/2, 0, 0]` and viewed at an angle through the perspective camera. The texture is stretched along the depth axis (Z after rotation). Naive prompts like "a beautiful stone floor" produce images with eye-level composition that look wrong when projected onto a horizontal plane.

**Prompt strategy:**
- Request textures with a **receding perspective** or **top-down view**: "stone path extending into the distance", "top-down view of forest floor", "cobblestone road in perspective"
- Use **repeating/seamless patterns** that tolerate stretching: tiles, planks, gravel, water ripples, grass
- Avoid **centered focal-point compositions** — there should be no single "hero" element in the center
- Avoid **horizon lines** within the image — the 3D scene provides its own horizon
- Request **wide aspect ratios** or compositions that read well when stretched horizontally

**Why this matters:** The perspective projection matrix compresses the far end of a floor texture into a narrow band near the horizon and expands the near end to fill the bottom of the frame. Images with centered compositions produce a visible "sweet spot" that breaks the illusion.

#### Rule P2: `bottom_up` (Ceiling Planes)

Ceiling planes are rotated `[PI/2, 0, 0]`. Similar constraints to `top_down` but inverted.

**Prompt strategy:**
- Request **overhead/architectural textures** viewed from below: "cave ceiling with stalactites, looking upward", "industrial pipes and beams overhead"
- Same seamless/repeating requirements as floor
- Avoid images with sky or horizon — the ceiling IS the overhead enclosure

#### Rule P3: `side` (Wall Planes)

Wall planes are rotated `[0, ±PI/2, 0]` and recede to a vanishing point along the Z-axis.

**Prompt strategy:**
- Request **elongated horizontal textures**: "brick wall extending into the distance", "rock face with horizontal striations"
- **Horizontally seamless/tileable** textures prevent visible seaming at the near edge
- Avoid **text, signage, or asymmetric details** that become distorted
- **Scale matters:** corridor-height walls (tunnel) should prompt for enclosed, human-scale surfaces; towering walls (canyon) should prompt for dramatic cliff faces and vertical scale

#### Rule P4: `frontal` (Camera-Facing Planes)

Camera-facing planes have no rotation. Standard composition rules apply.

**Prompt strategy:**
- For **subjects**: request transparent background ("isolated on transparent background, PNG")
- For **backdrops**: request wide, atmospheric scenes without foreground elements
- For **end walls**: request high-contrast images readable through fog

### Transparency Handling Guidelines

#### Guideline T1: When to Request Alpha

Request transparent backgrounds for slots where `requiresAlpha: true`:
- **Subjects** (all geometries): always.
- **Foreground elements** (`near_fg`, atmospheric particles): always.
- **Landmarks** (flyover's `landmark_far`, `landmark_left`, `landmark_right`): always.

Do NOT request for slots where `requiresAlpha: false`:
- Sky/backdrop planes: fill frame edge-to-edge.
- Floor/ceiling/wall textures: fill their plane completely.

#### Guideline T2: Prompt Phrasing for Transparency

Flux.1 Schnell responds best to explicit transparency instructions:
- **Strong**: `", isolated on transparent background, PNG"` (use this — it is the standard `alphaSuffix`)
- **Medium**: `", on transparent background"`
- **Weak** (avoid): `", no background"` (often produces white/gray)

#### Guideline T3: Fallback When Alpha Fails

When Flux.1 produces an image without alpha despite the request:
- The asset pipeline (OBJ-054) applies **background removal** (rembg or equivalent) as post-processing for any slot where `requiresAlpha: true`
- Categories `subject`, `foreground`, and `landmark` always get background removal if no alpha channel is detected
- Categories `sky`, `backdrop`, `floor`, `ceiling`, `wall`, `midground` never need background removal

### Prompt Composition Formula

```
[content description specific to the topic, substituting {theme}]
+ [perspective-orientation keywords from the guidance]
+ [style/mood modifiers for the video's overall aesthetic]
+ [alphaSuffix if requiresAlpha]
```

## Design Decisions

### D1: Two-level registry with default fallback

The registry uses `(geometry, slot)` lookup with a `'default'` geometry fallback. Slots with the same name and spatial behavior across geometries (e.g., `subject`) share default guidance. Geometries with unique spatial requirements override (e.g., tunnel `floor` vs stage `floor` have different depth extensions). New geometries get reasonable guidance for standard slot names automatically via defaults.

**Alternatives considered:** (a) Flat `geometryName:slotName` key — no fallback, requires duplication. (b) Single slot-name-only map — ignores geometry context. The two-level approach balances specificity with DRY.

### D2: `cacheCategory` normalizes slot names for cross-geometry caching

OBJ-054 queries the AssetLibrary filtered by `slot_type`. Without normalization, flyover's `ground` (functionally equivalent to `floor`) would miss cache entries from tunnel/canyon/stage floors. The 9 categories cover all verified geometries.

`end_wall` maps to `'backdrop'` because end walls and backdrops serve visually similar roles (distant vistas, atmospheric scenes), maximizing cache reuse. The semantic similarity threshold (0.92) handles cases where content diverges.

**Extensibility:** `SlotCacheCategory` is a union type. New geometries may introduce new categories (additive, non-breaking change). Existing cache entries are unaffected.

### D3: `PerspectiveOrientation` is explicit, not inferred from rotation

Inferring perspective from Euler angles is fragile (multiple rotations produce the same orientation). Making it explicit ensures prompt engineering advice is grounded in human-understandable spatial reasoning.

### D4: `{theme}` placeholder with `themeUsageNote`

**Addresses challenger's Issue #4.** The placeholder is renamed from `{subject}` to `{theme}` to clarify it represents the video's overall topic, not the slot's content. Each `SlotPromptGuidance` includes a `themeUsageNote` explaining how `{theme}` integrates into that specific template — e.g., for a sky slot, `{theme}` modifies atmosphere; for a subject slot, `{theme}` names the focal element directly.

Single placeholder keeps templates simple. The LLM adapts `{theme}` per slot context guided by `themeUsageNote`. Multiple placeholders (theme + content + style) were rejected — LLMs compose better with a simple template and contextual guidance than with multi-slot grammar.

### D5: `getGuidanceForSlots` requires caller-provided slot names

**Addresses challenger's Issue #1.** The original `getAllGuidanceForGeometry` could not know which slots a geometry defines without importing the geometry registry (violating AC-33). The renamed `getGuidanceForSlots` accepts a `slotNames` parameter. Callers (OBJ-072, OBJ-056) obtain the slot list from the geometry registry and pass it. This keeps `src/prompts/` self-contained while producing correctly scoped results.

### D6: Canyon vs tunnel wall differentiation via prompt engineering, not cache category split

**Addresses challenger's Issue #3.** Canyon walls (~14 units tall, cliff faces) and tunnel walls (~4 units tall, corridor panels) share `cacheCategory: 'wall'`. Rather than splitting into `wall_corridor` / `wall_cliff` (which reduces cache reuse), the differentiation is handled by prompt engineering: canyon wall `perspectiveNotes` explicitly instruct prompting for "towering, vertically dramatic" surfaces while tunnel wall notes instruct "corridor-scale, compact." This prompt differentiation naturally produces embeddings that diverge below the 0.92 threshold, preventing inappropriate reuse.

This is documented explicitly in the canyon wall guidance entries rather than left as an implicit assumption.

### D7: Reference implementations for default + tunnel, structural rules for the rest

**Addresses challenger's Issue #6.** Full `SlotPromptGuidance` objects are provided for all 5 default slots and all 5 tunnel slots (10 total reference implementations). Stage, canyon, and flyover entries are specified as content requirements tables with specific constraints, but not full verbatim objects — the implementer authors them following the reference pattern. Structural rules enforce quality:
- Every `top_down` slot must include `examplePrompts` with "extending into the distance" or "seamless repeating pattern" phrasing
- Every `side` slot must include `examplePrompts` with "horizontal elongation" or "seamless" phrasing
- Every slot must meet the acceptance criteria for content quality (AC-24–AC-30)

### D8: This module supersedes OBJ-007's `promptGuidance` and geometry-specific guidance

OBJ-007's `DEFAULT_SLOT_TAXONOMY` and geometry specs (OBJ-018–021) include preliminary `promptGuidance` strings. OBJ-051's `SLOT_PROMPT_REGISTRY` supersedes all of them as the single source of truth for image generation prompting. Downstream consumers (OBJ-072, OBJ-054) import from `src/prompts/`, not from `promptGuidance` fields on spatial types. The spatial module's fields remain for backwards compatibility and in-module documentation.

### D9: Module is self-contained — no imports from spatial or geometry modules

Per AC-33, `src/prompts/` does not import from `src/spatial/` or `src/scenes/`. The perspective and requiresAlpha values are authored based on knowledge of the geometry specs, verified against them via acceptance criteria, but not computed from them at runtime. This prevents circular dependencies and keeps the prompt module deployable independently of the rendering engine.

## Acceptance Criteria

### Registry Completeness

- [ ] **AC-01:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'default'` with exactly 5 slots: `sky`, `back_wall`, `midground`, `subject`, `near_fg`.
- [ ] **AC-02:** `SLOT_PROMPT_REGISTRY` contains geometry-specific entries for `'stage'` with at least: `backdrop`, `floor`. Other stage slots (`sky`, `midground`, `subject`, `near_fg`) are served by default fallbacks.
- [ ] **AC-03:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'tunnel'` with exactly 5 slots: `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`.
- [ ] **AC-04:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'canyon'` with at least: `sky`, `left_wall`, `right_wall`, `floor`. (Other slots may be geometry-specific or default fallback.)
- [ ] **AC-05:** `SLOT_PROMPT_REGISTRY` contains entries for geometry `'flyover'` with at least: `ground`, `landmark_far`, `landmark_left`, `landmark_right`. (Other slots may be geometry-specific or default fallback.)

### Perspective Correctness

- [ ] **AC-06:** Every slot whose geometry definition uses `FLOOR` rotation (`[-PI/2, 0, 0]`) has `perspective: 'top_down'`. Includes: stage `floor`, tunnel `floor`, canyon `floor`, flyover `ground`.
- [ ] **AC-07:** Every slot whose geometry definition uses `CEILING` rotation (`[PI/2, 0, 0]`) has `perspective: 'bottom_up'`. Includes: tunnel `ceiling`.
- [ ] **AC-08:** Every slot whose geometry definition uses `LEFT_WALL` or `RIGHT_WALL` rotation has `perspective: 'side'`. Includes: tunnel `left_wall`/`right_wall`, canyon `left_wall`/`right_wall`.
- [ ] **AC-09:** Every slot whose geometry definition uses `FACING_CAMERA` rotation (`[0, 0, 0]`) has `perspective: 'frontal'`.
- [ ] **AC-10:** Canyon `sky` has `perspective: 'bottom_up'` (rotation `[PI/2, 0, 0]` per OBJ-020).

### Alpha/Transparency

- [ ] **AC-11:** Every entry with `requiresAlpha: true` has a non-empty `alphaSuffix` containing the phrase "transparent background".
- [ ] **AC-12:** Every entry with `requiresAlpha: false` has `alphaSuffix` equal to `""`.
- [ ] **AC-13:** `requiresAlpha` is `true` for all slots where the corresponding geometry definition has `transparent: true` / `expectsAlpha: true`. Includes: default/stage `subject`, default/stage `near_fg`, canyon `subject`, flyover `landmark_far`, `landmark_left`, `landmark_right`, flyover `near_fg`.
- [ ] **AC-14:** `requiresAlpha` is `false` for all sky, backdrop, floor, ceiling, wall, end_wall, and ground slots.

### Cache Categories

- [ ] **AC-15:** `cacheCategory` mappings: sky→`'sky'`; backdrop/back_wall→`'backdrop'`; floor/ground→`'floor'`; ceiling→`'ceiling'`; left_wall/right_wall→`'wall'`; midground→`'midground'`; subject→`'subject'`; near_fg→`'foreground'`; landmark_far/landmark_left/landmark_right→`'landmark'`; end_wall→`'backdrop'`.
- [ ] **AC-16:** `getCacheCategory('tunnel', 'left_wall')` returns `'wall'`. `getCacheCategory('canyon', 'left_wall')` also returns `'wall'`.
- [ ] **AC-17:** `getCacheCategory('flyover', 'ground')` returns `'floor'`.

### Resolution Functions

- [ ] **AC-18:** `resolvePromptGuidance('tunnel', 'floor')` returns tunnel-specific guidance (verified by `geometryName === 'tunnel'`).
- [ ] **AC-19:** `resolvePromptGuidance('stage', 'subject')` returns guidance (default fallback, `geometryName === 'default'`).
- [ ] **AC-20:** `resolvePromptGuidance('unknown_geometry', 'sky')` returns default `sky` guidance.
- [ ] **AC-21:** `resolvePromptGuidance('unknown_geometry', 'unknown_slot')` returns `undefined`.
- [ ] **AC-22:** `getGuidanceForSlots('tunnel', ['floor', 'ceiling', 'left_wall', 'right_wall', 'end_wall'])` returns a map with 5 entries, all tunnel-specific.
- [ ] **AC-23:** `getGuidanceForSlots('stage', ['backdrop', 'sky', 'floor', 'midground', 'subject', 'near_fg'])` returns 6 entries — `backdrop` and `floor` are stage-specific, the rest are default fallbacks.
- [ ] **AC-24:** `getGuidanceForSlots('stage', ['backdrop', 'sky', 'nonexistent_slot'])` returns 2 entries (`backdrop`, `sky`). `nonexistent_slot` is omitted (no guidance available).

### Content Quality

- [ ] **AC-25:** Every `SlotPromptGuidance` entry has a non-empty `contentDescription`.
- [ ] **AC-26:** Every `SlotPromptGuidance` entry has a non-empty `promptTemplate` containing the `{theme}` placeholder.
- [ ] **AC-27:** Every `SlotPromptGuidance` entry has a non-empty `themeUsageNote`.
- [ ] **AC-28:** Every entry with `perspective` !== `'frontal'` has a non-empty `perspectiveNotes`.
- [ ] **AC-29:** Every `SlotPromptGuidance` entry has at least 2 entries in `examplePrompts`.
- [ ] **AC-30:** Every `SlotPromptGuidance` entry has at least 1 entry in `avoidList`.
- [ ] **AC-31:** No `examplePrompts` entry for a `top_down` perspective slot contains horizon lines, centered compositions, or eye-level viewpoints.
- [ ] **AC-32:** No `examplePrompts` entry for a `side` perspective slot contains text, signage, or strongly vertical center compositions.
- [ ] **AC-33:** Canyon wall entries' `perspectiveNotes` explicitly mention "towering" or "vertically dramatic" and contrast with "corridor-scale" tunnel walls.

### Module Structure

- [ ] **AC-34:** All types and functions are accessible via `src/prompts/index.ts` barrel export.
- [ ] **AC-35:** The module has zero runtime dependencies beyond standard JavaScript built-ins (Map, string operations).
- [ ] **AC-36:** The module does NOT import from `src/spatial/` or `src/scenes/`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `resolvePromptGuidance` for a geometry that exists but a slot that doesn't | Returns `undefined`. No error thrown. |
| `resolvePromptGuidance` for `('default', 'some_slot')` where `some_slot` is not in default taxonomy | Returns `undefined`. |
| `getGuidanceForSlots` with an empty `slotNames` array | Returns empty `Map`. |
| `getGuidanceForSlots` with slot names that have no guidance | Those slots omitted from result. |
| `getGuidanceForSlots` for an unknown geometry with default-taxonomy slot names | Returns default entries for matching slots. |
| `getCacheCategory` for unknown geometry/slot | Returns `undefined`. |
| Same slot name, different geometries, different `perspective` | Expected — canyon `sky` is `bottom_up`, default `sky` is `frontal`. Geometry-specific entry takes precedence. |
| Stage `floor` and tunnel `floor` share `cacheCategory: 'floor'` | Correct — cross-geometry cache reuse is intentional. Semantic threshold handles content divergence. |
| Canyon wall and tunnel wall share `cacheCategory: 'wall'` | Correct. Prompt engineering differentiation (cliff face vs corridor panel) produces sufficiently divergent embeddings. Documented in D6 and canyon wall `perspectiveNotes`. |
| `{theme}` not substituted in template | Templates are documentation consumed by LLMs. Substitution is the caller's responsibility. Missing substitution is a pipeline bug. |

## Test Strategy

### Unit Tests

**resolvePromptGuidance:**
1. Known geometry + known slot → returns specific guidance (verify `geometryName` field).
2. Unknown geometry + known default slot → returns default guidance (`geometryName === 'default'`).
3. Known geometry + unknown slot → returns `undefined`.
4. Unknown geometry + unknown slot → returns `undefined`.
5. Geometry-specific entry overrides default for same slot name.

**getGuidanceForSlots:**
1. `('tunnel', ['floor', 'ceiling', 'left_wall', 'right_wall', 'end_wall'])` → map with 5 tunnel-specific entries.
2. `('stage', ['backdrop', 'sky', 'floor', 'midground', 'subject', 'near_fg'])` → map with 6 entries (2 stage-specific + 4 defaults).
3. `('stage', ['backdrop', 'nonexistent'])` → map with 1 entry.
4. Unknown geometry + default slot names → default entries returned.
5. Any geometry + empty array → empty map.

**getCacheCategory:**
1. `('tunnel', 'left_wall')` → `'wall'`.
2. `('canyon', 'left_wall')` → `'wall'`.
3. `('flyover', 'ground')` → `'floor'`.
4. `('tunnel', 'end_wall')` → `'backdrop'`.
5. Unknown combination → `undefined`.

**Registry content validation (static assertions):**
1. Every entry's `perspective` matches corresponding geometry rotation (AC-06–AC-10).
2. Every entry's `requiresAlpha` matches geometry's transparency flag (AC-13, AC-14).
3. Every entry has non-empty `contentDescription`, `promptTemplate` with `{theme}`, `themeUsageNote`, `examplePrompts` (≥2), `avoidList` (≥1).
4. Every non-frontal entry has non-empty `perspectiveNotes`.
5. Every `requiresAlpha: true` entry has non-empty `alphaSuffix`.
6. Canyon wall `perspectiveNotes` reference vertical scale differentiation (AC-33).

### Relevant Testable Claims

- **TC-04** (partial): Prompt templates enable "no manual 3D positioning" — LLMs use slot names and templates, never coordinates.
- **TC-08** (partial): Cache categories support the geometry coverage goal by normalizing slot names.

## Integration Points

### Depends on

| Upstream | What OBJ-051 imports/references |
|---|---|
| **OBJ-007** (Depth model) | **Referenced, not imported.** `DEFAULT_SLOT_TAXONOMY` slot names, `promptGuidance`, and `expectsAlpha` inform default guidance content. OBJ-051 supersedes OBJ-007's `promptGuidance` as the definitive source. |
| **OBJ-018** (Stage geometry) | **Referenced, not imported.** Slot names, rotations, transparency flags inform stage entries. |
| **OBJ-019** (Tunnel geometry) | **Referenced, not imported.** `tunnelSlotGuidance` content incorporated and expanded. |
| **OBJ-020** (Canyon geometry) | **Referenced, not imported.** Slot metadata informs canyon entries. |
| **OBJ-021** (Flyover geometry) | **Referenced, not imported.** Slot descriptions inform flyover entries. |

### Consumed by

| Downstream | How it uses OBJ-051 |
|---|---|
| **OBJ-054** (Semantic caching middleware) | Calls `getCacheCategory(geometry, slot)` for AssetLibrary `slot_type` queries. Uses `requiresAlpha` to determine background removal post-processing. |
| **OBJ-072** (SKILL.md prompt templates) | Calls `getGuidanceForSlots()` to auto-generate prompt template documentation. Surfaces `promptTemplate`, `themeUsageNote`, `examplePrompts`, `avoidList`, `perspectiveNotes`. |
| **OBJ-056** (Manifest generation via Claude API) | References prompt templates and perspective rules to compose Flux.1 prompts. |

### File Placement

```
depthkit/
  src/
    prompts/
      index.ts                    # Barrel export
      types.ts                    # PerspectiveOrientation, SlotPromptGuidance,
                                  #   SlotCacheCategory
      slot-prompt-registry.ts     # SLOT_PROMPT_REGISTRY, resolvePromptGuidance,
                                  #   getGuidanceForSlots, getCacheCategory
```

## Open Questions

1. **Should the module also define "style modifier" templates?** E.g., "cinematic documentary", "watercolor illustration" — consistent style tags appended to all prompts. **Recommendation:** Defer to OBJ-072. Style modifiers are a SKILL.md concern, not a slot-spatial concern.

2. **How should this module evolve when OBJ-022–025 are verified?** Each new geometry spec defines its slot names and rotations. The implementer adds entries to `SLOT_PROMPT_REGISTRY` following the reference pattern. Map to existing `cacheCategory` where possible; introduce new categories only for fundamentally novel spatial roles. No architectural change needed — the registry is designed for extension.

3. **Should `perspectiveNotes` be required for `frontal` slots?** Currently it may be empty string for frontal slots (no special perspective considerations). Could require notes even for frontal to remind about backdrop vs subject composition differences. **Recommendation:** Keep optional for frontal — the `contentDescription` and `avoidList` carry this guidance sufficiently. Non-frontal slots are where the perspective-specific knowledge is critical.

---

I believe this revision addresses all the challenger's issues:

- **Issue #1 (Critical):** `getAllGuidanceForGeometry` → renamed to `getGuidanceForSlots` with required `slotNames` parameter. Updated all ACs.
- **Issue #3 (Major):** Canyon wall differentiation explicitly documented in D6, canyon wall content requirements table, and AC-33.
- **Issue #4 (Major):** `{subject}` → `{theme}`. Added `themeUsageNote` field with per-slot usage explanation. Updated all templates and examples.
- **Issue #6 (Major):** Full reference implementations for default (5 slots) and tunnel (5 slots). Structural rules and content requirements tables for stage/canyon/flyover.
- **Issue #5 (Minor):** AC-09 cleaned up — no parenthetical exception.
- **Issue #8 (Minor):** Flyover `ground` content requirements note about direct overhead view.
- **Issue #9 (Minor):** Extensibility note added to `SlotCacheCategory` type doc and D2.
- **Issue #10 (Minor):** `end_wall→'backdrop'` justification moved from OQ to D2.

I'd like the Challenger to verify these changes and assess whether the spec is ready for approval.

---

## Round 4 — spec_challenger

I'll verify each of my original objections against the revised spec.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Write,Bash",
  "max_results": 4
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me verify the canyon geometry spec to confirm the sky rotation claim in AC-10, and check the flyover spec for its sky and ground slot details.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-020/output.md",
  "offset": 30,
  "limit": 120
}
[Tool Result]     30→
    31→| Slot | Position | Rotation | Size | Required | transparent | fogImmune | renderOrder | Description |
    32→|------|----------|----------|------|----------|-------------|-----------|-------------|-------------|
    33→| `sky` | `[0, 12, -20]` | `[Math.PI/2, 0, 0]` | `[12, 56]` | `true` | `false` | `true` | 0 | Open sky visible above the canyon walls. Horizontal plane facing downward, positioned high above the canyon floor. fogImmune because sky should remain vivid regardless of depth fog. |
    34→| `left_wall` | `[-4, 3, -20]` | `[0, Math.PI/2, 0]` | `[56, 18]` | `true` | `false` | `false` | 1 | Left canyon wall. Tall vertical plane facing right. Width (56) extends deep along Z to prevent edge reveal during forward camera push including gentle_float backward drift margin. Height (18) provides vertical drama. |
    35→| `right_wall` | `[4, 3, -20]` | `[0, -Math.PI/2, 0]` | `[56, 18]` | `true` | `false` | `false` | 1 | Right canyon wall. Tall vertical plane facing left.... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-021/output.md",
  "offset": 30,
  "limit": 120
}
[Tool Result]     30→ *
    31→ * Best suited for landscape, environment, and travel themes.
    32→ * Designed primarily for 16:9 landscape orientation where
    33→ * the wide frame emphasizes the panoramic ground coverage.
    34→ */
    35→export const flyoverGeometry: SceneGeometry;
    36→```
    37→
    38→### Geometry Fields
    39→
    40→| Field | Value | Rationale |
    41→|-------|-------|-----------|
    42→| `name` | `'flyover'` | Matches seed Section 4.2 naming |
    43→| `description` | `'Aerial bird\'s-eye view. Large ground plane below with perspective foreshortening, sky backdrop above, and optional landmark elements rising from the terrain. Camera glides forward for a flyover effect. Best for landscapes, travel, and environment themes.'` | Describes the spatial feel per OBJ-005's `description` contract |
    44→| `default_camera` | `'slow_push_forward'` | The only verified forward-motion camera preset (OBJ-027). Produces a valid flyover-like effect with ground foreshortening. Whe... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-018/output.md",
  "offset": 30,
  "limit": 120
}
[Tool Result]     30→ */
    31→export const stageGeometry: SceneGeometry;
    32→```
    33→
    34→### Geometry Fields
    35→
    36→| Field | Value | Rationale |
    37→|-------|-------|-----------|
    38→| `name` | `'stage'` | Matches seed Section 4.2 naming |
    39→| `description` | `'A classic subject-in-front-of-background setup. Large backdrop at depth, angled floor plane with real perspective foreshortening, and a subject plane at shallow Z. The most versatile geometry for general-purpose scenes.'` | Describes the spatial feel per OBJ-005's `description` contract |
    40→| `default_camera` | `'slow_push_forward'` | Seed Section 4.2: "Camera pushes in or drifts laterally." Forward push is the defining 2.5D motion. |
    41→| `compatible_cameras` | `['static', 'slow_push_forward', 'slow_pull_back', 'lateral_track_left', 'lateral_track_right', 'gentle_float', 'dramatic_push', 'crane_up']` | Stage supports most camera motions except geometry-specific ones (tunnel_push_forward, flyover_glide... [truncated]
Good. I've now verified all geometry specs against the proposal's claims. Let me do my systematic verification:

## Verification of All Prior Issues

### Issue #1 (Critical) — `getAllGuidanceForGeometry` merge semantics: **VERIFIED FIXED.**
- Function renamed to `getGuidanceForSlots` with required `slotNames: readonly string[]` parameter ✓
- Documentation explicitly states callers obtain slot list from geometry registry ✓
- AC-22, AC-23, AC-24 all pass `slotNames` ✓
- Edge case for empty `slotNames` documented ✓

### Issue #3 (Major) — Canyon vs tunnel wall differentiation: **VERIFIED FIXED.**
- D6 explicitly documents the design choice ✓
- Tunnel wall reference implementation includes "corridor-scale proportions" in `promptTemplate` and "Vertically tall/cliff-face compositions — tunnel walls are corridor-height" in `avoidList` ✓
- Canyon content requirements table says "towering, vertically dramatic" ✓
- AC-33 requires canyon wall `perspectiveNotes` to mention vertical scale differentiation ✓

### Issue #4 (Major) — `{subject}` placeholder: **VERIFIED FIXED.**
- Renamed to `{theme}` throughout ✓
- New `themeUsageNote` field on `SlotPromptGuidance` with clear per-slot docs ✓
- AC-27 (renumbered from original) requires non-empty `themeUsageNote` ✓
- All 10 reference implementations include meaningful `themeUsageNote` values ✓
- The subject slot's `themeUsageNote` correctly explains the special case where `{theme}` IS the content ✓

### Issue #6 (Major) — Missing content: **VERIFIED FIXED.**
- Full reference implementations for all 5 default taxonomy slots ✓
- Full reference implementations for all 5 tunnel slots ✓
- Content requirements tables with specific constraints for stage, canyon, flyover ✓
- D7 documents the structural rules the remaining entries must follow ✓

### Minor issues #5, #8, #9, #10: All verified addressed.

## New Checks on the Revised Spec

**Perspective mapping verification against actual geometry specs:**
- Canyon `sky` rotation: `[Math.PI/2, 0, 0]` → `bottom_up` — AC-10 correct ✓
- Flyover `sky` rotation: `[0, 0, 0]` → `frontal` — correct ✓
- Flyover `ground` rotation: `[-Math.PI/2, 0, 0]` → `top_down` — AC-06 correct ✓
- Stage `floor` rotation: `[-Math.PI/2, 0, 0]` → `top_down` — AC-06 correct ✓
- Stage `subject` transparent: `true` → `requiresAlpha: true` — AC-13 correct ✓
- Flyover `near_fg` transparent: `true` → `requiresAlpha: true` — AC-13 correct ✓
- Canyon `end_wall` required: `false` per OBJ-020 — spec's AC-04 says "at least: sky, left_wall, right_wall, floor" which correctly omits it from required geometry-specific entries ✓

**One observation:** Stage geometry has `midground` with `transparent: false` but the stage doesn't use default taxonomy's midground (which also has `expectsAlpha: false` / `requiresAlpha: false`). The fallback works correctly here. ✓

**Canyon `subject` scale guidance:** The content requirements table says "Default fallback or geometry-specific. Scale note: `perspectiveNotes` should mention the subject should feel small relative to the canyon walls." This is guidance for the implementer but isn't enforced by any AC. Minor — acceptable as implementation guidance.

The spec is solid. All critical and major issues are resolved. The content quality of the reference implementations is high. The interface is precise and implementable. The downstream consumers (OBJ-054, OBJ-072) have clear integration paths.

CONCLUSION:

The specification for OBJ-051 (Image Generation Strategy — Flux.1 Schnell Prompt Engineering Per Slot Type) is approved. The spec defines:

1. **A `SlotPromptGuidance` type system** with perspective orientation, alpha requirements, cache categories, prompt templates with `{theme}` placeholder, and `themeUsageNote` per-slot context.
2. **A `SLOT_PROMPT_REGISTRY`** with two-level resolution (geometry-specific → default fallback) covering all 4 verified geometries plus the default taxonomy.
3. **`getGuidanceForSlots()`** requiring caller-provided slot names to avoid geometry-registry coupling.
4. **Perspective-aware prompting rules** (P1–P4) for top_down, bottom_up, side, and frontal orientations.
5. **Full reference implementations** for 10 slots (5 default + 5 tunnel) with content requirements tables for stage/canyon/flyover.
6. **Cache category normalization** mapping geometry-specific slot names to 9 canonical categories for OBJ-054.
7. **Canyon vs tunnel wall differentiation** handled via prompt engineering (documented in D6 and AC-33).
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md",
  "content": "# Specification: Image Generation Strategy \u2014 Flux.1 Schnell Prompt Engineering Per Slot Type (OBJ-051)\n\n## Summary\n\nOBJ-051 defines the **image generation prompt engineering strategy** for depthkit \u2014 the prompt templates, perspective-aware prompting rules, transparency handling guidelines, and per-slot-type generation guidance that enable an LLM to produce Flux.1 Schnell image prompts that are spatially appropriate for each slot in each geometry. This is a knowledge artifact with a thin programmatic interface: a `SlotPromptGuidance` type system and a `SLOT_PROMPT_REGISTRY` data structure that maps `(geometry, slot_name)` pairs to structured prompt guidance. It is consumed by OBJ-072 (SKILL.md prompt templates section), OBJ-054 (semantic caching middleware \u2014 uses `slot_type` categorization for cache queries), and indirectly by any LLM authoring pipeline that needs to generate images for a manifest.\n\n## Interface Contract\n\n### Core Types\n\n```typescript\n// src/prompts/types.ts\n\n/**\n * Perspective orientation of the generated image.\n * Controls prompt engineering to match how the plane is\n * rotated in 3D space.\n *\n * - 'frontal': Image viewed straight-on (camera-facing planes).\n *   Standard composition. Used for backdrops, subjects, end walls.\n *\n * - 'top_down': Image viewed from above, mapped onto a floor plane\n *   (rotation [-PI/2, 0, 0]). Texture should look correct when\n *   viewed in perspective from a forward-looking or downward-angled\n *   camera. NOT a bird's-eye map \u2014 the texture is stretched along\n *   the depth axis by perspective projection.\n *\n * - 'bottom_up': Image viewed from below, mapped onto a ceiling\n *   plane (rotation [PI/2, 0, 0]). Similar to top_down but inverted.\n *\n * - 'side': Image viewed from the side, mapped onto a wall plane\n *   (rotation [0, \u00b1PI/2, 0]).
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-051",
     3→  "description": "Image generation strategy -- Flux.1 Schnell prompt engineering per slot type per Section 4.7. Perspective-aware prompting for floor/wall/ceiling textures (e.g., tunnel floor needs a perspective-correct ground texture). Prompt templates for far_bg, mid_bg, midground, subject, and near_fg slots. Guidelines for transparency requests in prompts.",
     4→  "category": "integration",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-007"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 4 integration. Medium priority. Informs SKILL.md prompt templates (OBJ-072) and semantic caching (OBJ-054)."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/meta.json",
  "content": "{\n  \"id\": \"OBJ-051\",\n  \"description\": \"Image generation strategy -- Flux.1 Schnell prompt engineering per slot type per Section 4.7. Perspective-aware prompting for floor/wall/ceiling textures (e.g., tunnel floor needs a perspective-correct ground texture). Prompt templates with {theme} placeholder for all slot types across verified geometries. Guidelines for transparency requests. Cache category normalization for semantic caching (OBJ-054).\",\n  \"category\": \"integration\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T00:00:00Z\",\n  \"depends_on\": [\"OBJ-007\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 4 integration. Medium priority. Informs SKILL.md prompt templates (OBJ-072) and semantic caching (OBJ-054). Spec defines SlotPromptGuidance type, SLOT_PROMPT_REGISTRY with two-level resolution (geometry-specific -> default fallback), perspective-aware prompting rules (P1-P4), transparency guidelines (T1-T3), and cache category normalization. Full reference implementations for default taxonomy (5 slots) and tunnel geometry (5 slots). Content requirements tables for stage, canyon, flyover.\",\n  \"status\": \"specified\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-051/meta.json has been updated successfully.

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-051/output.md nodes/OBJ-051/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-051): image generation strategy \u2014 prompt engineering per slot type\n\nDefines SlotPromptGuidance type system, SLOT_PROMPT_REGISTRY with\ntwo-level resolution (geometry-specific -> default fallback),\nperspective-aware prompting rules (P1-P4 for top_down/bottom_up/\nside/frontal), transparency guidelines (T1-T3), and cache category\nnormalization for OBJ-054 semantic caching. Full reference\nimplementations for default taxonomy (5 slots) and tunnel (5 slots).\nContent requirements for stage, canyon, flyover geometries.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-051 spec and updated meta.json"
}
[Tool Result] [master 873fead] spec(OBJ-051): image generation strategy — prompt engineering per slot type
 2 files changed, 846 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-051/output.md
The specification for OBJ-051 has been written to disk and committed. 

**Summary of the deliberation:**

- **Round 1:** Proposer submitted initial spec with `SlotPromptGuidance` type, `SLOT_PROMPT_REGISTRY`, and prompt guidance for all 4 verified geometries.
- **Round 2:** I identified 1 critical issue (`getAllGuidanceForGeometry` merge semantics undefined without geometry slot knowledge), 3 major issues (canyon/tunnel wall cache differentiation, `{subject}` placeholder ambiguity, missing example content), and 4 minor issues.
- **Round 3:** Proposer addressed all issues — renamed function to `getGuidanceForSlots` with required `slotNames` param, renamed placeholder to `{theme}` with `themeUsageNote`, added full reference implementations for 10 slots, documented canyon wall differentiation in D6 and AC-33.
- **Round 4:** I verified all fixes against the actual geometry specs (OBJ-018–021), confirmed perspective mappings and transparency flags are correct, and converged.
