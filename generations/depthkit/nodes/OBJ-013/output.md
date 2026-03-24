# Specification: OBJ-013 — FFmpeg Encoder

## Summary

OBJ-013 implements the FFmpeg encoding module (`src/engine/ffmpeg-encoder.ts`) — the final stage of the rendering pipeline that receives raw pixel buffers via its API, pipes them to an FFmpeg child process over stdin, and produces an H.264-encoded MP4 file. This module is deliberately independent of Puppeteer: it accepts `Buffer` data from any source, making it testable in isolation and reusable if the frame-capture mechanism changes. It implements the encoding half of constraint C-02 and supports the determinism guarantee of C-05.

Audio muxing is **out of scope** — that is OBJ-014's responsibility. This module produces a video-only MP4.

## Interface Contract

```typescript
// src/engine/ffmpeg-encoder.ts

/**
 * Supported input pixel formats for frame data piped to FFmpeg.
 * - 'png': Each frame is a complete PNG-encoded buffer. FFmpeg uses `image2pipe` demuxer.
 * - 'rgba': Each frame is raw RGBA pixel data (width * height * 4 bytes). FFmpeg uses `rawvideo` input.
 */
export type FrameFormat = 'png' | 'rgba';

/**
 * H.264 encoding preset. Controls the speed/quality/filesize tradeoff.
 * Maps directly to FFmpeg's `-preset` flag.
 */
export type H264Preset =
  | 'ultrafast' | 'superfast' | 'veryfast' | 'faster'
  | 'fast' | 'medium' | 'slow' | 'slower' | 'veryslow';

/**
 * Configuration for the FFmpeg encoder.
 */
export interface FFmpegEncoderConfig {
  /** Output file path for the MP4. Must be writable. Parent directory must exist. */
  outputPath: string;

  /** Frame width in pixels. */
  width: number;

  /** Frame height in pixels. */
  height: number;

  /**
   * Frames per second. Sets FFmpeg's input framerate. No output -r flag is set,
   * so output framerate equals input framerate — preserving 1:1 frame correspondence (C-03).
   */
  fps: number;

  /**
   * Input frame format. Default: 'png'.
   * - 'png': frames are PNG buffers piped via image2pipe. Self-describing, simpler.
   * - 'rgba': frames are raw RGBA buffers. Faster, requires exact buffer sizes.
   */
  frameFormat?: FrameFormat;

  /** H.264 encoding preset. Default: 'medium'. */
  preset?: H264Preset;

  /**
   * Constant Rate Factor (0-51). Lower = higher quality, larger file. Default: 23.
   * 18-23 is visually lossless for most content.
   */
  crf?: number;

  /**
   * Output pixel format. Default: 'yuv420p'.
   * Passed directly to FFmpeg's -pix_fmt flag. Invalid values will surface as
   * FFmpegEncoderError from FFmpeg's stderr — no encoder-side validation is performed.
   */
  pixelFormat?: string;

  /**
   * If true, forces single-threaded encoding (-threads 1) for byte-identical
   * video stream output across runs. Container metadata (creation timestamps,
   * encoder version strings) may still differ between runs. For C-05's
   * "byte-identical or visually indistinguishable" requirement, the default
   * multithreaded mode produces visually indistinguishable output, which
   * satisfies the constraint. Default: false.
   */
  deterministic?: boolean;

  /**
   * Optional path to FFmpeg binary. If not provided, resolves via resolveFFmpegPath().
   */
  ffmpegPath?: string;
}

/**
 * Result returned when encoding completes successfully.
 */
export interface FFmpegEncoderResult {
  /** Absolute path to the output MP4 file. */
  outputPath: string;

  /** Total number of frames written. */
  frameCount: number;

  /** Total encoding duration in milliseconds (wall-clock time from start() to finalize()). */
  durationMs: number;

  /** FFmpeg's stderr output (contains encoding stats, warnings). Capped at last 1MB. */
  ffmpegLog: string;
}

/**
 * Custom error class for FFmpeg encoding failures.
 * Contains the FFmpeg stderr log for diagnosis.
 */
export class FFmpegEncoderError extends Error {
  constructor(
    message: string,
    public readonly exitCode: number | null,
    public readonly ffmpegLog: string,
    public readonly framesWritten: number,
  ) {
    super(message);
    this.name = 'FFmpegEncoderError';
  }
}

/**
 * The FFmpeg encoder. Manages a single FFmpeg child process for one video encode.
 *
 * Lifecycle:
 *   const encoder = new FFmpegEncoder(config);
 *   await encoder.start();
 *   for each frame:
 *     await encoder.writeFrame(buffer);
 *   const result = await encoder.finalize();
 *
 * Not reusable — one encoder instance per output file.
 */
export class FFmpegEncoder {
  constructor(config: FFmpegEncoderConfig);

  /**
   * Spawns the FFmpeg child process via child_process.spawn().
   * Resolves once the child process is spawned and stdin is writable.
   *
   * IMPORTANT: start() succeeding does NOT guarantee encoding will succeed.
   * Invalid FFmpeg arguments (e.g., bad codec name) may only surface at
   * writeFrame() or finalize() after the process exits with an error.
   *
   * Throws FFmpegEncoderError if:
   * - FFmpeg binary cannot be found (via resolveFFmpegPath())
   * - The child process fails to spawn (ENOENT, EACCES, etc.)
   * - start() has already been called on this instance
   */
  start(): Promise<void>;

  /**
   * Writes a single frame's pixel data to FFmpeg's stdin.
   *
   * Handles backpressure: if stream.write() returns false (FFmpeg's stdin
   * buffer is full), awaits the 'drain' event before resolving.
   *
   * NOT safe to call concurrently. The orchestrator's deterministic frame
   * loop (C-03) guarantees sequential calls. Concurrent calls produce
   * undefined behavior (interleaved frame data).
   *
   * Throws FFmpegEncoderError if:
   * - start() has not been called
   * - finalize() has already been called
   * - FFmpeg process has exited unexpectedly (checked before write)
   * - For 'rgba' format: buffer size !== width * height * 4
   */
  writeFrame(data: Buffer): Promise<void>;

  /**
   * Closes FFmpeg's stdin and waits for the process to exit.
   * Returns the encoding result on success.
   * Throws FFmpegEncoderError if FFmpeg exits with a non-zero code.
   */
  finalize(): Promise<FFmpegEncoderResult>;

  /**
   * Kills the FFmpeg process immediately (SIGKILL) and cleans up.
   * Idempotent — safe to call multiple times or after finalize().
   * Does NOT delete the partial output file at outputPath.
   * Cleanup of partial files is the caller's responsibility.
   */
  abort(): void;

  /** Number of frames successfully written so far. */
  readonly framesWritten: number;

  /** Whether the encoder is currently active (started and not finalized/aborted). */
  readonly isActive: boolean;
}

/**
 * Resolves the FFmpeg binary path. Tries in order:
 * 1. Explicit path (if provided)
 * 2. FFMPEG_PATH environment variable
 * 3. ffmpeg-static package (ESM import — see D-10)
 * 4. 'ffmpeg' (assumes it's on system PATH)
 *
 * Validates the resolved path by spawning `ffmpeg -version` via
 * child_process.spawn() and checking exit code 0.
 * Throws FFmpegEncoderError if no working FFmpeg binary is found.
 */
export function resolveFFmpegPath(explicitPath?: string): Promise<string>;
```

