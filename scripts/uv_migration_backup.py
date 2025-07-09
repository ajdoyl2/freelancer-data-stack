#!/usr/bin/env python3
"""
UV Migration Backup and Rollback Script
Comprehensive backup and rollback for Poetry to UV migration

This script provides backup creation, restoration, and rollback
capabilities for Poetry to UV migration, ensuring safe migration
with ability to revert if needed.
"""

import json
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import click


@dataclass
class BackupMetadata:
    """Metadata for backup"""

    timestamp: str
    backup_id: str
    project_root: str
    migration_type: str  # "pre_migration", "post_migration", "rollback"
    files_backed_up: list[str]
    directories_backed_up: list[str]
    environment_info: dict[str, Any]
    description: str


class UVMigrationBackup:
    """Backup and rollback manager for UV migration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backups_dir = project_root / "backups"
        self.backups_dir.mkdir(exist_ok=True)

    def get_environment_info(self) -> dict[str, Any]:
        """Get current environment information"""
        env_info: dict[str, Any] = {
            "python_version": None,
            "poetry_version": None,
            "uv_version": None,
            "pip_version": None,
            "virtualenv_path": None,
            "installed_packages": [],
        }

        # Get Python version
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                env_info["python_version"] = result.stdout.strip()
        except Exception:
            pass

        # Get Poetry version
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                env_info["poetry_version"] = result.stdout.strip()
        except Exception:
            pass

        # Get UV version
        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                env_info["uv_version"] = result.stdout.strip()
        except Exception:
            pass

        # Get pip version
        try:
            result = subprocess.run(
                ["pip", "--version"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                env_info["pip_version"] = result.stdout.strip()
        except Exception:
            pass

        # Get virtual environment info
        venv_path = self.project_root / ".venv"
        if venv_path.exists():
            env_info["virtualenv_path"] = str(venv_path)

        # Get installed packages
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                env_info["installed_packages"] = json.loads(result.stdout)
        except Exception:
            pass

        return env_info

    def create_backup(self, migration_type: str, description: str = "") -> str:
        """Create comprehensive backup"""

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_id = f"{migration_type}_{timestamp}"
        backup_path = self.backups_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)

        print(f"📦 Creating backup: {backup_id}")

        # Files to backup
        files_to_backup = [
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
            "requirements.txt",
            "requirements-dev.txt",
            ".python-version",
            "Pipfile",
            "Pipfile.lock",
            "setup.py",
            "setup.cfg",
            "environment.yml",
            "conda-environment.yml",
        ]

        # Directories to backup
        directories_to_backup = [
            ".venv",
            ".conda",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        ]

        backed_up_files = []
        backed_up_directories = []

        # Backup files
        for file_name in files_to_backup:
            file_path = self.project_root / file_name
            if file_path.exists():
                backup_file_path = backup_path / file_name
                shutil.copy2(file_path, backup_file_path)
                backed_up_files.append(file_name)
                print(f"   📄 Backed up: {file_name}")

        # Backup directories
        for dir_name in directories_to_backup:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                backup_dir_path = backup_path / dir_name
                shutil.copytree(dir_path, backup_dir_path, dirs_exist_ok=True)
                backed_up_directories.append(dir_name)
                print(f"   📁 Backed up: {dir_name}")

        # Create package snapshots
        self._create_package_snapshots(backup_path)

        # Get environment info
        env_info = self.get_environment_info()

        # Create backup metadata
        metadata = BackupMetadata(
            timestamp=timestamp,
            backup_id=backup_id,
            project_root=str(self.project_root),
            migration_type=migration_type,
            files_backed_up=backed_up_files,
            directories_backed_up=backed_up_directories,
            environment_info=env_info,
            description=description,
        )

        # Save metadata
        metadata_path = backup_path / "backup_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(asdict(metadata), f, indent=2)

        # Create restore script
        self._create_restore_script(backup_path, metadata)

        print(f"✅ Backup created: {backup_path}")
        return backup_id

    def _create_package_snapshots(self, backup_path: Path) -> None:
        """Create package snapshots for different package managers"""

        # Poetry snapshot
        try:
            result = subprocess.run(
                ["poetry", "show", "--tree"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                with open(backup_path / "poetry_packages.txt", "w") as f:
                    f.write(result.stdout)
                print("   📊 Created Poetry package snapshot")
        except Exception:
            pass

        # UV snapshot
        try:
            result = subprocess.run(
                ["uv", "pip", "list"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                with open(backup_path / "uv_packages.txt", "w") as f:
                    f.write(result.stdout)
                print("   📊 Created UV package snapshot")
        except Exception:
            pass

        # Pip snapshot
        try:
            result = subprocess.run(
                ["pip", "freeze"], capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                with open(backup_path / "pip_packages.txt", "w") as f:
                    f.write(result.stdout)
                print("   📊 Created pip package snapshot")
        except Exception:
            pass

    def _create_restore_script(
        self, backup_path: Path, metadata: BackupMetadata
    ) -> None:
        """Create restore script for this backup"""

        script_content = f"""#!/bin/bash
