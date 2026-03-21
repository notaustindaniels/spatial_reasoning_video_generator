# Seed Document: Parallax Engine for Autonomous 2.5D Video Production

**Seed Version:** 3.0  
**Domain:** Programmatic video generation  
**Codename:** `depthkit`  
**Revision Note:** v3.0 removes Remotion as a dependency and mandates a custom zero-license rendering pipeline: Puppeteer (headless Chromium) loads a Three.js WebGL canvas, deterministically steps through frames using a virtualized clock, extracts pixel buffers, and pipes them directly into FFmpeg via stdio. This eliminates all third-party licensing concerns while retaining the full 2.5D camera projection architecture from v2.0.

---

## Section 1: Goal Statement

Build a **custom, zero-license Node.js video engine** — called **depthkit** — that accepts a declarative JSON scene manifest and renders a finished MP4 video file with synchronized audio. The engine uses **Puppeteer** to load a **Three.js** WebGL canvas in headless Chromium, deterministically steps through frames using a virtualized clock, extracts pixel buffers, and pipes them directly into **FFmpeg** via stdio to encode the final MP4. It maps AI-generated 2D images onto flat mesh planes positioned in a true 3D scene, then moves a perspective camera through that scene to produce **2.5D camera projection** — the effect seen in After Effects camera projection and Procreate Dreams, where flat images undergo real perspective distortion as the camera navigates Z-depth, vanishing points, tunnels, and flythrough spaces.

This is not flat side-scrolling parallax. The camera physically moves through 3D space. Walls recede to vanishing points. Floors skew into perspective. The depth illusion comes from WebGL's native perspective projection matrix, not from manually computing 2D displacement per layer.

The engine must be authorable by an LLM that cannot see its own output. This is the defining constraint. Every spatial decision — mesh placement in XYZ space, camera trajectory, scene geometry — must be expressible as a selection from a finite vocabulary of validated presets, or as parameterized values within mathematically proven safe ranges. The engine must make it trivially easy to produce correct video and structurally difficult to produce broken video.

The final deliverable includes:

1. The **depthkit rendering engine** — a custom Node.js application with a Three.js scene renderer, a Puppeteer-based frame capture pipeline, an FFmpeg encoder, a CLI interface, and an importable library for programmatic use. Zero third-party video framework licenses.
2. A **spatial authoring vocabulary** — the library of scene geometries (tunnel, flyover, stage, canyon, etc.), depth models, camera paths, and composition rules that an LLM uses to author scenes without performing raw 3D math.
3. A **SKILL.md** — a single document (or primary document with modular sub-files) that teaches any LLM agent how to use depthkit to produce 2.5D parallax videos.
4. An **n8n-compatible HTTP interface** — a thin wrapper that accepts a topic and duration, orchestrates asset generation (via external APIs), and returns an MP4.

---

## Section 2: Vocabulary

These terms are binding across all sessions. If a term needs refinement, the change must be proposed through the review process and propagated back to this seed.

### Canvas
The output frame. Fixed dimensions per video. Default: 1920×1080 (16:9). In the rendering pipeline, this is the viewport of the headless Chromium browser — the pixel dimensions that the Three.js `<PerspectiveCamera>` renders to and that Puppeteer captures.

### Plane (formerly "Layer")
A flat `<mesh>` in Three.js with a `<planeGeometry>` that has a 2D image mapped onto it as a texture. Every visible element in a scene is a plane. Planes are positioned in 3D space using `position={[x, y, z]}` and can be rotated using `rotation={[rx, ry, rz]}` (in radians). The perspective camera's projection matrix handles all depth, foreshortening, and vanishing-point distortion natively — no manual parallax calculation required.

### Depth Slot
A named position in the scene's Z-axis layout. Not a raw Z coordinate — a semantic label (e.g., `sky`, `back_wall`, `floor`, `subject`, `near_fg`). Each depth slot maps to a specific `[x, y, z]` position and `[rx, ry, rz]` rotation in 3D space, defined by the scene geometry template. The mapping from slot names to 3D transforms is defined once per scene geometry and is not recomputed per scene.

### Scene Geometry
A pre-validated 3D arrangement of planes for a common scene type. This replaces the v1 concept of "layout template." A scene geometry defines the spatial structure of the entire 3D environment — not just where images go, but the shape of the space itself. Examples: **tunnel** (floor, ceiling, left wall, right wall receding to a vanishing point), **stage** (flat backdrop with a floor plane and side wings), **canyon** (tall walls on either side with a floor), **flyover** (ground plane below, sky dome above, camera glides forward). Each geometry defines which planes exist, their positions/rotations in 3D space, and which depth slots map to which planes.

### Camera Path
A parametric 3D trajectory for the `<PerspectiveCamera>`. Expressed as `position(t) = [x(t), y(t), z(t)]` and `lookAt(t) = [lx(t), ly(t), lz(t)]` as functions of normalized time `t ∈ [0, 1]`. Camera paths are selected from a library of named presets tied to specific scene geometries. Unlike v1's 2D displacement model, the camera physically moves through 3D space — pushing forward on Z, rising on Y, tracking laterally on X — and the perspective projection matrix handles all apparent motion of the planes.

### Field of View (FOV)
The vertical angle of the perspective camera's view frustum, in degrees. Default: 50°. A narrower FOV (e.g., 35°) compresses depth and feels more telephoto. A wider FOV (e.g., 75°) exaggerates perspective and feels more dramatic. FOV can be animated over time as part of a camera path preset (e.g., a "dolly zoom" effect).

### Scene
A temporal segment of the video. Has a duration (in seconds), a scene geometry, plane assignments (which images map to which geometry slots), a camera path preset, and transition settings for entering/exiting. A video is an ordered sequence of scenes. Each scene is a self-contained Three.js scene graph with its own camera and plane arrangement.

### Manifest
The complete JSON document that describes an entire video. Contains: global settings (resolution, fps, audio track), an ordered array of scenes, and metadata. The manifest is the contract between the LLM author and the rendering engine.

### Easing
A timing function applied to camera paths and transitions. Named presets: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_cubic`, `ease_in_out_cubic`. All easing functions map `t ∈ [0,1] → t' ∈ [0,1]`. Implemented as pure JavaScript functions in the engine's interpolation module.

### Transition
A visual effect applied at scene boundaries. Named presets: `cut` (instant), `crossfade` (opacity blend over N frames), `dip_to_black` (fade out then fade in). Transitions have a duration in seconds. Implemented by the engine's scene sequencer, which renders overlapping scenes with animated opacity during transition windows.

### Composition
The top-level container for a video. One composition equals one video. Contains global settings (resolution, fps, total duration in frames) and an ordered list of scenes with their timing. The engine's scene sequencer iterates through the composition frame-by-frame, rendering the active scene(s) for each frame.

### HUD Layer
A 2D overlay rendered on top of the 3D scene, not affected by perspective projection. Used for titles, captions, subtitles, and any text or UI elements. Implemented as HTML/CSS elements positioned absolutely over the Three.js canvas in the headless browser, or composited as a separate pass. HUD layers are always at a fixed position relative to the viewport.

### Virtualized Clock
The engine's mechanism for deterministic frame-by-frame rendering. Instead of relying on `requestAnimationFrame` or wall-clock time, the engine tells the Three.js scene exactly which frame (and therefore which timestamp) to render, waits for the WebGL draw to complete, captures the pixel buffer, and only then advances to the next frame. This ensures zero dropped frames regardless of scene complexity or hardware speed.

### Director Agent
A Vision-capable LLM (e.g., Claude with vision, GPT-4o) used **exclusively during the harness development phase** to review short test renders and provide directional visual feedback. The Director Agent can see rendered frames/video that the Code Agent (Explorer) cannot. It operates under a strict Human-in-the-Loop circuit breaker — its critiques are recommendations, never direct code changes, and must be approved by a human before the Code Agent acts on them. The Director Agent is never part of the production pipeline; it exists only to tune the spatial presets during development.

### Visual Critique
A structured feedback document produced by the Director Agent after reviewing a test render. Contains timestamped, directional observations about camera motion, depth placement, edge reveals, and overall cinematic quality. A Visual Critique is explicitly labeled "Recommended Tweaks" and requires human sign-off before it enters the Code Agent's context.

### HITL Circuit Breaker
The Human-in-the-Loop approval gate between the Director Agent's visual feedback and the Code Agent's implementation. Prevents subjective hallucination loops where two AI agents endlessly adjust parameters based on compounding non-grounded opinions. The human reviews, modifies, and explicitly approves each round of feedback. The convergence loop only closes when the human is satisfied with the render.

