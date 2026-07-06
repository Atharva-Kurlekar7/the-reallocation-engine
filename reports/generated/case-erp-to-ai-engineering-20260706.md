# ERP-to-AI Engineering — Applied-AI Sponsor Shortlist

- Run: `case-erp-to-ai-engineering-20260706` (mode: sample)
- Source: `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv`
- Generated: 2026-07-06T19:04:54

## Run summary

- Records seen: **30,369**
- Records with H-1B title data: **1,557**
- Applied/mixed AI sponsors found: **160**
- Research-gated-only sponsors (excluded from shortlist): **22**
- Rejected (below min approvals=5): **75**

## Verified vs inferred

- **Verified** (source CSV columns): approvals, approval rate, median salary, funding stage/date.
- **Verified** (BLS/O*NET source): `cognitive_pivot_score` when the base occupation carries one.
- **Inferred** (keyword judgment, not verified): the applied / research-gated / mixed **class**, the ranking **score**, and the **target SOC** mapping.

Cognitive Pivot column is **advisory** (Ch.9 role quality): shown for the
human, not folded into any gate. The book leaves the role-quality weight
unpinned, so pretending it is a vote would invent a number the source does
not support. Where a SOC is unscored in BLS, it is flagged, not guessed.

## Shortlist (top 50 applied-AI sponsors)

