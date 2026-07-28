# constraints.md — the acceptance gate for *The Reallocation Engine, Audited*

Source of truth for what "done" means on this assignment (INFO 7375, 100 pts).
**Run this gate after every plan step.** A step is not complete because the code
runs; it is complete when the boxes it touches are checkable by someone else.

Tool under construction: `tools/effort-reallocator/` — reallocates next week's
**application-slot budget** (people/time) across companies.
Book anchor: **Ch.2** (reallocation principle), **Ch.11 §"Why liveness and timeline
are multipliers"** (composite + 0.3 threshold), **Ch.15** (skip-rate dial, 3-3-2).
Report: `Kurlekar_Atharva_ReallocationEngine.md`. Journal: `FRICTIONAL-JOURNAL.md`.

---

## 0. How to use this file

After each plan todo:

1. Re-read **§1 Deduction guards**. Any unchecked box there is a stop-work item.
2. Tick only the §2 criteria the step actually produced, and write the **evidence**
   (file path, command, or line) next to it. A tick with no evidence is a claim,
   and per `SNICKERDOODLE.md` a claim without evidence is a violation, not progress.
3. Run **§4 Verification commands**. All must pass before the step is called done.
4. Append one line to **§6 Step sign-off log**.

Rule of the house: if a box cannot be honestly ticked, say so in the report. A
documented gap scores; a silent one is the failure this course is built to catch.

---

## 1. Deduction guards (blocking — check every step)

These are not points. These are subtractions, and each one is larger than most
components. Verify all six on every pass.

- [x] **Frictional Journal prediction exists and is timestamped BEFORE the first
      line of tool code** (−10 if missing). Must state: expected hardest failure,
      expected causal validity, confidence **as a number**. Never edited after the
      fact — corrections go in the reflection.
      → *Evidence:* `FRICTIONAL-JOURNAL.md` Entry 1 timestamped **2026-07-27 14:54 EDT**;
      hardest failure, causal validity, and confidence **28/100** filled in.
- [x] **Frictional Journal reflection written immediately after the build** (−10):
      what actually happened, where the prediction was wrong, what that says about
      calibration.
      → *Evidence:* Entry 2 timestamped **2026-07-27 20:05 EDT**; §§1–3 and 5 filled;
      §4 factual log retained from committed run artifacts.
- [x] **AI Use Disclosure present and "What the AI could not do" is a SPECIFIC
      instance** (−10). Category claims ("AI lacks context") fail. It must name one
      concrete judgment call requiring domain knowledge, values, or accountability
      — e.g. a confounder only I can see because I lived the case.
      → *Evidence:* report § *AI Use Disclosure*, all five fields. The specific
      instance: the model could not know **Amgen's 0.000 was a Workday adapter gap,
      not a hiring signal** — Amgen appears identically to a genuinely closed role, and
      the fact lives in `portals.yml` (`enabled: false`) plus having sat through the
      earlier run. `neutral-flagged` exists as a policy *because* of that lived failure.
      Second instance: choosing to starve early-stage firms is a values call about my
      own week against an OPT clock.
- [x] **Video explainer 5–8 min exists** (−10), aimed at a non-specialist: what it
      reallocates, the most surprising failure, what a deployer needs beyond accuracy.
      → *Evidence:* `youtube/effort-reallocator/effort-reallocator.mp4` (~5:54);
      `VIDEO-OUTLINE.md` / `VIDEO-AI-BRIEF.md`; says "where I would not trust this tool"
      aloud.
- [x] **Tool runs and is reproducible from a clean clone of the repo** (−15).
      Zero-install: stdlib Python only; `README.md` states the exact command; the
      committed `examples/` inputs are sufficient (no private data required).
      → *Evidence:* `python3 tools/effort-reallocator/reallocate.py all` — stdlib only
      (no `pip install`, no network); inputs are the committed public CSV, the tracked
      `data/BLS/compact/soc_occupation_compact.csv` (CLI refuses if missing; exit 2), plus
      synthetic `examples/`; Monte Carlo seed fixed at 20260727. **Proven:** clean clone of
      `origin/mode/atharva-kurlekar-erp-to-ai` → `all` exit 5, 38 tests OK. See
      `logs/RUN_LOG.md` recovery entry. `runs/2026-07-27/README.md` gives the commands.
