# Deliberation Transcript: OBJ-015

---

## Round 1 — spec_author

I'll start by reviewing the relevant files to understand the current state of the project before proposing the spec.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]


Let me examine the current project state and relevant dependency outputs.
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-015/**/*"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-010/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json
/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/transcript.md

[Tool: Glob]
  Input: {
  "pattern": "src/page/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/engine/page-types*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/spatial/types*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "src/**/*.ts"
}

[Tool: Glob]
  Input: {
  "pattern": "src/**/*.js"
}
[Tool Result] No files found
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-005/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-003/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: Scene Geometry Type Contract (OBJ-005)
     2→
     3→## Summary
     4→
     5→OBJ-005 defines the TypeScript type system for all scene geometries in depthkit: the `PlaneSlot` interface describing a single named position in a 3D scene, the `SceneGeometry` interface describing a complete spatial arrangement of planes, the `FogConfig` interface for depth-based atmospheric fading, a geometry registry with explicit registration and deep-freeze semantics, and the slot naming conventions that all 8 geometry implementations (OBJ-018 through OBJ-025) must follow. This is a pure type/contract module — it defines the shape of geometry data, not any specific geometry's values. It imports spatial primitives from OBJ-003 and is consumed by every downstream objective that creates, validates, instantiates, or queries scene geometries.
     6→
     7→## Interface Contract
     8→
     9→### Core Types
    10→
    11→```typescript
    12→// src/scenes/geometries/types.ts
    13... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: Coordinate System and Spatial Math Reference (OBJ-003)
     2→
     3→## Summary
     4→
     5→OBJ-003 codifies the spatial foundation for all depthkit geometry and camera work: the Three.js right-handed coordinate conventions, the relationship between camera FOV / distance and visible area, plane sizing math, and utility functions for computing spatial relationships. This module is a pure-math reference library with zero rendering dependencies — it exports constants, types, and deterministic computation functions that every downstream geometry definition (OBJ-005), camera path preset (OBJ-006), easing/interpolation module (OBJ-007), scene sequencer (OBJ-010), and edge-reveal validator (OBJ-040) will import.
     6→
     7→## Interface Contract
     8→
     9→### Constants
    10→
    11→```typescript
    12→// src/spatial/constants.ts
    13→
    14→/** Three.js right-handed coordinate system conventions */
    15→export const AXIS = {
    16→  RIGHT: [1, 0, 0... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": 100,
  "limit": 150
}
[Tool Result]    100→}
   101→
   102→/**
   103→ * A complete scene geometry definition — the 3D spatial structure
   104→ * of a scene type. Each geometry defines which planes exist, their
   105→ * positions/rotations in 3D space, and which depth slots map to
   106→ * which planes (seed Section 8.6).
   107→ *
   108→ * Geometries are registered by name and looked up at validation time
   109→ * and at render time. The LLM author selects a geometry name and maps
   110→ * images to its named slots; the geometry handles all 3D positioning
   111→ * internally (seed C-06, AP-03).
   112→ *
   113→ * Once registered, all fields are deeply frozen and immutable (see D10).
   114→ */
   115→export interface SceneGeometry {
   116→  /**
   117→   * Unique identifier for this geometry. Must match the key used
   118→   * in the geometry registry. Lowercase, underscore-separated.
   119→   * Must match /^[a-z][a-z0-9_]*$/.
   120→   * Examples: 'stage', 'tunnel', 'canyon', 'flyover'
   121→   */
   122→ ... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": 100,
  "limit": 80
}
[Tool Result]    100→  fov: number;
   101→  /** Composition aspect ratio (width / height) */
   102→  aspectRatio: number;
   103→  /**
   104→   * Scalar multiplier to oversize the plane beyond the visible area.
   105→   * 1.0 = exact fit, 1.2 = 20% larger in both dimensions.
   106→   * Must be >= 1.0. Defaults to 1.0.
   107→   *
   108→   * NOTE: This is uniform in both axes. For camera paths with purely
   109→   * directional motion (e.g., lateral-only), this overallocates in the
   110→   * non-moving axis. Per-axis oversize factors could be added if OBJ-040
   111→   * (edge-reveal validation) identifies this as a significant waste issue,
   112→   * but scalar is sufficient for V1 correctness.
   113→   */
   114→  oversizeFactor?: number;
   115→}
   116→
   117→/** Result of computing required plane dimensions */
   118→export interface PlaneSizingResult {
   119→  /** Recommended plane size in world units [width, height] */
   120→  size: Size2D;
   121→  /** The visible area at this d... [truncated]
Now let me also check the OBJ-005 spec for the `transparent` field on PlaneSlot, which is directly relevant to texture loading:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": 250,
  "limit": 200
}
[Tool Result]    250→ * @throws Error if the geometry fails structural validation
   251→ *         (see validateGeometryDefinition). The error message includes
   252→ *         all validation errors formatted as:
   253→ *         "Cannot register geometry '{name}': {error1}; {error2}; ..."
   254→ */
   255→export function registerGeometry(geometry: SceneGeometry): void;
   256→
   257→/**
   258→ * Returns an array of all registered geometry names.
   259→ * Useful for validation error messages ("expected one of: stage, tunnel, ...").
   260→ *
   261→ * Implicitly locks the registry on first call.
   262→ */
   263→export function getGeometryNames(): readonly string[];
   264→```
   265→
   266→### Geometry Definition Validator
   267→
   268→```typescript
   269→// src/scenes/geometries/validate.ts
   270→
   271→import type { SceneGeometry } from './types';
   272→
   273→/**
   274→ * Structural self-consistency errors found in a geometry definition.
   275→ */
   276→export interface Geomet... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "offset": 1,
  "limit": 50
}
[Tool Result]      1→# Specification: OBJ-010 — Three.js Page Shell, Build/Bundle Architecture, and Scene Renderer Skeleton
     2→
     3→## Summary
     4→
     5→OBJ-010 establishes the browser-side rendering foundation and the authoritative Node.js/browser code-split architecture for depthkit. It delivers: (1) the final HTML page shell with a properly sized WebGL canvas, (2) the Three.js `Scene` / `PerspectiveCamera` / `WebGLRenderer` initialization skeleton that all downstream rendering depends on, (3) the architectural decision that the browser page is a **data-driven renderer** — a "dumb page" that receives computed scene state from the Node.js orchestrator and executes Three.js calls accordingly, and (4) a minimal `renderFrame()` primitive that downstream objectives build upon. This objective also defines Node-side TypeScript types for data crossing the Node/browser boundary (excluding geometry serialization, which is deferred to OBJ-011).
     6→
     7→## Interface Contract
     8→
     9→... [truncated]
Now I have a solid understanding of the dependencies. Let me check what OBJ-011 expects from the texture loader, since it's closely related:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-011",
     3→  "description": "Full Puppeteer-to-page message protocol -- defines every message type crossing the Node.js/browser boundary. Includes: frame step commands (frame number, fps, totalFrames), scene setup/teardown commands (geometry instantiation, texture URLs, slot assignments), texture loading completion signals, transition signals (prepare next scene, start overlap rendering), and error reporting from page back to orchestrator. Single source of truth for the cross-boundary contract.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-010", "OBJ-005"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Expanded scope per Round 2 Issue 7 to cover full protocol, not just frame stepping. Depends on OBJ-005 for geometry slot structures in sce... [truncated]
Good. Now I have all the context I need. Let me propose the specification.

---

# Proposed Specification: OBJ-015 — Texture Loader and Format Handling

## Summary

OBJ-015 defines the browser-side texture loading module and its associated Node-side types. It provides: (1) a `THREE.TextureLoader`-based async texture loading API exposed on `window.depthkit`, with textures stored in a keyed map for retrieval by downstream geometry materialization; (2) alpha channel detection that samples loaded image pixel data to distinguish images with genuine transparency from those without; (3) texture metadata reporting (dimensions, aspect ratio, `hasAlpha`) back to the Node.js orchestrator; (4) a Node-side warning utility that flags non-transparent images assigned to slots that expect alpha (per OBJ-005's `PlaneSlot.transparent` field); and (5) texture lifecycle management (load, retrieve, unload, dispose). This directly satisfies C-09 (image format tolerance) and partially addresses OQ-02 (images without alpha — detect and warn, don't fix).

## Interface Contract

### Browser-Side: `src/page/texture-loader.js`

Imported by `src/page/scene-renderer.js` and merged into `window.depthkit`. All functions run inside headless Chromium.

```typescript
// Conceptual contract — implementation is plain JS running in Chromium.
// Types document the contract.

/**
 * Metadata returned after a texture is successfully loaded.
 * JSON-serializable — safe to return via page.evaluate().
 */
interface TextureMetadata {
  /** The caller-assigned texture ID. */
  id: string;
  /** Original image width in pixels. */
  width: number;
  /** Original image height in pixels. */
  height: number;
  /** width / height. Pre-computed for convenience. */
  aspectRatio: number;
  /**
   * Whether the image contains meaningful transparency.
   * Determined by sampling the image's pixel data: if any sampled
   * pixel has alpha < 250, this is true. See alpha detection algorithm.
   */
  hasAlpha: boolean;
}

/**
 * Options for texture loading. All optional with sensible defaults.
 */
interface TextureLoadOptions {
  /**
   * Whether to flip the texture vertically.
   * THREE.TextureLoader defaults to flipY=true, which matches
   * HTML canvas convention (origin top-left).
   * Default: true.
   */
  flipY?: boolean;

  /**
   * Color space for the texture.
   * 'srgb' → THREE.SRGBColorSpace (correct for photographic/AI-generated images).
   * 'linear' → THREE.LinearSRGBColorSpace (for data textures, normal maps).
   * Default: 'srgb'.
   */
  colorSpace?: 'srgb' | 'linear';

  /**
   * Minification filter.
   * Default: THREE.LinearMipmapLinearFilter (trilinear — best quality).
   * WebGL 2 handles non-power-of-two textures with mipmaps correctly.
   */
  minFilter?: number;

  /**
   * Magnification filter.
   * Default: THREE.LinearFilter (bilinear — smooth scaling up).
   */
  magFilter?: number;

  /**
   * Whether to skip alpha detection for this texture.
   * When true, hasAlpha is always reported as false.
   * Useful for known-opaque textures (backgrounds) to skip the
   * canvas sampling step for performance.
   * Default: false.
   */
  skipAlphaDetection?: boolean;
}

// Extensions to the DepthkitPage interface (window.depthkit)
interface DepthkitPage {
  // ... existing OBJ-010 methods ...

  /**
   * Loads a single texture by URL, detects alpha, caches it by ID,
   * and returns metadata.
   *
   * Internally:
   * 1. Creates a THREE.TextureLoader instance.
   * 2. Loads the image from `url` (returns Promise).
   * 3. Applies texture settings (colorSpace, flipY, filters).
   * 4. Detects alpha channel via canvas pixel sampling
   *    (unless skipAlphaDetection is true).
   * 5. Stores the THREE.Texture in an internal Map<string, THREE.Texture>.
   * 6. Returns TextureMetadata.
   *
   * If a texture with the same `id` already exists, the old texture
   * is disposed (texture.dispose()) and replaced. A console warning
   * is logged: "depthkit: replacing existing texture '{id}'".
   *
   * @param id - Unique identifier for this texture. Used by geometry
   *             materialization to reference the loaded texture.
   *             Typically the slot name (e.g., 'floor', 'subject').
   * @param url - URL to load the image from. Supports http://, https://,
   *              data: URIs, and relative paths (relative to the page).
   * @param options - Optional texture settings.
   * @returns Promise<TextureMetadata> — resolves when load + detection complete.
   * @throws Error if not initialized: "depthkit: not initialized. Call init() first."
   * @throws Error if url is empty/falsy: "depthkit: texture url is required for id '{id}'"
   * @throws Error if id is empty/falsy: "depthkit: texture id is required"
   * @throws Error if the image fails to load (404, network error, corrupt):
   *         "depthkit: failed to load texture '{id}' from '{url}': {original_error}"
   */
  loadTexture(id: string, url: string, options?: TextureLoadOptions): Promise<TextureMetadata>;

  /**
   * Loads multiple textures in parallel and returns all metadata.
   * Wraps loadTexture() with Promise.all().
   *
   * If ANY texture fails to load, the entire batch rejects.
   * Successfully loaded textures from the batch remain in the cache
   * (they are not rolled back). The error message identifies which
   * texture(s) failed.
   *
   * @param entries - Array of { id, url, options? } objects.
   * @returns Promise<TextureMetadata[]> — ordered to match input entries.
   * @throws Error if not initialized.
   * @throws Error if entries is empty: "depthkit: loadTextures requires at least one entry"
   * @throws Error if any entry has duplicate id within the batch:
   *         "depthkit: duplicate texture id '{id}' in batch"
   */
  loadTextures(entries: Array<{
    id: string;
    url: string;
    options?: TextureLoadOptions;
  }>): Promise<TextureMetadata[]>;

  /**
   * Retrieves a loaded THREE.Texture by ID.
   * Used by geometry materialization (downstream of OBJ-011) to
   * assign textures to mesh materials.
   *
   * @param id - The texture ID used during loadTexture().
   * @returns The THREE.Texture, or null if no texture with that ID is loaded.
   */
  getTexture(id: string): THREE.Texture | null;

  /**
   * Retrieves metadata for a loaded texture.
   * Returns the same TextureMetadata that was returned by loadTexture().
   *
   * @param id - The texture ID.
   * @returns TextureMetadata, or null if no texture with that ID is loaded.
   */
  getTextureMetadata(id: string): TextureMetadata | null;

  /**
   * Returns metadata for all currently loaded textures.
   * Useful for diagnostics and for the orchestrator to verify
   * all textures are loaded before rendering begins.
   *
   * @returns Array of TextureMetadata for all loaded textures.
   */
  getAllTextureMetadata(): TextureMetadata[];

  /**
   * Returns the number of currently loaded textures.
   */
  getTextureCount(): number;

  /**
   * Unloads a single texture by ID.
   * Calls texture.dispose() to free GPU/WebGL memory.
   * Removes the texture and its metadata from internal maps.
   *
   * @param id - The texture ID.
   * @returns true if a texture was unloaded, false if id was not found.
   */
  unloadTexture(id: string): boolean;

  /**
   * Unloads all textures. Calls texture.dispose() on each.
   * Clears both the texture map and the metadata map.
   * Called during scene teardown and before dispose().
   */
  unloadAllTextures(): void;
}
```

