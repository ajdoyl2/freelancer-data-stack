name: "Poetry to UV Migration - Comprehensive Data Stack Transformation"
description: |

## Purpose

Complete migration from Poetry to UV package management across the entire freelancer-data-stack project, updating 32 integration points including CI/CD pipelines, Docker containers, development scripts, and automation workflows to leverage UV's 10-100x performance improvements.

## Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and caveats from comprehensive codebase analysis
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix throughout migration
3. **Information Dense**: Use keywords and patterns from existing Poetry usage analysis
4. **Progressive Success**: Start simple, validate, then enhance with comprehensive rollback capability

---

## Goal

Migrate the freelancer-data-stack project from Poetry to UV package management while preserving all functionality, maintaining dependency groups, and ensuring seamless development workflow transition with 10-100x performance improvements.

## Why

- **Performance**: UV provides 10-100x faster package operations vs Poetry
- **Standards Compliance**: Align with Python packaging standards (PEP 621, PEP 735)
- **Developer Experience**: Faster dependency resolution and installation
- **CI/CD Efficiency**: Dramatically reduce pipeline execution time
- **Future-Proofing**: UV is the modern Python packaging standard

## What

Complete replacement of Poetry with UV across:
- Core project configuration (pyproject.toml transformation)
- 6 GitHub Actions workflows
- 2 Docker containers
- 2 shell scripts
- 3 Python automation scripts
- All development documentation

### Success Criteria

- [ ] All 277 dependencies correctly resolved with UV
- [ ] All 6 dependency groups preserved and functional
- [ ] CI/CD pipelines execute with UV (10-100x faster)
- [ ] Docker builds use UV (faster image builds)
- [ ] Development workflow maintains all functionality
- [ ] All existing tests pass without modification
- [ ] Comprehensive validation scripts confirm migration success

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- url: https://docs.astral.sh/uv/
  why: Official UV documentation with complete command reference

- url: https://docs.astral.sh/uv/concepts/projects/dependencies/
  why: Dependency management concepts and PEP 735 compliance

- url: https://www.loopwerk.io/articles/2024/migrate-poetry-to-uv/
  why: Comprehensive migration guide with real-world examples

- url: https://pydevtools.com/handbook/how-to/how-to-migrate-from-poetry-to-uv/
  why: Python Developer Tooling Handbook migration instructions

- url: https://github.com/mkniewallner/migrate-to-uv
  why: Automated migration tool (uvx migrate-to-uv)

- file: pyproject.toml
  why: Current Poetry configuration with 6 dependency groups requiring transformation

- file: poetry.lock
  why: 277 packages (703KB) requiring UV lock file generation

- file: .github/workflows/lint-test.yml
  why: Primary CI/CD workflow with extensive Poetry integration

- file: mcp-server/Dockerfile
  why: Container using Poetry for server dependencies

- file: scripts/update-requirements.sh
  why: Shell script with 5 Poetry export commands needing UV conversion

- docfile: docs/poetry-to-uv-migration-validation-strategy.md
  why: Comprehensive validation strategy created during research

- file: scripts/uv_migration_validator.py
  why: Custom validation script for migration verification

- file: scripts/uv_health_check.py
  why: Ongoing health monitoring for UV environment

- file: scripts/uv_migration_backup.py
  why: Backup and rollback capability for safe migration
```

### Current Codebase Analysis - 32 Poetry Integration Points

From comprehensive analysis, Poetry is used in:

**Core Configuration:**
- `pyproject.toml` - Complete Poetry project configuration
- `poetry.lock` - 277 packages, 703KB dependency resolution

**CI/CD Pipelines (6 workflows):**
- `/.github/workflows/lint-test.yml` - 21 Poetry command references
- `/.github/workflows/build-push.yml` - Poetry version build args
- `/.github/workflows/e2e-pipeline-test.yml` - Development workflow
- Additional workflows with Poetry dependencies

**Containerization:**
- `/mcp-server/Dockerfile` - Poetry installation and dependency management
- `/Dockerfile.agents` - Uses Poetry-exported requirements

**Development Scripts:**
- `/viz/streamlit/run.sh` - Poetry install and run commands
- `/scripts/update-requirements.sh` - 5 Poetry export commands

**Python Automation:**
- `/scripts/enhance_claude_md.py` - Poetry conflict detection
- `/scripts/create_comprehensive_validation.py` - Poetry validation
- `/PRPs/scripts/prp_runner.py` - Poetry guidance and validation

### Desired Codebase Changes

```bash
# Core configuration transformation
pyproject.toml          # Poetry → UV + PEP 621/735 format
poetry.lock → uv.lock   # UV lock file generation

