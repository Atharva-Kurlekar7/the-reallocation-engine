# Adversarial robustness and fragility — 2026-07-27

The engine is robust to the perturbation everyone tests (proportional noise on the counts) and fragile to the ones nobody does: a single mis-scaled cell, a two-cell identity split, and an evergreen requisition it cannot see at all.

| # | Perturbation | Realistic because | Allocation changed | Fragility distance |
|---|---|---|---|---|
| P1 | vintage shift — one fiscal year of filings removed | the dataset is a snapshot with no per-record date; a refresh shifts every count at once and nothing in the file says so | n/a — undetectable | the allocation changes once approvals are discounted to 70% of their stated value |
| P2 | units error — one Approval_Rate cell on a 0-1 scale | the dataset already mixes scale conventions across columns; one upstream refresh writing a proportion instead of a percentage is a single-line change nobody reviews | **yes** | one cell in 30,369 rows moves MAPLEBEAR INC from 1 slots to 0 |
| P3 | gamed input — an evergreen 'talent pipeline' requisition | large employers keep perpetual reqs open for pipeline building; they pass every automated liveness signal because they are, factually, open postings | n/a — undetectable | zero data change required — the posting is real. No check in this tool can distinguish an evergreen req from a live one |
| P4 | entity split — one firm's history across two legal names | the dataset already contains PELOTON INTERACTIVE INC and PELOTON INTERACTIVE LLC with identical filing counts; the join is by name and nothing resolves them | no | 2 edited cells out of 581 candidate rows move MAPLEBEAR INC from 1 slots to 1 |
| P5 | parameter sweep — VOLUME_REF and repeat-slot decay | both are your-input numbers with no external justification; another analyst would pick different ones and get a different answer from the same data | n/a — undetectable | 5 of 6 plausible VOLUME_REF values and 1 of 6 plausible decay values change the allocation |

## P1 — vintage shift — one fiscal year of filings removed

- **flips_at_approvals_kept**: 0.7

**Fragility distance:** the allocation changes once approvals are discounted to 70% of their stated value

| Approvals kept | Allocation changed | Top company | Skip rate |
|---:|---|---|---:|
| 95% | no | MAPLEBEAR INC | 31.5% |
| 90% | no | MAPLEBEAR INC | 35.8% |
| 85% | no | MAPLEBEAR INC | 36.3% |
| 80% | no | MAPLEBEAR INC | 36.3% |
| 75% | no | ROKU INC | 39.2% |
| 70% | yes | ROKU INC | 39.4% |
| 60% | yes | ROKU INC | 41.8% |
| 50% | yes | ROKU INC | 48.2% |
| 40% | yes | ROKU INC | 53.2% |
| 25% | yes | LINKEDIN CORP | 63.7% |

*Honest limit:* The dataset holds cumulative totals only, so this is a proportional discount and not a true year-by-year replay. The engine cannot distinguish a firm that sponsored heavily in 2016 and stopped from one sponsoring heavily now. That is a data limitation no amount of modelling fixes.

## P2 — units error — one Approval_Rate cell on a 0-1 scale

- **cells_changed**: 1
- **of_total_cells**: 1 of 30,369 rows
- **victim**: MAPLEBEAR INC
- **victim_stated_rate_pct**: 99.2
- **corrupted_to**: 0.992
- **sponsorship_p_before**: 0.95
- **sponsorship_p_after**: 0.0099
- **allocation_changed**: True
- **slots_before**: 1
- **slots_after**: 0
- **gate_catches_it**: True

**Fragility distance:** one cell in 30,369 rows moves MAPLEBEAR INC from 1 slots to 0

*Honest limit:* The gate's RATE_SCALE_ANOMALY check catches this class before scoring, which is why the check exists. Without it the failure is silent: the composite still looks reasonable, just for the wrong company.

## P3 — gamed input — an evergreen 'talent pipeline' requisition