### Alpha Detection Algorithm

The alpha detection runs inside the browser using a temporary 2D canvas:

1. Create an offscreen `<canvas>` element (not added to DOM).
2. Determine sample dimensions: `sampleWidth = Math.min(image.width, 64)`, `sampleHeight = Math.min(image.height, 64)`. This downscales large images for performance.
3. Set canvas dimensions to `sampleWidth × sampleHeight`.
4. Get 2D context, draw the loaded image scaled to sample dimensions: `ctx.drawImage(image, 0, 0, sampleWidth, sampleHeight)`.
5. Call `ctx.getImageData(0, 0, sampleWidth, sampleHeight)` to get pixel data.
6. Iterate over the alpha channel (every 4th byte starting at index 3): if **any** pixel has `alpha < 250`, return `hasAlpha = true`.
7. If no pixel has alpha < 250, return `hasAlpha = false`.

**Why 250 instead of 255?** JPEG compression and canvas resampling can introduce alpha values of 254-255 on images that are conceptually fully opaque. The threshold of 250 avoids false positives from compression artifacts while still detecting intentional transparency (which typically has alpha values of 0 for fully transparent regions).

**Why 64×64?** At 64×64, only 4,096 pixels are sampled — fast even on CPU. For images with transparent backgrounds (the primary use case), the transparent region is usually large enough that downsampling to 64×64 still captures it. For images with only thin transparent edges, the downsampling might miss them, but such images are functionally opaque for the 2.5D use case.

**Performance:** The entire detection takes <5ms for any image size, as the browser's canvas scaling and pixel readback are highly optimized.

### Node-Side Types: `src/engine/texture-types.ts`

```typescript
// src/engine/texture-types.ts

/**
 * Texture metadata as returned from the page's loadTexture().
 * This is the Node-side mirror — used by the orchestrator to
 * inspect loaded texture properties without touching Three.js types.
 */
export interface TextureMetadata {
  id: string;
  width: number;
  height: number;
  aspectRatio: number;
  hasAlpha: boolean;
}

/**
 * Options for texture loading, passed to the page via page.evaluate().
 * JSON-serializable — no THREE.* constants. The page maps string/number
 * values to Three.js constants internally.
 */
export interface TextureLoadOptions {
  flipY?: boolean;
  colorSpace?: 'srgb' | 'linear';
  /**
   * Three.js filter constant values.
   * The page interprets these as THREE[filterName].
   * Callers should use Three.js constant values (numbers).
   * Defaults applied on page side if omitted.
   */
  minFilter?: number;
  magFilter?: number;
  skipAlphaDetection?: boolean;
}

/**
 * A single entry in a batch texture load command.
 */
export interface TextureLoadEntry {
  id: string;
  url: string;
  options?: TextureLoadOptions;
}

/**
 * A warning generated when a texture's alpha status doesn't match
 * the slot's transparency expectation.
 */
export interface TextureSlotWarning {
  /** The texture ID (typically matches the slot name). */
  textureId: string;
  /** The slot name in the geometry. */
  slotName: string;
  /** The geometry name. */
  geometryName: string;
  /** Warning severity. */
  severity: 'warning' | 'info';
  /** Human-readable warning message. */
  message: string;
}
```

### Node-Side Warning Utility: `src/engine/texture-warnings.ts`

```typescript
// src/engine/texture-warnings.ts

import type { TextureMetadata, TextureSlotWarning } from './texture-types.js';
import type { SceneGeometry } from '../scenes/geometries/types.js';

/**
 * Checks loaded texture metadata against a geometry's slot expectations
 * and returns warnings for mismatches.
 *
 * Warnings are generated for:
 * 1. A slot has `transparent: true` but the loaded texture has `hasAlpha: false`.
 *    This means the image will display with hard rectangular edges in the scene.
 *    Severity: 'warning'.
 *    Message: "Texture '{id}' for slot '{slot}' in geometry '{geo}' has no alpha
 *    channel, but this slot expects transparency. The image will appear as a
 *    hard-edged rectangle. Consider using an image with a transparent background
 *    or applying background removal before rendering."
 *
 * 2. A slot has `transparent: false` (or undefined) but the loaded texture has
 *    `hasAlpha: true`. This is informational — the alpha will be ignored since
 *    the material won't enable transparency blending.
 *    Severity: 'info'.
 *    Message: "Texture '{id}' for slot '{slot}' in geometry '{geo}' has an alpha
 *    channel, but this slot does not use transparency. Alpha will be ignored."
 *
 * @param textureMetadataMap - Map of texture ID → TextureMetadata for loaded textures.
 * @param geometry - The SceneGeometry definition with slot expectations.
 * @param slotToTextureId - Map of slot name → texture ID. Not all slots need entries
 *                          (optional slots may be omitted).
 * @returns Array of TextureSlotWarning. Empty if no mismatches.
 */
export function checkTextureSlotCompatibility(
  textureMetadataMap: Map<string, TextureMetadata>,
  geometry: SceneGeometry,
  slotToTextureId: Record<string, string>
): TextureSlotWarning[];
```

## Design Decisions

### D1: Texture Loading Runs in the Browser, Commanded by the Orchestrator

**Decision:** The texture loader is a browser-side module (part of `window.depthkit`). The orchestrator triggers texture loading via `page.evaluate()`, passing URLs. The page loads images via `THREE.TextureLoader`, which uses the browser's native image decoding.

**Rationale:** Three.js `TextureLoader` relies on `HTMLImageElement` for image decoding — this only works in a browser context. Loading must happen where Three.js runs. The "dumb page" architecture (OBJ-010 D1) means the page receives load commands and reports metadata back, but holds no domain logic about *which* textures to load or *when*.

**Impact on image accessibility:** The orchestrator is responsible for making image files accessible to the browser via URLs. This could be via a local HTTP server, `file://` protocol, data URIs, or Puppeteer request interception. OBJ-015 does not constrain the URL scheme — it accepts any URL that the browser's image loading can resolve. The mechanism for serving local files to the browser page is the orchestrator's concern (OBJ-011 / OBJ-009).

### D2: Texture Keyed by Caller-Assigned String ID

**Decision:** Each texture is stored in a `Map<string, THREE.Texture>` keyed by a string ID provided by the caller. The ID is typically the slot name (e.g., `'floor'`, `'subject'`), but the loader imposes no naming constraint — it treats IDs as opaque strings.

**Rationale:** Slot names are the natural key for texture → mesh assignment. By using the slot name as the texture ID, geometry materialization (downstream) can call `getTexture('floor')` without a separate mapping table. However, keeping IDs opaque allows flexibility for non-slot textures (e.g., HUD layer textures, transition masks) if needed in the future.

### D3: Alpha Detection via Canvas Pixel Sampling, Not Format Sniffing

**Decision:** Alpha is detected by actually sampling pixel data from the loaded image, not by checking the file extension or MIME type.

**Alternatives considered:**
1. **Format sniffing** (JPEG = no alpha, PNG = maybe alpha) — unreliable. PNGs can be fully opaque. WebP can be either. Data URIs obscure the original format.
2. **Full-resolution pixel scan** — accurate but slow for large images (a 4K image = 33M pixels).
3. **Downscaled sampling** (chosen) — draws the image to a 64×64 canvas and scans 4,096 pixels. Fast, and sufficient for detecting transparent backgrounds.

**Rationale:** The purpose is to detect whether the image has meaningful transparency (as in background-removed subject images), not to detect single-pixel alpha variations. Downscaling to 64×64 reliably catches transparent backgrounds while keeping detection under 5ms.

### D4: Replacement Semantics for Duplicate IDs

**Decision:** If `loadTexture()` is called with an ID that already exists, the old texture is disposed and replaced. A console warning is logged.

**Rationale:** During scene transitions, the orchestrator may reuse slot names across scenes. Rather than requiring explicit unload-before-load, replacement semantics keep the API simple. The warning helps catch accidental overwrites during development.

### D5: Batch Loading via Promise.all (Fail-Fast)

**Decision:** `loadTextures()` uses `Promise.all()` — if any texture fails, the entire batch rejects. Successfully loaded textures remain in the cache.

**Alternatives considered:**
1. **`Promise.allSettled()`** — returns all results (fulfilled and rejected). More resilient but requires the caller to inspect each result.
2. **`Promise.all()`** (chosen) — simpler error handling. The orchestrator's expected pattern is "load all textures for a scene → if any fail, abort the scene."

**Rationale:** Partial scene rendering (where some textures are missing) produces broken output — a plane with no texture is worse than failing. Fail-fast matches the engine's "fail fast, fail clearly" philosophy (C-10).

### D6: Warning Utility on Node Side, Not Page Side

**Decision:** The `checkTextureSlotCompatibility()` function runs on the Node side, not in the browser page. The page reports `hasAlpha` per texture; the orchestrator cross-references this with geometry slot definitions (from OBJ-005).

**Rationale:** The page is a "dumb renderer" (OBJ-010 D1). It doesn't know about geometry definitions, slot names, or the `transparent` field on `PlaneSlot`. Cross-referencing texture metadata with geometry contracts is domain logic that belongs on the Node side.

### D7: `sRGBColorSpace` as Default

**Decision:** Textures default to `THREE.SRGBColorSpace`.

**Rationale:** All depthkit textures are photographic or AI-generated images, which are authored in sRGB color space. Using `SRGBColorSpace` ensures Three.js applies correct gamma decoding. `LinearSRGBColorSpace` is only needed for data textures (e.g., normal maps), which depthkit V1 doesn't use.

### D8: `dispose()` Calls `unloadAllTextures()` Implicitly

**Decision:** When `window.depthkit.dispose()` is called (from OBJ-010), it must call `unloadAllTextures()` before disposing the renderer. OBJ-015 extends the existing `dispose()` to include texture cleanup.

**Rationale:** Textures hold GPU memory. If the renderer is disposed without disposing textures first, the memory may leak until the browser tab/context is closed. Since `dispose()` is the "clean shutdown" mechanism, it should be comprehensive.

### D9: No Texture Resizing or Clamping to MAX_TEXTURE_SIZE

