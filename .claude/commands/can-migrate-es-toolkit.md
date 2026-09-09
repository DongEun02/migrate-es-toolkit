---
name: can-migrate-es-toolkit
description: >
  Analyze a GitHub repository to decide whether replacing its lodash dependency with es-toolkit is worth doing and possible,
  and report the benefits, risks, and recommendation. Triggers on "/can-migrate-es-toolkit", "can this repo migrate from lodash",
  "check lodash migration", "es-toolkit migration feasibility", or any request to assess a lodash-to-es-toolkit swap.
---

# can-migrate-es-toolkit

```
/can-migrate-es-toolkit <repository-url> [response-language]
```

- `repository-url`: GitHub repo URL. `response-language`: ISO 639-1 (`ko`, `ja`, …). Default `en`.

Two questions, in this order: **is the migration worth doing** (who collects a benefit, how big), then **is it possible** (what blocks it, how large the change, whether it holds together). The first gates the second — a migration nobody benefits from is not worth checking the feasibility of.

The deliverable is an assessment ending at Step 5. Issue drafting belongs to a separate skill; do not generate an issue title, body, or posting script here. The score measures whether the migration is worth pursuing, not the probability that a maintainer will merge a PR immediately. Report implementation readiness separately.

Follow the steps in order, recording results cumulatively. On a termination condition, skip the rest and submit immediately. **Most no-go verdicts should land by the end of Step 2** — terminating early is a successful run, not an abandoned one.

---

## Execution Rules

**1. Primary source before secondary.** A search result, an issue title, a `WebFetch` summary, or a subagent report is a hypothesis. When one suggests something new ("this repo exposes lodash through its plugin API"), spend **exactly one** targeted command checking it against the code. Confirm or drop it. Never let a secondary source open an exploration branch.

**2. Do not install or build the target until Tier 2's gate is met — and it usually is not.** Tiers 0 and 1 need only the source on disk. Reaching for `install` early is what turns a ten-minute question into an hour.

```bash
command -v gh node npm; node -v                 # preflight, before Tier 0

command -v gtimeout pnpm yarn                   # only once the Tier 2 gate is met
<pkg-manager> install --no-frozen-lockfile      # NOT --ignore-scripts: skips workspace
<pkg-manager> -r run build                      # builds, and each missing dist/ costs a
                                                # failed test run
```

Shell notes: macOS has no `timeout` (use `gtimeout` or omit). Quote grep globs (`--include="*.ts"`) — zsh expands them otherwise. Edit `package.json` by parsing JSON, never by regex.

**3. Baseline in a second clone (Tier 2 only).** Clone twice: `base/` and `migrated/`. Never `git stash` to recover the baseline — it forces a reinstall each way.

**4. State the exit condition before searching.** "Find where lodash is used" has no end. "Get the distinct function list and file count, then stop" does.

**5. Track the five steps with TodoWrite, and write the provisional score down before entering Tier 2.** The gate is a number you committed to, not a feeling you had after starting the install.

---

## Step 1. Gate Check

Find every `package.json` (monorepo-aware). Check for `lodash`, `lodash-es`, or `lodash.*` per-method packages in `dependencies` / `devDependencies`.

- **Found** → Step 2
- **Not found** → terminate: "No lodash dependency detected"

---

## Step 2. Is It Worth Doing?

### 2-1. Project type

Classify from README and `package.json`: end-user application / npm-published library / Node-only build tool or server runtime. Confirm publish intent via `name`, `main`, `module`, `exports`, `files`, `private`.

Check for a plugin architecture or `peerDependencies`. If the project hands lodash instances to external plugins, a compatibility shim is needed instead of a swap (cf. Grafana).

### 2-2. Does lodash reach a shipped bundle?

**The question that outranks everything else: does this project's code get bundled at all?**

