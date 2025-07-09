#!/bin/bash
# Update all requirements files from UV lock file

set -e

echo "Updating requirements files..."

# Export main dependencies
uv export --format requirements.txt --output-file requirements.txt
echo "✓ requirements.txt updated"

# Export dev dependencies
uv export --format requirements.txt --group dev --output-file requirements-dev.txt
echo "✓ requirements-dev.txt updated"

# Export server dependencies
uv export --format requirements.txt --group server --output-file requirements-server.txt
echo "✓ requirements-server.txt updated"

# Export Jupyter dependencies
uv export --format requirements.txt --group jupyter --output-file requirements-jupyter.txt
echo "✓ requirements-jupyter.txt updated"

# Export DataHub dependencies
uv export --format requirements.txt --group datahub --output-file requirements-datahub.txt
echo "✓ requirements-datahub.txt updated"

# Export visualization dependencies
uv export --format requirements.txt --group viz --output-file requirements-viz.txt
echo "✓ requirements-viz.txt updated"

# Export Meltano dependencies
uv export --format requirements.txt --group meltano --output-file requirements-meltano.txt
echo "✓ requirements-meltano.txt updated"

echo "All requirements files updated successfully!"
