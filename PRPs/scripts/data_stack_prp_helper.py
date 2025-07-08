#!/usr/bin/env python3
"""
Data Stack PRP Integration Helper

Provides enhanced integration between PRPs and data stack workflows.
"""

import os
import subprocess
from pathlib import Path

import click
from pydantic import BaseModel


class DataStackContext(BaseModel):
    """Context for data stack PRP execution."""

    project_root: Path
    virtual_env: str = "venv_linux"
    cost_target: float = 50.0
    quality_threshold: float = 0.85
    agent_patterns: list[str] = ["agent.py", "tools.py", "prompts.py"]


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
            "cost.*optimization",
        ]

        import re

        for section in required_sections:
            if not re.search(section, content, re.IGNORECASE):
                click.echo(f"⚠️  Missing data stack section: {section}", err=True)
                return False

        return True

    def execute_prp_with_context(
        self, prp_path: Path, interactive: bool = True
    ) -> None:
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

        cmd = ["python", str(runner_path), "--prp-path", str(prp_path)]

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
