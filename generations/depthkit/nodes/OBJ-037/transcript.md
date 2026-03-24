# Deliberation Transcript: OBJ-037

---

## Round 1 — spec_author

Looking at OBJ-037, I need to understand what it does in the architecture: OBJ-036 (Scene Sequencer) determines *what* to render at *what opacity* per frame. OBJ-008 defines the opacity computation math. OBJ-037 is the **page-side GPU compositing** — the Three.js component that actually renders multiple scenes with per-pass opacity onto a single canvas.

Let me review the existing code and dependency outputs to make sure my spec aligns.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read,Glob,Grep",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Grep'}]

[Tool: Glob]
  Input: {
  "pattern": "**/src/page/**"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/src/transitions/**"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-037/**"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-037/meta.json

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-036/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-011/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-036/output.md
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md"
}
[Tool Error] File content (15329 tokens) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file, or search for specific content instead of reading the whole file.

[Tool: Glob]
  Input: {
  "pattern": "**/nodes/OBJ-035/output.md"
}

[Tool: Glob]
  Input: {
  "pattern": "**/src/**/*.ts"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "limit": 100
}
[Tool Result]      1→# Specification: OBJ-011 — Puppeteer-to-Page Message Protocol
     2→
     3→## Summary
     4→
     5→OBJ-011 defines the complete cross-boundary message protocol between the Node.js orchestrator and the headless Chromium page. It delivers: (1) a `PageProtocol` class on the Node side that wraps `PuppeteerBridge.evaluate()` with typed, high-level commands — initialization, scene setup/teardown, frame rendering (with multi-pass support for transitions), and disposal; (2) page-side extensions to `window.depthkit` that implement the protocol handlers — scene management (creating/removing THREE.Group instances with textured meshes), texture loading via THREE.TextureLoader, and multi-pass compositing for transitions; and (3) shared protocol types (`src/engine/protocol-types.ts`) that define every data structure crossing the boundary. This is the single source of truth for the Node.js/browser contract, building on OBJ-009's `evaluate()` primitive, OBJ-010's renderer skeleton, and OBJ-... [truncated]

[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/src/**"
}
[Tool Result] No files found

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": 100,
  "limit": 150
}
[Tool Result]    100→   *   'file://' + path by the page handler)
   101→   * - file:// URL
   102→   * - data: URI (base64-encoded image)
   103→   * - http:// or https:// URL (development/testing only)
   104→   *
   105→   * The page handler detects the format and handles accordingly.
   106→   * Absolute POSIX file paths are the primary production path
   107→   * per OBJ-009 D10.
   108→   *
   109→   * Production use should prefer absolute file paths or data URIs
   110→   * for deterministic rendering (C-05). HTTP/HTTPS URLs are
   111→   * supported for development/testing but introduce network
   112→   * dependency that may affect reproducibility.
   113→   *
   114→   * Path resolution assumes POSIX filesystem paths (Linux/macOS).
   115→   * The depthkit engine targets Linux VPS and Docker containers
   116→   * (seed C-08, C-11). Windows paths are not supported.
   117→   */
   118→  textureSrc: string;
   119→  /**
   120→   * Whether the material should enable transparency (alpha blen... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": 250,
  "limit": 200
}
[Tool Result]    250→  /**
   251→   * Opacity for this pass (0.0 = fully transparent, 1.0 = fully opaque).
   252→   * Clamped to [0.0, 1.0] by the page handler.
   253→   *
   254→   * Applied by setting material.opacity on all meshes in the scene group
   255→   * before rendering. Original opacities are saved before and restored after
   256→   * each frame's render passes complete.
   257→   */
   258→  opacity: number;
   259→
   260→  /**
   261→   * Camera state for this pass. All three fields are required —
   262→   * the orchestrator always computes the full camera state.
   263→   */
   264→  camera: RequiredCameraState;
   265→}
   266→
   267→// ────────────────────────────────────────────
   268→// Scene Teardown
   269→// ────────────────────────────────────────────
   270→
   271→/**
   272→ * Result of tearing down a scene.
   273→ */
   274→export interface SceneTeardownResult {
   275→  /** The scene ID that was torn down. */
   276→  sceneId: string;
   277→  /** Number of meshe... [truncated]
This is critical — OBJ-011 already defines a compositing model. Let me read the rest to understand the full picture.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": 450,
  "limit": 150
}
[Tool Result]    450→   *
   451→   * @param command - The render passes for this frame.
   452→   * @throws PageProtocolError with code 'NOT_INITIALIZED' if init not called.
   453→   * @throws PageProtocolError with code 'SCENE_NOT_FOUND' if a pass references
   454→   *         a sceneId that has not been set up or has been torn down.
   455→   * @throws PageProtocolError with code 'INVALID_COMMAND' if passes is empty.
   456→   */
   457→  renderFrame(command: RenderFrameCommand): Promise<void>;
   458→
   459→  /**
   460→   * Tear down a scene: remove all meshes from the Three.js scene,
   461→   * dispose all textures and materials, and delete the scene group.
   462→   *
   463→   * After teardown, the sceneId is no longer valid for renderFrame
   464→   * or teardownScene. setupScene can be called again with the same
   465→   * sceneId (fresh setup).
   466→   *
   467→   * @param sceneId - The scene to tear down.
   468→   * @returns Disposal statistics.
   469→   * @throws PageProtocolEr... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "composit|transition|opacity|multi.pass|renderFrame",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "head_limit": 40
}
[Tool Result] 5:[Omitted long matching line]
33: * which is used by OBJ-010's lower-level renderFrame() method.
55: * (required for transition overlap rendering).
78:   * Applied when this scene is the primary (highest-opacity) scene
180: * Supports multi-pass rendering for transitions: each pass
181: * renders one scene with its own camera state and opacity.
182: * The page composites all passes into a single frame using
189: * both the opacity values AND the pass order.
191: * For normal (non-transition) frames:
192: *   passes = [{ sceneId: A, opacity: 1.0, camera: ... }]
194: * For crossfade transitions at progress p (0->1, where 0=fully A, 1=fully B):
196: *     { sceneId: A, opacity: 1.0, camera: ... },  // outgoing scene, full opacity
197: *     { sceneId: B, opacity: p,   camera: ... },   // incoming scene, increasing opacity
201: *   This is an approximation of true alpha compositing but produces
204: * For dip_to_black transitions:
205: *   Fade out: passes = [{ sceneId: A, opacity: 1-p, c... [truncated]
Now let me read the rest of OBJ-011's spec and look at OBJ-035 for the orchestrator integration.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": 597,
  "limit": 200
}
[Tool Result]    597→  renderComposite(command: RenderFrameCommand): Promise<void>;
   598→
   599→  /**
   600→   * Tear down a scene group.
   601→   *
   602→   * For each mesh in the group:
   603→   *   1. mesh.geometry.dispose()
   604→   *   2. mesh.material.map?.dispose() (texture)
   605→   *   3. mesh.material.dispose()
   606→   * Then: group.removeFromParent()
   607→   * Then: delete from internal scene registry.
   608→   *
   609→   * @param sceneId - Scene to tear down.
   610→   * @returns SceneTeardownResult with disposal statistics.
   611→   * @throws Error with PageErrorInfo if not initialized or scene not found.
   612→   */
   613→  teardownScene(sceneId: string): Promise<SceneTeardownResult>;
   614→
   615→  /**
   616→   * Dispose all active scenes and the renderer.
   617→   *
   618→   * Iterates all active scenes, calls teardownScene logic for each,
   619→   * then calls the existing OBJ-010 dispose() logic
   620→   * (renderer.forceContextLoss() + renderer.dispose()).... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "renderComposite|over.paint|AdditiveBlending|autoClear|NormalBlending",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "head_limit": 20
}
[Tool Result] 183: * sequential rendering with autoClear=false.
185: * COMPOSITING MODEL (order-dependent over-paint):
220:   * later passes paint over earlier ones via NormalBlending
221:   * with autoClear=false.
412:   * Compositing algorithm (sequential over-paint with autoClear=false):
419:   *   4. renderer.render(scene, camera) with autoClear=true (normal).
422:   *   1. renderer.autoClear = false
443:   *   7. renderer.autoClear = true (restore)
571:   *   - renderer.render(scene, camera) with autoClear=true
574:   *   - renderer.autoClear = false
592:   *   - renderer.autoClear = true
597:  renderComposite(command: RenderFrameCommand): Promise<void>;
668:**Decision:** Transitions are expressed as multi-pass render commands. Passes are rendered sequentially with `renderer.autoClear = false`. Each pass paints over the previous one using Three.js NormalBlending with per-material opacity scaling. Between each pass, `renderer.clearDepth()` clears the depth buffer while preserving the color buffe... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "render.target|FBO|OBJ-037|OBJ-068",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "head_limit": 15
}
[Tool Result] 690:1. **Render targets (FBOs):** Render each scene to a separate texture, composite with a shader. Correct but complex. Deferred to OBJ-068 if visual artifacts are found.
982:### OQ-A: Should multi-pass compositing use render targets instead of autoClear toggling?
984:The spec's D2 chooses sequential multi-pass rendering with `autoClear=false` and per-pass `clearDepth()`. For V1's three transition types with opaque scenes, this produces mathematically correct crossfades. If OBJ-068 (transition tuning) finds visual artifacts with transparent scenes or exotic transitions, the page handler can be upgraded to render-target-based compositing. The protocol types (`RenderFrameCommand`, `RenderPass`) would not change — only the page-side implementation.

[Showing results with pagination = limit: 15, offset: 0]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md",
  "limit": 80
}
[Tool Result]      1→# Specification: OBJ-035 — Orchestrator: Main Render Loop
     2→
     3→## Summary
     4→
     5→OBJ-035 delivers the `Orchestrator` class (`src/engine/orchestrator.ts`) — the top-level integration point that coordinates the entire depthkit rendering pipeline from manifest to MP4. It composes FrameClock and PuppeteerBridge (OBJ-009), FrameCapture (OBJ-012), FFmpegEncoder (OBJ-013), AudioMuxer (OBJ-014), PageProtocol (OBJ-011), and the manifest loader (OBJ-016) into a deterministic frame-by-frame render loop implementing seed Section 4.4 steps 1–5. It enforces C-02 (Puppeteer + Three.js + FFmpeg pipeline), C-03 (deterministic virtualized timing), C-05 (deterministic output), and C-10 (manifest validation before rendering). This is the single entry point for both the CLI (OBJ-046) and the programmatic library API.
     6→
     7→## Interface Contract
     8→
     9→### Module: `src/engine/orchestrator.ts`
    10→
    11→```typescript
    12→import type { Manifest, ManifestRegist... [truncated]

[Tool: Grep]
  Input: {
  "pattern": "SceneSequencer|planFrame|transition|OBJ-036|OBJ-037",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-035/output.md",
  "output_mode": "content",
  "head_limit": 30
}
[Tool Result] 172:   * - Crossfade transition: ['scene_001', 'scene_002'] (outgoing first)
306: * Scene transition rendering (crossfade, dip_to_black) is handled
307: * inline in V1. OBJ-036 (scene sequencer) will later extract this
309: * replaceable by OBJ-036 without changing the public API.
390:   c. Check for transition windows (see D13).
393:   f. **If two scenes are active (transition overlap):** construct multi-pass `RenderFrameCommand` per D13.
395:**Rationale:** OBJ-036 (scene sequencer) depends on OBJ-035, so the orchestrator must be functional without it. Private methods are structured so OBJ-036 can later provide a `SceneSequencer` that replaces the scene iteration without changing the public API.
496:**Decision:** The orchestrator computes transition state per-frame:
498:**Crossfade** (scene A `transition_out: crossfade` -> scene B `transition_in: crossfade`):
504:**Dip-to-black** (scene A `transition_out: dip_to_black`):
505:- Fade-out window: `[A.start_time + A.duration - A.transitio... [truncated]
Now I have a comprehensive understanding of the architecture. Let me check what exists in the actual codebase.
[Tool: Glob]
  Input: {
  "pattern": "**/depthkit/package.json"
}
[Tool Result] No files found

