# Specification: OBJ-010 — Three.js Page Shell, Build/Bundle Architecture, and Scene Renderer Skeleton

## Summary

OBJ-010 establishes the browser-side rendering foundation and the authoritative Node.js/browser code-split architecture for depthkit. It delivers: (1) the final HTML page shell with a properly sized WebGL canvas, (2) the Three.js `Scene` / `PerspectiveCamera` / `WebGLRenderer` initialization skeleton that all downstream rendering depends on, (3) the architectural decision that the browser page is a **data-driven renderer** — a "dumb page" that receives computed scene state from the Node.js orchestrator and executes Three.js calls accordingly, and (4) a minimal `renderFrame()` primitive that downstream objectives build upon. This objective also defines Node-side TypeScript types for data crossing the Node/browser boundary (excluding geometry serialization, which is deferred to OBJ-011).

## Interface Contract

### Module: `src/page/scene-renderer.js`

This is the esbuild entry point (per OBJ-001). It initializes Three.js, exposes a global `window.depthkit` namespace, and imports the other page modules. After OBJ-010, this file contains the renderer skeleton — downstream objectives populate scene management and message handling.

```typescript
// Conceptual contract for window.depthkit (exposed as globals on the page).
// These are NOT TypeScript files — they are plain JS running in Chromium.
// Types here document the contract; implementation is JS.

interface DepthkitPage {
  /**
   * Initializes the Three.js renderer, camera, and scene.
   * Called once when the page is first set up by the orchestrator.
   *
   * Behavior:
   * - Creates a WebGLRenderer bound to the #depthkit-canvas element.
   * - Calls renderer.setSize(width, height) to set canvas intrinsic dimensions.
   * - Calls renderer.setPixelRatio(1) to prevent HiDPI scaling.
   * - Calls renderer.setClearColor(clearColor, clearAlpha) for the background.
   *   scene.background is NOT set — the clear color serves as the background.
   * - Creates a PerspectiveCamera with the specified (or default) parameters.
   * - Creates an empty Scene.
   *
   * Width and height are rounded to the nearest integer via Math.round().
   * If the input was not already an integer, a warning is logged to console:
   *   "depthkit: non-integer dimensions rounded: {input} -> {rounded}"
   *
   * @param config - Composition-level settings.
   * @throws Error if canvas element not found, already initialized, or WebGL fails.
   */
  init(config: PageInitConfig): void;

  /**
   * Returns true if init() has been called successfully.
   */
  isInitialized(): boolean;

  /**
   * Returns renderer diagnostic info for the orchestrator to log.
   *
   * Implementation hints:
   * - webglVersion: gl.getParameter(gl.VERSION) where gl = renderer.getContext()
   * - vendor / gpuRenderer: obtained via WEBGL_debug_renderer_info extension.
   *   If extension unavailable, return 'unknown'.
   *     const ext = gl.getExtension('WEBGL_debug_renderer_info');
   *     vendor = ext ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) : 'unknown';
   *     gpuRenderer = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown';
   * - maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE)
   *
   * If not initialized, returns a zeroed-out structure (see Edge Cases).
   */
  getRendererInfo(): RendererInfo;

  /**
   * Renders the current scene with the current camera to the canvas.
   * This is the primitive render call. OBJ-011's message protocol will
   * call this after setting camera state per frame.
   *
   * If cameraState is provided, updates the camera before rendering.
   * Fields are applied in this exact order:
   *   1. position — camera.position.set(x, y, z)
   *   2. lookAt — camera.lookAt(x, y, z)  (must follow position, since
   *      lookAt computes rotation from the camera's current position)
   *   3. fov — camera.fov = value; camera.updateProjectionMatrix()
   *
   * Only provided fields are updated; omitted fields leave the camera unchanged.
   * After applying any updates, calls renderer.render(scene, camera).
   *
   * @param cameraState - Optional partial camera state to apply before rendering.
   * @throws Error if not initialized.
   */
  renderFrame(cameraState?: {
    position?: [number, number, number];
    lookAt?: [number, number, number];
    fov?: number;
  }): void;

  /**
   * Disposes of all Three.js resources.
   * Calls renderer.forceContextLoss() then renderer.dispose() to ensure
   * the WebGL context is fully released.
   * Sets renderer, scene, camera to null.
   *
   * After dispose(), init() can be called again (re-entrant lifecycle).
   * Calling dispose() when not initialized is a no-op (idempotent).
   */
  dispose(): void;

  /**
   * The Three.js WebGLRenderer instance.
   * null before init() or after dispose().
   */
  renderer: THREE.WebGLRenderer | null;

  /**
   * The Three.js Scene instance.
   * Downstream objectives (OBJ-015, OBJ-011 scene setup commands)
   * add meshes to this scene.
   * null before init() or after dispose().
   */
  scene: THREE.Scene | null;

  /**
   * The Three.js PerspectiveCamera instance.
   * Camera path presets (consumed via OBJ-011 frame commands) update
   * this camera's position, lookAt, and fov each frame via renderFrame().
   * null before init() or after dispose().
   */
  camera: THREE.PerspectiveCamera | null;
}

interface PageInitConfig {
  /** Canvas width in pixels. Rounded to nearest integer if non-integer. Must be > 0 after rounding. */
  width: number;
  /** Canvas height in pixels. Rounded to nearest integer if non-integer. Must be > 0 after rounding. */
  height: number;
  /**
   * Background clear color as CSS hex string (e.g., '#000000').
   * Applied via renderer.setClearColor(). scene.background is NOT set.
   * Default: '#000000'.
   */
  clearColor?: string;
  /** Background clear alpha (0-1). Default: 1. */
  clearAlpha?: number;
  /** Initial camera FOV in degrees. Default: 50 (from OBJ-003 DEFAULT_CAMERA). */
  fov?: number;
  /** Camera near plane. Default: 0.1 (from OBJ-003 DEFAULT_CAMERA). */
  near?: number;
  /** Camera far plane. Default: 100 (from OBJ-003 DEFAULT_CAMERA). */
  far?: number;
  /** Initial camera position [x, y, z]. Default: [0, 0, 5] (from OBJ-003 DEFAULT_CAMERA). */
  cameraPosition?: [number, number, number];
  /** Initial camera lookAt target [x, y, z]. Default: [0, 0, 0] (from OBJ-003 DEFAULT_CAMERA). */
  cameraLookAt?: [number, number, number];
  /**
   * Whether to enable antialiasing on the WebGL context.
   * Default: false. Antialiasing produces implementation-defined results
   * across GPU hardware and SwiftShader, violating C-05 (deterministic output).
   * Enable only if visual tuning objectives (OBJ-059-066) determine it's needed
   * and determinism is verified across target environments.
   */
  antialias?: boolean;
  /**
   * Whether to request a WebGL context with preserveDrawingBuffer.
   * Required for canvas.toDataURL() capture method.
   * Default: true (required for frame capture).
   */
  preserveDrawingBuffer?: boolean;
}

interface RendererInfo {
  /** True if init() succeeded. */
  initialized: boolean;
  /** Canvas dimensions [width, height] in pixels. */
  canvasSize: [number, number];
  /** WebGL version string (e.g., 'WebGL 2.0 (OpenGL ES 3.0 Chromium)'). */
  webglVersion: string;
  /** GPU vendor string from WEBGL_debug_renderer_info, or 'unknown'. */
  vendor: string;
  /** GPU renderer string (e.g., 'SwiftShader', 'ANGLE (...)'), or 'unknown'. */
  gpuRenderer: string;
  /** Max texture size supported by the WebGL context. */
  maxTextureSize: number;
  /** Whether antialiasing is enabled. */
  antialias: boolean;
}
```

