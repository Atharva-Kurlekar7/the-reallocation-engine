# Attestation — local wage-adjustment layer

**Recipe:** `recipes/local-wage-adjustment.md` `recipe_version: 0.2.0`
**Run:** `local-wage-adjustment-2026-08-17-001` (re-run after the G2 reason-code split; supersedes `local-wage-adjustment-2026-08-15-001`)
**Report:** `reports/generated/local-wage-adjustment-20260817.md`
**Prior run also attested:** `reports/generated/local-wage-adjustment-20260815.md` (signed 2026-08-15; kept with a correction header)

This is a **sample-run adequacy** record, not the VERIFIED attestation. The recipe stays `status: RUNNABLE-SAMPLE` and `attestation: null` — per `SNICKERDOODLE.md` the `attestation:` field is bound only at VERIFIED, which requires a prior RUNNABLE-LIVE gated run this recipe has not had. The machine does not sign this. A named human does.

## Verified-vs-inferred boundary — every emitted field

The script writes 15 CSV columns (`OUTPUT_FIELDS` in `scripts/bls/local-wage-adjustment.py`). Each is labeled below; the report and machine log add three derived figures, also labeled.

| Field emitted | Label | Source |
|---|---|---|
| `metro_area` | `record` | resolved `AREA_TITLE` from `data/bls/local-wage/metro_oews.csv` (or the raw input echoed back on `no-metro-match`) |
| `soc_code` | `your-input` | the SOC requested (normalized); which occupations to test is my selection |
| `status` (`ok`/`missing`) | `script-output` | which gate the row reached |
| `missing_reason` | `script-output` | first failed gate; codes locked in `data/BLS/local-wage-adjustment-audit.md` |
| `nominal_wage_mean` | `record` | `A_MEAN` from the OEWS row on `(AREA, OCC_CODE)` |
| `nominal_wage_median` | `record` | `A_MEDIAN` from the OEWS row on `(AREA, OCC_CODE)` |
| `bea_rpp_value` | `record` | `rpp_all_items_2024` from `data/bls/local-wage/bea_rpp.csv` via exact `AREA=GeoFIPS` |
| `adjusted_wage_band_low` / `_high` | `script-output` | `real = nominal / (RPP / 100)` applied to `A_PCT25` / `A_PCT75`; empty if the percentile is suppressed |
| `adjusted_wage_median` | `script-output` | `real = nominal / (RPP / 100)` applied to `A_MEDIAN` |
| `plausibility_flag` (`ok`/`review`) | `script-output` | G4: adjusted median within 0.3×–3× of the national median, else `review` |
| `national_median_wage` | `record` | `annual_median_wage` from `data/bls/compact/soc_occupation_compact.csv` (G4 comparison only) |
| `source_bls_file` | `record` | path of the OEWS file actually read |
| `source_bea_file` | `record` | path of the BEA file actually read |
| `run_date` | `script-output` | UTC date stamped at run time (`datetime.now(timezone.utc)`) |
| Coverage `100/112` | `script-output` | count of `status=ok` / 112 attempted sample rows; identical in the 2026-08-15 and 2026-08-17 runs |
| `mean_adjusted_median` `124695.1482` | `script-output` | `--aggregate` mean of the 100 `ok` adjusted medians; 12 missing excluded, never zero |
| `g4_review_count` `0` | `script-output` | count of `plausibility_flag=review` over the 100 `ok` rows |
| Skill-match % | **not emitted** | out of scope; no defensible source here |

The machine log (`logs/local-wage-adjustment-2026081*.json`) is a hand-recorded transcript; its `logged_at` is labeled `your-input` (wall-clock), and it deliberately carries **no** `rejects`/`duplicates` fields because the script computes neither — reporting `0` for a stage that does not exist would be an invented number.

## Tested

| Ran | Saw | Expected |
|---|---|---|
| `--sample data/bls/local-wage/sample.csv --aggregate --json` | `coverage = 100/112 (ok=100 attempted=112 missing_reason={'suppressed-small-sample': 6, 'no-occupation-row': 6})`; mean `124695.1482` | 100/112 with the misses split across the two G2 codes; mean over ok rows only |
| `--metro "Glens Falls, NY" --soc 15-1252` (break: suppression token) | `missing: suppressed-small-sample`, all wage fields empty | detailed row exists, `A_MEDIAN=*` → suppressed, no interpolation |
| `--metro "Glens Falls, NY" --soc 15-1243` (break: absent row) | `missing: no-occupation-row`, all wage fields empty | no detailed `(AREA, SOC)` row → the new code, not "suppressed" |
| `--metro "New Yrok" --soc 15-1252` (break: misspelling) | `missing: no-metro-match` | no fuzzy match to New York |
| `--metro "Ponce, PR" --soc 15-1252` (break: no BEA join) | `missing: no-crosswalk-match` | BLS-only MSA, exact-code miss, no name guess |
| `--metro "New York-Newark-Jersey City, NY-NJ" --soc 15-1252` (worked ok row) | nominal `161970`, RPP `112.5630`, adjusted `143892.75`, flag `ok` | RPP shrinks the NY nominal premium; plausible |
| G4 scan of all 100 ok rows | `plausibility_flag=review` count `0`; no row rewritten | flag, never auto-correct |

