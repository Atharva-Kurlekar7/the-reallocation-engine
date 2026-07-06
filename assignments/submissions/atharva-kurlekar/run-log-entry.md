# RUN_LOG entry (also appended to logs/RUN_LOG.md)

## 2026-07-06 -- ERP-to-AI Engineering triage (sample mode, ats:scan 16 boards, BLS cognitive advisory)

- **Recipe:** `case-erp-to-ai-engineering` v0.1.0 (RUNNABLE-SAMPLE)
- **Inputs:** H-1B mapped CSV (30,369 rows); BLS compact CSV; `data/examples/erp-to-ai-portals.yml` (16 enabled Greenhouse boards); 6 hand-assembled roles in roles.json.
- **Commands:** `npm run verify`; `npm run doctor`; filter-ai-title-sponsors.py; `REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml npm run ats:scan -- --dry-run`; `npm run score`.
- **Result:** 160 applied/mixed sponsors; scan **16 companies · 1,742 jobs · 341 yield**; score Apply 3 / Consider 1 / Skip 2 (33% skip).
- **Gates:** source PASS; hiring-now via ats:scan --dry-run; Fit rubric in mode file.
- **P6 open defect:** scan yield not auto-wired to roles JSON.
- **No private data.**

## AI Use Disclosure

- **What the AI did:** drafted scripts, mode file, assignment docs; configured portals.yml; ran filter + scan + score.
- **What I did:** chose domain, confirmed applied/research taxonomy, set timeline factors, validated canonical run numbers match terminal output.
- **What the AI could not do:** decide personal `data/ats/portals.yml` targets for live runs — stays in private `data/ats/`.