# Restore script for backup: {metadata.backup_id}
# Generated on: {metadata.timestamp}
# Description: {metadata.description}

set -e

echo "🔄 Restoring backup: {metadata.backup_id}"
echo "📁 Backup path: {backup_path}"
echo "🎯 Target path: {metadata.project_root}"

# Change to project root
cd "{metadata.project_root}"

# Remove current virtual environment
if [ -d ".venv" ]; then
    echo "🗑️  Removing current virtual environment..."
    rm -rf .venv
fi

# Restore files
"""

        for file_name in metadata.files_backed_up:
            script_content += f"""
if [ -f "{backup_path}/{file_name}" ]; then
    echo "📄 Restoring: {file_name}"
    cp "{backup_path}/{file_name}" "./{file_name}"
fi"""

        for dir_name in metadata.directories_backed_up:
            script_content += f"""
if [ -d "{backup_path}/{dir_name}" ]; then
    echo "📁 Restoring: {dir_name}"
    cp -r "{backup_path}/{dir_name}" "./{dir_name}"
fi"""

        script_content += """

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
"""

        script_path = backup_path / "restore.sh"
        with open(script_path, "w") as f:
            f.write(script_content)

        # Make script executable
        script_path.chmod(0o755)
        print(f"   📜 Created restore script: {script_path}")

    def list_backups(self) -> list[BackupMetadata]:
        """List all available backups"""
        backups = []

        for backup_dir in self.backups_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "backup_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata_dict = json.load(f)
                            metadata = BackupMetadata(**metadata_dict)
                            backups.append(metadata)
                    except Exception as e:
                        print(f"⚠️  Failed to read backup metadata: {backup_dir} - {e}")

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups

    def restore_backup(self, backup_id: str) -> bool:
        """Restore from backup"""
        backup_path = self.backups_dir / backup_id

        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_id}")
            return False

        metadata_file = backup_path / "backup_metadata.json"
        if not metadata_file.exists():
            print(f"❌ Backup metadata not found: {backup_id}")
            return False

        # Load metadata
        with open(metadata_file) as f:
            metadata_dict = json.load(f)
            metadata = BackupMetadata(**metadata_dict)

        print(f"🔄 Restoring backup: {backup_id}")
        print(f"📅 Created: {metadata.timestamp}")
        print(f"📝 Description: {metadata.description}")

        # Confirm restoration
        confirm = input("Are you sure you want to restore this backup? (y/N): ")
        if confirm.lower() not in ["y", "yes"]:
            print("❌ Restore cancelled")
            return False

        # Create pre-restore backup
        pre_restore_backup_id = self.create_backup(
            "pre_restore", f"Before restoring {backup_id}"
        )
        print(f"🔄 Created pre-restore backup: {pre_restore_backup_id}")

        try:
            # Remove current virtual environment
            venv_path = self.project_root / ".venv"
            if venv_path.exists():
                print("🗑️  Removing current virtual environment...")
                shutil.rmtree(venv_path)

            # Restore files
            for file_name in metadata.files_backed_up:
                source_path = backup_path / file_name
                target_path = self.project_root / file_name

                if source_path.exists():
                    shutil.copy2(source_path, target_path)
                    print(f"📄 Restored: {file_name}")

            # Restore directories
            for dir_name in metadata.directories_backed_up:
                source_path = backup_path / dir_name
                target_path = self.project_root / dir_name

                if source_path.exists():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                    print(f"📁 Restored: {dir_name}")

            print("✅ Backup restored successfully")
            return True

        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False

    def rollback_to_poetry(self) -> bool:
        """Rollback from UV to Poetry"""

        print("🔄 Rolling back to Poetry...")

        # Find the most recent pre-migration backup
        backups = self.list_backups()
        pre_migration_backup = None

        for backup in backups:
            if backup.migration_type == "pre_migration":
                pre_migration_backup = backup
                break

        if not pre_migration_backup:
            print("❌ No pre-migration backup found")
            print("💡 Create a manual backup and restore Poetry configuration")
            return False

        print(f"📦 Found pre-migration backup: {pre_migration_backup.backup_id}")

        # Restore the backup
        if self.restore_backup(pre_migration_backup.backup_id):
            print("✅ Successfully rolled back to Poetry")

            # Verify Poetry is working
            try:
                result = subprocess.run(
                    ["poetry", "check"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if result.returncode == 0:
                    print("✅ Poetry configuration is valid")
                else:
                    print("⚠️  Poetry configuration may need manual adjustment")
                    print(f"   Error: {result.stderr}")
            except Exception as e:
                print(f"⚠️  Could not verify Poetry installation: {e}")

            return True
        else:
            print("❌ Rollback failed")
            return False

    def cleanup_old_backups(self, keep_count: int = 5) -> None:
        """Clean up old backups, keeping only the most recent ones"""

        backups = self.list_backups()

        if len(backups) <= keep_count:
            print(
                f"📦 No cleanup needed. {len(backups)} backups (keeping {keep_count})"
            )
            return

        # Remove old backups
        backups_to_remove = backups[keep_count:]

        for backup in backups_to_remove:
            backup_path = self.backups_dir / backup.backup_id
            if backup_path.exists():
                shutil.rmtree(backup_path)
                print(f"🗑️  Removed old backup: {backup.backup_id}")

        print(f"✅ Cleaned up {len(backups_to_remove)} old backups")


@click.command()
@click.option(
    "--create", type=str, help="Create backup (pre_migration|post_migration|manual)"
)
@click.option("--description", type=str, help="Backup description")
@click.option("--list", "list_backups", is_flag=True, help="List available backups")
@click.option("--restore", type=str, help="Restore backup by ID")
@click.option("--rollback", is_flag=True, help="Rollback to Poetry")
@click.option("--cleanup", is_flag=True, help="Clean up old backups")
@click.option(
    "--keep", type=int, default=5, help="Number of backups to keep during cleanup"
)
def main(
    create: str,
    description: str,
    list_backups: bool,
    restore: str,
    rollback: bool,
    cleanup: bool,
    keep: int,
):
    """UV Migration Backup and Rollback Tool"""

    project_root = Path.cwd()
    backup_manager = UVMigrationBackup(project_root)

    if create:
        if create not in ["pre_migration", "post_migration", "manual"]:
            print(
                "❌ Invalid backup type. Use: pre_migration, post_migration, or manual"
            )
            return

        backup_id = backup_manager.create_backup(create, description or "")
        print(f"📦 Backup created: {backup_id}")

    elif list_backups:
        backups = backup_manager.list_backups()

        if not backups:
            print("📦 No backups found")
            return

        print(f"📦 Found {len(backups)} backups:")
        print()

        for backup in backups:
            print(f"🔸 **{backup.backup_id}**")
            print(f"   📅 Created: {backup.timestamp}")
            print(f"   🏷️  Type: {backup.migration_type}")
            print(f"   📝 Description: {backup.description}")
            print(f"   📄 Files: {len(backup.files_backed_up)}")
            print(f"   📁 Directories: {len(backup.directories_backed_up)}")
            print()

    elif restore:
        success = backup_manager.restore_backup(restore)
        if success:
            print("✅ Restore completed successfully")
        else:
            print("❌ Restore failed")

    elif rollback:
        success = backup_manager.rollback_to_poetry()
        if success:
            print("✅ Rollback completed successfully")
            print("📋 Next steps:")
            print("   1. Run: poetry install")
            print("   2. Verify: poetry check")
            print("   3. Test: poetry run python --version")
        else:
            print("❌ Rollback failed")

    elif cleanup:
        backup_manager.cleanup_old_backups(keep)

    else:
        print("🔧 UV Migration Backup and Rollback Tool")
        print("Usage: python scripts/uv_migration_backup.py [OPTIONS]")
        print()
        print("Options:")
        print(
            "  --create TYPE         Create backup (pre_migration|post_migration|manual)"
        )
        print("  --description TEXT    Backup description")
        print("  --list               List available backups")
        print("  --restore ID         Restore backup by ID")
        print("  --rollback           Rollback to Poetry")
        print("  --cleanup            Clean up old backups")
        print("  --keep N             Number of backups to keep (default: 5)")
        print()
        print("Examples:")
        print(
            "  python scripts/uv_migration_backup.py --create pre_migration --description 'Before UV migration'"
        )
        print("  python scripts/uv_migration_backup.py --list")
        print(
            "  python scripts/uv_migration_backup.py --restore pre_migration_20240101_120000"
        )
        print("  python scripts/uv_migration_backup.py --rollback")


if __name__ == "__main__":
    main()