## Design Decisions

### D-01: Class-Based Lifecycle over Streaming API
**Choice:** `FFmpegEncoder` class with explicit `start()` -> `writeFrame()` -> `finalize()` lifecycle.
**Rationale:** The orchestrator (OBJ-035) needs precise control over the FFmpeg process: start it before the frame loop, write frames one at a time in the deterministic render loop, and finalize after the last frame. A Node.js `Writable` stream interface was considered but rejected because it obscures lifecycle semantics and makes error handling at frame boundaries more complex. The explicit lifecycle maps directly to the frame loop in seed Section 4.4.

### D-02: Normative FFmpeg Argument Arrays
**Choice:** The following are the **complete, definitive** argument arrays for each format. Every flag is included. An implementer must construct these arrays exactly, substituting config values where indicated.

**PNG input format:**
```
ffmpeg
  -y                              # Overwrite output without prompting (D-06)
  -f image2pipe                   # Input demuxer: reads images from stdin
  -framerate {fps}                # Input framerate (no output -r flag; output matches input)
  -i pipe:0                       # Read from stdin
  -c:v libx264                    # H.264 video codec
  -preset {preset}                # Encoding speed/quality tradeoff (default: 'medium')
  -crf {crf}                      # Quality (default: 23)
  -pix_fmt {pixelFormat}          # Output pixel format (default: 'yuv420p')
  -movflags +faststart            # Move moov atom for web progressive playback (D-07)
  [-threads 1]                    # ONLY when deterministic: true (D-09)
  {outputPath}                    # Output MP4 file path
```

