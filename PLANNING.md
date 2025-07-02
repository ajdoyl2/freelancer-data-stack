# PLANNING.md

## Vision
Build a **self-service data platform** where a developer (human) issues natural-language requests through Warp and embedded AI agents autonomously **create, test, update and extend** the stack – from ingestion all the way to visualisation – for both local development and cloud production.

* The Generative-AI agents act as your data team: writing code, managing infra, validating data, fixing bugs and documenting work.
* An **MCP (Multi-Component Platform) server** provides state, orchestration and a secure execution sandbox for agents.

---

## Guiding Principles
1. **Human-in-the-loop** – every change is proposed by an agent, reviewed/approved by a human.
2. **Fail-fast, test-first** – automated tests + linters gate all agent PRs.
3. **Incremental deployment** – identical dev/CI/prod environments, promoted via CI pipelines.
4. **Explainability** – agents must emit reasoning steps and link to source in PR descriptions.
5. **Best practices by default** – black, ruff, pre-commit, semantic versioning, conventional commits.
6. **Secure by design** – no plaintext secrets; all infra through IaC (Terraform + Pulumi).

---

## Strategic Objectives
| # | Objective | Outcome Metric |
|---|-----------|---------------|
|1|Local AI development loop < **5 min**|Time from NL request → green tests|
|2|One-command cloud deploy|`make deploy-cloud` provisions full stack in <30 min|
|3|Agent success rate > **90 %**|PRs merged without human refactor|
|4|Recovery time < 15 min|MTTR for failed prod runs|
|5|Cost efficiency < $0.25 per agent run|OpenAI/FaaS cost dashboards|

---

## Roadmap (rolling 6-week horizon)

### Phase 0 – Foundation (Week 0-1)
- [ ] Adopt **Poetry** project layout (DONE)
- [ ] Enable **direnv** + `.envrc` for seamless venv loading
- [ ] Add `make agent-test` that runs `pytest`, `ruff`, `black --check`
- [ ] Containerise MCP server; expose gRPC + REST for agent calls
- [ ] Set up **LangChain code index** so agents can semantically search repo

### Phase 1 – Agent Framework (Week 1-3)
- [ ] Add **Agent SDK** (OpenAI-functions) as `freelancer_ai/` package
- [ ] Implement "Plan → Code diff → PR" loop using GitHub App
- [ ] Auto-generate unit tests for new code paths (pytest + hypothesis)
- [ ] Integrate **DeepEval** for scoring agent outputs

### Phase 2 – Core Stack Automation (Week 2-4)
- [ ] Dagster: agent can scaffold asset/jobs via NL prompt
- [ ] dbt: agent produces models/tests/docs, runs `dbt build`
- [ ] Airbyte/DataHub connectors: agent updates YAML specs
- [ ] Streamlit: agent adds new dashboards with mocked data

### Phase 3 – Cloud Deployment (Week 3-5)
- [ ] Terraform modules for AWS EKS + RDS + S3
- [ ] GitHub Actions → OIDC → AWS deploy
- [ ] "deploy-preview": every PR spins ephemeral stack via Tilt or Okteto

### Phase 4 – Optimisation & Observability (Week 4-6)
- [ ] Add **OpenTelemetry** traces around agent invocations
- [ ] Configure **Prometheus + Grafana** dashboards for latency/cost
- [ ] Run nightly synthetic tasks to detect drift & schema changes

> Phases overlap; refine weekly in sprint-planning.

---

## AI-Enablement Backlog (Always-on)

| Priority | Action Item | Benefit |
|----------|-------------|---------|
|P0|Document core domain concepts in `/docs/knowledge_base/` (auto-built mkdocs)|↓Hallucinations|
|P0|Hook **Conventional Commits** into `commitlint`|Better change logs|
|P1|Add `pre-commit` hook to run `nbqa black` on notebooks|Consistency|
|P1|Publish **Embed model** of codebase to Pinecone|Faster RAG|
|P2|Implement "self-heal": agent re-runs failed CI job, suggests fix|Resilience|
|P2|Auto-summarise merged PRs into CHANGELOG.md|Docs|
|P3|Refactor docker-compose → **Dagger** pipelines|Speed|

---

## Risks & Mitigation
* **Hallucination / Wrong changes** → unit & integration tests, human review.
* **Cost overrun** → monitor token usage, set OpenAI hard limits.
* **Secret leakage** → use **doppler** / AWS Secrets Manager, never echo secrets.
* **State drift between dev & prod** → GitOps, env parity via containers.

---

## Roles & Responsibilities
| Actor | Responsibility |
|-------|----------------|
|AI Agent(s)|Generate plan, code diff, tests, docs, PR description|
|Human Reviewer|Approve/deny PRs, refine prompts, escalate issues|
|MCP Server|Task queue, sandboxed execution, artefact storage|
|CI/CD|Run tests/lint/scan, deploy on merge|

---

## Success Metrics Dashboard (to build)
- Lead-time for change (DORA)
- PR agent accuracy (%)
- Token consumption per task
- MTTR for failed prod run
- Weekly new features delivered

---

## Glossary
* **MCP** – Multi-Component Platform server coordinating agent tasks.
* **Warp** – AI-enhanced terminal used as primary interface.
* **Agent** – LLM-powered autonomous worker paired with human oversight.

---

_Last updated: 2025-07-02_
