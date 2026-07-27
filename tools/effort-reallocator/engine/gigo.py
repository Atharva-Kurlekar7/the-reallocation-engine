"""The GIGO gate — run BEFORE the engine is allowed to reallocate anything.

The quality standard, stated so a human can check it:

    Every record used to move a slot must have (1) a company identity that resolves
    to exactly one firm, (2) a sponsorship count and a denial count that agree with
    the stated rate, (3) a funding date recent enough to mean anything, and (4) a
    collection timestamp and a source. A record failing (1) or (2) is rejected. A
    record failing (3) is flagged. The dataset as a whole fails (4).

That last clause is not a formality. This dataset has no per-record timestamp and no
per-record source column, so by the standard above **the dataset fails the gate**.
The tool does not quietly proceed: `DATASET_NO_RECORD_PROVENANCE` is a *blocking*
check, and `execute` refuses until a named human waives it with a written reason.
A gate that cannot fail is decoration.

What this dataset assumes that is not true:

  1. That a blank H-1B cell means "does not sponsor". ~95% of rows are blank
     (see data/verified/.../validation_report.json). Absence of a filing record is
     absence of evidence. The engine routes those firms to an `unknown` tier that
     cannot earn slots on sponsorship grounds — it never imputes zero.
  2. That `Approval_Rate` measures willingness to sponsor. It measures approval
     *given that the firm already filed for someone it had already chosen*.
  3. That `latest_funding_stage` is the company's stage. It is the stage of its last
     SEC Form D filing — a private-placement exemption. Public companies show up as
     "Series B", and a firm with 316 H-1B approvals shows up as "Pre-Seed".
  4. That one row is one company. Identical filing counts appear under multiple legal
     names (INC and LLC variants of the same firm), so a naive join double-counts.
"""

import csv
import datetime
import os
import re

from . import config
from . import util

# severity: "blocking" must be waived by a human before execute; "reject" drops the
# row; "flag" annotates it and travels with the recommendation.
CHECKS = {
    "DATASET_NO_RECORD_PROVENANCE": {
        "severity": "blocking",
        "standard": "every record has a collection timestamp and a source",
        "why": "Without a per-record timestamp there is no way to tell a 2015 filing "
               "from a 2024 one, and no way to detect a protocol change mid-collection. "
               "The engine is reallocating on a snapshot of unknown vintage.",
    },
    "RATE_WITHOUT_DENOMINATOR": {
        "severity": "reject",
        "standard": "a stated rate has a countable numerator and denominator",
        "why": "A percentage with no counts behind it cannot be given a credible interval.",
    },
    "RATE_ARITHMETIC_MISMATCH": {
        "severity": "reject",
        "standard": "Approval_Rate equals approvals/(approvals+denials) x 100",
        "why": "If the stated rate disagrees with its own counts, one of them is wrong "
               "and the tool cannot tell which.",
    },
    "RATE_SCALE_ANOMALY": {
        "severity": "reject",
        "standard": "Approval_Rate is on a 0-100 scale",
        "why": "A 0-1 value in a 0-100 column silently becomes a ~1% approval rate. "
               "This is the perturbation class the fragility pass exploits.",
    },
    "ABSURD_VALUE": {
        "severity": "reject",
        "standard": "counts are non-negative, rates are 0-100, funding is non-negative",
        "why": "An impossible number means the pipeline that produced it is not trustworthy.",
    },
    "ENTITY_COLLISION": {
        "severity": "flag",
        "standard": "one company identity resolves to one row",
        "why": "Identical filing counts under two legal names double-count the same "
               "evidence and can push one firm's history into two thin halves.",
    },
    "IDENTITY_AMBIGUOUS": {
        "severity": "reject",
        "standard": "a company identity resolves to one filing history",
        "why": "The same normalised name carries DIFFERENT filing counts across rows, so "
               "there is no way to tell which row is the firm I would be applying to. "
               "Picking one would be inventing an answer, so every row in the ambiguous "
               "group is refused — including rows with a strong record. That cost is real "
               "and it is the correct cost: a wrong join produces a confident number about "
               "the wrong company.",
    },
    "WAGE_IN_TITLE": {
        "severity": "flag",
        "standard": "a job title contains no salary figure",
        "why": "A wage leaked into the title column means the upstream parse misaligned "
               "fields for that row. If it leaked here it may have leaked elsewhere.",
    },
    "FUNDING_STAGE_IMPLAUSIBLE": {
        "severity": "flag",
        "standard": "funding stage is consistent with sponsorship volume",
        "why": "Form D stage is the stage of the last exemption filing, not the "
               "company's current stage. Using it as a maturity signal is a category error.",
    },
    "FUNDING_DATE_STALE": {
        "severity": "flag",
        "standard": f"the last funding event is within {config.FUNDING_STALE_YEARS} years",
        "why": "An old Form D is not a signal that a company is hiring now.",
    },
    "FUNDING_DATE_MISSING": {
        "severity": "flag",
        "standard": "a funding record carries a date",
        "why": "Undated funding cannot be aged, so it cannot be discounted.",
    },
    "H1B_FIELDS_ABSENT": {
        "severity": "flag",
        "standard": "sponsorship evidence is present, or its absence is labelled unknown",
        "why": "The dominant condition in this dataset. Flagged, never imputed to zero: "
               "the whole engine turns on refusing to read a blank cell as a 'no'.",
    },
    "BLS_TABLE_ABSENT": {
        "severity": "flag",
        "standard": "the BLS occupation table used for role_quality is present",
        "why": "Without the BLS table the role_quality vote is empty while Monte Carlo still "
               "draws its weight from U[0, 0.20]. The intervals change with no crash and no "
               "warning — silence, not a refusal. The CLI refuses a missing path; this check "
               "keeps the absence visible in the gate report if a caller bypasses the CLI.",
    },
}

