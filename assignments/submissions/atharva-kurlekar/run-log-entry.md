# RUN_LOG entry (also appended to logs/RUN_LOG.md)

## 2026-07-06 -- ERP-to-AI Engineering triage (sample mode, live liveness gate)

- **Recipe:** `case-erp-to-ai-engineering` v0.1.0 (RUNNABLE-SAMPLE)
- **Inputs:** `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` (30,369 rows); `data/examples/erp-to-ai-liveness-urls.txt` (4 shortlist companies + 1 deliberately dead URL); `data/examples/erp-to-ai-roles.json` (5 roles).
- **Commands:** `python3 scripts/ai-pivot/filter-ai-title-sponsors.py --top 20 --min-approvals 5`; `node scripts/ai-pivot/liveness-gate.mjs --file data/examples/erp-to-ai-liveness-urls.txt`; `npm run score data/examples/erp-to-ai-roles.json`.
- **Result:** 30,369 seen -> 1,557 with H-1B title data -> 160 applied/mixed AI sponsors (22 research-gated-only excluded) -> shortlist 20. Liveness: 1 PASS (Airbnb) / 4 CLOSED (Reddit, Etsy, DocuSign landing pages + 1 dead greenhouse URL, HTTP 404). Score: Apply 1 (Airbnb 0.372) / Consider 1 (Quantiphi 0.252) / Skip 3 (liveness-gated to 0.000) — skip 60% (healthy).
- **Gates:** source PASS; scope sample; data-shape PASS; liveness gate did real work (zeroed 3 strong sponsors with no live posting); timeline encoded as `timeline.factor` for F-1/OPT-not-filed.
- **Verification:** cross-checked research-gated count (script 22 vs naive grep 19 — differ because the classifier's research bucket is broader and excludes mixed sponsors); JSON agent log parses; dead URL reproducibly returns 404.
- **Break attempts:** filter on missing CSV -> clean stop (exit 2, "refuses to guess"); scorer on malformed JSON -> refuses to score (exit 1, raw SyntaxError — logged as a graceful-stop follow-up on the shared scorer).
- **Artifacts:** `logs/case-erp-to-ai-engineering-20260706.json`, `logs/case-erp-to-ai-engineering-liveness-20260706.json`, `reports/generated/case-erp-to-ai-engineering-20260706.md`, `data/examples/role-scores.{json,md}`.
- **Open issues (typed TODOs):** `[TODO: DEV] jd-soc-classifier.py` (applied/research split is title-string only); `[TODO: DATA SOURCE]` per-posting URLs from `npm run ats:scan` (landing pages caused 3 uncertain/expired); `[TODO: DEFINE]` ERP->AI fit rubric; `role_quality` weight still 0.0 (unpinned).
- **No private data:** run uses the public 30K CSV and public careers URLs only; nothing from `private/`.

---

## AI Use Disclosure

- **What the AI did:** Claude (via Cursor) wrote the two scripts (`filter-ai-title-sponsors.py`, `liveness-gate.mjs`), drafted the mode file, domain justification, and worked-run write-up, and assembled the roles evidence JSON.
- **What I did:** chose the domain (ERP -> applied-AI, my own pivot), confirmed the applied/research title taxonomy against my knowledge of which titles gate on a PhD, supplied the liveness URLs, judged the `fit.p` values for an ERP background, and set the visa-timeline factor for my actual F-1/OPT-not-filed status.
- **What the AI could not do (specific instance):** the AI initially treated every "Data Scientist" title filing as applied ML. From my own job search I know a large share of "Data Scientist" reqs at non-tech firms are BI/analytics roles that would not move me toward AI engineering. That domain knowledge is why the mode labels the applied/research class **inferred, not verified**, keeps the stage at RUNNABLE-SAMPLE, and makes a JD-to-SOC classifier the top next step. The model cannot tell, from a title string alone, which door is actually open to someone without a PhD — that judgment required my situation.
