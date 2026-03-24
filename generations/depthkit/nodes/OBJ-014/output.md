# Specification: OBJ-014 — FFmpeg Audio Muxing

## Summary

OBJ-014 implements the audio muxing module (`src/engine/audio-muxer.ts`) — the post-encoding stage that combines OBJ-013's video-only MP4 with an audio file (WAV or MP3) to produce the final deliverable MP4 with synchronized audio. This module covers constraint C-07 (audio synchronization) at the encoding level, making the single-pass vs. two-pass decision, handling format differences between WAV and MP3 inputs, and managing duration mismatches between video and audio streams.

This module is deliberately separate from OBJ-013's `FFmpegEncoder` — it operates on completed files, not on streaming frame data. It accepts file paths, not buffers.

## Interface Contract

```typescript
// src/engine/audio-muxer.ts

/**
 * Strategy for handling duration mismatches between video and audio.
 *
 * - 'match_shortest': Output duration equals the shorter of video/audio.
 *   Uses FFmpeg's `-shortest` flag.
 *
 * - 'match_audio': Output duration equals audio duration.
 *   If video is shorter than audio by more than DURATION_EQUAL_THRESHOLD_MS,
 *   the last video frame is held (frozen) via the `tpad` filter, which forces
 *   video re-encoding. If video is longer, it is truncated via `-t`.
 *   If durations are within DURATION_EQUAL_THRESHOLD_MS, no adjustment is made.
 *   This is the expected production mode — the orchestrator computes frame count
 *   from audio duration, so durations should already match.
 *
 * - 'match_video': Output duration equals video duration.
 *   If audio is shorter, no flag is needed — FFmpeg outputs until the longest
 *   input ends, so the tail of the video plays in silence. If audio is longer,
 *   `-t {videoDurationSeconds}` truncates the output to video length.
 *
 * - 'error': Reject if durations differ by more than `toleranceMs`.
 *   Strictest mode — used for testing deterministic alignment.
 */
export type DurationStrategy = 'match_shortest' | 'match_audio' | 'match_video' | 'error';

/**
 * Configuration for the audio muxer.
 */
export interface AudioMuxerConfig {
  /** Path to the video-only MP4 file produced by OBJ-013's FFmpegEncoder. */
  videoPath: string;

  /** Path to the audio file (WAV or MP3). */
  audioPath: string;

  /** Path for the final output MP4 with muxed audio+video. */
  outputPath: string;

  /**
   * Strategy for handling duration mismatches. Default: 'match_audio'.
   */
  durationStrategy?: DurationStrategy;

  /**
   * Tolerance in milliseconds for the 'error' duration strategy.
   * If abs(videoDuration - audioDuration) * 1000 > toleranceMs, muxing
   * fails with AudioMuxerError. Ignored for other strategies.
   * Default: 100 (allows up to 100ms drift from frame rounding).
   */
  toleranceMs?: number;

  /**
   * Audio volume adjustment. 1.0 = original volume.
   * Applied via FFmpeg's `-filter:a volume={volume}` filter.
   * When volume is exactly 1.0 (default), no audio filter is applied
   * and audio is stream-copied (`-c:a copy` for MP3) or minimally
   * transcoded (`-c:a aac` for WAV).
   * When volume !== 1.0, audio is always re-encoded to AAC.
   * Valid range: 0.0 to 5.0.
   */
  volume?: number;

  /**
   * AAC audio bitrate when audio re-encoding is needed.
   * Used when: input is WAV (always re-encoded), or volume !== 1.0.
   * Default: '192k'.
   */
  audioBitrate?: string;

  /**
   * Optional path to FFmpeg binary.
   * If not provided, uses resolveFFmpegPath() from OBJ-013.
   */
  ffmpegPath?: string;
}

/**
 * Result returned when muxing completes successfully.
 */
export interface AudioMuxerResult {
  /** Absolute path to the output MP4 file. */
  outputPath: string;

  /**
   * Duration of the output file in seconds, obtained by calling probeMedia()
   * on the output file after FFmpeg completes. This ensures the reported
   * duration reflects what FFmpeg actually produced, not what was computed
   * from inputs.
   */
  durationSeconds: number;

  /**
   * Whether the video stream was re-encoded or stream-copied.
   * 'copy' in all cases EXCEPT when `match_audio` strategy requires the
   * `tpad` filter to freeze the last frame (video shorter than audio by
   * more than DURATION_EQUAL_THRESHOLD_MS). In that case: 'reencode'.
   */
  videoCodecAction: 'copy' | 'reencode';

  /**
   * Whether the audio stream was re-encoded or stream-copied.
   * 'copy' only when input is MP3 and volume is 1.0.
   * 'encode' when input is WAV, or volume !== 1.0.
   */
  audioCodecAction: 'copy' | 'encode';

  /** Total muxing duration in milliseconds (wall-clock time). */
  durationMs: number;

  /** FFmpeg's stderr output. Capped at last 1MB. */
  ffmpegLog: string;
}

/**
 * Metadata about a media file, obtained via ffprobe.
 */
export interface MediaProbeResult {
  /** Duration in seconds. */
  durationSeconds: number;

  /** Detected format/container (e.g., 'mov,mp4,m4a,3gp,3g2,mj2', 'wav', 'mp3'). */
  formatName: string;

  /** Whether the file contains a video stream. */
  hasVideo: boolean;

  /** Whether the file contains an audio stream. */
  hasAudio: boolean;

  /** Audio codec name if present (e.g., 'aac', 'mp3', 'pcm_s16le'). */
  audioCodec?: string;

  /** Audio sample rate if present (e.g., 44100, 48000). */
  audioSampleRate?: number;
}

/**
 * Custom error class for audio muxing failures.
 */
export class AudioMuxerError extends Error {
  constructor(
    message: string,
    public readonly exitCode: number | null,
    public readonly ffmpegLog: string,
  ) {
    super(message);
    this.name = 'AudioMuxerError';
  }
}

/**
 * Threshold in milliseconds below which video and audio durations are
 * considered "equal" for the purposes of the `match_audio` strategy.
 * Within this threshold, no tpad or -t flag is applied, preserving
 * -c:v copy.
 *
 * Rationale: At 30fps, one frame = 33.3ms. At 24fps, one frame = 41.7ms.
 * 50ms accommodates up to ~1.5 frames of rounding drift at 30fps, which
 * is the maximum drift from `Math.round(audioDuration * fps)`.
 *
 * This threshold applies ONLY to `match_audio` strategy. `match_shortest`
 * and `match_video` use flags that are idempotent for equal durations.
 * `error` uses its own configurable `toleranceMs`.
 */
export const DURATION_EQUAL_THRESHOLD_MS = 50;

/**
 * Resolves the ffprobe binary path. Tries in order:
 * 1. Explicit path (if provided via ffprobePath parameter)
 * 2. FFPROBE_PATH environment variable
 * 3. ffprobe-static package (ESM import, same pattern as OBJ-013's D-10)
 * 4. Co-located with the resolved FFmpeg binary (same directory)
 * 5. 'ffprobe' on system PATH
 *
 * Validates by spawning `ffprobe -version` and checking exit code 0.
 * Throws AudioMuxerError if no working ffprobe binary is found.
 */
export function resolveFFprobePath(ffmpegPath?: string, ffprobePath?: string): Promise<string>;

/**
 * Probes a media file using ffprobe, returning duration and stream info.
 *
 * Uses `ffprobe -v quiet -print_format json -show_format -show_streams {filePath}`.
 * Spawned via child_process.spawn() with array arguments (no shell).
 *
 * Internally calls resolveFFprobePath(ffmpegPath) to locate the ffprobe binary.
 * The ffmpegPath parameter is passed through for co-location resolution (step 4
 * of resolveFFprobePath), not used directly.
 *
 * Throws AudioMuxerError if:
 * - ffprobe binary cannot be found
 * - The file does not exist or is unreadable
 * - ffprobe exits with non-zero code
 * - ffprobe output cannot be parsed as JSON
 */
export function probeMedia(filePath: string, ffmpegPath?: string): Promise<MediaProbeResult>;

/**
 * Muxes a video-only MP4 with an audio file to produce the final MP4.
 *
 * This is a stateless function (not a class) because muxing is a single
 * atomic FFmpeg invocation — there is no streaming lifecycle to manage.
 *
 * The video stream is stream-copied (-c:v copy) in all cases EXCEPT when
 * the `match_audio` strategy requires the `tpad` filter (video shorter than
 * audio by more than DURATION_EQUAL_THRESHOLD_MS). In that case, video is
 * re-encoded with `-c:v libx264 -preset ultrafast -crf 18`.
 *
 * The audio stream handling depends on format and volume — see D-04.
 *
 * After FFmpeg completes, probeMedia() is called on the output file to
 * populate AudioMuxerResult.durationSeconds.
 *
 * Throws AudioMuxerError if:
 * - outputPath equals videoPath or audioPath
 * - Volume is outside [0.0, 5.0]
 * - Video file does not exist or has no video stream
 * - Audio file does not exist or has no audio stream
 * - Duration mismatch exceeds tolerance (when strategy is 'error')
 * - FFmpeg exits with non-zero code
 * - Output path is not writable
 */
export function muxAudio(config: AudioMuxerConfig): Promise<AudioMuxerResult>;
```

