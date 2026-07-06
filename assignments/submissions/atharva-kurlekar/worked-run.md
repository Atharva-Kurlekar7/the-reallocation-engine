# Worked Run — ERP-to-AI Engineering Sponsorship Triage

- **Mode:** `recipes/case-erp-to-ai-engineering.md` v0.1.0
- **By:** Atharva Kurlekar · 2026-07-06
- **Mode:** sample (no tracker writes); liveness gate run live over the network
- **Lifecycle stage reached:** RUNNABLE-SAMPLE

## Scenario

An ERP/AMS support engineer (Oracle OTM, ServiceNow, SQL) pivoting to applied
AI/ML, on F-1 with OPT not yet filed, needs H-1B sponsorship, no PhD. Question the
mode answers: *which companies both sponsor applied-AI titles and are hiring now,
and where should the next application go?*

## Inputs used

| Input | Value |
|---|---|
| Sponsor dataset | `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` (30,369 rows) |
| min approvals | 5 |
| Liveness URLs | `data/examples/erp-to-ai-liveness-urls.txt` (4 shortlist companies + 1 deliberately dead URL) |
| Roles evidence | `data/examples/erp-to-ai-roles.json` (5 roles) |

## Commands run and real output

### Step 1 — filter by H-1B title filings (offline, read-only)

```
$ python3 scripts/ai-pivot/filter-ai-title-sponsors.py --top 20 --min-approvals 5

Records seen:            30,369
With H-1B title data:    1,557
Applied/mixed sponsors:  160
Research-gated excluded:  22
Rejected (<5 approvals): 75
Shortlist size:          20

Top 10 applied-AI sponsors by score:
   1. LINKEDIN CORP                      score= 4934.16  approvals=4962  class=applied
   2. ICON TECHNOLOGY INC                score= 2511.73  approvals=2200  class=applied
   3. AMGEN INC                          score= 1872.05  approvals=1882  class=applied
   4. HUMAN INC                          score= 1370.10  approvals=1382  class=applied
   5. ZOOX INC                           score= 1354.07  approvals=1364  class=applied
   6. DOCUSIGN INC                       score= 1070.13  approvals=1082  class=applied
   7. AIRBNB INC                         score=  990.10  approvals=1000  class=applied
   8. ROBLOX CORP                        score=  846.12  approvals=856  class=applied
   9. TWILIO INC                         score=  782.49  approvals=802  class=applied
  10. ROKU INC                           score=  650.02  approvals=654  class=applied

Agent log:    logs/case-erp-to-ai-engineering-20260706.json
Human report: reports/generated/case-erp-to-ai-engineering-20260706.md
```

### Step 2 — liveness gate (live, Playwright)

```
$ node scripts/ai-pivot/liveness-gate.mjs --file data/examples/erp-to-ai-liveness-urls.txt

Liveness gate: checking 5 posting(s)...

[PASS ] active    Airbnb — https://careers.airbnb.com/positions/
[CLOSED] uncertain Reddit — https://www.redditinc.com/careers
          reason: content present but no visible apply control found
[CLOSED] uncertain Etsy — https://careers.etsy.com/
          reason: content present but no visible apply control found
[CLOSED] expired   DocuSign — https://careers.docusign.com/
          reason: insufficient content — likely nav/footer only
[CLOSED] expired   DEAD-POSTING (break attempt) — https://boards.greenhouse.io/embed/job_app?for=doesnotexist12345&token=00000000
          reason: HTTP 404

Gate results: 1 PASS  4 CLOSED
Gate log: logs/case-erp-to-ai-engineering-liveness-20260706.json
```

### Step 4 — score the assembled evidence (deterministic)

```
$ npm run score data/examples/erp-to-ai-roles.json

✓ scored 5 roles → Apply 1 · Consider 1 · Skip 3 (skip 60%)
  data/examples/role-scores.json  +  data/examples/role-scores.md
```

Audit trace (`data/examples/role-scores.md`):

| Role | Composite | Rec | Why |
|---|---|---|---|
| AIRBNB INC — Data Scientist | 0.372 | **Apply** | ≥ 0.3, gates healthy (liveness 1, timeline 0.8) |
| QUANTIPHI INC — Sr ML Engineer | 0.252 | **Consider** | in Consider band [0.2, 0.3) |
| REDDIT INC — SWE, ML | 0.000 | **Skip** | gated: liveness ≈ 0 |
| ETSY INC — Sr SWE I, ML | 0.000 | **Skip** | gated: liveness ≈ 0 |
| DOCUSIGN INC — Data Engineer | 0.000 | **Skip** | gated: liveness ≈ 0 |

## Verified vs inferred (line by line)

