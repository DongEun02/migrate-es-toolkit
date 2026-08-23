# can-migrate-es-toolkit

A Claude Code and Codex skill that analyzes GitHub repositories to determine whether their lodash dependency can be migrated to [es-toolkit](https://github.com/toss/es-toolkit).

## What it does

Given a GitHub repository URL, this skill:

1. **Gate check** — Detects whether lodash exists in any `package.json`
2. **Target assessment** — Analyzes project type, bundle inclusion, import patterns, and hard blockers, then applies an early-termination gate: if no migration rationale survives, the skill stops here and reports
3. **Organizational signals** — Checks repo activity, prior migration attempts, CLA requirements
4. **Measure & verify** — Measures the bundle-size delta and, for strong candidates only, applies the migration and runs the target's build and test suite
5. **Report** — Produces a scored (1–100) migration feasibility report
6. **Issue draft** — Generates a GitHub issue description for candidates scoring 50+

Step 4 runs in tiers so that cost tracks how promising the repository already looks:

| Tier | Cost | Entry condition | What it produces |
|------|------|-----------------|------------------|
| 0 — synthetic measurement | seconds, no install | always | bundle-size delta, install-footprint delta, empirical `es-toolkit/compat` coverage check |
| 1 — codemod shape | seconds, no install | Tier 0 says candidate | diff size, the fraction that is one-line import rewrites, every hand fix the codemod cannot do |
| 2 — full verification | **minutes to an hour** | provisional score ≥ 70, and you intend to propose it | baseline vs migrated build, full test suite, production artifact comparison |

**Tier 2 is the expensive one, and most runs must never reach it.** Verifying a migration you are about to argue against costs an hour and buys nothing, so a no-go verdict never earns a Tier 2 run — the gate is a provisional score written down *before* the first `install`. Tiers 0 and 1 alone cap the score at 69: a measured benefit plus a mechanical diff is still an untested change, and the issue draft says exactly that.

Steps 3–6 are skipped entirely when Step 2 terminates. A repository with no migration rationale gets a two-minute answer, not an hour of organizational research.

## Installation

### Codex

Clone the repository and launch Codex from anywhere inside it. Codex automatically discovers the repository-scoped skill under `.agents/skills`.

For personal use across repositories, symlink the skill so the Codex adapter can continue sharing the canonical workflow and scripts from this checkout.

```bash
mkdir -p ~/.agents/skills
ln -s /absolute/path/to/can-migrate-es-toolkit/.agents/skills/can-migrate-es-toolkit \
  ~/.agents/skills/can-migrate-es-toolkit
```

Invoke it with:

```text
$can-migrate-es-toolkit https://github.com/org/repo
$can-migrate-es-toolkit https://github.com/org/repo ko
```

### Claude Code

#### From `.skill` file

```bash
claude install-skill can-migrate-es-toolkit.skill
```

#### Manual

Copy this directory into your Claude Code skills directory:

```bash
cp -r can-migrate-es-toolkit ~/.claude/skills/can-migrate-es-toolkit
```

## Claude Code usage

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

`lodash/fp` imports are reported separately as manual-rewrite warnings. They do not
trigger an automatic hard blocker, but they are unverified manual cost the report has to
name.

When the lockfile shows transitive lodash, the reported delta is an **upper bound, not a
saving** — another dependency may keep its own lodash copy, in which case es-toolkit is
added beside it and the shipped bundle grows. The skill reports it that way, names the
dependency responsible, and scores the benefit as unproven rather than found.

### `scripts/migrate_lodash_imports.py`

Replaces lodash imports with `es-toolkit/compat` equivalents. Used in Step 4, Tier 1 — it is pure source transformation, so it runs in seconds and never installs anything.

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
| 50–69 | Feasible, with a measured benefit that reaches someone — but stopped at Tier 1, so untested |
| 70–89 | Good conditions, a measured benefit, and a green Tier 2 |
| 90–100 | Excellent — narrow scope, active repo, Tier 2 green including a production build, minimal risk |

70+ requires a completed Tier 2; Tiers 0–1 cap at 69 however clean the code looks. A green Tier 2 run proves the migration is *safe*, not that it is *worth doing* — when the benefit reaches nobody (a Node-only project that is never bundled) or the net size effect is a regression, the score belongs in 0–29 however green the verification. Before citing a number as an upside, name who collects it.

## Requirements

- Codex or Claude Code CLI
- Python 3.9+ (for the bundled scripts)
- `node` and `npm` (for `measure_bundle_size.py`)
- `gh` CLI — optional. Used for GitHub API queries in Step 3; falls back to web fetches when unavailable

## License

MIT