- [x] **No resource moves without the hard stop** (−15). `execute` refuses without
      `--approve --approver --reason`. Slots are my own irreplaceable application
      time against an OPT clock — the gate is non-negotiable and justified in writing.
      → *Evidence:* `runs/2026-07-27/terminal-02-execute-refused.txt` — **exit 4, 10
      blocks, nothing moved**, on the engine's own recommendation. No `--force` flag
      exists. Justification in the report's delegation-map section: this engine commits
      *a resource* (application time), spends no money, changes no one's access.
- [x] **No causal claim asserted without interrogation** (−10). Every "moving slots
      to B improves yield" statement in code comments, report, and video carries its
      confounders or an explicit "this is correlational."
      → *Evidence:* report §5 — six named confounders, the verdict *"this engine
      reallocates on correlation dressed as causation"*, and the refusal to let the one
      interventional component (liveness) launder the rest, since liveness was itself
      unverified for six of eight destinations. The `expected_gain` field carries a
      `caveat` string in every artifact; `engine/uncertainty.py` and
      `engine/allocate.py` carry the same warning in comments; video beat 8 states it.

---

## 2. Core components (80 pts) — acceptance criteria

### 1. Working reallocation tool — 12 pts

- [x] Ingests the real dataset: `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv`
      (30,369 rows) + `data/BLS/compact/soc_occupation_compact.csv`.
- [x] Output is a concrete **move**: quantity **Q** slots from **A** to **B** — not a
      ranked list, not a score dump. The diff versus the baseline allocation is explicit.
- [x] **Uncertainty attached to the move itself**, not just to the inputs: interval +
      move-stability share across Monte Carlo draws.
- [x] Objective stated in **one plain sentence** in both `README.md` and the report,
      with **what it leaves out** named immediately after.
- [x] A person could run it: single entry point, `--help` works, non-zero exit codes
      are meaningful, it is not a notebook of disconnected cells.
- [x] Refuses rather than guesses when inputs are missing (exit code, no output file).

Evidence: 8 moves in `runs/2026-07-27/default/proposal.md` (e.g. *1 slot ACME ANALYTICS
LLC → MAPLEBEAR INC*, 80% CI 1.0–1.0, stability 100.0%), each with a `why leave` / `why
arrive`. Per-move stability and an 80% CI on Q come from 2,000 MC draws (seed 20260727)
over four named sources; **3 of 8 moves reported as "not distinguishable from no change"**.
Expected gain +0.121 [+0.117, +0.123] with the optimiser's curse measured at 6.1%.
Exit codes: 0 ok · 2 missing input (no output file) · 4 hard stop · 5 gate blocking, all
observed in the four committed transcripts. 37 unit tests pass, including Ch.11 parity
(0.44625 Apply / 0.1785 Skip) against `data/examples/role-scores.json`.

### 2. Data validation & the GIGO gate — 10 pts

- [x] **Hidden assumptions named** — what the dataset assumes that is not true.
      Minimum bar for this dataset: *absence of an H-1B record is not evidence of
      non-sponsorship* (96.8% of rows have no H-1B fields, per
      `data/verified/atharva-kurlekar-funded-systems-analyst/validation_report.json`).
      Missingness is **not** MCAR and the gate must not read missing as zero.
      → **Note the correction:** this tool's own gate measures **94.9% (28,812 of
      30,369)** on the full dataset, not 96.8%. The 96.8% figure came from a
      differently-filtered slice in the earlier report. The bias audit was quoting the
      inherited number until the gate contradicted it; it now reads the measured rate.
- [x] **A quality standard a human could check**, written as discrete named checks
      (not prose): required fields, rate-with-null-denominator, 0–1 vs 0–100 scale
      confusion, wage-leaked-into-title artifact, funding-date vintage, entity-
      resolution collisions.
