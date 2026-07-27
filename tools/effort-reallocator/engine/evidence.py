"""Turn the SEC/DOL dataset into per-company evidence, with the uncertainty visible.

Four inputs to the Ch.11 composite are assembled here.

SPONSORSHIP (a record, then arithmetic over it). Two different quantities live in the
DOL columns and conflating them is the small-sample trap:

    P(approval | the firm filed)   <- the Approval_Rate column, Beta posterior
    does the firm sponsor at all   <- the approvals count, a volume factor

A firm with 2 approvals and 0 denials has a 100% approval rate. Reporting that as
"P(sponsorship) = 1.0" is how a tool ends up recommending a week of applications on
the strength of two filings, so the posterior mean is multiplied by a volume factor
and the 80% credible interval travels with the number everywhere it goes.

FIT (a model judgment). A deterministic rubric over the company's filed titles, not an
LLM call — reproducible, auditable, and still a judgment. Labelled as one.

ROLE QUALITY (a record where present). BLS/O*NET median wage for the target SOC codes
against the company's median sponsored salary. Its weight in the composite is 0.0 by
default because Chapter 11 never pinned one, which means this signal currently
contributes nothing. That is a real open question, not a settled design.

LIVENESS (a GATE — and the honest part is what was not checked). This tool makes no
network calls, so liveness is UNVERIFIED for every company. What differs is whether a
posting is even *checkable*: the repo's scanner supports greenhouse / lever / ashby.
Under the default `neutral-flagged` policy an uncheckable firm is still recommended,
flagged for human verification, and the hard stop refuses to execute it. Under
`legacy-zero` it scores 0.0 — which reproduces the earlier worked run where AMGEN INC
(1,882 approvals) was skipped purely because its board is Workday. That policy switch
is how the bias audit measures the harm instead of asserting it.
"""

import csv
import datetime
import random
import re

from . import composite
from . import config
from . import gigo
from . import util

_TOKEN_RE = re.compile(r"[a-z0-9+#]+")


def _tokens(text):
    return set(_TOKEN_RE.findall(str(text or "").lower()))


def load_portals(path):
    """Read the ATS portals config: which firms the scanner can even check.

    A tiny line-oriented parser rather than a YAML dependency — the tool must run
    from a clean clone. The file carries the dataset's own company spelling in a
    trailing comment (`# H-1B: MAPLEBEAR INC — 498 approvals`), which gives an exact
    join instead of a fuzzy one.
    """
    entries = []
    cur = None
    try:
        with open(path, encoding="utf-8") as fh:
            in_companies = False
            for raw in fh:
                line = raw.rstrip("\n")
                if re.match(r"^tracked_companies:", line):
                    in_companies = True
                    continue
                if not in_companies:
                    continue
                m = re.match(r"^\s*-\s*name:\s*(.+?)\s*$", line)
                if m:
                    cur = {"name": m.group(1), "enabled": False, "provider": None,
                           "csv_name": None}
                    entries.append(cur)
                    continue
                if cur is None:
                    continue
                m = re.match(r"^\s*enabled:\s*(true|false)\s*$", line, re.I)
                if m:
                    cur["enabled"] = m.group(1).lower() == "true"
                    continue
                m = re.match(r"^\s*provider:\s*(\S+)\s*$", line)
                if m:
                    cur["provider"] = m.group(1)
                    continue
                m = re.match(r"^\s*#\s*H-1B:\s*([A-Z0-9 .,&'\-]+?)\s+[—-]", line)
                if m:
                    cur["csv_name"] = m.group(1).strip()
    except FileNotFoundError:
        return {"entries": [], "by_norm": {}, "path": util.rel(path), "found": False}

    by_norm = {}
    for e in entries:
        for key in (e.get("csv_name"), e.get("name")):
            if key:
                by_norm.setdefault(util.normalize_company(key), e)
    return {"entries": entries, "by_norm": by_norm, "path": util.rel(path), "found": True}


