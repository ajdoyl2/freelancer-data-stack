#!/usr/bin/env python3
"""
Environment Variable Password Generation Script

Generates secure passwords for all services in the data stack and creates
.env files with proper credential management following security best practices.
"""

import secrets
import string
import sys
from pathlib import Path

import click
from pydantic import BaseModel, Field


class PasswordConfig(BaseModel):
    """Password generation configuration."""

    length: int = Field(default=32, description="Password length")
    use_special_chars: bool = Field(
        default=False, description="Include special characters"
    )
    use_url_safe: bool = Field(default=True, description="Use URL-safe encoding")
    min_uppercase: int = Field(default=2, description="Minimum uppercase letters")
    min_lowercase: int = Field(default=2, description="Minimum lowercase letters")
    min_digits: int = Field(default=2, description="Minimum digits")


class CredentialConfig(BaseModel):
    """Standard credential configuration structure."""

    username: str = Field(default="ajdoyle", description="Default username")
    password: str = Field(description="Generated secure password")
    database: str | None = Field(default=None, description="Optional database name")
    host: str = Field(default="localhost", description="Default host")
    port: int | None = Field(default=None, description="Service-specific port")


class EnvironmentGenerator:
    """Environment variable generator with secure password generation."""

    def __init__(self, config: PasswordConfig):
        self.config = config
        self.generated_passwords: dict[str, str] = {}

    def generate_secure_password(
        self, length: int | None = None, use_special: bool | None = None
    ) -> str:
        """
        Generate cryptographically secure password.

        Args:
            length: Password length (uses config default if None)
            use_special: Include special characters (uses config default if None)

        Returns:
            str: Cryptographically secure password
        """
        length = length or self.config.length
        use_special = (
            use_special if use_special is not None else self.config.use_special_chars
        )

        # PATTERN: Use secrets module for cryptographic security
        if use_special:
            # GOTCHA: Some services don't handle special chars well
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
        else:
            # SAFE: Alphanumeric only for database compatibility
            chars = string.ascii_letters + string.digits

        # CRITICAL: Use secrets.choice for cryptographic randomness
        password = "".join(secrets.choice(chars) for _ in range(length))

        # VALIDATION: Ensure password meets complexity requirements
        if not self.validate_password_strength(password):
            # Recursive retry if validation fails
            return self.generate_secure_password(length, use_special)

        return password

    def validate_password_strength(self, password: str) -> bool:
        """
        Validate password meets complexity requirements.

        Args:
            password: Password to validate

        Returns:
            bool: True if password meets requirements
        """
        # Check length
        if len(password) < self.config.length:
            return False

        # Count character types
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())

        # Validate minimum requirements
        return (
            uppercase_count >= self.config.min_uppercase
            and lowercase_count >= self.config.min_lowercase
            and digit_count >= self.config.min_digits
        )

    def generate_fernet_key(self) -> str:
        """
        Generate Fernet key for Airflow encryption.

        Returns:
            str: Base64-encoded Fernet key
        """
        # Fernet keys must be 32 URL-safe base64-encoded bytes
        key = secrets.token_urlsafe(32)
        return key

    def generate_secret_key(self) -> str:
        """
        Generate secret key for JWT and application secrets.

        Returns:
            str: URL-safe secret key
        """
        return secrets.token_urlsafe(64)

    def generate_all_credentials(self) -> dict[str, str]:
        """
        Generate all required credentials for the data stack.

        Returns:
            Dict[str, str]: Environment variables with generated credentials
        """
        credentials = {}

        # PostgreSQL credentials
        credentials["POSTGRES_USER"] = "ajdoyle"
        credentials["POSTGRES_PASSWORD"] = self.generate_secure_password(
            use_special=False
        )  # Database safe

        # Airflow credentials
        credentials["AIRFLOW_USERNAME"] = "ajdoyle"
        credentials["AIRFLOW_PASSWORD"] = self.generate_secure_password(
            use_special=False
        )
        credentials["AIRFLOW_FERNET_KEY"] = self.generate_fernet_key()

        # Grafana credentials
        credentials["GRAFANA_USERNAME"] = "ajdoyle"
        credentials["GRAFANA_PASSWORD"] = self.generate_secure_password()

        # Neo4j credentials
        credentials["NEO4J_USERNAME"] = "ajdoyle"
        credentials["NEO4J_PASSWORD"] = self.generate_secure_password(
            use_special=False
        )  # Database safe

        # DataHub credentials
        credentials["DATAHUB_SECRET"] = self.generate_secret_key()
        credentials["DATAHUB_TOKEN"] = self.generate_secret_key()

        # Metabase credentials
        credentials["METABASE_DB_USERNAME"] = "ajdoyle"
        credentials["METABASE_DB_PASSWORD"] = credentials[
            "POSTGRES_PASSWORD"
        ]  # Reuse PostgreSQL password
        credentials["METABASE_ADMIN_EMAIL"] = "ajdoyle@datastack.local"

        # MCP Server credentials
        credentials["SECRET_KEY"] = self.generate_secret_key()

        # Store for reference
        self.generated_passwords = credentials

        return credentials

    def create_env_file(self, env_file_path: str, credentials: dict[str, str]) -> None:
        """
        Create .env file with generated credentials.

        Args:
            env_file_path: Path to .env file
            credentials: Dictionary of environment variables
        """
        env_path = Path(env_file_path)

        # Ensure directory exists
        env_path.parent.mkdir(parents=True, exist_ok=True)

        # Create .env file content
        env_content = [
            "# AI Agent-Driven Data Stack Environment Variables",
            "# Generated on: " + str(Path(__file__).stat().st_mtime),
            "# SECURITY: Do not commit this file to version control",
            "",
            "# ============================================================================",
            "# DATABASE CREDENTIALS",
            "# ============================================================================",
            f"POSTGRES_USER={credentials['POSTGRES_USER']}",
            f"POSTGRES_PASSWORD={credentials['POSTGRES_PASSWORD']}",
            "",
            "# ============================================================================",
            "# AIRFLOW CREDENTIALS",
            "# ============================================================================",
            f"AIRFLOW_USERNAME={credentials['AIRFLOW_USERNAME']}",
            f"AIRFLOW_PASSWORD={credentials['AIRFLOW_PASSWORD']}",
            f"AIRFLOW_FERNET_KEY={credentials['AIRFLOW_FERNET_KEY']}",
            "",
            "# ============================================================================",
            "# GRAFANA CREDENTIALS",
            "# ============================================================================",
            f"GRAFANA_USERNAME={credentials['GRAFANA_USERNAME']}",
            f"GRAFANA_PASSWORD={credentials['GRAFANA_PASSWORD']}",
            "",
            "# ============================================================================",
            "# NEO4J CREDENTIALS",
            "# ============================================================================",
            f"NEO4J_USERNAME={credentials['NEO4J_USERNAME']}",
            f"NEO4J_PASSWORD={credentials['NEO4J_PASSWORD']}",
            "",
            "# ============================================================================",
            "# DATAHUB CREDENTIALS",
            "# ============================================================================",
            f"DATAHUB_SECRET={credentials['DATAHUB_SECRET']}",
            f"DATAHUB_TOKEN={credentials['DATAHUB_TOKEN']}",
            "",
            "# ============================================================================",
            "# METABASE CREDENTIALS",
            "# ============================================================================",
            f"METABASE_DB_USERNAME={credentials['METABASE_DB_USERNAME']}",
            f"METABASE_DB_PASSWORD={credentials['METABASE_DB_PASSWORD']}",
            f"METABASE_ADMIN_EMAIL={credentials['METABASE_ADMIN_EMAIL']}",
            "",
            "# ============================================================================",
            "# MCP SERVER CREDENTIALS",
            "# ============================================================================",
            f"SECRET_KEY={credentials['SECRET_KEY']}",
            "",
            "# ============================================================================",
            "# EXTERNAL SERVICE PLACEHOLDERS (Add your own values)",
            "# ============================================================================",
            "OPENAI_API_KEY=",
            "ANTHROPIC_API_KEY=",
            "GOOGLE_API_KEY=",
            "XAI_API_KEY=",
            "",
            "# Snowflake (if using)",
            "SNOWFLAKE_ACCOUNT=",
            "SNOWFLAKE_USERNAME=",
            "SNOWFLAKE_PASSWORD=",
            "SNOWFLAKE_ROLE=",
            "SNOWFLAKE_WAREHOUSE=",
            "SNOWFLAKE_DATABASE=",
            "SNOWFLAKE_SCHEMA=",
            "",
            "# Monitoring",
            "SLACK_API_URL=",
            "",
        ]

        # Write to file
        with open(env_path, "w") as f:
            f.write("\n".join(env_content))

        print(f"✅ Created .env file: {env_path}")

    def create_env_example_file(self, env_example_path: str) -> None:
        """
        Create .env.example file with placeholder values.

        Args:
            env_example_path: Path to .env.example file
        """
        example_path = Path(env_example_path)

        # Ensure directory exists
        example_path.parent.mkdir(parents=True, exist_ok=True)

        # Create .env.example content
        example_content = [
            "# AI Agent-Driven Data Stack Environment Variables - EXAMPLE",
            "# Copy this file to .env and update with actual values",
            "# SECURITY: This file can be committed to version control",
            "",
            "# ============================================================================",
            "# DATABASE CREDENTIALS",
            "# ============================================================================",
            "POSTGRES_USER=ajdoyle",
            "POSTGRES_PASSWORD=your_secure_postgres_password_here",
            "",
            "# ============================================================================",
            "# AIRFLOW CREDENTIALS",
            "# ============================================================================",
            "AIRFLOW_USERNAME=ajdoyle",
            "AIRFLOW_PASSWORD=your_secure_airflow_password_here",
            "AIRFLOW_FERNET_KEY=your_fernet_key_here",
            "",
            "# ============================================================================",
            "# GRAFANA CREDENTIALS",
            "# ============================================================================",
            "GRAFANA_USERNAME=ajdoyle",
            "GRAFANA_PASSWORD=your_secure_grafana_password_here",
            "",
            "# ============================================================================",
            "# NEO4J CREDENTIALS",
            "# ============================================================================",
            "NEO4J_USERNAME=ajdoyle",
            "NEO4J_PASSWORD=your_secure_neo4j_password_here",
            "",
            "# ============================================================================",
            "# DATAHUB CREDENTIALS",
            "# ============================================================================",
            "DATAHUB_SECRET=your_secure_datahub_secret_here",
            "DATAHUB_TOKEN=your_secure_datahub_token_here",
            "",
            "# ============================================================================",
            "# METABASE CREDENTIALS",
            "# ============================================================================",
            "METABASE_DB_USERNAME=ajdoyle",
            "METABASE_DB_PASSWORD=your_secure_postgres_password_here",
            "METABASE_ADMIN_EMAIL=ajdoyle@datastack.local",
            "",
            "# ============================================================================",
            "# MCP SERVER CREDENTIALS",
            "# ============================================================================",
            "SECRET_KEY=your_secure_secret_key_here",
            "",
            "# ============================================================================",
            "# EXTERNAL SERVICE CREDENTIALS (Add your own values)",
            "# ============================================================================",
            "OPENAI_API_KEY=sk-your_openai_api_key_here",
            "ANTHROPIC_API_KEY=your_anthropic_api_key_here",
            "GOOGLE_API_KEY=your_google_api_key_here",
            "XAI_API_KEY=your_xai_api_key_here",
            "",
            "# Snowflake (if using)",
            "SNOWFLAKE_ACCOUNT=your_account_here",
            "SNOWFLAKE_USERNAME=your_snowflake_username_here",
            "SNOWFLAKE_PASSWORD=your_snowflake_password_here",
            "SNOWFLAKE_ROLE=your_role_here",
            "SNOWFLAKE_WAREHOUSE=your_warehouse_here",
            "SNOWFLAKE_DATABASE=your_database_here",
            "SNOWFLAKE_SCHEMA=your_schema_here",
            "",
            "# Monitoring",
            "SLACK_API_URL=your_slack_webhook_url_here",
            "",
        ]

        # Write to file
        with open(example_path, "w") as f:
            f.write("\n".join(example_content))

        print(f"✅ Created .env.example file: {example_path}")


