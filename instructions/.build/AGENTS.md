<!-- GENERATED FILE — do not edit by hand.
     Source: instructions/ (_shared/ modules + project file) · manifest: instructions/manifest.yml
     Rebuild: node scripts/build-instructions.mjs   ·   Promote: --promote
     Hand edits are overwritten on the next build. -->

# Agent Instructions

## Governance

Read `SNICKERDOODLE.md` (the constitution — principles, the verification stack, the recipe lifecycle, the logging rules) and `DOMAIN.md` (this project's index — layout and what is runnable today) before acting. If any file conflicts with `SNICKERDOODLE.md`, `SNICKERDOODLE.md` governs and the conflict is a bug — log it in `logs/RUN_LOG.md`.

The contract in brief (SNICKERDOODLE.md governs in full):

1. Verified local data before external lookup; stored scripts before ad-hoc code.
2. Never invent a count, rate, or confidence; label model judgments as judgments.
3. Gates are hard stops cleared by a named human and logged.
4. Machines verify conformance; humans verify adequacy.
5. Log meaningful runs, blockers, and artifacts in `logs/RUN_LOG.md`.

## Default to Markdown for humans

AI-native formats (JSON, YAML) are the source of truth for the machine. When showing an artifact to a person, render the Markdown view (`scripts/to-markdown.mjs` / the `review` skill) by default. Show raw JSON/YAML only when asked.

## Never delete — archive instead

Never delete source, data, recipes, logs, or any hand-made file. Move superseded or scratch files to an archive (or out of the working tree into the full-copy archive). The only safe removals are generated/rebuildable artifacts — `**/.build/`, `__pycache__/`, `*.pyc`, `*.bak` — because they regenerate from source. When in doubt, archive and ask.

## Conformance before done

Run `node scripts/conformance.mjs <paths>` (or `npm run verify`) before declaring work complete. Invalid JSON / YAML / JS is not done — it is not even gradeable. This is the machine half of P4; whether the content is *adequate* is still the human gate.

## Scope subagents narrowly

Give a subagent only what its task needs — the index (`DOMAIN.md`), the one relevant subfolder, and the specific files named. Never hand a subagent the whole repository. Subagents run in their own context window and should return a summary, not raw file dumps.

## Reporting completion

Before reporting a task complete, state: files changed; scripts or data checked; tests, builds, or searches run; and any unverified assumptions or remaining risks. No silent done.

## The Reallocation Engine

An **evidence-first job-search system for international students** (F-1/OPT/STEM OPT), and the working repository for the book *The Reallocation Engine*. It reallocates scarce application effort using five evidence components — company funding (SEC Form D), sponsorship history (DOL/H-1B), posting liveness (ATS), role quality (BLS/O*NET), and visa timeline — where liveness and timeline are **gates, not votes** (a healthy run skips at least half of evaluated roles). It is a domain built on the Snickerdoodle framework. Project-specific rules:

- Use lowercase `scripts/`; never create `SCRIPTS/`.
- Manuscript content lives in `chapters/` — no scripts or data there.
- `data/ats/`, rendered resumes/PDFs, and `.env*` are **private by default** — review before commit (they reveal personal job-search activity).

### `help` command

When the user's message is just `help` (or `/help`), reply with **exactly** the fenced block below — verbatim, nothing before or after — then stop and wait:

```
THE REALLOCATION ENGINE — evidence-first job search (a Snickerdoodle domain)
Reallocate scarce application effort by evidence. The rule of the house:
fluency is the first sign of trouble — the human owns the irreducible judgment.

WHAT YOU CAN DO
  recipes    Read a recipe + its run evidence (best first look):
             recipes/ (44 recipes — scan, pipeline, oferta, tracker, pdf, patterns…)
  runnable   npm run ats:scan -- --dry-run   ·   ats:liveness <url>   ·   ats:verify
             npm run resumes:pdf -- --all    ·   python3 scripts/sec/refresh-recent-sec-quarters.py
  evidence   SEC Form D (funding) · DOL/H-1B (sponsorship) · ATS (liveness, a GATE)
             BLS/O*NET (role quality) · visa timeline (a GATE)
  book       The Reallocation Engine manuscript: chapters/ (21 chapters)
  data       Two-layer target data/raw -> data/verified (planned); domain dirs run today
  scripts    conformance · to-markdown · build-instructions · svg-to-png

HOW IT WORKS
  Every finding traces report -> log -> recipe -> source. Gates are hard stops a named
  human clears. Skip is a successful outcome. Machines verify conformance; humans verify
  adequacy. (Constitution: SNICKERDOODLE.md)

TRY
  "run the ats scan dry-run and read the report"   ·   "what's runnable today?"
  "show me the scan recipe"                        ·   "list the known defects"
```