def load_bls(path, soc_codes):
    """Median wage and cognitive-pivot score for the profile's target SOC codes."""
    wanted = set(soc_codes or [])
    rows = []
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("bls_soc_code") in wanted:
                    wage = util.to_float(r.get("annual_median_wage"))
                    cog = util.to_float(r.get("cognitive_pivot_score"))
                    rows.append({"soc": r.get("bls_soc_code"), "title": r.get("title"),
                                 "median_wage": wage, "cognitive_pivot_score": cog})
    except FileNotFoundError:
        return {"found": False, "rows": [], "median_wage": None,
                "cognitive_pivot_score": None, "path": util.rel(path)}
    wages = sorted(r["median_wage"] for r in rows if r["median_wage"] is not None)
    cogs = sorted(r["cognitive_pivot_score"] for r in rows
                  if r["cognitive_pivot_score"] is not None)
    return {
        "found": bool(rows),
        "rows": rows,
        "median_wage": util.quantile(wages, 0.5) if wages else None,
        "cognitive_pivot_score": util.quantile(cogs, 0.5) if cogs else None,
        "path": util.rel(path),
    }


def beta_interval(alpha, beta, rng):
    """80% credible interval for Beta(alpha, beta), by seeded sampling.

    Sampling rather than an incomplete-beta inverse keeps this dependency-free. The
    seed is fixed in config, so the interval is reproducible run to run.
    """
    draws = sorted(rng.betavariate(alpha, beta) for _ in range(config.CI_DRAWS))
    return (util.quantile(draws, config.CI_LOW_Q), util.quantile(draws, config.CI_HIGH_Q))


def volume_factor(approvals, volume_ref=None):
    """How much the *count* of filings supports "this firm sponsors people".

    log1p-saturating: 2 approvals is weak evidence of a sponsorship pathway even at a
    100% approval rate; 500 is strong. VOLUME_REF is a your-input parameter and the
    fragility pass sweeps it, because the ranking is sensitive to it.
    """
    ref = volume_ref if volume_ref is not None else config.VOLUME_REF
    import math
    if approvals is None or approvals <= 0:
        return 0.0
    return min(1.0, math.log1p(approvals) / math.log1p(ref))


def sponsorship_evidence(approvals, denials, rng, volume_ref=None):
    """The sponsorship vote, with its tier and its interval.

    Returns None-valued p when there is no filing record at all. That is the single
    most important line in this file: no record means `unknown`, not zero.
    """
    if approvals is None or denials is None:
        return {
            "p": None, "tier": "unknown", "source": util.RECORD,
            "approvals": None, "denials": None,
            "alpha": None, "beta": None, "ci80": [None, None],
            "volume_factor": 0.0,
            "note": "no H-1B filing matched — UNKNOWN, not zero. Absence of a filing "
                    "record is absence of evidence, and the engine will not spend a "
                    "slot on the strength of a blank cell.",
        }
    alpha = approvals + config.BETA_PRIOR_ALPHA
    beta = denials + config.BETA_PRIOR_BETA
    mean = alpha / (alpha + beta)
    vf = volume_factor(approvals, volume_ref)
    lo, hi = beta_interval(alpha, beta, rng)
    p = min(config.P_SPONSORSHIP_CAP, mean * vf)
    rate = 100.0 * approvals / (approvals + denials) if (approvals + denials) > 0 else None

    if approvals >= config.TIER_PROVEN_MIN_APPROVALS and (rate or 0) >= config.TIER_PROVEN_MIN_RATE:
        tier = "proven"
    elif approvals >= config.TIER_LIKELY_MIN_APPROVALS:
        tier = "likely"
    elif approvals >= 1:
        tier = "possible"
    else:
        tier = "none"

    return {
        "p": round(p, 4),
        "tier": tier,
        "source": util.DERIVED,
        "approvals": approvals,
        "denials": denials,
        "stated_rate_pct": rate,
        "alpha": alpha, "beta": beta,
        "posterior_mean": round(mean, 4),
        "ci80": [round(min(config.P_SPONSORSHIP_CAP, lo * vf), 4),
                 round(min(config.P_SPONSORSHIP_CAP, hi * vf), 4)],
        "volume_factor": round(vf, 4),
        "note": ("p = Beta posterior mean x volume factor, capped at "
                 f"{config.P_SPONSORSHIP_CAP}. The interval is the posterior, scaled. "
                 "Approval rate answers 'did their filings succeed', not 'will they "
                 "sponsor me'."),
    }