- [x] **Documented rejections**: `rejects.json` with a reason code per rejected row
      and a count per code; the gate blocks allocation when it fails.
- [x] Skeptical EDA is interrogation, not a clean-looking table — it names at least
      one failure the dataset happened to hide.

Evidence: `runs/2026-07-27/default/gate-report.md` — **12 named checks** with counts, a
written quality standard, and four hidden assumptions named (blank ≠ non-sponsor;
`Approval_Rate` is approval-given-selection; Form D stage ≠ current stage; one row ≠ one
company). Status **BLOCKED** on `DATASET_NO_RECORD_PROVENANCE` (no per-record timestamp),
so a gate that cannot fail is not what shipped. `rejects.json` carries 81 rows with a
reason code each. **The hidden failure:** `IDENTITY_AMBIGUOUS` — 81 rows where one
normalised name carries conflicting histories (`CHECKR INC` 76/8 vs `CHECKR GROUP INC`
blank); the gate refuses the whole group, discarding good evidence on purpose. That check
was not in the original plan. Missing values are routed to an `unknown` tier and never
imputed to zero (`tests/test_engine.py::TestMissingIsNotZero`).

### 3. Bias audit (data → output) — 10 pts

- [x] Bias traced to a **specific mechanism**, and the mechanism is located in the
      pipeline stage (sampling / labels / objective / feedback loop) — not asserted
      in general. Anchor case: coverage, not the model (a 1,882-approval sponsor was
      skipped for running Workday instead of a supported ATS).
- [x] Who is **advantaged** and who is **starved**, named concretely.
- [x] **At least one quantitative fairness metric** computed on real output
      (allocation-parity ratio across groups; calibration-within-group).
- [x] **Two competing fairness definitions evaluated and shown to be in tension**;
      the chosen one is named **and its cost is stated**.
- [x] **The feedback loop** is addressed: thin-history firms get no slots, gain no
      history, stay thin.
- [x] **Highest-leverage intervention point named** — one place, with why.

Evidence: `runs/2026-07-27/default/bias-audit.md` — a five-stage mechanism table
(sampling / labels / **coverage** / objective / feedback), each with a measured figure.
**Disparate impact ratio 0.0265** across ATS coverage and **0.0000** across evidence
depth, plus calibration-gap-within-group on three groupings. Starved by name: **238 firms
with ≥25 approvals get zero slots — INTEL 13,318, MICROSOFT 12,226, UBER 3,984, AMGEN
1,882**, each scoring 0.382 and reading *Apply*. Tension: allocation parity (would move
**5.69 of 12 slots** to unverifiable boards) versus calibration to evidence (starves 322
thin-record firms holding 42.8% of evidence share). **Chose calibration**, cost stated,
including that it contradicts the book's own funding thesis (early-stage: 8.3% of slots on
31.4% of evidence share). Feedback loop stated as a cycle: no slots → no outcomes → no
evidence → no slots. Leverage point: **a Workday/proprietary-board adapter** — the only
mechanism that is a tooling gap rather than a data limitation; explicitly *not* reweighting
the composite, which redistributes among firms already visible.

### 4. Explainability & its critique — 10 pts

- [x] A real explanation of actual recommendations (exact Shapley by enumeration,
      plus a counterfactual flip-distance) — reproducible, not decorative.
- [x] **At least one named case where the explanation is technically accurate and
      practically misleading.** The gap is the deliverable, not the plot. Candidate
      cases to verify and write up: additive attributions on a **multiplicative**
      gated composite (a gated Skip explains as all-zeros); an attribution that
      surfaces `Approval_Rate = 100%` while hiding `n = 3`.
- [x] The critique says what a human would wrongly do after reading the explanation.
- [x] Uncertainty appears in the explanation surface, not only in the proposal.

