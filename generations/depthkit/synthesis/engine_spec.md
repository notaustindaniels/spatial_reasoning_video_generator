# Consolidated Engine Specification — depthkit

> **Generated:** 2026-03-23 | **Category:** engine | **Mode:** CHUNK
> **Source Nodes:** OBJ-002, OBJ-004, OBJ-009, OBJ-010, OBJ-011, OBJ-012, OBJ-013, OBJ-014, OBJ-015, OBJ-016, OBJ-017, OBJ-035, OBJ-036, OBJ-038, OBJ-039, OBJ-040, OBJ-041, OBJ-046, OBJ-047, OBJ-048, OBJ-049, OBJ-058

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Dependency Order](#2-dependency-order)
3. [Tier 0 — Foundational Primitives](#3-tier-0--foundational-primitives)
4. [Tier 1 — Core Infrastructure](#4-tier-1--core-infrastructure)
5. [Tier 2 — Protocol, Capture & Encoding](#5-tier-2--protocol-capture--encoding)
6. [Tier 3 — Sequencing & Timing](#6-tier-3--sequencing--timing)
7. [Tier 4 — Configuration & Error Handling](#7-tier-4--configuration--error-handling)
8. [Tier 5 — Orchestration](#8-tier-5--orchestration)
9. [Tier 6 — External Interfaces](#9-tier-6--external-interfaces)
10. [Cross-Cutting: Spatial Integration](#10-cross-cutting-spatial-integration)
11. [Integration Boundary Map](#11-integration-boundary-map)
12. [Inconsistencies & Open Conflicts](#12-inconsistencies--open-conflicts)
13. [Consolidated File Manifest](#13-consolidated-file-manifest)
14. [Consolidated Acceptance Criteria Index](#14-consolidated-acceptance-criteria-index)

---

## 1. Architecture Overview

depthkit is a zero-license 2.5D video engine built on Three.js (MIT), Puppeteer (Apache-2.0), ffmpeg-static (LGPL/GPL via stdio), Zod (MIT), and Commander (MIT). The architecture follows the **Dumb Page / Smart Orchestrator** pattern (OBJ-010 D1):

- **Node.js side** holds all domain logic: manifest parsing, geometry definitions, camera path presets, scene sequencing, the virtualized clock, and frame-by-frame camera state computation.
- **Browser side** is a generic, data-driven Three.js renderer that receives pre-computed state per frame and executes Three.js API calls.

The **Virtualized Clock** (C-03) eliminates `requestAnimationFrame`. Every frame is rendered deterministically by the orchestrator calling `page.evaluate()` with computed state, then capturing the result via CDP.

### Rendering Pipeline (seed Section 4.4)

```
Manifest JSON
    │
    ▼
[Manifest Validation] ─── OBJ-004/OBJ-016/OBJ-017
    │
    ▼
[Scene Timing Resolution] ─── OBJ-038
    │
    ▼
[Scene Sequencing] ─── OBJ-036
    │
    ▼
[Browser Launch + Page Init] ─── OBJ-009/OBJ-010/OBJ-049
    │
    ▼
For each frame (FrameClock iterator):
  ├─ planFrame() → active scenes, opacity, normalizedTime
  ├─ Scene setup/teardown via PageProtocol ─── OBJ-011/OBJ-039
  ├─ Camera state computation (from spatial/camera registries)
  ├─ renderFrame() via PageProtocol ─── OBJ-011
  ├─ Frame capture ─── OBJ-012
  └─ Write to FFmpeg ─── OBJ-013
    │
    ▼
[FFmpeg finalize → video-only MP4]
    │
    ▼
[Audio mux (if audio present)] ─── OBJ-014
    │
    ▼
Final MP4
```

---

## 2. Dependency Order

Modules are organized into tiers by dependency depth. Each tier depends only on modules in earlier tiers (or external dependencies).

| Tier | Modules | Description |
|------|---------|-------------|
| **0** | OBJ-002, OBJ-004 | Foundational primitives (math, schema) — no engine deps |
| **1** | OBJ-009, OBJ-010, OBJ-016, OBJ-017 | Core infrastructure (clock, bridge, page shell, validation) |
| **2** | OBJ-011, OBJ-015, OBJ-039, OBJ-012, OBJ-013, OBJ-014 | Protocol, texture, geometry materialization, capture, encoding |
| **3** | OBJ-036, OBJ-038 | Scene sequencing and audio sync timing |
| **4** | OBJ-049, OBJ-048 | Rendering config, error handling |
| **5** | OBJ-035 | Orchestrator — composes everything |
| **6** | OBJ-046, OBJ-047, OBJ-058 | CLI, Library API, Director Agent tools |
| **X** | OBJ-040, OBJ-041 | Cross-cutting spatial integration |

---

## 3. Tier 0 — Foundational Primitives

### 3.1 OBJ-002 — Interpolation, Easing, and Spring Utilities

**Files:** `src/interpolation/{easings,interpolate,spring,index}.ts`

Pure math primitives underpinning all animation. Zero dependencies, isomorphic (Node.js only in Dumb Page architecture — OBJ-010 D1 confirmed interpolation runs only on Node side).

**Key Exports:**
- `interpolate(value, inputRange, outputRange, options?)` — range mapping with easing
- `spring(frame, fps, config?)` — damped spring physics
- 6 named easings: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`
- `getEasing(name)`, `isEasingName(name)` — runtime lookup

**Critical Design Decisions:**
- **D2:** Two-element ranges only (no multi-segment)
- **D3:** Clamp by default; `extend` mode uses linear extrapolation (easing NOT applied outside [0,1])
- **D7:** Fail-fast on NaN/non-finite — prevents corrupt frames reaching Three.js

**Acceptance Criteria:** AC-01 through AC-26 (26 total). See OBJ-002 spec for full list.

> **Integration Boundary → spatial:** Consumed by camera path presets (OBJ-006) and transition system (OBJ-008) from the spatial category.

---

### 3.2 OBJ-004 — Manifest Schema Core

**Files:** `src/manifest/schema.ts`

Zod validation schemas for the manifest JSON contract. Defines all types (`Manifest`, `Scene`, `Composition`, `Audio`, `Transition`, `CameraParams`, `PlaneRef`), the `ManifestRegistry` interface, and error types.

**Key Exports:**
- Zod schemas: `ManifestSchema`, `SceneSchema`, `CompositionSchema`, `TransitionSchema`, `CameraParamsSchema`, `PlaneRefSchema`, `AudioSchema`
- Registry: `ManifestRegistry`, `GeometryRegistration`, `CameraRegistration`, `PlaneSlotDef`, `createRegistry()`
- Validation: `ManifestError`, `ManifestResult`

**Critical Design Decisions:**
- **D-01:** Two-phase validation (structural Zod + semantic registry)
- **D-03:** Geometry's `compatibleCameras` is authoritative for validation (camera's `compatibleGeometries` is informational only)
- **D-04:** `start_time` is explicit, not computed
- **D-12:** Integer FPS with bounds [1, 120]
- **D-14:** `.strict()` on sub-schemas (catches typos), `.passthrough()` at top level

**Error Codes:** `UNKNOWN_GEOMETRY`, `UNKNOWN_CAMERA`, `INCOMPATIBLE_CAMERA`, `MISSING_REQUIRED_SLOT`, `UNKNOWN_SLOT`, `DUPLICATE_SCENE_ID`, `SCENE_OVERLAP`, `CROSSFADE_NO_ADJACENT`, `SCENE_GAP` (warning), `SCENE_ORDER_MISMATCH` (warning), `AUDIO_DURATION_MISMATCH` (warning), `FOV_WITHOUT_SUPPORT` (warning), `INVALID_JSON`, `FILE_NOT_FOUND`

**Acceptance Criteria:** AC-01 through AC-34 (34 total).

> **Integration Boundary → spatial:** `GeometryRegistration` and `CameraRegistration` are populated by OBJ-005 (geometry base) and OBJ-006 (camera presets) from the spatial category. `ManifestRegistry` is the validation-only registry; full spatial data lives in separate `GeometryRegistry` and `CameraPathRegistry` types.

---

## 4. Tier 1 — Core Infrastructure

### 4.1 OBJ-009 — FrameClock and PuppeteerBridge

**Files:** `src/engine/frame-clock.ts`, `src/engine/puppeteer-bridge.ts`

#### FrameClock
Pure, immutable utility for deterministic frame-to-timestamp mapping. No scene awareness.

- `frameToTimestamp(frame)` → seconds
- `timestampToFrame(timestamp)` → frame number (Math.round + clamp)
- `frames()` → Generator<FrameTick> (canonical render loop iterator)
- `FrameClock.fromDuration(fps, seconds)` → factory

#### PuppeteerBridge
Lifecycle manager for headless Chromium. Launches browser, loads page shell, sets viewport, exposes `evaluate()`.

- `launch()` / `close()` — browser lifecycle
- `evaluate(fn, ...args)` — typed `page.evaluate()` wrapper
- `captureFrame()` — convenience screenshot (superseded by OBJ-012 in production)
- `isLaunched` / `page` — state accessors

**Critical Design Decisions:**
- Bridge does NOT call `window.depthkit.init()` — that's OBJ-011/OBJ-035's responsibility
- `deviceScaleFactor: 1` enforced for 1:1 pixel mapping
- `pageerror` listener surfaces uncaught browser exceptions
- `gpu` flag controls `--disable-gpu`; supplementary args come from OBJ-049

**Acceptance Criteria:** AC-01 through AC-32 (OBJ-009 spec).

---

### 4.2 OBJ-010 — Three.js Page Shell and Scene Renderer

**Files:** `src/page/index.html`, `src/page/scene-renderer.js`, `src/page/geometry-library.js` (stub), `src/page/message-handler.js` (stub), `src/engine/page-types.ts`

The browser-side rendering foundation. Exposes `window.depthkit` with:
- `init(config)` — creates WebGLRenderer + PerspectiveCamera + Scene
- `renderFrame(cameraState?)` — applies camera state, calls `renderer.render()`
- `dispose()` — full resource cleanup
- `getRendererInfo()` — WebGL diagnostics
- `isInitialized()`, `renderer`, `scene`, `camera` — state accessors

**Node-side types** (`page-types.ts`): `PageInitConfig`, `RendererInfo`, `FrameCameraState`

**Critical Design Decisions:**
- **D1 (Dumb Page):** Browser is a data-driven renderer — no domain logic
- **D3:** `preserveDrawingBuffer: true` by default (required for canvas-png capture)
- **D4:** `antialias: false` by default (determinism C-05)
- **D8:** Unlit rendering (`MeshBasicMaterial`) — lighting deferred per OQ-09
- Camera state application order: position → lookAt → fov + updateProjectionMatrix

**Acceptance Criteria:** AC-01 through AC-20 (OBJ-010 spec).

> **Integration Boundary → spatial:** Camera defaults (fov: 50, near: 0.1, far: 100, position: [0,0,5], lookAt: [0,0,0]) hardcoded to match OBJ-003's `DEFAULT_CAMERA` from the spatial category.

---

### 4.3 OBJ-016 — Manifest Loader and Validator

**Files:** `src/manifest/loader.ts`

Implements OBJ-004's validation interface. Two-phase pipeline:
- Phase 1: `parseManifest(raw)` — Zod structural validation
- Phase 2: `validateManifestSemantics(manifest, registry)` — registry-backed checks
- Combined: `loadManifest(raw, registry)`, `loadManifestFromFile(path, registry)`
- Utility: `computeTotalDuration(manifest)`

**Key Behaviors:**
- All errors collected at once (not one-at-a-time)
- Phase 2 skipped entirely if Phase 1 fails
- Per-scene slot checks skipped if geometry is unknown (skip-on-unknown pattern)
- Adds `FILE_READ_ERROR` code beyond OBJ-004's table
- Audio duration comparison uses ±0.01s tolerance
- Scene overlap uses 1ms floating-point tolerance

**Acceptance Criteria:** AC-01 through AC-31 (OBJ-016 spec).

---

### 4.4 OBJ-017 — Geometry-Specific Structural Validation

**Files:** `src/manifest/validate-geometry.ts`

Composable validation module for geometry slot matching. Authoritative source for `UNKNOWN_GEOMETRY`, `MISSING_REQUIRED_SLOT`, `UNKNOWN_SLOT` error codes.

- `validateGeometrySlots(manifest, resolveGeometry, listGeometryNames)` → ManifestError[]
- Uses `ValidatableGeometry` interface (satisfied by both OBJ-004's `GeometryRegistration` and OBJ-005's `SceneGeometry`)
- Dependency-injected via `GeometryResolver` / `GeometryNameLister` function types

> **Integration Boundary → spatial:** `ValidatableGeometry` is structurally compatible with OBJ-005's `SceneGeometry`, enabling either registry to be used.

---

## 5. Tier 2 — Protocol, Capture & Encoding

### 5.1 OBJ-011 — Puppeteer-to-Page Message Protocol

**Files:** `src/engine/protocol-types.ts`, `src/engine/page-protocol.ts`, page-side extensions to `src/page/scene-renderer.js`

The complete Node.js/browser message protocol. Provides typed commands over `PuppeteerBridge.evaluate()`.

**Protocol Types** (`protocol-types.ts`):
- `RequiredCameraState` — fully-specified camera state (all fields required, distinct from OBJ-010's optional `FrameCameraState`)
- `SceneSetupConfig` / `SlotSetup` — scene materialization data
- `SceneSetupResult` / `SlotLoadResult` — per-slot texture loading outcomes
- `RenderFrameCommand` / `RenderPass` — multi-pass compositing for transitions

**PageProtocol** class (`page-protocol.ts`):
- `initialize(config)` — calls `window.depthkit.init()`
- `setupScene(config)` → `SceneSetupResult` — creates THREE.Group with textured meshes
- `teardownScene(sceneId)` — removes and disposes
- `renderFrame(command)` — multi-pass compositing with autoClear toggling
- `dispose()` — full page cleanup
- `getRendererInfo()` → `RendererInfo`

**Multi-pass compositing model:**
- Normal frames: single pass, opacity 1.0
- Crossfade: pass 1 (outgoing, opacity 1.0) + pass 2 (incoming, opacity p) with `autoClear=false`
- Dip-to-black: single scene with fading opacity
- Opacity applied via `material.opacity` on all meshes in the scene group

**Acceptance Criteria:** AC-01 through AC-27 (OBJ-011 spec).

> **Integration Boundary → spatial:** `SlotSetup` contains spatial data (position, rotation, size) from geometry definitions (OBJ-005). The orchestrator resolves geometry + manifest overrides into `SlotSetup` before sending to the page.

---

### 5.2 OBJ-015 — Texture Loader and Format Handling

**Files:** `src/page/texture-loader.js`, `src/engine/texture-types.ts`, `src/engine/texture-warnings.ts`

Browser-side texture loading with alpha detection. Extends `window.depthkit`:
- `loadTexture(id, url, options?)` → `TextureMetadata`
- `loadTextures(entries)` → `TextureMetadata[]` (parallel)
- `getTexture(id)` / `getTextureMetadata(id)` / `getAllTextureMetadata()` / `getTextureCount()`
- `unloadTexture(id)` / `unloadAllTextures()`

**Alpha detection:** Canvas pixel sampling — any sampled pixel with alpha < 250 → `hasAlpha: true`. CORS fallback: `hasAlpha: false` with console warning.

**Node-side types:** `TextureMetadata`, `TextureLoadOptions` (in `texture-types.ts`); `checkTextureWarnings()` (in `texture-warnings.ts`)

**Acceptance Criteria:** Per OBJ-015 spec.

---

### 5.3 OBJ-039 — Three.js Page-Side Geometry Instantiation

**Files:** `src/page/geometry-library.js`

Fulfills OBJ-010's geometry-library stub. Converts `SlotSetup` definitions into Three.js meshes:
- `materializeScene(sceneId, slots)` → `SceneMaterializationResult`
- `disposeScene(group)` — full disposal of meshes, materials, textures
- `resolveTextureUrl(textureSrc)` — path-to-URL conversion (POSIX paths → `file://`)

**Key Behaviors:**
- Textures loaded via `THREE.TextureLoader.loadAsync()` (parallel per scene)
- Validates texture dimensions against `gl.MAX_TEXTURE_SIZE`
- Fallback: magenta material (0xff00ff) on texture failure
- Group starts with `visible=false` until render pass activates it

> **INCONSISTENCY FLAG (I-1):** OBJ-015 predicted OBJ-039 would use its texture cache API (`window.depthkit.loadTexture()`), but OBJ-039 uses direct `THREE.TextureLoader` instead (documented in OBJ-039 D2). The two modules have parallel texture loading paths — OBJ-039 does not consume OBJ-015's cache. This is intentional per OBJ-039 D2 but creates duplicate texture loading logic.

---

### 5.4 OBJ-012 — Frame Capture Pipeline

**Files:** `src/engine/frame-capture.ts`

Configurable frame extraction between rendering and encoding.

**Two strategies:**
| Strategy | Captures HUD | Needs preserveDrawingBuffer | Transfer | Default |
|---|---|---|---|---|
| `viewport-png` | Yes | No | CDP `Page.captureScreenshot` | Yes |
| `canvas-png` | No | Yes | `canvas.toDataURL()` | No |

- `capture()` → `CaptureResult` (PNG Buffer + metadata + timing)
- `getStats()` → `CaptureStats` (count, avg/min/max timing)
- CDPSession: lazy creation with staleness detection on bridge re-launch
- Buffer validation: PNG magic bytes check

**Error codes:** `BRIDGE_NOT_LAUNCHED`, `CANVAS_NOT_FOUND`, `WEBGL_CONTEXT_LOST`, `CAPTURE_FAILED`, `INVALID_BUFFER`

**Acceptance Criteria:** AC-01 through AC-21 (OBJ-012 spec).

---

### 5.5 OBJ-013 — FFmpeg Encoder

**Files:** `src/engine/ffmpeg-encoder.ts`

H.264 encoding via stdin piping. Video-only MP4 (audio is OBJ-014).

- `start()` → spawns FFmpeg child process
- `writeFrame(buffer)` → pipes PNG/RGBA frame data with backpressure handling
- `finalize()` → closes stdin, awaits exit → `FFmpegEncoderResult`
- `abort()` → SIGKILL

**Key Config:** `outputPath`, `width`, `height`, `fps`, `frameFormat` ('png'|'rgba'), `preset`, `crf`, `pixelFormat` ('yuv420p'), `deterministic`

**FFmpeg path resolution:** explicit path → `FFMPEG_PATH` env → ffmpeg-static → system `ffmpeg`

**Acceptance Criteria:** Per OBJ-013 spec.

---

### 5.6 OBJ-014 — Audio Muxer

**Files:** `src/engine/audio-muxer.ts`

Post-encoding remux of video-only MP4 + audio file → final MP4.

**Duration strategies:**
- `match_shortest` — FFmpeg `-shortest`
- `match_audio` (default) — freeze last frame via tpad if video shorter; `-t` if longer
- `match_video` — silence if audio shorter; `-t` if longer
- `error` — reject if mismatch > toleranceMs

**Additional exports:**
- `probeMedia(path)` → `MediaProbeResult` (via ffprobe)
- `resolveFFprobePath()` — ffprobe binary resolution
- `DURATION_EQUAL_THRESHOLD_MS = 50` — within this, no adjustment applied

**Acceptance Criteria:** Per OBJ-014 spec.

---

## 6. Tier 3 — Sequencing & Timing

### 6.1 OBJ-036 — Scene Sequencer

**Files:** `src/scenes/scene-sequencer.ts`

Converts manifest scene timing into per-frame rendering plans.

**Key API:**
- `new SceneSequencer(config: SequencerConfig)` — builds internal timeline
- `planFrame(frame)` → `FramePlan` (passes, requiredSceneIds, isGap)
- `planAll()` → `FramePlan[]` (all frames)
- Diagnostic: `timeline` (TimelineEntry[]), `boundaries` (ResolvedBoundary[]), `warnings`

**FramePlan structure:**
- `passes: RenderPassPlan[]` — each with `sceneId`, `normalizedTime`, `opacity`
- Empty passes = gap frame (render black)
- Single pass = normal frame or fade
- Two passes = crossfade (outgoing first)

**Boundary resolution policy:**
- Scene A's `transition_out` + Scene B's `transition_in` resolved at boundary
- Crossfade requires actual scene time overlap
- Independent fades (dip_to_black out + dip_to_black in) each apply independently

**Warning codes:** `CROSSFADE_NO_OVERLAP`, `CROSSFADE_FIRST_SCENE`, `CROSSFADE_LAST_SCENE`, `TRANSITION_CONFLICT`, `TRANSITION_EXCEEDS_SCENE`, etc.

> **INCONSISTENCY FLAG (I-3):** OBJ-036 uses its own independent fade algorithm for dip_to_black opacity computation instead of consuming OBJ-008's transition system (documented in OBJ-036 D4). The scene sequencer's fade math is self-contained — it does not import from `src/transitions/`.

**Acceptance Criteria:** Per OBJ-036 spec.

---

### 6.2 OBJ-038 — Audio Sync and Scene Timing

**Files:** `src/engine/scene-timing.ts`

Bridge between declarative manifest timing and concrete frame-level rendering.

**Timing Modes** (seed Section 8.7):
- `explicit` — manifest values as-is
- `audio_proportional` — durations scaled to audio length (weights)
- `audio_cue` — start_times as narration cue timestamps

**Key API:**
- `resolveTimeline(manifest, audioInfo?, config?)` → `ResolvedTimeline`
- `resolveFrameState(timeline, frame)` → `FrameState` (active scenes + opacity + normalizedTime)

**ResolvedTimeline contains:**
- `clock: FrameClock` — constructed from resolved total duration
- `scenes: ResolvedScene[]` — with frame ranges, transitions
- `warnings: TimingWarning[]`

> **INCONSISTENCY FLAG (I-4):** OBJ-038's `resolveFrameState()` overlaps conceptually with OBJ-036's `planFrame()` — both compute per-frame active scenes with opacity and normalizedTime. The orchestrator (OBJ-035) must choose which to use. OBJ-035's spec references OBJ-036's `planFrame()` as the primary per-frame lookup, with OBJ-038 handling only timeline resolution. The overlap suggests OBJ-038's `resolveFrameState()` may be vestigial or serve as a simpler alternative for non-transition cases.

---

## 7. Tier 4 — Configuration & Error Handling

### 7.1 OBJ-049 — Software Rendering Configuration

**Files:** `src/engine/rendering-config.ts`

Resolves Chromium launch args for software/hardware WebGL. Supplements OBJ-009's built-in flags.

**GPU Modes:**
- `software` → `bridgeGpu: false` + `--use-gl=swiftshader`, `--disable-gpu-compositing`
- `hardware` → `bridgeGpu: true` + `--enable-gpu-rasterization`, `--ignore-gpu-blocklist`
- `auto` → launch with hardware flags, probe result, continue regardless

**Key API:**
- `resolveRenderingConfig(mode)` → `ResolvedRenderingConfig` (pure, no I/O)
- `probeWebGLRenderer(bridge)` → `WebGLRendererInfo` (post-launch probe via temp canvas)
- `validateWebGLCapabilities(info, width, height)` — viewport size check

**Exported constants:** `EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, `EXTRA_HARDWARE_ARGS`

**Acceptance Criteria:** Per OBJ-049 spec.

---

### 7.2 OBJ-048 — Error Handling and Reporting Strategy

**Files:** `src/engine/errors.ts`

Unified error taxonomy and structured reporting. Does NOT define new error classes — those are defined by originating modules. Provides:

- `classifyError(code)` → `ErrorCategory` (validation|asset|browser|render|encode|audio|cancelled|internal)
- `createErrorReport(error)` → `ErrorReport` (structured, JSON-serializable)
- `createValidationErrorReport(errors)` — for standalone validation
- `createUnexpectedErrorReport(error)` — catch-all
- `generateSuggestions(error)` → actionable remediation strings
- `extractFFmpegLogTail(log, maxLines?)` — last N lines of FFmpeg stderr
- `DEGRADATION_RULES` — testable graceful degradation policy

**ErrorReport structure:** `success`, `category`, `code`, `message`, `validationErrors`, `frame`, `detail`, `suggestions`

**Acceptance Criteria:** Per OBJ-048 spec.

---

## 8. Tier 5 — Orchestration

### 8.1 OBJ-035 — Orchestrator: Main Render Loop

**Files:** `src/engine/orchestrator.ts`

Top-level integration point. Composes all engine modules into the deterministic render loop.

**Key API:**
- `new Orchestrator(config: OrchestratorConfig)`
- `render()` → `Promise<OrchestratorResult>`
- `onProgress` callback with cancellation support

**OrchestratorConfig requires three registries:**
1. `registry: ManifestRegistry` — for validation (OBJ-004 types)
2. `geometryRegistry: GeometryRegistry` — for spatial data (OBJ-005 types)
3. `cameraRegistry: CameraPathRegistry` — for camera evaluation (OBJ-006 types)

**Render Loop (seed Section 4.4):**
1. Validate manifest via `loadManifest()` (C-10)
2. Resolve timeline via OBJ-038
3. Launch PuppeteerBridge with OBJ-049 rendering config
4. Initialize page via PageProtocol
5. Create FFmpegEncoder
6. For each frame (FrameClock iterator):
   a. `planFrame()` via SceneSequencer (OBJ-036)
   b. Setup/teardown scenes as needed via PageProtocol
   c. Compute camera state from camera registry
   d. `renderFrame()` via PageProtocol (multi-pass for transitions)
   e. `capture()` via FrameCapture
   f. `writeFrame()` to FFmpegEncoder
   g. Invoke `onProgress` callback
7. `finalize()` FFmpegEncoder
8. Audio mux if audio present (OBJ-014)
9. Cleanup: dispose page, close browser

**OrchestratorResult:** `outputPath`, `totalFrames`, `renderDurationMs`, `totalDurationMs`, `captureStats`, `encoderResult`, `rendererInfo`, `audioResult`

**OrchestratorError codes:** `MANIFEST_INVALID`, `BROWSER_LAUNCH_FAILED`, `PAGE_INIT_FAILED`, `SCENE_SETUP_FAILED`, `RENDER_FAILED`, `CAPTURE_FAILED`, `ENCODE_FAILED`, `AUDIO_MUX_FAILED`, `CANCELLED`, `GEOMETRY_NOT_FOUND`, `CAMERA_NOT_FOUND`

**Acceptance Criteria:** Per OBJ-035 spec.

> **Integration Boundary → spatial:** The orchestrator consumes `GeometryRegistry` (OBJ-005) for slot spatial data and `CameraPathRegistry` (OBJ-006) for camera path evaluation. These registries are the primary integration point with the spatial category.

> **Integration Boundary → tuning:** OBJ-058's test-render utility wraps the Orchestrator with quality presets (draft/review/proof) and scene isolation for Director Agent workflows.

---

## 9. Tier 6 — External Interfaces

### 9.1 OBJ-046 — CLI Interface

**Files:** `src/cli.ts`, `src/cli/format.ts`, `src/cli/colors.ts`, `src/cli/registry-init.ts`

Commander-based CLI with three commands:

| Command | Description | Exit Codes |
|---------|-------------|------------|
| `depthkit render <manifest>` | Full render to MP4 | 0=success, 1=error |
| `depthkit validate <manifest>` | Validate without rendering | 0=valid, 1=invalid |
| `depthkit preview <manifest>` | Local HTTP preview (stub) | 0 |

**Render options:** `--output`, `--width`, `--height`, `--fps`, `--assets-dir`, `--gpu`, `--preset`, `--crf`, `--ffmpeg-path`, `--chromium-path`

**Global options:** `--verbose`, `--debug`, `--color`/`--no-color`

**Registry initialization:** `initRegistries()` in `src/cli/registry-init.ts` populates all three registries (manifest, geometry, camera) synchronously via static imports.

**Acceptance Criteria:** Per OBJ-046 spec.

> **INCONSISTENCY FLAG (I-2):** OBJ-004's `CameraParamsSchema` does not include an `offset` field, but OBJ-006's `CameraParams` type includes `offset?: [number, number, number]`. Noted in OBJ-046 OQ-F. The manifest schema does not validate or pass through `offset` — this field is camera-preset internal only.

---

### 9.2 OBJ-047 — Library API

**Files:** `src/index.ts`, `src/api.ts`, `src/registry.ts`

Programmatic entry point for Node.js consumers (n8n, custom scripts).

**Key API:**
- `render(options: RenderOptions)` → `Promise<RenderResult>` — from manifest object
- `renderFile(manifestPath, options?)` → `Promise<RenderResult>` — from file
- `initRegistries()` → `RegistryBundle` — shared with CLI

**RenderOptions:** manifest, outputPath, overrides (width/height/fps), assetsDir, captureStrategy, encodingPreset, crf, gpu, hooks

**RenderHooks:** `onFrameRendered`, `onSceneStart`, `onSceneEnd`, `onComplete`, `onError` — richer than Orchestrator's single `onProgress`

**Registry relocation:** `initRegistries()` moved from `src/cli/registry-init.ts` to shared `src/registry.ts`. CLI re-exports from there.

**Acceptance Criteria:** Per OBJ-047 spec.

---

### 9.3 OBJ-058 — Director Agent Workflow

**Files:** `src/tools/test-render.ts`

Test-render utility wrapping OBJ-035's Orchestrator for Director Agent visual tuning.

**Quality presets:**
- `draft`: 640x360, crf 28, 24fps
- `review`: 1280x720, crf 23, 30fps
- `proof`: 1920x1080, crf 20, 30fps

**Features:** `maxDuration` (default 30s), `isolateScene`, keyframe thumbnail extraction

> **Integration Boundary → tuning:** This module directly supports OBJ-059–OBJ-066 (geometry tuning) and OBJ-068 (transition tuning) from the tuning category.

---

## 10. Cross-Cutting: Spatial Integration

### 10.1 OBJ-040 — Plane Sizing and Edge-Reveal Prevention

**Files:** `src/spatial/plane-sizing.ts`

Pure spatial math module for texture-to-plane sizing.

**Sizing modes:**
- `contain` — texture fits within slot bounds (may letterbox)
- `cover` — texture covers slot bounds (may overflow)
- `stretch` — exact slot size (may distort)

**Additional capabilities:**
- Camera-motion-dependent oversizing computation
- Edge-reveal validation (sampling-based)
- `suggestSizeMode(slotRole)` — recommend mode based on slot semantic role

> **Integration Boundary → spatial:** Extends OBJ-003's spatial library. Consumes geometry (OBJ-005) and camera path metadata (OBJ-006).

---

### 10.2 OBJ-041 — Geometry-Camera Spatial Compatibility Validation

**Files:** `src/validation/spatial-compatibility.ts`

Cross-references geometry and camera registries for spatial correctness.

**Three validation categories:**
1. **Compatibility:** camera path declared compatible with geometry (bidirectional)
2. **Registry consistency:** all cross-references resolve
3. **Oversizing sufficiency:** planes large enough for camera motion envelope

**Key API:**
- `validateSceneSpatialCompatibility(sceneId, geometryName, cameraName, ...)` — per-scene
- `validateRegistryConsistency(geometryRegistry, cameraRegistry)` — boot-time check
- `analyzeDesignSpaceCoverage(geometryRegistry, cameraRegistry)` — TC-08

> **Integration Boundary → spatial:** Primary consumer of OBJ-005's `SceneGeometry` and OBJ-006's `CameraPathPreset` types. Results consumed by OBJ-017 as additive validation.

---

## 11. Integration Boundary Map

### Engine → Spatial Category

| Engine Module | Spatial Module | Integration Type |
|---|---|---|
| OBJ-002 (interpolation) | OBJ-006 (camera presets), OBJ-008 (transitions) | Math primitives consumed |
| OBJ-004 (manifest schema) | OBJ-005 (geometry base), OBJ-006 (camera presets) | Registry population |
| OBJ-010 (page shell) | OBJ-003 (spatial math) | `DEFAULT_CAMERA` values, `Vec3` type |
| OBJ-011 (protocol) | OBJ-005 (geometry types) | `SlotSetup` spatial data |
| OBJ-017 (validation) | OBJ-005 (geometry) | `ValidatableGeometry` interface |
| OBJ-035 (orchestrator) | OBJ-005 (GeometryRegistry), OBJ-006 (CameraPathRegistry) | Full spatial data for rendering |
| OBJ-040 (plane sizing) | OBJ-003, OBJ-005, OBJ-006 | Spatial math extension |
| OBJ-041 (compatibility) | OBJ-005, OBJ-006 | Cross-registry validation |

### Engine → Tuning Category

| Engine Module | Tuning Module | Integration Type |
|---|---|---|
| OBJ-058 (test-render) | OBJ-059–066 (geometry tuning), OBJ-068 (transition tuning) | Test render utility |
| OBJ-035 (orchestrator) | All tuning objectives | Wrapped by test-render |

### Engine → Integration Category

| Engine Module | Integration Module | Integration Type |
|---|---|---|
| OBJ-047 (library API) | OBJ-055 (n8n endpoint) | Programmatic render interface |
| OBJ-048 (error handling) | OBJ-055 (n8n endpoint) | Structured error reports |

---

## 12. Inconsistencies & Open Conflicts

### I-1: Duplicate Texture Loading Paths (OBJ-015 vs OBJ-039)

**Severity:** Medium — Functional but wasteful.

OBJ-015 defines a full texture loading/caching API on `window.depthkit` (`loadTexture()`, `getTexture()`, `unloadTexture()`). OBJ-039 ignores this cache and uses `THREE.TextureLoader.loadAsync()` directly in `materializeScene()`. This is documented in OBJ-039 D2 as intentional but means:
- Two independent texture loading code paths exist on the page
- OBJ-015's cache is unused by the production rendering path
- Alpha detection from OBJ-015 must be separately handled

**Resolution:** OBJ-039 owns the production texture loading path. OBJ-015's cache API may be useful for preview mode or standalone testing but is not in the hot path.

### I-2: CameraParams `offset` Field Missing from Schema (OBJ-004 vs OBJ-006)

**Severity:** Low — Informational only.

OBJ-004's `CameraParamsSchema` has: `speed`, `easing`, `fov_start`, `fov_end`. OBJ-006's `CameraParams` type additionally defines `offset?: [number, number, number]`. The manifest cannot currently express camera offset overrides. Noted in OBJ-046 OQ-F.

**Resolution:** If offset support is needed in manifests, `CameraParamsSchema` must be extended. Currently camera offset is preset-internal only.

### I-3: Independent Fade Algorithm in Scene Sequencer (OBJ-036 vs OBJ-008)

**Severity:** Low — Intentional separation.

OBJ-036 computes dip_to_black opacity using its own linear fade math rather than importing from OBJ-008's transition system. Documented in OBJ-036 D4.

**Resolution:** Acceptable for V1. OBJ-008 defines transition types; OBJ-036 implements the frame-level opacity computation independently. If transition easing is added to dip_to_black, both must be updated.

### I-4: Overlapping Frame-State Functions (OBJ-038 vs OBJ-036)

**Severity:** Medium — Potential confusion during implementation.

OBJ-038's `resolveFrameState()` and OBJ-036's `planFrame()` both compute per-frame active scenes with opacity and normalizedTime. OBJ-035's spec uses OBJ-036's `planFrame()` as the primary per-frame lookup.

**Resolution:** OBJ-038 handles timeline resolution (mode selection, duration scaling, frame range computation). OBJ-036 handles per-frame rendering plans. The orchestrator should use OBJ-038 for initial timeline setup, then OBJ-036 for per-frame planning. `resolveFrameState()` may be a convenience for simpler use cases or testing.

### I-5: Transition Renderer Spec Gap (OBJ-037)

**Severity:** Low — Only a one-line description exists.

OBJ-037 (Transition Renderer) has no full verified spec. Transition rendering is effectively specified across OBJ-011 (multi-pass compositing model), OBJ-036 (opacity computation), and OBJ-035 (orchestration loop).

**Resolution:** The transition rendering behavior is fully covered by the combination of OBJ-011 + OBJ-036. OBJ-037 may be vestigial.

---

## 13. Consolidated File Manifest

### Source Files

```
src/
├── interpolation/
│   ├── easings.ts              [OBJ-002]  Easing functions + registry
│   ├── interpolate.ts          [OBJ-002]  Range interpolation
│   ├── spring.ts               [OBJ-002]  Spring physics
│   └── index.ts                [OBJ-002]  Barrel export
├── manifest/
│   ├── schema.ts               [OBJ-004]  Zod schemas, types, registry interfaces
│   ├── loader.ts               [OBJ-016]  Two-phase validation pipeline
│   └── validate-geometry.ts    [OBJ-017]  Geometry slot validation
├── engine/
│   ├── frame-clock.ts          [OBJ-009]  Deterministic frame-timestamp mapping
│   ├── puppeteer-bridge.ts     [OBJ-009]  Chromium lifecycle manager
│   ├── page-types.ts           [OBJ-010]  Node-side boundary types
│   ├── protocol-types.ts       [OBJ-011]  Protocol data structures
│   ├── page-protocol.ts        [OBJ-011]  Typed command interface
│   ├── frame-capture.ts        [OBJ-012]  CDP/canvas frame capture
│   ├── ffmpeg-encoder.ts       [OBJ-013]  H.264 encoding via FFmpeg
│   ├── audio-muxer.ts          [OBJ-014]  Audio+video muxing
│   ├── texture-types.ts        [OBJ-015]  Texture metadata types
│   ├── texture-warnings.ts     [OBJ-015]  Texture warning checks
│   ├── scene-timing.ts         [OBJ-038]  Audio sync + timing resolution
│   ├── rendering-config.ts     [OBJ-049]  Software/hardware WebGL config
│   ├── errors.ts               [OBJ-048]  Error classification + reporting
│   └── orchestrator.ts         [OBJ-035]  Main render loop
├── scenes/
│   └── scene-sequencer.ts      [OBJ-036]  Per-frame rendering plans
├── spatial/
│   └── plane-sizing.ts         [OBJ-040]  Texture-to-plane sizing math
├── validation/
│   └── spatial-compatibility.ts [OBJ-041] Geometry-camera compatibility
├── page/
│   ├── index.html              [OBJ-010]  HTML shell
│   ├── scene-renderer.js       [OBJ-010+011+015] Three.js init + protocol handlers
│   ├── geometry-library.js     [OBJ-039]  Mesh creation from SlotSetup
│   ├── texture-loader.js       [OBJ-015]  Browser-side texture loading
│   └── message-handler.js      [OBJ-011]  Protocol message dispatch
├── tools/
│   └── test-render.ts          [OBJ-058]  Director Agent test render utility
├── cli.ts                      [OBJ-046]  CLI entry point
├── cli/
│   ├── format.ts               [OBJ-046]  Output formatting
│   ├── colors.ts               [OBJ-046]  ANSI color utilities
│   └── registry-init.ts        [OBJ-046→047] Registry init (re-exports from registry.ts)
├── registry.ts                 [OBJ-047]  Shared registry initialization
├── index.ts                    [OBJ-047]  Library API entry point
└── api.ts                      [OBJ-047]  render() / renderFile() implementation
```

---

## 14. Consolidated Acceptance Criteria Index

Total ACs across all engine-category specs:

| OBJ | Module | AC Count | Critical ACs |
|-----|--------|----------|-------------|
| 002 | Interpolation | 26 | AC-01 (easing boundaries), AC-20 (determinism) |
| 004 | Manifest Schema | 34 | AC-01 (parse valid), AC-17–21 (semantic validation) |
| 009 | Clock + Bridge | 32 | AC-01 (frame-to-time), AC-17 (viewport match) |
| 010 | Page Shell | 20 | AC-03 (init), AC-08 (preserveDrawingBuffer), AC-18 (renderFrame) |
| 011 | Protocol | 27 | AC-01 (init), AC-10 (setupScene), AC-16 (multi-pass) |
| 012 | Frame Capture | 21 | AC-04 (viewport-png), AC-06 (determinism), AC-20 (FFmpeg compat) |
| 013 | FFmpeg Encoder | ~20 | start/writeFrame/finalize lifecycle, backpressure, determinism |
| 014 | Audio Muxer | ~18 | Duration strategies, stream copy/encode decisions |
| 015 | Texture Loader | ~15 | Alpha detection, cache semantics, format tolerance |
| 016 | Manifest Loader | 31 | AC-01 (all errors collected), AC-12 (skip-on-unknown) |
| 017 | Geometry Validation | ~10 | Authoritative error codes, slot matching |
| 035 | Orchestrator | ~25 | Full render lifecycle, cancellation, error propagation |
| 036 | Scene Sequencer | ~20 | planFrame correctness, boundary resolution, transition opacity |
| 038 | Scene Timing | ~15 | Three timing modes, frame range computation |
| 046 | CLI | ~15 | Command parsing, exit codes, progress display |
| 047 | Library API | ~12 | render/renderFile, hooks, registry sharing |
| 048 | Error Handling | ~15 | Classification, suggestion generation, degradation rules |
| 049 | Rendering Config | ~12 | Mode resolution, probe, validation |
| 040 | Plane Sizing | ~12 | contain/cover/stretch math, edge-reveal |
| 041 | Spatial Compat | ~10 | Bidirectional validation, coverage analysis |
| 058 | Director Tools | ~8 | Quality presets, scene isolation |

**Total estimated ACs: ~400+**

Each module's full AC list is preserved in its respective OBJ-NNN output.md file in the `nodes/` directory. All ACs must pass before the module is considered implementation-complete.

---

*End of consolidated engine specification.*
