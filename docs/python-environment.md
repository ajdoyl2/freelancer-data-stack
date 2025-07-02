# Python Environment Management

This project uses a comprehensive Python environment management setup with `pyenv`, `direnv`, and `poetry` for reproducible and isolated development environments.

## Components

### 1. Pyenv + Python 3.11.x Global

- **Python Version**: 3.11.13 (set as global default)
- **Installation**: Managed via `pyenv`
- **Verification**: `python --version` should show `Python 3.11.13`

### 2. Direnv Integration

- **Purpose**: Automatic environment activation when entering directories
- **Configuration**: `.envrc` files in project root and subdirectories
- **Features**:
  - Automatic Poetry virtual environment activation
  - Environment variable loading from `.env` files
  - Directory-specific configurations

### 3. Poetry Dependency Management

- **Configuration**: `pyproject.toml` with dependency groups
- **Dependency Groups**:
  - `dev`: Development tools (ruff, black, isort, sqlfluff, pre-commit)
  - `airflow`: Apache Airflow and related packages
  - `jupyter`: Jupyter Lab and notebook dependencies
  - `datahub`: DataHub client and tools

### 4. Requirements Lock Files

Generated from Poetry lock file for Docker image compatibility:

- `requirements.txt` - Main dependencies
- `requirements-dev.txt` - Development dependencies
- `requirements-airflow.txt` - Airflow-specific dependencies
- `requirements-jupyter.txt` - Jupyter dependencies
- `requirements-datahub.txt` - DataHub dependencies

Update with: `./scripts/update-requirements.sh`

### 5. Pre-commit Hooks

Automatically run code quality checks on commit:

- **ruff**: Fast Python linter and formatter
- **black**: Code formatter
- **isort**: Import sorter
- **sqlfluff**: SQL linter and formatter
- **mypy**: Static type checker

## Quick Start

1. **Initial Setup**:
   ```bash
   # Install dependencies
   poetry install --with dev

   # Install pre-commit hooks
   poetry run pre-commit install

   # Allow direnv
   direnv allow
   ```

2. **Working with Dependencies**:
   ```bash
   # Add a new dependency
   poetry add requests

   # Add a development dependency
   poetry add --group dev pytest

   # Update requirements files
   ./scripts/update-requirements.sh
   ```

3. **Code Quality**:
   ```bash
   # Run linters manually
   ruff check .
   black --check .
   isort --check-only .

   # Format code
   ruff format .
   black .
   isort .

   # Run pre-commit on all files
   pre-commit run --all-files
   ```

## Directory-Specific Environments

### DAGs (Airflow)
- **Location**: `dags/.envrc`
- **Features**: Airflow-specific environment variables
- **Activation**: Automatic when entering `dags/` directory

### Streamlit (Visualization)
- **Location**: `viz/streamlit/.envrc`
- **Features**: Streamlit-specific configuration
- **Activation**: Automatic when entering `viz/streamlit/` directory

## Tool Configuration

### Ruff
- **Target**: Python 3.11
- **Line Length**: 88 characters
- **Rules**: E, W, F, I, B, C4, UP
- **Config**: `[tool.ruff]` in `pyproject.toml`

### Black
- **Target**: Python 3.11
- **Line Length**: 88 characters
- **Config**: `[tool.black]` in `pyproject.toml`

### isort
- **Profile**: Black-compatible
- **Config**: `[tool.isort]` in `pyproject.toml`

### SQLFluff
- **Dialect**: PostgreSQL
- **Line Length**: 88 characters
- **Config**: `[tool.sqlfluff]` in `pyproject.toml`

## Troubleshooting

### Poetry Virtual Environment Issues
```bash
# Check current environment
poetry env info

# List all environments
poetry env list

# Remove and recreate environment
poetry env remove python
poetry install
```

### Direnv Not Loading
```bash
# Allow current directory
direnv allow

# Check status
direnv status

# Reload configuration
direnv reload
```

### Pre-commit Hook Failures
```bash
# Skip hooks temporarily
git commit --no-verify

# Update hook versions
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install
```
