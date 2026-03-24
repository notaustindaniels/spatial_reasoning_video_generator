# Deliberation Transcript: OBJ-010

---

## Round 1 — spec_author

Looking at OBJ-010's scope, dependencies, and what it blocks, let me first check the current state of the codebase and any existing work.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-010/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json

[Tool: Glob]
  Input: {
  "pattern": "depthkit/src/**/*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-009/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-009",
     3→  "description": "Virtualized clock -- global frame-to-timestamp mapping (t = frame / fps), frame counter mechanics, deterministic frame stepping guarantee per C-03. Pure utility with no scene awareness. The clock provides the global frame number and timestamp; per-scene normalized time computation is handled by the scene sequencer (OBJ-036). Ensures zero dropped frames regardless of scene complexity or hardware speed.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Narrowed to pure global clock -- per-scene time normalization moved to OBJ-036."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-010",
     3→  "description": "Three.js page shell, build/bundle strategy, and scene renderer skeleton -- HTML shell (src/page/index.html), page-side module loading strategy (CDN vs bundled Three.js, ESM vs build step via esbuild/vite), mechanism for making TypeScript geometry definitions available to the browser page, Three.js Scene/PerspectiveCamera/WebGLRenderer initialization, and WebGL canvas setup. This is the authoritative decision point for the Node.js/browser code-split architecture.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001", "OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Expanded to cover build/bundle strategy per Round 2 Issue 5."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-011/meta.json"
}

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-015/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-015/meta.json

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

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-005",
     3→  "description": "Scene geometry type contract -- TypeScript interfaces for SceneGeometry and PlaneSlot per Section 8.6. PlaneSlot defines position [x,y,z], rotation [rx,ry,rz], size [w,h], required flag, and description. SceneGeometry defines name, slots record, compatible_cameras list, default_camera, and optional fog config. Establishes slot naming conventions and required-vs-optional plane semantics.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Defines the type system for all 8 scene geometry implementations."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-006/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-006",
     3→  "description": "Camera path type contract -- TypeScript interface for camera path presets. Defines position(t) and lookAt(t) as functions of normalized time t in [0,1], start/end position and lookAt vectors, FOV animation range (fov_start, fov_end), easing defaults, compatible_geometries list, and oversizing requirements metadata. Per Section 4.3.",
     4→  "category": "spatial",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-002", "OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 1 contract. Depends on interpolation utilities (OBJ-002) for easing references and coordinate system (OBJ-003) for spatial conventions."
    12→}
    13→

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-005/output.md"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-006/output.md"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-007/output.md"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-002/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-002/output.md"
}
[Tool Result]      1→# Specification: OBJ-002 — Interpolation, Easing, and Spring Utilities
     2→
     3→## Summary
     4→
     5→OBJ-002 defines the math primitives that underpin all animation in depthkit: an `interpolate()` function for mapping frame numbers to output values, a `spring()` function for organic/physics-based motion, and six named easing functions. These utilities are isomorphic — they must run identically in both the Node.js orchestrator (scene sequencer transition timing) and the headless Chromium browser (Three.js camera interpolation). This is a Tier 0 foundation with no dependencies; every camera path preset, scene transition, and FOV animation consumes these primitives.
     6→
     7→## Interface Contract
     8→
     9→### Module: `src/interpolation/easings.ts`
    10→
    11→```typescript
    12→/**
    13→ * An easing function maps normalized time t in [0,1] to eased time t' in [0,1].
    14→ * Behavior outside [0,1] is undefined (see design notes).
    15→ */
    16→exp... [truncated]
Now I have a clear picture of the dependencies and downstream consumers. Let me propose the full specification for OBJ-010.

---

# Specification Proposal: OBJ-010 — Three.js Page Shell, Build/Bundle Architecture, and Scene Renderer Skeleton

## Summary

OBJ-010 establishes the browser-side rendering foundation and the authoritative Node.js/browser code-split architecture for depthkit. It delivers three things: (1) the final HTML page shell with a properly sized WebGL canvas, (2) the Three.js `Scene` / `PerspectiveCamera` / `WebGLRenderer` initialization skeleton that all downstream rendering depends on, and (3) the architectural decision for how data flows from Node.js to the headless Chromium page — specifically, that geometry definitions are **not** duplicated on the browser side but instead serialized as plain data and passed at runtime via Puppeteer. The page is a "data-driven renderer" that receives scene descriptions as JSON-serializable objects, materializes them into Three.js scene graphs, and renders frames on command. This objective also defines the page-side API surface that OBJ-011 (message protocol) and OBJ-015 (texture loader) will build upon.

## Interface Contract

### Module: `src/page/scene-renderer.js`

This is the esbuild entry point (per OBJ-001). It initializes Three.js, exposes a global `depthkit` namespace on `window`, and imports the other page modules. After OBJ-010, this file contains the renderer skeleton — downstream objectives populate the scene management and frame rendering logic.

```typescript
// Conceptual contract for window.depthkit (exposed as globals on the page)
// These are NOT TypeScript files — they are plain JS running in Chromium.
// Types here document the contract; implementation is JS.

interface DepthkitPage {
  /**
   * Initializes the Three.js renderer, camera, and scene.
   * Called once when the page is first set up by the orchestrator.
   *
   * @param config - Composition-level settings.
   * @returns void. Throws if WebGL context cannot be created.
   */
  init(config: PageInitConfig): void;

  /**
   * Returns true if init() has been called successfully.
   */
  isInitialized(): boolean;

  /**
   * Returns renderer diagnostic info for the orchestrator to log.
   * Includes WebGL capabilities, renderer type (hardware/software), canvas size.
   */
  getRendererInfo(): RendererInfo;

  /**
   * Disposes of all Three.js resources (renderer, textures, geometries, materials).
   * Called once at the end of the render pipeline.
   * After dispose(), init() must be callable again (re-entrant).
   */
  dispose(): void;

  /**
   * The Three.js WebGLRenderer instance. Exposed for OBJ-011 (message protocol)
   * and OBJ-015 (texture loader) to access directly.
   * null before init() is called.
   */
  renderer: THREE.WebGLRenderer | null;

  /**
   * The Three.js Scene instance. The "current" active scene.
   * Downstream objectives (OBJ-015, scene setup commands from OBJ-011)
   * add meshes to this scene.
   * null before init() is called.
   */
  scene: THREE.Scene | null;

  /**
   * The Three.js PerspectiveCamera instance.
   * Camera path presets (consumed via OBJ-011 frame commands) update
   * this camera's position, lookAt, and fov each frame.
   * null before init() is called.
   */
  camera: THREE.PerspectiveCamera | null;
}

