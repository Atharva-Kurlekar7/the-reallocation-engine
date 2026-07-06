# Domain Justification — ERP-to-AI Engineering Sponsorship Triage

**Mode:** `recipes/case-erp-to-ai-engineering.md`
**Lifecycle stage reached:** RUNNABLE-SAMPLE

## Who uses this, and in what exact situation

An international master's student with an **ERP / application-support background**
(Oracle OTM/AMS, ServiceNow, SQL — L2/L3 support, not implementation) who is
pivoting into **applied AI/ML engineering** (ML Engineer, Data Engineer, Applied
Scientist), is on **F-1 with OPT not yet filed**, requires **H-1B sponsorship**,
and does **not** hold a research doctorate. This is my own situation. The person
has real transferable evidence (SQL, data pipelines, an OCI Generative AI cert,
two RAG course projects) but no shipped production AI role yet, and a hard OPT
clock that makes wasted applications expensive.

## The information asymmetry it addresses

A job board shows a **title** and a **company**. It does not show two things this
person most needs to see:

1. **Whether the company sponsors *applied* AI titles or only PhD-gated research.**
   "AI hiring" conflates two very different doors. A company that files H-1Bs for
   *Research Scientist* is effectively closed to someone without a PhD; a company
   that files for *Machine Learning Engineer* or *Data Engineer* is open. From the
   outside these look identical. The engine's `top_job_titles_sponsored` column
   makes the distinction visible: of 1,557 companies with H-1B title data, this run
   found **160 applied/mixed sponsors** and excluded **22 research-gated-only**
   companies that a naive "does it sponsor AI?" filter would have kept.

2. **Whether a historically strong sponsor is actually hiring right now.** History
   is not intent. `npm run ats:scan --dry-run` queries each enabled company's Greenhouse
   API, filters to applied-AI title keywords, and reports yield — only companies with
   postings in that yield pass the hiring-now gate. Optional `--verify` adds Playwright
   page checks before applying; not required for RUNNABLE-SAMPLE.

## Connection to the engine layers

- **80 Days to Stay** — the mode reads the SEC Form D + DOL/H-1B mapped dataset
  (`data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv`): approvals, approval
  rate, funding stage, and the job titles actually filed.
- **Job-Ops** — `npm run ats:scan --dry-run` reads `data/examples/erp-to-ai-portals.yml`,
  scans **16 applied-AI H-1B shortlist companies** on Greenhouse. The 2026-07-06 run:
  **1,742 jobs → 341 applied-AI yield**. Six sample roles for scoring were hand-picked
  from that yield (P6 logged gap: no auto-wiring script yet).
- **The Cognitive Pivot** — the filter reads `data/bls/compact/soc_occupation_compact.csv`
  and attaches the base-occupation `cognitive_pivot_score` as an **advisory column**
  in the shortlist report (not a gate vote — the book leaves the role_quality weight
  unpinned). Verified: SOC 15-1252 (Software Developers) = **3.834**; SOC 15-2051
  (Data Scientists) is **blank in the BLS source** and is surfaced as `gap`, not
  guessed. That blank is itself a finding: the primary "Data Scientist" occupation
  the mode targets has no cognitive score in the repo's verified data.

## Failure modes specific to this domain

**1. Title-string false positive ("Data Scientist" that isn't applied ML).**
The classifier keys on title strings. "Data Scientist" can mean production ML or
it can mean BI/dashboard analytics; both file under the same string. The mode will
rank a BI-analytics sponsor as an applied-AI target. **Who struggles most to catch
it:** exactly this user — a career changer who cannot yet read the seniority and
stack signals in a JD, and who is therefore most likely to trust the title at face
value and burn an application. A domain expert or a working ML engineer would catch
it in seconds; the person the mode is *for* is the one who can't.

**2. Historical H-1B volume mistaken for current hiring intent.**
The filter ranks on *cumulative* approvals — LINKEDIN CORP shows 4,962 approvals
and lands #1 — but that history says nothing about whether the company is hiring
applied-AI roles *this month*. A career-changer reads "4,962 approvals" as "they
hire a lot of people like me" and applies; only someone tracking recent req flow
(or running `npm run ats:scan --dry-run` on an enabled Greenhouse board) catches that the signal is
past-tense. The scan mitigates this **only when the company is on a scannable board and appears in yield**;
without one, a top-ranked historical sponsor is still a Skip in the scorer.
