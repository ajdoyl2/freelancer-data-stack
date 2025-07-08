#!/usr/bin/env python3
"""
Intelligent Command Merging System

Merges PRPs-agentic-eng commands with existing freelancer-data-stack commands
while preserving domain-specific functionality and enhancing capabilities.
"""

import re
from pathlib import Path

import click
from pydantic import BaseModel


class CommandMergeStrategy(BaseModel):
    """Strategy for merging two command files."""

    existing_file: str
    new_file: str
    merge_type: str  # "enhance", "replace_sections", "append", "manual"
    sections_to_preserve: list[str] = []
    sections_to_enhance: list[str] = []
    manual_review_required: bool = False


class CommandMerger:
    """Intelligent command merging system."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.existing_commands_dir = project_root / ".claude" / "commands"
        self.temp_commands_dir = (
            project_root / "temp" / "PRPs-agentic-eng" / ".claude" / "commands"
        )

        # Commands that need intelligent merging
        self.merge_targets = {
            "prp-spec-create.md": {
                "existing": self.existing_commands_dir / "prp-spec-create.md",
                "new": self.temp_commands_dir / "PRPs" / "prp-spec-create.md",
                "priority": "high",
            },
            "prp-spec-execute.md": {
                "existing": self.existing_commands_dir / "prp-spec-execute.md",
                "new": self.temp_commands_dir / "PRPs" / "prp-spec-execute.md",
                "priority": "high",
            },
            "prp-task-create.md": {
                "existing": self.existing_commands_dir / "prp-task-create.md",
                "new": self.temp_commands_dir / "PRPs" / "prp-task-create.md",
                "priority": "medium",
            },
            "prp-task-execute.md": {
                "existing": self.existing_commands_dir / "prp-task-execute.md",
                "new": self.temp_commands_dir / "PRPs" / "prp-task-execute.md",
                "priority": "medium",
            },
        }

    def extract_markdown_sections(self, content: str) -> dict[str, str]:
        """
        Extract markdown sections from command file.

        Args:
            content: Markdown content

        Returns:
            Dict[str, str]: Mapping of section headers to content
        """
        sections = {}
        current_section = "header"
        current_content = []

        lines = content.split("\n")

        for line in lines:
            # Check if this is a section header
            if line.startswith("#"):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content)

                # Start new section
                current_section = line.strip()
                current_content = [line]
            else:
                current_content.append(line)

        # Save final section
        if current_content:
            sections[current_section] = "\n".join(current_content)

        return sections

    def identify_domain_specific_content(self, content: str) -> list[str]:
        """
        Identify domain-specific data stack content that must be preserved.

        Args:
            content: File content

        Returns:
            List[str]: List of domain-specific patterns found
        """
        domain_patterns = [
            r"DataStackEngineer",
            r"data[-_]stack",
            r"meltano",
            r"dbt",
            r"airflow",
            r"duckdb",
            r"docker[-_]compose",
            r"freelancer[-_]data[-_]stack",
            r"venv_linux",
            r"agents/",
            r"tools/",
            r"\.env",
            r"deploy[-_]stack",
            r"monitor[-_]stack",
            r"validate[-_]pipeline",
            r"cost[-_]optimization",
        ]

        found_patterns = []
        content_lower = content.lower()

        for pattern in domain_patterns:
            if re.search(pattern, content_lower):
                found_patterns.append(pattern)

        return found_patterns

    def analyze_merge_strategy(
        self, existing_file: Path, new_file: Path
    ) -> CommandMergeStrategy:
        """
        Analyze files and determine optimal merge strategy.

        Args:
            existing_file: Path to existing command file
            new_file: Path to new command file

        Returns:
            CommandMergeStrategy: Recommended merge strategy
        """
        if not existing_file.exists():
            return CommandMergeStrategy(
                existing_file=str(existing_file),
                new_file=str(new_file),
                merge_type="replace",
            )

        if not new_file.exists():
            return CommandMergeStrategy(
                existing_file=str(existing_file),
                new_file=str(new_file),
                merge_type="keep_existing",
            )

        # Read both files
        existing_content = existing_file.read_text()
        new_content = new_file.read_text()

        # Extract sections
        existing_sections = self.extract_markdown_sections(existing_content)
        new_sections = self.extract_markdown_sections(new_content)

        # Identify domain-specific content
        domain_patterns = self.identify_domain_specific_content(existing_content)

        # Determine merge strategy
        if domain_patterns:
            # Has domain-specific content - need careful merging
            strategy = CommandMergeStrategy(
                existing_file=str(existing_file),
                new_file=str(new_file),
                merge_type="enhance",
                sections_to_preserve=list(existing_sections.keys()),
                sections_to_enhance=[],
                manual_review_required=True,
            )

            # Identify sections that can be enhanced
            for section_name in new_sections.keys():
                if section_name not in existing_sections:
                    strategy.sections_to_enhance.append(section_name)

        else:
            # No domain-specific content - can replace more freely
            strategy = CommandMergeStrategy(
                existing_file=str(existing_file),
                new_file=str(new_file),
                merge_type="replace_sections",
                sections_to_preserve=[],
                sections_to_enhance=list(new_sections.keys()),
            )

        return strategy

    def create_enhanced_command(self, strategy: CommandMergeStrategy) -> str:
        """
        Create enhanced command content based on merge strategy.

        Args:
            strategy: Merge strategy to apply

        Returns:
            str: Enhanced command content
        """
        existing_file = Path(strategy.existing_file)
        new_file = Path(strategy.new_file)

        existing_content = existing_file.read_text() if existing_file.exists() else ""
        new_content = new_file.read_text() if new_file.exists() else ""

        if strategy.merge_type == "replace":
            return new_content
        elif strategy.merge_type == "keep_existing":
            return existing_content

        # Extract sections for intelligent merging
        existing_sections = self.extract_markdown_sections(existing_content)
        new_sections = self.extract_markdown_sections(new_content)

        # Build enhanced content
        enhanced_sections = {}

        # Start with existing sections (preserve domain-specific content)
        for section_name, content in existing_sections.items():
            enhanced_sections[section_name] = content

        # Add enhancements from new file
        for section_name, content in new_sections.items():
            if section_name not in enhanced_sections:
                # New section - add it
                enhanced_sections[section_name] = content
            else:
                # Existing section - enhance if not domain-specific
                if not self.identify_domain_specific_content(
                    existing_sections[section_name]
                ):
                    # Check if new version has more content/features
                    if len(content) > len(existing_sections[section_name]) * 1.2:
                        # New version is significantly longer - likely enhanced
                        enhanced_sections[f"{section_name} (Enhanced)"] = content

        # Combine sections back into content
        enhanced_content = []

        # Add header section first
        if "header" in enhanced_sections:
            enhanced_content.append(enhanced_sections["header"])
            del enhanced_sections["header"]

        # Add remaining sections
        for section_content in enhanced_sections.values():
            enhanced_content.append(section_content)

        return "\n\n".join(enhanced_content)

    def backup_original(self, file_path: Path) -> Path:
        """
        Create backup of original file.

        Args:
            file_path: Path to file to backup

        Returns:
            Path: Backup file path
        """
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        backup_path.write_text(file_path.read_text())
        return backup_path

    def merge_command(self, command_name: str) -> tuple[bool, str]:
        """
        Merge a specific command with intelligent strategy.

        Args:
            command_name: Name of command to merge

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if command_name not in self.merge_targets:
            return False, f"Command {command_name} not in merge targets"

        target = self.merge_targets[command_name]
        existing_file = target["existing"]
        new_file = target["new"]

        print(f"🔄 Merging {command_name}...")

        # Analyze merge strategy
        strategy = self.analyze_merge_strategy(existing_file, new_file)

        if strategy.manual_review_required:
            print(f"⚠️  Manual review required for {command_name}")

        # Backup original
        if existing_file.exists():
            backup_path = self.backup_original(existing_file)
            print(f"📁 Backed up original: {backup_path}")

        # Create enhanced content
        try:
            enhanced_content = self.create_enhanced_command(strategy)

            # Write enhanced command
            existing_file.write_text(enhanced_content)

            print(f"✅ Enhanced {command_name}")

            if strategy.manual_review_required:
                return True, "Enhanced with manual review recommended"
            else:
                return True, "Enhanced successfully"

        except Exception as e:
            return False, f"Error enhancing {command_name}: {e}"

    def create_merge_report(self, results: dict[str, tuple[bool, str]]) -> None:
        """
        Create comprehensive merge report.

        Args:
            results: Merge results for each command
        """
        report_file = self.project_root / "temp" / "command_merge_report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report_content = f"""# Command Merge Report