def fit_evidence(titles, profile):
    """A deterministic rubric. Reproducible, auditable — and still a judgment."""
    targets = [t.lower() for t in profile.get("target_titles", [])]
    excluded = [t.lower() for t in profile.get("excluded_titles", [])]
    entry = [t.lower() for t in profile.get("entry_rung_titles", [])]
    if not titles:
        return {"p": None, "source": util.MODEL,
                "basis": "no filed titles on record — no basis for a fit judgment, so "
                         "the vote is withheld rather than guessed"}

    tset = [t.lower() for t in titles]
    hits = sorted({t for t in targets if any(t in title for title in tset)})
    excl_hits = sorted({t for t in excluded if any(t in title for title in tset)})
    has_entry = any(any(e in title for e in entry) for title in tset)

    p = config.FIT_FLOOR + config.FIT_TITLE_HIT * len(hits)
    notes = [f"{len(hits)} target title(s) in the filed history: "
             f"{', '.join(hits) if hits else 'none'}"]
    if not has_entry:
        p -= config.FIT_SENIORITY_PENALTY
        notes.append("no entry-rung title in the history (they sponsor seniors, not my level)")
    if len(excl_hits) >= 2:
        p -= config.FIT_EXCLUDED_PENALTY
        notes.append(f"history leans excluded/senior: {', '.join(excl_hits[:3])}")
    p = max(0.05, min(config.FIT_CEILING, p))
    return {
        "p": round(p, 4),
        "source": util.MODEL,
        "target_title_hits": hits,
        "basis": "rubric over filed job titles (config.FIT_*). " + "; ".join(notes),
        "caveat": "This compares my target titles to the titles a company has *filed "
                  "H-1Bs for*, which is not the same as reading a live job description "
                  "against my CV. It is the weakest link in the composite.",
    }


def role_quality_evidence(median_salary, bls):
    """Company's median sponsored salary against the BLS median for my SOC codes."""
    if median_salary is None or not bls.get("median_wage"):
        return {"p": None, "source": util.RECORD,
                "basis": "no median sponsored salary on record for this firm, or no BLS "
                         "median for the target SOC codes — vote withheld"}
    ratio = median_salary / bls["median_wage"]
    p = max(0.0, min(1.0, (ratio - 0.6) / 0.8))
    return {
        "p": round(p, 4),
        "source": util.DERIVED,
        "median_salary_offered": median_salary,
        "bls_median_wage": bls["median_wage"],
        "ratio": round(ratio, 3),
        "cognitive_pivot_score": bls.get("cognitive_pivot_score"),
        "basis": ("company median sponsored salary / BLS median wage for the target SOC "
                  "codes, mapped to [0,1] over ratio 0.6-1.4"),
        "caveat": (f"weight is {config.WEIGHTS['role_quality']} — Chapter 11 never pinned "
                   "one, so this signal currently contributes nothing to the composite. "
                   "The uncertainty pass varies the weight instead of pretending it is settled."),
    }


def liveness_evidence(portal_entry, policy):
    """The liveness GATE. What matters most is what this run did not check."""
    supported = bool(portal_entry and portal_entry.get("enabled")
                     and portal_entry.get("provider"))
    if supported:
        return {
            "factor": config.LIVENESS_VERIFIABLE_FACTOR,
            "source": util.DERIVED,
            "status": "checkable-but-unchecked",
            "provider": portal_entry.get("provider"),
            "manual_verification_required": False,
            "note": "board is on a supported ATS provider, so a posting COULD be "
                    "verified with `npm run ats:liveness <url>`. This run made no "
                    "network call: the gate is open on the strength of provider "
                    "coverage, not of a checked posting.",
        }
    reason = ("no supported ATS provider (scanner covers greenhouse / lever / ashby); "
              "the firm may well be hiring — nobody looked")
    if policy == "legacy-zero":
        return {"factor": 0.0, "source": util.DERIVED, "status": "unverifiable",
                "provider": None, "manual_verification_required": False,
                "note": "policy `legacy-zero`: unverifiable treated as dead. This is the "
                        "behaviour that skipped AMGEN INC (1,882 approvals) in the earlier "
                        "worked run. Kept runnable so the bias can be measured. " + reason}
    if policy == "block":
        return {"factor": 0.0, "source": util.DERIVED, "status": "unverifiable-blocked",
                "provider": None, "manual_verification_required": True,
                "note": "policy `block`: excluded from allocation and listed separately. " + reason}
    return {
        "factor": config.LIVENESS_VERIFIABLE_FACTOR,
        "source": util.DERIVED,
        "status": "unverifiable",
        "provider": None,
        "manual_verification_required": True,
        "note": "policy `neutral-flagged`: missing evidence is not evidence of absence, "
                "so the gate stays open and the recommendation carries a human "
                "verification requirement that the HARD STOP enforces. " + reason,
    }