### AssetLibrary
The Supabase (PostgreSQL + pgvector) table that serves as the semantic cache for generated image assets. Each row stores a prompt, its vector embedding, the slot type it was generated for, and a URL to the cached image file in R2/S3. Queried by cosine similarity before every image generation call to avoid redundant API spending and to maintain visual consistency across videos.

### Threshold Gate
The cosine similarity cutoff (default: 0.92) that determines whether a cached image is "close enough" to a new prompt to be reused. Above the threshold: cache hit, skip generation. Below: cache miss, generate new image and cache it. The threshold is tuned during the harness phase and may differ by slot type (backgrounds may tolerate lower thresholds than subjects).

---

## Section 3: Constraints

These are non-negotiable unless formally revised through the harness review process.

### C-01: Zero-License Node.js Application
The engine must be a **custom, zero-license Node.js application**. It must not depend on any third-party video framework that carries licensing fees, usage restrictions, or commercial tier requirements (e.g., Remotion, Creatomate, Shotstack). The only allowed media-pipeline dependencies are:
- **`three`** — Three.js for WebGL 3D scene rendering. MIT licensed.
- **`puppeteer`** (or `playwright`) — for headless Chromium control and frame capture. Apache-2.0 licensed.
- **`ffmpeg-static`** — for a bundled FFmpeg binary, OR FFmpeg installed on the host machine. LGPL/GPL licensed (linking via stdio is permitted).
- Standard npm utilities (e.g., `zod` for validation, `commander` for CLI) are allowed.

React and `@react-three/fiber` are permitted as optional developer ergonomics for authoring scene components, but the engine must not require a React runtime for rendering. If React is used, it runs inside the headless browser page, not as a framework dependency of the rendering pipeline itself.

### C-02: Puppeteer + Three.js + FFmpeg Pipeline
The engine must use **Puppeteer** (or Playwright) to load a Three.js WebGL canvas in headless Chromium, **deterministically step through frames** using a virtualized clock, extract the pixel buffers (via `canvas.toDataURL()`, `canvas.toBlob()`, or the CDP `Page.captureScreenshot` protocol), and **pipe them directly into FFmpeg via stdio** to encode the final MP4. This is the complete rendering pipeline. There is no intermediate video framework.

### C-03: Deterministic Virtualized Timing
The engine must **not** rely on real-time playback for frame capture. It must use a **virtualized clock** that forces Three.js to render exact timestamps frame-by-frame. The render loop must be:
1. Set the scene state to frame `N` (camera position, plane positions, opacity, etc.) based on the computed timestamp `t = N / fps`.
2. Call `renderer.render(scene, camera)` to draw the frame.
3. Wait for the WebGL draw call to complete.
4. Capture the pixel buffer from the canvas.
5. Pipe the buffer to FFmpeg.
6. Advance to frame `N + 1`.

This ensures that complex 3D scenes, heavy post-processing (like depth of field), or slow hardware never cause dropped frames. Every frame is rendered to completion before the next begins. The output is identical regardless of the machine's real-time rendering speed.

### C-04: Resolution and Frame Rate
Must support at minimum: 1920×1080 (16:9 landscape) and 1080×1920 (9:16 portrait) at 24fps and 30fps. The architecture should not preclude other resolutions or frame rates, but these four combinations are the baseline.

### C-05: Deterministic Output
The same manifest + the same input images + the same audio file must produce byte-identical (or visually indistinguishable) output every time. No randomness in the rendering path unless explicitly seeded.

### C-06: Blind-Authorable
An LLM with no visual perception must be able to author a manifest that produces a visually correct video, by selecting from the spatial authoring vocabulary (layout templates, camera presets, depth model). This means:
- Layout templates must have been validated to produce correct spatial relationships for their intended use case.
- Camera motion presets must have been validated to not reveal edges given their associated depth model.
- The manifest schema must reject invalid combinations at validation time, before rendering begins.

### C-07: Audio Synchronization
The engine must accept an audio file (WAV or MP3) and synchronize total video duration to audio duration. Additionally, the manifest must support timestamp-based scene boundaries aligned to narration cues (e.g., "scene 2 starts at 12.5 seconds when the narrator begins discussing the ocean floor").

### C-08: Render Performance
A 60-second video at 1920×1080, 30fps (1,800 frames), with 5 textured planes per scene, must render in under 15 minutes on a standard 4-core VPS with at least 4GB RAM (e.g., a $20/month DigitalOcean droplet or equivalent). The Puppeteer + Three.js pipeline renders each frame deterministically and captures via CDP, which is slower per-frame than raw image compositing but produces correct perspective projection without manual matrix math. For scaled production, the rendering can be parallelized by splitting the frame range across multiple Puppeteer instances (each rendering a chunk of frames to a separate FFmpeg process, then concatenating). The 15-minute target is for single-instance rendering only.

### C-09: Image Format Tolerance
The engine must handle input images with and without alpha channels (transparency). For images without transparency that are used as foreground layers, the engine must support a configurable solid-color or blurred background fill, or the author must be warned that the layer will have hard rectangular edges.

### C-10: Manifest Validation
Before rendering begins, the engine must validate the manifest against the schema and report all errors with actionable messages. Invalid manifests must never produce partial output — fail fast, fail clearly.

### C-11: Software Rendering Baseline
The engine must render correctly using headless Chromium with software-based WebGL (SwiftShader/ANGLE, which Puppeteer uses by default with `--disable-gpu`). GPU acceleration is beneficial for render speed but must not be required for correctness. This ensures the engine can run in Docker containers and CI/CD pipelines without GPU passthrough. When a GPU is available, the Puppeteer launch flags should be configured to use it for faster rendering.

---

## Section 4: Directional Sketch

These are hunches and intuitions — informed starting points, not mandates. Explorer sessions are explicitly invited to deviate if exploration reveals a better path.

### 4.1: The Depth Model — Z-Axis Placement

In the Three.js coordinate system, the camera defaults to looking down the negative Z-axis. Planes placed at more negative Z values are farther from the camera. The depth model maps semantic slot names to **Z positions** in world units:

| Slot Name      | Z Position | Typical Content                         | Notes                                |
|----------------|------------|-----------------------------------------|--------------------------------------|
| `sky`          | -50        | Sky, space, distant gradient            | Large plane, fills background        |
| `back_wall`    | -30        | Distant landscape, city skyline         | May be rotated for perspective       |
| `midground`    | -15        | Buildings, terrain, environmental props | Can be floor/wall/ceiling plane      |
| `subject`      | -5         | Primary subject (person, object, animal)| Upright plane facing camera          |
| `near_fg`      | -1         | Foreground foliage, particles, frame    | Close to camera, may be partially off-screen |

These Z values are defaults. Different scene geometries will override them — a tunnel geometry spaces planes very differently from a stage geometry. The key insight is that **the perspective camera's projection matrix handles all parallax, foreshortening, and depth perception natively**. We do not compute parallax factors. We place planes in 3D space and let WebGL do the math.

Whether 5 slots is optimal for the 3D model, or whether scene geometries should define their own slot sets (e.g., a tunnel needs `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall` — 5 slots but different ones), is a question for exploration.

### 4.2: Scene Geometries (formerly Layout Templates)

Scene geometries define the **3D spatial structure** of a scene. Each geometry is a React component that accepts image textures and maps them onto positioned/rotated planes. The library should probably start with **6-8 core geometries**:

- **`stage`** — The default. A large backdrop plane at `z=-30`, a floor plane angled down from the camera, and a subject plane at `z=-5`. Camera pushes in or drifts laterally. Classic "subject in front of a background" setup, but with real perspective on the floor.

- **`tunnel`** — Floor plane (`rotation=[-π/2, 0, 0]`), ceiling plane (`rotation=[π/2, 0, 0]`), left wall (`rotation=[0, π/2, 0]`), right wall (`rotation=[0, -π/2, 0]`), and an end wall at deep Z. Camera pushes forward on Z-axis. Walls undergo real perspective distortion — receding to a vanishing point. This is the effect that Sharp cannot do.

- **`canyon`** — Tall wall planes on left and right, a floor plane, open sky above. Camera pushes forward or floats upward. Good for narrow dramatic spaces.

- **`flyover`** — Large ground plane below (`rotation=[-π/2, 0, 0]`), sky plane above, optional landmark planes rising from the ground. Camera moves forward and slightly downward-looking. Aerial/bird's-eye feel.

- **`diorama`** — A semicircle of planes arranged at varying Z-depths, like layers of a paper theater. Camera pushes in gently. This is the closest to traditional parallax but with real perspective foreshortening on the outer planes.