[Tool: Grep]
  Input: {
  "pattern": "transition|compositor",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit",
  "glob": "**/*.{ts,js,json}",
  "output_mode": "files_with_matches",
  "head_limit": 10
}
[Tool Result] Found 10 files limit: 10, offset: 0
nodes/OBJ-036/meta.json
nodes/OBJ-038/meta.json
nodes/OBJ-035/meta.json
nodes/OBJ-011/meta.json
nodes/OBJ-008/meta.json
nodes/OBJ-004/meta.json
nodes/OBJ-002/meta.json
nodes/OBJ-078/meta.json
nodes/OBJ-068/meta.json
nodes/OBJ-037/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-037/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-037",
     3→  "description": "Transition renderer -- implements crossfade, dip_to_black, and cut transitions by rendering overlapping scenes with animated opacity per Section 8.8. During overlap windows, both scenes' Three.js scene graphs render in sequence to the same canvas with complementary opacity. Addresses TC-10 (transitions mask compositing seams).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-036", "OBJ-008"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration."
    12→}
    13→

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-068/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-068",
     3→  "description": "Transition visual validation -- crossfade and dip_to_black quality across scene boundaries. Test whether 0.5-1.0 second crossfade masks visible artifacts at scene boundaries per TC-10. Submit transition test renders to Director Agent, iterate through HITL.",
     4→  "category": "tuning",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-037", "OBJ-035", "OBJ-058"],
     9→  "visual_status": "needs_tuning",
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 5 tuning. Covers TC-10."
    12→}
    13→
Now I have full context. Let me also check OBJ-011's acceptance criteria for multi-pass rendering to understand what's already tested:
[Tool: Grep]
  Input: {
  "pattern": "AC-1[5-9]|AC-2[0-9]|multi.pass|composite|crossfade",
  "path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "output_mode": "content",
  "head_limit": 30
}
[Tool Result] 5:[Omitted long matching line]
180: * Supports multi-pass rendering for transitions: each pass
182: * The page composites all passes into a single frame using
194: * For crossfade transitions at progress p (0->1, where 0=fully A, 1=fully B):
421:   * Multi-pass or any pass with opacity < 1.0 (composite path):
564:   * Render a composited frame from one or more passes.
573:   * Multi-pass or reduced-opacity (composite path):
668:**Decision:** Transitions are expressed as multi-pass render commands. Passes are rendered sequentially with `renderer.autoClear = false`. Each pass paints over the previous one using Three.js NormalBlending with per-material opacity scaling. Between each pass, `renderer.clearDepth()` clears the depth buffer while preserving the color buffer.
670:**Compositing algorithm for crossfade at progress `p` (0->1):**
676:This is an approximation — not a true alpha composite of two independent renders. The exact math for two passes with NormalBlending:
686:- **crossfade:... [truncated]
Now I have the full picture. Here's my analysis and proposed specification.

---

## Key Findings from Dependency Analysis

**Critical architectural tension**: OBJ-011 D2 defines a **sequential over-paint** compositing model where crossfade uses `outgoing=1.0, incoming=p` with NormalBlending. OBJ-036 produces **complementary opacities** (`outgoing=1-p, incoming=p`). These are incompatible: OBJ-036's opacities through OBJ-011's over-paint model produce mathematically incorrect results (outgoing is attenuated by `(1-β)` instead of rendered at its specified opacity).

**OBJ-011 anticipated this**: D2 explicitly calls the model "an approximation" and OQ-A says "the page handler can be upgraded to render-target-based compositing. The protocol types (`RenderFrameCommand`, `RenderPass`) would not change — only the page-side implementation."

**OBJ-037's role**: Upgrade the page-side compositing to use render targets with additive blending, making OBJ-036's complementary opacities render correctly. The protocol types are unchanged. This is the "Transition Renderer" — the rendering engine for transitions.

---

# Specification: OBJ-037 — Transition Renderer

## Summary

OBJ-037 delivers the `TransitionCompositor` — a page-side class (`src/page/transition-compositor.js`) that replaces OBJ-011's approximate over-paint compositing (D2) with mathematically correct weighted compositing via render targets and additive blending. It enables OBJ-036's complementary opacity model to produce correct visual output for all transition types. Each scene pass renders to an intermediate `WebGLRenderTarget` at full fidelity; a final compositing pass draws fullscreen quads with per-pass opacity using additive blending, producing `finalPixel = Σ(scene_i × opacity_i)`. The `RenderFrameCommand` and `RenderPass` protocol types (OBJ-011) are unchanged — only the page-side `renderComposite()` implementation evolves. Addresses TC-10 (transitions mask compositing seams).

## Interface Contract

### Page-Side Class: `src/page/transition-compositor.js`

This class runs inside headless Chromium. Documented here as TypeScript for contract precision; implemented as plain JavaScript on the page.

```typescript
// Conceptual TypeScript contract — implemented as plain JS.

/**
 * Configuration for creating a TransitionCompositor.
 */
interface TransitionCompositorConfig {
  /** The Three.js WebGLRenderer instance (from window.depthkit.renderer). */
  renderer: THREE.WebGLRenderer;
  /** Composition width in pixels. */
  width: number;
  /** Composition height in pixels. */
  height: number;
}

/**
 * A resolved render pass ready for compositing.
 * Constructed by renderComposite() from the RenderFrameCommand
 * and the page's internal scene registry.
 */
interface ResolvedPass {
  /** The THREE.Group containing this scene's meshes. */
  group: THREE.Group;
  /** Camera state for this pass. */
  camera: { position: [number, number, number]; lookAt: [number, number, number]; fov: number };
  /** Opacity for this pass. Range [0, 1]. */
  opacity: number;
  /** Fog config for this scene, or null. */
  fog: FogConfig | null;
}

/**
 * Composites multi-pass frames with per-pass opacity using
 * render targets and additive blending.
 *
 * Replaces OBJ-011's sequential over-paint model (D2) with
 * correct weighted compositing: each scene renders to its own
 * render target at full fidelity, then fullscreen quads are
 * drawn with additive blending at per-pass opacity.
 *
 * Compositing formula:
 *   finalPixel = Σ(renderTarget_i_rgb × opacity_i)
 *
 * This produces correct results for:
 * - Crossfade (complementary opacities, α + β = 1.0):
 *     pixel = A × α + B × (1-α)  [correct linear blend]
 * - Independent fades (sub-unity, α + β < 1.0):
 *     pixel = A × α + B × β      [dim, through black]
 * - Single pass at reduced opacity:
 *     pixel = A × α              [fade to/from black]
 *
 * Lifecycle: create (at init) → compositeFrame (per frame) → dispose.
 * Immutable after construction (except resize).
 */
class TransitionCompositor {
  constructor(config: TransitionCompositorConfig);

  /**
   * Composite one or more scene passes into a single frame.
   *
   * Behavior by pass configuration:
   * - 0 passes: clears the canvas to black (gap frame).
   * - 1 pass, opacity === 1.0: renders directly to canvas.
   *   No render target used. Equivalent to OBJ-011's fast path.
   * - 1 pass, opacity < 1.0: renders to render target, composites
   *   at requested opacity over black background.
   * - 2+ passes: renders each to its own render target, composites
   *   all in order with additive blending.
   *
   * The shared THREE.Scene and THREE.PerspectiveCamera from
   * window.depthkit are passed in because the compositor needs
   * to manipulate group visibility, scene fog, and camera state
   * before each per-target render call.
   *
   * @param passes - Ordered array of resolved passes.
   * @param scene - The shared THREE.Scene (contains all scene groups).
   * @param camera - The shared THREE.PerspectiveCamera.
   */
  compositeFrame(
    passes: ResolvedPass[],
    scene: THREE.Scene,
    camera: THREE.PerspectiveCamera
  ): void;

  /**
   * Updates internal render target dimensions.
   * Must be called if composition resolution changes.
   */
  resize(width: number, height: number): void;

  /**
   * Releases all GPU resources: render targets, compositing
   * material, compositing geometry, compositing scene.
   * Must be called during page disposal (disposeAll).
   */
  dispose(): void;
}
```

### Integration with `window.depthkit.renderComposite()`

The existing `renderComposite()` method (OBJ-011, D9) is modified to delegate multi-pass compositing to the `TransitionCompositor`. The method signature and error handling remain unchanged — only the internal compositing algorithm changes.

```typescript
// Modified renderComposite() — conceptual contract.
// The function still lives in src/page/scene-renderer.js.

/**
 * CHANGED BEHAVIOR (OBJ-037):
 *
 * The compositing algorithm for multi-pass frames is replaced.
 * OBJ-011's over-paint model (NormalBlending, autoClear=false,
 * material opacity modification) is replaced with render-target
 * compositing via TransitionCompositor.
 *
 * Single-pass at opacity 1.0 (fast path): UNCHANGED.
 *   - Set referenced scene group visible=true
 *   - Set all other scene groups visible=false
 *   - Set scene.fog from this scene's fog config
 *   - Apply camera state
 *   - renderer.render(scene, camera) with autoClear=true
 *
 * Multi-pass or any pass with opacity < 1.0:
 *   - Resolve each RenderPass to a ResolvedPass
 *     (lookup group from scene registry, include fog config)
 *   - Delegate to compositor.compositeFrame(resolvedPasses, scene, camera)
 *
 * Material opacity save/restore (OBJ-011 D2 steps 5c/5d/6)
 * is NO LONGER NEEDED. The compositor renders each scene to
 * its own render target at FULL material opacity. Per-pass
 * opacity is applied only during the compositing step.
 *
 * Fog handling CHANGES from OBJ-011 D10:
 * - Each pass's scene fog is set independently before rendering
 *   to that pass's render target.
 * - No "primary scene" fog determination needed — each scene
 *   renders with its own fog in its own render target.
 */
renderComposite(command: RenderFrameCommand): Promise<void>;
```

### Page State Changes

```typescript
// Additions to window.depthkit internal state:

interface DepthkitPage {
  // ... existing state from OBJ-010, OBJ-011 ...

  /**
   * TransitionCompositor instance. Created during init().
   * Used by renderComposite() for multi-pass frames.
   * Disposed during disposeAll().
   */
  compositor: TransitionCompositor | null;
}
```

### No Protocol Type Changes

`RenderFrameCommand`, `RenderPass`, `RequiredCameraState`, and all other types in `src/engine/protocol-types.ts` (OBJ-011) are **unchanged**. The compositor upgrade is purely page-side. The Node.js orchestrator continues to construct `RenderFrameCommand` exactly as specified in OBJ-036's Orchestrator Integration Contract.

## Design Decisions

### D1: Render-Target Compositing Replaces Over-Paint

**Decision:** Multi-pass frames use intermediate `THREE.WebGLRenderTarget` instances. Each pass's scene renders to its own render target at full material opacity. A final compositing step draws fullscreen quads textured with each render target, applying per-pass opacity via `THREE.AdditiveBlending`.

**Compositing algorithm:**
1. For each pass with `opacity > 0`:
   a. `renderer.setRenderTarget(renderTargets[i])`
   b. Set only this pass's scene group `visible = true`; all others `visible = false`.
   c. Set `scene.fog` from this pass's scene fog config (or `null`).
   d. Apply camera state (position, lookAt, fov, updateProjectionMatrix).
   e. `renderer.render(scene, camera)` — renders to the render target at full fidelity.
2. Switch to canvas: `renderer.setRenderTarget(null)`.
3. Clear canvas to black.
4. Set `renderer.autoClear = false`.
5. For each rendered pass (in order):
   a. Set compositing material's `map` to `renderTargets[i].texture`.
   b. Set compositing material's `opacity` to `pass.opacity`.
   c. `renderer.render(compositeScene, compositeCamera)` — additive blend onto canvas.
6. Restore `renderer.autoClear = true`.

**Why this replaces OBJ-011 D2:** OBJ-011's over-paint model with NormalBlending produces `pixel = B×β + A×α×(1-β)` for two passes. When OBJ-036 sends complementary opacities (α=0.7, β=0.3), the result is `0.3B + 0.49A` — incorrect. The correct result is `0.3B + 0.7A`. The render-target approach with additive blending produces `pixel = A×α + B×β = 0.7A + 0.3B` — correct for all opacity combinations.

**OBJ-011 anticipated this:** D2 says "This is an approximation." OQ-A says "the page handler can be upgraded to render-target-based compositing. The protocol types would not change — only the page-side implementation." OBJ-037 implements this upgrade.

