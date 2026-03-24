# Deliberation Transcript: OBJ-013

---

## Round 1 — spec_author

# Specification Proposal: OBJ-013 — FFmpeg Encoder

## Summary

OBJ-013 implements the FFmpeg encoding module (`src/engine/ffmpeg-encoder.ts`) — the final stage of the rendering pipeline that receives raw pixel buffers via its API, pipes them to an FFmpeg child process over stdin, and produces an H.264-encoded MP4 file. This module is deliberately independent of Puppeteer: it accepts `Buffer` data from any source, making it testable in isolation and reusable if the frame-capture mechanism changes. It implements the encoding half of constraint C-02 and supports the determinism guarantee of C-05.

Audio muxing is **out of scope** — that is OBJ-014's responsibility. This module produces a video-only MP4 (or a muxable intermediate stream that OBJ-014 can combine with audio).

## Interface Contract

```typescript
// src/engine/ffmpeg-encoder.ts

/**
 * Supported input pixel formats for frame data piped to FFmpeg.
 * - 'png': Each frame is a complete PNG-encoded buffer. FFmpeg uses `image2pipe` demuxer.
 * - 'rgba': Each frame is raw RGBA pixel data (width × height × 4 bytes). FFmpeg uses `rawvideo` input.
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
  /** Output file path for the MP4. Must be writable. */
  outputPath: string;

  /** Frame width in pixels. Required for 'rgba' format; used for 'png' as well for validation. */
  width: number;

  /** Frame height in pixels. Required for 'rgba' format; used for 'png' as well for validation. */
  height: number;

  /** Frames per second. Used for FFmpeg's input framerate (`-r` or `-framerate`). */
  fps: number;

  /**
   * Input frame format.
   * - 'png': frames are PNG buffers piped via image2pipe. Simpler, slightly larger per-frame data.
   * - 'rgba': frames are raw RGBA buffers. Faster throughput, requires exact buffer sizes.
   * Default: 'png'
   */
  frameFormat?: FrameFormat;

  /**
   * H.264 encoding preset. Default: 'medium'.
   * For development/testing, 'ultrafast' reduces encode time at the cost of file size.
   * For production, 'medium' or 'slow' produces better quality/size ratio.
   */
  preset?: H264Preset;

  /**
   * Constant Rate Factor (0-51). Lower = higher quality, larger file. Default: 23.
   * 18-23 is visually lossless for most content. 0 = mathematically lossless.
   */
  crf?: number;

  /**
   * Output pixel format for the encoded video. Default: 'yuv420p'.
   * 'yuv420p' is required for maximum compatibility (web browsers, mobile players).
   */
  pixelFormat?: string;

  /**
   * Optional path to FFmpeg binary. If not provided, resolves in order:
   * 1. FFMPEG_PATH environment variable
   * 2. ffmpeg-static package
   * 3. 'ffmpeg' on system PATH
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

  /** Total encoding duration in milliseconds (wall-clock). */
  durationMs: number;

  /** FFmpeg's stderr output (contains encoding stats, warnings). */
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
   * Spawns the FFmpeg child process. Must be called before writeFrame().
   * Throws FFmpegEncoderError if the process fails to spawn (e.g., FFmpeg not found).
   */
  start(): Promise<void>;

  /**
   * Writes a single frame's pixel data to FFmpeg's stdin.
   *
   * For 'png' format: `data` must be a valid PNG-encoded buffer.
   * For 'rgba' format: `data` must be exactly (width × height × 4) bytes.
   *
   * Handles backpressure: if FFmpeg's stdin buffer is full, this method
   * awaits the 'drain' event before resolving. This naturally throttles
   * the frame producer (the orchestrator) to FFmpeg's encoding speed.
   *
   * Throws FFmpegEncoderError if:
   * - start() has not been called
   * - finalize() has already been called
   * - FFmpeg process has exited unexpectedly
   * - For 'rgba' format: buffer size !== width × height × 4
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
   * Used for error recovery / abort scenarios.
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
 * 3. ffmpeg-static package (require('ffmpeg-static'))
 * 4. 'ffmpeg' (assumes it's on system PATH)
 *
 * Validates the resolved path by spawning `ffmpeg -version` and checking exit code 0.
 * Throws FFmpegEncoderError if no working FFmpeg binary is found.
 */
export function resolveFFmpegPath(explicitPath?: string): Promise<string>;
```

## Design Decisions

### D-01: Class-Based Lifecycle over Streaming API
**Choice:** `FFmpegEncoder` class with explicit `start()` → `writeFrame()` → `finalize()` lifecycle.
**Rationale:** The orchestrator (OBJ-035) needs precise control over the FFmpeg process: start it before the frame loop, write frames synchronously one at a time in the deterministic render loop, and finalize after the last frame. A Node.js `Writable` stream interface was considered but rejected because it obscures the lifecycle semantics (when does encoding actually start? when is stdin closed?) and makes error handling at specific frame boundaries more complex. The explicit lifecycle maps directly to the frame loop in seed Section 4.4 step 4.

### D-02: PNG as Default Frame Format, RGBA as Performance Option
**Choice:** Support both `png` and `rgba` input formats. Default to `png`.
**Rationale:** PNG is self-describing — FFmpeg's `image2pipe` demuxer detects frame boundaries automatically from the PNG stream. No dimension/format metadata is needed per-frame. This is simpler and more resilient. Raw RGBA is faster (no PNG encode/decode overhead) but requires exact buffer sizes and careful synchronization. Starting with PNG satisfies AP-05 (no premature optimization). The `rgba` option exists for when TC-02 performance testing reveals whether the PNG encode overhead is a bottleneck.

**FFmpeg arguments for PNG input:**
```
ffmpeg -y -f image2pipe -framerate {fps} -i pipe:0 -c:v libx264 -preset {preset} -crf {crf} -pix_fmt yuv420p {outputPath}
```

**FFmpeg arguments for RGBA input:**
```
ffmpeg -y -f rawvideo -pix_fmt rgba -s {width}x{height} -framerate {fps} -i pipe:0 -c:v libx264 -preset {preset} -crf {crf} -pix_fmt yuv420p {outputPath}
```

### D-03: Backpressure via Drain Events
**Choice:** `writeFrame()` returns a Promise that resolves when the data is flushed or when the stream's `drain` event fires after a full buffer.
**Rationale:** If the orchestrator produces frames faster than FFmpeg can encode, stdin's internal buffer fills up. Node.js `stream.write()` returns `false` when the buffer is full. The encoder must await `drain` before accepting the next frame. This naturally throttles the render loop to FFmpeg's speed, preventing unbounded memory growth. This is critical for the 1,800-frame (60s × 30fps) renders described in C-08.