- **`portal`** — Concentric frames/planes at increasing Z-depth, creating a "looking through layers" effect. Camera pushes through them. Good for transitions or dreamlike sequences.

- **`panorama`** — A very wide backdrop plane (or curved set of planes approximating a cylinder). Camera rotates (pans) rather than translates. No foreground elements. Pure environment.

- **`close_up`** — Subject plane fills most of the view at shallow Z. Minimal background visible. Very subtle camera motion (slight drift or breathing zoom via FOV animation).

Each geometry is a React component with a signature like:
```jsx
<TunnelGeometry
  floor="./images/floor.png"
  ceiling="./images/ceiling.png"
  leftWall="./images/left.png"
  rightWall="./images/right.png"
  endWall="./images/end.png"
  cameraPath="tunnel_push_forward"
/>
```

The LLM author selects a geometry name and maps images to its named slots. The geometry component handles all 3D positioning, rotation, and plane sizing internally.

### 4.3: Camera Path Presets

Camera paths are now **3D trajectories** — the camera moves through space, not just across a 2D plane. Each preset defines `position(t)` and `lookAt(t)` as functions of normalized time, implemented using the engine's built-in `interpolate()` and easing functions.

The library should probably include:

- **`static`** — Camera at fixed position and orientation. No movement.
- **`slow_push_forward`** — Camera moves from `z=5` to `z=0` (or similar). Creates the "moving into the scene" effect. The defining motion for 2.5D projection.
- **`slow_pull_back`** — Reverse of push forward. Reveals the scene.
- **`lateral_track_left`** — Camera translates along X-axis, looking slightly ahead. Cinematic tracking shot.
- **`lateral_track_right`** — Mirror of above.
- **`tunnel_push_forward`** — Camera pushes deep into Z-space, specifically tuned for tunnel geometry with appropriate near/far planes and speed.
- **`flyover_glide`** — Camera moves forward on Z while positioned above the ground plane, looking slightly down. Bird's-eye movement.
- **`gentle_float`** — Very slow, subtle movement in all three axes. Almost subliminal. Good for ambient scenes.
- **`dramatic_push`** — Faster forward push with ease-out. For emphasis moments.
- **`crane_up`** — Camera rises on Y-axis while keeping the lookAt target steady. Reveals vertical space.
- **`dolly_zoom`** — Camera moves forward while FOV widens (or vice versa). The Hitchcock/Spielberg "vertigo" effect. Dramatic but use sparingly.

