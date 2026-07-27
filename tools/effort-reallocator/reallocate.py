#!/usr/bin/env python3
"""Effort Reallocator — a slot-budget engine that doubts itself.

WHAT IT REALLOCATES
  Application slots: the ~12 applications one week of Chapter 15's three-hour apply
  block actually buys. The resource is my own irreplaceable time against an OPT
  clock, so the engine recommends and a human commits. It never applies to anything.

THE OBJECTIVE, IN ONE SENTENCE
  Maximise expected sponsored-interview yield per slot, subject to a per-company cap
  and Chapter 15's >= 50% skip rate.

WHAT THAT OBJECTIVE LEAVES OUT
  Referrals, my own application quality, interview conversion, salary, team quality,
  whether I would be happy there, and every company that files no H-1B petition and
  runs no supported ATS. It optimises a proxy for "who has sponsored people like me
  before", which is not the same thing as "who will hire me".

BOOK ANCHOR
  Ch.2 the reallocation principle · Ch.11 the Bayesian Role Scorer, section
  "Why liveness and timeline are multipliers, not addends" (the composite and the
  0.3 threshold) · Ch.15 the skip-rate dial.

COMMANDS
  gate      run the GIGO gate over the raw dataset and stop. Nothing is scored.
  allocate  propose a reallocation with uncertainty attached. Writes proposal.json.
  explain   exact Shapley attribution + counterfactual flip distance, and the
            cases where that explanation is accurate but misleading.
  audit     bias audit (two fairness metrics that disagree) + adversarial fragility.
  execute   HARD STOP. Refuses without --approve --approver --reason.
  all       gate -> allocate -> explain -> audit (never execute).

Run from the repository root:

  python3 tools/effort-reallocator/reallocate.py all
  python3 tools/effort-reallocator/reallocate.py execute --approve \\
      --approver "Your Name" --reason "verified three live postings by hand"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from engine import __version__, config, util  # noqa: E402
from engine import adversarial as adversarial_mod  # noqa: E402
from engine import allocate as allocate_mod  # noqa: E402
from engine import evidence as evidence_mod  # noqa: E402
from engine import explain as explain_mod  # noqa: E402
from engine import fairness as fairness_mod  # noqa: E402
from engine import gigo as gigo_mod  # noqa: E402
from engine import hardstop as hardstop_mod  # noqa: E402
from engine import uncertainty as uncertainty_mod  # noqa: E402

DEFAULT_OUT = os.path.join(util.tool_root(), "out")
EXAMPLES = os.path.join(util.tool_root(), "examples")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_REFUSED = 3       # the hard stop refused: no approver
EXIT_BLOCKED = 4       # the hard stop blocked: unsafe to execute
EXIT_GATE_FAILED = 5   # the data gate failed and was not waived


def build_parser():
    p = argparse.ArgumentParser(
        prog="reallocate.py",
        description="Reallocate a weekly application-slot budget, with the "
                    "skeptical machinery attached. Recommends; never moves.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Objective: maximise expected sponsored-interview yield per slot, "
               "subject to a per-company cap and a >=50%% skip rate. It leaves out "
               "referrals, application quality, and every firm with no filing record.",
    )
    p.add_argument("command",
                   choices=["gate", "allocate", "explain", "audit", "execute", "all"],
                   help="which stage to run")
    p.add_argument("--version", action="version", version=f"effort-reallocator {__version__}")

    d = p.add_argument_group("data inputs")
    d.add_argument("--csv", default=config.DEFAULT_CSV,
                   help="SEC/DOL company dataset (default: %(default)s)")
    d.add_argument("--bls", default=config.DEFAULT_BLS,
                   help="BLS/O*NET compact table for the role-quality vote")
    d.add_argument("--portals", default=config.DEFAULT_PORTALS,
                   help="ATS portals config — determines which firms are even checkable")
    d.add_argument("--profile", default=os.path.join(EXAMPLES, "profile.json"),
                   help="candidate profile (your-input assumptions)")
    d.add_argument("--baseline", default=os.path.join(EXAMPLES, "baseline-allocation.json"),
                   help="where the slots go today — the allocation being argued against")

    a = p.add_argument_group("allocation")
    a.add_argument("--slots", type=int, default=None,
                   help=f"slots to allocate this week (default: profile or {config.SLOTS_PER_WEEK})")
    a.add_argument("--cap", type=int, default=None,
                   help=f"max slots at one company (default: profile or {config.PER_COMPANY_CAP})")
    a.add_argument("--decay", type=float, default=None,
                   help="value multiplier for each repeat slot at the same company")
    a.add_argument("--liveness-policy", choices=list(config.LIVENESS_POLICIES),
                   default=config.LIVENESS_DEFAULT_POLICY,
                   help="what to do with firms whose postings cannot be checked "
                        "(default: %(default)s — recommend but require human verification)")

    u = p.add_argument_group("uncertainty")
    u.add_argument("--draws", type=int, default=config.MC_DRAWS,
                   help="Monte Carlo draws (default: %(default)s)")
    u.add_argument("--seed", type=int, default=config.MC_SEED,
                   help="RNG seed — runs are reproducible (default: %(default)s)")

    g = p.add_argument_group("the data gate")
    g.add_argument("--waive", action="append", default=[], metavar="CODE",
                   help="waive a blocking gate check by code (repeatable). "
                        "Requires --waiver-reason. Logged with the run.")
    g.add_argument("--waiver-reason", default=None,
                   help="why the waiver is defensible — recorded in the gate report")

    h = p.add_argument_group("the hard stop (execute only)")
    h.add_argument("--approve", action="store_true",
                   help="assert human approval for committing slots")
    h.add_argument("--approver", default=None, help="the named human who is accountable")
    h.add_argument("--reason", default=None, help="what the human verified, in their words")

    o = p.add_argument_group("output")
    o.add_argument("--out-dir", default=DEFAULT_OUT, help="artifact directory (default: %(default)s)")
    o.add_argument("--top", type=int, default=12, help="rows to print to the terminal")
    o.add_argument("--quiet", action="store_true", help="artifacts only, minimal stdout")
    return p


def _settings(args, profile):
    return {
        "slots": args.slots or profile.get("slots_per_week", config.SLOTS_PER_WEEK),
        "cap": args.cap or profile.get("per_company_cap", config.PER_COMPANY_CAP),
        "decay": args.decay if args.decay is not None
        else profile.get("repeat_slot_decay", config.REPEAT_SLOT_DECAY),
        "liveness_policy": args.liveness_policy,
        "draws": args.draws,
        "seed": args.seed,
    }


def _run_gate(args, out_dir, quiet=False):
    gate = gigo_mod.run_gate(
        csv_path=util.resolve(args.csv),
        waivers=args.waive,
        waiver_reason=args.waiver_reason,
        bls_path=util.resolve(args.bls),
    )
    util.write_json(os.path.join(out_dir, "gate-report.json"), gate)
    util.write_json(os.path.join(out_dir, "rejects.json"), {
        "_what_this_is": "Every row the gate refused, with a reason code. A gate with "
                         "an empty rejects file has not been run against real data.",
        "generated": gate["generated"],
        "reject_count": len(gate["rejects"]),
        "by_code": gate["reject_counts"],
        "rejects": gate["rejects"],
    })
    util.write_text(os.path.join(out_dir, "gate-report.md"), gigo_mod.render(gate))
    if not quiet:
        print(gigo_mod.summary_lines(gate))
    return gate


def _build_candidates(args, gate, profile, settings):
    return evidence_mod.build(
        csv_path=util.resolve(args.csv),
        bls_path=util.resolve(args.bls),
        portals_path=util.resolve(args.portals),
        profile=profile,
        gate=gate,
        liveness_policy=settings["liveness_policy"],
    )


def _propose(args, out_dir, quiet=False):
    """gate -> evidence -> allocate -> uncertainty. The full recommendation path."""
    profile = util.read_json(args.profile)
    settings = _settings(args, profile)
    gate = _run_gate(args, out_dir, quiet=True)
    ev = _build_candidates(args, gate, profile, settings)
    baseline = util.read_json(args.baseline)
    proposal = allocate_mod.propose(
        candidates=ev["candidates"], baseline=baseline, profile=profile,
        slots=settings["slots"], cap=settings["cap"], decay=settings["decay"],
    )
    unc = uncertainty_mod.analyze(
        candidates=ev["candidates"], baseline=baseline, profile=profile,
        proposal=proposal, slots=settings["slots"], cap=settings["cap"],
        decay=settings["decay"], draws=settings["draws"], seed=settings["seed"],
    )
    proposal["uncertainty"] = unc
    allocate_mod.attach_uncertainty(proposal, unc)
    proposal["gate"] = {
        "status": gate["status"],
        "blocking_unwaived": gate["blocking_unwaived"],
        # Carried forward so downstream artifacts quote the rate this run MEASURED
        # rather than a figure remembered from an earlier report.
        "row_count": gate["row_count"],
        "rows_with_h1b_fields": gate["rows_with_h1b_fields"],
        "h1b_missing_rate": gate["h1b_missing_rate"],
        "report": util.rel(os.path.join(out_dir, "gate-report.json")),
    }
    proposal["inputs"] = {
        "csv": util.rel(util.resolve(args.csv)),
        "bls": util.rel(util.resolve(args.bls)),
        "portals": util.rel(util.resolve(args.portals)),
        "profile": util.rel(util.resolve(args.profile)),
        "baseline": util.rel(util.resolve(args.baseline)),
        "settings": settings,
    }
    proposal["evidence_meta"] = ev["meta"]
    return profile, settings, gate, ev, baseline, proposal


def cmd_gate(args, out_dir):
    gate = _run_gate(args, out_dir)
    print(f"\n  artifacts: {util.rel(os.path.join(out_dir, 'gate-report.md'))}"
          f" · {util.rel(os.path.join(out_dir, 'rejects.json'))}")
    if gate["blocking_unwaived"]:
        print("\n  The gate is BLOCKING. `allocate` will still run (it moves nothing),")
        print("  but `execute` will refuse until a human waives each code with a reason:")
        for code in gate["blocking_unwaived"]:
            print(f"    --waive {code} --waiver-reason \"...\"")
        return EXIT_GATE_FAILED
    return EXIT_OK


def cmd_allocate(args, out_dir):
    profile, settings, gate, ev, baseline, proposal = _propose(args, out_dir, quiet=True)
    util.write_json(os.path.join(out_dir, "proposal.json"), proposal)
    util.write_json(os.path.join(out_dir, "candidates.json"), {
        "_what_this_is": "Per-company evidence with provenance on every term.",
        "generated": proposal["generated"],
        "meta": ev["meta"],
        "candidates": ev["candidates"],
    })
    util.write_text(os.path.join(out_dir, "proposal.md"),
                    allocate_mod.render(proposal, top=args.top))
    if not args.quiet:
        print(allocate_mod.summary_lines(proposal, top=args.top))
        print(f"\n  artifacts: {util.rel(os.path.join(out_dir, 'proposal.md'))}"
              f" · {util.rel(os.path.join(out_dir, 'proposal.json'))}")
        print("  nothing has moved: `execute` requires --approve --approver --reason")
    return EXIT_OK


def cmd_explain(args, out_dir):
    profile, settings, gate, ev, baseline, proposal = _propose(args, out_dir, quiet=True)
    result = explain_mod.explain(candidates=ev["candidates"], proposal=proposal,
                                 profile=profile)
    util.write_json(os.path.join(out_dir, "explanation.json"), result)
    util.write_text(os.path.join(out_dir, "explanation.md"), explain_mod.render(result))
    if not args.quiet:
        print(explain_mod.summary_lines(result))
        print(f"\n  artifacts: {util.rel(os.path.join(out_dir, 'explanation.md'))}")
    return EXIT_OK


def cmd_audit(args, out_dir):
    profile, settings, gate, ev, baseline, proposal = _propose(args, out_dir, quiet=True)
    bias = fairness_mod.audit(candidates=ev["candidates"], proposal=proposal)
    frag = adversarial_mod.audit(
        candidates=ev["candidates"], baseline=baseline, profile=profile,
        proposal=proposal, slots=settings["slots"], cap=settings["cap"],
        decay=settings["decay"], csv_path=util.resolve(args.csv),
        bls_path=util.resolve(args.bls), portals_path=util.resolve(args.portals),
        gate=gate, liveness_policy=settings["liveness_policy"],
    )
    util.write_json(os.path.join(out_dir, "bias-audit.json"), bias)
    util.write_text(os.path.join(out_dir, "bias-audit.md"), fairness_mod.render(bias))
    util.write_json(os.path.join(out_dir, "fragility.json"), frag)
    util.write_text(os.path.join(out_dir, "fragility.md"), adversarial_mod.render(frag))
    if not args.quiet:
        print(fairness_mod.summary_lines(bias))
        print(adversarial_mod.summary_lines(frag))
        print(f"\n  artifacts: {util.rel(os.path.join(out_dir, 'bias-audit.md'))}"
              f" · {util.rel(os.path.join(out_dir, 'fragility.md'))}")
    return EXIT_OK


def cmd_execute(args, out_dir):
    return hardstop_mod.execute(
        out_dir=out_dir,
        approve=args.approve,
        approver=args.approver,
        reason=args.reason,
        exit_codes={"ok": EXIT_OK, "refused": EXIT_REFUSED, "blocked": EXIT_BLOCKED,
                    "usage": EXIT_USAGE},
    )


def cmd_all(args, out_dir):
    rc_gate = EXIT_OK
    gate = _run_gate(args, out_dir)
    if gate["blocking_unwaived"]:
        rc_gate = EXIT_GATE_FAILED
    print()
    cmd_allocate(args, out_dir)
    print()
    cmd_explain(args, out_dir)
    print()
    cmd_audit(args, out_dir)
    print("\n" + "=" * 74)
    print("NOTHING HAS MOVED. The engine recommends; a named human commits.")
    print("  next: python3 tools/effort-reallocator/reallocate.py execute \\")
    print('          --approve --approver "Your Name" --reason "what you verified"')
    print("=" * 74)
    return rc_gate


def main(argv=None):
    args = build_parser().parse_args(argv)
    out_dir = util.ensure_dir(os.path.abspath(args.out_dir))
    if args.waive and not args.waiver_reason:
        print("refused: --waive requires --waiver-reason (an unexplained waiver is "
              "just switching the gate off)", file=sys.stderr)
        return EXIT_USAGE
    for path, what in ((args.csv, "dataset"), (args.profile, "profile"),
                       (args.baseline, "baseline"),
                       (args.bls, "BLS occupation table")):
        if args.command != "execute" and not os.path.exists(util.resolve(path)):
            print(f"refused: {what} not found at {path}\n"
                  f"  the engine does not guess at missing inputs.", file=sys.stderr)
            return EXIT_USAGE
    return {
        "gate": cmd_gate, "allocate": cmd_allocate, "explain": cmd_explain,
        "audit": cmd_audit, "execute": cmd_execute, "all": cmd_all,
    }[args.command](args, out_dir)


if __name__ == "__main__":
    sys.exit(main())
