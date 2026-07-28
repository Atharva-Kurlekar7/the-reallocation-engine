# The Reallocation Engine, Audited

**Atharva Kurlekar · INFO 7375 · 2026-07-27**

Tool: `tools/effort-reallocator/` · Sample run: `tools/effort-reallocator/runs/2026-07-27/`
Journal: `FRICTIONAL-JOURNAL.md` · Acceptance gate: `constraints.md`

## Canvas submission comment

Paste into the Canvas assignment comment:

```
Name: Atharva Kurlekar
Assignment: The Reallocation Engine, Audited

Repo: https://github.com/Atharva-Kurlekar7/the-reallocation-engine/tree/mode/atharva-kurlekar-erp-to-ai
Tool: tools/effort-reallocator/
Run: python3 tools/effort-reallocator/reallocate.py all

Report: Kurlekar_Atharva_ReallocationEngine.md
Journal: FRICTIONAL-JOURNAL.md
Video: https://youtu.be/dZcid2Jc2fg
```

Every number below is copied from a committed artifact of the run in
`tools/effort-reallocator/runs/2026-07-27/`, and each section names the file it came from.
Nothing in this report was typed from memory.

---

## What it reallocates

**The scarce resource is application slots** — the twelve applications one week of
Chapter 15's three-hour apply block actually buys, spent against an OPT clock that does
not pause. The engine takes last week's allocation and outputs a **move**: *shift Q slots
from company A to company B*, with an interval on the gain and a stability percentage.

**Objective, in one sentence:** maximise expected sponsored-interview yield per slot,
subject to a per-company cap of 3 — with Chapter 15's ≥50% skip rate reported as a
**dial**, not enforced as a constraint, because it is a process metric a human reads
in two directions.

**What that objective leaves out:** referrals, my own application quality and its
variance, interview conversion, compensation, team quality, and every firm with no H-1B
filing record and no readable job board. The last omission is the largest and it is
quantified in §2.

**Book anchors:** Ch.2 (the reallocation principle), Ch.11 (the composite
`(Σ vote·weight) × liveness × timeline` and the 0.3 threshold), Ch.15 (the skip-rate dial).

### Run it

```bash
python3 tools/effort-reallocator/reallocate.py all       # gate → allocate → explain → audit
python3 tools/effort-reallocator/reallocate.py execute    # exits 4: refuses to commit
```

Python 3.9+, standard library only, no install step, no network. Inputs are the committed
public dataset (30,369 rows) plus a synthetic profile and baseline in `examples/`, so a
clean clone reproduces every number here.

---

## The headline finding

**The engine's own recommendation cannot be executed.** `all` produces a twelve-slot
allocation and eight moves; `execute` then refuses with exit code 4 and eleven blocks. Six
destinations have job boards nobody can check, three moves are statistically
indistinguishable from doing nothing, and the dataset never cleared the quality gate in
the first place.

That is the tool working. A reallocation engine that always has an answer is not measuring
anything.

---

## Check 1 — Working tool + uncertainty on the move itself

*Evidence: `runs/2026-07-27/default/proposal.md`, `terminal-01-all-default.txt`*

The composite is a reimplementation of this repo's `scripts/score/role-scorer.mjs`. It is
**verified, not asserted**: `tests/test_composite_parity.py` reproduces Chapter 11's worked
example exactly (biotech 0.44625 → Apply; non-sponsor 0.1785 → Skip) and asserts parity
against the committed `data/examples/role-scores.json`. 38 tests pass.

The output is a move, not a ranked list:

| Q | From | To | 80% CI on Q | Stability | Verdict |
|---:|---|---|---|---:|---|
| 1 | ACME ANALYTICS LLC | MAPLEBEAR INC | 1.0–1.0 | 100.0% | directional |
| 1 | ACME ANALYTICS LLC | ROKU INC | 1.0–1.0 | 100.0% | directional |
| 1 | LINKEDIN CORP | HUMAN INC | 0.0–1.0 | **20.7%** | **not distinguishable from no change** |
| 1 | LINKEDIN CORP | PINTEREST INC | 0.0–1.0 | 70.7% | directional |
| 1 | ETSY INC | ROBLOX CORP | 0.0–1.0 | 70.2% | directional |
| 1 | AIRBNB INC | TELADOC HEALTH INC | 0.0–1.0 | **18.4%** | **not distinguishable from no change** |
| 1 | DOCUSIGN INC | TWILIO INC | 0.0–1.0 | 72.5% | directional |
| 1 | ZOOX INC | VISICON TECHNOLOGIES INC | 0.0–0.0 | **5.2%** | **not distinguishable from no change** |