**RGBA input format:**
```
ffmpeg
  -y
  -f rawvideo                     # Input is raw pixel data
  -pix_fmt rgba                   # Input pixel format: RGBA, 4 bytes per pixel
  -s {width}x{height}             # Input frame dimensions (required for rawvideo)
  -framerate {fps}                # Input framerate
  -i pipe:0                       # Read from stdin
  -c:v libx264
  -preset {preset}
  -crf {crf}
  -pix_fmt {pixelFormat}          # Output pixel format (default: 'yuv420p')
  -movflags +faststart
  [-threads 1]                    # ONLY when deterministic: true
  {outputPath}
```

**Critical invariant:** No output `-r` flag is set. Output framerate equals input framerate. This preserves the 1:1 frame correspondence required by C-03. If input and output rates mismatch, FFmpeg interpolates frames, violating deterministic frame-by-frame rendering.

### D-03: Backpressure via Drain Events
**Choice:** `writeFrame()` returns a Promise. Internally, it calls `stream.write(data)`. If `write()` returns `false` (buffer full), the Promise awaits the `drain` event before resolving.
**Rationale:** Prevents unbounded memory growth when the orchestrator produces frames faster than FFmpeg can encode. Critical for the 1,800-frame renders described in C-08.

### D-04: Video-Only Output, Audio Muxing Deferred to OBJ-014
**Choice:** OBJ-013 produces a video-only MP4 (no audio stream).
**Rationale:** The seed mentions "Audio is muxed in a final FFmpeg pass." Separating video encoding from audio muxing keeps OBJ-013 focused and testable. OBJ-014 can remux with `-c copy` (cheap) or modify the encoder to accept a second input.

### D-05: FFmpeg Binary Resolution Order
**Choice:** Explicit path -> `FFMPEG_PATH` env -> `ffmpeg-static` -> system PATH.
**Rationale:** Matches OBJ-001's D-04 decision. Validation via `ffmpeg -version` confirms the binary works.

### D-06: `-y` Flag (Overwrite Without Prompting)
**Choice:** Always pass `-y` to FFmpeg.
**Rationale:** FFmpeg prompts on stdin if the output file exists, which deadlocks the pipe. The caller is responsible for choosing output paths.

### D-07: `-movflags +faststart` for Web Playback
**Choice:** Always include `-movflags +faststart`.
**Rationale:** Moves the MP4 moov atom to the beginning of the file, enabling progressive playback in web browsers. Required for SC-01.

### D-08: CRF 23 Default
**Choice:** Default CRF of 23, configurable via `crf` option.
**Rationale:** FFmpeg's own default for libx264. Visually good quality with reasonable file size.

### D-09: Deterministic Encoding Flag
**Choice:** Optional `deterministic: boolean` flag. When true, adds `-threads 1` to the argument array. Default: false (multithreaded for speed).
**Rationale:** C-05 requires "byte-identical (or visually indistinguishable)" output. Multithreaded libx264 can introduce non-determinism from thread scheduling, but the output is visually indistinguishable. The parenthetical in C-05 permits this. The `deterministic` flag exists for cases where byte-identical video streams are required (e.g., TC-06 verification). **Note:** Container-level metadata (creation timestamps, encoder version strings) may still differ between runs regardless of this flag.

### D-10: ESM Import of ffmpeg-static
**Choice:** Import `ffmpeg-static` via `import ffmpegStatic from 'ffmpeg-static'` (ESM default import). If the installed version of `ffmpeg-static` does not support ESM default export, use `import { createRequire } from 'node:module'; const require = createRequire(import.meta.url); const ffmpegPath = require('ffmpeg-static');` as a fallback.
**Rationale:** OBJ-001 mandates `"type": "module"` (ESM). `require()` is not available in ESM without `createRequire`. The implementer must verify which mechanism works with the installed `ffmpeg-static` version.

