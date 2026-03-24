# Specification: OBJ-001 — Project Scaffolding and Build System

## Summary

OBJ-001 establishes the depthkit Node.js project container: directory structure, package.json with all allowed dependencies, TypeScript configuration, and build pipeline. This is the Tier 0 foundation that every other objective imports from. It must satisfy C-01 (zero-license) by including only the explicitly allowed dependencies, and it must mirror the directory layout from seed Section 4.5 so that downstream objectives know exactly where to place their implementations.

## Interface Contract

OBJ-001 does not export runtime code. It exports **project structure** and **build tooling** that all subsequent objectives depend on. The contract is the file tree, the build commands, and the dependency manifest.

### Directory Structure

```
depthkit/
├── src/
│   ├── cli.ts                          # CLI entry point (OBJ-013)
│   ├── index.ts                        # Library entry point — re-exports public API
│   ├── engine/
│   │   ├── orchestrator.ts             # (OBJ-035) Main render loop
│   │   ├── puppeteer-bridge.ts         # (OBJ-009) Puppeteer launch, frame capture
│   │   ├── ffmpeg-encoder.ts           # (OBJ-012) FFmpeg child process
│   │   └── frame-clock.ts             # (OBJ-010) Virtualized clock
│   ├── scenes/
│   │   ├── scene-sequencer.ts          # (OBJ-015) Scene routing + transitions
│   │   ├── geometries/
│   │   │   ├── index.ts                # Geometry registry
│   │   │   └── [geometry].ts           # (OBJ-018–025) Individual geometries
│   │   └── cameras/
│   │       ├── path-presets.ts         # (OBJ-006) Camera path definitions
│   │       └── interpolate.ts          # (OBJ-007) Easing + interpolation
│   ├── manifest/
│   │   ├── schema.ts                   # (OBJ-004) Zod schema
│   │   └── loader.ts                   # (OBJ-004) Manifest parser/validator
│   └── page/                           # Files served to headless Chromium
│       ├── index.html                  # (OBJ-009) Minimal HTML shell
│       ├── scene-renderer.js           # (OBJ-005) Three.js scene setup — single esbuild entry point
│       ├── geometry-library.js         # (OBJ-005) Geometry defs, imported by scene-renderer.js
│       └── message-handler.js          # (OBJ-009) Frame command receiver, imported by scene-renderer.js
├── test/
│   ├── unit/                           # Unit tests mirror src/ structure
│   ├── integration/                    # End-to-end render tests
│   └── fixtures/                       # Test images/audio for integration tests (.gitkeep)
├── assets/                             # Runtime: per-video generated images + audio (gitignored)
│   ├── images/
│   └── audio/
├── dist/                               # Build output (gitignored)
├── package.json
├── tsconfig.json
├── tsconfig.build.json                 # Production build config
├── README.md                           # Project overview + prerequisites
└── .gitignore
```

**Key structural decisions:**

1. **`src/page/` files are plain JavaScript**, bundled by esbuild for headless Chromium. `scene-renderer.js` is the **single entry point** — it imports `geometry-library.js` and `message-handler.js`, and esbuild bundles all three (plus Three.js) into one output file at `dist/page/scene-renderer.js`.

2. **`src/page/index.html`** is a minimal valid HTML stub: `<!DOCTYPE html>`, `<html>`, `<body>`, a `<canvas id="depthkit-canvas">` element, and a `<script src="scene-renderer.js"></script>` tag. Contains a TODO comment referencing OBJ-009.

3. **`src/index.ts`** — the library entry point that re-exports the public API for programmatic use.

4. **`test/fixtures/`** — committed directory (with `.gitkeep`) for test images/audio used by integration tests. Distinct from `assets/` which is gitignored runtime content.

5. **`dist/`** — compiled output directory, gitignored.

### package.json Contract

