"""Who does this engine starve, and where exactly does that enter?

The subject of a fairness audit here is unusual and worth stating plainly: the engine
allocates MY attention, so the parties it advantages or starves are **employers**, not
job-seekers. That does not make the bias harmless. It decides which firms ever see an
application from a candidate who needs sponsorship, and the pattern it produces is
systematic, self-reinforcing, and invisible in the accuracy of any single score.

WHERE THE BIAS ENTERS — traced to a mechanism, per stage

  Sampling  A firm appears in the sponsorship data only if it filed an H-1B petition.
            Non-filers are indistinguishable from firms that would sponsor but have
            not yet had the chance. ~95% of rows carry no filing data at all.
  Labels    `Approval_Rate` is an outcome measured on firms that had already selected a
            candidate. It is a label about the government's decision, not the firm's
            willingness — and certainly not about me.
  Coverage  A firm is only *checkable* if its board runs greenhouse / lever / ashby.
            This is the sharpest mechanism in the whole engine, and it lives in
            tooling, not in the model: AMGEN INC (1,882 approvals) scored 0.000 in the
            earlier worked run purely because its board is Workday.
  Objective Expected yield per slot rewards volume of past filings, which is a proxy
            for firm size. Big firms have more filings, so they win slots.
  Feedback  A firm that gets no slots produces no outcome data for me, so it never
            earns evidence, so it never gets slots. The loop closes on itself and the
            engine calls the result "efficient".

TWO METRICS THAT DISAGREE (and cannot both be satisfied)

  1. ALLOCATION PARITY — every eligible firm should have a comparable chance at a slot,
     independent of group. Measured as slots-per-eligible-firm by group, reported as a
     disparate-impact ratio (min group rate / max group rate).
  2. CALIBRATION TO EVIDENCE — a group's share of slots should match its share of the
     total evidence-weighted expected yield. Slots should follow the evidence.

They conflict structurally: the groups with the thinnest evidence are precisely the
ones parity would give more slots to, and calibration gives fewer. The tool computes
both, states which one it chose, and quantifies what that choice costs.
"""

import datetime

from . import config
from . import util


def _group_ats(c):
    return "supported ATS board" if c["ats"]["supported_provider"] else "no supported board"


def _group_evidence_depth(c):
    a = c["sponsorship"]["approvals"]
    if a is None:
        return "no filing record"
    if a < config.SMALL_N_APPROVALS:
        return f"thin record (<{config.SMALL_N_APPROVALS} approvals)"
    return f"deep record (>={config.SMALL_N_APPROVALS} approvals)"


def _group_stage(c):
    stage = c["latest_funding_stage"] or "unstated"
    if stage in config.EARLY_STAGES:
        return "early stage (per last Form D)"
    if stage == "Series D+":
        return "late stage (per last Form D)"
    if stage in ("Series B", "Series C"):
        return "mid stage (per last Form D)"
    return "no stage on record"


GROUPINGS = {
    "ats_coverage": (_group_ats,
                     "Can the repo's scanner even check this firm's postings? "
                     "greenhouse / lever / ashby only."),
    "evidence_depth": (_group_evidence_depth,
                       "How many filings stand behind the sponsorship estimate."),
    "funding_stage": (_group_stage,
                      "Stage of the LAST Form D filing — not the firm's current stage. "
                      "The gate flags this; the grouping inherits the flaw and says so."),
}