TITLE_WAGE_RE = re.compile(r"\d{4,}\.\d+")


def _today():
    return datetime.date.today()


def _parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(str(s).strip(), fmt).date()
        except ValueError:
            continue
    return None


def run_gate(csv_path, waivers=None, waiver_reason=None, stale_years=None, bls_path=None):
    """Walk every row of the dataset and apply the checks above.

    Returns a dict with per-check findings, per-row rejects with reason codes, and
    the blocking codes that remain unwaived.
    """
    waivers = [w.strip().upper() for w in (waivers or [])]
    stale_years = stale_years if stale_years is not None else config.FUNDING_STALE_YEARS
    today = _today()

    findings = {code: {"count": 0, "examples": []} for code in CHECKS}
    rejects = []
    reject_counts = {}
    row_count = 0
    with_h1b = 0
    by_norm = {}
    rows_by_norm = {}

    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row_count += 1
            name = (row.get("company_name") or "").strip()
            approvals = util.to_float(row.get("Total Approvals"))
            denials = util.to_float(row.get("Total Denials"))
            rate = util.to_float(row.get("Approval_Rate"))
            funding = util.to_float(row.get("total_funding"))
            stage = (row.get("latest_funding_stage") or "").strip()
            fdate = _parse_date(row.get("latest_funding_date"))
            titles = util.parse_titles(row.get("top_job_titles_sponsored"))
            codes = []

            has_counts = approvals is not None and denials is not None
            if has_counts:
                with_h1b += 1
            else:
                codes.append("H1B_FIELDS_ABSENT")

            if rate is not None and not has_counts:
                codes.append("RATE_WITHOUT_DENOMINATOR")

            if rate is not None and has_counts and (approvals + denials) > 0:
                if rate <= 1.0 and approvals > 1:
                    codes.append("RATE_SCALE_ANOMALY")
                else:
                    implied = 100.0 * approvals / (approvals + denials)
                    if abs(implied - rate) > config.RATE_ARITHMETIC_TOLERANCE:
                        codes.append("RATE_ARITHMETIC_MISMATCH")

            if ((approvals is not None and approvals < 0)
                    or (denials is not None and denials < 0)
                    or (rate is not None and (rate < 0 or rate > 100.0))
                    or (funding is not None and funding < 0)):
                codes.append("ABSURD_VALUE")

            if any(TITLE_WAGE_RE.search(t) for t in titles):
                codes.append("WAGE_IN_TITLE")

            if (stage in config.EARLY_STAGES and approvals is not None
                    and approvals >= config.IMPLAUSIBLE_STAGE_APPROVALS):
                codes.append("FUNDING_STAGE_IMPLAUSIBLE")

            if funding is not None:
                if fdate is None:
                    codes.append("FUNDING_DATE_MISSING")
                elif (today - fdate).days > stale_years * 365:
                    codes.append("FUNDING_DATE_STALE")

            norm = util.normalize_company(name)
            if norm:
                key = (norm, approvals, denials)
                by_norm.setdefault(key, []).append(name)
                rows_by_norm.setdefault(norm, []).append(
                    {"company_name": name, "approvals": approvals, "denials": denials,
                     "rate": rate})

            for code in codes:
                f = findings[code]
                f["count"] += 1
                if len(f["examples"]) < 5:
                    ex = {"company_name": name}
                    if code in ("RATE_WITHOUT_DENOMINATOR", "RATE_ARITHMETIC_MISMATCH",
                                "RATE_SCALE_ANOMALY", "ABSURD_VALUE"):
                        ex.update({"approvals": approvals, "denials": denials, "rate": rate})
                    if code == "WAGE_IN_TITLE":
                        ex["title"] = next(t for t in titles if TITLE_WAGE_RE.search(t))
                    if code == "FUNDING_STAGE_IMPLAUSIBLE":
                        ex.update({"stage": stage, "approvals": approvals})
                    if code in ("FUNDING_DATE_STALE", "FUNDING_DATE_MISSING"):
                        ex.update({"latest_funding_date": row.get("latest_funding_date"),
                                   "total_funding": funding})
                    f["examples"].append(ex)

            rejected = [c for c in codes if CHECKS[c]["severity"] == "reject"]
            if rejected:
                rejects.append({
                    "company_name": name,
                    "codes": rejected,
                    "approvals": approvals,
                    "denials": denials,
                    "approval_rate": rate,
                    "what_the_engine_does": "excluded from the candidate pool entirely",
                })
                for c in rejected:
                    reject_counts[c] = reject_counts.get(c, 0) + 1

    # Identity ambiguity: the same normalised name with DIFFERENT filing histories. The
    # engine cannot tell which row is the firm, so it refuses all of them rather than
    # guessing. This is where the gate costs something real.
    ambiguous = []
    for norm, entries in rows_by_norm.items():
        if len(entries) < 2:
            continue
        counts = {(e["approvals"], e["denials"]) for e in entries}
        if len(counts) < 2:
            continue  # identical histories -> handled as ENTITY_COLLISION below
        if not any(e["approvals"] is not None for e in entries):
            continue  # all blank: nothing to attribute, so nothing to get wrong
        ambiguous.append({"normalized": norm, "rows": entries})
        for e in entries:
            rejects.append({
                "company_name": e["company_name"],
                "codes": ["IDENTITY_AMBIGUOUS"],
                "approvals": e["approvals"],
                "denials": e["denials"],
                "approval_rate": e["rate"],
                "normalized": norm,
                "conflicting_rows": [x["company_name"] for x in entries],
                "what_the_engine_does": "excluded from the candidate pool — the filing "
                                        "history cannot be attributed to one firm",
            })
            reject_counts["IDENTITY_AMBIGUOUS"] = reject_counts.get("IDENTITY_AMBIGUOUS", 0) + 1
    ambiguous.sort(key=lambda a: -max((e["approvals"] or 0) for e in a["rows"]))
    findings["IDENTITY_AMBIGUOUS"]["count"] = sum(len(a["rows"]) for a in ambiguous)
    findings["IDENTITY_AMBIGUOUS"]["examples"] = [
        {"normalized": a["normalized"],
         "rows": [f"{e['company_name']} "
                  f"({'blank' if e['approvals'] is None else int(e['approvals'])} approvals)"
                  for e in a["rows"]]}
        for a in ambiguous[:5]
    ]

    # Entity collisions: the same normalized name with identical filing counts under
    # more than one legal name. Identical counts are the tell — two genuinely different
    # firms would not share an approval and denial count exactly.
    collisions = []
    for (norm, appr, den), names in by_norm.items():
        if len(names) > 1 and appr is not None:
            collisions.append({
                "normalized": norm, "approvals": appr, "denials": den,
                "rows": sorted(set(names)),
                "risk": "double-counted evidence if joined naively; two thin halves if split",
            })
    collisions.sort(key=lambda c: -(c["approvals"] or 0))
    findings["ENTITY_COLLISION"]["count"] = len(collisions)
    findings["ENTITY_COLLISION"]["examples"] = collisions[:5]

    # The dataset-level provenance failure. Checked structurally, not per row.
    with open(csv_path, newline="", encoding="utf-8") as fh:
        header = next(csv.reader(fh))
    prov_cols = [c for c in header
                 if re.search(r"(timestamp|collected|as_of|retrieved|source|vintage)", c, re.I)]
    if not prov_cols:
        findings["DATASET_NO_RECORD_PROVENANCE"]["count"] = row_count
        findings["DATASET_NO_RECORD_PROVENANCE"]["examples"] = [{
            "header": header[:6] + ["..."],
            "missing": "no timestamp / as_of / source / vintage column exists",
            "consequence": "the snapshot's vintage is unknown and un-agable per record",
        }]

    # BLS table: the CLI refuses a missing path, but a programmatic caller can still
    # reach evidence.load_bls and silently proceed with empty role_quality. Surface
    # that here so the gate report cannot look clean while the intervals quietly change.
    if bls_path and not os.path.exists(bls_path):
        findings["BLS_TABLE_ABSENT"]["count"] = 1
        findings["BLS_TABLE_ABSENT"]["examples"] = [{
            "path": util.rel(bls_path),
            "missing": "BLS occupation table not found at the configured path",
            "consequence": "role_quality votes empty; Monte Carlo still draws the weight",
        }]

    blocking = [c for c, spec in CHECKS.items()
                if spec["severity"] == "blocking" and findings[c]["count"] > 0]
    blocking_unwaived = [c for c in blocking if c not in waivers]
    flags = {c: findings[c]["count"] for c, s in CHECKS.items()
             if s["severity"] == "flag" and findings[c]["count"] > 0}

    if blocking_unwaived:
        status = "BLOCKED"
    elif blocking:
        status = "PASS-WITH-WAIVER"
    elif rejects or flags:
        status = "PASS-WITH-FLAGS"
    else:
        status = "PASS"

    return {
        "_what_this_is": "The GIGO gate. The engine may not reallocate until this "
                         "passes; execute() refuses while a blocking code is unwaived.",
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "dataset": util.rel(csv_path),
        "status": status,
        "row_count": row_count,
        "rows_with_h1b_fields": with_h1b,
        "h1b_missing_rate": round(1.0 - (with_h1b / row_count), 4) if row_count else None,
        "standard": (
            "Every record used to move a slot must have (1) an identity resolving to "
            "one firm, (2) counts that agree with the stated rate, (3) a funding date "
            "recent enough to mean anything, and (4) a collection timestamp and source."
        ),
        "hidden_assumptions": [
            "A blank H-1B cell means the company does not sponsor. It does not: it "
            "means no filing was matched. The engine routes these to `unknown` and "
            "never imputes zero.",
            "Approval_Rate measures willingness to sponsor. It measures approval given "
            "the firm already filed for a candidate it had already selected.",
            "latest_funding_stage is the company's stage. It is the stage of its last "
            "Form D filing, so public firms appear as early-stage.",
            "One row is one company. Identical filing counts recur under INC/LLC variants.",
        ],
        "checks": {
            code: {
                "severity": spec["severity"],
                "standard": spec["standard"],
                "why_it_matters": spec["why"],
                "count": findings[code]["count"],
                "rate": round(findings[code]["count"] / row_count, 4) if row_count else None,
                "examples": findings[code]["examples"],
            }
            for code, spec in CHECKS.items()
        },
        "rejects": rejects,
        "reject_counts": reject_counts,
        "reject_total": len(rejects),
        "identity_ambiguous_groups": [
            {"normalized": a["normalized"],
             "rows": [{"company_name": e["company_name"], "approvals": e["approvals"]}
                      for e in a["rows"]]}
            for a in ambiguous[:40]
        ],
        "identity_ambiguous_group_total": len(ambiguous),
        "flags": flags,
        "entity_collisions": collisions[:40],
        "entity_collision_total": len(collisions),
        "blocking": blocking,
        "blocking_unwaived": blocking_unwaived,
        "waivers": [{"code": c, "reason": waiver_reason} for c in waivers],
        "waiver_reason": waiver_reason,
    }


