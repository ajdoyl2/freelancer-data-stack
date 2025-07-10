"""
Configuration settings for MCP Server
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Basic app settings
    app_name: str = "MCP Server"
    debug: bool = False

    # Database connections
    snowflake_account: str | None = None
    snowflake_user: str | None = None
    snowflake_password: str | None = None
    snowflake_warehouse: str | None = None
    snowflake_database: str | None = None
    snowflake_schema: str | None = None

    duckdb_path: str = "data/duckdb.db"

    # Dagster settings
    dagster_host: str = "localhost"
    dagster_port: int = 3000

    # dbt settings
    dbt_project_dir: str | None = None
    dbt_profiles_dir: str | None = None

    # DataHub settings
    datahub_server: str = "http://localhost:8080"
    datahub_token: str | None = None

    # LLM settings
    openai_api_key: str | None = None
    openai_model: str = "gpt-4"

    # Monitoring
    enable_monitoring: bool = True
    monitoring_interval: int = 30  # seconds

    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Quick Data MCP configuration
    quick_data_mcp_host: str = "quick-data-mcp"
    quick_data_mcp_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
