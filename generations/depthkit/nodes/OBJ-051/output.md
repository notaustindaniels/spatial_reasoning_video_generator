# Specification: Image Generation Strategy — Flux.1 Schnell Prompt Engineering Per Slot Type (OBJ-051)

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
 * the geometry registry (AC-36) and therefore cannot know which
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

Must produce: 2 geometry-specific entries (`backdrop`, `floor`), with the remaining 4 slots served by default fallbacks. Each geometry-specific entry must meet the same content quality standards as the reference implementations (>=2 example prompts, >=1 avoid list entry, etc.).

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
| `sky` | `frontal` | `false` | `sky` | Default fallback. |
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

Wall planes are rotated `[0, +/-PI/2, 0]` and recede to a vanishing point along the Z-axis.

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

The placeholder is named `{theme}` (not `{subject}`) to clarify it represents the video's overall topic, not the slot's content. Each `SlotPromptGuidance` includes a `themeUsageNote` explaining how `{theme}` integrates into that specific template — e.g., for a sky slot, `{theme}` modifies atmosphere; for a subject slot, `{theme}` names the focal element directly.

Single placeholder keeps templates simple. The LLM adapts `{theme}` per slot context guided by `themeUsageNote`. Multiple placeholders (theme + content + style) were rejected — LLMs compose better with a simple template and contextual guidance than with multi-slot grammar.

### D5: `getGuidanceForSlots` requires caller-provided slot names

The function accepts a `slotNames` parameter because this module does not import the geometry registry (AC-36) and cannot know which slots a geometry defines. Callers (OBJ-072, OBJ-056) obtain the slot list from the geometry registry and pass it. This keeps `src/prompts/` self-contained while producing correctly scoped results.

### D6: Canyon vs tunnel wall differentiation via prompt engineering, not cache category split

Canyon walls (~14 units tall, cliff faces) and tunnel walls (~4 units tall, corridor panels) share `cacheCategory: 'wall'`. Rather than splitting into `wall_corridor` / `wall_cliff` (which reduces cache reuse), the differentiation is handled by prompt engineering: canyon wall `perspectiveNotes` explicitly instruct prompting for "towering, vertically dramatic" surfaces while tunnel wall notes instruct "corridor-scale, compact." This prompt differentiation naturally produces embeddings that diverge below the 0.92 threshold, preventing inappropriate reuse.

This is documented explicitly in the canyon wall guidance entries rather than left as an implicit assumption.

### D7: Reference implementations for default + tunnel, structural rules for the rest

Full `SlotPromptGuidance` objects are provided for all 5 default slots and all 5 tunnel slots (10 total reference implementations). Stage, canyon, and flyover entries are specified as content requirements tables with specific constraints, but not full verbatim objects — the implementer authors them following the reference pattern. Structural rules enforce quality:
- Every `top_down` slot must include `examplePrompts` with "extending into the distance" or "seamless repeating pattern" phrasing
- Every `side` slot must include `examplePrompts` with "horizontal elongation" or "seamless" phrasing
- Every slot must meet the acceptance criteria for content quality (AC-25–AC-33)

### D8: This module supersedes OBJ-007's `promptGuidance` and geometry-specific guidance

OBJ-007's `DEFAULT_SLOT_TAXONOMY` and geometry specs (OBJ-018–021) include preliminary `promptGuidance` strings. OBJ-051's `SLOT_PROMPT_REGISTRY` supersedes all of them as the single source of truth for image generation prompting. Downstream consumers (OBJ-072, OBJ-054) import from `src/prompts/`, not from `promptGuidance` fields on spatial types. The spatial module's fields remain for backwards compatibility and in-module documentation.

### D9: Module is self-contained — no imports from spatial or geometry modules

Per AC-36, `src/prompts/` does not import from `src/spatial/` or `src/scenes/`. The perspective and requiresAlpha values are authored based on knowledge of the geometry specs, verified against them via acceptance criteria, but not computed from them at runtime. This prevents circular dependencies and keeps the prompt module deployable independently of the rendering engine.

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

- [ ] **AC-15:** `cacheCategory` mappings: sky->`'sky'`; backdrop/back_wall->`'backdrop'`; floor/ground->`'floor'`; ceiling->`'ceiling'`; left_wall/right_wall->`'wall'`; midground->`'midground'`; subject->`'subject'`; near_fg->`'foreground'`; landmark_far/landmark_left/landmark_right->`'landmark'`; end_wall->`'backdrop'`.
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
1. Known geometry + known slot -> returns specific guidance (verify `geometryName` field).
2. Unknown geometry + known default slot -> returns default guidance (`geometryName === 'default'`).
3. Known geometry + unknown slot -> returns `undefined`.
4. Unknown geometry + unknown slot -> returns `undefined`.
5. Geometry-specific entry overrides default for same slot name.

**getGuidanceForSlots:**
1. `('tunnel', ['floor', 'ceiling', 'left_wall', 'right_wall', 'end_wall'])` -> map with 5 tunnel-specific entries.
2. `('stage', ['backdrop', 'sky', 'floor', 'midground', 'subject', 'near_fg'])` -> map with 6 entries (2 stage-specific + 4 defaults).
3. `('stage', ['backdrop', 'nonexistent'])` -> map with 1 entry.
4. Unknown geometry + default slot names -> default entries returned.
5. Any geometry + empty array -> empty map.

**getCacheCategory:**
1. `('tunnel', 'left_wall')` -> `'wall'`.
2. `('canyon', 'left_wall')` -> `'wall'`.
3. `('flyover', 'ground')` -> `'floor'`.
4. `('tunnel', 'end_wall')` -> `'backdrop'`.
5. Unknown combination -> `undefined`.

**Registry content validation (static assertions):**
1. Every entry's `perspective` matches corresponding geometry rotation (AC-06–AC-10).
2. Every entry's `requiresAlpha` matches geometry's transparency flag (AC-13, AC-14).
3. Every entry has non-empty `contentDescription`, `promptTemplate` with `{theme}`, `themeUsageNote`, `examplePrompts` (>=2), `avoidList` (>=1).
4. Every non-frontal entry has non-empty `perspectiveNotes`.
5. Every `requiresAlpha: true` entry has non-empty `alphaSuffix`.
6. Canyon wall `perspectiveNotes` reference vertical scale differentiation (AC-33).

### Relevant Testable Claims

- **TC-04** (partial): The prompt templates are part of enabling "no manual 3D positioning" — the LLM uses slot names and prompt templates, never raw coordinates.
- **TC-08** (partial): The cache categories support the 8-geometry coverage goal by normalizing slot names across geometries.

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
