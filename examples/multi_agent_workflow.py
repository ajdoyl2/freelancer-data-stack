#!/usr/bin/env python3
"""
Multi-Agent Workflow Example

This script demonstrates how to coordinate multiple AI agents for complex
data stack operations that require collaboration between different roles.
"""

import asyncio
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.base_agent import AgentRole, WorkflowPriority, WorkflowRequest
from agents.orchestrator import AgentOrchestrator
from interface.workflow_executor import WorkflowExecutor


async def demonstrate_multi_agent_coordination():
    """Demonstrate coordinated multi-agent workflows."""

    print("🤝 Multi-Agent Workflow Examples")
    print("=" * 50)

    # Initialize orchestrator
    orchestrator = AgentOrchestrator()

    # Example 1: Complete Data Pipeline Setup
    print("\n1. Complete Data Pipeline Setup")
    print("   Involves: Platform Engineer → Data Engineer → Analytics Engineer")

    pipeline_workflow = WorkflowRequest(
        user_prompt="Set up a complete data pipeline from CSV files to analytics dashboards",
        agents_involved=[
            AgentRole.DATA_PLATFORM_ENGINEER,
            AgentRole.DATA_ENGINEER,
            AgentRole.ANALYTICS_ENGINEER,
        ],
        priority=WorkflowPriority.HIGH,
        context={
            "source_type": "csv",
            "target_type": "dashboard",
            "complexity": "multi_agent",
        },
    )

    try:
        result = await orchestrator.execute_workflow(pipeline_workflow)
        print(f"✅ Pipeline setup completed: {result.status}")
        print(f"   Execution time: {result.execution_time_ms}ms")
        print(f"   Output: {result.output.get('overall_status', 'N/A')}")
    except Exception as e:
        print(f"❌ Pipeline setup failed: {str(e)}")

    # Example 2: Data Quality Assessment
    print("\n\n2. Data Quality Assessment")
    print("   Involves: Data Engineer → Data Scientist → Data Analyst")

    quality_workflow = WorkflowRequest(
        user_prompt="Perform a comprehensive data quality assessment and create a report",
        agents_involved=[
            AgentRole.DATA_ENGINEER,
            AgentRole.DATA_SCIENTIST,
            AgentRole.DATA_ANALYST,
        ],
        priority=WorkflowPriority.MEDIUM,
        context={"assessment_type": "comprehensive", "output_format": "report"},
    )

    try:
        result = await orchestrator.execute_workflow(quality_workflow)
        print(f"✅ Quality assessment completed: {result.status}")
        print(f"   Output: {result.output.get('overall_status', 'N/A')}")
        print(f"   Agent results: {len(result.output.get('agent_results', {}))}")
    except Exception as e:
        print(f"❌ Quality assessment failed: {str(e)}")

    # Example 3: ML Pipeline Deployment
    print("\n\n3. ML Pipeline Deployment")
    print("   Involves: Platform Engineer → Data Scientist → Data Engineer")

    ml_workflow = WorkflowRequest(
        user_prompt="Deploy a machine learning pipeline for customer churn prediction",
        agents_involved=[
            AgentRole.DATA_PLATFORM_ENGINEER,
            AgentRole.DATA_SCIENTIST,
            AgentRole.DATA_ENGINEER,
        ],
        priority=WorkflowPriority.HIGH,
        context={"model_type": "classification", "deployment_target": "production"},
    )

    try:
        result = await orchestrator.execute_workflow(ml_workflow)
        print(f"✅ ML pipeline deployed: {result.status}")
        print(f"   Output: {result.output.get('overall_status', 'N/A')}")
        print(f"   Agent results: {len(result.output.get('agent_results', {}))}")
    except Exception as e:
        print(f"❌ ML pipeline deployment failed: {str(e)}")


async def demonstrate_natural_language_workflows():
    """Demonstrate natural language workflow processing."""

    print("\n\n💬 Natural Language Workflow Examples")
    print("=" * 50)

    # Initialize workflow executor
    executor = WorkflowExecutor()

    # Example natural language requests
    requests = [
        "I need to migrate our customer data from the old system to the new one",
        "Create a real-time dashboard showing our key business metrics",
        "Set up automated alerts for when our data quality drops below 95%",
        "Build a recommendation system for our e-commerce platform",
        "Generate a monthly report showing our data pipeline performance",
    ]

    for i, request in enumerate(requests, 1):
        print(f"\n{i}. Processing: '{request}'")

        try:
            # Analyze the request
            analysis = await executor.prompt_handler.analyze_prompt(request)
            print(f"   Intent: {analysis['intent'].value}")
            print(f"   Complexity: {analysis['complexity'].value}")
            print(
                f"   Required agents: {[role.value for role in analysis['required_agents']]}"
            )
            print(f"   Confidence: {analysis['confidence']:.2f}")

            # Execute the workflow (simulated)
            result = await executor.process_request(request)
            print(f"   Status: {result.status}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


async def demonstrate_workflow_monitoring():
    """Demonstrate workflow monitoring and status tracking."""

    print("\n\n📊 Workflow Monitoring Examples")
    print("=" * 50)

    orchestrator = AgentOrchestrator()

    # Get active workflows
    active_workflows = await orchestrator.list_active_workflows()
    print(f"Active workflows: {len(active_workflows)}")

    for workflow in active_workflows:
        print(
            f"  - {workflow['workflow_id']}: {workflow['status']} - {workflow['prompt']}"
        )

    # Show orchestrator capabilities
    capabilities = await orchestrator.get_capabilities()
    print(f"\nOrchestrator Capabilities: {len(capabilities)}")
    for cap in capabilities:
        print(f"  - {cap.name}: {cap.description}")


async def main():
    """Main execution function."""

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        await demonstrate_multi_agent_coordination()
        await demonstrate_natural_language_workflows()
        await demonstrate_workflow_monitoring()

        print("\n✅ Multi-agent workflow examples completed!")

    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
