# local-wage-adjustment — honest run — 2026-08-17

**Recipe:** `recipes/local-wage-adjustment.md` `recipe_version: 0.2.0`
**Script:** `scripts/bls/local-wage-adjustment.py` (re-execs repo `.venv`)
**Mode:** sample (local compact extracts only; no live BLS/BEA fetch in this run)
**Run id:** `local-wage-adjustment-2026-08-17-001`
**Supersedes:** `reports/generated/local-wage-adjustment-20260815.md` — same sample, same wages, **corrected missing-reason breakdown** (see below)

Date note: the script stamps `run_date` in UTC, so every cell reads `2026-08-17`. The run was executed the evening of 2026-08-16 local time (UTC-4).

Every number below is either printed by that script against named files, or counted from its CSV. None are estimates.

## Why this run exists

The 2026-08-15 run reported all 12 missing rows as `suppressed-small-sample`. That was wrong, and the defect was in the script, not the report: `evaluate_pair` returned `suppressed-small-sample` both when BLS suppressed a median (`*` / `**` / `#`) **and** when there was no detailed OEWS row for `(AREA, SOC)` at all. Two different events, one code.

Fixed: an absent detailed row now emits `no-occupation-row`. Suppression keeps `suppressed-small-sample`. Reason codes are locked in `data/BLS/local-wage-adjustment-audit.md`.

Coverage did not change. The classification of the misses did.

## Coverage (the one metric)

From `--sample data/bls/local-wage/sample.csv` (frozen 112 pairs; denominator was not edited after this run):

```
coverage = 100/112 (ok=100 attempted=112 missing_reason={'suppressed-small-sample': 6, 'no-occupation-row': 6})
```

- **ok = 100** — `script-output`, count of `status=ok` in `reports/generated/local-wage-adjustment-20260817.csv`
- **attempted = 112** — `script-output`, row count of `data/bls/local-wage/sample.csv` (header excluded)
- **missing = 12** — `script-output`, now split 6 `suppressed-small-sample` + 6 `no-occupation-row`
- **G4:** `plausibility_flag=ok` on all 100 ok rows; **0** `review` flags. National median from `data/bls/compact/soc_occupation_compact.csv`.

Worked example (script-output from the same CSV): New York-Newark-Jersey City, NY-NJ × 15-1252 → nominal median `161970.00`, BEA RPP `112.5630`, adjusted median `143892.75`, flag `ok`. Formula `real = nominal / (RPP / 100)`. Unchanged from the 2026-08-15 run.

Twelve missing rows (empty wage fields):

| metro_area | soc_code | missing_reason | 2026-08-15 said |
|---|---|---|---|
| San Jose-Sunnyvale-Santa Clara, CA | 11-3021 | suppressed-small-sample | suppressed-small-sample |
| Atlanta-Sandy Springs-Roswell, GA | 13-1111 | suppressed-small-sample | suppressed-small-sample |
| Glens Falls, NY | 15-1252 | suppressed-small-sample | suppressed-small-sample |
| Glens Falls, NY | 15-1243 | **no-occupation-row** | suppressed-small-sample |
| Glens Falls, NY | 15-2051 | suppressed-small-sample | suppressed-small-sample |
| Glens Falls, NY | 15-2031 | **no-occupation-row** | suppressed-small-sample |
| Glens Falls, NY | 15-1299 | **no-occupation-row** | suppressed-small-sample |
| Glens Falls, NY | 11-3021 | suppressed-small-sample | suppressed-small-sample |
| Great Falls, MT | 15-1243 | **no-occupation-row** | suppressed-small-sample |
| Great Falls, MT | 15-2051 | **no-occupation-row** | suppressed-small-sample |
| Great Falls, MT | 15-2031 | **no-occupation-row** | suppressed-small-sample |
| Great Falls, MT | 11-3021 | suppressed-small-sample | suppressed-small-sample |

Six rows were reclassified. No wage cell changed.

## Pasted terminals

### Sample + aggregate (break-test 4)

```
$ python3 scripts/bls/local-wage-adjustment.py --sample data/bls/local-wage/sample.csv --aggregate --json --output reports/generated/local-wage-adjustment-20260817.csv
coverage = 100/112 (ok=100 attempted=112 missing_reason={'suppressed-small-sample': 6, 'no-occupation-row': 6})
{
  "aggregate": {
    "ok_rows_in_mean": 100,
    "missing_rows_excluded": 12,
    "mean_adjusted_median": 124695.1482,
    "note": "missing rows are excluded; never treated as zero"
  }
}
{
  "coverage": {
    "ok": 100,
    "attempted": 112,
    "coverage": "100/112",
    "missing_reason": {
      "suppressed-small-sample": 6,
      "no-occupation-row": 6
    }
  }
}
```

