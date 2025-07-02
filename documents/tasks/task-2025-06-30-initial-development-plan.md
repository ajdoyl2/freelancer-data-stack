# Task: Initial Development Plan - Freelancer Data Stack

Complete setup of a comprehensive data stack development environment and infrastructure.

## Current Status Overview
- **Task 6 (Python environments)**: ✅ COMPLETED
- **Current Position**: Ready to proceed with remaining tasks
- **Next Priority**: Assess completion status of previous tasks and continue systematic implementation

---

## 1. Bootstrap macOS development environment ✅ (MOSTLY COMPLETED)
### 1.1 Core Installation
- [x] Install Homebrew (COMPLETED - /opt/homebrew/bin/brew)
- [ ] Install Rosetta 2 (if needed for Apple Silicon) - ASSESS REQUIREMENT
- [x] Create `~/data-stack` workspace directory (COMPLETED)

### 1.2 Command-line essentials
- [x] Install `git` (COMPLETED - /opt/homebrew/bin/git)
- [x] Install `gh` (GitHub CLI) (COMPLETED - /opt/homebrew/bin/gh)
- [x] Install `pyenv` ✅ (COMPLETED in Task 6)
- [x] Install `asdf` (COMPLETED - function loaded)
- [x] Install `direnv` ✅ (COMPLETED in Task 6)
- [x] Install `make` (COMPLETED - /opt/homebrew/opt/make/libexec/gnubin/make)

### 1.3 Shell Configuration ✅ COMPLETED
- [x] Configure global `.zshrc` with environment variables placeholders
- [x] Configure `.warp/init.zsh` with environment variables
- [x] Add placeholders: `AWS_PROFILE`, `SNOWFLAKE_ACCOUNT`, etc.
- [x] Add data stack aliases and shortcuts

### 1.4 GitHub Setup ✅ COMPLETED
- [x] Generate SSH keys (already existed)
- [x] Connect to GitHub (already configured)
- [x] Test GitHub connectivity (authenticated as ajdoyl2)

---

## 2. Install and configure Docker Desktop (Apple Silicon) ✅ COMPLETED
### 2.1 Docker Installation
- [x] Install Docker Desktop for Apple Silicon (COMPLETED - Docker version 28.2.2)
- [!] Configure resource limits (memory, CPU) - NEEDS ATTENTION: Currently 2 CPUs, 2GB RAM
- [x] Test Docker functionality (COMPLETED - hello-world test passed)

### 2.2 Kubernetes & Alternatives
- [x] Enable Kubernetes in Docker Desktop (COMPLETED - running at kubernetes.docker.internal:6443)
- [ ] Install Colima (optional lightweight alternative) - NOT NEEDED
- [x] Test cluster functionality (COMPLETED - kubectl cluster-info successful)

### 2.3 Volume Configuration
- [x] Create shared volumes directory (`~/data-stack/volumes`)
- [x] Set up volume permissions (COMPLETED)
- [x] Test volume mounting (COMPLETED - alpine test successful)
- [x] Create service-specific volume directories

### 2.4 Multi-arch Support
- [x] Test multi-arch image builds (COMPLETED - both arm64 and amd64 working)
- [x] Configure platform pinning for `linux/amd64` when required
- [x] Document platform-specific requirements

---

## 3. Repo & project scaffolding ✅ (PARTIALLY COMPLETED)
### 3.1 Repository Setup
- [x] Initialize mono-repo `freelancer-data-stack` on GitHub
- [x] Clone repository locally

### 3.2 Folder Structure
- [x] Create folder structure:
  - [x] `infra/terraform`
  - [x] `docker/`
  - [x] `orchestration/dagster`
  - [x] `ingestion/airbyte`
  - [x] `ingestion/dlt`
  - [x] `transformation/dbt`
  - [x] `quality/great_expectations`
  - [x] `viz/evidence`
  - [x] `viz/metabase`
  - [x] `viz/streamlit`
  - [x] `catalog/datahub`
  - [x] `mcp-server`

