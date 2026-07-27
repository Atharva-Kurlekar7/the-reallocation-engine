"""Turn scores into a MOVE: shift Q slots from company A to company B.

A ranked list is not a reallocation. A reallocation names what to stop doing, and the
resource has to come from somewhere — so this module always works against a baseline
(where the slots go today) and emits the diff.

The allocation rule:

  value of the k-th slot at company c = composite(c) x base_response_rate x decay^(k-1)

Diminishing returns are not cosmetic. Without the decay every slot piles onto the
single highest-scoring firm, which is not how applying works — a second application to
the same company is worth less than the first, and a fourth is worth almost nothing.
`decay` is a your-input parameter and the fragility pass sweeps it.

Two constraints:

  * per-company cap (default 3) — more than three open applications at one firm is noise
  * Chapter 15's skip rate >= 50% — only Apply-tier companies earn slots, and if that
    leaves the budget underfilled the tool reports the shortfall rather than reaching
    down the ranking to spend the remainder. An unspent slot is a legitimate outcome;
    "skip is a successful outcome" is the domain's whole thesis.
"""

import datetime

from . import config
from . import util


def expected_yield(composite_score, base_response_rate):
    """Expected responses from one application. A proxy, and a thin one.

    base_response_rate is my own historical rate — a your-input number. Every yield
    figure in this tool scales linearly with it, so the absolute values mean much less
    than the differences between options.
    """
    return float(composite_score) * float(base_response_rate)


def _marginal_values(cand, cap, decay, base_rate):
    v0 = expected_yield(cand["composite"], base_rate)
    return [v0 * (decay ** k) for k in range(cap)]


def allocate_slots(candidates, slots, cap, decay, base_rate, eligible_recs=("Apply",)):
    """Greedy allocation by marginal value. Returns {normalized: slots} plus a log."""
    pool = [c for c in candidates if c["recommendation"] in eligible_recs
            and c["composite"] > 0]
    items = []
    for c in pool:
        for k, v in enumerate(_marginal_values(c, cap, decay, base_rate)):
            items.append((v, c["normalized"], k + 1))
    # Sort by marginal value, then deterministically by name so runs are reproducible.
    items.sort(key=lambda t: (-t[0], t[1], t[2]))

    alloc = {}
    picks = []
    for v, norm, k in items:
        if sum(alloc.values()) >= slots:
            break
        if alloc.get(norm, 0) != k - 1:
            continue  # slots at one company must be taken in order
        alloc[norm] = k
        picks.append({"normalized": norm, "slot_index": k, "marginal_value": round(v, 5)})
    return alloc, picks, pool