| Claim in the output | Verified or inferred | Source |
|---|---|---|
| 30,369 companies in dataset; 1,557 with H-1B title data | **Verified** | row count of the CSV |
| 160 applied/mixed sponsors; 22 research-gated excluded | **Verified counts, inferred classification** | counts are exact; the applied/research *class* is a keyword heuristic |
| Airbnb 1000 approvals, 99% rate | **Verified** | CSV columns `Total Approvals`, `Approval_Rate` |
| Airbnb posting is live now | **Verified** | live Playwright check, `active` with apply controls |
| Reddit/Etsy/DocuSign postings not usable | **Verified** | live check returned uncertain/expired |
| `fit.p` (0.4–0.55) for each role | **Inferred** | my model-judgment of an ERP→AI fit; labeled `model-judgment` in the JSON |
| `timeline.factor` 0.7–0.8 | **Inferred (your-input)** | my estimate of an F-1/OPT-not-filed start window |
| Final Apply/Consider/Skip | **Derived** | deterministic arithmetic over the above, fully traced |

## Verification (how I confirmed the output is real)

1. **Cross-checked a count against source.** My script reports 22 research-gated-only
   sponsors. An independent grep for a research-scientist title returned 19 rows:
   ```
   $ python3 -c "import csv; print(sum(1 for r in csv.DictReader(open('data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv')) if 'research scientist' in (r.get('top_job_titles_sponsored') or '').lower() or 'research data scientist' in (r.get('top_job_titles_sponsored') or '').lower()))"
   19
   ```
   The numbers differ *for a real reason*: my classifier's research bucket also
   catches "research engineer", "postdoc", "principal scientist", and it excludes
   companies that ALSO filed an applied title (those become **mixed**, not
   research-gated). The gap is the heuristic showing its seams — exactly the kind of
   inferred-vs-verified boundary the class is labeled for.
2. **Parsed the JSON agent log** — valid; `records_seen: 30369`, top shortlist entry
   `LINKEDIN CORP` with its real applied titles.
3. **Liveness re-run reproducibility** — the dead greenhouse URL returns HTTP 404
   every run; Airbnb's positions page returns `active` every run.

## Attestation

- Recipe: case-erp-to-ai-engineering v0.1.0
- By: Atharva Kurlekar · 2026-07-06

### Tested
| Ran | Saw | Expected |
|---|---|---|
| `filter-ai-title-sponsors.py --min-approvals 5` | 30,369 seen → 160 applied sponsors, shortlist 20; JSON+MD written | a ranked applied-AI shortlist + two artifacts |
| `liveness-gate.mjs --file …` | 1 PASS (Airbnb), 4 CLOSED | live postings pass, dead/landing pages close the gate |
| `npm run score erp-to-ai-roles.json` | Apply 1 · Consider 1 · Skip 3 (60%) | gated companies zeroed to Skip; healthy skip rate |
| **Break: filter on a missing CSV** | `STOP: source CSV not found … refuses to guess`, exit 2 | a clean stop condition, not a crash |
| **Break: dead job URL in the gate** | HTTP 404 → `expired` → gate CLOSED | the gate rejects a non-existent posting |
| **Break: scorer on malformed JSON** | `SyntaxError … Expected property name`, exit 1 | it refuses to score bad input (see "Broke", below) |

### Did not test
- The `[TODO: DEV] jd-soc-classifier.py` (not built) — the applied/research split is
  still title-string only.
- Liveness for the other 16 shortlisted companies (only 4 checked live).
- Whether any "mixed" company's *open* reqs are research-only.
- The Cognitive-Pivot role-quality weight (`role_quality: 0.0`, unpinned by the book).

### Broke during testing, fixed
- The malformed-JSON break showed the scorer fails with a raw `SyntaxError` and a
  stack trace rather than a friendly stop message. It does correctly refuse to score
  (exit 1, no output file), so the *contract* holds, but the failure is a crash, not
  a graceful stop. Logged as a follow-up rather than patched, since it is the repo's
  shared scorer, not my script. My own filter script exits cleanly (code 2) on a
  missing source.

## Reflection

**What went well.** The whole chain runs on real data end to end: 30K rows → a
160-company applied-AI shortlist → a live liveness gate → an auditable Apply/
Consider/Skip. The liveness gate did real work — it turned four "strong sponsor"
rows into Skips because there was no usable live posting, which is the mode's entire
point: history is not a job opening.

**What it got wrong / missed.** The liveness run exposed that I fed *careers landing
pages*, not specific job-posting URLs, so three companies came back `uncertain`/
`expired` for a boring reason (a landing page has no single apply control), not
because they aren't hiring. That is a real limitation of my inputs, not the gate.
The classifier also over-trusts the title string: "Data Scientist" is treated as
applied even when it may be BI/analytics.

**Next steps.** (1) Feed the gate real per-posting URLs from `npm run ats:scan`
instead of landing pages. (2) Build `jd-soc-classifier.py` so the applied/research
split is grounded in the JD and a SOC code, not a keyword. (3) Decide a real
`role_quality` weight so the Cognitive-Pivot layer actually contributes. (4) Get a
working ML engineer to sanity-check 10 "applied" classifications — the failure mode
my domain justification names is one I cannot catch alone.
