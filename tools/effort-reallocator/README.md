# Effort Reallocator

A reallocation engine for a scarce resource that is not money: **application slots** —
the ~12 applications one week of Chapter 15's three-hour apply block actually buys.

It ingests the SEC/DOL company dataset, scores companies with the Chapter 11 composite,
and outputs an explicit **move**: *shift Q slots from company A to company B*, with an
80% interval and a stability figure attached. Then it argues with itself: a data gate
that can block, a bias audit whose two metrics disagree, an explanation plus the cases
where that explanation misleads, a causal verdict, a fragility sweep, and a hard stop
that refuses to commit a single slot without a named human and a written reason.

Built for the INFO 7375 assignment *The Reallocation Engine, Audited*. The validation
report is [`../../Kurlekar_Atharva_ReallocationEngine.md`](../../Kurlekar_Atharva_ReallocationEngine.md).

## Quickstart

No install. Standard library only, Python 3.9+. Run from the repository root:

```bash
python3 tools/effort-reallocator/reallocate.py all
```

That runs the gate, the proposal with uncertainty, the explanation, the bias audit,
and the fragility sweep, writing every artifact to `tools/effort-reallocator/out/`.
It cannot move anything — `execute` is a separate command and it refuses by default.

A committed sample run (the one quoted in the report) is in
[`runs/2026-07-27/`](runs/2026-07-27/).

## The objective, and what it leaves out

**Objective, in one sentence:** maximise expected sponsored-interview yield per slot,
subject to a per-company cap of 3 — with Chapter 15's ≥50% skip rate reported as a
**dial**, not enforced as a constraint, because it is a process metric a human reads
in two directions.

**What that objective leaves out:** referrals, my own application quality, interview
conversion, salary, team quality, whether I would be happy there — and every company
that files no H-1B petition and runs no supported ATS. It optimises a proxy for *who
has sponsored people like me before*, which is not the same claim as *who will hire me*.

**Book anchor:** Ch.2 (the reallocation principle) · **Ch.11, "Why liveness and
timeline are multipliers, not addends"** — the composite `(Σ vote·weight) × liveness ×
timeline` with a threshold near 0.3 · Ch.15 (the skip-rate dial).

## Commands

| Command | What it does | Moves anything? |
|---|---|---|
| `gate` | Runs the GIGO gate over all 30,369 rows and stops. Writes `gate-report.md`, `rejects.json`. | No |
| `allocate` | Proposes the reallocation with Monte Carlo uncertainty. Writes `proposal.md/json`, `candidates.json`. | No |
| `explain` | Exact Shapley attribution + counterfactual flip distance, plus the cases where the explanation is accurate and misleading. | No |
| `audit` | Bias audit (two fairness metrics in tension) + adversarial fragility. | No |
| `execute` | **HARD STOP.** Refuses without `--approve --approver --reason`; blocks on a failed gate, an unstable move, or an unverified posting. | Only with a named human |
| `all` | gate → allocate → explain → audit. Never execute. | No |

Useful flags:

```bash
--slots 12 --cap 3                 # the weekly budget and per-company ceiling
--liveness-policy legacy-zero      # reproduce the older behaviour that skipped Amgen
--draws 4000 --seed 20260727       # Monte Carlo size; runs are reproducible
--waive CODE --waiver-reason "..." # a blocking gate check, waived on the record
--baseline private/my-tracker.json # your real baseline (artifacts stay out of git)
```

Exit codes: `0` ok · `2` usage/missing input · `3` the hard stop refused (no approver) ·
`4` the hard stop blocked (unsafe) · `5` the data gate failed and was not waived.

## What the numbers mean

Every term carries a provenance label, following Ch.11's audit trace:

- `record` — a government or company filing, quoted as-is.
- `derived` — arithmetic over records, plus a stated parameter.
- `model-judgment` — a judgment. Here the fit vote, computed by a deterministic
  rubric rather than an LLM, so it is reproducible; it is still a judgment.
- `your-input` — my own assumption about my own situation (timeline, response rate).

`engine/config.py` marks each parameter with whether the book pins it. Two are marked
`[VERIFY]` because the repo's own defect list says Chapter 11 never pinned them —
the `role_quality` weight and the Consider-band floor. The uncertainty pass varies
them rather than pretending they are settled.

## Where I would not trust this tool

- **Liveness is unverified in every run.** This tool makes no network calls. It knows
  whether a company's board is *checkable* by the repo's scanner (Greenhouse, Lever,
  Ashby), not whether a posting exists. Under the default policy an uncheckable firm
  still gets recommended, flagged `manual_verification_required`, and the hard stop
  refuses to execute until a human looks.
- **No outcome data.** Nothing here is fit against whether I got an interview. Every
  "yield" is `composite × my assumed response rate`, and the assumed rate is a
  `your-input` number that scales every result linearly.
- **Small samples.** A 100% approval rate over 2 filings and a 99% rate over 4,962
  filings are different facts. The Beta posterior keeps them apart; the point estimate
  alone does not, which is exactly the failure the explanation critique documents.
- **`latest_funding_stage` is the stage of the last Form D filing, not the company's
  current stage.** Public companies appear as "Series B". The gate flags it.

## Privacy

Runs on committed public data plus the synthetic `examples/` inputs, so it works from
a clean clone. If you point `--baseline` at a real tracker under `private/` or
`data/ats/`, direct `--out-dir` into `private/` too. Nothing derived from personal data
belongs in a tracked file. `out/` is gitignored; `runs/` is the committed sample.

## Tests

```bash
python3 -m unittest discover tools/effort-reallocator/tests -v
```

Includes a parity test asserting this Python composite reproduces the repo's own
`scripts/score/role-scorer.mjs` output on the committed fixture, and Chapter 11's
worked example (Apply 0.446 / Skip 0.178) to four decimal places. The reimplementation
is verified against the book, not asserted to match it.