**Alternative considered:** Remap OBJ-036's complementary opacities to OBJ-011's model (set outgoing=1.0 for crossfade). Rejected: requires knowing the transition type in the orchestrator-to-page mapping, only works for crossfade (not independent fades with overlap), and perpetuates the approximation.

### D2: Single-Pass Fast Path Preserved

**Decision:** When `passes.length === 1` and `passes[0].opacity === 1.0`, `renderComposite()` renders directly to the canvas exactly as OBJ-011's fast path specifies — no render target, no compositing overhead. This is the common case for ~90% of frames.

**Opacity comparison:** Uses `=== 1.0` (exact equality). OBJ-036's `planFrame()` returns exactly `1.0` for non-transition frames (D6: "opacity 1.0 during normal rendering"). If edge cases produce `0.9999999`, the frame takes the compositor path — visually indistinguishable but slightly slower. This is acceptable; the implementer may use a threshold like `>= 1.0 - 1e-9` as an optimization.

**Single-pass with opacity < 1.0** (dip_to_black fade): Uses the compositor. Renders scene to render target, composites at reduced opacity over black. This correctly produces a dimmed frame without modifying material opacities.

### D3: Additive Blending via THREE.AdditiveBlending

**Decision:** The compositing material uses `THREE.AdditiveBlending` for the fullscreen quad renders.

**Three.js blending equation for `AdditiveBlending`:**
- Source factor: `GL_SRC_ALPHA`
- Dest factor: `GL_ONE`
- Equation: `result = src_rgb × src_alpha + dst_rgb × 1`

With material `opacity = p` and texture RGB = (R, G, B):
- Fragment output: `(R, G, B, p)` (MeshBasicMaterial multiplies alpha by opacity)
- Blending: `result = (R×p, G×p, B×p) + dst_rgb`
- After N passes over black: `result = Σ(texture_i_rgb × opacity_i)` ✓

**Energy conservation:** For crossfade (opacities sum to 1.0), pixels never exceed source brightness. For independent fades (opacities sum to < 1.0), pixels are dimmer. The compositor does NOT validate that opacities sum to ≤ 1.0. If they exceed 1.0 (not expected from OBJ-036), pixels may clip — this is the caller's responsibility.

### D4: Render Target Pool

**Decision:** The compositor pre-allocates 2 render targets at construction. This covers the expected maximum concurrent passes (OBJ-036 D11 warns when >2 scenes overlap). If more passes are needed, additional render targets are created on demand and retained for future frames.

**Render target specification:**
- Size: `width × height` (from config).
- Format: `THREE.RGBAFormat`.
- Type: `THREE.UnsignedByteType` (8-bit per channel, matching canvas precision).
- MinFilter/MagFilter: `THREE.LinearFilter`.
- `depthBuffer: true` — required for correct depth sorting within each scene.
- Stencil buffer: not needed (V1 has no stencil-based effects).

**Memory footprint:** 2 render targets at 1920×1080×4 bytes = ~16MB GPU memory. Acceptable for the target hardware (C-08).

### D5: Compositing Geometry — Fullscreen Quad with Orthographic Camera

**Decision:** The compositor creates a dedicated `THREE.Scene` ("composite scene") containing a single `THREE.Mesh` with `THREE.PlaneGeometry(2, 2)` and a `THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)`. The mesh uses a `THREE.MeshBasicMaterial` with:
- `map`: set per-pass to the render target's texture
- `transparent: true`
- `opacity`: set per-pass to the pass opacity
- `blending: THREE.AdditiveBlending`
- `depthTest: false`
- `depthWrite: false`

The mesh's texture and opacity are updated per-pass; the geometry, camera, and scene are reused across all frames.

### D6: Per-Scene Fog (Replaces OBJ-011 D10 "Primary Scene" Fog)

**Decision:** With render targets, each scene renders independently in its own render target with its own fog configuration. There is no "primary scene" fog determination.

**Before (OBJ-011 D10):** Determine the primary scene (highest opacity pass), set fog from its config, use that fog for ALL passes.

**After (OBJ-037):** Each pass sets `scene.fog` from its own scene's fog config before rendering to its render target. Each scene's fog is correct for that scene. During crossfade between a foggy scene and a non-foggy scene, each renders with its own fog setting, and the compositing blend produces a natural visual transition between fog states.

**For the single-pass fast path:** Fog handling is unchanged from OBJ-011 — set fog from the single scene's config before rendering.

### D7: No Material Opacity Modification

**Decision:** The compositor renders each scene to its render target at **full material opacity**. OBJ-011's steps 5c/5d/6 (save material opacities → modify → render → restore) are eliminated for the compositor path. Per-pass opacity is applied exclusively during the compositing step via the compositing material's opacity.

**Rationale:** This is a major simplification. OBJ-011's approach of traversing all meshes to save/modify/restore opacities was a workaround for the lack of render targets. With render targets, the scene renders at full fidelity; opacity is applied as a post-process during compositing. This eliminates:
- Material traversal per multi-pass frame
- Risk of state leakage if restoration fails
- Interaction bugs between pass-level opacity and per-material transparency (e.g., a subject plane with alpha texture)

### D8: Skip Zero-Opacity Passes

**Decision:** Passes with `opacity === 0.0` are skipped entirely — no render target is used, no compositing quad is drawn. A fully transparent pass contributes nothing to the final image.

**Rationale:** At the boundaries of transitions (first frame of crossfade incoming, or last frame of a fade), one pass has opacity 0.0. Skipping it saves one render target fill and one compositing draw call per such frame.

### D9: Compositor Created at init(), Disposed at disposeAll()

**Decision:** The `TransitionCompositor` is created during `window.depthkit.init()` and stored as `window.depthkit.compositor`. It is disposed during `window.depthkit.disposeAll()`. The compositor's lifecycle matches the renderer's lifecycle.

**Rationale:** Eager creation avoids render-target allocation during the first transition frame (which could cause a timing hiccup in the frame capture pipeline). The memory cost (D4: ~16MB) is constant and acceptable.

### D10: Compositor is a Page-Side Module Only

**Decision:** `TransitionCompositor` runs inside headless Chromium. It requires `THREE.WebGLRenderer` and other WebGL-dependent classes. It is NOT isomorphic. No Node.js-side changes are needed — the orchestrator continues to construct `RenderFrameCommand` per OBJ-036's Orchestrator Integration Contract, and the page protocol transmits it unchanged.

### D11: Depth Buffer Handling in Render Targets

**Decision:** Each render target has its own depth buffer (`depthBuffer: true`). When rendering a scene to its render target, Three.js's default depth testing (`GL_LESS`) applies — meshes within the scene depth-sort correctly against each other.

The compositing quads disable depth testing (`depthTest: false, depthWrite: false`). They are drawn in pass order; since additive blending is commutative for the RGB result, the order does not affect the final pixel color, but the convention (outgoing first) is maintained for consistency with OBJ-036's `FramePlan.passes` ordering.

**Replaces OBJ-011's `clearDepth()` per pass:** OBJ-011 needed `renderer.clearDepth()` between passes to prevent cross-scene depth rejection. With render targets, each scene has its own depth buffer — no cross-scene depth interaction occurs.

## Acceptance Criteria

### Core Compositing Correctness

- [ ] **AC-01:** A single pass with `opacity: 1.0` produces output pixel-identical to a direct `renderer.render(scene, camera)` call. No intermediate render target is used (fast path preserved from OBJ-011).
- [ ] **AC-02:** A single pass with `opacity: 0.5` produces an image where every non-zero pixel's RGB values are approximately half those of the full-opacity render, within ±2/255 per channel (8-bit quantization tolerance).
- [ ] **AC-03:** A single pass with `opacity: 0.0` produces a fully black frame (all pixels RGB ≤ 1/255).
- [ ] **AC-04:** Zero passes (empty array) produces a fully black frame.

### Crossfade Compositing (Complementary Opacities)

- [ ] **AC-05:** Two passes with opacities `(0.5, 0.5)` rendering solid red (scene A) and solid blue (scene B) produce pixels ≈ `(128, 0, 128)` within ±2/255 per channel. This is the correct average — `A×0.5 + B×0.5`.
- [ ] **AC-06:** Two passes with `(1.0, 0.0)` produce an image identical to rendering only the first scene at full opacity.
- [ ] **AC-07:** Two passes with `(0.0, 1.0)` produce an image identical to rendering only the second scene at full opacity.
- [ ] **AC-08:** Two passes with `(0.7, 0.3)` produce pixels ≈ `A×0.7 + B×0.3` within ±2/255 per channel. Specifically, for solid red A and solid blue B: `(179, 0, 77)` ±2.

### Independent Fade Compositing (Sub-Unity Opacities)

- [ ] **AC-09:** Two passes with `(0.3, 0.3)` produce pixels ≈ `A×0.3 + B×0.3` within ±2/255. For solid red A and blue B: `(77, 0, 77)` ±2. This verifies that the outgoing scene is NOT attenuated by the incoming scene's opacity (which would happen with NormalBlending over-paint).
- [ ] **AC-10:** Two passes with `(0.0, 0.0)` produce a fully black frame.

### Transition Type Correctness (End-to-End)

- [ ] **AC-11:** **Crossfade**: A 2-scene composition with OBJ-036 crossfade opacities (complementary, summing to 1.0) renders correctly. At the midpoint frame (opacities ~0.5/0.5), both scenes are equally visible. At boundaries, only one scene is visible.
- [ ] **AC-12:** **Dip-to-black**: A 2-scene composition with OBJ-036 independent fades produces frames that fade to black between scenes. The midpoint frame (both opacities near 0) is near-black.
- [ ] **AC-13:** **Cut**: A 2-scene composition with cut transition renders as a single pass at full opacity per frame. The fast path is used (no render targets).

### Fog Handling

