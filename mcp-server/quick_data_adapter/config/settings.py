"""Server configuration settings."""

import os


class Settings:
    """Application settings."""

    def __init__(self):
        self.server_name = "Modular MCP Server"
        self.version = "0.1.0"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.api_key: str | None = os.getenv("API_KEY")
        self.database_url: str | None = os.getenv("DATABASE_URL")

    @property
    def server_info(self) -> dict:
        """Get server information."""
        return {
            "name": self.server_name,
            "version": self.version,
            "log_level": self.log_level,
        }


settings = Settings()