def _metrics_for_grouping(candidates, slots_by_norm, yields_by_norm, keyfn):
    groups = {}
    for c in candidates:
        g = keyfn(c)
        rec = groups.setdefault(g, {
            "group": g, "eligible": 0, "apply_tier": 0, "slots": 0,
            "evidence_yield": 0.0, "companies_with_slots": 0,
        })
        rec["eligible"] += 1
        if c["recommendation"] == "Apply":
            rec["apply_tier"] += 1
        n = slots_by_norm.get(c["normalized"], 0)
        rec["slots"] += n
        if n:
            rec["companies_with_slots"] += 1
        rec["evidence_yield"] += yields_by_norm.get(c["normalized"], 0.0)

    total_slots = sum(g["slots"] for g in groups.values()) or 1
    total_yield = sum(g["evidence_yield"] for g in groups.values()) or 1.0
    total_eligible = sum(g["eligible"] for g in groups.values()) or 1

    rows = []
    for g in groups.values():
        slots_per_eligible = g["slots"] / g["eligible"] if g["eligible"] else 0.0
        rows.append({
            **g,
            "eligible_share": round(g["eligible"] / total_eligible, 4),
            "slot_share": round(g["slots"] / total_slots, 4),
            "evidence_share": round(g["evidence_yield"] / total_yield, 4),
            "slots_per_eligible_company": round(slots_per_eligible, 5),
            "parity_gap": round(g["slots"] / total_slots - g["eligible"] / total_eligible, 4),
            "calibration_gap": round(g["slots"] / total_slots
                                     - g["evidence_yield"] / total_yield, 4),
        })
    rows.sort(key=lambda r: -r["slot_share"])

    rates = [r["slots_per_eligible_company"] for r in rows]
    hi = max(rates) if rates else 0.0
    lo = min(rates) if rates else 0.0
    di_ratio = (lo / hi) if hi > 0 else 0.0
    worst_parity = min(rows, key=lambda r: r["parity_gap"]) if rows else None
    worst_calib = max(rows, key=lambda r: abs(r["calibration_gap"])) if rows else None
    return {
        "groups": rows,
        "allocation_parity": {
            "metric": "disparate impact ratio = min(slots per eligible company) / max(...)",
            "value": round(di_ratio, 4),
            "interpretation": ("1.0 is exact parity. The conventional 0.8 rule of thumb is "
                              "borrowed from employment law and is a weak analogy here — "
                              "reported because it is legible, not because it is apt."),
            "passes_four_fifths": di_ratio >= 0.8,
            "worst_served_group": worst_parity["group"] if worst_parity else None,
            "worst_served_gap": worst_parity["parity_gap"] if worst_parity else None,
        },
        "calibration": {
            "metric": "slot share minus evidence share, by group",
            "largest_deviation_group": worst_calib["group"] if worst_calib else None,
            "largest_deviation": worst_calib["calibration_gap"] if worst_calib else None,
            "interpretation": ("0.0 means slots track the evidence exactly. This is the "
                              "definition the engine optimises."),
        },
    }


