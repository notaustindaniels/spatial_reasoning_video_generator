# Deliberation Transcript: OBJ-039

---

## Round 1 — spec_author

# Proposed Specification: OBJ-039 — Three.js Page-Side Geometry Instantiation

## Summary

OBJ-039 implements `src/page/geometry-library.js` — the browser-side module that converts serialized slot definitions (from OBJ-011's `SceneSetupConfig`) into Three.js scene graph objects. It provides functions to: (1) create textured plane meshes from `SlotSetup` data with correct position, rotation, size, and material properties, (2) load textures via `THREE.TextureLoader` with proper configuration matching OBJ-015's conventions, (3) assemble meshes into a `THREE.Group` for scene management, and (4) dispose of scene resources cleanly. This module is called by `scene-renderer.js`'s `setupScene()` and `teardownScene()` handlers defined by OBJ-011's protocol.

## Interface Contract

### Module: `src/page/geometry-library.js`

This module fulfills the stub established by OBJ-010. It is imported by `scene-renderer.js` and its functions are called from OBJ-011's protocol handlers. Functions are NOT exposed on `window.depthkit` directly — they are internal page-side utilities.

```typescript
// Conceptual contract — implementation is plain JS running in Chromium.
// Types here document the contract; implementation is JS.

/**
 * Result of materializing a single slot into a Three.js mesh.
 */
interface SlotMaterializationResult {
  /** The slot name. */
  slotName: string;
  /** The created mesh (always created, even on texture failure). */
  mesh: THREE.Mesh;
  /** The loaded texture, or null if loading failed. */
  texture: THREE.Texture | null;
  /** Whether the texture loaded successfully. */
  status: 'loaded' | 'error';
  /** Natural width of the loaded texture in pixels. Present when status='loaded'. */
  naturalWidth?: number;
  /** Natural height of the loaded texture in pixels. Present when status='loaded'. */
  naturalHeight?: number;
  /** Error message if status='error'. */
  error?: string;
}

/**
 * Result of materializing all slots for a scene.
 */
interface SceneMaterializationResult {
  /** The THREE.Group containing all slot meshes. Starts with visible=false. */
  group: THREE.Group;
  /** Per-slot results keyed by slot name. */
  slots: Record<string, SlotMaterializationResult>;
  /** Map from slot name to mesh (for renderComposite opacity manipulation). */
  meshMap: Map<string, THREE.Mesh>;
  /** Map from slot name to texture (for disposal tracking). */
  textureMap: Map<string, THREE.Texture>;
  /** True if ALL slots loaded their textures successfully. */
  success: boolean;
}

/**
 * Materializes a complete scene from SlotSetup definitions.
 *
 * For each slot in the config (all slots load textures concurrently):
 * 1. Resolves the texture URL via resolveTextureUrl().
 * 2. Loads the texture via THREE.TextureLoader.loadAsync() (parallel).
 * 3. Creates a THREE.PlaneGeometry with the slot's size.
 * 4. Creates a THREE.MeshBasicMaterial with the loaded texture
 *    and slot-level rendering properties (transparent, fog, etc.).
 * 5. Creates a THREE.Mesh, positions and rotates it per the slot definition.
 * 6. Adds the mesh to a THREE.Group.
 *
 * If a texture fails to load, a magenta fallback material (color: 0xff00ff)
 * is used instead. The mesh is still created at the correct position/rotation
 * so spatial layout is diagnosable in rendered output.
 *
 * The returned group has visible=false and group.name = sceneId.
 *
 * @param sceneId - Scene identifier (used for group.name and log messages).
 * @param slots - Record of slot name -> SlotSetup from SceneSetupConfig.
 *                Uses the SlotSetup type from OBJ-011's protocol-types.
 * @returns Promise resolving to SceneMaterializationResult.
 */
function materializeScene(
  sceneId: string,
  slots: Record<string, SlotSetup>
): Promise<SceneMaterializationResult>;

/**
 * Creates a single Three.js mesh from a slot definition and loaded texture.
 *
 * Mesh creation steps (in this exact order):
 * 1. new THREE.PlaneGeometry(size[0], size[1])
 * 2. new THREE.MeshBasicMaterial({
 *      map: texture,                           // null for fallback
 *      color: texture ? 0xffffff : 0xff00ff,   // white (texture tinted) or magenta
 *      transparent: slot.transparent ?? false,
 *      alphaTest: (slot.transparent ?? false) ? 0.01 : 0,
 *      side: THREE.FrontSide,
 *      fog: !(slot.fogImmune ?? false),
 *      opacity: 1.0,
 *    })
 * 3. mesh = new THREE.Mesh(geometry, material)
 * 4. mesh.position.set(position[0], position[1], position[2])
 * 5. mesh.rotation.set(rotation[0], rotation[1], rotation[2])
 * 6. mesh.renderOrder = slot.renderOrder ?? 0
 * 7. mesh.name = slotName
 *
 * @param slotName - The slot name (used for mesh.name).
 * @param slot - The SlotSetup definition from OBJ-011.
 * @param texture - The loaded THREE.Texture, or null for magenta fallback.
 * @returns The created THREE.Mesh.
 */
function createSlotMesh(
  slotName: string,
  slot: SlotSetup,
  texture: THREE.Texture | null
): THREE.Mesh;

/**
 * Loads a texture from a source string using THREE.TextureLoader.
 *
 * 1. Resolves the URL via resolveTextureUrl().
 * 2. Calls new THREE.TextureLoader().loadAsync(resolvedUrl).
 * 3. Applies texture configuration:
 *    - texture.colorSpace = THREE.SRGBColorSpace
 *    - texture.minFilter = THREE.LinearMipmapLinearFilter
 *    - texture.magFilter = THREE.LinearFilter
 *    (flipY is left at Three.js default: true)
 * 4. Reads texture.image.naturalWidth and texture.image.naturalHeight.
 *
 * @param src - The texture source string from SlotSetup.textureSrc.
 * @returns Promise resolving to { texture, naturalWidth, naturalHeight }.
 * @throws Error if src is empty/falsy: "Texture source is empty"
 * @throws Error if src format is unsupported (from resolveTextureUrl).
 * @throws Error if image fails to load (propagated from TextureLoader).
 */
function loadSlotTexture(
  src: string
): Promise<{ texture: THREE.Texture; naturalWidth: number; naturalHeight: number }>;

/**
 * Resolves a texture source string to a URL loadable by THREE.TextureLoader.
 *
 * Resolution rules:
 * - Strings starting with '/' → prepend 'file://' (POSIX absolute path)
 * - Strings starting with 'file://' → pass through
 * - Strings starting with 'data:' → pass through
 * - Strings starting with 'http://' → pass through
 * - Strings starting with 'https://' → pass through
 * - All other strings → throw Error:
 *   "Unsupported texture source format: must be absolute path, file://,
 *    data:, http://, or https:// URL. Got: '{src}'"
 *
 * Note: POSIX paths only. Windows paths (e.g., 'C:\...') are not supported
 * per seed C-08/C-11 (Linux VPS/Docker targets).
 *
 * @param src - Raw texture source from SlotSetup.textureSrc.
 * @returns Resolved URL string.
 * @throws Error if src format is unsupported.
 */
function resolveTextureUrl(src: string): string;

/**
 * Disposes all Three.js resources associated with a scene group.
 *
 * Traverses the group (via group.traverse()) and for each object
 * that is a THREE.Mesh:
 * 1. mesh.geometry.dispose()
 * 2. If mesh.material.map is non-null: mesh.material.map.dispose()
 * 3. mesh.material.dispose()
 *
 * After traversal:
 * 4. group.removeFromParent() — removes from the scene graph.
 * 5. group.clear() — removes all children from the group.
 *
 * @param group - The THREE.Group to dispose.
 * @returns { meshesRemoved: number, texturesDisposed: number }
 *          meshesRemoved counts meshes whose geometry+material were disposed.
 *          texturesDisposed counts meshes that had a non-null material.map.
 */
function disposeSceneGroup(
  group: THREE.Group
): { meshesRemoved: number; texturesDisposed: number };
```

### Integration with OBJ-011's `scene-renderer.js`

OBJ-011's `setupScene()` handler in `scene-renderer.js` calls `materializeScene()` and maps the result into OBJ-011's internal `PageSceneEntry` and the protocol's `SceneSetupResult`:

```typescript
// Pseudocode showing the call relationship — NOT implementation code.
// This documents how scene-renderer.js delegates to geometry-library.js.

// In setupScene(config: SceneSetupConfig):
//   const result = await materializeScene(config.sceneId, config.slots);
//   Store result.group, result.meshMap, result.textureMap in PageSceneEntry
//   Store config.fog in PageSceneEntry.fog
//   scene.add(result.group);
//   Map result.slots to SceneSetupResult.slots (SlotLoadResult)
//   return SceneSetupResult

// In teardownScene(sceneId):
//   const entry = sceneRegistry.get(sceneId);
//   const stats = disposeSceneGroup(entry.group);
//   sceneRegistry.delete(sceneId);
//   return { sceneId, meshesRemoved: stats.meshesRemoved, texturesDisposed: stats.texturesDisposed }
```

## Design Decisions

### D1: Dedicated geometry-library.js Module (Internal, Not on window.depthkit)

**Decision:** Geometry materialization is implemented in `src/page/geometry-library.js` as a separate module imported by `scene-renderer.js`. Its functions are NOT exposed on `window.depthkit` — they are internal page-side utilities called only by the protocol handlers.

**Rationale:** OBJ-010 established `geometry-library.js` as the stub for geometry materialization. Separating concerns keeps `scene-renderer.js` focused on protocol handling (scene registry, visibility, multi-pass compositing per OBJ-011) while `geometry-library.js` focuses on Three.js object creation. Since esbuild bundles everything into a single IIFE (per OBJ-001), the import is resolved at build time. Not exposing on `window.depthkit` prevents external callers from bypassing OBJ-011's scene lifecycle management.

### D2: Direct THREE.TextureLoader, Not OBJ-015's Cache API

**Decision:** `geometry-library.js` loads textures directly via `THREE.TextureLoader.loadAsync()`, applying the same texture configuration conventions as OBJ-015 (SRGBColorSpace, trilinear minFilter, bilinear magFilter). It does NOT call OBJ-015's `window.depthkit.loadTexture()` cache API.

**Alternatives considered:**
1. **Use OBJ-015's cache with scene-scoped IDs** (e.g., `scene_001:floor`) — Creates dual-ownership issues. OBJ-011's `teardownScene` disposes textures from the scene group directly. If those same textures also exist in OBJ-015's global cache, disposal leaves stale cache entries, or teardown must coordinate with OBJ-015's `unloadTexture()` for each slot.
2. **Direct THREE.TextureLoader** (chosen) — Textures are owned exclusively by the scene group's `PageSceneEntry`. Disposal is straightforward: traverse the group and dispose each texture. No global cache coordination needed.

**Relationship to OBJ-015:** OBJ-039 follows OBJ-015's texture configuration conventions to ensure visual consistency. OBJ-015's alpha detection (canvas pixel sampling) is NOT replicated in OBJ-039 — `materializeScene` reports `naturalWidth`/`naturalHeight` per slot, which the Node-side orchestrator can use for upstream warnings via OBJ-015's `checkTextureSlotCompatibility()` if desired. Alpha detection belongs to the orchestrator pipeline, not the dumb page renderer.

### D3: Magenta Fallback Material for Failed Textures

**Decision:** When a texture fails to load, the mesh is created with a solid magenta `MeshBasicMaterial` (color: `0xff00ff`) instead of skipping the mesh entirely.

**Rationale:** Per OBJ-011's spec. Preserving the mesh at its correct position/rotation makes spatial layout issues diagnosable in rendered output. Magenta is a visually unmistakable debug indicator that cannot be mistaken for a valid scene element. The orchestrator receives `SceneSetupResult.success = false` and can abort rendering if strict mode is desired.

### D4: Group Created with visible=false

**Decision:** The `THREE.Group` returned by `materializeScene` has `visible = false` and `group.name` set to the `sceneId`.

**Rationale:** Per OBJ-011 D3 — prevents newly-setup scenes from flashing into rendered output before the orchestrator is ready. `renderComposite` (OBJ-011) sets visibility per-frame.

### D5: Mesh.name Set to Slot Name

**Decision:** Each mesh has its `name` property set to the slot name (e.g., `'floor'`, `'subject'`).

**Rationale:** Aids debugging in Three.js inspector/logs. Also enables `renderComposite` to identify meshes by slot name if needed for future per-slot opacity manipulation (OBJ-044).

### D6: Parallel Texture Loading with Promise.allSettled

**Decision:** All textures for a scene load concurrently via `Promise.allSettled()`. Individual slot failures do not block other slots from loading.

**Rationale:** Per OBJ-011 D7 — per-slot error reporting allows the protocol to return detailed status while the orchestrator decides whether to abort. Unlike OBJ-015's batch load (`Promise.all`, fail-fast), `materializeScene` always creates all meshes (with fallback materials for failures), so `Promise.allSettled` is the correct primitive here.

### D7: POSIX-Only Path Resolution

**Decision:** Texture URL resolution supports POSIX absolute paths (starting with `/`), `file://`, `data:`, `http://`, and `https://` URLs. Windows paths are not supported.

**Rationale:** Per OBJ-011 D6 and seed C-08/C-11 (Linux VPS and Docker targets). Path detection is by prefix matching, not by parsing — simple and deterministic.

### D8: disposeSceneGroup Uses group.traverse()

**Decision:** `disposeSceneGroup` uses `group.traverse()` to find all meshes rather than assuming direct children only.

**Rationale:** Future-proofs against geometry implementations that might nest groups. For V1, all meshes are direct children of the scene group, but `traverse()` handles both flat and nested structures correctly with no additional cost for the flat case.

### D9: Material color Set to 0xffffff for Textured Meshes

**Decision:** When a texture is successfully loaded, the material's `color` is set to `0xffffff` (white). `MeshBasicMaterial` multiplies the texture color by the material color, so white preserves the texture's original colors. When no texture is available (fallback), color is `0xff00ff` (magenta).

**Rationale:** Ensures textures display at their true colors. If the `color` property were omitted, Three.js defaults to white anyway, but setting it explicitly documents intent and ensures the fallback path produces a distinctly colored mesh.

### D10: No Texture Resizing or MAX_TEXTURE_SIZE Validation

**Decision:** Textures are loaded at their natural size. No resizing or clamping to `MAX_TEXTURE_SIZE` is performed.

**Rationale:** Per OBJ-015 D9 — Three.js auto-downscales oversized textures in modern versions. The `naturalWidth`/`naturalHeight` returned in slot results reflect the original image dimensions (from `texture.image.naturalWidth`/`naturalHeight` or `texture.image.width`/`height`), not any auto-downscaled dimensions. If the orchestrator needs to check against `MAX_TEXTURE_SIZE`, it can do so using `getRendererInfo().maxTextureSize` from OBJ-010.

### D11: Single TextureLoader Instance per materializeScene Call

**Decision:** `materializeScene` creates a single `THREE.TextureLoader` instance and reuses it for all slots within a scene. The loader is not cached across scenes.

**Rationale:** `THREE.TextureLoader` is lightweight (it's a thin wrapper over `HTMLImageElement` loading). Creating one per scene setup is negligible. Sharing across scenes would require global state management with no measurable benefit.

## Acceptance Criteria

- [ ] **AC-01:** `src/page/geometry-library.js` exports `materializeScene`, `createSlotMesh`, `loadSlotTexture`, `resolveTextureUrl`, and `disposeSceneGroup` functions.

- [ ] **AC-02:** `materializeScene('scene_001', slots)` with a single slot containing a valid PNG texture returns a `SceneMaterializationResult` with `success === true`, the slot's `status === 'loaded'`, `naturalWidth > 0`, `naturalHeight > 0`, and a `group` containing exactly one child mesh.

- [ ] **AC-03:** The returned `group` has `visible === false` and `group.name === 'scene_001'` (matching the sceneId argument).

- [ ] **AC-04:** The mesh within the group has `position`, `rotation`, and `renderOrder` values matching the corresponding `SlotSetup` values exactly.

- [ ] **AC-05:** The mesh's material is an instance of `THREE.MeshBasicMaterial` with `map` set to the loaded texture, `side === THREE.FrontSide`, and `opacity === 1.0`.

- [ ] **AC-06:** For a slot with `transparent: true`, the mesh's material has `transparent === true` and `alphaTest === 0.01`.

- [ ] **AC-07:** For a slot with `transparent` omitted or `false`, the mesh's material has `transparent === false` and `alphaTest === 0`.

- [ ] **AC-08:** For a slot with `fogImmune: true`, the mesh's material has `fog === false`.

- [ ] **AC-09:** For a slot with `fogImmune` omitted or `false`, the mesh's material has `fog === true`.

- [ ] **AC-10:** When a texture fails to load (e.g., nonexistent file path), the mesh is still created with a magenta `MeshBasicMaterial` (`material.color` equals `0xff00ff`), the slot's `status === 'error'`, `error` contains a non-empty string, and `SceneMaterializationResult.success === false`.

- [ ] **AC-11:** `materializeScene` with multiple slots loads all textures concurrently. If one slot's texture fails, other slots still load successfully with `status === 'loaded'`. The `group` contains one mesh per slot regardless of load status.

- [ ] **AC-12:** Loaded textures have `colorSpace === THREE.SRGBColorSpace`, `minFilter === THREE.LinearMipmapLinearFilter`, and `magFilter === THREE.LinearFilter`.

- [ ] **AC-13:** `resolveTextureUrl('/path/to/image.png')` returns `'file:///path/to/image.png'`.

- [ ] **AC-14:** `resolveTextureUrl('file:///already/a/url.png')` returns the input unchanged.

- [ ] **AC-15:** `resolveTextureUrl('data:image/png;base64,...')` returns the input unchanged.

- [ ] **AC-16:** `resolveTextureUrl('http://example.com/img.png')` and `resolveTextureUrl('https://example.com/img.png')` return the input unchanged.

- [ ] **AC-17:** `resolveTextureUrl('relative/path.png')` throws an Error with message containing `"Unsupported texture source format"`.

- [ ] **AC-18:** `disposeSceneGroup(group)` calls `.dispose()` on each mesh's geometry, material, and material.map (when non-null), then removes the group from its parent and clears the group's children. Returns `{ meshesRemoved, texturesDisposed }` with accurate counts.

- [ ] **AC-19:** `disposeSceneGroup` on a group containing meshes with magenta fallback materials (no texture map) does not throw and reports `texturesDisposed` counting only meshes that had non-null `material.map`.

- [ ] **AC-20:** Each mesh's `name` property equals the slot name string (e.g., `'floor'`, `'subject'`).

- [ ] **AC-21:** Each mesh's `PlaneGeometry` has parameters matching `slot.size[0]` (width) and `slot.size[1]` (height).

- [ ] **AC-22:** `materializeScene` with an empty `slots` record `{}` returns a group with no children, `success === true`, empty `slots` result, and empty maps.

- [ ] **AC-23:** After `disposeSceneGroup`, the group has no children and `group.parent === null`.

- [ ] **AC-24:** A mesh created by `materializeScene`, when the group is added to `window.depthkit.scene` with `visible = true`, renders a visible (non-black) frame when captured via `canvas.toDataURL()` after `window.depthkit.renderFrame()`.

- [ ] **AC-25:** `geometry-library.js` functions are NOT exposed on `window.depthkit`. They are internal to the page bundle, called only by `scene-renderer.js`.

- [ ] **AC-26:** `loadSlotTexture('')` rejects with `"Texture source is empty"`. `loadSlotTexture` with a `null` or `undefined` argument rejects with the same message.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Empty `slots` record `{}` | Returns group with no children. `success === true`. Empty `slots` result, empty `meshMap`, empty `textureMap`. |
| All textures fail to load | `success === false`. All slots have magenta fallback meshes with `status === 'error'`. Group contains one mesh per slot. |
| Texture source is empty string | `loadSlotTexture` rejects: `"Texture source is empty"`. Slot gets magenta fallback in `materializeScene`. |
| Texture source is `null` or `undefined` | `loadSlotTexture` rejects: `"Texture source is empty"` (falsy check). Slot gets magenta fallback. |
| Texture source is relative path (`images/foo.png`) | `resolveTextureUrl` throws: `"Unsupported texture source format..."`. Slot gets magenta fallback. |
| Texture source is Windows path (`C:\images\foo.png`) | `resolveTextureUrl` throws (no leading `/`, not a recognized protocol prefix). Slot gets magenta fallback. |
| Very large texture (e.g., 8192×8192) | Loads normally. Three.js auto-downscales if needed. `naturalWidth`/`naturalHeight` report the original image dimensions from `texture.image`. |
| Texture file is corrupt/truncated | `THREE.TextureLoader.loadAsync()` rejects. Error message propagated. Slot gets magenta fallback. |
| Slot with `size: [0, 0]` | `PlaneGeometry` created with zero dimensions. Mesh exists but renders as invisible (degenerate geometry). No error thrown by OBJ-039. Manifest validation (OBJ-004) should prevent this upstream. |
| Slot with negative size components | `PlaneGeometry` created with negative dimensions (Three.js takes absolute value internally for geometry, or produces degenerate mesh). No error thrown. Manifest validation should prevent upstream. |
| `renderOrder` is very large (e.g., 999999) | Passed directly to `mesh.renderOrder`. Three.js accepts any number. |
| `renderOrder` omitted | Defaults to 0 (`slot.renderOrder ?? 0`). |
| `transparent` omitted | Defaults to `false` (`slot.transparent ?? false`). |
| `fogImmune` omitted | Defaults to `false` (`slot.fogImmune ?? false`), meaning `material.fog = true`. |
| Multiple slots with same `renderOrder` | Valid. Three.js uses insertion order as secondary sort for equal renderOrder values. |
| `disposeSceneGroup` on a group not added to any scene | `group.removeFromParent()` is a no-op if group has no parent. Meshes still disposed. Returns correct counts. |
| `disposeSceneGroup` called twice on same group | Second call: group has no children (cleared on first call). Returns `{ meshesRemoved: 0, texturesDisposed: 0 }`. No error — `dispose()` on already-disposed Three.js objects is safe. |
| Data URI texture with invalid base64 | Browser image decode fails. `TextureLoader.loadAsync()` rejects. Slot gets magenta fallback. |
| Data URI texture with valid image | Loads normally. `naturalWidth`/`naturalHeight` reflect the decoded image dimensions. |
| `sceneId` is empty string in `materializeScene` | Group created with `name === ''`. No error from geometry-library. OBJ-011's protocol layer validates sceneId before calling this function. |
| Slot position/rotation contain `NaN` | Mesh position/rotation set to `NaN`. Three.js renders nothing for that mesh (degenerate transform). No error thrown. Upstream validation should prevent. |

## Test Strategy

### Puppeteer-Based Integration Tests (Primary)

These tests launch headless Chromium, load the depthkit page, call `window.depthkit.init()`, and exercise geometry materialization within the real browser rendering context.

**Test fixtures:** Small solid-color PNG images (e.g., 100×100 pixels: red, blue, green) and one transparent PNG (colored circle on transparent background). Generated programmatically or provided as static fixtures. Served to the browser via Puppeteer request interception or as data URIs to avoid CORS issues.

**Materialization tests:**
1. Single slot with valid texture: verify group has 1 child, mesh has correct position/rotation/renderOrder/name, material has loaded texture.
2. Multiple slots (3): verify group has 3 children, each mesh has correct properties.
3. Empty slots record: verify empty group, `success === true`.
4. Verify `group.visible === false` and `group.name === sceneId`.

**Texture loading tests:**
5. Valid absolute POSIX path: `status === 'loaded'`, `naturalWidth`/`naturalHeight` correct.
6. Valid data URI: `status === 'loaded'`.
7. Nonexistent file path: `status === 'error'`, mesh has magenta material (`material.color.getHex() === 0xff00ff`).
8. Relative path: `status === 'error'` (unsupported format in error message).
9. Mixed success/failure (2 valid + 1 invalid): 2 loaded, 1 error, `success === false`, group has 3 meshes.

**Material property tests:**
10. `transparent: true` → `material.transparent === true`, `material.alphaTest === 0.01`.
11. `transparent: false` → `material.transparent === false`, `material.alphaTest === 0`.
12. `transparent` omitted → same as `false`.
13. `fogImmune: true` → `material.fog === false`.
14. `fogImmune: false` → `material.fog === true`.
15. `fogImmune` omitted → `material.fog === true`.
16. `renderOrder: 5` → `mesh.renderOrder === 5`.
17. `renderOrder` omitted → `mesh.renderOrder === 0`.
18. Texture `colorSpace`, `minFilter`, `magFilter` match expected constants.

**Rendering test:**
19. Materialize a scene with a textured slot, add group to `window.depthkit.scene`, set `group.visible = true`, call `window.depthkit.renderFrame({ position: [0,0,5], lookAt: [0,0,0], fov: 50 })`, capture `canvas.toDataURL()`, verify frame is not all-black.
20. Render same scene with camera at two different positions. Verify captured frames differ (perspective projection produces different views).

**Disposal tests:**
21. `disposeSceneGroup`: verify returned `meshesRemoved` and `texturesDisposed` match expectations.
22. After disposal, `group.children.length === 0` and `group.parent === null`.
23. Disposal with magenta fallback meshes: `texturesDisposed` does not count fallback slots. No error thrown.
24. Double disposal: second call returns `{ meshesRemoved: 0, texturesDisposed: 0 }`, no error.

**URL resolution tests:**
25. `/absolute/path` → `file:///absolute/path`
26. `file:///already/url` → unchanged
27. `data:image/png;base64,...` → unchanged
28. `http://example.com/img.png` → unchanged
29. `https://example.com/img.png` → unchanged
30. `relative/path.png` → throws with "Unsupported texture source format"
31. Empty string → throws "Texture source is empty"

### Relevant Testable Claims

- **TC-02** (render performance): Materialization time (texture loading + mesh creation) contributes to per-scene setup time. Tests should log timing for benchmarking.
- **TC-04** (scene geometries eliminate manual 3D positioning): Meshes are positioned entirely from SlotSetup data — no manual coordinates in the page code. All 3D placement comes from the orchestrator via geometry definitions.
- **TC-05** (tunnel geometry produces convincing depth): When tunnel geometry slots are materialized and rendered with a forward camera push, the perspective distortion should be visible in captured frames.
- **TC-06** (deterministic output): Same slots + same textures + same camera state → identical captured frame. Material settings are deterministic.

## Integration Points

### Depends on

| Dependency | What OBJ-039 uses |
|---|---|
| **OBJ-010** (Page shell) | Three.js runtime environment: `THREE.PlaneGeometry`, `THREE.MeshBasicMaterial`, `THREE.Mesh`, `THREE.Group`, `THREE.TextureLoader`, `THREE.SRGBColorSpace`, `THREE.LinearMipmapLinearFilter`, `THREE.LinearFilter`, `THREE.FrontSide`. OBJ-039 runs in the same Chromium page and uses Three.js (bundled into the IIFE by esbuild). |
| **OBJ-005** (Geometry types) | Informs the `SlotSetup` field structure consumed (position, rotation, size, transparent, renderOrder, fogImmune). OBJ-039 does not import OBJ-005 directly — it receives `SlotSetup` data as plain JSON from OBJ-011's protocol. The field names and semantics match OBJ-005's `PlaneSlot`. |
| **OBJ-015** (Texture loader) | Texture configuration conventions: `SRGBColorSpace`, `LinearMipmapLinearFilter`, `LinearFilter`. OBJ-039 applies the same settings to textures loaded directly via `THREE.TextureLoader`. Does NOT call OBJ-015's `loadTexture()`/`getTexture()` API — avoids dual-ownership of texture lifecycle. OBJ-015's `checkTextureSlotCompatibility()` (Node-side) remains available to the orchestrator using `naturalWidth`/`naturalHeight` from slot results. |
| **OBJ-011** (Message protocol) | Defines `SlotSetup` type (the input to `materializeScene`). Defines `SceneSetupResult` and `SceneTeardownResult` types (the output format the protocol expects). `scene-renderer.js`'s `setupScene()` and `teardownScene()` handlers call `materializeScene()` and `disposeSceneGroup()` respectively, mapping results to protocol response types. |

### Consumed by

| Downstream | How it uses OBJ-039 |
|---|---|
| OBJ-011's page-side implementation (`scene-renderer.js`) | `setupScene()` delegates Three.js object creation to `materializeScene()`. `teardownScene()` delegates resource cleanup to `disposeSceneGroup()`. This is the sole consumer. |

*OBJ-039 has no further downstream consumers in the progress map (`blocks: []`).*

### File Placement

```
depthkit/
  src/
    page/
      geometry-library.js    # IMPLEMENT — evolve from OBJ-010's stub.
                              #   Exports: materializeScene, createSlotMesh,
                              #   loadSlotTexture, resolveTextureUrl,
                              #   disposeSceneGroup
      scene-renderer.js      # MODIFY — import geometry-library.js functions.
                              #   setupScene() calls materializeScene() and
                              #   maps result to PageSceneEntry + SceneSetupResult.
                              #   teardownScene() calls disposeSceneGroup() and
                              #   maps result to SceneTeardownResult.
```

## Open Questions

### OQ-A: Should materializeScene report alpha detection per slot?

OBJ-015 defines alpha detection via canvas pixel sampling (~5ms per texture). `materializeScene` could replicate this and include `hasAlpha` in slot results, enabling the Node-side orchestrator to call `checkTextureSlotCompatibility()` with complete data. Currently, only `naturalWidth`/`naturalHeight` are reported.

**Recommendation:** Defer for V1. The orchestrator can rely on manifest-level `transparent` flags matching image generation pipeline conventions (subject images generated with alpha, backgrounds without). If mismatches cause visual issues in production, alpha detection can be added to `loadSlotTexture` as a follow-up without changing the API contract — just add `hasAlpha` to the returned object and to `SlotMaterializationResult`.

### OQ-B: Should texture configuration (colorSpace, filters) be parameterizable?

Currently hardcoded to SRGBColorSpace + trilinear/bilinear, matching OBJ-015 D10. Future use cases (normal maps, data textures for OQ-09 lighting) might need different settings.

**Recommendation:** Hardcode for V1. If lighting (OQ-09) is adopted, add optional `colorSpace` and `filter` fields to `SlotSetup` (which would require a protocol-types.ts change in OBJ-011).

### OQ-C: Should materializeScene validate slot data?

Currently, `materializeScene` trusts the `SlotSetup` data (position/rotation/size are valid numbers, etc.). The orchestrator (OBJ-036) constructs `SlotSetup` from validated manifest data + validated geometry definitions (OBJ-005).

**Recommendation:** No. The page is a dumb renderer (OBJ-010 D1). Validation belongs on the Node side. The page creates what it's told to create. Adding validation in the page would duplicate Node-side logic and violate the architecture.

---

I believe this spec fully addresses OBJ-039's scope. I'd appreciate the Challenger's review — particularly on:
1. The decision to NOT use OBJ-015's cache API (D2)
2. Whether the `SceneMaterializationResult` interface provides sufficient data for OBJ-011's scene management
3. Whether any edge cases are missing from the table

---

## Round 2 — spec_challenger

I've reviewed the proposed OBJ-039 specification carefully against the seed, all four dependency specs, and the progress map. Here's my assessment.

---

## What's Sound

- **D1 (internal module, not on window.depthkit):** Clean separation. Correct that OBJ-010's stub is the right home.
- **D3 (magenta fallback):** Consistent with OBJ-011's spec.
- **D4 (group visible=false):** Matches OBJ-011 D3 exactly.
- **D6 (Promise.allSettled for parallel loading):** Correct choice — differs from OBJ-015's `Promise.all` for good reason (we always want all meshes created, even with fallbacks).
- **D7 (POSIX-only):** Consistent with seed C-08/C-11 and OBJ-011 D6.
- **D8 (traverse for disposal):** Correct future-proofing.
- **Scope:** Stays within OBJ-039's metadata description. No bleed into OBJ-011 protocol handling or OBJ-036 sequencing.
- **Vocabulary:** Correct throughout — "plane," "scene geometry," "slot." No drift.

---

## Issues

### Issue 1: OBJ-011 Contradicts OBJ-039 on MAX_TEXTURE_SIZE Handling (Major)

OBJ-011's edge case table explicitly states:

> "Texture file is very large (e.g., 8192x8192) — Page handler checks against `gl.getParameter(gl.MAX_TEXTURE_SIZE)` after loading. If texture exceeds the limit, `SlotLoadResult.status = 'error'` with message: `'Texture dimensions {w}x{h} exceed WebGL max texture size {max}'`. Mesh created with magenta fallback."

OBJ-039's D10 says: "No Texture Resizing or MAX_TEXTURE_SIZE Validation" and "Three.js auto-downscales oversized textures in modern versions."

These are directly contradictory. Since OBJ-011 is a dependency whose spec is already verified/approved, OBJ-039 either needs to implement the MAX_TEXTURE_SIZE check (conforming to OBJ-011's contract), or this contradiction needs to be explicitly called out with a rationale for why OBJ-039 deviates and what the downstream impact is.

**Proposed fix:** `loadSlotTexture` should check `texture.image.width` and `texture.image.height` against `renderer.capabilities.maxTextureSize` (accessible via the Three.js renderer on the page) after loading. If either dimension exceeds the limit, return `status: 'error'` with the message format OBJ-011 specifies. Add an acceptance criterion:

> AC-XX: When a loaded texture's dimensions exceed `gl.MAX_TEXTURE_SIZE`, `loadSlotTexture` rejects with message `"Texture dimensions {w}x{h} exceed WebGL max texture size {max}"`. The slot gets a magenta fallback mesh.

This requires `loadSlotTexture` to have access to the renderer (or the max texture size value). Since `materializeScene` runs inside the page where `window.depthkit.renderer` is available, this value can be read at call time and passed to `loadSlotTexture`, or `loadSlotTexture` can read it directly from the global `window.depthkit.renderer.capabilities.maxTextureSize`.

---

### Issue 2: OBJ-015 Dependency Spec Claims OBJ-039 Uses Its API (Major)

OBJ-015's "Consumed by" table states:

> **OBJ-039** (Scene setup / geometry materialization) — Calls `getTexture(slotName)` to retrieve loaded textures and assign them to mesh materials during scene instantiation. Uses `getTextureMetadata()` for aspect-ratio-aware plane sizing.

OBJ-039's spec (D2) explicitly says it does NOT call OBJ-015's API, loading textures directly via `THREE.TextureLoader` instead. D2's rationale is sound (avoiding dual-ownership of texture lifecycle). But the mismatch needs to be explicitly documented, because:

1. A reader of OBJ-015's verified spec would expect OBJ-039 to call `getTexture()`.
2. OBJ-015 is in OBJ-039's `depends_on` list.

**Proposed fix:** Add a design decision or prominent note explaining that OBJ-015's "Consumed by" prediction for OBJ-039 was incorrect, and that the actual relationship is convention-following only (same texture config: SRGBColorSpace, trilinear, bilinear). The dependency on OBJ-015 is for its texture configuration conventions, not its API. This should also note that OBJ-015's `checkTextureSlotCompatibility()` remains available on the Node side if the orchestrator wants to use `naturalWidth`/`naturalHeight` from the slot results.

---

### Issue 3: `naturalWidth`/`naturalHeight` Not Guaranteed on All Image Types (Minor)

The spec says: "Reads `texture.image.naturalWidth` and `texture.image.naturalHeight`."

`THREE.TextureLoader` internally creates an `HTMLImageElement`, which has `naturalWidth`/`naturalHeight`. However, in some Three.js configurations or newer versions, `createImageBitmap()` may be used, which produces `ImageBitmap` objects — these only have `width`/`height`, not `naturalWidth`/`naturalHeight`.

**Proposed fix:** Specify the fallback chain:

> `naturalWidth = texture.image.naturalWidth ?? texture.image.width`
> `naturalHeight = texture.image.naturalHeight ?? texture.image.height`

And add a note in the `loadSlotTexture` contract.

---

### Issue 4: Test Strategy Doesn't Explain Access to Internal Functions (Minor)

AC-25 says functions are NOT exposed on `window.depthkit`. The test strategy says "Puppeteer-Based Integration Tests" that verify group children, mesh properties, material settings, etc. But if `materializeScene` is internal to the IIFE bundle, how do Puppeteer tests invoke it and inspect results?

The practical answer is: tests call OBJ-011's `setupScene()` through the protocol (or via `page.evaluate(() => window.depthkit.setupScene(config))`), then inspect the scene graph via `page.evaluate(() => { /* traverse window.depthkit.scene.children */ })`. But this isn't stated.

**Proposed fix:** Add a paragraph to the test strategy clarifying that tests invoke `materializeScene` indirectly through `window.depthkit.setupScene()` (OBJ-011's page-side handler), then inspect the resulting scene graph via `page.evaluate()` using `window.depthkit.scene.children`. For URL resolution tests (`resolveTextureUrl`), since the function is internal, these should be tested via the observable behavior of `setupScene` with various `textureSrc` formats (which exercises `resolveTextureUrl` indirectly).

---

### Issue 5: Missing AC for `material.color = 0xffffff` on Successful Texture Load (Minor)

D9 specifies that textured meshes have `material.color = 0xffffff`. AC-10 verifies magenta (`0xff00ff`) for failures. But no AC verifies white for success. Since `MeshBasicMaterial` multiplies texture color by material color, getting this wrong would tint all textures.

**Proposed fix:** Add AC:

> AC-XX: For a slot with a successfully loaded texture, the mesh's material has `color` equal to `0xffffff` (white), ensuring the texture displays at its true colors.

---

### Issue 6: Missing Euler Order Documentation (Minor)

`mesh.rotation.set(rotation[0], rotation[1], rotation[2])` uses Three.js's default Euler order (`'XYZ'`). OBJ-005 and OBJ-003 define `EulerRotation` as `readonly [number, number, number]` — the order is implicit. The seed's Section 8.4 uses rotations like `[-Math.PI/2, 0, 0]` which are clearly `[rx, ry, rz]` in XYZ order.

**Proposed fix:** Add a brief note in `createSlotMesh`'s contract that rotation uses Three.js's default Euler order `'XYZ'`, consistent with OBJ-003's `EulerRotation` type. This is documentation, not a code change.

---

### Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | MAX_TEXTURE_SIZE contradiction with OBJ-011 | Major | Needs fix |
| 2 | OBJ-015 dependency claim mismatch | Major | Needs documentation |
| 3 | naturalWidth fallback for ImageBitmap | Minor | Needs fix |
| 4 | Test strategy access mechanism unclear | Minor | Needs clarification |
| 5 | Missing AC for material.color = white | Minor | Needs AC |
| 6 | Euler order not documented | Minor | Needs note |

Please address Issues 1 and 2 (major), and I'd like to see 3-5 addressed as well. Issue 6 can be a one-line addition. Once I verify the fixes, I'll converge.

---

## Round 3 — spec_author

# Revised Specification: OBJ-039 — Three.js Page-Side Geometry Instantiation

All six issues from Round 2 are addressed below. I'll call out each fix inline.

## Summary

OBJ-039 implements `src/page/geometry-library.js` — the browser-side module that converts serialized slot definitions (from OBJ-011's `SceneSetupConfig`) into Three.js scene graph objects. It provides functions to: (1) create textured plane meshes from `SlotSetup` data with correct position, rotation, size, and material properties, (2) load textures via `THREE.TextureLoader` with proper configuration matching OBJ-015's conventions, (3) validate loaded textures against `MAX_TEXTURE_SIZE`, (4) assemble meshes into a `THREE.Group` for scene management, and (5) dispose of scene resources cleanly. This module is called by `scene-renderer.js`'s `setupScene()` and `teardownScene()` handlers defined by OBJ-011's protocol.

## Interface Contract

### Module: `src/page/geometry-library.js`

This module fulfills the stub established by OBJ-010. It is imported by `scene-renderer.js` and its functions are called from OBJ-011's protocol handlers. Functions are NOT exposed on `window.depthkit` directly — they are internal page-side utilities called only by the protocol handlers.

```typescript
// Conceptual contract — implementation is plain JS running in Chromium.
// Types here document the contract; implementation is JS.

/**
 * Result of materializing a single slot into a Three.js mesh.
 */
interface SlotMaterializationResult {
  /** The slot name. */
  slotName: string;
  /** The created mesh (always created, even on texture failure). */
  mesh: THREE.Mesh;
  /** The loaded texture, or null if loading failed. */
  texture: THREE.Texture | null;
  /** Whether the texture loaded successfully. */
  status: 'loaded' | 'error';
  /** Natural width of the loaded texture in pixels. Present when status='loaded'. */
  naturalWidth?: number;
  /** Natural height of the loaded texture in pixels. Present when status='loaded'. */
  naturalHeight?: number;
  /** Error message if status='error'. */
  error?: string;
}

/**
 * Result of materializing all slots for a scene.
 */
interface SceneMaterializationResult {
  /** The THREE.Group containing all slot meshes. Starts with visible=false. */
  group: THREE.Group;
  /** Per-slot results keyed by slot name. */
  slots: Record<string, SlotMaterializationResult>;
  /** Map from slot name to mesh (for renderComposite opacity manipulation). */
  meshMap: Map<string, THREE.Mesh>;
  /** Map from slot name to texture (for disposal tracking). */
  textureMap: Map<string, THREE.Texture>;
  /** True if ALL slots loaded their textures successfully. */
  success: boolean;
}

/**
 * Materializes a complete scene from SlotSetup definitions.
 *
 * For each slot in the config (all slots load textures concurrently):
 * 1. Resolves the texture URL via resolveTextureUrl().
 * 2. Loads the texture via THREE.TextureLoader.loadAsync() (parallel).
 * 3. Validates texture dimensions against MAX_TEXTURE_SIZE.
 * 4. Creates a THREE.PlaneGeometry with the slot's size.
 * 5. Creates a THREE.MeshBasicMaterial with the loaded texture
 *    and slot-level rendering properties (transparent, fog, etc.).
 * 6. Creates a THREE.Mesh, positions and rotates it per the slot definition.
 * 7. Adds the mesh to a THREE.Group.
 *
 * If a texture fails to load or exceeds MAX_TEXTURE_SIZE, a magenta
 * fallback material (color: 0xff00ff) is used instead. The mesh is
 * still created at the correct position/rotation so spatial layout
 * is diagnosable in rendered output.
 *
 * The returned group has visible=false and group.name = sceneId.
 *
 * Requires window.depthkit.renderer to be initialized (reads
 * renderer.capabilities.maxTextureSize for texture validation).
 *
 * @param sceneId - Scene identifier (used for group.name and log messages).
 * @param slots - Record of slot name -> SlotSetup from SceneSetupConfig.
 *                Uses the SlotSetup type from OBJ-011's protocol-types.
 * @returns Promise resolving to SceneMaterializationResult.
 */
function materializeScene(
  sceneId: string,
  slots: Record<string, SlotSetup>
): Promise<SceneMaterializationResult>;

/**
 * Creates a single Three.js mesh from a slot definition and loaded texture.
 *
 * Mesh creation steps (in this exact order):
 * 1. new THREE.PlaneGeometry(size[0], size[1])
 * 2. new THREE.MeshBasicMaterial({
 *      map: texture,                           // null for fallback
 *      color: texture ? 0xffffff : 0xff00ff,   // white (texture tinted) or magenta
 *      transparent: slot.transparent ?? false,
 *      alphaTest: (slot.transparent ?? false) ? 0.01 : 0,
 *      side: THREE.FrontSide,
 *      fog: !(slot.fogImmune ?? false),
 *      opacity: 1.0,
 *    })
 * 3. mesh = new THREE.Mesh(geometry, material)
 * 4. mesh.position.set(position[0], position[1], position[2])
 * 5. mesh.rotation.set(rotation[0], rotation[1], rotation[2])
 *    (Uses Three.js default Euler order 'XYZ', consistent with
 *    OBJ-003's EulerRotation type [rx, ry, rz].)
 * 6. mesh.renderOrder = slot.renderOrder ?? 0
 * 7. mesh.name = slotName
 *
 * @param slotName - The slot name (used for mesh.name).
 * @param slot - The SlotSetup definition from OBJ-011.
 * @param texture - The loaded THREE.Texture, or null for magenta fallback.
 * @returns The created THREE.Mesh.
 */
function createSlotMesh(
  slotName: string,
  slot: SlotSetup,
  texture: THREE.Texture | null
): THREE.Mesh;

/**
 * Loads a texture from a source string using THREE.TextureLoader,
 * applies standard configuration, and validates against MAX_TEXTURE_SIZE.
 *
 * 1. Resolves the URL via resolveTextureUrl().
 * 2. Calls new THREE.TextureLoader().loadAsync(resolvedUrl).
 * 3. Applies texture configuration:
 *    - texture.colorSpace = THREE.SRGBColorSpace
 *    - texture.minFilter = THREE.LinearMipmapLinearFilter
 *    - texture.magFilter = THREE.LinearFilter
 *    (flipY is left at Three.js default: true)
 * 4. Reads image dimensions with fallback chain:
 *    naturalWidth = texture.image.naturalWidth ?? texture.image.width
 *    naturalHeight = texture.image.naturalHeight ?? texture.image.height
 *    (ImageBitmap objects only have width/height, not naturalWidth/naturalHeight.
 *    HTMLImageElement has both. The fallback handles either case.)
 * 5. Validates dimensions against maxTextureSize:
 *    If naturalWidth > maxTextureSize OR naturalHeight > maxTextureSize,
 *    disposes the loaded texture and throws:
 *    "Texture dimensions {w}x{h} exceed WebGL max texture size {max}"
 *
 * @param src - The texture source string from SlotSetup.textureSrc.
 * @param maxTextureSize - The WebGL MAX_TEXTURE_SIZE from the renderer.
 *                         Read from window.depthkit.renderer.capabilities.maxTextureSize
 *                         by the caller (materializeScene).
 * @returns Promise resolving to { texture, naturalWidth, naturalHeight }.
 * @throws Error if src is empty/falsy: "Texture source is empty"
 * @throws Error if src format is unsupported (from resolveTextureUrl).
 * @throws Error if texture dimensions exceed maxTextureSize.
 * @throws Error if image fails to load (propagated from TextureLoader).
 */
function loadSlotTexture(
  src: string,
  maxTextureSize: number
): Promise<{ texture: THREE.Texture; naturalWidth: number; naturalHeight: number }>;

/**
 * Resolves a texture source string to a URL loadable by THREE.TextureLoader.
 *
 * Resolution rules:
 * - Strings starting with '/' → prepend 'file://' (POSIX absolute path)
 * - Strings starting with 'file://' → pass through
 * - Strings starting with 'data:' → pass through
 * - Strings starting with 'http://' → pass through
 * - Strings starting with 'https://' → pass through
 * - All other strings → throw Error:
 *   "Unsupported texture source format: must be absolute path, file://,
 *    data:, http://, or https:// URL. Got: '{src}'"
 *
 * Note: POSIX paths only. Windows paths (e.g., 'C:\...') are not supported
 * per seed C-08/C-11 (Linux VPS/Docker targets).
 *
 * @param src - Raw texture source from SlotSetup.textureSrc.
 * @returns Resolved URL string.
 * @throws Error if src format is unsupported.
 */
function resolveTextureUrl(src: string): string;

/**
 * Disposes all Three.js resources associated with a scene group.
 *
 * Traverses the group (via group.traverse()) and for each object
 * that is a THREE.Mesh:
 * 1. mesh.geometry.dispose()
 * 2. If mesh.material.map is non-null: mesh.material.map.dispose()
 * 3. mesh.material.dispose()
 *
 * After traversal:
 * 4. group.removeFromParent() — removes from the scene graph.
 * 5. group.clear() — removes all children from the group.
 *
 * @param group - The THREE.Group to dispose.
 * @returns { meshesRemoved: number, texturesDisposed: number }
 *          meshesRemoved counts meshes whose geometry+material were disposed.
 *          texturesDisposed counts meshes that had a non-null material.map.
 */
function disposeSceneGroup(
  group: THREE.Group
): { meshesRemoved: number; texturesDisposed: number };
```

### Integration with OBJ-011's `scene-renderer.js`

OBJ-011's `setupScene()` handler in `scene-renderer.js` calls `materializeScene()` and maps the result into OBJ-011's internal `PageSceneEntry` and the protocol's `SceneSetupResult`:

```typescript
// Pseudocode showing the call relationship — NOT implementation code.
// This documents how scene-renderer.js delegates to geometry-library.js.

// In setupScene(config: SceneSetupConfig):
//   const result = await materializeScene(config.sceneId, config.slots);
//   Store result.group, result.meshMap, result.textureMap in PageSceneEntry
//   Store config.fog in PageSceneEntry.fog
//   scene.add(result.group);
//   Map result.slots to SceneSetupResult.slots (SlotLoadResult)
//   return SceneSetupResult

// In teardownScene(sceneId):
//   const entry = sceneRegistry.get(sceneId);
//   const stats = disposeSceneGroup(entry.group);
//   sceneRegistry.delete(sceneId);
//   return { sceneId, meshesRemoved: stats.meshesRemoved, texturesDisposed: stats.texturesDisposed }
```

## Design Decisions

### D1: Dedicated geometry-library.js Module (Internal, Not on window.depthkit)

**Decision:** Geometry materialization is implemented in `src/page/geometry-library.js` as a separate module imported by `scene-renderer.js`. Its functions are NOT exposed on `window.depthkit` — they are internal page-side utilities called only by the protocol handlers.

**Rationale:** OBJ-010 established `geometry-library.js` as the stub for geometry materialization. Separating concerns keeps `scene-renderer.js` focused on protocol handling (scene registry, visibility, multi-pass compositing per OBJ-011) while `geometry-library.js` focuses on Three.js object creation. Since esbuild bundles everything into a single IIFE (per OBJ-001), the import is resolved at build time. Not exposing on `window.depthkit` prevents external callers from bypassing OBJ-011's scene lifecycle management.

### D2: Direct THREE.TextureLoader, Not OBJ-015's Cache API

**Decision:** `geometry-library.js` loads textures directly via `THREE.TextureLoader.loadAsync()`, applying the same texture configuration conventions as OBJ-015 (SRGBColorSpace, trilinear minFilter, bilinear magFilter). It does NOT call OBJ-015's `window.depthkit.loadTexture()` / `getTexture()` API.

**Deviation from OBJ-015's "Consumed by" prediction:** OBJ-015's spec (verified) states in its integration table that OBJ-039 "Calls `getTexture(slotName)` to retrieve loaded textures and assign them to mesh materials during scene instantiation. Uses `getTextureMetadata()` for aspect-ratio-aware plane sizing." This prediction was incorrect. At implementation time, the architectural choice becomes clear: textures loaded into OBJ-015's global cache create dual-ownership problems with OBJ-011's per-scene teardown lifecycle.

**Alternatives considered:**
1. **Use OBJ-015's cache with scene-scoped IDs** (e.g., `scene_001:floor`) — Creates dual-ownership issues. OBJ-011's `teardownScene` disposes textures from the scene group directly (via `disposeSceneGroup`). If those same textures also exist in OBJ-015's global cache, disposal leaves stale cache entries, or teardown must coordinate with OBJ-015's `unloadTexture()` for each slot — adding cross-module coupling for no benefit.
2. **Direct THREE.TextureLoader** (chosen) — Textures are owned exclusively by the scene group's `PageSceneEntry`. Disposal is straightforward: traverse the group and dispose each texture. No global cache coordination needed.

**Actual relationship to OBJ-015:** OBJ-039 depends on OBJ-015 for its **texture configuration conventions** (SRGBColorSpace, LinearMipmapLinearFilter, LinearFilter), not for its runtime API. Both modules apply the same settings to ensure visual consistency regardless of which loading path was used. OBJ-015's Node-side `checkTextureSlotCompatibility()` remains available to the orchestrator using `naturalWidth`/`naturalHeight` from the slot results reported back via the protocol.

### D3: Magenta Fallback Material for Failed Textures

**Decision:** When a texture fails to load (network error, corrupt file, exceeds MAX_TEXTURE_SIZE), the mesh is created with a solid magenta `MeshBasicMaterial` (color: `0xff00ff`) instead of skipping the mesh entirely.

**Rationale:** Per OBJ-011's spec. Preserving the mesh at its correct position/rotation makes spatial layout issues diagnosable in rendered output. Magenta is a visually unmistakable debug indicator that cannot be mistaken for a valid scene element. The orchestrator receives `SceneSetupResult.success = false` and can abort rendering if strict mode is desired.

### D4: Group Created with visible=false

**Decision:** The `THREE.Group` returned by `materializeScene` has `visible = false` and `group.name` set to the `sceneId`.

**Rationale:** Per OBJ-011 D3 — prevents newly-setup scenes from flashing into rendered output before the orchestrator is ready. `renderComposite` (OBJ-011) sets visibility per-frame.

### D5: Mesh.name Set to Slot Name

**Decision:** Each mesh has its `name` property set to the slot name (e.g., `'floor'`, `'subject'`).

**Rationale:** Aids debugging in Three.js inspector/logs. Also enables `renderComposite` to identify meshes by slot name if needed for future per-slot opacity manipulation (OBJ-044).

### D6: Parallel Texture Loading with Promise.allSettled

**Decision:** All textures for a scene load concurrently via `Promise.allSettled()`. Individual slot failures do not block other slots from loading.

**Rationale:** Per OBJ-011 D7 — per-slot error reporting allows the protocol to return detailed status while the orchestrator decides whether to abort. Unlike OBJ-015's batch load (`Promise.all`, fail-fast), `materializeScene` always creates all meshes (with fallback materials for failures), so `Promise.allSettled` is the correct primitive here.

### D7: POSIX-Only Path Resolution

**Decision:** Texture URL resolution supports POSIX absolute paths (starting with `/`), `file://`, `data:`, `http://`, and `https://` URLs. Windows paths are not supported.

**Rationale:** Per OBJ-011 D6 and seed C-08/C-11 (Linux VPS and Docker targets). Path detection is by prefix matching, not by parsing — simple and deterministic.

### D8: disposeSceneGroup Uses group.traverse()

**Decision:** `disposeSceneGroup` uses `group.traverse()` to find all meshes rather than assuming direct children only.

**Rationale:** Future-proofs against geometry implementations that might nest groups. For V1, all meshes are direct children of the scene group, but `traverse()` handles both flat and nested structures correctly with no additional cost for the flat case.

### D9: Material color Set to 0xffffff for Textured Meshes

**Decision:** When a texture is successfully loaded, the material's `color` is set to `0xffffff` (white). `MeshBasicMaterial` multiplies the texture color by the material color, so white preserves the texture's original colors. When no texture is available (fallback), color is `0xff00ff` (magenta).

**Rationale:** Ensures textures display at their true colors. If the `color` property were omitted, Three.js defaults to white anyway, but setting it explicitly documents intent and ensures the fallback path produces a distinctly colored mesh.

### D10: MAX_TEXTURE_SIZE Validation After Load

**Decision:** `loadSlotTexture` validates loaded texture dimensions against `renderer.capabilities.maxTextureSize` after loading. If either dimension exceeds the limit, the loaded texture is disposed and an error is thrown with the message format specified by OBJ-011: `"Texture dimensions {w}x{h} exceed WebGL max texture size {max}"`. The slot receives a magenta fallback mesh.

**Rationale:** OBJ-011's edge case table explicitly specifies this validation as a page-side responsibility. The `maxTextureSize` value is read from `window.depthkit.renderer.capabilities.maxTextureSize` by `materializeScene` and passed to `loadSlotTexture` as a parameter, keeping `loadSlotTexture` a pure function that doesn't reach into global state.

### D11: Single TextureLoader Instance per materializeScene Call

**Decision:** `materializeScene` creates a single `THREE.TextureLoader` instance and reuses it for all slots within a scene. The loader is not cached across scenes.

**Rationale:** `THREE.TextureLoader` is lightweight (it's a thin wrapper over `HTMLImageElement` loading). Creating one per scene setup is negligible. Sharing across scenes would require global state management with no measurable benefit.

### D12: Image Dimension Fallback Chain

**Decision:** After loading a texture, image dimensions are read with a fallback chain: `naturalWidth = texture.image.naturalWidth ?? texture.image.width` and `naturalHeight = texture.image.naturalHeight ?? texture.image.height`.

**Rationale:** `THREE.TextureLoader` internally creates an `HTMLImageElement`, which has both `naturalWidth`/`naturalHeight` and `width`/`height`. However, in some Three.js configurations or newer versions, `createImageBitmap()` may be used instead, producing `ImageBitmap` objects that only have `width`/`height`. The fallback chain handles either case correctly.

## Acceptance Criteria

- [ ] **AC-01:** `src/page/geometry-library.js` exports `materializeScene`, `createSlotMesh`, `loadSlotTexture`, `resolveTextureUrl`, and `disposeSceneGroup` functions.

- [ ] **AC-02:** `materializeScene('scene_001', slots)` with a single slot containing a valid PNG texture returns a `SceneMaterializationResult` with `success === true`, the slot's `status === 'loaded'`, `naturalWidth > 0`, `naturalHeight > 0`, and a `group` containing exactly one child mesh.

- [ ] **AC-03:** The returned `group` has `visible === false` and `group.name === 'scene_001'` (matching the sceneId argument).

- [ ] **AC-04:** The mesh within the group has `position`, `rotation`, and `renderOrder` values matching the corresponding `SlotSetup` values exactly. Rotation uses Three.js default Euler order `'XYZ'`, consistent with OBJ-003's `EulerRotation` type `[rx, ry, rz]`.

- [ ] **AC-05:** The mesh's material is an instance of `THREE.MeshBasicMaterial` with `map` set to the loaded texture, `side === THREE.FrontSide`, and `opacity === 1.0`.

- [ ] **AC-06:** For a slot with `transparent: true`, the mesh's material has `transparent === true` and `alphaTest === 0.01`.

- [ ] **AC-07:** For a slot with `transparent` omitted or `false`, the mesh's material has `transparent === false` and `alphaTest === 0`.

- [ ] **AC-08:** For a slot with `fogImmune: true`, the mesh's material has `fog === false`.

- [ ] **AC-09:** For a slot with `fogImmune` omitted or `false`, the mesh's material has `fog === true`.

- [ ] **AC-10:** When a texture fails to load (e.g., nonexistent file path), the mesh is still created with a magenta `MeshBasicMaterial` (`material.color` equals `0xff00ff`), the slot's `status === 'error'`, `error` contains a non-empty string, and `SceneMaterializationResult.success === false`.

- [ ] **AC-11:** `materializeScene` with multiple slots loads all textures concurrently. If one slot's texture fails, other slots still load successfully with `status === 'loaded'`. The `group` contains one mesh per slot regardless of load status.

- [ ] **AC-12:** Loaded textures have `colorSpace === THREE.SRGBColorSpace`, `minFilter === THREE.LinearMipmapLinearFilter`, and `magFilter === THREE.LinearFilter`.

- [ ] **AC-13:** `resolveTextureUrl('/path/to/image.png')` returns `'file:///path/to/image.png'`.

- [ ] **AC-14:** `resolveTextureUrl('file:///already/a/url.png')` returns the input unchanged.

- [ ] **AC-15:** `resolveTextureUrl('data:image/png;base64,...')` returns the input unchanged.

- [ ] **AC-16:** `resolveTextureUrl('http://example.com/img.png')` and `resolveTextureUrl('https://example.com/img.png')` return the input unchanged.

- [ ] **AC-17:** `resolveTextureUrl('relative/path.png')` throws an Error with message containing `"Unsupported texture source format"`.

- [ ] **AC-18:** `disposeSceneGroup(group)` calls `.dispose()` on each mesh's geometry, material, and material.map (when non-null), then removes the group from its parent and clears the group's children. Returns `{ meshesRemoved, texturesDisposed }` with accurate counts.

- [ ] **AC-19:** `disposeSceneGroup` on a group containing meshes with magenta fallback materials (no texture map) does not throw and reports `texturesDisposed` counting only meshes that had non-null `material.map`.

- [ ] **AC-20:** Each mesh's `name` property equals the slot name string (e.g., `'floor'`, `'subject'`).

- [ ] **AC-21:** Each mesh's `PlaneGeometry` has parameters matching `slot.size[0]` (width) and `slot.size[1]` (height).

- [ ] **AC-22:** `materializeScene` with an empty `slots` record `{}` returns a group with no children, `success === true`, empty `slots` result, and empty maps.

- [ ] **AC-23:** After `disposeSceneGroup`, the group has no children and `group.parent === null`.

- [ ] **AC-24:** A mesh created by `materializeScene`, when the group is added to `window.depthkit.scene` with `visible = true`, renders a visible (non-black) frame when captured via `canvas.toDataURL()` after `window.depthkit.renderFrame()`.

- [ ] **AC-25:** `geometry-library.js` functions are NOT exposed on `window.depthkit`. They are internal to the page bundle, called only by `scene-renderer.js`.

- [ ] **AC-26:** `loadSlotTexture('')` rejects with `"Texture source is empty"`. `loadSlotTexture` with a `null` or `undefined` argument rejects with the same message.

- [ ] **AC-27:** For a slot with a successfully loaded texture, the mesh's material has `color` equal to `0xffffff` (white), ensuring the texture displays at its true colors without tinting.

- [ ] **AC-28:** When a loaded texture's dimensions exceed `renderer.capabilities.maxTextureSize` (e.g., a 8192×8192 image on a context with maxTextureSize=4096), `loadSlotTexture` disposes the loaded texture and rejects with message `"Texture dimensions {w}x{h} exceed WebGL max texture size {max}"`. The slot gets a magenta fallback mesh in `materializeScene`, with `status === 'error'` and the error message included.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Empty `slots` record `{}` | Returns group with no children. `success === true`. Empty `slots` result, empty `meshMap`, empty `textureMap`. |
| All textures fail to load | `success === false`. All slots have magenta fallback meshes with `status === 'error'`. Group contains one mesh per slot. |
| Texture source is empty string | `loadSlotTexture` rejects: `"Texture source is empty"`. Slot gets magenta fallback in `materializeScene`. |
| Texture source is `null` or `undefined` | `loadSlotTexture` rejects: `"Texture source is empty"` (falsy check). Slot gets magenta fallback. |
| Texture source is relative path (`images/foo.png`) | `resolveTextureUrl` throws: `"Unsupported texture source format..."`. Slot gets magenta fallback. |
| Texture source is Windows path (`C:\images\foo.png`) | `resolveTextureUrl` throws (no leading `/`, not a recognized protocol prefix). Slot gets magenta fallback. |
| Texture exceeds MAX_TEXTURE_SIZE (e.g., 8192×8192 on a 4096 context) | `loadSlotTexture` disposes the loaded texture and rejects: `"Texture dimensions 8192x8192 exceed WebGL max texture size 4096"`. Slot gets magenta fallback. |
| Texture file is corrupt/truncated | `THREE.TextureLoader.loadAsync()` rejects. Error message propagated. Slot gets magenta fallback. |
| Slot with `size: [0, 0]` | `PlaneGeometry` created with zero dimensions. Mesh exists but renders as invisible (degenerate geometry). No error thrown by OBJ-039. Manifest validation (OBJ-004) should prevent this upstream. |
| Slot with negative size components | `PlaneGeometry` created with negative dimensions (Three.js takes absolute value internally for geometry, or produces degenerate mesh). No error thrown. Manifest validation should prevent upstream. |
| `renderOrder` is very large (e.g., 999999) | Passed directly to `mesh.renderOrder`. Three.js accepts any number. |
| `renderOrder` omitted | Defaults to 0 (`slot.renderOrder ?? 0`). |
| `transparent` omitted | Defaults to `false` (`slot.transparent ?? false`). |
| `fogImmune` omitted | Defaults to `false` (`slot.fogImmune ?? false`), meaning `material.fog = true`. |
| Multiple slots with same `renderOrder` | Valid. Three.js uses insertion order as secondary sort for equal renderOrder values. |
| `disposeSceneGroup` on a group not added to any scene | `group.removeFromParent()` is a no-op if group has no parent. Meshes still disposed. Returns correct counts. |
| `disposeSceneGroup` called twice on same group | Second call: group has no children (cleared on first call). Returns `{ meshesRemoved: 0, texturesDisposed: 0 }`. No error — `dispose()` on already-disposed Three.js objects is safe. |
| Data URI texture with invalid base64 | Browser image decode fails. `TextureLoader.loadAsync()` rejects. Slot gets magenta fallback. |
| Data URI texture with valid image | Loads normally. `naturalWidth`/`naturalHeight` reflect the decoded image dimensions. |
| `sceneId` is empty string in `materializeScene` | Group created with `name === ''`. No error from geometry-library. OBJ-011's protocol layer validates sceneId before calling this function. |
| Slot position/rotation contain `NaN` | Mesh position/rotation set to `NaN`. Three.js renders nothing for that mesh (degenerate transform). No error thrown. Upstream validation should prevent. |
| `texture.image` is `ImageBitmap` (no `naturalWidth`/`naturalHeight`) | Dimension fallback chain: `naturalWidth = texture.image.naturalWidth ?? texture.image.width`, `naturalHeight = texture.image.naturalHeight ?? texture.image.height`. Reports correct dimensions. |

## Test Strategy

### Testing Access Pattern

Since `geometry-library.js` functions are internal to the IIFE bundle (AC-25), Puppeteer integration tests exercise them **indirectly** through `window.depthkit.setupScene()` (OBJ-011's page-side protocol handler), which delegates to `materializeScene()`. Test assertions inspect the resulting scene graph via `page.evaluate()` using `window.depthkit.scene.children` to examine group structure, mesh properties, and material settings. Similarly, `window.depthkit.teardownScene()` exercises `disposeSceneGroup()`.

For URL resolution behavior (`resolveTextureUrl`), tests verify observable outcomes: `setupScene` with various `textureSrc` formats (absolute path, data URI, relative path, etc.) and checking whether each slot's load status is `'loaded'` or `'error'` with the expected error message.

### Test Fixtures

Small solid-color PNG images (e.g., 100×100 pixels: red, blue, green) and one transparent PNG (colored circle on transparent background). Generated programmatically or provided as static fixtures. Served to the browser via Puppeteer request interception, written as temporary files to disk (absolute POSIX paths), or encoded as data URIs.

### Puppeteer-Based Integration Tests

**Materialization tests (via setupScene):**
1. Single slot with valid texture: verify group has 1 child, mesh has correct position/rotation/renderOrder/name, material has loaded texture with `color === 0xffffff`.
2. Multiple slots (3): verify group has 3 children, each mesh has correct properties.
3. Empty slots record: verify empty group, `success === true`.
4. Verify `group.visible === false` and `group.name === sceneId`.

**Texture loading tests (via setupScene):**
5. Valid absolute POSIX path: `status === 'loaded'`, `naturalWidth`/`naturalHeight` correct.
6. Valid data URI: `status === 'loaded'`.
7. Nonexistent file path: `status === 'error'`, mesh has magenta material (`material.color.getHex() === 0xff00ff`).
8. Relative path: `status === 'error'`, error message contains `"Unsupported texture source format"`.
9. Mixed success/failure (2 valid + 1 invalid): 2 loaded, 1 error, `success === false`, group has 3 meshes.
10. Empty string `textureSrc`: `status === 'error'`, error contains `"Texture source is empty"`.

**MAX_TEXTURE_SIZE tests:**
11. If feasible: load a texture whose dimensions exceed the WebGL context's `maxTextureSize` (may require generating a large test image). Verify `status === 'error'` with message containing `"exceed WebGL max texture size"`. If generating a large enough image for testing is impractical, document that this path is tested via a unit test in a future objective or via mocking.

**Material property tests (inspected via page.evaluate on scene graph):**
12. `transparent: true` → `material.transparent === true`, `material.alphaTest === 0.01`.
13. `transparent: false` → `material.transparent === false`, `material.alphaTest === 0`.
14. `transparent` omitted → same as `false`.
15. `fogImmune: true` → `material.fog === false`.
16. `fogImmune: false` → `material.fog === true`.
17. `fogImmune` omitted → `material.fog === true`.
18. `renderOrder: 5` → `mesh.renderOrder === 5`.
19. `renderOrder` omitted → `mesh.renderOrder === 0`.
20. Texture `colorSpace`, `minFilter`, `magFilter` match expected Three.js constants.
21. Successfully loaded texture → `material.color.getHex() === 0xffffff`.

**Rendering test:**
22. Materialize a scene with a textured slot via `setupScene`, set `group.visible = true`, call `renderFrame()` with a standard camera state, capture `canvas.toDataURL()`, verify frame is not all-black.
23. Render same scene with camera at two different positions. Verify captured frames differ (perspective projection produces different views).

**Disposal tests (via teardownScene):**
24. `teardownScene`: verify returned `meshesRemoved` and `texturesDisposed` match expectations.
25. After teardown, verify scene graph has no remaining children from the disposed group.
26. Teardown with magenta fallback meshes: `texturesDisposed` does not count fallback slots. No error thrown.
27. Double teardown: second call throws `SCENE_NOT_FOUND` (OBJ-011 protocol behavior), verifying the scene was fully removed on first call.

**Geometry dimension tests:**
28. Inspect `mesh.geometry.parameters` to verify `width === slot.size[0]` and `height === slot.size[1]`.

### Relevant Testable Claims

- **TC-02** (render performance): Materialization time (texture loading + mesh creation) contributes to per-scene setup time. Tests should log timing for benchmarking.
- **TC-04** (scene geometries eliminate manual 3D positioning): Meshes are positioned entirely from SlotSetup data — no manual coordinates in the page code. All 3D placement comes from the orchestrator via geometry definitions.
- **TC-05** (tunnel geometry produces convincing depth): When tunnel geometry slots are materialized and rendered with a forward camera push, the perspective distortion should be visible in captured frames.
- **TC-06** (deterministic output): Same slots + same textures + same camera state → identical captured frame. Material settings are deterministic.

## Integration Points

### Depends on

| Dependency | What OBJ-039 uses |
|---|---|
| **OBJ-010** (Page shell) | Three.js runtime environment: `THREE.PlaneGeometry`, `THREE.MeshBasicMaterial`, `THREE.Mesh`, `THREE.Group`, `THREE.TextureLoader`, `THREE.SRGBColorSpace`, `THREE.LinearMipmapLinearFilter`, `THREE.LinearFilter`, `THREE.FrontSide`. `window.depthkit.renderer.capabilities.maxTextureSize` for texture validation. OBJ-039 runs in the same Chromium page and uses Three.js (bundled into the IIFE by esbuild). |
| **OBJ-005** (Geometry types) | Informs the `SlotSetup` field structure consumed (position, rotation, size, transparent, renderOrder, fogImmune). OBJ-039 does not import OBJ-005 directly — it receives `SlotSetup` data as plain JSON from OBJ-011's protocol. The field names and semantics match OBJ-005's `PlaneSlot`. |
| **OBJ-015** (Texture loader) | **Convention dependency only — NOT API dependency.** OBJ-039 follows OBJ-015's texture configuration conventions (SRGBColorSpace, LinearMipmapLinearFilter, LinearFilter) to ensure visual consistency. OBJ-039 does NOT call OBJ-015's `loadTexture()`/`getTexture()` API. OBJ-015's "Consumed by" table predicted OBJ-039 would call these APIs; this prediction was superseded by the direct-loading approach (see D2). OBJ-015's Node-side `checkTextureSlotCompatibility()` remains available to the orchestrator using `naturalWidth`/`naturalHeight` from slot results. |
| **OBJ-011** (Message protocol) | Defines `SlotSetup` type (the input to `materializeScene`). Defines `SceneSetupResult` and `SceneTeardownResult` types (the output format the protocol expects). `scene-renderer.js`'s `setupScene()` and `teardownScene()` handlers call `materializeScene()` and `disposeSceneGroup()` respectively, mapping results to protocol response types. |

### Consumed by

| Downstream | How it uses OBJ-039 |
|---|---|
| OBJ-011's page-side implementation (`scene-renderer.js`) | `setupScene()` delegates Three.js object creation to `materializeScene()`. `teardownScene()` delegates resource cleanup to `disposeSceneGroup()`. This is the sole consumer. |

*OBJ-039 has no further downstream consumers in the progress map (`blocks: []`).*

### File Placement

```
depthkit/
  src/
    page/
      geometry-library.js    # IMPLEMENT — evolve from OBJ-010's stub.
                              #   Exports: materializeScene, createSlotMesh,
                              #   loadSlotTexture, resolveTextureUrl,
                              #   disposeSceneGroup
      scene-renderer.js      # MODIFY — import geometry-library.js functions.
                              #   setupScene() calls materializeScene() and
                              #   maps result to PageSceneEntry + SceneSetupResult.
                              #   teardownScene() calls disposeSceneGroup() and
                              #   maps result to SceneTeardownResult.
```

## Open Questions

### OQ-A: Should materializeScene report alpha detection per slot?

OBJ-015 defines alpha detection via canvas pixel sampling (~5ms per texture). `materializeScene` could replicate this and include `hasAlpha` in slot results, enabling the Node-side orchestrator to call `checkTextureSlotCompatibility()` with complete data. Currently, only `naturalWidth`/`naturalHeight` are reported.

**Recommendation:** Defer for V1. The orchestrator can rely on manifest-level `transparent` flags matching image generation pipeline conventions (subject images generated with alpha, backgrounds without). If mismatches cause visual issues in production, alpha detection can be added to `loadSlotTexture` as a follow-up without changing the API contract — just add `hasAlpha` to the returned object and to `SlotMaterializationResult`.

### OQ-B: Should texture configuration (colorSpace, filters) be parameterizable?

Currently hardcoded to SRGBColorSpace + trilinear/bilinear, matching OBJ-015 D10. Future use cases (normal maps, data textures for OQ-09 lighting) might need different settings.

**Recommendation:** Hardcode for V1. If lighting (OQ-09) is adopted, add optional `colorSpace` and `filter` fields to `SlotSetup` (which would require a protocol-types.ts change in OBJ-011).

### OQ-C: Should materializeScene validate slot data?

Currently, `materializeScene` trusts the `SlotSetup` data (position/rotation/size are valid numbers, etc.). The orchestrator (OBJ-036) constructs `SlotSetup` from validated manifest data + validated geometry definitions (OBJ-005).

**Recommendation:** No. The page is a dumb renderer (OBJ-010 D1). Validation belongs on the Node side. The page creates what it's told to create. Adding validation in the page would duplicate Node-side logic and violate the architecture.

---

## Summary of Changes from Round 1

| Issue | Fix Applied |
|---|---|
| **Issue 1** (MAX_TEXTURE_SIZE contradiction) | Added D10 (MAX_TEXTURE_SIZE Validation After Load). `loadSlotTexture` now accepts `maxTextureSize` parameter, validates after load, disposes and rejects if exceeded. Added AC-28. Added edge case row for oversized textures. Added test #11 for MAX_TEXTURE_SIZE. |
| **Issue 2** (OBJ-015 dependency mismatch) | Expanded D2 with explicit "Deviation from OBJ-015's 'Consumed by' prediction" section. Updated integration table entry for OBJ-015 to say "Convention dependency only — NOT API dependency" with explanation of the superseded prediction. |
| **Issue 3** (naturalWidth fallback) | Added D12 (Image Dimension Fallback Chain). Updated `loadSlotTexture` contract step 4. Added edge case row for `ImageBitmap`. |
| **Issue 4** (test access mechanism) | Added "Testing Access Pattern" section at top of Test Strategy explaining indirect testing via `setupScene`/`teardownScene` and scene graph inspection via `page.evaluate()`. Reframed all test descriptions to reference the indirect invocation path. |
| **Issue 5** (missing white color AC) | Added AC-27 verifying `material.color === 0xffffff` for successfully loaded textures. Added test #21 for white color verification. |
| **Issue 6** (Euler order) | Added note in `createSlotMesh` contract step 5 and AC-04 documenting `'XYZ'` Euler order consistency with OBJ-003. |

I believe all six issues are now resolved. I'd like the Challenger to verify the fixes and confirm whether this spec is ready for convergence.

---

## Round 4 — spec_challenger

I've verified all six fixes from Round 2 against the revised spec:

| Issue | Verified? | Notes |
|---|---|---|
| 1 (MAX_TEXTURE_SIZE) | ✅ | D10 added with correct flow (load → validate → dispose+reject). AC-28 specifies exact error message format matching OBJ-011. `loadSlotTexture` takes `maxTextureSize` param keeping it pure. |
| 2 (OBJ-015 mismatch) | ✅ | D2 explicitly documents the deviation with rationale. Integration table says "Convention dependency only — NOT API dependency." |
| 3 (naturalWidth fallback) | ✅ | D12 added. Step 4 of `loadSlotTexture` uses `?? texture.image.width` fallback. Edge case row for ImageBitmap present. |
| 4 (test access) | ✅ | "Testing Access Pattern" section explains indirect testing via `setupScene`/`teardownScene` + scene graph inspection. All test descriptions reference the indirect path. |
| 5 (white color AC) | ✅ | AC-27 verifies `color === 0xffffff`. Test #21 added. |
| 6 (Euler order) | ✅ | Note in `createSlotMesh` step 5 and AC-04. |

No new issues introduced by the revisions. Scope is clean, vocabulary is correct, constraints are respected, and the spec is implementable without guessing.

CONCLUSION:

The spec for OBJ-039 defines the browser-side `geometry-library.js` module that materializes serialized `SlotSetup` data into Three.js scene graph objects. It provides `materializeScene`, `createSlotMesh`, `loadSlotTexture`, `resolveTextureUrl`, and `disposeSceneGroup` — all internal to the page bundle, called by OBJ-011's protocol handlers. Key design choices: direct `THREE.TextureLoader` (not OBJ-015's cache API) to avoid dual-ownership, `Promise.allSettled` for parallel texture loading with per-slot error reporting, magenta fallback materials for failed textures, MAX_TEXTURE_SIZE validation per OBJ-011's contract, and POSIX-only path resolution. 28 acceptance criteria cover material properties, texture loading, disposal, URL resolution, and rendering correctness.

Let me write the files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me first check if the node directory and meta.json exist:
[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-039/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "ls nodes/OBJ-039/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-039 node directory exists"
}
[Tool Result] meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-039/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-039",
     3→  "description": "Three.js page-side geometry instantiation -- how geometry definitions are loaded and instantiated in the browser page, mesh creation from PlaneSlot definitions (position, rotation, size), texture application to meshBasicMaterial, and scene graph construction. Responds to scene setup commands from the message protocol (OBJ-011).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-010", "OBJ-005", "OBJ-015", "OBJ-011"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration. Added OBJ-011 dep per Round 4 Issue B -- needs message protocol for scene setup commands."
    12→}
    13→
Good. Now let me write the final spec and update meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-039/output.md",
  "content": "# Specification: OBJ-039 \u2014 Three.js Page-Side Geometry Instantiation\n\n## Summary\n\nOBJ-039 implements `src/page/geometry-library.js` \u2014 the browser-side module that converts serialized slot definitions (from OBJ-011's `SceneSetupConfig`) into Three.js scene graph objects. It provides functions to: (1) create textured plane meshes from `SlotSetup` data with correct position, rotation, size, and material properties, (2) load textures via `THREE.TextureLoader` with proper configuration matching OBJ-015's conventions, (3) validate loaded textures against `MAX_TEXTURE_SIZE`, (4) assemble meshes into a `THREE.Group` for scene management, and (5) dispose of scene resources cleanly. This module is called by `scene-renderer.js`'s `setupScene()` and `teardownScene()` handlers defined by OBJ-011's protocol.\n\n## Interface Contract\n\n### Module: `src/page/geometry-library.js`\n\nThis module fulfills the stub established by OBJ-010. It is imported by `scene-renderer.js` and its functions are called from OBJ-011's protocol handlers. Functions are NOT exposed on `window.depthkit` directly \u2014 they are internal page-side utilities called only by the protocol handlers.\n\n```typescript\n// Conceptual contract \u2014 implementation is plain JS running in Chromium.\n// Types here document the contract; implementation is JS.\n\n/**\n * Result of materializing a single slot into a Three.js mesh.\n */\ninterface SlotMaterializationResult {\n  /** The slot name. */\n  slotName: string;\n  /** The created mesh (always created, even on texture failure). */\n  mesh: THREE.Mesh;\n  /** The loaded texture, or null if loading failed. */\n  texture: THREE.Texture | null;\n  /** Whether the texture loaded successfully. */\n  status: 'loaded' | 'error';\n  /** Natural width of the loaded texture in pixels. Present when status='loaded'. */\n  naturalWidth?:
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-039/output.md
Now update meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-039/meta.json",
  "content": "{\n  \"id\": \"OBJ-039\",\n  \"description\": \"Three.js page-side geometry instantiation -- how geometry definitions are loaded and instantiated in the browser page, mesh creation from PlaneSlot definitions (position, rotation, size), texture application to meshBasicMaterial, and scene graph construction. Responds to scene setup commands from the message protocol (OBJ-011).\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T04:15:00Z\",\n  \"depends_on\": [\"OBJ-010\", \"OBJ-005\", \"OBJ-015\", \"OBJ-011\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 3 engine integration. Added OBJ-011 dep per Round 4 Issue B -- needs message protocol for scene setup commands. Spec deliberated in 4 rounds, 6 issues raised and resolved: MAX_TEXTURE_SIZE validation per OBJ-011 contract, OBJ-015 API deviation documented, naturalWidth/ImageBitmap fallback chain, test access pattern clarified, material color AC added, Euler order documented.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-039/meta.json has been updated successfully.
Now commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-039/output.md nodes/OBJ-039/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-039): Three.js page-side geometry instantiation\n\nDefines geometry-library.js \u2014 the browser-side module that converts\nserialized SlotSetup data into Three.js scene graph objects. Provides\nmaterializeScene, createSlotMesh, loadSlotTexture, resolveTextureUrl,\nand disposeSceneGroup functions. Key decisions: direct TextureLoader\n(not OBJ-015 cache), Promise.allSettled for parallel loading, magenta\nfallback materials, MAX_TEXTURE_SIZE validation per OBJ-011 contract.\n28 acceptance criteria. Deliberated in 4 rounds, 6 issues resolved.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-039 spec output and updated meta.json"
}
[Tool Result] [master f281cf8] spec(OBJ-039): Three.js page-side geometry instantiation
 2 files changed, 509 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-039/output.md
The specification for OBJ-039 has been written to disk and committed. 

**Summary of the converged spec:**

- **Module:** `src/page/geometry-library.js` — internal page-side utilities (not exposed on `window.depthkit`)
- **5 exported functions:** `materializeScene`, `createSlotMesh`, `loadSlotTexture`, `resolveTextureUrl`, `disposeSceneGroup`
- **12 design decisions** covering texture loading strategy (direct TextureLoader, not OBJ-015 cache), magenta fallback materials, POSIX-only paths, MAX_TEXTURE_SIZE validation, Euler order, and image dimension fallback chains
- **28 acceptance criteria** covering material properties, texture loading, disposal, URL resolution, rendering correctness, and MAX_TEXTURE_SIZE validation
- **28 integration tests** exercised indirectly through OBJ-011's `setupScene`/`teardownScene` protocol handlers
- **3 open questions** deferred to future objectives (alpha detection, parameterizable texture config, slot data validation)
- **6 issues raised and resolved** across 4 deliberation rounds
