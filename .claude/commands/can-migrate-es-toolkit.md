---
name: can-migrate-es-toolkit
description: >
  Analyze a GitHub repository to decide whether replacing its lodash dependency with es-toolkit is worth doing and possible,
  and draft the issue proposing it. Triggers on "/can-migrate-es-toolkit", "can this repo migrate from lodash",
  "check lodash migration", "es-toolkit migration feasibility", or any request to assess a lodash-to-es-toolkit swap.
---

# can-migrate-es-toolkit

```
/can-migrate-es-toolkit <repository-url> [response-language]
```

- `repository-url`: GitHub repo URL. `response-language`: ISO 639-1 (`ko`, `ja`, …). Default `en`.

Two questions, in this order: **is the migration worth doing** (who collects a benefit, how big), then **is it possible** (what blocks it, how large the change, whether it holds together). The first gates the second — a migration nobody benefits from is not worth checking the feasibility of.

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

**5. Track the six steps with TodoWrite, and write the provisional score down before entering Tier 2.** The gate is a number you committed to, not a feeling you had after starting the install.

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

On termination: score in 0–29, label **Do not migrate**, one sentence naming the condition, and state that Steps 3–6 were skipped. Do not research organizational signals to pad it.

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
- **Prior issues/PRs** on lodash removal or es-toolkit — why didn't it land: abandoned, rejected, still open? **One closed with a reasoned technical objection is decisive, not a data point.** Check whether it still holds — es-toolkit's install size grows over time, so an old size-based rejection may have gotten *stronger*. Re-proposing without new evidence is the same pitch twice. If the earlier proposer was affiliated with es-toolkit, disclosure in Step 6 is mandatory
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

**Do not install, build, or run tests here.** Record three things, all of which belong in the Step 6 draft:

1. **Diff shape** — files changed, `+N/−N`, what fraction is one-line import rewrites.
2. **What the codemod could not do** — skipped files (`lodash/fp`, hard blockers) and every export the swap cannot satisfy: a type name es-toolkit does not export, a default-vs-named binding, a mock path still pointing at lodash (`vi.mock('lodash/uniqueId')`).
3. **Whether `lodash` can leave `package.json`** — it cannot while any shipped `lodash/fp` import remains.

**A clean codemod run is not verification.** It rewrites imports and executes nothing; a named export bound as a default fails at the call site, not at import time. Say "the diff is mechanical," never "it works."

### Tier 2 — Full verification (gated)

**Forbidden unless all four hold. Write them out before running a single command:**

1. Tiers 0–1 complete and a **provisional score of 70 or higher already recorded**.
2. You intend to draft an issue in Step 6.
3. No Step 2-5 termination fired, and Step 3 found no unanswered maintainer rejection.
4. The project is browser-bundled, or the change touches enough shipped surface that a suite result would move a maintainer's answer.

**A no-go verdict never earns a Tier 2 run** — verifying a change you are about to argue against costs an hour and buys nothing. Under 70, stop at Tier 1 and write the report. This rule exists because it has been broken: a 15/100 verdict once carried a full 2,542-test before/after run whose own write-up admitted it was not there to justify anything.

When the gate is met: preflight (Rule 2), clone twice (Rule 3), then run the full build and test suite across packages plus typecheck if one exists. **Capture the baseline run too** — "N passed" means nothing without a before-number. For browser-bundled projects, compare production artifacts from both clones: minified and gzip bytes, exact delta. With transitive lodash, inspect both artifacts for evidence lodash survived; if it remains and es-toolkit sits beside it, score the **net artifact delta**, not the Tier 0 slice — a net regression caps at 29. If the compat barrel breaks their production bundler, test function-level deep imports and record it as a required hand fix; a passing unit suite does not override a failed production build.

A real behavioral difference outranks every other signal — report it prominently and cap below 50.

**Recording**: raw numbers, not summaries — bytes before/after, diff size, and for Tier 2 tests before/after. Name the highest tier reached. An unreached tier is unmeasured, not passed.

---

## Step 5. Report

| Score  | Verdict label (verbatim) | Meaning                                                                                     |
| ------ | ------------------------ | ------------------------------------------------------------------------------------------- |
| 0–29   | **Do not migrate**       | Hard blocker; lodash never reaches users; benefit doesn't apply; net size regression        |
| 30–49  | **Not recommended**      | Possible, but major organizational barriers or very large scope                             |
| 50–69  | **Marginal**             | Feasible, with a measured benefit that reaches someone — but stopped at Tier 1, so untested |
| 70–89  | **Recommended**          | Good conditions, a measured benefit, and a green Tier 2                                     |
| 90–100 | **Strongly recommended** | Narrow scope, active repo, Tier 2 green including a production build, minimal risk          |

- **70+ requires a completed Tier 2.** Tiers 0–1 cap at 69 however clean the code looks. Never award 70+ on the intention to verify.
- **Green verification is not a benefit.** A passing suite proves the change is *safe*, not *worth doing*. A flawless Tier 2 run on a pointless change scores 0–29.
- **Score the benefit that reaches someone.** Name who collects it. "Nobody, it's never bundled" makes the number worth zero.
- **Cap at 29 on a net size regression**; **cap below 50 when the delta is an upper bound and size is the only rationale**, unless Tier 2 settled the sign.
- State deductions explicitly. Never drop a bare number.

**Lead with the verdict** — score, verbatim label, and one sentence naming the single decisive reason, before any step detail:

```
Verdict: 15 / 100 — Do not migrate
Metro is a Node.js bundler that is never bundled, so the byte saving reaches
nobody, while es-toolkit adds 3.2 MB to every install.
```

