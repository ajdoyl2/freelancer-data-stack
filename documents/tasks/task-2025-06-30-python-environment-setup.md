# Task: Python Environment & Dependency Management Setup

Set up Python environments & dependency management using `pyenv` + `python 3.11.x` as global, per-tool virtualenvs managed via `direnv` and `poetry`, `requirements-*.txt` lock files to mirror in Docker images, and pre-commit hooks: `ruff`, `black`, `isort`, `sqlfmt`.

## Steps

1. [x] Install and configure Python 3.11.13 via pyenv as global
2. [x] Set up Poetry for dependency management
3. [x] Configure direnv for automatic environment activation
4. [x] Create pyproject.toml with dependency groups (dev, airflow, jupyter, datahub)
5. [x] Install development tools (ruff, black, isort, sqlfluff)
6. [x] Generate requirements-*.txt lock files for Docker compatibility
7. [x] Set up pre-commit hooks configuration
8. [x] Install and configure pre-commit hooks
9. [x] Create directory-specific .envrc files
10. [x] Create scripts for updating requirements files
11. [x] Document the setup in docs/python-environment.md
12. [x] Test all tools and verify functionality

## Testing Results

- ✅ Python version: 3.11.13
- ✅ Poetry installation and virtual environment
- ✅ Direnv automatic activation
- ✅ Pre-commit hooks installed
- ✅ All development tools working:
  - ruff 0.8.6
  - black 24.10.0
  - isort 5.13.2
  - sqlfluff 3.4.1
- ✅ Requirements files generated
- ✅ Documentation created

## Files Created/Modified

### Configuration Files
- `.envrc` - Main direnv configuration
- `pyproject.toml` - Poetry configuration with tool settings
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `dags/.envrc` - Airflow-specific environment
- `viz/streamlit/.envrc` - Streamlit-specific environment

### Requirements Files
- `requirements.txt` - Main dependencies
- `requirements-dev.txt` - Development dependencies
- `requirements-airflow.txt` - Airflow dependencies
- `requirements-jupyter.txt` - Jupyter dependencies
- `requirements-datahub.txt` - DataHub dependencies

### Scripts
- `scripts/update-requirements.sh` - Update all requirements files

### Documentation
- `docs/python-environment.md` - Comprehensive setup documentation

## Notes

- Used sqlfluff instead of sqlfmt (original package was outdated)
- Configured Poetry with package-mode = false since this is a project, not a package
- Set up dependency groups for modular installation
- Created directory-specific environments for better tool isolation

## Problems/Blockers

- [x] Initial sqlfmt package version issue - resolved by switching to sqlfluff
- [x] Poetry package mode issue - resolved by setting package-mode = false
- [x] Airflow Python version compatibility - resolved by constraining Python to <3.13

---

*Date Created: 2025-06-30*
*Last Modified: 2025-06-30*
*Status: Completed*
