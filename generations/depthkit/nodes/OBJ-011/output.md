# Specification: OBJ-011 — Puppeteer-to-Page Message Protocol

## Summary

OBJ-011 defines the complete cross-boundary message protocol between the Node.js orchestrator and the headless Chromium page. It delivers: (1) a `PageProtocol` class on the Node side that wraps `PuppeteerBridge.evaluate()` with typed, high-level commands — initialization, scene setup/teardown, frame rendering (with multi-pass support for transitions), and disposal; (2) page-side extensions to `window.depthkit` that implement the protocol handlers — scene management (creating/removing THREE.Group instances with textured meshes), texture loading via THREE.TextureLoader, and multi-pass compositing for transitions; and (3) shared protocol types (`src/engine/protocol-types.ts`) that define every data structure crossing the boundary. This is the single source of truth for the Node.js/browser contract, building on OBJ-009's `evaluate()` primitive, OBJ-010's renderer skeleton, and OBJ-005's geometry slot structures.

## Interface Contract

### Protocol Types: `src/engine/protocol-types.ts`

All types in this module are JSON-serializable (no functions, no class instances, no Three.js types). They document the shapes that cross the `page.evaluate()` boundary.

```typescript
// src/engine/protocol-types.ts

import type { PageInitConfig, RendererInfo } from './page-types.js';
import type { FogConfig } from '../scenes/geometries/types.js';

// Re-export for protocol consumers
export type { PageInitConfig, RendererInfo, FogConfig };

// ────────────────────────────────────────────
// Camera State
// ────────────────────────────────────────────

/**
 * Fully-specified camera state for a render pass.
 * All fields are required — the orchestrator always computes
 * the complete camera state per frame per pass. No optional
 * fields, no carry-forward semantics.
 *
 * Distinct from OBJ-010's FrameCameraState (all-optional),
 * which is used by OBJ-010's lower-level renderFrame() method.
 * This type is used exclusively in the OBJ-011 render protocol.
 */
export interface RequiredCameraState {
  /** Camera position in world units [x, y, z]. */
  position: [number, number, number];
  /** Camera lookAt target in world units [x, y, z]. */
  lookAt: [number, number, number];
  /** Vertical field of view in degrees. */
  fov: number;
}

// ────────────────────────────────────────────
// Scene Setup
// ────────────────────────────────────────────

/**
 * Configuration for setting up a scene on the page.
 * Sent by the orchestrator when preparing a scene for rendering.
 *
 * Each scene is an isolated group of Three.js meshes identified
 * by sceneId. Multiple scenes can coexist on the page simultaneously
 * (required for transition overlap rendering).
 */
export interface SceneSetupConfig {
  /**
   * Unique identifier for this scene instance.
   * Must match the manifest's scene.id.
   * Used to reference this scene in render and teardown commands.
   * Must be non-empty.
   */
  sceneId: string;

  /**
   * The plane slots to create as textured meshes.
   * Keys are slot names (from the geometry definition).
   * Values define spatial placement + texture source.
   *
   * Only slots with assigned images are included — optional
   * geometry slots without images are omitted by the orchestrator.
   */
  slots: Record<string, SlotSetup>;

  /**
   * Optional fog configuration for this scene.
   * Applied when this scene is the primary (highest-opacity) scene
   * in a render pass. null or omitted means no fog.
   */
  fog?: FogConfig | null;
}

/**
 * Setup data for a single plane slot within a scene.
 * Combines spatial data (from the geometry's PlaneSlot definition,
 * with any manifest overrides applied by the orchestrator) with
 * the texture source.
 */
export interface SlotSetup {
  /** Position in world units [x, y, z]. */
  position: [number, number, number];
  /** Euler rotation in radians [rx, ry, rz]. */
  rotation: [number, number, number];
  /** Plane geometry dimensions in world units [width, height]. */
  size: [number, number];
  /**
   * Texture source. One of:
   * - Absolute POSIX file path (starting with '/', converted to
   *   'file://' + path by the page handler)
   * - file:// URL
   * - data: URI (base64-encoded image)
   * - http:// or https:// URL (development/testing only)
   *
   * The page handler detects the format and handles accordingly.
   * Absolute POSIX file paths are the primary production path
   * per OBJ-009 D10.
   *
   * Production use should prefer absolute file paths or data URIs
   * for deterministic rendering (C-05). HTTP/HTTPS URLs are
   * supported for development/testing but introduce network
   * dependency that may affect reproducibility.
   *
   * Path resolution assumes POSIX filesystem paths (Linux/macOS).
   * The depthkit engine targets Linux VPS and Docker containers
   * (seed C-08, C-11). Windows paths are not supported.
   */
  textureSrc: string;
  /**
   * Whether the material should enable transparency (alpha blending).
   * When true: material.transparent = true, material.alphaTest = 0.01.
   * When false or omitted: material is fully opaque.
   */
  transparent?: boolean;
  /**
   * Three.js render order for depth-sorting.
   * Higher values render on top. Default: 0.
   */
  renderOrder?: number;
  /**
   * Whether this plane should ignore scene fog.
   * When true: the material is created with `fog: false`, exempting
   * it from Three.js distance-based fog fading.
   * When false or omitted: the material uses `fog: true` (default),
   * meaning it fades toward the fog color at distance.
   *
   * NOTE: In V1, all materials are MeshBasicMaterial (unlit, per
   * OBJ-010 D8). MeshBasicMaterial IS affected by Three.js scene
   * fog when its material `fog` property is `true` (the default).
   * For fogImmune slots, the material is created with `fog: false`,
   * exempting it from distance-based fading.
   */
  fogImmune?: boolean;
}

/**
 * Result of a scene setup operation.
 * Reports per-slot texture loading outcomes.
 */
export interface SceneSetupResult {
  /** The scene ID that was set up. */
  sceneId: string;
  /** Per-slot loading results. Keys match the input slots. */
  slots: Record<string, SlotLoadResult>;
  /** True if ALL slots loaded successfully. */
  success: boolean;
}

/**
 * Result of loading a single slot's texture.
 */
export interface SlotLoadResult {
  /** Whether the texture loaded successfully. */
  status: 'loaded' | 'error';
  /** Natural width of the loaded texture in pixels. Present when status='loaded'. */
  naturalWidth?: number;
  /** Natural height of the loaded texture in pixels. Present when status='loaded'. */
  naturalHeight?: number;
  /** Error message if status='error'. */
  error?: string;
}

// ────────────────────────────────────────────
// Frame Rendering
// ────────────────────────────────────────────

/**
 * Command to render a single output frame.
 *
 * Supports multi-pass rendering for transitions: each pass
 * renders one scene with its own camera state and opacity.
 * The page composites all passes into a single frame using
 * sequential rendering with autoClear=false.
 *
 * COMPOSITING MODEL (order-dependent over-paint):
 *
 * Passes are rendered sequentially. Each pass paints over whatever
 * was rendered by previous passes. The visual result depends on
 * both the opacity values AND the pass order.
 *
 * For normal (non-transition) frames:
 *   passes = [{ sceneId: A, opacity: 1.0, camera: ... }]
 *
 * For crossfade transitions at progress p (0->1, where 0=fully A, 1=fully B):
 *   passes = [
 *     { sceneId: A, opacity: 1.0, camera: ... },  // outgoing scene, full opacity
 *     { sceneId: B, opacity: p,   camera: ... },   // incoming scene, increasing opacity
 *   ]
 *   Visual result: B at p% over A. As p increases, B progressively
 *   covers A. At p=0.5: ~50/50 blend. At p=1.0: fully B.
 *   This is an approximation of true alpha compositing but produces
 *   visually acceptable results for opaque scenes.
 *
 * For dip_to_black transitions:
 *   Fade out: passes = [{ sceneId: A, opacity: 1-p, camera: ... }]
 *   Fade in:  passes = [{ sceneId: B, opacity: p,   camera: ... }]
 *   The clear color (black) shows through where opacity < 1.
 *
 * For cut transitions:
 *   passes = [{ sceneId: B, opacity: 1.0, camera: ... }]
 *   Scene just changes between frames.
 *
 * The orchestrator (OBJ-036) is responsible for computing the
 * correct opacity values for each pass given the transition type
 * and progress. The protocol transmits them as-is.
 */
export interface RenderFrameCommand {
  /**
   * Ordered list of render passes. Rendered in order;
   * later passes paint over earlier ones via NormalBlending
   * with autoClear=false.
   * Must contain at least one pass.
   */
  passes: RenderPass[];

  /**
   * Optional frame metadata for debugging/logging.
   * Not used by the page for any rendering logic.
   */
  debug?: {
    /** Current frame number (zero-indexed). */
    frame?: number;
    /** Frames per second. */
    fps?: number;
    /** Total frames in the composition. */
    totalFrames?: number;
  };
}

/**
 * A single render pass within a frame.
 * Renders one scene at a given opacity with a given camera state.
 */
export interface RenderPass {
  /**
   * The scene to render. Must have been set up via setupScene().
   */
  sceneId: string;

  /**
   * Opacity for this pass (0.0 = fully transparent, 1.0 = fully opaque).
   * Clamped to [0.0, 1.0] by the page handler.
   *
   * Applied by setting material.opacity on all meshes in the scene group
   * before rendering. Original opacities are saved before and restored after
   * each frame's render passes complete.
   */
  opacity: number;

  /**
   * Camera state for this pass. All three fields are required —
   * the orchestrator always computes the full camera state.
   */
  camera: RequiredCameraState;
}

// ────────────────────────────────────────────
// Scene Teardown
// ────────────────────────────────────────────

/**
 * Result of tearing down a scene.
 */
export interface SceneTeardownResult {
  /** The scene ID that was torn down. */
  sceneId: string;
  /** Number of meshes removed. */
  meshesRemoved: number;
  /** Number of textures disposed. */
  texturesDisposed: number;
}

// ────────────────────────────────────────────
// Error Reporting
// ────────────────────────────────────────────

/**
 * Structured error from the page, surfaced through evaluate().
 * Page-side handlers throw errors with this shape serialized
 * as the message, which Puppeteer propagates to the Node side.
 *
 * The PageProtocol class catches these and wraps them in
 * PageProtocolError instances.
 */
export interface PageErrorInfo {
  /** Error category for programmatic handling. */
  code: PageErrorCode;
  /** Human-readable error description. */
  message: string;
  /** Additional context (e.g., which sceneId, which slot). */
  details?: Record<string, unknown>;
}

/**
 * Error codes for page-side errors.
 */
export type PageErrorCode =
  | 'NOT_INITIALIZED'        // init() not called
  | 'ALREADY_INITIALIZED'    // init() called twice
  | 'SCENE_EXISTS'           // setupScene with duplicate sceneId
  | 'SCENE_NOT_FOUND'        // renderFrame/teardown with unknown sceneId
  | 'TEXTURE_LOAD_FAILED'    // One or more textures failed to load
  | 'WEBGL_ERROR'            // WebGL context error
  | 'INVALID_COMMAND'        // Malformed command data
  ;
```

