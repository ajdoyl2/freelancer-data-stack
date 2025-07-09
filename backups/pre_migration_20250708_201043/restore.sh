#!/bin/bash
# Restore script for backup: pre_migration_20250708_201043
# Generated on: 20250708_201043
# Description: Before Poetry to UV migration - comprehensive backup

set -e

echo "🔄 Restoring backup: pre_migration_20250708_201043"
echo "📁 Backup path: /Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043"
echo "🎯 Target path: /Users/ajdoyle/data-stack/freelancer-data-stack"

# Change to project root
cd "/Users/ajdoyle/data-stack/freelancer-data-stack"

# Remove current virtual environment
if [ -d ".venv" ]; then
    echo "🗑️  Removing current virtual environment..."
    rm -rf .venv
fi

# Restore files

if [ -f "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/pyproject.toml" ]; then
    echo "📄 Restoring: pyproject.toml"
    cp "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/pyproject.toml" "./pyproject.toml"
fi
if [ -f "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/poetry.lock" ]; then
    echo "📄 Restoring: poetry.lock"
    cp "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/poetry.lock" "./poetry.lock"
fi
if [ -f "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/requirements.txt" ]; then
    echo "📄 Restoring: requirements.txt"
    cp "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/requirements.txt" "./requirements.txt"
fi
if [ -d "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/.pytest_cache" ]; then
    echo "📁 Restoring: .pytest_cache"
    cp -r "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/.pytest_cache" "./.pytest_cache"
fi
if [ -d "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/.mypy_cache" ]; then
    echo "📁 Restoring: .mypy_cache"
    cp -r "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/.mypy_cache" "./.mypy_cache"
fi
if [ -d "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/.ruff_cache" ]; then
    echo "📁 Restoring: .ruff_cache"
    cp -r "/Users/ajdoyle/data-stack/freelancer-data-stack/backups/pre_migration_20250708_201043/.ruff_cache" "./.ruff_cache"
fi

echo "✅ Backup restored successfully"
echo "📋 Next steps:"
echo "   1. Verify project configuration"
echo "   2. Reinstall dependencies"
echo "   3. Run tests to confirm functionality"

# Auto-install dependencies if Poetry is available
if command -v poetry &> /dev/null; then
    echo "🔧 Attempting to reinstall dependencies with Poetry..."
    poetry install
    echo "✅ Dependencies installed"
else
    echo "⚠️  Poetry not found. Install dependencies manually:"
    echo "   poetry install"
fi