### D-04: Video-Only Output, Audio Muxing Deferred to OBJ-014
**Choice:** OBJ-013 produces a video-only MP4 (no audio stream). OBJ-014 handles audio muxing.
**Rationale:** The seed's Appendix A step 5 mentions "Audio is muxed in a final FFmpeg pass (or in the same pass via a separate input stream)." Separating video encoding from audio muxing keeps OBJ-013 focused and testable in isolation. OBJ-014 can either: (a) add audio in a second FFmpeg pass (`ffmpeg -i video.mp4 -i audio.mp3 -c copy -shortest output.mp4`), or (b) modify the encoder to accept a second input. That's OBJ-014's design decision to make.

### D-05: FFmpeg Binary Resolution Order
**Choice:** Explicit path → `FFMPEG_PATH` env → `ffmpeg-static` → system PATH.
**Rationale:** Matches OBJ-001's D-04 decision. `ffmpeg-static` provides an out-of-the-box experience. The env var allows Docker/CI environments to use a pre-installed FFmpeg. System PATH is the last resort. The `resolveFFmpegPath()` function validates the binary by running `ffmpeg -version` before returning.

### D-06: `-y` Flag (Overwrite Without Prompting)
**Choice:** Always pass `-y` to FFmpeg.
**Rationale:** FFmpeg prompts on stdin if the output file exists, which would deadlock the pipe. `-y` forces overwrite. The caller (orchestrator) is responsible for choosing output paths.

### D-07: `-movflags +faststart` for Web Playback
**Choice:** Include `-movflags +faststart` in the FFmpeg arguments.
**Rationale:** Moves the MP4 moov atom to the beginning of the file, enabling progressive playback in web browsers without downloading the entire file. Required for SC-01 ("plays correctly in web browsers").

### D-08: CRF 23 Default with Override
**Choice:** Default CRF of 23, configurable via `crf` option.
**Rationale:** CRF 23 is FFmpeg's own default for libx264 — visually good quality with reasonable file size. The config allows tuning per use case (lower CRF for archival quality, higher for smaller files in the n8n pipeline).

### D-09: Deterministic Encoding for C-05
**Choice:** No multithreaded FFmpeg flags that introduce non-determinism. However, full byte-identical output requires careful consideration.
**Rationale:** C-05 requires deterministic output. libx264 with the same input frames, CRF, preset, and single-threaded encoding produces deterministic output. However, the default multithreaded encoding in libx264 can introduce non-determinism due to thread scheduling. If C-05 is strictly required at the byte level, the encoder should pass `-threads 1` when a `deterministic: true` flag is set. The default should prioritize speed (multithreaded) since C-05 says "byte-identical (or visually indistinguishable)" — the parenthetical suggests visual equivalence is acceptable.

**Decision:** Default to multithreaded encoding for speed. Document that byte-identical output requires `-threads 1` and expose this as an optional config flag (`deterministic?: boolean`). Add this to the config interface:

```typescript
/**
 * If true, forces single-threaded encoding for byte-identical output
 * across runs (C-05). Slower but deterministic. Default: false.
 */
deterministic?: boolean;
```

## Acceptance Criteria

- [ ] **AC-01:** `FFmpegEncoder` class is exported from `src/engine/ffmpeg-encoder.ts` with the interface defined above.
- [ ] **AC-02:** `resolveFFmpegPath()` is exported and correctly resolves FFmpeg from `ffmpeg-static` when no explicit path or env var is set.
- [ ] **AC-03:** `resolveFFmpegPath()` throws `FFmpegEncoderError` with a descriptive message when no FFmpeg binary can be found (e.g., `ffmpeg-static` missing and no system FFmpeg).
- [ ] **AC-04:** Writing 30 solid-color PNG frames (1920×1080) at 30fps via `writeFrame()` and calling `finalize()` produces a valid MP4 that `ffprobe` reports as: H.264 codec, 1920×1080 resolution, ~1 second duration, yuv420p pixel format.
- [ ] **AC-05:** Writing frames in `rgba` format with buffers of exactly `width × height × 4` bytes produces the same valid MP4 output as the PNG path (same resolution, codec, duration).
- [ ] **AC-06:** `writeFrame()` rejects with `FFmpegEncoderError` when called before `start()`.
- [ ] **AC-07:** `writeFrame()` rejects with `FFmpegEncoderError` when called after `finalize()`.
- [ ] **AC-08:** For `rgba` format, `writeFrame()` rejects with `FFmpegEncoderError` if the buffer size is not exactly `width × height × 4` bytes.
- [ ] **AC-09:** `finalize()` returns an `FFmpegEncoderResult` with correct `frameCount`, non-zero `durationMs`, and the `outputPath` matching the config.
- [ ] **AC-10:** If FFmpeg exits with a non-zero code during encoding, `finalize()` rejects with `FFmpegEncoderError` containing the exit code and FFmpeg's stderr log.
- [ ] **AC-11:** `abort()` kills the FFmpeg process and is idempotent (calling it multiple times does not throw).
- [ ] **AC-12:** Backpressure is handled: when FFmpeg's stdin buffer is full, `writeFrame()` awaits drain rather than buffering unboundedly in Node.js memory.
- [ ] **AC-13:** The output MP4 includes `-movflags +faststart` for web-compatible progressive playback.
- [ ] **AC-14:** The encoder works with both `1920×1080` (16:9) and `1080×1920` (9:16) resolutions, satisfying C-04.
- [ ] **AC-15:** `resolveFFmpegPath()` respects the `FFMPEG_PATH` environment variable when set, using it in preference to `ffmpeg-static`.

## Edge Cases and Error Handling

1. **FFmpeg not found:** `resolveFFmpegPath()` attempts all four sources in order. If none produce a working binary (validated via `ffmpeg -version`), throws `FFmpegEncoderError` with message: `"FFmpeg binary not found. Install ffmpeg-static, set FFMPEG_PATH, or ensure ffmpeg is on your system PATH."`.

2. **FFmpeg process crashes mid-encode:** The encoder must listen for the child process `error` and `close` events. If FFmpeg exits unexpectedly while frames are still being written, the next `writeFrame()` call must reject with an `FFmpegEncoderError` containing the exit code and accumulated stderr. The `isActive` property must reflect this state immediately.

