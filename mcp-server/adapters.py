"""
Plugin adapters for data tools integration
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import duckdb
import httpx
from dagster import DagsterInstance
from datahub.emitter.mcp_emitter import DatahubRestEmitter
from sqlalchemy import create_engine

from config import settings

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """Base adapter class"""

    @abstractmethod
    async def initialize(self):
        """Initialize the adapter"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup resources"""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check adapter health"""
        pass


class DagsterAdapter(BaseAdapter):
    """Dagster integration adapter"""

    def __init__(self):
        self.instance = None
        self.client = None

    async def initialize(self):
        """Initialize Dagster connection"""
        try:
            # Initialize Dagster instance
            self.instance = DagsterInstance.get()
            self.client = httpx.AsyncClient(
                base_url=f"http://{settings.dagster_host}:{settings.dagster_port}"
            )
            logger.info("Dagster adapter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Dagster adapter: {e}")
            raise

    async def cleanup(self):
        """Cleanup Dagster resources"""
        if self.client:
            await self.client.aclose()

    async def health_check(self) -> dict[str, Any]:
        """Check Dagster health"""
        try:
            if self.client:
                response = await self.client.get("/health")
                return {"status": "healthy", "response_code": response.status_code}
            return {"status": "not_initialized"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def get_jobs(self) -> list[dict[str, Any]]:
        """Get Dagster jobs"""
        try:
            # Mock implementation - replace with actual Dagster API calls
            return [
                {
                    "name": "daily_etl_job",
                    "status": "success",
                    "last_run": datetime.now(),
                    "description": "Daily ETL pipeline",
                },
                {
                    "name": "hourly_sync_job",
                    "status": "running",
                    "last_run": datetime.now(),
                    "description": "Hourly data sync",
                },
            ]
        except Exception as e:
            logger.error(f"Error getting Dagster jobs: {e}")
            return []


class DbtAdapter(BaseAdapter):
    """dbt integration adapter"""

    def __init__(self):
        self.project_dir = settings.dbt_project_dir
        self.profiles_dir = settings.dbt_profiles_dir

    async def initialize(self):
        """Initialize dbt connection"""
        logger.info("dbt adapter initialized")

    async def cleanup(self):
        """Cleanup dbt resources"""
        pass

    async def health_check(self) -> dict[str, Any]:
        """Check dbt health"""
        try:
            if self.project_dir:
                return {"status": "healthy", "project_dir": self.project_dir}
            return {"status": "not_configured"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def get_models(self) -> list[dict[str, Any]]:
        """Get dbt models"""
        try:
            # Mock implementation - replace with actual dbt manifest parsing
            return [
                {
                    "name": "dim_customers",
                    "path": "models/dimensions/dim_customers.sql",
                    "status": "success",
                    "last_run": datetime.now(),
                    "description": "Customer dimension table",
                },
                {
                    "name": "fct_orders",
                    "path": "models/facts/fct_orders.sql",
                    "status": "success",
                    "last_run": datetime.now(),
                    "description": "Orders fact table",
                },
            ]
        except Exception as e:
            logger.error(f"Error getting dbt models: {e}")
            return []


class SnowflakeAdapter(BaseAdapter):
    """Snowflake integration adapter"""

    def __init__(self):
        self.connection = None
        self.engine = None

    async def initialize(self):
        """Initialize Snowflake connection"""
        try:
            if all(
                [
                    settings.snowflake_account,
                    settings.snowflake_user,
                    settings.snowflake_password,
                ]
            ):
                # Create connection string
                conn_string = (
                    f"snowflake://{settings.snowflake_user}:{settings.snowflake_password}"
                    f"@{settings.snowflake_account}/{settings.snowflake_database}"
                    f"/{settings.snowflake_schema}?warehouse={settings.snowflake_warehouse}"
                )
                self.engine = create_engine(conn_string)
                logger.info("Snowflake adapter initialized")
            else:
                logger.warning("Snowflake credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake adapter: {e}")
            raise

    async def cleanup(self):
        """Cleanup Snowflake resources"""
        if self.engine:
            self.engine.dispose()

    async def health_check(self) -> dict[str, Any]:
        """Check Snowflake health"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute("SELECT CURRENT_VERSION()")
                    version = result.fetchone()[0]
                    return {"status": "healthy", "version": version}
            return {"status": "not_configured"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def get_warehouses(self) -> list[dict[str, Any]]:
        """Get Snowflake warehouses"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute("SHOW WAREHOUSES")
                    warehouses = []
                    for row in result:
                        warehouses.append(
                            {
                                "name": row[0],
                                "size": row[2],
                                "state": row[1],
                                "auto_suspend": row[6],
                            }
                        )
                    return warehouses
            return []
        except Exception as e:
            logger.error(f"Error getting Snowflake warehouses: {e}")
            return []


class DuckDBAdapter(BaseAdapter):
    """DuckDB integration adapter"""

    def __init__(self):
        self.connection = None

    async def initialize(self):
        """Initialize DuckDB connection"""
        try:
            self.connection = duckdb.connect(settings.duckdb_path)
            logger.info("DuckDB adapter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DuckDB adapter: {e}")
            raise

    async def cleanup(self):
        """Cleanup DuckDB resources"""
        if self.connection:
            self.connection.close()

    async def health_check(self) -> dict[str, Any]:
        """Check DuckDB health"""
        try:
            if self.connection:
                result = self.connection.execute("SELECT version()").fetchone()
                return {"status": "healthy", "version": result[0]}
            return {"status": "not_initialized"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def get_tables(self) -> list[dict[str, Any]]:
        """Get DuckDB tables"""
        try:
            if self.connection:
                result = self.connection.execute(
                    "SELECT table_name, table_schema FROM information_schema.tables"
                ).fetchall()

                tables = []
                for row in result:
                    table_name, schema = row
                    # Get row count
                    try:
                        count_result = self.connection.execute(
                            f"SELECT COUNT(*) FROM {schema}.{table_name}"
                        ).fetchone()
                        row_count = count_result[0] if count_result else None
                    except:
                        row_count = None

                    tables.append(
                        {
                            "name": table_name,
                            "schema": schema,
                            "row_count": row_count,
                            "columns": [],  # Could be populated with column info
                        }
                    )

                return tables
            return []
        except Exception as e:
            logger.error(f"Error getting DuckDB tables: {e}")
            return []


class DataHubAdapter(BaseAdapter):
    """DataHub integration adapter"""

    def __init__(self):
        self.emitter = None
        self.client = None

    async def initialize(self):
        """Initialize DataHub connection"""
        try:
            if settings.datahub_server:
                self.emitter = DatahubRestEmitter(gms_server=settings.datahub_server)
                self.client = httpx.AsyncClient(base_url=settings.datahub_server)
                logger.info("DataHub adapter initialized")
            else:
                logger.warning("DataHub server not configured")
        except Exception as e:
            logger.error(f"Failed to initialize DataHub adapter: {e}")
            raise

    async def cleanup(self):
        """Cleanup DataHub resources"""
        if self.client:
            await self.client.aclose()

    async def health_check(self) -> dict[str, Any]:
        """Check DataHub health"""
        try:
            if self.client:
                response = await self.client.get("/health")
                return {"status": "healthy", "response_code": response.status_code}
            return {"status": "not_configured"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def get_datasets(self) -> list[dict[str, Any]]:
        """Get DataHub datasets"""
        try:
            # Mock implementation - replace with actual DataHub API calls
            return [
                {
                    "urn": "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table1,PROD)",
                    "name": "customer_data",
                    "platform": "snowflake",
                    "description": "Customer information dataset",
                    "tags": ["customer", "pii"],
                },
                {
                    "urn": "urn:li:dataset:(urn:li:dataPlatform:duckdb,orders,PROD)",
                    "name": "orders",
                    "platform": "duckdb",
                    "description": "Order transactions",
                    "tags": ["orders", "transactions"],
                },
            ]
        except Exception as e:
            logger.error(f"Error getting DataHub datasets: {e}")
            return []
