# Specification: OBJ-049 — Software Rendering Configuration

## Summary

OBJ-049 delivers the `rendering-config` module (`src/engine/rendering-config.ts`) — a utility that resolves the correct *supplementary* Chromium launch arguments for software or hardware-accelerated WebGL rendering, probes the active WebGL backend after launch, and validates that the backend meets depthkit's minimum requirements. This module enforces C-11 (engine must render correctly with software WebGL / SwiftShader, without GPU passthrough) while providing an opt-in path to GPU acceleration when available. It does not own the Puppeteer lifecycle — it produces configuration that `PuppeteerBridge` (OBJ-009) consumes via its existing `gpu` and `extraArgs` config, and provides post-launch validation that `FrameCapture` (OBJ-012) and the orchestrator (OBJ-035) use to confirm rendering correctness.

## Interface Contract

### Module: `src/engine/rendering-config.ts`

```typescript
import type { PuppeteerBridge } from './puppeteer-bridge.js';

/**
 * GPU rendering mode for the engine.
 *
 * - 'software': Force software rendering via SwiftShader/ANGLE.
 *   OBJ-009's gpu:false handles --disable-gpu. OBJ-049 adds
 *   supplementary flags (--use-gl=swiftshader, --disable-gpu-compositing).
 *   Guaranteed to work in Docker/CI without GPU passthrough.
 *   This is the C-11 baseline.
 *
 * - 'hardware': Request hardware GPU acceleration. OBJ-009's
 *   gpu:true omits --disable-gpu. OBJ-049 adds optimization
 *   flags (--enable-gpu-rasterization, etc.). Requires GPU
 *   drivers and (in Docker) GPU passthrough.
 *
 * - 'auto': Launch with hardware flags, probe WebGL. If the
 *   probe detects a software renderer, log the result and
 *   continue — Chromium's implicit SwiftShader fallback is
 *   functionally equivalent. No re-launch. The orchestrator
 *   records which backend it got for logging/diagnostics.
 */
export type GpuMode = 'software' | 'hardware' | 'auto';

/**
 * Information about the active WebGL rendering backend,
 * obtained by probing the launched browser's WebGL context.
 */
export interface WebGLRendererInfo {
  /** The WebGL renderer string from WEBGL_debug_renderer_info.
   *  e.g., "Google SwiftShader", "ANGLE (NVIDIA GeForce RTX 3080 ...)"
   *  null if the extension is unavailable. */
  renderer: string | null;

  /** The WebGL vendor string from WEBGL_debug_renderer_info.
   *  e.g., "Google Inc. (Google)", "Google Inc. (NVIDIA)"
   *  null if the extension is unavailable. */
  vendor: string | null;

  /** WebGL version string from gl.getParameter(gl.VERSION).
   *  e.g., "WebGL 2.0 (OpenGL ES 3.0 SwiftShader 5.0.0)" */
  version: string;

  /** Whether the renderer appears to be software-based.
   *  Detected by checking if the renderer string contains
   *  "SwiftShader", "llvmpipe", or "softpipe" (case-insensitive).
   *  Returns false if renderer is null or unrecognized. */
  isSoftwareRenderer: boolean;

  /** Maximum texture size supported (gl.MAX_TEXTURE_SIZE).
   *  Typically 4096-16384 for hardware, 8192 for SwiftShader. */
  maxTextureSize: number;

  /** Maximum viewport dimensions (gl.MAX_VIEWPORT_DIMS).
   *  Array of [maxWidth, maxHeight]. */
  maxViewportDims: [number, number];
}

/**
 * Result of resolving the GPU mode, including the supplementary
 * Chromium launch arguments that OBJ-009 does NOT already provide.
 */
export interface ResolvedRenderingConfig {
  /** The resolved GPU mode. For 'auto', this is 'hardware'
   *  (initial attempt — actual backend is determined post-launch
   *  via probeWebGLRenderer). */
  resolvedMode: 'software' | 'hardware';

  /** The requested GPU mode (what the caller asked for). */
  requestedMode: GpuMode;

  /** The value to pass to PuppeteerBridge's `gpu` config option.
   *  'software' -> false, 'hardware'/'auto' -> true. */
  bridgeGpu: boolean;

  /** Supplementary Chromium args to pass to PuppeteerBridge's
   *  `extraArgs` config. These ONLY contain args that OBJ-009
   *  does NOT already add. OBJ-009's internal defaults
   *  (--no-sandbox, --disable-dev-shm-usage, etc.) and
   *  gpu-flag logic (--disable-gpu when gpu:false) are NOT
   *  duplicated here.
   *
   *  For 'software': EXTRA_SOFTWARE_ARGS
   *    (--use-gl=swiftshader, --disable-gpu-compositing)
   *  For 'hardware'/'auto': EXTRA_HARDWARE_ARGS
   *    (--enable-gpu-rasterization, --enable-zero-copy,
   *     --ignore-gpu-blocklist)
   *  Both modes also include EXTRA_BASELINE_ARGS
   *    (throttling-prevention flags).
   */
  extraArgs: string[];

  /** Whether GPU was detected as available. null until
   *  probeWebGLRenderer() is called post-launch. This field
   *  is NOT populated by resolveRenderingConfig() — it is
   *  set by the orchestrator after probing. Present in the
   *  type for the orchestrator to populate and log. */
  gpuDetected: boolean | null;
}

/**
 * Error thrown when WebGL validation fails after launch.
 */
export class WebGLValidationError extends Error {
  readonly code: WebGLValidationErrorCode;
  readonly rendererInfo?: WebGLRendererInfo;

  constructor(
    code: WebGLValidationErrorCode,
    message: string,
    rendererInfo?: WebGLRendererInfo
  );
}

export type WebGLValidationErrorCode =
  | 'NO_WEBGL'            // WebGL context could not be created
  | 'CONTEXT_LOST'        // WebGL context was created but is lost
  | 'VIEWPORT_TOO_SMALL'  // maxViewportDims < requested viewport size
  ;

/**
 * Resolve the supplementary Chromium args and bridge config
 * for a given GPU mode. Pure function — no I/O.
 *
 * Returns the `bridgeGpu` flag and `extraArgs` to pass to
 * PuppeteerBridge's constructor. Does NOT duplicate args that
 * OBJ-009 already adds internally.
 */
export function resolveRenderingConfig(mode: GpuMode): ResolvedRenderingConfig;

/**
 * Probe the WebGL rendering backend of a launched PuppeteerBridge.
 *
 * Creates a temporary <canvas> in the page, obtains a WebGL context
 * (tries WebGL2 first, falls back to WebGL1), queries debug info,
 * then removes the canvas. Does NOT interfere with #depthkit-canvas
 * or the Three.js renderer.
 *
 * @param bridge - A launched PuppeteerBridge instance.
 * @throws Error if bridge is not launched.
 * @throws WebGLValidationError with code 'NO_WEBGL' if no WebGL
 *         context can be created.
 */
export function probeWebGLRenderer(
  bridge: PuppeteerBridge
): Promise<WebGLRendererInfo>;

/**
 * Validate that the WebGL backend meets depthkit's minimum
 * requirements for a given viewport size.
 *
 * Checks:
 * 1. maxViewportDims >= [viewportWidth, viewportHeight].
 *
 * This does NOT validate individual texture dimensions — those
 * are unknown at config time and are validated at texture load
 * time by OBJ-015. The viewportWidth/Height parameters refer
 * to the composition's output dimensions (e.g., 1920x1080),
 * not texture sizes.
 *
 * @throws WebGLValidationError with code 'VIEWPORT_TOO_SMALL'
 *         if maxViewportDims is insufficient.
 */
export function validateWebGLCapabilities(
  info: WebGLRendererInfo,
  viewportWidth: number,
  viewportHeight: number
): void;

/**
 * Supplementary baseline args that OBJ-009 does NOT add.
 * These prevent Chromium from throttling background pages,
 * which is critical for C-03 (deterministic virtualized timing).
 * Included in both software and hardware modes.
 */
export const EXTRA_BASELINE_ARGS: readonly string[];

/**
 * Supplementary software-rendering args that OBJ-009 does NOT add.
 * OBJ-009 already adds --disable-gpu when gpu:false.
 * These add explicit SwiftShader selection and compositing control.
 */
export const EXTRA_SOFTWARE_ARGS: readonly string[];

/**
 * Supplementary hardware-rendering args for GPU optimization.
 */
export const EXTRA_HARDWARE_ARGS: readonly string[];
```

