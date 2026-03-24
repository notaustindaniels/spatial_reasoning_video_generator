# Specification: OBJ-077 — End-to-End Integration Test Plan

## Summary

OBJ-077 delivers the **end-to-end integration test plan** for depthkit — concrete, step-by-step procedures for verifying SC-01 (60-second, 5-scene video renders to valid MP4), SC-03 (performance target met), SC-05 (n8n POST/poll/download works), and SC-06 (manifest validation soundness). This document IS the test plan: it contains executable procedures with literal CLI commands, exact `ffprobe` invocations, and unambiguous pass/fail thresholds. OBJ-078 executes these procedures.

## Interface Contract

OBJ-077 produces no code module. Its deliverable is this test plan document (`output.md`). The plan specifies test fixtures, procedures, and validation commands that OBJ-078 follows.

---

## Resolved Design Questions

**Determinism Comparison Method:** Frame MD5 comparison as primary method. Extract per-frame checksums via `ffmpeg -i output.mp4 -f framemd5 -`. If frame MD5s differ, compute per-frame PSNR via `ffmpeg -i output1.mp4 -i output2.mp4 -lavfi psnr -f null -`. PSNR >= 60dB on all frames constitutes "visually indistinguishable." Below 60dB on any frame is a fail.

**Benchmark Run Count:** 3 runs, report median. No other CPU-intensive processes running during benchmark. Document all three values.

**SC-05 Poll Timeout:** 20-minute timeout, 10-second poll interval. Timeout is a fail condition.

**Smoke Test:** Included as Suite 0. A quick (<30 second) 2-second, 1-scene render at 320x240 validates the pipeline is functional before committing to full suites.

---

## Test Fixtures

### Fixture F-01: Benchmark Manifest

A single manifest used for both SC-01 (correctness) and SC-03 (performance). Exercises the full pipeline.

**Composition:**
```json
{
  "version": "3.0",
  "composition": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "audio": {
      "src": "./audio/test-60s.wav",
      "volume": 1.0
    }
  }
}
```

**Scene Layout (5 scenes, 60s total, explicit timing):**

| Scene | Geometry | Camera | Duration | start_time | transition_in | transition_out | Planes (slots) |
|-------|----------|--------|----------|------------|---------------|----------------|----------------|
| scene_001 | `tunnel` (OBJ-019) | `slow_push_forward` (OBJ-027) | 13.0s | 0.0 | `{ type: "dip_to_black", duration: 1.0 }` | `{ type: "crossfade", duration: 1.0 }` | floor, ceiling, left_wall, right_wall, end_wall (5 planes) |
| scene_002 | `stage` (OBJ-018) | `gentle_float` (OBJ-031) | 13.0s | 12.0 | `{ type: "crossfade", duration: 1.0 }` | `{ type: "cut" }` | backdrop, floor, subject (3 planes, only required) |
| scene_003 | `canyon` (OBJ-020) | `lateral_track_left` (OBJ-029) | 12.0s | 25.0 | `{ type: "cut" }` | `{ type: "dip_to_black", duration: 0.5 }` | floor, left_wall, right_wall, end_wall, sky (5 planes) |
| scene_004 | `flyover` (OBJ-021) | `crane_up` (OBJ-030) | 12.0s | 36.5 | `{ type: "dip_to_black", duration: 0.5 }` | `{ type: "crossfade", duration: 1.0 }` | ground, sky, landmark_1 (3+ planes per flyover geometry) |
| scene_005 | `stage` (OBJ-018) | `static` (OBJ-026) | 12.5s | 47.5 | `{ type: "crossfade", duration: 1.0 }` | `{ type: "dip_to_black", duration: 1.0 }` | backdrop, floor, subject (3 planes) |

**Timing verification:** Scene 1 ends at 13.0s, Scene 2 starts at 12.0s (1.0s crossfade overlap). Scene 2 ends at 25.0s, Scene 3 starts at 25.0s (cut). Scene 3 ends at 37.0s, Scene 4 starts at 36.5s (0.5s dip_to_black overlap). Scene 4 ends at 48.5s, Scene 5 starts at 47.5s (1.0s crossfade overlap). Scene 5 ends at 60.0s. Total composition duration: 60.0s.

**Coverage achieved:**
- 4 distinct geometry types: tunnel, stage, canyon, flyover (>= 3 required).
- 5 distinct camera presets: slow_push_forward, gentle_float, lateral_track_left, crane_up, static (>= 3 required).
- Transitions: 2 crossfade, 3 dip_to_black, 1 cut (all three types present).
- No manual coordinates: only geometry names, slot keys, camera preset names. No `position_override`, no `rotation_override`.
- 5 textured planes in scenes 1 and 3 (maximum typical load per C-08).

**Note on slot names:** The exact slot names depend on the verified geometry definitions (OBJ-018 through OBJ-021). OBJ-078 must consult each geometry's `PlaneSlot` definitions and adjust the manifest accordingly. The table above uses expected slot names; if a geometry defines different names, substitute them.

### Fixture F-01-AUDIO: Test Audio File

A 60-second WAV file. Generate via:
```bash
ffmpeg -f lavfi -i "sine=frequency=440:duration=60" -ar 44100 -ac 1 ./audio/test-60s.wav
```
A 440Hz tone. Content is irrelevant; duration is critical. Must be exactly 60.0s (+/- 0.01s).