def rejected_names(gate):
    """Normalized names the gate refuses to let into the candidate pool."""
    return {util.normalize_company(r["company_name"]) for r in gate["rejects"]}


def collision_names(gate):
    """Normalized names involved in an entity collision (flagged, not rejected)."""
    out = set()
    for c in gate.get("entity_collisions", []):
        for n in c["rows"]:
            out.add(util.normalize_company(n))
    return out


def summary_lines(gate):
    lines = []
    lines.append("=" * 74)
    lines.append(f"GIGO GATE — {gate['dataset']}")
    lines.append("=" * 74)
    lines.append(f"  rows                     {gate['row_count']:,}")
    lines.append(f"  rows with H-1B fields    {gate['rows_with_h1b_fields']:,} "
                 f"({util.pct(1 - gate['h1b_missing_rate'])})")
    lines.append(f"  H-1B fields ABSENT       {util.pct(gate['h1b_missing_rate'])} "
                 f"— flagged unknown, NEVER imputed to zero")
    lines.append("")
    lines.append("  check                          sev       count   rate")
    for code, c in gate["checks"].items():
        if c["count"] == 0:
            continue
        lines.append(f"  {code:<30} {c['severity']:<9} {c['count']:>7,} "
                     f"{util.pct(c['rate'])}")
    lines.append("")
    lines.append(f"  rejected rows            {gate['reject_total']:,} "
                 f"({', '.join(f'{k}={v}' for k, v in gate['reject_counts'].items()) or 'none'})")
    lines.append(f"  STATUS                   {gate['status']}")
    if gate["blocking_unwaived"]:
        lines.append("")
        lines.append("  !! BLOCKING — the dataset does not meet the stated standard:")
        for code in gate["blocking_unwaived"]:
            lines.append(f"     {code}: {gate['checks'][code]['standard']}")
    return "\n".join(lines)


