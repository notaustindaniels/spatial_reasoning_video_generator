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
   * 'srgb' -> THREE.SRGBColorSpace (correct for photographic/AI-generated images).
   * 'linear' -> THREE.LinearSRGBColorSpace (for data textures, normal maps).
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
   *    - colorSpace: maps 'srgb' -> THREE.SRGBColorSpace,
   *      'linear' -> THREE.LinearSRGBColorSpace. Default: SRGBColorSpace.
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
3. Set canvas dimensions to `sampleWidth x sampleHeight`.
4. Get 2D context, draw the loaded image scaled to sample dimensions: `ctx.drawImage(image, 0, 0, sampleWidth, sampleHeight)`.
5. Call `ctx.getImageData(0, 0, sampleWidth, sampleHeight)` to get pixel data.
6. Iterate over the alpha channel (every 4th byte starting at index 3): if **any** pixel has `alpha < 250`, return `hasAlpha = true`.
7. If no pixel has alpha < 250, return `hasAlpha = false`.

**CORS fallback:** If `ctx.getImageData()` throws a `SecurityError` (tainted canvas from cross-origin image without CORS headers), alpha detection falls back to `hasAlpha: false` and logs a console warning: `"depthkit: alpha detection failed for texture '{id}' (CORS restriction). Assuming opaque."` The texture is still loaded successfully — only alpha detection fails gracefully.

**Why 250 instead of 255?** JPEG compression and canvas resampling can introduce alpha values of 254-255 on images that are conceptually fully opaque. The threshold of 250 avoids false positives from compression artifacts while still detecting intentional transparency (which typically has alpha values of 0 for fully transparent regions).

**Why 64x64?** At 64x64, only 4,096 pixels are sampled — fast even on CPU. For images with transparent backgrounds (the primary use case), the transparent region is usually large enough that downsampling to 64x64 still captures it. For images with only thin transparent edges, the downsampling might miss them, but such images are functionally opaque for the 2.5D use case.

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
 * @param textureMetadata - Record mapping texture ID -> TextureMetadata.
 * @param geometry - The SceneGeometry definition with slot expectations.
 * @param slotToTextureId - Record mapping slot name -> texture ID. Not all slots
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

**Rationale:** Slot names are the natural key for texture -> mesh assignment. By using the slot name as the texture ID, geometry materialization (downstream) can call `getTexture('floor')` without a separate mapping table. However, keeping IDs opaque allows flexibility for non-slot textures (e.g., HUD layer textures, transition masks) if needed in the future.

### D3: Alpha Detection via Canvas Pixel Sampling, Not Format Sniffing

**Decision:** Alpha is detected by actually sampling pixel data from the loaded image, not by checking the file extension or MIME type.

**Alternatives considered:**
1. **Format sniffing** (JPEG = no alpha, PNG = maybe alpha) — unreliable. PNGs can be fully opaque. WebP can be either. Data URIs obscure the original format.
2. **Full-resolution pixel scan** — accurate but slow for large images (a 4K image = 33M pixels).
3. **Downscaled sampling** (chosen) — draws the image to a 64x64 canvas and scans 4,096 pixels. Fast, and sufficient for detecting transparent backgrounds.

**Rationale:** The purpose is to detect whether the image has meaningful transparency (as in background-removed subject images), not to detect single-pixel alpha variations. Downscaling to 64x64 reliably catches transparent backgrounds while keeping detection under 5ms.

### D4: Replacement Semantics for Duplicate IDs

**Decision:** If `loadTexture()` is called with an ID that already exists, the old texture is disposed and replaced. A console warning is logged.

**Rationale:** During scene transitions, the orchestrator may reuse slot names across scenes. Rather than requiring explicit unload-before-load, replacement semantics keep the API simple. The warning helps catch accidental overwrites during development.

### D5: Batch Loading via Promise.all (Fail-Fast)

**Decision:** `loadTextures()` uses `Promise.all()` — if any texture fails, the entire batch rejects. Successfully loaded textures remain in the cache.

**Alternatives considered:**
1. **`Promise.allSettled()`** — returns all results (fulfilled and rejected). More resilient but requires the caller to inspect each result.
2. **`Promise.all()`** (chosen) — simpler error handling. The orchestrator's expected pattern is "load all textures for a scene -> if any fail, abort the scene."

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
  unloadAllTextures();   // <-- added by OBJ-015
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

**Rationale:** `MAX_TEXTURE_SIZE` is typically 4096 (SwiftShader) to 16384 (modern GPUs). depthkit's recommended image sizes (1920x1080 to 4K) are within these limits. Adding explicit resizing logic would add complexity for an edge case that Three.js already handles. The `getRendererInfo().maxTextureSize` (from OBJ-010) allows the orchestrator to warn upstream if needed — but that's outside OBJ-015's scope.

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

