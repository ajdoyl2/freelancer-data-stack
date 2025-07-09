#!/usr/bin/env python3
"""
Script to import AI agent workflows into Warp's database.
This avoids the need to manually add each workflow through the UI.
"""

import json
import sqlite3
from pathlib import Path

# Warp database path
WARP_DB_PATH = (
    Path.home() / "Library/Application Support/dev.warp.Warp-Stable/warp.sqlite"
)

# Workflows to add
WORKFLOWS = [
    {
        "name": "AI Code Review",
        "command": """echo 'Please perform a comprehensive code review of the following code. Focus on:

1. Code Quality & Style:
   - PEP 8 compliance, type hints, docstrings
   - Code organization and decomposition
   - Import organization

2. Functionality & Logic:
   - Correctness and edge case handling
   - Data validation and business logic alignment
   - Algorithm efficiency

3. Data Stack Integration:
   - Dagster asset dependencies and resource usage
   - dbt model structure and testing
   - Database connection management

4. Security & Best Practices:
   - Input validation and injection prevention
   - Secrets management
   - Error handling and logging

5. Testing & Documentation:
   - Test coverage and mock usage
   - API documentation and examples

Provide specific recommendations with before/after code examples where helpful.'""",
        "tags": ["ai", "code-review", "quality", "python", "dagster", "dbt"],
        "description": "Comprehensive code review with quality, security, and performance analysis",
        "arguments": [],
        "source_url": None,
        "author": None,
        "author_url": None,
        "shells": [],
        "environment_variables": None,
    },
    {
        "name": "Data Pipeline Design",
        "command": """echo 'Design a comprehensive data pipeline using our freelancer data stack:

Stack: Dagster (orchestration), dbt (transformation), DuckDB (warehouse), Streamlit (visualization)
Infrastructure: Docker Compose, Poetry, PostgreSQL, Redis

Please provide:

1. Architecture Overview:
   - Data flow from sources to consumption
   - Component interaction diagram
   - Technology stack integration

2. Implementation Strategy:
   - Dagster assets and jobs structure
   - dbt model organization (staging/intermediate/marts)
   - Data quality framework with Great Expectations

3. Quality & Performance:
   - Error handling and retry mechanisms
   - Monitoring and alerting setup
   - Performance optimization strategies

4. Detailed Design:
   - Source system connections
   - Transformation logic
   - Storage optimization
   - Scheduling and dependencies

Provide specific code examples for Dagster assets and dbt models.'""",
        "tags": ["ai", "data-pipeline", "architecture", "dagster", "dbt", "design"],
        "description": "Design comprehensive data pipeline architecture with Dagster and dbt",
        "arguments": [],
        "source_url": None,
        "author": None,
        "author_url": None,
        "shells": [],
        "environment_variables": None,
    },
    {
        "name": "AI Debug Assistant",
        "command": """echo 'Help me debug this issue systematically:

1. Initial Analysis:
   - Understand the error context and symptoms
   - Identify the component (Dagster, dbt, DuckDB, Docker, etc.)
   - Determine the data flow impact

2. Investigation Steps:
   - Check logs and error messages
   - Verify service health (Docker, databases)
   - Test connectivity and dependencies
   - Review recent changes

3. Data Stack Specific Checks:
   - Dagster asset status and dependencies
   - dbt model compilation and execution
   - Database connections and queries
   - Docker service status

4. Resolution Strategy:
   - Provide specific troubleshooting steps
   - Suggest immediate fixes and long-term solutions
   - Include prevention measures
   - Recommend monitoring improvements

Please provide actionable steps with specific commands where applicable.'""",
        "tags": ["ai", "debugging", "troubleshooting", "dagster", "dbt", "docker"],
        "description": "Systematic error analysis and troubleshooting for data stack issues",
        "arguments": [],
        "source_url": None,
        "author": None,
        "author_url": None,
        "shells": [],
        "environment_variables": None,
    },
    {
        "name": "Production Issue Triage",
        "command": """echo 'PRODUCTION ISSUE TRIAGE - Emergency Response:

🚨 IMMEDIATE ASSESSMENT:
1. Impact Analysis:
   - What services/data are affected?
   - How many users/processes impacted?
   - Data integrity concerns?

2. Quick Stabilization:
   - Can we rollback recent changes?
   - Are there immediate workarounds?
   - Need to pause automated processes?

3. Service Health Check:
   - Docker services: docker-compose ps
   - Database connectivity
   - Dagster pipeline status
   - Data freshness validation

🔍 ROOT CAUSE INVESTIGATION:
1. Recent Changes:
   - Git commits in last 24 hours
   - Deployment timeline
   - Configuration changes

2. System Diagnostics:
   - Resource usage (CPU, memory, disk)
   - Error logs and patterns
   - Network connectivity

3. Data Pipeline Status:
   - Failed Dagster runs
   - dbt model failures
   - Data quality check results

🛠️ RESOLUTION & RECOVERY:
Provide step-by-step recovery plan with rollback options.'""",
        "tags": ["ai", "production", "emergency", "triage", "incident"],
        "description": "Emergency production issue response and resolution",
        "arguments": [],
        "source_url": None,
        "author": None,
        "author_url": None,
        "shells": [],
        "environment_variables": None,
    },
    {
        "name": "dbt Model Development",
        "command": """echo 'Help me develop a dbt model following freelancer data stack best practices:

Stack Context: dbt-core 1.8.8, dbt-duckdb 1.9.4, DuckDB warehouse

Please provide:

1. Model Structure:
   - Proper staging/intermediate/marts organization
   - Materialization strategy (table/view/incremental)
   - Partitioning and clustering recommendations

2. SQL Best Practices:
   - Optimized queries for DuckDB
   - Proper use of dbt functions and macros
   - Window functions and aggregations

3. Testing & Documentation:
   - dbt tests (unique, not_null, relationships)
   - Custom data quality tests
   - Model and column descriptions

4. Performance Optimization:
   - Incremental model patterns
   - Efficient joins and filters
   - Memory usage considerations

5. Dependencies & Lineage:
   - Source and ref() usage
   - Proper dependency structure
   - Dagster asset integration

Provide complete model code with tests and documentation.'""",
        "tags": ["ai", "dbt", "sql", "data-modeling", "optimization"],
        "description": "Create optimized dbt models following best practices",
        "arguments": [],
        "source_url": None,
        "author": None,
        "author_url": None,
        "shells": [],
        "environment_variables": None,
    },
    {
        "name": "Dagster Asset Creation",
        "command": """echo 'Help me create a Dagster asset following our data stack patterns:

Stack: Dagster 1.8.13, integrated with dbt, DuckDB, DataHub

Please provide:

1. Asset Definition:
   - Proper asset decorator usage
   - Dependencies and partitioning
   - Resource configuration

2. Integration Patterns:
   - dbt model execution
   - Database connection handling
   - Data quality validation

3. Metadata & Monitoring:
   - MaterializeResult with metadata
   - Logging and observability
   - Error handling and retries

4. Testing Strategy:
   - Unit tests for asset logic
   - Integration tests with dependencies
   - Mock patterns for external services

5. Performance Considerations:
   - Batch processing patterns
   - Memory management
   - Incremental processing

Provide complete asset code with tests and documentation.'""",
        "tags": ["ai", "dagster", "assets", "orchestration", "python"],
        "description": "Create Dagster assets with proper dependencies and metadata",
        "arguments": [],
        "source_url": None,
        "author": None,
        "author_url": None,
        "shells": [],
        "environment_variables": None,
    },
]