# CI/CD pipeline updates
.github/workflows/      # Poetry actions → UV installation
  lint-test.yml         # Poetry commands → UV equivalents
  build-push.yml        # Build args updated
  e2e-pipeline-test.yml # Development workflow

# Container updates
mcp-server/Dockerfile   # Poetry → UV installation
docker-compose.yml      # Updated build contexts

# Script updates
scripts/
  update-requirements.sh # Poetry export → UV export
viz/streamlit/run.sh    # Poetry commands → UV commands

# Documentation updates
docs/                   # Poetry instructions → UV instructions
README.md              # Setup instructions updated
CLAUDE.md              # Development commands updated
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: UV uses different command structure than Poetry
# Poetry: poetry install --with dev
# UV: uv sync --group dev

# CRITICAL: pyproject.toml format changes significantly
# Poetry: [tool.poetry.dependencies]
# UV: [project.dependencies] (PEP 621)

# CRITICAL: Dependency groups use PEP 735 format
# Poetry: [tool.poetry.group.dev.dependencies]
# UV: [dependency-groups] dev = ["package>=1.0"]

# CRITICAL: Build system configuration changes
# Poetry: requires = ["poetry-core"]
# UV: requires = ["hatchling"] (or setuptools)

# CRITICAL: Authors field format changes
# Poetry: authors = ["Name <email@example.com>"]
# UV: authors = [{name = "Name", email = "email@example.com"}]

# CRITICAL: UV resolves different versions than Poetry
# Must validate all 277 packages resolve correctly

# CRITICAL: Private repository configuration changes
# Poetry: [[tool.poetry.source]]
# UV: [[tool.uv.index]]

# GOTCHA: CI/CD caching strategies need updates for UV
# UV uses different cache directories than Poetry

# GOTCHA: Docker builds need UV-compatible base images
# Some containers may need pip fallback during transition
```

## Implementation Blueprint

### Data Models and Structure

The migration maintains all existing data models while transforming configuration format:

```yaml
# Dependency Groups Mapping (preserve all 6 groups)
Poetry Groups → UV Groups:
  [tool.poetry.dependencies] → [project.dependencies]
  [tool.poetry.group.dev.dependencies] → [dependency-groups] dev
  [tool.poetry.group.jupyter.dependencies] → [dependency-groups] jupyter
  [tool.poetry.group.datahub.dependencies] → [dependency-groups] datahub
  [tool.poetry.group.server.dependencies] → [dependency-groups] server
  [tool.poetry.group.viz.dependencies] → [dependency-groups] viz
  [tool.poetry.group.meltano.dependencies] → [dependency-groups] meltano

# Command Mapping (update all scripts)
Poetry Commands → UV Commands:
  poetry install → uv sync
  poetry install --with GROUP → uv sync --group GROUP
  poetry install --only GROUP → uv sync --only-group GROUP
  poetry add PACKAGE → uv add PACKAGE
  poetry export → uv export
  poetry run COMMAND → uv run COMMAND
```

### List of Tasks to be Completed

```yaml
Task 1 - Pre-Migration Backup and Validation:
CREATE comprehensive backup using scripts/uv_migration_backup.py:
  - BACKUP current Poetry environment state
  - DOCUMENT all Poetry command usage patterns
  - VALIDATE current environment functionality
  - CREATE rollback checkpoint

Task 2 - Core Configuration Migration:
TRANSFORM pyproject.toml:
  - REPLACE [tool.poetry] section with [project] (PEP 621)
  - CONVERT dependency groups to [dependency-groups] format (PEP 735)
  - UPDATE build-system to hatchling or setuptools
  - PRESERVE all tool configurations (ruff, black, isort, sqlfluff)
  - MIGRATE authors field to structured format