Uncertainty is attached to **the move**, not only to the inputs. Monte Carlo (2,000 draws,
seed 20260727) over four named sources: a Beta(approvals+1, denials+1) posterior per firm;
the `role_quality` weight Chapter 11 leaves unpinned, drawn from U[0, 0.20]; two
missingness scenarios (MCAR vs a pessimistic MNAR Beta(1,4)); and jitter on `fit`, because
fit is a rubric output rather than a measurement.

### The visualization, with the uncertainty in it

```
expected additional responses per week   ([ ] = 80% CI, | = point, 0 = no change)
.....0.........................................[=|].....  axis -0.015 to +0.138

per-move stability — share of draws in which the move survives
(70.0% floor marked +; below it the move is reported as no change)
######################################## 100.0%  MAPLEBEAR INC
######################################## 100.0%  ROKU INC
########....................+...........  20.7%  HUMAN INC  <- no change
############################+...........  70.7%  PINTEREST INC
############################+...........  70.2%  ROBLOX CORP
#######.....................+...........  18.4%  TELADOC HEALTH INC  <- no change
#############################...........  72.5%  TWILIO INC
##..........................+...........   5.2%  VISICON TECHNOLOGIES INC  <- no change
```

Expected gain **+0.121 responses per week, 80% CI [+0.117, +0.123]**. The interval clears
zero in 100% of draws — *under the model's own assumptions*, which is not the same as being
right about the world. Three of eight moves are reported as no-change rather than as small
positives, which is the distinction the rubric asks for and the one most tools quietly skip.

**The optimizer's curse, measured.** Re-optimising the allocation inside every draw reports
**+0.12766**; holding the actual recommendation fixed reports **+0.11989**. The difference,
**+0.00777 or 6.1%**, is gain that exists only because the optimiser was allowed to see
noise nobody can observe. The naive number is the larger one, and it is the one a
straightforward Monte Carlo would have printed.

**Refusal behaviour.** A missing input exits 2 with no output file. A failed gate exits 5.
A blocked execution exits 4 and writes nothing to the ledger. There is no `--force`.

---

## Check 2 — Data validation and the GIGO gate

*Evidence: `runs/2026-07-27/default/gate-report.md`, `rejects.json`*

**Status on the real dataset: BLOCKED.** Twelve named checks, each with a count and a
reason code:

| Check | Severity | Count | Rate |
|---|---|---:|---:|
| `DATASET_NO_RECORD_PROVENANCE` | **blocking** | 30,369 | 100.0% |
| `IDENTITY_AMBIGUOUS` | reject | 81 | 0.3% |
| `FUNDING_DATE_STALE` | flag | 22,451 | 73.9% |
| `H1B_FIELDS_ABSENT` | flag | 28,812 | **94.9%** |
| `FUNDING_STAGE_IMPLAUSIBLE` | flag | 31 | 0.1% |
| `ENTITY_COLLISION` | flag | 9 | — |
| `WAGE_IN_TITLE` | flag | 3 | — |
| `RATE_WITHOUT_DENOMINATOR`, `RATE_ARITHMETIC_MISMATCH`, `RATE_SCALE_ANOMALY`, `ABSURD_VALUE`, `FUNDING_DATE_MISSING` | reject/flag | 0 | 0.0% |

### The hidden assumptions, named

1. **A blank H-1B cell means the firm does not sponsor.** It does not — it means no filing
   was matched. **94.9% of rows (28,812 of 30,369)** are blank. The gate routes them to an
   `unknown` tier and *never* imputes zero. That single refusal is the difference between
   "no evidence" and "evidence of no", and the missingness is plainly not MCAR: a firm has
   a filing record only if it has already sponsored someone.
2. **`Approval_Rate` measures willingness to sponsor.** It measures USCIS approval *given*
   the firm already filed for a candidate it had already selected. See §5.
3. **`latest_funding_stage` is the firm's stage.** It is the stage of its last Form D, so
   public companies appear as early-stage. 31 rows are implausible on their face
   (early-stage label, >100 approvals).
4. **One row is one company.** It is not: 9 normalised names carry identical filing counts
   under two legal forms (`PELOTON INTERACTIVE INC` / `LLC`, 310 approvals each).

### The failure the dataset was hiding