### Module: `src/page/geometry-library.js`

After OBJ-010, this file contains a **stub with a documented contract**. The geometry materialization function is populated by downstream objectives once OBJ-005 (geometry type contract) and OBJ-011 (message protocol, which defines `SerializedGeometry`) are finalized.

```javascript
// src/page/geometry-library.js
// Stub: Geometry materialization logic.
//
// This module will contain functions that convert serialized geometry
// descriptions (plain JSON objects) into Three.js meshes added to a scene.
//
// The serialized geometry contract is defined by OBJ-011 (message protocol),
// which depends on OBJ-005 (geometry type contract) for the slot structure.
//
// OBJ-010 does not define the serialization format — it provides the
// renderer, scene, and camera that geometry materialization targets.
//
// TODO: OBJ-005 + OBJ-011 — Geometry materialization
export {};
```

### Module: `src/page/message-handler.js`

After OBJ-010, this file contains a **stub**. OBJ-011 defines the full message handling protocol.

```javascript
// src/page/message-handler.js
// Stub: Message protocol between Puppeteer orchestrator and browser page.
//
// OBJ-011 defines every message type crossing the Node.js/browser boundary:
// frame step commands, scene setup/teardown, texture loading signals, etc.
//
// Messages arrive via page.evaluate() calls from the Node.js orchestrator.
// The handler calls into window.depthkit methods (init, renderFrame, dispose).
//
// TODO: OBJ-011 — Full message protocol
export {};
```

