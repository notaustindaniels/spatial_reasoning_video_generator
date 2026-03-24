# Deliberation Transcript: OBJ-014

---

## Round 1 — spec_author

Looking at OBJ-014's metadata, its dependency (OBJ-013), and the relevant seed constraints. Let me propose the specification.
[Tool: ToolSearch]
  Input: {
  "query": "select:Read",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Read'}]


Now let me check the current state of the project and any existing OBJ-014 files:
[Tool: ToolSearch]
  Input: {
  "query": "select:Glob,Bash",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Glob'}, {'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-014/**/*"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/meta.json

[Tool: Glob]
  Input: {
  "pattern": "src/engine/ffmpeg*"
}
[Tool Result] No files found

[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-013/output.md"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-014",
     3→  "description": "FFmpeg audio muxing -- audio track integration (WAV and MP3 input), synchronization strategy, single-pass vs two-pass encoding decision (mux audio in the same FFmpeg invocation as video frames, or in a separate remux pass). Covers C-07 (audio synchronization) at the encoding level.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-013"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Separate from frame encoding (OBJ-013) because audio muxing is an additional concern."
    12→}
    13→
Good. Now let me check what OBJ-038 expects (since OBJ-014 blocks it):
[Tool: Glob]
  Input: {
  "pattern": "nodes/OBJ-038/meta.json"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-038/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-038",
     3→  "description": "Audio sync and scene timing -- duration distribution algorithm per Section 8.7: audio-driven (T = audio_duration, scenes share proportionally), explicit (T = sum of scene durations + transition overlaps), or combined (explicit durations with audio mismatch warning). Timestamp-based scene boundary alignment to narration cues. Covers C-07 (audio synchronization) and TC-13 (audio duration drives total video length).",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-009", "OBJ-014", "OBJ-016"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 3 engine integration."
    12→}
    13→
Now I have everything I need. Let me also quickly check OBJ-013's implementation status to understand what's been built:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-013/output.md",
  "limit": 50
}
[Tool Result]      1→# Specification: OBJ-013 — FFmpeg Encoder
     2→
     3→## Summary
     4→
     5→OBJ-013 implements the FFmpeg encoding module (`src/engine/ffmpeg-encoder.ts`) — the final stage of the rendering pipeline that receives raw pixel buffers via its API, pipes them to an FFmpeg child process over stdin, and produces an H.264-encoded MP4 file. This module is deliberately independent of Puppeteer: it accepts `Buffer` data from any source, making it testable in isolation and reusable if the frame-capture mechanism changes. It implements the encoding half of constraint C-02 and supports the determinism guarantee of C-05.
     6→
     7→Audio muxing is **out of scope** — that is OBJ-014's responsibility. This module produces a video-only MP4.
     8→
     9→## Interface Contract
    10→
    11→```typescript
    12→// src/engine/ffmpeg-encoder.ts
    13→
    14→/**
    15→ * Supported input pixel formats for frame data piped to FFmpeg.
    16→ * - 'png': Each frame is a complete PNG-encod... [truncated]
Good — I've confirmed OBJ-013's spec is exactly what was provided in the dependency specs above. Now I have full context to propose the OBJ-014 specification.

---

# Proposed Specification: OBJ-014 — FFmpeg Audio Muxing

## Summary

OBJ-014 implements the audio muxing module (`src/engine/audio-muxer.ts`) — the post-encoding stage that combines OBJ-013's video-only MP4 with an audio file (WAV or MP3) to produce the final deliverable MP4 with synchronized audio. This module covers constraint C-07 (audio synchronization) at the encoding level, making the single-pass vs. two-pass decision, handling format differences between WAV and MP3 inputs, and managing duration mismatches between video and audio streams.

This module is deliberately separate from OBJ-013's `FFmpegEncoder` — it operates on completed files, not on streaming frame data. It accepts file paths, not buffers.

## Interface Contract

```typescript
// src/engine/audio-muxer.ts

/**
 * Supported audio input formats.
 */
export type AudioFormat = 'wav' | 'mp3';

/**
 * Strategy for handling duration mismatches between video and audio.
 *
 * - 'match_shortest': Output duration equals the shorter of video/audio.
 *   The longer stream is truncated. Uses FFmpeg's `-shortest` flag.
 *
 * - 'match_audio': Output duration equals audio duration.
 *   If video is shorter than audio, the last video frame is held (frozen)
 *   for the remaining audio duration. If video is longer than audio,
 *   audio is padded with silence to match video duration.
 *   This is the expected mode for production: the orchestrator (OBJ-035)
 *   computes frame count from audio duration, so durations should already
 *   match — this mode exists as a safety net for minor rounding drift.
 *
 * - 'match_video': Output duration equals video duration.
 *   If audio is shorter, it ends and the remaining video plays in silence.
 *   If audio is longer, it is truncated to match video.
 *
 * - 'error': Reject if durations differ by more than `toleranceMs`.
 *   This is the strictest mode — used for testing deterministic alignment.
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
   * See DurationStrategy for details.
   */
  durationStrategy?: DurationStrategy;

  /**
   * Tolerance in milliseconds for the 'error' duration strategy.
   * If abs(videoDuration - audioDuration) > toleranceMs, muxing
   * fails with AudioMuxerError. Ignored for other strategies.
   * Default: 100 (allows up to 100ms drift from frame rounding).
   */
  toleranceMs?: number;

  /**
   * Audio volume adjustment. 1.0 = original volume.
   * Applied via FFmpeg's `-filter:a volume={volume}` filter.
   * When volume is exactly 1.0 (default), no audio filter is applied
   * and audio is stream-copied (`-c:a copy` for MP3, `-c:a aac` for WAV).
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

  /** Duration of the output file in seconds (from ffprobe). */
  durationSeconds: number;

  /** Whether the video stream was re-encoded or stream-copied. Always 'copy'. */
  videoCodecAction: 'copy';

  /** Whether the audio stream was re-encoded or stream-copied. */
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
 * Probes a media file using ffprobe, returning duration and stream info.
 *
 * Uses `ffprobe -v quiet -print_format json -show_format -show_streams`.
 * Spawned via child_process.spawn() with array arguments (no shell).
 *
 * The ffprobe binary is resolved from the same directory as the FFmpeg
 * binary (they are co-located in ffmpeg-static and in system installs).
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
 * The video stream is always stream-copied (-c:v copy) — never re-encoded.
 * This is fast (seconds, not minutes) and preserves OBJ-013's encoding
 * quality exactly.
 *
 * The audio stream handling depends on format and volume:
 * - MP3 input + volume 1.0: stream-copied (-c:a copy). Fastest.
 * - WAV input: always re-encoded to AAC (-c:a aac). WAV in MP4 is
 *   non-standard and poorly supported by players.
 * - Any input + volume !== 1.0: re-encoded to AAC with volume filter.
 *
 * Throws AudioMuxerError if:
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
**Choice:** Audio is muxed in a separate FFmpeg invocation after OBJ-013 produces a video-only MP4. The video stream is stream-copied (`-c:v copy`), never re-encoded.

**Rationale:**
1. **Separation of concerns (AP-04 adjacent):** OBJ-013's `FFmpegEncoder` manages a complex streaming lifecycle (spawn → pipe frames → finalize). Adding a second input stream for audio would complicate its backpressure handling, error recovery, and lifecycle management.
2. **Speed:** Stream-copying the video (`-c:v copy`) makes the remux nearly instantaneous (seconds for a 60s video vs. minutes for re-encoding). The audio transcode (WAV→AAC) is also fast.
3. **Flexibility:** The orchestrator (OBJ-035) may not have the audio file ready when frame rendering begins (e.g., TTS generation may run in parallel). Two-pass decouples video rendering from audio availability.
4. **Debuggability:** The intermediate video-only MP4 can be inspected independently.
5. **OBJ-013 compatibility:** OBJ-013's spec explicitly produces video-only MP4 and defers audio to OBJ-014. Modifying OBJ-013 would require reopening a verified objective.

**Trade-off:** An intermediate file is written to disk. For a 60s 1080p video at CRF 23, this is roughly 10-30MB — negligible.

### D-02: Function over Class
**Choice:** `muxAudio()` is a standalone async function, not a class with lifecycle methods.

**Rationale:** Unlike OBJ-013's frame-by-frame streaming, muxing is a single atomic operation: spawn FFmpeg with two file inputs, wait for completion. There is no streaming lifecycle to manage. A function is simpler and maps directly to the operation.

### D-03: Video Stream Always Copied, Never Re-encoded
**Choice:** The video stream uses `-c:v copy` unconditionally.

**Rationale:** OBJ-013 already encoded to H.264 with the desired quality settings. Re-encoding would be slow (defeating the two-pass speed advantage) and would introduce generation loss. There is no scenario in OBJ-014's scope where the video needs re-encoding.

### D-04: WAV Always Re-encoded to AAC; MP3 Copied When Possible
**Choice:**
- WAV input → always re-encode to AAC (`-c:a aac -b:a 192k`).
- MP3 input + volume 1.0 → stream-copy (`-c:a copy`).
- Any input + volume ≠ 1.0 → re-encode to AAC with volume filter.

**Rationale:** WAV (PCM) inside an MP4 container is technically possible but has poor player compatibility — many browsers and mobile players don't support it. AAC is the standard audio codec for MP4. MP3 in MP4 is well-supported, so stream-copying avoids unnecessary transcoding and quality loss.

### D-05: Normative FFmpeg Argument Arrays
**Choice:** The following are the **complete, definitive** argument arrays for each scenario. The implementer must construct these exactly, substituting config values.

**Scenario A — MP3 input, volume 1.0, `match_shortest` strategy:**
```
ffmpeg
  -y
  -i {videoPath}
  -i {audioPath}
  -c:v copy
  -c:a copy
  -map 0:v:0
  -map 1:a:0
  -shortest
  -movflags +faststart
  {outputPath}
```

**Scenario B — WAV input, volume 1.0, `match_shortest` strategy:**
```
ffmpeg
  -y
  -i {videoPath}
  -i {audioPath}
  -c:v copy
  -c:a aac
  -b:a {audioBitrate}
  -map 0:v:0
  -map 1:a:0
  -shortest
  -movflags +faststart
  {outputPath}
```

**Scenario C — Any input, volume ≠ 1.0, `match_shortest` strategy:**
```
ffmpeg
  -y
  -i {videoPath}
  -i {audioPath}
  -c:v copy
  -c:a aac
  -b:a {audioBitrate}
  -filter:a volume={volume}
  -map 0:v:0
  -map 1:a:0
  -shortest
  -movflags +faststart
  {outputPath}
```

**Duration strategy flag mapping:**
- `match_shortest` → add `-shortest` flag
- `match_video` → add `-shortest` flag (same effect: audio truncated or video keeps going with silence — FFmpeg naturally stops at end of video since video is a fixed-length file)
- `match_audio` → no `-shortest` flag; instead use `-stream_loop -1` on video input to loop/extend video frames if needed, BUT this loops the entire video which is wrong. **Revised approach:** For `match_audio`, if video is shorter than audio, add an FFmpeg filter to pad the last frame: use `-vf tpad=stop_mode=clone:stop_duration={delta}` where `delta` is `audioDuration - videoDuration`. If video is longer, add `-t {audioDuration}` to truncate. If durations are equal (within 50ms), use neither flag.
- `error` → no FFmpeg flags; validation happens before FFmpeg is spawned

**Revised Scenario — `match_audio`, video shorter than audio, WAV input, volume 1.0:**
```
ffmpeg
  -y
  -i {videoPath}
  -i {audioPath}
  -c:v libx264
  -preset ultrafast
  -crf 18
  -c:a aac
  -b:a {audioBitrate}
  -vf tpad=stop_mode=clone:stop_duration={deltaSeconds}
  -map 0:v:0
  -map 1:a:0
  -movflags +faststart
  {outputPath}
```

**Important:** When the `tpad` video filter is used, the video **must** be re-encoded (cannot use `-c:v copy` with filters). In this case, use `-c:v libx264 -preset ultrafast -crf 18` to re-encode as quickly as possible with minimal quality loss. This is the **only** scenario where video re-encoding occurs, and it should be rare — the orchestrator should compute frame count from audio duration, making the durations match within a frame or two.

**Scenario — `match_audio`, video longer than audio, MP3 input, volume 1.0:**
```
ffmpeg
  -y
  -i {videoPath}
  -i {audioPath}
  -c:v copy
  -c:a copy
  -t {audioDurationSeconds}
  -map 0:v:0
  -map 1:a:0
  -movflags +faststart
  {outputPath}
```

### D-06: Pre-Mux Validation via ffprobe
**Choice:** Before spawning the muxing FFmpeg process, `muxAudio()` probes both input files via `probeMedia()` to validate existence, stream presence, and duration.

**Rationale:** Fail-fast with clear error messages (C-10 spirit). FFmpeg's own error messages for missing streams or corrupt files are often cryptic. Probing first lets us provide actionable errors: "Audio file has no audio stream" rather than FFmpeg's "Stream map '1:a:0' matches no streams."

### D-07: ffprobe Binary Resolution
**Choice:** The ffprobe binary is resolved by taking the directory of the resolved FFmpeg binary and looking for `ffprobe` in the same directory. Falls back to `ffprobe` on system PATH.

**Rationale:** `ffmpeg-static` bundles both `ffmpeg` and `ffprobe` in the same directory. System installs also co-locate them. Using the same resolution strategy as OBJ-013 (importing `resolveFFmpegPath()`) and deriving `ffprobe`'s path from it is reliable.

### D-08: `-movflags +faststart` Preserved
**Choice:** Always include `-movflags +faststart` on the muxed output.

**Rationale:** The video-only MP4 from OBJ-013 already has this, but remuxing creates a new container. The flag must be re-applied to ensure the final deliverable supports web progressive playback (SC-01).

### D-09: Volume Validation Range
**Choice:** Volume must be in range `[0.0, 5.0]`. Validated before FFmpeg is spawned.

**Rationale:** Volume 0.0 is valid (mute). Values above 5.0 cause extreme distortion and clipping. This is a sensible guard rail, not an FFmpeg limitation.

### D-10: `-map` Flags for Explicit Stream Selection
**Choice:** Always use `-map 0:v:0 -map 1:a:0` to explicitly select the first video stream from input 0 and the first audio stream from input 1.

**Rationale:** Without explicit mapping, FFmpeg's automatic stream selection may behave unexpectedly if either input has multiple streams. Explicit mapping is defensive and predictable.

### D-11: Intermediate File Cleanup is Caller's Responsibility
**Choice:** `muxAudio()` does not delete the intermediate video-only MP4 (`videoPath`). Cleanup is the orchestrator's responsibility.

**Rationale:** Consistent with OBJ-013's D-13 (abort doesn't delete partial output). The orchestrator may want to keep the intermediate for debugging.