## Design Decisions

### D-01: Two-Pass (Remux) over Single-Pass
**Choice:** Audio is muxed in a separate FFmpeg invocation after OBJ-013 produces a video-only MP4. The video stream is stream-copied (`-c:v copy`) in the common case, never re-encoded except when the `tpad` filter is required.

**Rationale:**
1. **Separation of concerns:** OBJ-013's `FFmpegEncoder` manages a complex streaming lifecycle (spawn -> pipe frames -> finalize). Adding a second input stream for audio would complicate its backpressure handling, error recovery, and lifecycle management.
2. **Speed:** Stream-copying the video (`-c:v copy`) makes the remux nearly instantaneous (seconds for a 60s video vs. minutes for re-encoding). The audio transcode (WAV->AAC) is also fast.
3. **Flexibility:** The orchestrator (OBJ-035) may not have the audio file ready when frame rendering begins (e.g., TTS generation may run in parallel). Two-pass decouples video rendering from audio availability.
4. **Debuggability:** The intermediate video-only MP4 can be inspected independently.
5. **OBJ-013 compatibility:** OBJ-013's spec explicitly produces video-only MP4 and defers audio to OBJ-014. Modifying OBJ-013 would require reopening a verified objective.

**Trade-off:** An intermediate file is written to disk. For a 60s 1080p video at CRF 23, this is roughly 10-30MB — negligible.

