# 5-Minute Show-and-Tell — ERP-to-AI Engineering Mode

No slides. Show the mode file and the terminal. Target the four graded beats:
domain, asymmetry, one thing learned from running it, one honest limitation.

---

## 0:00–0:45 — The situation (be specific)

> "I'm an ERP / application-support engineer — Oracle OTM, ServiceNow, SQL —
> pivoting to **applied** AI/ML. F-1, OPT not filed yet, I need H-1B sponsorship,
> and I don't have a PhD. Every application I send costs OPT time I can't get back."

Point at `recipes/case-erp-to-ai-engineering.md` Purpose section.

## 0:45–1:45 — The information asymmetry

> "A job board shows a title and a company. It does NOT show two things I most need:
> (1) does this company sponsor **applied** AI — ML Engineer, Data Engineer — or only
> **PhD-gated research** like Research Scientist? Those look identical from outside,
> but one door is closed to me. (2) Is it even hiring right now, or am I applying to
> a historical sponsor with nothing open?"

## 1:45–3:15 — Show it run (live terminal)

Run these three, talking over them:

```bash
python3 scripts/ai-pivot/filter-ai-title-sponsors.py --top 20 --min-approvals 5
```
> "30K companies → 160 applied-AI sponsors. 22 research-only excluded."

```bash
REALLOCATION_ENGINE_PORTALS=data/examples/erp-to-ai-portals.yml \
  npm run ats:scan -- --dry-run
```
> "16 Greenhouse boards from the H-1B shortlist → 1,742 jobs → 341 applied-AI
> matches. This is hiring now — from the ATS API, not hand URLs."

```bash
npm run score data/examples/erp-to-ai-roles.json
```
> "Apply 3 · Consider 1 · Skip 2."

## 3:15–4:15 — One thing I learned from running it

> "History is not a job opening. Amgen has 1,882 approvals and DocuSign 1,082 — both
> score **0.000 → Skip** because they aren't on a scannable Greenhouse board. Without
> the scan gate I'd waste applications on companies I can't confirm are hiring now.
> Airbnb alone returned dozens of live ML/Data Scientist reqs in the dry-run."

## 4:15–5:00 — One honest limitation (what it cannot verify)

> "The scan only reads Greenhouse/Lever/Ashby APIs. Amazon, Apple, Google, Infosys,
> and TCS are in my config but disabled — Workday/proprietary portals need a provider
> we don't have yet. And it classifies by the **title string** — 'Data Scientist' can
> mean applied ML or BI analytics. That's why this is **RUNNABLE-SAMPLE, not VERIFIED**."

---

## If asked "why RUNNABLE-SAMPLE not VERIFIED?"
> "The filter and scorer really run on real data, and the ATS scan really hit 16
> Greenhouse boards — but the applied/research split is a keyword heuristic, big-tech
> portals aren't scannable yet, and title strings aren't SOC codes. Calling it VERIFIED
> would be the exact fluency-over-evidence failure this course is about."

## Backup numbers (memorize)
- 30,369 rows · 1,557 with H-1B title data · 160 applied/mixed · 22 research-gated excluded
- BLS cognitive: 15-1252 = 3.834 · 15-2051 = gap (blank in source, not guessed)
- ATS scan: 16 companies · 1,742 jobs found · 341 applied-AI yield (dry-run)
- Score: Apply 3 · Consider 1 · Skip 2 (33% skip)
- Top Apply: Reddit Staff Data Engineer 0.382; Twilio Staff ML Engineer 0.346
