# Reallocation proposal — 2026-07-27

> **Nothing has moved.** This is a recommendation. Committing a slot requires `execute` with a named approver and a written reason.

**Objective:** maximise expected sponsored-interview yield per slot, subject to a per-company cap — with Chapter 15's >=50% skip rate reported as a dial, not enforced as a constraint, because it is a process metric a human reads in two directions.  

**What the objective leaves out:** referrals, my own application quality, interview conversion, salary, team quality, and every firm with no filing record and no supported ATS board.

**Anchor:** Ch.11 'Why liveness and timeline are multipliers, not addends' (composite, threshold 0.3); Ch.2 the reallocation principle; Ch.15 the skip-rate dial.

## The move

| Q | From | To | 80% CI on Q | Stability | Verdict |
|---:|---|---|---|---:|---|
| 1 | ACME ANALYTICS LLC | MAPLEBEAR INC | 1.0–1.0 | 100.00% | directional — the move survives resampling |
| 1 | ACME ANALYTICS LLC | ROKU INC | 1.0–1.0 | 100.00% | directional — the move survives resampling |
| 1 | DOCUSIGN INC | ROBLOX CORP | 1.0–1.0 | 100.00% | directional — the move survives resampling |
| 1 | DOCUSIGN INC | TWILIO INC | 1.0–1.0 | 100.00% | directional — the move survives resampling |
| 1 | ZOOX INC | MOLOCO INC | 1.0–1.0 | 98.00% | directional — the move survives resampling |
| 1 | ZOOX INC | NEXTDOOR INC | 1.0–1.0 | 99.85% | directional — the move survives resampling |
| 1 | LINKEDIN CORP | REDDIT INC | 1.0–1.0 | 97.60% | directional — the move survives resampling |
| 1 | LINKEDIN CORP | FIGMA INC | 1.0–1.0 | 90.40% | directional — the move survives resampling |
| 1 | ETSY INC | PELOTON INTERACTIVE INC | 0.0–1.0 | 86.05% | directional — the move survives resampling |

- **1 slot(s): ACME ANALYTICS LLC → MAPLEBEAR INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.428 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 498 approvals
- **1 slot(s): ACME ANALYTICS LLC → ROKU INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.428 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 654 approvals
- **1 slot(s): DOCUSIGN INC → ROBLOX CORP**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.405 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 856 approvals
- **1 slot(s): DOCUSIGN INC → TWILIO INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.405 ≥ 0.3, gates healthy — sponsorship p=0.950 (80% CI 0.950–0.950) over 802 approvals
- **1 slot(s): ZOOX INC → MOLOCO INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.395 ≥ 0.3, gates healthy — sponsorship p=0.841 (80% CI 0.830–0.848) over 200 approvals
- **1 slot(s): ZOOX INC → NEXTDOOR INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.394 ≥ 0.3, gates healthy — sponsorship p=0.836 (80% CI 0.822–0.849) over 222 approvals
- **1 slot(s): LINKEDIN CORP → REDDIT INC**  
  *why leave:* composite 0.405 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.378 ≥ 0.3, gates healthy — sponsorship p=0.938 (80% CI 0.927–0.948) over 408 approvals
- **1 slot(s): LINKEDIN CORP → FIGMA INC**  
  *why leave:* composite 0.405 ≥ 0.3, gates healthy  
  *why arrive:* composite 0.369 ≥ 0.3, gates healthy — sponsorship p=0.830 (80% CI 0.819–0.838) over 188 approvals
- **1 slot(s): ETSY INC → PELOTON INTERACTIVE INC**  
  *why leave:* no sponsorship evidence in the dataset for this firm  
  *why arrive:* composite 0.366 ≥ 0.3, gates healthy — sponsorship p=0.897 (80% CI 0.886–0.908) over 310 approvals

## Expected gain, with its uncertainty

Point estimate **+0.184 expected responses per week**, 80% credible interval **[+0.185, +0.203]**.

```
expected additional responses per week   ([ ] = 80% CI, | = point, 0 = no change)
.....0.......................................|[===].....  axis -0.024 to +0.228

per-move stability — share of draws in which the move survives
(70.0% floor marked +; below it the move is reported as no change)
######################################## 100.00%  MAPLEBEAR INC
######################################## 100.00%  ROKU INC
######################################## 100.00%  ROBLOX CORP
######################################## 100.00%  TWILIO INC
#######################################.  98.00%  MOLOCO INC
########################################  99.85%  NEXTDOOR INC
#######################################.  97.60%  REDDIT INC
####################################....  90.40%  FIGMA INC
##################################......  86.05%  PELOTON INTERACTIVE INC
```

*Scales linearly with base_response_rate (a your-input number) and is computed from an observational proxy. Read the interval, not this number.*

**Verdict:** The gain is positive in 100.0% of draws and the 80% interval [+0.185, +0.203] excludes zero — under the model's own assumptions. That is not the same as being right about the world.

**Point estimate vs interval.** The point estimate sits OUTSIDE its own interval, which looks like a bug and is a finding. The point estimate fixes the role_quality weight at Chapter 11's 0.0 — the value that makes the role-quality signal irrelevant. The Monte Carlo draws it from U[0, 0.2] because the book never pinned it, and the firms this engine allocates to tend to pay above the BLS median, so almost every draw with a non-zero weight scores them higher. The interval is therefore not centred on the point estimate: it is telling you that the recommendation's value depends on a parameter nobody has decided.

