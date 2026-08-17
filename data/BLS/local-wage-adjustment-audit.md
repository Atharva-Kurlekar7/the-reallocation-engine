# Local wage-adjustment sources — provenance audit

**Written:** 2026-08-15  
**Step:** 2 of the capstone (ingest + provenance). No wage script, no coverage rate.  
**Python:** repo `.venv` (`python3.13`, packages via `.venv/bin/pip` only — never global). Pins: `data/bls/local-wage/requirements.txt`.

This audit closes the two `[DATA SOURCE]` TODOs in `Projects/target.md`. Compact extracts live beside this file under `data/bls/local-wage/`. Raw archives are gitignored (`data/bls/local-wage/raw/`).

---

## Formula (locked; cite, do not invent)

BEA Regional Price Parities are an index with **United States = 100**. LineCode `1` is **RPPs: All items** (`MARPP__definition.xml`).

Adjusted (real) wage:

```
real = nominal / (RPP / 100)
```

That is the standard conversion of a current-dollar figure by the all-items RPP (BEA: RPPs are “expressed as a percentage of the overall national price level”). Band fields are that formula applied to OEWS `A_PCT25` / `A_PCT75`. G2 still requires a non-suppressed `A_MEDIAN`.

---

## Source 1 — BLS OEWS metropolitan (May 2024)

Same survey year as the national workbook already in `data/BLS/oesm24nat/national_M2024_dl.xlsx`.

| Field | Value |
|---|---|
| Official URL (canonical) | `https://www.bls.gov/oes/special.requests/oesm24ma.zip` |
| Index checked | `https://www.bls.gov/oes/tables.htm` lists **May 2024 → Metropolitan and nonmetropolitan area (XLSX)** |
| Live fetch 2026-08-15 | Akamai **403 Access Denied** from this host (GET and HEAD, with and without a browser User-Agent) |
| Retrieval used | Internet Archive `id_` snapshot of the **same official URL**: `https://web.archive.org/web/20260613061327id_/https://www.bls.gov/oes/special.requests/oesm24ma.zip` |
| Wayback CDX | timestamp `20260613061327`, mimetype `application/x-zip-compressed`, status 200, digest `A7RHWG4CKCB7SGWW766U3AUFXUM337XQ`, length ~40,202,919 |
| Local file | `data/bls/local-wage/raw/oesm24ma.zip` (gitignored) |
| SHA-256 (zip) | `7bf915fc47e464983c5b8b8200d63a733ef90275c7af0576b78875e5b04d35d9` |
| Workbook used | `oesm24ma/MSA_M2024_dl.xlsx` (MSA table; `BOS_M2024_dl.xlsx` is metro *divisions*, unused) |
| SHA-256 (xlsx) | `2a172aed29693f50afa398be03fd107ce6bfff8b04e5fd163b4c5ddcf941d6ec` |
| Compact extract | `data/bls/local-wage/metro_oews.csv` (150,176 rows; `AREA_TYPE` is only `4` = MSA) |

**Column map (OEWS → compact):**

| Compact | OEWS |
|---|---|
| AREA | AREA (normalized to 5-digit CBSA) |
| AREA_TITLE | AREA_TITLE |
| AREA_TYPE | AREA_TYPE |
| OCC_CODE | OCC_CODE |
| OCC_TITLE | OCC_TITLE |
| O_GROUP | O_GROUP (`detailed` / `major` / `total`) |
| A_MEAN, A_MEDIAN, A_PCT25, A_PCT75 | same; suppression tokens `*` / `**` / `#` kept as text, never coerced to 0 |
| TOT_EMP | TOT_EMP |

---

## Source 2 — BEA Regional Price Parities by MSA

| Field | Value |
|---|---|
| Official URL | `https://apps.bea.gov/regional/zip/MARPP.zip` |
| Index checked | BEA RPP product page + live HEAD 200, `Last-Modified: Thu, 19 Feb 2026 13:30:06 GMT` |
| Retrieval | direct download 2026-08-15 |
| Local file | `data/bls/local-wage/raw/MARPP.zip` (gitignored) |
| SHA-256 (zip) | `5dbf2e6ac2af222cc9abc205586c9b480344d89392752eb689c3ec823a34c83e` |
| Table used | `MARPP_MSA_2008_2024.csv`, LineCode `1` (RPPs: All items), year column `2024` |
| SHA-256 (csv) | `4ce7a7e2ea08ff721de83f50d8a70bb9c93956a49970462f462372aa58cee9f4` |
| Compact extract | `data/bls/local-wage/bea_rpp.csv` (389 rows including US and nonmetro) |
| Footnote | Last updated February 19, 2026 — new 2024 statistics; MSAs delineated by OMB bulletin 23-01 |

**Column map:** GeoFIPS (5-digit) · GeoName · `rpp_all_items_2024`.

---

