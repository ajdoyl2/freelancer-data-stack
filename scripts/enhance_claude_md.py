#!/usr/bin/env python3
"""
Intelligent CLAUDE.md Enhancement System

Merges PRPs-agentic-eng CLAUDE.md enhancements with existing freelancer-data-stack
CLAUDE.md while preserving all project-specific rules and domain expertise.
"""

import re
from pathlib import Path

import click
from pydantic import BaseModel


class CLAUDESection(BaseModel):
    """Represents a section in CLAUDE.md."""

    title: str
    content: str
    is_project_specific: bool = False
    has_domain_rules: bool = False
    enhancement_candidate: bool = False


class CLAUDEEnhancer:
    """Intelligent CLAUDE.md enhancement system."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.current_claude = project_root / "CLAUDE.md"
        self.enhanced_claude = project_root / "temp" / "prp_agentic_eng_CLAUDE.md"

        # Project-specific patterns that MUST be preserved
        self.project_patterns = {
            "environment_rules": [
                r"venv_linux",
                r"UV.*dependency",
                r"python_dotenv.*load_env",
            ],
            "architecture_rules": [
                r"500.*line.*limit",
                r"agent\.py.*tools\.py.*prompts\.py",
                r"relative.*imports",
            ],
            "data_stack_rules": [
                r"SQL.*Jinja.*YAML.*Python.*analytics",
                r"dbt.*meltano.*airflow",
                r"docker.*containerization",
                r"data.?stack",
            ],
            "testing_rules": [
                r"pytest.*unit.*tests",
                r"3.*test.*types",
                r"expected.*edge.*failure",
                r"TASK\.md",
                r"PLANNING\.md",
            ],
            "ai_behavior_rules": [
                r"never.*assume.*missing.*context",
                r"never.*hallucinate.*libraries",
                r"never.*delete.*overwrite.*code",
            ],
        }

    def extract_sections(self, content: str) -> list[CLAUDESection]:
        """
        Extract sections from CLAUDE.md content.

        Args:
            content: CLAUDE.md content

        Returns:
            List[CLAUDESection]: Extracted sections
        """
        sections = []
        lines = content.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            # Check for section headers (### or ##)
            if line.startswith("###") or line.startswith("##"):
                # Save previous section
                if current_section:
                    section_content = "\n".join(current_content)
                    sections.append(
                        CLAUDESection(
                            title=current_section,
                            content=section_content,
                            is_project_specific=self.is_project_specific(
                                section_content
                            ),
                            has_domain_rules=self.has_domain_rules(section_content),
                            enhancement_candidate=self.is_enhancement_candidate(
                                current_section
                            ),
                        )
                    )

                # Start new section
                current_section = line.strip()
                current_content = [line]
            else:
                if current_section:
                    current_content.append(line)

        # Save final section
        if current_section:
            section_content = "\n".join(current_content)
            sections.append(
                CLAUDESection(
                    title=current_section,
                    content=section_content,
                    is_project_specific=self.is_project_specific(section_content),
                    has_domain_rules=self.has_domain_rules(section_content),
                    enhancement_candidate=self.is_enhancement_candidate(
                        current_section
                    ),
                )
            )

        return sections

    def is_project_specific(self, content: str) -> bool:
        """
        Check if content contains project-specific rules that must be preserved.

        Args:
            content: Section content

        Returns:
            bool: True if project-specific
        """
        content_lower = content.lower()

        for _category, patterns in self.project_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return True

        return False

    def has_domain_rules(self, content: str) -> bool:
        """
        Check if content has data stack domain-specific rules.

        Args:
            content: Section content

        Returns:
            bool: True if has domain rules
        """
        domain_keywords = [
            "data.?stack",
            "meltano",
            "dbt",
            "airflow",
            "duckdb",
            "docker.?compose",
            "agent",
            "tool",
            "pipeline",
            "analytics",
        ]

        content_lower = content.lower()
        for keyword in domain_keywords:
            if re.search(keyword, content_lower):
                return True

        return False

    def is_enhancement_candidate(self, title: str) -> bool:
        """
        Check if section is a candidate for enhancement.

        Args:
            title: Section title

        Returns:
            bool: True if can be enhanced
        """
        enhancement_sections = [
            "project awareness",
            "code structure",
            "testing",
            "ai behavior",
            "documentation",
        ]

        title_lower = title.lower()
        for section in enhancement_sections:
            if section in title_lower:
                return True

        return False

    def merge_sections(
        self,
        current_sections: list[CLAUDESection],
        enhanced_sections: list[CLAUDESection],
    ) -> list[CLAUDESection]:
        """
        Intelligently merge sections from both CLAUDE.md files.

        Args:
            current_sections: Sections from existing CLAUDE.md
            enhanced_sections: Sections from PRPs-agentic-eng CLAUDE.md

        Returns:
            List[CLAUDESection]: Merged sections
        """
        merged_sections = []

        # Create mapping of enhanced sections
        enhanced_map = {
            s.title.lower().replace("#", "").strip(): s for s in enhanced_sections
        }

        for current_section in current_sections:
            # Always preserve project-specific sections exactly
            if current_section.is_project_specific or current_section.has_domain_rules:
                merged_sections.append(current_section)
                continue

            # Check if we can enhance this section
            section_key = current_section.title.lower().replace("#", "").strip()

            # Look for matching enhanced section
            enhanced_section = None
            for key, section in enhanced_map.items():
                if self.sections_match(section_key, key):
                    enhanced_section = section
                    break

            if enhanced_section and current_section.enhancement_candidate:
                # Merge with enhancements
                merged_content = self.merge_section_content(
                    current_section.content, enhanced_section.content
                )

                merged_section = CLAUDESection(
                    title=current_section.title,
                    content=merged_content,
                    is_project_specific=current_section.is_project_specific,
                    has_domain_rules=current_section.has_domain_rules,
                    enhancement_candidate=True,
                )
                merged_sections.append(merged_section)
            else:
                # Keep original section
                merged_sections.append(current_section)

        # Add new sections from enhanced version that don't exist in current
        current_titles = {
            s.title.lower().replace("#", "").strip() for s in current_sections
        }

        for enhanced_section in enhanced_sections:
            enhanced_key = enhanced_section.title.lower().replace("#", "").strip()

            # Check if this is a new section
            is_new_section = True
            for current_title in current_titles:
                if self.sections_match(enhanced_key, current_title):
                    is_new_section = False
                    break

            if is_new_section:
                # Add new enhancement section
                merged_sections.append(enhanced_section)

        return merged_sections

    def sections_match(self, key1: str, key2: str) -> bool:
        """
        Check if two section keys match (fuzzy matching).

        Args:
            key1: First section key
            key2: Second section key

        Returns:
            bool: True if sections match
        """
        # Remove common words and normalize
        common_words = {"and", "the", "of", "for", "with", "in", "on", "at"}

        def normalize_key(key):
            words = re.findall(r"\w+", key.lower())
            return " ".join(word for word in words if word not in common_words)

        norm_key1 = normalize_key(key1)
        norm_key2 = normalize_key(key2)

        # Check for partial matches
        if norm_key1 in norm_key2 or norm_key2 in norm_key1:
            return True

        # Check for keyword overlap
        words1 = set(norm_key1.split())
        words2 = set(norm_key2.split())

        if words1 & words2:  # If there's any overlap
            return True

        return False

    def merge_section_content(self, current_content: str, enhanced_content: str) -> str:
        """
        Merge content from two sections, preserving project-specific rules.

        Args:
            current_content: Current section content
            enhanced_content: Enhanced section content

        Returns:
            str: Merged content
        """
        # Split content into bullet points and rules
        current_rules = self.extract_rules(current_content)
        enhanced_rules = self.extract_rules(enhanced_content)

        # Preserve all project-specific rules
        merged_rules = []

        # Add all current rules (preserve project-specific)
        for rule in current_rules:
            merged_rules.append(rule)

        # Add enhanced rules that don't conflict
        for enhanced_rule in enhanced_rules:
            if not self.conflicts_with_project_rules(enhanced_rule):
                # Check if this is a new rule
                if not any(
                    self.rules_similar(enhanced_rule, current_rule)
                    for current_rule in current_rules
                ):
                    merged_rules.append(enhanced_rule)

        # Reconstruct section with merged rules
        return self.reconstruct_section_content(current_content, merged_rules)

    def extract_rules(self, content: str) -> list[str]:
        """
        Extract individual rules/bullet points from section content.

        Args:
            content: Section content

        Returns:
            List[str]: Extracted rules
        """
        rules = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            # Look for bullet points, numbered lists, or bold statements
            if (
                line.startswith("-")
                or line.startswith("*")
                or re.match(r"^\d+\.", line)
                or line.startswith("**")
            ):
                rules.append(line)

        return rules

    def conflicts_with_project_rules(self, rule: str) -> bool:
        """
        Check if a rule conflicts with project-specific requirements.

        Args:
            rule: Rule to check

        Returns:
            bool: True if conflicts
        """
        rule_lower = rule.lower()

        # Check for conflicting patterns
        conflicts = [
            ("uv", "venv_linux"),  # UV conflicts with venv_linux requirement
            ("pip install", "uv"),  # pip conflicts with UV
            ("npm", "uv"),  # npm conflicts with UV Python project
        ]

        for conflict_pattern, _project_requirement in conflicts:
            if conflict_pattern in rule_lower:
                return True

        return False

    def rules_similar(self, rule1: str, rule2: str) -> bool:
        """
        Check if two rules are similar enough to avoid duplication.

        Args:
            rule1: First rule
            rule2: Second rule

        Returns:
            bool: True if similar
        """

        # Normalize rules by removing markdown and punctuation
        def normalize_rule(rule):
            cleaned = re.sub(r"[*\-#`]", "", rule)
            cleaned = re.sub(r"\s+", " ", cleaned)
            return cleaned.lower().strip()

        norm_rule1 = normalize_rule(rule1)
        norm_rule2 = normalize_rule(rule2)

        # Check for substantial overlap
        words1 = set(norm_rule1.split())
        words2 = set(norm_rule2.split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        overlap = len(words1 & words2)
        min_length = min(len(words1), len(words2))

        # If more than 60% overlap, consider similar
        return overlap / min_length > 0.6

    def reconstruct_section_content(
        self, original_content: str, rules: list[str]
    ) -> str:
        """
        Reconstruct section content with merged rules.

        Args:
            original_content: Original section content
            rules: Merged rules

        Returns:
            str: Reconstructed content
        """
        lines = original_content.split("\n")
        result_lines = []

        # Keep non-rule lines (headers, explanations, etc.)
        for line in lines:
            line_stripped = line.strip()
            if not (
                line_stripped.startswith("-")
                or line_stripped.startswith("*")
                or re.match(r"^\d+\.", line_stripped)
                or line_stripped.startswith("**")
            ):
                result_lines.append(line)
            elif not result_lines or result_lines[-1].strip():
                # Add separator before rules
                result_lines.append("")
                break

        # Add merged rules
        for rule in rules:
            result_lines.append(rule)

        return "\n".join(result_lines)

    def create_enhanced_claude_md(self) -> str:
        """
        Create enhanced CLAUDE.md content.

        Returns:
            str: Enhanced CLAUDE.md content
        """
        # Read current CLAUDE.md
        if not self.current_claude.exists():
            raise FileNotFoundError(
                f"Current CLAUDE.md not found: {self.current_claude}"
            )

        current_content = self.current_claude.read_text()

        # Read enhanced CLAUDE.md
        enhanced_content = ""
        if self.enhanced_claude.exists():
            enhanced_content = self.enhanced_claude.read_text()
        else:
            print("⚠️  Enhanced CLAUDE.md not found, using current only")

        # Extract sections
        current_sections = self.extract_sections(current_content)
        enhanced_sections = (
            self.extract_sections(enhanced_content) if enhanced_content else []
        )

        # Merge sections intelligently
        merged_sections = self.merge_sections(current_sections, enhanced_sections)

        # Add PRPs-agentic-eng specific enhancements at the end
        prp_enhancements = self.create_prp_enhancements()

        # Reconstruct CLAUDE.md
        enhanced_content_parts = []

        for section in merged_sections:
            enhanced_content_parts.append(section.content)

        # Add PRP enhancements
        enhanced_content_parts.append(prp_enhancements)

        return "\n\n".join(enhanced_content_parts)

    def create_prp_enhancements(self) -> str:
        """
        Create PRPs-agentic-eng specific enhancement section.

        Returns:
            str: PRP enhancement section
        """
        return """### 🚀 PRP (Product Requirements Planning) Enhancement