### D-02: Function over Class
**Choice:** `muxAudio()` is a standalone async function, not a class with lifecycle methods.

**Rationale:** Unlike OBJ-013's frame-by-frame streaming, muxing is a single atomic operation: spawn FFmpeg with two file inputs, wait for completion. There is no streaming lifecycle to manage. A function is simpler and maps directly to the operation.

### D-03: Video Stream Always Copied, Never Re-encoded (with one exception)
**Choice:** The video stream uses `-c:v copy` unconditionally, **except** when the `match_audio` duration strategy requires the `tpad` video filter (video shorter than audio). Filters cannot operate on stream-copied data, so this case forces re-encoding with `-c:v libx264 -preset ultrafast -crf 18`.

**Rationale:** OBJ-013 already encoded to H.264 with the desired quality settings. Re-encoding would be slow and introduce generation loss. The `tpad` exception should be rare in practice — the orchestrator computes frame count from audio duration, so durations should match within a frame or two, which falls within `DURATION_EQUAL_THRESHOLD_MS`.

### D-04: Audio Codec Decision Table
**Choice:** The audio codec flags are determined by a two-axis table: input format x volume setting.

| Input Format | Volume = 1.0 | Volume != 1.0 |
|---|---|---|
| **MP3** | `-c:a copy` | `-c:a aac -b:a {audioBitrate} -filter:a volume={volume}` |
| **WAV** | `-c:a aac -b:a {audioBitrate}` | `-c:a aac -b:a {audioBitrate} -filter:a volume={volume}` |

**Rationale:**
- WAV (PCM) inside MP4 is non-standard and poorly supported by browsers and mobile players. Always transcode to AAC.
- MP3 in MP4 is well-supported. Stream-copy avoids unnecessary transcoding and quality loss.
- Volume adjustment requires an audio filter, which in turn requires re-encoding.
- No explicit `-ar` (sample rate) flag is set; FFmpeg preserves the input audio sample rate during transcoding. This is acceptable for standard rates (44100, 48000). Unusual rates (e.g., 22050) may produce lower quality AAC but are not rejected — this is a conscious decision, not an omission.

**Input format detection:** The audio format is determined from `probeMedia()` results, not from file extension. If `audioCodec` contains `pcm` (e.g., `pcm_s16le`, `pcm_f32le`), treat as WAV (re-encode). If `audioCodec` contains `mp3`, treat as MP3 (eligible for copy). For any other codec (e.g., `aac`, `vorbis`, `flac`), treat as "needs re-encoding" (same path as WAV).

### D-05: Duration Strategy Flag Table
**Choice:** Duration handling is determined by a two-axis table: strategy x duration relationship. Duration comparison uses probed values from both input files.