## Acceptance Criteria

- [ ] **AC-01:** `muxAudio` function, `probeMedia` function, `AudioMuxerError` class, and all types (`AudioFormat`, `DurationStrategy`, `AudioMuxerConfig`, `AudioMuxerResult`, `MediaProbeResult`) are exported from `src/engine/audio-muxer.ts`.
- [ ] **AC-02:** `probeMedia()` returns correct `durationSeconds`, `hasVideo`, `hasAudio`, `audioCodec`, and `audioSampleRate` for a known WAV file.
- [ ] **AC-03:** `probeMedia()` returns correct metadata for a known MP3 file.
- [ ] **AC-04:** `probeMedia()` returns correct metadata for a video-only MP4 (produced by OBJ-013): `hasVideo: true`, `hasAudio: false`.
- [ ] **AC-05:** `probeMedia()` throws `AudioMuxerError` for a nonexistent file path, with a message containing the file path.
- [ ] **AC-06:** Muxing a video-only MP4 with an MP3 file (volume 1.0) produces a valid MP4 that `ffprobe` reports as having both a video stream (H.264) and an audio stream (mp3). The video stream is bit-identical to the input (stream-copied).
- [ ] **AC-07:** Muxing a video-only MP4 with a WAV file produces a valid MP4 with video (H.264) and audio (AAC) streams.
- [ ] **AC-08:** When `volume` is set to 0.5, the output audio is re-encoded to AAC regardless of input format.
- [ ] **AC-09:** `durationStrategy: 'error'` throws `AudioMuxerError` when `abs(videoDuration - audioDuration) > toleranceMs`, with a message containing both durations.
- [ ] **AC-10:** `durationStrategy: 'error'` succeeds when durations differ by less than `toleranceMs`.
- [ ] **AC-11:** `durationStrategy: 'match_shortest'` produces output whose duration equals the shorter input (within 100ms tolerance).
- [ ] **AC-12:** `durationStrategy: 'match_audio'` with video shorter than audio produces output whose duration matches audio duration (within 100ms tolerance), with the last video frame held/frozen.
- [ ] **AC-13:** `durationStrategy: 'match_video'` with audio shorter than video produces output whose duration matches video duration (within 100ms tolerance).
- [ ] **AC-14:** The `AudioMuxerResult` includes correct `outputPath`, `durationSeconds > 0`, correct `audioCodecAction` ('copy' for MP3 at volume 1.0, 'encode' for WAV or volume ≠ 1.0), and non-empty `ffmpegLog`.
- [ ] **AC-15:** Output MP4 includes `-movflags +faststart` (verifiable via `ffprobe -show_format`).
- [ ] **AC-16:** Volume outside `[0.0, 5.0]` throws `AudioMuxerError` before FFmpeg is spawned, with message containing "volume".
- [ ] **AC-17:** `muxAudio()` throws `AudioMuxerError` with message "no video stream" when `videoPath` points to a file with no video stream.
- [ ] **AC-18:** `muxAudio()` throws `AudioMuxerError` with message "no audio stream" when `audioPath` points to a file with no audio stream.
- [ ] **AC-19:** FFmpeg is spawned via `child_process.spawn()` with arguments as an array, not via a shell string.
- [ ] **AC-20:** Works with both 1920×1080 and 1080×1920 video inputs (C-04).
- [ ] **AC-21:** The intermediate video-only MP4 (`videoPath`) is NOT deleted by `muxAudio()`.

