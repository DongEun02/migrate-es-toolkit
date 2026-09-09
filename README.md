# can-migrate-es-toolkit

A Claude Code and Codex skill that analyzes GitHub repositories to determine whether their lodash dependency can be migrated to [es-toolkit](https://github.com/toss/es-toolkit).

## What it does

Given a GitHub repository URL, this skill:

1. **Gate check** — Detects whether lodash exists in any `package.json`
2. **Target assessment** — Analyzes project type, bundle inclusion, import patterns, and hard blockers, then applies an early-termination gate: if no migration rationale survives, the skill stops here and reports
3. **Organizational signals** — Checks repo activity, prior migration attempts, CLA requirements
4. **Measure & verify** — Measures the bundle-size delta and, for strong candidates only, applies the migration and runs the target's build and test suite
5. **Report** — Produces a scored (0–100) recommendation with evidence, risks, and implementation readiness

The skill ends with the assessment. Issue drafting is reserved for a separate skill.

Step 4 runs in tiers so that cost tracks how promising the repository already looks:

| Tier | Cost | Entry condition | What it produces |
|------|------|-----------------|------------------|
| 0 — synthetic measurement | seconds, no install | always | bundle-size delta, install-footprint delta, empirical `es-toolkit/compat` coverage check |
| 1 — codemod shape | seconds, no install | Tier 0 says candidate | diff size, the fraction that is one-line import rewrites, every hand fix the codemod cannot do |
| 2 — full verification | **minutes to an hour** | provisional score ≥ 70, a named uncertainty that verification can resolve, and the workflow's remaining gates met | baseline vs migrated build, full test suite, production artifact comparison |

**Tier 2 is the expensive one, and most runs must never reach it.** A no-go verdict does not earn a Tier 2 run — the gate is a provisional score written down *before* the first `install`. Run Tier 2 when its gates and environment permit. Tiers 0–1 normally cap the final score at 69; a strong, evidenced benefit can qualify for 70–79 when verification cannot be completed, with implementation readiness explicitly marked as pending. This exception does not justify skipping available verification.

When Step 2 terminates, skip further investigation and record the no-go score in the five-step report. A repository with no migration rationale gets a short answer without organizational research.

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

> A clean dry-run is **not** verification — it counts import statements without executing anything. Follow `--write` with the gated Tier 2 checks before claiming the migration works; a Tier 1 assessment must say verification is pending.

## Score Bands

| Score | Meaning |
|-------|---------|
| 0–29 | Hard blocker; no applicable benefit; or a net regression in the claimed size benefit |
| 30–49 | No persuasive net benefit, or unresolved evidence against the migration |
| 50–69 | Some benefit, but insufficient evidence or benefit relative to remaining work |
| 70–89 | A defensible benefit worth pursuing; green Tier 2, or the strong-benefit exception at 70–79 |
| 90–100 | Excellent — narrow scope, active repo, Tier 2 green including a production build, minimal risk |

The score reflects whether the migration is worth pursuing, separately from whether it is ready to merge. A large diff, feasible manual rewrites, or an uncertain maintainer response alone should not force a clearly worthwhile migration below 70.

The **strong-benefit exception** requires all four: a confirmed beneficiary and concrete gain; a repository-specific case supported by measurements or substantial, source-confirmed maintenance savings; a credible path through the remaining work; and no overriding negative evidence. Generic es-toolkit advantages or hope that a PR will be accepted do not qualify.

For qualifying cases, restore **5–10 points** deducted for implementation or review friction, once and never more than those deductions. This is not an automatic score floor or a duplicate benefit bonus. Without green Tier 2, qualifying scores remain capped at **79** and must say **“Recommended — implementation verification pending.”** Scores of 80+ require green Tier 2, and 90+ also require a production build and minimal risk.

Hard blockers, actual behavioral regressions, an upper-bound-only size argument, and unanswered technical objections remain disqualifying for the exception. A net regression in the claimed size benefit caps at 29; an upper-bound-only size rationale or behavioral regression caps below 50. A green suite supplies verification, not a benefit. Name the users collecting a saving or the maintainers whose concrete work disappears, and account for install growth explicitly.

The complete bases, adjustments, and exception conditions are maintained in the [shared workflow](.claude/commands/can-migrate-es-toolkit.md).

## Requirements

- Codex or Claude Code CLI
- Python 3.9+ (for the bundled scripts)
- `node` and `npm` (for `measure_bundle_size.py`)
- `gh` CLI — optional. Used for GitHub API queries in Step 3; falls back to web fetches when unavailable

## License

MIT