### Module: `src/page/index.html`

The final HTML shell (evolving the OBJ-001 stub):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>depthkit</title>
  <style>
    /* Reset all margins/padding. Canvas must be the exact composition size. */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; overflow: hidden; background: #000; }
    /* Canvas is positioned absolutely and sized by Three.js renderer.setSize() */
    #depthkit-canvas { display: block; }
  </style>
</head>
<body>
  <canvas id="depthkit-canvas"></canvas>
  <script src="scene-renderer.js"></script>
</body>
</html>
```

### Node-Side Types: `src/engine/page-types.ts`

Shared TypeScript types for the data structures that cross the Node/browser boundary. These types live on the Node side only — the browser receives plain objects via `page.evaluate()`. Limited to types OBJ-010 owns: initialization config, renderer info, and per-frame camera state. Geometry serialization types are deferred to OBJ-011.

```typescript
// src/engine/page-types.ts

import type { Vec3 } from '../spatial/types.js';

/**
 * Configuration sent to the page's init() function.
 * Serializable as JSON — no functions, no class instances.
 */
export interface PageInitConfig {
  width: number;
  height: number;
  clearColor?: string;
  clearAlpha?: number;
  fov?: number;
  near?: number;
  far?: number;
  cameraPosition?: Vec3;
  cameraLookAt?: Vec3;
  antialias?: boolean;
  preserveDrawingBuffer?: boolean;
}

/**
 * Diagnostic info returned by the page's getRendererInfo() function.
 */
export interface RendererInfo {
  initialized: boolean;
  canvasSize: [number, number];
  webglVersion: string;
  vendor: string;
  gpuRenderer: string;
  maxTextureSize: number;
  antialias: boolean;
}

/**
 * Partial camera state for the page's renderFrame() function.
 * Sent per-frame by the orchestrator (via OBJ-011 message protocol).
 */
