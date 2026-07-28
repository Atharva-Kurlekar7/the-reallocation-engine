# FACTCHECK — effort-reallocator

Every claim checked against the run artifacts in
`the-reallocation-engine/tools/effort-reallocator/video-assets/` (copies of
`tools/effort-reallocator/out/*.md` and the two terminal transcripts), not
against the brief's fact sheet alone.

| Claim (beat) | Verdict | Source | Note |
|---|---|---|---|
| Weekly budget ~12 slots (B01, B23) | ✓ | proposal.md "12 of 12 slots allocated" | |
| Dataset 30,369 rows (B04, B13) | ✓ | terminal-01 line 4; fragility.md P2 "1 of 30,369 rows" | |
| 94.9% rows with no H-1B data (B04) | ✓ | terminal-01 line 15: "H1B_FIELDS_ABSENT flag 28,812 94.9%" | 28,812/30,369 = 94.9% confirmed |
| Moves proposed = 8 (B06) | ✓ | terminal-02 line 6 "moves: 8"; proposal.md move table has 8 rows | |
| Top move: 1 slot ACME ANALYTICS LLC → MAPLEBEAR INC, stability 100% (B06) | ✓ | proposal.md line 15 / terminal-01 line 34 | |
| Expected gain +0.121, 80% CI [+0.117, +0.123] (B08) | ✓ | proposal.md line 55 / terminal-01 line 70 | |
| Unstable moves: HUMAN 20.7%, TELADOC 18.45%, VISICON 5.2% (B07) | ✓ | proposal.md lines 65-70; terminal-01 lines 41-67 | brief's fact sheet says "18.4%" for TELADOC; source says 18.45% — use source value |
| Stability floor 70% (B06-B07) | ✓ | proposal.md / terminal-01 "70.00% floor" | |
| INTEL 13,318 approvals, 0 slots (B10) | ✓ | bias-audit.md starved table | |
| MICROSOFT 12,226 approvals, 0 slots (B10) | ✓ | bias-audit.md starved table | |
| AMGEN 1,882 approvals, 0 slots (B10) | ✓ | bias-audit.md starved table | |
| Starved reason: unsupported ATS, not "won't sponsor" (B11) | ✓ | bias-audit.md "no supported board... (unverifiable)" + sampling row | |
| ATS coverage: supported 4% evidence / 50% slots; unsupported 96% evidence / 50% slots; ratio 0.0265 (B12) | ✓ | bias-audit.md "Grouping: ats_coverage" table | |
| Fragility P2: 1 cell (0.992 vs 99.2%) flips MAPLEBEAR from 1 slot to 0 (B13) | ✓ | fragility.md P2 section, exact values match | |
| Fragility P5: 5 of 6 VOLUME_REF values change allocation (B14) | ✓ | fragility.md P5 table: 5 of 6 rows show "yes" | decay sweep separately shows 1 of 6 — brief conflates the two counts as "5 of 6... 1 of 6"; beat script only claims the VOLUME_REF figure, which is correct as stated |
| 5,126 firms never enter the pool (B21) | ✓ | proposal.md "The blind spot" section: "5,126 firms... NO H-1B filing record" | |
| No --force flag; human must name + reason (B15-B16) | ✓ | terminal-02 line 53 "There is no --force flag" | |
| execute → exit 4, 10 blocks, nothing moved (B15) | ✓ | terminal-02 lines 4-6, 52 "NOTHING MOVED" | |
| "6 destinations have postings nobody has checked" (B16) | ✓ | terminal-02 lines 24-41: 6 POSTING_NOT_VERIFIED blocks (DOCUSIGN, HUMAN, PINTEREST, TELADOC, ZOOX, VISICON) | |
| "3 of the moves are coin flips" (B16) | ✓ | terminal-02 lines 42-50: 3 MOVE_NOT_STABLE blocks | |
| Causal-honesty claim: data measures post-hoc gov't approval, not choice of "me" (B18) | ✓ | proposal.md / bias-audit.md "labels" row: "Approval_Rate is the government's decision on a candidate the firm had already selected" | |
| Skip rate 31.5% vs ≥50% target, reported not enforced; reported as a dial the human reads (B02b, new) | ✓ | proposal.md "Skip rate 31.5%... Reported, NOT enforced" | Now spoken in expanded B02 — added for the 6-min cut |
| Optimizer's curse: fixed-allocation gain +0.11989 vs re-optimized-per-draw +0.12766, optimism +0.00777 (6.1%) (B08b, new) | ✓ | proposal.md "The optimizer's curse, measured" section, exact figures | New beat added for the 6-min cut |
| Two-definitions tradeoff: parity ratio 0.0265 vs calibration deviation +0.46; parity would cost supported-board firms -5.69 slots / unsupported +5.69 slots; 238 deep-record + 322 thin-record firms get nothing either way (B12b, new) | ✓ | bias-audit.md "The tradeoff: two definitions, one budget" section, exact figures | New beat added for the 6-min cut |

## Corrections made from the brief's fact-sheet table to the source artifacts

- TELADOC stability: fact sheet table rounds to "18.4%"; source (proposal.md, terminal-01, terminal-02) gives **18.45%**. The spoken script itself already says "18.45" is not spoken (script says "Three are stubs" without reading exact numbers aloud for B07), so no correction needed to narration; the on-screen bar chart (B07) must use **18.45%**, not 18.4%.
- No other discrepancies found between the brief's fact sheet and the underlying artifacts.

## Unverifiable / assumption-flagged claims (correctly presented as uncertain in the script)

- Sponsorship probabilities (p=0.950) are model outputs, not empirical firm-level certainties — script correctly frames the move as uncertain ("I cannot tell these apart from doing nothing"), never stated as fact.
- "Posting is live" values are explicitly flagged `LIVENESS_UNVERIFIABLE`/`LIVENESS_UNCHECKED` in proposal.md — script's claim in B22 ("not one was actually checked") is accurate to this default run.

## Gate

**GATE: claims hold.** No narration or on-screen number found in the beat sheet contradicts the source run artifacts, subject to the TELADOC rounding note above (chart must use 18.45%, matching source, not the fact sheet's rounded 18.4%). Three added beats (B02b skip-rate dial, B08b optimizer's curse, B12b two-definitions tradeoff) checked against the same artifacts and hold.