Generated: {click.get_current_context().params.get('timestamp', 'now')}

## Summary
- **Commands processed**: {len(results)}
- **Successful merges**: {sum(1 for success, _ in results.values() if success)}
- **Failed merges**: {sum(1 for success, _ in results.values() if not success)}
- **Manual review required**: {sum(1 for _, msg in results.values() if 'manual review' in msg)}

## Merge Results

"""

        for command_name, (success, message) in results.items():
            status_emoji = "✅" if success else "❌"
            priority = self.merge_targets[command_name]["priority"]

            report_content += f"""### {command_name} ({priority} priority)
{status_emoji} **Status**: {message}

**Files involved**:
- Existing: {self.merge_targets[command_name]['existing']}
- New: {self.merge_targets[command_name]['new']}

---

"""

        report_content += """## Next Steps
1. Review enhanced commands for correctness
2. Test enhanced commands functionality
3. Address any manual review requirements
4. Proceed with CLAUDE.md enhancement (Task 5)

## Validation Commands
```bash
# Test enhanced commands
ls -la .claude/commands/prp-*.md

# Check for backup files
ls -la .claude/commands/*.backup

# Validate markdown syntax
markdownlint .claude/commands/prp-*.md
```
"""

        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"📋 Merge report created: {report_file}")

    def merge_all_commands(self) -> dict[str, tuple[bool, str]]:
        """
        Merge all commands marked for enhancement.

        Returns:
            Dict[str, Tuple[bool, str]]: Results for each command
        """
        results = {}

        print("🔄 Starting intelligent command merging...")
        print(f"📁 Processing {len(self.merge_targets)} commands")

        for command_name in self.merge_targets.keys():
            success, message = self.merge_command(command_name)
            results[command_name] = (success, message)

        return results


@click.command()
@click.option("--command", "-c", help="Specific command to merge (or 'all' for all)")
@click.option("--dry-run", is_flag=True, help="Show merge strategy without executing")
@click.option("--force", "-f", is_flag=True, help="Force merge without confirmation")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def merge_commands(command: str, dry_run: bool, force: bool, verbose: bool):
    """Intelligently merge PRPs-agentic-eng commands with existing commands."""

    project_root = Path.cwd()
    merger = CommandMerger(project_root)

    if dry_run:
        print("🔍 DRY RUN: Analyzing merge strategies...")

        for command_name, target in merger.merge_targets.items():
            existing_file = target["existing"]
            new_file = target["new"]

            strategy = merger.analyze_merge_strategy(existing_file, new_file)

            print(f"\n📋 {command_name} ({target['priority']} priority):")
            print(f"   Strategy: {strategy.merge_type}")
            print(
                f"   Manual review: {'Yes' if strategy.manual_review_required else 'No'}"
            )

            if strategy.sections_to_preserve:
                print(f"   Sections to preserve: {len(strategy.sections_to_preserve)}")
            if strategy.sections_to_enhance:
                print(f"   Sections to enhance: {len(strategy.sections_to_enhance)}")

        return

    if command and command != "all":
        # Merge specific command
        if command not in merger.merge_targets:
            print(f"❌ Command {command} not found in merge targets")
            return

        success, message = merger.merge_command(command)
        if success:
            print(f"✅ {command}: {message}")
        else:
            print(f"❌ {command}: {message}")
    else:
        # Merge all commands
        if not force:
            print("🔍 This will merge 4 commands with PRPs-agentic-eng enhancements:")
            for name, target in merger.merge_targets.items():
                print(f"  - {name} ({target['priority']} priority)")

            response = click.confirm("Continue with command merging?", default=True)
            if not response:
                print("❌ Command merging cancelled.")
                return

        # Execute merging
        results = merger.merge_all_commands()

        # Create report
        merger.create_merge_report(results)

        # Summary
        successful = sum(1 for success, _ in results.values() if success)
        total = len(results)

        print(
            f"\n📊 Merge Summary: {successful}/{total} commands enhanced successfully"
        )

        if successful == total:
            print("🎉 All commands merged successfully!")
        else:
            print("⚠️  Some commands require attention - check merge report")


if __name__ == "__main__":
    merge_commands()