The check I did not plan for is the one that found something. `IDENTITY_AMBIGUOUS` rejected
**81 rows** where one normalised name carries *conflicting* filing histories — `CHECKR INC`
has 76 approvals and 8 denials while `CHECKR GROUP INC` has none; `BEACHBODY LLC` has 34/2
while `BEACHBODY CO GROUP LLC` is blank. There is no way to tell which entity posts the job
I would apply to, so **the gate refuses the whole group, including the row with the strong
record**. Throwing away good evidence is the correct cost here: a wrong join produces a
confident number about the wrong company, and that is worse than no number.

The blocking check is the one about the data as a whole rather than any row: the file has
**no per-record collection timestamp or source**, so a 2015 filing is indistinguishable
from a 2024 one and a mid-collection protocol change would be invisible. Clearing it takes
a named human and a written waiver — which is exactly what the `executed/` run records.

---

## Check 3 — Bias audit, from collection to output

*Evidence: `runs/2026-07-27/default/bias-audit.md`*

The parties advantaged or starved here are **employers**, not a protected class of people.
The harm is nonetheless real and self-reinforcing: which firms ever see an application from
a candidate who needs sponsorship.

| Pipeline stage | Mechanism | Measured in this run |
|---|---|---|
| sampling | a firm appears only if it filed an H-1B petition | 94.9% of rows carry no H-1B fields |
| labels | the label is approval *given the firm already selected someone* | not willingness, and not about me |
| **coverage** | only Greenhouse/Lever/Ashby boards are readable | `AMGEN INC`, 1,882 approvals, scored **0.000** in the prior worked run because its board is Workday |
| objective | yield-per-slot rewards filing volume, a proxy for firm size | the volume factor saturates at 500 approvals — my parameter, not a finding |
| **feedback** | no slots → no outcomes → no evidence → no slots | 322 thin-record firms received zero slots |

**The bias is in the tooling, not the model.** Grouping by whether the repo's scanner can
read a firm's board:

| Group | Eligible | Slots | Slot share | Evidence share | Slots/firm |
|---|---:|---:|---:|---:|---:|
| supported ATS board | 15 | 6 | 50.0% | 4.0% | 0.4000 |
| no supported board | 566 | 6 | 50.0% | 96.0% | 0.0106 |

**Disparate impact ratio 0.0265** — a factor of 38. (The four-fifths rule is borrowed from
employment law and is a weak analogy for employers rather than applicants; I report it
because it is legible, not because it is apt.) By evidence depth the ratio is **0.0000**:
322 firms with fewer than 25 approvals hold 42.8% of the evidence share and receive **zero**
slots.

**Who is starved, by name:** 238 firms with ≥25 approvals get nothing because nobody can
check their postings — **INTEL CORP (13,318 approvals), MICROSOFT CORP (12,226), UBER
(3,984), AMGEN (1,882)**. Each scores 0.382 and reads *Apply*. Each gets zero slots.

**Two definitions, in genuine tension.** *Allocation parity across ATS coverage* demands
slots for the group with the least verifiable evidence — 5.69 of 12 slots would move to
firms whose postings cannot be confirmed, which is the exact waste the liveness gate exists
to prevent. *Calibration to evidence* demands slot share track evidence-weighted yield, and
starves thin-record firms by construction. With a fixed twelve-slot budget no allocation
satisfies both.

**I chose calibration**, and the cost is precise: 238 deep-record firms and 322 thin-record
firms receive nothing. My reason is not that parity is wrong but that I am not a regulator
distributing a public good — I am one candidate with twelve applications and a visa clock.

**The uncomfortable part:** calibration starves early-stage firms (8.3% of slots on 31.4%
of evidence share), which **contradicts this book's own thesis** that recent Form D funding
is the hiring signal worth chasing. The engine's objective and the domain's premise
disagree, and the objective currently wins.

**Highest-leverage intervention: a Workday/proprietary-board provider adapter.** One place,
and the reason is that it is the only mechanism here that is a *tooling gap* rather than a
data limitation — fixable by writing code instead of by assuming something unknowable.
Reweighting the composite is *not* the leverage point: it redistributes among firms the
engine can already see and leaves the mechanism untouched.

---

## Check 4 — Explainability and its critique

*Evidence: `runs/2026-07-27/default/explanation.md`*

Exact Shapley values by full enumeration over 5 features (32 coalitions — no sampling, no
`shap` dependency), plus a flip-distance counterfactual per firm. Additivity is asserted
exactly for every row: `Σφ = v(full) − v(∅)`. Uncertainty appears **in the explanation
surface**, not only in the proposal: each row carries its approval count and the width of
its sponsorship interval.