def workflow_exists(conn, name):
    """Check if a workflow with the given name already exists."""
    cursor = conn.execute(
        "SELECT COUNT(*) FROM workflows WHERE json_extract(data, '$.name') = ?", (name,)
    )
    return cursor.fetchone()[0] > 0


def add_workflow(conn, workflow_data):
    """Add a workflow to the Warp database."""
    workflow_json = json.dumps(workflow_data)

    if workflow_exists(conn, workflow_data["name"]):
        print(f"⚠️  Workflow '{workflow_data['name']}' already exists, skipping...")
        return False

    try:
        conn.execute("INSERT INTO workflows (data) VALUES (?)", (workflow_json,))
        print(f"✅ Added workflow: '{workflow_data['name']}'")
        return True
    except Exception as e:
        print(f"❌ Failed to add workflow '{workflow_data['name']}': {e}")
        return False


def main():
    """Main function to import workflows."""
    if not WARP_DB_PATH.exists():
        print(f"❌ Warp database not found at: {WARP_DB_PATH}")
        print("Make sure Warp is installed and has been run at least once.")
        return

    print(f"🔧 Connecting to Warp database: {WARP_DB_PATH}")

    try:
        conn = sqlite3.connect(WARP_DB_PATH)

        print(f"\n📝 Importing {len(WORKFLOWS)} AI agent workflows...")

        added_count = 0
        for workflow in WORKFLOWS:
            if add_workflow(conn, workflow):
                added_count += 1

        conn.commit()
        conn.close()

        print(f"\n🎉 Successfully imported {added_count} workflows!")
        print("📱 Open Warp and press Cmd+P to access your new AI workflows.")

        if added_count > 0:
            print("\n🎯 Try these workflows:")
            for workflow in WORKFLOWS[:3]:  # Show first 3
                print(f"   • {workflow['name']}")

    except Exception as e:
        print(f"❌ Error connecting to Warp database: {e}")
        print("Make sure Warp is not running while importing workflows.")


if __name__ == "__main__":
    main()
