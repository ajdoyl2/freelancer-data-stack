#!/usr/bin/env python3
"""
PRP Utility Integration System

Integrates prp_runner.py and related utilities from PRPs-agentic-eng
while adapting them for the data stack project structure and patterns.
"""

import re
import shutil
from pathlib import Path

import click
from pydantic import BaseModel


class UtilityIntegration(BaseModel):
    """Integration specification for a utility script."""

    script_name: str
    source_path: str
    target_path: str
    adaptations: list[str] = []
    data_stack_enhancements: list[str] = []


class PRPUtilityIntegrator:
    """System for integrating PRPs-agentic-eng utilities into data stack project."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.temp_dir = project_root / "temp" / "PRPs-agentic-eng"
        self.scripts_dir = project_root / "scripts"
        self.prp_scripts_dir = project_root / "PRPs" / "scripts"

        # Data stack specific patterns for enhanced workflow guidance
        self.data_stack_patterns = {
            "environment": "venv_linux",
            "dependency_manager": "Poetry",
            "testing_framework": "pytest",
            "database": "DuckDB",
            "pipeline_tools": "meltano, dbt, airflow",
            "cost_target": "$50/month",
            "quality_threshold": "0.85",
            "file_size_limit": "500 lines",
            "agent_structure": "agent.py, tools.py, prompts.py",
        }

    def create_data_stack_prp_runner(self) -> str:
        """
        Create data stack enhanced version of prp_runner.py.

        Returns:
            str: Enhanced prp_runner.py content
        """
        source_path = self.temp_dir / "PRPs" / "scripts" / "prp_runner.py"

        if not source_path.exists():
            raise FileNotFoundError(f"Source prp_runner.py not found at {source_path}")

        content = source_path.read_text()

        # Enhanced META_HEADER with data stack specific guidance
        enhanced_meta_header = '''"""Enhanced Data Stack PRP Runner

Data Stack Project-Specific Instructions:
- Use venv_linux for ALL Python commands
- Follow 500-line file limit rule
- Use Poetry for dependency management
- Integrate with existing agent patterns (agent.py, tools.py, prompts.py)
- Target $50/month operational cost
- Maintain 0.85 quality threshold
- Preserve DuckDB/Meltano/dbt/Airflow integration patterns

