# Reallocation proposal — 2026-07-27

> **Nothing has moved.** This is a recommendation. Committing a slot requires `execute` with a named approver and a written reason.

**Objective:** maximise expected sponsored-interview yield per slot, subject to a per-company cap — with Chapter 15's >=50% skip rate reported as a dial, not enforced as a constraint, because it is a process metric a human reads in two directions.  

**What the objective leaves out:** referrals, my own application quality, interview conversion, salary, team quality, and every firm with no filing record and no supported ATS board.

**Anchor:** Ch.11 'Why liveness and timeline are multipliers, not addends' (composite, threshold 0.3); Ch.2 the reallocation principle; Ch.15 the skip-rate dial.

## The move

| Q | From | To | 80% CI on Q | Stability | Verdict |
|---:|---|---|---|---:|---|
| 1 | ACME ANALYTICS LLC | MAPLEBEAR INC | 1.0–1.0 | 100.00% | directional — the move survives resampling |
| 1 | ACME ANALYTICS LLC | ROKU INC | 1.0–1.0 | 99.95% | directional — the move survives resampling |
| 1 | LINKEDIN CORP | HUMAN INC | 0.0–1.0 | 20.70% | NOT distinguishable from no change — the move appears in only 20.70% of draws, below the 70.00% floor. Treat as 'no evidence to move', not 'evidence to move a little'. |
| 1 | LINKEDIN CORP | PINTEREST INC | 0.0–1.0 | 70.70% | directional — the move survives resampling |
| 1 | ETSY INC | ROBLOX CORP | 0.0–1.0 | 70.25% | directional — the move survives resampling |
| 1 | AIRBNB INC | TELADOC HEALTH INC | 0.0–1.0 | 18.45% | NOT distinguishable from no change — the move appears in only 18.45% of draws, below the 70.00% floor. Treat as 'no evidence to move', not 'evidence to move a little'. |
| 1 | DOCUSIGN INC | TWILIO INC | 0.0–1.0 | 72.55% | directional — the move survives resampling |
| 1 | ZOOX INC | VISICON TECHNOLOGIES INC | 0.0–0.0 | 5.20% | NOT distinguishable from no change — the move appears in only 5.20% of draws, below the 70.00% floor. Treat as 'no evidence to move', not 'evidence to move a little'. |

- **1 slot(s): ACME ANALYTICS LLC → MAPLEBEAR INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.428 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 498 approvals
- **1 slot(s): ACME ANALYTICS LLC → ROKU INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.428 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 654 approvals
- **1 slot(s): LINKEDIN CORP → HUMAN INC**  
  *why leave:* composite 0.405 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.405 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 1382 approvals
  **The destination's postings cannot be checked by the scanner. The hard stop blocks this move until a human verifies a live posting.**
- **1 slot(s): LINKEDIN CORP → PINTEREST INC**  
  *why leave:* composite 0.405 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.405 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 1364 approvals
  **The destination's postings cannot be checked by the scanner. The hard stop blocks this move until a human verifies a live posting.**
- **1 slot(s): ETSY INC → ROBLOX CORP**  
  *why leave:* composite 0.355 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.405 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 856 approvals
- **1 slot(s): AIRBNB INC → TELADOC HEALTH INC**  
  *why leave:* composite 0.405 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.405 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 510 approvals
  **The destination's postings cannot be checked by the scanner. The hard stop blocks this move until a human verifies a live posting.**
- **1 slot(s): DOCUSIGN INC → TWILIO INC**  
  *why leave:* composite 0.405 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.405 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 802 approvals
- **1 slot(s): ZOOX INC → VISICON TECHNOLOGIES INC**  
  *why leave:* composite 0.405 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.398 ≥ 0.3, gates healthy — sponsorship p=0.925 (80% CI 0.919–0.930) over 330 approvals
  **The destination's postings cannot be checked by the scanner. The hard stop blocks this move until a human verifies a live posting.**

## Expected gain, with its uncertainty

Point estimate **+0.121 expected responses per week**, 80% credible interval **[+0.117, +0.123]**.

```
expected additional responses per week   ([ ] = 80% CI, | = point, 0 = no change)
.....0.........................................[=|].....  axis -0.015 to +0.138

per-move stability — share of draws in which the move survives
(70.0% floor marked +; below it the move is reported as no change)
######################################## 100.00%  MAPLEBEAR INC
########################################  99.95%  ROKU INC
########....................+...........  20.70%  HUMAN INC  <- no change
############################+...........  70.70%  PINTEREST INC
############################+...........  70.25%  ROBLOX CORP
#######.....................+...........  18.45%  TELADOC HEALTH INC  <- no change
#############################...........  72.55%  TWILIO INC
##..........................+...........   5.20%  VISICON TECHNOLOGIES INC  <- no change
```

*Scales linearly with base_response_rate (a your-input number) and is computed from an observational proxy. Read the interval, not this number.*

**Verdict:** The gain is positive in 100.0% of draws and the 80% interval [+0.117, +0.123] excludes zero — under the model's own assumptions. That is not the same as being right about the world.