def propose(candidates, baseline, profile, slots=None, cap=None, decay=None):
    """The recommendation: a target allocation, and the move that gets there."""
    slots = slots or profile.get("slots_per_week", config.SLOTS_PER_WEEK)
    cap = cap or profile.get("per_company_cap", config.PER_COMPANY_CAP)
    decay = decay if decay is not None else profile.get("repeat_slot_decay",
                                                        config.REPEAT_SLOT_DECAY)
    base_rate = profile.get("base_response_rate", config.BASE_RESPONSE_RATE)
    by_norm = {c["normalized"]: c for c in candidates}

    # ── baseline: value where the slots go today ────────────────────────────
    base_alloc = {}
    baseline_rows = []
    for row in baseline.get("allocations", []):
        name = row.get("company_name", "")
        norm = util.normalize_company(name)
        n = int(row.get("slots", 0))
        cand = by_norm.get(norm)
        base_alloc[norm] = base_alloc.get(norm, 0) + n
        if cand is None:
            baseline_rows.append({
                "company_name": name, "normalized": norm, "slots": n,
                "composite": None, "expected_yield": None,
                "status": "not in the evidence set",
                "why": "no row in the SEC/DOL dataset matched this name, or its filed "
                       "titles do not match the profile. The engine has NO evidence "
                       "about it — which is not the same as evidence against it.",
                "note": row.get("note"),
            })
        else:
            vals = _marginal_values(cand, n, decay, base_rate)
            baseline_rows.append({
                "company_name": cand["company_name"], "normalized": norm, "slots": n,
                "composite": cand["composite"],
                "recommendation": cand["recommendation"],
                "expected_yield": round(sum(vals), 5),
                "status": "scored",
                "flags": cand["flags"],
                "note": row.get("note"),
            })

    baseline_yield = sum(r["expected_yield"] or 0.0 for r in baseline_rows)
    baseline_unknown_slots = sum(r["slots"] for r in baseline_rows
                                 if r["expected_yield"] is None)

    # ── target: greedy on Apply-tier only ──────────────────────────────────
    alloc, picks, apply_pool = allocate_slots(candidates, slots, cap, decay, base_rate)
    allocated_slots = sum(alloc.values())
    target_rows = []
    for norm, n in sorted(alloc.items(), key=lambda kv: -by_norm[kv[0]]["composite"]):
        c = by_norm[norm]
        vals = _marginal_values(c, n, decay, base_rate)
        target_rows.append({
            "company_name": c["company_name"], "normalized": norm, "slots": n,
            "composite": c["composite"], "recommendation": c["recommendation"],
            "sponsorship_p": c["sponsorship"]["p"],
            "sponsorship_ci80": c["sponsorship"]["ci80"],
            "sponsorship_tier": c["sponsorship"]["tier"],
            "approvals": c["sponsorship"]["approvals"],
            "expected_yield": round(sum(vals), 5),
            "manual_verification_required": c["manual_verification_required"],
            "flags": c["flags"],
            "reason": c["reason"],
        })
    target_yield = sum(r["expected_yield"] for r in target_rows)

    # ── the move: what to stop doing, and where it goes ─────────────────────
    deltas = {}
    for norm in sorted(set(base_alloc) | set(alloc)):
        deltas[norm] = alloc.get(norm, 0) - base_alloc.get(norm, 0)

    def composite_of(norm):
        c = by_norm.get(norm)
        return c["composite"] if c else -1.0

    # Deterministic ordering matters more than it looks: iterating a set of strings is
    # not stable across processes (Python randomises string hashing), so an unsorted
    # pairing would quietly produce different "from -> to" pairs on identical inputs.
    # Give up the weakest source first; fill the strongest destination first.
    sources = sorted(((n, -d) for n, d in deltas.items() if d < 0),
                     key=lambda t: (-t[1], composite_of(t[0]), t[0]))
    sinks = sorted(((n, d) for n, d in deltas.items() if d > 0),
                   key=lambda t: (-t[1], -composite_of(t[0]), t[0]))

    def label(norm):
        c = by_norm.get(norm)
        if c:
            return c["company_name"]
        for r in baseline_rows:
            if r["normalized"] == norm:
                return r["company_name"]
        return norm

    def why_from(norm):
        c = by_norm.get(norm)
        if c is None:
            return "no sponsorship evidence in the dataset for this firm"
        return c["reason"]

    moves = []
    si, ki = 0, 0
    src = list(sources)
    snk = list(sinks)
    while si < len(src) and ki < len(snk):
        s_norm, s_left = src[si]
        k_norm, k_left = snk[ki]
        q = min(s_left, k_left)
        cand_to = by_norm.get(k_norm)
        moves.append({
            "quantity": q,
            "unit": "application slots",
            "from": label(s_norm),
            "from_normalized": s_norm,
            "from_why": why_from(s_norm),
            "to": label(k_norm),
            "to_normalized": k_norm,
            "to_why": cand_to["reason"] if cand_to else "",
            "to_sponsorship_p": cand_to["sponsorship"]["p"] if cand_to else None,
            "to_sponsorship_ci80": cand_to["sponsorship"]["ci80"] if cand_to else None,
            "to_approvals": cand_to["sponsorship"]["approvals"] if cand_to else None,
            "to_manual_verification_required": bool(
                cand_to and cand_to["manual_verification_required"]),
        })
        src[si] = (s_norm, s_left - q)
        snk[ki] = (k_norm, k_left - q)
        if src[si][1] == 0:
            si += 1
        if snk[ki][1] == 0:
            ki += 1

    # ── ties: where the engine cannot actually tell candidates apart ─────────
    # The greedy sort breaks ties by company name, which means an alphabetical
    # accident decides who gets a week of my life. That is not a defensible
    # tie-break, so it is reported rather than hidden. This section exists because
    # the first run of this tool allocated its last four slots alphabetically.
    tie_report = None
    if target_rows:
        cutoff = min(r["composite"] for r in target_rows)
        tied_in = [r["company_name"] for r in target_rows
                   if abs(r["composite"] - cutoff) < 1e-9]
        tied_out = [c["company_name"] for c in candidates
                    if c["normalized"] not in alloc
                    and c["recommendation"] == "Apply"
                    and abs(c["composite"] - cutoff) < 1e-9]
        tie_report = {
            "cutoff_composite": cutoff,
            "selected_at_cutoff": tied_in,
            "excluded_at_identical_score": tied_out[:25],
            "excluded_at_identical_score_count": len(tied_out),
            "tie_break_rule": "company name, ascending — an arbitrary rule, stated so it "
                              "cannot masquerade as a finding",
            "what_it_means": (
                f"{len(tied_out)} firms scored EXACTLY the same as the weakest firm that "
                f"got a slot. The engine has no evidence distinguishing them; the cut was "
                f"alphabetical. Any of them is as defensible a target as the ones chosen."
                if tied_out else
                "No excluded firm ties the cutoff, so the selection boundary is not "
                "arbitrary in this run."),
        }

    # ── Ch.15 skip rate: of everything evaluated, how much did we decline? ──
    evaluated = len(candidates)
    skipped = sum(1 for c in candidates if c["recommendation"] == "Skip")
    considered = sum(1 for c in candidates if c["recommendation"] == "Consider")
    applied = sum(1 for c in candidates if c["recommendation"] == "Apply")
    skip_rate = (skipped / evaluated) if evaluated else None
    skip_verdict = (
        "healthy — a good run declines at least half of what it evaluates (Ch.15)"
        if skip_rate is not None and skip_rate >= config.MIN_SKIP_RATE
        else "BELOW the >=50% target — the filter is too loose. Reported, NOT enforced: "
             "raising the threshold until the skip rate hits 50% would be optimising the "
             "dial instead of the decision, which is Goodhart's law with extra steps. A "
             "human decides whether to tighten the profile or accept a loose filter."
    )

    return {
        "_what_this_is": "A RECOMMENDATION. Nothing has moved. Executing it requires a "
                         "named human, a written reason, and a passed gate.",
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "objective": ("maximise expected sponsored-interview yield per slot, subject to a "
                      "per-company cap — with Chapter 15's >=50% skip rate reported as a "
                      "dial, not enforced as a constraint, because it is a process metric "
                      "a human reads in two directions"),
        "objective_omits": ("referrals, my own application quality, interview conversion, "
                            "salary, team quality, and every firm with no filing record "
                            "and no supported ATS board"),
        "book_anchor": ("Ch.11 'Why liveness and timeline are multipliers, not addends' "
                        "(composite, threshold 0.3); Ch.2 the reallocation principle; "
                        "Ch.15 the skip-rate dial"),
        "settings": {"slots": slots, "cap": cap, "decay": decay,
                     "base_response_rate": base_rate},
        "moves": moves,
        "baseline": {
            "week_of": baseline.get("week_of"),
            "total_slots": sum(base_alloc.values()),
            "expected_yield": round(baseline_yield, 5),
            "slots_on_unscored_firms": baseline_unknown_slots,
            "rows": baseline_rows,
        },
        "target": {
            "total_slots": allocated_slots,
            "requested_slots": slots,
            "unspent_slots": slots - allocated_slots,
            "expected_yield": round(target_yield, 5),
            "rows": target_rows,
            "picks": picks,
        },
        "expected_gain": {
            "point": round(target_yield - baseline_yield, 5),
            "unit": "expected responses per week",
            "caveat": ("Scales linearly with base_response_rate (a your-input number) and "
                       "is computed from an observational proxy. Read the interval, not "
                       "this number."),
        },
        "skip_rate": {
            "evaluated": evaluated, "apply": applied, "consider": considered,
            "skip": skipped, "rate": round(skip_rate, 4) if skip_rate is not None else None,
            "target": config.MIN_SKIP_RATE, "verdict": skip_verdict,
            "two_levels": (
                "There are two skip rates and quoting only the flattering one would be "
                "dishonest. This figure is over companies the scorer actually EVALUATED. "
                "The pool filter declined the rest of the dataset before scoring, mostly "
                "because they have no filed job titles — which is not a judgment about "
                "them, it is the absence of one."),
        },
        "ties": tie_report,
        "manual_verification_required": [
            r["company_name"] for r in target_rows if r["manual_verification_required"]
        ],
    }