Task 3 - Automated Migration Execution:
RUN automated migration tool:
  - EXECUTE: uvx migrate-to-uv
  - VALIDATE pyproject.toml transformation
  - GENERATE uv.lock from poetry.lock
  - VERIFY all 277 packages resolve correctly

Task 4 - Development Script Updates:
MODIFY scripts/update-requirements.sh:
  - REPLACE poetry export commands with uv export
  - UPDATE all 5 export commands for different groups
  - PRESERVE existing file output structure

MODIFY viz/streamlit/run.sh:
  - REPLACE poetry install --with viz with uv sync --group viz
  - REPLACE poetry run streamlit with uv run streamlit
  - PRESERVE existing functionality

Task 5 - CI/CD Pipeline Migration:
MODIFY .github/workflows/lint-test.yml:
  - REPLACE snok/install-poetry action with UV installation
  - UPDATE cache configuration for UV
  - REPLACE poetry install commands with uv sync
  - REPLACE poetry run commands with uv run
  - PRESERVE all existing test workflows

MODIFY .github/workflows/build-push.yml:
  - REMOVE Poetry version build args
  - UPDATE Docker build context for UV
  - PRESERVE matrix build strategy

MODIFY .github/workflows/e2e-pipeline-test.yml:
  - REPLACE Poetry installation with UV setup
  - UPDATE development workflow commands
  - PRESERVE end-to-end testing logic

Task 6 - Container Migration:
MODIFY mcp-server/Dockerfile:
  - REPLACE Poetry installation with UV installation
  - UPDATE dependency installation commands
  - REPLACE poetry install --no-dev --with server with uv sync --only-group server
  - PRESERVE container functionality

Task 7 - Python Script Updates:
MODIFY scripts/enhance_claude_md.py:
  - UPDATE Poetry conflict detection patterns
  - ADD UV pattern recognition
  - PRESERVE existing functionality

MODIFY scripts/create_comprehensive_validation.py:
  - REPLACE Poetry validation with UV validation
  - ADD UV health checks
  - PRESERVE validation framework

MODIFY PRPs/scripts/prp_runner.py:
  - UPDATE Poetry guidance to UV guidance
  - REPLACE Poetry validation commands with UV commands
  - PRESERVE PRP execution workflow

Task 8 - Environment Testing and Validation:
EXECUTE comprehensive validation using scripts/uv_migration_validator.py:
  - VALIDATE environment equivalence
  - CHECK dependency resolution accuracy
  - VERIFY development workflow integrity
  - BENCHMARK performance improvements

Task 9 - Documentation Updates:
UPDATE README.md:
  - REPLACE Poetry setup instructions with UV instructions
  - UPDATE development command examples
  - PRESERVE project structure documentation

UPDATE CLAUDE.md:
  - REPLACE Poetry command references with UV equivalents
  - UPDATE development workflow instructions
  - PRESERVE coding standards and guidelines

UPDATE docs/ files:
  - FIND all Poetry references in documentation
  - REPLACE with UV equivalents
  - PRESERVE setup and usage instructions
```

### Integration Points

```yaml
BUILD_SYSTEM:
  - change: "Replace poetry-core with hatchling"
  - location: "pyproject.toml [build-system] section"
  - pattern: 'requires = ["hatchling"]'

DEPENDENCY_RESOLUTION:
  - validation: "Verify all 277 packages resolve with UV"
  - command: "uv lock --check"
  - fallback: "Manual dependency review for conflicts"

CI_CACHE:
  - change: "Update GitHub Actions cache paths"
  - old_pattern: "~/.cache/pypoetry"
  - new_pattern: "~/.cache/uv"

ENVIRONMENT_VARIABLES:
  - remove: "POETRY_* environment variables"
  - add: "UV_* environment variables if needed"
  - preserve: "Project-specific environment configuration"

PERFORMANCE_MONITORING:
  - add: "UV performance benchmarking"
  - compare: "Installation speed vs Poetry baseline"
  - validate: "10-100x improvement achieved"
