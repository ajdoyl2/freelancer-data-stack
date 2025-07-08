# Project Requirements Plan: Comprehensive MCP Server Integration

**Project ID**: PRP-MCP-001
**Created**: 2025-01-08
**Priority**: High
**Estimated Duration**: 4-6 weeks
**Status**: Planning Phase

## Executive Summary

This PRP outlines the comprehensive integration of Model Context Protocol (MCP) servers into the AI agent-driven data stack, focusing on security, performance, and extensive tool capabilities. The plan addresses critical security vulnerabilities in the current implementation while adding 24 new MCP server integrations to significantly expand AI agent capabilities with complete data stack coverage.

### Key Objectives
1. **Security Hardening**: Fix critical vulnerabilities (CORS wildcard, authentication gaps)
2. **MCP Server Integration**: Add 24 high-priority community and official MCP servers (10 Tier 1, 9 Tier 2, 5 Tier 3)
3. **Testing Framework**: Implement comprehensive testing for MCP integrations
4. **Agent Enhancement**: Modify agents to leverage new MCP capabilities
5. **Performance Optimization**: Manage 27.5% token usage increase through caching and optimization

### Business Impact
- **Enhanced AI Capabilities**: 300+ new tools available to AI agents across complete data stack
- **Improved Security**: Production-ready authentication and input validation
- **Better Performance**: Connection pooling and caching reduce latency by 40%
- **Comprehensive Testing**: 95% code coverage for MCP integrations
- **Future-Proof Architecture**: Scalable foundation for additional MCP servers

## Current State Analysis

### Existing MCP Infrastructure ✅
- **FastAPI MCP Server**: Port 8003 with GraphQL and WebSocket support
- **Base Adapters**: Snowflake, DuckDB, DataHub, dbt, Dagster integrations
- **Docker Integration**: Configured in docker-compose.yml with health checks
- **Agent Framework**: Pydantic AI agents with role-based capabilities

### Critical Issues Identified ❌
- **Security Vulnerabilities**:
  - CORS configured with `allow_origins=["*"]` (major risk)
  - No authentication or authorization
  - Missing input validation and sanitization
  - Potential command injection vectors
- **Performance Issues**:
  - No connection pooling
  - Missing caching layer
  - No rate limiting
  - Synchronous database connections
- **Operational Gaps**:
  - Basic error handling without retries
  - No structured logging
  - Missing monitoring metrics
  - No backup or disaster recovery

## Technical Requirements

### 1. Security Hardening (Critical Priority)

#### 1.1 Authentication and Authorization
```python
# Implementation: JWT-based authentication with role-based access
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

class AuthManager:
    def __init__(self):
        self.secret_key = settings.jwt_secret
        self.algorithm = "HS256"

    async def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

#### 1.2 Input Validation and Sanitization
```python
# Implementation: Comprehensive input validation
from pydantic import BaseModel, validator
import re

class MCPQueryRequest(BaseModel):
    query: str
    parameters: dict = {}

    @validator('query')
    def validate_sql_query(cls, v):
        # Prevent SQL injection and command injection
        forbidden_patterns = [
            r';\s*drop\s+table', r';\s*delete\s+from', r';\s*update\s+',
            r'exec\s*\(', r'system\s*\(', r'eval\s*\(', r'import\s+os'
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, v.lower()):
                raise ValueError(f"Potentially dangerous query detected: {pattern}")

        return v
```

#### 1.3 CORS Configuration
```python
# Replace wildcard CORS with specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 2. MCP Server Integrations (24 High-Priority Servers)

#### 2.1 Tier 1: Essential Data Stack Integrations

**Core Analytics & Data Processing (Original)**
1. **disler/quick-data-mcp** - 32 analytics tools for data analysis workflows
2. **motherduckdb/mcp-server-motherduck** - DuckDB cloud integration and analytics
3. **MammothGrowth/dbt-cli-mcp** - dbt command line interface for transformation
4. **ergut/mcp-bigquery-server** - BigQuery integration for cloud data warehouse
5. **crystaldba/postgres-mcp** - PostgreSQL optimization and performance tuning

**Critical Data Stack Infrastructure (Newly Added)**
6. **yangkyeongmo/mcp-server-apache-airflow** - Apache Airflow orchestration and DAG management
   - **Integration Value**: Direct integration with Airflow 3.0.2 for workflow automation
   - **Key Features**: DAG management, task monitoring, pipeline orchestration
   - **Production Status**: Actively maintained with comprehensive API coverage

7. **confluentinc/mcp-confluent** - Kafka/Confluent streaming integration
   - **Integration Value**: Native integration with Kafka 7.4.0, Schema Registry, and KSQL
   - **Key Features**: Topic management, connector operations, Flink SQL execution
   - **Production Status**: Official Confluent support, enterprise-grade reliability

8. **acryldata/mcp-server-datahub** - DataHub data catalog and governance
   - **Integration Value**: Essential for DataHub v0.11.0 metadata management
   - **Key Features**: Asset discovery, metadata querying, lineage traversal
   - **Production Status**: Official Acryl Data support, supports Core and Cloud versions

9. **elastic/mcp-server-elasticsearch** - Elasticsearch search analytics
   - **Integration Value**: Direct integration with Elasticsearch 7.17.9 for search operations
   - **Key Features**: Index management, search analytics, cluster monitoring
   - **Production Status**: Official Elastic support with comprehensive documentation

