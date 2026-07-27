# Recipe Run Log

Human-readable history for recipe-driven work.

Use this file to record what was run, what worked, what failed, and what should
be tested next. Keep entries short. Do not include secrets, real phone numbers,
private emails, or sensitive application notes.

## 2026-07-27 -- Effort Reallocator recovery pass (grader findings)

- **Why:** Hostile grade took −35 gating (nothing committed; journal/video blank) and −8
  from two real defects: objective claimed a skip-rate constraint the allocator never
  applied; `round(0.6995, 3) >= 0.70` let a sub-floor move be committed. BLS path was
  unguarded — missing file silently emptied role_quality while Monte Carlo still drew
  its weight.
- **Fixes:**
  1. CLI refuses missing `--bls`; gate flags `BLS_TABLE_ABSENT`; track
     `data/BLS/compact/soc_occupation_compact.csv`.
  2. Objective reworded (allocate / README / report): Ch.15 skip rate is a **reported
     dial**, not an enforced constraint.
  3. Stability: strict `stability >= 0.70`; display to 2 decimals; regression test;
     executed demo at `--slots 11` → 9 moves, all ≥86% stable (APPLOVIN gone).
  4. `search/resume.json` untracked → `private/resume.json`; removed `!search/resume.json`
     gitignore override. `npm run doctor` PRIVACY ✓ (history still holds the earlier
     commit; rewrite declined).
- **Re-run:** `all` exit 5; `execute` exit 4 (10 blocks); `allocate --slots 11 --liveness-policy
  block --waive …` exit 0; `execute --approve …` exit 0. Artifacts refreshed under
  `tools/effort-reallocator/runs/2026-07-27/`.
- **Tests:** 38 OK (added sub-floor stability regression).
- **Still open (author only):** Frictional Journal Entry 1 + reflection §§1–3,5; video
  recording from `VIDEO-OUTLINE.md`.
- **Clean-clone proof:** cloned `origin/mode/atharva-kurlekar-erp-to-ai` to a temp dir;
  `reallocate.py all` → exit 5 with full gate report; 38 tests OK; missing BLS path
  prints `refused: BLS occupation table not found` (non-zero exit). `search/resume.json`
  not tracked in the clone.

## 2026-07-27 -- Effort Reallocator built and run (INFO 7375 "Reallocation Engine, Audited")

- **Tool (new):** `tools/effort-reallocator/` — stdlib-only Python CLI, subcommands
  `gate | allocate | explain | audit | execute | all`. Reallocates a weekly **application-slot
  budget** (12 slots, per-company cap 3). Anchors: Ch.2, Ch.11 composite + 0.3 threshold, Ch.15
  skip-rate dial. Reimplements `scripts/score/role-scorer.mjs` in Python with a **parity test**
  against `data/examples/role-scores.json` and Ch.11's worked example (0.44625 Apply / 0.1785 Skip).
- **Inputs:** `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` (30,369 rows);
  `data/bls/compact/soc_occupation_compact.csv`; `data/examples/erp-to-ai-portals.yml`;
  synthetic `examples/profile.json` + `examples/baseline-allocation.json` (so a clean clone runs).
- **Commands:** `reallocate.py all` → **exit 5** (gate blocking); `reallocate.py execute` →
  **exit 4**, 11 blocks, nothing moved; `allocate --liveness-policy block --waive
  DATASET_NO_RECORD_PROVENANCE --waiver-reason "…"` → exit 0; `execute --approve --approver
  "Atharva Kurlekar" --reason "…"` → exit 0, ledger written.
