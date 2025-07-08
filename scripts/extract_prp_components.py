#!/usr/bin/env python3
"""
PRPs-agentic-eng Component Extraction Script

Intelligently extracts and prepares components from PRPs-agentic-eng for
integration with freelancer-data-stack while avoiding conflicts.
"""

import shutil
from pathlib import Path

import click
from pydantic import BaseModel


class ComponentMapping(BaseModel):
    """Mapping of source to destination components."""

    source_path: str
    dest_path: str
    action: str  # "copy", "merge", "rename", "skip"
    reason: str
    priority: str = "medium"  # "high", "medium", "low"


class PRPComponentExtractor:
    """Extract and prepare PRPs-agentic-eng components for integration."""

    def __init__(self, source_dir: Path, dest_dir: Path):
        self.source_dir = source_dir
        self.dest_dir = dest_dir

        # Existing commands that must be preserved
        self.existing_commands = {
            "ai-agent-task.md",
            "create-base-prp-parallel.md",
            "create-planning-parallel.md",
            "create-pr.md",
            "data-stack-help.md",
            "debug-issue.md",
            "deploy-data-stack.md",
            "execute-prp.md",
            "generate-prp.md",
            "monitor-data-stack.md",
            "onboarding-docs.md",
            "optimize-costs.md",
            "prime-context.md",
            "prp-spec-create.md",
            "prp-spec-execute.md",
            "prp-task-create.md",
            "prp-task-execute.md",
            "run-data-pipeline.md",
            "scale-data-stack.md",
            "troubleshoot-stack.md",
            "validate-pipeline.md",
        }

    def analyze_command_conflicts(self) -> dict[str, ComponentMapping]:
        """
        Analyze command conflicts and create mapping strategy.

        Returns:
            Dict[str, ComponentMapping]: Command integration mapping
        """
        mappings = {}
        source_commands_dir = self.source_dir / ".claude" / "commands"

        # Scan all command files in PRPs-agentic-eng
        for command_file in source_commands_dir.rglob("*.md"):
            relative_path = command_file.relative_to(source_commands_dir)
            command_name = command_file.name

            # Determine integration strategy
            if command_name in self.existing_commands:
                # Handle conflicts
                if command_name in ["create-pr.md", "onboarding.md"]:
                    # Rename to avoid conflict but preserve both
                    new_name = f"prp-{command_name}"
                    mapping = ComponentMapping(
                        source_path=str(relative_path),
                        dest_path=new_name,
                        action="rename",
                        reason=f"Conflict with existing {command_name}",
                        priority="medium",
                    )
                elif command_name in [
                    "prp-spec-create.md",
                    "prp-spec-execute.md",
                    "prp-task-create.md",
                    "prp-task-execute.md",
                ]:
                    # These might enhance existing versions
                    mapping = ComponentMapping(
                        source_path=str(relative_path),
                        dest_path=str(relative_path),
                        action="merge",
                        reason=f"Enhance existing {command_name}",
                        priority="high",
                    )
                else:
                    # Skip to preserve domain-specific commands
                    mapping = ComponentMapping(
                        source_path=str(relative_path),
                        dest_path=str(relative_path),
                        action="skip",
                        reason=f"Preserve domain-specific {command_name}",
                        priority="low",
                    )
            else:
                # New command, safe to add
                mapping = ComponentMapping(
                    source_path=str(relative_path),
                    dest_path=str(relative_path),
                    action="copy",
                    reason=f"New command: {command_name}",
                    priority="high",
                )

            mappings[str(relative_path)] = mapping

        return mappings

    def extract_commands(self, mappings: dict[str, ComponentMapping]) -> list[str]:
        """
        Extract and copy command files based on mapping strategy.

        Args:
            mappings: Command integration mappings

        Returns:
            List[str]: List of successfully integrated commands
        """
        integrated_commands = []
        dest_commands_dir = self.dest_dir / ".claude" / "commands"
        dest_commands_dir.mkdir(parents=True, exist_ok=True)

        for relative_path, mapping in mappings.items():
            source_file = self.source_dir / ".claude" / "commands" / relative_path

            if mapping.action == "copy":
                dest_file = dest_commands_dir / mapping.dest_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                integrated_commands.append(mapping.dest_path)
                print(f"✅ Copied: {mapping.dest_path}")

            elif mapping.action == "rename":
                dest_file = dest_commands_dir / mapping.dest_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                integrated_commands.append(mapping.dest_path)
                print(f"✅ Renamed: {relative_path} → {mapping.dest_path}")

            elif mapping.action == "skip":
                print(f"⏭️  Skipped: {relative_path} ({mapping.reason})")

            elif mapping.action == "merge":
                # Mark for later manual merge
                print(f"🔄 Marked for merge: {relative_path}")

        return integrated_commands

    def extract_templates(self) -> list[str]:
        """
        Extract enhanced PRP templates.

        Returns:
            List[str]: List of extracted templates
        """
        extracted_templates = []
        source_templates_dir = self.source_dir / "PRPs" / "templates"
        dest_templates_dir = self.dest_dir / "PRPs" / "templates"

        if not source_templates_dir.exists():
            print("⚠️  Source templates directory not found")
            return extracted_templates

        for template_file in source_templates_dir.glob("*.md"):
            template_name = template_file.name

            if template_name == "prp_base.md":
                # Special handling for base template - enhance existing
                dest_file = dest_templates_dir / "prp_base_enhanced.md"
                shutil.copy2(template_file, dest_file)
                extracted_templates.append("prp_base_enhanced.md")
                print(f"✅ Enhanced template: {template_name} → prp_base_enhanced.md")
            else:
                # Copy new templates
                dest_file = dest_templates_dir / template_name
                shutil.copy2(template_file, dest_file)
                extracted_templates.append(template_name)
                print(f"✅ Added template: {template_name}")

        return extracted_templates

    def extract_scripts(self) -> list[str]:
        """
        Extract utility scripts.

        Returns:
            List[str]: List of extracted scripts
        """
        extracted_scripts = []
        source_scripts_dir = self.source_dir / "PRPs" / "scripts"
        dest_scripts_dir = self.dest_dir / "PRPs" / "scripts"
        dest_scripts_dir.mkdir(parents=True, exist_ok=True)

        if not source_scripts_dir.exists():
            print("⚠️  Source scripts directory not found")
            return extracted_scripts

        for script_file in source_scripts_dir.glob("*"):
            if script_file.is_file():
                dest_file = dest_scripts_dir / script_file.name
                shutil.copy2(script_file, dest_file)

                # Make Python scripts executable
                if script_file.suffix == ".py":
                    dest_file.chmod(0o755)

                extracted_scripts.append(script_file.name)
                print(f"✅ Extracted script: {script_file.name}")

        return extracted_scripts

    def extract_ai_docs(self) -> list[str]:
        """
        Extract AI documentation while preserving existing docs.

        Returns:
            List[str]: List of extracted documentation
        """
        extracted_docs = []
        source_docs_dir = self.source_dir / "PRPs" / "ai_docs"
        dest_docs_dir = self.dest_dir / "PRPs" / "ai_docs"

        if not source_docs_dir.exists():
            print("⚠️  Source ai_docs directory not found")
            return extracted_docs

        for doc_file in source_docs_dir.glob("*.md"):
            doc_name = doc_file.name

            # Check if we already have this doc (from PRP generation)
            dest_file = dest_docs_dir / doc_name
            if dest_file.exists():
                # Create enhanced version
                new_name = f"enhanced_{doc_name}"
                dest_file = dest_docs_dir / new_name
                shutil.copy2(doc_file, dest_file)
                extracted_docs.append(new_name)
                print(f"✅ Enhanced doc: {doc_name} → {new_name}")
            else:
                # Copy new documentation
                shutil.copy2(doc_file, dest_file)
                extracted_docs.append(doc_name)
                print(f"✅ Added doc: {doc_name}")

        return extracted_docs

    def extract_claude_md_enhancements(self) -> str:
        """
        Extract CLAUDE.md enhancements for later intelligent merging.

        Returns:
            str: Path to extracted CLAUDE.md
        """
        source_claude = self.source_dir / "CLAUDE.md"

        if not source_claude.exists():
            print("⚠️  Source CLAUDE.md not found")
            return ""

        # Extract to temp location for later merging
        dest_claude = self.dest_dir / "temp" / "prp_agentic_eng_CLAUDE.md"
        dest_claude.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_claude, dest_claude)

        print(f"✅ Extracted CLAUDE.md enhancements: {dest_claude}")
        return str(dest_claude)

    def create_integration_report(
        self,
        commands: list[str],
        templates: list[str],
        scripts: list[str],
        docs: list[str],
        claude_md_path: str,
    ) -> None:
        """
        Create comprehensive integration report.

        Args:
            commands: List of integrated commands
            templates: List of extracted templates
            scripts: List of extracted scripts
            docs: List of extracted documentation
            claude_md_path: Path to extracted CLAUDE.md
        """
        report_file = self.dest_dir / "temp" / "integration_report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report_content = f"""# PRPs-agentic-eng Integration Report

