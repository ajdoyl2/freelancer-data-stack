#!/usr/bin/env python3
"""
Configuration Backup and Rollback Script

Creates backups of current Docker Compose configuration and provides rollback
capabilities for safe credential migration.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import click
from pydantic import BaseModel, Field


class BackupConfig(BaseModel):
    """Configuration for backup operations."""

    project_root: Path = Field(default_factory=lambda: Path.cwd())
    backup_dir: str = Field(default="backups")
    timestamp_format: str = Field(default="%Y%m%d_%H%M%S")
    create_rollback_script: bool = Field(default=True)


class BackupMetadata(BaseModel):
    """Metadata for backup operations."""

    backup_timestamp: str
    backup_id: str
    files_backed_up: list[str] = Field(default_factory=list)
    original_credentials: dict[str, str] = Field(default_factory=dict)
    backup_directory: str
    rollback_script_path: str | None = None


class ConfigurationBackup:
    """Configuration backup and rollback manager."""

    def __init__(self, config: BackupConfig):
        self.config = config
        self.backup_metadata: BackupMetadata | None = None

        # Files to backup
        self.files_to_backup = [
            "docker-compose.yml",
            "docker-compose.agents.yml",
            ".env",
            ".gitignore",
        ]

        # Optional files that might exist
        self.optional_files = [".env.example", ".env.local", ".env.production"]

    def create_backup_directory(self) -> Path:
        """
        Create timestamped backup directory.

        Returns:
            Path: Backup directory path
        """
        timestamp = datetime.now().strftime(self.config.timestamp_format)
        backup_id = f"docker_compose_backup_{timestamp}"

        backup_dir = self.config.project_root / self.config.backup_dir / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        return backup_dir

    def extract_current_credentials(self) -> dict[str, str]:
        """
        Extract current credential patterns from docker-compose.yml.

        Returns:
            Dict[str, str]: Current credential mapping
        """
        credentials: dict[str, str] = {}

        compose_file = self.config.project_root / "docker-compose.yml"

        if not compose_file.exists():
            print(f"⚠️  docker-compose.yml not found at {compose_file}")
            return credentials

        try:
            with open(compose_file) as f:
                content = f.read()

            # Extract current credential patterns
            credential_patterns = [
                ("POSTGRES_USER", "postgres"),
                ("POSTGRES_PASSWORD", "${POSTGRES_PASSWORD:-postgres}"),
                ("AIRFLOW_USERNAME", "${AIRFLOW_USERNAME:-admin}"),
                ("AIRFLOW_PASSWORD", "${AIRFLOW_PASSWORD:-admin}"),
                ("GF_SECURITY_ADMIN_USER", "admin"),
                ("GF_SECURITY_ADMIN_PASSWORD", "${GRAFANA_PASSWORD:-admin}"),
                ("NEO4J_AUTH", "neo4j/${NEO4J_PASSWORD:-datahub}"),
                ("NEO4J_USERNAME", "neo4j"),
                ("DATAHUB_SECRET", "${DATAHUB_SECRET:-YouMustChangeThisSecretKey}"),
                ("MB_DB_USER", "postgres"),
                ("MB_ADMIN_EMAIL", "admin@datastack.local"),
                ("SECRET_KEY", "${SECRET_KEY:-your-secret-key-here}"),
            ]

            for var_name, pattern in credential_patterns:
                if pattern in content:
                    credentials[var_name] = pattern

        except Exception as e:
            print(f"⚠️  Error extracting credentials: {e}")

        return credentials

    def backup_files(self, backup_dir: Path) -> list[str]:
        """
        Backup configuration files.

        Args:
            backup_dir: Backup directory path

        Returns:
            List[str]: List of backed up files
        """
        backed_up_files = []

        # Backup required files
        for file_name in self.files_to_backup:
            source_file = self.config.project_root / file_name
            if source_file.exists():
                dest_file = backup_dir / file_name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                backed_up_files.append(file_name)
                print(f"✅ Backed up: {file_name}")
            else:
                print(f"⚠️  File not found: {file_name}")

        # Backup optional files
        for file_name in self.optional_files:
            source_file = self.config.project_root / file_name
            if source_file.exists():
                dest_file = backup_dir / file_name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                backed_up_files.append(file_name)
                print(f"✅ Backed up (optional): {file_name}")

        return backed_up_files

    def create_rollback_script(self, backup_dir: Path, metadata: BackupMetadata) -> str:
        """
        Create rollback script for easy restoration.

        Args:
            backup_dir: Backup directory path
            metadata: Backup metadata

        Returns:
            str: Rollback script path
        """
        rollback_script_path = backup_dir / "rollback.sh"

        # Create rollback script content
        rollback_content = [
            "#!/bin/bash",
            "# Rollback Script for Docker Compose Credential Migration",
            f"# Created: {metadata.backup_timestamp}",
            f"# Backup ID: {metadata.backup_id}",
            "",
            "set -e  # Exit on any error",
            "",
            'echo "🔄 Rolling back Docker Compose configuration..."',
            "",
            "# Define project root and backup directory",
            f'PROJECT_ROOT="{self.config.project_root.absolute()}"',
            f'BACKUP_DIR="{backup_dir.absolute()}"',
            "",
            "# Function to restore file",
            "restore_file() {",
            '    local file_name="$1"',
            '    if [ -f "$BACKUP_DIR/$file_name" ]; then',
            '        echo "📁 Restoring $file_name..."',
            '        cp "$BACKUP_DIR/$file_name" "$PROJECT_ROOT/$file_name"',
            '        echo "✅ Restored: $file_name"',
            "    else",
            '        echo "⚠️  Backup file not found: $file_name"',
            "    fi",
            "}",
            "",
            "# Stop Docker services first",
            'echo "🛑 Stopping Docker services..."',
            'cd "$PROJECT_ROOT"',
            "docker-compose down || true",
            "",
            "# Restore configuration files",
        ]

        # Add restore commands for each backed up file
        for file_name in metadata.files_backed_up:
            rollback_content.append(f'restore_file "{file_name}"')

        rollback_content.extend(
            [
                "",
                "# Validate restored configuration",
                'echo "🔍 Validating restored configuration..."',
                "docker-compose config --quiet",
                "",
                'echo "✅ Rollback completed successfully!"',
                'echo "💡 You can now restart services with: docker-compose up -d"',
                "",
            ]
        )

        # Write rollback script
        with open(rollback_script_path, "w") as f:
            f.write("\n".join(rollback_content))

        # Make script executable
        rollback_script_path.chmod(0o755)

        return str(rollback_script_path)

    def save_metadata(self, backup_dir: Path, metadata: BackupMetadata) -> None:
        """
        Save backup metadata as JSON.

        Args:
            backup_dir: Backup directory path
            metadata: Backup metadata to save
        """
        metadata_file = backup_dir / "backup_metadata.json"

        with open(metadata_file, "w") as f:
            json.dump(metadata.dict(), f, indent=2, default=str)

        print(f"📋 Saved backup metadata: {metadata_file}")

    def create_backup(self) -> BackupMetadata:
        """
        Create complete backup of current configuration.

        Returns:
            BackupMetadata: Backup operation metadata
        """
        print("🔄 Creating backup of current Docker Compose configuration...")

        # Create backup directory
        backup_dir = self.create_backup_directory()
        backup_id = backup_dir.name

        # Extract current credentials
        current_credentials = self.extract_current_credentials()

        # Backup files
        backed_up_files = self.backup_files(backup_dir)

        # Create metadata
        metadata = BackupMetadata(
            backup_timestamp=datetime.now().isoformat(),
            backup_id=backup_id,
            files_backed_up=backed_up_files,
            original_credentials=current_credentials,
            backup_directory=str(backup_dir),
        )

        # Create rollback script
        if self.config.create_rollback_script:
            rollback_script_path = self.create_rollback_script(backup_dir, metadata)
            metadata.rollback_script_path = rollback_script_path
            print(f"📜 Created rollback script: {rollback_script_path}")

        # Save metadata
        self.save_metadata(backup_dir, metadata)

        self.backup_metadata = metadata

        print("\n✅ Backup completed successfully!")
        print(f"📁 Backup location: {backup_dir}")
        print(f"🆔 Backup ID: {backup_id}")

        return metadata

    def list_backups(self) -> list[Path]:
        """
        List all available backups.

        Returns:
            List[Path]: List of backup directories
        """
        backup_base_dir = self.config.project_root / self.config.backup_dir

        if not backup_base_dir.exists():
            return []

        backups = []
        for item in backup_base_dir.iterdir():
            if item.is_dir() and item.name.startswith("docker_compose_backup_"):
                backups.append(item)

        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return backups

    def restore_from_backup(self, backup_id: str) -> bool:
        """
        Restore configuration from specific backup.

        Args:
            backup_id: Backup ID to restore from

        Returns:
            bool: True if restoration successful
        """
        backup_dir = self.config.project_root / self.config.backup_dir / backup_id

        if not backup_dir.exists():
            print(f"❌ Backup not found: {backup_id}")
            return False

        metadata_file = backup_dir / "backup_metadata.json"
        if not metadata_file.exists():
            print(f"❌ Backup metadata not found: {metadata_file}")
            return False

        try:
            # Load metadata
            with open(metadata_file) as f:
                metadata_dict = json.load(f)

            metadata = BackupMetadata(**metadata_dict)

            print(f"🔄 Restoring from backup: {backup_id}")
            print(f"📅 Created: {metadata.backup_timestamp}")

            # Restore files
            for file_name in metadata.files_backed_up:
                source_file = backup_dir / file_name
                dest_file = self.config.project_root / file_name

                if source_file.exists():
                    shutil.copy2(source_file, dest_file)
                    print(f"✅ Restored: {file_name}")
                else:
                    print(f"⚠️  Backup file missing: {file_name}")

            print("✅ Restoration completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error during restoration: {e}")
            return False


@click.command()
@click.option("--backup-dir", "-d", default="backups", help="Backup directory name")
@click.option("--list-backups", "-l", is_flag=True, help="List available backups")
@click.option("--restore", "-r", help="Restore from backup ID")
@click.option(
    "--force", "-f", is_flag=True, help="Force operation without confirmation"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def backup_config(
    backup_dir: str, list_backups: bool, restore: str, force: bool, verbose: bool
):
    """Backup and restore Docker Compose configuration."""

    config = BackupConfig(backup_dir=backup_dir)
    backup_manager = ConfigurationBackup(config)

    if list_backups:
        # List available backups
        backups = backup_manager.list_backups()

        if not backups:
            print("📭 No backups found.")
            return

        print(f"📋 Available backups ({len(backups)}):")
        for i, backup_path in enumerate(backups, 1):
            metadata_file = backup_path / "backup_metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)

                    timestamp = metadata.get("backup_timestamp", "Unknown")
                    files_count = len(metadata.get("files_backed_up", []))

                    print(f"  {i}. {backup_path.name}")
                    print(f"     📅 Created: {timestamp}")
                    print(f"     📁 Files: {files_count}")
                    print()
                except Exception:
                    print(f"  {i}. {backup_path.name} (metadata unreadable)")

        return

    if restore:
        # Restore from backup
        if not force:
            response = click.confirm(
                "⚠️  This will overwrite current configuration files. Continue?",
                default=False,
            )
            if not response:
                print("❌ Restoration cancelled.")
                return

        success = backup_manager.restore_from_backup(restore)
        if success:
            print("\n💡 Remember to restart Docker services:")
            print("   docker-compose down")
            print("   docker-compose up -d")
        sys.exit(0 if success else 1)

    # Create backup
    if not force:
        print("🔍 Current configuration will be backed up before migration.")
        response = click.confirm("Continue with backup creation?", default=True)
        if not response:
            print("❌ Backup cancelled.")
            return

    try:
        metadata = backup_manager.create_backup()

        if verbose:
            print("\n📊 Backup Summary:")
            print(f"   📁 Files backed up: {len(metadata.files_backed_up)}")
            print(f"   🔐 Credentials tracked: {len(metadata.original_credentials)}")
            print(
                f"   📜 Rollback script: {'✅' if metadata.rollback_script_path else '❌'}"
            )

        print("\n🛡️  Rollback instructions:")
        if metadata.rollback_script_path:
            print(f"   Quick rollback: bash {metadata.rollback_script_path}")
        print(f"   Manual rollback: python {__file__} --restore {metadata.backup_id}")

    except Exception as e:
        print(f"❌ Backup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    backup_config()