interface PageInitConfig {
  /** Canvas width in pixels. */
  width: number;
  /** Canvas height in pixels. */
  height: number;
  /** Background clear color as CSS hex string (e.g., '#000000'). Default: '#000000'. */
  clearColor?: string;
  /** Background clear alpha (0-1). Default: 1. */
  clearAlpha?: number;
  /** Initial camera FOV in degrees. Default: 50. */
  fov?: number;
  /** Camera near plane. Default: 0.1. */
  near?: number;
  /** Camera far plane. Default: 100. */
  far?: number;
  /** Initial camera position [x, y, z]. Default: [0, 0, 5]. */
  cameraPosition?: [number, number, number];
  /** Initial camera lookAt target [x, y, z]. Default: [0, 0, 0]. */
  cameraLookAt?: [number, number, number];
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
  /** WebGL version string (e.g., 'WebGL 2.0'). */
  webglVersion: string;
  /** GPU vendor string from WebGL debug info, or 'unknown'. */
  vendor: string;
  /** GPU renderer string from WebGL debug info (e.g., 'SwiftShader'), or 'unknown'. */
  gpuRenderer: string;
  /** Max texture size supported by the WebGL context. */
  maxTextureSize: number;
}
```

### Module: `src/page/geometry-library.js`

After OBJ-010, this file contains a **stub with a documented contract**. The actual geometry materialization logic is populated by OBJ-005 (geometry type contract) and individual geometry objectives (OBJ-018–025). OBJ-010 establishes that geometry data arrives as plain serializable objects (not code), and this module will contain the function that turns that data into Three.js meshes.

```typescript
// Conceptual contract — populated by OBJ-005+
interface GeometryMaterializer {
  /**
   * Creates Three.js meshes from a serialized geometry description.
   * Called by scene setup commands (OBJ-011).
   *
   * @param geometryData - Plain object describing slots, positions, rotations, sizes.
   * @param textures - Map of slot name to loaded THREE.Texture.
   * @param scene - The THREE.Scene to add meshes to.
   */
  materializeGeometry(
    geometryData: SerializedGeometry,
    textures: Record<string, THREE.Texture>,
    scene: THREE.Scene
  ): void;
}

/** The serialized form of a SceneGeometry that crosses the Node/browser boundary. */
interface SerializedGeometry {
  name: string;
  slots: Record<string, {
    position: [number, number, number];
    rotation: [number, number, number];
    size: [number, number];
  }>;
  fog?: { color: string; near: number; far: number };
}
```

### Module: `src/page/message-handler.js`

After OBJ-010, this file contains a **stub**. OBJ-011 (message protocol) defines the full message handling. OBJ-010 establishes the pattern: the message handler listens for commands dispatched via `page.evaluate()` and calls into the `window.depthkit` API.

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

### Node-Side Type: `src/engine/page-types.ts`

Shared TypeScript types for the data structures that cross the Node/browser boundary. These types live on the Node side only — the browser receives plain objects. Downstream objectives (OBJ-011 for the full protocol, OBJ-009 for Puppeteer bridge) import these types.

```typescript
// src/engine/page-types.ts

import type { Vec3 } from '../spatial/types';

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
}

/**
 * Serialized geometry data that crosses the Node/browser boundary.
 * This is the plain-object representation of a SceneGeometry (OBJ-005).
 * The Node side resolves geometry names to these objects; the browser
 * materializes them into Three.js meshes.
 */
export interface SerializedGeometrySlot {
  position: [number, number, number];
  rotation: [number, number, number];
  size: [number, number];
}

