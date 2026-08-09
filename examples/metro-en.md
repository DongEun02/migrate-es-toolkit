# can-migrate-es-toolkit — `react/metro`

```
/can-migrate-es-toolkit https://github.com/react/metro en
```

**Analyzed:** 2026-08-09 · **Repo state:** `main` @ 0.87.0 (last push 2026-08-08)

## Verdict: 15 / 100 — Do not migrate

**Metro is a Node.js bundler that is never itself bundled, so the byte saving reaches nobody — while es-toolkit adds 3.7 MB to every install.**

**Do not open an issue or PR.** Not "probably not worth it" — there is no case to make. The migration was already proposed as [PR #1534](https://github.com/react/metro/pull/1534) and correctly declined, and every measurement taken since has moved further against it.

The change is trivial and verifies perfectly clean (2,542 tests, Flow, and the full build all green on a 5-file diff). That is not an argument for doing it. A flawless diff of a change with negative net value is still negative.

---

## Stage 1 — Migration Gate

20 `package.json` files scanned (Yarn v1 workspaces). lodash found in 2.

| Package      | Package name     | Location       |
| ------------ | ---------------- | -------------- |
| `metro`      | `lodash.throttle@^4.1.1` | `dependencies` |
| `metro-core` | `lodash.throttle@^4.1.1` | `dependencies` |

No `lodash`, no `lodash-es`, no `@types/lodash`. Only the single per-method package `lodash.throttle`.

**→ Proceed to Stage 2.**

---

## Stage 2 — Migration Target

### 2-1. Project character

**Build tool / Node.js runtime.** Metro is the JavaScript bundler for React Native — a CLI plus a Node API, published as ~20 npm packages (`metro`, `metro-core`, `metro-resolver`, …). Every package declares `main: "src/index.js"` and an `exports` map; all ship to npm.

`"engines": { "node": "^22.13.0 || ^24.3.0 || >= 26.0.0" }` — Node-only, no browser target.

**This is the fact that decides the whole analysis.** Metro's own code never reaches a consumer's browser bundle. It is the thing that *produces* bundles; it does not live inside one. So the standard es-toolkit argument — "your users download fewer bytes" — has no addressee here. The only size metric that means anything for Metro is **install footprint**, and that is the one metric where es-toolkit loses (see 4-3).

**Plugin exposure: no.** `throttle` is used internally in two constructors. It is not re-exported and does not appear in any public API surface (confirmed against the 14 verified API snapshots in `scripts/generateApiSnapshots.js`).

### 2-2. Is lodash in the shipped bundle?

**Shipped as a runtime `dependency`, but never bundled.** A fresh `npm i metro@0.87.0 --omit=dev` install pulls exactly one lodash package:

```
node_modules/lodash.throttle
```

**Transitive lodash: dev-only.** Every other lodash in `yarn.lock` belongs to build/lint tooling, none of it in the production tree:

| Package             | Pulled by                                   |
| ------------------- | ------------------------------------------- |
| `lodash@~4.17.15`   | `@microsoft/api-extractor`                  |
| `lodash@^4.17.14`   | `async` (→ `babel-plugin-tester`)           |
| `lodash@^4.17.21`   | `eslint-plugin-ft-flow`                     |
| `lodash.merge`      | `eslint`                                    |
| `lodash.mergewith`  | `babel-plugin-tester`                       |
| `lodash.debounce`   | `@babel/helper-define-polyfill-provider`    |

So migrating would genuinely make Metro's **production** dependency tree lodash-free. That is a real, if very small, result — and it is the strongest thing that can be said for this migration.

### 2-3. Import patterns & scope

| Pattern | Count | Bundle impact |
| ------- | ----- | ------------- |
| Full import (`import _ from 'lodash'`) | 0 | — |
| Named import | 0 | — |
| **Per-method package (`import throttle from 'lodash.throttle'`)** | **2** | Already maximally optimized |

**2 imports across 2 files. 1 distinct function.**

| File | Line | Usage |
| ---- | ---- | ----- |
| [`packages/metro/src/lib/TerminalReporter.js`](https://github.com/react/metro/blob/main/packages/metro/src/lib/TerminalReporter.js#L21) | 107 | `throttle(data => …, 100)` — bundle progress updates |
| [`packages/metro-core/src/Terminal.js`](https://github.com/react/metro/blob/main/packages/metro-core/src/Terminal.js#L15) | 116 | `throttle(status => …, 3500)` — non-TTY status writes; calls `.flush()` at line 163 |

Neither call site passes `{leading, trailing}` options. One call site depends on the `.flush()` method.

The `lodash.throttle` per-method package is the *most* optimized form lodash usage can take — a standalone 16 KB package with zero dependencies. There is no tree-shaking win available, because there is nothing left to shake.

### 2-4. Hard blockers

`sortedUniq`, `sortedUniqBy`, `mixin`, `noConflict`, `runInContext` — **none present.** No `lodash/fp`.

### Stage 2 summary

```
Repository: react/metro
2-1 (Character): Build tool / Node.js runtime (20 published pkgs) — Plugin exposure: no
2-2 (Bundle):    Runtime dependency, but Node-only — never enters a consumer bundle
                 Transitive lodash: dev tooling only (eslint, api-extractor, babel)
2-3 (Imports):   Full ×0 / Named ×0 / Per-method ×2 — Files: 2 — Functions: throttle
2-4 (Blockers):  None

Stage 2 verdict: Technically a migration candidate — but with no bundle-size case
```

---

## Stage 3 — Organizational Signals

| Signal | Finding |
| ------ | ------- |
| **Activity** | Very active. Last push 2026-08-08, last commit 2026-08-06 (`Deploy 0.326.0 to xplat`). 5,621 stars, 458 open issues. Meta-internal-first development, synced out to GitHub. |
| **Prior art** | 🔴 **[PR #1534 — "Replace lodash.throttle with es-toolkit's throttle"](https://github.com/react/metro/pull/1534). Opened 2025-07-16, closed 2025-07-17 — declined in under 24 hours.** |
| **CLA** | 🔴 **Required.** Meta CLA (`CONTRIBUTING.md` §7, `code.facebook.com/cla`), enforced by `facebook-github-bot`. PR #1534 was blocked on it immediately. |
| **lodash in public API** | No. |

### PR #1534 — what happened, and why it matters

This is not a "prior attempt that stalled." It is the identical change, argued by the es-toolkit maintainer, and refused on the merits.

**@vzaidman** (maintainer):

> Hey! Thanks for your contribution. This would have too little benefits / impact for us to replace the well tested and highly reliable and secure lodash.

**@robhogan** (maintainer) — the substantive rebuttal:

> ```
> $ gdu -sh --apparent-size node_modules/es-toolkit node_modules/lodash node_modules/lodash.throttle
> 2.5M    node_modules/es-toolkit
> 1.4M    node_modules/lodash
> 17K     node_modules/lodash.throttle
> ```
>
> Metro is a Node.js application, so install size would be the only relevant size consideration (though not a particularly important one). `es-toolkit` is actually larger than `lodash`, let alone `lodash.throttle`, which is the package you're proposing to replace. It'd be different if we included `lodash` in bundler output, but we don't.
>
> Besides that, we do tend to be cautious about accepting PRs from folks promoting their own packages, especially when they don't mention their affiliation.

The proposer (**@raon0211**, es-toolkit's author) accepted the outcome:

> Thank you for the clear feedback and explaining the reasoning! ❤️

Three things follow:

1. **The maintainers' technical reasoning is correct.** They independently identified exactly what 2-1 concludes: Metro is not bundled, so only install size counts, and on install size es-toolkit is a regression.
2. **Their objection has gotten stronger, not weaker.** They measured es-toolkit at 2.5 MB in July 2025. It is **3.70 MB apparent / 16 MB on disk** today (v1.50.0) — roughly 1.5× the size they already rejected, and that is before counting the 16 MB it occupies in real disk blocks.
3. **There is a stated affiliation-disclosure concern.** Re-raising this proposal without new evidence, especially from anyone connected to es-toolkit, would read as the same pitch a second time.

---

## Stage 4 — Verification & Measurement

Reached **Tier 2** (full build + full test suite + Flow typecheck), in an isolated clone.

The point of running Tier 2 on a repo this small is not to justify the migration — it is to make sure the low score reflects the *cost side* honestly, rather than an untested guess that the change is risky. It isn't risky. It's just not worth doing.

### 4-1. Applied migration

At the time of this run the bundled codemod did not recognise per-method packages (`lodash.throttle`), so Tier 0 reported `No lodash usage found in shipped source.` and the change was applied by hand. **That gap has since been fixed** — `measure_bundle_size.py` and `migrate_lodash_imports.py` now detect `lodash.<fn>` packages, canonicalize their all-lowercase names, and report install footprint. Re-running the patched script on a clean clone finds both imports and flags the regression:

```diff
- // $FlowFixMe[untyped-import] lodash.throttle
- import throttle from 'lodash.throttle';
+ // $FlowFixMe[untyped-import] es-toolkit
+ import {throttle} from 'es-toolkit';
```

plus `lodash.throttle` → `es-toolkit@^1.50.0` in both manifests.

Note `es-toolkit`, not `es-toolkit/compat` — the main entry is sufficient here (verified in 4-2), and compat would only add bytes.

Two hand fixes a codemod would have missed:

1. **Default → named import.** `lodash.throttle` exports a CJS default; `es-toolkit` exports `throttle` as a named export. `import throttle from 'es-toolkit'` would bind the whole namespace object and fail at the call site, not at import time.
2. **The Flow suppression must be kept and retargeted.** Metro is a Flow codebase. es-toolkit ships TypeScript types, not Flow types, so `$FlowFixMe[untyped-import]` is still required — and since Metro errors on *unused* suppressions, deleting it would break `flow check` just as surely as leaving it stale. `Terminal.js` had no suppression before (`lodash.throttle` has a `flow-typed` libdef in the repo) and needed one added.

### 4-2. Behavioral equivalence

Metro's usage is `throttle(fn, ms)` with default edges, plus `.flush()`. Verified all three implementations against that exact shape:

| Implementation | `.flush` | `.cancel` | 3 rapid sync calls | after `.flush()` | after 250 ms |
| -------------- | -------- | --------- | ------------------ | ---------------- | ------------ |
| `lodash.throttle` | ✅ | ✅ | `["a"]` | `["a","c"]` | `["a","c"]` |
| `es-toolkit` | ✅ | ✅ | `["a"]` | `["a","c"]` | `["a","c"]` |
| `es-toolkit/compat` | ✅ | ✅ | `["a"]` | `["a","c"]` | `["a","c"]` |

**Byte-identical behavior across all three.** `es-toolkit`'s main entry matches lodash on leading-edge fire, trailing coalescing, and `.flush()` semantics — so the heavier `compat` entry is unnecessary.

### 4-3. Test, typecheck, build

| Check | Before | After |
| ----- | ------ | ----- |
| `jest --ci` (whole monorepo) | 140 suites, **2,542 passed**, 14 skipped, 510 snapshots | 140 suites, **2,542 passed**, 14 skipped, 510 snapshots |
| `flow check` (1,050 files) | No errors | **No errors** |
| `yarn run build` (all packages) | OK | **OK** |
| `eslint` on both touched files | clean | clean |
| API snapshots | 14 verified | 14 verified |

**Zero regressions. Zero behavioral differences.** Diff size: **5 files changed, +14 / −13** (including `yarn.lock`).

This is about as clean as a migration gets.

### 4-4. Size — where it falls apart

**(a) Synthetic bundle of `throttle` alone** — `esbuild --bundle --minify --format=esm`:

| | minified | gzip |
| --- | --- | --- |
| `lodash.throttle` | 2,504 B | 1,210 B |
| `es-toolkit` | 844 B | 435 B |
| `es-toolkit/compat` | 1,054 B | 544 B |
| **Delta (main entry)** | **−1,660 B (−66.3%)** | **−775 B (−64.0%)** |

The −66% is real, and it is exactly the number PR #1534 quoted. **It is also irrelevant here.** Metro is never bundled and never minified for a browser; nothing downstream ever pays these 2,504 bytes as download weight. This row measures a saving that no Metro user can collect.

**(b) Install footprint — the metric that actually applies:**

| | tarball | unpacked (apparent) | on disk |
| --- | --- | --- | --- |
| `lodash.throttle@4.1.1` | 5,554 B | **16,478 B (16.1 KB)** | 28 KB |
| `es-toolkit@1.50.0` | 473,418 B | **3,879,844 B (3.70 MB)** | 16 MB |
| **Delta** | **+467,864 B (85×)** | **+3.68 MB (235×)** | **+16 MB** |

es-toolkit's bulk is its multi-format output: `dist/` 11 MB, `compat/` 4.6 MB. Metro would consume one function out of it.

**(c) In context of Metro's real production tree:**

```
npm i metro@0.87.0 --omit=dev   →   25,977,316 B  (24.8 MB)
  lodash.throttle share                 16,478 B  (0.063%)

after migration                 →   29,840,682 B  (28.5 MB, +14.9%)
```

**Swapping one function's implementation would grow every React Native developer's `node_modules` by ~15%.** That is the whole trade: save 1.6 kB that nobody downloads, pay 3.7 MB that everybody installs.

*(Dependency count is a wash — both packages have zero transitive dependencies.)*

---

## Stage 5 — Report

### Score: 15 / 100 — Do not migrate

**What migration would actually buy**

- Metro's production dependency tree becomes lodash-free (removes 1 of 1 runtime lodash packages).
- `throttle` implementation is 66% smaller by bytes and actively maintained; `lodash.throttle` has had no release since 2016.
- Verified zero-risk: 2,542 tests, Flow, and the full build all green on a 5-file diff.

**Why that is not enough**

| Deduction | Reason |
| --------- | ------ |
| **−45** | **No bundle-size case exists.** Metro is a Node.js bundler, not bundled code. The central es-toolkit benefit has no mechanism to reach a user. The 66% byte saving is unclaimable. |
| **−25** | **Install size regresses hard.** +3.68 MB apparent (235×) for one function; +14.9% on Metro's entire production tree. On the *only* size metric that applies to a Node tool, this migration makes things worse. |
| **−10** | **Already proposed and declined** ([#1534](https://github.com/react/metro/pull/1534)), with correct reasoning that has only strengthened as es-toolkit doubled in size. No new evidence has appeared since — and this analysis produced none. |
| **−5** | **Meta CLA required**, plus a stated maintainer wariness about es-toolkit-affiliated PRs. |

**The honest summary:** a flawless migration of something that should not be migrated. The scope is 2 files, the risk is nil, and the verification is perfect — but a perfect execution of a change with negative net value is still negative. `lodash.throttle` is the rare lodash dependency that is *already* in its optimal form: 17 KB, zero deps, single function, frozen and battle-tested. es-toolkit cannot beat that on the one axis that counts for a Node.js tool.

**Recommendation: do not open an issue or PR.** The maintainers have answered this question, their answer was technically right, and the facts have moved further in their favor.

---

## Stage 6 — Draft Issue

**Not produced.** Score 15 < 70, and the "still has merit" exception does not apply.

The skill's Stage 6 exists to write a proposal a maintainer would be glad to receive. Here, the maintainers already received it, evaluated it in under 24 hours, and explained precisely why they said no — and the strongest counter-evidence available (the size measurements above) supports *their* position, not the proposal's. Re-filing it would be re-litigating a settled, correctly-decided question.

### If circumstances change

This verdict is a function of es-toolkit's install footprint, not of anything about Metro. It would be worth revisiting if:

- **es-toolkit ships a slim distribution** — a Node-facing entry point that installs in the tens of KB rather than 3.7 MB. This is the single blocker; everything else about the migration is already green.
- **Metro's lodash usage grows** past one function, or Metro starts shipping code into browser bundles. Neither is on the horizon.

Until one of those holds, the correct action is none.

---

## Appendix — Reproduction

```bash
git clone --depth 1 https://github.com/react/metro.git && cd metro
yarn install --frozen-lockfile
npx jest --ci                                   # baseline: 2,542 passed

# apply: lodash.throttle → es-toolkit in TerminalReporter.js + Terminal.js,
#        swap dependency in packages/metro/package.json + packages/metro-core/package.json
yarn install
npx jest --ci                                   # 2,542 passed — identical
npx flow check                                  # No errors!
yarn run build                                  # all packages OK

# install footprint
npm i metro@0.87.0 --omit=dev                   # 24.8 MB
npm pack es-toolkit@1.50.0 lodash.throttle@4.1.1  # 473,418 B vs 5,554 B
```

**Note on the repo URL:** `facebook/metro` now redirects to **`react/metro`** — the org moved. Both `git clone` and the GitHub API follow the redirect, but API calls need `curl -L` (a bare call returns `301 Moved Permanently`).