def attach_uncertainty(proposal, unc):
    """Fold the Monte Carlo results into each move, so no move travels bare."""
    by_pair = {(m["from_normalized"], m["to_normalized"]): m for m in proposal["moves"]}
    for mu in unc.get("moves", []):
        key = (mu["from_normalized"], mu["to_normalized"])
        m = by_pair.get(key)
        if not m:
            continue
        m["quantity_ci80"] = mu["quantity_ci80"]
        m["stability"] = mu["stability"]
        m["stable"] = mu["stable"]
        m["verdict"] = mu["verdict"]
    proposal["expected_gain"]["ci80"] = unc["expected_gain"]["ci80"]
    proposal["expected_gain"]["p_positive"] = unc["expected_gain"]["p_positive"]
    proposal["expected_gain"]["straddles_zero"] = unc["expected_gain"]["straddles_zero"]
    proposal["expected_gain"]["verdict"] = unc["expected_gain"]["verdict"]
    proposal["expected_gain"]["optimizers_curse"] = unc["optimizers_curse"]
    proposal["expected_gain"]["point_outside_interval"] = \
        unc["expected_gain"]["point_outside_interval"]
    proposal["expected_gain"]["point_vs_interval_note"] = \
        unc["expected_gain"]["point_vs_interval_note"]
    return proposal


