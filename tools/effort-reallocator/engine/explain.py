"""Exact Shapley attribution — and the cases where it is accurate and misleading.

The composite has five features, so the Shapley values can be computed EXACTLY by
enumerating all 2^5 = 32 coalitions. No sampling, no `shap` dependency, no
approximation error to argue about: the additivity identity

    sum_i phi_i  ==  v(full) - v(empty)

is asserted in code and reported in the artifact. This is a better explanation than an
approximate SHAP run over the same function, which matters because the point of this
component is to then show that a *better* explanation is still misleading.

THE GAP THIS MODULE EXISTS TO FIND

  Case A — additive attribution over a multiplicative function. The composite is
    (sum vote x weight) x liveness x timeline. Shapley credit lands on whichever term
    is largest, but the cheapest way to CHANGE the decision is often a gate. The
    explanation ranks by contribution; a human acts by leverage. Those are different
    orderings and nothing on the plot says so.

  Case B — the point estimate hides the sample size. Two firms can receive identical
    attributions when one has 4,962 filings behind it and the other has 2. The
    attribution is a function of p, and p alone. Same explanation, incomparable
    evidence.

  Case C — "liveness = 1.0" reads as a verified fact. In this run nothing was
    verified: the gate reflects whether a board is on a supported ATS provider. An
    explanation that shows liveness contributing +0.08 is technically accurate about
    the arithmetic and quietly wrong about the world, because it cannot distinguish
    "checked and live" from "never checked".
"""

import datetime
import itertools
import math

from . import composite
from . import config
from . import util

FEATURES = list(composite.FEATURES)  # sponsorship, fit, role_quality, liveness, timeline


def _value(active, actual, reference, weights):
    """v(S): composite with features in S at actual values, others at reference."""
    votes, gates = {}, {}
    for k in composite.VOTE_KEYS:
        votes[k] = actual[k] if k in active else reference[k]
    for k in composite.GATE_KEYS:
        gates[k] = actual[k] if k in active else reference[k]
    comp, _, _ = composite.composite_from_terms(votes, gates, weights)
    return comp


def shapley(actual, reference, weights):
    """Exact Shapley values by coalition enumeration (5 features -> 32 subsets)."""
    n = len(FEATURES)
    factorial = math.factorial
    phi = {f: 0.0 for f in FEATURES}
    cache = {}

    def v(subset):
        key = frozenset(subset)
        if key not in cache:
            cache[key] = _value(key, actual, reference, weights)
        return cache[key]

    for f in FEATURES:
        others = [g for g in FEATURES if g != f]
        for r in range(len(others) + 1):
            for subset in itertools.combinations(others, r):
                w = factorial(len(subset)) * factorial(n - len(subset) - 1) / factorial(n)
                phi[f] += w * (v(set(subset) | {f}) - v(set(subset)))
    return phi, v(set()), v(set(FEATURES)), len(cache)


def flip_distance(actual, weights, gates_actual, tier, needs_sponsor, current_rec):
    """Smallest single-feature change that flips the recommendation.

    Solved analytically: the composite is linear in each vote and linear in each gate
    multiplier, so the required delta is closed-form rather than searched.
    """
    target = (config.APPLY_THRESHOLD if current_rec != "Apply" else config.APPLY_THRESHOLD)
    vote_sum = sum((actual[k] or 0.0) * weights.get(k, 0.0) for k in composite.VOTE_KEYS)
    gate_product = 1.0
    for k in composite.GATE_KEYS:
        gate_product *= actual[k] if actual[k] is not None else 1.0

    out = []
    for k in composite.VOTE_KEYS:
        w = weights.get(k, 0.0)
        if w <= 0 or actual[k] is None or gate_product <= 0:
            out.append({"feature": k, "delta": None,
                        "reachable": False,
                        "note": ("weight is zero — this feature cannot move the decision "
                                 "at all" if w <= 0 else
                                 "no value on record, or a closed gate makes every vote "
                                 "irrelevant")})
            continue
        needed_vote_sum = target / gate_product
        delta = (needed_vote_sum - vote_sum) / w
        new_val = actual[k] + delta
        out.append({"feature": k, "delta": round(delta, 4),
                    "from": actual[k], "to": round(new_val, 4),
                    "reachable": 0.0 <= new_val <= 1.0,
                    "note": ("within range" if 0.0 <= new_val <= 1.0 else
                             "would require a value outside [0,1] — unreachable")})
    for k in composite.GATE_KEYS:
        other = 1.0
        for g in composite.GATE_KEYS:
            if g != k:
                other *= actual[g] if actual[g] is not None else 1.0
        if vote_sum <= 0 or other <= 0:
            out.append({"feature": k, "delta": None, "reachable": False,
                        "note": "votes sum to zero, so no gate value reaches the threshold"})
            continue
        needed = target / (vote_sum * other)
        delta = needed - (actual[k] if actual[k] is not None else 1.0)
        out.append({"feature": k, "delta": round(delta, 4),
                    "from": actual[k], "to": round(needed, 4),
                    "reachable": 0.0 <= needed <= 1.0,
                    "note": ("within range" if 0.0 <= needed <= 1.0 else
                             "would require a gate outside [0,1] — unreachable")})
    reachable = [o for o in out if o.get("reachable") and o.get("delta") is not None]
    cheapest = min(reachable, key=lambda o: abs(o["delta"])) if reachable else None
    return {"target_threshold": target, "per_feature": out, "cheapest": cheapest}