10. **neo4j-contrib/mcp-neo4j** - Neo4j graph database operations
    - **Integration Value**: Critical for Neo4j 4.4.9 graph analytics and traversal
    - **Key Features**: Cypher query execution, relationship analysis, graph modeling
    - **Production Status**: Official Neo4j contribution with active development

#### 2.2 Tier 2: Enhanced Capabilities
11. **redis/mcp-redis** - Redis session and cache management
12. **hyeongjun-dev/metabase-mcp-server** - Metabase BI automation
13. **grafana/mcp-grafana** - Grafana monitoring integration
14. **qdrant/mcp-server-qdrant** - Qdrant vector search operations
15. **zilliztech/mcp-server-milvus** - Milvus vector database
16. **waii-ai/waii-mcp-server** - Natural language SQL
17. **unravel-team/mcp-analyst** - Data analysis capabilities
18. **marlonluo2018/pandas-mcp-server** - Pandas operations
19. **krzko/google-cloud-mcp** - GCP integration

#### 2.3 Tier 3: Specialized Tools
20. **singlestore-labs/mcp-server-singlestore** - Distributed SQL
21. **Niell007/supabase-mcp-server** - Supabase integration
22. **shionhonda/mcp-gsheet** - Google Sheets integration
23. **Lemos1347/chromadb-mcp** - ChromaDB vector search
24. **atcol/glue-mcp** - AWS Glue Data Catalog

#### 2.4 Integration Architecture
```python
# MCP Server Registry with Dynamic Loading
class MCPServerRegistry:
    def __init__(self):
        self.servers = {}
        self.health_status = {}

    async def register_server(self, name: str, config: dict):
        """Register MCP server with health monitoring"""
        server = MCPServerClient(config)
        await server.initialize()

        self.servers[name] = server
        self.health_status[name] = await server.health_check()

        logger.info(f"Registered MCP server: {name}")

    async def execute_tool(self, server_name: str, tool_name: str, parameters: dict):
        """Execute tool on specific MCP server"""
        server = self.servers.get(server_name)
        if not server:
            raise ValueError(f"MCP server not found: {server_name}")

        return await server.call_tool(tool_name, parameters)
```

### 3. Performance Optimization Framework

#### 3.1 Connection Pooling
```python
# Database connection pooling implementation
from sqlalchemy.pool import QueuePool
from contextlib import asynccontextmanager

class ConnectionManager:
    def __init__(self):
        self.pools = {}

    def create_pool(self, database_url: str, pool_size: int = 10):
        """Create connection pool for database"""
        engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        return engine

    @asynccontextmanager
    async def get_connection(self, pool_name: str):
        """Get connection from pool with proper cleanup"""
        pool = self.pools[pool_name]
        async with pool.begin() as conn:
            yield conn
```

#### 3.2 Intelligent Caching Layer
```python
# Redis-based caching with TTL and invalidation
class MCPCacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host=settings.redis_host)
        self.default_ttl = 300  # 5 minutes

    async def cached_tool_call(self, server_name: str, tool_name: str,
                             parameters: dict, ttl: int = None):
        """Cache MCP tool calls with intelligent invalidation"""
        cache_key = f"mcp:{server_name}:{tool_name}:{hash(str(parameters))}"

        # Check cache first
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

        # Execute and cache result
        result = await self.registry.execute_tool(server_name, tool_name, parameters)

        ttl = ttl or self.default_ttl
        await self.redis_client.setex(cache_key, ttl, json.dumps(result, default=str))

        return result
```

#### 3.3 Rate Limiting Implementation
```python
# Sliding window rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/mcp/{server_name}/tools/{tool_name}")
@limiter.limit("30/minute")
async def execute_mcp_tool(
    request: Request,
    server_name: str,
    tool_name: str,
    parameters: MCPQueryRequest
):
    """Rate-limited MCP tool execution"""
    return await mcp_registry.execute_tool(server_name, tool_name, parameters.dict())
```

### 4. Comprehensive Testing Framework

#### 4.1 Unit Testing for MCP Servers
```python
# Test framework for MCP server integrations
import pytest
from unittest.mock import AsyncMock, MagicMock

class TestMCPIntegrations:
    @pytest.fixture
    def mock_mcp_server(self):
        server = MagicMock()
        server.call_tool = AsyncMock()
        server.list_tools = AsyncMock(return_value=[
            {"name": "test_tool", "description": "Test tool"}
        ])
        server.health_check = AsyncMock(return_value={"status": "healthy"})
        return server

    @pytest.mark.asyncio
    async def test_quick_data_mcp_integration(self, mock_mcp_server):
        """Test quick-data-mcp server integration"""
        registry = MCPServerRegistry()
        registry.servers["quick-data"] = mock_mcp_server

        # Test tool execution
        result = await registry.execute_tool(
            "quick-data",
            "analyze_dataframe",
            {"dataframe_path": "/tmp/test.csv"}
        )

        mock_mcp_server.call_tool.assert_called_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_mcp_server_health_monitoring(self):
        """Test health monitoring for all MCP servers"""
        registry = MCPServerRegistry()

        # Mock multiple servers
        for server_name in ["quick-data", "motherduck", "dbt-cli"]:
            mock_server = MagicMock()
            mock_server.health_check = AsyncMock(return_value={
                "status": "healthy",
                "response_time": 0.1
            })
            registry.servers[server_name] = mock_server

        health_results = await registry.check_all_health()

        assert len(health_results) == 3
        assert all(result["status"] == "healthy" for result in health_results.values())
```

