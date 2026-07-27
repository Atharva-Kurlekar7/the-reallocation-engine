"""The hard stop. Nothing moves without a named human and a written reason.

WHICH OF THE THREE THINGS DOES THIS ENGINE DO?

It **commits a resource**. Not money, and not another person's access — my own time,
twelve applications a week, against an F-1/OPT clock that does not stop. That is
irreplaceable in the strictest sense: a slot spent on a dead posting in July cannot be
recovered in August, and the clock's end date is fixed by immigration law rather than
by anything I can renegotiate.

WHY THE GATE IS NON-NEGOTIABLE HERE

Because the engine's central signal is one it cannot verify. Liveness is a gate in the
arithmetic and an *assumption* in this run: no network call was made, so "the board is
on a supported ATS provider" is standing in for "a posting exists". An unattended run
would spend real weeks of a real visa clock on that substitution. The failure mode is
not dramatic — no crash, no error, just twelve applications into a void and a month
gone. "It ran unattended and reallocated the week" is precisely what this gate exists
to prevent.

THREE RESPONSES

  APPROVE  a named human asserts they verified what the engine could not, and the
           decision is appended to logs/gate-decisions/ with their name and reason.
  FLAG     the move proceeds but carries an unresolved caveat that travels with it.
  BLOCK    the move is refused regardless of approval, because approving it would be
           approving something nobody has checked.

Block conditions, in order of precedence:
  1. the GIGO gate has an unwaived blocking code -> BLOCK (the data is not gradeable)
  2. a destination is flagged manual_verification_required -> BLOCK until verified
  3. a move's Monte Carlo stability is below the floor -> BLOCK (not distinguishable
     from doing nothing, and "we might as well" is not a reason to spend a week)
  4. no approver, or no reason -> REFUSE (a different exit code: nothing was wrong
     with the proposal, the human simply was not there)

WHO RESOLVES WHAT

  the engine    arithmetic, intervals, flags, and the refusal itself
  the human     whether a posting is real, whether the reason is honest, whether a
                blocked move should be unblocked by going and checking
  nobody        may switch the gate off. There is no --force flag, by design.
"""

import datetime
import os

from . import config
from . import util

MIN_REASON_CHARS = 15


def _load(out_dir, name):
    path = os.path.join(out_dir, name)
    if not os.path.exists(path):
        return None, path
    return util.read_json(path), path


def evaluate(proposal, gate):
    """Decide approve / flag / block for the proposal as a whole and per move."""
    blocks = []
    flags = []

    unwaived = gate.get("blocking_unwaived") if gate else None
    if unwaived:
        blocks.append({
            "code": "GATE_BLOCKING_UNWAIVED",
            "detail": ", ".join(unwaived),
            "response": "block",
            "resolver": "a named human waives each code with a written reason "
                        "(--waive CODE --waiver-reason \"...\"), or the dataset is fixed",
            "why": "the data does not meet the stated quality standard, so no allocation "
                   "computed from it is gradeable",
        })

    for name in proposal.get("manual_verification_required", []):
        blocks.append({
            "code": "POSTING_NOT_VERIFIED",
            "detail": name,
            "response": "block",
            "resolver": "a human opens the careers page and confirms a live, current "
                        "posting for a matching title",
            "why": "liveness is a gate in the arithmetic and an assumption in this run; "
                   "this firm's board cannot be read by the scanner at all",
        })

    for m in proposal.get("moves", []):
        stab = m.get("stability")
        # Use the stability verdict the uncertainty pass recorded, so a move sitting
        # exactly on the floor cannot be called stable in one artifact and unstable
        # in another.
        unstable = (not m["stable"]) if "stable" in m else (
            stab is not None and stab < config.MOVE_STABILITY_FLOOR)
        if stab is not None and unstable:
            blocks.append({
                "code": "MOVE_NOT_STABLE",
                "detail": f"{m['from']} -> {m['to']} (stability {util.pct(stab, places=2)} < "
                          f"{util.pct(config.MOVE_STABILITY_FLOOR, places=2)})",
                "response": "block",
                "resolver": "the human decides whether to move anyway, on grounds the "
                            "engine does not have — a referral, a conversation, a deadline",
                "why": "the move is not distinguishable from leaving the allocation alone; "
                       "spending a week on a coin flip is worse than spending it on habit",
            })
        if m.get("to_sponsorship_p") is not None and (m.get("to_approvals") or 0) < config.SMALL_N_APPROVALS:
            flags.append({
                "code": "THIN_SPONSORSHIP_RECORD",
                "detail": f"{m['to']} — {int(m.get('to_approvals') or 0)} approvals",
                "response": "flag",
                "resolver": "the human reads the interval, not the point estimate",
                "why": "fewer than 25 filings; the credible interval is wider than the gap "
                       "to the next candidate",
            })

    eg = proposal.get("expected_gain", {})
    if eg.get("straddles_zero") or (eg.get("ci80") and eg["ci80"][0] is not None
                                    and eg["ci80"][0] <= 0 <= eg["ci80"][1]):
        flags.append({
            "code": "GAIN_STRADDLES_ZERO",
            "detail": f"80% CI {eg.get('ci80')}",
            "response": "flag",
            "resolver": "the human decides whether a move with no measurable gain is worth "
                        "making for reasons outside the model",
            "why": "the proposal cannot be distinguished from the baseline on this evidence",
        })

    sr = proposal.get("skip_rate", {})
    if sr.get("rate") is not None and sr["rate"] < config.MIN_SKIP_RATE:
        flags.append({
            "code": "SKIP_RATE_BELOW_TARGET",
            "detail": f"{util.pct(sr['rate'])} < {util.pct(config.MIN_SKIP_RATE)}",
            "response": "flag",
            "resolver": "the human tightens the filter before spending the week",
            "why": "Ch.15: a low skip rate is the filter failing, not productivity",
        })

    return {"blocks": blocks, "flags": flags,
            "decision": "block" if blocks else ("flag" if flags else "approve-eligible")}


