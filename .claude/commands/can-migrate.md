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

```
/can-migrate-es-toolkit <repository-url> [response-language]
```

- `repository-url`: GitHub repo URL. `response-language`: ISO 639-1 (`ko`, `ja`, …). Default `en`.

Follow the steps in order, recording results cumulatively. On a termination condition, skip the rest and submit immediately.

**Most no-go verdicts should land by the end of Step 2.** Steps 3–6 exist to evaluate a migration worth evaluating. Terminating early is a successful run, not an abandoned one.

---

## Execution Rules

These govern every step. Violating them is what turns a 10-minute run into an hour.

**1. Primary source before secondary.** A web search result, an issue title, a `WebFetch` summary, or a subagent report is a *hypothesis*, not a fact — they are written by small models or by strangers. When one suggests something new (e.g. "this repo exposes lodash through its plugin API"), spend **exactly one** targeted command checking it against the code. Confirm or drop it. Never let a secondary source open a multi-call exploration branch.

**2. Preflight the environment once, before Tier 1.** Environment failures discovered one at a time each spawn their own detour. Get them all in one call:

```bash
command -v gh gtimeout pnpm yarn npm node; node -v          # assume nothing is installed
<pkg-manager> install --no-frozen-lockfile                   # NOT --ignore-scripts: it skips
                                                             # workspace builds, and every
                                                             # missing dist/ costs a failed test run
<pkg-manager> -r run build                                   # prebuild all workspace packages
```

Shell notes: macOS has no `timeout` (use `gtimeout` or omit). Quote grep globs (`--include="*.ts"`) — zsh expands them otherwise. Edit `package.json` by parsing JSON, never by regex — deleting a key with `sed`/`re.sub` leaves a trailing comma.

**3. Baseline in a second clone.** Clone twice: `base/` and `migrated/`. Never use `git stash` to recover the baseline — it forces a reinstall each way and invites stash/install desync.

**4. State the exit condition before searching.** "Find where lodash is used" has no end. "Get the distinct function list and file count, then stop" does.

**5. Track the six steps with TodoWrite.** Gates are only enforceable if "where am I" is visible.

**6. Budget the verification tier before entering it.** Decide what you will run. Widening mid-run is a decision to make explicitly, not something to drift into.

---

## Step 1. Migration Gate Check

Find every `package.json` (monorepo-aware). Check for `lodash`, `lodash-es`, or `lodash.*` per-method packages in `dependencies` / `devDependencies`.

- **Found** → Step 2
- **Not found** → terminate: "No lodash dependency detected"

---

## Step 2. Assess Migration Target

### 2-1. Project type (README + package.json)

Classify: end-user application / npm-published library / Node-only build tool or server runtime. Confirm publish intent via `name`, `main`, `module`, `exports`, `files`, `private`.

Check for a plugin or extension architecture, or `peerDependencies`. If the project hands lodash instances to external plugins, a compatibility shim is needed instead of a swap (cf. Grafana).

### 2-2. Does lodash reach a shipped bundle?

**The question that outranks everything else here: does this project's code get bundled at all?**

A dependency is not a bundled byte. Node-only projects — CLIs, bundlers, dev servers, test runners — run from `node_modules` and are never bundled for a browser. For those the "your users download fewer bytes" argument has **no recipient**.

Node-only signals: `engines.node` with no browser field or `browserslist`; a `bin` entry; README describes tooling that *processes* code rather than shipping into an app.