#### 4.2 Integration Testing with AI Agents
```python
# Agent-MCP integration tests
class TestAgentMCPIntegration:
    @pytest.mark.asyncio
    async def test_data_engineer_with_mcp_tools(self):
        """Test Data Engineer agent using MCP tools"""
        agent = DataEngineer(model_name="openai:gpt-4")

        # Mock MCP registry
        with patch('agents.data_engineer.mcp_registry') as mock_registry:
            mock_registry.execute_tool = AsyncMock(return_value={
                "success": True,
                "result": "Pipeline executed successfully"
            })

            request = WorkflowRequest(
                user_prompt="Run the analytics pipeline using Meltano",
                context={"pipeline_name": "customer_analytics"}
            )

            response = await agent.execute_task(request)

            assert response.status == ResponseStatus.SUCCESS
            mock_registry.execute_tool.assert_called()

    @pytest.mark.asyncio
    async def test_analytics_engineer_dbt_mcp(self):
        """Test Analytics Engineer using dbt MCP server"""
        agent = AnalyticsEngineer(model_name="openai:gpt-4")

        with patch('agents.analytics_engineer.mcp_registry') as mock_registry:
            mock_registry.execute_tool = AsyncMock(return_value={
                "success": True,
                "models_run": ["customers", "orders", "revenue"]
            })

            request = WorkflowRequest(
                user_prompt="Run dbt models for customer analytics",
                context={"models": ["customers", "orders"]}
            )

            response = await agent.execute_task(request)

            assert response.status == ResponseStatus.SUCCESS
            assert "customers" in str(response.output)
```

#### 4.3 Performance and Load Testing
```python
# Load testing for MCP server performance
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class MCPLoadTester:
    def __init__(self, registry: MCPServerRegistry):
        self.registry = registry

    async def load_test_tool_execution(self, server_name: str, tool_name: str,
                                     concurrent_requests: int = 10,
                                     total_requests: int = 100):
        """Load test MCP tool execution"""

        async def execute_single_request():
            start_time = time.time()
            try:
                await self.registry.execute_tool(server_name, tool_name, {})
                return time.time() - start_time, True
            except Exception as e:
                return time.time() - start_time, False

        # Execute concurrent requests
        tasks = []
        for _ in range(total_requests):
            tasks.append(execute_single_request())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        response_times = [r[0] for r in results if isinstance(r, tuple)]
        success_count = sum(1 for r in results if isinstance(r, tuple) and r[1])

        return {
            "total_requests": total_requests,
            "successful_requests": success_count,
            "average_response_time": sum(response_times) / len(response_times),
            "max_response_time": max(response_times),
            "success_rate": success_count / total_requests
        }
```

### 5. Agent Enhancement Strategy

#### 5.1 MCP Tool Integration in Agents
```python
# Enhanced base agent with MCP capabilities
class MCPEnabledAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mcp_registry = MCPServerRegistry()

    async def get_available_mcp_tools(self) -> list[dict]:
        """Get all available MCP tools for this agent"""
        tools = []
        for server_name, server in self.mcp_registry.servers.items():
            server_tools = await server.list_tools()
            for tool in server_tools:
                tools.append({
                    "server": server_name,
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("parameters", {})
                })
        return tools

    async def execute_mcp_tool(self, server_name: str, tool_name: str,
                             parameters: dict) -> dict:
        """Execute MCP tool with error handling and logging"""
        try:
            self.logger.info(f"Executing MCP tool: {server_name}.{tool_name}")

            result = await self.mcp_registry.execute_tool(
                server_name, tool_name, parameters
            )

            self.logger.info(f"MCP tool execution successful: {server_name}.{tool_name}")
            return result

        except Exception as e:
            self.logger.error(f"MCP tool execution failed: {server_name}.{tool_name} - {e}")
            raise
```

#### 5.2 Data Engineer Agent with MCP Tools
```python
# Enhanced Data Engineer with comprehensive MCP integration
class EnhancedDataEngineer(DataEngineer, MCPEnabledAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Register preferred MCP servers for data engineering
        self.preferred_mcp_servers = [
            "quick-data",      # Analytics operations
            "dbt-cli",         # dbt commands
            "motherduck",      # DuckDB operations
            "bigquery",        # BigQuery access
            "postgres"         # PostgreSQL operations
        ]

    async def _handle_pipeline_task_with_mcp(self, request: WorkflowRequest,
                                           analysis: dict) -> dict:
        """Enhanced pipeline handling with MCP tools"""
        pipeline_prompt = f"""
        As a Data Engineer with access to MCP tools, handle this pipeline request:

        Request: {request.user_prompt}
        Available MCP Tools: {await self.get_available_mcp_tools()}

        Use appropriate MCP tools to:
        1. Analyze data sources using quick-data-mcp
        2. Execute dbt operations using dbt-cli-mcp
        3. Query databases using appropriate MCP servers
        4. Monitor pipeline performance

        Provide specific MCP tool calls and their expected results.
        """

        response = await self.run_with_retry(pipeline_prompt)

        # Parse response for MCP tool calls
        mcp_calls = self._parse_mcp_tool_calls(str(response))

        # Execute MCP tools
        mcp_results = {}
        for call in mcp_calls:
            try:
                result = await self.execute_mcp_tool(
                    call["server"], call["tool"], call["parameters"]
                )
                mcp_results[f"{call['server']}.{call['tool']}"] = result
            except Exception as e:
                mcp_results[f"{call['server']}.{call['tool']}"] = {
                    "error": str(e), "success": False
                }

        return {
            "task_type": "pipeline_with_mcp",
            "agent_response": str(response),
            "mcp_tool_calls": mcp_calls,
            "mcp_results": mcp_results,
            "pipeline_status": "completed" if all(
                r.get("success", True) for r in mcp_results.values()
            ) else "partial_failure"
        }
```

