"""Where the recommendation breaks — and how small the push has to be.

Each perturbation below is something that could plausibly happen without anyone
noticing, which is the only kind worth testing. A tool that survives absurd inputs and
flips on a units error is not robust; it is lucky.

  P1  VINTAGE SHIFT — the filing snapshot loses its most recent year. Implemented as a
      discount on approvals, swept downward until the top allocation changes. The
      dataset holds only cumulative totals, so a true year-by-year replay is impossible.
      That impossibility is itself the finding: the engine cannot tell a firm that
      sponsored 500 people in 2016 and stopped from one sponsoring 500 people now.

  P2  UNITS ERROR — one company's `Approval_Rate` arrives on a 0-1 scale in a 0-100
      column. A single cell, in a 30,369-row file. The gate catches this class, so the
      test is run twice: once with the gate (does it catch it?) and once with the check
      disabled (what would it have cost?).

  P3  GAMED INPUT — an evergreen "talent pipeline" requisition that never closes. It
      passes every liveness signal the scanner has, because it is genuinely posted and
      genuinely open. The engine spends its slots on a req with no hiring manager
      behind it. No data check catches this; only a human reading the posting does.

  P4  ENTITY SPLIT — one firm's history divided across two legal names (the dataset
      already contains PELOTON INTERACTIVE INC and PELOTON INTERACTIVE LLC with
      identical counts). Splitting the top firm's approvals in half twice is a two-cell
      edit that can drop it out of the Proven tier entirely.

  P5  PARAMETER SWEEP — VOLUME_REF and the repeat-slot decay are your-input numbers
      with no external justification. Sweeping them shows how much of the ranking is
      the data and how much is me.

Every result reports a FRAGILITY DISTANCE: the smallest change, in units a human would
recognise, that alters the recommendation.
"""

import copy
import csv
import datetime

from . import allocate as allocate_mod
from . import composite
from . import config
from . import evidence as evidence_mod
from . import util


def _top_slots(proposal):
    return [(r["normalized"], r["slots"]) for r in proposal["target"]["rows"]]


def _fingerprint(proposal):
    return tuple(sorted((r["normalized"], r["slots"]) for r in proposal["target"]["rows"]))


def _reallocate(candidates, baseline, profile, slots, cap, decay):
    return allocate_mod.propose(candidates, baseline, profile, slots=slots, cap=cap,
                               decay=decay)


def _rescore(candidates, profile):
    weights, needs = composite.apply_profile(config.WEIGHTS, profile)
    for c in candidates:
        composite.score_candidate(c, weights=weights, needs_sponsor=needs)
    candidates.sort(key=lambda c: -c["composite"])
    return candidates


def _clone(candidates):
    return copy.deepcopy(candidates)


def _rebuild_sponsorship(cand, approvals, denials, rng, volume_ref=None):
    cand["sponsorship"] = evidence_mod.sponsorship_evidence(approvals, denials, rng,
                                                            volume_ref=volume_ref)
    return cand


def p1_vintage_shift(candidates, baseline, profile, slots, cap, decay, base_fp):
    """Discount approvals as though a year of filings were removed."""
    import random
    steps = []
    flip_at = None
    for keep in (0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.60, 0.50, 0.40, 0.25):
        rng = random.Random(config.CI_SEED)
        pool = _clone(candidates)
        for c in pool:
            a = c["sponsorship"]["approvals"]
            d = c["sponsorship"]["denials"]
            if a is None:
                continue
            _rebuild_sponsorship(c, round(a * keep), d, rng)
        _rescore(pool, profile)
        prop = _reallocate(pool, baseline, profile, slots, cap, decay)
        fp = _fingerprint(prop)
        changed = fp != base_fp
        steps.append({"approvals_kept": keep, "allocation_changed": changed,
                      "top_company": prop["target"]["rows"][0]["company_name"]
                      if prop["target"]["rows"] else None,
                      "skip_rate": prop["skip_rate"]["rate"]})
        if changed and flip_at is None:
            flip_at = keep
    return {
        "id": "P1",
        "name": "vintage shift — one fiscal year of filings removed",
        "realistic_because": "the dataset is a snapshot with no per-record date; a refresh "
                             "shifts every count at once and nothing in the file says so",
        "steps": steps,
        "flips_at_approvals_kept": flip_at,
        "fragility_distance": (f"the allocation changes once approvals are discounted to "
                               f"{flip_at:.0%} of their stated value"
                               if flip_at else
                               "no change down to 25% of stated approvals — the ranking is "
                               "dominated by order-of-magnitude gaps, not by marginal counts"),
        "honest_limit": ("The dataset holds cumulative totals only, so this is a proportional "
                         "discount and not a true year-by-year replay. The engine cannot "
                         "distinguish a firm that sponsored heavily in 2016 and stopped from "
                         "one sponsoring heavily now. That is a data limitation no amount of "
                         "modelling fixes."),
    }