- **victim**: MAPLEBEAR INC
- **liveness_signal**: checkable-but-unchecked
- **engine_behaviour**: the gate opens, the composite stands at 0.428, and up to 3 slots go to a requisition with no hiring manager behind it
- **slots_at_risk**: 3
- **detected_by_any_check**: False

**Fragility distance:** zero data change required — the posting is real. No check in this tool can distinguish an evergreen req from a live one

**What would catch it:** a human reading the posting date, the req ID pattern, and whether the same title has been open for months — Ch.8's five liveness checks done by eye, not by API

*Honest limit:* This is the failure mode the engine is structurally blind to. The hard stop is the only mitigation, and it works only if the human actually looks.

## P4 — entity split — one firm's history across two legal names

- **victim**: MAPLEBEAR INC
- **approvals_before**: 498.0
- **approvals_after**: 249.0
- **cells_changed**: 2
- **tier_before**: proven
- **tier_after**: proven
- **sponsorship_p_before**: 0.95
- **sponsorship_p_after**: 0.8776
- **slots_before**: 1
- **slots_after**: 1
- **allocation_changed**: False

**Fragility distance:** 2 edited cells out of 581 candidate rows move MAPLEBEAR INC from 1 slots to 1

*Honest limit:* The gate flags collisions but does not merge them, because merging two firms that merely share a name would be worse. The residual risk is real and unresolved.

## P5 — parameter sweep — VOLUME_REF and repeat-slot decay

- **allocations_changed_by_volume_ref**: 5 of 6 settings
- **allocations_changed_by_decay**: 1 of 6 settings

**Fragility distance:** 5 of 6 plausible VOLUME_REF values and 1 of 6 plausible decay values change the allocation

| VOLUME_REF | Allocation changed | Top company | Apply tier | Skip rate |
|---:|---|---|---:|---:|
| 25 | yes | DEEPFRAUD TECHNOLOGIES INC | 257 | 14.3% |
| 50 | yes | MAPLEBEAR INC | 257 | 14.3% |
| 100 | yes | MAPLEBEAR INC | 252 | 22.2% |
| 250 | yes | MAPLEBEAR INC | 185 | 26.3% |
| 500 | no | MAPLEBEAR INC | 149 | 31.5% |
| 1000 | yes | ROKU INC | 105 | 36.3% |

| repeat-slot decay | Allocation changed | Distinct companies | Top company |
|---:|---|---:|---|
| 0.25 | no | 12 | MAPLEBEAR INC |
| 0.40 | no | 12 | MAPLEBEAR INC |
| 0.50 | no | 12 | MAPLEBEAR INC |
| 0.65 | no | 12 | MAPLEBEAR INC |
| 0.80 | no | 12 | MAPLEBEAR INC |
| 0.95 | yes | 10 | MAPLEBEAR INC |

*Honest limit:* These are not data errors. They are the analyst's choices, and the recommendation is partly a function of them. Reporting a single allocation without this sweep would overstate how much of the answer comes from the evidence.

## What the coverage bias costs, measured

The `legacy-zero` policy is what the earlier worked run did: a firm whose board the scanner cannot read scores 0.000. Running both policies over the same data turns that bias from an assertion into a number.

| Liveness policy | Apply tier | Skip rate | Slots allocated | Top company | Firms zeroed by policy |
|---|---:|---:|---:|---|---:|
| `neutral-flagged` | 149 | 31.5% | 12 | MAPLEBEAR INC | 0 |
| `legacy-zero` | 15 | 97.4% | 12 | MAPLEBEAR INC | 566 |

## Where I would not trust this tool

- Any firm whose slots depend on fewer than ~25 filings — the interval is wider than the gap to the next candidate.
- Any run where the gate's RATE_SCALE_ANOMALY or ENTITY_COLLISION counts changed since the last refresh.
- Any recommendation whose destination has an unverifiable board, until a human has opened the posting.
- The absolute yield numbers, ever. They inherit a your-input response rate.