def audit(candidates, proposal):
    gate = proposal["gate"]
    slots_by_norm = {r["normalized"]: r["slots"] for r in proposal["target"]["rows"]}
    base_rate = proposal["settings"]["base_response_rate"]
    yields_by_norm = {c["normalized"]: max(0.0, c["composite"] * base_rate)
                      for c in candidates}

    by_grouping = {}
    for name, (keyfn, why) in GROUPINGS.items():
        by_grouping[name] = {
            "why_this_grouping": why,
            **_metrics_for_grouping(candidates, slots_by_norm, yields_by_norm, keyfn),
        }

    # The starvation count that matters most: firms with real sponsorship evidence that
    # get zero slots because nobody can check their postings.
    starved = [
        {
            "company_name": c["company_name"],
            "approvals": c["sponsorship"]["approvals"],
            "sponsorship_p": c["sponsorship"]["p"],
            "composite": c["composite"],
            "recommendation": c["recommendation"],
            "liveness_status": c["liveness"]["status"],
            "why_starved": "no supported ATS board — the scanner cannot reach it",
        }
        for c in candidates
        if not c["ats"]["supported_provider"]
        and (c["sponsorship"]["approvals"] or 0) >= config.TIER_PROVEN_MIN_APPROVALS
        and slots_by_norm.get(c["normalized"], 0) == 0
    ]
    starved.sort(key=lambda r: -(r["approvals"] or 0))

    thin_starved = [c for c in candidates
                    if (c["sponsorship"]["approvals"] or 0) < config.SMALL_N_APPROVALS
                    and slots_by_norm.get(c["normalized"], 0) == 0]

    # The counterfactual cost of choosing calibration over parity, in slots.
    ats_rows = by_grouping["ats_coverage"]["groups"]
    total_slots = sum(r["slots"] for r in ats_rows) or 1
    parity_target = {}
    for r in ats_rows:
        parity_target[r["group"]] = r["eligible_share"] * total_slots
    parity_cost = {
        g: round(parity_target[g] - next(r["slots"] for r in ats_rows if r["group"] == g), 2)
        for g in parity_target
    }

    return {
        "_what_this_is": "Bias traced from collection to output, with two fairness "
                         "metrics that cannot both be satisfied and a stated choice.",
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "who_is_affected": (
            "The engine allocates MY attention, so the parties advantaged or starved are "
            "employers. The harm is not to a protected class of people; it is a systematic, "
            "self-reinforcing pattern in which firms ever see an application from a "
            "candidate who needs sponsorship."),
        "mechanisms": [
            {"stage": "sampling",
             "mechanism": "a firm appears only if it filed an H-1B petition; non-filers are "
                          "indistinguishable from would-be sponsors",
             # Measured on THIS dataset by the gate, not quoted from the earlier
             # validation report (which said 96.8% on a differently filtered slice).
             # A bias audit that cites a number its own gate contradicts is not an audit.
             "evidence": f"{round(gate['h1b_missing_rate'] * 100, 1)}% of dataset rows "
                         f"({gate['row_count'] - gate['rows_with_h1b_fields']:,} of "
                         f"{gate['row_count']:,}) carry no H-1B fields, measured by the "
                         "gate in this run"},
            {"stage": "labels",
             "mechanism": "Approval_Rate is the government's decision on a candidate the "
                          "firm had already selected — not willingness, and not about me",
             "evidence": "the column is approvals/(approvals+denials) over filed petitions"},
            {"stage": "coverage",
             "mechanism": "only greenhouse / lever / ashby boards are checkable, so "
                          "everything else is either flagged or zeroed by policy",
             "evidence": "AMGEN INC, 1,882 approvals, scored 0.000 in the earlier worked "
                         "run because its board is Workday"},
            {"stage": "objective",
             "mechanism": "expected yield per slot rewards filing volume, a proxy for firm size",
             "evidence": "the volume factor saturates at "
                         f"{int(config.VOLUME_REF)} approvals — a your-input parameter"},
            {"stage": "feedback",
             "mechanism": "no slots -> no outcomes -> no evidence -> no slots",
             "evidence": f"{len(thin_starved)} thin-record firms received zero slots in this run"},
        ],
        "groupings": by_grouping,
        "starved_despite_strong_evidence": starved[:15],
        "starved_despite_strong_evidence_count": len(starved),
        "thin_record_zero_slot_count": len(thin_starved),
        "fairness_tradeoff": {
            "definition_1": {
                "name": "allocation parity across ATS coverage",
                "requires": "slots per eligible company equal across groups",
                "disparate_impact_ratio": by_grouping["ats_coverage"]["allocation_parity"]["value"],
                "cost_if_chosen": ("slots would go to firms whose postings nobody can "
                                   "verify, so some fraction of the week would be spent "
                                   "applying into voids — the exact waste the liveness "
                                   "gate exists to prevent"),
            },
            "definition_2": {
                "name": "calibration to evidence",
                "requires": "slot share equals evidence-weighted yield share",
                "largest_deviation": by_grouping["ats_coverage"]["calibration"]["largest_deviation"],
                "cost_if_chosen": ("firms with thin or no filing record are starved by "
                                   "construction, including the small Form D-funded firms "
                                   "the book's own funding thesis says to surface"),
            },
            "incompatible_because": (
                "Parity demands slots for the groups with the least evidence; calibration "
                "demands slots follow evidence. With a fixed 12-slot budget, satisfying "
                "one violates the other — there is no allocation that does both."),
            "chosen": "calibration to evidence",
            "why_chosen": (
                "The resource is a week of my own life against an OPT clock. I am not a "
                "regulator distributing a public good; I am one candidate with twelve "
                "applications. Parity across employers is not a duty I owe, and the cost "
                "of parity here is applications sent into unverifiable voids."),
            "what_it_costs": {
                "slots_parity_would_redistribute": parity_cost,
                "firms_with_deep_records_starved": len(starved),
                "thin_record_firms_starved": len(thin_starved),
                "internal_contradiction": (
                    "This choice starves early-stage firms, which contradicts the book's "
                    "own thesis that recent Form D funding is a hiring signal worth "
                    "chasing. The engine's objective and the domain's premise disagree, "
                    "and the objective currently wins."),
            },
        },
        "highest_leverage_intervention": {
            "point": "ATS provider coverage — a Workday/proprietary-board adapter",
            "why": (
                "It is the only mechanism here that is a tooling gap rather than a data "
                "limitation, so it is fixable by writing code rather than by assuming "
                "something unknowable. Every other mechanism (missing filings, "
                "selection-conditioned labels, size proxy) needs data that does not exist. "
                "Coverage needs a provider module."),
            "expected_effect": (
                f"{len(starved)} firms with >= {config.TIER_PROVEN_MIN_APPROVALS} approvals "
                "currently get zero slots because nobody can check them. Adding one "
                "provider moves them from 'flagged, human must verify' to 'checked', which "
                "is where the engine's gate is supposed to operate."),
            "not_the_leverage_point": (
                "Reweighting the composite. Tuning weights redistributes among firms the "
                "engine can already see, which leaves the mechanism untouched."),
        },
    }