export interface FrameCameraState {
  position?: Vec3;
  lookAt?: Vec3;
  fov?: number;
}
```

## Design Decisions

### D1: Data-Driven Renderer (Dumb Page / Smart Orchestrator)

**Decision:** The browser page is a **generic, data-driven Three.js renderer**. It does NOT contain geometry definitions, camera path logic, or scene sequencing intelligence. Instead:

- **Node.js side** holds all domain logic: manifest parsing, geometry definitions (OBJ-005), camera path presets (OBJ-006), scene sequencing (OBJ-015), the virtualized clock (OBJ-009), and frame-by-frame camera state computation.
- **Browser side** receives pre-computed state for each frame and executes Three.js API calls.
- Geometry data (slot positions, rotations, sizes) is serialized as JSON-compatible objects on the Node side and passed to the page via `page.evaluate()` during scene setup.

**Alternatives considered:**

1. **Smart Page** (seed Section 4.4 sketch) — Camera interpolation, easing, and scene timing run inside the browser. The orchestrator sends only frame numbers. Requires bundling interpolation, camera presets, and sequencer into the page.
2. **Hybrid** — Camera interpolation in browser, everything else on Node. Reduces per-frame data but still splits domain logic.
3. **Dumb Page** (chosen) — Orchestrator computes complete scene state per frame and sends it. Page applies values and calls `renderer.render()`.

**Rationale for Dumb Page:**

- **Single source of truth.** Geometry definitions, camera paths, and timing logic exist in one place (Node.js TypeScript). No risk of drift between Node validation and browser rendering.
- **Simpler browser bundle.** Only Three.js + a thin rendering shell. No `src/interpolation/`, `src/spatial/`, camera presets, or scene sequencing.
- **Easier debugging.** Orchestrator logs exact camera state per frame. Inspectable on Node side without browser DevTools.
- **Per-frame data is small.** A frame command is ~200 bytes of JSON. At 30fps, ~6KB/s — negligible for in-process Puppeteer.
- **Purest C-03 expression.** The page never computes time. It renders what it's told.

**Impact on OBJ-002 (interpolation):** Runs only on Node side. Does not need to be bundled for browser.

**Impact on OBJ-011 (message protocol):** Frame commands include computed camera state (position, lookAt, FOV), not just frame numbers.

### D2: Canvas Sized by JavaScript, Not CSS

**Decision:** The `<canvas>` element has no explicit `width`/`height` attributes. `renderer.setSize(width, height)` sets intrinsic pixel dimensions and CSS display size during `init()`.

**Rationale:** Three.js's `setSize()` is canonical. Setting dimensions elsewhere leads to DPI/scaling bugs. Renderer owns the size.

**Pixel ratio:** `renderer.setPixelRatio(1)` is called explicitly. Chromium may report `devicePixelRatio > 1` even in headless mode. We need exactly 1:1 pixel mapping — a 1920x1080 canvas must produce a 1920x1080 frame buffer.

### D3: `preserveDrawingBuffer: true` as Default

**Decision:** The `WebGLRenderer` is created with `preserveDrawingBuffer: true` by default.

**Rationale:** Without this flag, canvas contents may be cleared after compositing, making `canvas.toDataURL()` return blank images. While CDP `Page.captureScreenshot` may not need it, `toDataURL()` is a common fallback. Negligible performance impact.

### D4: `antialias: false` as Default

**Decision:** The `WebGLRenderer` is created with `antialias: false` by default. Configurable via `PageInitConfig.antialias`.

**Rationale:** Antialiasing is implementation-defined across GPU hardware and SwiftShader. Different backends produce different sub-pixel results, violating C-05 (deterministic output). Defaulting to `false` ensures deterministic frame capture across environments. Visual tuning objectives (OBJ-059-066) may enable it if determinism is verified for their target environments.

### D5: Scene Lifecycle is Downstream's Responsibility

**Decision:** OBJ-010 provides a single `THREE.Scene` instance via `window.depthkit.scene`. Scene content lifecycle (adding/removing meshes, scene teardown between video scenes, transition rendering with multiple scenes or `autoClear` toggling) is managed by downstream objectives: OBJ-011 (message protocol for scene setup/teardown commands), OBJ-015 (scene sequencer), and OBJ-008 (transition system). OBJ-010 does not constrain or anticipate these patterns — it provides the renderer and scene primitives they build upon.

**Rationale:** OBJ-010's job is the rendering foundation. Scene management crosses into orchestration territory. The renderer skeleton should be neutral — usable by any downstream scene management approach.

### D6: Confirm OBJ-001's esbuild IIFE Strategy

**Decision:** OBJ-001's build strategy is confirmed without modification. `src/page/scene-renderer.js` is the single esbuild entry point, bundled as IIFE with Three.js inlined.

**Rationale:** The Dumb Page architecture (D1) means the page bundle is simple — Three.js + a rendering shell. No domain logic crosses the build boundary.

### D7: `window.depthkit` Global Namespace

**Decision:** The page exposes its API as `window.depthkit` — a single global object. Puppeteer interacts exclusively through this namespace via `page.evaluate()`.

**Rationale:** IIFE bundles don't produce ES module exports. A global namespace is the standard pattern for script-tag-loaded libraries.

### D8: Unlit Rendering by Default

**Decision:** OBJ-010 initializes the scene without lights. The default material for geometry meshes (downstream) is `THREE.MeshBasicMaterial` — textures display at full brightness.

**Rationale:** Seed OQ-09 explicitly defers the lighting decision. `MeshBasicMaterial` is the simplest correct choice for V1.

### D9: WebGL 2 Preferred, WebGL 1 Fallback Acceptable

**Decision:** The `WebGLRenderer` is created without forcing a specific WebGL version. Three.js defaults to WebGL 2 when available, falls back to WebGL 1. `getRendererInfo()` reports the acquired version.

**Rationale:** SwiftShader (C-11) supports WebGL 2. No V1 features require WebGL 2. Let Three.js negotiate.

### D10: Non-Integer Dimensions Rounded with Warning

**Decision:** `init()` rounds `width` and `height` to the nearest integer via `Math.round()`. If the input was not already an integer, a warning is logged: `"depthkit: non-integer dimensions rounded: {input} -> {rounded}"`. After rounding, if either dimension is <= 0, an Error is thrown.

**Rationale:** Canvas dimensions must be integers. `Math.round()` is more intuitive than `Math.floor()` (e.g., 1919.7 -> 1920 instead of 1919). The warning prevents silent resolution changes that could cause frame size mismatches with FFmpeg.

## Acceptance Criteria

- [ ] **AC-01:** `src/page/index.html` is a valid HTML5 document containing a `<canvas id="depthkit-canvas">` element and a `<script src="scene-renderer.js">` tag. CSS resets margin/padding to 0, hides overflow, and sets a black background.

- [ ] **AC-02:** `src/page/scene-renderer.js` imports Three.js, creates a `WebGLRenderer` bound to `#depthkit-canvas` during `init()`, and exposes `window.depthkit` with `init`, `dispose`, `isInitialized`, `getRendererInfo`, and `renderFrame` methods, plus `renderer`, `scene`, and `camera` properties.

