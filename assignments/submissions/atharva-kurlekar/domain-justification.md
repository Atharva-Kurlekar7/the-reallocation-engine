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
   is not intent. The liveness gate turns a past-tense signal into a present-tense
   one.

## Connection to the engine layers

- **80 Days to Stay** — the mode is built directly on the SEC Form D + DOL/H-1B
  mapped dataset (`data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv`),
  reading approvals, approval rate, funding stage, and sponsored titles.
- **Job-Ops** — the liveness gate reuses the repo's tested liveness checker
  (`scripts/ats/liveness-browser.mjs`) to confirm a posting is live before it
  counts.
- **The Cognitive Pivot** — applied-AI SOCs (15-2051 Data Scientists, 15-1252
  Software Developers) are the target occupations; role-quality scoring against
  BLS/O*NET is the natural next weight once the JD-SOC classifier exists.

## Failure modes specific to this domain

**1. Title-string false positive ("Data Scientist" that isn't applied ML).**
The classifier keys on title strings. "Data Scientist" can mean production ML or
it can mean BI/dashboard analytics; both file under the same string. The mode will
rank a BI-analytics sponsor as an applied-AI target. **Who struggles most to catch
it:** exactly this user — a career changer who cannot yet read the seniority and
stack signals in a JD, and who is therefore most likely to trust the title at face
value and burn an application. A domain expert or a working ML engineer would catch
it in seconds; the person the mode is *for* is the one who can't.

**2. "Mixed" sponsor whose open reqs are all research.** A company that has filed
for both "ML Engineer" and "Research Scientist" is classed **mixed** and kept — but
its *currently open* reqs may all be the PhD-gated ones. The mode's optimism here is
invisible to someone without a PhD, who assumes any AI filing signals a door they
can walk through. The person with the credential to catch this (a PhD, or an insider
who knows the team's headcount) is precisely the person who doesn't need the mode;
the person who needs it is the one it can mislead. This is why the mode marks
liveness a hard gate and labels the applied/research class **inferred, not verified**
in every artifact.
