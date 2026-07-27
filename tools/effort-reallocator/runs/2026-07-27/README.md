# Sample run — 2026-07-27

Every number in `../../../../Kurlekar_Atharva_ReallocationEngine.md` comes from these
files. Reproducible from a clean clone: the inputs are the committed public dataset plus
the tracked BLS compact table (`data/BLS/compact/soc_occupation_compact.csv`) plus the
synthetic `examples/` profile and baseline, and the Monte Carlo seed is fixed at 20260727.

## Two runs, on purpose

**`default/` — the honest headline.** Default settings (`--liveness-policy
neutral-flagged`, 12 slots). The gate **BLOCKS** on `DATASET_NO_RECORD_PROVENANCE`, the
engine proposes 8 moves anyway (proposing is free; committing is not), and `execute`
**refuses with exit 4** because six of the eight destinations have postings nobody can
check and three of the moves are not distinguishable from doing nothing. *The engine's own
recommendation cannot be executed.* That is the intended behaviour, not a failure to fix.

**`executed/` — what it takes to actually move a slot.** `--liveness-policy block`
(drop every firm whose board the scanner cannot read), `--slots 11` (so a move that once
cleared the 70% floor only via `round()` is never proposed), plus an explicit human waiver
of the blocking gate code, then `execute --approve --approver --reason`. Nine stable
moves, all ≥86%, all to verifiable boards. The cost of getting here is stated plainly:
Intel (13,318 approvals) and Microsoft (12,226) are discarded for running the wrong ATS.

## Terminal transcripts

| File | Command | Exit |
|---|---|---|
| `terminal-01-all-default.txt` | `reallocate.py all` | 5 — gate failed, unwaived |
| `terminal-02-execute-refused.txt` | `reallocate.py execute` | 4 — blocked, nothing moved |
| `terminal-03-allocate-block-policy.txt` | `allocate --slots 11 --liveness-policy block --waive … --waiver-reason …` | 0 |
| `terminal-04-execute-approved.txt` | `execute --approve --approver … --reason …` | 0 — committed |

## Artifacts

| File | What it is |
|---|---|
| `gate-report.md` / `.json` | The GIGO gate: the quality standard, what the data assumes that is not true, every check with a count |
| `rejects.json` | The 81 rows the gate refused, with a reason code each |
| `proposal.md` / `.json` | The move, its 80% interval, move stability, the tie report, the skip-rate account, the blind spot |
| `candidates.json` | Per-company evidence with a provenance label on every term |
| `explanation.md` / `.json` | Exact Shapley (32 coalitions), flip distances, and the four cases where the explanation misleads |
| `bias-audit.md` / `.json` | Bias by pipeline stage, two fairness metrics that disagree, the chosen one and its cost |
| `fragility.md` / `.json` | Five perturbations with fragility distances, plus the measured cost of the coverage bias |
| `execution-decision.json` | The hard stop's verdict, blocks and flags |
| `committed-allocation.json` | *(executed only)* the ledger a named human signed |
| `gate-decisions-2026-07-27.md` | Copy of the append-only decision log written to `logs/gate-decisions/` |

## Reproducing

```bash
python3 tools/effort-reallocator/reallocate.py all
python3 tools/effort-reallocator/reallocate.py execute        # expect exit 4
```

Identical inputs give identical output, including the `from → to` pairing of each move
(that pairing is explicitly sorted, because iterating a set of strings is not stable
across Python processes — a bug found by running the tool twice and diffing).