Generated: {click.datetime.now().isoformat()}

## Summary
- **Commands integrated**: {len(commands)}
- **Templates extracted**: {len(templates)}
- **Scripts extracted**: {len(scripts)}
- **Documentation extracted**: {len(docs)}
- **CLAUDE.md enhancements**: {'✅' if claude_md_path else '❌'}

## Integrated Commands ({len(commands)})
"""

        for command in sorted(commands):
            report_content += f"- {command}\n"

        report_content += f"""
## Extracted Templates ({len(templates)})
"""

        for template in sorted(templates):
            report_content += f"- {template}\n"

        report_content += f"""
## Extracted Scripts ({len(scripts)})
"""

        for script in sorted(scripts):
            report_content += f"- {script}\n"

        report_content += f"""
## Extracted Documentation ({len(docs)})
"""

        for doc in sorted(docs):
            report_content += f"- {doc}\n"

        if claude_md_path:
            report_content += f"""
## CLAUDE.md Enhancements
- Source: {claude_md_path}
- Status: Ready for intelligent merging
"""

        report_content += """
## Next Steps
1. Review extracted components
2. Proceed with intelligent command merging (Task 4)
3. Enhance CLAUDE.md with intelligent merging (Task 5)
4. Enhance PRP templates with validation loops (Task 6)
5. Integrate utility scripts (Task 7)
"""

        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"\n📋 Integration report created: {report_file}")


@click.command()
@click.option(
    "--source",
    "-s",
    default="temp/PRPs-agentic-eng",
    help="Source PRPs-agentic-eng directory",
)
@click.option("--dest", "-d", default=".", help="Destination directory (project root)")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be extracted without doing it"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def extract_components(source: str, dest: str, dry_run: bool, verbose: bool):
    """Extract PRPs-agentic-eng components for integration."""

    source_dir = Path(source)
    dest_dir = Path(dest)

    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return

    print("🔄 Extracting PRPs-agentic-eng components...")
    print(f"📁 Source: {source_dir.absolute()}")
    print(f"📁 Destination: {dest_dir.absolute()}")

    if dry_run:
        print("\n🔍 DRY RUN: Components that would be extracted:")

        # Analyze commands
        extractor = PRPComponentExtractor(source_dir, dest_dir)
        mappings = extractor.analyze_command_conflicts()

        print(f"\n📋 Commands Analysis ({len(mappings)} total):")
        for relative_path, mapping in mappings.items():
            action_emoji = {
                "copy": "✅",
                "rename": "🔄",
                "merge": "🔀",
                "skip": "⏭️",
            }.get(mapping.action, "❓")

            print(f"  {action_emoji} {relative_path} → {mapping.action}")
            if verbose:
                print(f"      Reason: {mapping.reason}")

        return

    # Execute extraction
    extractor = PRPComponentExtractor(source_dir, dest_dir)

    # Analyze command conflicts
    mappings = extractor.analyze_command_conflicts()

    # Extract components
    print("\n📋 Extracting commands...")
    commands = extractor.extract_commands(mappings)

    print("\n📄 Extracting templates...")
    templates = extractor.extract_templates()

    print("\n🔧 Extracting scripts...")
    scripts = extractor.extract_scripts()

    print("\n📚 Extracting documentation...")
    docs = extractor.extract_ai_docs()

    print("\n⚙️  Extracting CLAUDE.md enhancements...")
    claude_md_path = extractor.extract_claude_md_enhancements()

    # Create integration report
    extractor.create_integration_report(
        commands, templates, scripts, docs, claude_md_path
    )

    print("\n✅ Component extraction completed!")
    print(
        f"📊 Summary: {len(commands)} commands, {len(templates)} templates, {len(scripts)} scripts, {len(docs)} docs"
    )


if __name__ == "__main__":
    extract_components()