**Under 50, state a decision, not an impression.** Name the action ("Do not open an issue or PR"), give the deciding reason first, and stop there: no consolation path, no staged rollout, no draft "just in case". Do not soften a no-go with how clean or mechanical the change would be, and do not treat maintainer resistance as an obstacle to route around — if they declined for a sound reason, the finding is that they were right. Banned in a verdict sentence: *might*, *could be worth*, *arguably*, *some teams may*, *it depends*. Close with a specific falsifiable condition that would change the answer ("es-toolkit ships a slim Node entry under 100 KB"), not "revisit later."

**Sanity check — any "no" caps below 50:** who specifically is better off and in what unit; does that survive the install-footprint number; and if a maintainer already declined, what new evidence answers their objection.

---

## Step 6. Draft Issue

**Condition**: score ≥ 50. **Skip entirely under 50** — no draft "for reference," no sketch, one line saying it was skipped and why. **If a PR or issue already proposes this, draft nothing**: report its state and what it's blocked on, and recommend supporting it.

This is one person asking another person a question. Warm, suggesting rather than telling, specific enough that it could only have been written about this repository.

- **15 lines maximum**, blank lines included. Count them.
- **No headers, no bullets, no tables.** Prose only.
- **Open with the ask and the link**: "How about migrating from lodash to [es-toolkit](https://github.com/toss/es-toolkit)?"
- **Introduce es-toolkit in three lines or fewer**, leading on bundle size and speed.
- **Prove the benefit with one number, inside a sentence.** No breakdown, no second and third statistic — one figure a maintainer can hold in their head.
- **Name who gains**: their users, concretely.
- **Let a small number carry its weight.** A modest delta is not a weak argument — it is collected on every install, every build, and every page load, and it stacks with the other small wins that keep a project lean. Attach that as one clause to the number, in the maintainer's own terms. One clause, not a paragraph, and never inflate the figure to make the point.
- **Say what adopting costs**, in one sentence, from the tier you reached. This is what turns a suggestion into something a maintainer can say yes to.
- **Close warmly, on a question.**

**Never disparage lodash.** The maintainer chose a well-built, widely trusted library on purpose. Nothing is bloated, outdated, legacy, or slow. The frame is "es-toolkit may be a better fit here," never "lodash is bad."

Do not:

- **Claim their project gets faster.** Describing es-toolkit's own characteristics is fine — the link lets them check. Asserting a measured speedup in *their* code is not.
- **Claim more than the tier you reached.** Tier 1 ran nothing: say the diff is mechanical and note you haven't run their suite. Only a completed Tier 2 earns "I ran the tests," with the before-number beside it.
- **Present an upper bound as a saving.** With transitive lodash, say the bytes leave only if lodash leaves, and name the dependency holding it. The maintainer owns the build and will check.
- **Call it "CJS lodash" if they use `lodash-es`.** Describing their codebase wrong in the first sentence loses them immediately.
- **Refer to a previous attempt.** If Step 3 turned up an earlier issue or PR on this — closed, rejected, or abandoned — the draft never mentions it: no "I saw #123 didn't land," no "unlike the earlier attempt," no summary of why it stalled. That turns the message into a re-litigation of a settled thread instead of a proposal. Prior art decides the score and the evidence you bring; it stays out of the text. Write it so it reads to someone meeting the idea for the first time.
- **Cite es-toolkit adoption by other projects** — it reads as marketing. Disclose any affiliation.

```markdown
How about migrating from lodash to [es-toolkit](https://github.com/toss/es-toolkit)?

es-toolkit is a modern utility library that covers the same functions through its
`es-toolkit/compat` entry, with noticeably smaller bundles and faster implementations.
It also ships its own TypeScript types, so no separate `@types` package is needed.

I noticed <the specific thing you found in their repo> — <one clause on why it happens>.
Swapping to es-toolkit brings that slice from <before> to <after> gzip, about <Y>%
smaller — small on its own, but it's carried by every app built on <repo>, on every
build, and it's the kind of trim that adds up.

<the cost sentence — by tier, below>

I'd be glad to open a PR if that sounds useful. What do you think?
```

Only the fourth paragraph changes with the tier reached:

```markdown
Tier 1 — The change itself is small: <N> files, almost all one-line import rewrites,
plus <the one manual fix>. I haven't run your suite, so that's worth a check on your side.

Tier 2 — The change itself is small: <N> files, almost all one-line import rewrites,
plus <the one manual fix>. I ran your test suite after applying it — <N> passing,
identical to the baseline before the change.
```

---

## Response Language

Use the `response-language` argument (ISO 639-1) for the report. Default `en`.

**Step 6 drafts stay in English** unless the repository's own issues are not — the message goes to maintainers, not to the user. All Step 6 rules apply in whatever language it ends up in.

## Required Report Structure

Use this exact top-level order so runs from different agents are comparable. Localize the prose to the requested language, but preserve the English verdict label in parentheses.

```markdown
can-migrate-es-toolkit — <owner/repo>

Analyzed: <branch/tag> @ <version-or-commit> (<recency>)

Result: <score> / 100 — <localized verdict> (<English verdict label>)

<one paragraph naming the decisive reason and the measured recipient or regression>

<explicit action: open or do not open an issue/PR>

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
<deductions and the three sanity-check answers>

Step 6 — Issue Draft
<draft, existing issue/PR state, or one line saying why skipped>
```

Do not rename `Step` to `Stage`, omit reached steps, or collapse the report into a short summary. When an early gate terminates the run, keep the same headings and mark all later steps as skipped with the gate reason.
