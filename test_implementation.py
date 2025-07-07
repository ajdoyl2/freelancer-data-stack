#!/usr/bin/env python3
"""
Test script to validate the AI agent implementation.

This script tests the core functionality of the modernized data stack
with AI agents to ensure everything is working correctly.
"""

import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from agents import get_agent, list_available_agents
from agents.base_agent import AgentRole
from config.agent_configs import AgentConfigs
from config.model_configs import ModelConfigs
from config.tool_configs import ToolConfigs
from interface.prompt_handler import PromptHandler
from interface.response_formatter import OutputFormat, ResponseFormatter
from interface.workflow_executor import WorkflowExecutor


async def test_agent_framework():
    """Test the basic agent framework functionality."""
    print("🧪 Testing Agent Framework...")

    try:
        # Test agent registry
        available_agents = list_available_agents()
        print(f"✅ Found {len(available_agents)} available agent roles:")
        for role in available_agents:
            print(f"  - {role.value}")

        # Test agent instantiation (without actual model calls)
        print("\n🤖 Testing agent instantiation...")
        for role in [AgentRole.DATA_PLATFORM_ENGINEER, AgentRole.DATA_ENGINEER]:
            try:
                agent = get_agent(role, model_name="openai:gpt-4")
                print(f"✅ Successfully created {role.value} agent")

                # Test capabilities
                capabilities = await agent.get_capabilities()
                print(f"  - {len(capabilities)} capabilities defined")

            except Exception as e:
                print(f"❌ Failed to create {role.value} agent: {str(e)}")

        print("✅ Agent framework test completed")
        return True

    except Exception as e:
        print(f"❌ Agent framework test failed: {str(e)}")
        return False