def summary_lines(bias):
    o = []
    o.append("")
    o.append("=" * 74)
    o.append("BIAS AUDIT")
    o.append("=" * 74)
    ats = bias["groupings"]["ats_coverage"]
    o.append("  by ATS coverage (the sharpest mechanism — tooling, not model):")
    o.append("    group                      eligible  slots  slot%  evid%  slots/firm")
    for g in ats["groups"]:
        o.append(f"    {g['group']:<25} {g['eligible']:>8,} {g['slots']:>6} "
                 f"{util.pct(g['slot_share'], 0):>6} {util.pct(g['evidence_share'], 0):>6} "
                 f"{g['slots_per_eligible_company']:>10.4f}")
    ap = ats["allocation_parity"]
    o.append(f"    disparate impact ratio {ap['value']:.4f} "
             f"({'passes' if ap['passes_four_fifths'] else 'FAILS'} the 4/5 rule of thumb)")
    o.append("")
    o.append(f"  starved despite deep records: {bias['starved_despite_strong_evidence_count']} firms")
    for s in bias["starved_despite_strong_evidence"][:3]:
        o.append(f"    {s['company_name']} — {int(s['approvals'] or 0):,} approvals, "
                 f"0 slots ({s['why_starved']})")
    t = bias["fairness_tradeoff"]
    o.append("")
    o.append(f"  two definitions in tension: {t['definition_1']['name']} vs "
             f"{t['definition_2']['name']}")
    o.append(f"  chosen: {t['chosen']} — {t['why_chosen'][:120]}...")
    o.append(f"  cost:   {t['what_it_costs']['firms_with_deep_records_starved']} deep-record "
             f"firms and {t['what_it_costs']['thin_record_firms_starved']} thin-record firms "
             "get nothing")
    o.append(f"  leverage point: {bias['highest_leverage_intervention']['point']}")
    return "\n".join(o)