#### 5.3 Analytics Engineer with dbt MCP Integration
```python
# Enhanced Analytics Engineer with dbt MCP integration
class EnhancedAnalyticsEngineer(AnalyticsEngineer, MCPEnabledAgent):
    async def _handle_dbt_task_with_mcp(self, request: WorkflowRequest) -> dict:
        """Handle dbt tasks using dbt-cli MCP server"""

        # Extract dbt commands from request
        dbt_commands = self._extract_dbt_commands(request.user_prompt)

        results = {}
        for command in dbt_commands:
            try:
                result = await self.execute_mcp_tool(
                    "dbt-cli",
                    "run_command",
                    {"command": command, "project_dir": "/app/transform"}
                )
                results[command] = result
            except Exception as e:
                results[command] = {"error": str(e), "success": False}

        return {
            "task_type": "dbt_with_mcp",
            "dbt_commands": dbt_commands,
            "dbt_results": results,
            "models_affected": self._extract_models_from_results(results)
        }
```

### 6. Monitoring and Observability

#### 6.1 Comprehensive Monitoring Dashboard
```python
# Prometheus metrics for MCP operations
from prometheus_client import Counter, Histogram, Gauge

# MCP-specific metrics
MCP_REQUESTS_TOTAL = Counter(
    'mcp_requests_total',
    'Total MCP requests',
    ['server', 'tool', 'status']
)

MCP_REQUEST_DURATION = Histogram(
    'mcp_request_duration_seconds',
    'MCP request duration',
    ['server', 'tool']
)

MCP_CACHE_HITS = Counter(
    'mcp_cache_hits_total',
    'MCP cache hits',
    ['server', 'tool']
)

MCP_ACTIVE_CONNECTIONS = Gauge(
    'mcp_active_connections',
    'Active MCP server connections',
    ['server']
)

# Monitoring middleware
@app.middleware("http")
async def mcp_monitoring_middleware(request: Request, call_next):
    """Monitor MCP requests with detailed metrics"""
    if request.url.path.startswith("/api/mcp/"):
        start_time = time.time()

        # Extract server and tool from path
        path_parts = request.url.path.split("/")
        server_name = path_parts[3] if len(path_parts) > 3 else "unknown"
        tool_name = path_parts[5] if len(path_parts) > 5 else "unknown"

        response = await call_next(request)

        duration = time.time() - start_time
        status = "success" if response.status_code < 400 else "error"

        # Record metrics
        MCP_REQUESTS_TOTAL.labels(
            server=server_name,
            tool=tool_name,
            status=status
        ).inc()

        MCP_REQUEST_DURATION.labels(
            server=server_name,
            tool=tool_name
        ).observe(duration)

        return response

    return await call_next(request)
```

#### 6.2 Health Monitoring System
```python
# Comprehensive health monitoring for MCP servers
class MCPHealthMonitor:
    def __init__(self, registry: MCPServerRegistry):
        self.registry = registry
        self.health_history = {}

    async def continuous_health_monitoring(self, interval: int = 30):
        """Continuous health monitoring with alerting"""
        while True:
            health_results = {}

            for server_name, server in self.registry.servers.items():
                try:
                    start_time = time.time()
                    health = await server.health_check()
                    response_time = time.time() - start_time

                    health_data = {
                        "status": health.get("status", "unknown"),
                        "response_time": response_time,
                        "timestamp": datetime.now(),
                        "details": health
                    }

                    health_results[server_name] = health_data

                    # Update Prometheus metrics
                    MCP_ACTIVE_CONNECTIONS.labels(server=server_name).set(
                        1 if health_data["status"] == "healthy" else 0
                    )

                except Exception as e:
                    health_results[server_name] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now()
                    }

                    MCP_ACTIVE_CONNECTIONS.labels(server=server_name).set(0)

            # Store health history
            self.health_history[datetime.now()] = health_results

            # Check for alerts
            await self._check_health_alerts(health_results)

            await asyncio.sleep(interval)

    async def _check_health_alerts(self, health_results: dict):
        """Check health results and send alerts if needed"""
        unhealthy_servers = [
            name for name, health in health_results.items()
            if health.get("status") != "healthy"
        ]

        if unhealthy_servers:
            alert_message = f"Unhealthy MCP servers detected: {', '.join(unhealthy_servers)}"
            logger.error(alert_message)

            # Send alert to monitoring system
            await self._send_alert(alert_message, unhealthy_servers)
```

## Implementation Roadmap

### Phase 1: Security and Foundation (Week 1-2)
**Priority**: Critical
**Duration**: 2 weeks

#### Week 1: Security Hardening
- [ ] **Day 1-2**: Implement JWT authentication system
  - Create AuthManager class with token verification
  - Add authentication middleware to all MCP endpoints
  - Create user management system with role-based access

- [ ] **Day 3-4**: Input validation and sanitization
  - Implement comprehensive Pydantic models for all inputs
  - Add SQL injection prevention
  - Create command injection protection
  - Add XSS prevention measures

- [ ] **Day 5**: CORS and security headers
  - Replace wildcard CORS with specific domain configuration
  - Add security headers (HSTS, CSP, X-Frame-Options)
  - Implement request size limits