Four cases where the explanation is technically correct and practically misleading, all
generated from this run rather than hypothesised:

**Case A — additive attributions on a multiplicative composite (11 instances).** For
`MAPLEBEAR INC` the explanation says *sponsorship is the largest contributor (φ = +0.0696)*.
True. But the cheapest change that would flip the decision is **timeline, at −0.2542**.
Credit for magnitude and leverage for action are different orderings, and the chart shows
only the first. **What a human would wrongly do:** spend the week chasing better sponsorship
evidence when the decision actually turns on a timeline number.

**Case B — the explanation deletes the sample size (3 pairs).** `MAPLEBEAR INC` (498
approvals) and `LINKEDIN CORP` (4,962 approvals) receive a **byte-identical** sponsorship
attribution of +0.06957, on records that differ by **10x**. The attribution is a function of
`p`, and `p` is capped at 0.95, so every large sponsor collapses onto the same number and
the credible intervals collapse to zero width with it. **A reader comparing the two
explanations sees no difference in the evidence, because the explanation has removed it.**

**Case C — an unverified gate reads as a verified one (3 instances).** `liveness` shows
φ = +0.0000 for firms whose boards the scanner cannot read at all. A zero attribution looks
like "checked, no effect". It means "not checked". **What a human would wrongly do:** apply
without opening the careers page, because the explanation showed liveness as a settled term.

**Case D — the decision's nearest edge is an assumption, not a record (4 instances).** The
cheapest lever for `MAPLEBEAR INC` is `timeline`, whose provenance is `your-input` — a
number I chose. The explanation presents evidence and assumption in the same units, on the
same chart, so nothing signals that the decision is one adjustment of my own guess away
from reversing.

Case B is in this report only because the first version of the detector compared *interval
widths* and found nothing: the capped intervals are degenerate, so the widths were all
identical too. The detector was looking for the symptom in the one place the failure had
already erased it.

---

## Check 5 — Causal and counterfactual reasoning

### Rung 1 — Observation (what correlates, in this data)

Firms with more H-1B approvals and a recent Form D filing have historically hired more
sponsored workers. That is an association in the filing record and the engine reproduces it
faithfully: 149 of 581 evaluated firms reach the *Apply* tier, and slots follow approval
volume.

### Rung 2 — Intervention (does moving *my* slots change *my* outcome?)

**The engine optimises an observational quantity and presents it as an interventional one.**
Stated plainly, because that gap is the whole point of the assignment.

`P(sponsored interview | I apply to firm B)` is not what the data measures. The data
measures `P(USCIS approval | the firm already filed | the firm had already selected a
candidate)`. **The outcome variable is conditioned on the firm having already chosen
someone.** It is a measure of willingness *given selection*, and the engine uses it as a
proxy for selection itself. Those are different quantities and no amount of arithmetic
converts one into the other.

Confounders that could make the correlation vanish — or reverse — under intervention:

- **Firm selectivity.** LinkedIn's 4,962 approvals also mean orders of magnitude more
  applicants per opening. Approval volume and application difficulty rise together, so the
  engine's top signal is partly a measure of how hard it is to get in.
- **Referral channel.** Large sponsors fill a large share of roles through referrals. Cold
  applications and referred applications are different treatments with different response
  rates, and the engine models neither.
- **Seniority mix.** A firm's filings may be dominated by senior roles I cannot fill. The
  fit rubric penalises this weakly; the filing counts do not distinguish it at all.
- **Filing recency versus a current freeze.** A 2023 filing record says nothing about a
  2026 hiring freeze, and the dataset has **no per-record timestamp** — the blocking gate
  code is exactly this confounder.
- **Survivorship.** Only firms that have already filed appear in the pool. **5,126 firms
  with recent Form D funding and no filing record never enter it** — see the blind spot
  below.
- **Base-rate substitution.** The expected-gain figure multiplies composites by
  `base_response_rate = 0.06`, my own historical response rate. Every firm inherits the
  same rate, so the gain scales linearly with a number that has no per-firm content.

### The blind spot the pool filter creates

*Evidence: `proposal.md` § "The blind spot"*

The pool requires filed job titles to compute a fit vote. A firm has filed titles only if
it has already sponsored someone, so **the filter selects on the very outcome the engine
predicts**. **5,126 firms** with Form D funding in the last three years and no filing record
are not ranked low — they never enter the pool at all. With no titles there is no fit vote,
so their composite cannot exceed `0.95 × 0.35 × 0.9 = 0.30` even if sponsorship were imputed
at maximum: they are **structurally unreachable, not merely disadvantaged**, and the Monte
Carlo missingness scenarios cannot rescue them.