## Design Decisions

### D1: Separate Module from PuppeteerBridge

**Decision:** OBJ-049 is a standalone utility module (`rendering-config.ts`), not a modification to OBJ-009's `PuppeteerBridge`.

**Rationale:** OBJ-009 is verified. Modifying it would require re-verification. OBJ-009 already exposes `gpu: boolean` and `extraArgs: string[]` — OBJ-049 produces values that map directly to these config options. The bridge remains a transport layer; OBJ-049 provides the domain knowledge about *which supplementary flags* to use and *why*.

### D2: Supplementary Args Only — No Duplication with OBJ-009

**Decision:** OBJ-049's exported arg constants (`EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, `EXTRA_HARDWARE_ARGS`) contain ONLY args that OBJ-009 does NOT already add internally. The `extraArgs` field in `ResolvedRenderingConfig` is passed directly to `PuppeteerBridge({ extraArgs })`.

**OBJ-009's internal args (NOT duplicated by OBJ-049):**
- `--disable-dev-shm-usage`
- `--no-sandbox`
- `--disable-setuid-sandbox`
- `--hide-scrollbars`
- `--mute-audio`
- `--allow-file-access-from-files`
- `--disable-gpu` (added by OBJ-009 when `gpu: false`)

**OBJ-049's `EXTRA_BASELINE_ARGS` (new, added to both modes):**
```
--disable-background-timer-throttling
--disable-renderer-backgrounding
--disable-backgrounding-occluded-windows
```
These prevent Chromium from throttling the headless page's JavaScript execution, which would introduce non-deterministic timing — violating C-03.

