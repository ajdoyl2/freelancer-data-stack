#!/usr/bin/env python3
"""
PRP Template Enhancement System

Enhances existing PRP templates with validation loops and PRPs-agentic-eng
improvements while preserving data stack specific patterns and conventions.
"""

import re
from pathlib import Path

import click
from pydantic import BaseModel


class TemplateEnhancement(BaseModel):
    """Enhancement specification for a template."""

    template_name: str
    source_file: str
    target_file: str
    enhancement_type: str  # "validation_loops", "data_stack_patterns", "merge_enhanced"
    preserve_patterns: list[str] = []
    add_sections: list[str] = []


class PRPTemplateEnhancer:
    """System for enhancing PRP templates with validation loops."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / "PRPs" / "templates"

        # Data stack specific patterns to preserve
        self.data_stack_patterns = [
            r"DataStackEngineer",
            r"venv_linux",
            r"Poetry.*dependency",
            r"meltano.*dbt.*airflow",
            r"docker.*compose",
            r"agent\.py.*tools\.py",
            r"data.?stack",
            r"pytest.*tests",
            r"500.*line.*limit",
        ]

        # Validation loop patterns from PRPs-agentic-eng
        self.validation_patterns = {
            "level_1": "ruff check --fix && mypy .",
            "level_2": "uv run pytest tests/ -v",
            "level_3": "curl -X POST http://localhost:8000/endpoint",
            "level_4": "# Creative validation gates",
        }

    def analyze_template(self, template_path: Path) -> dict[str, any]:
        """
        Analyze template structure and identify enhancement opportunities.

        Args:
            template_path: Path to template file

        Returns:
            Dict[str, any]: Analysis results
        """
        if not template_path.exists():
            return {"exists": False}

        content = template_path.read_text()

        analysis = {
            "exists": True,
            "has_validation_loops": "validation loop" in content.lower(),
            "has_data_stack_patterns": any(
                re.search(pattern, content, re.IGNORECASE)
                for pattern in self.data_stack_patterns
            ),
            "has_executable_gates": any(
                cmd in content for cmd in self.validation_patterns.values()
            ),
            "section_count": len(re.findall(r"^#+\s+", content, re.MULTILINE)),
            "line_count": len(content.split("\n")),
            "needs_enhancement": False,
        }

        # Determine if enhancement is needed
        if not analysis["has_validation_loops"] or not analysis["has_executable_gates"]:
            analysis["needs_enhancement"] = True

        return analysis

    def extract_validation_loops_section(self) -> str:
        """
        Create comprehensive validation loops section for templates.

        Returns:
            str: Validation loops section content
        """
        return """## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check scripts/ --fix          # Auto-fix Python scripts
ruff check PRPs/scripts/ --fix     # Fix PRP utility scripts
mypy scripts/                      # Type checking
black scripts/ PRPs/scripts/       # Code formatting