## Edge Cases and Error Handling

1. **Video file does not exist:** `probeMedia()` throws `AudioMuxerError`: `"Cannot probe file: {videoPath} does not exist or is unreadable."`. This is caught before FFmpeg muxing is attempted.

2. **Audio file does not exist:** Same as above for `audioPath`.

3. **Video file has no video stream (e.g., audio-only file passed as video):** After probing, `muxAudio()` throws `AudioMuxerError`: `"Video file has no video stream: {videoPath}"`.

4. **Audio file has no audio stream (e.g., video-only file passed as audio):** After probing, `muxAudio()` throws `AudioMuxerError`: `"Audio file has no audio stream: {audioPath}"`.

5. **Duration mismatch with 'error' strategy:** After probing both files, if `Math.abs(videoDuration - audioDuration) * 1000 > toleranceMs`, throws `AudioMuxerError`: `"Duration mismatch: video is {v}s, audio is {a}s (delta {d}ms exceeds tolerance of {toleranceMs}ms)"`.

6. **Duration mismatch with 'match_audio' — video shorter:** Uses `tpad` filter to freeze last frame. This forces video re-encoding (libx264, ultrafast preset, CRF 18). The `videoCodecAction` in the result should still report `'copy'` — wait, no, it should accurately reflect what happened. **Decision:** Add a third possible value. Actually, let's keep `videoCodecAction` simple: it's always `'copy'` unless `tpad` is used, in which case it's `'reencode'`. Update the type: `videoCodecAction: 'copy' | 'reencode'`.

7. **Volume = 0.0:** Valid. Produces silent audio. FFmpeg handles `volume=0.0` correctly.

8. **Volume > 5.0 or < 0.0:** Throws `AudioMuxerError` synchronously: `"Volume must be between 0.0 and 5.0, got {volume}"`.

9. **Output path not writable / parent directory missing:** FFmpeg fails. Error surfaces as `AudioMuxerError` from the FFmpeg process, including stderr.

10. **Corrupt audio file (e.g., truncated WAV):** FFmpeg may partially succeed or fail. The error surfaces as `AudioMuxerError` with FFmpeg's stderr for diagnosis.

11. **Very short audio (< 1 second):** Should work — no special handling needed. The muxing is format-level, not content-aware.

12. **Audio has multiple streams:** The `-map 1:a:0` flag selects only the first audio stream. Additional streams are ignored silently.

