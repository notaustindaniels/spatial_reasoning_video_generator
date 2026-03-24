# Deliberation Transcript: OBJ-001

---

## Round 1 — spec_author

# Specification Proposal: OBJ-001 — Project Scaffolding and Build System

## Summary

OBJ-001 establishes the depthkit Node.js project container: directory structure, package.json with all allowed dependencies, TypeScript configuration, and build pipeline. This is the Tier 0 foundation that every other objective imports from. It must satisfy C-01 (zero-license) by including only the explicitly allowed dependencies, and it must mirror the directory layout from seed Section 4.5 so that downstream objectives know exactly where to place their implementations.

## Interface Contract

OBJ-001 does not export runtime code. It exports **project structure** and **build tooling** that all subsequent objectives depend on. The contract is the file tree, the build commands, and the dependency manifest.

### Directory Structure (from Seed §4.5, with clarifications)

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
│       ├── index.html                  # (OBJ-009) HTML shell with canvas
│       ├── scene-renderer.js           # (OBJ-005) Three.js scene setup
│       ├── geometry-library.js         # (OBJ-005) Geometry defs (browser-side)
│       └── message-handler.js          # (OBJ-009) Frame command receiver
├── test/
│   ├── unit/                           # Unit tests mirror src/ structure
│   └── integration/                    # End-to-end render tests
├── assets/                             # Runtime: per-video images + audio
│   ├── images/
│   └── audio/
├── dist/                               # Build output (gitignored)
├── package.json
├── tsconfig.json
├── tsconfig.build.json                 # Separate config for production build
└── .gitignore
```

**Key structural decisions:**

1. **`src/page/` files are plain JavaScript (or bundled separately)** — they run inside headless Chromium, not in Node.js. The TypeScript build pipeline compiles `src/` → `dist/` but `src/page/` files need a different treatment: either they remain as `.js` files copied to `dist/page/` as-is, or they are bundled with a lightweight bundler (esbuild) into a single browser-ready script. The build system must handle this split.

2. **`src/index.ts`** — the library entry point that re-exports the public API for programmatic use (as opposed to CLI use). This supports the seed's requirement for "an importable library for programmatic use."

3. **`dist/`** — the compiled output directory. The CLI and library entry points resolve from here.

### package.json Contract

```typescript
// These are the contracts, not the literal file — implementer fills in versions
interface PackageJsonContract {
  name: "depthkit";
  version: "0.1.0";
  type: "module";               // ESM modules
  main: "dist/index.js";        // Library entry
  bin: { depthkit: "dist/cli.js" };  // CLI entry
  
  scripts: {
    build: string;              // Compile TS → JS, bundle page assets
    "build:node": string;       // Compile src/ (excluding page/) via tsc
    "build:page": string;       // Bundle src/page/ for browser via esbuild
    dev: string;                // Watch mode for development
    test: string;               // Run test suite
    "test:unit": string;
    "test:integration": string;
    lint: string;               // ESLint
    typecheck: string;          // tsc --noEmit
    clean: string;              // Remove dist/
  };

  dependencies: {
    three: string;              // MIT — 3D rendering
    puppeteer: string;          // Apache-2.0 — headless browser control
    "ffmpeg-static": string;    // GPL — bundled FFmpeg binary (stdio linking)
    zod: string;                // MIT — schema validation
    commander: string;          // MIT — CLI framework
  };

  devDependencies: {
    typescript: string;         // Build tooling
    "@types/node": string;
    "@types/three": string;
    esbuild: string;            // Bundle src/page/ for browser
    vitest: string;             // Test runner
    eslint: string;             // Linting
    "@typescript-eslint/parser": string;
    "@typescript-eslint/eslint-plugin": string;
  };