export interface SerializedGeometry {
  name: string;
  slots: Record<string, SerializedGeometrySlot>;
  fog?: { color: string; near: number; far: number };
}
```

## Design Decisions

### D1: Data-Driven Renderer (Dumb Page / Smart Orchestrator)

**Decision:** The browser page is a **generic, data-driven Three.js renderer**. It does NOT contain geometry definitions, camera path logic, or scene sequencing intelligence. Instead:

- **Node.js side** holds all domain logic: manifest parsing, geometry definitions (OBJ-005), camera path presets (OBJ-006), scene sequencing (OBJ-015), and the virtualized clock (OBJ-009).
- **Browser side** receives serialized plain-object descriptions of what to render and executes Three.js API calls accordingly.
- Geometry data (slot positions, rotations, sizes) is serialized as JSON-compatible objects on the Node side and passed to the page via `page.evaluate()` during scene setup.

**Alternatives considered:**

1. **Smart Page** (seed Section 8.5 sketch) — Camera interpolation, easing, and scene timing all run inside the browser. The orchestrator sends only frame numbers. This requires bundling the interpolation module, camera path presets, and scene sequencer logic into the page, creating a large browser bundle and duplicating domain logic across the boundary.

2. **Hybrid** — Camera interpolation in the browser, everything else on Node. Reduces per-frame data transfer but still requires bundling interpolation + camera presets into the page.

3. **Dumb Page** (chosen) — The orchestrator computes the complete scene state for each frame (camera position, lookAt, FOV, plane states if animated) and sends it to the page. The page simply applies the values and calls `renderer.render()`.

**Rationale for Dumb Page:**

- **Single source of truth.** Geometry definitions, camera paths, and timing logic exist in exactly one place (Node.js TypeScript). No risk of drift between Node validation logic and browser rendering logic.
- **Simpler browser bundle.** The page bundle contains only Three.js + a thin rendering shell. No need to bundle `src/interpolation/`, `src/spatial/`, camera presets, or scene sequencing.
- **Easier debugging.** The orchestrator can log the exact camera state it sends per frame. If a frame looks wrong, the state is inspectable on the Node side without browser DevTools.
- **Per-frame data is small.** A frame command is ~200 bytes of JSON (camera position, lookAt, FOV, maybe opacity). At 30fps, that's 6KB/s — negligible for an in-process Puppeteer connection.
- **Aligns with C-03 (virtualized clock).** The clock lives entirely on the Node side. The page never computes time — it renders what it's told. This is the purest expression of "the page never advances time on its own."

**Impact on OBJ-002 (interpolation):** The interpolation module does NOT need to be isomorphic. It runs only on the Node side. OBJ-002's spec notes it should be bundleable for the browser — this is still possible if a future objective needs it, but OBJ-010 does not require it.

**Impact on OBJ-011 (message protocol):** Frame commands include computed camera state (position, lookAt, FOV), not just frame numbers. OBJ-011 designs the protocol accordingly.

### D2: Canvas is sized by JavaScript, not CSS

**Decision:** The `<canvas>` element in `index.html` has no explicit `width`/`height` attributes. The Three.js `WebGLRenderer` calls `renderer.setSize(width, height)` during `init()`, which sets the canvas's intrinsic pixel dimensions and its CSS display size. Puppeteer's viewport is set to match.

**Rationale:** Three.js's `setSize()` is the canonical way to control canvas resolution. Setting dimensions in HTML or CSS and then trying to match them in Three.js leads to DPI/scaling bugs. Letting the renderer own the size ensures the canvas, the WebGL framebuffer, and the Puppeteer viewport are all consistent.

**Note on `setPixelRatio`:** The renderer must call `renderer.setPixelRatio(1)` explicitly. Chromium may report a devicePixelRatio > 1 even in headless mode. We want exactly 1:1 pixel mapping — a 1920×1080 canvas must produce a 1920×1080 frame buffer. No HiDPI scaling.

### D3: `preserveDrawingBuffer: true` as default

**Decision:** The `WebGLRenderer` is created with `preserveDrawingBuffer: true`.

**Rationale:** Without this flag, the WebGL canvas contents may be cleared after compositing, making `canvas.toDataURL()` or `canvas.toBlob()` return blank images. While `Page.captureScreenshot` (CDP) captures the composited page and doesn't need this flag, `toDataURL()` is a common fallback capture method and the flag has negligible performance impact. Safer to enable by default.

### D4: Single Scene Instance, Cleared Between Scenes

**Decision:** The page maintains one `THREE.Scene` instance. When transitioning between scenes, the current scene's children are disposed and removed, and new geometry is added. For transition overlaps (crossfade), a second temporary `THREE.Scene` is created for the incoming scene; both are rendered in sequence to the same canvas with opacity compositing.

**Rationale:** Three.js scenes are lightweight — creating a new one for transitions is cheaper than trying to swap scene graphs. The renderer renders to the same canvas in both passes. Transition compositing (opacity blending of two scenes) is handled by rendering the outgoing scene, then rendering the incoming scene with `renderer.autoClear = false` and material opacity adjustments.

**Note:** Transition rendering details are OBJ-015's (scene sequencer) and OBJ-008's (transition system) responsibility. OBJ-010 ensures the renderer supports multi-pass rendering (`renderer.autoClear` can be toggled).

### D5: Confirm OBJ-001's esbuild IIFE Strategy

**Decision:** OBJ-001's build strategy is confirmed without modification. `src/page/scene-renderer.js` is the single esbuild entry point, bundled as IIFE with Three.js inlined. No additional build-time complexity (no TypeScript for page files, no shared-module bundling).

**Rationale:** The Dumb Page architecture (D1) means the page bundle is simple — Three.js + a rendering shell. No domain logic needs to cross the build boundary. If a future objective needs to share code between Node and browser, it can introduce a `tsconfig.browser.json` as OBJ-001 noted, but OBJ-010 does not require it.

### D6: `window.depthkit` Global Namespace

**Decision:** The page exposes its API as `window.depthkit` — a single global object with methods (`init`, `dispose`, `getRendererInfo`, `isInitialized`) and accessors (`renderer`, `scene`, `camera`). Puppeteer interacts with the page exclusively through this namespace via `page.evaluate()`.

**Rationale:** IIFE bundles don't produce ES module exports. A global namespace is the standard pattern for script-tag-loaded libraries in Chromium. A single namespace keeps the API discoverable and prevents pollution. Puppeteer's `page.evaluate('window.depthkit.init(...)')` is clean and debuggable.

### D7: `meshBasicMaterial` as Default (Unlit Rendering)

**Decision:** OBJ-010 initializes the scene without lights. The geometry materializer (downstream) will use `THREE.MeshBasicMaterial` by default — textures display at full brightness. No `AmbientLight` or `DirectionalLight` is added by the renderer skeleton.

**Rationale:** Seed Section 4.2 and OQ-09 explicitly defer the lighting decision. `MeshBasicMaterial` is the simplest correct choice for V1 — images display as-authored without lighting artifacts. If a downstream objective (OQ-09) adds lighting, it adds lights to the scene and switches materials. The renderer skeleton doesn't prevent this.

### D8: WebGL 2 Preferred, WebGL 1 Fallback Acceptable

**Decision:** The `WebGLRenderer` is created without forcing a specific WebGL version. Three.js defaults to WebGL 2 when available, falling back to WebGL 1. The `getRendererInfo()` function reports which version was acquired.

**Rationale:** SwiftShader (software renderer in headless Chromium, per C-11) supports WebGL 2. Hardware GPUs support WebGL 2. There's no reason to force WebGL 1, and no features in the V1 renderer skeleton that require WebGL 2. Let Three.js negotiate.

## Acceptance Criteria

- [ ] **AC-01:** `src/page/index.html` is a valid HTML5 document containing a `<canvas id="depthkit-canvas">` element and a `<script src="scene-renderer.js">` tag. CSS resets margin/padding to 0, hides overflow, and sets a black background.

- [ ] **AC-02:** `src/page/scene-renderer.js` imports Three.js (`import * as THREE from 'three'`), creates a `WebGLRenderer` bound to the `#depthkit-canvas` element during `init()`, and exposes the `window.depthkit` namespace with `init`, `dispose`, `isInitialized`, and `getRendererInfo` methods.

- [ ] **AC-03:** After calling `window.depthkit.init({ width: 1920, height: 1080 })`, `window.depthkit.isInitialized()` returns `true`, and `window.depthkit.renderer` is a non-null `THREE.WebGLRenderer` instance.

- [ ] **AC-04:** After `init({ width: 1920, height: 1080 })`, the canvas element's intrinsic dimensions (`canvas.width`, `canvas.height`) are exactly 1920 and 1080. The renderer's pixel ratio is 1 (verified via `renderer.getPixelRatio() === 1`).

- [ ] **AC-05:** After `init({ width: 1920, height: 1080, fov: 50 })`, `window.depthkit.camera` is a `THREE.PerspectiveCamera` with `fov === 50`, `aspect` approximately equal to `1920/1080`, `near === 0.1`, `far === 100`, and position `[0, 0, 5]`.

- [ ] **AC-06:** `window.depthkit.getRendererInfo()` returns an object with `initialized: true`, `canvasSize: [1920, 1080]`, a non-empty `webglVersion` string, and a numeric `maxTextureSize` > 0.

- [ ] **AC-07:** Calling `window.depthkit.dispose()` sets `renderer`, `scene`, and `camera` to null, and calling `isInitialized()` returns `false`. After dispose, calling `init()` again succeeds (re-entrant lifecycle).

- [ ] **AC-08:** The `WebGLRenderer` is created with `preserveDrawingBuffer: true`. Verified by: after rendering a non-black scene, `canvas.toDataURL()` returns a data URL that is NOT an all-black image.

- [ ] **AC-09:** The renderer sets `renderer.setPixelRatio(1)` regardless of `window.devicePixelRatio`. Verified by: even if Chromium reports `devicePixelRatio: 2`, the canvas still has intrinsic dimensions equal to the requested width/height (not doubled).

- [ ] **AC-10:** When `init()` is called with default parameters (no `fov`, `near`, `far`, `cameraPosition`, `cameraLookAt`), the camera uses the defaults from OBJ-003's `DEFAULT_CAMERA`: `fov: 50`, `near: 0.1`, `far: 100`, position `[0, 0, 5]`, lookAt `[0, 0, 0]`.

- [ ] **AC-11:** `src/engine/page-types.ts` exports `PageInitConfig`, `RendererInfo`, `SerializedGeometry`, and `SerializedGeometrySlot` types. All types are JSON-serializable (no functions, no class instances, no `THREE.*` types).

