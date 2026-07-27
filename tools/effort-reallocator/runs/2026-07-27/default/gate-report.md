# GIGO gate report — 2026-07-27

**Dataset:** `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` — 30,369 rows  
**Status:** **BLOCKED**

## The quality standard

> Every record used to move a slot must have (1) an identity resolving to one firm, (2) counts that agree with the stated rate, (3) a funding date recent enough to mean anything, and (4) a collection timestamp and source.

## What this dataset assumes that is not true

1. A blank H-1B cell means the company does not sponsor. It does not: it means no filing was matched. The engine routes these to `unknown` and never imputes zero.
2. Approval_Rate measures willingness to sponsor. It measures approval given the firm already filed for a candidate it had already selected.
3. latest_funding_stage is the company's stage. It is the stage of its last Form D filing, so public firms appear as early-stage.
4. One row is one company. Identical filing counts recur under INC/LLC variants.

## Checks

| Check | Severity | Count | Rate | Why it matters |
|---|---|---:|---:|---|
| `DATASET_NO_RECORD_PROVENANCE` | blocking | 30,369 | 100.0% | Without a per-record timestamp there is no way to tell a 2015 filing from a 2024 one, and no way to detect a protocol change mid-collection. The engine is reallocating on a snapshot of unknown vintage. |
| `RATE_WITHOUT_DENOMINATOR` | reject | 0 | 0.0% | A percentage with no counts behind it cannot be given a credible interval. |
| `RATE_ARITHMETIC_MISMATCH` | reject | 0 | 0.0% | If the stated rate disagrees with its own counts, one of them is wrong and the tool cannot tell which. |
| `RATE_SCALE_ANOMALY` | reject | 0 | 0.0% | A 0-1 value in a 0-100 column silently becomes a ~1% approval rate. This is the perturbation class the fragility pass exploits. |
| `ABSURD_VALUE` | reject | 0 | 0.0% | An impossible number means the pipeline that produced it is not trustworthy. |
| `ENTITY_COLLISION` | flag | 9 | 0.0% | Identical filing counts under two legal names double-count the same evidence and can push one firm's history into two thin halves. |
| `IDENTITY_AMBIGUOUS` | reject | 81 | 0.3% | The same normalised name carries DIFFERENT filing counts across rows, so there is no way to tell which row is the firm I would be applying to. Picking one would be inventing an answer, so every row in the ambiguous group is refused — including rows with a strong record. That cost is real and it is the correct cost: a wrong join produces a confident number about the wrong company. |
| `WAGE_IN_TITLE` | flag | 3 | 0.0% | A wage leaked into the title column means the upstream parse misaligned fields for that row. If it leaked here it may have leaked elsewhere. |
| `FUNDING_STAGE_IMPLAUSIBLE` | flag | 31 | 0.1% | Form D stage is the stage of the last exemption filing, not the company's current stage. Using it as a maturity signal is a category error. |
| `FUNDING_DATE_STALE` | flag | 22,451 | 73.9% | An old Form D is not a signal that a company is hiring now. |
| `FUNDING_DATE_MISSING` | flag | 0 | 0.0% | Undated funding cannot be aged, so it cannot be discounted. |
| `H1B_FIELDS_ABSENT` | flag | 28,812 | 94.9% | The dominant condition in this dataset. Flagged, never imputed to zero: the whole engine turns on refusing to read a blank cell as a 'no'. |
| `BLS_TABLE_ABSENT` | flag | 0 | 0.0% | Without the BLS table the role_quality vote is empty while Monte Carlo still draws its weight from U[0, 0.20]. The intervals change with no crash and no warning — silence, not a refusal. The CLI refuses a missing path; this check keeps the absence visible in the gate report if a caller bypasses the CLI. |

**Missing H-1B fields: 94.9% of rows.** The engine routes these to an `unknown` sponsorship tier that cannot earn slots on sponsorship grounds. It never reads a blank cell as a zero — that single decision is the difference between "no evidence" and "evidence of no".

## Rejections

81 rows rejected: `IDENTITY_AMBIGUOUS` × 81

