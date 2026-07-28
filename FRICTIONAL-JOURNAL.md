# Frictional Journal — Effort Reallocator (INFO 7375)

Assignment: *The Reallocation Engine, Audited — Build a Useful Tool That Doubts Itself.*
Tool: `tools/effort-reallocator/` — reallocates a weekly **application-slot budget**
across companies. Book anchor: Ch.2 (reallocation principle), Ch.11 (the composite),
Ch.15 (skip-rate dial).

This file is the frictional record. Two entries: a prediction written **before** the
build, and a reflection written **immediately after**. The prediction is never edited
after the fact — if it turns out wrong, that is the data. Corrections belong in the
reflection.

---

## Entry 1 — Prediction

**Timestamp (before any tool code existed):** 2026-07-27 14:54 EDT (UTC−04:00)

**Repo state at this moment:** `tools/effort-reallocator/` does not exist. The only
prior art is `scripts/score/role-scorer.mjs` (the Ch.11 scorer) and the earlier
funded-systems-analyst pipeline under `scripts/{ingest,gigo,tools}/`.

### 1. What I expect the hardest failure to be

Blank H-1B cells treated as “does not sponsor.” I already know most of this file is
empty on sponsorship — if the engine imputes zero and looks decisive, I’ll waste a week
on the wrong story. Runner-up: thin records with a pretty rate looking safer than they
are. Less worried about the Ch.11 math; more worried I’ll believe a ranking built on a
misread missing cell.

### 2. How causally valid I expect the engine to turn out

Correlation in a decision’s clothes. Approval rate is “USCIS said yes to someone they
already picked,” not “they’ll pick me.” Biggest confounder: **selection into filing** —
blank means non-filer *or* never filed for someone like me. Only **liveness** feels like
it might survive Rung 2. Building it anyway beats guessing twelve slots with no
structure.

### 3. My confidence, as a number

**Confidence: 28 / 100**

**What that number claims:** odds I’d spend next week’s twelve applications on the top
move *without* opening the boards myself. Not “will the code run” — “would I trust this
with a week against an OPT clock.”

---

## Entry 2 — Reflection

**Timestamp (immediately after the build):** 2026-07-27 20:05 EDT (UTC−04:00)

### 1. What actually happened

`all` → exit 5, eight moves. Top: **ACME → MAPLEBEAR**, 1 slot, 100% stable, gain
**[+0.117, +0.123]**. Three moves called “no change.” Then `execute` → exit **4**,
**10 blocks, nothing moved.** Headline isn’t MAPLEBEAR — it’s that the engine won’t
execute its own proposal. Worst finding: Intel / Microsoft / Amgen score Apply and get
**zero slots** because I never built adapters for their ATS. Amgen’s Workday zero from
the earlier run coming back “fair” still stung.

### 2. Where my prediction was wrong

I prepared for blank→zero. The gate actually refuses that (94.9% flagged, not imputed).
What I missed: **5,126 funded firms never enter the pool** — titles only exist if they
already filed, so the filter selects on the outcome. Fragility wasn’t noisy counts; it
was one mis-scaled cell, and **`VOLUME_REF`** (a number I invented) putting slots in
**alphabetical** order when I set it to 100 — math correct, answer garbage. Bias was
plumbing, not weights. And I did **not** predict the tool would refuse its own
recommendation. Mid-build: hash-randomized move pairs, `round(0.6995,3)` almost
committing a sub-floor move, silent missing BLS, walking back a skip-rate “constraint”
I shouldn’t have claimed.

### 3. What that says about my calibration

28 asked the right question and still missed *why*. I under-worried blank→zero and
over-trusted “tests pass ⇒ recommendation means something.” Alphabetical `VOLUME_REF`
and identical Shapley φ for firms 10× apart in approvals made that clear. Next time:
worry less about arithmetic, more about invented parameters and adapters I didn’t build.

### 4. What the build actually surfaced (factual log — for your reference when writing 1–3)

Observed findings only, so the reflection above can be written against evidence rather
than memory. Every line traces to a committed artifact under
`tools/effort-reallocator/runs/2026-07-27/`. The interpretation in 1–3 and 5 stays yours.

**The run, in one line.** `reallocate.py all` exited **5** (gate blocking) and produced 8
moves; `reallocate.py execute` exited **4** with **10 blocks** and moved nothing. The
engine's own recommendation was not executable by its own rules.

**What the tool did.**

- Evaluated **581** of 30,369 companies → Apply 149 · Consider 249 · Skip 183.
- Top move: **1 slot ACME ANALYTICS LLC → MAPLEBEAR INC**, 80% CI on Q 1.0–1.0,
  **stability 100.0%**, sponsorship p = 0.950 over 498 approvals.
- Expected gain **+0.121 responses/week, 80% CI [+0.117, +0.123]**, positive in 100% of
  draws — under the model's own assumptions.
- **3 of 8 moves were reported as "not distinguishable from no change"** (stability 20.7%,
  18.4%, 5.2%) rather than as small gains.