This is where the gate's carefulness stops helping. Refusing to read a blank cell as a zero
protects the arithmetic for firms *in* the pool and does nothing for 5,126 firms the pool
never sees. The tool's most rigorous check and its largest blind spot are the same design
decision seen from two sides.

Consequently the MCAR/MNAR scenarios were applied to **0 of 79** pooled candidates. That is
not a clean result — it means every firm in the pool already has a filing record, so the
missingness machinery had nothing to act on. Reporting a zero here as success would have
been the more comfortable lie.

### Rung 3 — Counterfactual (one specific past case)

**The case:** in my prior worked run (`assignments/submissions/atharva-kurlekar/worked-run.md`),
`AMGEN — Data Engineer` scored **0.000 → Skip**, while `REDDIT — Staff Data Engineer` scored
**0.382 → Apply**. Amgen holds **1,882 approvals**. It scored zero for one reason: its board
is Workday and `enabled: false` in `portals.yml`, so the liveness gate multiplied the whole
composite by zero. The scan never attempted Amgen. That is not verified absence of
postings — it is absence of a check.

**The counterfactual:** had one slot gone to Amgen instead of the fourth Reddit
application, what would have happened?

The engine as built says: nothing good, because Amgen's composite was 0.000. The engine
under `neutral-flagged` — the policy this tool introduced — says Amgen is an *Apply* at
0.382, tied with Reddit. **Same firm, same week, same evidence, opposite recommendation, and
the only thing that changed is a policy choice about how to treat an unreadable board.**

Its assumptions, stated: (1) Amgen had a live matching requisition that week — unverified,
and unverifiable now; (2) Amgen's 1,882 approvals imply a response probability at least
equal to Reddit's, which assumes away the selectivity confounder above; (3) the marginal
Reddit application was worth less than the first Amgen one, which the repeat-slot decay of
0.5 asserts rather than measures. **Under those three assumptions the reallocation would
have been positive. I cannot check the first one, so the counterfactual is a structured
argument, not a result.** What I can verify is the mechanism: a 1,882-approval sponsor was
excluded by a tooling gap, and the tool called it *Skip*.

### The verdict, plainly

**This engine reallocates on correlation dressed as causation.** Its central quantity is
conditioned on the firm having already selected a candidate, and its strongest signal
(approval volume) is entangled with the thing that makes those firms hardest to enter.
Nothing in the arithmetic fixes that.

**One component is genuinely interventional: liveness.** A closed posting yields nothing
under any intervention — no confounder rescues an application into a requisition that does
not exist. That is a real causal claim and it is why liveness is a gate rather than a vote.

**And it does not launder the rest.** Liveness tells you a door exists. It says nothing
about whether walking through it changes anything, and in this run liveness was *itself
unverified* for six of eight destinations. The one interventional component of the engine
was, in the actual run, an assumption.

---

## Check 6 — Adversarial robustness and fragility

*Evidence: `runs/2026-07-27/default/fragility.md`*

Five perturbations, each plausible, each with a measured fragility distance:

| # | Perturbation | Result | Fragility distance |
|---|---|---|---|
| P1 | vintage shift — one fiscal year of filings removed | changes | flips once approvals are discounted to **70%** of stated value |
| P2 | units error — one `Approval_Rate` cell on a 0–1 scale | **FLIPS** | **one cell in 30,369 rows** moves `MAPLEBEAR INC` from 1 slot to 0 |
| P3 | gamed input — an evergreen "talent pipeline" requisition | undetectable | **zero data change required — the posting is real** |
| P4 | entity split — one firm's history across two legal names | holds | 2 edited cells of 581 do not change the allocation |
| P5 | parameter sweep — `VOLUME_REF`, repeat-slot decay | changes | **5 of 6** plausible `VOLUME_REF` values change the allocation |

**The engine is robust to the perturbation everyone tests and fragile to the ones nobody
does.** Proportional noise on the counts (P1) needs a 30% discount to matter. A single
mis-scaled cell (P2) is enough to remove the top-ranked firm's slot — and a `0.95` in a
column of percentages is not a typo a human would notice while scrolling, because it looks
like a perfectly ordinary number.

**The perturbation a human would not notice at all is P3.** An evergreen requisition — a
"talent pipeline" post kept open with no role behind it — passes every check this tool has,
because the posting genuinely exists. No amount of data quality work detects it. It needs a
phone call.

