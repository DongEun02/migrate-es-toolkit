# can-migrate-es-toolkit

A Claude Code skill that analyzes GitHub repositories to determine whether their lodash dependency can be migrated to [es-toolkit](https://github.com/toss/es-toolkit).

## What it does

Given a GitHub repository URL, this skill:

1. **Gate check** — Detects whether lodash exists in any `package.json`
2. **Target assessment** — Analyzes project type, bundle inclusion, import patterns, and hard blockers, then applies an early-termination gate: if no migration rationale survives, the skill stops here and reports
3. **Organizational signals** — Checks repo activity, prior migration attempts, CLA requirements
4. **Measure & verify** — Measures the bundle-size delta and verifies the migration actually builds and passes tests, in escalating tiers
5. **Report** — Produces a scored (1–100) migration feasibility report
6. **Issue draft** — Generates a GitHub issue description for high-scoring candidates

Step 4 runs in tiers so cost tracks confidence:

| Tier | Cost | What it produces |
|------|------|------------------|
| 0 — synthetic measurement | seconds, no repo install | bundle-size delta, install-footprint delta, empirical `es-toolkit/compat` coverage check |
| 1 — codemod smoke test | ~1 min | migration applied, largest package's tests run |
| 2 — full verification | minutes | full build + full test suite across all packages |

Tier 0 always runs — Step 2's termination gate invokes it, so a size-based no-go is always measured rather than assumed. Tiers 1 and 2 are entered only when the score justifies them. Scores of 70+ require measurement; static analysis alone caps at 69.

Steps 3–6 are skipped entirely when Step 2 terminates. A repository with no migration rationale gets a two-minute answer, not an hour of organizational research.

## Installation

### From `.skill` file

```bash
claude install-skill can-migrate-es-toolkit.skill
```

### Manual

Copy this directory into your Claude Code skills directory:

```bash
cp -r can-migrate-es-toolkit ~/.claude/skills/can-migrate-es-toolkit
```

## Usage

```
/can-migrate-es-toolkit https://github.com/org/repo
```

With a specific response language:

```
/can-migrate-es-toolkit https://github.com/org/repo ko
```

### Examples

```
/can-migrate-es-toolkit https://github.com/vercel/next.js
/can-migrate-es-toolkit https://github.com/facebook/react ko
/can-migrate-es-toolkit https://github.com/expressjs/express ja
```

## Bundled Scripts

### `scripts/measure_bundle_size.py`

Measures the bundle-size impact of the migration without installing or building the target repository. Used in Step 4, Tier 0.

```bash
python scripts/measure_bundle_size.py /path/to/repo
python scripts/measure_bundle_size.py /path/to/repo --include-tests
python scripts/measure_bundle_size.py /path/to/repo --json
```

It extracts the distinct lodash functions the repo's shipped source actually uses (subpath, named, `require`, whole-namespace `_.fn()` call sites, and per-method packages like `lodash.throttle`), runtime-checks each against `es-toolkit/compat` — which also recovers the canonical casing that all-lowercase per-method package names lose (`lodash.mergewith` → `mergeWith`) — then bundles that exact function set from `lodash-es`, or from the real per-method package where one is used, and from `es-toolkit/compat` with esbuild, reporting the minified / gzip delta.

It also reports the **install-footprint** delta and warns when es-toolkit is the larger install. For a Node-only project — a CLI, bundler, or server that is never bundled for a browser — that is the only size metric that applies, and the bundle delta is unclaimable. Read both numbers before citing either.

Requires `node` and `npm`. Installs three packages into a reusable scratch dir — about 3 seconds cold, under a second cached.

```
                          minified          gzip
------------------------------------------------
lodash-es                 31,059 B      11,464 B
es-toolkit/compat         20,285 B       6,226 B
delta                    -10,774 B      -5,238 B
                            -34.7%        -45.7%
```

The synthetic figure tracks reality closely: against a real before/after build of `react-jsonschema-form`, it predicted the measured delta to within 1% (−10,774 B synthetic vs −10,681 B actual, minified).

It measures the **lodash slice only** — the bytes that leave a consumer's bundle, not their total bundle size.

Functions missing from `es-toolkit/compat` are reported and excluded from the measurement. This is an empirical blocker check, so it catches gaps the fixed hard-blocker list does not.

### `scripts/migrate_lodash_imports.py`

Replaces lodash imports with `es-toolkit/compat` equivalents. Used in Step 4, Tier 1.

```bash
# Preview changes
python scripts/migrate_lodash_imports.py /path/to/repo --dry-run

# Apply changes
python scripts/migrate_lodash_imports.py /path/to/repo --write
```

Handles ES module imports, CommonJS requires, subpath imports, namespace imports, per-method packages (`lodash.throttle`, `lodash.mergewith`), and `lodash-es`. Local bindings are preserved (`import _get from 'lodash/get'` → `import { get as _get } from 'es-toolkit/compat'`). Skips files importing hard-blocker functions (`sortedUniq`, `sortedUniqBy`, `mixin`, `noConflict`, `runInContext`) or using `lodash/fp`.

> A clean dry-run is **not** verification — it counts import statements without executing anything. Import-shape errors in migrated code fail silently at runtime, not at import time. Always follow `--write` with a test run.

## Score Bands

| Score | Meaning |
|-------|---------|
| 0–29 | Hard blocker; lodash never reaches end users; the benefit does not apply; or the net size effect is a regression |
| 30–49 | Technically possible but major organizational barriers or very large scope |
| 50–69 | Feasible but limited benefit, or measurement stopped at Tier 0 |
| 70–89 | Good conditions with a measured benefit (Tier 0 minimum, Tier 1 green) |
| 90–100 | Excellent — narrow scope, active repo, Tier 2 green, minimal risk |

A clean Tier 2 run proves the migration is *safe*, not that it is *worth doing*. When the benefit reaches nobody (a Node-only project that is never bundled) or the net size effect is a regression, the score belongs in 0–29 however green the verification. Before citing a number as an upside, name who collects it.

## Requirements

- Claude Code CLI
- Python 3.9+ (for the bundled scripts)
- `node` and `npm` (for `measure_bundle_size.py`)
- `gh` CLI — optional. Used for GitHub API queries in Step 3; falls back to web fetches when unavailable

## License

MIT