- [ ] **AC-03:** After `window.depthkit.init({ width: 1920, height: 1080 })`, `isInitialized()` returns `true`, and `renderer`, `scene`, `camera` are non-null.

- [ ] **AC-04:** After `init({ width: 1920, height: 1080 })`, the canvas element's intrinsic dimensions (`canvas.width`, `canvas.height`) are exactly 1920 and 1080. `renderer.getPixelRatio()` returns 1.

- [ ] **AC-05:** After `init({ width: 1920, height: 1080, fov: 50 })`, `camera.fov === 50`, `camera.aspect` approximately equals `1920/1080`, `camera.near === 0.1`, `camera.far === 100`, and camera position is `[0, 0, 5]`.

- [ ] **AC-06:** `getRendererInfo()` after init returns `initialized: true`, `canvasSize: [1920, 1080]`, a non-empty `webglVersion` string, a numeric `maxTextureSize > 0`, and `antialias: false`.

- [ ] **AC-07:** `dispose()` calls `renderer.forceContextLoss()` then `renderer.dispose()`, sets `renderer`, `scene`, `camera` to null, and `isInitialized()` returns `false`. After dispose, `init()` succeeds again (re-entrant).

- [ ] **AC-08:** The `WebGLRenderer` is created with `preserveDrawingBuffer: true` (default). Verified: after calling `renderFrame()` on a scene containing a non-black mesh, `canvas.toDataURL()` returns a data URL that is NOT all-black.