**P5 is the perturbation I did not expect to fail.** Five of six defensible values for
`VOLUME_REF` — a parameter I invented, with no source in the book or the data — change which
firms get slots. The recommendation is more sensitive to a number I chose than to a year of
missing filings.

**What was not tested:** actual distribution shift over time (impossible without record
timestamps — the blocking gate code), adversarial manipulation of Form D filings, whether
`fit` is stable across rubric authors, and the effect of a real ATS provider adapter. The
engine also cannot test whether its `base_response_rate` of 0.06 holds for firms it has
never applied to, which is all of them.

---

## Check 7 — Delegation map and the hard-stop gate

*Evidence: `terminal-02-execute-refused.txt`, `logs/gate-decisions/2026-07-27-effort-reallocator.md`*

**What this engine does, of the three:** it **commits a resource** — my own irreplaceable
application time against an OPT clock. It spends no money and changes no one's access. A
wasted week is not recoverable, and there are not many of them left, which is why the gate
is non-negotiable rather than advisory.

| Component | The tool decides | I decide | Where my judgment overrides |
|---|---|---|---|
| GIGO gate | which rows fail which named check | whether a blocking code is acceptable this week | `--waive CODE --waiver-reason` — written, logged |
| Sponsorship evidence | the Beta posterior and its interval | whether a thin record is worth a slot anyway | slot-level; the tool never hides `n` |
| Fit | a deterministic rubric score | whether the rubric read the role correctly | `role.override` with a documented reason (Ch.11) |
| Liveness | flag vs zero, per policy | **whether a posting is actually live** | mandatory: unreadable boards **block** |
| Timeline | applies my stated factor | the factor itself — it is my input | direct; it is my number |
| Allocation | the ranked slot assignment under caps | whether an alphabetical tie-break is acceptable | tie report names every firm at the cutoff |
| Uncertainty | stability % and intervals | whether a 70.7% move is worth acting on | the floor blocks; I may still decline |
| Execution | assembles the ledger | **everything** | no approver, no move — no exception |

**The hard stop, implemented and demonstrated.** `execute` with no arguments on this run:

```
  gate status: BLOCKED
  BLOCKED — approval cannot clear these:
    [block] GATE_BLOCKING_UNWAIVED: DATASET_NO_RECORD_PROVENANCE
    [block] POSTING_NOT_VERIFIED: DOCUSIGN INC          (+5 more firms)
    [block] MOVE_NOT_STABLE: LINKEDIN CORP -> HUMAN INC (stability 20.7% < 70.0%)
    [block] MOVE_NOT_STABLE: AIRBNB INC -> TELADOC HEALTH INC (18.4% < 70.0%)
    [block] MOVE_NOT_STABLE: ZOOX INC -> VISICON TECHNOLOGIES INC (5.2% < 70.0%)

  NOTHING MOVED. Decision logged: logs/gate-decisions/2026-07-27-effort-reallocator.md
  There is no --force flag. Resolve the blocks or accept the baseline.
```

Exit code 4. Eleven blocks, one flag. Every gate has a stated response and a named
resolver: **block** on an unwaived gate code, an unverifiable posting, or a move below the
stability floor; **flag** on a skip rate under Chapter 15's 50% target, because that one is
a judgment about my own filter and not a fact about a firm.

Approval is auditable and refusals are logged too — the append-only
`logs/gate-decisions/2026-07-27-effort-reallocator.md` holds both the refusal above and the
later approval, each with approver, timestamp, reason, and the full move list. (That
directory is one `DOMAIN.md` lists as planned-but-missing, so the tool closes a documented
repo gap.)

**What it takes to actually move a slot** (`executed/`): switch liveness policy to `block`
so only readable boards are eligible, waive the provenance code in writing, plan for
**11 slots** (so a move that previously cleared the 70% floor only by rounding is never
proposed), then approve with a reason. **Nine moves, all ≥86% stable**, gain **+0.184**
with an 80% interval of **[+0.185, +0.203]** — and the point estimate sits *below* its own
interval, which looks like a bug and is a finding. The point estimate holds `role_quality`
at Chapter 11's 0.0; the Monte Carlo draws it from U[0, 0.20] because the book never pinned
it, and these firms pay above the BLS median, so nearly every draw with a non-zero weight
scores them higher. The interval is not centred on the point estimate because the
recommendation's value depends on a parameter nobody has decided. The tool prints this
rather than hiding the mismatch. The cost of
executability is stated on the same page: Intel and Microsoft are discarded for running the
wrong ATS, and the skip rate falls to **0.0%** — every firm that survives the coverage
filter is an Apply, which means the filter stopped filtering. **Buying executability cost me
the skip-rate signal**, and I would rather see that trade than have it averaged away.

