# depthkit — Final Consolidated Specification

> **Version:** 3.0 | **Generated:** 2026-03-23 | **Mode:** ROLLUP
> **Source Documents:** `synthesis/engine_spec.md`, `synthesis/spatial_spec.md`, `synthesis/integration_spec.md`, Seed Document v3.0
> **Total Verified Objectives:** 55 | **Unspecified Objectives:** ~28 | **Estimated Acceptance Criteria:** 580+

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Deliverable Map](#2-deliverable-map)
3. [Critical Path](#3-critical-path)
4. [Cross-Category Architecture](#4-cross-category-architecture)
5. [Deliverable 1: Rendering Engine](#5-deliverable-1-rendering-engine)
6. [Deliverable 2: Spatial Authoring Vocabulary](#6-deliverable-2-spatial-authoring-vocabulary)
7. [Deliverable 3: SKILL.md](#7-deliverable-3-skillmd)
8. [Deliverable 4: n8n-Compatible HTTP Interface](#8-deliverable-4-n8n-compatible-http-interface)
9. [Cross-Category Integration Points](#9-cross-category-integration-points)
10. [Consolidated File Manifest](#10-consolidated-file-manifest)
11. [Implementation Order](#11-implementation-order)
12. [Consolidated Inconsistencies](#12-consolidated-inconsistencies)
13. [Consolidated Open Questions](#13-consolidated-open-questions)
14. [Verification and Success Criteria Traceability](#14-verification-and-success-criteria-traceability)
15. [Constraint Compliance Map](#15-constraint-compliance-map)

---

## 1. Executive Summary

**depthkit** is a zero-license Node.js video engine that renders 2.5D camera-projection video from declarative JSON manifests. It maps AI-generated 2D images onto flat mesh planes in a Three.js 3D scene, moves a perspective camera through that scene, and captures deterministic frame-by-frame output through Puppeteer into FFmpeg for H.264 MP4 encoding.

The engine is designed to be **authored by an LLM that cannot see its output**. Every spatial decision is expressed as a selection from a finite vocabulary of validated presets (scene geometries, camera paths, transitions, easing curves) or as parameterized values within mathematically proven safe ranges.

### Technology Stack

| Layer | Technology | License | Role |
|-------|-----------|---------|------|
| 3D Rendering | Three.js | MIT | WebGL scene graph, perspective projection |
| Browser Control | Puppeteer | Apache-2.0 | Headless Chromium, deterministic frame capture |
| Video Encoding | FFmpeg (via stdio) | LGPL/GPL | H.264 encoding, audio muxing |
| Validation | Zod | MIT | Manifest schema validation |
| CLI | Commander | MIT | Command-line interface |

### Scale Summary

- **Verified node specifications:** 55 objectives with full specs and acceptance criteria
- **Unspecified nodes:** ~28 objectives with descriptions only (portal, panorama, dramatic_push, crane_up, dolly_zoom, Docker, n8n endpoint, manifest generation, asset orchestration, cache middleware, background removal, etc.)
- **Scene geometries specified:** 6 of 8 (stage, tunnel, canyon, flyover, diorama, close_up)
- **Camera presets specified:** 6 of 9 (static, slow_push_forward, slow_pull_back, lateral_track_left/right, tunnel_push_forward, flyover_glide, gentle_float)
- **Total acceptance criteria:** ~580+ across all verified specs

---

## 2. Deliverable Map

The seed document (Section 1) defines four deliverables. This section maps each to the objectives and category specs that fulfill it.

### Deliverable 1: depthkit Rendering Engine

The custom Node.js application: Three.js scene renderer, Puppeteer frame capture, FFmpeg encoder, CLI, and library API.

**Primary category:** engine
**Supporting category:** spatial (consumed as registries)
**Objectives:** OBJ-002, OBJ-004, OBJ-009, OBJ-010, OBJ-011, OBJ-012, OBJ-013, OBJ-014, OBJ-015, OBJ-016, OBJ-017, OBJ-035, OBJ-036, OBJ-038, OBJ-039, OBJ-040, OBJ-041, OBJ-046, OBJ-047, OBJ-048, OBJ-049, OBJ-058
**Success criteria:** SC-01, SC-03, SC-06

### Deliverable 2: Spatial Authoring Vocabulary

The library of scene geometries, depth models, camera paths, transitions, and composition rules.

**Primary category:** spatial
**Objectives:** OBJ-003, OBJ-005, OBJ-006, OBJ-007, OBJ-008, OBJ-018–025, OBJ-026–034, OBJ-040, OBJ-041
**Tuning objectives:** OBJ-059–066 (geometry tuning), OBJ-067 (visual gate), OBJ-068 (transition tuning)
**Success criteria:** SC-02, SC-07

### Deliverable 3: SKILL.md

The documentation system that enables blind LLM authoring.

**Primary category:** integration
**Objectives:** OBJ-070, OBJ-071, OBJ-072
**Success criteria:** SC-02, SC-04

### Deliverable 4: n8n-Compatible HTTP Interface

The production pipeline wrapper: topic in, MP4 out.

**Primary category:** integration
**Objectives:** OBJ-051, OBJ-052, OBJ-053, OBJ-054, OBJ-055, OBJ-056, OBJ-057
**Success criteria:** SC-05

---

## 3. Critical Path

The critical path traces the longest dependency chain from foundational primitives to the capstone validation gate (OBJ-078).

```
PHASE 1: Foundations (parallel tracks)
═══════════════════════════════════════

Track A: Engine Primitives               Track B: Spatial Primitives
─────────────────────────                ─────────────────────────
OBJ-002 Interpolation/Easing             OBJ-003 Spatial Math
         │                                        │
OBJ-004 Manifest Schema              ┌───────────┼───────────┐
         │                            │           │           │
OBJ-009 FrameClock + Bridge      OBJ-005 Geometry  OBJ-006 Camera  OBJ-007 Depth Model
OBJ-010 Page Shell               OBJ-008 Transitions    │           │
         │                            │           │      │           │
         ▼                            ▼           ▼      ▼           ▼

PHASE 2: Components (parallel tracks)
═══════════════════════════════════════

Track A: Engine Core                     Track B: Spatial Content
─────────────────────                    ─────────────────────
OBJ-016 Manifest Loader                 OBJ-018 Stage
OBJ-017 Geometry Validation             OBJ-019 Tunnel
OBJ-011 Page Protocol                   OBJ-020 Canyon
OBJ-015 Texture Loader                  OBJ-021 Flyover
OBJ-039 Geometry Instantiation          OBJ-022 Diorama
OBJ-012 Frame Capture                   OBJ-025 Close-up
OBJ-013 FFmpeg Encoder                  OBJ-026 Static camera
OBJ-014 Audio Muxer                     OBJ-027 Push/Pull cameras
OBJ-036 Scene Sequencer                 OBJ-028 Lateral Track cameras
OBJ-038 Scene Timing                    OBJ-029 Tunnel Push camera
OBJ-048 Error Handling                  OBJ-030 Flyover Glide camera
OBJ-049 Rendering Config                OBJ-031 Gentle Float camera
         │                              OBJ-040 Plane Sizing
         │                              OBJ-041 Spatial Compatibility
         │                                       │
         └───────────┬───────────────────────────┘
                     │
                     ▼

PHASE 3: Orchestration
══════════════════════
OBJ-035 Orchestrator (composes ALL engine + spatial modules)
         │
    ┌────┼──────────────┐
    │    │              │
    ▼    ▼              ▼

PHASE 4: Interfaces + Tuning + Integration (parallel)
═════════════════════════════════════════════════════

Track A: CLI/API    Track B: Tuning          Track C: SKILL.md + Pipeline
───────────────     ──────────────           ──────────────────────────
OBJ-046 CLI         OBJ-058 Director Tools   OBJ-051 Prompt Engineering
OBJ-047 Library API OBJ-059-066 Geo Tuning   OBJ-053 Cache Schema
                    OBJ-068 Transition Tune   OBJ-070 SKILL.md Core
                    OBJ-067 Visual Gate       OBJ-071 SKILL.md Geo/Camera
                                              OBJ-072 SKILL.md Prompts/Patterns
                         │                    OBJ-052 Background Removal
                         │                    OBJ-054 Cache Middleware
                         │                    OBJ-055 n8n Endpoint
                         │                    OBJ-056 Manifest Generation
                         │                    OBJ-057 Asset Orchestration
                         │                             │
                         └──────────┬──────────────────┘
                                    │
                                    ▼

PHASE 5: Verification
═════════════════════
OBJ-073 Determinism Verification
OBJ-074 Performance Benchmark
OBJ-075 Blind Authoring Tests
OBJ-076 Cache Validation
OBJ-077 E2E Test Plan
         │
         ▼
OBJ-078 End-to-End Validation Gate  ← PROJECT COMPLETE WHEN THIS PASSES
```

**Longest path:** OBJ-003 → OBJ-005 → OBJ-018 → OBJ-035 → OBJ-058 → OBJ-059 → OBJ-067 → OBJ-077 → OBJ-078

---

## 4. Cross-Category Architecture

### The Dumb Page / Smart Orchestrator Pattern

The engine follows a strict architectural split (OBJ-010 D1):

```
┌─────────────────────────────────────────────────────────────┐
│                      NODE.JS SIDE                            │
│  (Smart Orchestrator — all domain logic)                     │
│                                                              │
│  Manifest validation ──► Scene timing ──► Frame clock        │
│  Geometry registry ──► Slot resolution ──► Camera evaluation │
│  Scene sequencer ──► Frame planning ──► Transition opacity   │
│  Error handling ──► Progress reporting                       │
│                          │                                   │
│                   page.evaluate()                            │
│                          │                                   │
├──────────────────────────┼──────────────────────────────────┤
│                          ▼                                   │
│                   BROWSER SIDE                               │
│  (Dumb Page — data-driven Three.js renderer)                 │
│                                                              │
│  window.depthkit.init(config)                                │
│  window.depthkit.setupScene(slots)                           │
│  window.depthkit.renderFrame(cameraState, passes)            │
│  window.depthkit.dispose()                                   │
│                                                              │
│  Three.js: WebGLRenderer, PerspectiveCamera, Scene,          │
│            PlaneGeometry, MeshBasicMaterial, TextureLoader    │
└─────────────────────────────────────────────────────────────┘
```

### Registry Architecture

Three registries supply domain knowledge to the engine:

| Registry | Source | Pattern | Consumer |
|----------|--------|---------|----------|
| `ManifestRegistry` | OBJ-004 | Interface — populated by OBJ-005/006 registrations | OBJ-016 (validation) |
| `GeometryRegistry` | OBJ-005 | Lock-on-first-read singleton | OBJ-035, OBJ-041, OBJ-017 |
| `CameraPathRegistry` | OBJ-006 | Parameter-passed map | OBJ-035, OBJ-041 |

**Assembly point:** `src/registry.ts` (OBJ-047) — shared by CLI (OBJ-046) and library API (OBJ-047). Calls `initRegistries()` which imports all geometry/camera modules (triggering self-registration) and returns a `RegistryBundle` containing all three registries.

### Data Flow: Manifest to MP4

```
1. JSON manifest string
   │
   ├─ OBJ-004: Zod structural parse → typed Manifest object
   ├─ OBJ-016: Semantic validation against ManifestRegistry
   └─ OBJ-017: Geometry slot validation against GeometryRegistry
   │
2. Validated Manifest
   │
   ├─ OBJ-038: Resolve timeline (explicit/audio_proportional/audio_cue)
   │   └─ Produces: ResolvedTimeline with FrameClock + per-scene frame ranges
   │
   ├─ OBJ-036: Build SceneSequencer from timeline
   │   └─ Produces: planFrame(n) → FramePlan (active scenes, opacity, normalizedTime)
   │
3. Render loop (OBJ-035 Orchestrator)
   │
   ├─ OBJ-009: PuppeteerBridge.launch() → headless Chromium
   ├─ OBJ-049: resolveRenderingConfig(gpuMode) → Chromium flags
   ├─ OBJ-011: PageProtocol.initialize(config) → Three.js renderer ready
   ├─ OBJ-013: FFmpegEncoder.start() → encoding process ready
   │
   For each frame N in FrameClock.frames():
   │
   │  ├─ OBJ-036: planFrame(N) → FramePlan
   │  │   └─ sceneIds, normalizedTime per scene, opacity per pass
   │  │
   │  ├─ OBJ-011: PageProtocol.setupScene(slotSetup) [if new scene]
   │  │   └─ OBJ-005: GeometryRegistry → slot positions/rotations/sizes
   │  │   └─ OBJ-007: resolveSlotTransform(slot, manifest overrides)
   │  │   └─ OBJ-039: materializeScene() → Three.js meshes
   │  │
   │  ├─ OBJ-006: CameraPathPreset.evaluate(t, params) → CameraFrameState
   │  │   └─ OBJ-002: interpolate() + easing functions
   │  │
   │  ├─ OBJ-011: PageProtocol.renderFrame(command) → Three.js render
   │  │   └─ Multi-pass compositing for transitions (OBJ-008 opacity)
   │  │
   │  ├─ OBJ-012: FrameCapture.capture() → PNG buffer
   │  │
   │  └─ OBJ-013: FFmpegEncoder.writeFrame(buffer)
   │
   ├─ OBJ-013: FFmpegEncoder.finalize() → video-only MP4
   └─ OBJ-014: AudioMuxer.mux(video, audio) → final MP4

4. Output: MP4 file
```

---

## 5. Deliverable 1: Rendering Engine

> Full specification: `synthesis/engine_spec.md`

The rendering engine is organized into 7 tiers by dependency depth. This section summarizes each tier and its key integration points.

### Tier 0: Foundational Primitives

| Module | File | Key Exports |
|--------|------|-------------|
| **OBJ-002** Interpolation | `src/interpolation/` | `interpolate()`, `spring()`, 6 named easings, `getEasing()` |
| **OBJ-004** Manifest Schema | `src/manifest/schema.ts` | Zod schemas, `ManifestRegistry` interface, error types |

**OBJ-002** provides pure math primitives (26 ACs). Two-element ranges only, clamp by default, fail-fast on NaN. Consumed by camera presets (OBJ-006) and transitions (OBJ-008) from the spatial category.

**OBJ-004** defines the manifest JSON contract (34 ACs). Two-phase validation: Zod structural + semantic registry checks. Geometry's `compatibleCameras` is authoritative for validation; camera's `compatibleGeometries` is informational. `.strict()` on sub-schemas catches typos.

### Tier 1: Core Infrastructure

| Module | File | Key Exports |
|--------|------|-------------|
| **OBJ-009** FrameClock + PuppeteerBridge | `src/engine/` | `FrameClock`, `PuppeteerBridge` |
| **OBJ-010** Page Shell | `src/page/`, `src/engine/page-types.ts` | `window.depthkit` API, `PageInitConfig` |
| **OBJ-016** Manifest Loader | `src/manifest/loader.ts` | `loadManifest()`, `loadManifestFromFile()` |
| **OBJ-017** Geometry Validation | `src/manifest/validate-geometry.ts` | `validateGeometrySlots()` |

**FrameClock:** Pure deterministic frame-to-timestamp mapping. `frames()` generator is the canonical render loop iterator.

**PuppeteerBridge:** Lifecycle manager. `deviceScaleFactor: 1` enforced. Does NOT call `window.depthkit.init()` — that's the orchestrator's job.

**Page Shell:** Browser-side Three.js foundation. `preserveDrawingBuffer: true` for capture. `antialias: false` for determinism. `MeshBasicMaterial` (unlit) — lighting deferred per OQ-09.

### Tier 2: Protocol, Capture & Encoding

| Module | File | Key Exports |
|--------|------|-------------|
| **OBJ-011** Page Protocol | `src/engine/page-protocol.ts` | `PageProtocol` class: `initialize()`, `setupScene()`, `renderFrame()`, `dispose()` |
| **OBJ-015** Texture Loader | `src/page/texture-loader.js` | `window.depthkit.loadTexture()`, alpha detection |
| **OBJ-039** Geometry Instantiation | `src/page/geometry-library.js` | `materializeScene()`, `disposeScene()` |
| **OBJ-012** Frame Capture | `src/engine/frame-capture.ts` | `capture()` → PNG Buffer, two strategies (viewport-png, canvas-png) |
| **OBJ-013** FFmpeg Encoder | `src/engine/ffmpeg-encoder.ts` | `start()`, `writeFrame()`, `finalize()`, backpressure handling |
| **OBJ-014** Audio Muxer | `src/engine/audio-muxer.ts` | `mux()`, `probeMedia()`, 4 duration strategies |

**Multi-pass compositing model** (OBJ-011): Normal frames = 1 pass. Crossfade = 2 passes (outgoing at opacity 1.0, incoming at opacity p, autoClear=false). Dip-to-black = 1 pass with fading opacity.

**Frame capture** (OBJ-012): Default `viewport-png` via CDP `Page.captureScreenshot` — captures HUD layers. Alternative `canvas-png` via `canvas.toDataURL()`.

**Audio muxing** (OBJ-014): 4 duration strategies — `match_shortest`, `match_audio` (default, freeze last frame if video shorter), `match_video`, `error`.

### Tier 3: Sequencing & Timing

| Module | File | Key Exports |
|--------|------|-------------|
| **OBJ-036** Scene Sequencer | `src/scenes/scene-sequencer.ts` | `planFrame()` → `FramePlan`, transition boundary resolution |
| **OBJ-038** Scene Timing | `src/engine/scene-timing.ts` | `resolveTimeline()` → `ResolvedTimeline`, 3 timing modes |

**OBJ-038** handles timeline resolution: `explicit` (manifest values), `audio_proportional` (scale to audio), `audio_cue` (narration timestamps).

**OBJ-036** converts resolved timeline into per-frame rendering plans. Handles crossfade overlap (two concurrent scenes) and dip_to_black (independent fade). OBJ-035 uses OBJ-038 for initial timeline setup, then OBJ-036 for per-frame planning.

### Tier 4: Configuration & Error Handling

| Module | File | Key Exports |
|--------|------|-------------|
| **OBJ-049** Rendering Config | `src/engine/rendering-config.ts` | `resolveRenderingConfig()`, 3 GPU modes, WebGL probe |
| **OBJ-048** Error Handling | `src/engine/errors.ts` | `classifyError()`, `createErrorReport()`, `generateSuggestions()` |

### Tier 5: Orchestrator

| Module | File | Key Exports |
|--------|------|-------------|
| **OBJ-035** Orchestrator | `src/engine/orchestrator.ts` | `Orchestrator` class: `render()` → `OrchestratorResult` |

The top-level integration point. Requires three registries: `ManifestRegistry`, `GeometryRegistry`, `CameraPathRegistry`. Implements the complete deterministic render loop (seed Section 4.4, C-03).

### Tier 6: External Interfaces

| Module | File | Key Exports |
|--------|------|-------------|
| **OBJ-046** CLI | `src/cli.ts` | `depthkit render`, `depthkit validate`, `depthkit preview` |
| **OBJ-047** Library API | `src/index.ts`, `src/api.ts` | `render()`, `renderFile()`, `initRegistries()` |
| **OBJ-058** Director Tools | `src/tools/test-render.ts` | `renderTestClip()`, quality presets, tuning log schema |

---

## 6. Deliverable 2: Spatial Authoring Vocabulary

> Full specification: `synthesis/spatial_spec.md`

### Foundation Layer

**OBJ-003 — Spatial Math** (`src/spatial/`): Pure Vec3/EulerRotation/Size2D types, frustum computation, view-axis distance projection, plane sizing. All types are `readonly [number, number, number]` tuples — JSON-serializable, no Three.js dependency. FOV in degrees, rotations in radians.

**OBJ-005 — Geometry Type Contract** (`src/scenes/geometries/`): `SceneGeometry` type with `PlaneSlot` definitions. Lock-on-first-read singleton registry. Deep-frozen after first read. 11-check validation.

**OBJ-006 — Camera Path Type Contract** (`src/camera/`): `CameraPathPreset` with `evaluate(t, params?) => CameraFrameState`. Parameter-passed registry (not singleton). Speed scales spatial amplitude (not temporal rate). Offset applied post-evaluate by renderer. 11-check validation at 100 sample points.

**OBJ-007 — Depth Model** (`src/spatial/depth-model.ts`): `DepthSlot` type, `DEFAULT_SLOT_TAXONOMY` (5 standard slots), `PlaneOverride` (manifest escape hatch), `resolveSlotTransform()`. Slot names validated against `/^[a-z][a-z0-9_]*$/`.

**OBJ-008 — Transitions** (`src/transitions/`): 3 types (`cut`, `crossfade`, `dip_to_black`). `computeTransitionOpacity()` for per-frame values. Crossfade: `outgoing + incoming = 1.0`. Dip-to-black: midpoint frame is fully black.

### Scene Geometries (6 of 8 specified)

| Geometry | File | Slots | Required | Default Camera | Fog | Key Feature |
|----------|------|-------|----------|----------------|-----|-------------|
| **stage** (OBJ-018) | `stage.ts` | 6 | 3 (backdrop, floor, subject) | slow_push_forward | #000000, 20-60 | Floor perspective foreshortening |
| **tunnel** (OBJ-019) | `tunnel.ts` | 5 | 4 (floor, left_wall, right_wall, end_wall) | tunnel_push_forward | #000000, 15-50 | Walls converge to vanishing point |
| **canyon** (OBJ-020) | `canyon.ts` | 6 | 4 (sky, left_wall, right_wall, floor) | slow_push_forward | #1a1a2e, 15-48 | Tall walls, vertical drama |
| **flyover** (OBJ-021) | `flyover.ts` | 6 | 2 (sky, ground) | slow_push_forward* | #b8c6d4, 20-55 | Aerial perspective, `ground` not `floor` |
| **diorama** (OBJ-022) | `diorama.ts` | 6 | 2 (backdrop, subject) | slow_push_forward | #0d0d1a, 15-45 | Wing rotation PI/10 (18deg) |
| **close_up** (OBJ-025) | `close_up.ts` | 3 | 2 (backdrop, subject) | gentle_float | #000000, 10-25 | Shallowest subject (Z=-2), all fog-immune |

**\* Flyover's default_camera should be updated to `flyover_glide` at implementation time** (see Inconsistency #5).

**Unspecified:** portal (OBJ-023), panorama (OBJ-024).

### Camera Path Presets (6 of 9 specified)

| Preset | File | Primary Motion | Compatible Geometries | Default Easing |
|--------|------|---------------|----------------------|----------------|
| **static** (OBJ-026) | `static.ts` | None | All 8 | linear |
| **slow_push_forward** (OBJ-027) | `push_pull.ts` | Z: 5 → -3 | All except panorama | ease_in_out |
| **slow_pull_back** (OBJ-027) | `push_pull.ts` | Z: -3 → 5 | All except panorama | ease_in_out |
| **lateral_track_left** (OBJ-028) | `lateral_track.ts` | X: 3 → -3 | stage, diorama, portal, panorama, close_up | ease_in_out |
| **lateral_track_right** (OBJ-028) | `lateral_track.ts` | X: -3 → 3 | stage, diorama, portal, panorama, close_up | ease_in_out |
| **tunnel_push_forward** (OBJ-029) | `tunnel_push.ts` | Z: 5 → -20, Y: -0.3 → 0 | tunnel only | ease_in_out_cubic |
| **flyover_glide** (OBJ-030) | `flyover-glide.ts` | Z: 5 → -25 at Y=8 | flyover only | ease_in_out |
| **gentle_float** (OBJ-031) | `gentle_float.ts` | Sinusoidal drift (X:0.3, Y:0.2, Z:0.4) | All 8 | linear |

**Unspecified:** dramatic_push (OBJ-032), crane_up (OBJ-033), dolly_zoom (OBJ-034).

### Spatial Validation (Tier 3)

**OBJ-040 — Plane Sizing & Edge-Reveal** (`src/spatial/plane-sizing.ts`, `edge-reveal.ts`): Three texture sizing modes (contain/cover/stretch), sampling-based edge-reveal validation, minimum plane size computation. `suggestTextureSizeMode()` heuristic for slot roles.

**OBJ-041 — Spatial Compatibility** (`src/validation/spatial-compatibility.ts`): Scene-level validation (camera in geometry's compatible list), registry consistency (bidirectional), oversizing sufficiency. Coverage analysis for TC-08.

### Geometry-Camera Compatibility Matrix

| Geometry | static | push_fwd | pull_back | lateral_L/R | tunnel_push | flyover_glide | gentle_float |
|----------|--------|----------|-----------|-------------|-------------|---------------|-------------|
| stage | Y | **Y** | Y | Y | - | - | Y |
| tunnel | Y | Y | - | - | **Y** | - | Y |
| canyon | Y | **Y** | - | - | - | - | Y |
| flyover | Y | **Y*** | Y | - | - | Y | Y |
| diorama | Y | **Y** | Y | - | - | - | Y |
| close_up | Y | Y | Y | - | - | - | **Y** |

**Bold** = default camera. **\*** = provisional default pending flyover_glide adoption.

---

## 7. Deliverable 3: SKILL.md

> Full specification: `synthesis/integration_spec.md`, Part 1

### Document Architecture

```
depthkit/
  SKILL.md                              # Primary entry point (<500 lines)
  docs/skill/
    geometry-reference.md               # All geometries: slots, cameras, fog, usage
    camera-reference.md                 # All camera presets: motion, compatibility
    prompt-templates.md                 # Image generation prompts per slot type
    manifest-schema-reference.md        # Complete field reference
    patterns.md                         # Common multi-scene video recipes
```

**Total target:** < 2000 lines / 60KB combined.

### Content (OBJ-070)

Primary file contains: purpose statement, quick-start example (stage + slow_push_forward), complete 5+ scene annotated example, scene authoring workflow checklist, geometry/camera summary tables, inline transitions/easing/audio references, anti-patterns (AP-03, AP-07), CLI usage matching OBJ-046 flags exactly, and sub-file pointers.

### Geometry & Camera Reference (OBJ-071)

Full documentation sections for all verified geometries (stage, tunnel, canyon, flyover, diorama, close_up) and cameras (static, push/pull, lateral track, tunnel push, flyover glide, gentle float). Stub sections for unverified items. **Canyon/lateral-track compatibility asymmetry** documented with warning notes (geometry is authoritative).

### Prompt Templates & Patterns (OBJ-072)

Consumes OBJ-051's `SLOT_PROMPT_REGISTRY` via `getGuidanceForSlots()` to generate per-slot prompt templates. Includes recipe patterns for common video types.

---

## 8. Deliverable 4: n8n-Compatible HTTP Interface

> Full specification: `synthesis/integration_spec.md`, Parts 2-3

### Production Pipeline (Seed Appendix A)

```
1. USER INPUT (topic, duration, style)
        │
2. MANIFEST GENERATION ─── OBJ-056 (Claude API + SKILL.md)
        │
3. NARRATION ─── Chatterbox TTS (external)
        │
4. ASSET RETRIEVAL ─── OBJ-054 (Cache middleware)
   │                   └─ OBJ-053 (Supabase/pgvector schema)
   │                   └─ OBJ-051 (Prompt engineering registry)
   │                   └─ OBJ-052 (Background removal via rembg)
   │
5. VIDEO RENDERING ─── depthkit engine (OBJ-035/046/047)
        │
6. DELIVERY ─── OBJ-055 (n8n HTTP endpoint)
```

### Asset Pipeline Components

**OBJ-051 — Prompt Engineering Registry** (`src/prompts/`): `SLOT_PROMPT_REGISTRY` keyed by (geometry, slot). Per-slot `SlotPromptGuidance` with perspective-aware prompts, alpha requirements, cache categories. Self-contained — no imports from `src/spatial/`.

**OBJ-053 — AssetLibrary Schema** (`sql/`, `src/cache/`): Supabase PostgreSQL + pgvector. `VECTOR(1536)` embeddings, IVFFlat index, `slot_type` + `embedding_model` filtering. R2/S3 storage at `assets/{slot_type}/{id}.png`.

**OBJ-054 — Cache Middleware** (unspecified): Threshold gate at cosine similarity 0.92. Embed prompt → query Supabase → hit/miss routing. Type narrowing from string to `SlotCacheCategory`.

**OBJ-052 — Background Removal** (unspecified): `rembg` subprocess for subject/foreground/landmark slots only.

### n8n Endpoint (OBJ-055, unspecified)

POST endpoint accepting `{ topic, duration, style }`, returning `{ job_id }`. Poll endpoint for status. Download endpoint for MP4. Wraps OBJ-047 library API.

---

## 9. Cross-Category Integration Points

This section documents every interface where a module in one category is consumed by a module in another. These are the seams that must align during implementation.

### 9.1 Engine ← Spatial (Spatial provides data to Engine)

| Engine Consumer | Spatial Provider | Interface | Notes |
|----------------|-----------------|-----------|-------|
| OBJ-004 `ManifestRegistry` | OBJ-005 `registerGeometry()`, OBJ-006 camera registration | `GeometryRegistration`, `CameraRegistration` | Populates validation-only registry |
| OBJ-010 Page Shell defaults | OBJ-003 `DEFAULT_CAMERA` | `fov: 50, near: 0.1, far: 100, position: [0,0,5]` | Hardcoded values must match |
| OBJ-011 `SlotSetup` | OBJ-005 `PlaneSlot` | `position, rotation, size` fields | Orchestrator resolves geometry → SlotSetup |
| OBJ-017 `validateGeometrySlots()` | OBJ-005 `ValidatableGeometry` | Structural interface (not import) | Dependency-injected |
| OBJ-035 Orchestrator | OBJ-005 `GeometryRegistry` | Slot spatial data for scene setup | Primary spatial integration |
| OBJ-035 Orchestrator | OBJ-006 `CameraPathRegistry` | `evaluate(t, params)` for per-frame camera | Primary camera integration |
| OBJ-035 Orchestrator | OBJ-007 `resolveSlotTransform()` | Merge geometry defaults + manifest overrides | Runtime slot resolution |
| OBJ-036 Scene Sequencer | OBJ-008 `TransitionSpec` | Transition type/duration from manifest | Timeline construction |

### 9.2 Engine ← Engine (Internal engine dependencies)

| Consumer | Provider | Interface |
|----------|----------|-----------|
| OBJ-035 | OBJ-009, OBJ-011, OBJ-012, OBJ-013, OBJ-014, OBJ-036, OBJ-038, OBJ-048, OBJ-049 | All composed into render loop |
| OBJ-011 | OBJ-010 | Page shell's `window.depthkit` API |
| OBJ-039 | OBJ-011 | `SlotSetup` → Three.js meshes |
| OBJ-016 | OBJ-004 | Zod schemas for structural parse |

### 9.3 Spatial ← Engine (Engine provides math to Spatial)

| Spatial Consumer | Engine Provider | Interface |
|-----------------|----------------|-----------|
| OBJ-006 `resolveCameraParams()` | OBJ-002 `getEasing()` | Easing function lookup |
| OBJ-006 `evaluate()` | OBJ-002 `interpolate()` | Range interpolation |
| OBJ-008 `computeTransitionOpacity()` | OBJ-002 easing functions | Eased opacity curves |

### 9.4 Integration ← Engine (Engine provides infrastructure to Integration)

| Integration Consumer | Engine Provider | Interface |
|--------------------|----------------|-----------|
| OBJ-058 Test Render | OBJ-035 `Orchestrator` | `render()` with quality presets |
| OBJ-073 Determinism | OBJ-035 `Orchestrator`, OBJ-013 `resolveFFmpegPath()` | Multi-run render + comparison |
| OBJ-074 Benchmark | OBJ-035 `Orchestrator`, OBJ-049 `resolveRenderingConfig()` | Timed render with environment info |
| OBJ-077 E2E Tests | OBJ-046 CLI | `depthkit render`, `depthkit validate` commands |
| OBJ-055 n8n Endpoint | OBJ-047 `render()` | Programmatic render interface |

### 9.5 Integration ← Spatial (Spatial provides content to Integration)

| Integration Consumer | Spatial Provider | Interface |
|--------------------|-----------------|-----------|
| OBJ-051 Prompt Registry | OBJ-007 `DepthSlot.expectsAlpha` | Alpha requirement per slot |
| OBJ-070/071 SKILL.md | OBJ-005 geometry definitions, OBJ-006 camera definitions | Documentation content |
| OBJ-074 Benchmark | OBJ-018 stage geometry | Reference benchmark fixture |
| OBJ-075 Blind Authoring | All geometries/cameras | Test topics mapped to geometries |

### 9.6 Integration ← Integration (Internal integration dependencies)

| Consumer | Provider | Interface |
|----------|----------|-----------|
| OBJ-054 Cache Middleware | OBJ-051 `getCacheCategory()`, OBJ-053 SQL queries | Category routing + DB access |
| OBJ-057 Asset Orchestration | OBJ-054, OBJ-052 | Cache lookup + background removal |
| OBJ-056 Manifest Generation | OBJ-071 SKILL.md | Geometry/camera knowledge base |
| OBJ-072 SKILL.md Prompts | OBJ-051 `getGuidanceForSlots()` | Prompt template content |
| OBJ-078 Execution Gate | OBJ-077 test plans | Procedure execution |

---

## 10. Consolidated File Manifest

Complete file tree for the depthkit project, annotated with owning objectives.

```
depthkit/
├── src/
│   ├── interpolation/                  # OBJ-002
│   │   ├── easings.ts                  #   6 named easings + registry
│   │   ├── interpolate.ts              #   Range interpolation
│   │   ├── spring.ts                   #   Damped spring physics
│   │   └── index.ts                    #   Barrel export
│   │
│   ├── spatial/                        # OBJ-003, OBJ-007, OBJ-040
│   │   ├── types.ts                    #   Vec3, EulerRotation, Size2D, CameraState, etc.
│   │   ├── constants.ts                #   AXIS, DEFAULT_CAMERA, PLANE_ROTATIONS, etc.
│   │   ├── math.ts                     #   computeFrustumRect, computePlaneSize, etc.
│   │   ├── depth-model.ts             #   DepthSlot, DEFAULT_SLOT_TAXONOMY, resolveSlotTransform
│   │   ├── plane-sizing.ts            #   TextureSizeMode, computeTexturePlaneSize
│   │   ├── edge-reveal.ts             #   PlaneMargins, validateGeometryEdgeReveal
│   │   └── index.ts                    #   Barrel export
│   │
│   ├── scenes/
│   │   ├── geometries/                 # OBJ-005, OBJ-018–025
│   │   │   ├── types.ts               #   PlaneSlot, SceneGeometry, FogConfig
│   │   │   ├── registry.ts            #   registerGeometry, getGeometry, lock-on-first-read
│   │   │   ├── validate.ts            #   validateGeometryDefinition
│   │   │   ├── slot-utils.ts          #   getRequiredSlotNames, isCameraCompatible
│   │   │   ├── stage.ts               #   OBJ-018: 6 slots, 3 required
│   │   │   ├── tunnel.ts              #   OBJ-019: 5 slots, 4 required + tunnelSlotGuidance
│   │   │   ├── canyon.ts              #   OBJ-020: 6 slots, 4 required
│   │   │   ├── flyover.ts             #   OBJ-021: 6 slots, 2 required
│   │   │   ├── diorama.ts             #   OBJ-022: 6 slots, 2 required
│   │   │   ├── close_up.ts            #   OBJ-025: 3 slots, 2 required
│   │   │   └── index.ts               #   Barrel + geometry imports (triggers registration)
│   │   │
│   │   └── scene-sequencer.ts         # OBJ-036: planFrame(), boundary resolution
│   │
│   ├── camera/                         # OBJ-006, OBJ-026–031
│   │   ├── types.ts                    #   CameraFrameState, CameraParams, CameraPathPreset
│   │   ├── registry.ts                #   getCameraPath, listCameraPathNames
│   │   ├── validate.ts                #   validateCameraPathPreset
│   │   ├── presets/
│   │   │   ├── static.ts              #   OBJ-026
│   │   │   ├── push_pull.ts           #   OBJ-027: slow_push_forward, slow_pull_back
│   │   │   ├── lateral_track.ts       #   OBJ-028: lateral_track_left, lateral_track_right
│   │   │   ├── tunnel_push.ts         #   OBJ-029: tunnel_push_forward
│   │   │   ├── flyover-glide.ts       #   OBJ-030: flyover_glide
│   │   │   └── gentle_float.ts        #   OBJ-031: gentle_float
│   │   └── index.ts                    #   Barrel + preset imports
│   │
│   ├── transitions/                    # OBJ-008
│   │   ├── types.ts                    #   TransitionTypeName, TransitionSpec
│   │   ├── presets.ts                  #   cut, crossfade, dip_to_black definitions
│   │   ├── compute.ts                 #   computeTransitionOpacity
│   │   ├── resolve.ts                 #   resolveTransition (seconds → frames)
│   │   └── index.ts                    #   Barrel export
│   │
│   ├── manifest/                       # OBJ-004, OBJ-016, OBJ-017
│   │   ├── schema.ts                  #   Zod schemas, ManifestRegistry interface
│   │   ├── loader.ts                  #   Two-phase validation pipeline
│   │   └── validate-geometry.ts       #   Geometry slot matching
│   │
│   ├── engine/                         # OBJ-009–014, OBJ-035, OBJ-038, OBJ-048–049
│   │   ├── frame-clock.ts             #   OBJ-009: Deterministic frame-timestamp mapping
│   │   ├── puppeteer-bridge.ts        #   OBJ-009: Chromium lifecycle manager
│   │   ├── page-types.ts             #   OBJ-010: Node-side boundary types
│   │   ├── protocol-types.ts         #   OBJ-011: Protocol data structures
│   │   ├── page-protocol.ts          #   OBJ-011: Typed command interface
│   │   ├── frame-capture.ts          #   OBJ-012: CDP/canvas frame capture
│   │   ├── ffmpeg-encoder.ts         #   OBJ-013: H.264 encoding via FFmpeg stdio
│   │   ├── audio-muxer.ts            #   OBJ-014: Video+audio muxing
│   │   ├── texture-types.ts          #   OBJ-015: Texture metadata types
│   │   ├── texture-warnings.ts       #   OBJ-015: Texture warning checks
│   │   ├── scene-timing.ts           #   OBJ-038: Timeline resolution (3 modes)
│   │   ├── rendering-config.ts       #   OBJ-049: Software/hardware WebGL config
│   │   ├── errors.ts                 #   OBJ-048: Error classification + reporting
│   │   ├── determinism.ts            #   OBJ-073: Deterministic output verification
│   │   └── orchestrator.ts           #   OBJ-035: Main render loop
│   │
│   ├── validation/                     # OBJ-041
│   │   ├── spatial-compatibility.ts   #   Scene-level + registry + oversizing validation
│   │   └── coverage-analysis.ts       #   TC-08 geometry-camera matrix
│   │
│   ├── page/                           # Browser-side (loaded by Puppeteer)
│   │   ├── index.html                 #   OBJ-010: HTML shell with canvas
│   │   ├── scene-renderer.js          #   OBJ-010+011: Three.js init + protocol
│   │   ├── geometry-library.js        #   OBJ-039: Mesh creation from SlotSetup
│   │   ├── texture-loader.js          #   OBJ-015: Browser-side texture loading
│   │   └── message-handler.js         #   OBJ-011: Protocol message dispatch
│   │
│   ├── prompts/                        # OBJ-051
│   │   ├── types.ts                   #   SlotPromptGuidance, SlotCacheCategory
│   │   ├── slot-prompt-registry.ts    #   SLOT_PROMPT_REGISTRY, resolvePromptGuidance
│   │   └── index.ts                    #   Barrel export
│   │
│   ├── cache/                          # OBJ-053
│   │   ├── asset-library.types.ts     #   AssetLibraryRow, AssetSimilarityResult
│   │   └── index.ts                    #   Barrel export
│   │
│   ├── benchmark/                      # OBJ-074
│   │   ├── runner.ts                  #   runBenchmark(), reference manifest
│   │   └── fixtures/
│   │       └── generate-assets.ts     #   Solid-color PNG generation via zlib
│   │
│   ├── tools/                          # OBJ-058
│   │   ├── test-render.ts             #   renderTestClip(), quality presets
│   │   └── tuning-log-schema.ts       #   TuningLog Zod schema
│   │
│   ├── cli.ts                         # OBJ-046: CLI entry point (commander)
│   ├── cli/
│   │   ├── format.ts                  #   Output formatting
│   │   ├── colors.ts                  #   ANSI color utilities
│   │   └── registry-init.ts           #   Re-exports from registry.ts
│   │
│   ├── registry.ts                    # OBJ-047: Shared registry initialization
│   ├── index.ts                       # OBJ-047: Library API entry point
│   └── api.ts                         # OBJ-047: render(), renderFile()
│
├── sql/                                # OBJ-053
│   ├── 001_create_asset_library.sql
│   └── 002_create_match_asset.sql     # Optional RPC
│
├── test/plans/                         # OBJ-075, OBJ-077
│   ├── blind-authoring/
│   │   ├── README.md
│   │   ├── topics-25.md
│   │   ├── scene-types-15.md
│   │   ├── scoring-rubric.md
│   │   ├── tc08-geometry-mapping.md
│   │   ├── tc04-manifest-validation.md
│   │   ├── tc01-plane-sufficiency.md
│   │   ├── sc02-blind-authoring.md
│   │   └── results/
│   └── e2e/                            # OBJ-077
│       ├── fixtures/
│       └── procedures/
│
├── SKILL.md                            # OBJ-070: Primary entry point
├── docs/skill/                         # OBJ-070, OBJ-071, OBJ-072
│   ├── geometry-reference.md
│   ├── camera-reference.md
│   ├── prompt-templates.md
│   ├── manifest-schema-reference.md
│   └── patterns.md
│
├── package.json
└── tsconfig.json
```

---

## 11. Implementation Order

### Phase 1: Foundations (no dependencies)

Parallel execution. All modules have zero internal dependencies.

| Track | Objectives | Output |
|-------|-----------|--------|
| **A: Engine math** | OBJ-002 (interpolation) | `src/interpolation/` |
| **B: Spatial math** | OBJ-003 (spatial types/math) | `src/spatial/types.ts`, `constants.ts`, `math.ts` |
| **C: Schema** | OBJ-004 (manifest schema) | `src/manifest/schema.ts` |

### Phase 2: Type Contracts (depends on Phase 1)

| Track | Objectives | Dependencies | Output |
|-------|-----------|-------------|--------|
| **A: Geometry contract** | OBJ-005 | OBJ-003 | `src/scenes/geometries/{types,registry,validate}.ts` |
| **B: Camera contract** | OBJ-006 | OBJ-003, OBJ-002 | `src/camera/{types,registry,validate}.ts` |
| **C: Depth model** | OBJ-007 | OBJ-003 | `src/spatial/depth-model.ts` |
| **D: Transitions** | OBJ-008 | OBJ-002 | `src/transitions/` |
| **E: Engine infra** | OBJ-009, OBJ-010 | OBJ-003 (constants) | `src/engine/{frame-clock,puppeteer-bridge}.ts`, `src/page/` |

### Phase 3: Content + Components (depends on Phase 2)

Large parallel phase. Geometries, cameras, and engine components can all proceed independently.

| Track | Objectives | Dependencies | Output |
|-------|-----------|-------------|--------|
| **A: Geometries** | OBJ-018–025 | OBJ-005, OBJ-007 | `src/scenes/geometries/{stage,tunnel,...}.ts` |
| **B: Camera presets** | OBJ-026–031 | OBJ-006 | `src/camera/presets/*.ts` |
| **C: Engine protocol** | OBJ-011, OBJ-015 | OBJ-009, OBJ-010 | `src/engine/page-protocol.ts`, `src/page/texture-loader.js` |
| **D: Engine capture/encode** | OBJ-012, OBJ-013, OBJ-014 | OBJ-009 | `src/engine/{frame-capture,ffmpeg-encoder,audio-muxer}.ts` |
| **E: Engine validation** | OBJ-016, OBJ-017 | OBJ-004, OBJ-005 | `src/manifest/{loader,validate-geometry}.ts` |
| **F: Engine sequencing** | OBJ-036, OBJ-038 | OBJ-009, OBJ-008 | `src/scenes/scene-sequencer.ts`, `src/engine/scene-timing.ts` |
| **G: Spatial validation** | OBJ-040, OBJ-041 | OBJ-003, OBJ-005, OBJ-006 | `src/spatial/{plane-sizing,edge-reveal}.ts`, `src/validation/` |
| **H: Page-side geometry** | OBJ-039 | OBJ-011 | `src/page/geometry-library.js` |
| **I: Config/errors** | OBJ-048, OBJ-049 | OBJ-009 | `src/engine/{errors,rendering-config}.ts` |
| **J: Prompt registry** | OBJ-051 | None (self-contained) | `src/prompts/` |
| **K: Cache schema** | OBJ-053 | None | `sql/`, `src/cache/` |

### Phase 4: Orchestration (depends on Phase 3 A-I)

| Objective | Dependencies | Output |
|-----------|-------------|--------|
| **OBJ-035** Orchestrator | OBJ-009, OBJ-010, OBJ-011, OBJ-012, OBJ-013, OBJ-014, OBJ-016, OBJ-036, OBJ-038, OBJ-048, OBJ-049 + all spatial registries | `src/engine/orchestrator.ts` |

**This is the integration bottleneck.** All engine and spatial components must be ready before the orchestrator can be fully implemented and tested.

### Phase 5: Interfaces + Documentation (depends on Phase 4)

| Track | Objectives | Dependencies | Output |
|-------|-----------|-------------|--------|
| **A: CLI + Library** | OBJ-046, OBJ-047 | OBJ-035 | `src/cli.ts`, `src/index.ts`, `src/api.ts`, `src/registry.ts` |
| **B: Director tools** | OBJ-058 | OBJ-035 | `src/tools/test-render.ts` |
| **C: SKILL.md** | OBJ-070, OBJ-071, OBJ-072 | OBJ-004, OBJ-046, all geometries/cameras, OBJ-051 | `SKILL.md`, `docs/skill/` |
| **D: Verification tools** | OBJ-073, OBJ-074 | OBJ-035, OBJ-049 | `src/engine/determinism.ts`, `src/benchmark/` |

### Phase 6: Visual Tuning (depends on Phase 5B)

Sequential per geometry. Each requires the HITL Director Agent loop (OBJ-058 workflow).

| Objectives | Target | Budget |
|-----------|--------|--------|
| OBJ-059 | Stage tuning | ≤5 rounds |
| OBJ-060 | Tunnel tuning | ≤5 rounds |
| OBJ-061 | Canyon tuning | ≤5 rounds |
| OBJ-062 | Flyover tuning | ≤5 rounds |
| OBJ-063 | Diorama tuning | ≤5 rounds |
| OBJ-064 | Close-up tuning | ≤5 rounds |
| OBJ-065/066 | Portal/Panorama tuning | ≤5 rounds |
| OBJ-067 | Visual gate (all geometries signed off) | - |
| OBJ-068 | Transition tuning | ≤5 rounds |

**SC-07 gate:** Every geometry's `meta.json` must show `"visual_status": "tuned"` before production readiness.

### Phase 7: Production Pipeline (depends on Phase 5C, 5D)

| Objectives | Dependencies | Output |
|-----------|-------------|--------|
| OBJ-052 Background removal | None (external tool) | Subprocess wrapper |
| OBJ-054 Cache middleware | OBJ-051, OBJ-053 | Threshold gate logic |
| OBJ-055 n8n endpoint | OBJ-047 | HTTP server |
| OBJ-056 Manifest generation | OBJ-071 (SKILL.md) | Claude API prompt |
| OBJ-057 Asset orchestration | OBJ-054, OBJ-052 | Pipeline glue |
| OBJ-050 Docker | OBJ-046 | Dockerfile |

### Phase 8: Capstone Validation (depends on everything)

| Objectives | Validates | Output |
|-----------|-----------|--------|
| OBJ-075 Blind authoring tests | TC-08, TC-04, TC-01, SC-02 | Test procedures + results |
| OBJ-076 Cache validation | TC-17, TC-18, TC-19, TC-20 | Test procedures + results |
| OBJ-077 E2E test plan | SC-01, SC-03, SC-05, SC-06 | Test suites + fixtures |
| **OBJ-078 Execution gate** | ALL success criteria | **PROJECT COMPLETE** |

---

## 12. Consolidated Inconsistencies

All inconsistencies identified across the three category specs, with severity, status, and resolution guidance.

### I-1: Duplicate Texture Loading Paths (engine)

**Source:** OBJ-015 vs OBJ-039 | **Severity:** Medium

OBJ-015 defines `window.depthkit.loadTexture()` with caching. OBJ-039 uses `THREE.TextureLoader.loadAsync()` directly (documented in OBJ-039 D2 as intentional).

**Resolution:** OBJ-039 owns the production texture loading path. OBJ-015's cache API may be useful for preview mode but is not in the hot path.

### I-2: CameraParams `offset` Field Missing from Schema (engine)

**Source:** OBJ-004 vs OBJ-006 | **Severity:** Low

OBJ-006 defines `CameraParams.offset?: Vec3`. OBJ-004's `CameraParamsSchema` does not include `offset`.

**Resolution:** Camera offset is preset-internal only. If manifest-level offset is needed, extend `CameraParamsSchema`.

### I-3: Independent Fade Algorithm in Scene Sequencer (engine)

**Source:** OBJ-036 vs OBJ-008 | **Severity:** Low

OBJ-036 computes dip_to_black opacity independently rather than importing from OBJ-008.

**Resolution:** Acceptable for V1. If transition easing is added to dip_to_black, both must be updated.

### I-4: Overlapping Frame-State Functions (engine)

**Source:** OBJ-038 `resolveFrameState()` vs OBJ-036 `planFrame()` | **Severity:** Medium

Both compute per-frame active scenes with opacity and normalizedTime.

**Resolution:** OBJ-038 for timeline resolution, OBJ-036 for per-frame planning. Orchestrator uses OBJ-038 first, then OBJ-036.

### I-5: Transition Renderer Spec Gap (engine)

**Source:** OBJ-037 | **Severity:** Low

OBJ-037 has no full spec. Transition rendering is covered by OBJ-011 + OBJ-036 + OBJ-035.

**Resolution:** OBJ-037 may be vestigial.

### I-6: PlaneSlot vs DepthSlot Type Gap (spatial)

**Source:** OBJ-005 vs OBJ-007 | **Severity:** Medium

`PlaneSlot` (geometry registry) and `DepthSlot` (depth model) are related but structurally different. No formal subtype relationship. Geometries handle this inconsistently: stage uses PlaneSlot only, tunnel exports separate guidance, canyon includes DepthSlot metadata inline.

**Resolution:** Either merge DepthSlot metadata into PlaneSlot, or mandate a standard companion export pattern. Canyon's structural typing approach is most pragmatic.

### I-7: Registry Pattern Divergence (spatial)

**Source:** OBJ-005 (singleton) vs OBJ-006 (parameter-based) | **Severity:** Low

**Resolution:** Acceptable per OBJ-006 D7. `src/registry.ts` is the canonical assembly point.

### I-8: Incomplete Prompt Guidance Coverage (spatial)

**Source:** OBJ-018, OBJ-021, OBJ-022, OBJ-025 | **Severity:** Medium

Only tunnel and canyon export per-slot prompt guidance. Stage, flyover, diorama, and close_up do not.

**Resolution:** All geometries should export companion guidance (like `tunnelSlotGuidance`) for OBJ-051 consumption.

### I-9: Forward References to Unspecified Presets (spatial)

**Source:** OBJ-018 (stage), OBJ-020 (canyon), OBJ-022 (diorama) | **Severity:** Medium

Declare compatibility with `dramatic_push` (OBJ-032) and `crane_up` (OBJ-033) — neither is specified.

**Resolution:** `validateRegistryConsistency()` should warn (not error) on unregistered camera names, or these presets must be specified first.

### I-10: Flyover default_camera Provisional (spatial)

**Source:** OBJ-021 vs OBJ-030 | **Severity:** Low

Flyover declares `default_camera: 'slow_push_forward'` but `flyover_glide` (OBJ-030) is now verified.

**Resolution:** Update flyover's `default_camera` to `'flyover_glide'` at implementation time.

### I-11: Lateral Track / Canyon Compatibility Asymmetry (integration)

**Source:** OBJ-028 vs OBJ-020 | **Severity:** Low

OBJ-028 claims canyon compatibility; OBJ-020 does not list lateral tracks. Geometry is authoritative (OBJ-004 D-03).

**Resolution:** Document in SKILL.md with warning notes. Consider upstream resolution.

### I-12: OBJ-077 Fixture Camera Compatibility Issues (integration)

**Source:** OBJ-077 F-01 fixture | **Severity:** Medium

Benchmark fixture uses `lateral_track_left` for canyon (incompatible per OBJ-020) and `crane_up` for flyover (unspecified OBJ-033).

**Resolution:** OBJ-078 must adjust F-01 to use only verified, compatible cameras.

### I-13: OBJ-051 Supersedes All `promptGuidance` Fields (integration)

**Source:** OBJ-051 D8 | **Severity:** Low

OBJ-051's `SLOT_PROMPT_REGISTRY` supersedes `promptGuidance` strings in OBJ-007 and geometry specs. Downstream consumers must import from `src/prompts/`, not from spatial types.

**Resolution:** Documented. No code conflict.

---

## 13. Consolidated Open Questions

Open questions from the seed document, annotated with current status based on verified specs.

| # | Question | Status | Resolution / Notes |
|---|---------|--------|-------------------|
| OQ-01 | Per-frame opacity animation? | **Deferred.** OBJ-007 D7: static opacity only in V1. OBJ-044 created as deferred node. |
| OQ-02 | Best strategy for images without alpha? | **Partially addressed.** OBJ-052 (rembg subprocess) created but unspecified. OBJ-051 defines `requiresAlpha` per slot. |
| OQ-03 | Subtitle/caption overlay? | **Deferred.** OBJ-043 (HUD/overlay planes) created but unspecified. Page shell architecture (HTML over canvas) supports it. |
| OQ-04 | Vertical (9:16) video adaptation? | **Deferred.** OBJ-045 created but unspecified. Geometries declare `preferred_aspect` (advisory). Close-up and stage support `'both'`. |
| OQ-05 | Browser-based preview mode? | **Stub.** OBJ-046 includes `depthkit preview` command stub. Not fully specified. |
| OQ-06 | Camera path composition (chaining)? | **Deferred.** OBJ-079 created but unspecified. |
| OQ-07 | Minimum viable geometry count? | **Answered: 6.** Stage, tunnel, canyon, flyover, diorama, close_up all specified. Portal and panorama deferred. |
| OQ-08 | Dynamic plane count? | **Deferred.** OBJ-080 created but unspecified. |
| OQ-09 | Lighting? | **Deferred.** OBJ-081 created but unspecified. OBJ-010 D8: `MeshBasicMaterial` (unlit) for V1. |
| OQ-10 | Parallelized multi-instance rendering? | **Not addressed.** No objective created. C-08 target is single-instance. |

---

## 14. Verification and Success Criteria Traceability

### Success Criteria → Objectives

| Criterion | Description | Key Objectives | Test Procedures |
|-----------|-------------|---------------|-----------------|
| **SC-01** | 60s 5-scene video renders to valid MP4 | OBJ-035, OBJ-013, OBJ-014, OBJ-036 | OBJ-077: SC01-01 through SC01-04 |
| **SC-02** | LLM authors 5 manifests, 4/5 look correct | OBJ-070, OBJ-071, all geometries | OBJ-075: SC-02 procedure |
| **SC-03** | 60s renders in < 15 min on 4-core VPS | OBJ-035, OBJ-049, OBJ-012 | OBJ-074 benchmark, OBJ-077: SC03-01/02 |
| **SC-04** | SKILL.md is self-sufficient | OBJ-070, OBJ-071, OBJ-072 | OBJ-075: TC-04 procedure |
| **SC-05** | n8n integration works | OBJ-055, OBJ-047 | OBJ-077: SC05-01/02/03 |
| **SC-06** | Validation is comprehensive | OBJ-004, OBJ-016, OBJ-017 | OBJ-077: SC06-FORWARD/BACKWARD |
| **SC-07** | All geometries visually tuned | OBJ-059–066, OBJ-067, OBJ-058 | OBJ-067 visual gate |

### Testable Claims → Objectives

| Claim | Description | Key Objectives | Status |
|-------|-------------|---------------|--------|
| TC-01 | 5 planes per scene sufficient | OBJ-018–025, OBJ-075 | Verified: 6 geometries use 3-6 slots |
| TC-02 | < 500ms/frame software WebGL | OBJ-074 | Test procedure defined |
| TC-03 | Perspective projection convincing | OBJ-019 (tunnel), OBJ-058 | Requires visual tuning |
| TC-04 | Geometries eliminate manual positioning | OBJ-075 | Test procedure defined |
| TC-05 | Tunnel produces convincing depth | OBJ-019, OBJ-029, OBJ-060 | Requires visual tuning |
| TC-06 | Virtualized clock is deterministic | OBJ-073 | Test procedure defined |
| TC-07 | Validation catches common errors | OBJ-077: SC06-BACKWARD | 22 invalid manifests defined |
| TC-08 | 8 geometries cover design space | OBJ-041, OBJ-075 | Test procedure defined |
| TC-09 | Eased paths feel more natural | OBJ-058 (Director) | Requires visual tuning |
| TC-10 | Transitions mask compositing seams | OBJ-068 | Requires visual tuning |
| TC-11 | Engine runs in Docker with software WebGL | OBJ-050 | Unspecified |
| TC-12 | rembg viable as subprocess | OBJ-052 | Unspecified |
| TC-13 | Audio duration drives video length | OBJ-038, OBJ-077: SC01-04 | Test procedure defined |
| TC-14 | FOV animation useful | OBJ-034 (dolly zoom) | Unspecified, deferred |
| TC-15 | Director workflow converges ≤5 rounds | OBJ-058 | Budget defined, untested |
| TC-16 | Director-tuned outperforms blind-authored | OBJ-058 | Baseline capture defined |
| TC-17 | 0.92 threshold produces acceptable reuse | OBJ-076 | Unspecified |
| TC-18 | Slot-type filtering prevents contamination | OBJ-076 | Unspecified |
| TC-19 | Cache hit rates reach 30-60% | OBJ-076 | Unspecified |
| TC-20 | Embedding query latency negligible | OBJ-076 | Unspecified |

---

## 15. Constraint Compliance Map

| Constraint | Description | Enforcing Modules | Status |
|-----------|-------------|------------------|--------|
| **C-01** | Zero-license Node.js app | All — only Three.js (MIT), Puppeteer (Apache-2.0), FFmpeg (LGPL via stdio), Zod (MIT), Commander (MIT) | **Compliant by design** |
| **C-02** | Puppeteer + Three.js + FFmpeg pipeline | OBJ-009, OBJ-010, OBJ-011, OBJ-012, OBJ-013, OBJ-035 | **Fully specified** |
| **C-03** | Deterministic virtualized timing | OBJ-009 (FrameClock), OBJ-035 (render loop), OBJ-010 (no RAF) | **Fully specified** |
| **C-04** | 1920x1080 + 1080x1920, 24/30fps | OBJ-004 (schema), OBJ-009 (clock), OBJ-049 (config) | **Fully specified** |
| **C-05** | Deterministic output | OBJ-073 (verification), OBJ-010 D4 (no antialias), OBJ-013 (deterministic flag) | **Fully specified + verification tool** |
| **C-06** | Blind-authorable | OBJ-005, OBJ-006, OBJ-070, OBJ-071, OBJ-075 | **Fully specified + test plan** |
| **C-07** | Audio synchronization | OBJ-038 (3 timing modes), OBJ-014 (muxing) | **Fully specified** |
| **C-08** | < 15 min on 4-core VPS | OBJ-074 (benchmark), OBJ-077 (SC03-02) | **Benchmark + test plan defined** |
| **C-09** | Image format tolerance (alpha) | OBJ-015 (alpha detection), OBJ-051 (requiresAlpha), OBJ-052 (rembg) | **Partially specified** (OBJ-052 unspecified) |
| **C-10** | Manifest validation (fail fast) | OBJ-004, OBJ-016, OBJ-017, OBJ-041 | **Fully specified** |
| **C-11** | Software rendering baseline | OBJ-049 (SwiftShader config), OBJ-074 (benchmark), OBJ-050 (Docker) | **Config specified** (Docker unspecified) |

---

*End of final consolidated specification. This document maps to the three per-category specs:*
- *`synthesis/engine_spec.md` — rendering engine infrastructure (22 objectives)*
- *`synthesis/spatial_spec.md` — spatial authoring vocabulary (19 verified + 12 unspecified objectives)*
- *`synthesis/integration_spec.md` — documentation, asset pipeline, deployment, verification (18 objectives)*

*The project is production-ready when OBJ-078 (End-to-End Validation Execution Gate) passes all procedures defined in OBJ-077.*