**Point estimate vs interval.** The point estimate falls inside its interval, as expected.

### The optimizer's curse, measured

If the allocation is re-optimised inside every Monte Carlo draw, it adapts to noise nobody can observe, and the reported gain flatters the method rather than describing the decision. Both quantities are computed here so the difference is visible instead of accidental.

- Gain of the allocation actually recommended, held fixed: **+0.11989**
- Gain if the allocation is re-optimised inside every draw: **+0.12766** (80% CI [0.12321, 0.132])
- Optimism: **+0.00777**, i.e. **6.1%** of the naive figure

The re-optimised figure is the one a naive Monte Carlo would print. Any gap between it and the fixed-proposal figure is gain that exists only because the optimiser was allowed to see the noise.

## Ties — where the engine cannot tell candidates apart

Cutoff composite **0.398**. Tie-break rule: *company name, ascending — an arbitrary rule, stated so it cannot masquerade as a finding*.

No excluded firm ties the cutoff, so the selection boundary is not arbitrary in this run.

## Skip rate (Ch.15)

Evaluated **581** companies → Apply 149 · Consider 249 · Skip 183. **Skip rate 31.5%** against a ≥50.0% target.

BELOW the >=50% target — the filter is too loose. Reported, NOT enforced: raising the threshold until the skip rate hits 50% would be optimising the dial instead of the decision, which is Goodhart's law with extra steps. A human decides whether to tighten the profile or accept a loose filter.

*There are two skip rates and quoting only the flattering one would be dishonest. This figure is over companies the scorer actually EVALUATED. The pool filter declined the rest of the dataset before scoring, mostly because they have no filed job titles — which is not a judgment about them, it is the absence of one.*

| Stage | Rows |
|---|---:|
| dataset | 30,369 |
| no filed job titles (never scored) | 28,812 |
| titles present but off-profile | 959 |
| refused by the gate | 15 |
| duplicate identity, first kept | 2 |
| **evaluated by the scorer** | **581** |

### The blind spot

**5,126 firms** have firms with Form D funding in the last 3 years and NO H-1B filing record. A firm has filed job titles only if it has already sponsored someone, so the title filter selects on the very outcome the engine predicts. These firms are not ranked low — they never enter the pool at all. The gate's refusal to read a blank cell as a zero protects the arithmetic and does nothing for these firms, because the pool never sees them. They are also exactly the recently-funded companies the domain's funding thesis says to surface.

The fit vote is computed from filed titles. With no titles there is no fit vote, so the composite cannot exceed sponsorship x 0.35 x timeline = 0.30 even if sponsorship were imputed at its maximum. These firms are structurally unreachable, not merely disadvantaged, and the Monte Carlo missingness scenarios cannot rescue them.

## Target allocation

12 of 12 slots allocated

| Slots | Composite | Sponsorship p (80% CI) | Approvals | Tier | Company | Flags |
|---:|---:|---|---:|---|---|---|
| 1 | 0.428 | 0.950 [0.950–0.950] | 498 | proven | MAPLEBEAR INC | `LIVENESS_UNCHECKED` |
| 1 | 0.428 | 0.950 [0.950–0.950] | 654 | proven | ROKU INC | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 1000 | proven | AIRBNB INC | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 1082 | proven | DOCUSIGN INC | `LIVENESS_UNVERIFIABLE` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 1382 | proven | HUMAN INC | `LIVENESS_UNVERIFIABLE` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 4962 | proven | LINKEDIN CORP | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 1364 | proven | PINTEREST INC | `LIVENESS_UNVERIFIABLE` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 856 | proven | ROBLOX CORP | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 510 | proven | TELADOC HEALTH INC | `LIVENESS_UNVERIFIABLE` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 802 | proven | TWILIO INC | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 1364 | proven | ZOOX INC | `LIVENESS_UNVERIFIABLE` |
| 1 | 0.398 | 0.925 [0.919–0.930] | 330 | proven | VISICON TECHNOLOGIES INC | `FUNDING_STAGE_IMPLAUSIBLE`, `LIVENESS_UNVERIFIABLE` |

## Baseline being argued against

Week of 2026-07-20 — 12 slots, expected yield 0.173.

| Slots | Company | Composite | Status |
|---:|---|---:|---|
| 3 | LINKEDIN CORP | 0.405 | scored |
| 2 | AIRBNB INC | 0.405 | scored |
| 2 | ZOOX INC | 0.405 | scored |
| 2 | DOCUSIGN INC | 0.405 | scored |
| 1 | ETSY INC | 0.355 | scored |
| 2 | ACME ANALYTICS LLC | — | not in the evidence set — no row in the SEC/DOL dataset matched this name, or its filed titles do not match the profile. The engine has NO evidence about it — which is not the same as evidence against it. |

## Requires human verification before any slot is committed

- DOCUSIGN INC
- HUMAN INC
- PINTEREST INC
- TELADOC HEALTH INC
- ZOOX INC
- VISICON TECHNOLOGIES INC

