# Explanation and its critique — 2026-07-27

**Method:** exact Shapley by coalition enumeration over 32 coalitions of 5 features: `sponsorship`, `fit`, `role_quality`, `liveness`, `timeline`.

*Why not SHAP:* With five features the exact values are cheap, so an approximation would add sampling error for nothing. The additivity identity is asserted in code.

*Reference point:* pool-median vote values; gates at 1.0. The attribution is relative to that reference and changes if the reference changes — a property of every Shapley explanation that plots rarely mention.

## Attributions

| Company | Rec | Composite | φ sponsorship | φ fit | φ role_quality | φ liveness | φ timeline | Exact? |
|---|---|---:|---:|---:|---:|---:|---:|---|
| MAPLEBEAR INC | Apply | 0.428 | +0.0696 | +0.0500 | +0.0000 | +0.0000 | -0.0658 | yes |
| ROKU INC | Apply | 0.428 | +0.0696 | +0.0500 | +0.0000 | +0.0000 | -0.0658 | yes |
| AIRBNB INC | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| DOCUSIGN INC | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| HUMAN INC | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| LINKEDIN CORP | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| PINTEREST INC | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| ROBLOX CORP | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| TELADOC HEALTH INC | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| TWILIO INC | Apply | 0.405 | +0.0696 | +0.0250 | +0.0000 | +0.0000 | -0.0638 | yes |
| VISICON TECHNOLOGIES INC | Apply | 0.398 | +0.0614 | +0.0250 | +0.0000 | +0.0000 | -0.0631 | yes |
| BENEFITS SCIENCE LLC | Consider | 0.279 | -0.0923 | +0.0500 | +0.0000 | +0.0000 | -0.0527 | yes |
| YOSHI INC | Skip | 0.165 | -0.1671 | +0.0000 | +0.0000 | +0.0000 | -0.0426 | yes |

Additivity holds exactly for every row: Σφ = v(full) − v(∅). That is the strongest form of this explanation — which is the point of the next section.

## Counterfactual: what would flip the decision

| Company | Top contributor | Cheapest lever | Δ needed |
|---|---|---|---:|
| MAPLEBEAR INC | sponsorship (+0.0696) | timeline | -0.2542 |
| ROKU INC | sponsorship (+0.0696) | timeline | -0.2542 |
| AIRBNB INC | sponsorship (+0.0696) | timeline | -0.2204 |
| DOCUSIGN INC | sponsorship (+0.0696) | timeline | -0.2204 |
| HUMAN INC | sponsorship (+0.0696) | timeline | -0.2204 |
| LINKEDIN CORP | sponsorship (+0.0696) | timeline | -0.2204 |
| PINTEREST INC | sponsorship (+0.0696) | timeline | -0.2204 |
| ROBLOX CORP | sponsorship (+0.0696) | timeline | -0.2204 |
| TELADOC HEALTH INC | sponsorship (+0.0696) | timeline | -0.2204 |
| TWILIO INC | sponsorship (+0.0696) | timeline | -0.2204 |
| VISICON TECHNOLOGIES INC | timeline (-0.0631) | timeline | -0.2086 |
| BENEFITS SCIENCE LLC | sponsorship (-0.0923) | timeline | +0.0632 |
| YOSHI INC | sponsorship (-0.1671) | sponsorship | +0.4550 |

## Where the explanation is accurate and misleading

All four cases are technically accurate arithmetic. Each one misleads a reader who would act on it: A points effort at the wrong term, B implies two firms are equally well-evidenced, C implies liveness was checked, and D hides that the decision's nearest edge is an assumption rather than a record.

### Case A — additive attribution over a multiplicative function

**MAPLEBEAR INC** — the explanation says sponsorship is the largest contributor (phi = +0.0696); the cheapest way to change the decision is timeline — a change of -0.2542 crosses the threshold.  
The attribution is additive; the composite is multiplicative through the gates. Credit for size and leverage for action are different orderings. A reader who trusts the ranking spends effort on sponsorship when the decision actually turns on timeline.

**ROKU INC** — the explanation says sponsorship is the largest contributor (phi = +0.0696); the cheapest way to change the decision is timeline — a change of -0.2542 crosses the threshold.  
The attribution is additive; the composite is multiplicative through the gates. Credit for size and leverage for action are different orderings. A reader who trusts the ranking spends effort on sponsorship when the decision actually turns on timeline.

**AIRBNB INC** — the explanation says sponsorship is the largest contributor (phi = +0.0696); the cheapest way to change the decision is timeline — a change of -0.2204 crosses the threshold.  
The attribution is additive; the composite is multiplicative through the gates. Credit for size and leverage for action are different orderings. A reader who trusts the ranking spends effort on sponsorship when the decision actually turns on timeline.

**DOCUSIGN INC** — the explanation says sponsorship is the largest contributor (phi = +0.0696); the cheapest way to change the decision is timeline — a change of -0.2204 crosses the threshold.  
The attribution is additive; the composite is multiplicative through the gates. Credit for size and leverage for action are different orderings. A reader who trusts the ranking spends effort on sponsorship when the decision actually turns on timeline.

### Case B — the point estimate hides the sample size

**MAPLEBEAR INC vs LINKEDIN CORP** — sponsorship attributions +0.06957 and +0.06957 over records 10.0x apart.  
MAPLEBEAR INC (498 approvals) and LINKEDIN CORP (4962 approvals) receive a byte-identical sponsorship attribution (+0.06957 vs +0.06957) on records that differ by 10.0x. The attribution is a function of p, and p is capped at 0.95, so every large sponsor collapses onto the same number and the credible intervals collapse with it. A reader comparing these two explanations sees no difference in the evidence, because the explanation has removed it.