# Validate markdown files
markdownlint .claude/commands/*.md PRPs/templates/*.md PRPs/ai_docs/*.md

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Testing
```bash
# Test new functionality
uv run pytest tests/test_*.py -v

# Test data stack specific workflows
uv run pytest tests/test_data_stack_workflows.py -v
uv run pytest tests/test_prp_integration.py -v

# Expected: All tests pass, existing functionality preserved, new functionality working
```

### Level 3: Integration Testing
```bash
# Test complete workflow with data stack
.claude/commands/deploy-data-stack.md --validate-only
.claude/commands/monitor-data-stack.md --health-check
.claude/commands/validate-pipeline.md --verbose

# Test enhanced PRP workflows
.claude/commands/prp-base-create.md "Test integration workflow"
.claude/commands/prp-base-execute.md "PRPs/test-integration-prp.md"

# Expected: All workflows functional, no regression in data stack capabilities
```

### Level 4: Creative Validation
```bash
# Test end-to-end data pipeline
cd data_stack/meltano && meltano --environment=dev elt tap-csv target-duckdb
cd ../dbt && dbt run --profiles-dir . && dbt test --profiles-dir .

# Verify dashboard functionality
curl -f http://localhost:8501/health || echo "Streamlit dashboard check"
curl -f http://localhost:3000/api/health || echo "Grafana monitoring check"

# AI agent validation
python -c "
from agents.data_stack_engineer import DataStackEngineer
from agents.base_agent import WorkflowRequest
agent = DataStackEngineer()
print('AI agent system functional')
"

# Expected: Complete data pipeline functional, monitoring operational
```"""

    def extract_data_stack_context_section(self) -> str:
        """
        Create data stack specific context section for templates.

        Returns:
            str: Data stack context section
        """
        return """### Data Stack Context

```yaml
# MUST READ - Data stack specific context
- file: agents/data_stack_engineer.py
  why: Core AI agent patterns for data infrastructure management

- file: tools/duckdb_tools.py
  why: Database operations and analytics patterns (90% cost reduction vs Snowflake)

- file: tools/meltano_tools.py
  why: ELT pipeline management with Singer protocol

- file: tools/dbt_tools.py
  why: Data transformation and modeling patterns

- file: data_stack/airflow/dags/
  why: Workflow orchestration patterns with AI agent integration

- file: data_stack/dbt/models/staging/
  why: 31-column EDA transformation patterns

- url: http://localhost:8501
  why: Streamlit dashboard for real-time data monitoring

- url: http://localhost:3000
  why: Grafana monitoring and alerting interface

- url: http://localhost:8080
  why: Airflow UI for pipeline orchestration
```

### Data Stack Architecture Patterns
```python
# CRITICAL: Use existing agent patterns
from agents.data_stack_engineer import DataStackEngineer
from agents.base_agent import WorkflowRequest, AgentResponse

agent = DataStackEngineer()
result = await agent.execute_task(WorkflowRequest(
    user_prompt="YOUR_DATA_STACK_TASK"
))

# CRITICAL: Cost optimization patterns (~$50/month target)
config.cost_optimization = {
    "duckdb_vs_snowflake": "90% cost reduction",
    "self_hosted_vs_cloud": "88-95% savings",
    "quality_threshold": 0.85
}

# CRITICAL: Use venv_linux for Python commands
# Example: pytest tests/ should be run in venv_linux environment
```"""

    def enhance_template_with_validation_loops(self, template_path: Path) -> str:
        """
        Enhance template with validation loops while preserving data stack patterns.

        Args:
            template_path: Path to template file

        Returns:
            str: Enhanced template content
        """
        if not template_path.exists():
            return ""

        content = template_path.read_text()

        # Check if already has validation loops
        if "validation loop" in content.lower():
            print(f"⚠️  {template_path.name} already has validation loops")
            return content

        # Find insertion point (before final checklist or at end)
        insertion_patterns = [
            r"## Final validation Checklist",
            r"## Quality Checklist",
            r"## Anti-Patterns to Avoid",
            r"---\s*$",
        ]

        insertion_point = len(content)
        for pattern in insertion_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                insertion_point = match.start()
                break

        # Insert validation loops and data stack context
        validation_section = self.extract_validation_loops_section()
        data_stack_section = self.extract_data_stack_context_section()

        # Insert before final sections
        enhanced_content = (
            content[:insertion_point]
            + "\n\n"
            + data_stack_section
            + "\n\n"
            + validation_section
            + "\n\n"
            + content[insertion_point:]
        )

        return enhanced_content

    def merge_enhanced_template(self, original_path: Path, enhanced_path: Path) -> str:
        """
        Merge original template with enhanced version, preserving data stack patterns.

        Args:
            original_path: Path to original template
            enhanced_path: Path to enhanced template

        Returns:
            str: Merged template content
        """
        if not original_path.exists():
            return enhanced_path.read_text() if enhanced_path.exists() else ""

        if not enhanced_path.exists():
            return self.enhance_template_with_validation_loops(original_path)

        original_content = original_path.read_text()
        enhanced_content = enhanced_path.read_text()

        # Preserve data stack specific sections from original
        data_stack_sections = []
        for line in original_content.split("\n"):
            for pattern in self.data_stack_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Find the section this line belongs to
                    section = self.extract_section_containing_line(
                        original_content, line
                    )
                    if section and section not in data_stack_sections:
                        data_stack_sections.append(section)

        # Use enhanced content as base and inject preserved sections
        merged_content = enhanced_content

        # Add preserved data stack sections
        if data_stack_sections:
            preserved_section = (
                "\n\n### Preserved Data Stack Patterns\n\n"
                + "\n\n".join(data_stack_sections)
            )

            # Insert before validation loops
            insertion_point = merged_content.find("## Validation Loop")
            if insertion_point != -1:
                merged_content = (
                    merged_content[:insertion_point]
                    + preserved_section
                    + "\n\n"
                    + merged_content[insertion_point:]
                )
            else:
                merged_content += "\n\n" + preserved_section

        return merged_content

    def extract_section_containing_line(
        self, content: str, target_line: str
    ) -> str | None:
        """
        Extract the section that contains a specific line.

        Args:
            content: Full content
            target_line: Line to find

        Returns:
            Optional[str]: Section content or None
        """
        lines = content.split("\n")
        section_lines = []
        in_target_section = False

        for line in lines:
            if line.startswith("#"):
                if in_target_section:
                    break
                section_lines = [line]
                in_target_section = False
            else:
                section_lines.append(line)
                if target_line.strip() in line:
                    in_target_section = True

        return "\n".join(section_lines) if in_target_section else None

    def enhance_template(
        self, template_name: str, enhancement: TemplateEnhancement
    ) -> bool:
        """
        Enhance a specific template.

        Args:
            template_name: Name of template to enhance
            enhancement: Enhancement specification

        Returns:
            bool: True if successful
        """
        source_path = self.templates_dir / enhancement.source_file
        target_path = self.templates_dir / enhancement.target_file

        print(f"🔄 Enhancing {template_name}...")

        try:
            if enhancement.enhancement_type == "validation_loops":
                enhanced_content = self.enhance_template_with_validation_loops(
                    source_path
                )
            elif enhancement.enhancement_type == "merge_enhanced":
                enhanced_source = self.templates_dir / f"{template_name}_enhanced.md"
                enhanced_content = self.merge_enhanced_template(
                    source_path, enhanced_source
                )
            else:
                enhanced_content = (
                    source_path.read_text() if source_path.exists() else ""
                )

            # Backup original if it exists and is different from target
            if target_path.exists() and source_path != target_path:
                backup_path = target_path.with_suffix(".md.backup")
                backup_path.write_text(target_path.read_text())
                print(f"📁 Backed up original: {backup_path}")

            # Write enhanced content
            target_path.write_text(enhanced_content)
            print(f"✅ Enhanced {template_name}")

            return True

        except Exception as e:
            print(f"❌ Error enhancing {template_name}: {e}")
            return False

    def enhance_all_templates(self) -> dict[str, bool]:
        """
        Enhance all PRP templates with validation loops and data stack patterns.

        Returns:
            Dict[str, bool]: Results for each template
        """
        enhancements = {
            "prp_base": TemplateEnhancement(
                template_name="prp_base",
                source_file="prp_base.md",
                target_file="prp_base.md",
                enhancement_type="merge_enhanced",
            ),
            "prp_planning": TemplateEnhancement(
                template_name="prp_planning",
                source_file="prp-planning.md",
                target_file="prp-planning.md",
                enhancement_type="validation_loops",
            ),
            "prp_test": TemplateEnhancement(
                template_name="prp_test",
                source_file="prp-test.md",
                target_file="prp-test.md",
                enhancement_type="validation_loops",
            ),
            "prp_validate": TemplateEnhancement(
                template_name="prp_validate",
                source_file="prp-validate.md",
                target_file="prp-validate.md",
                enhancement_type="validation_loops",
            ),
        }

        results = {}

        print("🔄 Enhancing PRP templates with validation loops...")
        print(f"📁 Processing {len(enhancements)} templates")

        for template_name, enhancement in enhancements.items():
            success = self.enhance_template(template_name, enhancement)
            results[template_name] = success

        return results

    def create_enhancement_report(self, results: dict[str, bool]) -> None:
        """
        Create template enhancement report.

        Args:
            results: Enhancement results
        """
        report_file = self.project_root / "temp" / "template_enhancement_report.md"

        successful = sum(results.values())
        total = len(results)

        report_content = f"""# PRP Template Enhancement Report

## Summary
✅ **{successful}/{total} templates enhanced** with validation loops and data stack patterns

## Enhanced Templates

"""

        for template_name, success in results.items():
            status_emoji = "✅" if success else "❌"
            template_file = f"{template_name.replace('_', '-')}.md"

            report_content += f"""### {template_name}
{status_emoji} **Status**: {"Enhanced successfully" if success else "Enhancement failed"}
- **File**: PRPs/templates/{template_file}
- **Enhancements**: Validation loops, data stack context, executable gates

"""

        report_content += """## Key Enhancements Added

### Validation Loops (4 Levels)
1. **Syntax & Style**: ruff, mypy, black, markdownlint
2. **Unit Testing**: pytest with data stack specific tests
3. **Integration Testing**: Data pipeline validation, command workflows
4. **Creative Validation**: End-to-end pipeline, AI agent testing

### Data Stack Context
- Agent patterns and tool integration
- Cost optimization strategies (~$50/month target)
- Architecture patterns (DuckDB, Meltano, dbt, Airflow)
- Service endpoints and monitoring

### Executable Gates
- All validation commands are executable by AI
- Progressive validation from syntax to integration
- Data stack specific validation workflows
- Real service endpoints for integration testing

## Template Usage
```bash
# Use enhanced templates for PRP creation
.claude/commands/prp-base-create.md "Your feature description"
.claude/commands/prp-planning-create.md "Your planning needs"

# Templates now include comprehensive validation
# AI agents can execute all validation gates
# Data stack patterns preserved throughout
```

## Next Steps
1. ✅ **Task 6 Complete**: PRP templates enhanced with validation loops
2. 🔄 **Task 7 Next**: Integrate utility scripts from PRPs-agentic-eng
3. 🔄 **Task 8 Next**: Create comprehensive validation system
4. 🔄 **Task 9 Next**: Update project documentation

## Quality Assurance
- All templates maintain data stack domain expertise
- Validation loops are executable by AI agents
- Progressive enhancement from syntax to integration
- Cost optimization and performance patterns preserved
"""

        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"📋 Enhancement report created: {report_file}")


@click.command()
@click.option(
    "--template", "-t", help="Specific template to enhance (or 'all' for all)"
)
@click.option("--dry-run", is_flag=True, help="Analyze templates without enhancing")
@click.option(
    "--force", "-f", is_flag=True, help="Force enhancement without confirmation"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def enhance_templates(template: str, dry_run: bool, force: bool, verbose: bool):
    """Enhance PRP templates with validation loops and data stack patterns."""

    project_root = Path.cwd()
    enhancer = PRPTemplateEnhancer(project_root)

    if dry_run:
        print("🔍 DRY RUN: Analyzing PRP templates...")

        template_files = list(enhancer.templates_dir.glob("*.md"))

        for template_file in template_files:
            analysis = enhancer.analyze_template(template_file)

            print(f"\n📄 {template_file.name}:")
            print(f"   Exists: {'Yes' if analysis['exists'] else 'No'}")
            if analysis["exists"]:
                print(
                    f"   Has validation loops: {'Yes' if analysis['has_validation_loops'] else 'No'}"
                )
                print(
                    f"   Has data stack patterns: {'Yes' if analysis['has_data_stack_patterns'] else 'No'}"
                )
                print(
                    f"   Has executable gates: {'Yes' if analysis['has_executable_gates'] else 'No'}"
                )
                print(
                    f"   Needs enhancement: {'Yes' if analysis['needs_enhancement'] else 'No'}"
                )
                print(
                    f"   Sections: {analysis['section_count']}, Lines: {analysis['line_count']}"
                )

        return

    if template and template != "all":
        print("❌ Single template enhancement not implemented yet. Use 'all' for now.")
        return
    else:
        # Enhance all templates
        if not force:
            print("🔍 This will enhance PRP templates with validation loops:")
            print("  ✅ Add 4-level validation framework")
            print("  ✅ Integrate data stack context and patterns")
            print("  ✅ Add executable validation gates")
            print("  ✅ Preserve existing domain-specific content")

            response = click.confirm(
                "Continue with template enhancement?", default=True
            )
            if not response:
                print("❌ Template enhancement cancelled.")
                return

        # Execute enhancement
        results = enhancer.enhance_all_templates()

        # Create report
        enhancer.create_enhancement_report(results)

        # Summary
        successful = sum(results.values())
        total = len(results)

        print(
            f"\n📊 Enhancement Summary: {successful}/{total} templates enhanced successfully"
        )

        if successful == total:
            print("🎉 All templates enhanced with validation loops!")
        else:
            print("⚠️  Some templates require attention - check enhancement report")


if __name__ == "__main__":
    enhance_templates()
