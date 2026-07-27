# Bias audit — 2026-07-27

The engine allocates MY attention, so the parties advantaged or starved are employers. The harm is not to a protected class of people; it is a systematic, self-reinforcing pattern in which firms ever see an application from a candidate who needs sponsorship.

## Where the bias enters, by stage

| Stage | Mechanism | Evidence in this run |
|---|---|---|
| sampling | a firm appears only if it filed an H-1B petition; non-filers are indistinguishable from would-be sponsors | 94.9% of dataset rows (28,812 of 30,369) carry no H-1B fields, measured by the gate in this run |
| labels | Approval_Rate is the government's decision on a candidate the firm had already selected — not willingness, and not about me | the column is approvals/(approvals+denials) over filed petitions |
| coverage | only greenhouse / lever / ashby boards are checkable, so everything else is either flagged or zeroed by policy | AMGEN INC, 1,882 approvals, scored 0.000 in the earlier worked run because its board is Workday |
| objective | expected yield per slot rewards filing volume, a proxy for firm size | the volume factor saturates at 500 approvals — a your-input parameter |
| feedback | no slots -> no outcomes -> no evidence -> no slots | 322 thin-record firms received zero slots in this run |

## Grouping: `ats_coverage`

*Can the repo's scanner even check this firm's postings? greenhouse / lever / ashby only.*

| Group | Eligible | Apply tier | Slots | Slot share | Evidence share | Slots per firm | Parity gap | Calibration gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| supported ATS board | 15 | 15 | 6 | 50.0% | 4.0% | 0.40000 | +0.4742 | +0.4600 |
| no supported board | 566 | 134 | 6 | 50.0% | 96.0% | 0.01060 | -0.4742 | -0.4600 |

**Allocation parity (disparate impact ratio): 0.0265** — **fails** the four-fifths rule of thumb. Worst-served group: *no supported board* (parity gap -0.4742).  
*1.0 is exact parity. The conventional 0.8 rule of thumb is borrowed from employment law and is a weak analogy here — reported because it is legible, not because it is apt.*

**Calibration:** largest deviation is *supported ATS board* at +0.4600 slot-share points from its evidence share.

## Grouping: `evidence_depth`

*How many filings stand behind the sponsorship estimate.*

| Group | Eligible | Apply tier | Slots | Slot share | Evidence share | Slots per firm | Parity gap | Calibration gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| deep record (>=25 approvals) | 259 | 149 | 12 | 100.0% | 57.2% | 0.04633 | +0.5542 | +0.4281 |
| thin record (<25 approvals) | 322 | 0 | 0 | 0.0% | 42.8% | 0.00000 | -0.5542 | -0.4281 |

**Allocation parity (disparate impact ratio): 0.0000** — **fails** the four-fifths rule of thumb. Worst-served group: *thin record (<25 approvals)* (parity gap -0.5542).  
*1.0 is exact parity. The conventional 0.8 rule of thumb is borrowed from employment law and is a weak analogy here — reported because it is legible, not because it is apt.*

**Calibration:** largest deviation is *deep record (>=25 approvals)* at +0.4281 slot-share points from its evidence share.

## Grouping: `funding_stage`

*Stage of the LAST Form D filing — not the firm's current stage. The gate flags this; the grouping inherits the flaw and says so.*

| Group | Eligible | Apply tier | Slots | Slot share | Evidence share | Slots per firm | Parity gap | Calibration gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| late stage (per last Form D) | 128 | 63 | 6 | 50.0% | 26.3% | 0.04688 | +0.2797 | +0.2370 |
| mid stage (per last Form D) | 239 | 51 | 5 | 41.7% | 41.4% | 0.02092 | +0.0053 | +0.0023 |
| early stage (per last Form D) | 210 | 32 | 1 | 8.3% | 31.4% | 0.00476 | -0.2781 | -0.2309 |
| no stage on record | 4 | 3 | 0 | 0.0% | 0.9% | 0.00000 | -0.0069 | -0.0085 |