- [ ] **AC-09:** `renderer.setPixelRatio(1)` is called regardless of `window.devicePixelRatio`. Canvas intrinsic dimensions always equal requested dimensions (not doubled for HiDPI).

- [ ] **AC-10:** When `init()` is called with no optional parameters, camera uses OBJ-003 `DEFAULT_CAMERA` values: `fov: 50`, `near: 0.1`, `far: 100`, position `[0, 0, 5]`, lookAt `[0, 0, 0]`.

- [ ] **AC-11:** `src/engine/page-types.ts` exports `PageInitConfig`, `RendererInfo`, and `FrameCameraState` types. All types are JSON-serializable (no functions, no class instances, no `THREE.*` types).

- [ ] **AC-12:** `npm run build` produces `dist/page/scene-renderer.js` (>500KB, Three.js included) and `dist/page/index.html`.

- [ ] **AC-13:** After `init()`, `scene` is a `THREE.Scene`. `scene.background` is null. The background is set via `renderer.setClearColor()`.

- [ ] **AC-14:** `init()` twice without `dispose()` throws: `"depthkit: already initialized. Call dispose() first."`.

- [ ] **AC-15:** `init()` with missing canvas element throws: `"depthkit: canvas element '#depthkit-canvas' not found"`.

- [ ] **AC-16:** The `WebGLRenderer` is created with `antialias: false` by default. Passing `antialias: true` in config enables it. `getRendererInfo().antialias` reflects the setting.

- [ ] **AC-17:** `renderFrame()` when not initialized throws: `"depthkit: not initialized. Call init() first."`.

- [ ] **AC-18:** `renderFrame({ position: [1, 2, 3], lookAt: [0, 0, -10], fov: 35 })` applies camera state in order (position, then lookAt, then fov + updateProjectionMatrix), then calls `renderer.render(scene, camera)`. After the call, `camera.position` is `(1, 2, 3)` and `camera.fov` is `35`.

- [ ] **AC-19:** `renderFrame()` with no arguments renders with the camera's current state (no changes applied).

- [ ] **AC-20:** `init({ width: 1919.7, height: 1080.3 })` rounds to 1920x1080 and logs a console warning about non-integer dimensions.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `init()` with no canvas in DOM | Throws `Error`: `"depthkit: canvas element '#depthkit-canvas' not found"` |
| `init()` called twice without `dispose()` | Throws `Error`: `"depthkit: already initialized. Call dispose() first."` |
| `init()` with `width <= 0` or `height <= 0` (after rounding) | Throws `Error`: `"depthkit: width and height must be positive integers, got {w}x{h}"` |
| `init()` with non-integer width/height | Rounds via `Math.round()`, logs console warning: `"depthkit: non-integer dimensions rounded: {input} -> {rounded}"` |
| WebGL context creation fails | Throws `Error`: `"depthkit: WebGL context creation failed. Ensure headless Chromium has WebGL support (SwiftShader or GPU)."` Listen for `webglcontextcreationerror` on canvas. |
| `dispose()` when not initialized | No-op. Idempotent. No throw. |
| `getRendererInfo()` before `init()` | Returns `{ initialized: false, canvasSize: [0, 0], webglVersion: '', vendor: 'unknown', gpuRenderer: 'unknown', maxTextureSize: 0, antialias: false }` |
| `init()` after `dispose()` | Succeeds. Creates new renderer, scene, camera. |
| `renderFrame()` before `init()` | Throws `Error`: `"depthkit: not initialized. Call init() first."` |
| `renderFrame()` with partial `cameraState` | Only provided fields are updated in order (position, lookAt, fov). Omitted fields leave camera unchanged. |
| `renderFrame()` with empty `cameraState` `{}` | No camera changes; renders current state. |
| `clearColor` not a valid hex string | Three.js `Color` constructor throws. Error propagates. |
| `fov <= 0` or `fov >= 180` in init or renderFrame | Passed through to Three.js. Produces incorrect rendering. OBJ-004 (manifest validation) catches this upstream. |
| WebGL context limit (~16 contexts) | `dispose()` calls `renderer.forceContextLoss()` then `renderer.dispose()` to fully release the context. If the limit is reached despite proper disposal, `init()` fails with WebGL context creation error. Orchestrator must call `dispose()` between videos. |
| Very large canvas (e.g., 7680x4320) | Allowed if within WebGL's `MAX_VIEWPORT_DIMS`. OBJ-010 does not impose resolution limits — OBJ-004 validates. |
| `WEBGL_debug_renderer_info` extension unavailable | `getRendererInfo()` returns `'unknown'` for `vendor` and `gpuRenderer`. |