---

## Uncertainty communication

**The one sentence a non-specialist should take from this:** *the tool says moving two
applications to Instacart and Roku is a real improvement and it is confident about that,
but for six of the eight companies it recommends, nobody has checked whether the job
posting is still open — so it refuses to let me act on them until I look.*

**Neither overstated nor understated.** Three of eight moves are reported as *not
distinguishable from no change* rather than as small gains. The gain interval is printed
with a zero marker on the axis. The point estimate and the re-optimised estimate are both
shown so the 6.1% optimism is visible instead of absorbed.

### Where I would not trust this tool

1. **Any claim that moving slots raises my interview probability.** The outcome is
   conditioned on the firm having already selected someone (§5). Trust the ranking as a
   guide to *where sponsorship has happened*, not to where I will be hired.
2. **The absence of a firm from the shortlist.** 5,126 recently funded firms are
   structurally unreachable and 238 deep-record sponsors are excluded by an ATS gap. A
   missing name means "not visible to this tool", never "not worth applying to".
3. **Any `p` at or near 0.95.** The cap saturates, intervals collapse to zero width, and
   firms 10x apart in evidence become indistinguishable (§4, Case B).
4. **`VOLUME_REF`, `base_response_rate`, `REPEAT_SLOT_DECAY`, and the `timeline` factor.**
   All are mine, none has a source, and P5 shows the allocation moves with them.
5. **Every liveness value in the default run.** Six of eight destinations were flagged
   `unverifiable`. The one genuinely causal component of the engine was, in practice, an
   assumption.
6. **The expected-gain number as a rate.** It is composite × 0.06 summed over slots. Read
   it as an ordering of options, not as a forecast of responses.
7. **The `executed/` run's skip rate of 0.0%.** It looks like the filter passing everything
   because the pool is good. It is the filter having nothing left to reject.
8. **Any gain figure whose point estimate sits outside its own interval** — as the
   `executed/` run's does. It is honest reporting of specification uncertainty, and it also
   means the number is not a summary of the distribution behind it.
9. **Anything about pay, team, or whether I would want the job.** Not modelled at all.

---

## What changed during the build

The wrong versions are recorded rather than erased, because the corrections are the evidence
that anything was actually checked.

| What I built | What was wrong | What I changed |
|---|---|---|
| `VOLUME_REF = 100` | `p` saturated at the 0.95 cap for nearly every mid-size sponsor, and the twelve slots were decided **alphabetically** | raised to 500; added a **tie report** that names every firm at the cutoff so an arbitrary cut can never read as a finding |
| Case B detector on interval widths | found nothing — the capped intervals are degenerate, so all widths matched too | compares **approval counts** instead; now finds MAPLEBEAR 498 vs LINKEDIN 4,962 with identical φ |
| Move pairing from a Python set | `from → to` pairs changed between identical runs (hash randomisation) | explicit deterministic sort; found by running twice and diffing |
| Stability floor compared in two places | a 70.0% move was called stable in the proposal and unstable by the hard stop | the uncertainty pass records one `stable` verdict; the hard stop reads it |
| Stability floor via `round(stability, 3)` | `round(0.6995, 3) == 0.700` let a sub-floor move (AIRBNB → APPLOVIN) be **committed** | strict `stability >= 0.70`; display to 2 decimals; executed demo re-planned at **11 slots** so no sub-floor move is proposed |
| Objective claimed a skip-rate constraint | sentence said "subject to … ≥50% skip rate" while the allocator never constrained on it | reworded to Ch.15's own framing: skip rate is a **reported dial**, not an enforced constraint |
| BLS path unguarded | missing `soc_occupation_compact.csv` was swallowed by `FileNotFoundError`; Monte Carlo intervals changed with no refusal | CLI refuses a missing BLS path; gate flags `BLS_TABLE_ABSENT`; file is tracked |
| Composite override | an override with a whitespace-only reason was applied | requires non-empty reason — a **deliberate divergence** from `role-scorer.mjs`, which has this defect |
| Bias audit citing 96.8% missingness | inherited from the prior assignment's report; **my own gate measures 94.9%** | reads the rate this run measured |
| Skip-rate constraint | I intended to enforce ≥50% | **reports** it instead: tightening the threshold until the metric goes green is Goodhart's law with extra steps |

---