A dependency is not a bundled byte. Node-only projects — CLIs, bundlers, dev servers, test runners — run from `node_modules` and are never bundled for a browser, so "your users download fewer bytes" has **no recipient**. Signals: `engines.node` with no browser field or `browserslist`; a `bin` entry; README describes tooling that processes code rather than shipping into an app.

If Node-only, **install footprint is the only size metric that applies** — es-toolkit ships every build format (~3.9 MB unpacked vs. lodash's 1.4 MB, or 16 KB for a per-method package). Expect a regression, and carry no bundle-size argument into the report.

Also check:

- lodash in `dependencies` vs. `devDependencies` only
- Import paths: `src/` `lib/` → shipped. `test/` `examples/` `docs/` `scripts/` → not shipped
- Build config and `files` / `.npmignore` — confirm those paths reach the published artifact
- **Transitive lodash**: grep the lockfile. Other deps pulling lodash in is not a blocker, but it decides how the Tier 0 number may be reported

### 2-3. Import patterns and scope

| Pattern        | Example                                  | Impact                                                                                              |
| -------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Full           | `import _ from 'lodash'`                 | Pulls everything. Max benefit                                                                       |
| Named (CJS)    | `import { pick } from 'lodash'`          | Not tree-shakeable. High benefit                                                                    |
| Named (ESM)    | `import { pick } from 'lodash-es'`       | Already tree-shakes. Benefit is per-function size only                                              |
| Subpath        | `import pick from 'lodash/pick'`         | Already optimized. Smaller gain                                                                     |
| Per-method pkg | `import throttle from 'lodash.throttle'` | **Already optimal** — standalone, zero deps. Migration adds install weight. Strong negative signal   |
| Functional     | `import set from 'lodash/fp/set'`        | No drop-in es-toolkit API. Every call site needs a hand rewrite the codemod cannot do                |

Record: file and import count per pattern, distinct function count, top functions by frequency. Flag scope of 40+ files — large PRs stall in review.

### 2-4. Hard blockers

Any of `sortedUniq`, `sortedUniqBy`, `mixin`, `noConflict`, `runInContext` → **terminate immediately**: "Hard blocker found".

`lodash/fp` is **not** automatically a hard blocker. Its data-last, auto-curried, immutable behavior needs a manual rewrite at every call site: count those sites and report the count as unverified cost. Apply condition C only when a required direct substitution is absent from `missing_from_compat`, or a targeted code check proves the rewrite infeasible.

### 2-5. Early termination

Run Tier 0 first (seconds). A termination citing size must cite a measured size.

Terminate with **"No migration rationale"** if any one holds:

| #   | Condition                                                                                                                              | Why it ends the analysis                                     |
| --- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| A   | lodash only in `devDependencies`, or only under test/docs/example/script paths                                                         | Nothing reaches a user                                       |
| B   | Never browser-bundled **and** usage already minimal (per-method pkgs, a few subpath imports) **and** Tier 0 shows an install regression | No byte reaches a consumer, and the only metric that applies gets worse. The `react/metro` shape |
| C   | A required direct-substitution function is in Tier 0 `missing_from_compat`, and no small semantics-preserving rewrite exists            | Impossible, not merely unwise                                |

**Do not terminate** while any of these survive — they outlive the bundle argument: a large non-tree-shakeable surface (many functions via CJS named or namespace imports); lodash in `dependencies` of several published packages; an independent type or maintenance argument (`@types/lodash` as a separate dep, a `TODO: drop lodash` in the source); an install regression that is trivial against the existing tree.

**"The benefit reaches nobody" is a termination. "The benefit is small" is a low score.** Condition B needs all three clauses — terminating *solely* because a project is Node-only means you applied the gate wrong.

On termination: score in 0–29, label **Do not migrate**, one sentence naming the condition, and state that Steps 3–5 were skipped except for recording the final score. Do not research organizational signals to pad it.

```
2-1 Type: <App / Library / Node runtime> — Plugin exposure: <y/n>
2-2 Bundle: <Included / Not / devDep only> — Browser-bundled: <y/n> — Transitive: <y/n>
2-3 Scope: Full ×N / Named ×N / Subpath ×N / Per-method ×N — Files: N
           Distinct fns: N — Top: <list>
2-4 Hard blocker: <None / Found: fn>
2-5 Early exit: <None — continue / Terminated: A|B|C — reason>
Verdict: <Migration candidate / Not a target / No rationale — terminated>
```

---

## Step 3. Organizational Signals

**Write down your Step 2 technical verdict before reading any prior issue or PR.** A maintainer's rejection is persuasive; reading it first makes it impossible to tell whether the score is yours or theirs. Commit to a provisional number, look, then record whether prior art *changed* it or merely *confirmed* it.

- **Activity**: recent commits, issue response rate. Inactive repo → PRs get ignored
- **Prior issues/PRs** on lodash removal or es-toolkit — why didn't it land: abandoned, rejected, still open? Distinguish timing, scope, or an abandoned attempt from a reasoned technical objection. Check whether the objection still holds; an unanswered objection about compatibility or net benefit remains decisive. Record new evidence that answers it when available. An uncertain maintainer response or a difficult-looking PR alone does not negate a demonstrated benefit. If a proposal is already open, report its state and remaining work in this assessment
- **CLA**: check `CONTRIBUTING.md` and `.github/`. Adds contributor friction
- **lodash in the public API / plugins** (revisit 2-1) → a back-compat shim is needed

---

## Step 4. Measure and Verify

Two questions: **how many bytes does this move and who collects them**, and **how much risk does adopting it carry**. Do not benchmark runtime speed. Work in an isolated scratch clone, never the user's workspace.

| Tier                      | Cost                   | Entry condition                 |
| ------------------------- | ---------------------- | ------------------------------- |
| 0 — synthetic measurement | seconds                | always                          |
| 1 — codemod, no install   | seconds                | Tier 0 says candidate           |
| 2 — install, build, test  | **minutes to an hour** | the hard gate below, in writing |

### Tier 0 — Synthetic measurement

```bash
python {skill_directory}/scripts/measure_bundle_size.py <clone-dir>   # --json for machine output
```

Extracts distinct functions from **shipped** source (`--include-tests` to widen), recovers namespace-import functions via `_.fn()` call sites and per-method packages, runtime-checks each against `es-toolkit/compat` (catching gaps the 2-4 list misses), then bundles that exact set from both and reports minified + gzip delta plus install footprint.

**Read both numbers and decide which applies.** The bundle delta counts only if 2-2 established the code reaches a consumer bundle; for Node-only projects the install-footprint line *is* the measurement. Reporting a gzip saving nobody can collect is the most misleading thing this skill can do. This is the **lodash slice only**, not the app's total bundle — report it that way.

Treat `warnings` separately from `missing_from_compat`: a `lodash/fp` warning is unverified rewrite cost, not a condition C termination.

**With transitive lodash present, the delta is an upper bound, not a saving.** Another dependency keeps its own copy, so the slice can shrink while the shipped bundle grows. Tier 0 cannot tell which happened, and only a Tier 2 artifact comparison can. In that case: report it as "at most `<N>` B gzip, and only if lodash actually leaves the bundle"; name the dependency holding lodash from the lockfile (that finding may be worth more to the maintainer than the delta); deduct in Step 5; and if size is the *only* rationale, cap below 50. A number whose sign you cannot establish is worse than no number.

### Tier 1 — Codemod shape (no install)

Answers **"how big and how mechanical is the change?"** — the question that lowers a maintainer's perceived risk. Pure source transformation, so it costs seconds:

```bash
python {skill_directory}/scripts/migrate_lodash_imports.py <clone-dir> --dry-run
python {skill_directory}/scripts/migrate_lodash_imports.py <clone-dir> --write
git -C <clone-dir> diff --stat
```

**Do not install, build, or run tests here.** Record these three things in the assessment:

1. **Diff shape** — files changed, `+N/−N`, what fraction is one-line import rewrites.
2. **What the codemod could not do** — skipped files (`lodash/fp`, hard blockers) and every export the swap cannot satisfy: a type name es-toolkit does not export, a default-vs-named binding, a mock path still pointing at lodash (`vi.mock('lodash/uniqueId')`).
3. **Whether `lodash` can leave `package.json`** — it cannot while any shipped `lodash/fp` import remains.

**A clean codemod run is not verification.** It rewrites imports and executes nothing; a named export bound as a default fails at the call site, not at import time. Say "the diff is mechanical," never "it works."

### Tier 2 — Full verification (gated)

**Forbidden unless all four hold. Write them out before running a single command:**

1. Tiers 0–1 complete and a **provisional score of 70 or higher already recorded**.
2. A build, test, or artifact result would materially resolve a named uncertainty in the assessment.
3. No Step 2-5 termination fired, and Step 3 found no unanswered technical objection about compatibility or net benefit.
4. The project is browser-bundled, or the change touches enough shipped surface that a suite result would move a maintainer's answer.

**A no-go verdict never earns a Tier 2 run** — verifying a change you are about to argue against costs an hour and buys nothing. Under 70, stop at Tier 1 and write the report. This rule exists because it has been broken: a 15/100 verdict once carried a full 2,542-test before/after run whose own write-up admitted it was not there to justify anything.

For a provisional 70+, run Tier 2 when all gates hold and the environment permits it. If a gate or an external prerequisite prevents it, record the exact reason and the remaining verification work. Assess eligibility for the Step 5 strong-benefit exception; missing verification alone does not erase established value. Do not skip available verification merely to use that exception.

When the gate is met: preflight (Rule 2), clone twice (Rule 3), then run the full build and test suite across packages plus typecheck if one exists. **Capture the baseline run too** — "N passed" means nothing without a before-number. For browser-bundled projects, compare production artifacts from both clones: minified and gzip bytes, exact delta. With transitive lodash, inspect both artifacts for evidence lodash survived; if it remains and es-toolkit sits beside it, score the **net artifact delta**, not the Tier 0 slice — a net regression caps at 29. If the compat barrel breaks their production bundler, test function-level deep imports and record it as a required hand fix; a passing unit suite does not override a failed production build.

A real behavioral difference outranks every other signal — report it prominently and cap below 50.

**Recording**: raw numbers, not summaries — bytes before/after, diff size, and for Tier 2 tests before/after. Name the highest tier reached. An unreached tier is unmeasured, not passed.

---

## Step 5. Report

| Score  | Verdict label (verbatim) | Meaning                                                                                     |
| ------ | ------------------------ | ------------------------------------------------------------------------------------------- |
| 0–29   | **Do not migrate**       | Hard blocker; no applicable benefit; net regression in the claimed size benefit             |
| 30–49  | **Not recommended**      | No persuasive net benefit, or unresolved evidence against the migration                    |
| 50–69  | **Marginal**             | Some benefit, but insufficient evidence or benefit relative to the remaining work          |
| 70–89  | **Recommended**          | A defensible benefit worth pursuing; green Tier 2, or the strong-benefit exception at 70–79 |
| 90–100 | **Strongly recommended** | Narrow scope, active repo, Tier 2 green including a production build, minimal risk          |

**Start from who benefits, then adjust.** Set one base from 2-2, Tier 0, and source evidence, then apply the adjustments. If several bases apply, use the highest supported one; do not add them together.

| Base  | When                                                                                                                                                                    |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 75    | Tier 0 measured a gzip reduction in code reaching a **browser bundle**, outside the already-optimized small-delta case below — the project's users or downstream apps collect it on every load |
| 65    | Tier 0 measured a small per-function gzip reduction in browser-shipped code already tree-shaken (`lodash-es`, subpath)                                                   |
| 70    | Source evidence identifies substantial removable build/type-maintenance machinery, the maintainers who benefit, and why that gain outweighs measured costs; count the files, build steps, or dependency pairs removed |
| 40    | Shipped only to Node consumers, without the strong independent maintenance case above — install footprint is the applicable size metric                                 |
| 0–29  | A Step 2-5 termination: no recipient, hard blocker, or net regression in the claimed size benefit                                                                      |

**A small saving is not a weak benefit.** Bytes off a shipped bundle are collected by every user on every load, permanently, and they compound with every other trim the maintainer makes. Deduct for a benefit **nobody collects**, a delta whose **sign you cannot establish**, or numbers you did not measure — never for a real saving being modest.

Adjust from the base:

- **+10** a large non-tree-shakeable surface (namespace or CJS named imports), or lodash in `dependencies` of several published packages
- **+5** build machinery the swap deletes (module-format shims, dual `lodash` + `lodash-es` pairs, a separate `@types/lodash`)
- **−10** scope of 40+ files, or an active plugin/public-API exposure needing a shim
- **−10 to −20** documented organizational barriers: inactive repo, CLA, or concrete review constraints
- Caps still bind over everything above: 29 on a net regression in the claimed size benefit, below 50 on an upper-bound-only size rationale or a real behavioral difference

Apply deductions to documented work or barriers, not a prediction that maintainers will say no. Do not count the same burden twice as both scope and organizational friction, or add the +5 machinery bonus when that same evidence already supplied the 70-point maintenance base.

### Strong-benefit exception

Use this exception only when **all four** are supported in the report:

1. **A confirmed beneficiary and concrete gain.** Applicable measurements show a size reduction, or source evidence identifies substantial maintenance work the migration removes. Generic claims that es-toolkit is smaller, faster, newer, or has built-in types do not qualify. A synthetic delta is still a lodash-slice measurement, never a measured whole-app saving.
2. **A repository-specific case worth advocating.** Cite the source paths and measurements that make this change useful to this project's users or maintainers, and explain why the gain outweighs install growth and migration effort. The argument must stand without speculation about PR acceptance.
3. **A credible implementation path.** Enumerate remaining manual rewrites, compatibility work, and verification prerequisites with a plausible way to resolve them. Many files, feasible `lodash/fp` rewrites, timing, or unavailable build infrastructure can delay adoption without removing its value. An unknown solution to a required API gap does not qualify.
4. **No overriding negative evidence.** No hard blocker, actual behavioral regression, net size regression on the claimed size benefit, upper-bound-only size rationale, or unanswered technical objection from maintainers. All hard caps below still apply.

When all four hold, **restore 5–10 points deducted for implementation or review friction, at most once and never more than was deducted for those burdens**. If no such deduction was made, restore zero; the verification-cap exception can still apply. Explain which deduction is reduced and why the confirmed benefit warrants it. This adjustment recognizes worthwhile work despite current difficulty; it is not a second bonus for the same benefit, and it does not automatically raise every candidate to 70.

Use **5** when meaningful manual implementation or review work remains; use **10** when the deducted burden is predominantly mechanical changes or a bounded prerequisite. Choose from that evidence before checking whether the score crosses 70.

Then apply the scoring rules:

- **Without green Tier 2, the usual final cap is 69.** When all four strong-benefit conditions hold and Tier 2 could not be completed for the recorded reason, allow **70–79**, capped at 79. Never raise a calculated score below 70 just to enter that band. State **"Recommended — implementation verification pending"**, preserving **Recommended** as the verdict label. This is a recommendation to pursue the migration, not a claim that it is ready to merge.
- **80+ requires green Tier 2; 90+ also requires a production build and minimal remaining risk.** A mechanical diff, intended future tests, or an expected maintainer response cannot supply verification.
- **Compute the provisional score before Tier 2** using the same benefit evidence, adjustments, exception conditions, and hard caps, but without the verification-tier cap. Report both provisional and final numbers when they differ; explain changes caused by new evidence.
- **Green verification is not a benefit.** A passing suite proves the change is *safe*, not *worth doing*. A flawless Tier 2 run on a pointless change scores 0–29.
- **Score the benefit that reaches someone.** Name the users collecting bytes or the maintainers whose concrete work disappears. A Node-only project's browser-bundle saving is worth zero; assess an independent maintenance benefit on its own evidence.
- **Cap at 29 on a net regression in the claimed size benefit**; **cap below 50 when the delta is an upper bound and size is the only rationale**, unless Tier 2 settled the sign. Install growth alongside a browser-bundle or independent maintenance benefit is a cost to weigh explicitly, not automatically a net-value regression.
- State the base, additions, deductions, any restored points, and applied caps explicitly. Never drop a bare number.

Example: a browser library has a measured 5 KB gzip slice reduction, no transitive lodash, 48 files using CJS namespace imports, and six enumerated, feasible manual rewrites. Its base is 75, broad CJS usage adds 10, and scope subtracts 10. If all four exception conditions hold, restore 5 for a justified final calculation of 80. When a private registry blocks baseline installation, the verification cap makes the final score **79 — Recommended**, with verification pending. If transitive lodash instead makes that size-only case an upper bound, the exception is unavailable and the final score stays below 50.

**Lead with the verdict** — score, verbatim label, and one sentence naming the single decisive reason, before any step detail:

```
Verdict: 15 / 100 — Do not migrate
Metro is a Node.js bundler that is never bundled, so the byte saving reaches
nobody, while es-toolkit adds 3.2 MB to every install.
```

**Under 50, state a decision, not an impression.** Name the action ("Do not pursue this migration on the current evidence"), give the deciding reason first, and stop there: no consolation path or staged rollout. Do not soften a no-go with how clean or mechanical the change would be. Distinguish a supported technical objection from anticipated resistance; the latter alone cannot establish a no-go. Banned in a verdict sentence: *might*, *could be worth*, *arguably*, *some teams may*, *it depends*. Close with a specific falsifiable condition that would change the answer ("es-toolkit ships a slim Node entry under 100 KB"), not "revisit later."

**Sanity check — any "no" caps below 50:** is there a named beneficiary and concrete unit of gain; does that case survive the measured install-footprint cost; and has any prior technical objection about compatibility or net benefit been answered with new evidence (mark not applicable when there is none). Timing, scope concerns, or a predicted response alone are not such an objection.

---

## Response Language

Use the `response-language` argument (ISO 639-1) for the report. Default `en`.

## Required Report Structure

Use this exact top-level order so runs from different agents are comparable. Localize the prose to the requested language, but preserve the English verdict label in parentheses.

```markdown
can-migrate-es-toolkit — <owner/repo>

Analyzed: <branch/tag> @ <version-or-commit> (<recency>)

Result: <score> / 100 — <localized verdict> (<English verdict label>)

<one paragraph naming the decisive reason and the measured recipient or regression>

<explicit action: pursue the migration, resolve named prerequisites first, or do not pursue>

Readiness: <verified / implementation verification pending / blocked>

---

Step 1 — Gate Check
<result>

Step 2 — Is It Worth Doing?
<2-1 through 2-5, including the provisional verdict>

Step 3 — Organizational Signals
<results, or one line saying why skipped>

Step 4 — Measure and Verify
<Tier 0 and Tier 1 raw numbers. Name the highest tier reached; if Tier 2 was not
entered, state the gate condition that stopped it>

Step 5 — Final Score
<base, additions, deductions, restored points, caps, and the three sanity-check answers.
If using the strong-benefit exception, provide evidence for all four conditions, the
remaining implementation/verification work, and why the case merits active advocacy>
```

Do not rename `Step` to `Stage`, omit reached steps, or collapse the report into a short summary. When an early gate terminates the run, keep the same headings and mark all later steps as skipped with the gate reason.
