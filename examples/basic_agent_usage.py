#!/usr/bin/env python3
"""
Basic AI Agent Usage Example

This script demonstrates how to use individual AI agents for specific tasks
in the data stack environment.
"""

import asyncio
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents import get_agent
from agents.base_agent import AgentRole, WorkflowRequest


async def demonstrate_basic_agent_usage():
    """Demonstrate basic agent usage patterns."""

    print("🤖 AI Agent Basic Usage Examples")
    print("=" * 50)

    # Example 1: Data Platform Engineer
    print("\n1. Data Platform Engineer - Infrastructure Tasks")
    platform_agent = get_agent(AgentRole.DATA_PLATFORM_ENGINEER)

    tasks = [
        "Check the status of all Docker containers",
        "Show me the current resource usage of the data stack",
        "Restart the PostgreSQL service if it's not running",
    ]

    for task in tasks:
        print(f"\n📋 Task: {task}")
        try:
            request = WorkflowRequest(user_prompt=task)
            result = await platform_agent.execute_task(request)
            print(f"✅ Result: {result.output}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    # Example 2: Data Engineer
    print("\n\n2. Data Engineer - Pipeline Tasks")
    data_engineer = get_agent(AgentRole.DATA_ENGINEER)

    pipeline_tasks = [
        "Check the status of our Airflow DAGs",
        "Run a quality check on the customer data",
        "Show me the latest Meltano pipeline runs",
    ]

    for task in pipeline_tasks:
        print(f"\n📋 Task: {task}")
        try:
            request = WorkflowRequest(user_prompt=task)
            result = await data_engineer.execute_task(request)
            print(f"✅ Result: {result.output}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    # Example 3: Analytics Engineer
    print("\n\n3. Analytics Engineer - dbt Tasks")
    analytics_engineer = get_agent(AgentRole.ANALYTICS_ENGINEER)

    dbt_tasks = [
        "Run dbt tests on the customer models",
        "Generate documentation for our dbt project",
        "Create a new staging model for product data",
    ]

    for task in dbt_tasks:
        print(f"\n📋 Task: {task}")
        try:
            request = WorkflowRequest(user_prompt=task)
            result = await analytics_engineer.execute_task(request)
            print(f"✅ Result: {result.output}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    # Example 4: Data Scientist
    print("\n\n4. Data Scientist - ML Tasks")
    data_scientist = get_agent(AgentRole.DATA_SCIENTIST)

    ml_tasks = [
        "Analyze customer churn patterns in our dataset",
        "Create a predictive model for sales forecasting",
        "Generate a statistical summary of our user behavior data",
    ]

    for task in ml_tasks:
        print(f"\n📋 Task: {task}")
        try:
            request = WorkflowRequest(user_prompt=task)
            result = await data_scientist.execute_task(request)
            print(f"✅ Result: {result.output}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    # Example 5: Data Analyst
    print("\n\n5. Data Analyst - Reporting Tasks")
    data_analyst = get_agent(AgentRole.DATA_ANALYST)

    reporting_tasks = [
        "Create a dashboard showing monthly revenue trends",
        "Generate a report on customer acquisition costs",
        "Build a visualization of our top performing products",
    ]

    for task in reporting_tasks:
        print(f"\n📋 Task: {task}")
        try:
            request = WorkflowRequest(user_prompt=task)
            result = await data_analyst.execute_task(request)
            print(f"✅ Result: {result.output}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def demonstrate_agent_capabilities():
    """Show agent capabilities and available tools."""

    print("\n\n🛠️ Agent Capabilities Overview")
    print("=" * 50)

    for role in AgentRole:
        agent = get_agent(role)
        capabilities = await agent.get_capabilities()

        print(f"\n{role.value.upper()}:")
        print(f"  Available capabilities: {len(capabilities)}")
        for i, capability in enumerate(capabilities[:3], 1):
            print(f"  {i}. {capability}")
        if len(capabilities) > 3:
            print(f"  ... and {len(capabilities) - 3} more")


async def main():
    """Main execution function."""

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        await demonstrate_basic_agent_usage()
        await demonstrate_agent_capabilities()

        print("\n✅ Basic agent usage examples completed!")

    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