Each preset carries metadata:
- `start_position`, `end_position`: `[x, y, z]` vectors.
- `start_lookAt`, `end_lookAt`: `[x, y, z]` vectors.
- `fov_start`, `fov_end`: Field of view animation (if applicable).
- `compatible_geometries`: Which scene geometries this path works with (a tunnel_push doesn't make sense on a stage geometry).

### 4.4: The Rendering Stack

The rendering pipeline has three layers, each with a single responsibility:

**Three.js** handles the 3D scene: `THREE.Scene`, `THREE.PerspectiveCamera`, `THREE.Mesh` planes with `THREE.PlaneGeometry`, texture loading via `THREE.TextureLoader`, and all matrix transforms. Three.js runs inside a headless Chromium page loaded by Puppeteer.

**Puppeteer** handles deterministic frame capture: it loads an HTML page containing the Three.js scene, communicates frame numbers to the page via `page.evaluate()` or a message protocol, waits for each frame to render, and captures the canvas pixel buffer via the Chrome DevTools Protocol (`Page.captureScreenshot` or `canvas.toDataURL()`).

**FFmpeg** handles encoding: Puppeteer pipes raw frame data (PNG or raw RGBA buffers) into an FFmpeg child process via stdio. FFmpeg encodes the stream to H.264 MP4 and muxes in the audio track.

The frame rendering pipeline:
1. The Node.js orchestrator spawns Puppeteer and an FFmpeg child process.
2. Puppeteer loads the Three.js scene page with all textures pre-loaded.
3. For each frame `N` from 0 to `totalFrames - 1`:
   a. The orchestrator sends `{ frame: N, fps: 30, totalFrames: 1800 }` to the page.
   b. The page computes normalized time `t = N / totalFrames` (or per-scene t).
   c. The page sets camera position/lookAt by interpolating the active camera path preset to `t`.
   d. The page calls `renderer.render(scene, camera)`.
   e. The page signals "frame ready."
   f. Puppeteer captures the canvas pixels via CDP.
   g. The pixel buffer is written to FFmpeg's stdin.
4. After all frames, FFmpeg's stdin is closed; FFmpeg finalizes the MP4.
5. Audio is muxed in a final FFmpeg pass (or in the same pass via a separate input stream).

**The key invariant:** The page never advances time on its own. The orchestrator controls the clock. This is the virtualized timing model from C-03.

### 4.5: Project Structure

```
depthkit/
├── src/
│   ├── cli.ts                      # CLI entry point (commander)
│   ├── engine/
│   │   ├── orchestrator.ts         # Main render loop: Puppeteer + FFmpeg coordination
│   │   ├── puppeteer-bridge.ts     # Puppeteer launch, page load, frame capture
│   │   ├── ffmpeg-encoder.ts       # FFmpeg child process, stdin piping, audio mux
│   │   └── frame-clock.ts          # Virtualized clock: frame → timestamp mapping
│   ├── scenes/
│   │   ├── scene-sequencer.ts      # Routes manifest scenes to geometries, handles transitions
│   │   ├── geometries/
│   │   │   ├── stage.ts            # "stage" scene geometry definition
│   │   │   ├── tunnel.ts           # "tunnel" scene geometry definition
│   │   │   ├── canyon.ts           # ...etc
│   │   │   └── index.ts
│   │   └── cameras/
│   │       ├── path-presets.ts     # All camera path definitions
│   │       └── interpolate.ts     # Easing functions and interpolation utilities
│   ├── manifest/
│   │   ├── schema.ts               # Zod schema for manifest validation
│   │   └── loader.ts               # Manifest parser and validator
│   └── page/                       # Files served to headless Chromium
│       ├── index.html              # Minimal HTML shell with canvas
│       ├── scene-renderer.js       # Three.js scene setup, texture loading, render loop
│       ├── geometry-library.js     # All geometry definitions (Three.js side)
│       └── message-handler.js      # Receives frame commands from Puppeteer
├── assets/                         # Per-video generated images and audio
│   ├── images/
│   └── audio/
├── package.json
└── tsconfig.json
```

Note the split architecture: `src/engine/` runs in Node.js (orchestrator, Puppeteer control, FFmpeg encoding), while `src/page/` runs inside headless Chromium (Three.js rendering, texture management, frame-by-frame scene state). Communication between them is via Puppeteer's `page.evaluate()` or the CDP message protocol.

### 4.6: Manifest Schema

The manifest should be validated with Zod. The key change from v1: instead of specifying `layout` + `depth_slot` layers, the author specifies `geometry` + named image slots defined by that geometry:

```json
{
  "version": "3.0",
  "composition": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "audio": {
      "src": "./audio/narration.mp3",
      "volume": 1.0
    }
  },
  "scenes": [
    {
      "id": "scene_001",
      "duration": 8.5,
      "start_time": 0,
      "geometry": "tunnel",
      "camera": "tunnel_push_forward",
      "camera_params": {
        "speed": 1.0,
        "easing": "ease_in_out"
      },
      "transition_in": { "type": "crossfade", "duration": 1.0 },
      "transition_out": { "type": "dip_to_black", "duration": 0.5 },
      "planes": {
        "floor": { "src": "./images/scene1_floor.png" },
        "ceiling": { "src": "./images/scene1_ceiling.png" },
        "left_wall": { "src": "./images/scene1_left.png" },
        "right_wall": { "src": "./images/scene1_right.png" },
        "end_wall": { "src": "./images/scene1_end.png" }
      }
    },
    {
      "id": "scene_002",
      "duration": 10.0,
      "start_time": 8.0,
      "geometry": "stage",
      "camera": "slow_push_forward",
      "planes": {
        "backdrop": { "src": "./images/scene2_bg.png" },
        "floor": { "src": "./images/scene2_floor.png" },
        "subject": { "src": "./images/scene2_person.png" }
      }
    }
  ]
}
```

Note that the `planes` keys are defined by the geometry — a `tunnel` expects `floor`, `ceiling`, `left_wall`, `right_wall`, `end_wall`, while a `stage` expects `backdrop`, `floor`, `subject`. The Zod schema validates that the provided planes match the geometry's requirements.

### 4.7: Image Generation Strategy for Flux.1 Schnell

When generating images for the parallax pipeline, prompt engineering is critical. Each depth slot needs a different kind of image:

- **`far_bg`**: Full-scene backgrounds. Prompt for wide, atmospheric images. No foreground elements. "Expansive ocean horizon at sunset, wide angle, no objects in foreground, cinematic"
- **`mid_bg`**: Environmental elements that read as middle-distance. "Mountain range silhouette, slightly hazy, atmospheric perspective"
- **`midground`**: Objects that occupy the middle of the scene. May need transparency. "Coral reef formation, isolated on transparent background" or can be extracted via background removal.
- **`subject`**: The primary focus element. Almost always needs transparency. "Deep sea anglerfish, dramatic lighting, isolated on transparent background, PNG"
- **`near_fg`**: Foreground framing elements. Needs transparency. Often blurred. "Underwater particles and bubbles, scattered, transparent background, bokeh"

The SKILL.md should include a **prompt template library** for each depth slot so the LLM generating manifests also knows how to prompt for the images.

### 4.8: Background Removal

Many image generation models don't reliably produce transparent backgrounds. The engine (or the pipeline around it) should support a background removal step. Options:
- `rembg` (Python, open source, runs on CPU). Could be called as a subprocess.
- Sharp-based chroma key (remove a specific color). Simpler but less robust.
- Accept that `far_bg` and `mid_bg` don't need transparency and only apply removal to `subject` and `near_fg`.

### 4.9: The SKILL.md

The SKILL.md should follow a modular pattern — a primary file that references sub-files loaded based on context. The core SKILL.md would include:
- How to structure a manifest (with a complete, annotated example).
- The layout template reference (one section per template, with a description of what it's for and what parameters it accepts).
- The camera motion reference (one section per preset, with a description of the visual effect and when to use it).
- The depth model reference (the slot names, their factors, and guidance on which content goes in which slot).
- Prompt engineering templates for image generation per depth slot.
- Common patterns (e.g., "how to do a 5-scene explainer video," "how to do a 30-second social media clip").
- Anti-patterns (e.g., "never put text content in a parallax layer — it looks wrong when it moves").

### 4.10: Asset Semantic Caching (Vector RAG)

At scale (100+ videos per day), generating every image asset from scratch for every video becomes prohibitively expensive and introduces visual inconsistency — a "mountain range at sunset" prompt will produce a subtly different mountain range each time, which breaks brand coherence if a creator wants a recurring visual identity across videos.

The pipeline should include a **semantic caching middleware** layer that sits between the manifest's image prompts and the image generation API. Before generating any image, the pipeline embeds the prompt and queries a vector database for visually equivalent cached assets. If a sufficiently similar image already exists, it is reused instead of regenerated.

**Infrastructure:** Supabase (PostgreSQL + `pgvector` extension) for the vector store, with R2/S3 for image file storage. Supabase is chosen because it provides managed PostgreSQL with pgvector, a REST API callable from n8n, and a generous free tier — no additional infrastructure beyond what the pipeline already uses.

**Database Schema — `AssetLibrary` table:**

```sql
CREATE TABLE asset_library (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slot_type       TEXT NOT NULL,          -- e.g., 'sky', 'subject', 'floor', 'left_wall'
  original_prompt TEXT NOT NULL,          -- the exact prompt used to generate this image
  prompt_embedding VECTOR(1536) NOT NULL, -- embedding of the prompt (dimension matches model)
  image_url       TEXT NOT NULL,          -- R2/S3 URL to the cached PNG
  has_alpha       BOOLEAN DEFAULT false,  -- whether background removal was applied
  width           INT,                    -- image dimensions for sizing validation
  height          INT,
  usage_count     INT DEFAULT 1,          -- tracks reuse frequency for analytics
  created_at      TIMESTAMPTZ DEFAULT now(),
  last_used_at    TIMESTAMPTZ DEFAULT now()
);

-- pgvector index for fast similarity search, scoped by slot_type
CREATE INDEX idx_asset_embedding ON asset_library
  USING ivfflat (prompt_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_asset_slot_type ON asset_library (slot_type);
```

**Threshold Gate Logic:**

The caching decision is a simple threshold gate in the n8n pipeline (or in the HTTP endpoint's image retrieval step):

1. **Embed the prompt.** Use a text embedding model (e.g., OpenAI `text-embedding-3-small`, or a self-hosted model) to generate a vector from the image prompt.
2. **Query Supabase.** Search the `AssetLibrary` table for the nearest neighbor, **filtered by `slot_type`** to ensure a cached `sky` image is never returned for a `subject` slot:
   ```sql
   SELECT id, image_url, 1 - (prompt_embedding <=> $1) AS similarity
   FROM asset_library
   WHERE slot_type = $2
   ORDER BY prompt_embedding <=> $1
   LIMIT 1;
   ```
3. **Apply the threshold:**
   - **Cosine similarity > 0.92** → **Cache hit.** Return the cached `image_url`. Increment `usage_count` and update `last_used_at`. Skip image generation entirely.
   - **Cosine similarity ≤ 0.92** → **Cache miss.** Call the Flux.1 Schnell API (or self-hosted endpoint) to generate the image. Apply background removal if needed (rembg for subject/foreground slots). Upload the result to R2/S3. INSERT a new row into `AssetLibrary` with the prompt, embedding, image URL, and slot type.

**Why 0.92?** This threshold should be tuned during the harness phase. Too high (e.g., 0.98) and the cache rarely hits. Too low (e.g., 0.80) and visually dissimilar images get reused, producing jarring mismatches. The 0.92 starting point is a hunch based on typical semantic similarity curves — prompts that are genuinely paraphrases of each other (e.g., "expansive ocean horizon at sunset" vs "wide ocean sunset panorama") tend to land above 0.90 in embedding space, while semantically different prompts (e.g., "ocean sunset" vs "mountain sunrise") fall below 0.85. Explorer sessions should test this threshold empirically.

**Why filter by `slot_type`?** Without this filter, a cached `subject` image (e.g., an isolated anglerfish) could be returned as a match for a `sky` prompt about deep blue ocean. The slot type filter ensures that cached assets are only reused in geometrically compatible contexts — a floor image for a floor slot, a sky for a sky.

**Cost impact:** At steady state with a well-populated cache, the pipeline could see 30-60% cache hit rates for common scene types (nature backgrounds, sky panoramas, standard environmental textures). At $0.003/image from Replicate, a 50% hit rate on 20 images per minute of video saves ~$0.03/minute — a ~35% reduction in image generation cost. The embedding query cost is negligible (a fraction of a cent per query).

**Consistency benefit:** When a creator establishes a visual style (e.g., "all backgrounds should be painterly watercolor sunsets"), the cache naturally converges on a consistent set of reused assets, creating visual coherence across videos without explicit style management.

---

## Section 5: Testable Claims

These are specific assertions that exploration sessions should verify or refute. Each may become an objective in the progress map.

### TC-01: Five planes per scene geometry are sufficient
A scene geometry with 3-5 textured planes handles at least 90% of common YouTube/social media video scene types without feeling flat or artificial. Test by defining 15 diverse scene types and checking whether the proposed geometries can accommodate all of them.

### TC-02: Puppeteer + Three.js render performance
The Puppeteer + Three.js pipeline can render a 5-plane 3D scene at 1920×1080 and capture the frame in under 500ms per frame using software WebGL (no GPU). This would yield a 60-second, 30fps video in under 15 minutes. Test on a 4-core VPS with 4GB+ RAM. If software rendering is too slow, document the threshold where GPU acceleration becomes necessary.

### TC-03: Perspective projection produces convincing 2.5D
When images are mapped onto planes positioned in 3D space and the camera pushes forward on the Z-axis, the resulting perspective distortion (foreshortening, vanishing points, skewing of wall/floor planes) produces a convincingly immersive 2.5D effect that is visually distinguishable from (and superior to) flat 2D side-scrolling parallax. Test by rendering the same scene with both approaches and requesting human evaluation.

### TC-04: Scene geometries eliminate manual 3D positioning
An LLM can produce a valid manifest using only geometry names and plane slot keys — without ever specifying XYZ coordinates, rotations, or matrix transforms — and the resulting video has correct spatial relationships. Test by having an LLM author 10 different manifests and checking each for spatial correctness.

### TC-05: The tunnel geometry produces convincing depth
The tunnel geometry (floor, ceiling, left wall, right wall, end wall) with a forward camera push produces a convincing "traveling through a space" effect where walls visibly recede to a vanishing point. Test with various image types and camera speeds.

### TC-06: The virtualized clock produces deterministic output
The same manifest + same images + same audio produces visually identical output across multiple render runs on the same hardware, confirming that the virtualized clock eliminates all timing-dependent variation. Test by rendering the same composition 3 times and comparing frame checksums.

### TC-07: Manifest validation catches common authoring errors
The Zod schema validation catches at least the following errors before rendering begins: planes that don't match the geometry's expected slots, geometry names that don't exist, camera paths incompatible with the chosen geometry, negative durations, overlapping scene timecodes, and resolution mismatches. Test by submitting 20 deliberately broken manifests and verifying that each produces a clear error message.

### TC-08: Eight scene geometries cover the design space
The proposed 8 scene geometries (stage, tunnel, canyon, flyover, diorama, portal, panorama, close_up) can accommodate at least 20 out of 25 randomly selected video topics without the LLM needing to specify raw 3D coordinates. Test by generating a list of 25 diverse topics and attempting to map each to a geometry.

### TC-09: Eased camera paths feel more natural than linear
Camera paths with ease-in-out timing functions are consistently preferred over linear interpolation in human evaluation. Document the reasoning.

### TC-10: Cross-scene transitions mask compositing seams
A 0.5-1.0 second crossfade between scenes (implemented by the scene sequencer rendering both scenes simultaneously with animated opacity) is sufficient to mask any visible artifacts at scene boundaries. Test by rendering transitions with and without crossfade and inspecting the boundary frames.

### TC-11: The engine runs in a Docker container with software WebGL
The engine, including all dependencies (Three.js, Puppeteer, Chromium, FFmpeg), can be installed and run in a Docker container without GPU passthrough, using software WebGL rendering (SwiftShader), and meets the performance requirements in C-08.

### TC-12: Background removal via rembg is viable as a subprocess
Calling rembg as a Python subprocess from Node.js adds less than 5 seconds per image and produces acceptable masks for subject isolation. If rembg is too slow or produces poor masks, document the failure and propose an alternative.

### TC-13: Audio duration drives total video length
When an audio file is provided, the engine automatically distributes scene durations proportionally to fill exactly the audio duration, unless explicit timestamps override. Test by providing a 45-second audio file and a 5-scene manifest with no explicit timecodes, and verifying the output is exactly 45 seconds.

### TC-14: FOV animation produces useful dramatic effects
Animating the camera's field of view during a scene (e.g., narrowing from 60° to 40° during a push-in) produces a visually distinct and useful cinematic effect (dolly zoom / vertigo effect). Test whether this is worth including in V1 or deferring.

### TC-15: The Director Agent workflow converges in ≤5 iterations
For a given scene geometry + camera path combination, the Director Agent → HITL → Code Agent loop reaches "no Priority 1 issues" within 5 or fewer iterations. If it consistently takes more, the feedback format or the geometry's parameterization needs restructuring. Test on at least 3 different geometries.

### TC-16: Director-tuned presets outperform blind-authored presets
Scene geometries and camera paths that have been through the Director Agent tuning workflow produce renders that a human evaluator consistently rates higher (on a 1-5 cinematic quality scale) than the same geometries with parameters set purely by the Code Agent's mathematical reasoning. This validates that the Director Agent workflow adds real value and isn't just ceremony.

### TC-17: The 0.92 cosine similarity threshold produces acceptable cache reuse
At the default threshold of 0.92, cached images returned for semantically similar prompts are visually acceptable substitutes at least 90% of the time (as judged by human review of 50+ cache hit pairs). If the threshold is too low (too many visually mismatched hits) or too high (too few hits), document the failure and propose a revised threshold.

### TC-18: Slot-type filtering prevents cross-category cache contamination
When the AssetLibrary query filters by `slot_type`, a cached `subject` image is never returned for a `sky` prompt, even if the embeddings are superficially similar (e.g., "blue whale" as a subject vs "blue sky" as a background). Test by inserting deliberately confusable prompts across different slot types and verifying that the filter prevents cross-contamination in all cases.

### TC-19: Cache hit rates reach 30-60% at steady state
After populating the AssetLibrary with assets from 50+ videos across diverse topics, the cache hit rate for common scene types (nature backgrounds, sky panoramas, standard environmental textures) reaches at least 30%. Test by running 20 new video manifests through the caching pipeline and measuring the ratio of cache hits to total image requests.

### TC-20: Embedding + query latency is negligible relative to generation
The full cache lookup cycle (embed prompt → query Supabase → return result) completes in under 500ms per image, which is negligible relative to the 2-5 seconds per image for Flux.1 Schnell generation. Test by benchmarking 100 sequential cache queries against Supabase.

---

## Section 6: Success Criteria

The harness has converged successfully when all of the following are true:

### SC-01: End-to-End Rendering
A manifest describing a 60-second, 5-scene video with narration audio, using only layout templates and camera presets (no manual coordinates), renders to a valid MP4 file that plays correctly in VLC and web browsers.

### SC-02: Blind Authoring Validation
An LLM (Claude) authors 5 different manifests for 5 different topics (e.g., deep sea creatures, space exploration, ancient Rome, cooking basics, jazz history) using only the SKILL.md as reference. All 5 render successfully. A human reviewer confirms that the spatial relationships in at least 4 out of 5 look correct and professional.

### SC-03: Performance Target Met
The 60-second benchmark video renders in under 15 minutes on a 4-core, 4GB+ RAM machine using software WebGL. With GPU acceleration or parallelized multi-instance rendering, it should render in under 3 minutes.

### SC-04: SKILL.md Is Self-Sufficient
An LLM that has never seen the engine's source code can, using only the SKILL.md, produce a valid manifest for an arbitrary topic. The SKILL.md is a single document (or a primary document with modular sub-files) that fits within a single context window.

### SC-05: n8n Integration Works
A simple n8n workflow can POST a topic and desired duration to an HTTP endpoint, receive a job ID, poll for completion, and download the resulting MP4. The endpoint handles: manifest generation (via Claude API), image generation (via Flux.1 Schnell), narration generation (via Chatterbox TTS), and rendering (via depthkit).

### SC-06: Manifest Validation Is Comprehensive
No manifest that passes validation produces a rendering error. No manifest that fails validation is a valid video description.

### SC-07: All Core Scene Geometries Are Visually Tuned
Every scene geometry and its default camera path preset has been through at least one complete Director Agent → HITL → Code Agent tuning cycle, and has been signed off by the human as cinematically acceptable. The progress map shows `"visual_status": "tuned"` for all core geometries before the engine is considered production-ready.

---

## Section 7: Anti-Patterns

The harness must actively avoid these.

### AP-01: Do Not Build a General-Purpose Video Editor
Depthkit renders 2D images mapped onto 3D planes with perspective camera projection. It does not do skeletal animation, physics simulation, dynamic lighting, real-time shadows, or arbitrary 3D model rendering. Three.js is powerful enough to do all of those things — depthkit intentionally does not. If a feature doesn't serve the 2.5D camera projection use case, it doesn't belong.

### AP-02: Do Not Bypass the Puppeteer Frame Loop
All frame rendering must go through the orchestrator's virtualized clock → Puppeteer → Three.js → FFmpeg pipeline. Do not attempt to use `requestAnimationFrame` for timing, do not render frames asynchronously without waiting for completion, do not write frames to disk when piping to FFmpeg would suffice (except in debug mode). The deterministic frame loop is the engine's correctness guarantee.

### AP-03: Do Not Require Manual Coordinate Entry
If the LLM has to specify pixel coordinates to produce a correct scene, the abstraction layer has failed. The layout templates and depth model exist to prevent this. Manual coordinates should be an escape hatch for edge cases, never the primary authoring method.

### AP-04: Do Not Conflate Rendering with Asset Generation
The rendering engine accepts a manifest and pre-existing image/audio files. It does not generate images, run AI models, or call external APIs. Asset generation (Flux.1, ElevenLabs, background removal) is a separate pipeline stage that produces the inputs the engine consumes. Keep these concerns cleanly separated.

### AP-05: Do Not Optimize Prematurely
The first version should prioritize correctness and authorability over render speed. If compositing takes 500ms per frame instead of 200ms, that's a 15-minute render instead of a 6-minute render — acceptable for V1. Performance optimization is a later objective.

### AP-06: Do Not Invent New Terminology
Use the vocabulary defined in this seed. If a new concept genuinely needs a name, propose it through the review process. Silently introducing synonyms (e.g., calling layers "planes" or depth slots "z-levels") causes cross-session confusion and is the most common form of drift in multi-agent collaboration.

### AP-07: Do Not Put Text in Parallax Layers
Text that moves with parallax looks wrong to humans — our visual system expects text to be anchored to the screen, not to a 3D scene. If text is needed (titles, captions, subtitles), it should be composited as a HUD layer at parallax factor 0.0 (pinned to viewport) or rendered as a post-processing step. Never place text in a scene layer with depth > 0.

### AP-08: Do Not Hard-Code the Depth Model
The Z-positions and rotations for each plane slot should be configurable per-composition or per-scene, with the geometry's defaults as the starting point. Some scenes may want compressed Z-ranges (tight, intimate spaces); others may want stretched ranges (vast landscapes). The defaults should be good enough for 90% of cases, but the engine must not break if they're overridden via `position_override` in the manifest.

### AP-09: Do Not Let the Director Agent Bypass the Human
The Director Agent's critiques are recommendations, never directives. The Code Agent must never receive unfiltered Director Agent output. If the orchestration layer is automated, it must gate Director feedback behind an explicit human approval step. Removing the HITL circuit breaker — even temporarily for "faster iteration" — risks subjective hallucination loops where two AI agents chase each other's aesthetic preferences into increasingly bizarre parameter space. The human grounds the loop.

### AP-10: Do Not Use the Director Agent in Production
The Director Agent exists to tune presets during development. It must never be part of the production rendering pipeline, the n8n workflow, or any runtime path. If a production video looks wrong, the fix is to re-tune the preset through the harness (with the Director), not to add a runtime Director check. The entire point of the preset library is that it was tuned once and works blindly forever after.

---

## Section 8: 3D Spatial Foundations

This section provides the core spatial logic that explorer sessions will implement and verify. The fundamental shift from v1: **we do not compute parallax, perspective, or foreshortening manually.** WebGL's perspective projection matrix does all of this natively. Our job is to place planes and cameras correctly in 3D space and let the GPU (or software renderer) handle the math.

### 8.1: Coordinate System

Three.js uses a right-handed coordinate system:
- **X-axis**: positive = right, negative = left.
- **Y-axis**: positive = up, negative = down.
- **Z-axis**: positive = toward the viewer, negative = into the scene.

The camera defaults to position `[0, 0, 5]` looking toward `[0, 0, 0]`. Planes placed at more negative Z values are farther away.

### 8.2: Perspective Camera Configuration

The `<PerspectiveCamera>` is configured with:
- **FOV** (field of view): Vertical angle in degrees. Default: 50°.
- **Aspect ratio**: `width / height` of the composition (e.g., 1920/1080 = 1.778 for 16:9).
- **Near plane**: Minimum render distance. Default: 0.1 units.
- **Far plane**: Maximum render distance. Default: 100 units.

```jsx
<PerspectiveCamera
  makeDefault
  fov={50}
  position={[camX(t), camY(t), camZ(t)]}
  near={0.1}
  far={100}
/>
```

The perspective matrix automatically handles:
- Objects farther from the camera appear smaller.
- Parallel lines converge to vanishing points.
- Planes angled relative to the camera undergo perspective distortion (keystone/trapezoid).
- Objects outside the frustum are clipped.

### 8.3: Plane Sizing in 3D Space

A `<planeGeometry>` with `args={[width, height]}` creates a flat rectangle in world units. To ensure a plane fills the camera's view at a given Z distance, the visible area at distance `d` from the camera is:

```
visible_height = 2 × d × tan(FOV / 2)
visible_width = visible_height × aspect_ratio
```

For FOV=50° and distance d=30 (a backdrop at z=-25 with camera at z=5):
```
visible_height = 2 × 30 × tan(25°) ≈ 27.98 units
visible_width = 27.98 × 1.778 ≈ 49.74 units
```

Planes should be sized **larger than the visible area** to prevent edge reveal during camera motion. The oversizing factor depends on how much the camera moves — each camera path preset should define the required oversizing per plane.

### 8.4: Plane Rotation for Scene Geometries

Planes default to facing the camera (normal along positive Z). To create floors, ceilings, and walls, they are rotated:

- **Floor**: `rotation={[-Math.PI / 2, 0, 0]}` — lies flat, facing up.
- **Ceiling**: `rotation={[Math.PI / 2, 0, 0]}` — lies flat, facing down.
- **Left wall**: `rotation={[0, Math.PI / 2, 0]}` — faces right.
- **Right wall**: `rotation={[0, -Math.PI / 2, 0]}` — faces left.
- **Backdrop**: `rotation={[0, 0, 0]}` — faces camera (default).

For the **tunnel geometry**, this creates a box-like space:
```jsx
{/* Floor */}
<mesh position={[0, -2, -15]} rotation={[-Math.PI/2, 0, 0]}>
  <planeGeometry args={[8, 30]} />
  <meshBasicMaterial map={floorTexture} />
</mesh>

{/* Left wall */}
<mesh position={[-4, 0, -15]} rotation={[0, Math.PI/2, 0]}>
  <planeGeometry args={[30, 4]} />
  <meshBasicMaterial map={leftWallTexture} />
</mesh>

{/* End wall (far) */}
<mesh position={[0, 0, -30]}>
  <planeGeometry args={[8, 4]} />
  <meshBasicMaterial map={endWallTexture} />
</mesh>
```

As the camera pushes forward (Z decreases), the walls, floor, and ceiling undergo natural perspective distortion — receding to the vanishing point. This is the core 2.5D projection effect.

### 8.5: Camera Path Interpolation

Camera positions are interpolated using the engine's built-in `interpolate()` utility. The orchestrator passes the current frame number and total frame count to the Three.js page, which computes normalized time and applies easing:

```javascript
// Inside the Three.js page (src/page/scene-renderer.js)

function interpolate(frame, inputRange, outputRange, easing = linear) {
  const t = (frame - inputRange[0]) / (inputRange[1] - inputRange[0]);
  const clamped = Math.max(0, Math.min(1, t));
  const eased = easing(clamped);
  return outputRange[0] + (outputRange[1] - outputRange[0]) * eased;
}

// Called by the message handler when the orchestrator sends a frame command
function renderFrame(frame, totalFrames) {
  const camZ = interpolate(
    frame,
    [0, totalFrames],
    [5, -20],                    // Camera pushes from z=5 to z=-20
    easings.easeInOut
  );

  const camY = interpolate(
    frame,
    [0, totalFrames],
    [0, 0.5],                    // Slight upward drift
    easings.easeInOutCubic
  );

  camera.position.set(0, camY, camZ);
  camera.lookAt(0, 0, -30);
  renderer.render(scene, camera);
}
```

For spring-based camera motions (organic, bouncy feel), the engine provides a `spring()` utility:
```javascript
function spring(frame, fps, config = { damping: 200, mass: 0.5, stiffness: 10 }) {
  // Compute spring physics at the given frame
  const t = frame / fps;
  const { damping, mass, stiffness } = config;
  const omega = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));
  // Critically/over-damped spring response
  if (zeta >= 1) {
    return 1 - Math.exp(-omega * t) * (1 + omega * t);
  }
  const omegaD = omega * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * omega * t) * Math.cos(omegaD * t);
}

const springValue = spring(frame, fps, { damping: 200, mass: 0.5, stiffness: 10 });
const camZ = interpolate(springValue, [0, 1], [5, -20], linear);
```

### 8.6: Scene Geometry Spatial Contract

Each scene geometry defines, for each plane slot:

```typescript
interface PlaneSlot {
  position: [number, number, number];   // [x, y, z] in world units
  rotation: [number, number, number];   // [rx, ry, rz] in radians
  size: [number, number];               // [width, height] in world units
  required: boolean;
  description: string;                  // For SKILL.md documentation
}

interface SceneGeometry {
  name: string;
  slots: Record<string, PlaneSlot>;
  compatible_cameras: string[];         // Camera path preset names
  default_camera: string;
  fog?: { color: string; near: number; far: number; }; // Optional depth fog
}
```

Example for the tunnel geometry:
```typescript
const tunnelGeometry: SceneGeometry = {
  name: 'tunnel',
  slots: {
    floor:      { position: [0, -2, -15], rotation: [-Math.PI/2, 0, 0], size: [8, 40], required: true, description: "Ground surface" },
    ceiling:    { position: [0,  2, -15], rotation: [Math.PI/2, 0, 0],  size: [8, 40], required: false, description: "Overhead surface" },
    left_wall:  { position: [-4, 0, -15], rotation: [0, Math.PI/2, 0],  size: [40, 4], required: true, description: "Left boundary" },
    right_wall: { position: [4,  0, -15], rotation: [0, -Math.PI/2, 0], size: [40, 4], required: true, description: "Right boundary" },
    end_wall:   { position: [0,  0, -35], rotation: [0, 0, 0],          size: [8, 4],  required: true, description: "Distant end of tunnel" },
  },
  compatible_cameras: ['tunnel_push_forward', 'static', 'gentle_float'],
  default_camera: 'tunnel_push_forward',
  fog: { color: '#000000', near: 10, far: 40 },
};
```

### 8.7: Scene Timing (unchanged from v1)

Total video duration `T` is determined by:
- If audio is provided and no explicit scene durations: `T = audio_duration`. Scenes share duration proportionally (or equally if no weights are provided).
- If explicit scene durations are provided: `T = sum(scene_durations) + sum(transition_overlaps)`.
- If both audio and explicit durations: explicit durations are used, but the engine warns if `T ≠ audio_duration`.

### 8.8: Transition Overlap (unchanged from v1)

When scene A transitions to scene B with a crossfade of duration `d`:
- For frames in the overlap window, both scenes render simultaneously.
- Scene A's opacity interpolates from 1 to 0; scene B's from 0 to 1.
- Implemented by the scene sequencer: during the overlap window, both scenes' Three.js scene graphs are rendered in sequence to the same canvas, with the outgoing scene's global opacity decreasing and the incoming scene's increasing. The sequencer manages this by rendering scene A, compositing it at reduced opacity, then rendering scene B at complementary opacity, all within a single frame capture cycle.

### 8.9: Texture Loading and Aspect Ratio

Images loaded as Three.js textures retain their native aspect ratio. When mapped onto a plane, the image stretches to fill the plane's geometry. To avoid distortion:
- The plane's width/height ratio should match the image's aspect ratio, OR
- The geometry component should auto-calculate plane dimensions from the loaded texture's dimensions.

The recommended approach: each geometry component loads its textures, reads `texture.image.width` and `texture.image.height`, and adjusts plane sizes accordingly while maintaining the geometry's spatial structure. This means the LLM author never needs to know image dimensions — the engine adapts.

### 8.10: Fog and Atmosphere

Three.js's `<fog>` component provides depth-based fading, which significantly enhances the 2.5D effect:
- Objects farther from the camera fade toward the fog color.
- This hides hard edges on distant planes and creates atmospheric perspective.
- Each scene geometry can define default fog settings that the author can override.

```jsx
<Canvas>
  <fog attach="fog" args={['#000000', 10, 40]} />
  {/* Scene content */}
</Canvas>
```

---

## Section 9: Open Questions for Exploration

These are questions the seed author does not know the answer to. Explorer sessions should address them.

### OQ-01: Should planes support per-frame opacity animation?
Use case: a foreground fog layer that fades in and out, or a subject that materializes. This adds complexity to the manifest schema but could significantly improve visual quality. React Three Fiber makes this trivial (`<meshBasicMaterial opacity={...} transparent />`), so the question is whether the manifest schema and SKILL.md should expose it.

### OQ-02: What's the best strategy for images without alpha?
When Flux.1 generates an image with a white or colored background instead of transparency, what's the most reliable automated approach? Rembg? Chroma key? Color-range selection? Or should we require the image pipeline to handle this before the engine sees the image? In the Three.js context, non-transparent images on subject planes will show rectangular edges — this is more visible in 3D than in flat compositing because the perspective distortion makes the rectangle obvious.

### OQ-03: Should the engine support subtitle/caption overlay?
Narration-synced captions are common in social media videos. With the custom pipeline architecture, captions would be HUD layers — HTML/CSS elements positioned over the Three.js canvas inside headless Chromium, or composited as a separate post-processing step. This is architecturally clean (no 3D involvement), so the question is mainly about scope for V1.

### OQ-04: How should vertical (9:16) video differ from horizontal (16:9)?
Scene geometries need different plane sizes and camera FOV for portrait mode. Do we need parallel geometry variants, or can geometries auto-adapt based on the composition's aspect ratio? A tunnel in portrait mode needs taller walls and a narrower floor.

### OQ-05: Is a browser-based preview mode useful?
The engine could expose a `--preview` flag that serves the Three.js page on localhost with real-time `requestAnimationFrame` playback (as opposed to the deterministic frame-by-frame capture used for rendering). The LLM can't use it, but the human operator could preview camera motions before committing to a full render. Should the SKILL.md instruct the LLM to generate a preview command for the human?

### OQ-06: Should camera paths support composition (chaining)?
E.g., "slow_push_forward for the first half, then lateral_track for the second half." The engine's `interpolate()` utility supports input ranges with multiple segments, making this straightforward. Is it needed for V1?

### OQ-07: What's the minimum viable number of scene geometries?
The directional sketch proposes 8. Could we start with 3-4 and add more in a later version? Which ones would cover the most ground? (`stage` + `tunnel` + `diorama` might be the minimum viable set.)

### OQ-08: Should geometries support dynamic plane count?
E.g., a `stage` geometry that accepts 1-3 background planes at varying Z-depths instead of a fixed single backdrop. This adds flexibility but complicates the slot contract.

### OQ-09: How should lighting be handled?
Currently the directional sketch uses `<meshBasicMaterial>` which is unlit — the texture displays at full brightness regardless of scene lighting. Should geometries support `<ambientLight>` and `<directionalLight>` with `<meshStandardMaterial>` for more atmospheric scenes? This would enable dramatic lighting (e.g., a dark tunnel with a light at the end) but adds complexity.

### OQ-10: Is parallelized multi-instance rendering worth building for V1?
The frame range can be split across multiple Puppeteer instances (each rendering a chunk of frames to a separate FFmpeg process, then concatenating the chunks). A 60-second video that takes 15 minutes on a single instance could render in under 4 minutes across 4 parallel instances on the same machine. Is this worth implementing for the n8n pipeline, or is single-instance rendering sufficient for V1?

---

## Section 10: Director Agent — Visual Tuning Workflow

### 10.1: The Problem

The Code Agent (Claude, the Explorer in the harness) cannot see rendered output. It can author mathematically valid Three.js scenes, but "mathematically valid" and "cinematically compelling" are different problems. A camera push that is technically correct (smooth interpolation, no edge reveals, correct easing) might still feel robotic, too fast, too slow, or poorly framed. Plane Z-depths might produce correct perspective geometry but feel flat or exaggerated. These are subjective, visual-quality problems that require eyes.

The harness needs a mechanism to close the gap between "structurally correct" and "visually polished" during the development phase — when scene geometries and camera path presets are being designed and tuned. This mechanism must not become a runtime dependency: the final production engine must run blindly and flawlessly at scale, using only the presets that were tuned during development.

### 10.2: The Director Agent Role

The **Director Agent** is a Vision-capable LLM (e.g., Claude with vision capabilities, GPT-4o, or any model that can analyze video frames or short clips) that serves as the harness's "eyes" during the development phase. Its role is narrowly scoped:

**What the Director does:**
- Reviews short test renders (under 60 seconds) produced by the Code Agent's current geometry/camera implementations.
- Produces a structured **Visual Critique** with timestamped, directional feedback.
- Identifies visual problems the Code Agent cannot detect: awkward camera motion, unnatural depth spacing, edge reveals, physics that feel robotic rather than organic, incorrect focal emphasis.

**What the Director does NOT do:**
- Write code, modify manifests, or adjust Three.js parameters directly.
- Run during production. The Director Agent is a development tool only.
- Operate without human oversight. Every critique passes through the HITL Circuit Breaker.

### 10.3: The HITL Circuit Breaker

To prevent subjective hallucination loops — where two AI agents endlessly adjust parameters based on compounding non-grounded aesthetic opinions — the Director Agent operates under a strict Human-in-the-Loop constraint:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIRECTOR AGENT WORKFLOW                       │
│                                                                 │
│  1. Code Agent (Explorer) implements or updates a               │
│     scene geometry or camera path preset.                       │
│                                                                 │
│  2. Code Agent renders a short test video                       │
│     (10-30 seconds, using depthkit).                            │
│                                                                 │
│  3. Director Agent (Vision LLM) reviews the render.             │
│     Produces a Visual Critique labeled                          │
│     "RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL"              │
│                                                                 │
│  4. ┌──── HITL CIRCUIT BREAKER ────┐                            │
│     │                              │                            │
│     │  Human reviews the critique. │                            │
│     │  Options:                    │                            │
│     │  a) APPROVE as-is            │                            │
│     │  b) MODIFY and approve       │                            │
│     │  c) REJECT (discard)         │                            │
│     │  d) OVERRIDE with own notes  │                            │
│     │                              │                            │
│     └──────────────────────────────┘                            │
│                                                                 │
│  5. If approved (a or b): Human-approved feedback is            │
│     passed to the Code Agent for implementation.                │
│                                                                 │
│  6. Code Agent adjusts the preset math and re-renders.          │
│                                                                 │
│  7. Loop returns to step 3 until Human is satisfied.            │
│                                                                 │
│  8. CONVERGENCE: Human signs off on the final render.           │
│     The geometry/camera preset is marked as "tuned"             │
│     in the progress map.                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Critical rule:** The Code Agent never receives unfiltered Director Agent output. Every piece of visual feedback passes through the human first. This is not a suggestion — it is a hard constraint of the workflow.