- [ ] **AC-14:** During a crossfade between a scene with fog (color #000000, near 10, far 40) and a scene without fog, each scene's render target correctly applies (or omits) fog for its own content. The fog does not leak between scenes.

### Optimization

- [ ] **AC-15:** Passes with `opacity === 0.0` are not rendered to a render target and no compositing quad is drawn for them.
- [ ] **AC-16:** Single-pass frames at `opacity === 1.0` do not allocate or use render targets.

### Scene-Internal Transparency

- [ ] **AC-17:** A scene containing a plane with alpha-transparent texture (e.g., a subject with `transparent: true`) renders correctly to the render target. The transparency is preserved in the render target and composites correctly during transitions.

### Resource Management

- [ ] **AC-18:** `dispose()` releases all render targets, compositing material, compositing geometry, and the compositing scene. No WebGL resource leaks after disposal.
- [ ] **AC-19:** `resize()` updates render target dimensions. Subsequent `compositeFrame()` calls produce output at the new resolution.

### OBJ-011 Behavioral Parity

- [ ] **AC-20:** OBJ-011's AC-17 still passes: a two-pass frame with opacity (1.0, 0.5) renders both scenes composited into a single frame that is visually distinct from either scene alone.
- [ ] **AC-21:** OBJ-011's AC-18 still passes: a single pass at opacity 0.0 produces a black frame.
- [ ] **AC-22:** OBJ-011's AC-19 still passes: single pass at opacity 1.0 produces the same output as before the upgrade.
- [ ] **AC-23:** OBJ-011's AC-20 still passes: after multi-pass rendering, a subsequent single-pass render at full opacity produces the same output as before the multi-pass frame. (Material opacities are never modified, so this is inherently satisfied.)

### Determinism

- [ ] **AC-24:** Rendering the same passes with the same scenes/cameras/opacities produces identical pixel output across multiple calls on the same hardware (deterministic per C-05).

### Performance

- [ ] **AC-25:** A multi-pass compositing frame (2 passes) completes within 2× the time of a single-pass frame at the same resolution, measured on a software WebGL renderer. This verifies that the render-target overhead is bounded.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Empty passes array | Clear canvas to black. No render targets used. |
| Single pass, `opacity === 1.0` | Direct render (fast path). No render target. |
| Single pass, `opacity === 0.0` | Skip rendering entirely. Canvas cleared to black. |
| Single pass, `0 < opacity < 1.0` | Render to RT, composite at opacity over black. |
| Two passes, both `opacity === 0.0` | Both skipped. Canvas remains black. |
| Two passes, complementary opacities | Correct weighted blend: `A×α + B×(1-α)`. |
| Two passes, independent fades | Correct additive: `A×α + B×β`, dim result. |
| Three or more passes | All render to separate RTs. Additional RTs created on demand. Additive composite of all. |
| Pass with `opacity > 1.0` | Compositor does not clamp. Renders as given. Pixels may clip to white. Caller's responsibility (OBJ-036 never produces this). |
| Pass with `opacity < 0.0` | Three.js clamps material opacity to [0,1]. Effectively treated as 0.0. |
| Scene with no meshes (empty group) | Renders as black to the RT. Contributes black × opacity = black. |
| Scene with transparent meshes (alpha textures) | Scene renders with alpha to RT. Alpha channel preserved. Compositing applies pass opacity on top. |
| Scene with fog | Fog applied correctly in this scene's RT. Does not affect other scenes' RTs. |
| `compositeFrame()` called after `dispose()` | Undefined behavior. Caller must not call after disposal. |
| `resize()` to different aspect ratio | Render targets recreated at new size. Compositing geometry unchanged (fullscreen quad is aspect-ratio independent with ortho camera). |
| Very large composition (4K: 3840×2160) | Render targets may exceed GPU memory on software renderer. No explicit guard — WebGL context loss would occur, caught by existing error handling. |

## Test Strategy

### Test Environment

Testing requires a WebGL context (Three.js rendering). Tests run in Puppeteer with a headless Chromium instance, consistent with the depthkit rendering environment. This matches the testing pattern implied by OBJ-011's acceptance criteria.

### Unit-Level Tests: `test/integration/transition-compositor.test.ts`

(Located under `test/integration/` because they require Puppeteer + WebGL, not pure Node.js unit tests.)

**Setup:** Each test creates a minimal Three.js environment inside Puppeteer, sets up the compositor, creates test scenes with solid-color planes at known positions.

**Solid-color scene factory:** Create scenes with a single `MeshBasicMaterial({ color: 0xff0000 })` plane filling the camera view. Use red (scene A), blue (scene B), and green (scene C) for arithmetic verification.

**Tests:**

1. **Fast path equivalence (AC-01):** Render scene A at opacity 1.0 via compositor. Render scene A via direct `renderer.render()`. Compare pixel buffers — must be identical.
2. **Half-opacity fade (AC-02):** Render solid red at opacity 0.5. Sample center pixel. Verify R ≈ 128 ±2, G = 0, B = 0.
3. **Zero-opacity black (AC-03):** Render at opacity 0.0. Verify all-black output.
4. **Empty passes black (AC-04):** Render with empty array. Verify all-black.
5. **Crossfade midpoint (AC-05):** Red at 0.5, blue at 0.5. Verify center pixel ≈ (128, 0, 128) ±2.
6. **Crossfade 100/0 (AC-06):** Red at 1.0, blue at 0.0. Verify pure red.
7. **Crossfade 0/100 (AC-07):** Red at 0.0, blue at 1.0. Verify pure blue.
8. **Crossfade 70/30 (AC-08):** Red at 0.7, blue at 0.3. Verify ≈ (179, 0, 77) ±2.
9. **Independent fades correctness (AC-09):** Red at 0.3, blue at 0.3. Verify ≈ (77, 0, 77) ±2. **This is the critical test that distinguishes render-target compositing from over-paint.** With over-paint NormalBlending, the result would be ≈ (54, 0, 77) — red attenuated by (1-0.3). The correct additive result is (77, 0, 77).
10. **Both zero (AC-10):** Red at 0.0, blue at 0.0. Verify all-black.
11. **Three-pass (AC-15 edge case):** Red 0.33, green 0.33, blue 0.34. Verify ≈ (84, 84, 87) ±3.
12. **Zero-opacity skip (AC-15):** Two passes, one at 0.0. Verify the 0.0 pass is not rendered (measurable by: the scene should not have its group set visible at any point, or by timing — if the scene is very complex, rendering should not slow down).
13. **Fog isolation (AC-14):** Scene A with black fog (near=1, far=5). Scene B with no fog. Crossfade at 0.5/0.5. Verify that scene A planes show fog attenuation in their contribution while scene B planes do not.
14. **Alpha transparency (AC-17):** Scene A with a half-transparent red plane (material opacity 0.5, transparent: true). Render at pass opacity 0.5. Center pixel R channel should be ≈ 64 (0.5 × 0.5 × 255) ±2.
15. **Resize (AC-19):** Create at 1920×1080, resize to 960×540, render. Verify output is at new resolution.
16. **Dispose (AC-18):** Call dispose(), verify no errors. A subsequent init()+create should work (no leaked state).
17. **Determinism (AC-24):** Render same frame 10 times, compare all pixel buffers — must be identical.
18. **Performance (AC-25):** Time 100 single-pass renders and 100 two-pass renders. Two-pass average should be < 2.5× single-pass average.

### End-to-End Tests: `test/integration/transition-rendering.test.ts`

These test transitions through the full pipeline (manifest → orchestrator → protocol → compositor → capture).

19. **Crossfade end-to-end (AC-11):** 2-scene manifest with 0.5s crossfade. Render all frames. Sample frames at: pre-transition (only scene A), mid-transition (both blended), post-transition (only scene B). Verify blend progression.
20. **Dip-to-black end-to-end (AC-12):** 2-scene manifest with 1.0s dip_to_black on both scenes. Verify fade-out frames darken, midpoint is near-black, fade-in frames brighten.
21. **Cut end-to-end (AC-13):** 2-scene manifest with cut. Verify instant switch — no blended frames, all frames use single-pass fast path.
22. **OBJ-011 parity (AC-20–23):** Re-run OBJ-011's multi-pass tests (AC-17 through AC-20) against the new compositor to verify behavioral parity.

### Relevant Testable Claims

- **TC-10** (Cross-scene transitions mask compositing seams): Tests 19–21 validate that all three transition types produce smooth, artifact-free scene boundaries. Visual inspection of mid-transition frames confirms no hard edges or compositing artifacts.
- **TC-06** (Deterministic output): Test 17 confirms compositor determinism. Test 24 (AC-24) formalized.

## Integration Points

### Depends on

| Dependency | What OBJ-037 uses | How |
|---|---|---|
| **OBJ-036** (Scene Sequencer) | `RenderPassPlan` type (indirectly) | The orchestrator maps `FramePlan.passes` to `RenderFrameCommand.passes`. The compositor receives these via the protocol. OBJ-037 does not import OBJ-036 directly. |
| **OBJ-008** (Transition Type Contract) | `TransitionSpec` (indirectly) | OBJ-008 defines the transition types whose opacities OBJ-036 computes. The compositor is agnostic to transition types — it renders any opacity values correctly. |
| **OBJ-011** (Page Protocol) | `RenderFrameCommand`, `RenderPass`, `renderComposite()` method | OBJ-037 modifies the implementation of `renderComposite()` to use the compositor for multi-pass frames. The protocol types are unchanged. |
| **OBJ-010** (Page Shell) | `window.depthkit` namespace, `renderer`, `scene`, `camera` | The compositor uses the existing Three.js renderer, scene, and camera. Created during `init()`, stored on `window.depthkit`. |
| **Three.js** | `WebGLRenderTarget`, `MeshBasicMaterial`, `PlaneGeometry`, `OrthographicCamera`, `Scene`, `Mesh`, `AdditiveBlending` | Core GPU rendering primitives for render targets and compositing. |

### Consumed by

| Downstream | How it uses OBJ-037 |
|---|---|
| **OBJ-068** (Transition visual tuning) | Requires working transition rendering to produce test renders for Director Agent review. |
| **OBJ-077** (Integration) | Full pipeline integration requires correct transitions. |

### File Placement

```
depthkit/
  src/
    page/
      transition-compositor.js   # NEW — TransitionCompositor class
      scene-renderer.js          # MODIFIED — renderComposite() delegates
                                 #   to compositor for multi-pass frames;
                                 #   init() creates compositor;
                                 #   disposeAll() disposes compositor
  test/
    integration/
      transition-compositor.test.ts   # NEW — compositor-focused tests
      transition-rendering.test.ts    # NEW — end-to-end transition tests
```

## Open Questions

### OQ-A: Should the compositor support a configurable clear color?

The compositor always clears to black `(0, 0, 0)`. A future `dip_to_white` transition would need a white clear color. The simplest extension: accept an optional `clearColor` in `compositeFrame()` or as a `TransitionCompositor` config option.

**Recommendation:** Defer. Seed Section 2 defines only `dip_to_black`. If `dip_to_white` is added, extend the compositor config. The protocol could carry a `clearColor` field in `RenderFrameCommand` (minor additive change to OBJ-011 types).

### OQ-B: Should render targets use floating-point format?

`THREE.UnsignedByteType` (8-bit per channel) introduces ±1/255 quantization per render target. For 2-pass compositing, the cumulative error is ±2/255 — imperceptible. `THREE.HalfFloatType` (16-bit) eliminates this but doubles GPU memory (32MB for 2 targets at 1080p).

**Recommendation:** Use `UnsignedByteType` for V1. The ±2/255 tolerance is included in all acceptance criteria. Upgrade to `HalfFloatType` if OBJ-068 (visual tuning) identifies banding artifacts during transitions.

### OQ-C: Should the compositor handle the `premultipliedAlpha` renderer setting?

Three.js `WebGLRenderer` has a `premultipliedAlpha` option (default: `true`) that affects how alpha is handled in the final canvas output. The compositor's additive blending should work correctly regardless of this setting because:
- Render targets use their own alpha format.
- The compositing quads blend RGB additively; alpha channel behavior in the final canvas output is controlled by the renderer, not the compositor.

**Recommendation:** Verify during implementation by testing with `premultipliedAlpha: true` (default) and `premultipliedAlpha: false`. Document any difference.

---

I believe this spec is comprehensive and implementable. It addresses the core architectural tension between OBJ-036's complementary opacity model and OBJ-011's over-paint compositing, resolves it with the render-target approach that OBJ-011 explicitly anticipated (D2, OQ-A), and does so without changing any protocol types.

I'd like the challenger to verify:
1. The render-target approach is the right resolution for the OBJ-036/OBJ-011 opacity mismatch
2. The fog handling change (per-scene instead of primary-scene) is sound
3. The scope is correct — compositor + renderComposite() modification, NOT orchestrator integration
4. The acceptance criteria are complete and the tolerance (±2/255) is appropriate

---

## Round 2 — spec_challenger

I've reviewed the proposed spec carefully against the seed, OBJ-036, OBJ-008, and OBJ-011. Let me read one more critical section of OBJ-011 to verify the compositing model before giving my assessment.
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": "400",
  "limit": "100"
}
[Tool Result]    400→   *
   401→   * @param config - Scene geometry slots with texture sources.
   402→   * @returns Per-slot loading results and overall success flag.
   403→   * @throws PageProtocolError with code 'NOT_INITIALIZED' if init not called.
   404→   * @throws PageProtocolError with code 'SCENE_EXISTS' if sceneId already set up.
   405→   * @throws PageProtocolError with code 'INVALID_COMMAND' if sceneId is empty.
   406→   */
   407→  setupScene(config: SceneSetupConfig): Promise<SceneSetupResult>;
   408→
   409→  /**
   410→   * Render a single output frame with one or more passes.
   411→   *
   412→   * Compositing algorithm (sequential over-paint with autoClear=false):
   413→   *
   414→   * Single-pass at opacity 1.0 (fast path):
   415→   *   1. Set only the referenced scene group visible=true.
   416→   *   2. Set scene.fog from this scene's fog config (or null if the
   417→   *      scene has no fog config).
   418→   *   3. Apply camera state.
   419→   *   4. renderer.ren... [truncated]

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-011/output.md",
  "offset": "660",
  "limit": "80"
}
[Tool Result]    660→### D1: PageProtocol Wraps Bridge, Does Not Own It
   661→
   662→**Decision:** `PageProtocol` accepts a `PuppeteerBridge` in its constructor but does not call `bridge.launch()` or `bridge.close()`. The orchestrator (OBJ-035) owns the bridge lifecycle.
   663→
   664→**Rationale:** Separation of concerns. The bridge is a transport layer; the protocol is a domain layer. The orchestrator needs direct bridge access for `captureFrame()` (which is not a protocol concern — it's a pixel extraction concern for FFmpeg piping). Ownership nesting: orchestrator -> bridge + protocol -> page.
   665→
   666→### D2: Multi-Pass Compositing via Sequential Over-Paint
   667→
   668→**Decision:** Transitions are expressed as multi-pass render commands. Passes are rendered sequentially with `renderer.autoClear = false`. Each pass paints over the previous one using Three.js NormalBlending with per-material opacity scaling. Between each pass, `renderer.clearDepth()` clears the depth buffer while pres... [truncated]
Good. Now I have the full picture of what OBJ-011 does for compositing, and I can give a thorough review.

---

## Round 2 — Spec Challenger Review

### Points of Agreement (What's Sound)

1. **The render-target approach is the right fix.** OBJ-011 D2 explicitly anticipated this upgrade ("Deferred to OBJ-068 if visual artifacts are found") and OQ-A confirms protocol types don't change. The core thesis of OBJ-037 is correct.

2. **Per-scene fog** (D6) is a clean improvement over OBJ-011's "primary scene wins" fog model. Each scene gets its own fog in its own RT — no cross-scene fog contamination.

3. **Scope is correct** — page-side only, no protocol changes, no orchestrator changes.

4. **The fast-path preservation** (D2) is right — 90% of frames are single-pass full-opacity.

5. **The zero-opacity skip** (D8) is a sound optimization.

6. **±2/255 tolerance** is appropriate for 8-bit render targets.

7. **The pool of 2 RTs** (D4) matching OBJ-036's concurrent scene limit is well-reasoned.

---

### CRITICAL — Issue 1: `AdditiveBlending` with `MeshBasicMaterial` Produces Wrong Results for Transparent Content

**The problem:** The spec says (D3, D5):

> The compositing material uses `THREE.AdditiveBlending` for the fullscreen quad renders... `THREE.MeshBasicMaterial` with `map`, `transparent: true`, `opacity`, `blending: THREE.AdditiveBlending`.

Three.js `AdditiveBlending` uses the WebGL blend function `GL_SRC_ALPHA, GL_ONE`. With `MeshBasicMaterial`, the fragment output alpha is `texture.a × material.opacity`. This means:

```
result.rgb += src.rgb × src.alpha
result.rgb += rt_texture.rgb × rt_texture.alpha × pass_opacity
```

For opaque scenes (all RT pixels have alpha=1.0), this works: `result += rt_rgb × 1.0 × pass_opacity = rt_rgb × pass_opacity`. ✓

For scenes with **transparent content** (AC-17's exact case — a subject plane with alpha texture), RT pixels have alpha < 1.0. The RT's alpha *double-attenuates* the result:
- Scene renders to RT: pixel = (R×0.5, G×0.5, B×0.5, 0.25) for a 50%-opacity mesh against black
- Compositing: `result += (R×0.5) × 0.25 × pass_opacity` — but the correct result is `(R×0.5) × pass_opacity`

The alpha from the render target leaks into the compositing blend, producing incorrect output. **AC-17 would fail with the spec as written.**

**Proposed fix:** Replace `MeshBasicMaterial` with a `ShaderMaterial` for the compositing quad. The fragment shader must ignore the RT's alpha and apply only the pass opacity:

```glsl
uniform sampler2D tDiffuse;
uniform float uOpacity;
varying vec2 vUv;
void main() {
  vec4 texel = texture2D(tDiffuse, vUv);
  gl_FragColor = vec4(texel.rgb * uOpacity, 1.0);
}
```

With `blending: THREE.AdditiveBlending` (or `CustomBlending` with `blendSrc: OneFactor, blendDst: OneFactor`), the result becomes:
```
result.rgb += texel.rgb × uOpacity × 1.0 = texel.rgb × uOpacity  ✓
```

D3 and D5 must be rewritten around this ShaderMaterial. The compositing geometry/camera setup in D5 can stay, but the material must change.

---

### MAJOR — Issue 2: Missing Render Target Clear Specification

**The problem:** D1's compositing algorithm step 1 says "render scene to RT" but never specifies:
1. What `clearColor` and `clearAlpha` are set on the renderer before rendering to each RT
2. Whether `autoClear` is explicitly `true` during the RT render passes

If the RT is cleared to anything other than `(0, 0, 0, 0)`, the additive compositing will produce incorrect results — a non-zero clear color contributes additive energy that shouldn't be there.

If `autoClear` happens to be `false` at that point (e.g., from a previous frame's compositing step that didn't properly restore state), the RT will contain stale pixels.

**Proposed fix:** Add explicit steps to D1:

- Before step 1: `renderer.setClearColor(0x000000, 0.0)` (black, fully transparent)
- Step 1 must explicitly set `renderer.autoClear = true` before each RT render (or call `renderer.clear()` explicitly before each `renderer.render()`)
- After step 4 (`autoClear = false`), note that the canvas clear in step 3 must be done with `renderer.setClearColor(0x000000, 1.0)` + `renderer.clear()` — opaque black, not transparent black (otherwise premultipliedAlpha may affect the final output)

---

### MAJOR — Issue 3: `premultipliedAlpha` Interaction Is Not a Deferrable Question

**The problem:** OQ-C says "verify during implementation" for `premultipliedAlpha`. But this directly affects compositing correctness:

- Three.js `WebGLRenderer` defaults to `premultipliedAlpha: true`
- With `premultipliedAlpha: true`, the final canvas expects premultiplied alpha output
- Our additive compositing writes `(R×opacity, G×opacity, B×opacity)` with alpha 1.0 per pass. After all passes, the canvas pixel is `(Σ(Ri×αi), Σ(Gi×αi), Σ(Bi×αi), accumulated_alpha)` 
- If the renderer premultiplies and the accumulated alpha isn't correct, the canvas-to-PNG capture may produce incorrect colors

With the ShaderMaterial fix (Issue 1) outputting `gl_FragColor = vec4(texel.rgb * uOpacity, 1.0)` for every pass, and additive blending where alpha accumulates... after two passes the alpha could exceed 1.0, which gets clamped. This is fine for RGB but the alpha channel behavior matters for capture.

**Proposed fix:** Make D1 an explicit design decision: the renderer SHALL be configured with `premultipliedAlpha: false` for the compositing pass (or document that OBJ-010's renderer config must use this setting). Alternatively, if OBJ-010 already sets this, reference it. But don't leave it as "verify later" — the implementer needs to know what value to expect.

Actually, the more practical fix: document that the ShaderMaterial always outputs alpha=1.0, and after all additive passes the final canvas pixel has alpha=1.0 (clamped). Since `Page.captureScreenshot` captures RGB regardless of alpha, `premultipliedAlpha` is irrelevant to the *captured* output. **But this reasoning needs to be in the spec**, not left as an open question.

---

### MAJOR — Issue 4: `renderComposite()` vs `renderFrame()` Method Naming Confusion

**The problem:** OBJ-011 defines TWO methods on the page:
- `window.depthkit.renderFrame()` — OBJ-010's single-scene render
- `window.depthkit.renderComposite()` — OBJ-011's multi-pass render (D9)

And `PageProtocol.renderFrame()` on the Node side calls `window.depthkit.renderComposite()`.

The OBJ-037 spec says it modifies `renderComposite()`, which is correct. But the Interface Contract section shows `renderComposite(command: RenderFrameCommand): Promise<void>` with a comment block that says both "Modified renderComposite()" and references "the existing `renderComposite()` method (OBJ-011, D9)". 

The spec needs to be explicit: **which code path changes?** The `PageProtocol.renderFrame()` Node-side method is unchanged. The `window.depthkit.renderComposite()` page-side implementation is changed. The spec should state this unambiguously in a single place rather than scattering it across the integration contract and design decisions.

**Proposed fix:** Add a clear statement to the Interface Contract: "The Node-side `PageProtocol.renderFrame()` method (OBJ-011) is unchanged. Only the page-side `window.depthkit.renderComposite()` implementation changes. Specifically, OBJ-011 D2 steps 421-443 (the composite path) are replaced."

---

### MAJOR — Issue 5: Missing Specification of How `renderComposite()` Constructs `ResolvedPass` from `RenderPass`

**The problem:** The spec defines `ResolvedPass` (group, camera, opacity, fog) and says `renderComposite()` resolves `RenderPass` to `ResolvedPass`. But it never specifies:
- Where does `fog` come from? OBJ-011's `setupScene` stores fog config per scene. The spec says "include fog config" but doesn't say where it's stored or how it's retrieved.
- Is the scene group lookup from the existing scene registry (the same one OBJ-011 D3 uses)?

An implementer reading only this spec would not know the data source for `ResolvedPass.fog`.

**Proposed fix:** State explicitly: "The `fog` field on `ResolvedPass` is read from the existing per-scene fog config stored during `setupScene()` (OBJ-011). The `group` field is the `THREE.Group` retrieved from the scene registry by `sceneId` (OBJ-011 D3). These are existing data structures; OBJ-037 does not modify the scene registry or setup path."

---

### MINOR — Issue 6: Test 9 Is the Differentiator But Has No Explicit Regression Guard

**The problem:** Test 9 ("Independent fades correctness — AC-09") is described as "the critical test that distinguishes render-target compositing from over-paint." The spec correctly notes that over-paint would give (54, 0, 77) while the correct answer is (77, 0, 77). But AC-09 only says "within ±2/255" — it doesn't explicitly state the *wrong* answer that must be rejected.

**Proposed fix:** Add to AC-09: "The result must NOT be approximately (54, 0, 77) ±5, which would indicate the over-paint bug from OBJ-011 D2 is still present."

---

### MINOR — Issue 7: Missing Error Handling for `compositeFrame()` Failures

**The problem:** The edge case table says `compositeFrame()` after `dispose()` is "undefined behavior." But what about WebGL context loss during compositing? Or a render target that fails to create (e.g., out of GPU memory)?

**Proposed fix:** Add to edge cases: "If `renderer.setRenderTarget()` fails or the WebGL context is lost during compositing, the error propagates to the `PageProtocol.renderFrame()` caller as a page-side error, caught by the existing `evaluate()` error handling (OBJ-009/OBJ-011). No special error handling is needed in the compositor beyond letting exceptions propagate."

---

### MINOR — Issue 8: Vocabulary Drift — "TransitionCompositor" is New Terminology

**The problem:** The seed vocabulary (Section 2) and AP-06 say "Do Not Invent New Terminology." `TransitionCompositor` is a new term not in the seed vocabulary. It's an internal implementation class name, not a vocabulary term, but the spec should acknowledge this.

**Proposed fix:** Add a brief note: "`TransitionCompositor` is an implementation class name, not a seed vocabulary term. It does not appear in the manifest schema, SKILL.md, or any LLM-facing interface."

---

### Summary

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| 1 | **Critical** | `MeshBasicMaterial` + `AdditiveBlending` double-attenuates via RT alpha | Needs ShaderMaterial fix |
| 2 | **Major** | RT clear color/alpha and autoClear state unspecified | Needs explicit steps |
| 3 | **Major** | `premultipliedAlpha` not resolved — affects compositing correctness | Needs concrete decision |
| 4 | **Major** | `renderComposite()` change scope ambiguous | Needs explicit boundary statement |
| 5 | **Major** | `ResolvedPass.fog` data source unspecified | Needs explicit reference to OBJ-011 storage |
| 6 | Minor | AC-09 doesn't explicitly reject the over-paint wrong answer | Add negative assertion |
| 7 | Minor | No error propagation spec for GPU failures | Add propagation statement |
| 8 | Minor | `TransitionCompositor` is new terminology | Add acknowledgment note |

Please address the critical and major issues in your revision. The core compositing approach is correct — it's the right architecture — but Issue 1 is a real correctness bug that would cause test failures.

---

## Round 3 — spec_author

All eight issues are valid. Let me address each and present the revised spec.

---

# Specification: OBJ-037 — Transition Renderer

## Summary

OBJ-037 delivers the `TransitionCompositor` — a page-side class (`src/page/transition-compositor.js`) that replaces OBJ-011's approximate over-paint compositing (D2) with mathematically correct weighted compositing via render targets and a custom `ShaderMaterial` with additive blending. It enables OBJ-036's complementary opacity model to produce correct visual output for all transition types. Each scene pass renders to an intermediate `WebGLRenderTarget` at full fidelity; a final compositing pass draws fullscreen quads using a shader that multiplies only by the pass opacity uniform (ignoring render target alpha), producing `finalPixel = Σ(scene_i_rgb × opacity_i)`. The `RenderFrameCommand` and `RenderPass` protocol types (OBJ-011) are unchanged — only the page-side `window.depthkit.renderComposite()` implementation evolves. Addresses TC-10 (transitions mask compositing seams).

**Terminology note:** `TransitionCompositor` is an implementation class name, not a seed vocabulary term. It does not appear in the manifest schema, SKILL.md, or any LLM-facing interface.

## Interface Contract

### Page-Side Class: `src/page/transition-compositor.js`

This class runs inside headless Chromium. Documented here as TypeScript for contract precision; implemented as plain JavaScript on the page.

```typescript
// Conceptual TypeScript contract — implemented as plain JS.

/**
 * Configuration for creating a TransitionCompositor.
 */