| Strategy | Video ~ Audio (within threshold) | Video < Audio | Video > Audio |
|---|---|---|---|
| **`match_shortest`** | `-shortest` | `-shortest` | `-shortest` |
| **`match_audio`** | no flag | `-vf tpad=stop_mode=clone:stop_duration={delta}` + video re-encode | `-t {audioDur}` |
| **`match_video`** | no flag | `-t {videoDur}` | no flag |
| **`error`** | no flag | rejected pre-FFmpeg | rejected pre-FFmpeg |

**"Video ~ Audio" for `match_audio`:** Defined as `Math.abs(videoDuration - audioDuration) * 1000 <= DURATION_EQUAL_THRESHOLD_MS` (50ms). Within this threshold, no `tpad` or `-t` is applied, preserving `-c:v copy`. This threshold applies **only** to `match_audio`. `match_shortest` uses `-shortest` unconditionally (idempotent for equal durations). `match_video` uses no flag for equal durations (also idempotent — FFmpeg stops at the end of both streams). `error` uses its own configurable `toleranceMs`.

**Where `delta` is:** `audioDuration - videoDuration` in seconds (positive, since video < audio in this cell).

**Where `audioDur` / `videoDur` is:** The probed duration in seconds.

### D-06: Normative FFmpeg Argument Template
**Choice:** All FFmpeg muxing invocations follow this single template. The codec flags and duration flags slot in from D-04 and D-05 respectively.

```
ffmpeg
  -y                                  # Always: overwrite without prompting
  -i {videoPath}                      # Input 0: video-only MP4
  -i {audioPath}                      # Input 1: audio file
  {videoCodecFlags}                   # From D-03/D-05: -c:v copy OR -c:v libx264 -preset ultrafast -crf 18
  {audioCodecFlags}                   # From D-04 table
  {durationVideoFilter}              # From D-05: -vf tpad=... (only for match_audio + video shorter)
  -map 0:v:0                          # Always: first video stream from input 0
  -map 1:a:0                          # Always: first audio stream from input 1
  {durationFlags}                     # From D-05: -shortest, -t {seconds}, or nothing
  -movflags +faststart                # Always: web progressive playback
  {outputPath}
```

**Slot contents by scenario:**

| Slot | Default (stream copy) | tpad scenario |
|---|---|---|
| `{videoCodecFlags}` | `-c:v copy` | `-c:v libx264 -preset ultrafast -crf 18` |
| `{audioCodecFlags}` | Per D-04 table | Per D-04 table |
| `{durationVideoFilter}` | (absent) | `-vf tpad=stop_mode=clone:stop_duration={delta}` |
| `{durationFlags}` | Per D-05 table | (absent — tpad handles it) |

**Note:** The `-vf tpad=...` and `-filter:a volume=...` flags are independent (video vs. audio filter) and coexist in the same FFmpeg invocation without conflict.

**Important ordering constraint:** `-filter:a` and `-vf` must appear before `-map` flags in the argument array. FFmpeg applies filters before mapping.

### D-07: Pre-Mux and Post-Mux Validation via ffprobe
**Choice:** Before spawning the muxing FFmpeg process, `muxAudio()` probes both input files via `probeMedia()` to validate existence, stream presence, and duration. After muxing completes, `probeMedia()` is called on the output file to populate `AudioMuxerResult.durationSeconds`.

**Rationale:** Fail-fast with clear error messages (C-10 spirit). FFmpeg's own error messages for missing streams or corrupt files are often cryptic. Probing first lets us provide actionable errors: "Audio file has no audio stream" rather than FFmpeg's "Stream map '1:a:0' matches no streams." Post-mux probing ensures the reported output duration reflects reality.

### D-08: ffprobe Binary Resolution
**Choice:** Add `ffprobe-static` (MIT licensed, C-01 compliant) as an allowed dependency. Define `resolveFFprobePath()` with resolution order: explicit path -> `FFPROBE_PATH` env -> `ffprobe-static` package -> co-located with resolved FFmpeg binary (same directory) -> `ffprobe` on system PATH.

**Rationale:** `ffmpeg-static` does **not** include ffprobe. The `ffprobe-static` package (MIT licensed) provides the binary. This is the most reliable cross-platform approach. The co-location fallback covers system installs where both binaries are in `/usr/bin/` or similar. Validation via `ffprobe -version` confirms the binary works.

**Dependency addition:** `ffprobe-static` must be added to `package.json` dependencies. This is MIT licensed, consistent with C-01's zero-license constraint (MIT is explicitly allowed — see `three` in C-01).

### D-09: `-movflags +faststart` Preserved
**Choice:** Always include `-movflags +faststart` on the muxed output.

**Rationale:** The video-only MP4 from OBJ-013 already has this, but remuxing creates a new container. The flag must be re-applied to ensure the final deliverable supports web progressive playback (SC-01).