13. **Output path same as input path:** FFmpeg with `-y` will overwrite the input, corrupting it. `muxAudio()` must validate that `outputPath` differs from both `videoPath` and `audioPath`. Throws `AudioMuxerError`: `"Output path must differ from input paths"`.

14. **ffprobe not found:** `probeMedia()` throws `AudioMuxerError`: `"ffprobe binary not found. It should be co-located with FFmpeg."`.

15. **Rounding drift between video and audio durations:** In production, the orchestrator computes `totalFrames = Math.round(audioDuration * fps)`. This can introduce up to `0.5 / fps` seconds of drift (≈16ms at 30fps). The default `toleranceMs` of 100ms for the 'error' strategy accommodates this comfortably. The `match_audio` strategy handles it via `tpad` (if video is short) or `-t` truncation (if video is long).

**Updated `videoCodecAction` type:**
```typescript
videoCodecAction: 'copy' | 'reencode';
```

## Test Strategy

### Unit Tests (`test/unit/audio-muxer.test.ts`)

1. **Volume validation:**
   - Volume 0.0 does not throw.
   - Volume 1.0 does not throw.
   - Volume 5.0 does not throw.
   - Volume -0.1 throws `AudioMuxerError` with "volume" in message.
   - Volume 5.1 throws `AudioMuxerError` with "volume" in message.

2. **Output path collision detection:**
   - `outputPath === videoPath` throws `AudioMuxerError` with "must differ" in message.
   - `outputPath === audioPath` throws `AudioMuxerError` with "must differ" in message.

3. **Duration strategy 'error' validation logic** (can be unit-tested by mocking `probeMedia`):
   - Video 10.0s, audio 10.05s, toleranceMs 100 → should not throw.
   - Video 10.0s, audio 10.2s, toleranceMs 100 → should throw with both durations in message.

### Integration Tests (`test/integration/audio-muxer.test.ts`)

These require FFmpeg and ffprobe on the system. Test fixtures needed:

**Test fixture creation:** Generate a short video-only MP4 using OBJ-013's `FFmpegEncoder` (30 frames of solid color at 30fps = 1 second). Generate a short WAV file using FFmpeg's `sine` audio source (`ffmpeg -f lavfi -i sine=frequency=440:duration=1 test.wav`). Generate a short MP3 from the WAV.

4. **probeMedia — video-only MP4:** Returns `hasVideo: true`, `hasAudio: false`, `durationSeconds ≈ 1.0`.
5. **probeMedia — WAV file:** Returns `hasVideo: false`, `hasAudio: true`, `audioCodec` containing `pcm`, `durationSeconds ≈ 1.0`.
6. **probeMedia — MP3 file:** Returns `hasVideo: false`, `hasAudio: true`, `audioCodec` containing `mp3`.
7. **probeMedia — nonexistent file:** Throws `AudioMuxerError`.

8. **Mux video + MP3, volume 1.0:** Output has video (H.264) + audio (mp3). `audioCodecAction: 'copy'`. `videoCodecAction: 'copy'`.
9. **Mux video + WAV, volume 1.0:** Output has video (H.264) + audio (aac). `audioCodecAction: 'encode'`.
10. **Mux video + MP3, volume 0.5:** Output has audio (aac). `audioCodecAction: 'encode'`.
11. **Mux with no-video file as videoPath:** Throws with "no video stream".
12. **Mux with no-audio file as audioPath:** Throws with "no audio stream".

13. **Duration strategy 'match_shortest':** Create 1s video and 2s audio. Output duration ≈ 1s.
14. **Duration strategy 'match_audio', video shorter:** Create 1s video and 2s audio. Output duration ≈ 2s. `videoCodecAction: 'reencode'`.
15. **Duration strategy 'match_video':** Create 2s video and 1s audio. Output duration ≈ 2s.
16. **Duration strategy 'error', within tolerance:** 1.0s video, 1.05s audio, toleranceMs 100. Succeeds.
17. **Duration strategy 'error', exceeds tolerance:** 1.0s video, 2.0s audio, toleranceMs 100. Throws.

18. **Portrait mode (1080×1920):** Mux succeeds, `ffprobe` reports 1080×1920.
19. **faststart flag:** Verify output has faststart (moov atom before mdat) via `ffprobe -show_format`.
20. **Output file cleanup:** Verify `videoPath` still exists after muxing (not deleted by muxer).

### Relevant Testable Claims
- **TC-06** (deterministic output): Same video + same audio + same config → same output (when using stream copy, output should be byte-identical; when re-encoding, visually indistinguishable).
- **TC-13** (audio duration drives total video length): Validated at the orchestrator level (OBJ-038), but OBJ-014's `match_audio` strategy is the encoding-level mechanism that makes it work.

## Integration Points

### Depends on
- **OBJ-013** (`FFmpegEncoder`, `resolveFFmpegPath`): Imports `resolveFFmpegPath()` for FFmpeg binary resolution. Consumes the video-only MP4 produced by `FFmpegEncoder.finalize()` — specifically `FFmpegEncoderResult.outputPath`.

### Consumed by
- **OBJ-038** (Audio sync and scene timing): Uses `muxAudio()` as the final step after the orchestrator has rendered video and prepared audio. OBJ-038 handles the higher-level concern of computing frame counts and scene durations from audio; OBJ-014 handles the mechanical muxing.
- **OBJ-035** (Orchestrator): Primary consumer. After OBJ-013's encoder produces a video-only MP4 and audio is available, the orchestrator calls `muxAudio()` to produce the final deliverable.

### File Placement
- **Implementation:** `src/engine/audio-muxer.ts`
- **Unit tests:** `test/unit/audio-muxer.test.ts`
- **Integration tests:** `test/integration/audio-muxer.test.ts`

## Open Questions

1. **Should `muxAudio` support multiple audio tracks?** The manifest schema (Section 4.6) shows a single `audio` object. Background music + narration would need mixing before muxing, which is arguably a separate concern. Current spec: single audio input. If multi-track is needed, it would be a separate utility or a future extension to this module.

2. **Should the module also handle video-without-audio as a pass-through?** If no audio file is provided, should `muxAudio()` just copy the video? Or should the caller skip muxing entirely? Current spec: both `videoPath` and `audioPath` are required. The orchestrator should skip muxing if there's no audio. This is simpler and avoids a degenerate code path.

3. **AAC encoder selection:** FFmpeg's built-in AAC encoder (`-c:a aac`) is acceptable quality. `libfdk_aac` is higher quality but requires a non-free build of FFmpeg. Current spec uses the built-in encoder for zero-license compatibility (C-01 spirit). If quality is insufficient, the caller can pre-encode audio to MP3/AAC before passing it to `muxAudio()`.

4. **Should `probeMedia` be in this module or a shared utility?** Other modules (OBJ-038 for duration computation) may also need to probe files. For now, it lives in `audio-muxer.ts` since it's the first consumer. If OBJ-038 needs it, it can import from here, or it can be extracted to a shared `src/engine/media-probe.ts` utility. This refactoring decision can be made by the implementer or deferred to OBJ-038.