### 10.4: Visual Critique Format

The Director Agent's feedback must follow these guidelines to be maximally useful to a Code Agent that cannot see:

**1. Timestamp everything.** Feedback must be anchored to specific moments in the render, not general impressions.
- "At 00:14 to 00:18, the camera push feels too aggressive."
- NOT: "The camera motion is generally too fast."

**2. Use directional deltas, not absolute values.** The Director empathizes with the Code Agent's blindness. It describes *which direction* a parameter should move, not *what value* it should be. The Code Agent understands its own parameter space better than the Director does.
- "The camera push needs to start slower and end faster — more ease-in on the first third of the motion."
- "The background mountain plane is moving too fast relative to the subject — push it further back on the Z-axis to reduce its apparent parallax."
- NOT: "Change the Bezier control point to 0.8." (The Director doesn't know the Code Agent's interpolation implementation.)
- NOT: "Set z = -45." (The Director should describe the visual problem, not prescribe the coordinate fix.)

**3. Report edge reveals with spatial direction.**
- "At 00:22, the camera panned far enough left that the right edge of the sky plane is visible. Either restrict the camera's X-axis range or scale the sky plane wider."

**4. Describe physics and motion feel.**
- "The crane-up motion feels weightless — like the camera teleports upward. It needs a heavier ease-out to simulate physical mass and deceleration."
- "The tunnel flythrough feels too uniform. The first half should feel like acceleration, the second half like coasting."

