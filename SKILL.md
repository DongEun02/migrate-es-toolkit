---
name: can-migrate-es-toolkit
description: >
  Analyze a GitHub repository to determine whether its lodash dependency can be migrated to es-toolkit.
  Use this skill whenever the user wants to check migration feasibility for a specific open-source project,
  evaluate lodash-to-es-toolkit migration risk, or prepare an issue proposal for lodash removal.
  Triggers on: "/can-migrate-es-toolkit", "can this repo migrate from lodash", "check lodash migration",
  "es-toolkit migration feasibility", or any request to assess whether a library can replace lodash with es-toolkit.
---

# can-migrate-es-toolkit

Analyze a GitHub repository's lodash usage and determine whether it can be migrated to es-toolkit.

## Usage

```
/can-migrate-es-toolkit <repository-url> [response-language]
```

- `repository-url`: GitHub repository URL (e.g. `https://github.com/org/repo`)
- `response-language`: ISO 639-1 code (e.g. `ko`, `ja`). Default: `en`

Follow the workflow below in order. Record each step's results in the report cumulatively. If an early step hits a termination condition, skip remaining steps and submit the report immediately.

**Most no-go verdicts should be reached by the end of Step 2.** Steps 3–6 exist to evaluate a migration that is worth evaluating; running them on a repository that has already failed the Step 2-5 gate spends an hour to reach a conclusion you already had. Terminating early is a successful run, not an abandoned one.

---

## Step 1. Migration Gate Check

Find every `package.json` in the repository (monorepo-aware).

Check whether any `package.json` lists `lodash` (or `lodash-es`, `lodash.*` per-method packages) in `dependencies` or `devDependencies`.

- **Found** → proceed to Step 2
- **Not found** → terminate with report: "No lodash dependency detected"

---

## Step 2. Assess Migration Target

### 2-1. Understand the project from README.md

The migration criteria differ depending on whether the repository is an end-user application or a published library that others depend on.

Check:
- Classify via README intro / Installation section:
  - End-user application (web app, CLI tool)
  - Published library/package (npm-published)
  - Build tool / server runtime (Node.js-only)
- Confirm publish intent from `package.json` fields: `name`, `main`/`module`/`exports`
- Look for plugin architecture, extension systems, or `peerDependencies` mentions in README
  - If present: the library may pass lodash instances or utilities to external plugins → a compatibility shim layer may be needed instead of a simple swap (cf. Grafana case)

### 2-2. Confirm lodash reaches the shipped bundle

If lodash never reaches end users, migration has no practical impact.

**First, a question that outranks every other check in this step: does this project's code get bundled at all?**

A `dependency` is not the same as a bundled byte. Node-only projects — CLIs, bundlers, dev servers, build tools, test runners — are installed and executed from `node_modules`, never bundled or minified for a browser. For those, the "your users download fewer bytes" argument has **no recipient**, and any gzip delta you measure is unclaimable by anyone.

Signals that a project is Node-only:
- `"engines": { "node": … }` with no browser field, no `browserslist`
- `bin` entry, or the README describes a CLI / server / build step
- README positions it as tooling that *processes* code rather than shipping into an app