3. **Output path not writable:** FFmpeg will fail on its own with a stderr message. The encoder surfaces this as an `FFmpegEncoderError` from `start()` or `finalize()` (depending on when FFmpeg detects the issue — some versions fail at startup, others at finalize). The error includes the FFmpeg stderr for diagnosis.

4. **Output path parent directory does not exist:** The encoder does **not** create parent directories. The caller is responsible for ensuring the output directory exists. FFmpeg's error message will be surfaced through `FFmpegEncoderError`.

5. **Zero frames written:** If `finalize()` is called without any `writeFrame()` calls, FFmpeg will likely exit with an error (no input data). The encoder surfaces this as `FFmpegEncoderError` with a clear message: `"FFmpeg exited with code {N}: no frames were written before finalize(). Ensure at least one frame is written."`.

6. **Corrupted PNG data:** If a `writeFrame()` call passes invalid PNG data in `png` mode, FFmpeg's `image2pipe` demuxer will fail. This manifests as a non-zero exit code at `finalize()`. The encoder does **not** validate PNG structure — that's FFmpeg's job. The error is surfaced via `FFmpegEncoderError` with FFmpeg's stderr.

7. **Wrong-sized RGBA buffer:** For `rgba` format, `writeFrame()` validates `data.length === width * height * 4` before writing. Rejects immediately with `FFmpegEncoderError`: `"RGBA frame buffer size mismatch: expected {expected} bytes (${width}×${height}×4), got {actual}."`.

8. **Very long videos (memory):** FFmpeg stderr is accumulated in memory for the `ffmpegLog` field. For very long encodes, stderr could grow large. The encoder should cap the stderr buffer at 1MB, keeping the last 1MB of output. This prevents OOM for multi-hour encodes while preserving the most recent (and most diagnostic) output.

9. **Concurrent writeFrame calls:** `writeFrame()` is not safe to call concurrently. The orchestrator's deterministic frame loop (C-03) guarantees sequential calls. The encoder does not need internal locking but should document this constraint. If called concurrently, behavior is undefined (frames may interleave).

10. **Double start():** Calling `start()` on an already-started encoder throws `FFmpegEncoderError`: `"Encoder already started. Create a new FFmpegEncoder instance for a new encode."`.

11. **Platform-specific FFmpeg behavior:** The `-pix_fmt yuv420p` flag ensures consistent output across platforms. Without it, FFmpeg may default to `yuv444p` on some inputs, which is incompatible with many players.

## Test Strategy

### Unit Tests (`test/unit/ffmpeg-encoder.test.ts`)

1. **FFmpeg path resolution:**
   - Test that `resolveFFmpegPath()` returns a valid path when `ffmpeg-static` is installed.
   - Test that `resolveFFmpegPath()` prefers `FFMPEG_PATH` env var when set (mock the env).
   - Test that `resolveFFmpegPath()` throws when no FFmpeg is available (mock all sources to fail).

2. **Config validation / lifecycle guards:**
   - Test that `writeFrame()` before `start()` rejects with `FFmpegEncoderError`.
   - Test that `writeFrame()` after `finalize()` rejects with `FFmpegEncoderError`.
   - Test that double `start()` throws.
   - Test that `abort()` is idempotent.

3. **RGBA buffer size validation:**
   - Test that `writeFrame()` with a correctly-sized buffer succeeds (1920×1080×4 = 8,294,400 bytes).
   - Test that `writeFrame()` with an incorrectly-sized buffer rejects with a descriptive error.

### Integration Tests (`test/integration/ffmpeg-encoder.test.ts`)

These tests spawn real FFmpeg processes and validate output files. They require FFmpeg to be available (via `ffmpeg-static` or system install).

4. **PNG encode pipeline:**
   - Create 30 solid-color PNG frames (e.g., red 1920×1080) programmatically using a Canvas-like utility or raw PNG construction.
   - Write them through `FFmpegEncoder` with `frameFormat: 'png'`, `fps: 30`.
   - Verify output file exists, is >0 bytes.
   - Run `ffprobe` on output to verify: H.264 codec, 1920×1080, ~1s duration, yuv420p.

5. **RGBA encode pipeline:**
   - Create 30 raw RGBA buffers (1920×1080×4 bytes each, solid blue).
   - Write through encoder with `frameFormat: 'rgba'`.
   - Verify output with `ffprobe` as above.

6. **Portrait mode (9:16):**
   - Create 30 frames at 1080×1920.
   - Verify `ffprobe` reports 1080×1920.

7. **Result object verification:**
   - Verify `finalize()` returns `FFmpegEncoderResult` with `frameCount === 30`, `durationMs > 0`, correct `outputPath`, non-empty `ffmpegLog`.

8. **Error on corrupted input:**
   - Write garbage data as "PNG" frames.
   - Verify `finalize()` rejects with `FFmpegEncoderError` containing non-zero exit code.

9. **Zero-frame encode:**
   - Call `start()` then `finalize()` with no frames.
   - Verify `finalize()` rejects with `FFmpegEncoderError`.

10. **Abort mid-encode:**
    - Start encoding, write a few frames, call `abort()`.
    - Verify `isActive` is false. Verify no unhandled exceptions.

**Relevant testable claims:** TC-02 (render performance — the FFmpeg encoding time is part of the per-frame budget), TC-06 (deterministic output — with `deterministic: true`, the same frames should produce identical MP4s).

### Performance Benchmark (Manual / CI)

11. **Throughput measurement:**
    - Write 1,800 frames (60s × 30fps) of 1920×1080 solid-color PNGs.
    - Measure total encoding time.
    - Target: encoding should not be the bottleneck vs. the 500ms/frame budget from TC-02 (i.e., FFmpeg should encode faster than Puppeteer can produce frames).

## Integration Points

### Depends on
- **OBJ-001** (Project scaffolding): Provides `src/engine/ffmpeg-encoder.ts` stub, `ffmpeg-static` in dependencies, TypeScript build pipeline. The encoder imports `ffmpeg-static` to resolve the default binary path.

### Consumed by
- **OBJ-014** (Audio muxing): Will either wrap this encoder to add audio as a second FFmpeg pass, or extend the FFmpeg arguments to accept a second input stream. OBJ-014 depends on the `FFmpegEncoderResult.outputPath` to know where the video-only MP4 is.
- **OBJ-035** (Orchestrator): Instantiates `FFmpegEncoder`, calls `start()` before the render loop, calls `writeFrame()` for each frame captured by Puppeteer, and calls `finalize()` after the last frame. The orchestrator is the primary consumer.
- **OBJ-083** (appears to depend on OBJ-013 + OBJ-035): Likely a downstream integration.