---

I believe this specification is complete and covers all the concerns in OBJ-014's description: WAV and MP3 input handling, synchronization strategy (via `DurationStrategy`), single-pass vs. two-pass decision (two-pass, with rationale), and C-07 at the encoding level. I'd like the Challenger to review and identify any gaps or issues.

---

## Round 2 — spec_challenger

I've read the proposed spec carefully. There's a lot to like here — the two-pass decision is well-reasoned, the `DurationStrategy` enum is a clean abstraction, the separation from OBJ-013 is appropriate, and the test strategy is concrete. But I've found several issues that would cause an implementer to guess or produce incorrect behavior.

---

## Critical Issues

### C1: `match_video` FFmpeg implementation is wrong

The spec says:

> `match_video` → add `-shortest` flag (same effect: audio truncated or video keeps going with silence — FFmpeg naturally stops at end of video since video is a fixed-length file)

This is **backwards**. `-shortest` stops encoding when the **shortest** input ends. If audio is 1s and video is 2s, `-shortest` produces 1s of output — the opposite of `match_video`'s documented behavior ("Output duration equals video duration").

**Fix:** For `match_video`:
- If audio is shorter than video: Do NOT use `-shortest`. Use no duration flag (FFmpeg outputs until the longest input ends, so output = video duration; the tail has silence). Or use `-t {videoDurationSeconds}` for explicitness.
- If audio is longer than video: Use `-t {videoDurationSeconds}` to truncate audio to match video.
- Provide a normative argument array for this strategy, just like you did for `match_audio`.

### C2: Interface contract `videoCodecAction` type contradicts edge case update

The interface contract declares:
```typescript
/** Whether the video stream was re-encoded or stream-copied. Always 'copy'. */
videoCodecAction: 'copy';
```

But edge case 6 later amends this to `'copy' | 'reencode'` because `tpad` forces re-encoding. The interface as written is the contract an implementer codes against — the edge case narrative is supplementary. The interface must be self-consistent.

**Fix:** Update the `AudioMuxerResult` interface to:
```typescript
videoCodecAction: 'copy' | 'reencode';
```
And update the JSDoc to explain when each value occurs.

### C3: ffprobe availability is assumed but not guaranteed

The spec says:

> The ffprobe binary is resolved from the same directory as the FFmpeg binary (they are co-located in ffmpeg-static and in system installs).

**`ffmpeg-static` does not include ffprobe.** The npm package `ffmpeg-static` provides only the ffmpeg binary. ffprobe requires a separate package (`ffprobe-static` or `@ffprobe-installer/ffprobe`). The spec's resolution strategy will silently fail in environments that only have `ffmpeg-static` installed.