#### Week 2: Performance Foundation
- [ ] **Day 1-2**: Connection pooling implementation
  - Create ConnectionManager with SQLAlchemy pools
  - Update all adapters to use connection pooling
  - Add connection health monitoring

- [ ] **Day 3-4**: Caching layer implementation
  - Set up Redis-based caching system
  - Implement intelligent cache invalidation
  - Add cache warming strategies

- [ ] **Day 5**: Rate limiting and monitoring
  - Implement sliding window rate limiting
  - Add Prometheus metrics collection
  - Create structured logging system

### Phase 2: Core MCP Integrations (Week 3-4)
**Priority**: High
**Duration**: 2 weeks

#### Week 3: Tier 1 MCP Server Integration
- [ ] **Day 1**: quick-data-mcp server integration
  - Docker container setup and configuration
  - Tool registration and testing
  - Integration with existing analytics workflows

- [ ] **Day 2**: motherduckdb/mcp-server-motherduck
  - DuckDB cloud connectivity setup
  - Integration with existing DuckDB workflows
  - Performance optimization for large datasets

- [ ] **Day 3**: MammothGrowth/dbt-cli-mcp
  - dbt CLI integration and configuration
  - Integration with Analytics Engineer agent
  - Automated testing for dbt operations

- [ ] **Day 4**: ergut/mcp-bigquery-server
  - BigQuery authentication and setup
  - Cost control and query limit implementation
  - Integration with Data Engineer workflows

- [ ] **Day 5**: crystaldba/postgres-mcp
  - PostgreSQL optimization tool integration
  - Database health monitoring setup
  - Performance tuning automation

#### Week 4: Tier 2 MCP Server Integration
- [ ] **Day 1-2**: Vector database integrations
  - zilliztech/mcp-server-milvus setup
  - Lemos1347/chromadb-mcp integration
  - Vector search capability testing

- [ ] **Day 3**: Natural language SQL integration
  - waii-ai/waii-mcp-server setup
  - Integration with all agent types
  - Query optimization and validation

- [ ] **Day 4**: Data analysis tools
  - unravel-team/mcp-analyst integration
  - marlonluo2018/pandas-mcp-server setup
  - Performance testing for large datasets

- [ ] **Day 5**: Cloud platform integrations
  - krzko/google-cloud-mcp setup
  - Multi-cloud strategy implementation
  - Security and credential management

### Phase 3: Testing and Agent Enhancement (Week 5)
**Priority**: Medium
**Duration**: 1 week

#### Week 5: Comprehensive Testing Framework
- [ ] **Day 1-2**: Unit testing implementation
  - Create test fixtures for all MCP servers
  - Implement mock strategies for external services
  - Add automated test data generation

- [ ] **Day 3**: Integration testing
  - Agent-MCP integration tests
  - End-to-end workflow testing
  - Cross-server interaction testing

- [ ] **Day 4**: Performance and load testing
  - Load testing for concurrent MCP requests
  - Memory and CPU usage optimization
  - Token usage monitoring and optimization

- [ ] **Day 5**: Agent enhancement
  - Update all agents to use MCP tools
  - Add MCP tool discovery and selection logic
  - Implement agent-specific MCP preferences

### Phase 4: Advanced Features and Production Readiness (Week 6)
**Priority**: Medium
**Duration**: 1 week

#### Week 6: Production Readiness
- [ ] **Day 1**: Tier 3 MCP server integration
  - singlestore-labs/mcp-server-singlestore
  - Niell007/supabase-mcp-server
  - shionhonda/mcp-gsheet
  - atcol/glue-mcp

- [ ] **Day 2**: Advanced monitoring and alerting
  - Grafana dashboard creation
  - Alert rule configuration
  - Health monitoring automation

- [ ] **Day 3**: Backup and disaster recovery
  - Automated backup system implementation
  - Disaster recovery procedures
  - Data migration tools

- [ ] **Day 4**: Documentation and deployment
  - Complete API documentation
  - Deployment automation
  - Production environment setup

- [ ] **Day 5**: Performance optimization and final testing
  - Final performance tuning
  - Security audit and penetration testing
  - Go-live preparation

## Technical Specifications

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Agent Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Data Platform │  Data Engineer │ Analytics │ Data Scientist    │
│   Engineer     │                │ Engineer  │                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                  MCP Gateway & Registry                         │
├─────────────────────────────────────────────────────────────────┤
│  • Authentication & Authorization                               │
│  • Rate Limiting & Caching                                     │
│  • Load Balancing & Health Monitoring                          │
│  • Tool Discovery & Registration                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                     MCP Servers                                │
├─────────────────────────────────────────────────────────────────┤
│  Tier 1: Essential Data Stack                                  │
│  ├─ quick-data-mcp      (32 analytics tools)                   │
│  ├─ motherduck-mcp      (DuckDB cloud)                         │
│  ├─ dbt-cli-mcp         (dbt operations)                       │
│  ├─ bigquery-mcp        (BigQuery access)                      │
│  └─ postgres-mcp        (PostgreSQL optimization)              │
│                                                                 │
│  Tier 2: Enhanced Capabilities                                 │
│  ├─ milvus-mcp          (Vector database)                      │
│  ├─ waii-mcp            (Natural language SQL)                 │
│  ├─ analyst-mcp         (Data analysis)                        │
│  ├─ pandas-mcp          (Pandas operations)                    │
│  └─ google-cloud-mcp    (GCP integration)                      │
│                                                                 │
│  Tier 3: Specialized Tools                                     │
│  ├─ singlestore-mcp     (Distributed SQL)                      │
│  ├─ supabase-mcp        (Supabase integration)                 │
│  ├─ gsheet-mcp          (Google Sheets)                        │
│  ├─ chromadb-mcp        (Vector search)                        │
│  └─ glue-mcp            (AWS Glue)                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                 Data Infrastructure                             │
├─────────────────────────────────────────────────────────────────┤
│  DuckDB │ Snowflake │ PostgreSQL │ BigQuery │ DataHub │ Redis   │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Requirements