### D-11: child_process.spawn() with Array Arguments
**Choice:** Use `child_process.spawn()` with arguments as an array, not `exec()` with a shell string.
**Rationale:** `spawn()` does not invoke a shell, avoiding argument injection risks and path-with-spaces issues. The `outputPath` from the manifest may contain spaces, parentheses, or Unicode characters — `spawn()` handles these correctly.

### D-12: start() Resolution Semantics
**Choice:** `start()` resolves once `child_process.spawn()` returns and the child process's stdin is confirmed writable (i.e., the `spawn` event fires without error). It does **not** wait for FFmpeg to parse arguments or write its banner to stderr.
**Rationale:** Parsing stderr for "FFmpeg started successfully" is fragile and version-dependent. Argument validation errors surface naturally when the process exits with a non-zero code, which is detected at the next `writeFrame()` or at `finalize()`. This is simpler and avoids timing races.

**Consequence for consumers:** `start()` succeeding means "FFmpeg process is spawned." It does not mean "FFmpeg arguments are valid" or "encoding will succeed." Errors from invalid arguments will appear as `FFmpegEncoderError` from `writeFrame()` or `finalize()`.

### D-13: abort() Does Not Delete Partial Output
**Choice:** `abort()` kills the FFmpeg process but does **not** delete the partial/corrupted output file at `outputPath`.
**Rationale:** Cleanup of partial files is the caller's responsibility. The orchestrator (OBJ-035) is in a better position to decide whether to delete, retry, or preserve for debugging.

## Acceptance Criteria

- [ ] **AC-01:** `FFmpegEncoder` class and `resolveFFmpegPath` function are exported from `src/engine/ffmpeg-encoder.ts` with the interfaces defined above.
- [ ] **AC-02:** `resolveFFmpegPath()` returns a valid path when `ffmpeg-static` is installed and no explicit path or env var is set.
- [ ] **AC-03:** `resolveFFmpegPath()` throws `FFmpegEncoderError` with message containing "FFmpeg binary not found" when no FFmpeg binary can be found.
- [ ] **AC-04:** Writing 30 solid-color PNG frames (1920x1080) at 30fps via `writeFrame()` and calling `finalize()` produces a valid MP4 that `ffprobe` reports as: H.264 codec, 1920x1080, ~1 second duration, yuv420p pixel format.
- [ ] **AC-05:** Writing frames in `rgba` format with buffers of exactly `width * height * 4` bytes produces a valid MP4 with the same codec, resolution, and pixel format properties.
- [ ] **AC-06:** `writeFrame()` rejects with `FFmpegEncoderError` when called before `start()`.
- [ ] **AC-07:** `writeFrame()` rejects with `FFmpegEncoderError` when called after `finalize()`.
- [ ] **AC-08:** For `rgba` format, `writeFrame()` rejects with `FFmpegEncoderError` if the buffer size is not exactly `width * height * 4` bytes. Error message includes expected and actual sizes.
- [ ] **AC-09:** `finalize()` returns an `FFmpegEncoderResult` with correct `frameCount`, non-zero `durationMs`, the `outputPath` matching the config, and non-empty `ffmpegLog`.
- [ ] **AC-10:** If FFmpeg exits with a non-zero code, `finalize()` rejects with `FFmpegEncoderError` containing the exit code and FFmpeg's stderr log.
- [ ] **AC-11:** `abort()` kills the FFmpeg process, is idempotent, and does not delete the partial output file.
- [ ] **AC-12:** Backpressure is handled: when `stream.write()` returns false, `writeFrame()` awaits `drain` before resolving.
- [ ] **AC-13:** The output MP4 includes `-movflags +faststart` (verifiable via `ffprobe -v quiet -show_format` — `format_name` should be `mov,mp4` and the moov atom should precede mdat).
- [ ] **AC-14:** The encoder works with both `1920x1080` and `1080x1920` resolutions (C-04).
- [ ] **AC-15:** `resolveFFmpegPath()` respects the `FFMPEG_PATH` environment variable, using it in preference to `ffmpeg-static`.
- [ ] **AC-16:** FFmpeg is spawned via `child_process.spawn()` with arguments as an array, not via a shell string.
- [ ] **AC-17:** The FFmpeg argument array matches D-02's normative specification exactly (all flags present, correct order of input/output options).

