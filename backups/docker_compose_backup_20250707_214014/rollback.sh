#!/bin/bash
# Rollback Script for Docker Compose Credential Migration
# Created: 2025-07-07T21:40:14.324678
# Backup ID: docker_compose_backup_20250707_214014

set -e  # Exit on any error

echo "🔄 Rolling back Docker Compose configuration..."

# Define project root and backup directory
PROJECT_ROOT="/Users/ajdoyle/data-stack/freelancer-data-stack"
BACKUP_DIR="/Users/ajdoyle/data-stack/freelancer-data-stack/backups/docker_compose_backup_20250707_214014"

# Function to restore file
restore_file() {
    local file_name="$1"
    if [ -f "$BACKUP_DIR/$file_name" ]; then
        echo "📁 Restoring $file_name..."
        cp "$BACKUP_DIR/$file_name" "$PROJECT_ROOT/$file_name"
        echo "✅ Restored: $file_name"
    else
        echo "⚠️  Backup file not found: $file_name"
    fi
}

# Stop Docker services first
echo "🛑 Stopping Docker services..."
cd "$PROJECT_ROOT"
docker-compose down || true

# Restore configuration files
restore_file "docker-compose.yml"
restore_file "docker-compose.agents.yml"
restore_file ".env"
restore_file ".gitignore"
restore_file ".env.example"

# Validate restored configuration
echo "🔍 Validating restored configuration..."
docker-compose config --quiet

echo "✅ Rollback completed successfully!"
echo "💡 You can now restart services with: docker-compose up -d"
