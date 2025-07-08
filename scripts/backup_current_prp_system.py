#!/usr/bin/env python3
"""
PRP System Backup and Rollback Script

Creates comprehensive backups of current PRP system before PRPs-agentic-eng
integration and provides rollback capabilities for safe integration.
"""

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import click
from pydantic import BaseModel, Field


class PRPBackupConfig(BaseModel):
    """Configuration for PRP backup operations."""

    project_root: Path = Field(default_factory=lambda: Path.cwd())
    backup_dir: str = Field(default="backups")
    timestamp_format: str = Field(default="%Y%m%d_%H%M%S")
    create_rollback_script: bool = Field(default=True)
    generate_checksums: bool = Field(default=True)


class PRPBackupMetadata(BaseModel):
    """Metadata for PRP backup operations."""

    backup_timestamp: str
    backup_id: str
    files_backed_up: list[str] = Field(default_factory=list)
    file_checksums: dict[str, str] = Field(default_factory=dict)
    backup_directory: str
    rollback_script_path: str | None = None
    git_commit_hash: str | None = None
    integration_purpose: str = "PRPs-agentic-eng integration"


class PRPSystemBackup:
    """PRP system backup and rollback manager."""

    def __init__(self, config: PRPBackupConfig):
        self.config = config
        self.backup_metadata: PRPBackupMetadata | None = None

        # Critical PRP files to backup
        self.critical_files = [
            "CLAUDE.md",
            "pyproject.toml",
        ]

        # Directories to backup recursively
        self.critical_directories = [
            ".claude/commands",
            "PRPs/templates",
        ]

        # Optional files that might exist
        self.optional_files = [
            ".claude/settings.local.json",
            "PRPs/README.md",
            "README.md",
        ]

    def get_git_commit_hash(self) -> str | None:
        """
        Get current git commit hash for version tracking.

        Returns:
            str | None: Current git commit hash
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.config.project_root,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def calculate_file_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of file for integrity validation.

        Args:
            file_path: Path to file

        Returns:
            str: SHA256 checksum
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"⚠️  Error calculating checksum for {file_path}: {e}")
            return ""

    def create_backup_directory(self) -> Path:
        """
        Create timestamped backup directory.

        Returns:
            Path: Backup directory path
        """
        timestamp = datetime.now().strftime(self.config.timestamp_format)
        backup_id = f"prp_integration_backup_{timestamp}"

        backup_dir = self.config.project_root / self.config.backup_dir / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        return backup_dir

    def backup_file(self, source_file: Path, backup_dir: Path) -> tuple[str, str]:
        """
        Backup individual file and calculate checksum.

        Args:
            source_file: Source file path
            backup_dir: Backup directory path

        Returns:
            tuple[str, str]: (relative_path, checksum)
        """
        relative_path = str(source_file.relative_to(self.config.project_root))
        dest_file = backup_dir / relative_path

        # Create directory structure
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file with metadata preservation
        shutil.copy2(source_file, dest_file)

        # Calculate checksum
        checksum = ""
        if self.config.generate_checksums:
            checksum = self.calculate_file_checksum(source_file)

        print(f"✅ Backed up: {relative_path}")
        return relative_path, checksum

    def backup_directory(self, source_dir: Path, backup_dir: Path) -> dict[str, str]:
        """
        Backup directory recursively.

        Args:
            source_dir: Source directory path
            backup_dir: Backup directory path

        Returns:
            dict[str, str]: Mapping of relative paths to checksums
        """
        file_checksums = {}

        if not source_dir.exists():
            print(f"⚠️  Directory not found: {source_dir}")
            return file_checksums

        # Recursively backup all files in directory
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                relative_path, checksum = self.backup_file(file_path, backup_dir)
                if checksum:
                    file_checksums[relative_path] = checksum

        return file_checksums

    def backup_files(self, backup_dir: Path) -> tuple[list[str], dict[str, str]]:
        """
        Backup all critical PRP system files.

        Args:
            backup_dir: Backup directory path

        Returns:
            tuple[list[str], dict[str, str]]: (backed_up_files, checksums)
        """
        backed_up_files = []
        file_checksums = {}

        # Backup critical files
        for file_name in self.critical_files:
            source_file = self.config.project_root / file_name
            if source_file.exists():
                relative_path, checksum = self.backup_file(source_file, backup_dir)
                backed_up_files.append(relative_path)
                if checksum:
                    file_checksums[relative_path] = checksum
            else:
                print(f"⚠️  Critical file not found: {file_name}")

        # Backup critical directories
        for dir_name in self.critical_directories:
            source_dir = self.config.project_root / dir_name
            if source_dir.exists():
                print(f"📁 Backing up directory: {dir_name}")
                dir_checksums = self.backup_directory(source_dir, backup_dir)
                file_checksums.update(dir_checksums)

                # Add directory files to backed up list
                for file_path in source_dir.rglob("*"):
                    if file_path.is_file():
                        relative_path = str(
                            file_path.relative_to(self.config.project_root)
                        )
                        backed_up_files.append(relative_path)
            else:
                print(f"⚠️  Critical directory not found: {dir_name}")

        # Backup optional files
        for file_name in self.optional_files:
            source_file = self.config.project_root / file_name
            if source_file.exists():
                relative_path, checksum = self.backup_file(source_file, backup_dir)
                backed_up_files.append(relative_path)
                if checksum:
                    file_checksums[relative_path] = checksum
                print(f"✅ Backed up (optional): {relative_path}")

        return backed_up_files, file_checksums

    def create_rollback_script(
        self, backup_dir: Path, metadata: PRPBackupMetadata
    ) -> str:
        """
        Create comprehensive rollback script for PRP system restoration.

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
            "# PRP System Rollback Script for PRPs-agentic-eng Integration",
            f"# Created: {metadata.backup_timestamp}",
            f"# Backup ID: {metadata.backup_id}",
            f"# Git Commit: {metadata.git_commit_hash or 'unknown'}",
            "",
            "set -e  # Exit on any error",
            "",
            'echo "🔄 Rolling back PRP system to pre-integration state..."',
            "",
            "# Define project root and backup directory",
            f'PROJECT_ROOT="{self.config.project_root.absolute()}"',
            f'BACKUP_DIR="{backup_dir.absolute()}"',
            "",
            "# Function to validate file integrity",
            "validate_checksum() {",
            '    local file_path="$1"',
            '    local expected_checksum="$2"',
            '    if [ -n "$expected_checksum" ]; then',
            "        local actual_checksum=$(sha256sum \"$file_path\" | cut -d' ' -f1)",
            '        if [ "$actual_checksum" != "$expected_checksum" ]; then',
            '            echo "❌ Checksum mismatch for $file_path"',
            "            return 1",
            "        fi",
            "    fi",
            "    return 0",
            "}",
            "",
            "# Function to restore file",
            "restore_file() {",
            '    local file_path="$1"',
            '    local expected_checksum="$2"',
            '    local backup_file="$BACKUP_DIR/$file_path"',
            '    local target_file="$PROJECT_ROOT/$file_path"',
            "",
            '    if [ -f "$backup_file" ]; then',
            '        echo "📁 Restoring $file_path..."',
            "",
            "        # Validate backup file integrity",
            '        if ! validate_checksum "$backup_file" "$expected_checksum"; then',
            '            echo "⚠️  Backup file integrity check failed, proceeding anyway..."',
            "        fi",
            "",
            "        # Create target directory if needed",
            '        mkdir -p "$(dirname "$target_file")"',
            "",
            "        # Restore file",
            '        cp "$backup_file" "$target_file"',
            '        echo "✅ Restored: $file_path"',
            "    else",
            '        echo "⚠️  Backup file not found: $file_path"',
            "    fi",
            "}",
            "",
            "# Validate backup integrity first",
            'echo "🔍 Validating backup integrity..."',
        ]

        # Add checksum validation for critical files
        if self.config.generate_checksums:
            rollback_content.extend(
                [
                    "",
                    "# Validate critical backup files",
                ]
            )
            for file_path, checksum in metadata.file_checksums.items():
                if checksum:
                    rollback_content.append(
                        f'validate_checksum "$BACKUP_DIR/{file_path}" "{checksum}" || exit 1'
                    )

        rollback_content.extend(
            [
                "",
                'echo "✅ Backup integrity validated"',
                "",
                "# Restore files",
                'echo "📂 Restoring PRP system files..."',
            ]
        )

        # Add restore commands for each backed up file
        for file_path in metadata.files_backed_up:
            checksum = metadata.file_checksums.get(file_path, "")
            rollback_content.append(f'restore_file "{file_path}" "{checksum}"')

        rollback_content.extend(
            [
                "",
                "# Git status check",
                'echo "📊 Checking git status..."',
                'cd "$PROJECT_ROOT"',
                "git status --porcelain",
                "",
                'echo "✅ PRP system rollback completed successfully!"',
                'echo "💡 You can now review changes with: git status"',
                'echo "🔧 To commit rollback: git add -A && git commit -m \\"Rollback PRP system to pre-integration state\\""',
                "",
            ]
        )

        # Write rollback script
        with open(rollback_script_path, "w") as f:
            f.write("\n".join(rollback_content))

        # Make script executable
        rollback_script_path.chmod(0o755)

        return str(rollback_script_path)

    def save_metadata(self, backup_dir: Path, metadata: PRPBackupMetadata) -> None:
        """
        Save backup metadata as JSON with comprehensive information.

        Args:
            backup_dir: Backup directory path
            metadata: Backup metadata to save
        """
        metadata_file = backup_dir / "backup_metadata.json"

        with open(metadata_file, "w") as f:
            json.dump(metadata.dict(), f, indent=2, default=str)

        print(f"📋 Saved backup metadata: {metadata_file}")

    def create_backup(self) -> PRPBackupMetadata:
        """
        Create complete backup of current PRP system.

        Returns:
            PRPBackupMetadata: Backup operation metadata
        """
        print(
            "🔄 Creating backup of current PRP system for PRPs-agentic-eng integration..."
        )

        # Create backup directory
        backup_dir = self.create_backup_directory()
        backup_id = backup_dir.name

        # Get git commit hash
        git_commit = self.get_git_commit_hash()

        # Backup files
        backed_up_files, file_checksums = self.backup_files(backup_dir)

        # Create metadata
        metadata = PRPBackupMetadata(
            backup_timestamp=datetime.now().isoformat(),
            backup_id=backup_id,
            files_backed_up=backed_up_files,
            file_checksums=file_checksums,
            backup_directory=str(backup_dir),
            git_commit_hash=git_commit,
        )

        # Create rollback script
        if self.config.create_rollback_script:
            rollback_script_path = self.create_rollback_script(backup_dir, metadata)
            metadata.rollback_script_path = rollback_script_path
            print(f"📜 Created rollback script: {rollback_script_path}")

        # Save metadata
        self.save_metadata(backup_dir, metadata)

        self.backup_metadata = metadata

        print("\n✅ PRP system backup completed successfully!")
        print(f"📁 Backup location: {backup_dir}")
        print(f"🆔 Backup ID: {backup_id}")
        print(f"📊 Files backed up: {len(backed_up_files)}")
        print(f"🔐 Checksums generated: {len(file_checksums)}")

        return metadata

    def list_backups(self) -> list[Path]:
        """
        List all available PRP backups.

        Returns:
            List[Path]: List of backup directories
        """
        backup_base_dir = self.config.project_root / self.config.backup_dir

        if not backup_base_dir.exists():
            return []

        backups = []
        for item in backup_base_dir.iterdir():
            if item.is_dir() and item.name.startswith("prp_integration_backup_"):
                backups.append(item)

        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return backups

    def restore_from_backup(
        self, backup_id: str, validate_checksums: bool = True
    ) -> bool:
        """
        Restore PRP system from specific backup.

        Args:
            backup_id: Backup ID to restore from
            validate_checksums: Whether to validate file checksums

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

            metadata = PRPBackupMetadata(**metadata_dict)

            print(f"🔄 Restoring PRP system from backup: {backup_id}")
            print(f"📅 Created: {metadata.backup_timestamp}")
            print(f"🔗 Git commit: {metadata.git_commit_hash or 'unknown'}")

            # Validate checksums if requested
            if validate_checksums and self.config.generate_checksums:
                print("🔍 Validating backup integrity...")
                for file_path, expected_checksum in metadata.file_checksums.items():
                    backup_file = backup_dir / file_path
                    if backup_file.exists():
                        actual_checksum = self.calculate_file_checksum(backup_file)
                        if actual_checksum != expected_checksum:
                            print(f"❌ Checksum mismatch for {file_path}")
                            print(f"   Expected: {expected_checksum}")
                            print(f"   Actual:   {actual_checksum}")
                            return False
                print("✅ Backup integrity validated")

            # Restore files
            for file_path in metadata.files_backed_up:
                source_file = backup_dir / file_path
                dest_file = self.config.project_root / file_path

                if source_file.exists():
                    # Create directory structure
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    # Restore file
                    shutil.copy2(source_file, dest_file)
                    print(f"✅ Restored: {file_path}")
                else:
                    print(f"⚠️  Backup file missing: {file_path}")

            print("✅ PRP system restoration completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error during restoration: {e}")
            return False


@click.command()
@click.option("--backup-dir", "-d", default="backups", help="Backup directory name")
@click.option("--list-backups", "-l", is_flag=True, help="List available backups")
@click.option("--restore", "-r", help="Restore from backup ID")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be backed up without doing it"
)
@click.option(
    "--force", "-f", is_flag=True, help="Force operation without confirmation"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option(
    "--no-checksums", is_flag=True, help="Skip checksum generation for faster backup"
)
def backup_prp_system(
    backup_dir: str,
    list_backups: bool,
    restore: str,
    dry_run: bool,
    force: bool,
    verbose: bool,
    no_checksums: bool,
):
    """Backup and restore PRP system for PRPs-agentic-eng integration."""

    config = PRPBackupConfig(backup_dir=backup_dir, generate_checksums=not no_checksums)
    backup_manager = PRPSystemBackup(config)

    if list_backups:
        # List available backups
        backups = backup_manager.list_backups()

        if not backups:
            print("📭 No PRP backups found.")
            return

        print(f"📋 Available PRP backups ({len(backups)}):")
        for i, backup_path in enumerate(backups, 1):
            metadata_file = backup_path / "backup_metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)

                    timestamp = metadata.get("backup_timestamp", "Unknown")
                    files_count = len(metadata.get("files_backed_up", []))
                    git_commit = metadata.get("git_commit_hash", "unknown")[:8]

                    print(f"  {i}. {backup_path.name}")
                    print(f"     📅 Created: {timestamp}")
                    print(f"     📁 Files: {files_count}")
                    print(f"     🔗 Git: {git_commit}")
                    print()
                except Exception:
                    print(f"  {i}. {backup_path.name} (metadata unreadable)")

        return

    if restore:
        # Restore from backup
        if not force:
            response = click.confirm(
                "⚠️  This will overwrite current PRP system files. Continue?",
                default=False,
            )
            if not response:
                print("❌ Restoration cancelled.")
                return

        success = backup_manager.restore_from_backup(restore)
        if success:
            print("\n💡 Remember to review changes:")
            print("   git status")
            print("   git diff")
        sys.exit(0 if success else 1)

    if dry_run:
        # Show what would be backed up
        print("🔍 DRY RUN: Files that would be backed up:")

        for file_name in backup_manager.critical_files:
            file_path = config.project_root / file_name
            status = "✅" if file_path.exists() else "❌"
            print(f"  {status} {file_name}")

        for dir_name in backup_manager.critical_directories:
            dir_path = config.project_root / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*")))
                print(f"  📁 {dir_name}/ ({file_count} files)")
            else:
                print(f"  ❌ {dir_name}/ (not found)")

        for file_name in backup_manager.optional_files:
            file_path = config.project_root / file_name
            if file_path.exists():
                print(f"  📄 {file_name} (optional)")

        return

    # Create backup
    if not force:
        print(
            "🔍 Current PRP system will be backed up before PRPs-agentic-eng integration."
        )
        print(
            "📁 This includes: .claude/commands/, CLAUDE.md, PRPs/templates/, pyproject.toml"
        )
        response = click.confirm("Continue with backup creation?", default=True)
        if not response:
            print("❌ Backup cancelled.")
            return

    try:
        metadata = backup_manager.create_backup()

        if verbose:
            print("\n📊 Backup Summary:")
            print(f"   📁 Files backed up: {len(metadata.files_backed_up)}")
            print(f"   🔐 Checksums generated: {len(metadata.file_checksums)}")
            print(
                f"   📜 Rollback script: {'✅' if metadata.rollback_script_path else '❌'}"
            )
            print(f"   🔗 Git commit: {metadata.git_commit_hash or 'unknown'}")

        print("\n🛡️  Rollback instructions:")
        if metadata.rollback_script_path:
            print(f"   Quick rollback: bash {metadata.rollback_script_path}")
        print(f"   Manual rollback: python {__file__} --restore {metadata.backup_id}")

    except Exception as e:
        print(f"❌ Backup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    backup_prp_system()
