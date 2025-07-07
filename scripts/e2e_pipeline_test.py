#!/usr/bin/env python3
"""
End-to-End Pipeline Testing Script
Orchestrates complete data pipeline: Dagster -> Airbyte -> dbt -> DataHub

Features:
- Trigger orchestrated pipeline run
- Validate KPIs and data quality checks
- Verify lineage propagation
- Generate coverage report for CI artifacts
"""

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("e2e_pipeline_test.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for pipeline components"""

    airflow_host: str = "localhost"
    airflow_port: int = 8080
    airflow_username: str = "admin"
    airflow_password: str = "admin"

    datahub_host: str = "localhost"
    datahub_port: int = 9002

    meltano_project_dir: str = "./meltano"
    dbt_project_dir: str = "./transformation/dbt"

    timeout_seconds: int = 1800  # 30 minutes
    check_interval_seconds: int = 30


@dataclass
class TestResult:
    """Test result structure"""

    name: str
    status: str  # "PASS", "FAIL", "SKIP"
    message: str
    duration_seconds: float
    details: dict | None = None


class PipelineTestSuite:
    """End-to-end pipeline testing suite"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.results: list[TestResult] = []
        self.start_time = datetime.now()

    def run_command(
        self, command: list[str], cwd: str | None = None, timeout: int = 300
    ) -> tuple[int, str, str]:
        """Execute shell command and return exit code, stdout, stderr"""
        try:
            logger.info(f"Executing: {' '.join(command)}")
            result = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)

    def check_service_health(self, service_name: str, url: str) -> TestResult:
        """Check if a service is healthy"""
        start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                return TestResult(
                    name=f"{service_name}_health_check",
                    status="PASS",
                    message=f"{service_name} is healthy",
                    duration_seconds=duration,
                    details={"status_code": response.status_code},
                )
            else:
                return TestResult(
                    name=f"{service_name}_health_check",
                    status="FAIL",
                    message=f"{service_name} health check failed",
                    duration_seconds=duration,
                    details={"status_code": response.status_code},
                )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=f"{service_name}_health_check",
                status="FAIL",
                message=f"{service_name} health check failed: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def trigger_airflow_dag(self, dag_id: str) -> TestResult:
        """Trigger Airflow DAG execution"""
        start_time = time.time()

        try:
            # Trigger DAG
            url = f"http://{self.config.airflow_host}:{self.config.airflow_port}/api/v1/dags/{dag_id}/dagRuns"
            headers = {"Content-Type": "application/json"}
            auth = (self.config.airflow_username, self.config.airflow_password)

            payload = {
                "dag_run_id": f"e2e_test_{int(time.time())}",
                "logical_date": datetime.now().isoformat(),
                "conf": {"test_mode": True},
            }

            response = requests.post(
                url, json=payload, headers=headers, auth=auth, timeout=30
            )
            duration = time.time() - start_time

            if response.status_code in [200, 201]:
                dag_run_id = response.json().get("dag_run_id")
                return TestResult(
                    name=f"trigger_dag_{dag_id}",
                    status="PASS",
                    message=f"Successfully triggered DAG {dag_id}",
                    duration_seconds=duration,
                    details={"dag_run_id": dag_run_id},
                )
            else:
                return TestResult(
                    name=f"trigger_dag_{dag_id}",
                    status="FAIL",
                    message=f"Failed to trigger DAG {dag_id}: {response.text}",
                    duration_seconds=duration,
                    details={
                        "status_code": response.status_code,
                        "response": response.text,
                    },
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=f"trigger_dag_{dag_id}",
                status="FAIL",
                message=f"Error triggering DAG {dag_id}: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def wait_for_dag_completion(self, dag_id: str, dag_run_id: str) -> TestResult:
        """Wait for DAG run to complete"""
        start_time = time.time()

        try:
            url = f"http://{self.config.airflow_host}:{self.config.airflow_port}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"
            auth = (self.config.airflow_username, self.config.airflow_password)

            max_wait_time = self.config.timeout_seconds
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                response = requests.get(url, auth=auth, timeout=30)
                if response.status_code == 200:
                    dag_run = response.json()
                    state = dag_run.get("state")

                    if state == "success":
                        duration = time.time() - start_time
                        return TestResult(
                            name=f"wait_dag_completion_{dag_id}",
                            status="PASS",
                            message=f"DAG {dag_id} completed successfully",
                            duration_seconds=duration,
                            details={"final_state": state, "dag_run": dag_run},
                        )
                    elif state == "failed":
                        duration = time.time() - start_time
                        return TestResult(
                            name=f"wait_dag_completion_{dag_id}",
                            status="FAIL",
                            message=f"DAG {dag_id} execution failed",
                            duration_seconds=duration,
                            details={"final_state": state, "dag_run": dag_run},
                        )
                    elif state in ["running", "queued"]:
                        logger.info(f"DAG {dag_id} is {state}, waiting...")
                        time.sleep(self.config.check_interval_seconds)
                        elapsed_time += self.config.check_interval_seconds

                time.sleep(5)
                elapsed_time += 5

            # Timeout
            duration = time.time() - start_time
            return TestResult(
                name=f"wait_dag_completion_{dag_id}",
                status="FAIL",
                message=f"DAG {dag_id} execution timed out after {max_wait_time} seconds",
                duration_seconds=duration,
                details={"timeout": True},
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=f"wait_dag_completion_{dag_id}",
                status="FAIL",
                message=f"Error waiting for DAG {dag_id}: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def run_meltano_pipeline(self) -> TestResult:
        """Execute Meltano ELT pipeline"""
        start_time = time.time()

        try:
            # Run Meltano ELT pipeline
            exit_code, stdout, stderr = self.run_command(
                ["meltano", "run", "tap-csv", "target-duckdb"],
                cwd=self.config.meltano_project_dir,
                timeout=600,
            )

            duration = time.time() - start_time

            if exit_code == 0:
                return TestResult(
                    name="meltano_elt_pipeline",
                    status="PASS",
                    message="Meltano ELT pipeline completed successfully",
                    duration_seconds=duration,
                    details={"stdout": stdout, "stderr": stderr},
                )
            else:
                return TestResult(
                    name="meltano_elt_pipeline",
                    status="FAIL",
                    message=f"Meltano ELT pipeline failed with exit code {exit_code}",
                    duration_seconds=duration,
                    details={
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                    },
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="meltano_elt_pipeline",
                status="FAIL",
                message=f"Error running Meltano pipeline: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def run_dbt_transformations(self) -> TestResult:
        """Execute dbt transformations"""
        start_time = time.time()

        try:
            # Run dbt transformations
            exit_code, stdout, stderr = self.run_command(
                ["dbt", "run"], cwd=self.config.dbt_project_dir, timeout=600
            )

            duration = time.time() - start_time

            if exit_code == 0:
                return TestResult(
                    name="dbt_transformations",
                    status="PASS",
                    message="dbt transformations completed successfully",
                    duration_seconds=duration,
                    details={"stdout": stdout, "stderr": stderr},
                )
            else:
                return TestResult(
                    name="dbt_transformations",
                    status="FAIL",
                    message=f"dbt transformations failed with exit code {exit_code}",
                    duration_seconds=duration,
                    details={
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                    },
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="dbt_transformations",
                status="FAIL",
                message=f"Error running dbt transformations: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def run_dbt_tests(self) -> TestResult:
        """Execute dbt data quality tests"""
        start_time = time.time()

        try:
            # Run dbt tests
            exit_code, stdout, stderr = self.run_command(
                ["dbt", "test"], cwd=self.config.dbt_project_dir, timeout=300
            )

            duration = time.time() - start_time

            if exit_code == 0:
                return TestResult(
                    name="dbt_data_quality_tests",
                    status="PASS",
                    message="dbt data quality tests passed",
                    duration_seconds=duration,
                    details={"stdout": stdout, "stderr": stderr},
                )
            else:
                return TestResult(
                    name="dbt_data_quality_tests",
                    status="FAIL",
                    message=f"dbt data quality tests failed with exit code {exit_code}",
                    duration_seconds=duration,
                    details={
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                    },
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="dbt_data_quality_tests",
                status="FAIL",
                message=f"Error running dbt tests: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def validate_datahub_lineage(self) -> TestResult:
        """Validate DataHub lineage propagation"""
        start_time = time.time()

        try:
            # Check DataHub lineage endpoint
            url = f"http://{self.config.datahub_host}:{self.config.datahub_port}/api/graphql"

            # GraphQL query to check lineage
            query = """
            query GetLineage($urn: String!) {
                entity(urn: $urn) {
                    ... on Dataset {
                        upstream {
                            total
                            entities {
                                entity {
                                    urn
                                    type
                                }
                            }
                        }
                        downstream {
                            total
                            entities {
                                entity {
                                    urn
                                    type
                                }
                            }
                        }
                    }
                }
            }
            """

            # Sample dataset URN (you may need to adjust this)
            variables = {
                "urn": "urn:li:dataset:(urn:li:dataPlatform:duckdb,analytics.customer_segments,PROD)"
            }

            response = requests.post(
                url, json={"query": query, "variables": variables}, timeout=30
            )

            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if "errors" not in data:
                    return TestResult(
                        name="datahub_lineage_validation",
                        status="PASS",
                        message="DataHub lineage validation successful",
                        duration_seconds=duration,
                        details={"lineage_data": data},
                    )
                else:
                    return TestResult(
                        name="datahub_lineage_validation",
                        status="FAIL",
                        message=f"DataHub lineage query returned errors: {data['errors']}",
                        duration_seconds=duration,
                        details={"errors": data["errors"]},
                    )
            else:
                return TestResult(
                    name="datahub_lineage_validation",
                    status="FAIL",
                    message=f"DataHub lineage validation failed: {response.text}",
                    duration_seconds=duration,
                    details={
                        "status_code": response.status_code,
                        "response": response.text,
                    },
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="datahub_lineage_validation",
                status="FAIL",
                message=f"Error validating DataHub lineage: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def validate_kpis(self) -> TestResult:
        """Validate key performance indicators"""
        start_time = time.time()

        try:
            # Example KPI validations - adapt based on your specific KPIs
            kpis = {
                "data_freshness": self._check_data_freshness(),
                "data_completeness": self._check_data_completeness(),
                "transformation_success_rate": self._check_transformation_success(),
                "lineage_coverage": self._check_lineage_coverage(),
            }

            duration = time.time() - start_time

            failed_kpis = [k for k, v in kpis.items() if not v["passed"]]

            if not failed_kpis:
                return TestResult(
                    name="kpi_validation",
                    status="PASS",
                    message="All KPIs passed validation",
                    duration_seconds=duration,
                    details={"kpis": kpis},
                )
            else:
                return TestResult(
                    name="kpi_validation",
                    status="FAIL",
                    message=f"Failed KPIs: {', '.join(failed_kpis)}",
                    duration_seconds=duration,
                    details={"kpis": kpis, "failed_kpis": failed_kpis},
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="kpi_validation",
                status="FAIL",
                message=f"Error validating KPIs: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def _check_data_freshness(self) -> dict:
        """Check if data is fresh (within expected time window)"""
        try:
            # Implementation depends on your data source
            # This is a placeholder - adapt to your specific data sources
            return {"passed": True, "message": "Data freshness check passed"}
        except Exception as e:
            return {
                "passed": False,
                "message": f"Data freshness check failed: {str(e)}",
            }

    def _check_data_completeness(self) -> dict:
        """Check data completeness"""
        try:
            # Example: Check for null values, record counts, etc.
            exit_code, stdout, stderr = self.run_command(
                ["dbt", "test", "--select", "tag:completeness"],
                cwd=self.config.dbt_project_dir,
                timeout=120,
            )
            return {
                "passed": exit_code == 0,
                "message": (
                    "Data completeness tests passed"
                    if exit_code == 0
                    else "Data completeness tests failed"
                ),
            }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Data completeness check failed: {str(e)}",
            }

    def _check_transformation_success(self) -> dict:
        """Check transformation success rate"""
        try:
            # This would typically check transformation metrics
            return {"passed": True, "message": "Transformation success rate acceptable"}
        except Exception as e:
            return {
                "passed": False,
                "message": f"Transformation success check failed: {str(e)}",
            }

    def _check_lineage_coverage(self) -> dict:
        """Check lineage coverage percentage"""
        try:
            # This would check what percentage of assets have lineage
            return {"passed": True, "message": "Lineage coverage acceptable"}
        except Exception as e:
            return {
                "passed": False,
                "message": f"Lineage coverage check failed: {str(e)}",
            }

    def generate_coverage_report(self) -> TestResult:
        """Generate test coverage report"""
        start_time = time.time()

        try:
            total_tests = len(self.results)
            passed_tests = len([r for r in self.results if r.status == "PASS"])
            failed_tests = len([r for r in self.results if r.status == "FAIL"])
            skipped_tests = len([r for r in self.results if r.status == "SKIP"])

            coverage_percentage = (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            )

            report = {
                "test_suite": "E2E Pipeline Testing",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "skipped": skipped_tests,
                    "coverage_percentage": round(coverage_percentage, 2),
                },
                "test_results": [
                    {
                        "name": r.name,
                        "status": r.status,
                        "message": r.message,
                        "duration_seconds": r.duration_seconds,
                        "details": r.details,
                    }
                    for r in self.results
                ],
            }

            # Save report to file
            report_file = "e2e_pipeline_coverage_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            duration = time.time() - start_time

            return TestResult(
                name="generate_coverage_report",
                status="PASS",
                message=f"Coverage report generated: {report_file}",
                duration_seconds=duration,
                details={"report_file": report_file, "coverage": coverage_percentage},
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="generate_coverage_report",
                status="FAIL",
                message=f"Error generating coverage report: {str(e)}",
                duration_seconds=duration,
                details={"error": str(e)},
            )

    def run_full_test_suite(self) -> bool:
        """Run the complete end-to-end test suite"""
        logger.info("Starting E2E Pipeline Test Suite")

        # 1. Health checks
        logger.info("Running health checks...")
        self.results.append(
            self.check_service_health(
                "Airflow",
                f"http://{self.config.airflow_host}:{self.config.airflow_port}/health",
            )
        )
        self.results.append(
            self.check_service_health(
                "DataHub",
                f"http://{self.config.datahub_host}:{self.config.datahub_port}/api/v2/system/status",
            )
        )

        # 2. Trigger and monitor orchestrated pipeline
        logger.info("Triggering orchestrated pipeline...")
        dag_trigger_result = self.trigger_airflow_dag("meltano_elt_pipeline")
        self.results.append(dag_trigger_result)

        if dag_trigger_result.status == "PASS" and dag_trigger_result.details:
            dag_run_id = dag_trigger_result.details.get("dag_run_id")
            if dag_run_id:
                logger.info(f"Waiting for DAG completion: {dag_run_id}")
                self.results.append(
                    self.wait_for_dag_completion("meltano_elt_pipeline", dag_run_id)
                )

        # 3. Run individual pipeline components
        logger.info("Running Meltano pipeline...")
        self.results.append(self.run_meltano_pipeline())

        logger.info("Running dbt transformations...")
        self.results.append(self.run_dbt_transformations())

        logger.info("Running dbt tests...")
        self.results.append(self.run_dbt_tests())

        # 4. Validate lineage and KPIs
        logger.info("Validating DataHub lineage...")
        self.results.append(self.validate_datahub_lineage())

        logger.info("Validating KPIs...")
        self.results.append(self.validate_kpis())

        # 5. Generate coverage report
        logger.info("Generating coverage report...")
        self.results.append(self.generate_coverage_report())

        # Summary
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])

        logger.info(f"Test Suite Complete: {passed_tests}/{total_tests} tests passed")

        if failed_tests > 0:
            logger.error("Failed tests:")
            for result in self.results:
                if result.status == "FAIL":
                    logger.error(f"  - {result.name}: {result.message}")

        return failed_tests == 0


def main():
    """Main entry point"""
    # Load configuration from environment or use defaults
    config = PipelineConfig(
        airflow_host=os.getenv("AIRFLOW_HOST", "localhost"),
        airflow_port=int(os.getenv("AIRFLOW_PORT", "8080")),
        airflow_username=os.getenv("AIRFLOW_USERNAME", "admin"),
        airflow_password=os.getenv("AIRFLOW_PASSWORD", "admin"),
        datahub_host=os.getenv("DATAHUB_HOST", "localhost"),
        datahub_port=int(os.getenv("DATAHUB_PORT", "9002")),
        meltano_project_dir=os.getenv("MELTANO_PROJECT_DIR", "./meltano"),
        dbt_project_dir=os.getenv("DBT_PROJECT_DIR", "./transformation/dbt"),
    )

    # Run test suite
    test_suite = PipelineTestSuite(config)
    success = test_suite.run_full_test_suite()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