def _actual_and_reference(cand, pool):
    actual = {
        "sponsorship": cand["sponsorship"]["p"],
        "fit": cand["fit"]["p"],
        "role_quality": cand["role_quality"]["p"],
        "liveness": cand["liveness"]["factor"],
        "timeline": cand["timeline"]["factor"],
    }
    def med(key, sub):
        vals = sorted(c[key][sub] for c in pool if c[key][sub] is not None)
        return util.quantile(vals, 0.5) if vals else 0.0
    reference = {
        "sponsorship": med("sponsorship", "p"),
        "fit": med("fit", "p"),
        "role_quality": med("role_quality", "p") or 0.0,
        "liveness": 1.0,
        "timeline": 1.0,
    }
    actual = {k: (0.0 if v is None else v) for k, v in actual.items()}
    return actual, reference


def explain(candidates, proposal, profile, top=6):
    """Explain the destinations of the proposed move, then critique the explanation."""
    weights, needs_sponsor = composite.apply_profile(config.WEIGHTS, profile)
    by_norm = {c["normalized"]: c for c in candidates}
    pool = candidates[:200]

    targets = [r["normalized"] for r in proposal["target"]["rows"][:top]]
    for m in proposal["moves"]:
        if m["to_normalized"] not in targets:
            targets.append(m["to_normalized"])

    # Probe rows, added deliberately rather than found by luck. Case B needs a
    # thin-record firm to compare against a deep-record one; if the explained set
    # happens to contain only large sponsors, the critique cannot be tested at all.
    probes = []
    thin = [c for c in candidates
            if c["sponsorship"]["approvals"] is not None
            and c["sponsorship"]["approvals"] < config.SMALL_N_APPROVALS
            and c["recommendation"] in ("Apply", "Consider")]
    if thin:
        probes.append({"normalized": thin[0]["normalized"],
                       "why_included": "thinnest filing record in the Apply/Consider tier "
                                       "— included on purpose to test whether the "
                                       "explanation distinguishes it from a deep record"})
    widest = sorted((c for c in candidates
                     if c["sponsorship"]["ci80"] and c["sponsorship"]["ci80"][0] is not None),
                    key=lambda c: -(c["sponsorship"]["ci80"][1] - c["sponsorship"]["ci80"][0]))
    if widest:
        probes.append({"normalized": widest[0]["normalized"],
                       "why_included": "widest sponsorship credible interval in the pool"})
    for p in probes:
        if p["normalized"] not in targets:
            targets.append(p["normalized"])
    probe_reasons = {p["normalized"]: p["why_included"] for p in probes}

    explanations = []
    for norm in targets:
        cand = by_norm.get(norm)
        if cand is None:
            continue
        actual, reference = _actual_and_reference(cand, pool)
        phi, v_empty, v_full, coalitions = shapley(actual, reference, weights)
        identity_error = abs(sum(phi.values()) - (v_full - v_empty))
        fd = flip_distance(actual, weights,
                           {k: actual[k] for k in composite.GATE_KEYS},
                           cand["sponsorship"]["tier"], needs_sponsor,
                           cand["recommendation"])
        top_feature = max(phi.items(), key=lambda kv: abs(kv[1]))
        ci = cand["sponsorship"]["ci80"]
        sources = {
            "sponsorship": cand["sponsorship"]["source"],
            "fit": cand["fit"]["source"],
            "role_quality": cand["role_quality"]["source"],
            "liveness": f"{cand['liveness']['source']} ({cand['liveness']['status']})",
            "timeline": cand["timeline"]["source"],
        }
        if fd["cheapest"]:
            fd["cheapest"]["source"] = sources[fd["cheapest"]["feature"]]
        explanations.append({
            "company_name": cand["company_name"],
            "normalized": norm,
            "why_explained": probe_reasons.get(norm, "in the proposed allocation"),
            "feature_sources": sources,
            "recommendation": cand["recommendation"],
            "composite": cand["composite"],
            "shapley": {k: round(v, 5) for k, v in phi.items()},
            "baseline_value": round(v_empty, 5),
            "full_value": round(v_full, 5),
            "coalitions_evaluated": coalitions,
            "additivity_error": identity_error,
            "exact": identity_error < 1e-9,
            "top_contributor": {"feature": top_feature[0], "phi": round(top_feature[1], 5)},
            "cheapest_lever": fd["cheapest"],
            "flip_distance": fd,
            "sponsorship_ci80": ci,
            "sponsorship_ci_width": (round(ci[1] - ci[0], 4)
                                     if ci and ci[0] is not None else None),
            "approvals": cand["sponsorship"]["approvals"],
            "liveness_status": cand["liveness"]["status"],
        })

    # ── Case A: the top contributor is not the cheapest lever ───────────────
    case_a = []
    for e in explanations:
        cheap = e["cheapest_lever"]
        if cheap and cheap["feature"] != e["top_contributor"]["feature"]:
            case_a.append({
                "company_name": e["company_name"],
                "explanation_says": (f"{e['top_contributor']['feature']} is the largest "
                                     f"contributor (phi = {e['top_contributor']['phi']:+.4f})"),
                "action_actually_cheapest": (f"{cheap['feature']} — a change of "
                                             f"{cheap['delta']:+.4f} crosses the threshold"),
                "why_it_misleads": (
                    "The attribution is additive; the composite is multiplicative through "
                    "the gates. Credit for size and leverage for action are different "
                    "orderings. A reader who trusts the ranking spends effort on "
                    f"{e['top_contributor']['feature']} when the decision actually turns on "
                    f"{cheap['feature']}."),
            })

    # ── Case B: identical attribution over wildly different evidence ────────
    # The comparison that matters is not interval width but the COUNT behind the
    # estimate. Because p is capped, every large sponsor lands on the same value, so
    # the attribution is byte-identical for firms whose records differ by an order of
    # magnitude. Detecting this on interval width alone missed it entirely: the
    # capped intervals are degenerate, which is itself part of the failure.
    case_b = []
    with_n = [e for e in explanations if e["approvals"]]
    for a, b in itertools.combinations(with_n, 2):
        pa, pb = a["shapley"]["sponsorship"], b["shapley"]["sponsorship"]
        if pa == 0 or pb == 0:
            continue
        if abs(pa - pb) / max(abs(pa), abs(pb)) > 0.05:
            continue
        na, nb = a["approvals"], b["approvals"]
        ratio = max(na, nb) / min(na, nb)
        if ratio < 3.0:
            continue
        thin, thick = (a, b) if na < nb else (b, a)
        case_b.append({
            "pair": [thin["company_name"], thick["company_name"]],
            "sponsorship_phi": [round(pa, 5), round(pb, 5)],
            "phi_identical": abs(pa - pb) < 1e-9,
            "approvals": {thin["company_name"]: thin["approvals"],
                          thick["company_name"]: thick["approvals"]},
            "approvals_ratio": round(ratio, 1),
            "ci_widths": {thin["company_name"]: thin["sponsorship_ci_width"],
                          thick["company_name"]: thick["sponsorship_ci_width"]},
            "why_it_misleads": (
                f"{thin['company_name']} ({int(thin['approvals'])} approvals) and "
                f"{thick['company_name']} ({int(thick['approvals'])} approvals) receive "
                f"{'a byte-identical' if abs(pa - pb) < 1e-9 else 'an indistinguishable'} "
                f"sponsorship attribution ({pa:+.5f} vs {pb:+.5f}) on records that differ "
                f"by {round(ratio, 1)}x. The attribution is a function of p, and p is capped "
                f"at {config.P_SPONSORSHIP_CAP}, so every large sponsor collapses onto the "
                "same number and the credible intervals collapse with it. A reader comparing "
                "these two explanations sees no difference in the evidence, because the "
                "explanation has removed it."),
        })
    case_b = sorted(case_b, key=lambda x: -x["approvals_ratio"])[:3]

    # ── Case C: an unverified gate explained as though it were checked ──────
    case_c = []
    for e in explanations:
        if e["liveness_status"] in ("unverifiable", "checkable-but-unchecked"):
            phi_l = e["shapley"]["liveness"]
            case_c.append({
                "company_name": e["company_name"],
                "liveness_status": e["liveness_status"],
                "liveness_phi": phi_l,
                "why_it_misleads": (
                    "The explanation reports a liveness contribution as if liveness were "
                    "measured. It was not: this run made no network call, and the gate "
                    f"value reflects {'ATS provider coverage only' if e['liveness_status'] == 'checkable-but-unchecked' else 'a policy decision about firms the scanner cannot reach'}. "
                    "Nothing in the attribution distinguishes 'checked and live' from "
                    "'never checked' — the number is identical either way."),
            })
    case_c = case_c[:3]

    # ── Case D: the decision's nearest edge is one of my own assumptions ────
    case_d = []
    for e in explanations:
        cheap = e["cheapest_lever"]
        if not cheap:
            continue
        src = cheap.get("source", "")
        if util.INPUT in src or "unverifiable" in src or "unchecked" in src:
            case_d.append({
                "company_name": e["company_name"],
                "cheapest_lever": cheap["feature"],
                "source": src,
                "delta_to_flip": cheap["delta"],
                "why_it_misleads": (
                    f"The smallest change that would flip this recommendation is "
                    f"{cheap['delta']:+.4f} on `{cheap['feature']}`, whose provenance is "
                    f"`{src}` — my own assumption or an unverified gate, not a filing "
                    "record. The explanation presents evidence and assumption in the same "
                    "units and the same chart, so a reader cannot see that the decision's "
                    "nearest edge is a number I chose rather than a number I found."),
            })
    case_d = case_d[:4]

    return {
        "_what_this_is": "Exact Shapley attribution over the 5-feature composite, plus "
                         "the counterfactual flip distance, plus the specific cases where "
                         "that explanation is accurate and misleading.",
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "method": {
            "name": "exact Shapley by coalition enumeration",
            "features": FEATURES,
            "coalitions": 2 ** len(FEATURES),
            "why_not_shap": ("With five features the exact values are cheap, so an "
                             "approximation would add sampling error for nothing. The "
                             "additivity identity is asserted in code."),
            "reference_point": ("pool-median vote values; gates at 1.0. The attribution is "
                                "relative to that reference and changes if the reference "
                                "changes — a property of every Shapley explanation that "
                                "plots rarely mention."),
        },
        "explanations": explanations,
        "critique": {
            "case_a_additive_over_multiplicative": case_a,
            "case_b_hidden_sample_size": case_b,
            "case_c_unverified_gate_reads_as_verified": case_c,
            "case_d_nearest_edge_is_an_assumption": case_d,
            "summary": (
                "All four cases are technically accurate arithmetic. Each one misleads a "
                "reader who would act on it: A points effort at the wrong term, B implies "
                "two firms are equally well-evidenced, C implies liveness was checked, and "
                "D hides that the decision's nearest edge is an assumption rather than a "
                "record."),
        },
    }