**5. Note depth and focus issues.**
- "The depth-of-field blur is hitting the subject instead of the background. The focal distance needs to match the subject plane's Z-position."
- "The foreground particles feel like they're on the same plane as the subject — push them closer to the camera (less negative Z, or positive Z) for clearer depth separation."

**6. Evaluate cinematic quality holistically.**
- "The scene reads as flat — all planes feel equidistant. Exaggerate the Z-spacing between the midground and subject."
- "The transition from scene 2 to scene 3 is jarring — scene 2 ends mid-motion. Let the camera settle before the crossfade."

**7. Use comparative language when possible.**
- "This feels more like a security camera than a dolly shot. A real dolly has slight vertical float — add a subtle Y-axis sine wave to the camera path."
- "The parallax between the floor and walls reads correctly for a tunnel, but the ceiling plane should be the same height as the floor-to-camera distance — right now it feels too low, like a crawlspace."

### 10.5: Visual Critique Template

```markdown
# Visual Critique — [Geometry/Preset Name]
## Status: RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL

**Test Render:** [filename or link]
**Duration:** [X seconds]
**Geometry:** [name]
**Camera Path:** [name]

### Overall Impression
[1-2 sentences on the general quality and feel]

### Timestamped Observations

#### 00:00 – 00:04 (Scene Entry)
- [Observation about opening frame, initial camera position, first impression of depth]

#### 00:05 – 00:12 (Main Motion)
- [Observation about camera movement quality, parallax feel, depth separation]

#### 00:13 – 00:20 (Mid-Scene)
- [Edge reveal issues, plane sizing problems, depth-of-field notes]

#### 00:21 – 00:30 (Scene Exit / Transition)
- [Transition quality, camera settling, exit motion feel]

### Priority Tweaks (Ordered by Impact)
1. **[Highest impact issue]** — [Directional description of fix]
2. **[Second issue]** — [Directional description]
3. **[Third issue]** — [Directional description]

### Things That Work Well (Preserve These)
- [What should NOT be changed — important for preventing regression]
```

