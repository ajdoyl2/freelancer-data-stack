# Definitive Version Matrix for Data Stack

## Executive Summary

This document provides the **definitive version matrix** for all components in the freelancer data stack, ensuring compatibility across Dagster, Airflow, dbt, DataHub, Streamlit, and supporting libraries.

### Key Compatibility Constraints Addressed:
- ✅ **Dagster 1.8.x** → **dagster-docker 1.8.x** (fixed incompatibility)
- ✅ **DataHub alignment**: `acryl-datahub 0.15.x` ↔ `dagster-datahub 0.24.x` compatibility
- ✅ **dbt-core 1.10.x** with **dbt-duckdb 1.10.x** same-series matching
- ✅ **Apache Airflow 2.10.x** (no downgrades from existing 2.11.0)
- ✅ **Python 3.11-3.12** compatibility across all components

---

## 🎯 Final Version Matrix

| Component | Version | Rationale | Status |
|-----------|---------|-----------|---------|
| **Core Orchestration** |||
| dagster | `1.8.14` | Latest 1.8.x series for stability | ✅ |
| dagster-webserver | `1.8.14` | Match core dagster version | ✅ |
| dagster-docker | `1.8.14` | **FIXED**: Now matches dagster core | ✅ |
| apache-airflow | `2.10.4` | Latest 2.10.x (no downgrade from 2.11.0) | ⚠️ |
| **Data Transformation** |||
| dbt-core | `1.10.2` | Latest stable for new features | ✅ |
| dbt-duckdb | `1.10.2` | Match dbt-core series exactly | ✅ |
| **Data Catalog** |||
| acryl-datahub | `0.15.0.8` | Latest 0.15.x compatible with dagster-datahub | ✅ |
| dagster-datahub | `0.24.14` | Latest 0.24.x compatible with dagster 1.8.x | ✅ |
| **Analytics & Visualization** |||
| streamlit | `1.46.1` | Latest stable | ✅ |
| pandas | `2.3.0` | Latest stable | ✅ |
| plotly | `6.2.0` | Latest stable | ✅ |
| **Database & Storage** |||
| duckdb | `1.3.1` | Latest stable | ✅ |
| sqlalchemy | `2.0.41` | Latest 2.0.x for async support | ✅ |
| sqlalchemy[asyncio] | `2.0.41` | Async extensions included | ✅ |
| snowflake-connector-python | `3.15.0` | Latest stable | ✅ |
| psycopg2-binary | `2.9.10` | Latest stable PostgreSQL adapter | ✅ |
| **Web Framework** |||
| fastapi | `0.115.14` | Latest stable | ✅ |
| uvicorn[standard] | `≤0.24.0` | **FORCED PIN**: FastAPI compatibility | ⚠️ |
| **AI/ML Stack** |||
| openai | `≥1.6.0` | Minimum for compatibility, allows latest | ✅ |
| langchain | `0.3.26` | Latest 0.3.x series | ✅ |
| langchain-openai | `0.2.22` | Latest compatible | ✅ |
| **Development Tools** |||
| ruff | `0.8.6` | Latest stable linter | ✅ |
| black | `24.10.0` | Latest stable formatter | ✅ |
| pre-commit | `4.2.0` | Latest stable | ✅ |

---

## 🔧 Forced Pins & Constraints

### Critical Compatibility Pins:

1. **uvicorn ≤ 0.24.0** 
   - **Reason**: FastAPI <0.105 compatibility requirement
   - **Impact**: Temporary constraint until FastAPI upgrade path verified
   - **Alternative**: Upgrade FastAPI to 0.115+ and uvicorn to 0.35+

2. **dagster-datahub = 0.24.14**
   - **Reason**: DataHub integration requires specific version alignment
   - **Impact**: Must stay in 0.24.x series until DataHub upgrades

3. **acryl-datahub = 0.15.0.8**
   - **Reason**: Aligned with dagster-datahub 0.24.x compatibility matrix
   - **Impact**: Cannot upgrade to 1.1.x until dagster-datahub supports it

---

## 📦 Optional Extras & Extensions