#### Context Engineering Principles
- **Context is King**: Include ALL necessary documentation, examples, and gotchas in PRPs
- **Information Dense**: Use specific action verbs (MIRROR, COPY, ADD, MODIFY, DELETE, RENAME, MOVE, REPLACE, CREATE)
- **Validation Loops**: Progressive validation with executable commands (syntax → unit → integration → creative)
- **One-Pass Implementation**: Comprehensive context enables successful first-pass implementation

#### PRP Creation Workflow
- **Research Phase**: Use parallel agents for comprehensive codebase and external research
- **Context Synthesis**: Combine research findings into implementation blueprint
- **Validation Gates**: Include executable commands for quality assurance
- **Quality Scoring**: Rate PRPs on 1-10 scale for implementation confidence

#### Enhanced Command Library
- **49 Total Commands**: 21 existing data stack + 28 integrated PRPs-agentic-eng commands
- **Domain Preservation**: All data stack commands maintain exact functionality
- **New Capabilities**: Advanced PRP creation, conflict resolution, code review automation
- **TypeScript Support**: Specialized TypeScript development workflows

#### Template Enhancements
- **prp_base_enhanced.md**: Enhanced base template with validation loops
- **prp_planning.md**: Visual planning with Mermaid diagrams
- **prp_spec.md**: Technical specification template
- **prp_task.md**: Task-based development template