**OBJ-049's `EXTRA_SOFTWARE_ARGS`:**
```
--use-gl=swiftshader            # Explicitly select SwiftShader GL backend
--disable-gpu-compositing       # Disable GPU-based compositing
```
Note: `--disable-gpu` is NOT here — OBJ-009 adds it when `gpu: false`.

**OBJ-049's `EXTRA_HARDWARE_ARGS`:**
```
--enable-gpu-rasterization      # Use GPU for rasterization
--enable-zero-copy              # Zero-copy GPU memory for textures
--ignore-gpu-blocklist          # Allow GPUs that Chromium has blocklisted
```

**Integration pattern for OBJ-035:**
```typescript
const config = resolveRenderingConfig('software');
const bridge = new PuppeteerBridge({
  width: 1920,
  height: 1080,
  gpu: config.bridgeGpu,        // false for software
  extraArgs: config.extraArgs,  // EXTRA_BASELINE_ARGS + EXTRA_SOFTWARE_ARGS
});
```

### D3: Three GPU Modes — software, hardware, auto

**Decision:** Three explicit modes rather than a simple boolean.

**Rationale:**
- `software` is the C-11 baseline. Always works. Docker, CI/CD, VPS without GPU. This is the default.
- `hardware` is for environments where the operator knows a GPU is available.
- `auto` attempts hardware, then probes to discover what it actually got. See D4.

**Mapping to OBJ-009's `gpu: boolean`:**
| GpuMode | `bridgeGpu` | OBJ-009 behavior |
|---|---|---|
| `'software'` | `false` | OBJ-009 adds `--disable-gpu` |
| `'hardware'` | `true` | OBJ-009 omits `--disable-gpu` |
| `'auto'` | `true` | OBJ-009 omits `--disable-gpu` (let Chromium try hardware, fall back internally) |