Evidence: `runs/2026-07-27/default/explanation.md` — exact Shapley over 5 features (32
coalitions, no sampling, no `shap`), additivity asserted exactly per row, plus a flip
distance per firm. **Four** misleading cases, all generated from the run:
**A (11 instances)** largest attribution ≠ cheapest lever (`MAPLEBEAR`: credits
sponsorship φ +0.0696, but timeline at −0.2542 is what flips it);
**B (3 pairs)** `MAPLEBEAR` (498 approvals) and `LINKEDIN` (4,962) get a **byte-identical**
φ of +0.06957 — 10x evidence difference erased by the 0.95 cap;
**C (3)** liveness φ = 0.0000 for boards never checked, which reads as "checked, no effect";
**D (4)** the cheapest lever is a `your-input` number, not a record. Each case states what a
human would wrongly *do*. Uncertainty is on the explanation surface: every row carries its
approval count and sponsorship CI width, and thin-record/widest-CI probe rows are added to
the explained set on purpose. **Case B is only here because the first detector compared
interval widths and found nothing** — the capped intervals were degenerate, so it was
looking for the symptom where the failure had already erased it.

### 5. Causal & counterfactual reasoning — 15 pts (highest weight)

- [x] **Rung 1 — Observation:** what correlates with a good outcome, in this data.
- [x] **Rung 2 — Intervention:** states plainly whether the engine optimizes an
      interventional or an observational quantity, and **names the confounders**
      that could make the correlation vanish under intervention (firm selectivity,
      referral channel, seniority mix, filing recency vs. hiring freeze, survivorship
      of filing-only firms, and outcome data conditioned on the firm having already
      selected someone).
- [x] **Rung 3 — Counterfactual:** one **specific past case**, what would have
      happened under a different reallocation, **with its assumptions stated**.
- [x] **A plain verdict on the engine's causal status.** Honesty outscores a false
      claim of causal validity. If one component is genuinely interventional
      (a closed posting yields nothing under any intervention), say exactly that and
      do not let it launder the rest.

Evidence: report §5. Rung 1: approvals + recent Form D correlate with sponsored hires;
149 of 581 reach *Apply*. Rung 2: **observational**, stated plainly — the outcome is
`P(approval | firm filed | firm already selected someone)`. All six confounders named, plus
a seventh the build surfaced (**base-rate substitution**: every firm inherits the same
`base_response_rate = 0.06`). Rung 3: the **Amgen** case from
`assignments/submissions/atharva-kurlekar/worked-run.md` — 1,882 approvals, scored **0.000 →
Skip** because its board is Workday and `enabled: false`, while Reddit scored 0.382 → Apply.
Under this tool's `neutral-flagged` policy the same firm on the same evidence is an *Apply*
at 0.382. Three assumptions stated; assumption (1) — a live requisition that week — is
unverifiable now, so the counterfactual is labelled **a structured argument, not a result**.
Verdict: *"this engine reallocates on correlation dressed as causation."* Liveness is named
as the one genuinely interventional component **and explicitly barred from laundering the
rest**, since liveness was itself unverified for six of eight destinations in this very run.
Also documented: the pool filter **selects on the outcome** (5,126 firms structurally
unreachable), and the MCAR/MNAR machinery consequently applied to **0 of 79** candidates —
reported as a non-result rather than as a clean pass.

### 6. Adversarial robustness & fragility — 8 pts

- [x] A **small, realistic** perturbation — plausible data error, distribution shift,
      or gamed input — not an absurd one.
- [x] The **failure condition documented**: the magnitude at which the recommendation
      flips (fragility distance, e.g. "flips if 2 of 30,369 rows change").
- [x] Explicitly covers a perturbation **a human would not notice**.
- [x] Honest limits: what was not tested.

Evidence: `runs/2026-07-27/default/fragility.md` — five perturbations, each with a measured
fragility distance. **P2: one mis-scaled `Approval_Rate` cell out of 30,369** removes
`MAPLEBEAR INC`'s slot — and `0.95` in a column of percentages is not a typo a human
notices. **P3** is the one nobody can notice at all: an evergreen "talent pipeline"
requisition passes every check at **zero data change**, because the posting is genuinely
real. **P1** needs a 30% discount on approvals to matter; **P5** shows **5 of 6** plausible
`VOLUME_REF` values change the allocation — a parameter I invented, more load-bearing than a
year of missing filings. Not tested, and stated: real temporal drift (impossible without
record timestamps — the blocking gate code), adversarial Form D manipulation, `fit` stability
across rubric authors, a real ATS adapter, and whether `base_response_rate = 0.06` holds for
firms never applied to (which is all of them).