### File Placement
- **Implementation:** `src/engine/ffmpeg-encoder.ts`
- **Unit tests:** `test/unit/ffmpeg-encoder.test.ts`
- **Integration tests:** `test/integration/ffmpeg-encoder.test.ts`

## Open Questions

1. **Should the encoder produce a raw H.264 stream or a containerized MP4?** Current spec says MP4 because it's the final deliverable format and OBJ-014 can remux cheaply with `-c copy`. If OBJ-014 finds that remuxing an MP4 into another MP4 with audio is problematic, it may prefer a raw `.h264` stream or an `.mkv` intermediate. This is OBJ-014's call — the current default of MP4 is fine for now.

2. **Should we expose `additionalArgs?: string[]` for arbitrary FFmpeg flags?** This would be an escape hatch for advanced users (e.g., adding filters, changing profile/level). Current spec omits it to keep the interface focused. If OBJ-035 or OBJ-014 need custom flags, they can request this addition.

3. **PNG creation for tests:** Integration tests need to create valid PNG buffers. Options: use the `sharp` package (not in dependencies), use a minimal PNG encoder (e.g., `pngjs`), or hand-craft minimal valid PNGs. Recommendation: add `pngjs` or `sharp` as a `devDependency` for test fixtures only, or use Node.js `zlib` to construct minimal valid PNGs (a 1-color PNG is ~70 bytes of header + deflated data). The implementer should choose the simplest approach.

---

I believe this spec is complete and precise enough for an implementer to build from. I'd like the challenger to review and identify any gaps, particularly around:
- Whether the FFmpeg argument construction is sufficiently specified
- Whether the backpressure mechanism needs more detail
- Whether the `deterministic` flag approach is sound for C-05
- Whether the stderr buffering cap (1MB) is appropriate

---

## Round 2 — spec_challenger

I've read the proposal carefully. It's a solid first draft — the lifecycle model, backpressure design, and error class are well-thought-out. Let me enumerate what's sound before getting to the issues.

## What's Sound

- **D-01 (class lifecycle):** Maps directly to the seed's frame loop (Section 4.4). Clean separation of concerns.
- **D-03 (backpressure via drain):** Essential for the 1,800-frame renders. Correct approach.
- **D-04 (video-only, audio to OBJ-014):** Clean boundary. Matches seed's "Audio is muxed in a final FFmpeg pass."
- **D-06 (`-y` flag):** Necessary to prevent deadlock. Good catch.
- **D-07 (`-movflags +faststart`):** Required for SC-01 web playback.
- **Edge cases 1-11:** Thorough coverage, particularly concurrent writeFrame, double start, zero frames.
- **Test strategy:** Both unit and integration layers, realistic scenarios.

## Issues

### Issue 1 — FFmpeg Arguments Are Illustrative, Not Normative (Major)

D-02 shows example FFmpeg argument arrays, but they're presented as rationale prose, not as the definitive specification. An implementer would need to reconstruct the full argument list from scattered pieces: `-y` from D-06, `-movflags +faststart` from D-07, `-threads 1` from D-09 — none of which appear in D-02's examples.

Worse, D-02 uses `-framerate` without clarifying whether this is the input framerate flag or the output. For `image2pipe`, `-framerate` sets the input rate. But should there also be an output `-r` flag? If input and output rates mismatch, FFmpeg interpolates frames — violating C-03's determinism guarantee.

**Proposed fix:** Make D-02 contain the **complete, normative** argument arrays for both formats. Include every flag from D-06, D-07, and D-09 in the arrays. Use comments to explain each flag. Example for PNG:

```
ffmpeg -y -f image2pipe -framerate {fps} -i pipe:0
  -c:v libx264 -preset {preset} -crf {crf}
  -pix_fmt yuv420p -movflags +faststart
  [-threads 1]  // only when deterministic: true
  {outputPath}
```

Also explicitly state: no output `-r` flag is set, so output framerate matches input framerate — this preserves the 1:1 frame correspondence required by C-03.

### Issue 2 — `ffmpeg-static` Import in ESM Context (Major)

The spec says `require('ffmpeg-static')` in the `resolveFFmpegPath` description, but OBJ-001 mandates `"type": "module"` (D-01). `require()` is not available in ESM without `createRequire`. The `ffmpeg-static` package exports a path string — but the import mechanism matters.

**Proposed fix:** Specify that `ffmpeg-static` should be imported via `import ffmpegStatic from 'ffmpeg-static'` (ESM default import) if the package supports it, or via `createRequire(import.meta.url)('ffmpeg-static')` as a fallback. The implementer must verify at implementation time which mechanism works with the installed version. Remove the `require()` phrasing from the spec.

### Issue 3 — `start()` Resolution Semantics Undefined (Major)

When does `start()` resolve? Options:
- (a) Immediately after `child_process.spawn()` returns (process is spawned but may not be ready).
- (b) After FFmpeg writes its banner to stderr (confirms process is alive and arguments were accepted).
- (c) After stdin is confirmed writable.

These have different failure characteristics. With (a), an invalid argument like `-c:v nonexistent_codec` won't surface until `writeFrame()` or `finalize()`. With (b), you catch argument errors early but need to parse stderr.

**Proposed fix:** Specify option (a) — `start()` resolves once the child process is spawned and `process.stdin` is confirmed writable. Argument validation errors surface at `finalize()` or the next `writeFrame()` after the process exits. This is simpler and avoids fragile stderr parsing. Document this explicitly so consumers know that `start()` succeeding does not guarantee encoding will succeed.

### Issue 4 — `spawn()` vs `exec()` Not Specified (Major)

The spec never states which `child_process` method to use. `exec()` goes through a shell and has argument injection risks / path-with-spaces issues. `spawn()` does not. For a module that receives arbitrary file paths as `outputPath`, this matters.

**Proposed fix:** Add a design decision specifying `child_process.spawn()` with arguments as an array (not a shell string). This avoids shell interpretation of `outputPath` containing spaces, parentheses, or other special characters.

### Issue 5 — `-movflags +faststart` Missing from D-02 Argument Lists (Minor → but causes bugs)