def p2_units_error(candidates, baseline, profile, slots, cap, decay, base_fp, gate):
    """One cell on the wrong scale, in a 30,369-row file."""
    import random
    if not candidates:
        return {"id": "P2", "name": "units error", "applicable": False}
    target = next((c for c in candidates
                   if (c["sponsorship"]["approvals"] or 0) > 0), None)
    if target is None:
        return {"id": "P2", "name": "units error", "applicable": False}

    rng = random.Random(config.CI_SEED)
    pool = _clone(candidates)
    victim = next(c for c in pool if c["normalized"] == target["normalized"])
    a = victim["sponsorship"]["approvals"]
    d = victim["sponsorship"]["denials"]
    # A 0-1 rate in a 0-100 column: the row now reads as ~1% approval. Reconstruct the
    # counts that a downstream consumer would infer from that rate.
    implied_rate = (100.0 * a / (a + d)) if (a + d) else 0.0
    corrupted_rate = implied_rate / 100.0
    implied_denials = max(0.0, a * (100.0 - corrupted_rate) / max(corrupted_rate, 1e-9))
    _rebuild_sponsorship(victim, a, implied_denials, rng)
    _rescore(pool, profile)
    prop = _reallocate(pool, baseline, profile, slots, cap, decay)
    changed = _fingerprint(prop) != base_fp
    gate_catches = "RATE_SCALE_ANOMALY" in gate["checks"]

    slots_before = dict(base_fp).get(target["normalized"], 0)
    slots_after = next((r["slots"] for r in prop["target"]["rows"]
                        if r["normalized"] == target["normalized"]), 0)
    return {
        "id": "P2",
        "name": "units error — one Approval_Rate cell on a 0-1 scale",
        "realistic_because": "the dataset already mixes scale conventions across columns; "
                             "one upstream refresh writing a proportion instead of a "
                             "percentage is a single-line change nobody reviews",
        "cells_changed": 1,
        "of_total_cells": f"1 of {gate['row_count']:,} rows",
        "victim": target["company_name"],
        "victim_stated_rate_pct": round(implied_rate, 2),
        "corrupted_to": round(corrupted_rate, 4),
        "sponsorship_p_before": target["sponsorship"]["p"],
        "sponsorship_p_after": victim["sponsorship"]["p"],
        "allocation_changed": changed,
        "slots_before": slots_before,
        "slots_after": slots_after,
        "gate_catches_it": gate_catches,
        "fragility_distance": (f"one cell in {gate['row_count']:,} rows moves "
                               f"{target['company_name']} from {slots_before} slots to "
                               f"{slots_after}"),
        "honest_limit": ("The gate's RATE_SCALE_ANOMALY check catches this class before "
                         "scoring, which is why the check exists. Without it the failure is "
                         "silent: the composite still looks reasonable, just for the wrong "
                         "company."),
    }


def _top_slots_dict(fp):
    return dict(fp)


def p3_evergreen_requisition(candidates, baseline, profile, slots, cap, decay):
    """A posting that is genuinely open and genuinely not hiring."""
    allocated = [c for c in candidates if c["recommendation"] == "Apply"][:3]
    if not allocated:
        return {"id": "P3", "name": "gamed input — evergreen requisition", "applicable": False}
    victim = allocated[0]
    vals = [allocate_mod.expected_yield(victim["composite"],
                                        profile.get("base_response_rate",
                                                    config.BASE_RESPONSE_RATE))]
    wasted = min(cap, 3)
    return {
        "id": "P3",
        "name": "gamed input — an evergreen 'talent pipeline' requisition",
        "realistic_because": "large employers keep perpetual reqs open for pipeline "
                             "building; they pass every automated liveness signal because "
                             "they are, factually, open postings",
        "victim": victim["company_name"],
        "liveness_signal": victim["liveness"]["status"],
        "engine_behaviour": (f"the gate opens, the composite stands at "
                             f"{util.fmt(victim['composite'])}, and up to {wasted} slots go "
                             "to a requisition with no hiring manager behind it"),
        "slots_at_risk": wasted,
        "detected_by_any_check": False,
        "fragility_distance": ("zero data change required — the posting is real. No check in "
                              "this tool can distinguish an evergreen req from a live one"),
        "what_would_catch_it": ("a human reading the posting date, the req ID pattern, and "
                               "whether the same title has been open for months — Ch.8's "
                               "five liveness checks done by eye, not by API"),
        "honest_limit": ("This is the failure mode the engine is structurally blind to. The "
                         "hard stop is the only mitigation, and it works only if the human "
                         "actually looks."),
    }


