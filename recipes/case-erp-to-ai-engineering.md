---
status: RUNNABLE-SAMPLE
todos_open: 4
last_gate: ats-scan-sample, 2026-07-06
attestation: null
recipe_version: 0.1.0
---

# ERP-to-AI Engineering Sponsorship Triage

## Purpose

For an ERP / application-support engineer (Oracle OTM, ServiceNow, SQL) pivoting
to **applied** AI/ML engineering, this mode ranks employers by the job **titles**
they have actually filed H-1B petitions for — separating companies that sponsor
applied-AI work (Machine Learning Engineer, Applied Scientist, Data Engineer)
from those whose only AI filings are **PhD-gated research** (Research Scientist,
Research Data Scientist). It then puts every shortlisted company through a
**hiring-now gate** (`npm run ats:scan --dry-run` — posting must appear in scan
yield on an enabled Greenhouse board) and a **visa-timeline gate** before any
application is recommended.

Use it when: you have transferable data/enterprise-systems experience, you need
H-1B sponsorship, you do **not** have a research doctorate, and you cannot afford
to spend OPT time applying to companies whose "AI hiring" is closed to you.

## Source Inventory

| Source | Type | Exact path / command | Human check |
|---|---|---|---|
| SEC+DOL H-1B mapped dataset | file (CSV) | `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` | Confirm the `top_job_titles_sponsored`, `Total Approvals`, `Approval_Rate`, `latest_funding_*` columns are present. |
| Title-filing filter (this mode's core tool) | script | `python3 scripts/ai-pivot/filter-ai-title-sponsors.py` | Read the applied/research keyword taxonomy; the class is a heuristic, not a fact. |
| ATS portal scan (Job-Ops — hiring now) | script | `REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml npm run ats:scan -- --dry-run` | Fetches live postings from Greenhouse/Lever/Ashby APIs; use `--verify` for Playwright liveness inside the scan. Sample config: `data/examples/erp-to-ai-portals.yml`. |
| Bayesian role scorer | script | `npm run score <roles.json>` (`scripts/score/role-scorer.mjs`) | Combiner only; liveness/timeline are multiplicative gates. |
| BLS/O*NET role quality | file (CSV) | `data/bls/compact/soc_occupation_compact.csv` | Base-occupation `cognitive_pivot_score` per SOC. The filter attaches it as an **advisory** column: 15-1252 (Software Developers) = 3.834; 15-2051 (Data Scientists) is **blank in the source** — surfaced as `gap`, not guessed. |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| sponsor_dataset | CSV path | `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` | Yes |
| min_approvals | int | run flag `--min-approvals` (default 5) | No |
| liveness_urls | text file | Not required when using `npm run ats:scan` — the scan discovers posting URLs from ATS APIs. Optional legacy: `Company \| posting-URL` per line. | No (scan replaces hand URLs) |
| portals_config | YAML | `data/examples/erp-to-ai-portals.yml` (copy to `data/ats/portals.yml` for personal runs) | Yes for the scan step |
| roles_evidence | JSON | derived shortlist in the Ch.11 role-evidence schema (e.g. `data/examples/erp-to-ai-roles.json`) | Yes for scoring |

## Proposed additions

- `[TODO: DEV]` `scripts/ai-pivot/scan-yield-to-roles.py` — build Ch.11 role-evidence JSON
  from `ats:scan --dry-run` output so the 341-offer yield feeds the scorer without hand assembly.
- `[TODO: DEV]` `scripts/ai-pivot/jd-soc-classifier.py` — map a job posting's text to a
  SOC code so the applied/research split is grounded in the JD, not the title string.
  Justification: a title like "Data Scientist" spans SOC 15-2051 (applied) and pure BI
  analytics; only the JD disambiguates. Belongs here because the whole mode turns on
  that distinction.
- `[TODO: DEV]` Workday / proprietary ATS provider for Amazon, Apple, Google, Infosys,
  and TCS US — listed in `data/examples/erp-to-ai-portals.yml` with `enabled: false`
  until a provider exists (today only greenhouse · lever · ashby scan).
- `[TODO: APPROVE]` before any live ATS scan that **writes** to `data/ats/pipeline.md`
  (sample runs use `--dry-run`; no tracker writes without approval).

(The fit-score rubric is now specified in **Fit rubric** below — formerly an open DEFINE item.)

## Fit rubric (ERP/AMS → applied-AI pivot)

Maps an ERP/application-support background (Oracle OTM, ServiceNow, SQL, L2/L3
support) to a bounded `fit.p` for the scorer. Each role's `_provenance` in the
roles JSON cites this table — `fit.p` is a rubric lookup, not a bare model guess.

| Target title pattern | fit.p | Rationale |
|---|---|---|
| Data Engineer | 0.60 | High: SQL + data pipelines + enterprise systems map directly |
| ML Engineer / Software Engineer, ML | 0.45 | Medium: reachable from data/SQL foundation; needs a shipped ML project |
| Applied Scientist / Data Scientist | 0.40 | Medium-low: closer to analytics than engineering for this background |
| Engineering Manager (ML org) | 0.30 | Low: people-management of an ML org is not an IC pivot from support |
| Research Scientist / PhD-gated | 0.10 | Closed door: no research doctorate; do not apply regardless of sponsorship |

## Phase Gates

1. **Source gate** — the sponsor dataset exists and has the title column.
   Test: `test -f data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv && head -1 data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv | rg -q top_job_titles_sponsored`.
2. **Scope gate** — the run declares `sample` mode (no writes to trackers). Test: filter script prints `mode: sample` in its log.
3. **Data-shape gate** — the roles JSON parses. Test: `python3 -m json.tool data/examples/erp-to-ai-roles.json`.
4. **Hiring-now gate (hard stop, not a vote)** — a role advances only if `npm run ats:scan --dry-run`
   lists that title in yield for an enabled Greenhouse board (ATS API returns open postings only).
   Test:
   `REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml npm run ats:scan -- --dry-run`;
   expect `New offers added` > 0 for the company. Optional stricter check:
   add `--verify` (Playwright) before applying — not required for RUNNABLE-SAMPLE.
5. **Visa-timeline gate (hard stop, not a vote)** — the role's start date must fit the authorization window. For F-1 with OPT **not yet filed**, treat any role requiring a start before EAD issuance as gated to zero. Encoded as `timeline.factor` in the roles JSON.
6. **Report gate** — agent log (JSON) and human report (Markdown) both written. Test: `test -f logs/case-erp-to-ai-engineering-<date>.json && test -f reports/generated/case-erp-to-ai-engineering-<date>.md`.

## What it CAN verify

- That a company has an H-1B **approval history** and at what volume/rate (source CSV).
- That its historically sponsored titles include **applied-AI** titles, not only research (title-string heuristic).
- That a company has **open applied-AI postings now** (ATS scan `--dry-run`: Greenhouse API yield after title/location filters).
- Whether a specific posting page still accepts applications (optional `--verify` with Playwright — stricter, not run for every company in the sample).
- The **BLS cognitive_pivot_score** for the mapped target SOC when the base occupation carries one in `data/bls/compact/soc_occupation_compact.csv` (advisory column only — not a gate vote).
- The **arithmetic** of the Apply/Consider/Skip recommendation, term by term, with each term's source.

## What it CANNOT verify

- That an **open** role today is the same applied title the company filed for in the past (history is not intent).
- Whether a "Data Scientist" filing was applied ML or BI/analytics — needs the JD-level SOC classifier (see Proposed additions).
- Whether a company that filed **both** applied and research titles has its *open* reqs gated on a PhD (the "mixed" class is optimistic).
- Any immigration-law conclusion (STEM eligibility, cap-gap) — that is a DSO/attorney decision, never this mode's.

## Steps

1. **Filter by title filings.** Labor: AI, no gate (read-only).
   Script: `scripts/ai-pivot/filter-ai-title-sponsors.py` (reads H-1B CSV + BLS compact CSV).
   Output: shortlist JSON + Markdown report (applied/mixed sponsors ranked; research-gated excluded; advisory SOC + cognitive_pivot_score column).
   Goes to: `logs/`, `reports/generated/`.
2. **ATS scan (hiring now).** Labor: AI with human gate (network).
   Command: `REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml npm run ats:scan -- --dry-run`.
   Output: portal scan report (companies scanned, jobs found, filtered, new offers).
   Goes to: stdout (report); `data/ats/pipeline.md` only on approved live writes (no `--dry-run`).
3. **Assemble role evidence.** Labor: human + AI.
   Combine verified sponsorship (step 1) + scan-listed titles (step 2) + **Fit rubric lookup** + your-input timeline into the Ch.11 role schema.
   **Known gap (P6):** no script yet auto-builds roles JSON from scan yield — this sample hand-assembles 6 roles from the 341-offer scan. Logged, not hidden.
   Output: `data/examples/erp-to-ai-roles.json`.
4. **Score.** Labor: AI, deterministic.
   Command: `npm run score data/examples/erp-to-ai-roles.json`.
   Output: `data/examples/role-scores.{json,md}` — Apply/Consider/Skip with audit trace.
5. **Produce human report + log the run.** Labor: human review.
   Output: report gate artifacts + a `logs/RUN_LOG.md` entry.

## Output Contract

### Agent output (machine)
File: `logs/case-erp-to-ai-engineering-<date>.json`
Fields: workflow, run_id, mode, generated_at, source_file, records_seen,
records_with_h1b_titles, applied_or_mixed_sponsors, research_gated_sponsors,
rejects_below_min_approvals, shortlist, verified_fields, inferred_fields,
todo_items, stop_conditions.

### Human report (reader = you + a mentor/reviewer)
File: `reports/generated/case-erp-to-ai-engineering-<date>.md`
Decision enabled: which companies are worth a real application this week.
Sections: run summary, verified-vs-inferred, shortlist table, next gate.

These are two artifacts on purpose (P5): the JSON is for the next script, the
Markdown is for a human deciding where to spend OPT time. Neither serves both.

## Stop Conditions

- Stop if the sponsor CSV is missing or lacks the title column — the mode refuses to guess (the filter script exits 2).
- Stop if the roles JSON does not parse — no scoring on malformed evidence.
- Stop and mark **Skip** if the hiring-now gate is CLOSED — a historical sponsor
  with no posting in `ats:scan --dry-run` yield (or not on the enabled scan allowlist)
  is not an application target.
- Stop and mark **Skip** if the visa-timeline gate cannot be cleared.
- Stop before any live ATS write, recruiter-policy claim, or immigration conclusion without the approval gate.

## Snickerdoodle

### Run Commands (v0 runtime = Claude Code executes each step; snickerdoodle CLI is roadmap)

```bash
# Step 1 — filter by title filings (offline, read-only)
python3 scripts/ai-pivot/filter-ai-title-sponsors.py --top 20 --min-approvals 5

# Step 2 — ATS scan: hiring-now gate (network, no writes)
REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml \
  npm run ats:scan -- --dry-run

# Step 4 — score the assembled evidence (deterministic)
npm run score data/examples/erp-to-ai-roles.json
```

### Script Locations

| Step | Script | Layer |
|---|---|---|
| Filter by title filings | `scripts/ai-pivot/filter-ai-title-sponsors.py` | tools |
| ATS scan (Job-Ops) | `scripts/ats/scan.mjs` (`npm run ats:scan`) | gate |
| Score | `scripts/score/role-scorer.mjs` (`npm run score`) | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Shortlist agent log | `logs/case-erp-to-ai-engineering-<date>.json` | JSON |
| Shortlist human report | `reports/generated/case-erp-to-ai-engineering-<date>.md` | Markdown |
| ATS scan report | stdout from `npm run ats:scan` | terminal |
| Scored roles | `data/examples/role-scores.{json,md}` | JSON + Markdown |

## RUN_LOG template

```markdown
## <date> -- ERP-to-AI Engineering triage (<mode>)
- Recipe: case-erp-to-ai-engineering v0.1.0
- Inputs: SEC_DOL_H1b_data_mapped.csv; erp-to-ai-portals.yml (<n> enabled boards); roles.json (<n> roles)
- Commands: filter-ai-title-sponsors.py; REALLOCATION_ENGINE_PORTALS=... npm run ats:scan -- --dry-run; npm run score
- Result: <records_seen> seen -> <applied> applied sponsors -> scan <companies> boards, <jobs> jobs, <yield> yield;
  score Apply <a> / Consider <c> / Skip <s> (skip <pct>%)
- Gates: source PASS; hiring-now scan PASS/closed; timeline <...>
- Open issues: <typed TODOs>; P6 defect if scan yield not auto-wired to roles JSON
```