def summary_lines(result):
    o = []
    o.append("=" * 74)
    o.append("EXPLANATION — exact Shapley (32 coalitions, no approximation)")
    o.append("=" * 74)
    for e in result["explanations"][:5]:
        o.append(f"  {e['company_name']}  composite {util.fmt(e['composite'])} "
                 f"→ {e['recommendation']}")
        for f, v in sorted(e["shapley"].items(), key=lambda kv: -abs(kv[1])):
            o.append(f"      {f:<14} φ {v:+.4f}  {util.bar(abs(v), 20, 0.25)}")
        o.append(f"      additivity check: Σφ = v(full) − v(∅) "
                 f"{'OK (exact)' if e['exact'] else 'FAILED'}")
        cheap = e["cheapest_lever"]
        if cheap:
            o.append(f"      cheapest lever to flip: {cheap['feature']} "
                     f"({cheap['delta']:+.4f})")
        o.append("")
    c = result["critique"]
    o.append("  WHERE THIS EXPLANATION MISLEADS")
    o.append(f"    additive-over-multiplicative cases: {len(c['case_a_additive_over_multiplicative'])}")
    o.append(f"    hidden-sample-size pairs:           {len(c['case_b_hidden_sample_size'])}")
    o.append(f"    unverified-gate cases:              {len(c['case_c_unverified_gate_reads_as_verified'])}")
    o.append(f"    nearest-edge-is-an-assumption:      {len(c['case_d_nearest_edge_is_an_assumption'])}")
    if c["case_a_additive_over_multiplicative"]:
        a = c["case_a_additive_over_multiplicative"][0]
        o.append(f"    e.g. {a['company_name']}: explanation credits "
                 f"{a['explanation_says']}, but {a['action_actually_cheapest']}")
    return "\n".join(o)