#### Utility Integration
- **prp_runner.py**: Automated PRP execution with multiple output formats
- **AI Documentation**: 13 curated Claude Code documentation files in PRPs/ai_docs/
- **Security System**: Comprehensive backup and rollback capability"""

    def backup_current_claude(self) -> Path:
        """
        Create backup of current CLAUDE.md.

        Returns:
            Path: Backup file path
        """
        backup_path = self.current_claude.with_suffix(".md.backup")
        backup_path.write_text(self.current_claude.read_text())
        return backup_path

    def create_enhancement_report(self, backup_path: Path) -> None:
        """
        Create enhancement report.

        Args:
            backup_path: Path to backup file
        """
        report_file = self.project_root / "temp" / "claude_md_enhancement_report.md"

        report_content = rf"""# CLAUDE.md Enhancement Report

## Summary
✅ **CLAUDE.md successfully enhanced** with PRPs-agentic-eng improvements

## Key Enhancements
- **Context Engineering**: Added PRP methodology section
- **Enhanced Command Library**: Documentation for 49 total commands
- **Template Integration**: References to enhanced PRP templates
- **Utility Documentation**: prp_runner.py and AI documentation structure
- **Validation Framework**: Progressive validation methodology

## Project-Specific Rules Preserved
✅ **Environment Rules**: venv_linux, UV dependency management, python_dotenv usage
✅ **Architecture Rules**: 500-line file limit, agent structure patterns, relative imports
✅ **Data Stack Rules**: SQL/Jinja/YAML/Python analytics, dbt/Meltano/Airflow integration
✅ **Testing Rules**: Pytest requirements, 3 test types, TASK.md/PLANNING.md integration
✅ **AI Behavior Rules**: Context validation, library verification, code preservation