#### Response Time Targets
- **MCP Tool Execution**: < 2 seconds (95th percentile)
- **Agent Workflow Completion**: < 30 seconds (95th percentile)
- **Health Check Response**: < 500ms (99th percentile)
- **Cache Hit Response**: < 100ms (99th percentile)

#### Throughput Targets
- **Concurrent MCP Requests**: 100 requests/second
- **Agent Workflows**: 10 concurrent workflows
- **Database Connections**: 50 concurrent connections per adapter
- **Memory Usage**: < 2GB per MCP server container

#### Reliability Targets
- **Uptime**: 99.9% availability
- **Error Rate**: < 0.1% for MCP tool executions
- **Cache Hit Rate**: > 70% for repeated queries
- **Health Check Success**: > 99.5%

### Security Requirements

#### Authentication and Authorization
- **JWT Token Expiry**: 8 hours for interactive sessions
- **API Key Rotation**: Every 90 days
- **Role-Based Access**: 5 distinct permission levels
- **Session Management**: Redis-backed with 24-hour TTL

#### Input Validation
- **SQL Injection Prevention**: Comprehensive pattern matching and parameterized queries
- **Command Injection Prevention**: Whitelist-based command validation
- **XSS Prevention**: HTML sanitization and CSP headers
- **Rate Limiting**: 100 requests/minute per user, 1000 requests/minute per organization

#### Data Protection
- **Encryption in Transit**: TLS 1.3 for all communications
- **Encryption at Rest**: AES-256 for sensitive data storage
- **Audit Logging**: All MCP tool executions and admin actions
- **Data Retention**: 90 days for logs, 1 year for audit trails

## Testing Strategy

### Unit Testing Requirements
```python
# Test coverage targets
- MCP server integrations: 95% code coverage
- Authentication system: 100% code coverage
- Input validation: 100% code coverage
- Agent MCP integration: 90% code coverage
- Error handling: 95% code coverage
```

### Integration Testing Framework
```python
# Test scenarios to cover
1. Agent → MCP Gateway → MCP Server → Data Source
2. Authentication flow with JWT tokens
3. Rate limiting and caching behavior
4. Error propagation and handling
5. Health monitoring and alerting
6. Backup and disaster recovery procedures
```

### Performance Testing Specifications
```python
# Load testing parameters
- Concurrent users: 50-200
- Test duration: 30 minutes sustained load
- Ramp-up time: 5 minutes
- Success criteria:
  * 95th percentile response time < 2 seconds
  * Error rate < 0.1%
  * Memory usage stable (no leaks)
  * CPU usage < 70% average
```

## Deployment Configuration

### Docker Compose Updates
```yaml
# New services to add to docker-compose.yml
services:
  # MCP Server Registry
  mcp-registry:
    build: ./mcp-registry
    environment:
      - REDIS_HOST=redis
      - AUTH_SECRET=${JWT_SECRET}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    depends_on:
      - redis
      - prometheus
    ports:
      - "8004:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Quick Data MCP Server
  quick-data-mcp:
    image: disler/quick-data-mcp:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATA_PATH=/data
    volumes:
      - ./volumes/duckdb:/data
    ports:
      - "8005:8000"

  # MotherDuck MCP Server
  motherduck-mcp:
    image: motherduckdb/mcp-server:latest
    environment:
      - MOTHERDUCK_TOKEN=${MOTHERDUCK_TOKEN}
      - DUCKDB_PATH=/data/analytics.db
    volumes:
      - ./volumes/duckdb:/data

  # dbt CLI MCP Server
  dbt-cli-mcp:
    image: mammothgrowth/dbt-cli-mcp:latest
    environment:
      - DBT_PROJECT_DIR=/app/transform
      - DBT_PROFILES_DIR=/app/dbt_profiles
    volumes:
      - ./transform:/app/transform
      - ./dbt_profiles:/app/dbt_profiles

  # BigQuery MCP Server
  bigquery-mcp:
    image: ergut/bigquery-mcp:latest
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-key.json
      - QUERY_LIMIT_GB=1
    volumes:
      - ./credentials/gcp-key.json:/app/gcp-key.json

  # PostgreSQL MCP Server
  postgres-mcp:
    image: crystaldba/postgres-mcp:latest
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=data_stack
    depends_on:
      - postgres

  # Apache Airflow MCP Server
  airflow-mcp:
    image: yangkyeongmo/mcp-server-apache-airflow:latest
    environment:
      - AIRFLOW_HOST=airflow-webserver
      - AIRFLOW_PORT=8080
      - AIRFLOW_USERNAME=${AIRFLOW_USERNAME}
      - AIRFLOW_PASSWORD=${AIRFLOW_PASSWORD}
    depends_on:
      - airflow-webserver
    ports:
      - "8006:8000"

  # Confluent/Kafka MCP Server
  confluent-mcp:
    image: confluentinc/mcp-confluent:latest
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - SCHEMA_REGISTRY_URL=http://schema-registry:8081
      - KSQL_SERVER_URL=http://ksqldb-server:8088
    depends_on:
      - kafka
      - schema-registry
    ports:
      - "8007:8000"

  # DataHub MCP Server
  datahub-mcp:
    image: acryldata/mcp-server-datahub:latest
    environment:
      - DATAHUB_GMS_HOST=datahub-gms
      - DATAHUB_GMS_PORT=8081
      - DATAHUB_TOKEN=${DATAHUB_TOKEN}
    depends_on:
      - datahub-gms
    ports:
      - "8008:8000"

  # Elasticsearch MCP Server
  elasticsearch-mcp:
    image: elastic/mcp-server-elasticsearch:latest
    environment:
      - ELASTICSEARCH_HOST=elasticsearch
      - ELASTICSEARCH_PORT=9200
      - ELASTICSEARCH_INDEX_PREFIX=data_stack
    depends_on:
      - elasticsearch
    ports:
      - "8009:8000"

  # Neo4j MCP Server
  neo4j-mcp:
    image: neo4j-contrib/mcp-neo4j:latest
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USERNAME=${NEO4J_USERNAME}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
    depends_on:
      - neo4j
    ports:
      - "8010:8000"
```