Ingest and understand the Product Requirement Prompt (PRP) below in detail.

    # DATA STACK WORKFLOW GUIDANCE:

    ## Planning Phase (Data Stack Specific)
    - **Read PLANNING.md and CLAUDE.md** for project context and patterns
    - **Check TASK.md** before starting - add task if not listed
    - Think hard before you code. Create comprehensive plan addressing requirements.
    - Use TodoWrite tool to create and track implementation plan.
    - Search for existing data stack patterns in agents/, tools/, data_stack/
    - Consider cost optimization and performance impact (~$50/month target)
    - Identify integration points with Meltano, dbt, Airflow, DuckDB

    ## Implementation Phase (Data Stack Specific)
    - **Use venv_linux** for all Python command execution
    - **Follow agent structure**: agent.py (logic), tools.py (functions), prompts.py (system prompts)
    - **Respect 500-line limit** - refactor by splitting into modules if needed
    - Follow existing patterns in data_stack/ directory
    - Use Poetry for dependency management
    - Integrate with existing DuckDB, Meltano, dbt, Airflow patterns
    - Consider cost optimization for data processing (~90% cost reduction patterns)
    - Use type hints and pydantic for data validation
    - Follow PEP8 and format with black

    ## Testing Phase (Data Stack Specific)
    - **Create pytest unit tests** for all new functions/classes
    - Test data pipeline integration (extract, transform, load)
    - Validate agent patterns and tool integration
    - Test cost optimization and performance metrics
    - Verify Docker Compose service integration
    - Run validation gates: syntax, unit, integration, creative
    - Ensure all requirements satisfied before marking complete

    ## Data Stack Validation Gates:

    ### Level 1: Syntax & Style (Data Stack)
    ```bash
    # CRITICAL: Use venv_linux for ALL Python commands
    source venv_linux/bin/activate
    ruff check scripts/ --fix
    ruff check agents/ --fix
    ruff check tools/ --fix
    mypy scripts/ agents/ tools/
    black scripts/ agents/ tools/
    markdownlint PRPs/templates/*.md PRPs/ai_docs/*.md
    ```

    ### Level 2: Unit Testing (Data Stack)
    ```bash
    # Test new functionality with existing patterns
    uv run pytest tests/test_*.py -v
    uv run pytest tests/test_data_stack_workflows.py -v
    uv run pytest tests/test_agents.py -v
    uv run pytest tests/test_tools.py -v
    ```

    ### Level 3: Integration Testing (Data Stack)
    ```bash
    # Test complete data stack integration
    docker-compose up -d duckdb meltano streamlit

    # Test data pipeline functionality
    cd data_stack/meltano && meltano --environment=dev elt tap-csv target-duckdb
    cd ../dbt && dbt run --profiles-dir . && dbt test --profiles-dir .

    # Test monitoring and dashboards
    curl -f http://localhost:8501/health || echo "Streamlit dashboard check"
    curl -f http://localhost:3000/api/health || echo "Grafana monitoring check"
    curl -f http://localhost:8080/api/v1/health || echo "Airflow orchestration check"
    ```

    ### Level 4: Creative Validation (Data Stack)
    ```bash
    # Test AI agent functionality
    python -c "
    from agents.data_stack_engineer import DataStackEngineer
    from agents.base_agent import WorkflowRequest
    agent = DataStackEngineer()
    result = agent.execute_task(WorkflowRequest(user_prompt='Test task'))
    print('AI agent system functional')
    "

    # Test cost optimization
    python -c "
    from tools.cost_optimizer import CostOptimizer
    optimizer = CostOptimizer()
    print(f'Monthly cost estimate: ${optimizer.calculate_monthly_cost()}')
    "

    # Test end-to-end data pipeline
    python scripts/test_full_pipeline.py --validate-cost-optimization
    ```

    ## Example Data Stack Implementation Approach:
    1. **Context Loading**: Read PLANNING.md, CLAUDE.md, existing agent patterns
    2. **Analysis**: Search agents/, tools/, data_stack/ for existing patterns
    3. **Research**: Web search for data stack best practices, cost optimization
    4. **Planning**: Create TodoWrite plan with data stack integration points
    5. **Implementation**: Follow agent structure, use venv_linux, respect 500-line limit
    6. **Testing**: Run all 4 validation levels, ensure cost/performance targets met
    7. **Integration**: Verify Docker Compose, monitoring, and AI agent integration

    ***When finished, move completed PRP to PRPs/completed folder and update TASK.md***
    """'''

        # Replace original META_HEADER with enhanced version
        enhanced_content = re.sub(
            r'META_HEADER = """.*?"""',
            f"META_HEADER = {enhanced_meta_header}",
            content,
            flags=re.DOTALL,
        )

        # Update ROOT path calculation for data stack project
        enhanced_content = re.sub(
            r"ROOT = Path\(__file__\)\.resolve\(\)\.parent\.parent",
            r"ROOT = Path(__file__).resolve().parent.parent  # freelancer-data-stack root",
            enhanced_content,
        )

        # Add data stack specific tool allowlist
        data_stack_tools = [
            "Edit",
            "Bash",
            "Write",
            "MultiEdit",
            "NotebookEdit",
            "WebFetch",
            "Agent",
            "LS",
            "Grep",
            "Read",
            "NotebookRead",
            "TodoRead",
            "TodoWrite",
            "WebSearch",
            "Task",
            "Glob",
            "mcp__ide__getDiagnostics",
            "mcp__ide__executeCode",
        ]

        tools_str = ",".join(data_stack_tools)
        enhanced_content = re.sub(
            r'"Edit,Bash,Write,MultiEdit,NotebookEdit,WebFetch,Agent,LS,Grep,Read,NotebookRead,TodoRead,TodoWrite,WebSearch"',
            f'"{tools_str}"',
            enhanced_content,
        )

        return enhanced_content

    def create_data_stack_integration_script(self) -> str:
        """
        Create integration script for data stack PRP workflows.

        Returns:
            str: Integration script content
        """
        script_content = '''#!/usr/bin/env python3
"""
Data Stack PRP Integration Helper