### 3.3 Default Files
- [x] Commit default `.editorconfig`
- [x] Commit `.gitignore`
- [x] Commit `LICENSE`
- [x] Commit `README.md`

---

## 4. Infrastructure-as-Code with Terraform
### 4.1 Module Setup
- [ ] Create `s3` module
- [ ] Create `snowflake` module
- [ ] Create `ecr` module
- [ ] Create `ecs` module (or `fly.io` alternative)
- [ ] Create secret manager module

### 4.2 Backend Configuration
- [ ] Set up local backend (`local.tfstate`)
- [ ] Configure remote backend (`s3`)
- [ ] Test backend switching

### 4.3 GitHub OIDC Integration
- [ ] Configure Terraform outputs for GitHub OIDC
- [ ] Set up deploy permissions
- [ ] Test OIDC authentication

### 4.4 Make Targets
- [ ] Provide `make deploy-local`
- [ ] Provide `make deploy-prod`
- [ ] Test deployment commands

---

## 5. Docker-Compose stack for local services
### 5.1 Core Services Setup
- [ ] Postgres (Airbyte, Metabase metadata)
- [ ] Airbyte
- [ ] Dagster (code-location hot reload)
- [ ] DataHub + Kafka quickstart

### 5.2 Analysis & Visualization Services
- [ ] Great Expectations Jupyter/Streamlit image
- [ ] Evidence.dev dev server
- [ ] Metabase
- [ ] DuckDB exposed via REST (duckdb-http)

### 5.3 Infrastructure Services
- [ ] Proxy network & Traefik dashboard
- [ ] Volume mapping to `~/data-stack/volumes/*`
- [ ] Service health checks
- [ ] Inter-service networking

### 5.4 Testing & Validation
- [ ] Test all services start successfully
- [ ] Verify service connectivity
- [ ] Test volume persistence
- [ ] Document service URLs and ports

---

## 6. Python environments & dependency management ✅ COMPLETED
- [x] Use `pyenv` + `python 3.11.x` as global
- [x] Per-tool virtualenvs managed via `direnv` and `poetry`
- [x] `requirements-*.txt` lock files to mirror in Docker images
- [x] Pre-commit hooks: `ruff`, `black`, `isort`, `sqlfluff`

**Status**: Fully implemented and tested. See `task-2025-06-30-python-environment-setup.md`

---

## 7. Configure dbt with DuckDB & Snowflake
### 7.1 dbt Setup
- [ ] Install dbt-core and adapters (duckdb, snowflake)
- [ ] Initialize dbt project structure
- [ ] Configure project settings

### 7.2 Profile Configuration
- [ ] Create `profiles.yml` with two targets:
  - [ ] `duckdb_local` target
  - [ ] `snowflake_prod` target
- [ ] Test profile connections

### 7.3 Example Data & Models
- [ ] Seed example datasets
- [ ] Add incremental model showcasing environment switch
- [ ] Test model compilation and execution

### 7.4 Package Integration
- [ ] Add dbt packages: `dbt_expectations`, `dbt_artifacts`
- [ ] Configure package dependencies
- [ ] Test package installation

### 7.5 DataHub Integration
- [ ] Register dbt manifest with DataHub on every run
- [ ] Configure lineage tracking
- [ ] Test DataHub integration

---

## 8. Orchestrate pipelines with Dagster
### 8.1 Dagster Setup
- [ ] Install Dagster and required packages
- [ ] Initialize Dagster project structure
- [ ] Configure code locations

### 8.2 Asset Development
- [ ] Create Airbyte `sync` job asset
- [ ] Create dlt ingestion pipeline asset
- [ ] Create dbt `run` & `test` assets
- [ ] Create Great Expectations validation asset

### 8.3 DataHub Integration
- [ ] Configure `dagster-datahub` integration
- [ ] Map software-defined assets to DataHub
- [ ] Test lineage visualization