### Environment Variables
```bash
# Core MCP Configuration
JWT_SECRET=your-32-character-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_PER_MINUTE=100
CACHE_TTL_SECONDS=300
HEALTH_CHECK_INTERVAL=30

# Original Tier 1 MCP Server Variables
MOTHERDUCK_TOKEN=your-motherduck-token
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json
QUERY_LIMIT_GB=1

# New Tier 1 MCP Server Variables
AIRFLOW_USERNAME=${AIRFLOW_USERNAME:-ajdoyle}
AIRFLOW_PASSWORD=${AIRFLOW_PASSWORD}
DATAHUB_TOKEN=${DATAHUB_TOKEN}
NEO4J_USERNAME=${NEO4J_USERNAME:-ajdoyle}
NEO4J_PASSWORD=${NEO4J_PASSWORD}

# Port Configuration for MCP Servers
MCP_REGISTRY_PORT=8004
QUICK_DATA_MCP_PORT=8005
AIRFLOW_MCP_PORT=8006
CONFLUENT_MCP_PORT=8007
DATAHUB_MCP_PORT=8008
ELASTICSEARCH_MCP_PORT=8009
NEO4J_MCP_PORT=8010
```

## Monitoring and Alerting

### Prometheus Metrics
```yaml
# Additional metrics to monitor
- mcp_requests_total{server, tool, status}
- mcp_request_duration_seconds{server, tool}
- mcp_cache_hits_total{server, tool}
- mcp_active_connections{server}
- mcp_authentication_failures_total
- mcp_rate_limit_exceeded_total{user, endpoint}
- mcp_token_usage_total{agent, server, tool}
- mcp_error_rate{server, error_type}
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "MCP Server Monitoring",
    "panels": [
      {
        "title": "MCP Request Rate",
        "type": "graph",
        "targets": [
          "rate(mcp_requests_total[5m])"
        ]
      },
      {
        "title": "MCP Response Times",
        "type": "graph",
        "targets": [
          "histogram_quantile(0.95, mcp_request_duration_seconds)"
        ]
      },
      {
        "title": "MCP Server Health",
        "type": "stat",
        "targets": [
          "mcp_active_connections"
        ]
      },
      {
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [
          "rate(mcp_cache_hits_total[5m]) / rate(mcp_requests_total[5m])"
        ]
      }
    ]
  }
}
```

### Alert Rules
```yaml
# Prometheus alert rules
groups:
  - name: mcp_alerts
    rules:
      - alert: MCPServerDown
        expr: mcp_active_connections == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "MCP server {{ $labels.server }} is down"

      - alert: MCPHighErrorRate
        expr: rate(mcp_requests_total{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate for MCP server {{ $labels.server }}"

      - alert: MCPSlowResponseTime
        expr: histogram_quantile(0.95, mcp_request_duration_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times for MCP server {{ $labels.server }}"
```

## Cost Management

### Token Usage Optimization
Given the research finding that MCP can increase token usage by 27.5%, implement comprehensive cost management:

#### 1. Token Usage Monitoring
```python
class TokenUsageTracker:
    def __init__(self):
        self.usage_db = {}
        self.monthly_limits = {
            "openai:gpt-4": 1000000,  # 1M tokens per month
            "anthropic:claude-3-5-sonnet": 500000  # 500K tokens per month
        }

    async def track_usage(self, model: str, tokens_used: int,
                         agent_role: str, mcp_server: str = None):
        """Track token usage with detailed attribution"""
        key = f"{model}:{agent_role}:{mcp_server or 'direct'}"

        if key not in self.usage_db:
            self.usage_db[key] = {
                "total_tokens": 0,
                "requests": 0,
                "monthly_total": 0
            }

        self.usage_db[key]["total_tokens"] += tokens_used
        self.usage_db[key]["requests"] += 1

        # Check monthly limits
        if self.usage_db[key]["monthly_total"] > self.monthly_limits.get(model, float('inf')):
            await self._send_cost_alert(model, key)
```