If Node-only, **install footprint is the only size metric that applies** — and es-toolkit ships every build format (~3.7 MB unpacked vs. lodash's 1.4 MB, or 16 KB for a per-method package). Expect a regression and measure it in Step 4. Do not carry a bundle-size argument into the report for a project that is never bundled.

Check:
- Is lodash in `dependencies` vs. `devDependencies` only?
- Paths where lodash is imported:
  - `src/`, `lib/` → shipped code
  - `test/`, `__tests__/`, `examples/`, `docs/`, `scripts/` → not shipped (weak migration justification if all usage is here)
- Build config (webpack/rollup/vite config, `.npmignore`, `package.json` `files` field) — confirm the import paths actually end up in the published artifact
- **Transitive dependency check**: scan the lockfile (`package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`) for other dependencies that pull in lodash
  - If others also require lodash, migrating this repo alone won't eliminate lodash from `node_modules` → not a blocker, but note it in the report

### 2-3. Catalog import patterns and usage scope

Import style affects bundle-size impact and migration workload. The data collected here is reused in Steps 4 and 5 — no need to re-grep later.

Grep for these patterns:

| Pattern | Example | Impact |
|---------|---------|--------|
| Full import | `import _ from 'lodash'`, `const _ = require('lodash')` | Pulls everything — max bundle impact. Highest migration benefit |
| Named import | `import { pick, chunk } from 'lodash'` | lodash is not tree-shakeable — still bloats the bundle. High benefit |
| Subpath import | `import pick from 'lodash/pick'` | Already optimized. Smaller bundle gain, but still reduces install size and type surface |
| Per-method package | `import throttle from 'lodash.throttle'`, `require('lodash.mergewith')` | **Already the optimal form** — a standalone package with zero dependencies. Nothing left to tree-shake. Migration adds install weight and removes almost nothing. Treat as a strong negative signal unless the project is browser-bundled |

Also record:
- File count and import count per pattern (total scope)
- Top functions by usage frequency (Step 4 re-derives this precisely — a rough tally is enough here)
- If scope is large (40+ files), flag in the report: large PRs risk being ignored or stuck in review

### 2-4. Hard-blocker: compat-unsupported functions

If the codebase uses any of these functions, migration to `es-toolkit/compat` is impossible. **Terminate immediately** with report "Hard blocker found".

Grep for:
- `sortedUniq`
- `sortedUniqBy`
- `mixin`
- `noConflict`
- `runInContext`

### 2-5. Early termination: is there any rationale left?

Most repositories that should not migrate can be settled here, without Step 3's organizational research or Step 4's Tier 1/2 runs. Terminating early is the point of this step — a firm no delivered in two minutes is more useful than the same no after an hour.

**Run Tier 0 first** (`measure_bundle_size.py`, seconds). A termination that cites size must cite a measured size, not an assumption.

Terminate with **"No migration rationale"** when **any one** of these holds:

| # | Condition | Why it ends the analysis |
|---|-----------|--------------------------|
| A | lodash appears only in `devDependencies`, or only under test / docs / example / script paths | Nothing reaches a user. There is nothing to remove |
| B | Project is never bundled for a browser **and** lodash usage is already in its minimal form (per-method packages, or a handful of subpath imports) **and** Tier 0 shows an install-footprint regression | No byte reaches a consumer, and the swap makes the only applicable metric worse. This is the `react/metro` shape |
| C | A function in use is missing from `es-toolkit/compat` (2-4, or the Tier 0 runtime check) | Migration is impossible, not merely unwise |

**Do not terminate** if any of the following is true — these are the residual benefits that survive even when the bundle argument dies, and killing the analysis here would be wrong:

- **Non-tree-shakeable surface is large**: many distinct functions pulled through `import { … } from 'lodash'` or a whole-namespace import. Even in a Node process, that is real parse and resolve weight, and it is not already optimized
- **lodash sits in `dependencies` of several published packages** — every downstream install carries it, and removing it simplifies more than one dependency graph
- **Type-quality or maintenance arguments have independent force**: `@types/lodash` is a separate untyped dependency, or the repo's own source carries `TODO: move away from lodash` markers
- The install-footprint regression is **proportionally trivial** against the project's existing dependency tree

The distinction that matters: **"the benefit does not reach anyone" is a termination; "the benefit is small" is a low score.** Condition B requires all three of its clauses precisely so that a Node-only project with a large, unoptimized lodash surface still gets a full analysis. If you find yourself terminating solely because the project is Node-only, you have applied the gate wrong — go back and check the residual-benefit list.

On termination: write the report with the score in the 0–29 band, the verdict label **Do not migrate**, and one sentence naming the condition that fired. State plainly that Steps 3–6 were skipped and why. Do not research organizational signals to pad it out.

### Step 2 Verdict Template

```
Repository: <repo>
2-1 (Type): <Application / Library / Server runtime> — Plugin exposure: <yes/no>
2-2 (Bundle): <Included / Not included / devDep only> — Browser-bundled: <yes/no>
                Transitive deps: <yes/no>
2-3 (Imports/Scope): Full ×N / Named ×N / Subpath ×N / Per-method ×N — Files: N
                     Distinct functions: N — Top: <list>
2-4 (Hard blocker): <None / Found: function_name>
2-5 (Early exit): <None — continue / Terminated: condition A|B|C — reason>

Step 2 verdict: <Migration candidate / Not a migration target / No migration rationale — terminated>
```

---

## Step 3. Organizational Signal Check

Even when technically feasible, organizational barriers can prevent migration from actually landing (cf. react-router, Grafana, n8n cases).

**Write down your technical verdict from Step 2 before you read any prior issue or PR.** A maintainer's rejection is persuasive, and reading it first makes it hard to tell whether your score reflects your own evidence or theirs. Commit to a provisional number, then look, then record whether the prior art *changed* it or merely confirmed it. Both facts belong in the report.

Check:
- **Repository activity**: recent commit / issue-response frequency. Inactive repos → PRs get ignored
- **Prior related issues/PRs**: search for lodash removal, dependency cleanup, or es-toolkit mentions
  - If found: understand why they didn't land (abandoned, rejected, still open) and whether context can be reused
  - **A prior attempt closed with a reasoned technical objection is decisive, not merely a data point.** Check whether the objection still holds against today's measurements — es-toolkit's install size grows over time, so an old size-based rejection may have gotten *stronger*. Re-proposing without new evidence that answers the stated objection is not a contribution; it is the same pitch a second time
  - Note whether the earlier proposer was affiliated with es-toolkit, and whether maintainers reacted to that. If so, tone in Step 6 matters more than usual — and disclosure is mandatory
- **CLA requirement**: check `CONTRIBUTING.md` and `.github/` for CLA bot config. CLA adds contributor friction
- **Lodash exposed via public API / plugins** (revisit 2-1): if so, note that a backwards-compatibility shim is needed

These findings feed into Step 5 scoring and Step 6 issue tone.

---

## Step 4. Measure and Verify

Steps 1–3 establish that migration is *possible*. They cannot tell you what it *costs* or whether it actually *works* — static analysis passes cases that break on execution. This step produces the two things maintainers ask about: **how many bytes do consumers save**, and **does the test suite still pass**.

Do not benchmark runtime speed. Most repositories have no benchmark script, and "is lodash slower" is rarely the question behind a migration proposal.

Work in an **isolated scratch clone** throughout — never the user's workspace.

Escalate through the tiers. Stop at whichever tier answers the question.

### Tier 0 — Synthetic measurement (always run; seconds)

Step 2-5 already runs this. Reuse those numbers rather than re-running — and if you reached Step 4 at all, it means the 2-5 gate did *not* fire, so read the Tier 0 output again with that in mind.

```bash
python {skill_directory}/scripts/measure_bundle_size.py <clone-dir>
```

Needs no repository install and no benchmark script. It:

- extracts the distinct lodash functions used in **shipped** source (test / docs / example paths excluded by default; `--include-tests` to include them)
- recovers functions from whole-namespace imports via `_.fn()` call sites
- **runtime-checks every function against `es-toolkit/compat`** — an empirical blocker check that catches gaps the fixed list in 2-4 would miss
- recovers per-method packages (`lodash.throttle`, `lodash.mergewith`) and canonicalizes their all-lowercase names against the real export list
- bundles that exact function set from `lodash-es` — or from the actual per-method package where one is used — and from `es-toolkit/compat`, reporting the minified and gzip delta
- reports the **install footprint** delta alongside it, and warns when es-toolkit is the larger install

Add `--json` for machine-readable output.

**Read both numbers, and decide which one applies.** The bundle delta only counts if 2-2 established that this project's code reaches a consumer bundle. For a Node-only project, the install-footprint line *is* the measurement, and it will normally show a regression. Reporting a gzip saving that nobody can collect is the single most misleading thing this skill can do.

This measures the **lodash slice only** — the bytes that leave a consumer's bundle, not their total bundle size. Report it that way. Do not inflate it into a claim about the app's whole bundle.

Tier 0 alone is enough to score up to the 70s. If any function is missing from `es-toolkit/compat`, treat it exactly like a 2-4 hard blocker.

### Tier 1 — Codemod smoke test (migration candidates only; ~1 minute)

Only when Tier 0 says the repo is a candidate and you intend to recommend migration.

1. Run `{skill_directory}/scripts/migrate_lodash_imports.py <clone-dir>` with `--dry-run` first, then `--write`.
2. Replace `lodash` / `lodash-es` with `es-toolkit` in every affected `package.json`, then install.
3. Run the test suite of the **single package with the most lodash imports**.

**A clean dry-run is not verification.** It counts import statements; it does not execute anything. Import-shape mistakes in migrated code — a named export bound as a default, a dropped alias — fail silently at runtime, not at import time. Only a test run catches them.

Record every hand fix the codemod could not make. These belong in the report: they are the honest cost of the migration, and maintainers will hit them too. Common ones:

- test-harness mock paths (`vi.mock('lodash/uniqueId')`, `jest.mock(...)`) still pointing at lodash
- `@ts-expect-error` directives that become stale, or stay necessary, after the swap

### Tier 2 — Full verification (only when drafting an issue in Step 6; minutes)

Run the full build and the full test suite across all packages. If a build or typecheck script exists, run it too. Report exact counts (`N tests passed, 0 failed`) — a precise number is the single most persuasive line in the issue.

Optionally, if the repo does happen to have a benchmark script, run it before and after as a bonus data point. Never block on its absence.

If Tier 2 surfaces a real behavioral difference between lodash and `es-toolkit/compat`, that outranks every other signal — report it prominently and cap the score below 50.

**Separate a semantic difference from a platform-floor regression.** They are not the same finding and must not carry the same penalty:

- **Semantic** — the same input produces a different result. Unfixable without changing call sites. Caps the score below 50.
- **Platform floor** — behavior is identical everywhere it runs, but `es-toolkit` requires newer JS builtins than lodash does, so the minimum supported browser rises. `es-toolkit/compat` reaches for `Object.hasOwn` (Safari 15.4+, Chrome 93+) in `get`, `set`, `pick`, `omit`, `merge`, `isEqual`, `cloneDeep`, `union`, `uniqBy`, `mapValues`, `flatMap`, `findLastIndex` and others, where lodash uses none. No cap, but a **mandatory prominent caveat plus a stated mitigation** — the maintainers' documented baseline is the thing that decides it, and only they can move it.

A green test suite cannot detect a platform-floor regression: tests run in Node, which has every builtin. So check it explicitly rather than inferring it from a passing run. Bundle each used function and grep the output for the newer builtins:

```bash
for f in <functions>; do
  echo "import { $f } from 'es-toolkit/compat'; console.log($f);" > e.mjs
  esbuild e.mjs --bundle --format=esm --outfile=o.js
  grep -c "Object\.hasOwn" o.js
done
```

Then compare the hit list against the project's documented browser support (`README`, `docs/**/installation*`, `browserslist`, `.browserslistrc`). The main `es-toolkit` entry usually hits far fewer than `compat` does — if a function exists in both, prefer main and re-check.

### Recording

Attach raw numbers, not summaries: byte counts before and after, test counts before and after, and the diff size (`files changed, +insertions/-deletions`). State which tier you reached — an unreached tier is unmeasured, not passed.

---

## Step 5. Submit Report

Synthesize all findings into a report.

**Scoring**: qualitative judgment on a 1–100 scale based on all evidence gathered in Steps 1–4. Use these bands as anchors:

| Score | Verdict label (use verbatim) | Meaning |
|-------|------------------------------|---------|
| 0–29 | **Do not migrate** | Hard blocker present; lodash never reaches end users; the benefit does not apply to this project; or the net size effect is a regression |
| 30–49 | **Not recommended** | Technically possible but major organizational barriers (low activity, CLA, a reasoned prior rejection) or very large scope |
| 50–69 | **Marginal** | Feasible but limited benefit (transitive deps remain, mostly subpath imports), or measurement never got past Tier 0 |
| 70–89 | **Recommended** | Good technical and organizational conditions, with a **measured** benefit (Tier 0 minimum, Tier 1 green) |
| 90–100 | **Strongly recommended** | All conditions excellent — narrow scope, active repo, Tier 2 green, measured improvement, minimal risk |

Rules on scoring:

- A score of 70+ requires measurement from Step 4. Static analysis alone caps at 69, however clean it looks.
- Always explain **why** the score is what it is — never just drop a number. State the deductions explicitly.
- **Green verification is not a benefit.** A passing test suite proves the migration is *safe*, not that it is *worth doing*. The bands above measure value delivered; a flawless Tier 2 run on a change with no upside scores in the 0–29 band, not the 70–89 one. Do not let the size of your verification effort inflate the score.
- **Score the benefit that actually reaches someone.** Before citing a number as an upside, name who collects it. If the answer is "nobody, because this project is never bundled," the number is worth zero, however large the percentage.
- **Cap at 29 when the net size effect is negative.** If migration removes bytes nobody downloads while adding megabytes everybody installs, that is a regression regardless of how clean the diff is.

### Lead with the verdict

Every report opens with the score, the verbatim verdict label, and **one sentence naming the single decisive reason** — before any stage detail. The reader must know the answer without scrolling.

```
Verdict: 15 / 100 — Do not migrate
Metro is a Node.js bundler that is never bundled, so the byte saving reaches
nobody, while es-toolkit adds 3.7 MB to every install.
```

### Say "no" without hedging

A no-go verdict is the most useful output this skill produces, and it is worthless if the reader has to infer it. When the score is under 50, state the conclusion as a decision, not as an impression:

- **Name the action.** "Do not open an issue or PR." Not "may not be worth pursuing," not "the maintainers might not be receptive."
- **Give the one reason that decides it**, and put it first. Extra reasons go after; they must not dilute the first.
- **Do not soften a no-go with the verification results.** "All 2,542 tests pass" belongs in Step 4, not in the verdict. A perfect diff of a pointless change is still a pointless change — say exactly that.
- **Do not offer a consolation path** — no "if you still want to try," no staged-rollout plan, no draft issue "just in case." Those belong to scores ≥ 70 only.
- **Do not treat maintainer resistance as an obstacle to route around.** If they declined for a sound reason, the finding is that they were right.
- Banned hedges in a verdict sentence: *might*, *could be worth*, *arguably*, *some teams may*, *it depends*.

Then say what would change the answer — a specific, falsifiable condition ("es-toolkit ships a slim Node entry point under 100 KB"), not a vague "revisit later." That is what makes a firm no honest rather than dismissive.

### Sanity check before submitting

Answer these in one line each. Any "no" caps the score below 50:

1. Who specifically is better off after this migration, and in what unit?
2. Does that benefit survive the install-footprint number from Step 4?
3. If a maintainer has already declined this, what new evidence answers their stated objection?

If all three answers are weak, the correct output is a low score, a blunt no-go verdict, and no issue draft. That is a successful run of this skill, not a failed one.

---

## Step 6. Draft Issue Description

**Condition**: score ≥ 70, or < 70 but migration still has merit.

**If a PR or issue proposing this migration is already open, do not draft anything.** A second proposal splits attention and reads as pressure. Report the open item, say what state it is in and what it is blocked on, and make the recommendation *support that PR* — a review, a reproduction of its numbers, a fix for the specific objection raised on it. This holds regardless of score; a 90 with an open PR still produces no draft.

**Skip this step entirely when the score is under 50.** Do not draft an issue "for reference," do not include a shortened version, do not sketch what it would say. Write one line stating the step was skipped and why. Producing a polished proposal for a migration you just argued against undercuts the verdict and is the most likely way this skill misleads someone.

Include:
- Why migration is worth considering
- What changes (before/after)
- Concrete benefits — cite the Step 4 measurements, and say which tier produced them
- The hand fixes Tier 1 required, and any caveat that weakens the case (transitive lodash that survives, install-size growth, large diff). Stating these unprompted is what separates a proposal from a pitch

### Tone guidelines
- Friendly, respectful, and open to discussion
- Frame as a suggestion, not a demand
- Provide persuasive evidence without coming across as promotional for es-toolkit
- Adjust tone based on Step 3 organizational signals:
  - Low activity → be extra gentle, acknowledge the maintenance situation
  - CLA barrier → mention it honestly
  - Prior failed attempts → acknowledge and respect that context
- Lead with the measurements; keep prose tight. Tables over paragraphs

---

## Response Language

Check the `response-language` argument. Default is English.

Supported format: ISO 639-1 codes like `ko`, `ja`, `zh`, `es`, etc.
