# Deliberation Transcript: OBJ-011

---

## Round 1 — spec_author

Looking at the objective metadata, dependencies (OBJ-009, OBJ-010, OBJ-005), and the seed document, I'll propose the full specification for OBJ-011.

Let me first check the current state of the codebase and existing files.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]
Let me examine the existing codebase to understand what's already built before proposing the spec.
[Tool: Glob]
  Input: {
  "pattern": "**/src/**/*.ts"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/page/**"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-011/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**"
}

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/**/*.ts"
}
[Tool Result] No files found
[Tool Result] No files found

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

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-009/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-009/output.md

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-010/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-005/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-010/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-005/output.md
Good — the dependency specs are all provided inline in the prompt, so I have everything I need. Let me also check what OBJ-003 spatial types look like since OBJ-005 references them:
[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-003/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-003/output.md",
  "limit": 120
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
Good, I have the spatial types. Now I have everything needed to draft the spec. Let me propose the complete specification for OBJ-011.

---

# Proposed Specification: OBJ-011 — Puppeteer-to-Page Message Protocol

## Summary

OBJ-011 defines the complete cross-boundary message protocol between the Node.js orchestrator and the headless Chromium page. It delivers: (1) a `PageProtocol` class on the Node side that wraps `PuppeteerBridge.evaluate()` with typed, high-level commands — initialization, scene setup/teardown, frame rendering (with multi-pass support for transitions), and disposal; (2) page-side extensions to `window.depthkit` that implement the protocol handlers — scene management (creating/removing THREE.Group instances with textured meshes), texture loading via THREE.TextureLoader, and multi-pass compositing for transitions; and (3) shared protocol types (`src/engine/protocol-types.ts`) that define every data structure crossing the boundary. This is the single source of truth for the Node.js/browser contract, building on OBJ-009's `evaluate()` primitive, OBJ-010's renderer skeleton, and OBJ-005's geometry slot structures.

## Interface Contract

### Protocol Types: `src/engine/protocol-types.ts`

All types in this module are JSON-serializable (no functions, no class instances, no Three.js types). They document the shapes that cross the `page.evaluate()` boundary.

```typescript
// src/engine/protocol-types.ts

import type { PageInitConfig, RendererInfo, FrameCameraState } from './page-types.js';

// Re-export for protocol consumers
export type { PageInitConfig, RendererInfo, FrameCameraState };

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
   * - Absolute file path (converted to file:// URL by the page handler)
   * - file:// URL
   * - data: URI (base64-encoded image)
   * - http:// or https:// URL
   *
   * The page handler detects the format and handles accordingly.
   * Absolute file paths (starting with '/') are the primary
   * production path per OBJ-009 D10.
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
   * When true: uses MeshBasicMaterial regardless of fog.
   * When false or omitted: uses material affected by fog
   * (MeshBasicMaterial is unaffected by fog anyway in Three.js,
   * but if the scene uses MeshLambertMaterial/MeshStandardMaterial
   * for fog interaction, this flag overrides back to Basic).
   *
   * NOTE: In V1, all materials are MeshBasicMaterial (unlit,
   * per OBJ-010 D8). Fog is implemented via THREE.Fog on the scene,
   * which affects Basic materials. fogImmune planes are added to a
   * separate group or have fog disabled per-material — implementation
   * detail, but the contract is: fogImmune planes render at full
   * brightness regardless of distance.
   */
  fogImmune?: boolean;
}

/**
 * Fog configuration (matches OBJ-005 FogConfig, repeated here
 * as a protocol type for serialization clarity).
 */
export interface FogConfig {
  /** CSS hex color string (#RRGGBB). */
  color: string;
  /** Distance from camera where fog begins (world units). */
  near: number;
  /** Distance from camera where fog is fully opaque (world units). */
  far: number;
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
 * The page composites all passes into a single frame.
 *
 * For normal (non-transition) frames: passes has one entry
 * with opacity 1.0.
 *
 * For crossfade transitions: passes has two entries with
 * complementary opacities (e.g., 0.7 and 0.3).
 *
 * For dip_to_black: passes has one entry with decreasing
 * opacity (fade out) or increasing opacity (fade in).
 * The clear color (black) shows through.
 *
 * For cut transitions: single pass, opacity 1.0 — the scene
 * just changes between frames.
 */
export interface RenderFrameCommand {
  /**
   * Ordered list of render passes. Rendered in order;
   * later passes composite on top of earlier ones.
   * Must contain at least one pass.
   */
  passes: RenderPass[];

  /**
   * Optional frame metadata for debugging/logging.
   * Not used by the page for any rendering logic.
   * The page is a "dumb renderer" per OBJ-010 D1 — it does
   * not compute time or interpolate. These are purely diagnostic.
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
   * Implementation: for single-pass frames at opacity 1.0, the page
   * renders normally. For multi-pass or reduced-opacity passes, the
   * page uses one of:
   * - Material opacity on all meshes in the scene group
   * - Render-to-texture with an opacity composite shader
   * - renderer.autoClear toggling with global alpha
   *
   * The compositing strategy is an implementation detail of the page
   * handler. The protocol guarantees: the visual result is equivalent
   * to rendering each pass independently and alpha-blending them in
   * order over the clear color background.
   */
  opacity: number;

  /**
   * Camera state for this pass. All three fields are required per pass
   * — the orchestrator always computes the full camera state.
   */
  camera: {
    position: [number, number, number];
    lookAt: [number, number, number];
    fov: number;
  };
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
  /** Structured error info from the page. */
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
   * @throws PageProtocolError with code 'INVALID_COMMAND' if config is malformed.
   */
  setupScene(config: SceneSetupConfig): Promise<SceneSetupResult>;

  /**
   * Render a single output frame with one or more passes.
   *
   * For each pass in order:
   * 1. Makes the referenced scene group visible.
   * 2. Sets the camera to the pass's camera state.
   * 3. Renders at the pass's opacity.
   * 4. Composites onto the frame buffer.
   *
   * After all passes, the frame is complete and ready for capture
   * via bridge.captureFrame().
   *
   * Scene groups not referenced in any pass are set to visible=false
   * for this frame (they don't render, but are not torn down).
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
   * Calls window.depthkit.dispose() which releases the WebGL context.
   *
   * All active scenes are torn down implicitly.
   * After dispose(), initialize() can be called again.
   *
   * Idempotent — safe to call when not initialized.
   */
  dispose(): Promise<void>;

  /**
   * Returns the list of currently active scene IDs on the page.
   * Active = set up and not yet torn down.
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
   * - All other strings treated as relative file paths,
   *   converted to file:// URLs relative to document.baseURI
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
   * @param config - Scene setup configuration (plain JSON object).
   * @returns SceneSetupResult with per-slot load status.
   * @throws Error with PageErrorInfo if not initialized or sceneId exists.
   */
  setupScene(config: SceneSetupConfig): Promise<SceneSetupResult>;

  /**
   * Render a composited frame from one or more passes.
   *
   * Single-pass rendering (passes.length === 1, opacity === 1.0):
   *   - Set referenced scene group visible=true
   *   - Set all other scene groups visible=false
   *   - Apply camera state via existing renderFrame() method
   *   - renderer.render(scene, camera)
   *
   * Multi-pass rendering (passes.length > 1 or opacity < 1.0):
   *   - renderer.autoClear = false
   *   - renderer.clear() (manual clear to the clear color)
   *   - For each pass in order:
   *     a. Set only the pass's scene group visible=true
   *     b. Set material opacity on all meshes in the group
   *     c. Apply camera state
   *     d. renderer.render(scene, camera)
   *   - renderer.autoClear = true (restore)
   *   - Restore original material opacities
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
   * Returns array of currently active scene IDs.
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
  /**
   * Original material opacity values, stored before multi-pass
   * opacity override and restored after. Keyed by slot name.
   */
  originalOpacities: Map<string, number>;
}

// Internal registry: Map<string, PageSceneEntry>
// Managed by setupScene() and teardownScene().
```

## Design Decisions

### D1: PageProtocol Wraps Bridge, Does Not Own It

**Decision:** `PageProtocol` accepts a `PuppeteerBridge` in its constructor but does not call `bridge.launch()` or `bridge.close()`. The orchestrator (OBJ-035) owns the bridge lifecycle.

**Rationale:** Separation of concerns. The bridge is a transport layer; the protocol is a domain layer. The orchestrator needs direct bridge access for `captureFrame()` (which is not a protocol concern — it's a pixel extraction concern for FFmpeg piping). Ownership nesting: orchestrator → bridge + protocol → page.

### D2: Multi-Pass Compositing for Transitions

**Decision:** Transitions are expressed as multi-pass render commands. Each pass specifies a scene, camera state, and opacity. The page composites them using `renderer.autoClear = false` with per-pass rendering.

**Alternatives considered:**
1. **Single-pass with material opacity:** Set all materials in both scenes to their target opacity, render once. *Rejected:* Opaque background planes at 50% opacity would reveal the clear color through them rather than blending correctly with the other scene. The visual result is wrong — you'd see black bleeding through during a crossfade rather than one scene dissolving into the other.
2. **Render targets (FBOs):** Render each scene to a separate texture, then composite with a fullscreen quad shader. *Rejected for V1:* Correct but complex. Adds a post-processing pass, two render targets, and a composite shader. Overkill for V1's three transition types (cut, crossfade, dip_to_black). Can be added later if visual quality demands it.
3. **Chosen approach: Sequential multi-pass with `autoClear=false`:** Render pass A, then render pass B on top without clearing. The later pass's mesh opacity controls the blend. For crossfade: pass A at full mesh opacity but rendered first, pass B at its crossfade opacity rendered second. This produces acceptable visual blending because the second pass writes over the first proportionally to its opacity.

**Limitation:** This approach is approximate — it's not mathematically equivalent to a true alpha composite of two independent renders. For 0.5/0.5 crossfade, the result differs from a true 50%/50% blend because the second pass's depth writes interact with the first pass's pixels. However, for the short transition durations used in practice (0.5-1.0 seconds per seed Section 8.8), the visual difference is imperceptible. OBJ-068 (transition tuning) can evaluate whether render targets are needed.

### D3: Scene Groups Start Hidden

**Decision:** `setupScene()` adds the THREE.Group to the scene graph with `visible = false`. The group becomes visible only when referenced in a `renderFrame` pass.

**Rationale:** Prevents a newly-setup scene from flashing into the rendered output before the orchestrator is ready. The orchestrator sets up scene B while scene A is still actively rendering. Without hidden-by-default, the setup frame would show scene B's meshes at their full opacity.

### D4: All Camera Fields Required Per Pass

**Decision:** Each `RenderPass.camera` requires all three fields: position, lookAt, fov. There are no optional fields or "carry forward from previous frame" semantics.

**Rationale:** The page is a dumb renderer (OBJ-010 D1). It should not track camera state across frames. The orchestrator computes the complete camera state per-frame from the camera path presets (OBJ-006) and interpolation (OBJ-002/OBJ-007). Sending all three fields per pass eliminates an entire class of stale-state bugs. The cost is ~72 extra bytes per pass per frame — negligible.

### D5: Texture Loading is Blocking Within setupScene

**Decision:** `setupScene()` is an async operation that resolves only after all texture loads have completed (or failed). There is no separate "load textures" + "await textures" split.

**Rationale:** Simplifies the protocol. The orchestrator calls `setupScene()`, awaits it, checks the result for errors, then proceeds to rendering. For transitions, the orchestrator calls `setupScene()` for the next scene during a window when it has time — between frame renders or during a batch of non-transition frames. Texture preloading as a separate command is a performance optimization deferred per AP-05.

**Performance note:** For a 5-slot scene with 1920×1080 PNG textures, Three.js TextureLoader loads from file:// URLs in-process. Expected load time: 100-500ms per texture depending on file size. All textures load in parallel, so total setup time is bounded by the slowest texture, not the sum. This is acceptable for V1 — scene setup happens once per scene, not per frame.

### D6: Texture URL Resolution on the Page

**Decision:** The page handler resolves texture sources rather than requiring the Node side to pre-convert everything to file:// URLs.

**Rationale:** Keeps the Node-side protocol clean (pass file paths as strings) while handling the URL conversion in the only place that needs it (the page's TextureLoader). Absolute paths starting with '/' are the primary production path. Data URIs are supported for testing and inline assets.

### D7: Per-Slot Error Reporting, Not All-or-Nothing

**Decision:** If some textures fail to load, `setupScene()` still succeeds (returns a result), but `SceneSetupResult.success` is `false` and the individual `SlotLoadResult.status` values indicate which slots failed. The orchestrator decides whether to abort, retry, or render without those slots.

**Rationale:** A single missing texture shouldn't prevent the rest of the scene from being usable. The orchestrator (OBJ-035) can implement policy: "if any required slot fails, abort; if optional slots fail, warn and continue." The protocol reports; the orchestrator decides.

### D8: Structured Page Errors via PageErrorCode

**Decision:** Page-side errors follow a structured format with error codes, human-readable messages, and optional details. The Node-side `PageProtocol` catches these and wraps them in `PageProtocolError` instances.

**Rationale:** Structured errors enable programmatic handling by the orchestrator. The code field allows branching (e.g., `SCENE_NOT_FOUND` → setup the scene first; `TEXTURE_LOAD_FAILED` → retry or fallback). This is more robust than parsing error message strings.

### D9: renderComposite() is Separate from OBJ-010's renderFrame()

**Decision:** The page exposes `renderComposite()` as a new method (handling multi-pass rendering with scene group management), distinct from OBJ-010's existing `renderFrame()` (single-scene, single-camera). The protocol's `PageProtocol.renderFrame()` calls `window.depthkit.renderComposite()`.

**Rationale:** OBJ-010's `renderFrame()` operates on the bare scene/camera — it has no concept of scene groups, opacity, or multi-pass. Rather than modifying OBJ-010's existing method (which would change its contract), OBJ-011 adds a higher-level method that uses the renderer, scene, and camera from OBJ-010. `renderComposite()` internally manages group visibility and calls `renderer.render()` directly.

### D10: Fog is Per-Scene, Applied During Render

**Decision:** Each scene carries its own fog config (set during `setupScene`). During `renderComposite()`, the page applies the primary scene's fog (highest-opacity pass) to `scene.fog` before rendering. Fog is cleared between scenes if the next scene has no fog config.

**Rationale:** Different scenes can have different fog settings (a dark tunnel scene vs. an open sky scene). Fog is a scene-level property in Three.js (`scene.fog`), so it must be swapped during multi-pass rendering. The "primary scene" heuristic (highest opacity) ensures fog transitions smoothly during crossfades.

### D11: MeshBasicMaterial.fog Property for fogImmune

**Decision:** Three.js `MeshBasicMaterial` has a `fog` property (boolean, default `true`) that controls whether the material is affected by scene fog. For `fogImmune: true` slots, the material is created with `fog: false`.

**Rationale:** This is the Three.js-native way to exempt specific meshes from fog. No special rendering passes or separate groups needed. The MeshBasicMaterial.fog property is well-supported in both WebGL 1 and WebGL 2 (SwiftShader included).

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

### Multi-Pass Rendering (Transitions)

- [ ] **AC-16:** A `RenderFrameCommand` with two passes (sceneId A at opacity 0.5, sceneId B at opacity 0.5) renders both scenes composited into a single frame. The captured PNG is visually distinct from either scene rendered alone. (Proves multi-pass compositing works.)
- [ ] **AC-17:** A `RenderFrameCommand` with one pass at opacity 0.0 produces a frame that is the clear color (black by default). (Proves opacity=0 suppresses rendering.)
- [ ] **AC-18:** A `RenderFrameCommand` with one pass at opacity 1.0 produces the same output as if the scene were rendered without the multi-pass machinery. (Proves single-pass optimization path works.)
- [ ] **AC-19:** After multi-pass rendering, material opacities are restored to their original values. A subsequent single-pass render at opacity 1.0 produces the same output as before the multi-pass frame. (Proves no state leakage between frames.)

### Texture Loading

- [ ] **AC-20:** `setupScene()` with slots whose `textureSrc` is an absolute file path (e.g., `/path/to/image.png`) loads the texture successfully. `SlotLoadResult.status === 'loaded'` and `naturalWidth`/`naturalHeight` reflect the image dimensions.
- [ ] **AC-21:** `setupScene()` with a slot whose `textureSrc` is a nonexistent path returns `SlotLoadResult.status === 'error'` for that slot, with a descriptive `error` string. Other slots still load successfully.
- [ ] **AC-22:** `setupScene()` with a slot whose `textureSrc` is a base64 data URI loads the texture successfully.

### Scene Lifecycle

- [ ] **AC-23:** After `teardownScene()`, calling `setupScene()` with the same sceneId succeeds (fresh setup — ID can be reused).
- [ ] **AC-24:** Scenes set up but not referenced in any `renderFrame` pass do not appear in the captured frame (hidden by default via `visible=false`).
- [ ] **AC-25:** Multiple scenes can be set up simultaneously. `getActiveSceneIds()` returns all of them.

### Fog

- [ ] **AC-26:** A scene set up with `fog: { color: '#000000', near: 5, far: 30 }` applies Three.js fog during rendering. Meshes farther from the camera fade toward the fog color.
- [ ] **AC-27:** A slot with `fogImmune: true` renders at full brightness regardless of scene fog distance.
- [ ] **AC-28:** A scene without fog config does not apply fog.

### Protocol Types

- [ ] **AC-29:** All types in `protocol-types.ts` are JSON-serializable — no functions, no class instances, no TypeScript-only constructs. They can be passed through `JSON.parse(JSON.stringify(value))` without data loss.
- [ ] **AC-30:** `protocol-types.ts` re-exports `PageInitConfig`, `RendererInfo`, `FrameCameraState` from `page-types.ts` (OBJ-010).

## Edge Cases and Error Handling

### Scene Setup

| Scenario | Expected Behavior |
|---|---|
| `sceneId` is empty string | `PageProtocolError` with code `INVALID_COMMAND`: `"sceneId must be non-empty"` |
| `slots` is empty object `{}` | Succeeds — creates an empty scene group. `SceneSetupResult.success = true`, `slots = {}`. Valid for scenes with no images (e.g., a solid-color scene). |
| Slot with `textureSrc` pointing to a non-image file (e.g., `.txt`) | `SlotLoadResult.status = 'error'` with message describing the load failure. Mesh is created with a magenta fallback material so the slot's spatial position is visible (aids debugging). |
| Texture file is very large (e.g., 8192×8192) | Page handler checks against `gl.getParameter(gl.MAX_TEXTURE_SIZE)`. If texture exceeds the limit, `SlotLoadResult.status = 'error'` with message: `"Texture dimensions {w}x{h} exceed WebGL max texture size {max}"`. |
| `setupScene` called after `dispose()` | `PageProtocolError` with code `NOT_INITIALIZED`. |
| All texture loads fail | `SceneSetupResult.success = false`. All slots have `status: 'error'`. Scene group still exists (with magenta fallback meshes). Orchestrator decides whether to proceed or abort. |

### Frame Rendering

| Scenario | Expected Behavior |
|---|---|
| `passes` array has more than 2 entries | Allowed. Renders all passes in order. No artificial limit. |
| Pass `opacity` > 1.0 or < 0.0 | Clamped to [0.0, 1.0] by the page handler. No error. |
| Pass `opacity` is NaN | Treated as 0.0 (clamped). No error. |
| Two passes reference the same sceneId | Allowed. Scene renders twice with potentially different camera states/opacities. Unusual but not invalid (could create a double-exposure effect). |
| `renderFrame` called with scene that has failed textures | Renders with magenta fallback materials for failed slots. No error — the scene was set up, just with degraded textures. |
| `camera.fov` is 0 or negative | Passed to Three.js. Produces degenerate rendering. OBJ-004 (manifest validation) prevents this upstream. The protocol does not validate camera values. |
| `debug` field is omitted | No effect. Debug metadata is purely optional. |

### Scene Teardown

| Scenario | Expected Behavior |
|---|---|
| Teardown a scene that is currently referenced in a render pass | The teardown runs after the current `renderFrame` completes (protocol commands are sequential via `evaluate()`). The scene is removed. Next `renderFrame` referencing this scene will throw `SCENE_NOT_FOUND`. |
| Teardown the only active scene, then call `renderFrame` referencing it | `PageProtocolError` with code `SCENE_NOT_FOUND`. |
| `dispose()` with active scenes | All scenes are torn down first, then the renderer is disposed. Equivalent to calling `teardownScene` for each active scene, then `dispose()`. |

### Bridge/Page Errors

| Scenario | Expected Behavior |
|---|---|
| Bridge not launched when protocol method is called | `PuppeteerBridge.evaluate()` throws its own "not launched" error (per OBJ-009 AC-16). This propagates through `PageProtocol` unmodified. |
| Page crashes during `setupScene` (e.g., OOM from textures) | Bridge's `pageerror` handler fires. Next protocol call rejects with bridge's stored error (per OBJ-009 D13). |
| WebGL context lost during rendering | Page-side handler catches the context loss event and throws with code `WEBGL_ERROR`. Protocol propagates as `PageProtocolError`. |

## Test Strategy

### Unit Tests: `test/unit/protocol-types.test.ts`

1. **Serialization round-trip:** Construct each protocol type (SceneSetupConfig, RenderFrameCommand, etc.) as a plain object, run through `JSON.parse(JSON.stringify(...))`, verify no data loss.
2. **PageProtocolError:** Construct with a PageErrorInfo object, verify `instanceof Error`, verify `code`, `message`, `details` properties.

### Integration Tests: `test/integration/page-protocol.test.ts`

These tests launch real headless Chromium via PuppeteerBridge and exercise the full protocol. Each test creates a bridge, launches it, creates a PageProtocol, runs commands, and verifies results. Tests should use small viewports (e.g., 320×240) and simple test textures (solid-color PNGs, ≤100×100) for speed.

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
11. `getActiveSceneIds()` reflects setup/teardown state.

**Frame rendering tests:**
12. Single-pass render: setup scene, render one frame, capture PNG, verify non-black.
13. Camera state is applied: render same scene with two different camera positions, capture both frames, verify they differ (pixel comparison or basic check).
14. Multi-pass render (transition): setup two scenes with different colored meshes, render with 0.5/0.5 opacity, capture frame, verify it differs from either scene alone.
15. Opacity 0.0: render at zero opacity, verify frame is the clear color (black).
16. Opacity 1.0 single-pass: verify same result as rendering without multi-pass overhead.
17. State restoration: render multi-pass frame, then render single-pass frame at 1.0, verify single-pass output is identical to a fresh single-pass render (no opacity leakage).
18. Unknown sceneId in pass: throws `SCENE_NOT_FOUND`.
19. Empty passes array: throws `INVALID_COMMAND`.

**Scene teardown tests:**
20. Teardown removes scene. `getActiveSceneIds()` no longer includes it.
21. Teardown returns `meshesRemoved > 0`, `texturesDisposed > 0`.
22. After teardown, rendering with that sceneId throws `SCENE_NOT_FOUND`.
23. After teardown, `setupScene()` with same sceneId succeeds (ID reuse).
24. Teardown unknown sceneId throws `SCENE_NOT_FOUND`.

**Dispose tests:**
25. `dispose()` tears down all scenes and disposes renderer. `getRendererInfo()` returns `initialized: false`.
26. `dispose()` is idempotent.
27. After `dispose()`, `initialize()` succeeds again (re-entrant lifecycle).

**Fog tests:**
28. Scene with fog config renders differently than scene without fog (distant meshes fade).
29. fogImmune slot renders at full brightness even with scene fog.

**Determinism tests (TC-06):**
30. Same setup + same renderFrame command produces identical PNG buffers across two runs.

### Relevant Testable Claims

- **TC-02** (render performance): Protocol overhead per frame (evaluate round-trip) is measurable. Log it.
- **TC-05** (tunnel geometry): When OBJ-018 is implemented, the protocol can set up and render a tunnel geometry.
- **TC-06** (deterministic output): Test 30 verifies determinism through the protocol.
- **TC-10** (transitions mask seams): Tests 14-17 verify multi-pass compositing works.

## Integration Points

### Depends on

| Dependency | What OBJ-011 uses |
|---|---|
| **OBJ-009** (Puppeteer bridge) | `PuppeteerBridge` class — `evaluate()` as the transport for all protocol commands, `page` property for advanced page event handling. OBJ-011 does NOT use `captureFrame()` — that's the orchestrator's concern. |
| **OBJ-010** (Page shell) | `window.depthkit` API — `init()`, `dispose()`, `isInitialized()`, `getRendererInfo()`, `renderFrame()`, `renderer`, `scene`, `camera` properties. OBJ-011 extends this namespace with `setupScene()`, `renderComposite()`, `teardownScene()`, `getActiveSceneIds()`. `PageInitConfig`, `RendererInfo`, `FrameCameraState` types from `page-types.ts`. |
| **OBJ-005** (Geometry types) | `PlaneSlot` interface informs `SlotSetup` structure (position, rotation, size, transparent, renderOrder, fogImmune). `FogConfig` interface is mirrored in protocol types. OBJ-011 does NOT import OBJ-005 at runtime — the orchestrator (OBJ-035/OBJ-036) resolves geometry definitions and constructs `SceneSetupConfig` objects using OBJ-005 data, which OBJ-011 sends to the page as plain JSON. |

### Consumed by

| Downstream | How it uses OBJ-011 |
|---|---|
| **OBJ-012** (FFmpeg encoder) | Indirectly — OBJ-012 receives PNG buffers from `bridge.captureFrame()` after OBJ-011's `renderFrame()` has rendered the frame. OBJ-012 does not call OBJ-011 directly. |
| **OBJ-035** (Orchestrator) | The primary consumer. Composes OBJ-009 (bridge + clock), OBJ-011 (protocol), and OBJ-012 (encoder) into the render loop: `protocol.initialize()` → for each scene: `protocol.setupScene()` → for each frame: `protocol.renderFrame()` + `bridge.captureFrame()` → pipe to FFmpeg → `protocol.teardownScene()` → `protocol.dispose()`. |
| **OBJ-036** (Scene sequencer) | Constructs `SceneSetupConfig` objects from manifest scenes + geometry definitions (OBJ-005), then passes them to `protocol.setupScene()`. Constructs `RenderFrameCommand` objects per frame with camera state from OBJ-006/OBJ-007 interpolation. |
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
                               #          teardownScene, getActiveSceneIds
                               #          to window.depthkit
```

## Open Questions

### OQ-A: Should multi-pass compositing use render targets instead of autoClear toggling?

The spec's D2 chooses sequential multi-pass rendering with `autoClear=false` for simplicity. This produces approximate blending — the second pass's depth writes interact with the first pass's pixels. For short transitions (0.5-1.0s), this is likely imperceptible. However, if OBJ-068 (transition tuning) finds visual artifacts, the page handler should be upgraded to render each pass to a `THREE.WebGLRenderTarget` and composite them with a fullscreen quad using proper alpha blending. The protocol types (`RenderFrameCommand`, `RenderPass`) would not change — only the page-side compositing implementation would change.

### OQ-B: Should setupScene support texture load timeouts?

Currently, `setupScene` waits indefinitely for texture loads to resolve. If a texture hangs (e.g., network URL that never responds), the protocol blocks forever. A timeout (e.g., 30 seconds per texture) could be added as a field in `SceneSetupConfig`. For V1, file:// URLs are the primary path and load near-instantly, so timeouts are less critical. But if HTTP URLs are used for testing or integration, a timeout becomes important. Recommendation: defer to OBJ-035 if needed — the orchestrator can wrap `protocol.setupScene()` in a `Promise.race()` with a timeout.

### OQ-C: Should the protocol support per-frame plane transforms?

The current spec has static plane transforms set at scene setup time. Seed OQ-01 asks about per-frame opacity animation. If per-frame plane state updates are needed (position, opacity, scale), the protocol would need a `updateSlot()` command or an extension to `RenderPass`. This is deferred to OBJ-044 (per-frame opacity animation). The current protocol design does not preclude adding this — a new command type can be added without breaking existing commands.

### OQ-D: Should the protocol support adding/removing individual slots after scene setup?

Currently, a scene's slots are fixed at setup time. If the orchestrator needs to add or remove a slot mid-scene (e.g., a foreground element that appears partway through), it would need to tear down and re-setup the entire scene. An `addSlot()` / `removeSlot()` command pair could be added. Deferred — V1 scenes have fixed slot assignments.

### OQ-E: Magenta fallback material for failed textures — is this the right default?

The spec proposes creating a mesh with a magenta `MeshBasicMaterial` when a texture fails to load, so the slot's spatial position is visible for debugging. An alternative is to not create the mesh at all (skip failed slots). Magenta is more debuggable; skipping is cleaner for production. The orchestrator can make this decision based on `SceneSetupResult.success` — if it proceeds despite failures, the magenta meshes indicate where the problems are. If it aborts, the fallback material is never seen.

---

I believe this specification is complete and precise enough for an implementer to build from. It covers:
- Every message type crossing the boundary (init, setupScene, renderFrame/renderComposite, teardownScene, dispose, getRendererInfo, getActiveSceneIds)
- The Node-side wrapper class with full error handling
- The page-side extensions with implementation contracts
- Multi-pass rendering for transitions
- Texture loading with per-slot error reporting
- Fog handling with fogImmune support
- All edge cases I can identify

I'd like the Challenger to verify and evaluate this proposal. Are there gaps, ambiguities, or constraint violations I've missed?

---

## Round 2 — spec_challenger

I've carefully reviewed the proposed OBJ-011 specification against the seed, dependency specs (OBJ-009, OBJ-010, OBJ-005), and downstream consumers. Here's my assessment.

---

## Points of Agreement

These aspects are sound and well-designed:

1. **PageProtocol wrapping bridge without owning it (D1):** Clean separation. The orchestrator needs direct bridge access for `captureFrame()`, which is outside the protocol's concern. ✓
2. **Scene groups start hidden (D3):** Prevents flash-on-setup artifacts. ✓
3. **All camera fields required per pass (D4):** Eliminates stale-state bugs. Cost is negligible. ✓
4. **Per-slot error reporting (D7):** "Protocol reports; orchestrator decides" is the right policy boundary. ✓
5. **Structured error codes (D8):** Enables programmatic handling. ✓
6. **`renderComposite()` as a new method, not overriding OBJ-010's `renderFrame()` (D9):** Respects OBJ-010's contract. ✓
7. **Texture loading blocking within `setupScene` (D5):** Simple and sufficient for V1. ✓
8. **Overall scope discipline:** Stays within OBJ-011's boundaries. Doesn't bleed into OBJ-035 (orchestrator), OBJ-006 (camera paths), or OBJ-005 (geometry definitions). ✓

---

## Issues

### Issue 1 — CRITICAL: Multi-pass compositing opacity math is self-contradictory and underspecified

The spec contradicts itself on how crossfade opacity works:

- **D2** says: *"For crossfade: pass A at full mesh opacity but rendered first, pass B at its crossfade opacity rendered second."*
- **AC-16** says: *"sceneId A at opacity 0.5, sceneId B at opacity 0.5"*
- The `RenderPass` interface gives BOTH passes their own `opacity` field.

These can't all be true. If pass A has opacity 0.5 and pass B has opacity 0.5 with `autoClear=false` and `NormalBlending`:
- After pass A: 50% scene-A + 50% black
- After pass B: 50% scene-B + 50% × (50% scene-A + 50% black) = 50% B + 25% A + 25% black

That's NOT a 50/50 crossfade — it's a 2:1 ratio favoring B. To get a true 50/50 blend, you'd need pass A at opacity 1.0 then pass B at opacity 0.5, producing: 50% B + 50% A. But that's not what the AC says.

The spec acknowledges this is "approximate" but doesn't give the implementer the actual algorithm. An implementer needs to know: **for a crossfade at progress `p` (0→1), what opacity values should passes A and B receive?**

**Proposed fix:** Specify the exact compositing algorithm in the page-side `renderComposite` contract. My recommendation:

```
For multi-pass compositing using autoClear=false with NormalBlending:
- Passes are rendered in order.
- Pass 1 (outgoing scene): opacity = 1.0
- Pass 2 (incoming scene): opacity = p (crossfade progress)
- Result: (1-p) × sceneA + p × sceneB (approximation via
  NormalBlending over-paint, exact for opaque scenes).

The orchestrator (OBJ-036) is responsible for computing the
correct opacity values for each pass given the transition type
and progress. The protocol transmits them as-is.
```

Also update AC-16 to use the actual opacity values that produce a visible blend (e.g., pass A opacity 1.0, pass B opacity 0.5), and document that the compositing is order-dependent (later passes paint over earlier ones).

### Issue 2 — MAJOR: Incorrect claim that MeshBasicMaterial is unaffected by fog

In the `SlotSetup.fogImmune` JSDoc comment:

> "MeshBasicMaterial is unaffected by fog anyway in Three.js"

This is **factually wrong**. Three.js `MeshBasicMaterial` IS affected by scene fog when its `fog` property is `true` (the default). The Three.js source and documentation explicitly show fog integration in the `MeshBasicMaterial` shader. This incorrect comment would mislead an implementer into thinking `fogImmune` is a no-op.

**Proposed fix:** Replace the parenthetical with:

> "NOTE: In V1, all materials are MeshBasicMaterial (unlit, per OBJ-010 D8). MeshBasicMaterial IS affected by Three.js scene fog when its material `fog` property is `true` (the default). For fogImmune slots, the material is created with `fog: false`, exempting it from distance-based fading."

This aligns with D11's correct statement.

### Issue 3 — MAJOR: Fog management during multi-pass rendering is underspecified

D10 says: *"the page applies the primary scene's fog (highest-opacity pass) to `scene.fog` before rendering."*

Two problems:

**3a.** During a 50/50 crossfade, both passes have equal opacity. Which scene's fog wins? The spec has no tie-breaking rule.

**3b.** Is fog applied once before all passes, or switched between passes? If scene A has dark fog and scene B has no fog, and we're crossfading:
- Option X: Apply scene A's fog, render both passes → scene B's distant meshes incorrectly fade to A's fog color
- Option Y: Switch fog per pass → fog appearance changes abruptly between consecutive passes in the same frame

Neither is ideal, and the spec doesn't pick one.

**Proposed fix:** Specify explicitly:

```
Fog algorithm during renderComposite:
1. Determine primary scene: the pass with the highest opacity.
   Tie-break: first pass in order wins.
2. Set scene.fog from the primary scene's fog config (or null).
3. Fog remains constant for ALL passes in this frame.
4. After all passes, fog is NOT restored — it persists until
   the next renderComposite call sets it.
```

This is simple, deterministic, and produces acceptable results because during transitions, the outgoing scene's fog dominates in the first half (when it has higher opacity) and the incoming scene's fog dominates in the second half. Add an AC for the tie-break.

### Issue 4 — MAJOR: `FrameCameraState` re-export creates a type confusion hazard

`protocol-types.ts` re-exports `FrameCameraState` (all-optional fields) from OBJ-010, but `RenderPass.camera` uses an inline type with all-required fields. A consumer importing from `protocol-types.ts` would see both types and could mistakenly use `FrameCameraState` for render pass construction, leading to runtime errors when fields are missing.

**Proposed fix:** Either:
- **(a)** Do NOT re-export `FrameCameraState` from `protocol-types.ts` — it's an OBJ-010 type used by OBJ-010's `renderFrame()`, not by OBJ-011's protocol.
- **(b)** Define a `RequiredCameraState` type in `protocol-types.ts` and use it in `RenderPass`:

```typescript
export interface RequiredCameraState {
  position: [number, number, number];
  lookAt: [number, number, number];
  fov: number;
}
```

I recommend (b) — it names the concept and makes the requirement explicit.

### Issue 5 — MAJOR: `FogConfig` is duplicated instead of imported from OBJ-005

`protocol-types.ts` defines its own `FogConfig` that's structurally identical to OBJ-005's `FogConfig`. The comment says "repeated here as a protocol type for serialization clarity." But OBJ-005's `FogConfig` is already a plain interface with no Three.js dependencies — it's in `src/scenes/geometries/types.ts`, a pure types module. Duplicating it creates a maintenance risk: if OBJ-005's `FogConfig` gains a field (e.g., `density` for `FogExp2`), the protocol copy silently diverges.

**Proposed fix:** Import `FogConfig` from OBJ-005 and re-export it:

```typescript
import type { FogConfig } from '../scenes/geometries/types.js';
export type { FogConfig };
```

If there's a concern about protocol types depending on spatial types, document why the dependency is acceptable (both are pure type modules with no rendering dependencies).

### Issue 6 — MINOR: Texture URL resolution assumes POSIX paths

The resolution rules say "Paths starting with '/' are converted to 'file://' + path." This is Linux/macOS specific. Windows absolute paths start with a drive letter (e.g., `C:\`).

**Proposed fix:** Add a note:

> "Path resolution assumes POSIX filesystem paths (Linux/macOS). The depthkit engine targets Linux VPS and Docker containers (seed C-08, C-11). Windows paths are not supported."

### Issue 7 — MINOR: `dispose()` implementation path unclear

`PageProtocol.dispose()` says "All active scenes are torn down implicitly." But how? Does it:
- (a) Call `teardownScene()` N times via evaluate(), then call `window.depthkit.dispose()` once?
- (b) Call a single page-side function that does everything?

Option (a) is N+1 `evaluate()` round-trips. Option (b) is 1 round-trip. For correctness they're equivalent, but for an implementer, the spec should specify which approach.

**Proposed fix:** Add to the `dispose()` JSDoc:

> "Implementation: calls a single page-side function that iterates active scenes, disposes their resources, then calls window.depthkit.dispose(). This is a single evaluate() call, not N+1 calls."

### Issue 8 — MINOR: No AC for `getActiveSceneIds()` ordering guarantee

`getActiveSceneIds()` returns `string[]` but doesn't specify ordering. Is it insertion order? Alphabetical? Arbitrary?

**Proposed fix:** Specify "Returns scene IDs in setup order" or "Returns scene IDs in no guaranteed order." If no guarantee, state it. I'd recommend insertion order since it's natural for a Map-backed registry.

### Issue 9 — MINOR: Missing AC for `SceneSetupConfig` with empty `sceneId`

The edge case table says empty `sceneId` returns `INVALID_COMMAND`, but there's no AC covering it. Add:

> **AC-31:** `protocol.setupScene({ sceneId: '', slots: {} })` throws `PageProtocolError` with `code: 'INVALID_COMMAND'`.

### Issue 10 — MINOR: `http://` and `https://` textureSrc is allowed but may break determinism

`SlotSetup.textureSrc` allows http/https URLs. Network-loaded textures could timeout, fail, or return different content on different runs (CDN cache, image processing, etc.), violating C-05 (deterministic output).

**Proposed fix:** Add a note in `SlotSetup.textureSrc` docs:

> "Production use should prefer absolute file paths or data URIs for deterministic rendering (C-05). HTTP/HTTPS URLs are supported for development/testing but introduce network dependency that may affect reproducibility."

---

## Summary

- **1 Critical issue:** Multi-pass compositing opacity math
- **4 Major issues:** Incorrect fog comment, fog during multi-pass, FrameCameraState re-export confusion, FogConfig duplication
- **5 Minor issues:** POSIX paths, dispose strategy, getActiveSceneIds ordering, empty sceneId AC, http texture warning

Please revise and I'll verify the fixes.

---

## Round 3 — spec_author

Thank you for the thorough review. All 10 issues are valid. Here's my revised specification with each issue addressed.

---

# Revised Specification: OBJ-011 — Puppeteer-to-Page Message Protocol

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
 * For crossfade transitions at progress p (0→1, where 0=fully A, 1=fully B):
 *   passes = [
 *     { sceneId: A, opacity: 1.0, camera: ... },  // outgoing scene, full opacity
 *     { sceneId: B, opacity: p,   camera: ... },   // incoming scene, increasing opacity
 *   ]
 *   Visual result: B at p% over A → as p increases, B progressively
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
   *   2. Apply scene fog (if configured).
   *   3. Apply camera state.
   *   4. renderer.render(scene, camera) with autoClear=true (normal).
   *
   * Multi-pass or any pass with opacity < 1.0 (composite path):
   *   1. renderer.autoClear = false
   *   2. renderer.clear() (manual clear to the clear color)
   *   3. Determine primary scene: the pass with the highest opacity.
   *      Tie-break: first pass in order wins.
   *   4. Set scene.fog from the primary scene's fog config (or null
   *      if the primary scene has no fog). Fog remains constant for
   *      ALL passes in this frame.
   *   5. For each pass in order:
   *      a. Set only this pass's scene group visible=true;
   *         all other scene groups set to visible=false.
   *      b. Save original material opacities for all meshes in the group.
   *      c. Set material.opacity = originalOpacity * pass.opacity
   *         on all meshes. Set material.transparent = true if
   *         pass.opacity < 1.0 (required for Three.js opacity to take effect).
   *      d. Apply camera state (position, lookAt, fov + updateProjectionMatrix).
   *      e. renderer.render(scene, camera)
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
   *   - Apply scene fog from this scene's config (or null)
   *   - Apply camera state (position, lookAt, fov + updateProjectionMatrix)
   *   - renderer.render(scene, camera) with autoClear=true
   *
   * Multi-pass or reduced-opacity (composite path):
   *   - renderer.autoClear = false
   *   - renderer.clear()
   *   - Determine primary scene: pass with highest opacity;
   *     tie-break: first pass in order wins.
   *   - Set scene.fog from primary scene's fog config (or null).
   *     Fog remains constant for ALL passes in this frame.
   *   - For each pass in order:
   *     a. Set only this pass's scene group visible=true
   *     b. Save original material opacity and transparent flag
   *        for all meshes in the group
   *     c. Set material.opacity = originalOpacity * pass.opacity
   *        on all meshes. If pass.opacity < 1.0, set
   *        material.transparent = true.
   *     d. Apply camera state
   *     e. renderer.render(scene, camera)
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

**Rationale:** Separation of concerns. The bridge is a transport layer; the protocol is a domain layer. The orchestrator needs direct bridge access for `captureFrame()` (which is not a protocol concern — it's a pixel extraction concern for FFmpeg piping). Ownership nesting: orchestrator → bridge + protocol → page.

### D2: Multi-Pass Compositing via Sequential Over-Paint

**Decision:** Transitions are expressed as multi-pass render commands. Passes are rendered sequentially with `renderer.autoClear = false`. Each pass paints over the previous one using Three.js NormalBlending with per-material opacity scaling.

**Compositing algorithm for crossfade at progress `p` (0→1):**
- Pass 1 (outgoing scene A): opacity = 1.0
- Pass 2 (incoming scene B): opacity = p

Visual result: as `p` increases from 0 to 1, scene B progressively covers scene A. At p=0 only A is visible. At p=1 only B is visible. At p=0.5, the result is approximately 50/50.

This is an approximation — not a true alpha composite of two independent renders. The exact math for two passes with NormalBlending:
- After pass 1: pixel = A_color × A_opacity (over clear color)
- After pass 2: pixel = B_color × B_opacity + previous_pixel × (1 - B_opacity)

For opaque scenes (A_opacity=1.0): result = B×p + A×(1-p), which IS a correct linear blend. The approximation only manifests when pass 1 has opacity < 1.0 (e.g., dip_to_black where both passes have reduced opacity), or when pass 1 contains transparent meshes whose alpha channels interact with pass 2.

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

**Rationale:** Simplifies the protocol. For a 5-slot scene with 1920×1080 PNG textures via file:// URLs, expected load time is 100-500ms per texture, all loading in parallel. Total setup time bounded by the slowest texture. Acceptable for V1.

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

**Rationale:** During crossfades, the outgoing scene (pass 1, opacity 1.0) is always the primary scene in the first half of the transition (its opacity is highest). The incoming scene becomes primary only when its opacity exceeds the outgoing scene's — which under the crossfade algorithm happens when p > 1.0 (never, since pass 1 is always 1.0). Therefore for crossfades, the outgoing scene's fog dominates throughout. This is visually acceptable because the incoming scene's visual contribution increases gradually while the fog environment remains consistent. The transition is short (0.5-1.0s), and abrupt fog changes would be more jarring than a slight inconsistency.

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
| Texture file is very large (e.g., 8192×8192) | Page handler checks against `gl.getParameter(gl.MAX_TEXTURE_SIZE)` after loading. If texture exceeds the limit, `SlotLoadResult.status = 'error'` with message: `"Texture dimensions {w}x{h} exceed WebGL max texture size {max}"`. Mesh created with magenta fallback. |
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

These tests launch real headless Chromium via PuppeteerBridge and exercise the full protocol. Each test creates a bridge, launches it, creates a PageProtocol, runs commands, and verifies results. Tests should use small viewports (e.g., 320×240) and simple test textures (solid-color PNGs, ≤100×100) for speed.

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

**Scene teardown tests:**
22. Teardown removes scene. `getActiveSceneIds()` no longer includes it.
23. Teardown returns `meshesRemoved > 0`, `texturesDisposed > 0`.
24. After teardown, rendering with that sceneId throws `SCENE_NOT_FOUND`.
25. After teardown, `setupScene()` with same sceneId succeeds (ID reuse).
26. Teardown unknown sceneId throws `SCENE_NOT_FOUND`.

**Dispose tests:**
27. `dispose()` tears down all scenes and disposes renderer. `getRendererInfo()` returns `initialized: false`.
28. `dispose()` is idempotent.
29. After `dispose()`, `initialize()` succeeds again (re-entrant lifecycle).

**Fog tests:**
30. Scene with fog config: render a mesh at far distance, capture frame. Compare with same mesh rendered without fog. Fog version should be darker/faded.
31. fogImmune slot renders at full brightness even with scene fog.
32. During multi-pass render, fog comes from the primary scene (highest opacity, first wins on tie).

**Determinism tests (TC-06):**
33. Same setup + same renderFrame command produces identical PNG buffers across two consecutive runs.

### Relevant Testable Claims

- **TC-02** (render performance): Protocol overhead per frame (evaluate round-trip) is measurable. Log it.
- **TC-06** (deterministic output): Test 33 verifies determinism through the protocol.
- **TC-10** (transitions mask seams): Tests 15-18, 21 verify multi-pass compositing works.

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
| **OBJ-035** (Orchestrator) | The primary consumer. Composes OBJ-009 (bridge + clock), OBJ-011 (protocol), and OBJ-012 (encoder) into the render loop: `protocol.initialize()` → for each scene: `protocol.setupScene()` → for each frame: `protocol.renderFrame()` + `bridge.captureFrame()` → pipe to FFmpeg → `protocol.teardownScene()` → `protocol.dispose()`. |
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

The spec's D2 chooses sequential multi-pass rendering with `autoClear=false`. For V1's three transition types with opaque scenes, this produces mathematically correct crossfades. If OBJ-068 (transition tuning) finds visual artifacts with transparent scenes or exotic transitions, the page handler can be upgraded to render-target-based compositing. The protocol types (`RenderFrameCommand`, `RenderPass`) would not change — only the page-side implementation.

### OQ-B: Should setupScene support texture load timeouts?

Currently, `setupScene` waits indefinitely for texture loads. For V1, file:// URLs load near-instantly, so timeouts are less critical. If HTTP URLs are used, the orchestrator can wrap `protocol.setupScene()` in a `Promise.race()` with a timeout.

### OQ-C: Should the protocol support per-frame plane transforms?

The current spec has static plane transforms set at scene setup time. If per-frame plane state updates are needed (position, opacity, scale), the protocol would need an `updateSlots()` command or an extension to `RenderPass`. Deferred to OBJ-044 (per-frame opacity animation). The current protocol design does not preclude adding this.

### OQ-D: Should the protocol support adding/removing individual slots after scene setup?

Currently, a scene's slots are fixed at setup time. An `addSlot()` / `removeSlot()` command pair could be added later. Deferred — V1 scenes have fixed slot assignments.

### OQ-E: Magenta fallback material for failed textures — is this the right default?

The spec proposes magenta `MeshBasicMaterial` (0xff00ff) when textures fail, preserving the slot's spatial position for debugging. The alternative is skipping failed slots entirely. The orchestrator can act on `SceneSetupResult.success` to abort if needed. The magenta fallback is more debuggable; if production wants clean failure, the orchestrator aborts on `success: false`.

---

I believe this revision addresses all 10 issues raised:

1. **Critical (compositing math):** D2 now specifies the exact algorithm — pass A at 1.0, pass B at p — with the mathematical justification that this produces a correct linear blend for opaque scenes. AC-17 updated to use these correct values. AC-21 added to prove order-dependence.
2. **Major (fog comment):** SlotSetup.fogImmune docs corrected — MeshBasicMaterial IS affected by fog.
3. **Major (fog during multi-pass):** D10 specifies: highest opacity pass = primary scene, first pass wins ties, fog constant for all passes in a frame.
4. **Major (FrameCameraState re-export):** D13 + new `RequiredCameraState` type. `FrameCameraState` is NOT re-exported. AC-34 added.
5. **Major (FogConfig duplication):** D12 — imported from OBJ-005, not duplicated. AC-33 updated.
6. **Minor (POSIX paths):** D6 + SlotSetup.textureSrc docs + edge case for relative paths.
7. **Minor (dispose strategy):** D14 + explicit JSDoc on `dispose()` — single evaluate() call.
8. **Minor (getActiveSceneIds ordering):** D15 — insertion order, documented in JSDoc.
9. **Minor (empty sceneId AC):** AC-16 added.
10. **Minor (http texture determinism):** Warning added to SlotSetup.textureSrc docs.

Challenger, please verify these fixes and let me know if any issues remain.

---

## Round 4 — spec_challenger

I've verified all 10 fixes from Round 2. Every one is structurally present and correct in the revised spec. Well done. Now let me check for issues introduced by the revisions or previously missed.

---

## Verification of Round 2 Fixes

1. ✅ **Compositing math (Critical):** D2 now specifies Pass A at 1.0, Pass B at p, with mathematical proof for opaque scenes. AC-17/AC-21 updated.
2. ✅ **Fog comment:** Corrected in SlotSetup.fogImmune docs.
3. ✅ **Fog multi-pass:** D10 specifies primary scene = highest opacity, first-pass tie-break, constant fog per frame. AC-31 added.
4. ✅ **FrameCameraState:** D13 defines RequiredCameraState. FrameCameraState NOT re-exported. AC-34 added.
5. ✅ **FogConfig:** D12 imports from OBJ-005. AC-33 updated.
6. ✅ **POSIX paths:** D6 + docs + edge case for unsupported formats.
7. ✅ **dispose():** D14 specifies single evaluate() call. `disposeAll()` added page-side.
8. ✅ **getActiveSceneIds ordering:** D15, insertion order.
9. ✅ **Empty sceneId AC:** AC-16 added.
10. ✅ **HTTP texture warning:** Added to SlotSetup.textureSrc docs.

---

## New Issue: Depth Buffer Interaction Between Multi-Pass Renders

### Issue 11 — CRITICAL: Depth buffer from pass 1 corrupts pass 2 in multi-pass compositing

The renderComposite composite path algorithm (step 2) calls `renderer.clear()` once at the start, then renders multiple passes WITHOUT clearing the depth buffer between them. This breaks crossfade transitions.

Here's why:

1. `renderer.clear()` clears both color buffer and depth buffer.
2. Pass 1 (scene A, opacity 1.0) renders — writes colors AND depth values.
3. Pass 2 (scene B, opacity 0.5) renders — Three.js's default depth function is `GL_LESS`.
4. Scene B's backdrop at z=-30 occupies the same screen pixels as Scene A's backdrop at z=-30. Since the depth is NOT strictly less than what pass 1 wrote, **pass 2's fragments are rejected by the depth test**. The crossfade produces only scene A's colors at those pixels.

Even if the scenes have meshes at slightly different Z positions, the interactions are unpredictable — some of pass 2's fragments pass the depth test, others don't, creating visible artifacts (holes/stripes in the blend).

**Proposed fix:** Add a depth buffer clear between each pass. Update the composite path algorithm:

```
5. For each pass in order:
   a. Clear the DEPTH BUFFER only (renderer.clearDepth()) —
      preserving the color buffer from previous passes.
   b. Set only this pass's scene group visible=true;
      all other scene groups set to visible=false.
   c. Save original material opacities...
   [rest unchanged]
```

And update D2's compositing model description accordingly. This ensures each pass renders with a fresh depth buffer, so its own meshes depth-sort correctly against each other, while the color from previous passes is preserved and painted over by the new pass via alpha blending.

Add an AC:

> **AC-35:** During multi-pass rendering, each pass's depth buffer is independent — meshes in pass 2 are not depth-rejected by meshes in pass 1, even if they occupy the same Z positions.

---

That's the only remaining issue. Everything else in the revised spec is solid.

---

## Round 5 — spec_author

Excellent catch on Issue 11. The depth buffer interaction is a real Three.js rendering bug that would completely break crossfade transitions. Here's the targeted fix.

---

## Revision for Issue 11: Depth Buffer Clear Between Passes

### Changes to the `renderComposite()` composite path algorithm

In the **PageProtocol.renderFrame() JSDoc** and the **page-side renderComposite() contract**, the composite path step 5 is updated:

**Before (broken):**
```
5. For each pass in order:
   a. Set only this pass's scene group visible=true;
      all other scene groups set to visible=false.
   b. Save original material opacities...
   ...
```

**After (fixed):**
```
5. For each pass in order:
   a. Clear the depth buffer only: renderer.clearDepth().
      This preserves the color buffer from previous passes
      while giving this pass a fresh depth buffer so its
      own meshes depth-sort correctly against each other
      and are not rejected by depth values from earlier passes.
   b. Set only this pass's scene group visible=true;
      all other scene groups set to visible=false.
   c. Save original material opacities for all meshes in the group.
   d. Set material.opacity = originalOpacity * pass.opacity
      on all meshes. Set material.transparent = true if
      pass.opacity < 1.0.
   e. Apply camera state (position, lookAt, fov + updateProjectionMatrix).
   f. renderer.render(scene, camera)
```

### Changes to D2

Add to the end of D2's compositing algorithm description:

> **Depth buffer handling:** Between each pass, `renderer.clearDepth()` is called to clear the depth buffer while preserving the color buffer. Without this, pass 2's fragments would be rejected by the depth test against pass 1's depth values — meshes at the same Z position in both scenes would fail `GL_LESS`, causing pass 2 to be invisible at those pixels. Clearing the depth buffer per-pass ensures each pass depth-sorts its own meshes correctly while painting over the color from previous passes via alpha blending.

### New acceptance criterion

> **AC-35:** During multi-pass rendering, each pass has an independent depth buffer — meshes in pass 2 are not depth-rejected by meshes in pass 1, even if they occupy identical Z positions. Verified by: setting up two scenes with identically-positioned meshes (same slot positions) but different colored textures, rendering [A at 1.0, B at 0.5], and confirming that the captured frame shows a blend of both colors (not just A's color).

---

## Complete Updated Sections

For clarity, here are the three sections as they should appear in the final spec with the depth buffer fix integrated:

### Updated PageProtocol.renderFrame() JSDoc (in page-protocol.ts)

```typescript
  /**
   * Render a single output frame with one or more passes.
   *
   * Compositing algorithm (sequential over-paint with autoClear=false):
   *
   * Single-pass at opacity 1.0 (fast path):
   *   1. Set only the referenced scene group visible=true.
   *   2. Apply scene fog (if configured).
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
```

### Updated page-side renderComposite() contract

```typescript
  /**
   * Render a composited frame from one or more passes.
   *
   * Single-pass at opacity 1.0 (fast path):
   *   - Set referenced scene group visible=true
   *   - Set all other scene groups visible=false
   *   - Apply scene fog from this scene's config (or null)
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
```

### Updated D2 (full replacement)

**D2: Multi-Pass Compositing via Sequential Over-Paint**

**Decision:** Transitions are expressed as multi-pass render commands. Passes are rendered sequentially with `renderer.autoClear = false`. Each pass paints over the previous one using Three.js NormalBlending with per-material opacity scaling. Between each pass, `renderer.clearDepth()` clears the depth buffer while preserving the color buffer.

**Compositing algorithm for crossfade at progress `p` (0→1):**
- Pass 1 (outgoing scene A): opacity = 1.0
- Pass 2 (incoming scene B): opacity = p

Visual result: as `p` increases from 0 to 1, scene B progressively covers scene A. At p=0 only A is visible. At p=1 only B is visible. At p=0.5, the result is approximately 50/50.

This is an approximation — not a true alpha composite of two independent renders. The exact math for two passes with NormalBlending:
- After pass 1: pixel = A_color × A_opacity (over clear color)
- After pass 2: pixel = B_color × B_opacity + previous_pixel × (1 - B_opacity)

For opaque scenes (A_opacity=1.0): result = B×p + A×(1-p), which IS a correct linear blend. The approximation only manifests when pass 1 has opacity < 1.0 (e.g., dip_to_black where both passes have reduced opacity), or when pass 1 contains transparent meshes whose alpha channels interact with pass 2.

**Depth buffer handling:** Between each pass, `renderer.clearDepth()` is called to clear the depth buffer while preserving the color buffer. Without this, pass 2's fragments would be rejected by the depth test against pass 1's depth values — meshes at the same Z position in both scenes would fail `GL_LESS`, causing pass 2 to be invisible at those pixels. Clearing the depth buffer per-pass ensures each pass depth-sorts its own meshes correctly while painting over the color from previous passes via alpha blending.

**For V1's three transition types:**
- **cut:** Single pass, opacity 1.0. Exact.
- **crossfade:** Pass A at 1.0, pass B at p. Exact for opaque scenes (all V1 backgrounds are opaque).
- **dip_to_black:** Fade out = one pass at (1-p). Fade in = one pass at p. Exact.

**Alternatives considered:**
1. **Render targets (FBOs):** Render each scene to a separate texture, composite with a shader. Correct but complex. Deferred to OBJ-068 if visual artifacts are found.
2. **Single pass with all materials at blended opacity:** Incorrect — background planes at 50% opacity reveal the clear color through them rather than blending with the other scene.

---

That's the only change needed. The rest of the Round 3 spec stands. Challenger, please verify this fix addresses Issue 11 and let me know if the spec is ready for finalization.

---

## Round 6 — spec_challenger

## Verification of Round 4 Fix (Issue 11)

**Issue 11 — Depth buffer between passes:** ✅ Fixed correctly in all three locations:

1. **D2** — Now includes "Depth buffer handling" paragraph explaining `clearDepth()` per-pass.
2. **PageProtocol.renderFrame() JSDoc** — Step 5a explicitly calls `renderer.clearDepth()` before each pass.
3. **Page-side renderComposite() contract** — Same step 5a with `renderer.clearDepth()`.
4. **AC-35** — Tests depth independence with identically-positioned meshes in both scenes.

The fix is structurally sound. Each pass gets a fresh depth buffer (via `clearDepth()`) while preserving the color buffer from previous passes — exactly what's needed for sequential over-paint compositing.

---

## Final Comprehensive Review

I've re-read the complete revised spec one more time. All 11 issues from Rounds 2 and 4 are verified as addressed. The spec is:

- **Implementable without guessing** — every protocol message, error code, compositing step, and lifecycle transition is specified
- **Constraint-compliant** — C-02 (pipeline), C-03 (virtualized clock via dumb page), C-05 (determinism via no page-side state tracking), C-11 (software rendering — MeshBasicMaterial + fog works in SwiftShader)
- **Vocabulary-correct** — uses "plane" not "layer," "scene geometry" not "layout template"
- **Within scope** — defines the cross-boundary protocol without bleeding into OBJ-035 (orchestrator), OBJ-036 (sequencer), or OBJ-005 (geometry definitions)
- **Downstream-compatible** — OBJ-035/OBJ-036 can construct `SceneSetupConfig` and `RenderFrameCommand` from the defined types

No new issues found. The spec is ready.

CONCLUSION:

The OBJ-011 specification defines the complete Puppeteer-to-page message protocol for depthkit. It delivers protocol types (`protocol-types.ts`), a Node-side `PageProtocol` class wrapping `PuppeteerBridge.evaluate()`, and page-side extensions to `window.depthkit`. Key design decisions: dumb page / smart orchestrator (all state computed Node-side), multi-pass compositing via sequential over-paint with `clearDepth()` per pass for transitions, per-slot texture error reporting with magenta fallback, `RequiredCameraState` (all fields required per pass), fog from primary scene (highest opacity, first-pass tie-break), `FogConfig` imported from OBJ-005 not duplicated, POSIX-only paths, single `evaluate()` call for dispose, insertion-ordered scene IDs. 35 acceptance criteria cover initialization, scene setup/teardown, single-pass and multi-pass rendering, texture loading, fog, determinism, and error cases.

Let me write the files to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}]


Now let me write the final specification and update the meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "content": "# Specification: OBJ-011 \u2014 Puppeteer-to-Page Message Protocol\n\n## Summary\n\nOBJ-011 defines the complete cross-boundary message protocol between the Node.js orchestrator and the headless Chromium page. It delivers: (1) a `PageProtocol` class on the Node side that wraps `PuppeteerBridge.evaluate()` with typed, high-level commands \u2014 initialization, scene setup/teardown, frame rendering (with multi-pass support for transitions), and disposal; (2) page-side extensions to `window.depthkit` that implement the protocol handlers \u2014 scene management (creating/removing THREE.Group instances with textured meshes), texture loading via THREE.TextureLoader, and multi-pass compositing for transitions; and (3) shared protocol types (`src/engine/protocol-types.ts`) that define every data structure crossing the boundary. This is the single source of truth for the Node.js/browser contract, building on OBJ-009's `evaluate()` primitive, OBJ-010's renderer skeleton, and OBJ-005's geometry slot structures.\n\n## Interface Contract\n\n### Protocol Types: `src/engine/protocol-types.ts`\n\nAll types in this module are JSON-serializable (no functions, no class instances, no Three.js types). They document the shapes that cross the `page.evaluate()` boundary.\n\n```typescript\n// src/engine/protocol-types.ts\n\nimport type { PageInitConfig, RendererInfo } from './page-types.js';\nimport type { FogConfig } from '../scenes/geometries/types.js';\n\n// Re-export for protocol consumers\nexport type { PageInitConfig, RendererInfo, FogConfig };\n\n// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n// Camera State\n// \u2500\u2500\u2500\u2500\u250
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md
Now update the meta.json:
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

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json",
  "content": "{\n  \"id\": \"OBJ-011\",\n  \"description\": \"Full Puppeteer-to-page message protocol -- defines every message type crossing the Node.js/browser boundary. Includes: frame step commands (frame number, fps, totalFrames), scene setup/teardown commands (geometry instantiation, texture URLs, slot assignments), texture loading completion signals, transition signals (prepare next scene, start overlap rendering), and error reporting from page back to orchestrator. Single source of truth for the cross-boundary contract.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"spec_deliberation\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-009\", \"OBJ-010\", \"OBJ-005\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"notes\": \"Tier 2 engine core. Delivers PageProtocol class (Node-side), protocol-types.ts (shared types), and page-side extensions to window.depthkit. Key decisions: dumb page / smart orchestrator, multi-pass compositing via sequential over-paint with clearDepth() per pass, RequiredCameraState (all fields required), FogConfig imported from OBJ-005, per-slot error reporting with magenta fallback, POSIX-only paths. 35 acceptance criteria. Specified via 6-round deliberation resolving 11 issues (compositing math, depth buffer interaction, fog multi-pass tie-breaking, MeshBasicMaterial fog correctness, FrameCameraState/RequiredCameraState separation, FogConfig deduplication, POSIX path scoping, dispose atomicity, insertion-order scene IDs, empty sceneId validation, HTTP texture determinism warning).\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/meta.json has been updated successfully.
Now let me commit to git:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Check git status for OBJ-011 files"
}

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Check recent commit messages for style"
}
[Tool Result] d9a7835 OBJ-027: Push/pull camera path preset specification
6c02bd2 spec(OBJ-015): Texture loader and format handling specification
af6acf5 spec(OBJ-018): stage scene geometry -- default geometry with 6 slots
7a64c90 spec(OBJ-008): transition type contract — cut, crossfade, dip_to_black
82035d9 spec(OBJ-009): virtualized clock and Puppeteer bridge specification
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-011/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/transcript.md
	nodes/OBJ-002/transcript.md
	nodes/OBJ-003/transcript.md
	nodes/OBJ-004/transcript.md
	nodes/OBJ-005/transcript.md
	nodes/OBJ-006/transcript.md
	nodes/OBJ-007/transcript.md
	nodes/OBJ-008/transcript.md
	nodes/OBJ-009/transcript.md
	nodes/OBJ-010/transcript.md
	nodes/OBJ-011/output.md
	nodes/OBJ-013/transcript.md
	nodes/OBJ-015/transcript.md
	nodes/OBJ-016/transcript.md
	nodes/OBJ-018/transcript.md
	nodes/OBJ-026/transcript.md
	nodes/OBJ-027/transcript.md
	nodes/OBJ-031/transcript.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-011/output.md nodes/OBJ-011/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-011): Puppeteer-to-page message protocol\n\nDefines the complete cross-boundary contract between Node.js orchestrator\nand headless Chromium page. Delivers PageProtocol class, protocol-types.ts,\nand page-side window.depthkit extensions (setupScene, renderComposite,\nteardownScene, disposeAll, getActiveSceneIds). Key decisions: dumb page /\nsmart orchestrator, multi-pass compositing with clearDepth() per pass for\ntransitions, RequiredCameraState (all fields required), FogConfig from\nOBJ-005, per-slot error reporting with magenta fallback. 35 acceptance\ncriteria. 6-round deliberation resolving 11 issues including depth buffer\ninteraction, compositing math, fog tie-breaking, and type safety.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-011 specification files"
}
[Tool Result] [master 9ea9d41] spec(OBJ-011): Puppeteer-to-page message protocol
 2 files changed, 1005 insertions(+), 3 deletions(-)
 create mode 100644 nodes/OBJ-011/output.md
The OBJ-011 specification has been written to disk and committed. The deliberation converged after 6 rounds resolving 11 issues:

**Critical issues resolved (2):**
1. Multi-pass compositing opacity math — specified exact algorithm (Pass A at 1.0, Pass B at progress p) with mathematical proof for opaque scenes
2. Depth buffer interaction — added `renderer.clearDepth()` per pass to prevent GL_LESS rejection across passes

**Major issues resolved (4):**
3. Corrected false claim that MeshBasicMaterial is unaffected by fog
4. Specified fog tie-breaking during multi-pass (highest opacity, first-pass wins)
5. Separated `RequiredCameraState` from `FrameCameraState` to prevent type confusion
6. Imported `FogConfig` from OBJ-005 instead of duplicating it

**Minor issues resolved (5):**
7. Scoped path resolution to POSIX only
8. Specified `dispose()` as single `evaluate()` call via `disposeAll()`
9. Guaranteed `getActiveSceneIds()` returns insertion order
10. Added AC-16 for empty `sceneId` validation
11. Added HTTP texture determinism warning
