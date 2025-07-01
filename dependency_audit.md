# Dependency Audit Report

## Executive Summary

This audit covers all dependencies across:
- **pyproject.toml** (Poetry configuration with multiple groups)
- **mcp-server/requirements.txt** 
- **viz/streamlit/requirements.txt**
- **Currently installed packages** (pip list)
- **Latest available versions** on PyPI

### 🚨 Critical Issues Identified:

1. **Dagster Version Incompatibility**: dagster-docker 0.24.0 ❌ **INCOMPATIBLE** with dagster ≥1.8 (Poetry has ^1.8.0)
2. **Major Version Gaps**: Many packages significantly behind latest versions
3. **Duplicate Dependencies**: Same packages with different versions across files
4. **Missing Dagster Installation**: Dagster group not installed despite being in pyproject.toml

---

## Comprehensive Dependency Matrix

| Package | Poetry Version | MCP Server | Streamlit | Installed | Latest PyPI | Status | Notes |
|---------|---------------|------------|-----------|-----------|-------------|--------|-------|
| **🔧 Core Framework Dependencies** |
| dagster | ^1.8.0 | 1.5.13 | - | ❌ Not installed | 1.11.0 | 🚨 **CRITICAL** | Poetry: 1.8+, MCP: 1.5.13, Latest: 1.11.0 |
| dagster-webserver | ^1.8.0 | 1.5.13 | - | ❌ Not installed | 1.11.0 | 🚨 **CRITICAL** | Version mismatch |
| dagster-datahub | ^0.24.0 | - | - | ❌ Not installed | - | 🚨 **INCOMPATIBLE** | 0.24.0 incompatible with dagster ≥1.8 |
| dagster-docker | ^0.24.0 | - | - | ❌ Not installed | - | 🚨 **INCOMPATIBLE** | 0.24.0 incompatible with dagster ≥1.8 |
| apache-airflow | ^2.10.0 | - | - | 2.11.0 | 3.0.2 | ⚠️ **OUTDATED** | Major version behind (v2 vs v3) |
| acryl-datahub | ^0.15.0 | 0.12.1.5 | - | 0.15.0.5 | 1.1.0.4 | ⚠️ **OUTDATED** | Poetry: 0.15, MCP: 0.12, Latest: 1.1 |
| **🌐 Web Framework Dependencies** |
| fastapi | - | 0.104.1 | - | ❌ Not installed | 0.115.14 | ⚠️ **OUTDATED** | MCP version behind latest |
| uvicorn | - | 0.24.0 | - | ❌ Not installed | 0.35.0 | ⚠️ **OUTDATED** | Significant version gap |
| streamlit | - | - | ≥1.28.0 | ❌ Not installed | 1.46.1 | ⚠️ **OUTDATED** | Streamlit req significantly behind |
| strawberry-graphql | - | 0.215.1 | - | ❌ Not installed | 0.275.5 | ⚠️ **OUTDATED** | 60+ versions behind |
| **📊 Data & Analytics Dependencies** |
| duckdb | - | 0.9.2 | ≥0.8.0 | 1.3.1 | 1.3.1 | ✅ **CURRENT** | Installed version is latest |
| sqlalchemy | - | 2.0.23 | ≥2.0.0 | 1.4.54 | 2.0.41 | ⚠️ **MIXED** | Req: 2.0.23, Installed: 1.4.54, Latest: 2.0.41 |
| snowflake-connector-python | - | 3.6.0 | ≥3.0.0 | 3.15.0 | 3.15.0 | ✅ **CURRENT** | Installed version is latest |
| pandas | - | - | ≥2.0.0 | ❌ Not installed | 2.3.0 | ⚠️ **OUTDATED** | Missing, latest available |
| plotly | - | - | ≥5.15.0 | ❌ Not installed | 6.2.0 | ⚠️ **OUTDATED** | Missing, major version behind |
| **🧠 AI/ML Dependencies** |
| langchain | - | 0.0.350 | - | ❌ Not installed | 0.3.26 | ⚠️ **OUTDATED** | Using pre-1.0 version, latest 0.3.x |
| langchain-openai | - | 0.0.2 | - | ❌ Not installed | - | ⚠️ **OUTDATED** | Very early version |
| openai | - | 1.6.1 | - | ❌ Not installed | 1.93.0 | ⚠️ **OUTDATED** | 87 versions behind |
| **📐 Data Validation Dependencies** |
| pydantic | - | 2.5.2 | - | 2.11.7 | 2.11.7 | ✅ **CURRENT** | Installed version is latest |
| **🔨 Development Dependencies** |
| ruff | ^0.8.0 | - | - | 0.8.6 | - | ✅ **CURRENT** | Recent version |
| black | ^24.0.0 | - | - | 24.10.0 | - | ✅ **CURRENT** | Recent version |
| isort | ^5.13.0 | - | - | 5.13.2 | - | ✅ **CURRENT** | Recent version |
| pre-commit | ^4.0.0 | - | - | 4.2.0 | - | ✅ **CURRENT** | Recent version |
| **📊 Jupyter Dependencies** |
| jupyter | ^1.1.0 | - | - | 1.1.1 | - | ✅ **CURRENT** | Recent version |
| jupyterlab | ^4.3.0 | - | - | 4.4.4 | - | ✅ **CURRENT** | Recent version |
| **🔄 Data Pipeline Dependencies** |
| dbt-core | - | 1.7.4 | - | 1.10.2 | 1.10.2 | ✅ **CURRENT** | Installed version is latest |
| **🔒 Database Dependencies** |
| psycopg2-binary | - | - | ≥2.9.0 | ❌ Not installed | - | ⚠️ **MISSING** | Required for PostgreSQL |
| **🔧 Utility Dependencies** |
| requests | ^2.31.0 | - | - | 2.32.4 | - | ✅ **CURRENT** | Recent version |
| python-dotenv | - | 1.0.0 | - | ❌ Not installed | - | ⚠️ **MISSING** | Environment configuration |
| httpx | - | 0.26.0 | - | 0.28.1 | - | ✅ **CURRENT** | Recent version |