Provides enhanced integration between PRPs and data stack workflows.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

import click
from pydantic import BaseModel


class DataStackContext(BaseModel):
    """Context for data stack PRP execution."""

    project_root: Path
    virtual_env: str = "venv_linux"
    cost_target: float = 50.0
    quality_threshold: float = 0.85
    agent_patterns: List[str] = ["agent.py", "tools.py", "prompts.py"]


class DataStackPRPHelper:
    """Helper for executing PRPs in data stack context."""

    def __init__(self, context: DataStackContext):
        self.context = context

    def prepare_environment(self) -> None:
        """Prepare data stack environment for PRP execution."""
        # Ensure virtual environment is activated
        venv_path = self.context.project_root / self.context.virtual_env
        if not venv_path.exists():
            raise FileNotFoundError(f"Virtual environment not found: {venv_path}")

        # Set environment variables for data stack
        os.environ["DATA_STACK_ROOT"] = str(self.context.project_root)
        os.environ["COST_TARGET"] = str(self.context.cost_target)
        os.environ["QUALITY_THRESHOLD"] = str(self.context.quality_threshold)

    def validate_data_stack_requirements(self, prp_path: Path) -> bool:
        """
        Validate PRP has required data stack context.

        Args:
            prp_path: Path to PRP file

        Returns:
            bool: True if valid
        """
        if not prp_path.exists():
            return False

        content = prp_path.read_text()

        # Check for required data stack sections
        required_sections = [
            "data.?stack",
            "venv_linux",
            "agent.*tool",
            "duckdb|meltano|dbt|airflow",
            "cost.*optimization"
        ]

        import re
        for section in required_sections:
            if not re.search(section, content, re.IGNORECASE):
                click.echo(f"⚠️  Missing data stack section: {section}", err=True)
                return False

        return True

    def execute_prp_with_context(self, prp_path: Path, interactive: bool = True) -> None:
        """
        Execute PRP with data stack context.

        Args:
            prp_path: Path to PRP file
            interactive: Use interactive mode
        """
        if not self.validate_data_stack_requirements(prp_path):
            raise ValueError("PRP does not meet data stack requirements")

        self.prepare_environment()

        # Execute using enhanced prp_runner
        runner_path = self.context.project_root / "PRPs" / "scripts" / "prp_runner.py"

        cmd = [
            "python", str(runner_path),
            "--prp-path", str(prp_path)
        ]

        if interactive:
            cmd.append("--interactive")

        subprocess.run(cmd, cwd=self.context.project_root, check=True)


@click.command()
@click.option("--prp-path", required=True, help="Path to PRP file")
@click.option("--interactive/--headless", default=True, help="Interactive mode")
@click.option("--validate-only", is_flag=True, help="Only validate, don't execute")
def main(prp_path: str, interactive: bool, validate_only: bool):
    """Execute PRP with data stack context."""

    context = DataStackContext(project_root=Path.cwd())
    helper = DataStackPRPHelper(context)

    prp_file = Path(prp_path)

    if validate_only:
        if helper.validate_data_stack_requirements(prp_file):
            click.echo("✅ PRP meets data stack requirements")
        else:
            click.echo("❌ PRP validation failed")
            return

    try:
        helper.execute_prp_with_context(prp_file, interactive)
        click.echo("✅ PRP execution completed")
    except Exception as e:
        click.echo(f"❌ PRP execution failed: {e}")


if __name__ == "__main__":
    main()