### D4: `auto` Mode — Probe and Log, No Re-Launch

**Decision:** In `auto` mode, the orchestrator launches with hardware flags, probes WebGL, and **logs the result without re-launching**. If Chromium fell back to SwiftShader internally, rendering proceeds on SwiftShader.

**Rationale:** When Chromium can't access a GPU, it automatically falls back to SwiftShader. The browser is already rendering with SwiftShader — re-launching with explicit `--disable-gpu` and `--use-gl=swiftshader` restarts the browser to arrive at the same backend. The supplementary software args (`--disable-gpu-compositing`, `--use-gl=swiftshader`) provide marginally cleaner initialization but do not change the rendering backend or correctness. The 2-5 second re-launch cost is not justified by this marginal benefit.

**Auto-mode orchestrator pattern (for OBJ-035):**
```
1. resolveRenderingConfig('auto') -> { bridgeGpu: true, extraArgs: [...hardware + baseline] }
2. Launch bridge
3. probeWebGLRenderer(bridge) -> info
4. If info.isSoftwareRenderer:
   Log: "GPU not available; rendering with SwiftShader (software)"
5. Else:
   Log: "GPU available; rendering with hardware acceleration ({info.renderer})"
6. validateWebGLCapabilities(info, width, height)
7. Proceed with rendering
```

No re-launch. No bridge lifecycle management in OBJ-049.

**When explicit software mode matters:** If the operator wants guaranteed reproducibility of the software rendering path (e.g., for CI/CD where deterministic args are desired regardless of host GPU), they should use `'software'` explicitly, not `'auto'`.

### D5: `resolveRenderingConfig()` is Pure

**Decision:** The config resolver is a pure function — no I/O, no probing, no system calls.

**Rationale:** Reliable GPU detection requires a running browser. System-level checks (`lspci`, `nvidia-smi`) are platform-specific and may not reflect what Chromium can actually use. The two-phase approach (resolve args -> launch -> probe) is cleaner.

### D6: Probe via Temporary Canvas

**Decision:** `probeWebGLRenderer()` creates a temporary `<canvas>` in the page, obtains a WebGL context, reads the debug info, then removes the canvas. It does NOT use `#depthkit-canvas` or the Three.js renderer.

**Rationale:** The probe may run before OBJ-011's `init()` creates the Three.js renderer. A temporary canvas avoids coupling to the renderer lifecycle and prevents interference (e.g., WebGL context limits).

### D7: Software Renderer Detection Heuristic

**Decision:** `isSoftwareRenderer` checks if the `WEBGL_debug_renderer_info` renderer string contains (case-insensitive) any of:
- `"SwiftShader"` — Chromium's built-in software renderer
- `"llvmpipe"` — Mesa's software rasterizer
- `"softpipe"` — Mesa's reference software rasterizer

Returns `false` if renderer is `null` or unrecognized.

**Rationale:** The generic `"Mesa"` string is NOT checked because Mesa is also the userspace driver stack for hardware-accelerated rendering on Linux (e.g., `"Mesa Intel(R) UHD Graphics 630"`, `"AMD RADV NAVI10"`). Checking for `"Mesa"` would false-positive on hardware Mesa. The specific software rasterizer names (`llvmpipe`, `softpipe`) are unambiguous.

**If `WEBGL_debug_renderer_info` is unavailable** (privacy-restricted profile): `renderer` and `vendor` are `null`, `isSoftwareRenderer` is `false` (unknown defaults to not-software). This is conservative — the worst case is that `auto` mode doesn't detect software rendering, which is harmless (rendering proceeds regardless).

### D8: Validation Scope — Viewport Only