**Allocation parity (disparate impact ratio): 0.0000** — **fails** the four-fifths rule of thumb. Worst-served group: *early stage (per last Form D)* (parity gap -0.2781).  
*1.0 is exact parity. The conventional 0.8 rule of thumb is borrowed from employment law and is a weak analogy here — reported because it is legible, not because it is apt.*

**Calibration:** largest deviation is *late stage (per last Form D)* at +0.2370 slot-share points from its evidence share.

## Starved despite deep sponsorship records

238 firms with at least 25 approvals received zero slots because their postings cannot be checked. This is the bias in one table.

| Company | Approvals | Composite | Rec | Liveness status |
|---|---:|---:|---|---|
| INTEL CORP | 13,318 | 0.382 | Apply | `unverifiable` |
| MICROSOFT CORP | 12,226 | 0.382 | Apply | `unverifiable` |
| UBER TECHNOLOGIES INC | 3,984 | 0.382 | Apply | `unverifiable` |
| ICON TECHNOLOGY INC | 2,200 | 0.382 | Apply | `unverifiable` |
| DELOITTE TAX LLP | 2,176 | 0.382 | Apply | `unverifiable` |
| AMGEN INC | 1,882 | 0.382 | Apply | `unverifiable` |
| SNOWFLAKE INC | 1,816 | 0.382 | Apply | `unverifiable` |
| DATABRICKS INC | 1,640 | 0.382 | Apply | `unverifiable` |
| STRIPE INC | 1,250 | 0.382 | Apply | `unverifiable` |
| JUNIPER NETWORKS INC | 1,244 | 0.382 | Apply | `unverifiable` |
| NUTANIX INC | 1,118 | 0.382 | Apply | `unverifiable` |
| ROBINHOOD MARKETS INC | 824 | 0.382 | Apply | `unverifiable` |
| PURE STORAGE INC | 822 | 0.382 | Apply | `unverifiable` |
| ZSCALER INC | 802 | 0.382 | Apply | `unverifiable` |
| ARISTA NETWORKS INC | 702 | 0.382 | Apply | `unverifiable` |

## The tradeoff: two definitions, one budget

**Definition 1 — allocation parity across ATS coverage.** Requires slots per eligible company equal across groups. Current disparate impact ratio: 0.0265.  
*Cost if chosen:* slots would go to firms whose postings nobody can verify, so some fraction of the week would be spent applying into voids — the exact waste the liveness gate exists to prevent.

**Definition 2 — calibration to evidence.** Requires slot share equals evidence-weighted yield share. Largest deviation: +0.4600.  
*Cost if chosen:* firms with thin or no filing record are starved by construction, including the small Form D-funded firms the book's own funding thesis says to surface.

**Why they cannot both hold:** Parity demands slots for the groups with the least evidence; calibration demands slots follow evidence. With a fixed 12-slot budget, satisfying one violates the other — there is no allocation that does both.

**Chosen: calibration to evidence.** The resource is a week of my own life against an OPT clock. I am not a regulator distributing a public good; I am one candidate with twelve applications. Parity across employers is not a duty I owe, and the cost of parity here is applications sent into unverifiable voids.

**What that choice costs, in slots:**

- *supported ATS board*: parity would move -5.69 slots relative to the calibrated allocation.
- *no supported board*: parity would move +5.69 slots relative to the calibrated allocation.
- 238 deep-record firms and 322 thin-record firms receive nothing.

**The uncomfortable part:** This choice starves early-stage firms, which contradicts the book's own thesis that recent Form D funding is a hiring signal worth chasing. The engine's objective and the domain's premise disagree, and the objective currently wins.

## Highest-leverage intervention point

**ATS provider coverage — a Workday/proprietary-board adapter.** It is the only mechanism here that is a tooling gap rather than a data limitation, so it is fixable by writing code rather than by assuming something unknowable. Every other mechanism (missing filings, selection-conditioned labels, size proxy) needs data that does not exist. Coverage needs a provider module.

*Expected effect:* 238 firms with >= 25 approvals currently get zero slots because nobody can check them. Adding one provider moves them from 'flagged, human must verify' to 'checked', which is where the engine's gate is supposed to operate.

*What is not the leverage point:* Reweighting the composite. Tuning weights redistributes among firms the engine can already see, which leaves the mechanism untouched.