### Node-Side Protocol Class: `src/engine/page-protocol.ts`

```typescript
// src/engine/page-protocol.ts

import type { PuppeteerBridge } from './puppeteer-bridge.js';
import type {
  PageInitConfig,
  RendererInfo,
  SceneSetupConfig,
  SceneSetupResult,
  RenderFrameCommand,
  SceneTeardownResult,
  PageErrorInfo,
} from './protocol-types.js';

/**
 * Error thrown by PageProtocol methods when a page-side error occurs.
 * Wraps the structured PageErrorInfo from the page.
 */
export class PageProtocolError extends Error {
  /** Structured error code from the page. */
  readonly code: string;
  readonly details?: Record<string, unknown>;

  constructor(info: PageErrorInfo);
}

/**
 * High-level protocol client for communicating with the depthkit
 * page running in headless Chromium.
 *
 * Wraps PuppeteerBridge.evaluate() with typed, domain-specific
 * commands. Each method corresponds to one protocol operation.
 *
 * The PageProtocol does NOT own the PuppeteerBridge lifecycle —
 * the caller (OBJ-035 orchestrator) creates the bridge, calls
 * bridge.launch(), then creates PageProtocol with the bridge.
 *
 * Usage:
 *   const bridge = new PuppeteerBridge({ width: 1920, height: 1080 });
 *   await bridge.launch();
 *   const protocol = new PageProtocol(bridge);
 *   const info = await protocol.initialize({ width: 1920, height: 1080 });
 *   // ... setup scenes, render frames, teardown scenes ...
 *   await protocol.dispose();
 *   await bridge.close();
 */
export class PageProtocol {
  constructor(bridge: PuppeteerBridge);

  /**
   * Initialize the Three.js renderer on the page.
   * Calls window.depthkit.init() with the provided config.
   *
   * Must be called once before any other protocol method
   * (except getRendererInfo, which works before init).
   *
   * @param config - Composition-level renderer settings.
   * @returns Renderer diagnostic info.
   * @throws PageProtocolError with code 'ALREADY_INITIALIZED' if called twice.
   * @throws Error if bridge is not launched.
   */
  initialize(config: PageInitConfig): Promise<RendererInfo>;

  /**
   * Set up a scene: create a THREE.Group, create meshes for each
   * slot with PlaneGeometry, load textures, and add the group to
   * the Three.js scene (hidden by default — visible: false until
   * referenced in a renderFrame pass).
   *
   * Texture loading is asynchronous on the page. This method waits
   * for all textures to either load or fail before returning.
   *
   * The scene group is added to window.depthkit.scene but starts
   * with visible=false. It becomes visible only when referenced
   * in a RenderFrameCommand pass. This prevents a newly-setup scene
   * from flashing on screen before the orchestrator is ready.
   *
   * Multiple scenes can be set up simultaneously (required for
   * transition overlap). Each scene is independent — they do not
   * share textures or meshes.
   *
   * @param config - Scene geometry slots with texture sources.
   * @returns Per-slot loading results and overall success flag.
   * @throws PageProtocolError with code 'NOT_INITIALIZED' if init not called.
   * @throws PageProtocolError with code 'SCENE_EXISTS' if sceneId already set up.
   * @throws PageProtocolError with code 'INVALID_COMMAND' if sceneId is empty.
   */
  setupScene(config: SceneSetupConfig): Promise<SceneSetupResult>;

  /**
   * Render a single output frame with one or more passes.
   *
   * Compositing algorithm (sequential over-paint with autoClear=false):
   *
   * Single-pass at opacity 1.0 (fast path):
   *   1. Set only the referenced scene group visible=true.
   *   2. Set scene.fog from this scene's fog config (or null if the
   *      scene has no fog config).
   *   3. Apply camera state.
   *   4. renderer.render(scene, camera) with autoClear=true (normal).
   *
   * Multi-pass or any pass with opacity < 1.0 (composite path):
   *   1. renderer.autoClear = false
   *   2. renderer.clear() (clears both color and depth buffers to clear color)
   *   3. Determine primary scene: the pass with the highest opacity.
   *      Tie-break: first pass in order wins.
   *   4. Set scene.fog from the primary scene's fog config (or null
   *      if the primary scene has no fog). Fog remains constant for
   *      ALL passes in this frame.
   *   5. For each pass in order:
   *      a. renderer.clearDepth() — clear depth buffer only, preserving
   *         the color buffer from previous passes. Ensures this pass's
   *         meshes are not rejected by depth values from earlier passes.
   *      b. Set only this pass's scene group visible=true;
   *         all other scene groups set to visible=false.
   *      c. Save original material opacities for all meshes in the group.
   *      d. Set material.opacity = originalOpacity * pass.opacity
   *         on all meshes. Set material.transparent = true if
   *         pass.opacity < 1.0 (required for Three.js opacity to take effect).
   *      e. Apply camera state (position, lookAt, fov + updateProjectionMatrix).
   *      f. renderer.render(scene, camera)
   *   6. Restore original material opacities and transparent flags
   *      on all meshes in all rendered scene groups.
   *   7. renderer.autoClear = true (restore)
   *
   * Scene groups not referenced in any pass are set to visible=false
   * for this frame (they don't render, but are not torn down).
   *
   * After all passes, the frame is complete and ready for capture
   * via bridge.captureFrame().
   *
   * @param command - The render passes for this frame.
   * @throws PageProtocolError with code 'NOT_INITIALIZED' if init not called.
   * @throws PageProtocolError with code 'SCENE_NOT_FOUND' if a pass references
   *         a sceneId that has not been set up or has been torn down.
   * @throws PageProtocolError with code 'INVALID_COMMAND' if passes is empty.
   */
  renderFrame(command: RenderFrameCommand): Promise<void>;

  /**
   * Tear down a scene: remove all meshes from the Three.js scene,
   * dispose all textures and materials, and delete the scene group.
   *
   * After teardown, the sceneId is no longer valid for renderFrame
   * or teardownScene. setupScene can be called again with the same
   * sceneId (fresh setup).
   *
   * @param sceneId - The scene to tear down.
   * @returns Disposal statistics.
   * @throws PageProtocolError with code 'NOT_INITIALIZED' if init not called.
   * @throws PageProtocolError with code 'SCENE_NOT_FOUND' if sceneId unknown.
   */
  teardownScene(sceneId: string): Promise<SceneTeardownResult>;

  /**
   * Get renderer diagnostic info from the page.
   * Works both before and after init().
   *
   * @returns Renderer info (initialized flag, WebGL version, etc.).
   */
  getRendererInfo(): Promise<RendererInfo>;

  /**
   * Dispose the Three.js renderer and all scene resources.
   *
   * Implementation: calls a single page-side function that iterates
   * all active scenes, disposes their resources (meshes, textures,
   * materials), then calls window.depthkit.dispose() to release the
   * WebGL context. This is a single evaluate() call, not N+1 calls.
   *
   * After dispose(), initialize() can be called again.
   *
   * Idempotent — safe to call when not initialized.
   */
  dispose(): Promise<void>;

  /**
   * Returns the list of currently active scene IDs on the page.
   * Active = set up and not yet torn down.
   *
   * Returns scene IDs in setup order (insertion order).
   */
  getActiveSceneIds(): Promise<string[]>;
}
```

