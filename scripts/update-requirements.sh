#!/bin/bash
# Update all requirements files from Poetry lock file

set -e

echo "Updating requirements files..."

# Export main dependencies
poetry export -f requirements.txt --output requirements.txt
echo "✓ requirements.txt updated"

# Export dev dependencies
poetry export -f requirements.txt --with dev --output requirements-dev.txt
echo "✓ requirements-dev.txt updated"

# Export Airflow dependencies
poetry export -f requirements.txt --only airflow --output requirements-airflow.txt
echo "✓ requirements-airflow.txt updated"

# Export Jupyter dependencies
poetry export -f requirements.txt --only jupyter --output requirements-jupyter.txt
echo "✓ requirements-jupyter.txt updated"

# Export DataHub dependencies
poetry export -f requirements.txt --only datahub --output requirements-datahub.txt
echo "✓ requirements-datahub.txt updated"

echo "All requirements files updated successfully!"