### D-10: Volume Validation Range
**Choice:** Volume must be in range `[0.0, 5.0]`. Validated synchronously before any async work (probing, FFmpeg).

**Rationale:** Volume 0.0 is valid (mute). Values above 5.0 cause extreme distortion and clipping. This is a sensible guard rail, not an FFmpeg limitation.

### D-11: `-map` Flags for Explicit Stream Selection
**Choice:** Always use `-map 0:v:0 -map 1:a:0`.

**Rationale:** Without explicit mapping, FFmpeg's automatic stream selection may behave unexpectedly if either input has multiple streams. Explicit mapping is defensive and predictable.

### D-12: Intermediate File Cleanup is Caller's Responsibility
**Choice:** `muxAudio()` does not delete the intermediate video-only MP4 (`videoPath`). Cleanup is the orchestrator's responsibility.

**Rationale:** Consistent with OBJ-013's D-13. The orchestrator may want to keep the intermediate for debugging.

### D-13: Output Path Collision Prevention
**Choice:** `muxAudio()` validates that `outputPath` differs from both `videoPath` and `audioPath` before any work begins. Comparison uses `path.resolve()` to normalize paths.

**Rationale:** FFmpeg with `-y` overwrites the output file. If `outputPath === videoPath`, FFmpeg truncates the video input before reading it, corrupting the encode. This is a silent, unrecoverable failure that must be prevented with an early check.

## Acceptance Criteria

- [ ] **AC-01:** `muxAudio` function, `probeMedia` function, `resolveFFprobePath` function, `AudioMuxerError` class, `DURATION_EQUAL_THRESHOLD_MS` constant, and all types (`DurationStrategy`, `AudioMuxerConfig`, `AudioMuxerResult`, `MediaProbeResult`) are exported from `src/engine/audio-muxer.ts`.
- [ ] **AC-02:** `probeMedia()` returns correct `durationSeconds`, `hasVideo`, `hasAudio`, `audioCodec`, and `audioSampleRate` for a known WAV file.
- [ ] **AC-03:** `probeMedia()` returns correct metadata for a known MP3 file.
- [ ] **AC-04:** `probeMedia()` returns correct metadata for a video-only MP4 (produced by OBJ-013): `hasVideo: true`, `hasAudio: false`.
- [ ] **AC-05:** `probeMedia()` throws `AudioMuxerError` for a nonexistent file path, with a message containing the file path.
- [ ] **AC-06:** Muxing a video-only MP4 with an MP3 file (volume 1.0) produces a valid MP4 that `ffprobe` reports as having both a video stream (H.264) and an audio stream (mp3). `audioCodecAction: 'copy'`. `videoCodecAction: 'copy'`.
- [ ] **AC-07:** Muxing a video-only MP4 with a WAV file produces a valid MP4 with video (H.264) and audio (AAC) streams. `audioCodecAction: 'encode'`.
- [ ] **AC-08:** When `volume` is set to 0.5, the output audio is re-encoded to AAC regardless of input format. `audioCodecAction: 'encode'`.
- [ ] **AC-09:** `durationStrategy: 'error'` throws `AudioMuxerError` when `Math.abs(videoDuration - audioDuration) * 1000 > toleranceMs`, with a message containing both durations and the tolerance.
- [ ] **AC-10:** `durationStrategy: 'error'` succeeds when durations differ by less than `toleranceMs`.
- [ ] **AC-11:** `durationStrategy: 'match_shortest'` produces output whose duration equals the shorter input (within 100ms tolerance).
- [ ] **AC-12:** `durationStrategy: 'match_audio'` with video shorter than audio (by more than `DURATION_EQUAL_THRESHOLD_MS`) produces output whose duration matches audio duration (within 100ms tolerance), with the last video frame held/frozen. `videoCodecAction: 'reencode'`.
- [ ] **AC-13:** `durationStrategy: 'match_video'` with audio shorter than video produces output whose duration matches video duration (within 100ms tolerance).
- [ ] **AC-14:** The `AudioMuxerResult` includes correct `outputPath`, `durationSeconds > 0` (from post-mux probe), correct `videoCodecAction` and `audioCodecAction`, non-zero `durationMs`, and non-empty `ffmpegLog`.
- [ ] **AC-15:** Output MP4 includes `-movflags +faststart` (verifiable via `ffprobe -show_format`).
- [ ] **AC-16:** Volume outside `[0.0, 5.0]` throws `AudioMuxerError` before any async work, with message containing "volume".
- [ ] **AC-17:** `muxAudio()` throws `AudioMuxerError` with message containing "no video stream" when `videoPath` points to a file with no video stream.
- [ ] **AC-18:** `muxAudio()` throws `AudioMuxerError` with message containing "no audio stream" when `audioPath` points to a file with no audio stream.
- [ ] **AC-19:** FFmpeg is spawned via `child_process.spawn()` with arguments as an array, not via a shell string.
- [ ] **AC-20:** Works with both 1920x1080 and 1080x1920 video inputs (C-04).
- [ ] **AC-21:** The intermediate video-only MP4 (`videoPath`) is NOT deleted by `muxAudio()`.
- [ ] **AC-22:** `muxAudio()` throws `AudioMuxerError` with message containing "must differ" when `outputPath` equals `videoPath` or `audioPath` (comparison via `path.resolve()`).
- [ ] **AC-23:** `resolveFFprobePath()` returns a valid path when `ffprobe-static` is installed and no explicit path or env var is set.
- [ ] **AC-24:** `resolveFFprobePath()` throws `AudioMuxerError` with message containing "ffprobe" when no ffprobe binary can be found.
- [ ] **AC-25:** `durationStrategy: 'match_video'` with audio longer than video produces output whose duration matches video duration (audio truncated).
- [ ] **AC-26:** `durationStrategy: 'match_audio'` with durations within `DURATION_EQUAL_THRESHOLD_MS` preserves `-c:v copy` (no re-encoding). `videoCodecAction: 'copy'`.