- Optimiser's curse measured: re-optimising per draw reports **+0.12766** against the fixed
  proposal's **+0.11989** — **6.1%** of the naive figure is the optimiser fitting noise.

**Where the data fought back.**

- Gate status **BLOCKED** on `DATASET_NO_RECORD_PROVENANCE` — the file has no per-record
  timestamp, so a 2015 filing is indistinguishable from a 2024 one.
- **94.9% of rows (28,812 of 30,369) carry no H-1B fields.** Never imputed to zero.
- **81 rows rejected `IDENTITY_AMBIGUOUS`** — one normalised name with conflicting filing
  histories (`CHECKR INC` 76/8 vs `CHECKR GROUP INC` blank). The gate refuses the whole
  group, discarding good evidence, because a wrong join produces a confident number about
  the wrong company. *This check was not in the original plan.*
- `FUNDING_DATE_STALE` on **22,451 rows (73.9%)**; 9 entity collisions; 3 wage-in-title
  artifacts; 31 implausible funding stages.

**The blind spot (largest single finding).** **5,126 firms** have recent Form D funding and
no filing record, and they **never enter the pool at all** — the pool requires filed job
titles to compute a fit vote, and a firm has filed titles only if it already sponsored
someone. The filter selects on the outcome being predicted. With no titles the composite
cannot exceed 0.30 even with sponsorship imputed at maximum: structurally unreachable, not
merely disadvantaged. The MCAR/MNAR machinery therefore applied to **0 of 79** pooled
candidates.

**Bias.** Disparate impact ratio **0.0265** by ATS coverage (a factor of 38): 15 firms with
readable boards took 6 of 12 slots on 4% of the evidence share; 566 firms without took 6 on
96%. **238 firms with ≥25 approvals got zero slots**, including **INTEL (13,318 approvals)**,
**MICROSOFT (12,226)**, **UBER (3,984)**, **AMGEN (1,882)** — all scored 0.382, all read
*Apply*, all unreachable. By evidence depth the ratio is **0.0000**: 322 thin-record firms
hold 42.8% of evidence share and receive nothing.

**Fragility.** One mis-scaled `Approval_Rate` cell — **1 of 30,369** — removes the
top-ranked firm's slot. Removing a fiscal year of filings needs a **30%** discount to matter.
**5 of 6** plausible values of `VOLUME_REF`, a parameter with no source that I invented,
change which firms get slots. An evergreen "talent pipeline" requisition is undetectable at
**zero data change**, because the posting is genuinely real.

**Explanation.** Exact Shapley, additivity exact on every row. `MAPLEBEAR INC` (498
approvals) and `LINKEDIN CORP` (4,962) receive a **byte-identical** sponsorship attribution
of **+0.06957** — 10x difference in evidence, no difference in explanation, because p is
capped at 0.95 and the intervals collapse to zero width. For 11 firms the largest attribution
(sponsorship) is *not* the cheapest lever (timeline), and for 4 the cheapest lever is a
`your-input` number rather than a record.

**Causal status.** The engine optimises an observational quantity: the outcome is
`P(approval | firm filed | firm already selected someone)`. **Liveness is the one genuinely
interventional component** — and in this run it was *unverified for six of eight
destinations*, so the only causal part of the engine was itself an assumption.

**What changed mid-build (the wrong versions, kept).**

1. `VOLUME_REF = 100` saturated p at the cap for nearly every mid-size sponsor; the twelve
   slots ended up decided **alphabetically**. Raised to 500 and a tie report added.
2. The Case-B detector compared *interval widths* and found nothing — the capped intervals
   were degenerate, so the widths matched too. The detector was looking for the symptom in
   the place the failure had already erased.
3. Move `from → to` pairings changed between identical runs (Python hash randomisation);
   found by running twice and diffing.
4. A 70.0% move was called stable by the proposal and unstable by the hard stop — then
   a deeper bug: `round(0.6995, 3) == 0.700` let AIRBNB → APPLOVIN be **committed**. Fixed
   to a strict comparison; executed demo re-planned at 11 slots.
5. The bias audit quoted **96.8%** missingness inherited from the earlier assignment while
   this tool's own gate measured **94.9%**.
6. The skip-rate constraint was specified as enforced and became **reported** (and the
   objective sentence was rewritten so it no longer claims a constraint the code lacks):
   the run's 31.5% is below Chapter 15's 50% target, and tightening the threshold until the
   metric went green would have been Goodhart's law with extra steps.
7. Buying executability cost the signal: under `--liveness-policy block` the engine commits
   **9** stable moves (11-slot plan) and the skip rate falls to **0.0%** — the filter
   stopped filtering.
8. A missing BLS table was swallowed silently by `FileNotFoundError`, changing Monte Carlo
   intervals with no refusal. CLI now refuses; gate flags `BLS_TABLE_ABSENT`; the compact
   CSV is tracked.

### 5. The one thing I would tell the next person building a reallocation engine

Before you trust a “correct” ranking, check whether a number you invented — or an ATS
adapter you never built — is actually choosing the twelve slots.

---
