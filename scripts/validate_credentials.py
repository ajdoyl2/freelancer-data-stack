#!/usr/bin/env python3
"""
Credential Migration Validation Script

Validates that all credentials have been properly migrated to environment variables
and that the Docker Compose configuration is secure.
"""

import re
import sys
from pathlib import Path
from typing import Any

import click
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Result of a validation check."""

    check_name: str
    success: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class CredentialValidator:
    """Validates credential migration and security."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.results: list[ValidationResult] = []

    def validate_env_file_exists(self) -> ValidationResult:
        """Validate .env file exists and is readable."""
        env_file = self.project_root / ".env"

        if not env_file.exists():
            return ValidationResult(
                check_name="env_file_exists",
                success=False,
                message=".env file not found",
            )

        if not env_file.is_file():
            return ValidationResult(
                check_name="env_file_exists",
                success=False,
                message=".env exists but is not a file",
            )

        return ValidationResult(
            check_name="env_file_exists",
            success=True,
            message=".env file found and readable",
        )

    def validate_env_variables(self) -> ValidationResult:
        """Validate all required environment variables are set."""
        required_vars = [
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "AIRFLOW_USERNAME",
            "AIRFLOW_PASSWORD",
            "AIRFLOW_FERNET_KEY",
            "GRAFANA_USERNAME",
            "GRAFANA_PASSWORD",
            "NEO4J_USERNAME",
            "NEO4J_PASSWORD",
            "DATAHUB_SECRET",
            "DATAHUB_TOKEN",
            "METABASE_DB_USERNAME",
            "METABASE_DB_PASSWORD",
            "METABASE_ADMIN_EMAIL",
            "SECRET_KEY",
        ]

        # Load .env file
        env_file = self.project_root / ".env"
        if not env_file.exists():
            return ValidationResult(
                check_name="env_variables", success=False, message=".env file not found"
            )

        env_vars = {}
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

        missing_vars = []
        empty_vars = []

        for var in required_vars:
            if var not in env_vars:
                missing_vars.append(var)
            elif not env_vars[var] or env_vars[var].strip() == "":
                empty_vars.append(var)

        if missing_vars or empty_vars:
            return ValidationResult(
                check_name="env_variables",
                success=False,
                message=f"Missing: {missing_vars}, Empty: {empty_vars}",
                details={"missing": missing_vars, "empty": empty_vars},
            )

        return ValidationResult(
            check_name="env_variables",
            success=True,
            message=f"All {len(required_vars)} required environment variables are set",
            details={"variables_count": len(required_vars)},
        )

    def validate_password_strength(self) -> ValidationResult:
        """Validate password strength requirements."""
        env_file = self.project_root / ".env"
        if not env_file.exists():
            return ValidationResult(
                check_name="password_strength",
                success=False,
                message=".env file not found",
            )

        env_vars = {}
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

        password_vars = [
            "POSTGRES_PASSWORD",
            "AIRFLOW_PASSWORD",
            "GRAFANA_PASSWORD",
            "NEO4J_PASSWORD",
        ]

        weak_passwords = []

        for var in password_vars:
            if var in env_vars:
                password = env_vars[var]
                if len(password) < 16:
                    weak_passwords.append(f"{var}: too short ({len(password)} chars)")
                elif password.lower() in ["password", "admin", "postgres", "root"]:
                    weak_passwords.append(f"{var}: common weak password")

        if weak_passwords:
            return ValidationResult(
                check_name="password_strength",
                success=False,
                message="Weak passwords found",
                details={"weak_passwords": weak_passwords},
            )

        return ValidationResult(
            check_name="password_strength",
            success=True,
            message="All passwords meet strength requirements",
        )

    def validate_no_hardcoded_credentials(self) -> ValidationResult:
        """Validate no hardcoded credentials remain in docker-compose.yml."""
        compose_file = self.project_root / "docker-compose.yml"

        if not compose_file.exists():
            return ValidationResult(
                check_name="no_hardcoded_credentials",
                success=False,
                message="docker-compose.yml not found",
            )

        with open(compose_file) as f:
            content = f.read()

        # Patterns to check for hardcoded credentials (excluding legitimate config)
        hardcoded_patterns = [
            r"(USER|USERNAME|PASSWORD|AUTH):\s*postgres\s*$",
            r"(USER|USERNAME|PASSWORD|AUTH):\s*admin\s*$",
            r"(USER|USERNAME|PASSWORD|AUTH):\s*password\s*$",
            r"(USER|USERNAME|PASSWORD|AUTH):\s*root\s*$",
            r"(USER|USERNAME|PASSWORD|AUTH):\s*datahub\s*$",
            r"admin@datastack\.local",
            r"YouMustChangeThisSecretKey",
            r"your-secret-key-here",
        ]

        hardcoded_found = []

        for pattern in hardcoded_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                hardcoded_found.extend(matches)

        if hardcoded_found:
            return ValidationResult(
                check_name="no_hardcoded_credentials",
                success=False,
                message="Hardcoded credentials found",
                details={"hardcoded": hardcoded_found},
            )

        return ValidationResult(
            check_name="no_hardcoded_credentials",
            success=True,
            message="No hardcoded credentials found in docker-compose.yml",
        )

    def validate_gitignore_config(self) -> ValidationResult:
        """Validate .env is properly ignored by git."""
        gitignore_file = self.project_root / ".gitignore"

        if not gitignore_file.exists():
            return ValidationResult(
                check_name="gitignore_config",
                success=False,
                message=".gitignore file not found",
            )

        with open(gitignore_file) as f:
            gitignore_content = f.read()

        if ".env" not in gitignore_content:
            return ValidationResult(
                check_name="gitignore_config",
                success=False,
                message=".env not found in .gitignore",
            )

        return ValidationResult(
            check_name="gitignore_config",
            success=True,
            message=".env properly configured in .gitignore",
        )

    def validate_docker_compose_syntax(self) -> ValidationResult:
        """Validate Docker Compose configuration syntax."""
        try:
            import subprocess

            result = subprocess.run(
                ["docker", "compose", "config", "--quiet"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return ValidationResult(
                    check_name="docker_compose_syntax",
                    success=True,
                    message="Docker Compose configuration is valid",
                )
            else:
                return ValidationResult(
                    check_name="docker_compose_syntax",
                    success=False,
                    message=f"Docker Compose validation failed: {result.stderr}",
                )
        except Exception as e:
            return ValidationResult(
                check_name="docker_compose_syntax",
                success=False,
                message=f"Error running docker compose config: {str(e)}",
            )

    def run_all_validations(self) -> list[ValidationResult]:
        """Run all validation checks."""
        validations = [
            self.validate_env_file_exists,
            self.validate_env_variables,
            self.validate_password_strength,
            self.validate_no_hardcoded_credentials,
            self.validate_gitignore_config,
            self.validate_docker_compose_syntax,
        ]

        results = []
        for validation in validations:
            try:
                result = validation()
                results.append(result)
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_name=validation.__name__,
                        success=False,
                        message=f"Validation error: {str(e)}",
                    )
                )

        return results


@click.command()
@click.option("--check-strength", is_flag=True, help="Check password strength")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def validate_credentials(check_strength: bool, verbose: bool):
    """Validate credential migration and security."""

    validator = CredentialValidator()
    results = validator.run_all_validations()

    print("🔐 Credential Migration Validation Report")
    print("=" * 50)

    passed = 0
    failed = 0

    for result in results:
        status_icon = "✅" if result.success else "❌"
        print(f"{status_icon} {result.check_name}: {result.message}")

        if verbose and result.details:
            for key, value in result.details.items():
                print(f"   - {key}: {value}")

        if result.success:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 Summary: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All credential validation checks passed!")
        print("\n🔐 Security Status: SECURE ✅")
        print("\n📝 Next Steps:")
        print("   1. Review generated passwords in .env")
        print("   2. Add external API keys as needed")
        print("   3. Test service startup: docker compose up -d")
        sys.exit(0)
    else:
        print(f"⚠️  {failed} validation checks failed!")
        print("\n🔐 Security Status: NEEDS ATTENTION ❌")
        sys.exit(1)


if __name__ == "__main__":
    validate_credentials()