**Decision:** `validateWebGLCapabilities()` checks only `maxViewportDims >= [viewportWidth, viewportHeight]`. It does NOT check `maxTextureSize` against texture dimensions (unknown at config time). The `TEXTURE_TOO_SMALL` error code is removed.

**Rationale:** Individual texture oversizing is handled at texture load time by OBJ-015. Validating `maxTextureSize` against the viewport dimensions would give a false sense of security — a 4096x4096 sky texture on a 1920x1080 viewport would pass the viewport check but fail the texture check. Better to not pretend we validate textures here and leave that to the appropriate module.

### D9: Headless Mode Compatibility

**Decision:** OBJ-049's args are tested with Puppeteer's default headless mode (which uses `--headless=new` in modern Puppeteer/Chrome). The spec does not prescribe a specific headless mode — OBJ-009 controls this via its `headless` config option.

**Rationale:** Chrome's new headless mode (`--headless=new`, default since Puppeteer v21 / Chrome 112) uses the same browser engine as headed mode, including full WebGL support. The old headless mode (`--headless=old` / `headless: 'shell'`) used a stripped-down rendering path with potentially different SwiftShader behavior. OBJ-009's `headless: true` maps to the new headless mode by default, which is the correct choice for depthkit. If an operator explicitly sets `headless: 'shell'` (old mode) via OBJ-009, OBJ-049's software rendering config is still expected to work — SwiftShader is available in both modes — but this combination is not a tested configuration. Documented as OQ-D.

## Acceptance Criteria

### Configuration Resolution

- [ ] **AC-01:** `resolveRenderingConfig('software')` returns `resolvedMode: 'software'`, `requestedMode: 'software'`, `bridgeGpu: false`, `gpuDetected: null`, and `extraArgs` containing `'--use-gl=swiftshader'`, `'--disable-gpu-compositing'`, `'--disable-background-timer-throttling'`, `'--disable-renderer-backgrounding'`, `'--disable-backgrounding-occluded-windows'`. `extraArgs` does NOT contain `'--disable-gpu'` (OBJ-009 handles that via `bridgeGpu: false`).
- [ ] **AC-02:** `resolveRenderingConfig('hardware')` returns `resolvedMode: 'hardware'`, `bridgeGpu: true`, and `extraArgs` containing `'--enable-gpu-rasterization'`, `'--ignore-gpu-blocklist'`, `'--disable-background-timer-throttling'`, `'--disable-renderer-backgrounding'`, `'--disable-backgrounding-occluded-windows'`. `extraArgs` does NOT contain `'--disable-gpu'`.
- [ ] **AC-03:** `resolveRenderingConfig('auto')` returns `resolvedMode: 'hardware'`, `requestedMode: 'auto'`, `bridgeGpu: true`, and `extraArgs` identical to the `'hardware'` resolution.
- [ ] **AC-04:** `EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, and `EXTRA_HARDWARE_ARGS` are frozen readonly arrays.
- [ ] **AC-05:** `resolveRenderingConfig()` is a pure function — calling it twice with the same argument returns deeply equal results.
- [ ] **AC-06:** The throttling-prevention flags (`--disable-background-timer-throttling`, `--disable-renderer-backgrounding`, `--disable-backgrounding-occluded-windows`) appear in `extraArgs` for ALL three modes (`software`, `hardware`, `auto`).

### WebGL Probing

- [ ] **AC-07:** After launching a PuppeteerBridge with `gpu: false`, `probeWebGLRenderer(bridge)` returns a `WebGLRendererInfo` with `isSoftwareRenderer: true`, `renderer` containing `"SwiftShader"`, `version` containing `"WebGL"`, `maxTextureSize >= 4096`, and `maxViewportDims` each `>= 1920`.
- [ ] **AC-08:** `probeWebGLRenderer()` when bridge is not launched throws `Error` (not `WebGLValidationError`) with a message containing "not launched".
- [ ] **AC-09:** `probeWebGLRenderer()` does not interfere with `#depthkit-canvas`. After probing, the Three.js renderer (if initialized via OBJ-011) still functions correctly. Verifiable by: launch bridge -> probe -> init page (OBJ-011) -> render a frame -> capture — capture succeeds.
- [ ] **AC-10:** `WebGLRendererInfo.renderer` and `vendor` are populated strings (not null) when running in standard headless Chromium.