### 10.6: Scope Limitation

The Director Agent is invoked **only** for the following objective types in the progress map:

- Tuning a new scene geometry (e.g., "Tune the tunnel geometry for cinematic quality").
- Tuning a new camera path preset (e.g., "Tune tunnel_push_forward for natural motion feel").
- Validating that a geometry + camera combination produces no edge reveals.
- Final visual sign-off on a completed geometry before marking it as "verified" in the progress map.

The Director Agent is **never** invoked for:
- Manifest schema design, Zod validation, or code architecture decisions.
- n8n pipeline integration, audio sync, or transition logic.
- Any production rendering. The Director does not exist in the production pipeline.

### 10.7: Convergence Criteria

A scene geometry or camera path preset is considered "visually tuned" when:

1. The Director Agent's most recent critique contains no Priority 1 (high-impact) issues.
2. The Human has reviewed the final render and explicitly signed off.
3. The Code Agent has committed the tuned parameters with a descriptive message documenting what was adjusted and why.
4. The preset is marked as `"visual_status": "tuned"` in the progress map.

A tuned preset should not be modified unless a subsequent integration review reveals that it conflicts with other tuned presets, or unless the human explicitly requests a revision.

---

## Appendix A: Reference Pipeline (n8n Orchestration)

This is a sketch of the full production pipeline for context. The engine itself only handles step 5.

