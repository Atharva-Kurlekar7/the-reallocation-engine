#!/usr/bin/env python3
"""filter-ai-title-sponsors.py — core tool for the ERP-to-AI Engineering mode.

Reads the verified SEC+DOL H-1B mapped dataset and ranks employers by the JOB
TITLES they have actually filed H-1B petitions for. The pivot problem this solves:
a job board shows a title, but not whether the employer sponsors *applied* AI work
(Machine Learning Engineer, Applied Scientist, ML Ops) or only PhD-gated *research*
(Research Scientist, Research Data Scientist). For someone changing careers without
a PhD, that distinction decides whether an application is worth OPT time.

This script is read-only on the source CSV and makes no network calls. It emits
BOTH machine and human artifacts (Output Contract P5):
  - JSON agent log     -> logs/case-erp-to-ai-engineering-<date>.json
  - Markdown report    -> reports/generated/case-erp-to-ai-engineering-<date>.md

Usage:
  python3 scripts/ai-pivot/filter-ai-title-sponsors.py \
      [--csv PATH] [--top N] [--min-approvals N] [--out-dir logs] [--date YYYYMMDD]

Verified vs inferred:
  VERIFIED here = the columns in the source CSV (approvals, rate, titles, funding).
  INFERRED here = the applied/research/mixed CLASS, which is a keyword heuristic
  over the title strings. The class is a judgment, labeled as such in the output.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import json
import os
import sys
from typing import Dict, List, Optional, Tuple

DEFAULT_CSV = "data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv"
WORKFLOW = "case-erp-to-ai-engineering"

# Applied-AI engineering titles: the work an ERP/support engineer can pivot into
# without a research doctorate.
APPLIED_KEYWORDS = [
    "machine learning engineer",
    "ml engineer",
    "applied scientist",
    "applied machine learning",
    "ai engineer",
    "ml ops",
    "mlops",
    "machine learning",
    "data scientist",
    "data engineer",
    "deep learning engineer",
    "computer vision engineer",
    "nlp engineer",
]

# Research-gated titles: typically require a PhD / publication record. A career
# changer without one should treat these as a closed door, not an open req.
RESEARCH_KEYWORDS = [
    "research scientist",
    "research data scientist",
    "research engineer",
    "phd",
    "postdoc",
    "post-doc",
    "principal scientist",
    "staff research",
    "distinguished scientist",
]


def classify_title(title: str) -> str:
    """Classify a single title. Research gate dominates: a 'Research Data
    Scientist' is research-gated even though it contains 'data scientist'."""
    t = title.lower()
    if any(k in t for k in RESEARCH_KEYWORDS):
        return "research"
    if any(k in t for k in APPLIED_KEYWORDS):
        return "applied"
    return "other"


def parse_titles(raw: str) -> List[str]:
    """The source stores titles as a Python-list literal string, e.g.
    "['Machine Learning Engineer III']". Parse defensively."""
    raw = (raw or "").strip()
    if not raw:
        return []
    try:
        val = ast.literal_eval(raw)
        if isinstance(val, list):
            return [str(x).strip() for x in val if str(x).strip()]
        return [str(val).strip()]
    except (ValueError, SyntaxError):
        # Fallback: treat as a single title string.
        return [raw]


def to_float(x: str) -> Optional[float]:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def funding_recency_years(date_str: str, today: dt.date) -> Optional[float]:
    date_str = (date_str or "").strip()
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            d = dt.datetime.strptime(date_str, fmt).date()
            return round((today - d).days / 365.25, 2)
        except ValueError:
            continue
    return None


def company_class(applied: List[str], research: List[str]) -> Optional[str]:
    if applied and research:
        return "mixed"
    if applied:
        return "applied"
    if research:
        return "research-gated"
    return None  # non-AI sponsor, out of scope