def summary_lines(proposal, top=12):
    o = []
    o.append("=" * 74)
    o.append("REALLOCATION PROPOSAL — application slots (nothing has moved)")
    o.append("=" * 74)
    o.append(f"  objective: {proposal['objective']}")
    o.append(f"  omits:     {proposal['objective_omits']}")
    o.append("")
    sr = proposal["skip_rate"]
    o.append(f"  evaluated {sr['evaluated']:,} companies → Apply {sr['apply']:,} · "
             f"Consider {sr['consider']:,} · Skip {sr['skip']:,}")
    o.append(f"  skip rate {util.pct(sr['rate'])} (target ≥{util.pct(sr['target'])}) — {sr['verdict']}")
    o.append("")
    o.append("  THE MOVE")
    if not proposal["moves"]:
        o.append("    none — the baseline allocation is already what the engine would choose")
    for m in proposal["moves"]:
        q = m["quantity"]
        ci = m.get("quantity_ci80")
        ci_s = f" [80% CI {ci[0]:.1f}–{ci[1]:.1f}]" if ci else ""
        stab = f" stability {util.pct(m.get('stability'), places=2)}" if m.get("stability") is not None else ""
        o.append(f"    move {q} slot(s){ci_s}{stab}")
        o.append(f"      from  {m['from']}")
        o.append(f"      to    {m['to']}"
                 + (f"  (sponsorship p={util.fmt(m['to_sponsorship_p'])}, "
                    f"CI80 {util.fmt(m['to_sponsorship_ci80'][0])}–{util.fmt(m['to_sponsorship_ci80'][1])}, "
                    f"{int(m['to_approvals'] or 0)} approvals)" if m.get("to_sponsorship_p") is not None else ""))
        if m.get("verdict"):
            o.append(f"      verdict: {m['verdict']}")
        if m.get("to_manual_verification_required"):
            o.append("      !! posting NOT verifiable by the scanner — the hard stop will "
                     "block this until a human confirms a live posting")
    eg = proposal["expected_gain"]
    o.append("")
    o.append(f"  expected gain {eg['point']:+.3f} {eg['unit']}"
             + (f"  80% CI [{eg['ci80'][0]:+.3f}, {eg['ci80'][1]:+.3f}]" if eg.get("ci80") else ""))
    if eg.get("ci80"):
        lo, hi, pt = eg["ci80"][0], eg["ci80"][1], eg["point"]
        o.append("                " + util.interval_bar(lo, hi, pt, width=44)
                 + "  " + util.axis_label(lo, hi, pt))
        o.append("                (0 = no change · [ ] = 80% CI · | = point estimate)")
    if eg.get("verdict"):
        o.append(f"  {eg['verdict']}")
    if eg.get("point_outside_interval"):
        o.append("  NOTE: the point estimate is outside its own interval — "
                 "see proposal.md, it is a finding about an unpinned weight, not a bug")
    oc = eg.get("optimizers_curse")
    if oc:
        o.append(f"  optimizer's curse: re-optimising per draw would report "
                 f"{oc['reoptimised_mean_gain']:+.3f} instead of "
                 f"{oc['fixed_proposal_mean_gain']:+.3f} — "
                 f"{util.pct(oc['optimism_share_of_reported_gain'])} of that gain is the "
                 "optimiser fitting noise")
    ties = proposal.get("ties")
    if ties and ties["excluded_at_identical_score_count"]:
        o.append("")
        o.append(f"  TIES: {ties['excluded_at_identical_score_count']} firms scored exactly "
                 f"{util.fmt(ties['cutoff_composite'])} — the same as the weakest firm that "
                 "got a slot.")
        o.append(f"        The cut was made by {ties['tie_break_rule'].split(' — ')[0]}. "
                 "The engine cannot tell these apart.")
    o.append("")
    o.append(f"  TARGET ALLOCATION ({proposal['target']['total_slots']} of "
             f"{proposal['target']['requested_slots']} slots"
             + (f"; {proposal['target']['unspent_slots']} deliberately unspent"
                if proposal["target"]["unspent_slots"] else "") + ")")
    o.append("    slots  composite  sponsorship p (80% CI)        company")
    for r in proposal["target"]["rows"][:top]:
        ci = r["sponsorship_ci80"]
        ci_s = (f"{util.fmt(r['sponsorship_p'])} [{util.fmt(ci[0])}–{util.fmt(ci[1])}]"
                if r["sponsorship_p"] is not None else "unknown")
        flag = " !verify" if r["manual_verification_required"] else ""
        o.append(f"    {r['slots']:>5}  {util.fmt(r['composite']):>9}  {ci_s:<28}  "
                 f"{r['company_name']}{flag}")
    return "\n".join(o)