```
1. USER INPUT
   └─> Topic: "Deep sea creatures"
   └─> Duration: "90 seconds"
   └─> Style: "cinematic documentary"

2. SCRIPT GENERATION (Claude API)
   └─> Input: topic, duration, style
   └─> Output: structured script with scenes, narration text, image prompts per plane, geometry + camera selections

3. NARRATION (Chatterbox TTS — self-hosted or RunPod serverless)
   └─> Input: narration text, voice reference audio, emotion intensity
   └─> Output: audio file (WAV), word-level timestamps

4. ASSET RETRIEVAL & GENERATION (Semantic Caching + Flux.1 Schnell)
   └─> Input: image prompts (from step 2), slot types per plane
   └─> Intercept: Embed each prompt → query Supabase 'AssetLibrary' via pgvector, filtered by slot_type
   └─> Route A (Cosine Similarity > 0.92): Return cached image_url, increment usage_count
   └─> Route B (Cosine Similarity ≤ 0.92): Call Flux.1 API, remove background if needed,
       upload to R2, INSERT new embedding + image_url into AssetLibrary

5. VIDEO RENDERING (depthkit — Puppeteer + Three.js + FFmpeg) ← THIS IS WHAT WE'RE BUILDING
   └─> Input: manifest (from step 2), images (from step 4), audio (from step 3)
   └─> Process: Puppeteer loads Three.js scene, steps through frames via virtualized clock, pipes to FFmpeg
   └─> Output: MP4 video file

6. DELIVERY
   └─> Upload to R2/S3, return URL
```

---

## Appendix B: Session Orientation Checklists

### B.1: All Sessions

Every harness session should begin by confirming:

- [ ] I have read this seed document.
- [ ] I have read the current progress_map.json.
- [ ] I know which objective I am working on.
- [ ] I know what that objective's dependencies are and that they are satisfied.
- [ ] I know the vocabulary and will use it consistently.
- [ ] I know the constraints and will respect them.
- [ ] I will commit a discrete, reviewable artifact before my context fills up.
- [ ] If I discover something that contradicts the seed, I will flag it for review rather than silently deviating.

### B.2: Director Agent Sessions

Before producing a Visual Critique, the Director Agent should confirm:

- [ ] I am reviewing a test render, not production output.
- [ ] My critique will be labeled "RECOMMENDED TWEAKS — REQUIRES HUMAN APPROVAL."
- [ ] I will timestamp every observation to a specific moment in the render.
- [ ] I will use directional deltas ("move further back," "needs more ease-in"), not absolute parameter values.
- [ ] I will not suggest specific code changes, coordinate values, or Bezier control points.
- [ ] I will note what works well (not just what's wrong) to prevent regression.
- [ ] I understand that my feedback will be filtered through a human before the Code Agent sees it.

### B.3: Code Agent Sessions Receiving Director Feedback

When a Code Agent session receives human-approved visual feedback:

- [ ] The feedback has been explicitly approved by the human (not raw Director output).
- [ ] I will translate directional descriptions into parameter adjustments using my knowledge of the codebase.
- [ ] I will re-render a test clip after making adjustments.
- [ ] I will commit changes with a descriptive message referencing the Director feedback round number.
- [ ] I will not adjust parameters that the feedback marked as "working well" unless required to fix a higher-priority issue.