### isSoftwareRenderer Detection

- [ ] **AC-11:** Renderer string `"Google SwiftShader"` -> `isSoftwareRenderer: true`.
- [ ] **AC-12:** Renderer string `"ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 ...)"` -> `isSoftwareRenderer: false`.
- [ ] **AC-13:** Renderer string containing `"llvmpipe"` -> `isSoftwareRenderer: true`.
- [ ] **AC-14:** Renderer string `"Mesa Intel(R) UHD Graphics 630"` -> `isSoftwareRenderer: false` (hardware Mesa).
- [ ] **AC-15:** Renderer string `null` -> `isSoftwareRenderer: false`.

### WebGL Validation

- [ ] **AC-16:** `validateWebGLCapabilities(info, 1920, 1080)` does not throw when `maxViewportDims >= [1920, 1080]`.
- [ ] **AC-17:** `validateWebGLCapabilities(info, 32000, 32000)` throws `WebGLValidationError` with code `'VIEWPORT_TOO_SMALL'`.
- [ ] **AC-18:** `WebGLValidationError` instances have `code`, `message`, and optional `rendererInfo`. `error instanceof WebGLValidationError === true`. `error instanceof Error === true`.

### Software Rendering Correctness (C-11)

- [ ] **AC-19:** A PuppeteerBridge launched with software rendering config can: initialize the Three.js page (OBJ-011), render a scene with a colored mesh, and produce a non-black frame capture (OBJ-012). This is the end-to-end C-11 validation.
- [ ] **AC-20:** A frame rendered under software rendering, captured twice in sequence, produces identical PNG buffers (same-backend determinism, C-05 + C-11).
- [ ] **AC-21:** `probeWebGLRenderer()` after software rendering launch returns `isSoftwareRenderer: true`.

## Edge Cases and Error Handling

| Scenario | Expected Behavior |
|---|---|
| `resolveRenderingConfig()` with invalid mode | TypeScript compile error (union type). No runtime check needed. |
| `probeWebGLRenderer()` on page with no WebGL support | Throws `WebGLValidationError` with code `'NO_WEBGL'`. Extremely unlikely in Chromium (SwiftShader always provides WebGL). |
| `probeWebGLRenderer()` when `WEBGL_debug_renderer_info` unavailable | Returns `renderer: null`, `vendor: null`, `isSoftwareRenderer: false`. `version` and capability values still populated from standard WebGL API. |
| `validateWebGLCapabilities()` with viewport > `maxViewportDims` | Throws `WebGLValidationError` with code `'VIEWPORT_TOO_SMALL'`, message includes requested vs. available dimensions. |
| Hardware mode in Docker without GPU passthrough | Browser launches, Chromium internally falls back to SwiftShader. `probeWebGLRenderer()` returns `isSoftwareRenderer: true`. Rendering works correctly — SwiftShader is a complete WebGL implementation. |
| `auto` mode on machine with GPU | Launch with hardware flags -> probe -> `isSoftwareRenderer: false` -> log "hardware acceleration active" -> proceed. |
| `auto` mode on machine without GPU | Launch with hardware flags -> Chromium falls back to SwiftShader -> probe -> `isSoftwareRenderer: true` -> log "software rendering active" -> proceed (no re-launch). |
| Multiple `probeWebGLRenderer()` calls on same bridge | Safe. Each creates and destroys a temporary canvas. No state accumulation. |
| Probe after WebGL context loss on `#depthkit-canvas` | Probe uses its own temporary canvas. Context loss on depthkit canvas doesn't affect probe. |
| SwiftShader `maxViewportDims` vs. 4K composition | SwiftShader's typical `MAX_VIEWPORT_DIMS` is [8192, 8192], accommodating 4K (3840x2160). Validation catches attempts beyond this. |
| `extraArgs` passed to OBJ-009 with duplicate args | OBJ-049's `extraArgs` are designed to contain NO duplicates with OBJ-009's internal args. If a caller manually adds duplicates via their own `extraArgs`, Chromium tolerates them harmlessly. |