**Decision:** OBJ-015 does not resize images that exceed the WebGL context's `MAX_TEXTURE_SIZE`. If an image exceeds the limit, Three.js handles it (it downscales automatically in modern versions, or renders incorrectly in older versions).

**Rationale:** `MAX_TEXTURE_SIZE` is typically 4096 (SwiftShader) to 16384 (modern GPUs). depthkit's recommended image sizes (1920×1080 to 4K) are within these limits. Adding explicit resizing logic would add complexity for an edge case that Three.js already handles. The `getRendererInfo().maxTextureSize` (from OBJ-010) allows the orchestrator to warn upstream if needed — but that's outside OBJ-015's scope.

## Acceptance Criteria

- [ ] **AC-01:** `src/page/texture-loader.js` exports functions that are merged into `window.depthkit`: `loadTexture`, `loadTextures`, `getTexture`, `getTextureMetadata`, `getAllTextureMetadata`, `getTextureCount`, `unloadTexture`, `unloadAllTextures`.

- [ ] **AC-02:** After `loadTexture('bg', url)` resolves, `getTexture('bg')` returns a `THREE.Texture` instance (non-null), and `getTextureMetadata('bg')` returns a `TextureMetadata` object with `id === 'bg'`, numeric `width > 0`, `height > 0`, `aspectRatio > 0`, and a boolean `hasAlpha`.

- [ ] **AC-03:** A PNG image with a transparent background (e.g., a subject isolated on transparency) is detected as `hasAlpha: true`.

- [ ] **AC-04:** A JPEG image (which cannot have alpha) is detected as `hasAlpha: false`.

- [ ] **AC-05:** A PNG image that is fully opaque (all pixels have alpha 255) is detected as `hasAlpha: false`.

- [ ] **AC-06:** After `loadTexture()`, the returned `TextureMetadata.width` and `.height` match the original image's natural dimensions (not the 64×64 sampling size).

- [ ] **AC-07:** `loadTextures([{id:'a', url:url1}, {id:'b', url:url2}])` loads both textures in parallel. After resolution, `getTexture('a')` and `getTexture('b')` both return non-null textures. Returned metadata array has length 2 and is ordered to match input.

- [ ] **AC-08:** `loadTextures()` with a batch where one URL is invalid (404) rejects with an error message identifying the failed texture. Textures that loaded successfully remain in the cache.

- [ ] **AC-09:** Calling `loadTexture('x', url)` when a texture with id `'x'` already exists: the old texture is disposed (`texture.dispose()` called), the new texture replaces it, and a console warning is logged containing the string `"replacing existing texture 'x'"`.

- [ ] **AC-10:** `unloadTexture('bg')` disposes the texture (`texture.dispose()` called), removes it from both internal maps, and returns `true`. Subsequent `getTexture('bg')` returns `null`. Calling `unloadTexture('nonexistent')` returns `false`.

- [ ] **AC-11:** `unloadAllTextures()` disposes all loaded textures and clears both maps. `getTextureCount()` returns 0 afterward.

- [ ] **AC-12:** Calling any texture method (`loadTexture`, `getTexture`, etc.) before `init()` throws: `"depthkit: not initialized. Call init() first."`

- [ ] **AC-13:** `loadTexture('x', '')` throws: `"depthkit: texture url is required for id 'x'"`. `loadTexture('', url)` throws: `"depthkit: texture id is required"`.

- [ ] **AC-14:** Loading a texture with `{ skipAlphaDetection: true }` returns `hasAlpha: false` regardless of actual image content.

- [ ] **AC-15:** Loaded textures default to `THREE.SRGBColorSpace`. Loading with `{ colorSpace: 'linear' }` sets `THREE.LinearSRGBColorSpace`.

- [ ] **AC-16:** `window.depthkit.dispose()` calls `unloadAllTextures()` before disposing the renderer. After dispose, `getTextureCount()` returns 0.

- [ ] **AC-17:** `src/engine/texture-types.ts` exports `TextureMetadata`, `TextureLoadOptions`, `TextureLoadEntry`, and `TextureSlotWarning` types.

- [ ] **AC-18:** `src/engine/texture-warnings.ts` exports `checkTextureSlotCompatibility()`. Given a texture with `hasAlpha: false` and a slot with `transparent: true`, it returns a warning with severity `'warning'` and a message mentioning "no alpha channel" and "hard-edged rectangle".

- [ ] **AC-19:** `checkTextureSlotCompatibility()` given a texture with `hasAlpha: true` and a slot with `transparent: false` (or undefined), returns an info-level entry mentioning alpha will be ignored.

- [ ] **AC-20:** `checkTextureSlotCompatibility()` returns an empty array when alpha status matches slot expectations (both true, or both false/undefined).

- [ ] **AC-21:** `loadTextures()` with duplicate IDs in the same batch rejects: `"depthkit: duplicate texture id '{id}' in batch"`.

- [ ] **AC-22:** `loadTextures([])` (empty array) rejects: `"depthkit: loadTextures requires at least one entry"`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `loadTexture()` before `init()` | Throws `"depthkit: not initialized. Call init() first."` |
| `loadTexture('', url)` | Throws `"depthkit: texture id is required"` |
| `loadTexture('x', '')` | Throws `"depthkit: texture url is required for id 'x'"` |
| `loadTexture('x', null)` or `undefined` | Throws `"depthkit: texture url is required for id 'x'"` (falsy check) |
| URL returns 404 | Rejects: `"depthkit: failed to load texture 'x' from '{url}': {error}"` |
| URL points to non-image file | Rejects with same error format (browser image decode fails) |
| Corrupt/truncated image file | Rejects with same error format |
| Image exceeds MAX_TEXTURE_SIZE | Three.js auto-downscales. Metadata reports original image dimensions. |
| Replacing existing texture ID | Old texture disposed, new one stored, console warning logged |
| `loadTextures` with one failure | Promise rejects. Successfully loaded textures remain cached. |
| `loadTextures` with duplicate IDs in batch | Rejects before loading any textures (synchronous validation) |
| `loadTextures` with empty array | Rejects: `"depthkit: loadTextures requires at least one entry"` |
| `getTexture('nonexistent')` | Returns `null` |
| `getTextureMetadata('nonexistent')` | Returns `null` |
| `unloadTexture('nonexistent')` | Returns `false` (no-op) |
| `unloadAllTextures()` when no textures loaded | No-op, no error |
| `dispose()` with loaded textures | All textures disposed via `unloadAllTextures()` before renderer disposal |
| Data URI as URL | Loads normally (browser handles data URIs natively) |
| Very large image (e.g., 8000×6000 PNG) | Loads normally. Alpha detection uses 64×64 downscale, so performance is constant. |
| Image with semi-transparent pixels (alpha ~128) | Detected as `hasAlpha: true` (128 < 250) |
| Image with nearly-opaque pixels (alpha 251-254) | Detected as `hasAlpha: false` (251 > 250). These artifacts are not meaningful transparency. |
| `checkTextureSlotCompatibility` with slot not in slotToTextureId | Skipped — no warning. Optional slots without textures are valid. |
| `checkTextureSlotCompatibility` with texture ID not in metadata map | Skipped — texture wasn't loaded (may be handled by other validation). |

## Test Strategy

### Puppeteer-Based Integration Tests (Primary)

These tests launch headless Chromium, load the depthkit page, call `init()`, and exercise texture loading with real images.

**Test images required:** A set of small test images should be created or provided:
- `opaque.jpg` — A small JPEG (e.g., 100×75), fully opaque.
- `opaque.png` — A small PNG (e.g., 80×60), fully opaque (no alpha channel, or all pixels alpha=255).
- `transparent.png` — A small PNG (e.g., 100×100) with transparent background (e.g., a colored circle on transparency).
- `semitransparent.png` — A small PNG with semi-transparent regions (alpha ~128).
- `large_opaque.png` — A larger image (e.g., 2048×1024) to verify metadata reports original dimensions.

These test images should be served to the browser via a simple HTTP server or Puppeteer request interception.

**Load and metadata tests:**
1. Load `opaque.jpg` → verify metadata: `hasAlpha: false`, width/height match, aspectRatio ≈ width/height.
2. Load `opaque.png` → verify `hasAlpha: false`.
3. Load `transparent.png` → verify `hasAlpha: true`.
4. Load `semitransparent.png` → verify `hasAlpha: true`.
5. Load `large_opaque.png` → verify metadata reports original dimensions (2048×1024), not 64×64.
6. Load with `skipAlphaDetection: true` on `transparent.png` → verify `hasAlpha: false`.

**Texture retrieval tests:**
7. After load, `getTexture(id)` returns a Three.js Texture (has `.image` property).
8. `getTexture('nonexistent')` returns null.
9. `getTextureMetadata(id)` returns the same metadata as loadTexture resolved with.
10. `getAllTextureMetadata()` returns array with correct length after loading N textures.
11. `getTextureCount()` reflects number of loaded textures.

**Batch loading tests:**
12. `loadTextures` with 3 entries → all resolve, metadata array has length 3 in order.
13. `loadTextures` with one bad URL → rejects, good textures remain in cache.
14. `loadTextures([])` → rejects with expected message.
15. `loadTextures` with duplicate IDs → rejects with expected message.

**Lifecycle tests:**
16. `unloadTexture(id)` → `getTexture(id)` returns null, `getTextureCount()` decremented.
17. `unloadAllTextures()` → `getTextureCount() === 0`.
18. Load, then load same ID again → old texture replaced, warning logged (verify via `page.on('console')`).
19. `dispose()` after loading textures → `getTextureCount() === 0` after re-init.

**Error condition tests:**
20. Any texture method before `init()` → throws expected error.
21. Empty/falsy id or url → throws expected error.
22. 404 URL → rejects with expected error format.

**Color space test:**
23. Load with `colorSpace: 'srgb'` → `texture.colorSpace === THREE.SRGBColorSpace`.
24. Load with `colorSpace: 'linear'` → `texture.colorSpace === THREE.LinearSRGBColorSpace`.
25. Load with default → `texture.colorSpace === THREE.SRGBColorSpace`.

### Node-Side Unit Tests

26. `checkTextureSlotCompatibility` with alpha-mismatch → returns warning.
27. `checkTextureSlotCompatibility` with matching alpha → returns empty array.
28. `checkTextureSlotCompatibility` with `hasAlpha: true` / `transparent: false` → returns info.
29. `checkTextureSlotCompatibility` with missing slot entries → no warning for missing slots.
30. Types compile without error.

### Relevant Testable Claims

- **TC-02** (render performance): Texture loading time adds to per-scene setup. Load time should be measured but is not per-frame — it's a one-time cost per scene.
- **C-09** (image format tolerance): AC-03/04/05 directly validate this constraint.
- **OQ-02** (images without alpha): AC-03/04/05 + AC-18 partially address this — detect and warn.

## Integration Points

### Depends on

| Dependency | What OBJ-015 uses |
|---|---|
| **OBJ-010** (Page shell) | `window.depthkit.scene`, `window.depthkit.renderer` (for WebGL context), `window.depthkit.isInitialized()` guard, the `init()`/`dispose()` lifecycle. OBJ-015 extends `dispose()` to include texture cleanup. |

### Consumed by

| Downstream | How it uses OBJ-015 |
|---|---|
| **OBJ-011** (Message protocol) | Defines `load_textures` message type that triggers `loadTexture()`/`loadTextures()` on the page. Uses `TextureMetadata` in response messages. |
| **OBJ-039** (Scene setup / geometry materialization) | Calls `getTexture(slotName)` to retrieve loaded textures and assign them to mesh materials during scene instantiation. Uses `getTextureMetadata()` for aspect-ratio-aware plane sizing. |
| **OBJ-040** (Aspect ratio / edge-reveal validation) | Uses `TextureMetadata.aspectRatio` and `TextureMetadata.width`/`height` to verify plane sizing against texture dimensions. |
| **OBJ-052** (Subtitle/caption overlay) | May use texture loading for HUD layer images. |
| **Scene sequencer** (OBJ-036) | Calls `unloadAllTextures()` during scene teardown to free GPU memory between scenes. Uses `checkTextureSlotCompatibility()` on the Node side to emit warnings before rendering. |

### File Placement

