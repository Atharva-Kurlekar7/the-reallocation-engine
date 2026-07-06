# RUN_LOG entry (also appended to logs/RUN_LOG.md)

## 2026-07-06 -- ERP-to-AI Engineering triage (sample mode, live liveness gate, BLS cognitive advisory)

- **Recipe:** `case-erp-to-ai-engineering` v0.1.0 (RUNNABLE-SAMPLE)
- **Inputs:** H-1B mapped CSV (30,369 rows); BLS compact CSV; 3 Reddit Greenhouse postings + 1 dead URL; 6 roles in roles.json.
- **Commands:** filter-ai-title-sponsors.py; liveness-gate.mjs; npm run score.
- **Result:** 160 applied/mixed sponsors; shortlist 20 with BLS cognitive advisory (15-1252=3.834, 15-2051=gap). Liveness 3 PASS / 1 CLOSED. Score Apply 2 / Consider 1 / Skip 3 (50% skip).
- **Gates:** source PASS; liveness on real job URLs; Fit rubric in mode file.
- **No private data.**

## AI Use Disclosure

- **What the AI did:** drafted scripts, mode file, domain justification, worked run; sourced Reddit Greenhouse posting URLs via public API.
- **What I did:** chose domain, confirmed applied/research taxonomy, set timeline factors for my F-1 status, validated that landing-page liveness failure was an input error not a gate bug.
- **What the AI could not do:** the first liveness run used careers landing pages and failed for the wrong reason — I recognized that real job-posting URLs were needed, which required knowing what a Greenhouse board URL looks like vs a generic careers page.
