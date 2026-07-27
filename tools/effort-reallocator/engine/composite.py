"""The Chapter 11 composite, reimplemented in Python and verified against the repo.

    Composite = ( sum_i vote_i * weight_i ) x liveness x timeline

Votes are graduated (sponsorship, fit, role quality). **Liveness and timeline are
gates — multipliers, not addends** (Ch.11, "Why liveness and timeline are multipliers,
not addends"), so a ghost posting or an impossible start date drives the composite to
zero no matter how strong the votes. Threshold near 0.3 maps to Apply / Consider / Skip.

This is a reimplementation of `scripts/score/role-scorer.mjs`, which is Node. Two
tests hold it honest, and they are the reason the reimplementation is defensible
rather than merely plausible:

  * parity against the committed output `data/examples/role-scores.json`, and
  * Chapter 11's worked example — Apply 0.4463 for the Cambridge biotech, Skip 0.1785
    for the identical candidate at a non-sponsor.

The multiplicative structure matters for a reason that resurfaces in the explanation
critique: an additive attribution over a multiplicative function tells you what
contributed, not what to do about it.
"""

from . import config
from . import util

VOTE_KEYS = ("sponsorship", "fit", "role_quality")
GATE_KEYS = ("liveness", "timeline")
FEATURES = VOTE_KEYS + GATE_KEYS


def apply_profile(weights, profile):
    """Weights are a function of the profile, not constants.

    If the candidate does not need sponsorship, the sponsorship term stops being a
    binding constraint and its weight goes to zero — a perfect-fit non-sponsor is no
    longer a skip. Mirrors applyProfile() in role-scorer.mjs.
    """
    w = dict(weights)
    needs = True
    if profile is not None:
        auth = str(profile.get("authorization", "")).lower()
        if profile.get("needs_sponsorship") is False:
            needs = False
        elif auth and any(k in auth for k in
                          ("citizen", "permanent resident", "green card", "gc",
                           "no sponsorship", "already authorized")):
            needs = False
    if not needs:
        w["sponsorship"] = 0.0
    return w, needs


def composite_from_terms(votes, gates, weights):
    """The arithmetic alone. Votes/gates are {key: value or None}."""
    vote_sum = 0.0
    for k in VOTE_KEYS:
        v = votes.get(k)
        if v is None:
            continue
        vote_sum += float(v) * float(weights.get(k, 0.0))
    gate_product = 1.0
    for k in GATE_KEYS:
        g = gates.get(k)
        gate_product *= 1.0 if g is None else float(g)
    return vote_sum * gate_product, vote_sum, gate_product


def classify(composite, gates, tier, needs_sponsor):
    """Apply / Consider / Skip, with the gate check first.

    A closed gate is not a low score. It is a different kind of answer: the question
    "is this worth applying to" does not arise if the posting is fiction.
    """
    closed = None
    for k in GATE_KEYS:
        g = gates.get(k)
        if g is not None and g <= config.GATE_ZERO:
            closed = (k, g)
            break
    if closed:
        return "Skip", (f"gated: {closed[0]} ≈ {util.fmt(closed[1])} (a closed gate "
                        f"zeroes the composite regardless of votes)")

    tier_l = str(tier or "").lower()
    if composite >= config.APPLY_THRESHOLD:
        soft_sponsor = needs_sponsor and tier_l in config.SOFT_SPONSORSHIP_TIERS
        timeline = gates.get("timeline")
        soft_timeline = timeline is not None and timeline < 0.6
        if soft_sponsor or soft_timeline:
            what = (f'sponsorship tier "{tier}"' if soft_sponsor
                    else f"timeline {util.fmt(timeline)}")
            return "Consider", (f"above threshold ({util.fmt(composite)}) but one soft "
                                f"spot: {what}")
        return "Apply", (f"composite {util.fmt(composite)} ≥ {config.APPLY_THRESHOLD}, "
                         f"gates healthy")
    if composite >= config.CONSIDER_FLOOR:
        return "Consider", (f"composite {util.fmt(composite)} in the Consider band "
                            f"[{config.CONSIDER_FLOOR}, {config.APPLY_THRESHOLD})")
    return "Skip", (f"composite {util.fmt(composite)} < {config.CONSIDER_FLOOR} — time "
                    f"is better spent elsewhere")