def render(proposal, top=25):
    o = []
    o.append(f"# Reallocation proposal — {proposal['generated'][:10]}\n")
    o.append("> **Nothing has moved.** This is a recommendation. Committing a slot "
             "requires `execute` with a named approver and a written reason.\n")
    o.append(f"**Objective:** {proposal['objective']}.  \n")
    o.append(f"**What the objective leaves out:** {proposal['objective_omits']}.\n")
    o.append(f"**Anchor:** {proposal['book_anchor']}.\n")

    o.append("## The move\n")
    if not proposal["moves"]:
        o.append("No move: the baseline is already what the engine would choose.\n")
    else:
        o.append("| Q | From | To | 80% CI on Q | Stability | Verdict |")
        o.append("|---:|---|---|---|---:|---|")
        for m in proposal["moves"]:
            ci = m.get("quantity_ci80")
            o.append(f"| {m['quantity']} | {m['from']} | {m['to']} | "
                     f"{f'{ci[0]:.1f}–{ci[1]:.1f}' if ci else '—'} | "
                     f"{util.pct(m.get('stability'), places=2)} | {m.get('verdict', '—')} |")
        o.append("")
        for m in proposal["moves"]:
            o.append(f"- **{m['quantity']} slot(s): {m['from']} → {m['to']}**  ")
            o.append(f"  *why leave:* {m['from_why']}  ")
            o.append(f"  *why arrive:* {m['to_why']}"
                     + (f" — sponsorship p={util.fmt(m['to_sponsorship_p'])} "
                        f"(80% CI {util.fmt(m['to_sponsorship_ci80'][0])}–"
                        f"{util.fmt(m['to_sponsorship_ci80'][1])}) over "
                        f"{int(m['to_approvals'] or 0)} approvals"
                        if m.get("to_sponsorship_p") is not None else ""))
            if m.get("to_manual_verification_required"):
                o.append("  **The destination's postings cannot be checked by the scanner. "
                         "The hard stop blocks this move until a human verifies a live posting.**")
    o.append("")

    eg = proposal["expected_gain"]
    o.append("## Expected gain, with its uncertainty\n")
    o.append(f"Point estimate **{eg['point']:+.3f} {eg['unit']}**"
             + (f", 80% credible interval **[{eg['ci80'][0]:+.3f}, {eg['ci80'][1]:+.3f}]**"
                if eg.get("ci80") else "") + ".\n")
    if eg.get("ci80"):
        lo, hi, pt = eg["ci80"][0], eg["ci80"][1], eg["point"]
        o.append("```")
        o.append("expected additional responses per week   ([ ] = 80% CI, | = point, 0 = no change)")
        o.append(util.interval_bar(lo, hi, pt, width=56) + "  " + util.axis_label(lo, hi, pt))
        o.append("")
        o.append("per-move stability — share of draws in which the move survives")
        o.append(f"({util.pct(config.MOVE_STABILITY_FLOOR)} floor marked +; below it the move is "
                 "reported as no change)")
        for m in proposal.get("moves", []):
            st = m.get("stability")
            if st is None:
                continue
            width = 40
            filled = int(round(st * width))
            floor_at = int(round(config.MOVE_STABILITY_FLOOR * width))
            cells = ["#" if i < filled else "." for i in range(width)]
            if 0 <= floor_at < width and cells[floor_at] == ".":
                cells[floor_at] = "+"
            o.append("".join(cells) + f" {util.pct(st, places=2):>7}  {m['to'][:28]}"
                     + ("" if m.get("stable") else "  <- no change"))
        o.append("```\n")
    o.append(f"*{eg['caveat']}*\n")
    if eg.get("verdict"):
        o.append(f"**Verdict:** {eg['verdict']}\n")
    if eg.get("point_vs_interval_note"):
        o.append(f"**Point estimate vs interval.** {eg['point_vs_interval_note']}\n")
    oc = eg.get("optimizers_curse")
    if oc:
        o.append("### The optimizer's curse, measured\n")
        o.append(f"{oc['what_it_is']}\n")
        o.append(f"- Gain of the allocation actually recommended, held fixed: "
                 f"**{oc['fixed_proposal_mean_gain']:+.5f}**")
        o.append(f"- Gain if the allocation is re-optimised inside every draw: "
                 f"**{oc['reoptimised_mean_gain']:+.5f}** "
                 f"(80% CI {oc['reoptimised_ci80']})")
        o.append(f"- Optimism: **{oc['optimism']:+.5f}**, i.e. "
                 f"**{util.pct(oc['optimism_share_of_reported_gain'])}** of the naive figure")
        o.append(f"\n{oc['why_it_matters']}\n")

    ties = proposal.get("ties")
    if ties:
        o.append("## Ties — where the engine cannot tell candidates apart\n")
        o.append(f"Cutoff composite **{util.fmt(ties['cutoff_composite'])}**. "
                 f"Tie-break rule: *{ties['tie_break_rule']}*.\n")
        o.append(f"{ties['what_it_means']}\n")
        if ties["excluded_at_identical_score"]:
            o.append("Firms excluded at an identical score: "
                     + ", ".join(ties["excluded_at_identical_score"][:15])
                     + (f", … ({ties['excluded_at_identical_score_count']} total)"
                        if ties["excluded_at_identical_score_count"] > 15 else "") + "\n")

    sr = proposal["skip_rate"]
    o.append("## Skip rate (Ch.15)\n")
    o.append(f"Evaluated **{sr['evaluated']:,}** companies → Apply {sr['apply']:,} · "
             f"Consider {sr['consider']:,} · Skip {sr['skip']:,}. "
             f"**Skip rate {util.pct(sr['rate'])}** against a ≥{util.pct(sr['target'])} target.\n")
    o.append(f"{sr['verdict']}\n")
    o.append(f"*{sr['two_levels']}*\n")
    meta = proposal.get("evidence_meta") or {}
    counts = meta.get("counts") or {}
    if counts:
        o.append("| Stage | Rows |")
        o.append("|---|---:|")
        o.append(f"| dataset | {counts.get('rows', 0):,} |")
        o.append(f"| no filed job titles (never scored) | {counts.get('no_titles', 0):,} |")
        o.append(f"| titles present but off-profile | {counts.get('title_mismatch', 0):,} |")
        o.append(f"| refused by the gate | {counts.get('gate_rejected', 0):,} |")
        o.append(f"| duplicate identity, first kept | {counts.get('duplicate_identity', 0):,} |")
        o.append(f"| **evaluated by the scorer** | **{meta.get('candidate_count', 0):,}** |")
        o.append("")
    bs = meta.get("blind_spot")
    if bs:
        o.append("### The blind spot\n")
        o.append(f"**{bs['count']:,} firms** have {bs['what']}. {bs['why_it_matters']}\n")
        o.append(f"{bs['why_the_engine_cannot_fix_it']}\n")

    o.append("## Target allocation\n")
    o.append(f"{proposal['target']['total_slots']} of {proposal['target']['requested_slots']} "
             "slots allocated"
             + (f"; **{proposal['target']['unspent_slots']} left deliberately unspent** — "
                "the engine will not reach down the ranking to fill a budget."
                if proposal["target"]["unspent_slots"] else "") + "\n")
    o.append("| Slots | Composite | Sponsorship p (80% CI) | Approvals | Tier | Company | Flags |")
    o.append("|---:|---:|---|---:|---|---|---|")
    for r in proposal["target"]["rows"][:top]:
        ci = r["sponsorship_ci80"]
        ci_s = (f"{util.fmt(r['sponsorship_p'])} [{util.fmt(ci[0])}–{util.fmt(ci[1])}]"
                if r["sponsorship_p"] is not None else "unknown")
        o.append(f"| {r['slots']} | {util.fmt(r['composite'])} | {ci_s} | "
                 f"{util.fmt(r['approvals'], 0)} | {r['sponsorship_tier']} | "
                 f"{r['company_name']} | {', '.join('`%s`' % f for f in r['flags'])} |")
    o.append("")

    o.append("## Baseline being argued against\n")
    o.append(f"Week of {proposal['baseline']['week_of']} — "
             f"{proposal['baseline']['total_slots']} slots, expected yield "
             f"{proposal['baseline']['expected_yield']:.3f}.\n")
    o.append("| Slots | Company | Composite | Status |")
    o.append("|---:|---|---:|---|")
    for r in proposal["baseline"]["rows"]:
        o.append(f"| {r['slots']} | {r['company_name']} | "
                 f"{util.fmt(r.get('composite'))} | {r['status']}"
                 + (f" — {r['why']}" if r.get("why") else "") + " |")
    o.append("")
    if proposal["manual_verification_required"]:
        o.append("## Requires human verification before any slot is committed\n")
        for name in proposal["manual_verification_required"]:
            o.append(f"- {name}")
        o.append("")
    return "\n".join(o) + "\n"