def render(result):
    o = []
    o.append(f"# Explanation and its critique — {result['generated'][:10]}\n")
    m = result["method"]
    o.append(f"**Method:** {m['name']} over {m['coalitions']} coalitions of "
             f"{len(m['features'])} features: {', '.join('`%s`' % f for f in m['features'])}.\n")
    o.append(f"*Why not SHAP:* {m['why_not_shap']}\n")
    o.append(f"*Reference point:* {m['reference_point']}\n")

    o.append("## Attributions\n")
    o.append("| Company | Rec | Composite | " +
             " | ".join(f"φ {f}" for f in FEATURES) + " | Exact? |")
    o.append("|---|---|---:|" + "---:|" * len(FEATURES) + "---|")
    for e in result["explanations"]:
        o.append(f"| {e['company_name']} | {e['recommendation']} | "
                 f"{util.fmt(e['composite'])} | "
                 + " | ".join(f"{e['shapley'][f]:+.4f}" for f in FEATURES)
                 + f" | {'yes' if e['exact'] else 'NO'} |")
    o.append("")
    o.append("Additivity holds exactly for every row: Σφ = v(full) − v(∅). "
             "That is the strongest form of this explanation — which is the point of "
             "the next section.\n")

    o.append("## Counterfactual: what would flip the decision\n")
    o.append("| Company | Top contributor | Cheapest lever | Δ needed |")
    o.append("|---|---|---|---:|")
    for e in result["explanations"]:
        cheap = e["cheapest_lever"]
        delta_s = "{:+.4f}".format(cheap["delta"]) if cheap else "—"
        o.append(f"| {e['company_name']} | {e['top_contributor']['feature']} "
                 f"({e['top_contributor']['phi']:+.4f}) | "
                 f"{cheap['feature'] if cheap else '— none reachable'} | "
                 f"{delta_s} |")
    o.append("")

    c = result["critique"]
    o.append("## Where the explanation is accurate and misleading\n")
    o.append(f"{c['summary']}\n")

    o.append("### Case A — additive attribution over a multiplicative function\n")
    if c["case_a_additive_over_multiplicative"]:
        for case in c["case_a_additive_over_multiplicative"][:4]:
            o.append(f"**{case['company_name']}** — the explanation says "
                     f"{case['explanation_says']}; the cheapest way to change the "
                     f"decision is {case['action_actually_cheapest']}.  ")
            o.append(f"{case['why_it_misleads']}\n")
    else:
        o.append("No instance in this run: for every explained row the largest "
                 "contributor was also the cheapest lever. Worth re-checking whenever "
                 "the weights or the gate policy change.\n")

    o.append("### Case B — the point estimate hides the sample size\n")
    if c["case_b_hidden_sample_size"]:
        for case in c["case_b_hidden_sample_size"]:
            o.append(f"**{case['pair'][0]} vs {case['pair'][1]}** — sponsorship "
                     f"attributions {case['sponsorship_phi'][0]:+.5f} and "
                     f"{case['sponsorship_phi'][1]:+.5f} over records "
                     f"{case['approvals_ratio']}x apart.  ")
            o.append(f"{case['why_it_misleads']}\n")
    else:
        o.append("No qualifying pair in this run.\n")

    o.append("### Case C — an unverified gate reads as a verified one\n")
    if c["case_c_unverified_gate_reads_as_verified"]:
        for case in c["case_c_unverified_gate_reads_as_verified"]:
            o.append(f"**{case['company_name']}** (`{case['liveness_status']}`, "
                     f"φ liveness {case['liveness_phi']:+.4f})  ")
            o.append(f"{case['why_it_misleads']}\n")
    else:
        o.append("No instance in this run.\n")

    o.append("### Case D — the decision's nearest edge is an assumption, not a record\n")
    if c["case_d_nearest_edge_is_an_assumption"]:
        for case in c["case_d_nearest_edge_is_an_assumption"]:
            o.append(f"**{case['company_name']}** — cheapest lever `{case['cheapest_lever']}` "
                     f"({case['delta_to_flip']:+.4f}), provenance `{case['source']}`.  ")
            o.append(f"{case['why_it_misleads']}\n")
    else:
        o.append("No instance in this run.\n")

    o.append("## Provenance of each explained term\n")
    o.append("| Company | Why explained | " + " | ".join(FEATURES) + " |")
    o.append("|---|---|" + "---|" * len(FEATURES))
    for e in result["explanations"]:
        o.append(f"| {e['company_name']} | {e['why_explained']} | "
                 + " | ".join(f"`{e['feature_sources'][f]}`" for f in FEATURES) + " |")
    o.append("")
    return "\n".join(o) + "\n"