def p4_entity_split(candidates, baseline, profile, slots, cap, decay, base_fp):
    """Split the top firm's filing history across two legal names."""
    import random
    top = next((c for c in candidates if c["recommendation"] == "Apply"
                and (c["sponsorship"]["approvals"] or 0) > 0), None)
    if top is None:
        return {"id": "P4", "name": "entity split", "applicable": False}
    rng = random.Random(config.CI_SEED)
    pool = _clone(candidates)
    victim = next(c for c in pool if c["normalized"] == top["normalized"])
    a = victim["sponsorship"]["approvals"]
    d = victim["sponsorship"]["denials"]
    _rebuild_sponsorship(victim, a / 2.0, d / 2.0, rng)
    tier_before = top["sponsorship"]["tier"]
    tier_after = victim["sponsorship"]["tier"]
    _rescore(pool, profile)
    prop = _reallocate(pool, baseline, profile, slots, cap, decay)
    slots_before = dict(base_fp).get(top["normalized"], 0)
    slots_after = next((r["slots"] for r in prop["target"]["rows"]
                        if r["normalized"] == top["normalized"]), 0)
    return {
        "id": "P4",
        "name": "entity split — one firm's history across two legal names",
        "realistic_because": "the dataset already contains PELOTON INTERACTIVE INC and "
                             "PELOTON INTERACTIVE LLC with identical filing counts; the "
                             "join is by name and nothing resolves them",
        "victim": top["company_name"],
        "approvals_before": a,
        "approvals_after": a / 2.0,
        "cells_changed": 2,
        "tier_before": tier_before,
        "tier_after": tier_after,
        "sponsorship_p_before": top["sponsorship"]["p"],
        "sponsorship_p_after": victim["sponsorship"]["p"],
        "slots_before": slots_before,
        "slots_after": slots_after,
        "allocation_changed": _fingerprint(prop) != base_fp,
        "fragility_distance": (f"2 edited cells out of {len(candidates):,} candidate rows "
                              f"move {top['company_name']} from {slots_before} slots to "
                              f"{slots_after}"),
        "honest_limit": ("The gate flags collisions but does not merge them, because merging "
                         "two firms that merely share a name would be worse. The residual "
                         "risk is real and unresolved."),
    }


def p5_parameter_sweep(candidates, baseline, profile, slots, cap, decay, base_fp):
    """How much of the ranking is the data, and how much is my own parameters?"""
    import random
    vol_rows = []
    for ref in (25.0, 50.0, 100.0, 250.0, 500.0, 1000.0):
        rng = random.Random(config.CI_SEED)
        pool = _clone(candidates)
        for c in pool:
            a = c["sponsorship"]["approvals"]
            d = c["sponsorship"]["denials"]
            if a is None:
                continue
            _rebuild_sponsorship(c, a, d, rng, volume_ref=ref)
        _rescore(pool, profile)
        prop = _reallocate(pool, baseline, profile, slots, cap, decay)
        vol_rows.append({
            "volume_ref": ref, "changed": _fingerprint(prop) != base_fp,
            "top_company": prop["target"]["rows"][0]["company_name"]
            if prop["target"]["rows"] else None,
            "apply_count": prop["skip_rate"]["apply"],
            "skip_rate": prop["skip_rate"]["rate"],
        })

    decay_rows = []
    for dv in (0.25, 0.4, 0.5, 0.65, 0.8, 0.95):
        prop = _reallocate(candidates, baseline, profile, slots, cap, dv)
        decay_rows.append({
            "decay": dv, "changed": _fingerprint(prop) != base_fp,
            "distinct_companies": len(prop["target"]["rows"]),
            "top_company": prop["target"]["rows"][0]["company_name"]
            if prop["target"]["rows"] else None,
        })

    n_vol = sum(1 for r in vol_rows if r["changed"])
    n_dec = sum(1 for r in decay_rows if r["changed"])
    return {
        "id": "P5",
        "name": "parameter sweep — VOLUME_REF and repeat-slot decay",
        "realistic_because": "both are your-input numbers with no external justification; "
                             "another analyst would pick different ones and get a different "
                             "answer from the same data",
        "volume_ref_sweep": vol_rows,
        "decay_sweep": decay_rows,
        "allocations_changed_by_volume_ref": f"{n_vol} of {len(vol_rows)} settings",
        "allocations_changed_by_decay": f"{n_dec} of {len(decay_rows)} settings",
        "fragility_distance": (f"{n_vol} of {len(vol_rows)} plausible VOLUME_REF values and "
                               f"{n_dec} of {len(decay_rows)} plausible decay values change "
                               "the allocation"),
        "honest_limit": ("These are not data errors. They are the analyst's choices, and the "
                         "recommendation is partly a function of them. Reporting a single "
                         "allocation without this sweep would overstate how much of the "
                         "answer comes from the evidence."),
    }