D-07 mandates `-movflags +faststart`. D-02's argument examples omit it. An implementer copy-pasting D-02's examples will miss it. AC-13 will catch this at test time, but the spec should be internally consistent.

**Proposed fix:** Add `-movflags +faststart` to D-02's argument arrays.

### Issue 6 — `abort()` and Partial Output File (Minor)

`abort()` kills the FFmpeg process, but what about the partial/corrupted MP4 left on disk? The spec doesn't say whether `abort()` deletes it or leaves it. A partial MP4 at `outputPath` could confuse downstream code (OBJ-014, OBJ-035) that checks for file existence.

**Proposed fix:** Specify that `abort()` does NOT delete the partial output file. Cleanup is the caller's responsibility. Document this as an explicit contract so the orchestrator (OBJ-035) knows to handle it.

### Issue 7 — `pixelFormat` Is a Free `string` Type (Minor)

`pixelFormat?: string` accepts any garbage. While FFmpeg will reject invalid formats, a typo like `'yuv420'` instead of `'yuv420p'` will produce a cryptic FFmpeg error rather than a clear validation message.

**Proposed fix:** Either (a) constrain to a union type (`'yuv420p' | 'yuv444p'`), or (b) keep it as `string` and add a note that invalid values will surface as `FFmpegEncoderError` from FFmpeg's stderr — no encoder-side validation. Given AP-05 (no premature optimization of developer experience), option (b) is fine but should be stated explicitly.

### Issue 8 — Open Question 3 (PNG Test Fixtures) Should Be Resolved (Minor)

The spec leaves "how to create PNG buffers for tests" as an open question. This is an implementation prerequisite for the test strategy — if it's unresolved, the implementer has to make an undocumented design decision about test dependencies.

**Proposed fix:** Recommend adding `pngjs` as a devDependency (MIT, small, purpose-built) for test fixture creation, or specify that minimal valid PNGs should be constructed using Node.js `Buffer` and `zlib` (no additional dependency). Pick one. I'd recommend the `Buffer`+`zlib` approach since it avoids adding a dependency and a valid 1-color PNG is ~100 bytes of well-documented format.

### Issue 9 — `deterministic` Flag Scope vs C-05 (Minor)

The spec says `deterministic: true` forces `-threads 1` for "byte-identical output." But MP4 container metadata includes creation timestamps (`creation_time`), which differ between runs regardless of thread count. So even with `-threads 1`, the output won't be byte-identical at the container level.

**Proposed fix:** Clarify the `deterministic` flag's guarantee: "byte-identical **video stream** output. Container metadata (timestamps, encoder version strings) may still differ between runs. For the purposes of C-05 ('byte-identical or visually indistinguishable'), the default multithreaded mode produces visually indistinguishable output, which satisfies the constraint."

---

## Summary

- **3 major issues** (1, 2, 3, 4 — I count 4 actually) that would force an implementer to guess
- **5 minor issues** that could cause bugs or confusion

Please revise the spec to address these. I'm particularly interested in seeing the normative FFmpeg argument arrays (Issue 1) and the `start()` resolution semantics (Issue 3) nailed down.

---

## Round 3 — spec_author

# Revised Specification: OBJ-013 — FFmpeg Encoder

All nine issues from the challenger are valid. Here's the revised spec with each addressed.

## Summary

OBJ-013 implements the FFmpeg encoding module (`src/engine/ffmpeg-encoder.ts`) — the final stage of the rendering pipeline that receives raw pixel buffers via its API, pipes them to an FFmpeg child process over stdin, and produces an H.264-encoded MP4 file. This module is deliberately independent of Puppeteer: it accepts `Buffer` data from any source, making it testable in isolation and reusable if the frame-capture mechanism changes. It implements the encoding half of constraint C-02 and supports the determinism guarantee of C-05.

Audio muxing is **out of scope** — that is OBJ-014's responsibility. This module produces a video-only MP4.

## Interface Contract