interface TransitionCompositorConfig {
  /** The Three.js WebGLRenderer instance (from window.depthkit.renderer). */
  renderer: THREE.WebGLRenderer;
  /** Composition width in pixels. */
  width: number;
  /** Composition height in pixels. */
  height: number;
}

/**
 * A resolved render pass ready for compositing.
 * Constructed by renderComposite() from the RenderFrameCommand's
 * RenderPass entries and the page's internal scene registry.
 *
 * The `group` field is the THREE.Group retrieved from the scene
 * registry by sceneId (OBJ-011 D3 — the internal Map<string, SceneEntry>
 * that setupScene() populates).
 *
 * The `fog` field is the per-scene fog config stored during
 * setupScene() (OBJ-011). Each scene's fog config is set as
 * scene.fog before rendering to that scene's render target.
 * OBJ-037 does not modify the scene registry or the setup path.
 */
interface ResolvedPass {
  /** The THREE.Group containing this scene's meshes. */
  group: THREE.Group;
  /** Camera state for this pass. */
  camera: { position: [number, number, number]; lookAt: [number, number, number]; fov: number };
  /** Opacity for this pass. Range [0, 1]. */
  opacity: number;
  /** Fog config for this scene (from scene registry), or null. */
  fog: FogConfig | null;
}