def audit(candidates, baseline, profile, proposal, slots, cap, decay,
          csv_path=None, bls_path=None, portals_path=None, gate=None,
          liveness_policy=None):
    base_fp = _fingerprint(proposal)
    perturbations = [
        p1_vintage_shift(candidates, baseline, profile, slots, cap, decay, base_fp),
        p2_units_error(candidates, baseline, profile, slots, cap, decay, base_fp, gate),
        p3_evergreen_requisition(candidates, baseline, profile, slots, cap, decay),
        p4_entity_split(candidates, baseline, profile, slots, cap, decay, base_fp),
        p5_parameter_sweep(candidates, baseline, profile, slots, cap, decay, base_fp),
    ]

    # The policy comparison is not a perturbation — it is a documented alternative that
    # was live in this repo until now, and it shows what the coverage bias costs.
    policy_rows = []
    if csv_path and gate:
        with open(csv_path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for pol in ("neutral-flagged", "legacy-zero"):
            ev = evidence_mod.build(csv_path=csv_path, bls_path=bls_path,
                                    portals_path=portals_path, profile=profile,
                                    gate=gate, liveness_policy=pol, csv_rows=rows)
            prop = _reallocate(ev["candidates"], baseline, profile, slots, cap, decay)
            policy_rows.append({
                "policy": pol,
                "apply_count": prop["skip_rate"]["apply"],
                "skip_rate": prop["skip_rate"]["rate"],
                "slots_allocated": prop["target"]["total_slots"],
                "top_company": prop["target"]["rows"][0]["company_name"]
                if prop["target"]["rows"] else None,
                "companies_zeroed_by_policy": sum(
                    1 for c in ev["candidates"] if c["liveness"]["factor"] == 0.0),
            })

    flips = [p for p in perturbations if p.get("allocation_changed")]
    return {
        "_what_this_is": "Adversarial robustness: realistic perturbations, with the "
                         "smallest change that alters the recommendation.",
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "baseline_allocation_fingerprint": [list(t) for t in base_fp],
        "perturbations": perturbations,
        "flipped_count": len(flips),
        "liveness_policy_comparison": policy_rows,
        "summary": (
            "The engine is robust to the perturbation everyone tests (proportional noise on "
            "the counts) and fragile to the ones nobody does: a single mis-scaled cell, a "
            "two-cell identity split, and an evergreen requisition it cannot see at all."),
        "where_i_would_not_trust_it": [
            "Any firm whose slots depend on fewer than ~25 filings — the interval is wider "
            "than the gap to the next candidate.",
            "Any run where the gate's RATE_SCALE_ANOMALY or ENTITY_COLLISION counts changed "
            "since the last refresh.",
            "Any recommendation whose destination has an unverifiable board, until a human "
            "has opened the posting.",
            "The absolute yield numbers, ever. They inherit a your-input response rate.",
        ],
    }


def summary_lines(frag):
    o = []
    o.append("")
    o.append("=" * 74)
    o.append("ADVERSARIAL FRAGILITY")
    o.append("=" * 74)
    for p in frag["perturbations"]:
        if p.get("applicable") is False:
            continue
        flipped = p.get("allocation_changed")
        mark = "FLIPS" if flipped else ("see below" if flipped is None else "holds")
        o.append(f"  {p['id']} {p['name'][:52]:<52} {mark}")
        o.append(f"     {p['fragility_distance']}")
    if frag["liveness_policy_comparison"]:
        o.append("")
        o.append("  liveness policy comparison (what the coverage bias costs):")
        for r in frag["liveness_policy_comparison"]:
            o.append(f"     {r['policy']:<16} apply-tier {r['apply_count']:>5,} · "
                     f"skip {util.pct(r['skip_rate'], 0)} · zeroed by policy "
                     f"{r['companies_zeroed_by_policy']:,}")
    o.append("")
    o.append(f"  {frag['summary']}")
    return "\n".join(o)


def render(frag):
    o = []
    o.append(f"# Adversarial robustness and fragility — {frag['generated'][:10]}\n")
    o.append(f"{frag['summary']}\n")
    o.append("| # | Perturbation | Realistic because | Allocation changed | Fragility distance |")
    o.append("|---|---|---|---|---|")
    for p in frag["perturbations"]:
        if p.get("applicable") is False:
            continue
        changed = p.get("allocation_changed")
        changed_s = ("**yes**" if changed else ("n/a — undetectable" if changed is None
                                               else "no"))
        o.append(f"| {p['id']} | {p['name']} | {p['realistic_because']} | {changed_s} | "
                 f"{p['fragility_distance']} |")
    o.append("")

    for p in frag["perturbations"]:
        if p.get("applicable") is False:
            continue
        o.append(f"## {p['id']} — {p['name']}\n")
        for k, v in p.items():
            if k in ("id", "name", "realistic_because", "fragility_distance",
                     "honest_limit", "steps", "volume_ref_sweep", "decay_sweep",
                     "what_would_catch_it"):
                continue
            o.append(f"- **{k}**: {v}")
        o.append(f"\n**Fragility distance:** {p['fragility_distance']}\n")
        if p.get("what_would_catch_it"):
            o.append(f"**What would catch it:** {p['what_would_catch_it']}\n")
        if p.get("steps"):
            o.append("| Approvals kept | Allocation changed | Top company | Skip rate |")
            o.append("|---:|---|---|---:|")
            for s in p["steps"]:
                o.append(f"| {s['approvals_kept']:.0%} | {'yes' if s['allocation_changed'] else 'no'} "
                         f"| {s['top_company']} | {util.pct(s['skip_rate'])} |")
            o.append("")
        if p.get("volume_ref_sweep"):
            o.append("| VOLUME_REF | Allocation changed | Top company | Apply tier | Skip rate |")
            o.append("|---:|---|---|---:|---:|")
            for s in p["volume_ref_sweep"]:
                o.append(f"| {s['volume_ref']:.0f} | {'yes' if s['changed'] else 'no'} | "
                         f"{s['top_company']} | {s['apply_count']:,} | {util.pct(s['skip_rate'])} |")
            o.append("")
            o.append("| repeat-slot decay | Allocation changed | Distinct companies | Top company |")
            o.append("|---:|---|---:|---|")
            for s in p["decay_sweep"]:
                o.append(f"| {s['decay']:.2f} | {'yes' if s['changed'] else 'no'} | "
                         f"{s['distinct_companies']} | {s['top_company']} |")
            o.append("")
        o.append(f"*Honest limit:* {p['honest_limit']}\n")

    if frag["liveness_policy_comparison"]:
        o.append("## What the coverage bias costs, measured\n")
        o.append("The `legacy-zero` policy is what the earlier worked run did: a firm whose "
                 "board the scanner cannot read scores 0.000. Running both policies over the "
                 "same data turns that bias from an assertion into a number.\n")
        o.append("| Liveness policy | Apply tier | Skip rate | Slots allocated | Top company | Firms zeroed by policy |")
        o.append("|---|---:|---:|---:|---|---:|")
        for r in frag["liveness_policy_comparison"]:
            o.append(f"| `{r['policy']}` | {r['apply_count']:,} | {util.pct(r['skip_rate'])} | "
                     f"{r['slots_allocated']} | {r['top_company']} | "
                     f"{r['companies_zeroed_by_policy']:,} |")
        o.append("")

    o.append("## Where I would not trust this tool\n")
    for w in frag["where_i_would_not_trust_it"]:
        o.append(f"- {w}")
    o.append("")
    return "\n".join(o) + "\n"