@click.command()
@click.option("--output-file", "-o", default=".env", help="Output .env file path")
@click.option(
    "--example-file", "-e", default=".env.example", help="Output .env.example file path"
)
@click.option("--password-length", "-l", default=32, help="Password length")
@click.option(
    "--use-special-chars",
    "-s",
    is_flag=True,
    default=False,
    help="Include special characters",
)
@click.option(
    "--force", "-f", is_flag=True, default=False, help="Overwrite existing files"
)
@click.option("--verbose", "-v", is_flag=True, default=False, help="Verbose output")
def generate_passwords(
    output_file: str,
    example_file: str,
    password_length: int,
    use_special_chars: bool,
    force: bool,
    verbose: bool,
):
    """Generate secure passwords for the AI agent-driven data stack."""

    if verbose:
        print("🔐 Generating secure passwords for data stack services...")

    # Check if files exist and force flag
    if Path(output_file).exists() and not force:
        print(f"❌ File {output_file} already exists. Use --force to overwrite.")
        sys.exit(1)

    # Create password configuration
    password_config = PasswordConfig(
        length=password_length, use_special_chars=use_special_chars
    )

    # Initialize generator
    generator = EnvironmentGenerator(password_config)

    try:
        # Generate all credentials
        credentials = generator.generate_all_credentials()

        if verbose:
            print(f"📊 Generated {len(credentials)} environment variables")
            print("🔒 All passwords use cryptographically secure generation")

        # Create .env file
        generator.create_env_file(output_file, credentials)

        # Create .env.example file
        generator.create_env_example_file(example_file)

        if verbose:
            print("\n✅ Password generation completed successfully!")
            print("\n🔐 Security recommendations:")
            print("   1. Add .env to your .gitignore file")
            print("   2. Set appropriate file permissions (chmod 600 .env)")
            print("   3. Rotate passwords regularly in production")
            print("   4. Use Docker secrets for production deployments")

        print("\n📝 Next steps:")
        print(f"   1. Review generated passwords in {output_file}")
        print("   2. Add external API keys as needed")
        print("   3. Run: docker-compose config --quiet")
        print("   4. Run: docker-compose up -d")

    except Exception as e:
        print(f"❌ Error generating passwords: {e}")
        sys.exit(1)


if __name__ == "__main__":
    generate_passwords()