## Edge Cases and Error Handling

1. **FFmpeg not found:** `resolveFFmpegPath()` attempts all four sources in order. If none produce a working binary (validated via `ffmpeg -version` with `spawn()`), throws `FFmpegEncoderError` with message: `"FFmpeg binary not found. Install ffmpeg-static, set FFMPEG_PATH, or ensure ffmpeg is on your system PATH."`.

2. **FFmpeg process crashes mid-encode:** The encoder listens for the child process `error` and `close` events. If FFmpeg exits unexpectedly, a flag is set and the next `writeFrame()` call rejects with `FFmpegEncoderError` containing the exit code and accumulated stderr. `isActive` returns `false` immediately upon unexpected exit.

3. **Output path not writable / parent directory missing:** FFmpeg fails with a stderr message. The encoder does **not** create parent directories. The error surfaces as `FFmpegEncoderError` from `finalize()` (or `writeFrame()` if FFmpeg exits immediately). The error includes FFmpeg's stderr for diagnosis.

4. **Zero frames written:** If `finalize()` is called without any `writeFrame()` calls, FFmpeg exits with an error. Surfaced as `FFmpegEncoderError`: `"FFmpeg exited with code {N}: no frames were written before finalize()."`.

5. **Corrupted PNG data:** Invalid PNG data in `png` mode causes FFmpeg's `image2pipe` demuxer to fail. The encoder does **not** validate PNG structure. The error surfaces via `FFmpegEncoderError` at `finalize()` with FFmpeg's stderr.

6. **Wrong-sized RGBA buffer:** `writeFrame()` validates `data.length === width * height * 4` before writing. Rejects immediately: `"RGBA frame buffer size mismatch: expected {expected} bytes ({width}x{height}x4), got {actual}."`.

7. **Stderr buffer cap:** FFmpeg stderr is accumulated in memory. The buffer is capped at 1MB, retaining the **last** 1MB of output (ring buffer or truncation of older content). This prevents OOM for multi-hour encodes while preserving the most diagnostic (most recent) output.

8. **Concurrent writeFrame calls:** Not safe. The orchestrator's deterministic frame loop (C-03) guarantees sequential calls. Concurrent calls produce undefined behavior (interleaved frame data). Documented on the method, not enforced with internal locking.

9. **Double start():** Throws `FFmpegEncoderError`: `"Encoder already started. Create a new FFmpegEncoder instance for a new encode."`.

10. **Platform-specific pixel format:** The `-pix_fmt yuv420p` default ensures consistent output. Without it, FFmpeg may default to `yuv444p` on some inputs, which is incompatible with many players.

11. **`ffmpeg-static` ESM import failure:** If the default ESM import fails, fall back to `createRequire`. If both fail (package not installed), proceed to the system PATH fallback. Do not throw until all four sources are exhausted.

## Test Strategy

### Unit Tests (`test/unit/ffmpeg-encoder.test.ts`)

1. **FFmpeg path resolution:**
   - `resolveFFmpegPath()` returns a valid path when `ffmpeg-static` is installed.
   - `resolveFFmpegPath()` prefers `FFMPEG_PATH` env var when set (set env, call, verify returned path matches env value, restore env).
   - `resolveFFmpegPath()` throws `FFmpegEncoderError` when no FFmpeg is available (requires mocking — may be better as an integration test with a controlled environment).

2. **Lifecycle guards:**
   - `writeFrame()` before `start()` rejects with `FFmpegEncoderError`.
   - `writeFrame()` after `finalize()` rejects with `FFmpegEncoderError`.
   - Double `start()` throws `FFmpegEncoderError`.
   - `abort()` is idempotent (call twice, no throw).
   - `isActive` is false before `start()`, true after `start()`, false after `finalize()`, false after `abort()`.

3. **RGBA buffer size validation:**
   - Correctly-sized buffer (1920x1080x4 = 8,294,400 bytes) does not throw the size error.
   - Incorrectly-sized buffer rejects with error message containing expected and actual sizes.

