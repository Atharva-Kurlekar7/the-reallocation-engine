# Local wage adjustment for The Reallocation Engine

**Atharva Kurlekar** · August 2026
Contribution to [The Reallocation Engine](https://github.com/nikbearbrown/the-reallocation-engine), an evidence-first job-search system for international students.

Pull request: [nikbearbrown/the-reallocation-engine#43](https://github.com/nikbearbrown/the-reallocation-engine/pull/43)
Demo: `youtube/national-pay-is-not-local-pay/mp4/national-pay-is-not-local-pay.mp4` (4:19). **The terminal shown in the current cut is an animated reconstruction, not a screen capture** — see "About the demo footage" at the end. The tool itself is runnable in four commands; those are in "How to check any of this" below, and they are the honest way to verify this page.

---

## The problem

I am an F-1 student. When my OPT clock starts, the scarce resource is not job postings — it is my own attention. Every application I write is one I cannot write somewhere else, so the decision that matters is which roles to spend that effort on.

The engine already read role quality from the U.S. Bureau of Labor Statistics Occupational Employment and Wage Statistics (OEWS). But it read the *national* estimate, and the book is explicit about why that is a limit rather than an answer:

> "National OEWS estimates are national and lagging… They don't capture what this specific company pays, what the local market pays in your city… The compact row tells you the occupation's gravity; it cannot tell you the specific role's orbit around it."
> — `chapters/09-is-the-role-any-good-bls-onet-role-quality.md`

That gap is an information asymmetry with a direction. An employer posting in a high-cost metro knows that its salary band buys less there. A candidate comparing a national median against a Manhattan offer does not, unless someone does the arithmetic. The same nominal number is a different standard of living in Glens Falls, New York than in New York City — and a student ranking roles by nominal pay alone, with no local price level to correct for it, can be misled by exactly the metros where the number flatters the offer most.

## What I built

A layer that answers one question: **for this metro and this occupation, what do BLS and BEA jointly support as a cost-adjusted wage?**

The pipeline is deliberately short, and it is a sequence of gates rather than a scoring function:

1. **Resolve the metro.** Match the input to a BLS `AREA` by exact code or exact `AREA_TITLE` (case-folded). No fuzzy matching — `New Yrok` is not New York.
2. **Read the metro wage.** Look up the detailed OEWS row for `(AREA, SOC)` and read `A_MEDIAN`.
3. **Join the price level.** Match the BLS `AREA` to a BEA `GeoFIPS` on **exact code equality** in a static crosswalk (387 exact matches), and read the 2024 all-items Regional Price Parity.
4. **Adjust.** `real = nominal / (RPP / 100)`, where the U.S. average RPP is 100.
5. **Sanity-check.** Flag the row for a human if the adjusted median falls outside 0.3×–3× of the national median for that occupation. Flag, never rewrite.

Any gate that fails ends the row. The output is `missing` plus exactly one reason code, and every wage column is left empty:

| Reason | What actually happened |
|---|---|
| `no-metro-match` | the input never resolved to a BLS area |
| `no-occupation-row` | the metro resolved, but BLS publishes no row for that occupation there |
| `suppressed-small-sample` | the row exists and BLS suppressed the median (`*`, `**`, `#`) |
| `no-crosswalk-match` | no exact BEA price index for that area code |

There is no national fallback and no interpolation from neighbouring metros. A missing row stays missing, because the alternative — quietly substituting the national figure into a metro cell — is the exact error the layer exists to prevent.

Interfaces: `scripts/bls/local-wage-adjustment.py` (CLI, single pair or a batch CSV), plus a recipe for agents and a card for humans.

## The honest number

The improvement I can defend is not a bigger number — coverage was 100/112 before and after — it is a class of silent error removed. Six of the twelve "missing" rows had been labelled with the wrong reason, and the split that fixed them is the measurable delta below. The headline metric held; the honesty of the metric improved.

On a sample of **112 metro–occupation pairs** — 14 metro areas × 8 occupation codes, frozen in `data/bls/local-wage/sample.csv` *before* the run so the denominator could not be chosen afterwards:

```
coverage = 100/112 (ok=100 attempted=112
                    missing_reason={'suppressed-small-sample': 6, 'no-occupation-row': 6})
```

100 of 112 pairs returned a cost-adjusted wage traceable to a named BLS row and a named BEA row. The 12 that did not are reported with their reason and empty wage fields. I am quoting the count and the denominator rather than a percentage, because the percentage would hide both the denominator and the fact that the 12 misses are two different events.

Two other measured facts from the same run:

- The batch mean of the adjusted medians is **$124,695.15** over the **100 ok rows**. The 12 missing rows are excluded from that mean, not counted as zero.
- The plausibility gate flagged **0** of the 100 rows for human review, and rewrote none.

Worked example, straight from the output CSV: New York-Newark-Jersey City, NY-NJ × SOC 15-1252 (Software Developers) → nominal median **$161,970**, RPP **112.563**, adjusted median **$143,892.75**. New York's nominal premium shrinks by roughly $18,000 once its price level is applied — which is the entire point of the layer.

**A correction I am including because leaving it out would be the dishonest choice.** The first run, on 2026-08-15, reported all 12 missing rows as `suppressed-small-sample`. That was wrong, and the bug was mine: one code path returned "suppressed" both when BLS had suppressed a median and when there was no OEWS row at all. Six of the twelve had no row. I split the code path, added `no-occupation-row`, and re-ran: coverage stayed 100/112 and not one wage cell changed, but the classification of six rows did. The superseded report is kept in the repository with a correction header rather than overwritten (`reports/generated/local-wage-adjustment-20260815.md` → `-20260817.md`).

## Verified versus inferred

Every field the tool emits carries a label. That boundary is the deliverable as much as the numbers are:

| Field | Label | Where it comes from |
|---|---|---|
| Metro nominal wage (mean / median) | `record` | the OEWS row for `(AREA, OCC_CODE)` in `data/bls/local-wage/metro_oews.csv` |
| BEA 2024 all-items RPP | `record` | `data/bls/local-wage/bea_rpp.csv`, joined on exact `AREA` = `GeoFIPS` |
| Adjusted median and 25th–75th band | `script-output` | `real = nominal / (RPP / 100)`, computed by the named script |
| Coverage `100/112` | `script-output` | count of `status=ok` over the 112 pre-declared sample rows |
| Missing reason codes | `script-output` | which gate failed |
| The 8-occupation target list | `your-input` | my own choice of roles to test — a judgment, not a finding |
| Skill-match percentage | **not emitted** | out of scope; there is no defensible way to compute it here |

Source files are recorded with their URLs and SHA-256 hashes in `data/BLS/local-wage-adjustment-audit.md`, and every output row carries the `source_bls_file` and `source_bea_file` it came from.

## Failure modes I expect

1. **Drift.** BLS or BEA ship a new annual file with renamed columns and the parser reads a flag as a wage. Mitigation: suppression tokens stay text and never coerce to numbers; sources are hashed in the audit; column maps are re-checked on each ingest.
2. **Contract violation.** Someone later adds a skill-match score into the same CSV as the wage, blending a model judgment into a column of records. Mitigation: the card forbids blending, and the recipe refuses the request rather than obliging it.
3. **Crosswalk staleness.** OMB redraws metro boundaries and the static exact-code table goes wrong. Mitigation: unmatched codes stay `no-crosswalk-match`; no name-based guessing; the table gets rebuilt from a new vintage rather than patched.
4. **Suppression misread.** Treating `*` as zero, or as missing-at-random and therefore safe to interpolate, fabricates a wage. Labelling an *absent* row as "suppressed" is the same class of error, one step earlier — it claims to know why the data is not there. Mitigation: the two now have separate reason codes, and Glens Falls × 15-1252 is a permanent test fixture for the suppression path.

## The limitation it cannot verify

**It cannot tell you what a specific employer will pay you.** OEWS is a survey of occupations within metro areas; it is not an offer, and no amount of cost adjustment turns it into one. A company that just closed a Series A may pay at the top of the band; one burning runway may be below the median with equity attached. What the layer establishes is a comparison at the occupation level — a published metro survey adjusted for the metro's price level, so two cities can be read on the same scale. It does not narrow the range for any specific employer, and reading a personal salary quote out of it would be a misuse, which the card says plainly.

Two related limits, stated for the same reason: the tool cannot verify that a job title maps to the right occupation code (frontier titles stay a human call), and when BLS publishes no row it records only *that* the row is absent, never why.

## How to check any of this

```bash
# the honest failure — a real metro, a suppressed median, no invented wage
python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1252

# the same metro, a different occupation — absent row, a different reason code
python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1243

# the worked example
python3 scripts/bls/local-wage-adjustment.py \
  --metro "New York-Newark-Jersey City, NY-NJ" --soc 15-1252

# the full sample and its coverage
python3 scripts/bls/local-wage-adjustment.py \
  --sample data/bls/local-wage/sample.csv --aggregate --json
```

## About the demo footage

The terminal sequence in the current cut of the video is **an animated reconstruction of the first and third commands above, not a live screen capture.** The text it displays was copied from a real run, and two of its lines are visibly truncated with `...` because they were laid out to fit a slide — no program printed them in that form. I am flagging this rather than letting the footage imply otherwise, because a rendered terminal that looks live is the same class of error this contribution exists to catch: output that is well-formed, plausible, and not produced by the thing it appears to come from.

A genuine capture does exist and is kept in the repository: `youtube/national-pay-is-not-local-pay/live/take.cast`, a 44.79s `asciinema` recording of both commands run back to back in a real pty, with the script's real stdout. An earlier cut of the film had it spliced in; a later re-render against a new voiceover dropped it, and the reconstruction is what currently ships. The regression is logged in `logs/RUN_LOG.md` (2026-08-16). In that recording the keystrokes are replayed at a fixed rate — the command text is typed programmatically, the **output** is whatever the script printed.

The reliable way to check this page is not the footage. It is the four commands above, run against the committed extracts, which reproduce every number quoted here.

Full trail: recipe `recipes/local-wage-adjustment.md` · card `recipes/local-wage-adjustment.card.md` · report `reports/generated/local-wage-adjustment-20260817.md` · machine log `logs/local-wage-adjustment-20260817.json` · signed attestation `logs/attestations/local-wage-adjustment.md` · provenance `data/BLS/local-wage-adjustment-audit.md` · run history `logs/RUN_LOG.md`.

---

**AI use.** I used Claude and Cursor to draft the script, the recipe, and the card, and to build the video. The judgments were mine: which occupations to test, freezing the sample before measuring coverage, and refusing the national fallback. The reason-code defect — one path returning "suppressed" for both a suppressed median and an absent row — was surfaced by a review pass, not caught by me on first write; I own that it was my logic and that it survived because the output was well-formed and confidently wrong. Deciding it was a real error rather than a cosmetic one, and keeping the superseded report in the tree instead of overwriting it, were the calls I made. That is the failure mode this whole project is about, and it caught me too.
