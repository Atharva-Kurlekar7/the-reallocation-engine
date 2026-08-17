# Capstone submission — local wage-adjustment layer (Ch 9)

**Atharva Kurlekar** · contribution to The Reallocation Engine

A layer that turns a national BLS OEWS wage into a metro one, adjusted for local price level
using BEA Regional Price Parities — or returns `missing` with a reason code. It never
interpolates and never falls back to the national figure.

Pull request: [nikbearbrown/the-reallocation-engine#43](https://github.com/nikbearbrown/the-reallocation-engine/pull/43)

## What is here

| File | What it is |
|---|---|
| [`SUBMISSION-COVER-SHEET.md`](SUBMISSION-COVER-SHEET.md) | Submission cover sheet — every link and deliverable path in one place |
| [`local-wage-adjustment-portfolio.md`](local-wage-adjustment-portfolio.md) | The portfolio piece — a case study written for a technical hiring manager |

`.pdf` renders of both are generated, not tracked. Rebuild them with:

```bash
./scripts/md-to-pdf.sh assignments/submissions/atharva-kurlekar/*.md
```

## The contribution itself

| | |
|---|---|
| Code | [`scripts/bls/local-wage-adjustment.py`](../../../scripts/bls/local-wage-adjustment.py) |
| Recipe (for the agent) | [`recipes/local-wage-adjustment.md`](../../../recipes/local-wage-adjustment.md) |
| Card (for the human) | [`recipes/local-wage-adjustment.card.md`](../../../recipes/local-wage-adjustment.card.md) |
| Honest run | [`reports/generated/local-wage-adjustment-20260817.md`](../../../reports/generated/local-wage-adjustment-20260817.md) |
| Signed attestation | [`logs/attestations/local-wage-adjustment.md`](../../../logs/attestations/local-wage-adjustment.md) |
| Provenance + SHA-256s | [`data/BLS/local-wage-adjustment-audit.md`](../../../data/BLS/local-wage-adjustment-audit.md) |
| Run steps | [`scripts/bls/README.md`](../../../scripts/bls/README.md) |

## Run it

```bash
# an honest miss — BLS suppressed the median
python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1252

# a real answer
python3 scripts/bls/local-wage-adjustment.py \
  --metro "New York-Newark-Jersey City, NY-NJ" --soc 15-1252

# the frozen 112-pair sample — coverage 100/112
python3 scripts/bls/local-wage-adjustment.py \
  --sample data/bls/local-wage/sample.csv --aggregate --json
```

**The one limitation:** it cannot tell you what a specific employer will pay. OEWS is an
occupation-metro survey, not an offer.