```typescript
interface PackageJsonContract {
  name: "depthkit";
  version: "0.1.0";
  type: "module";
  main: "dist/index.js";
  bin: { depthkit: "dist/cli.js" };

  scripts: {
    build: string;              // "npm run build:node && npm run build:page"
    "build:node": string;       // "tsc -p tsconfig.build.json"
    "build:page": string;       // esbuild with flags specified in D-02, then cp index.html
    dev: string;                // Watch mode for development
    test: string;               // "vitest run"
    "test:unit": string;        // "vitest run test/unit"
    "test:integration": string; // "vitest run test/integration"
    lint: string;               // "eslint src/"
    typecheck: string;          // "tsc --noEmit"
    clean: string;              // "rm -rf dist" (Unix — see D-09)
  };

  dependencies: {
    three: string;              // MIT — 3D rendering
    puppeteer: string;          // Apache-2.0 — headless browser control
    "ffmpeg-static": string;    // GPL — bundled FFmpeg binary (stdio linking)
    zod: string;                // MIT — schema validation
    commander: string;          // MIT — CLI framework
  };

  devDependencies: {
    typescript: string;
    "@types/node": string;
    esbuild: string;            // Bundle src/page/ for browser
    vitest: string;
    eslint: string;
    "@typescript-eslint/parser": string;
    "@typescript-eslint/eslint-plugin": string;
  };

  engines: {
    node: ">=18.0.0";
  };
}
```

**Note on `@types/three`:** Three.js v0.160+ bundles its own TypeScript declarations. If the implementer selects a version >=0.160, `@types/three` is unnecessary and should be omitted. If an older version is chosen, `@types/three` must be added to devDependencies **at the same version** as the `three` package. The implementer must verify this at implementation time.

### tsconfig.json Contract

```typescript
interface TsConfigContract {
  compilerOptions: {
    target: "ES2022";
    module: "Node16";
    moduleResolution: "Node16";
    outDir: "dist";
    rootDir: "src";
    strict: true;
    esModuleInterop: true;
    declaration: true;
    declarationMap: true;
    sourceMap: true;
    skipLibCheck: true;
    forceConsistentCasingInFileNames: true;
    resolveJsonModule: true;
  };
  include: ["src/**/*.ts"];
  exclude: ["src/page/**", "node_modules", "dist", "test"];
}
```

`src/page/` is excluded from TypeScript compilation — those files target the browser and are handled by esbuild.

### tsconfig.build.json

Extends `tsconfig.json`. Used for production builds. May strip `sourceMap` or add `declarationDir` as needed. Inherits the same `exclude` of `src/page/`.

### Build Pipeline Contract

Two outputs:

1. **Node.js modules** (`dist/`) — compiled from TypeScript via `tsc -p tsconfig.build.json`.
2. **Browser bundle** (`dist/page/scene-renderer.js`) — `src/page/scene-renderer.js` bundled via esbuild with Three.js included.

**esbuild command specification:**
```
esbuild src/page/scene-renderer.js \
  --bundle \
  --format=iife \
  --platform=browser \
  --outdir=dist/page
```

- `--format=iife` — the output is loaded via a `<script>` tag in headless Chromium, not imported as a module. IIFE wraps everything in a function scope, avoiding global pollution.
- `--platform=browser` — tells esbuild to resolve for browser environment (e.g., excludes Node.js built-ins).
- `--bundle` — resolves and inlines all imports, including `three` from `node_modules/`.

The `index.html` file is **copied** (not bundled) from `src/page/index.html` to `dist/page/index.html` as part of the `build:page` script. The copy can be a simple `cp` command chained after the esbuild invocation.

### Stub Files

OBJ-001 creates **placeholder stub files** for every file in the directory structure. Each stub is syntactically valid and compiles/bundles without errors. Each contains a TODO comment referencing the owning objective.

**TypeScript stubs** (`src/**/*.ts`):
```typescript
// src/engine/orchestrator.ts
// TODO: OBJ-035 — Main render loop: Puppeteer + FFmpeg coordination
export {};
```