## Edge Cases and Error Handling

1. **Video file does not exist:** `probeMedia()` throws `AudioMuxerError`: `"Cannot probe file: {videoPath} does not exist or is unreadable."`. Caught before FFmpeg muxing.

2. **Audio file does not exist:** Same as above for `audioPath`.

3. **Video file has no video stream:** After probing, `muxAudio()` throws `AudioMuxerError`: `"Video file has no video stream: {videoPath}"`.

4. **Audio file has no audio stream:** After probing, `muxAudio()` throws `AudioMuxerError`: `"Audio file has no audio stream: {audioPath}"`.

5. **Duration mismatch with 'error' strategy:** After probing both files, if `Math.abs(videoDuration - audioDuration) * 1000 > toleranceMs`, throws `AudioMuxerError`: `"Duration mismatch: video is {v}s, audio is {a}s (delta {d}ms exceeds tolerance of {toleranceMs}ms)"`.

6. **Duration mismatch with 'match_audio' — video shorter by more than DURATION_EQUAL_THRESHOLD_MS:** Uses `tpad` filter to freeze last frame. Forces video re-encoding (`-c:v libx264 -preset ultrafast -crf 18`). `videoCodecAction` in result is `'reencode'`.

7. **Duration mismatch with 'match_audio' — video shorter by <= DURATION_EQUAL_THRESHOLD_MS:** No `tpad`, no `-t`. Preserves `-c:v copy`. Output may be up to 50ms shorter than audio — acceptable drift.

8. **Duration mismatch with 'match_audio' — video longer:** Uses `-t {audioDurationSeconds}` to truncate. Video is stream-copied. `videoCodecAction: 'copy'`.

9. **Duration mismatch with 'match_video' — audio shorter:** No duration flags needed. FFmpeg outputs until the longest input (video) ends. The tail of the video has no audio (silence). `videoCodecAction: 'copy'`.

10. **Duration mismatch with 'match_video' — audio longer:** Uses `-t {videoDurationSeconds}` to truncate output to video duration. `videoCodecAction: 'copy'`.

11. **Volume = 0.0:** Valid. Produces silent audio via `volume=0.0` filter. `audioCodecAction: 'encode'`.

12. **Volume > 5.0 or < 0.0:** Throws `AudioMuxerError` synchronously: `"Volume must be between 0.0 and 5.0, got {volume}"`. Thrown before probing.

13. **Output path collides with input path:** `muxAudio()` resolves all three paths via `path.resolve()` and checks for equality. Throws `AudioMuxerError`: `"Output path must differ from input paths: {outputPath} collides with {collidingInput}"`.

14. **Output path not writable / parent directory missing:** FFmpeg fails. Error surfaces as `AudioMuxerError` with FFmpeg's stderr.

15. **Corrupt audio file:** FFmpeg may partially succeed or fail. Error surfaces as `AudioMuxerError` with FFmpeg's stderr.

16. **Very short audio (< 1 second):** Works normally. No special handling.

17. **Audio has multiple streams:** `-map 1:a:0` selects only the first audio stream. Additional streams are ignored silently.