If Node-only, **install footprint is the only size metric that applies**, and es-toolkit ships every build format (~3.9 MB unpacked vs. lodash's 1.4 MB, or 16 KB for a per-method package). Expect a regression. Do not carry a bundle-size argument into the report.

Also check:
- lodash in `dependencies` vs. `devDependencies` only
- Import paths: `src/` `lib/` → shipped. `test/` `__tests__/` `examples/` `docs/` `scripts/` → not shipped
- Build config and `files` / `.npmignore` — confirm those paths reach the published artifact
- **Transitive lodash**: grep the lockfile. If other deps pull lodash in, migrating this repo won't remove it from `node_modules` — not a blocker, but report it

### 2-3. Import patterns and scope

| Pattern | Example | Impact |
|---|---|---|
| Full | `import _ from 'lodash'` | Pulls everything. Max benefit |
| Named (CJS) | `import { pick } from 'lodash'` | Not tree-shakeable. High benefit |
| Named (ESM) | `import { pick } from 'lodash-es'` | Already tree-shakes. Benefit is per-function size only |
| Subpath | `import pick from 'lodash/pick'` | Already optimized. Smaller gain |
| Per-method pkg | `import throttle from 'lodash.throttle'` | **Already optimal** — standalone, zero deps. Migration adds install weight and removes almost nothing. Strong negative signal unless browser-bundled |

Record: file and import count per pattern, distinct function count, top functions by frequency. Flag scope of 40+ files — large PRs stall in review.

### 2-4. Hard blockers

Any of `sortedUniq`, `sortedUniqBy`, `mixin`, `noConflict`, `runInContext` → **terminate immediately**: "Hard blocker found".

### 2-5. Early termination

Run Tier 0 first (seconds). A termination citing size must cite a *measured* size.

Terminate with **"No migration rationale"** if **any one** holds:

| # | Condition | Why it ends the analysis |
|---|---|---|
| A | lodash only in `devDependencies`, or only under test/docs/example/script paths | Nothing reaches a user |
| B | Never browser-bundled **and** usage already minimal (per-method pkgs, a few subpath imports) **and** Tier 0 shows an install regression | No byte reaches a consumer, and the only applicable metric gets worse. The `react/metro` shape |
| C | A function in use is missing from `es-toolkit/compat` | Impossible, not merely unwise |

**Do not terminate** if any of these survive — they outlive the bundle argument:

- Large non-tree-shakeable surface (many functions via CJS named or namespace imports) — real parse and resolve weight even in Node
- lodash sits in `dependencies` of **several published packages** — every downstream install carries it
- Independent type or maintenance arguments: `@types/lodash` is a separate untyped dep, or the source carries `TODO: drop lodash`
- The install regression is proportionally trivial against the existing dependency tree

**"The benefit reaches nobody" is a termination. "The benefit is small" is a low score.** Condition B needs all three clauses so a Node-only project with a large unoptimized surface still gets a full analysis. Terminating *solely* because a project is Node-only means you applied the gate wrong.

On termination: score in the 0–29 band, label **Do not migrate**, one sentence naming the condition. State that Steps 3–6 were skipped. Do not research organizational signals to pad it.

### Verdict template

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

**Write down your Step 2 technical verdict before reading any prior issue or PR.** A maintainer's rejection is persuasive; reading it first makes it impossible to tell whether the score is yours or theirs. Commit to a provisional number, then look, then record whether prior art *changed* it or merely *confirmed* it. Both go in the report.

- **Activity**: recent commits, issue response rate. Inactive repo → PRs get ignored
- **Prior issues/PRs** on lodash removal, dependency cleanup, or es-toolkit. If found, why didn't it land — abandoned, rejected, still open?
  - **A prior attempt closed with a reasoned technical objection is decisive, not a data point.** Check whether that objection still holds today — es-toolkit's install size grows over time, so an old size-based rejection may have gotten *stronger*. Re-proposing without new evidence answering it is the same pitch a second time, not a contribution
  - Note if the earlier proposer was affiliated with es-toolkit and how maintainers reacted. If so, disclosure in Step 6 is mandatory
- **CLA**: check `CONTRIBUTING.md` and `.github/`. Adds contributor friction
- **lodash in the public API / plugins** (revisit 2-1) → a back-compat shim is needed

---

## Step 4. Measure and Verify

Steps 1–3 show migration is *possible*; they cannot show what it *costs* or whether it *works*. This step answers the two questions maintainers ask: **how many bytes do consumers save**, and **does the suite still pass**.

Do not benchmark runtime speed. Work in an isolated scratch clone — never the user's workspace. Stop at whichever tier answers the question.

### Tier 0 — Synthetic (always; seconds)

```bash
python {skill_directory}/scripts/measure_bundle_size.py <clone-dir>   # --json for machine output
```

Extracts distinct functions from **shipped** source (`--include-tests` to widen), recovers namespace-import functions via `_.fn()` call sites and per-method packages, **runtime-checks every function against `es-toolkit/compat`** (catches gaps the 2-4 list misses), then bundles that exact set from both and reports minified + gzip delta plus install footprint.

**Read both numbers and decide which applies.** The bundle delta only counts if 2-2 established the code reaches a consumer bundle. For Node-only projects the install-footprint line *is* the measurement. Reporting a gzip saving nobody can collect is the most misleading thing this skill can do.

This is the **lodash slice only** — not the app's total bundle. Report it that way.

Tier 0 alone caps the score in the 70s. A function missing from compat is a 2-4 hard blocker.

### Tier 1 — Codemod smoke test (~1 min)

Only when Tier 0 says candidate and you intend to recommend it. Preflight first (Execution Rule 2).

1. `{skill_directory}/scripts/migrate_lodash_imports.py <clone-dir>` — `--dry-run`, then `--write`
2. Swap `lodash`/`lodash-es` → `es-toolkit` in every affected `package.json` (parse JSON, don't regex), install
3. Run the test suite of the **single package with the most lodash imports**

**A clean dry-run is not verification.** It counts import statements; it executes nothing. A named export bound as a default, or a dropped alias, fails at runtime, not at import time.

Record every hand fix the codemod missed — that is the honest cost, and maintainers will hit it too. Common: mock paths still pointing at lodash (`vi.mock('lodash/uniqueId')`), stale or newly-necessary `@ts-expect-error`.

### Tier 2 — Full verification (only when drafting in Step 6)

Full build + full test suite across packages; run typecheck if it exists. **Capture the baseline run too** (Execution Rule 3) — "N passed" only means something against a before-number. Report exact counts.

A real behavioral difference outranks every other signal — report it prominently and cap the score below 50. But separate two things:

- **Semantic** — same input, different result. Unfixable without changing call sites. Caps below 50.
- **Platform floor** — identical behavior, but a newer JS builtin raises the minimum browser. `es-toolkit/compat` uses `Object.hasOwn` (Safari 15.4+, Chrome 93+) in `get`, `set`, `pick`, `omit`, `merge`, `isEqual`, `cloneDeep`, `union`, `uniqBy`, `mapValues`, `flatMap`, `findLastIndex` and others; lodash uses none. No cap, but a **mandatory prominent caveat plus a mitigation** — only maintainers can move their documented baseline.

A green suite cannot detect a platform-floor regression — tests run in Node, which has every builtin. Check explicitly:

```bash
for f in <functions>; do
  echo "import { $f } from 'es-toolkit/compat'; console.log($f);" > e.mjs
  esbuild e.mjs --bundle --format=esm --outfile=o.js
  grep -c "Object\.hasOwn" o.js
done
```

Compare against `browserslist`, `.browserslistrc`, README, or docs. The main `es-toolkit` entry usually hits far fewer than `compat` — if a function exists in both, prefer main and re-check.

### Recording

Raw numbers, not summaries: bytes before/after, tests before/after, diff size (`files changed, +N/-N`). State which tier you reached — an unreached tier is unmeasured, not passed.

---

## Step 5. Report

| Score | Verdict label (verbatim) | Meaning |
|---|---|---|
| 0–29 | **Do not migrate** | Hard blocker; lodash never reaches users; benefit doesn't apply; net size regression |
| 30–49 | **Not recommended** | Possible, but major organizational barriers or very large scope |
| 50–69 | **Marginal** | Feasible, limited benefit, or measurement stopped at Tier 0 |
| 70–89 | **Recommended** | Good conditions with a **measured** benefit (Tier 0 min, Tier 1 green) |
| 90–100 | **Strongly recommended** | Narrow scope, active repo, Tier 2 green, measured gain, minimal risk |

- 70+ requires Step 4 measurement. Static analysis caps at 69 however clean.
- Always state the deductions explicitly. Never drop a bare number.
- **Green verification is not a benefit.** A passing suite proves the change is *safe*, not *worth doing*. A flawless Tier 2 run on a pointless change scores 0–29, not 70–89.
- **Score the benefit that reaches someone.** Name who collects it. "Nobody, it's never bundled" makes the number worth zero.
- **Cap at 29 when the net size effect is negative.**

### Lead with the verdict

Open with score, verbatim label, and **one sentence naming the single decisive reason** — before any stage detail.

```
Verdict: 15 / 100 — Do not migrate
Metro is a Node.js bundler that is never bundled, so the byte saving reaches
nobody, while es-toolkit adds 3.2 MB to every install.
```

### Say no without hedging

Under 50, state a decision, not an impression:

- **Name the action**: "Do not open an issue or PR."
- **Give the deciding reason first.** Extra reasons must not dilute it.
- **Do not soften a no-go with verification results.** "All 2,542 tests pass" belongs in Step 4. A perfect diff of a pointless change is still pointless — say that.
- **No consolation path** — no "if you still want to," no staged rollout, no draft "just in case."
- **Do not treat maintainer resistance as an obstacle to route around.** If they declined for a sound reason, the finding is that they were right.
- Banned in a verdict sentence: *might*, *could be worth*, *arguably*, *some teams may*, *it depends*.

Then give a specific, falsifiable condition that would change the answer ("es-toolkit ships a slim Node entry under 100 KB") — not "revisit later."

### Sanity check — any "no" caps below 50

1. Who specifically is better off, and in what unit?
2. Does that survive the install-footprint number?
3. If a maintainer already declined, what new evidence answers their stated objection?

---

## Step 6. Draft Issue

**Condition**: score ≥ 70, or < 70 with genuine merit.

**Skip entirely under 50.** No draft "for reference," no shortened version, no sketch. One line saying it was skipped and why. Polishing a proposal you just argued against is the most likely way this skill misleads someone.

**If a PR or issue already proposes this, draft nothing** — even at 90. Report its state and what it's blocked on, and recommend *supporting* it: a review, a reproduction of its numbers, a fix for the objection raised.

### Hard rule: 20 lines maximum

Count them. A long proposal reads as a pitch and gets skimmed; a short one with real numbers gets read. Cut in this order: prose → tables → adjectives. **No tables** — this format is too short to earn one. Numbers inline, bolded.

Every draft carries at least one caveat (surviving transitive lodash, install growth, diff size, hand fixes). Stating it unprompted is what separates a proposal from a pitch.

### Template A — issue / PR description

````markdown
## Summary

Replaces `lodash` with `es-toolkit/compat` across <N> files in <M> packages.
Drop-in: same API, same behavior, no call-site changes.

- **Bundle size**: `<artifact>` gzip **<before> → <after>** (−<X> kB, −<Y>%)
- **Dependencies**: drops `lodash` and `@types/lodash` — es-toolkit ships its own types
- **Maintenance**: es-toolkit is actively maintained; already used by Storybook and Recharts

```diff
- import { cloneDeep } from 'lodash'
+ import { cloneDeep } from 'es-toolkit/compat'
```

## Test plan

`<command>` → **<N> passed, 0 failed** — identical to the pre-change baseline.

Caveats: <transitive lodash survives / install +<X> MB / <N>-file diff>.
````

### Template B — reply to a maintainer's pushback

Only when Step 3 says you have **new evidence answering their stated objection**. Without it, do not reply — re-pitching is not a contribution.

````markdown
Thanks for the thoughtful response — the concern about <their exact objection> is fair.
A few numbers that may shift the cost-benefit:

**1. <Benefit> for <who>**
<before> → <after> (**−<Y>%**), affecting <the specific consumer>.

**2. Zero-risk swap** — same API, same behavior, <N> tests pass unchanged.

```diff
- import { throttle } from 'lodash'
+ import { throttle } from 'es-toolkit/compat'
```

**3. <Maintenance / type surface / dependency count>**
<one concrete sentence>. <Caveat you are not hiding.>

Fair enough if this still reads as unnecessary churn — but would you be open to
reconsidering? Thanks for maintaining <project>.
````

### Tone

Friendly, respectful, a suggestion rather than a demand. Persuasive without reading as promotional for es-toolkit. Disclose any es-toolkit affiliation. Adjust for Step 3 signals: low activity → gentler, acknowledge the maintenance load; CLA → mention it honestly; prior failed attempts → acknowledge and respect that context.

---

## Response Language

Use the `response-language` argument (ISO 639-1). Default `en`. **The 20-line cap and both templates apply in every language** — issue drafts stay in English unless the repository's own issues are not.