| Company | Codes | Approvals | Denials | Stated rate |
|---|---|---:|---:|---:|
| 98POINT6 INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| 98POINT6 TECHNOLOGIES INC | `IDENTITY_AMBIGUOUS` | 2 | 0 | 100.00 |
| ADVOCATE INC | `IDENTITY_AMBIGUOUS` | 16 | 0 | 100.00 |
| ADVOCATE TECHNOLOGIES INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| AEYE INC | `IDENTITY_AMBIGUOUS` | 20 | 0 | 100.00 |
| AEYE TECHNOLOGIES INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| ASCENT HOLDING CO | `IDENTITY_AMBIGUOUS` | — | — | — |
| ASCENT TECHNOLOGIES INC | `IDENTITY_AMBIGUOUS` | 2 | 0 | 100.00 |
| AVAVA INC | `IDENTITY_AMBIGUOUS` | 2 | 0 | 100.00 |
| AVAVA LLC | `IDENTITY_AMBIGUOUS` | — | — | — |
| AXIA TECHNOLOGIES INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| AXIA TECHNOLOGIES LLC | `IDENTITY_AMBIGUOUS` | 2 | 0 | 100.00 |
| BEACHBODY CO GROUP LLC | `IDENTITY_AMBIGUOUS` | — | — | — |
| BEACHBODY LLC | `IDENTITY_AMBIGUOUS` | 34 | 2 | 94.44 |
| BILT INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| BILT TECHNOLOGIES INC | `IDENTITY_AMBIGUOUS` | 12 | 0 | 100.00 |
| BRIGHTINSIGHT HOLDINGS INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| BRIGHTINSIGHT INC | `IDENTITY_AMBIGUOUS` | 16 | 0 | 100.00 |
| CHECKR GROUP INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| CHECKR INC | `IDENTITY_AMBIGUOUS` | 76 | 8 | 90.48 |
| CLASSY HOLDINGS INC | `IDENTITY_AMBIGUOUS` | — | — | — |
| CLASSY INC | `IDENTITY_AMBIGUOUS` | 18 | 2 | 90.00 |
| COMPASS THERAPEUTICS INC | `IDENTITY_AMBIGUOUS` | 6 | 0 | 100.00 |
| COMPASS THERAPEUTICS LLC | `IDENTITY_AMBIGUOUS` | — | — | — |
| HEARTFLOW HOLDING INC | `IDENTITY_AMBIGUOUS` | — | — | — |

… and 56 more in `rejects.json`.

## Entity collisions (flagged)

9 normalized names carry identical filing counts under more than one legal name. Identical counts are the tell: two genuinely different firms would not share an approval *and* a denial count exactly.

| Normalized | Approvals | Rows |
|---|---:|---|
| PELOTON INTERACTIVE | 310 | PELOTON INTERACTIVE INC · PELOTON INTERACTIVE LLC |
| DELOITTE TOUCHE TOHMATSU SERVICES | 242 | DELOITTE TOUCHE TOHMATSU SERVICES INC · DELOITTE TOUCHE TOHMATSU SERVICES LLC |
| BERKELEY RESEARCH | 50 | BERKELEY RESEARCH GROUP HOLDINGS LLC · BERKELEY RESEARCH GROUP LLC |
| ARCTURUS THERAPEUTICS | 12 | ARCTURUS THERAPEUTICS INC · ARCTURUS THERAPEUTICS LTD |
| ZAPATA COMPUTING | 6 | ZAPATA COMPUTING HOLDINGS INC · ZAPATA COMPUTING INC |
| AVIDITY BIOSCIENCES | 4 | AVIDITY BIOSCIENCES INC · AVIDITY BIOSCIENCES LLC |
| CARGOMETRICS | 4 | CARGOMETRICS TECHNOLOGIES INC · CARGOMETRICS TECHNOLOGIES LLC |
| TREATMENT TECHNOLOGIES INSIGHTS | 4 | TREATMENT TECHNOLOGIES & INSIGHTS INC · TREATMENT TECHNOLOGIES & INSIGHTS LLC |
| NEWLIGHT | 2 | NEWLIGHT TECHNOLOGIES INC · NEWLIGHT TECHNOLOGIES LLC |

## Blocking

- **`DATASET_NO_RECORD_PROVENANCE`** — standard: *every record has a collection timestamp and a source*. Without a per-record timestamp there is no way to tell a 2015 filing from a 2024 one, and no way to detect a protocol change mid-collection. The engine is reallocating on a snapshot of unknown vintage. **UNWAIVED — `execute` will refuse.**

A gate that cannot fail is decoration. This one fails on the dataset's own terms, and clearing it takes a named human and a written reason.