def build(csv_path, bls_path, portals_path, profile, gate, liveness_policy=None,
          volume_ref=None, csv_rows=None):
    """Assemble the candidate pool: every firm whose filed titles match the profile.

    Rows the gate rejected never enter. Rows the gate flagged enter carrying the flag.
    """
    policy = liveness_policy or config.LIVENESS_DEFAULT_POLICY
    rng = random.Random(config.CI_SEED)
    portals = load_portals(portals_path)
    bls = load_bls(bls_path, profile.get("target_soc_codes"))
    rejected = gigo.rejected_names(gate) if gate else set()
    collisions = gigo.collision_names(gate) if gate else set()

    targets = [t.lower() for t in profile.get("target_titles", [])]
    timeline_factor = (profile.get("timeline") or {}).get("factor", 0.85)
    timeline_source = (profile.get("timeline") or {}).get("source", util.INPUT)

    weights, needs_sponsor = composite.apply_profile(config.WEIGHTS, profile)

    rows = csv_rows
    if rows is None:
        with open(csv_path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

    candidates = []
    seen_norm = set()
    counted = {"rows": len(rows), "title_match": 0, "title_mismatch": 0,
               "gate_rejected": 0, "duplicate_identity": 0, "no_titles": 0}
    # THE BLIND SPOT, counted rather than assumed away. A firm only has filed titles if
    # it has already sponsored someone, so the title filter silently selects on the
    # outcome the engine is trying to predict. Firms with recent Form D funding and no
    # filing record — precisely the ones the book's funding thesis says to surface — are
    # not scored low by this engine. They are invisible to it.
    blind_spot = {"count": 0, "sample": []}
    today = datetime.date.today()

    for row in rows:
        name = (row.get("company_name") or "").strip()
        norm = util.normalize_company(name)
        titles = util.parse_titles(row.get("top_job_titles_sponsored"))
        if not titles:
            counted["no_titles"] += 1
            funding = util.to_float(row.get("total_funding"))
            fdate = (row.get("latest_funding_date") or "").strip()
            if funding and fdate:
                try:
                    d = datetime.datetime.strptime(fdate, "%Y-%m-%d").date()
                except ValueError:
                    d = None
                if d and (today - d).days <= config.FUNDING_STALE_YEARS * 365:
                    blind_spot["count"] += 1
                    if len(blind_spot["sample"]) < 20:
                        blind_spot["sample"].append({
                            "company_name": name, "total_funding": funding,
                            "latest_funding_stage": (row.get("latest_funding_stage") or "").strip(),
                            "latest_funding_date": fdate,
                        })
            continue
        low = " | ".join(t.lower() for t in titles)
        if not any(t in low for t in targets):
            counted["title_mismatch"] += 1
            continue
        counted["title_match"] += 1
        if norm in rejected:
            counted["gate_rejected"] += 1
            continue
        if norm in seen_norm:
            # An entity collision already flagged by the gate: keep the first row so
            # the same evidence is not counted twice under two legal names.
            counted["duplicate_identity"] += 1
            continue
        seen_norm.add(norm)

        approvals = util.to_float(row.get("Total Approvals"))
        denials = util.to_float(row.get("Total Denials"))
        portal_entry = portals["by_norm"].get(norm)
        spon = sponsorship_evidence(approvals, denials, rng, volume_ref=volume_ref)
        fit = fit_evidence(titles, profile)
        rq = role_quality_evidence(util.to_float(row.get("median_salary_offered")), bls)
        live = liveness_evidence(portal_entry, policy)

        flags = []
        if spon["p"] is None:
            flags.append("H1B_FIELDS_ABSENT")
        if norm in collisions:
            flags.append("ENTITY_COLLISION")
        if any(gigo.TITLE_WAGE_RE.search(t) for t in titles):
            flags.append("WAGE_IN_TITLE")
        stage = (row.get("latest_funding_stage") or "").strip()
        if (stage in config.EARLY_STAGES and approvals is not None
                and approvals >= config.IMPLAUSIBLE_STAGE_APPROVALS):
            flags.append("FUNDING_STAGE_IMPLAUSIBLE")
        if live["status"].startswith("unverifiable"):
            flags.append("LIVENESS_UNVERIFIABLE")
        else:
            flags.append("LIVENESS_UNCHECKED")
        if (spon["approvals"] or 0) < config.SMALL_N_APPROVALS and spon["p"] is not None:
            flags.append("SMALL_N_SPONSORSHIP")

        cand = {
            "company_name": name,
            "normalized": norm,
            "industry": (row.get("industry") or "").strip(),
            "state": (row.get("state") or "").strip(),
            "titles_sponsored": titles[:8],
            "total_funding": util.to_float(row.get("total_funding")),
            "latest_funding_stage": stage,
            "latest_funding_date": (row.get("latest_funding_date") or "").strip(),
            "sponsorship": spon,
            "fit": fit,
            "role_quality": rq,
            "liveness": live,
            "timeline": {"factor": timeline_factor, "source": timeline_source,
                         "note": "profile-level: per-posting start dates are not in this "
                                 "dataset, so the same factor applies to every company"},
            "ats": {
                "supported_provider": bool(portal_entry and portal_entry.get("enabled")),
                "provider": (portal_entry or {}).get("provider"),
                "portal_name": (portal_entry or {}).get("name"),
                "in_portals_config": portal_entry is not None,
            },
            "flags": flags,
            "manual_verification_required": bool(live.get("manual_verification_required")),
        }
        composite.score_candidate(cand, weights=weights, needs_sponsor=needs_sponsor)
        candidates.append(cand)

    if policy == "block":
        blocked = [c for c in candidates if c["liveness"]["status"] == "unverifiable-blocked"]
        candidates = [c for c in candidates
                      if c["liveness"]["status"] != "unverifiable-blocked"]
    else:
        blocked = []

    candidates.sort(key=lambda c: -c["composite"])
    return {
        "candidates": candidates,
        "blocked_by_policy": blocked,
        "meta": {
            "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "liveness_policy": policy,
            "weights": weights,
            "needs_sponsorship": needs_sponsor,
            "counts": counted,
            "candidate_count": len(candidates),
            "with_sponsorship_record": sum(1 for c in candidates
                                           if c["sponsorship"]["p"] is not None),
            "unknown_sponsorship": sum(1 for c in candidates
                                       if c["sponsorship"]["p"] is None),
            "manual_verification_required": sum(1 for c in candidates
                                                if c["manual_verification_required"]),
            "supported_ats": sum(1 for c in candidates if c["ats"]["supported_provider"]),
            "portals": {"path": portals["path"], "found": portals["found"],
                        "entries": len(portals["entries"]),
                        "enabled": sum(1 for e in portals["entries"] if e["enabled"])},
            "bls": {"path": bls["path"], "found": bls["found"],
                    "median_wage": bls["median_wage"],
                    "cognitive_pivot_score": bls["cognitive_pivot_score"],
                    "soc_codes": profile.get("target_soc_codes")},
            "unverified_liveness_note": "This run made no network calls. Liveness is "
                                        "unverified for every company; the gate reflects "
                                        "provider coverage only.",
            "blind_spot": {
                "what": "firms with Form D funding in the last "
                        f"{config.FUNDING_STALE_YEARS} years and NO H-1B filing record",
                "count": blind_spot["count"],
                "sample": blind_spot["sample"],
                "why_it_matters": (
                    "A firm has filed job titles only if it has already sponsored someone, "
                    "so the title filter selects on the very outcome the engine predicts. "
                    "These firms are not ranked low — they never enter the pool at all. "
                    "The gate's refusal to read a blank cell as a zero protects the "
                    "arithmetic and does nothing for these firms, because the pool never "
                    "sees them. They are also exactly the recently-funded companies the "
                    "domain's funding thesis says to surface."),
                "why_the_engine_cannot_fix_it": (
                    "The fit vote is computed from filed titles. With no titles there is no "
                    "fit vote, so the composite cannot exceed sponsorship x 0.35 x timeline "
                    "= 0.30 even if sponsorship were imputed at its maximum. These firms are "
                    "structurally unreachable, not merely disadvantaged, and the Monte Carlo "
                    "missingness scenarios cannot rescue them."),
            },
        },
    }
