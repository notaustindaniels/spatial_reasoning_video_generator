# Specification: OBJ-046 — CLI Interface

## Summary

OBJ-046 delivers the Commander-based CLI for depthkit (`src/cli.ts`) — the primary human-facing entry point for rendering, validating, and previewing manifests. It exposes three commands (`render`, `validate`, `preview`), handles argument parsing for manifest paths, output paths, resolution/fps overrides, GPU mode, encoding presets, verbose/debug output, and provides structured progress reporting and timing statistics during renders. It composes the Orchestrator (OBJ-035), manifest loader (OBJ-016), geometry registry (OBJ-005), and camera registry (OBJ-006) into a user-friendly terminal experience. The `package.json` `bin` field points to this module.

## Interface Contract

### Module: `src/cli.ts`

This is the executable entry point. The source file begins with `#!/usr/bin/env node` (preserved by the TypeScript compiler or prepended by the build step). It is not designed for programmatic import — it runs `program.parse(process.argv)` at module scope, wrapped in a top-level error handler.

**Entry point structure:**

```typescript
#!/usr/bin/env node

/**
 * Creates and configures the Commander program instance.
 * Exported for testing — allows invoking CLI commands programmatically
 * without spawning a child process.
 *
 * The returned program has exitOverride() enabled. Instead of calling
 * process.exit(), Commander throws a CommanderError with exitCode and
 * message. The src/cli.ts entry-point code catches CommanderError and
 * calls process.exit(error.exitCode). This separation ensures
 * createProgram() is safe for programmatic invocation in tests.
 *
 * @returns Configured Commander.Command instance with all commands registered.
 */
export function createProgram(): Command;
```

**Version source:** The program version is read from `package.json` at module load time. The implementation resolves the `package.json` path relative to `__dirname` (or `import.meta.url` for ESM), reads it with `readFileSync`, parses it, and extracts the `version` field. This value is passed to Commander's `.version()` method.

### Shared Global Options