```typescript
// src/engine/ffmpeg-encoder.ts

export type FrameFormat = 'png' | 'rgba';

export type H264Preset =
  | 'ultrafast' | 'superfast' | 'veryfast' | 'faster'
  | 'fast' | 'medium' | 'slow' | 'slower' | 'veryslow';

export interface FFmpegEncoderConfig {
  /** Output file path for the MP4. Must be writable. Parent directory must exist. */
  outputPath: string;

  /** Frame width in pixels. */
  width: number;

  /** Frame height in pixels. */
  height: number;

  /** Frames per second. Sets FFmpeg's input framerate. No output -r flag is set,
   *  so output framerate equals input framerate — preserving 1:1 frame correspondence (C-03). */
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
   * - For 'rgba' format: buffer size !== width × height × 4
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

  readonly framesWritten: number;
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
**Choice:** `FFmpegEncoder` class with explicit `start()` → `writeFrame()` → `finalize()` lifecycle.
**Rationale:** The orchestrator (OBJ-035) needs precise control over the FFmpeg process: start it before the frame loop, write frames one at a time in the deterministic render loop, and finalize after the last frame. A Node.js `Writable` stream interface was considered but rejected because it obscures lifecycle semantics and makes error handling at frame boundaries more complex. The explicit lifecycle maps directly to the frame loop in seed Section 4.4.

### D-02: Normative FFmpeg Argument Arrays
**Choice:** The following are the **complete, definitive** argument arrays for each format. Every flag is included. An implementer should construct these arrays exactly, substituting config values where indicated.

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
**Choice:** Explicit path → `FFMPEG_PATH` env → `ffmpeg-static` → system PATH.
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
**Rationale:** OBJ-001 mandates `"type": "module"` (ESM). `require()` is not available in ESM without `createRequire`. The implementer must verify which mechanism works with the installed `ffmpeg-static` version. *(Addresses Issue 2.)*

### D-11: child_process.spawn() with Array Arguments
**Choice:** Use `child_process.spawn()` with arguments as an array, not `exec()` with a shell string.
**Rationale:** `spawn()` does not invoke a shell, avoiding argument injection risks and path-with-spaces issues. The `outputPath` from the manifest may contain spaces, parentheses, or Unicode characters — `spawn()` handles these correctly. `exec()` would require shell escaping. *(Addresses Issue 4.)*

### D-12: start() Resolution Semantics
**Choice:** `start()` resolves once `child_process.spawn()` returns and the child process's stdin is confirmed writable (i.e., the `spawn` event fires without error). It does **not** wait for FFmpeg to parse arguments or write its banner to stderr.
**Rationale:** Parsing stderr for "FFmpeg started successfully" is fragile and version-dependent. Argument validation errors (e.g., invalid codec) surface naturally when the process exits with a non-zero code, which is detected at the next `writeFrame()` (if the process exited between calls) or at `finalize()`. This is simpler and avoids timing races. *(Addresses Issue 3.)*

**Consequence for consumers:** `start()` succeeding means "FFmpeg process is spawned." It does not mean "FFmpeg arguments are valid" or "encoding will succeed." Errors from invalid arguments will appear as `FFmpegEncoderError` from `writeFrame()` or `finalize()`.

### D-13: abort() Does Not Delete Partial Output
**Choice:** `abort()` kills the FFmpeg process but does **not** delete the partial/corrupted output file at `outputPath`.
**Rationale:** Cleanup of partial files is the caller's responsibility. The orchestrator (OBJ-035) is in a better position to decide whether to delete, retry, or preserve for debugging. *(Addresses Issue 6.)*

## Acceptance Criteria

- [ ] **AC-01:** `FFmpegEncoder` class and `resolveFFmpegPath` function are exported from `src/engine/ffmpeg-encoder.ts` with the interfaces defined above.
- [ ] **AC-02:** `resolveFFmpegPath()` returns a valid path when `ffmpeg-static` is installed and no explicit path or env var is set.
- [ ] **AC-03:** `resolveFFmpegPath()` throws `FFmpegEncoderError` with message containing "FFmpeg binary not found" when no FFmpeg binary can be found.
- [ ] **AC-04:** Writing 30 solid-color PNG frames (1920×1080) at 30fps via `writeFrame()` and calling `finalize()` produces a valid MP4 that `ffprobe` reports as: H.264 codec, 1920×1080, ~1 second duration, yuv420p pixel format.
- [ ] **AC-05:** Writing frames in `rgba` format with buffers of exactly `width × height × 4` bytes produces a valid MP4 with the same codec, resolution, and pixel format properties.
- [ ] **AC-06:** `writeFrame()` rejects with `FFmpegEncoderError` when called before `start()`.
- [ ] **AC-07:** `writeFrame()` rejects with `FFmpegEncoderError` when called after `finalize()`.
- [ ] **AC-08:** For `rgba` format, `writeFrame()` rejects with `FFmpegEncoderError` if the buffer size is not exactly `width × height × 4` bytes. Error message includes expected and actual sizes.
- [ ] **AC-09:** `finalize()` returns an `FFmpegEncoderResult` with correct `frameCount`, non-zero `durationMs`, the `outputPath` matching the config, and non-empty `ffmpegLog`.
- [ ] **AC-10:** If FFmpeg exits with a non-zero code, `finalize()` rejects with `FFmpegEncoderError` containing the exit code and FFmpeg's stderr log.
- [ ] **AC-11:** `abort()` kills the FFmpeg process, is idempotent, and does not delete the partial output file.
- [ ] **AC-12:** Backpressure is handled: when `stream.write()` returns false, `writeFrame()` awaits `drain` before resolving.
- [ ] **AC-13:** The output MP4 includes `-movflags +faststart` (verifiable via `ffprobe -v quiet -show_format` — `format_name` should be `mov,mp4` and the moov atom should precede mdat).
- [ ] **AC-14:** The encoder works with both `1920×1080` and `1080×1920` resolutions (C-04).
- [ ] **AC-15:** `resolveFFmpegPath()` respects the `FFMPEG_PATH` environment variable, using it in preference to `ffmpeg-static`.
- [ ] **AC-16:** FFmpeg is spawned via `child_process.spawn()` with arguments as an array, not via a shell string.
- [ ] **AC-17:** The FFmpeg argument array matches D-02's normative specification exactly (all flags present, correct order of input/output options).

## Edge Cases and Error Handling

1. **FFmpeg not found:** `resolveFFmpegPath()` attempts all four sources in order. If none produce a working binary (validated via `ffmpeg -version` with `spawn()`), throws `FFmpegEncoderError` with message: `"FFmpeg binary not found. Install ffmpeg-static, set FFMPEG_PATH, or ensure ffmpeg is on your system PATH."`.

2. **FFmpeg process crashes mid-encode:** The encoder listens for the child process `error` and `close` events. If FFmpeg exits unexpectedly, a flag is set and the next `writeFrame()` call rejects with `FFmpegEncoderError` containing the exit code and accumulated stderr. `isActive` returns `false` immediately upon unexpected exit.

3. **Output path not writable / parent directory missing:** FFmpeg fails with a stderr message. The encoder does **not** create parent directories. The error surfaces as `FFmpegEncoderError` from `finalize()` (or `writeFrame()` if FFmpeg exits immediately). The error includes FFmpeg's stderr for diagnosis.

4. **Zero frames written:** If `finalize()` is called without any `writeFrame()` calls, FFmpeg exits with an error. Surfaced as `FFmpegEncoderError`: `"FFmpeg exited with code {N}: no frames were written before finalize()."`.

5. **Corrupted PNG data:** Invalid PNG data in `png` mode causes FFmpeg's `image2pipe` demuxer to fail. The encoder does **not** validate PNG structure. The error surfaces via `FFmpegEncoderError` at `finalize()` with FFmpeg's stderr.

6. **Wrong-sized RGBA buffer:** `writeFrame()` validates `data.length === width * height * 4` before writing. Rejects immediately: `"RGBA frame buffer size mismatch: expected {expected} bytes ({width}×{height}×4), got {actual}."`.

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
   - Correctly-sized buffer (1920×1080×4 = 8,294,400 bytes) does not throw the size error.
   - Incorrectly-sized buffer rejects with error message containing expected and actual sizes.

### Integration Tests (`test/integration/ffmpeg-encoder.test.ts`)

These spawn real FFmpeg processes. Require FFmpeg available via `ffmpeg-static` or system install.

**PNG buffer creation for tests:** Construct minimal valid PNG buffers using Node.js `Buffer` and `zlib`. A single-color PNG is a well-documented format: 8-byte signature, IHDR chunk (13 bytes data), IDAT chunk (deflated scanlines), IEND chunk. Total ~100-200 bytes for a 1×1 image; for 1920×1080 solid color, deflate compresses the repeated scanlines efficiently. No additional devDependency required. *(Resolves Open Question 3.)*

4. **PNG encode pipeline:** Create 30 solid-color PNG frames (1920×1080). Write via encoder at 30fps. Verify output exists and `ffprobe` reports: H.264, 1920×1080, ~1s duration, yuv420p.

5. **RGBA encode pipeline:** Create 30 raw RGBA buffers (1920×1080×4 bytes, solid blue). Write via encoder. Verify with `ffprobe`.

6. **Portrait mode (9:16):** 30 frames at 1080×1920. Verify `ffprobe` reports 1080×1920.

7. **Result object:** Verify `finalize()` returns `FFmpegEncoderResult` with `frameCount === 30`, `durationMs > 0`, correct `outputPath`, non-empty `ffmpegLog`.

8. **Corrupted input:** Write garbage data as "PNG" frames. Verify `finalize()` rejects with `FFmpegEncoderError` with non-zero exit code.

9. **Zero-frame encode:** `start()` then `finalize()` with no frames. Verify rejects with `FFmpegEncoderError`.

10. **Abort mid-encode:** Start, write a few frames, `abort()`. Verify `isActive` is false, no unhandled exceptions. Verify partial output file still exists on disk.

11. **Argument array verification:** After `start()`, inspect the spawned process arguments (if accessible) or verify the output MP4 properties match D-02's flags (e.g., faststart, yuv420p). Alternatively, test with a known-bad `pixelFormat` and verify the error surfaces.

**Relevant testable claims:** TC-02 (FFmpeg encoding time is part of the per-frame budget), TC-06 (with `deterministic: true`, same frames → identical video streams).

### Performance Benchmark (Manual / CI)

12. **Throughput:** Write 1,800 solid-color PNG frames (1920×1080) at 30fps. Measure encoding time. FFmpeg should encode faster than Puppeteer's ~500ms/frame budget (TC-02), confirming it's not the bottleneck.

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

1. **Should the encoder produce video-only MP4 or raw H.264 stream?** Current spec says MP4 because it's the final deliverable format and OBJ-014 can remux cheaply with `-c copy`. If OBJ-014 finds that remuxing MP4→MP4 is problematic, it may request a raw `.h264` intermediate. This is OBJ-014's decision — the current MP4 default is correct for now.

2. **Should we expose `additionalArgs?: string[]` for arbitrary FFmpeg flags?** Omitted to keep the interface focused. If OBJ-035 or OBJ-014 need custom flags, they can request this addition in a later revision.

---

I believe this revision addresses all nine issues raised:

| Issue | Resolution |
|-------|-----------|
| 1 — FFmpeg args illustrative, not normative | D-02 now contains complete, normative argument arrays with every flag. Explicitly states no output `-r` flag. |
| 2 — `require()` in ESM context | D-10 specifies ESM import with `createRequire` fallback. |
| 3 — `start()` resolution semantics undefined | D-12 specifies: resolves after spawn, does not wait for stderr. Documented consequence for consumers. |
| 4 — `spawn()` vs `exec()` | D-11 mandates `child_process.spawn()` with array arguments. AC-16 added. |
| 5 — `-movflags +faststart` missing from D-02 | Now included in D-02's normative arrays. |
| 6 — `abort()` and partial output | D-13 specifies abort does NOT delete. Documented on the `abort()` method. |
| 7 — `pixelFormat` free string | Interface doc now explicitly states: "Invalid values will surface as FFmpegEncoderError from FFmpeg's stderr — no encoder-side validation." |
| 8 — PNG test fixture creation unresolved | Test Strategy now specifies: construct minimal PNGs with `Buffer` + `zlib`, no additional devDependency. |
| 9 — `deterministic` flag scope vs container metadata | D-09 and the `deterministic` field doc now clarify: byte-identical **video stream**, container metadata may differ. |

Challenger — please verify these revisions address your concerns and approve or raise further issues.

---

## Round 4 — spec_challenger

## Verification of Round 3 Revisions

I've walked through the revised spec against each of my nine original issues:

| Issue | Verified? | Location in Rev |
|-------|-----------|-----------------|
| 1 — Normative FFmpeg args | ✅ D-02 has complete arrays, all flags, comments, explicit "no output `-r`" statement | 
| 2 — ESM import | ✅ D-10 specifies ESM default import + `createRequire` fallback. Edge case 11 covers cascading failure |
| 3 — `start()` semantics | ✅ D-12 defines resolution point + documents consequence for consumers. Interface JSDoc repeats it |
| 4 — `spawn()` mandate | ✅ D-11 + AC-16 added |
| 5 — `faststart` in args | ✅ Present in both D-02 arrays |
| 6 — `abort()` partial file | ✅ D-13 + `abort()` JSDoc + integration test 10 verifies file persists |
| 7 — `pixelFormat` string | ✅ Config doc explicitly states no encoder-side validation |
| 8 — PNG test fixtures | ✅ Test Strategy specifies `Buffer` + `zlib`, no extra devDep |
| 9 — `deterministic` scope | ✅ D-09 + config JSDoc clarify video-stream-only guarantee |

Every fix is structurally present in the revised text, not just claimed. The interface contract, design decisions, acceptance criteria, edge cases, and test strategy are internally consistent.

**One minor remaining observation** (not a blocker): Edge case 2 says "the **next** `writeFrame()` call rejects" when FFmpeg exits unexpectedly. If a `writeFrame()` is currently awaiting a `drain` event when FFmpeg crashes, the drain will never fire and that promise hangs forever. The fix is straightforward (also listen for stdin `error`/`close` to reject pending drain promises), and a competent Node.js implementer will do this naturally. I'll record it as an open question rather than demand another round.

Everything else — lifecycle model, normative argument arrays, error taxonomy, test coverage, scope boundaries, vocabulary compliance, constraint compliance (C-01 through C-05), downstream compatibility with OBJ-014/OBJ-035 — is solid.

CONCLUSION:

The specification for OBJ-013 (FFmpeg Encoder) is approved. It defines a clean `FFmpegEncoder` class with explicit start/writeFrame/finalize lifecycle, normative FFmpeg argument arrays for both PNG and RGBA input formats, comprehensive error handling via `FFmpegEncoderError`, and a complete test strategy covering unit, integration, and performance benchmarks. All nine challenger issues from Round 2 have been structurally resolved in the revision.

Let me write the final spec and meta to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read,Bash",
  "max_results": 3
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]


Let me first check the current state of the node directory and files.
[Tool: Bash]
  Input: {
  "command": "ls -la nodes/OBJ-013/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-013 node directory exists"
}

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-013",
     3→  "description": "FFmpeg encoder -- child process spawn, stdin piping of raw frame data (PNG or raw RGBA buffers), H.264 encoding parameters, pixel format options, output container format (MP4). Implements the encoding half of C-02. Independent of Puppeteer -- receives raw pixel buffers via stdin regardless of their source.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-001"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Independent of Puppeteer -- only needs project scaffolding."
    12→}
    13→
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:17 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   663 Mar 22 19:17 meta.json
Good. Now let me write the final spec and update the meta.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "content": "# Specification: OBJ-013 \u2014 FFmpeg Encoder\n\n## Summary\n\nOBJ-013 implements the FFmpeg encoding module (`src/engine/ffmpeg-encoder.ts`) \u2014 the final stage of the rendering pipeline that receives raw pixel buffers via its API, pipes them to an FFmpeg child process over stdin, and produces an H.264-encoded MP4 file. This module is deliberately independent of Puppeteer: it accepts `Buffer` data from any source, making it testable in isolation and reusable if the frame-capture mechanism changes. It implements the encoding half of constraint C-02 and supports the determinism guarantee of C-05.\n\nAudio muxing is **out of scope** \u2014 that is OBJ-014's responsibility. This module produces a video-only MP4.\n\n## Interface Contract\n\n```typescript\n// src/engine/ffmpeg-encoder.ts\n\n/**\n * Supported input pixel formats for frame data piped to FFmpeg.\n * - 'png': Each frame is a complete PNG-encoded buffer. FFmpeg uses `image2pipe` demuxer.\n * - 'rgba': Each frame is raw RGBA pixel data (width * height * 4 bytes). FFmpeg uses `rawvideo` input.\n */\nexport type FrameFormat = 'png' | 'rgba';\n\n/**\n * H.264 encoding preset. Controls the speed/quality/filesize tradeoff.\n * Maps directly to FFmpeg's `-preset` flag.\n */\nexport type H264Preset =\n  | 'ultrafast' | 'superfast' | 'veryfast' | 'faster'\n  | 'fast' | 'medium' | 'slow' | 'slower' | 'veryslow';\n\n/**\n * Configuration for the FFmpeg encoder.\n */\nexport interface FFmpegEncoderConfig {\n  /** Output file path for the MP4. Must be writable. Parent directory must exist. */\n  outputPath: string;\n\n  /** Frame width in pixels. */\n  width: number;\n\n  /** Frame height in pixels. */\n  height: number;\n\n  /**\n   * Frames per second. Sets FFmpeg's input framerate. No output -r flag is set,\n   * so output framerate equals input framerate \u2014 preserving 1:1 frame corresp
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/meta.json",
  "content": "{\n  \"id\": \"OBJ-013\",\n  \"description\": \"FFmpeg encoder -- child process spawn, stdin piping of raw frame data (PNG or raw RGBA buffers), H.264 encoding parameters, pixel format options, output container format (MP4). Implements the encoding half of C-02. Independent of Puppeteer -- receives raw pixel buffers via stdin regardless of their source.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:00:00Z\",\n  \"depends_on\": [\"OBJ-001\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 engine core. Independent of Puppeteer -- only needs project scaffolding. Spec completed via 4-round deliberation. Video-only MP4 output; audio muxing deferred to OBJ-014.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\",\n  \"spec_deliberation_rounds\": 4\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/meta.json has been updated successfully.