  engines: {
    node: ">=18.0.0";           // LTS baseline
  };
}
```

### tsconfig.json Contract

```typescript
interface TsConfigContract {
  compilerOptions: {
    target: "ES2022";           // Modern Node.js
    module: "Node16";           // ESM with Node.js module resolution
    moduleResolution: "Node16";
    outDir: "dist";
    rootDir: "src";
    strict: true;
    esModuleInterop: true;
    declaration: true;          // Generate .d.ts for library consumers
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

**Note:** `src/page/` is excluded from the TypeScript compilation because those files target the browser (Chromium) and use a different module system. They are handled by the `build:page` script using esbuild.

### tsconfig.build.json

Extends tsconfig.json, strips test-related settings, used only for production builds. May further exclude test utilities or dev-only exports.

### Build Pipeline Contract

The build system must produce two outputs:

1. **Node.js modules** (`dist/cli.js`, `dist/index.js`, `dist/engine/`, `dist/scenes/`, `dist/manifest/`) — compiled from TypeScript via `tsc`.
2. **Browser bundle** (`dist/page/`) — `src/page/*.js` bundled via esbuild into a self-contained script that Puppeteer loads. Three.js is bundled into this browser script (not loaded from CDN).

```
build:node  →  tsc -p tsconfig.build.json  →  dist/ (Node.js modules)
build:page  →  esbuild src/page/scene-renderer.js --bundle --outdir=dist/page  →  dist/page/ (browser bundle)
build       →  build:node && build:page
```

### Stub Files

OBJ-001 must create **placeholder stub files** for every file in the directory structure, each exporting an empty interface or a TODO comment. This allows downstream objectives to import from known paths immediately. The stubs must be syntactically valid TypeScript that compiles without errors.

Example stub:
```typescript
// src/engine/orchestrator.ts
// TODO: OBJ-035 — Main render loop: Puppeteer + FFmpeg coordination
export {};
```

For `src/page/` files, stubs are valid JavaScript:
```javascript
// src/page/scene-renderer.js
// TODO: OBJ-005 — Three.js scene setup, texture loading, render loop
```

## Design Decisions

### D-01: ESM over CommonJS
**Choice:** `"type": "module"` with ESM imports throughout.
**Rationale:** Three.js v0.150+ ships ESM-first. Puppeteer supports ESM. Modern Node.js (≥18) has stable ESM support. Avoids dual-module complexity.

### D-02: esbuild for Browser Bundle
**Choice:** esbuild for bundling `src/page/` into a browser-ready script.
**Rationale:** The `src/page/` files run inside headless Chromium and need Three.js bundled in. esbuild is zero-config, extremely fast, and has no licensing concerns. Alternatives considered: webpack (too heavy for this use case), rollup (viable but more config). esbuild is already common as a devDependency.
**Constraint:** esbuild is a devDependency only — it does not appear in production `dependencies`.

### D-03: Vitest over Jest
**Choice:** Vitest as the test runner.
**Rationale:** Native ESM support without transform hacks. Fast. Compatible with the `"type": "module"` project setup. Jest requires additional configuration for ESM projects.

### D-04: ffmpeg-static as Default, System FFmpeg as Fallback
**Choice:** Include `ffmpeg-static` in dependencies for a bundled FFmpeg binary. The engine should also accept a `FFMPEG_PATH` environment variable to use a system-installed FFmpeg.
**Rationale:** `ffmpeg-static` ensures the engine works out of the box without requiring the user to install FFmpeg separately. The env var fallback supports Docker/CI environments where FFmpeg is pre-installed and the bundled binary is unnecessary. This satisfies C-01's allowance of `ffmpeg-static` and the note about "FFmpeg installed on the host machine."

### D-05: Node.js ≥18 Baseline
**Choice:** `engines.node >= 18.0.0`.
**Rationale:** Node 18 is LTS with stable ESM, `fetch`, and `crypto.randomUUID()`. The seed targets VPS deployment (C-08) where Node version is controllable.

### D-06: Stub Files for All Planned Modules
**Choice:** Create syntactically valid stub files for every module in the directory tree.
**Rationale:** Downstream objectives (OBJ-004, OBJ-009, OBJ-010, OBJ-013) need to import from known paths. Stubs prevent import resolution errors during incremental development. Each stub clearly marks which objective owns it via a TODO comment.

### D-07: src/page/ as Plain JS with esbuild
**Choice:** `src/page/` files are authored as JavaScript (not TypeScript) and bundled with esbuild.
**Rationale:** These files run in headless Chromium's V8, not in Node.js. TypeScript would require a separate tsconfig targeting browser globals (`window`, `document`, `WebGLRenderingContext`). Plain JS with JSDoc type annotations keeps the build simple. esbuild bundles Three.js into the output so the Chromium page doesn't need network access to load dependencies. If a downstream objective finds this insufficient, it can introduce a browser-targeted tsconfig — but that's out of scope for scaffolding.

### D-08: Declaration Files for Library API
**Choice:** `declaration: true` in tsconfig to generate `.d.ts` files.
**Rationale:** The seed requires "an importable library for programmatic use." TypeScript declarations enable type-safe consumption by external projects or the n8n integration layer.

## Acceptance Criteria

- [ ] **AC-01:** Running `npm install` in the project root succeeds with zero errors and installs exactly the dependencies listed in the contract above (no unlisted runtime dependencies).
- [ ] **AC-02:** Running `npm run build` succeeds, producing `dist/` with compiled Node.js modules and a bundled `dist/page/` directory.
- [ ] **AC-03:** Running `npm run typecheck` succeeds with zero TypeScript errors on the stub files.
- [ ] **AC-04:** Running `npm test` executes vitest and reports zero failures (stub test file with at least one trivial assertion to confirm the test runner works).
- [ ] **AC-05:** The directory structure matches Section 4.5 of the seed, including all subdirectories and stub files.
- [ ] **AC-06:** Every stub file in `src/` contains a TODO comment referencing the objective that owns it.
- [ ] **AC-07:** `dist/cli.js` is executable (`#!/usr/bin/env node` shebang or equivalent), and running `node dist/cli.js --help` prints a help message (from Commander stub).
- [ ] **AC-08:** `dist/index.js` is importable as an ES module (`import {} from 'depthkit'` resolves).
- [ ] **AC-09:** All runtime dependencies satisfy C-01: Three.js (MIT), Puppeteer (Apache-2.0), ffmpeg-static (LGPL/GPL via stdio), Zod (MIT), Commander (MIT). No other runtime dependencies with restrictive licenses.
- [ ] **AC-10:** `.gitignore` excludes `node_modules/`, `dist/`, and `assets/` (runtime-generated content).
- [ ] **AC-11:** The `engines` field in package.json specifies `node >= 18.0.0`.
- [ ] **AC-12:** `src/page/scene-renderer.js` (browser stub) is successfully bundled by esbuild with Three.js as a dependency, producing `dist/page/scene-renderer.js`.

## Edge Cases and Error Handling

1. **Missing FFmpeg:** If `ffmpeg-static` fails to install (e.g., unsupported platform), the project should still install. The FFmpeg resolution logic (in OBJ-012, not here) will handle the fallback. For scaffolding, the dependency is declared; its runtime resolution is a downstream concern.

2. **Node.js version mismatch:** If a user runs `npm install` on Node <18, npm should warn via the `engines` field. The build should not silently produce broken output.

3. **Platform-specific puppeteer issues:** Puppeteer downloads a Chromium binary on install. On some CI/Docker environments this fails. The scaffolding should include a `.npmrc` or environment guidance noting `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true` as an option (with the expectation that the Docker image provides Chromium). This is documentation, not code.

4. **esbuild bundling Three.js:** Three.js is large (~1MB bundled). The esbuild bundle for `dist/page/` will be substantial. This is acceptable — it loads into a local headless Chromium instance, not a remote browser. No tree-shaking optimization is required for V1 (per AP-05: no premature optimization).

5. **Empty stub imports:** If a downstream objective tries to import a specific named export from a stub that only has `export {}`, TypeScript will error. This is **intentional** — it forces the implementing objective to populate the stub before downstream consumers can build against it. The stubs exist to establish path conventions, not to provide mock implementations.

## Test Strategy

OBJ-001's tests verify the scaffolding itself, not application logic:

1. **Smoke test (automated):** A single vitest test file (`test/unit/scaffold.test.ts`) that:
   - Confirms `import('depthkit')` resolves without error.
   - Confirms the CLI entry point exists at the expected path.
   - This test validates AC-04.

2. **Build verification (CI):** The `npm run build` command is the primary test. If it succeeds, the TypeScript config, esbuild config, and dependency graph are correct.

3. **License audit (manual or scripted):** Run `npx license-checker --summary` and verify no runtime dependency carries a license outside the C-01 allowlist (MIT, Apache-2.0, ISC, BSD-2-Clause, BSD-3-Clause, LGPL/GPL for ffmpeg-static only).

**Relevant testable claims:** None directly — OBJ-001 is infrastructure. But it enables TC-06 (deterministic output), TC-11 (Docker software WebGL), and all other claims by providing the project container.

## Integration Points

### Depends on
Nothing — Tier 0 foundational objective.

### Consumed by (blocked objectives)
- **OBJ-004** (Manifest schema + Zod validation) — imports from `src/manifest/schema.ts`, `src/manifest/loader.ts`. Needs Zod as a dependency.
- **OBJ-009** (Puppeteer bridge) — imports from `src/engine/puppeteer-bridge.ts`. Needs Puppeteer as a dependency. Needs `src/page/` directory and HTML shell.
- **OBJ-010** (Frame clock / virtualized timing) — imports from `src/engine/frame-clock.ts`.
- **OBJ-013** (CLI interface) — imports from `src/cli.ts`. Needs Commander as a dependency.

### File Placement
All files listed in the Directory Structure section above. The implementer creates the full tree with stubs.

## Open Questions

1. **Three.js version pinning:** Should the spec pin a specific Three.js version (e.g., `^0.170.0`) or use latest? Three.js has no semver stability guarantees — minor versions can break APIs. **Recommendation:** Pin to a specific minor version and document it. The implementer should choose the current stable release at implementation time.

2. **Monorepo potential:** The seed mentions an n8n HTTP wrapper as a separate concern. Should the project use a monorepo (e.g., npm workspaces) to house both the engine and the HTTP wrapper? **Recommendation:** No — keep OBJ-001 as a single package. The HTTP wrapper (OBJ-046+) can be a separate package that depends on `depthkit`. This avoids over-engineering the scaffolding.

3. **`src/page/` TypeScript option:** Decision D-07 chose plain JS for browser files. If downstream objectives find this limiting (e.g., they want type-safe geometry definitions shared between Node and browser), they can introduce a `tsconfig.browser.json`. OBJ-001 should not block this but does not need to implement it.

---

I believe this covers the full scope of OBJ-001. I'd like the Challenger to verify that:
- The dependency list is complete and C-01 compliant
- The build pipeline split (tsc for Node, esbuild for browser) is sound
- The stub file strategy is sufficient for downstream objectives
- No acceptance criteria are missing

---

## Round 2 — spec_challenger

## Challenger Review — Round 2

The proposal is solid overall. The directory structure, dependency list, and build pipeline split are well-reasoned. I'll go through my checklist systematically.

### Points of Agreement (Approved)

- **D-01 (ESM):** Sound choice, well-justified.
- **D-02 (esbuild):** Correct — lightweight, no licensing concern, devDep only.
- **D-03 (Vitest):** Good fit for ESM projects.
- **D-05 (Node ≥18):** Reasonable baseline.
- **D-08 (Declaration files):** Needed for library consumers per seed.
- **C-01 compliance:** The dependency list is correct. All runtime deps are on the seed's allowlist.
- **Stub file strategy (D-06):** Smart approach for incremental development.
- **Edge case #5 (empty stub imports):** Intentional breakage on missing exports is the right call.

### Issues

---

**Issue 1: `src/page/index.html` is missing from the stub file list**

**Severity:** Major

The directory structure lists `src/page/index.html` as a file (owned by OBJ-009), but the spec only discusses JavaScript stubs. The HTML shell is the entry point that Puppeteer loads. If it doesn't exist, OBJ-009 can't even start work without first creating the file structure that OBJ-001 is supposed to provide.

**Fix:** Add `src/page/index.html` to the stub file list explicitly. It should be a minimal valid HTML file with an empty `<canvas>` element and a `<script>` tag pointing to the bundled scene-renderer. Add a TODO comment referencing OBJ-009. Add it to AC-05's scope.

---

**Issue 2: The `build:page` esbuild command is underspecified for Three.js bundling**

**Severity:** Major

The spec says esbuild bundles `src/page/scene-renderer.js` with Three.js. But the stub `scene-renderer.js` is empty — it doesn't import Three.js yet. The esbuild command won't bundle Three.js unless there's an actual import statement.

This creates a bootstrapping problem: AC-12 says the stub "is successfully bundled by esbuild with Three.js as a dependency," but an empty stub with no imports will trivially pass bundling. That makes AC-12 vacuous.

**Fix:** The stub `scene-renderer.js` should contain at minimum `import * as THREE from 'three';` (and then discard/noop it) so that the esbuild bundle actually exercises Three.js resolution. Revise AC-12 to: "The esbuild bundle of `src/page/scene-renderer.js` produces a `dist/page/scene-renderer.js` file that includes Three.js code (file size > 500KB confirms Three.js was bundled)." This makes the criterion non-vacuous.

---

**Issue 3: esbuild `format` and `platform` not specified**

**Severity:** Major

The esbuild command is sketched as `esbuild src/page/scene-renderer.js --bundle --outdir=dist/page` but doesn't specify `--format=iife` (or `esm`) and `--platform=browser`. Without these, esbuild defaults to `iife` for bundled output, which is probably correct, but the implementer shouldn't have to guess.

**Fix:** Specify the esbuild flags: `--bundle --format=iife --platform=browser --outdir=dist/page`. Document the rationale: IIFE because the script is loaded via a `<script>` tag in headless Chromium, not imported as a module.

---

**Issue 4: No specification for how `src/page/` files reference each other**

**Severity:** Minor

The seed's directory structure shows three JS files in `src/page/`: `scene-renderer.js`, `geometry-library.js`, and `message-handler.js`. Are these bundled as a single entry point, or separately? If `scene-renderer.js` imports the other two, esbuild bundles them together from a single entry. If they're separate entry points, esbuild needs multiple entries.

**Fix:** Specify that `scene-renderer.js` is the single entry point for esbuild bundling, and that `geometry-library.js` and `message-handler.js` are imported by it (bundled into the single output). This matches the seed's architecture where the Chromium page loads one script. Add this to D-07.

---

**Issue 5: `assets/` gitignore vs. seed expectation**

**Severity:** Minor

AC-10 says `.gitignore` excludes `assets/`. But the seed describes `assets/` as "Per-video generated images and audio" — runtime content. However, some downstream objectives (like integration tests in OBJ-035+) may want to commit small test fixtures under `assets/` or a `test/fixtures/` directory.

**Fix:** Gitignore `assets/` but explicitly create a `test/fixtures/` directory (with a `.gitkeep`) for test assets. Downstream integration tests place their test images/audio there, not in `assets/`. Clarify this in the directory structure.

---

**Issue 6: Missing `.npmrc` or Puppeteer environment guidance**

**Severity:** Minor

Edge case #3 mentions noting `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true` as guidance, but doesn't specify where this documentation goes. "This is documentation, not code" — but documentation needs a location.

**Fix:** Create a `README.md` stub that includes a "Prerequisites" section with the Puppeteer/Chromium note and the `FFMPEG_PATH` environment variable. Add AC for its existence.

---

**Issue 7: The `clean` script behavior isn't specified**

**Severity:** Minor

The scripts contract lists `clean: string` but doesn't say what it removes. Just `dist/`? What about `node_modules/.cache`?

**Fix:** Specify: `clean` removes `dist/` only. Simple `rm -rf dist` (or `rimraf dist` if cross-platform is needed). If cross-platform is needed, add `rimraf` as a devDependency. Otherwise, document that the project assumes Unix-like environments (which is reasonable given C-08's VPS target and C-11's Docker target).

---

**Issue 8: No `@types/three` version coupling note**

**Severity:** Minor

Three.js types (`@types/three`) must match the Three.js version exactly — a mismatch produces type errors. The spec lists both as devDependencies/dependencies but doesn't note this coupling.

**Fix:** Add a note in the Open Questions or Design Decisions: "`@types/three` version must match the installed `three` version. Pin them together." Actually, since Three.js v0.160+, types are bundled with the main package. If the implementer uses a recent version, `@types/three` may be unnecessary. **Revised fix:** Note in D-07 or Open Questions that if the chosen Three.js version bundles its own types, `@types/three` can be dropped from devDependencies. The implementer should verify at implementation time.

---

### Summary of Required Fixes

**Critical:** None.

**Major (must fix before convergence):**
1. Add `src/page/index.html` stub
2. Make AC-12 non-vacuous (Three.js import in stub + file size check)
3. Specify esbuild `--format`, `--platform` flags

**Minor (can be documented as notes/open questions):**
4. Clarify single entry point bundling for `src/page/`
5. Add `test/fixtures/` directory, clarify `assets/` gitignore intent
6. Specify where Puppeteer/env documentation lives (README stub)
7. Specify `clean` script behavior
8. Note `@types/three` version coupling

I need the three major issues addressed before I'll converge. The minor issues can be folded in as notes if you prefer, but the majors are non-negotiable — they'd each cause an implementer to stop and make an unguided decision.

---

## Round 3 — spec_author

# Revised Specification: OBJ-001 — Project Scaffolding and Build System

All three major issues and all five minor issues from Round 2 are addressed below. I'll flag each fix inline so the Challenger can verify.

---

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

1. **`src/page/` files are plain JavaScript**, bundled by esbuild for headless Chromium. `scene-renderer.js` is the **single entry point** — it imports `geometry-library.js` and `message-handler.js`, and esbuild bundles all three (plus Three.js) into one output file at `dist/page/scene-renderer.js`. **(Fix for Issue 4)**

2. **`src/page/index.html`** is a minimal valid HTML stub: `<!DOCTYPE html>`, `<html>`, `<body>`, a `<canvas id="depthkit-canvas">` element, and a `<script src="scene-renderer.js"></script>` tag. Contains a TODO comment referencing OBJ-009. **(Fix for Issue 1)**

3. **`src/index.ts`** — the library entry point that re-exports the public API for programmatic use.

4. **`test/fixtures/`** — committed directory (with `.gitkeep`) for test images/audio used by integration tests. Distinct from `assets/` which is gitignored runtime content. **(Fix for Issue 5)**

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
    "build:page": string;       // esbuild with flags specified in D-02
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

**Note on `@types/three`:** Three.js v0.160+ bundles its own TypeScript declarations. If the implementer selects a version ≥0.160, `@types/three` is unnecessary and should be omitted. If an older version is chosen, `@types/three` must be added to devDependencies **at the same version** as the `three` package. The implementer must verify this at implementation time. **(Fix for Issue 8)**

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

**esbuild command specification:** **(Fix for Issue 3)**
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

`src/page/scene-renderer.js` — the esbuild entry point — must contain a Three.js import to validate bundling: **(Fix for Issue 2)**
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

**HTML stub** (`src/page/index.html`): **(Fix for Issue 1)**
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

### README.md Stub **(Fix for Issue 6)**

A `README.md` at the project root with the following sections:

- **Overview** — one paragraph describing depthkit.
- **Prerequisites** — Node.js ≥18, and notes:
  - Puppeteer downloads Chromium on `npm install`. In Docker/CI, set `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true` and ensure Chromium is available in the image.
  - FFmpeg: bundled via `ffmpeg-static`. To use a system-installed FFmpeg instead, set `FFMPEG_PATH=/path/to/ffmpeg`.
- **Quick Start** — `npm install`, `npm run build`, `npx depthkit --help`.
- **Development** — `npm run dev`, `npm test`.
- All sections are stubs with TODO markers for expansion by later objectives.

## Design Decisions

### D-01: ESM over CommonJS
**Choice:** `"type": "module"` with ESM imports throughout.
**Rationale:** Three.js v0.150+ ships ESM-first. Puppeteer supports ESM. Modern Node.js (≥18) has stable ESM support. Avoids dual-module complexity.

### D-02: esbuild for Browser Bundle
**Choice:** esbuild for bundling `src/page/` into a browser-ready IIFE script.
**Rationale:** `src/page/` files run inside headless Chromium and need Three.js bundled in. esbuild is zero-config, fast, and MIT licensed. Alternatives: webpack (too heavy), rollup (viable but more config). esbuild is a devDependency only.
**Flags:** `--bundle --format=iife --platform=browser --outdir=dist/page`. IIFE because the script loads via `<script>` tag, not as an ES module. **(Fix for Issue 3)**

### D-03: Vitest over Jest
**Choice:** Vitest as the test runner.
**Rationale:** Native ESM support without transform hacks. Fast. Compatible with `"type": "module"`.

### D-04: ffmpeg-static as Default, System FFmpeg as Fallback
**Choice:** `ffmpeg-static` in dependencies; `FFMPEG_PATH` env var for override.
**Rationale:** Out-of-the-box experience. Docker/CI environments can skip the bundled binary. Satisfies C-01 allowance.

### D-05: Node.js ≥18 Baseline
**Choice:** `engines.node >= 18.0.0`.
**Rationale:** Stable ESM, `fetch`, `crypto.randomUUID()`. VPS deployment (C-08) allows version control.

### D-06: Stub Files for All Planned Modules
**Choice:** Syntactically valid stubs for every module, with TODO + objective ID.
**Rationale:** Downstream objectives import from known paths immediately. Empty stubs that only `export {}` intentionally break if a consumer tries to import a named export — forcing the implementing objective to populate the stub first.

### D-07: src/page/ as Plain JS with Single Entry Point
**Choice:** `src/page/` files are authored as JavaScript. `scene-renderer.js` is the **single esbuild entry point** that imports `geometry-library.js` and `message-handler.js`. esbuild bundles all three plus Three.js into one output file.
**Rationale:** These files run in Chromium's V8, not Node.js. Plain JS with a single entry point keeps the build simple. If downstream objectives need shared TypeScript types between Node and browser, they can introduce a `tsconfig.browser.json` — that's out of OBJ-001's scope. **(Fix for Issue 4)**

### D-08: Declaration Files for Library API
**Choice:** `declaration: true` in tsconfig.
**Rationale:** The seed requires "an importable library for programmatic use." `.d.ts` files enable type-safe consumption.

### D-09: Unix-Assumed Clean Script **(Fix for Issue 7)**
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
- [ ] **AC-12:** The esbuild bundle at `dist/page/scene-renderer.js` includes Three.js code. Verified by: the file exists AND its size is >500KB (Three.js alone is ~1MB when bundled). **(Fix for Issue 2)**
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

1. **Three.js version pinning:** Three.js has no semver stability guarantees. **Recommendation:** Pin to a specific minor version (e.g., `"three": "0.170.0"` — not `^0.170.0`). The implementer chooses the current stable release at implementation time. If the chosen version is ≥0.160, `@types/three` is unnecessary (types are bundled). If <0.160, add `@types/three` at the matching version.

2. **Monorepo potential:** The n8n HTTP wrapper (OBJ-046+) could be a separate package. **Decision:** OBJ-001 is a single package. Monorepo structure is out of scope. The HTTP wrapper depends on `depthkit` as an external package.

3. **`src/page/` TypeScript option:** If downstream objectives need type-safe geometry definitions shared between Node and browser, they can introduce a `tsconfig.browser.json`. OBJ-001 does not block this but does not implement it.

---

I believe all three major issues and all five minor issues from Round 2 are now addressed:

| Issue | Severity | Fix Location |
|-------|----------|-------------|
| 1. Missing `index.html` stub | Major | Directory Structure, Stub Files section |
| 2. Vacuous AC-12 | Major | Stub Files (`scene-renderer.js` imports THREE), AC-12 revised with 500KB check |
| 3. esbuild flags unspecified | Major | Build Pipeline Contract, D-02 |
| 4. Single entry point not clarified | Minor | D-07, Directory Structure note |
| 5. `test/fixtures/` + `assets/` gitignore | Minor | Directory Structure, AC-10 |
| 6. README/documentation location | Minor | README.md Stub section, AC-13 |
| 7. `clean` script behavior | Minor | D-09 |
| 8. `@types/three` coupling | Minor | Note under package.json contract, Open Question 1 |

Challenger — does this address all your concerns? Ready to verify and approve?

---

## Round 4 — spec_challenger

## Challenger Verification — Round 4

I've systematically verified every fix against my Round 2 objections.

| Issue | Verdict | Verification |
|-------|---------|-------------|
| 1. Missing `index.html` stub | ✅ Fixed | Present in directory structure, full HTML stub content provided, AC-05 scope updated |
| 2. Vacuous AC-12 | ✅ Fixed | `scene-renderer.js` stub imports `THREE`, AC-12 specifies >500KB file size check |
| 3. esbuild flags | ✅ Fixed | `--bundle --format=iife --platform=browser --outdir=dist/page` in Build Pipeline Contract and D-02 |
| 4. Single entry point | ✅ Fixed | D-07 and directory structure note clarify `scene-renderer.js` as sole entry |
| 5. `test/fixtures/` | ✅ Fixed | Directory structure includes it with `.gitkeep`, AC-10 explicitly excludes it from gitignore |
| 6. README location | ✅ Fixed | README.md stub section with prerequisites content, AC-13 added |
| 7. `clean` script | ✅ Fixed | D-09 specifies `rm -rf dist`, rationale for no cross-platform wrapper |
| 8. `@types/three` | ✅ Fixed | Note under package.json contract, Open Question 1 |

No new issues introduced by the revision. The spec is complete and implementable.

CONCLUSION:

The specification for OBJ-001 is agreed. It defines the depthkit project scaffolding: directory structure per seed §4.5, package.json with C-01-compliant dependencies (three, puppeteer, ffmpeg-static, zod, commander), TypeScript config with ESM modules, a split build pipeline (tsc for Node.js, esbuild IIFE bundle for browser-side `src/page/`), stub files for all planned modules with objective ownership markers, and 13 testable acceptance criteria. Key design decisions: ESM-first (D-01), esbuild for browser bundle (D-02), Vitest (D-03), single entry point for page bundle (D-07), Unix-assumed clean script (D-09).

Let me write the final spec and update meta.json.
[Tool: ToolSearch]
  Input: {
  "query": "select:Write,Read",
  "max_results": 2
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Write'}, {'type': 'tool_reference', 'tool_name': 'Read'}]


Let me first check the current state of the node directory and meta.json.
[Tool: Read]
  Input: {
  "file_path": "/home/user/depthkit/nodes/OBJ-001/meta.json"
}
[Tool Error] File does not exist. Note: your current working directory is /Users/austin/spatial_reasoning_video_generator/generations/depthkit.

[Tool: ToolSearch]
  Input: {
  "query": "select:Bash",
  "max_results": 1
}
[Tool Result] [{'type': 'tool_reference', 'tool_name': 'Bash'}]

[Tool: Bash]
  Input: {
  "command": "ls -la nodes/OBJ-001/ 2>/dev/null || echo \"Directory does not exist\"",
  "description": "Check if OBJ-001 node directory exists"
}

[Tool: Bash]
  Input: {
  "command": "pwd",
  "description": "Show current working directory"
}
[Tool Result] /Users/austin/spatial_reasoning_video_generator/generations/depthkit
[Tool Result] total 8
drwxr-xr-x   3 austin  staff    96 Mar 22 19:15 .
drwxr-xr-x  85 austin  staff  2720 Mar 22 19:15 ..
-rw-r--r--   1 austin  staff   581 Mar 22 19:15 meta.json

[Tool: Read]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-001/meta.json"
}
[Tool Result]      1→{
     2→  "id": "OBJ-001",
     3→  "description": "Project scaffolding and build system -- package.json, tsconfig, directory layout per Section 4.5, dependency list satisfying C-01 (zero-license). Establishes the Node.js project container with Three.js, Puppeteer, FFmpeg, Zod, and Commander as allowed dependencies.",
     4→  "category": "engine",
     5→  "created_by_session": "initializer",
     6→  "created_at": "2026-03-22T00:00:00Z",
     7→  "updated_at": "2026-03-22T00:00:00Z",
     8→  "depends_on": [],
     9→  "visual_status": null,
    10→  "tuning_rounds": 0,
    11→  "notes": "Tier 0 foundation. No dependencies. Covers C-01."
    12→}
    13→
Good. Now let me write the final spec and update the meta.json.
[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-001/output.md",
  "content": "# Specification: OBJ-001 \u2014 Project Scaffolding and Build System\n\n## Summary\n\nOBJ-001 establishes the depthkit Node.js project container: directory structure, package.json with all allowed dependencies, TypeScript configuration, and build pipeline. This is the Tier 0 foundation that every other objective imports from. It must satisfy C-01 (zero-license) by including only the explicitly allowed dependencies, and it must mirror the directory layout from seed Section 4.5 so that downstream objectives know exactly where to place their implementations.\n\n## Interface Contract\n\nOBJ-001 does not export runtime code. It exports **project structure** and **build tooling** that all subsequent objectives depend on. The contract is the file tree, the build commands, and the dependency manifest.\n\n### Directory Structure\n\n```\ndepthkit/\n\u251c\u2500\u2500 src/\n\u2502   \u251c\u2500\u2500 cli.ts                          # CLI entry point (OBJ-013)\n\u2502   \u251c\u2500\u2500 index.ts                        # Library entry point \u2014 re-exports public API\n\u2502   \u251c\u2500\u2500 engine/\n\u2502   \u2502   \u251c\u2500\u2500 orchestrator.ts             # (OBJ-035) Main render loop\n\u2502   \u2502   \u251c\u2500\u2500 puppeteer-bridge.ts         # (OBJ-009) Puppeteer launch, frame capture\n\u2502   \u2502   \u251c\u2500\u2500 ffmpeg-encoder.ts           # (OBJ-012) FFmpeg child process\n\u2502   \u2502   \u2514\u2500\u2500 frame-clock.ts             # (OBJ-010) Virtualized clock\n\u2502   \u251c\u2500\u2500 scenes/\n\u2502   \u2502   \u251c\u2500\u2500 scene-sequencer.ts          # (OBJ-015) Scene routing + transitions\n\u2502   \u2502   \u251c\u2500\u2500 geometries/\n\u2502   \u2502   \u2502   \u251c\u2500\u2500 index.ts                # Geometry registry\n\u2502   \u2502   \u2502   \u2514\u2500\u2500 [geometry].ts           # (OBJ
... [truncated]
[Tool Result] File created successfully at: /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-001/output.md

[Tool: Write]
  Input: {
  "file_path": "/Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-001/meta.json",
  "content": "{\n  \"id\": \"OBJ-001\",\n  \"description\": \"Project scaffolding and build system -- package.json, tsconfig, directory layout per Section 4.5, dependency list satisfying C-01 (zero-license). Establishes the Node.js project container with Three.js, Puppeteer, FFmpeg, Zod, and Commander as allowed dependencies.\",\n  \"category\": \"engine\",\n  \"created_by_session\": \"initializer\",\n  \"created_at\": \"2026-03-22T00:00:00Z\",\n  \"updated_at\": \"2026-03-22T23:45:00Z\",\n  \"depends_on\": [],\n  \"visual_status\": null,\n  \"tuning_rounds\": 0,\n  \"notes\": \"Tier 0 foundation. No dependencies. Covers C-01. Spec completed via 4-round deliberation.\",\n  \"spec_status\": \"complete\"\n}\n"
}
[Tool Result] The file /Users/austin/spatial_reasoning_video_generator/generations/depthkit/nodes/OBJ-001/meta.json has been updated successfully.
Now let me commit:
[Tool: Bash]
  Input: {
  "command": "git status",
  "description": "Show working tree status"
}
[Tool Result] On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   frontier.json
	modified:   index.json
	modified:   nodes/OBJ-001/meta.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.claude_settings.json
	feed.md
	nodes/OBJ-001/output.md
	nodes/OBJ-003/transcript.md
	sessions/

no changes added to commit (use "git add" and/or "git commit -a")

[Tool: Bash]
  Input: {
  "command": "git log --oneline -5",
  "description": "Show recent commits"
}
[Tool Result] fb3e4b3 spec(OBJ-003): Coordinate system and spatial math reference
76f7b6b Initialize DAG decomposition: 83 objectives across 7 dependency tiers
f5f8c11 Initial project setup

[Tool: Bash]
  Input: {
  "command": "git add nodes/OBJ-001/output.md nodes/OBJ-001/meta.json && git commit -m \"$(cat <<'EOF'\nspec(OBJ-001): Project scaffolding and build system specification\n\nDefines directory layout, package.json contract (C-01 compliant deps),\ntsconfig, split build pipeline (tsc for Node + esbuild IIFE for browser),\nstub files for all planned modules, and 13 acceptance criteria.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n)\"",
  "description": "Commit OBJ-001 spec output and updated meta"
}
[Tool Result] [master 28fe944] spec(OBJ-001): Project scaffolding and build system specification
 2 files changed, 367 insertions(+), 2 deletions(-)
 create mode 100644 nodes/OBJ-001/output.md
The OBJ-001 specification has been finalized and committed. 

**Summary of what was agreed:**

- **Directory structure** mirroring seed §4.5 with all subdirectories and stub files
- **5 runtime dependencies** (three, puppeteer, ffmpeg-static, zod, commander) — all C-01 compliant
- **Split build pipeline**: `tsc` for Node.js modules, `esbuild --bundle --format=iife --platform=browser` for the Chromium-side page bundle
- **ESM throughout** (`"type": "module"`)
- **Stub files** for every planned module with TODO + objective ID ownership markers
- **`src/page/scene-renderer.js`** as the single esbuild entry point, importing Three.js to validate bundling (AC-12: >500KB size check)
- **`src/page/index.html`** stub with canvas element for Puppeteer
- **13 acceptance criteria** covering install, build, typecheck, test, CLI output, bundle validation, license audit, and documentation
- **3 open questions** documented (Three.js version pinning, monorepo potential, page TypeScript option)