- [ ] **AC-12:** `npm run build` succeeds and produces `dist/page/scene-renderer.js` (bundled IIFE with Three.js) and `dist/page/index.html`. The bundle size is >500KB (Three.js included).

- [ ] **AC-13:** `window.depthkit.scene` is a `THREE.Scene` after `init()`. The scene has a black background (matching `clearColor` default).

- [ ] **AC-14:** Calling `init()` twice without an intervening `dispose()` throws an Error with a message indicating the renderer is already initialized.

- [ ] **AC-15:** If the `<canvas>` element is not found in the DOM, `init()` throws an Error with a message naming the expected element ID (`depthkit-canvas`).

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `init()` called with no canvas in DOM | Throws `Error`: `"depthkit: canvas element '#depthkit-canvas' not found"` |
| `init()` called twice without `dispose()` | Throws `Error`: `"depthkit: already initialized. Call dispose() first."` |
| `init()` with `width <= 0` or `height <= 0` | Throws `Error`: `"depthkit: width and height must be positive integers"` |
| `init()` with non-integer width/height | Floors to integer (canvas dimensions must be integers). No throw. |
| WebGL context creation fails (no GPU, no SwiftShader) | Throws `Error`: `"depthkit: WebGL context creation failed. Ensure headless Chromium has WebGL support (SwiftShader or GPU)."` Three.js fires a `webglcontextcreationerror` event on the canvas — the renderer skeleton listens for this. |
| `dispose()` called when not initialized | No-op. No throw. Idempotent. |
| `getRendererInfo()` called before `init()` | Returns `{ initialized: false, canvasSize: [0, 0], webglVersion: '', vendor: 'unknown', gpuRenderer: 'unknown', maxTextureSize: 0 }`. |
| `init()` after `dispose()` (re-initialization) | Succeeds. Creates new renderer, scene, camera. Re-entrant lifecycle. |
| Very large canvas dimensions (e.g., 7680×4320) | Allowed if within WebGL's `MAX_VIEWPORT_DIMS`. The renderer skeleton does not impose resolution limits — that's OBJ-004 (manifest validation) responsibility. |
| `clearColor` is not a valid hex string | Three.js `Color` constructor throws. OBJ-010 does not add additional validation — Three.js error propagates. |
| `fov <= 0` or `fov >= 180` | Allowed by Three.js (it doesn't validate FOV). Produces incorrect rendering. OBJ-004 (manifest validation) should catch this. OBJ-010 passes values through. |

## Test Strategy

### Unit Tests for Page Logic

Since the page code runs inside Chromium, unit tests require a browser-like environment. Two approaches:

1. **Puppeteer-based integration tests** (recommended for V1): Launch headless Chromium, load the page, call `page.evaluate('window.depthkit.init(...)')`, and assert on return values. This tests the real code path.

2. **jsdom-based unit tests** (limited): jsdom doesn't support WebGL. Can only test non-rendering logic (e.g., error handling for missing canvas). Not recommended as primary strategy.

**Test scenarios:**

**Initialization tests (via Puppeteer):**
1. Load page, call `init({ width: 1920, height: 1080 })`. Verify `isInitialized() === true`.
2. Verify `getRendererInfo()` returns expected structure with `initialized: true`, correct `canvasSize`.
3. Verify canvas intrinsic dimensions match requested width/height.
4. Verify pixel ratio is 1.
5. Verify camera defaults match OBJ-003's `DEFAULT_CAMERA`.
6. Call `init()` with custom `fov: 35`, `cameraPosition: [0, 2, 10]`. Verify camera reflects custom values.
7. Call `init()` twice — verify Error thrown.
8. Call `dispose()` then `init()` — verify success (re-entrant).

**Dispose tests:**
9. After `dispose()`, verify `isInitialized() === false`, renderer/scene/camera are null.
10. `dispose()` when not initialized — verify no error.

**Frame capture smoke test:**
11. After `init()`, render a simple colored scene (add a mesh programmatically via `page.evaluate`), call `canvas.toDataURL()`, verify the result is not all-black (validates `preserveDrawingBuffer`).

**Error condition tests:**
12. Remove canvas from DOM before `init()` — verify error.
13. `init({ width: 0, height: 1080 })` — verify error.

### Node-Side Type Tests

14. Verify `PageInitConfig`, `RendererInfo`, `SerializedGeometry` are importable from `src/engine/page-types.ts`.
15. Verify types compile without error and are JSON-serializable (no function or class types).

### Relevant Testable Claims

- **TC-02** (render performance): OBJ-010 establishes the renderer that TC-02 benchmarks. The smoke test (test 11) provides the first data point on per-frame render+capture time.
- **TC-06** (deterministic output): The renderer skeleton with `setPixelRatio(1)` and `preserveDrawingBuffer: true` are prerequisites for deterministic frame capture.
- **TC-11** (Docker/software WebGL): The `getRendererInfo()` function reports whether SwiftShader is in use, enabling TC-11 verification.

## Integration Points

### Depends on

| Dependency | What OBJ-010 uses |
|---|---|
| **OBJ-001** (Project scaffolding) | Directory structure, esbuild build pipeline, `src/page/` stub files, Three.js dependency. OBJ-010 evolves the stubs into real implementations. |
| **OBJ-003** (Spatial math) | `DEFAULT_CAMERA` constants (fov, near, far, position, lookAt) for camera initialization defaults. `Vec3` type for `PageInitConfig`. The import is Node-side only (`src/engine/page-types.ts` imports from `src/spatial/types`). The page JS does NOT import OBJ-003 — it receives values as plain arrays. |

### Consumed by

| Downstream | How it uses OBJ-010 |
|---|---|
| **OBJ-011** (Message protocol) | Builds on `window.depthkit` API. Defines frame commands that call into the renderer. Uses `PageInitConfig`, `RendererInfo`, `SerializedGeometry` types from `page-types.ts`. |
| **OBJ-015** (Texture loader) | Runs inside the browser page. Uses `window.depthkit.scene` to add loaded textures as mesh materials. Depends on the renderer being initialized. |
| **OBJ-039** (Audio sync) | Uses composition timing from the same frame-clock/orchestrator path that OBJ-010's architecture enables. |
| **OBJ-042, OBJ-043, OBJ-044** (Spatial objectives) | Depend on the renderer being able to display geometry. Use the page shell for visual verification. |
| **OBJ-081, OBJ-082** (Low-priority extensions) | Build on the renderer skeleton. |

### File Placement

```
depthkit/
  src/
    engine/
      page-types.ts           # NEW — PageInitConfig, RendererInfo, SerializedGeometry,
                               #        SerializedGeometrySlot types (Node-side only)
    page/
      index.html              # EVOLVE from OBJ-001 stub — final HTML shell
      scene-renderer.js       # EVOLVE from OBJ-001 stub — Three.js init, window.depthkit API
      geometry-library.js     # EVOLVE stub — documented contract for geometry materialization
      message-handler.js      # EVOLVE stub — documented contract for frame command handling
```

## Open Questions

### OQ-A: Should `init()` accept a `Puppeteer.Page` reference for tighter integration?

No. The page code has no knowledge of Puppeteer. Communication is exclusively via `page.evaluate()` from the Node side. The page exposes a vanilla JavaScript API.

### OQ-B: Should the renderer support `antialias`?

Three.js `WebGLRenderer` accepts an `antialias` option. For V1, defaulting to `antialias: true` improves visual quality at minimal performance cost. However, antialiasing may introduce sub-pixel differences across hardware, potentially affecting C-05 (deterministic output). **Recommendation:** Default `antialias: false` for determinism. Add as an optional `PageInitConfig` field if downstream visual tuning objectives request it.

### OQ-C: Should there be a `renderFrame()` method on `window.depthkit` in this objective?

OBJ-010 initializes the renderer but does NOT define the per-frame render call. That belongs to OBJ-011 (message protocol), which defines how the orchestrator triggers a render and what camera/scene state is sent per frame. OBJ-010 provides the `renderer`, `scene`, and `camera` objects that OBJ-011's `renderFrame` will use. If the challenger believes a minimal `renderFrame` stub should live here, I'm open to adding it.

### OQ-D: Transition multi-pass rendering

D4 notes that transitions may require rendering two scenes to the same canvas in sequence. The `renderer.autoClear` property controls whether the canvas is cleared between renders. OBJ-010 leaves `autoClear` at its Three.js default (`true`). OBJ-008 (transition system) will toggle it during transition frames. OBJ-010 does not need to anticipate this — it just needs to not prevent it.

---

I believe this covers the full scope of OBJ-010: the authoritative code-split decision (D1 — Dumb Page), the HTML shell, Three.js initialization, the `window.depthkit` API contract, Node-side types for cross-boundary data, and clear handoff points to downstream objectives. I'd like the challenger to evaluate whether:

1. The Dumb Page vs. Smart Page decision (D1) is well-justified given the seed's sketches that show interpolation happening browser-side.
2. The scope boundary with OBJ-011 (no `renderFrame` here) is appropriate.
3. The `page-types.ts` placement and the `SerializedGeometry` contract are sufficient for downstream objectives.

---

## Round 2 — spec_challenger

I've read the proposal carefully. It's a solid first draft with the right instincts — the Dumb Page architecture is well-reasoned, and the scope boundaries are mostly correct. But I have several issues that need resolution before this is implementable.

---

## Points of Agreement

1. **D1 (Dumb Page / Smart Orchestrator)** — Strong agree. The seed's Section 4.4 sketches show interpolation browser-side, but those are "hunches, not mandates" (Section 4 preamble). Single source of truth on the Node side is cleaner and aligns perfectly with C-03. The justification is thorough.

2. **D2 (Canvas sized by JS)** — Correct. `renderer.setSize()` is the right approach.

3. **D3 (`preserveDrawingBuffer: true`)** — Correct for correctness, and the rationale is sound.

4. **D6 (`window.depthkit` namespace)** — Clean pattern for IIFE bundles.

5. **D7 (unlit rendering)** — Correct deferral per OQ-09.

6. **The `page-types.ts` approach** — Good idea to have Node-side types for cross-boundary data.

---

## Issues

### Issue 1: `antialias` Default — Contradicts Determinism Goal (Major)

OQ-B recommends `antialias: false` for determinism but doesn't commit. This is a design decision, not an open question — C-05 (deterministic output) is a non-negotiable constraint, and antialiasing is implementation-defined across GPU/SwiftShader. 

**Fix:** Move this from OQ-B to a Design Decision. State: `antialias: false` is the default. Add it to `PageInitConfig` as an optional boolean (`antialias?: boolean`, default `false`). Add AC verifying the default.

### Issue 2: Missing `renderFrame` Stub Creates an Awkward Gap (Major)

The spec says OBJ-011 defines how frames are rendered, but OBJ-010 blocks OBJ-011 and also blocks OBJ-015, OBJ-039, OBJ-042, OBJ-043, OBJ-044, OBJ-081, OBJ-082. Several of those consumers (OBJ-015 texture loader, OBJ-042/043/044 spatial objectives) will need to *see something rendered* to verify their work. Without even a minimal `renderFrame()` on `window.depthkit`, OBJ-010's own AC-08 ("render a non-black scene and capture via toDataURL") can't be tested — who calls `renderer.render(scene, camera)`?

The spec's test #11 says "add a mesh programmatically via `page.evaluate`" and then capture — but that requires calling `renderer.render()` somewhere. Is the test supposed to inline that call? That works for a test but leaves no contract for downstream consumers.

**Fix:** Add a minimal `renderFrame()` method to `window.depthkit`:

```typescript
/**
 * Renders the current scene with the current camera to the canvas.
 * This is the primitive render call. OBJ-011's message protocol
 * will call this after setting camera state per frame.
 *
 * @param cameraState - Optional. If provided, updates camera before rendering.
 */
renderFrame(cameraState?: {
  position?: [number, number, number];
  lookAt?: [number, number, number];
  fov?: number;
}): void;
```

This gives OBJ-010 a self-contained testable contract and gives downstream objectives a primitive to build on. OBJ-011 wraps this in its message protocol; it doesn't reinvent the render call.

### Issue 3: `scene.background` vs `renderer.setClearColor` Ambiguity (Minor)

AC-13 says "The scene has a black background (matching `clearColor` default)." But the spec uses both `clearColor`/`clearAlpha` in `PageInitConfig` (which maps to `renderer.setClearColor()`) and doesn't mention `scene.background`. These are different things in Three.js:

- `renderer.setClearColor()` — the color the canvas is cleared to before rendering.
- `scene.background` — a Three.js `Color` or texture that fills the scene background.

If both are unset, the result is black. But if someone sets `clearColor: '#ff0000'` expecting a red background, they'll get it — unless `scene.background` is set to something else.

**Fix:** Clarify: `init()` calls `renderer.setClearColor(clearColor, clearAlpha)`. `scene.background` is left as `null` (Three.js default). The clear color is the background. Add a one-line note in the `PageInitConfig` docs: "The clear color serves as the scene background. `scene.background` is not set by default."

### Issue 4: `SerializedGeometry` May Be Premature / Scope Bleed (Major)

`SerializedGeometry` and `SerializedGeometrySlot` in `page-types.ts` are defining a contract for how geometry data crosses the Node/browser boundary. But this contract depends on OBJ-005 (scene geometry type contract), which is listed as a *sibling* in progress (both in_progress), not a dependency of OBJ-010. OBJ-010 depends on OBJ-001 and OBJ-003 only.

The `SerializedGeometry` type is essentially a simplified version of OBJ-005's `SceneGeometry` interface. If OBJ-005's final spec changes the slot structure (e.g., adds `required`, `description`, `material` properties), `SerializedGeometry` must be updated. OBJ-010 is defining a type it doesn't own.

**Fix:** Remove `SerializedGeometry` and `SerializedGeometrySlot` from OBJ-010's deliverables. Keep `PageInitConfig` and `RendererInfo` in `page-types.ts` — those are genuinely owned by OBJ-010. Add a note in the spec that OBJ-011 (which depends on both OBJ-010 and OBJ-005) will define the serialized geometry types once OBJ-005's contract is finalized. The `geometry-library.js` stub can note this dependency without defining the contract.

### Issue 5: `dispose()` Doesn't Specify WebGL Context Loss Handling (Minor)

`dispose()` sets renderer/scene/camera to null. But `renderer.dispose()` in Three.js also releases the WebGL context. If `init()` is called again after `dispose()`, it needs to create a new `WebGLRenderer` — which creates a new WebGL context on the same canvas. Chromium has a limit on WebGL contexts (typically 16). In a long-running test suite or a multi-video pipeline, hitting this limit would cause silent failures.

**Fix:** Add to Edge Cases: "WebGL context limit: Chromium supports a limited number of simultaneous WebGL contexts (~16). `dispose()` releases the context via `renderer.dispose()`. If the context limit is reached, `init()` will fail with the WebGL context creation error. For multi-video rendering, the orchestrator must call `dispose()` between videos. The orchestrator should also call `renderer.forceContextLoss()` before `renderer.dispose()` to ensure the context is fully released." Add a note to `dispose()` contract that it calls `renderer.forceContextLoss()` then `renderer.dispose()`.

### Issue 6: D4 (Single Scene, Second for Transitions) — Contradicts Seed Section 8.8 (Major)

D4 says "For transition overlaps, a second temporary `THREE.Scene` is created for the incoming scene." But then it says "OBJ-010 leaves `autoClear` at its Three.js default (`true`). OBJ-008 (transition system) will toggle it during transition frames."

The problem: the spec is making architectural commitments about transition rendering (two scenes, opacity compositing, `autoClear` toggling) while simultaneously saying it's OBJ-008's responsibility. This is half-decided territory — an implementer doesn't know if they should prepare for this pattern or not.

Also: OBJ-008 in the progress map depends on OBJ-002, not OBJ-010. And the transitions description in D4 mentions scene children being "disposed and removed" between scenes — but scene teardown is OBJ-011 territory (scene setup/teardown commands).

**Fix:** Remove transition-specific details from D4. Replace with: "OBJ-010 provides a single `THREE.Scene` instance. Scene content lifecycle (adding/removing meshes, scene teardown) is managed by OBJ-011 (message protocol). Transition rendering (if it requires multiple scenes or `autoClear` toggling) is the responsibility of the transition system (OBJ-008/OBJ-015). OBJ-010 does not constrain or anticipate these patterns — it provides the renderer and scene primitives they will build upon."

### Issue 7: Missing Puppeteer Viewport Sizing Guidance (Minor)

The spec says Puppeteer's viewport should match the canvas size, but doesn't say where or how. This isn't OBJ-010's job to implement (that's OBJ-009), but OBJ-010 should document the requirement since it affects correctness.

**Fix:** Add to Integration Points / Consumed by OBJ-009: "OBJ-009 (Puppeteer bridge) must set the Puppeteer viewport dimensions to match `PageInitConfig.width` and `PageInitConfig.height` before loading the page. If viewport and canvas dimensions mismatch, captured frames will be incorrectly sized."

### Issue 8: `getRendererInfo().webglVersion` Extraction Not Specified (Minor)

How does the implementer get the WebGL version string? Three.js doesn't expose it directly. You need `renderer.getContext().getParameter(renderer.getContext().VERSION)`. The `vendor` and `gpuRenderer` require the `WEBGL_debug_renderer_info` extension, which may not be available.

**Fix:** Add implementation hints to `getRendererInfo()` contract:
- `webglVersion`: obtained via `gl.getParameter(gl.VERSION)` where `gl = renderer.getContext()`.
- `vendor` / `gpuRenderer`: obtained via `WEBGL_debug_renderer_info` extension. If the extension is unavailable, return `'unknown'`.
- `maxTextureSize`: `gl.getParameter(gl.MAX_TEXTURE_SIZE)`.

### Issue 9: `init()` with Non-Integer Width/Height — "Floors to integer" Not Sufficient (Minor)

The edge case table says non-integer width/height are floored. But `Math.floor(1919.9)` = 1919, which silently changes the composition resolution. This could cause frame size mismatches with FFmpeg, which expects exact dimensions.

**Fix:** Change behavior: `init()` rounds to nearest integer via `Math.round()` (not floor), and logs a warning if the input was not already an integer. The warning should say what the input was and what it was rounded to.

---

## Summary of Required Changes

| # | Severity | Issue | Fix |
|---|---|---|---|
| 1 | Major | `antialias` not decided | Make it a Design Decision, default `false`, add to config |
| 2 | Major | No `renderFrame()` — gap for testing and downstream | Add minimal `renderFrame()` method |
| 3 | Minor | `clearColor` vs `scene.background` confusion | Clarify in PageInitConfig docs |
| 4 | Major | `SerializedGeometry` scope bleed from OBJ-005 | Remove from OBJ-010, defer to OBJ-011 |
| 5 | Minor | `dispose()` missing `forceContextLoss()` | Add to dispose contract and edge cases |
| 6 | Major | D4 half-decides transition architecture | Remove transition details, keep it neutral |
| 7 | Minor | Puppeteer viewport sizing requirement undocumented | Add note in integration points |
| 8 | Minor | `getRendererInfo()` implementation not specified | Add WebGL API hints |
| 9 | Minor | Non-integer dimension handling | Use `Math.round()` + warning |

Please revise addressing the 4 major issues (1, 2, 4, 6) and the 5 minor ones. I'll verify the fixes structurally in the next round.

---

## Round 3 — spec_author

All nine issues are valid. Here's the fully revised specification addressing every one.

---

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
   * If cameraState is provided, updates the camera before rendering:
   * - position: calls camera.position.set(x, y, z)
   * - lookAt: calls camera.lookAt(x, y, z)
   * - fov: sets camera.fov and calls camera.updateProjectionMatrix()
   *
   * Only provided fields are updated; omitted fields leave the camera unchanged.
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
   * Enable only if visual tuning objectives (OBJ-059–066) determine it's needed
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

After OBJ-010, this file contains a **stub**. OBJ-011 defines the full message handling protocol. OBJ-010 establishes the pattern: the message handler listens for commands dispatched via `page.evaluate()` and calls into the `window.depthkit` API.

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

Shared TypeScript types for the data structures that cross the Node/browser boundary. These types live on the Node side only — the browser receives plain objects via `page.evaluate()`. Limited to types OBJ-010 owns: initialization config and renderer info. Geometry serialization types are deferred to OBJ-011.

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

**Pixel ratio:** `renderer.setPixelRatio(1)` is called explicitly. Chromium may report `devicePixelRatio > 1` even in headless mode. We need exactly 1:1 pixel mapping — a 1920×1080 canvas must produce a 1920×1080 frame buffer.

### D3: `preserveDrawingBuffer: true` as Default

**Decision:** The `WebGLRenderer` is created with `preserveDrawingBuffer: true` by default.

**Rationale:** Without this flag, canvas contents may be cleared after compositing, making `canvas.toDataURL()` return blank images. While CDP `Page.captureScreenshot` may not need it, `toDataURL()` is a common fallback. Negligible performance impact.

### D4: `antialias: false` as Default

**Decision:** The `WebGLRenderer` is created with `antialias: false` by default. Configurable via `PageInitConfig.antialias`.

**Rationale:** Antialiasing is implementation-defined across GPU hardware and SwiftShader. Different backends produce different sub-pixel results, violating C-05 (deterministic output). Software WebGL (SwiftShader) and hardware GPUs will produce different antialiased output for the same scene. Defaulting to `false` ensures deterministic frame capture across environments. Visual tuning objectives (OBJ-059–066) may enable it if determinism is verified for their target environments.

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

**Rationale:** Canvas dimensions must be integers. `Math.round()` is more intuitive than `Math.floor()` (e.g., 1919.7 → 1920 instead of 1919). The warning prevents silent resolution changes that could cause frame size mismatches with FFmpeg.

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

- [ ] **AC-18:** `renderFrame({ position: [1, 2, 3], lookAt: [0, 0, -10], fov: 35 })` updates the camera's position, lookAt, and FOV, then calls `renderer.render(scene, camera)`. After the call, `camera.position` is `(1, 2, 3)`, `camera.fov` is `35`, and `camera.updateProjectionMatrix()` has been called.

- [ ] **AC-19:** `renderFrame()` with no arguments renders with the camera's current state (no changes applied).

- [ ] **AC-20:** `init({ width: 1919.7, height: 1080.3 })` rounds to 1920×1080 and logs a console warning about non-integer dimensions.

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
| `renderFrame()` with partial `cameraState` | Only provided fields are updated. Omitted fields leave camera unchanged. |
| `renderFrame()` with empty `cameraState` `{}` | No camera changes; renders current state. |
| `clearColor` not a valid hex string | Three.js `Color` constructor throws. Error propagates. |
| `fov <= 0` or `fov >= 180` in init or renderFrame | Passed through to Three.js. Produces incorrect rendering. OBJ-004 (manifest validation) catches this upstream. |
| WebGL context limit (~16 contexts) | `dispose()` calls `renderer.forceContextLoss()` then `renderer.dispose()` to fully release the context. If the limit is reached despite proper disposal, `init()` fails with WebGL context creation error. Orchestrator must call `dispose()` between videos. |
| Very large canvas (e.g., 7680×4320) | Allowed if within WebGL's `MAX_VIEWPORT_DIMS`. OBJ-010 does not impose resolution limits — OBJ-004 validates. |
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
12. Call `renderFrame({ position: [1, 2, 3], lookAt: [0, 0, -10], fov: 35 })`. Assert camera position, fov updated.
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

---

I believe this revision addresses all nine issues raised in Round 2:

1. ✅ **antialias** → D4, added to `PageInitConfig`, AC-16, `RendererInfo.antialias`
2. ✅ **renderFrame()** → Full method contract, AC-17/18/19, tests 11-14
3. ✅ **clearColor vs scene.background** → Clarified in `init()` contract and AC-13
4. ✅ **SerializedGeometry removed** → Deferred to OBJ-011, `page-types.ts` only has OBJ-010-owned types
5. ✅ **dispose() forceContextLoss** → Added to contract, edge cases, AC-07
6. ✅ **D4 transition details removed** → Replaced with D5 (neutral scene lifecycle stance)
7. ✅ **Puppeteer viewport note** → Added to OBJ-009 integration point
8. ✅ **getRendererInfo() hints** → Added WebGL API details in contract
9. ✅ **Non-integer dimensions** → D10, `Math.round()` + warning, AC-20

Challenger — please verify and approve if satisfactory.

---

## Round 4 — spec_challenger

I've carefully verified the Round 3 revision against every issue from Round 2.

## Verification Results

| # | Issue | Status | Verification |
|---|---|---|---|
| 1 | `antialias` undecided | ✅ Fixed | D4 exists, `PageInitConfig.antialias` has default `false`, AC-16 tests both states, `RendererInfo.antialias` reflects setting |
| 2 | No `renderFrame()` | ✅ Fixed | Full method contract with partial `cameraState`, AC-17 (not init'd error), AC-18 (state application), AC-19 (no-arg render), tests 11-14 |
| 3 | `clearColor` vs `scene.background` | ✅ Fixed | `init()` docs: "scene.background is NOT set — the clear color serves as the background." AC-13 asserts `scene.background` is null |
| 4 | `SerializedGeometry` scope bleed | ✅ Fixed | Removed from `page-types.ts`. Only `PageInitConfig`, `RendererInfo`, `FrameCameraState` remain. `geometry-library.js` stub notes deferral to OBJ-011 |
| 5 | `dispose()` missing `forceContextLoss` | ✅ Fixed | Contract says "Calls renderer.forceContextLoss() then renderer.dispose()." AC-07 verifies. Edge case table documents context limit |
| 6 | D4 transition overreach | ✅ Fixed | Replaced with D5: "Scene content lifecycle... is managed by downstream objectives." Neutral stance, no transition architecture prescribed |
| 7 | Puppeteer viewport note | ✅ Fixed | OBJ-009 consumed-by entry says "Must set Puppeteer viewport dimensions to match PageInitConfig.width and PageInitConfig.height" |
| 8 | `getRendererInfo()` impl hints | ✅ Fixed | Contract includes `gl.getParameter(gl.VERSION)`, `WEBGL_debug_renderer_info` extension pattern, `gl.getParameter(gl.MAX_TEXTURE_SIZE)` |
| 9 | Non-integer dimensions | ✅ Fixed | D10 specifies `Math.round()` + warning. AC-20 tests `1919.7 → 1920`. Edge case table covers <= 0 after rounding |

## One Remaining Minor Issue

**`renderFrame()` order of operations**: The contract lists position, lookAt, and fov updates but doesn't explicitly state they must be applied in that order. In Three.js, `camera.lookAt()` computes the rotation from the *current* position to the target. If an implementer applies lookAt before position, the camera would briefly point in the wrong direction — and since `lookAt` sets the quaternion once (not as a constraint), the final rendered frame would have the camera at the new position but looking from the old position's perspective.

This is minor because a competent implementer would likely do it correctly, and the listed order (position → lookAt → fov) is the natural reading. I'll add an explicit note in the final spec.

---

Everything else is solid. The D1 (Dumb Page) decision is well-justified and documented. The scope boundaries are clean — no bleed into OBJ-005, OBJ-011, or OBJ-008 territory. The acceptance criteria are specific and testable. The edge case table is comprehensive. The integration points correctly identify what each downstream consumer needs.

CONCLUSION:

The spec is approved with the minor addition of explicit operation ordering in `renderFrame()`. Writing to disk now.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md",
  "content": "# Specification: OBJ-010 \u2014 Three.js Page Shell, Build/Bundle Architecture, and Scene Renderer Skeleton\n\n## Summary\n\nOBJ-010 establishes the browser-side rendering foundation and the authoritative Node.js/browser code-split architecture for depthkit. It delivers: (1) the final HTML page shell with a properly sized WebGL canvas, (2) the Three.js `Scene` / `PerspectiveCamera` / `WebGLRenderer` initialization skeleton that all downstream rendering depends on, (3) the architectural decision that the browser page is a **data-driven renderer** \u2014 a \"dumb page\" that receives computed scene state from the Node.js orchestrator and executes Three.js calls accordingly, and (4) a minimal `renderFrame()` primitive that downstream objectives build upon. This objective also defines Node-side TypeScript types for data crossing the Node/browser boundary (excluding geometry serialization, which is deferred to OBJ-011).\n\n## Interface Contract\n\n### Module: `src/page/scene-renderer.js`\n\nThis is the esbuild entry point (per OBJ-001). It initializes Three.js, exposes a global `window.depthkit` namespace, and imports the other page modules. After OBJ-010, this file contains the renderer skeleton \u2014 downstream objectives populate scene management and message handling.\n\n```typescript\n// Conceptual contract for window.depthkit (exposed as globals on the page).\n// These are NOT TypeScript files \u2014 they are plain JS running in Chromium.\n// Types here document the contract; implementation is JS.\n\ninterface DepthkitPage {\n  /**\n   * Initializes the Three.js renderer, camera, and scene.\n   * Called once when the page is first set up by the orchestrator.\n   *\n   * Behavior:\n   * - Creates a WebGLRenderer bound to the #depthkit-canvas element.\n   * - Calls renderer.setSize(width, height) to set canvas intrinsic dimensions.\n   * - Ca
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md
Now update the meta.json:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-010",
     3→  "description": "Three.js page shell, build/bundle strategy, and scene renderer skeleton -- HTML shell (src/page/index.html), page-side module loading strategy (CDN vs bundled Three.js, ESM vs build step via esbuild/vite), mechanism for making TypeScript geometry definitions available to the browser page, Three.js Scene/PerspectiveCamera/WebGLRenderer initialization, and WebGL canvas setup. This is the authoritative decision point for the Node.js/browser code-split architecture.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001", "OBJ-003"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Expanded to cover build/bundle strategy per Round 2 Issue 5."
    12→}
    13→

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json",
  "content": "{\n  \"id\": \"OBJ-010\",\n  \"description\": \"Three.js page shell, build/bundle strategy, and scene renderer skeleton -- HTML shell (src/page/index.html), page-side module loading strategy (CDN vs bundled Three.js, ESM vs build step via esbuild/vite), mechanism for making TypeScript geometry definitions available to the browser page, Three.js Scene/PerspectiveCamera/WebGLRenderer initialization, and WebGL canvas setup. This is the authoritative decision point for the Node.js/browser code-split architecture.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"spec-deliberation\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T01:30:00Z\",\n  \"depends_on\": [\"OBJ-001\", \"OBJ-003\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"review_status\": \"approved\",\n  \"notes\": \"Spec approved after 4-round deliberation. Key decision: Dumb Page / Smart Orchestrator architecture (D1) -- browser page is a data-driven renderer receiving pre-computed camera state per frame. Confirms OBJ-001 esbuild IIFE strategy. Exposes window.depthkit API with init/dispose/renderFrame/getRendererInfo. Antialias defaults false for C-05 determinism. SerializedGeometry types deferred to OBJ-011. Node-side types in src/engine/page-types.ts.\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/meta.json has been updated successfully.

[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]


Now let me commit these files:
[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Show working tree status"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commits"
}
[Tool Result] dcf4d08 spec(OBJ-007): depth model — semantic slot taxonomy and override system
dc13dd4 spec(OBJ-004): Manifest schema core — Zod validation and registry contract
90a2c38 spec(OBJ-002): interpolation, easing, and spring utilities
28fe944 spec(OBJ-001): Project scaffolding and build system specification
fb3e4b3 spec(OBJ-003): Coordinate system and spatial math reference
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-010/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/transcript.md
	nodes/OBJ-002/transcript.md
	nodes/OBJ-003/transcript.md
	nodes/OBJ-004/transcript.md
	nodes/OBJ-006/output.md
	nodes/OBJ-007/transcript.md
	nodes/OBJ-010/output.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-010/output.md nodes/OBJ-010/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-010): Three.js page shell, build/bundle architecture, and scene renderer skeleton\n\nKey decisions:\n- Dumb Page / Smart Orchestrator architecture: browser page is a data-driven\n  renderer receiving pre-computed camera state per frame from Node.js\n- Confirms OBJ-001 esbuild IIFE strategy, no domain logic in browser bundle\n- Exposes window.depthkit API: init/dispose/renderFrame/getRendererInfo\n- antialias defaults false for C-05 determinism\n- SerializedGeometry types deferred to OBJ-011 (avoids OBJ-005 scope bleed)\n- Node-side types (PageInitConfig, RendererInfo, FrameCameraState) in\n  src/engine/page-types.ts\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-010 spec and updated meta.json"
}
[Tool Result] [master bcaf2c5] spec(OBJ-010): Three.js page shell, build/bundle architecture, and scene renderer skeleton
 2 files changed, 536 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-010/output.md
