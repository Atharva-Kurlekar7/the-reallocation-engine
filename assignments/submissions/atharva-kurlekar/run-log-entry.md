# RUN_LOG entry (also appended to logs/RUN_LOG.md)

## 2026-07-06 -- ERP-to-AI Engineering triage (sample mode, ats:scan + verify, BLS cognitive advisory)

- **Recipe:** `case-erp-to-ai-engineering` v0.1.0 (RUNNABLE-SAMPLE)
- **Inputs:** H-1B mapped CSV (30,369 rows); BLS compact CSV; `data/examples/erp-to-ai-portals.yml` (16 Greenhouse boards); 6 roles in roles.json.
- **Commands:** `npm run verify`; `npm run doctor`; filter-ai-title-sponsors.py; `REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml npm run ats:scan -- --dry-run`; same + `--verify --company Reddit`; `npm run score`.
- **Result:** 160 applied/mixed sponsors; scan 1,742 jobs → 341 yield (16 Greenhouse boards). Score Apply 2 / Consider 1 / Skip 3 (50% skip).
- **Gates:** source PASS; liveness via ats:scan --verify (not hand URLs); Fit rubric in mode file.
- **No private data.**

## AI Use Disclosure

- **What the AI did:** drafted scripts, mode file, domain justification, worked run; configured sample portals.yml; ran ats:scan dry-run + verify.
- **What I did:** chose domain, confirmed applied/research taxonomy, set timeline factors for my F-1 status, validated scan output against Reddit board.
- **What the AI could not do:** decide which companies belong in my personal portals.yml for live runs — that stays in private `data/ats/`.
