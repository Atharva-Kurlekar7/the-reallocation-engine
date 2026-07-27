"""Monte Carlo over the things this engine does not know.

A point recommendation on a dataset this thin would be a lie of precision. Three
distinct sources of uncertainty get sampled, and they are different in kind:

  1. SAMPLING uncertainty (the honest kind). Sponsorship p is drawn from
     Beta(approvals+1, denials+1) x volume factor. A firm with 2 approvals and a 100%
     stated rate moves all over the interval; a firm with 4,962 approvals barely
     moves. This is what keeps a two-filing company from outranking LinkedIn.

  2. SPECIFICATION uncertainty (the uncomfortable kind). The `role_quality` weight is
     not pinned by Chapter 11 — the repo's own defect list says so — so it is drawn
     from [0, 0.20] and the sponsorship/fit weights are renormalised to keep the total
     vote weight at Chapter 11's 0.65. If the recommendation depends on which number
     an unpinned parameter takes, that is a finding, not a nuisance.

  3. MISSINGNESS uncertainty (the kind that is really an assumption). Most rows
     carry no H-1B fields. Two scenarios are sampled 50/50 for those firms:
       MCAR  — missing at random: draw p from the distribution of firms that DO have
               records. Absence carries no information.
       MNAR  — missing not at random: draw p from a pessimistic Beta(1,4). Absence
               correlates with not sponsoring.
     These are not both true. The spread between them is the price of not knowing
     which, and it is reported rather than averaged away.

Fit also gets +/- jitter, because it is a judgment and judgments are not precise to
three decimals.

Output: an 80% interval on each move's quantity, a STABILITY figure (the share of
draws in which the move still points the same way), and an explicit verdict when a
move is not distinguishable from doing nothing.
"""

import datetime
import random

from . import allocate as allocate_mod
from . import composite
from . import config
from . import util


def _draw_sponsorship(cand, rng, observed_pool, scenario):
    """One draw of the sponsorship vote for one company."""
    s = cand["sponsorship"]
    if s["p"] is not None:
        p = rng.betavariate(s["alpha"], s["beta"]) * s["volume_factor"]
        return min(config.P_SPONSORSHIP_CAP, p)
    # No filing record. The engine's default is to withhold the vote entirely; the MC
    # asks what would happen under each of the two stories about why it is missing.
    if scenario == "MCAR":
        if not observed_pool:
            return None
        return rng.choice(observed_pool)
    return rng.betavariate(config.MNAR_ALPHA, config.MNAR_BETA) * 0.25