**Fix:** Either:
(a) Add `ffprobe-static` as an allowed dependency (it's MIT licensed — compliant with C-01), and define a `resolveFFprobePath()` function with explicit resolution order: explicit path → `FFPROBE_PATH` env → `ffprobe-static` package → co-located with FFmpeg binary → system PATH. Or:
(b) Avoid ffprobe entirely by parsing FFmpeg's stderr output (FFmpeg prints stream info when processing). But this is fragile — option (a) is better.

I'd recommend option (a), and it should be listed in the interface contract.

---

## Major Issues

### M1: Normative FFmpeg arg arrays are incomplete — implementer must guess combinations

The spec provides normative args for:
- MP3 + volume 1.0 + `match_shortest`
- WAV + volume 1.0 + `match_shortest`
- Any + volume ≠ 1.0 + `match_shortest`
- `match_audio` + video shorter (with tpad)
- `match_audio` + video longer

But the strategy flags and codec/volume decisions are **orthogonal concerns** that combine. The spec doesn't show how to compose them. For example: `match_video` + WAV + volume 0.5 — which flags apply? An implementer must reverse-engineer the composition rules from scattered examples.

**Fix:** Refactor D-05 into two clearly separated layers:

1. **Codec decision table** (determines `-c:a` and `-filter:a`):
   | Input | Volume | Audio codec flags |
   |-------|--------|-------------------|
   | MP3 | 1.0 | `-c:a copy` |
   | MP3 | ≠ 1.0 | `-c:a aac -b:a {bitrate} -filter:a volume={vol}` |
   | WAV | 1.0 | `-c:a aac -b:a {bitrate}` |
   | WAV | ≠ 1.0 | `-c:a aac -b:a {bitrate} -filter:a volume={vol}` |

2. **Duration strategy flag table** (determines duration/padding flags):
   | Strategy | Video ≈ Audio | Video < Audio | Video > Audio |
   |----------|---------------|---------------|---------------|
   | `match_shortest` | `-shortest` | `-shortest` | `-shortest` |
   | `match_audio` | (no flag) | `-vf tpad=...` + reencode | `-t {audioDur}` |
   | `match_video` | (no flag) | `-t {videoDur}` | (no flag) |
   | `error` | (no flag) | N/A (rejected) | N/A (rejected) |

Then one complete normative template that shows where each group of flags goes in the argument array.

### M2: Missing acceptance criterion for output path collision

Edge case 13 specifies that `outputPath` must differ from `videoPath` and `audioPath`, but no AC covers this. It's a validation behavior that should be testable.

**Fix:** Add AC-22: `muxAudio()` throws `AudioMuxerError` with message containing "must differ" when `outputPath` equals `videoPath` or `audioPath`.

### M3: `match_audio` "near equal" threshold is underspecified

D-05 says:

> If durations are equal (within 50ms), use neither flag.

Where does 50ms come from? This is a magic number that determines whether `tpad` (and thus re-encoding) kicks in. At 30fps, a frame is 33ms, so 50ms is ~1.5 frames of drift. At 24fps, it's ~1.2 frames.

More importantly: is this 50ms threshold applied only to `match_audio`, or also to `match_video` and `match_shortest`? The spec only mentions it for `match_audio`.

**Fix:** Define this as a named constant in the spec (e.g., `DURATION_EQUAL_THRESHOLD_MS = 50`) with rationale tied to frame duration. State explicitly that it applies only to `match_audio` (since `match_shortest` and `match_video` use flags that are idempotent for equal durations). Document that within this threshold, no `tpad` or `-t` is needed, preserving `-c:v copy`.

### M4: `durationSeconds` in `AudioMuxerResult` — where does it come from?

The interface says:
```typescript
/** Duration of the output file in seconds (from ffprobe). */
durationSeconds: number;
```

The "(from ffprobe)" comment implies that `muxAudio()` probes the output file after FFmpeg completes. But this behavior is never described in the function's implementation notes or the normative flow. An implementer might compute it from inputs instead.

**Fix:** State explicitly in the function description or in a design decision: "After FFmpeg completes successfully, `muxAudio()` calls `probeMedia()` on the output file to populate `durationSeconds`. This ensures the reported duration reflects what FFmpeg actually produced, not what was computed from inputs."

---

## Minor Issues

### m1: Audio sample rate not addressed

WAV files can have wildly different sample rates (8000, 22050, 44100, 48000). When re-encoding to AAC, FFmpeg's built-in AAC encoder defaults to the input sample rate, which might produce suboptimal results for some rates. The normative args don't include `-ar`.

**Fix:** Add a note in D-04 or D-05: "No explicit `-ar` flag is set; FFmpeg preserves the input audio sample rate during transcoding. This is acceptable for standard rates (44100, 48000). Unusual rates (e.g., 22050) may produce lower quality AAC but are not rejected." This makes it a conscious decision rather than an omission.

### m2: `tpad` filter interaction with `-filter:a volume` when both are needed

If `match_audio` requires `tpad` AND volume ≠ 1.0, the FFmpeg args need both `-vf tpad=...` and `-filter:a volume=...`. The spec shows these in separate scenarios but never shows them combined. Since they operate on different streams (video vs audio filter), they should compose cleanly, but it should be called out.

**Fix:** Add a note in D-05: "The video filter (`-vf tpad=...`) and audio filter (`-filter:a volume=...`) are independent and can coexist in the same FFmpeg invocation."

### m3: `AudioFormat` type is declared but never used

The interface declares `export type AudioFormat = 'wav' | 'mp3';` but no config field or function parameter uses it. It's dead weight.

**Fix:** Either remove it, or use it — e.g., add an optional `audioFormat?: AudioFormat` to `AudioMuxerConfig` that overrides auto-detection (for cases where the file extension doesn't match the content). Or if auto-detection from probing is sufficient (it should be), just remove the type.

---

## What's Sound

- **Two-pass decision (D-01):** Well-argued, correct. OBJ-013 shouldn't be reopened.
- **Function over class (D-02):** Appropriate for an atomic operation.
- **Pre-mux validation via ffprobe (D-06):** Good fail-fast pattern.
- **`-map` flags (D-10):** Defensive and correct.
- **Edge cases 1-5, 7-12, 14-15:** Thorough.
- **Test strategy structure:** Concrete fixtures, clear pass/fail criteria.
- **Scope discipline:** Stays within OBJ-014's boundary, doesn't bleed into OBJ-038's timing logic.

---

Please address the three critical issues (C1, C2, C3) and the four major issues (M1-M4) before I'll consider convergence. The minor issues can be addressed or documented as conscious decisions.

---

## Round 3 — spec_author

All the challenger's points are valid. Let me present the revised specification with every issue addressed.

---

# Revised Specification: OBJ-014 — FFmpeg Audio Muxing

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
1. **Separation of concerns:** OBJ-013's `FFmpegEncoder` manages a complex streaming lifecycle (spawn → pipe frames → finalize). Adding a second input stream for audio would complicate its backpressure handling, error recovery, and lifecycle management.
2. **Speed:** Stream-copying the video (`-c:v copy`) makes the remux nearly instantaneous (seconds for a 60s video vs. minutes for re-encoding). The audio transcode (WAV→AAC) is also fast.
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
**Choice:** The audio codec flags are determined by a two-axis table: input format × volume setting.

| Input Format | Volume = 1.0 | Volume ≠ 1.0 |
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
**Choice:** Duration handling is determined by a two-axis table: strategy × duration relationship. Duration comparison uses probed values from both input files.

| Strategy | Video ≈ Audio (within threshold) | Video < Audio | Video > Audio |
|---|---|---|---|
| **`match_shortest`** | `-shortest` | `-shortest` | `-shortest` |
| **`match_audio`** | no flag | `-vf tpad=stop_mode=clone:stop_duration={delta}` + video re-encode | `-t {audioDur}` |
| **`match_video`** | no flag | `-t {videoDur}` | no flag |
| **`error`** | no flag | rejected pre-FFmpeg | rejected pre-FFmpeg |

**"Video ≈ Audio" for `match_audio`:** Defined as `Math.abs(videoDuration - audioDuration) * 1000 <= DURATION_EQUAL_THRESHOLD_MS` (50ms). Within this threshold, no `tpad` or `-t` is applied, preserving `-c:v copy`. This threshold applies **only** to `match_audio`. `match_shortest` uses `-shortest` unconditionally (idempotent for equal durations). `match_video` uses no flag for equal durations (also idempotent — FFmpeg stops at the end of both streams). `error` uses its own configurable `toleranceMs`.

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

### D-07: Pre-Mux Validation via ffprobe
**Choice:** Before spawning the muxing FFmpeg process, `muxAudio()` probes both input files via `probeMedia()` to validate existence, stream presence, and duration. After muxing completes, `probeMedia()` is called on the output file to populate `AudioMuxerResult.durationSeconds`.

**Rationale:** Fail-fast with clear error messages (C-10 spirit). FFmpeg's own error messages for missing streams or corrupt files are often cryptic. Probing first lets us provide actionable errors: "Audio file has no audio stream" rather than FFmpeg's "Stream map '1:a:0' matches no streams." Post-mux probing ensures the reported output duration reflects reality.

### D-08: ffprobe Binary Resolution
**Choice:** Add `ffprobe-static` (MIT licensed, C-01 compliant) as an allowed dependency. Define `resolveFFprobePath()` with resolution order: explicit path → `FFPROBE_PATH` env → `ffprobe-static` package → co-located with resolved FFmpeg binary (same directory) → `ffprobe` on system PATH.

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
- [ ] **AC-20:** Works with both 1920×1080 and 1080×1920 video inputs (C-04).
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

7. **Duration mismatch with 'match_audio' — video shorter by ≤ DURATION_EQUAL_THRESHOLD_MS:** No `tpad`, no `-t`. Preserves `-c:v copy`. Output may be up to 50ms shorter than audio — acceptable drift.

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

19. **Rounding drift between video and audio durations:** In production, the orchestrator computes `totalFrames = Math.round(audioDuration * fps)`. This can introduce up to `0.5 / fps` seconds of drift (≈16ms at 30fps). The default `toleranceMs` of 100ms for the 'error' strategy and `DURATION_EQUAL_THRESHOLD_MS` of 50ms for `match_audio` both accommodate this comfortably.

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
   - Video 10.0s, audio 10.05s, toleranceMs 100 → does not throw.
   - Video 10.0s, audio 10.2s, toleranceMs 100 → throws with both durations in message.

4. **`match_audio` threshold logic** (mock `probeMedia`):
   - Video 10.0s, audio 10.04s → no tpad (within 50ms threshold), videoCodecAction should be 'copy'.
   - Video 10.0s, audio 10.10s → tpad applied, videoCodecAction should be 'reencode'.

5. **Audio codec detection logic** (mock `probeMedia`):
   - `audioCodec: 'mp3'` + volume 1.0 → `audioCodecAction: 'copy'`.
   - `audioCodec: 'pcm_s16le'` + volume 1.0 → `audioCodecAction: 'encode'`.
   - `audioCodec: 'mp3'` + volume 0.5 → `audioCodecAction: 'encode'`.
   - `audioCodec: 'aac'` + volume 1.0 → `audioCodecAction: 'encode'`.

### Integration Tests (`test/integration/audio-muxer.test.ts`)

These require FFmpeg and ffprobe on the system.

**Test fixture creation:**
- Short video-only MP4: Use OBJ-013's `FFmpegEncoder` (30 solid-color PNG frames at 30fps = 1s).
- Short WAV: `ffmpeg -f lavfi -i sine=frequency=440:duration=1 -ar 44100 test.wav` (via spawn).
- Short MP3: `ffmpeg -i test.wav -c:a libmp3lame -b:a 128k test.mp3` (via spawn).
- Longer WAV (2s): `ffmpeg -f lavfi -i sine=frequency=440:duration=2 -ar 44100 test_2s.wav`.
- Longer video (2s): 60 solid-color frames at 30fps.

6. **probeMedia — video-only MP4:** Returns `hasVideo: true`, `hasAudio: false`, `durationSeconds ≈ 1.0`.
7. **probeMedia — WAV file:** Returns `hasVideo: false`, `hasAudio: true`, `audioCodec` containing `pcm`, `durationSeconds ≈ 1.0`.
8. **probeMedia — MP3 file:** Returns `hasVideo: false`, `hasAudio: true`, `audioCodec` containing `mp3`.
9. **probeMedia — nonexistent file:** Throws `AudioMuxerError`.
10. **resolveFFprobePath — with ffprobe-static:** Returns a valid path.
11. **resolveFFprobePath — respects FFPROBE_PATH env var.**

12. **Mux video + MP3, volume 1.0:** Output has H.264 video + mp3 audio. `audioCodecAction: 'copy'`. `videoCodecAction: 'copy'`.
13. **Mux video + WAV, volume 1.0:** Output has H.264 video + AAC audio. `audioCodecAction: 'encode'`.
14. **Mux video + MP3, volume 0.5:** Output has AAC audio. `audioCodecAction: 'encode'`.
15. **Mux with no-video file as videoPath:** Throws with "no video stream".
16. **Mux with no-audio file as audioPath:** Throws with "no audio stream".

17. **`match_shortest` — 1s video + 2s audio:** Output duration ≈ 1s.
18. **`match_audio` — 1s video + 2s audio:** Output duration ≈ 2s. `videoCodecAction: 'reencode'`. Last frame frozen.
19. **`match_audio` — equal durations (1s each):** Output duration ≈ 1s. `videoCodecAction: 'copy'`.
20. **`match_video` — 2s video + 1s audio:** Output duration ≈ 2s.
21. **`match_video` — 1s video + 2s audio:** Output duration ≈ 1s (audio truncated).
22. **`error` — within tolerance:** 1.0s video, 1.05s audio, toleranceMs 100. Succeeds.
23. **`error` — exceeds tolerance:** 1.0s video, 2.0s audio, toleranceMs 100. Throws.

24. **Portrait mode (1080×1920):** Mux succeeds, `ffprobe` reports 1080×1920.
25. **faststart flag:** Verify output has faststart via `ffprobe -show_format`.
26. **Intermediate file preserved:** Verify `videoPath` still exists after muxing.

### Relevant Testable Claims
- **TC-06** (deterministic output): Same video + same audio + same config → same output. When using stream copy for both streams, output should be byte-identical. When re-encoding, visually indistinguishable.
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

---

## Changes from Round 1 → Round 2

**C1 (match_video wrong):** Completely replaced. `match_video` now uses no flag when audio is shorter (FFmpeg naturally outputs to the end of the longest input), and `-t {videoDur}` when audio is longer. Normative arg arrays updated. Added AC-25 to test audio-longer case.

**C2 (videoCodecAction type):** Fixed interface to `'copy' | 'reencode'` with JSDoc explaining when each occurs. Consistent throughout.

**C3 (ffprobe not in ffmpeg-static):** Added `ffprobe-static` as an explicit dependency. Created `resolveFFprobePath()` with 5-step resolution order. Added AC-23 and AC-24. Updated D-08.

**M1 (composable tables):** Refactored D-04 (audio codec) and D-05 (duration strategy) into explicit two-axis tables. Added D-06 as a single normative template showing where each flag group slots in. Noted tpad + volume filter coexistence.

**M2 (missing AC for path collision):** Added AC-22.

**M3 (50ms threshold):** Exported as `DURATION_EQUAL_THRESHOLD_MS` constant with rationale. Explicitly scoped to `match_audio` only. Added AC-26 to test the threshold boundary.

**M4 (durationSeconds source):** Updated `AudioMuxerResult.durationSeconds` JSDoc and D-07 to explicitly state post-mux probing.

**m1 (sample rate):** Added note in D-04 rationale.

**m2 (tpad + volume):** Added note in D-06 and edge case 21.

**m3 (unused AudioFormat type):** Removed. Format detection is now via `probeMedia()` codec inspection (D-04 rationale).

---

I believe this revision addresses all critical, major, and minor issues raised. I'd like the Challenger to verify and approve.

---

## Round 4 — spec_challenger

I've carefully verified every fix from Round 2 against the revised spec. Let me walk through my verification.

## Verification of Round 2 Fixes

**C1 (match_video wrong):** ✓ Fixed. D-05 table now correctly shows: Video < Audio → `-t {videoDur}`, Video > Audio → no flag. This is correct FFmpeg behavior. AC-25 covers the audio-longer case.

**C2 (videoCodecAction type):** ✓ Fixed. Interface now reads `videoCodecAction: 'copy' | 'reencode'` with JSDoc explaining when each occurs.

**C3 (ffprobe not in ffmpeg-static):** ✓ Fixed. `ffprobe-static` added as dependency, `resolveFFprobePath()` defined with 5-step resolution, AC-23 and AC-24 cover it, D-08 provides rationale.

**M1 (composable tables):** ✓ Fixed. D-04 (codec) and D-05 (duration) are clean two-axis tables. D-06 shows a single normative template with labeled slots. Tpad + volume coexistence noted.

**M2 (missing AC for path collision):** ✓ AC-22 added with `path.resolve()` normalization.

**M3 (50ms threshold):** ✓ Exported as `DURATION_EQUAL_THRESHOLD_MS` with frame-duration rationale. Explicitly scoped to `match_audio`. AC-26 tests the boundary.

**M4 (durationSeconds source):** ✓ JSDoc now says "obtained by calling probeMedia() on the output file after FFmpeg completes." D-07 restates this.

**m1-m3:** ✓ All addressed — sample rate noted as conscious decision, filter coexistence documented, unused `AudioFormat` type removed.

## One Minor New Issue

### m4: `probeMedia` parameter name misleads

```typescript
export function probeMedia(filePath: string, ffmpegPath?: string): Promise<MediaProbeResult>;
```

The second parameter is called `ffmpegPath` but this function needs **ffprobe**, not ffmpeg. An implementer will wonder whether to pass the ffmpeg path (for co-location resolution) or a direct ffprobe path. Meanwhile, `resolveFFprobePath` accepts both `ffmpegPath` and `ffprobePath` separately, creating an API mismatch.

**Fix (can be handled as an open question rather than a blocker):** Document in the spec that `probeMedia` internally calls `resolveFFprobePath(ffmpegPath)` using the provided parameter for co-location resolution. This is clear enough — I'll note it in the open questions when writing the final spec rather than requiring another revision round.

---

Everything else is structurally sound. The tables compose correctly, the edge cases are thorough, the ACs are testable, the scope stays within OBJ-014's boundaries, and the interfaces integrate cleanly with OBJ-013's contract. I'm satisfied.

CONCLUSION:

The specification for OBJ-014 defines the `audio-muxer.ts` module — a two-pass (remux) approach that combines OBJ-013's video-only MP4 with a WAV or MP3 audio file. Key decisions: video is stream-copied (never re-encoded except when `tpad` filter is needed for `match_audio`), audio codec selection follows a format×volume table, duration strategy is a clean four-option enum with composable FFmpeg flag tables, and `ffprobe-static` is added as a dependency for pre/post-mux probing. All critical and major issues from Round 2 have been verified as addressed in the revision.

Let me write the final spec to disk.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Now let me read the existing meta.json before updating it:
[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-014",
     3→  "description": "FFmpeg audio muxing -- audio track integration (WAV and MP3 input), synchronization strategy, single-pass vs two-pass encoding decision (mux audio in the same FFmpeg invocation as video frames, or in a separate remux pass). Covers C-07 (audio synchronization) at the encoding level.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": ["OBJ-013"],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 2 engine core. Separate from frame encoding (OBJ-013) because audio muxing is an additional concern."
    12→}
    13→
Good. Now let me write both files:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/output.md",
  "content": "# Specification: OBJ-014 \u2014 FFmpeg Audio Muxing\n\n## Summary\n\nOBJ-014 implements the audio muxing module (`src/engine/audio-muxer.ts`) \u2014 the post-encoding stage that combines OBJ-013's video-only MP4 with an audio file (WAV or MP3) to produce the final deliverable MP4 with synchronized audio. This module covers constraint C-07 (audio synchronization) at the encoding level, making the single-pass vs. two-pass decision, handling format differences between WAV and MP3 inputs, and managing duration mismatches between video and audio streams.\n\nThis module is deliberately separate from OBJ-013's `FFmpegEncoder` \u2014 it operates on completed files, not on streaming frame data. It accepts file paths, not buffers.\n\n## Interface Contract\n\n```typescript\n// src/engine/audio-muxer.ts\n\n/**\n * Strategy for handling duration mismatches between video and audio.\n *\n * - 'match_shortest': Output duration equals the shorter of video/audio.\n *   Uses FFmpeg's `-shortest` flag.\n *\n * - 'match_audio': Output duration equals audio duration.\n *   If video is shorter than audio by more than DURATION_EQUAL_THRESHOLD_MS,\n *   the last video frame is held (frozen) via the `tpad` filter, which forces\n *   video re-encoding. If video is longer, it is truncated via `-t`.\n *   If durations are within DURATION_EQUAL_THRESHOLD_MS, no adjustment is made.\n *   This is the expected production mode \u2014 the orchestrator computes frame count\n *   from audio duration, so durations should already match.\n *\n * - 'match_video': Output duration equals video duration.\n *   If audio is shorter, no flag is needed \u2014 FFmpeg outputs until the longest\n *   input ends, so the tail of the video plays in silence. If audio is longer,\n *   `-t {videoDurationSeconds}` truncates the output to video length.\n *\n * - 'error': Reject if durations differ b
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/output.md
Now update the meta.json:
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/meta.json",
  "content": "{\n  \"id\": \"OBJ-014\",\n  \"description\": \"FFmpeg audio muxing -- audio track integration (WAV and MP3 input), synchronization strategy, single-pass vs two-pass encoding decision (mux audio in the same FFmpeg invocation as video frames, or in a separate remux pass). Covers C-07 (audio synchronization) at the encoding level.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-23T02:30:00Z\",\n  \"depends_on\": [\"OBJ-013\"],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 2 engine core. Two-pass remux approach: OBJ-013 produces video-only MP4, this module muxes audio via separate FFmpeg invocation with -c:v copy. Adds ffprobe-static as a dependency. Supports WAV (re-encoded to AAC) and MP3 (stream-copied when volume=1.0). Four duration strategies: match_shortest, match_audio (default), match_video, error.\",\n  \"status\": \"specified\",\n  \"review_status\": \"approved\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-014/meta.json has been updated successfully.
Now commit to git:
[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-014/output.md nodes/OBJ-014/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-014): FFmpeg audio muxing specification\n\nTwo-pass remux approach: OBJ-013 produces video-only MP4, this module\nmuxes audio via separate FFmpeg invocation with -c:v copy. Adds\nffprobe-static dependency for pre/post-mux probing. Supports WAV\n(re-encoded to AAC) and MP3 (stream-copied at volume 1.0). Four\nduration strategies (match_shortest, match_audio, match_video, error)\nwith composable codec and duration flag tables.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Stage and commit OBJ-014 spec files"
}
[Tool Result] [master 4fb72b7] spec(OBJ-014): FFmpeg audio muxing specification
 2 files changed, 534 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-014/output.md
The specification has been written and committed. Here's a summary of the final agreed spec:

## OBJ-014 — FFmpeg Audio Muxing — Final Specification

**Core Decision:** Two-pass remux. OBJ-013 produces a video-only MP4; this module (`src/engine/audio-muxer.ts`) combines it with audio in a separate FFmpeg invocation using `-c:v copy` (no video re-encoding except when `tpad` is needed).

**Key interfaces:**
- `muxAudio(config)` — stateless async function (not a class), atomic operation
- `probeMedia(filePath)` — ffprobe wrapper for pre/post-mux validation
- `resolveFFprobePath()` — 5-step resolution (explicit → env → ffprobe-static → co-located → PATH)
- `DURATION_EQUAL_THRESHOLD_MS = 50` — threshold for `match_audio` tpad avoidance

**Four duration strategies:** `match_shortest`, `match_audio` (default), `match_video`, `error` — each with a clean flag table composable with the audio codec decision table (MP3 × volume → copy/encode).

**Issues resolved during deliberation:**
- **C1:** Fixed incorrect `match_video` FFmpeg flags (was using `-shortest`, now uses no flag / `-t`)
- **C2:** Fixed `videoCodecAction` type from `'copy'` to `'copy' | 'reencode'`
- **C3:** Added `ffprobe-static` dependency (ffmpeg-static doesn't include ffprobe)
- **M1:** Refactored scattered examples into composable codec + duration tables
- **M2:** Added AC-22 for output path collision
- **M3:** Named and scoped the 50ms threshold constant
- **M4:** Explicit post-mux probe for `durationSeconds`

**26 acceptance criteria**, **21 edge cases**, comprehensive unit + integration test strategy.
