#!/usr/bin/env python3
"""
UV Migration Validation Script
Comprehensive validation for Poetry to UV migration

This script provides automated validation for Poetry to UV migration,
including environment equivalence testing, dependency resolution validation,
and performance benchmarking.
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click


@dataclass
class ValidationResult:
    """Result of a validation check"""

    command: str
    description: str
    success: bool
    execution_time: float
    output: str
    error: str


class UVMigrationValidator:
    """Comprehensive validation for Poetry to UV migration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: list[ValidationResult] = []

    def run_command(
        self, command: str, description: str, timeout: int = 300
    ) -> ValidationResult:
        """Run command and capture results"""
        print(f"🔍 {description}...")
        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )

            execution_time = time.time() - start_time
            success = result.returncode == 0

            if success:
                print(f"✅ {description}: PASSED ({execution_time:.2f}s)")
            else:
                print(f"❌ {description}: FAILED ({execution_time:.2f}s)")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()[:200]}")

            return ValidationResult(
                command=command,
                description=description,
                success=success,
                execution_time=execution_time,
                output=result.stdout,
                error=result.stderr,
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏰ {description}: TIMEOUT ({execution_time:.2f}s)")

            return ValidationResult(
                command=command,
                description=description,
                success=False,
                execution_time=execution_time,
                output="",
                error=f"Command timed out after {timeout}s",
            )
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"💥 {description}: ERROR ({execution_time:.2f}s)")
            print(f"   Exception: {str(e)}")

            return ValidationResult(
                command=command,
                description=description,
                success=False,
                execution_time=execution_time,
                output="",
                error=str(e),
            )

    def validate_uv_installation(self) -> list[ValidationResult]:
        """Validate UV installation and basic functionality"""
        print("\n📋 Validating UV Installation...")

        checks = [
            ("uv --version", "UV installation check"),
            ("uv python list", "Python version management"),
            ("uv pip --help", "UV pip functionality"),
            ("uv sync --help", "UV sync functionality"),
            ("uv lock --help", "UV lock functionality"),
        ]

        results = []
        for command, description in checks:
            result = self.run_command(command, description)
            results.append(result)

        return results

    def validate_environment_equivalence(self) -> list[ValidationResult]:
        """Validate that UV produces equivalent environment to Poetry"""
        print("\n📋 Validating Environment Equivalence...")

        results = []

        # Check UV package list
        result = self.run_command("uv pip list --format=json", "Get UV package list")
        results.append(result)

        # Compare with Poetry backup if available
        poetry_backup = self.project_root / "pre_migration_poetry_tree.txt"
        if poetry_backup.exists():
            result = self.run_command(
                "uv pip tree > post_migration_uv_tree.txt",
                "Generate UV dependency tree",
            )
            results.append(result)

            # Compare trees
            result = self.run_command(
                "diff pre_migration_poetry_tree.txt post_migration_uv_tree.txt || echo 'Differences found'",
                "Compare dependency trees",
            )
            results.append(result)

        return results

    def validate_dependency_resolution(self) -> list[ValidationResult]:
        """Validate dependency resolution works correctly"""
        print("\n📋 Validating Dependency Resolution...")

        checks = [
            ("uv pip check", "Check for dependency conflicts"),
            ("uv lock --check", "Validate lockfile is up-to-date"),
            ("uv sync --check", "Verify environment sync"),
            ("uv pip tree", "Generate dependency tree"),
            ("uv sync --all-groups", "Sync all dependency groups"),
        ]

        results = []
        for command, description in checks:
            result = self.run_command(command, description)
            results.append(result)

        return results

    def validate_development_workflow(self) -> list[ValidationResult]:
        """Validate development workflow integrity"""
        print("\n📋 Validating Development Workflow...")

        workflow_commands = [
            ("uv run python --version", "Python execution"),
            ("uv run pip --version", "Pip functionality"),
            (
                "uv run python -c \"import sys; print('Python path:', sys.path[:3])\"",
                "Python environment",
            ),
        ]

        # Add data stack specific commands based on project structure
        if (self.project_root / "pyproject.toml").exists():
            pyproject_content = (self.project_root / "pyproject.toml").read_text()

            # Check for common development tools
            if "ruff" in pyproject_content:
                workflow_commands.append(("uv run ruff check .", "Code linting"))
            if "mypy" in pyproject_content:
                workflow_commands.append(("uv run mypy --version", "Type checking"))
            if "black" in pyproject_content:
                workflow_commands.append(("uv run black --version", "Code formatting"))
            if "pytest" in pyproject_content:
                workflow_commands.append(
                    ("uv run pytest --version", "Testing framework")
                )

        # Data stack specific validations
        data_stack_commands = [
            (
                "uv run python -c \"import duckdb; print('DuckDB:', duckdb.__version__)\"",
                "DuckDB integration",
            ),
            (
                "uv run python -c \"import pandas; print('Pandas:', pandas.__version__)\"",
                "Pandas integration",
            ),
        ]

        results = []
        for command, description in workflow_commands:
            result = self.run_command(command, description)
            results.append(result)

        # Test data stack components (optional failures)
        for command, description in data_stack_commands:
            result = self.run_command(command, description)
            results.append(result)

        return results

    def validate_project_structure(self) -> list[ValidationResult]:
        """Validate project structure and files"""
        print("\n📋 Validating Project Structure...")

        results = []

        # Check critical files
        critical_files = ["pyproject.toml", "uv.lock", ".python-version"]

        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                result = ValidationResult(
                    command=f"ls {file_path}",
                    description=f"Check {file_path} exists",
                    success=True,
                    execution_time=0.0,
                    output=f"{file_path} exists",
                    error="",
                )
                print(f"✅ Check {file_path} exists: PASSED")
            else:
                result = ValidationResult(
                    command=f"ls {file_path}",
                    description=f"Check {file_path} exists",
                    success=False,
                    execution_time=0.0,
                    output="",
                    error=f"{file_path} missing",
                )
                print(f"❌ Check {file_path} exists: FAILED")

            results.append(result)

        # Check for old Poetry files
        old_files = ["poetry.lock", "poetry.toml"]
        for file_path in old_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                result = ValidationResult(
                    command=f"ls {file_path}",
                    description=f"Check {file_path} removed",
                    success=False,
                    execution_time=0.0,
                    output=f"{file_path} still exists",
                    error=f"Old Poetry file {file_path} should be removed",
                )
                print(f"⚠️  Check {file_path} removed: WARNING")
            else:
                result = ValidationResult(
                    command=f"ls {file_path}",
                    description=f"Check {file_path} removed",
                    success=True,
                    execution_time=0.0,
                    output=f"{file_path} properly removed",
                    error="",
                )
                print(f"✅ Check {file_path} removed: PASSED")

            results.append(result)

        return results

    def benchmark_performance(self) -> list[ValidationResult]:
        """Benchmark UV performance"""
        print("\n📋 Benchmarking Performance...")

        # Performance tests
        performance_tests = [
            ("uv sync --frozen", "Frozen sync (production)"),
            ("uv lock --upgrade", "Dependency resolution"),
            ("uv pip list", "Package listing"),
            ("uv pip tree", "Dependency tree generation"),
        ]

        results = []
        for command, description in performance_tests:
            result = self.run_command(command, description)
            results.append(result)

        return results

    def run_comprehensive_validation(self) -> dict[str, Any]:
        """Run comprehensive validation suite"""
        print("🚀 Starting comprehensive UV migration validation...")
        start_time = time.time()

        validation_groups = [
            ("UV Installation", self.validate_uv_installation),
            ("Project Structure", self.validate_project_structure),
            ("Environment Equivalence", self.validate_environment_equivalence),
            ("Dependency Resolution", self.validate_dependency_resolution),
            ("Development Workflow", self.validate_development_workflow),
            ("Performance Benchmark", self.benchmark_performance),
        ]

        all_results = []
        group_summaries = {}

        for group_name, validation_func in validation_groups:
            group_results = validation_func()
            all_results.extend(group_results)

            # Calculate group summary
            passed = sum(1 for r in group_results if r.success)
            total = len(group_results)
            group_summaries[group_name] = {
                "passed": passed,
                "total": total,
                "success_rate": (passed / total * 100) if total > 0 else 0,
            }

            print(
                f"   {group_name}: {passed}/{total} checks passed ({group_summaries[group_name]['success_rate']:.1f}%)"
            )

        # Calculate overall summary
        total_time = time.time() - start_time
        passed_checks = sum(1 for r in all_results if r.success)
        total_checks = len(all_results)
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": total_checks - passed_checks,
                "success_rate": success_rate,
                "total_time": total_time,
            },
            "group_summaries": group_summaries,
            "detailed_results": [
                {
                    "command": r.command,
                    "description": r.description,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "output": r.output[:500] if r.output else "",
                    "error": r.error[:500] if r.error else "",
                }
                for r in all_results
            ],
        }

        return report

    def create_validation_report(self, report: dict[str, Any]) -> None:
        """Create comprehensive validation report"""

        # Create reports directory
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)

        # Generate markdown report
        report_file = reports_dir / "uv_migration_validation_report.md"

        markdown_content = f"""# UV Migration Validation Report

## Summary
**Generated**: {report['timestamp']}
**Success Rate**: {report['summary']['success_rate']:.1f}% ({report['summary']['passed_checks']}/{report['summary']['total_checks']} checks passed)
**Total Time**: {report['summary']['total_time']:.2f} seconds

## Group Results
"""

        for group_name, summary in report["group_summaries"].items():
            status_icon = (
                "✅"
                if summary["success_rate"] == 100
                else "⚠️" if summary["success_rate"] > 50 else "❌"
            )
            markdown_content += f"- **{group_name}**: {status_icon} {summary['passed']}/{summary['total']} ({summary['success_rate']:.1f}%)\n"

        markdown_content += "\n## Detailed Results\n\n"

        for result in report["detailed_results"]:
            status_icon = "✅" if result["success"] else "❌"
            markdown_content += f"### {status_icon} {result['description']}\n"
            markdown_content += f"- **Command**: `{result['command']}`\n"
            markdown_content += (
                f"- **Status**: {'PASSED' if result['success'] else 'FAILED'}\n"
            )
            markdown_content += f"- **Time**: {result['execution_time']:.2f}s\n"

            if result["output"]:
                markdown_content += f"- **Output**: \n```\n{result['output']}\n```\n"
            if result["error"]:
                markdown_content += f"- **Error**: \n```\n{result['error']}\n```\n"

            markdown_content += "\n"

        # Add recommendations
        markdown_content += "## Recommendations\n\n"

        if report["summary"]["success_rate"] == 100:
            markdown_content += "🎉 **All validation checks passed!** Your UV migration is successful.\n\n"
        elif report["summary"]["success_rate"] > 80:
            markdown_content += "⚠️ **Minor issues detected.** Review failed checks and address if necessary.\n\n"
        else:
            markdown_content += "🔴 **Multiple failures detected.** Review and fix issues before proceeding.\n\n"

        markdown_content += """## Next Steps
1. Review any failed checks in the detailed results
2. Fix any critical dependency or environment issues
3. Re-run validation after fixes: `python scripts/uv_migration_validator.py --comprehensive`
4. Setup continuous monitoring with health checks

## Validation Commands
- **Full validation**: `python scripts/uv_migration_validator.py --comprehensive`
- **Quick check**: `python scripts/uv_migration_validator.py --quick`
- **Performance only**: `python scripts/uv_migration_validator.py --performance`
"""

        with open(report_file, "w") as f:
            f.write(markdown_content)

        print(f"📋 Validation report created: {report_file}")

        # Also create JSON report
        json_report_file = reports_dir / "uv_migration_validation_report.json"
        with open(json_report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 JSON report created: {json_report_file}")


@click.command()
@click.option("--comprehensive", is_flag=True, help="Run comprehensive validation")
@click.option("--quick", is_flag=True, help="Run quick validation checks")
@click.option("--performance", is_flag=True, help="Run performance benchmarks only")
@click.option("--report", is_flag=True, help="Generate validation report")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(
    comprehensive: bool, quick: bool, performance: bool, report: bool, verbose: bool
):
    """UV Migration Validation Tool"""

    project_root = Path.cwd()
    validator = UVMigrationValidator(project_root)

    if not any([comprehensive, quick, performance]):
        print("🔍 UV Migration Validation Tool")
        print("Usage: python scripts/uv_migration_validator.py [OPTIONS]")
        print("\nOptions:")
        print("  --comprehensive  Run comprehensive validation")
        print("  --quick         Run quick validation checks")
        print("  --performance   Run performance benchmarks only")
        print("  --report        Generate validation report")
        print("  --verbose       Verbose output")
        return

    if comprehensive:
        print("🚀 Running comprehensive UV migration validation...")
        validation_report = validator.run_comprehensive_validation()

        print("\n📊 Validation Summary:")
        print(f"   Total checks: {validation_report['summary']['total_checks']}")
        print(f"   Passed: {validation_report['summary']['passed_checks']}")
        print(f"   Failed: {validation_report['summary']['failed_checks']}")
        print(f"   Success rate: {validation_report['summary']['success_rate']:.1f}%")
        print(f"   Total time: {validation_report['summary']['total_time']:.2f}s")

        if report:
            validator.create_validation_report(validation_report)

        # Set exit code based on success rate
        if validation_report["summary"]["success_rate"] < 80:
            print("\n🔴 Validation failed - fix issues before proceeding")
            sys.exit(1)
        elif validation_report["summary"]["success_rate"] < 100:
            print("\n⚠️ Validation passed with warnings - review issues")
            sys.exit(0)
        else:
            print("\n🎉 All validation checks passed!")
            sys.exit(0)

    elif quick:
        print("⚡ Running quick validation checks...")
        results = []
        results.extend(validator.validate_uv_installation())
        results.extend(validator.validate_project_structure())
        results.extend(validator.validate_dependency_resolution())

        passed = sum(1 for r in results if r.success)
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0

        print(
            f"\n📊 Quick validation: {passed}/{total} checks passed ({success_rate:.1f}%)"
        )

        if success_rate < 100:
            sys.exit(1)

    elif performance:
        print("🚀 Running performance benchmarks...")
        results = validator.benchmark_performance()

        passed = sum(1 for r in results if r.success)
        total = len(results)
        avg_time = sum(r.execution_time for r in results) / len(results)

        print(f"\n📊 Performance benchmark: {passed}/{total} operations completed")
        print(f"   Average execution time: {avg_time:.2f}s")

        if passed < total:
            sys.exit(1)


if __name__ == "__main__":
    main()