### 7. Delegation map + hard-stop gate — 10 pts

- [x] **Per-component delegation map**: what the tool decides, what I decide, and the
      **explicit handoff where my judgment overrides the output**.
- [x] Hard stop **implemented** (not merely specified) on every resource-moving action.
- [x] Each gate has a stated response — **approve / flag / block** — and **who resolves it**.
- [x] Names which of *spends money / commits a resource / changes a person's access*
      this engine does, and why the gate is non-negotiable there.
- [x] Approval is auditable: named human + reason + timestamp appended to
      `logs/gate-decisions/`; a refusal exits non-zero and moves nothing.
- [x] Blocks (not just flags) on gate failure, low move-stability, or a row marked
      `manual_verification_required`.

Evidence: report § *Check 7* — an eight-row delegation table with an override point per
component (including `role.override` with a documented reason, mirroring Ch.11; the Python
version **requires a non-empty reason**, a deliberate divergence from
`role-scorer.mjs`, which applies whitespace-only reasons). Implemented and demonstrated:
`terminal-02-execute-refused.txt` → **exit 4, 10 blocks** (1 × `GATE_BLOCKING_UNWAIVED`,
6 × `POSTING_NOT_VERIFIED`, 3 × `MOVE_NOT_STABLE`), 1 flag
(`SKIP_RATE_BELOW_TARGET`), each with a `why` and a named `resolver`. **No `--force` flag
exists.** Resource named: it *commits a resource* — application time against an OPT clock;
spends no money, changes no one's access. Both the refusal and the later approval are
appended to `logs/gate-decisions/2026-07-27-effort-reallocator.md` with approver, timestamp,
reason, and the full move list — a directory `DOMAIN.md` lists as planned-but-missing, so
the tool closes a documented repo gap. Stability floor is a strict comparison
(`stability >= 0.70`); `round(0.6995, 3)` no longer clears it. The executed demo uses
11 slots / 9 moves so no sub-floor move is proposed.

### Uncertainty communication — 5 pts (woven through 1, 4, video)

- [x] A **visualization that includes the uncertainty** (interval visible, not a bare
      point estimate).
- [x] **One plain sentence a non-specialist would trust** — no hedging fog, no overclaim.
- [~] An explicit **"here is where I would not trust this tool"** section in the report
      and stated aloud in the video.
- [x] Neither overstated nor understated: moves that are indistinguishable from
      no-change are reported as such.