### 8.4 Scheduling & Sensors
- [ ] Schedule daily demo job
- [ ] Create sensors for GitHub release events
- [ ] Test automation triggers

---

## 9. Quality & observability setup
### 9.1 Great Expectations
- [ ] Configure Great Expectations
- [ ] Create data validation suites
- [ ] Set up data docs generation

### 9.2 Data Docs Integration
- [ ] Serve Great Expectations data docs via Evidence
- [ ] Configure automated updates
- [ ] Test documentation accessibility

### 9.3 Lineage Visualization
- [ ] Configure Dagster + DataHub lineage visualization
- [ ] Test end-to-end lineage tracking
- [ ] Document lineage capabilities

### 9.4 Monitoring & Alerting
- [ ] Add Prometheus & Grafana side-car in compose for metrics
- [ ] Configure Slack alert webhooks template
- [ ] Test alerting workflows

---

## 10. Visualization layer configuration
### 10.1 Evidence.dev Setup
- [ ] Configure Evidence.dev for DuckDB file access
- [ ] Configure Evidence.dev for Snowflake (through gateway)
- [ ] Create sample Evidence reports
- [ ] Test Evidence development workflow

### 10.2 Metabase Configuration
- [ ] Configure Metabase container
- [ ] Create sample dashboards
- [ ] Configure env var loading of DB credentials
- [ ] Test Metabase functionality

### 10.3 Streamlit Upgrade
- [ ] Upgrade Jupyter to Streamlit: `streamlit run notebooks/app.py`
- [ ] Create sample Streamlit applications
- [ ] Test Streamlit integration

---

## 11. CI/CD with GitHub Actions
### 11.1 Lint & Test Workflow
- [ ] Create `lint-test.yml` workflow
- [ ] Configure static checks and unit tests
- [ ] Test workflow execution

### 11.2 Build & Push Workflow
- [ ] Create `build-push.yml` workflow
- [ ] Configure multi-arch image builds
- [ ] Configure push to ECR
- [ ] Test image building and pushing

### 11.3 Infrastructure Deployment
- [ ] Create `deploy-infra.yml` workflow
- [ ] Configure Terraform plan/apply with OIDC
- [ ] Test infrastructure deployment

### 11.4 Application Deployment
- [ ] Create `deploy-app.yml` workflow
- [ ] Configure Helm/Compose stack deploy to prod
- [ ] Test application deployment

### 11.5 Matrix Strategy
- [ ] Configure matrix strategy for M1/local vs amd64/cloud builds
- [ ] Test cross-platform builds

---

## 12. Developer tooling: VS Code & Warp
### 12.1 VS Code Configuration
- [ ] Create devcontainer referencing Docker stack
- [ ] Configure extensions:
  - [ ] Python
  - [ ] dbt-Power User
  - [ ] SQLFluff
  - [ ] Terraform
  - [ ] Docker
  - [ ] DataHub
  - [ ] AI pair-programmer

### 12.2 Warp Workflows
- [ ] Create `.warp/workflows` for common commands:
  - [ ] `warp dagster ui`
  - [ ] `warp airbyte sync`
  - [ ] `warp dbt run -s model+`

### 12.3 Snippets & Templates
- [ ] Create snippets for LLM prompts
- [ ] Create MCP command templates
- [ ] Test developer productivity tools

---

## 13. Enable micro-batch & real-time capabilities
### 13.1 Streaming Infrastructure
- [ ] Add optional Kafka services to compose
- [ ] Add optional Materialize services to compose
- [ ] Configure streaming data pipelines

### 13.2 Real-time Processing
- [ ] Create Dagster asset sensor for Kafka topic consumption
- [ ] Configure dbt incremental model triggers
- [ ] Test real-time data processing

### 13.3 Feature Flags
- [ ] Document feature flags for streaming capabilities
- [ ] Create configuration templates
- [ ] Test streaming feature activation

---