## Crosswalk (exact codes only)

Rule: `BLS AREA == BEA GeoFIPS` after stripping quotes/spaces and zero-filling to 5 digits. **No fuzzy name match.**

| Result | Count | File |
|---|---|---|
| Matched | 387 | `data/bls/local-wage/bls_bea_msa_crosswalk.csv` |
| BLS only | 6 Puerto Rico MSAs (Aguadilla, Arecibo, Guayama, Mayaguez, Ponce, San Juan-Bayamon-Caguas) | `data/bls/local-wage/crosswalk_unmatched.csv` (`side=bls_only`) |
| BEA only | 2 (United States; United States Nonmetropolitan Portion) — not MSAs | same file (`side=bea_only`) |

PR MSAs are the natural G3 fixture (`no-crosswalk-match`). They are **not** in the coverage sample.

---

## Reason codes (locked contract)

Each missing row ships with exactly one reason. Do not interpolate. Do not fall back to the national wage.

| Code | When |
|---|---|
| `no-metro-match` | Input does not resolve to a BLS `AREA` by exact code or exact `AREA_TITLE` (casefold). G1. |
| `no-occupation-row` | Metro resolved, but there is no detailed OEWS row for `(AREA, SOC)`. Not a suppression token. |
| `suppressed-small-sample` | Detailed row exists and `A_MEDIAN` is `*` / `**` / `#` (or otherwise not a number). G2. Glens Falls + 15-1252 is the fixture. |
| `no-crosswalk-match` | `AREA` has no exact `GeoFIPS` in the static crosswalk, or BEA all-items RPP for 2024 does not parse. G3. Ponce, PR is the fixture. |

An absent occupation row is **not** `suppressed-small-sample`. Those two events used to share one code; they do not.

Formula (unchanged): `real = nominal / (RPP / 100)` with US RPP = 100.

---

## Frozen sample (written before any coverage rate)

File: `data/bls/local-wage/sample.csv` — **112 rows** = 14 metros × 8 SOC codes. Do not edit after Step 5 starts.

**12 large MSAs** (locked prefixes from the Step-1 spec, resolved to the unique BLS `AREA_TITLE` that starts with that prefix):

| AREA | AREA_TITLE |
|---|---|
| 35620 | New York-Newark-Jersey City, NY-NJ |
| 41860 | San Francisco-Oakland-Fremont, CA |
| 41940 | San Jose-Sunnyvale-Santa Clara, CA |
| 14460 | Boston-Cambridge-Newton, MA-NH |
| 42660 | Seattle-Tacoma-Bellevue, WA |
| 12420 | Austin-Round Rock-San Marcos, TX |
| 16980 | Chicago-Naperville-Elgin, IL-IN |
| 19100 | Dallas-Fort Worth-Arlington, TX |
| 12060 | Atlanta-Sandy Springs-Roswell, GA |
| 47900 | Washington-Arlington-Alexandria, DC-VA-MD-WV |
| 31080 | Los Angeles-Long Beach-Anaheim, CA |
| 19740 | Denver-Aurora-Centennial, CO |

**2 small MSAs** (chosen from the ingested metro file where a sample SOC has suppressed `A_MEDIAN`; names recorded here, not after seeing coverage):

| AREA | AREA_TITLE | Why chosen |
|---|---|---|
| 24020 | Glens Falls, NY | only MSA with `A_MEDIAN=*` on 15-1252 Software Developers (break-test 1 / video) |
| 24500 | Great Falls, MT | suppressed `A_MEDIAN=*` on 11-3021; smallest `00-0000` employment among remaining sample-SOC suppressions (36,770) |

SOC list remains `your-input` (role selection, not skill-overlap scoring): 13-1111, 15-1211, 15-1252, 15-1243, 15-2051, 15-2031, 15-1299, 11-3021.

**Not computed in this step:** `coverage = ok / attempted`. That is Step 5.

---

## Reproduce (venv only)

```bash
/opt/homebrew/bin/python3.13 -m venv .venv
.venv/bin/pip install -r data/bls/local-wage/requirements.txt
# compact CSVs already written; re-extract from raw/ with the Step 2 python session if needed
```

`.venv/` is gitignored. Do not `pip install` into the system interpreter.

## Data directory casing

These compact files are committed under `data/BLS/local-wage/` (uppercase `BLS`), matching the pre-existing national OEWS archives already on `main`. The docs, reports, and emitted `source_bls_file` / `source_bea_file` provenance use lowercase `data/bls/` — the repo's stated convention (see `DOMAIN.md`). On case-insensitive macOS the two are the same directory; on a case-sensitive checkout they are not. `scripts/bls/local-wage-adjustment.py` resolves either casing at read time (lowercase first, then the committed `data/BLS`), so a fresh Linux clone finds the files and a macOS run still reproduces the committed reports byte-for-byte.
