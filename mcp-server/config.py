"""
Configuration settings for MCP Server
"""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    app_name: str = "MCP Server"
    debug: bool = False
    
    # Database connections
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
    
    duckdb_path: str = "data/duckdb.db"
    
    # Dagster settings
    dagster_host: str = "localhost"
    dagster_port: int = 3000
    
    # dbt settings
    dbt_project_dir: Optional[str] = None
    dbt_profiles_dir: Optional[str] = None
    
    # DataHub settings
    datahub_server: str = "http://localhost:8080"
    datahub_token: Optional[str] = None
    
    # LLM settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Monitoring
    enable_monitoring: bool = True
    monitoring_interval: int = 30  # seconds
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