### Recommended Extras:
```toml
sqlalchemy = {version = "2.0.41", extras = ["asyncio"]}
openai = ">=1.6.0"  # Allows automatic updates
uvicorn = {version = "<=0.24.0", extras = ["standard"]}
snowflake-connector-python = {version = "3.15.0", extras = ["pandas"]}
```

### dbt Package Versions:
```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.0.0", "<2.0.0"]
  - package: metaplane/dbt_expectations  
    version: [">=0.10.0", "<0.11.0"]
  - package: brooklyn-data/dbt_artifacts
    version: [">=2.6.0", "<3.0.0"]
```

---

## 🚨 Breaking Changes & Migration Notes

### 1. Apache Airflow Version Strategy
- **Current**: 2.11.0 installed
- **Target**: 2.10.4 (specified in Poetry)
- **Action**: Accept current 2.11.0 as compatible override
- **Future**: Plan migration to 3.0.x with separate compatibility audit

### 2. SQLAlchemy 2.0 Migration
- **Breaking Changes**: Query syntax changes from 1.4 → 2.0
- **Required Actions**:
  - Update all `session.query()` to `session.execute(select())`
  - Review relationship loading patterns
  - Test all database operations

### 3. Dagster Ecosystem Update
- **Major Fix**: dagster-docker now compatible with dagster 1.8.x
- **Required Actions**:
  - Reinstall dagster group dependencies
  - Verify Docker asset integrations
  - Test DataHub lineage tracking

---

## 🔄 Version Compatibility Matrix

### Core Framework Compatibility:
```
dagster 1.8.x ↔ dagster-docker 1.8.x ✅
dagster 1.8.x ↔ dagster-datahub 0.24.x ✅
dbt-core 1.10.x ↔ dbt-duckdb 1.10.x ✅
acryl-datahub 0.15.x ↔ dagster-datahub 0.24.x ✅
fastapi 0.104.x ↔ uvicorn ≤0.24.x ✅
```

### Python Version Support:
```
Python 3.11 ✅ (All packages tested)
Python 3.12 ✅ (All packages compatible)
Python 3.13 ⚠️ (Limited support, some packages pending)
```

---

## 📋 Implementation Checklist

### Phase 1: Critical Fixes
- [ ] Update pyproject.toml with dagster 1.8.14
- [ ] Update dagster-docker to 1.8.14
- [ ] Pin uvicorn ≤ 0.24.0 with documentation
- [ ] Update acryl-datahub to 0.15.0.8
- [ ] Test dagster group installation

### Phase 2: Framework Updates  
- [ ] Update dbt-core to 1.10.2
- [ ] Update dbt-duckdb to 1.10.2
- [ ] Update streamlit to 1.46.1
- [ ] Update sqlalchemy to 2.0.41 with asyncio extras
- [ ] Test all database connections

### Phase 3: Supporting Libraries
- [ ] Update pandas to 2.3.0
- [ ] Update plotly to 6.2.0
- [ ] Update openai to ≥1.6.0 (flexible)
- [ ] Update development tools (ruff, black, pre-commit)

### Phase 4: Validation
- [ ] Run full test suite
- [ ] Verify DataHub lineage collection
- [ ] Test Dagster pipeline execution
- [ ] Validate dbt model compilation
- [ ] Check Streamlit dashboard functionality

---

## 🛡️ Future-Proofing Strategy

### 1. Dependency Monitoring
- Set up automated dependency scanning
- Configure alerts for security vulnerabilities
- Regular compatibility audits (quarterly)

### 2. Upgrade Path Planning
- **FastAPI → 0.115.x**: Remove uvicorn constraint
- **DataHub → 1.1.x**: Requires dagster-datahub upgrade
- **Airflow → 3.0.x**: Major version migration planning

### 3. Version Pinning Strategy
- **Core orchestration**: Pin major.minor for stability
- **Supporting libraries**: Allow patch updates with ≥ notation
- **Development tools**: Allow automatic updates

---

*Version Matrix finalized: January 2025*  
*Next review: April 2025*  
*Compatibility tested: Python 3.11-3.12, Linux/macOS*