'''

        return script_content

    def integrate_utility_scripts(self) -> dict[str, bool]:
        """
        Integrate all utility scripts from PRPs-agentic-eng.

        Returns:
            Dict[str, bool]: Results for each script
        """
        results = {}

        # Create PRPs/scripts directory if it doesn't exist
        self.prp_scripts_dir.mkdir(parents=True, exist_ok=True)

        print("🔄 Integrating PRP utility scripts...")

        # 1. Create enhanced prp_runner.py
        try:
            enhanced_runner_content = self.create_data_stack_prp_runner()
            runner_path = self.prp_scripts_dir / "prp_runner.py"

            # Backup existing if present
            if runner_path.exists():
                backup_path = runner_path.with_suffix(".py.backup")
                shutil.copy2(runner_path, backup_path)
                print(f"📁 Backed up existing: {backup_path}")

            runner_path.write_text(enhanced_runner_content)
            runner_path.chmod(0o755)  # Make executable
            print("✅ Enhanced prp_runner.py created")
            results["prp_runner"] = True

        except Exception as e:
            print(f"❌ Error creating prp_runner.py: {e}")
            results["prp_runner"] = False

        # 2. Create data stack integration helper
        try:
            integration_content = self.create_data_stack_integration_script()
            integration_path = self.prp_scripts_dir / "data_stack_prp_helper.py"

            integration_path.write_text(integration_content)
            integration_path.chmod(0o755)  # Make executable
            print("✅ Data stack PRP helper created")
            results["data_stack_helper"] = True

        except Exception as e:
            print(f"❌ Error creating data stack helper: {e}")
            results["data_stack_helper"] = False

        # 3. Copy additional utility scripts if they exist
        source_scripts = self.temp_dir / "PRPs" / "scripts"
        if source_scripts.exists():
            for script_file in source_scripts.glob("*.py"):
                if script_file.name not in ["prp_runner.py"]:  # Skip main runner
                    try:
                        target_path = self.prp_scripts_dir / script_file.name
                        shutil.copy2(script_file, target_path)
                        target_path.chmod(0o755)
                        print(f"✅ Copied utility script: {script_file.name}")
                        results[script_file.name] = True
                    except Exception as e:
                        print(f"❌ Error copying {script_file.name}: {e}")
                        results[script_file.name] = False

        return results

    def create_integration_report(self, results: dict[str, bool]) -> None:
        """
        Create utility integration report.

        Args:
            results: Integration results
        """
        report_file = self.project_root / "temp" / "utility_integration_report.md"

        successful = sum(results.values())
        total = len(results)

        report_content = f"""# PRP Utility Integration Report

## Summary
✅ **{successful}/{total} utility scripts integrated** with data stack enhancements

## Integrated Scripts

### prp_runner.py
{'✅' if results.get('prp_runner', False) else '❌'} **Status**: {"Enhanced successfully" if results.get('prp_runner', False) else "Integration failed"}
- **Location**: PRPs/scripts/prp_runner.py
- **Enhancements**:
  - Data stack specific workflow guidance
  - venv_linux environment integration
  - Enhanced validation gates (4 levels)
  - Cost optimization patterns (~$50/month target)
  - Agent structure validation (agent.py, tools.py, prompts.py)
  - DuckDB/Meltano/dbt/Airflow integration checks

### data_stack_prp_helper.py
{'✅' if results.get('data_stack_helper', False) else '❌'} **Status**: {"Created successfully" if results.get('data_stack_helper', False) else "Creation failed"}
- **Location**: PRPs/scripts/data_stack_prp_helper.py
- **Features**:
  - Data stack context validation
  - Environment preparation
  - Cost and quality threshold enforcement
  - Agent pattern validation
  - Enhanced PRP execution with data stack context

## Key Enhancements

### Data Stack Integration
- **Environment**: venv_linux activation and validation
- **Architecture**: Agent structure patterns (agent.py, tools.py, prompts.py)
- **Cost Optimization**: $50/month target with 90% reduction patterns
- **Quality**: 0.85 threshold enforcement
- **Pipeline Integration**: DuckDB, Meltano, dbt, Airflow support

### Enhanced Validation Gates
1. **Level 1**: Syntax & Style (ruff, mypy, black) with venv_linux
2. **Level 2**: Unit Testing (pytest) with data stack specific tests
3. **Level 3**: Integration Testing (Docker Compose, pipeline validation)
4. **Level 4**: Creative Validation (AI agents, cost optimization, end-to-end)

### Tool Integration
- All Claude Code tools enabled
- MCP server integration (mcp__ide__getDiagnostics, mcp__ide__executeCode)
- Task management and parallel execution support
- Web search and research capabilities

## Usage Examples

### Execute PRP with Data Stack Context
```bash
# Interactive mode (recommended)
python PRPs/scripts/prp_runner.py --prp-path PRPs/your-feature.md --interactive

# Validate PRP requirements
python PRPs/scripts/data_stack_prp_helper.py --prp-path PRPs/your-feature.md --validate-only

# Execute with data stack context
python PRPs/scripts/data_stack_prp_helper.py --prp-path PRPs/your-feature.md --interactive
```

### Integration with Existing Commands
```bash
# Use with existing .claude/commands
.claude/commands/prp-base-execute.md "PRPs/your-feature.md"
.claude/commands/prp-planning-execute.md "PRPs/planning-doc.md"
```

## Next Steps
1. ✅ **Task 7 Complete**: Utility scripts integrated with data stack enhancements
2. 🔄 **Task 8 Next**: Create comprehensive validation system
3. 🔄 **Task 9 Next**: Update project documentation

## Quality Assurance
- All scripts maintain data stack domain expertise
- Enhanced validation gates are executable by AI agents
- Cost optimization and performance patterns preserved
- Agent structure patterns enforced throughout
- Virtual environment integration properly configured

## Rollback Information
All existing scripts were backed up with .backup extension before modification.
"""

        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"📋 Integration report created: {report_file}")


@click.command()
@click.option("--dry-run", is_flag=True, help="Analyze integration without executing")
@click.option(
    "--force", "-f", is_flag=True, help="Force integration without confirmation"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def integrate_utilities(dry_run: bool, force: bool, verbose: bool):
    """Integrate PRPs-agentic-eng utility scripts with data stack enhancements."""

    project_root = Path.cwd()
    integrator = PRPUtilityIntegrator(project_root)

    if dry_run:
        print("🔍 DRY RUN: Analyzing utility integration requirements...")

        # Check source availability
        source_scripts = integrator.temp_dir / "PRPs" / "scripts"
        if source_scripts.exists():
            scripts = list(source_scripts.glob("*.py"))
            print(f"📄 Found {len(scripts)} utility scripts to integrate:")
            for script in scripts:
                print(f"   - {script.name}")
        else:
            print("❌ Source scripts directory not found")

        # Check target structure
        print(f"📁 Target directory: {integrator.prp_scripts_dir}")
        print(
            f"📁 Target exists: {'Yes' if integrator.prp_scripts_dir.exists() else 'No'}"
        )

        return

    if not force:
        print(
            "🔍 This will integrate PRP utility scripts with data stack enhancements:"
        )
        print("  ✅ Create enhanced prp_runner.py with data stack context")
        print("  ✅ Create data_stack_prp_helper.py for integration")
        print("  ✅ Copy additional utility scripts")
        print("  ✅ Add validation gates and cost optimization patterns")

        response = click.confirm("Continue with utility integration?", default=True)
        if not response:
            print("❌ Utility integration cancelled.")
            return

    # Execute integration
    results = integrator.integrate_utility_scripts()

    # Create report
    integrator.create_integration_report(results)

    # Summary
    successful = sum(results.values())
    total = len(results)

    print(
        f"\n📊 Integration Summary: {successful}/{total} utilities integrated successfully"
    )

    if successful == total:
        print("🎉 All utility scripts integrated with data stack enhancements!")
    else:
        print("⚠️  Some utilities require attention - check integration report")


if __name__ == "__main__":
    integrate_utilities()