```
depthkit/
  src/
    engine/
      texture-types.ts       # NEW — TextureMetadata, TextureLoadOptions, TextureLoadEntry, TextureSlotWarning
      texture-warnings.ts    # NEW — checkTextureSlotCompatibility()
    page/
      texture-loader.js      # NEW — browser-side texture loading, alpha detection, cache
      scene-renderer.js      # MODIFY — import texture-loader.js, merge into window.depthkit, extend dispose()
```

## Open Questions

### OQ-A: Should the texture loader report a warning for images exceeding MAX_TEXTURE_SIZE?

`getRendererInfo().maxTextureSize` is available after init. The texture loader could check `image.width` and `image.height` against this value and include a boolean `exceedsMaxTextureSize` in the metadata, or log a warning. Three.js auto-downscales, so this is informational only. **Recommendation:** Include an `exceedsMaxTextureSize` field in metadata if the check is trivial. Defer if it requires accessing the renderer's GL context from within the loader.

### OQ-B: Should `loadTextures` use `Promise.allSettled` instead of `Promise.all`?

`Promise.all` fails fast — one bad texture aborts the whole batch. `Promise.allSettled` would let the orchestrator decide what to do with partial results. The current design uses `Promise.all` for simplicity and because partial scenes are broken scenes. If downstream objectives find this too aggressive, it could be revisited.

### OQ-C: Should the alpha detection threshold (250) be configurable?

The threshold is hardcoded at 250. Some use cases might want stricter detection (255 = only perfectly opaque is "no alpha") or looser (200 = ignore minor transparency). **Recommendation:** Hardcode 250 for V1. The threshold is a heuristic that works for the overwhelmingly common case (background-removed images vs. fully opaque images). Expose as configurable only if tuning reveals edge cases.

---

I believe this spec covers the full scope of OBJ-015. I'd like the challenger to review, particularly:
1. Whether the alpha detection algorithm (64×64 downsample, threshold 250) is sound
2. Whether the `checkTextureSlotCompatibility` warning utility scope is right
3. Whether any edge cases are missing
4. Whether the integration with OBJ-010's `dispose()` lifecycle is correctly specified

---

## Round 2 — spec_challenger

