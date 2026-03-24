# Consolidated Spatial Specification — depthkit

> **Generated:** 2026-03-23 | **Category:** spatial | **Mode:** CHUNK
> **Source Nodes:** OBJ-003, OBJ-005, OBJ-006, OBJ-007, OBJ-008, OBJ-018, OBJ-019, OBJ-020, OBJ-021, OBJ-022, OBJ-025, OBJ-026, OBJ-027, OBJ-028, OBJ-029, OBJ-030, OBJ-031, OBJ-040, OBJ-041
> **Description-Only Nodes (unspecified):** OBJ-023, OBJ-024, OBJ-032, OBJ-033, OBJ-034, OBJ-042, OBJ-043, OBJ-044, OBJ-045, OBJ-079, OBJ-080, OBJ-081

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Dependency Order](#2-dependency-order)
3. [Tier 0 — Spatial Math Foundation (OBJ-003)](#3-tier-0--spatial-math-foundation-obj-003)
4. [Tier 1 — Type Contracts](#4-tier-1--type-contracts)
   - 4.1 [Geometry Type Contract (OBJ-005)](#41-geometry-type-contract-obj-005)
   - 4.2 [Camera Path Type Contract (OBJ-006)](#42-camera-path-type-contract-obj-006)
   - 4.3 [Depth Model / Slot Taxonomy (OBJ-007)](#43-depth-model--slot-taxonomy-obj-007)
   - 4.4 [Transition Type Contract (OBJ-008)](#44-transition-type-contract-obj-008)
5. [Tier 2 — Geometry Implementations](#5-tier-2--geometry-implementations)
   - 5.1 [Stage (OBJ-018)](#51-stage-obj-018)
   - 5.2 [Tunnel (OBJ-019)](#52-tunnel-obj-019)
   - 5.3 [Canyon (OBJ-020)](#53-canyon-obj-020)
   - 5.4 [Flyover (OBJ-021)](#54-flyover-obj-021)
   - 5.5 [Diorama (OBJ-022)](#55-diorama-obj-022)
   - 5.6 [Close-Up (OBJ-025)](#56-close-up-obj-025)
   - 5.7 [Portal (OBJ-023) — UNSPECIFIED](#57-portal-obj-023--unspecified)
   - 5.8 [Panorama (OBJ-024) — UNSPECIFIED](#58-panorama-obj-024--unspecified)
6. [Tier 2 — Camera Path Implementations](#6-tier-2--camera-path-implementations)
   - 6.1 [Static (OBJ-026)](#61-static-obj-026)
   - 6.2 [Push/Pull (OBJ-027)](#62-pushpull-obj-027)
   - 6.3 [Lateral Track (OBJ-028)](#63-lateral-track-obj-028)
   - 6.4 [Tunnel Push (OBJ-029)](#64-tunnel-push-obj-029)
   - 6.5 [Flyover Glide (OBJ-030)](#65-flyover-glide-obj-030)
   - 6.6 [Gentle Float (OBJ-031)](#66-gentle-float-obj-031)
   - 6.7 [Dramatic Push (OBJ-032) — UNSPECIFIED](#67-dramatic-push-obj-032--unspecified)
   - 6.8 [Crane Up (OBJ-033) — UNSPECIFIED](#68-crane-up-obj-033--unspecified)
   - 6.9 [Dolly Zoom (OBJ-034) — UNSPECIFIED](#69-dolly-zoom-obj-034--unspecified)
7. [Tier 3 — Validation & Sizing](#7-tier-3--validation--sizing)
   - 7.1 [Plane Sizing & Edge-Reveal (OBJ-040)](#71-plane-sizing--edge-reveal-obj-040)
   - 7.2 [Spatial Compatibility Validation (OBJ-041)](#72-spatial-compatibility-validation-obj-041)
8. [Deferred Spatial Nodes](#8-deferred-spatial-nodes)
9. [Geometry-Camera Compatibility Matrix](#9-geometry-camera-compatibility-matrix)
10. [Integration Boundary Map](#10-integration-boundary-map)
11. [Inconsistencies & Open Conflicts](#11-inconsistencies--open-conflicts)
12. [Consolidated File Manifest](#12-consolidated-file-manifest)
13. [Consolidated Acceptance Criteria Index](#13-consolidated-acceptance-criteria-index)

---

## 1. Architecture Overview

The spatial category encompasses all 3D positioning, camera motion, transition timing, and spatial validation in depthkit. It is the geometric heart of the 2.5D engine — defining how flat images become a perspective scene.

### Core Principles

- **Pure math, no rendering:** All spatial modules are isomorphic (Node.js + browser), use plain `readonly [number, number, number]` tuples (not Three.js types), and have zero rendering dependencies.
- **Named abstractions:** LLM authors interact with geometry names and slot names, never raw coordinates. The spatial system resolves names to 3D transforms.
- **Validate before render:** All spatial relationships are validated at manifest parse time. Camera-geometry compatibility, plane oversizing, and edge-reveal risk are checked before Puppeteer launches.
- **Deterministic:** All spatial functions are pure. Same inputs produce identical outputs (C-05).

### Spatial Pipeline

```
Manifest
    |
    v
[Geometry lookup]  -- OBJ-005 registry
    |
    v
[Camera path lookup] -- OBJ-006 registry
    |
    v
[Slot validation]  -- OBJ-007 validatePlaneSlots
    |
    v
[Compatibility check] -- OBJ-041 validateSceneSpatialCompatibility
    |
    v
[Edge-reveal check]   -- OBJ-040 validateGeometryEdgeReveal
    |
    v
[Slot transform resolution] -- OBJ-007 resolveSlotTransform
    |
    v
[Per-frame: evaluate(t)] -- OBJ-006 CameraPathEvaluator
    |
    v
[Per-frame: transition opacity] -- OBJ-008 computeTransitionOpacity
    |
    v
Three.js renderer (engine category)
```

---

## 2. Dependency Order

```
Tier 0:  OBJ-003  Spatial Math Foundation (zero dependencies)

Tier 1:  OBJ-005  Geometry Type Contract      (depends: OBJ-003)
         OBJ-006  Camera Path Type Contract    (depends: OBJ-003, OBJ-002*)
         OBJ-007  Depth Model / Slot Taxonomy  (depends: OBJ-003)
         OBJ-008  Transition Type Contract     (depends: OBJ-002*)

Tier 2:  OBJ-018  Stage geometry       (depends: OBJ-005, OBJ-007)
         OBJ-019  Tunnel geometry      (depends: OBJ-005, OBJ-007)
         OBJ-020  Canyon geometry      (depends: OBJ-005, OBJ-007)
         OBJ-021  Flyover geometry     (depends: OBJ-005, OBJ-007)
         OBJ-022  Diorama geometry     (depends: OBJ-005, OBJ-007)
         OBJ-025  Close-up geometry    (depends: OBJ-005, OBJ-007)
         OBJ-023  Portal geometry      (depends: OBJ-005, OBJ-007) [UNSPECIFIED]
         OBJ-024  Panorama geometry    (depends: OBJ-005, OBJ-007) [UNSPECIFIED]
         OBJ-026  Static camera        (depends: OBJ-006)
         OBJ-027  Push/Pull cameras    (depends: OBJ-006)
         OBJ-028  Lateral Track cams   (depends: OBJ-006)
         OBJ-029  Tunnel Push camera   (depends: OBJ-006)
         OBJ-030  Flyover Glide camera (depends: OBJ-006)
         OBJ-031  Gentle Float camera  (depends: OBJ-006)
         OBJ-032  Dramatic Push camera (depends: OBJ-006) [UNSPECIFIED]
         OBJ-033  Crane Up camera      (depends: OBJ-006) [UNSPECIFIED]
         OBJ-034  Dolly Zoom camera    (depends: OBJ-006) [UNSPECIFIED]

Tier 3:  OBJ-040  Plane Sizing / Edge-Reveal  (depends: OBJ-003, OBJ-005, OBJ-006)
         OBJ-041  Spatial Compatibility        (depends: OBJ-005, OBJ-006)

* OBJ-002 (interpolation/easing) is in the engine category but is a cross-category dependency.
```

---

## 3. Tier 0 — Spatial Math Foundation (OBJ-003)

**File:** `src/spatial/types.ts`, `src/spatial/constants.ts`, `src/spatial/math.ts`, `src/spatial/index.ts`

### Types

| Type | Definition | Purpose |
|------|-----------|---------|
| `Vec3` | `readonly [number, number, number]` | All 3D positions, directions |
| `EulerRotation` | `readonly [number, number, number]` | Rotation in radians [rx, ry, rz] |
| `Size2D` | `readonly [number, number]` | Plane dimensions [width, height] in world units |
| `FrustumRect` | `{ visibleHeight, visibleWidth, distance, fov, aspectRatio }` | Camera frustum at a distance |
| `PlaneTransform` | `{ position: Vec3, rotation: EulerRotation, size: Size2D }` | Complete plane spatial state |
| `PlaneSizingInput` | `{ distanceFromCamera, fov, aspectRatio, oversizeFactor? }` | Input for plane sizing |
| `PlaneSizingResult` | `{ size: Size2D, frustum: FrustumRect, oversizeFactor }` | Plane sizing result |
| `CameraState` | `{ position, lookAt, fov, aspectRatio, near, far }` | Complete camera state |

### Constants

| Constant | Key Values |
|----------|------------|
| `AXIS` | `RIGHT: [1,0,0]`, `UP: [0,1,0]`, `INTO_SCENE: [0,0,-1]`, etc. |
| `DEFAULT_CAMERA` | `fov: 50`, `near: 0.1`, `far: 100`, `position: [0,0,5]`, `lookAt: [0,0,0]` |
| `COMPOSITION_PRESETS` | `LANDSCAPE_1080P: 1920x1080`, `PORTRAIT_1080P: 1080x1920` |
| `FRAME_RATES` | `[24, 30]` |
| `PLANE_ROTATIONS` | `FACING_CAMERA: [0,0,0]`, `FLOOR: [-PI/2,0,0]`, `CEILING: [PI/2,0,0]`, `LEFT_WALL: [0,PI/2,0]`, `RIGHT_WALL: [0,-PI/2,0]` |

### Functions

| Function | Signature | Notes |
|----------|-----------|-------|
| `computeFrustumRect` | `(distance, fov, aspectRatio) => FrustumRect` | `visibleHeight = 2 * distance * tan(fov/2)` |
| `computePlaneSize` | `(PlaneSizingInput) => PlaneSizingResult` | Applies uniform oversizeFactor (>= 1.0) |
| `computeViewAxisDistance` | `(cameraPos, cameraLookAt, planePos) => number` | Signed, projected along forward vector |
| `computeAspectCorrectSize` | `(texW, texH, maxW, maxH) => Size2D` | "Contain" fit logic |
| `degToRad`, `radToDeg` | Conversion utilities | |
| `distance3D`, `normalize`, `dot`, `subtract`, `scale`, `add` | Vec3 math utilities | `normalize([0,0,0])` returns `[0,0,0]` |

### Design Decisions

- **D1:** Pure math, no Three.js dependency. Vec3 tuples convert at the rendering boundary.
- **D2:** `computeViewAxisDistance` returns signed projected distance (not Euclidean). Negative = behind camera.
- **D3:** Oversize factor is scalar (uniform both axes). V1 simplification documented.
- **D4:** `readonly` tuples, not classes. JSON-serializable for Puppeteer message passing.
- **D5:** FOV in degrees (matching Three.js PerspectiveCamera), rotations in radians (matching Three.js Euler).

### Acceptance Criteria

| ID | Criterion |
|----|-----------|
| AC-01 | `computeFrustumRect(30, 50, 16/9)` returns height ~27.98, width ~49.74 (tolerance +/-0.1) |
| AC-02 | `computeFrustumRect` throws RangeError for distance <= 0, fov not in (0,180), aspectRatio <= 0 |
| AC-03 | `computePlaneSize` with oversizeFactor 1.2 returns dimensions exactly 1.2x frustum |
| AC-04 | `computePlaneSize` throws RangeError for oversizeFactor < 1.0 |
| AC-05 | `computeViewAxisDistance` for camera [0,0,5] lookAt [0,0,0] plane [0,0,-25] returns 30 |
| AC-06 | Returns negative when plane behind camera (camera [0,0,5] lookAt [0,0,0] plane [0,0,10] -> -5) |
| AC-07 | `computeAspectCorrectSize(1920, 1080, 50, 30)` returns [50, 28.125] |
| AC-08 | `PLANE_ROTATIONS.FLOOR` equals `[-Math.PI/2, 0, 0]` exactly |
| AC-09 | All exported constants are readonly/as const |
| AC-10 | Zero runtime dependencies beyond standard Math |
| AC-11 | All exports via barrel `import { ... } from './spatial'` |
| AC-12 | Projected distance, not Euclidean: plane [10,0,-5] from camera [0,0,0] lookAt [0,0,-1] returns 5 |
| AC-13 | Non-axis-aligned projection test: ~7.60 (tolerance +/-0.01) |
| AC-14 | Returns 0 when cameraPosition equals cameraLookAt |

---

## 4. Tier 1 — Type Contracts

### 4.1 Geometry Type Contract (OBJ-005)

**Files:** `src/scenes/geometries/types.ts`, `registry.ts`, `validate.ts`, `slot-utils.ts`, `index.ts`

#### Core Types

**PlaneSlot** extends PlaneTransform (OBJ-003):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `position` | `Vec3` | yes | Inherited from PlaneTransform |
| `rotation` | `EulerRotation` | yes | Inherited from PlaneTransform |
| `size` | `Size2D` | yes | Inherited from PlaneTransform |
| `required` | `boolean` | yes | Must manifest provide this slot? |
| `description` | `string` | yes | Non-empty. For SKILL.md and errors |
| `renderOrder` | `number?` | no | Three.js draw-order hint |
| `transparent` | `boolean?` | no | Alpha channel expected? |
| `fogImmune` | `boolean?` | no | Excluded from fog calculations? |

**FogConfig:**

| Field | Type | Constraint |
|-------|------|-----------|
| `color` | `string` | `#RRGGBB` hex format |
| `near` | `number` | >= 0 |
| `far` | `number` | > near |

**SceneGeometry:**

| Field | Type | Constraint |
|-------|------|-----------|
| `name` | `string` | `/^[a-z][a-z0-9_]*$/` |
| `slots` | `Record<string, PlaneSlot>` | >= 1 entry, >= 1 required |
| `compatible_cameras` | `readonly string[]` | Non-empty, names match pattern |
| `default_camera` | `string` | Must be in compatible_cameras |
| `fog` | `FogConfig?` | Optional |
| `description` | `string` | Non-empty |
| `preferred_aspect` | `'landscape' \| 'portrait' \| 'both'?` | Advisory only |

#### Registry Pattern: Lock-on-First-Read

- **Registration phase:** `registerGeometry(geometry)` accepts new geometries.
- **Locked phase:** First call to `getGeometryRegistry()`, `getGeometry()`, or `getGeometryNames()` transitions to locked. All data deep-frozen via `Object.freeze` recursively.
- Post-lock registration throws: `"Cannot register geometry '{name}': registry is locked."`
- Duplicate names throw: `"Geometry '{name}' is already registered"`
- Invalid definitions throw with all validation errors semicolon-separated.

#### Slot Utilities

| Function | Purpose |
|----------|---------|
| `getRequiredSlotNames(geometry)` | Returns required slot names |
| `getOptionalSlotNames(geometry)` | Returns optional slot names |
| `getAllSlotNames(geometry)` | Returns all slot names |
| `isCameraCompatible(geometry, cameraName)` | Checks compatible_cameras list |

#### Validation (`validateGeometryDefinition`)

11 checks: name format, non-empty slots, slot key format, at least one required slot, non-empty compatible_cameras, camera name format, default_camera in list, fog constraints, non-empty descriptions, positive slot sizes. Returns `GeometryValidationError[]`.

#### Acceptance Criteria (OBJ-005)

| ID | Criterion |
|----|-----------|
| AC-01 | PlaneSlot extends PlaneTransform with required, description, optional renderOrder/transparent/fogImmune |
| AC-02 | SceneGeometry includes all specified fields |
| AC-03 | registerGeometry throws on duplicate name |
| AC-04 | registerGeometry throws on invalid definition with all errors |
| AC-05 | registerGeometry throws after registry locked |
| AC-06 | validateGeometryDefinition catches all 11 error conditions |
| AC-07 | getRequiredSlotNames returns correct subset |
| AC-08 | getAllSlotNames returns all keys |
| AC-09 | isCameraCompatible true only for listed cameras |
| AC-10 | getGeometry('nonexistent') returns undefined |
| AC-11 | Tunnel geometry example from seed passes validation |
| AC-12 | Zero runtime dependencies beyond OBJ-003 types |
| AC-13 | Barrel export works |
| AC-14 | Deep freeze: mutation of any nested property throws TypeError |
| AC-15 | Optional PlaneSlot fields can be omitted |
| AC-16 | preferred_aspect is optional |

---

### 4.2 Camera Path Type Contract (OBJ-006)

**Files:** `src/camera/types.ts`, `registry.ts`, `validate.ts`, `index.ts`

#### Core Types

**CameraFrameState** — path-controlled subset of camera state:
```
{ position: Vec3, lookAt: Vec3, fov: number }
```

**CameraParams** — manifest-level customization:

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `speed` | `number?` | 1.0 | Amplitude multiplier (not temporal rate). Must be > 0. |
| `easing` | `EasingName?` | preset's default | Overrides preset's default easing |
| `offset` | `Vec3?` | [0,0,0] | Applied OUTSIDE evaluate() by renderer. lookAt not shifted. |

**ResolvedCameraParams** — validated, ready for preset consumption:
```
{ speed: number, easing: EasingFn }
```
Note: offset is NOT included; it's applied post-evaluate by renderer.

**OversizeRequirements** — per-preset metadata for edge-reveal:

| Field | Type | Notes |
|-------|------|-------|
| `maxDisplacementX` | `number` | >= 0, world units at speed=1.0 |
| `maxDisplacementY` | `number` | >= 0 |
| `maxDisplacementZ` | `number` | >= 0 |
| `fovRange` | `readonly [number, number]` | [min, max] in degrees, both in (0,180) |
| `recommendedOversizeFactor` | `number` | >= 1.0, safe upper bound |

**CameraPathPreset:**

| Field | Type | Notes |
|-------|------|-------|
| `name` | `string` | Lowercase snake_case |
| `description` | `string` | For SKILL.md |
| `evaluate` | `CameraPathEvaluator` | `(t, params?) => CameraFrameState` |
| `defaultStartState` | `CameraFrameState` | Must match evaluate(0) within 1e-6 |
| `defaultEndState` | `CameraFrameState` | Must match evaluate(1) within 1e-6 |
| `defaultEasing` | `EasingName` | |
| `compatibleGeometries` | `readonly string[]` | Non-empty, explicit enumeration |
| `oversizeRequirements` | `OversizeRequirements` | |
| `tags` | `readonly string[]` | For SKILL.md search |

#### Registry Pattern: Parameter-Based

Unlike OBJ-005's singleton lock-on-first-read, OBJ-006's registry is passed as a parameter:
- `getCameraPath(registry, name)` — throws if not found
- `isCameraPathName(registry, name)` — type guard
- `listCameraPathNames(registry)` — alphabetically sorted
- `getCameraPathsForGeometry(registry, geometryName)` — filter by compatibility

#### Bridge Functions

| Function | Purpose |
|----------|---------|
| `toCameraState(frame, aspectRatio, near?, far?)` | Merge CameraFrameState + composition constants into full CameraState |
| `resolveCameraParams(params, defaultEasing)` | Validate and resolve raw CameraParams; throws on speed<=0 or invalid easing |

#### Validation (`validateCameraPathPreset`)

11 checks: evaluate(0)/evaluate(1) match static states, FOV in range at 100 sample points, no NaN/Infinity, oversize factor >= 1.0, fovRange valid, displacements >= 0, name format, non-empty compatibleGeometries, valid defaultEasing, sampled FOV within declared fovRange.

#### Design Decisions

- **D1:** Evaluation function over keyframe data. Each preset owns its interpolation logic.
- **D2:** Speed/easing inside evaluate(), offset outside (applied by renderer post-evaluate).
- **D3:** Speed scales spatial amplitude, not temporal rate. `speed=0.5` = half displacement, same easing curve.
- **D7:** Registry takes registry as parameter (testability). Different from OBJ-005's singleton.
- **D10:** CameraFrameState (path-controlled) vs CameraState (full). `toCameraState()` bridges them.

#### Acceptance Criteria (OBJ-006)

35 acceptance criteria covering: type exports (AC-01 through AC-08), toCameraState (AC-09/10), resolveCameraParams (AC-11 through AC-15), registry (AC-16 through AC-20), validation (AC-21 through AC-33), determinism (AC-34), isomorphism (AC-35/36).

---

### 4.3 Depth Model / Slot Taxonomy (OBJ-007)

**File:** `src/spatial/depth-model.ts`

#### Core Types

**SlotName:** `string` matching `/^[a-z][a-z0-9_]*$/`

**DepthSlot** — enriched slot definition (supersedes seed's PlaneSlot sketch):

| Field | Type | Notes |
|-------|------|-------|
| `name` | `SlotName` | Must match SLOT_NAME_PATTERN |
| `position` | `Vec3` | Default position |
| `rotation` | `EulerRotation` | Default rotation |
| `size` | `Size2D` | Default size |
| `required` | `boolean` | |
| `description` | `string` | For SKILL.md |
| `promptGuidance` | `string` | Image generation guidance |
| `expectsAlpha` | `boolean` | Informs asset pipeline |
| `renderOrder` | `number` | Draw-order hint |

**PlaneOverride** — manifest escape hatch (AP-08):

| Field | Type | Notes |
|-------|------|-------|
| `position?` | `Vec3` | |
| `rotation?` | `EulerRotation` | |
| `size?` | `Size2D` | Components must be > 0 |
| `opacity?` | `number` | [0.0, 1.0], static per scene |

**ResolvedSlot** — after merging geometry defaults with overrides:
```
{ position, rotation, size, opacity, renderOrder }
```

#### DEFAULT_SLOT_TAXONOMY

5 standard slots (seed Section 4.1):

| Slot | Position | Size | Required | expectsAlpha | renderOrder |
|------|----------|------|----------|-------------|------------|
| `sky` | `[0, 0, -50]` | `[120, 70]` | yes | no | 0 |
| `back_wall` | `[0, 0, -30]` | `[70, 40]` | no | no | 1 |
| `midground` | `[0, 0, -15]` | `[40, 25]` | no | no | 2 |
| `subject` | `[0, 0, -5]` | `[12, 12]` | yes | yes | 3 |
| `near_fg` | `[0, 0, -1]` | `[25, 16]` | no | yes | 4 |

All sizes assume DEFAULT_CAMERA at [0,0,5], FOV=50, 16:9. Oversize factor >= 1.0 validated by AC-23.

#### Functions

| Function | Purpose |
|----------|---------|
| `isValidSlotName(name)` | Validates against SLOT_NAME_PATTERN |
| `validatePlaneSlots(planes, slots, geometryName)` | Validates manifest plane keys vs geometry slots. Checks: required present, no unknown keys, format valid, override values safe. Stable error ordering. |
| `resolveSlotTransform(slot, override?)` | Merges defaults with partial override. renderOrder always from slot. |

#### Design Decisions

- **D1:** Two-tier model: default taxonomy is a convenience grab-bag; each geometry declares its own SlotSet.
- **D2:** DepthSlot supersedes seed's PlaneSlot. Adds name, promptGuidance, expectsAlpha, renderOrder.
- **D3:** PlaneOverride is partial merge (not replacement). Unspecified fields retain defaults.
- **D5:** renderOrder not in PlaneOverride (not overridable by manifest author).
- **D7:** Static opacity only in V1. No per-frame animation.
- **D10:** OBJ-007 owns slot types/rules; OBJ-005 owns geometry registry.

#### Acceptance Criteria (OBJ-007)

23 acceptance criteria covering: taxonomy structure (AC-01/02), slot name validation (AC-03/04), validatePlaneSlots behavior (AC-05 through AC-13), resolveSlotTransform (AC-14 through AC-17), metadata (AC-18 through AC-20), module requirements (AC-21/22), size validation (AC-23).

---

### 4.4 Transition Type Contract (OBJ-008)

**Files:** `src/transitions/types.ts`, `presets.ts`, `compute.ts`, `resolve.ts`, `index.ts`

#### Types

**TransitionTypeName:** `'cut' | 'crossfade' | 'dip_to_black'`

**TransitionSpec** (manifest form):
```
{ type: TransitionTypeName, duration: number, easing?: EasingName }
```

**ResolvedTransition** (frame-based):
```
{ type, durationFrames, easing, overlapStartFrame, overlapEndFrame }
```

**TransitionOpacityResult:**
```
{ outgoingOpacity: number, incomingOpacity: number }
```

#### Preset Definitions

| Name | defaultEasing | requiresOverlap | requiresDuration |
|------|--------------|-----------------|-----------------|
| `cut` | `linear` | false | false |
| `crossfade` | `linear` | true | true |
| `dip_to_black` | `ease_in_out` | false | true |

#### Computation Contract

**crossfade:** `t = (frame - start) / (end - start)`, `t' = easing(t)`, `outgoing = 1 - t'`, `incoming = t'`. Invariant: `outgoing + incoming = 1.0`.

**dip_to_black:** Two phases split at `midpoint = Math.floor(durationFrames / 2)`. Phase 1: outgoing fades 1->0, incoming=0. Phase 2: outgoing=0, incoming fades 0->1. Midpoint frame is fully black. Invariant: `min(outgoing, incoming) = 0`.

**cut:** Returns `{ outgoing: 0, incoming: 1 }` immediately. All validation bypassed.

#### Functions

| Function | Purpose |
|----------|---------|
| `computeTransitionOpacity(type, frame, start, end, easing)` | Per-frame opacity computation |
| `resolveTransition(spec, fps, sceneEndFrame, direction)` | Seconds->frames, overlap window positioning |
| `isTransitionTypeName(name)` | Type guard |
| `getTransitionPreset(name)` | Lookup with error on invalid |

#### Acceptance Criteria (OBJ-008)

33 acceptance criteria covering: preset registry (AC-01 through AC-05), cut behavior (AC-06/07), crossfade computation (AC-08 through AC-12), dip-to-black computation (AC-13 through AC-17), resolve function (AC-18 through AC-22), error handling (AC-23 through AC-29), degenerate cases (AC-30), module constraints (AC-31 through AC-33).

---

## 5. Tier 2 — Geometry Implementations

All geometries self-register via `registerGeometry()` at module load time. All construct `PlaneSlot` objects (OBJ-005) with all optional fields explicitly set. All assume DEFAULT_CAMERA at [0,0,5], FOV=50, 16:9.

### 5.1 Stage (OBJ-018)

**File:** `src/scenes/geometries/stage.ts`

The default, most fundamental geometry. Subject in front of background with a perspective-foreshortened floor.

| Field | Value |
|-------|-------|
| `name` | `'stage'` |
| `default_camera` | `'slow_push_forward'` |
| `compatible_cameras` | `static, slow_push_forward, slow_pull_back, lateral_track_left, lateral_track_right, gentle_float, dramatic_push, crane_up` |
| `fog` | `#000000, near: 20, far: 60` |
| `preferred_aspect` | `'both'` |

**Slots (6 total, 3 required):**

| Slot | Pos | Rot | Size | Req | Transp | FogImm | RO |
|------|-----|-----|------|-----|--------|--------|----|
| `sky` | [0,5,-50] | [0,0,0] | [120,70] | no | no | **yes** | -1 |
| `backdrop` | [0,0,-30] | [0,0,0] | [75,45] | **yes** | no | no | 0 |
| `floor` | [0,-3,-10] | [-PI/2,0,0] | [20,40] | **yes** | no | no | 1 |
| `midground` | [0,-1,-15] | [0,0,0] | [40,25] | no | no | no | 2 |
| `subject` | [0,-0.5,-5] | [0,0,0] | [12,12] | **yes** | yes | no | 3 |
| `near_fg` | [0,0,-1] | [0,0,0] | [25,16] | no | yes | no | 4 |

The floor plane (`FLOOR` rotation) is the defining spatial element — its perspective foreshortening as the camera pushes forward creates the primary 2.5D illusion.

---

### 5.2 Tunnel (OBJ-019)

**File:** `src/scenes/geometries/tunnel.ts`

Box-like corridor receding along -Z. Walls converge to vanishing point.

| Field | Value |
|-------|-------|
| `name` | `'tunnel'` |
| `default_camera` | `'tunnel_push_forward'` |
| `compatible_cameras` | `tunnel_push_forward, slow_push_forward, static, gentle_float` |
| `fog` | `#000000, near: 15, far: 50` |
| `preferred_aspect` | `'landscape'` |

**Slots (5 total, 4 required):**

| Slot | Pos | Rot | Size | Req |
|------|-----|-----|------|-----|
| `floor` | [0,-3,-20] | [-PI/2,0,0] | [8,50] | **yes** |
| `ceiling` | [0,3,-20] | [PI/2,0,0] | [8,50] | no |
| `left_wall` | [-4,0,-20] | [0,PI/2,0] | [50,6] | **yes** |
| `right_wall` | [4,0,-20] | [0,-PI/2,0] | [50,6] | **yes** |
| `end_wall` | [0,0,-45] | [0,0,0] | [8,6] | **yes** |

**Companion export:** `tunnelSlotGuidance` — per-slot `promptGuidance` and `expectsAlpha` for OBJ-051/OBJ-053.

---

### 5.3 Canyon (OBJ-020)

**File:** `src/scenes/geometries/canyon.ts`

Tall walls, floor, open sky. Vertically dramatic narrow space.

| Field | Value |
|-------|-------|
| `name` | `'canyon'` |
| `default_camera` | `'slow_push_forward'` |
| `compatible_cameras` | `slow_push_forward, crane_up, dramatic_push, gentle_float, static` |
| `fog` | `#1a1a2e, near: 15, far: 48` |
| `preferred_aspect` | `'landscape'` |

**Slots (6 total, 4 required):**

| Slot | Pos | Rot | Size | Req |
|------|-----|-----|------|-----|
| `sky` | [0,12,-20] | [PI/2,0,0] | [12,56] | **yes** |
| `left_wall` | [-4,3,-20] | [0,PI/2,0] | [56,18] | **yes** |
| `right_wall` | [4,3,-20] | [0,-PI/2,0] | [56,18] | **yes** |
| `floor` | [0,-3,-20] | [-PI/2,0,0] | [8,56] | **yes** |
| `end_wall` | [0,3,-48] | [0,0,0] | [8,18] | no |
| `subject` | [0,-1,-10] | [0,0,0] | [6,6] | no |

Canyon includes DepthSlot metadata (name, promptGuidance, expectsAlpha) directly in slot objects via structural typing — a different pattern than stage (which omits it) and tunnel (which exports it separately).

---

### 5.4 Flyover (OBJ-021)

**File:** `src/scenes/geometries/flyover.ts`

Aerial/bird's-eye perspective. Large ground plane below, sky above, landmarks.

| Field | Value |
|-------|-------|
| `name` | `'flyover'` |
| `default_camera` | `'slow_push_forward'` (until flyover_glide verified) |
| `compatible_cameras` | `static, flyover_glide, slow_push_forward, slow_pull_back, gentle_float` |
| `fog` | `#b8c6d4, near: 20, far: 55` |
| `preferred_aspect` | `'landscape'` |

**Slots (6 total, 2 required):**

| Slot | Pos | Rot | Size | Req |
|------|-----|-----|------|-----|
| `sky` | [0,20,-50] | [0,0,0] | [130,60] | **yes** |
| `ground` | [0,-4,-20] | [-PI/2,0,0] | [60,80] | **yes** |
| `landmark_far` | [0,1,-35] | [0,0,0] | [12,10] | no |
| `landmark_left` | [-8,-1,-15] | [0,0,0] | [8,8] | no |
| `landmark_right` | [8,-1,-18] | [0,0,0] | [8,8] | no |
| `near_fg` | [0,-2,-3] | [0,0,0] | [20,6] | no |

---

### 5.5 Diorama (OBJ-022)

**File:** `src/scenes/geometries/diorama.ts`

Victorian paper theater — semicircle of planes with inward-rotated wings.

| Field | Value |
|-------|-------|
| `name` | `'diorama'` |
| `default_camera` | `'slow_push_forward'` |
| `compatible_cameras` | `static, slow_push_forward, slow_pull_back, gentle_float, dramatic_push` |
| `fog` | `#0d0d1a, near: 15, far: 45` |
| `preferred_aspect` | `'landscape'` |

**Slots (6 total, 2 required):**

| Slot | Pos | Rot | Size | Req |
|------|-----|-----|------|-----|
| `backdrop` | [0,0,-30] | [0,0,0] | [75,45] | **yes** |
| `wing_left` | [-8,0,-18] | [0,PI/10,0] | [18,28] | no |
| `wing_right` | [8,0,-18] | [0,-PI/10,0] | [18,28] | no |
| `midground` | [0,-1,-12] | [0,0,0] | [30,20] | no |
| `subject` | [0,-0.5,-5] | [0,0,0] | [12,12] | **yes** |
| `near_fg` | [0,0,-1] | [0,0,0] | [25,16] | no |

Wing rotation of ~18 degrees (PI/10) is the defining spatial feature — produces real perspective foreshortening distinguishing diorama from flat parallax.

---

### 5.6 Close-Up (OBJ-025)

**File:** `src/scenes/geometries/close_up.ts`

Intimate framing. Subject dominates the view. Fewest slots (3).

| Field | Value |
|-------|-------|
| `name` | `'close_up'` |
| `default_camera` | `'gentle_float'` |
| `compatible_cameras` | `static, slow_push_forward, slow_pull_back, gentle_float` |
| `fog` | `#000000, near: 10, far: 25` |
| `preferred_aspect` | `'both'` |

**Slots (3 total, 2 required):**

| Slot | Pos | Rot | Size | Req | FogImm |
|------|-----|-----|------|-----|--------|
| `backdrop` | [0,0,-15] | [0,0,0] | [45,28] | **yes** | **yes** |
| `subject` | [0,0,-2] | [0,0,0] | [10,10] | **yes** | **yes** |
| `accent` | [0,0,-0.5] | [0,0,0] | [18,12] | no | **yes** |

All three slots are fog-immune. Subject at Z=-2 (distance 7) is the shallowest of any geometry.

---

### 5.7 Portal (OBJ-023) — UNSPECIFIED

> **Status:** Description only (no full spec). Depends on OBJ-005, OBJ-007.
>
> Concentric frames/planes at increasing Z-depth creating a "looking through layers" effect. Camera pushes through them. Good for transitions or dreamlike sequences.

### 5.8 Panorama (OBJ-024) — UNSPECIFIED

> **Status:** Description only (no full spec). Depends on OBJ-005, OBJ-007.
>
> Very wide backdrop plane (or curved set of planes approximating a cylinder). Camera rotates (pans) rather than translates. No foreground elements. Pure environment.

---

## 6. Tier 2 — Camera Path Implementations

All camera presets implement `CameraPathPreset` (OBJ-006). All call `resolveCameraParams()` at the top of evaluate(). Offset is applied by the renderer post-evaluate, not by presets.

### 6.1 Static (OBJ-026)

**File:** `src/camera/presets/static.ts`

Fixed position/orientation. Zero displacement. Reference implementation.

| Field | Value |
|-------|-------|
| `name` | `'static'` |
| `defaultEasing` | `'linear'` |
| `start/end position` | `[0, 0, 5]` |
| `start/end lookAt` | `[0, 0, 0]` |
| `fov` | `50` (constant) |
| `compatibleGeometries` | All 8 geometries |
| `oversizeRequirements` | All 0, factor 1.0 |

Speed and easing resolved but ignored (zero displacement scaled by any factor is zero).

---

### 6.2 Push/Pull (OBJ-027)

**File:** `src/camera/presets/push_pull.ts`

Two presets sharing a common path function:

| | `slow_push_forward` | `slow_pull_back` |
|---|---|---|
| `start.position` | `[0, 0, 5]` | `[0, 0, -3]` |
| `end.position` | `[0, 0, -3]` | `[0, 0, 5]` |
| `lookAt` | `[0, 0, -30]` (fixed) | `[0, 0, -30]` (fixed) |
| `fov` | 50 (constant) | 50 (constant) |
| `defaultEasing` | `ease_in_out` | `ease_in_out` |
| `maxDisplacementZ` | 8 | 8 |
| `recommendedOversizeFactor` | 1.3 | 1.3 |
| `compatibleGeometries` | stage, tunnel, canyon, flyover, diorama, portal, close_up (excludes panorama) | same |

---

### 6.3 Lateral Track (OBJ-028)

**File:** `src/camera/presets/lateral_track.ts`

Two presets: `lateral_track_left` and `lateral_track_right`.

| Field | left | right |
|-------|------|-------|
| `start.position` | `[3, 0, 5]` | `[-3, 0, 5]` |
| `end.position` | `[-3, 0, 5]` | `[3, 0, 5]` |
| `lookAt` | `[-1, 0, -10]` (static) | `[1, 0, -10]` (static) |
| `maxDisplacementX` | 6 | 6 |
| `defaultEasing` | `ease_in_out` | `ease_in_out` |
| `compatibleGeometries` | stage, diorama, portal, panorama, close_up (excludes tunnel, canyon, flyover) | same |

Speed scales X displacement only. lookAt is static with 1-unit lead toward travel direction.

---

### 6.4 Tunnel Push (OBJ-029)

**File:** `src/camera/presets/tunnel_push.ts`

Deep Z-axis push for tunnel geometry only.

| Field | Value |
|-------|-------|
| `name` | `'tunnel_push_forward'` |
| `start.position` | `[0, -0.3, 5]` |
| `end.position` | `[0, 0, -20]` |
| `lookAt` | `[0, 0, -45]` (fixed, anchored to end wall) |
| `fov` | 50 (constant) |
| `defaultEasing` | `'ease_in_out_cubic'` |
| `maxDisplacementZ` | 25 |
| `maxDisplacementY` | 0.3 |
| `compatibleGeometries` | `['tunnel']` only |

Subtle Y-axis rise (-0.3 to 0) simulates grounded starting perspective.

---

### 6.5 Flyover Glide (OBJ-030)

**File:** `src/camera/presets/flyover-glide.ts`

Elevated aerial glide. Camera at Y=8, looking down.

| Field | Value |
|-------|-------|
| `name` | `'flyover_glide'` |
| `start.position` | `[0, 8, 5]` |
| `end.position` | `[0, 8, -25]` |
| `lookAt` | Tracks camera Z minus 15 units at Y=-2 |
| `fov` | 50 (constant) |
| `defaultEasing` | `'ease_in_out'` |
| `maxDisplacementZ` | 30 |
| `compatibleGeometries` | `['flyover']` only |

Constant downward viewing angle ~33.7 degrees below horizontal. Y and LOOK_AHEAD not scaled by speed.

---

### 6.6 Gentle Float (OBJ-031)

**File:** `src/camera/presets/gentle_float.ts`

Subtle multi-axis sinusoidal drift. Almost subliminal.

| Field | Value |
|-------|-------|
| `name` | `'gentle_float'` |
| `start/end` | `[0, 0, 5]` (returns to start) |
| `fov` | 50 (constant) |
| `defaultEasing` | `'linear'` |
| `compatibleGeometries` | All 8 geometries |

**Position amplitudes (speed=1.0):** X: +/-0.3, Y: +/-0.2, Z: +/-0.4

Incommensurate frequencies (X: 0.7, Y: 1.1, Z: 0.5 cycles/t) with phase offsets produce organic non-repeating drift. Fade envelope `sin(pi * easing(t))` forces zero displacement at t=0 and t=1. lookAt drifts independently with dampened oscillations.

---

### 6.7 Dramatic Push (OBJ-032) — UNSPECIFIED

> Faster forward push with ease-out for emphasis moments. More aggressive than slow_push_forward.

### 6.8 Crane Up (OBJ-033) — UNSPECIFIED

> Camera rises on Y-axis keeping lookAt steady. Reveals vertical space. Compatible with canyon, stage.

### 6.9 Dolly Zoom (OBJ-034) — UNSPECIFIED

> Simultaneous Z push + FOV animation (Hitchcock/Spielberg vertigo effect). May be deferred to post-V1.

---

## 7. Tier 3 — Validation & Sizing

### 7.1 Plane Sizing & Edge-Reveal (OBJ-040)

**Files:** `src/spatial/plane-sizing.ts`, `src/spatial/edge-reveal.ts`

#### Texture-to-Plane Sizing

**TextureSizeMode:**
- `'contain'` — fits texture AR within slot bounds (may letterbox). For subject/near_fg.
- `'cover'` — covers slot bounds completely (may extend beyond). For sky/backdrop/floor/walls.
- `'stretch'` — exact slot size, may distort. For abstract/procedural textures.

**Functions:**
- `computeTexturePlaneSize(texW, texH, slotW, slotH, mode?) => TexturePlaneSizeResult`
- `suggestTextureSizeMode(slot) => TextureSizeMode` — heuristic based on transparent/fogImmune/rotation

#### Edge-Reveal Computation

**PlaneMargins:** `{ left, right, top, bottom }` — positive = safe, negative = edge reveal.

**Key Functions:**
- `computeFacingPlaneMargins(cameraState, planeTransform, aspectRatio)` — margins for a facing-camera plane at a single camera position
- `validateFacingPlaneEdgeReveal(preset, planeTransform, aspectRatio, params?, numSamples?)` — sampling-based check across the full camera path
- `validateGeometryEdgeReveal(geometry, preset, aspectRatio, params?)` — validates all slots in a geometry against a camera path
- `computeMinimumFacingPlaneSize(preset, planePos, aspectRatio, params?)` — minimum size to prevent edge reveal
- `computeOversizeFactor(minSize, slotSize)` — how much bigger the slot is than required
- `isFacingCameraRotation(rotation)` — true for [0,0,0] rotation

#### Design Decisions

- Sampling-based validation (100 samples default) for general camera paths.
- Analytical approach possible for axis-aligned planes with linear camera motion.
- Only facing-camera planes are validated analytically; rotated planes (floor, walls) use sampling.
- offset from CameraParams added to displacement when computing margins.

---

### 7.2 Spatial Compatibility Validation (OBJ-041)

**Files:** `src/validation/spatial-compatibility.ts`, `src/validation/coverage-analysis.ts`

#### Scene-Level Validation

`validateSceneSpatialCompatibility(sceneId, geometryName, cameraName, cameraParams, aspectRatio, geoRegistry, camRegistry)` checks:
1. Camera path name exists in camera registry
2. Camera name in geometry's compatible_cameras
3. Geometry name in camera's compatibleGeometries
4. Oversizing sufficiency at given speed/offset/aspect

#### Registry Consistency

`validateRegistryConsistency(geoRegistry, camRegistry)` checks:
1. All compatible_cameras entries exist in camera registry
2. All compatibleGeometries entries exist in geometry registry
3. Bidirectional agreement (if G lists C, then C must list G)
4. Every geometry has at least one valid camera

#### Coverage Analysis (TC-08)

`analyzeCoverage(geoRegistry, camRegistry)` produces a matrix showing which geometry-camera combinations are compatible. `formatCoverageMatrix()` renders it as a human-readable table.

#### SpatialValidationError Structure

```typescript
{
  category: 'compatibility' | 'registry_consistency' | 'oversizing',
  sceneId: string | null,
  message: string,       // Human-readable, actionable
  suggestion: string     // Phrased as LLM instruction
}
```

---

## 8. Deferred Spatial Nodes

These nodes are in the spatial category but have no full specification. They represent future work.

| Node | Description | Dependencies |
|------|-------------|-------------|
| OBJ-042 | Fog override system — per-scene fog customization | OBJ-005 |
| OBJ-043 | HUD/overlay planes — screen-space elements that don't move with camera | OBJ-005 |
| OBJ-044 | Per-frame opacity animation — keyframe system for plane opacity | OBJ-005, OBJ-007 |
| OBJ-045 | Portrait/vertical adaptation — auto-adjust plane sizes for 9:16 | OBJ-005, OBJ-040 |
| OBJ-079 | Camera path chaining — compose multiple paths in sequence | OBJ-006 |
| OBJ-080 | Dynamic plane count — variable number of slots per scene | OBJ-005 |
| OBJ-081 | Lighting system — Three.js lights for depth enhancement | OBJ-005 |

---

## 9. Geometry-Camera Compatibility Matrix

Bidirectional declarations from verified specs. **Bold** = geometry's default camera.

| Geometry | static | slow_push_fwd | slow_pull_back | lateral_track_L/R | tunnel_push_fwd | flyover_glide | gentle_float | dramatic_push | crane_up |
|----------|--------|---------------|----------------|-------------------|-----------------|---------------|-------------|---------------|----------|
| stage | yes | **yes** | yes | yes | - | - | yes | yes* | yes* |
| tunnel | yes | yes | - | - | **yes** | - | yes | - | - |
| canyon | yes | **yes** | - | - | - | - | yes | yes* | yes* |
| flyover | yes | **yes**^ | yes | - | - | yes | yes | - | - |
| diorama | yes | **yes** | yes | - | - | - | yes | yes* | - |
| close_up | yes | yes | yes | - | - | - | **yes** | - | - |
| portal** | yes | yes | yes | yes | - | - | yes | yes* | - |
| panorama** | yes | - | - | yes | - | - | yes | - | - |

`*` = camera preset UNSPECIFIED (OBJ-032/033), compatibility declared by geometry but preset not yet built.
`^` = flyover's default_camera is slow_push_forward pending flyover_glide verification.
`**` = geometry UNSPECIFIED (OBJ-023/024), compatibility declared by camera presets only.

---

## 10. Integration Boundary Map

### Spatial -> Engine Category

| Spatial Module | Engine Consumer | Interface |
|---------------|----------------|-----------|
| OBJ-003 types (Vec3, CameraState) | OBJ-010 Scene Sequencer | Type imports for timing/camera state |
| OBJ-005 registry (getGeometry) | OBJ-017 Manifest Validation | Geometry lookup for slot validation |
| OBJ-005 registry (getGeometry) | OBJ-036 Scene Sequencer | Geometry lookup per scene |
| OBJ-005 PlaneSlot | OBJ-039 Page Renderer | Mesh creation from slot data |
| OBJ-006 evaluate() | OBJ-036 Scene Sequencer | Per-frame camera state computation |
| OBJ-006 registry | OBJ-017 Manifest Validation | Camera name validation |
| OBJ-007 validatePlaneSlots | OBJ-017 Manifest Validation | Slot key validation |
| OBJ-007 resolveSlotTransform | OBJ-036 Scene Sequencer | Runtime slot resolution |
| OBJ-008 resolveTransition | OBJ-036 Scene Sequencer | Timeline construction |
| OBJ-008 computeTransitionOpacity | OBJ-037 Transition Renderer | Per-frame opacity |
| OBJ-040 sizing | OBJ-039 Page Renderer | Texture-to-plane auto-sizing |
| OBJ-041 validation | OBJ-017 Manifest Validation | Spatial compatibility checking |

### Spatial -> Integration Category

| Spatial Module | Integration Consumer | Interface |
|---------------|---------------------|-----------|
| OBJ-007 DepthSlot.promptGuidance | OBJ-051 SKILL.md | Slot documentation generation |
| OBJ-007 DepthSlot.expectsAlpha | OBJ-053 Prompt Templates | Alpha requirement for asset pipeline |
| OBJ-005 SceneGeometry.description | OBJ-071 SKILL.md geometry ref | Geometry documentation |
| OBJ-006 CameraPathPreset.tags | OBJ-071 SKILL.md camera ref | Preset search/selection |

### Cross-Category Dependency (Engine -> Spatial)

| Engine Module | Spatial Dependency |
|--------------|-------------------|
| OBJ-002 Easing/Interpolation | Used by OBJ-006 (resolveCameraParams), OBJ-008 (transition opacity) |

---

## 11. Inconsistencies & Open Conflicts

### INCONSISTENCY-1: PlaneSlot vs DepthSlot Type Gap

**OBJ-005** defines `PlaneSlot` (extends PlaneTransform + required, description, renderOrder?, transparent?, fogImmune?) for the geometry registry.

**OBJ-007** defines `DepthSlot` (adds name, promptGuidance, expectsAlpha, renderOrder as required) for the depth model.

These are related but structurally different types. There is no formal subtype relationship. Geometry implementations handle this inconsistently:

- **Stage (OBJ-018):** Constructs `PlaneSlot` objects only. DepthSlot metadata (promptGuidance, expectsAlpha) is surfaced via OBJ-007's `DEFAULT_SLOT_TAXONOMY` separately.
- **Tunnel (OBJ-019):** Constructs `PlaneSlot` objects for registry + exports a separate `tunnelSlotGuidance` companion object with promptGuidance and expectsAlpha.
- **Canyon (OBJ-020):** Constructs objects satisfying BOTH PlaneSlot and DepthSlot via structural typing. DepthSlot metadata is inline in the slot objects.
- **Flyover (OBJ-021), Diorama (OBJ-022), Close-up (OBJ-025):** Follow the PlaneSlot-only pattern (like stage). No companion guidance export.

**Impact:** Consumers needing promptGuidance (OBJ-051 SKILL.md, OBJ-053 prompt templates) must use different access patterns depending on the geometry. No unified interface.

**Recommendation:** Either (a) merge DepthSlot metadata into PlaneSlot making it the single slot type, or (b) mandate a standard companion export pattern for all geometries. The canyon approach (structural typing to satisfy both) is the most pragmatic if both types must persist.

### INCONSISTENCY-2: Registry Pattern Divergence

**OBJ-005** (Geometry): Lock-on-first-read singleton. `getGeometryRegistry()` returns the global frozen registry. No parameter needed.

**OBJ-006** (Camera): Registry-as-parameter. `getCameraPath(registry, name)` takes the registry explicitly.

**Impact:** Downstream consumers (OBJ-041, OBJ-017) must use different patterns to access each registry. The geometry registry is a global singleton; the camera registry must be assembled and passed through.

**Recommendation:** Acceptable divergence per OBJ-006 D7 (testability rationale for parameter-based). Document the canonical assembly point for the camera registry.

### INCONSISTENCY-3: Incomplete Prompt Guidance Coverage

Only tunnel (OBJ-019) and canyon (OBJ-020) export per-slot prompt guidance. Stage, flyover, diorama, and close-up do not. For stage, the DEFAULT_SLOT_TAXONOMY provides guidance for standard slot names (sky, subject, near_fg), but stage-specific slots like `backdrop` and `floor` are not in the default taxonomy and have no explicit promptGuidance.

**Impact:** SKILL.md generation (OBJ-051) will have incomplete per-slot guidance for several geometries.

**Recommendation:** All geometry implementations should export a companion guidance object (like tunnelSlotGuidance) or include DepthSlot-compatible metadata inline (like canyon).

### INCONSISTENCY-4: Forward References to Unspecified Presets

Several verified geometry specs declare compatibility with unspecified camera presets:
- Stage lists `dramatic_push` (OBJ-032) and `crane_up` (OBJ-033)
- Canyon lists `dramatic_push` and `crane_up`
- Diorama lists `dramatic_push`

These presets have no verified spec — only meta.json descriptions. The compatibility declarations are provisional and cannot be validated by OBJ-041 until the presets are specified.

**Impact:** `validateRegistryConsistency()` will fail until these presets are specified, or will need to skip unregistered camera names.

**Recommendation:** Either (a) spec OBJ-032/033 before running registry consistency checks, or (b) modify `validateRegistryConsistency` to warn (not error) on camera names that don't exist in the camera registry.

### INCONSISTENCY-5: Flyover default_camera Provisional

Flyover (OBJ-021) declares `default_camera: 'slow_push_forward'` with a note that it should be updated to `flyover_glide` once that preset is verified. The flyover_glide preset (OBJ-030) IS verified and declares `compatibleGeometries: ['flyover']`. This is a coordination gap — the flyover geometry spec was likely written before flyover_glide was finalized.

**Recommendation:** Update flyover's `default_camera` to `'flyover_glide'` at implementation time.

### OPEN CONFLICT-1: OBJ-003 oversizeFactor Is Scalar; OBJ-040 Computes Per-Axis

OBJ-003's `computePlaneSize` accepts a scalar `oversizeFactor`. OBJ-040 computes per-axis minimum sizes based on camera displacement envelopes. These are compatible (OBJ-040 can compute a per-axis factor and pass the max to OBJ-003), but OBJ-003 D3 explicitly notes this as a "V1 simplification" with per-axis factors as a possible future addition.

**Status:** Not a conflict — compatible by design. Document that OBJ-040 is the authoritative sizing system and OBJ-003's scalar factor is for simple cases.

---

## 12. Consolidated File Manifest

```
src/
  spatial/
    index.ts                  # Barrel: types + constants + math + depth-model + plane-sizing + edge-reveal
    types.ts                  # OBJ-003: Vec3, EulerRotation, Size2D, FrustumRect, PlaneTransform,
                              #          PlaneSizingInput, PlaneSizingResult, CameraState
    constants.ts              # OBJ-003: AXIS, DEFAULT_CAMERA, COMPOSITION_PRESETS, FRAME_RATES,
                              #          PLANE_ROTATIONS
    math.ts                   # OBJ-003: computeFrustumRect, computePlaneSize, computeViewAxisDistance,
                              #          computeAspectCorrectSize, degToRad, radToDeg, distance3D,
                              #          normalize, dot, subtract, scale, add
    depth-model.ts            # OBJ-007: SlotName, SLOT_NAME_PATTERN, isValidSlotName, DepthSlot,
                              #          SlotSet, DEFAULT_SLOT_TAXONOMY, PlaneOverride, ResolvedSlot,
                              #          SlotValidationResult, validatePlaneSlots, resolveSlotTransform
    plane-sizing.ts           # OBJ-040: TextureSizeMode, computeTexturePlaneSize, suggestTextureSizeMode
    edge-reveal.ts            # OBJ-040: PlaneMargins, EdgeRevealCheck, computeFacingPlaneMargins,
                              #          validateFacingPlaneEdgeReveal, validateGeometryEdgeReveal,
                              #          computeMinimumFacingPlaneSize, computeOversizeFactor,
                              #          isFacingCameraRotation

  scenes/
    geometries/
      index.ts                # Barrel: types + registry + validate + slot-utils + all geometry imports
      types.ts                # OBJ-005: PlaneSlot, SceneGeometry, FogConfig, GeometryRegistry,
                              #          GeometryValidationError
      registry.ts             # OBJ-005: registerGeometry, getGeometry, getGeometryRegistry,
                              #          getGeometryNames
      validate.ts             # OBJ-005: validateGeometryDefinition
      slot-utils.ts           # OBJ-005: getRequiredSlotNames, getOptionalSlotNames, getAllSlotNames,
                              #          isCameraCompatible
      stage.ts                # OBJ-018: stageGeometry (6 slots, 3 required)
      tunnel.ts               # OBJ-019: tunnelGeometry + tunnelSlotGuidance (5 slots, 4 required)
      canyon.ts               # OBJ-020: canyonGeometry (6 slots, 4 required)
      flyover.ts              # OBJ-021: flyoverGeometry (6 slots, 2 required)
      diorama.ts              # OBJ-022: dioramaGeometry (6 slots, 2 required)
      close_up.ts             # OBJ-025: closeUpGeometry (3 slots, 2 required)
      # portal.ts             # OBJ-023: UNSPECIFIED
      # panorama.ts           # OBJ-024: UNSPECIFIED

  camera/
    index.ts                  # Barrel: types + registry + validate + all preset imports
    types.ts                  # OBJ-006: CameraFrameState, CameraParams, ResolvedCameraParams,
                              #          OversizeRequirements, CameraPathEvaluator, CameraPathPreset,
                              #          toCameraState(), resolveCameraParams()
    registry.ts               # OBJ-006: CameraPathRegistry, getCameraPath, isCameraPathName,
                              #          listCameraPathNames, getCameraPathsForGeometry
    validate.ts               # OBJ-006: validateCameraPathPreset, validateCameraParams
    presets/
      static.ts               # OBJ-026: staticPreset
      push_pull.ts            # OBJ-027: slowPushForward, slowPullBack
      lateral_track.ts        # OBJ-028: lateralTrackLeft, lateralTrackRight
      tunnel_push.ts          # OBJ-029: tunnelPushForward
      flyover-glide.ts        # OBJ-030: flyoverGlide
      gentle_float.ts         # OBJ-031: gentleFloat
      # dramatic_push.ts      # OBJ-032: UNSPECIFIED
      # crane_up.ts           # OBJ-033: UNSPECIFIED
      # dolly_zoom.ts         # OBJ-034: UNSPECIFIED

  transitions/
    index.ts                  # Barrel
    types.ts                  # OBJ-008: TransitionTypeName, TransitionSpec, ResolvedTransition,
                              #          TransitionOpacityResult
    presets.ts                # OBJ-008: TransitionPresetDefinition, transitionPresets,
                              #          isTransitionTypeName, getTransitionPreset
    compute.ts                # OBJ-008: computeTransitionOpacity
    resolve.ts                # OBJ-008: resolveTransition

  validation/
    spatial-compatibility.ts  # OBJ-041: SpatialValidationError, validateSceneSpatialCompatibility,
                              #          validateRegistryConsistency, checkOversizingSufficiency,
                              #          validateOversizing
    coverage-analysis.ts      # OBJ-041: analyzeCoverage, formatCoverageMatrix
```

---

## 13. Consolidated Acceptance Criteria Index

### OBJ-003: Spatial Math (14 ACs)
AC-01 through AC-14: Frustum computation, plane sizing, view axis distance, aspect-correct sizing, constants, barrel export.

### OBJ-005: Geometry Type Contract (16 ACs)
AC-01 through AC-16: Type structure, registry lifecycle, validation, slot utilities, deep freeze, barrel export.

### OBJ-006: Camera Path Type Contract (36 ACs)
AC-01 through AC-36: Type exports, toCameraState, resolveCameraParams, registry functions, validation (11 checks at 100 sample points), determinism, isomorphism.

### OBJ-007: Depth Model (23 ACs)
AC-01 through AC-23: Taxonomy structure, slot name validation, validatePlaneSlots (13 behavioral checks), resolveSlotTransform (4 merge scenarios), metadata, size validation.

### OBJ-008: Transitions (33 ACs)
AC-01 through AC-33: Preset registry, cut/crossfade/dip_to_black computation, resolve function, error handling, degenerate cases, purity/isomorphism.

### OBJ-018: Stage Geometry
Per-geometry ACs defined in OBJ-018 spec: slot count, positions, rotations, sizes, required flags, fog config, compatible cameras, registration side effect, all optional PlaneSlot fields explicitly set.

### OBJ-019: Tunnel Geometry
Per-geometry ACs: 5 slots (4 required), wall positioning, tunnel_push_forward as default, fog config, tunnelSlotGuidance companion export.

### OBJ-020: Canyon Geometry
Per-geometry ACs: 6 slots (4 required), wall height/depth, sky orientation, fog color, 3-unit near-edge safety margin.

### OBJ-021: Flyover Geometry
Per-geometry ACs: 6 slots (2 required), ground plane coverage, elevated sky, landmark positioning, aerial fog.

### OBJ-022: Diorama Geometry
Per-geometry ACs: 6 slots (2 required), wing rotation PI/10, theatrical fog, backdrop fog-immune.

### OBJ-025: Close-Up Geometry
Per-geometry ACs: 3 slots (2 required), shallowest subject (Z=-2), all slots fog-immune, accent renderOrder ensures correct compositing.

### OBJ-026 through OBJ-031: Camera Presets
Each preset validated by the standard conformance suite from OBJ-006: boundary start/end match, continuity (no NaN/Infinity), FOV in range, determinism, speed scaling, easing override, full validateCameraPathPreset pass.

### OBJ-040: Plane Sizing / Edge-Reveal
ACs for: TextureSizeMode contain/cover/stretch computation, suggestTextureSizeMode heuristic, margin computation, edge-reveal sampling validation, minimum plane size computation, oversize factor computation.

### OBJ-041: Spatial Compatibility
ACs for: scene-level compatibility (4 checks), registry consistency (4 checks), oversizing sufficiency, coverage analysis matrix.

**Total verified acceptance criteria across all spatial nodes: ~180+**