def score_company(approvals: Optional[float], rate: Optional[float],
                  applied_n: int, research_n: int,
                  recency_years: Optional[float]) -> float:
    """Applied-friendliness score. Higher = better target for an applied-AI pivot.

    base            = approvals * (rate/100)   [both VERIFIED columns]
    applied_ratio   = down-ranks research-heavy sponsors
    recency_bonus   = recent Form D funding is a mild positive (hiring capacity)
    """
    base = (approvals or 0.0) * ((rate or 0.0) / 100.0)
    denom = applied_n + research_n
    applied_ratio = (applied_n / denom) if denom else 0.0
    recency_bonus = 1.0
    if recency_years is not None and recency_years <= 3.0:
        recency_bonus = 1.15
    return round(base * applied_ratio * recency_bonus, 3)


def run(csv_path: str, top: int, min_approvals: float,
        out_dir: str, date_str: str) -> Tuple[dict, str]:
    today = dt.date.today()
    rows_seen = 0
    rows_with_titles = 0
    applied_pool: List[dict] = []
    research_gated: List[dict] = []
    rejects = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_seen += 1
            titles_raw = row.get("top_job_titles_sponsored")
            titles = parse_titles(titles_raw)
            if not titles:
                continue
            rows_with_titles += 1

            classes = [classify_title(t) for t in titles]
            applied_titles = [t for t, c in zip(titles, classes) if c == "applied"]
            research_titles = [t for t, c in zip(titles, classes) if c == "research"]
            cls = company_class(applied_titles, research_titles)
            if cls is None:
                continue  # non-AI sponsor

            approvals = to_float(row.get("Total Approvals"))
            rate = to_float(row.get("Approval_Rate"))
            median_sal = to_float(row.get("median_salary_offered"))
            recency = funding_recency_years(row.get("latest_funding_date"), today)

            if approvals is None or approvals < min_approvals:
                rejects += 1
                continue

            rec = {
                "company": row.get("company_name", "").strip(),
                "industry": row.get("industry", "").strip(),
                "class": cls,
                "class_source": "model-judgment (keyword heuristic over titles)",
                "total_approvals": approvals,
                "approval_rate": rate,
                "median_salary_offered": median_sal,
                "latest_funding_stage": row.get("latest_funding_stage", "").strip(),
                "latest_funding_date": row.get("latest_funding_date", "").strip(),
                "funding_recency_years": recency,
                "applied_titles": applied_titles,
                "research_titles": research_titles,
                "score": score_company(approvals, rate, len(applied_titles),
                                       len(research_titles), recency),
            }
            if cls in ("applied", "mixed"):
                applied_pool.append(rec)
            else:
                research_gated.append(rec)

    applied_pool.sort(key=lambda r: r["score"], reverse=True)
    shortlist = applied_pool[:top]

    agent_log = {
        "workflow": WORKFLOW,
        "run_id": f"{WORKFLOW}-{date_str}",
        "mode": "sample",
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source_file": csv_path,
        "records_seen": rows_seen,
        "records_with_h1b_titles": rows_with_titles,
        "applied_or_mixed_sponsors": len(applied_pool),
        "research_gated_sponsors": len(research_gated),
        "rejects_below_min_approvals": rejects,
        "min_approvals": min_approvals,
        "shortlist_size": len(shortlist),
        "shortlist": shortlist,
        "stop_conditions": [],
        "todo_items": [
            "[TODO: DEV] JD-level SOC classifier — title strings are not SOC codes",
            "[TODO: DATA SOURCE] live job-posting URLs per company for the liveness gate",
        ],
        "verified_fields": [
            "total_approvals", "approval_rate", "median_salary_offered",
            "latest_funding_stage", "latest_funding_date",
        ],
        "inferred_fields": ["class", "score"],
    }

    # Human report (Markdown)
    lines: List[str] = []
    lines.append(f"# ERP-to-AI Engineering — Applied-AI Sponsor Shortlist")
    lines.append("")
    lines.append(f"- Run: `{agent_log['run_id']}` (mode: sample)")
    lines.append(f"- Source: `{csv_path}`")
    lines.append(f"- Generated: {agent_log['generated_at']}")
    lines.append("")
    lines.append("## Run summary")
    lines.append("")
    lines.append(f"- Records seen: **{rows_seen:,}**")
    lines.append(f"- Records with H-1B title data: **{rows_with_titles:,}**")
    lines.append(f"- Applied/mixed AI sponsors found: **{len(applied_pool)}**")
    lines.append(f"- Research-gated-only sponsors (excluded from shortlist): **{len(research_gated)}**")
    lines.append(f"- Rejected (below min approvals={min_approvals:g}): **{rejects}**")
    lines.append("")
    lines.append("## Verified vs inferred")
    lines.append("")
    lines.append("- **Verified** (source CSV columns): approvals, approval rate, median salary, funding stage/date.")
    lines.append("- **Inferred** (keyword judgment, not verified): the applied / research-gated / mixed **class** and the ranking **score**.")
    lines.append("")
    lines.append(f"## Shortlist (top {len(shortlist)} applied-AI sponsors)")
    lines.append("")
    lines.append("| # | Company | Class | Approvals | Rate % | Median $ | Funding | Applied titles (sample) |")
    lines.append("|---|---------|-------|-----------|--------|----------|---------|--------------------------|")
    for i, r in enumerate(shortlist, 1):
        titles_sample = "; ".join(r["applied_titles"][:2])
        rate = f"{r['approval_rate']:.0f}" if r["approval_rate"] is not None else "—"
        sal = f"{r['median_salary_offered']:,.0f}" if r["median_salary_offered"] is not None else "—"
        stage = r["latest_funding_stage"] or "—"
        lines.append(
            f"| {i} | {r['company']} | {r['class']} | {r['total_approvals']:.0f} | "
            f"{rate} | {sal} | {stage} | {titles_sample} |"
        )
    lines.append("")
    lines.append("## Next gate")
    lines.append("")
    lines.append("This shortlist has cleared the sponsorship-title signal only. Before any")
    lines.append("application, each company must clear the **liveness gate** (is a real")
    lines.append("posting open now?) and the **visa-timeline gate**. Neither is a vote; both")
    lines.append("are hard stops. See `recipes/case-erp-to-ai-engineering.md`.")
    lines.append("")
    report_md = "\n".join(lines)

    return agent_log, report_md


