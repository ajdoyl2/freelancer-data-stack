#!/usr/bin/env python3
"""
UV Health Check Script
Daily health monitoring for UV-based projects

This script provides continuous monitoring and validation
for UV-based Python projects, ensuring environment integrity
and detecting issues early.
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
class HealthCheckResult:
    """Result of a health check"""

    name: str
    status: str  # "passed", "failed", "warning"
    message: str
    execution_time: float
    details: str | None = None


class UVHealthChecker:
    """Health checker for UV-based projects"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: list[HealthCheckResult] = []

    def run_check(
        self, command: str, name: str, timeout: int = 30
    ) -> HealthCheckResult:
        """Run a health check command"""
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

            if result.returncode == 0:
                return HealthCheckResult(
                    name=name,
                    status="passed",
                    message="✅ PASSED",
                    execution_time=execution_time,
                    details=result.stdout.strip()[:200] if result.stdout else None,
                )
            else:
                return HealthCheckResult(
                    name=name,
                    status="failed",
                    message="❌ FAILED",
                    execution_time=execution_time,
                    details=result.stderr.strip()[:200] if result.stderr else None,
                )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return HealthCheckResult(
                name=name,
                status="failed",
                message="⏰ TIMEOUT",
                execution_time=execution_time,
                details=f"Command timed out after {timeout}s",
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return HealthCheckResult(
                name=name,
                status="failed",
                message="💥 ERROR",
                execution_time=execution_time,
                details=str(e),
            )

    def check_uv_installation(self) -> list[HealthCheckResult]:
        """Check UV installation and basic functionality"""
        checks = [
            ("uv --version", "UV Installation"),
            ("uv python --version", "UV Python Management"),
            ("uv pip --version", "UV Pip Functionality"),
        ]

        results = []
        for command, name in checks:
            result = self.run_check(command, name)
            results.append(result)

        return results

    def check_project_environment(self) -> list[HealthCheckResult]:
        """Check project environment health"""
        checks = [
            ("uv pip check", "Dependency Conflicts"),
            ("uv lock --check", "Lockfile Validation"),
            ("uv sync --check", "Environment Sync"),
            (
                "uv pip list | grep -E '(missing|broken)' || echo 'No broken packages'",
                "Package Integrity",
            ),
        ]

        results = []
        for command, name in checks:
            result = self.run_check(command, name)
            results.append(result)

        return results

    def check_development_tools(self) -> list[HealthCheckResult]:
        """Check development tools availability"""
        results = []

        # Check if pyproject.toml exists and parse tools
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            results.append(
                HealthCheckResult(
                    name="Project Configuration",
                    status="warning",
                    message="⚠️ pyproject.toml not found",
                    execution_time=0.0,
                    details="No pyproject.toml found in project root",
                )
            )
            return results

        # Read pyproject.toml to determine available tools
        try:
            pyproject_content = pyproject_path.read_text()

            # Check common development tools
            tool_checks = []
            if "ruff" in pyproject_content:
                tool_checks.append(("uv run ruff --version", "Ruff Linter"))
            if "mypy" in pyproject_content:
                tool_checks.append(("uv run mypy --version", "MyPy Type Checker"))
            if "black" in pyproject_content:
                tool_checks.append(("uv run black --version", "Black Formatter"))
            if "pytest" in pyproject_content:
                tool_checks.append(("uv run pytest --version", "Pytest Testing"))

            # Check data stack tools
            if "duckdb" in pyproject_content:
                tool_checks.append(
                    (
                        "uv run python -c \"import duckdb; print(f'DuckDB {duckdb.__version__}')\"",
                        "DuckDB",
                    )
                )
            if "pandas" in pyproject_content:
                tool_checks.append(
                    (
                        "uv run python -c \"import pandas; print(f'Pandas {pandas.__version__}')\"",
                        "Pandas",
                    )
                )
            if "streamlit" in pyproject_content:
                tool_checks.append(("uv run streamlit --version", "Streamlit"))
            if "dbt-core" in pyproject_content:
                tool_checks.append(("uv run dbt --version", "dbt"))

            # Run tool checks
            for command, name in tool_checks:
                result = self.run_check(command, name)
                results.append(result)

        except Exception as e:
            results.append(
                HealthCheckResult(
                    name="Project Configuration",
                    status="failed",
                    message="❌ Failed to parse pyproject.toml",
                    execution_time=0.0,
                    details=str(e),
                )
            )

        return results

    def check_data_stack_health(self) -> list[HealthCheckResult]:
        """Check data stack specific health"""
        results = []

        # Check for data stack directories
        data_stack_dirs = [
            "data_stack",
            "transformation",
            "meltano",
            "dbt",
            "notebooks",
        ]

        for dir_name in data_stack_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                result = HealthCheckResult(
                    name=f"Data Stack Directory: {dir_name}",
                    status="passed",
                    message="✅ EXISTS",
                    execution_time=0.0,
                    details=f"Directory {dir_name} is present",
                )
            else:
                result = HealthCheckResult(
                    name=f"Data Stack Directory: {dir_name}",
                    status="warning",
                    message="⚠️ MISSING",
                    execution_time=0.0,
                    details=f"Directory {dir_name} not found (may be optional)",
                )
            results.append(result)

        # Check for data stack configuration files
        config_files = ["docker-compose.yml", "dbt_project.yml", "meltano.yml"]

        for file_name in config_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                result = HealthCheckResult(
                    name=f"Config File: {file_name}",
                    status="passed",
                    message="✅ EXISTS",
                    execution_time=0.0,
                    details=f"Configuration file {file_name} is present",
                )
            else:
                result = HealthCheckResult(
                    name=f"Config File: {file_name}",
                    status="warning",
                    message="⚠️ MISSING",
                    execution_time=0.0,
                    details=f"Configuration file {file_name} not found (may be optional)",
                )
            results.append(result)

        return results

    def check_performance_metrics(self) -> list[HealthCheckResult]:
        """Check performance metrics"""
        results = []

        # Benchmark common operations
        performance_checks = [
            ("time uv pip list > /dev/null", "Package List Performance"),
            ("time uv lock --check", "Lockfile Check Performance"),
            ("time uv sync --check", "Sync Check Performance"),
        ]

        for command, name in performance_checks:
            result = self.run_check(command, name)

            # Adjust status based on execution time
            if result.status == "passed":
                if result.execution_time < 1.0:
                    result.message = f"✅ FAST ({result.execution_time:.2f}s)"
                elif result.execution_time < 5.0:
                    result.message = f"✅ GOOD ({result.execution_time:.2f}s)"
                    result.status = "warning"
                else:
                    result.message = f"⚠️ SLOW ({result.execution_time:.2f}s)"
                    result.status = "warning"

            results.append(result)

        return results

    def run_health_check(self, include_performance: bool = True) -> dict[str, Any]:
        """Run comprehensive health check"""
        print("🔍 Running UV Health Check...")
        start_time = time.time()

        health_groups = [
            ("UV Installation", self.check_uv_installation),
            ("Project Environment", self.check_project_environment),
            ("Development Tools", self.check_development_tools),
            ("Data Stack Health", self.check_data_stack_health),
        ]

        if include_performance:
            health_groups.append(
                ("Performance Metrics", self.check_performance_metrics)
            )

        all_results = []
        group_summaries = {}

        for group_name, check_func in health_groups:
            print(f"\n📋 {group_name}...")
            group_results = check_func()
            all_results.extend(group_results)

            # Print individual results
            for result in group_results:
                print(f"   {result.name}: {result.message}")
                if result.details and result.status == "failed":
                    print(f"      Details: {result.details}")

            # Calculate group summary
            passed = sum(1 for r in group_results if r.status == "passed")
            failed = sum(1 for r in group_results if r.status == "failed")
            warnings = sum(1 for r in group_results if r.status == "warning")
            total = len(group_results)

            group_summaries[group_name] = {
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "total": total,
            }

        # Calculate overall summary
        total_time = time.time() - start_time
        passed_checks = sum(1 for r in all_results if r.status == "passed")
        failed_checks = sum(1 for r in all_results if r.status == "failed")
        warning_checks = sum(1 for r in all_results if r.status == "warning")
        total_checks = len(all_results)

        health_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "warning_checks": warning_checks,
                "health_score": health_score,
                "total_time": total_time,
            },
            "group_summaries": group_summaries,
            "detailed_results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "execution_time": r.execution_time,
                    "details": r.details,
                }
                for r in all_results
            ],
        }

        return report

    def create_health_report(self, report: dict[str, Any]) -> None:
        """Create health check report"""

        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)

        # Generate timestamp for report
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # Create JSON report
        json_report_file = reports_dir / f"uv_health_check_{timestamp}.json"
        with open(json_report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Create markdown report
        markdown_report_file = reports_dir / f"uv_health_check_{timestamp}.md"

        markdown_content = f"""# UV Health Check Report

## Summary
**Generated**: {report['timestamp']}
**Health Score**: {report['summary']['health_score']:.1f}%
**Total Checks**: {report['summary']['total_checks']}
**Passed**: {report['summary']['passed_checks']}
**Failed**: {report['summary']['failed_checks']}
**Warnings**: {report['summary']['warning_checks']}
**Execution Time**: {report['summary']['total_time']:.2f}s

## Health Status
"""

        if report["summary"]["health_score"] >= 90:
            markdown_content += "🟢 **HEALTHY** - System is operating normally\n\n"
        elif report["summary"]["health_score"] >= 70:
            markdown_content += "🟡 **DEGRADED** - Minor issues detected\n\n"
        else:
            markdown_content += (
                "🔴 **UNHEALTHY** - Multiple issues require attention\n\n"
            )

        # Group summaries
        markdown_content += "## Group Results\n\n"
        for group_name, summary in report["group_summaries"].items():
            passed = summary["passed"]
            failed = summary["failed"]
            warnings = summary["warnings"]

            if failed > 0:
                status_icon = "❌"
            elif warnings > 0:
                status_icon = "⚠️"
            else:
                status_icon = "✅"

            markdown_content += f"- **{group_name}**: {status_icon} {passed} passed, {failed} failed, {warnings} warnings\n"

        # Detailed results
        markdown_content += "\n## Detailed Results\n\n"
        for result in report["detailed_results"]:
            status_icon = {"passed": "✅", "failed": "❌", "warning": "⚠️"}[
                result["status"]
            ]
            markdown_content += f"### {status_icon} {result['name']}\n"
            markdown_content += f"- **Status**: {result['status'].upper()}\n"
            markdown_content += f"- **Time**: {result['execution_time']:.2f}s\n"

            if result["details"]:
                markdown_content += f"- **Details**: {result['details']}\n"

            markdown_content += "\n"

        # Recommendations
        markdown_content += "## Recommendations\n\n"

        if report["summary"]["failed_checks"] > 0:
            markdown_content += "### Critical Issues\n"
            failed_results = [
                r for r in report["detailed_results"] if r["status"] == "failed"
            ]
            for result in failed_results:
                markdown_content += (
                    f"- **{result['name']}**: {result['details'] or 'Check failed'}\n"
                )
            markdown_content += "\n"

        if report["summary"]["warning_checks"] > 0:
            markdown_content += "### Warnings\n"
            warning_results = [
                r for r in report["detailed_results"] if r["status"] == "warning"
            ]
            for result in warning_results:
                markdown_content += f"- **{result['name']}**: {result['details'] or 'Warning detected'}\n"
            markdown_content += "\n"

        markdown_content += """### General Recommendations
1. **Run health checks regularly** (daily or before major operations)
2. **Monitor performance trends** to detect degradation early
3. **Keep UV updated** to latest version for bug fixes and improvements
4. **Review failed checks** and address underlying issues
5. **Setup automated health monitoring** in CI/CD pipeline

## Next Steps
- Address any failed checks immediately
- Investigate performance issues if execution times are high
- Setup automated health check scheduling
- Monitor health score trends over time

## Health Check Commands
```bash
# Quick health check
python scripts/uv_health_check.py --quick

# Full health check with performance
python scripts/uv_health_check.py --full

# Generate report
python scripts/uv_health_check.py --full --report
```

---
*Generated by UV Health Check v1.0*
"""

        with open(markdown_report_file, "w") as f:
            f.write(markdown_content)

        print(f"📋 Health report created: {markdown_report_file}")
        print(f"📊 JSON report created: {json_report_file}")


@click.command()
@click.option("--quick", is_flag=True, help="Run quick health check (skip performance)")
@click.option(
    "--full", is_flag=True, help="Run full health check including performance"
)
@click.option("--report", is_flag=True, help="Generate health report")
@click.option("--json", is_flag=True, help="Output JSON format")
@click.option("--quiet", "-q", is_flag=True, help="Quiet output (errors only)")
def main(quick: bool, full: bool, report: bool, json: bool, quiet: bool):
    """UV Health Check Tool"""

    project_root = Path.cwd()
    health_checker = UVHealthChecker(project_root)

    if not any([quick, full]):
        print("🔍 UV Health Check Tool")
        print("Usage: python scripts/uv_health_check.py [OPTIONS]")
        print("\nOptions:")
        print("  --quick    Run quick health check (skip performance)")
        print("  --full     Run full health check including performance")
        print("  --report   Generate health report")
        print("  --json     Output JSON format")
        print("  --quiet    Quiet output (errors only)")
        return

    include_performance = full
    health_report = health_checker.run_health_check(include_performance)

    if not quiet:
        print("\n📊 Health Check Summary:")
        print(f"   Health Score: {health_report['summary']['health_score']:.1f}%")
        print(f"   Total checks: {health_report['summary']['total_checks']}")
        print(f"   Passed: {health_report['summary']['passed_checks']}")
        print(f"   Failed: {health_report['summary']['failed_checks']}")
        print(f"   Warnings: {health_report['summary']['warning_checks']}")
        print(f"   Execution time: {health_report['summary']['total_time']:.2f}s")

    if json:
        import json as json_module

        print(json_module.dumps(health_report, indent=2))

    if report:
        health_checker.create_health_report(health_report)

    # Determine exit code
    if health_report["summary"]["failed_checks"] > 0:
        if not quiet:
            print("\n🔴 Health check failed - address critical issues")
        sys.exit(1)
    elif health_report["summary"]["warning_checks"] > 0:
        if not quiet:
            print("\n⚠️ Health check passed with warnings")
        sys.exit(0)
    else:
        if not quiet:
            print("\n🎉 All health checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