def score_role(role, weights=None, needs_sponsor=True):
    """Score one role-evidence record, emitting the full audit trace.

    Input shape is the same as `scripts/score/role-scorer.mjs` takes, so the parity
    test can feed both the same fixture.
    """
    weights = weights or config.WEIGHTS
    votes = {}
    trace_votes = []
    default_src = {"sponsorship": util.RECORD, "fit": util.MODEL,
                   "role_quality": util.RECORD}
    for k in VOTE_KEYS:
        obj = role.get(k) or {}
        p = obj.get("p")
        if not isinstance(p, (int, float)):
            continue
        votes[k] = float(p)
        w = float(weights.get(k, 0.0))
        trace_votes.append({
            "factor": k, "value": float(p), "weight": w,
            "contribution": round(float(p) * w, 4),
            "source": obj.get("source", default_src[k]),
        })

    gates = {}
    trace_gates = []
    default_gate_src = {"liveness": util.RECORD, "timeline": util.INPUT}
    for k in GATE_KEYS:
        obj = role.get(k) or {}
        f = obj.get("factor")
        val = float(f) if isinstance(f, (int, float)) else 1.0
        gates[k] = val
        trace_gates.append({"factor": k, "multiplier": val,
                            "source": obj.get("source", default_gate_src[k])})

    comp, vote_sum, gate_product = composite_from_terms(votes, gates, weights)
    tier = (role.get("sponsorship") or {}).get("tier")
    rec, reason = classify(comp, gates, tier, needs_sponsor)

    # A human override is allowed, but only with a documented reason. An override
    # without one is not judgment; it is ignoring the arithmetic (Ch.11).
    #
    # KNOWN DIVERGENCE from scripts/score/role-scorer.mjs: that implementation tests
    # the raw `override.reason` property in its ternary, so a whitespace-only reason
    # ("   ") is truthy in JS and the override is applied anyway — with a warning
    # attached that nothing acts on. This implementation honours the chapter instead:
    # a blank reason means the override is discarded. Logged as a defect in
    # logs/RUN_LOG.md; the parity fixture contains no whitespace-reason case, so
    # parity with the Node scorer is unaffected.
    overridden = None
    has_reason = False
    ov = role.get("override") or {}
    if ov.get("decision"):
        has_reason = bool(str(ov.get("reason") or "").strip())
        overridden = dict(ov)
        if not has_reason:
            overridden["_warning"] = ("override WITHOUT a documented reason — ignored "
                                      "(Ch.11: that is just ignoring the math)")

    arithmetic = (
        "(" + (" + ".join(f"{v['value']}·{v['weight']}" for v in trace_votes) or "0")
        + ") × " + " × ".join(str(g["multiplier"]) for g in trace_gates)
        + f" = {util.fmt(comp)}"
    )
    return {
        "role_id": role.get("role_id"),
        "company": role.get("company"),
        "title": role.get("title"),
        "composite": round(comp, 4),
        "composite_exact": comp,
        "recommendation": overridden["decision"] if has_reason else rec,
        "machine_recommendation": rec,
        "reason": reason,
        "override": overridden,
        "trace": {
            "votes": trace_votes,
            "vote_sum": round(vote_sum, 4),
            "gates": trace_gates,
            "gate_product": round(gate_product, 4),
            "arithmetic": arithmetic,
        },
    }


def score_candidate(cand, weights=None, needs_sponsor=True):
    """Score a candidate produced by evidence.build() (in place)."""
    scored = score_role(cand, weights=weights, needs_sponsor=needs_sponsor)
    cand["composite"] = scored["composite"]
    cand["recommendation"] = scored["recommendation"]
    cand["machine_recommendation"] = scored["machine_recommendation"]
    cand["reason"] = scored["reason"]
    cand["trace"] = scored["trace"]
    return cand