## Documented gaps

Per `constraints.md`: a gap that is named scores, a gap that is silent is the failure this
course exists to catch.

- **The profile and baseline are synthetic.** `examples/profile.json` and
  `baseline-allocation.json` are invented so a clean clone runs and so no personal
  job-search data enters a public repo. The composites are real; the `fit` and `timeline`
  inputs driving them are not mine.
- **Liveness was never actually checked in either run.** The `neutral-flagged` policy
  assigns 1.0 and a flag; `block` drops the firm. Neither opens a careers page. The hard
  stop blocks on this rather than papering over it, but the arithmetic still contains an
  unverified gate.
- **The Rung 3 counterfactual is unverifiable.** Whether Amgen had a live matching
  requisition that week cannot be recovered now.
- **The MCAR/MNAR machinery did nothing.** It applied to 0 of 79 pooled candidates,
  because the pool filter admits only firms that already have filing records.
- **No pinned `role_quality` weight.** Chapter 11 leaves it unpinned, so the point
  estimate keeps it at 0.0 — meaning the role-quality signal contributes **nothing** to
  every number in this report. The Monte Carlo draws it from U[0, 0.20] instead of
  resolving it. (The BLS *table* itself is now a required input and is tracked; that is
  a different problem from the unpinned weight.)
- **`ENTITY_COLLISION` flags but does not merge.** Nine firms' histories may be split
  across legal forms, and the engine scores them separately.
- **No figure in `brutalist/` style.** The uncertainty visualisations here are ASCII inside
  the tool's own output, so they reproduce with the run rather than depending on a build
  step. No SVG or PNG was generated, so `npm run audit:layout` has nothing to audit.

---

## AI Use Disclosure

**Tools used.** Cursor with Claude (Opus 5), throughout the build.

**Portions assisted.** Scaffolding the `engine/` module layout and the `argparse` CLI;
writing the exact-Shapley enumeration, the Beta sampling, and the quantile helper in pure
standard-library Python; drafting the Markdown renderers; drafting `constraints.md` from the
assignment rubric; drafting the prose of this report against the committed artifacts.

**How I used it.** Directed, one plan step at a time, with `constraints.md` as the
acceptance gate after each step. I chose what to reallocate (application slots, not hours or
dollars), the stdlib-only constraint, and which skeptical checks to build. Every number in
this report was read back out of a committed artifact rather than accepted from a
description of one.

**What I changed.** All seven rows of the iteration table above. Two are worth naming as
mine: raising `VOLUME_REF` after noticing the allocation had been decided alphabetically —
the AI's arithmetic was correct and the output was meaningless — and refusing to enforce the
skip-rate constraint I had originally specified, because a constraint that makes a process
metric look good is worse than a reported failure. I also rejected the model's initial plan
to use `pandas`, `shap`, and `fairlearn`: dependencies I cannot install on a locked-down
machine are dependencies that make the tool unrunnable when I need it.

**What the AI could not do.** It could not have known that Amgen's zero was a Workday
problem rather than a hiring problem. That fact is not in the dataset, not in the score, and
not in any error message — Amgen appears as `0.000 / Skip` alongside genuinely closed roles,
and the composite gives no way to tell "no posting" from "no adapter". I know it because I
sat through the earlier run, watched a 1,882-approval sponsor score zero, went looking for
why, and found `enabled: false` in `portals.yml` with a comment about the provider. That is
the difference between a firm that will not sponsor and a firm my own tooling cannot see —
and it decides whether I spend a slot there. The model reproduced the arithmetic faithfully
in both cases and had no basis for preferring one reading over the other; **`neutral-flagged`
exists as a policy because I had lived the failure the default was hiding.** It also could
not decide that starving early-stage firms is an acceptable price for calibration. That is a
values judgment about my own scarce week against an OPT clock, and I am the one who bears it.

---

## Verification

| Command | Result |
|---|---|
| `python3 -m unittest discover tools/effort-reallocator/tests` | **38 tests, OK** |
| `node scripts/conformance.mjs tools/effort-reallocator` | **57 files, all conform** |
| `reallocate.py all` | exit **5** (gate blocking) — artifacts written |
| `reallocate.py execute` | exit **4** (10 blocks) — nothing moved, decision logged |
| `reallocate.py allocate --slots 11 --liveness-policy block --waive … ` | exit **0** |
| `reallocate.py execute --approve --approver … --reason …` | exit **0** — ledger written |

Reproduce everything: `tools/effort-reallocator/runs/2026-07-27/README.md`.