| # | Company | Class | Approvals | Rate % | Median $ | Funding | SOC | Cog. pivot | Applied titles (sample) |
|---|---------|-------|-----------|--------|----------|---------|-----|-----------|--------------------------|
| 1 | LINKEDIN CORP | applied | 4962 | 99 | 167,149 | Series D+ | 15-2051 | gap | Sr Data Scientist; Sr. Software Engineer, Machine Learning |
| 2 | ICON TECHNOLOGY INC | applied | 2200 | 99 | 108,140 | Series C | 15-2051 | gap | Data Scientist 2 |
| 3 | AMGEN INC | applied | 1882 | 99 | 120,000 | — | 15-1252 | 3.834 | Data Engineer ⚠ |
| 4 | HUMAN INC | applied | 1382 | 99 | 132,078 | Series B | 15-1252 | 3.834 | Data Engineer 2 |
| 5 | ZOOX INC | applied | 1364 | 99 | 158,080 | Series D+ | 15-1252 | 3.834 | Data Engineer |
| 6 | DOCUSIGN INC | applied | 1082 | 99 | 172,107 | Series B | 15-1252 | 3.834 | Data Engineer |
| 7 | AIRBNB INC | applied | 1000 | 99 | 158,080 | Series B | 15-2051 | gap | Data Scientist; Senior Data Scientist |
| 8 | ROBLOX CORP | applied | 856 | 99 | 265,000 | Series B | 15-1252 | 3.834 | Principal Machine Learning Engineer - Personalization |
| 9 | TWILIO INC | applied | 802 | 98 | 160,000 | Series D+ | 15-1252 | 3.834 | Machine Learning Engineer (L2) |
| 10 | ROKU INC | applied | 654 | 99 | 182,155 | Series C | 15-2051 | gap | Senior Data Scientist; Senior Data Engineer |
| 11 | TREDENCE INC | applied | 564 | 97 | 135,000 | Series D+ | 15-1252 | 3.834 | Associate Manager – Data Engineering |
| 12 | TELADOC HEALTH INC | applied | 510 | 97 | 127,758 | Series D+ | 15-2051 | gap | Data Scientist III; DATA SCIENTIST III |
| 13 | MAPLEBEAR INC | applied | 498 | 99 | 185,000 | Series D+ | 15-2051 | gap | Senior Machine Learning Engineer; Senior Data Scientist |
| 14 | REDDIT INC | applied | 408 | 97 | 220,000 | Series D+ | 15-1252 | 3.834 | Software Engineer, Machine Learning |
| 15 | VISICON TECHNOLOGIES INC | applied | 330 | 99 | 98,309 | Pre-Seed | 15-1252 | 3.834 | Data Engineer; Data Engineer |
| 16 | UPSTART NETWORK INC | applied | 316 | 99 | 160,000 | Pre-Seed | 15-1252 | 3.834 | Data Engineer |
| 17 | PELOTON INTERACTIVE INC | applied | 310 | 97 | 167,149 | Series C | 15-2051 | gap | Marketing Data Scientist |
| 18 | PELOTON INTERACTIVE LLC | applied | 310 | 97 | 167,149 | Seed | 15-2051 | gap | Marketing Data Scientist |
| 19 | QUANTIPHI INC | applied | 270 | 96 | 125,660 | Series A | 15-1252 | 3.834 | Senior Data Engineer; Senior Machine Learning Engineer |
| 20 | ETSY INC | applied | 222 | 99 | 186,150 | Series A | 15-1252 | 3.834 | Senior Software Engineer I, Machine Learning; Engineering Manager, Machine Learning Systems |
| 21 | NEXTDOOR INC | applied | 222 | 97 | 157,250 | Series D+ | 15-2051 | gap | Data Scientist; Machine Learning Engineer |
| 22 | FIGMA INC | applied | 188 | 99 | 190,000 | Series D+ | 15-2051 | gap | Data Scientist, Product Analytics |
| 23 | AGENT TECHNOLOGIES INC | applied | 216 | 98 | 135,000 | Seed | 15-1252 | 3.834 | Machine Learning Engineer |
| 24 | GUARDANT HEALTH INC | applied | 214 | 99 | 124,717 | Series D+ | 15-1252 | 3.834 | Manager, Data Engineering |
| 25 | MOLOCO INC | applied | 200 | 99 | 146,242 | Series D+ | 15-2051 | gap | Staff Data Scientist; Machine Learning Engineer II |
| 26 | PROCORE TECHNOLOGIES INC | applied | 190 | 100 | 147,200 | Series C | 15-1252 | 3.834 | Senior Data Engineer |
| 27 | CHEGG INC | applied | 132 | 100 | 186,144 | Pre-Seed | 15-2051 | gap | Staff Data Scientist |
| 28 | APPLOVIN CORP | applied | 130 | 98 | 150,000 | Series D+ | 15-1252 | 3.834 | Machine Learning Engineer |
| 29 | GRID DYNAMICS HOLDINGS INC | applied | 126 | 100 | 122,500 | Series D+ | 15-2051 | gap | Data Scientist |
| 30 | DISCORD INC | applied | 122 | 100 | 218,000 | Series B | 15-1252 | 3.834 | Software Engineer, Machine Learning |
| 31 | FORMATION DATA SYSTEMS INC | applied | 130 | 92 | 88,400 | Series A | 15-1252 | 3.834 | Data Engineer |
| 32 | COHERE HEALTH INC | applied | 104 | 98 | 160,000 | Series C | 15-1252 | 3.834 | Senior Machine Learning DevOps Engineer; Machine Learning Engineer |
| 33 | CLARI INC | applied | 116 | 100 | 189,155 | Series B | 15-2051 | gap | Senior Data Scientist |
| 34 | MEDALLIA INC | applied | 116 | 98 | 170,000 | Series A | 15-2051 | gap | Data Scientist |
| 35 | WHOOP INC | applied | 114 | 100 | 140,000 | Series C | 15-1252 | 3.834 | Machine Learning Operations Engineer II |
| 36 | ATTENTIVE MOBILE INC | applied | 96 | 100 | 155,000 | Series D+ | 15-1252 | 3.834 | Senior Machine Learning Engineer I |
| 37 | COURSERA INC | applied | 88 | 98 | 151,674 | Series D+ | 15-1252 | 3.834 | Data Engineer |
| 38 | NERDWALLET INC | applied | 88 | 98 | 162,000 | Series C | 15-1252 | 3.834 | Staff Data Engineer; Data Engineer |
| 39 | SILA NANOTECHNOLOGIES INC | applied | 74 | 100 | 177,000 | Series D+ | 15-1252 | 3.834 | Senior Data Engineer |
| 40 | HINGE HEALTH INC | applied | 84 | 100 | 192,600 | Series D+ | 15-1252 | 3.834 | Senior Engineering Manager, Data Engineering |
| 41 | FRESHWORKS INC | applied | 82 | 100 | 144,696 | Series D+ | 15-1252 | 3.834 | Lead Software Engineer - Machine Learning |
| 42 | SOCURE INC | applied | 82 | 100 | 174,850 | Series C | 15-1252 | 3.834 | Sr. Data Engineer; Computer Vision Engineer |
| 43 | PATHAI INC | applied | 78 | 98 | 145,600 | Series C | 15-1252 | 3.834 | Machine Learning Engineer III; Senior Machine Learning Engineer |
| 44 | PATHRAI INC | applied | 78 | 98 | 145,600 | Pre-Seed | 15-1252 | 3.834 | Machine Learning Engineer III; Senior Machine Learning Engineer |
| 45 | COALITION INC | applied | 76 | 100 | 145,000 | Series D+ | 15-2051 | gap | Data Scientist; Operations Research Analyst (Senior Data Scientist) |
| 46 | THOUGHTSPOT INC | applied | 76 | 100 | 141,232 | Series C | 15-1252 | 3.834 | Staff Software Engineer - Machine Learning |
| 47 | CAMBRIDGE MOBILE TELEMATICS INC | applied | 72 | 100 | 134,616 | Seed | 15-2051 | gap | Principal Data Scientist I; Senior Software Engineer - Machine Learning |
| 48 | INSITRO INC | applied | 68 | 100 | 167,500 | Series D+ | 15-1252 | 3.834 | Senior Machine Learning Scientist |
| 49 | YEXT INC | applied | 68 | 100 | 142,727 | Series C | 15-1252 | 3.834 | Senior Data Engineer |
| 50 | EXABEAM INC | applied | 68 | 97 | 157,500 | Series B | 15-1252 | 3.834 | Data Engineer |

## Data quality flags (source CSV)

These are **verified raw-field artifacts**, not inferred. Do not treat
numeric suffixes as part of the job title.

- **AMGEN INC**: `Data Engineer 20516.3745` → display as **Data Engineer**; wage-like suffix `20516.3745` appended to title in source CSV — verify before trusting

## Next gate

This shortlist has cleared the sponsorship-title signal only. Before any
application, each company must clear the **hiring-now gate** (`npm run ats:scan
--dry-run` on an enabled Greenhouse board — posting appears in scan yield)
and the **visa-timeline gate**. Neither is a vote; both are hard stops.
See `recipes/case-erp-to-ai-engineering.md`.
