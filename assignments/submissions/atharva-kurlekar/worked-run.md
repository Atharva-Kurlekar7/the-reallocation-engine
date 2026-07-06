# Worked Run — ERP-to-AI Engineering Sponsorship Triage

- **Mode:** `recipes/case-erp-to-ai-engineering.md` v0.1.0
- **By:** Atharva Kurlekar · 2026-07-06
- **Run mode:** sample (`--dry-run` on ATS scan — no writes to `data/ats/`)
- **Lifecycle stage reached:** RUNNABLE-SAMPLE

## Before You Start (assignment checklist)

| Step | Done | Evidence |
|------|------|----------|
| Clone repo + `npm install` | Yes | Fork `Atharva-Kurlekar7/the-reallocation-engine`; `node_modules` present |
| Read governing files | Yes | See **Governing files read** below |
| `npm run verify` | Yes | `✓ all conform (machine half of P4)` |
| `npm run doctor` | Yes | `environment: ✓ runnable`; no PII tracked on this branch |
| Real side-effect-free repo run | Yes | `npm run ats:scan -- --dry-run` + `npm run score` |
| Capture terminal output | Yes | Pasted below |
| Personal data private | Yes | Sample uses public CSVs + `data/examples/erp-to-ai-portals.yml` only |

### Governing files read

| File | What it governs |
|------|-----------------|
| **`SNICKERDOODLE.md`** | P3 provenance, P4 gates, P6 recipe/run alignment, attestation format |
| **`DOMAIN.md`** | Runnable commands (`npm run ats:scan`, `npm run score`) |
| **`AGENTS.md`** | Conformance before done; no private data committed |
| **`recipes/README.md`** | Lifecycle frontmatter and `[TODO]` taxonomy |

## Scenario

An ERP/AMS support engineer pivoting to applied AI/ML, on F-1 with OPT not yet filed,
needs H-1B sponsorship, no PhD. Question: *which companies sponsor applied-AI titles
and are hiring right now?*

## Inputs used

| Input | Value |
|---|---|
| Sponsor dataset | `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` (30,369 rows) |
| BLS cognitive scores | `data/bls/compact/soc_occupation_compact.csv` |
| ATS portals config | `data/examples/erp-to-ai-portals.yml` (16 enabled Greenhouse boards) |
| Roles evidence | `data/examples/erp-to-ai-roles.json` (6 roles, hand-assembled from scan yield) |

## Canonical run numbers (single source of truth)

| Metric | Value | Source |
|--------|-------|--------|
| H-1B rows | 30,369 | filter script |
| Applied/mixed sponsors | 160 | filter script |
| Research-gated excluded | 22 | filter script |
| Companies scanned | **16** | `ats:scan --dry-run` |
| Total jobs (API) | **1,742** | `ats:scan --dry-run` |
| Applied-AI yield (after filters) | **341** | `ats:scan --dry-run` |
| Roles scored | 6 | hand-assembled sample |
| Score outcome | Apply 3 · Consider 1 · Skip 2 | `npm run score` |

## Commands run and real output

### Toolchain — `npm run verify`

```
$ npm run verify

conformance: 136 files (78 md · 31 py · 24 js · 1 sh · 1 yaml · 1 json)
✓ all conform (machine half of P4). Adequacy is still the human gate.
✓ manifest check passed (4 warnings)
```

### Toolchain — `npm run doctor` (excerpt)

```
ENVIRONMENT (required)
  ✓ node       v23.11.0
  ✓ python3    Python 3.9.6

RUNNABLE COMMANDS
  ✓ verify  ✓ score  ✓ ats:scan  …

PRIVACY
  ✓ no private/PII paths are tracked

SUMMARY
  environment: ✓ runnable
```

### Step 1 — filter by H-1B title filings + BLS cognitive annotation

```
$ python3 scripts/ai-pivot/filter-ai-title-sponsors.py --top 20 --min-approvals 5

Records seen:            30,369
With H-1B title data:    1,557
Applied/mixed sponsors:  160
Research-gated excluded:  22
BLS cognitive source:    data/bls/compact/soc_occupation_compact.csv

Top 10 (abbreviated):
   1. LINKEDIN CORP     SOC=15-2051  cog=gap   approvals=4962
   3. AMGEN INC         SOC=15-1252  cog=3.834 approvals=1882
   9. TWILIO INC        SOC=15-1252  cog=3.834 approvals=802
```

### Step 2 — ATS scan: hiring-now gate (`npm run ats:scan --dry-run`)

The scan reads each enabled Greenhouse board via public JSON API (zero LLM tokens),
filters by applied-AI title/location keywords, and reports yield. Open postings only
come back from the API — this is the assignment's Job-Ops anchor run.