def render(gate):
    o = []
    o.append(f"# GIGO gate report — {gate['generated'][:10]}\n")
    o.append(f"**Dataset:** `{gate['dataset']}` — {gate['row_count']:,} rows  ")
    o.append(f"**Status:** **{gate['status']}**\n")
    o.append("## The quality standard\n")
    o.append(f"> {gate['standard']}\n")
    o.append("## What this dataset assumes that is not true\n")
    for i, a in enumerate(gate["hidden_assumptions"], 1):
        o.append(f"{i}. {a}")
    o.append("")
    o.append("## Checks\n")
    o.append("| Check | Severity | Count | Rate | Why it matters |")
    o.append("|---|---|---:|---:|---|")
    for code, c in gate["checks"].items():
        o.append(f"| `{code}` | {c['severity']} | {c['count']:,} | "
                 f"{util.pct(c['rate'])} | {c['why_it_matters']} |")
    o.append("")
    o.append(f"**Missing H-1B fields: {util.pct(gate['h1b_missing_rate'])} of rows.** "
             "The engine routes these to an `unknown` sponsorship tier that cannot earn "
             "slots on sponsorship grounds. It never reads a blank cell as a zero — that "
             "single decision is the difference between \"no evidence\" and \"evidence of no\".\n")

    o.append("## Rejections\n")
    if gate["rejects"]:
        o.append(f"{gate['reject_total']:,} rows rejected: "
                 + ", ".join(f"`{k}` × {v}" for k, v in gate["reject_counts"].items()) + "\n")
        o.append("| Company | Codes | Approvals | Denials | Stated rate |")
        o.append("|---|---|---:|---:|---:|")
        for r in gate["rejects"][:25]:
            o.append(f"| {r['company_name']} | {', '.join('`%s`' % c for c in r['codes'])} | "
                     f"{util.fmt(r['approvals'], 0)} | {util.fmt(r['denials'], 0)} | "
                     f"{util.fmt(r['approval_rate'], 2)} |")
        if gate["reject_total"] > 25:
            o.append(f"\n… and {gate['reject_total'] - 25:,} more in `rejects.json`.")
    else:
        o.append("No rows rejected outright. That is a finding to be suspicious of, "
                 "not a clean bill of health — see the flags above.")
    o.append("")

    o.append("## Entity collisions (flagged)\n")
    o.append(f"{gate['entity_collision_total']:,} normalized names carry identical filing "
             "counts under more than one legal name. Identical counts are the tell: two "
             "genuinely different firms would not share an approval *and* a denial count "
             "exactly.\n")
    if gate["entity_collisions"]:
        o.append("| Normalized | Approvals | Rows |")
        o.append("|---|---:|---|")
        for c in gate["entity_collisions"][:10]:
            o.append(f"| {c['normalized']} | {util.fmt(c['approvals'], 0)} | "
                     f"{' · '.join(c['rows'])} |")
    o.append("")

    if gate["blocking"]:
        o.append("## Blocking\n")
        for code in gate["blocking"]:
            c = gate["checks"][code]
            waived = code not in gate["blocking_unwaived"]
            o.append(f"- **`{code}`** — standard: *{c['standard']}*. {c['why_it_matters']} "
                     f"{'**WAIVED** by a human: ' + (gate.get('waiver_reason') or '(no reason given)') if waived else '**UNWAIVED — `execute` will refuse.**'}")
        o.append("")
        o.append("A gate that cannot fail is decoration. This one fails on the dataset's "
                 "own terms, and clearing it takes a named human and a written reason.\n")
    return "\n".join(o) + "\n"