### Integration Tests (`test/integration/ffmpeg-encoder.test.ts`)

These spawn real FFmpeg processes. Require FFmpeg available via `ffmpeg-static` or system install.

**PNG buffer creation for tests:** Construct minimal valid PNG buffers using Node.js `Buffer` and `zlib`. A single-color PNG is a well-documented format: 8-byte signature, IHDR chunk (13 bytes data), IDAT chunk (deflated scanlines), IEND chunk. No additional devDependency required.

4. **PNG encode pipeline:** Create 30 solid-color PNG frames (1920x1080). Write via encoder at 30fps. Verify output exists and `ffprobe` reports: H.264, 1920x1080, ~1s duration, yuv420p.

5. **RGBA encode pipeline:** Create 30 raw RGBA buffers (1920x1080x4 bytes, solid blue). Write via encoder. Verify with `ffprobe`.

6. **Portrait mode (9:16):** 30 frames at 1080x1920. Verify `ffprobe` reports 1080x1920.

7. **Result object:** Verify `finalize()` returns `FFmpegEncoderResult` with `frameCount === 30`, `durationMs > 0`, correct `outputPath`, non-empty `ffmpegLog`.

8. **Corrupted input:** Write garbage data as "PNG" frames. Verify `finalize()` rejects with `FFmpegEncoderError` with non-zero exit code.

9. **Zero-frame encode:** `start()` then `finalize()` with no frames. Verify rejects with `FFmpegEncoderError`.

10. **Abort mid-encode:** Start, write a few frames, `abort()`. Verify `isActive` is false, no unhandled exceptions. Verify partial output file still exists on disk.

11. **Argument array verification:** Verify output MP4 properties match D-02's flags (e.g., faststart, yuv420p via `ffprobe`). Alternatively, test with a known-bad `pixelFormat` and verify the error surfaces.

**Relevant testable claims:** TC-02 (FFmpeg encoding time is part of the per-frame budget), TC-06 (with `deterministic: true`, same frames produce identical video streams).

### Performance Benchmark (Manual / CI)

12. **Throughput:** Write 1,800 solid-color PNG frames (1920x1080) at 30fps. Measure encoding time. FFmpeg should encode faster than Puppeteer's ~500ms/frame budget (TC-02), confirming it's not the bottleneck.

## Integration Points

### Depends on
- **OBJ-001** (Project scaffolding): Provides `src/engine/ffmpeg-encoder.ts` stub, `ffmpeg-static` in dependencies, TypeScript build pipeline, `"type": "module"` ESM context.

### Consumed by
- **OBJ-014** (Audio muxing): Uses `FFmpegEncoderResult.outputPath` to locate the video-only MP4 for audio muxing. May either wrap this encoder or invoke a separate FFmpeg pass.
- **OBJ-035** (Orchestrator): Primary consumer. Instantiates `FFmpegEncoder`, calls `start()` before the render loop, `writeFrame()` per frame, `finalize()` after the last frame.
- **OBJ-083** (downstream integration): Depends on OBJ-013 + OBJ-035.

### File Placement
- **Implementation:** `src/engine/ffmpeg-encoder.ts`
- **Unit tests:** `test/unit/ffmpeg-encoder.test.ts`
- **Integration tests:** `test/integration/ffmpeg-encoder.test.ts`

## Open Questions

1. **Should the encoder produce video-only MP4 or raw H.264 stream?** Current spec says MP4 because it's the final deliverable format and OBJ-014 can remux cheaply with `-c copy`. If OBJ-014 finds that remuxing MP4-to-MP4 is problematic, it may request a raw `.h264` intermediate. This is OBJ-014's decision — the current MP4 default is correct for now.

2. **Should we expose `additionalArgs?: string[]` for arbitrary FFmpeg flags?** Omitted to keep the interface focused. If OBJ-035 or OBJ-014 need custom flags, they can request this addition in a later revision.

3. **Pending drain + FFmpeg crash interaction:** If `writeFrame()` is awaiting a `drain` event when FFmpeg crashes mid-encode, the drain will never fire. The implementer should ensure that the stdin `error`/`close` event also rejects any pending `writeFrame()` promise, not just set a flag for the next call. This is standard Node.js stream error handling but is called out here to prevent a subtle hang.
