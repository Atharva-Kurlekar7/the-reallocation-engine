# local-wage-adjustment — honest run — 2026-08-15

**Recipe:** `recipes/local-wage-adjustment.md`  
**Script:** `scripts/bls/local-wage-adjustment.py` (re-execs repo `.venv`)  
**Mode:** sample (local compact extracts only; no live BLS/BEA fetch in this run)  
**Run id:** `local-wage-adjustment-2026-08-15-001`

> **Superseded 2026-08-16 — read `reports/generated/local-wage-adjustment-20260817.md` instead.**
> This report is kept as the record of what the 2026-08-15 run actually printed. Its
> missing-reason breakdown is wrong: the script emitted `suppressed-small-sample` both for a
> BLS suppression token and for a `(AREA, SOC)` pair with no detailed OEWS row at all. Of the
> 12 missing rows below, **6 were absent rows, not suppressed estimates** — they now emit
> `no-occupation-row`. Coverage (`100/112`), the mean (`124695.1482`), and every wage cell are
> unaffected and reproduced in the newer run.

Every number below is either printed by that script against named files, or counted from its CSV. None are estimates.

## Coverage (the one metric)

From `--sample data/bls/local-wage/sample.csv` (frozen 112 pairs; denominator was not edited after this run):

```
coverage = 100/112 (ok=100 attempted=112 missing_reason={'suppressed-small-sample': 12})
```

- **ok = 100** — `script-output`, count of `status=ok` in `reports/generated/local-wage-adjustment-20260815.csv`
- **attempted = 112** — `script-output`, row count of `data/bls/local-wage/sample.csv` (header excluded)
- **missing = 12**, all `suppressed-small-sample` — listed below
- **G4:** `plausibility_flag=ok` on all 100 ok rows; **0** `review` flags. National median from `data/bls/compact/soc_occupation_compact.csv`.

Worked example (script-output from the same CSV): New York-Newark-Jersey City, NY-NJ × 15-1252 → nominal median `161970.00`, BEA RPP `112.5630`, adjusted median `143892.75`, flag `ok`. Formula `real = nominal / (RPP / 100)`.

Twelve missing rows (empty wage fields):

| metro_area | soc_code | missing_reason |
|---|---|---|
| San Jose-Sunnyvale-Santa Clara, CA | 11-3021 | suppressed-small-sample |
| Atlanta-Sandy Springs-Roswell, GA | 13-1111 | suppressed-small-sample |
| Glens Falls, NY | 15-1252 | suppressed-small-sample |
| Glens Falls, NY | 15-1243 | suppressed-small-sample |
| Glens Falls, NY | 15-2051 | suppressed-small-sample |
| Glens Falls, NY | 15-2031 | suppressed-small-sample |
| Glens Falls, NY | 15-1299 | suppressed-small-sample |
| Glens Falls, NY | 11-3021 | suppressed-small-sample |
| Great Falls, MT | 15-1243 | suppressed-small-sample |
| Great Falls, MT | 15-2051 | suppressed-small-sample |
| Great Falls, MT | 15-2031 | suppressed-small-sample |
| Great Falls, MT | 11-3021 | suppressed-small-sample |

## Pasted terminals

### Sample + aggregate (break-test 4)

```
$ python3 scripts/bls/local-wage-adjustment.py --sample data/bls/local-wage/sample.csv --aggregate --json --output reports/generated/local-wage-adjustment-20260815.csv
coverage = 100/112 (ok=100 attempted=112 missing_reason={'suppressed-small-sample': 12})
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
      "suppressed-small-sample": 12
    }
  }
}
```

`--aggregate` used 100 ok rows and **excluded** 12 missing. Missing were not zeros. Mean `124695.1482` is script-output from those 100 adjusted medians only.

### Break 1 — suppressed metro (G2)

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1252 --json
coverage = 0/1 (ok=0 attempted=1 missing_reason={'suppressed-small-sample': 1})
metro_area,soc_code,status,missing_reason,...
"Glens Falls, NY",15-1252,missing,suppressed-small-sample,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-15
```

Wage columns empty. No interpolation. No national fallback.

### Break 2a — bad spelling (G1)

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "New Yrok" --soc 15-1252 --json
coverage = 0/1 (ok=0 attempted=1 missing_reason={'no-metro-match': 1})
New Yrok,15-1252,missing,no-metro-match,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-15
```

Not fuzzy-matched to New York.

### Break 2b — BLS MSA with no BEA row (G3)

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Ponce, PR" --soc 15-1252 --json
coverage = 0/1 (ok=0 attempted=1 missing_reason={'no-crosswalk-match': 1})
"Ponce, PR",15-1252,missing,no-crosswalk-match,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-15
```

Ponce is `bls_only` in `data/bls/local-wage/crosswalk_unmatched.csv`. Exact-code miss, not a name guess.

### Break 3 — SOC outside the ERP list

First try `11-1011` (Chief Executives), off-list:

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Austin-Round Rock-San Marcos, TX" --soc 11-1011 --json
coverage = 0/1 (ok=0 attempted=1 missing_reason={'suppressed-small-sample': 1})
"Austin-Round Rock-San Marcos, TX",11-1011,missing,suppressed-small-sample,,,,,,,,,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-15
```

Honest miss: Austin’s `11-1011` median is suppressed. The list-filter claim is not “every off-list SOC is ok.” Retry with off-list `11-1021` (General and Operations Managers), which BLS does publish:

```
$ python3 scripts/bls/local-wage-adjustment.py --metro "Austin-Round Rock-San Marcos, TX" --soc 11-1021 --json
coverage = 1/1 (ok=1 attempted=1 missing_reason={})
"Austin-Round Rock-San Marcos, TX",11-1021,ok,,141810.00,108940.00,98.0660,72298.25,176554.57,111088.45,ok,102950.00,data/bls/local-wage/metro_oews.csv,data/bls/local-wage/bea_rpp.csv,2026-08-15
```

Off-list SOC **processed**. The ERP list is a sample filter, not a hard-coded wage restriction.

## G4 plausibility audit

Scanned all 100 `ok` rows in the sample CSV. `plausibility_flag=review` count = **0**. Bound: adjusted median within 0.3×–3× of `annual_median_wage` in `data/bls/compact/soc_occupation_compact.csv`. No row was rewritten.

## What the machine could not know

- What **this employer** pays. OEWS is an occupation-metro survey, not an offer.
- Whether a job title maps to the right SOC (frontier titles stay a human call).
- Why a cell is `*` — only that it is not a number. Do not treat suppression as “wage is zero.”
- Whether 2024 OMB metro lines still match a future BEA vintage. Unmatched codes stay missing.

Human call handed back: G4 `review` (none in this sample); adequacy of using these 8 SOCs as the ERP selection list (`your-input`); signature on the attestation.

## Gate results

| Gate | This run |
|---|---|
| G1 | fail path observed (`New Yrok`) |
| G2 | fail path observed (Glens Falls 15-1252; 12 sample rows) |
| G3 | fail path observed (`Ponce, PR`) |
| G4 | pass path observed (100/100 ok rows `ok`; 0 auto-corrects) |
| Human adequacy | **SIGNED** — Atharva Kurlekar, 2026-08-15, adequate as sample run (`logs/attestations/local-wage-adjustment.md`) |

## Artifacts

- CSV: `reports/generated/local-wage-adjustment-20260815.csv`
- Machine log: `logs/local-wage-adjustment-20260815.json`
- This report: `reports/generated/local-wage-adjustment-20260815.md`
