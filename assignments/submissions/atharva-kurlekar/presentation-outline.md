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
> "30,369 companies → 160 that sponsor applied-AI titles. It **excluded 22** that
> only file for research scientists — those a naive 'does it sponsor AI?' filter
> would have kept."

```bash
node scripts/ai-pivot/liveness-gate.mjs --file data/examples/erp-to-ai-liveness-urls.txt
```
> "This is the gate. 1 passes, 4 close — including a dead posting that 404s."

```bash
npm run score data/examples/erp-to-ai-roles.json
```
> "Apply 1, Consider 1, Skip 3. The three skips are strong sponsors — but the
> liveness gate zeroed them because there's no live posting. Skip is the point."

## 3:15–4:15 — One thing I learned from running it

> "History is not a job opening. Reddit, Etsy, DocuSign are all proven applied-AI
> sponsors with 99% approval rates — and all three scored **0.000 → Skip**, because
> the liveness gate found nothing live to apply to. Without the gate I'd have spent
> three applications on companies that weren't hiring. The gate multiplying to zero
> is what makes that visible."

## 4:15–5:00 — One honest limitation (what it cannot verify)

> "It classifies by the **title string**. 'Data Scientist' gets treated as applied ML
> even if it's really BI/analytics — and the person most likely to be fooled by that
> is exactly who the mode is for: a career-changer who can't yet read a JD. That's why
> I marked it **RUNNABLE-SAMPLE, not VERIFIED**, labeled the class 'inferred' in every
> artifact, and my top next step is a JD-to-SOC classifier so the split is grounded in
> the posting, not the title."

---

## If asked "why RUNNABLE-SAMPLE not VERIFIED?"
> "The filter and scorer really run on real data, and liveness is a real live check —
> but I only liveness-checked 4 of 20 companies, the applied/research split is a
> keyword heuristic, and I fed careers landing pages instead of per-posting URLs.
> Calling it VERIFIED would be the exact fluency-over-evidence failure this course
> is about."

## Backup numbers (memorize)
- 30,369 rows · 1,557 with H-1B title data · 160 applied/mixed · 22 research-gated excluded
- Liveness: 1 PASS / 4 CLOSED · Score: Apply 1 / Consider 1 / Skip 3 (60% skip)
- Airbnb composite 0.372 (Apply); gated companies 0.000 (Skip)