Now commit:
[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-013/output.md nodes/OBJ-013/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-013): FFmpeg encoder specification \u2014 approved after 4-round deliberation\n\nDefines FFmpegEncoder class with start/writeFrame/finalize lifecycle,\nnormative FFmpeg argument arrays for PNG and RGBA input formats,\nbackpressure handling via drain events, and resolveFFmpegPath utility.\nVideo-only MP4 output; audio muxing deferred to OBJ-014.\n\nKey design decisions: child_process.spawn() with array args, ESM import\nof ffmpeg-static with createRequire fallback, -movflags +faststart for\nweb playback, optional deterministic flag for byte-identical video streams.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-013 spec and updated meta.json"
}
[Tool Error] Could not parse command for security validation: git add nodes/OBJ-013/output.md nodes/OBJ-013/meta.json && git commit -m "$(cat <<'EOF'
spec(OBJ-013): FFmpeg encoder specification — approved after 4-round deliberation

Defines FFmpegEncoder class with start/writeFrame/finalize lifecycle,
normative FFmpeg argument arrays for PNG and RGBA input formats,
backpressure handling via drain events, and resolveFFmpegPath utility.
Video-only MP4 output; audio muxing deferred to OBJ-014.

Key design decis

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-013/output.md nodes/OBJ-013/meta.json",
  "description": "Stage OBJ-013 spec files"
}
[Tool Result] (Bash completed with no output)