### Fixture F-01-IMAGES: Test Images

Generate solid-color 1920x1080 PNGs in distinct colors per slot for visual identification. Use ImageMagick (`convert`) or any tool that produces valid PNGs:

```bash
mkdir -p images
convert -size 1920x1080 xc:'#8B0000' images/s1_floor.png      # dark red
convert -size 1920x1080 xc:'#00008B' images/s1_ceiling.png     # dark blue
convert -size 1920x1080 xc:'#006400' images/s1_left_wall.png   # dark green
convert -size 1920x1080 xc:'#4B0082' images/s1_right_wall.png  # indigo
convert -size 1920x1080 xc:'#FF8C00' images/s1_end_wall.png    # dark orange
```

Repeat for each scene with different color families (scene 1: warm, scene 2: cool, scene 3: earth tones, etc.) so human visual inspection can confirm correct scene ordering.

**Alternative if ImageMagick is unavailable:** Use `ffmpeg` to generate test images:
```bash
ffmpeg -f lavfi -i "color=c=#8B0000:s=1920x1080:d=0.04" -frames:v 1 images/s1_floor.png
```

The engine auto-adapts plane sizing from texture aspect ratio per seed Section 8.9, so 1920x1080 images are acceptable for all slot types.

### Fixture F-02: Smoke Test Manifest

A minimal manifest for Suite 0:

```json
{
  "version": "3.0",
  "composition": { "width": 320, "height": 240, "fps": 10 },
  "scenes": [{
    "id": "smoke_001",
    "duration": 2.0,
    "start_time": 0.0,
    "geometry": "stage",
    "camera": "static",
    "planes": {
      "backdrop": { "src": "./images/smoke_bg.png" },
      "subject": { "src": "./images/smoke_subject.png" }
    }
  }]
}
```

Generate 320x240 test images:
```bash
convert -size 320x240 xc:blue images/smoke_bg.png
convert -size 320x240 xc:red images/smoke_subject.png
```

Only required slots for `stage` geometry. No audio. Expected: 20 frames, ~2s video.

### Fixture F-03: SC-06 Valid Manifest Corpus

20 manifests exercising valid variations. Each is a separate JSON file. All use small resolutions (320x240) and short durations (1-3s at 10fps) for fast rendering.

| ID | Description | Key Properties |
|----|-------------|----------------|
| V-01 | Single scene, single required slot, no transitions, no audio | stage, static, 1.0s |
| V-02 | Single scene, all slots filled for tunnel geometry | tunnel, slow_push_forward, 2.0s, 5 planes |
| V-03 | 3 scenes with cut transitions only | stage x3, 1.0s each |
| V-04 | 2 scenes with crossfade transition (1.0s overlap) | stage, tunnel, 2.0s each |
| V-05 | 2 scenes with dip_to_black transitions | canyon, flyover, 2.0s each |
| V-06 | Mixed transitions: cut, crossfade, dip_to_black across 3 scenes | stage, tunnel, canyon |
| V-07 | Audio with explicit scene durations matching audio length | 3.0s audio, 3 scenes x 1.0s |
| V-08 | Audio present, scene durations sum to different value (warning expected) | 3.0s audio, scenes sum to 4.0s; expect `AUDIO_DURATION_MISMATCH` warning |
| V-09 | Portrait mode 240x320 (swapped) | stage, 1.0s |
| V-10 | 24fps variant | stage, 1.0s, 24fps |
| V-11 | 30fps variant | tunnel, 2.0s, 30fps |
| V-12 | Short scene 0.1s (3 frames at 30fps) | stage, static, 0.1s |
| V-13 | Scene with `camera_params.speed` override | tunnel, slow_push_forward, speed: 0.5 |
| V-14 | Scene with `camera_params.easing` override | stage, gentle_float, easing: "ease_out_cubic" |
| V-15 | Scene with optional slots omitted | stage with only required slots |
| V-16 | Scene with `scale: 1.5` on a PlaneRef | stage, subject plane scaled |
| V-17 | Scenes not in start_time order (warning expected) | 2 scenes, scene[0].start_time > scene[1].start_time; expect `SCENE_ORDER_MISMATCH` warning |
| V-18 | Tunnel geometry (OBJ-019) | Full 5-slot tunnel |
| V-19 | Canyon geometry (OBJ-020) with crane_up camera (OBJ-030) | Tests geometry/camera compatibility |
| V-20 | 10 scenes, each 0.3s, cuts only | Stress test for scene count |

**For each valid manifest:** Generate matching solid-color test images at the manifest's resolution. Where audio is needed, generate a sine tone of the required duration.

### Fixture F-04a: SC-06 Invalid Manifest Corpus -- Validation Failures

These fail at manifest validation (before any rendering). Testable via `depthkit validate`.