```
$ REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml \
    npm run ats:scan -- --dry-run

Scanning 16 companies via providers (0 local parser; 0 skipped)
(dry run — no files will be written)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Portal Scan — 2026-07-06
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Companies scanned:     16
Total jobs found:      1,742
Filtered by title:     1,142 removed
Filtered by location:  226 removed
Duplicates:            33 skipped
New offers added:      341

Boards: LinkedIn, Airbnb, Roblox, Twilio, Roku, Reddit, Instacart, Upstart,
Peloton, Figma, Moloco, Discord, Nextdoor, Applovin, PathAI, Yext
```

### Step 3 — assemble role evidence (manual sample)

Six roles hand-picked from the 341-offer scan yield + H-1B shortlist to demonstrate
the scorer. **P6 logged defect:** no script yet maps scan output → roles JSON automatically.

### Step 4 — score

```
$ npm run score data/examples/erp-to-ai-roles.json

✓ scored 6 roles → Apply 3 · Consider 1 · Skip 2 (skip 33%)
```

| Role | Composite | Rec | Gate note |
|---|---|---|---|
| REDDIT — Staff Data Engineer | 0.382 | **Apply** | in scan yield |
| REDDIT — Senior ML Engineer | 0.346 | **Apply** | in scan yield |
| TWILIO — Staff ML Engineer | 0.346 | **Apply** | in scan yield |
| REDDIT — ML Eng Manager | 0.271 | **Consider** | in scan yield |
| AMGEN — Data Engineer | 0.000 | **Skip** | not on scan allowlist (`enabled: false`) |
| QUANTIPHI — Sr ML Engineer | 0.000 | **Skip** | not on scan allowlist |

## Verified vs inferred

| Claim | Verified or inferred | Source |
|---|---|---|
| H-1B approvals, rates, titles | **Verified** | SEC+DOL CSV |
| BLS cognitive_pivot_score (3.834 / gap) | **Verified where present** | BLS compact CSV |
| 16 boards scanned, 1,742 jobs, 341 yield | **Verified** | `ats:scan --dry-run` stdout |
| Role title in scan yield (Reddit, Twilio) | **Verified** | matched against scan report |
| Applied/research class, target SOC | **Inferred** | keyword heuristics |
| fit.p | **Inferred (rubric-bound)** | Fit rubric in mode file |
| Apply/Consider/Skip | **Derived** | Ch.11 scorer |
| Amgen/Quantiphi hiring-now closed | **Not on scan allowlist** | Amgen `enabled:false` in portals.yml; Quantiphi not listed — scan never attempted, not verified absence of postings |

## Attestation

### Tested
| Ran | Saw | Expected |
|---|---|---|
| `npm run verify` | all conform | toolchain valid |
| `npm run doctor` | environment runnable | before push |
| `filter-ai-title-sponsors.py` | 160 applied sponsors + BLS column | shortlist + cognitive advisory |
| `ats:scan --dry-run` | 16 cos · 1,742 jobs · **341 yield** | hiring-now gate from API |
| `npm run score` | Apply 3 / Consider 1 / Skip 2 | scorer on assembled roles |
| **Break: missing CSV** | exit 2, no output | refuses to guess |
| **Break: Amgen wage-in-title** | report flags `Data Engineer 20516.3745` | data-quality section catches CSV artifact |
| **Break: malformed roles JSON** | scorer exit 1 | no score on bad evidence |

### Did not test
- Live scan without `--dry-run` (writes `data/ats/pipeline.md` — needs `[TODO: APPROVE]`)
- `ats:scan --verify` Playwright pass on all 16 companies (optional stricter gate)
- Auto-build roles JSON from 341 scan offers (`[TODO: DEV]`)
- `jd-soc-classifier.py` (not built)

### Broke during testing, fixed
- **Stale cross-artifact numbers (P3):** early docs said 345→84 from a 2-company run while scan later showed 1,742→341 — reconciled to canonical table above.
- **Recipe/run mismatch (P6):** mode file referenced `liveness-gate.mjs`; runtime uses `npm run ats:scan` — template and gates updated.
- **First liveness approach:** hand-picked careers landing pages failed — replaced by ATS API scan.

## Reflection

**What went well.** Filter, scan, and score all run on real data with one consistent
number set. Sixteen Greenhouse boards from the H-1B shortlist produce 341 applied-AI
matches — a credible hiring-now signal without hand URLs.

**What it missed.** Scan finds 341 roles but scoring uses 6 hand-assembled examples —
the pipeline is not closed. Amgen (1,882 approvals) skips because its board is Workday,
not Greenhouse. Amazon/Apple/Google/Infosys/TCS are listed but disabled pending a provider.

**Next steps.** `[TODO: DEV]` script: scan yield → roles JSON; `[TODO: DEV]` Workday provider;
optional `--verify` before live applications.