I'll review the proposed spec carefully against the seed, dependencies, and implementability requirements.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md",
  "offset": "40",
  "limit": "120"
}
[Tool Result]     40→ * Any function accepting PlaneTransform also accepts PlaneSlot.
    41→ *
    42→ * PlaneSlot values in a registered SceneGeometry are immutable templates
    43→ * (see D9). The readonly tuple types (Vec3, EulerRotation, Size2D) enforce
    44→ * this at compile time; deep freezing at registration enforces it at runtime.
    45→ * These values are the geometry's defaults. Downstream consumers (OBJ-036,
    46→ * OBJ-039) may apply per-scene overrides from the manifest by creating a
    47→ * new PlaneTransform with the override applied, rather than mutating the
    48→ * slot definition. The override mechanism is defined by the manifest schema
    49→ * (OBJ-004), not by this contract.
    50→ */
    51→export interface PlaneSlot extends PlaneTransform {
    52→  /**
    53→   * Whether the manifest MUST provide an image for this slot.
    54→   * If true, manifest validation (OBJ-017) rejects manifests that
    55→   * omit this slot. If false, the slot is available but the g... [truncated]
Good. Now I have the `PlaneSlot.transparent` field confirmed. Let me check a few more things:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "offset": "1",
  "limit": "50"
}
[Tool Result]      1→# Specification: Coordinate System and Spatial Math Reference (OBJ-003)
     2→
     3→## Summary
     4→
     5→OBJ-003 codifies the spatial foundation for all depthkit geometry and camera work: the Three.js right-handed coordinate conventions, the relationship between camera FOV / distance and visible area, plane sizing math, and utility functions for computing spatial relationships. This module is a pure-math reference library with zero rendering dependencies — it exports constants, types, and deterministic computation functions that every downstream geometry definition (OBJ-005), camera path preset (OBJ-006), easing/interpolation module (OBJ-007), scene sequencer (OBJ-010), and edge-reveal validator (OBJ-040) will import.
     6→
     7→## Interface Contract
     8→
     9→### Constants
    10→
    11→```typescript
    12→// src/spatial/constants.ts
    13→
    14→/** Three.js right-handed coordinate system conventions */
    15→export const AXIS = {
    16→  RIGHT: [1, 0, 0... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "offset": "200",
  "limit": "100"
}
[Tool Result]    200→After OBJ-010, this file contains a **stub**. OBJ-011 defines the full message handling protocol.
   201→
   202→```javascript
   203→// src/page/message-handler.js
   204→// Stub: Message protocol between Puppeteer orchestrator and browser page.
   205→//
   206→// OBJ-011 defines every message type crossing the Node.js/browser boundary:
   207→// frame step commands, scene setup/teardown, texture loading signals, etc.
   208→//
   209→// Messages arrive via page.evaluate() calls from the Node.js orchestrator.
   210→// The handler calls into window.depthkit methods (init, renderFrame, dispose).
   211→//
   212→// TODO: OBJ-011 — Full message protocol
   213→export {};
   214→```
   215→
   216→### Module: `src/page/index.html`
   217→
   218→The final HTML shell (evolving the OBJ-001 stub):
   219→
   220→```html
   221→<!DOCTYPE html>
   222→<html lang="en">
   223→<head>
   224→  <meta charset="UTF-8">
   225→  <meta name="viewport" content="width=device-width, initial-scal... [truncated]
Now I have enough context. Let me do my review.

---

## Challenger Review — OBJ-015

### Points of Agreement (Sound)

The overall structure is solid:
- Browser-side texture loading via `THREE.TextureLoader` is the correct architecture
- Alpha detection via canvas pixel sampling is a reasonable approach
- Node-side warning utility that cross-references against OBJ-005's `PlaneSlot.transparent` is the right separation of concerns
- Keying textures by caller-assigned string ID is pragmatic
- `sRGBColorSpace` as default is correct for this use case
- The edge cases table is comprehensive for the common cases
- The `dispose()` integration with `unloadAllTextures()` is necessary

### Issues

---

**Issue 1: `minFilter`/`magFilter` passed as raw numbers breaks the "dumb page" contract** — Major

The `TextureLoadOptions.minFilter` and `magFilter` are typed as `number` and the doc says "Callers should use Three.js constant values (numbers)." But the Node side is TypeScript with no Three.js runtime dependency — the orchestrator would need to hardcode magic numbers like `1008` for `THREE.LinearMipmapLinearFilter`. The node-side types file says "JSON-serializable — no THREE.* constants" and then immediately implies consumers use THREE.* constant values.

**Fix:** Define string literal union types mapping to Three.js filter names, and have the page-side code map them to THREE constants. Same pattern as `colorSpace: 'srgb' | 'linear'`:

```typescript
minFilter?: 'nearest' | 'linear' | 'linear_mipmap_linear';
magFilter?: 'nearest' | 'linear';
```

Or, since the defaults are always correct for depthkit's use case (photographic textures), remove `minFilter`/`magFilter` from the public API entirely and hardcode them in the page. These are expert-level Three.js knobs that an LLM or orchestrator has no reason to change.

---

**Issue 2: The spec says OBJ-015 "extends `dispose()`" but doesn't specify the mechanism** — Major

D8 says: "OBJ-015 extends the existing `dispose()` to include texture cleanup." AC-16 says `dispose()` calls `unloadAllTextures()`. But OBJ-010's `dispose()` is already implemented — how does OBJ-015 modify it? Does texture-loader.js monkey-patch `window.depthkit.dispose`? Does scene-renderer.js import texture-loader.js and call `unloadAllTextures()` within its own `dispose()` implementation? The implementation path is ambiguous.

**Fix:** Specify the mechanism explicitly. The cleanest approach: `scene-renderer.js` imports texture-loader.js's `unloadAllTextures` and calls it within the existing `dispose()` function body, before `renderer.forceContextLoss()`. State this in the spec so the implementer knows they're modifying `scene-renderer.js`'s `dispose()` function, not creating a separate hook system.

---

**Issue 3: `loadTexture` returns `Promise<TextureMetadata>` but no specification of how the Promise is created** — Minor

The spec says `THREE.TextureLoader` is used. Three.js's `TextureLoader.load()` uses callbacks, not Promises. The spec should note that the implementation wraps `loader.load(url, onLoad, onProgress, onError)` in a `new Promise()`, or uses `loader.loadAsync(url)` (available since Three.js r148). This is close to implementation detail, but since `loadAsync` didn't exist in older Three.js versions, it's worth stating which approach to use.

**Fix:** Add a note: "Uses `THREE.TextureLoader.loadAsync(url)` (available since Three.js r148) which returns a native Promise. If loadAsync is unavailable, wrap `loader.load()` callbacks in `new Promise()`."

---

**Issue 4: `checkTextureSlotCompatibility` signature uses `Map<string, TextureMetadata>` but consumers will likely have a plain object** — Minor

The orchestrator receives texture metadata from `page.evaluate()` as plain objects/arrays (from `getAllTextureMetadata()`), not as a `Map`. Requiring callers to construct a Map adds friction.

**Fix:** Accept `Record<string, TextureMetadata>` instead of `Map<string, TextureMetadata>`, or accept both:
```typescript
textureMetadataMap: Record<string, TextureMetadata> | Map<string, TextureMetadata>
```
Simplest: just use `Record<string, TextureMetadata>`.

---

**Issue 5: Missing specification for how local file URLs are served to the browser** — Major

The spec says "OBJ-015 does not constrain the URL scheme" and "The mechanism for serving local files to the browser page is the orchestrator's concern (OBJ-011 / OBJ-009)." But this is a critical integration point. The manifest specifies paths like `"./images/scene1_floor.png"`. The browser page loaded by Puppeteer runs from a `file://` or served URL. Three.js `TextureLoader` uses `fetch()` or `XMLHttpRequest`, both of which have CORS restrictions on `file://` URLs. If the page is loaded from `file://`, local image loading may fail due to browser security policies.

**Fix:** This isn't OBJ-015's problem to solve, but the spec should **explicitly document the assumption**: "The URLs passed to `loadTexture()` must be resolvable by the browser's image loading mechanism. When the page is loaded from a local file (`file://` protocol), CORS restrictions may prevent loading local images via relative paths. The orchestrator (OBJ-009/OBJ-011) is responsible for ensuring images are accessible — e.g., by serving the page and images via a local HTTP server, using `data:` URIs, or using Puppeteer request interception. OBJ-015 treats URL resolution as opaque and reports load failures via the error path."

This moves it from an implicit assumption to a documented constraint. Without this, an implementer will test with `file://` URLs and hit CORS errors with no guidance.

---

**Issue 6: `flipY` default of `true` needs justification and interaction with Three.js's own default** — Minor

The spec says `flipY` defaults to `true` and notes "THREE.TextureLoader defaults to flipY=true." This is correct — Three.js textures flip Y by default because WebGL textures are bottom-up while HTML images are top-down. But the spec doesn't clarify: is OBJ-015 *setting* `flipY` or *not touching it* (relying on Three.js default)? If Three.js already defaults to `true`, then OBJ-015's default of `true` just means "don't change it." This is fine but the spec should say "Relies on Three.js TextureLoader default. Explicitly set only when `flipY: false` is requested."

**Fix:** Clarify: "Three.js `TextureLoader` defaults to `texture.flipY = true`. OBJ-015 only explicitly sets `texture.flipY` when the caller passes `flipY: false`. When omitted, the Three.js default applies."

---

**Issue 7: The "Consumed by" section lists OBJ-015 as the "scene sequencer" but the metadata says OBJ-015 is the texture loader** — Critical (naming confusion)

In the Integration Points → "Consumed by" section:
> **Scene sequencer** (OBJ-036) — Calls `unloadAllTextures()` during scene teardown...

But OBJ-015 IS the texture loader. The description says "OBJ-036" is the scene sequencer. But look at the progress map: OBJ-015 `blocks: ["OBJ-039", "OBJ-040", "OBJ-052"]`. OBJ-036 is NOT listed as a downstream of OBJ-015 in the progress map. Also, OBJ-010's spec says "OBJ-015 (scene sequencer)" in its consumed-by section — this is a mistake in OBJ-010, not in this spec, but this spec shouldn't propagate the error.

**Fix:** Replace "Scene sequencer (OBJ-036)" with the actual downstream consumers listed in the progress map. OBJ-015 blocks OBJ-039, OBJ-040, and OBJ-052. The `checkTextureSlotCompatibility()` is called by whichever Node-side component orchestrates scene setup — probably OBJ-011 or OBJ-039. Don't invent a connection to OBJ-036 that the DAG doesn't have.

---

**Issue 8: No acceptance criterion for `getTexture()` returning a usable Three.js Texture** — Minor

AC-02 says `getTexture('bg')` returns a `THREE.Texture instance (non-null)`. But there's no criterion verifying the texture is actually usable — that it can be assigned to a `MeshBasicMaterial.map` and rendered. This matters because the downstream geometry materialization (OBJ-039) depends on it.

**Fix:** Add an AC: "After `loadTexture('bg', url)` resolves, a mesh created with `new THREE.MeshBasicMaterial({ map: window.depthkit.getTexture('bg') })` and rendered via `renderFrame()` produces a visible (non-black) frame when captured via `canvas.toDataURL()`." This is effectively a smoke test that the texture is renderable, not just loaded.

---

**Issue 9: Alpha detection on images loaded via `THREE.TextureLoader` — the `image` property may be an `HTMLImageElement`, not directly drawable to canvas in all cases** — Minor

The alpha detection algorithm says "draw the loaded image" to a canvas. `THREE.TextureLoader` sets `texture.image` to an `HTMLImageElement`. This should work with `ctx.drawImage(image, ...)` in the browser. However, if the image is cross-origin loaded (CORS), `getImageData()` will throw a security error ("tainted canvas"). The spec should note this constraint.

**Fix:** Add to edge cases: "If the image is loaded cross-origin without proper CORS headers, `ctx.getImageData()` will throw a SecurityError. In this case, alpha detection falls back to `hasAlpha: false` and logs a console warning: `'depthkit: alpha detection failed for texture {id} (CORS restriction). Assuming opaque.'`" This is defensive — the orchestrator should ensure CORS is handled, but the texture loader shouldn't crash.

---

**Issue 10: `loadTextures` duplicate ID check — timing vs. replacement semantics contradiction** — Minor

`loadTexture()` has replacement semantics (D4: replace and warn). But `loadTextures()` rejects duplicate IDs within a batch (AC-21). What if a batch entry duplicates an *already-loaded* texture (not within the batch)? The spec says `loadTexture` replaces, and `loadTextures` wraps `loadTexture` via `Promise.all`. So a batch entry duplicating an existing texture should replace it (per `loadTexture` semantics), while duplicate IDs *within the same batch* are rejected. This is consistent but not explicitly stated.

**Fix:** Add a sentence to `loadTextures` doc: "Duplicate IDs within the batch are rejected before any loading begins. If a batch entry's ID matches an already-loaded texture (from a prior call), the existing texture is replaced per `loadTexture()` semantics."

---

**Issue 11: The spec references OBJ-039 as consuming `getTextureMetadata()` for aspect-ratio-aware plane sizing, but OBJ-039 is not a direct downstream in the DAG** — Minor

The progress map shows OBJ-015 blocks `[OBJ-039, OBJ-040, OBJ-052]`. The spec's "Consumed by" section lists OBJ-039 correctly. But it also lists OBJ-011 and OBJ-036 as consumers. OBJ-011 is reasonable (it defines the message protocol that triggers loading). OBJ-036 is incorrect per Issue 7. Keep OBJ-011 as a consumer, fix OBJ-036.

---

### Summary of Issues by Severity

| # | Severity | Issue |
|---|----------|-------|
| 7 | Critical | Wrong downstream OBJ reference (OBJ-036 as scene sequencer consumer) |
| 1 | Major | `minFilter`/`magFilter` as raw numbers breaks dumb-page contract |
| 2 | Major | `dispose()` extension mechanism unspecified |
| 5 | Major | Local file URL accessibility not documented as a constraint |
| 3 | Minor | Promise creation mechanism for TextureLoader not specified |
| 4 | Minor | `Map` vs `Record` in `checkTextureSlotCompatibility` |
| 6 | Minor | `flipY` default justification |
| 8 | Minor | No AC for texture renderability |
| 9 | Minor | CORS fallback for alpha detection |
| 10 | Minor | Batch vs. existing duplicate ID semantics clarity |
| 11 | Minor | OBJ-036 consumer reference (subset of #7) |

Please revise the spec addressing the critical and major issues (1, 2, 5, 7). The minor issues should be addressed too but are less blocking. I'll verify the fixes in the next round.

---

## Round 3 — spec_author

Thank you for the thorough review. All issues are valid. Here's the revised spec addressing every point:

---

# Specification: OBJ-015 — Texture Loader and Format Handling

## Summary

OBJ-015 defines the browser-side texture loading module and its associated Node-side types. It provides: (1) a `THREE.TextureLoader`-based async texture loading API exposed on `window.depthkit`, with textures stored in a keyed map for retrieval by downstream geometry materialization; (2) alpha channel detection that samples loaded image pixel data to distinguish images with genuine transparency from those without; (3) texture metadata reporting (dimensions, aspect ratio, `hasAlpha`) back to the Node.js orchestrator; (4) a Node-side warning utility that flags non-transparent images assigned to slots that expect alpha (per OBJ-005's `PlaneSlot.transparent` field); and (5) texture lifecycle management (load, retrieve, unload, dispose). This directly satisfies C-09 (image format tolerance) and partially addresses OQ-02 (images without alpha — detect and warn, don't fix).

## Interface Contract

### Browser-Side: `src/page/texture-loader.js`

Imported by `src/page/scene-renderer.js` and merged into `window.depthkit`. All functions run inside headless Chromium.

```typescript
// Conceptual contract — implementation is plain JS running in Chromium.
// Types document the contract.

/**
 * Metadata returned after a texture is successfully loaded.
 * JSON-serializable — safe to return via page.evaluate().
 */
interface TextureMetadata {
  /** The caller-assigned texture ID. */
  id: string;
  /** Original image width in pixels. */
  width: number;
  /** Original image height in pixels. */
  height: number;
  /** width / height. Pre-computed for convenience. */
  aspectRatio: number;
  /**
   * Whether the image contains meaningful transparency.
   * Determined by sampling the image's pixel data: if any sampled
   * pixel has alpha < 250, this is true. See alpha detection algorithm.
   */
  hasAlpha: boolean;
}

/**
 * Options for texture loading. All optional with sensible defaults.
 */
interface TextureLoadOptions {
  /**
   * Whether to flip the texture vertically.
   * Three.js TextureLoader defaults to texture.flipY = true, which
   * matches HTML canvas convention (origin top-left). OBJ-015 only
   * explicitly sets texture.flipY when the caller passes flipY: false.
   * When omitted, the Three.js default (true) applies.
   * Default: not set (Three.js default = true).
   */
  flipY?: boolean;

  /**
   * Color space for the texture.
   * 'srgb' → THREE.SRGBColorSpace (correct for photographic/AI-generated images).
   * 'linear' → THREE.LinearSRGBColorSpace (for data textures, normal maps).
   * Default: 'srgb'.
   */
  colorSpace?: 'srgb' | 'linear';

  /**
   * Whether to skip alpha detection for this texture.
   * When true, hasAlpha is always reported as false.
   * Useful for known-opaque textures (backgrounds) to skip the
   * canvas sampling step for performance.
   * Default: false.
   */
  skipAlphaDetection?: boolean;
}

// Extensions to the DepthkitPage interface (window.depthkit)
interface DepthkitPage {
  // ... existing OBJ-010 methods ...

  /**
   * Loads a single texture by URL, detects alpha, caches it by ID,
   * and returns metadata.
   *
   * Internally:
   * 1. Calls THREE.TextureLoader.loadAsync(url) which returns a Promise.
   *    (loadAsync is available since Three.js r148. If unavailable, wraps
   *    loader.load() callbacks in new Promise().)
   * 2. Applies texture settings:
   *    - colorSpace: maps 'srgb' → THREE.SRGBColorSpace,
   *      'linear' → THREE.LinearSRGBColorSpace. Default: SRGBColorSpace.
   *    - flipY: only set explicitly when caller passes flipY: false.
   *    - minFilter: hardcoded to THREE.LinearMipmapLinearFilter (trilinear).
   *    - magFilter: hardcoded to THREE.LinearFilter (bilinear).
   *    These filter settings are optimal for photographic/AI-generated
   *    textures and are not caller-configurable.
   * 3. Detects alpha channel via canvas pixel sampling
   *    (unless skipAlphaDetection is true). If CORS prevents
   *    getImageData(), falls back to hasAlpha: false with console warning.
   * 4. Stores the THREE.Texture in an internal Map<string, THREE.Texture>.
   * 5. Stores TextureMetadata in a parallel Map<string, TextureMetadata>.
   * 6. Returns TextureMetadata.
   *
   * If a texture with the same `id` already exists, the old texture
   * is disposed (texture.dispose()) and replaced. A console warning
   * is logged: "depthkit: replacing existing texture '{id}'".
   *
   * @param id - Unique identifier for this texture. Used by geometry
   *             materialization to reference the loaded texture.
   *             Typically the slot name (e.g., 'floor', 'subject').
   * @param url - URL to load the image from. Supports http://, https://,
   *              data: URIs, and relative paths (resolved relative to
   *              the page's origin). See D1 for URL accessibility constraints.
   * @param options - Optional texture settings.
   * @returns Promise<TextureMetadata> — resolves when load + detection complete.
   * @throws Error if not initialized: "depthkit: not initialized. Call init() first."
   * @throws Error if url is empty/falsy: "depthkit: texture url is required for id '{id}'"
   * @throws Error if id is empty/falsy: "depthkit: texture id is required"
   * @throws Error if the image fails to load (404, network error, corrupt):
   *         "depthkit: failed to load texture '{id}' from '{url}': {original_error}"
   */
  loadTexture(id: string, url: string, options?: TextureLoadOptions): Promise<TextureMetadata>;

  /**
   * Loads multiple textures in parallel and returns all metadata.
   * Wraps loadTexture() with Promise.all().
   *
   * Duplicate ID validation: Before any loading begins, the batch is
   * scanned for duplicate IDs. If found, rejects immediately.
   * If a batch entry's ID matches an already-loaded texture (from a
   * prior call), the existing texture is replaced per loadTexture()
   * replacement semantics.
   *
   * If ANY texture fails to load, the entire batch rejects.
   * Successfully loaded textures from the batch remain in the cache
   * (they are not rolled back). The error message identifies which
   * texture(s) failed.
   *
   * @param entries - Array of { id, url, options? } objects.
   * @returns Promise<TextureMetadata[]> — ordered to match input entries.
   * @throws Error if not initialized.
   * @throws Error if entries is empty: "depthkit: loadTextures requires at least one entry"
   * @throws Error if any entry has duplicate id within the batch:
   *         "depthkit: duplicate texture id '{id}' in batch"
   */
  loadTextures(entries: Array<{
    id: string;
    url: string;
    options?: TextureLoadOptions;
  }>): Promise<TextureMetadata[]>;

  /**
   * Retrieves a loaded THREE.Texture by ID.
   * Used by geometry materialization (downstream of OBJ-011) to
   * assign textures to mesh materials.
   *
   * @param id - The texture ID used during loadTexture().
   * @returns The THREE.Texture, or null if no texture with that ID is loaded.
   */
  getTexture(id: string): THREE.Texture | null;

  /**
   * Retrieves metadata for a loaded texture.
   * Returns the same TextureMetadata that was returned by loadTexture().
   *
   * @param id - The texture ID.
   * @returns TextureMetadata, or null if no texture with that ID is loaded.
   */
  getTextureMetadata(id: string): TextureMetadata | null;

  /**
   * Returns metadata for all currently loaded textures.
   * Useful for diagnostics and for the orchestrator to verify
   * all textures are loaded before rendering begins.
   *
   * @returns Array of TextureMetadata for all loaded textures.
   */
  getAllTextureMetadata(): TextureMetadata[];

  /**
   * Returns the number of currently loaded textures.
   */
  getTextureCount(): number;

  /**
   * Unloads a single texture by ID.
   * Calls texture.dispose() to free GPU/WebGL memory.
   * Removes the texture and its metadata from internal maps.
   *
   * @param id - The texture ID.
   * @returns true if a texture was unloaded, false if id was not found.
   */
  unloadTexture(id: string): boolean;

  /**
   * Unloads all textures. Calls texture.dispose() on each.
   * Clears both the texture map and the metadata map.
   * Called during scene teardown and before dispose().
   */
  unloadAllTextures(): void;
}
```

### Alpha Detection Algorithm

The alpha detection runs inside the browser using a temporary 2D canvas:

1. Create an offscreen `<canvas>` element (not added to DOM).
2. Determine sample dimensions: `sampleWidth = Math.min(image.width, 64)`, `sampleHeight = Math.min(image.height, 64)`. This downscales large images for performance.
3. Set canvas dimensions to `sampleWidth × sampleHeight`.
4. Get 2D context, draw the loaded image scaled to sample dimensions: `ctx.drawImage(image, 0, 0, sampleWidth, sampleHeight)`.
5. Call `ctx.getImageData(0, 0, sampleWidth, sampleHeight)` to get pixel data.
6. Iterate over the alpha channel (every 4th byte starting at index 3): if **any** pixel has `alpha < 250`, return `hasAlpha = true`.
7. If no pixel has alpha < 250, return `hasAlpha = false`.

**CORS fallback:** If `ctx.getImageData()` throws a `SecurityError` (tainted canvas from cross-origin image without CORS headers), alpha detection falls back to `hasAlpha: false` and logs a console warning: `"depthkit: alpha detection failed for texture '{id}' (CORS restriction). Assuming opaque."` The texture is still loaded successfully — only alpha detection fails gracefully.

**Why 250 instead of 255?** JPEG compression and canvas resampling can introduce alpha values of 254-255 on images that are conceptually fully opaque. The threshold of 250 avoids false positives from compression artifacts while still detecting intentional transparency (which typically has alpha values of 0 for fully transparent regions).

**Why 64×64?** At 64×64, only 4,096 pixels are sampled — fast even on CPU. For images with transparent backgrounds (the primary use case), the transparent region is usually large enough that downsampling to 64×64 still captures it. For images with only thin transparent edges, the downsampling might miss them, but such images are functionally opaque for the 2.5D use case.

**Performance:** The entire detection takes <5ms for any image size, as the browser's canvas scaling and pixel readback are highly optimized.

### Node-Side Types: `src/engine/texture-types.ts`

```typescript
// src/engine/texture-types.ts

/**
 * Texture metadata as returned from the page's loadTexture().
 * This is the Node-side mirror — used by the orchestrator to
 * inspect loaded texture properties without touching Three.js types.
 */
export interface TextureMetadata {
  id: string;
  width: number;
  height: number;
  aspectRatio: number;
  hasAlpha: boolean;
}

/**
 * Options for texture loading, passed to the page via page.evaluate().
 * JSON-serializable — no THREE.* constants or numeric magic values.
 * The page maps string values to Three.js constants internally.
 */
export interface TextureLoadOptions {
  flipY?: boolean;
  colorSpace?: 'srgb' | 'linear';
  skipAlphaDetection?: boolean;
}

/**
 * A single entry in a batch texture load command.
 */
export interface TextureLoadEntry {
  id: string;
  url: string;
  options?: TextureLoadOptions;
}

/**
 * A warning generated when a texture's alpha status doesn't match
 * the slot's transparency expectation.
 */
export interface TextureSlotWarning {
  /** The texture ID (typically matches the slot name). */
  textureId: string;
  /** The slot name in the geometry. */
  slotName: string;
  /** The geometry name. */
  geometryName: string;
  /** Warning severity. */
  severity: 'warning' | 'info';
  /** Human-readable warning message. */
  message: string;
}
```

### Node-Side Warning Utility: `src/engine/texture-warnings.ts`

```typescript
// src/engine/texture-warnings.ts

import type { TextureMetadata, TextureSlotWarning } from './texture-types.js';
import type { SceneGeometry } from '../scenes/geometries/types.js';

/**
 * Checks loaded texture metadata against a geometry's slot expectations
 * and returns warnings for mismatches.
 *
 * Warnings are generated for:
 * 1. A slot has `transparent: true` but the loaded texture has `hasAlpha: false`.
 *    This means the image will display with hard rectangular edges in the scene.
 *    Severity: 'warning'.
 *    Message: "Texture '{id}' for slot '{slot}' in geometry '{geo}' has no alpha
 *    channel, but this slot expects transparency. The image will appear as a
 *    hard-edged rectangle. Consider using an image with a transparent background
 *    or applying background removal before rendering."
 *
 * 2. A slot has `transparent: false` (or undefined) but the loaded texture has
 *    `hasAlpha: true`. This is informational — the alpha will be ignored since
 *    the material won't enable transparency blending.
 *    Severity: 'info'.
 *    Message: "Texture '{id}' for slot '{slot}' in geometry '{geo}' has an alpha
 *    channel, but this slot does not use transparency. Alpha will be ignored."
 *
 * Slots not present in slotToTextureId are skipped (optional slots without textures).
 * Texture IDs in slotToTextureId not found in textureMetadata are skipped
 * (texture may not have been loaded yet, or validation is handled elsewhere).
 *
 * @param textureMetadata - Record mapping texture ID → TextureMetadata.
 * @param geometry - The SceneGeometry definition with slot expectations.
 * @param slotToTextureId - Record mapping slot name → texture ID. Not all slots
 *                          need entries (optional slots may be omitted).
 * @returns Array of TextureSlotWarning. Empty if no mismatches.
 */
export function checkTextureSlotCompatibility(
  textureMetadata: Record<string, TextureMetadata>,
  geometry: SceneGeometry,
  slotToTextureId: Record<string, string>
): TextureSlotWarning[];
```

## Design Decisions

### D1: Texture Loading Runs in the Browser, Commanded by the Orchestrator

**Decision:** The texture loader is a browser-side module (part of `window.depthkit`). The orchestrator triggers texture loading via `page.evaluate()`, passing URLs. The page loads images via `THREE.TextureLoader`, which uses the browser's native image decoding.

**Rationale:** Three.js `TextureLoader` relies on `HTMLImageElement` for image decoding — this only works in a browser context. Loading must happen where Three.js runs. The "dumb page" architecture (OBJ-010 D1) means the page receives load commands and reports metadata back, but holds no domain logic about *which* textures to load or *when*.

**URL accessibility constraint:** The URLs passed to `loadTexture()` must be resolvable by the browser's image loading mechanism. When the page is loaded from a local file (`file://` protocol), CORS restrictions may prevent loading local images via relative paths or `file://` URLs — `ctx.getImageData()` will throw on tainted canvases, and `fetch()`-based loading may be blocked entirely. The orchestrator (OBJ-009/OBJ-011) is responsible for ensuring images are accessible — e.g., by serving the page and images via a local HTTP server, using `data:` URIs, or using Puppeteer request interception. OBJ-015 treats URL resolution as opaque and reports load failures via the error path. Alpha detection has a CORS fallback (see Alpha Detection Algorithm).

### D2: Texture Keyed by Caller-Assigned String ID

**Decision:** Each texture is stored in a `Map<string, THREE.Texture>` keyed by a string ID provided by the caller. The ID is typically the slot name (e.g., `'floor'`, `'subject'`), but the loader imposes no naming constraint — it treats IDs as opaque strings.

**Rationale:** Slot names are the natural key for texture → mesh assignment. By using the slot name as the texture ID, geometry materialization (downstream) can call `getTexture('floor')` without a separate mapping table. However, keeping IDs opaque allows flexibility for non-slot textures (e.g., HUD layer textures, transition masks) if needed in the future.

### D3: Alpha Detection via Canvas Pixel Sampling, Not Format Sniffing

**Decision:** Alpha is detected by actually sampling pixel data from the loaded image, not by checking the file extension or MIME type.

**Alternatives considered:**
1. **Format sniffing** (JPEG = no alpha, PNG = maybe alpha) — unreliable. PNGs can be fully opaque. WebP can be either. Data URIs obscure the original format.
2. **Full-resolution pixel scan** — accurate but slow for large images (a 4K image = 33M pixels).
3. **Downscaled sampling** (chosen) — draws the image to a 64×64 canvas and scans 4,096 pixels. Fast, and sufficient for detecting transparent backgrounds.

**Rationale:** The purpose is to detect whether the image has meaningful transparency (as in background-removed subject images), not to detect single-pixel alpha variations. Downscaling to 64×64 reliably catches transparent backgrounds while keeping detection under 5ms.

### D4: Replacement Semantics for Duplicate IDs

**Decision:** If `loadTexture()` is called with an ID that already exists, the old texture is disposed and replaced. A console warning is logged.

**Rationale:** During scene transitions, the orchestrator may reuse slot names across scenes. Rather than requiring explicit unload-before-load, replacement semantics keep the API simple. The warning helps catch accidental overwrites during development.

### D5: Batch Loading via Promise.all (Fail-Fast)

**Decision:** `loadTextures()` uses `Promise.all()` — if any texture fails, the entire batch rejects. Successfully loaded textures remain in the cache.

**Alternatives considered:**
1. **`Promise.allSettled()`** — returns all results (fulfilled and rejected). More resilient but requires the caller to inspect each result.
2. **`Promise.all()`** (chosen) — simpler error handling. The orchestrator's expected pattern is "load all textures for a scene → if any fail, abort the scene."

**Rationale:** Partial scene rendering (where some textures are missing) produces broken output — a plane with no texture is worse than failing. Fail-fast matches the engine's "fail fast, fail clearly" philosophy (C-10).

### D6: Warning Utility on Node Side, Not Page Side

**Decision:** The `checkTextureSlotCompatibility()` function runs on the Node side, not in the browser page. The page reports `hasAlpha` per texture; the orchestrator cross-references this with geometry slot definitions (from OBJ-005).

**Rationale:** The page is a "dumb renderer" (OBJ-010 D1). It doesn't know about geometry definitions, slot names, or the `transparent` field on `PlaneSlot`. Cross-referencing texture metadata with geometry contracts is domain logic that belongs on the Node side.

### D7: `sRGBColorSpace` as Default

**Decision:** Textures default to `THREE.SRGBColorSpace`.

**Rationale:** All depthkit textures are photographic or AI-generated images, which are authored in sRGB color space. Using `SRGBColorSpace` ensures Three.js applies correct gamma decoding. `LinearSRGBColorSpace` is only needed for data textures (e.g., normal maps), which depthkit V1 doesn't use.

### D8: `dispose()` Extension via Direct Modification of `scene-renderer.js`

**Decision:** `scene-renderer.js` imports `texture-loader.js`'s `unloadAllTextures` function and calls it within its existing `dispose()` function body, **before** calling `renderer.forceContextLoss()`. This is a direct modification to `scene-renderer.js`'s `dispose()` implementation, not a hook or monkey-patch system.

**Mechanism:** The `dispose()` function in `scene-renderer.js` (defined by OBJ-010) is modified to insert `unloadAllTextures()` as the first step:
```
dispose() {
  unloadAllTextures();   // ← added by OBJ-015
  // ... existing OBJ-010 dispose logic:
  renderer.forceContextLoss();
  renderer.dispose();
  renderer = null;
  scene = null;
  camera = null;
}
```

**Rationale:** Textures hold GPU memory referenced by the WebGL context. They must be disposed before the context is force-lost. Inserting the call directly into `dispose()` is simpler and more reliable than a hook system, and matches the "single source of truth" principle.

### D9: No Texture Resizing or Clamping to MAX_TEXTURE_SIZE

**Decision:** OBJ-015 does not resize images that exceed the WebGL context's `MAX_TEXTURE_SIZE`. If an image exceeds the limit, Three.js handles it (it downscales automatically in modern versions).

**Rationale:** `MAX_TEXTURE_SIZE` is typically 4096 (SwiftShader) to 16384 (modern GPUs). depthkit's recommended image sizes (1920×1080 to 4K) are within these limits. Adding explicit resizing logic would add complexity for an edge case that Three.js already handles. The `getRendererInfo().maxTextureSize` (from OBJ-010) allows the orchestrator to warn upstream if needed — but that's outside OBJ-015's scope.

### D10: Hardcoded Texture Filters (Not Caller-Configurable)

**Decision:** `minFilter` and `magFilter` are hardcoded in the page-side code: `THREE.LinearMipmapLinearFilter` (trilinear) for minification, `THREE.LinearFilter` (bilinear) for magnification. These are not exposed in `TextureLoadOptions`.

**Alternatives considered:**
1. **Expose as Three.js numeric constants** — breaks the dumb-page contract; Node side would need to know magic numbers like `1008`.
2. **Expose as string literals** (e.g., `'nearest' | 'linear'`) — adds API surface for knobs no one will turn.
3. **Hardcode** (chosen) — trilinear/bilinear are universally correct for photographic textures.

**Rationale:** These filters are the correct choice for every depthkit use case (AI-generated and photographic images). Exposing them adds API complexity without benefit. If a future use case needs different filters (e.g., pixel-art nearest-neighbor), a new option can be added then.

## Acceptance Criteria

- [ ] **AC-01:** `src/page/texture-loader.js` exports functions that are merged into `window.depthkit`: `loadTexture`, `loadTextures`, `getTexture`, `getTextureMetadata`, `getAllTextureMetadata`, `getTextureCount`, `unloadTexture`, `unloadAllTextures`.

- [ ] **AC-02:** After `loadTexture('bg', url)` resolves, `getTexture('bg')` returns a `THREE.Texture` instance (non-null), and `getTextureMetadata('bg')` returns a `TextureMetadata` object with `id === 'bg'`, numeric `width > 0`, `height > 0`, `aspectRatio > 0`, and a boolean `hasAlpha`.

- [ ] **AC-03:** A PNG image with a transparent background (e.g., a subject isolated on transparency) is detected as `hasAlpha: true`.

- [ ] **AC-04:** A JPEG image (which cannot have alpha) is detected as `hasAlpha: false`.

- [ ] **AC-05:** A PNG image that is fully opaque (all pixels have alpha 255) is detected as `hasAlpha: false`.

- [ ] **AC-06:** After `loadTexture()`, the returned `TextureMetadata.width` and `.height` match the original image's natural dimensions (not the 64×64 sampling size).

- [ ] **AC-07:** `loadTextures([{id:'a', url:url1}, {id:'b', url:url2}])` loads both textures in parallel. After resolution, `getTexture('a')` and `getTexture('b')` both return non-null textures. Returned metadata array has length 2 and is ordered to match input.

- [ ] **AC-08:** `loadTextures()` with a batch where one URL is invalid (404) rejects with an error message identifying the failed texture. Textures that loaded successfully remain in the cache.

- [ ] **AC-09:** Calling `loadTexture('x', url)` when a texture with id `'x'` already exists: the old texture is disposed (`texture.dispose()` called), the new texture replaces it, and a console warning is logged containing the string `"replacing existing texture 'x'"`.

- [ ] **AC-10:** `unloadTexture('bg')` disposes the texture (`texture.dispose()` called), removes it from both internal maps, and returns `true`. Subsequent `getTexture('bg')` returns `null`. Calling `unloadTexture('nonexistent')` returns `false`.

- [ ] **AC-11:** `unloadAllTextures()` disposes all loaded textures and clears both maps. `getTextureCount()` returns 0 afterward.

- [ ] **AC-12:** Calling any texture method (`loadTexture`, `getTexture`, etc.) before `init()` throws: `"depthkit: not initialized. Call init() first."`

- [ ] **AC-13:** `loadTexture('x', '')` throws: `"depthkit: texture url is required for id 'x'"`. `loadTexture('', url)` throws: `"depthkit: texture id is required"`.

- [ ] **AC-14:** Loading a texture with `{ skipAlphaDetection: true }` returns `hasAlpha: false` regardless of actual image content.

- [ ] **AC-15:** Loaded textures default to `THREE.SRGBColorSpace`. Loading with `{ colorSpace: 'linear' }` sets `THREE.LinearSRGBColorSpace`.

- [ ] **AC-16:** `window.depthkit.dispose()` calls `unloadAllTextures()` before `renderer.forceContextLoss()`. After dispose, `getTextureCount()` returns 0.

- [ ] **AC-17:** `src/engine/texture-types.ts` exports `TextureMetadata`, `TextureLoadOptions`, `TextureLoadEntry`, and `TextureSlotWarning` types.

- [ ] **AC-18:** `src/engine/texture-warnings.ts` exports `checkTextureSlotCompatibility()`. Given a texture with `hasAlpha: false` and a slot with `transparent: true`, it returns a warning with severity `'warning'` and a message mentioning "no alpha channel" and "hard-edged rectangle".

- [ ] **AC-19:** `checkTextureSlotCompatibility()` given a texture with `hasAlpha: true` and a slot with `transparent: false` (or undefined), returns an info-level entry mentioning alpha will be ignored.

- [ ] **AC-20:** `checkTextureSlotCompatibility()` returns an empty array when alpha status matches slot expectations (both true, or both false/undefined).

- [ ] **AC-21:** `loadTextures()` with duplicate IDs in the same batch rejects synchronously (before any loading begins): `"depthkit: duplicate texture id '{id}' in batch"`.

- [ ] **AC-22:** `loadTextures([])` (empty array) rejects: `"depthkit: loadTextures requires at least one entry"`.

- [ ] **AC-23:** After `loadTexture('bg', url)` resolves, a mesh created with `new THREE.MeshBasicMaterial({ map: window.depthkit.getTexture('bg') })` added to `window.depthkit.scene` and rendered via `renderFrame()` produces a visible (non-black) frame when captured via `canvas.toDataURL()`.

- [ ] **AC-24:** Texture `minFilter` is `THREE.LinearMipmapLinearFilter` and `magFilter` is `THREE.LinearFilter` on all loaded textures. These are not configurable via `TextureLoadOptions`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `loadTexture()` before `init()` | Throws `"depthkit: not initialized. Call init() first."` |
| `loadTexture('', url)` | Throws `"depthkit: texture id is required"` |
| `loadTexture('x', '')` | Throws `"depthkit: texture url is required for id 'x'"` |
| `loadTexture('x', null)` or `undefined` | Throws `"depthkit: texture url is required for id 'x'"` (falsy check) |
| URL returns 404 | Rejects: `"depthkit: failed to load texture 'x' from '{url}': {error}"` |
| URL points to non-image file | Rejects with same error format (browser image decode fails) |
| Corrupt/truncated image file | Rejects with same error format |
| Image exceeds MAX_TEXTURE_SIZE | Three.js auto-downscales. Metadata reports original image dimensions. |
| Replacing existing texture ID | Old texture disposed, new one stored, console warning logged |
| `loadTextures` with one failure | Promise rejects. Successfully loaded textures remain cached. |
| `loadTextures` with duplicate IDs in batch | Rejects synchronously before loading any textures |
| `loadTextures` with batch ID matching already-loaded texture | Existing texture replaced per `loadTexture()` replacement semantics |
| `loadTextures` with empty array | Rejects: `"depthkit: loadTextures requires at least one entry"` |
| `getTexture('nonexistent')` | Returns `null` |
| `getTextureMetadata('nonexistent')` | Returns `null` |
| `unloadTexture('nonexistent')` | Returns `false` (no-op) |
| `unloadAllTextures()` when no textures loaded | No-op, no error |
| `dispose()` with loaded textures | `unloadAllTextures()` called before `renderer.forceContextLoss()` |
| Data URI as URL | Loads normally (browser handles data URIs natively) |
| Very large image (e.g., 8000×6000 PNG) | Loads normally. Alpha detection uses 64×64 downscale, so performance is constant. |
| Image with semi-transparent pixels (alpha ~128) | Detected as `hasAlpha: true` (128 < 250) |
| Image with nearly-opaque pixels (alpha 251-254) | Detected as `hasAlpha: false` (251 > 250). These artifacts are not meaningful transparency. |
| Cross-origin image without CORS headers | Texture loads successfully. Alpha detection `getImageData()` throws SecurityError → falls back to `hasAlpha: false`, logs warning: `"depthkit: alpha detection failed for texture '{id}' (CORS restriction). Assuming opaque."` |
| `checkTextureSlotCompatibility` with slot not in slotToTextureId | Skipped — no warning. Optional slots without textures are valid. |
| `checkTextureSlotCompatibility` with texture ID not in metadata record | Skipped — texture wasn't loaded (may be handled by other validation). |

## Test Strategy

### Puppeteer-Based Integration Tests (Primary)

These tests launch headless Chromium, load the depthkit page, call `init()`, and exercise texture loading with real images.

**Test images required:** A set of small test images should be created or provided:
- `opaque.jpg` — A small JPEG (e.g., 100×75), fully opaque.
- `opaque.png` — A small PNG (e.g., 80×60), fully opaque (no alpha channel, or all pixels alpha=255).
- `transparent.png` — A small PNG (e.g., 100×100) with transparent background (e.g., a colored circle on transparency).
- `semitransparent.png` — A small PNG with semi-transparent regions (alpha ~128).
- `large_opaque.png` — A larger image (e.g., 2048×1024) to verify metadata reports original dimensions.

These test images must be served to the browser via a local HTTP server or Puppeteer request interception (not `file://` URLs, due to CORS constraints on `getImageData()`).

**Load and metadata tests:**
1. Load `opaque.jpg` → verify metadata: `hasAlpha: false`, width/height match, aspectRatio ≈ width/height.
2. Load `opaque.png` → verify `hasAlpha: false`.
3. Load `transparent.png` → verify `hasAlpha: true`.
4. Load `semitransparent.png` → verify `hasAlpha: true`.
5. Load `large_opaque.png` → verify metadata reports original dimensions (2048×1024), not 64×64.
6. Load with `skipAlphaDetection: true` on `transparent.png` → verify `hasAlpha: false`.

**Texture renderability test:**
7. Load a texture, create a `MeshBasicMaterial` with it as `map`, add a plane mesh to the scene, call `renderFrame()`, capture `canvas.toDataURL()` → verify the frame is not all-black. (Validates that the texture is usable for rendering, not just stored.)

**Texture retrieval tests:**
8. After load, `getTexture(id)` returns a Three.js Texture (has `.image` property).
9. `getTexture('nonexistent')` returns null.
10. `getTextureMetadata(id)` returns the same metadata as loadTexture resolved with.
11. `getAllTextureMetadata()` returns array with correct length after loading N textures.
12. `getTextureCount()` reflects number of loaded textures.

**Batch loading tests:**
13. `loadTextures` with 3 entries → all resolve, metadata array has length 3 in order.
14. `loadTextures` with one bad URL → rejects, good textures remain in cache.
15. `loadTextures([])` → rejects with expected message.
16. `loadTextures` with duplicate IDs → rejects with expected message before any loading.

**Lifecycle tests:**
17. `unloadTexture(id)` → `getTexture(id)` returns null, `getTextureCount()` decremented.
18. `unloadAllTextures()` → `getTextureCount() === 0`.
19. Load, then load same ID again → old texture replaced, warning logged (verify via `page.on('console')`).
20. `dispose()` after loading textures → `getTextureCount() === 0` after re-init.

**Error condition tests:**
21. Any texture method before `init()` → throws expected error.
22. Empty/falsy id or url → throws expected error.
23. 404 URL → rejects with expected error format.

**Color space tests:**
24. Load with `colorSpace: 'srgb'` → `texture.colorSpace === THREE.SRGBColorSpace`.
25. Load with `colorSpace: 'linear'` → `texture.colorSpace === THREE.LinearSRGBColorSpace`.
26. Load with default → `texture.colorSpace === THREE.SRGBColorSpace`.

**Filter tests:**
27. Load any texture → verify `texture.minFilter === THREE.LinearMipmapLinearFilter` and `texture.magFilter === THREE.LinearFilter`.

### Node-Side Unit Tests

28. `checkTextureSlotCompatibility` with alpha-mismatch → returns warning.
29. `checkTextureSlotCompatibility` with matching alpha → returns empty array.
30. `checkTextureSlotCompatibility` with `hasAlpha: true` / `transparent: false` → returns info.
31. `checkTextureSlotCompatibility` with missing slot entries → no warning for missing slots.
32. `checkTextureSlotCompatibility` with texture ID not in metadata → skipped, no warning.
33. Types compile without error.

### Relevant Testable Claims

- **TC-02** (render performance): Texture loading time adds to per-scene setup. Load time should be measured but is not per-frame — it's a one-time cost per scene.
- **C-09** (image format tolerance): AC-03/04/05 directly validate this constraint.
- **OQ-02** (images without alpha): AC-03/04/05 + AC-18 partially address this — detect and warn.

## Integration Points

### Depends on

| Dependency | What OBJ-015 uses |
|---|---|
| **OBJ-010** (Page shell) | `window.depthkit.scene`, `window.depthkit.renderer` (for WebGL context), `window.depthkit.isInitialized()` guard, the `init()`/`dispose()` lifecycle. OBJ-015 modifies `scene-renderer.js`'s `dispose()` to call `unloadAllTextures()` before renderer disposal. |

### Consumed by

| Downstream | How it uses OBJ-015 |
|---|---|
| **OBJ-011** (Message protocol) | Defines message types that trigger `loadTexture()`/`loadTextures()` on the page. Uses `TextureMetadata` in response messages. May invoke `checkTextureSlotCompatibility()` on the Node side after loading to emit warnings. |
| **OBJ-039** (Scene setup / geometry materialization) | Calls `getTexture(slotName)` to retrieve loaded textures and assign them to mesh materials during scene instantiation. Uses `getTextureMetadata()` for aspect-ratio-aware plane sizing. |
| **OBJ-040** (Aspect ratio / edge-reveal validation) | Uses `TextureMetadata.aspectRatio` and `TextureMetadata.width`/`height` to verify plane sizing against texture dimensions. |
| **OBJ-052** (Subtitle/caption overlay) | May use texture loading for HUD layer images. |

### File Placement

```
depthkit/
  src/
    engine/
      texture-types.ts       # NEW — TextureMetadata, TextureLoadOptions, TextureLoadEntry, TextureSlotWarning
      texture-warnings.ts    # NEW — checkTextureSlotCompatibility()
    page/
      texture-loader.js      # NEW — browser-side texture loading, alpha detection, cache
      scene-renderer.js      # MODIFY — import texture-loader.js, merge into window.depthkit, add unloadAllTextures() call to dispose()
```

## Open Questions

### OQ-A: Should the texture loader report a warning for images exceeding MAX_TEXTURE_SIZE?

`getRendererInfo().maxTextureSize` is available after init. The texture loader could check `image.width` and `image.height` against this value and include a boolean `exceedsMaxTextureSize` in the metadata, or log a warning. Three.js auto-downscales, so this is informational only. **Recommendation:** Defer for V1. The check would require accessing the renderer's GL context from within the texture loader, coupling it to the renderer. The orchestrator can compare metadata dimensions against `getRendererInfo().maxTextureSize` on the Node side if needed.

### OQ-B: Should `loadTextures` use `Promise.allSettled` instead of `Promise.all`?

`Promise.all` fails fast — one bad texture aborts the whole batch. `Promise.allSettled` would let the orchestrator decide what to do with partial results. The current design uses `Promise.all` for simplicity and because partial scenes are broken scenes. If downstream objectives find this too aggressive, it could be revisited.

### OQ-C: Should the alpha detection threshold (250) be configurable?

The threshold is hardcoded at 250. Some use cases might want stricter detection (255 = only perfectly opaque is "no alpha") or looser (200 = ignore minor transparency). **Recommendation:** Hardcode 250 for V1. The threshold is a heuristic that works for the overwhelmingly common case (background-removed images vs. fully opaque images). Expose as configurable only if tuning reveals edge cases.

---

## Changes from Round 1 (addressing challenger feedback)

| Issue # | Severity | Resolution |
|---------|----------|------------|
| **7** | Critical | Removed OBJ-036 from "Consumed by". Corrected downstream list to match DAG: OBJ-011, OBJ-039, OBJ-040, OBJ-052. |
| **1** | Major | Removed `minFilter`/`magFilter` from `TextureLoadOptions`. Hardcoded in page-side code. Added D10 design decision with rationale. Added AC-24 for filter verification. |
| **2** | Major | Added D8 specifying the exact mechanism: `scene-renderer.js`'s `dispose()` is modified to call `unloadAllTextures()` before `renderer.forceContextLoss()`. Included pseudocode showing insertion point. |
| **5** | Major | Added URL accessibility constraint paragraph to D1. Documented `file://` CORS limitation and orchestrator's responsibility. Updated test strategy to require HTTP server for test images. |
| **3** | Minor | Added note to `loadTexture` doc: "Calls `THREE.TextureLoader.loadAsync(url)` (available since Three.js r148)." |
| **4** | Minor | Changed `checkTextureSlotCompatibility` first param from `Map<string, TextureMetadata>` to `Record<string, TextureMetadata>`. |
| **6** | Minor | Clarified `flipY` in `TextureLoadOptions`: "OBJ-015 only explicitly sets `texture.flipY` when the caller passes `flipY: false`. When omitted, the Three.js default (true) applies." |
| **8** | Minor | Added AC-23: renderability smoke test — load texture, create material + mesh, render, verify non-black frame via `toDataURL()`. |
| **9** | Minor | Added CORS fallback to alpha detection algorithm: catches SecurityError, falls back to `hasAlpha: false` with console warning. Added to edge cases table. |
| **10** | Minor | Added explicit sentence to `loadTextures` doc: "If a batch entry's ID matches an already-loaded texture (from a prior call), the existing texture is replaced per `loadTexture()` semantics." Added to edge cases table. |
| **11** | Minor | Subsumed by Issue 7 fix. |

I believe all 11 issues have been addressed. Challenger, please verify and approve.

---

## Round 4 — spec_challenger

I'll verify each fix against the revised spec.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]
## Verification of Round 2 Fixes

I'll verify each of my 11 issues against the revised spec:

| # | Severity | Issue | Verified? |
|---|----------|-------|-----------|
| **7** | Critical | Wrong OBJ-036 reference | ✅ Removed. "Consumed by" now lists OBJ-011, OBJ-039, OBJ-040, OBJ-052 — matches DAG. |
| **1** | Major | `minFilter`/`magFilter` as raw numbers | ✅ Removed from `TextureLoadOptions`. D10 added with rationale. AC-24 verifies hardcoded values. |
| **2** | Major | `dispose()` extension mechanism | ✅ D8 specifies direct modification of `scene-renderer.js`, with pseudocode showing insertion before `forceContextLoss()`. |
| **5** | Major | Local file URL accessibility | ✅ D1 has explicit paragraph on CORS constraints and orchestrator responsibility. Test strategy requires HTTP server. |
| **3** | Minor | Promise creation mechanism | ✅ `loadTexture` doc notes `THREE.TextureLoader.loadAsync(url)` (r148+). |
| **4** | Minor | `Map` vs `Record` | ✅ Changed to `Record<string, TextureMetadata>`. |
| **6** | Minor | `flipY` default | ✅ Clarified: "only explicitly sets texture.flipY when the caller passes flipY: false." |
| **8** | Minor | No AC for renderability | ✅ AC-23 added: load texture → create material+mesh → renderFrame → verify non-black via toDataURL. |
| **9** | Minor | CORS fallback for alpha | ✅ Algorithm section documents SecurityError catch → `hasAlpha: false` + console warning. Edge cases table includes it. |
| **10** | Minor | Batch vs existing duplicate semantics | ✅ `loadTextures` doc has explicit sentence. Edge cases table has "batch ID matching already-loaded texture" row. |
| **11** | Minor | OBJ-036 consumer | ✅ Subsumed by Issue 7 fix. |

All 11 issues are structurally addressed in the revised spec. No new issues introduced by the revisions.

The spec is clean, implementable, and correctly scoped. Contracts are precise, ACs are testable, edge cases are comprehensive, vocabulary is consistent, and integration points match the DAG.

CONCLUSION:

The spec for OBJ-015 (Texture Loader and Format Handling) is approved. It defines: (1) browser-side texture loading via `THREE.TextureLoader.loadAsync()` exposed on `window.depthkit`, (2) alpha detection via 64×64 canvas pixel sampling with threshold 250 and CORS fallback, (3) texture metadata reporting, (4) Node-side `checkTextureSlotCompatibility()` warning utility, (5) texture lifecycle management including `dispose()` integration. 24 acceptance criteria, comprehensive edge cases, and a test strategy with 33 test cases covering Puppeteer integration and Node-side unit tests.

Let me write the final spec and update meta.json.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/output.md",
  "content": "# Specification: OBJ-015 \u2014 Texture Loader and Format Handling\n\n## Summary\n\nOBJ-015 defines the browser-side texture loading module and its associated Node-side types. It provides: (1) a `THREE.TextureLoader`-based async texture loading API exposed on `window.depthkit`, with textures stored in a keyed map for retrieval by downstream geometry materialization; (2) alpha channel detection that samples loaded image pixel data to distinguish images with genuine transparency from those without; (3) texture metadata reporting (dimensions, aspect ratio, `hasAlpha`) back to the Node.js orchestrator; (4) a Node-side warning utility that flags non-transparent images assigned to slots that expect alpha (per OBJ-005's `PlaneSlot.transparent` field); and (5) texture lifecycle management (load, retrieve, unload, dispose). This directly satisfies C-09 (image format tolerance) and partially addresses OQ-02 (images without alpha \u2014 detect and warn, don't fix).\n\n## Interface Contract\n\n### Browser-Side: `src/page/texture-loader.js`\n\nImported by `src/page/scene-renderer.js` and merged into `window.depthkit`. All functions run inside headless Chromium.\n\n```typescript\n// Conceptual contract \u2014 implementation is plain JS running in Chromium.\n// Types document the contract.\n\n/**\n * Metadata returned after a texture is successfully loaded.\n * JSON-serializable \u2014 safe to return via page.evaluate().\n */\ninterface TextureMetadata {\n  /** The caller-assigned texture ID. */\n  id: string;\n  /** Original image width in pixels. */\n  width: number;\n  /** Original image height in pixels. */\n  height: number;\n  /** width / height. Pre-computed for convenience. */\n  aspectRatio: number;\n  /**\n   * Whether the image contains meaningful transparency.\n   * Determined by sampling the image's pixel data: if any sampled\n   * pixel has a
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-015",
     3→  "description": "Texture loader and format handling -- Three.js TextureLoader usage, alpha channel detection (distinguishing images with and without transparency), aspect ratio reading from loaded textures (texture.image.width/height), handling of non-transparent images on subject/foreground planes (warning about rectangular edges). Covers C-09 (image format tolerance) and partially addresses OQ-02 (images without alpha).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-010"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Runs inside the browser page -- depends on page shell (OBJ-010)."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/meta.json",
  "content": "{\n  \"id\": \"OBJ-015\",\n  \"description\": \"Texture loader and format handling -- Three.js TextureLoader usage, alpha channel detection (distinguishing images with and without transparency), aspect ratio reading from loaded textures (texture.image.width/height), handling of non-transparent images on subject/foreground planes (warning about rectangular edges). Covers C-09 (image format tolerance) and partially addresses OQ-02 (images without alpha).\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-010\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 engine core. Runs inside the browser page -- depends on page shell (OBJ-010). Spec defines browser-side texture loading API (loadTexture/loadTextures/getTexture/unload), alpha detection via 64x64 canvas sampling with threshold 250, Node-side checkTextureSlotCompatibility() warning utility, and dispose() integration. Blocks OBJ-039, OBJ-040, OBJ-052.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/meta.json has been updated successfully.
Now commit:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-015/output.md nodes/OBJ-015/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-015): Texture loader and format handling specification\n\nDefines browser-side texture loading API (loadTexture/loadTextures/\ngetTexture/unload) on window.depthkit, alpha channel detection via\n64x64 canvas pixel sampling with threshold 250 and CORS fallback,\nNode-side checkTextureSlotCompatibility() warning utility, and\ndispose() integration. 24 acceptance criteria, 33 test cases.\n\nSatisfies C-09 (image format tolerance), partially addresses OQ-02.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-015 spec files"
}
[Tool Result] [master 6c02bd2] spec(OBJ-015): Texture loader and format handling specification
 2 files changed, 608 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-015/output.md
Spec committed. The OBJ-015 specification is finalized with all 11 review issues resolved across 4 rounds of deliberation.