- **Result:** 581 of 30,369 companies evaluated → Apply 149 / Consider 249 / Skip 183
  (**skip rate 31.5%**, below Ch.15's 50% — reported, deliberately NOT enforced). 8 moves;
  top move 1 slot ACME ANALYTICS LLC → MAPLEBEAR INC at 100% stability; **3 of 8 moves reported
  as "not distinguishable from no change"** (20.7% / 18.4% / 5.2%). Expected gain **+0.121
  responses/week, 80% CI [+0.117, +0.123]**; optimiser's curse measured at **6.1%** of the naive
  figure.
- **Gate:** **BLOCKED** on `DATASET_NO_RECORD_PROVENANCE` (no per-record timestamp/source).
  **94.9% of rows (28,812) carry no H-1B fields** — routed to `unknown`, never imputed to zero.
  81 rows rejected `IDENTITY_AMBIGUOUS` (a check added mid-build: one normalised name with
  conflicting filing histories, e.g. `CHECKR INC` 76/8 vs `CHECKR GROUP INC` blank — the whole
  group is refused, discarding good evidence, because a wrong join yields a confident number
  about the wrong firm). Flags: 22,451 stale funding dates, 9 entity collisions, 3 wage-in-title.
- **Largest finding (blind spot):** **5,126 firms** with recent Form D funding and no filing
  record never enter the pool at all — the pool needs filed job titles for a fit vote, so the
  filter selects on the outcome being predicted. MCAR/MNAR scenarios therefore applied to
  **0 of 79** pooled candidates.
- **Bias:** disparate impact ratio **0.0265** by ATS coverage; **238 firms with ≥25 approvals get
  zero slots** including INTEL (13,318), MICROSOFT (12,226), UBER (3,984), AMGEN (1,882). Chose
  calibration over parity and stated the cost. Leverage point: a Workday/proprietary-board adapter.
- **Fragility:** **one mis-scaled cell in 30,369** removes the top firm's slot; **5 of 6** plausible
  `VOLUME_REF` values change the allocation; an evergreen requisition is undetectable at zero
  data change.
- **Hard stop:** blocks on unwaived gate code, unverifiable posting, or stability < 70%. No
  `--force`. Approvals *and* refusals append to **`logs/gate-decisions/`** — a directory
  `DOMAIN.md` lists as planned-but-missing, so this closes that gap.
- **Iteration (wrong versions kept, not erased):** `VOLUME_REF` 100 → 500 after the twelve slots
  turned out to be decided **alphabetically**; Case-B detector moved from interval widths to
  approval counts (the capped intervals were degenerate); non-deterministic move pairing fixed
  (set iteration); stability floor compared in two places disagreed at 70.0%; bias audit was
  quoting **96.8%** missingness inherited from the earlier assignment while this tool's own gate
  measured **94.9%**.
- **Verification:** `python3 -m unittest discover tools/effort-reallocator/tests` → **37 tests OK**;
  `node scripts/conformance.mjs tools/effort-reallocator` → **56 files conform**.
- **Blockers found in the repo (pre-existing, NOT from this work):**
  1. `npm run verify` fails on `metadata.yaml` — `ModuleNotFoundError: No module named 'yaml'`.
     The system `python3` has no PyYAML. Plan: `pip install pyyaml`, or teach
     `conformance.mjs` to skip YAML when the module is absent instead of reporting a
     content failure. (This tool is stdlib-only precisely to avoid that class of breakage.)
  2. `npm run doctor` **PRIVACY** check fails: **`search/resume.json` is git-tracked** and holds
     real personal data (`basics`, `education`, `work`). Committed earlier in
     `65bfdba`, so it is also in history. **Not touched here** — removing a tracked
     personal file is the user's decision. Plan: `git rm --cached search/resume.json`, move it
     under `private/`, and decide whether history needs rewriting before any public push.
- **Artifacts:** `tools/effort-reallocator/runs/2026-07-27/` (two runs — `default/` refused,
  `executed/` committed — plus four terminal transcripts and a README),
  `logs/gate-decisions/2026-07-27-effort-reallocator.md`,
  `Kurlekar_Atharva_ReallocationEngine.md`, `FRICTIONAL-JOURNAL.md`, `constraints.md`.
- **No private data.** The committed run uses synthetic `examples/` only; `out/` is gitignored.

## 2026-07-06 -- ERP-to-AI Engineering triage (sample mode, live liveness gate, BLS cognitive advisory)

**Superseded** by the entry below (2026-07-06 ats:scan migration). Kept for provenance only.

- **Recipe:** `case-erp-to-ai-engineering` v0.1.0 (RUNNABLE-SAMPLE)
- **Inputs:** `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` (30,369 rows); `data/bls/compact/soc_occupation_compact.csv`; `data/examples/erp-to-ai-liveness-urls.txt` (3 Reddit Greenhouse postings + 1 dead URL); `data/examples/erp-to-ai-roles.json` (6 roles).
- **Commands:** `python3 scripts/ai-pivot/filter-ai-title-sponsors.py --top 20 --min-approvals 5`; `node scripts/ai-pivot/liveness-gate.mjs --file data/examples/erp-to-ai-liveness-urls.txt`; `npm run score data/examples/erp-to-ai-roles.json`.
- **Result:** 30,369 seen -> 160 applied/mixed AI sponsors (22 research-gated excluded) -> shortlist 20 with advisory BLS cognitive scores (15-1252=3.834; 15-2051=gap). Liveness: 3 PASS (real Reddit Greenhouse job postings) / 1 CLOSED (dead board, HTTP 404). Score: Apply 2 (Reddit Staff DE 0.382, Reddit ML Engineer 0.346) / Consider 1 / Skip 3 (Amgen, DocuSign, Quantiphi — strong historical sponsors, no live posting) — skip 50%.
- **Gates:** source PASS (H-1B CSV + BLS CSV); scope sample; data-shape PASS; liveness gate passed on real job URLs; Fit rubric specified in mode file; timeline encoded for F-1/OPT-not-filed.
- **Verification:** research-gated count cross-check (22 vs grep 19); BLS spot-check (15-1252.00=3.834, 15-2051.00 blank); three Greenhouse URLs reproducibly `active`.
- **Break attempts:** missing CSV -> stop exit 2; dead URL -> HTTP 404 gate CLOSED; malformed JSON -> scorer exit 1.
- **Artifacts:** `logs/case-erp-to-ai-engineering-20260706.json`, `logs/case-erp-to-ai-engineering-liveness-20260706.json`, `reports/generated/case-erp-to-ai-engineering-20260706.md`, `data/examples/role-scores.{json,md}`.
- **Open issues:** `[TODO: DEV] jd-soc-classifier.py`; `[TODO: DATA SOURCE]` automated posting URLs via `npm run ats:scan` (hand-sourced Reddit URLs for this run only); `role_quality` weight unpinned by book — cognitive scores stay advisory.
- **No private data:** public CSVs and public job-posting URLs only.

## 2026-06-12 — Wrote Tutorial 00 (Exercise Zero) in full

- **Recipe:** manual
- **Inputs:** `docs/search-profile-design.md` v3, `data/bls/compact/soc_occupation_compact.csv` schema, MYCROFT.md attestation rules
- **Outputs:** `docs/tutorials/00-personal-layer.md` — privacy-first setup (gitignore gate), paste-ready agent prompt (3 tasks with hard stops), resume.json schema with evidence fields and attested timestamp, full 8-question conditional intake tree (visa block only after a "no" at Q4), gaps draft with 3 required student edits (kill a row / rewrite a row / write one startable plan), migration rule, 4 exercises (delete test, inflation hunt, multi-model SOC second opinion, six-hour test), what-can-go-wrong table; index updated to ready
- **Result:** Exercise Zero runnable today in Claude Code with zero new scripts. Extraction-corrections count gives each student a personal fluency-vs-truth measurement on day one.
- **Open issues:** SOC matching quality from free text untested against real student answers; the agent prompt should be re-tested once the config generator lands (Tutorial 01 hand-edit note then changes); per-section attestation flags deliberately omitted in favor of one file-level timestamp — revisit if students attest carelessly.

## 2026-06-12 — Dropped personas for conditional intake; added gaps file + Exercise Zero

- **Recipe:** manual (human design input: don't invent personas, ask for relevant facts — past for resume, future for wants/constraints; generate an editable gaps file; gaps migrate to resume with evidence; this is the first exercise)
- **Inputs:** `docs/search-profile-design.md` v3, `data/bls/compact/soc_occupation_compact.csv` (skill_*_lv / ability_*_lv columns)
- **Outputs:** design doc revised — personas replaced by conditional intake over canonical fields (question tree branches on answers, no labels); new gaps-file section (generated draft from O*NET levels + scanned-posting keyword frequency, human-owned thereafter, regenerate-as-diff, migration-to-resume.json only with evidence); Exercise Zero defined; tutorials index gains Tutorial 00 (planned)
- **Result:** Personal layer is three files with distinct epistemic status: resume.json (attested past), profile.yml (declared future), gaps.md (managed delta). Aspirational resume entries become structurally impossible. Engine extends from application allocator to development allocator (gaps = what to build in the six hours).
- **Open issues:** gap computation quality unknown until tried against a real resume + SOC pair; Tutorial 00 not yet written; intake question tree not yet drafted.

## 2026-06-12 — Added profile metadata + personas to the design

- **Recipe:** manual (human design input: resume facts ≠ search metadata; US citizens shouldn't see visa questions; start with a few personas, add later)
- **Inputs:** `docs/search-profile-design.md` v2
- **Outputs:** new "Profile metadata" section — four starting personas (international student, US new grad, employed-and-quietly-looking, flexible/part-time); two-layer model: canonical profile fields + personas as intake routing/defaults only; scorer weights become a function of profile fields (sponsorship weight ≈ 0 for citizens, timeline gate persona-conditional)
- **Result:** Persona proliferation avoided — combinations are field combinations, not new personas; engine reads fields, never labels. New-persona criterion is evidence-driven (recurring intake combinations the presets serve badly).
- **Open issues:** discretion mechanics for the employed persona (employer-affiliate exclusion list source?); whether persona presets live in data/ as a versioned file (recommended) or in the intake recipe prose.

## 2026-06-12 — Revised profile design: roles-first intake + resume.json layer

- **Recipe:** manual (human design input: never ask for companies; ask what they want to do → SOC codes → suggest companies; resume converted to verified JSON, generated docs derive from it)
- **Inputs:** `docs/search-profile-design.md` v1, `data/bls/compact/soc_occupation_compact.csv`, `scripts/resumes/`
- **Outputs:** design doc revised — 5-step pipeline (intake → SOC resolution with human confirmation gate → generate → review/prune → scan); new resume.json section (upload → extract → field-by-field human attestation → all resume artifacts generated as projections, never rewrites); search/ layout extended; course-project mapping section (student H-1B probability tools and resume-JSON converters are the engine's missing components)
- **Result:** Companies are now an output of the engine, not an input. Resume claims become machine-checkable against attested source fields — verified-data contract extended to the student's own history.
- **Open issues:** unchanged 4 open decisions + new: JSON Resume schema as-is vs extended; where extraction-hallucination checking lives (conformance script vs gate checklist).

## 2026-06-12 — Designed profile-driven config generation

- **Recipe:** manual (triggered by human design question: why does a human hand-edit portals.yml?)
- **Inputs:** `recipes/_profile.template.md`, `scripts/ats/detect-ats.py`, `data/bls/compact/soc_occupation_compact.csv` (alternate_titles columns), `data/80-days-to-stay/`, `scripts/ats/scan.mjs` (REALLOCATION_ENGINE_PORTALS env var)
- **Outputs:** `docs/search-profile-design.md` (intake → search/profile.yml → generated portals.yml with O*NET + curated synonym expansion, evidence-derived company suggestions, gitignored personal `search/` folder); Tutorial 01 Step 1 reframed (hand-editing = looking under the hood, not steady state)
- **Result:** Design connects four existing-but-disconnected pieces: profile template, detect-ats.py, O*NET alternate titles, sponsorship data. Human reads/judges generated config; never writes it.
- **Open issues:** Generator script, synonyms seed file, profile recipe, and `.gitignore` entry not yet built — design awaits approval on 4 open decisions (folder name, intake form, suggestion cap, fate of personal files in data/ats/).

## 2026-06-12 — Verified Greenhouse API liveness; fixed tutorial browser-check step

- **Recipe:** manual (triggered by human observation: `job-boards.greenhouse.io/databricks` redirects to the company careers site; same pattern at Duolingo)
- **Inputs:** `scripts/ats/providers/greenhouse.mjs` (read: provider derives `boards-api.greenhouse.io/v1/boards/<slug>/jobs` and fetches with `redirect: 'error'`); fetched the Databricks and Duolingo API endpoints directly
- **Outputs:** `docs/tutorials/01-first-scan.md` Step 6 rewritten (verify against the API JSON, not the board page, with explanation of the redirect pattern); new what-can-go-wrong row
- **Result:** Both APIs live and serving: Databricks ≈97 KB payload, 100+ postings; Duolingo ≈78 KB, ≈80 postings. The browser redirect is a UI relocation, not an API removal — human-facing board pages increasingly redirect to branded careers sites while the JSON API keeps serving. Scanner unaffected by design (API-only + redirect:'error'). This partially closes the prior open issue "provider fetch not verified": the endpoint is confirmed reachable and serving from this environment's fetch tool, though still not via the scanner process itself.
- **Open issues:** Job counts are approximate (counted from match listings, not a parsed total). If Greenhouse ever moves or gates boards-api, the provider fails loudly (`fetch failed` / redirect error) — correct behavior, but worth a tutorial-02 liveness note. Some companies may genuinely leave Greenhouse; a redirected board page plus a 404 from boards-api is the signature of that case.

## 2026-06-12 — Added tutorials layer (docs/tutorials/)

- **Recipe:** manual
- **Inputs:** `data/ats/portals.example.yml`, `scripts/ats/scan.mjs` (usage header, flags, default paths), `package.json`, MYCROFT.md conventions
- **Outputs:** `docs/tutorials/01-first-scan.md` (full predict→run→inspect→judge→record walkthrough with 6 graduated exercises and a what-can-go-wrong table), `docs/tutorials/README.md` (index; tutorials 02–05 marked planned), `DOMAIN.md` first-win section now points to the tutorial
- **Result:** The first-win command is no longer a bare one-liner; a student can complete the scan loop unassisted. Exercise 6 rehearses the attestation format; exercise 4 teaches the conformance/adequacy boundary by deliberate breakage.
- **Open issues:** Sample output numbers in Step 5 are illustrative (live fetch is blocked in this sandbox — could not capture a real success report). Tutorials 02–05 are titles only. Exercise 4's typo-provider behavior was not executed; the tutorial asks the student to discover it, but an instructor should verify the actual error message once on an unrestricted machine.

## 2026-06-12 — First honest run: BLS extract + ATS scan dry-run

- **Recipe:** manual (pre-recipe verification run under MYCROFT.md contract)
- **Inputs:** `scripts/bls/extract-soc-occupation-table.py` against `data/bls/db-30-2-text/` + `data/bls/oesm24nat/`; `npm run ats:scan -- --dry-run` with `REALLOCATION_ENGINE_PORTALS=data/ats/portals.example.yml`
- **Outputs:** `data/bls/compact/soc_occupation_compact.csv` (1,016 occupations; SHA-256 recorded in audit), `data/bls/bls-audit.md` (962/1,016 = 94.7% matched to OEWS 2024 detailed SOC rows)
- **Result:** BLS extractor runs clean after the `Skills.txt` fix; audit generated and read; CSV schema unchanged (`skill_*` columns intact). ATS scan loaded the example portal config, matched the Greenhouse provider, ran filter/dedup/report logic, and wrote nothing in dry-run mode — machinery verified.
- **Open issues:** ATS scan's live fetch failed in the sandboxed environment (network egress blocked) — provider fetch is **not** verified end-to-end; rerun on an unrestricted machine. BLS extractor was not executed pre-fix, so "failed before fix" is inferred from the missing `Recipes.txt` file, not observed. `playwright`/`sharp` not installed; only `js-yaml`/`glob` were needed for this run.

## 2026-06-12 — Fixed rename-shrapnel bugs; added lifecycle frontmatter

- **Recipe:** manual
- **Inputs:** `scripts/bls/extract-soc-occupation-table.py`, `scripts/ats/analyze-patterns.py`, `scripts/ats/README.md`, 8 core recipe files
- **Outputs:** three one-line fixes (`Recipes.txt`→`Skills.txt`; `modes/RUN_LOG.md`→`logs/RUN_LOG.md` in script and README; audit prose "recipe Level scores"→"skill Level scores"); MYCROFT.md lifecycle frontmatter added to `_shared` (type: contract) and `scan`, `pipeline`, `oferta`, `tracker`, `pdf`, `patterns`, `update` (status: DRAFT, todos_open: 11 each)
- **Result:** Known defects 1–2 from DOMAIN.md closed. Recipe status is now machine-readable.
- **Open issues:** `scripts/cowork-agentic-repo.py` still contains mangled prose ("Recipes and recipes…") — cosmetic, not load-bearing. The 33 non-core recipes have no frontmatter yet.

## 2026-06-11 — Established MYCROFT.md as source of truth

- **Recipe:** manual
- **Inputs:** architecture review of the full repo; Codex cross-review; Gru SDD; principles discussion (Cowork session)
- **Outputs:** `MYCROFT.md` (new — constitution v0.1.0: 8 principles, verification stack, recipe lifecycle, TODO-closure evidence, attestation format), `DOMAIN.md` (new — domain manifest: actual layout, runnable command surface, known gaps/defects), `CLAUDE.md` (rewritten as pointer to MYCROFT.md), `AGENTS.md` (rewritten as pointer; also removed "recipes, recipes" rename shrapnel)
- **Result:** One governing file; precedence rule explicit; current-vs-planned architecture separated (domain layout is current; `data/raw`/`data/verified`/snickerdoodle CLI marked roadmap). Claude Code named as v0 runtime.
- **Open issues:** Known defects listed in DOMAIN.md §Known gaps: BLS `Recipes.txt` bug, `modes/RUN_LOG.md` path bug, scorer unimplemented, no recipe has a logged run, doctor script not built, person-named recipes need privacy review, skill/recipe terminology in manuscript unreconciled. README and `docs/` not yet updated to cite MYCROFT.md.

## 2026-05-28 — Recipe folder converted to verified-data workflows

- **Recipe:** manual
- **Inputs:** `recipes/`, `scripts/`, `README.md`, `DATA_CONTRACT.md`
- **Outputs:** `recipes/_shared.md`, `recipes/README.md`, active recipes, and draft/helper recipe files
- **Result:** Recipes now point students toward repo scripts, audits, and logs instead of prompt-only recipes.
- **Open issues:** Some workflows remain intentionally marked as draft until supporting scripts exist.

## 2026-05-28 — Removed copied Job-Ops source tree

- **Recipe:** manual
- **Inputs:** `data/career-ops-main/`, `scripts/ats/`, `recipes/`, `resumes/`
- **Outputs:** `.gitignore`, `README.md`, `DATA_CONTRACT.md`, provider docs
- **Result:** Removed the copied reference directory after useful pieces had been adapted into maintained repo paths.
- **Open issues:** Provenance now lives in docs and adapted files, not in a local source copy.

## 2026-05-28 — Normalized data directory names

- **Recipe:** manual
- **Inputs:** old mixed-case 80 Days and BLS data directories, `data/sec/form-d/`
- **Outputs:** `data/80-days-to-stay/`, `data/bls/`, lower-kebab SEC extracted folders, updated docs/scripts
- **Result:** Source/reference data directories now use lower-case kebab-case names. Maintained automation now uses lowercase `scripts/` by repo convention.
- **Open issues:** Some source data filenames and JSON field values still preserve upstream naming.

## 2026-06-13 -- Context parity + privacy pass + doctor (consolidated; re-logged after a git reset dropped prior entries)

- **Parity:** brought this repo to the Madison/Mycroft context architecture — ported `conformance.mjs`/`to-markdown.mjs`/`build-instructions.mjs`, added `instructions/` (6 shared rule modules + `reallocation-engine.md` + manifest) compiling to generated root `AGENTS.md`/`CLAUDE.md`, plus `.claude/` hooks (archive-guard + conformance-check) and `.github/workflows/verify.yml` (conformance + instruction drift guard). `MYCROFT.md` confirmed identical to the other Mycroft-domain repos.
- **Privacy pass (gap #6):** 14 person-named case-study recipes anonymized -> `case-*.md` role slugs; student names + Canvas submission-IDs scrubbed. Verified zero residual PII repo-wide. Git **history** also purged via `git filter-repo` (--invert-paths on the 14 old paths + --replace-text on names/IDs); force-pushed.
- **doctor (gap #5):** `scripts/doctor.mjs` (`npm run doctor`) — environment + npm-command-target + domain-dir checks + recipe-status dashboard. Surfaced gap #8: only 7/42 recipes carry lifecycle frontmatter; declared todos_open (77) vs 518 body `[TODO` markers.
- **Note:** a later `git reset`/`filter-repo` reverted edits to pre-existing tracked files (DOMAIN.md gaps reconciliation, this log, package.json scripts, generated AGENTS/CLAUDE) while new files survived; re-applied 2026-06-13. New files were unaffected.
- **Result:** doctor + conformance green; DOMAIN.md known-gaps reconciled (#1,#2,#5,#6 resolved; #3,#4,#7,#8 open).

## 2026-06-13 -- Backfill recipe lifecycle frontmatter (gap #8)

- **Commands:** One-off migration over recipes/ (excl. README + templates): prepended a `status/todos_open/last_gate/attestation/recipe_version` block to the 34 recipes that lacked one, injected the lifecycle keys into `_shared.md` (kept `type: contract`), and reconciled `todos_open` to the true `[TODO`-marker body count everywhere. 7 already-stamped recipes unchanged (idempotent).
- **Result:** doctor now reports 42/42 recipes with frontmatter, 0 missing; declared todos_open == body markers (518 = 518, mismatch gone). Conformance clean. DOMAIN gap #8 resolved.
- **Open issues:** All 42 remain `status: DRAFT` — promotion past DRAFT still requires a real gated run (gap #4) + attestation. Frontmatter is now the substrate for that lifecycle tracking.

## 2026-06-13 -- Build the Bayesian Role Scorer (gap #3)

- **Skill:** Implement the book's Chapter-11 decision core — the composite role scorer / combiner.
- **Inputs:** spec from `chapters/11-the-bayesian-role-scorer.md` (composite form, weights sponsorship 0.35 / fit 0.30, multiplicative liveness+timeline gates, threshold ~0.3, Apply/Consider/Skip, override discipline, auditability thesis) + `docs/search-profile-design.md` (weights are a function of the profile, not constants). Confirmed exact structure by reproducing the chapter's worked example backward.
- **Commands:** Wrote `scripts/score/role-scorer.mjs` — combiner only (reads per-role evidence records; does not compute components). Multiplicative gates × weighted votes; profile-conditional sponsorship weight (→0 when authorization doesn't need sponsorship); per-term audit trace with source labels (record / model-judgment / your-input); documented-override support (override without a reason is ignored, per Ch.11); JSON + Markdown report + skip-rate summary. Config block annotates every weight/threshold with provenance; role_quality weight + Consider floor left as documented `[VERIFY]` defaults (not pinned by the chapter). Built fixture `data/examples/ch11-roles.json` reproducing the chapter's two roles + gate/Consider/override cases. Wired `npm run score`.
- **Result:** Verified against the book — Cambridge biotech composite 0.446 → Apply; identical-fit non-sponsor 0.178 → Skip; ghost posting gated to 0 → Skip; Likely-tier → Consider; documented override flips Skip→Apply and records the reason. Conformance clean; doctor sees the new command. DOMAIN gap #3 resolved.
- **Open issues:** `[VERIFY]` weights (role_quality, Consider floor) need confirmation vs the system design document before real decisions. The scorer is a pure combiner — wiring the upstream feeds (Ch.7/8/9/10) to emit the per-role evidence envelope is separate (the run-envelope schema is still `[TODO: DEFINE]` in recipes/pipeline.md) and tied to the honest run (gap #4).

## 2026-06-14 -- The honest run (gap #4): first gated, logged recipe run

- **Recipe:** `oferta` (Ch.11 Bayesian role scorer), **sample mode**, run id `oferta-2026-06-14-001`.
- **Command:** `npm run score data/examples/ch11-roles.json` (stored script; no ad-hoc code).
- **Inputs:** verified fixture `data/examples/ch11-roles.json` + run-envelope (`mode: sample`).
- **Gates:** 1 Source ✓ · 2 Scope ✓ (sample) · 3 Data-shape ✓ · 4 Script-readiness ✓ · 5 Approval n/a (no live network/writes/model) · 6 Report ✓. Human adequacy gate: **PENDING attestation.**
- **Result:** 5 roles → Apply 2 · Consider 1 · Skip 2 (skip 40%). Cambridge 0.446 / non-sponsor 0.178 reproduce Ch.11. Output fully sourced (record / model-judgment / your-input).
- **Artifacts:** `logs/oferta-2026-06-14.json`, `reports/generated/oferta-2026-06-14.md`, `data/examples/role-scores.{json,md}`.
- **Flags:** skip-rate 40% < 50% (curated fixture, expected); `role_quality` weight 0 [VERIFY] drops the Ch.9 signal (gap #3); 1 documented override.
- **Open:** machine half of P4 done; **human adequacy (P4 second half) outstanding** — attest to promote `oferta` past DRAFT.

## 2026-06-25 -- Setup Exercise: Personal Layer (INFO 7375)

- **What was built:** Three files constituting the engine's personal data layer — `search/resume.json` (attested), `search/profile.yml`, `search/gaps.md`. Privacy boundary: `search/private-notes.md` gitignored.
- **Three attestation errors caught in resume.json:**
  1. ServiceNow CSA listed as an "excluded" credential but still present in the certifications array — removed entirely and moved to a `not_yet_obtained` block. Not an earned credential.
  2. Diploma qualification (3-year diploma, lateral entry) was missing from the education record. BE duration of 3 years is correct, but the prior diploma was not recorded. Added as `edu_3` with institution/dates flagged for verification.
  3. Metric percentages at FLO Group (30% error reduction, 20% onboarding reduction) were extracted as facts — confirmed as estimated, not measured from data. Noted inline in the relevant bullet points.
- **Top gap from gaps.md:** ServiceNow administration at CSA level (Gap B1, IT Systems Analyst track — primary) — 3 of 3 active target postings (IBM R-646296, HCLTech Admin, State Street R-790190) list ServiceNow as required or preferred. Current evidence is end-user ITSM experience only. Closes when CSA credential is issued.
- **Field corrected in profile.yml from agent's first draft:**
  - Agent initially wrote `status: "F-1 OPT"` and `opt_end: "2027-08"`. Corrected to `status: "F-1 student"` and `opt_end: null` — OPT EAD has not been filed yet; graduation is August 2026 and application must be submitted immediately via DSO. A date on an un-issued card is not a fact.
  - `stem_end_potential` also nulled — STEM OPT cannot be planned until initial OPT is approved.
- **Source data:** BLS compact file `data/bls/compact/soc_occupation_compact.csv` (SOC 15-1211, pulled 2026-06-25), 3-posting spot sample (IBM R-646296, HCLTech Administrator Miami-Dade, State Street R-790190).
- **Gaps.md edits completed:**
  - Killed row B2 (BRD/UAT ownership) — agent generated this from the generic O*NET 15-1211 Systems Analyst task list, but none of the actual target postings (IBM R-646296, HCLTech Admin, State Street R-790190) require BRD or UAT coordination; they are technical/implementation roles, not business analyst roles.
  - Rewrote row A1 (no shipped AI project) in own words — the rewritten row distinguishes between having an OCI GenAI cert and being able to demonstrate working code in an interview; the plan closes only when a public GitHub repo with a running pipeline exists, not when another course is completed.
- **Verification check (Step 4):**
  - resume.json: Every job entry is traceable to a role I held. Metric percentages (~30% error reduction, ~20% onboarding reduction) are noted as estimated — I confirmed they were not measured from data. Diploma institution and start date remain a TODO; the agent's import missed the diploma entirely, which was a real extraction failure. Those fields need to be verified against my certificate before the record is fully clean.
  - profile.yml: OPT end date is null. The agent's first draft wrote "F-1 OPT" and a 2027 expiry date — both fabricated from résumé language, not from a physical document. I have not filed for my EAD yet. Setting a gate date on an un-issued card would have caused the engine to produce Apply recommendations for a timeline I cannot currently defend.
  - gaps.md: IT track evidence cites verifiable posting IDs and req numbers (IBM R-646296, HCLTech Miami-Dade, State Street R-790190) — these are checkable. AI/Gen AI track is labeled aspirational with a note that no active applications exist yet; those gaps are forward-looking and not blocking the current search.
- **AI Use Disclosure:**
  - What the agent did: Claude Sonnet (via Cursor) extracted and structured `resume.json` from my master resume JSON, drafted `profile.yml` from my stated constraints, and drafted the initial `gaps.md` from BLS SOC data and a posting sample.
  - What I did: I ran the attestation pass and found three real errors — the CSA cert that was present but not earned, the missing diploma qualification, and the estimated metrics stated as measured facts. I corrected the visa status section in both `resume.json` and `profile.yml`. I killed gap row B2 because I know the actual postings I applied to don't require BRD work. I rewrote gap row A1 in my own words.
  - What the agent could not do: The agent read "F-1 OPT" in my source résumé JSON and confidently wrote `"status": "F-1 OPT"` and `"opt_end": "2027-08"` in `resume.json` — inferring an active OPT and fabricating an expiry date from an assumed one-year timeline. I have not filed for my EAD yet and am still on F-1 student status. That error required knowledge of my own immigration documents, which the agent does not have access to. An undetected fabricated gate date in `profile.yml` would have caused the Bayesian scorer to treat roles as Apply-eligible on a timeline I cannot legally support.

## 2026-07-06 -- ERP-to-AI Engineering triage (sample mode, ats:scan 16 boards, BLS cognitive advisory)

- **Recipe:** `case-erp-to-ai-engineering` v0.1.0 (RUNNABLE-SAMPLE)
- **Inputs:** H-1B mapped CSV (30,369 rows); BLS compact CSV; `data/examples/erp-to-ai-portals.yml` (16 enabled Greenhouse boards); 6 hand-assembled roles in roles.json.
- **Commands:** `npm run verify`; `npm run doctor`; filter-ai-title-sponsors.py; `REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml npm run ats:scan -- --dry-run`; `npm run score`.
- **Result:** 160 applied/mixed sponsors; scan **16 companies · 1,742 jobs · 341 yield**; score Apply 3 / Consider 1 / Skip 2 (33% skip).
- **Gates:** source PASS; hiring-now via ats:scan --dry-run; Fit rubric in mode file.
- **P6 open defect:** scan yield not auto-wired to roles JSON (6 sample roles hand-assembled).
- **No private data.**

## 2026-07-06 -- ERP-to-AI Engineering triage (sample mode, ats:scan + verify, BLS cognitive advisory)

**Superseded** — intermediate 2-company run; see canonical entry above.

- **Recipe:** `case-erp-to-ai-engineering` v0.1.0 (RUNNABLE-SAMPLE)
- **Inputs:** H-1B mapped CSV (30,369 rows); BLS compact CSV; `data/examples/erp-to-ai-portals.yml` (16 Greenhouse boards); 6 roles in roles.json.
- **Commands:** `npm run verify`; `npm run doctor`; filter-ai-title-sponsors.py; `REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml npm run ats:scan -- --dry-run`; same + `--verify --company Reddit`; `npm run score`.
- **Result:** 160 applied/mixed sponsors; scan 1,742 jobs → 341 yield (16 Greenhouse boards). Score Apply 2 / Consider 1 / Skip 3 (50% skip).
- **Gates:** source PASS; hiring-now via ats:scan --dry-run; Fit rubric in mode file.
- **No private data.**

## 2026-06-14 -- Rename MYCROFT.md → SNICKERDOODLE.md (constitution rebrand)

- **Why:** disambiguate this repo's constitution from the shared **Mycroft** agent-OS frame it was forked from. Renamed to a cookie-recipe name fitting the book's "recipe" vocabulary.
- **Did:** `git mv MYCROFT.md SNICKERDOODLE.md`; rebranded the file's own identity (`# SNICKERDOODLE`, "Snickerdoodle is an agent-operating system…", lineage line preserved). Swapped every `MYCROFT.md` path/governance reference (instructions/ source, `conformance.mjs` required-files list, `manifest.yml` `@import`, CI comment, `DOMAIN.md`, `status.md`, `archive/README.md`, docs/). Rebranded this-repo "Mycroft" prose (P4, "a Snickerdoodle domain", audit doc); **kept** the cross-repo "Madison and Mycroft" shared-library mention.
- **Rebuilt:** `node scripts/build-instructions.mjs --promote` → `AGENTS.md` + `CLAUDE.md` regenerated; `CLAUDE.md` now imports `@SNICKERDOODLE.md`.
- **Untouched:** `data/` CSVs (real company names containing "mycroft") and prior RUN_LOG history (append-only).
- **Result:** conformance + doctor green; no stale `MYCROFT.md` outside data/history.