- [ ] **AC-06:** After `loadTexture()`, the returned `TextureMetadata.width` and `.height` match the original image's natural dimensions (not the 64x64 sampling size).

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
| Very large image (e.g., 8000x6000 PNG) | Loads normally. Alpha detection uses 64x64 downscale, so performance is constant. |
| Image with semi-transparent pixels (alpha ~128) | Detected as `hasAlpha: true` (128 < 250) |
| Image with nearly-opaque pixels (alpha 251-254) | Detected as `hasAlpha: false` (251 > 250). These artifacts are not meaningful transparency. |
| Cross-origin image without CORS headers | Texture loads successfully. Alpha detection `getImageData()` throws SecurityError -> falls back to `hasAlpha: false`, logs warning: `"depthkit: alpha detection failed for texture '{id}' (CORS restriction). Assuming opaque."` |
| `checkTextureSlotCompatibility` with slot not in slotToTextureId | Skipped — no warning. Optional slots without textures are valid. |
| `checkTextureSlotCompatibility` with texture ID not in metadata record | Skipped — texture wasn't loaded (may be handled by other validation). |

## Test Strategy

### Puppeteer-Based Integration Tests (Primary)

These tests launch headless Chromium, load the depthkit page, call `init()`, and exercise texture loading with real images.

**Test images required:** A set of small test images should be created or provided:
- `opaque.jpg` — A small JPEG (e.g., 100x75), fully opaque.
- `opaque.png` — A small PNG (e.g., 80x60), fully opaque (no alpha channel, or all pixels alpha=255).
- `transparent.png` — A small PNG (e.g., 100x100) with transparent background (e.g., a colored circle on transparency).
- `semitransparent.png` — A small PNG with semi-transparent regions (alpha ~128).
- `large_opaque.png` — A larger image (e.g., 2048x1024) to verify metadata reports original dimensions.

These test images must be served to the browser via a local HTTP server or Puppeteer request interception (not `file://` URLs, due to CORS constraints on `getImageData()`).

**Load and metadata tests:**
1. Load `opaque.jpg` -> verify metadata: `hasAlpha: false`, width/height match, aspectRatio approx width/height.
2. Load `opaque.png` -> verify `hasAlpha: false`.
3. Load `transparent.png` -> verify `hasAlpha: true`.
4. Load `semitransparent.png` -> verify `hasAlpha: true`.
5. Load `large_opaque.png` -> verify metadata reports original dimensions (2048x1024), not 64x64.
6. Load with `skipAlphaDetection: true` on `transparent.png` -> verify `hasAlpha: false`.

**Texture renderability test:**
7. Load a texture, create a `MeshBasicMaterial` with it as `map`, add a plane mesh to the scene, call `renderFrame()`, capture `canvas.toDataURL()` -> verify the frame is not all-black. (Validates that the texture is usable for rendering, not just stored.)

**Texture retrieval tests:**
8. After load, `getTexture(id)` returns a Three.js Texture (has `.image` property).
9. `getTexture('nonexistent')` returns null.
10. `getTextureMetadata(id)` returns the same metadata as loadTexture resolved with.
11. `getAllTextureMetadata()` returns array with correct length after loading N textures.
12. `getTextureCount()` reflects number of loaded textures.

**Batch loading tests:**
13. `loadTextures` with 3 entries -> all resolve, metadata array has length 3 in order.
14. `loadTextures` with one bad URL -> rejects, good textures remain in cache.
15. `loadTextures([])` -> rejects with expected message.
16. `loadTextures` with duplicate IDs -> rejects with expected message before any loading.

**Lifecycle tests:**
17. `unloadTexture(id)` -> `getTexture(id)` returns null, `getTextureCount()` decremented.
18. `unloadAllTextures()` -> `getTextureCount() === 0`.
19. Load, then load same ID again -> old texture replaced, warning logged (verify via `page.on('console')`).
20. `dispose()` after loading textures -> `getTextureCount() === 0` after re-init.

**Error condition tests:**
21. Any texture method before `init()` -> throws expected error.
22. Empty/falsy id or url -> throws expected error.
23. 404 URL -> rejects with expected error format.

**Color space tests:**
24. Load with `colorSpace: 'srgb'` -> `texture.colorSpace === THREE.SRGBColorSpace`.
25. Load with `colorSpace: 'linear'` -> `texture.colorSpace === THREE.LinearSRGBColorSpace`.
26. Load with default -> `texture.colorSpace === THREE.SRGBColorSpace`.

**Filter tests:**
27. Load any texture -> verify `texture.minFilter === THREE.LinearMipmapLinearFilter` and `texture.magFilter === THREE.LinearFilter`.

### Node-Side Unit Tests

28. `checkTextureSlotCompatibility` with alpha-mismatch -> returns warning.
29. `checkTextureSlotCompatibility` with matching alpha -> returns empty array.
30. `checkTextureSlotCompatibility` with `hasAlpha: true` / `transparent: false` -> returns info.
31. `checkTextureSlotCompatibility` with missing slot entries -> no warning for missing slots.
32. `checkTextureSlotCompatibility` with texture ID not in metadata -> skipped, no warning.
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
