# can-migrate-es-toolkit — `rjsf-team/react-jsonschema-form`

```
/can-migrate-es-toolkit https://github.com/rjsf-team/react-jsonschema-form en
```

**Analyzed:** 2026-08-09 · **Repo state:** `main` @ 6.7.1 · **Verdict: 78 / 100 — Recommended**

---

## Stage 1 — Migration Gate

19 `package.json` files scanned (pnpm + Nx monorepo). lodash found in 9 of them.

| Package                    | lodash          | lodash-es | Location          |
| -------------------------- | --------------- | --------- | ----------------- |
| `@rjsf/core`               | ✅              | ✅        | `dependencies`    |
| `@rjsf/utils`              | ✅              | ✅        | `dependencies`    |
| `@rjsf/validator-ajv8`     | ✅              | ✅        | `dependencies`    |
| `@rjsf/validator-ata`      | ✅              | ✅        | `dependencies`    |
| `@rjsf/validator-cfworker` | ✅              | ✅        | `dependencies`    |
| `@rjsf/antd`               | ✅              | ✅        | `dependencies`    |
| `@rjsf/shadcn`             | ✅              | ✅        | `dependencies`    |
| `@rjsf/semantic-ui`        | ✅              | —         | `dependencies`    |
| `@rjsf/playground`         | ✅              | —         | `dependencies`    |
| root                       | `@types/lodash` | —         | `devDependencies` |

**→ Proceed to Stage 2.**

---

## Stage 2 — Migration Target

### 2-1. Project character

Published **library monorepo** — 18 npm packages under the `@rjsf/*` scope, Apache-2.0, React JSON Schema form builder with a pluggable theme architecture (antd, MUI, Chakra, shadcn, Semantic UI, …).

Every package declares `main` / `module` / `exports` / `files: ["dist", "lib", "src"]` — everything ships to npm.

**Plugin exposure: no.** Themes consume `@rjsf/utils` through its own exported API. No lodash instance or lodash type leaks into the public API surface, so no compatibility shim is required.

### 2-2. Is lodash in the shipped bundle?

**Yes — `dependencies`, not `devDependencies`, in all 9 packages.** Every `@rjsf/*` install pulls lodash.

Notable build detail: the repo maintains a custom `tsc-alias` replacer to make lodash work in both module systems.