### Page-Side Extensions: `window.depthkit` additions

These methods are added to the `window.depthkit` namespace, implemented in `src/page/scene-renderer.js` (extending OBJ-010's skeleton). They are plain JavaScript running in Chromium. Types here document the contract; implementation is JS.

```typescript
// Conceptual contract — implemented as plain JS on the page.
// Extends OBJ-010's window.depthkit interface.

interface DepthkitPage {
  // ... existing OBJ-010 methods: init, dispose, isInitialized,
  //     getRendererInfo, renderFrame, renderer, scene, camera ...

  /**
   * Set up a scene group with textured plane meshes.
   *
   * Creates a THREE.Group, creates a PlaneGeometry + MeshBasicMaterial
   * + Mesh for each slot, loads textures via THREE.TextureLoader,
   * and adds the group to this.scene (visible: false).
   *
   * Texture loading is parallel — all textures load concurrently.
   * The method resolves when all textures have either loaded or
   * errored. Individual slot failures do NOT prevent other slots
   * from loading.
   *
   * Texture URL resolution:
   * - Paths starting with '/' are converted to 'file://' + path
   * - 'file://', 'data:', 'http://', 'https://' used as-is
   * - All other strings: treated as error (rejected with
   *   'Unsupported texture source format')
   *
   * Note: Path resolution assumes POSIX paths. Windows not supported.
   *
   * Mesh creation per slot:
   * 1. new THREE.PlaneGeometry(size[0], size[1])
   * 2. new THREE.MeshBasicMaterial({
   *      map: loadedTexture,
   *      transparent: slot.transparent ?? false,
   *      alphaTest: slot.transparent ? 0.01 : 0,
   *      side: THREE.FrontSide,
   *      fog: !(slot.fogImmune ?? false),
   *    })
   * 3. mesh.position.set(...slot.position)
   * 4. mesh.rotation.set(...slot.rotation)
   * 5. mesh.renderOrder = slot.renderOrder ?? 0
   * 6. group.add(mesh)
   *
   * If a texture fails to load, the mesh is created with a magenta
   * MeshBasicMaterial (color: 0xff00ff) as a visible debug indicator.
   * The slot's spatial position is preserved so layout issues are
   * still diagnosable in the rendered output.
   *
   * @param config - Scene setup configuration (plain JSON object).
   * @returns SceneSetupResult with per-slot load status.
   * @throws Error with PageErrorInfo if not initialized or sceneId exists.
   */
  setupScene(config: SceneSetupConfig): Promise<SceneSetupResult>;

  /**
   * Render a composited frame from one or more passes.
   *
   * Single-pass at opacity 1.0 (fast path):
   *   - Set referenced scene group visible=true
   *   - Set all other scene groups visible=false
   *   - Set scene.fog from this scene's fog config (or null)
   *   - Apply camera state (position, lookAt, fov + updateProjectionMatrix)
   *   - renderer.render(scene, camera) with autoClear=true
   *
   * Multi-pass or reduced-opacity (composite path):
   *   - renderer.autoClear = false
   *   - renderer.clear() (clears color + depth to clear color)
   *   - Determine primary scene: pass with highest opacity;
   *     tie-break: first pass in order wins.
   *   - Set scene.fog from primary scene's fog config (or null).
   *     Fog remains constant for ALL passes in this frame.
   *   - For each pass in order:
   *     a. renderer.clearDepth() — clear depth buffer only,
   *        preserving color buffer from previous passes
   *     b. Set only this pass's scene group visible=true
   *     c. Save original material opacity and transparent flag
   *        for all meshes in the group
   *     d. Set material.opacity = originalOpacity * pass.opacity
   *        on all meshes. If pass.opacity < 1.0, set
   *        material.transparent = true.
   *     e. Apply camera state
   *     f. renderer.render(scene, camera)
   *   - Restore original material opacities and transparent flags
   *   - renderer.autoClear = true
   *
   * @param command - Render frame command (plain JSON object).
   * @throws Error with PageErrorInfo if not initialized or scene not found.
   */
  renderComposite(command: RenderFrameCommand): Promise<void>;

  /**
   * Tear down a scene group.
   *
   * For each mesh in the group:
   *   1. mesh.geometry.dispose()
   *   2. mesh.material.map?.dispose() (texture)
   *   3. mesh.material.dispose()
   * Then: group.removeFromParent()
   * Then: delete from internal scene registry.
   *
   * @param sceneId - Scene to tear down.
   * @returns SceneTeardownResult with disposal statistics.
   * @throws Error with PageErrorInfo if not initialized or scene not found.
   */
  teardownScene(sceneId: string): Promise<SceneTeardownResult>;

  /**
   * Dispose all active scenes and the renderer.
   *
   * Iterates all active scenes, calls teardownScene logic for each,
   * then calls the existing OBJ-010 dispose() logic
   * (renderer.forceContextLoss() + renderer.dispose()).
   *
   * This is the function called by PageProtocol.dispose() in a
   * single evaluate() call.
   */
  disposeAll(): Promise<void>;

  /**
   * Returns array of currently active scene IDs in setup order.
   */
  getActiveSceneIds(): string[];
}
```

### Page-Side Internal State

The page maintains a scene registry (internal to `window.depthkit`, not directly exposed):

```typescript
// Internal page state — not part of the public protocol,
// but documented here for clarity.

interface PageSceneEntry {
  /** The THREE.Group containing all meshes for this scene. */
  group: THREE.Group;
  /** Map from slot name to mesh reference (for opacity manipulation). */
  meshes: Map<string, THREE.Mesh>;
  /** Map from slot name to texture (for disposal). */
  textures: Map<string, THREE.Texture>;
  /** Fog config for this scene, if any. */
  fog: FogConfig | null;
}

// Internal registry: Map<string, PageSceneEntry>
// Insertion-ordered (JavaScript Map guarantees insertion order).
// Managed by setupScene() and teardownScene().
```

## Design Decisions

### D1: PageProtocol Wraps Bridge, Does Not Own It

**Decision:** `PageProtocol` accepts a `PuppeteerBridge` in its constructor but does not call `bridge.launch()` or `bridge.close()`. The orchestrator (OBJ-035) owns the bridge lifecycle.

**Rationale:** Separation of concerns. The bridge is a transport layer; the protocol is a domain layer. The orchestrator needs direct bridge access for `captureFrame()` (which is not a protocol concern — it's a pixel extraction concern for FFmpeg piping). Ownership nesting: orchestrator -> bridge + protocol -> page.

### D2: Multi-Pass Compositing via Sequential Over-Paint

**Decision:** Transitions are expressed as multi-pass render commands. Passes are rendered sequentially with `renderer.autoClear = false`. Each pass paints over the previous one using Three.js NormalBlending with per-material opacity scaling. Between each pass, `renderer.clearDepth()` clears the depth buffer while preserving the color buffer.

**Compositing algorithm for crossfade at progress `p` (0->1):**
- Pass 1 (outgoing scene A): opacity = 1.0
- Pass 2 (incoming scene B): opacity = p

Visual result: as `p` increases from 0 to 1, scene B progressively covers scene A. At p=0 only A is visible. At p=1 only B is visible. At p=0.5, the result is approximately 50/50.

This is an approximation — not a true alpha composite of two independent renders. The exact math for two passes with NormalBlending:
- After pass 1: pixel = A_color x A_opacity (over clear color)
- After pass 2: pixel = B_color x B_opacity + previous_pixel x (1 - B_opacity)

For opaque scenes (A_opacity=1.0): result = B x p + A x (1-p), which IS a correct linear blend. The approximation only manifests when pass 1 has opacity < 1.0 (e.g., dip_to_black where both passes have reduced opacity), or when pass 1 contains transparent meshes whose alpha channels interact with pass 2.

**Depth buffer handling:** Between each pass, `renderer.clearDepth()` is called to clear the depth buffer while preserving the color buffer. Without this, pass 2's fragments would be rejected by the depth test against pass 1's depth values — meshes at the same Z position in both scenes would fail `GL_LESS`, causing pass 2 to be invisible at those pixels. Clearing the depth buffer per-pass ensures each pass depth-sorts its own meshes correctly while painting over the color from previous passes via alpha blending.

**For V1's three transition types:**
- **cut:** Single pass, opacity 1.0. Exact.
- **crossfade:** Pass A at 1.0, pass B at p. Exact for opaque scenes (all V1 backgrounds are opaque).
- **dip_to_black:** Fade out = one pass at (1-p). Fade in = one pass at p. Exact.

**Alternatives considered:**
1. **Render targets (FBOs):** Render each scene to a separate texture, composite with a shader. Correct but complex. Deferred to OBJ-068 if visual artifacts are found.
2. **Single pass with all materials at blended opacity:** Incorrect — background planes at 50% opacity reveal the clear color through them rather than blending with the other scene.

### D3: Scene Groups Start Hidden

**Decision:** `setupScene()` adds the THREE.Group to the scene graph with `visible = false`. The group becomes visible only when referenced in a `renderFrame` pass.

**Rationale:** Prevents a newly-setup scene from flashing into the rendered output before the orchestrator is ready.

### D4: All Camera Fields Required Per Pass

**Decision:** Each `RenderPass.camera` uses `RequiredCameraState` — all three fields (position, lookAt, fov) are required. There are no optional fields or "carry forward from previous frame" semantics.

**Rationale:** The page is a dumb renderer (OBJ-010 D1). It should not track camera state across frames. Sending all fields per pass eliminates stale-state bugs. The cost is ~72 extra bytes per pass per frame — negligible.

### D5: Texture Loading is Blocking Within setupScene

**Decision:** `setupScene()` is an async operation that resolves only after all texture loads have completed (or failed). There is no separate "load textures" + "await textures" split.

**Rationale:** Simplifies the protocol. For a 5-slot scene with 1920x1080 PNG textures via file:// URLs, expected load time is 100-500ms per texture, all loading in parallel. Total setup time bounded by the slowest texture. Acceptable for V1.

### D6: Texture URL Resolution on the Page (POSIX Only)

**Decision:** The page handler resolves texture sources. Paths starting with '/' are converted to 'file://' URLs. The engine targets POSIX (Linux/macOS) per seed C-08 and C-11 (Docker/VPS). Windows paths are not supported.

**Rationale:** Keeps the Node-side protocol clean (pass file paths as strings) while handling URL conversion in the only place that needs it (the page's TextureLoader).

### D7: Per-Slot Error Reporting, Not All-or-Nothing

**Decision:** If some textures fail to load, `setupScene()` still completes (returns a result), but `SceneSetupResult.success` is `false` and individual `SlotLoadResult.status` values indicate which slots failed. Failed slots get a magenta fallback material. The orchestrator decides whether to abort, retry, or render with degraded output.

**Rationale:** Protocol reports; orchestrator decides. A single missing texture shouldn't prevent the rest of the scene from being usable.

### D8: Structured Page Errors via PageErrorCode

**Decision:** Page-side errors follow a structured format with error codes, human-readable messages, and optional details. The Node-side `PageProtocol` catches these and wraps them in `PageProtocolError` instances.

**Rationale:** Structured errors enable programmatic handling by the orchestrator.

### D9: renderComposite() is Separate from OBJ-010's renderFrame()

**Decision:** The page exposes `renderComposite()` as a new method (handling multi-pass rendering with scene group management), distinct from OBJ-010's existing `renderFrame()` (single-scene, single-camera). The protocol's `PageProtocol.renderFrame()` calls `window.depthkit.renderComposite()`.

**Rationale:** OBJ-010's `renderFrame()` operates on the bare scene/camera — it has no concept of scene groups, opacity, or multi-pass. Rather than modifying OBJ-010's existing method, OBJ-011 adds a higher-level method.

### D10: Fog is Per-Scene, Primary Scene Wins with Deterministic Tie-Break

**Decision:** Each scene carries its own fog config (set during `setupScene`). During multi-pass `renderComposite()`:

1. Determine the primary scene: the pass with the highest opacity value.
2. Tie-break: if multiple passes share the highest opacity, the first pass in order wins.
3. Set `scene.fog` from the primary scene's fog config (or `null` if it has no fog).
4. Fog remains constant for ALL passes in this frame.
5. Fog is not restored after rendering — it persists until the next `renderComposite()` call sets it.

**Rationale:** During crossfades, the outgoing scene (pass 1, opacity 1.0) is always the primary scene because pass 1 opacity is always 1.0 under the crossfade algorithm (D2). The incoming scene's visual contribution increases gradually while the fog environment remains consistent. The transition is short (0.5-1.0s), and abrupt fog changes would be more jarring than a slight inconsistency.

For dip_to_black, only one scene renders per pass, so fog is always from that scene. No ambiguity.

### D11: MeshBasicMaterial.fog Property for fogImmune

**Decision:** Three.js `MeshBasicMaterial` has a `fog` property (boolean, default `true`) that controls whether the material is affected by scene fog. For `fogImmune: true` slots, the material is created with `fog: false`.

**Rationale:** This is the Three.js-native way to exempt specific meshes from fog. No special rendering passes or separate groups needed.

### D12: FogConfig Imported from OBJ-005, Not Duplicated

**Decision:** `protocol-types.ts` imports `FogConfig` from `src/scenes/geometries/types.ts` (OBJ-005) and re-exports it. No duplication.

**Rationale:** OBJ-005's `FogConfig` is already a plain interface with no rendering dependencies. Importing it is a clean type-level dependency between two pure-type modules. If OBJ-005's `FogConfig` evolves, the protocol type evolves automatically.

### D13: RequiredCameraState vs FrameCameraState

**Decision:** `protocol-types.ts` defines `RequiredCameraState` (all fields required) and uses it in `RenderPass.camera`. OBJ-010's `FrameCameraState` (all fields optional) is NOT re-exported from `protocol-types.ts`.

**Rationale:** These are different concepts serving different layers. `FrameCameraState` is OBJ-010's low-level "partial camera update" API. `RequiredCameraState` is OBJ-011's protocol-level "complete camera state per pass." Keeping them separate and NOT re-exporting `FrameCameraState` prevents consumers from accidentally using the wrong type.

### D14: dispose() is a Single evaluate() Call

**Decision:** `PageProtocol.dispose()` calls a single page-side function (`window.depthkit.disposeAll()`) that iterates all active scenes, disposes their resources, then disposes the renderer. This is one `evaluate()` round-trip, not N+1 calls.

**Rationale:** Performance and atomicity. N+1 calls create N+1 evaluate() round-trips and leave the page in an intermediate state if one fails partway.

### D15: getActiveSceneIds() Returns Insertion Order

**Decision:** Active scene IDs are returned in the order they were set up, guaranteed by JavaScript `Map` insertion order semantics.

**Rationale:** Provides a deterministic ordering that downstream consumers can rely on without additional sorting.

## Acceptance Criteria

### PageProtocol (Node-side)

- [ ] **AC-01:** `PageProtocol` is importable from `src/engine/page-protocol.ts`. `new PageProtocol(bridge)` accepts a `PuppeteerBridge` instance.
- [ ] **AC-02:** `protocol.initialize({ width: 1920, height: 1080 })` calls `window.depthkit.init()` on the page and returns `RendererInfo` with `initialized: true`.
- [ ] **AC-03:** `protocol.initialize()` when already initialized throws `PageProtocolError` with `code: 'ALREADY_INITIALIZED'`.
- [ ] **AC-04:** `protocol.setupScene({ sceneId: 'scene_001', slots: { ... } })` returns `SceneSetupResult` with per-slot load statuses.
- [ ] **AC-05:** `protocol.setupScene()` with a duplicate `sceneId` throws `PageProtocolError` with `code: 'SCENE_EXISTS'`.
- [ ] **AC-06:** `protocol.setupScene()` before `initialize()` throws `PageProtocolError` with `code: 'NOT_INITIALIZED'`.
- [ ] **AC-07:** After `setupScene`, `protocol.getActiveSceneIds()` includes the new scene ID.
- [ ] **AC-08:** `protocol.renderFrame({ passes: [{ sceneId: 'scene_001', opacity: 1.0, camera: { position: [0,0,5], lookAt: [0,0,0], fov: 50 } }] })` completes without error. A subsequent `bridge.captureFrame()` returns a non-black PNG buffer (proving the scene rendered).
- [ ] **AC-09:** `protocol.renderFrame()` with a pass referencing an unknown sceneId throws `PageProtocolError` with `code: 'SCENE_NOT_FOUND'`.
- [ ] **AC-10:** `protocol.renderFrame({ passes: [] })` throws `PageProtocolError` with `code: 'INVALID_COMMAND'`.
- [ ] **AC-11:** `protocol.teardownScene('scene_001')` returns `SceneTeardownResult` with `meshesRemoved > 0` and `texturesDisposed > 0`. After teardown, `getActiveSceneIds()` does not include `'scene_001'`.
- [ ] **AC-12:** `protocol.teardownScene('nonexistent')` throws `PageProtocolError` with `code: 'SCENE_NOT_FOUND'`.
- [ ] **AC-13:** `protocol.dispose()` tears down all active scenes and disposes the renderer. After dispose, `protocol.getRendererInfo()` returns `initialized: false`.
- [ ] **AC-14:** `protocol.dispose()` is idempotent — calling it when not initialized does not throw.
- [ ] **AC-15:** `PageProtocolError` instances have `code`, `message`, and optional `details` properties. `error instanceof PageProtocolError` is `true`. `error instanceof Error` is `true`.
- [ ] **AC-16:** `protocol.setupScene({ sceneId: '', slots: {} })` throws `PageProtocolError` with `code: 'INVALID_COMMAND'` and message containing "sceneId must be non-empty".

### Multi-Pass Rendering (Transitions)

- [ ] **AC-17:** A `RenderFrameCommand` with two passes (scene A at opacity 1.0, scene B at opacity 0.5) renders both scenes composited into a single frame. The captured PNG is visually distinct from either scene rendered alone at full opacity. (Proves multi-pass compositing works.)
- [ ] **AC-18:** A `RenderFrameCommand` with one pass at opacity 0.0 produces a frame that is the clear color (black by default). (Proves opacity=0 suppresses rendering.)
- [ ] **AC-19:** A `RenderFrameCommand` with one pass at opacity 1.0 produces the same output as a simple single-pass render of that scene. (Proves the fast path is equivalent.)
- [ ] **AC-20:** After multi-pass rendering, material opacities are restored to their original values. A subsequent single-pass render at opacity 1.0 produces the same output as before the multi-pass frame. (Proves no state leakage between frames.)
- [ ] **AC-21:** Compositing is order-dependent: rendering [A at 1.0, B at 0.5] produces a different result than [B at 1.0, A at 0.5]. (Proves later passes paint over earlier ones.)

### Depth Buffer Independence

- [ ] **AC-35:** During multi-pass rendering, each pass has an independent depth buffer — meshes in pass 2 are not depth-rejected by meshes in pass 1, even if they occupy identical Z positions. Verified by: setting up two scenes with identically-positioned meshes (same slot positions) but different colored textures, rendering [A at 1.0, B at 0.5], and confirming that the captured frame shows a blend of both colors (not just A's color).

### Texture Loading

- [ ] **AC-22:** `setupScene()` with slots whose `textureSrc` is an absolute POSIX file path (e.g., `/path/to/image.png`) loads the texture successfully. `SlotLoadResult.status === 'loaded'` and `naturalWidth`/`naturalHeight` reflect the image dimensions.
- [ ] **AC-23:** `setupScene()` with a slot whose `textureSrc` is a nonexistent path returns `SlotLoadResult.status === 'error'` for that slot, with a descriptive `error` string. Other slots still load successfully.
- [ ] **AC-24:** `setupScene()` with a slot whose `textureSrc` is a base64 data URI loads the texture successfully.

### Scene Lifecycle

- [ ] **AC-25:** After `teardownScene()`, calling `setupScene()` with the same sceneId succeeds (fresh setup — ID can be reused).
- [ ] **AC-26:** Scenes set up but not referenced in any `renderFrame` pass do not appear in the captured frame (hidden by default via `visible=false`).
- [ ] **AC-27:** Multiple scenes can be set up simultaneously. `getActiveSceneIds()` returns all of them in setup order.

### Fog

- [ ] **AC-28:** A scene set up with `fog: { color: '#000000', near: 5, far: 30 }` applies Three.js fog during rendering. Meshes farther from the camera fade toward the fog color.
- [ ] **AC-29:** A slot with `fogImmune: true` renders at full brightness regardless of scene fog distance.
- [ ] **AC-30:** A scene without fog config does not apply fog.
- [ ] **AC-31:** During a multi-pass render where pass 1 (opacity 1.0) has fog and pass 2 (opacity 0.5) has no fog, the fog from pass 1 is applied (pass 1 is the primary scene).

### Protocol Types

- [ ] **AC-32:** All types in `protocol-types.ts` are JSON-serializable — no functions, no class instances, no TypeScript-only constructs. They can be passed through `JSON.parse(JSON.stringify(value))` without data loss.
- [ ] **AC-33:** `protocol-types.ts` re-exports `PageInitConfig` and `RendererInfo` from `page-types.ts` (OBJ-010) and `FogConfig` from OBJ-005's geometry types.
- [ ] **AC-34:** `RequiredCameraState` has all three fields required (position, lookAt, fov). `FrameCameraState` (OBJ-010) is NOT exported from `protocol-types.ts`.

## Edge Cases and Error Handling

### Scene Setup

| Scenario | Expected Behavior |
|---|---|
| `sceneId` is empty string | `PageProtocolError` with code `INVALID_COMMAND`: `"sceneId must be non-empty"` |
| `slots` is empty object `{}` | Succeeds — creates an empty scene group. `SceneSetupResult.success = true`, `slots = {}`. Valid for scenes with no images (e.g., a solid-color scene). |
| Slot with `textureSrc` pointing to a non-image file (e.g., `.txt`) | `SlotLoadResult.status = 'error'` with message describing the load failure. Mesh is created with a magenta fallback material (color: 0xff00ff) so the slot's spatial position is visible (aids debugging). |
| Texture file is very large (e.g., 8192x8192) | Page handler checks against `gl.getParameter(gl.MAX_TEXTURE_SIZE)` after loading. If texture exceeds the limit, `SlotLoadResult.status = 'error'` with message: `"Texture dimensions {w}x{h} exceed WebGL max texture size {max}"`. Mesh created with magenta fallback. |
| `setupScene` called after `dispose()` | `PageProtocolError` with code `NOT_INITIALIZED`. |
| All texture loads fail | `SceneSetupResult.success = false`. All slots have `status: 'error'`. Scene group exists with magenta fallback meshes. |
| `textureSrc` is a relative path (no leading `/`, no protocol) | `SlotLoadResult.status = 'error'` with message: `"Unsupported texture source format: must be absolute path, file://, data:, http://, or https:// URL"`. |

### Frame Rendering

| Scenario | Expected Behavior |
|---|---|
| `passes` array has more than 2 entries | Allowed. Renders all passes in order. No artificial limit. |
| Pass `opacity` > 1.0 or < 0.0 | Clamped to [0.0, 1.0] by the page handler. No error. |
| Pass `opacity` is NaN | Treated as 0.0 (clamped). No error. |
| Two passes reference the same sceneId | Allowed. Scene renders twice with potentially different camera states/opacities. Unusual but not invalid. |
| `renderFrame` called with scene that has failed textures | Renders with magenta fallback materials for failed slots. No error. |
| `camera.fov` is 0 or negative | Passed to Three.js. Produces degenerate rendering. OBJ-004 (manifest validation) prevents this upstream. The protocol does not validate camera values. |
| `debug` field is omitted | No effect. Debug metadata is purely optional. |
| Both passes have identical opacity (tie-break for fog) | First pass in order is the primary scene. Its fog config is used. |

### Scene Teardown

| Scenario | Expected Behavior |
|---|---|
| Teardown a scene that was referenced in the most recent render pass | Teardown runs. The rendered frame was already captured. Next `renderFrame` referencing this scene throws `SCENE_NOT_FOUND`. |
| Teardown the only active scene, then call `renderFrame` referencing it | `PageProtocolError` with code `SCENE_NOT_FOUND`. |
| `dispose()` with active scenes | All scenes torn down, then renderer disposed. Single evaluate() call. |

### Bridge/Page Errors

| Scenario | Expected Behavior |
|---|---|
| Bridge not launched when protocol method is called | `PuppeteerBridge.evaluate()` throws its own "not launched" error (per OBJ-009 AC-16). Propagates through `PageProtocol` unmodified. |
| Page crashes during `setupScene` (e.g., OOM from textures) | Bridge's `pageerror` handler fires. Next protocol call rejects with bridge's stored error (per OBJ-009 D13). |
| WebGL context lost during rendering | Page-side handler catches the context loss event and throws with code `WEBGL_ERROR`. Protocol propagates as `PageProtocolError`. |

## Test Strategy

### Unit Tests: `test/unit/protocol-types.test.ts`

1. **Serialization round-trip:** Construct each protocol type (SceneSetupConfig, RenderFrameCommand, SceneTeardownResult, etc.) as a plain object, run through `JSON.parse(JSON.stringify(...))`, verify no data loss.
2. **PageProtocolError:** Construct with a PageErrorInfo object, verify `instanceof Error`, verify `code`, `message`, `details` properties.
3. **RequiredCameraState vs FrameCameraState:** Verify that `RequiredCameraState` requires all three fields at compile time (TypeScript compilation test).

### Integration Tests: `test/integration/page-protocol.test.ts`

These tests launch real headless Chromium via PuppeteerBridge and exercise the full protocol. Each test creates a bridge, launches it, creates a PageProtocol, runs commands, and verifies results. Tests should use small viewports (e.g., 320x240) and simple test textures (solid-color PNGs, <=100x100) for speed.

**Test fixtures:** Create a `test/fixtures/` directory with small solid-color PNG images (red.png, blue.png, green.png, transparent.png with alpha) generated at test setup time (e.g., via a helper script or inline Buffer construction).

**Initialization tests:**
3. `initialize()` succeeds, returns `RendererInfo` with `initialized: true`.
4. `initialize()` twice throws `PageProtocolError` with code `ALREADY_INITIALIZED`.
5. `setupScene()` before `initialize()` throws with code `NOT_INITIALIZED`.

**Scene setup tests:**
6. `setupScene()` with one slot using a valid PNG file path returns `success: true`, `status: 'loaded'`, correct `naturalWidth`/`naturalHeight`.
7. `setupScene()` with multiple slots loads all textures. All slots report `status: 'loaded'`.
8. `setupScene()` with a missing file returns `success: false`, the failed slot has `status: 'error'`, other slots still load.
9. `setupScene()` with data URI texture loads successfully.
10. `setupScene()` with duplicate sceneId throws `SCENE_EXISTS`.
11. `setupScene()` with empty sceneId throws `INVALID_COMMAND`.
12. `getActiveSceneIds()` reflects setup/teardown state and returns IDs in setup order.

**Frame rendering tests:**
13. Single-pass render: setup scene with colored mesh, render one frame, capture PNG, verify non-black.
14. Camera state is applied: render same scene with two different camera positions, capture both frames, verify they differ.
15. Multi-pass render (crossfade): setup two scenes (one with red mesh, one with blue mesh), render with scene A at 1.0 and scene B at 0.5, capture frame, verify it differs from either scene alone.
16. Opacity 0.0: render at zero opacity, verify frame is the clear color (black).
17. Opacity 1.0 single-pass: verify same result as rendering without multi-pass overhead.
18. State restoration: render multi-pass frame, then render single-pass frame at 1.0, verify single-pass output is identical to a fresh single-pass render (no opacity leakage).
19. Unknown sceneId in pass: throws `SCENE_NOT_FOUND`.
20. Empty passes array: throws `INVALID_COMMAND`.
21. Pass ordering matters: [A@1.0, B@0.5] produces different PNG than [B@1.0, A@0.5].
22. Depth buffer independence (AC-35): two scenes with identically-positioned meshes but different colors, render [A@1.0, B@0.5], verify blended output (not just A's color).

**Scene teardown tests:**
23. Teardown removes scene. `getActiveSceneIds()` no longer includes it.
24. Teardown returns `meshesRemoved > 0`, `texturesDisposed > 0`.
25. After teardown, rendering with that sceneId throws `SCENE_NOT_FOUND`.
26. After teardown, `setupScene()` with same sceneId succeeds (ID reuse).
27. Teardown unknown sceneId throws `SCENE_NOT_FOUND`.

**Dispose tests:**
28. `dispose()` tears down all scenes and disposes renderer. `getRendererInfo()` returns `initialized: false`.
29. `dispose()` is idempotent.
30. After `dispose()`, `initialize()` succeeds again (re-entrant lifecycle).

**Fog tests:**
31. Scene with fog config: render a mesh at far distance, capture frame. Compare with same mesh rendered without fog. Fog version should be darker/faded.
32. fogImmune slot renders at full brightness even with scene fog.
33. During multi-pass render, fog comes from the primary scene (highest opacity, first wins on tie).

**Determinism tests (TC-06):**
34. Same setup + same renderFrame command produces identical PNG buffers across two consecutive runs.

### Relevant Testable Claims

- **TC-02** (render performance): Protocol overhead per frame (evaluate round-trip) is measurable. Log it.
- **TC-06** (deterministic output): Test 34 verifies determinism through the protocol.
- **TC-10** (transitions mask seams): Tests 15-18, 21-22 verify multi-pass compositing works.

## Integration Points

### Depends on

| Dependency | What OBJ-011 uses |
|---|---|
| **OBJ-009** (Puppeteer bridge) | `PuppeteerBridge` class — `evaluate()` as the transport for all protocol commands. OBJ-011 does NOT use `captureFrame()` — that's the orchestrator's concern. |
| **OBJ-010** (Page shell) | `window.depthkit` API — `init()`, `dispose()`, `isInitialized()`, `getRendererInfo()`, `renderFrame()`, `renderer`, `scene`, `camera` properties. OBJ-011 extends this namespace with `setupScene()`, `renderComposite()`, `teardownScene()`, `disposeAll()`, `getActiveSceneIds()`. `PageInitConfig`, `RendererInfo` types from `page-types.ts`. |
| **OBJ-005** (Geometry types) | `FogConfig` type imported and re-exported by `protocol-types.ts`. `PlaneSlot` interface informs `SlotSetup` structure (position, rotation, size, transparent, renderOrder, fogImmune). OBJ-011 does NOT import OBJ-005 at runtime — the orchestrator resolves geometry definitions and constructs `SceneSetupConfig` objects using OBJ-005 data, which OBJ-011 sends to the page as plain JSON. |

### Consumed by

| Downstream | How it uses OBJ-011 |
|---|---|
| **OBJ-012** (FFmpeg encoder) | Indirectly — OBJ-012 receives PNG buffers from `bridge.captureFrame()` after OBJ-011's `renderFrame()` has rendered the frame. OBJ-012 does not call OBJ-011 directly. |
| **OBJ-035** (Orchestrator) | The primary consumer. Composes OBJ-009 (bridge + clock), OBJ-011 (protocol), and OBJ-012 (encoder) into the render loop: `protocol.initialize()` -> for each scene: `protocol.setupScene()` -> for each frame: `protocol.renderFrame()` + `bridge.captureFrame()` -> pipe to FFmpeg -> `protocol.teardownScene()` -> `protocol.dispose()`. |
| **OBJ-036** (Scene sequencer) | Constructs `SceneSetupConfig` objects from manifest scenes + geometry definitions (OBJ-005), then passes them to `protocol.setupScene()`. Constructs `RenderFrameCommand` objects per frame with camera state from OBJ-006/OBJ-007 interpolation and transition opacity from the sequencer's transition logic. |
| **OBJ-039** (Per-frame scene state) | May build on the `renderFrame` command structure for per-frame plane opacity animation (OBJ-044). |

### File Placement

```
depthkit/
  src/
    engine/
      protocol-types.ts       # NEW — All protocol data types
      page-protocol.ts        # NEW — PageProtocol class + PageProtocolError
    page/
      scene-renderer.js       # EVOLVE — Add setupScene, renderComposite,
                               #          teardownScene, disposeAll,
                               #          getActiveSceneIds
                               #          to window.depthkit
```

## Open Questions

### OQ-A: Should multi-pass compositing use render targets instead of autoClear toggling?

The spec's D2 chooses sequential multi-pass rendering with `autoClear=false` and per-pass `clearDepth()`. For V1's three transition types with opaque scenes, this produces mathematically correct crossfades. If OBJ-068 (transition tuning) finds visual artifacts with transparent scenes or exotic transitions, the page handler can be upgraded to render-target-based compositing. The protocol types (`RenderFrameCommand`, `RenderPass`) would not change — only the page-side implementation.

### OQ-B: Should setupScene support texture load timeouts?

Currently, `setupScene` waits indefinitely for texture loads. For V1, file:// URLs load near-instantly, so timeouts are less critical. If HTTP URLs are used, the orchestrator can wrap `protocol.setupScene()` in a `Promise.race()` with a timeout.

### OQ-C: Should the protocol support per-frame plane transforms?

The current spec has static plane transforms set at scene setup time. If per-frame plane state updates are needed (position, opacity, scale), the protocol would need an `updateSlots()` command or an extension to `RenderPass`. Deferred to OBJ-044 (per-frame opacity animation). The current protocol design does not preclude adding this.

### OQ-D: Should the protocol support adding/removing individual slots after scene setup?

Currently, a scene's slots are fixed at setup time. An `addSlot()` / `removeSlot()` command pair could be added later. Deferred — V1 scenes have fixed slot assignments.

### OQ-E: Magenta fallback material for failed textures — is this the right default?

The spec proposes magenta `MeshBasicMaterial` (0xff00ff) when textures fail, preserving the slot's spatial position for debugging. The alternative is skipping failed slots entirely. The orchestrator can act on `SceneSetupResult.success` to abort if needed. The magenta fallback is more debuggable; if production wants clean failure, the orchestrator aborts on `success: false`.