def render(bias):
    o = []
    o.append(f"# Bias audit — {bias['generated'][:10]}\n")
    o.append(f"{bias['who_is_affected']}\n")

    o.append("## Where the bias enters, by stage\n")
    o.append("| Stage | Mechanism | Evidence in this run |")
    o.append("|---|---|---|")
    for m in bias["mechanisms"]:
        o.append(f"| {m['stage']} | {m['mechanism']} | {m['evidence']} |")
    o.append("")

    for name, grp in bias["groupings"].items():
        o.append(f"## Grouping: `{name}`\n")
        o.append(f"*{grp['why_this_grouping']}*\n")
        o.append("| Group | Eligible | Apply tier | Slots | Slot share | Evidence share "
                 "| Slots per firm | Parity gap | Calibration gap |")
        o.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for g in grp["groups"]:
            o.append(f"| {g['group']} | {g['eligible']:,} | {g['apply_tier']:,} | "
                     f"{g['slots']} | {util.pct(g['slot_share'])} | "
                     f"{util.pct(g['evidence_share'])} | "
                     f"{g['slots_per_eligible_company']:.5f} | "
                     f"{g['parity_gap']:+.4f} | {g['calibration_gap']:+.4f} |")
        ap = grp["allocation_parity"]
        o.append("")
        o.append(f"**Allocation parity (disparate impact ratio): {ap['value']:.4f}** — "
                 f"{'passes' if ap['passes_four_fifths'] else '**fails**'} the four-fifths "
                 f"rule of thumb. Worst-served group: *{ap['worst_served_group']}* "
                 f"(parity gap {ap['worst_served_gap']:+.4f}).  ")
        o.append(f"*{ap['interpretation']}*\n")
        o.append(f"**Calibration:** largest deviation is *{grp['calibration']['largest_deviation_group']}* "
                 f"at {grp['calibration']['largest_deviation']:+.4f} slot-share points "
                 f"from its evidence share.\n")

    o.append("## Starved despite deep sponsorship records\n")
    o.append(f"{bias['starved_despite_strong_evidence_count']} firms with at least "
             f"{config.TIER_PROVEN_MIN_APPROVALS} approvals received zero slots because "
             "their postings cannot be checked. This is the bias in one table.\n")
    if bias["starved_despite_strong_evidence"]:
        o.append("| Company | Approvals | Composite | Rec | Liveness status |")
        o.append("|---|---:|---:|---|---|")
        for s in bias["starved_despite_strong_evidence"]:
            o.append(f"| {s['company_name']} | {int(s['approvals'] or 0):,} | "
                     f"{util.fmt(s['composite'])} | {s['recommendation']} | "
                     f"`{s['liveness_status']}` |")
    o.append("")

    t = bias["fairness_tradeoff"]
    o.append("## The tradeoff: two definitions, one budget\n")
    o.append(f"**Definition 1 — {t['definition_1']['name']}.** Requires "
             f"{t['definition_1']['requires']}. Current disparate impact ratio: "
             f"{t['definition_1']['disparate_impact_ratio']:.4f}.  ")
    o.append(f"*Cost if chosen:* {t['definition_1']['cost_if_chosen']}.\n")
    o.append(f"**Definition 2 — {t['definition_2']['name']}.** Requires "
             f"{t['definition_2']['requires']}. Largest deviation: "
             f"{t['definition_2']['largest_deviation']:+.4f}.  ")
    o.append(f"*Cost if chosen:* {t['definition_2']['cost_if_chosen']}.\n")
    o.append(f"**Why they cannot both hold:** {t['incompatible_because']}\n")
    o.append(f"**Chosen: {t['chosen']}.** {t['why_chosen']}\n")
    o.append("**What that choice costs, in slots:**\n")
    for g, cost in t["what_it_costs"]["slots_parity_would_redistribute"].items():
        o.append(f"- *{g}*: parity would move {cost:+.2f} slots relative to the "
                 "calibrated allocation.")
    o.append(f"- {t['what_it_costs']['firms_with_deep_records_starved']} deep-record firms "
             f"and {t['what_it_costs']['thin_record_firms_starved']} thin-record firms "
             "receive nothing.")
    o.append(f"\n**The uncomfortable part:** {t['what_it_costs']['internal_contradiction']}\n")

    li = bias["highest_leverage_intervention"]
    o.append("## Highest-leverage intervention point\n")
    o.append(f"**{li['point']}.** {li['why']}\n")
    o.append(f"*Expected effect:* {li['expected_effect']}\n")
    o.append(f"*What is not the leverage point:* {li['not_the_leverage_point']}\n")
    return "\n".join(o) + "\n"