def _decision_record(proposal, gate, verdict, approver, reason, executed):
    return {
        "_what_this_is": "A gate decision. The accountable record of a human either "
                         "committing a scarce resource or declining to.",
        "when": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "tool": "tools/effort-reallocator",
        "resource": "application slots (my own time against an F-1/OPT clock)",
        "action": "commit slots" if executed else "refused / blocked — nothing committed",
        "executed": executed,
        "approver": approver,
        "reason": reason,
        "proposal_generated": proposal.get("generated"),
        "gate_status": (gate or {}).get("status"),
        "moves": [{"quantity": m["quantity"], "from": m["from"], "to": m["to"],
                   "stability": m.get("stability")}
                  for m in proposal.get("moves", [])],
        "blocks": verdict["blocks"],
        "flags": verdict["flags"],
        "expected_gain": proposal.get("expected_gain", {}).get("point"),
        "expected_gain_ci80": proposal.get("expected_gain", {}).get("ci80"),
    }


def _append_gate_decision(record):
    """Append to logs/gate-decisions/ — a directory DOMAIN.md lists as planned."""
    d = util.ensure_dir(os.path.join(util.repo_root(), config.GATE_DECISIONS_DIR))
    day = record["when"][:10]
    path = os.path.join(d, f"{day}-effort-reallocator.md")
    lines = []
    if not os.path.exists(path):
        lines.append(f"# Gate decisions — {day}\n")
        lines.append("Append-only. Each entry is a human either committing a scarce "
                     "resource or declining to. Written by "
                     "`tools/effort-reallocator/reallocate.py execute`.\n")
    lines.append(f"## {record['when']} — {record['action']}\n")
    lines.append(f"- **Tool:** `{record['tool']}`")
    lines.append(f"- **Resource:** {record['resource']}")
    lines.append(f"- **Approver:** {record['approver'] or '(none — refused)'}")
    lines.append(f"- **Reason:** {record['reason'] or '(none given)'}")
    lines.append(f"- **Gate status:** {record['gate_status']}")
    lines.append(f"- **Expected gain:** {record['expected_gain']} "
                 f"(80% CI {record['expected_gain_ci80']})")
    if record["moves"]:
        lines.append("- **Moves:**")
        for m in record["moves"]:
            lines.append(f"  - {m['quantity']} slot(s) {m['from']} → {m['to']} "
                         f"(stability {util.pct(m.get('stability'), places=2)})")
    if record["blocks"]:
        lines.append("- **Blocked by:**")
        for b in record["blocks"]:
            lines.append(f"  - `{b['code']}` {b['detail']} — resolver: {b['resolver']}")
    if record["flags"]:
        lines.append("- **Flags carried:**")
        for f in record["flags"]:
            lines.append(f"  - `{f['code']}` {f['detail']}")
    lines.append("")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def execute(out_dir, approve, approver, reason, exit_codes):
    """The only command that could commit anything. It mostly refuses."""
    proposal, ppath = _load(out_dir, "proposal.json")
    gate, _ = _load(out_dir, "gate-report.json")

    print("=" * 74)
    print("HARD STOP — committing application slots")
    print("=" * 74)

    if proposal is None:
        print(f"refused: no proposal at {util.rel(ppath)}")
        print("  run `allocate` first. The engine will not execute a plan nobody has read.")
        return exit_codes["usage"]

    verdict = evaluate(proposal, gate)
    print(f"  proposal:    {util.rel(ppath)} (generated {proposal.get('generated')})")
    print(f"  gate status: {(gate or {}).get('status', 'MISSING')}")
    print(f"  moves:       {len(proposal.get('moves', []))}")
    for m in proposal.get("moves", []):
        print(f"    {m['quantity']} slot(s) {m['from']} → {m['to']} "
              f"(stability {util.pct(m.get('stability'), places=2)})")
    print("")

    if verdict["flags"]:
        print("  FLAGS (carried, not blocking):")
        for f in verdict["flags"]:
            print(f"    [flag]  {f['code']}: {f['detail']}")
            print(f"            resolver: {f['resolver']}")
        print("")

    if verdict["blocks"]:
        print("  BLOCKED — approval cannot clear these:")
        for b in verdict["blocks"]:
            print(f"    [block] {b['code']}: {b['detail']}")
            print(f"            why:      {b['why']}")
            print(f"            resolver: {b['resolver']}")
        print("")
        record = _decision_record(proposal, gate, verdict, approver if approve else None,
                                 reason, executed=False)
        log = _append_gate_decision(record)
        util.write_json(os.path.join(out_dir, "execution-decision.json"), record)
        print(f"  NOTHING MOVED. Decision logged: {util.rel(log)}")
        print("  There is no --force flag. Resolve the blocks or accept the baseline.")
        return exit_codes["blocked"]

    if not approve or not approver or not str(reason or "").strip():
        print("  REFUSED — this engine does not commit a resource on its own authority.")
        missing = []
        if not approve:
            missing.append("--approve")
        if not approver:
            missing.append('--approver "Your Name"')
        if not str(reason or "").strip():
            missing.append('--reason "what you verified"')
        print(f"    missing: {' '.join(missing)}")
        print("    the reason is not paperwork: it is the record of what a human checked")
        print("    that the engine could not.")
        record = _decision_record(proposal, gate, verdict, None, None, executed=False)
        log = _append_gate_decision(record)
        print(f"  NOTHING MOVED. Refusal logged: {util.rel(log)}")
        return exit_codes["refused"]

    if len(str(reason).strip()) < MIN_REASON_CHARS:
        print(f"  REFUSED — the reason is {len(str(reason).strip())} characters. A reason "
              f"shorter than {MIN_REASON_CHARS} is a rubber stamp, and a rubber stamp is "
              "how accountability disappears.")
        return exit_codes["refused"]

    record = _decision_record(proposal, gate, verdict, approver, reason, executed=True)
    ledger = {
        "_what_this_is": "The committed allocation. This is a LEDGER, not an action: the "
                         "tool cannot apply to a job. It records what a named human "
                         "committed to, so the outcome can be checked against the claim.",
        "committed_at": record["when"],
        "approver": approver,
        "reason": reason,
        "flags_accepted": verdict["flags"],
        "slots": [{"company_name": r["company_name"], "slots": r["slots"],
                   "composite": r["composite"],
                   "sponsorship_ci80": r["sponsorship_ci80"]}
                  for r in proposal["target"]["rows"]],
        "moves": proposal["moves"],
        "expected_gain": proposal["expected_gain"],
        "what_to_check_later": (
            "Responses per company against the composite that earned each slot. If the "
            "top-composite firms do not out-respond the rest, the engine is optimising a "
            "correlation that does not survive the intervention — which is the open "
            "question the causal section says it cannot answer yet."),
    }
    util.write_json(os.path.join(out_dir, "committed-allocation.json"), ledger)
    util.write_json(os.path.join(out_dir, "execution-decision.json"), record)
    log = _append_gate_decision(record)
    print(f"  APPROVED by {approver}")
    print(f"    reason: {reason}")
    if verdict["flags"]:
        print(f"    {len(verdict['flags'])} flag(s) accepted on the record")
    print("")
    print(f"  committed ledger: {util.rel(os.path.join(out_dir, 'committed-allocation.json'))}")
    print(f"  gate decision:    {util.rel(log)}")
    print("  This tool still applied to nothing. You do that part, and the ledger is what")
    print("  you check the outcome against.")
    return exit_codes["ok"]