## Did not test

- A **live** fetch of BLS/BEA (the run is sample mode against frozen compact extracts; the live 403/Wayback story is documented in the audit, not re-exercised here).
- Behaviour on a case-sensitive filesystem was reasoned about and coded for (the script resolves `data/bls` or `data/BLS`), but the corrected script was executed only on macOS in this session.
- Any occupation outside the frozen 8-SOC / 14-metro sample beyond the single off-list Austin probe.
- Whether a job title maps to the correct SOC — out of scope and explicitly a human call.
- Full `npm run doctor` cleanliness beyond the privacy gate. Privacy now passes on the contribution branch (ethics gate (a)). `doctor` still reports a non-privacy environment finding and two recipes missing lifecycle frontmatter; both are untracked local files outside this contribution, and neither was fixed by me.
- Whether the delivered explainer video matches what the recipe and portfolio claim about it. A re-render silently dropped the spliced real terminal take once already (logged 2026-08-16); the film is a build artifact I re-check by measurement, not something this attestation covers.

## Broke during testing, fixed

- **G2 reason-code overload.** `evaluate_pair` returned `suppressed-small-sample` both for a suppression token and for a `(AREA, SOC)` pair with no detailed OEWS row. Split so an absent row emits `no-occupation-row`; re-ran and 6 of 12 misses reclassified, coverage and every wage cell unchanged. Fix in `scripts/bls/local-wage-adjustment.py` (`evaluate_pair`); reason codes locked in `data/BLS/local-wage-adjustment-audit.md`.
- **Invented log counts.** The machine logs carried `rejects: 0` / `duplicates: 0` for stages the script does not implement, and a `generated_at` timestamp the script does not emit. Removed the invented counts and relabeled the timestamp as hand-recorded `your-input` (both `logs/local-wage-adjustment-2026081*.json`).

## Ethics gate (a) Privacy

This contribution uses public BLS/BEA extracts only. No `data/ats/` and no `private/` files were read or written for the run.

`npm run doctor` privacy excerpt, on the contribution branch `contrib/local-wage-adjustment-v2` (re-run 2026-08-16 after the branch was re-cut):

```
PRIVACY (no personal data committed)
  ✓ no private/PII paths are tracked
```

**The gate now passes, and it did not before.** The earlier state is kept here rather than deleted, because the reason it failed matters more than the fact that it now passes:

```
PRIVACY (no personal data committed)
  ✗ 1 private/PII path(s) are git-tracked — REMOVE before pushing:
      search/resume.json
```

The original contribution branch was cut from a fork `main` carrying an unrelated personal-assignment layer. That inherited `search/resume.json`, `search/gaps.md`, and `search/profile.yml` — real name, personal email, LinkedIn URL, and immigration status — into the contribution's own diff and into public PR #43, and it inherited a `.gitignore` line (`!search/resume.json`) that deliberately un-ignored the résumé. I had recorded this as "pre-existing, not mine." That was accurate about origin and wrong about responsibility: the moment those files sat inside this PR's diff, they were this contribution's problem, and a failing privacy gate is a hard stop under `SNICKERDOODLE.md` P4 regardless of who introduced it.

Fixed by re-cutting the branch from `upstream/main` and re-applying only the contribution's 22 files. The `!search/resume.json` override is gone. This contribution's diff contains no `private/`, no `data/ats/`, and no `search/` personal data — verified by grepping the full staged diff for the email address, LinkedIn URL, and full legal name (0 hits).

## Ethics gate (b) Honesty

Coverage is `100/112` with a 12-row missing breakdown — **6 `suppressed-small-sample` + 6 `no-occupation-row`** — not a bare percentage. Missing rows were not filled, interpolated, or averaged as zero. Off-list SOC `11-1011` in Austin was reported suppressed rather than forced ok.

Correction I am signing off on, not hiding: the 2026-08-15 run reported all 12 as `suppressed-small-sample`. Six of those rows have no BLS row at all, which is a different fact about the world than a suppressed estimate. The script now separates them. I kept the old report with a correction header rather than overwriting it, so the mistake stays in the record.

## Signature (human)

I have read the report and the boundary table. I attest the numbers I am using came from the named script and records, or are labeled `your-input`. Any edit to the recipe or its scripts after this signature voids the attestation (per `SNICKERDOODLE.md`).

- Name: Atharva Kurlekar
- Date: 15 August 2026 (sample run) · re-affirmed 16 August 2026 (G2 reason-code split, invented log fields removed)
- Decision: [X] adequate as sample run  [ ] block — notes: ________
