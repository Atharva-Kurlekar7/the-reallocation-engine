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

> **[FILL IN — in your own words, before you read the tool code.]**
> This must be yours. An AI-written prediction measures nothing about *your*
> calibration, which is the only thing this entry exists to measure. Three answers,
> a few sentences each. Delete this blockquote when done.

### 1. What I expect the hardest failure to be

*What will be the most stubborn or most surprising thing that goes wrong — in the
data, the math, the allocation, or my own reasoning? Be specific enough to be
wrong. "The data will be messy" cannot be graded against reality; "the sponsorship
signal will look strongest exactly where the sample is too small to support it"
can.*

**[FILL IN]**

### 2. How causally valid I expect the engine to turn out

*A reallocation is a causal claim: "moving slots to B will produce a better outcome."
Before building it — do I expect this engine to be optimizing an interventional
quantity, or a correlation wearing a decision's clothes? Which specific confounder
do I expect to matter most? Which component, if any, do I expect to survive Rung 2?*

**[FILL IN]**

### 3. My confidence, as a number

*One number, 0–100, for how much I would trust this engine's top recommendation
enough to actually spend a week of applications on it — plus one line on what that
number is a claim about.*

**Confidence: __ / 100**

**What that number claims:** **[FILL IN]**

---

## Entry 2 — Reflection

**Timestamp (immediately after the build):** [FILL IN after reading §4 below]

> **[FILL IN — the build is finished and §4 is populated. Read §4 first, then write
> 1, 2, 3 and 5 in your own words.]**
> The prompts are scaffolding, not answers. §4 is the factual log; the judgments are
> yours, and they are the only part of this file that measures anything.

### 1. What actually happened

*What did the tool actually do on the real data? What was the top move, and how wide
was its interval?*

Anchors from §4 if useful: the top move (ACME → MAPLEBEAR, 1 slot, 100% stable), the
gain interval [+0.117, +0.123], the fact that `execute` refused with 11 blocks, and
which single finding you would put first if you had one sentence.

**[FILL IN]**

### 2. Where my prediction was wrong

*Name the specific gap between Entry 1 and what happened. Both directions count: what
you feared and did not happen is as informative as what blindsided you.*

Compare your Entry-1 answer to §4 line by line. Candidates for "did you call this?":

- Did you predict the **hardest failure** would be the thin-record/small-n problem? What
  actually dominated was the **pool filter selecting on the outcome** — 5,126 recently
  funded firms never entered the pool, which no amount of care with small samples fixes.
- Did you expect fragility to come from **noisy counts**? It came from **one mis-scaled
  cell in 30,369** and from **a parameter you invented** (`VOLUME_REF`, 5 of 6 values
  change the allocation).
- Did you expect the **bias** to be in the model or in the weights? It was in **ATS
  coverage** — a tooling gap that zeroes a 13,318-approval sponsor.
- Did you predict the engine would ever **refuse its own recommendation**?

**[FILL IN]**

### 3. What that says about my calibration

*Was the confidence number too high or too low, and in which direction do I
systematically err — over-trusting the arithmetic, or over-trusting my own
skepticism? What would I bet differently next time?*

One useful test against §4: the arithmetic was correct in every case where the output
was meaningless. The composite was right while the twelve slots were being decided
alphabetically; the Shapley values were exact while two firms 10x apart got identical
explanations. If your Entry-1 confidence number was mostly a statement about whether the
math would be right, it was answering a question that was never in doubt.

**[FILL IN]**

### 4. What the build actually surfaced (factual log — for your reference when writing 1–3)

Observed findings only, so the reflection above can be written against evidence rather
than memory. Every line traces to a committed artifact under
`tools/effort-reallocator/runs/2026-07-27/`. The interpretation in 1–3 and 5 stays yours.

**The run, in one line.** `reallocate.py all` exited **5** (gate blocking) and produced 8
moves; `reallocate.py execute` exited **4** with **11 blocks** and moved nothing. The
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

*One sentence. Not a summary of the build — the thing you would say to stop them from
repeating whichever mistake in §4 cost you the most time.*

**[FILL IN]**

---

## A note on what is and is not filled in

Entry 1 and the judgments in Entry 2 (§1, 2, 3, 5) are deliberately left blank for the
author to write. An AI-drafted prediction measures nothing about a human's calibration,
which is the only thing this file exists to measure, and an AI-drafted reflection on that
prediction would be a machine grading its own homework. §4 is factual and is drafted from
committed artifacts because a reflection written from memory is a reflection about memory.