| ID | Description | Expected Error |
|----|-------------|----------------|
| E-01 | Missing `version` field | Zod structural error |
| E-02 | `version: "1.0"` (wrong version) | Zod structural error |
| E-03 | Missing `composition` field | Zod structural error |
| E-04 | `composition.width: 0` | Zod structural error (non-positive) |
| E-05 | `composition.fps: 0` | Zod structural error |
| E-06 | Empty `scenes` array | Zod structural error (min 1) |
| E-07 | Scene missing `geometry` field | Zod structural error |
| E-08 | Scene missing `duration` | Zod structural error |
| E-09 | Scene with `duration: -1` | Zod structural error |
| E-10 | Unknown geometry name `"tunl"` | `UNKNOWN_GEOMETRY` |
| E-11 | Unknown camera name `"push_fast"` | `UNKNOWN_CAMERA` |
| E-12 | Camera incompatible with geometry (use a camera whose `compatible_geometries` does not include the scene's geometry -- consult camera registry) | `INCOMPATIBLE_CAMERA` |
| E-13 | Missing required slot for geometry | `MISSING_REQUIRED_SLOT` |
| E-14 | Extra slot not defined by geometry | `UNKNOWN_SLOT` |
| E-15 | Crossfade transition_in on first scene (no predecessor) | `CROSSFADE_NO_ADJACENT` |
| E-16 | Duplicate scene IDs | Validation error |
| E-17 | Not valid JSON (syntax error in file) | `INVALID_JSON` |
| E-18 | Valid JSON but array instead of object | Zod structural error |
| E-19 | Valid JSON but a string `"hello"` | Zod structural error |
| E-20 | `geometry: ""` (empty string) | Validation error |
| E-21 | `camera: ""` (empty string) | Validation error |
| E-22 | `composition.width: 1.5` (non-integer if schema requires int) | Zod structural error |

### Fixture F-04b: SC-06 Pre-Flight Failures

These pass manifest validation but fail at orchestrator pre-flight. Must be tested via `depthkit render`, not `depthkit validate`.

| ID | Description | Expected Error Code |
|----|-------------|-------------------|
| P-01 | Image `src` pointing to non-existent file | `SCENE_SETUP_FAILED` |
| P-02 | Multiple missing images across scenes | `SCENE_SETUP_FAILED` (lists all missing) |
| P-03 | Audio `src` pointing to non-existent file | `AUDIO_MUX_FAILED` or `SCENE_SETUP_FAILED` (either is acceptable -- depends on whether OBJ-035 pre-flight checks audio existence; document whichever code is observed) |

### Fixture F-05: SC-05 n8n Test Payload

```json
{
  "topic": "Deep sea creatures",
  "duration": 30,
  "style": "cinematic documentary"
}
```

Execution gated on OBJ-057 and OBJ-075.

---

## Test Procedures

### Suite 0: Smoke Test

**Purpose:** Validate the pipeline is functional before committing to full suites. Not mapped to any SC.

#### SMOKE-01: Minimal Pipeline Smoke Test

**Preconditions:**
- `depthkit` CLI is installed and on PATH (or invokable via `npx`).
- `ffmpeg` and `ffprobe` are available: `ffmpeg -version` and `ffprobe -version` succeed.
- Puppeteer can launch headless Chromium: `node -e "const p = require('puppeteer'); p.launch({headless:true}).then(b => { console.log('OK'); b.close(); })"` succeeds.
- Smoke test fixtures (F-02) are generated.

**Steps:**
1. Generate test images:
   ```bash
   convert -size 320x240 xc:blue fixtures/smoke/images/smoke_bg.png
   convert -size 320x240 xc:red fixtures/smoke/images/smoke_subject.png
   ```
2. Validate the manifest:
   ```bash
   depthkit validate fixtures/smoke/manifest.json
   ```
   Expected: exit code 0, stdout contains "valid".
3. Render the manifest:
   ```bash
   depthkit render fixtures/smoke/manifest.json -o fixtures/smoke/output.mp4 --gpu software
   ```
   Expected: exit code 0, stdout contains "Rendered".
4. Validate output with `ffprobe`:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/smoke/output.mp4
   ```
5. Assert on `ffprobe` JSON output:
   - `streams[0].codec_type === "video"`
   - `streams[0].codec_name === "h264"`
   - `streams[0].width === 320`
   - `streams[0].height === 240`
   - `parseFloat(format.duration)` is within `[1.5, 2.5]` (2.0s +/- 0.5s)
   - No audio stream (no audio in manifest).

**Pass:** All assertions hold. Output MP4 exists and is >0 bytes.

**Fail:** Any assertion fails, CLI exits non-zero, or output is 0 bytes.

**Time budget:** <30 seconds total.

---

### Suite 1: SC-01 -- End-to-End Rendering

#### SC01-01: 60-Second 5-Scene Video Renders to Valid MP4

**Preconditions:**
- SMOKE-01 passed.
- Benchmark fixtures (F-01, F-01-AUDIO, F-01-IMAGES) are generated.

**Steps:**
1. Generate the 60s audio file:
   ```bash
   ffmpeg -f lavfi -i "sine=frequency=440:duration=60" -ar 44100 -ac 1 fixtures/benchmark/audio/test-60s.wav
   ```
2. Generate all scene images (distinct colors per scene -- see F-01-IMAGES).
3. Validate the benchmark manifest:
   ```bash
   depthkit validate fixtures/benchmark/manifest.json
   ```
   Expected: exit code 0.
4. Render:
   ```bash
   depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/output.mp4 \
     --gpu software \
     --verbose
   ```
   Expected: exit code 0. Record the render summary output for SC-03 reference.
5. Validate output with `ffprobe`:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/benchmark/output.mp4
   ```
6. Assert on `ffprobe` JSON -- video stream:
   - `streams` contains an entry with `codec_type === "video"`
   - Video stream: `codec_name === "h264"`
   - Video stream: `width === 1920`
   - Video stream: `height === 1080`
   - Video stream: parse `r_frame_rate` as fraction; numerator/denominator must evaluate to ~30.0 (+/- 0.1). Accept `"30/1"` or `"30000/1001"`.
7. Assert on `ffprobe` JSON -- duration:
   - `|parseFloat(format.duration) - 60.0| < 0.5`
8. Assert on `ffprobe` JSON -- audio stream:
   - `streams` contains an entry with `codec_type === "audio"`
9. Assert on `ffprobe` JSON -- faststart:
   - Run: `ffprobe -v trace fixtures/benchmark/output.mp4 2>&1 | head -50`
   - Verify `moov` atom appears before `mdat` atom in the trace output (this indicates `movflags +faststart`).
10. Count frames:
    ```bash
    ffprobe -v quiet -count_frames -select_streams v:0 \
      -show_entries stream=nb_read_frames \
      -print_format csv=p=0 fixtures/benchmark/output.mp4
    ```
    Expected: value is within `[1790, 1810]` (1800 +/- 10 frames, accounting for rounding).

**Pass:** All assertions in steps 6-10 hold. CLI exited with code 0.

**Fail:** Any assertion fails or CLI exited non-zero.

**Constraint refs:** C-02, C-04, C-07, C-11.
**TC refs:** TC-04, TC-10, TC-13.

#### SC01-02: Manual Playback Verification

**Preconditions:** SC01-01 passed. Output MP4 exists.

**Steps:**
1. Open `fixtures/benchmark/output.mp4` in VLC (or any media player).
2. Verify:
   - Video plays from beginning to end without errors or corruption.
   - 5 distinct scenes are visible (identifiable by color palette).
   - Scene transitions are visible: at least one smooth crossfade blend, at least one fade-through-black, at least one instant cut.
   - Camera motion is visible in at least 3 scenes (not all static).
   - Audio tone plays throughout.
3. Open the same file in a web browser (drag into Chrome/Firefox tab or use `<video>` element).
4. Verify playback starts without download prompt (faststart working).

**Pass:** Human operator confirms all items in step 2 and step 4.

**Fail:** Any visual artifact, corrupt frame, missing scene, or playback failure.

**Note:** This is a human verification step. Record pass/fail and any observations in the test report.

#### SC01-03: Deterministic Output (C-05, TC-06)

**Preconditions:** SC01-01 passed.

**Steps:**
1. Render the benchmark manifest a second time to a different output path:
   ```bash
   depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/output_run2.mp4 \
     --gpu software
   ```
2. Extract frame MD5 checksums from both renders:
   ```bash
   ffmpeg -i fixtures/benchmark/output.mp4 -f framemd5 - > fixtures/benchmark/run1.md5
   ffmpeg -i fixtures/benchmark/output_run2.mp4 -f framemd5 - > fixtures/benchmark/run2.md5
   ```
3. Compare:
   ```bash
   diff fixtures/benchmark/run1.md5 fixtures/benchmark/run2.md5
   ```
4. If `diff` reports no differences: **pass** (byte-identical frames).
5. If `diff` reports differences: compute PSNR:
   ```bash
   ffmpeg -i fixtures/benchmark/output.mp4 \
     -i fixtures/benchmark/output_run2.mp4 \
     -lavfi psnr=stats_file=fixtures/benchmark/psnr.log \
     -f null -
   ```
6. Inspect `psnr.log`. If all frames have `psnr_avg >= 60.0`: **pass** (visually indistinguishable).
7. If any frame has `psnr_avg < 60.0`: **fail** (non-deterministic rendering).

**Pass:** Step 4 (identical) or step 6 (PSNR >= 60dB on all frames).

**Fail:** Step 7.

**Constraint refs:** C-03, C-05.
**TC refs:** TC-06.

#### SC01-04: Audio Duration Drives Video Length (TC-13)

**Preconditions:** SMOKE-01 passed.

**Steps:**
1. Generate a 45-second audio file:
   ```bash
   ffmpeg -f lavfi -i "sine=frequency=440:duration=45" -ar 44100 -ac 1 fixtures/sc01-04/audio.wav
   ```
2. Create a manifest with 5 scenes at 320x240, 10fps, with explicit durations summing to exactly 45.0s (9.0s each), and `composition.audio.src` pointing to the 45s audio file.
3. Generate matching 320x240 solid-color test images.
4. Render:
   ```bash
   depthkit render fixtures/sc01-04/manifest.json \
     -o fixtures/sc01-04/output.mp4 --gpu software
   ```
5. Verify output duration:
   ```bash
   ffprobe -v quiet -print_format json -show_format fixtures/sc01-04/output.mp4
   ```
6. Assert `|parseFloat(format.duration) - 45.0| < 0.5`.
7. Assert audio stream is present in the output.

**Pass:** Output duration matches audio duration within tolerance. Audio stream present.

**Fail:** Duration mismatch >0.5s, missing audio stream, or render error.

**TC refs:** TC-13.
**Constraint refs:** C-07.

---

### Suite 2: SC-03 -- Performance Target

#### SC03-01: Benchmark Environment Verification

**Preconditions:** None.

**Steps:**
1. Document machine specs:
   ```bash
   echo "=== CPU ===" && nproc && cat /proc/cpuinfo | grep "model name" | head -1
   echo "=== RAM ===" && free -m | grep Mem
   echo "=== OS ===" && uname -a
   echo "=== FFmpeg ===" && ffmpeg -version | head -1
   echo "=== Node ===" && node --version
   ```
   On macOS, substitute: `sysctl -n hw.ncpu` for `nproc`, `sysctl hw.memsize` for `free -m`.
2. Assert:
   - CPU cores >= 4 (`nproc` >= 4).
   - Available RAM >= 4096 MB.
3. Record all values in the test report.

**Pass:** Machine meets minimum spec (4 cores, 4GB+ RAM).

**Fail:** Machine below spec -- benchmark results are informational only, not pass/fail. Document the shortfall.

#### SC03-02: Software WebGL Baseline Benchmark

**Preconditions:** SC03-01 passed. SC01-01 fixtures generated.

**Steps:**
1. Ensure no other CPU-intensive processes are running: `top -b -n1 | head -20` (document load average).
2. Run benchmark -- iteration 1:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_run1.mp4 \
     --gpu software --verbose
   ```
   Record: total wall-clock time (from `time` output), render duration from CLI verbose output, average frame time.
3. Run benchmark -- iteration 2:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_run2.mp4 \
     --gpu software --verbose
   ```
4. Run benchmark -- iteration 3:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_run3.mp4 \
     --gpu software --verbose
   ```
5. Compute median of the 3 total wall-clock times.
6. Assert: median < 900,000ms (15 minutes).
7. Record all three times plus median in the test report. Also record average frame time from verbose output.

**Pass:** Median of 3 runs < 15 minutes.

**Fail:** Median >= 15 minutes. Document all values -- this informs whether the target needs revision or the pipeline needs optimization.

**Constraint refs:** C-08, C-11.
**TC refs:** TC-02, TC-11.

#### SC03-03: GPU-Accelerated Benchmark (Optional)

**Preconditions:** SC03-02 completed. GPU available on test machine.

**Steps:**
1. Run:
   ```bash
   time depthkit render fixtures/benchmark/manifest.json \
     -o fixtures/benchmark/bench_gpu.mp4 \
     --gpu hardware --verbose
   ```
2. Record wall-clock time and average frame time.
3. Compare to SC03-02 median. Document the speedup ratio.

**Pass/Fail:** Informational only. No hard target for GPU. Document results.

**Note:** Per C-08, GPU acceleration should render in under 3 minutes, but this is aspirational, not a gate.

---

### Suite 3: SC-05 -- n8n Integration

**Execution gate:** OBJ-057 (full pipeline integration) and OBJ-075 (n8n HTTP interface) must both have `status: "verified"` in the progress map. If either is not verified, this entire suite is **blocked** -- skip and report as "blocked on OBJ-057/OBJ-075."

#### SC05-01: POST Topic and Receive Job ID

**Preconditions:** n8n workflow is running. HTTP endpoint URL is known (e.g., `http://localhost:5678/webhook/depthkit`).

**Steps:**
1. POST the test payload:
   ```bash
   curl -s -w "\n%{http_code}" -X POST \
     -H "Content-Type: application/json" \
     -d '{"topic":"Deep sea creatures","duration":30,"style":"cinematic documentary"}' \
     http://localhost:5678/webhook/depthkit
   ```
2. Assert HTTP status code is `200` or `202` (accepted).
3. Parse response body. Assert it contains a `job_id` field (string, non-empty).
4. Record `job_id` for subsequent steps.

**Pass:** Status 200/202, `job_id` present.

**Fail:** Non-2xx status, missing `job_id`, or connection refused.

#### SC05-02: Poll for Completion

**Preconditions:** SC05-01 passed. `job_id` obtained.

**Steps:**
1. Poll every 10 seconds for up to 20 minutes (120 polls max):
   ```bash
   JOB_ID="<from SC05-01>"
   for i in $(seq 1 120); do
     RESPONSE=$(curl -s http://localhost:5678/webhook/depthkit/status/$JOB_ID)
     STATUS=$(echo $RESPONSE | jq -r '.status')
     echo "Poll $i: status=$STATUS"
     if [ "$STATUS" = "completed" ]; then
       echo "Job completed."
       break
     elif [ "$STATUS" = "failed" ]; then
       echo "Job failed."
       exit 1
     fi
     sleep 10
   done
   ```
2. Assert: loop exited with `status === "completed"` within 120 polls.
3. Parse response: assert it contains a `download_url` field.

**Pass:** Status reached `"completed"` within 20 minutes. `download_url` present.

**Fail:** Timeout (120 polls without completion), `"failed"` status, or missing `download_url`.

#### SC05-03: Download and Validate MP4

**Preconditions:** SC05-02 passed. `download_url` obtained.

**Steps:**
1. Download:
   ```bash
   curl -s -o fixtures/sc05/output.mp4 "$DOWNLOAD_URL"
   ```
2. Assert file exists and is >0 bytes.
3. Validate with `ffprobe`:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/sc05/output.mp4
   ```
4. Assert:
   - Video stream: `codec_name === "h264"`, resolution is valid (any supported resolution).
   - `parseFloat(format.duration)` is within `[25.0, 35.0]` (~30s +/- 5s tolerance for pipeline variability).
   - Audio stream is present.

**Pass:** All assertions hold.

**Fail:** Any assertion fails.

**Constraint refs:** SC-05.

---

### Suite 4: SC-06 -- Manifest Validation Soundness

SC-06 is a biconditional: "No manifest that passes validation produces a rendering error. No manifest that fails validation is a valid video description."

#### SC06-FORWARD: Valid Manifests Render Without Error

**Preconditions:** SMOKE-01 passed. Valid corpus (F-03) manifests and matching images generated.

**Procedure (repeated for each manifest V-01 through V-20):**

1. Validate:
   ```bash
   depthkit validate fixtures/valid/V-XX.json
   ```
   - Expected: exit code 0.
   - For V-08: exit code 0 WITH warning containing `AUDIO_DURATION_MISMATCH` in stdout.
   - For V-17: exit code 0 WITH warning containing `SCENE_ORDER_MISMATCH` in stdout.
   - Record any warnings.

2. Render:
   ```bash
   depthkit render fixtures/valid/V-XX.json \
     -o fixtures/valid/output/V-XX.mp4 \
     --gpu software
   ```
   - Expected: exit code 0.

3. Validate output:
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams fixtures/valid/output/V-XX.mp4
   ```
   Assert:
   - Video stream: `codec_name === "h264"`.
   - Resolution matches manifest's `composition.width` and `composition.height`.
   - FPS: parse `r_frame_rate` as fraction; evaluate to manifest's `composition.fps` (+/- 0.1).
   - Duration: `|parseFloat(format.duration) - expectedDuration| < 0.5` where `expectedDuration` = sum of scene durations minus transition overlaps (computed from the manifest).
   - If manifest has audio: audio stream present.

**Pass for the suite:** All 20 valid manifests render without error and pass `ffprobe` validation.

**Fail:** Any valid manifest fails validation, fails rendering, or produces an invalid MP4. Document the manifest ID, the error, and the component that failed. File as a bug.

**Constraint refs:** C-04, C-10.
**TC refs:** TC-07.

#### SC06-BACKWARD-A: Invalid Manifests Fail Validation

**Preconditions:** Invalid corpus F-04a (E-01 through E-22) created.

**Procedure (repeated for each manifest E-01 through E-22):**

1. Run validation:
   ```bash
   depthkit validate fixtures/invalid/E-XX.json
   ```
2. Assert:
   - Exit code is 1.
   - Stderr contains an error message.
   - Error message contains the expected error code or recognizable description matching the F-04a table.
3. Verify no rendering occurred:
   - Time the command: `time depthkit validate ...`. Assert completes in < 1 second (validation is synchronous, no browser or FFmpeg).
   - Verify no output file was created in the working directory.

**Pass for the suite:** All 22 invalid manifests fail validation with appropriate error messages.

**Fail:** Any invalid manifest passes validation (exit code 0), or error message does not identify the problem. Document the manifest ID and which validation rule is missing. File as a bug against OBJ-016/OBJ-004.

#### SC06-BACKWARD-B: Pre-Flight Failures Prevent Rendering

**Preconditions:** Pre-flight failure corpus F-04b (P-01 through P-03) created.

**Procedure (repeated for each manifest P-01 through P-03):**

1. Verify the manifest passes validation:
   ```bash
   depthkit validate fixtures/preflight/P-XX.json
   ```
   Expected: exit code 0 (manifest structure is valid).

2. Attempt to render:
   ```bash
   depthkit render fixtures/preflight/P-XX.json \
     -o fixtures/preflight/output/P-XX.mp4 \
     --gpu software 2>fixtures/preflight/P-XX.stderr
   ```
3. Assert:
   - Exit code is 1.
   - Stderr (captured in `P-XX.stderr`) contains the expected error code (`SCENE_SETUP_FAILED` for P-01/P-02; `AUDIO_MUX_FAILED` or `SCENE_SETUP_FAILED` for P-03).
   - For P-02: error message lists **all** missing file paths, not just the first.
   - No output MP4 file exists at the output path.
4. Verify no extended browser session:
   - Time the render command. Assert it completes in < 5 seconds (pre-flight check happens before browser launch per OBJ-035 D15).

**Pass:** All pre-flight failure manifests fail before rendering with appropriate errors. No partial output.

**Fail:** Render proceeds despite missing files, or error message is incomplete.

**Constraint refs:** C-10.
**TC refs:** TC-07.

---

## Design Decisions

### D1: Test Plan Document, Not Test Code

**Decision:** OBJ-077's `output.md` IS the test plan -- concrete procedures with literal commands.

**Rationale:** Objective metadata: "documents test procedures only -- OBJ-078 executes them." OBJ-078 can follow these procedures directly or convert them into automated test scripts.

### D2: Merged Benchmark Fixture (F-01)

**Decision:** A single fixture serves both SC-01 (correctness) and SC-03 (performance).

**Rationale:** The SC-01 benchmark manifest already specifies 1920x1080, 30fps, 5 scenes with 5 planes in tunnel/canyon scenes. This matches C-08's performance target conditions exactly. Separate fixtures would be redundant.

### D3: SC-05 Gated on Dependencies

**Decision:** Suite 3 (SC-05) is fully documented but execution is gated on OBJ-057 and OBJ-075 being verified.

**Rationale:** OBJ-077's own dependencies don't include the n8n stack. The plan is written now; OBJ-078 skips the suite if dependencies aren't met.

### D4: Verified-Only Fixtures

**Decision:** All fixtures use only geometries (OBJ-018 stage, OBJ-019 tunnel, OBJ-020 canyon, OBJ-021 flyover) and cameras (OBJ-026 static, OBJ-027 slow_push_forward, OBJ-028 slow_pull_back, OBJ-029 lateral_track_left, OBJ-030 crane_up, OBJ-031 gentle_float) with `status: "verified"` in the progress map.

**Rationale:** Isolates pipeline defects from preset bugs. If a test fails, the cause is in the rendering pipeline, not in an unverified geometry or camera preset.

### D5: Split Invalid Corpus (F-04a / F-04b)

**Decision:** Schema/semantic validation failures (F-04a) are tested via `depthkit validate`. Pre-flight failures (F-04b) are tested via `depthkit render`. Different tools, different expected behaviors.

**Rationale:** Validation failures never launch a browser (OBJ-035 D7). Pre-flight failures pass validation but fail before rendering. Conflating them produces wrong pass criteria.

### D6: Frame MD5 for Determinism, PSNR as Fallback

**Decision:** SC01-03 compares frame MD5 checksums. If different, PSNR >= 60dB on all frames is the fallback acceptance threshold.

**Rationale:** C-05 says "byte-identical (or visually indistinguishable)." Frame MD5 tests the former; PSNR tests the latter. 60dB PSNR means the maximum pixel difference is imperceptible to human vision.

### D7: Three Benchmark Runs With Median

**Decision:** SC03-02 runs the benchmark 3 times, reports the median.

**Rationale:** Single runs are affected by system load, cache state, thermal throttling. Median of 3 is standard benchmarking practice and smooths outliers.

### D8: `ffprobe` JSON as Canonical Validation

**Decision:** All output validation uses `ffprobe -v quiet -print_format json -show_format -show_streams`. This is the canonical invocation for all procedures.

**Rationale:** JSON output is machine-parseable and field paths are unambiguous. OBJ-078 can implement automated assertions against JSON fields.

### D9: Small Fixtures for SC-06 Corpus

**Decision:** SC-06 valid corpus manifests use 320x240 at 10fps with 1-3s durations.

**Rationale:** The valid corpus has 20 manifests, each of which must actually render. At 1920x1080/30fps, that would take hours. Small resolutions and short durations keep the total suite time under 20 minutes while still exercising the full pipeline.

### D10: Audio Synchronization Tested via Observable Behavior

**Decision:** SC01-04 tests audio synchronization by verifying the output video duration matches the audio duration, using explicit manifest durations that sum to the audio length.

**Rationale:** OBJ-035's current spec computes duration from scene `start_time + duration`. OBJ-038 provides `resolveTimeline()` with audio-proportional mode, but whether OBJ-035 integrates it as an explicit mode flag is an implementation detail. The test validates the observable behavior (C-07: audio synchronization) -- the output video has audio and its duration matches the audio file duration.

## Acceptance Criteria

### Test Plan Completeness

- [ ] **AC-01:** The plan contains five suites: Suite 0 (Smoke), Suite 1 (SC-01), Suite 2 (SC-03), Suite 3 (SC-05), Suite 4 (SC-06).
- [ ] **AC-02:** Each procedure has: unique ID, preconditions, literal CLI commands, exact assertion conditions, pass/fail thresholds.
- [ ] **AC-03:** SC-01 addresses: 60s 5-scene rendering, 3+ geometry types, 3+ camera presets, crossfade/dip_to_black/cut transitions, audio sync, manual playback check, VLC + browser playback, determinism, and audio-driven duration.
- [ ] **AC-04:** SC-03 specifies environment requirements, 3-run median, and the 15-minute threshold on software WebGL.
- [ ] **AC-05:** SC-05 documents POST/poll/download with HTTP status codes, 20-minute timeout, 10-second poll interval, and ffprobe validation of the downloaded MP4.
- [ ] **AC-06:** SC-06 tests both directions: 20 valid manifests render successfully (forward); 22 invalid manifests fail validation (backward-A); 3 pre-flight failures fail before rendering (backward-B).
- [ ] **AC-07:** SC01-03 provides a determinism procedure with frame MD5 comparison and PSNR >= 60dB fallback.
- [ ] **AC-08:** All fixtures reference only verified geometries and camera presets per the current progress map.
- [ ] **AC-09:** The plan specifies how to generate test images and audio files (literal commands for both ImageMagick and ffmpeg alternatives).
- [ ] **AC-10:** `ffprobe` validation uses a single canonical invocation (`-v quiet -print_format json -show_format -show_streams`) with explicit JSON field assertions per procedure.
- [ ] **AC-11:** Each procedure references relevant TC and C identifiers.
- [ ] **AC-12:** V-08 and V-17 procedures assert specific expected warning codes (`AUDIO_DURATION_MISMATCH` and `SCENE_ORDER_MISMATCH` respectively).

## Edge Cases and Error Handling

### Environment Issues

| Scenario | Plan Response |
|---|---|
| Machine has <4GB RAM | SC03-01 detects and reports. Benchmark results are informational, not pass/fail. |
| No FFmpeg installed | SMOKE-01 precondition fails. All suites blocked. |
| No Chromium available | SMOKE-01 precondition fails. All suites blocked. |
| GPU not available for SC03-03 | SC03-03 is optional. Skip and note. |
| ImageMagick not installed | Use ffmpeg alternative for image generation (documented in F-01-IMAGES). |

### Timing Variability

| Scenario | Plan Response |
|---|---|
| SC-03 benchmark marginally exceeds 15 min | Median of 3 runs is the value. If median < 15 min, pass. |
| Duration tolerance (ffprobe vs expected) | +/- 0.5s for all videos. |
| Frame count rounding | +/- 10 frames tolerance for the 60s benchmark (1800 +/- 10). |

### Partial Infrastructure

| Scenario | Plan Response |
|---|---|
| OBJ-057 or OBJ-075 not complete | Suite 3 (SC-05) is blocked. Report as "blocked." |
| New geometries verified after plan written | OBJ-078 may add them to the valid corpus but is not required to. |

### Test Failures

| Scenario | Plan Response |
|---|---|
| Valid manifest fails to render | SC-06 forward direction failure. Document error, manifest ID, and component that failed. File as bug. |
| Invalid manifest passes validation | SC-06 backward direction failure. Document manifest ID and which validation rule is missing. File as bug against OBJ-016/OBJ-004. |
| Determinism check fails | SC01-03 failure. Document the differing frames and PSNR values. Investigate source of non-determinism (likely FFmpeg encoder or Three.js rounding). |
| Pre-flight check doesn't catch missing audio | P-03 documents that either `AUDIO_MUX_FAILED` or `SCENE_SETUP_FAILED` is acceptable. Document observed behavior. |

## Traceability Matrix

| TC/Constraint | Procedures |
|---|---|
| TC-02 (Render performance) | SC03-02 |
| TC-04 (Geometries eliminate manual positioning) | SC01-01 (no manual coords in fixture) |
| TC-06 (Deterministic output) | SC01-03 |
| TC-07 (Validation catches errors) | SC06-BACKWARD-A, SC06-BACKWARD-B |
| TC-10 (Transitions mask seams) | SC01-01, SC01-02 (visual check) |
| TC-11 (Docker/software WebGL) | SC03-02 (software WebGL) |
| TC-13 (Audio drives video length) | SC01-04 |
| C-02 (Puppeteer+Three.js+FFmpeg) | SC01-01 |
| C-03 (Deterministic timing) | SC01-03 |
| C-04 (Resolution/frame rate) | SC06-FORWARD (V-09 portrait, V-10 24fps, V-11 30fps) |
| C-05 (Deterministic output) | SC01-03 |
| C-07 (Audio sync) | SC01-01, SC01-04 |
| C-08 (Render performance) | SC03-02 |
| C-10 (Manifest validation) | SC06-BACKWARD-A, SC06-BACKWARD-B |
| C-11 (Software rendering) | SC03-02 |

## Integration Points

### Depends On

| Dependency | What This Plan Uses |
|---|---|
| **OBJ-035** (Orchestrator) | SC-01 and SC-03 procedures render via the orchestrator (through CLI). SC-06 pre-flight tests rely on OBJ-035's error codes (`SCENE_SETUP_FAILED`, `AUDIO_MUX_FAILED`). |
| **OBJ-046** (CLI) | All procedures use `depthkit render` and `depthkit validate` commands. CLI output format (from `src/cli/format.ts`) is referenced for assertion patterns ("Rendered", "valid"). |
| **OBJ-037** (Scene Sequencer) | Transition tests (crossfade, dip_to_black in F-01 manifest) rely on OBJ-037's integration into OBJ-035. Not referenced directly. |
| **OBJ-038** (Scene Timing) | Audio sync tests (SC01-04) rely on OBJ-038's timing resolution through OBJ-035. Not referenced directly. |

### Consumed By

| Consumer | How |
|---|---|
| **OBJ-078** (E2E Test Execution) | Primary consumer. Creates fixtures, executes procedures, reports results. |

### File Placement

```
nodes/
  OBJ-077/
    meta.json    # UPDATED -- status, notes
    output.md    # NEW -- this specification / test plan
```

## Open Questions

### OQ-A: SC-05 Endpoint URL and Response Schema

The SC-05 procedures assume an endpoint at `http://localhost:5678/webhook/depthkit` with response fields `job_id`, `status`, and `download_url`. These are placeholders. OBJ-075's specification will define the actual endpoint contract. OBJ-078 must consult OBJ-075's spec and adjust the SC-05 procedures (URL, field names, status values) accordingly.

### OQ-B: E-12 Incompatible Camera Selection

E-12 requires a camera preset that is incompatible with the chosen geometry. The specific combination depends on which camera presets declare which `compatible_geometries`. OBJ-078 must consult the camera registry (OBJ-026 through OBJ-031) to find a valid incompatible pairing. If no verified camera is incompatible with any verified geometry (all cameras are compatible with all geometries), E-12 should be documented as untestable with verified presets and deferred.

### OQ-C: Additional Valid Corpus Manifests

The F-03 corpus specifies 20 manifests as a minimum. If OBJ-078 discovers additional edge cases during execution (e.g., specific slot combinations, boundary durations), additional manifests may be added to the corpus. The plan does not constrain the corpus to exactly 20.
