# Worked Run — ERP-to-AI Engineering Sponsorship Triage

- **Mode:** `recipes/case-erp-to-ai-engineering.md` v0.1.0
- **By:** Atharva Kurlekar · 2026-07-06
- **Run mode:** sample (no tracker writes); liveness gate run live over the network
- **Lifecycle stage reached:** RUNNABLE-SAMPLE

## Scenario

An ERP/AMS support engineer (Oracle OTM, ServiceNow, SQL) pivoting to applied
AI/ML, on F-1 with OPT not yet filed, needs H-1B sponsorship, no PhD. Question the
mode answers: *which companies both sponsor applied-AI titles and are hiring right now,
and where should the next application go?*

## Inputs used

| Input | Value |
|---|---|
| Sponsor dataset | `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` (30,369 rows) |
| BLS cognitive scores | `data/bls/compact/soc_occupation_compact.csv` |
| min approvals | 5 |
| Liveness URLs | `data/examples/erp-to-ai-liveness-urls.txt` (3 real Reddit Greenhouse postings + 1 dead URL break attempt) |
| Roles evidence | `data/examples/erp-to-ai-roles.json` (6 roles) |

## Commands run and real output

### Step 1 — filter by H-1B title filings + BLS cognitive annotation (offline)

```
$ python3 scripts/ai-pivot/filter-ai-title-sponsors.py --top 20 --min-approvals 5

Records seen:            30,369
With H-1B title data:    1,557
Applied/mixed sponsors:  160
Research-gated excluded:  22
Rejected (<5 approvals): 75
Shortlist size:          20

BLS cognitive source:    data/bls/compact/soc_occupation_compact.csv

Top 10 applied-AI sponsors by score:
   1. LINKEDIN CORP                  score= 4934.16  approvals=4962  SOC=15-2051  cog=gap   class=applied
   2. ICON TECHNOLOGY INC            score= 2511.73  approvals=2200  SOC=15-2051  cog=gap   class=applied
   3. AMGEN INC                      score= 1872.05  approvals=1882  SOC=15-1252  cog=3.834  class=applied
   4. HUMAN INC                      score= 1370.10  approvals=1382  SOC=15-1252  cog=3.834  class=applied
   5. ZOOX INC                       score= 1354.07  approvals=1364  SOC=15-1252  cog=3.834  class=applied
   6. DOCUSIGN INC                   score= 1070.13  approvals=1082  SOC=15-1252  cog=3.834  class=applied
   7. AIRBNB INC                     score=  990.10  approvals=1000  SOC=15-2051  cog=gap   class=applied
   8. ROBLOX CORP                    score=  846.12  approvals=856  SOC=15-1252  cog=3.834  class=applied
   9. TWILIO INC                     score=  782.49  approvals=802  SOC=15-1252  cog=3.834  class=applied
  10. ROKU INC                       score=  650.02  approvals=654  SOC=15-2051  cog=gap   class=applied

Agent log:    logs/case-erp-to-ai-engineering-20260706.json
Human report: reports/generated/case-erp-to-ai-engineering-20260706.md
```

### Step 2 — liveness gate (live, Playwright, real job-posting URLs)

```
$ node scripts/ai-pivot/liveness-gate.mjs --file data/examples/erp-to-ai-liveness-urls.txt

Liveness gate: checking 4 posting(s)...

[PASS ] active    Reddit (Machine Learning Engineer) — https://job-boards.greenhouse.io/reddit/jobs/8026401
[PASS ] active    Reddit (Eng Manager, Ads ML Efficiency) — https://job-boards.greenhouse.io/reddit/jobs/8022366
[PASS ] active    Reddit (Staff Data Engineer) — https://job-boards.greenhouse.io/reddit/jobs/8039702
[CLOSED] expired   DEAD-POSTING (break attempt) — https://job-boards.greenhouse.io/thiscompanydoesnotexist99999/jobs/1
          reason: HTTP 404

Gate results: 3 PASS  1 CLOSED
Gate log: logs/case-erp-to-ai-engineering-liveness-20260706.json
```

### Step 4 — score the assembled evidence (deterministic)

```
$ npm run score data/examples/erp-to-ai-roles.json

✓ scored 6 roles → Apply 2 · Consider 1 · Skip 3 (skip 50%)
  data/examples/role-scores.json  +  data/examples/role-scores.md
```

Audit trace (`data/examples/role-scores.md`):

| Role | Composite | Rec | Why |
|---|---|---|---|
| REDDIT INC — Staff Data Engineer | 0.382 | **Apply** | ≥ 0.3; liveness 1, fit 0.60 (Fit rubric: Data Engineer = high) |
| REDDIT INC — Machine Learning Engineer | 0.346 | **Apply** | ≥ 0.3; liveness 1, fit 0.45 (Fit rubric: ML Engineer = medium) |
| REDDIT INC — Eng Manager, Ads ML Efficiency | 0.271 | **Consider** | in Consider band; fit 0.30 (Fit rubric: Eng Manager = low) |
| DOCUSIGN INC — Data Engineer | 0.000 | **Skip** | gated: liveness 0 (no live posting confirmed this run) |
| AMGEN INC — Data Engineer | 0.000 | **Skip** | gated: liveness 0 (top-volume sponsor, no live posting) |
| QUANTIPHI INC — Sr ML Engineer | 0.000 | **Skip** | gated: liveness 0 |