`--aggregate` used 100 ok rows and **excluded** 12 missing. Missing were not zeros. Mean `124695.1482` is script-output from those 100 adjusted medians only — identical to the 2026-08-15 value, as expected, because no ok row changed.

### Break 1 — suppressed metro (G2, suppression token)

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1252
coverage = 0/1 (ok=0 attempted=1 missing_reason={'suppressed-small-sample': 1})
"Glens Falls, NY",15-1252,missing,suppressed-small-sample,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-17
```

Wage columns empty. No interpolation. No national fallback. The detailed row exists; `A_MEDIAN` is a suppression token.

### Break 1b — absent occupation row (the new code)

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1243
coverage = 0/1 (ok=0 attempted=1 missing_reason={'no-occupation-row': 1})
"Glens Falls, NY",15-1243,missing,no-occupation-row,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-17
```

Same metro, different SOC, different reason. BLS publishes no Database Architects row for Glens Falls at all — that is not a suppressed estimate. Before the fix, this row claimed it was.

### Break 2a — bad spelling (G1)

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "New Yrok" --soc 15-1252
coverage = 0/1 (ok=0 attempted=1 missing_reason={'no-metro-match': 1})
New Yrok,15-1252,missing,no-metro-match,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-17
```

Not fuzzy-matched to New York.

### Break 2b — BLS MSA with no BEA row (G3)

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Ponce, PR" --soc 15-1252
coverage = 0/1 (ok=0 attempted=1 missing_reason={'no-crosswalk-match': 1})
"Ponce, PR",15-1252,missing,no-crosswalk-match,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-17
```

Ponce is `bls_only` in `data/bls/local-wage/crosswalk_unmatched.csv`. Exact-code miss, not a name guess.

### Break 3 — SOC outside the ERP list

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Austin-Round Rock-San Marcos, TX" --soc 11-1011
coverage = 0/1 (ok=0 attempted=1 missing_reason={'suppressed-small-sample': 1})
"Austin-Round Rock-San Marcos, TX",11-1011,missing,suppressed-small-sample,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-17
```

Honest miss, and now a precise one: the row exists, the median is suppressed. Retry with off-list `11-1021`, which BLS does publish:

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Austin-Round Rock-San Marcos, TX" --soc 11-1021
coverage = 1/1 (ok=1 attempted=1 missing_reason={})
"Austin-Round Rock-San Marcos, TX",11-1021,ok,,141810.00,108940.00,98.0660,72298.25,176554.57,111088.45,ok,102950.00,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-17
```

Off-list SOC **processed**. The ERP list is a sample filter, not a hard-coded wage restriction.

## G4 plausibility audit

Scanned all 100 `ok` rows in the sample CSV. `plausibility_flag=review` count = **0**. Bound: adjusted median within 0.3×–3× of `annual_median_wage` in `data/bls/compact/soc_occupation_compact.csv`. No row was rewritten.

## What the machine could not know

- What **this employer** pays. OEWS is an occupation-metro survey, not an offer.
- Whether a job title maps to the right SOC (frontier titles stay a human call).
- Why a cell is `*` — only that it is not a number. Do not treat suppression as "wage is zero."
- Why BLS publishes no row at all for a `(metro, SOC)` pair — `no-occupation-row` records that the row is absent, not the reason it is absent.
- Whether 2024 OMB metro lines still match a future BEA vintage. Unmatched codes stay missing.

Human call handed back: G4 `review` (none in this sample); adequacy of using these 8 SOCs as the ERP selection list (`your-input`); signature on the attestation.

## Gate results

| Gate | This run |
|---|---|
| G1 | fail path observed (`New Yrok` → `no-metro-match`) |
| G2 suppression | fail path observed (Glens Falls 15-1252; 6 sample rows) |
| G2 absent row | fail path observed (Glens Falls 15-1243; 6 sample rows) |
| G3 | fail path observed (`Ponce, PR` → `no-crosswalk-match`) |
| G4 | pass path observed (100/100 ok rows `ok`; 0 auto-corrects) |
| Human adequacy | **SIGNED** — Atharva Kurlekar, 2026-08-16, adequate as sample run (`logs/attestations/local-wage-adjustment.md`) |

## Artifacts

- CSV: `reports/generated/local-wage-adjustment-20260817.csv`
- Machine log: `logs/local-wage-adjustment-20260817.json`
- This report: `reports/generated/local-wage-adjustment-20260817.md`
- RUN_LOG entry: `logs/RUN_LOG.md` — 2026-08-16
- Superseded run (kept, not deleted): `reports/generated/local-wage-adjustment-20260815.md`