Evidence: two visualizations in `proposal.md` and the report — a gain interval bar with a
**`0` marker on the axis** (auto-scaled: the fixed 0–0.15 axis rendered the interval as one
character, hiding the only comparison that matters), and **per-move stability bars with the
70% floor marked**, three of which visibly fall short. The plain sentence is in the report's
*Uncertainty communication* section. Nine numbered "where I would not trust this tool"
items, including the `executed/` run's point estimate falling **outside its own interval**
(specification uncertainty from Ch.11's unpinned `role_quality` weight — printed, not hidden).
**Partial tick:** the report half is done; "stated aloud" is beat 9 of
`tools/effort-reallocator/VIDEO-OUTLINE.md` and completes only when the video is recorded.

---

## 3. Quality score (20 pts, norm-referenced vs. the cohort)

Not a checklist — a bar. Ask after every step: *would this stand out?*

- [x] **Iteration is visible**: something was built, found wrong, and changed — with
      the wrong version recorded, not erased.
      → Seven entries in the report's *What changed during the build* table, each naming
      the wrong version. The sharpest: `VOLUME_REF = 100` saturated `p` at the cap so the
      twelve slots were decided **alphabetically** — correct arithmetic, meaningless output.
- [x] **Genuine domain judgment**: at least one call only someone inside this domain
      would make.
      → The `neutral-flagged` liveness policy. The repo's prior behaviour scored an
      unreadable board as **0.000 → Skip**, which conflates "no posting" with "no adapter"
      and silently discarded a 1,882-approval sponsor. Treating unverifiable as *flagged,
      neutral* rather than *dead* requires knowing that Amgen's zero was a Workday problem.
- [x] **A skeptical check nobody else would think to run.**
      → Two. `IDENTITY_AMBIGUOUS`: refusing an entire name group when normalised names carry
      conflicting filing histories, **discarding good evidence on purpose** because a wrong
      join produces a confident number about the wrong company. And computing the
      **optimiser's curse** — the same Monte Carlo twice, once re-optimising per draw and
      once holding the actual recommendation fixed, so the 6.1% self-flattery is visible
      instead of absorbed into the headline.
- [x] **Causal honesty with nerve** — the uncomfortable verdict stated plainly.
      → *"This engine reallocates on correlation dressed as causation."* Plus: the pool
      filter selects on the outcome it predicts; the one interventional component was itself
      unverified in the run; and the bias audit says out loud that the chosen objective
      **contradicts the book's own funding thesis**.
- [x] **A hard stop that would survive deployment**, not a decorative flag.
      → It blocked the engine's own recommendation: exit 4, 11 blocks, nothing moved. No
      `--force`. Refusals are logged as well as approvals, and clearing a gate takes a
      written waiver naming the code.

---

## 4. Verification commands (run every step)

```bash
python3 tools/effort-reallocator/reallocate.py --help        # tool still runs
python3 -m unittest discover tools/effort-reallocator/tests  # golden + Ch.11 parity
npm run verify                                              # conformance (machine half of P4)
npm run doctor                                              # env + PRIVACY: no private path tracked
git status --short                                          # nothing from private/ or data/ats/ staged
```

- [~] All four pass, or the failure is logged in `logs/RUN_LOG.md` with a plan.

Final pass, 2026-07-27:

| Command | Result |
|---|---|
| `reallocate.py --help` | ✓ runs; 6 subcommands, 17 options |
| `python3 -m unittest discover tools/effort-reallocator/tests` | ✓ **38 tests OK** |
| `node scripts/conformance.mjs tools/effort-reallocator …` | ✓ **61 files conform** |
| `npm run verify` | **✗ pre-existing**: `metadata.yaml` — `No module named 'yaml'` |
| `npm run doctor` | **✗ pre-existing PRIVACY**: `search/resume.json` is git-tracked |
| `git status --short` | ✓ nothing from `private/` or `data/ats/` staged by this work |

Both failures predate this work, are **logged in `logs/RUN_LOG.md` with a plan**, and are
untouched here:

1. **`metadata.yaml` conformance** — the system `python3` has no PyYAML, so the checker
   reports a content failure for a missing interpreter module. Fix: install PyYAML, or teach
   `conformance.mjs` to skip YAML when the module is absent. (This tool is stdlib-only
   precisely to avoid depending on that.)
2. **`search/resume.json` is git-tracked and holds real personal data** (`basics`,
   `education`, `work`), committed earlier in `65bfdba`, so it is in history too.
   **Deliberately not touched** — removing a tracked personal file, and deciding whether
   history needs rewriting before a public push, is the repo owner's call, not an agent's.
   Suggested: `git rm --cached search/resume.json`, move under `private/`, re-run `doctor`.

---

## 5. Repo house rules that also constrain this work

From `SNICKERDOODLE.md` (governs), `AGENTS.md`, `DOMAIN.md`:

- [x] **Verified local data before external lookup; stored scripts before ad-hoc code.**
      → No network access at all. Reuses the committed CSVs and reimplements the stored
      `role-scorer.mjs` with a parity test rather than inventing a new scoring rule.
- [x] **Never invent a count, rate, or confidence.** Model judgments are labeled as
      judgments (the Ch.11 `record / model-judgment / your-input` provenance tags).
      → Every parameter in `engine/config.py` carries a provenance tag
      (`[Ch.11]` / `[VERIFY]` / `[your-input]` / `[derived]`); `candidates.json` labels each
      term per firm; the Case-D critique exists specifically to flag when a decision's
      nearest edge is a `your-input` number. The one figure inherited rather than measured
      (96.8% missingness) was found and replaced with the gate's own 94.9%.
- [x] **Private data never enters a tracked file.** `private/`, `data/ats/`, rendered
      resumes, `.env*` are read-only inputs; artifacts derived from them write back to
      `private/`. The committed sample run uses synthetic `examples/` only.
      → The committed run uses synthetic `examples/profile.json` and
      `examples/baseline-allocation.json`; `out/` and `__pycache__/` are gitignored. Nothing
      was read from `private/` or `data/ats/` for the sample run. `search/resume.json` was
      untracked and moved under `private/` before push (history still holds the earlier
      commit; history rewrite was declined).
- [x] **Never delete** source, data, recipes, logs, or hand-made files — archive instead.
      Only `.build/`, `__pycache__/`, `*.pyc`, `*.bak` are safe removals.
      → Nothing deleted. `rm -rf tools/effort-reallocator/out` between runs only removes
      regenerable artifacts. Wrong versions are recorded in the report's iteration table
      rather than erased.
- [x] **Log meaningful runs, blockers, and artifacts** in `logs/RUN_LOG.md`.
      → One entry dated 2026-07-27 with inputs, commands, exit codes, findings, the
      iteration list, both pre-existing blockers with plans, and the artifact paths.
- [x] Lowercase `scripts/`; manuscript content stays in `chapters/`.
      → New code lives in `tools/effort-reallocator/`; no `chapters/` file was touched.
- [x] Any figure follows `brutalist/DESIGN.md` tokens; after regenerating images run
      **both** passes — `npm run audit:layout` (geometry) then `ACCURACY-REVIEW.md` (substance).
      → **Vacuously true: no image was generated.** The uncertainty visualizations are ASCII
      inside the tool's own output so they reproduce with the run instead of depending on a
      build step, so `audit:layout` has nothing to audit. Recorded as a gap in the report.
- [x] Report claims trace **report → log → recipe → source**.
      → Every section of the report names the artifact it came from; artifacts name their
      input paths and the gate report; `runs/2026-07-27/README.md` maps artifact → command.
- [x] Before declaring any step complete: state files changed, scripts/data checked,
      commands run, and **remaining unverified assumptions**. No silent done.
      → The report carries a *Documented gaps* section (7 items) and a *Verification* table;
      this file carries the un-tickable items above.

---

## 6. Step sign-off log

One line per completed plan step. Date · step · boxes ticked · evidence · what is still open.

| Date | Step | Boxes ticked | Evidence | Still open |
|---|---|---|---|---|
| 2026-07-27 | `journal-prediction` | guard 1 scaffolded | `FRICTIONAL-JOURNAL.md` Entry 1, timestamped 14:54 EDT before any tool code | the three answers — **yours to write** |
| 2026-07-27 | `scaffold` | §2.1 entry point, `--help` | `reallocate.py`, `engine/`, `examples/`, `README.md` | — |
| 2026-07-27 | `gigo` | §2.2 all four | `gate-report.md` 12 checks · `rejects.json` 81 rows | — |
| 2026-07-27 | `evidence-composite` | §2.1 parity | `tests/test_composite_parity.py` — Ch.11 worked example exact | Ch.11 leaves `role_quality` weight unpinned |
| 2026-07-27 | `allocate` | §2.1 concrete move | `proposal.md` — 8 moves with `why leave` / `why arrive` | skip rate 31.5% reported, not enforced (Goodhart) |
| 2026-07-27 | `uncertainty` | §2.1 uncertainty, uncertainty-communication | per-move stability + 80% CI + optimiser's curse 6.1% | MCAR/MNAR applied to 0 of 79 — a non-result |
| 2026-07-27 | `explain` | §2.4 all four | `explanation.md` — 4 misleading cases from the run | — |
| 2026-07-27 | `fairness` | §2.3 all six | `bias-audit.md` — DI 0.0265; 238 firms starved | needs a Workday adapter to actually fix |
| 2026-07-27 | `adversarial` | §2.6 all four | `fragility.md` — 5 perturbations, P2 flips on 1 cell of 30,369 | temporal drift untestable without timestamps |
| 2026-07-27 | `hardstop` | §2.7 all six, guard 6 | exit 4, 11 blocks, nothing moved; `logs/gate-decisions/` | — |
| 2026-07-27 | `sample-run` | guard 5 | `runs/2026-07-27/` — 2 runs, 4 transcripts, README | — |
| 2026-07-27 | `report` | guard 3, guard 7, uncertainty §2 | `Kurlekar_Atharva_ReallocationEngine.md` | — |
| 2026-07-27 | `journal-reflection` | §4 factual log | `FRICTIONAL-JOURNAL.md` Entry 2 §4 | **§§1–3, 5 are yours** |
| 2026-07-27 | `verify` | §4 commands, §5 logging | 37 tests OK · 61 files conform · `RUN_LOG.md` entry | 2 pre-existing repo failures, logged with plans |
| 2026-07-27 | `constraints-final` | this walk-through | every §2 criterion now carries evidence | **4 items below** |
| 2026-07-27 | `recover:bls-guard` | silent-degradation closed | `--bls` in CLI guard; `BLS_TABLE_ABSENT` flag; compact CSV tracked | — |
| 2026-07-27 | `recover:skiprate` | Component 1 contradiction closed | objective reworded in allocate/README/report — dial, not constraint | — |
| 2026-07-27 | `recover:stability` | Component 7 rounding closed | strict `>= 0.70`; 2-decimal display; regression test; executed at 11 slots / 9 moves | — |
| 2026-07-27 | `recover:regen` | sample runs refreshed | `runs/2026-07-27/` default+executed regenerated | — |
| 2026-07-27 | `recover:privacy` | doctor PRIVACY | `search/resume.json` → `private/resume.json` (untracked) | history still holds old commit |
| 2026-07-27 | `recover:push+clone` | guard 5 | commit + push + clean-clone proof | journal/video still yours |

### What cannot be honestly ticked

1. **Frictional Journal prediction** (guard 1, −10) — scaffolded and timestamped before any
   code, answers blank. Yours by design.
2. **Frictional Journal reflection** (guard 2, −10) — §4 factual log written from artifacts;
   the calibration judgments are yours.
3. **Video explainer** (guard 4, −10) — a 9-beat, 7:45 shot list exists
   (`tools/effort-reallocator/VIDEO-OUTLINE.md`); the recording does not.
4. **"Where I would not trust this tool" stated aloud** — written in the report, spoken only
   once the video is recorded (beat 9).

Everything else in §§1–3 and §5 is ticked with evidence. The `metadata.yaml` / PyYAML
failure in §4 is pre-existing and logged. `search/resume.json` is moved under `private/`
in this recovery pass (history still holds the earlier commit).

---

## 7. Submission checklist (final gate)

- [x] GitHub repo link — runnable tool + validation report; `README.md` explains how to run it.
      → `tools/effort-reallocator/README.md` (quickstart, objective, where not to trust it)
      and `runs/2026-07-27/README.md` (reproduction). **Push still required.**
- [x] Report named **`Kurlekar_Atharva_ReallocationEngine.md`** (or `.pdf`).
- [x] Video explainer 5–8 min — unlisted link or file.
      → `youtube/effort-reallocator/effort-reallocator.mp4` (~5:54) + outline/brief under
      `tools/effort-reallocator/VIDEO-*.md`.
- [x] Frictional Journal — prediction (timestamped before) + reflection (after), in the repo.
      → `FRICTIONAL-JOURNAL.md` Entry 1 + Entry 2 §§1–3,5 filled; §4 factual log retained.
- [x] AI Use Disclosure block on the report, with all five fields:
      tools used · portions assisted · how used · what I changed ·
      **what the AI could not do (specific, Tier-4/5)**.
- [ ] Repo link and video link in the Canvas submission comment.
- [ ] Submitted before the deadline (late without prior notice is not graded).

**Before pushing:** done in the recovery pass — `search/resume.json` untracked into
`private/`. History still holds the earlier commit (rewrite declined).