These options are available on every command:

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--verbose` | `-v` | boolean | `false` | Enable verbose output (timing stats, per-scene details, renderer info). |
| `--debug` | | boolean | `false` | Enable debug output (forwards headless Chromium console logs to stderr, enables `OrchestratorConfig.debug`). Implies `--verbose`. |
| `--color` | | boolean | auto-detected | Force color output. Default: auto-detect via `process.stdout.isTTY`. `--no-color` disables. |

### Command: `depthkit render <manifest>`

Renders a manifest to an MP4 file.

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:**

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output` | `-o` | string | `"./output.mp4"` | Output MP4 file path. |
| `--width` | `-W` | number | _(from manifest)_ | Override `composition.width`. |
| `--height` | `-H` | number | _(from manifest)_ | Override `composition.height`. Note: uppercase `-H` to avoid conflict with Commander's reserved `-h` for `--help`. |
| `--fps` | | number | _(from manifest)_ | Override `composition.fps`. |
| `--assets-dir` | `-a` | string | _(manifest's parent directory)_ | Base directory for resolving relative image paths. |
| `--gpu` | | string | `"software"` | GPU mode: `"software"`, `"hardware"`, or `"auto"`. Maps to `OrchestratorConfig.gpu` (boolean) — see D4. |
| `--preset` | | string | `"medium"` | H.264 encoding preset. One of: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`. Maps to `OrchestratorConfig.encodingPreset`. |
| `--crf` | | number | `23` | Constant Rate Factor (0–51). Maps to `OrchestratorConfig.crf`. |
| `--ffmpeg-path` | | string | _(auto-resolved)_ | Path to FFmpeg binary. Maps to `OrchestratorConfig.ffmpegPath`. |
| `--chromium-path` | | string | _(bundled)_ | Path to Chromium executable. Maps to `OrchestratorConfig.chromiumPath`. |

**Behavior:**
1. Parse and validate CLI arguments (see D2 for override application).
2. Populate registries via `initRegistries()` (see D3).
3. Load manifest file via `loadManifestFromFile()` (OBJ-016).
4. Apply resolution/fps overrides to the loaded manifest (see D2).
5. Construct `OrchestratorConfig` and create `Orchestrator`.
6. Provide an `onProgress` callback that renders a progress bar to stderr (see D5).
7. Call `orchestrator.render()`.
8. On success: print summary to stdout, exit code 0.
9. On failure: print formatted error to stderr, exit code 1.

**Stdout output on success (non-verbose):**
```
✓ Rendered 1800 frames in 8m 32s → ./output.mp4
  Duration: 60.00s | Resolution: 1920×1080 | FPS: 30
  Avg frame: 284ms | File size: 12.4 MB
```

**Stdout output on success (verbose):**
```
✓ Rendered 1800 frames in 8m 32s → ./output.mp4
  Duration: 60.00s | Resolution: 1920×1080 | FPS: 30
  Avg frame: 284ms | File size: 12.4 MB
  Scenes: 5 | Geometry types: stage, tunnel, diorama
  Capture strategy: viewport-png | Encoding preset: medium | CRF: 23
  WebGL: SwiftShader (software) | WebGL 2.0
  Audio: muxed (narration.mp3)
  Warnings: 0
```

### Command: `depthkit validate <manifest>`

Validates a manifest without rendering. Fast — no browser or FFmpeg launched.

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:** None beyond global options.

**Behavior:**
1. Populate registries via `initRegistries()` (see D3).
2. Load and validate manifest via `loadManifestFromFile()` (OBJ-016).
3. On valid (with or without warnings): print summary to stdout, exit code 0.
4. On invalid: print formatted errors to stderr, exit code 1.

**Stdout on valid:**
```
✓ Manifest valid: 5 scenes, 60.00s total duration
  Geometries: stage (2), tunnel (2), diorama (1)
  Cameras: slow_push_forward (3), tunnel_push_forward (2)
```

If warnings exist:
```
✓ Manifest valid with 2 warning(s): 5 scenes, 60.00s total duration
  ⚠ scenes: Scene array order differs from start_time order (SCENE_ORDER_MISMATCH)
  ⚠ scenes[2].planes.subject: Per-plane opacity is not supported in V1 (UNSUPPORTED_FEATURE)
  Geometries: stage (2), tunnel (2), diorama (1)
  Cameras: slow_push_forward (3), tunnel_push_forward (2)
```

**Stderr on invalid:**
```
✗ Manifest validation failed (3 error(s)):
  ✗ scenes[0].geometry: Unknown geometry "tunl". Available: stage, tunnel, canyon, flyover, diorama, portal, panorama, close_up (UNKNOWN_GEOMETRY)
  ✗ scenes[1].planes: Missing required slot "floor" for geometry "stage" (MISSING_REQUIRED_SLOT)
  ✗ scenes[2].camera: Unknown camera "push_fast". Available: static, slow_push_forward, ... (UNKNOWN_CAMERA)
```

**Assumption:** Validation error messages from OBJ-016 include available options (geometry names, camera names) in their `message` field. The CLI does not need access to registries for error formatting.

### Command: `depthkit preview <manifest>`

Serves the Three.js scene on a local HTTP server for real-time preview in a browser. (Addresses OQ-05 from the seed.)

**Positional argument:**
- `<manifest>` — Path to the manifest JSON file. Required.

**Options:**

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--port` | `-p` | number | `3000` | HTTP server port. |
| `--open` | | boolean | `false` | Automatically open the preview URL in the default browser. |

**Behavior:**
1. Validate the manifest (same as `validate` command).
2. If valid: start an HTTP server that serves the Three.js page with the manifest's scene data, using real-time `requestAnimationFrame` playback.
3. Print the URL to stdout.
4. Keep the process running until the user presses Ctrl+C (SIGINT).

**Scope note:** The preview command's HTTP server and page serving logic is deliberately under-specified. OBJ-046 defines the CLI command signature, argument parsing, manifest validation gate, and lifecycle. The actual preview server implementation is deferred. OBJ-046's implementation uses a dynamic import extension point (see D7) so the preview server can be plugged in later. If the preview server module is not yet available, the command prints an informational message and exits with code 0:

```
ℹ Preview server not yet implemented. Use 'depthkit render' for full rendering.
```

### Module: `src/cli/format.ts` — Output Formatting

Handles all terminal output formatting. Separated from `src/cli.ts` for testability.

```typescript
/**
 * Formats an OrchestratorResult into a human-readable summary string.
 * File size is obtained by the caller via fs.stat() and passed in.
 *
 * @param result - The orchestrator result.
 * @param fileSizeBytes - Output file size in bytes.
 * @param verbose - Whether to include extended details.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string (no trailing newline).
 */
export function formatRenderResult(
  result: OrchestratorResult,
  fileSizeBytes: number,
  verbose: boolean,
  color: boolean,
): string;

/**
 * Formats a successful validation result into a human-readable summary.
 *
 * @param manifest - The validated manifest.
 * @param warnings - Any validation warnings.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatValidationSuccess(
  manifest: Manifest,
  warnings: ManifestError[],
  color: boolean,
): string;

/**
 * Formats validation errors into a human-readable error report.
 *
 * @param errors - All ManifestError objects from validation.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatValidationErrors(
  errors: ManifestError[],
  color: boolean,
): string;

/**
 * Formats an OrchestratorError into a human-readable error message.
 * Includes the error code, message, and context (frame number, validation errors).
 *
 * @param error - The orchestrator error.
 * @param verbose - Whether to include stack trace and cause chain.
 * @param color - Whether to include ANSI color codes.
 * @returns Formatted multi-line string.
 */
export function formatOrchestratorError(
  error: OrchestratorError,
  verbose: boolean,
  color: boolean,
): string;

/**
 * Formats a render progress update for terminal display.
 * Returns a single-line string suitable for overwriting the current line
 * via \r (carriage return).
 *
 * Spinner character cycles based on progress.frame % SPINNER_FRAMES.length
 * using Braille dot characters (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏).
 *
 * Example: "⠸ Rendering [████████░░░░░░░░] 48% | Frame 864/1800 | 3m 12s remaining"
 *
 * @param progress - The RenderProgress data from the orchestrator callback.
 * @param color - Whether to include ANSI color codes.
 * @returns Single-line string (no newline).
 */
export function formatProgress(
  progress: RenderProgress,
  color: boolean,
): string;

/**
 * Formats a file size in bytes into a human-readable string.
 * e.g., 1024 → "1.0 KB", 13042688 → "12.4 MB"
 */
export function formatFileSize(bytes: number): string;

/**
 * Formats a duration in milliseconds into a human-readable string.
 * e.g., 512000 → "8m 32s", 1500 → "1.5s", 45 → "45ms"
 */
export function formatDuration(ms: number): string;
```

### Module: `src/cli/registry-init.ts` — Registry Population

Centralizes registry population so both `render` and `validate` commands use the same registries.

```typescript
import type { ManifestRegistry } from '../manifest/schema.js';
import type { GeometryRegistry } from '../scenes/geometries/types.js';
import type { CameraPathRegistry } from '../camera/types.js';

/**
 * Registry bundle returned by initRegistries().
 */
export interface RegistryBundle {
  manifestRegistry: ManifestRegistry;
  geometryRegistry: GeometryRegistry;
  cameraRegistry: CameraPathRegistry;
}

/**
 * Populates and returns all three registries needed by the orchestrator.
 *
 * This function is synchronous. All geometry and camera modules are
 * imported statically at the top of registry-init.ts — their
 * registerGeometry() side effects execute at module load time, before
 * this function is called. The function body simply:
 *
 * 1. Calls getGeometryRegistry() (OBJ-005) to retrieve and freeze
 *    the geometry registry.
 * 2. Constructs the CameraPathRegistry by importing the camera
 *    preset barrel module (see D8 for mechanism).
 * 3. Creates a ManifestRegistry via createRegistry() (OBJ-004) and
 *    populates it by iterating the geometry and camera registries,
 *    converting each SceneGeometry → GeometryRegistration and
 *    CameraPathPreset → CameraRegistration.
 * 4. Returns the RegistryBundle.
 *
 * Must be called once at startup. Subsequent calls return the same
 * registries (because OBJ-005's registry locks on first read).
 *
 * @returns RegistryBundle with all registries populated.
 */
export function initRegistries(): RegistryBundle;
```

## Design Decisions

### D1: Commander as CLI Framework

**Decision:** Use `commander` (npm) for argument parsing and command routing.

**Rationale:** Commander is MIT-licensed, the most widely adopted Node.js CLI framework, and is already permitted by C-01 ("Standard npm utilities... are allowed"). It provides subcommand support, automatic `--help` generation, option type coercion, and default values.

### D2: Resolution/FPS Overrides Are Applied Post-Validation

**Decision:** CLI `--width`, `--height`, and `--fps` overrides are applied to the manifest object **after** Phase 1 (structural) and Phase 2 (semantic) validation, but **before** constructing the Orchestrator. The overrides mutate the `Manifest.composition` fields directly.

**Rationale:** The manifest on disk is the source of truth. Overrides are a convenience for testing different resolutions without editing the file. Applying overrides after validation ensures the base manifest is valid. The overridden values do not need re-validation because:
- Width/height: any positive integer is valid per OBJ-004's `CompositionSchema`.
- FPS: any integer in [1, 120] is valid per OBJ-004's `CompositionSchema`.

**Guard:** The CLI validates override values before applying: width and height must be positive integers; fps must be an integer in [1, 120]. Invalid CLI overrides produce an error message and exit code 1 before any manifest loading.

### D3: Registry Population is Centralized and Synchronous

**Decision:** A single synchronous `initRegistries()` function in `src/cli/registry-init.ts` returns a `RegistryBundle` containing all three registries. All geometry and camera modules are **statically imported** at the top of `registry-init.ts` — their `registerGeometry()` side effects execute at module load time. The function body only calls `getGeometryRegistry()`, assembles the camera registry, iterates both to build the `ManifestRegistry`, and returns.

**Rationale:** Both `render` and `validate` commands need the same registries. All geometry and camera modules are known at build time — dynamic imports add async complexity for no benefit. Static imports ensure all side-effect registrations are complete before `initRegistries()` is called.

**Key detail:** The `ManifestRegistry` (OBJ-004) stores validation-only metadata, while the spatial registries store full 3D data. `initRegistries()` converts between them:
- `SceneGeometry` → `GeometryRegistration`: extract `name`, `slots` (convert `PlaneSlot` → `PlaneSlotDef` by keeping only `required` and `description`), `compatibleCameras` (from `compatible_cameras`), `defaultCamera` (from `default_camera`).
- `CameraPathPreset` → `CameraRegistration`: extract `name`, `compatibleGeometries`, `supportsFovAnimation` (derived from `oversizeRequirements.fovRange[0] !== oversizeRequirements.fovRange[1]`).

### D4: GPU Mode Mapping

**Decision:** The CLI `--gpu` flag accepts `"software"`, `"hardware"`, or `"auto"` (string). This maps to `OrchestratorConfig.gpu` (boolean):
- `"software"` → `gpu: false`
- `"hardware"` → `gpu: true`
- `"auto"` → `gpu: false` (V1 simplification)

**Rationale:** OBJ-035's `OrchestratorConfig.gpu` is a simple boolean. OBJ-049 defines a richer `GpuMode` type but that integration is between OBJ-049 and OBJ-035. For V1, the CLI maps to the boolean. The `--gpu` flag is a string (not boolean) to preserve forward compatibility.

### D5: Progress Reporting via stderr

**Decision:** The `onProgress` callback writes progress updates to stderr using carriage return (`\r`) line overwriting. When stderr is not a TTY (piped to a file or another process), progress is suppressed entirely.

**Rationale:**
- **stderr, not stdout:** Stdout is reserved for the final result summary. This allows `depthkit render manifest.json > result.txt` to capture only the summary.
- **Carriage return overwriting:** Standard CLI progress bar pattern. After completion, a final newline is written so the success message appears on a fresh line.
- **TTY detection:** Piped stderr should not contain ANSI escape codes or carriage-return progress spam.

### D6: Exit Codes

**Decision:**
| Exit Code | Meaning |
|---|---|
| `0` | Success (render complete, manifest valid, preview started). |
| `1` | Failure (validation error, render error, invalid arguments). |
| `2` | Usage error (unknown command, missing required argument). Commander handles this by default. |

### D7: Preview Command Stub with Dynamic Import Extension Point

**Decision:** The `preview` command validates the manifest and then attempts to dynamically import a preview server module (`../preview/server.js`). If the import fails (module doesn't exist yet), it prints an informational message and exits with code 0.

**Rationale:** The preview server is outside OBJ-046's scope but the CLI command should be registered now so the `--help` output is complete. Dynamic import keeps the dependency optional — no build errors if the preview module doesn't exist.

### D8: Camera Registry Population Mechanism

**Decision:** OBJ-006 defines `CameraPathRegistry` as `Readonly<Record<string, CameraPathPreset>>` but does not define a mutable registry with `register()` / `getCameraPathRegistry()` functions analogous to OBJ-005's pattern. The `registry-init.ts` module constructs the `CameraPathRegistry` by:

1. Statically importing a **barrel module** at `src/camera/presets/index.ts` that re-exports all camera preset objects from OBJ-026 through OBJ-034. Each preset module exports a `CameraPathPreset` object as its default or named export.
2. Assembling these into a `Record<string, CameraPathPreset>` keyed by `preset.name`.
3. Freezing the record to produce a `CameraPathRegistry`.

**If the barrel module pattern is not used by the camera preset implementations**, `registry-init.ts` instead imports each camera preset module individually (e.g., `import { staticPreset } from '../camera/presets/static.js'`) and assembles them manually.

**Rationale:** OBJ-006's registry type is a plain frozen Record, not a stateful registry. The assembly must happen somewhere — `registry-init.ts` is the natural place since it's already responsible for bridging between spatial registries and the `ManifestRegistry`. The exact import mechanism depends on how OBJ-026–034 export their presets, but the contract is: `registry-init.ts` must produce a `CameraPathRegistry` containing all registered camera presets.

### D9: Assets Dir Default

**Decision:** If `--assets-dir` is not provided, the default is the **parent directory of the manifest file**, not `process.cwd()`. This matches the common pattern where images sit alongside or relative to the manifest.

**Rationale:** OBJ-035's default `assetsDir` is `process.cwd()`, which is appropriate for the programmatic API. For CLI usage, the manifest's directory is more intuitive — a user running `depthkit render ./projects/video1/manifest.json` expects image paths in the manifest to resolve relative to `./projects/video1/`, not the current directory.

### D10: SIGINT Handling

**Decision:** During rendering, SIGINT (Ctrl+C) is caught and converted to a cancellation request. The `onProgress` callback checks a flag and returns `false` to trigger the orchestrator's graceful shutdown. A second SIGINT force-kills the process via `process.exit(1)`.

**Rationale:** Graceful shutdown ensures FFmpeg is properly terminated and partial files are cleaned up, per OBJ-035's cleanup guarantees. The second-SIGINT escape hatch prevents the process from becoming unkillable if cleanup hangs.

### D11: No Color Dependency

**Decision:** ANSI color codes are generated using inline escape sequences, not a color library. A minimal color utility (6-8 functions: `red`, `green`, `yellow`, `cyan`, `bold`, `dim`, `reset`) is implemented in `src/cli/colors.ts`.

**Rationale:** Minimizes dependencies. The CLI needs only basic colors. The `--color` / `--no-color` flag and TTY detection control whether escape codes are emitted.

### D12: File Size in Summary

**Decision:** The render summary includes the output file size. This requires a `fs.stat()` call on the output MP4 after `render()` completes. The file size is passed to `formatRenderResult()` as a separate parameter (not derived from `OrchestratorResult`).

### D13: Commander exitOverride for Testability

**Decision:** `createProgram()` calls Commander's `exitOverride()` on the returned program. Instead of calling `process.exit()`, Commander throws a `CommanderError` with `exitCode` and `message` properties. The `src/cli.ts` entry-point code (the non-exported part that calls `program.parse(process.argv)`) wraps the parse call in a try/catch that catches `CommanderError` and calls `process.exit(error.exitCode)`.

**Rationale:** Without `exitOverride()`, Commander calls `process.exit()` on missing arguments, unknown commands, and `--help`/`--version`. This kills the test runner when tests invoke `createProgram().parseAsync()`. With `exitOverride()`, tests can catch `CommanderError` and assert on its `exitCode` and `message`.

## Acceptance Criteria

### Argument Parsing

- [ ] **AC-01:** `depthkit render manifest.json` renders the manifest to `./output.mp4` (default output path).
- [ ] **AC-02:** `depthkit render manifest.json -o video.mp4` renders to the specified output path.
- [ ] **AC-03:** `depthkit render manifest.json -W 1080 -H 1920 --fps 24` overrides the manifest's composition settings. The output video is 1080x1920 at 24fps.
- [ ] **AC-04:** `depthkit render` with no manifest argument prints a usage error and exits with code 2.
- [ ] **AC-05:** `depthkit render manifest.json --gpu hardware --preset slow --crf 18` passes the correct values to the orchestrator.
- [ ] **AC-06:** `depthkit --help` prints help with all three commands listed. `depthkit render --help` prints render-specific options including `-W` and `-H`.
- [ ] **AC-07:** `depthkit --version` prints the version string read from `package.json`.

### Validate Command

- [ ] **AC-08:** `depthkit validate manifest.json` with a valid manifest prints a success summary and exits with code 0. No browser or FFmpeg process is launched.
- [ ] **AC-09:** `depthkit validate manifest.json` with an invalid manifest prints all errors to stderr and exits with code 1.
- [ ] **AC-10:** `depthkit validate manifest.json` with a valid manifest that has warnings prints both the success summary and the warnings, and exits with code 0.

### Render Command — Success Path

- [ ] **AC-11:** A successful render prints a summary to stdout including frame count, duration, resolution, fps, average frame time, and file size.
- [ ] **AC-12:** With `--verbose`, the summary additionally includes scene count, geometry types used, capture strategy, encoding preset, CRF, WebGL renderer info, audio status, and warning count.
- [ ] **AC-13:** During rendering, a progress bar updates on stderr showing spinner, percentage, current/total frames, and estimated remaining time. The progress bar is suppressed when stderr is not a TTY.

### Render Command — Error Path

- [ ] **AC-14:** A `MANIFEST_INVALID` orchestrator error prints all validation errors to stderr in the same format as the `validate` command, and exits with code 1.
- [ ] **AC-15:** A non-validation orchestrator error (e.g., `ENCODE_FAILED`) prints the error code, message, and (if `--verbose`) the cause chain to stderr, and exits with code 1.
- [ ] **AC-16:** Invalid CLI argument values (e.g., `--fps -5`, `--crf 60`, `--gpu banana`) print a descriptive error and exit with code 1, before any manifest loading.
- [ ] **AC-17:** A non-existent manifest file path prints `"Manifest file not found: <path>"` and exits with code 1.

### Preview Command

- [ ] **AC-18:** `depthkit preview manifest.json` validates the manifest. If valid, attempts to start the preview server. If the preview server module is not available, prints an informational message and exits with code 0.
- [ ] **AC-19:** `depthkit preview invalid-manifest.json` prints validation errors and exits with code 1 (same as `validate`).

### SIGINT Handling

- [ ] **AC-20:** Pressing Ctrl+C during a render triggers graceful cancellation. The orchestrator's `CANCELLED` error is caught, partial files are cleaned up (per OBJ-035), and the process exits with code 1 and message `"Render cancelled."`.
- [ ] **AC-21:** Pressing Ctrl+C twice force-kills the process immediately.

### Output Formatting

- [ ] **AC-22:** All stderr error output uses red coloring (when color is enabled). Success uses green. Warnings use yellow.
- [ ] **AC-23:** `--no-color` suppresses all ANSI escape codes in both stdout and stderr output.
- [ ] **AC-24:** Progress bar format includes a spinner (Braille dot characters cycling based on frame number), visual bar, percentage, frame counter, and ETA.

### Assets Dir

- [ ] **AC-25:** When `--assets-dir` is not specified, relative image paths in the manifest are resolved against the manifest file's parent directory.
- [ ] **AC-26:** When `--assets-dir /custom/path` is specified, relative image paths resolve against `/custom/path`.

### Registry Initialization

- [ ] **AC-27:** Both `render` and `validate` commands use the same registry population logic. A geometry or camera available to `validate` is also available to `render`.
- [ ] **AC-28:** If no geometries are registered (empty registry), `validate` reports `UNKNOWN_GEOMETRY` for every scene — it does not crash.

### Debug Mode

- [ ] **AC-29:** `depthkit render manifest.json --debug` produces verbose output (same as `--verbose`) plus headless browser console messages on stderr.

### Testability

- [ ] **AC-30:** `createProgram()` returns a Commander program with `exitOverride()` enabled. Programmatic invocation via `createProgram().parseAsync([...])` does not call `process.exit()` — it throws `CommanderError` instead.

## Edge Cases and Error Handling

### CLI Argument Edge Cases

| Scenario | Expected Behavior |
|---|---|
| `--width 0` or `--width -1` | Error: "Width must be a positive integer." Exit code 1. |
| `--fps 0` or `--fps 200` | Error: "FPS must be an integer between 1 and 120." Exit code 1. |
| `--crf -1` or `--crf 52` | Error: "CRF must be between 0 and 51." Exit code 1. |
| `--gpu invalid` | Error: "GPU mode must be one of: software, hardware, auto." Exit code 1. |
| `--preset invalid` | Error: "Encoding preset must be one of: ultrafast, superfast, ..." Exit code 1. |
| `--output` pointing to a read-only directory | FFmpeg fails -> `ENCODE_FAILED`. Orchestrator error formatted and printed. Exit code 1. |
| Manifest path is a directory, not a file | `loadManifestFromFile()` returns `FILE_READ_ERROR`. Formatted and printed. Exit code 1. |
| Manifest file is valid JSON but not a valid manifest | Validation errors listed. Exit code 1. |
| Manifest file is not valid JSON | `INVALID_JSON` error. Exit code 1. |
| `-W` without `-H` (or vice versa) | Allowed. Only the specified dimension is overridden; the other comes from the manifest. |
| `-h` flag | Commander treats this as `--help`, not `--height`. This is correct — `--height` uses `-H`. |

### Runtime Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Render succeeds but output file is 0 bytes | Summary prints "0 B" for file size. No special handling. |
| Very long render (>1 hour) | Duration formats as "1h 12m 45s". Progress bar ETA formats similarly. |
| Very short render (<1 second) | Duration formats as "0.8s" or "845ms". |
| SIGINT during validation (before render starts) | Process exits immediately (validation is synchronous and fast). |
| SIGINT during audio mux phase | Orchestrator handles cleanup per OBJ-035. CLI catches the `CANCELLED` error. |
| Orchestrator throws an unexpected non-OrchestratorError | Caught by a top-level handler. Prints "Unexpected error: <message>". If `--verbose`, includes stack trace. Exit code 1. |
| Multiple `-W` flags (e.g., `-W 1080 -W 720`) | Commander takes the last value. Standard behavior. |

### Output Formatting Edge Cases

| Scenario | Expected Behavior |
|---|---|
| No audio in manifest | Summary omits the "Audio: ..." line (non-verbose) or shows "Audio: none" (verbose). |
| 0 warnings | Verbose summary shows "Warnings: 0". Non-verbose omits. |
| 50+ validation errors | All errors are printed. No truncation. |
| Very long file paths in error messages | Not truncated. Terminal wrapping handles it. |
| Unicode in manifest file paths | Handled natively by Node.js fs module. No special treatment. |

## Test Strategy

### Unit Tests: `test/unit/cli/format.test.ts`

1. **formatRenderResult — non-verbose:** Given an `OrchestratorResult` with known values, verify the output matches the expected format with frame count, duration, resolution, fps, avg frame time, and file size.

2. **formatRenderResult — verbose:** Same result, verify extended output includes scene count, geometry types, WebGL info, audio status, warnings.

3. **formatRenderResult — no audio:** Verify the "Audio" line is omitted (non-verbose) or shows "none" (verbose) when `audioResult` is null.

4. **formatValidationSuccess — no warnings:** Verify output includes scene count, total duration, geometry summary, camera summary.

5. **formatValidationSuccess — with warnings:** Verify warnings are listed with warning prefix and error codes.

6. **formatValidationErrors:** Given 3 `ManifestError` objects, verify each is formatted with error prefix, path, message, and code.

7. **formatOrchestratorError — MANIFEST_INVALID:** Verify validation errors are listed.

8. **formatOrchestratorError — ENCODE_FAILED, verbose:** Verify cause chain is included.

9. **formatProgress:** Given progress at 48%, verify the single-line output contains a spinner, bar, percentage, frame counter, and ETA.

10. **formatProgress — 0%:** First frame. ETA shows "calculating...".

11. **formatProgress — 100%:** Last frame. ETA shows "0s".

12. **formatFileSize:** Test bytes, KB, MB, GB boundaries.

13. **formatDuration:** Test ms, seconds, minutes, hours boundaries.

14. **Color disabled:** All format functions with `color: false` produce strings with no ANSI escape sequences.

### Unit Tests: `test/unit/cli/registry-init.test.ts`

15. **initRegistries returns populated bundle:** Verify `manifestRegistry.geometries.size > 0`, `manifestRegistry.cameras.size > 0`, and both spatial registries are non-empty.

16. **Geometry conversion:** Verify a `SceneGeometry` is correctly converted to `GeometryRegistration` — `required` and `description` are preserved, spatial data (position, rotation, size) is not present in the `GeometryRegistration`.

17. **Camera conversion:** Verify a `CameraPathPreset` is correctly converted to `CameraRegistration` — `supportsFovAnimation` is true when `fovRange[0] !== fovRange[1]`.

18. **Idempotent:** Calling `initRegistries()` twice returns equivalent registries (same keys, same values).

### Integration Tests: `test/integration/cli.test.ts`

These use `createProgram().parseAsync()` for speed, or spawn the CLI as a child process where needed.

19. **render — success:** Create a minimal valid manifest with a test geometry and a solid-color test image. Run `depthkit render manifest.json -o output.mp4`. Verify exit code 0, stdout contains "Rendered", output file exists.

20. **render — invalid manifest:** Run `depthkit render broken.json`. Verify exit code 1, stderr contains error code.

21. **render — missing file:** Run `depthkit render nonexistent.json`. Verify exit code 1, stderr contains "not found".

22. **validate — valid:** Run `depthkit validate manifest.json`. Verify exit code 0, stdout contains "valid".

23. **validate — invalid:** Run `depthkit validate broken.json`. Verify exit code 1, stderr contains errors.

24. **validate — warnings:** Run `depthkit validate manifest-with-warnings.json`. Verify exit code 0, stdout contains both success and warning messages.

25. **render — resolution override:** Run with `-W 320 -H 240 --fps 10`. Verify output MP4 is 320x240 via ffprobe.

26. **render — assets-dir:** Create a manifest with `./images/bg.png`, images in a separate directory. Run with `--assets-dir <dir>`. Verify render succeeds.

27. **render — default assets-dir:** Run without `--assets-dir`. Verify images are resolved relative to the manifest's parent directory.

28. **help output:** Run `depthkit --help`. Verify output lists `render`, `validate`, `preview` commands.

29. **version output:** Run `depthkit --version`. Verify it prints a semver string.

30. **invalid arguments:** Run `depthkit render manifest.json --fps -5`. Verify exit code 1, stderr contains "FPS must be".

31. **no-color:** Run `depthkit render manifest.json --no-color`. Verify stdout/stderr contain no ANSI escape codes (`\x1b[` not present).

32. **preview — stub:** Run `depthkit preview manifest.json`. If preview module is absent, verify exit code 0 and informational message.

33. **debug mode:** Run `depthkit render manifest.json --debug`. Verify verbose output is present (debug implies verbose).

34. **createProgram exitOverride:** Call `createProgram().parseAsync(['render'])` with no manifest. Verify `CommanderError` is thrown (not `process.exit()`), with `exitCode` of 2.

### Relevant Testable Claims

- **TC-04:** Tests 19, 22 verify that the CLI (using geometry names and slot keys) produces correct output.
- **TC-07:** Tests 20, 23 verify manifest validation catches errors via the CLI path.
- **TC-11:** All integration tests can run with default `--gpu software` (software WebGL).

## Integration Points

### Depends on

| Dependency | What OBJ-046 uses |
|---|---|
| **OBJ-035** (Orchestrator) | `Orchestrator` class, `OrchestratorConfig`, `OrchestratorResult`, `OrchestratorError`, `OrchestratorErrorCode`, `RenderProgress`, `renderFromFile()`. |
| **OBJ-004** (Manifest Schema) | `Manifest`, `ManifestError`, `ManifestRegistry`, `createRegistry()`, `GeometryRegistration`, `CameraRegistration`, `PlaneSlotDef`. |
| **OBJ-016** (Manifest Loader) | `loadManifestFromFile()`, `loadManifest()`, `computeTotalDuration()`. |
| **OBJ-005** (Geometry Registry) | `GeometryRegistry`, `SceneGeometry`, `getGeometryRegistry()`, `registerGeometry()`. Imported transitively by `registry-init.ts`. |
| **OBJ-006** (Camera Registry) | `CameraPathRegistry`, `CameraPathPreset`. The camera registry type and `getCameraPath()` function. |
| **OBJ-018–025** (Individual Geometries) | Imported statically by `registry-init.ts` for their `registerGeometry()` side effects. |
| **OBJ-026–034** (Individual Camera Presets) | Imported statically by `registry-init.ts` to assemble the `CameraPathRegistry`. |

### Consumed by

| Downstream | How it uses OBJ-046 |
|---|---|
| **OBJ-050** (Preview Server Integration) | The preview command stub will be connected to the actual preview server when OBJ-050 is implemented. |
| **OBJ-070** (SKILL.md) | Documents CLI usage, command syntax, and examples for LLM authors and human operators. |
| **OBJ-075** (n8n HTTP Interface) | May invoke the CLI as a subprocess, or may use the programmatic API directly (via `Orchestrator`). The CLI provides a tested, validated entry path. |
| **OBJ-077** (End-to-End Integration) | Uses the CLI or `createProgram()` to run full pipeline tests. |

### File Placement

```
depthkit/
  src/
    cli.ts                      # NEW — Main CLI entry point (#!/usr/bin/env node),
                                #       Commander setup, command handlers, createProgram()
    cli/
      format.ts                 # NEW — Output formatting (render result, validation,
                                #       progress, errors)
      colors.ts                 # NEW — Minimal ANSI color utilities (red, green, yellow,
                                #       cyan, bold, dim; gated by color flag)
      registry-init.ts          # NEW — Registry population bridge (static imports of
                                #       all geometry + camera modules, registry assembly)
  test/
    unit/
      cli/
        format.test.ts          # NEW — Format function unit tests
        registry-init.test.ts   # NEW — Registry initialization unit tests
    integration/
      cli.test.ts               # NEW — CLI integration tests
```

The `package.json` `bin` field:
```json
{
  "bin": {
    "depthkit": "./dist/cli.js"
  }
}
```

The compiled `dist/cli.js` must begin with `#!/usr/bin/env node`. This is typically ensured by including the shebang as the first line in `src/cli.ts` (TypeScript preserves leading comments when `removeComments` is false, or a build step prepends it).

## Open Questions

### OQ-A: Should the CLI support `--quiet` mode?

A `--quiet` flag that suppresses all output except errors could be useful for scripted pipelines. Not specified for V1.

### OQ-B: Should `validate` check image file existence?

Currently `validate` runs OBJ-016's two-phase validation, which does not check whether image files exist on disk. Adding a `--check-assets` flag would require extracting the image path resolution logic from the orchestrator into a shared utility.

### OQ-C: Should the render command support `--dry-run`?

A `--dry-run` that validates and computes frame count without rendering. Strictly a superset of `validate` with additional computation.

### OQ-D: Should progress be emitted as JSON for machine consumption?

A `--json` flag emitting newline-delimited JSON progress. Deferred — OBJ-075 may use the programmatic API.

### OQ-E: Should the CLI read environment variables for defaults?

E.g., `DEPTHKIT_FFMPEG_PATH`, `DEPTHKIT_GPU_MODE`. Commander supports `.env()` on options. Low priority.

### OQ-F: CameraParams.offset discrepancy between OBJ-004 and OBJ-006

OBJ-004's `CameraParamsSchema` does not include an `offset` field, while OBJ-006's `CameraParams` type does. This is a cross-objective discrepancy not caused by OBJ-046. The CLI passes through whatever the manifest contains — if `offset` is present in the JSON, Zod's behavior depends on whether `CameraParamsSchema` uses `.strict()` or `.passthrough()`. This should be resolved between OBJ-004 and OBJ-006 directly.