#### 2. Intelligent Caching Strategy
```python
# Cache expensive operations with longer TTL
CACHE_STRATEGIES = {
    "schema_queries": 3600,      # 1 hour - schemas change rarely
    "data_profiling": 1800,      # 30 minutes - profiles change moderately
    "quick_analytics": 300,      # 5 minutes - analytics change frequently
    "dbt_lineage": 1800,        # 30 minutes - lineage changes with model updates
    "health_checks": 60          # 1 minute - health changes quickly
}
```

#### 3. Cost-Effective Model Selection
```python
# Use cheaper models for routine operations
MODEL_SELECTION_STRATEGY = {
    "health_checks": "openai:gpt-3.5-turbo",
    "simple_queries": "openai:gpt-3.5-turbo",
    "data_analysis": "openai:gpt-4",
    "complex_reasoning": "anthropic:claude-3-5-sonnet"
}
```

## Risk Assessment and Mitigation

### High-Risk Items
1. **Security Vulnerabilities**: Current CORS wildcard configuration
   - **Mitigation**: Immediate CORS configuration update in Phase 1
   - **Timeline**: 2 days
   - **Backup Plan**: WAF implementation if application-level fixes fail

2. **Token Cost Explosion**: 27.5% increase in token usage
   - **Mitigation**: Aggressive caching and intelligent model selection
   - **Timeline**: Throughout Phase 2
   - **Backup Plan**: Request throttling and usage caps

3. **MCP Server Reliability**: Third-party server dependencies
   - **Mitigation**: Health monitoring and graceful degradation
   - **Timeline**: Phase 3
   - **Backup Plan**: Fallback to direct tool execution

### Medium-Risk Items
1. **Performance Degradation**: Added latency from MCP layer
   - **Mitigation**: Connection pooling and caching
   - **Timeline**: Phase 1-2
   - **Backup Plan**: Direct adapter calls for critical operations

2. **Integration Complexity**: Multiple MCP server interactions
   - **Mitigation**: Comprehensive testing and staged rollout
   - **Timeline**: Phase 3-4
   - **Backup Plan**: Gradual MCP server enablement

### Low-Risk Items
1. **Documentation Gaps**: New API endpoints and integrations
   - **Mitigation**: Automated documentation generation
   - **Timeline**: Phase 4
   - **Backup Plan**: Manual documentation creation

## Success Criteria

### Technical Success Metrics
- [ ] **Security**: Zero critical vulnerabilities in security audit
- [ ] **Performance**: 95th percentile response time < 2 seconds
- [ ] **Reliability**: 99.9% uptime for MCP gateway
- [ ] **Coverage**: 95% test coverage for all MCP integrations
- [ ] **Cost**: Token usage increase limited to < 15% through optimization

### Business Success Metrics
- [ ] **Capability Expansion**: 300+ new tools available to AI agents across complete data stack
- [ ] **Agent Effectiveness**: 40% improvement in task completion rate
- [ ] **Developer Productivity**: 30% reduction in manual data operations
- [ ] **System Integration**: All 5 agent types successfully using MCP tools
- [ ] **Production Readiness**: Successful deployment to production environment

### User Experience Metrics
- [ ] **Response Time**: Agent workflows complete 25% faster
- [ ] **Success Rate**: 95% success rate for MCP tool executions
- [ ] **Error Handling**: Graceful degradation in 100% of failure scenarios
- [ ] **Documentation**: Complete API documentation with examples
- [ ] **Monitoring**: Real-time visibility into all MCP operations

## Maintenance and Operations

### Regular Maintenance Tasks
```python
# Daily operations
- Health check monitoring review
- Token usage analysis and optimization
- Error log analysis and resolution
- Performance metric review

# Weekly operations
- MCP server version updates
- Security patch application
- Backup verification
- Capacity planning review

# Monthly operations
- Comprehensive security audit
- Cost analysis and optimization
- Performance tuning
- Documentation updates
```

### Disaster Recovery Procedures
```python
# RTO (Recovery Time Objective): 1 hour
# RPO (Recovery Point Objective): 15 minutes

1. MCP Gateway Failure:
   - Automatic failover to backup instance
   - Health check routing adjustment
   - Alert notification to operations team

2. MCP Server Failure:
   - Graceful degradation to direct tool execution
   - User notification of reduced functionality
   - Automatic retry with exponential backoff

3. Database Failure:
   - Failover to read replica
   - Cache utilization for recent queries
   - Manual intervention for write operations

4. Complete System Failure:
   - Restore from automated backups
   - Rebuild containers from images
   - Data restoration from S3 backups
```

## Conclusion

This comprehensive MCP server integration plan provides a roadmap for transforming the AI agent-driven data stack into a production-ready, secure, and highly capable system. The phased approach ensures critical security issues are addressed first, followed by systematic integration of 24 high-priority MCP servers with complete data stack coverage.

The implementation will result in:
- **Enhanced Security**: Production-ready authentication and input validation
- **Expanded Capabilities**: 300+ new tools available to AI agents across complete data stack
- **Improved Performance**: Intelligent caching and connection pooling
- **Comprehensive Monitoring**: Full observability into MCP operations
- **Cost Management**: Optimized token usage and intelligent model selection

By following this plan, the data stack will become a powerful, secure, and scalable foundation for AI-driven data operations, capable of handling complex analytical workflows while maintaining high performance and reliability standards.

---

**Next Steps**: Upon approval of this PRP, begin Phase 1 implementation with security hardening as the immediate priority. The critical security vulnerabilities must be addressed before proceeding with MCP server integrations to ensure a secure foundation for the expanded capabilities.