### The optimizer's curse, measured

If the allocation is re-optimised inside every Monte Carlo draw, it adapts to noise nobody can observe, and the reported gain flatters the method rather than describing the decision. Both quantities are computed here so the difference is visible instead of accidental.

- Gain of the allocation actually recommended, held fixed: **+0.19433**
- Gain if the allocation is re-optimised inside every draw: **+0.19447** (80% CI [0.18566, 0.20324])
- Optimism: **+0.00013**, i.e. **0.1%** of the naive figure

The re-optimised figure is the one a naive Monte Carlo would print. Any gap between it and the fixed-proposal figure is gain that exists only because the optimiser was allowed to see the noise.

## Ties — where the engine cannot tell candidates apart

Cutoff composite **0.366**. Tie-break rule: *company name, ascending — an arbitrary rule, stated so it cannot masquerade as a finding*.

No excluded firm ties the cutoff, so the selection boundary is not arbitrary in this run.

## Skip rate (Ch.15)

Evaluated **15** companies → Apply 15 · Consider 0 · Skip 0. **Skip rate 0.0%** against a ≥50.0% target.

BELOW the >=50% target — the filter is too loose. Reported, NOT enforced: raising the threshold until the skip rate hits 50% would be optimising the dial instead of the decision, which is Goodhart's law with extra steps. A human decides whether to tighten the profile or accept a loose filter.

*There are two skip rates and quoting only the flattering one would be dishonest. This figure is over companies the scorer actually EVALUATED. The pool filter declined the rest of the dataset before scoring, mostly because they have no filed job titles — which is not a judgment about them, it is the absence of one.*

| Stage | Rows |
|---|---:|
| dataset | 30,369 |
| no filed job titles (never scored) | 28,812 |
| titles present but off-profile | 959 |
| refused by the gate | 15 |
| duplicate identity, first kept | 2 |
| **evaluated by the scorer** | **15** |

### The blind spot

**5,126 firms** have firms with Form D funding in the last 3 years and NO H-1B filing record. A firm has filed job titles only if it has already sponsored someone, so the title filter selects on the very outcome the engine predicts. These firms are not ranked low — they never enter the pool at all. The gate's refusal to read a blank cell as a zero protects the arithmetic and does nothing for these firms, because the pool never sees them. They are also exactly the recently-funded companies the domain's funding thesis says to surface.

The fit vote is computed from filed titles. With no titles there is no fit vote, so the composite cannot exceed sponsorship x 0.35 x timeline = 0.30 even if sponsorship were imputed at its maximum. These firms are structurally unreachable, not merely disadvantaged, and the Monte Carlo missingness scenarios cannot rescue them.

## Target allocation

11 of 11 slots allocated

| Slots | Composite | Sponsorship p (80% CI) | Approvals | Tier | Company | Flags |
|---:|---:|---|---:|---|---|---|
| 1 | 0.428 | 0.950 [0.950–0.950] | 498 | proven | MAPLEBEAR INC | `LIVENESS_UNCHECKED` |
| 1 | 0.428 | 0.950 [0.950–0.950] | 654 | proven | ROKU INC | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 1000 | proven | AIRBNB INC | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 4962 | proven | LINKEDIN CORP | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 856 | proven | ROBLOX CORP | `LIVENESS_UNCHECKED` |
| 1 | 0.405 | 0.950 [0.950–0.950] | 802 | proven | TWILIO INC | `LIVENESS_UNCHECKED` |
| 1 | 0.395 | 0.841 [0.830–0.848] | 200 | proven | MOLOCO INC | `LIVENESS_UNCHECKED` |
| 1 | 0.394 | 0.836 [0.822–0.849] | 222 | proven | NEXTDOOR INC | `LIVENESS_UNCHECKED` |
| 1 | 0.378 | 0.938 [0.927–0.948] | 408 | proven | REDDIT INC | `LIVENESS_UNCHECKED` |
| 1 | 0.369 | 0.830 [0.819–0.838] | 188 | proven | FIGMA INC | `LIVENESS_UNCHECKED` |
| 1 | 0.366 | 0.897 [0.886–0.908] | 310 | proven | PELOTON INTERACTIVE INC | `ENTITY_COLLISION`, `LIVENESS_UNCHECKED` |

## Baseline being argued against

Week of 2026-07-20 — 12 slots, expected yield 0.079.

| Slots | Company | Composite | Status |
|---:|---|---:|---|
| 3 | LINKEDIN CORP | 0.405 | scored |
| 2 | AIRBNB INC | 0.405 | scored |
| 2 | ZOOX INC | — | not in the evidence set — no row in the SEC/DOL dataset matched this name, or its filed titles do not match the profile. The engine has NO evidence about it — which is not the same as evidence against it. |
| 2 | DOCUSIGN INC | — | not in the evidence set — no row in the SEC/DOL dataset matched this name, or its filed titles do not match the profile. The engine has NO evidence about it — which is not the same as evidence against it. |
| 1 | ETSY INC | — | not in the evidence set — no row in the SEC/DOL dataset matched this name, or its filed titles do not match the profile. The engine has NO evidence about it — which is not the same as evidence against it. |
| 2 | ACME ANALYTICS LLC | — | not in the evidence set — no row in the SEC/DOL dataset matched this name, or its filed titles do not match the profile. The engine has NO evidence about it — which is not the same as evidence against it. |

