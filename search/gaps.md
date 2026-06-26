# search/gaps.md
# Agent-drafted gap table — dual track: Applied AI / Gen AI Engineer (primary) + IT Systems Analyst (parallel)
# Primary SOC: 15-2051 Data Scientists ($112,590 median) / 15-1252 Software Developers ($133,080 median)
# Parallel SOC: 15-1211 Computer Systems Analysts ($103,790 median)
# Cross-referenced against BLS/O*NET skill levels and 3-posting pattern analysis.
# Updated 2026-06-25: AI Engineer track added as primary target.
#
# Assignment edits pending (by you):
#   □ Kill one wrong row — delete it from the table, write one sentence below explaining why
#   □ Rewrite one row in your own words
# ---

## Gap Table — AI Engineer Track (primary)

| # | Gap | Evidence the target demands it | What I have | Plan to close it |
|---|-----|-------------------------------|-------------|-----------------|
| A1 | Shipped AI/Gen AI project in a public repo (LLM, RAG, or fine-tuned model) | BLS 15-2051 alternate titles include "Applied Scientist" and "AI Developer." Pattern across 3 AI Engineer postings (Oracle AI Associate, IBM AI Engineer, general Gen AI JDs): all require a portfolio of working AI projects, not just certifications. OCI Gen AI cert alone is not sufficient evidence. | Oracle Cloud Infrastructure Generative AI Professional cert (2025) demonstrates conceptual understanding of LLMs, RAG architecture, and OCI AI services. No shipped project using an LLM API, no public repo with a deployed model or pipeline. | Build and publish one end-to-end RAG pipeline — e.g., index the Reallocation Engine repo docs with embeddings, expose a Q&A interface via FastAPI. Host on GitHub with README explaining architecture choices. Closes when a public repo with working code and documented output exists. |
| A2 | Python data science and ML stack depth (pandas, scikit-learn, PyTorch or HuggingFace) | BLS 15-2051 Job Zone 4 requires "considerable preparation." O*NET tasks: "develop and implement analytics applications." Pattern: every AI Engineer posting in sample requires Python proficiency + at least one ML framework. | Python used in INFO 7375 pipeline scripts (data ingest, transform, scoring). No documented use of scikit-learn, PyTorch, or HuggingFace in resume or projects. Academic coursework likely included these but no project demonstrates end-to-end model training or inference. | Complete one project demonstrating a full ML pipeline: data → features → model → evaluation → inference. Publish to GitHub with a model card. Can reuse the Reallocation Engine dataset (SEC + H1B sponsorship prediction). Closes when a repo shows training run, eval metrics, and inference example. |
| A3 | LLM integration experience — prompt engineering, API wrapping, chain/agent design | Gen AI Engineer JDs consistently require hands-on LLM API experience (OpenAI, Anthropic, or OCI GenAI). Pattern: 2 of 3 sampled postings list LangChain, LlamaIndex, or equivalent orchestration framework as preferred. | OCI GenAI cert covers prompt engineering concepts. No documented project using LLM APIs at code level — no chain design, no function calling, no agent orchestration in resume or projects. | Build one LLM-powered tool using LangChain or LlamaIndex — a document Q&A or structured data extractor on a real dataset. Closes when working code is deployed or demonstrated in a screencast with source available. |
| A4 | MLOps basics — model versioning, deployment pipeline, basic monitoring | BLS 15-1252 Software Developers (ML Engineer track): skill_complex_problem_solving_lv 3.5. IBM and HCLTech AI postings list MLflow, Docker, or Kubernetes for model deployment as preferred. Pattern: all 3 postings expect a candidate who can get a model from notebook to API. | No MLOps tools (MLflow, DVC, Docker for ML) in resume or projects. Pipeline scripts exist but are data pipelines, not model serving pipelines. | Containerize one trained model with Docker + FastAPI. Use MLflow to log experiment runs on the Reallocation Engine project. Closes when a Docker image and MLflow experiment log can be pointed to. |
| A5 | Cloud ML platform hands-on (OCI AI Services, AWS SageMaker, or Azure ML) | BLS 15-2051 employment 233K, growth high. All 3 sampled postings require cloud platform deployment of models, not just local notebook runs. OCI GenAI cert covers concepts but not hands-on implementation evidence. | OCI certifications (GenAI Professional + Data Platform Foundations 2025) demonstrate cloud conceptual knowledge. No deployed model on a cloud ML platform in resume or projects. | Use OCI Data Science service (free tier) to train and deploy one model end-to-end. Document the deployment architecture. Closes when a deployment notebook and endpoint URL (or screenshot of active endpoint) is linked in resume. Leverages existing OCI cert investment. |

---

## Gap Table — IT Systems Analyst Track (parallel, still active)

| # | Gap | Evidence the target demands it | What I have | Plan to close it |
|---|-----|-------------------------------|-------------|-----------------|
| B1 | ServiceNow administration (CSA-level, not end-user) | 3 of 3 sampled IT postings (IBM Oracle Package Specialist, HCLTech Admin, State Street Systems Analyst) list ServiceNow as required or preferred. CSA preferred in 2 of 3. O*NET 15-1211 skill_systems_evaluation_lv 4.12. | Used ServiceNow for incident/change management as an end-user at exp_1 and exp_2. No admin access, no flow design, no CSA credential. | Build a ServiceNow Personal Developer Instance (free at developer.servicenow.com), complete CAD course, sit CSA exam. Closes when CSA credential issued. |

---

## Killed Row

**Row killed:** B2 — Business requirements documentation and UAT ownership

**Reason:** The agent generated this gap because BRD ownership appears in generic O*NET 15-1211 Systems Analyst task descriptions, but the actual roles I applied to — IBM AI Engineer, HCLTech Admin, Oracle AI Associate — are technical implementation roles, not business analyst positions; none of their job descriptions list BRD or UAT coordination as a requirement.

---

## Rewritten Row

**Row rewritten:** A1 — No shipped AI project in a public repo

| Gap | Evidence the target demands it | What I have | Plan to close it |
|-----|-------------------------------|-------------|-----------------|
| I have an OCI Generative AI Professional certification but no working AI project I can point a recruiter to. Every AI Engineer role I have looked at screens for a GitHub repo or a demo — the cert shows I understand the concepts, but it does not show I can build anything with them. | The IBM AI Engineer entry-level posting and the Oracle AI Associate program both list a portfolio of AI/ML projects as a requirement or strong preference. The OCI GenAI cert is listed as a plus, not a substitute. The pattern across the three postings I reviewed is consistent: conceptual knowledge alone does not pass the first screen. | I understand LLM architecture, RAG pipeline design, and OCI AI Services from cert prep. I have no deployed project, no public repo with model code, and nothing I can walk through in a technical interview without sounding like I memorized documentation. | Build one end-to-end RAG pipeline on a dataset I already have — the Reallocation Engine's SEC + H1B data — expose it through a FastAPI endpoint, and publish it to GitHub with a README that explains why I made each design choice. This closes when the repo is public and the code runs. Not when I finish another course. |

---

## Notes

- BLS source: `data/bls/compact/soc_occupation_compact.csv` pulled 2026-06-25.
- AI Engineer posting sample: Oracle AI Associate program JD, IBM AI Engineer entry-level, one generic Gen AI Developer posting from LinkedIn (3-posting pattern, searched 2026-06-25).
- IT Analyst posting sample: IBM R-646296, HCLTech Administrator Miami-Dade, State Street R-790190.
- Gaps close only when external evidence exists: a shipped project, a published piece, or a credential with an external issuer. "Took a course" is not a closing condition.
- When a gap closes: add the credential/project to `resume.json`, delete the row here.
