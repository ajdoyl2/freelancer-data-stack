#!/usr/bin/env python3
"""
Automated Data Stack Deployment Script

This script provides automated deployment, validation, and management of the AI agent-driven data stack.
Integrates with the DataStackEngineer agent for comprehensive infrastructure management.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import click
import yaml
from pydantic import BaseModel, Field


class DeploymentConfig(BaseModel):
    """Configuration for data stack deployment."""

    project_root: Path = Field(default_factory=lambda: Path.cwd())
    environment: str = Field(default="dev")
    docker_compose_file: str = Field(default="docker-compose.yml")
    duckdb_path: str = Field(default="/data/duckdb/analytics.db")
    meltano_project_path: str = Field(default="data_stack/meltano")
    dbt_project_path: str = Field(default="data_stack/dbt")
    airflow_dags_path: str = Field(default="data_stack/airflow/dags")
    timeout_minutes: int = Field(default=30)
    health_check_retries: int = Field(default=10)
    health_check_interval: int = Field(default=30)
    enable_monitoring: bool = Field(default=True)
    enable_data_validation: bool = Field(default=True)
    force_rebuild: bool = Field(default=False)


class DeploymentStep(BaseModel):
    """Individual deployment step."""

    name: str
    description: str
    command: str | None = None
    function: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    timeout_seconds: int = Field(default=300)
    required: bool = Field(default=True)
    rollback_command: str | None = None


class DeploymentResult(BaseModel):
    """Result of deployment operation."""

    success: bool
    step_results: list[dict[str, Any]] = Field(default_factory=list)
    deployment_time_seconds: float = Field(default=0.0)
    services_deployed: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    health_check_results: dict[str, Any] = Field(default_factory=dict)
    next_actions: list[str] = Field(default_factory=list)


class DataStackDeployer:
    """Main deployment orchestrator for the AI agent data stack."""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.start_time = time.time()
        self.deployed_services = []
        self.deployment_steps = self._define_deployment_steps()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"deployment_{int(time.time())}.log"),
            ],
        )
        return logging.getLogger(__name__)

    def _define_deployment_steps(self) -> list[DeploymentStep]:
        """Define the complete deployment workflow."""
        return [
            DeploymentStep(
                name="validate_environment",
                description="Validate deployment environment and prerequisites",
                function="validate_environment",
                required=True,
            ),
            DeploymentStep(
                name="prepare_directories",
                description="Create required directories and set permissions",
                function="prepare_directories",
                required=True,
            ),
            DeploymentStep(
                name="start_docker_services",
                description="Start Docker Compose services",
                function="start_docker_services",
                depends_on=["prepare_directories"],
                timeout_seconds=600,
                required=True,
            ),
            DeploymentStep(
                name="wait_for_services",
                description="Wait for all services to be healthy",
                function="wait_for_services",
                depends_on=["start_docker_services"],
                timeout_seconds=600,
                required=True,
            ),
            DeploymentStep(
                name="initialize_duckdb",
                description="Initialize DuckDB database and schemas",
                function="initialize_duckdb",
                depends_on=["wait_for_services"],
                required=True,
            ),
            DeploymentStep(
                name="setup_meltano",
                description="Configure and validate Meltano project",
                function="setup_meltano",
                depends_on=["initialize_duckdb"],
                required=True,
            ),
            DeploymentStep(
                name="setup_dbt",
                description="Install dbt dependencies and compile models",
                function="setup_dbt",
                depends_on=["setup_meltano"],
                required=True,
            ),
            DeploymentStep(
                name="setup_airflow",
                description="Configure Airflow and deploy DAGs",
                function="setup_airflow",
                depends_on=["setup_dbt"],
                required=True,
            ),
            DeploymentStep(
                name="run_initial_pipeline",
                description="Execute initial data pipeline",
                function="run_initial_pipeline",
                depends_on=["setup_airflow"],
                required=False,
            ),
            DeploymentStep(
                name="validate_deployment",
                description="Run comprehensive deployment validation",
                function="validate_deployment",
                depends_on=["run_initial_pipeline"],
                required=True,
            ),
            DeploymentStep(
                name="setup_monitoring",
                description="Configure monitoring and alerting",
                function="setup_monitoring",
                depends_on=["validate_deployment"],
                required=False,
            ),
            DeploymentStep(
                name="generate_deployment_report",
                description="Generate deployment summary report",
                function="generate_deployment_report",
                depends_on=["setup_monitoring"],
                required=True,
            ),
        ]

    async def deploy(self) -> DeploymentResult:
        """Execute the complete deployment workflow."""
        self.logger.info("Starting AI Agent Data Stack deployment")
        self.logger.info(f"Environment: {self.config.environment}")
        self.logger.info(f"Project root: {self.config.project_root}")

        result = DeploymentResult(success=False)

        try:
            # Execute deployment steps in order
            for step in self.deployment_steps:
                self.logger.info(f"Executing step: {step.name}")

                # Check dependencies
                if not self._check_dependencies(step, result.step_results):
                    error_msg = f"Dependencies not met for step: {step.name}"
                    self.logger.error(error_msg)
                    result.errors.append(error_msg)
                    if step.required:
                        return result
                    continue

                # Execute step
                step_result = await self._execute_step(step)
                result.step_results.append(step_result)

                # Handle step failure
                if not step_result.get("success", False):
                    error_msg = f"Step failed: {step.name} - {step_result.get('error', 'Unknown error')}"
                    self.logger.error(error_msg)
                    result.errors.append(error_msg)

                    if step.required:
                        self.logger.error("Required step failed, aborting deployment")
                        await self._handle_deployment_failure(result)
                        return result
                    else:
                        self.logger.warning(
                            f"Optional step failed, continuing: {step.name}"
                        )
                        result.warnings.append(f"Optional step failed: {step.name}")

            # Calculate deployment time
            result.deployment_time_seconds = time.time() - self.start_time
            result.services_deployed = self.deployed_services
            result.success = True

            self.logger.info(
                f"Deployment completed successfully in {result.deployment_time_seconds:.2f} seconds"
            )

            return result

        except Exception as e:
            self.logger.error(f"Deployment failed with exception: {str(e)}")
            result.errors.append(f"Deployment exception: {str(e)}")
            result.deployment_time_seconds = time.time() - self.start_time
            await self._handle_deployment_failure(result)
            return result

    def _check_dependencies(
        self, step: DeploymentStep, completed_steps: list[dict[str, Any]]
    ) -> bool:
        """Check if step dependencies are satisfied."""
        if not step.depends_on:
            return True

        completed_step_names = [
            s["step_name"] for s in completed_steps if s.get("success", False)
        ]
        return all(dep in completed_step_names for dep in step.depends_on)

    async def _execute_step(self, step: DeploymentStep) -> dict[str, Any]:
        """Execute a single deployment step."""
        step_start_time = time.time()

        try:
            if step.function:
                # Execute Python function
                function = getattr(self, step.function)
                result = await function()
            elif step.command:
                # Execute shell command
                result = await self._execute_command(step.command, step.timeout_seconds)
            else:
                result = {"success": False, "error": "No function or command specified"}

            execution_time = time.time() - step_start_time

            return {
                "step_name": step.name,
                "description": step.description,
                "success": result.get("success", False),
                "execution_time_seconds": execution_time,
                "result": result,
            }

        except Exception as e:
            execution_time = time.time() - step_start_time
            return {
                "step_name": step.name,
                "description": step.description,
                "success": False,
                "execution_time_seconds": execution_time,
                "error": str(e),
            }

    async def _execute_command(
        self, command: str, timeout_seconds: int
    ) -> dict[str, Any]:
        """Execute a shell command with timeout."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.config.project_root,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout_seconds
            )

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "command": command,
            }

        except TimeoutError:
            return {
                "success": False,
                "error": f"Command timed out after {timeout_seconds} seconds",
                "command": command,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    async def validate_environment(self) -> dict[str, Any]:
        """Validate deployment environment."""
        self.logger.info("Validating deployment environment")

        checks = []

        # Check if project root exists
        if not self.config.project_root.exists():
            checks.append(
                {
                    "check": "project_root",
                    "success": False,
                    "error": "Project root does not exist",
                }
            )
        else:
            checks.append({"check": "project_root", "success": True})

        # Check if Docker is available
        try:
            result = await self._execute_command("docker --version", 30)
            checks.append(
                {"check": "docker", "success": result["success"], "details": result}
            )
        except Exception as e:
            checks.append({"check": "docker", "success": False, "error": str(e)})

        # Check if Docker Compose is available
        try:
            result = await self._execute_command("docker-compose --version", 30)
            checks.append(
                {
                    "check": "docker_compose",
                    "success": result["success"],
                    "details": result,
                }
            )
        except Exception as e:
            checks.append(
                {"check": "docker_compose", "success": False, "error": str(e)}
            )

        # Check if required files exist
        required_files = [
            "docker-compose.yml",
            "data_stack/meltano/meltano.yml",
            "data_stack/dbt/dbt_project.yml",
            "transactions.csv",
        ]

        for file_path in required_files:
            full_path = self.config.project_root / file_path
            if full_path.exists():
                checks.append({"check": f"file_{file_path}", "success": True})
            else:
                checks.append(
                    {
                        "check": f"file_{file_path}",
                        "success": False,
                        "error": f"Missing required file: {file_path}",
                    }
                )

        # Check Python environment
        try:
            result = await self._execute_command("python --version", 30)
            checks.append(
                {"check": "python", "success": result["success"], "details": result}
            )
        except Exception as e:
            checks.append({"check": "python", "success": False, "error": str(e)})

        all_checks_passed = all(check["success"] for check in checks)

        return {
            "success": all_checks_passed,
            "checks": checks,
            "message": (
                "Environment validation completed"
                if all_checks_passed
                else "Environment validation failed"
            ),
        }

    async def prepare_directories(self) -> dict[str, Any]:
        """Prepare required directories."""
        self.logger.info("Preparing directories")

        directories = [
            "volumes/duckdb",
            "volumes/meltano",
            "volumes/airflow/logs",
            "volumes/airflow/dags",
            "volumes/grafana",
            "volumes/prometheus",
        ]

        created_dirs = []
        errors = []

        for dir_path in directories:
            try:
                os.makedirs(dir_path, exist_ok=True)
                # Set permissions
                os.chmod(dir_path, 0o755)
                created_dirs.append(dir_path)
            except Exception as e:
                errors.append(f"Failed to create {dir_path}: {str(e)}")

        return {
            "success": len(errors) == 0,
            "created_directories": created_dirs,
            "errors": errors,
        }

    async def start_docker_services(self) -> dict[str, Any]:
        """Start Docker Compose services."""
        self.logger.info("Starting Docker services")

        # Build and start services
        if self.config.force_rebuild:
            command = "docker-compose down && docker-compose build --no-cache && docker-compose up -d"
        else:
            command = "docker-compose up -d"

        result = await self._execute_command(command, 600)

        if result["success"]:
            self.deployed_services.extend(
                ["postgres", "redis", "duckdb-http", "meltano", "airflow", "grafana"]
            )

        return result

    async def wait_for_services(self) -> dict[str, Any]:
        """Wait for all services to be healthy."""
        self.logger.info("Waiting for services to be healthy")

        services_to_check = ["postgres", "redis", "airflow-webserver"]
        healthy_services = []

        for attempt in range(self.config.health_check_retries):
            self.logger.info(
                f"Health check attempt {attempt + 1}/{self.config.health_check_retries}"
            )

            for service in services_to_check:
                if service not in healthy_services:
                    health_result = await self._check_service_health(service)
                    if health_result["healthy"]:
                        healthy_services.append(service)
                        self.logger.info(f"Service {service} is healthy")

            if len(healthy_services) == len(services_to_check):
                return {
                    "success": True,
                    "healthy_services": healthy_services,
                    "attempts": attempt + 1,
                }

            if attempt < self.config.health_check_retries - 1:
                await asyncio.sleep(self.config.health_check_interval)

        return {
            "success": False,
            "healthy_services": healthy_services,
            "failed_services": [
                s for s in services_to_check if s not in healthy_services
            ],
            "attempts": self.config.health_check_retries,
        }

    async def _check_service_health(self, service: str) -> dict[str, Any]:
        """Check health of a specific service."""
        try:
            if service == "postgres":
                result = await self._execute_command(
                    "docker-compose exec -T postgres pg_isready -U postgres", 10
                )
                return {"healthy": result["success"], "details": result}
            elif service == "redis":
                result = await self._execute_command(
                    "docker-compose exec -T redis redis-cli ping", 10
                )
                return {
                    "healthy": result["success"] and "PONG" in result.get("stdout", ""),
                    "details": result,
                }
            elif service == "airflow-webserver":
                # Check if Airflow webserver is responding
                result = await self._execute_command(
                    "curl -f http://localhost:8080/health || echo 'FAILED'", 10
                )
                return {
                    "healthy": result["success"]
                    and "FAILED" not in result.get("stdout", ""),
                    "details": result,
                }
            else:
                return {"healthy": False, "error": f"Unknown service: {service}"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def initialize_duckdb(self) -> dict[str, Any]:
        """Initialize DuckDB database."""
        self.logger.info("Initializing DuckDB database")

        try:
            # Add tools to path for imports
            sys.path.append(str(self.config.project_root))

            from tools.duckdb_tools import DuckDBTools

            duckdb_tools = DuckDBTools()

            # Create basic schema
            init_queries = [
                "CREATE SCHEMA IF NOT EXISTS raw_data",
                "CREATE SCHEMA IF NOT EXISTS staging",
                "CREATE SCHEMA IF NOT EXISTS analytics",
                "CREATE SCHEMA IF NOT EXISTS monitoring",
            ]

            results = []
            for query in init_queries:
                result = await duckdb_tools.execute_query(
                    query, self.config.duckdb_path
                )
                results.append(result)

            all_success = all(r["success"] for r in results)

            return {
                "success": all_success,
                "initialization_results": results,
                "database_path": self.config.duckdb_path,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"DuckDB initialization failed: {str(e)}",
            }

    async def setup_meltano(self) -> dict[str, Any]:
        """Setup Meltano project."""
        self.logger.info("Setting up Meltano project")

        meltano_dir = self.config.project_root / self.config.meltano_project_path

        commands = [
            f"cd {meltano_dir} && meltano install",
            f"cd {meltano_dir} && meltano invoke tap-csv --about",
            f"cd {meltano_dir} && meltano invoke target-duckdb --about",
        ]

        results = []
        for command in commands:
            result = await self._execute_command(command, 300)
            results.append(result)

        all_success = all(r["success"] for r in results)

        return {
            "success": all_success,
            "setup_results": results,
            "meltano_project_path": str(meltano_dir),
        }

    async def setup_dbt(self) -> dict[str, Any]:
        """Setup dbt project."""
        self.logger.info("Setting up dbt project")

        dbt_dir = self.config.project_root / self.config.dbt_project_path

        commands = [
            f"cd {dbt_dir} && dbt deps --profiles-dir .",
            f"cd {dbt_dir} && dbt compile --profiles-dir .",
            f"cd {dbt_dir} && dbt parse --profiles-dir .",
        ]

        results = []
        for command in commands:
            result = await self._execute_command(command, 300)
            results.append(result)

        all_success = all(r["success"] for r in results)

        return {
            "success": all_success,
            "setup_results": results,
            "dbt_project_path": str(dbt_dir),
        }

    async def setup_airflow(self) -> dict[str, Any]:
        """Setup Airflow DAGs."""
        self.logger.info("Setting up Airflow")

        # Copy DAGs to Airflow directory
        airflow_dags_dir = Path("/data/airflow/dags")
        local_dags_dir = self.config.project_root / self.config.airflow_dags_path

        try:
            if local_dags_dir.exists():
                result = await self._execute_command(
                    f"cp -r {local_dags_dir}/* {airflow_dags_dir}/", 60
                )

                # Trigger DAG refresh
                refresh_result = await self._execute_command(
                    "docker-compose exec -T airflow-webserver airflow dags list", 60
                )

                return {
                    "success": result["success"] and refresh_result["success"],
                    "copy_result": result,
                    "refresh_result": refresh_result,
                }
            else:
                return {
                    "success": False,
                    "error": f"DAGs directory not found: {local_dags_dir}",
                }

        except Exception as e:
            return {"success": False, "error": f"Airflow setup failed: {str(e)}"}

    async def run_initial_pipeline(self) -> dict[str, Any]:
        """Run initial data pipeline."""
        self.logger.info("Running initial data pipeline")

        try:
            # Check if transactions.csv exists
            transactions_file = self.config.project_root / "transactions.csv"
            if not transactions_file.exists():
                return {"success": False, "error": "transactions.csv not found"}

            # Run Meltano ELT
            meltano_dir = self.config.project_root / self.config.meltano_project_path
            elt_result = await self._execute_command(
                f"cd {meltano_dir} && meltano --environment=dev elt tap-csv target-duckdb",
                600,
            )

            if not elt_result["success"]:
                return {
                    "success": False,
                    "error": "Meltano ELT failed",
                    "details": elt_result,
                }

            # Run dbt transformations
            dbt_dir = self.config.project_root / self.config.dbt_project_path
            dbt_result = await self._execute_command(
                f"cd {dbt_dir} && dbt run --profiles-dir .", 600
            )

            return {
                "success": dbt_result["success"],
                "elt_result": elt_result,
                "dbt_result": dbt_result,
            }

        except Exception as e:
            return {"success": False, "error": f"Initial pipeline failed: {str(e)}"}

    async def validate_deployment(self) -> dict[str, Any]:
        """Validate the deployment."""
        self.logger.info("Validating deployment")

        validation_results = {}

        # Check if DuckDB has data
        try:
            sys.path.append(str(self.config.project_root))
            from tools.duckdb_tools import DuckDBTools

            duckdb_tools = DuckDBTools()

            # Check if staging table exists and has data
            result = await duckdb_tools.execute_query(
                "SELECT COUNT(*) FROM main.stg_transactions", self.config.duckdb_path
            )

            if result["success"] and result["rows"]:
                row_count = result["rows"][0][0]
                validation_results["data_validation"] = {
                    "success": row_count > 0,
                    "row_count": row_count,
                }
            else:
                validation_results["data_validation"] = {
                    "success": False,
                    "error": "Could not query staging table",
                }
        except Exception as e:
            validation_results["data_validation"] = {"success": False, "error": str(e)}

        # Check Docker services
        docker_result = await self._execute_command("docker-compose ps", 30)
        validation_results["docker_services"] = docker_result

        # Check if Airflow DAGs are loaded
        airflow_result = await self._execute_command(
            "docker-compose exec -T airflow-webserver airflow dags list", 60
        )
        validation_results["airflow_dags"] = airflow_result

        all_validations_passed = all(
            v.get("success", False) for v in validation_results.values()
        )

        return {
            "success": all_validations_passed,
            "validation_results": validation_results,
        }

    async def setup_monitoring(self) -> dict[str, Any]:
        """Setup monitoring and alerting."""
        self.logger.info("Setting up monitoring")

        if not self.config.enable_monitoring:
            return {"success": True, "message": "Monitoring disabled"}

        # Basic monitoring setup - would be expanded in production
        return {
            "success": True,
            "message": "Monitoring setup completed (basic configuration)",
        }

    async def generate_deployment_report(self) -> dict[str, Any]:
        """Generate deployment summary report."""
        self.logger.info("Generating deployment report")

        report = {
            "deployment_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "deployment_duration_seconds": time.time() - self.start_time,
            "environment": self.config.environment,
            "project_root": str(self.config.project_root),
            "services_deployed": self.deployed_services,
            "configuration": self.config.dict(),
        }

        # Save report to file
        report_path = (
            self.config.project_root / f"deployment_report_{int(time.time())}.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return {"success": True, "report_path": str(report_path), "report": report}

    async def _handle_deployment_failure(self, result: DeploymentResult) -> None:
        """Handle deployment failure and cleanup."""
        self.logger.error("Handling deployment failure")

        # Add cleanup and rollback logic here
        result.next_actions = [
            "Check deployment logs for detailed error information",
            "Verify Docker services are running",
            "Check file permissions and disk space",
            "Retry deployment with --force-rebuild flag",
            "Contact support if issues persist",
        ]


@click.command()
@click.option("--environment", default="dev", help="Deployment environment")
@click.option("--project-root", default=".", help="Project root directory")
@click.option("--force-rebuild", is_flag=True, help="Force rebuild of Docker images")
@click.option("--timeout", default=30, help="Timeout in minutes")
@click.option("--config-file", help="Path to deployment configuration file")
@click.option("--dry-run", is_flag=True, help="Perform dry run without making changes")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(
    environment: str,
    project_root: str,
    force_rebuild: bool,
    timeout: int,
    config_file: str | None,
    dry_run: bool,
    verbose: bool,
):
    """Deploy the AI Agent Data Stack."""

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = DeploymentConfig(
        project_root=Path(project_root),
        environment=environment,
        force_rebuild=force_rebuild,
        timeout_minutes=timeout,
    )

    if config_file:
        # Load configuration from file
        try:
            with open(config_file) as f:
                config_data = yaml.safe_load(f)
                config = DeploymentConfig(**config_data)
        except Exception as e:
            click.echo(f"Error loading configuration file: {e}", err=True)
            sys.exit(1)

    if dry_run:
        click.echo("Dry run mode - no changes will be made")
        click.echo(f"Configuration: {config.dict()}")
        return

    # Create deployer and run deployment
    deployer = DataStackDeployer(config)

    try:
        result = asyncio.run(deployer.deploy())

        if result.success:
            click.echo("✅ Deployment completed successfully!")
            click.echo(f"Deployment time: {result.deployment_time_seconds:.2f} seconds")
            click.echo(f"Services deployed: {', '.join(result.services_deployed)}")

            if result.warnings:
                click.echo("⚠️  Warnings:")
                for warning in result.warnings:
                    click.echo(f"  - {warning}")
        else:
            click.echo("❌ Deployment failed!")
            click.echo("Errors:")
            for error in result.errors:
                click.echo(f"  - {error}")

            click.echo("Next actions:")
            for action in result.next_actions:
                click.echo(f"  - {action}")

            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Deployment failed with unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