## Test Strategy

### Puppeteer-Based Integration Tests (Primary)

Page code runs inside Chromium, so tests launch headless Chromium and interact via `page.evaluate()`. This tests the real code path.

**Initialization tests:**
1. Load page, call `init({ width: 1920, height: 1080 })`. Assert `isInitialized() === true`.
2. Assert `getRendererInfo()` returns `initialized: true`, `canvasSize: [1920, 1080]`, non-empty `webglVersion`, `maxTextureSize > 0`, `antialias: false`.
3. Assert `canvas.width === 1920`, `canvas.height === 1080`.
4. Assert `renderer.getPixelRatio() === 1`.
5. Call `init({ fov: 35, cameraPosition: [0, 2, 10] })`. Verify camera reflects custom values.
6. Call `init()` with defaults. Verify camera matches OBJ-003 `DEFAULT_CAMERA`.

**Double init / re-entrant tests:**
7. Call `init()` twice — assert Error with expected message.
8. Call `dispose()` then `init()` — assert success.

**Dispose tests:**
9. After `dispose()`, assert `isInitialized() === false`, renderer/scene/camera are null.
10. `dispose()` when not initialized — assert no error.

**renderFrame tests:**
11. After `init()`, add a colored mesh to `window.depthkit.scene` via `page.evaluate`, call `renderFrame()`, capture `canvas.toDataURL()`, verify not all-black. (Validates `preserveDrawingBuffer` and `renderFrame` together.)
12. Call `renderFrame({ position: [1, 2, 3], lookAt: [0, 0, -10], fov: 35 })`. Assert camera position is `(1, 2, 3)` and fov is `35`.
13. Call `renderFrame()` with no arguments — assert no error, render succeeds.
14. Call `renderFrame()` before `init()` — assert Error.

**Antialias tests:**
15. `init({ width: 100, height: 100, antialias: true })`. Assert `getRendererInfo().antialias === true`.
16. Default init. Assert `getRendererInfo().antialias === false`.

**Dimension rounding test:**
17. `init({ width: 1919.7, height: 1080.3 })`. Assert `canvas.width === 1920`, `canvas.height === 1080`. (Console warning verified via Puppeteer `page.on('console')` listener.)

**Error condition tests:**
18. Remove canvas from DOM before `init()` — assert Error with `#depthkit-canvas` in message.
19. `init({ width: 0, height: 1080 })` — assert Error.

### Node-Side Type Tests

20. Assert `PageInitConfig`, `RendererInfo`, `FrameCameraState` are importable from `src/engine/page-types.ts`.
21. Assert types compile without error.

### Relevant Testable Claims