async def test_configuration_system():
    """Test the configuration management system."""
    print("\n⚙️ Testing Configuration System...")

    try:
        # Test agent configurations
        agent_configs = AgentConfigs()
        print(
            f"✅ Agent configurations loaded for environment: {agent_configs.environment.value}"
        )

        summary = agent_configs.get_environment_summary()
        print(f"  - {summary['total_agents']} agents configured")
        print(f"  - {summary['enabled_agents']} agents enabled")

        # Test model configurations
        model_configs = ModelConfigs()
        print(f"✅ Model configurations loaded: {len(model_configs.models)} models")

        # Test tool configurations
        tool_configs = ToolConfigs()
        summary = tool_configs.get_permissions_summary()
        print(f"✅ Tool configurations loaded: {summary['total_tools']} tools")

        # Validate configurations
        issues = agent_configs.validate_configurations()
        if issues:
            print(f"⚠️ Configuration issues found: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"  - {issue}")
        else:
            print("✅ No configuration issues found")

        print("✅ Configuration system test completed")
        return True

    except Exception as e:
        print(f"❌ Configuration system test failed: {str(e)}")
        return False


async def test_prompt_processing():
    """Test the natural language prompt processing."""
    print("\n💬 Testing Prompt Processing...")

    try:
        prompt_handler = PromptHandler()

        # Test various prompts
        test_prompts = [
            "Deploy the Docker services",
            "Create a dbt model for customer analytics",
            "Set up a complete data pipeline from CSV to dashboard",
            "Monitor the health of all services",
            "Generate a report showing project success rates",
        ]

        for prompt in test_prompts:
            analysis = await prompt_handler.analyze_prompt(prompt)
            print(f"✅ Analyzed: '{prompt[:50]}...'")
            print(f"  - Intent: {analysis['intent'].value}")
            print(f"  - Complexity: {analysis['complexity'].value}")
            print(f"  - Agents: {[role.value for role in analysis['required_agents']]}")
            print(f"  - Confidence: {analysis['confidence']:.2f}")

        print("✅ Prompt processing test completed")
        return True

    except Exception as e:
        print(f"❌ Prompt processing test failed: {str(e)}")
        return False


async def test_response_formatting():
    """Test the response formatting system."""
    print("\n📝 Testing Response Formatting...")

    try:
        formatter = ResponseFormatter()

        # Test error response formatting
        error_response = await formatter.format_error_response(
            user_prompt="Test prompt",
            error_message="Test error",
            execution_id="test_123",
            output_format=OutputFormat.MARKDOWN,
        )

        print("✅ Error response formatting works")
        print(f"  - Format: {error_response['format']}")
        print(f"  - Status: {error_response['status']}")

        # Test progress formatting
        progress = formatter.format_progress_update(
            execution_id="test_123", message="Testing progress", progress=0.5
        )

        print("✅ Progress formatting works")
        print(f"  - Progress: {progress['progress']}")

        print("✅ Response formatting test completed")
        return True

    except Exception as e:
        print(f"❌ Response formatting test failed: {str(e)}")
        return False


async def test_workflow_executor():
    """Test the workflow executor (without actual LLM calls)."""
    print("\n🔄 Testing Workflow Executor...")

    try:
        # Initialize executor (without agents to avoid API calls)
        executor = WorkflowExecutor()

        # Test prompt handler integration
        test_prompt = "Show me the status of Docker services"
        workflow_request = await executor.prompt_handler.create_workflow_request(
            test_prompt
        )

        print("✅ Workflow request creation works")
        print(f"  - Prompt: {workflow_request.user_prompt}")
        print(f"  - Priority: {workflow_request.priority.value}")
        print(
            f"  - Agents: {[role.value for role in workflow_request.agents_involved]}"
        )

        # Test execution strategy determination
        strategy = executor._determine_execution_strategy(workflow_request)
        print("✅ Execution strategy determination works")
        print(f"  - Type: {strategy['type']}")
        print(f"  - Coordination required: {strategy['coordination_required']}")

        print("✅ Workflow executor test completed")
        return True

    except Exception as e:
        print(f"❌ Workflow executor test failed: {str(e)}")
        return False


async def test_directory_structure():
    """Test that all required directories and files exist."""
    print("\n📁 Testing Directory Structure...")

    required_dirs = [
        "agents",
        "tools",
        "config",
        "interface",
        "tests",
        "examples",
        "PRPs",
    ]

    required_files = [
        "agents/__init__.py",
        "agents/base_agent.py",
        "agents/data_platform_engineer.py",
        "agents/data_engineer.py",
        "agents/analytics_engineer.py",
        "agents/data_scientist.py",
        "agents/data_analyst.py",
        "agents/orchestrator.py",
        "tools/__init__.py",
        "tools/docker_tools.py",
        "tools/dbt_tools.py",
        "config/__init__.py",
        "config/agent_configs.py",
        "config/model_configs.py",
        "config/tool_configs.py",
        "interface/__init__.py",
        "interface/prompt_handler.py",
        "interface/workflow_executor.py",
        "interface/response_formatter.py",
    ]

    try:
        # Check directories
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                print(f"✅ Directory exists: {dir_name}")
            else:
                print(f"❌ Missing directory: {dir_name}")
                return False

        # Check files
        for file_name in required_files:
            file_path = Path(file_name)
            if file_path.exists() and file_path.is_file():
                print(f"✅ File exists: {file_name}")
            else:
                print(f"❌ Missing file: {file_name}")
                return False

        print("✅ Directory structure test completed")
        return True

    except Exception as e:
        print(f"❌ Directory structure test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting AI Agent Implementation Tests")
    print("=" * 50)

    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise

    test_functions = [
        test_directory_structure,
        test_configuration_system,
        test_agent_framework,
        test_prompt_processing,
        test_response_formatting,
        test_workflow_executor,
    ]

    results = []

    for test_func in test_functions:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {str(e)}")
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All tests passed! The AI agent implementation is working correctly.")
        print("\n✅ Ready for deployment!")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        print("\n🔧 Implementation needs fixes before deployment.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