## Test Strategy

### Unit Tests: `test/unit/rendering-config.test.ts`

1. **`resolveRenderingConfig('software')`:** Returns correct `resolvedMode`, `bridgeGpu: false`, `extraArgs` containing `EXTRA_BASELINE_ARGS` + `EXTRA_SOFTWARE_ARGS` but NOT `--disable-gpu`.
2. **`resolveRenderingConfig('hardware')`:** Returns correct fields, `bridgeGpu: true`, `extraArgs` containing `EXTRA_BASELINE_ARGS` + `EXTRA_HARDWARE_ARGS`, no `--disable-gpu`.
3. **`resolveRenderingConfig('auto')`:** Returns `resolvedMode: 'hardware'`, `requestedMode: 'auto'`, `bridgeGpu: true`, `extraArgs` matching hardware config.
4. **Throttling flags in all modes:** All three modes include `--disable-background-timer-throttling`, `--disable-renderer-backgrounding`, `--disable-backgrounding-occluded-windows` in `extraArgs`.
5. **No OBJ-009 arg duplication:** None of `EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, `EXTRA_HARDWARE_ARGS` contain `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-setuid-sandbox`, `--hide-scrollbars`, `--mute-audio`, `--allow-file-access-from-files`, or `--disable-gpu`.
6. **Purity:** Two calls with same arg return deeply equal results.
7. **Arg arrays frozen:** `EXTRA_BASELINE_ARGS`, `EXTRA_SOFTWARE_ARGS`, `EXTRA_HARDWARE_ARGS` are frozen (Object.isFrozen).
8. **`WebGLValidationError` construction:** All error codes construct correctly, `instanceof` checks pass.
9. **`validateWebGLCapabilities` pass:** Mock info with `maxViewportDims: [8192, 8192]`, validate 1920x1080 — no throw.
10. **`validateWebGLCapabilities` viewport fail:** Mock info with `maxViewportDims: [1024, 1024]`, validate 1920x1080 — throws `VIEWPORT_TOO_SMALL`.
11. **`isSoftwareRenderer` detection cases:** `"Google SwiftShader"` -> true, `"ANGLE (NVIDIA ...)"` -> false, `"Mesa/X.org llvmpipe"` -> true, `"softpipe"` -> true, `"Mesa Intel(R) UHD Graphics 630"` -> false, `null` -> false, `""` -> false.

### Integration Tests: `test/integration/rendering-config.test.ts`

Small viewports (320x240) for speed. All tests run with `gpu: false` (software rendering) by default.

12. **Software rendering probe:** Launch bridge with software config -> probe -> `isSoftwareRenderer: true`, renderer contains "SwiftShader".
13. **Software rendering end-to-end (C-11):** Launch with software config -> init page (OBJ-011) -> render colored mesh -> capture (OBJ-012) -> non-black PNG.
14. **Same-backend determinism (C-05):** Render same frame twice under software rendering -> identical PNG buffers.
15. **Probe does not interfere:** Launch -> probe -> init -> render -> capture succeeds.
16. **Probe on unlaunched bridge:** Throws Error with "not launched".
17. **Viewport validation with real SwiftShader:** Probe real SwiftShader -> validate 1920x1080 -> no throw.
18. **Viewport validation failure:** Probe real SwiftShader -> validate 32000x32000 -> throws `VIEWPORT_TOO_SMALL`.
19. **Multiple probes safe:** Probe 3 times sequentially -> all return consistent results.

### Performance Baseline

20. **Probe latency:** Time 10 sequential `probeWebGLRenderer()` calls, log average. Expected: <100ms per probe. One-time cost per render job.

### Docker/CI Validation (TC-11)

21. **Software rendering in Docker:** Run integration test 13 inside a Docker container with no GPU passthrough. Must pass, confirming C-11.

### Relevant Testable Claims

- **TC-02**: Software vs. hardware performance is observable via downstream modules' stats. OBJ-049's probe reports which backend is active.
- **TC-06**: Test 14 validates same-backend determinism.
- **TC-11**: Tests 12, 13, and 21 directly validate Docker/software WebGL.

## Integration Points

### Depends on

| Dependency | What OBJ-049 uses |
|---|---|
| **OBJ-012** (FrameCapture) | Used in integration tests to verify frame capture produces correct output under software rendering. `FrameCapture.capture()` is the validation mechanism for C-11. |
| **OBJ-009** (PuppeteerBridge) — transitive via OBJ-012 | `probeWebGLRenderer()` accepts a `PuppeteerBridge` and calls `bridge.evaluate()` for WebGL probing. Uses `bridge.isLaunched` for pre-condition checks. `resolveRenderingConfig()` produces `bridgeGpu` and `extraArgs` values that map to OBJ-009's `gpu` and `extraArgs` config. |

### Consumed by

| Downstream | How it uses OBJ-049 |
|---|---|
| **OBJ-035** (Orchestrator) | Calls `resolveRenderingConfig()` to determine bridge config. Passes `bridgeGpu` and `extraArgs` to PuppeteerBridge constructor. After launch, calls `probeWebGLRenderer()` and `validateWebGLCapabilities()`. Implements `auto`-mode probe-and-log pattern. Logs `WebGLRendererInfo` for diagnostics. |
| **OBJ-050** (Docker containerization) | Depends on OBJ-049's software rendering config being correct. Docker image uses `resolveRenderingConfig('software')` as default. OBJ-050's acceptance tests exercise the full software rendering pipeline inside Docker. |
| **OBJ-074** (Performance benchmarking) | Uses `probeWebGLRenderer()` to report active rendering backend during benchmarks. |

### File Placement

```
depthkit/
  src/
    engine/
      rendering-config.ts         # NEW — resolveRenderingConfig(), probeWebGLRenderer(),
                                   #       validateWebGLCapabilities(), GpuMode,
                                   #       WebGLRendererInfo, ResolvedRenderingConfig,
                                   #       WebGLValidationError, arg constants
  test/
    unit/
      rendering-config.test.ts     # NEW — unit tests (pure function tests, no browser)
    integration/
      rendering-config.test.ts     # NEW — integration tests with Puppeteer