---

## 🚨 Critical Incompatibilities

### 1. Dagster Ecosystem Mismatch
- **Issue**: `dagster-docker: 0.24.0` and `dagster-datahub: 0.24.0` are **INCOMPATIBLE** with `dagster: ^1.8.0`
- **Root Cause**: These plugins are from an older ecosystem (0.24.x) that doesn't support dagster 1.8+
- **Impact**: Cannot install dagster group from Poetry
- **Resolution Required**: Update plugin versions to match dagster 1.8+ compatibility

### 2. SQLAlchemy Version Conflict
- **Issue**: MCP Server requires `sqlalchemy==2.0.23` but Poetry has `1.4.54` installed
- **Impact**: Potential breaking changes between 1.4 and 2.0
- **Resolution Required**: Standardize on SQLAlchemy 2.0+ across all components

---

## 📋 Dependency Sources Summary

### Poetry Groups (pyproject.toml):
- **main**: python ≥3.11,<3.13
- **dev**: ruff, black, isort, sqlfluff, pre-commit
- **airflow**: apache-airflow ^2.10.0
- **jupyter**: jupyter, jupyterlab
- **datahub**: acryl-datahub ^0.15.0
- **dagster**: dagster ^1.8.0, dagster-webserver ^1.8.0, dagster-datahub ^0.24.0, dagster-docker ^0.24.0, requests ^2.31.0

### MCP Server Requirements:
- Web: fastapi==0.104.1, uvicorn[standard]==0.24.0, websockets==12.0
- GraphQL: strawberry-graphql[fastapi]==0.215.1
- Database: snowflake-connector-python==3.6.0, duckdb==0.9.2, sqlalchemy==2.0.23
- Orchestration: dagster==1.5.13, dagster-webserver==1.5.13, dbt-core==1.7.4
- DataHub: acryl-datahub==0.12.1.5
- AI: langchain==0.0.350, langchain-openai==0.0.2, openai==1.6.1
- Utils: pydantic==2.5.2, python-multipart==0.0.6, httpx==0.26.0

### Streamlit Requirements:
- Core: streamlit≥1.28.0, pandas≥2.0.0, plotly≥5.15.0
- Database: duckdb≥0.8.0, snowflake-connector-python≥3.0.0, sqlalchemy≥2.0.0, psycopg2-binary≥2.9.0

---

## 🛠️ Recommended Actions

### Immediate (Critical):
1. **Fix Dagster Incompatibility**: 
   - Remove or update `dagster-datahub` and `dagster-docker` to versions compatible with dagster 1.8+
   - Install dagster dependencies to resolve the missing packages

2. **Standardize SQLAlchemy**:
   - Update all components to use SQLAlchemy 2.0+
   - Test for breaking changes in queries/models

### Short-term (High Priority):
3. **Update Core Frameworks**:
   - FastAPI: 0.104.1 → 0.115.14
   - Uvicorn: 0.24.0 → 0.35.0
   - Streamlit: 1.28.0+ → 1.46.1

4. **Unify DataHub Versions**:
   - Standardize on acryl-datahub 1.1.0.4 (latest) across all components

### Medium-term (Medium Priority):
5. **AI/ML Stack Update**:
   - OpenAI: 1.6.1 → 1.93.0
   - Langchain: 0.0.350 → 0.3.26
   - Review breaking changes in these major updates

6. **Apache Airflow Planning**:
   - Plan migration from 2.11.0 → 3.0.2 (major version upgrade)
   - Review breaking changes and migration guide

### Long-term (Low Priority):
7. **Dependency Consolidation**:
   - Consider moving all dependencies to Poetry for unified management
   - Implement dependency scanning in CI/CD
   - Set up automated security vulnerability scanning

---

## 🔍 Dependency Tree Analysis

**Key Findings from `poetry show --tree`:**
- Heavy dependency on Jupyter ecosystem (multiple circular dependencies noted)
- Airflow providers create circular dependency warnings
- Most packages have reasonable dependency trees
- No obvious bloat or conflicting transitive dependencies

**Missing from Installation:**
- Entire dagster group (due to incompatibility)
- MCP server dependencies (fastapi, uvicorn, etc.)
- Streamlit dependencies (streamlit, pandas, plotly, psycopg2-binary)

---

*Audit completed: January 2025*
*Tools used: poetry show --tree, pip list, pipdeptree, PyPI API*