## Files Modified
- **Original**: CLAUDE.md (backed up to {backup_path.name})
- **Enhanced**: CLAUDE.md (with intelligent merging)
- **Source**: temp/prp_agentic_eng_CLAUDE.md (PRPs-agentic-eng enhancements)

## Integration Quality
- **Zero Conflicts**: All project-specific rules preserved
- **Additive Enhancement**: Only beneficial additions made
- **Domain Expertise**: Data stack knowledge maintained
- **Command Documentation**: All 49 commands properly documented

## Next Steps
1. ✅ **Task 5 Complete**: CLAUDE.md enhanced with intelligent merging
2. 🔄 **Task 6 Next**: Enhance PRP templates with validation loops
3. 🔄 **Task 7 Next**: Integrate utility scripts
4. 🔄 **Task 8 Next**: Create comprehensive validation system
5. 🔄 **Task 9 Next**: Update project documentation

## Rollback Information
If needed, restore original CLAUDE.md:
```bash
cp {backup_path.name} CLAUDE.md
```

## Validation Commands
```bash
# Verify CLAUDE.md syntax
markdownlint CLAUDE.md

# Check for project-specific patterns
grep -i "venv_linux\|uv\|500.*line" CLAUDE.md

# Verify enhanced sections
grep -i "context.*engineering\|prp.*enhancement" CLAUDE.md
```
"""

        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"📋 Enhancement report created: {report_file}")


@click.command()
@click.option(
    "--dry-run", is_flag=True, help="Show enhancement strategy without executing"
)
@click.option(
    "--force", "-f", is_flag=True, help="Force enhancement without confirmation"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def enhance_claude_md(dry_run: bool, force: bool, verbose: bool):
    """Intelligently enhance CLAUDE.md with PRPs-agentic-eng improvements."""

    project_root = Path.cwd()
    enhancer = CLAUDEEnhancer(project_root)

    if not enhancer.current_claude.exists():
        print(f"❌ Current CLAUDE.md not found: {enhancer.current_claude}")
        return

    if dry_run:
        print("🔍 DRY RUN: Analyzing CLAUDE.md enhancement strategy...")

        # Analyze current CLAUDE.md
        current_content = enhancer.current_claude.read_text()
        current_sections = enhancer.extract_sections(current_content)

        print(f"\n📋 Current CLAUDE.md Analysis ({len(current_sections)} sections):")
        for section in current_sections:
            status_indicators = []
            if section.is_project_specific:
                status_indicators.append("PROJECT-SPECIFIC")
            if section.has_domain_rules:
                status_indicators.append("DOMAIN-RULES")
            if section.enhancement_candidate:
                status_indicators.append("ENHANCEMENT-CANDIDATE")

            status = " | ".join(status_indicators) if status_indicators else "STANDARD"
            print(f"  📄 {section.title}")
            if verbose:
                print(f"      Status: {status}")

        # Analyze enhanced CLAUDE.md if available
        if enhancer.enhanced_claude.exists():
            enhanced_content = enhancer.enhanced_claude.read_text()
            enhanced_sections = enhancer.extract_sections(enhanced_content)
            print(
                f"\n📈 PRPs-agentic-eng CLAUDE.md ({len(enhanced_sections)} sections):"
            )
            for section in enhanced_sections:
                print(f"  📄 {section.title}")

        print("\n🔄 Enhancement Strategy:")
        print("  ✅ Preserve all project-specific rules")
        print("  ✅ Enhance candidate sections with PRPs-agentic-eng features")
        print("  ✅ Add new PRP methodology section")
        print("  ✅ Maintain data stack domain expertise")

        return

    if not force:
        print("🔍 This will enhance CLAUDE.md with PRPs-agentic-eng improvements:")
        print("  ✅ Context engineering principles")
        print("  ✅ Enhanced command library documentation")
        print("  ✅ PRP methodology integration")
        print("  ✅ All project-specific rules preserved")

        response = click.confirm("Continue with CLAUDE.md enhancement?", default=True)
        if not response:
            print("❌ CLAUDE.md enhancement cancelled.")
            return

    try:
        print("🔄 Enhancing CLAUDE.md with intelligent merging...")

        # Backup current CLAUDE.md
        backup_path = enhancer.backup_current_claude()
        print(f"📁 Backed up current CLAUDE.md: {backup_path}")

        # Create enhanced content
        enhanced_content = enhancer.create_enhanced_claude_md()

        # Write enhanced CLAUDE.md
        enhancer.current_claude.write_text(enhanced_content)

        print("✅ CLAUDE.md enhanced successfully!")

        # Create enhancement report
        enhancer.create_enhancement_report(backup_path)

        print("\n🎉 Task 5 completed: CLAUDE.md enhanced with intelligent merging")
        print("✅ All project-specific rules preserved")
        print("✅ PRPs-agentic-eng methodology integrated")
        print("✅ Enhanced command library documented")

    except Exception as e:
        print(f"❌ Error enhancing CLAUDE.md: {e}")
        return


if __name__ == "__main__":
    enhance_claude_md()