**JavaScript stubs** (`src/page/*.js`):

`src/page/scene-renderer.js` — the esbuild entry point — must contain a Three.js import to validate bundling:
```javascript
// src/page/scene-renderer.js
// TODO: OBJ-005 — Three.js scene setup, texture loading, render loop
// Entry point for browser bundle. Imports geometry-library and message-handler.
import * as THREE from 'three';
import './geometry-library.js';
import './message-handler.js';

// Stub: confirm Three.js loaded
console.log('depthkit page loaded, THREE revision:', THREE.REVISION);
```

`src/page/geometry-library.js`:
```javascript
// src/page/geometry-library.js
// TODO: OBJ-005 — Geometry definitions (browser-side)
export {};
```

`src/page/message-handler.js`:
```javascript
// src/page/message-handler.js
// TODO: OBJ-009 — Receives frame commands from Puppeteer orchestrator
export {};
```

**HTML stub** (`src/page/index.html`):
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>depthkit</title>
  <style>
    * { margin: 0; padding: 0; }
    canvas { display: block; }
  </style>
</head>
<body>
  <!-- TODO: OBJ-009 — Puppeteer loads this page and communicates via CDP -->
  <canvas id="depthkit-canvas"></canvas>
  <script src="scene-renderer.js"></script>
</body>
</html>
```

**CLI stub** (`src/cli.ts`):
```typescript
// src/cli.ts
// TODO: OBJ-013 — Full CLI implementation
import { Command } from 'commander';

const program = new Command();
program
  .name('depthkit')
  .description('2.5D parallax video engine')
  .version('0.1.0');