```

### Preserved Data Stack Patterns

All existing data stack patterns are preserved:
- Meltano ELT workflows remain unchanged
- dbt transformation pipelines continue functioning
- DuckDB operations maintain compatibility
- Airflow DAGs preserve execution logic
- Streamlit visualization components unchanged
- MCP server functionality preserved

## Validation Loop

### Level 1: Syntax & Style

```bash
# Pre-migration validation
poetry check
poetry show --tree > pre_migration_deps.txt

# Execute automated migration
uvx migrate-to-uv

# Validate pyproject.toml syntax
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Validate UV installation
uv --version
uv python list

# Expected: No syntax errors, UV properly installed
```

### Level 2: Environment Equivalence Testing

```bash
# Generate UV lock file
uv lock

# Install dependencies with UV
uv sync

# Verify environment equivalence
python scripts/uv_migration_validator.py --comprehensive

# Compare dependency trees
uv tree > post_migration_deps.txt
diff pre_migration_deps.txt post_migration_deps.txt

# Expected: All dependencies resolved, minimal differences
```

### Level 3: Development Workflow Testing

```bash
# Test dependency group installations
uv sync --group dev
uv sync --group viz
uv sync --group server
uv sync --group jupyter
uv sync --group datahub
uv sync --group meltano

# Test development commands
uv run ruff check .
uv run black --check .
uv run isort --check-only .
uv run mypy .
uv run pytest tests/ -v

# Test streamlit workflow
cd viz/streamlit && ./run.sh

# Expected: All commands execute successfully
```

### Level 4: CI/CD and Production Validation

```bash
# Test CI/CD workflow locally
act -j lint-and-test  # GitHub Actions local testing

# Test Docker builds
docker build -f mcp-server/Dockerfile .

# Performance benchmarking
python scripts/uv_migration_validator.py --benchmark

# Health monitoring setup
python scripts/uv_health_check.py --full

# Expected: CI/CD passes, Docker builds succeed, 10-100x performance improvement
```

### Level 5: Creative Validation & Monitoring

```bash
# End-to-end data stack validation
./scripts/deploy_stack.py --validate-only
./scripts/validate_pipeline.py --comprehensive

# MCP server integration testing
curl -X POST http://localhost:8003/health

# Streamlit dashboard testing
curl http://localhost:8501/health

# Performance monitoring dashboard
python scripts/uv_health_check.py --monitor --duration=24h

# Rollback capability testing (dry run)
python scripts/uv_migration_backup.py --test-rollback

# Expected: Full data stack functional, monitoring active, rollback ready
```

## Final Validation Checklist

- [ ] All 277 dependencies correctly resolved: `uv lock --check`
- [ ] No syntax errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy .`
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] CI/CD pipelines execute: GitHub Actions validation
- [ ] Docker builds succeed: `docker build` completion
- [ ] Development workflow intact: All dev commands functional
- [ ] Performance improvement verified: 10-100x faster operations
- [ ] Rollback capability tested: Backup and restore functional
- [ ] Documentation updated: All Poetry references replaced
- [ ] Health monitoring active: Continuous validation running

---

## Anti-Patterns to Avoid

- ❌ Don't delete poetry.lock before UV migration is complete
- ❌ Don't skip automated migration tool - it handles edge cases
- ❌ Don't ignore dependency resolution differences - validate thoroughly
- ❌ Don't update CI/CD without local testing first
- ❌ Don't forget to update Docker base images if needed
- ❌ Don't skip performance benchmarking - main benefit of UV
- ❌ Don't remove backup capability - essential for rollback
- ❌ Don't ignore cache configuration changes in CI/CD
- ❌ Don't assume all Poetry features have UV equivalents

## Migration Risk Mitigation

- **Comprehensive backup system** with one-click rollback
- **Automated validation scripts** for environment equivalence
- **Performance benchmarking** to verify improvements
- **Health monitoring** for ongoing validation
- **Documentation preservation** of all changes made
- **CI/CD testing** before production deployment

**Confidence Score: 9/10** - Comprehensive context, automated tools, extensive validation, and full rollback capability ensure high success probability for one-pass implementation.