Spec committed. Here's a summary of the agreed specification:

## OBJ-010 — Final Spec Summary

**Core architectural decision (D1):** The browser page is a **Dumb Page / Smart Orchestrator** — a generic data-driven Three.js renderer that receives pre-computed camera state per frame from the Node.js orchestrator. No domain logic (interpolation, camera paths, scene sequencing) runs in the browser. This is the purest expression of C-03 (virtualized clock) and creates a single source of truth on the Node side.

**Deliverables:**
- `src/page/index.html` — Final HTML shell with canvas
- `src/page/scene-renderer.js` — Three.js init skeleton exposing `window.depthkit` API (`init`, `dispose`, `renderFrame`, `getRendererInfo`, `isInitialized` + `renderer`/`scene`/`camera` properties)
- `src/engine/page-types.ts` — Node-side types: `PageInitConfig`, `RendererInfo`, `FrameCameraState`
- Updated stubs for `geometry-library.js` and `message-handler.js` with documented contracts

**Key design choices:**
- `antialias: false` default (C-05 determinism)
- `preserveDrawingBuffer: true` default (frame capture correctness)
- `setPixelRatio(1)` enforced (no HiDPI scaling)
- `renderFrame()` applies camera state in strict order: position → lookAt → fov
- `dispose()` calls `forceContextLoss()` before `dispose()` for context cleanup
- Non-integer dimensions rounded with warning
- Scene lifecycle (transitions, teardown) left neutral for downstream objectives

**20 acceptance criteria**, comprehensive edge case table, 21-item test strategy using Puppeteer-based integration tests.