## Verified vs inferred (line by line)

| Claim in the output | Verified or inferred | Source |
|---|---|---|
| 30,369 companies; 1,557 with H-1B title data | **Verified** | row count of the CSV |
| 160 applied/mixed; 22 research-gated excluded | **Verified counts, inferred class** | counts exact; applied/research class is keyword heuristic |
| Reddit 408 approvals, 97% rate | **Verified** | CSV `Total Approvals`, `Approval_Rate` |
| Reddit ML Engineer / Staff DE / EM postings live | **Verified** | Playwright liveness on real Greenhouse URLs, all `active` |
| AMGEN cog=3.834 (SOC 15-1252); LinkedIn cog=gap (SOC 15-2051) | **Verified where present; gap flagged** | `data/bls/compact/soc_occupation_compact.csv` base occupation |
| target SOC per company (15-1252 vs 15-2051) | **Inferred** | title→SOC heuristic in filter script |
| `fit.p` per role | **Inferred (rubric-bound)** | Fit rubric in mode file; each role cites the table in `_provenance` |
| `timeline.factor` 0.7–0.8 | **Inferred (your-input)** | F-1/OPT-not-filed start window estimate |
| Apply/Consider/Skip | **Derived** | deterministic Ch.11 arithmetic, fully traced |

## Verification (how I confirmed the output is real)

1. **Cross-checked research-gated count** — script reports 22; naive grep for
   "research scientist" returns 19 (broader keyword bucket + mixed sponsors excluded).
2. **BLS cognitive score spot-check** — opened `soc_occupation_compact.csv`; row
   `15-1252.00` shows `cognitive_pivot_score=3.834`; row `15-2051.00` is blank —
   matches filter output `cog=3.834` vs `cog=gap`.
3. **Liveness on real postings** — three Reddit Greenhouse job IDs pass every re-run;
   dead board URL returns HTTP 404 every re-run.

## Attestation

- Recipe: case-erp-to-ai-engineering v0.1.0
- By: Atharva Kurlekar · 2026-07-06

### Tested
| Ran | Saw | Expected |
|---|---|---|
| `filter-ai-title-sponsors.py --min-approvals 5` | 30,369 seen → 160 applied sponsors; BLS cog column (3.834 vs gap); JSON+MD written | ranked shortlist + advisory cognitive scores |
| `liveness-gate.mjs --file …` | 3 PASS (real Reddit Greenhouse postings), 1 CLOSED (404) | real job URLs pass; dead URL closes gate |
| `npm run score erp-to-ai-roles.json` | Apply 2 · Consider 1 · Skip 3 (50%) | liveness-gated sponsors zeroed; healthy skip rate |
| **Break: filter on missing CSV** | `STOP: source CSV not found … refuses to guess`, exit 2 | clean stop condition |
| **Break: dead job URL** | HTTP 404 → `expired` → gate CLOSED | gate rejects non-existent posting |
| **Break: scorer on malformed JSON** | `SyntaxError`, exit 1, no output file | refuses to score bad input |

### Did not test
- `[TODO: DEV] jd-soc-classifier.py` — applied/research split is still title-string only.
- Liveness for the other 17 shortlisted companies (only Reddit checked live this run).
- Whether cognitive_pivot_score should carry weight in the scorer (book leaves it unpinned).

### Broke during testing, fixed
- **First liveness run used careers landing pages** — 4/5 closed for "no apply control."
  Fixed by sourcing real Greenhouse posting URLs from Reddit (a proven applied-AI
  sponsor on the shortlist). Re-run: 3/3 real postings PASS.
- Scorer on malformed JSON crashes with raw SyntaxError (shared repo tool); contract
  holds (exit 1, no score written) but not a graceful stop message.

## Reflection

**What went well.** The full chain runs on three verified data sources (H-1B CSV,
BLS compact CSV, live posting URLs): 30K rows → 160 applied-AI sponsors with advisory
cognitive scores → three live Reddit postings pass the gate → Apply 2 / Consider 1 /
Skip 3. The gate zeroing AMGEN (1,882 approvals) and DocuSign (1,082 approvals) because
no live posting was confirmed is exactly the "history is not intent" lesson the mode
is built to teach.

**What it got wrong / missed.** The title→SOC heuristic maps any company whose applied
titles include "Data Scientist" to 15-2051, which is unscored in BLS — so LinkedIn,
Airbnb, and Roku show `cog=gap` even though they sponsor strong applied-AI work.
The classifier still over-trusts "Data Scientist" as applied ML when it may be BI.

**Next steps.** (1) Feed liveness URLs from `npm run ats:scan` for all 20 shortlist
companies. (2) Build `jd-soc-classifier.py`. (3) Decide whether to give role_quality
weight once the book pins it — until then, keep cognitive scores advisory only.