/**
 * Composites multi-pass frames with per-pass opacity using
 * render targets and a custom ShaderMaterial with additive blending.
 *
 * Replaces OBJ-011's sequential over-paint model (D2) with
 * correct weighted compositing: each scene renders to its own
 * render target at full fidelity, then fullscreen quads are
 * drawn with a ShaderMaterial that applies only the pass opacity
 * uniform (ignoring the render target's alpha channel).
 *
 * Compositing formula:
 *   finalPixel.rgb = Σ(renderTarget_i.rgb × opacity_i)
 *
 * This produces correct results for:
 * - Crossfade (complementary opacities, α + β = 1.0):
 *     pixel = A_rgb × α + B_rgb × (1-α)  [correct linear blend]
 * - Independent fades (sub-unity, α + β < 1.0):
 *     pixel = A_rgb × α + B_rgb × β      [dim, through black]
 * - Single pass at reduced opacity:
 *     pixel = A_rgb × α                  [fade to/from black]
 *
 * Lifecycle: create (at init) → compositeFrame (per frame) → dispose.
 * Immutable after construction (except resize).
 */
class TransitionCompositor {
  constructor(config: TransitionCompositorConfig);

  /**
   * Composite one or more scene passes into a single frame.
   *
   * Behavior by pass configuration:
   * - 0 passes: clears the canvas to black (gap frame).
   * - 1 pass, opacity === 1.0: renders directly to canvas.
   *   No render target used. Equivalent to OBJ-011's fast path.
   * - 1 pass, opacity < 1.0: renders to render target, composites
   *   at requested opacity over black background.
   * - 2+ passes: renders each to its own render target, composites
   *   all in order with additive blending.
   *
   * @param passes - Ordered array of resolved passes.
   * @param scene - The shared THREE.Scene (contains all scene groups).
   * @param camera - The shared THREE.PerspectiveCamera.
   */
  compositeFrame(
    passes: ResolvedPass[],
    scene: THREE.Scene,
    camera: THREE.PerspectiveCamera
  ): void;

  /**
   * Updates internal render target dimensions.
   * Existing render targets are disposed and new ones created
   * at the new dimensions. Must be called if composition
   * resolution changes.
   */
  resize(width: number, height: number): void;

  /**
   * Releases all GPU resources: render targets, compositing
   * ShaderMaterial, compositing geometry, compositing scene.
   * Must be called during page disposal (disposeAll).
   */
  dispose(): void;
}
```

### Change Boundary

**What changes:**
- `window.depthkit.renderComposite()` — the page-side function in `src/page/scene-renderer.js`. Specifically, OBJ-011 D2 steps 421–443 (the multi-pass composite path) are replaced with delegation to the `TransitionCompositor`. The function signature, error handling, and the single-pass fast path (D2 steps 414–419) are unchanged.
- `window.depthkit.init()` — creates the `TransitionCompositor` instance and stores it as `window.depthkit.compositor`.
- `window.depthkit.disposeAll()` — calls `compositor.dispose()` before existing cleanup.

**What does NOT change:**
- The Node-side `PageProtocol.renderFrame()` method (OBJ-011). It continues to call `window.depthkit.renderComposite()` via `bridge.evaluate()` with the same `RenderFrameCommand` payload.
- `RenderFrameCommand`, `RenderPass`, `RequiredCameraState`, and all other types in `src/engine/protocol-types.ts`.
- `window.depthkit.setupScene()` and `window.depthkit.teardownScene()`.
- The scene registry data structure (OBJ-011 D3).

### Modified `renderComposite()` Contract

```typescript
// The function still lives in src/page/scene-renderer.js.
// The method signature and error handling are UNCHANGED from OBJ-011.

/**
 * CHANGED BEHAVIOR (OBJ-037):
 *
 * Single-pass at opacity 1.0 (fast path): UNCHANGED from OBJ-011.
 *   - Set referenced scene group visible=true
 *   - Set all other scene groups visible=false
 *   - Set scene.fog from this scene's fog config
 *   - Apply camera state
 *   - renderer.render(scene, camera) with autoClear=true
 *
 * Multi-pass or any pass with opacity < 1.0:
 *   - Resolve each RenderPass to a ResolvedPass:
 *     - group: looked up from scene registry (OBJ-011 D3) by sceneId
 *     - fog: looked up from scene registry's per-scene fog config
 *     - camera: from pass.camera
 *     - opacity: from pass.opacity
 *   - Delegate to compositor.compositeFrame(resolvedPasses, scene, camera)
 *
 * Material opacity save/restore (OBJ-011 D2 steps 5c/5d/6)
 * is NO LONGER NEEDED. The compositor renders each scene to
 * its own render target at FULL material opacity. Per-pass
 * opacity is applied only during the compositing step via
 * the ShaderMaterial's uOpacity uniform.
 *
 * Fog handling CHANGES from OBJ-011 D10:
 * - Each pass's scene fog is set independently before rendering
 *   to that pass's render target (D6).
 * - No "primary scene" fog determination needed.
 */
renderComposite(command: RenderFrameCommand): Promise<void>;
```

### Page State Changes

```typescript
// Additions to window.depthkit internal state:

interface DepthkitPage {
  // ... existing state from OBJ-010, OBJ-011 ...