def analyze(candidates, baseline, profile, proposal, slots, cap, decay,
            draws=None, seed=None):
    """Re-run the allocation `draws` times under sampled parameters."""
    draws = draws or config.MC_DRAWS
    rng = random.Random(seed or config.MC_SEED)
    base_rate = profile.get("base_response_rate", config.BASE_RESPONSE_RATE)
    _, needs_sponsor = composite.apply_profile(config.WEIGHTS, profile)

    # Keep the MC over the plausible pool: everything currently allocated, everything
    # in the baseline, plus the top of the ranking that could displace them.
    pool_norms = {r["normalized"] for r in proposal["target"]["rows"]}
    pool_norms |= {r["normalized"] for r in proposal["baseline"]["rows"]}
    ranked = [c for c in candidates if c["normalized"] not in pool_norms]
    pool = ([c for c in candidates if c["normalized"] in pool_norms]
            + ranked[:max(0, config.CANDIDATE_POOL_CAP - len(pool_norms))])

    observed_pool = [c["sponsorship"]["p"] for c in candidates
                     if c["sponsorship"]["p"] is not None]

    base_alloc = {}
    for row in baseline.get("allocations", []):
        n = util.normalize_company(row.get("company_name", ""))
        base_alloc[n] = base_alloc.get(n, 0) + int(row.get("slots", 0))

    move_keys = [(m["from_normalized"], m["to_normalized"], m["quantity"])
                 for m in proposal["moves"]]
    fixed_alloc = {r["normalized"]: r["slots"] for r in proposal["target"]["rows"]}
    slot_draws = {c["normalized"]: [] for c in pool}
    for n in base_alloc:
        slot_draws.setdefault(n, [])
    gain_draws = []
    reopt_gain_draws = []
    move_q_draws = {(f, t): [] for f, t, _ in move_keys}
    scenario_counts = {"MCAR": 0, "MNAR": 0}
    rq_weights = []

    for _ in range(draws):
        scenario = "MCAR" if rng.random() < 0.5 else "MNAR"
        scenario_counts[scenario] += 1
        w_rq = rng.uniform(0.0, config.ROLE_QUALITY_WEIGHT_MAX)
        rq_weights.append(w_rq)
        # Renormalise so total vote weight stays at Ch.11's 0.65.
        total = config.WEIGHTS["sponsorship"] + config.WEIGHTS["fit"]
        scale = (total - w_rq) / total if total > 0 else 1.0
        weights = {
            "sponsorship": config.WEIGHTS["sponsorship"] * scale,
            "fit": config.WEIGHTS["fit"] * scale,
            "role_quality": w_rq,
        }
        if not needs_sponsor:
            weights["sponsorship"] = 0.0

        drawn = []
        for c in pool:
            p_s = _draw_sponsorship(c, rng, observed_pool, scenario)
            p_f = c["fit"]["p"]
            if p_f is not None:
                p_f = max(0.0, min(1.0, p_f + rng.uniform(-config.FIT_JITTER,
                                                          config.FIT_JITTER)))
            votes = {"sponsorship": p_s, "fit": p_f,
                     "role_quality": c["role_quality"]["p"]}
            gates = {"liveness": c["liveness"]["factor"],
                     "timeline": c["timeline"]["factor"]}
            comp, _, _ = composite.composite_from_terms(votes, gates, weights)
            rec, _ = composite.classify(comp, gates, c["sponsorship"]["tier"],
                                        needs_sponsor)
            drawn.append({"normalized": c["normalized"], "composite": comp,
                          "recommendation": rec})

        alloc, _, _ = allocate_mod.allocate_slots(drawn, slots, cap, decay, base_rate)
        by_norm = {d["normalized"]: d for d in drawn}
        for norm in slot_draws:
            slot_draws[norm].append(alloc.get(norm, 0))

        def yield_of(allocation):
            total = 0.0
            for norm, n in allocation.items():
                d = by_norm.get(norm)
                if d is None:
                    continue  # not in the evidence set: contributes nothing either way
                v0 = allocate_mod.expected_yield(d["composite"], base_rate)
                total += sum(v0 * (decay ** k) for k in range(n))
            return total

        base_yield = yield_of(base_alloc)
        # The decision-relevant quantity: how the allocation ACTUALLY RECOMMENDED
        # performs under this draw. Re-optimising per draw instead would report the
        # gain of a plan that adapts to noise nobody can see — the optimizer's curse.
        gain_draws.append(yield_of(fixed_alloc) - base_yield)
        reopt_gain_draws.append(yield_of(alloc) - base_yield)

        for f, t, _q in move_keys:
            lost = max(0, base_alloc.get(f, 0) - alloc.get(f, 0))
            gained = max(0, alloc.get(t, 0) - base_alloc.get(t, 0))
            move_q_draws[(f, t)].append(min(lost, gained))

    def interval(vals):
        s = sorted(vals)
        return [util.quantile(s, config.CI_LOW_Q), util.quantile(s, config.CI_HIGH_Q)]

    moves_out = []
    for m in proposal["moves"]:
        key = (m["from_normalized"], m["to_normalized"])
        qs = move_q_draws.get(key, [])
        stability = (sum(1 for q in qs if q > 0) / len(qs)) if qs else 0.0
        lo, hi = interval(qs) if qs else (None, None)
        # Strict comparison: round(0.6995, 3) == 0.700 would wrongly clear a 70% floor.
        # Display prints two decimals so a sub-floor move never looks like 70.0%.
        stable = stability >= config.MOVE_STABILITY_FLOOR
        moves_out.append({
            "from_normalized": key[0], "to_normalized": key[1],
            "from": m["from"], "to": m["to"],
            "quantity": m["quantity"],
            "quantity_ci80": [lo, hi],
            "quantity_median": util.quantile(sorted(qs), 0.5) if qs else None,
            "stability": round(stability, 4),
            "verdict": ("directional — the move survives resampling"
                        if stable else
                        "NOT distinguishable from no change — the move appears in only "
                        f"{util.pct(stability, places=2)} of draws, below the "
                        f"{util.pct(config.MOVE_STABILITY_FLOOR, places=2)} floor. Treat as "
                        "'no evidence to move', not 'evidence to move a little'."),
            "stable": stable,
        })

    gain_lo, gain_hi = interval(gain_draws)
    p_pos = sum(1 for g in gain_draws if g > 0) / len(gain_draws)
    straddles = gain_lo is not None and gain_hi is not None and gain_lo <= 0 <= gain_hi
    gain_verdict = (
        f"The 80% interval [{gain_lo:+.3f}, {gain_hi:+.3f}] straddles zero: on this "
        "evidence the proposal cannot be distinguished from leaving the allocation "
        "alone." if straddles else
        f"The gain is positive in {util.pct(p_pos)} of draws and the 80% interval "
        f"[{gain_lo:+.3f}, {gain_hi:+.3f}] excludes zero — under the model's own "
        "assumptions. That is not the same as being right about the world."
    )
    mean_fixed = sum(gain_draws) / len(gain_draws)
    mean_reopt = sum(reopt_gain_draws) / len(reopt_gain_draws)
    optimism = mean_reopt - mean_fixed
    reopt_lo, reopt_hi = interval(reopt_gain_draws)

    slot_summary = []
    for norm, vals in slot_draws.items():
        if not any(vals) and not base_alloc.get(norm):
            continue
        s = sorted(vals)
        slot_summary.append({
            "normalized": norm,
            "baseline_slots": base_alloc.get(norm, 0),
            "proposed_slots": next((r["slots"] for r in proposal["target"]["rows"]
                                    if r["normalized"] == norm), 0),
            "ci80": [util.quantile(s, config.CI_LOW_Q), util.quantile(s, config.CI_HIGH_Q)],
            "median": util.quantile(s, 0.5),
            "p_gets_any": round(sum(1 for v in vals if v > 0) / len(vals), 4),
        })
    slot_summary.sort(key=lambda r: -(r["median"] or 0))

    return {
        "_what_this_is": "Monte Carlo over sampling, specification, and missingness "
                         "uncertainty. The interval is the product, not decoration.",
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "draws": draws,
        "seed": seed or config.MC_SEED,
        "pool_size": len(pool),
        "sources_of_uncertainty": [
            {"name": "sampling", "what": "Beta(approvals+1, denials+1) x volume factor",
             "kind": "record-level sampling error",
             "why": "a 100% rate over 2 filings and a 99% rate over 4,962 filings are "
                    "different facts"},
            {"name": "specification",
             "what": f"role_quality weight ~ U[0, {config.ROLE_QUALITY_WEIGHT_MAX}], "
                     "sponsorship/fit renormalised to keep total vote weight 0.65",
             "kind": "unpinned parameter [VERIFY]",
             "why": "Chapter 11 never pinned this weight; if the answer depends on it, "
                    "that is a finding"},
            {"name": "missingness",
             "what": f"MCAR (draw from observed) vs MNAR (Beta({config.MNAR_ALPHA},"
                     f"{config.MNAR_BETA}) x 0.25), sampled 50/50",
             "kind": "untestable assumption",
             "why": "most rows have no H-1B fields at all (see the gate's measured rate); "
                    "the two stories about why disagree and only one can be true"},
            {"name": "judgment", "what": f"fit +/- U[{-config.FIT_JITTER}, {config.FIT_JITTER}]",
             "kind": "model judgment", "why": "fit is a rubric output, not a measurement"},
        ],
        "scenario_counts": scenario_counts,
        "missingness_scenario_applied_to_candidates": sum(
            1 for c in pool if c["sponsorship"]["p"] is None),
        "missingness_finding": (
            "The MCAR/MNAR scenarios were applied to "
            f"{sum(1 for c in pool if c['sponsorship']['p'] is None)} of {len(pool)} pooled "
            "candidates. When that number is zero it is not a clean result — it means every "
            "firm in the pool already has a filing record, because the pool filter requires "
            "filed job titles. The 94.9% of the dataset with no H-1B fields is not being "
            "handled cautiously here; it is absent. See `evidence_meta.blind_spot`."),
        "role_quality_weight_mean": round(sum(rq_weights) / len(rq_weights), 4),
        "moves": moves_out,
        "expected_gain": {
            "point": proposal["expected_gain"]["point"],
            "ci80": [round(gain_lo, 5) if gain_lo is not None else None,
                     round(gain_hi, 5) if gain_hi is not None else None],
            "p_positive": round(p_pos, 4),
            "straddles_zero": straddles,
            "verdict": gain_verdict,
            "measured_on": ("the allocation actually recommended, held fixed across draws "
                            "— the decision-relevant quantity"),
            "point_outside_interval": (
                gain_lo is not None
                and not (gain_lo <= proposal["expected_gain"]["point"] <= gain_hi)),
            "point_vs_interval_note": (
                "The point estimate sits OUTSIDE its own interval, which looks like a bug "
                "and is a finding. The point estimate fixes the role_quality weight at "
                "Chapter 11's 0.0 — the value that makes the role-quality signal "
                f"irrelevant. The Monte Carlo draws it from U[0, {config.ROLE_QUALITY_WEIGHT_MAX}] "
                "because the book never pinned it, and the firms this engine allocates to "
                "tend to pay above the BLS median, so almost every draw with a non-zero "
                "weight scores them higher. The interval is therefore not centred on the "
                "point estimate: it is telling you that the recommendation's value depends "
                "on a parameter nobody has decided."
                if gain_lo is not None
                and not (gain_lo <= proposal["expected_gain"]["point"] <= gain_hi)
                else "The point estimate falls inside its interval, as expected."),
        },
        "optimizers_curse": {
            "what_it_is": (
                "If the allocation is re-optimised inside every Monte Carlo draw, it adapts "
                "to noise nobody can observe, and the reported gain flatters the method "
                "rather than describing the decision. Both quantities are computed here so "
                "the difference is visible instead of accidental."),
            "fixed_proposal_mean_gain": round(mean_fixed, 5),
            "reoptimised_mean_gain": round(mean_reopt, 5),
            "optimism": round(optimism, 5),
            "optimism_share_of_reported_gain": (round(optimism / mean_reopt, 4)
                                                if mean_reopt else None),
            "reoptimised_ci80": [round(reopt_lo, 5) if reopt_lo is not None else None,
                                 round(reopt_hi, 5) if reopt_hi is not None else None],
            "why_it_matters": (
                "The re-optimised figure is the one a naive Monte Carlo would print. Any "
                "gap between it and the fixed-proposal figure is gain that exists only "
                "because the optimiser was allowed to see the noise."),
        },
        "slot_stability": slot_summary[:30],
        "what_this_does_not_cover": [
            "Whether the composite's structure is right at all (Ch.11's weights are a "
            "design choice, not a fitted model).",
            "base_response_rate — a your-input scalar that multiplies every yield.",
            "Liveness: unverified in this run, so its uncertainty is not sampled. It is "
            "handled as a gate plus a human verification requirement instead.",
            "Anything causal. A tighter interval does not make the underlying claim "
            "interventional.",
        ],
    }