```

## Open Questions

### OQ-A: Should `probeWebGLRenderer()` also check WebGL extension availability?

Some Three.js features require specific WebGL extensions. SwiftShader supports most standard extensions but may lack some. For V1, `meshBasicMaterial` doesn't require non-standard extensions. Defer until a scene geometry requires an advanced material.

### OQ-B: Should the module export a convenience function combining resolve + launch + probe + validate?

A `launchWithRendering(mode, bridgeConfig)` function would simplify OBJ-035 but would own bridge lifecycle, violating D1. Defer to OBJ-035's spec.

### OQ-C: Cross-backend determinism (software vs. hardware)

Software and hardware WebGL renderers may produce per-pixel differences due to floating-point implementation differences. For `meshBasicMaterial` (unlit, texture-only), differences should be minimal but non-zero. C-05 (deterministic output) should be scoped to "same rendering backend" rather than "any backend." Cross-backend visual equivalence is desirable but not guaranteed. If empirically tested and the divergence is measurable, document the tolerance.

### OQ-D: Old headless mode compatibility

Puppeteer's `headless: 'shell'` (old headless mode) uses a stripped-down rendering path. OBJ-049's software rendering config is expected to work in both modes, but only the new headless mode (`headless: true`, the default) is a tested configuration. If old headless mode produces different SwiftShader behavior, document the divergence.