18. **ffprobe not found:** `resolveFFprobePath()` tries all five sources. If none work, throws `AudioMuxerError`: `"ffprobe binary not found. Install ffprobe-static, set FFPROBE_PATH, or ensure ffprobe is on your system PATH."`.

19. **Rounding drift between video and audio durations:** In production, the orchestrator computes `totalFrames = Math.round(audioDuration * fps)`. This can introduce up to `0.5 / fps` seconds of drift (~16ms at 30fps). The default `toleranceMs` of 100ms for the 'error' strategy and `DURATION_EQUAL_THRESHOLD_MS` of 50ms for `match_audio` both accommodate this comfortably.

20. **Audio codec is neither MP3 nor PCM (e.g., AAC, FLAC, Vorbis):** Treated as "needs re-encoding" — same path as WAV. `-c:a aac -b:a {audioBitrate}`. This ensures any audio format can be muxed, not just the two explicitly named in the seed.

21. **tpad + volume filter coexistence:** When `match_audio` requires `tpad` AND `volume !== 1.0`, both `-vf tpad=stop_mode=clone:stop_duration={delta}` and `-filter:a volume={volume}` appear in the same invocation. These operate on different streams (video filter vs. audio filter) and coexist without conflict.

## Test Strategy

### Unit Tests (`test/unit/audio-muxer.test.ts`)

1. **Volume validation:**
   - Volume 0.0: does not throw.
   - Volume 1.0: does not throw.
   - Volume 5.0: does not throw.
   - Volume -0.1: throws `AudioMuxerError` with "volume" in message.
   - Volume 5.1: throws `AudioMuxerError` with "volume" in message.

2. **Output path collision detection:**
   - `outputPath === videoPath`: throws `AudioMuxerError` with "must differ" in message.
   - `outputPath === audioPath`: throws `AudioMuxerError` with "must differ" in message.
   - Same path with different relative forms (e.g., `./out.mp4` vs `out.mp4`): still detected via `path.resolve()`.

3. **Duration strategy 'error' validation logic** (mock `probeMedia`):
   - Video 10.0s, audio 10.05s, toleranceMs 100 -> does not throw.
   - Video 10.0s, audio 10.2s, toleranceMs 100 -> throws with both durations in message.

4. **`match_audio` threshold logic** (mock `probeMedia`):
   - Video 10.0s, audio 10.04s -> no tpad (within 50ms threshold), videoCodecAction should be 'copy'.
   - Video 10.0s, audio 10.10s -> tpad applied, videoCodecAction should be 'reencode'.

5. **Audio codec detection logic** (mock `probeMedia`):
   - `audioCodec: 'mp3'` + volume 1.0 -> `audioCodecAction: 'copy'`.
   - `audioCodec: 'pcm_s16le'` + volume 1.0 -> `audioCodecAction: 'encode'`.
   - `audioCodec: 'mp3'` + volume 0.5 -> `audioCodecAction: 'encode'`.
   - `audioCodec: 'aac'` + volume 1.0 -> `audioCodecAction: 'encode'`.

### Integration Tests (`test/integration/audio-muxer.test.ts`)

These require FFmpeg and ffprobe on the system.

**Test fixture creation:**
- Short video-only MP4: Use OBJ-013's `FFmpegEncoder` (30 solid-color PNG frames at 30fps = 1s).
- Short WAV: `ffmpeg -f lavfi -i sine=frequency=440:duration=1 -ar 44100 test.wav` (via spawn).
- Short MP3: `ffmpeg -i test.wav -c:a libmp3lame -b:a 128k test.mp3` (via spawn).
- Longer WAV (2s): `ffmpeg -f lavfi -i sine=frequency=440:duration=2 -ar 44100 test_2s.wav`.
- Longer video (2s): 60 solid-color frames at 30fps.

6. **probeMedia — video-only MP4:** Returns `hasVideo: true`, `hasAudio: false`, `durationSeconds ~ 1.0`.
7. **probeMedia — WAV file:** Returns `hasVideo: false`, `hasAudio: true`, `audioCodec` containing `pcm`, `durationSeconds ~ 1.0`.
8. **probeMedia — MP3 file:** Returns `hasVideo: false`, `hasAudio: true`, `audioCodec` containing `mp3`.
9. **probeMedia — nonexistent file:** Throws `AudioMuxerError`.
10. **resolveFFprobePath — with ffprobe-static:** Returns a valid path.
11. **resolveFFprobePath — respects FFPROBE_PATH env var.**