**TELADOC HEALTH INC vs LINKEDIN CORP** — sponsorship attributions +0.06957 and +0.06957 over records 9.7x apart.  
TELADOC HEALTH INC (510 approvals) and LINKEDIN CORP (4962 approvals) receive a byte-identical sponsorship attribution (+0.06957 vs +0.06957) on records that differ by 9.7x. The attribution is a function of p, and p is capped at 0.95, so every large sponsor collapses onto the same number and the credible intervals collapse with it. A reader comparing these two explanations sees no difference in the evidence, because the explanation has removed it.

**ROKU INC vs LINKEDIN CORP** — sponsorship attributions +0.06957 and +0.06957 over records 7.6x apart.  
ROKU INC (654 approvals) and LINKEDIN CORP (4962 approvals) receive a byte-identical sponsorship attribution (+0.06957 vs +0.06957) on records that differ by 7.6x. The attribution is a function of p, and p is capped at 0.95, so every large sponsor collapses onto the same number and the credible intervals collapse with it. A reader comparing these two explanations sees no difference in the evidence, because the explanation has removed it.

### Case C — an unverified gate reads as a verified one

**MAPLEBEAR INC** (`checkable-but-unchecked`, φ liveness +0.0000)  
The explanation reports a liveness contribution as if liveness were measured. It was not: this run made no network call, and the gate value reflects ATS provider coverage only. Nothing in the attribution distinguishes 'checked and live' from 'never checked' — the number is identical either way.

**ROKU INC** (`checkable-but-unchecked`, φ liveness +0.0000)  
The explanation reports a liveness contribution as if liveness were measured. It was not: this run made no network call, and the gate value reflects ATS provider coverage only. Nothing in the attribution distinguishes 'checked and live' from 'never checked' — the number is identical either way.

**AIRBNB INC** (`checkable-but-unchecked`, φ liveness +0.0000)  
The explanation reports a liveness contribution as if liveness were measured. It was not: this run made no network call, and the gate value reflects ATS provider coverage only. Nothing in the attribution distinguishes 'checked and live' from 'never checked' — the number is identical either way.

### Case D — the decision's nearest edge is an assumption, not a record

**MAPLEBEAR INC** — cheapest lever `timeline` (-0.2542), provenance `your-input`.  
The smallest change that would flip this recommendation is -0.2542 on `timeline`, whose provenance is `your-input` — my own assumption or an unverified gate, not a filing record. The explanation presents evidence and assumption in the same units and the same chart, so a reader cannot see that the decision's nearest edge is a number I chose rather than a number I found.

**ROKU INC** — cheapest lever `timeline` (-0.2542), provenance `your-input`.  
The smallest change that would flip this recommendation is -0.2542 on `timeline`, whose provenance is `your-input` — my own assumption or an unverified gate, not a filing record. The explanation presents evidence and assumption in the same units and the same chart, so a reader cannot see that the decision's nearest edge is a number I chose rather than a number I found.

**AIRBNB INC** — cheapest lever `timeline` (-0.2204), provenance `your-input`.  
The smallest change that would flip this recommendation is -0.2204 on `timeline`, whose provenance is `your-input` — my own assumption or an unverified gate, not a filing record. The explanation presents evidence and assumption in the same units and the same chart, so a reader cannot see that the decision's nearest edge is a number I chose rather than a number I found.

**DOCUSIGN INC** — cheapest lever `timeline` (-0.2204), provenance `your-input`.  
The smallest change that would flip this recommendation is -0.2204 on `timeline`, whose provenance is `your-input` — my own assumption or an unverified gate, not a filing record. The explanation presents evidence and assumption in the same units and the same chart, so a reader cannot see that the decision's nearest edge is a number I chose rather than a number I found.

## Provenance of each explained term

| Company | Why explained | sponsorship | fit | role_quality | liveness | timeline |
|---|---|---|---|---|---|---|
| MAPLEBEAR INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (checkable-but-unchecked)` | `your-input` |
| ROKU INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (checkable-but-unchecked)` | `your-input` |
| AIRBNB INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (checkable-but-unchecked)` | `your-input` |
| DOCUSIGN INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (unverifiable)` | `your-input` |
| HUMAN INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (unverifiable)` | `your-input` |
| LINKEDIN CORP | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (checkable-but-unchecked)` | `your-input` |
| PINTEREST INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (unverifiable)` | `your-input` |
| ROBLOX CORP | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (checkable-but-unchecked)` | `your-input` |
| TELADOC HEALTH INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (unverifiable)` | `your-input` |
| TWILIO INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (checkable-but-unchecked)` | `your-input` |
| VISICON TECHNOLOGIES INC | in the proposed allocation | `derived` | `model-judgment` | `derived` | `derived (unverifiable)` | `your-input` |
| BENEFITS SCIENCE LLC | thinnest filing record in the Apply/Consider tier — included on purpose to test whether the explanation distinguishes it from a deep record | `derived` | `model-judgment` | `derived` | `derived (unverifiable)` | `your-input` |
| YOSHI INC | widest sponsorship credible interval in the pool | `derived` | `model-judgment` | `derived` | `derived (unverifiable)` | `your-input` |