[Tool: Bash]
  Input: {
  "command": "git commit -m \"spec(OBJ-013): FFmpeg encoder specification -- approved after 4-round deliberation\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\"",
  "description": "Commit OBJ-013 spec"
}
[Tool Result] [master baa00bf] spec(OBJ-013): FFmpeg encoder specification -- approved after 4-round deliberation
 2 files changed, 413 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-013/output.md
Committed successfully. The OBJ-013 FFmpeg Encoder specification is now finalized at `nodes/OBJ-013/output.md` with updated `meta.json`. 

**Summary of what was agreed:**

- **`FFmpegEncoder` class** with explicit `start()` → `writeFrame()` → `finalize()` lifecycle, plus `abort()` for error recovery
- **Two input formats:** PNG (default, self-describing) and RGBA (performance option)
- **Normative FFmpeg argument arrays** in D-02 — complete and definitive, no guessing required
- **Backpressure** via `drain` event awaiting in `writeFrame()`
- **Video-only MP4** output; audio muxing is OBJ-014's scope
- **`resolveFFmpegPath()`** with 4-source fallback chain (explicit → env → ffmpeg-static → system PATH)
- **13 design decisions**, **17 acceptance criteria**, **11 edge cases**, **12 test scenarios**

**Key issues resolved during deliberation:**
1. FFmpeg args made normative (not illustrative)
2. ESM import of ffmpeg-static specified with `createRequire` fallback
3. `start()` resolution semantics defined (spawn-based, not stderr-parsing)
4. `child_process.spawn()` mandated over `exec()`
5. `abort()` partial file cleanup responsibility assigned to caller
6. `deterministic` flag scoped to video stream only (container metadata may differ)