program.parse();
```

This ensures `node dist/cli.js --help` produces output (AC-07).

### README.md Stub

A `README.md` at the project root with the following sections:

- **Overview** — one paragraph describing depthkit.
- **Prerequisites** — Node.js >=18, and notes:
  - Puppeteer downloads Chromium on `npm install`. In Docker/CI, set `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true` and ensure Chromium is available in the image.
  - FFmpeg: bundled via `ffmpeg-static`. To use a system-installed FFmpeg instead, set `FFMPEG_PATH=/path/to/ffmpeg`.
- **Quick Start** — `npm install`, `npm run build`, `npx depthkit --help`.
- **Development** — `npm run dev`, `npm test`.
- All sections are stubs with TODO markers for expansion by later objectives.

## Design Decisions

### D-01: ESM over CommonJS
**Choice:** `"type": "module"` with ESM imports throughout.
**Rationale:** Three.js v0.150+ ships ESM-first. Puppeteer supports ESM. Modern Node.js (>=18) has stable ESM support. Avoids dual-module complexity.

### D-02: esbuild for Browser Bundle
**Choice:** esbuild for bundling `src/page/` into a browser-ready IIFE script.
**Rationale:** `src/page/` files run inside headless Chromium and need Three.js bundled in. esbuild is zero-config, fast, and MIT licensed. Alternatives: webpack (too heavy), rollup (viable but more config). esbuild is a devDependency only.
**Flags:** `--bundle --format=iife --platform=browser --outdir=dist/page`. IIFE because the script loads via `<script>` tag, not as an ES module.

### D-03: Vitest over Jest
**Choice:** Vitest as the test runner.
**Rationale:** Native ESM support without transform hacks. Fast. Compatible with `"type": "module"`.

### D-04: ffmpeg-static as Default, System FFmpeg as Fallback
**Choice:** `ffmpeg-static` in dependencies; `FFMPEG_PATH` env var for override.
**Rationale:** Out-of-the-box experience. Docker/CI environments can skip the bundled binary. Satisfies C-01 allowance.

### D-05: Node.js >= 18 Baseline
**Choice:** `engines.node >= 18.0.0`.
**Rationale:** Stable ESM, `fetch`, `crypto.randomUUID()`. VPS deployment (C-08) allows version control.

### D-06: Stub Files for All Planned Modules
**Choice:** Syntactically valid stubs for every module, with TODO + objective ID.
**Rationale:** Downstream objectives import from known paths immediately. Empty stubs that only `export {}` intentionally break if a consumer tries to import a named export — forcing the implementing objective to populate the stub first.

### D-07: src/page/ as Plain JS with Single Entry Point
**Choice:** `src/page/` files are authored as JavaScript. `scene-renderer.js` is the **single esbuild entry point** that imports `geometry-library.js` and `message-handler.js`. esbuild bundles all three plus Three.js into one output file.
**Rationale:** These files run in Chromium's V8, not Node.js. Plain JS with a single entry point keeps the build simple. If downstream objectives need shared TypeScript types between Node and browser, they can introduce a `tsconfig.browser.json` — that's out of OBJ-001's scope.

### D-08: Declaration Files for Library API
**Choice:** `declaration: true` in tsconfig.
**Rationale:** The seed requires "an importable library for programmatic use." `.d.ts` files enable type-safe consumption.

### D-09: Unix-Assumed Clean Script
**Choice:** `clean` script is `rm -rf dist`. No cross-platform wrapper (no `rimraf` dependency).
**Rationale:** Per C-08 (4-core VPS) and C-11 (Docker), the target environments are Unix-like. Adding `rimraf` as a devDependency for Windows compatibility is unnecessary scope. If Windows support is needed later, this is a one-line change.

## Acceptance Criteria

- [ ] **AC-01:** `npm install` succeeds with zero errors. All runtime dependencies are exactly: `three`, `puppeteer`, `ffmpeg-static`, `zod`, `commander`. No other packages appear in `dependencies`.
- [ ] **AC-02:** `npm run build` succeeds, producing `dist/` with compiled Node.js modules (`dist/cli.js`, `dist/index.js`, `dist/engine/`, `dist/scenes/`, `dist/manifest/`) and a bundled `dist/page/` directory containing `scene-renderer.js` and `index.html`.
- [ ] **AC-03:** `npm run typecheck` succeeds with zero TypeScript errors on all stub files.
- [ ] **AC-04:** `npm test` executes vitest and reports zero failures. At least one smoke test exists (see Test Strategy).
- [ ] **AC-05:** The directory structure matches the structure defined above, including all subdirectories, all stub files, `src/page/index.html`, `test/fixtures/` (with `.gitkeep`), and `README.md`.
- [ ] **AC-06:** Every stub file in `src/` contains a TODO comment referencing the objective ID that owns it.
- [ ] **AC-07:** Running `node dist/cli.js --help` prints a help message including the name "depthkit" and version "0.1.0".
- [ ] **AC-08:** `dist/index.js` is importable as an ES module: `import {} from './dist/index.js'` resolves without error.
- [ ] **AC-09:** All runtime dependencies satisfy C-01. Verification: `npx license-checker --production --summary` shows only MIT, Apache-2.0, ISC, BSD-2-Clause, BSD-3-Clause, or (for ffmpeg-static only) LGPL/GPL.
- [ ] **AC-10:** `.gitignore` excludes `node_modules/`, `dist/`, and `assets/`. `test/fixtures/` is NOT gitignored.
- [ ] **AC-11:** `package.json` contains `"engines": { "node": ">=18.0.0" }`.
- [ ] **AC-12:** The esbuild bundle at `dist/page/scene-renderer.js` includes Three.js code. Verified by: the file exists AND its size is >500KB (Three.js alone is ~1MB when bundled).
- [ ] **AC-13:** `README.md` exists at project root and contains sections for Prerequisites (mentioning `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD` and `FFMPEG_PATH`) and Quick Start.

## Edge Cases and Error Handling

1. **Missing FFmpeg:** If `ffmpeg-static` fails to install (unsupported platform), `npm install` should still complete for the other packages. FFmpeg runtime resolution (OBJ-012) will handle the fallback. For scaffolding, the dependency is declared; runtime resolution is a downstream concern.

2. **Node.js version mismatch:** If `npm install` runs on Node <18, npm emits a warning via the `engines` field. The build may still succeed but is unsupported.

3. **Puppeteer Chromium download in CI/Docker:** Puppeteer downloads ~300MB of Chromium on install. In constrained environments, set `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true` and ensure Chromium is available. Documented in README.md.

4. **esbuild bundling Three.js size:** The `dist/page/scene-renderer.js` bundle will be ~1-2MB due to Three.js. Acceptable — it loads into a local headless Chromium, not a remote browser. No tree-shaking for V1 (AP-05).

5. **Empty stub imports:** If a downstream objective tries `import { Orchestrator } from '../engine/orchestrator.js'` but the stub only has `export {}`, TypeScript errors at compile time. This is intentional — it forces the implementing objective to populate the stub before consumers can build against it.

6. **esbuild resolving Three.js from node_modules:** esbuild must be able to resolve `three` from `node_modules/` when bundling `src/page/scene-renderer.js`. Since `three` is a runtime dependency (listed in `dependencies`), it will be installed. No additional esbuild configuration (`--external`, etc.) is needed — `three` should be bundled in, not externalized.

## Test Strategy

OBJ-001's tests verify scaffolding correctness, not application logic:

1. **Smoke test** (`test/unit/scaffold.test.ts`):
   - Asserts `import('../src/index.js')` resolves without error.
   - Asserts the CLI module exists at the expected path.
   - A trivial assertion (`expect(true).toBe(true)`) to confirm vitest runs.
   - Validates AC-04.

2. **Build verification:** `npm run build` succeeding is the primary structural test (AC-02). CI should run this.

3. **Bundle size check:** After build, verify `dist/page/scene-renderer.js` is >500KB (AC-12). This can be a manual check or a test that reads `fs.statSync`.

4. **License audit:** Run `npx license-checker --production --summary` and verify no runtime dependency carries a license outside the C-01 allowlist. This can be manual for V1 or automated as a test.

**Relevant testable claims:** None directly — OBJ-001 is infrastructure. Enables TC-06, TC-11, and all others by providing the project container.

## Integration Points

### Depends on
Nothing — Tier 0 foundational objective.

### Consumed by (blocked objectives)
- **OBJ-004** (Manifest schema + Zod validation) — needs `src/manifest/schema.ts` and `src/manifest/loader.ts` stubs, and `zod` in dependencies.
- **OBJ-009** (Puppeteer bridge) — needs `src/engine/puppeteer-bridge.ts` stub, `src/page/index.html`, `src/page/message-handler.js`, and `puppeteer` in dependencies.
- **OBJ-010** (Frame clock) — needs `src/engine/frame-clock.ts` stub.
- **OBJ-013** (CLI) — needs `src/cli.ts` stub and `commander` in dependencies.

### File Placement
All files listed in the Directory Structure section. The implementer creates the full tree with stubs as specified.

## Open Questions

1. **Three.js version pinning:** Three.js has no semver stability guarantees. **Recommendation:** Pin to a specific minor version (e.g., `"three": "0.170.0"` — not `^0.170.0`). The implementer chooses the current stable release at implementation time. If the chosen version is >=0.160, `@types/three` is unnecessary (types are bundled). If <0.160, add `@types/three` at the matching version.

2. **Monorepo potential:** The n8n HTTP wrapper (OBJ-046+) could be a separate package. **Decision:** OBJ-001 is a single package. Monorepo structure is out of scope. The HTTP wrapper depends on `depthkit` as an external package.

3. **`src/page/` TypeScript option:** If downstream objectives need type-safe geometry definitions shared between Node and browser, they can introduce a `tsconfig.browser.json`. OBJ-001 does not block this but does not implement it.