```ts
// tsc-alias-replacer/lodashReplacer.ts
export default function lodashReplacer({
  orig,
}: AliasReplacerArguments): string {
  if (orig.startsWith("from 'lodash/")) {
    const origLodashEs = orig
      .substring(0, orig.length - 1)
      .replace("lodash/", "lodash-es/");
    return `${origLodashEs}.js'`;
  }
  return orig;
}
```

Source is written against `lodash/*`; the ESM build rewrites it to `lodash-es/*.js`. This is why 7 packages carry **both** `lodash` and `lodash-es`, plus a `compileReplacer` build step and a `tsconfig.replacer.json` per package. es-toolkit ships dual ESM/CJS with types out of the box, so this entire plumbing layer becomes deletable.

**Transitive lodash (stays after migration):** 20 packages in `pnpm-lock.yaml` still depend on lodash.

- Dev-only: `@docusaurus/*` (docs site), `html-webpack-plugin`, `caniuse-api`, `@babel/helper-define-polyfill-provider`
- **Shipped:** `semantic-ui-react` (→ `@rjsf/semantic-ui`), `@fluentui/*` (→ `@rjsf/fluentui-rc`)

So `core` / `utils` / `validator-*` become fully lodash-free; the Semantic UI and Fluent UI themes keep lodash via their upstream UI libraries. Not a blocker — just an honest ceiling on the claim.

### 2-3. Import patterns & scope

| Pattern                                       | Count   | Bundle impact                   |
| --------------------------------------------- | ------- | ------------------------------- |
| Full import (`import _ from 'lodash'`)        | 1       | Test file only                  |
| Named import (`import { get } from 'lodash'`) | 4       | 3 test files, 1 playground file |
| **Subpath (`import get from 'lodash/get'`)**  | **179** | Already per-function optimized  |

**184 imports across 101 files** (63 in `src/`, 38 in `test/`).

| Package                             | Files  |
| ----------------------------------- | ------ |
| `utils`                             | 58     |
| `core`                              | 18     |
| `validator-ata`                     | 7      |
| `validator-ajv8`                    | 6      |
| `validator-cfworker` / `playground` | 3 each |
| `shadcn` / `semantic-ui` / `antd`   | 2 each |

Top functions: `get` (40), `noop` (28), `isObject` (14), `isEmpty` (14), `set` (10), `has` (10), `cloneDeep` (8), `isString` (7).

38 distinct functions in `src/`. **All 38 exist in `es-toolkit/compat`** (verified by runtime `typeof` check).

> **Note on benefit size:** subpath imports dominate, so lodash is _already_ tree-shaken here. The upside is therefore smaller than a typical `import _ from 'lodash'` codebase — the win is per-function byte size, dependency-graph simplification, and build-config deletion, not "we accidentally shipped 70 kB of lodash."

### 2-4. Hard blockers

`sortedUniq`, `sortedUniqBy`, `mixin`, `noConflict`, `runInContext` — **none present.** No `lodash/fp` usage either.

### Stage 2 summary

```
Repository: rjsf-team/react-jsonschema-form
2-1 (Character): Published library monorepo (18 pkgs) — Plugin exposure: no
2-2 (Bundle):    Shipped (dependencies) — Transitive lodash: semantic-ui-react, @fluentui/*, docusaurus (dev)
2-3 (Imports):   Full ×1 / Named ×4 / Subpath ×179 — Files: 101 — Top: get, noop, isObject, isEmpty, set
2-4 (Blockers):  None

Stage 2 verdict: Migration candidate
```

---

## Stage 3 — Organizational Signals

| Signal                   | Finding                                                                                                                                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity**             | Very active. Commits on 2026-08-09, 08-08, 08-07, 08-03… Multiple external contributors merged in the last two weeks (#5171, #5174, #5175, #5159).                                                         |
| **Release cadence**      | 6.7.1 released 2026-07-24. Dependabot enabled and merging.                                                                                                                                                 |
| **Prior art**            | GitHub search for `es-toolkit` in this repo → **0 results**. Only lodash-related items are dependabot bumps (#5020, #5018, lodash 4.17.23 → 4.18.1). No failed prior attempt to respect or explain around. |
| **CLA**                  | **None.** `CONTRIBUTING.md` has no CLA language; no CLA bot in `.github/`. Low contributor friction.                                                                                                       |
| **Issue hygiene**        | `stale.yml` with a 456-day window — patient maintainers, issues aren't auto-closed quickly.                                                                                                                |
| **lodash in public API** | No. Internal use only.                                                                                                                                                                                     |

Healthy, actively maintained, receptive to outside PRs, no legal paperwork. Good conditions for a proposal.

---

## Stage 4 — Verification & Measurement

No `benchmark` / `bench` / `perf` script exists anywhere in the monorepo, so the skill's benchmark path does not apply. Substituted with two things that matter more for a published library: **does it actually still work**, and **how many bytes do consumers save**.

### 4-1. Applied migration

`scripts/migrate_lodash_imports.py` dry-run → 184 replacements, 101 files, 0 blockers. Applied with `--write`, then `lodash` + `lodash-es` swapped for `es-toolkit` in all 9 package manifests.

**Three manual fixes were needed after the automated pass** (see [Known issues](#known-issues-in-the-bundled-script) — two are script bugs):

1. `import get from 'lodash/get'` → the script emitted `import get from 'es-toolkit/compat'`, a **default** import. `es-toolkit/compat` has no matching default export, so every call site silently received the whole namespace object. 97 files affected. Correct form is `import { get } from 'es-toolkit/compat'`.
2. Aliased imports (`import _get from 'lodash/get'`, 7 in `Form.tsx`) need `import { get as _get } from 'es-toolkit/compat'`. 3 files affected.
3. `packages/utils/test/getTestIds.test.ts` mocks `vi.mock('lodash/uniqueId')`. Test-harness path, has to be retargeted at the named export — a hand edit in any migration, not an es-toolkit defect.

### 4-2. Test results

Baseline `@rjsf/utils`: **79 files / 1440 tests passed.**

| Stage                   | Result                                                                                                                                         |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| After raw script output | 30 files failed, **678 tests failed** — all from the default-import bug (`Maximum call stack size exceeded`, `mockClear is not a function`, …) |
| After fixing imports    | 1 file failed, 6 tests failed — the stale `vi.mock` path only                                                                                  |
| After fixing the mock   | **79 files / 1440 tests passed — identical to baseline**                                                                                       |

Full monorepo:

```
pnpm run build  →  NX  Successfully ran target build for 18 projects
pnpm run test   →  NX  Successfully ran target test for 17 projects
                    9,684 tests passed, 0 failed
```

**No behavioral difference found in any of the 9,684 tests.** No `es-toolkit/compat` incompatibility surfaced anywhere in the suite.

One TypeScript note: `Form.tsx:1042` carries `// @ts-expect-error TS2590` for `_get(schemaValidationErrorSchema, path)` on a deeply recursive `ErrorSchema` type. es-toolkit's `get` reproduces the same TS2590, so the directive stays as-is — same behavior, no new suppression needed.

Diff size: **111 files changed, +234 / −405.**

### 4-3. Bundle size

**(a) Real consumer bundle** — `esbuild --bundle --minify` of `@rjsf/core` + `@rjsf/validator-ajv8` + `@rjsf/utils`, React external, built from the actual `lib/` output before and after.

|                    | minified              | gzip                 |
| ------------------ | --------------------- | -------------------- |
| Before (lodash-es) | 392,823 B             | 131,667 B            |
| After (es-toolkit) | 382,142 B             | 125,604 B            |
| **Delta**          | **−10,681 B (−2.7%)** | **−6,063 B (−4.6%)** |

Modest in percentage terms because AJV dominates this bundle. The absolute saving is the honest number: **~10.4 kB minified / ~5.9 kB gzip off every consumer's bundle.**

**(b) The lodash slice alone** — synthetic bundle of exactly the 38 functions `src/` uses, `lodash-es` subpath imports vs `es-toolkit/compat`.

|                                  | minified               | gzip                  |
| -------------------------------- | ---------------------- | --------------------- |
| `lodash-es` (38 subpath imports) | 31,184 B               | 11,555 B              |
| `es-toolkit/compat`              | 20,721 B               | 6,353 B               |
| **Delta**                        | **−10,463 B (−33.6%)** | **−5,202 B (−45.0%)** |

The two measurements agree (−10,463 vs −10,681 minified), which confirms the saving is genuinely the lodash slice and not build noise.

**(c) Disk footprint — the one regression.** `lodash` 4.9 MB + `lodash-es` 2.6 MB = 7.5 MB, versus `es-toolkit` at 16 MB unpacked (it ships many build formats). `node_modules` gets bigger; shipped bytes get smaller. Worth stating plainly rather than hiding.

---

## Stage 5 — Report

### Score: 78 / 100 — Recommended

**Why it scores high**

- Verified end-to-end: full build (18 projects) and full test suite (**9,684 tests**) green after migration, no behavior change.
- lodash sits in `dependencies` of published packages — every consumer pays for it today.
- Real, measured saving: **~10.4 kB min / ~5.9 kB gzip** off a core+validator+utils bundle; **−45% gzip** on the lodash slice itself.
- Zero hard blockers; all 38 functions covered by `es-toolkit/compat`.
- **Build simplification is arguably the bigger win**: the `lodashReplacer` tsc-alias plugin, 6 × `tsconfig.replacer.json`, 6 × `compileReplacer` script steps, and the dual `lodash` + `lodash-es` dependency pairs all exist _only_ to make lodash work in both module systems. es-toolkit ships dual ESM/CJS with bundled types, so all of it can be deleted.
- Active repo, external PRs merging weekly, **no CLA**, no failed prior attempt to work around.

**Why it isn't 90+**

- **Scope**: 101 files / 184 imports across 9 packages. Mechanical, but a large diff to review, and it touches `@rjsf/core` and `@rjsf/utils` — the two most sensitive packages in the project.
- **Subpath imports already dominate** (179/184). lodash is not being over-shipped today, so the byte win is real but not dramatic — 2.7% of a realistic app bundle.
- **Transitive lodash persists** for `@rjsf/semantic-ui` and `@rjsf/fluentui-rc` via `semantic-ui-react` and `@fluentui/*`. "Removes lodash from rjsf" is only true for `core` / `utils` / `validator-*`.
- **`node_modules` grows** from 7.5 MB to 16 MB unpacked.
- Being a widely used library, maintainers will reasonably weigh a dependency swap against churn risk for downstream users.

**Recommended approach:** split into staged PRs rather than one 101-file change. `@rjsf/utils` first (58 files, the biggest and most self-contained chunk, 100% test coverage as a safety net), then `@rjsf/core`, then the validators, then the themes.

---

## Stage 6 — Draft Issue

> Score ≥ 70 → issue draft included. Written in English (repo's primary language).

---

**Title:** Consider replacing lodash with es-toolkit

Hi rjsf team 👋

I've been looking at the lodash usage across the `@rjsf/*` packages and wanted to share some measurements, in case replacing it with [es-toolkit](https://github.com/toss/es-toolkit) is of interest. Happy to be told this isn't worth the churn — I'd rather ask first than open a 100-file PR unannounced.

### Context

lodash is a runtime `dependency` of 9 published packages (`core`, `utils`, `validator-ajv8`, `validator-ata`, `validator-cfworker`, `antd`, `shadcn`, `semantic-ui`, `playground`), so every consumer installs and bundles it. The code uses 38 distinct lodash functions across 101 files, almost entirely via subpath imports (179 of 184).

### What I measured

I ran the migration locally (`lodash/*` → `es-toolkit/compat`) to check whether it actually holds up:

- `pnpm run build` — **all 18 projects build**
- `pnpm run test` — **all 17 projects pass, 9,684 tests, 0 failures**
- No behavioral difference surfaced anywhere in the suite

Bundle size, `esbuild --bundle --minify` of `@rjsf/core` + `@rjsf/validator-ajv8` + `@rjsf/utils` (React external), built from real `lib/` output:

|            | minified          | gzip             |
| ---------- | ----------------- | ---------------- |
| lodash-es  | 392,823 B         | 131,667 B        |
| es-toolkit | 382,142 B         | 125,604 B        |
| delta      | −10,681 B (−2.7%) | −6,063 B (−4.6%) |

Isolating just the 38 functions actually used: 31,184 → 20,721 B minified (−33.6%), 11,555 → 6,353 B gzip (−45.0%). The two numbers line up, so the saving really is the lodash slice.

### The part I think matters more than bytes

Because lodash's CJS build doesn't work in ESM output, the repo currently maintains:

- `tsc-alias-replacer/lodashReplacer.ts`
- 6 × `tsconfig.replacer.json`
- 6 × `compileReplacer` build steps
- both `lodash` **and** `lodash-es` as dependencies in 7 packages
- `@types/lodash` at the root

es-toolkit ships dual ESM/CJS with bundled TypeScript types, so this whole layer could go away. That felt like a more compelling reason than the byte count.

### Honest caveats

- **lodash won't fully disappear.** `semantic-ui-react` and `@fluentui/*` pull it transitively, so `@rjsf/semantic-ui` and `@rjsf/fluentui-rc` keep it. `core` / `utils` / `validator-*` would become lodash-free.
- **`node_modules` grows**: lodash + lodash-es ≈ 7.5 MB unpacked vs es-toolkit ≈ 16 MB. Shipped bytes shrink, install footprint doesn't.
- **The diff is large**: 111 files, +234/−405. Mechanical, but it touches `core` and `utils`.
- Three spots need hand-editing rather than a codemod: aliased imports in `Form.tsx` (`import _get from 'lodash/get'` → `import { get as _get } from 'es-toolkit/compat'`), and the `vi.mock('lodash/uniqueId')` in `packages/utils/test/getTestIds.test.ts`.
- One thing that stayed identical: the `@ts-expect-error TS2590` at `Form.tsx:1042` is still needed with es-toolkit's `get` — same typing behavior on the recursive `ErrorSchema`.

### Suggested rollout

Rather than one big PR, I'd propose staging it:

1. `@rjsf/utils` (58 files — largest and most self-contained, and it has 100% test coverage as a safety net)
2. `@rjsf/core` (18 files)
3. `validator-ajv8` / `validator-ata` / `validator-cfworker`
4. Theme packages
5. Cleanup: drop `lodashReplacer`, the `tsconfig.replacer.json` files, and `@types/lodash`

Would you be open to this? If so I'm glad to open the first PR against `@rjsf/utils` so you can judge the real diff before committing to the rest. And if you'd rather not add dependency churn right now, that's a completely reasonable answer — thanks either way for the work on this project.