12. **Mux video + MP3, volume 1.0:** Output has H.264 video + mp3 audio. `audioCodecAction: 'copy'`. `videoCodecAction: 'copy'`.
13. **Mux video + WAV, volume 1.0:** Output has H.264 video + AAC audio. `audioCodecAction: 'encode'`.
14. **Mux video + MP3, volume 0.5:** Output has AAC audio. `audioCodecAction: 'encode'`.
15. **Mux with no-video file as videoPath:** Throws with "no video stream".
16. **Mux with no-audio file as audioPath:** Throws with "no audio stream".

17. **`match_shortest` — 1s video + 2s audio:** Output duration ~ 1s.
18. **`match_audio` — 1s video + 2s audio:** Output duration ~ 2s. `videoCodecAction: 'reencode'`. Last frame frozen.
19. **`match_audio` — equal durations (1s each):** Output duration ~ 1s. `videoCodecAction: 'copy'`.
20. **`match_video` — 2s video + 1s audio:** Output duration ~ 2s.
21. **`match_video` — 1s video + 2s audio:** Output duration ~ 1s (audio truncated).
22. **`error` — within tolerance:** 1.0s video, 1.05s audio, toleranceMs 100. Succeeds.
23. **`error` — exceeds tolerance:** 1.0s video, 2.0s audio, toleranceMs 100. Throws.

24. **Portrait mode (1080x1920):** Mux succeeds, `ffprobe` reports 1080x1920.
25. **faststart flag:** Verify output has faststart via `ffprobe -show_format`.
26. **Intermediate file preserved:** Verify `videoPath` still exists after muxing.

### Relevant Testable Claims
- **TC-06** (deterministic output): Same video + same audio + same config -> same output. When using stream copy for both streams, output should be byte-identical. When re-encoding, visually indistinguishable.
- **TC-13** (audio duration drives total video length): Validated at the orchestrator level (OBJ-038), but OBJ-014's `match_audio` strategy is the encoding-level mechanism that makes it work.

## Integration Points

### Depends on
- **OBJ-013** (`FFmpegEncoder`, `resolveFFmpegPath`): Imports `resolveFFmpegPath()` for FFmpeg binary resolution. Consumes the video-only MP4 produced by `FFmpegEncoder.finalize()` — specifically `FFmpegEncoderResult.outputPath`.
- **OBJ-001** (Project scaffolding): Provides `src/engine/audio-muxer.ts` stub path, TypeScript build pipeline, `"type": "module"` ESM context. **New dependency for this module:** `ffprobe-static` must be added to `package.json` dependencies.

### Consumed by
- **OBJ-038** (Audio sync and scene timing): Uses `muxAudio()` as the final step after the orchestrator has rendered video and prepared audio. May also use `probeMedia()` for duration computation. OBJ-038 handles the higher-level concern of computing frame counts and scene durations from audio; OBJ-014 handles the mechanical muxing.
- **OBJ-035** (Orchestrator): Primary consumer. After OBJ-013's encoder produces a video-only MP4 and audio is available, the orchestrator calls `muxAudio()` to produce the final deliverable.

### File Placement
- **Implementation:** `src/engine/audio-muxer.ts`
- **Unit tests:** `test/unit/audio-muxer.test.ts`
- **Integration tests:** `test/integration/audio-muxer.test.ts`

## Open Questions

1. **Should `muxAudio` support multiple audio tracks?** The manifest schema (Section 4.6) shows a single `audio` object. Background music + narration would need mixing before muxing, which is arguably a separate concern. Current spec: single audio input. If multi-track is needed, it would be a separate utility or a future extension.

2. **Should the module handle video-without-audio as a pass-through?** If no audio file is provided, should `muxAudio()` just copy the video? Current spec: both `videoPath` and `audioPath` are required. The orchestrator should skip muxing if there's no audio. This avoids a degenerate code path.

3. **AAC encoder selection:** FFmpeg's built-in AAC encoder (`-c:a aac`) is acceptable quality. `libfdk_aac` is higher quality but requires a non-free FFmpeg build. Current spec uses the built-in encoder for zero-license compatibility (C-01 spirit).

4. **Should `probeMedia` be extracted to a shared utility?** Other modules (OBJ-038) may need to probe files. For now it lives in `audio-muxer.ts` as the first consumer. If OBJ-038 needs it, it can import from here, or a shared `src/engine/media-probe.ts` can be extracted. This refactoring can be deferred.

5. **`probeMedia` parameter naming:** The `ffmpegPath` parameter on `probeMedia` is passed through to `resolveFFprobePath()` for co-location resolution — it is not used to invoke FFmpeg directly. A future refactor could rename this to `ffprobePath` for clarity, but the current signature is documented and functional.