## 14. Scaffold MCP (Model Context Protocol) server
### 14.1 FastAPI Service Setup
- [ ] Create FastAPI service in `mcp-server/`
- [ ] Configure basic service structure
- [ ] Test basic API functionality

### 14.2 Plugin Adapters
- [ ] Create Dagster adapter
- [ ] Create dbt adapter
- [ ] Create Snowflake adapter
- [ ] Create DuckDB adapter
- [ ] Create DataHub adapter
- [ ] Expose GraphQL + REST interfaces

### 14.3 LLM Integration
- [ ] Configure LLM gateway (LangChain)
- [ ] Implement code generation capabilities
- [ ] Implement data Q&A functionality

### 14.4 Real-time Features
- [ ] Implement WebSocket channel for real-time monitoring
- [ ] Configure alerting capabilities
- [ ] Test real-time communication

### 14.5 Deployment
- [ ] Create Dockerfile for MCP server
- [ ] Create Helm chart
- [ ] Register service in Terraform outputs
- [ ] Test MCP server deployment

---

## Recommended Priority Order (After Deep Analysis)

### **PHASE 1: Foundation (Local Development)**
**Priority 1A**: Complete Task 1 - macOS Environment
- Shell configuration (.zshrc/.warp with env vars)
- GitHub SSH setup and connectivity
- **Why First**: Essential for all subsequent git operations and environment consistency

**Priority 1B**: Complete Task 2 - Docker Environment
- Docker Desktop configuration and testing
- Volume setup and multi-arch validation
- **Why Second**: Required for local services stack and development workflow

**Priority 1C**: Task 5 - Docker-Compose Local Stack
- Core services (Postgres, basic networking)
- **Why Third**: Enables local development and testing of all subsequent components

### **PHASE 2: Infrastructure & Base Services**
**Priority 2A**: Task 4 - Terraform Infrastructure
- Start with local backend, basic modules
- **Why Here**: Infrastructure foundation needed before cloud deployments

**Priority 2B**: Task 7 - dbt Configuration
- Local DuckDB setup first, then Snowflake integration
- **Why Before Dagster**: Data transformation layer is foundational to orchestration

### **PHASE 3: Orchestration & Data Pipeline**
**Priority 3A**: Task 8 - Dagster Orchestration
- **Why After dbt**: Orchestration depends on having transformation layer ready

**Priority 3B**: Complete Task 5 - Full Docker-Compose Stack
- Add remaining services (Airbyte, DataHub, etc.)
- **Why Here**: Now we have core pipeline to integrate with these services

### **PHASE 4: Quality & Visualization**
**Priority 4A**: Task 9 - Quality & Observability
**Priority 4B**: Task 10 - Visualization Layer

### **PHASE 5: Production & Advanced Features**
**Priority 5A**: Task 11 - CI/CD
**Priority 5B**: Task 12 - Developer Tooling
**Priority 5C**: Task 13 - Real-time Capabilities
**Priority 5D**: Task 14 - MCP Server

## Phase 1C: Docker-Compose Local Stack ✅ COMPLETED

**COMPLETED:**
- ✅ PostgreSQL, Redis, Metabase running successfully
- ✅ Docker volumes configured (avoiding permissions issues)
- ✅ Service connectivity tested and verified
- ✅ Metabase accessible at http://localhost:3000

## Phase 2A: Terraform Infrastructure 🔄 IN PROGRESS

**PROCEEDING WITH:**

1. **Complete shell configuration** (.zshrc/.warp with environment variables)
2. **Set up GitHub SSH keys** and test connectivity
3. **Configure Docker Desktop** (resources, Kubernetes if needed)
4. **Test Docker functionality** with simple multi-arch build
5. **Set up basic volume structure** for local development

**Estimated Time**: 30-45 minutes
**Dependencies**: None (all prerequisites met)
**Risk Level**: Low
**Immediate Value**: Essential foundation for all subsequent work

---

*Date Created: 2025-06-30*
*Last Modified: 2025-06-30*
*Status: Planning Phase - Ready to Execute*