  /**
   * TransitionCompositor instance. Created during init().
   * Used by renderComposite() for multi-pass frames.
   * Disposed during disposeAll().
   */
  compositor: TransitionCompositor | null;
}
```

## Design Decisions

### D1: Render-Target Compositing with Custom ShaderMaterial

**Decision:** Multi-pass frames use intermediate `THREE.WebGLRenderTarget` instances. Each pass's scene renders to its own render target at full material opacity. A final compositing step draws fullscreen quads using a custom `THREE.ShaderMaterial` that samples the render target's RGB and multiplies only by a `uOpacity` uniform, ignoring the render target's alpha channel entirely.

**Compositing ShaderMaterial contract:**

Vertex shader:
```glsl
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
```

Fragment shader:
```glsl
uniform sampler2D tDiffuse;
uniform float uOpacity;
varying vec2 vUv;
void main() {
  vec4 texel = texture2D(tDiffuse, vUv);
  gl_FragColor = vec4(texel.rgb * uOpacity, uOpacity);
}
```

Material properties:
- `blending: THREE.CustomBlending`
- `blendSrc: THREE.OneFactor`
- `blendDst: THREE.OneFactor`
- `blendEquation: THREE.AddEquation`
- `depthTest: false`
- `depthWrite: false`
- `transparent: true`

**Blend equation:** `result.rgb = src.rgb × 1 + dst.rgb × 1` (pure additive). Since the fragment shader outputs `texel.rgb × uOpacity`, this produces `result.rgb += texel.rgb × uOpacity` per pass.

After all passes over a black-cleared canvas: `result.rgb = Σ(renderTarget_i.rgb × opacity_i)` ✓

**Why ShaderMaterial instead of MeshBasicMaterial:** `MeshBasicMaterial` with `AdditiveBlending` uses `GL_SRC_ALPHA` as the source factor. The fragment's alpha equals `texture.a × material.opacity`. For scenes containing transparent content (e.g., a subject plane with alpha texture), the render target's alpha is < 1.0 at those pixels. This would **double-attenuate** the result: `result += rt_rgb × rt_alpha × pass_opacity` instead of the correct `result += rt_rgb × pass_opacity`. The custom ShaderMaterial ignores the render target's alpha entirely, producing correct compositing for both opaque and transparent scene content.

**Why `gl_FragColor.a = uOpacity`:** The alpha output does not affect the RGB additive blending (both blend factors are `OneFactor`). Setting alpha to `uOpacity` rather than `1.0` avoids accumulating alpha > 1.0 across passes unnecessarily, though the alpha channel of the final canvas pixel is irrelevant to the captured output (see D3).

**Compositing algorithm:**

1. Save renderer state: current render target, clear color, clear alpha, autoClear.
2. For each pass with `opacity > 0`:
   a. `renderer.setRenderTarget(renderTargets[i])`.
   b. `renderer.setClearColor(0x000000, 0.0)` — black, fully transparent.
   c. `renderer.autoClear = true`.
   d. Set only this pass's scene group `visible = true`; all others `visible = false`.
   e. Set `scene.fog` from this pass's scene fog config (or `null`).
   f. Apply camera state (position, lookAt, fov, `camera.updateProjectionMatrix()`).
   g. `renderer.render(scene, camera)` — renders to the render target at full fidelity. autoClear=true clears the RT before rendering.
3. Switch to canvas: `renderer.setRenderTarget(null)`.
4. `renderer.setClearColor(0x000000, 1.0)` — opaque black.
5. `renderer.autoClear = true`.
6. `renderer.clear()` — clear canvas to opaque black.
7. `renderer.autoClear = false` — prevent subsequent compositing renders from clearing.
8. For each rendered pass (in order):
   a. Set ShaderMaterial uniform `tDiffuse` to `renderTargets[i].texture`.
   b. Set ShaderMaterial uniform `uOpacity` to `pass.opacity`.
   c. `renderer.render(compositeScene, compositeCamera)` — additive blend onto canvas.
9. Restore renderer state: original render target, clear color, clear alpha, autoClear.

**Why this replaces OBJ-011 D2:** OBJ-011's over-paint model with NormalBlending produces `pixel = B×β + A×α×(1-β)` for two passes. When OBJ-036 sends complementary opacities (α=0.7, β=0.3), the result is `0.3B + 0.49A` — incorrect. The correct result is `0.3B + 0.7A`. The render-target approach with additive blending produces `pixel = A×α + B×β = 0.7A + 0.3B` ✓

**OBJ-011 anticipated this:** D2 says "This is an approximation." OQ-A says "the page handler can be upgraded to render-target-based compositing. The protocol types would not change — only the page-side implementation." OBJ-037 implements this upgrade.

### D2: Single-Pass Fast Path Preserved

**Decision:** When `passes.length === 1` and `passes[0].opacity === 1.0`, `renderComposite()` renders directly to the canvas exactly as OBJ-011's fast path specifies — no render target, no compositing overhead. This is the common case for ~90% of frames.

**Opacity comparison:** Uses `=== 1.0` (exact equality). OBJ-036's `planFrame()` returns exactly `1.0` for non-transition frames. If edge cases produce `0.9999999`, the frame takes the compositor path — visually indistinguishable but slightly slower. The implementer may use a threshold like `>= 1.0 - 1e-9` as an optimization.

**Single-pass with opacity < 1.0** (dip_to_black fade): Uses the compositor. Renders scene to render target, composites at reduced opacity over black. This correctly produces a dimmed frame without modifying material opacities.

### D3: premultipliedAlpha Is Irrelevant to Captured Output

**Decision:** The `premultipliedAlpha` setting on `THREE.WebGLRenderer` (default: `true`) does not affect compositing correctness for the depthkit pipeline. This is a concrete design decision, not a deferred question.

**Reasoning:**

1. **Render targets are independent of premultipliedAlpha.** The RT clear color is set to `(0, 0, 0, 0.0)` with `setClearColor(0x000000, 0.0)`. Scenes render to RTs with their native alpha. `premultipliedAlpha` only affects the final canvas-to-display compositing.

2. **The compositing ShaderMaterial controls final output.** The fragment shader outputs `vec4(texel.rgb * uOpacity, uOpacity)`. With `CustomBlending(OneFactor, OneFactor)`, the RGB result is purely additive — the blend factors ignore alpha entirely.

3. **Canvas alpha is irrelevant to frame capture.** Puppeteer's `Page.captureScreenshot` (CDP) and `canvas.toDataURL('image/png')` both capture the RGB values of the canvas. The `premultipliedAlpha` setting affects how the browser composites the canvas against the page background for display, but depthkit never displays the page — it only captures pixel buffers.

4. **The opaque black canvas clear (step 4–5 of D1) ensures alpha=1.0 before compositing.** After additive passes, the canvas alpha accumulates but is clamped to 1.0. Since the starting alpha is 1.0 (opaque black clear) and the blend function is additive, final alpha ≥ 1.0 (clamped to 1.0). This means `premultipliedAlpha` has no visible effect even in a hypothetical display scenario.

**Conclusion:** OBJ-037 does not require any specific `premultipliedAlpha` setting. The spec does not constrain OBJ-010's renderer configuration on this parameter.

### D4: Render Target Pool

**Decision:** The compositor pre-allocates 2 render targets at construction. This covers the expected maximum concurrent passes (OBJ-036 D11 warns when >2 scenes overlap). If more passes are needed, additional render targets are created on demand and retained for future frames.

**Render target specification:**
- Size: `width × height` (from config).
- Format: `THREE.RGBAFormat`.
- Type: `THREE.UnsignedByteType` (8-bit per channel, matching canvas precision).
- MinFilter/MagFilter: `THREE.LinearFilter`.
- `depthBuffer: true` — required for correct depth sorting within each scene.
- `stencilBuffer: false` — V1 has no stencil-based effects.

**Memory footprint:** 2 render targets at 1920×1080×4 bytes = ~16MB GPU memory. Acceptable for the target hardware (C-08).

### D5: Compositing Geometry — Fullscreen Quad with Orthographic Camera

**Decision:** The compositor creates a dedicated `THREE.Scene` ("composite scene") containing a single `THREE.Mesh` with `THREE.PlaneGeometry(2, 2)` and a `THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)`. The mesh uses the custom `THREE.ShaderMaterial` described in D1.

The mesh's `tDiffuse` and `uOpacity` uniforms are updated per-pass; the geometry, camera, and scene are reused across all frames.

### D6: Per-Scene Fog Replaces OBJ-011 D10 "Primary Scene" Fog

**Decision:** With render targets, each scene renders independently in its own render target with its own fog configuration. There is no "primary scene" fog determination.

**Before (OBJ-011 D10):** Determine the primary scene (highest opacity pass), set fog from its config, use that fog for ALL passes.

**After (OBJ-037):** Each pass sets `scene.fog` from its own scene's fog config (retrieved from the scene registry populated by `setupScene()`, OBJ-011) before rendering to its render target. Each scene's fog is correct for that scene. During crossfade between a foggy scene and a non-foggy scene, each renders with its own fog setting, and the compositing blend produces a natural visual transition between fog states.

**For the single-pass fast path:** Fog handling is unchanged from OBJ-011 — set fog from the single scene's config before rendering.

### D7: No Material Opacity Modification

**Decision:** The compositor renders each scene to its render target at **full material opacity**. OBJ-011's steps 5c/5d/6 (save material opacities → modify → render → restore) are eliminated for the compositor path. Per-pass opacity is applied exclusively during the compositing step via the ShaderMaterial's `uOpacity` uniform.

**Rationale:** This is a major simplification. OBJ-011's approach of traversing all meshes to save/modify/restore opacities was a workaround for the lack of render targets. With render targets, the scene renders at full fidelity; opacity is applied as a post-process. This eliminates:
- Material traversal per multi-pass frame
- Risk of state leakage if restoration fails
- Interaction bugs between pass-level opacity and per-material transparency (e.g., a subject plane with alpha texture)

### D8: Skip Zero-Opacity Passes

**Decision:** Passes with `opacity === 0.0` are skipped entirely — no render target is used, no compositing quad is drawn. A fully transparent pass contributes nothing to the final image.

**Rationale:** At the boundaries of transitions (first frame of crossfade incoming, or last frame of a fade), one pass has opacity 0.0. Skipping it saves one render target fill and one compositing draw call per such frame.

### D9: Compositor Created at init(), Disposed at disposeAll()

**Decision:** The `TransitionCompositor` is created during `window.depthkit.init()` and stored as `window.depthkit.compositor`. It is disposed during `window.depthkit.disposeAll()`. The compositor's lifecycle matches the renderer's lifecycle.

**Rationale:** Eager creation avoids render-target allocation during the first transition frame (which could cause a timing hiccup in the frame capture pipeline). The memory cost (D4: ~16MB) is constant and acceptable.

### D10: Compositor is a Page-Side Module Only

**Decision:** `TransitionCompositor` runs inside headless Chromium. It requires `THREE.WebGLRenderer` and other WebGL-dependent classes. It is NOT isomorphic. No Node.js-side changes are needed — the orchestrator continues to construct `RenderFrameCommand` per OBJ-036's Orchestrator Integration Contract, and the page protocol transmits it unchanged.

### D11: Depth Buffer Handling in Render Targets

**Decision:** Each render target has its own depth buffer (`depthBuffer: true`). When rendering a scene to its render target, Three.js's default depth testing (`GL_LESS`) applies — meshes within the scene depth-sort correctly against each other.

The compositing quads disable depth testing (`depthTest: false, depthWrite: false`). They are drawn in pass order; since the additive blending is commutative for the RGB result, the order does not affect the final pixel color, but the convention (outgoing first) is maintained for consistency with OBJ-036's `FramePlan.passes` ordering.

**Replaces OBJ-011's `clearDepth()` per pass:** OBJ-011 needed `renderer.clearDepth()` between passes to prevent cross-scene depth rejection. With render targets, each scene has its own depth buffer — no cross-scene depth interaction occurs.

### D12: Error Propagation for GPU Failures

**Decision:** The compositor does not implement special error handling for GPU failures (WebGL context loss, render target creation failure, out-of-memory). If `renderer.setRenderTarget()` fails or the WebGL context is lost during compositing, the error propagates naturally through the call stack to `window.depthkit.renderComposite()`, which is called via `bridge.evaluate()`. The existing error handling in the `evaluate()` pipeline (OBJ-009/OBJ-011) catches page-side exceptions and surfaces them as `PageProtocolError` on the Node side. No compositor-specific error handling is needed beyond letting exceptions propagate.

## Acceptance Criteria

### Core Compositing Correctness

- [ ] **AC-01:** A single pass with `opacity: 1.0` produces output pixel-identical to a direct `renderer.render(scene, camera)` call. No intermediate render target is used (fast path preserved from OBJ-011).
- [ ] **AC-02:** A single pass with `opacity: 0.5` produces an image where every non-zero pixel's RGB values are approximately half those of the full-opacity render, within ±2/255 per channel (8-bit quantization tolerance).
- [ ] **AC-03:** A single pass with `opacity: 0.0` produces a fully black frame (all pixels RGB ≤ 1/255).
- [ ] **AC-04:** Zero passes (empty array) produces a fully black frame.

### Crossfade Compositing (Complementary Opacities)

- [ ] **AC-05:** Two passes with opacities `(0.5, 0.5)` rendering solid red (scene A) and solid blue (scene B) produce pixels ≈ `(128, 0, 128)` within ±2/255 per channel. This is the correct average — `A×0.5 + B×0.5`.
- [ ] **AC-06:** Two passes with `(1.0, 0.0)` produce an image identical to rendering only the first scene at full opacity.
- [ ] **AC-07:** Two passes with `(0.0, 1.0)` produce an image identical to rendering only the second scene at full opacity.
- [ ] **AC-08:** Two passes with `(0.7, 0.3)` produce pixels ≈ `A×0.7 + B×0.3` within ±2/255 per channel. Specifically, for solid red A and solid blue B: `(179, 0, 77)` ±2.

### Independent Fade Compositing (Sub-Unity Opacities)

- [ ] **AC-09:** Two passes with `(0.3, 0.3)` produce pixels ≈ `A×0.3 + B×0.3` within ±2/255. For solid red A and blue B: `(77, 0, 77)` ±2. The result must NOT be approximately `(54, 0, 77)` ±5, which would indicate the over-paint bug from OBJ-011 D2 is still present (outgoing red attenuated by `(1 - 0.3)` = `0.7 × 0.3 × 255 ≈ 54`).
- [ ] **AC-10:** Two passes with `(0.0, 0.0)` produce a fully black frame.

### Transition Type Correctness (End-to-End)

- [ ] **AC-11:** **Crossfade**: A 2-scene composition with OBJ-036 crossfade opacities (complementary, summing to 1.0) renders correctly. At the midpoint frame (opacities ~0.5/0.5), both scenes are equally visible. At boundaries, only one scene is visible.
- [ ] **AC-12:** **Dip-to-black**: A 2-scene composition with OBJ-036 independent fades produces frames that fade to black between scenes. The midpoint frame (both opacities near 0) is near-black.
- [ ] **AC-13:** **Cut**: A 2-scene composition with cut transition renders as a single pass at full opacity per frame. The fast path is used (no render targets).

### Fog Handling

- [ ] **AC-14:** During a crossfade between a scene with fog (color #000000, near 10, far 40) and a scene without fog, each scene's render target correctly applies (or omits) fog for its own content. The fog does not leak between scenes.

### Optimization

- [ ] **AC-15:** Passes with `opacity === 0.0` are not rendered to a render target and no compositing quad is drawn for them.
- [ ] **AC-16:** Single-pass frames at `opacity === 1.0` do not allocate or use render targets.

### Scene-Internal Transparency

- [ ] **AC-17:** A scene containing a plane with alpha-transparent texture (e.g., a subject with `transparent: true, opacity: 0.5` on the material) renders correctly to the render target. When composited at pass opacity 0.5, the semi-transparent pixels are attenuated by the pass opacity only (not double-attenuated by the render target's alpha). For a scene with a solid red plane at material opacity 0.5 against black, composited at pass opacity 0.5: the red pixels should be ≈ `(64, 0, 0)` ±2 (i.e., `255 × 0.5 × 0.5`). The result must NOT be ≈ `(32, 0, 0)` which would indicate alpha double-attenuation.

### Resource Management

- [ ] **AC-18:** `dispose()` releases all render targets, compositing ShaderMaterial, compositing geometry, and the compositing scene. No WebGL resource leaks after disposal.
- [ ] **AC-19:** `resize()` updates render target dimensions. Subsequent `compositeFrame()` calls produce output at the new resolution.

### OBJ-011 Behavioral Parity

- [ ] **AC-20:** OBJ-011's AC-17 still passes: a two-pass frame with opacity (1.0, 0.5) renders both scenes composited into a single frame that is visually distinct from either scene alone.
- [ ] **AC-21:** OBJ-011's AC-18 still passes: a single pass at opacity 0.0 produces a black frame.
- [ ] **AC-22:** OBJ-011's AC-19 still passes: single pass at opacity 1.0 produces the same output as before the upgrade.
- [ ] **AC-23:** OBJ-011's AC-20 still passes: after multi-pass rendering, a subsequent single-pass render at full opacity produces the same output as before the multi-pass frame. (Material opacities are never modified, so this is inherently satisfied by D7.)

### Renderer State Restoration

- [ ] **AC-24:** After a multi-pass `compositeFrame()` call, the renderer's render target, clear color, clear alpha, and autoClear settings are restored to their pre-call values. A subsequent single-pass fast-path render produces correct output without state contamination.

### Determinism

- [ ] **AC-25:** Rendering the same passes with the same scenes/cameras/opacities produces identical pixel output across multiple calls on the same hardware (deterministic per C-05).

### Performance

- [ ] **AC-26:** A multi-pass compositing frame (2 passes) completes within 2.5× the time of a single-pass frame at the same resolution, measured on a software WebGL renderer. This verifies that the render-target overhead is bounded.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| Empty passes array | Clear canvas to opaque black. No render targets used. |
| Single pass, `opacity === 1.0` | Direct render (fast path). No render target. |
| Single pass, `opacity === 0.0` | Skip rendering entirely. Canvas cleared to opaque black. |
| Single pass, `0 < opacity < 1.0` | Render to RT, composite at opacity over black. |
| Two passes, both `opacity === 0.0` | Both skipped. Canvas remains opaque black. |
| Two passes, complementary opacities | Correct weighted blend: `A_rgb × α + B_rgb × (1-α)`. |
| Two passes, independent fades | Correct additive: `A_rgb × α + B_rgb × β`, dim result. |
| Three or more passes | All render to separate RTs. Additional RTs created on demand. Additive composite of all. |
| Pass with `opacity > 1.0` | Compositor does not clamp. ShaderMaterial applies `uOpacity` directly. Pixels may clip to white. Caller's responsibility (OBJ-036 never produces this). |
| Pass with `opacity < 0.0` | ShaderMaterial applies negative `uOpacity` — produces negative RGB contributions (clamped to 0 by WebGL). Effectively treated as 0.0. |
| Scene with no meshes (empty group) | Renders as black to the RT. Contributes black × opacity = black. |
| Scene with transparent meshes (alpha textures) | Scene renders with alpha to RT. ShaderMaterial ignores RT alpha, applies only pass opacity. No double-attenuation. |
| Scene with fog | Fog applied correctly in this scene's RT. Does not affect other scenes' RTs. |
| `compositeFrame()` called after `dispose()` | Undefined behavior. Caller must not call after disposal. The compositor does not guard against this. |
| `resize()` to different aspect ratio | Render targets recreated at new size. Compositing geometry unchanged (fullscreen quad is aspect-ratio independent with ortho camera). |
| Very large composition (4K: 3840×2160) | Render targets may exceed GPU memory on software renderer. No explicit guard — WebGL context loss would propagate as an error through `evaluate()` (D12). |
| WebGL context loss during compositing | Error propagates to `renderComposite()` caller. Caught by existing `evaluate()` error handling (OBJ-009/OBJ-011). See D12. |
| Renderer state contamination after compositing | D1 steps 1 and 9 save and restore renderer state (render target, clear color, clear alpha, autoClear). AC-24 verifies this. |

## Test Strategy

### Test Environment

Testing requires a WebGL context (Three.js rendering). Tests run in Puppeteer with a headless Chromium instance, consistent with the depthkit rendering environment.

### Compositor-Focused Tests: `test/integration/transition-compositor.test.ts`

**Setup:** Each test creates a minimal Three.js environment inside Puppeteer, sets up the compositor, creates test scenes with solid-color planes at known positions.

**Solid-color scene factory:** Create scenes with a single `MeshBasicMaterial({ color: 0xff0000 })` plane filling the camera view. Use red (scene A), blue (scene B), and green (scene C) for arithmetic verification.

**Tests:**

1. **Fast path equivalence (AC-01):** Render scene A at opacity 1.0 via compositor. Render scene A via direct `renderer.render()`. Compare pixel buffers — must be identical.
2. **Half-opacity fade (AC-02):** Render solid red at opacity 0.5. Sample center pixel. Verify R ≈ 128 ±2, G = 0, B = 0.
3. **Zero-opacity black (AC-03):** Render at opacity 0.0. Verify all-black output.
4. **Empty passes black (AC-04):** Render with empty array. Verify all-black.
5. **Crossfade midpoint (AC-05):** Red at 0.5, blue at 0.5. Verify center pixel ≈ (128, 0, 128) ±2.
6. **Crossfade 100/0 (AC-06):** Red at 1.0, blue at 0.0. Verify pure red.
7. **Crossfade 0/100 (AC-07):** Red at 0.0, blue at 1.0. Verify pure blue.
8. **Crossfade 70/30 (AC-08):** Red at 0.7, blue at 0.3. Verify ≈ (179, 0, 77) ±2.
9. **Independent fades correctness (AC-09):** Red at 0.3, blue at 0.3. Verify ≈ (77, 0, 77) ±2. **This is the critical test that distinguishes render-target compositing from OBJ-011's over-paint.** Assert result is NOT ≈ (54, 0, 77) ±5.
10. **Both zero (AC-10):** Red at 0.0, blue at 0.0. Verify all-black.
11. **Three-pass compositing:** Red 0.33, green 0.33, blue 0.34. Verify ≈ (84, 84, 87) ±3.
12. **Zero-opacity skip (AC-15):** Two passes, one at 0.0. Verify the zero-opacity pass produces no visible contribution. Timing-based verification optional.
13. **Fog isolation (AC-14):** Scene A with black fog (near=1, far=5). Scene B with no fog. Crossfade at 0.5/0.5. Verify that scene A planes show fog attenuation in their contribution while scene B planes do not.
14. **Alpha transparency — no double-attenuation (AC-17):** Scene A with a red plane at material opacity 0.5 (`transparent: true`). Render at pass opacity 0.5. Center pixel R channel ≈ 64 ±2 (`255 × 0.5 × 0.5`). Assert R is NOT ≈ 32 ±5 (which would indicate double-attenuation via RT alpha).
15. **Resize (AC-19):** Create at 1920×1080, resize to 960×540, render. Verify output is at new resolution.
16. **Dispose (AC-18):** Call dispose(), verify no errors. A subsequent init()+create should work (no leaked state).
17. **Determinism (AC-25):** Render same frame 10 times, compare all pixel buffers — must be identical.
18. **Performance (AC-26):** Time 100 single-pass renders and 100 two-pass renders. Two-pass average should be < 2.5× single-pass average.
19. **Renderer state restoration (AC-24):** Execute multi-pass compositeFrame(), then immediately execute single-pass fast-path render. Verify the fast-path output is unaffected by the prior multi-pass call (renderer state fully restored).

### End-to-End Tests: `test/integration/transition-rendering.test.ts`

These test transitions through the full pipeline (manifest → orchestrator → protocol → compositor → capture).

20. **Crossfade end-to-end (AC-11):** 2-scene manifest with 0.5s crossfade. Render all frames. Sample frames at: pre-transition (only scene A), mid-transition (both blended), post-transition (only scene B). Verify blend progression.
21. **Dip-to-black end-to-end (AC-12):** 2-scene manifest with 1.0s dip_to_black on both scenes. Verify fade-out frames darken, midpoint is near-black, fade-in frames brighten.
22. **Cut end-to-end (AC-13):** 2-scene manifest with cut. Verify instant switch — no blended frames, all frames use single-pass fast path.
23. **OBJ-011 parity (AC-20–23):** Re-run OBJ-011's multi-pass tests (AC-17 through AC-20) against the new compositor to verify behavioral parity.

### Relevant Testable Claims

- **TC-10** (Cross-scene transitions mask compositing seams): Tests 20–22 validate that all three transition types produce smooth, artifact-free scene boundaries.
- **TC-06** (Deterministic output): Test 17 confirms compositor determinism.

## Integration Points

### Depends on

| Dependency | What OBJ-037 uses | How |
|---|---|---|
| **OBJ-036** (Scene Sequencer) | `FramePlan.passes` opacity values (indirectly) | The orchestrator maps `FramePlan.passes` to `RenderFrameCommand.passes`. The compositor receives these via the protocol. OBJ-037 does not import OBJ-036 directly. |
| **OBJ-008** (Transition Type Contract) | Transition semantics (indirectly) | OBJ-008 defines the transition types whose opacities OBJ-036 computes. The compositor is agnostic to transition types — it correctly renders any opacity values. |
| **OBJ-011** (Page Protocol) | `RenderFrameCommand`, `RenderPass`, `renderComposite()` method, scene registry (D3), per-scene fog config | OBJ-037 modifies the implementation of `renderComposite()` to use the compositor for multi-pass frames. Protocol types unchanged. Scene registry and fog config accessed as existing data structures from `setupScene()`. |
| **OBJ-010** (Page Shell) | `window.depthkit` namespace, `renderer`, `scene`, `camera` | The compositor uses the existing Three.js renderer, scene, and camera. Created during `init()`, stored on `window.depthkit`. |
| **Three.js** | `WebGLRenderTarget`, `ShaderMaterial`, `PlaneGeometry`, `OrthographicCamera`, `Scene`, `Mesh`, `CustomBlending`, `OneFactor`, `AddEquation` | Core GPU rendering primitives for render targets and compositing. |

### Consumed by

| Downstream | How it uses OBJ-037 |
|---|---|
| **OBJ-068** (Transition visual tuning) | Requires working transition rendering to produce test renders for Director Agent review. |
| **OBJ-077** (Integration) | Full pipeline integration requires correct transitions. |

### File Placement

```
depthkit/
  src/
    page/
      transition-compositor.js   # NEW — TransitionCompositor class
      scene-renderer.js          # MODIFIED — renderComposite() delegates
                                 #   to compositor for multi-pass frames;
                                 #   init() creates compositor;
                                 #   disposeAll() disposes compositor
  test/
    integration/
      transition-compositor.test.ts   # NEW — compositor-focused tests
      transition-rendering.test.ts    # NEW — end-to-end transition tests