- **TC-02** (render performance): OBJ-010 establishes the renderer benchmarked by TC-02. Test 11 provides the first data point on per-frame render+capture time.
- **TC-06** (deterministic output): `setPixelRatio(1)`, `preserveDrawingBuffer: true`, and `antialias: false` are prerequisites for deterministic frame capture.
- **TC-11** (Docker/software WebGL): `getRendererInfo().gpuRenderer` reports whether SwiftShader is in use.

## Integration Points

### Depends on

| Dependency | What OBJ-010 uses |
|---|---|
| **OBJ-001** (Project scaffolding) | Directory structure, esbuild build pipeline, `src/page/` stub files, Three.js dependency. OBJ-010 evolves the stubs into real implementations. |
| **OBJ-003** (Spatial math) | `DEFAULT_CAMERA` constants (fov, near, far, position, lookAt) for camera initialization defaults. `Vec3` type for `PageInitConfig`. Import is Node-side only (`src/engine/page-types.ts` imports from `src/spatial/types.js`). The page JS does NOT import OBJ-003 — it receives values as plain arrays. The default values (fov: 50, near: 0.1, far: 100, position: [0,0,5], lookAt: [0,0,0]) are hardcoded in the page JS to match OBJ-003's `DEFAULT_CAMERA`, documented as "must match OBJ-003 DEFAULT_CAMERA." |

### Consumed by

| Downstream | How it uses OBJ-010 |
|---|---|
| **OBJ-011** (Message protocol) | Builds on `window.depthkit` API. Defines frame commands that call `renderFrame()`. Defines `SerializedGeometry` types (combining OBJ-010's renderer contract with OBJ-005's geometry types). Uses `PageInitConfig`, `RendererInfo`, `FrameCameraState` from `page-types.ts`. |
| **OBJ-015** (Texture loader) | Runs inside the browser page. Uses `window.depthkit.scene` to add loaded textures as mesh materials. Depends on the renderer being initialized. |
| **OBJ-009** (Puppeteer bridge) | Must set Puppeteer viewport dimensions to match `PageInitConfig.width` and `PageInitConfig.height` before loading the page. If viewport and canvas dimensions mismatch, captured frames will be incorrectly sized or cropped. |
| **OBJ-039** (Audio sync) | Uses composition timing from the orchestrator path that OBJ-010's architecture enables. |
| **OBJ-042, OBJ-043, OBJ-044** (Spatial objectives) | Use the page shell for visual verification. Call `renderFrame()` to test geometry rendering. |
| **OBJ-081, OBJ-082** (Low-priority extensions) | Build on the renderer skeleton. |

### File Placement

```
depthkit/
  src/
    engine/
      page-types.ts           # NEW — PageInitConfig, RendererInfo, FrameCameraState
    page/
      index.html              # EVOLVE from OBJ-001 stub — final HTML shell
      scene-renderer.js       # EVOLVE from OBJ-001 stub — Three.js init, window.depthkit API
      geometry-library.js     # EVOLVE stub — documented contract for geometry materialization
      message-handler.js      # EVOLVE stub — documented contract for message handling
```

## Open Questions

### OQ-A: Should `renderFrame()` return timing data?

A `renderFrame()` call could return `{ renderTimeMs: number }` — the time spent in `renderer.render()`. This would give the orchestrator per-frame performance data for TC-02 benchmarking. **Recommendation:** Defer. The orchestrator can measure round-trip time from `page.evaluate()`. Adding return data adds complexity for marginal benefit.

### OQ-B: Should the page support `renderer.autoClear` toggling?

Transition rendering (OBJ-008) may need multi-pass rendering to the same canvas (render outgoing scene, then incoming scene without clearing). This requires `renderer.autoClear = false` for the second pass. OBJ-010 leaves `autoClear` at its Three.js default (`true`). Downstream objectives can toggle it via `window.depthkit.renderer.autoClear = false` from `page.evaluate()`. **No action needed in OBJ-010** — the renderer property is exposed and mutable.