def main() -> int:
    ap = argparse.ArgumentParser(description="Rank H-1B employers by applied-AI title filings.")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="Path to SEC+DOL H-1B mapped CSV")
    ap.add_argument("--top", type=int, default=20, help="Shortlist size")
    ap.add_argument("--min-approvals", type=float, default=5.0, help="Minimum H-1B approvals")
    ap.add_argument("--out-dir", default="logs", help="Directory for the JSON agent log")
    ap.add_argument("--report-dir", default="reports/generated", help="Directory for the Markdown report")
    ap.add_argument("--date", default=dt.date.today().strftime("%Y%m%d"), help="Run date tag YYYYMMDD")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        print(f"STOP: source CSV not found: {args.csv}", file=sys.stderr)
        print("This is a stop condition, not a crash — the mode refuses to guess "
              "without verified data.", file=sys.stderr)
        return 2

    agent_log, report_md = run(args.csv, args.top, args.min_approvals,
                               args.out_dir, args.date)

    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.report_dir, exist_ok=True)
    json_path = os.path.join(args.out_dir, f"{WORKFLOW}-{args.date}.json")
    md_path = os.path.join(args.report_dir, f"{WORKFLOW}-{args.date}.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(agent_log, f, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"Records seen:            {agent_log['records_seen']:,}")
    print(f"With H-1B title data:    {agent_log['records_with_h1b_titles']:,}")
    print(f"Applied/mixed sponsors:  {agent_log['applied_or_mixed_sponsors']}")
    print(f"Research-gated excluded:  {agent_log['research_gated_sponsors']}")
    print(f"Rejected (<{args.min_approvals:g} approvals): {agent_log['rejects_below_min_approvals']}")
    print(f"Shortlist size:          {agent_log['shortlist_size']}")
    print()
    print("Top 10 applied-AI sponsors by score:")
    for i, r in enumerate(agent_log["shortlist"][:10], 1):
        print(f"  {i:2d}. {r['company'][:34]:34s} "
              f"score={r['score']:8.2f}  approvals={r['total_approvals']:.0f}  "
              f"class={r['class']}")
    print()
    print(f"Agent log:    {json_path}")
    print(f"Human report: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