```

## Open Questions

### OQ-A: Should the compositor support a configurable clear color?

The compositor always clears the canvas to opaque black `(0, 0, 0, 1)` before compositing. A future `dip_to_white` transition would need a white clear color. The simplest extension: accept an optional `clearColor` in `compositeFrame()` or as a compositor config option.

**Recommendation:** Defer. Seed Section 2 defines only `dip_to_black`. If `dip_to_white` is added, extend the compositor config.

### OQ-B: Should render targets use floating-point format?

`THREE.UnsignedByteType` (8-bit per channel) introduces ±1/255 quantization per render target. For 2-pass compositing, the cumulative error is ±2/255 — imperceptible. `THREE.HalfFloatType` (16-bit) eliminates this but doubles GPU memory (32MB for 2 targets at 1080p).

**Recommendation:** Use `UnsignedByteType` for V1. The ±2/255 tolerance is included in all acceptance criteria. Upgrade to `HalfFloatType` if OBJ-068 (visual tuning) identifies banding artifacts during transitions.

---

I believe this revision addresses all eight issues raised:

1. **Critical (ShaderMaterial):** D1 and D5 fully rewritten around a custom `THREE.ShaderMaterial` with explicit GLSL and `CustomBlending(OneFactor, OneFactor)`. AC-17 explicitly tests for no double-attenuation.
2. **Major (RT clear):** D1 compositing algorithm now has explicit numbered steps for `setClearColor`, `autoClear`, and state save/restore.
3. **Major (premultipliedAlpha):** Elevated from OQ-C to D3 with concrete reasoning for why it's irrelevant. No longer an open question.
4. **Major (change boundary):** New "Change Boundary" section explicitly lists what changes and what does not, referencing OBJ-011 D2 step numbers.
5. **Major (ResolvedPass.fog source):** `ResolvedPass` JSDoc now explicitly states the data source. D6 references OBJ-011's `setupScene()` registry.
6. **Minor (AC-09 negative):** AC-09 now includes explicit "must NOT be approximately (54, 0, 77)" assertion with explanation.
7. **Minor (error propagation):** New D12 specifies error propagation behavior.
8. **Minor (terminology):** Summary now has explicit note about `TransitionCompositor` not being a seed vocabulary term.

New addition: AC-24 + Test 19 for renderer state restoration (arose from the explicit save/restore steps in D1).

Challenger, please verify these revisions address your concerns.
